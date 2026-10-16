"""D5 Monte Carlo backgrounds; NU, T_SCALE, t_innov and Garch moved verbatim from experiments/e2_floor_validation.py."""
import math

import numpy as np

NU = 7
T_SCALE = math.sqrt((NU - 2) / NU)          # unit-variance Student-t innovations


def t_innov(rng, shape):
    """Unit-variance Student-t (nu = 7); multivariate t when shape is 2-D."""
    if len(shape) == 1:
        return rng.standard_t(NU, size=shape) * T_SCALE
    z = rng.standard_normal(shape)
    w = np.sqrt(rng.chisquare(NU, size=shape[0]) / NU)
    return z / w[:, None] * T_SCALE


class Garch:
    """Common-volatility GARCH(1,1), unit unconditional variance, run in parallel."""

    def __init__(self, rng, reps, dim, alpha, beta, burn=1000):
        self.rng, self.reps, self.dim = rng, reps, dim
        self.alpha, self.beta, self.omega = alpha, beta, 1.0 - alpha - beta
        self.s2 = np.ones(reps)
        self.prev = np.zeros(reps)          # mean square of the last background draw
        for _ in range(burn):
            self.draw()

    def draw(self):
        self.s2 = self.omega + self.alpha * self.prev + self.beta * self.s2
        sig = np.sqrt(self.s2)
        if self.dim == 1:
            x = sig * t_innov(self.rng, (self.reps,))
            self.prev = x ** 2
        else:
            x = sig[:, None] * t_innov(self.rng, (self.reps, self.dim))
            self.prev = (x ** 2).mean(axis=1)
        sign = self.rng.choice((-1.0, 1.0), size=self.reps)   # day-level symmetrisation
        return (x * sign) if self.dim == 1 else x * sign[:, None], sig


def gaussian_latent(T, D, rng):
    """Gaussian i.i.d. latent stream (T, D), the D5 background of Propositions 2-3."""
    return rng.standard_normal((T, D))


def garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None, burn=1000):
    """Common-volatility GARCH(1,1) panel (T, N), unit variance, multivariate t_nu or Gaussian (nu=None) innovations."""
    if alpha < 0 or beta < 0 or alpha + beta >= 1:
        raise ValueError(f"need alpha, beta >= 0 and alpha + beta < 1, got {alpha}, {beta}")
    if nu is not None and nu <= 2:
        raise ValueError(f"nu must exceed 2 for unit-variance innovations, got {nu}")
    if factor_rho is not None and not 0 <= factor_rho < 1:
        raise ValueError(f"factor_rho must lie in [0, 1), got {factor_rho}")
    omega = 1.0 - alpha - beta
    s2, prev = 1.0, 0.0
    out = np.empty((T, N))
    # ponytail: one panel per call, add a replicate axis if E3's many-path loops dominate runtime
    for t in range(burn + T):
        s2 = omega + alpha * prev + beta * s2
        z = rng.standard_normal(N)
        if factor_rho is not None:
            z = math.sqrt(factor_rho) * rng.standard_normal() + math.sqrt(1.0 - factor_rho) * z
        if nu is not None:
            z = z / math.sqrt(rng.chisquare(nu) / nu) * math.sqrt((nu - 2) / nu)
        x = math.sqrt(s2) * z
        prev = float(np.mean(x ** 2))
        if t >= burn:
            out[t - burn] = x
    return out
