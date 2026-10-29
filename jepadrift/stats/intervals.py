"""Binomial intervals shared by the experiments; `wilson` moved verbatim from experiments/e10_robustness.py (stream 27)."""
from statsmodels.stats.proportion import proportion_confint


def wilson(k, n):
    """Wilson 95 % interval of k successes out of n (n may be an effective size), clamped to contain k / n in [0, 1]."""
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return max(0.0, min(float(lo), k / n)), min(1.0, max(float(hi), k / n))
