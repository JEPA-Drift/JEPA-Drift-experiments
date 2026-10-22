"""Drift statistics shared by the audit and the experiments, moved verbatim from experiments/audit_information.py.

Stream 8b (C-stats-drift): debiased drift Sharpe, moving-block bootstrap, shifted percentile interval, SPY phase
transitions and circular placebo rotations; `_ci` of the audit is exported as `shifted_percentile_ci`.
"""
import numpy as np

WINDOW = ("2005-01-01", "2019-12-31")
MIN_PHASE = 20
BLOCK = 20


def transitions(phases):
    """Adjacent phase pairs with a boundary in [2005-01-01, 2019-12-31) and at least MIN_PHASE rows on each side."""
    return [(i, i + 1) for i in range(len(phases) - 1)
            if phases[i][2] == phases[i + 1][1] and WINDOW[0] <= phases[i][2] < WINDOW[1]
            and min(phases[i][3].size, phases[i + 1][3].size) >= MIN_PHASE]


def _sr2(delta, S, n1, n2):
    """Raw, exactly unbiased and prompt-formula SR^2 from mean differences and pooled covariances (leading axes broadcast)."""
    dim, nu, c = delta.shape[-1], n1 + n2 - 2, 1.0 / n1 + 1.0 / n2
    if nu <= dim + 1:
        raise ValueError(f"a pooled covariance with {nu} degrees of freedom cannot whiten {dim} dimensions")
    D2 = np.einsum("...i,...i->...", delta, np.linalg.solve(S, delta[..., None])[..., 0])
    k = (nu - dim - 1) / nu
    return 252 * D2, 252 * (D2 * k - dim * c), 252 * (D2 - dim * c) * k


def debiased_sr2(Y1, Y2):
    """(sr2_raw, sr2_debiased, sr2_spec) of the mean shift from phase 1 to phase 2, pooled within-phase covariance."""
    A, B = Y1 - Y1.mean(axis=0), Y2 - Y2.mean(axis=0)
    S = (A.T @ A + B.T @ B) / (len(Y1) + len(Y2) - 2)
    return tuple(float(v) for v in _sr2(Y2.mean(axis=0) - Y1.mean(axis=0), S, len(Y1), len(Y2)))


def mbb_indices(n, B, rng):
    """Moving-block bootstrap rows (Kunsch, 1989): ceil(n / BLOCK) uniform block starts, blocks concatenated, cut to n."""
    starts = rng.integers(0, n - BLOCK + 1, size=(B, -(-n // BLOCK)))
    return (starts[:, :, None] + np.arange(BLOCK)).reshape(B, -1)[:, :n]


def shifted_percentile_ci(draws, estimate):
    """95 % percentile interval of the bootstrap draws shifted by the bootstrap bias mean(draws) - estimate."""
    shift = draws.mean() - estimate
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return lo - shift, hi - shift


def rotate_phases(phases, T, offset):
    """Phases moved by `offset` rows around the window (circular); a phase crossing the seam keeps its rows pooled."""
    return [(pid, start, end, np.sort((rows + offset) % T)) for pid, start, end, rows in phases]
