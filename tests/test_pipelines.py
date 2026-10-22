"""Tests for jepadrift.pipelines and jepadrift.monitors.calibration (pytest)."""
import json
import math

import numpy as np
import pandas as pd
import pytest

from jepadrift import floors, injection, sim
from jepadrift import pipelines as pl
from jepadrift.data_loader import articleB
from jepadrift.monitors import calibration, cusum, eprocess, lattice, streams

BETS = np.array([0.1, -0.1, 0.25, -0.25, 0.5, -0.5, 0.9, -0.9])


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([7, *key]))


@pytest.fixture(scope="module")
def d2():
    ret, dates, _ = articleB.load_d2()
    start, stop = pl.split_rows(dates, articleB.load_splits("d2_us97"))["pre_monitor"]
    X, d = np.ascontiguousarray(ret[start:stop]), dates[start:stop]
    return X, d, pl.split_rows(d, articleB.load_splits("d2_us97"))


def _h0_records(n, T, H, key, pre=0):
    g = _rng(*key)
    return [{"seed": [7, *key, i], "tau_star": int(g.integers(pre, T - H + 1)), "family": "H0"} for i in range(n)]


def _match_window(w, x):
    for s in range(len(x) - len(w) + 1):
        if np.array_equal(np.abs(w), np.abs(x[s:s + len(w)])):
            return s
    return -1


def test_null_windows_draw_order_and_flip():
    x = _rng(1).standard_normal((50, 3))
    one = calibration.null_windows(x, 7, 10, _rng(2))
    g = _rng(2)
    two = np.concatenate([calibration.null_windows(x, 7, 4, g), calibration.null_windows(x, 7, 6, g)])
    assert one.shape == (10, 7, 3) and np.array_equal(one, two)
    for w in one:
        s = _match_window(w, x)
        assert s >= 0 and np.array_equal(w, x[s:s + 7])
    flipped = calibration.null_windows(x, 7, 10, _rng(3), flip=True)
    assert not np.array_equal(np.sign(flipped), np.sign(calibration.null_windows(x, 7, 10, _rng(3))))
    for w in flipped:
        s = _match_window(w, x)
        assert s >= 0
        ratio = w / x[s:s + 7]
        assert set(np.unique(ratio)) <= {-1.0, 1.0} and (ratio == ratio[:, :1]).all()
    assert calibration.null_windows(x[:, 0], 50, 2, _rng(4), flip=True).shape == (2, 50)
    for length, n in ((51, 1), (0, 1), (7, 0)):
        with pytest.raises(ValueError):
            calibration.null_windows(x, length, n, _rng(5))


def test_bootstrap_threshold_rule():
    m = _rng(6).standard_normal(1000)
    assert calibration.bootstrap_threshold(m, 0.05) == float(np.quantile(m, 0.95))
    for alpha in (0.0, 1.0, -0.1):
        with pytest.raises(ValueError):
            calibration.bootstrap_threshold(m, alpha)
    with pytest.raises(ValueError):
        calibration.bootstrap_threshold([], 0.05)


def test_average_betting_eprocess():
    x = _rng(7).uniform(-1.0, 1.0, size=(3, 40, 4))
    got = eprocess.log_average_betting_eprocess(x, BETS)
    ref = np.log(np.mean([np.exp(eprocess.log_betting_eprocess(x[..., k], lam)) for lam in BETS for k in range(4)],
                         axis=0))
    assert got.shape == (3, 40) and np.allclose(got, ref, rtol=1e-12, atol=1e-12)
    assert eprocess.log_average_betting_eprocess(x[0], BETS).shape == (40,)
    coins = _rng(8).choice((-1.0, 1.0), size=(2000, 500, 1))
    share = (eprocess.log_average_betting_eprocess(coins, BETS).max(axis=-1) >= np.log(20.0)).mean()
    assert share <= 0.05 + 3.0 * np.sqrt(0.05 * 0.95 / 2000)
    for bad in ([1.0], [], [[0.1]]):
        with pytest.raises(ValueError):
            eprocess.log_average_betting_eprocess(x, bad)
    with pytest.raises(ValueError):
        eprocess.log_average_betting_eprocess(2.0 * x, BETS)


def test_alarms_schema_one_row_per_record(d2, tmp_path):
    X, _, splits = d2
    spec = pl.make_spec("P3-C", dataset="d2_us97")
    state = pl.fit_pipeline(spec, X, splits)
    recs = _h0_records(5, len(X), spec["H"], (10,))
    df = pl.run_pipeline(spec, X, splits, recs, state)
    assert list(df.columns) == pl.COLUMNS and len(df) == 5
    assert (df["run_id"] == pl.run_id(spec)).all() and len(pl.run_id(spec)) == 16
    assert df["seed"].tolist() == ["-".join(map(str, r["seed"])) for r in recs]
    assert df["tau_star"].tolist() == [r["tau_star"] for r in recs]
    for row in df.itertuples():
        if row.detected:
            assert row.tau_star <= row.alarm_index < row.tau_star + spec["H"]
            assert row.delay == row.alarm_index - row.tau_star + 1
        else:
            assert row.alarm_index == -1 and math.isnan(row.delay)
    assert (df["threshold"] == spec["gamma"]).all() and (df["reading"] == "anytime-valid").all()
    assert (df["family"] == "H0").all() and (df["dataset"] == "d2_us97").all()
    assert pl.run_pipeline(spec, X, splits, recs).equals(df)
    exact = pl.make_spec("P3-C", reading="exact", channels=[1], alpha=0.05)
    dfe = pl.run_pipeline(exact, X, splits, recs, pl.fit_pipeline(exact, X, splits))
    assert (dfe["threshold"] == lattice.select_threshold(0.05, H=750, delta=0.1, sided=2)["threshold"]).all()
    empty = pl.run_pipeline(spec, X, splits, [], state)
    assert list(empty.columns) == pl.COLUMNS and len(empty) == 0
    path = tmp_path / "alarms.csv"
    pl.run_pipeline(spec, X, splits, recs, state, out=path)
    back = pd.read_csv(path, float_precision="round_trip", dtype={"run_id": str, "seed": str})
    pd.testing.assert_frame_equal(back, df, check_dtype=False)


def test_parallel_and_partition_invariance(d2):
    X, _, splits = d2
    spec = pl.make_spec("P3-C")
    state = pl.fit_pipeline(spec, X, splits)
    recs = _h0_records(8, len(X), spec["H"], (11,))
    seq = pl.run_pipeline(spec, X, splits, recs, state)
    assert seq.equals(pl.run_pipeline(spec, X, splits, recs, state, n_jobs=2))
    parts = pd.concat([pl.run_pipeline(spec, X, splits, recs[:3], state),
                       pl.run_pipeline(spec, X, splits, recs[3:], state)], ignore_index=True)
    assert seq.equals(parts)


def test_x_and_z_inputs_agree(d2):
    X, _, splits = d2
    for spec in (pl.make_spec("P3-C"), pl.make_spec("P3-C", reading="exact", channels=[0], alpha=0.05),
                 pl.make_spec("P3-D", H=500, N_cal=2000), pl.make_spec("P3-CS"), pl.make_spec("P3-CS", variant="a")):
        state = pl.fit_pipeline(spec, X, splits)
        recs = _h0_records(6, len(X), spec["H"], (12,))
        Z = state["rep"].transform_panel(X)
        assert pl.run_pipeline(spec, Z, splits, recs, state).equals(pl.run_pipeline(spec, X, splits, recs, state))


def test_guards_and_monitor_reset(d2):
    X, _, splits = d2
    spec = pl.make_spec("P3-C")
    state = pl.fit_pipeline(spec, X, splits)
    with pytest.raises(ValueError):
        pl.run_pipeline(spec, X, splits, [{"seed": [1], "tau_star": len(X) - 10, "family": "H0"}], state)
    bad = X.copy()
    bad[100, 3] = np.nan
    with pytest.raises(ValueError):
        pl.run_pipeline(spec, bad, splits, [{"seed": [1], "tau_star": 50, "family": "H0"}], state)
    for kw in ({"reading": "exact", "channels": "all"}, {"reading": "exact", "channels": [0, 1]},
               {"foo": 1}, {"reading": "bootstrap"}):
        with pytest.raises(ValueError):
            pl.make_spec("P3-C", **kw)
    with pytest.raises(ValueError):
        pl.make_spec("P9")
    with pytest.raises(ValueError):
        pl.run_pipeline(spec, X, splits, [{"seed": [1], "tau_star": 100, "family": "F1"}])
    rec = _h0_records(1, len(X), spec["H"], (13,))
    tau = rec[0]["tau_star"]
    moved = X.copy()
    moved[:tau] *= -3.0
    moved[tau + spec["H"]:] *= 0.5
    assert pl.run_pipeline(spec, moved, splits, rec, state).equals(pl.run_pipeline(spec, X, splits, rec, state))


def test_p2c_recentred_stream_matches_worker(d2):
    X, _, splits = d2
    spec = pl.make_spec("P2-C", K=10, N_cal=10)
    state = pl.fit_pipeline(spec, X, splits)
    eps = X[:, state["cols"]].T
    for i in range(20):
        start = int(_rng(20, i).integers(0, X.shape[0] - (500 + 750) + 1))
        x = pl.PIPELINES["P2-C"][1](spec, state, X, {"seed": [i], "tau_star": start + 500, "family": "H0"})
        assert cusum.cusum_max_bilateral(x, 0.0) == calibration.worker_null_window_real(_rng(20, i), eps, 500, 750)


def test_p2c_bootstrap_fpr(d2):
    X, _, splits = d2
    spec = pl.make_spec("P2-C", K=20)
    state = pl.fit_pipeline(spec, X, splits)
    recs = [{"seed": [7, 30, 1, i], "tau_star": int(_rng(30, 1, i).integers(0, X.shape[0] - 1250 + 1)) + 500,
             "family": "H0"} for i in range(2000)]
    fpr = pl.run_pipeline(spec, X, splits, recs, state)["detected"].mean()
    half = 2.5758293035489004 * math.sqrt(0.05 * 0.95 * (1 / 2000 + 1 / 20000))
    assert 0.05 - half <= fpr <= 0.05 + half and abs(half - 0.0132) < 1e-4
    eps = X[:, state["cols"]].T
    d = state["diagnostics"]
    f = streams.fraction_stream(eps - np.median(eps, axis=1, keepdims=True))
    assert d["K_eff_meas"] == 1.0 / (4.0 * np.var(f)) and d["K_eff_ana"] == 20 / (1.0 + 19 * d["rho_sign"])
    assert len(state["cols"]) == 20 and state["cols"] == pl.composition_for(20, 97).tolist()
    av = pl.make_spec("P2-C", reading="anytime-valid")
    assert pl.fit_pipeline(av, X, splits)["threshold"] == av["gamma"]


def test_p3d_energy_and_gamma_op(d2):
    X, _, splits = d2
    q = pl.residual_energy(sim.gaussian_latent(200000, 5, _rng(40)) ** 2, [0, 1, 2, 3, 4])
    assert abs(q.mean()) <= 4.0 / math.sqrt(len(q)) and abs(q.var() - 1.0) <= 0.05
    spec = pl.make_spec("P3-D", H=500)
    state = pl.fit_pipeline(spec, X, splits)
    a, b = splits["calib"]
    z_even = state["rep"].transform_panel(np.ascontiguousarray(X[a:b]))["z_even"]
    qc = pl.residual_energy(z_even, state["channels"]["residual"])
    peaks = cusum.cusum_trajectory_vec(np.lib.stride_tricks.sliding_window_view(qc, 500), 0.5).max(axis=1)
    lam = state["threshold"]
    assert (peaks > lam).mean() <= 0.05 < (peaks > lam * (1.0 - 1e-6)).mean()
    assert 1.0 < state["gamma_op"] < np.inf and state["gamma_op"] == lam / state["lam_iid"]
    assert state["gamma_spec"] > 1.0
    with pytest.raises(ValueError):
        pl.fit_pipeline(pl.make_spec("P3-D", H=942), X, splits)


def test_p3cs_stakes_predictable(d2):
    X, _, splits = d2
    spec = pl.make_spec("P3-CS")
    state = pl.fit_pipeline(spec, X, splits)
    norms = state["rep"].transform_panel(np.ascontiguousarray(X[:300]))["z_even"][:, 0]
    lam = pl.stakes(norms, state["sigma_bar"])
    for t in (0, 1, 150, 299):
        moved = norms.copy()
        moved[t:] *= 7.0
        assert np.array_equal(pl.stakes(moved, state["sigma_bar"])[:t + 1], lam[:t + 1])
    assert (lam <= 0.5).all() and np.array_equal(lam[0], np.minimum(0.5, np.asarray(state["c"]) / state["sigma_bar"]))
    Y = pl.PIPELINES["P3-CS"][1](spec, state, X, {"seed": [7, 50], "tau_star": 1000, "family": "H0"})
    w = state["rep"].transform_panel(np.ascontiguousarray(X[1000:1750]))
    x = 2.0 * streams.exact_sign_stream(w["z_odd"], np.random.default_rng(np.random.SeedSequence([7, 50, 7])))
    lam = pl.stakes(w["z_even"][:, 0], state["sigma_bar"])
    logm, ref = np.full((x.shape[1], 4, 2), -np.inf), np.empty(750)
    for t in range(750):
        logm = np.maximum(0.0, logm) + np.log(1.0 + np.stack([lam[t], -lam[t]], axis=-1)[None] * x[t][:, None, None])
        ref[t] = np.log(np.exp(logm).mean())
    got = eprocess.log_dictionary_edetector(Y[None], "cusum", eta0=(0.25,))[0]
    assert Y.shape == (750, 4 * x.shape[1]) and np.allclose(got, ref, rtol=1e-12, atol=1e-12)


def test_p3cs_pivot_eprocess_and_randomization(d2):
    X, _, splits = d2
    spec = pl.make_spec("P3-CS", variant="a")
    state = pl.fit_pipeline(spec, X, splits)
    pivots = state["rep"].transform_panel(np.ascontiguousarray(X[900:1650]))["z_odd"]
    bets = np.array([side * b for b in pl.PIVOT_BETS for side in (1.0, -1.0)])
    ref = int(eprocess.first_alarm(eprocess.log_average_betting_eprocess(pivots, bets), spec["gamma"]))
    row = pl.run_pipeline(spec, X, splits, [{"seed": [7, 51], "tau_star": 900, "family": "H0"}], state).iloc[0]
    assert row["alarm_index"] == (900 + ref if ref >= 0 else -1)
    rand = pl.make_spec("P3-CS", variant="a", reading="randomization", B=300)
    state = pl.fit_pipeline(rand, X, splits, key=[7, 52])
    P = state["rep"].transform_panel(X)["z_odd"] / state["rms"]
    g = np.random.default_rng(np.random.SeedSequence([7, 52, 0]))
    m = cusum.cusum_max_bilateral_vec(np.moveaxis(calibration.null_windows(P, 750, 300, g, flip=True), -1, -2), 0.0)
    assert state["threshold"] == calibration.bootstrap_threshold(m.max(axis=-1), 0.05)
    assert pl.fit_pipeline(pl.make_spec("P3-CS", variant="a", reading="randomization", B=301), X, splits,
                           key=[7, 52])["threshold"] != state["threshold"]
    with pytest.raises(ValueError):
        pl.make_spec("P3-CS", reading="randomization")
    with pytest.raises(ValueError):
        pl.make_spec("P3-CS", variant="c")


def test_null_fpr_d6(d2):
    X, _, splits = d2
    specs = (pl.null_specs("P3-C", "d2_us97", 6) + [pl.make_spec("P2-C", reading="anytime-valid", gamma=15000.0),
                                                     pl.make_spec("P3-CS", variant="a"),
                                                     pl.make_spec("P3-CS", variant="a", reading="randomization")])
    rows, summary = pl.null_check(specs, X, splits, 2000, [7, 60])
    assert len(rows) == 2000 * len(specs) and (rows["family"] == "H0").all()
    assert summary["ok"].all(), summary[["pipeline", "reading", "fpr", "lo", "hi", "target"]]
    exact = summary[summary["reading"] == "exact"]
    level = lattice.select_threshold(0.05, H=750, delta=0.1, sided=2)["level"]
    assert len(exact) == 6 and np.allclose(exact["target"], level) and (exact["kind"] == "=").all()
    assert summary.loc[summary["reading"] == "randomization", ["lo", "hi"]].round(4).values.tolist() == [[0.0322, 0.0678]]
    bound = summary[(summary["kind"] == "<=")]
    assert len(bound) == 3 and np.allclose(bound["target"], 0.05)
    head, _ = pl.null_check(specs[:2], X, splits, 200, [7, 60])
    assert head.equals(pl.null_check(specs[:2], X, splits, 200, [7, 60])[0])
    first = rows[rows["run_id"].isin([pl.run_id(s) for s in specs[:2]])].groupby("run_id", sort=False).head(200)
    assert head.equals(first.reset_index(drop=True))


def test_null_check_rejects_zero_reps(d2):
    X, _, splits = d2
    with pytest.raises(ValueError, match="reps must be >= 1"):
        pl.null_check(pl.null_specs("P3-C", "d2_us97", 6), X, splits, 0, [7, 70])


def test_strong_f2_detected(d2):
    X, _, splits = d2
    T, N = X.shape
    C = np.broadcast_to(_rng(41).standard_normal((N, 4)), (T, N, 4)).copy()
    H, blocks, recs = 2000, [], []
    for r in range(50):
        g = _rng(40, r)
        Xs, _ = injection.symmetrize(X, g)
        tau = injection.draw_tau_star(0, T - 1, 500, H, g)
        Xt, delta, _ = injection.inject(Xs, "F2", tau, floors.kl_from_sharpe(8.0),
                                        {"calib": splits["calib"], "K": 6, "C": C}, g)
        blocks.append(Xt[tau:tau + H])
        recs.append({"seed": [7, 40, r], "tau_star": r * H, "family": "F2", "delta": delta[:H]})
    panel = np.concatenate(blocks)
    specs = {"P3-C": pl.make_spec("P3-C", mode="full", H=H), "P3-CS b": pl.make_spec("P3-CS", mode="full", H=H),
             "P7": pl.make_spec("P7", H=H), "P3-CS a": pl.make_spec("P3-CS", mode="full", variant="a", H=H),
             "P3-CS a rand": pl.make_spec("P3-CS", mode="full", variant="a", reading="randomization", H=H)}
    for name, spec in specs.items():
        state = pl.fit_pipeline(spec, X, splits)
        detected = pl.run_pipeline(spec, panel, splits, recs, state)["detected"]
        assert detected.all() if name in ("P3-C", "P3-CS b", "P7") else detected.mean() >= 0.9, (name, detected.mean())
    with pytest.raises(ValueError):
        pl.run_pipeline(specs["P7"], panel, splits, [{"seed": [1], "tau_star": 0, "family": "F2"}],
                        pl.fit_pipeline(specs["P7"], X, splits))
    with pytest.raises(ValueError):
        pl.null_check([specs["P7"]], X, splits, 10, [7, 64])


def test_cross_independence_gate(d2):
    X, _, splits = d2
    ok = pl.cross_independence(np.sign(sim.gaussian_latent(941, 5, _rng(61))))
    assert ok["passed"] and ok["pairs"] == 10 and ok["se"] == 1.0 / math.sqrt(941)
    state = pl.fit_pipeline(pl.make_spec("P3-C"), X, splits)
    a, b = splits["calib"]
    res = state["rep"].transform_panel(np.ascontiguousarray(X[a:b]))["z_odd"][:, state["channels"]["residual"]]
    bad = pl.cross_independence(np.sign(res))
    assert not bad["passed"] and bad["max_abs_rho"] > 3.0 / math.sqrt(941) and bad["over"] >= 1
    with pytest.raises(ValueError):
        pl.fit_pipeline(pl.make_spec("P3-C", mixture_s2=0.01), X, splits)
    with pytest.raises(ValueError):
        pl.make_spec("P3-C", mixture_s2=0.01, reading="exact", channels=[0])
    g = _rng(62)
    T, N = 3774, 97
    Y = (g.standard_normal((T, 4)) @ (g.standard_normal((N, 4)) * np.array([3.0, 1.5, 1.2, 1.0])).T
         + g.standard_normal((T, N))) * 0.01
    syn = {"pretrain": (0, 2768), "calib": (2833, 3774), "pre_monitor": (0, 3774),
           "dates": np.datetime64("2005-01-03") + np.arange(T)}
    spec = pl.make_spec("P3-C", mixture_s2=0.01)
    st = pl.fit_pipeline(spec, Y, syn)
    assert st["gate"]["passed"] and st["gate"]["pairs"] >= 1
    out = pl.run_pipeline(spec, Y, syn, _h0_records(20, T, 750, (63,)), st)
    assert len(out) == 20 and out["detected"].dtype == bool


def test_horizon_gamma():
    assert pl.horizon_gamma(750) == 15000.0 and pl.horizon_gamma(500, 0.1) == 5000.0
    spec = pl.make_spec("P3-C", gamma=pl.horizon_gamma(pl.H_DET))
    assert pl.null_target(spec, None) == (pytest.approx(pl.TARGET_FPR, rel=1e-12), "<=", None)


def test_cli_null_check_smoke(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert pl.main(["--pipeline", "P3-C", "--dataset", "d2_us97", "--null-check", "--reps", "50",
                        "--out", str(out), "--log-dir", str(out)]) == 0
        outs.append(out)
    stem = "P3-C_d2_us97_null"
    alarms = pd.read_csv(outs[0] / f"alarms_{stem}.csv", float_precision="round_trip", dtype={"run_id": str, "seed": str})
    runs = json.loads((outs[0] / f"runs_{stem}.json").read_text())
    assert len(alarms) == 50 * 7 and set(runs) == set(alarms["run_id"]) and len(runs) == 7
    for name in (f"alarms_{stem}.csv", f"runs_{stem}.json", "null_P3-C_d2_us97.log"):
        assert (outs[0] / name).read_bytes() == (outs[1] / name).read_bytes()
    assert str(tmp_path) not in (outs[0] / "null_P3-C_d2_us97.log").read_text()
    for argv in (["--pipeline", "P7", "--dataset", "d2_us97", "--null-check"], ["--pipeline", "P3-C", "--dataset", "d2_us97"]):
        with pytest.raises(SystemExit):
            pl.main(argv)
