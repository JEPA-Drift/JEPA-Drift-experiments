"""Tests of experiments/e10_robustness.py (stream 27, E10 linear stage): generators, bits, references, CIs, gains."""
import math

import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import e10_robustness as e10
from jepadrift import pipelines as pl
from jepadrift import sim
from jepadrift.injection import inject, symmetrize

H = 750


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([27, 99, *key]))


def _region(p, n):
    half = pl.Z99 * math.sqrt(p * (1.0 - p) / n)
    return p - half, p + half


def test_local_generator_reproduces_garch_panel():
    for nu, rho in ((7, 0.4), (None, None), (3, 0.4)):
        a = e10.d5_panel(300, 6, 0.08, 0.90, nu, _rng(1), factor_rho=rho, burn=50)
        b = sim.garch_panel(300, 6, 0.08, 0.90, nu, _rng(1), factor_rho=rho, burn=50)
        assert a.tobytes() == b.tobytes()


def test_shock_day_signs_in_loop_equal_post_hoc_symmetrization():
    X = e10.d5_panel(400, 5, 0.08, 0.90, 7, _rng(2), factor_rho=0.4, burn=50, shock=(0.5, 0.05))
    Xs, eps = symmetrize(X, _rng(3))
    Y = e10.d5_panel(400, 5, 0.08, 0.90, 7, _rng(2), factor_rho=0.4, burn=50, shock=(0.5, 0.05), day_signs=eps)
    assert Y.tobytes() == Xs.tobytes()
    with pytest.raises(ValueError):
        e10.d5_panel(10, 3, 0.08, 0.90, 7, _rng(4), shock=(0.5, 0.05))


def test_gjr_unit_variance_and_shock_moments():
    X = e10.d5_panel(50_000, 4, 0.03, 0.90, None, _rng(5), factor_rho=0.4, burn=500, gjr=0.10)
    assert abs((X ** 2).mean() - 1.0) < 0.15
    S = e10.d5_panel(20_000, 50, 0.08, 0.90, None, _rng(6), factor_rho=0.4, burn=200, shock=(0.25, 0.05))
    assert abs(S.mean()) < 0.02
    lo, hi = _region(0.5245, 20_000)
    assert lo - 0.003 <= (S.mean(axis=1) > 0).mean() <= hi + 0.003


def _d5_case(T_cal=300, H_=200, sr=16.0):
    X = sim.garch_panel(T_cal + H_, 12, 0.08, 0.90, 7, _rng(7), factor_rho=0.4, burn=100)
    X, _, _ = inject(X, "F1", T_cal, sr ** 2 / 504, {"calib": (0, T_cal), "K": 3}, _rng(8))
    splits = {"calib": (0, T_cal), "dates": np.arange(T_cal + H_).astype("datetime64[D]")}
    return X, splits, T_cal, H_


def test_p3c_bits_reproduce_run_pipeline_and_exact_state():
    X, splits, T_cal, H_ = _d5_case()
    gamma = pl.horizon_gamma(H_)
    spec = pl.make_spec("P3-C", K=2, gamma=gamma, H=H_, dataset="d5")
    state = pl.fit_pipeline(spec, X, splits)
    z = state["rep"].transform_panel(np.ascontiguousarray(X[T_cal:]))["z_odd"]
    seed = [27, 1, 0]
    B = e10.p3c_bits(z, seed)
    rec = [{"seed": seed, "tau_star": 0, "family": "F1"}]
    off = e10.run_p3c(spec, state, z, rec)
    assert off[0] >= 0
    assert off[0] == e10.dictionary_alarm(B, 0.5, gamma)
    sel = e10.lattice_selection(0.05, H_)
    ex_spec = pl.make_spec("P3-C", reading="exact", channels=[0], alpha=0.05, K=2, H=H_, dataset="d5")
    ex_state = e10.exact_state(state, sel)
    fitted = pl.fit_pipeline(ex_spec, X, splits)
    keys = ("threshold", "level", "lattice_units")
    assert {k: fitted[k] for k in keys} == {k: ex_state[k] for k in keys}
    assert fitted["rep"].state_hash() == ex_state["rep"].state_hash()
    off_ex = e10.run_p3c(ex_spec, ex_state, z, rec)
    assert off_ex[0] == e10.alarms(B[:, 0], 0.5, "exact", sel["threshold"], gamma)


def test_arms_share_bits_and_inputs_stay_bounded():
    y = np.array([[0.0, 1.0, -1.0, 0.0, 2.0] * 40] * 3)
    B = e10.coin_bits(y, _rng(9))
    assert set(np.unique(B)) <= {0.0, 1.0}
    assert (B[y > 0] == 1.0).all() and (B[y < 0] == 0.0).all()
    gamma = pl.horizon_gamma(200)
    half = e10.alarms(B, 0.5, "anytime-valid", 9.1, gamma)
    assert (half == e10.alarms(B, np.full((3, 1), 0.5), "anytime-valid", 9.1, gamma)).all()
    for c in (0.0, 0.3, 0.7, 1.0):
        e10.alarms(B, c, "anytime-valid", 9.1, gamma)
        e10.dictionary_alarm(B.T, np.full(3, c), gamma)


def test_half_exact_level_on_valid_gjr_t3_background():
    sel = e10.lattice_selection(0.05, H)
    det = []
    for r in range(50):
        X = e10.d5_panel(H, 40, 0.03, 0.90, 3, _rng(10, r), burn=200, gjr=0.10)
        B = e10.coin_bits(X, _rng(11, r))
        det.append(e10.alarms(B.T, 0.5, "exact", sel["threshold"], None) >= 0)
    lo, hi = _region(sel["level"], 2000)
    assert lo <= np.mean(det) <= hi


def test_iid_references_formula_and_monte_carlo_tolerance():
    sel = e10.lattice_selection(0.05, H)
    B = (_rng(12).random((4000, H)) < 0.53).astype(float)
    fpr = (e10.alarms(B, 0.5, "exact", sel["threshold"], None) >= 0).mean()
    pred = e10.fpr_pred_iid(0.53, sel, H)
    lo, hi = _region(pred, 4000)
    assert lo <= fpr <= hi
    ref = e10.coin_reference(range(4), 1000, H, 941, (3,), sel, pl.horizon_gamma(H), 5)
    k, n = ref[("single", "half", "exact")]
    lo, hi = _region(sel["level"], n)
    assert n == 4000 and lo <= k / n <= hi
    assert e10.iid_tolerance(k, n, sel["level"])["within"]


def test_wilson_interval_contains_the_rate():
    assert e10.wilson(0, 2000) == (0.0, e10.wilson(0, 2000)[1])
    assert e10.wilson(2000, 2000)[1] == 1.0
    for k in (0, 1, 37, 1999, 2000):
        lo, hi = e10.wilson(k, 2000)
        assert 0.0 <= lo <= k / 2000 <= hi <= 1.0


def test_deff_ci_rules():
    assert e10.deff_rate_ci(np.zeros(100), 10)[-1] == "na"
    e = _rng(13).standard_normal(2020)
    ind = (np.convolve(e, np.ones(20), "valid") > 4.0).astype(float)
    deff, n_eff, lo, hi, kind = e10.deff_rate_ci(ind, 40)
    assert kind == "hac_bartlett" and deff > 1.0 and 1.0 <= n_eff <= ind.size and lo < ind.mean() < hi
    assert e10.deff_rate_ci(ind[:5], 10)[-1] == "na"
    alternating = np.tile([0.0, 1.0], 100)
    deff, n_eff, *_, kind = e10.deff_rate_ci(alternating, 5)
    assert deff < 1.0 and n_eff > alternating.size and kind == "na"
    mean, lo, hi, kind = e10.hac_mean_ci(np.zeros(50), 5)
    assert kind == "na" and math.isnan(lo)


def test_gain_rows_censoring_and_same_asset_fpr():
    n, m, H_ = 40, 5, 100
    rng = _rng(14)
    p3 = rng.integers(5, 30, n)
    p1 = rng.integers(20, H_, (n, m))
    p1[: n // 2, 3] = -1
    h0_p1 = rng.random((60, m)) < 0.1
    h0_p3 = rng.random(60) < 0.05
    rows = e10.gain_rows({"p3": p3, "p1": p1}, {"p1": h0_p1, "p3": h0_p3}, H_, _rng(15), 200)
    assert [r["asset_selection"] for r in rows] == ["median", "oracle"]
    assert rows[1]["oracle"] and not rows[0]["oracle"]
    t1 = np.where(p1 >= 0, p1 + 1.0, H_).mean(axis=0)
    assert rows[1]["asset_index"] == int(np.argmin(t1))
    for r in rows:
        assert r["bounds_add_ratio"]
        assert r["fpr_p1"] == h0_p1[:, r["asset_index"]].mean()
        assert r["fpr_p3"] == h0_p3.mean()
        assert r["rmst_ratio_lo"] <= r["rmst_ratio"] <= r["rmst_ratio_hi"]
    p3c = p3.copy()
    p3c[0] = -1
    assert not any(r["bounds_add_ratio"] for r in e10.gain_rows({"p3": p3c, "p1": p1},
                                                                 {"p1": h0_p1, "p3": h0_p3}, H_, _rng(15), 50))


def test_gates_and_window_guard():
    with pytest.raises(SystemExit):
        e10.main(["--stage", "jepa", "--families", "F1"])
    with pytest.raises(SystemExit):
        e10.main(["--stage", "linear", "--families", "F2"])
    with pytest.raises(ValueError):
        e10.check_window(np.array(["2019-12-31", "2020-01-02"], dtype="datetime64[D]"))


def _mini_config(tmp_path):
    cfg = yaml.safe_load(e10.CONFIG.read_text())
    cfg["H"] = 300
    cfg["n_p1"] = 5
    cfg["sr"] = [16]
    cfg["reps"] = {"h0": 6, "f1": 4, "coins": 300, "boot": 50}
    cfg["d5"].update({"N": 30, "T_calib": 400, "K": 3, "burn": 200, "pilot_days": 2000})
    cfg["d5"]["backgrounds"] = {k: cfg["d5"]["backgrounds"][k] for k in ("base", "shock25", "zero05")}
    cfg["d6"], cfg["raw"] = ["d2_us97"], []
    path = tmp_path / "e10_mini.yaml"
    path.write_text(yaml.safe_dump(cfg))
    return path


def test_cli_labels_determinism_and_jobs(tmp_path):
    cfg = _mini_config(tmp_path)
    outs = []
    for jobs in (1, 2):
        out = tmp_path / f"out{jobs}"
        args = ["--stage", "linear", "--families", "F1", "--config", str(cfg), "--out", str(out),
                "--fig-dir", str(tmp_path / f"fig{jobs}"), "--log-dir", str(tmp_path / f"log{jobs}"),
                "--jobs", str(jobs)]
        assert e10.main(args) == 0
        outs.append(out)
    for name in ("e10_cells.csv", "e10_gains.csv"):
        assert (outs[0] / name).read_bytes() == (outs[1] / name).read_bytes()
    cells = pd.read_csv(outs[0] / "e10_cells.csv", float_precision="round_trip")
    assert set(cells["reference_kind"]) <= set(e10.REFERENCE_KINDS)
    assert set(cells["design"]) <= set(e10.DESIGNS)
    assert set(cells["null_valid"]) <= set(e10.NULL_VALID)
    for col in ("ci_kind", "ref_ci_kind", "inflation_ci_kind"):
        assert set(cells[col]) <= set(e10.CI_KINDS)
    h0 = cells[cells["family"] == "H0"]
    base = h0[h0["background"] == "base"]
    half_exact = base[(base["arm"] == "half") & (base["reading"] == "exact")]
    assert (half_exact["reference_kind"] == "level_exact").all() and half_exact["fpr_ref"].isna().all()
    assert (base[base["reading"] == "anytime-valid"]["reference_kind"] == "self_valid").all()
    shock = h0[h0["background"] == "shock25"]
    assert (shock["reference_kind"] == "matched_valid_generator").all()
    assert shock["fpr_ref"].notna().all() and (shock["null_valid"] == "invalid").all()
    assert (h0[h0["background"] == "shock25:sym"]["null_valid"] == "valid").all()
    zero_neg = h0[h0["arm"].str.startswith("zero_neg")]
    assert set(zero_neg["background"]) == {"zero05", "d6"}
    assert (zero_neg["null_valid"] == "invalid").all() and (zero_neg["reference_kind"] == "none").all()
    coins = cells[cells["background"] == "ref_coins"]
    assert (coins["design"] == "iid_scenario").all() and len(coins)
    assert cells.loc[cells["arm"].str.startswith("zero_neg"), "fpr_iid_mc"].isna().all()
    gains = pd.read_csv(outs[0] / "e10_gains.csv", float_precision="round_trip")
    assert set(gains["asset_selection"]) == {"median", "oracle"}
    assert (gains.loc[gains["asset_selection"] == "oracle", "exploratory"]).all()


def test_raw_windows_references_and_na_rule():
    cfg = yaml.safe_load(e10.CONFIG.read_text())
    sel = e10.lattice_selection(cfg["alpha"], cfg["H"])
    rows, ctx = e10.raw_rows("d2_us97", cfg, sel, starts=np.arange(0, 2000, 400))
    df = pd.DataFrame(rows)
    assert ctx["state_hash"].startswith("85147fd9")
    half = df[df["arm"] == "half"]
    assert (half["reference_kind"] == "symmetrized_window").all() and half["fpr_ref"].notna().all()
    assert (half["ref_ci_kind"] == "wilson_conditional_approx").all()
    other = df[df["arm"] != "half"]
    assert (other["reference_kind"] == "descriptive_contrast").all()
    assert other["fpr_ref"].isna().all() and other["inflation"].isna().all() and other["contrast_fpr"].notna().all()
    assert (df["design"] == "retrospective").all()
    assert (df["ci_kind"] == "na").all()
    assert (half["inflation_ci_kind"] == "na").all() and half["inflation_lo"].isna().all()
    assert (df.loc[df["arm"].str.startswith("zero_neg"), "null_valid"] == "invalid").all()
