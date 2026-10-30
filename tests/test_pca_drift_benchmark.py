"""Tests of experiments/pca_drift_benchmark.py (stream 28): kernels, selection, identifiers, real guard, CLI."""
import itertools
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import pca_drift_benchmark as pdb
from jepadrift import floors, injection
from jepadrift.data_loader import sp500
from jepadrift.monitors import eprocess
from jepadrift.representations.extract import segment_rows
from jepadrift.representations.pca import mp_count

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "configs" / "pca_drift_benchmark.yaml"
OUTPUTS = ("manifest.json", "spectra.csv", "selection.csv", "calibration.csv", "trials.csv", "aggregates.csv",
           "issues.csv")


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([28, 99, *key]))


def tiny_cfg(**over):
    cfg = pdb.load_config(CONFIG, "smoke")
    cfg.update(N=24, H=12, T_fit=80, nmax=6, n_center=6, n_cal=19, n_null=8, n_alt=8, minibatch=3, cov_search_chunk=7)
    cfg["synthetic"]["C_axes"] = [3, 5]
    cfg.update(over)
    return cfg


def _slow_loglik(z, s2):
    H, d = z.shape
    out = np.full((H, H), np.nan)
    for t in range(1, H + 1):
        for tau in range(1, t + 1):
            D = z[tau - 1:t].sum(axis=0)
            n = t - tau + 1
            out[t - 1, tau - 1] = -0.5 * d * math.log1p(n * s2) + s2 * float(D @ D) / (2.0 * (1.0 + n * s2))
    return out


def test_g1_mixture_cost_matches_fixed_point_and_deck():
    for d in (1, 2, 4, 8, 16, 20, 500):
        m = pdb.mixture_cost(d, 504)
        assert m == pytest.approx(floors.mixture_multiplier(d, 504), rel=1e-10)
        x, a = m * math.log(504), math.log(504)
        assert x == pytest.approx(a + 0.5 * d * math.log1p(2.0 * x / d), rel=1e-12)
    for d, ref in {1: 1.2239, 4: 1.5696, 8: 1.8785, 16: 2.3290, 500: 9.6427}.items():
        assert abs(pdb.mixture_cost(d, 504) - ref) < 6e-5
    assert all(pdb.mixture_cost(d, 504) > 1.0 for d in range(1, 21))
    for bad in [(0, 504), (1, 1.0), (1, 0.5), (2.5, 504), (True, 504)]:
        with pytest.raises(ValueError):
            pdb.mixture_cost(*bad)


def test_g1_affine_chord_is_fixed_between_1_and_20():
    a, c = pdb.affine_costs(504)
    assert a > 0 and c > 0
    assert a + c == pytest.approx(pdb.mixture_cost(1, 504), rel=1e-14)
    assert a + 20 * c == pytest.approx(pdb.mixture_cost(20, 504), rel=1e-14)
    tables = {nmax: pdb.cost_tables(504, nmax) for nmax in (1, 6, 20)}
    for nmax, (mix, aff) in tables.items():
        assert mix.shape == aff.shape == (nmax,)
        np.testing.assert_array_equal(aff, tables[20][1][:nmax])
        np.testing.assert_array_equal(mix, tables[20][0][:nmax])


def test_g1_mean_kl_identity_in_eigenbasis_and_order_counterexample():
    g = _rng(1)
    A = g.standard_normal((6, 6))
    sigma = A @ A.T + 6.0 * np.eye(6)
    lam, V = np.linalg.eigh(sigma)
    lam, V = lam[::-1], V[:, ::-1]
    delta = g.standard_normal(6)
    full = pdb.kl_mean(delta, sigma)
    assert full == pytest.approx(0.5 * delta @ np.linalg.solve(sigma, delta), rel=1e-12)
    assert pdb.q_plugin(V.T @ delta, lam).sum() == pytest.approx(full, rel=1e-12)
    q_last = pdb.q_plugin(V.T @ (0.3 * V[:, -1]), lam)
    assert int(np.argmax(q_last)) == 5
    assert q_last[0] < 1e-30


def test_g1_joint_cov_kl_differs_from_marginal_sum():
    c, s = math.cos(math.pi / 4), math.sin(math.pi / 4)
    R = np.array([[c, -s], [s, c]])
    s0 = np.diag([4.0, 1.0])
    s1 = R @ s0 @ R.T
    joint, marg = pdb.kl_cov(s0, s1), pdb.cov_marginals(s0, s1)
    assert joint == pytest.approx(0.5625, abs=1e-12)
    assert marg.sum() == pytest.approx(0.3394, abs=1e-4)
    assert abs(joint - marg.sum()) > 0.2
    batch = pdb.kl_cov_batch(np.stack([s0, s0]), np.stack([s1, s0]))
    np.testing.assert_allclose(batch, [0.5625, 0.0], atol=1e-12)


def test_g1_pop_joint_dpi_monotone_non_additive_and_whitening_invariant():
    g = _rng(2)
    N = 8
    A = g.standard_normal((N, N))
    sigma0 = A @ A.T + N * np.eye(N)
    P = g.standard_normal((N, N))
    lam_hat, V_hat = np.linalg.eigh(sigma0 + 0.5 * (P + P.T))
    lam_hat, V_hat = lam_hat[::-1][:5], V_hat[:, ::-1][:, :5]
    delta = g.standard_normal(N)
    W = V_hat / np.sqrt(lam_hat)
    C0, mu = W.T @ sigma0 @ W, W.T @ delta

    def info(S):
        return pdb.kl_mean(mu[S], C0[np.ix_(S, S)])

    assert info([0, 1, 2, 3, 4]) <= pdb.kl_mean(delta, sigma0) + 1e-12
    assert info([0]) <= info([0, 1]) <= info([0, 1, 2]) <= info([0, 1, 2, 3, 4])
    assert abs(info([0, 1]) - info([0]) - info([1])) > 1e-6
    Cu, beta = V_hat.T @ sigma0 @ V_hat, V_hat.T @ delta
    assert pdb.kl_mean(beta, Cu) == pytest.approx(pdb.kl_mean(mu, C0), rel=1e-12)
    B = g.standard_normal((N, N))
    sigma1 = sigma0 + 0.3 * B @ B.T
    C1, Cu1 = W.T @ sigma1 @ W, V_hat.T @ sigma1 @ V_hat
    assert pdb.kl_cov(Cu, Cu1) == pytest.approx(pdb.kl_cov(C0, C1), rel=1e-12)
    X = g.standard_normal((9, N))
    U, Z = X @ V_hat, X @ W
    np.testing.assert_allclose(pdb.llr_mean(Z, mu, C0), pdb.llr_mean(U, beta, Cu), rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(pdb.llr_cov(Z, C0, C1), pdb.llr_cov(U, Cu, Cu1), rtol=1e-10, atol=1e-12)


def test_g1_scan_matches_slow_reference():
    s2 = 0.15
    for d in (1, 2, 4):
        for H in (1, 5, 12):
            z = 0.7 * _rng(3, d, H).standard_normal((H, d)) + 0.2
            ref, L = _slow_loglik(z, s2), pdb.segment_loglik(z, s2)
            assert int(np.isfinite(L).sum()) == H * (H + 1) // 2
            np.testing.assert_array_equal(np.isfinite(L), np.isfinite(ref))
            np.testing.assert_allclose(L[np.isfinite(ref)], ref[np.isfinite(ref)], rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(L[:, 0], eprocess.log_subgaussian_mixture(z, s2), rtol=1e-12, atol=1e-12)
            W, first = pdb.scan_statistic(z[None], s2)
            np.testing.assert_allclose(W[0], np.nanmax(ref, axis=1), rtol=1e-12, atol=1e-12)
            assert first[0] == -1
            h = float(np.median(W[0]))
            _, first = pdb.scan_statistic(z[None], s2, h)
            assert first[0] == int(np.argmax(np.nanmax(ref, axis=1) >= h)) + 1


def test_g1_scan_edge_cases():
    s2 = 0.2
    zero = np.zeros((1, 6, 2))
    W, first = pdb.scan_statistic(zero, s2, 0.5)
    assert first[0] == -1
    np.testing.assert_array_equal(W[0], np.full(6, -np.log1p(s2)))
    _, first = pdb.scan_statistic(zero, s2, float(W[0, 0]))
    assert first[0] == 1
    spike = np.zeros((1, 4, 1))
    spike[0, 0, 0] = 10.0
    assert pdb.scan_statistic(spike, s2, 1.0)[1][0] == 1
    late = np.concatenate([np.zeros(6), np.full(6, 2.0)])[:, None]
    assert int(np.nanargmax(pdb.segment_loglik(late, s2)[11])) == 6
    for bad in [(np.zeros((2, 3)), s2), (np.zeros((1, 3, 1)), 0.0), (np.full((1, 3, 1), np.nan), s2),
                (np.zeros((1, 0, 1)), s2)]:
        with pytest.raises(ValueError):
            pdb.scan_statistic(*bad)


def test_g1_scan_is_minibatch_invariant():
    Z = _rng(4).standard_normal((7, 15, 3))
    W_all, _ = pdb.scan_statistic(Z, 0.1)
    _, f_all = pdb.scan_statistic(Z, 0.1, 2.0)
    for B in (1, 3, 7):
        W = np.concatenate([pdb.scan_statistic(Z[i:i + B], 0.1)[0] for i in range(0, 7, B)])
        f = np.concatenate([pdb.scan_statistic(Z[i:i + B], 0.1, 2.0)[1] for i in range(0, 7, B)])
        assert np.array_equal(W, W_all) and np.array_equal(f, f_all)


def test_p0_predictive_rank_threshold():
    m40, m2000 = np.arange(40.0), np.arange(2000.0)
    assert pdb.predictive_rank(40, 0.05) == 1 and pdb.predictive_bound(1, 40) == 2 / 41
    assert pdb.rank_threshold(m40, 0.05, "GT") == (38.0, 1, 1)
    assert pdb.rank_threshold(m40, 0.05, "GE") == (np.nextafter(38.0, np.inf), 1, 1)
    assert pdb.predictive_rank(2000, 0.05) == 99 and pdb.predictive_bound(99, 2000) == 100 / 2001
    assert pdb.rank_threshold(m2000, 0.05, "GT") == (1900.0, 99, 99)
    assert pdb.min_calibration_n(0.05) == 19 and pdb.predictive_rank(19, 0.05) == 0
    assert pdb.predictive_rank(18, 0.05) == -1 and pdb.predictive_bound(0, 19) == 0.05
    assert issubclass(pdb.InsufficientCalibration, pdb.CalibrationFailed)
    for n in (1, 5, 18):
        with pytest.raises(pdb.InsufficientCalibration, match=f"n = {n} .*at least 19"):
            pdb.rank_threshold(np.arange(float(n)), 0.05, "GE")
    assert pdb.rank_threshold(np.array([5.0, 1.0, 4.0, 2.0, 3.0]), 0.3, "GT") == (5.0, 0, 0)
    assert pdb.rank_threshold(np.array([1.0, 2.0, 2.0, 2.0, 3.0]), 0.4, "GT") == (2.0, 1, 1)
    assert pdb.rank_threshold(np.full(4, 2.0), 0.3, "GE") == (np.nextafter(2.0, np.inf), 0, 0)
    ties = np.concatenate([np.zeros(37), np.full(3, 5.0)])
    assert pdb.rank_threshold(ties, 0.05, "GE") == (np.nextafter(5.0, np.inf), 1, 0)
    assert pdb.rank_threshold(ties, 0.05, "GT") == (5.0, 1, 0)
    for alpha in (0.05, 0.3, 0.4):
        h_ge, r, a_ge = pdb.rank_threshold(m40, alpha, "GE")
        h_gt, _, a_gt = pdb.rank_threshold(m40, alpha, "GT")
        assert a_ge == a_gt == int((m40 >= h_ge).sum()) == int((m40 > h_gt).sum()) <= r
        assert pdb.predictive_bound(r, 40) <= alpha
    for bad in [(np.array([]), 0.05, "GE"), (np.array([np.nan]), 0.05, "GE"), (np.array([np.inf]), 0.05, "GT"),
                (np.zeros((2, 2)), 0.05, "GE"), (m40, 0.0, "GE"), (m40, 1.0, "GE"), (m40, -0.1, "GT"),
                (m40, 0.05, "X")]:
        with pytest.raises(ValueError):
            pdb.rank_threshold(*bad)
    top = np.concatenate([np.zeros(19), [np.finfo(np.float64).max]])
    with pytest.raises(pdb.CalibrationFailed, match="not finite"):
        pdb.rank_threshold(top, 0.05, "GE")
    assert pdb.rank_threshold(top, 0.05, "GT") == (np.finfo(np.float64).max, 0, 0)


def test_g1_vech_std_and_centering_identity():
    A = np.array([[4.0, 1.0, 2.0], [1.0, 9.0, 3.0], [2.0, 3.0, 16.0]])
    r2 = math.sqrt(2.0)
    np.testing.assert_array_equal(pdb.vech_std(A), [4.0 / r2, 9.0 / r2, 16.0 / r2, 1.0, 2.0, 3.0])
    Z = _rng(5).standard_normal((3, 10, 3)) * np.array([1.0, 2.0, 0.5])
    C = np.einsum("ntp,ntq->pq", Z, Z) / 30.0
    Y = pdb.vech_stream(Z, C)
    assert Y.shape == (3, 10, 6)
    np.testing.assert_allclose(Y.reshape(-1, 6).mean(axis=0), 0.0, atol=1e-12)


def test_g1_index_energy_decreases_under_rotation_with_positive_kl():
    N, rho = 12, 0.4
    sigma0 = pdb.equicorrelation(N, rho)
    X = np.linalg.cholesky(sigma0) @ _rng(6).standard_normal((N, 400))
    M = pdb.rotation(np.ascontiguousarray(X.T), 30.0, _rng(7))
    np.testing.assert_allclose(M @ M.T, np.eye(N), atol=1e-12)
    sigma1 = M @ sigma0 @ M.T
    a = np.full(N, 1.0 / N)
    assert a @ sigma1 @ a < a @ sigma0 @ a
    assert pdb.kl_cov(sigma0, sigma1) > 0.0
    np.testing.assert_allclose(pdb.equicorrelation_inverse(N, rho) @ sigma0, np.eye(N), atol=1e-12)
    fit = injection.fit_background(np.ascontiguousarray(X.T), 1)
    assert pdb.kl_cov(fit["sigma"], M @ fit["sigma"] @ M.T) == pytest.approx(
        injection.inject(np.ascontiguousarray(X.T), "F4-rotate", 0, None,
                         {"calib": (0, 400), "fit": fit, "pair": (0, 1), "theta_deg": 30.0}, _rng(7))[2]["info"],
        rel=1e-9)


def test_g2_smoke_config_changes_only_the_four_counts():
    full, smoke = pdb.load_config(CONFIG, "full"), pdb.load_config(CONFIG, "smoke")
    assert {k for k in full if full[k] != smoke[k]} == {"n_center", "n_cal", "n_null", "n_alt", "mode"}
    assert all(smoke[k] == 40 for k in ("n_center", "n_cal", "n_null", "n_alt"))
    assert (full["N"], full["H"], full["T_fit"], full["nmax"]) == (239, 250, 1000, 20)
    assert full["n_center"] == full["n_cal"] == full["n_null"] == full["n_alt"] == 2000
    assert full["synthetic"]["C_axes"] == [10, 20] and full["synthetic"]["rotation_deg"] == 30.0
    pdb.validate_config(full)
    pdb.validate_config(smoke)


def test_g2_validate_config_refuses_invalid_values():
    pdb.validate_config(tiny_cfg())
    for over in [dict(N=1), dict(nmax=0), dict(nmax=24), dict(N=40, nmax=21), dict(H=0), dict(T_fit=1),
                 dict(n_center=0), dict(n_cal=0), dict(n_null=0), dict(n_alt=0), dict(alpha=0.0), dict(alpha=1.0),
                 dict(gamma_M=1.0), dict(minibatch=0), dict(nmax=2.5)]:
        with pytest.raises(ValueError):
            pdb.validate_config(tiny_cfg(**over))
    for res in ({"mem_limit_gib": 0.0, "max_wall_minutes": 30.0}, {"mem_limit_gib": 8.0, "max_wall_minutes": 0.0}):
        with pytest.raises(ValueError):
            pdb.validate_config(tiny_cfg(resources=res))
    assert pdb.c_supported(tiny_cfg())
    for axes in ([3, 7], [1, 4], [5, 3]):
        cfg = tiny_cfg()
        cfg["synthetic"]["C_axes"] = axes
        assert not pdb.c_supported(cfg)


def test_g2_seed_keys_are_role_specific_and_reproducible():
    cfg = tiny_cfg()
    keys = {tuple(pdb.seed_key(cfg["seed"], "path", "SYNTH_T7_EQUICORR", role, 0)) for role in pdb.SEED_ROLES}
    assert len(keys) == len(pdb.SEED_ROLES) == 5
    a = pdb.draw_path(cfg, "SYNTH_T7_EQUICORR", "calibration", 3, 12)
    assert a.shape == (12, 24) and a.dtype == np.float64
    assert np.array_equal(a, pdb.draw_path(cfg, "SYNTH_T7_EQUICORR", "calibration", 3, 12))
    assert not np.array_equal(a, pdb.draw_path(cfg, "SYNTH_T7_EQUICORR", "holdout_null", 3, 12))
    assert not np.array_equal(a, pdb.draw_path(cfg, "SYNTH_GAUSS_EQUICORR", "calibration", 3, 12))


def test_g2_spectra_use_correlation_for_mp_and_kaiser():
    X = np.ascontiguousarray(0.01 * (np.linalg.cholesky(pdb.equicorrelation(15, 0.4))
                                     @ _rng(10).standard_normal((15, 200))).T)
    basis = pdb.fit_basis(X)
    assert (basis["eigval"] < 1.0).all() and basis["lambda_corr"][0] >= 1.0
    assert (basis["mp_count"], basis["mp_edge"]) == mp_count(X)
    assert basis["kaiser_count"] == int((basis["lambda_corr"] >= 1.0).sum()) >= 1
    assert np.all(np.diff(basis["cpv"]) >= 0.0) and basis["cpv"][-1] == pytest.approx(1.0, abs=1e-12)
    rows = pdb.spectra_rows(basis, {"dataset_id": "SYNTH_GAUSS_EQUICORR"}, nmax=6)
    assert [r["k"] for r in rows] == list(range(1, 16))
    assert [r["kaiser_ge1"] for r in rows] == [bool(v >= 1.0) for v in basis["lambda_corr"]]
    assert [r["mp_above"] for r in rows] == [bool(v > basis["mp_edge"]) for v in basis["lambda_corr"]]
    assert all(r["lambda_lw"] < 1.0 for r in rows) and rows[0]["basis_hash"] == basis["basis_hash"]


def test_g2_cpv90_inside_and_outside_top():
    assert pdb.cpv90(np.array([5.0, 3.0, 1.0, 0.5, 0.5])) == 3
    assert pdb.cpv90_status(3, 3) == "CPV90_IN_TOP20" and pdb.cpv90_status(3, 2) == "CPV90_OUTSIDE_TOP20"
    lam = np.r_[96.2, np.full(238, 0.6)]
    assert pdb.cpv90(lam) == 200
    assert lam[:14].sum() / lam.sum() == pytest.approx(0.435146, abs=1e-6)


def test_g2_scenarios_follow_declared_normalizations():
    cfg = tiny_cfg()
    X = pdb.draw_path(cfg, "SYNTH_GAUSS_EQUICORR", "fit", 0, 80)
    basis = pdb.fit_basis(X)
    V, lam = basis["eigvec"], basis["eigval"]
    s0, s0inv = pdb.equicorrelation(24, 0.4), pdb.equicorrelation_inverse(24, 0.4)
    beta_A, delta_A = pdb.scenario_A(V, s0, 4.0)
    v1 = V[:, 0]
    assert 0.5 * (v1 @ delta_A) ** 2 / (v1 @ s0 @ v1) == pytest.approx(16.0 / 504.0, rel=1e-12)
    assert (v1 @ delta_A) / math.sqrt(v1 @ s0 @ v1) * math.sqrt(252.0) == pytest.approx(4.0, rel=1e-12)
    np.testing.assert_allclose(V.T @ delta_A, beta_A, atol=1e-12)
    assert np.count_nonzero(beta_A) == 1
    beta_C, delta_C, c = pdb.scenario_C(V, s0inv, (3, 5), 3.0)
    assert c > 0.0 and 0.5 * delta_C @ s0inv @ delta_C == pytest.approx(3.0, rel=1e-12)
    np.testing.assert_allclose(V.T @ delta_C, beta_C, atol=1e-12)
    assert np.flatnonzero(beta_C).tolist() == [2, 3, 4]
    assert np.abs(V[:, :2].T @ delta_C).max() < 1e-12
    np.testing.assert_allclose(pdb.q_plugin(beta_C, lam), 0.5 * (beta_C / np.sqrt(lam)) ** 2, rtol=0, atol=0)
    M = pdb.rotation(X, 30.0, _rng(11))
    W = V[:, :6] / np.sqrt(lam[:6])
    s1 = M @ s0 @ M.T
    np.linalg.cholesky(s1)
    C0, C1 = W.T @ s0 @ W, W.T @ s1 @ W
    assert abs(C1[0, 1] - C0[0, 1]) > 1e-3


def test_g2_top_q_equals_exhaustive_and_greedy():
    for cost in pdb.cost_tables(504, 12):
        for seed in range(5):
            q = _rng(12, seed).exponential(size=12) * (_rng(13, seed).random(12) < 0.6)
            for k in range(1, 13):
                cand, sel = pdb.select_top_q(q, k, cost)
                assert [c["d"] for c in cand] == list(range(1, k + 1))
                best_v = max(q[list(S)].sum() / cost[d - 1] for d in range(1, k + 1)
                             for S in itertools.combinations(range(k), d))
                assert sel["V"] == pytest.approx(best_v, rel=1e-12, abs=1e-300)
                remaining, chosen, values = list(range(k)), [], []
                for d in range(1, k + 1):
                    j = max(remaining, key=lambda i: (q[i], -i))
                    remaining.remove(j)
                    chosen.append(j)
                    values.append(q[chosen].sum() / cost[d - 1])
                d_g = int(np.argmax(values)) + 1
                assert sel["d"] == d_g and sel["S"] == sorted(chosen[:d_g])


def test_g2_top_q_tie_rule():
    mix = pdb.cost_tables(504, 4)[0]
    _, sel = pdb.select_top_q(np.array([0.2, 0.5, 0.5, 0.0]), 4, mix)
    assert sel["rank_order"] == [1, 2, 0, 3]
    _, sel = pdb.select_top_q(np.zeros(4), 4, mix)
    assert sel["d"] == 1 and sel["S"] == [0] and sel["tie_broken"] and sel["V"] == 0.0


def test_g2_exhaustive_cov_matches_brute_force():
    g = _rng(14)
    A, B = g.standard_normal((6, 6)), g.standard_normal((6, 6))
    C0 = A @ A.T + 6.0 * np.eye(6)
    C1 = C0 + 0.5 * B @ B.T
    best, _ = pdb.exhaustive_cov(C0, C1, 6, chunk=4)
    for k in range(1, 7):
        for d in range(1, k + 1):
            vals = {S: pdb.kl_cov(C0[np.ix_(S, S)], C1[np.ix_(S, S)]) for S in itertools.combinations(range(k), d)}
            S_best = max(vals, key=vals.get)
            assert best[(k, d)][0] == pytest.approx(vals[S_best], rel=1e-12)
            assert best[(k, d)][1] == list(S_best)
    mix = pdb.cost_tables(504, 6)[0]
    d_star, S_star, value, _ = pdb.select_from_best(best, 6, mix)
    ratios = [best[(6, d)][0] / mix[d - 1] for d in range(1, 7)]
    assert d_star == int(np.argmax(ratios)) + 1 and S_star == best[(6, d_star)][1] and value == max(ratios)
    with pytest.raises(ValueError):
        pdb.exhaustive_cov(np.eye(21), np.eye(21), 21, chunk=10)


def test_g2_ids_and_subset_serialization():
    assert pdb.S_json([4, 0, 2]) == "[1,3,5]"
    assert pdb.parse_S("[1,3,5]", 6) == [1, 3, 5]
    for bad in ["[0,1]", "[1,1]", "[3,1]", "[7]", "[]", "x", "[1.5]"]:
        with pytest.raises(ValueError):
            pdb.parse_S(bad, 6)
    assert pdb.sha16({"b": 1, "a": [1, 2]}) == pdb.sha16({"a": [1, 2], "b": 1})
    assert len(pdb.sha16({"a": 1})) == 16
    assert pdb.sha16({"S": pdb.S_json([0, 1])}) != pdb.sha16({"S": pdb.S_json([0, 2])})


def test_g2_asset_permutation_equivariance():
    cfg = tiny_cfg()
    X = pdb.draw_path(cfg, "SYNTH_GAUSS_EQUICORR", "fit", 0, 80)
    perm = _rng(15).permutation(24)
    b1, b2 = pdb.fit_basis(X), pdb.fit_basis(np.ascontiguousarray(X[:, perm]))
    np.testing.assert_allclose(b1["eigval"], b2["eigval"], rtol=1e-10)
    np.testing.assert_allclose(b1["lambda_corr"], b2["lambda_corr"], rtol=1e-10, atol=1e-12)
    delta = _rng(16).standard_normal(24)
    q1 = pdb.q_plugin(b1["eigvec"][:, :6].T @ delta, b1["eigval"][:6])
    q2 = pdb.q_plugin(b2["eigvec"][:, :6].T @ delta[perm], b2["eigval"][:6])
    np.testing.assert_allclose(q1, q2, rtol=1e-8, atol=1e-14)


def _run(tmp, name, cfg=None, dataset="synthetic", **kw):
    out, log = tmp / name / "out", tmp / name / "log"
    return pdb.run_benchmark(cfg or tiny_cfg(), dataset, out, log, **kw), out, log


def _tables(out):
    return {f[:-4]: pd.read_csv(out / f, float_precision="round_trip") for f in OUTPUTS if f.endswith(".csv")}


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    code, out, _ = _run(tmp_path_factory.mktemp("tiny"), "a")
    assert code == 0
    return out, _tables(out), json.loads((out / "manifest.json").read_text())


def _fake_derived(tmp_path, N=21):
    dates = np.arange(np.datetime64("2004-12-31"), np.datetime64("2023-12-30"))
    dates = dates[np.is_busday(dates)]
    g = _rng(20)
    X = 0.01 * (0.7 * g.standard_normal((len(dates), N)) + 0.5 * g.standard_normal((len(dates), 1)))
    X[dates >= np.datetime64("2020-01-01")] = np.nan
    d = tmp_path / "derived" / "fake"
    d.mkdir(parents=True)
    np.save(d / "ret_wide.npy", np.asfortranarray(X))
    np.save(d / "dates.npy", dates)
    (d / "assets.json").write_text(json.dumps([f"A{i}" for i in range(N)]))
    segments = sp500._realize_segments(dates)
    (d / "splits.yaml").write_text(yaml.safe_dump({"dataset": "fake", "embargo_trading_days": 65,
                                                   "segments": segments}, sort_keys=False))
    outputs = [{"path": f"data/derived/fake/{n}", "sha256": pdb.file_sha256(d / n)}
               for n in ("ret_wide.npy", "dates.npy", "assets.json", "splits.yaml")]
    (tmp_path / "MANIFEST.json").write_text(json.dumps({"datasets": {"fake": {"outputs": outputs}}}))
    return d, dates, segments


def _fake_cfg(tmp_path, derived, dates, segments):
    cfg = tiny_cfg()
    cfg["mode"] = "full"
    calib = segment_rows(dates, segments["calib"])
    cfg["real"].update(derived_dir=str(derived), manifest=str(tmp_path / "MANIFEST.json"), dataset="fake", n_null=19,
                       expected_calib_rows=calib[1] - calib[0])
    return cfg


def test_g3_tables_have_exact_columns_and_closed_enums(tiny_run):
    _, t, manifest = tiny_run
    assert pdb.COLUMNS["trials"] == ["group_id", "role", "replicate", "first_hit", "censored_time", "detected",
                                     "stat_max", "pre_onset_alarm", "detected_during_event"]
    for name, df in t.items():
        assert list(df.columns) == pdb.COLUMNS[name], name
        for col, allowed in pdb.ENUMS.items():
            if col in df.columns:
                values = set(df[col].dropna().astype(str))
                assert values <= set(allowed), (name, col, values - set(allowed))
    flags = {f for v in t["selection"]["claim_flag"].dropna() for f in json.loads(v)}
    assert flags <= set(pdb.CLAIM_FLAGS)
    assert t["issues"]["issue_id"].is_unique and t["aggregates"]["metric_id"].is_unique
    assert t["calibration"]["null_calibration_id"].is_unique
    sel = t["selection"]
    known = sel["S"].notna()
    for text in sel.loc[known, "S"]:
        pdb.parse_S(text, 6)
    assert (sel.loc[known, "d"] == sel.loc[known, "S"].map(lambda s: len(json.loads(s)))).all()
    assert manifest["identity"]["schema_version"] == pdb.SCHEMA_VERSION == manifest["schema_version"]


def test_g3_prefix_and_mix_rows_reuse_the_same_metrics(tiny_run):
    _, t, _ = tiny_run
    sel, agg = t["selection"], t["aggregates"]
    syn = sel[sel["cohort_id"].isna()]
    cols = ["selection_id", "metric_id", "null_metric_id", "S", "d", "I_objective", "V_mix", "V_affine",
            "calibration_hash"]
    groups = 0
    for _, g in syn.groupby(["dataset_id", "event_id", "detector_family"]):
        pre = g[g["method"] == "BASELINE_PREFIX"]
        if pre.empty:
            continue
        groups += 1
        e1 = pre[pre["experiment"] == "E1"].sort_values("k")[cols].reset_index(drop=True)
        e2 = pre[pre["experiment"] == "E2"].sort_values("k")[cols].reset_index(drop=True)
        pd.testing.assert_frame_equal(e1, e2)
        assert e1["S"].tolist() == [pdb.S_json(range(k)) for k in range(1, 7)]
        for method in ("ORACLE_Q_MIX", "COV_JOINT_ORACLE"):
            chosen = g[(g["method"] == method) & (g["row_kind"] == "SELECTED")]
            for _, gg in chosen.groupby("objective_kind"):
                k_max = gg[(gg["experiment"] == "E2") & (gg["k"] == 6)][cols].reset_index(drop=True)
                pd.testing.assert_frame_equal(k_max, gg[gg["experiment"] == "E3"][cols].reset_index(drop=True))
    assert groups == 6
    assert set(syn["metric_id"].dropna()) <= set(agg["metric_id"])
    assert set(syn["null_metric_id"].dropna()) <= set(agg["metric_id"])
    alt = agg[agg["metric_kind"] == "ALT_RMST"]
    per_subset = alt.groupby(["dataset_id", "event_id", "detector_family", "S"], dropna=False)["metric_id"]
    assert per_subset.nunique().eq(1).all() and alt["metric_id"].nunique() == per_subset.ngroups


def test_g3_cpv90_outside_and_inside(tiny_run, tmp_path):
    _, t, _ = tiny_run
    sel = t["selection"]
    cpv = sel[(sel["method"] == "BASELINE_CPV90") & sel["cohort_id"].isna()]
    assert len(cpv) == 6 and (cpv["status"] == "CPV90_OUTSIDE_TOP20").all()
    assert cpv["S"].isna().all() and cpv["metric_id"].isna().all() and (cpv["cpv90_k_full"] > 6).all()
    assert (cpv["comparability"] == "NOT_COMPARABLE_OUTSIDE_TOP20").all()
    cfg = tiny_cfg(N=8, nmax=7)
    cfg["synthetic"]["rho"] = 0.9
    code, out, _ = _run(tmp_path, "inside", cfg)
    assert code == 0
    sel = _tables(out)["selection"]
    sel = sel[sel["cohort_id"].isna()]
    checked = 0
    for _, g in sel.groupby(["dataset_id", "event_id", "detector_family"]):
        row = g[g["method"] == "BASELINE_CPV90"]
        if row.empty:
            continue
        k90 = int(row["cpv90_k_full"].iloc[0])
        pre = g[(g["method"] == "BASELINE_PREFIX") & (g["k"] == k90) & (g["experiment"] == "E1")]
        assert k90 <= 7 and row["status"].iloc[0] == "OK"
        assert row["metric_id"].iloc[0] == pre["metric_id"].iloc[0] and row["S"].iloc[0] == pre["S"].iloc[0]
        checked += 1
    assert checked == 6


def test_g3_t7_information_is_labelled_proxy_and_thresholds_are_empirical(tiny_run):
    _, t, _ = tiny_run
    sel, cal, agg = t["selection"], t["calibration"], t["aggregates"]
    t7 = sel.loc[sel["dataset_id"] == "SYNTH_T7_EQUICORR", "info_kind"].dropna()
    assert len(t7) and t7.str.contains("T7_PROXY").all()
    assert not sel.loc[sel["dataset_id"] == "SYNTH_GAUSS_EQUICORR", "info_kind"].dropna().str.contains("T7").any()
    assert not cal["anytime_valid"].astype(bool).any()
    assert set(cal["null_validity"]) <= {"EMPIRICAL_QUASI_LIKELIHOOD", "EMPIRICAL_ENERGY",
                                         "APPROXIMATE_D6_INSAMPLE_OVERLAPPING"}
    assert not np.isclose(cal["threshold"], math.log(504)).any()
    assert not np.isclose(cal["threshold"], math.log(12 / 0.05)).any()
    assert set(cal["detector_family"]) == {"MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM", "COV_QUADRATIC_VECH_SCAN",
                                           "ENERGY_INCREASE_CUSUM"}
    kinds = agg.groupby("dataset_id")["metric_kind"].apply(set)
    assert "GAUSS_PROXY_CHECK_T7" in kinds["SYNTH_T7_EQUICORR"] and "GAUSS_FORMULA_CHECK" not in kinds["SYNTH_T7_EQUICORR"]
    assert "GAUSS_FORMULA_CHECK" in kinds["SYNTH_GAUSS_EQUICORR"]
    checks = agg[agg["metric_kind"].isin(["GAUSS_FORMULA_CHECK", "GAUSS_PROXY_CHECK_T7"])]
    assert len(checks) == 6 and np.isfinite(checks[["check_estimate", "check_se", "check_reference"]]).all().all()
    assert set(checks["check_space"]) == {"WHITENED_Z6"}


def test_g3_poisoned_test_roles_leave_fit_selection_and_centering_unchanged(monkeypatch):
    run = pdb.Run(tiny_cfg(), "test-fingerprint")
    ref = pdb.prepare_background(run, "SYNTH_T7_EQUICORR")
    draw = pdb.draw_path

    def poisoned(cfg, background, role, i, T):
        X = draw(cfg, background, role, i, T)
        return np.full_like(X, np.nan) if role in ("calibration", "holdout_null", "alternative") else X

    monkeypatch.setattr(pdb, "draw_path", poisoned)
    got = pdb.prepare_background(run, "SYNTH_T7_EQUICORR")
    assert got["basis"]["basis_hash"] == ref["basis"]["basis_hash"] and got["centering_hash"] == ref["centering_hash"]
    assert pdb.canon(got["specs"]) == pdb.canon(ref["specs"])

    def scaled_centering(cfg, background, role, i, T):
        X = draw(cfg, background, role, i, T)
        return 2.0 * X if role == "centering" else X

    monkeypatch.setattr(pdb, "draw_path", scaled_centering)
    moved = pdb.prepare_background(run, "SYNTH_T7_EQUICORR")
    assert moved["centering_hash"] != ref["centering_hash"]
    assert moved["basis"]["basis_hash"] == ref["basis"]["basis_hash"]
    assert pdb.canon(moved["specs"]) == pdb.canon(ref["specs"])


def test_g3_roles_never_share_paths_and_scenarios_share_the_alternative_base():
    cfg = tiny_cfg()
    owners = {}
    for role in pdb.SEED_ROLES:
        for i in range(4):
            owners.setdefault(pdb.array_sha256(pdb.draw_path(cfg, "SYNTH_GAUSS_EQUICORR", role, i, 12)), set()).add(role)
    assert all(len(v) == 1 for v in owners.values()) and len(owners) == 20
    run = pdb.Run(cfg, "test-fingerprint")
    prep = pdb.prepare_background(run, "SYNTH_GAUSS_EQUICORR")
    data = pdb.role_data(run, "SYNTH_GAUSS_EQUICORR", prep)
    W = prep["W"]
    za = data["alternative"]["A_market_mean"][0] - prep["scenarios"]["A_market_mean"]["delta"] @ W
    zc = data["alternative"]["C_residual_mean"][0] - prep["scenarios"]["C_residual_mean"]["delta"] @ W
    np.testing.assert_allclose(za, zc, atol=1e-12)
    base = np.stack([pdb.draw_path(cfg, "SYNTH_GAUSS_EQUICORR", "alternative", i, 12) for i in range(cfg["n_alt"])])
    np.testing.assert_allclose(data["alternative"]["B_cov_rotate30"][0], base @ prep["M"].T @ W, atol=1e-12)


def test_g3_aggregates_follow_from_trials(tiny_run):
    _, t, _ = tiny_run
    agg = t["aggregates"].set_index("metric_id")
    cal = t["calibration"].set_index("null_calibration_id")
    tr = t["trials"]
    assert set(tr["role"]) == {"calibration", "holdout_null", "alternative"}
    for mid, g in tr[tr["role"] == "alternative"].groupby("group_id"):
        row = agg.loc[mid]
        assert row["metric_kind"] == "ALT_RMST" and row["n"] == len(g) == 8
        assert (g["censored_time"] == np.where(g["first_hit"] > 0, g["first_hit"], 12)).all()
        assert row["rmst"] == pytest.approx(g["censored_time"].mean(), rel=1e-14)
        assert row["det_rate"] == pytest.approx(g["detected"].mean(), rel=1e-14)
        assert row["det_rate"] + row["censored_share"] == pytest.approx(1.0, abs=1e-15)
    for mid, g in tr[tr["role"] == "holdout_null"].groupby("group_id"):
        assert agg.loc[mid, "metric_kind"] == "HOLDOUT_NULL_FPR"
        assert agg.loc[mid, "fpr"] == pytest.approx(g["detected"].mean(), rel=1e-14)
        assert agg.loc[mid, "alarms"] == g["detected"].sum()
    for cid, g in tr[tr["role"] == "calibration"].groupby("group_id"):
        row = cal.loc[cid]
        assert row["calibration_alarms"] == g["detected"].sum() <= row["rank_r"]
        assert row["maxima_sha256"] == pdb.array_sha256(g.sort_values("replicate")["stat_max"].to_numpy())


def test_g3_two_fresh_directories_are_byte_identical_and_the_seed_matters(tiny_run, tmp_path):
    out_a = tiny_run[0]
    code, out_b, _ = _run(tmp_path, "b")
    assert code == 0
    for f in OUTPUTS:
        assert (out_a / f).read_bytes() == (out_b / f).read_bytes(), f
    code, out_c, _ = _run(tmp_path, "c", tiny_cfg(seed=7))
    assert code == 0
    a, c = _tables(out_a)["aggregates"], _tables(out_c)["aggregates"]
    assert not np.array_equal(a["rmst"].dropna().to_numpy(), c["rmst"].dropna().to_numpy())


def test_g3_refuses_to_overwrite_outputs(tiny_run, tmp_path):
    out = tiny_run[0]
    before = {f: (out / f).read_bytes() for f in OUTPUTS}
    for resume in (False, True):
        with pytest.raises(pdb.OutputExists):
            pdb.run_benchmark(tiny_cfg(), "synthetic", out, tmp_path / f"log{resume}", resume=resume)
    assert before == {f: (out / f).read_bytes() for f in OUTPUTS}
    (tmp_path / "busy").mkdir()
    (tmp_path / "busy" / "x.txt").write_text("1")
    with pytest.raises(pdb.OutputExists):
        pdb.run_benchmark(tiny_cfg(), "synthetic", tmp_path / "busy", tmp_path / "logbusy")


def test_g3_blocked_resource_then_resume_is_byte_identical(tiny_run, tmp_path):
    ticks = itertools.count()
    early = tiny_cfg(resources={"mem_limit_gib": 8.0, "max_wall_minutes": 0.1})
    assert pdb.run_benchmark(early, "synthetic", tmp_path / "o3", tmp_path / "l3", clock=lambda: float(next(ticks))) == 3
    report = json.loads((tmp_path / "l3" / "blocked_resource.json").read_text())
    assert "covariance search d=" in report["reason"] and report["partitions"] == 0
    ticks = itertools.count()
    cfg = tiny_cfg(resources={"mem_limit_gib": 8.0, "max_wall_minutes": 1.0})
    out, log = tmp_path / "out", tmp_path / "log"
    assert pdb.run_benchmark(cfg, "synthetic", out, log, clock=lambda: float(next(ticks))) == 3
    assert not (out / "manifest.json").exists() and (log / "blocked_resource.json").exists()
    assert json.loads((log / "blocked_resource.json").read_text())["status"] == "BLOCKED_RESOURCE"
    assert 0 < len(list((log / "partitions").glob("*.json")))
    with pytest.raises(pdb.OutputExists):
        pdb.run_benchmark(tiny_cfg(), "synthetic", out, log)
    assert pdb.run_benchmark(tiny_cfg(), "synthetic", out, log, resume=True) == 0
    for f in OUTPUTS:
        assert (out / f).read_bytes() == (tiny_run[0] / f).read_bytes(), f
    ticks = itertools.count()
    out2, log2 = tmp_path / "out2", tmp_path / "log2"
    assert pdb.run_benchmark(cfg, "synthetic", out2, log2, clock=lambda: float(next(ticks))) == 3
    meta = sorted((log2 / "partitions").glob("*.json"))[0]
    record = json.loads(meta.read_text())
    record["fingerprint"] = "0" * 64
    meta.write_text(json.dumps(record))
    with pytest.raises(pdb.PartitionMismatch):
        pdb.run_benchmark(tiny_cfg(), "synthetic", out2, log2, resume=True)


def test_g3_smoke_is_synthetic_only_and_never_reads_real_returns(tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as exc:
        pdb.main(["--mode", "smoke", "--dataset", "real", "--out", str(tmp_path / "o"), "--log-dir", str(tmp_path / "l")])
    assert exc.value.code == 2
    with pytest.raises(ValueError):
        pdb.run_benchmark(tiny_cfg(), "both", tmp_path / "o2", tmp_path / "l2")

    def refuse(*args, **kwargs):
        raise AssertionError("real returns read in smoke mode")

    monkeypatch.setattr(pdb, "read_pre2020_panel", refuse)
    assert _run(tmp_path, "smoke")[0] == 0


def test_g3_check_env_refuses_non_conforming_environment(tmp_path):
    for var, value in (("PYTHONHASHSEED", "0"), ("OMP_NUM_THREADS", "4"), ("MKL_CBWR", "AUTO")):
        env = dict(os.environ, **{var: value})
        cmd = [sys.executable, str(REPO / "experiments" / "pca_drift_benchmark.py"), "--mode", "smoke",
               "--out", str(tmp_path / var), "--log-dir", str(tmp_path / f"{var}_log")]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        assert res.returncode == 2 and var in res.stderr
        assert not (tmp_path / var).exists()


def test_g3_real_cohorts_are_present_blocked_and_disjoint(tiny_run):
    _, t, manifest = tiny_run
    agg = t["aggregates"]
    real = agg[agg["cohort_id"].notna()]
    assert set(real["cohort_id"]) == {"cohort_standard_embargo", "cohort_retrospective_covid"}
    std = real[real["cohort_id"] == "cohort_standard_embargo"]
    retro = real[real["cohort_id"] == "cohort_retrospective_covid"]
    covid = std[std["event_id"] == "COVID_2020"]
    assert len(covid) and (covid["status"] == "NOT_EVALUABLE_STANDARD_SPLIT").all()
    assert (real.drop(covid.index)["status"] == "BLOCKED_PRE_J4").all()
    assert (real["execution"] == "NOT_EXECUTED").all()
    for col in ("rmst", "fpr", "n", "time_to_alarm_during_event", "post_onset_delay_h250"):
        assert real[col].isna().all()
    assert not set(std["metric_id"]) & set(retro["metric_id"])
    assert real.groupby("cohort_id")["split_hash"].nunique().eq(1).all() and real["split_hash"].nunique() == 2
    assert (retro["claim_scope"] == "REAL_RETROSPECTIVE_EXPLORATORY").all()
    assert (retro["time_origin"] == "CONTINUOUS_RESTART_AFTER_ALARM").all()
    assert (std["claim_scope"] == "REAL_STANDARD_SPLIT").all()
    assert set(retro["onset_date"]) == {"2020-02-24"} and set(retro["event_end_date"]) == {"2020-03-23"}
    assert set(std.loc[std["event_id"] == "STYLE_2022H1", "time_origin"]) == {"ONSET_ALIGNED"}
    sel = t["selection"]
    flags = sel.loc[sel["event_id"] == "STYLE_2022H1", "claim_flag"].map(json.loads)
    assert flags.map(lambda f: "RETROSPECTIVE_DIAGNOSTIC" in f).all()
    oracle = sel[sel["method"].isin(["ORACLE_Q_MIX", "ORACLE_Q_AFFINE"]) & sel["cohort_id"].notna()]
    assert oracle["claim_flag"].map(lambda v: "EX_POST_ORACLE" in json.loads(v)).all()
    assert {"BLOCKED_PRE_J4", "NOT_EVALUABLE_STANDARD_SPLIT", "RETROSPECTIVE_DEVIATION"} <= set(t["issues"]["code"])
    assert manifest["pre_j4"]["frozen_json_present"] is False


def test_g3_pre2020_reader_indexes_only_pre2020_rows(tmp_path):
    derived, dates, segments = _fake_derived(tmp_path)
    cfg = _fake_cfg(tmp_path, derived, dates, segments)
    recorded = []

    class Recorder(np.ndarray):
        def __getitem__(self, key):
            recorded.append(key)
            return super().__getitem__(key)

    def loader(path, mmap_mode=None):
        a = np.load(path, mmap_mode=mmap_mode)
        return a.view(Recorder) if Path(path).name == "ret_wide.npy" else a

    expected = pdb.manifest_hashes(cfg)
    panel = pdb.read_pre2020_panel(cfg, expected, load=loader)
    first_2020 = int(np.searchsorted(dates, np.datetime64("2020-01-01")))
    assert recorded and all(isinstance(k, slice) and k.stop <= first_2020 for k in recorded)
    assert np.isfinite(panel["X"]).all() and panel["X"].flags["C_CONTIGUOUS"]
    assert panel["days"].min() == np.datetime64("2005-01-04") and panel["days"].max() <= np.datetime64("2019-12-31")
    with pytest.raises(pdb.DataUnavailable):
        pdb.read_pre2020_panel(cfg, dict(expected, **{"ret_wide.npy": "0" * 64}))
    with pytest.raises(pdb.PreJ4Refused):
        pdb.check_pre_j4(np.array(["2019-12-31", "2020-01-02"], dtype="datetime64[D]"))


def test_g3_real_pre2020_pipeline_on_a_fake_dated_panel(tmp_path):
    derived, dates, segments = _fake_derived(tmp_path)
    cfg = _fake_cfg(tmp_path, derived, dates, segments)
    code, out, _ = _run(tmp_path, "real", cfg, dataset="both")
    assert code == 0
    t = _tables(out)
    manifest = json.loads((out / "manifest.json").read_text())
    real_cal = t["calibration"][t["calibration"]["dataset_id"] == "D3_239"]
    assert len(real_cal) and np.isfinite(real_cal["threshold"]).all()
    assert set(real_cal["null_kind"]) == {"REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS"}
    assert set(real_cal["null_validity"]) == {"APPROXIMATE_D6_INSAMPLE_OVERLAPPING"}
    ids = real_cal.groupby("cohort_id")["null_calibration_id"].apply(set)
    assert len(ids) == 2 and not ids.iloc[0] & ids.iloc[1]
    spec = t["spectra"][t["spectra"]["dataset_id"] == "D3_239"]
    assert len(spec) == 21 and spec["fit_last_day"].max() <= "2019-12-31"
    sel = t["selection"]
    ex = sel[(sel["method"] == "EXANTE_QBAR") & (sel["row_kind"] == "SELECTED") & (sel["dataset_id"] == "D3_239")]
    assert len(ex) == 3 and ex["S"].notna().all()
    real = t["aggregates"][t["aggregates"]["cohort_id"].notna()]
    assert real["status"].isin(["BLOCKED_PRE_J4", "NOT_EVALUABLE_STANDARD_SPLIT"]).all() and real["rmst"].isna().all()
    first_2020 = int(np.searchsorted(dates, np.datetime64("2020-01-01")))
    assert manifest["real"]["rows_indexed"][1] <= first_2020
    panel = pdb.read_pre2020_panel(cfg, pdb.manifest_hashes(cfg))
    a, b = segment_rows(panel["days"], segments["calib"])
    basis = pdb.fit_basis(np.ascontiguousarray(panel["X"][a:b]))
    rbar = panel["X"][a:b].mean(axis=0)
    qs = []
    for lo, hi in cfg["real"]["stress_windows"].values():
        rows = (panel["days"] >= np.datetime64(lo)) & (panel["days"] <= np.datetime64(hi))
        qs.append(pdb.q_plugin((basis["eigvec"].T @ (panel["X"][rows].mean(axis=0) - rbar))[:6], basis["eigval"][:6]))
    np.testing.assert_allclose(manifest["real"]["stress_library"]["qbar"], np.mean(qs, axis=0), rtol=1e-12)


def test_g3_stress_window_with_missing_rows_gives_no_exante_result():
    days = np.arange(np.datetime64("2008-09-01"), np.datetime64("2008-12-31"))
    X = _rng(21).standard_normal((len(days), 5))
    basis = pdb.fit_basis(X)
    windows = {"S2008": ["2008-09-15", "2008-11-20"]}
    q, info = pdb.stress_library(X, days, windows, X.mean(axis=0), basis, 3)
    assert q.shape == (3,) and info["S2008"]["rows"] == int(((days >= np.datetime64("2008-09-15"))
                                                             & (days <= np.datetime64("2008-11-20"))).sum())
    X[20, 2] = np.nan
    with pytest.raises(pdb.IncompleteWindow):
        pdb.stress_library(X, days, windows, np.zeros(5), basis, 3)
    with pytest.raises(pdb.IncompleteWindow):
        pdb.stress_library(X, days, {"S2020": ["2020-02-24", "2020-03-23"]}, np.zeros(5), basis, 3)


def test_g3_cohort_definitions_follow_splits_and_calendar(tmp_path):
    _, dates, segments = _fake_derived(tmp_path)
    splits = {"segments": segments}
    cfg = pdb.load_config(CONFIG, "smoke")
    defs = pdb.cohort_definitions(cfg, splits, dates)
    std, retro = defs["cohort_standard_embargo"], defs["cohort_retrospective_covid"]
    assert std["monitor_armed_from"] == str(segments["monitor"]["first_day"])
    assert std["events"]["COVID_2020"]["status"] == "NOT_EVALUABLE_STANDARD_SPLIT"
    assert std["events"]["STYLE_2022H1"]["status"] == "BLOCKED_PRE_J4"
    assert retro["events"]["COVID_2020"]["status"] == "BLOCKED_PRE_J4"
    assert retro["monitor_armed_from"] == str(dates[dates >= np.datetime64("2020-01-01")][0])
    assert std["embargo_after_2019"] == 65 and retro["embargo_after_2019"] == 0
    assert std["split_hash"] != retro["split_hash"]
    assert pdb.cohort_definitions(cfg, splits, None)["cohort_retrospective_covid"]["monitor_armed_from"] is None


def test_g3_retrospective_rules_r1_to_r5():
    dates = np.arange(np.datetime64("2020-01-01"), np.datetime64("2021-06-30"))
    dates = dates[np.is_busday(dates)]
    oi = int(np.searchsorted(dates, np.datetime64("2020-02-24")))
    ei = int(np.searchsorted(dates, np.datetime64("2020-03-23"), side="right")) - 1
    args = (0.3, 3.0, "2020-02-24", "2020-03-23", 250, "CONTINUOUS_RESTART_AFTER_ALARM", "FAKE_DATED_TEST")
    z = np.zeros((len(dates), 1))
    z[5] = z[oi + 3] = 6.0
    r = pdb.evaluate_real_path(z, dates, *args)
    assert r["pre_onset_alarms"] == 1 and json.loads(r["pre_onset_alarm_dates"]) == [str(dates[5])]
    assert json.loads(r["alarm_dates"]) == [str(dates[5]), str(dates[oi + 3])]
    assert r["detected_during_event"] and not r["event_censored"] and r["time_to_alarm_during_event"] == 4
    assert r["post_onset_delay_h250"] == 4 and not r["post_event_alarm"] and r["status"] == "OK"
    z = np.zeros((len(dates), 1))
    z[ei + 5] = 6.0
    r = pdb.evaluate_real_path(z, dates, *args)
    assert not r["detected_during_event"] and r["event_censored"]
    assert r["time_to_alarm_during_event"] == r["n_event_sessions"] == ei - oi + 1
    assert r["post_onset_delay_h250"] == ei + 5 - oi + 1 and r["post_event_alarm"]
    r = pdb.evaluate_real_path(np.zeros((len(dates), 1)), dates, *args)
    assert r["pre_onset_alarms"] == 0 and r["post_onset_delay_h250"] == 250 and not r["post_event_alarm"]
    short = dates[:oi + 40]
    r = pdb.evaluate_real_path(np.zeros((len(short), 1)), short, *args)
    assert r["status"] == "PATH_TOO_SHORT" and not r["path_supports_H"] and math.isnan(r["post_onset_delay_h250"])
    with pytest.raises(pdb.PreJ4Refused):
        pdb.evaluate_real_path(z, dates, *args[:-1], "REAL_RETROSPECTIVE")


def test_g3_missing_real_inputs_mark_real_rows_unavailable(tmp_path):
    cfg = tiny_cfg()
    cfg["real"]["derived_dir"] = str(tmp_path / "missing")
    code, out, _ = _run(tmp_path, "missing", cfg)
    assert code == 0
    t = _tables(out)
    real = t["aggregates"][t["aggregates"]["cohort_id"].notna()]
    assert len(real) and (real["status"] == "DATA_UNAVAILABLE").all()
    assert "DATA_UNAVAILABLE" in set(t["issues"]["code"])
    assert (t["aggregates"].loc[t["aggregates"]["cohort_id"].isna(), "status"] == "OK").all()


def _none(v):
    return None if isinstance(v, float) and math.isnan(v) else v


def test_p0_calibration_rows_separate_rate_bound_and_holdout_fpr(tiny_run):
    _, t, manifest = tiny_run
    cal, agg = t["calibration"], t["aggregates"]
    assert manifest["schema_version"] == pdb.SCHEMA_VERSION == "pca_drift_benchmark/2"
    assert set(cal["threshold_rule"]) == {"predictive_exchangeable_rank_v2"}
    syn = cal[cal["null_kind"] == "SYNTH_INDEPENDENT_PATHS"]
    assert len(syn) and (syn["status"] == "OK").all() and (syn["n_cal"] == 19).all() and (syn["rank_r"] == 0).all()
    assert set(syn["guarantee_basis"]) == {"EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA"}
    np.testing.assert_array_equal(syn["predictive_bound"], (syn["rank_r"] + 1) / (syn["n_cal"] + 1))
    assert (syn["predictive_bound"] <= syn["alpha"]).all()
    np.testing.assert_array_equal(syn["calibration_fraction"], syn["calibration_alarms"] / syn["n_cal"])
    hold = agg[agg["metric_kind"] == "HOLDOUT_NULL_FPR"]
    assert len(hold) and (hold["n"] == 8).all() and (hold["target_fpr"] == 0.05).all()
    np.testing.assert_array_equal(hold["fpr"], hold["alarms"] / hold["n"])
    for _, row in syn.iterrows():
        p = _none(row["p"])
        params = {"p": None if p is None else int(p), "s2": _none(row["s2"]), "delta": _none(row["cusum_delta"]),
                  "alarm_rule": row["alarm_rule"]}
        assert row["null_calibration_id"] == pdb.sha16({
            "null_id": row["null_id"], "family": row["detector_family"], "params": params,
            "centering_hash": _none(row["centering_hash"]), "basis_hash": row["basis_hash"], "S": _none(row["S"]),
            "alpha": row["alpha"], "rule": "predictive_exchangeable_rank_v2"})
    block = manifest["calibration"]
    assert block["threshold_rule"] == "predictive_exchangeable_rank_v2" and block["anytime_valid"] is False
    assert block["guarantee_basis"] == {"SYNTH_INDEPENDENT_PATHS": "EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA",
                                        "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS": "NOT_ESTABLISHED_HISTORICAL_WINDOWS"}
    assert block["min_n_cal"] == 19 and block["configured"]["n_cal"] == {"n": 19, "rank_r": 0, "predictive_bound": 0.05}


def test_p0_guarantee_is_absent_for_historical_windows_and_the_real_path(tmp_path):
    derived, dates, segments = _fake_derived(tmp_path)
    cfg = _fake_cfg(tmp_path, derived, dates, segments)
    code, out, _ = _run(tmp_path, "real", cfg, dataset="both")
    assert code == 0
    t = _tables(out)
    real = t["calibration"][t["calibration"]["null_kind"] == "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS"]
    assert len(real) and (real["status"] == "OK").all() and np.isfinite(real["threshold"]).all()
    assert set(real["guarantee_basis"]) == {"NOT_ESTABLISHED_HISTORICAL_WINDOWS"} and real["predictive_bound"].isna().all()
    assert set(real["threshold_rule"]) == {"predictive_exchangeable_rank_v2"} and (real["rank_r"] == 0).all()
    path = t["aggregates"][t["aggregates"]["metric_kind"] == "REAL_EVENT_PATH"]
    assert len(path) and path[["fpr", "fpr_lo", "fpr_hi", "target_fpr", "n"]].isna().all().all()
    block = json.loads((out / "manifest.json").read_text())["calibration"]
    assert block["configured"]["real_n_null"] == {"n": 19, "rank_r": 0, "predictive_bound": None}


def test_p0_insufficient_calibration_marks_rows_failed_without_threshold(tmp_path):
    code, out, _ = _run(tmp_path, "small", tiny_cfg(n_cal=8))
    assert code == 0
    t = _tables(out)
    cal, agg, tr, sel = t["calibration"], t["aggregates"], t["trials"], t["selection"]
    assert len(cal) and (cal["status"] == "CALIBRATION_FAILED").all() and (cal["n_cal"] == 8).all()
    assert cal[["threshold", "predictive_bound", "rank_r", "calibration_alarms", "calibration_fraction",
                "calibration_hash"]].isna().all().all()
    assert cal["maxima_sha256"].notna().all() and set(cal["threshold_rule"]) == {"predictive_exchangeable_rank_v2"}
    syn = agg[agg["metric_kind"].isin(["HOLDOUT_NULL_FPR", "ALT_RMST"])]
    assert len(syn) and (syn["status"] == "CALIBRATION_FAILED").all() and (syn["execution"] == "NOT_EXECUTED").all()
    assert syn[["n", "alarms", "fpr", "rmst", "det_rate"]].isna().all().all()
    assert tr.empty
    evaluated = sel[sel["metric_id"].notna() & sel["cohort_id"].isna()]
    assert len(evaluated) and (evaluated["status"] == "CALIBRATION_FAILED").all()
    assert (evaluated["execution"] == "NOT_EXECUTED").all()
    issue = t["issues"][t["issues"]["code"] == "CALIBRATION_FAILED"]
    assert len(issue) == 2 and (issue["severity"] == "BLOCKER").all()
    assert issue["message"].str.contains("n = 8 ").all() and issue["message"].str.contains("at least 19").all()
    block = json.loads((out / "manifest.json").read_text())["calibration"]
    assert block["configured"]["n_cal"] == {"n": 8, "rank_r": None, "predictive_bound": None}


def test_p1_mixture_cost_brackets_dynamically_and_fails_explicitly(monkeypatch):
    for bad in [(1, math.inf), (1, math.nan), (1, -math.inf), (2 ** 53, 504), (-1, 504)]:
        with pytest.raises(ValueError):
            pdb.mixture_cost(*bad)
    assert pdb.mixture_cost(500, 504) == pytest.approx(floors.mixture_multiplier(500, 504), rel=1e-10)
    big = pdb.mixture_cost(2 ** 40, 504)
    assert math.isfinite(big) and big > pdb.mixture_cost(500, 504)
    monkeypatch.setattr(pdb, "MIXTURE_MAX_DOUBLINGS", 0)
    assert pdb.mixture_cost(1, 504) == pytest.approx(floors.mixture_multiplier(1, 504), rel=1e-10)
    with pytest.raises(ArithmeticError, match="no finite bracket"):
        pdb.mixture_cost(500, 504)


def test_p1_stream_dimensions_are_inferred_and_checked(monkeypatch):
    Z = _rng(30).standard_normal((2, 6, 3))
    Y = pdb.vech_stream(Z, np.eye(3))
    assert Y.shape == (2, 6, 6)
    W, _ = pdb.scan_statistic(Y, 0.1)
    np.testing.assert_allclose(W[1], np.nanmax(_slow_loglik(Y[1], 0.1), axis=1), rtol=1e-12, atol=1e-12)
    for bad in (np.eye(2), np.eye(4), np.ones((3, 2))):
        with pytest.raises(ValueError):
            pdb.vech_stream(Z, bad)
    run = pdb.Run(tiny_cfg(), "test-fingerprint")
    assert pdb._scan(run, [Y], 0.1, None, 6)[0].shape == (2, 6)
    with pytest.raises(ValueError, match="dimension"):
        pdb._scan(run, [Y], 0.1, None, 5)
    monkeypatch.setattr(pdb, "vech_std", lambda A: np.zeros(A.shape[:-2] + (5,)))
    with pytest.raises(ArithmeticError):
        pdb.vech_stream(Z, np.eye(3))


def test_p1_exhaustive_search_batches_checks_and_reuse(monkeypatch):
    g = _rng(31)
    A, B = g.standard_normal((6, 6)), g.standard_normal((6, 6))
    C0, C1 = A @ A.T + 6.0 * np.eye(6), B @ B.T + 6.0 * np.eye(6)
    ref, _ = pdb.exhaustive_cov(C0, C1, 6, 20000)
    for chunk in (1, 2, 7, 20, 64):
        assert pdb.exhaustive_cov(C0, C1, 6, chunk)[0] == ref
    for chunk in (0, 20001, 2.5):
        with pytest.raises(ValueError):
            pdb.exhaustive_cov(C0, C1, 6, chunk)
    shapes = []
    raw = pdb.kl_cov_raw

    def counting(A0, A1):
        shapes.append(A0.shape)
        return raw(A0, A1)

    monkeypatch.setattr(pdb, "kl_cov_raw", counting)
    pdb.exhaustive_cov(C0, C1, 6, 7)
    assert sum(s[0] for s in shapes) == 2 ** 6 - 1 and max(s[0] for s in shapes) == 7
    shapes.clear()
    mem = 3 * pdb.cov_batch_bytes(6)
    assert pdb.exhaustive_cov(C0, C1, 6, 20000, mem_bytes=mem)[0] == ref
    assert sum(s[0] for s in shapes) == 63 and all(s[0] <= mem // pdb.cov_batch_bytes(s[1]) for s in shapes)
    with pytest.raises(pdb.ResourceBlocked):
        pdb.exhaustive_cov(C0, C1, 6, 20000, mem_bytes=pdb.cov_batch_bytes(1) - 1)
    seen = []
    pdb.exhaustive_cov(C0, C1, 6, 2, check=seen.append)
    assert len(seen) == sum(-(-math.comb(6, d) // 2) for d in range(1, 7)) == 33
    stops = []

    def stop_at_five(stage):
        stops.append(stage)
        if len(stops) == 5:
            raise pdb.ResourceBlocked("stop between batches")

    with pytest.raises(pdb.ResourceBlocked):
        pdb.exhaustive_cov(C0, C1, 6, 2, check=stop_at_five)
    assert len(stops) == 5 and "d=2" in stops[3] and "d=2" in stops[4]
    store = pdb.Store(Path("unused"), "fp", deadline=-1.0, clock=lambda: 0.0, mem_limit=8 * 2 ** 30)
    with pytest.raises(pdb.ResourceBlocked, match="wall-clock"):
        store.check("covariance search")
    monkeypatch.setattr(pdb, "peak_rss_bytes", lambda: 9 * 2 ** 30)
    with pytest.raises(pdb.ResourceBlocked, match="RSS"):
        pdb.Store(Path("unused"), "fp", deadline=1e9, clock=lambda: 0.0, mem_limit=8 * 2 ** 30).check("batch")


def test_p1_exhaustive_cov_floating_memory_budget(monkeypatch):
    C0 = np.eye(6)
    C1 = np.diag(np.arange(1.0, 7.0))
    ref, _ = pdb.exhaustive_cov(C0, C1, 6, 20000)
    for k in range(1, 7):
        for d in range(1, k + 1):
            assert ref[(k, d)][1] == list(range(k - d, k))
            assert ref[(k, d)][0] == pytest.approx(
                sum(0.5 * (r - 1.0 - math.log(r)) for r in range(k - d + 1, k + 1)), rel=1e-12)
    mem = 3.0 * pdb.cov_batch_bytes(6)
    assert mem == 5184.0
    shapes, seen = [], []
    raw = pdb.kl_cov_raw

    def counting(A0, A1):
        shapes.append(A0.shape)
        return raw(A0, A1)

    monkeypatch.setattr(pdb, "kl_cov_raw", counting)
    best, _ = pdb.exhaustive_cov(C0, C1, 6, 20000, check=seen.append, mem_bytes=mem)
    assert best == ref
    assert sum(s[0] for s in shapes) == 63
    assert all(s[0] <= math.floor(mem / pdb.cov_batch_bytes(s[1])) for s in shapes)
    assert len(seen) == len(shapes)
    shapes.clear()
    with pytest.raises(pdb.ResourceBlocked):
        pdb.exhaustive_cov(C0, C1, 6, 20000, mem_bytes=pdb.cov_batch_bytes(1) - 0.5)
    assert not shapes
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            pdb.exhaustive_cov(C0, C1, 6, 20000, mem_bytes=bad)
    rss = 2.5 * 2 ** 30
    monkeypatch.setattr(pdb, "peak_rss_bytes", lambda: rss)
    store = pdb.Store(Path("unused"), "fp", deadline=1e18, clock=lambda: 0.0, mem_limit=rss + mem)
    run = pdb.Run(tiny_cfg(), "fp", store)
    avail = run.available_bytes()
    assert isinstance(avail, float) and avail == 5184.0
    best, _ = pdb.exhaustive_cov(C0, C1, 6, 20000, run.check, avail)
    assert best == ref


def test_p1_seed_plan_covers_executed_roles_and_refuses_collisions(monkeypatch, tmp_path):
    cfg = tiny_cfg()
    plan = pdb.seed_plan(cfg, real=False)
    assert plan["n_keys"] == len(plan["keys"]) == 2 * (1 + 6 + 19 + 8 + 8 + 1)
    assert len(set(plan["keys"])) == plan["n_keys"]
    assert set(plan["vocabulary"]) >= {"path", "inject", "B", "SYNTH_GAUSS_EQUICORR", *pdb.SEED_ROLES}
    assert len(set(plan["vocabulary"].values())) == len(plan["vocabulary"])
    assert pdb.seed_plan(cfg, real=True)["n_keys"] == plan["n_keys"] + 2
    used = []
    real_rng = pdb.rng

    def recording(root, *parts):
        used.append((root, *parts))
        return real_rng(root, *parts)

    monkeypatch.setattr(pdb, "rng", recording)
    assert _run(tmp_path, "rng")[0] == 0
    assert len(used) == len(set(used)) and set(used) == {(cfg["seed"], *k) for k in plan["keys"]}
    a, b = np.random.SeedSequence([28, 42, 7]), np.random.SeedSequence([28, 42, 7, 0])
    assert np.array_equal(a.generate_state(4), b.generate_state(4))
    assert pdb.entropy_words([28, 42, 7]) == pdb.entropy_words([28, 42, 7, 0])
    with pytest.raises(ValueError, match="entropy collision"):
        pdb.check_entropies([[28, 42, 7], [28, 42, 7, 0]])
    clash = tiny_cfg()
    clash["synthetic"]["backgrounds"] = {"plumless": None, "buckeroo": 7}
    with pytest.raises(ValueError, match="CRC32 collision"):
        pdb.seed_plan(clash, real=False)
    drawn = []
    monkeypatch.setattr(pdb, "draw_path", lambda *args: drawn.append(args))
    with pytest.raises(ValueError, match="CRC32 collision"):
        pdb.run_benchmark(clash, "synthetic", tmp_path / "clash_out", tmp_path / "clash_log")
    assert not drawn and not (tmp_path / "clash_out").exists()
    for seed in (-1, 2 ** 32, 1.5, True):
        with pytest.raises(ValueError):
            pdb.validate_config(tiny_cfg(seed=seed))


def test_g2_schema_version_is_two_in_config_manifest_and_csvs(tiny_run):
    for mode in ("smoke", "full"):
        assert pdb.load_config(CONFIG, mode)["schema_version"] == pdb.SCHEMA_VERSION == "pca_drift_benchmark/2"
    for res in ({"mem_limit_gib": float("inf"), "max_wall_minutes": 30.0},
                {"mem_limit_gib": 8.0, "max_wall_minutes": float("nan")}):
        with pytest.raises(ValueError):
            pdb.validate_config(tiny_cfg(resources=res))
    cfg = tiny_cfg()
    cfg["schema_version"] = "pca_drift_benchmark/1"
    with pytest.raises(ValueError, match="schema_version"):
        pdb.validate_config(cfg)
    _, t, manifest = tiny_run
    assert manifest["schema_version"] == pdb.SCHEMA_VERSION
    assert manifest["identity"]["schema_version"] == pdb.SCHEMA_VERSION
    assert manifest["config"]["schema_version"] == pdb.SCHEMA_VERSION
    for name, df in t.items():
        if "schema_version" in df.columns:
            assert (df["schema_version"] == pdb.SCHEMA_VERSION).all(), name
