"""Tests of experiments/figures/plot_figure_1.py (stream 30): predeclared registry, refusal codes, rendering, determinism."""
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from experiments import pca_drift_benchmark as pdb
from experiments import pca_drift_tables as pdt
from experiments.figures import plot_figure_1 as pf

REPO = Path(__file__).resolve().parents[1]
IN = REPO / "results" / "pca_drift_benchmark" / "smoke_predictive_v2_closeout"
TABLES = REPO / "results" / "pca_drift_benchmark" / "tables" / "smoke_predictive_v2_closeout"
STEMS = ("Figure_1_mean", "Figure_1_mean_t7", "Figure_1_cov")
BANNED = ("peak", "plateau", "floor", "≈", "faster", "outperform", "superior", "collapse", "explod")


def _g(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "NaN"
    return f"{v:.17g}"


def _canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def _tiny_ctx(cpv=None, cpv90_status="CPV90_OUTSIDE_TOP20", cpv90_k_full=158, nan_k=(6,), sel_all_nan=False,
              sel_fpr_disjoint_k=()):
    """Fixture (a): tiny in-memory context for the predeclared entry `mean`, k = 1..20, no disk I/O."""
    ks = list(range(1, 21))
    ds, ev, fam, obj = "SYNTH_GAUSS_EQUICORR", "C_residual_mean", "MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM", "MEAN_MIX_FLUID_SURROGATE"
    if cpv is None:
        cpv = [0.20 + 0.40 * (k - 1) / 19 for k in ks]
    costs = [1.0 + 0.01 * d for d in ks]
    v_prefix = {k: 0.10 * k for k in ks}
    v_star = 0.05
    rmst_pre = {k: (np.nan if k in nan_k else 100.0) for k in ks}
    rmst_sel = {k: (np.nan if sel_all_nan else 90.0) for k in ks}
    fpr_pre = {k: 0.05 for k in ks}
    lo_pre, hi_pre = 0.01, 0.16
    fpr_sel = {k: (0.5 if k in sel_fpr_disjoint_k else 0.05) for k in ks}
    lo_sel = {k: (0.30 if k in sel_fpr_disjoint_k else 0.01) for k in ks}
    hi_sel = {k: (0.70 if k in sel_fpr_disjoint_k else 0.16) for k in ks}
    status_pre = {k: ("CALIBRATION_FAILED" if k in nan_k else "OK") for k in ks}

    spectra = pd.DataFrame([{"dataset_id": ds, "basis_hash": "bh1", "k": str(k), "cpv_lw": _g(cpv[k - 1]),
                             "cpv90_k_full": str(cpv90_k_full), "cpv90_status": cpv90_status} for k in ks])
    sel_rows = []
    for k in ks:
        sel_rows.append({"selection_id": f"e1sel{k}", "experiment": "E1", "row_kind": "SELECTED", "d": str(k),
                         "dataset_id": ds, "event_id": ev, "detector_family": fam, "objective_kind": "NONE",
                         "V_mix": _g(v_prefix[k]), "M_cost": _g(costs[k - 1]), "info_kind": "MEAN_GAUSS_PLUGIN_LW",
                         "status": "OK"})
        sel_rows.append({"selection_id": f"e2sel{k}", "experiment": "E2", "row_kind": "SELECTED", "d": "1",
                         "dataset_id": ds, "event_id": ev, "detector_family": fam, "objective_kind": obj,
                         "V_mix": _g(v_star), "M_cost": _g(costs[0]), "info_kind": "MEAN_GAUSS_PLUGIN_LW",
                         "status": "OK"})
    selection = pd.DataFrame(sel_rows)
    agg_rows = []
    for k in ks:
        pre_rmst = _g(rmst_pre[k])
        sel_rmst = _g(rmst_sel[k])
        common = {"dataset_id": ds, "event_id": ev, "detector_family": fam, "null_id": "null1",
                  "null_calibration_id": "cal1", "H": "250", "n": "40", "time_origin": "ONSET_ALIGNED"}
        agg_rows.append({**common, "metric_id": f"alt{k}", "metric_kind": "ALT_RMST", "rmst": pre_rmst,
                         "rmst_lo": "NaN" if np.isnan(rmst_pre[k]) else _g(95.0),
                         "rmst_hi": "NaN" if np.isnan(rmst_pre[k]) else _g(105.0),
                         "null_metric_id": f"hold{k}", "fpr": "NaN", "fpr_lo": "NaN", "fpr_hi": "NaN"})
        agg_rows.append({**common, "metric_id": f"hold{k}", "metric_kind": "HOLDOUT_NULL_FPR", "time_origin": "NaN",
                         "rmst": "NaN", "rmst_lo": "NaN", "rmst_hi": "NaN", "fpr": _g(fpr_pre[k]),
                         "fpr_lo": _g(lo_pre), "fpr_hi": _g(hi_pre), "null_metric_id": "NaN"})
        agg_rows.append({**common, "metric_id": f"alts{k}", "metric_kind": "ALT_RMST", "rmst": sel_rmst,
                         "rmst_lo": "NaN" if np.isnan(rmst_sel[k]) else _g(85.0),
                         "rmst_hi": "NaN" if np.isnan(rmst_sel[k]) else _g(95.0),
                         "null_metric_id": f"holds{k}", "fpr": "NaN", "fpr_lo": "NaN", "fpr_hi": "NaN"})
        agg_rows.append({**common, "metric_id": f"holds{k}", "metric_kind": "HOLDOUT_NULL_FPR", "time_origin": "NaN",
                         "rmst": "NaN", "rmst_lo": "NaN", "rmst_hi": "NaN", "fpr": _g(fpr_sel[k]),
                         "fpr_lo": _g(lo_sel[k]), "fpr_hi": _g(hi_sel[k]), "null_metric_id": "NaN"})
    aggregates = pd.DataFrame(agg_rows)
    calibration = pd.DataFrame([{"null_calibration_id": "cal1", "dataset_id": ds, "detector_family": fam,
                                 "threshold_rule": "predictive_exchangeable_rank_v2", "alpha": _g(0.05), "n_cal": "40",
                                 "alarm_rule": "GE", "guarantee_basis": "EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA",
                                 "H": "250"}])

    t1_rows = []
    for k in ks:
        t1_rows.append({"table": "T1", "row_id": f"T1:blk1:{k}", "block_id": "blk1", "k": str(k), "dataset_id": ds,
                        "cohort_id": "NaN", "event_id": ev, "detector_family": fam, "cpv_lw": _g(cpv[k - 1]),
                        "cpv90_k_full": str(cpv90_k_full), "cpv90_status": cpv90_status,
                        "rmst": _g(rmst_pre[k]),
                        "rmst_lo": "NaN" if np.isnan(rmst_pre[k]) else _g(95.0),
                        "rmst_hi": "NaN" if np.isnan(rmst_pre[k]) else _g(105.0),
                        "fpr_test_null": _g(fpr_pre[k]), "fpr_lo": _g(lo_pre), "fpr_hi": _g(hi_pre),
                        "metric_id": f"alt{k}", "null_metric_id": f"hold{k}", "null_id": "null1",
                        "null_calibration_id": "cal1", "status": status_pre[k]})
    t2_rows = []
    for k in ks:
        t2_rows.append({"table": "T2", "row_id": f"T2:blk2:{k}", "block_id": "blk2", "k": str(k), "dataset_id": ds,
                        "cohort_id": "NaN", "event_id": ev, "detector_family": fam, "objective_kind": obj,
                        "block_family": "MEAN", "V_prefix": _g(v_prefix[k]), "V_star": _g(v_star),
                        "rmst_prefix": _g(rmst_pre[k]),
                        "rmst_prefix_lo": "NaN" if np.isnan(rmst_pre[k]) else _g(95.0),
                        "rmst_prefix_hi": "NaN" if np.isnan(rmst_pre[k]) else _g(105.0),
                        "fpr_prefix": _g(fpr_pre[k]), "fpr_prefix_lo": _g(lo_pre), "fpr_prefix_hi": _g(hi_pre),
                        "metric_id_prefix": f"alt{k}", "null_metric_id_prefix": f"hold{k}",
                        "rmst_selected": _g(rmst_sel[k]),
                        "rmst_selected_lo": "NaN" if np.isnan(rmst_sel[k]) else _g(85.0),
                        "rmst_selected_hi": "NaN" if np.isnan(rmst_sel[k]) else _g(95.0),
                        "fpr_selected": _g(fpr_sel[k]), "fpr_selected_lo": _g(lo_sel[k]), "fpr_selected_hi": _g(hi_sel[k]),
                        "metric_id_subset": f"alts{k}", "null_metric_id_subset": f"holds{k}",
                        "status_prefix": status_pre[k], "status_subset": "OK", "d_star": "1",
                        "info_kind": "MEAN_GAUSS_PLUGIN_LW", "claim_flag": '["ORACLE_INJECTED_DELTA"]',
                        "n_cal": "40"})
    t3 = pd.DataFrame(columns=list(pf.T3_COLS))

    lin = []
    for k in ks:
        rid1, rid2 = f"T1:blk1:{k}", f"T2:blk2:{k}"
        lin.append({"table": "T1", "row_id": rid1, "column": "cpv_lw", "kind": "SOURCE", "source_file": "spectra.csv",
                    "source_key": _canon({"basis_hash": "bh1", "dataset_id": ds, "k": k}), "source_column": "cpv_lw"})
        for col, mid, scol in (("rmst", f"alt{k}", "rmst"), ("rmst_lo", f"alt{k}", "rmst_lo"),
                               ("rmst_hi", f"alt{k}", "rmst_hi"), ("fpr_test_null", f"hold{k}", "fpr"),
                               ("fpr_lo", f"hold{k}", "fpr_lo"), ("fpr_hi", f"hold{k}", "fpr_hi")):
            lin.append({"table": "T1", "row_id": rid1, "column": col, "kind": "SOURCE",
                        "source_file": "aggregates.csv", "source_key": _canon({"metric_id": mid}),
                        "source_column": scol})
        lin.append({"table": "T2", "row_id": rid2, "column": "V_prefix", "kind": "SOURCE",
                    "source_file": "selection.csv",
                    "source_key": _canon({"d": str(k), "experiment": "E1", "row_kind": "SELECTED",
                                          "selection_id": f"e1sel{k}"}),
                    "source_column": "V_mix"})
        lin.append({"table": "T2", "row_id": rid2, "column": "V_star", "kind": "SOURCE", "source_file": "selection.csv",
                    "source_key": _canon({"d": "1", "experiment": "E2", "row_kind": "SELECTED",
                                          "selection_id": f"e2sel{k}"}),
                    "source_column": "V_mix"})
        for col, mid, scol in (("rmst_selected", f"alts{k}", "rmst"), ("rmst_selected_lo", f"alts{k}", "rmst_lo"),
                               ("rmst_selected_hi", f"alts{k}", "rmst_hi"), ("fpr_selected", f"holds{k}", "fpr"),
                               ("fpr_selected_lo", f"holds{k}", "fpr_lo"), ("fpr_selected_hi", f"holds{k}", "fpr_hi")):
            lin.append({"table": "T2", "row_id": rid2, "column": col, "kind": "SOURCE",
                        "source_file": "aggregates.csv", "source_key": _canon({"metric_id": mid}),
                        "source_column": scol})
    lineage = pd.DataFrame(lin)

    manifest = {
        "schema_version": "pca_drift_benchmark/2", "run_mode": "smoke",
        "run_fingerprint": "0" * 64,
        "config": {"H": 250, "N": 239, "T_fit": 1000, "alpha": 0.05, "gamma_M": 504, "nmax": 20, "seed": 42,
                   "n_alt": 40, "n_cal": 40, "n_null": 40, "n_center": 40, "mode": "smoke",
                   "synthetic": {"C_I_target": 3.0, "C_axes": [10, 20], "rho": 0.4, "rotation_deg": 30.0,
                                 "rotation_pair": [1, 2],
                                 "backgrounds": {"SYNTH_GAUSS_EQUICORR": None, "SYNTH_T7_EQUICORR": 7}}},
        "costs": {"M": costs},
        "detectors": {fam: "test scan detector", "COV_QUADRATIC_VECH_SCAN": "cov scan",
                      "ENERGY_INCREASE_CUSUM": "energy cusum"},
        "calibration": {"threshold_rule": "predictive_exchangeable_rank_v2",
                        "configured": {"n_cal": {"n": 40, "predictive_bound": 2 / 41, "rank_r": 1}}},
        "differences_from_full": {"n_alt": {"full": 2000, "smoke": 40}},
    }
    run_text = {"spectra.csv": spectra, "selection.csv": selection, "aggregates.csv": aggregates,
                "calibration.csv": calibration}
    tables_text = {"T1": pd.DataFrame(t1_rows), "T2": pd.DataFrame(t2_rows), "T3": t3, "lineage": lineage}
    return pf.Ctx(manifest, run_text, tables_text, {}, Path("in"), Path("tb"))


@pytest.fixture(scope="module")
def tables(tmp_path_factory):
    d = tmp_path_factory.mktemp("tables")
    assert pdt.main(["--input-dir", str(IN), "--output-dir", str(d), "--strict"]) == 0
    return d


@pytest.fixture(scope="module")
def fig_run(tmp_path_factory, tables):
    out = tmp_path_factory.mktemp("fig") / "out"
    rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(out), "--strict"])
    assert rc == 0
    return out


def _run_main(monkeypatch, tables_dir, out, *extra):
    argv = ["--input-dir", str(IN), "--tables-dir", str(tables_dir), "--output-dir", str(out), *extra]
    return pf.main(argv)


def _patch(monkeypatch, name, mutate):
    orig = getattr(pf, name)
    def patched(*a, **kw):
        obj = orig(*a, **kw)
        mutate(obj)
        return obj
    monkeypatch.setattr(pf, name, patched)


class TestG1Chain:
    def test_registry_specs(self):
        assert set(pf.SPECS) == {"mean", "mean_t7", "cov"}
        assert pf.SPECS["mean"]["stem"] == "Figure_1_mean" and pf.SPECS["mean"]["role"] == "PRIMARY"
        assert pf.SPECS["mean_t7"]["role"] == "ROBUSTNESS" and pf.SPECS["mean_t7"]["stem"] == "Figure_1_mean_t7"
        assert pf.SPECS["cov"]["stem"] == "Figure_1_cov"
        assert pf.SPECS["cov"]["comparator"] == ("ENERGY_INDEX_COMPARATOR", "ENERGY_INCREASE_CUSUM")

    def test_smoke_accepted_three_records_and_source_equals_runner(self, fig_run):
        man = json.loads((fig_run / "figure_manifest.json").read_text())
        assert set(man["records"]) == {"mean", "cov", "mean_t7"}
        assert man["figures_schema"] == "pca_drift_figures/1"
        assert pf.verify_figures_dir(fig_run)
        assert len(list(fig_run.iterdir())) == 17
        agg = pd.read_csv(IN / "aggregates.csv", dtype=str, keep_default_na=False).set_index("metric_id")
        for stem in STEMS:
            src = pd.read_csv(fig_run / f"{stem}_source.csv", dtype=str, keep_default_na=False)
            assert list(src.columns) == list(pf.SRC_COLS)
            for _, r in src.iterrows():
                if r["series"].startswith("RMST") and r["metric_id"] != "NaN":
                    assert r["y"] == agg.loc[r["metric_id"], "rmst"]
                    assert r["null_fpr"] == agg.loc[r["null_metric_id"], "fpr"]
            for series in ("CPV", "V_prefix", "V_selected", "RMST_prefix", "RMST_selected"):
                ks = sorted(src.loc[src.series == series, "k"].dropna().astype(int))
                if series in ("CPV", "V_prefix", "V_selected", "RMST_prefix", "RMST_selected") and stem != "x":
                    assert ks == list(range(1, 21))
        energy = pd.read_csv(fig_run / "Figure_1_cov_source.csv", dtype=str, keep_default_na=False)
        erow = energy[energy.series == "RMST_energy"].iloc[0]
        assert erow["k"] == "NaN" and erow["table"] == "T3"

    def test_tables_incomplete_refused(self, tmp_path, tables, capsys):
        bad = tmp_path / "tables_bad"
        shutil.copytree(tables, bad)
        with open(bad / "Tableau_PCA_2.csv", "a") as f:
            f.write("x\n")
        rc = _run_main(None, bad, tmp_path / "out")
        assert rc == 2 and "TABLES_INCOMPLETE" in capsys.readouterr().err

    def test_input_invalid_altered_runner_csv(self, tmp_path, tables, capsys):
        bad_in = tmp_path / "in_bad"
        shutil.copytree(IN, bad_in)
        with open(bad_in / "aggregates.csv", "a") as f:
            f.write("x\n")
        rc = pf.main(["--input-dir", str(bad_in), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o")])
        assert rc == 2 and "INPUT_INVALID" in capsys.readouterr().err

    def test_tables_stale_altered_source_with_updated_manifest(self, tmp_path, tables, capsys):
        bad_in = tmp_path / "in_stale"
        shutil.copytree(IN, bad_in)
        p = bad_in / "spectra.csv"
        with open(p, "a") as f:
            f.write("x\n")
        m = json.loads((bad_in / "manifest.json").read_text())
        m["outputs"]["spectra.csv"]["sha256"] = pdb.file_sha256(p)
        (bad_in / "manifest.json").write_text(json.dumps(m, sort_keys=True, indent=2) + "\n")
        rc = pf.main(["--input-dir", str(bad_in), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o")])
        assert rc == 2 and "TABLES_STALE" in capsys.readouterr().err

    def test_prefix_identity_metric_id(self, monkeypatch, tables, tmp_path, capsys):
        def mut(t):
            t["T2"].loc[t["T2"].k == "3", "metric_id_prefix"] = "zzz"
        _patch(monkeypatch, "read_tables_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "PREFIX_IDENTITY_FAILED" in capsys.readouterr().err

    def test_prefix_identity_rmst_one_ulp(self, monkeypatch, tables, tmp_path, capsys):
        def mut(t):
            m = t["T2"].k == "5"
            v = float(t["T2"].loc[m, "rmst_prefix"].iloc[0])
            t["T2"].loc[m, "rmst_prefix"] = _g(np.nextafter(v, np.inf))
        _patch(monkeypatch, "read_tables_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "PREFIX_IDENTITY_FAILED" in capsys.readouterr().err

    def test_source_mismatch_altered_aggregate(self, monkeypatch, tables, tmp_path, capsys):
        def mut(frames):
            agg = frames["aggregates.csv"]
            m = agg.metric_id == "6369ebd71d1eea7c"
            v = float(agg.loc[m, "rmst"].iloc[0])
            agg.loc[m, "rmst"] = _g(np.nextafter(v, np.inf))
        _patch(monkeypatch, "read_run_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "SOURCE_MISMATCH" in capsys.readouterr().err

    def test_lineage_formula_cell_refused(self, monkeypatch, tables, tmp_path, capsys):
        def mut(t):
            lin = t["lineage"]
            m = (lin.table == "T1") & (lin.column == "rmst") & (lin.row_id.str.endswith(":1"))
            lin.loc[m, "kind"] = "FORMULA"
        _patch(monkeypatch, "read_tables_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "LINEAGE_UNRESOLVED" in capsys.readouterr().err

    def test_horizon_incompatible(self, monkeypatch, tables, tmp_path, capsys):
        def mut(frames):
            agg = frames["aggregates.csv"]
            agg.loc[agg.metric_kind == "ALT_RMST", "H"] = "200"
        _patch(monkeypatch, "read_run_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "HORIZON_INCOMPATIBLE" in capsys.readouterr().err

    def test_series_protocol_mismatch_ncal(self, monkeypatch, tables, tmp_path, capsys):
        def mut(frames):
            cal = frames["calibration.csv"]
            cal.loc[cal.null_calibration_id == cal.null_calibration_id.iloc[4], "n_cal"] = "39"
        _patch(monkeypatch, "read_run_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "SERIES_PROTOCOL_MISMATCH" in capsys.readouterr().err

    def test_v_not_comparable_info_kind(self, monkeypatch, tables, tmp_path, capsys):
        def mut(t):
            t["T2"].loc[(t["T2"].k == "7") & (t["T2"].objective_kind == "MEAN_MIX_FLUID_SURROGATE")
                        & (t["T2"].event_id == "C_residual_mean"), "info_kind"] = "MEAN_OTHER"
        _patch(monkeypatch, "read_tables_text", mut)
        rc = _run_main(monkeypatch, tables, tmp_path / "out")
        assert rc == 2 and "V_NOT_COMPARABLE" in capsys.readouterr().err

    def test_empty_series_refused_no_dir(self, monkeypatch, tables, tmp_path, capsys):
        def mut(t):
            m = t["T2"].rmst_selected.notna()
            t["T2"].loc[m, "rmst_selected"] = "NaN"
            t["T2"].loc[m, ["rmst_selected_lo", "rmst_selected_hi"]] = "NaN"
        _patch(monkeypatch, "read_tables_text", mut)
        def mut2(frames):
            agg = frames["aggregates.csv"]
            m = agg.metric_id.str.startswith("x")  # no-op keeps frames identical
            assert not m.any()
        out = tmp_path / "out"
        rc = _run_main(monkeypatch, tables, out)
        assert rc == 2 and "EMPTY_SERIES" in capsys.readouterr().err
        assert not out.exists()

    def test_tiny_entry_builds(self):
        ctx = _tiny_ctx()
        e = pf.build_entry(ctx, "mean")
        assert e["meta"]["stem"] == "Figure_1_mean"
        assert len(e["source"]) > 0
        assert e["fpr_mismatch_k"] == []
        assert 6 in e["missing"]["RMST_prefix"]


class TestG2Cli:
    def test_figure_mean_produces_mean_and_t7(self, tables, tmp_path):
        out = tmp_path / "out"
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(out),
                      "--figure", "mean"])
        assert rc == 0
        assert {p.name for p in out.iterdir() if p.suffix == ".png"} == {"Figure_1_mean.png", "Figure_1_mean_t7.png"}
        man = json.loads((out / "figure_manifest.json").read_text())
        assert set(man["records"]) == {"mean", "mean_t7"}

    def test_selectors_matching_registry_accepted(self, tables, tmp_path):
        out = tmp_path / "out"
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(out),
                      "--figure", "both", "--dataset-id", "SYNTH_GAUSS_EQUICORR", "--event-id", "B_cov_rotate30"])
        assert rc == 0
        man = json.loads((out / "figure_manifest.json").read_text())
        assert set(man["records"]) == {"cov"}

    def test_strict_passes_on_smoke(self, fig_run):
        man = json.loads((fig_run / "figure_manifest.json").read_text())
        assert man["strict"] is True

    def test_event_not_predeclared(self, tables, tmp_path, capsys):
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o"),
                      "--event-id", "A_market_mean"])
        assert rc == 2 and "NOT_PREDECLARED" in capsys.readouterr().err

    def test_real_dataset_refused(self, tables, tmp_path, capsys):
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o"),
                      "--dataset-id", "D3_239"])
        assert rc == 2 and "REAL_FIGURE_NOT_EXECUTED_SCHEMA_2" in capsys.readouterr().err

    def test_cohort_refused(self, tables, tmp_path, capsys):
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o"),
                      "--cohort-id", "cohort_retrospective_covid"])
        assert rc == 2 and "REAL_FIGURE_NOT_EXECUTED_SCHEMA_2" in capsys.readouterr().err

    def test_invalid_enum_exit2(self, tables, tmp_path):
        with pytest.raises(SystemExit) as exc:
            pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(tmp_path / "o"),
                     "--dataset-id", "NOPE"])
        assert exc.value.code == 2

    def test_non_strict_tables_under_strict(self, tables, tmp_path, capsys):
        lax = tmp_path / "tables_lax"
        shutil.copytree(tables, lax)
        mp = lax / "table_manifest.json"
        tm = json.loads(mp.read_text())
        tm["strict"] = False
        mp.write_text(json.dumps(tm, sort_keys=True, indent=2) + "\n")
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(lax), "--output-dir", str(tmp_path / "o"),
                      "--strict"])
        assert rc == 2 and "TABLES_NOT_STRICT" in capsys.readouterr().err


class TestG3Conditionals:
    def _fig(self, **kw):
        ctx = _tiny_ctx(**kw)
        e = pf.build_entry(ctx, "mean")
        text = pf.save_fair_csv_text(e["source"])
        src = pd.read_csv(__import__("io").StringIO(text), float_precision="round_trip")
        return pf.render_figure(src, e["meta"]), src, e

    def test_cpv90_annotation_at_k7(self):
        cpv = [0.5 + 0.1 * (k - 1) for k in range(1, 21)]  # crosses 0.9 at k = 5? 0.5+0.1*(k-1)>=0.9 -> k=5
        cpv = [0.2] * 6 + [0.95] + [0.96] * 13  # first >= 0.9 at k = 7
        fig, src, e = self._fig(cpv=cpv, cpv90_status="CPV90_IN_TOP20", cpv90_k_full=7)
        texts = [t.get_text() for t in fig.findobj(matplotlib.text.Text)]
        assert any("CPV ≥ 90 % at k = 7" in t for t in texts)
        assert not any("not reached" in t for t in texts)
        plt.close(fig)

    def test_cpv90_outside_note(self):
        fig, src, e = self._fig()
        texts = [t.get_text() for t in fig.findobj(matplotlib.text.Text)]
        assert any("CPV90 not reached within top 20 (k90_full = 158)" in t for t in texts)
        assert not any("CPV ≥ 90 %" in t for t in texts)
        plt.close(fig)

    def test_fpr_mismatch_marker_and_phrase(self):
        fig, src, e = self._fig(sel_fpr_disjoint_k=(3,))
        assert e["fpr_mismatch_k"] == [3]
        texts = [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text)]
        assert any("FPR mismatch" in t for t in texts)
        assert any("not interpretable as speed differences at equal false-alarm rate" in t for t in texts)
        plt.close(fig)

    def test_fpr_overlap_no_marker(self):
        fig, src, e = self._fig()
        texts = [t.get_text() for t in fig.findobj(matplotlib.text.Text)]
        assert not any("FPR mismatch" in t for t in texts)
        plt.close(fig)

    def test_banned_expressions_absent(self):
        fig, src, e = self._fig(sel_fpr_disjoint_k=(3,))
        for t in fig.findobj(matplotlib.text.Text):
            s = t.get_text()
            for b in BANNED:
                assert b not in s, (b, s)
        plt.close(fig)

    def test_only_conditional_k_equals_n(self):
        fig, src, e = self._fig(cpv=[0.2] * 6 + [0.95] + [0.96] * 13, cpv90_status="CPV90_IN_TOP20", cpv90_k_full=7)
        import re
        for t in fig.findobj(matplotlib.text.Text):
            for m in re.findall(r"k = \d+", t.get_text()):
                assert m == "k = 7" and "CPV ≥ 90 %" in t.get_text()
        plt.close(fig)


class TestG4Render:
    def test_nan_marker_and_legend_class(self):
        ctx = _tiny_ctx()
        e = pf.build_entry(ctx, "mean")
        import io
        src = pd.read_csv(io.StringIO(pf.save_fair_csv_text(e["source"])), float_precision="round_trip")
        fig = pf.render_figure(src, e["meta"])
        ax_r = fig.axes[-1]
        lines = ax_r.get_lines()
        rp = [ln for ln in lines if ln.get_marker() == "s" and ln.get_linestyle() == "--"]
        assert rp
        ydata = rp[0].get_ydata()
        assert np.isnan(ydata[5])  # k = 6
        assert any(ln.get_marker() == "x" for ln in lines)
        texts = [t.get_text() for t in fig.findobj(matplotlib.text.Text)]
        assert any("CALIBRATION_FAILED" in t or "missing measure" in t for t in texts)
        plt.close(fig)

    def test_render_checks_pass_and_limits_cover(self):
        ctx = _tiny_ctx()
        e = pf.build_entry(ctx, "mean")
        import io
        src = pd.read_csv(io.StringIO(pf.save_fair_csv_text(e["source"])), float_precision="round_trip")
        fig = pf.render_figure(src, e["meta"])
        chk = pf.render_checks(fig, src, e["meta"])
        assert chk["issues"] == []
        assert chk["text_in_frame"] and chk["legend_disjoint"] and chk["ylim_covers"]
        assert chk["font_min"] >= 6.0
        ax_r = fig.axes[-1]
        lo, hi = ax_r.get_ylim()
        sub = src[src.series.str.startswith("RMST")]
        assert lo <= np.nanmin(sub.y_lo) and hi >= np.nanmax(sub.y_hi) and hi >= 250
        styles = [(ln.get_linestyle(), ln.get_marker()) for ln in ax_r.get_lines() if ln.get_label() and not ln.get_label().startswith("_")]
        assert len(styles) == len(set(styles))
        plt.close(fig)

    def test_colors_and_png_size(self, fig_run):
        import matplotlib.image as mpimg
        for stem in STEMS:
            img = mpimg.imread(fig_run / f"{stem}.png")
            assert img.shape[:2] == (1620, 1050)
        svg_mean = (fig_run / "Figure_1_mean.svg").read_text().lower()
        assert "#0072b2" in svg_mean and "#d55e00" in svg_mean and "#009e73" in svg_mean

    def test_cov_flags_present_only_on_cov(self, fig_run):
        cov_svg = " ".join((fig_run / "Figure_1_cov.svg").read_text().split())
        for s in ("COV_SURROGATE_EXPLORATORY", pf.H5_PHRASE, "DETECTOR_FAMILY_MISMATCH"):
            assert s in cov_svg
        for stem in ("Figure_1_mean", "Figure_1_mean_t7"):
            txt = (fig_run / f"{stem}.svg").read_text()
            assert "COV_SURROGATE_EXPLORATORY" not in txt
        man = json.loads((fig_run / "figure_manifest.json").read_text())
        assert "COV_SURROGATE_EXPLORATORY" in man["records"]["cov"]["tags"]
        assert "ORACLE_TRUE_SIGMA1" in man["records"]["cov"]["claim_flags"]
        assert "COV_SURROGATE_EXPLORATORY" not in man["records"]["mean"]["tags"]
        cov_pdf = (fig_run / "Figure_1_cov.pdf").read_bytes()
        assert b"COV_SURROGATE_EXPLORATORY" in cov_pdf

    def test_cov_legend_contains_h5_and_family_mismatch(self, fig_run):
        man = json.loads((fig_run / "figure_manifest.json").read_text())
        rec = man["records"]["cov"]
        src = pd.read_csv(fig_run / f"{rec['render']['stem']}_source.csv", float_precision="round_trip")
        fig = pf.render_figure(src, rec["render"])
        texts = [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text)]
        assert any(pf.H5_PHRASE in t for t in texts)
        assert any("DETECTOR_FAMILY_MISMATCH" in t for t in texts)
        assert any("ENERGY_INCREASE_CUSUM" in t for t in texts)
        assert any("constant in k" in t for t in texts)
        plt.close(fig)

    def test_svg_mandatory_strings(self, fig_run):
        for stem in STEMS:
            txt = (fig_run / f"{stem}.svg").read_text()
            assert "RMST250" in txt
            assert "model-based, not observed detection speed" in txt
            assert "SMOKE_NO_CLAIMS" in txt


class TestG5Write:
    def test_double_run_byte_identical(self, tables, tmp_path):
        o1, o2 = tmp_path / "o1", tmp_path / "o2"
        argv = ["--input-dir", str(IN), "--tables-dir", str(tables), "--strict"]
        assert pf.main([*argv, "--output-dir", str(o1)]) == 0
        assert pf.main([*argv, "--output-dir", str(o2)]) == 0
        assert sorted(p.name for p in o1.iterdir()) == sorted(p.name for p in o2.iterdir())
        for p in sorted(o1.iterdir()):
            assert p.read_bytes() == (o2 / p.name).read_bytes(), p.name
        m1 = json.loads((o1 / "figure_manifest.json").read_text())
        m2 = json.loads((o2 / "figure_manifest.json").read_text())
        assert m1["figures_fingerprint"] == m2["figures_fingerprint"]

    def test_round_trip_from_source_csv(self, fig_run):
        man = json.loads((fig_run / "figure_manifest.json").read_text())
        for key, rec in man["records"].items():
            stem = rec["render"]["stem"]
            src = pd.read_csv(fig_run / f"{stem}_source.csv", float_precision="round_trip")
            fig = pf.render_figure(src, rec["render"])
            tags = " ".join(rec["tags"])
            for fmt in ("svg", "pdf", "png"):
                assert pf.figure_bytes(fig, fmt, tags) == (fig_run / f"{stem}.{fmt}").read_bytes()
            plt.close(fig)

    def test_no_home_paths(self, fig_run):
        for p in fig_run.iterdir():
            assert b"/home/" not in p.read_bytes(), p.name

    def test_output_not_empty_refused(self, fig_run, tables, capsys):
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(fig_run)])
        assert rc == 2 and "OUTPUT_NOT_EMPTY" in capsys.readouterr().err

    def test_oserror_exit3_no_manifest(self, monkeypatch, tables, tmp_path, capsys):
        calls = {"n": 0}
        orig = pf._write_bytes
        def boom(path, data):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("simulated disk failure")
            return orig(path, data)
        monkeypatch.setattr(pf, "_write_bytes", boom)
        out = tmp_path / "out"
        rc = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(out)])
        assert rc == 3
        assert not (out / "figure_manifest.json").exists()
        assert not pf.verify_figures_dir(out)
        monkeypatch.setattr(pf, "_write_bytes", orig)
        rc2 = pf.main(["--input-dir", str(IN), "--tables-dir", str(tables), "--output-dir", str(out)])
        assert rc2 == 2
