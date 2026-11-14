import concurrent.futures
import copy
import gzip
import hashlib
import itertools
import json
import math
import multiprocessing
import os
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from experiments import e4_alignment as e4
from experiments import e4_production as ep
from experiments import pca_drift_benchmark as pdb
from jepadrift import pipelines

BASE = {"stream": 19, "seed": 42, "rho": 0.4, "H": 30, "alpha": 0.05, "grid": [4, 6], "T_fit": 60, "n_cal": 20,
        "n_hold": 20, "n_alt": 20, "B_boot": 50, "pilot_n": 4, "prefix_k": 2, "info_divisor": 40.0,
        "backgrounds": {"gaussian": None, "t7": 7}, "fpr_margin": 0.01, "qualification": 0.95,
        "limits": {"rss_gib": 8.0, "invocation_seconds": 1800, "block_paths": 8}}


def cfg(**kw):
    c = copy.deepcopy(BASE)
    c.update(kw)
    return e4.validate_config(c)


def run_all(root, c, mode="full", block=7, reverse=False, workers=1, config=None):
    """Every planned partition, phase by phase; blocks of a phase reversed or spread over spawned processes."""
    identity = ep.production_identity(c, mode, config)
    ep.write_plan(c, mode, root, identity, block)
    for prefix in ("scalar_cal", "fit_", "calmax_", "thresholds", "trials_", "merge", "analysis"):
        plan = ep.plan_partitions(c, mode, block, ep.fit_statuses(c, root, identity))
        group = [p for p in plan if p.startswith(prefix)]
        group = group[::-1] if reverse else group
        if workers > 1 and len(group) > 1:
            ctx = multiprocessing.get_context("spawn")
            with concurrent.futures.ProcessPoolExecutor(workers, mp_context=ctx) as pool:
                list(pool.map(ep.run_phase, *zip(*[(c, mode, root, identity, p) for p in group])))
        else:
            for p in group:
                ep.run_phase(c, mode, root, identity, p)
    assert ep.next_pending(c, mode, root, identity) is None
    return identity


def tree(root):
    return {p.relative_to(root).as_posix(): pdb.file_sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}


def logical(root):
    part = root / "partitions"
    out = {"manifest": (part / "merge" / "manifest.json").read_bytes()}
    for rel in ("thresholds/calibration.csv", "thresholds/cells.csv"):
        out[rel] = (part / rel).read_bytes()
    for p in sorted((part / "analysis" / "analysis").iterdir()):
        out[p.name] = p.read_bytes()
    return out


def test_block_ranges_cover_exactly():
    assert ep.block_ranges(40, 8) == [(0, 8), (8, 16), (16, 24), (24, 32), (32, 40)]
    assert ep.block_ranges(40, 7)[-1] == (35, 40)
    assert ep.block_ranges(5, 1) == [(i, i + 1) for i in range(5)]
    assert ep.block_ranges(5, 5) == [(0, 5)]
    assert ep.block_ranges(5, 9) == [(0, 5)]
    assert ep.block_ranges(2000, 250)[-1] == (1750, 2000) and len(ep.block_ranges(2000, 250)) == 8
    assert len(ep.block_ranges(2000, 125)) == 16
    for n, b in itertools.product([1, 7, 40, 2000], [1, 3, 125, 250, 2000]):
        r = ep.block_ranges(n, b)
        assert r[0][0] == 0 and r[-1][1] == n
        assert all(s < t for s, t in r) and all(r[k][1] == r[k + 1][0] for k in range(len(r) - 1))
    for n, b in ((10, 0), (0, 5), (10, True), (10, 2.0)):
        with pytest.raises(ValueError):
            ep.block_ranges(n, b)


def test_pid_parser_refuses_unsafe_ids():
    c = cfg()
    assert ep.parse_pid("calmax_gaussian_N4_r0000-0007", c, "full", 7) == {
        "kind": "calmax", "background": "gaussian", "N": 4, "role": "calibration", "start": 0, "stop": 7}
    assert ep.parse_pid("trials_t7_N6_alternative_r0014-0020", c, "full", 7)["stop"] == 20
    assert ep.parse_pid("fit_t7_N6", c, "cost_fixture", 7) == {"kind": "fit", "background": "t7", "N": 6}
    assert ep.parse_pid("thresholds", c, "cost_fixture", 7) == {"kind": "thresholds"}
    assert ep.parse_pid("cost_t7_N6_holdout", c, "production_pilot")["role"] == "holdout"
    bad = ["calmax:gaussian:4", "../fit_gaussian_N4", "fit_gaussian_N4/x", "fit_gaussian_N5", "fit_gaussian_n4",
           "fit_gaussian_N04", "fit_cauchy_N4", "calmax_gaussian_N4_r0000-0008", "calmax_gaussian_N4_r0007-0007",
           "trials_gaussian_N4_holdout_r0014-0021", "trials_gaussian_N4_calibration_r0000-0007",
           "cost_gaussian_N4_holdout", "calmax_gaussian_N4_r000-0007", "", "session"]
    for pid in bad:
        with pytest.raises(ValueError):
            ep.parse_pid(pid, c, "full", 7)
    for pid in ("fit_gaussian_N4", "scalar_cal", "merge"):
        with pytest.raises(ValueError):
            ep.parse_pid(pid, c, "production_pilot")
    with pytest.raises(ValueError):
        ep.parse_pid("cost_gaussian_N4_holdout", c, "cost_fixture", 7)


def test_plan_counts_cover_354_and_690_when_every_fit_is_ok():
    full = e4.validate_config(e4.load_config(e4.CONFIG))
    assert len(ep.plan_partitions(full, "full", 250)) == 354
    assert len(ep.plan_partitions(full, "full", 125)) == 690
    plan = ep.plan_partitions(full, "full", 250)
    assert plan[0] == "scalar_cal" and plan[-2:] == ["merge", "analysis"]
    assert plan.index("thresholds") > max(i for i, p in enumerate(plan) if p.startswith("calmax_"))
    assert plan.index("thresholds") < min(i for i, p in enumerate(plan) if p.startswith("trials_"))
    refused = {cell: "OK" for cell in ep.cells_of(full)}
    refused[("t7", 500)] = "EIGENVALUE_TIE_UNRESOLVED"
    assert len(ep.plan_partitions(full, "full", 250, refused)) == 354 - 8
    assert not any(p.startswith("calmax_t7_N500") for p in ep.plan_partitions(full, "full", 250, refused))


def test_identity_separates_mode_and_space_and_excludes_geometry():
    c = cfg()
    full, fixture = ep.production_identity(c, "full"), ep.production_identity(c, "cost_fixture")
    assert full["space"] == "science" and fixture["space"] == "pilot" and full["mode"] == "full"
    assert full["session_id"] != fixture["session_id"]
    assert "experiments/e4_production.py" in full["code"] and "experiments/e4_alignment.py" in full["code"]
    assert full == ep.production_identity(c, "full")
    assert not {"block", "jobs", "workers", "time"} & set(full)
    with pytest.raises(ValueError):
        ep.production_identity(c, "science")


def test_nested_partition_writer_records_relative_paths_and_resumes(tmp_path):
    identity = {"session_id": "s1", "mode": "unit"}
    calls = []

    def compute(tmp):
        calls.append(1)
        (tmp / "sub" / "deep").mkdir(parents=True)
        (tmp / "sub" / "deep" / "a.txt").write_text("a", encoding="utf-8")
        (tmp / "b.txt").write_text("b", encoding="utf-8")
        return {"answer": 1}

    assert ep.run_production_partition(tmp_path, "merge", identity, compute) == ("COMPLETE", [])
    final = tmp_path / "partitions" / "merge"
    record = json.loads((final / "partition.json").read_text(encoding="utf-8"))
    assert record["files"] == {"b.txt": pdb.file_sha256(final / "b.txt"),
                               "sub/deep/a.txt": pdb.file_sha256(final / "sub" / "deep" / "a.txt")}
    assert record["status"] == "COMPLETE" and record["objects"] == {"answer": 1}
    before = tree(tmp_path)
    assert ep.run_production_partition(tmp_path, "merge", identity, compute) == ("SKIPPED_COMPLETE", [])
    assert calls == [1] and tree(tmp_path) == before
    assert ep.load_partition(tmp_path, "merge", identity)["objects"] == {"answer": 1}

    (final / "sub" / "deep" / "a.txt").write_text("tampered", encoding="utf-8")
    with pytest.raises(pdb.PartitionMismatch):
        ep.run_production_partition(tmp_path, "merge", identity, compute)
    (final / "sub" / "deep" / "a.txt").write_text("a", encoding="utf-8")
    for intruder in ("file", "dir", "link"):
        target = final / "sub" / "intruder"
        if intruder == "file":
            target.write_text("x", encoding="utf-8")
        elif intruder == "dir":
            target.mkdir()
        else:
            os.symlink(final / "b.txt", target)
        with pytest.raises(pdb.PartitionMismatch):
            ep.load_partition(tmp_path, "merge", identity)
        target.unlink() if intruder != "dir" else target.rmdir()
    assert ep.load_partition(tmp_path, "merge", identity)["status"] == "COMPLETE"
    with pytest.raises(pdb.PartitionMismatch):
        ep.load_partition(tmp_path, "merge", {"session_id": "other"})

    def failing(tmp):
        (tmp / "partial.txt").write_text("p", encoding="utf-8")
        raise RuntimeError("interrupted before rename")

    with pytest.raises(RuntimeError):
        ep.run_production_partition(tmp_path, "analysis", identity, failing)
    assert not (tmp_path / "partitions" / "analysis").exists()
    status, leftovers = ep.run_production_partition(tmp_path, "analysis", identity, compute)
    assert status == "COMPLETE" and len(leftovers) == 1 and leftovers[0].startswith("analysis.tmp-")
    assert (tmp_path / "partitions" / leftovers[0] / "partial.txt").read_text(encoding="utf-8") == "p"


def test_nested_partition_writer_refuses_a_symlink_produced_by_compute(tmp_path):
    def compute(tmp):
        (tmp / "a.txt").write_text("a", encoding="utf-8")
        os.symlink(tmp / "a.txt", tmp / "alias.txt")
        return {}

    with pytest.raises(pdb.PartitionMismatch):
        ep.run_production_partition(tmp_path, "merge", {"session_id": "s"}, compute)
    assert not (tmp_path / "partitions" / "merge").exists()


def test_fair_fragments_are_canonical_and_gzip_deterministic(tmp_path):
    df = pd.DataFrame({"background": ["gaussian"] * 3, "N": [4, 4, 4], "replicate": [0, 1, 2],
                       "j_k": [0.1, 1.0 / 3.0, 2.0 ** -40], "claim_flag": ["ORACLE_DIAGNOSTIC"] * 3})
    pipelines.save_fair_csv(df, tmp_path / "plain.csv")
    info = ep.write_table(df, tmp_path / "a" / "x.csv.gz")
    again = ep.write_table(df, tmp_path / "b" / "x.csv.gz")
    raw = (tmp_path / "a" / "x.csv.gz").read_bytes()
    assert raw == (tmp_path / "b" / "x.csv.gz").read_bytes() and info == again
    assert raw[3] & 0x08 == 0 and raw[4:8] == b"\x00\x00\x00\x00"
    assert gzip.decompress(raw) == (tmp_path / "plain.csv").read_bytes()
    assert info == {"rows": 3, "sha256_csv": pdb.file_sha256(tmp_path / "plain.csv"),
                    "bytes_csv": (tmp_path / "plain.csv").stat().st_size,
                    "sha256_gz": hashlib.sha256(raw).hexdigest(), "bytes_gz": len(raw)}
    assert not (tmp_path / "a" / "x.csv").exists()
    back = ep.read_table(tmp_path / "a" / "x.csv.gz")
    assert back["j_k"].tolist() == df["j_k"].tolist()


def test_tiles_require_the_exact_planned_ranges():
    expected = ep.block_ranges(20, 7)
    ep.tiles(set(expected), expected, "calmax_gaussian_N4")
    for found in (set(expected) - {(14, 20)}, set(expected) - {(0, 7)}, set(expected) | {(0, 3)},
                  set(expected) | {(20, 21)}, set(expected) - {(7, 14)} | {(7, 13), (13, 14)}, set()):
        with pytest.raises(ep.IncompleteWork):
            ep.tiles(found, expected, "calmax_gaussian_N4")


def test_production_matches_prototype_bytes(tmp_path):
    c = cfg()
    proto = e4.run_cells(c, "science")
    shas = e4.write_tables(tmp_path / "proto", proto)
    root = tmp_path / "prod"
    run_all(root, c, block=7)
    part = root / "partitions"
    manifest = json.loads((part / "merge" / "manifest.json").read_text(encoding="utf-8"))
    for table in ("trials", "diagnostics", "diagnostics_axes"):
        assert manifest["tables"][table]["sha256_whole"] == shas[table]
    assert manifest["tables"]["trials"]["rows"] == len(proto["trials"])
    assert manifest["tables"]["diagnostics_axes"]["rows"] == len(proto["diagnostics_axes"])
    assert pdb.file_sha256(part / "thresholds" / "calibration.csv") == shas["calibration"]
    assert pdb.file_sha256(part / "thresholds" / "cells.csv") == shas["cells"]
    expected = {"holdout_fpr.csv": e4.holdout_fpr(proto["trials"])}
    for reading in e4.READINGS:
        res = e4.analyse(proto["trials"], c, "science", reading)
        expected.update({f"{k}_{reading}.csv": res[k] for k in ("cells", "contrasts", "warnings")})
    for name, df in expected.items():
        pipelines.save_fair_csv(df, tmp_path / name)
        assert (part / "analysis" / "analysis" / name).read_bytes() == (tmp_path / name).read_bytes(), name
    assert sorted(p.name for p in (part / "analysis" / "analysis").iterdir()) == sorted(expected)


def test_logical_outputs_invariant_to_geometry_order_and_processes(tmp_path):
    c = cfg()
    runs = {"b1": dict(block=1), "b3_reverse": dict(block=3, reverse=True), "bn": dict(block=20),
            "b7_spawn3": dict(block=7, workers=3)}
    outputs, lineages = {}, {}
    for name, kw in runs.items():
        run_all(tmp_path / name, c, **kw)
        outputs[name] = logical(tmp_path / name)
        lineages[name] = (tmp_path / name / "partitions" / "merge" / "lineage.json").read_bytes()
    first = outputs["b1"]
    assert all(out == first for out in outputs.values())
    assert lineages["b1"] != lineages["bn"]
    run_all(tmp_path / "seed43", cfg(seed=43), block=7)
    assert logical(tmp_path / "seed43")["manifest"] != first["manifest"]


def test_maxima_fragment_is_sorted_by_method_and_replicate(tmp_path):
    c = cfg()
    root = tmp_path / "r"
    run_all(root, c, block=3, reverse=True)
    frag = ep.read_table(root / "partitions" / "merge" / "calibration_maxima" / "gaussian_N4.csv.gz")
    assert list(frag.columns) == ep.MAX_COLUMNS and len(frag) == 3 * c["n_cal"]
    assert frag[["method", "replicate"]].equals(frag.sort_values(["method", "replicate"])[["method", "replicate"]]
                                                .reset_index(drop=True))
    cal = pd.read_csv(root / "partitions" / "thresholds" / "calibration.csv", float_precision="round_trip")
    for m, g in frag.groupby("method"):
        row = cal[(cal["background"] == "gaussian") & (cal["N"] == 4) & (cal["method"] == m)].iloc[0]
        assert row["maxima_sha256"] == pdb.array_sha256(g.sort_values("replicate")["max_log"].to_numpy())


def test_refused_basis_cell_matches_prototype(tmp_path, monkeypatch):
    real = e4.fit_cell

    def fit(c_, background, N, space):
        if (background, N) == ("t7", 6):
            raise e4.EigenTieUnresolved("forced tie", [[0, 1]], [0.0])
        return real(c_, background, N, space)

    monkeypatch.setattr(e4, "fit_cell", fit)
    c = cfg()
    shas = e4.write_tables(tmp_path / "proto", e4.run_cells(c, "science"))
    root = tmp_path / "prod"
    run_all(root, c, block=7)
    part = root / "partitions"
    assert not any(p.name.startswith("calmax_t7_N6") for p in part.iterdir())
    manifest = json.loads((part / "merge" / "manifest.json").read_text(encoding="utf-8"))
    for table in ("trials", "diagnostics", "diagnostics_axes"):
        assert manifest["tables"][table]["sha256_whole"] == shas[table]
    assert pdb.file_sha256(part / "thresholds" / "calibration.csv") == shas["calibration"]
    assert pdb.file_sha256(part / "thresholds" / "cells.csv") == shas["cells"]
    trials = ep.read_table(part / "merge" / "trials" / "t7_N6.csv.gz")
    assert set(trials["method"]) == {"EW", "O-dir"}
    assert not (part / "merge" / "diagnostics_axes" / "t7_N6.csv.gz").exists()
    contrasts = pd.read_csv(part / "analysis" / "analysis" / "contrasts_predictive_rank.csv")
    assert set(contrasts.loc[contrasts["background"] == "t7", "qualification"]) == {"NOT_IDENTIFIED"}


def test_resume_skips_complete_without_recompute(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = run_all(root, c, block=7)
    before = tree(root)

    def boom(*a, **k):
        raise AssertionError("recomputed")

    monkeypatch.setattr(e4, "method_log_path", boom)
    monkeypatch.setattr(e4, "fit_cell", boom)
    monkeypatch.setattr(e4, "scalar_calibration", boom)
    for pid in ep.plan_partitions(c, "full", 7, ep.fit_statuses(c, root, identity)):
        assert ep.run_phase(c, "full", root, identity, pid) == "SKIPPED_COMPLETE"
    assert tree(root) == before


def test_tiling_refuses_holes_overlaps_and_foreign_blocks(tmp_path):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "full")
    ep.write_plan(c, "full", root, identity, 7)
    for pid in ep.plan_partitions(c, "full", 7):
        if pid == "thresholds":
            break
        ep.run_phase(c, "full", root, identity, pid)
    part = root / "partitions"
    hidden = tmp_path / "hidden"
    shutil.move(part / "calmax_gaussian_N4_r0014-0020", hidden)
    with pytest.raises(ep.IncompleteWork):
        ep.run_phase(c, "full", root, identity, "thresholds")
    assert not (part / "thresholds").exists()
    shutil.move(hidden, part / "calmax_gaussian_N4_r0014-0020")
    shutil.copytree(part / "calmax_gaussian_N4_r0000-0007", part / "calmax_gaussian_N4_r0000-0003")
    with pytest.raises((ep.IncompleteWork, ValueError)):
        ep.run_phase(c, "full", root, identity, "thresholds")
    assert not (part / "thresholds").exists()
    shutil.rmtree(part / "calmax_gaussian_N4_r0000-0003")
    ep.run_phase(c, "full", root, identity, "thresholds")
    for pid in ep.plan_partitions(c, "full", 7, ep.fit_statuses(c, root, identity)):
        if pid.startswith("trials_"):
            ep.run_phase(c, "full", root, identity, pid)
    shutil.move(part / "trials_t7_N6_alternative_r0014-0020", hidden)
    with pytest.raises(ep.IncompleteWork):
        ep.run_phase(c, "full", root, identity, "merge")
    assert not (part / "merge").exists()
    assert ep.next_pending(c, "full", root, identity) == "trials_t7_N6_alternative_r0014-0020"


def test_last_replicate_block_is_required(tmp_path):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "full")
    ep.write_plan(c, "full", root, identity, 1)
    for pid in ep.plan_partitions(c, "full", 1):
        if pid == "thresholds":
            break
        if pid != "calmax_t7_N6_r0019-0020":
            ep.run_phase(c, "full", root, identity, pid)
    with pytest.raises(ep.IncompleteWork):
        ep.run_phase(c, "full", root, identity, "thresholds")
    ep.run_phase(c, "full", root, identity, "calmax_t7_N6_r0019-0020")
    ep.run_phase(c, "full", root, identity, "thresholds")


def test_divergences_are_refused_without_mutation(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "full")
    ep.write_plan(c, "full", root, identity, 7)
    with pytest.raises(pdb.PartitionMismatch):
        ep.write_plan(c, "full", root, identity, 3)
    for pid in ep.plan_partitions(c, "full", 7):
        if pid.startswith("trials_"):
            break
        ep.run_phase(c, "full", root, identity, pid)
    part = root / "partitions"
    before = tree(root)
    gz = part / "calmax_gaussian_N6_r0007-0014" / "maxima.csv.gz"
    original = gz.read_bytes()
    gz.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    tampered = tree(root)
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_campaign(c, "full", root, identity)
    assert tree(root) == tampered
    gz.write_bytes(original)
    cal = part / "thresholds" / "calibration.csv"
    text = cal.read_bytes()
    cal.write_bytes(text.replace(b"OK", b"OX", 1))
    with pytest.raises(pdb.PartitionMismatch):
        ep.run_phase(c, "full", root, identity, "trials_gaussian_N4_holdout_r0000-0007")
    cal.write_bytes(text)
    assert tree(root) == before
    real = e4.fit_cell

    def shifted(c_, background, N, space):
        cell = real(c_, background, N, space)
        return {**cell, "basis_hash_e4": "0" * 64}

    monkeypatch.setattr(e4, "fit_cell", shifted)
    with pytest.raises(pdb.PartitionMismatch):
        ep.run_phase(c, "full", root, identity, "trials_gaussian_N4_holdout_r0000-0007")
    assert tree(root) == before
    monkeypatch.setattr(e4, "fit_cell", real)
    with pytest.raises(pdb.PartitionMismatch):
        ep.run_phase(cfg(seed=43), "full", root, ep.production_identity(cfg(seed=43), "full"), "merge")
    assert tree(root) == before


def test_threshold_barrier_blocks_monitoring(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "full")
    ep.write_plan(c, "full", root, identity, 7)
    for pid in ("scalar_cal", "fit_gaussian_N4"):
        ep.run_phase(c, "full", root, identity, pid)
    calls = []
    monkeypatch.setattr(e4, "role_path", lambda *a, **k: calls.append(a) or (_ for _ in ()).throw(AssertionError))
    for pid in ("trials_gaussian_N4_holdout_r0000-0007", "trials_gaussian_N4_alternative_r0000-0007", "thresholds",
                "calmax_t7_N6_r0000-0007", "merge", "analysis"):
        with pytest.raises(ep.IncompleteWork):
            ep.run_phase(c, "full", root, identity, pid)
        assert not (root / "partitions" / pid).exists()
    assert calls == []


def test_calmax_of_a_refused_cell_is_refused(tmp_path, monkeypatch):
    real = e4.fit_cell

    def fit(c_, background, N, space):
        if (background, N) == ("gaussian", 4):
            raise e4.EigenTieUnresolved("forced tie", [[0, 1]], [0.0])
        return real(c_, background, N, space)

    monkeypatch.setattr(e4, "fit_cell", fit)
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "full")
    ep.write_plan(c, "full", root, identity, 7)
    ep.run_phase(c, "full", root, identity, "fit_gaussian_N4")
    with pytest.raises(ep.IncompleteWork):
        ep.run_phase(c, "full", root, identity, "calmax_gaussian_N4_r0000-0007")


def test_axes_are_streamed_and_each_replicate_has_n_axes(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    real_read = pd.read_csv

    def guarded(path, *a, **k):
        p = Path(str(path))
        if p.name.startswith("axes.") or p.parent.name == "diagnostics_axes":
            raise AssertionError(f"J_k table loaded as a DataFrame: {path}")
        return real_read(path, *a, **k)

    monkeypatch.setattr(pd, "read_csv", guarded)
    run_all(root, c, block=7)
    monkeypatch.setattr(pd, "read_csv", real_read)
    real_diag = e4.oracle_diagnostics

    def short(cell, u, c_):
        d = real_diag(cell, u, c_)
        return {**d, "j_k": d["j_k"][:-1]} if cell["N"] == 6 else d

    monkeypatch.setattr(e4, "oracle_diagnostics", short)
    bad = tmp_path / "bad"
    with pytest.raises(ep.IncompleteWork):
        run_all(bad, c, block=7)
    assert not (bad / "partitions" / "merge").exists()


def coverage_tables(n=3):
    cells = pd.DataFrame([{"background": "gaussian", "N": 4, "status": "OK"},
                          {"background": "gaussian", "N": 6, "status": "EIGENVALUE_TIE_UNRESOLVED"}])
    cal = []
    for N, status in ((4, "OK"), (6, "EIGENVALUE_TIE_UNRESOLVED")):
        for m in e4.METHODS:
            st = "OK" if m in e4.SCALAR or status == "OK" else status
            st = "CALIBRATION_FAILED" if (N, m) == (4, "SPEC-prefix8") else st
            cal.append({"background": "gaussian", "N": N, "method": m, "status": st})
    cal = pd.DataFrame(cal)
    rows = []
    for N in (4, 6):
        methods = e4.METHODS if N == 4 else ("EW", "O-dir")
        for m, role, i in itertools.product(methods, ("holdout", "alternative"), range(n)):
            readings = ["anytime_valid_horizon"] + ([] if (N, m) == (4, "SPEC-prefix8") else ["predictive_rank"])
            rows += [{"background": "gaussian", "N": N, "method": m, "role": role, "replicate": i, "reading": r,
                      "first_hit": -1, "claim_flag": e4.ORACLE.get(m, "NONE")} for r in readings]
    return cells, cal, pd.DataFrame(rows, columns=e4.TRIAL_COLUMNS)


def test_trial_coverage_follows_cells_and_calibration():
    cells, cal, trials = coverage_tables()
    counts = {"holdout": 3, "alternative": 3}
    ep.check_trials(trials, cells, cal, counts)
    for broken in (trials.drop(index=5), pd.concat([trials, trials.iloc[[0]]], ignore_index=True),
                   trials[~((trials["N"] == 4) & (trials["method"] == "EW") & (trials["reading"] == "predictive_rank"))],
                   pd.concat([trials, trials.iloc[[0]].assign(N=6, method="SPEC-full")], ignore_index=True),
                   pd.concat([trials, trials.iloc[[0]].assign(method="SPEC-prefix8", reading="predictive_rank",
                                                              replicate=0)], ignore_index=True),
                   trials.assign(replicate=trials["replicate"].where(trials["replicate"] != 2, 3))):
        with pytest.raises(ep.IncompleteWork):
            ep.check_trials(broken, cells, cal, counts)


def test_scientific_route_reads_no_data_file(tmp_path, monkeypatch):
    import builtins
    roots = [str(e4.REPO_ROOT / "data"), str((e4.REPO_ROOT / "data").resolve())]

    def forbidden(path):
        p = Path(path)
        return any(str(q).startswith(r) for q in (p.absolute(), p.resolve()) for r in roots)

    def guard(real):
        def wrapped(path, *a, **k):
            if isinstance(path, (str, Path)) and forbidden(path):
                raise AssertionError(f"data access {path}")
            return real(path, *a, **k)
        return wrapped

    monkeypatch.setattr(builtins, "open", guard(builtins.open))
    monkeypatch.setattr(np, "load", guard(np.load))
    monkeypatch.setattr(pd, "read_csv", guard(pd.read_csv))
    with pytest.raises(AssertionError):
        open(e4.REPO_ROOT / "data" / "raw" / "probe.csv")
    state = np.random.get_state()[1].copy()
    run_all(tmp_path / "r", cfg(), block=7)
    assert np.array_equal(np.random.get_state()[1], state)


def write_cfg(tmp_path, **kw):
    import yaml
    c = copy.deepcopy(BASE)
    c.update(kw)
    path = tmp_path / "e4.yaml"
    path.write_text(yaml.safe_dump(c), encoding="utf-8")
    return path


def attempt(attempts, k, rc=None, user=1.0, system=0.5, rss=1000, cmd="--phase next", status_line=True):
    d = attempts / f"A{k:07d}"
    d.mkdir(parents=True)
    (d / "cmd.txt").write_text(cmd + "\n", encoding="utf-8")
    if rc is not None:
        head = f"Command exited with non-zero status {rc}\n" if rc and status_line else ""
        (d / "time.txt").write_text(f"{head}{user:.2f} {system:.2f} {user + system:.2f} {rss} {rc}\n", encoding="utf-8")
        (d / "exit.txt").write_text(f"{rc}\n", encoding="utf-8")
    return d.name


class Host:
    """Host-side attempt bookkeeping around in-process CLI calls: reserve, run with E4_ATTEMPT_ID, finalize."""

    def __init__(self, tmp_path, monkeypatch):
        self.attempts, self.monkeypatch, self.k = tmp_path / "attempts", monkeypatch, 0
        self.limits = []
        monkeypatch.setattr(ep.resource, "setrlimit", lambda which, value: self.limits.append((which, value)))

    def __call__(self, args):
        self.k += 1
        aid = attempt(self.attempts, self.k, cmd=" ".join(map(str, args)))
        self.monkeypatch.setenv("E4_ATTEMPT_ID", aid)
        rc = ep.main([str(a) for a in args] + ["--attempts", str(self.attempts)])
        d = self.attempts / aid
        (d / "time.txt").write_text(f"0.10 0.01 0.11 1000 {rc}\n", encoding="utf-8")
        (d / "exit.txt").write_text(f"{rc}\n", encoding="utf-8")
        return rc

    def decide(self):
        decisions = self.attempts.parent / "decisions"
        decisions.mkdir(exist_ok=True)
        (decisions / f"A{self.k:07d}.txt").write_text("expected refusal reviewed\n", encoding="utf-8")


def test_plan_cli_prints_only_k_and_next_ends_with_code_10(tmp_path, monkeypatch, capsys):
    host = Host(tmp_path, monkeypatch)
    root = tmp_path / "w"
    base = ["--mode", "cost_fixture", "--root", root, "--config", write_cfg(tmp_path)]
    assert host(["--phase", "plan", "--block", 7] + base) == 0
    out = capsys.readouterr()
    plan = json.loads((root / "campaign_plan.json").read_text(encoding="utf-8"))
    assert out.out == f"{plan['K']}\n" and plan["block"] == 7 and plan["K"] == 44
    assert (ep.resource.RLIMIT_CPU, ep.CPU_RLIMIT_S) in host.limits
    codes = [host(["--phase", "next"] + base) for _ in range(plan["K"] - 1)]
    assert codes == [0] * (plan["K"] - 1)
    assert host(["--phase", "verify"] + base) == 5
    assert host(["--phase", "next"] + base) == 6
    host.decide()
    assert host(["--phase", "next"] + base) == 0
    assert host(["--phase", "next"] + base) == 10
    assert host(["--phase", "verify"] + base) == 0
    assert host(["--phase", "plan", "--block", 3] + base) == 5
    host.decide()
    capsys.readouterr()
    assert host(["--phase", "plan", "--block", 7] + base) == 0
    assert capsys.readouterr().out == f"{plan['K']}\n"


def test_full_mode_is_refused_without_activation(tmp_path, monkeypatch):
    host = Host(tmp_path, monkeypatch)
    root = tmp_path / "w"
    base = ["--mode", "full", "--root", root, "--config", write_cfg(tmp_path)]
    for args in (["--phase", "plan", "--block", 7], ["--phase", "next"], ["--phase", "run", "--partition", "scalar_cal"],
                 ["--phase", "publish", "--to", tmp_path / "pub"]):
        assert host(args + base) == 3
    (tmp_path / "act.json").write_text(json.dumps({"activated": True}), encoding="utf-8")
    assert host(["--phase", "plan", "--block", 7, "--activation", tmp_path / "act.json"] + base) == 3
    assert not root.exists() and not (tmp_path / "pub").exists()


def test_attempt_ledger_is_append_only_and_stops_on_unknown(tmp_path):
    att = tmp_path / "attempts"
    attempt(att, 1, rc=0, user=1.25, system=0.25)
    attempt(att, 2, rc=124, user=3.0, system=1.0)
    led = ep.ledger(att)
    assert led["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 1.5 + 4.0)
    assert [a["state"] for a in led["attempts"]] == ["MEASURED", "MEASURED"] and led["attempts"][1]["exit"] == 124
    snap = led["snapshot"]
    assert snap["cutoff"] == "A0000002" and snap["n_attempts"] == 2
    attempt(att, 3, rc=0)
    ep.check_snapshot(att, snap)
    original = (att / "A0000001" / "time.txt").read_text(encoding="utf-8")
    (att / "A0000001" / "time.txt").write_text("0.00 0.00 0.00 1000 0\n", encoding="utf-8")
    with pytest.raises(ep.GateStop):
        ep.check_snapshot(att, snap)
    (att / "A0000001" / "time.txt").write_text(original, encoding="utf-8")
    ep.check_snapshot(att, snap)
    attempt(att, 4)
    with pytest.raises(ep.GateStop):
        ep.ledger(att)
    assert ep.ledger(att, active="A0000004")["snapshot"]["n_attempts"] == 3
    attempt(att, 5)
    with pytest.raises(ep.GateStop):
        ep.ledger(att, active="A0000005")
    (att / "A0000004" / "time.txt").write_text("garbage\n", encoding="utf-8")
    (att / "A0000004" / "exit.txt").write_text("0\n", encoding="utf-8")
    with pytest.raises(ep.GateStop):
        ep.ledger(att, active="A0000005")
    with pytest.raises(ep.GateStop):
        ep.ledger(att, active="A0000099")


def test_gate_budget_disk_and_previous_exit(tmp_path, monkeypatch):
    att = tmp_path / "attempts"
    attempt(att, 1, rc=0, user=10.0, system=0.0)
    attempt(att, 2)
    led = ep.gate(att, "A0000002", 0.0, tmp_path)
    assert led["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 10.0)
    with pytest.raises(ep.GateStop):
        ep.gate(att, "A0000002", ep.CPU_CAP_S - ep.PRIOR_CPU_S - 10.0 - ep.NEXT_INVOCATION_CPU_S + 1.0, tmp_path)
    ep.gate(att, "A0000002", ep.CPU_CAP_S - ep.PRIOR_CPU_S - 10.0 - ep.NEXT_INVOCATION_CPU_S - 1.0, tmp_path)
    with pytest.raises(ep.GateStop):
        ep.gate(att, "A0000002", 0.0, tmp_path, ceiling_cpu_s=ep.PRIOR_CPU_S + 10.0 + ep.NEXT_INVOCATION_CPU_S - 1.0)
    monkeypatch.setattr(ep, "DISK_RESERVE_BYTES", 2 ** 62)
    with pytest.raises(ep.GateStop):
        ep.gate(att, "A0000002", 0.0, tmp_path)
    monkeypatch.setattr(ep, "DISK_RESERVE_BYTES", 2 ** 20)
    other = tmp_path / "other"
    attempt(other, 1, rc=124)
    attempt(other, 2)
    with pytest.raises(ep.GateStop):
        ep.gate(other, "A0000002", 0.0, tmp_path)
    (tmp_path / "other_decisions").mkdir()
    (tmp_path / "other_decisions" / "A0000001.txt").write_text("timeout reviewed\n", encoding="utf-8")
    ep.gate(other, "A0000002", 0.0, tmp_path, decisions=tmp_path / "other_decisions")
    fixture = tmp_path / "fixture"
    attempt(fixture, 1, rc=7, cmd="--phase run --mode cost_fixture --partition x --fixture-interrupt")
    attempt(fixture, 2)
    assert ep.ledger(fixture, "A0000002")["attempts"][0]["intended_interrupt"]
    ep.gate(fixture, "A0000002", 0.0, tmp_path)
    fake = tmp_path / "fake"
    attempt(fake, 1, rc=7, cmd="--phase run --mode full --partition x")
    attempt(fake, 2)
    with pytest.raises(ep.GateStop):
        ep.gate(fake, "A0000002", 0.0, tmp_path)
    big = tmp_path / "big"
    attempt(big, 1, rc=0, rss=8 * 2 ** 20 + 1)
    attempt(big, 2)
    with pytest.raises(ep.GateStop):
        ep.gate(big, "A0000002", 0.0, tmp_path)


def test_enospc_never_completes(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "cost_fixture")
    ep.write_plan(c, "cost_fixture", root, identity, 7)
    real_save, real_replace = pipelines.save_fair_csv, os.replace

    def no_space(*a, **k):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(pipelines, "save_fair_csv", no_space)
    with pytest.raises(OSError):
        ep.run_phase(c, "cost_fixture", root, identity, "scalar_cal")
    monkeypatch.setattr(pipelines, "save_fair_csv", real_save)
    monkeypatch.setattr(os, "replace", no_space)
    with pytest.raises(OSError):
        ep.run_phase(c, "cost_fixture", root, identity, "scalar_cal")
    monkeypatch.setattr(os, "replace", real_replace)
    assert not (root / "partitions" / "scalar_cal").exists()
    ep.run_phase(c, "cost_fixture", root, identity, "scalar_cal")
    ep.run_phase(c, "cost_fixture", root, identity, "fit_gaussian_N4")
    monkeypatch.setattr(ep, "DISK_RESERVE_BYTES", 2 ** 62)
    with pytest.raises(OSError):
        ep.run_phase(c, "cost_fixture", root, identity, "calmax_gaussian_N4_r0000-0007")
    assert not (root / "partitions" / "calmax_gaussian_N4_r0000-0007").exists()
    host = Host(tmp_path, monkeypatch)
    base = ["--mode", "cost_fixture", "--root", tmp_path / "w", "--config", write_cfg(tmp_path)]
    monkeypatch.setattr(ep, "DISK_RESERVE_BYTES", 2 ** 20)
    assert host(["--phase", "plan", "--block", 7] + base) == 0
    monkeypatch.setattr(pipelines, "save_fair_csv", no_space)
    assert host(["--phase", "next"] + base) == 4
    assert not (tmp_path / "w" / "partitions" / "scalar_cal").exists()


def test_fixture_interrupt_leaves_tmp_and_recomputes(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = ep.production_identity(c, "cost_fixture")
    ep.write_plan(c, "cost_fixture", root, identity, 7)
    for pid in ep.plan_partitions(c, "cost_fixture", 7):
        if pid.startswith("trials_"):
            break
        ep.run_phase(c, "cost_fixture", root, identity, pid)
    pid = "trials_t7_N6_alternative_r0014-0020"
    with pytest.raises(ep.FixtureInterrupt):
        ep.run_phase(c, "cost_fixture", root, identity, pid, interrupt=True)
    part = root / "partitions"
    leftovers = sorted(part.glob(f"{pid}.tmp-*"))
    assert not (part / pid).exists() and len(leftovers) == 1
    assert {p.name for p in leftovers[0].iterdir()} == {"trials.csv.gz", "diagnostics.csv.gz", "axes.csv.gz"}
    snapshot = tree(leftovers[0])
    assert ep.run_phase(c, "cost_fixture", root, identity, pid) == "COMPLETE"
    assert tree(leftovers[0]) == snapshot
    with pytest.raises(ValueError):
        ep.run_phase(c, "full", root, identity, pid, interrupt=True)
    host = Host(tmp_path, monkeypatch)
    base = ["--mode", "cost_fixture", "--root", tmp_path / "w", "--config", write_cfg(tmp_path)]
    assert host(["--phase", "plan", "--block", 7] + base) == 0
    assert host(["--phase", "run", "--partition", "scalar_cal", "--fixture-interrupt"] + base) == 7
    assert host(["--phase", "next"] + base) == 0
    led = ep.ledger(host.attempts)
    assert [a["intended_interrupt"] for a in led["attempts"]] == [False, True, False]


def test_cost_fixture_runs_every_phase_with_full_counts(tmp_path, monkeypatch):
    c = cfg()
    seen = []
    real = e4.analyse

    def spy(trials, c_, space="science", reading="predictive_rank", n=None):
        seen.append((space, n))
        return real(trials, c_, space, reading, n)

    monkeypatch.setattr(e4, "analyse", spy)
    monkeypatch.setattr(e4, "role_path", lambda *a, **k: (_ for _ in ()).throw(AssertionError("fixture drew a path")))
    root = tmp_path / "r"
    identity = run_all(root, c, mode="cost_fixture", block=7)
    assert identity["mode"] == "cost_fixture" and identity["space"] == "pilot"
    part = root / "partitions"
    manifest = json.loads((part / "merge" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["label"] == "COST_FIXTURE"
    assert manifest["tables"]["trials"]["rows"] == 4 * 6 * 2 * (c["n_hold"] + c["n_alt"])
    assert manifest["tables"]["diagnostics_axes"]["rows"] == 2 * (4 + 6) * c["n_alt"]
    assert manifest["tables"]["calibration_maxima"]["rows"] == 4 * 3 * c["n_cal"]
    assert seen == [("pilot", {"alternative": c["n_alt"], "holdout": c["n_hold"]})] * 2
    scalar = ep.load_partition(root, "scalar_cal", identity)["objects"]["scalar"]
    assert scalar == ep._plain(e4.cell_calibration(ep.fixture_values(c["n_cal"], "scalar_cal"), c["alpha"]))
    block = ep.read_table(part / "calmax_gaussian_N4_r0007-0014" / "maxima.csv.gz")
    got = block[block["method"] == "SPEC-full"]["max_log"].to_numpy()
    assert np.array_equal(got, ep.fixture_values(c["n_cal"], "calmax|gaussian|4|SPEC-full")[7:14])


def test_cost_kernels_stay_outside_science(tmp_path, monkeypatch):
    host = Host(tmp_path, monkeypatch)
    spaces, cals = [], []
    real_path, real_cal = e4.role_path, e4.cell_calibration
    monkeypatch.setattr(e4, "role_path", lambda c_, space, *a, **k: spaces.append(space) or real_path(c_, space, *a, **k))
    monkeypatch.setattr(e4, "cell_calibration", lambda m, a: cals.append(len(m)) or real_cal(m, a))
    root = tmp_path / "p1"
    base = ["--mode", "production_pilot", "--root", root, "--config", write_cfg(tmp_path), "--replicates", 3]
    for role in ("calibration", "alternative"):
        assert host(["--phase", "cost-kernels", "--cell", "gaussian_N4", "--role", role] + base) == 0
    assert set(spaces) == {"pilot"} and cals == [3, 3, 3]
    assert sorted(p.name for p in (root / "partitions").iterdir()) == ["cost_gaussian_N4_alternative",
                                                                      "cost_gaussian_N4_calibration"]
    for p in (root / "partitions").iterdir():
        assert sorted(q.name for q in p.iterdir()) == ["cost.csv", "partition.json"]
        cost = pd.read_csv(p / "cost.csv")
        assert list(cost.columns) == e4.COST_COLUMNS
        assert all(re.fullmatch(ep.COST_STAGE_RE, s) for s in cost["stage"]), cost["stage"].tolist()
        assert set(cost["status"]) == {"COMPLETE"}
    assert host(["--phase", "cost-kernels", "--cell", "gaussian_N4", "--role", "holdout", "--mode", "full",
                 "--root", tmp_path / "x", "--config", write_cfg(tmp_path), "--replicates", 3]) in (3, 5)
    host.decide()
    assert host(["--phase", "next"] + base[:-2]) == 5
    assert not (tmp_path / "x").exists()


def published_files(target):
    return set(json.loads((target / "PUBLISHED.json").read_text(encoding="utf-8"))["files"])


def reinventory(target, rel):
    pub = json.loads((target / "PUBLISHED.json").read_text(encoding="utf-8"))
    p = target / rel
    pub["files"][rel] = {"sha256": pdb.file_sha256(p), "bytes": p.stat().st_size}
    (target / "PUBLISHED.json").write_text(pdb.canon(pub), encoding="utf-8")


def test_publication_is_closed_verified_and_atomic(tmp_path, monkeypatch):
    c = cfg()
    root = tmp_path / "r"
    identity = run_all(root, c, mode="cost_fixture", block=7)
    att = tmp_path / "attempts"
    attempt(att, 1, rc=0)
    target = tmp_path / "pub" / "fixture"
    assert ep.publish(c, "cost_fixture", root, identity, target, att) == "PUBLISHED"
    files = published_files(target)
    fixed = {"session.json", "campaign_plan.json", "manifest.json", "lineage.json", "ledger/attempts.jsonl",
             "ledger/cpu_ledger.csv", "records/scalar_cal/scalar_calibration.csv", "records/thresholds/calibration.csv",
             "records/thresholds/cells.csv"} | {f"records/fit_{bg}_N{N}/cell.csv" for bg, N in ep.cells_of(c)}
    assert fixed <= files
    rest = files - fixed
    assert all(f.split("/")[0] in ("calibration_maxima", "trials", "diagnostics", "diagnostics_axes", "analysis")
               for f in rest)
    assert len([f for f in rest if f.startswith("analysis/")]) == 7
    assert not list(root.glob("publish.tmp-*"))
    summary = ep.verify_publication(target)
    lineage = json.loads((target / "lineage.json").read_text(encoding="utf-8"))
    assert summary["blocks"] == len(lineage["blocks"]) > 0
    assert "merge" not in lineage["partitions"] and "analysis" not in lineage["partitions"]
    led = [json.loads(x) for x in (target / "ledger" / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [a["attempt_id"] for a in led] == ["A0000001"]
    assert ep.publish(c, "cost_fixture", root, identity, target, att) == "SKIPPED_COMPLETE"

    (target / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(target)
    (target / "extra.txt").unlink()
    frag = target / "trials" / "gaussian_N4.csv.gz"
    original = frag.read_bytes()
    rows = gzip.decompress(original).splitlines(keepends=True)
    frag.write_bytes(gzip.compress(b"".join(rows[:-1])))
    reinventory(target, "trials/gaussian_N4.csv.gz")
    with pytest.raises((pdb.PartitionMismatch, ep.IncompleteWork)):
        ep.verify_publication(target)
    frag.write_bytes(original)
    reinventory(target, "trials/gaussian_N4.csv.gz")
    ep.verify_publication(target)
    scalar = target / "records" / "scalar_cal" / "scalar_calibration.csv"
    text = scalar.read_bytes()
    scalar.write_bytes(text.replace(b",OK,", b",OK ,") if b",OK," in text else text.replace(b"OK", b"OX", 1))
    reinventory(target, "records/scalar_cal/scalar_calibration.csv")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(target)
    scalar.write_bytes(text)
    reinventory(target, "records/scalar_cal/scalar_calibration.csv")

    second = tmp_path / "pub" / "second"
    real = ep.verify_publication
    monkeypatch.setattr(ep, "verify_publication", lambda t: (_ for _ in ()).throw(OSError(28, "No space left")))
    with pytest.raises(OSError):
        ep.publish(c, "cost_fixture", root, identity, second, att)
    assert not second.exists() and len(list(root.glob("publish.tmp-*"))) == 1
    monkeypatch.setattr(ep, "verify_publication", real)
    assert ep.publish(c, "cost_fixture", root, identity, second, att) == "PUBLISHED"
    other = tmp_path / "pub" / "other"
    other.mkdir()
    (other / "PUBLISHED.json").write_text("{}", encoding="utf-8")
    with pytest.raises(pdb.PartitionMismatch):
        ep.publish(c, "cost_fixture", root, identity, other, att)


def test_mixed_publication_is_auditable_without_the_work_root(tmp_path, monkeypatch):
    real = e4.fit_cell

    def fit(c_, background, N, space):
        if (background, N) == ("t7", 6):
            raise e4.EigenTieUnresolved("forced tie", [[0, 1]], [0.0])
        return real(c_, background, N, space)

    monkeypatch.setattr(e4, "fit_cell", fit)
    c = cfg()
    root = tmp_path / "r"
    identity = run_all(root, c, block=7)
    att = tmp_path / "attempts"
    attempt(att, 1, rc=0)
    target = tmp_path / "pub"
    ep.publish(c, "full", root, identity, target, att)
    shutil.rmtree(root)
    calls = []
    real_scalar = e4.scalar_calibration
    monkeypatch.setattr(e4, "scalar_calibration", lambda c_, space: calls.append(space) or real_scalar(c_, space))
    summary = ep.verify_publication(target)
    assert calls == ["science"] and summary["calibrations_recomputed"] == 3 * 3
    assert "calibration_maxima/t7_N6.csv.gz" not in published_files(target)
    assert "records/fit_t7_N6/cell.csv" in published_files(target)
    cal = target / "records" / "thresholds" / "calibration.csv"
    text = cal.read_bytes()
    lines = text.splitlines(keepends=True)
    k = next(i for i, x in enumerate(lines) if b",SPEC-full," in x and b",OK," in x)
    lines[k] = lines[k].replace(b",OK,", b",CALIBRATION_FAILED,")
    cal.write_bytes(b"".join(lines))
    reinventory(target, "records/thresholds/calibration.csv")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(target)


def test_identity_stamp(record_testsuite_property):
    full = e4.validate_config(e4.load_config(e4.CONFIG))
    identity = ep.production_identity(full, "full", e4.CONFIG)
    assert identity["config_file_sha256"] == ep.REFERENCE_CONFIG_SHA256
    record_testsuite_property("e4_session_id", identity["session_id"])


def junit(path, sid, required, proto=2, fail=(), skip=()):
    cases = []
    for name in required:
        inner = '<failure message="x"/>' if name in fail else '<skipped message="x"/>' if name in skip else ""
        cases.append(f'<testcase classname="tests.test_e4_production" name="{name}" time="0.1">{inner}</testcase>')
    cases += [f'<testcase classname="tests.test_e4_alignment" name="test_p{i}" time="0.1"></testcase>'
              for i in range(proto)]
    path.write_text('<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" '
                    f'failures="{len(fail)}" skipped="{len(skip)}" tests="{len(cases)}"><properties>'
                    f'<property name="e4_session_id" value="{sid}"/></properties>{"".join(cases)}</testsuite>'
                    '</testsuites>', encoding="utf-8")
    return path


def test_tests_receipt_requires_stamp_coverage_and_success(tmp_path, monkeypatch):
    monkeypatch.setattr(ep, "REQUIRED_TESTS", ("test_a", "test_b"))
    monkeypatch.setattr(ep, "PROTOTYPE_TESTS", 2)
    identity = {"session_id": "s" * 64}
    log = tmp_path / "pytest.log"
    log.write_text("2 passed\n", encoding="utf-8")
    ok = junit(tmp_path / "ok.xml", "s" * 64, ("test_a", "test_b", "test_extra"))
    receipt = ep.receipt_tests(identity, ok, log, "pytest -q", 0)
    assert receipt["kind"] == "tests" and receipt["session_id"] == "s" * 64
    assert receipt["leaves"]["junit"]["sha256"] == pdb.file_sha256(ok)
    ep.validate_receipt("tests", receipt, identity)
    bad = {"stale": junit(tmp_path / "a.xml", "t" * 64, ("test_a", "test_b")),
           "missing": junit(tmp_path / "b.xml", "s" * 64, ("test_a",)),
           "skipped": junit(tmp_path / "c.xml", "s" * 64, ("test_a", "test_b"), skip=("test_b",)),
           "red": junit(tmp_path / "d.xml", "s" * 64, ("test_a", "test_b"), fail=("test_a",)),
           "prototype": junit(tmp_path / "e.xml", "s" * 64, ("test_a", "test_b"), proto=1)}
    for name, path in bad.items():
        with pytest.raises(ep.ActivationRefused):
            ep.receipt_tests(identity, path, log, "pytest -q", 0)
    with pytest.raises(ep.ActivationRefused):
        ep.receipt_tests(identity, ok, log, "pytest -q", 1)
    ok.write_text(ok.read_text(encoding="utf-8").replace("test_extra", "test_extra2"), encoding="utf-8")
    with pytest.raises(ep.ActivationRefused):
        ep.validate_receipt("tests", receipt, identity)


D4_SKIPS = ("SKIPPED [2] tests/test_chars.py:69: D4 is not built in this tree",
            "SKIPPED [1] tests/test_data_eurofidai.py:25: D4 not built; EUROFIDAI data must be exported first "
            "(see docs/sections/eurofidai_extraction_spec.md)")
SUMMARY_BAR = "=========================== short test summary info ============================"


def make_check_log(path, first="37 passed in 36.42s", second="1257 passed, 3 skipped in 497.23s (0:08:17)",
                   skips=D4_SKIPS, first_skips=(), suites=2):
    """make check output as the Makefile prints it: pyflakes, two echoed pytest -q suites, -rs skip lines."""
    lines = ["pyflakes jepadrift/floors.py experiments/e4_production.py", ep.MAKE_CHECK_SUITES[0], "." * 37 + " [100%]"]
    lines += [SUMMARY_BAR, *first_skips] if first_skips else []
    lines += [first]
    if suites == 2:
        lines += [ep.MAKE_CHECK_SUITES[1], "....s..s. [100%]"] + ([SUMMARY_BAR, *skips] if skips else []) + [second]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_make_check_receipt_reads_pytest_summaries(tmp_path):
    identity = {"session_id": "s" * 64}
    log = make_check_log(tmp_path / "make.log")
    receipt = ep.receipt_make_check(identity, log, "make check", 0)
    suites = receipt["facts"]["suites"]
    assert [s["command"] for s in suites] == list(ep.MAKE_CHECK_SUITES)
    assert suites[0]["counts"] == {"passed": 37} and suites[1]["counts"] == {"passed": 1257, "skipped": 3}
    assert suites[0]["skips"] == [] and [n for n, _ in suites[1]["skips"]] == [2, 1]
    ep.validate_receipt("make_check", receipt, identity)
    ep.receipt_make_check(identity, make_check_log(tmp_path / "bars.log", first="===== 37 passed in 36.42s ====="),
                          "make check", 0)
    torch = ("SKIPPED [1] tests/test_contracts.py:401: torch not installed; JEPA guards skipped",)
    pca = D4_SKIPS + ("SKIPPED [1] tests/test_pca_drift_contracts.py:1469: BLOCKED_DATA_UNAVAILABLE: "
                      "PCA_FULL2000_TRIALS unset or path absent",)
    bad = {"one_suite": {"suites": 1}, "torch_guard_skipped": {"first": "36 passed, 1 skipped in 30.0s",
                                                              "first_skips": torch},
           "pca_g1_skipped": {"second": "1256 passed, 4 skipped in 497.0s", "skips": pca},
           "unlisted_skips": {"second": "1257 passed, 4 skipped in 497.0s"},
           "no_skip_lines": {"skips": ()}, "failed": {"second": "1 failed, 1256 passed, 3 skipped in 497.0s"},
           "error": {"first": "37 passed, 1 error in 36.4s"}, "deselected": {"first": "37 passed, 2 deselected in 3.0s"},
           "no_test": {"first": "no tests ran in 0.01s"}}
    for name, kw in bad.items():
        with pytest.raises(ep.ActivationRefused):
            ep.receipt_make_check(identity, make_check_log(tmp_path / f"{name}.log", **kw), "make check", 0)
    with pytest.raises(ep.ActivationRefused):
        ep.receipt_make_check(identity, log, "make check", 2)
    make_check_log(log, second="1257 passed, 3 skipped in 400.00s (0:06:40)")
    with pytest.raises(ep.ActivationRefused):
        ep.validate_receipt("make_check", receipt, identity)


def test_make_check_partial_log_is_refused(tmp_path):
    path = tmp_path / "partial.log"
    path.write_text("== 2 passed in 1.0s ==\n", encoding="utf-8")
    problems, _ = ep._make_check_problems(path, 0)
    assert problems, "A single partial pytest suite cannot attest make check."


def test_required_tests_list_every_test_of_the_module():
    assert set(ep.REQUIRED_TESTS) == {n for n in globals() if n.startswith("test_")}
    assert len(ep.REQUIRED_TESTS) == len(set(ep.REQUIRED_TESTS))


def prior_costs(path, c):
    rows = [{"partition": "scalar_cal", "stage": "scalar_cal", "n_paths": 4, "n_runs": 1, "cpu_s": 0.2, "wall_s": 0.2,
             "peak_rss_kib": 1000, "status": "COMPLETE"}]
    for bg, N in ep.cells_of(c):
        rows.append({"partition": f"{bg}:{N}", "stage": "fit_cell", "n_paths": 1, "n_runs": 1, "cpu_s": 0.5,
                     "wall_s": 0.5, "peak_rss_kib": 1000, "status": "COMPLETE"})
        for role in ep.COST_ROLES:
            rows.append({"partition": f"{bg}:{N}", "stage": f"draw:{role}", "n_paths": 4, "n_runs": 4, "cpu_s": 0.4,
                         "wall_s": 0.4, "peak_rss_kib": 1000, "status": "COMPLETE"})
            rows.append({"partition": f"{bg}:{N}", "stage": f"logpath:SPEC-full:{role}", "n_paths": 4, "n_runs": 4,
                         "cpu_s": 0.8, "wall_s": 0.8, "peak_rss_kib": 1000, "status": "COMPLETE"})
    pipelines.save_fair_csv(pd.DataFrame(rows, columns=e4.COST_COLUMNS), path)
    return path


CONTROL_BOUND_S = 5.0


def mini_pilot(tmp_path, monkeypatch):
    monkeypatch.setattr(ep, "P1_CELLS", (("gaussian", 4),))
    host = Host(tmp_path, monkeypatch)
    path = write_cfg(tmp_path)
    c = e4.validate_config(e4.load_config(path))
    p1, p2, pub, report = tmp_path / "p1", tmp_path / "p2", tmp_path / "p2pub", tmp_path / "report"
    for role in ep.COST_ROLES:
        assert host(["--phase", "cost-kernels", "--mode", "production_pilot", "--cell", "gaussian_N4", "--role", role,
                     "--replicates", 3, "--root", p1, "--config", path]) == 0
    base = ["--mode", "cost_fixture", "--root", p2, "--config", path]
    assert host(["--phase", "plan", "--block", 7] + base) == 0
    assert host(["--phase", "run", "--partition", "scalar_cal", "--fixture-interrupt"] + base) == 7
    rc = 0
    while rc == 0:
        rc = host(["--phase", "next"] + base)
    assert rc == 10
    for pid in ("fit_gaussian_N4", "calmax_gaussian_N4_r0000-0007", "trials_t7_N6_alternative_r0014-0020"):
        assert host(["--phase", "run", "--partition", pid] + base) == 0
    assert host(["--phase", "verify"] + base) == 0
    assert host(["--phase", "publish", "--to", pub] + base) == 0
    assert host(["--phase", "verify-publication", "--to", pub] + base) == 0
    assert host(["--phase", "forecast", "--mode", "full", "--config", path, "--block", 7, "--p1-root", p1,
                 "--p2-root", p2, "--publication", pub, "--prior-costs", prior_costs(tmp_path / "prior.csv", c),
                 "--control-bound-s", CONTROL_BOUND_S, "--out", report]) == 0
    receipts = tmp_path / "receipts"
    common = ["--mode", "full", "--config", path, "--p1-root", p1, "--p2-root", p2, "--report", report,
              "--publication", pub]
    assert host(["--phase", "receipt", "--kind", "pilot", "--out", receipts / "pilot.json"] + common) == 0
    assert host(["--phase", "receipt", "--kind", "nonleak", "--out", receipts / "nonleak.json"] + common) == 0
    return host, c, path, p1, p2, pub, report, receipts


def test_forecast_and_pilot_receipt_from_a_measured_pilot(tmp_path, monkeypatch):
    host, c, path, p1, p2, pub, report, receipts = mini_pilot(tmp_path, monkeypatch)
    forecast = pd.read_csv(report / "forecast.csv", float_precision="round_trip")
    numbers = forecast.select_dtypes("number")
    assert np.isfinite(numbers.to_numpy()).all() and (numbers.to_numpy() >= 0).all()
    row = forecast[forecast["scenario"] == "FULL_GRID"].iloc[0]
    assert row["status"] == "WITHIN_CAP" and row["block"] == 7
    assert row["total_cpu_s"] == pytest.approx(row["consumed_cpu_s"] + row["projected_cpu_s"] + row["reserve_cpu_s"])
    frozen = json.loads((report / "MANIFEST.json").read_text(encoding="utf-8"))["ledger"]
    assert frozen["cutoff"] == row["cutoff"] and frozen["consumed_cpu_s"] == pytest.approx(row["consumed_cpu_s"])
    assert row["consumed_cpu_s"] == pytest.approx(ep.consumed_through(host.attempts, row["cutoff"], frozen["imports"]))
    per = pd.read_csv(report / "partition_forecast.csv", float_precision="round_trip")
    assert set(ep.plan_partitions(c, "full", 7)) <= set(per["partition"])
    assert (per["cpu_s"] > 0).all() and (per["projected_bytes"] >= 0).all()
    assert set(forecast["scenario"]) == {"FULL_GRID", "DROP_N500", "T7_ON_8_64_239"}
    manifest = json.loads((report / "MANIFEST.json").read_text(encoding="utf-8"))
    assert {p.name for p in report.iterdir()} == set(ep.REPORT_FILES) | {"MANIFEST.json"}
    assert manifest["label"] == "COST_ONLY_NOT_SCIENTIFIC_E4" and set(manifest["files"]) == set(ep.REPORT_FILES)
    assert all(pdb.file_sha256(report / n) == f["sha256"] for n, f in manifest["files"].items())
    assert ep._report_problems(report) == []
    lines = [json.loads(x) for x in (report / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [a["attempt_id"] for a in lines] == sorted(p.name for p in host.attempts.iterdir() if p.name <= row["cutoff"])
    assert all(set(a) == set(ep.ATTEMPT_KEYS) and a["state"] == "MEASURED" for a in lines)
    sources = ep.read_table(report / "cost_sources.csv")
    assert math.isclose(math.fsum(sources["cpu_s"]), row["consumed_cpu_s"], abs_tol=1e-6)
    assert set(sources["category"]) == {"prior_pilot", "producer"}
    stages = ep.read_table(report / "stage_costs.csv")
    assert list(stages.columns) == e4.COST_COLUMNS
    assert set(stages["partition"]) == {f"cost_gaussian_N4_{r}" for r in ep.COST_ROLES}
    volumes = ep.read_table(report / "volumes.csv")
    assert list(volumes.columns) == ep.VOLUME_COLUMNS and set(volumes["kind"]) == {"partition", "leftover", "publication"}
    assert set(volumes["final_label"]) == {"MEASURED_FINAL_BYTES"} and set(volumes["tmp_peak_status"]) == {"NOT_OBSERVED"}
    parts = volumes[volumes["kind"] == "partition"].set_index("item")
    assert set(parts.index) == set(ep.plan_partitions(c, "cost_fixture", 7)) and (parts["final_bytes"] > 0).all()
    assert (parts["tmp_bound_bytes"] >= parts["final_bytes"]).all()
    block = "trials_gaussian_N4_alternative_r0000-0007"
    assert parts.loc[block, "tmp_bound_basis"] == "DERIVED_FINAL_PLUS_LARGEST_PLAIN_CSV"
    assert parts.loc["merge", "tmp_bound_basis"] == "DERIVED_FINAL_PLUS_LARGEST_MERGED_PLAIN_CSV"
    assert parts.loc["scalar_cal", "tmp_bound_basis"] == "DERIVED_DIRECT_WRITE"
    assert all(parts.loc[p, "tmp_bound_bytes"] > parts.loc[p, "final_bytes"] for p in (block, "merge"))
    per_tmp = per.set_index("partition")
    assert per_tmp.loc["merge", "projected_tmp_bytes"] > 0
    assert per_tmp.loc["merge", "projected_tmp_basis"] == "DERIVED_LARGEST_MERGED_PLAIN_CSV"
    pilot = json.loads((receipts / "pilot.json").read_text(encoding="utf-8"))
    identity = ep.production_identity(c, "full", path)
    assert pilot["session_id"] == identity["session_id"]
    assert pilot["p2"]["block"] == 7 and pilot["p2"]["partitions"] == len(ep.plan_partitions(c, "cost_fixture", 7))
    for change in ({"block": 20, "partitions": len(ep.plan_partitions(c, "cost_fixture", 20))},
                   {"partitions": pilot["p2"]["partitions"] + 1}, {"publication": "not-a-sha256"}):
        with pytest.raises(ep.ActivationRefused):
            ep.validate_receipt("pilot", {**pilot, "p2": {**pilot["p2"], **change}}, identity, host.attempts)
    assert ep._receipt_fact_problems("pilot", {**pilot, "p2": {k: v for k, v in pilot["p2"].items() if k != "block"}},
                                     identity)
    assert pilot["interruption"]["partition"] == "scalar_cal" and len(pilot["replays"]) == 3
    assert sorted(pilot["p1"]["partitions"]) == [f"cost_gaussian_N4_{r}" for r in sorted(ep.COST_ROLES)]
    ep.validate_receipt("pilot", pilot, identity, host.attempts)
    ep.validate_receipt("nonleak", json.loads((receipts / "nonleak.json").read_text(encoding="utf-8")), identity,
                        host.attempts)
    other = tmp_path / "stale"
    shutil.copytree(p1, other)
    (other / "session.json").write_text(json.dumps({"session_id": "x"}), encoding="utf-8")
    with pytest.raises(ep.ActivationRefused):
        ep.receipt_pilot(c, identity, other, p2, report, pub, host.attempts)
    volumes_text = (report / "volumes.csv").read_text(encoding="utf-8")
    (report / "volumes.csv").write_text(volumes_text + "extra,partition,1,1,MEASURED_COST_FIXTURE\n", encoding="utf-8")
    assert ep._report_problems(report)
    (report / "volumes.csv").write_text(volumes_text, encoding="utf-8")
    (report / "extra.csv").write_text("a\n1\n", encoding="utf-8")
    with pytest.raises(ep.ActivationRefused):
        ep.receipt_nonleak(identity, p1, report, p2)


def activated(tmp_path, monkeypatch):
    """Measured mini pilot, the four receipts, a technical evidence-cost candidate, then the explicit activation."""
    host, c, path, p1, p2, pub, report, receipts = mini_pilot(tmp_path, monkeypatch)
    monkeypatch.setattr(ep, "REQUIRED_TESTS", ("test_a",))
    monkeypatch.setattr(ep, "PROTOTYPE_TESTS", 1)
    monkeypatch.setattr(ep, "REFERENCE_CONFIG_SHA256", pdb.file_sha256(path))
    identity = ep.production_identity(c, "full", path)
    log = tmp_path / "pytest.log"
    log.write_text("2 passed in 1.0s\n", encoding="utf-8")
    junit(tmp_path / "junit.xml", identity["session_id"], ("test_a",), proto=1)
    full = ["--mode", "full", "--config", path]
    assert host(["--phase", "receipt", "--kind", "tests", "--junit", tmp_path / "junit.xml", "--log", log,
                 "--command", "pytest -q", "--exit-code", 0, "--out", receipts / "tests.json"] + full) == 0
    assert host(["--phase", "receipt", "--kind", "make_check", "--log", make_check_log(tmp_path / "make.log"),
                 "--command", "make check", "--exit-code", 0, "--out", receipts / "make_check.json"] + full) == 0
    go = tmp_path / "GO-technical.md"
    go.write_text("technical GO\n", encoding="utf-8")
    evidence, act = tmp_path / "evidence", tmp_path / "activation.json"
    assert host(["--phase", "evidence-cost", "--receipts", receipts, "--report", report, "--technical-go", go,
                 "--volume", 200, "--out", evidence] + full) == 0
    assert not act.exists() and not (tmp_path / "w").exists()
    assert host(["--phase", "activate", "--receipts", receipts, "--report", report, "--technical-go", go,
                 "--evidence-cost", evidence, "--out", act, "--root", tmp_path / "w"] + full) == 0
    return host, c, path, identity, act, receipts, report, evidence


def test_activation_requires_bound_receipts(tmp_path, monkeypatch, capsys):
    host, c, path, identity, act, receipts, report, evidence = activated(tmp_path, monkeypatch)
    table = ep.read_table(evidence / "evidence_cost.csv")
    assert list(table["stage"]) == list(ep.EVIDENCE_STAGES) and set(table["status"]) == {"PASSED"}
    assert int(table["n_attempts"].max()) == 200
    ep.check_activation(act, identity, host.attempts)
    w = tmp_path / "w"
    capsys.readouterr()
    assert host(["--phase", "plan", "--block", 7, "--mode", "full", "--root", w, "--config", path,
                 "--activation", act]) == 0
    assert capsys.readouterr().out == "44\n"
    assert host(["--phase", "next", "--mode", "full", "--root", w, "--config", path, "--activation", act]) == 0
    assert (w / "partitions" / "scalar_cal").is_dir()
    record = json.loads(act.read_text(encoding="utf-8"))
    variants = {"stale": {**record, "session_id": "0" * 64}, "boolean": {"activated": True},
                "missing_receipt": {**record, "receipts": {k: v for k, v in record["receipts"].items() if k != "tests"}},
                "foreign_go": {**record, "go_full": {**record["go_full"], "sha256": "0" * 64}},
                "no_evidence_cost": {**record, "evidence_cost": None}}
    for name, body in variants.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(body), encoding="utf-8")
        with pytest.raises(ep.ActivationRefused):
            ep.check_activation(tmp_path / f"{name}.json", identity, host.attempts)
    forecast = report / "forecast.csv"
    text = forecast.read_bytes()
    forecast.write_bytes(text.replace(b"WITHIN_CAP", b"NaN", 1))
    with pytest.raises(ep.ActivationRefused):
        ep.check_activation(act, identity, host.attempts)
    assert host(["--phase", "next", "--mode", "full", "--root", w, "--config", path, "--activation", act]) == 3
    forecast.write_bytes(text)
    first = host.attempts / "A0000001" / "time.txt"
    original = first.read_text(encoding="utf-8")
    first.write_text("0.00 0.00 0.00 1000 0\n", encoding="utf-8")
    with pytest.raises((ep.ActivationRefused, ep.GateStop)):
        ep.check_activation(act, identity, host.attempts)
    first.write_text(original, encoding="utf-8")
    ep.check_activation(act, identity, host.attempts)
    attempt(host.attempts, host.k + 1, rc=0, user=ep.CPU_CAP_S, system=0.0, cmd="--phase receipt --kind tests")
    with pytest.raises(ep.ActivationRefused):
        ep.activate(c, identity, receipts, report, tmp_path / "GO-technical.md", host.attempts, None, "activate",
                    tmp_path / "activation2.json", tmp_path / "w", evidence)
    assert not (tmp_path / "activation2.json").exists()
    ep.check_activation(act, identity, host.attempts)


def test_accounting_receipt_links_the_publication_and_the_final_ledger(tmp_path, monkeypatch):
    host = Host(tmp_path, monkeypatch)
    path = write_cfg(tmp_path)
    root, pub = tmp_path / "w", tmp_path / "pub"
    base = ["--mode", "cost_fixture", "--root", root, "--config", path]
    assert host(["--phase", "plan", "--block", 20] + base) == 0
    rc = 0
    while rc == 0:
        rc = host(["--phase", "next"] + base)
    assert rc == 10 and host(["--phase", "publish", "--to", pub] + base) == 0
    out = tmp_path / "accounting.json"
    assert host(["--phase", "receipt", "--kind", "accounting", "--mode", "full", "--config", path, "--publication", pub,
                 "--out", out]) == 0
    receipt = json.loads(out.read_text(encoding="utf-8"))
    assert receipt["publication"]["published_sha256"] == pdb.file_sha256(pub / "PUBLISHED.json")
    assert receipt["publication"]["manifest_sha256"] == pdb.file_sha256(pub / "manifest.json")
    publish_attempt = f"A{host.k - 1:07d}"
    assert receipt["ledger"]["cutoff"] == publish_attempt and receipt["queue"]["active_attempt"] == f"A{host.k:07d}"
    published = json.loads((pub / "PUBLISHED.json").read_text(encoding="utf-8"))
    assert published["ledger_snapshot"]["cutoff"] < publish_attempt
    assert receipt["ledger"]["consumed_cpu_s"] > published["ledger_snapshot"]["consumed_cpu_s"]
    assert host(["--phase", "receipt", "--kind", "accounting", "--mode", "full", "--config", path, "--publication", pub,
                 "--out", out]) == 5


def forged(clean, out, rel, change):
    """Copy of a publication with one JSON document changed (None removes it), activation leaf and inventory refreshed."""
    shutil.copytree(clean, out)
    path, act_path = out / rel, out / "activation" / "activation.json"
    if change is None:
        path.unlink()
    else:
        doc = json.loads(path.read_text(encoding="utf-8"))
        change(doc)
        path.write_text(pdb.canon(doc), encoding="utf-8")
    if rel.startswith("activation/receipts/"):
        act = json.loads(act_path.read_text(encoding="utf-8"))
        kind = Path(rel).stem
        if change is None:
            act["receipts"].pop(kind)
        else:
            act["receipts"][kind] = {**act["receipts"][kind], "sha256": pdb.file_sha256(path),
                                     "bytes": path.stat().st_size}
        act_path.write_text(pdb.canon(act), encoding="utf-8")
    pub = json.loads((out / "PUBLISHED.json").read_text(encoding="utf-8"))
    for name in (rel, "activation/activation.json"):
        if (out / name).exists():
            pub["files"][name] = {"sha256": pdb.file_sha256(out / name), "bytes": (out / name).stat().st_size}
        else:
            pub["files"].pop(name, None)
    (out / "PUBLISHED.json").write_text(pdb.canon(pub), encoding="utf-8")
    return out


def test_published_activation_requires_four_normalized_receipts(tmp_path, monkeypatch):
    host, c, path, identity, act, receipts, report, evidence = activated(tmp_path, monkeypatch)
    work, clean = tmp_path / "campaign", tmp_path / "published"
    assert run_all(work, c, block=7, config=path) == identity
    ep.publish(c, "full", work, identity, clean, host.attempts, activation=act)
    shutil.rmtree(work)
    for raw in ("junit.xml", "pytest.log", "make.log"):
        (tmp_path / raw).unlink()
    assert ep.verify_publication(clean, require_activation=True)["activation"]
    assert {f"activation/receipts/{k}.json" for k in ep.RECEIPT_KINDS} <= published_files(clean)

    def facts(**kw):
        return lambda r: r["facts"].update(kw)

    variants = {"absent": ("activation/receipts/nonleak.json", None),
                "foreign_kind": ("activation/receipts/tests.json", lambda r: r.update(kind="pilot")),
                "foreign_session": ("activation/receipts/pilot.json", lambda r: r.update(session_id="0" * 64)),
                "red_tests": ("activation/receipts/tests.json", facts(not_passed=["tests.test_e4_production::test_a"])),
                "stale_stamp": ("activation/receipts/tests.json", facts(stamp="0" * 64)),
                "tests_exit": ("activation/receipts/tests.json", lambda r: r.update(exit_code=1)),
                "torch_skip": ("activation/receipts/make_check.json",
                               lambda r: r["facts"]["suites"][0]["counts"].update(skipped=1)),
                "pilot_coverage": ("activation/receipts/pilot.json", lambda r: r["p1"]["partitions"].popitem()),
                "nonleak_label": ("activation/receipts/nonleak.json", lambda r: r.update(p2_label="E4_SCIENCE")),
                "late_receipt": ("activation/receipts/tests.json", lambda r: r["ledger"].update(cutoff="A9999999")),
                "other_forecast": ("activation/receipts/pilot.json",
                                   lambda r: r["leaves"]["forecast.csv"].update(sha256="0" * 64)),
                "p2_block": ("activation/receipts/pilot.json", lambda r: r["p2"].update(
                    block=20, partitions=len(ep.plan_partitions(c, "cost_fixture", 20)))),
                "p2_count": ("activation/receipts/pilot.json", lambda r: r["p2"].update(partitions=0)),
                "p2_publication": ("activation/receipts/pilot.json", lambda r: r["p2"].update(publication="x" * 64)),
                "activation_session": ("activation/activation.json", lambda a: a.update(session_id="0" * 64))}
    for name, (rel, change) in variants.items():
        with pytest.raises(pdb.PartitionMismatch):
            ep.verify_publication(forged(clean, tmp_path / name, rel, change), require_activation=True)
    bare = tmp_path / "bare"
    other = tmp_path / "fixture"
    fixture_identity = run_all(other, c, mode="cost_fixture", block=7)
    ep.publish(c, "cost_fixture", other, fixture_identity, bare, host.attempts)
    with pytest.raises(ep.IncompleteWork):
        ep.verify_publication(bare, require_activation=True)
    with pytest.raises(pdb.PartitionMismatch):
        ep.publish(c, "cost_fixture", other, fixture_identity, tmp_path / "fixture_act", host.attempts, activation=act)


def test_published_seed_tamper_is_refused(tmp_path):
    c = cfg(grid=[4], backgrounds={"gaussian": None})
    work, target, attempts = tmp_path / "work", tmp_path / "published", tmp_path / "attempts"
    identity = run_all(work, c, mode="cost_fixture", block=20)
    attempt(attempts, 1, rc=0)
    ep.publish(c, "cost_fixture", work, identity, target, attempts)
    path = target / "session.json"
    session = json.loads(path.read_text(encoding="utf-8"))
    session["config"]["seed"] += 1
    path.write_text(pdb.canon(session), encoding="utf-8")
    reinventory(target, "session.json")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(target)


def rebind(target, session):
    """Publication rebound to a recomputed identity: session, PUBLISHED, manifest, plan, lineage and its records."""
    body = {k: v for k, v in session.items() if k != "session_id"}
    sid = hashlib.sha256(pdb.canon(body).encode()).hexdigest()
    for rel in ("session.json", "manifest.json", "campaign_plan.json", "lineage.json"):
        doc = dict(body) if rel == "session.json" else json.loads((target / rel).read_text(encoding="utf-8"))
        doc["session_id"] = sid
        for record in doc["partitions"].values() if rel == "lineage.json" else ():
            record["session_id"] = sid
        (target / rel).write_text(pdb.canon(doc), encoding="utf-8")
        reinventory(target, rel)
    pub = json.loads((target / "PUBLISHED.json").read_text(encoding="utf-8"))
    pub["session_id"] = sid
    (target / "PUBLISHED.json").write_text(pdb.canon(pub), encoding="utf-8")
    return target


def test_publication_identity_is_recomputed_and_reconciled(tmp_path, monkeypatch):
    c = cfg(grid=[4], backgrounds={"gaussian": None})
    identity = run_all(tmp_path / "w", c, mode="cost_fixture", block=7)
    attempt(tmp_path / "att", 1, rc=0)
    clean = tmp_path / "pub"
    ep.publish(c, "cost_fixture", tmp_path / "w", identity, clean, tmp_path / "att")
    session = json.loads((clean / "session.json").read_text(encoding="utf-8"))

    def copy(name):
        shutil.copytree(clean, tmp_path / name)
        return tmp_path / name

    ep.verify_publication(rebind(copy("same"), dict(session)))
    refused = [rebind(copy("space"), {**session, "space": "science"}),
               rebind(copy("domains"), {**session, "domains": session["domains"][:-1]})]
    edits = (("lineage", "lineage.json", lambda d: d.update(session_id="0" * 64)),
             ("record", "lineage.json", lambda d: d["partitions"]["fit_gaussian_N4"].update(session_id="0" * 64)),
             ("producers", "lineage.json", lambda d: d["partitions"].pop("calmax_gaussian_N4_r0007-0014")),
             ("plan_block", "campaign_plan.json", lambda d: d.update(block=10)),
             ("plan_mode", "campaign_plan.json", lambda d: d.update(mode="full")),
             ("manifest_mode", "manifest.json", lambda d: d.update(mode="full")),
             ("label", "PUBLISHED.json", lambda d: d.update(label="E4_SCIENCE")))
    for name, rel, change in edits:
        t = copy(name)
        doc = json.loads((t / rel).read_text(encoding="utf-8"))
        change(doc)
        (t / rel).write_text(pdb.canon(doc), encoding="utf-8")
        if rel != "PUBLISHED.json":
            reinventory(t, rel)
        refused.append(t)
    for t in refused:
        with pytest.raises(pdb.PartitionMismatch):
            ep.verify_publication(t)
    declared_only = copy("declared_only")
    pub = json.loads((declared_only / "PUBLISHED.json").read_text(encoding="utf-8"))
    pub["files"]["activation/activation.json"] = {"sha256": "0" * 64, "bytes": 2}
    (declared_only / "PUBLISHED.json").write_text(pdb.canon(pub), encoding="utf-8")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(declared_only)
    real = pdb.file_sha256
    monkeypatch.setattr(pdb, "file_sha256",
                        lambda p: "0" * 64 if str(p).endswith("experiments/e4_alignment.py") else real(p))
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(clean)
    monkeypatch.setattr(pdb, "file_sha256", real)
    monkeypatch.setattr(e4, "REPO_ROOT", tmp_path / "no_sources")
    with pytest.raises(pdb.PartitionMismatch):
        ep.verify_publication(clean)
    monkeypatch.setattr(e4, "REPO_ROOT", Path(ep.__file__).resolve().parents[1])
    ep.verify_publication(clean)


def test_forecast_partition_sum_is_reconciled(tmp_path, monkeypatch):
    _, c, path, _, _, _, report, _ = mini_pilot(tmp_path, monkeypatch)
    per = ep.read_table(report / "partition_forecast.csv")
    per.loc[0, "cpu_s"] += 100.0
    pipelines.save_fair_csv(per, report / "partition_forecast.csv")
    identity = ep.production_identity(c, "full", path)
    assert ep._forecast_problems(report, identity), "Partition costs differ from the accepted total projection."


def test_forecast_reconciles_partitions_geometry_controls_and_counts(tmp_path, monkeypatch):
    host, c, path, p1, p2, pub, report, receipts = mini_pilot(tmp_path, monkeypatch)
    identity = ep.production_identity(c, "full", path)
    assert ep._forecast_problems(report, identity) == []
    per, forecast = ep.read_table(report / "partition_forecast.csv"), ep.read_table(report / "forecast.csv")
    assert set(per["partition"]) == set(ep.plan_partitions(c, "full", 7)) | set(ep.PHASE_ROWS)
    assert set(forecast["control_bound_s"]) == {CONTROL_BOUND_S} and (per["cpu_s"] >= CONTROL_BOUND_S).all()
    assert {r.partition for r in per.itertuples() if "scalar_production" in r.basis} == {"scalar_cal"}
    assert {r.partition for r in per.itertuples() if "scalar_audit" in r.basis} == {
        "phase:publish", "phase:verify-publication"}
    full = forecast[forecast["scenario"] == "FULL_GRID"].iloc[0]
    assert full["n_partitions"] == len(per) and full["projected_cpu_s"] == pytest.approx(per["cpu_s"].sum())

    def variant(name, table, change):
        out = tmp_path / name
        shutil.copytree(report, out)
        pipelines.save_fair_csv(change(ep.read_table(out / table)), out / table)
        return ep._forecast_problems(out, identity)

    assert variant("duplicate", "partition_forecast.csv", lambda d: pd.concat([d, d.iloc[[3]]], ignore_index=True))
    assert variant("foreign", "partition_forecast.csv", lambda d: d.replace({"partition": {"merge": "merge_extra"}}))
    assert variant("block", "partition_forecast.csv",
                   lambda d: d.assign(partition=d["partition"].str.replace("_r0014-0020", "_r0014-0019")))
    assert variant("count", "forecast.csv", lambda d: d.assign(n_partitions=d["n_partitions"] + 1))
    assert variant("bytes", "forecast.csv", lambda d: d.assign(projected_bytes=d["projected_bytes"] + 1))
    assert variant("cap", "forecast.csv", lambda d: d.assign(cap_cpu_s=2 * ep.CPU_CAP_S))


def test_evidence_cost_problems_bound_the_control_overhead():
    sid = "s" * 64
    ok = pd.DataFrame([{"session_id": sid, "stage": s, "n_attempts": 120, "cpu_s": 0.5, "wall_s": 0.5,
                        "status": "PASSED", "label": ep.EVIDENCE_LABEL} for s in ep.EVIDENCE_STAGES],
                      columns=ep.EVIDENCE_COLUMNS)
    assert ep._evidence_problems(ok, sid, 2.0, 100) == []
    assert ep._evidence_problems(ok, sid, 1.0, 100)
    assert ep._evidence_problems(ok, sid, 2.0, 121)
    assert ep._evidence_problems(ok.assign(status="REFUSED"), sid, 2.0, 100)
    assert ep._evidence_problems(ok.assign(session_id="t" * 64), sid, 2.0, 100)
    assert ep._evidence_problems(ok.iloc[:-1], sid, 2.0, 100)
    assert ep._evidence_problems(ok.assign(cpu_s=float("nan")), sid, 2.0, 100)


def test_imported_costs_keep_provenance(tmp_path, monkeypatch):
    att = tmp_path / "attempts"
    attempt(att, 1, rc=0, user=1.0, system=0.5)
    source = tmp_path / "engineering.csv"
    pipelines.save_fair_csv(pd.DataFrame({"owner": ["worker", "codex"], "source_id": ["W0001", "R0001"],
                                          "cpu_s": [1.48, 53.26]}), source)
    record = ep.import_costs(att, source, "tests")
    assert record["import_id"] == "I0000001" and record["cpu_s"] == pytest.approx(54.74)
    assert record["source"]["sha256"] == pdb.file_sha256(source) and record["source_ids"] == ["R0001", "W0001"]
    led = ep.ledger(att)
    assert led["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 54.74 + 1.5)
    assert [i["import_id"] for i in led["snapshot"]["imports"]] == ["I0000001"]
    overlap, admin, nan = tmp_path / "overlap.csv", tmp_path / "admin.csv", tmp_path / "nan.csv"
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["W0001"], "cpu_s": [1.48]}), overlap)
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["R0004"], "cpu_s": [0.97]}), admin)
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["X"], "cpu_s": [float("nan")]}), nan)
    for path in (source, overlap):
        with pytest.raises(pdb.PartitionMismatch):
            ep.import_costs(att, path, "tests")
    with pytest.raises(ValueError):
        ep.import_costs(att, admin, "producer")
    with pytest.raises(ValueError):
        ep.import_costs(att, nan, "tests")
    snapshot = led["snapshot"]
    assert ep.import_costs(att, admin, "administrative")["import_id"] == "I0000002"
    ep.check_snapshot(att, snapshot)
    assert ep.ledger(att)["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 54.74 + 0.97 + 1.5)
    source.write_text(source.read_text(encoding="utf-8") + "codex,R0009,1.0\n", encoding="utf-8")
    with pytest.raises(ep.GateStop):
        ep.ledger(att)
    with pytest.raises(ep.GateStop):
        ep.check_snapshot(att, snapshot)
    host = Host(tmp_path / "cli", monkeypatch)
    assert host(["--phase", "import-costs", "--mode", "full", "--config", write_cfg(tmp_path), "--source", admin,
                 "--category", "administrative"]) == 0
    assert (tmp_path / "cli" / "imports" / "I0000001.json").is_file()
    assert ep.ledger(host.attempts)["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 0.97 + 0.11)


DRIVER = Path(__file__).resolve().parents[1] / "tools" / "run_e4_production.sh"
STUB = r"""#!/usr/bin/env bash
shift
printf '%s|%s\n' "$E4_ATTEMPT_ID" "$*" >> "$STUB_LOG"
case " $* " in
  *" --phase plan "*) printf '%s\n' "$STUB_K"; exit "${STUB_PLAN_RC:-0}" ;;
  *" --phase next "*)
    n=$(( $(cat "$STUB_STATE" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$STUB_STATE"
    read -r -a codes <<< "$STUB_NEXT"; i=$(( n - 1 ))
    [ "$i" -lt "${#codes[@]}" ] || i=$(( ${#codes[@]} - 1 ))
    exit "${codes[$i]}" ;;
  *" --phase verify "*) exit "${STUB_VERIFY_RC:-0}" ;;
  *" --phase publish "*) exit "${STUB_PUBLISH_RC:-0}" ;;
esac
exit "${STUB_OTHER_RC:-0}"
"""


def drive(tmp_path, *args, **env):
    """Run the real driver from a stub repository whose .venv/bin/python is a scripted, bounded producer."""
    repo = tmp_path / "repo"
    stub = repo / ".venv" / "bin" / "python"
    if not stub.exists():
        stub.parent.mkdir(parents=True)
        stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
        (repo / "experiments").mkdir()
        (repo / "experiments" / "e4_production.py").write_text("", encoding="utf-8")
    calls, state = tmp_path / "calls.log", tmp_path / "state"
    for p in (calls, state):
        p.unlink(missing_ok=True)
    full_env = {"PATH": os.environ["PATH"], "E4_LOCK": str(tmp_path / "driver.lock"), "STUB_LOG": str(calls),
                "STUB_STATE": str(state), "STUB_K": "3", "STUB_NEXT": "0 0 0 10", **{k: str(v) for k, v in env.items()}}
    proc = subprocess.run(["bash", str(DRIVER), *map(str, args)], cwd=repo, env=full_env, capture_output=True,
                          text=True, timeout=120)
    lines = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
    return proc.returncode, [x.split("|", 1) for x in lines]


def test_driver_campaign_with_a_stub_producer(tmp_path):
    campaign = ("campaign", "full", "w", 7, "pub", "act.json")
    rc, calls = drive(tmp_path, *campaign)
    attempts = tmp_path / "repo" / "logs" / "stream_19_e4_production" / "attempts"
    assert rc == 0 and [a.split()[1] for _, a in calls] == ["plan", "next", "next", "next", "next", "verify", "publish"]
    assert "--block 7" in calls[0][1] and all("--activation act.json" in a and "--root w" in a for _, a in calls)
    assert "--to pub" in calls[-1][1]
    ids = [f"A{k:07d}" for k in range(1, 8)]
    assert [i for i, _ in calls] == ids == sorted(p.name for p in attempts.iterdir())
    for i in ids:
        assert {p.name for p in (attempts / i).iterdir()} == {"cmd.txt", "time.txt", "exit.txt"}
        line = (attempts / i / "time.txt").read_text(encoding="utf-8").splitlines()[-1]
        assert re.fullmatch(r"[0-9.]+ [0-9.]+ [0-9.]+ [0-9]+ (0|10)", line)
        assert ep.read_attempt(attempts / i)["state"] == "MEASURED"
    before = {p: p.read_bytes() for p in attempts.rglob("*") if p.is_file()}
    rc, calls = drive(tmp_path, *campaign, STUB_NEXT="10")
    assert rc == 0 and [i for i, _ in calls] == [f"A{k:07d}" for k in range(8, 12)]
    assert all(p.read_bytes() == b for p, b in before.items())
    for k in ("3x", "", "012", "-1", "1234567"):
        rc, calls = drive(tmp_path, *campaign, STUB_K=k)
        assert rc == 5 and [a.split()[1] for _, a in calls] == ["plan"], k
    expected = {"error": ({"STUB_NEXT": "0 5"}, 5, ["plan", "next", "next"]),
                "exhausted": ({"STUB_NEXT": "0"}, 9, ["plan"] + ["next"] * 4),
                "plan_refused": ({"STUB_PLAN_RC": 3}, 3, ["plan"]),
                "verify": ({"STUB_VERIFY_RC": 5}, 5, ["plan"] + ["next"] * 4 + ["verify"]),
                "publish": ({"STUB_PUBLISH_RC": 4}, 4, ["plan"] + ["next"] * 4 + ["verify", "publish"])}
    for name, (env, code, phases) in expected.items():
        rc, calls = drive(tmp_path, *campaign, **env)
        assert rc == code and [a.split()[1] for _, a in calls] == phases, name
    rc, calls = drive(tmp_path, "campaign", "full", "w", "07", "pub")
    assert rc == 2 and calls == []
    rc, calls = drive(tmp_path, "attempt", "--phase", "receipt", "--kind", "tests", STUB_OTHER_RC=6)
    assert rc == 6 and [a for _, a in calls] == ["--phase receipt --kind tests"]


def test_import_record_cpu_must_match_its_hashed_source(tmp_path):
    source = tmp_path / "costs.csv"
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["unit-a", "unit-b"], "cpu_s": [1.0, 2.0]}), source)
    attempts = tmp_path / "attempts"
    ep.import_costs(attempts, source, "tests")
    record = ep.imports_dir(attempts) / "I0000001.json"
    fact = json.loads(record.read_text(encoding="utf-8"))
    fact["cpu_s"] = 0.0
    record.write_text(pdb.canon(fact), encoding="utf-8")
    with pytest.raises(ep.GateStop):
        ep.ledger(attempts)


def test_later_import_preserves_frozen_activation(tmp_path, monkeypatch):
    host, _, _, identity, activation, _, _, _ = activated(tmp_path, monkeypatch)
    before = ep.ledger(host.attempts)["consumed_cpu_s"]
    source = tmp_path / "administrative-tail.csv"
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["tail-unit"], "cpu_s": [3.0]}), source)
    ep.import_costs(host.attempts, source, "administrative")
    assert ep.ledger(host.attempts)["consumed_cpu_s"] == pytest.approx(before + 3.0)
    assert ep.check_activation(activation, identity, host.attempts)["session_id"] == identity["session_id"]


def test_pilot_normalized_p2_count_is_checked(tmp_path, monkeypatch):
    _, _, _, identity, _, receipts, _, _ = activated(tmp_path, monkeypatch)
    receipt = json.loads((receipts / "pilot.json").read_text(encoding="utf-8"))
    assert not ep._receipt_fact_problems("pilot", receipt, identity)
    receipt["p2"]["partitions"] = 0
    assert ep._receipt_fact_problems("pilot", receipt, identity), "An empty P2 cannot attest its complete fixture campaign."


def test_import_facts_and_frozen_membership(tmp_path):
    att, first, second = tmp_path / "attempts", tmp_path / "first.csv", tmp_path / "second.csv"
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["u1", "u2"], "cpu_s": [1.0, 2.0]}), first)
    pipelines.save_fair_csv(pd.DataFrame({"source_id": ["u3"], "cpu_s": [4.0]}), second)
    ep.import_costs(att, first, "tests")
    snapshot = ep.ledger(att)["snapshot"]
    assert snapshot["cutoff"] is None and snapshot["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 3.0)
    ep.import_costs(att, second, "administrative")
    assert ep.ledger(att)["consumed_cpu_s"] == pytest.approx(ep.PRIOR_CPU_S + 7.0)
    assert ep.consumed_through(att, snapshot["cutoff"], snapshot["imports"]) == pytest.approx(ep.PRIOR_CPU_S + 3.0)
    ep.check_snapshot(att, snapshot)
    record = ep.imports_dir(att) / "I0000001.json"
    original = record.read_text(encoding="utf-8")
    for change in ({"rows": 3}, {"source_ids": ["u1", "u9"]}, {"cpu_s": 3.5}):
        record.write_text(pdb.canon({**json.loads(original), **change}), encoding="utf-8")
        for call in (lambda: ep.ledger(att), lambda: ep.check_snapshot(att, snapshot),
                     lambda: ep.consumed_through(att, snapshot["cutoff"], snapshot["imports"])):
            with pytest.raises(ep.GateStop):
                call()
    record.write_text(original, encoding="utf-8")
    ep.check_snapshot(att, snapshot)
    record.unlink()
    for call in (lambda: ep.ledger(att), lambda: ep.consumed_through(att, snapshot["cutoff"], snapshot["imports"])):
        with pytest.raises(ep.GateStop):
            call()
