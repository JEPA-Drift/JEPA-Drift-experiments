"""Anytime-valid statistics on bounded centred streams x in [-1, 1] (x = 2s for the exact sign stream): betting
e-process, MIX (port of R09 build_mixture_kernel, l.317-336), SR and CUSUM e-detectors, dictionary average and the
closed-form sub-Gaussian mixture of Proposition 3. Every output is a natural logarithm."""
import numpy as np

MIX_H = 5000
START_GRID_SIZE = 16
ETA0_MIX_GRID = [0.05, 0.10, 0.15]
SIDES = [1, -1]
START_GRID = np.linspace(0, MIX_H - 1, START_GRID_SIZE, dtype=int)
C_MIX = len(START_GRID) * len(ETA0_MIX_GRID) * len(SIDES)
MIX_W = 1.0 / C_MIX
EDETECTOR_ETA0 = (0.05, 0.10, 0.15, 0.20)


def _bounded(x):
    x = np.asarray(x, dtype=np.float64)
    if not (np.isfinite(x).all() and (np.abs(x) <= 1.0).all()):
        raise ValueError("x must be finite and lie in [-1, 1]")
    return x


def _logsumexp(a, axis=-1):
    m = a.max(axis=axis)
    return m + np.log(np.exp(a - np.expand_dims(m, axis)).sum(axis=axis))


def log_betting_eprocess(x, lam):
    """log prod_{s<=t} (1 + lam_s x_s) along the last axis; |lam| < 1, lam scalar or predictable (lam_t from x_{<t})."""
    x = _bounded(x)
    lam = np.asarray(lam, dtype=np.float64)
    if not (np.abs(lam) < 1.0).all():
        raise ValueError("bets must satisfy |lam| < 1")
    return np.cumsum(np.log1p(lam * x), axis=-1)


def build_mixture_kernel():
    """
    The 16 x 3 x 2 = 96 betting martingales of the mixture, in the witness's own
    construction order (l.356-366): a start time from the horizon grid, a
    betting fraction from ETA0_MIX_GRID, a side from SIDES. A component that has
    not started holds value 1, so the convex combination is a non-negative
    martingale with E_0 = 1 and Ville's inequality applies to it.
    """
    log_inc_1 = np.zeros(C_MIX)
    log_inc_0 = np.zeros(C_MIX)
    idx = 0
    start_times = np.zeros(C_MIX, dtype=int)
    for st in START_GRID:
        for e0 in ETA0_MIX_GRID:
            for sd in SIDES:
                start_times[idx] = st
                log_inc_1[idx] = np.log(2 * (0.5 + sd * e0))
                log_inc_0[idx] = np.log(2 * (0.5 - sd * e0))
                idx += 1
    return start_times, log_inc_1, log_inc_0


def log_mix_eprocess(x):
    """log of the MIX mixture along the last axis (update rule of R09 l.451-455), the bit being x > 0."""
    x = _bounded(x)
    bits = x.reshape(-1, x.shape[-1]) > 0
    start_times, log_inc_1, log_inc_0 = build_mixture_kernel()
    log_m = np.full((bits.shape[0], C_MIX), np.log(MIX_W))
    out = np.empty(bits.shape)
    for t in range(bits.shape[1]):
        active = t >= start_times
        log_m[:, active] += np.where(bits[:, t, None], log_inc_1[active], log_inc_0[active])
        out[:, t] = _logsumexp(log_m)
    return out.reshape(x.shape)


def log_edetector(x, kind="cusum", eta0=EDETECTOR_ETA0):
    """log of the average of the SR (M_n = (1 + M_{n-1}) f_n) or CUSUM (M_n = max(1, M_{n-1}) f_n) e-detectors,
    f_n = 1 + lam x_n, over the bets lam = 2 side eta0 (eta0 in `eta0`, side in SIDES); M_n >= gamma gives ARL0 >= gamma."""
    if kind not in ("sr", "cusum"):
        raise ValueError(f"kind must be 'sr' or 'cusum', got {kind!r}")
    x = _bounded(x)
    lam = np.array([2.0 * side * e for e in eta0 for side in SIDES])
    if not (np.abs(lam) < 1.0).all():
        raise ValueError("bets must satisfy |2 eta0| < 1")
    flat = x.reshape(-1, x.shape[-1])
    log_m = np.full((flat.shape[0], lam.size), -np.inf)
    out = np.empty(flat.shape)
    for t in range(flat.shape[1]):
        log_f = np.log1p(lam * flat[:, t, None])
        log_m = (np.logaddexp(0.0, log_m) if kind == "sr" else np.maximum(0.0, log_m)) + log_f
        out[:, t] = _logsumexp(log_m) - np.log(lam.size)
    return out.reshape(x.shape)


def log_dictionary_edetector(x, kind="cusum", eta0=EDETECTOR_ETA0):
    """log of the equal-weight average over the K directions of x (..., T, K) of log_edetector; valid whatever the
    dependence between directions."""
    per = log_edetector(np.moveaxis(np.asarray(x, dtype=np.float64), -1, -2), kind, eta0)
    return _logsumexp(per, axis=-2) - np.log(per.shape[-2])


def log_subgaussian_mixture(z, s2):
    """log L_n = -(D/2) log(1 + n s2) + s2 |S_n|^2 / (2 (1 + n s2)), S_n = sum_{t<=n} z_t, z of shape (..., T, D)
    (Proposition 3); valid only if the coordinates are independent under H0 (sub-Gaussian variance proxy I_D, e.g.
    independent sign streams 2b - 1)."""
    z = np.asarray(z, dtype=np.float64)
    if not np.isfinite(z).all() or not s2 > 0:
        raise ValueError("z must be finite and s2 > 0")
    S = np.cumsum(z, axis=-2)
    n = np.arange(1, z.shape[-2] + 1)
    return -0.5 * z.shape[-1] * np.log1p(n * s2) + s2 * (S * S).sum(axis=-1) / (2.0 * (1.0 + n * s2))


def log_average_betting_eprocess(x, lam):
    """log of the average over bets lam (J,) and directions of x (..., T, K) of prod_{s<=t} (1 + lam_j x_{s,k})."""
    x = _bounded(x)
    lam = np.asarray(lam, dtype=np.float64)
    if lam.ndim != 1 or lam.size == 0 or not (np.abs(lam) < 1.0).all():
        raise ValueError("bets must form a non-empty 1-D array with |lam| < 1")
    logs = np.cumsum(np.log1p(lam[:, None, None] * np.moveaxis(x, -1, -2)[..., None, :, :]), axis=-1)
    flat = logs.reshape(logs.shape[:-3] + (-1, logs.shape[-1]))
    return _logsumexp(flat, axis=-2) - np.log(flat.shape[-2])


def first_alarm(log_m, gamma):
    """First index t with log_m[..., t] >= log(gamma) along the last axis; -1 when none."""
    hit = np.asarray(log_m) >= np.log(gamma)
    return np.where(hit.any(axis=-1), hit.argmax(axis=-1), -1).astype(np.int64)
