"""Tests of the information audit (stream 11): experiments/audit_information.py."""
import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from experiments import audit_information as au
from jepadrift import floors as fl
from jepadrift.stats.covariance import ledoit_wolf

REPO = Path(__file__).resolve().parents[1]
REF = {"d2_us97": (5, 1.7452090047873516, "85147fd9f553130e", "d1_d2_profile.csv"),
       "d3_239": (10, 2.261923854892941, "6c44d64a3bf139be", "d3_profile.csv")}


@pytest.fixture(scope="module")
def panels():
    return {name: au.load(name) for name in REF}


def test_window_rows_bounds():
    dates = np.array(["2004-12-31", "2005-01-03", "2019-12-31", "2020-01-02"], dtype="datetime64[D]")
    assert au.window_rows(dates).tolist() == [False, True, True, False]


def test_window_and_frozen_basis(panels):
    for name, (K, edge, prefix, _) in REF.items():
        d = panels[name]
        assert d["dates"].min() >= np.datetime64("2005-01-01")
        assert d["dates"].max() == np.datetime64("2019-12-31")
        assert d["K"] == K and d["n_above"] == K + 1
        assert d["mp_edge"] == pytest.approx(edge, rel=1e-12)
        assert d["state_hash"].startswith(prefix)
    assert panels["d2_us97"]["C"] is None
    assert panels["d3_239"]["C"].shape == (3775, 239, 15) and np.isfinite(panels["d3_239"]["C"]).all()


def test_spectrum_and_eta(panels):
    for name, d in panels.items():
        spec = pd.DataFrame(au.spectrum_rows(d))
        sample, lw = (spec[spec.matrix == m].eigval.to_numpy() for m in ("cov_sample", "cov_lw"))
        assert lw.sum() == pytest.approx(sample.sum(), rel=1e-12)
        assert lw[0] < sample[0] and lw[-1] > sample[-1]
        corr = spec[spec.matrix == "corr_sample"]
        assert int((corr.eigval > corr.mp_edge).sum()) == d["n_above"]
        eta = pd.DataFrame(au.eta_rows(d))
        assert eta.year.tolist() == list(range(2005, 2020))
        assert (eta.eta_lw < eta.eta_sample).all()
        assert eta.n_days.sum() == len(d["dates"])


def test_sign_corr_matches_profiles(panels):
    for name, (_, _, _, profile) in REF.items():
        rows = pd.DataFrame(au.sign_rows(panels[name])).set_index("segment")
        assert set(rows.index) == {"pretrain", "calib", "window"}
        prof = pd.read_csv(REPO / "results" / "data" / profile, float_precision="round_trip")
        ref = prof[(prof.dataset == name) & (prof.segment == "calib")].mean_sign_corr.iloc[0]
        cal = rows.loc["calib"]
        assert cal.rho_sign == pytest.approx(ref, rel=1e-12)
        assert cal.rho_gauss == pytest.approx(math.sin(math.pi * ref / 2), rel=1e-12)
        assert cal.K_eff == pytest.approx(1 / ref, rel=1e-12)
        assert cal.n_days == 941


def _brute_triples(y):
    n = len(y)
    T, bt, bst = 0, np.zeros(n, dtype=np.int64), {}
    for i, j, k in itertools.combinations(range(n), 3):
        g = int(np.sign(y[i] + y[j] - 2 * y[k]) + np.sign(y[i] + y[k] - 2 * y[j]) + np.sign(y[j] + y[k] - 2 * y[i]))
        T += g
        bt[[i, j, k]] += g
        for pair in ((i, j), (i, k), (j, k)):
            bst[pair] = bst.get(pair, 0) + g
    return T, int((bt ** 2).sum()), sum(v * v for v in bst.values())


def test_triples_matches_brute_force():
    y = np.random.default_rng(np.random.SeedSequence([11, 0])).standard_t(4, 37)
    T, bt2, bst2 = au.triples_counts(y)
    assert (T, bt2, bst2) == _brute_triples(y)
    n = 37
    var = ((n - 3) * (n - 4) / ((n - 1) * (n - 2)) * bt2 + (n - 3) / (n - 4) * bst2 + n * (n - 1) * (n - 2) / 6
           - (1 - (n - 3) * (n - 4) * (n - 5) / (n * (n - 1) * (n - 2))) * T ** 2)
    T2, z, p = au.triples_test(y)
    assert T2 == T
    assert z == pytest.approx(T / math.sqrt(var), rel=1e-12)
    assert p == pytest.approx(2 * stats.norm.sf(abs(z)), rel=1e-12)


def test_triples_null_and_power():
    rng = np.random.default_rng(np.random.SeedSequence([11, 1]))
    p_null = np.array([au.triples_test(rng.standard_normal(100))[2] for _ in range(400)])
    assert 0.022 <= (p_null < 0.05).mean() <= 0.078
    skewed = [au.triples_test(rng.exponential(size=100)) for _ in range(50)]
    assert np.mean([p < 0.05 for _, _, p in skewed]) >= 0.9
    assert all(z > 0 for _, z, _ in skewed)


def test_garch_filter_predictable():
    y = np.random.default_rng(np.random.SeedSequence([11, 2])).standard_normal(300)
    s = au.garch_filter(y, 0.05, 0.08, 0.9)
    assert s[0] ** 2 == pytest.approx(0.05 / 0.02)
    assert s[1] ** 2 == pytest.approx(0.05 + 0.08 * y[0] ** 2 + 0.9 * 0.05 / 0.02)
    y2 = y.copy()
    y2[150:] *= 3.0
    s2 = au.garch_filter(y2, 0.05, 0.08, 0.9)
    assert np.array_equal(s[:151], s2[:151])
    assert not np.array_equal(s[151:], s2[151:])


def test_char_directions():
    rng = np.random.default_rng(np.random.SeedSequence([11, 5]))
    V_f = np.linalg.qr(rng.standard_normal((20, 20)))[0][:, :4]
    C = rng.standard_normal((6, 20, 3))
    U = au.char_directions(C, V_f)
    assert U.shape == (6, 20, 3)
    assert np.abs(np.einsum("nk,tnp->tkp", V_f, U)).max() < 1e-12
    assert np.abs(np.linalg.norm(U, axis=1) - 1.0).max() < 1e-12
    assert (np.einsum("tnp,tnp->tp", U, C) > 0).all()
    C[2, :, 1] = V_f @ rng.standard_normal(4)
    with pytest.raises(ValueError):
        au.char_directions(C, V_f)


def _holm(p):
    order = np.argsort(p)
    m, adj, run = len(p), np.empty(len(p)), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i]))
        adj[i] = run
    return adj


def test_symmetry_holm_joint():
    rng = np.random.default_rng(np.random.SeedSequence([11, 6]))
    series = {f"s{i}": rng.standard_normal(400) for i in range(3)}
    series["shift"] = rng.standard_normal(400) + 0.5
    flat = {"omega": 1.0, "alpha": 0.0, "beta": 0.0, "converged": True}
    scales = {k: (np.ones(400), flat) for k in series}
    rows = pd.DataFrame(au.symmetry_rows("toy", series, scales)).set_index("direction")
    assert rows.binom_reject.tolist() == [False, False, False, True]
    assert not rows.triples_reject.any()
    p_all = np.r_[rows.binom_p.to_numpy(), rows.triples_p.to_numpy()]
    got = np.r_[rows.binom_p_holm.to_numpy(), rows.triples_p_holm.to_numpy()]
    assert got == pytest.approx(_holm(p_all), rel=1e-12)


def test_debiased_sr2_unbiased():
    rng = np.random.default_rng(np.random.SeedSequence([11, 3]))
    d, n1, n2, reps = 30, 250, 250, 2000
    nu, c = n1 + n2 - 2, 1 / n1 + 1 / n2
    shift = np.full(d, math.sqrt(4 / 252 / d))
    drift = np.array([au.debiased_sr2(rng.standard_normal((n1, d)), rng.standard_normal((n2, d)) + shift)
                      for _ in range(reps)])
    null = np.array([au.debiased_sr2(rng.standard_normal((n1, d)), rng.standard_normal((n2, d)))[1]
                     for _ in range(reps)])
    se = drift.std(axis=0, ddof=1) / math.sqrt(reps)
    spec_bias = 252 * c * d * (d + 1) / nu
    assert abs(drift[:, 1].mean() - 4) < 4 * se[1]
    assert abs(drift[:, 2].mean() - (4 + spec_bias)) < 4 * se[2]
    assert abs(drift[:, 1].mean() - (4 + spec_bias)) > 4 * se[1]
    assert abs(null.mean()) < 4 * null.std(ddof=1) / math.sqrt(reps)
    with pytest.raises(ValueError):
        au.debiased_sr2(rng.standard_normal((10, 30)), rng.standard_normal((10, 30)))


def test_mbb_indices():
    idx = au.mbb_indices(53, 7, np.random.default_rng(np.random.SeedSequence([11, 7])))
    assert idx.shape == (7, 53) and idx.min() >= 0 and idx.max() < 53
    for row in idx:
        for s in range(0, 53, 20):
            run = row[s:s + 20]
            assert np.array_equal(run, np.arange(run[0], run[0] + run.size))
            assert run[0] <= 53 - 20
    again = au.mbb_indices(53, 7, np.random.default_rng(np.random.SeedSequence([11, 7])))
    assert np.array_equal(idx, again)


def test_spy_transitions(panels):
    dates = panels["d2_us97"]["dates"]
    ps = au.spy_phases("strict_ps", dates)
    tr = au.transitions(ps)
    got = [(ps[i][2], ps[i][3].size, ps[j][3].size) for i, j in tr]
    assert len(tr) == 10
    assert got[0] == ("2007-10-09", 696, 355)
    assert got[-1] == ("2018-12-24", 65, 256)
    assert all(dates[rows].max() <= np.datetime64("2019-12-31") for _, _, _, rows in ps)
    lt = au.spy_phases("lt_spy", dates)
    bounds = [lt[i][2] for i, _ in au.transitions(lt)]
    assert len(bounds) == 9
    assert not {"2008-10-27", "2008-11-04", "2008-11-20"} & set(bounds)


def test_drift_rows_sums():
    rng = np.random.default_rng(np.random.SeedSequence([11, 8]))
    T, N, K = 200, 70, 3
    d = {"X": rng.standard_normal((T, N)), "eigvec": np.eye(N), "K": K}
    Ys = au.subspaces(d, {})
    assert {k: v.shape[1] for k, v in Ys.items()} == {"market": 1, "factor": 3, "idio:b1": 30, "idio:b2": 30,
                                                       "idio:b3": 6}
    phases = [(0, "2010-01-01", "2010-05-03", np.arange(0, 80)), (1, "2010-05-03", "2010-12-31", np.arange(80, 200))]
    rows = pd.DataFrame(au.drift_rows("toy", "test", phases, Ys, 20))
    tr = rows[rows.level == "transition"].set_index("subspace")
    for col in ("sr2_raw", "sr2_debiased", "sr2_spec"):
        idio = tr.loc[["idio:b1", "idio:b2", "idio:b3"], col].sum()
        assert tr.loc["idio", col] == pytest.approx(idio, rel=1e-12)
        assert tr.loc["residual_full", col] == pytest.approx(tr.loc["factor", col] + idio, rel=1e-12)
    assert tr.loc["residual_full", "d"] == N - 1 and tr.loc["idio", "d"] == N - K - 1
    assert tr.d.drop(["idio", "residual_full"]).max() <= 30
    assert (tr.ci_lo <= tr.ci_hi).all() and (tr.n_boot == 20).all()
    assert tr.boundary.unique().tolist() == ["2010-05-03"] and tr.transition.unique().tolist() == ["0-1"]
    med = rows[rows.level == "median"].set_index("subspace")
    assert set(med.index) == set(tr.index) and (med.n_transitions == 1).all()
    assert med.sr2_debiased.to_dict() == tr.sr2_debiased.to_dict()


def test_drift_ci_brackets_the_estimate():
    rng = np.random.default_rng(np.random.SeedSequence([11, 12]))
    T, N, K = 200, 40, 3
    d = {"X": 0.01 * rng.standard_normal((T, N)), "eigvec": np.eye(N), "K": K}
    phases = [(0, "2010-01-01", "2010-05-03", np.arange(0, 80)), (1, "2010-05-03", "2010-12-31", np.arange(80, 200))]
    rows = pd.DataFrame(au.drift_rows("toy", "test", phases, au.subspaces(d, {}), 400))
    assert ((rows.ci_lo <= rows.sr2_debiased) & (rows.sr2_debiased <= rows.ci_hi)).all()


def test_n1():
    Z = np.where(np.random.default_rng(np.random.SeedSequence([11, 9])).random((50, 8)) < 0.5, -1.0, 1.0)
    raw, corrected = au.n1(Z)
    assert raw == pytest.approx(1.0) and corrected == pytest.approx(6 / 8)
    raw, corrected = au.n1(np.vstack([Z[:25], 2.0 * Z[25:]]))
    assert raw == pytest.approx(1.5625) and corrected == pytest.approx(1.5625 * 6 / 8)


def test_rolling_lw_past_only():
    X = np.random.default_rng(np.random.SeedSequence([11, 10])).standard_normal((100, 5))
    first = next(au.rolling_lw(X, 60))
    assert np.array_equal(first, ledoit_wolf(X[:60])[0])
    X2 = X.copy()
    X2[60:] *= 5.0
    assert np.array_equal(next(au.rolling_lw(X2, 60)), first)
    assert len(list(au.rolling_lw(X, 60))) == 40


def test_info_ratio():
    rng = np.random.default_rng(np.random.SeedSequence([11, 11]))
    N, T, m = 6, 40, 3
    S0 = np.cov(rng.standard_normal((50, N)), rowvar=False)
    A = rng.standard_normal((N, m))
    ratio, i_cond, i_stat = au.info_ratio(np.broadcast_to(A, (T, N, m)), (S0 for _ in range(T)))
    assert ratio == pytest.approx(np.ones(m), rel=1e-12)
    assert i_cond == pytest.approx(0.5 * np.einsum("nm,nm->m", A, np.linalg.solve(S0, A)), rel=1e-12)
    assert i_stat == pytest.approx(i_cond, rel=1e-12)
    sigmas = [np.cov(rng.standard_normal((N + 3, N)), rowvar=False) + 0.1 * np.eye(N) for _ in range(T)]
    ratio, _, _ = au.info_ratio(rng.standard_normal((T, N, m)), iter(sigmas))
    assert (ratio >= 1.0).all()


def test_mvt_nu_recovers_nu():
    rng = np.random.default_rng(np.random.SeedSequence([11, 4]))
    n, d, nu = 20000, 5, 5.0
    L = np.linalg.cholesky(np.cov(rng.standard_normal((50, d)), rowvar=False))
    Z = (rng.standard_normal((n, d)) @ L.T) / np.sqrt(rng.chisquare(nu, n) / nu)[:, None]
    est, iterations, converged = au.mvt_nu(Z)
    assert converged and iterations < 500
    assert abs(est - nu) < 0.5


def test_t_ratio():
    assert au.t_ratio(5.0) == pytest.approx(1.25)
    assert math.isnan(au.t_ratio(2.0))
    assert au.t_ratio(1e6) == pytest.approx(1.0, abs=1e-5)


def _vol_panel(regimes):
    rng = np.random.default_rng(np.random.SeedSequence([11, 21]))
    T, N = 400, 12
    X = rng.standard_normal((T, N)) @ np.linalg.cholesky(np.cov(rng.standard_normal((50, N)), rowvar=False)).T
    if regimes:
        X *= np.repeat(np.where(np.arange(T // 100) % 2 == 0, 1.0, 3.0), 100)[:, None]
    return X, rng.standard_normal((N, 3))


def test_n2_noise_null_and_workers():
    X, A = _vol_panel(False)
    keys = [[11, 11, 0, b] for b in range(8)]
    noise = au.n2_noise(X, A, None, keys, 1)
    assert noise.shape == (8, 3) and (noise > 1).all()
    assert np.array_equal(noise, au.n2_noise(X, A, None, keys, 2))
    value = au.info_ratio(au._directions(A, None, len(X)), au.rolling_lw(X))[0]
    assert np.abs(value / np.median(noise, axis=0) - 1).max() < 0.05


def test_n2_noise_volatility_regimes():
    X, A = _vol_panel(True)
    noise = au.n2_noise(X, A, None, [[11, 11, 0, b] for b in range(8)], 1)
    value = au.info_ratio(au._directions(A, None, len(X)), au.rolling_lw(X))[0]
    assert (value / np.median(noise, axis=0) > 1.5).all()


def test_rotate_phases():
    phases = [(0, "a", "b", np.arange(0, 30)), (1, "b", "c", np.arange(30, 75)), (2, "c", "d", np.arange(75, 100))]
    same = au.rotate_phases(phases, 100, 0)
    assert all(np.array_equal(p[3], q[3]) for p, q in zip(phases, same))
    moved = au.rotate_phases(phases, 100, 80)
    assert [p[3].size for p in moved] == [30, 45, 25]
    assert np.array_equal(np.sort(np.concatenate([p[3] for p in moved])), np.arange(100))
    assert np.array_equal(moved[0][3], np.r_[np.arange(0, 10), np.arange(80, 100)])
    assert np.array_equal(moved[1][3], np.arange(10, 55))


def _chain(lengths):
    edges = np.r_[0, np.cumsum(lengths)]
    return [(k, f"2010-{k + 1:02d}-01", f"2010-{k + 2:02d}-01", np.arange(edges[k], edges[k + 1]))
            for k in range(len(lengths))]


def test_placebo_controls():
    lengths = [120, 80, 150, 100, 130, 90, 110, 140]
    phases, T = _chain(lengths), sum(lengths)
    rng = np.random.default_rng(np.random.SeedSequence([11, 22]))
    shift = np.concatenate([np.full(n, 0.004 if k % 2 == 0 else -0.004) for k, n in enumerate(lengths)])
    y = (0.01 * rng.standard_normal(T) + shift)[:, None]
    row, sel = au.placebo_rows("toy", "test", phases, y, 400, 200)
    assert sel["selection_excess"] > 0 and sel["p_placebo"] < 0.05 and sel["selection_factor"] > 1
    assert row["level"] == "placebo" and row["subspace"] == "market" and row["n_transitions"] == len(lengths) - 1
    assert row["ci_lo"] <= row["sr2_debiased"] <= row["ci_hi"] and row["n_boot"] == 200
    _, null = au.placebo_rows("toy", "test", phases, (0.01 * rng.standard_normal(T))[:, None], 400, 200)
    assert 0.025 <= null["p_placebo"] <= 0.975


def test_placebo_selection_committed():
    sel = pd.read_csv(REPO / "results" / "audit" / "placebo_selection.csv", float_precision="round_trip")
    assert set(sel.dataset) == set(REF) and set(sel.dating) == set(au.DATINGS)
    assert (sel.selection_excess > 0).all() and (sel.p_placebo < 0.05).all()


def test_budget_share():
    base = {"dataset": "toy", "dating": "x", "level": "transition", "subspace": "market", "n2": 300}
    drift = pd.DataFrame([{**base, "sr2_debiased": 10.0}, {**base, "sr2_debiased": 9.0},
                          {**base, "sr2_debiased": -5.0},
                          {**base, "level": "median", "n2": np.nan, "sr2_debiased": 9.0},
                          {**base, "subspace": "idio:b1", "sr2_debiased": 50.0}])
    rows = pd.DataFrame(au.budget_rows(drift)).set_index("gamma")
    assert rows.subspace.unique().tolist() == ["market"]
    assert rows.loc[20, "n_phases"] == 3 and rows.loc[20, "n_in_budget"] == 2
    assert rows.loc[252, "n_in_budget"] == 1 and rows.loc[252, "share"] == pytest.approx(1 / 3)


def test_planning_table_reproduced():
    rho, rho_s = 0.40, 0.26
    cases = ((97, 0.25, 2.461929, 3.736518, 16.416667, 42.878596), (97, 1 / 16, 2.461929, 3.736518, 4.104167, None),
             (97, 1.0, 2.461929, 3.736518, 65.666667, None), (239, 0.25, 2.484407, None, 40.083333, 102.067740),
             (239, 1 / 16, 2.484407, None, 10.020833, None), (239, 1.0, 2.484407, None, 160.333333, None))
    for N, kappa2, g12, g12s, g23, g13 in cases:
        sr2_i = kappa2 * (1 + (N - 1) * rho) / (1 - rho)
        rows = {r["step"]: r for r in au.planning_gains(N, 10, rho, rho_s, 1.0, 0.5, sr2_i, 252)}
        assert rows["1-2:F3"]["G_floor"] == pytest.approx(g12, rel=1e-6)
        if g12s is not None:
            assert rows["1-2:F3"]["G_floor_sign"] == pytest.approx(g12s, rel=1e-6)
        assert rows["2-3:F2"]["G_floor"] == pytest.approx(g23, rel=1e-6)
        assert rows["2-3:F2"]["kappa_hat"] == pytest.approx(math.sqrt(kappa2), rel=1e-12)
        if g13 is not None:
            assert rows["1-3:F3+F2"]["G_floor"] == pytest.approx(g13, rel=1e-6)
        m1 = fl.mixture_multiplier(1, 252)
        assert rows["2-3:F1"]["G_tax"] == pytest.approx(0.5 * m1 / fl.mixture_multiplier(10, 252), rel=1e-12)
        assert rows["2-3:F2"]["G_tax"] == pytest.approx(g23 * m1 / fl.mixture_multiplier(N - 1, 252), rel=1e-6)
        assert rows["1-2:F3"]["G_tax"] == rows["1-2:F3"]["G_floor"]
        assert math.isnan(rows["1-3:F3+F2"]["G_tax"])


def test_predicted_nan_on_nonpositive_median():
    rows = {r["step"]: r for r in au.planning_gains(97, 5, 0.4, 0.26, 10.0, 1.0, -3.0, 252)}
    for step in ("2-3:F2", "1-3:F3+F2"):
        assert math.isnan(rows[step]["G_floor"]) and math.isnan(rows[step]["kappa_hat"])
    assert rows["1-2:F3"]["G_floor"] == pytest.approx(97 / 39.4)
    assert rows["2-3:F1"]["G_floor"] == pytest.approx(0.1)
    rows = {r["step"]: r for r in au.planning_gains(97, 5, 0.4, 0.26, -1.0, 1.0, 3.0, 252)}
    assert all(math.isnan(rows[s]["G_floor"]) for s in ("2-3:F1", "2-3:F2", "1-3:F3+F2"))
    assert rows["1-2:F3"]["G_floor"] == pytest.approx(97 / 39.4)


COLUMNS = {
    "spectrum": ["dataset", "matrix", "rank", "eigval", "share", "cum_share", "n_days", "mp_edge", "n_above_edge",
                 "K", "lw_shrinkage"],
    "eta_by_year": ["dataset", "year", "n_days", "eta_sample", "eta_lw", "lw_shrinkage"],
    "sign_corr": ["dataset", "segment", "n_days", "N", "rho_sign", "rho_gauss", "rho_ret", "K_eff", "K_eff_N",
                  "rho_sign_med", "K_eff_meas", "K_eff_ana"],
    "symmetry_tests": ["dataset", "direction", "n", "q_hat", "binom_p", "triples_T", "triples_z", "triples_p",
                       "garch_omega", "garch_alpha", "garch_beta", "garch_converged", "binom_p_holm",
                       "triples_p_holm", "binom_reject", "triples_reject"],
    "drift_sharpe_transitions": ["dataset", "dating", "level", "transition", "boundary", "n1", "n2",
                                 "n_transitions", "subspace", "d", "sr2_raw", "sr2_debiased", "sr2_spec", "ci_lo",
                                 "ci_hi", "n_boot"],
    "channel_ceilings": ["dataset", "ceiling", "variant", "direction", "value", "i_cond", "i_static", "nu",
                         "iterations", "converged", "n_days", "d"],
    "budget_share": ["dataset", "dating", "subspace", "gamma", "n_phases", "n_in_budget", "share"],
    "predicted_gains": ["dataset", "dating", "step", "gamma", "N", "K", "rho_ret", "rho_sign", "kappa_hat",
                        "sr2_market", "sr2_factor", "sr2_idio", "D_A", "D_B", "M_A", "M_B", "G_floor",
                        "G_floor_sign", "G_tax"],
    "placebo_selection": ["dataset", "dating", "n_transitions", "n_placebo", "sr2_real_median", "sr2_placebo_median",
                          "ci_lo", "ci_hi", "selection_factor", "selection_excess", "p_placebo"],
}


def test_cli_quick_d2(tmp_path):
    out, fig, log = tmp_path / "out", tmp_path / "fig", tmp_path / "log"
    assert au.main(["--datasets", "d2_us97", "--quick", "--jobs", "2", "--out", str(out), "--fig-dir", str(fig),
                    "--log-dir", str(log)]) == 0
    frames = {name: pd.read_csv(out / f"{name}.csv", float_precision="round_trip") for name in COLUMNS}
    for name, cols in COLUMNS.items():
        assert list(frames[name].columns) == cols, name
        assert set(frames[name].dataset) == {"d2_us97"}, name
    assert sorted(p.name for p in fig.iterdir()) == sorted(
        f"{stem}.{ext}" for stem in ("spectrum", "symmetry", "drift_sharpe", "budget_share") for ext in ("png", "pdf"))
    assert str(au.REPO_ROOT) not in (log / "audit.log").read_text()
    drift = frames["drift_sharpe_transitions"]
    assert pd.to_datetime(drift.boundary.dropna()).max() <= pd.Timestamp("2019-12-31")
    assert set(drift.dating) == set(au.DATINGS) and (drift.n_boot == 50).all()
    assert frames["symmetry_tests"].direction.tolist() == ["PC1", "PC2", "PC3"]
    assert set(frames["channel_ceilings"].ceiling) == {"N1", "N2", "N3"}
    n2 = frames["channel_ceilings"][frames["channel_ceilings"].ceiling == "N2"]
    assert set(n2.variant) == {"lw60", "lw60_shuffle", "lw60_net"}
    assert (drift[drift.level == "placebo"].subspace == "market").all()
    assert len(drift[drift.level == "placebo"]) == len(au.DATINGS) == len(frames["placebo_selection"])
    assert len(frames["predicted_gains"]) == len(au.DATINGS) * 4 * len(au.GAMMAS)


def test_cli_rejects_bad_boot():
    with pytest.raises(SystemExit):
        au.main(["--boot", "0"])
