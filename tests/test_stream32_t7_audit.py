import builtins
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from scipy.stats import norm

from experiments import pca_info_online as producer


ROOT = Path(__file__).resolve().parents[1]
CSVS = {"aggregates.csv", "calibration.csv", "issues.csv", "selections.csv", "trials_summary.csv"}


def _json(path):
    return json.loads(path.read_bytes())


def _csv(root, name):
    return pd.read_csv(root / f"{name}.csv", float_precision="round_trip", keep_default_na=False,
                       dtype={"calibration_id": str, "setup_id": str, "policy_id": str})


def _fixture_argv(mode, root, monkeypatch):
    cfg = yaml.safe_load((ROOT / "configs" / f"pca_info_online_t7_{mode}.yaml").read_bytes())
    assert cfg["authorization"] is None
    cfg["dev"]["n_lib"] = 3
    cfg["modes"][mode]["sizes"].update(DEV_LIB=3, DEV_NULL=19, DEV_ALT=2, CAL_NULL=19, HOLD_NULL=50, ALT=3)
    cfg["bootstrap"]["B"] = 32
    desc = producer.design_descriptor(cfg, mode)
    did = producer.design_id(desc)
    go = root / "fixture-go.md"
    go.write_text(f"Synthetic pytest fixture {mode} only: {did}\n", encoding="utf-8")
    cfg["authorization"] = {"stage": mode, "design_id": did, "go_reference": {
        "path": go.name, "sha256": hashlib.sha256(go.read_bytes()).hexdigest()}}
    config = root / "fixture.yaml"
    config.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    monkeypatch.setattr(producer, "REPO_ROOT", root)
    log, publication = root / "run", root / "publication"
    argv = ["--mode", mode, "--config", str(config), "--log-dir", str(log), "--output-dir", str(publication)]
    return argv, log / "staging" / did[:16], publication


@pytest.mark.parametrize("mode,study", [("pilot", "PILOT_ONLY"), ("full", "DESCRIPTIVE_NOMINAL")])
def test_t7_native_unallocated_publication(mode, study, tmp_path, monkeypatch, capsys):
    argv, staging, publication = _fixture_argv(mode, tmp_path, monkeypatch)
    assert producer.main(argv) == 0, capsys.readouterr()
    phases = {name: _json(staging / "phases" / f"{name}.json") for name in producer.PHASES}
    assert [len(record["partitions"]) for record in phases.values()] == [4, 18, 4, 0, 4, 10]
    assert phases["NULL_PLAN"]["derived"] == {"status": "NOT_APPLICABLE"}
    assert all(len(part["key"]) == 6 for part in phases["CAL"]["partitions"])
    setups = phases["SETUP"]["derived"]["setups"]
    assert {tuple(json.loads(name)) for name in setups} == {("FITTED_LW_T7", 32, 0), ("FITTED_LW_T7", 239, 0)}
    for setup in setups.values():
        assert setup["information_basis"] == "GAUSSIAN_PROXY"
    assert {path.name for path in publication.glob("*.csv")} == CSVS
    selections = _csv(publication, "selections")
    assert set(selections.info_basis) == {"ORACLE_DIAGONAL_GAUSSIAN_PROXY"}
    assert set(selections.metric_basis) == {"ANALYTIC_PROXY"}
    aggregates = _csv(publication, "aggregates")
    assert set(aggregates.hypothesis) == {"", "NaN"}
    assert set(aggregates.status) == {study, "DESCRIPTIVE_V_RMST"}
    manifest = _json(publication / "manifest.json")
    local = {name for name, row in manifest["payloads"].items() if row["status"] == "LOCAL_HASHED_ONLY"}
    assert len(local) == 40 and all(name.startswith("partitions/") and name.endswith(".npz") for name in local)

    from tools.ops import audit_stream32_t7 as audit

    alt_record = staging / "phases" / "ALT.json"
    forbidden = {alt_record, staging / "phases" / "FINAL.json"}
    for row in phases["ALT"]["partitions"]:
        identity = {"design_id": manifest["design_id"], "key": row["key"], "upstream": phases["ALT"]["upstream"]}
        fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        forbidden.update(staging / "partitions" / (fingerprint + ext) for ext in (".json", ".npz"))
    original_open = Path.open
    builtin_open = builtins.open
    scandir = os.scandir

    def forbid(path):
        if not isinstance(path, int):
            path = Path(os.fsdecode(path)).resolve()
            assert path not in forbidden and not path.is_relative_to(publication), path

    def pre_alt_canary(path, *args, **kwargs):
        forbid(path)
        return original_open(path, *args, **kwargs)

    def pre_alt_builtin(path, *args, **kwargs):
        forbid(path)
        return builtin_open(path, *args, **kwargs)

    def pre_alt_list(path):
        forbid(path)
        return scandir(path)

    seal = tmp_path / "pre-alt.json"
    out = tmp_path / "analysis.json"
    with monkeypatch.context() as guarded:
        guarded.setattr(Path, "open", pre_alt_canary)
        guarded.setattr(builtins, "open", pre_alt_builtin)
        guarded.setattr(os, "scandir", pre_alt_list)
        digest = audit.pre_alt(staging, seal)
        assert digest == hashlib.sha256(seal.read_bytes()).hexdigest()
        pre = _json(seal)
        assert pre["verdict"] == "PASS"
        coverage = {(cell["role"], cell["dimension"], cell["application"], cell["kind"], cell["family"])
                    for cell in pre["replay"]}
        known = {(role, n, app, kind, None) for role in ("CAL_NULL", "HOLD_NULL") for n in (32, 239)
                 for app in ("MARKET", "RESIDUAL") for kind in ("ONLINE", "STATIC")}
        known |= {(role, n, row.application, "ORACLE", row.family)
                  for role in ("CAL_NULL", "HOLD_NULL") for n in (32, 239)
                  for row in selections[["application", "family"]].drop_duplicates().itertuples()}
        assert coverage == known
        assert len(pre["head"]) == 2 and all(len(row["I_E"]) == 16 for row in pre["head"].values())
        for geometry in pre["head"].values():
            assert geometry["I_E"][:8] == pytest.approx(geometry["I_E"][:-9:-1])
            assert np.all(np.asarray(geometry["I_P4"]) <= np.asarray(geometry["I_E"]))
        assert {row["status"] for row in pre["hold"].values()} == {
            "NULL_VALIDATED", "NULL_INCONCLUSIVE", "NULL_FAILED"}
        zero = next(row for row in pre["hold"].values() if row["k"] == 0)
        assert zero["lo"] == 0 and zero["hi"] == pytest.approx(1 - 0.05 ** (1 / zero["n"]))
        with pytest.raises(audit.AuditError, match="seal SHA-256"):
            audit.audit_alt(staging, publication, seal, "0" * 64, tmp_path / "refused-sha.json", authority_root=tmp_path)
        with pytest.raises(audit.AuditError, match="inside an input tree"):
            audit.audit_alt(staging, publication, alt_record, digest, tmp_path / "refused-location.json",
                            authority_root=tmp_path)
        rejected = tmp_path / "rejected-seal.json"
        rejected.write_text(json.dumps({**pre, "verdict": "DESIGN_REFUSED"}, sort_keys=True, separators=(",", ":"))
                            + "\n", encoding="utf-8")
        with pytest.raises(audit.AuditError, match="pre-ALT verdict"):
            audit.audit_alt(staging, publication, rejected, hashlib.sha256(rejected.read_bytes()).hexdigest(),
                            tmp_path / "refused-verdict.json", authority_root=tmp_path)
        cal = staging / "phases" / "CAL.json"
        source = cal.read_bytes()
        try:
            cal.write_bytes(source + b"\n")
            with pytest.raises(audit.AuditError, match="sealed input"):
                audit.audit_alt(staging, publication, seal, digest, tmp_path / "refused-input.json",
                                authority_root=tmp_path)
        finally:
            cal.write_bytes(source)

        bad = json.loads(source)
        row = next(iter(bad["derived"]["thresholds"].values()))
        row["h"] = float(np.nextafter(row["h"], np.inf))

        def canonical(obj):
            return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)

        identity = {key: bad[key] for key in ("design_id", "phase", "upstream", "derived")}
        identity["partitions"] = [[canonical(row["key"]), row["sha256"]] for row in bad["partitions"]]
        bad["phase_digest"] = hashlib.sha256(canonical(identity).encode()).hexdigest()
        refusal = tmp_path / "refused-cal.json"
        try:
            cal.write_text(canonical(bad) + "\n", encoding="utf-8")
            with pytest.raises(audit.AuditError, match="CAL thresholds differ from their raw maxima"):
                audit.pre_alt(staging, refusal)
        finally:
            cal.write_bytes(source)
        refused = _json(refusal)
        assert refused["verdict"] == "DESIGN_REFUSED"
        assert refused["inputs"]["staging/phases/CAL.json"] == hashlib.sha256((canonical(bad) + "\n").encode()).hexdigest()

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in publication.iterdir()}
    foreign = publication / "foreign.csv"
    foreign.touch()
    try:
        with pytest.raises(audit.AuditError, match="publication inventory"):
            audit.audit_alt(staging, publication, seal, digest, tmp_path / "refused-foreign.json", authority_root=tmp_path)
    finally:
        foreign.unlink()
    if mode == "pilot":
        payload = min(path for path in forbidden if path.suffix == ".npz")
        original = payload.read_bytes()
        corrupt = original + b"A2"
        report_path = tmp_path / "refused-alt.json"
        try:
            payload.write_bytes(corrupt)
            with pytest.raises(audit.AuditError, match="ALT partition.sha256"):
                audit.audit_alt(staging, publication, seal, digest, report_path, authority_root=tmp_path)
        finally:
            payload.write_bytes(original)
        evidence = _json(report_path)
        assert evidence["verdict"] == "DESIGN_REFUSED"
        assert evidence["inputs"][f"staging/partitions/{payload.name}"] == hashlib.sha256(corrupt).hexdigest()
    alt_sha = audit.audit_alt(staging, publication, seal, digest, out, authority_root=tmp_path)
    report = _json(out)
    assert alt_sha == hashlib.sha256(out.read_bytes()).hexdigest()
    assert report["pre_alt_sha256"] == digest and report["realization_id"] == manifest["realization_id"]
    assert report["verdict"] == "PASS"
    assert len(report["v_rmst"]) == 4 and len(report["alt_replay"]) == len(selections)
    assert {(row["application"], row["family"], row["calibration_id"]) for row in report["alt_replay"]} == {
        (row.application, row.family, row.calibration_id) for row in selections.itertuples()}
    status_by_id = _csv(publication, "trials_summary").query("role == 'HOLD_NULL'").set_index("calibration_id")
    expected_failures = set()
    for text in aggregates.query("record_kind == 'DESCRIPTIVE_CONTRAST'").inference_json:
        row = json.loads(text)
        cid, rid = row["candidate_calibration_id"], row["reference_calibration_id"]
        assert row["candidate_null_status"] == status_by_id.loc[cid, "null_status"]
        assert row["reference_null_status"] == status_by_id.loc[rid, "null_status"]
        if "NULL_FAILED" in (row["candidate_null_status"], row["reference_null_status"]):
            expected_failures.add((row["family"], cid, rid))
    marked = report["not_claimable"]
    assert expected_failures == {(row["family"], row["candidate_calibration_id"], row["reference_calibration_id"])
                                 for row in marked}
    assert expected_failures and all(row["analysis_status"] == "NULL_FAILED — NOT_CLAIMABLE" for row in marked)
    assert before == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in publication.iterdir()}


def test_independent_statistical_boundaries():
    from tools.ops import audit_stream32_t7 as audit

    maxima = np.r_[np.arange(37), [40.0, 40.0]]
    h, r, alarms = audit.calibration(maxima, 0.05)
    assert (h, r, alarms) == (np.nextafter(40.0, np.inf), 1, 0)
    assert audit.first_crossing(np.array([40.0, h]), h) == 2
    assert audit.first_crossing(np.array([40.0]), h) == -1
    with pytest.raises(audit.AuditError, match="predictive rank"):
        audit.calibration(maxima[:18], 0.05)

    tail, n = 0.05, 50
    assert audit.clopper_pearson(0, n, tail) == pytest.approx((0.0, 1 - tail ** (1 / n)))
    assert audit.clopper_pearson(n, n, tail) == pytest.approx((tail ** (1 / n), 1.0))
    for k in (0, 3, 15):
        assert audit.clopper_pearson(k, n, tail) == pytest.approx(producer.cp_bounds(k, n, tail), abs=1e-12)

    z2, tail = norm.isf(0.025) ** 2, 0.025
    assert audit.tango(0, 0, n, tail) == pytest.approx((-z2 / (n + z2), z2 / (n + z2)))
    assert audit.tango(n, 0, n, tail) == pytest.approx(((n - z2) / (n + z2), 1.0))
    positive = audit.tango(9, 2, n, tail)
    negative = audit.tango(2, 9, n, tail)
    assert negative == pytest.approx((-positive[1], -positive[0]), abs=2e-12)
    assert positive == pytest.approx(producer.tango_interval(9, 2, n, tail), abs=2e-12)


def test_dev_prefix_statistics_recompute_every_candidate():
    from tools.ops import audit_stream32_t7 as audit

    scores = np.array([[[1., 3.], [2., 0.], [-4., 2.]], [[0., 0.], [2., -2.], [2., 2.]]])
    depths, s2 = [1, 2], 0.2
    expected = np.array([[[max(
        sum((s2 * segment[:, axis].sum() ** 2 / (1 + s2 * len(segment)) - np.log(1 + s2 * len(segment))) / 2
            for axis in range(d))
        for segment in (path[start:stop] for start in range(stop))) for d in depths]
        for stop in range(1, len(path) + 1)] for path in scores])
    assert audit._dev_scans(scores, depths, s2) == pytest.approx(expected, abs=1e-14)
