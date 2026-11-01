"""Stream 30: Figure_1_mean / Figure_1_cov / Figure_1_mean_t7 from one sealed pca_drift_benchmark/2 run and its pca_drift_tables/1 tables (plan prompts/plans/plan-30.md)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments import pca_drift_benchmark as pdb
from experiments import pca_drift_tables as pdt

import argparse
import hashlib
import textwrap
import importlib
import io
import json

import numpy as np
import pandas as pd

from jepadrift.pipelines import save_fair_csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text as MplText
from matplotlib.transforms import blended_transform_factory

FIGURES_SCHEMA = "pca_drift_figures/1"
TABLES_SCHEMA = "pca_drift_tables/1"
RUN_FILES_READ = ("spectra.csv", "selection.csv", "aggregates.csv", "calibration.csv")
TABLE_FILES = {"T1": "Tableau_PCA_1.csv", "T2": "Tableau_PCA_2.csv", "T3": "Tableau_PCA_3.csv",
               "lineage": "table_lineage.csv"}
NMAX = 20
K_DOMAIN = tuple(range(1, NMAX + 1))
XTICKS = (1, 2, 5, 10, 15, 20)
MEAN_FAMILY = "MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM"
COV_FAMILY = "COV_QUADRATIC_VECH_SCAN"
ENERGY_FAMILY = "ENERGY_INCREASE_CUSUM"
BLUE = "#0072B2"
RED = "#D55E00"
GREEN = "#009E73"
DARK = "#404040"
BLACK = "#000000"
H5_PHRASE = "EXPLORATORY HEURISTIC: mean-mixture M is not a covariance detector cost"
MISMATCH_PHRASE = ("RMST differences at these k are not interpretable as speed differences at equal "
                   "false-alarm rate")
FAMILY_MISMATCH_PHRASE = "not an apples-to-apples test of two equally general detectors"
MODEL_BASED = "model-based, not observed detection speed"
SMOKE_BANNER = "SMOKE_NO_CLAIMS"
BLOCKED_CLASS = "blocked or impossible"
MEASURE_CLASS = "missing measure"
XLABEL = "k (reservoir P_k = PCA axes 1..k, frozen LW basis)"
SRC_COLS = ("figure_key", "panel", "series", "k", "y", "y_lo", "y_hi", "null_fpr", "null_fpr_lo", "null_fpr_hi",
            "status", "metric_id", "null_metric_id", "table", "row_id", "source_key")
T1_COLS = ("row_id", "k", "dataset_id", "cohort_id", "event_id", "detector_family", "cpv_lw", "cpv90_k_full",
           "cpv90_status", "rmst", "rmst_lo", "rmst_hi", "fpr_test_null", "fpr_lo", "fpr_hi", "metric_id",
           "null_metric_id", "null_id", "null_calibration_id", "status")
T2_COLS = ("row_id", "k", "dataset_id", "cohort_id", "event_id", "detector_family", "objective_kind", "V_prefix",
           "V_star", "rmst_prefix", "rmst_prefix_lo", "rmst_prefix_hi", "fpr_prefix", "fpr_prefix_lo",
           "fpr_prefix_hi", "metric_id_prefix", "null_metric_id_prefix", "rmst_selected", "rmst_selected_lo",
           "rmst_selected_hi", "fpr_selected", "fpr_selected_lo", "fpr_selected_hi", "metric_id_subset",
           "null_metric_id_subset", "status_prefix", "status_subset", "d_star", "info_kind", "claim_flag")
T3_COLS = ("row_id", "ordre", "method", "dataset_id", "cohort_id", "event_id", "detector_family", "rmst", "rmst_lo",
           "rmst_hi", "fpr", "fpr_lo", "fpr_hi", "metric_id", "null_metric_id", "null_calibration_id", "status")
LIN_COLS = ("table", "row_id", "column", "kind", "source_file", "source_key", "source_column")

SPECS = {
    "mean": {"role": "PRIMARY", "dataset_id": "SYNTH_GAUSS_EQUICORR", "event_id": "C_residual_mean",
             "detector_family": MEAN_FAMILY, "objective_kind": "MEAN_MIX_FLUID_SURROGATE", "comparator": None,
             "stem": "Figure_1_mean", "kind": "mean", "tags": [SMOKE_BANNER, "GAUSSIAN_PROXY"]},
    "mean_t7": {"role": "ROBUSTNESS", "dataset_id": "SYNTH_T7_EQUICORR", "event_id": "C_residual_mean",
                "detector_family": MEAN_FAMILY, "objective_kind": "MEAN_MIX_FLUID_SURROGATE", "comparator": None,
                "stem": "Figure_1_mean_t7", "kind": "mean",
                "tags": [SMOKE_BANNER, "GAUSSIAN_PROXY", "T7_ROBUSTNESS"]},
    "cov": {"role": "PRIMARY", "dataset_id": "SYNTH_GAUSS_EQUICORR", "event_id": "B_cov_rotate30",
            "detector_family": COV_FAMILY, "objective_kind": "COV_JOINT_MIX_HEURISTIC",
            "comparator": ("ENERGY_INDEX_COMPARATOR", ENERGY_FAMILY), "stem": "Figure_1_cov", "kind": "cov",
            "tags": [SMOKE_BANNER, "COV_SURROGATE_EXPLORATORY", "EXPLORATORY_HEURISTIC",
                     "DETECTOR_FAMILY_MISMATCH"]},
}

RC = {"font.family": "DejaVu Sans", "font.size": 7.0, "svg.hashsalt": "pca-figure-1-stream-30", "pdf.fonttype": 42,
      "svg.fonttype": "path", "axes.linewidth": 0.6, "xtick.labelsize": 6.0, "ytick.labelsize": 6.0,
      "axes.labelsize": 7.0, "legend.fontsize": 6.0, "legend.handlelength": 1.2, "legend.labelspacing": 0.25,
      "legend.borderpad": 0.2, "legend.handletextpad": 0.4}


class Refused(Exception):
    """A plan §5 refusal: printed as `refused: CODE: ...`, exit 2, nothing written."""

    def __init__(self, code, msg):
        super().__init__(f"{code}: {msg}")
        self.code = code


class Ctx:
    """Validated in-memory context: manifest, runner CSVs and table CSVs as raw text, table manifest."""

    def __init__(self, manifest, run_text, tables_text, table_manifest, input_dir, tables_dir):
        self.manifest = manifest
        self.run_text = run_text
        self.tables_text = tables_text
        self.table_manifest = table_manifest
        self.input_dir = Path(input_dir)
        self.tables_dir = Path(tables_dir)
        self._idx = {}
        self._lin = None

    def run_index(self, name):
        if name not in self._idx:
            keys = pdb.PRIMARY_KEYS[name.removesuffix(".csv")]
            fr = self.run_text[name]
            self._idx[name] = {tuple(fr.iloc[i][k] for k in keys): i for i in range(len(fr))}
        return self._idx[name]

    def run_row(self, name, source_key):
        """Runner row addressed by a canonical-JSON primary key (values normalized: None -> 'NaN', else str)."""
        want = json.loads(source_key)
        keys = pdb.PRIMARY_KEYS[name.removesuffix(".csv")]
        try:
            key = tuple("NaN" if want[k] is None else str(want[k]) for k in keys)
        except (KeyError, TypeError) as exc:
            raise Refused("LINEAGE_UNRESOLVED", f"{name} key {source_key!r} incomplete: {exc}") from exc
        idx = self.run_index(name)
        if key not in idx:
            raise Refused("LINEAGE_UNRESOLVED", f"{name} has no row for key {source_key!r}")
        return self.run_text[name].iloc[idx[key]]

    def lineage_index(self):
        if self._lin is None:
            lin = self.tables_text["lineage"]
            self._lin = {(lin.iloc[i]["table"], lin.iloc[i]["row_id"], lin.iloc[i]["column"]): i
                         for i in range(len(lin))}
        return self._lin


def _f(text):
    if text is None or text == "" or text == "NaN":
        return np.nan
    return float(text)


def _canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def save_fair_csv_text(df):
    """The exact bytes written to disk for a source frame: save_fair_csv into a buffer."""
    buf = io.StringIO()
    save_fair_csv(df, buf)
    return buf.getvalue()


def read_run_text(input_dir):
    """The four runner CSVs read by the figure, as raw text (str cells, 'NaN' kept verbatim)."""
    return {name: pd.read_csv(Path(input_dir) / name, dtype=str, keep_default_na=False)
            for name in RUN_FILES_READ}


def read_tables_text(tables_dir):
    """The four table files of a pca_drift_tables/1 output, as raw text."""
    return {key: pd.read_csv(Path(tables_dir) / fname, dtype=str, keep_default_na=False)
            for key, fname in TABLE_FILES.items()}


def load_context(input_dir, tables_dir, strict=False):
    """All §5 input/table validation, in memory, before any directory is created; raises Refused."""
    input_dir = Path(input_dir)
    tables_dir = Path(tables_dir)
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.is_file():
        raise Refused("INPUT_INVALID", "manifest.json missing")
    try:
        manifest = json.loads(manifest_path.read_text())
    except ValueError as exc:
        raise Refused("INPUT_INVALID", f"manifest.json is not JSON: {exc}") from exc
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        raise Refused("INPUT_INVALID", "manifest.outputs missing")
    for name in RUN_FILES_READ:
        p = input_dir / name
        if (not p.is_file() or not isinstance(outputs.get(name), dict)
                or pdb.file_sha256(p) != outputs[name].get("sha256")):
            raise Refused("INPUT_INVALID", f"{name} missing or its SHA-256 differs from manifest.outputs")
    if manifest.get("schema_version") != pdb.SCHEMA_VERSION or pdb.SCHEMA_VERSION != "pca_drift_benchmark/2":
        raise Refused("INPUT_INVALID", f"schema_version {manifest.get('schema_version')!r} != {pdb.SCHEMA_VERSION}")
    ident = manifest.get("identity")
    if (not isinstance(ident, dict)
            or manifest.get("run_fingerprint") != hashlib.sha256(pdb.canon(ident).encode()).hexdigest()):
        raise Refused("INPUT_INVALID", "run_fingerprint != sha256(canon(identity))")
    if not pdt.verify_output_dir(tables_dir):
        raise Refused("TABLES_INCOMPLETE", f"{tables_dir} is not a complete {TABLES_SCHEMA} output")
    table_manifest = json.loads((tables_dir / "table_manifest.json").read_text())
    if table_manifest.get("tables_schema") != TABLES_SCHEMA:
        raise Refused("TABLES_STALE", f"tables_schema {table_manifest.get('tables_schema')!r} != {TABLES_SCHEMA}")
    tin = table_manifest.get("input", {})
    if (tin.get("run_fingerprint") != manifest.get("run_fingerprint")
            or tin.get("schema_version") != pdb.SCHEMA_VERSION):
        raise Refused("TABLES_STALE", "table_manifest.input fingerprint/schema differs from the run manifest")
    tsha = tin.get("sha256", {})
    for name in RUN_FILES_READ + ("manifest.json",):
        if tsha.get(name) != pdb.file_sha256(input_dir / name):
            raise Refused("TABLES_STALE", f"table_manifest.input.sha256[{name}] differs from the file on disk")
    run_text = read_run_text(input_dir)
    tables_text = read_tables_text(tables_dir)
    for key, cols in (("T1", T1_COLS), ("T2", T2_COLS), ("T3", T3_COLS), ("lineage", LIN_COLS)):
        missing = [c for c in cols if c not in tables_text[key].columns]
        if missing:
            raise Refused("TABLE_CONTRACT_MISMATCH", f"{TABLE_FILES[key]} lacks columns {missing}")
    if strict:
        if table_manifest.get("strict") is not True:
            raise Refused("TABLES_NOT_STRICT", "table_manifest.strict is not true")
        declared = manifest["identity"].get("inputs")
        if not isinstance(declared, dict) or not declared:
            raise Refused("IDENTITY_STRICT_FAILED", "identity.inputs missing or empty")
        inputs = []
        for rel, sha in sorted(declared.items()):
            p = Path(rel)
            if p.is_absolute() or ".." in p.parts or not (pdb.REPO_ROOT / p).is_file() \
                    or pdb.file_sha256(pdb.REPO_ROOT / p) != sha:
                raise Refused("IDENTITY_STRICT_FAILED", f"declared input {rel!r} missing or hash differs")
            inputs.append(pdb.REPO_ROOT / p)
        importlib.import_module("statsmodels")
        if pdb.identity_block(manifest["config"], inputs) != manifest["identity"]:
            raise Refused("IDENTITY_STRICT_FAILED", "recomputed identity_block differs from manifest.identity")
        code = table_manifest.get("code", {})
        if (code.get("experiments/pca_drift_benchmark.py") != pdb.file_sha256(Path(pdb.__file__).resolve())
                or code.get("experiments/pca_drift_tables.py") != pdb.file_sha256(Path(pdt.__file__).resolve())):
            raise Refused("CODE_DRIFT", "table_manifest.code hashes differ from the current code")
    return Ctx(manifest, run_text, tables_text, table_manifest, input_dir, tables_dir)


def _resolve_cell(ctx, table, row_id, column):
    """One plotted cell: lineage must be a single SOURCE row resolving bit-identically in the runner."""
    key = (table, row_id, column)
    if key not in ctx.lineage_index():
        raise Refused("LINEAGE_UNRESOLVED", f"no lineage row for {table}:{row_id}:{column}")
    lr = ctx.tables_text["lineage"].iloc[ctx.lineage_index()[key]]
    if lr["kind"] != "SOURCE":
        raise Refused("LINEAGE_UNRESOLVED", f"{table}:{row_id}:{column} has lineage kind {lr['kind']}; only SOURCE cells are plotted")
    if lr["source_file"] not in RUN_FILES_READ:
        raise Refused("LINEAGE_UNRESOLVED", f"{table}:{row_id}:{column} points at unknown file {lr['source_file']!r}")
    trows = ctx.tables_text[table]
    m = trows.row_id == row_id
    if m.sum() != 1 or column not in trows.columns:
        raise Refused("LINEAGE_UNRESOLVED", f"{table}:{row_id}:{column} not an exported cell")
    cell = trows.loc[m, column].iloc[0]
    srow = ctx.run_row(lr["source_file"], lr["source_key"])
    if lr["source_column"] not in srow.index:
        raise Refused("LINEAGE_UNRESOLVED", f"{lr['source_file']} has no column {lr['source_column']!r}")
    if srow[lr["source_column"]] != cell:
        raise Refused("SOURCE_MISMATCH",
                      f"{table}:{row_id}:{column} != {lr['source_file']}[{lr['source_key']}].{lr['source_column']}")
    return cell, srow, lr["source_key"]


def _missing_class(status):
    if status.startswith("BLOCKED_") or status in ("UNSUPPORTED", "NOT_EVALUABLE_STANDARD_SPLIT", "DATA_UNAVAILABLE",
                                                   "CPV90_OUTSIDE_TOP20"):
        return BLOCKED_CLASS
    return MEASURE_CLASS


def _protocol(ctx, metric_id, null_metric_id):
    alt = ctx.run_row("aggregates.csv", _canon({"metric_id": metric_id}))
    if alt["metric_kind"] != "ALT_RMST":
        raise Refused("SOURCE_MISMATCH", f"aggregates {metric_id} is {alt['metric_kind']}, expected ALT_RMST")
    hold = ctx.run_row("aggregates.csv", _canon({"metric_id": null_metric_id}))
    if hold["metric_kind"] != "HOLDOUT_NULL_FPR":
        raise Refused("SOURCE_MISMATCH", f"aggregates {null_metric_id} is {hold['metric_kind']}, expected HOLDOUT_NULL_FPR")
    cal = ctx.run_row("calibration.csv", _canon({"null_calibration_id": alt["null_calibration_id"]}))
    for label, row in (("ALT_RMST", alt), ("HOLDOUT", hold), ("calibration", cal)):
        if row["H"] != "250":
            raise Refused("HORIZON_INCOMPATIBLE", f"{label} {metric_id} has H = {row['H']}, expected 250")
    if alt["time_origin"] != "ONSET_ALIGNED":
        raise Refused("HORIZON_INCOMPATIBLE", f"ALT_RMST {metric_id} time_origin = {alt['time_origin']!r}")
    return (alt["detector_family"], alt["null_id"], cal["threshold_rule"], cal["alpha"], cal["n_cal"], hold["n"],
            hold["H"], cal["alarm_rule"], cal["guarantee_basis"], alt["time_origin"])


def build_entry(ctx, key):
    """Validate and build one registry entry (§5, §6): source frame + render meta; raises Refused."""
    spec = SPECS[key]
    t1, t2, t3 = ctx.tables_text["T1"], ctx.tables_text["T2"], ctx.tables_text["T3"]
    m1 = ((t1.dataset_id == spec["dataset_id"]) & (t1.event_id == spec["event_id"])
          & (t1.detector_family == spec["detector_family"]))
    sel1 = t1[m1]
    if sel1.empty:
        raise Refused("BLOCK_MISSING", f"no T1 block for {spec['dataset_id']}/{spec['event_id']}/{spec['detector_family']}")
    if tuple(sorted(sel1.k.astype(int))) != K_DOMAIN:
        raise Refused("K_DOMAIN", "T1 block k set != {1..20}")
    m2 = ((t2.dataset_id == spec["dataset_id"]) & (t2.event_id == spec["event_id"])
          & (t2.detector_family == spec["detector_family"]) & (t2.objective_kind == spec["objective_kind"]))
    sel2 = t2[m2]
    if sel2.empty:
        raise Refused("BLOCK_MISSING", f"no T2 block for objective {spec['objective_kind']}")
    if tuple(sorted(sel2.k.astype(int))) != K_DOMAIN:
        raise Refused("K_DOMAIN", "T2 block k set != {1..20}")
    t1_by_k = {int(r["k"]): r for _, r in sel1.iterrows()}
    t2_by_k = {int(r["k"]): r for _, r in sel2.iterrows()}
    for k in K_DOMAIN:
        a, b = t1_by_k[k], t2_by_k[k]
        if b["metric_id_prefix"] != a["metric_id"] or b["null_metric_id_prefix"] != a["null_metric_id"]:
            raise Refused("PREFIX_IDENTITY_FAILED", f"k={k}: prefix identifiers differ from the T1 row")
        for c2, c1 in (("rmst_prefix", "rmst"), ("rmst_prefix_lo", "rmst_lo"), ("rmst_prefix_hi", "rmst_hi"),
                       ("fpr_prefix", "fpr_test_null"), ("fpr_prefix_lo", "fpr_lo"), ("fpr_prefix_hi", "fpr_hi")):
            if b[c2] != a[c1]:
                raise Refused("PREFIX_IDENTITY_FAILED", f"k={k}: T2.{c2} differs textually from T1.{c1}")
    series_text = {}
    for name, frame, row_of in (("CPV", sel1, t1_by_k), ("V_prefix", sel2, t2_by_k), ("V_star", sel2, t2_by_k),
                                ("RMST_prefix", sel1, t1_by_k), ("RMST_selected", sel2, t2_by_k)):
        col = {"CPV": "cpv_lw", "V_prefix": "V_prefix", "V_star": "V_star", "RMST_prefix": "rmst",
               "RMST_selected": "rmst_selected"}[name]
        series_text[name] = {k: row_of[k][col] for k in K_DOMAIN}
    energy_row = None
    if spec["comparator"] is not None:
        me = (t3.dataset_id == spec["dataset_id"]) & (t3.event_id == spec["event_id"]) \
            & (t3.method == spec["comparator"][0]) & (t3.detector_family == spec["comparator"][1])
        es = t3[me]
        if es.empty:
            raise Refused("BLOCK_MISSING", f"no T3 row (C) for {spec['comparator']}")
        energy_row = es.iloc[0]
        series_text["RMST_energy"] = {None: energy_row["rmst"]}
    for name, cells in series_text.items():
        if not any(v != "NaN" for v in cells.values()):
            raise Refused("EMPTY_SERIES", f"series {name} has no finite point; no figure is produced")
    resolved = {}
    for k in K_DOMAIN:
        a, b = t1_by_k[k], t2_by_k[k]
        for table, rid, col in (("T1", a["row_id"], "cpv_lw"), ("T1", a["row_id"], "rmst"),
                                ("T1", a["row_id"], "rmst_lo"), ("T1", a["row_id"], "rmst_hi"),
                                ("T1", a["row_id"], "fpr_test_null"), ("T1", a["row_id"], "fpr_lo"),
                                ("T1", a["row_id"], "fpr_hi"), ("T2", b["row_id"], "V_prefix"),
                                ("T2", b["row_id"], "V_star"), ("T2", b["row_id"], "rmst_selected"),
                                ("T2", b["row_id"], "rmst_selected_lo"), ("T2", b["row_id"], "rmst_selected_hi"),
                                ("T2", b["row_id"], "fpr_selected"), ("T2", b["row_id"], "fpr_selected_lo"),
                                ("T2", b["row_id"], "fpr_selected_hi")):
            resolved[(table, rid, col)] = _resolve_cell(ctx, table, rid, col)
    if energy_row is not None:
        rid = energy_row["row_id"]
        for col in ("rmst", "rmst_lo", "rmst_hi", "fpr", "fpr_lo", "fpr_hi"):
            resolved[("T3", rid, col)] = _resolve_cell(ctx, "T3", rid, col)
    iks = set(sel2.info_kind)
    if len(iks) != 1:
        raise Refused("V_NOT_COMPARABLE", f"info_kind varies over the T2 block: {sorted(iks)}")
    info_kind = sel2.info_kind.iloc[0]
    costs_M = ctx.manifest.get("costs", {}).get("M")
    gamma_M = ctx.manifest.get("config", {}).get("gamma_M")
    if not isinstance(costs_M, list) or len(costs_M) < NMAX or gamma_M is None:
        raise Refused("V_NOT_COMPARABLE", "manifest cost table M or gamma_M missing")
    for k in K_DOMAIN:
        b = t2_by_k[k]
        for col, d_expect in (("V_prefix", k), ("V_star", int(b["d_star"]))):
            cell, srow, _ = resolved[("T2", b["row_id"], col)]
            if cell == "NaN":
                continue
            if int(srow["d"]) != d_expect or float(srow["M_cost"]) != costs_M[d_expect - 1] \
                    or srow["info_kind"] != info_kind:
                raise Refused("V_NOT_COMPARABLE",
                              f"k={k} {col}: source row d/M_cost/info_kind inconsistent with the block cost table")
    proto_prefix = {k: _protocol(ctx, t1_by_k[k]["metric_id"], t1_by_k[k]["null_metric_id"]) for k in K_DOMAIN}
    proto_sel = {k: _protocol(ctx, t2_by_k[k]["metric_id_subset"], t2_by_k[k]["null_metric_id_subset"])
                 for k in K_DOMAIN}
    if len(set(proto_prefix.values())) != 1:
        raise Refused("SERIES_PROTOCOL_MISMATCH", "prefix protocol varies over k")
    if len(set(proto_sel.values())) != 1:
        raise Refused("SERIES_PROTOCOL_MISMATCH", "selected protocol varies over k")
    fpr_mismatch_k = []
    for k in K_DOMAIN:
        a, b = t1_by_k[k], t2_by_k[k]
        p_ok = proto_prefix[k] == proto_sel[k]
        lo_p, hi_p = _f(a["fpr_lo"]), _f(a["fpr_hi"])
        lo_s, hi_s = _f(b["fpr_selected_lo"]), _f(b["fpr_selected_hi"])
        w_ok = np.isfinite([lo_p, hi_p, lo_s, hi_s]).all() and max(lo_p, lo_s) <= min(hi_p, hi_s)
        if not (p_ok and w_ok):
            fpr_mismatch_k.append(k)
    if energy_row is not None:
        _protocol(ctx, energy_row["metric_id"], energy_row["null_metric_id"])
    missing = {}
    status_of = {}
    for name, cells in series_text.items():
        for k, v in cells.items():
            if v == "NaN":
                if name in ("CPV", "RMST_prefix"):
                    st = t1_by_k[k]["status"] if k is not None else energy_row["status"]
                elif name in ("V_prefix",):
                    st = t2_by_k[k]["status_prefix"]
                elif name in ("V_star", "RMST_selected"):
                    st = t2_by_k[k]["status_subset"]
                else:
                    st = energy_row["status"]
                missing.setdefault(name, {})[k] = _missing_class(st)
                status_of[(name, k)] = st
    rows = []
    for k in K_DOMAIN:
        a, b = t1_by_k[k], t2_by_k[k]
        rid1, rid2 = a["row_id"], b["row_id"]
        rows.append({"figure_key": key, "panel": "top_left", "series": "CPV", "k": float(k),
                     "y": _f(series_text["CPV"][k]), "y_lo": np.nan, "y_hi": np.nan,
                     "null_fpr": np.nan, "null_fpr_lo": np.nan, "null_fpr_hi": np.nan, "status": a["status"],
                     "metric_id": "NaN", "null_metric_id": "NaN", "table": "T1", "row_id": rid1,
                     "source_key": resolved[("T1", rid1, "cpv_lw")][2]})
        for col, series in (("V_prefix", "V_prefix"), ("V_star", "V_selected")):
            rows.append({"figure_key": key, "panel": "top_right", "series": series, "k": float(k),
                         "y": _f(series_text[col][k]), "y_lo": np.nan, "y_hi": np.nan,
                         "null_fpr": np.nan, "null_fpr_lo": np.nan, "null_fpr_hi": np.nan,
                         "status": b["status_prefix"] if series == "V_prefix" else b["status_subset"],
                         "metric_id": "NaN", "null_metric_id": "NaN", "table": "T2", "row_id": rid2,
                         "source_key": resolved[("T2", rid2, col)][2]})
        rows.append({"figure_key": key, "panel": "bottom", "series": "RMST_prefix", "k": float(k),
                     "y": _f(a["rmst"]), "y_lo": _f(a["rmst_lo"]), "y_hi": _f(a["rmst_hi"]),
                     "null_fpr": _f(a["fpr_test_null"]), "null_fpr_lo": _f(a["fpr_lo"]), "null_fpr_hi": _f(a["fpr_hi"]),
                     "status": a["status"], "metric_id": a["metric_id"], "null_metric_id": a["null_metric_id"],
                     "table": "T1", "row_id": rid1, "source_key": resolved[("T1", rid1, "rmst")][2]})
        rows.append({"figure_key": key, "panel": "bottom", "series": "RMST_selected", "k": float(k),
                     "y": _f(b["rmst_selected"]), "y_lo": _f(b["rmst_selected_lo"]),
                     "y_hi": _f(b["rmst_selected_hi"]), "null_fpr": _f(b["fpr_selected"]),
                     "null_fpr_lo": _f(b["fpr_selected_lo"]), "null_fpr_hi": _f(b["fpr_selected_hi"]),
                     "status": b["status_subset"], "metric_id": b["metric_id_subset"],
                     "null_metric_id": b["null_metric_id_subset"], "table": "T2", "row_id": rid2,
                     "source_key": resolved[("T2", rid2, "rmst_selected")][2]})
        if series_text["RMST_prefix"][k] == "NaN":
            rows.append({"figure_key": key, "panel": "bottom", "series": "NOT_MEASURED", "k": float(k), "y": np.nan,
                         "y_lo": np.nan, "y_hi": np.nan, "null_fpr": np.nan, "null_fpr_lo": np.nan,
                         "null_fpr_hi": np.nan, "status": status_of[("RMST_prefix", k)], "metric_id": a["metric_id"],
                         "null_metric_id": a["null_metric_id"], "table": "T1", "row_id": rid1,
                         "source_key": resolved[("T1", rid1, "rmst")][2]})
        if series_text["RMST_selected"][k] == "NaN":
            rows.append({"figure_key": key, "panel": "bottom", "series": "NOT_MEASURED", "k": float(k), "y": np.nan,
                         "y_lo": np.nan, "y_hi": np.nan, "null_fpr": np.nan, "null_fpr_lo": np.nan,
                         "null_fpr_hi": np.nan, "status": status_of[("RMST_selected", k)],
                         "metric_id": b["metric_id_subset"], "null_metric_id": b["null_metric_id_subset"],
                         "table": "T2", "row_id": rid2, "source_key": resolved[("T2", rid2, "rmst_selected")][2]})
        if k in fpr_mismatch_k:
            rows.append({"figure_key": key, "panel": "bottom", "series": "FPR_MISMATCH", "k": float(k), "y": np.nan,
                         "y_lo": np.nan, "y_hi": np.nan, "null_fpr": np.nan, "null_fpr_lo": np.nan,
                         "null_fpr_hi": np.nan, "status": "FPR_MISMATCH", "metric_id": b["metric_id_subset"],
                         "null_metric_id": b["null_metric_id_subset"], "table": "T2", "row_id": rid2,
                         "source_key": resolved[("T2", rid2, "fpr_selected")][2]})
    if energy_row is not None:
        rid = energy_row["row_id"]
        rows.append({"figure_key": key, "panel": "bottom", "series": "RMST_energy", "k": np.nan,
                     "y": _f(energy_row["rmst"]), "y_lo": _f(energy_row["rmst_lo"]), "y_hi": _f(energy_row["rmst_hi"]),
                     "null_fpr": _f(energy_row["fpr"]), "null_fpr_lo": _f(energy_row["fpr_lo"]),
                     "null_fpr_hi": _f(energy_row["fpr_hi"]), "status": energy_row["status"],
                     "metric_id": energy_row["metric_id"], "null_metric_id": energy_row["null_metric_id"],
                     "table": "T3", "row_id": rid, "source_key": resolved[("T3", rid, "rmst")][2]})
    source = pd.DataFrame(rows, columns=list(SRC_COLS))
    claims = sorted({f for v in sel2.claim_flag for f in json.loads(v)})
    k90 = t1_by_k[1]["cpv90_k_full"]
    meta = {"key": key, "kind": spec["kind"], "stem": spec["stem"],
            "title": f"Figure 1 ({spec['kind']}): {spec['event_id']}, {spec['dataset_id']}",
            "tags": list(spec["tags"]), "cpv90_k_full": None if k90 == "NaN" else int(k90),
            "cpv90_status": t1_by_k[1]["cpv90_status"], "fpr_mismatch_k": fpr_mismatch_k, "missing": missing,
            "is_cov": spec["comparator"] is not None}
    return {"key": key, "spec": spec, "source": source, "meta": meta, "fpr_mismatch_k": fpr_mismatch_k,
            "missing": missing, "claim_flags": claims}


def _outside_legend(ax, handles, y=-0.02):
    """Legend below its axes, in the reserved inter-row margin (checked in render_checks)."""
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, y), borderaxespad=0.0, frameon=False)


def _series(src, name):
    return src[src.series == name].sort_values("k").reset_index(drop=True)


def _banner_handle():
    return Line2D([], [], color="none", label=SMOKE_BANNER)


def _wrap(s, w):
    return "\n".join(textwrap.wrap(s, w, break_on_hyphens=False))


def render_figure(src, meta):
    """The whole figure, drawn only from the re-read source frame plus manifest-derived meta strings."""
    with matplotlib.rc_context(RC):
        fig = plt.figure(figsize=(3.5, 5.4))
        gs = fig.add_gridspec(2, 1, left=0.21, right=0.815, bottom=0.36, top=0.91, hspace=0.55,
                               height_ratios=(1.0, 1.1))
        ax_cpv = fig.add_subplot(gs[0, 0])
        ax_v = ax_cpv.twinx()
        ax_r = fig.add_subplot(gs[1, 0], sharex=ax_cpv)
        cpv = _series(src, "CPV")
        ax_cpv.plot(cpv.k, 100.0 * cpv.y, color=BLUE, ls="-", marker="o", ms=3, lw=1.0, label="CPV_k")
        ax_cpv.axhline(90.0, color=BLUE, lw=0.5)
        ax_cpv.set_ylim(0.0, 100.0)
        ax_cpv.set_yticks([0, 20, 40, 60, 80, 100])
        ax_cpv.yaxis.set_major_formatter(plt.FormatStrFormatter("%.0f %%"))
        ax_cpv.set_ylabel(_wrap("CPV_k (% of total LW variance, all N axes)", 26), color=BLUE)
        ax_cpv.tick_params(axis="y", colors=BLUE)
        fin = cpv[np.isfinite(cpv.y)]
        first90 = int(fin.k[fin.y >= 0.9].min()) if (fin.y >= 0.9).any() else None
        k90, st90 = meta["cpv90_k_full"], meta["cpv90_status"]
        if st90 == "CPV90_IN_TOP20" and k90 is not None and k90 <= NMAX and first90 == k90:
            ax_cpv.text(0.97, 0.97, f"CPV ≥ 90 % at k = {k90}", transform=ax_cpv.transAxes, fontsize=6,
                        va="top", ha="right")
        elif first90 is not None:
            ax_cpv.text(0.97, 0.97, f"CPV ≥ 90 % at k = {first90}", transform=ax_cpv.transAxes, fontsize=6,
                        va="top", ha="right")
        elif st90 == "CPV90_OUTSIDE_TOP20":
            ax_cpv.text(0.97, 0.97, f"CPV90 not reached within top 20 (k90_full = {k90})",
                        transform=ax_cpv.transAxes, fontsize=6, va="top", ha="right")
        vp, vs = _series(src, "V_prefix"), _series(src, "V_selected")
        ax_v.plot(vp.k, vp.y, color=RED, ls="--", marker="s", ms=3, lw=1.0, label="V_prefix P_k")
        ax_v.plot(vs.k, vs.y, color=GREEN, ls="-", marker="^", ms=3, lw=1.0, label="V_selected S*_k")
        vmax = float(np.nanmax(pd.concat([vp.y, vs.y]))) if np.isfinite(pd.concat([vp.y, vs.y])).any() else 0.0
        ax_v.set_ylim(0.0, vmax * 1.20 if vmax > 0 else 1.0)
        if meta["kind"] == "cov":
            ax_v.set_ylabel(_wrap("EXPLORATORY HEURISTIC / V_cov = I_cov_joint/M(d, γ)", 26), color=DARK)
            ax_v.text(0.04, 0.08, _wrap(H5_PHRASE, 24), transform=ax_v.transAxes, ha="left", va="bottom",
                      fontsize=6, bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": DARK, "lw": 0.5})
            pass
        else:
            ax_v.set_ylabel(_wrap("V = I_plugin/M(d, γ) (nats/day), GAUSSIAN_PROXY", 26), color=DARK)
        top_handles = [ax_cpv.lines[0], ax_v.lines[0], ax_v.lines[1],
                       Line2D([], [], color="none", label=MODEL_BASED), _banner_handle()]
        for name, color, line in (("CPV", BLUE, ax_cpv.lines[0]), ("V_prefix", RED, ax_v.lines[0]),
                                  ("V_star", GREEN, ax_v.lines[1])):
            if name in meta["missing"]:
                top_handles.append(Line2D([], [], color=color, marker="x", ls="none", label=f"{name} not measured"))
        ax_cpv.legend(handles=top_handles, loc="upper center", bbox_to_anchor=(0.5, -0.04), borderaxespad=0.0,
                      frameon=False)
        rp, rs = _series(src, "RMST_prefix"), _series(src, "RMST_selected")

        def _errbar(s, fmt, color, label):
            y = s.y.to_numpy()
            lo = s.y_lo.to_numpy()
            hi = s.y_hi.to_numpy()
            yerr = np.vstack([np.where(np.isfinite(y), y - lo, 0.0), np.where(np.isfinite(y), hi - y, 0.0)])
            return ax_r.errorbar(s.k, y, yerr=yerr, fmt=fmt, color=color, ms=3, lw=1.0, capsize=0, elinewidth=0.7,
                                 label=label)

        eb_prefix = _errbar(rp, "--s", RED, "RMST250 prefix P_k")
        eb_selected = _errbar(rs, "-^", GREEN, "RMST250 selected S*_k")
        rhandles = [eb_prefix, eb_selected]
        if meta["is_cov"]:
            en = _series(src, "RMST_energy").iloc[0]
            ax_r.axhline(float(en.y), color=BLACK, ls="-.", lw=1.0,
                         label=_wrap("ENERGY_INCREASE_CUSUM (equal-weight index, one-sided increase; no PCA axes; constant in k)", 46))
            ax_r.axhspan(float(en.y_lo), float(en.y_hi), color="0.8", alpha=0.5)
            rhandles.append(ax_r.lines[-1])
        ax_r.axhline(250.0, color="0.4", ls=":", lw=0.8, label="H = 250 (censoring cap)")
        rhandles.append(ax_r.lines[-1])
        lo_b = min(0.0, float(np.nanmin(pd.concat([rp.y_lo, rs.y_lo]))))
        hi_b = max(250.0, float(np.nanmax(pd.concat([rp.y_hi, rs.y_hi]))))
        if meta["is_cov"]:
            hi_b = max(hi_b, float(en.y_hi))
            lo_b = min(lo_b, float(en.y_lo))
        margin = 0.03 * (hi_b - lo_b) if hi_b > lo_b else 1.0
        ax_r.set_ylim(lo_b - margin, hi_b + margin)
        ax_r.set_ylabel(_wrap("RMST250 (days) = mean[min(T, 250)]", 24))
        tr = blended_transform_factory(ax_r.transData, ax_r.transAxes)
        for name, color in (("RMST_prefix", RED), ("RMST_selected", GREEN)):
            for k in meta["missing"].get(name, {}):
                ax_r.plot([k], [0.0], marker="x", color=color, ms=5, ls="none", transform=tr, clip_on=False)
        if any(n in meta["missing"] for n in ("RMST_prefix", "RMST_selected")):
            rhandles.append(Line2D([], [], color=DARK, marker="x", ls="none", label="not measured (see text legend)"))
        for k in meta["fpr_mismatch_k"]:
            ax_r.text(k, 0.98, "FPR mismatch", transform=tr, fontsize=6, ha="center", va="top", color=DARK)
        lines = []
        fpr_parts = []
        for name, s in (("prefix", rp), ("selected", rs)):
            f_ = s.null_fpr[np.isfinite(s.null_fpr)]
            lo_ = s.null_fpr_lo[np.isfinite(s.null_fpr_lo)]
            hi_ = s.null_fpr_hi[np.isfinite(s.null_fpr_hi)]
            if len(f_):
                fpr_parts.append(f"{name} [{f_.min():.3g}, {f_.max():.3g}] Wilson [{lo_.min():.3g}, {hi_.max():.3g}]")
        if meta["is_cov"]:
            fpr_parts.append(f"energy [{float(en.null_fpr):.3g}] Wilson [{float(en.null_fpr_lo):.3g}, {float(en.null_fpr_hi):.3g}]")
        if fpr_parts:
            lines.append("FPR250: " + "; ".join(fpr_parts))
        lines.append("FPR comparability (P identity + Wilson W): descriptive filter, not an equality test (n = 40)")
        for name, miss in meta["missing"].items():
            ks = sorted(k for k in miss if k is not None)
            if ks:
                cls = sorted({miss[k] for k in ks})
                lines.append(f"{name}: k = {ks} not measured ({', '.join(cls)})")
        if meta["fpr_mismatch_k"]:
            lines.append(f"FPR mismatch at k = {meta['fpr_mismatch_k']}")
            lines.append(MISMATCH_PHRASE)
        if meta["is_cov"]:
            lines.append(H5_PHRASE)
            lines.append("DETECTOR_FAMILY_MISMATCH: " + FAMILY_MISMATCH_PHRASE)
        rhandles.append(_banner_handle())
        ax_r.legend(handles=rhandles, loc="upper center", bbox_to_anchor=(0.5, -0.28), borderaxespad=0.0,
                    frameon=False)
        fig.text(0.5, 0.006, "\n".join(_wrap(l, 72) for l in lines), ha="center", va="bottom", fontsize=6)
        for ax in (ax_cpv, ax_v, ax_r):
            ax.set_xlim(0.5, 20.5)
            ax.set_xticks(XTICKS)
        plt.setp(ax_cpv.get_xticklabels(), visible=False)
        plt.setp(ax_v.get_xticklabels(), visible=False)
        ax_r.set_xlabel(XLABEL, labelpad=2)
        fig.suptitle(meta["title"] + "\n" + _wrap(" · ".join(meta["tags"]), 52), fontsize=7)
        return fig


def render_checks(fig, src, meta, png_bytes=None):
    """In-process render controls (plan §7): frame, fonts, legend/axes/xlabel/text collisions, ylim, PNG size."""
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    issues = []
    tick_texts = set()
    for ax in fig.axes:
        tick_texts.update(ax.get_xticklabels())
        tick_texts.update(ax.get_yticklabels())
    texts = [t for t in fig.findobj(MplText)
             if t.get_visible() and t.get_text().strip() and t not in tick_texts]
    font_min = min((t.get_fontsize() for t in texts), default=7.0)
    if font_min < 6.0:
        issues.append(f"font below 6 pt: {font_min}")
    text_in_frame = True
    for t in texts:
        bb = t.get_window_extent(renderer=ren)
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > fig.bbox.x1 + 0.5 or bb.y1 > fig.bbox.y1 + 0.5:
            text_in_frame = False
            issues.append(f"text outside the figure frame: {t.get_text()[:40]!r}")
    ax_bboxes = [ax.get_window_extent(ren) for ax in fig.axes]
    legend_boxes = []
    legend_disjoint = True
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is None:
            continue
        lb = leg.get_window_extent(ren)
        legend_boxes.append(lb)
        for ab in ax_bboxes:
            if lb.overlaps(ab):
                legend_disjoint = False
                issues.append("legend overlaps an axes")
        xlab = ax.xaxis.label
        if xlab.get_text() and xlab.get_visible():
            xb = xlab.get_window_extent(renderer=ren)
            if lb.overlaps(xb):
                legend_disjoint = False
                issues.append("legend overlaps its x-axis label")
    for ft in fig.texts:
        fb = ft.get_window_extent(renderer=ren)
        for lb in legend_boxes:
            if fb.overlaps(lb):
                legend_disjoint = False
                issues.append("figure text overlaps a legend")
    ylim_covers = True
    ax_cpv, ax_v, ax_r = fig.axes
    for ax, name in ((ax_cpv, "CPV"), (ax_v, "V_prefix"), (ax_v, "V_selected")):
        s = _series(src, name)
        y = 100.0 * s.y if name == "CPV" else s.y
        lo, hi = ax.get_ylim()
        if np.isfinite(y).any() and (y[np.isfinite(y)].min() < lo or y[np.isfinite(y)].max() > hi):
            ylim_covers = False
            issues.append(f"{name} outside ylim")
    lo, hi = ax_r.get_ylim()
    for name in ("RMST_prefix", "RMST_selected", "RMST_energy"):
        s = _series(src, name)
        vals = pd.concat([s.y, s.y_lo, s.y_hi])
        vals = vals[np.isfinite(vals)]
        if len(vals) and (vals.min() < lo or vals.max() > hi):
            ylim_covers = False
            issues.append(f"{name} or its interval outside ylim")
    png_size = None
    if png_bytes is not None:
        import matplotlib.image as mpimg
        png_size = tuple(mpimg.imread(io.BytesIO(png_bytes)).shape[:2])
        if png_size != (1620, 1050):
            issues.append(f"PNG size {png_size} != (1620, 1050)")
    return {"issues": issues, "text_in_frame": text_in_frame, "legend_disjoint": legend_disjoint,
            "ylim_covers": ylim_covers, "font_min": font_min, "png_size": png_size}


def figure_bytes(fig, fmt, tags):
    """Deterministic bytes of one format saved from the same Figure object."""
    meta = {"svg": {"Date": None, "Keywords": tags}, "pdf": {"CreationDate": None, "Keywords": tags},
            "png": {"Keywords": tags}}[fmt]
    buf = io.BytesIO()
    with matplotlib.rc_context(RC):
        if fmt == "png":
            fig.savefig(buf, format="png", dpi=300, metadata=meta)
        else:
            fig.savefig(buf, format=fmt, metadata=meta)
    return buf.getvalue()


def _write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def render_caption(ctx, entry, src):
    """⟨stem⟩_caption.md (English), generated from the manifest and the source frame."""
    m = ctx.manifest
    cfg = m["config"]
    syn = cfg["synthetic"]
    spec = entry["spec"]
    ds = spec["dataset_id"]
    if ds == "SYNTH_T7_EQUICORR":
        dfree = syn["backgrounds"][ds]
        law = (f"equicorrelated multivariate Student t{dfree} panel (one chi-square_{dfree} draw per day), "
               f"rho = {syn['rho']}")
    else:
        law = f"equicorrelated i.i.d. Gaussian panel, Sigma0 with rho = {syn['rho']}"
    if spec["event_id"].startswith("C_"):
        change = f"residual mean shift on axes {syn['C_axes']} scaled to I_target = {syn['C_I_target']} nats/day"
    else:
        change = f"covariance rotation of axes {syn['rotation_pair']} by theta_deg = {syn['rotation_deg']}"
    fam = spec["detector_family"]
    cal = m["calibration"]
    nc = cal["configured"]["n_cal"]
    bound = (nc["rank_r"] + 1) / (nc["n"] + 1)
    counts = cfg
    fpr_lines = []
    for name in ("RMST_prefix", "RMST_selected", "RMST_energy"):
        s = _series(src, name)
        f_ = s.null_fpr[np.isfinite(s.null_fpr)]
        if len(f_):
            fpr_lines.append(f"{name}: FPR250 in [{f_.min():.6g}, {f_.max():.6g}]")
    claims = ", ".join(entry["claim_flags"]) if entry["claim_flags"] else "NONE"
    miss = "; ".join(f"{n}: k = {sorted(k for k in v if k is not None)}" for n, v in entry["missing"].items()) or "none"
    mismatch = entry["fpr_mismatch_k"] or "none"
    return f"""# {spec['stem']} — caption (schema {FIGURES_SCHEMA})

- dataset `{ds}`: {law}; N = {cfg['N']}, T_fit = {cfg['T_fit']}, H = {cfg['H']}, nmax = {cfg['nmax']}
- change of regime: {change} (event `{spec['event_id']}`)
- reservoir: P_k = PCA axes 1..k of the frozen Ledoit-Wolf basis, k = 1..{NMAX}
- information domain: plug-in LW proxy q ({'GAUSSIAN_PROXY'}; on the Gaussian background the population joint KL is exact, on t7 it is a proxy), info_kind of the block
- detector family: `{fam}`: {m['detectors'][fam]}
- calibration: {cal['threshold_rule']}, n_cal = {nc['n']}, r = {nc['rank_r']}, bound (r+1)/(n_cal+1) = {bound:.6g}, distinct from the observed holdout FPR
- counts: smoke n = {counts['n_alt']} per role; full {m['differences_from_full']['n_alt']['full']} per role planned, not executed
- FPR250 per series (observed holdout): {'; '.join(fpr_lines)}
- RMST intervals: NORMAL_DEFF1, marginal, not truncated; no paired uncertainty is exported in this schema
- oracle flags: {claims} — diagnostic bound, not ex ante
- the 250-day cap is a natural axis limit, not evidence that a series reaches it
- missing k: {miss}; FPR mismatch k: {mismatch}

## Measured (this run)

RMST250 curves (prefix P_k vs selected S*_k, marginal intervals) and holdout FPR250 values above; smoke counts of 40 per role, {SMOKE_BANNER}.

## Model-based (not tested here)

V = I/M curves are {MODEL_BASED}; the whole right axis of the covariance figure is {H5_PHRASE if spec['comparator'] else 'not applicable'}.

## Status and limits

Tags: {' · '.join(spec['tags'])}. {SMOKE_BANNER}: no claim is made from these smoke counts.
"""


def _font_block():
    from matplotlib import font_manager
    p = font_manager.findfont("DejaVu Sans")
    return {"name": "DejaVu Sans", "file": os.path.basename(p), "sha256": pdb.file_sha256(p)}


def _env_block():
    return {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__, "MPLBACKEND": os.environ.get("MPLBACKEND"),
            **{k: os.environ.get(k) for k in pdb.REQUIRED_ENV}, "font": _font_block()}


def _select_registry(args):
    if args.dataset_id == "D3_239" or args.cohort_id is not None:
        raise Refused("REAL_FIGURE_NOT_EXECUTED_SCHEMA_2",
                      "under schema /2 no real figure is executed; no empty figure is produced")
    keys = list({"both": ("mean", "mean_t7", "cov"), "mean": ("mean", "mean_t7"), "cov": ("cov",)}[args.figure])
    for field in ("dataset_id", "event_id", "detector_family", "objective_kind"):
        value = getattr(args, field)
        if value is not None:
            keys = [k for k in keys if SPECS[k][field] == value]
    if not keys:
        raise Refused("NOT_PREDECLARED", "the selector combination is outside the predeclared registry")
    return keys


def _command_gabarit(args, rel_in, rel_tb):
    cmd = ("OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \\\n"
           f".venv/bin/python experiments/figures/plot_figure_1.py --input-dir {rel_in} --tables-dir {rel_tb} "
           "--output-dir <OUT> \\\n"
           f"  --figure {args.figure}")
    for flag, field in (("--dataset-id", "dataset_id"), ("--event-id", "event_id"), ("--cohort-id", "cohort_id"),
                        ("--detector-family", "detector_family"), ("--objective-kind", "objective_kind")):
        value = getattr(args, field)
        if value is not None:
            cmd += f" {flag} {value}"
    if args.strict:
        cmd += " --strict"
    return cmd


def verify_figures_dir(path):
    """Completeness: figure_manifest.json exists and every listed output exists with its SHA-256."""
    d = Path(path)
    mp = d / "figure_manifest.json"
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


def _render_check_md(ctx, records, checks, strict, code_sha, rel_in, rel_tb):
    m = ctx.manifest
    tm = ctx.table_manifest
    lines = ["# FIGURE_CHECK", "",
             f"- input: `{rel_in}` ; run_fingerprint `{m['run_fingerprint']}` ; schema `{m['schema_version']}` ; "
             f"run_mode `{m['run_mode']}`",
             f"- tables: `{rel_tb}` ; tables_schema `{tm['tables_schema']}` ; tables_fingerprint "
             f"`{tm['tables_fingerprint']}`",
             f"- strict checks: {'PASS' if strict else 'NOT RUN'}",
             "- code SHA-256: " + ", ".join(f"`{p}` `{s}`" for p, s in sorted(code_sha.items())), "",
             "## Runner sources read (SHA-256)"]
    for name in RUN_FILES_READ + ("manifest.json",):
        lines.append(f"- `{name}`: `{pdb.file_sha256(ctx.input_dir / name)}`")
    lines += ["", "## Table files read (SHA-256)"]
    for fname in TABLE_FILES.values():
        lines.append(f"- `{fname}`: `{pdb.file_sha256(ctx.tables_dir / fname)}`")
    lines += ["", "## Refusal chain (plan §5), all enforced in memory before any write: PASS",
              "ENV_INVALID / INPUT_INVALID / TABLES_INCOMPLETE / TABLES_STALE / TABLE_CONTRACT_MISMATCH / "
              "TABLES_NOT_STRICT / IDENTITY_STRICT_FAILED / CODE_DRIFT / NOT_PREDECLARED / "
              "REAL_FIGURE_NOT_EXECUTED_SCHEMA_2 / BLOCK_MISSING / K_DOMAIN / PREFIX_IDENTITY_FAILED / "
              "LINEAGE_UNRESOLVED / SOURCE_MISMATCH / HORIZON_INCOMPATIBLE / SERIES_PROTOCOL_MISMATCH / "
              "V_NOT_COMPARABLE / EMPTY_SERIES / OUTPUT_NOT_EMPTY", "", "## Per-figure counters and render checks"]
    for key, rec in records.items():
        chk = checks[key]
        src_rows = rec["source_rows"]
        lines.append(f"### {rec['render']['stem']} ({key}, role {rec['role']})")
        lines.append(f"- source rows: {src_rows} ; fpr_mismatch_k: {rec['fpr_mismatch_k']} ; "
                     f"missing: {rec['missing_k']}")
        lines.append(f"- render checks: text_in_frame {'PASS' if chk['text_in_frame'] else 'FAIL'} ; "
                     f"legend_disjoint {'PASS' if chk['legend_disjoint'] else 'FAIL'} ; "
                     f"ylim_covers {'PASS' if chk['ylim_covers'] else 'FAIL'} ; font_min {chk['font_min']} pt ; "
                     f"PNG {chk['png_size']} {'PASS' if chk['png_size'] == (1620, 1050) else 'FAIL'} ; "
                     f"issues: {chk['issues'] or 'none'}")
    lines += ["", "## External render checks (results recorded in logs/pca_drift_figures/ and the wrapup)",
              "- `pdftotext <OUT>/<stem>.pdf -` : expect `RMST250`, `model-based, not observed detection speed`",
              "- `pdfinfo <OUT>/<stem>.pdf`",
              "- `pdftoppm -r 100 -png <OUT>/<stem>.pdf <LOG>/<stem>.pdf_preview`",
              "- `rsvg-convert -o <LOG>/<stem>.svg_preview.png <OUT>/<stem>.svg`",
              "- `COV_SURROGATE_EXPLORATORY` present in the cov PDF text, absent from mean and mean_t7", ""]
    return "\n".join(lines)


def main(argv=None):
    """CLI: --input-dir DIR (required) [--tables-dir DIR] [--output-dir DIR] [--figure mean|cov|both] [selectors] [--strict]; exit 0 success, 2 refusal, 3 incomplete write."""
    ap = argparse.ArgumentParser(description="Stream 30: Figure_1_mean/cov/mean_t7 from one sealed "
                                             "pca_drift_benchmark/2 run and its pca_drift_tables/1 tables.")
    ap.add_argument("--input-dir", required=True, type=Path)
    ap.add_argument("--tables-dir", type=Path, default=None,
                    help="default results/pca_drift_benchmark/tables/<basename(input-dir)>/")
    ap.add_argument("--output-dir", type=Path, default=None,
                    help="default results/pca_drift_benchmark/figures/<basename(input-dir)>/")
    ap.add_argument("--figure", choices=("mean", "cov", "both"), default="both")
    ap.add_argument("--dataset-id", choices=pdb.ENUMS["dataset_id"], default=None)
    ap.add_argument("--event-id", choices=pdb.ENUMS["event_id"], default=None)
    ap.add_argument("--cohort-id", choices=pdb.ENUMS["cohort_id"], default=None)
    ap.add_argument("--detector-family", choices=pdb.ENUMS["detector_family"], default=None)
    ap.add_argument("--objective-kind", choices=pdb.ENUMS["objective_kind"], default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)
    problems = pdb.check_env()
    if problems:
        print("refused: ENV_INVALID: " + "; ".join(problems), file=sys.stderr)
        return 2
    try:
        keys = _select_registry(args)
        input_dir = args.input_dir
        tables_dir = args.tables_dir or (pdb.REPO_ROOT / "results" / "pca_drift_benchmark" / "tables"
                                         / Path(args.input_dir).name)
        out_dir = args.output_dir or (pdb.REPO_ROOT / "results" / "pca_drift_benchmark" / "figures"
                                      / Path(args.input_dir).name)
        if Path(out_dir).exists() and any(Path(out_dir).iterdir()):
            raise Refused("OUTPUT_NOT_EMPTY", f"{out_dir} is not empty; outputs are immutable, use a fresh directory")
        ctx = load_context(input_dir, tables_dir, args.strict)
        entries = [build_entry(ctx, k) for k in keys]
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        outputs = {}
        records = {}
        checks = {}

        def record(path):
            outputs[path.name] = {"sha256": pdb.file_sha256(path), "bytes": path.stat().st_size}

        for e in entries:
            stem = e["spec"]["stem"]
            text = save_fair_csv_text(e["source"])
            src = pd.read_csv(io.StringIO(text), float_precision="round_trip")
            fig = render_figure(src, e["meta"])
            tags = " ".join(e["meta"]["tags"])
            png = None
            for fmt in ("svg", "pdf", "png"):
                data = figure_bytes(fig, fmt, tags)
                if fmt == "png":
                    png = data
                _write_bytes(out / f"{stem}.{fmt}", data)
                record(out / f"{stem}.{fmt}")
            checks[e["key"]] = render_checks(fig, src, e["meta"], png_bytes=png)
            plt.close(fig)
            _write_text(out / f"{stem}_source.csv", text)
            record(out / f"{stem}_source.csv")
            _write_text(out / f"{stem}_caption.md", render_caption(ctx, e, src))
            record(out / f"{stem}_caption.md")
            records[e["key"]] = {"role": e["spec"]["role"], "spec": e["spec"], "predeclared": True,
                                 "tags": e["meta"]["tags"], "claim_flags": e["claim_flags"],
                                 "fpr_mismatch_k": e["fpr_mismatch_k"],
                                 "missing_k": {n: sorted(k for k in v if k is not None) for n, v in e["missing"].items()},
                                 "render": e["meta"], "source_rows": len(e["source"]),
                                 "outputs": [f"{stem}.{f}" for f in ("svg", "pdf", "png")]
                                            + [f"{stem}_source.csv", f"{stem}_caption.md"]}
        rel_in = pdb._rel(input_dir)
        rel_tb = pdb._rel(tables_dir)
        code_sha = {"experiments/figures/plot_figure_1.py": pdb.file_sha256(Path(__file__).resolve()),
                    "experiments/pca_drift_tables.py": pdb.file_sha256(Path(pdt.__file__).resolve()),
                    "experiments/pca_drift_benchmark.py": pdb.file_sha256(Path(pdb.__file__).resolve())}
        _write_text(out / "FIGURE_CHECK.md",
                    _render_check_md(ctx, records, checks, args.strict, code_sha, rel_in, rel_tb))
        record(out / "FIGURE_CHECK.md")
        input_block = {"path": rel_in, "run_fingerprint": ctx.manifest["run_fingerprint"],
                       "schema_version": ctx.manifest["schema_version"], "run_mode": ctx.manifest["run_mode"],
                       "sha256": {name: pdb.file_sha256(ctx.input_dir / name)
                                  for name in RUN_FILES_READ + ("manifest.json",)}}
        tables_block = {"path": rel_tb, "tables_schema": ctx.table_manifest["tables_schema"],
                        "tables_fingerprint": ctx.table_manifest["tables_fingerprint"],
                        "sha256": {fname: pdb.file_sha256(ctx.tables_dir / fname) for fname in TABLE_FILES.values()}}
        env_block = _env_block()
        filt = {"figure": args.figure, "dataset_id": args.dataset_id, "event_id": args.event_id,
                "cohort_id": args.cohort_id, "detector_family": args.detector_family,
                "objective_kind": args.objective_kind}
        manifest_out = {
            "figures_schema": FIGURES_SCHEMA, "input": input_block, "tables": tables_block, "code": code_sha,
            "environment": env_block, "filters": filt, "strict": bool(args.strict),
            "command": _command_gabarit(args, rel_in, rel_tb), "records": records, "outputs": outputs,
            "figures_fingerprint": hashlib.sha256(pdb.canon({
                "figures_schema": FIGURES_SCHEMA, "input": input_block, "tables": tables_block, "code": code_sha,
                "environment": env_block, "filters": filt, "strict": bool(args.strict)}).encode()).hexdigest()}
        tmp = out / "figure_manifest.json.partial"
        _write_text(tmp, json.dumps(manifest_out, sort_keys=True, indent=2, default=pdb._json_default) + "\n")
        os.replace(tmp, out / "figure_manifest.json")
        return 0
    except OSError as exc:
        print(f"output incomplete (no figure_manifest.json): {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
