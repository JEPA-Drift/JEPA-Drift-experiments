"""Tests of experiments/pca_drift_tables.py (stream 29): sealed /2 input validation, tables T1-T3, rendering, CLI."""
import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from experiments import pca_drift_benchmark as pdb
from experiments import pca_drift_tables as pdt

REPO = Path(__file__).resolve().parents[1]
IN = REPO / "results" / "pca_drift_benchmark" / "smoke_predictive_v2_closeout"
RUN_FILES = ("manifest.json", "spectra.csv", "selection.csv", "calibration.csv", "trials.csv", "aggregates.csv",
             "issues.csv")


@pytest.fixture(scope="module")
def run():
    r = pdt.load_run(IN)
    pdt.validate_run(r)
    return r


@pytest.fixture()
def mut(run):
    return copy.deepcopy(run)


def _copy_run(tmp_path):
    d = tmp_path / "run"
    shutil.copytree(IN, d)
    return d


def _rewrite_manifest(d, **changes):
    p = d / "manifest.json"
    m = json.loads(p.read_text())
    m.update(changes)
    p.write_text(json.dumps(m, sort_keys=True, indent=2) + "\n")


class TestG1Input:
    def test_smoke_accepted_with_counters(self, run):
        c = run.counters
        assert c["selection_rows"] == 2422
        assert c["sel_metric_refs"] == 610 and c["sel_metric_distinct"] == 275
        assert c["s_eval"] == 418 and c["s_noeval"] == 12 and c["s_cand"] == 1800 and c["s_real"] == 192
        assert c["real_s_na"] == 72 and c["real_null_calibration_filled"] == 0
        assert c["cand_theory_filled"] == 1800
        assert c["agg_rows"] == 387 and c["alt_ok"] == 146 and c["holdout_ok"] == 106
        assert c["gauss_check"] == 6 and c["real_path"] == 129
        assert c["cal_rows"] == 106 and c["cal_ok"] == 106 and c["cal_failed"] == 0
        assert c["trials_rows"] == 14320
        assert c["trials_calibration"] == 4240 and c["trials_holdout_null"] == 4240
        assert c["trials_alternative"] == 5840
        assert c["issues_rows"] == 10

    def test_numeric_identifiers_stay_strings(self, run):
        mid = run.frames["selection"]["metric_id"]
        assert str(mid.dtype) == "str"
        assert "1005596464754033" in set(mid.dropna())
        assert int((mid == "1005596464754033").sum()) == 2

    def test_hash_mismatch_refused(self, tmp_path):
        d = _copy_run(tmp_path)
        with open(d / "aggregates.csv", "ab") as f:
            f.write(b" ")
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "HASH_MISMATCH"

    def test_schema_v1_refused(self, tmp_path):
        d = _copy_run(tmp_path)
        _rewrite_manifest(d, schema_version="pca_drift_benchmark/1")
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "SCHEMA_MISMATCH"

    def test_fingerprint_tampered_refused(self, tmp_path):
        d = _copy_run(tmp_path)
        _rewrite_manifest(d, run_fingerprint="0" * 64)
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "FINGERPRINT_MISMATCH"

    def test_trials_missing_refused(self, tmp_path):
        d = _copy_run(tmp_path)
        (d / "trials.csv").unlink()
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "TRIALS_MISSING"

    def test_duplicate_metric_id_refused(self, mut):
        agg = mut.frames["aggregates"]
        mut.frames["aggregates"] = pd.concat([agg, agg.iloc[[0]]], ignore_index=True)
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "DUPLICATE_PRIMARY_KEY"

    def test_unknown_enum_refused(self, mut):
        sel = mut.frames["selection"]
        sel.loc[sel.index[0], "status"] = "BOGUS"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "ENUM_VIOLATION"

    def test_candidate_with_metric_id_refused(self, mut):
        sel = mut.frames["selection"]
        i = sel.index[sel["row_kind"] == "CANDIDATE"][0]
        sel.loc[i, "metric_id"] = "deadbeefdeadbeef"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "UNEXPECTED_ROW_STATE"

    def test_real_row_with_null_metric_id_refused(self, mut):
        sel = mut.frames["selection"]
        i = sel.index[sel["dataset_id"] == "D3_239"][0]
        sel.loc[i, "null_metric_id"] = "deadbeefdeadbeef"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "UNEXPECTED_ROW_STATE"

    def test_selection_without_calibration_refused(self, mut):
        sel = mut.frames["selection"]
        m = ((sel["row_kind"] == "SELECTED") & (sel["status"] == "OK") & (sel["dataset_id"] != "D3_239")
             & (sel["method"] == "ORACLE_Q_MIX"))
        i = sel.index[m][0]
        sel.loc[i, "null_calibration_id"] = "zzzzzzzzzzzzzzzz"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "FOREIGN_KEY_MISSING"

    def test_foreign_null_refused(self, mut):
        sel = mut.frames["selection"]
        m = ((sel["row_kind"] == "SELECTED") & (sel["status"] == "OK") & (sel["dataset_id"] != "D3_239")
             & (sel["method"] == "ORACLE_Q_MIX"))
        idx = list(sel.index[m])
        i0 = idx[0]
        other = next(j for j in idx if sel.loc[j, "null_calibration_id"] != sel.loc[i0, "null_calibration_id"])
        sel.loc[i0, "null_metric_id"] = sel.loc[other, "null_metric_id"]
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "FOREIGN_NULL"

    def test_trial_removed_refused(self, mut):
        tri = mut.frames["trials"]
        mut.frames["trials"] = tri.iloc[1:].reset_index(drop=True)
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "TRIALS_COUNT_MISMATCH"


@pytest.fixture(scope="module")
def t1(run):
    return pdt.build_tables(run)


class TestG2Table1:
    def test_blocks_and_rows(self, t1):
        rows = t1.rows["T1"]
        assert len(rows) == 180
        blocks = {}
        for r in rows:
            blocks.setdefault(r["block_id"], []).append(r)
        assert len(blocks) == 9
        assert len({(r["dataset_id"], r["event_id"], r["detector_family"]) for r in rows if r["dataset_id"] != "D3_239"}) == 6
        for bid, rs in blocks.items():
            assert [r["k"] for r in rs] == list(range(1, 21))
            assert all(r["row_id"] == f"T1:{bid}:{r['k']}" for r in rs)
            assert all(r["d"] == r["k"] for r in rs)

    def test_cpv_monotone_and_bounded(self, t1):
        blocks = {}
        for r in t1.rows["T1"]:
            blocks.setdefault(r["block_id"], []).append(r)
        for rs in blocks.values():
            cpv = [r["cpv_lw"] for r in rs]
            synth = [c for c in cpv if c is not None]
            assert synth == sorted(synth)
            assert cpv[19] is None or cpv[19] <= 1.0

    def test_criteria_markers(self, t1):
        rows = t1.rows["T1"]
        assert all("λ<1" not in (r["criteria"] or "") for r in rows)
        assert all("CPV 90" not in (r["criteria"] or "") for r in rows)
        for ds, mpk in (("SYNTH_GAUSS_EQUICORR", 1), ("SYNTH_T7_EQUICORR", 2)):
            blk = [r for r in rows if r["dataset_id"] == ds and r["cpv_lw"] is not None]
            by_k = {r["k"]: r for r in blk}
            assert by_k[mpk]["criteria"] == "MP (corr.)"
            assert all(r["criteria"] == "—" for k, r in by_k.items() if k != mpk)
            assert all(r["cpv90_k_full"] in (152, 158) and r["cpv90_status"] == "CPV90_OUTSIDE_TOP20" for r in blk)

    def test_fpr_from_holdout_source_and_alpha_separate(self, run, t1):
        for r in t1.rows["T1"]:
            if r["null_metric_id"] is None:
                assert r["dataset_id"] == "D3_239"
                assert r["fpr_test_null"] is None and r["rmst"] is None and r["lambda_lw"] is None
                continue
            h = run.agg_ix.loc[r["null_metric_id"]]
            a = run.agg_ix.loc[r["metric_id"]]
            assert r["fpr_test_null"] == float(h["fpr"]) and r["fpr_lo"] == float(h["fpr_lo"])
            assert r["fpr_hi"] == float(h["fpr_hi"]) and r["n_eval"] == int(h["n"])
            assert r["rmst"] == float(a["rmst"]) and r["n_alt"] == int(a["n"])
            assert r["target_fpr"] == float(h["target_fpr"]) == 0.05
            assert r["fpr_lo"] <= r["fpr_test_null"] <= r["fpr_hi"]
            cal = run.cal_ix.loc[r["null_calibration_id"]]
            assert r["fpr_calibration"] == float(cal["calibration_fraction"])
            assert r["threshold_rule"] == cal["threshold_rule"] and r["guarantee_basis"] == cal["guarantee_basis"]

    def test_block_missing_k_refused(self, mut):
        sel = mut.frames["selection"]
        m = ((sel["experiment"] == "E1") & (sel["method"] == "BASELINE_PREFIX")
             & (sel["dataset_id"] == "SYNTH_GAUSS_EQUICORR") & (sel["event_id"] == "A_market_mean") & (sel["k"] == 7))
        mut.frames["selection"] = sel.drop(index=sel.index[m])
        with pytest.raises(pdt.Refused) as exc:
            pdt.build_tables(mut)
        assert exc.value.code == "T1_BLOCK_INCOMPLETE"


class TestG3Table2:
    def test_blocks_and_rows(self, run):
        t = pdt.build_tables(run)
        rows = t.rows["T2"]
        assert len(rows) == 220
        blocks = {}
        for r in rows:
            blocks.setdefault(r["block_id"], []).append(r)
        assert len(blocks) == 11
        for rs in blocks.values():
            assert [r["k"] for r in rs] == list(range(1, 21))
        assert sum(1 for r in rows if r["block_family"] == "MEAN" and r["dataset_id"] != "D3_239") == 80
        assert sum(1 for r in rows if r["block_family"] == "COV") == 80
        assert sum(1 for r in rows if r["dataset_id"] == "D3_239") == 60

    def test_prefix_cells_are_t1_objects(self, run):
        t = pdt.build_tables(run)
        t1 = {(r["dataset_id"], r["cohort_id"], r["event_id"], r["detector_family"], r["k"]): r for r in t.rows["T1"]}
        n_ident = 0
        for r in t.rows["T2"]:
            p = t1[(r["dataset_id"], r["cohort_id"], r["event_id"], r["detector_family"], r["k"])]
            assert r["metric_id_prefix"] == p["metric_id"]
            assert r["null_metric_id_prefix"] == p["null_metric_id"]
            if p["metric_id"] is not None and r["dataset_id"] != "D3_239":
                assert r["rmst_prefix"] is p["rmst"]
                assert r["fpr_prefix"] is p["fpr_test_null"]
                n_ident += 1
        assert n_ident == 160

    def test_h3_q_recipe(self, run):
        q = pdt.mean_q_vectors(run)
        assert set(q) == {(ds, ev) for ds in ("SYNTH_GAUSS_EQUICORR", "SYNTH_T7_EQUICORR")
                          for ev in ("A_market_mean", "C_residual_mean")}
        for (ds, ev), qv in q.items():
            nz = [i + 1 for i, v in enumerate(qv) if v != 0.0]
            assert nz == ([1] if ev == "A_market_mean" else list(range(10, 21)))
        sel = run.frames["selection"]
        n_sum, n_rank = 0, 0
        for r in sel.itertuples(index=False):
            if r.dataset_id not in ("SYNTH_GAUSS_EQUICORR", "SYNTH_T7_EQUICORR") or r.detector_family != pdb.MEAN:
                continue
            qv = q[(r.dataset_id, r.event_id)]
            if not pdt._isna(r.S) and not pdt._isna(r.I_plugin_lw):
                S0 = [a - 1 for a in pdb.parse_S(r.S, 20)]
                assert float(qv[S0].sum()) == float(r.I_plugin_lw)
                n_sum += 1
            if not pdt._isna(r.rank_order):
                k = int(r.reservoir_k)
                order = sorted(range(k), key=lambda j: (-qv[j], j))
                assert json.loads(r.rank_order) == [j + 1 for j in order]
                n_rank += 1
        assert n_sum == 1168 and n_rank == 1008

    def test_cov_blocks_q_na_heuristic_surrogate(self, run):
        t = pdt.build_tables(run)
        cov = [r for r in t.rows["T2"] if r["block_family"] == "COV"]
        assert len(cov) == 80
        assert all(r["q_k"] is None and r["q_source"] == "NOT_EXPORTED_SCHEMA_2" for r in cov)
        assert all(r["V_prefix_meaning"] == "COV_HEURISTIC_SURROGATE" for r in cov)
        assert all(r["V_star_meaning"] == "COV_HEURISTIC_SURROGATE" for r in cov)
        assert all(r["I_marginal_cum_prefix"] is not None for r in cov)
        mean = [r for r in t.rows["T2"] if r["block_family"] == "MEAN" and r["dataset_id"] != "D3_239"]
        assert all(r["q_source"] == "FORMULA_Q_PLUGIN" and r["q_info_type"] == "MEAN_GAUSSIAN_PROXY" for r in mean)
        assert all(r["V_star_meaning"] == "MEAN_MIX_FLUID_SURROGATE" for r in mean)

    def test_l16_prefix_identity_refused(self, mut):
        sel = mut.frames["selection"]
        m = (sel["experiment"] == "E2") & (sel["method"] == "BASELINE_PREFIX")
        sel.loc[sel.index[m][0], "metric_id"] = "ffffffffffffffff"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "L16_PREFIX_IDENTITY"

    def test_l18_beta_tampered_refused(self, mut):
        sc = mut.manifest["synthetic"]["backgrounds"]["SYNTH_GAUSS_EQUICORR"]["scenarios"]["A_market_mean"]
        sc["beta_nonzero"]["1"] = sc["beta_nonzero"]["1"] * 2.0
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "L18_Q_CONTROL"


def _coherent_calibration_failure(mut, keep_metrics=False):
    cal = mut.frames["calibration"]
    agg = mut.frames["aggregates"]
    sel = mut.frames["selection"]
    ncid = cal["null_calibration_id"].iloc[0]
    ci = cal.index[cal["null_calibration_id"] == ncid][0]
    for f in ("rank_r", "threshold", "calibration_alarms", "calibration_fraction", "predictive_bound",
              "calibration_hash"):
        cal.loc[ci, f] = np.nan
    cal.loc[ci, "status"] = "CALIBRATION_FAILED"
    am = agg["null_calibration_id"] == ncid
    mids = list(agg.loc[am, "metric_id"])
    agg.loc[am, "status"] = "CALIBRATION_FAILED"
    agg.loc[am, "execution"] = "NOT_EXECUTED"
    if not keep_metrics:
        for f in pdt.METRIC_FIELDS:
            agg.loc[am, f] = np.nan
    sm = (sel["null_calibration_id"] == ncid) | sel["metric_id"].isin(mids)
    sel.loc[sm, "status"] = "CALIBRATION_FAILED"
    sel.loc[sm, "execution"] = "NOT_EXECUTED"
    tri = mut.frames["trials"]
    mut.frames["trials"] = tri[~((tri["group_id"] == ncid) | tri["group_id"].isin(mids))]
    iss = mut.frames["issues"]
    row = iss.iloc[[0]].copy()
    scope = pdb.canon({"null_calibration_id": ncid})
    row["issue_id"] = pdb.sha16({"code": "CALIBRATION_FAILED", "scope": scope})
    row["severity"] = "BLOCKER"
    row["code"] = "CALIBRATION_FAILED"
    row["scope"] = scope
    row["message"] = "synthetic test failure"
    row["status"] = "CALIBRATION_FAILED"
    mut.frames["issues"] = pd.concat([iss, row], ignore_index=True)
    return ncid, mids


class TestG4Table3:
    def test_rows_and_groups(self, run):
        t = pdt.build_tables(run)
        rows = t.rows["T3"]
        assert len(rows) == 44
        groups = {}
        for r in rows:
            groups.setdefault(r["block_id"], []).append(r)
        assert len(groups) == 9
        real = [rs for rs in groups.values() if rs[0]["dataset_id"] == "D3_239"]
        cov = [rs for rs in groups.values() if rs[0]["dataset_id"] != "D3_239"
               and any(r["detector_family"] == pdb.COV for r in rs)]
        mean = [rs for rs in groups.values() if rs not in real and rs not in cov]
        assert (len(real), len(cov), len(mean)) == (3, 2, 4)
        assert all(len(rs) == 4 for rs in real + mean)
        assert all(len(rs) == 8 for rs in cov)
        assert [r["ordre"] for r in sorted(cov[0], key=lambda r: r["ordre"])] == ["0", "1", "2", "3", "C", "D1", "D2", "D3"]

    def test_t3_oracle_mix_equals_t2_k20(self, run):
        t = pdt.build_tables(run)
        t2 = {(r["dataset_id"], r["cohort_id"], r["event_id"], r["k"]): r for r in t.rows["T2"]
              if r["objective_kind"] == "MEAN_MIX_FLUID_SURROGATE" and r["dataset_id"] != "D3_239"}
        seen = set()
        for r in t.rows["T3"]:
            if (r["ordre"] == "2" and r["method"] == "ORACLE_Q_MIX" and r["dataset_id"] != "D3_239"
                    and r["detector_family"] == pdb.MEAN):
                p = t2[(r["dataset_id"], r["cohort_id"], r["event_id"], 20)]
                assert r["S"] == p["S_star"] and r["V_star"] == p["V_star"] and r["d_star"] == p["d_star"]
                assert r["rmst"] is p["rmst_selected"] and r["metric_id"] == p["metric_id_subset"]
                seen.add((r["dataset_id"], r["event_id"]))
        assert seen == {(ds, ev) for ds in ("SYNTH_GAUSS_EQUICORR", "SYNTH_T7_EQUICORR")
                        for ev in ("A_market_mean", "C_residual_mean")}

    def test_two_covid_cohorts_distinct_and_blocked(self, run):
        t = pdt.build_tables(run)
        covid = [r for r in t.rows["T3"] if r["event_id"] == "COVID_2020"]
        std = [r for r in covid if r["cohort_id"] == "cohort_standard_embargo"]
        retro = [r for r in covid if r["cohort_id"] == "cohort_retrospective_covid"]
        assert len(std) == 4 and len(retro) == 4
        assert all(r["rmst"] is None and r["fpr"] is None and r["metric_id"] is not None for r in std + retro)
        assert not ({r["metric_id"] for r in std} & {r["metric_id"] for r in retro})
        assert not ({r["selection_id"] for r in std} & {r["selection_id"] for r in retro})
        assert all(r["status"] == "NOT_EVALUABLE_STANDARD_SPLIT" for r in std)
        assert all(r["status"] == "BLOCKED_PRE_J4" for r in retro)

    def test_coherent_calibration_failure_kept_as_na(self, mut):
        _coherent_calibration_failure(mut)
        pdt.validate_run(mut)
        assert mut.counters["cal_failed"] == 1 and mut.counters["calfail_agg"] > 0
        t = pdt.build_tables(mut)
        row = [r for r in t.rows["T1"] if r["dataset_id"] == "SYNTH_GAUSS_EQUICORR"
               and r["event_id"] == "B_cov_rotate30" and r["k"] == 1][0]
        assert row["status"] == "CALIBRATION_FAILED" and row["rmst"] is None
        assert row["metric_id"] is not None and row["null_calibration_id"] is not None

    def test_real_exante_theory_shown_with_blocked_status(self, mut):
        sel = mut.frames["selection"]
        m = (sel["dataset_id"] == "D3_239") & (sel["experiment"] == "E3") & (sel["method"] == "EXANTE_QBAR")
        i = sel.index[m][0]
        sel.loc[i, "S"] = "[3,7]"
        sel.loc[i, "d"] = 2
        sel.loc[i, "info_kind"] = "EXANTE_QBAR_PLUGIN_LW"
        sel.loc[i, "I_objective"] = 1.5
        sel.loc[i, "M_cost"] = 1.3612992538528576
        sel.loc[i, "V_mix"] = 1.5 / 1.3612992538528576
        sel.loc[i, "rank_order"] = "[3,7]"
        sel.loc[i, "tie_broken"] = False
        pdt.validate_run(mut)
        t = pdt.build_tables(mut)
        row = [r for r in t.rows["T3"] if r["dataset_id"] == "D3_239" and r["ordre"] == "3"][0]
        assert row["I_star"] == 1.5 and row["S"] == "[3,7]" and row["d_star"] == 2
        assert row["rmst"] is None and row["fpr"] is None
        assert row["status"] in ("BLOCKED_PRE_J4", "NOT_EVALUABLE_STANDARD_SPLIT")

    def test_cov_row_relabeled_oracle_q_refused(self, mut):
        sel = mut.frames["selection"]
        m = (sel["detector_family"] == pdb.COV) & (sel["method"] == "COV_JOINT_ORACLE")
        sel.loc[sel.index[m][0], "method"] = "ORACLE_Q_MIX"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "UNEXPECTED_ROW_STATE"

    def test_real_metric_numeric_refused(self, mut):
        agg = mut.frames["aggregates"]
        m = (agg["metric_kind"] == "REAL_EVENT_PATH") & (agg["cohort_id"] == "cohort_standard_embargo")
        agg.loc[agg.index[m][0], "rmst"] = 12.5
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2"

    def test_metric_id_shared_between_cohorts_refused(self, mut):
        sel = mut.frames["selection"]
        retro = sel[(sel["dataset_id"] == "D3_239") & (sel["cohort_id"] == "cohort_retrospective_covid")
                    & (sel["method"] == "EXANTE_QBAR")]
        std = sel[(sel["dataset_id"] == "D3_239") & (sel["cohort_id"] == "cohort_standard_embargo")
                  & (sel["method"] == "EXANTE_QBAR")]
        sel.loc[retro.index[0], "metric_id"] = std["metric_id"].iloc[0]
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "COHORT_ID_SHARED"

    def test_incoherent_calibration_failure_refused(self, mut):
        _coherent_calibration_failure(mut, keep_metrics=True)
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "INCOHERENT_CALIBRATION_FAILURE"

    def test_horizon_200_refused(self, mut):
        mut.manifest["config"]["H"] = 200
        mut.frames["aggregates"]["H"] = 200
        mut.frames["calibration"]["H"] = 200
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "HORIZON_INCOMPATIBLE"

    def test_real_executed_with_frozen_json_refused(self, mut):
        agg = mut.frames["aggregates"]
        m = agg["metric_kind"] == "REAL_EVENT_PATH"
        agg.loc[agg.index[m][0], "execution"] = "EXECUTED"
        agg.loc[agg.index[m][0], "rmst"] = 12.5
        agg.loc[agg.index[m][0], "detected_during_event"] = 1.0
        mut.manifest["pre_j4"]["frozen_json_present"] = True
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2"


OUT_FILES = ["Tableau_PCA_1.csv", "Tableau_PCA_1.md", "Tableau_PCA_2.csv", "Tableau_PCA_2.md", "Tableau_PCA_3.csv",
             "Tableau_PCA_3.md", "table_lineage.csv", "TABLES_VALIDATION.md", "table_manifest.json"]


@pytest.fixture(scope="module")
def out5(tmp_path_factory):
    out = tmp_path_factory.mktemp("g5") / "shared"
    assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 0
    return out


class TestG5Write:
    def test_csv_cells_equal_source_text(self, run, out5):
        out = out5
        t1 = pd.read_csv(out / "Tableau_PCA_1.csv", dtype=str, float_precision="round_trip")
        agg = pd.read_csv(IN / "aggregates.csv", dtype=str, float_precision="round_trip").set_index("metric_id")
        spe = pd.read_csv(IN / "spectra.csv", dtype=str, float_precision="round_trip")
        cal = pd.read_csv(IN / "calibration.csv", dtype=str, float_precision="round_trip").set_index("null_calibration_id")
        row = t1[(t1["dataset_id"] == "SYNTH_GAUSS_EQUICORR") & (t1["event_id"] == "A_market_mean")
                 & (t1["k"] == "1")].iloc[0]
        assert row["fpr_test_null"] == agg.loc[row["null_metric_id"], "fpr"]
        assert row["fpr_lo"] == agg.loc[row["null_metric_id"], "fpr_lo"]
        assert row["rmst"] == agg.loc[row["metric_id"], "rmst"]
        assert row["target_fpr"] == agg.loc[row["null_metric_id"], "target_fpr"]
        assert row["fpr_calibration"] == cal.loc[row["null_calibration_id"], "calibration_fraction"]
        sp = spe[(spe["dataset_id"] == "SYNTH_GAUSS_EQUICORR") & (spe["k"] == "1")].iloc[0]
        assert row["lambda_lw"] == sp["lambda_lw"] and row["cpv_lw"] == sp["cpv_lw"]

    def test_no_zero_for_na_and_md(self, run, out5):
        out = out5
        t1 = pd.read_csv(out / "Tableau_PCA_1.csv", dtype=str)
        r = t1[t1["dataset_id"] == "D3_239"].iloc[0]
        assert pd.isna(r["rmst"]) and pd.isna(r["lambda_lw"]) and pd.isna(r["fpr_test_null"])
        md = (out / "Tableau_PCA_1.md").read_text()
        assert "SMOKE_NO_CLAIMS" in md
        assert "50.5%" in md
        assert "Méthodologie et définitions" in md

    def test_double_render_byte_identical_and_no_server_path(self, run, tmp_path):
        o1, o2 = tmp_path / "a", tmp_path / "b"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(o1), "--strict"]) == 0
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(o2), "--strict"]) == 0
        assert sorted(p.name for p in o1.iterdir()) == sorted(OUT_FILES)
        for f in OUT_FILES:
            assert (o1 / f).read_bytes() == (o2 / f).read_bytes(), f
        m1 = json.loads((o1 / "table_manifest.json").read_text())
        m2 = json.loads((o2 / "table_manifest.json").read_text())
        assert m1["tables_fingerprint"] == m2["tables_fingerprint"]
        assert "<OUT>" in m1["command"]
        for f in OUT_FILES:
            assert "/home/" not in (o1 / f).read_text(), f
        val = (o1 / "TABLES_VALIDATION.md").read_text()
        assert "identity recomputation: PASS" in val

    def test_verify_output_dir(self, run, out5, tmp_path):
        assert pdt.verify_output_dir(out5)
        empty = tmp_path / "empty"
        empty.mkdir()
        assert not pdt.verify_output_dir(empty)
        broken = tmp_path / "broken"
        shutil.copytree(out5, broken)
        (broken / "table_manifest.json").unlink()
        assert not pdt.verify_output_dir(broken)

    def test_lineage_complete_and_source_resolves(self, run, out5):
        out = out5
        lin = pd.read_csv(out / "table_lineage.csv", dtype=str, float_precision="round_trip")
        for table in ("T1", "T2", "T3"):
            csv = pd.read_csv(out / f"Tableau_PCA_{table[1]}.csv", dtype=str, float_precision="round_trip")
            cells = {(r["row_id"], c) for _, r in csv.iterrows() for c in csv.columns}
            have = {(r["row_id"], r["column"]) for _, r in lin[lin["table"] == table].iterrows()}
            assert cells <= have, table
        frames = {n: pd.read_csv(IN / f"{n}.csv", dtype=str, float_precision="round_trip")
                  for n in ("spectra", "selection", "calibration", "aggregates")}
        n_src = 0
        for r in lin[lin["kind"] == "SOURCE"].itertuples(index=False):
            if r.source_file == "manifest.json":
                continue
            n_src += 1
            assert not pd.isna(r.source_key)
            name = r.source_file[:-4]
            df = frames[name]
            key = json.loads(r.source_key)
            mask = pd.Series(True, index=df.index)
            for k, v in key.items():
                mask &= df[k].isna() if v is None else df[k].astype(str) == str(v)
            assert mask.any(), (r.source_file, r.source_key)
            assert r.source_column in df.columns
        assert n_src > 1000

    def test_filters(self, run, tmp_path):
        out = tmp_path / "f"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out), "--dataset",
                         "SYNTH_GAUSS_EQUICORR"]) == 0
        t1 = pd.read_csv(out / "Tableau_PCA_1.csv", dtype=str)
        assert set(t1["dataset_id"]) == {"SYNTH_GAUSS_EQUICORR"} and len(t1) == 60
        assert pdt.verify_output_dir(out)

    def test_format_csv_has_no_md(self, run, tmp_path):
        out = tmp_path / "c"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out), "--format", "csv"]) == 0
        assert (out / "Tableau_PCA_1.csv").exists() and not (out / "Tableau_PCA_1.md").exists()
        assert pdt.verify_output_dir(out)

    def test_output_not_empty_refused(self, run, tmp_path):
        out = tmp_path / "o"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 0
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 2

    def test_io_error_exit3_then_refusal(self, run, tmp_path, monkeypatch):
        out = tmp_path / "e"
        calls = {"n": 0}
        real_save = pdt.save_fair_csv

        def boom(df, path):
            calls["n"] += 1
            if calls["n"] > 1:
                raise OSError("simulated I/O error")
            return real_save(df, path)

        monkeypatch.setattr(pdt, "save_fair_csv", boom)
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 3
        assert not (out / "table_manifest.json").exists()
        assert not pdt.verify_output_dir(out)
        monkeypatch.undo()
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 2

    def test_unknown_filter_exit2(self, tmp_path):
        with pytest.raises(SystemExit) as exc:
            pdt.main(["--input-dir", str(IN), "--output-dir", str(tmp_path / "x"), "--dataset", "NOPE"])
        assert exc.value.code == 2


def _d6_failed_calibration(mut):
    """In-memory fixture: one real D6 calibration EXECUTED/CALIBRATION_FAILED, attached to the real rows of one
    cohort (factitious metadata only; no real return is read)."""
    cal, sel, iss = mut.frames["calibration"], mut.frames["selection"], mut.frames["issues"]
    ncid = pdb.sha16({"fixture": "real-d6-failed"})
    row = cal.iloc[[0]].copy()
    row["null_calibration_id"] = ncid
    row["null_kind"] = "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS"
    row["status"] = "CALIBRATION_FAILED"
    row["execution"] = "EXECUTED"
    for f in ("rank_r", "threshold", "calibration_alarms", "calibration_fraction", "predictive_bound",
              "calibration_hash"):
        row[f] = np.nan
    cohort = "cohort_retrospective_covid"
    sm = (sel["dataset_id"] == "D3_239") & (sel["cohort_id"] == cohort)
    row["dataset_id"] = "D3_239"
    row["cohort_id"] = cohort
    row["split_hash"] = sel.loc[sm, "split_hash"].iloc[0]
    mut.frames["calibration"] = pd.concat([cal, row], ignore_index=True)
    sel.loc[sm, "null_calibration_id"] = ncid
    issue = iss.iloc[[0]].copy()
    scope = pdb.canon({"null_calibration_id": ncid})
    issue["issue_id"] = pdb.sha16({"code": "CALIBRATION_FAILED", "scope": scope})
    issue["code"] = "CALIBRATION_FAILED"
    issue["scope"] = scope
    issue["message"] = "real D6 calibration failed (in-memory fixture)"
    mut.frames["issues"] = pd.concat([iss, issue], ignore_index=True)
    return ncid


class TestAudit1Corrections:
    """Regression tests of docs/audits/stream-29-implementation-review.md (13 points). In-memory fixtures only."""

    def test_trials_empty_frame_refused(self, mut):
        mut.frames["trials"] = mut.frames["trials"].iloc[0:0]
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "TRIALS_GROUP_MISSING"

    def test_trials_whole_calibration_group_absent_refused(self, mut):
        cal = mut.frames["calibration"]
        ncid = cal["null_calibration_id"].iloc[0]
        tri = mut.frames["trials"]
        mut.frames["trials"] = tri[tri["group_id"] != ncid]
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "TRIALS_GROUP_MISSING"

    def test_trials_calibration_role_relabeled_refused(self, mut):
        cal = mut.frames["calibration"]
        ncid = cal["null_calibration_id"].iloc[0]
        tri = mut.frames["trials"]
        mut.frames["trials"] = tri.copy()
        mut.frames["trials"].loc[tri["group_id"] == ncid, "role"] = "alternative"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "TRIALS_COUNT_MISMATCH"

    def test_trials_wrong_role_for_alt_group_refused(self, mut):
        agg = mut.frames["aggregates"]
        mid = agg.loc[agg["metric_kind"] == "ALT_RMST", "metric_id"].iloc[0]
        tri = mut.frames["trials"]
        mut.frames["trials"] = tri.copy()
        mut.frames["trials"].loc[tri["group_id"] == mid, "role"] = "holdout_null"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "TRIALS_COUNT_MISMATCH"

    def test_t3_affine_and_mix_cost_columns(self, run):
        t = pdt.build_tables(run)
        sel = run.frames["selection"]
        e3 = sel[(sel["experiment"] == "E3") & (sel["row_kind"] == "SELECTED")]
        e3 = e3[~e3["selection_id"].duplicated()].set_index("selection_id")
        aff = [r for r in t.rows["T3"] if r["objective_kind"] in ("MEAN_AFFINE_SURROGATE", "COV_JOINT_AFFINE_SURROGATE")
               and r["status"] == "OK" and r["dataset_id"] != "D3_239"]
        mix = [r for r in t.rows["T3"] if r["objective_kind"] in ("MEAN_MIX_FLUID_SURROGATE", "COV_JOINT_MIX_HEURISTIC",
               "COV_MARGINAL_MIX_DIAGNOSTIC") and r["status"] == "OK" and r["dataset_id"] != "D3_239"]
        assert len(aff) == 6 and len(mix) == 8
        for r in aff:
            s = e3.loc[r["selection_id"]]
            assert r["C_affine"] == float(s["C_affine"]) and r["M_cost"] == float(s["M_cost"])
            assert r["V_denominator"] == "C_affine" and r["V_star"] == float(s["V_affine"])
            assert r["V_star"] * r["C_affine"] == pytest.approx(r["I_star"], rel=1e-12)
        for r in mix:
            s = e3.loc[r["selection_id"]]
            assert r["V_denominator"] == "M_cost" and r["V_star"] == float(s["V_mix"])
            assert r["V_star"] * r["M_cost"] == pytest.approx(r["I_star"], rel=1e-12)

    def test_full_mode_headers_have_no_smoke_text(self, mut):
        m = mut.manifest
        m["run_mode"] = "full"
        m["config"]["mode"] = "full"
        m["config"].pop("full_counts", None)
        for f in mut.frames.values():
            if "run_mode" in f.columns:
                f["run_mode"] = "full"
        t = pdt.build_tables(mut)
        md1 = pdt.render_md(mut, t, "T1")
        assert "SMOKE_NO_CLAIMS" not in md1 and "mode `full`" in md1
        eff = [l for l in md1.splitlines() if l.startswith("- effectifs")]
        assert eff and all("smoke" not in l and "non exécuté" not in l for l in eff)
        assert "n_center = 40" in eff[0] and "n_cal = 40" in eff[0] and "n_null = 40" in eff[0] and "n_alt = 40" in eff[0]

    def test_smoke_mode_headers_keep_banner_text(self, run):
        t = pdt.build_tables(run)
        md1 = pdt.render_md(run, t, "T1")
        eff = [l for l in md1.splitlines() if l.startswith("- effectifs")]
        assert eff and "smoke" in eff[0] and "non exécuté" in eff[0]

    def test_failed_rows_must_reference_failed_calibration(self, mut):
        ncid, _ = _coherent_calibration_failure(mut)
        cal = mut.frames["calibration"]
        ci = cal.index[cal["null_calibration_id"] == ncid][0]
        cal.loc[ci, "status"] = "OK"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "INCOHERENT_CALIBRATION_FAILURE"

    def test_real_d6_failed_calibration_accepted_blocked(self, mut):
        ncid = _d6_failed_calibration(mut)
        pdt.validate_run(mut)
        assert mut.counters["cal_failed"] == 1
        assert mut.counters["real_null_calibration_filled"] > 0
        sel = mut.frames["selection"]
        assert set(sel.loc[sel["null_calibration_id"] == ncid, "status"]) <= set(pdt.REAL_STATUSES)
        t = pdt.build_tables(mut)
        rows = [r for r in t.rows["T1"] if r["null_calibration_id"] == ncid]
        assert rows and rows[0]["dataset_id"] == "D3_239"
        assert rows[0]["n_cal"] is not None and rows[0]["threshold_rule"] is not None
        assert rows[0]["guarantee_basis"] is not None
        assert rows[0]["rmst"] is None and rows[0]["fpr_test_null"] is None and rows[0]["metric_id"] is not None

    def test_real_d6_row_flipped_to_executed_refused(self, mut):
        ncid = _d6_failed_calibration(mut)
        sel = mut.frames["selection"]
        i = sel.index[sel["null_calibration_id"] == ncid][0]
        sel.loc[i, "execution"] = "EXECUTED"
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code in ("UNEXPECTED_ROW_STATE", "INCOHERENT_CALIBRATION_FAILURE")

    def test_horizon_na_refused(self, mut):
        agg = mut.frames["aggregates"]
        i = agg.index[agg["metric_kind"] == "ALT_RMST"][0]
        agg.loc[i, "H"] = np.nan
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "HORIZON_INCOMPATIBLE"

    def test_horizon_fractional_refused(self, mut):
        mut.manifest["config"]["H"] = 250.5
        agg = mut.frames["aggregates"]
        agg["H"] = agg["H"].astype("float64")
        agg.loc[agg.index[agg["metric_kind"] == "ALT_RMST"][0], "H"] = 250.5
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "HORIZON_INCOMPATIBLE"

    def test_t2_real_rows_keep_subset_ids(self, run):
        t = pdt.build_tables(run)
        real = [r for r in t.rows["T2"] if r["dataset_id"] == "D3_239"]
        assert len(real) == 60
        assert all(r["metric_id_subset"] is not None for r in real)
        assert all(r["selection_id_subset"] is not None for r in real)
        assert all(r["null_metric_id_subset"] is None for r in real)
        assert all(r["rmst_selected"] is None and r["n_alt"] is None for r in real)

    def test_family_filter_cov_on_all_outputs(self, run, tmp_path):
        out = tmp_path / "cov"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out), "--detector-family", pdb.COV]) == 0
        for tb in ("Tableau_PCA_1.csv", "Tableau_PCA_2.csv", "Tableau_PCA_3.csv"):
            df = pd.read_csv(out / tb, dtype=str)
            assert set(df["detector_family"].dropna()) == {pdb.COV}, tb
        t3 = pd.read_csv(out / "Tableau_PCA_3.csv", dtype=str)
        assert len(t3) == 14
        lin = pd.read_csv(out / "table_lineage.csv", dtype=str)
        assert set(lin["table"]) == {"T1", "T2", "T3"}
        md3 = (out / "Tableau_PCA_3.md").read_text()
        assert "Épisodes réels" not in md3
        man = json.loads((out / "table_manifest.json").read_text())
        assert man["filters"] == {"dataset": None, "scenario": None, "detector_family": pdb.COV}

    def test_family_filter_mean_keeps_t3r(self, run):
        t = pdt.build_tables(run, family=pdb.MEAN)
        assert {r["detector_family"] for r in t.rows["T3"]} == {pdb.MEAN}
        assert len(t.rows["T3"]) == 28
        assert len(t.rows["T3R"]) == 12
        assert {r["detector_family"] for r in t.rows["T1"]} == {pdb.MEAN}

    def test_scenario_filter_applies_to_t3r(self, run):
        t = pdt.build_tables(run, scenario="COVID_2020")
        assert {r["event_id"] for r in t.rows["T3R"]} == {"COVID_2020"}
        assert len(t.rows["T3R"]) == 8
        t = pdt.build_tables(run, dataset="SYNTH_GAUSS_EQUICORR")
        assert len(t.rows["T3R"]) == 0

    def test_strict_accepts_declared_extra_input(self, mut):
        m = mut.manifest
        extra = "configs/pca_drift_benchmark.yaml"
        m["identity"]["inputs"][extra] = pdb.file_sha256(pdb.REPO_ROOT / extra)
        m["identity"]["input_hash"] = hashlib.sha256(pdb.canon(m["identity"]["inputs"]).encode()).hexdigest()
        m["run_fingerprint"] = hashlib.sha256(pdb.canon(m["identity"]).encode()).hexdigest()
        assert pdt.check_identity_strict(mut) is True

    def test_strict_declared_input_hash_drift_refused(self, mut):
        mut.manifest["identity"]["inputs"]["data/derived/d3_239/splits.yaml"] = "0" * 64
        with pytest.raises(pdt.Refused) as exc:
            pdt.check_identity_strict(mut)
        assert exc.value.code == "INPUT_HASH_MISMATCH"

    def test_strict_config_drift_refused(self, mut):
        mut.manifest["config"]["alpha"] = 0.07
        with pytest.raises(pdt.Refused) as exc:
            pdt.check_identity_strict(mut)
        assert exc.value.code == "IDENTITY_MISMATCH"

    def test_lineage_unique_complete_and_resolves(self, run):
        t = pdt.build_tables(run)
        pdt.validate_lineage(run, t)
        keys = [(e["table"], e["row_id"], e["column"]) for e in t.lineage]
        assert len(keys) == len(set(keys))

    def test_lineage_duplicate_refused(self, run):
        t = pdt.build_tables(run)
        t.lineage.append(dict(t.lineage[0]))
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_lineage(run, t)
        assert exc.value.code == "LINEAGE_DUPLICATE"

    def test_lineage_manifest_paths_resolve(self, run):
        t = pdt.build_tables(run)
        n = 0
        for e in t.lineage:
            if e["kind"] == "MANIFEST":
                node = run.manifest
                for p in json.loads(e["source_key"])["path"]:
                    node = node[p]
                n += 1
        assert n > 0

    def test_tables_fingerprint_full_input_recipe(self, run, tmp_path):
        out = tmp_path / "fp"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out)]) == 0
        m = json.loads((out / "table_manifest.json").read_text())
        assert len(m["input"]["sha256"]) == 7
        rec = hashlib.sha256(pdb.canon({"tables_schema": m["tables_schema"], "input": m["input"], "code": m["code"],
                                         "environment": m["environment"], "filters": m["filters"], "format": m["format"],
                                         "strict": m["strict"]}).encode()).hexdigest()
        assert rec == m["tables_fingerprint"]

    def test_t3_md_order_rmst_dstar_fpr_and_cost_columns(self, run, tmp_path):
        out = tmp_path / "md"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out), "--format", "md"]) == 0
        md = (out / "Tableau_PCA_3.md").read_text()
        header = next(l for l in md.splitlines() if "RMST250 (jours)" in l and l.startswith("|"))
        cells = [c.strip() for c in header.strip().strip("|").split("|")]
        i_rmst, i_d, i_fpr = cells.index("RMST250 (jours)"), cells.index("Dimension retenue d*"), cells.index("FPR250")
        assert i_rmst < i_d < i_fpr
        assert "Coût affine C(d)" in cells and "Dénominateur de V" in cells
        assert "KL jointe" in " ".join(cells)

    def test_t1_md_shows_holdout_interval(self, run, tmp_path):
        out = tmp_path / "md1"
        assert pdt.main(["--input-dir", str(IN), "--output-dir", str(out), "--format", "md"]) == 0
        md = (out / "Tableau_PCA_1.md").read_text()
        assert re.search(r"\d\.\d% \[\d\.\d%, \d\.\d%\]", md)

    def test_t3_d3_rows_carry_joint_companion(self, run):
        t = pdt.build_tables(run)
        d3 = [r for r in t.rows["T3"] if r["method"] == "COV_MARGINAL_DIAGNOSTIC"]
        assert len(d3) == 2
        for r in d3:
            assert r["I_cov_joint"] is not None and r["I_cov_marginal_sum"] is not None
            assert r["I_cov_joint"] == r["I_star"]

    def test_well_hashed_malformed_csv_refused(self, tmp_path):
        d = _copy_run(tmp_path)
        p = d / "aggregates.csv"
        lines = p.read_text().splitlines()
        ci = lines[0].split(",").index("rmst")
        parts = lines[1].split(",")
        parts[ci] = "not_a_float"
        lines[1] = ",".join(parts)
        p.write_text("\n".join(lines) + "\n")
        mp = d / "manifest.json"
        m = json.loads(mp.read_text())
        m["outputs"]["aggregates.csv"]["sha256"] = pdb.file_sha256(p)
        m["outputs"]["aggregates.csv"]["bytes"] = p.stat().st_size
        mp.write_text(json.dumps(m, sort_keys=True, indent=2) + "\n")
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "CSV_PARSE_FAILED"
        assert pdt.main(["--input-dir", str(d), "--output-dir", str(tmp_path / "o")]) == 2

    def test_hash_checked_before_parsing(self, tmp_path):
        d = _copy_run(tmp_path)
        p = d / "aggregates.csv"
        lines = p.read_text().splitlines()
        ci = lines[0].split(",").index("rmst")
        parts = lines[1].split(",")
        parts[ci] = "not_a_float"
        lines[1] = ",".join(parts)
        p.write_text("\n".join(lines) + "\n")
        with pytest.raises(pdt.Refused) as exc:
            pdt.load_run(d)
        assert exc.value.code == "HASH_MISMATCH"

    def test_alt_n1_only_undefined_fields_na_accepted(self, mut):
        agg, tri = mut.frames["aggregates"], mut.frames["trials"]
        m = (agg["metric_kind"] == "ALT_RMST") & (agg["status"] == "OK")
        alt_groups = set(agg.loc[m, "metric_id"])
        for i in agg.index[m]:
            agg.loc[i, "n"] = 1
            agg.loc[i, "deff"] = 1.0
            agg.loc[i, "n_eff"] = 1.0
            for f in ("rmst_sd", "rmst_se", "rmst_lo", "rmst_hi"):
                agg.loc[i, f] = np.nan
        keep_alt = tri[tri["group_id"].isin(alt_groups)].groupby("group_id").head(1)
        mut.frames["trials"] = pd.concat([tri[~tri["group_id"].isin(alt_groups)], keep_alt], ignore_index=True)
        pdt.validate_run(mut)
        t = pdt.build_tables(mut)
        mid = sorted(alt_groups)[0]
        a = mut.agg_ix.loc[mid]
        assert float(a["deff"]) == 1.0 and float(a["n_eff"]) == 1.0
        assert np.isfinite(float(a["det_lo"])) and np.isfinite(float(a["det_hi"]))
        row = [r for r in t.rows["T1"] if r["metric_id"] == mid][0]
        assert row["rmst"] is not None and row["rmst_lo"] is None and row["rmst_hi"] is None
        assert row["n_alt"] == 1

    def test_alt_n1_core_measures_still_required(self, mut):
        agg, tri = mut.frames["aggregates"], mut.frames["trials"]
        i = agg.index[(agg["metric_kind"] == "ALT_RMST") & (agg["status"] == "OK")][0]
        mid = agg.loc[i, "metric_id"]
        agg.loc[i, "n"] = 1
        agg.loc[i, "rmst"] = np.nan
        for f in ("rmst_sd", "rmst_se", "rmst_lo", "rmst_hi"):
            agg.loc[i, f] = np.nan
        g = tri[tri["group_id"] == mid]
        mut.frames["trials"] = pd.concat([tri[tri["group_id"] != mid], g.iloc[[0]]], ignore_index=True)
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "NON_FINITE_METRIC"


class TestAudit2Corrections:
    """Regression tests of docs/audits/stream-29-implementation-rereview.md (3 remaining points); in-memory fixtures."""

    def _spectra_csv(self, tmp_path, lambda_lw):
        cols = pdb.COLUMNS["spectra"]
        row = {c: "" for c in cols}
        row.update({"schema_version": pdb.SCHEMA_VERSION, "dataset_id": "D3_239", "basis_hash": "ab" * 16,
                    "k": "1", "N": "239", "T_fit": "2781", "fit_first_day": "2016-04-07",
                    "fit_last_day": "2019-12-31", "lambda_lw": lambda_lw, "cpv_lw": "0.5"})
        p = tmp_path / "spectra.csv"
        pd.DataFrame([row], columns=cols).to_csv(p, index=False)
        return p

    def test_date_metadata_pre2020_accepted(self, tmp_path):
        df = pdt.read_run_csv(self._spectra_csv(tmp_path, "1.5"), "spectra")
        assert df["fit_first_day"].iloc[0] == "2016-04-07"
        assert df["fit_last_day"].iloc[0] == "2019-12-31"
        assert float(df["lambda_lw"].iloc[0]) == 1.5

    def test_numeric_corruption_still_refused(self, tmp_path):
        with pytest.raises(ValueError):
            pdt.read_run_csv(self._spectra_csv(tmp_path, "not_a_float"), "spectra")

    def test_spectra_dates_load_run_accepted(self, tmp_path):
        d = _copy_run(tmp_path)
        p = d / "spectra.csv"
        df = pd.read_csv(p, dtype=str, float_precision="round_trip")
        df["fit_first_day"] = "2016-04-07"
        df["fit_last_day"] = "2019-12-31"
        df.to_csv(p, index=False)
        mp = d / "manifest.json"
        m = json.loads(mp.read_text())
        m["outputs"]["spectra.csv"]["sha256"] = pdb.file_sha256(p)
        m["outputs"]["spectra.csv"]["bytes"] = p.stat().st_size
        mp.write_text(json.dumps(m, sort_keys=True, indent=2) + "\n")
        r = pdt.load_run(d)
        pdt.validate_run(r)
        assert set(r.frames["spectra"]["fit_first_day"].dropna().unique()) == {"2016-04-07"}
        assert set(r.frames["spectra"]["fit_last_day"].dropna().unique()) == {"2019-12-31"}

    def _alt_ok_ix(self, mut):
        agg = mut.frames["aggregates"]
        return agg.index[(agg["metric_kind"] == "ALT_RMST") & (agg["status"] == "OK")][0]

    def _n1(self, mut, i):
        agg, tri = mut.frames["aggregates"], mut.frames["trials"]
        mid = agg.loc[i, "metric_id"]
        agg.loc[i, "n"] = 1
        g = tri[tri["group_id"] == mid]
        mut.frames["trials"] = pd.concat([tri[tri["group_id"] != mid], g.iloc[[0]]], ignore_index=True)

    def test_alt_n1_deff_missing_refused(self, mut):
        i = self._alt_ok_ix(mut)
        self._n1(mut, i)
        mut.frames["aggregates"].loc[i, "deff"] = np.nan
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "NON_FINITE_METRIC"

    def test_alt_n1_det_bounds_missing_refused(self, mut):
        i = self._alt_ok_ix(mut)
        self._n1(mut, i)
        mut.frames["aggregates"].loc[i, "det_lo"] = np.nan
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "NON_FINITE_METRIC"

    def test_alt_n_gt1_rmst_sd_missing_refused(self, mut):
        mut.frames["aggregates"].loc[self._alt_ok_ix(mut), "rmst_sd"] = np.nan
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "NON_FINITE_METRIC"

    def test_holdout_deff_missing_refused(self, mut):
        agg = mut.frames["aggregates"]
        i = agg.index[(agg["metric_kind"] == "HOLDOUT_NULL_FPR") & (agg["status"] == "OK")][0]
        agg.loc[i, "deff"] = np.nan
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_run(mut)
        assert exc.value.code == "NON_FINITE_METRIC"

    def _assert_lineage_exact(self, run, **kw):
        t = pdt.build_tables(run, **kw)
        pdt.validate_lineage(run, t)
        lin = {(e["table"], e["row_id"], e["column"]) for e in t.lineage}
        cells = {(tb, r["row_id"], c) for tb in ("T1", "T2", "T3", "T3R")
                 for r in t.rows[tb] for c, _ in t.cols[tb]}
        assert lin == cells
        return t

    def test_family_filter_cov_lineage_exact(self, run):
        self._assert_lineage_exact(run, family=pdb.COV)

    def test_family_filter_energy_lineage_exact(self, run):
        self._assert_lineage_exact(run, family=pdb.ENERGY)

    def test_lineage_orphan_entry_refused(self, run):
        t = pdt.build_tables(run)
        t.lineage.append({"table": "T3", "row_id": "T3:" + "0" * 16 + ":0", "column": "rmst", "kind": "RULE",
                          "source_file": "", "source_key": "", "source_column": "", "formula": "injected orphan",
                          "inputs": ""})
        with pytest.raises(pdt.Refused) as exc:
            pdt.validate_lineage(run, t)
        assert exc.value.code == "LINEAGE_ORPHAN"
