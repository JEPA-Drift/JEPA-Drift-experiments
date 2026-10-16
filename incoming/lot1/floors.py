"""Analytic delay floors for sequential drift detection (Article C, Section 3).

Units: one observation per trading day. ``info`` is the per-observation
Kullback-Leibler divergence I between post- and pre-change laws (nats).
``gamma`` is either an in-control average run length (ARL0) or an anytime-valid
threshold on the e-value scale; the docstring of each function states which.

Three readings of the same budget (Proposition 2):
  * evidence budget, exact: any e-process started at the onset needs
    E[T] >= ln(gamma)/I to reach gamma (Lemma 1), equality up to overshoot
    for the likelihood-ratio e-process;
  * CUSUM e-detector at threshold ln(gamma) (anytime-valid, ARL0 >= gamma):
    ADD * I = h' - 1 + exp(-h') with h' = ln(gamma) + 2*rho*theta;
  * CUSUM calibrated to ARL0 = gamma exactly (Lorden-optimal, Moustakides 1986):
    ADD * I = Phi(gamma * I), Brownian limit with Siegmund's correction.
All three share Lai's first-order limit ln(gamma)/I as gamma -> infinity.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

TRADING_DAYS = 252
RHO_GAUSS = 0.5826  # Siegmund's overshoot constant, Gaussian increments


def kl_from_sharpe(sr_annual: float) -> float:
    """Per-day KL of a homoscedastic Gaussian location shift: SR^2 / 504."""
    return sr_annual ** 2 / (2 * TRADING_DAYS)


def sharpe_from_kl(info: float) -> float:
    """Annualized Sharpe ratio carrying ``info`` nats per day."""
    return math.sqrt(2 * TRADING_DAYS * info)


def first_order_floor(gamma: float, info: float) -> float:
    """Lai's first-order bound ln(gamma)/I, exact only as gamma -> infinity."""
    return math.log(gamma) / info


def evidence_budget(gamma: float, info: float) -> float:
    """Lemma 1: lower bound on E[T] for any e-process started at the onset
    and stopped at gamma; attained up to overshoot by the likelihood ratio."""
    return math.log(gamma) / info


def onset_lr_delay(gamma: float, info: float, theta: float) -> float:
    """Expected delay of the likelihood-ratio e-process started at the onset,
    Gaussian shift of theta standard deviations (LLR increment s.d. = theta):
    E[T] = (ln(gamma) + rho*theta) / I (Wald identity, ladder-height overshoot)."""
    return (math.log(gamma) + RHO_GAUSS * theta) / info


def brownian_h(g: float) -> float:
    """Root h > 0 of exp(h) - h - 1 = g (Brownian CUSUM threshold, scaled)."""
    if g <= 0:
        raise ValueError("g must be positive")
    upper = max(2.0, 2.0 * math.log1p(g) + 2.0)
    return brentq(lambda h: math.expm1(h) - h - g, 1e-12, upper)


def phi(g: float) -> float:
    """Scaled Lorden-optimal delay: ADD * I = Phi(gamma * I).
    Phi(g) = ln g - 1 + O(ln g / g) as g -> inf; g - (2g)^{3/2}/3 + O(g^2) as g -> 0."""
    h = brownian_h(g)
    return h - 1.0 + math.exp(-h)


def cusum_exact(gamma: float, theta: float) -> dict:
    """Page CUSUM on the Gaussian LLR, calibrated to ARL0 = gamma (Siegmund).
    Returns the LLR threshold h and the predicted Lorden delay."""
    info = theta ** 2 / 2
    h_prime = brownian_h(gamma * info)
    h = h_prime - 2 * RHO_GAUSS * theta
    return {"h": h, "h_prime": h_prime,
            "add": (h_prime - 1.0 + math.exp(-h_prime)) / info,
            "feasible": h > 0}


def cusum_threshold(gamma: float, theta: float) -> dict:
    """CUSUM e-detector stopped when exp(W_n) >= gamma, i.e. h = ln(gamma).
    ARL0 >= gamma holds by Lorden's bound; the realised ARL0 is ~ gamma / I."""
    info = theta ** 2 / 2
    h = math.log(gamma)
    h_prime = h + 2 * RHO_GAUSS * theta
    return {"h": h, "h_prime": h_prime,
            "add": (h_prime - 1.0 + math.exp(-h_prime)) / info,
            "arl0": (math.expm1(h_prime) - h_prime) / info}


def mixture_multiplier(dim: int, gamma: float) -> float:
    """Proposition 3: M(D) = x/A with x = A + (D/2) ln(1 + 2x/D), A = ln(gamma).
    Fluid delay of the isotropic Gaussian mixture e-process (matched prior)
    relative to the known-direction likelihood ratio."""
    a = math.log(gamma)
    x = a
    for _ in range(10_000):
        x_new = a + 0.5 * dim * math.log1p(2.0 * x / dim)
        if abs(x_new - x) < 1e-12 * x_new:
            break
        x = x_new
    return x_new / a


def dictionary_multiplier(n_atoms: int, gamma: float, cos2: float) -> float:
    """Average of n_atoms direction-wise e-processes: delay multiplier
    (A + ln n_atoms) / (A cos^2), cos^2 = alignment of the whitened drift
    with the nearest atom."""
    a = math.log(gamma)
    return (a + math.log(n_atoms)) / (a * cos2)


def absorption_delay(add_oracle: float, tau_a: float) -> float:
    """Fluid delay when an adaptive encoder absorbs the drift at rate 1/tau_a.
    Necessary condition for almost-sure detection: tau_a > 2 * add_oracle."""
    ratio = 2.0 * add_oracle / tau_a
    if ratio >= 1.0:
        return math.inf
    return -0.5 * tau_a * math.log1p(-ratio)


def kl_bernoulli_half(p):
    """kl(p || 1/2) in nats, vectorised; information of an exact sign stream."""
    p = np.clip(np.asarray(p, dtype=float), 1e-15, 1 - 1e-15)
    return p * np.log(2 * p) + (1 - p) * np.log(2 * (1 - p))


def factor_information(B, sigma_f, psi_diag, d_lambda, d_alpha):
    """Exact split of Delta_mu' Sigma^{-1} Delta_mu for Sigma = B Sigma_F B' + Psi
    (Corollary 1). Returns (factor_term, breadth_term), with
    factor_term = dl' (Sigma_F + K^{-1})^{-1} dl, K = B' Psi^{-1} B,
    breadth_term = da_perp' Psi^{-1} da_perp (GLS residual of d_alpha on B)."""
    B = np.atleast_2d(np.asarray(B, dtype=float))
    if B.shape[0] < B.shape[1]:
        B = B.T
    psi_inv = 1.0 / np.asarray(psi_diag, dtype=float)
    K = B.T @ (psi_inv[:, None] * B)
    c = np.linalg.solve(K, B.T @ (psi_inv * d_alpha))
    da_perp = d_alpha - B @ c
    dl_tilde = np.atleast_1d(d_lambda) + c
    M = np.atleast_2d(sigma_f) + np.linalg.inv(K)
    factor_term = float(dl_tilde @ np.linalg.solve(M, dl_tilde))
    breadth_term = float(da_perp @ (psi_inv * da_perp))
    return factor_term, breadth_term
