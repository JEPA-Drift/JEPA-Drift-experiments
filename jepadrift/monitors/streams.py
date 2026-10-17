"""Monitored streams: Article B label and energy streams (R01 l.298-304, 369-374) and the exact sign stream (Lemma 2)."""
import numpy as np


def _finite(a):
    a = np.asarray(a, dtype=np.float64)
    if not np.isfinite(a).all():
        raise ValueError("input contains non-finite values")
    return a


def label_stream(r, q_hat):
    """Article B Concept stream 1{r > 0} - q_hat."""
    return (_finite(r) > 0).astype(float) - q_hat


def exact_sign_stream(y, rng):
    """Exact sign stream 1{y > 0} - 1/2; ties y == 0 are broken by a fair coin drawn from the Generator rng."""
    y = _finite(y)
    b = y > 0
    ties = y == 0
    b[ties] = rng.random(int(ties.sum())) < 0.5
    return b - 0.5


def energy_stream(r, mu, sigma):
    """Article B Data stream (r**2 - mu) / sigma."""
    return (_finite(r) ** 2 - mu) / sigma


def fraction_stream(eps):
    """Cross-sectional fraction of positive recentered signs (median=0 by symmetry)."""
    return (eps>0.0).mean(axis=0) - 0.5
