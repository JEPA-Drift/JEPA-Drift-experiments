"""Z-1 representation on a frozen CA-T-JEPA checkpoint (stream 14): nothing is fitted on the fit rows."""
from pathlib import Path

import numpy as np

from jepadrift.jepa import ca_tjepa
from jepadrift.representations.base import Representation


class CATJEPA(Representation):
    """Frozen context encoder with mask=none: z_odd = [f_hat(P), odd part of g], z_even = even part of g."""

    missing = True

    def __init__(self, ckpt, D=None):
        ca_tjepa.configure()
        self.net, record = ca_tjepa.load_checkpoint(ckpt)
        d = record["config"]["model"]["d"]
        if D is not None and D != d:
            raise ValueError(f"D = {D} does not match the checkpoint width d = {d}")
        self.s, self.b = (np.asarray(record["frozen"][k], dtype=np.float64) for k in ("s", "b"))
        self.lambda_f = record["config"]["neutralization"]["lambda_f"]
        self.weights = ca_tjepa.flat_weights(self.net)
        self.config = {"ckpt_sha256": Path(ckpt).name, "d": d, "extraction": "context encoder, mask=none",
                       "neutralization": {"factors": 1, "weights": "identity", "lambda_f": self.lambda_f}}

    def _fit(self, X, C):
        if X.shape[1] != self.s.size:
            raise ValueError(f"the checkpoint holds {self.s.size} assets, X has {X.shape[1]}")
        if C is None or C.shape != (*X.shape, ca_tjepa.N_CHARS):
            raise ValueError(f"C must be {(*X.shape, ca_tjepa.N_CHARS)}, got {None if C is None else C.shape}")
        d = self.config["d"]
        self.state = {"s": self.s, "b": self.b, "weights": self.weights}
        self.stats = {"c_nan_imputed": int(np.isnan(C).sum()), "absent_cells": int((~np.isfinite(X)).sum())}
        self.heads = {"z_odd": {"dim": d + 1, "parity": "odd", "degree": None,
                                "definition": "[f_hat(P), (g(x) - g(-x)) / 2], g = head(mean of context tokens)"},
                      "z_even": {"dim": d, "parity": "even", "degree": None, "definition": "(g(x) + g(-x)) / 2"}}
        self.channels = {"market": [0], "residual": list(range(1, d + 1))}

    def _day(self, x, C):
        return ca_tjepa.extract_day(self.net, x, C, self.s, self.b, self.lambda_f)
