"""Threshold calibrations: window bootstrap (R15 workers, l.431-478, verbatim; quantile rule l.1062) and sign-flip
randomization of null windows. The exact lattice reading is jepadrift.monitors.lattice.select_threshold."""
import numpy as np

from jepadrift.monitors.cusum import bilateral_delay, cusum_max_bilateral
from jepadrift.monitors.streams import fraction_stream


def worker_null_window_real(rng, eps_K_full, H_ref, H_det):
    """
    ADAPTED. The delivered form reads
    `def worker_null_window_real(seed, eps_K_full, H_ref, H_det)` with
    `rng = np.random.default_rng(seed)` as its first statement. Preamble S6
    requires the migration to a 128-bit SeedSequence keyed on role and index, so
    the generator is constructed by the caller and passed in. EVERY OTHER LINE
    IS THE WITNESS'S, and the witness segment is quoted in full in the log by
    control C9.

    Windowed REAL null (c=0), byte-for-byte commensurable with
    worker_race_h1_real: a random window, per-window median/std recentring on
    the H_ref past (non-anticipative), no injection. `cusum_max > lambda` is
    equivalent to `bilateral_delay` firing, so this null is the exact
    false-alarm construction of the H1 race pipeline at c = 0.
    """
    K, T_full = eps_K_full.shape
    t_start = rng.integers(0, T_full - (H_ref + H_det) + 1)
    w = eps_K_full[:, t_start:t_start + H_ref + H_det]
    med = np.median(w[:, :H_ref], axis=1, keepdims=True)
    std = np.std(w[:, :H_ref], axis=1, keepdims=True); std[std == 0] = 1.0
    z = (w - med) / std
    x = fraction_stream(z)[H_ref:]
    return cusum_max_bilateral(x, 0.0)


def worker_race_h1_real(rng, eps_K_full, H_ref, H_det, c, lam_boot):
    """
    ADAPTED, on the same single line and for the same reason. Every other line
    is the witness's, comments included, and the witness segment is quoted in
    full in the log by control C9.
    """
    K, T_full = eps_K_full.shape
    max_start = T_full - (H_ref + H_det)
    t_start = rng.integers(0, max_start + 1)
    eps_window = eps_K_full[:, t_start : t_start + H_ref + H_det]

    # Standardization over H_ref for c*sigma injection
    med = np.median(eps_window[:, :H_ref], axis=1, keepdims=True)
    std = np.std(eps_window[:, :H_ref], axis=1, keepdims=True)
    std[std == 0] = 1.0
    eps_std = (eps_window - med) / std

    # Semi-real H1 injection
    eps_std[:, H_ref:] += c

    x = fraction_stream(eps_std)[H_ref:]
    return bilateral_delay(x, 0.0, lam_boot)


def bootstrap_threshold(null_maxima, alpha):
    """(1 - alpha) quantile of null-window maxima (R15 l.1062); the alarm rule is S > threshold."""
    m = np.asarray(null_maxima, dtype=np.float64)
    if m.size == 0 or not 0.0 < alpha < 1.0:
        raise ValueError("need at least one null maximum and 0 < alpha < 1")
    return float(np.quantile(m, 1.0 - alpha))


def null_windows(x, length, n, rng, flip=False):
    """n windows of `length` rows of x at uniform starts, drawn one by one; flip: one Rademacher sign per day."""
    x = np.asarray(x, dtype=np.float64)
    if not 1 <= length <= x.shape[0] or n < 1:
        raise ValueError(f"need 1 <= length <= {x.shape[0]} and n >= 1, got length={length}, n={n}")
    out = np.empty((n, length) + x.shape[1:])
    for i in range(n):
        s = int(rng.integers(0, x.shape[0] - length + 1))
        out[i] = x[s:s + length]
        if flip:
            out[i] *= rng.choice((-1.0, 1.0), size=length).reshape((length,) + (1,) * (x.ndim - 1))
    return out
