"""Stream 29 assembler: Tableau_PCA_1/2/3 (CSV + Markdown) from one sealed pca_drift_benchmark/2 run directory.

Read-only consumer of a runner artifact: validates the seven files and their semantics, then renders the three
tables, the cell lineage, TABLES_VALIDATION.md and table_manifest.json. It never runs the runner, reads no real
return and recomputes no RMST or FPR. Output contract: docs/sections/pca_drift_tables.md (pca_drift_tables/1).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import pca_drift_benchmark as pdb

import argparse
import hashlib
import importlib
import json
import math

import numpy as np
import pandas as pd

from jepadrift.pipelines import save_fair_csv

EXPECTED_SCHEMA = "pca_drift_benchmark/2"
TABLES_SCHEMA = "pca_drift_tables/1"
RUN_FILES = ("manifest.json", "spectra.csv", "selection.csv", "calibration.csv", "trials.csv", "aggregates.csv",
             "issues.csv")
TABLE_FILES = ("spectra", "selection", "calibration", "trials", "aggregates", "issues")
JSON_STR_COLS = ("run_fingerprint", "group_id", "S", "rank_order", "claim_flag", "scope", "detail", "alarm_dates",
                 "pre_onset_alarm_dates", "maxima_sha256")
INT_COLS = ("k", "d", "reservoir_k")
REAL_STATUSES = ("NOT_EVALUABLE_STANDARD_SPLIT", "BLOCKED_PRE_J4", "DATA_UNAVAILABLE")
ACCORD_FIELDS = ("dataset_id", "cohort_id", "split_hash", "event_window_id", "event_id", "detector_family", "S", "d",
                 "null_id", "null_calibration_id", "calibration_hash", "basis_hash", "config_hash", "seed")
ALT_REQUIRED = ("n", "alarms", "rmst", "det_rate", "censored_share")
ALT_FIXED = ("deff", "n_eff", "det_lo", "det_hi")
ALT_N1_NA = ("rmst_sd", "rmst_se", "rmst_lo", "rmst_hi")
ALT_OPTIONAL = ALT_FIXED + ALT_N1_NA
HOLD_REQUIRED = ("n", "alarms", "fpr", "fpr_lo", "fpr_hi", "target_fpr")
HOLD_FIXED = ("deff", "n_eff")
HOLD_OPTIONAL = HOLD_FIXED
ALT_FIELDS = ALT_REQUIRED + ALT_OPTIONAL
HOLD_FIELDS = HOLD_REQUIRED + HOLD_OPTIONAL
METRIC_FIELDS = ALT_FIELDS + HOLD_FIELDS + ("n_event_sessions", "alarm_dates",
                             "pre_onset_alarms", "pre_onset_alarm_dates", "detected_during_event",
                             "time_to_alarm_during_event", "event_censored", "post_onset_delay_h250",
                             "post_onset_alarm_date", "post_event_alarm", "path_supports_H")
HORIZON = 250
FAMILY_METHODS = {pdb.MEAN: {"BASELINE_PREFIX", "BASELINE_CPV90", "ORACLE_Q_MIX", "ORACLE_Q_AFFINE", "EXANTE_QBAR"},
                  pdb.COV: {"BASELINE_PREFIX", "BASELINE_CPV90", "COV_JOINT_ORACLE", "COV_MARGINAL_DIAGNOSTIC",
                            "EXANTE_QBAR"},
                  pdb.ENERGY: {"ENERGY_INDEX_COMPARATOR"}}


class Refused(ValueError):
    """Input or usage refused; .code is the stable refusal code printed on stderr (exit 2)."""

    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _isna(v):
    return v is None or bool(pd.isna(v))


def _norm(v):
    """Comparable text of a cell: NA -> None, integral floats -> int text, else str(v)."""
    if _isna(v):
        return None
    if isinstance(v, (bool, np.bool_)):
        return str(v)
    if isinstance(v, (float, np.floating)) and float(v).is_integer():
        return str(int(v))
    return str(v)


def _truthy(v):
    return v is True or v == "True"


def _parse_S(text, nmax):
    try:
        return pdb.parse_S(text, nmax)
    except (ValueError, TypeError) as exc:
        raise Refused("INVALID_S", str(exc)) from exc


TEXT_EXTRA = ("schema_version", "run_mode", "s2_rule", "message", "deviation_ref", "monitor_armed_from",
              "onset_date", "event_end_date", "fit_first_day", "fit_last_day")


def read_run_csv(path, name):
    """One run CSV under the /2 rules (str ids/JSON/date fields, Int64 k/d/reservoir_k, round_trip floats); a non-numeric cell in a numeric column raises ValueError -> controlled CSV_PARSE_FAILED (exit 2)."""
    cols = pdb.COLUMNS[name]
    dtype = {c: str for c in cols if c.endswith(("_id", "_hash", "_sha256")) or c in JSON_STR_COLS}
    dtype.update({c: "Int64" for c in INT_COLS if c in cols})
    df = pd.read_csv(path, dtype=dtype, float_precision="round_trip")
    text = set(dtype) | set(pdb.ENUMS) | set(TEXT_EXTRA)
    for c in cols:
        if c in text or c in dtype:
            continue
        if str(df[c].dtype) in ("str", "object") and df[c].notna().any():
            raise ValueError(f"column {c!r} holds non-numeric text: malformed CSV")
    return df


def check_enums(frames):
    """Closed enumerations of pdb.ENUMS on every frame, plus the claim_flag JSON list (F8)."""
    for name, df in frames.items():
        for col, allowed in pdb.ENUMS.items():
            if col not in df.columns:
                continue
            bad = sorted({str(v) for v in df[col].dropna().unique() if v not in allowed and str(v) not in allowed})
            if bad:
                raise Refused("ENUM_VIOLATION", f"{name}.{col} outside its enumeration: {bad}")
    for v in frames["selection"]["claim_flag"].dropna():
        try:
            flags = json.loads(v)
        except ValueError as exc:
            raise Refused("ENUM_VIOLATION", f"claim_flag {v!r} is not JSON") from exc
        if not set(flags) <= set(pdb.CLAIM_FLAGS):
            raise Refused("ENUM_VIOLATION", f"claim_flag {v!r} outside CLAIM_FLAGS")


def _check_cells(manifest, frames):
    """F7: run-wide cells equal the manifest values wherever the column exists."""
    wants = {"schema_version": manifest["schema_version"], "run_fingerprint": manifest["run_fingerprint"],
             "config_hash": manifest["identity"]["config_hash"], "seed": str(manifest["identity"]["seed"]),
             "run_mode": manifest["run_mode"]}
    for name, df in frames.items():
        for col, want in wants.items():
            if col in df.columns:
                bad = {str(v) for v in df[col].dropna().unique() if str(v) != want}
                if bad:
                    raise Refused("CELL_MISMATCH", f"{name}.{col} holds {sorted(bad)} instead of {want!r}")


def _check_unique(df, keys, label):
    seen = set()
    for tup in df[list(keys)].itertuples(index=False, name=None):
        key = tuple(_norm(v) for v in tup)
        if key in seen:
            raise Refused("DUPLICATE_PRIMARY_KEY", f"{label}: duplicate key {key}")
        seen.add(key)


class Run:
    """A loaded run directory: manifest, the six parsed frames, and the indexes filled by validate_run."""

    def __init__(self, input_dir, manifest, frames):
        self.input_dir = Path(input_dir)
        self.manifest = manifest
        self.frames = frames
        self.nmax = int(manifest["config"]["nmax"])
        self.counters = {}
        self.sel_class = None
        self.agg_ix = None
        self.cal_ix = None
        self.spe_ix = None


def load_run(input_dir):
    """F1-F8: the seven files exist, the manifest identity is intact, every output hash/header/run-wide cell matches; returns the Run with parsed frames."""
    d = Path(input_dir)
    if not d.is_dir():
        raise Refused("INPUT_DIR_MISSING", f"{d} is not a directory")
    for f in RUN_FILES:
        if not (d / f).is_file():
            code = "TRIALS_MISSING" if f == "trials.csv" else "FILE_MISSING"
            raise Refused(code, f"{f} is absent from {pdb._rel(d)}")
    try:
        manifest = json.loads((d / "manifest.json").read_text())
    except ValueError as exc:
        raise Refused("MANIFEST_INVALID", str(exc)) from exc
    if not isinstance(manifest, dict):
        raise Refused("MANIFEST_INVALID", "manifest.json is not an object")
    ident, cfg = manifest.get("identity"), manifest.get("config")
    if not isinstance(ident, dict) or not isinstance(cfg, dict):
        raise Refused("MANIFEST_INVALID", "identity/config missing")
    if not (manifest.get("schema_version") == ident.get("schema_version") == cfg.get("schema_version")
            == EXPECTED_SCHEMA) or pdb.SCHEMA_VERSION != EXPECTED_SCHEMA:
        raise Refused("SCHEMA_MISMATCH", f"schema_version is not {EXPECTED_SCHEMA!r} everywhere")
    if manifest.get("run_fingerprint") != hashlib.sha256(pdb.canon(ident).encode()).hexdigest():
        raise Refused("FINGERPRINT_MISMATCH", "run_fingerprint != sha256(canon(identity))")
    sci = {k: v for k, v in cfg.items() if k != "resources"}
    if ident.get("config_hash") != hashlib.sha256(pdb.canon(sci).encode()).hexdigest():
        raise Refused("CONFIG_HASH_MISMATCH", "identity.config_hash != sha256(canon(config sans resources))")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        raise Refused("MANIFEST_INVALID", "outputs missing")
    frames = {}
    for name in TABLE_FILES:
        fn = f"{name}.csv"
        path = d / fn
        meta = outputs.get(fn)
        if not isinstance(meta, dict):
            raise Refused("OUTPUT_UNLISTED", f"manifest.outputs has no {fn}")
        if pdb.file_sha256(path) != meta.get("sha256") or path.stat().st_size != meta.get("bytes"):
            raise Refused("HASH_MISMATCH", f"{fn} differs from manifest.outputs (sha256/bytes)")
        with open(path, encoding="utf-8") as f:
            header = f.readline().rstrip("\n")
        if header != ",".join(pdb.COLUMNS[name]):
            raise Refused("HEADER_MISMATCH", f"{fn} header differs from pdb.COLUMNS[{name!r}]")
        try:
            df = read_run_csv(path, name)
        except (ValueError, TypeError) as exc:
            raise Refused("CSV_PARSE_FAILED", f"{fn} is not parseable under the /2 reading rules: {exc}") from exc
        if len(df) != meta.get("rows"):
            raise Refused("ROW_COUNT_MISMATCH", f"{fn}: {len(df)} rows, manifest says {meta.get('rows')}")
        frames[name] = df
    _check_cells(manifest, frames)
    check_enums(frames)
    return Run(d, manifest, frames)


def _classify_selection_row(r, nmax):
    """§3.3: one declared state class per selection row, else UNEXPECTED_ROW_STATE."""
    if r.method not in FAMILY_METHODS.get(r.detector_family, set()):
        raise Refused("UNEXPECTED_ROW_STATE",
                      f"method {r.method} is not applicable to detector_family {r.detector_family}")
    if r.dataset_id == "D3_239":
        if not (r.row_kind == "SELECTED" and r.execution == "NOT_EXECUTED" and r.status in REAL_STATUSES
                and not _isna(r.metric_id) and not _isna(r.split_hash) and _isna(r.null_metric_id)):
            raise Refused("UNEXPECTED_ROW_STATE",
                          f"real selection {r.selection_id} {r.experiment}: {r.row_kind}/{r.status}/{r.execution}")
        if not _isna(r.S):
            _parse_S(r.S, nmax)
        return "S-REAL"
    if r.row_kind == "CANDIDATE":
        if not (r.status == "OK" and r.execution == "NOT_EXECUTED" and _isna(r.metric_id) and not _isna(r.S)):
            raise Refused("UNEXPECTED_ROW_STATE",
                          f"candididate {r.selection_id} {r.experiment}: {r.status}/{r.execution}")
        _parse_S(r.S, nmax)
        return "S-CAND"
    if r.row_kind == "SELECTED":
        if r.status == "OK" and r.execution == "EXECUTED":
            if _isna(r.metric_id) or _isna(r.null_metric_id) or _isna(r.null_calibration_id):
                raise Refused("UNEXPECTED_ROW_STATE", f"evaluated {r.selection_id} {r.experiment} lacks an id")
            if r.detector_family == pdb.ENERGY:
                if not (_isna(r.k) and _isna(r.S) and _isna(r.d)):
                    raise Refused("UNEXPECTED_ROW_STATE", f"energy {r.selection_id} has k/S/d set")
            else:
                if _isna(r.S) or _isna(r.d) or int(r.d) != len(_parse_S(r.S, nmax)):
                    raise Refused("UNEXPECTED_ROW_STATE", f"selected {r.selection_id} {r.experiment}: bad S/d")
            return "S-EVAL"
        if r.status == "CALIBRATION_FAILED" and r.execution == "NOT_EXECUTED":
            if _isna(r.metric_id) or _isna(r.null_metric_id) or _isna(r.null_calibration_id):
                raise Refused("UNEXPECTED_ROW_STATE", f"calfail {r.selection_id} {r.experiment} lacks an id")
            return "S-CALFAIL"
        if r.status in ("CPV90_OUTSIDE_TOP20", "UNSUPPORTED") and r.execution == "NOT_EXECUTED":
            if not (_isna(r.metric_id) and _isna(r.null_metric_id) and _isna(r.null_calibration_id)):
                raise Refused("UNEXPECTED_ROW_STATE", f"noeval {r.selection_id} {r.experiment} carries a metric id")
            if not _isna(r.S):
                _parse_S(r.S, nmax)
            return "S-NOEVAL"
    raise Refused("UNEXPECTED_ROW_STATE",
                  f"selection {r.selection_id} {r.experiment} {r.row_kind}: {r.status}/{r.execution}")


def _accord(row, other, fields, label):
    for f in fields:
        a, b = _norm(getattr(row, f)), _norm(getattr(other, f))
        if a is not None and b is not None and a != b:
            raise Refused("ACCORD_MISMATCH", f"{label}: {f} is {a!r} vs {b!r}")


def validate_run(run):
    """§3.2-§3.5: primary keys, row-state classes, foreign keys/accords, aggregate classes, trial counts; fills run.counters/sel_class/agg_ix/cal_ix/spe_ix and returns run."""
    frames = run.frames
    nmax = run.nmax
    check_enums(frames)
    for name in TABLE_FILES:
        _check_unique(frames[name], pdb.PRIMARY_KEYS[name], name)
    sel, agg, cal, tri = frames["selection"], frames["aggregates"], frames["calibration"], frames["trials"]
    run.agg_ix = agg.set_index("metric_id", drop=False)
    run.cal_ix = cal.set_index("null_calibration_id", drop=False)
    run.spe_ix = {(r.dataset_id, r.basis_hash, int(r.k)): r for r in frames["spectra"].itertuples(index=False)}
    classes = [_classify_selection_row(r, nmax) for r in sel.itertuples(index=False)]
    run.sel_class = pd.Series(classes, index=sel.index)
    _validate_lineage_controls(run)
    validate_horizon(run)
    validate_real_contract(run)
    validate_calibration_failures(run)
    c = {k: 0 for k in ("selection_rows", "sel_metric_refs", "s_eval", "s_calfail", "s_noeval", "s_cand", "s_real",
                        "real_s_na", "real_null_calibration_filled", "cand_theory_filled", "agg_rows", "alt_ok",
                        "holdout_ok", "calfail_agg", "gauss_check", "real_path", "cal_rows", "cal_ok", "cal_failed",
                        "trials_rows", "trials_calibration", "trials_holdout", "trials_alternative", "issues_rows")}
    c["selection_rows"] = len(sel)
    c["agg_rows"] = len(agg)
    c["cal_rows"] = len(cal)
    c["trials_rows"] = len(tri)
    c["issues_rows"] = len(frames["issues"])
    refs = sel["metric_id"].dropna()
    c["sel_metric_refs"] = int(len(refs))
    c["sel_metric_distinct"] = int(refs.nunique())
    for r, cls in zip(sel.itertuples(index=False), classes):
        c[{"S-EVAL": "s_eval", "S-CALFAIL": "s_calfail", "S-NOEVAL": "s_noeval", "S-CAND": "s_cand",
           "S-REAL": "s_real"}[cls]] += 1
        if cls == "S-CAND" and all(not _isna(getattr(r, f)) for f in ("I_objective", "M_cost", "V_mix", "V_affine")):
            c["cand_theory_filled"] += 1
        if cls == "S-REAL":
            if _isna(r.S):
                c["real_s_na"] += 1
            if not _isna(r.null_calibration_id):
                c["real_null_calibration_filled"] += 1
    for r, cls in zip(sel.itertuples(index=False), classes):
        if _isna(r.metric_id):
            continue
        label = f"selection {r.selection_id} {r.experiment}"
        if r.metric_id not in run.agg_ix.index:
            raise Refused("FOREIGN_KEY_MISSING", f"{label}: metric_id {r.metric_id} not in aggregates")
        a = run.agg_ix.loc[r.metric_id]
        if cls == "S-REAL" and a.metric_kind != "REAL_EVENT_PATH":
            raise Refused("ACCORD_MISMATCH", f"{label}: real row points to {a.metric_kind}")
        if cls == "S-EVAL" and a.metric_kind != "ALT_RMST":
            raise Refused("ACCORD_MISMATCH", f"{label}: synthetic evaluated row points to {a.metric_kind}")
        if cls in ("S-EVAL", "S-CALFAIL"):
            if r.null_metric_id not in run.agg_ix.index:
                raise Refused("FOREIGN_KEY_MISSING", f"{label}: null_metric_id not in aggregates")
            if r.null_calibration_id not in run.cal_ix.index:
                raise Refused("FOREIGN_KEY_MISSING", f"{label}: null_calibration_id not in calibration")
            if cls == "S-CALFAIL" and run.cal_ix.loc[r.null_calibration_id].status != "CALIBRATION_FAILED":
                raise Refused("INCOHERENT_CALIBRATION_FAILURE",
                              f"{label}: failed selection references a non-failed calibration "
                              f"{r.null_calibration_id}")
            hold = run.agg_ix.loc[r.null_metric_id]
            if hold.metric_kind != "HOLDOUT_NULL_FPR":
                raise Refused("ACCORD_MISMATCH", f"{label}: null_metric_id is {hold.metric_kind}")
            if cls == "S-EVAL":
                if _norm(hold.null_calibration_id) != _norm(r.null_calibration_id) or _norm(a.null_metric_id) != _norm(r.null_metric_id):
                    raise Refused("FOREIGN_NULL", f"{label}: holdout of another null")
            crow = run.cal_ix.loc[r.null_calibration_id]
            _accord(r, crow, ("dataset_id", "detector_family", "S", "basis_hash", "null_id", "calibration_hash"),
                    label + " calibration")
        _accord(r, a, ACCORD_FIELDS, label)
        if cls == "S-REAL" and not _isna(r.null_calibration_id):
            if r.null_calibration_id not in run.cal_ix.index:
                raise Refused("FOREIGN_KEY_MISSING", f"{label}: real null_calibration_id not in calibration")
            crow = run.cal_ix.loc[r.null_calibration_id]
            if crow.null_kind != "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS" or _norm(crow.cohort_id) != _norm(r.cohort_id) \
                    or _norm(crow.split_hash) != _norm(r.split_hash):
                raise Refused("ACCORD_MISMATCH", f"{label}: real calibration cohort/split mismatch")
        if cls == "S-REAL" and not _isna(r.basis_hash) and not any(
                k[0] == r.dataset_id and k[1] == r.basis_hash for k in run.spe_ix):
            raise Refused("FOREIGN_KEY_MISSING", f"{label}: basis_hash not in spectra")
    for r in agg.itertuples(index=False):
        kind = r.metric_kind
        if kind in ("ALT_RMST", "HOLDOUT_NULL_FPR"):
            if r.status == "OK" and r.execution == "EXECUTED":
                if kind == "ALT_RMST":
                    req, fixed, n1_na = ALT_REQUIRED, ALT_FIXED, ALT_N1_NA
                else:
                    req, fixed, n1_na = HOLD_REQUIRED, HOLD_FIXED, ()
                nv = getattr(r, "n")
                at_n1 = not _isna(nv) and int(nv) == 1
                bad = [f for f in req + fixed if _isna(getattr(r, f)) or not math.isfinite(float(getattr(r, f)))]
                bad += [f for f in n1_na if not _isna(getattr(r, f)) and not math.isfinite(float(getattr(r, f)))]
                if not at_n1:
                    bad += [f for f in n1_na if _isna(getattr(r, f))]
                if bad:
                    raise Refused("NON_FINITE_METRIC",
                                  f"{r.metric_id} ({kind}) lacks finite {bad} (deff/n_eff and the Wilson bounds "
                                  f"are required at every n; at n = 1 only rmst_sd/rmst_se/rmst_lo/rmst_hi may "
                                  f"be NA, required finite again at n > 1; never non-finite)")
                if r.null_calibration_id not in run.cal_ix.index:
                    raise Refused("FOREIGN_KEY_MISSING", f"{r.metric_id}: calibration missing")
                crow = run.cal_ix.loc[r.null_calibration_id]
                if crow.status != "OK" or _isna(crow.threshold) or not math.isfinite(float(crow.threshold)):
                    raise Refused("CALIBRATION_NOT_OK", f"{r.metric_id}: linked calibration not OK/finite")
                c["alt_ok" if kind == "ALT_RMST" else "holdout_ok"] += 1
            elif r.status == "CALIBRATION_FAILED" and r.execution == "NOT_EXECUTED":
                if _isna(r.null_calibration_id) or r.null_calibration_id not in run.cal_ix.index \
                        or run.cal_ix.loc[r.null_calibration_id].status != "CALIBRATION_FAILED":
                    raise Refused("INCOHERENT_CALIBRATION_FAILURE",
                                  f"{r.metric_id}: failed aggregate does not reference a CALIBRATION_FAILED "
                                  f"calibration {r.null_calibration_id!r}")
                c["calfail_agg"] += 1
            else:
                raise Refused("UNEXPECTED_ROW_STATE", f"aggregates {r.metric_id}: {kind}/{r.status}/{r.execution}")
        elif kind in ("GAUSS_FORMULA_CHECK", "GAUSS_PROXY_CHECK_T7"):
            if r.status != "OK" or r.execution != "EXECUTED":
                raise Refused("UNEXPECTED_ROW_STATE", f"aggregates {r.metric_id}: {kind}/{r.status}/{r.execution}")
            c["gauss_check"] += 1
        elif kind == "REAL_EVENT_PATH":
            c["real_path"] += 1
        else:
            raise Refused("UNEXPECTED_ROW_STATE", f"aggregates {r.metric_id}: unknown metric_kind {kind!r}")
    for r in cal.itertuples(index=False):
        if r.status == "OK" and r.execution == "EXECUTED":
            c["cal_ok"] += 1
        elif r.status == "CALIBRATION_FAILED" and r.execution == "EXECUTED":
            c["cal_failed"] += 1
        else:
            raise Refused("UNEXPECTED_ROW_STATE",
                          f"calibration {r.null_calibration_id}: {r.status}/{r.execution}")
    agg_ids = set(agg["metric_id"].dropna())
    cal_ids = set(cal["null_calibration_id"].dropna())
    expected = {}
    for r in cal.itertuples(index=False):
        if r.status == "OK" and r.execution == "EXECUTED":
            expected[(r.null_calibration_id, "calibration")] = int(r.n_cal)
    for r in agg.itertuples(index=False):
        if r.metric_kind in ("ALT_RMST", "HOLDOUT_NULL_FPR") and r.status == "OK" and r.execution == "EXECUTED":
            expected[(r.metric_id, "alternative" if r.metric_kind == "ALT_RMST" else "holdout_null")] = int(r.n)
    observed = {}
    for (gid, role), n in tri.groupby(["group_id", "role"]).size().items():
        if role == "real_path":
            raise Refused("REAL_PATH_TRIALS", f"trials hold a real_path group {gid}")
        c[f"trials_{role}"] = c.get(f"trials_{role}", 0) + int(n)
        observed[(gid, role)] = int(n)
        if gid in cal_ids:
            crow = run.cal_ix.loc[gid]
            if crow.status != "OK" or role != "calibration" or int(n) != int(crow.n_cal):
                raise Refused("TRIALS_COUNT_MISMATCH",
                              f"calibration {gid}: {n} {role} trials, want {crow.n_cal} calibration")
        elif gid in agg_ids:
            a = run.agg_ix.loc[gid]
            if a.metric_kind not in ("ALT_RMST", "HOLDOUT_NULL_FPR") or _isna(a.n):
                raise Refused("TRIALS_COUNT_MISMATCH", f"{gid}: trials on a {a.metric_kind} aggregate")
            want_role = "alternative" if a.metric_kind == "ALT_RMST" else "holdout_null"
            if role != want_role or int(n) != int(a.n):
                raise Refused("TRIALS_COUNT_MISMATCH", f"{gid}: {n} {role} trials, want {a.n} {want_role}")
        else:
            raise Refused("ORPHAN_TRIALS", f"trial group {gid} matches no metric_id nor null_calibration_id")
    for key, want in expected.items():
        got = observed.get(key, 0)
        if got != want:
            code = "TRIALS_COUNT_MISMATCH" if key in observed else "TRIALS_GROUP_MISSING"
            raise Refused(code, f"trial group {key}: expected {want} trials, observed {got}")
    validate_spectra(run)
    run.counters = c
    return run


def validate_spectra(run):
    """§3.9: per (dataset_id, basis_hash), k = 1..N, lambda_lw positive non-increasing, cpv_lw non-decreasing with cpv_lw[nmax] <= 1, mp/kaiser/cpv90 fields coherent."""
    spe = run.frames["spectra"]
    nmax = run.nmax
    for (ds, bh), g in spe.groupby(["dataset_id", "basis_hash"]):
        g = g.sort_values("k")
        ks = [int(k) for k in g["k"]]
        if ks != list(range(1, len(ks) + 1)):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: k is not 1..N")
        lam = [float(v) for v in g["lambda_lw"]]
        cpv = [float(v) for v in g["cpv_lw"]]
        if any(not l > 0.0 for l in lam) or any(lam[i] < lam[i + 1] for i in range(len(lam) - 1)):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: lambda_lw not positive non-increasing")
        if any(cpv[i] > cpv[i + 1] for i in range(len(cpv) - 1)):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: cpv_lw not non-decreasing")
        if cpv[nmax - 1] > 1.0:
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: cpv_lw[{nmax}] = {cpv[nmax - 1]} > 1")
        if sum(1 for v in g["mp_above"] if _truthy(v)) != int(g["mp_count"].iloc[0]) \
                or sum(1 for v in g["kaiser_ge1"] if _truthy(v)) != int(g["kaiser_count"].iloc[0]):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: mp_count/kaiser_count disagree with the flags")
        k90 = next((k for k, cp in zip(ks, cpv) if cp >= 0.9), None)
        if k90 != int(g["cpv90_k_full"].iloc[0]):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: cpv90_k_full is {g['cpv90_k_full'].iloc[0]}, recomputed {k90}")
        if str(g["cpv90_status"].iloc[0]) != pdb.cpv90_status(k90, nmax):
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}/{bh}: cpv90_status incoherent")
    return run


class Tables:
    """Built tables: rows[table] = row dicts (None = NA), cols[table] = [(name, kind)], lineage = per-cell provenance rows, blocks[table] = Markdown header metadata."""

    def __init__(self):
        self.rows = {}
        self.cols = {}
        self.lineage = []
        self.blocks = {}


def _lin_add(tables, table, row_id, column, kind, source_file="", source_key="", source_column="", formula="",
             inputs=""):
    tables.lineage.append({"table": table, "row_id": row_id, "column": column, "kind": kind,
                           "source_file": source_file, "source_key": source_key, "source_column": source_column,
                           "formula": formula, "inputs": inputs})


T1_COLS = [("table", "str"), ("row_id", "str"), ("block_id", "str"), ("k", "int"), ("d", "int"),
           ("dataset_id", "str"), ("cohort_id", "str"), ("event_id", "str"), ("detector_family", "str"),
           ("lambda_lw", "float"), ("cpv_lw", "float"), ("criteria", "str"), ("mp_count", "int"), ("mp_edge", "float"),
           ("kaiser_count", "int"), ("cpv90_k_full", "int"), ("cpv90_status", "str"),
           ("rmst", "float"), ("rmst_lo", "float"), ("rmst_hi", "float"), ("det_rate", "float"),
           ("censored_share", "float"), ("n_alt", "int"),
           ("fpr_test_null", "float"), ("fpr_lo", "float"), ("fpr_hi", "float"), ("n_eval", "int"),
           ("fpr_calibration", "float"), ("n_cal", "int"), ("predictive_bound", "float"), ("target_fpr", "float"),
           ("threshold_rule", "str"), ("guarantee_basis", "str"),
           ("selection_id", "str"), ("metric_id", "str"), ("null_metric_id", "str"), ("null_id", "str"),
           ("null_calibration_id", "str"), ("calibration_hash", "str"), ("basis_hash", "str"), ("split_hash", "str"),
           ("config_hash", "str"), ("seed", "int"),
           ("source_kind", "str"), ("claim_scope", "str"), ("status", "str"), ("execution", "str"), ("na_reason", "str")]

T1_SEL_COLS = ("k", "d", "dataset_id", "cohort_id", "event_id", "detector_family", "selection_id", "metric_id",
               "null_metric_id", "null_id", "null_calibration_id", "calibration_hash", "basis_hash", "split_hash",
               "config_hash", "seed", "source_kind", "claim_scope", "status", "execution")
T1_SPE_COLS = ("lambda_lw", "cpv_lw", "mp_count", "mp_edge", "kaiser_count", "cpv90_k_full", "cpv90_status")
T1_ALT_COLS = ("rmst", "rmst_lo", "rmst_hi", "det_rate", "censored_share")
T1_HOLD_MAP = {"fpr_test_null": "fpr", "fpr_lo": "fpr_lo", "fpr_hi": "fpr_hi"}
T1_CAL_MAP = {"fpr_calibration": "calibration_fraction", "n_cal": "n_cal", "predictive_bound": "predictive_bound",
              "threshold_rule": "threshold_rule", "guarantee_basis": "guarantee_basis"}
T1_NA_MEASURES = ("rmst", "rmst_lo", "rmst_hi", "det_rate", "censored_share", "n_alt", "fpr_test_null", "fpr_lo",
                  "fpr_hi", "n_eval", "target_fpr")


def build_t1(run, dataset=None, scenario=None, family=None):
    """Tableau_PCA_1: one row per (E1 BASELINE_PREFIX block, k = 1..nmax); prefix measures are the source objects."""
    t = Tables()
    t.cols["T1"] = T1_COLS
    sel = run.frames["selection"]
    e1 = sel[(sel["experiment"] == "E1") & (sel["method"] == "BASELINE_PREFIX")]
    keys = []
    for r in e1.itertuples(index=False):
        key = (r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id, r.detector_family)
        if key not in keys:
            keys.append(key)
    keys.sort(key=lambda k: (k[0], k[1] or "", k[2], k[3]))
    rows, blocks = [], []
    for key in keys:
        ds, cohort, ev, fam = key
        if (dataset and ds != dataset) or (scenario and ev != scenario) or (family and fam != family):
            continue
        grp = sorted((r for r in e1.itertuples(index=False)
                      if (r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id,
                          r.detector_family) == key), key=lambda r: int(r.k))
        if [int(r.k) for r in grp] != list(range(1, run.nmax + 1)):
            raise Refused("T1_BLOCK_INCOMPLETE", f"T1 block {key}: k is not 1..{run.nmax}")
        bid = pdb.sha16({"table": "T1", "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                         "detector_family": fam, "objective_kind": "NONE"})
        for r in grp:
            k = int(r.k)
            rid = f"T1:{bid}:{k}"
            row = {}

            def put(col, value, kind, src_file="", src_key="", src_col="", formula="", inputs=""):
                row[col] = None if _isna(value) else value
                _lin_add(t, "T1", rid, col, kind, src_file, src_key, src_col, formula, inputs)

            put("table", "T1", "RULE", formula="literal 'T1'")
            put("row_id", rid, "RULE", formula="f'T1:{block_id}:{k}'")
            put("block_id", bid, "FORMULA",
                formula="pdb.sha16({table,dataset_id,cohort_id,event_id,detector_family,objective_kind:'NONE'})",
                inputs=pdb.canon({"table": "T1", "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                                  "detector_family": fam, "objective_kind": "NONE"}))
            sel_key = pdb.canon({"selection_id": r.selection_id, "experiment": r.experiment, "row_kind": r.row_kind,
                                 "d": _norm(r.d)})
            for col in T1_SEL_COLS:
                put(col, getattr(r, col), "SOURCE", "selection.csv", sel_key, col)
            sp = run.spe_ix.get((ds, r.basis_hash, k))
            if sp is not None:
                sp_key = pdb.canon({"dataset_id": ds, "basis_hash": r.basis_hash, "k": k})
                for col in T1_SPE_COLS:
                    put(col, getattr(sp, col), "SOURCE", "spectra.csv", sp_key, col)
                parts = []
                if k == int(sp.mp_count):
                    parts.append("MP (corr.)")
                if int(sp.cpv90_k_full) <= run.nmax and k == int(sp.cpv90_k_full):
                    parts.append("CPV 90 %")
                if int(sp.kaiser_count) <= run.nmax and k == int(sp.kaiser_count):
                    parts.append("Kaiser corr. λ≥1")
                put("criteria", " ; ".join(parts) if parts else "—", "FORMULA",
                    formula="markers at k==mp_count, cpv90_k_full<=nmax, kaiser_count<=nmax; else '—'; never 'λ<1'",
                    inputs=sp_key)
            else:
                for col in T1_SPE_COLS:
                    put(col, None, "RULE", formula="NA: no spectra row for (dataset_id, basis_hash, k) in this run")
                put("criteria", None, "RULE", formula="NA with the spectra cells (REAL_NOT_RUN in a smoke run)")
            if not _isna(r.null_metric_id):
                a = run.agg_ix.loc[r.metric_id]
                a_key = pdb.canon({"metric_id": r.metric_id})
                for col in T1_ALT_COLS:
                    put(col, getattr(a, col), "SOURCE", "aggregates.csv", a_key, col)
                put("n_alt", a.n, "SOURCE", "aggregates.csv", a_key, "n")
                h = run.agg_ix.loc[r.null_metric_id]
                h_key = pdb.canon({"metric_id": r.null_metric_id})
                for col, src in T1_HOLD_MAP.items():
                    put(col, getattr(h, src), "SOURCE", "aggregates.csv", h_key, src)
                put("n_eval", h.n, "SOURCE", "aggregates.csv", h_key, "n")
                put("target_fpr", h.target_fpr, "SOURCE", "aggregates.csv", h_key, "target_fpr")
            else:
                for col in T1_NA_MEASURES:
                    put(col, None, "RULE", formula=f"NA: selection row not executed (status {r.status})")
            if not _isna(r.null_calibration_id):
                c = run.cal_ix.loc[r.null_calibration_id]
                c_key = pdb.canon({"null_calibration_id": r.null_calibration_id})
                for col, src in T1_CAL_MAP.items():
                    put(col, getattr(c, src), "SOURCE", "calibration.csv", c_key, src)
            else:
                for col in T1_CAL_MAP:
                    put(col, None, "RULE", formula="NA: no calibration referenced (smoke real rows)")
            put("na_reason", r.status if r.status != "OK" else None, "SOURCE", "selection.csv", sel_key, "status",
                formula="status when not OK, else NA")
            rows.append(row)
        blocks.append({"block_id": bid, "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                       "detector_family": fam, "n_rows": len(grp)})
    t.rows["T1"] = rows
    t.blocks["T1"] = blocks
    return t


def mean_q_vectors(run):
    """H3 recipe: q = pdb.q_plugin(beta_nonzero, lambda_lw[:nmax]) per (synthetic dataset, mean event), from manifest beta_nonzero (0 elsewhere) and spectra lambda_lw."""
    nmax = run.nmax
    out = {}
    for ds, bg in run.manifest["synthetic"]["backgrounds"].items():
        bhs = run.frames["selection"].loc[run.frames["selection"]["dataset_id"] == ds, "basis_hash"].dropna().unique()
        if len(bhs) != 1:
            raise Refused("SPECTRA_INCONSISTENT", f"{ds}: {len(bhs)} distinct basis hashes")
        bh = bhs[0]
        lam = np.array([float(run.spe_ix[(ds, bh, k)].lambda_lw) for k in range(1, nmax + 1)])
        for ev, sc in bg["scenarios"].items():
            if "beta_nonzero" not in sc:
                continue
            beta = np.zeros(nmax)
            for a, v in sc["beta_nonzero"].items():
                beta[int(a) - 1] = float(v)
            out[(ds, ev)] = pdb.q_plugin(beta, lam)
    return out


def _validate_lineage_controls(run):
    """§3.9: L16 (E2 prefix == E1), L17 (E3 oracle copies == E2 at k = nmax), L18 (H3 q sums and rank orders)."""
    sel = run.frames["selection"]
    nmax = run.nmax
    ix = {}
    for r in sel.itertuples(index=False):
        ix[(r.selection_id, r.method, r.row_kind, _norm(r.d), r.experiment)] = r
    cols = [c for c in sel.columns if c != "experiment"]
    for r in sel.itertuples(index=False):
        if r.experiment == "E2" and r.method == "BASELINE_PREFIX":
            e1 = ix.get((r.selection_id, r.method, r.row_kind, _norm(r.d), "E1"))
            if e1 is None or any(_norm(getattr(r, c)) != _norm(getattr(e1, c)) for c in cols):
                raise Refused("L16_PREFIX_IDENTITY",
                              f"E2 prefix {r.selection_id} d={_norm(r.d)} differs from its E1 row")
        if r.experiment == "E3" and r.row_kind == "SELECTED" and r.method in ("ORACLE_Q_MIX", "COV_JOINT_ORACLE"):
            if int(r.reservoir_k) != nmax:
                raise Refused("L17_E3_COPY", f"E3 {r.method} at reservoir_k={r.reservoir_k}, expected {nmax}")
            e2 = ix.get((r.selection_id, r.method, r.row_kind, _norm(r.d), "E2"))
            if e2 is None or any(_norm(getattr(r, c)) != _norm(getattr(e2, c)) for c in cols):
                raise Refused("L17_E3_COPY", f"E3 {r.method} {r.selection_id} differs from its E2 copy at k={nmax}")
    qs = mean_q_vectors(run)
    for r in sel.itertuples(index=False):
        key = (r.dataset_id, r.event_id)
        if r.detector_family != pdb.MEAN or key not in qs:
            continue
        q = qs[key]
        if not _isna(r.S) and not _isna(r.I_plugin_lw):
            S0 = [a - 1 for a in _parse_S(r.S, nmax)]
            if float(q[S0].sum()) != float(r.I_plugin_lw):
                raise Refused("L18_Q_CONTROL", f"{r.selection_id} {r.experiment}: sum(q[S]) != I_plugin_lw")
        if not _isna(r.rank_order):
            k = int(r.reservoir_k)
            order = sorted(range(k), key=lambda j: (-q[j], j))
            if json.loads(r.rank_order) != [j + 1 for j in order]:
                raise Refused("L18_Q_CONTROL", f"{r.selection_id} {r.experiment}: rank_order mismatch at k={k}")
    return run


def _h_exact(v):
    """True iff v is present and numerically exactly HORIZON (no truncation, no NA)."""
    if _isna(v):
        return False
    try:
        return float(v) == float(HORIZON)
    except (TypeError, ValueError):
        return False


def validate_horizon(run):
    """§3.7 (H14): manifest/aggregate/calibration H present and exactly 250, every ALT_RMST ONSET_ALIGNED."""
    if not _h_exact(run.manifest["config"].get("H")):
        raise Refused("HORIZON_INCOMPATIBLE",
                      f"manifest config H = {run.manifest['config'].get('H')!r}, must be exactly {HORIZON}")
    for r in run.frames["aggregates"].itertuples(index=False):
        if r.metric_kind in ("ALT_RMST", "HOLDOUT_NULL_FPR", "REAL_EVENT_PATH") and not _h_exact(r.H):
            raise Refused("HORIZON_INCOMPATIBLE",
                          f"aggregates {r.metric_id}: H = {r.H!r}, must be present and exactly {HORIZON}")
        if r.metric_kind == "ALT_RMST" and r.time_origin != pdb.ONSET_ALIGNED:
            raise Refused("HORIZON_INCOMPATIBLE", f"aggregates {r.metric_id}: ALT time_origin {r.time_origin}")
    for r in run.frames["calibration"].itertuples(index=False):
        if not _h_exact(r.H):
            raise Refused("HORIZON_INCOMPATIBLE",
                          f"calibration {r.null_calibration_id}: H = {r.H!r}, must be present and exactly {HORIZON}")
    return run


def validate_real_contract(run):
    """§3.8 (H15): under /2 every REAL_EVENT_PATH is NOT_EXECUTED with all metric fields NA (whatever pre_j4.frozen_json_present), both cohorts present, claim scopes checked, id spaces disjoint."""
    sel = run.frames["selection"]
    agg = run.frames["aggregates"]
    real_agg = agg[agg["metric_kind"] == "REAL_EVENT_PATH"]
    frozen = run.manifest.get("pre_j4", {}).get("frozen_json_present")
    for r in real_agg.itertuples(index=False):
        bad = [f for f in METRIC_FIELDS if not _isna(getattr(r, f))]
        if r.execution != "NOT_EXECUTED" or bad:
            raise Refused("REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2",
                          f"{r.metric_id}: execution={r.execution}, numeric fields {bad}; "
                          f"frozen_json_present={frozen} authorizes nothing under schema /2")
    cohorts = run.manifest["real"]["cohorts"]
    real_sel = sel[sel["dataset_id"] == "D3_239"]
    present = set(real_sel["cohort_id"].dropna().unique())
    if present != set(cohorts):
        raise Refused("COHORT_MISSING", f"cohorts present {sorted(present)} != declared {sorted(cohorts)}")
    ids = {}
    for c, spec in cohorts.items():
        rows = real_sel[real_sel["cohort_id"] == c]
        if set(rows["claim_scope"].dropna().unique()) != {spec["claim_scope"]}:
            raise Refused("COHORT_MISSING", f"{c}: claim_scope differs from the manifest")
        if c == "cohort_standard_embargo" and set(rows.loc[rows["event_id"] == "COVID_2020", "status"].unique()) != {
                "NOT_EVALUABLE_STANDARD_SPLIT"}:
            raise Refused("COHORT_MISSING", "standard cohort COVID_2020 is not NOT_EVALUABLE_STANDARD_SPLIT")
        ids[c] = {f: set(rows[f].dropna().unique())
                  for f in ("selection_id", "metric_id", "split_hash", "null_calibration_id")}
    c0, c1 = sorted(cohorts)
    for f in ("selection_id", "metric_id", "split_hash", "null_calibration_id"):
        if ids[c0][f] & ids[c1][f]:
            raise Refused("COHORT_ID_SHARED", f"{f} shared between {c0} and {c1}: "
                                               f"{sorted(ids[c0][f] & ids[c1][f])[:3]}")
    agg_status = real_agg.set_index("metric_id")["status"]
    for r in real_sel.itertuples(index=False):
        if agg_status[r.metric_id] != r.status:
            raise Refused("REAL_STATUS_MISMATCH", f"{r.metric_id}: aggregate {agg_status[r.metric_id]} vs selection {r.status}")
    return run


def validate_calibration_failures(run):
    """§3.6: a CALIBRATION_FAILED artefact is coherent iff the five conditions hold, else refused (never masked by NA); the cascade is synthetic-only, a failed real D6 calibration keeps the blocked real rows."""
    cal, agg, sel, tri, iss = (run.frames[n] for n in ("calibration", "aggregates", "selection", "trials", "issues"))
    for c in cal[cal["status"] == "CALIBRATION_FAILED"].itertuples(index=False):
        ncid = c.null_calibration_id
        if c.execution != "EXECUTED" or _isna(c.n_cal) or _isna(c.maxima_sha256) or any(
                not _isna(getattr(c, f))
                for f in ("rank_r", "threshold", "calibration_alarms", "calibration_fraction", "predictive_bound",
                          "calibration_hash")):
            raise Refused("INCOHERENT_CALIBRATION_FAILURE", f"{ncid}: condition 1 (failed-row fields) violated")
        is_d6 = c.null_kind == "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS"
        rows = agg[(agg["null_calibration_id"] == ncid) & (agg["metric_kind"] != "REAL_EVENT_PATH")]
        for a in rows.itertuples(index=False):
            if a.metric_kind not in ("ALT_RMST", "HOLDOUT_NULL_FPR") or a.status != "CALIBRATION_FAILED" \
                    or a.execution != "NOT_EXECUTED" or _isna(a.metric_id) \
                    or any(not _isna(getattr(a, f)) for f in METRIC_FIELDS):
                raise Refused("INCOHERENT_CALIBRATION_FAILURE",
                              f"{a.metric_id}: condition 2 (aggregate keeps an executed/numeric state)")
        mids = set(rows["metric_id"].dropna())
        if len(tri[(tri["group_id"] == ncid) | tri["group_id"].isin(mids)]):
            raise Refused("INCOHERENT_CALIBRATION_FAILURE", f"{ncid}: condition 3 (trials kept) violated")
        srows = sel[(sel["null_calibration_id"] == ncid) | sel["metric_id"].isin(mids)]
        srows = srows[srows["dataset_id"] != "D3_239"]
        if not is_d6 and len(srows) == 0:
            raise Refused("INCOHERENT_CALIBRATION_FAILURE", f"{ncid}: condition 4 (no synthetic selection row)")
        if any(s.status != "CALIBRATION_FAILED" or s.execution != "NOT_EXECUTED"
               for s in srows.itertuples(index=False)):
            raise Refused("INCOHERENT_CALIBRATION_FAILURE", f"{ncid}: condition 4 (selection cascade) violated")
        if is_d6:
            rsel = sel[(sel["null_calibration_id"] == ncid) & (sel["dataset_id"] == "D3_239")]
            if any(s.status not in REAL_STATUSES or s.execution != "NOT_EXECUTED"
                   for s in rsel.itertuples(index=False)):
                raise Refused("INCOHERENT_CALIBRATION_FAILURE",
                              f"{ncid}: a real D6 row lost its blocked runner status (GO precision 1)")
        if not bool((iss["code"] == "CALIBRATION_FAILED").any()):
            raise Refused("INCOHERENT_CALIBRATION_FAILURE", f"{ncid}: condition 5 (no CALIBRATION_FAILED issue)")
    return run


T2_COLS = [("table", "str"), ("row_id", "str"), ("block_id", "str"), ("k", "int"),
           ("dataset_id", "str"), ("cohort_id", "str"), ("event_id", "str"), ("detector_family", "str"),
           ("objective_kind", "str"), ("block_family", "str"),
           ("lambda_lw", "float"), ("q_k", "float"), ("q_info_type", "str"), ("q_source", "str"),
           ("I_marginal_cum_prefix", "float"),
           ("I_prefix", "float"), ("V_prefix", "float"), ("V_prefix_meaning", "str"),
           ("rmst_prefix", "float"), ("rmst_prefix_lo", "float"), ("rmst_prefix_hi", "float"),
           ("fpr_prefix", "float"), ("fpr_prefix_lo", "float"), ("fpr_prefix_hi", "float"),
           ("metric_id_prefix", "str"), ("null_metric_id_prefix", "str"), ("selection_id_prefix", "str"),
           ("S_star", "str"), ("d_star", "int"), ("I_star", "float"), ("V_star", "float"), ("V_star_meaning", "str"),
           ("rmst_selected", "float"), ("rmst_selected_lo", "float"), ("rmst_selected_hi", "float"),
           ("fpr_selected", "float"), ("fpr_selected_lo", "float"), ("fpr_selected_hi", "float"),
           ("metric_id_subset", "str"), ("null_metric_id_subset", "str"), ("selection_id_subset", "str"),
           ("I_pop_joint_prefix", "float"), ("I_pop_joint_star", "float"), ("pop_offdiag_max_star", "float"),
           ("selector_kind", "str"), ("selection_exact", "str"), ("tie_broken", "str"), ("oracle_input", "str"),
           ("claim_flag", "str"), ("info_kind", "str"), ("status_prefix", "str"), ("status_subset", "str"),
           ("null_calibration_id", "str"), ("null_calibration_id_subset", "str"), ("calibration_hash", "str"),
           ("basis_hash", "str"), ("split_hash", "str"), ("config_hash", "str"), ("seed", "int"),
           ("n_alt", "int"), ("n_eval", "int"), ("n_cal", "int"),
           ("source_kind", "str"), ("claim_scope", "str"), ("na_reason", "str")]

T2_PREFIX_IDS = ("dataset_id", "cohort_id", "event_id", "detector_family", "objective_kind")
T2_COMPARABILITY = ("dataset_id", "cohort_id", "split_hash", "event_window_id", "detector_family", "null_id",
                    "basis_hash")


def build_t2(run, t, dataset=None, scenario=None, family=None):
    """Tableau_PCA_2: prefix P_k (the exact T1 row objects) against the E2-selected S*_k, per block + objective."""
    nmax = run.nmax
    t.cols["T2"] = T2_COLS
    sel = run.frames["selection"]
    t1_index = {(r["dataset_id"], r["cohort_id"], r["event_id"], r["detector_family"], r["k"]): r
                for r in t.rows["T1"]}
    e1_index = {}
    for r in sel[(sel["experiment"] == "E1") & (sel["method"] == "BASELINE_PREFIX")].itertuples(index=False):
        e1_index[(r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id, r.detector_family,
                  int(r.k))] = r
    e2 = sel[(sel["experiment"] == "E2") & (sel["row_kind"] == "SELECTED") & (sel["method"] != "BASELINE_PREFIX")]
    keys = []
    for r in e2.itertuples(index=False):
        key = (r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id, r.detector_family,
               r.objective_kind)
        if key not in keys:
            keys.append(key)
    keys.sort(key=lambda k: (k[0], k[1] or "", k[2], k[3], k[4]))
    qs = mean_q_vectors(run)
    rows, blocks = [], []
    for key in keys:
        ds, cohort, ev, fam, obj = key
        if (dataset and ds != dataset) or (scenario and ev != scenario) or (family and fam != family):
            continue
        grp = sorted((r for r in e2.itertuples(index=False)
                      if (r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id, r.detector_family,
                          r.objective_kind) == key), key=lambda r: int(r.reservoir_k))
        if [int(r.reservoir_k) for r in grp] != list(range(1, nmax + 1)):
            raise Refused("T2_BLOCK_INCOMPLETE", f"T2 block {key}: reservoir_k is not 1..{nmax}")
        bid = pdb.sha16({"table": "T2", "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                         "detector_family": fam, "objective_kind": obj})
        block_family = "MEAN" if fam == pdb.MEAN else "COV"
        mix = obj in ("MEAN_MIX_FLUID_SURROGATE", "COV_JOINT_MIX_HEURISTIC")
        meaning = ("MEAN_MIX_FLUID_SURROGATE" if block_family == "MEAN" else "COV_HEURISTIC_SURROGATE")
        for r in grp:
            k = int(r.reservoir_k)
            rid = f"T2:{bid}:{k}"
            row = {}

            def put(col, value, kind, src_file="", src_key="", src_col="", formula="", inputs=""):
                row[col] = None if _isna(value) else value
                _lin_add(t, "T2", rid, col, kind, src_file, src_key, src_col, formula, inputs)

            put("table", "T2", "RULE", formula="literal 'T2'")
            put("row_id", rid, "RULE", formula="f'T2:{block_id}:{k}'")
            put("block_id", bid, "FORMULA",
                formula="pdb.sha16({table,dataset_id,cohort_id,event_id,detector_family,objective_kind})",
                inputs=pdb.canon({"table": "T2", "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                                  "detector_family": fam, "objective_kind": obj}))
            put("k", k, "SOURCE", "selection.csv",
                pdb.canon({"selection_id": r.selection_id, "experiment": r.experiment, "row_kind": r.row_kind,
                           "d": _norm(r.d)}), "reservoir_k")
            put("block_family", block_family, "RULE", formula="'MEAN' if detector_family == MEAN else 'COV'")
            r1 = e1_index[(ds, cohort, ev, fam, k)]
            p = t1_index[(ds, cohort, ev, fam, k)]
            sel_key = pdb.canon({"selection_id": r.selection_id, "experiment": r.experiment, "row_kind": r.row_kind,
                                 "d": _norm(r.d)})
            sel1_key = pdb.canon({"selection_id": r1.selection_id, "experiment": r1.experiment,
                                  "row_kind": r1.row_kind, "d": _norm(r1.d)})
            for f in T2_COMPARABILITY:
                if _norm(getattr(r, f)) != _norm(getattr(r1, f)):
                    raise Refused("PREFIX_NOT_COMPARABLE", f"T2 block {key} k={k}: {f} differs prefix vs subset")
            if not (_isna(r.metric_id) or _isna(r1.metric_id) or _isna(r.null_metric_id) or _isna(r1.null_metric_id)):
                a1, a2 = run.agg_ix.loc[r1.metric_id], run.agg_ix.loc[r.metric_id]
                h1, h2 = run.agg_ix.loc[r1.null_metric_id], run.agg_ix.loc[r.null_metric_id]
                if not (_isna(a1.n) or _isna(a2.n) or _isna(h1.n) or _isna(h2.n)):
                    for a, b, what in ((a1, a2, "ALT"), (h1, h2, "HOLDOUT")):
                        if _norm(a.H) != _norm(b.H) or int(a.n) != int(b.n) or (what == "ALT" and a.time_origin != b.time_origin):
                            raise Refused("PREFIX_NOT_COMPARABLE",
                                          f"T2 block {key} k={k}: {what} H/time_origin/n differ")
            for col in T2_PREFIX_IDS:
                put(col, getattr(r, col), "SOURCE", "selection.csv", sel_key, col)
            put("lambda_lw", p["lambda_lw"], "FORMULA", formula="identity with the T1 row cell lambda_lw",
                inputs=pdb.canon({"t1_row_id": p["row_id"], "column": "lambda_lw"}))
            if block_family == "MEAN" and (ds, ev) in qs:
                q = qs[(ds, ev)]
                put("q_k", float(q[k - 1]), "FORMULA", formula="pdb.q_plugin(beta_nonzero, lambda_lw[:nmax])[k-1]",
                    inputs=pdb.canon({"beta_nonzero": f"manifest.json synthetic.backgrounds.{ds}.scenarios.{ev}.beta_nonzero",
                                      "lambda_lw": f"spectra.csv ({ds}, basis_hash, k=1..{nmax})"}))
                put("q_info_type", "MEAN_GAUSSIAN_PROXY", "RULE", formula="plug-in LW q on the two backgrounds")
                put("q_source", "FORMULA_Q_PLUGIN", "RULE", formula="H3 recipe")
                put("I_marginal_cum_prefix", None, "RULE", formula="NA: covariance diagnostic only")
            elif block_family == "COV":
                put("q_k", None, "RULE", formula="NA: per-axis covariance q is not exported by schema /2")
                put("q_info_type", "COV_GAUSSIAN_MARGINAL_PROXY", "RULE",
                    formula="type of the adjacent marginal diagnostic, never a joint KL")
                put("q_source", "NOT_EXPORTED_SCHEMA_2", "RULE", formula="NA reason")
                put("I_marginal_cum_prefix", r1.I_cov_marginal_sum, "SOURCE", "selection.csv", sel1_key,
                    "I_cov_marginal_sum")
            else:
                put("q_k", None, "RULE", formula="NA: real block, no synthetic beta")
                put("q_info_type", None, "RULE", formula="NA")
                put("q_source", None, "RULE", formula="NA")
                put("I_marginal_cum_prefix", None, "RULE", formula="NA")
            put("I_prefix", r1.I_objective, "SOURCE", "selection.csv", sel1_key, "I_objective")
            put("V_prefix", r1.V_mix if mix else r1.V_affine, "SOURCE", "selection.csv", sel1_key,
                "V_mix" if mix else "V_affine")
            put("V_prefix_meaning", meaning if ds != "D3_239" else None, "RULE",
                formula="MEAN_MIX_FLUID_SURROGATE (mean) / COV_HEURISTIC_SURROGATE (cov); NA real")
            for col, src in (("rmst_prefix", "rmst"), ("rmst_prefix_lo", "rmst_lo"), ("rmst_prefix_hi", "rmst_hi"),
                             ("fpr_prefix", "fpr_test_null"), ("fpr_prefix_lo", "fpr_lo"),
                             ("fpr_prefix_hi", "fpr_hi")):
                put(col, p[src], "FORMULA", formula=f"identity with the T1 row cell {src} (same object)",
                    inputs=pdb.canon({"t1_row_id": p["row_id"], "column": src}))
            put("metric_id_prefix", p["metric_id"], "FORMULA", formula="identity with the T1 row cell metric_id",
                inputs=pdb.canon({"t1_row_id": p["row_id"], "column": "metric_id"}))
            put("null_metric_id_prefix", p["null_metric_id"], "FORMULA",
                formula="identity with the T1 row cell null_metric_id",
                inputs=pdb.canon({"t1_row_id": p["row_id"], "column": "null_metric_id"}))
            put("selection_id_prefix", r1.selection_id, "SOURCE", "selection.csv", sel1_key, "selection_id")
            sub_key = sel_key
            for col, src in (("S_star", "S"), ("d_star", "d"), ("I_star", "I_objective"),
                             ("V_star", "V_mix" if mix else "V_affine"),
                             ("selection_exact", "selection_exact"), ("tie_broken", "tie_broken"),
                             ("oracle_input", "oracle_input"), ("claim_flag", "claim_flag"), ("info_kind", "info_kind"),
                             ("selector_kind", "method")):
                put(col, getattr(r, src), "SOURCE", "selection.csv", sub_key, src)
            put("V_star_meaning", meaning if ds != "D3_239" else None, "RULE", formula="same rule as V_prefix")
            put("I_pop_joint_prefix", r1.I_pop_joint, "SOURCE", "selection.csv", sel1_key, "I_pop_joint")
            put("I_pop_joint_star", r.I_pop_joint, "SOURCE", "selection.csv", sub_key, "I_pop_joint")
            put("pop_offdiag_max_star", r.pop_offdiag_max, "SOURCE", "selection.csv", sub_key, "pop_offdiag_max")
            if not _isna(r.null_metric_id):
                a2 = run.agg_ix.loc[r.metric_id]
                h2 = run.agg_ix.loc[r.null_metric_id]
                a2_key = pdb.canon({"metric_id": r.metric_id})
                h2_key = pdb.canon({"metric_id": r.null_metric_id})
                for col, src in (("rmst_selected", "rmst"), ("rmst_selected_lo", "rmst_lo"),
                                 ("rmst_selected_hi", "rmst_hi")):
                    put(col, getattr(a2, src), "SOURCE", "aggregates.csv", a2_key, src)
                for col, src in (("fpr_selected", "fpr"), ("fpr_selected_lo", "fpr_lo"),
                                 ("fpr_selected_hi", "fpr_hi")):
                    put(col, getattr(h2, src), "SOURCE", "aggregates.csv", h2_key, src)
                put("metric_id_subset", r.metric_id, "SOURCE", "selection.csv", sub_key, "metric_id")
                put("null_metric_id_subset", r.null_metric_id, "SOURCE", "selection.csv", sub_key, "null_metric_id")
                put("selection_id_subset", r.selection_id, "SOURCE", "selection.csv", sub_key, "selection_id")
                put("n_alt", a2.n, "SOURCE", "aggregates.csv", a2_key, "n")
                put("n_eval", h2.n, "SOURCE", "aggregates.csv", h2_key, "n")
            else:
                for col in ("rmst_selected", "rmst_selected_lo", "rmst_selected_hi", "fpr_selected",
                            "fpr_selected_lo", "fpr_selected_hi", "n_alt", "n_eval"):
                    put(col, None, "RULE", formula=f"NA: subset row not executed (status {r.status})")
                for col, src in (("metric_id_subset", "metric_id"), ("null_metric_id_subset", "null_metric_id"),
                                 ("selection_id_subset", "selection_id")):
                    put(col, getattr(r, src), "SOURCE", "selection.csv", sub_key, src)
            put("status_prefix", r1.status, "SOURCE", "selection.csv", sel1_key, "status")
            put("status_subset", r.status, "SOURCE", "selection.csv", sub_key, "status")
            for col in ("null_calibration_id", "calibration_hash", "basis_hash", "split_hash", "config_hash", "seed",
                        "source_kind", "claim_scope"):
                put(col, getattr(r1, col), "SOURCE", "selection.csv", sel1_key, col)
            put("null_calibration_id_subset", r.null_calibration_id, "SOURCE", "selection.csv", sub_key,
                "null_calibration_id")
            if not _isna(r1.null_calibration_id):
                c1 = run.cal_ix.loc[r1.null_calibration_id]
                put("n_cal", c1.n_cal, "SOURCE", "calibration.csv",
                    pdb.canon({"null_calibration_id": r1.null_calibration_id}), "n_cal")
            else:
                put("n_cal", None, "RULE", formula="NA: no calibration for a blocked real row")
            put("na_reason", r.status if r.status != "OK" else None, "SOURCE", "selection.csv", sub_key, "status",
                formula="status when not OK, else NA")
            rows.append(row)
        blocks.append({"block_id": bid, "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                       "detector_family": fam, "objective_kind": obj, "block_family": block_family, "n_rows": len(grp)})
    t.rows["T2"] = rows
    t.blocks["T2"] = blocks
    return t


T3_COLS = [("table", "str"), ("row_id", "str"), ("block_id", "str"), ("ordre", "str"), ("method", "str"),
           ("objective_kind", "str"), ("detector_family", "str"),
           ("dataset_id", "str"), ("cohort_id", "str"), ("event_id", "str"), ("event_window_id", "str"),
           ("S", "str"), ("d_star", "int"), ("I_star", "float"), ("info_kind", "str"),
           ("I_cov_joint", "float"), ("I_cov_marginal_sum", "float"),
           ("M_cost", "float"), ("C_affine", "float"), ("cost_kind", "str"), ("V_denominator", "str"),
           ("V_star", "float"), ("V_star_meaning", "str"),
           ("rmst", "float"), ("rmst_lo", "float"), ("rmst_hi", "float"), ("n_alt", "int"), ("det_rate", "float"),
           ("censored_share", "float"),
           ("fpr", "float"), ("fpr_lo", "float"), ("fpr_hi", "float"), ("n_eval", "int"),
           ("fpr_calibration", "float"), ("n_cal", "int"), ("predictive_bound", "float"), ("target_fpr", "float"),
           ("metric_id", "str"), ("null_metric_id", "str"), ("null_calibration_id", "str"), ("calibration_hash", "str"),
           ("selection_id", "str"),
           ("basis_hash", "str"), ("split_hash", "str"), ("config_hash", "str"), ("seed", "int"),
           ("oracle_input", "str"), ("claim_flag", "str"), ("selection_exact", "str"), ("tie_broken", "str"),
           ("comparability", "str"), ("cpv90_k_full", "int"),
           ("status", "str"), ("execution", "str"), ("source_kind", "str"), ("claim_scope", "str"),
           ("na_reason", "str"), ("footnotes", "str")]

T3_MEAN_ORDER = (("0", "BASELINE_CPV90", "CPV90_RULE"), ("1", "ORACLE_Q_AFFINE", "MEAN_AFFINE_SURROGATE"),
                 ("2", "ORACLE_Q_MIX", "MEAN_MIX_FLUID_SURROGATE"),
                 ("3", "EXANTE_QBAR", "EXANTE_QBAR_MIX_FLUID_SURROGATE"))
T3_COV_ORDER = T3_MEAN_ORDER + (("D1", "COV_JOINT_ORACLE", "COV_JOINT_AFFINE_SURROGATE"),
                                ("D2", "COV_JOINT_ORACLE", "COV_JOINT_MIX_HEURISTIC"),
                                ("D3", "COV_MARGINAL_DIAGNOSTIC", "COV_MARGINAL_MIX_DIAGNOSTIC"),
                                ("C", "ENERGY_INDEX_COMPARATOR", "NONE"))
T3R_COLS = [("table", "str"), ("row_id", "str"), ("block_id", "str"), ("cohort_id", "str"), ("event_id", "str"),
            ("event_window_id", "str"), ("method", "str"), ("claim_scope", "str"), ("status", "str"),
            ("calib_first_day", "str"), ("calib_last_day", "str"), ("monitor_start", "str"),
            ("embargo_after_2019", "int"), ("pre_onset_policy", "str"), ("monitor_armed_from", "str"),
            ("onset_date", "str"), ("event_end_date", "str"), ("time_origin", "str"),
            ("n_event_sessions", "int"), ("alarm_dates", "str"), ("pre_onset_alarms", "int"),
            ("pre_onset_alarm_dates", "str"), ("detected_during_event", "str"), ("time_to_alarm_during_event", "float"),
            ("event_censored", "str"), ("post_onset_delay_h250", "float"), ("post_onset_alarm_date", "str"),
            ("post_event_alarm", "str"), ("path_supports_H", "str"),
            ("selection_id", "str"), ("metric_id", "str"), ("claim_flag", "str"), ("footnotes", "str")]


def _eq_col(series, value):
    """pandas equality that maps None to NA (synthetic cohort_id)."""
    return series.isna() if value is None else series == value


def _t3_v_meaning(obj, is_cov):
    if is_cov:
        return "COV_HEURISTIC_SURROGATE"
    return {"MEAN_MIX_FLUID_SURROGATE": "MEAN_MIX_FLUID_SURROGATE",
            "MEAN_AFFINE_SURROGATE": "MEAN_AFFINE_SURROGATE",
            "EXANTE_QBAR_MIX_FLUID_SURROGATE": "EXANTE_QBAR_MIX_FLUID_SURROGATE"}.get(obj)


def build_t3(run, t, dataset=None, scenario=None, family=None):
    """Tableau_PCA_3: ablations/ex-ante selection, one group per (dataset_id, cohort_id, event_id), fixed order; mean row (2) reuses the exact T2 objects at k = nmax; T3R = real-episode sub-table (Markdown)."""
    nmax = run.nmax
    t.cols["T3"] = T3_COLS
    t.cols["T3R"] = T3R_COLS
    sel = run.frames["selection"]
    e1 = sel[(sel["experiment"] == "E1") & (sel["method"] == "BASELINE_PREFIX")]
    groups = []
    for r in e1.itertuples(index=False):
        key = (r.dataset_id, None if _isna(r.cohort_id) else r.cohort_id, r.event_id)
        if key not in groups:
            groups.append(key)
    groups.sort(key=lambda k: (k[0], k[1] or "", k[2]))
    t2_ix = {(r["dataset_id"], r["cohort_id"], r["event_id"], r["k"]): r for r in t.rows["T2"]}
    rows, blocks, rows_r = [], [], []
    for key in groups:
        ds, cohort, ev = key
        if (dataset and ds != dataset) or (scenario and ev != scenario):
            continue
        if family:
            fams = set(sel[(sel["dataset_id"] == ds) & _eq_col(sel["cohort_id"], cohort)
                           & (sel["event_id"] == ev)]["detector_family"].dropna())
            if family not in fams:
                continue
        gsel = sel[(sel["dataset_id"] == ds) & _eq_col(sel["cohort_id"], cohort) & (sel["event_id"] == ev)]
        real = ds == "D3_239"
        is_cov = bool((gsel["detector_family"] == pdb.COV).any())
        order = T3_COV_ORDER if is_cov else T3_MEAN_ORDER
        bid = pdb.sha16({"table": "T3", "dataset_id": ds, "cohort_id": cohort, "event_id": ev})
        e3 = gsel[(gsel["experiment"] == "E3") & (gsel["row_kind"] == "SELECTED")]
        block_rows = 0
        for ordre, method, obj in order:
            rid = f"T3:{bid}:{ordre}"
            row = {}

            def put(col, value, kind, src_file="", src_key="", src_col="", formula="", inputs=""):
                row[col] = None if _isna(value) else value
                _lin_add(t, "T3", rid, col, kind, src_file, src_key, src_col, formula, inputs)

            src = None
            if not (is_cov and ordre in ("1", "2")):
                cand = e3[(e3["method"] == method) & (e3["objective_kind"] == obj)]
                if len(cand) != 1:
                    raise Refused("T3_ROW_MISSING", f"T3 group {key}: {method}/{obj} has {len(cand)} E3 rows")
                src = cand.iloc[0]
            sel_key = ""
            if src is not None:
                sel_key = pdb.canon({"selection_id": src["selection_id"], "experiment": "E3",
                                     "row_kind": "SELECTED", "d": _norm(src["d"])})
            rule_line = is_cov and ordre in ("1", "2")
            row_fam = pdb.COV if rule_line else (None if src is None else src["detector_family"])
            if family is not None and row_fam != family:
                continue
            put("table", "T3", "RULE", formula="literal 'T3'")
            put("row_id", rid, "RULE", formula="f'T3:{block_id}:{ordre}'")
            put("block_id", bid, "FORMULA", formula="pdb.sha16({table,dataset_id,cohort_id,event_id})",
                inputs=pdb.canon({"table": "T3", "dataset_id": ds, "cohort_id": cohort, "event_id": ev}))
            put("ordre", ordre, "RULE", formula="fixed order of plan §6")
            t2copy = ordre == "2" and not is_cov and not real
            put("method", method, "SOURCE" if not rule_line else "RULE",
                "" if rule_line else "selection.csv", "" if rule_line else sel_key,
                "" if rule_line else "method",
                formula="" if not rule_line else
                "H7: mean-oracle lines are explicit UNSUPPORTED rows for covariance")
            if src is not None:
                put("objective_kind", obj, "SOURCE", "selection.csv", sel_key, "objective_kind")
                put("detector_family", src["detector_family"], "SOURCE", "selection.csv", sel_key, "detector_family")
                for col in ("dataset_id", "cohort_id", "event_id", "event_window_id", "S", "d", "I_objective",
                            "info_kind", "I_cov_joint", "I_cov_marginal_sum", "M_cost", "C_affine", "cost_kind",
                            "oracle_input", "claim_flag", "selection_exact", "tie_broken", "comparability",
                            "cpv90_k_full", "status", "execution", "source_kind", "claim_scope", "metric_id",
                            "null_metric_id", "null_calibration_id", "calibration_hash", "selection_id",
                            "basis_hash", "split_hash", "config_hash", "seed"):
                    if t2copy and col in ("S", "d", "metric_id"):
                        continue
                    put({"d": "d_star", "I_objective": "I_star"}.get(col, col), getattr(src, col), "SOURCE",
                        "selection.csv", sel_key, col)
            else:
                put("objective_kind", obj, "RULE", formula="declared objective of the mean-oracle rule")
                put("detector_family", pdb.COV, "RULE", formula="the covariance block family")
                for col in ("dataset_id", "cohort_id", "event_id"):
                    put(col, {"dataset_id": ds, "cohort_id": cohort, "event_id": ev}[col], "RULE", formula="group key")
                for col in ("event_window_id", "S", "d_star", "I_star", "info_kind", "I_cov_joint",
                            "I_cov_marginal_sum", "M_cost", "C_affine", "cost_kind", "metric_id", "null_metric_id",
                            "null_calibration_id", "calibration_hash", "selection_id", "basis_hash", "split_hash",
                            "config_hash", "seed", "oracle_input", "claim_flag", "selection_exact", "tie_broken",
                            "comparability", "cpv90_k_full"):
                    put(col, None, "RULE", formula="NA: UNSUPPORTED line, no metric")
                put("status", "UNSUPPORTED", "RULE", formula="H7")
                put("execution", "NOT_EXECUTED", "RULE", formula="H7")
                put("source_kind", "SYNTHETIC_GAUSSIAN" if ds == "SYNTH_GAUSS_EQUICORR" else "SYNTHETIC_T7",
                    "RULE", formula="background of the group")
                put("claim_scope", "SYNTHETIC_MC", "RULE", formula="synthetic group")
            v_col = "V_affine" if obj in ("MEAN_AFFINE_SURROGATE", "COV_JOINT_AFFINE_SURROGATE") else "V_mix"
            if src is not None and src["cost_kind"] == "NONE":
                v_den = None
            else:
                v_den = "C_affine" if v_col == "V_affine" else "M_cost"
            put("V_denominator", v_den, "RULE",
                formula="source cost column that divides I in V_star (AFFINE_SURROGATE -> C_affine, else M_cost; "
                        "NONE for the energy comparator); never recomputed")
            if src is not None:
                if not t2copy:
                    put("V_star", getattr(src, v_col), "SOURCE", "selection.csv", sel_key, v_col)
            else:
                put("V_star", None, "RULE", formula="NA: UNSUPPORTED line")
            put("V_star_meaning", None if real else _t3_v_meaning(obj, is_cov), "RULE",
                formula="surrogate meaning; NA for real rows")
            if src is not None and not _isna(src["null_metric_id"]):
                a = run.agg_ix.loc[src["metric_id"]]
                h = run.agg_ix.loc[src["null_metric_id"]]
                a_key = pdb.canon({"metric_id": src["metric_id"]})
                h_key = pdb.canon({"metric_id": src["null_metric_id"]})
                for col in ("rmst", "rmst_lo", "rmst_hi", "det_rate", "censored_share"):
                    if t2copy and col in ("rmst", "rmst_lo", "rmst_hi"):
                        continue
                    put(col, getattr(a, col), "SOURCE", "aggregates.csv", a_key, col)
                put("n_alt", a.n, "SOURCE", "aggregates.csv", a_key, "n")
                for col in ("fpr", "fpr_lo", "fpr_hi"):
                    if t2copy:
                        continue
                    put(col, getattr(h, col), "SOURCE", "aggregates.csv", h_key, col)
                put("n_eval", h.n, "SOURCE", "aggregates.csv", h_key, "n")
                put("target_fpr", h.target_fpr, "SOURCE", "aggregates.csv", h_key, "target_fpr")
            else:
                for col in ("rmst", "rmst_lo", "rmst_hi", "det_rate", "censored_share", "n_alt", "fpr", "fpr_lo",
                            "fpr_hi", "n_eval", "target_fpr"):
                    if t2copy and col in ("rmst", "rmst_lo", "rmst_hi", "fpr", "fpr_lo", "fpr_hi"):
                        continue
                    put(col, None, "RULE",
                        formula=f"NA: row not executed (status {row.get('status')})")
            if src is not None and not _isna(src["null_calibration_id"]):
                c = run.cal_ix.loc[src["null_calibration_id"]]
                c_key = pdb.canon({"null_calibration_id": src["null_calibration_id"]})
                for col, srcc in (("fpr_calibration", "calibration_fraction"), ("n_cal", "n_cal"),
                                  ("predictive_bound", "predictive_bound")):
                    put(col, getattr(c, srcc), "SOURCE", "calibration.csv", c_key, srcc)
            else:
                for col in ("fpr_calibration", "n_cal", "predictive_bound"):
                    put(col, None, "RULE", formula="NA: no calibration referenced by the source row")
            if t2copy:
                p = t2_ix[(ds, cohort, ev, nmax)]
                for col, src_col in (("S", "S_star"), ("d_star", "d_star"), ("V_star", "V_star"),
                                     ("rmst", "rmst_selected"), ("rmst_lo", "rmst_selected_lo"),
                                     ("rmst_hi", "rmst_selected_hi"), ("metric_id", "metric_id_subset"),
                                     ("fpr", "fpr_selected"), ("fpr_lo", "fpr_selected_lo"),
                                     ("fpr_hi", "fpr_selected_hi")):
                    row[col] = p[src_col]
                    _lin_add(t, "T3", rid, col, "FORMULA",
                             formula=f"identity with the T2 row at k={nmax} cell {src_col} (same object)",
                             inputs=pdb.canon({"t2_row_id": p["row_id"], "column": src_col}))
            put("na_reason", row.get("status") if row.get("status") not in (None, "OK") else None, "RULE",
                formula="status when not OK, else NA")
            notes = []
            if is_cov:
                notes.append("N-COV")
            if real:
                notes.append("N-REAL")
            if ds == "SYNTH_T7_EQUICORR":
                notes.append("N-T7")
            if row.get("status") == "CPV90_OUTSIDE_TOP20":
                notes.append("N-CPV90")
            if not (is_cov and ordre in ("1", "2")):
                notes.append("N-RULE" if False else "N-SRC")
            put("footnotes", ";".join(notes), "RULE", formula="note register ids")
            rows.append(row)
            block_rows += 1
        if block_rows:
            blocks.append({"block_id": bid, "dataset_id": ds, "cohort_id": cohort, "event_id": ev,
                           "kind": "real" if real else ("cov" if is_cov else "mean"), "n_rows": block_rows})
    t.rows["T3"] = rows
    t.blocks["T3"] = blocks
    cohorts = run.manifest["real"]["cohorts"]
    for c, spec in sorted(cohorts.items()):
        if dataset is not None and dataset != "D3_239":
            break
        for ev in sorted(spec["events"]):
            if scenario is not None and ev != scenario:
                continue
            defi = spec["definition"]
            ewid = spec["events"][ev]["event_window_id"]
            bid = pdb.sha16({"table": "T3R", "dataset_id": "D3_239", "cohort_id": c, "event_id": ev})
            gsel = sel[(sel["dataset_id"] == "D3_239") & (sel["cohort_id"] == c) & (sel["event_id"] == ev)]
            e3 = gsel[(gsel["experiment"] == "E3") & (gsel["row_kind"] == "SELECTED")]
            for ordre, method, obj in T3_MEAN_ORDER:
                rid = f"T3R:{bid}:{method}"
                row = {"table": "T3R", "row_id": rid, "block_id": bid, "cohort_id": c, "event_id": ev,
                       "event_window_id": ewid, "method": method, "claim_scope": spec["claim_scope"]}
                cand = e3[(e3["method"] == method) & (e3["objective_kind"] == obj)]
                src = cand.iloc[0] if len(cand) else None
                if family is not None and (pdb.MEAN if src is None else src["detector_family"]) != family:
                    continue
                sel_key = pdb.canon({"selection_id": src["selection_id"], "experiment": "E3", "row_kind": "SELECTED",
                                     "d": _norm(src["d"])}) if src is not None else ""
                mpaths = {"status": ["real", "cohorts", c, "events", ev, "status"],
                          "calib_first_day": ["real", "cohorts", c, "definition", "calib", 0],
                          "calib_last_day": ["real", "cohorts", c, "definition", "calib", 1],
                          "monitor_start": ["real", "cohorts", c, "definition", "monitor_start"],
                          "embargo_after_2019": ["real", "cohorts", c, "embargo_after_2019"],
                          "pre_onset_policy": ["real", "cohorts", c, "definition", "pre_onset_policy"],
                          "monitor_armed_from": ["real", "cohorts", c, "monitor_armed_from"],
                          "onset_date": ["real", "cohorts", c, "events", ev, "onset"],
                          "event_end_date": ["real", "cohorts", c, "events", ev, "end"],
                          "time_origin": ["real", "cohorts", c, "events", ev, "time_origin"]}
                for col, val in (("status", spec["events"][ev]["status"]), ("calib_first_day", defi["calib"][0]),
                                 ("calib_last_day", defi["calib"][1]), ("monitor_start", defi["monitor_start"]),
                                 ("embargo_after_2019", spec["embargo_after_2019"]),
                                 ("pre_onset_policy", defi["pre_onset_policy"]),
                                 ("monitor_armed_from", spec["monitor_armed_from"]),
                                 ("onset_date", spec["events"][ev]["onset"]), ("event_end_date", spec["events"][ev]["end"]),
                                 ("time_origin", spec["events"][ev]["time_origin"])):
                    row[col] = val
                    _lin_add(t, "T3R", rid, col, "MANIFEST", "manifest.json", pdb.canon({"path": mpaths[col]}), "",
                             "", "manifest real.cohorts block")
                for col in ("n_event_sessions", "alarm_dates", "pre_onset_alarms", "pre_onset_alarm_dates",
                            "detected_during_event", "time_to_alarm_during_event", "event_censored",
                            "post_onset_delay_h250", "post_onset_alarm_date", "post_event_alarm", "path_supports_H"):
                    row[col] = None
                    _lin_add(t, "T3R", rid, col, "RULE", formula="NA: not executed under schema /2 before J4")
                row["selection_id"] = None if src is None else src["selection_id"]
                row["metric_id"] = None if src is None else src["metric_id"]
                row["claim_flag"] = None if src is None else src["claim_flag"]
                for col in ("selection_id", "metric_id", "claim_flag"):
                    _lin_add(t, "T3R", rid, col, "SOURCE", "selection.csv", sel_key, col)
                row["footnotes"] = "N-REAL"
                _lin_add(t, "T3R", rid, "footnotes", "RULE", formula="note register id")
                for col in ("table", "row_id", "block_id", "cohort_id", "event_id", "event_window_id", "method",
                            "claim_scope"):
                    _lin_add(t, "T3R", rid, col, "RULE", formula="built key" if col not in row else "group key")
                rows_r.append(row)
    t.rows["T3R"] = rows_r
    return t


def build_tables(run, dataset=None, scenario=None, family=None):
    """Validates if needed, then builds the tables of the filtered run and checks the lineage."""
    if run.agg_ix is None:
        validate_run(run)
    t = build_t1(run, dataset, scenario, family)
    build_t2(run, t, dataset, scenario, family)
    build_t3(run, t, dataset, scenario, family)
    validate_lineage(run, t)
    return t


def validate_lineage(run, t):
    """Lineage contract: exact equality of the (table, row_id, column) keys of the exported cells and the lineage rows (no missing/duplicate/orphan); SOURCE pointers resolve to a source row + column, MANIFEST pointers to an exact manifest path."""
    seen = set()
    pk_ix = {}
    for name in ("spectra", "selection", "calibration", "aggregates"):
        keys = pdb.PRIMARY_KEYS[name]
        pk_ix[name] = {pdb.canon({k: _norm(getattr(r, k)) for k in keys})
                       for r in run.frames[name].itertuples(index=False)}
    for e in t.lineage:
        key = (e["table"], e["row_id"], e["column"])
        if key in seen:
            raise Refused("LINEAGE_DUPLICATE", f"{key} has more than one lineage row")
        seen.add(key)
        if e["kind"] == "SOURCE":
            sf = e["source_file"]
            name = sf[:-4] if sf.endswith(".csv") else None
            if name not in pk_ix:
                raise Refused("LINEAGE_SOURCE_UNKNOWN", f"{sf!r} is not a run CSV with a primary key")
            try:
                skey = json.loads(e["source_key"])
            except ValueError as exc:
                raise Refused("LINEAGE_KEY_INVALID", f"{sf} {e['source_key']!r}: {exc}") from exc
            if not isinstance(skey, dict) or pdb.canon({k: _norm(v) for k, v in skey.items()}) not in pk_ix[name]:
                raise Refused("LINEAGE_SOURCE_UNRESOLVED", f"{sf} {e['source_key']} resolves to no source row")
            if e["source_column"] not in run.frames[name].columns:
                raise Refused("LINEAGE_COLUMN_UNKNOWN", f"{sf} has no column {e['source_column']!r}")
        elif e["kind"] == "MANIFEST":
            try:
                path = json.loads(e["source_key"])["path"]
            except (ValueError, KeyError, TypeError) as exc:
                raise Refused("LINEAGE_KEY_INVALID", f"manifest {e['source_key']!r}: {exc}") from exc
            node = run.manifest
            try:
                for p in path:
                    node = node[p]
            except (KeyError, IndexError, TypeError) as exc:
                raise Refused("LINEAGE_MANIFEST_UNRESOLVED", f"manifest path {path}: {exc}") from exc
    for table in ("T1", "T2", "T3", "T3R"):
        have = {(e["row_id"], e["column"]) for e in t.lineage if e["table"] == table}
        want = {(r["row_id"], c) for r in t.rows[table] for c, _ in t.cols[table]}
        if want - have:
            raise Refused("LINEAGE_INCOMPLETE", f"{table}: {len(want - have)} displayed cells lack a lineage row")
        if have - want:
            raise Refused("LINEAGE_ORPHAN",
                          f"{table}: {len(have - want)} lineage rows point at no exported cell (filtered-out row), "
                          f"e.g. {sorted(have - want)[:3]}")
    return t


LIN_COLS = [("table", "str"), ("row_id", "str"), ("column", "str"), ("kind", "str"), ("source_file", "str"),
            ("source_key", "str"), ("source_column", "str"), ("formula", "str"), ("inputs", "str")]

T1_TITLES = {"row_id": "row_id", "k": "Indice k", "d": "Dimension retenue", "lambda_lw": "Valeur propre λ_k",
             "cpv_lw": "Variance cumulée CPV_k (%)", "criteria": "Critères standard", "rmst": "RMST250 préfixe (jours)",
             "rmst_lo": "RMST bas", "rmst_hi": "RMST haut", "det_rate": "Taux de détection",
             "censored_share": "Part censurée", "n_alt": "n_alt", "fpr_test_null": "FPR250 hors dérive",
             "fpr_lo": "FPR bas", "fpr_hi": "FPR haut", "n_eval": "n_eval", "fpr_calibration": "FPR de calibration",
             "n_cal": "n_cal", "predictive_bound": "Borne prédictive", "target_fpr": "alpha (cible)",
             "threshold_rule": "Règle de seuil", "guarantee_basis": "Base de garantie", "status": "Statut",
             "execution": "Exécution", "na_reason": "Raison NA"}
T2_TITLES = {"row_id": "row_id", "k": "Indice PCA k", "lambda_lw": "Variance λ_k (H0)", "q_k": "Information marginale q_k",
             "q_info_type": "Type d'information q", "q_source": "Source de q", "I_marginal_cum_prefix": "Σ q_j^cov (diagnostic)",
             "I_prefix": "I(P_k)", "V_prefix": "Score préfixe V(P_k)", "V_prefix_meaning": "Sens de V préfixe",
             "rmst_prefix": "RMST250 préfixe", "fpr_prefix": "FPR250 préfixe", "metric_id_prefix": "metric_id_prefix",
             "S_star": "Sous-ensemble optimal S*_k", "d_star": "Dimension optimale d*_k", "I_star": "I(S*_k)",
             "V_star": "Score V(S*_k)", "V_star_meaning": "Sens de V(S*)", "rmst_selected": "RMST250 sélection",
             "fpr_selected": "FPR250 sélection", "metric_id_subset": "metric_id_subset", "status_prefix": "Statut préfixe",
             "status_subset": "Statut sélection", "na_reason": "Raison NA", "objective_kind": "Objectif",
             "block_family": "Famille de bloc"}
T3_TITLES = {"row_id": "row_id", "ordre": "Ordre", "method": "Pipeline & règle", "objective_kind": "Objectif",
             "detector_family": "Famille", "S": "S (axes 1-based)", "d_star": "Dimension retenue d*",
             "I_star": "Information I(S)", "info_kind": "Type d'information",
             "I_cov_joint": "I_cov_joint (KL jointe, même S)", "I_cov_marginal_sum": "Σ q_j^cov (diagnostic, même S)",
             "M_cost": "Coût M(d)", "C_affine": "Coût affine C(d)", "cost_kind": "Applicabilité du coût",
             "V_denominator": "Dénominateur de V", "V_star": "Score V(S)", "V_star_meaning": "Sens de V(S)",
             "rmst": "RMST250 (jours)", "fpr": "FPR250", "n_alt": "n_alt", "n_eval": "n_eval", "status": "Statut",
             "execution": "Exécution", "footnotes": "Notes"}
T3R_TITLES = {"row_id": "row_id", "cohort_id": "Cohorte", "event_id": "Événement", "event_window_id": "Fenêtre",
              "method": "Méthode", "claim_scope": "Portée", "status": "Statut", "calib_first_day": "Calib début",
              "calib_last_day": "Calib fin", "monitor_start": "Début surveillance", "embargo_after_2019": "Embargo",
              "pre_onset_policy": "Politique pré-onset", "monitor_armed_from": "Armé depuis", "onset_date": "Onset",
              "event_end_date": "Fin", "time_origin": "Origine temps", "n_event_sessions": "Sessions (R)",
              "alarm_dates": "Alarmes (R1)", "pre_onset_alarms": "Alarmes pré-onset (R2)",
              "pre_onset_alarm_dates": "Dates pré-onset", "detected_during_event": "Détecté (R3)",
              "time_to_alarm_during_event": "Délai détection (R3)", "event_censored": "Censuré (R3)",
              "post_onset_delay_h250": "Délai post-onset H250 (R4)", "post_onset_alarm_date": "Date alarme post (R4)",
              "post_event_alarm": "Alarme post-événement", "path_supports_H": "Support H (R5)",
              "selection_id": "selection_id", "metric_id": "metric_id", "claim_flag": "claim_flag",
              "footnotes": "Notes", "table": "table", "block_id": "block_id"}
TITLES = {"T1": T1_TITLES, "T2": T2_TITLES, "T3": T3_TITLES, "T3R": T3R_TITLES}

T1_MD = ["row_id", "k", "d", "lambda_lw", "cpv_lw", "criteria", "rmst", "det_rate", "censored_share", "n_alt",
         "fpr_test_null", "n_eval", "fpr_calibration", "n_cal", "predictive_bound", "target_fpr", "status", "na_reason"]
T1_PROV = ["row_id", "block_id", "dataset_id", "cohort_id", "event_id", "detector_family", "selection_id", "metric_id",
           "null_metric_id", "null_id", "null_calibration_id", "calibration_hash", "basis_hash", "split_hash",
           "config_hash", "seed", "source_kind", "claim_scope", "status", "execution", "mp_count", "mp_edge",
           "kaiser_count", "cpv90_k_full", "cpv90_status", "threshold_rule", "guarantee_basis"]
T2_MD = ["row_id", "k", "lambda_lw", "q_k", "q_info_type", "I_marginal_cum_prefix", "I_prefix", "V_prefix",
         "V_prefix_meaning", "rmst_prefix", "fpr_prefix", "metric_id_prefix", "S_star", "d_star", "I_star", "V_star",
         "V_star_meaning", "rmst_selected", "fpr_selected", "metric_id_subset", "status_prefix", "status_subset",
         "na_reason"]
T2_PROV = ["row_id", "block_id", "dataset_id", "cohort_id", "event_id", "detector_family", "objective_kind",
           "block_family", "selection_id_prefix", "selection_id_subset", "null_metric_id_prefix",
           "null_metric_id_subset", "null_calibration_id", "null_calibration_id_subset", "calibration_hash",
           "basis_hash", "split_hash", "config_hash", "seed", "selector_kind", "selection_exact", "tie_broken",
           "oracle_input", "claim_flag", "info_kind", "I_pop_joint_prefix", "I_pop_joint_star", "pop_offdiag_max_star",
           "q_source", "n_alt", "n_eval", "n_cal", "source_kind", "claim_scope"]
T3_MD = ["row_id", "ordre", "method", "objective_kind", "S", "I_star", "I_cov_joint", "I_cov_marginal_sum",
         "info_kind", "M_cost", "C_affine", "cost_kind", "V_denominator", "V_star", "V_star_meaning", "rmst",
         "d_star", "fpr", "n_alt", "n_eval", "status", "execution", "footnotes"]
T3_PROV = ["row_id", "block_id", "dataset_id", "cohort_id", "event_id", "event_window_id", "detector_family",
           "metric_id", "null_metric_id", "null_calibration_id", "calibration_hash", "selection_id", "basis_hash",
           "split_hash", "config_hash", "seed", "oracle_input", "claim_flag", "selection_exact", "tie_broken",
           "comparability", "cpv90_k_full", "rmst_lo", "rmst_hi", "fpr_lo", "fpr_hi", "det_rate", "censored_share",
           "fpr_calibration", "n_cal", "predictive_bound", "target_fpr", "source_kind", "claim_scope", "na_reason"]
MD_COLS = {"T1": (T1_MD, T1_PROV), "T2": (T2_MD, T2_PROV), "T3": (T3_MD, T3_PROV)}

PCT_COLS = {"cpv_lw", "fpr_test_null", "fpr_lo", "fpr_hi", "fpr_calibration", "target_fpr", "predictive_bound",
            "det_rate", "censored_share", "fpr_prefix", "fpr_prefix_lo", "fpr_prefix_hi", "fpr_selected",
            "fpr_selected_lo", "fpr_selected_hi", "fpr", "fpr_lo", "fpr_hi"}
RMST_COLS = {"rmst", "rmst_lo", "rmst_hi", "rmst_prefix", "rmst_prefix_lo", "rmst_prefix_hi", "rmst_selected",
             "rmst_selected_lo", "rmst_selected_hi"}
G_COLS = {"lambda_lw", "q_k", "I_marginal_cum_prefix", "I_prefix", "V_prefix", "I_star", "V_star",
          "I_pop_joint_prefix", "I_pop_joint_star", "pop_offdiag_max_star", "mp_edge", "I_cov_joint",
          "I_cov_marginal_sum"}
F4_COLS = {"M_cost", "C_affine"}


def fmt(v, kind):
    """Display formatting (CSV keeps the raw source values): NA, .4g, .4f, percent one decimal, RMST one decimal."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "NA"
    if kind == "int":
        return str(int(v))
    if kind == "pct":
        return f"{100.0 * float(v):.1f}%"
    if kind == "rmst":
        return f"{float(v):.1f}"
    if kind == "f4":
        return f"{float(v):.4f}"
    if kind == "g":
        return f"{float(v):.4g}"
    return str(v)


def _fmt_kind(table, col, cols):
    kind = dict(cols)[col]
    if col in PCT_COLS:
        return "pct"
    if col in RMST_COLS:
        return "rmst"
    if col in G_COLS:
        return "g"
    if col in F4_COLS:
        return "f4"
    return "int" if kind == "int" else "str"


def fmt_interval(v, lo, hi, fkind):
    if v is None:
        return "NA"
    if lo is None or hi is None:
        return fmt(v, fkind)
    return f"{fmt(v, fkind)} [{fmt(lo, fkind)}, {fmt(hi, fkind)}]"


FPR_LO_HI = {"fpr_test_null": ("fpr_lo", "fpr_hi"), "fpr_prefix": ("fpr_prefix_lo", "fpr_prefix_hi"),
             "fpr_selected": ("fpr_selected_lo", "fpr_selected_hi"), "fpr": ("fpr_lo", "fpr_hi")}


def fmt_S(s):
    """Compact display of a sorted 1-based axis list: {1–3, 10}."""
    if s is None:
        return "NA"
    a = json.loads(s)
    out, i = [], 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[j + 1] == a[j] + 1:
            j += 1
        out.append(str(a[i]) if j == i else f"{a[i]}–{a[j]}")
        i = j + 1
    return "{" + ", ".join(out) + "}"


def _esc(s):
    return str(s).replace("|", "\\|")


def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_esc(c) for c in r) + " |")
    return "\n".join(out)


def _block_lines(run, block):
    m = run.manifest
    cfg = m["config"]
    mode = m.get("run_mode")
    ds, ev = block["dataset_id"], block.get("event_id")
    lines = [f"- dataset `{ds}` ; mode `{mode}` ; N = {cfg['N']} ; H = {cfg['H']} (RMST250/FPR250) ; "
             f"nmax = {cfg['nmax']}"]
    if block.get("detector_family"):
        lines.append(f"- famille de détecteur `{block['detector_family']}`"
                     + (f" ; objectif `{block.get('objective_kind')}` ; bloc `{block.get('block_family')}`"
                        if block.get("objective_kind") else ""))
    lines.append(f"- seuil : `{m['calibration']['threshold_rule']}` ; alpha = {m['calibration']['alpha']} ; "
                 f"s2 = {m['detectors']['s2_rule']} ; anytime_valid = {m['calibration']['anytime_valid']}")
    if ds in m["synthetic"]["backgrounds"]:
        model = m["synthetic"]["model"]
        law = model["t_mixing"] if ds.endswith("T7_EQUICORR") else "gaussienne i.i.d."
        lines.append(f"- loi : {model['Sigma0']} ; rho = {cfg['synthetic']['rho']} ; {law}")
        lines.append(f"- base LW gelée sur T_fit = {cfg['T_fit']} lignes indépendantes (rôle fit)")
        sc = m["synthetic"]["backgrounds"][ds]["scenarios"].get(ev, {})
        if ev == "A_market_mean":
            lines.append(f"- dérive injectée : translation de marché le long de v1, SR annuel = {sc.get('sr_annual')}")
        elif ev == "C_residual_mean":
            lines.append(f"- dérive injectée : translation résiduelle sur les axes {sc.get('axes')}, I cible = {sc.get('I_target')}")
        elif ev and ev.startswith("B_"):
            lines.append(f"- dérive injectée : rotation de covariance, paire {sc.get('pair')}, theta = {sc.get('theta_deg')} deg")
        eff = " ; ".join(f"{k} = {cfg.get(k)}" for k in ("n_center", "n_cal", "n_null", "n_alt"))
        if mode == "smoke":
            full = " ; ".join(f"{k} = {v}" for k, v in sorted((cfg.get("full_counts") or {}).items()))
            lines.append(f"- effectifs (smoke) : {eff} ; complet prévu : {full} — non exécuté")
        else:
            lines.append(f"- effectifs ({mode}) : {eff}")
    else:
        coh = m["real"].get("cohorts", {}).get(block.get("cohort_id"), {})
        defi = coh.get("definition", {})
        evd = coh.get("events", {}).get(ev, {})
        lines.append(f"- cohorte `{block.get('cohort_id')}` ; claim_scope `{coh.get('claim_scope')}` ; "
                     f"calib {defi.get('calib')} ; monitor_start `{defi.get('monitor_start')}` ; "
                     f"embargo {coh.get('embargo_after_2019')} ; pre_onset_policy `{defi.get('pre_onset_policy')}`")
        lines.append(f"- événement `{ev}` : onset {evd.get('onset')} ; fin {evd.get('end')} ; statut `{evd.get('status')}`")
        lines.append("- aucune lecture de rendement post-2019 (schéma /2, avant J4) ; mesures NA")
    lines.append(f"- provenance : run_fingerprint `{m['run_fingerprint'][:16]}…` ; sélection dans selection.csv (E1/E2/E3)")
    return lines


NOTES = {
    "N-SMOKE": "SMOKE_NO_CLAIMS : effectifs smoke de 40 par rôle ; aucune conclusion FPR/RMST ; le run complet (2000) "
               "n'est pas exécuté.",
    "N-COV": "Bloc covariance : V = I_cov_joint / coût est un substitut heuristique (COV_HEURISTIC_SURROGATE) ; "
             "I_cov_joint n'est pas additif ; le classement marginal n'est pas l'oracle covariance ; M(d) en covariance "
             "est un coût fluide de mélange non validé.",
    "N-REAL": "Ligne réelle bloquée avant J4 (schéma /2) : mesures empiriques NA, R1–R5 NA, aucun FPR holdout réel ; "
              "FROZEN.json présent n'autorise aucune mesure réelle.",
    "N-T7": "Fond t7 : q et V sont des proxys gaussiens (MEAN_GAUSSIAN_PROXY) ; le RMST empirique reste mesuré.",
    "N-CPV90": "CPV90 hors des 20 premiers axes (k90_full indiqué) : pas de métrique, NOT_COMPARABLE_OUTSIDE_TOP20.",
    "N-SRC": "Ligne issue de selection.csv (E1/E2/E3).",
}

METHODOLOGY = """## Méthodologie et définitions

- RMST250 : moyenne des temps censurés `censored_time` (alarme incluse, -1 -> H) sur les n_alt trajectoires
  alternatives ; intervalle normal (Z95 * rmst_se, deff = 1). Jamais déduit d'un score V analytique.
- FPR250 hors dérive : fréquence observée des alarmes sur les n_null trajectoires holdout indépendantes, intervalle
  de Wilson. Distincte de la fréquence empirique de calibration et de la borne prédictive (r+1)/(n_cal+1).
- Seuil `predictive_exchangeable_rank_v2` : r = floor(alpha (n_cal+1)) - 1 ; borne (r+1)/(n_cal+1) <= alpha pour des
  maxima échangeables ; quasi-vraisemblance (blanchiment LW estimé), anytime_valid = False.
- q_k (moyenne) : recette H3, q = 0.5 (beta_k / sqrt(lambda_lw_k))^2, somme exacte sur S égale à I_plugin_lw ; proxy
  gaussien sur les deux fonds. q_k covariance par axe : NA (non exporté par le schéma /2).
- V = I / coût ; M(d, gamma_M) est un substitut fluide de mélange, jamais un délai exact ; la corde affine C(d) est
  distincte. En covariance, V est un substitut heuristique (COV_HEURISTIC_SURROGATE).
- Lignes réelles : schéma /2, avant J4, NOT_EXECUTED, mesures et R1–R5 NA ; les deux cohortes Covid sont distinctes et
  bloquées. Les valeurs théoriques (I, M, C, V) sont recopiées telles quelles, même à l'état bloqué.
- NA signifie non applicable ou non calculé ; jamais un zéro. NOT_MEASURED : cible alpha présente sans FPR atteint.
"""

LEGEND = """## Légende des abréviations

- LW : Ledoit-Wolf ; CPV : variance cumulée ; MP : Marchenko-Pastur (matrice de corrélation) ; k90 : seuil CPV 90 %
  sur le spectre complet ; S : sous-ensemble d'axes 1-based trié ; d* : dimension retenue.
- H = 250 jours ; RMST250/FPR250 : lectures à horizon H. n_cal/n_eval/n_alt : effectifs des rôles calibration, holdout
  nul, alternative. row_id = `<T>:<block_id>:<k|ordre>` ; block_id = sha16 de la clé de bloc (contrat
  `pca_drift_tables/1`, docs/sections/pca_drift_tables.md).
"""


def render_md(run, t, table):
    """Markdown document of one table: banner, methodology, legend, per-block headers, main table, provenance sub-table, note register; T3 adds the T3R sub-table."""
    cols = t.cols[table]
    titles = TITLES[table]
    md_cols, prov_cols = MD_COLS[table]
    rows = t.rows[table]
    blocks = t.blocks[table]
    smoke = run.manifest["run_mode"] == "smoke"
    out = [f"# Tableau_PCA_{table[1]} — { {'T1': 'référence spectrale (k = 1..20)', 'T2': 'préfixe P_k contre sous-ensemble S*_k', 'T3': 'ablations et sélection ex ante'}[table] }", ""]
    if smoke:
        out += ["> **SMOKE_NO_CLAIMS** — effectifs smoke de 40 par rôle : aucune conclusion FPR/RMST. "
                "Le run complet (2000 par rôle) est prévu, non exécuté.", ""]
    out += [METHODOLOGY, "", LEGEND, ""]
    for b in blocks:
        brows = [r for r in rows if r["block_id"] == b["block_id"]]
        title = f"{b['dataset_id']}" + (f" / {b['cohort_id']}" if b.get("cohort_id") else "") + f" / {b['event_id']}"
        if b.get("detector_family"):
            title += f" / {b['detector_family']}"
        if b.get("objective_kind"):
            title += f" / {b['objective_kind']}"
        out += [f"### {title}", ""]
        out += _block_lines(run, b)
        out += [""]
        headers = [titles.get(c, c) for c in md_cols]
        mrows = []
        for r in brows:
            cells = []
            for c in md_cols:
                fk = _fmt_kind(table, c, cols)
                v = r.get(c)
                if c == "S_star" or c == "S":
                    cells.append(fmt_S(v))
                elif c in ("rmst", "rmst_prefix", "rmst_selected"):
                    cells.append(fmt_interval(v, r.get(c + "_lo"), r.get(c + "_hi"), "rmst"))
                elif c in ("fpr_test_null", "fpr_prefix", "fpr_selected", "fpr"):
                    lo_col, hi_col = FPR_LO_HI.get(c, (c + "_lo", c + "_hi"))
                    if v is None and r.get("target_fpr") is not None:
                        cells.append("NOT_MEASURED")
                    else:
                        cells.append(fmt_interval(v, r.get(lo_col), r.get(hi_col), "pct"))
                else:
                    cells.append(fmt(v, fk))
            mrows.append(cells)
        out += [_md_table(headers, mrows), ""]
        if b.get("kind") == "cov" or (table == "T2" and b.get("block_family") == "COV"):
            out += [f"> Avertissement — {NOTES['N-COV']}", ""]
        if table == "T1":
            k90 = brows[0].get("cpv90_k_full")
            if brows[0].get("cpv90_status") == "CPV90_OUTSIDE_TOP20":
                out += [f"> Note de bloc — CPV90_OUTSIDE_TOP20 (k90_full = {k90}) : aucun marqueur « CPV 90 % » "
                        "dans les lignes 1..20.", ""]
    out += ["## Sous-tableau de provenance", ""]
    prov_headers = [titles.get(c, c) for c in prov_cols]
    prov_rows = [[fmt(r.get(c), _fmt_kind(table, c, cols)) if c not in ("S",) else fmt_S(r.get(c))
                  for c in prov_cols] for r in rows]
    out += [_md_table(prov_headers, prov_rows), ""]
    if table == "T3" and t.rows["T3R"]:
        out += ["## Sous-tableau « Épisodes réels (trajectoire unique) »", "",
                "Une ligne par (cohorte, événement, méthode). Toutes les mesures R1–R5 sont NA : non exécuté "
                "(schéma /2, avant J4). La cohorte standard est NOT_EVALUABLE_STANDARD_SPLIT pour COVID_2020 ; "
                "la rétrospective est armée à la première séance de 2020 (non lisible avant J4).", ""]
        rcols = [c for c, _ in t.cols["T3R"]]
        rheaders = [TITLES["T3R"].get(c, c) for c in rcols]
        rrows = []
        for r in t.rows["T3R"]:
            rrows.append([fmt(r.get(c), _fmt_kind("T3R", c, t.cols["T3R"])) for c in rcols])
        out += [_md_table(rheaders, rrows), ""]
    used = sorted({n for r in rows for n in (r.get("footnotes") or "").split(";") if n})
    if smoke:
        used = ["N-SMOKE"] + [u for u in used if u != "N-SMOKE"]
    out += ["## Registre de notes", ""]
    for n in used:
        out.append(f"- **{n}** — {NOTES.get(n, '')}")
    out.append("")
    return "\n".join(out)


def _frame(rows, cols):
    """DataFrame with the declared dtypes: float64 / Int64 / str, so save_fair_csv rewrites the source text exactly."""
    data = {}
    for name, kind in cols:
        vals = [r.get(name) for r in rows]
        if kind == "float":
            data[name] = pd.array([np.nan if v is None else float(v) for v in vals], dtype="float64")
        elif kind == "int":
            data[name] = pd.array([pd.NA if v is None else int(v) for v in vals], dtype="Int64")
        else:
            data[name] = pd.array([pd.NA if v is None else str(v) for v in vals], dtype="str")
    return pd.DataFrame(data, columns=[c for c, _ in cols])


def render_validation(run, t, rel_input, command, strict, identity_status):
    """TABLES_VALIDATION.md (English): counters, per-table rows, source hashes, control list, identity line, regeneration command."""
    c = run.counters
    m = run.manifest
    lines = ["# TABLES_VALIDATION", "",
             f"- input: `{rel_input}` ; run_fingerprint `{m['run_fingerprint']}` ; schema `{m['schema_version']}` ; "
             f"run_mode `{m['run_mode']}` ; tables_schema `{TABLES_SCHEMA}`",
             f"- identity recomputation: {identity_status}", "",
             "## Counters (validated input)", "",
             f"- selection.csv: {c['selection_rows']} rows ; metric_id references {c['sel_metric_refs']} -> "
             f"{c['sel_metric_distinct']} distinct ; classes S-EVAL {c['s_eval']} / S-CALFAIL {c['s_calfail']} / "
             f"S-NOEVAL {c['s_noeval']} / S-CAND {c['s_cand']} (théorie I/M/V conservée: {c['cand_theory_filled']}) / "
             f"S-REAL {c['s_real']} (S NA: {c['real_s_na']} ; null_calibration_id renseigné: "
             f"{c['real_null_calibration_filled']})",
             f"- aggregates.csv: {c['agg_rows']} rows ; ALT_RMST OK {c['alt_ok']} ; HOLDOUT OK {c['holdout_ok']} ; "
             f"GAUSS checks {c['gauss_check']} (non tabulés) ; REAL_EVENT_PATH {c['real_path']} ; calfail "
             f"{c['calfail_agg']}",
             f"- calibration.csv: {c['cal_rows']} rows ; OK {c['cal_ok']} ; CALIBRATION_FAILED {c['cal_failed']}",
             f"- trials.csv: {c['trials_rows']} rows (calibration {c['trials_calibration']} ; holdout_null "
             f"{c['trials_holdout_null']} ; alternative {c['trials_alternative']}) ; real_path 0",
             f"- issues.csv: {c['issues_rows']} rows", "",
             "## Tables", ""]
    for table in ("T1", "T2", "T3"):
        rows = t.rows[table]
        blocks = t.blocks[table]
        na = sum(1 for r in rows if r.get("na_reason") is not None)
        lines.append(f"- Tableau_PCA_{table[1]}: {len(rows)} rows in {len(blocks)} blocks ; NA reasons {na}")
    lines += [f"- T3R (Markdown sub-table, real episodes): {len(t.rows['T3R'])} rows",
              f"- table_lineage.csv: {len(t.lineage)} rows (exact equality with the exported cell keys; unique, "
              f"SOURCE/MANIFEST pointers resolve)", "",
              "## Source SHA-256 (7 files)", ""]
    for f in RUN_FILES:
        lines.append(f"- `{f}` : `{pdb.file_sha256(run.input_dir / f)}`")
    lines += ["", "## Controls", ""]
    for name in ("F1 files present", "F2 schema /2", "F3 run fingerprint", "F4 config hash",
                 "F5 output hashes (checked before any CSV parsing)", "F6 CSV headers",
                 "CSV parse under the /2 reading rules (malformed -> CSV_PARSE_FAILED)", "F7 run-wide cells",
                 "F8 closed enumerations", "primary keys unique",
                 "selection row classes (S-EVAL/S-CALFAIL/S-NOEVAL/S-CAND/S-REAL)", "foreign keys and accords",
                 "aggregate classes; finiteness per metric_kind and effective count: deff/n_eff and det_lo/det_hi "
                 "required finite at every n (n = 1 included), only rmst_sd/rmst_se/rmst_lo/rmst_hi may be NA at "
                 "n = 1 and are required finite at n > 1, never non-finite", "trial inventory: every expected (group_id, role) "
                 "present with its exact n / n_cal count, wrong roles and orphans refused",
                 "calibration-failure coherence in both directions (§3.6; real D6 exception keeps blocked real "
                 "statuses)", "horizon H present and exactly 250 (H14)", "real contract /2 (H15)",
                 "spectra coherence", "L16 E2 prefix = E1", "L17 E3 oracle copies = E2 at k = nmax",
                 "L18 H3 q sums and rank orders", "T1/T2/T3 block completeness",
                 "lineage: exact equality of the (table, row_id, column) keys of the exported cells and the lineage "
                 "rows (no missing, duplicate or orphan), SOURCE/MANIFEST pointers resolve",
                 "filters applied to every table row, the T3R sub-table and the lineage (no provenance row is emitted "
                 "for a filtered-out row)"):
        lines.append(f"- {name}: PASS")
    lines += ["", "## Regeneration command (deterministic; <OUT> is the literal output directory)", "",
              "```", command, "```", ""]
    return "\n".join(lines)


def check_identity_strict(run):
    """H10 --strict: recompute pdb.identity_block from the artifact's DECLARED config and input set (relative repo paths, hash-checked) and require equality with manifest.identity; custom-config/extra-input artifacts accepted."""
    importlib.import_module("statsmodels")
    cfg = dict(run.manifest["config"])
    declared = run.manifest["identity"].get("inputs")
    if not isinstance(declared, dict) or not declared:
        raise Refused("MANIFEST_INVALID", "identity.inputs missing or empty")
    inputs = []
    for rel, sha in sorted(declared.items()):
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts:
            raise Refused("INPUT_PATH_INVALID", f"declared input {rel!r} is not a relative repository path")
        p = pdb.REPO_ROOT / p
        if not p.is_file() or pdb.file_sha256(p) != sha:
            raise Refused("INPUT_HASH_MISMATCH", f"declared input {rel} is missing or its SHA-256 differs")
        inputs.append(p)
    if pdb.identity_block(cfg, inputs) != run.manifest["identity"]:
        raise Refused("IDENTITY_MISMATCH", "recomputed identity_block differs from manifest.identity")
    return True


def _command_gabarit(rel_input, fmt_mode, dataset, scenario, family, strict):
    cmd = ("OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \\\n"
           f".venv/bin/python experiments/pca_drift_tables.py --input-dir {rel_input} --output-dir <OUT> \\\n"
           f"  --format {fmt_mode}")
    if dataset:
        cmd += f" --dataset {dataset}"
    if scenario:
        cmd += f" --scenario {scenario}"
    if family:
        cmd += f" --detector-family {family}"
    if strict:
        cmd += " --strict"
    return cmd


def _env_block():
    return {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
            "MPLBACKEND": os.environ.get("MPLBACKEND"),
            **{k: os.environ.get(k) for k in pdb.REQUIRED_ENV}}


def write_outputs(out_dir, run, t, fmt_mode, strict, identity_status, dataset, scenario, family):
    """Writes the output files in fixed order (table_manifest.json last via .partial + os.replace); returns the outputs dict {file: {sha256, bytes, rows}} of every written file except the manifest."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    outputs = {}

    def record(path, data_rows=None):
        with open(path, "rb") as f:
            n_lines = sum(1 for _ in f)
        outputs[path.name] = {"sha256": pdb.file_sha256(path), "bytes": path.stat().st_size,
                              "rows": data_rows if data_rows is not None else n_lines}

    for table in ("T1", "T2", "T3"):
        df = _frame(t.rows[table], t.cols[table])
        path = out / f"Tableau_PCA_{table[1]}.csv"
        save_fair_csv(df, path)
        record(path, data_rows=len(df))
        if fmt_mode in ("md", "both"):
            mpath = out / f"Tableau_PCA_{table[1]}.md"
            mpath.write_text(render_md(run, t, table))
            record(mpath)
    lin = _frame(t.lineage, LIN_COLS)
    lpath = out / "table_lineage.csv"
    save_fair_csv(lin, lpath)
    record(lpath, data_rows=len(lin))
    rel_input = pdb._rel(run.input_dir)
    command = _command_gabarit(rel_input, fmt_mode, dataset, scenario, family, strict)
    vpath = out / "TABLES_VALIDATION.md"
    vpath.write_text(render_validation(run, t, rel_input, command, strict, identity_status))
    record(vpath)
    input_block = {"path": rel_input, "run_fingerprint": run.manifest["run_fingerprint"],
                   "schema_version": run.manifest["schema_version"], "run_mode": run.manifest["run_mode"],
                   "sha256": {f: pdb.file_sha256(run.input_dir / f) for f in RUN_FILES}}
    code_block = {"experiments/pca_drift_tables.py": pdb.file_sha256(Path(__file__).resolve()),
                  "experiments/pca_drift_benchmark.py": pdb.file_sha256(Path(pdb.__file__).resolve())}
    env_block = _env_block()
    filt = {"dataset": dataset, "scenario": scenario, "detector_family": family}
    manifest_out = {
        "tables_schema": TABLES_SCHEMA,
        "input": input_block,
        "code": code_block,
        "environment": env_block,
        "filters": filt,
        "format": fmt_mode, "strict": bool(strict), "command": command,
        "columns": {table: {name: TITLES[table].get(name, name) for name, _ in t.cols[table]}
                    for table in ("T1", "T2", "T3", "T3R")},
        "outputs": outputs,
        "tables_fingerprint": hashlib.sha256(pdb.canon({
            "tables_schema": TABLES_SCHEMA, "input": input_block, "code": code_block, "environment": env_block,
            "filters": filt, "format": fmt_mode, "strict": bool(strict)}).encode()).hexdigest()}
    tmp = out / "table_manifest.json.partial"
    tmp.write_text(json.dumps(manifest_out, sort_keys=True, indent=2, default=pdb._json_default) + "\n")
    os.replace(tmp, out / "table_manifest.json")
    return outputs


def verify_output_dir(path):
    """Completeness (plan §7): table_manifest.json exists and every listed file exists with its SHA-256; consumer API for streams 30/31."""
    d = Path(path)
    mp = d / "table_manifest.json"
    if not mp.is_file():
        return False
    try:
        m = json.loads(mp.read_text())
    except ValueError:
        return False
    outputs = m.get("outputs")
    if not isinstance(outputs, dict) or not outputs:
        return False
    for f, meta in outputs.items():
        p = d / f
        if not p.is_file() or not isinstance(meta, dict) or pdb.file_sha256(p) != meta.get("sha256"):
            return False
    return True


def main(argv=None):
    """CLI: --input-dir DIR (required) [--output-dir DIR] [--dataset/--scenario/--detector-family ...] [--format csv|md|both] [--strict]; exit 0 success, 2 refusal, 3 incomplete write."""
    ap = argparse.ArgumentParser(description="Stream 29: Tableau_PCA_1/2/3 from one sealed "
                                             "pca_drift_benchmark/2 run directory (read-only).")
    ap.add_argument("--input-dir", required=True, type=Path, help="run directory holding manifest.json")
    ap.add_argument("--output-dir", type=Path, default=None,
                    help="default results/pca_drift_benchmark/tables/<basename(input-dir)>/")
    ap.add_argument("--dataset", choices=pdb.ENUMS["dataset_id"], default=None)
    ap.add_argument("--scenario", choices=pdb.ENUMS["event_id"], default=None)
    ap.add_argument("--detector-family", choices=pdb.ENUMS["detector_family"], default=None)
    ap.add_argument("--format", choices=("csv", "md", "both"), default="both")
    ap.add_argument("--strict", action="store_true", help="recompute the runner identity and require equality")
    args = ap.parse_args(argv)
    problems = pdb.check_env()
    if problems:
        print("environment refused: " + "; ".join(problems), file=sys.stderr)
        return 2
    try:
        run = load_run(args.input_dir)
        validate_run(run)
        identity_status = "NOT RUN (no --strict)"
        if args.strict:
            check_identity_strict(run)
            identity_status = "PASS"
        out = args.output_dir or (pdb.REPO_ROOT / "results" / "pca_drift_benchmark" / "tables"
                                  / Path(args.input_dir).name)
        t = build_tables(run, args.dataset, args.scenario, args.detector_family)
        if out.exists() and any(out.iterdir()):
            raise Refused("OUTPUT_EXISTS", f"{out} is not empty; outputs are immutable, use a fresh directory")
        try:
            write_outputs(out, run, t, args.format, args.strict, identity_status, args.dataset, args.scenario,
                          args.detector_family)
        except OSError as exc:
            print(f"output incomplete (no table_manifest.json): {exc}", file=sys.stderr)
            return 3
        return 0
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
