"""Stream 19 E4 production: replicate blocks, global threshold barrier, FAIR fragments, resume, merge and analysis.

Plan prompts/plans/plan-19-e4-production-20261112.md (GO prompts/GO-stream-19-e4-production-20261112.md). The scientific
kernels are those of experiments/e4_alignment.py, imported unchanged and rerun per block of global replicate indices.
Every scientific phase is refused without an activation record whose evidence is re-verified (full stays disabled).

Usage: python experiments/e4_production.py --phase PHASE --mode full|production_pilot|cost_fixture --root DIR [...]
"""
import argparse
import errno
import gzip
import hashlib
import json
import math
import os
import re
import resource
import shutil
import signal
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import e4_alignment as e4
from experiments import pca_drift_benchmark as pdb
from jepadrift import pipelines

MODES = {"full": "science", "production_pilot": "pilot", "cost_fixture": "pilot"}
TRIAL_ROLES = ("holdout", "alternative")
COST_ROLES = ("calibration", "holdout", "alternative")
SCALAR_FIELDS = e4.CAL_COLUMNS[4:]
FIT_FIELDS = e4.CELL_COLUMNS[2:]
MAX_COLUMNS = ["background", "N", "method", "replicate", "max_log"]
TABLES = {"calibration_maxima": MAX_COLUMNS, "trials": e4.TRIAL_COLUMNS, "diagnostics": e4.DIAG_COLUMNS,
          "diagnostics_axes": e4.AXES_COLUMNS}
GOLDEN = 0.6180339887498949
CPU_CAP_S = 86400.0
PRIOR_CPU_S = 645.23
NEXT_INVOCATION_CPU_S = 1800.0
CPU_RLIMIT_S = (1700, 1750)
CPU_GUARD_MARGIN_S = 30.0
DISK_RESERVE_BYTES = 2 ** 30
FRAGMENT_ALERT_BYTES = 45 * 2 ** 20
GIT_FILE_CAP_BYTES = 50 * 2 ** 20
SINGLE = {"scalar_cal", "thresholds", "merge", "analysis"}
_BG = r"([a-z0-9]+)"
_N = r"N([1-9][0-9]*)"
_R = r"r([0-9]{4})-([0-9]{4})"
PID_FORMS = {"fit": re.compile(rf"fit_{_BG}_{_N}"), "calmax": re.compile(rf"calmax_{_BG}_{_N}_{_R}"),
             "trials": re.compile(rf"trials_{_BG}_{_N}_(holdout|alternative)_{_R}"),
             "cost": re.compile(rf"cost_{_BG}_{_N}_(calibration|holdout|alternative)")}


class IncompleteWork(RuntimeError):
    """A dependency, block, replicate or table group is missing, foreign or duplicated: the work is not complete."""


class FixtureInterrupt(RuntimeError):
    """Deliberate cost_fixture interruption after the payload is written and before the atomic validation."""


def _plain(obj):
    if isinstance(obj, dict):
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj.item() if isinstance(obj, np.generic) else obj


def block_ranges(n, block):
    """Replicate blocks [s, min(s + block, n)) for s in range(0, n, block): exact cover, no empty tail."""
    n, block = e4._integer(n, "n", 1), e4._integer(block, "block", 1)
    return [(s, min(s + block, n)) for s in range(0, n, block)]


def role_counts(cfg):
    """Replicates per role at the configured sizes (scientific and cost_fixture modes alike, never pilot_n)."""
    return {"calibration": cfg["n_cal"], "holdout": cfg["n_hold"], "alternative": cfg["n_alt"]}


def cells_of(cfg):
    """(background, N) cells in canonical order: background name, then N."""
    return [(bg, N) for bg in sorted(cfg["backgrounds"]) for N in sorted(cfg["grid"])]


def pid_fit(bg, N):
    """Partition id of a cell fit."""
    return f"fit_{bg}_N{N}"


def pid_calmax(bg, N, s, t):
    """Partition id of a calibration-maxima block."""
    return f"calmax_{bg}_N{N}_r{s:04d}-{t:04d}"


def pid_trials(bg, N, role, s, t):
    """Partition id of a holdout or alternative trial block."""
    return f"trials_{bg}_N{N}_{role}_r{s:04d}-{t:04d}"


def parse_pid(pid, cfg, mode, block=None):
    """Parsed partition id; ValueError on an unknown form, mode, background, N or a range outside the planned blocks."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    if pid in SINGLE and mode != "production_pilot":
        return {"kind": pid}
    for kind, form in PID_FORMS.items():
        match = form.fullmatch(pid) if isinstance(pid, str) else None
        if match:
            break
    else:
        raise ValueError(f"refused partition id {pid!r}")
    if (kind == "cost") != (mode == "production_pilot"):
        raise ValueError(f"partition {pid!r} is not allowed in mode {mode}")
    groups = match.groups()
    bg, N = groups[0], int(groups[1])
    if bg not in cfg["backgrounds"] or N not in cfg["grid"]:
        raise ValueError(f"partition {pid!r}: background or N outside the configuration")
    out = {"kind": kind, "background": bg, "N": N}
    if kind == "fit":
        return out
    if kind == "cost":
        return {**out, "role": groups[2]}
    role = "calibration" if kind == "calmax" else groups[2]
    s, t = int(groups[-2]), int(groups[-1])
    planned = block_ranges(role_counts(cfg)[role], block) if block is not None else None
    if not 0 <= s < t <= role_counts(cfg)[role] or (planned is not None and (s, t) not in planned):
        raise ValueError(f"partition {pid!r}: range outside the planned blocks")
    return {**out, "role": role, "start": s, "stop": t}


def plan_partitions(cfg, mode, block, fit_status=None):
    """Ordered partitions; calmax only for cells whose fit is known OK (all cells when fit_status is None)."""
    if mode not in ("full", "cost_fixture"):
        raise ValueError(f"mode {mode!r} has no campaign plan")
    n = role_counts(cfg)
    cells = cells_of(cfg)
    ok = [c for c in cells if fit_status is None or fit_status.get(c) == "OK"]
    out = ["scalar_cal"] + [pid_fit(*c) for c in cells]
    out += [pid_calmax(*c, s, t) for c in ok for s, t in block_ranges(n["calibration"], block)]
    out += ["thresholds"]
    out += [pid_trials(*c, role, s, t) for c in cells for role in TRIAL_ROLES for s, t in block_ranges(n[role], block)]
    return out + ["merge", "analysis"]


def production_identity(cfg, mode, config_path=None):
    """Session identity: prototype identity body plus this script, the config file hash and the seed space."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    body = {k: v for k, v in e4.session_identity(cfg, mode).items() if k != "session_id"}
    body["code"] = {**body["code"], "experiments/e4_production.py": pdb.file_sha256(Path(__file__).resolve())}
    body["space"] = MODES[mode]
    body["config_file_sha256"] = None if config_path is None else pdb.file_sha256(config_path)
    return {"session_id": hashlib.sha256(pdb.canon(body).encode()).hexdigest(), **body}


def check_free(path, need=0):
    """OSError ENOSPC when free disk minus the planned bytes falls below the reserve."""
    free = shutil.disk_usage(path).free
    if free - need < DISK_RESERVE_BYTES:
        raise OSError(errno.ENOSPC, f"free disk {free} B minus {need} B is below the {DISK_RESERVE_BYTES} B reserve",
                      str(path))


def _safe_rel(name):
    p = PurePosixPath(name)
    return (bool(name) and not p.is_absolute() and "\\" not in name and all(q not in ("", ".", "..") for q in p.parts)
            and name != "partition.json")


def _inventory(directory):
    directory = Path(directory)
    files, dirs = {}, set()
    for dirpath, dirnames, filenames in os.walk(directory):
        base = Path(dirpath)
        for name in dirnames + filenames:
            if (base / name).is_symlink():
                raise pdb.PartitionMismatch(f"symbolic link {base / name} inside a partition")
        rel = base.relative_to(directory).as_posix()
        if rel != ".":
            dirs.add(rel)
        for name in filenames:
            files[(base / name).relative_to(directory).as_posix()] = base / name
    return files, dirs


def _parents(names):
    return {q.as_posix() for name in names for q in PurePosixPath(name).parents if q.as_posix() != "."}


def verify_partition(final, pid, identity):
    """Record of a COMPLETE partition whose recursive file set, parents and SHA-256 match it; PartitionMismatch else."""
    final = Path(final)
    if final.is_symlink() or not final.is_dir():
        raise pdb.PartitionMismatch(f"partition {pid} is not a plain directory")
    try:
        record = json.loads((final / "partition.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise pdb.PartitionMismatch(f"partition {pid} has no readable record") from exc
    files, dirs = _inventory(final)
    files.pop("partition.json", None)
    declared = record.get("files") if isinstance(record, dict) else None
    if (not isinstance(declared, dict) or record.get("partition") != pid
            or record.get("session_id") != identity["session_id"] or record.get("status") != "COMPLETE"
            or not all(_safe_rel(k) for k in declared) or sorted(files) != sorted(declared)
            or dirs != _parents(declared) or any(pdb.file_sha256(files[k]) != h for k, h in declared.items())):
        raise pdb.PartitionMismatch(f"partition {pid} differs from its record or from the session")
    return record


def load_partition(root, pid, identity):
    """Verified record of a COMPLETE partition; IncompleteWork when it is absent."""
    final = Path(root) / "partitions" / pid
    if not (final.exists() or final.is_symlink()):
        raise IncompleteWork(f"MISSING_PARTITION {pid}")
    return verify_partition(final, pid, identity)


def run_production_partition(root, pid, identity, compute):
    """Atomic nested partition: SKIPPED_COMPLETE when verified, else compute(tmp) -> objects, record, os.replace."""
    root = Path(root)
    parts, session, final = root / "partitions", root / "session.json", root / "partitions" / pid
    if session.exists() and json.loads(session.read_text(encoding="utf-8")) != identity:
        raise pdb.PartitionMismatch(f"{session} holds another session identity")
    leftovers = sorted(p.name for p in parts.glob(f"{pid}.tmp-*")) if parts.is_dir() else []
    if final.exists() or final.is_symlink():
        verify_partition(final, pid, identity)
        return "SKIPPED_COMPLETE", leftovers
    if compute is None:
        raise IncompleteWork(f"MISSING_PARTITION {pid}")
    if not session.exists():
        root.mkdir(parents=True, exist_ok=True)
        check_free(root)
        e4._write_atomic(session, pdb.canon(identity))
    parts.mkdir(parents=True, exist_ok=True)
    check_free(parts)
    tmp = Path(tempfile.mkdtemp(prefix=f"{pid}.tmp-{os.getpid()}-", dir=parts))
    objects = compute(tmp)
    files, _ = _inventory(tmp)
    record = {"partition": pid, "session_id": identity["session_id"], "status": "COMPLETE",
              "files": {k: pdb.file_sha256(p) for k, p in sorted(files.items())}, "objects": _plain(objects)}
    check_free(parts)
    (tmp / "partition.json").write_text(pdb.canon(record), encoding="utf-8")
    check_free(parts)
    os.replace(tmp, final)
    return "COMPLETE", leftovers


def write_table(df, path):
    """FAIR fragment: save_fair_csv bytes hashed, gzip without name or mtime, plain CSV removed; returns its sizes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plain = path.with_name(path.name[:-3])
    check_free(path.parent)
    pipelines.save_fair_csv(df, plain)
    sha_csv, bytes_csv = pdb.file_sha256(plain), plain.stat().st_size
    check_free(path.parent, bytes_csv)
    with open(plain, "rb") as src, open(path, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=6, mtime=0) as gz:
            shutil.copyfileobj(src, gz, 1 << 20)
    plain.unlink()
    return {"rows": int(len(df)), "sha256_csv": sha_csv, "bytes_csv": int(bytes_csv),
            "sha256_gz": pdb.file_sha256(path), "bytes_gz": int(path.stat().st_size)}


def read_table(path):
    """Fragment or CSV read back with round-trip float precision."""
    return pd.read_csv(path, float_precision="round_trip")


def stream_whole(paths, columns):
    """SHA-256 and rows of the canonical whole table: one header, then every fragment body, streamed."""
    h, rows, header = hashlib.sha256(), 0, (",".join(columns) + "\n").encode()
    h.update(header)
    for path in paths:
        with gzip.open(path, "rb") as fh:
            if fh.readline() != header:
                raise IncompleteWork(f"fragment {path} has another header")
            for line in fh:
                h.update(line)
                rows += 1
    return h.hexdigest(), rows


def fixture_values(length, label, start=0):
    """COST_FIXTURE reals 1 + frac((i + crc32(label)) * golden) at global indices start..start+length-1, no PRNG."""
    i = np.arange(start, start + length, dtype=np.float64)
    return 1.0 + np.mod((i + pdb.label_code(label)) * GOLDEN, 1.0)


def tiles(found, expected, what):
    """IncompleteWork unless the found block ranges are exactly the planned ones (no hole, overlap or foreign block)."""
    found, expected = set(found), set(expected)
    if found != expected:
        raise IncompleteWork(f"{what}: blocks {sorted(found - expected)} are foreign, {sorted(expected - found)} missing")


def _found(root, prefix):
    parts = Path(root) / "partitions"
    out = set()
    for p in parts.iterdir() if parts.is_dir() else ():
        if ".tmp-" in p.name or not p.name.startswith(prefix):
            continue
        match = re.fullmatch(rf"{re.escape(prefix)}{_R}", p.name)
        if not match:
            raise IncompleteWork(f"foreign partition {p.name}")
        out.add((int(match.group(1)), int(match.group(2))))
    return out


def write_plan(cfg, mode, root, identity, block):
    """Atomic campaign_plan.json fixing the block geometry and K; a different existing plan is refused."""
    root = Path(root)
    plan = {"session_id": identity["session_id"], "mode": mode, "block": e4._integer(block, "block", 1),
            "K": len(plan_partitions(cfg, mode, block)), "counts": role_counts(cfg)}
    path = root / "campaign_plan.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != plan:
            raise pdb.PartitionMismatch(f"{path} holds another plan or identity")
        return plan["K"]
    session = root / "session.json"
    if session.exists() and json.loads(session.read_text(encoding="utf-8")) != identity:
        raise pdb.PartitionMismatch(f"{session} holds another session identity")
    root.mkdir(parents=True, exist_ok=True)
    check_free(root)
    e4._write_atomic(path, pdb.canon(plan))
    return plan["K"]


def read_plan(root, identity):
    """campaign_plan.json of this identity; IncompleteWork when absent, PartitionMismatch when foreign."""
    path = Path(root) / "campaign_plan.json"
    if not path.exists():
        raise IncompleteWork(f"no campaign plan under {root}")
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("session_id") != identity["session_id"]:
        raise pdb.PartitionMismatch(f"{path} belongs to another session")
    return plan


def fit_statuses(cfg, root, identity):
    """Fit status of every cell whose fit partition is COMPLETE."""
    out = {}
    for c in cells_of(cfg):
        if (Path(root) / "partitions" / pid_fit(*c)).exists():
            out[c] = load_partition(root, pid_fit(*c), identity)["objects"]["fit"]["status"]
    return out


def next_pending(cfg, mode, root, identity):
    """First planned partition without a final directory, None when the plan is done."""
    plan = read_plan(root, identity)
    for pid in plan_partitions(cfg, mode, plan["block"], fit_statuses(cfg, root, identity)):
        if not (Path(root) / "partitions" / pid).exists():
            return pid
    return None


def verify_campaign(cfg, mode, root, identity):
    """Every expected partition COMPLETE and verified, no foreign final partition; returns counts and leftovers."""
    plan = read_plan(root, identity)
    fits = fit_statuses(cfg, root, identity)
    if set(fits) != set(cells_of(cfg)):
        raise IncompleteWork("some cell fits are missing")
    expected = plan_partitions(cfg, mode, plan["block"], fits)
    for pid in expected:
        load_partition(root, pid, identity)
    names = [p.name for p in (Path(root) / "partitions").iterdir()]
    foreign = sorted(set(n for n in names if ".tmp-" not in n) - set(expected))
    if foreign:
        raise IncompleteWork(f"foreign partitions {foreign}")
    return {"partitions": len(expected), "leftovers": sorted(n for n in names if ".tmp-" in n)}


def _guard(cfg, deadline, k):
    if k % cfg["limits"]["block_paths"]:
        return
    e4.guard(cfg["limits"]["block_paths"] * cfg["H"] * (1 + max(cfg["grid"])) * 8 * 4, cfg, deadline)
    soft = resource.getrlimit(resource.RLIMIT_CPU)[0]
    if soft != resource.RLIM_INFINITY and e4.process_cpu_s() > soft - CPU_GUARD_MARGIN_S:
        raise pdb.ResourceBlocked(f"process CPU is within {CPU_GUARD_MARGIN_S} s of its {soft} s limit")


def _interrupt(flag):
    if flag:
        raise FixtureInterrupt("deliberate cost_fixture interruption after the payload, before validation")


def _scalar_fields(cfg, mode):
    if mode == "cost_fixture":
        return _plain(e4.cell_calibration(fixture_values(cfg["n_cal"], "scalar_cal"), cfg["alpha"]))
    return _plain(e4.scalar_calibration(cfg, MODES[mode]))


def _fit_fields(cfg, mode, bg, N):
    if mode == "cost_fixture":
        def h(tag):
            return hashlib.sha256(f"COST_FIXTURE|{tag}|{bg}|{N}".encode()).hexdigest()
        return None, {"status": "OK", "basis_hash_e4": h("basis_e4"), "basis_hash_legacy": h("basis_legacy"),
                      "x_fit_sha256": h("x_fit"), "k_mp": 0, "mp_count_total": 1}
    try:
        cell = e4.fit_cell(cfg, bg, N, MODES[mode])
    except e4.EigenTieUnresolved:
        return {"N": N}, {"status": "EIGENVALUE_TIE_UNRESOLVED", **{k: None for k in FIT_FIELDS[1:]}}
    return cell, _plain({"status": "OK", **{k: cell[k] for k in FIT_FIELDS[1:]}})


def _checked_fit(cfg, mode, root, identity, bg, N):
    stored = load_partition(root, pid_fit(bg, N), identity)["objects"]["fit"]
    cell, fields = _fit_fields(cfg, mode, bg, N)
    if fields != stored:
        raise pdb.PartitionMismatch(f"the refit of {bg}:{N} differs from its fit partition")
    return cell, fields


def calmax_frame(cfg, mode, bg, N, cell, s, t, deadline=math.inf):
    """Calibration maxima of the dictionaries for global replicates [s, t), sorted (method, replicate)."""
    vals = {m: np.empty(t - s) for m in e4.DICTIONARY}
    if mode == "cost_fixture":
        vals = {m: fixture_values(t - s, f"calmax|{bg}|{N}|{m}", s) for m in e4.DICTIONARY}
    else:
        space = MODES[mode]
        for i in range(s, t):
            _guard(cfg, deadline, i - s)
            X, rec = e4.role_path(cfg, space, bg, "calibration", i, N), e4.coins_rec(cfg, space, "calibration", i)
            for m in e4.DICTIONARY:
                vals[m][i - s] = e4.method_log_path(m, cell, X, rec).max()
    df = pd.DataFrame({"background": bg, "N": N, "method": np.repeat(list(e4.DICTIONARY), t - s),
                       "replicate": np.tile(np.arange(s, t), len(e4.DICTIONARY)),
                       "max_log": np.concatenate([vals[m] for m in e4.DICTIONARY])}, columns=MAX_COLUMNS)
    return df.sort_values(["method", "replicate"], kind="stable").reset_index(drop=True)


def _fixture_diagnostics(cfg, bg, N, s, t):
    nu = cfg["backgrounds"][bg]
    cols = {"background": bg, "N": N, "replicate": np.arange(s, t), "claim_flag": "ORACLE_DIAGNOSTIC",
            "i_star_label": "GAUSSIAN_KL" if nu is None else "INFO_GAUSS_PROXY_T7", "k_star": 0, "k_mp": 0,
            "mp_count_total": 1}
    for col in e4.DIAG_COLUMNS:
        if col not in cols:
            cols[col] = fixture_values(t - s, f"diag|{col}|{bg}|{N}", s)
    return pd.DataFrame(cols, columns=e4.DIAG_COLUMNS)


def trial_frames(cfg, mode, bg, N, cell, status, h, role, s, t, deadline=math.inf):
    """Trial rows of global replicates [s, t) with the prototype loop; alternative OK cells add diagnostics and J_k."""
    methods = [m for m in e4.METHODS if status == "OK" or m not in e4.BASIS_METHODS]
    rows, diags, J = [], [], []
    oracle = role == "alternative" and status == "OK"
    if mode == "cost_fixture":
        hit = cfg["H"] // 2 if role == "alternative" else -1
        for i, m in ((i, m) for i in range(s, t) for m in methods):
            base = {"background": bg, "N": N, "method": m, "role": role, "replicate": i,
                    "claim_flag": e4.ORACLE.get(m, "NONE")}
            readings = (["predictive_rank"] if m in h else []) + ["anytime_valid_horizon"]
            rows += [{**base, "reading": r, "first_hit": hit} for r in readings]
        J = fixture_values((t - s) * N, f"axes|{bg}|{N}", s * N).reshape(t - s, N) if oracle else []
    else:
        space, gamma_h, scale = MODES[mode], pipelines.horizon_gamma(cfg["H"], cfg["alpha"]), e4.drift_scale(cfg)
        for i in range(s, t):
            _guard(cfg, deadline, i - s)
            u = e4.residual_direction(e4.direction_draw(cfg, space, i), N)
            X = e4.role_path(cfg, space, bg, role, i, N)
            if role == "alternative":
                X = X + scale * u
                if oracle:
                    d = e4.oracle_diagnostics(cell, u, cfg)
                    J.append(d.pop("j_k"))
                    diags.append({"background": bg, "N": N, "replicate": i, **d})
            rec = e4.coins_rec(cfg, space, role, i)
            for m in methods:
                log_m = e4.method_log_path(m, cell, X, rec, u if m in e4.ORACLE else None)
                base = {"background": bg, "N": N, "method": m, "role": role, "replicate": i,
                        "claim_flag": e4.ORACLE.get(m, "NONE")}
                if m in h:
                    rows.append({**base, "reading": "predictive_rank", "first_hit": e4.rank_first_hit(log_m, h[m])})
                rows.append({**base, "reading": "anytime_valid_horizon",
                             "first_hit": e4.horizon_first_hit(log_m, gamma_h)})
    out = {"trials.csv.gz": pd.DataFrame(rows, columns=e4.TRIAL_COLUMNS).sort_values(
        e4.TRIAL_KEYS, kind="stable").reset_index(drop=True)}
    if oracle:
        J = np.asarray(J, dtype=np.float64)
        if J.shape != (t - s, N):
            raise IncompleteWork(f"J_k block of {bg}:{N} has shape {J.shape}, expected {(t - s, N)}")
        out["diagnostics.csv.gz"] = (_fixture_diagnostics(cfg, bg, N, s, t) if mode == "cost_fixture"
                                     else pd.DataFrame(diags, columns=e4.DIAG_COLUMNS))
        out["axes.csv.gz"] = pd.DataFrame({"background": bg, "N": N, "replicate": np.repeat(np.arange(s, t), N),
                                           "axis": np.tile(np.arange(N), t - s), "j_k": J.ravel(),
                                           "claim_flag": "ORACLE_DIAGNOSTIC"}, columns=e4.AXES_COLUMNS)
    return out


def check_trials(trials, cells, calibration, counts):
    """IncompleteWork unless each expected (cell, method, role, reading) group holds replicates 0..n-1 exactly once."""
    if trials.duplicated(e4.TRIAL_KEYS).any():
        raise IncompleteWork("duplicated trial keys")
    cal = {(r.background, int(r.N), r.method): r.status for r in calibration.itertuples()}
    expected = set()
    for r in cells.itertuples():
        for m in e4.METHODS:
            if r.status != "OK" and m in e4.BASIS_METHODS:
                continue
            readings = ["anytime_valid_horizon"] + (["predictive_rank"] if cal.get((r.background, int(r.N), m)) == "OK"
                                                    else [])
            expected |= {(r.background, int(r.N), m, role, x) for role in TRIAL_ROLES for x in readings}
    seen = set()
    for key, reps in trials.groupby(["background", "N", "method", "role", "reading"], sort=True)["replicate"]:
        k = (key[0], int(key[1]), key[2], key[3], key[4])
        if k not in expected or not np.array_equal(np.sort(reps.to_numpy()), np.arange(counts[k[3]])):
            raise IncompleteWork(f"trial group {k} is unexpected or does not hold replicates 0..{counts.get(k[3])}-1")
        seen.add(k)
    if seen != expected:
        raise IncompleteWork(f"missing trial groups {sorted(expected - seen)[:5]}")


def _part(root, pid):
    return Path(root) / "partitions" / pid


def _build_scalar(cfg, mode, root, identity, plan, info, deadline, interrupt):
    def compute(tmp):
        fields = _scalar_fields(cfg, mode)
        pipelines.save_fair_csv(pd.DataFrame([fields], columns=SCALAR_FIELDS), tmp / "scalar_calibration.csv")
        _interrupt(interrupt)
        return {"scalar": fields}
    return compute


def _build_fit(cfg, mode, root, identity, plan, info, deadline, interrupt):
    bg, N = info["background"], info["N"]

    def compute(tmp):
        _, fields = _fit_fields(cfg, mode, bg, N)
        pipelines.save_fair_csv(pd.DataFrame([{"background": bg, "N": N, **fields}], columns=e4.CELL_COLUMNS),
                                tmp / "cell.csv")
        _interrupt(interrupt)
        return {"fit": fields}
    return compute


def _build_calmax(cfg, mode, root, identity, plan, info, deadline, interrupt):
    bg, N, s, t = info["background"], info["N"], info["start"], info["stop"]
    cell, fields = _checked_fit(cfg, mode, root, identity, bg, N)
    if fields["status"] != "OK":
        raise IncompleteWork(f"calmax of the refused cell {bg}:{N}")

    def compute(tmp):
        tables = {"maxima.csv.gz": write_table(calmax_frame(cfg, mode, bg, N, cell, s, t, deadline),
                                               tmp / "maxima.csv.gz")}
        _interrupt(interrupt)
        return {"range": [s, t], "fit": fields, "tables": tables}
    return compute


def _cell_blocks(cfg, root, identity, plan, bg, N, role, status):
    n = role_counts(cfg)[role]
    prefix = f"calmax_{bg}_N{N}_" if role == "calibration" else f"trials_{bg}_N{N}_{role}_"
    found = _found(root, prefix)
    expected = block_ranges(n, plan["block"]) if role != "calibration" or status == "OK" else []
    tiles(found, expected, prefix.rstrip("_"))
    pids = [pid_calmax(bg, N, s, t) if role == "calibration" else pid_trials(bg, N, role, s, t) for s, t in expected]
    return [(pid, s, t, load_partition(root, pid, identity)) for pid, (s, t) in zip(pids, expected)]


def indexed_maxima(frames, bg, N, n, status):
    """Dictionary maxima as float64 vectors indexed by global replicate i = 0..n-1, each covered exactly once."""
    dictionaries = [m for m in e4.DICTIONARY if status == "OK"]
    maxima = {m: np.full(n, np.nan) for m in dictionaries}
    seen = {m: np.zeros(n, dtype=np.int64) for m in dictionaries}
    for pid, s, t, df in frames:
        if set(df["method"]) != set(dictionaries) or (df["background"] != bg).any() or (df["N"] != N).any():
            raise IncompleteWork(f"{pid} holds foreign rows")
        for m, g in df.groupby("method"):
            idx = g["replicate"].to_numpy()
            if idx.min() < s or idx.max() >= t:
                raise IncompleteWork(f"{pid} holds replicates outside [{s}, {t})")
            maxima[m][idx] = g["max_log"].to_numpy()
            np.add.at(seen[m], idx, 1)
    if any((seen[m] != 1).any() for m in dictionaries):
        raise IncompleteWork(f"calibration maxima of {bg}:{N} do not cover 0..{n - 1} exactly once")
    return maxima


def calibration_table(cfg, statuses, scalar_fields, maxima):
    """CAL_COLUMNS rows of e4._cell: one shared scalar copy, dictionary rank thresholds, refusals kept as status rows."""
    rows = []
    for (bg, N), status in statuses.items():
        methods = [m for m in e4.METHODS if status == "OK" or m not in e4.BASIS_METHODS]
        cal = {**{m: dict(scalar_fields) for m in e4.SCALAR if m in methods},
               **{m: e4.cell_calibration(maxima[(bg, N)][m], cfg["alpha"]) for m in e4.DICTIONARY if m in methods}}
        rows += [{"background": bg, "N": N, "method": m, "claim_flag": e4.ORACLE.get(m, "NONE"),
                  **cal.get(m, {"status": status})} for m in e4.METHODS]
    return pd.DataFrame(rows, columns=e4.CAL_COLUMNS).sort_values(
        ["background", "N", "method"], kind="stable").reset_index(drop=True)


def _build_thresholds(cfg, mode, root, identity, plan, info, deadline, interrupt):
    scalar = load_partition(root, "scalar_cal", identity)
    fits = {c: load_partition(root, pid_fit(*c), identity) for c in cells_of(cfg)}
    blocks = {c: _cell_blocks(cfg, root, identity, plan, *c, "calibration", fits[c]["objects"]["fit"]["status"])
              for c in cells_of(cfg)}
    n = cfg["n_cal"]

    def compute(tmp):
        statuses = {c: fit["objects"]["fit"]["status"] for c, fit in fits.items()}
        maxima = {}
        for (bg, N), status in statuses.items():
            frames = [(pid, s, t, read_table(_part(root, pid) / "maxima.csv.gz")) for pid, s, t, _ in blocks[(bg, N)]]
            maxima[(bg, N)] = indexed_maxima(frames, bg, N, n, status)
        calibration = calibration_table(cfg, statuses, scalar["objects"]["scalar"], maxima)
        cell_rows = [{"background": bg, "N": N, **fit["objects"]["fit"]} for (bg, N), fit in fits.items()]
        cells = pd.DataFrame(cell_rows, columns=e4.CELL_COLUMNS).sort_values(
            ["background", "N"], kind="stable").reset_index(drop=True)
        pipelines.save_fair_csv(calibration, tmp / "calibration.csv")
        pipelines.save_fair_csv(cells, tmp / "cells.csv")
        _interrupt(interrupt)
        consumed = ["scalar_cal"] + [pid_fit(*c) for c in fits] + [b[0] for c in blocks for b in blocks[c]]
        return {"consumed": {pid: pdb.file_sha256(_part(root, pid) / "partition.json") for pid in consumed}}
    return compute


def _thresholds_tables(root, identity):
    thr = load_partition(root, "thresholds", identity)
    return thr, read_table(_part(root, "thresholds") / "cells.csv"), read_table(_part(root, "thresholds") /
                                                                                   "calibration.csv")


def _build_trials(cfg, mode, root, identity, plan, info, deadline, interrupt):
    bg, N, role, s, t = info["background"], info["N"], info["role"], info["start"], info["stop"]
    thr, _, cal = _thresholds_tables(root, identity)
    cell, fields = _checked_fit(cfg, mode, root, identity, bg, N)
    rows = cal[(cal["background"] == bg) & (cal["N"] == N)]
    h = {r.method: float.fromhex(r.threshold_hex) for r in rows.itertuples() if r.status == "OK"}

    def compute(tmp):
        frames = trial_frames(cfg, mode, bg, N, cell, fields["status"], h, role, s, t, deadline)
        tables = {name: write_table(df, tmp / name) for name, df in frames.items()}
        _interrupt(interrupt)
        return {"range": [s, t], "role": role, "fit": fields, "calibration_csv_sha256": thr["files"]["calibration.csv"],
                "tables": tables}
    return compute


def _stream_axes(blocks, out, bg, N, n_alt):
    header = (",".join(e4.AXES_COLUMNS) + "\n").encode()
    whole, rows, rep, axis = hashlib.sha256(header), 0, 0, 0
    with open(out, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=6, mtime=0) as gz:
        gz.write(header)
        for path, s, t, sha_csv in blocks:
            block_hash = hashlib.sha256()
            with gzip.open(path, "rb") as fh:
                head = fh.readline()
                block_hash.update(head)
                if head != header or rep != s:
                    raise IncompleteWork(f"{path}: foreign header or replicate gap before {s}")
                for line in fh:
                    block_hash.update(line)
                    f = line.rstrip(b"\n").split(b",")
                    if (len(f) != 6 or f[0].decode() != bg or int(f[1]) != N or int(f[2]) != rep
                            or int(f[3]) != axis):
                        raise IncompleteWork(f"{path}: expected replicate {rep} axis {axis} of {bg}:{N}")
                    axis = (axis + 1) % N
                    rep += axis == 0
                    whole.update(line)
                    gz.write(line)
                    rows += 1
            if block_hash.hexdigest() != sha_csv:
                raise pdb.PartitionMismatch(f"{path}: canonical bytes differ from the block record")
            if rep != t or axis:
                raise IncompleteWork(f"{path}: J_k rows end at replicate {rep} axis {axis}, expected {t}")
    if rep != n_alt:
        raise IncompleteWork(f"J_k axes of {bg}:{N} end at replicate {rep}, expected {n_alt}")
    return {"rows": rows, "sha256_csv": whole.hexdigest(), "sha256_gz": pdb.file_sha256(out),
            "bytes_gz": int(Path(out).stat().st_size)}


def _build_merge(cfg, mode, root, identity, plan, info, deadline, interrupt):
    thr, cells, cal = _thresholds_tables(root, identity)
    status = {(r.background, int(r.N)): r.status for r in cells.itertuples()}
    scalar = load_partition(root, "scalar_cal", identity)
    fits = {c: load_partition(root, pid_fit(*c), identity) for c in cells_of(cfg)}
    blocks = {(c, role): _cell_blocks(cfg, root, identity, plan, *c, role, status[c])
              for c in cells_of(cfg) for role in ("calibration",) + TRIAL_ROLES}
    counts = role_counts(cfg)

    def frag(name, pid):
        return _part(root, pid) / name

    def compute(tmp):
        fragments = {t: [] for t in TABLES}
        mapping = []

        def add(table, cell, df=None, info_=None):
            rel = f"{table}/{cell[0]}_N{cell[1]}.csv.gz"
            info_ = write_table(df, tmp / rel) if info_ is None else info_
            fragments[table].append({"file": rel, "rows": info_["rows"], "sha256_csv": info_["sha256_csv"]})
            return rel

        for c in cells_of(cfg):
            ok = status[c] == "OK"
            if ok:
                rel = f"calibration_maxima/{c[0]}_N{c[1]}.csv.gz"
                df = pd.concat([read_table(frag("maxima.csv.gz", b[0])) for b in blocks[(c, "calibration")]],
                               ignore_index=True).sort_values(["method", "replicate"], kind="stable")
                for m, g in df.groupby("method"):
                    if not np.array_equal(np.sort(g["replicate"].to_numpy()), np.arange(counts["calibration"])):
                        raise IncompleteWork(f"calibration maxima of {c} {m} are incomplete")
                add("calibration_maxima", c, df.reset_index(drop=True))
                mapping += [{"partition": b[0], "table": "calibration_maxima", "fragment": rel, "role": None,
                             "start": b[1], "stop": b[2], **_block_fact(b[3], "maxima.csv.gz")}
                            for b in blocks[(c, "calibration")]]
            trial_blocks = blocks[(c, "holdout")] + blocks[(c, "alternative")]
            df = pd.concat([read_table(frag("trials.csv.gz", b[0])) for b in trial_blocks], ignore_index=True)
            check_trials(df, cells[(cells["background"] == c[0]) & (cells["N"] == c[1])],
                         cal[(cal["background"] == c[0]) & (cal["N"] == c[1])], counts)
            rel = add("trials", c, df.sort_values(e4.TRIAL_KEYS, kind="stable").reset_index(drop=True))
            mapping += [{"partition": b[0], "table": "trials", "fragment": rel,
                         "role": b[3]["objects"]["role"], "start": b[1], "stop": b[2],
                         **_block_fact(b[3], "trials.csv.gz")} for b in trial_blocks]
            if ok:
                alt = blocks[(c, "alternative")]
                df = pd.concat([read_table(frag("diagnostics.csv.gz", b[0])) for b in alt], ignore_index=True)
                if not np.array_equal(df["replicate"].to_numpy(), np.arange(counts["alternative"])):
                    raise IncompleteWork(f"diagnostics of {c} do not cover the alternative replicates")
                rel = add("diagnostics", c, df)
                mapping += [{"partition": b[0], "table": "diagnostics", "fragment": rel, "role": "alternative",
                             "start": b[1], "stop": b[2], **_block_fact(b[3], "diagnostics.csv.gz")} for b in alt]
                rel = f"diagnostics_axes/{c[0]}_N{c[1]}.csv.gz"
                (tmp / "diagnostics_axes").mkdir(exist_ok=True)
                info_ = _stream_axes([(frag("axes.csv.gz", b[0]), b[1], b[2],
                                       b[3]["objects"]["tables"]["axes.csv.gz"]["sha256_csv"]) for b in alt],
                                     tmp / rel, c[0], c[1], counts["alternative"])
                add("diagnostics_axes", c, info_=info_)
                mapping += [{"partition": b[0], "table": "diagnostics_axes", "fragment": rel, "role": "alternative",
                             "start": b[1], "stop": b[2], **_block_fact(b[3], "axes.csv.gz")} for b in alt]
        tables = {}
        for table, frags in fragments.items():
            sha, rows = stream_whole([tmp / f["file"] for f in frags], TABLES[table])
            tables[table] = {"columns": TABLES[table], "fragments": frags, "rows": rows, "sha256_whole": sha}
        manifest = {"session_id": identity["session_id"], "mode": mode,
                    "label": "COST_FIXTURE" if mode == "cost_fixture" else "E4_SCIENCE", "tables": tables}
        producers = ["scalar_cal"] + [pid_fit(*c) for c in fits] + ["thresholds"] + [
            b[0] for key in blocks for b in blocks[key]]
        records = {"scalar_cal": scalar, "thresholds": thr, **{pid_fit(*c): fits[c] for c in fits},
                   **{b[0]: b[3] for key in blocks for b in blocks[key]}}
        lineage = {"session_id": identity["session_id"], "block": plan["block"],
                   "partitions": {pid: records[pid] for pid in producers}, "blocks": mapping}
        (tmp / "manifest.json").write_text(pdb.canon(manifest), encoding="utf-8")
        (tmp / "lineage.json").write_text(pdb.canon(lineage), encoding="utf-8")
        _interrupt(interrupt)
        return {"tables": {t: {"rows": v["rows"], "sha256_whole": v["sha256_whole"]} for t, v in tables.items()}}
    return compute


def _block_fact(record, name):
    fact = record["objects"]["tables"][name]
    return {"rows": fact["rows"], "sha256_csv": fact["sha256_csv"]}


def _build_analysis(cfg, mode, root, identity, plan, info, deadline, interrupt):
    merge = load_partition(root, "merge", identity)
    _, cells, cal = _thresholds_tables(root, identity)
    manifest = json.loads((_part(root, "merge") / "manifest.json").read_text(encoding="utf-8"))
    counts = role_counts(cfg)

    def compute(tmp):
        trials = pd.concat([read_table(_part(root, "merge") / f["file"])
                            for f in manifest["tables"]["trials"]["fragments"]], ignore_index=True)
        check_trials(trials, cells, cal, counts)
        n = None if mode == "full" else {"alternative": counts["alternative"], "holdout": counts["holdout"]}
        outputs = {"holdout_fpr": e4.holdout_fpr(trials)}
        for reading in e4.READINGS:
            res = e4.analyse(trials, cfg, MODES[mode], reading, n)
            outputs.update({f"{k}_{reading}": res[k] for k in ("cells", "contrasts", "warnings")})
        (tmp / "analysis").mkdir()
        for name, df in outputs.items():
            check_free(tmp)
            pipelines.save_fair_csv(df, tmp / "analysis" / f"{name}.csv")
        _interrupt(interrupt)
        return {"merge_manifest_sha256": merge["files"]["manifest.json"], "trial_rows": int(len(trials))}
    return compute


BUILDERS = {"scalar_cal": _build_scalar, "fit": _build_fit, "calmax": _build_calmax, "thresholds": _build_thresholds,
            "trials": _build_trials, "merge": _build_merge, "analysis": _build_analysis}


def run_phase(cfg, mode, root, identity, pid, deadline=math.inf, interrupt=False):
    """Run or verify one planned partition; dependencies are checked before anything is written."""
    if interrupt and mode != "cost_fixture":
        raise ValueError("--fixture-interrupt is a cost_fixture test hook only")
    root = Path(root)
    plan = read_plan(root, identity)
    info = parse_pid(pid, cfg, mode, plan["block"])
    if (root / "partitions" / pid).exists():
        return run_production_partition(root, pid, identity, None)[0]
    compute = BUILDERS[info["kind"]](cfg, mode, root, identity, plan, info, deadline, interrupt)
    return run_production_partition(root, pid, identity, compute)[0]


class ActivationRefused(RuntimeError):
    """The full campaign is not activated: absent, malformed, stale or unsupported activation evidence."""


class GateStop(RuntimeError):
    """A blocking budget, disk, memory or bookkeeping condition: STOP with the cost kept, a decision is required."""


ATTEMPTS_DIR = Path("logs/stream_19_e4_production/attempts")
RSS_CAP_KIB = 8 * 2 ** 20
PRIOR_SOURCE = {"path": "results/e4_alignment/cost_report_20261112/external_attempts.csv",
                "sha256": "45b79711c50eac4b286cfc9d8326b64dc241f2033c75cd07d0d83b4099b66925"}
COST_STAGE_RE = (r"(startup|identity|fit_cell|draw:(calibration|holdout|alternative)|"
                 r"paths:[A-Za-z0-9()-]+:(calibration|holdout|alternative)|dict_calibration|"
                 r"readings:(holdout|alternative)|oracle_diagnostics|j_k_table)")
_ATTEMPT_ID = re.compile(r"A[0-9]{7}")
_TIME_LINE = re.compile(r"([0-9]+(?:\.[0-9]+)?) ([0-9]+(?:\.[0-9]+)?) ([0-9]+(?:\.[0-9]+)?) ([0-9]+) (-?[0-9]+)")


def read_attempt(directory):
    """One attempt: RUNNING without exit.txt, MEASURED with a GNU time line and the host exit code, else UNKNOWN."""
    d = Path(directory)
    cmd = (d / "cmd.txt").read_text(encoding="utf-8").strip() if (d / "cmd.txt").is_file() else None
    if not (d / "exit.txt").exists():
        return {"attempt_id": d.name, "state": "RUNNING", "command": cmd}
    try:
        line = (d / "time.txt").read_text(encoding="utf-8").strip().splitlines()[-1].strip()
        match, rc = _TIME_LINE.fullmatch(line), int((d / "exit.txt").read_text(encoding="utf-8").strip())
        result = json.loads((d / "result.json").read_text(encoding="utf-8")) if (d / "result.json").is_file() else None
    except (OSError, ValueError, IndexError):
        match = None
    if match is None or cmd is None:
        return {"attempt_id": d.name, "state": "UNKNOWN", "command": cmd}
    tokens = cmd.split()
    return {"attempt_id": d.name, "state": "MEASURED", "command": cmd, "user_s": float(match.group(1)),
            "system_s": float(match.group(2)), "wall_s": float(match.group(3)), "max_rss_kib": int(match.group(4)),
            "time_status": int(match.group(5)), "exit": rc,
            "intended_interrupt": rc == 7 and "--fixture-interrupt" in tokens and "cost_fixture" in tokens,
            "result": result, "files_sha256": {p.name: pdb.file_sha256(p) for p in sorted(d.iterdir()) if p.is_file()}}


IMPORT_CATEGORIES = ("tests", "administrative")
_IMPORT_FILE = re.compile(r"I[0-9]{7}\.json")


def imports_dir(attempts_dir):
    """Imported measured costs live beside the attempt ledger, append-only."""
    return Path(attempts_dir).parent / "imports"


def _import_facts(source):
    df = read_table(source)
    if not {"source_id", "cpu_s"} <= set(df.columns) or df.empty or df["source_id"].duplicated().any():
        raise ValueError(f"{source} is not a cost table with unique source_id and cpu_s")
    cpu = df["cpu_s"].to_numpy(dtype=np.float64)
    if not np.isfinite(cpu).all() or (cpu < 0).any():
        raise ValueError("imported costs must be finite and non-negative: an unknown cost is never zero")
    return {"rows": int(len(df)), "source_ids": sorted(df["source_id"].astype(str)), "cpu_s": math.fsum(cpu)}


def read_imports(attempts_dir):
    """Contiguous import records whose CPU, rows and ids are recomputed from their hashed source; GateStop else."""
    d, out = imports_dir(attempts_dir), []
    for p in sorted(d.iterdir()) if d.is_dir() else ():
        if not _IMPORT_FILE.fullmatch(p.name) or p.is_symlink() or not p.is_file() or p.stem != f"I{len(out) + 1:07d}":
            raise GateStop(f"foreign or out-of-sequence entry {p} in the cost imports")
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
            ok = (rec["import_id"] == p.stem and rec["category"] in IMPORT_CATEGORIES
                  and pdb.file_sha256(_leaf_path(rec["source"])) == rec["source"]["sha256"]
                  and _import_facts(_leaf_path(rec["source"])) == {k: rec[k] for k in ("rows", "source_ids", "cpu_s")})
        except (OSError, ValueError, KeyError, TypeError):
            ok = False
        if not ok:
            raise GateStop(f"import {p.name} is unreadable or differs from its hashed source (CPU, rows or ids)")
        out.append({**rec, "record_sha256": pdb.file_sha256(p)})
    return out


def import_costs(attempts_dir, source, category):
    """Immutable import of measured costs (FAIR CSV with source_id, cpu_s) keeping its SHA-256 provenance."""
    if category not in IMPORT_CATEGORIES:
        raise ValueError(f"import category {category!r} is not one of {IMPORT_CATEGORIES}")
    facts, leaf, current = _import_facts(source), _leaf(source), read_imports(attempts_dir)
    if any(r["source"]["sha256"] == leaf["sha256"] or set(r["source_ids"]) & set(facts["source_ids"]) for r in current):
        raise pdb.PartitionMismatch(f"{source} overlaps costs already imported: no double count")
    d = imports_dir(attempts_dir)
    d.mkdir(parents=True, exist_ok=True)
    check_free(d)
    record = {"import_id": f"I{len(current) + 1:07d}", "category": category, "source": leaf, **facts,
              "label": "MEASURED_IMPORTED"}
    with open(d / f"{record['import_id']}.json", "x", encoding="utf-8") as fh:
        fh.write(pdb.canon(record))
    return record


def _consumed(prior_cpu_s, imports, attempts):
    return prior_cpu_s + math.fsum(r["cpu_s"] for r in imports) + sum(a["user_s"] + a["system_s"] for a in attempts)


def ledger(attempts_dir, active=None, prior_cpu_s=PRIOR_CPU_S):
    """Consumed CPU = prior + imports + every finalized attempt; GateStop on any unfinished attempt but the active."""
    d = Path(attempts_dir)
    rows, ids = [], []
    for e in sorted(d.iterdir()) if d.is_dir() else ():
        if not _ATTEMPT_ID.fullmatch(e.name) or e.is_symlink() or not e.is_dir():
            raise GateStop(f"foreign entry {e} in the attempt ledger")
        ids.append(e.name)
        a = read_attempt(e)
        if e.name == active:
            if a["state"] != "RUNNING":
                raise GateStop(f"the active attempt {active} is already finalized")
            continue
        if a["state"] != "MEASURED":
            raise GateStop(f"attempt {e.name} is {a['state']}: its cost is unknown, never zero")
        rows.append(a)
    if active is not None and active not in ids:
        raise GateStop(f"the active attempt {active} was not reserved by the host")
    imports = read_imports(attempts_dir)
    consumed = _consumed(prior_cpu_s, imports, rows)
    snapshot = {"cutoff": rows[-1]["attempt_id"] if rows else None, "n_attempts": len(rows),
                "attempts_sha256": hashlib.sha256(pdb.canon(rows).encode()).hexdigest(), "consumed_cpu_s": consumed,
                "prior_cpu_s": prior_cpu_s, "prior_source": PRIOR_SOURCE,
                "imports": [{"import_id": r["import_id"], "sha256": r["record_sha256"]} for r in imports],
                "imports_cpu_s": math.fsum(r["cpu_s"] for r in imports)}
    return {"attempts": rows, "imports": imports, "consumed_cpu_s": consumed, "snapshot": snapshot}


def check_snapshot(attempts_dir, snapshot):
    """GateStop unless the finalized prefix and the snapshot imports are unchanged (later ones may append)."""
    d = Path(attempts_dir)
    cutoff = snapshot["cutoff"]
    rows = [read_attempt(e) for e in (sorted(d.iterdir()) if d.is_dir() else ()) if cutoff is not None and e.name <= cutoff]
    if (len(rows) != snapshot["n_attempts"] or any(a["state"] != "MEASURED" for a in rows)
            or hashlib.sha256(pdb.canon(rows).encode()).hexdigest() != snapshot["attempts_sha256"]):
        raise GateStop(f"the attempt prefix up to {cutoff} differs from its frozen snapshot")
    current = {r["import_id"]: r["record_sha256"] for r in read_imports(attempts_dir)}
    if any(current.get(i["import_id"]) != i["sha256"] for i in snapshot.get("imports", [])):
        raise GateStop("an imported cost of the frozen snapshot changed or disappeared")


def _existing(path):
    path = Path(path).absolute()
    while not path.exists():
        path = path.parent
    return path


def gate(attempts_dir, active, remaining_cpu_s, disk_path, next_bytes=0, decisions=None, ceiling_cpu_s=CPU_CAP_S):
    """Pre-run STOP check: ledger, previous exit, RSS, consumed + next envelope + remaining CPU, free disk."""
    led = ledger(attempts_dir, active)
    decisions = Path(decisions) if decisions else Path(attempts_dir).parent / "decisions"

    def decided(a):
        return (decisions / f"{a['attempt_id']}.txt").is_file()

    prev = led["attempts"][-1] if led["attempts"] else None
    if prev and prev["exit"] not in (0, 10) and not prev["intended_interrupt"] and not decided(prev):
        raise GateStop(f"attempt {prev['attempt_id']} ended with {prev['exit']}: a recorded decision is required")
    over = [a["attempt_id"] for a in led["attempts"] if a["max_rss_kib"] > RSS_CAP_KIB and not decided(a)]
    if over:
        raise GateStop(f"attempts {over} exceeded the 8 GiB RSS cap")
    total = led["consumed_cpu_s"] + NEXT_INVOCATION_CPU_S + float(remaining_cpu_s)
    if not math.isfinite(total) or total > min(CPU_CAP_S, ceiling_cpu_s):
        raise GateStop(f"consumed + next envelope + remaining = {total} CPU s exceeds {min(CPU_CAP_S, ceiling_cpu_s)}")
    try:
        check_free(_existing(disk_path), next_bytes)
    except OSError as exc:
        raise GateStop(str(exc)) from exc
    return led


def cost_kernels(cfg, bg, N, role, replicates, meter, deadline=math.inf):
    """P1 cost entry: real kernels of one role on pilot replicates [0, replicates); every payload is discarded."""
    space, gamma_h = "pilot", pipelines.horizon_gamma(cfg["H"], cfg["alpha"])
    cost_fixture_log_threshold = math.log(gamma_h)
    with meter.stage("fit_cell", 1):
        try:
            cell, status = e4.fit_cell(cfg, bg, N, space), "OK"
        except e4.EigenTieUnresolved:
            cell, status = {"N": N}, "EIGENVALUE_TIE_UNRESOLVED"
    methods = [m for m in e4.METHODS if status == "OK" or m not in e4.BASIS_METHODS]
    if role == "calibration":
        methods = [m for m in e4.DICTIONARY if m in methods]
    maxima, scale = {m: [] for m in methods}, e4.drift_scale(cfg)
    for i in range(replicates):
        _guard(cfg, deadline, i)
        with meter.stage(f"draw:{role}", 1):
            u = e4.residual_direction(e4.direction_draw(cfg, space, i), N)
            X = e4.role_path(cfg, space, bg, role, i, N)
            X = X + scale * u if role == "alternative" else X
        rec = e4.coins_rec(cfg, space, role, i)
        for m in methods:
            with meter.stage(f"paths:{m}:{role}", 1):
                log_m = e4.method_log_path(m, cell, X, rec, u if m in e4.ORACLE else None)
            if role == "calibration":
                maxima[m].append(float(log_m.max()))
                continue
            with meter.stage(f"readings:{role}", 1):
                e4.rank_first_hit(log_m, cost_fixture_log_threshold)
                e4.horizon_first_hit(log_m, gamma_h)
        if role == "alternative" and status == "OK":
            with meter.stage("oracle_diagnostics", 1):
                d = e4.oracle_diagnostics(cell, u, cfg)
            with meter.stage("j_k_table", 1):
                pd.DataFrame({"replicate": i, "axis": np.arange(N), "j_k": d["j_k"]})
    if role == "calibration":
        with meter.stage("dict_calibration", replicates):
            for m in methods:
                e4.cell_calibration(np.asarray(maxima[m]), cfg["alpha"])
    return status


ANALYSIS_FILES = ["holdout_fpr.csv"] + [f"{k}_{r}.csv" for r in e4.READINGS for k in ("cells", "contrasts", "warnings")]
COST_SOURCE_COLUMNS = ["source", "category", "provenance_sha256", "cpu_s", "wall_s", "max_rss_kib", "exit", "label"]
PRODUCER_PHASES = {"plan", "next", "run", "verify", "publish", "verify-publication", "cost-kernels"}


def _attempt_category(a):
    tokens = (a.get("command") or "").split()
    phase = tokens[tokens.index("--phase") + 1] if "--phase" in tokens[:-1] else None
    return "producer" if phase in PRODUCER_PHASES else "administrative"


def cost_sources(led):
    """One row per measured cost source: prior pilot, imports with their provenance, finalized attempts by category."""
    rows = [{"source": "PRIOR_COST_PILOT", "category": "prior_pilot", "provenance_sha256": PRIOR_SOURCE["sha256"],
             "cpu_s": led["snapshot"]["prior_cpu_s"], "label": "MEASURED_PRIOR"}]
    rows += [{"source": r["import_id"], "category": r["category"], "provenance_sha256": r["source"]["sha256"],
              "cpu_s": r["cpu_s"], "label": r["label"]} for r in led["imports"]]
    rows += [{"source": a["attempt_id"], "category": _attempt_category(a), "provenance_sha256": a["files_sha256"].get(
        "time.txt"), "cpu_s": a["user_s"] + a["system_s"], "wall_s": a["wall_s"], "max_rss_kib": a["max_rss_kib"],
              "exit": a["exit"], "label": "MEASURED_ATTEMPT"} for a in led["attempts"]]
    return pd.DataFrame(rows, columns=COST_SOURCE_COLUMNS)


def _leaf(path):
    p = Path(path)
    rel = Path(os.path.relpath(p.absolute(), e4.REPO_ROOT)).as_posix()
    return {"path": rel, "sha256": pdb.file_sha256(p), "bytes": int(p.stat().st_size)}


def _leaf_path(leaf):
    return e4.REPO_ROOT / leaf["path"]


def _check_leaf(leaf):
    try:
        ok = isinstance(leaf, dict) and pdb.file_sha256(_leaf_path(leaf)) == leaf["sha256"]
    except (OSError, KeyError, TypeError):
        ok = False
    if not ok:
        raise ActivationRefused(f"evidence {leaf!r} is absent or differs from its recorded SHA-256")


def _publication_sources(cfg, root, activation=None):
    root = Path(root)
    part = root / "partitions"
    manifest = json.loads((part / "merge" / "manifest.json").read_text(encoding="utf-8"))
    src = {"session.json": root / "session.json", "campaign_plan.json": root / "campaign_plan.json",
           "manifest.json": part / "merge" / "manifest.json", "lineage.json": part / "merge" / "lineage.json",
           "records/scalar_cal/scalar_calibration.csv": part / "scalar_cal" / "scalar_calibration.csv",
           "records/thresholds/calibration.csv": part / "thresholds" / "calibration.csv",
           "records/thresholds/cells.csv": part / "thresholds" / "cells.csv"}
    src.update({f"records/{pid_fit(*c)}/cell.csv": part / pid_fit(*c) / "cell.csv" for c in cells_of(cfg)})
    src.update({f["file"]: part / "merge" / f["file"] for t in manifest["tables"].values() for f in t["fragments"]})
    src.update({f"analysis/{name}": part / "analysis" / "analysis" / name for name in ANALYSIS_FILES})
    if activation is not None:
        src["activation/activation.json"] = Path(activation)
        act = json.loads(Path(activation).read_text(encoding="utf-8"))
        src.update({f"activation/receipts/{kind}.json": _leaf_path(leaf) for kind, leaf in act["receipts"].items()})
    return src


def publish(cfg, mode, root, identity, target, attempts_dir, active=None, activation=None):
    """Closed publication staged under the work root, verified, marked by PUBLISHED.json last, renamed atomically."""
    root, target = Path(root), Path(target)
    verify_campaign(cfg, mode, root, identity)
    if target.exists() or target.is_symlink():
        try:
            same = (json.loads((target / "PUBLISHED.json").read_text(encoding="utf-8")).get("session_id")
                    == identity["session_id"] and (target / "manifest.json").read_bytes()
                    == (root / "partitions" / "merge" / "manifest.json").read_bytes())
        except (OSError, ValueError, AttributeError):
            same = False
        if not same:
            raise pdb.PartitionMismatch(f"{target} exists and differs from this publication")
        verify_publication(target)
        return "SKIPPED_COMPLETE"
    if activation is not None and json.loads(Path(activation).read_text(encoding="utf-8")).get(
            "session_id") != identity["session_id"]:
        raise pdb.PartitionMismatch(f"{activation} belongs to another session")
    led = ledger(attempts_dir, active)
    staging = Path(tempfile.mkdtemp(prefix="publish.tmp-", dir=root))
    for rel, src in sorted(_publication_sources(cfg, root, activation).items()):
        dst = staging / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        check_free(staging, src.stat().st_size)
        shutil.copyfile(src, dst)
    (staging / "ledger").mkdir()
    check_free(staging)
    (staging / "ledger" / "attempts.jsonl").write_text("".join(pdb.canon(a) + "\n" for a in led["attempts"]),
                                                      encoding="utf-8")
    pipelines.save_fair_csv(cost_sources(led), staging / "ledger" / "cpu_ledger.csv")
    files, _ = _inventory(staging)
    published = {"session_id": identity["session_id"], "mode": mode,
                 "label": "COST_FIXTURE" if mode == "cost_fixture" else "E4_SCIENCE", "ledger_snapshot": led["snapshot"],
                 "files": {k: {"sha256": pdb.file_sha256(p), "bytes": int(p.stat().st_size)} for k, p in sorted(files.items())}}
    check_free(staging)
    (staging / "PUBLISHED.json").write_text(pdb.canon(published), encoding="utf-8")
    verify_publication(staging)
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, target)
    return "PUBLISHED"


def _filtered_sha(path, columns, role, start, stop):
    header = (",".join(columns) + "\n").encode()
    h, rows = hashlib.sha256(header), 0
    rep_i, role_i = columns.index("replicate"), columns.index("role") if "role" in columns and role else None
    with gzip.open(path, "rb") as fh:
        if fh.readline() != header:
            raise IncompleteWork(f"{path} has another header")
        for line in fh:
            if b'"' in line:
                raise IncompleteWork(f"{path} holds a quoted field")
            f = line.rstrip(b"\n").split(b",")
            if start <= int(f[rep_i]) < stop and (role_i is None or f[role_i].decode() == role):
                h.update(line)
                rows += 1
    return h.hexdigest(), rows


def _fair_bytes(df):
    with tempfile.TemporaryDirectory() as d:
        pipelines.save_fair_csv(df, Path(d) / "x.csv")
        return (Path(d) / "x.csv").read_bytes()


def _identity_problems(session):
    """Published session: canonical hash recomputed, publishable mode and space, seed plan, audit sources unchanged."""
    try:
        body = {k: v for k, v in session.items() if k != "session_id"}
        problems = [] if hashlib.sha256(pdb.canon(body).encode()).hexdigest() == session["session_id"] else [
            "session_id is not the SHA-256 of the canonical session body"]
        mode, cfg = session["mode"], session["config"]
        if mode not in ("full", "cost_fixture") or session["space"] != MODES[mode]:
            problems.append(f"mode {mode!r} and space {session['space']!r} are not a publishable pair")
        if (e4.validate_config(cfg) != cfg or session["domains"] != list(e4.DOMAINS)
                or session["seed_plan_sha256"] != e4.seed_plan(cfg)["sha256"]):
            problems.append("the configuration, seed domains or seed plan differ from the session")
        sources = set(e4.CODE_FILES) | {"experiments/e4_production.py"}
        if set(session["code"]) != sources or any(pdb.file_sha256(e4.REPO_ROOT / p) != h
                                                  for p, h in sorted(session["code"].items())):
            problems.append("the audit sources differ from the sources recorded in the session")
    except (KeyError, TypeError, ValueError, AttributeError, FileNotFoundError, NotADirectoryError) as exc:
        problems = [f"malformed session identity or missing audit source: {exc!r}"]
    return problems


def _coherence_problems(session, pub, manifest, lineage, plan, statuses):
    """Identity-bearing artifacts reconciled: PUBLISHED, manifest, plan, lineage, producer records and block map."""
    sid, mode, cfg = session["session_id"], session["mode"], session["config"]
    label = "COST_FIXTURE" if mode == "cost_fixture" else "E4_SCIENCE"
    problems = [f"{name} carries another session or mode" for name, doc in
                (("PUBLISHED.json", pub), ("manifest.json", manifest), ("campaign_plan.json", plan))
                if doc.get("session_id") != sid or doc.get("mode") != mode]
    if pub.get("label") != label or manifest.get("label") != label:
        problems.append(f"the publication labels differ from {label}")
    block = plan.get("block")
    if (lineage.get("session_id") != sid or lineage.get("block") != block or plan.get("counts") != role_counts(cfg)
            or plan.get("K") != len(plan_partitions(cfg, mode, block))):
        problems.append("the campaign plan or the lineage differs from the session geometry")
    expected = set(plan_partitions(cfg, mode, block, statuses)) - {"merge", "analysis"}
    records = lineage.get("partitions", {})
    if set(records) != expected:
        problems.append("the lineage producers differ from the planned partitions")
    problems += [f"lineage record {pid} is foreign" for pid, r in sorted(records.items())
                 if r.get("partition") != pid or r.get("session_id") != sid or r.get("status") != "COMPLETE"]
    cal = records.get("thresholds", {}).get("files", {}).get("calibration.csv")
    if any(r.get("objects", {}).get("calibration_csv_sha256") != cal for p, r in records.items() if p.startswith("trials_")):
        problems.append("a trial block was produced under another calibration")
    if {b["partition"] for b in lineage.get("blocks", [])} != {p for p in expected if p.startswith(("calmax_", "trials_"))}:
        problems.append("the block-to-fragment map differs from the planned blocks")
    return problems


def _published_activation_problems(t, session, act, plan):
    """Published activation: full session, references, exactly the four receipts with coherent normalized facts."""
    if not isinstance(act, dict) or set(act) != ACTIVATION_KEYS:
        return ["the published activation does not hold exactly the required keys"]
    problems = []
    if session["mode"] != "full" or act["session_id"] != session["session_id"] or act["seed_plan_sha256"] != session[
            "seed_plan_sha256"]:
        problems.append("the activation does not bind this full session")
    if (act["references"] != REFERENCE_SHA256 or act["go_full"].get("path") != GO_FULL_PATH
            or act["go_full"].get("sha256") != REFERENCE_SHA256[GO_FULL_PATH]):
        problems.append("the activation cites other reference sources")
    if set(act["receipts"]) != set(RECEIPT_KINDS):
        return problems + [f"published receipts {sorted(act['receipts'])} differ from {list(RECEIPT_KINDS)}"]
    cutoff, receipts = act["ledger"].get("cutoff") or "", {}
    for kind in RECEIPT_KINDS:
        path = t / "activation" / "receipts" / f"{kind}.json"
        if not path.is_file() or pdb.file_sha256(path) != act["receipts"][kind]["sha256"]:
            problems.append(f"the published {kind} receipt differs from the activation record")
            continue
        receipts[kind] = json.loads(path.read_text(encoding="utf-8"))
        problems += _receipt_fact_problems(kind, receipts[kind], session)
        if ((receipts[kind].get("ledger") or {}).get("cutoff") or "") > cutoff:
            problems.append(f"the {kind} receipt is later than the activation ledger")
    if not problems and receipts["pilot"]["p2"]["block"] != plan.get("block"):
        problems.append("the attested P2 block differs from the published campaign block")
    return problems + (_forecast_link_problems(act, receipts) if not problems else [])


def _forecast_link_problems(act, receipts):
    """The activation forecast is the very report the pilot and non-leak receipts attested."""
    problems = []
    for name, key in (("forecast.csv", "forecast"), ("partition_forecast.csv", "partition_forecast"),
                      (REPORT_MANIFEST, "manifest")):
        sha = act["forecast"][key]["sha256"]
        if (receipts["pilot"]["leaves"][name]["sha256"] != sha
                or receipts["nonleak"]["leaves"][f"report/{name}"]["sha256"] != sha):
            problems.append(f"the activation {name} is not the one attested by the pilot and non-leak receipts")
    return problems


def verify_publication(target, require_activation=False):
    """Standalone audit: identity recomputed, closed inventory, coherent artifacts, blocks rebuilt, calibrations."""
    t = Path(target)
    try:
        return _verify_publication(t, require_activation)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, FileNotFoundError, NotADirectoryError,
            IsADirectoryError) as exc:
        raise pdb.PartitionMismatch(f"{t}: malformed or incomplete publication: {exc!r}") from exc


def _verify_publication(t, require_activation):
    try:
        pub, session, manifest, lineage, plan = (json.loads((t / name).read_text(encoding="utf-8")) for name in (
            "PUBLISHED.json", "session.json", "manifest.json", "lineage.json", "campaign_plan.json"))
    except (OSError, ValueError) as exc:
        raise pdb.PartitionMismatch(f"{t} is not a readable publication") from exc
    problems = _identity_problems(session)
    if problems:
        raise pdb.PartitionMismatch(f"{t}: " + "; ".join(problems))
    files, dirs = _inventory(t)
    files.pop("PUBLISHED.json", None)
    declared = pub.get("files", {})
    cfg, mode = session["config"], session["mode"]
    allowed = set(_publication_sources_names(cfg, manifest)) | {"ledger/attempts.jsonl", "ledger/cpu_ledger.csv"}
    act = None
    if "activation/activation.json" in declared:
        act = json.loads((t / "activation" / "activation.json").read_text(encoding="utf-8"))
        allowed |= {"activation/activation.json"} | {f"activation/receipts/{k}.json" for k in act.get("receipts", {})}
    elif require_activation:
        raise IncompleteWork(f"{t} carries no activation record")
    if sorted(files) != sorted(declared) or set(declared) != allowed or dirs != _parents(declared):
        raise pdb.PartitionMismatch(f"{t}: the inventory is not the closed publication set of this session")
    for rel, fact in declared.items():
        if pdb.file_sha256(files[rel]) != fact["sha256"] or files[rel].stat().st_size != fact["bytes"]:
            raise pdb.PartitionMismatch(f"{t / rel} differs from PUBLISHED.json")
        if fact["bytes"] > FRAGMENT_ALERT_BYTES:
            raise IncompleteWork(f"{rel} exceeds the {FRAGMENT_ALERT_BYTES}-byte fragment ceiling")
    cells = read_table(t / "records" / "thresholds" / "cells.csv")
    statuses = {(r.background, int(r.N)): r.status for r in cells.itertuples()}
    problems = _coherence_problems(session, pub, manifest, lineage, plan, statuses)
    problems += [] if act is None else _published_activation_problems(t, session, act, plan)
    if problems:
        raise pdb.PartitionMismatch(f"{t}: " + "; ".join(problems))
    for table, info in manifest["tables"].items():
        for f in info["fragments"]:
            if stream_whole([t / f["file"]], TABLES[table]) != (f["sha256_csv"], f["rows"]):
                raise pdb.PartitionMismatch(f"{f['file']} differs from the manifest")
        if stream_whole([t / f["file"] for f in info["fragments"]], TABLES[table]) != (info["sha256_whole"],
                                                                                       info["rows"]):
            raise pdb.PartitionMismatch(f"table {table} differs from the manifest")
    for b in lineage["blocks"]:
        if _filtered_sha(t / b["fragment"], TABLES[b["table"]], b["role"], b["start"], b["stop"]) != (
                b["sha256_csv"], b["rows"]):
            raise pdb.PartitionMismatch(f"block {b['partition']} cannot be rebuilt from {b['fragment']}")
    small = {"scalar_cal": ["scalar_calibration.csv"], "thresholds": ["calibration.csv", "cells.csv"],
             **{pid_fit(*c): ["cell.csv"] for c in cells_of(cfg)}}
    for pid, names in small.items():
        for name in names:
            if lineage["partitions"][pid]["files"][name] != pdb.file_sha256(t / "records" / pid / name):
                raise pdb.PartitionMismatch(f"records/{pid}/{name} differs from its partition record")
    maxima = {c: indexed_maxima([("calibration_maxima", 0, cfg["n_cal"],
                                  read_table(t / f"calibration_maxima/{c[0]}_N{c[1]}.csv.gz"))],
                                *c, cfg["n_cal"], "OK") for c, s in statuses.items() if s == "OK"}
    scalar = _scalar_fields(cfg, mode)
    if _fair_bytes(pd.DataFrame([scalar], columns=SCALAR_FIELDS)) != (t / "records/scalar_cal/scalar_calibration.csv"
                                                                     ).read_bytes():
        raise pdb.PartitionMismatch("the regenerated scalar calibration differs from the published row")
    if _fair_bytes(calibration_table(cfg, statuses, scalar, maxima)) != (t / "records/thresholds/calibration.csv"
                                                                        ).read_bytes():
        raise pdb.PartitionMismatch("calibrations recomputed from the published maxima differ from calibration.csv")
    return {"files": len(declared), "blocks": len(lineage["blocks"]), "calibrations_recomputed": 3 * len(maxima),
            "activation": "activation/activation.json" in declared}


def _publication_sources_names(cfg, manifest):
    names = {"session.json", "campaign_plan.json", "manifest.json", "lineage.json",
             "records/scalar_cal/scalar_calibration.csv", "records/thresholds/calibration.csv",
             "records/thresholds/cells.csv"}
    names |= {f"records/{pid_fit(*c)}/cell.csv" for c in cells_of(cfg)}
    names |= {f["file"] for tab in manifest["tables"].values() for f in tab["fragments"]}
    return names | {f"analysis/{name}" for name in ANALYSIS_FILES}


REFERENCE_CONFIG_SHA256 = "5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2"
REFERENCE_SHA256 = {"configs/e4_alignment.yaml": REFERENCE_CONFIG_SHA256,
                    "experiments/e4_alignment.py": "e457ebae9011a5f1d1b0b9bc43d38f2ab97a70bccd64069dba07ad51996efd01",
                    "docs/audits/stream_19_protocol_proposal_20261112.md":
                        "cd786a02d5d6407ccf9a88ba91cacce50c7dcc0f45655868bb32643c577ec657",
                    "prompts/GO-stream-19-e4-full-20261112.md":
                        "19d2697700bc9a0af5d98c9bd7c901129450aed385487582ef67c3f17e094746"}
PROTOTYPE_TESTS = 101
RECEIPT_KINDS = ("tests", "make_check", "pilot", "nonleak")
REQUIRED_TESTS = (
    "test_block_ranges_cover_exactly", "test_pid_parser_refuses_unsafe_ids",
    "test_plan_counts_cover_354_and_690_when_every_fit_is_ok",
    "test_identity_separates_mode_and_space_and_excludes_geometry",
    "test_nested_partition_writer_records_relative_paths_and_resumes",
    "test_nested_partition_writer_refuses_a_symlink_produced_by_compute",
    "test_fair_fragments_are_canonical_and_gzip_deterministic", "test_tiles_require_the_exact_planned_ranges",
    "test_production_matches_prototype_bytes", "test_logical_outputs_invariant_to_geometry_order_and_processes",
    "test_maxima_fragment_is_sorted_by_method_and_replicate", "test_refused_basis_cell_matches_prototype",
    "test_resume_skips_complete_without_recompute", "test_tiling_refuses_holes_overlaps_and_foreign_blocks",
    "test_last_replicate_block_is_required", "test_divergences_are_refused_without_mutation",
    "test_threshold_barrier_blocks_monitoring", "test_calmax_of_a_refused_cell_is_refused",
    "test_axes_are_streamed_and_each_replicate_has_n_axes", "test_trial_coverage_follows_cells_and_calibration",
    "test_scientific_route_reads_no_data_file", "test_plan_cli_prints_only_k_and_next_ends_with_code_10",
    "test_full_mode_is_refused_without_activation", "test_attempt_ledger_is_append_only_and_stops_on_unknown",
    "test_gate_budget_disk_and_previous_exit", "test_enospc_never_completes",
    "test_fixture_interrupt_leaves_tmp_and_recomputes", "test_cost_fixture_runs_every_phase_with_full_counts",
    "test_cost_kernels_stay_outside_science", "test_publication_is_closed_verified_and_atomic",
    "test_mixed_publication_is_auditable_without_the_work_root", "test_identity_stamp",
    "test_tests_receipt_requires_stamp_coverage_and_success", "test_make_check_receipt_reads_pytest_summaries",
    "test_required_tests_list_every_test_of_the_module", "test_forecast_and_pilot_receipt_from_a_measured_pilot",
    "test_activation_requires_bound_receipts", "test_accounting_receipt_links_the_publication_and_the_final_ledger",
    "test_make_check_partial_log_is_refused", "test_published_activation_requires_four_normalized_receipts",
    "test_published_seed_tamper_is_refused", "test_publication_identity_is_recomputed_and_reconciled",
    "test_forecast_partition_sum_is_reconciled", "test_forecast_reconciles_partitions_geometry_controls_and_counts",
    "test_evidence_cost_problems_bound_the_control_overhead", "test_imported_costs_keep_provenance",
    "test_driver_campaign_with_a_stub_producer", "test_import_record_cpu_must_match_its_hashed_source",
    "test_later_import_preserves_frozen_activation", "test_pilot_normalized_p2_count_is_checked",
    "test_import_facts_and_frozen_membership")
MAKE_CHECK_SUITES = ("pytest -q --ignore=external tests/test_contracts.py tests/test_decoupling.py",
                     "pytest -q --ignore=external --ignore=tests/test_contracts.py --ignore=tests/test_decoupling.py")
APPROVED_SKIP = re.compile(r"tests/test_chars\.py:[0-9]+: D4 is not built in this tree|"
                           r"tests/test_data_eurofidai\.py:[0-9]+: D4 not built; EUROFIDAI data must be exported first .*")
_OUTCOME = r"(?:passed|failed|errors?|skipped|deselected|xfailed|xpassed|warnings?)"
_SUMMARY = re.compile(rf"(?:=+ )?((?:[0-9]+ {_OUTCOME}(?:, )?)+) in [0-9.]+s(?: \([0-9:.]+\))?(?: =+)?")
_COUNT = re.compile(r"([0-9]+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed|warnings?)")
_SKIP_LINE = re.compile(r"SKIPPED \[([0-9]+)\] (.+)")


def parse_junit(path):
    """Suite properties and testcase outcomes (passed, failure, error, skipped) of a pytest JUnit XML file."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ActivationRefused(f"unreadable JUnit file {path}") from exc
    props = {p.get("name"): p.get("value") for p in root.iter("property")}
    cases = {f"{c.get('classname')}::{c.get('name')}": next(
        (tag for tag in ("failure", "error", "skipped") if c.find(tag) is not None), "passed")
        for c in root.iter("testcase")}
    return props, cases


def _tests_facts(junit_path):
    props, cases = parse_junit(junit_path)
    suites = ("tests.test_e4_production", "tests.test_e4_alignment")
    return {"stamp": props.get("e4_session_id"),
            "required_passed": sorted(n for n in REQUIRED_TESTS if cases.get(f"tests.test_e4_production::{n}") == "passed"),
            "prototype_passed": sum(1 for k, v in cases.items() if k.startswith("tests.test_e4_alignment::")
                                    and v == "passed"),
            "not_passed": sorted(k for k, v in cases.items() if v != "passed" and k.split("::")[0] in suites),
            "cases": len(cases)}


def _tests_fact_problems(facts, exit_code, session_id):
    problems = [] if exit_code == 0 else [f"pytest exit code {exit_code}"]
    if facts.get("stamp") != session_id:
        problems.append("the JUnit identity stamp is absent or stale")
    if facts.get("not_passed"):
        problems.append(f"not passed: {facts['not_passed'][:5]}")
    missing = sorted(set(REQUIRED_TESTS) - set(facts.get("required_passed") or ()))
    problems += [f"required tests absent or not passed: {missing[:5]}"] if missing else []
    if facts.get("prototype_passed") != PROTOTYPE_TESTS:
        problems.append(f"{facts.get('prototype_passed')} prototype tests passed, expected {PROTOTYPE_TESTS}")
    return problems


def _tests_problems(identity, junit_path, exit_code):
    facts = _tests_facts(junit_path)
    return _tests_fact_problems(facts, exit_code, identity["session_id"]), facts


def receipt_tests(identity, junit_path, log_path, command, exit_code):
    """Tests receipt with normalized facts bound to the JUnit identity stamp, coverage and success."""
    problems, facts = _tests_problems(identity, junit_path, exit_code)
    if problems:
        raise ActivationRefused("; ".join(problems))
    return {"kind": "tests", "session_id": identity["session_id"], "command": command, "exit_code": exit_code,
            "leaves": {"junit": _leaf(junit_path), "log": _leaf(log_path)}, "facts": facts}


def _make_check_facts(log_path):
    lines = [x.strip() for x in Path(log_path).read_text(encoding="utf-8").splitlines()]
    starts = [lines.index(cmd) if cmd in lines else None for cmd in MAKE_CHECK_SUITES]
    if None in starts or starts != sorted(starts):
        return []
    suites = []
    for cmd, a, b in zip(MAKE_CHECK_SUITES, starts, starts[1:] + [len(lines)]):
        found = [m.group(1) for m in map(_SUMMARY.fullmatch, lines[a + 1:b]) if m]
        counts = {k.rstrip("s") if k in ("errors", "warnings") else k: int(n)
                  for n, k in _COUNT.findall(found[-1])} if found else {}
        skips = [[int(m.group(1)), m.group(2)] for m in map(_SKIP_LINE.fullmatch, lines[a + 1:b]) if m]
        suites.append({"command": cmd, "summaries": len(found), "counts": counts, "skips": skips})
    return suites


def _suites_problems(suites, exit_code):
    """Approved make check policy on normalized facts: both suites, one clean summary each, only the D4 skips."""
    problems = [] if exit_code == 0 else [f"make check exit code {exit_code}"]
    if [s.get("command") for s in suites] != list(MAKE_CHECK_SUITES):
        return problems + ["the log does not hold both Makefile pytest suites in order"]
    for k, s in enumerate(suites, 1):
        counts, skips = s["counts"], s["skips"]
        if s["summaries"] != 1 or counts.get("passed", 0) < 1 or any(
                counts.get(x, 0) for x in ("failed", "error", "deselected", "xpassed")):
            problems.append(f"suite {k} summary {counts} is partial or not clean")
        if sum(n for n, _ in skips) != counts.get("skipped", 0):
            problems.append(f"suite {k}: {counts.get('skipped', 0)} skips but {len(skips)} listed reasons (-rs)")
        if k == 1 and (skips or counts.get("skipped", 0)):
            problems.append("the contract suite skipped tests: the torch guards must run")
        problems += [f"unapproved skip {reason}" for _, reason in skips if not APPROVED_SKIP.fullmatch(reason)]
    return problems


def _make_check_problems(log_path, exit_code):
    suites = _make_check_facts(log_path)
    return _suites_problems(suites, exit_code), suites


def receipt_make_check(identity, log_path, command, exit_code):
    """make check receipt: both Makefile suites clean, skips limited to the approved D4 absences (normalized facts)."""
    problems, suites = _make_check_problems(log_path, exit_code)
    if problems:
        raise ActivationRefused("; ".join(problems))
    return {"kind": "make_check", "session_id": identity["session_id"], "command": command, "exit_code": exit_code,
            "leaves": {"log": _leaf(log_path)}, "facts": {"suites": suites}}


def _pilot_fact_problems(receipt, session):
    expected = {f"cost_{bg}_N{N}_{r}" for bg, N in P1_CELLS for r in COST_ROLES}
    problems = []
    if receipt["p1"]["session_id"] != sibling_identity(session, "production_pilot")["session_id"] or receipt["p2"][
            "session_id"] != sibling_identity(session, "cost_fixture")["session_id"]:
        problems.append("stale pilot identities")
    if (set(receipt["p1"]["partitions"]) != expected or receipt["p1_attempts"] != len(expected)
            or len(set(receipt["p1"]["attempts"])) != len(expected)):
        problems.append("P1 coverage differs from the declared cells and roles")
    if (len(set(receipt["replays"])) < 3 or not receipt["interruption"]["recompute_attempts"]
            or not receipt["interruption"]["leftovers"]):
        problems.append("replays or interruption recompute missing")
    p2 = receipt["p2"]
    if p2["partitions"] != len(plan_partitions(session["config"], "cost_fixture", e4._integer(p2["block"], "block", 1))):
        problems.append("the P2 partition count differs from the complete fixture campaign at its attested block")
    if not isinstance(p2["publication"], str) or not re.fullmatch(r"[0-9a-f]{64}", p2["publication"]):
        problems.append("the P2 publication reference is not a SHA-256")
    return problems


def _nonleak_fact_problems(receipt):
    expected = {f"report/{n}" for n in REPORT_FILES + (REPORT_MANIFEST,)} | {
        f"p1/cost_{bg}_N{N}_{r}/cost.csv" for bg, N in P1_CELLS for r in COST_ROLES}
    problems = [] if set(receipt.get("leaves", {})) == expected else ["the non-leak inventory is not the closed set"]
    return problems + ([] if receipt.get("p2_label") == "COST_FIXTURE" else ["the P2 campaign is not COST_FIXTURE"])


def _receipt_fact_problems(kind, receipt, session):
    """Normalized receipt facts, checkable without raw leaves: kind, identity, success, test and pilot coverage."""
    if not isinstance(receipt, dict) or receipt.get("kind") != kind or receipt.get("session_id") != session["session_id"]:
        return [f"{kind} receipt is foreign or stale"]
    try:
        if kind == "tests":
            return _tests_fact_problems(receipt["facts"], receipt["exit_code"], session["session_id"])
        if kind == "make_check":
            return _suites_problems(receipt["facts"]["suites"], receipt["exit_code"])
        if kind == "pilot":
            return _pilot_fact_problems(receipt, session)
        if kind == "nonleak":
            return _nonleak_fact_problems(receipt)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        return [f"{kind} receipt facts are malformed: {exc!r}"]
    return [f"unknown receipt kind {kind}"]


def validate_receipt(kind, receipt, identity, attempts_dir=None):
    """Receipt re-verified against the current identity, its normalized facts, its leaf hashes and re-parsed leaves."""
    problems = _receipt_fact_problems(kind, receipt, identity)
    if problems:
        raise ActivationRefused(f"{kind} receipt: " + "; ".join(problems))
    for leaf in receipt.get("leaves", {}).values():
        _check_leaf(leaf)
    if kind == "tests":
        problems, facts = _tests_problems(identity, receipt["leaves"]["junit"]["path"], receipt["exit_code"])
        problems += [] if facts == receipt["facts"] else ["the tests facts differ from the JUnit file"]
    elif kind == "make_check":
        problems, suites = _make_check_problems(receipt["leaves"]["log"]["path"], receipt["exit_code"])
        problems += [] if suites == receipt["facts"]["suites"] else ["the make check facts differ from the log"]
    else:
        problems = RECEIPT_CHECKS[kind](receipt, identity, attempts_dir)
    if attempts_dir is not None and "ledger" in receipt:
        try:
            check_snapshot(attempts_dir, receipt["ledger"])
        except GateStop as exc:
            problems = problems + [str(exc)]
    if problems:
        raise ActivationRefused(f"{kind} receipt: " + "; ".join(problems))


ACTIVATION_KEYS = {"session_id", "seed_plan_sha256", "go_full", "technical_go", "references", "receipts", "forecast",
                   "evidence_cost", "disk", "ledger", "command"}


GO_FULL_PATH = "prompts/GO-stream-19-e4-full-20261112.md"
P1_CELLS = (("gaussian", 8), ("gaussian", 500), ("t7", 500))
PATH_STAGE_KINDS = ("draw", "stream", "logpath", "paths", "readings", "oracle_diagnostics", "j_k_table")
REPORT_LABEL = "COST_ONLY_NOT_SCIENTIFIC_E4"
REPORT_MANIFEST = "MANIFEST.json"
REPORT_FILES = ("attempts.jsonl", "cost_sources.csv", "stage_costs.csv", "volumes.csv", "forecast.csv",
                "partition_forecast.csv", "unmeasured.csv")
ATTEMPT_KEYS = ("attempt_id", "state", "command", "user_s", "system_s", "wall_s", "max_rss_kib", "time_status", "exit",
                "intended_interrupt", "result", "files_sha256")
VOLUME_COLUMNS = ["item", "kind", "final_bytes", "final_label", "tmp_bound_bytes", "tmp_bound_basis", "tmp_peak_status"]
TMP_BOUND_BASES = {"DERIVED_FINAL_PLUS_LARGEST_PLAIN_CSV", "DERIVED_FINAL_PLUS_LARGEST_MERGED_PLAIN_CSV",
                   "DERIVED_DIRECT_WRITE", "DERIVED_EXISTING_BYTES", "DERIVED_STAGING_RENAMED"}
FORECAST_COLUMNS = ["session_id", "scenario", "block", "n_partitions", "cutoff", "consumed_cpu_s", "projected_cpu_s",
                    "reserve_cpu_s", "total_cpu_s", "cap_cpu_s", "control_bound_s", "projected_bytes", "status"]
PARTITION_FORECAST_COLUMNS = ["partition", "cpu_s", "projected_bytes", "projected_tmp_bytes", "projected_tmp_basis",
                              "basis"]
PROJECTED_TMP_BASES = {"DERIVED_LARGEST_PLAIN_CSV", "DERIVED_LARGEST_MERGED_PLAIN_CSV", "DERIVED_DIRECT_WRITE",
                       "PHASE_COVERED_BY_ACTIVATION_FOOTPRINT"}
UNMEASURED_COLUMNS = ["item", "assumption", "status"]
UNMEASURED = (("per_path_linear", "per-path CPU of a role scales linearly with the replicates of a block"),
              ("fixture_overhead_transfer", "the cost_fixture invocation CPU of a partition stands for its startup, "
                                            "identity, dependency checks, serialization and hashing in full mode"),
              ("interruption_reserve", "three of the largest blocks are reserved for interrupted recomputation"),
              ("supervision_margin", "the 1800 CPU s next-invocation envelope includes the host supervision margin"),
              ("git_objects", "Git object storage equals the published bytes; no Git operation is measured"),
              ("control_bound", "every full invocation's evidence re-check, pending-cost read and ledger read stay "
                                "below the declared bound, confirmed before activation on a technical candidate"),
              ("evidence_cost_self_check", "reading the evidence-cost table itself is outside its own measurement"),
              ("accounting_transfer", "the final accounting receipt costs at most the measured cost_fixture plan call"),
              ("projected_volumes", "full partition bytes equal the measured cost_fixture partition bytes"),
              ("transient_peaks", "transient disk peaks are not observed; bounds derived from recorded plain CSV sizes "
                                  "stand for them"))
PHASE_ROWS = ("phase:plan", "phase:next-done", "phase:verify", "phase:publish", "phase:verify-publication",
              "phase:receipt-accounting")
SCALAR_PRODUCTION = "scalar_cal"
SCALAR_AUDITS = ("phase:publish", "phase:verify-publication")
INTERRUPTION_RESERVE_BLOCKS = 3
SCENARIOS = {"FULL_GRID": lambda c, t7: True, "DROP_N500": lambda c, t7: c[1] != 500,
             "T7_ON_8_64_239": lambda c, t7: c[1] != 500 and (c[0] not in t7 or c[1] in (8, 64, 239))}
EVIDENCE_STAGES = ("evidence_check", "pending_costs", "ledger_volume")
EVIDENCE_COLUMNS = ["session_id", "stage", "n_attempts", "cpu_s", "wall_s", "status", "label"]
EVIDENCE_LABEL = "TECHNICAL_CANDIDATE_NOT_ACTIVATION"


def sibling_identity(identity, mode):
    """The identity of another mode of the same configuration, code, environment and seed plan."""
    body = {k: v for k, v in identity.items() if k != "session_id"}
    body.update(mode=mode, space=MODES[mode])
    return {"session_id": hashlib.sha256(pdb.canon(body).encode()).hexdigest(), **body}


def consumed_through(attempts_dir, cutoff, imports, prior_cpu_s=PRIOR_CPU_S):
    """Prior CPU, the unchanged imports of a frozen snapshot and every finalized attempt up to its cutoff (included)."""
    d = Path(attempts_dir)
    rows = [read_attempt(e) for e in (sorted(d.iterdir()) if d.is_dir() else ()) if cutoff not in (None, "NONE")
            and e.name <= cutoff]
    if any(a["state"] != "MEASURED" for a in rows):
        raise GateStop(f"an attempt up to {cutoff} is not finalized")
    current = {r["import_id"]: r for r in read_imports(attempts_dir)}
    if any(current.get(i["import_id"], {}).get("record_sha256") != i["sha256"] for i in imports):
        raise GateStop("an import of the frozen snapshot changed or disappeared")
    return _consumed(prior_cpu_s, [current[i["import_id"]] for i in imports], rows)


def _per_path(rows, replicates):
    out = {}
    for r in rows.itertuples():
        kind, role = r.stage.split(":")[0], r.stage.rsplit(":", 1)[-1]
        role = "alternative" if kind in ("oracle_diagnostics", "j_k_table") else role
        if kind in PATH_STAGE_KINDS and role in COST_ROLES:
            out[role] = out.get(role, 0.0) + float(r.cpu_s) / replicates
    return out


def _dir_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())


def _scenario_rows(cfg, partitions, name):
    t7 = {bg for bg, nu in cfg["backgrounds"].items() if nu is not None}
    return [p for p in partitions if p.startswith("phase:") or "_N" not in p or SCENARIOS[name](_cell_of(p), t7)]


def _reserve(per):
    blocks = per[per["partition"].str.startswith(("calmax_", "trials_"))]["cpu_s"]
    return INTERRUPTION_RESERVE_BLOCKS * float(blocks.max()) if len(blocks) else 0.0


def _tmp_extras(cfg, p2_root, p2_id, block):
    """Derived transient bytes beyond the final ones: largest plain CSV of a block, or of a merged per-cell table."""
    out, merged = {}, {}
    for pid in plan_partitions(cfg, "cost_fixture", block, fit_statuses(cfg, p2_root, p2_id)):
        tables = load_partition(p2_root, pid, p2_id)["objects"].get("tables", {})
        if pid.startswith(("calmax_", "trials_")):
            out[pid] = (max(t["bytes_csv"] for t in tables.values()), "LARGEST_PLAIN_CSV")
            for name, fact in tables.items():
                if name != "axes.csv.gz":
                    key = (_cell_of(pid), name)
                    merged[key] = merged.get(key, 0) + fact["bytes_csv"]
        elif pid != "merge":
            out[pid] = (0, "DIRECT_WRITE")
    out["merge"] = (max(merged.values(), default=0), "LARGEST_MERGED_PLAIN_CSV")
    return out


def _p2_volumes(cfg, p2_root, p2_id, block, publication):
    rows, part, extras = [], Path(p2_root) / "partitions", _tmp_extras(cfg, p2_root, p2_id, block)
    for pid in plan_partitions(cfg, "cost_fixture", block, fit_statuses(cfg, p2_root, p2_id)):
        final, (extra, basis) = _dir_bytes(part / pid), extras[pid]
        basis = "DERIVED_DIRECT_WRITE" if basis == "DIRECT_WRITE" else f"DERIVED_FINAL_PLUS_{basis}"
        rows.append({"item": pid, "kind": "partition", "final_bytes": final, "tmp_bound_bytes": final + extra,
                     "tmp_bound_basis": basis})
    left, pub = sum(_dir_bytes(p) for p in part.glob("*.tmp-*")), _dir_bytes(publication)
    rows += [{"item": "leftovers", "kind": "leftover", "final_bytes": left, "tmp_bound_bytes": left,
              "tmp_bound_basis": "DERIVED_EXISTING_BYTES"},
             {"item": "publication", "kind": "publication", "final_bytes": pub, "tmp_bound_bytes": pub,
              "tmp_bound_basis": "DERIVED_STAGING_RENAMED"}]
    df = pd.DataFrame(rows, columns=VOLUME_COLUMNS)
    return df.assign(final_label="MEASURED_FINAL_BYTES", tmp_peak_status="NOT_OBSERVED")


def forecast_production(cfg, identity, block, p1_root, p2_root, prior_costs, attempts_dir, publication,
                        control_bound_s, active=None):
    """ESTIMATE per planned full invocation and scenario, with the measured pilot report tables (closed set)."""
    bound = float(control_bound_s)
    if not math.isfinite(bound) or bound <= 0:
        raise ValueError("--control-bound-s must be a positive finite CPU bound per full invocation")
    prior, pilot_n = read_table(prior_costs), cfg["pilot_n"]
    per_path, fit = {}, {}
    for bg, N in cells_of(cfg):
        rows = prior[prior["partition"] == f"{bg}:{N}"]
        if rows.empty:
            raise IncompleteWork(f"no prior cost rows for {bg}:{N}")
        per_path[(bg, N)] = _per_path(rows, pilot_n)
        fit[(bg, N)] = float(rows.loc[rows["stage"] == "fit_cell", "cpu_s"].sum())
    p1_id = sibling_identity(identity, "production_pilot")
    stage_tables = []
    for bg, N in P1_CELLS:
        for role in COST_ROLES:
            pid = f"cost_{bg}_N{N}_{role}"
            record = verify_partition(Path(p1_root) / "partitions" / pid, pid, p1_id)
            table = read_table(Path(p1_root) / "partitions" / pid / "cost.csv")
            stage_tables.append(table)
            measured = _per_path(table, record["objects"]["replicates"]).get(role, 0.0)
            per_path[(bg, N)][role] = max(per_path[(bg, N)].get(role, 0.0), measured)
            fit[(bg, N)] = max(fit[(bg, N)], float(table.loc[table["stage"] == "fit_cell", "cpu_s"].sum()))
    p2_id = sibling_identity(identity, "cost_fixture")
    if read_plan(p2_root, p2_id)["block"] != block:
        raise IncompleteWork("the cost_fixture pilot used another block geometry")
    verify_campaign(cfg, "cost_fixture", p2_root, p2_id)
    verify_publication(publication)
    led = ledger(attempts_dir, active)
    p2_cpu, measured_ends = {}, {(0, "COMPLETE"), (0, "PLANNED"), (10, "DONE"), (0, "VERIFIED"), (0, "PUBLISHED")}
    for a in led["attempts"]:
        r = a["result"] or {}
        if r.get("mode") == "cost_fixture" and (a["exit"], r.get("status")) in measured_ends:
            key = (r.get("partition") if r["status"] == "COMPLETE" else "phase:next-done" if r["status"] == "DONE"
                   else f"phase:{r.get('phase')}")
            p2_cpu[key] = max(p2_cpu.get(key, 0.0), a["user_s"] + a["system_s"])
    if "phase:plan" in p2_cpu:
        p2_cpu["phase:receipt-accounting"] = p2_cpu["phase:plan"]
    scalar_cost = float(prior.loc[prior["stage"] == "scalar_cal", "cpu_s"].sum()) * cfg["n_cal"] / pilot_n
    extras, rows = _tmp_extras(cfg, p2_root, p2_id, block), []
    for pid in plan_partitions(cfg, "full", block) + list(PHASE_ROWS):
        if pid not in p2_cpu:
            raise IncompleteWork(f"no measured cost_fixture attempt for {pid}")
        info = {"kind": "phase"} if pid.startswith("phase:") else parse_pid(pid, cfg, "full", block)
        cpu, basis = p2_cpu[pid], ["fixture_plan_transfer" if pid == "phase:receipt-accounting" else "fixture"]
        if pid == SCALAR_PRODUCTION or pid in SCALAR_AUDITS:
            cpu += scalar_cost
            basis += ["scalar_production" if pid == SCALAR_PRODUCTION else "scalar_audit"]
        if info["kind"] == "fit":
            cpu, basis = cpu + fit[(info["background"], info["N"])], basis + ["fit"]
        elif info["kind"] in ("calmax", "trials"):
            c = (info["background"], info["N"])
            cpu += fit[c] + per_path[c].get(info["role"], 0.0) * (info["stop"] - info["start"])
            basis += ["fit", "per_path"]
        part = Path(p2_root) / "partitions" / pid
        extra, tmp_basis = extras.get(pid, (0, "PHASE_COVERED_BY_ACTIVATION_FOOTPRINT"))
        rows.append({"partition": pid, "cpu_s": cpu + bound, "projected_bytes": _dir_bytes(part) if part.is_dir() else 0,
                     "projected_tmp_bytes": extra, "projected_tmp_basis": tmp_basis if tmp_basis.startswith("PHASE")
                     else f"DERIVED_{tmp_basis}", "basis": "+".join(basis + ["control_bound"])})
    per = pd.DataFrame(rows, columns=PARTITION_FORECAST_COLUMNS)
    reserve, cost = _reserve(per), dict(zip(per["partition"], per["cpu_s"]))
    size = dict(zip(per["partition"], per["projected_bytes"]))
    scenarios = []
    for name in SCENARIOS:
        sel = _scenario_rows(cfg, list(per["partition"]), name)
        projected = math.fsum(cost[p] for p in sel)
        total = led["consumed_cpu_s"] + projected + reserve
        scenarios.append({"session_id": identity["session_id"], "scenario": name, "block": block,
                          "n_partitions": len(sel), "cutoff": led["snapshot"]["cutoff"] or "NONE",
                          "consumed_cpu_s": led["consumed_cpu_s"], "projected_cpu_s": projected,
                          "reserve_cpu_s": reserve, "total_cpu_s": total, "cap_cpu_s": CPU_CAP_S,
                          "control_bound_s": bound, "projected_bytes": int(sum(int(size[p]) for p in sel)),
                          "status": "WITHIN_CAP" if total <= CPU_CAP_S else "OVER_CAP"})
    unmeasured = pd.DataFrame([{"item": k, "assumption": v, "status": "UNMEASURED_ASSUMPTION"} for k, v in UNMEASURED],
                              columns=UNMEASURED_COLUMNS)
    tables = {"cost_sources.csv": cost_sources(led), "stage_costs.csv": pd.concat(stage_tables, ignore_index=True),
              "volumes.csv": _p2_volumes(cfg, p2_root, p2_id, block, publication),
              "forecast.csv": pd.DataFrame(scenarios, columns=FORECAST_COLUMNS), "partition_forecast.csv": per,
              "unmeasured.csv": unmeasured}
    return tables, led


def _cell_of(pid):
    match = re.match(rf"[a-z]+_{_BG}_{_N}", pid)
    return match.group(1), int(match.group(2))


def _write_new_dir(out, tables, finish=None):
    out = Path(out)
    if out.exists():
        raise pdb.PartitionMismatch(f"{out} already exists; reports are immutable")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"{out.name}.tmp-", dir=out.parent))
    for name, df in tables.items():
        check_free(tmp)
        pipelines.save_fair_csv(df, tmp / name)
    if finish is not None:
        finish(tmp)
    os.replace(tmp, out)


def write_report(out, tables, led, identity):
    """Pilot report: FAIR tables, lossless attempts.jsonl, then MANIFEST.json (frozen ledger snapshot) last."""
    attempts = led["attempts"]

    def finish(tmp):
        check_free(tmp)
        (tmp / "attempts.jsonl").write_text("".join(pdb.canon(a) + "\n" for a in attempts), encoding="utf-8")
        files = {n: {"sha256": pdb.file_sha256(tmp / n), "bytes": int((tmp / n).stat().st_size),
                     "rows": int(len(tables[n])) if n in tables else len(attempts),
                     "columns": list(tables[n].columns) if n in tables else None} for n in REPORT_FILES}
        (tmp / REPORT_MANIFEST).write_text(pdb.canon({"label": REPORT_LABEL, "session_id": identity["session_id"],
                                                      "ledger": led["snapshot"], "files": files}), encoding="utf-8")
    _write_new_dir(out, tables, finish)


REPORT_COLUMNS = {"cost_sources.csv": COST_SOURCE_COLUMNS, "stage_costs.csv": e4.COST_COLUMNS,
                  "volumes.csv": VOLUME_COLUMNS, "forecast.csv": FORECAST_COLUMNS,
                  "partition_forecast.csv": PARTITION_FORECAST_COLUMNS, "unmeasured.csv": UNMEASURED_COLUMNS}


def _report_problems(report_dir):
    """Closed pilot report: exact file set, manifest hashes, closed schemas, lossless attempts, cost-only stages."""
    report = Path(report_dir)
    try:
        manifest = json.loads((report / REPORT_MANIFEST).read_text(encoding="utf-8"))
        names = {p.name for p in report.iterdir()}
        problems = [] if names == set(REPORT_FILES) | {REPORT_MANIFEST} else [f"report files {sorted(names)} are foreign"]
        if manifest.get("label") != REPORT_LABEL or set(manifest.get("files", {})) != set(REPORT_FILES):
            problems.append("the report manifest is not the closed cost-only set")
        problems += [f"{n} differs from the report manifest" for n, fact in sorted(manifest["files"].items())
                     if pdb.file_sha256(report / n) != fact["sha256"]]
        for name, cols in REPORT_COLUMNS.items():
            df = read_table(report / name)
            if list(df.columns) != cols:
                problems.append(f"{name} has foreign columns")
            elif name in ("cost_sources.csv", "volumes.csv", "stage_costs.csv"):
                values = df[["cpu_s"] if name != "volumes.csv" else ["final_bytes", "tmp_bound_bytes"]].to_numpy(
                    dtype=np.float64)
                problems += [] if np.isfinite(values).all() and (values >= 0).all() else [f"{name} has invalid values"]
        volumes = read_table(report / "volumes.csv")
        if (set(volumes["final_label"]) != {"MEASURED_FINAL_BYTES"} or set(volumes["tmp_peak_status"]) != {"NOT_OBSERVED"}
                or not set(volumes["tmp_bound_basis"]) <= TMP_BOUND_BASES
                or (volumes["tmp_bound_bytes"] < volumes["final_bytes"]).any()):
            problems.append("volumes.csv mixes measured bytes, derived bounds and unobserved peaks")
        if (manifest["ledger"]["cutoff"] or "NONE") != str(read_table(report / "forecast.csv")["cutoff"].iloc[0]):
            problems.append("the report manifest ledger cutoff differs from the forecast cutoff")
        stages = read_table(report / "stage_costs.csv")
        if set(stages["status"]) != {"COMPLETE"} or not all(re.fullmatch(COST_STAGE_RE, s) for s in stages["stage"]):
            problems.append("stage_costs.csv is not a closed cost table")
        lines = [json.loads(x) for x in (report / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        if any(set(a) != set(ATTEMPT_KEYS) or a["state"] != "MEASURED" for a in lines):
            problems.append("attempts.jsonl is not the lossless finalized attempt ledger")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [f"unreadable pilot report: {exc!r}"]
    return problems


def _forecast_problems(report_dir, identity):
    """Forecast reconciled: closed scenarios, exact partition and control rows, counts, sums, reserve, cap, status."""
    report = Path(report_dir)
    try:
        f, per, un = (read_table(report / n) for n in ("forecast.csv", "partition_forecast.csv", "unmeasured.csv"))
    except (OSError, ValueError) as exc:
        return [f"unreadable forecast tables: {exc}"]
    problems = [f"forecast table columns {list(df.columns)} differ from {cols}" for df, cols in (
        (f, FORECAST_COLUMNS), (per, PARTITION_FORECAST_COLUMNS), (un, UNMEASURED_COLUMNS)) if list(df.columns) != cols]
    if problems:
        return problems
    for df in (f, per):
        numbers = df.select_dtypes("number").to_numpy(dtype=np.float64)
        if numbers.size and (not np.isfinite(numbers).all() or (numbers < 0).any()):
            problems.append("forecast values are not finite and non-negative")
    if (f["session_id"] != identity["session_id"]).any():
        problems.append("the forecast belongs to another identity")
    if sorted(f["scenario"]) != sorted(SCENARIOS) or any(f[c].nunique() != 1 for c in (
            "block", "cutoff", "consumed_cpu_s", "control_bound_s")):
        return problems + ["the scenarios, block, cutoff, consumed CPU or control bound are not one closed set"]
    if (f["cap_cpu_s"] != CPU_CAP_S).any():
        problems.append(f"the CPU cap differs from {CPU_CAP_S} s")
    if sorted(un["item"]) != sorted(k for k, _ in UNMEASURED):
        problems.append("the unmeasured assumptions are not the declared set")
    try:
        cfg = identity["config"]
        planned = plan_partitions(cfg, "full", e4._integer(f["block"].iloc[0], "block", 1)) + list(PHASE_ROWS)
    except (ValueError, TypeError, KeyError) as exc:
        return problems + [f"forecast geometry refused: {exc}"]
    names = list(per["partition"])
    if len(names) != len(set(names)) or set(names) != set(planned):
        return problems + ["the partition forecast is not exactly the planned partitions and control rows"]
    bound = float(f["control_bound_s"].iloc[0])
    if bound <= 0 or (per["cpu_s"] < bound).any():
        problems.append("a forecast row does not carry the per-invocation control bound")
    if not set(per["projected_tmp_basis"]) <= PROJECTED_TMP_BASES:
        problems.append("a projected transient size has no declared derivation")
    cost, size, reserve = dict(zip(per["partition"], per["cpu_s"])), dict(zip(per["partition"], per["projected_bytes"])), \
        _reserve(per)
    for row in f.itertuples():
        sel = _scenario_rows(cfg, planned, row.scenario)
        projected = math.fsum(cost[p] for p in sel)
        if (row.n_partitions != len(sel) or not math.isclose(row.projected_cpu_s, projected, rel_tol=1e-9, abs_tol=1e-6)
                or row.projected_bytes != sum(int(size[p]) for p in sel)
                or not math.isclose(row.reserve_cpu_s, reserve, rel_tol=1e-9, abs_tol=1e-6)
                or not math.isclose(row.total_cpu_s, row.consumed_cpu_s + row.projected_cpu_s + row.reserve_cpu_s,
                                    rel_tol=1e-12, abs_tol=1e-6)
                or row.status != ("WITHIN_CAP" if row.total_cpu_s <= CPU_CAP_S else "OVER_CAP")):
            problems.append(f"scenario {row.scenario} does not reconcile with its partition rows")
    if f.loc[f["scenario"] == "FULL_GRID", "status"].iloc[0] != "WITHIN_CAP":
        problems.append("FULL_GRID is not WITHIN_CAP")
    return problems


def _evidence_problems(table, session_id, bound, required_volume):
    """Evidence-cost measurement against the forecast per-invocation control bound and the projected ledger volume."""
    if list(table.columns) != EVIDENCE_COLUMNS or list(table["stage"]) != list(EVIDENCE_STAGES):
        return ["the evidence-cost table is not the closed measurement"]
    cpu = table["cpu_s"].to_numpy(dtype=np.float64)
    problems = []
    if (table["session_id"] != session_id).any() or (table["label"] != EVIDENCE_LABEL).any():
        problems.append("the evidence-cost measurement belongs to another identity")
    if set(table["status"]) != {"PASSED"}:
        problems.append("the candidate evidence did not pass its verification")
    if not np.isfinite(cpu).all() or (cpu < 0).any() or not math.fsum(cpu) <= bound:
        problems.append(f"the measured control CPU {math.fsum(cpu)} s is invalid or above the {bound} s bound")
    if int(table.loc[table["stage"] == "ledger_volume", "n_attempts"].iloc[0]) < required_volume:
        problems.append(f"the ledger volume measured is below the {required_volume} projected attempts")
    return problems


def _synthetic_ledger(attempts_dir, out, volume):
    src, dst = Path(attempts_dir), Path(out) / "attempts"
    done = [e for e in sorted(src.iterdir()) if read_attempt(e)["state"] == "MEASURED"]
    if not done:
        raise IncompleteWork("no finalized attempt to extend into a ledger volume")
    dst.mkdir(parents=True)
    for e in done:
        shutil.copytree(e, dst / e.name)
    start = int(done[-1].name[1:]) + 1
    for k in range(start, start + max(0, volume - len(done))):
        shutil.copytree(done[-1], dst / f"A{k:07d}")
    if imports_dir(src).is_dir():
        shutil.copytree(imports_dir(src), imports_dir(dst))
    return dst


def evidence_cost(cfg, identity, receipts_dir, report_dir, technical_go, attempts_dir, active, volume, meter):
    """Technical candidate, never written as activation: CPU of one full invocation's controls at a ledger volume."""
    act = _activation_record(identity, receipts_dir, report_dir, technical_go, attempts_dir, active, None,
                             "evidence-cost candidate", None)
    status = "PASSED"
    with tempfile.TemporaryDirectory(prefix="e4-evidence-") as d:
        with meter.stage("evidence_check", 1):
            try:
                _verify_activation(act, identity, attempts_dir, candidate=True)
            except (ActivationRefused, GateStop, KeyError, TypeError, ValueError, OSError):
                status = "REFUSED"
        with meter.stage("pending_costs", 1):
            _remaining(cfg, Path(d) / "no_campaign", identity, act)
        synthetic = _synthetic_ledger(attempts_dir, d, volume)
        with meter.stage("ledger_volume", 1):
            n = len(ledger(synthetic)["attempts"])
    current = act["ledger"]["n_attempts"]
    rows = [{"session_id": identity["session_id"], "stage": s, "n_attempts": n if s == "ledger_volume" else current,
             "cpu_s": meter.rows[s]["cpu_s"], "wall_s": meter.rows[s]["wall_s"], "status": status,
             "label": EVIDENCE_LABEL} for s in EVIDENCE_STAGES]
    return pd.DataFrame(rows, columns=EVIDENCE_COLUMNS)


def receipt_pilot(cfg, identity, p1_root, p2_root, report_dir, publication, attempts_dir, active=None):
    """Pilot receipt: P1 cost partitions, complete P2 fixture campaign, interruption, replays, report tables."""
    p1_id, p2_id = sibling_identity(identity, "production_pilot"), sibling_identity(identity, "cost_fixture")
    expected = {f"cost_{bg}_N{N}_{r}" for bg, N in P1_CELLS for r in COST_ROLES}
    try:
        for root, sid in ((p1_root, p1_id), (p2_root, p2_id)):
            if json.loads((Path(root) / "session.json").read_text(encoding="utf-8")) != sid:
                raise ActivationRefused(f"{root} belongs to another identity: stale pilot evidence")
        names = {p.name for p in (Path(p1_root) / "partitions").iterdir()}
        if names != expected:
            raise ActivationRefused(f"P1 partitions {sorted(names)} differ from {sorted(expected)}")
        p1 = {}
        for pid in sorted(expected):
            verify_partition(Path(p1_root) / "partitions" / pid, pid, p1_id)
            p1[pid] = pdb.file_sha256(Path(p1_root) / "partitions" / pid / "partition.json")
        verify_campaign(cfg, "cost_fixture", p2_root, p2_id)
        verify_publication(publication)
        if json.loads((Path(publication) / "PUBLISHED.json").read_text(encoding="utf-8"))["session_id"] != p2_id[
                "session_id"]:
            raise ActivationRefused("the pilot publication belongs to another identity")
        led = ledger(attempts_dir, active)
    except (IncompleteWork, pdb.PartitionMismatch, GateStop, OSError, ValueError, KeyError) as exc:
        raise ActivationRefused(f"pilot evidence refused: {exc}") from exc
    results = [(a, a["result"] or {}) for a in led["attempts"]]
    p1_attempts = {r.get("partition"): a["attempt_id"] for a, r in results
                   if r.get("phase") == "cost-kernels" and a["exit"] == 0 and r.get("status") == "COMPLETE"}
    interrupted = [(a, r) for a, r in results if a["intended_interrupt"]]
    if set(p1_attempts) != expected or not interrupted:
        raise ActivationRefused("the P1 attempts or the deliberate interruption are missing from the ledger")
    a7, r7 = interrupted[-1]
    part = r7.get("partition")
    again = [a["attempt_id"] for a, r in results if a["attempt_id"] > a7["attempt_id"] and a["exit"] == 0
             and r.get("partition") == part and r.get("status") == "COMPLETE" and r.get("mode") == "cost_fixture"]
    leftovers = sorted(p.name for p in (Path(p2_root) / "partitions").glob(f"{part}.tmp-*"))
    replays = [a["attempt_id"] for a, r in results
               if r.get("mode") == "cost_fixture" and a["exit"] == 0 and r.get("status") == "SKIPPED_COMPLETE"]
    problems = _report_problems(report_dir) + _forecast_problems(report_dir, identity)
    if not again or not leftovers or len(replays) < 3 or problems:
        raise ActivationRefused(f"pilot evidence incomplete: recompute {again}, leftovers {leftovers}, "
                                f"replays {replays}, {problems}")
    return {"kind": "pilot", "session_id": identity["session_id"], "p1": {"session_id": p1_id["session_id"],
            "partitions": p1, "attempts": [p1_attempts[p] for p in sorted(expected)]},
            "p2": {"session_id": p2_id["session_id"], "block": read_plan(p2_root, p2_id)["block"],
                   "partitions": len(plan_partitions(cfg, "cost_fixture", read_plan(p2_root, p2_id)["block"])),
                   "publication": pdb.file_sha256(Path(publication) / "PUBLISHED.json")},
            "interruption": {"attempt": a7["attempt_id"], "partition": part, "recompute_attempts": again,
                             "leftovers": leftovers}, "replays": replays, "p1_attempts": len(p1_attempts),
            "leaves": {name: _leaf(Path(report_dir) / name) for name in REPORT_FILES + (REPORT_MANIFEST,)},
            "ledger": led["snapshot"]}


def receipt_accounting(identity, publication, active):
    """Terminal accounting receipt: published hashes and the post-publication ledger; its own attempt is the queue."""
    publication = Path(publication)
    return {"kind": "accounting", "session_id": identity["session_id"],
            "publication": {"published_sha256": pdb.file_sha256(publication / "PUBLISHED.json"),
                            "manifest_sha256": pdb.file_sha256(publication / "manifest.json")},
            "queue": {"active_attempt": active,
                      "note": "administrative bookkeeping outside producer measures; its CPU is finalized by the host"}}


def _pilot_checks(receipt, identity, attempts_dir):
    report = _leaf_path(receipt["leaves"]["forecast.csv"]).parent
    problems = _report_problems(report) + _forecast_problems(report, identity)
    if set(read_table(report / "forecast.csv")["block"]) != {receipt["p2"]["block"]}:
        problems.append("the attested P2 block differs from the forecast block")
    return problems


def receipt_nonleak(identity, p1_root, report_dir, p2_root):
    """Closed-set receipt: P1 holds cost tables only, the report is its closed manifest set, P2 is labelled fixture."""
    expected = {f"cost_{bg}_N{N}_{r}" for bg, N in P1_CELLS for r in COST_ROLES}
    leaves = {f"report/{n}": Path(report_dir) / n for n in REPORT_FILES + (REPORT_MANIFEST,)}
    leaves.update({f"p1/{pid}/cost.csv": Path(p1_root) / "partitions" / pid / "cost.csv" for pid in expected})
    try:
        problems = []
        if {p.name for p in (Path(p1_root) / "partitions").iterdir()} != expected:
            problems.append("P1 holds foreign partitions")
        problems += _report_problems(report_dir)
        for pid in sorted(expected):
            if {q.name for q in (Path(p1_root) / "partitions" / pid).iterdir()} != {"cost.csv", "partition.json"}:
                problems.append(f"{pid} holds foreign files")
        session = json.loads((Path(p2_root) / "session.json").read_text(encoding="utf-8"))
        manifest = json.loads((Path(p2_root) / "partitions" / "merge" / "manifest.json").read_text(encoding="utf-8"))
        if session["mode"] != "cost_fixture" or manifest["label"] != "COST_FIXTURE":
            problems.append("the P2 campaign is not labelled COST_FIXTURE")
        receipt = {"kind": "nonleak", "session_id": identity["session_id"],
                   "leaves": {k: _leaf(v) for k, v in leaves.items()}, "p2_label": manifest["label"]}
    except (OSError, ValueError, KeyError) as exc:
        raise ActivationRefused(f"non-leak evidence refused: {exc}") from exc
    problems += _nonleak_checks(receipt, identity, None)
    if problems:
        raise ActivationRefused("; ".join(problems))
    return receipt


def _nonleak_checks(receipt, identity, attempts_dir):
    problems = _nonleak_fact_problems(receipt)
    if problems:
        return problems
    problems += _report_problems(_leaf_path(receipt["leaves"][f"report/{REPORT_MANIFEST}"]).parent)
    for name, leaf in receipt["leaves"].items():
        if not name.startswith("p1/"):
            continue
        df = read_table(_leaf_path(leaf))
        if (list(df.columns) != e4.COST_COLUMNS or set(df["status"]) != {"COMPLETE"}
                or not all(re.fullmatch(COST_STAGE_RE, s) for s in df["stage"])):
            problems.append(f"{name} is not a closed cost table")
    return problems


RECEIPT_CHECKS = {"pilot": _pilot_checks, "nonleak": _nonleak_checks}


def _verify_activation(act, identity, attempts_dir, candidate=False):
    if act["session_id"] != identity["session_id"] or act["seed_plan_sha256"] != identity["seed_plan_sha256"]:
        raise ActivationRefused("the activation belongs to another identity: stale evidence")
    if identity.get("config_file_sha256") != REFERENCE_CONFIG_SHA256 or act["references"] != REFERENCE_SHA256:
        raise ActivationRefused("the configuration or the reference sources differ from the approved ones")
    for rel, sha in REFERENCE_SHA256.items():
        if not (e4.REPO_ROOT / rel).is_file() or pdb.file_sha256(e4.REPO_ROOT / rel) != sha:
            raise ActivationRefused(f"{rel} differs from its approved SHA-256")
    if act["go_full"].get("path") != GO_FULL_PATH:
        raise ActivationRefused("the activation does not cite the researcher's full GO")
    _check_leaf(act["go_full"])
    _check_leaf(act["technical_go"])
    if set(act["receipts"]) != set(RECEIPT_KINDS):
        raise ActivationRefused(f"receipts {sorted(act['receipts'])} differ from {list(RECEIPT_KINDS)}")
    receipts = {}
    for kind, leaf in act["receipts"].items():
        _check_leaf(leaf)
        receipts[kind] = json.loads(_leaf_path(leaf).read_text(encoding="utf-8"))
        validate_receipt(kind, receipts[kind], identity, attempts_dir)
    for leaf in act["forecast"].values():
        _check_leaf(leaf)
    problems = _forecast_link_problems(act, receipts)
    if problems:
        raise ActivationRefused("; ".join(problems))
    problems = _forecast_problems(_leaf_path(act["forecast"]["forecast"]).parent, identity)
    if problems:
        raise ActivationRefused("; ".join(problems))
    try:
        check_snapshot(attempts_dir, act["ledger"])
        f = read_table(_leaf_path(act["forecast"]["forecast"]))
        row = f[f["scenario"] == "FULL_GRID"].iloc[0]
        frozen = json.loads(_leaf_path(act["forecast"]["manifest"]).read_text(encoding="utf-8"))["ledger"]
        if (str(frozen["cutoff"] or "NONE") != str(row["cutoff"]) or not math.isclose(
                consumed_through(attempts_dir, row["cutoff"], frozen["imports"]), row["consumed_cpu_s"], abs_tol=1e-6)):
            raise ActivationRefused("the forecast consumed CPU differs from its frozen ledger snapshot")
        at_activation = consumed_through(attempts_dir, act["ledger"]["cutoff"], act["ledger"]["imports"])
        if not math.isclose(at_activation, act["ledger"]["consumed_cpu_s"], abs_tol=1e-6) or not (
                at_activation + row["projected_cpu_s"] + row["reserve_cpu_s"] <= CPU_CAP_S):
            raise ActivationRefused("the CPU measured up to the activation (receipts, evidence checks) plus the "
                                    "projection and reserve exceeds the cap or differs from the activation ledger")
    except GateStop as exc:
        raise ActivationRefused(str(exc)) from exc
    if candidate:
        return
    _check_leaf(act["evidence_cost"])
    required = act["ledger"]["n_attempts"] + int(row["n_partitions"]) + INTERRUPTION_RESERVE_BLOCKS
    problems = _evidence_problems(read_table(_leaf_path(act["evidence_cost"])), identity["session_id"],
                                  float(row["control_bound_s"]), required)
    if problems:
        raise ActivationRefused("; ".join(problems))


def check_activation(path, identity, attempts_dir=ATTEMPTS_DIR):
    """Activation record re-verified against the current identity and its evidence; ActivationRefused otherwise."""
    if not path:
        raise ActivationRefused("no activation record: the full campaign is not activated")
    try:
        act = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ActivationRefused(f"unreadable activation record {path}") from exc
    if not isinstance(act, dict) or set(act) != ACTIVATION_KEYS:
        raise ActivationRefused("the activation record does not hold exactly the required evidence keys")
    try:
        _verify_activation(act, identity, attempts_dir)
    except (KeyError, TypeError, AttributeError, IndexError, ValueError, OSError) as exc:
        raise ActivationRefused(f"malformed activation evidence: {exc!r}") from exc
    return act


def _activation_record(identity, receipts_dir, report_dir, technical_go, attempts_dir, active, evidence, command,
                       disk):
    return {"session_id": identity["session_id"], "seed_plan_sha256": identity["seed_plan_sha256"],
            "go_full": _leaf(e4.REPO_ROOT / GO_FULL_PATH), "technical_go": _leaf(technical_go),
            "references": REFERENCE_SHA256,
            "receipts": {k: _leaf(Path(receipts_dir) / f"{k}.json") for k in RECEIPT_KINDS},
            "forecast": {"forecast": _leaf(Path(report_dir) / "forecast.csv"),
                         "partition_forecast": _leaf(Path(report_dir) / "partition_forecast.csv"),
                         "manifest": _leaf(Path(report_dir) / REPORT_MANIFEST)},
            "evidence_cost": None if evidence is None else _leaf(Path(evidence) / "evidence_cost.csv"),
            "disk": disk, "ledger": ledger(attempts_dir, active)["snapshot"], "command": command}


def activate(cfg, identity, receipts_dir, report_dir, technical_go, attempts_dir, active, command, out, disk_root,
             evidence):
    """Explicit activation: receipts and evidence-cost revalidated, disk measured, record written once; its SHA-256."""
    per = read_table(Path(report_dir) / "partition_forecast.csv")
    footprint = 4 * int(per["projected_bytes"].sum()) + int(per["projected_tmp_bytes"].max())
    free = shutil.disk_usage(_existing(disk_root)).free
    if free - footprint < DISK_RESERVE_BYTES:
        raise ActivationRefused(f"free disk {free} B minus the projected {footprint} B is below the reserve")
    disk = {"free_bytes": int(free), "projected_footprint_bytes": footprint, "reserve_bytes": DISK_RESERVE_BYTES,
            "label": "ESTIMATE_FOOTPRINT_BLOCKS_FRAGMENTS_PUBLICATION_GIT"}
    act = _activation_record(identity, receipts_dir, report_dir, technical_go, attempts_dir, active, evidence, command,
                             disk)
    _verify_activation(act, identity, attempts_dir)
    out = Path(out)
    if out.exists() and json.loads(out.read_text(encoding="utf-8")) != act:
        raise pdb.PartitionMismatch(f"{out} already holds another activation record")
    out.parent.mkdir(parents=True, exist_ok=True)
    e4._write_atomic(out, pdb.canon(act))
    return pdb.file_sha256(out)


PHASES = ("plan", "next", "run", "verify", "publish", "verify-publication", "cost-kernels", "forecast", "receipt",
          "activate", "evidence-cost", "import-costs")
ACTIVATED_PHASES = {"plan", "next", "run", "verify", "publish"}


def _xcpu(signum, frame):
    raise pdb.ResourceBlocked("the process CPU soft limit is reached")


def _arm_cpu_limit():
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    target = CPU_RLIMIT_S if hard == resource.RLIM_INFINITY or hard >= CPU_RLIMIT_S[1] else (
        min(CPU_RLIMIT_S[0], hard), hard)
    resource.setrlimit(resource.RLIMIT_CPU, target)


def _root(args):
    if not args.root:
        raise ValueError(f"--phase {args.phase} needs --root")
    return Path(args.root)


def _cli_plan(cfg, args, identity, activation, deadline, meter):
    if args.block is None:
        raise ValueError("--phase plan needs --block")
    K = write_plan(cfg, args.mode, _root(args), identity, args.block)
    sys.stdout.write(f"{K}\n")
    sys.stdout.flush()
    return 0, "PLANNED"


def _cli_next(cfg, args, identity, activation, deadline, meter):
    pid = next_pending(cfg, args.mode, _root(args), identity)
    if pid is None:
        return 10, "DONE"
    args.partition = pid
    return 0, run_phase(cfg, args.mode, args.root, identity, pid, deadline, args.fixture_interrupt)


def _cli_run(cfg, args, identity, activation, deadline, meter):
    if not args.partition:
        raise ValueError("--phase run needs --partition")
    return 0, run_phase(cfg, args.mode, _root(args), identity, args.partition, deadline, args.fixture_interrupt)


def _cli_verify(cfg, args, identity, activation, deadline, meter):
    print(json.dumps(verify_campaign(cfg, args.mode, _root(args), identity), sort_keys=True), file=sys.stderr)
    return 0, "VERIFIED"


def _cli_cost(cfg, args, identity, activation, deadline, meter):
    if args.mode != "production_pilot":
        raise ValueError("--phase cost-kernels runs only in mode production_pilot (seed space pilot)")
    pid = f"cost_{args.cell}_{args.role}"
    info = parse_pid(pid, cfg, args.mode)
    replicates = e4._integer(args.replicates, "replicates", 1)

    def compute(tmp):
        cost_kernels(cfg, info["background"], info["N"], info["role"], replicates, meter, deadline)
        rows = [{"partition": pid, **{k: r[k] for k in e4.COST_COLUMNS[1:-1]}, "status": "COMPLETE"}
                for r in meter.rows.values()]
        pipelines.save_fair_csv(pd.DataFrame(rows, columns=e4.COST_COLUMNS), tmp / "cost.csv")
        return {"label": "COST_ONLY_NOT_SCIENTIFIC_E4", "replicates": replicates, "role": info["role"]}

    args.partition = pid
    return 0, run_production_partition(_root(args), pid, identity, compute)[0]


def _cli_publish(cfg, args, identity, activation, deadline, meter):
    if not args.to:
        raise ValueError("--phase publish needs --to")
    return 0, publish(cfg, args.mode, _root(args), identity, args.to, args.attempts, args.active,
                      args.activation if args.mode == "full" else None)


def _cli_verify_publication(cfg, args, identity, activation, deadline, meter):
    summary = verify_publication(args.to or args.publication, require_activation=args.mode == "full")
    print(json.dumps(summary, sort_keys=True), file=sys.stderr)
    return 0, "VERIFIED"


def _cli_forecast(cfg, args, identity, activation, deadline, meter):
    if (args.mode != "full" or args.block is None or not args.out or not args.publication
            or args.control_bound_s is None):
        raise ValueError("--phase forecast needs --mode full, --block, --publication, --control-bound-s and --out")
    tables, led = forecast_production(cfg, identity, args.block, args.p1_root, args.p2_root, args.prior_costs,
                                      args.attempts, args.publication, args.control_bound_s, args.active)
    write_report(args.out, tables, led, identity)
    return 0, "FORECAST_WRITTEN"


def _cli_evidence_cost(cfg, args, identity, activation, deadline, meter):
    if args.mode != "full" or not (args.receipts and args.report and args.technical_go and args.out and args.volume):
        raise ValueError("--phase evidence-cost needs --mode full, --receipts, --report, --technical-go, --volume, --out")
    table = evidence_cost(cfg, identity, args.receipts, args.report, args.technical_go, args.attempts, args.active,
                          e4._integer(args.volume, "volume", 1), meter)
    _write_new_dir(args.out, {"evidence_cost.csv": table})
    return 0, "EVIDENCE_COST_WRITTEN"


def _cli_import_costs(cfg, args, identity, activation, deadline, meter):
    if not (args.source and args.category):
        raise ValueError("--phase import-costs needs --source and --category")
    record = import_costs(args.attempts, args.source, args.category)
    print(json.dumps({"import_id": record["import_id"], "cpu_s": record["cpu_s"]}, sort_keys=True), file=sys.stderr)
    return 0, "IMPORTED"


def _cli_receipt(cfg, args, identity, activation, deadline, meter):
    if args.mode != "full" or not args.out:
        raise ValueError("--phase receipt needs --mode full (the identity it binds) and --out")
    if args.kind == "tests":
        body = receipt_tests(identity, args.junit, args.log, args.command, args.exit_code)
    elif args.kind == "make_check":
        body = receipt_make_check(identity, args.log, args.command, args.exit_code)
    elif args.kind == "pilot":
        body = receipt_pilot(cfg, identity, args.p1_root, args.p2_root, args.report, args.publication, args.attempts,
                             args.active)
    elif args.kind == "nonleak":
        body = receipt_nonleak(identity, args.p1_root, args.report, args.p2_root)
    elif args.kind == "accounting":
        body = receipt_accounting(identity, args.publication, args.active)
    else:
        raise ValueError("--phase receipt needs --kind")
    body["ledger"] = ledger(args.attempts, args.active)["snapshot"]
    out = Path(args.out)
    if out.exists():
        raise pdb.PartitionMismatch(f"{out} already exists; receipts are immutable")
    out.parent.mkdir(parents=True, exist_ok=True)
    e4._write_atomic(out, pdb.canon(body))
    return 0, "RECEIPT_WRITTEN"


def _cli_activate(cfg, args, identity, activation, deadline, meter):
    if args.mode != "full" or not (args.receipts and args.report and args.technical_go and args.out):
        raise ValueError("--phase activate needs --mode full, --receipts, --report, --technical-go and --out")
    sha = activate(cfg, identity, args.receipts, args.report, args.technical_go, args.attempts, args.active,
                   " ".join(sys.argv), args.out, args.root or ".", args.evidence_cost)
    sys.stdout.write(f"{sha}\n")
    return 0, "ACTIVATED"


DISPATCH = {"plan": _cli_plan, "next": _cli_next, "run": _cli_run, "verify": _cli_verify, "cost-kernels": _cli_cost,
            "publish": _cli_publish, "verify-publication": _cli_verify_publication, "forecast": _cli_forecast,
            "receipt": _cli_receipt, "activate": _cli_activate, "evidence-cost": _cli_evidence_cost,
            "import-costs": _cli_import_costs}


def _remaining(cfg, root, identity, activation):
    if activation is None:
        return 0.0, 0
    if not root:
        raise ValueError("an activated full phase needs --root")
    per = read_table(_leaf_path(activation["forecast"]["partition_forecast"]))
    f = read_table(_leaf_path(activation["forecast"]["forecast"]))
    block = int(f.loc[f["scenario"] == "FULL_GRID", "block"].iloc[0])
    cost = dict(zip(per["partition"], per["cpu_s"]))
    size = dict(zip(per["partition"], per["projected_bytes"] + per["projected_tmp_bytes"]))
    root = Path(root)
    fits = {c: "OK" for c in cells_of(cfg)}
    if (root / "campaign_plan.json").exists():
        if read_plan(root, identity)["block"] != block:
            raise GateStop("the campaign block differs from the activated forecast block")
        fits.update(fit_statuses(cfg, root, identity))
    pending = [p for p in plan_partitions(cfg, "full", block, fits) if not (root / "partitions" / p).exists()]
    missing = [p for p in pending if p not in cost]
    if missing:
        raise GateStop(f"no forecast for pending partitions {missing[:3]}")
    remaining = sum(cost[p] for p in pending[1:]) + sum(v for k, v in cost.items() if k.startswith("phase:"))
    return float(remaining), int(size[pending[0]]) if pending else 0


def _record(attempts, active, payload):
    target = Path(attempts) / active / "result.json" if active else None
    if target is None or not target.parent.is_dir() or target.exists():
        return
    try:
        target.write_text(pdb.canon(payload), encoding="utf-8")
    except OSError as exc:
        print(f"result of {active} not recorded: {exc}", file=sys.stderr)


def main(argv=None):
    """CLI; exit 0 done, 10 nothing pending, 3 not activated, 4 resource, 5 refused, 6 gate STOP, 7 fixture interrupt."""
    ap = argparse.ArgumentParser(description="E4 production: blocks, threshold barrier, merge, analysis, publication")
    ap.add_argument("--phase", required=True, choices=PHASES)
    ap.add_argument("--mode", required=True, choices=tuple(MODES))
    ap.add_argument("--root")
    ap.add_argument("--config", default=str(e4.CONFIG))
    ap.add_argument("--attempts", default=str(ATTEMPTS_DIR))
    ap.add_argument("--decisions")
    ap.add_argument("--activation")
    ap.add_argument("--block", type=int)
    ap.add_argument("--partition")
    ap.add_argument("--cell")
    ap.add_argument("--role", choices=COST_ROLES)
    ap.add_argument("--replicates", type=int)
    ap.add_argument("--to")
    ap.add_argument("--fixture-interrupt", action="store_true")
    ap.add_argument("--cpu-ceiling-s", type=float, default=CPU_CAP_S)
    ap.add_argument("--kind", choices=RECEIPT_KINDS + ("accounting",))
    for name in ("--junit", "--log", "--command", "--p1-root", "--p2-root", "--report", "--publication", "--out",
                 "--technical-go", "--receipts", "--prior-costs", "--evidence-cost", "--source", "--category"):
        ap.add_argument(name)
    ap.add_argument("--exit-code", type=int)
    ap.add_argument("--control-bound-s", type=float)
    ap.add_argument("--volume", type=int)
    args = ap.parse_args(argv)
    problems = pdb.check_env()
    if problems:
        print("environment refused: " + "; ".join(problems), file=sys.stderr)
        return 5
    active, meter = os.environ.get("E4_ATTEMPT_ID"), e4.Meter()
    args.active = active
    previous = {s: signal.getsignal(s) for s in (signal.SIGALRM, signal.SIGXCPU)}
    code, status = 5, "REFUSED"
    try:
        signal.signal(signal.SIGALRM, e4._alarm)
        signal.signal(signal.SIGXCPU, _xcpu)
        with meter.stage("startup", 0):
            cfg = e4.validate_config(e4.load_config(args.config))
        with meter.stage("identity", 0):
            identity = production_identity(cfg, args.mode, args.config)
        deadline = time.monotonic() + cfg["limits"]["invocation_seconds"]
        signal.alarm(max(1, int(cfg["limits"]["invocation_seconds"])))
        _arm_cpu_limit()
        activation = None
        if args.mode == "full" and args.phase in ACTIVATED_PHASES:
            activation = check_activation(args.activation, identity, args.attempts)
        if active is None:
            raise GateStop("E4_ATTEMPT_ID is required: every invocation is an attempt of the ledger")
        remaining, next_bytes = _remaining(cfg, args.root, identity, activation)
        gate(args.attempts, active, remaining, args.root or ".", next_bytes, args.decisions, args.cpu_ceiling_s)
        code, status = DISPATCH[args.phase](cfg, args, identity, activation, deadline, meter)
    except ActivationRefused as exc:
        code, status = 3, f"NOT_ACTIVATED: {exc}"
    except pdb.ResourceBlocked as exc:
        code, status = 4, f"BLOCKED_RESOURCE: {exc}"
    except OSError as exc:
        code, status = 4, f"OS_ERROR: {exc}"
    except (IncompleteWork, pdb.PartitionMismatch, ValueError, KeyError) as exc:
        code, status = 5, f"REFUSED: {exc}"
    except GateStop as exc:
        code, status = 6, f"STOP: {exc}"
    except FixtureInterrupt as exc:
        code, status = 7, f"FIXTURE_INTERRUPT: {exc}"
    finally:
        signal.alarm(0)
        for s, h in previous.items():
            signal.signal(s, h)
    print(f"{args.phase} {args.mode} {args.partition or ''}: {status}", file=sys.stderr)
    _record(args.attempts, active, {"phase": args.phase, "mode": args.mode, "partition": args.partition, "code": code,
                                    "status": status.split(":")[0]})
    return code


if __name__ == "__main__":
    sys.exit(main())
