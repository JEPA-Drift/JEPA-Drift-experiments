"""Interface Z (docs/sections/interface_Z.md): fit on one pretrain or calib segment, day-by-day transform, hashed frozen state."""
import copy
import hashlib
import json

import numpy as np

INTERFACE = "Z-1"


def _sha256(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def _check(a, ndim, name):
    if not isinstance(a, np.ndarray):
        raise TypeError(f"{name} must be a numpy array of returns, got {type(a).__name__}")
    if a.ndim != ndim or a.dtype != np.float64:
        raise ValueError(f"{name} must be {ndim}-D float64, got ndim={a.ndim}, dtype={a.dtype}")
    if not np.isfinite(a).all():
        raise ValueError(f"{name} has non-finite values")


class Representation:
    """Base class: subclasses set config in __init__ and implement _fit(X, C) and _day(x, C) -> (z_odd, z_even)."""

    odd_head = True

    def fit(self, X_fit, C_fit, dates_fit):
        """Fit on the rows of one pretrain or calib segment, dated by dates_fit; returns self."""
        _check(X_fit, 2, "X_fit")
        T, N = X_fit.shape
        if T < 2 or N < 2:
            raise ValueError(f"X_fit needs at least 2 days and 2 assets, got {X_fit.shape}")
        dates_fit = np.asarray(dates_fit, dtype="datetime64[D]")
        if dates_fit.shape != (T,):
            raise ValueError(f"dates_fit must hold one date per row of X_fit ({T}), got shape {dates_fit.shape}")
        self.n_assets = N
        self.fit_info = {"first_day": str(dates_fit[0]), "last_day": str(dates_fit[-1]), "days": T,
                         "x_sha256": _sha256(X_fit), "c_sha256": None if C_fit is None else _sha256(C_fit)}
        self._fit(X_fit, C_fit)
        return self

    def transform_day(self, x_t, C_t=None):
        """Encode one day: {"z_odd": (D,), "z_even": (D',)}."""
        _check(x_t, 1, "x_t")
        if x_t.shape[0] != self.n_assets:
            raise ValueError(f"x_t must hold {self.n_assets} assets, got {x_t.shape[0]}")
        z_odd, z_even = self._day(x_t, C_t)
        return {"z_odd": z_odd, "z_even": z_even}

    def transform_panel(self, X, C=None):
        """Apply transform_day to every row of X, with no operation across days."""
        _check(X, 2, "X")
        if X.shape[0] == 0:
            raise ValueError("X must hold at least one day (T >= 1)")
        # ponytail: per-day loop (bitwise equal to transform_day), vectorize in a subclass if E1 runtime needs it
        days = [self.transform_day(x, None if C is None else C[t]) for t, x in enumerate(X)]
        return {key: np.stack([day[key] for day in days]) for key in ("z_odd", "z_even")}

    def state_hash(self):
        """SHA-256 of the class, configuration and asset count, then of every state array (name, dtype, shape, bytes)."""
        header = {"class": type(self).__name__, "config": self.config, "n_assets": self.n_assets}
        h = hashlib.sha256(json.dumps(header, sort_keys=True).encode())
        for name in sorted(self.state):
            a = np.ascontiguousarray(self.state[name])
            h.update(f"{name}|{a.dtype.str}|{a.shape}|".encode())
            h.update(a.tobytes())
        return h.hexdigest()

    def sidecar(self):
        """JSON record: state and fit-data fingerprints, fit dates, head parities, frozen normalization statistics."""
        return {"interface": INTERFACE, "representation": type(self).__name__, "config": copy.deepcopy(self.config),
                "state_sha256": self.state_hash(), "n_assets": self.n_assets, "odd_head": self.odd_head,
                "heads": copy.deepcopy(self.heads), "channels": copy.deepcopy(self.channels),
                "fit": copy.deepcopy(self.fit_info), "normalization": copy.deepcopy(self.stats)}
