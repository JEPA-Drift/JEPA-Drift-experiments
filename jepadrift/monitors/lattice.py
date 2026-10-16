"""Exact law of a CUSUM on a two-point stream with integer steps +a/-b: absorbing Markov chain on the lattice (generalizes R08 l.521-549)."""
from fractions import Fraction
from math import gcd

import numpy as np

RULES = ("at_or_below", "at_or_above")


def lattice_steps(delta):
    """Steps +a/-b of S+ in lattice units, and the unit, for the exact sign stream 1{y > 0} - 1/2 with reference delta."""
    d = Fraction(repr(float(delta)))
    if not 0 <= d < Fraction(1, 2):
        raise ValueError(f"delta must lie in [0, 1/2), got {delta}")
    up, down = Fraction(1, 2) - d, Fraction(1, 2) + d
    unit = Fraction(gcd(up.numerator * down.denominator, down.numerator * up.denominator),
                    up.denominator * down.denominator)
    a, b = int(up / unit), int(down / unit)
    if a + b > 1000:
        raise ValueError(f"delta={delta} gives a lattice too fine: a + b = {a + b}")
    return a, b, float(unit)


def _barrier(L, a, b, q, sided, comparison):
    if comparison not in ("strict", "weak"):
        raise ValueError(f"comparison must be 'strict' or 'weak', got {comparison!r}")
    if sided not in (1, 2) or L < 0 or L != int(L) or a < 1 or b < 1 or not 0 <= q <= 1:
        raise ValueError("need sided in {1, 2}, integer L >= 0 (lattice units), a >= 1, b >= 1 and 0 <= q <= 1")
    return int(L) + 1 if comparison == "strict" else int(L)


def _down(P, b, axis):
    out = np.zeros_like(P)
    n = P.shape[axis]
    src = [slice(None)] * P.ndim
    dst = [slice(None)] * P.ndim
    src[axis], dst[axis] = slice(0, min(b + 1, n)), slice(0, 1)
    out[tuple(dst)] = P[tuple(src)].sum(axis=axis, keepdims=True)
    if n > b + 1:
        src[axis], dst[axis] = slice(b + 1, n), slice(1, n - b)
        out[tuple(dst)] = P[tuple(src)]
    return out


def _up(P, a, axis):
    out = np.zeros_like(P)
    n = P.shape[axis]
    k = max(n - a, 0)
    src = [slice(None)] * P.ndim
    dst = [slice(None)] * P.ndim
    src[axis], dst[axis] = slice(0, k), slice(a, n)
    out[tuple(dst)] = P[tuple(src)]
    src[axis] = slice(k, n)
    return out, P[tuple(src)].sum()


def exceedance(H, L, a, b, q=0.5, sided=2, comparison="strict"):
    """P(M_H > L) ('strict') or P(M_H >= L) ('weak') in lattice units, M_H = max over 1 <= t <= H of S+ (sided=1)
    or of max(S+, S-) (sided=2), S_0 = 0; with probability q, S+ steps +a and S- steps -b, otherwise S+ -b and S- +a."""
    B = _barrier(L, a, b, q, sided, comparison)
    if H < 0 or H != int(H):
        raise ValueError(f"H must be an integer >= 0, got {H}")
    if H == 0:
        return 0.0
    if B == 0:
        return 1.0
    P = np.zeros((B,) * sided)
    P[(0,) * sided] = 1.0
    absorbed = 0.0
    for _ in range(H):
        if sided == 1:
            up, out = _up(P, a, 0)
            P = q * up + (1 - q) * _down(P, b, 0)
            absorbed += q * out
        else:
            up1, out1 = _up(_down(P, b, 1), a, 0)
            up0, out0 = _up(_down(P, b, 0), a, 1)
            P = q * up1 + (1 - q) * up0
            absorbed += q * out1 + (1 - q) * out0
    return float(absorbed)


def arl0(L, a, b, q=0.5, sided=2, comparison="strict"):
    """Expected run length to the first alarm of the chain of `exceedance`, from S_0 = 0, by solving (I - Q) t = 1."""
    B = _barrier(L, a, b, q, sided, comparison)
    if not 0 < q < 1:
        raise ValueError("arl0 needs 0 < q < 1")
    if B == 0:
        return 1.0
    shape = (B,) * sided
    n = B ** sided
    if n > 10_000:  # ponytail: dense O(n^3) solve, banded/sparse solver if L > 99 is ever needed
        raise ValueError(f"state space too large for the dense ARL0 solve: {n} states")
    grid = np.indices(shape).reshape(sided, -1)
    rows = np.arange(n)
    Q = np.zeros((n, n))
    for prob, steps in ((q, (a, -b)), (1 - q, (-b, a))):
        new = [np.maximum(g + s, 0) for g, s in zip(grid, steps)]
        keep = np.all([v < B for v in new], axis=0)
        np.add.at(Q, (rows[keep], np.ravel_multi_index(tuple(v[keep] for v in new), shape)), prob)
    return float(np.linalg.solve(np.eye(n) - Q, np.ones(n))[0])


def _level(L, a, b, q, sided, comparison, H):
    if H is None:
        return 1.0 / arl0(L, a, b, q, sided, comparison)
    return exceedance(H, L, a, b, q, sided, comparison)


def attainable_levels(H=None, delta=0.1, sided=2, q=0.5, comparison="strict", min_level=1e-3):
    """Rows (lambda, level) for lambda = L * unit, L = 0, 1, ... down to the first level <= min_level;
    level = false-alarm probability by horizon H, or 1/ARL0 when H is None."""
    if not 0 < min_level < 1:
        raise ValueError("min_level must lie in (0, 1)")
    a, b, unit = lattice_steps(delta)
    rows = []
    L = 0
    while not rows or rows[-1][1] > min_level:
        rows.append((L * unit, _level(L, a, b, q, sided, comparison, H)))
        L += 1
    return np.array(rows)


def select_threshold(nominal, rule="at_or_below", comparison="strict", *, H=None, delta=0.1, sided=2, q=0.5):
    """Lattice threshold whose exact level (false-alarm probability by horizon H, or 1/ARL0 when H is None; for a
    target ARL0 gamma pass nominal = 1/gamma) is the nearest at or below / above the nominal level. Returns
    units L, lam = L * unit, the float `threshold` (midpoint between lattice points) to use as S > threshold,
    the exact level and the unit."""
    if rule not in RULES:
        raise ValueError(f"rule must be one of {RULES}, got {rule!r}")
    if not 0 < nominal < 1:
        raise ValueError("nominal must lie in (0, 1)")
    a, b, unit = lattice_steps(delta)

    def level(L):
        return _level(L, a, b, q, sided, comparison, H)

    lo, hi = -1, 0
    while level(hi) > nominal:
        lo, hi = hi, max(1, 2 * hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if level(mid) <= nominal else (mid, hi)
    L = hi if rule == "at_or_below" else hi - 1
    if L < 0:
        raise ValueError("no attainable level above the nominal one")
    return {"units": L, "lam": L * unit, "threshold": (L + 0.5 if comparison == "strict" else L - 0.5) * unit,
            "level": level(L), "unit": unit}
