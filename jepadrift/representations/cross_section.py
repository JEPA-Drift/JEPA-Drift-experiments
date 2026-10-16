"""Cross-sectional representations of degree 0 (P3-CS): normalized projected cross-section and centred ranks."""
import math

import numpy as np

from jepadrift.representations.base import Representation
from jepadrift.representations.pca import check_K, pca_directions

B_CHOICES = ("pc1", "ones")
DZ_MODES = ("factor", "full")


class DegreeZero(Representation):
    """z_odd = U'p / ||p||, p = x - b b'x (b unit: PC1 loadings or 1/sqrt(N), U frozen residual eigenvectors); z_even = [||p||]."""

    def __init__(self, b="pc1", K="mp", mode="factor"):
        if b not in B_CHOICES:
            raise ValueError(f"b must be one of {B_CHOICES}, got {b!r}")
        if mode not in DZ_MODES:
            raise ValueError(f"mode must be one of {DZ_MODES}, got {mode!r}")
        check_K(K)
        self.config = {"b": b, "K": K, "mode": mode}

    def _fit(self, X, C):
        _, eigvec, sel, stats = pca_directions(X, self.config["K"], self.config["mode"], "ledoit_wolf")
        N = self.n_assets
        b = eigvec[:, 0].copy() if self.config["b"] == "pc1" else np.full(N, 1.0 / math.sqrt(N))
        self.state = {"b": b, "U": eigvec[:, sel[1:]]}
        self.stats = {"b": self.config["b"], **{k: stats[k] for k in ("K", "mp_edge", "n_above_edge", "shrinkage")
                                                if k in stats}}
        D = sel.size - 1
        self.heads = {"z_odd": {"dim": D, "parity": "odd", "degree": 0,
                                "definition": "U'p / ||p||, p = x - b b'x, 0 when ||p|| = 0"},
                      "z_even": {"dim": 1, "parity": "even", "degree": 1, "definition": "[||p||]"}}
        self.channels = {"residual": list(range(D))}

    def _day(self, x, C):
        b, U = self.state["b"], self.state["U"]
        p = x - b * (b @ x)
        n = math.sqrt(p @ p)
        # ponytail: exact-zero guard only, add a relative threshold if a pure-market day ever appears
        z = p @ U / n if n > 0 else np.zeros(U.shape[1])
        return z, np.array([n])


class CenteredRanks(Representation):
    """z_i = (r_i - (N+1)/2)/N with average ranks for ties: odd in x and homogeneous of degree 0."""

    def __init__(self):
        self.config = {}

    def _fit(self, X, C):
        N = self.n_assets
        self.state, self.stats = {}, {}
        self.heads = {"z_odd": {"dim": N, "parity": "odd", "degree": 0,
                                "definition": "(rank_i - (N+1)/2)/N, average ranks for ties"},
                      "z_even": {"dim": N, "parity": "even", "degree": 0, "definition": "z_odd ** 2"}}
        self.channels = {"assets": list(range(N))}

    def _day(self, x, C):
        _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
        z = ((np.cumsum(cnt) - (cnt - 1) / 2)[inv] - (x.shape[0] + 1) / 2) / x.shape[0]
        return z, z * z
