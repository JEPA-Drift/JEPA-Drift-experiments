"""Variance-inflation factor of a monitored statistic: spectral (Bartlett) and operational (threshold ratio) readings."""
import numpy as np

from jepadrift.monitors.cusum import cusum_trajectory_vec


def gamma_spectral(x, L=None):
    """1 + 2 sum_{k<=L} (1 - k/(L+1)) rho_k along the last axis, L = floor(4 (n/100)^(2/9)) by default [Newey & West, 1994]."""
    x = np.asarray(x, dtype=np.float64)
    if not np.isfinite(x).all():
        raise ValueError("input contains non-finite values")
    n = x.shape[-1]
    if L is None:
        L = int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))
    if not 0 <= L < n:
        raise ValueError(f"need 0 <= L < n, got L={L}, n={n}")
    xc = x - x.mean(axis=-1, keepdims=True)
    denom = (xc * xc).sum(axis=-1)
    if (denom == 0.0).any():
        raise ValueError("gamma_spectral is undefined for a constant series (zero variance)")
    g = np.ones(x.shape[:-1])
    for k in range(1, L + 1):
        g = g + 2.0 * (1.0 - k / (L + 1.0)) * (xc[..., k:] * xc[..., :-k]).sum(axis=-1) / denom
    return g if g.ndim else float(g)


def required_threshold(paths, delta, target, criterion="fpr", H=None, tol=1e-9):
    """Smallest lambda for the strict one-sided CUSUM on null paths (R, T) whose false-alarm rate by horizon H is
    <= target (criterion 'fpr') or whose mean run length, censored at T, is >= target (criterion 'arl0');
    monotone bisection."""
    S = cusum_trajectory_vec(paths, delta)
    S = S.reshape(-1, S.shape[-1])
    if criterion == "fpr":
        peak = S[:, :H].max(axis=1)

        def ok(lam):
            return (peak > lam).mean() <= target
    elif criterion == "arl0":
        def ok(lam):
            hit = S > lam
            return np.where(hit.any(axis=1), hit.argmax(axis=1) + 1, S.shape[1]).mean() >= target
    else:
        raise ValueError(f"criterion must be 'fpr' or 'arl0', got {criterion!r}")
    lo, hi = 0.0, float(S.max()) + 1.0
    if not ok(hi):
        raise ValueError("target not attainable on these paths")
    if ok(lo):
        return lo
    while hi - lo > tol * max(1.0, hi):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi


def gamma_operational(paths, delta, lam_iid, target, criterion="fpr", H=None, tol=1e-9):
    """Gamma^op = lambda_required / lambda_iid at a fixed false-alarm rate or ARL0."""
    return required_threshold(paths, delta, target, criterion, H, tol) / lam_iid
