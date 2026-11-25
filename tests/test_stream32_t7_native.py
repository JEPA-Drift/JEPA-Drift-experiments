import hashlib
import json
import math
import os
import shutil
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom

from experiments import pca_info_online as producer
from jepadrift.sim import t_innov
from test_pca_info_online import (
    _authorized,
    _b2j_frame,
    _b2j_words,
    _b4f_durable,
    _b4o_authorized_cfg,
    _r3_smoke_cfg,
    _ref_masks,
    _tree,
)


def _t7_cfg(mode="full"):
    cfg = _b4o_authorized_cfg(mode)
    cfg["scope"]["setups"] = [["FITTED_LW_T7", 24, 0]]
    cfg["scope"]["applications"] = ["RESIDUAL", "MARKET"]
    cfg["scope"]["families"] = ["F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL", "F3_MARKET"]
    cfg["modes"][mode]["null_plan"] = None
    return cfg


def _start(root, cfg, desc, *, resume=False):
    staging = producer.open_staging(root, desc, resume)
    authority = producer.authorize("full", cfg, desc, 1)
    token = f"{root.name}-{'resume' if resume else 'initial'}"
    context = producer.start_invocation(staging, authority, producer.partition_plan(desc), token)
    context.update(jobs=1, bootstrap_cache={})
    return staging, context


def _publish(staging, context, desc, out):
    def build(temp, did, records):
        rows = list(producer._staged_descriptive_rows(staging, did, records, desc, {}, lambda: None))
        producer.export_payloads(temp, staging, did, records, descriptive_rows=rows)
        return {}

    return producer.finalize_planned(staging, out, context["authority"], context["plan"], build)


def test_t7_native_draw_has_one_daily_scale_and_disjoint_seed_domains():
    descriptors, entropies = {}, {}
    for mode in ("pilot", "full"):
        cfg = _t7_cfg(mode)
        desc = producer.design_descriptor(cfg, mode)
        keys = producer.seed_plan(cfg, mode)["keys"]
        words = [tuple(_b2j_words(cfg["seed"], key)) for key in keys]
        assert len(words) == len(set(words))
        assert {key[0] for key in keys} == {"frame", "fit", "path", "meta", "devlib", "boot"}
        assert {key[5] for key in keys if key[0] == "path"} == {
            "DEV_NULL", "DEV_ALT", "CAL_NULL", "HOLD_NULL", "ALT"}
        descriptors[mode], entropies[mode] = desc, set(words)
    assert entropies["pilot"].isdisjoint(entropies["full"])

    desc, frame = descriptors["full"], _b2j_frame()
    keys = [("fit", "FULL", "FITTED_LW_T7", 24, 0),
            ("path", "FULL", "FITTED_LW_T7", 24, 0, "CAL_NULL", 0)]
    for key in keys:
        words = _b2j_words(desc["seed"], key)
        rows = desc["science"]["parameters"]["T_fit" if key[0] == "fit" else "H"]
        rng = np.random.default_rng(np.random.SeedSequence(words))
        normal = rng.standard_normal((rows, 24))
        chi2 = rng.chisquare(7, size=rows)
        latent = normal / np.sqrt(chi2 / 7)[:, None] * math.sqrt(5 / 7)
        actual = t_innov(np.random.default_rng(np.random.SeedSequence(words)), (rows, 24))
        np.testing.assert_array_equal(actual, latent)
        np.testing.assert_allclose(actual / normal, np.broadcast_to(np.sqrt(5 / chi2)[:, None], actual.shape),
                                   rtol=4e-16, atol=0)
        expected = frame["mean"] + (latent * np.sqrt(frame["lam"])) @ frame["V"].T
        np.testing.assert_array_equal(producer.null_returns(desc, frame, key), expected)


def test_t7_nonoracle_scores_and_scans_ignore_independently_drawn_metadata():
    cfg = _t7_cfg()
    desc = producer.design_descriptor(cfg, "full")
    frame = _b2j_frame()
    setup = ("FITTED_LW_T7", 24, 0)
    fit_key = ("fit", "FULL", *setup)
    fit = producer.setup_bundle(desc, frame, producer.null_returns(desc, frame, fit_key), list(setup))["fit"]
    key = ("path", "FULL", *setup, "CAL_NULL", 0)
    Y = producer.path_scores(desc, frame, fit, "RESIDUAL", key)[None]
    labels = (*producer.P_CONF, "ONLINE_INFO_AFF_W32", "ONLINE_PREFIX_AFF_W32")
    bundles = [producer.frozen_policy(desc, "RESIDUAL", label) for label in labels]
    before = [producer.nonoracle_scan(Y, bundle) for bundle in bundles]
    metadata = [producer.direction_draws(desc, ("meta", "FULL", *setup, "CAL_NULL", family, 0))
                for family in cfg["scope"]["families"]]
    assert any(not np.array_equal(metadata[0], draw) for draw in metadata[1:])
    np.testing.assert_array_equal(producer.path_scores(desc, frame, fit, "RESIDUAL", key)[None], Y)
    for bundle, expected in zip(bundles, before):
        actual = producer.nonoracle_scan(Y, bundle)
        for name in ("W", "first", "mask_bits"):
            np.testing.assert_array_equal(actual[name], expected[name])
    oracle = producer.frozen_policy(desc, "RESIDUAL", "ORACLE_INFO_MIX")
    q = np.zeros((1, 20))
    q[0, 0] = 0.25
    first = producer.oracle_scan(Y, q, oracle)
    last = producer.oracle_scan(Y, q[:, ::-1].copy(), oracle)
    assert not np.array_equal(first["mask_bits"], last["mask_bits"])


def test_t7_cal_nonoracle_maxima_are_invariant_to_meta_replicate_permutation(tmp_path, monkeypatch):
    cfg, did = _authorized(tmp_path, monkeypatch, _t7_cfg(), "full")
    desc = producer.design_descriptor(cfg, "full")
    real_draws = producer.direction_draws

    def permuted(design, key):
        if key[0] == "meta" and key[5] == "CAL_NULL":
            key = (*key[:-1], (key[-1] + 1) % design["sizes"]["CAL_NULL"])
        return real_draws(design, key)

    results = []
    for changed in (False, True):
        staging, context = _start(tmp_path / f"metadata-{changed}", cfg, desc)
        producer.setup_phase(cfg, "full", context)
        producer.dev_phase(cfg, "full", context)
        with monkeypatch.context() as metadata:
            if changed:
                metadata.setattr(producer, "direction_draws", permuted)
            record = producer.cal_phase(cfg, "full", context)
        maxima = {}
        for part in record["partitions"]:
            maxima.update(producer._verify_partition(staging, did, record["upstream"], part["key"])[2])
        results.append((record["derived"]["thresholds"], maxima))
    thresholds, maxima = results[0]
    other_thresholds, other_maxima = results[1]
    assert {cid for cid, row in thresholds.items() if row.get("family") is None} == {
        cid for cid, row in other_thresholds.items() if row.get("family") is None}
    for cid, row in thresholds.items():
        if row.get("family") is None:
            assert row == other_thresholds[cid]
    nonoracle = {row["maxima_sha256"] for row in thresholds.values() if row.get("family") is None}
    for name, values in maxima.items():
        if producer.pdb.array_sha256(values) in nonoracle:
            np.testing.assert_array_equal(values, other_maxima[name])
    assert any(not np.array_equal(values, other_maxima[name]) for name, values in maxima.items())


@pytest.mark.parametrize("window", [32, 128])
@pytest.mark.parametrize("order", ["INFO", "PREFIX"])
def test_t7_online_windows_use_only_the_declared_past(window, order):
    rng = np.random.default_rng(np.random.SeedSequence([32, 7, window]))
    Y = rng.integers(-4, 5, size=(2, 132, 3)) / 2
    cost = np.array([1.0, 1.5, 2.0])
    actual = producer.online_masks(Y, window, cost, order)
    np.testing.assert_array_equal(actual, _ref_masks(Y, window, cost, order))
    np.testing.assert_array_equal(actual[:, 0], [[True, False, False]] * 2)
    cut = 130
    future = Y.copy()
    future[:, cut:] += 1024
    np.testing.assert_array_equal(producer.online_masks(future, window, cost, order)[:, :cut + 1],
                                  actual[:, :cut + 1])
    expired = Y.copy()
    expired[:, cut - window - 1] += 1024
    np.testing.assert_array_equal(producer.online_masks(expired, window, cost, order)[:, cut], actual[:, cut])


@pytest.mark.parametrize("maxima,rank,alarms", [([2.0] * 39, 1, 0), ([0.0] * 34 + [2.0] * 4 + [3.0], 1, 1)])
def test_t7_ge_rank_ties_and_first_hit_boundary(maxima, rank, alarms):
    maxima = np.asarray(maxima)
    result = producer._calibrate_ge(maxima[:, None], 0.05)
    assert (result["r"], result["alarms"], result["n"]) == (rank, alarms, 39)
    assert result["h"] == np.nextafter(2.0, np.inf)
    assert int((maxima >= result["h"]).sum()) == alarms
    assert int((maxima >= 2.0).sum()) > rank
    Y, mask = np.array([[[0.0], [0.0], [3.0]]]), np.ones((1, 3, 1), dtype=bool)
    W, _ = producer.masked_scan(Y, mask, 0.5)
    h = float(W[0, -1])
    assert h > W[0, :-1].max()
    assert producer.masked_scan(Y, mask, 0.5, h)[1].tolist() == [3]
    assert producer.masked_scan(Y, mask, 0.5, np.nextafter(h, np.inf))[1].tolist() == [-1]
    cell = ("w_probe", "policy", None, {})
    with pytest.raises(ValueError, match="GE rank"):
        producer._cal_row("setup", cell, maxima, 39, 0.05, 2.0, rank, alarms)


def test_t7_hold_cp_three_states_preserve_both_contrast_states():
    desc = producer.design_descriptor(_t7_cfg(), "full")
    labels = producer.P_CONF
    firsts = {cid: np.concatenate([np.ones(k, dtype=np.int64), -np.ones(100 - k, dtype=np.int64)])
              for cid, k in zip(labels, (0, 6, 100))}
    cells = {"cohort": [(cid, "setup", f"pid-{cid}", None, {}, 0.0) for cid in labels]}
    loaded = {"cohort": {cid: int((first > 0).sum()) for cid, first in firsts.items()}}
    checks = producer._hold_checks(desc, cells, loaded, {"cohort": 100})["null_checks"]
    assert [checks[cid]["status"] for cid in labels] == ["NULL_VALIDATED", "NULL_INCONCLUSIVE", "NULL_FAILED"]
    for cid, first in firsts.items():
        row = checks[cid]
        k, n = int((first > 0).sum()), 100
        assert row["k"] == k and row["n"] == n
        if k:
            assert binom.sf(k - 1, n, row["lo"]) == pytest.approx(0.05, abs=2e-14)
        else:
            assert row["lo"] == 0
        if k < n:
            assert binom.cdf(k, n, row["hi"]) == pytest.approx(0.05, abs=2e-14)
        else:
            assert row["hi"] == 1
    meta = {cid: {"policy_label": cid, "variant": "PRIMARY", "policy_id": row["policy_id"],
                  "calibration_family": None, "null_status": row["status"]} for cid, row in checks.items()}
    alt = {cid: np.array([1, 6, -1]) for cid in labels}
    rows = producer.descriptive_contrasts("full", 6, "F2_STRUCTURED_RESIDUAL", meta, firsts, alt,
                                         np.array([[0, 1, 2], [2, 1, 0]]))
    assert rows and any(row["candidate_null_status"] == "NULL_FAILED" for row in rows)
    for row in rows:
        assert row["status"] == "DESCRIPTIVE_NOMINAL"
        for role in ("candidate", "reference"):
            assert row[f"{role}_null_status"] == checks[row[f"{role}_calibration_id"]]["status"]


def test_t7_invalid_rank_refuses_cal_without_changing_committed_evidence(tmp_path, monkeypatch):
    cfg = _t7_cfg()
    cfg["modes"]["full"]["sizes"]["CAL_NULL"] = 18
    cfg, _ = _authorized(tmp_path, monkeypatch, cfg, "full")
    desc = producer.design_descriptor(cfg, "full")
    staging, context = _start(tmp_path / "invalid-rank", cfg, desc)
    producer.setup_phase(cfg, "full", context)
    producer.dev_phase(cfg, "full", context)
    before = _b4f_durable(staging)
    with pytest.raises(producer.pdb.InsufficientCalibration, match="18.*19") as refusal:
        producer.cal_phase(cfg, "full", context)
    assert str(refusal.value)
    assert _b4f_durable(staging) == before
    assert not (staging / "phases" / "CAL.json").exists()
    status = producer.finalize_planned(staging, tmp_path / "out", context["authority"], context["plan"],
                                      lambda *_: pytest.fail("an invalid CAL cannot publish"))
    assert status["status"] == "INCOMPLETE" and status["last_complete_phase"] == "DEV"
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("allocated", [False, True])
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_t7_npz_size_boundary_at_write_and_read(tmp_path, monkeypatch, allocated, offset):
    cfg, mode = (_r3_smoke_cfg(), "smoke") if allocated else (_t7_cfg(), "full")
    desc = producer.design_descriptor(cfg, mode)
    did = producer.design_id(desc)
    staging = producer.open_staging(tmp_path, desc, False)
    key, arrays = ["frame", mode.upper(), 24], {"probe": np.arange(8, dtype=np.int64)}
    payload, _ = producer._npz_payload(arrays)
    stem = producer._partition_path(staging, did, {}, key)
    limit = len(payload) + offset
    with monkeypatch.context() as bounded:
        bounded.setattr(producer, "MAX_PUBLISHED_BYTES", limit)
        if allocated and offset <= 0:
            with pytest.raises(ValueError, match="bytes"):
                producer.partition(staging, "SETUP", {}, key, lambda: arrays)
            assert not stem.with_suffix(".npz").exists() and not stem.with_suffix(".json").exists()
        else:
            producer.partition(staging, "SETUP", {}, key, lambda: arrays)
    producer.partition(staging, "SETUP", {}, key, lambda: arrays)
    monkeypatch.setattr(producer, "MAX_PUBLISHED_BYTES", limit)
    if allocated and offset <= 0:
        with pytest.raises(producer.PartitionMismatch, match="bytes"):
            producer._verify_partition(staging, did, {}, key)
    else:
        _, n, actual = producer._verify_partition(staging, did, {}, key)
        assert n == 8
        np.testing.assert_array_equal(actual["probe"], arrays["probe"])


@pytest.mark.parametrize("kind", ["csv", "json"])
def test_t7_unallocated_publication_size_boundary(tmp_path, monkeypatch, kind):
    cfg, _ = _authorized(tmp_path, monkeypatch, _t7_cfg(), "full")
    desc = producer.design_descriptor(cfg, "full")
    template, context = _start(tmp_path / "template", cfg, desc)
    producer.run_phases(cfg, "full", context)
    limit = 100000
    monkeypatch.setattr(producer, "MAX_PUBLISHED_BYTES", limit)
    for offset in (-1, 0, 1):
        root = tmp_path / f"{kind}-{offset}"
        staging = root / "staging" / template.name
        shutil.copytree(template, staging)
        out = root / "publication"
        target = limit + offset

        def build(temp, *_):
            data = b"probe\nx" if kind == "json" else b"probe\n" + b"x" * (target - 6)
            (temp / "probe.csv").write_bytes(data)
            return {"probe": "x" * (target - len(producer.pdb.canon({"probe": ""}) + "\n"))} if kind == "json" else {}

        if offset > 0:
            with pytest.raises(ValueError, match="bytes"):
                producer.finalize_planned(staging, out, context["authority"], context["plan"], build)
            assert not out.exists() and not (staging / "phases" / "FINAL.json").exists()
        else:
            final = producer.finalize_planned(staging, out, context["authority"], context["plan"], build)
            payload = out / ("telemetry.json" if kind == "json" else "probe.csv")
            assert payload.stat().st_size == target
            assert final["status"] == "PUBLISHED"
            producer._verified_publication(out)
            if kind == "json":
                assert json.loads(payload.read_bytes())["probe"]


@pytest.mark.parametrize("boundary", ["committed_hold_partition", "renamed_publication"])
def test_t7_native_resume_preserves_prefix_realization_and_csvs(tmp_path, monkeypatch, boundary):
    cfg, did = _authorized(tmp_path, monkeypatch, _t7_cfg(), "full")
    desc = producer.design_descriptor(cfg, "full")
    reference, ref_context = _start(tmp_path / "reference", cfg, desc)
    producer.run_phases(cfg, "full", ref_context)
    ref_out = tmp_path / "reference-out"
    _publish(reference, ref_context, desc, ref_out)
    expected = _b4f_durable(reference)
    staging, context = _start(tmp_path / "interrupted", cfg, desc)
    out, interrupted = tmp_path / "interrupted-out", []
    if boundary == "committed_hold_partition":
        real_partition = producer.partition

        def partition(*args, **kwargs):
            result = real_partition(*args, **kwargs)
            if args[1] == "HOLD" and not interrupted:
                interrupted.append(args[3])
                raise OSError("fixture interruption after committed HOLD partition")
            return result

        with monkeypatch.context() as fault:
            fault.setattr(producer, "partition", partition)
            with pytest.raises(OSError, match="committed HOLD"):
                producer.run_phases(cfg, "full", context)
        assert not (staging / "phases" / "HOLD.json").exists()
        upstream = {phase: json.loads((staging / "phases" / f"{phase}.json").read_bytes())["phase_digest"]
                    for phase in producer.PHASES[:4]}
        assert producer._verify_partition(staging, did, upstream, interrupted[0])[1] == 3
    else:
        producer.run_phases(cfg, "full", context)
        real_replace = os.replace

        def replace(src, dst, *args, **kwargs):
            result = real_replace(src, dst, *args, **kwargs)
            if Path(dst) == out:
                interrupted.append(Path(dst))
                raise OSError("fixture interruption after publication rename")
            return result

        with monkeypatch.context() as fault:
            fault.setattr(os, "replace", replace)
            with pytest.raises(OSError, match="publication rename"):
                _publish(staging, context, desc, out)
        assert _tree(out) == _tree(ref_out)
    assert len(interrupted) == 1
    assert (staging / "phases" / "CAL.json").is_file()
    assert not (staging / "phases" / "FINAL.json").exists()
    prefix = _b4f_durable(staging)
    assert prefix and {name: expected[name] for name in prefix} == prefix
    real_score, roles = producer.score_path_batch, []

    def score(desc, frame, fit, app, requests, **kwargs):
        requests = list(requests)
        actual_roles = [key[5] for key, _ in requests]
        assert "CAL_NULL" not in actual_roles, "committed CAL must not be rescored"
        if boundary == "renamed_publication":
            pytest.fail("an already published realization must not rescore any path")
        roles.extend(actual_roles)
        return real_score(desc, frame, fit, app, requests, **kwargs)

    def frozen(*_args, **_kwargs):
        pytest.fail("resume must not refit, choose DEV policies, or recalibrate committed CAL")

    with monkeypatch.context() as resumed:
        resumed.setattr(producer, "score_path_batch", score)
        resumed.setattr(producer, "fit_record", frozen)
        resumed.setattr(producer, "dev_choices", frozen)
        resumed.setattr(producer.pdb, "rank_threshold", frozen)
        reopened, context = _start(tmp_path / "interrupted", cfg, desc, resume=True)
        producer.run_phases(cfg, "full", context)
        _publish(reopened, context, desc, out)
    if boundary == "committed_hold_partition":
        assert set(roles) == {"HOLD_NULL", "ALT"}
    actual = _b4f_durable(staging)
    assert {name: actual[name] for name in prefix} == prefix
    assert actual == expected
    assert _tree(out) == _tree(ref_out)
    manifest = json.loads((out / "manifest.json").read_bytes())
    ref_manifest = json.loads((ref_out / "manifest.json").read_bytes())
    assert manifest["realization_id"] == ref_manifest["realization_id"]
    assert manifest["realization_descriptor"] == ref_manifest["realization_descriptor"]
    csvs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in out.glob("*.csv")}
    assert set(csvs) == {"aggregates.csv", "calibration.csv", "issues.csv", "selections.csv", "trials_summary.csv"}
    assert csvs == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in ref_out.glob("*.csv")}
