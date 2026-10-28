"""Drift statistics shared by the audit and the experiments, moved verbatim from experiments/audit_information.py.

Stream 8b (C-stats-drift): debiased drift Sharpe, moving-block bootstrap, shifted percentile interval, SPY phase
transitions and circular placebo rotations; `_ci` of the audit is exported as `shifted_percentile_ci`.
Stream 12 (C-e1-drift-move): SPY phases of a dating, frozen-direction projections and the subspaces of the budget.
"""
import numpy as np

from jepadrift.data_loader import articleB

WINDOW = ("2005-01-01", "2019-12-31")
MIN_PHASE = 20
BLOCK = 20
N_PC = 20
MAX_DIM = 30


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


def char_directions(C, V_f):
    """u_{t,j} = P c_{t,j} / ||P c_{t,j}||, P = I - V_f V_f' (Euclidean projection on the idiosyncratic subspace)."""
    U = C - V_f @ (V_f.T @ C)
    norm = np.linalg.norm(U, axis=1, keepdims=True)
    if not (norm > 1e-10 * np.linalg.norm(C, axis=1, keepdims=True)).all():
        raise ValueError("a characteristic vanishes after projection on the idiosyncratic subspace")
    return U / norm


def projections(d, n_pc=N_PC):
    """Frozen-direction series y_t = u_t'x_t: PC1..PC<n_pc>, then the orthogonalised characteristics (D3)."""
    series = {f"PC{k + 1}": d["X"] @ d["eigvec"][:, k] for k in range(n_pc)}
    if d["C"] is not None:
        y = np.einsum("tnp,tn->tp", char_directions(d["C"], d["eigvec"][:, :d["K"] + 1]), d["X"])
        series.update({f"char:{c.removeprefix('c_')}": y[:, j] for j, c in enumerate(d["chars"])})
    return series


def spy_phases(variant, dates):
    """SPY phases of a dating as (phase_id, start, end, window rows dated in (start, end]); empty phases dropped."""
    phases = articleB.load_phases(variant)
    out = []
    for r in phases[phases.ticker == "SPY"].itertuples():
        rows = np.flatnonzero((dates > np.datetime64(r.start_date)) & (dates <= np.datetime64(r.end_date)))
        if rows.size:
            out.append((int(r.phase_id), r.start_date, r.end_date, rows))
    return out


def subspaces(d, proj):
    """Projections of item 4: market PC1, factor PC2..PC(K+1), idiosyncratic blocks of MAX_DIM PCs, characteristics."""
    Z, K = d["X"] @ d["eigvec"], d["K"]
    out = {"market": Z[:, :1], "factor": Z[:, 1:K + 1]}
    for b, j in enumerate(range(K + 1, Z.shape[1], MAX_DIM), 1):
        out[f"idio:b{b}"] = Z[:, j:j + MAX_DIM]
    chars = [y for label, y in proj.items() if label.startswith("char:")]
    if chars:
        out["chars"] = np.column_stack(chars)
    return out
