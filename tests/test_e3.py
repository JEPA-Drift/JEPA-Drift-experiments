"""Tests of experiments/e3_calibration.py (stream 13, E3): strict window, E1 tickers, window resets, readings, CLI."""
import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import e3_calibration as e3
from jepadrift.monitors import lattice
from jepadrift.monitors.cusum import bilateral_delay, get_cusum_trajectory, strict_cusum
from jepadrift.monitors.gamma import gamma_spectral, required_threshold
from jepadrift.monitors.streams import energy_stream, exact_sign_stream, label_stream
from jepadrift.stats.garch import compute_gamma_exact, fit_garch_qmle
from jepadrift.stats.intervals import wilson

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "e3.yaml"
OUTPUTS = ("e3_cells.csv", "e3_arl0.csv", "e3_raw_placebo.csv", "e3_overshoot.csv", "e3_window_encoders.csv",
           "e3_j2_check.txt")
TICKERS = {"d2_us97": ([24, 71, 56, 46, 75], ["COST", "SHW", "SO", "MDLZ", "PSA"]),
           "d3_239": ([60, 177, 141, 116, 184], ["CASY", "KEY", "GPC", "ERIE", "LRCX"])}


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([13, 99, *key]))


def _days(*d):
    return np.array(d, dtype="datetime64[D]")


def _carried_offsets(x, starts, H, delta, thr):
    """Bilateral CUSUM carried from row 0 and read on [s, s + H): the missing reset the window tests must catch."""
    out = []
    for s in starts:
        sp = sn = 0.0
        hit = -1
        for t in range(s + H):
            sp, sn = max(0.0, sp + x[t] - delta), max(0.0, sn - x[t] - delta)
            if t >= s and (sp > thr or sn > thr):
                hit = t - s
                break
        out.append(hit)
    return np.array(out)


def test_check_window_refuses_rows_outside_the_strict_bounds():
    e3.check_window(_days("2005-01-04", "2019-12-31"))
    for bad in ("2005-01-03", "2020-01-02"):
        with pytest.raises(ValueError):
            e3.check_window(_days("2010-06-01", bad))
    with pytest.raises(ValueError):
        e3.check_window(_days())


@pytest.mark.parametrize("name, excluded", [("d2_us97", ()), ("d3_239", ("2005-01-03",))])
def test_rows_are_strict_and_the_exclusion_is_declared(name, excluded):
    X, days, splits, _ = e3.load_rows(name)
    assert (str(days[0]), str(days[-1]), len(days), X.shape[0]) == ("2005-01-04", "2019-12-31", 3774, 3774)
    assert e3.EXCLUDED_DAYS[name] == excluded
    assert splits["calib"][1] - splits["calib"][0] == 941


def test_an_undeclared_exclusion_raises(monkeypatch):
    monkeypatch.setitem(e3.EXCLUDED_DAYS, "d3_239", ())
    with pytest.raises(ValueError, match="declared"):
        e3.load_rows.__wrapped__("d3_239")


@pytest.mark.parametrize("name", sorted(TICKERS))
def test_p1_tickers_are_the_literal_e1_titles(name):
    cols, names = TICKERS[name]
    X, _, _, assets = e3.load_rows(name)
    assert X.shape[1] == {"d2_us97": 97, "d3_239": 239}[name]
    assert e3.tickers(name) == cols
    assert [assets[c] for c in cols] == names


def test_window_offsets_restart_at_each_window():
    x = exact_sign_stream(_rng(1).standard_normal(600), _rng(2))
    H, thr = 150, 1.9
    starts = np.r_[0, 37, 200, _rng(3).integers(0, 600 - H + 1, size=40)]
    got = e3.window_offsets(x, starts, H, 0.1, thr)
    assert got.tolist() == [bilateral_delay(x[s:s + H], 0.1, thr) for s in starts]
    assert e3.window_offsets(x, starts, H, 0.1, thr, sided=1).tolist() == [strict_cusum(x[s:s + H], 0.1, thr)
                                                                          for s in starts]
    y = x.copy()
    y[:200] = exact_sign_stream(_rng(4).standard_normal(200), _rng(5))
    assert e3.window_offsets(y, starts[2:3], H, 0.1, thr).tolist() == got[2:3].tolist()
    assert (got >= 0).any() and (_carried_offsets(x, starts, H, 0.1, thr) != got).any()


def test_window_peaks_restart_at_each_window():
    e, d = (_rng(6).standard_normal(600) ** 2 - 1.0) / np.sqrt(2.0), 0.05
    H, starts = 200, np.r_[0, 99, 300, _rng(7).integers(0, 401, size=20)]
    peaks = e3.window_peaks(e, starts, H, d)
    carried = []
    for s, p in zip(starts, peaks):
        assert p == get_cusum_trajectory(e[s:s + H], d).max()
        assert strict_cusum(e[s:s + H], d, p) == -1 and strict_cusum(e[s:s + H], d, p - 1e-9) >= 0
        carried.append(get_cusum_trajectory(e[:s + H], d)[s:].max())
    f = e.copy()
    f[:300] = (_rng(8).standard_normal(300) ** 2 - 1.0) / np.sqrt(2.0)
    assert e3.window_peaks(f, starts[2:3], H, d)[0] == peaks[2]
    assert (np.array(carried) != peaks).any()


def test_p1c_d6_replicates_monitor_their_window_only():
    X = e3.load_rows("d2_us97")[0]
    cols, q_hat, H, thr = [24, 71], np.array([0.52, 0.51]), 300, 2.3
    out = e3.p1c_d6_task({"dataset": "d2_us97", "H": H, "cols": cols, "q_hat": q_hat, "threshold": thr,
                          "label": "test|p1c"}, (0, 12))
    exact, label = np.zeros(2, dtype=int), np.zeros(2, dtype=int)
    for r in range(12):
        g = e3.rng("test|p1c", r)
        s = int(g.integers(0, len(X) - H + 1))
        Y = X[s:s + H][:, cols] * g.choice((-1.0, 1.0), size=H)[:, None]
        bits, lab = exact_sign_stream(Y, e3.rng("test|p1c", r, 7)), label_stream(Y, q_hat)
        for j in range(2):
            exact[j] += bilateral_delay(bits[:, j], 0.1, thr) >= 0
            label[j] += bilateral_delay(lab[:, j], 0.1, thr) >= 0
    assert out["exact"].tolist() == exact.tolist() and out["label"].tolist() == label.tolist()
    assert exact.sum() + label.sum() > 0


def test_d5_monitoring_restarts_after_the_clean_days():
    d5 = {"alpha": 0.08, "beta": 0.90, "burn": 100, "T_clean": 300}
    ctx = {"background": "gaussian", "label": "test|d5", "d5": d5, "H": [60, 150], "thresholds": {60: 1.9, 150: 2.3}}
    out = e3.d5_task(ctx, (0, 6))
    for r in range(6):
        y = e3.d5_path("gaussian", d5, 450, e3.rng("test|d5", r))
        clean, mon = y[:300], y[300:]
        bits, lab = exact_sign_stream(mon, e3.rng("test|d5", r, 7)), label_stream(mon, float(np.mean(clean > 0)))
        for H in (60, 150):
            assert out["det"]["exact", H][r] == (bilateral_delay(bits[:H], 0.1, ctx["thresholds"][H]) >= 0)
            assert out["det"]["label", H][r] == (bilateral_delay(lab[:H], 0.1, ctx["thresholds"][H]) >= 0)
        mu, sigma, _, _ = e3.p1d_fit(clean)
        assert out["energy"][r].tobytes() == energy_stream(mon, mu, sigma).tobytes()


def test_overshoot_paths_restart_from_zero():
    rows = [{"name": "fo", "kind": "first_order", "delta": 0.5, "threshold": 4.0},
            {"name": "sg", "kind": "sign", "delta": 0.1, "threshold": 3.3}]
    ctx = {"background": "iid", "label": "test|over", "T_max": 3000, "spec_days": 500, "d5": {}, "rows": rows}
    out = e3.overshoot_task(ctx, (0, 4))
    for r in range(4):
        x = e3.overshoot_path(ctx, r)
        for row, s in ((rows[0], x), (rows[1], exact_sign_stream(x, e3.rng("test|over", r, 7)))):
            t = strict_cusum(s, row["delta"], row["threshold"])
            assert out[row["name"]][0][r] == (t + 1 if t >= 0 else 3000) and out[row["name"]][1][r] == (t < 0)


def test_encoder_monitoring_starts_at_the_window_after_an_input_delay():
    sd = {1: 1.0, 5: 5 ** -0.5}
    ctx = {"background": "d5", "label": "test|enc", "L": [1, 5], "H": [100], "sd": sd, "delta": 0.5,
           "thresholds": {100: 1.9}, "lb_lags": 5, "wide_factor": 10, "alpha": 0.05}
    out = e3.encoder_task(ctx, (0, 3))
    for r in range(3):
        y = e3.rng("test|enc", r).standard_normal(4 + 100)
        for L in (1, 5):
            z = np.array([y[t - L + 1:t + 1].mean() for t in range(4, 104)])
            np.testing.assert_allclose(out[L, 100]["peak"][r], get_cusum_trajectory(z / sd[L], 0.5).max(), rtol=1e-12)
            bits = exact_sign_stream(z, e3.rng("test|enc", r, L, 7))
            assert out[L, 100]["sign"][r] == (bilateral_delay(bits, 0.1, 1.9) >= 0)


def test_wide_bandwidth_spectral_gamma_of_a_moving_average_is_near_L():
    z = e3.encoder(_rng(9).standard_normal(200_019), 20)
    assert gamma_spectral(z, L=200) == pytest.approx(20.0, rel=0.1)
    assert np.median(gamma_spectral(z[:199_500].reshape(266, 750))) < 10.0


def test_brook_evans_matches_the_tables_and_the_sign_row_is_exact():
    assert e3.brook_evans_arl0(0.5, 4.0, 2000) == pytest.approx(336.0, rel=0.01)
    assert e3.brook_evans_arl0(0.5, 5.0, 2000) == pytest.approx(931.0, rel=0.01)
    a, b, _ = lattice.lattice_steps(0.1)
    assert lattice.arl0(16, a, b, sided=1) == pytest.approx(213.09, abs=0.01)


def test_fpr_threshold_is_the_required_threshold():
    p = _rng(10).standard_normal((400, 150)) ** 2 - 1.0
    peaks = e3.cusum_trajectory_vec(p, 0.5).max(axis=-1)
    lam = e3.fpr_threshold(peaks, 0.05)
    assert abs(lam - required_threshold(p, 0.5, 0.05, "fpr", H=150)) < 1e-6
    assert (peaks > lam).mean() <= 0.05 < (peaks >= lam).mean()


def test_p1d_constants_follow_r01():
    r = _rng(11).standard_normal(941) * 0.01
    (_, a, b), conv = fit_garch_qmle(r - np.mean(r))
    assert e3.p1d_fit(r) == (float(np.mean(r ** 2)), float(np.std(r ** 2)), float(compute_gamma_exact(a, b)),
                             bool(conv))


def test_p1d_d5_thresholds_come_from_independent_calibration_paths():
    d5 = {"alpha": 0.08, "beta": 0.90, "burn": 100, "T_clean": 300}
    sels = {150: lattice.select_threshold(0.05, H=150)}

    def run(role, span):
        return [e3.d5_task({"background": "gaussian", "label": e3.d5_label("gaussian", role), "d5": d5, "H": [150],
                            "thresholds": {150: sels[150]["threshold"]}}, span)]

    cal, ev, ev2 = run("cal", (0, 30)), run("eval", (0, 20)), run("eval", (20, 40))
    assert e3.seed_key(e3.d5_label("gaussian", "cal"), 0) != e3.seed_key(e3.d5_label("gaussian", "eval"), 0)
    assert not np.array_equal(cal[0]["energy"][:20], ev[0]["energy"])
    cfg, label = {"alpha": 0.05, "d5": d5}, e3.d5_label("gaussian", "cal")
    p1d = pd.DataFrame(e3.d5_cells("gaussian", cal, ev, cfg, sels, label)).query("pipeline == 'P1-D'")
    lam_req = e3.fpr_threshold(e3.cusum_trajectory_vec(cal[0]["energy"][:, :150], 0.5).max(axis=-1), 0.05)
    peaks = e3.cusum_trajectory_vec(ev[0]["energy"][:, :150], 0.5).max(axis=-1)
    assert np.allclose(p1d["lam_req"], lam_req)
    assert p1d.set_index("reading").loc["lam_req", "alarms"] == int((peaks > lam_req).sum())
    assert set(p1d["reading"]) == {"lam_req", "rule_iid_x_gamma_hat", "iid", "r01_65_x_gamma_hat"}
    assert (p1d["n_cal"] == 30).all() and (p1d["n_eval"] == 20).all() and (p1d["n"] == 20).all()
    assert (p1d["validity"] == "out_of_sample").all() and (p1d["ci_kind"] == "wilson").all()
    p1d2 = pd.DataFrame(e3.d5_cells("gaussian", cal, ev2, cfg, sels, label)).query("pipeline == 'P1-D'")
    assert np.allclose(p1d2["lam_iid"], p1d["lam_iid"]) and np.allclose(p1d2["lam_req"], p1d["lam_req"])


def test_wilson_contains_the_estimate_at_the_bounds():
    for k, n in ((0, 50), (50, 50), (3, 1000)):
        lo, hi = wilson(k, n)
        assert 0.0 <= lo <= k / n <= hi <= 1.0


def test_arl_classification_is_pass_or_indeterminate_never_fail():
    s = np.full(1000, 30.0)
    s[:10] = 1200.0
    row = e3.classify_arl(s, s >= 1200.0, 20.0)
    assert row["classification"] == "PASS" and row["censored"] == 10 and row["deff"] == 1.0
    low = 5.0 + _rng(12).random(200)
    row = e3.classify_arl(low, np.zeros(200, dtype=bool), 20.0)
    assert row["classification"] == "INDETERMINATE"
    assert row["deficit"] == pytest.approx(20.0 - low.mean()) and row["deficit_lo"] < row["deficit"] < row["deficit_hi"]


def test_arl_standard_error_goes_through_the_effective_size():
    s = 20.0 + 10.0 * _rng(18).random(400)
    one, two = e3.classify_arl(s, np.zeros(400, dtype=bool), 20.0), e3.classify_arl(s, np.zeros(400, dtype=bool), 20.0,
                                                                                     deff=2.0)
    assert (one["deff"], one["n_eff"], two["n_eff"]) == (1.0, 400.0, 200.0)
    assert one["se"] == pytest.approx(s.std(ddof=1) / 20.0) and two["se"] == pytest.approx(one["se"] * np.sqrt(2.0))


def test_quick_overshoot_rows_are_diagnostic_without_gate():
    rows = [{"name": "fo", "kind": "first_order", "delta": 0.5, "threshold": 4.0, "ref": {"iid": 300.0}}]
    ctx = {"background": "iid", "label": "test|over", "T_max": 3000, "spec_days": 500, "d5": {}, "rows": rows,
           "n_primary": 6}
    parts = [e3.overshoot_task(ctx, (0, 8))]
    for quick, first in ((True, "quick_diagnostic"), (False, "primary")):
        out = pd.DataFrame(e3.overshoot_rows("iid", parts, ctx, {"overshoot": {"tolerance": 0.05}}, {}, {}, quick))
        assert out["role"].tolist() == [first, "diagnostic"] and out["gate"].tolist()[1] == "na"
        assert (out["gate"].iloc[0] == "na") == quick and out["gate"].iloc[0] in {"na", "PASS", "FAIL", "INDETERMINATE"}
        x = parts[0]["fo"][0][:6].astype(float)
        assert (out["deff"] == 1.0).all() and out["n_eff"].tolist() == [6.0, 8.0]
        assert out["se"].iloc[0] == pytest.approx(x.std(ddof=1) / np.sqrt(6.0))


def test_bounded_stopping_time_check_on_fair_coins():
    x = _rng(13).choice((-1.0, 1.0), size=(4000, 300))
    for kind in e3.TYPES:
        sigma, cz, m = e3.arl_lengths(e3.edetector_log(x, "P2-C", kind), 20.0, 1200)
        row = e3.classify_arl(sigma, cz, 20.0, m)
        assert row["ineq_lb99"] < 0.0 or kind == "sr"
        if kind == "sr":
            assert abs(row["ineq_mean"]) <= 4.0 * row["ineq_se"]


def test_familywise_violation_needs_the_bonferroni_bound():
    arl = pd.DataFrame({"classification": ["PASS"] * 66 + ["descriptive"], "ineq_mean": [3.0, 10.0] + [0.0] * 65,
                        "ineq_se": [1.0] * 67})
    out, z = e3.familywise_violations(arl)
    assert z == pytest.approx(3.6128, abs=1e-3)
    assert out["ineq_violated"].tolist()[:3] == [False, True, False] and np.isnan(out["ineq_lb_fw"].iloc[-1])


def test_circular_d6_path_continues_at_the_seam():
    base = {"z_odd": _rng(14).standard_normal((50, 3)), "z_even": _rng(15).standard_normal((50, 2))}
    eps = _rng(16).choice((-1.0, 1.0), size=120)
    d = e3.circular_data(base, 30, eps)
    idx = (30 + np.arange(120)) % 50
    assert np.array_equal(np.abs(d["z_odd"]), np.abs(base["z_odd"][idx]))
    assert np.array_equal(d["z_even"], base["z_even"][idx])
    assert np.array_equal(d["z_odd"], base["z_odd"][idx] * eps[:, None])
    assert not np.array_equal(np.sign(d["z_odd"][20:70]), np.sign(d["z_odd"][70:120]))
    x = _rng(17).choice((-1.0, 1.0), size=200)
    whole = e3.edetector_log(x, "P2-C", "sr")
    assert not np.allclose(whole[100:], e3.edetector_log(x[100:], "P2-C", "sr"))


def test_raw_window_counts():
    calib = e3.load_rows("d2_us97")[2]["calib"]
    assert e3.window_counts(3774, 750, calib)[:2] == (3025, 5)
    assert e3.window_counts(3774, 2000, calib)[:2] == (1775, 1)


def test_e3_injects_nothing():
    tree = ast.parse(Path(e3.__file__).read_text())
    imported = {(n.module, a.name) for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    assert {name for mod, name in imported if mod == "jepadrift.injection"} == {"symmetrize"}
    assert ("jepadrift", "injection") not in imported
    families = [v.value for d in ast.walk(tree) if isinstance(d, ast.Dict)
                for k, v in zip(d.keys, d.values) if isinstance(k, ast.Constant) and k.value == "family"]
    assert families and set(families) == {"H0"}


def test_config_pins_the_full_sizes():
    cfg = yaml.safe_load(CONFIG.read_text())
    reps = cfg["reps"]
    assert (reps["sign"], reps["iid"], reps["arl0"], reps["overshoot"], reps["overshoot_primary"]) == (
        20000, 20000, 20000, 20000, 2000)
    assert cfg["H"] == [750, 2000] and cfg["alpha"] == 0.05 and cfg["raw_stride"] == 1
    assert cfg["arl0"]["gammas"] == [20, 100, 252] and cfg["arl0"]["horizon_factor"] == 60
    assert cfg["overshoot"]["tolerance"] == 0.05 and cfg["K"] == {"d2_us97": 5, "d3_239": 10}


def _smoke_cfg():
    cfg = yaml.safe_load(CONFIG.read_text())
    cfg.update(datasets=["d2_us97"], H=[750], raw_stride=400, n_cal=200, b_flips=50, p3d_settings=[[750, "calib"]],
               packets={"d5": 10, "overshoot": 6, "p1c": 20, "encoders": 20})
    cfg["reps"].update(sign=40, iid=60, arl0=16, overshoot=12, overshoot_primary=8)
    cfg["arl0"].update(gammas=[20], raw_packet=4)
    cfg["overshoot"]["T_max"] = {"iid": 3000, "garch": 3000}
    cfg["d5"]["T_clean"] = 300
    cfg["encoders"]["L"] = [1, 5]
    return cfg


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    root = tmp_path_factory.mktemp("e3_smoke")
    path = root / "smoke.yaml"
    path.write_text(yaml.safe_dump(_smoke_cfg()))
    runs = []
    for jobs in (1, 2):
        d = root / f"jobs{jobs}"
        assert e3.main(["--config", str(path), "--out", str(d / "out"), "--fig-dir", str(d / "fig"), "--log-dir",
                        str(d / "log"), "--jobs", str(jobs)]) == 0
        runs.append(d)
    return runs


def _read(run, name):
    return pd.read_csv(run / "out" / name, float_precision="round_trip")


def test_cli_outputs_do_not_depend_on_jobs(smoke):
    for name in OUTPUTS:
        assert (smoke[0] / "out" / name).read_bytes() == (smoke[1] / "out" / name).read_bytes(), name
    figs = sorted(p.name for p in (smoke[0] / "fig").iterdir())
    assert figs == sorted(f"{s}.{x}" for s in ("arl0", "fpr_cells", "gamma", "raw_placebo") for x in ("pdf", "png"))


def test_cli_separates_fpr_arl0_and_gamma(smoke):
    cells, arl = _read(smoke[0], "e3_cells.csv"), _read(smoke[0], "e3_arl0.csv")
    assert set(cells["H"]) == {750} and not {"restricted_mean", "classification", "cap"} & set(cells.columns)
    bound = cells[cells["target_kind"] == "<="]
    ville = (bound["pipeline"] == "P3-CS") & (bound["reading"] == "anytime-valid_a")
    assert ville.any() and (bound.loc[ville, "gamma"] == 20.0).all()
    assert np.allclose(bound.loc[ville, "target"], 1.0 / bound.loc[ville, "gamma"])
    assert np.allclose(bound.loc[~ville, "gamma"], bound.loc[~ville, "H"] / 0.05)
    assert set(arl["gamma"]) == {20.0} and set(arl["cap"]) == {1200}
    assert set(arl["classification"]) <= {"PASS", "INDETERMINATE", "descriptive"}
    sign = cells[(cells["pipeline"] == "P1-C") | (cells["validity"] == "exact")]
    assert len(sign) and sign[["gamma_op", "gamma_spec"]].isna().all().all()
    amplitude = cells[cells["pipeline"].isin(["P1-D", "P3-D"])]
    assert len(amplitude) and np.isfinite(amplitude["gamma_op"]).all()


def test_cli_reports_design_effects_and_keeps_raw_rows_descriptive(smoke):
    cells, raw = _read(smoke[0], "e3_cells.csv"), _read(smoke[0], "e3_raw_placebo.csv")
    for name in ("e3_overshoot.csv", "e3_window_encoders.csv", "e3_arl0.csv"):
        df = _read(smoke[0], name)
        inferential = df[df["classification"] != "descriptive"] if "classification" in df else df
        assert (inferential["deff"] == 1.0).all() and (inferential["n_eff"] == inferential["n"]).all(), name
    assert (_read(smoke[0], "e3_window_encoders.csv")["n_cal"] == 60).all()
    d5 = cells[(cells["block"] == "d5") & (cells["pipeline"] == "P1-D")]
    assert len(d5) == 8 and (d5["validity"] == "out_of_sample").all() and d5["fpr_lo"].notna().all()
    assert (d5["n_cal"] == 60).all() and (d5["n_eval"] == 40).all()
    desc = cells[cells["validity"] == "descriptive"]
    assert len(desc) and (desc["ci_kind"] == "na").all() and desc[["fpr_lo", "fpr_hi"]].isna().all().all()
    assert not [c for c in raw.columns if c.endswith(("_lo", "_hi"))]
    assert (raw["design"] == "retrospective_descriptive").all()
    assert set(cells.loc[cells["pipeline"] == "P2-C", "validity"]) == {"calibrated_conditional", "bound"}


def test_cli_j2_file_is_a_secondary_check_without_verdict(smoke):
    lines = (smoke[0] / "out" / "e3_j2_check.txt").read_text().splitlines()
    text = "\n".join(lines)
    assert "not a J2 verdict" in text and "primary J2 (i) verdict is E1 (stream 12) at 2,000 replicates" in text
    assert not [line for line in lines if line.lower().startswith("verdict")]
    assert "valid under any dependence" in text and "descriptive" in text


def test_cli_logs_the_exclusion_and_the_block_costs(smoke):
    log = (smoke[0] / "log" / "run.log").read_text()
    assert "rows d2_us97: excluded before 2005-01-04: 0 []" in log
    assert "cpu seconds by block" in log and "d5|gaussian|cal" in log and "d5|gaussian|eval" in log
