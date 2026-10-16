"""Contract tests for jepadrift.floors (pytest)."""
import math

import numpy as np

from jepadrift import floors as fl


def test_phi_limits():
    for g in (50.0, 500.0, 5000.0):
        assert abs(fl.phi(g) - (math.log(g) - 1.0)) < 2.5 * (math.log(g) + 2) / g
    for g in (1e-4, 1e-3):
        assert abs(fl.phi(g) - (g - (2 * g) ** 1.5 / 3)) < 5 * g ** 2


def test_first_order_overstates_exact():
    info = fl.kl_from_sharpe(1.0)
    for gamma in (20, 252, 1000):
        exact = fl.cusum_exact(gamma, math.sqrt(2 * info))["add"]
        assert exact < fl.first_order_floor(gamma, info)


def test_mixture_multiplier_table():
    # values reported in the theoretical note of 11 Oct 2026 (ARL0 = 504)
    for dim, ref in ((1, 1.22), (10, 2.01), (64, 3.91), (500, 9.64)):
        assert abs(fl.mixture_multiplier(dim, 504) - ref) < 0.01


def test_factor_identity_matches_direct_inverse():
    rng = np.random.default_rng(0)
    n, k = 60, 3
    B = rng.normal(size=(n, k))
    sigma_f = np.diag([0.5, 0.2, 0.1])
    psi = rng.uniform(0.5, 1.5, size=n)
    dl, da = rng.normal(size=k), rng.normal(size=n)
    sigma = B @ sigma_f @ B.T + np.diag(psi)
    dmu = B @ dl + da
    direct = dmu @ np.linalg.solve(sigma, dmu)
    f_term, b_term = fl.factor_information(B, sigma_f, psi, dl, da)
    assert abs(direct - (f_term + b_term)) < 1e-8 * direct


def test_one_factor_keff():
    n, rho = 239, 0.40
    B = np.ones((n, 1))
    f_term, b_term = fl.factor_information(B, [[rho]], np.full(n, 1 - rho), np.array([1.0]), np.zeros(n))
    assert abs(f_term - n / (1 + (n - 1) * rho)) < 1e-9 and b_term < 1e-12


def test_absorption_threshold():
    assert math.isinf(fl.absorption_delay(100.0, 200.0))
    assert abs(fl.absorption_delay(100.0, 250.0) / 100.0 - 2.012) < 1e-3
