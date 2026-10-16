"""PCA-orthogonal representation (P3-C, P3-D, P3-KF): market channel PC1 plus a whitened residual block."""
import math
import operator

import numpy as np

from jepadrift.representations.base import Representation
from jepadrift.stats.covariance import eigh_desc, ledoit_wolf

MODES = ("factor", "full", "tail10")
SHRINKAGES = ("ledoit_wolf", None)
TAIL_SHARE = 0.10


def mp_edge(T, N):
    """Marchenko-Pastur upper edge (1 + sqrt(N/T))^2 of a T x N sample correlation (sigma^2 = 1)."""
    return (1.0 + math.sqrt(N / T)) ** 2


def mp_count(X):
    """Sample-correlation eigenvalues of X above the Marchenko-Pastur edge, PC1 included: (n_above, edge)."""
    T, N = X.shape
    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.corrcoef(X, rowvar=False)
    if not np.isfinite(R).all():
        raise ValueError("sample correlation is not finite: an asset has zero variance on the fit window")
    edge = mp_edge(T, N)
    return int((np.linalg.eigvalsh(R) > edge).sum()), edge


def check_K(K):
    """Return 'mp' unchanged, else K as a Python int >= 1 (numpy integers accepted, bool excluded)."""
    if K == "mp":
        return K
    try:
        k = 0 if isinstance(K, bool) else operator.index(K)
    except TypeError:
        k = 0
    if k < 1:
        raise ValueError(f"K must be 'mp' or an int >= 1, got {K!r}")
    return k


def pca_directions(X, K, mode, shrinkage):
    """Signed eigen-pairs of the fit covariance and selected columns (0 = PC1, then the residual of `mode`)."""
    N = X.shape[1]
    if shrinkage == "ledoit_wolf":
        sigma, delta = ledoit_wolf(X)
    else:
        Xc = X - X.mean(axis=0)
        sigma, delta = Xc.T @ Xc / X.shape[0], None
    eigval, eigvec = eigh_desc(sigma)
    n_above, edge = mp_count(X)
    stats = {"trace": float(eigval.sum()), "shrinkage": delta, "mp_edge": edge, "n_above_edge": n_above}
    if mode == "factor":
        k = n_above - 1 if K == "mp" else K
        if not 1 <= k <= N - 1:
            raise ValueError(f"factor residual needs 1 <= K <= {N - 1}, got K = {k} "
                             f"({n_above} eigenvalues above the MP edge); pass an integer K")
        sel = np.arange(k + 1)
        stats["K"] = k
    elif mode == "full":
        sel = np.arange(N)
    else:
        share = np.cumsum(eigval[::-1]) / eigval.sum()
        m = int((share <= TAIL_SHARE).sum())
        if m == 0:
            raise ValueError(f"no trailing component holds at most {TAIL_SHARE:.0%} of the variance")
        sel = np.concatenate([[0], np.arange(N - m, N)])
        stats["tail_count"], stats["tail_share"] = m, float(share[m - 1])
    if not eigval[sel].min() > 0:
        raise ValueError("a selected eigenvalue is not positive; use shrinkage='ledoit_wolf' or a longer fit window")
    stats["eigval"] = eigval[sel].tolist()
    return eigval, eigvec, sel, stats


class PCAOrthogonal(Representation):
    """z = x @ W with W = V_sel diag(eigval_sel)^(-1/2): column 0 = v_1'x / sqrt(lambda_1), then the residual block."""

    def __init__(self, K="mp", mode="factor", shrinkage="ledoit_wolf"):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
        if shrinkage not in SHRINKAGES:
            raise ValueError(f"shrinkage must be one of {SHRINKAGES}, got {shrinkage!r}")
        K = check_K(K)
        self.config = {"K": K, "mode": mode, "shrinkage": shrinkage}

    def _fit(self, X, C):
        eigval, eigvec, sel, self.stats = pca_directions(X, **self.config)
        self.state = {"W": eigvec[:, sel] / np.sqrt(eigval[sel])}
        D = sel.size
        self.heads = {"z_odd": {"dim": D, "parity": "odd", "degree": 1,
                                "definition": "x @ W, W = V_sel diag(eigval_sel)^(-1/2)"},
                      "z_even": {"dim": D, "parity": "even", "degree": 2, "definition": "z_odd ** 2"}}
        self.channels = {"market": [0], "residual": list(range(1, D))}

    def _day(self, x, C):
        z = x @ self.state["W"]
        return z, z * z
