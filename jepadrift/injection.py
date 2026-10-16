"""Drifts injected in return space only (Article C, Appendix B): D6 backgrounds, families F1-F4, exact onsets."""
import hashlib
import json
import math
import operator
from pathlib import Path

import numpy as np

from jepadrift import floors as fl
from jepadrift.stats.covariance import ledoit_wolf

FAMILIES = ("F1", "F2", "F3", "F4-deform", "F4-rotate")
SR_ASSET_B = 1.0


def _check_panel(X, finite):
    if not isinstance(X, np.ndarray):
        raise TypeError(f"expected a returns panel as a numpy array, got {type(X).__name__}; "
                        "latent Z objects are refused")
    if X.ndim != 2 or X.dtype != np.float64:
        raise ValueError(f"returns panel must be 2-D float64, got ndim={X.ndim}, dtype={X.dtype}")
    if finite and not np.isfinite(X).all():
        raise ValueError("returns panel has non-finite values; select a complete sub-panel (assets x days) first")


def symmetrize(X, rng):
    """D6 background: every whole day multiplied by one Rademacher sign; returns (X_sym, eps)."""
    _check_panel(X, finite=False)
    eps = rng.choice((-1.0, 1.0), size=X.shape[0])
    return X * eps[:, None], eps


def fit_background(X_calib, K):
    """Calibration estimates: Ledoit-Wolf sigma, signed eigen-pairs, B = V_K Lambda_K^(1/2), psi = diag(sigma - BB')."""
    _check_panel(X_calib, finite=True)
    sigma, shrinkage = ledoit_wolf(X_calib)
    N = sigma.shape[0]
    if not 1 <= K <= N - 1:
        raise ValueError(f"K must lie in [1, {N - 1}], got {K}")
    eigval, eigvec = np.linalg.eigh(sigma)
    eigval, eigvec = eigval[::-1].copy(), eigvec[:, ::-1]
    eigvec = eigvec * np.where(eigvec.sum(axis=0) < 0, -1.0, 1.0)
    B = eigvec[:, :K] * np.sqrt(eigval[:K])
    psi = np.diag(sigma) - np.sum(B ** 2, axis=1)
    if psi.min() <= 0:
        raise ValueError("residual variances must be positive; reduce K or lengthen the calibration window")
    return {"sigma": sigma, "shrinkage": shrinkage, "eigval": eigval, "eigvec": eigvec, "B": B, "psi": psi}


def gls_residual(A, B, psi):
    """GLS residual of the rows of A on the loadings B with weights 1/psi (Article C, Corollary 1)."""
    coef = np.linalg.solve(B.T @ (B / psi[:, None]), ((A / psi) @ B).T).T
    return A - coef @ B.T


def _unit(rng, k):
    g = rng.standard_normal(k)
    return g / np.linalg.norm(g)


def _info(D, sigma):
    return float(0.5 * np.mean(np.sum(D * np.linalg.solve(sigma, D.T).T, axis=-1)))


def _seed(rng):
    ss = rng.bit_generator.seed_seq
    if ss is None:
        return None
    entropy = ss.entropy
    entropy = [int(e) for e in entropy] if isinstance(entropy, (list, tuple, np.ndarray)) else int(entropy)
    return {"entropy": entropy, "spawn_key": [int(k) for k in ss.spawn_key]}


def _characteristics(params, T, N):
    C = params.get("C")
    if not isinstance(C, np.ndarray) or C.ndim != 3 or C.shape[:2] != (T, N) or C.dtype != np.float64:
        raise ValueError(f"F2 needs params['C'], a float64 array of shape ({T}, {N}, P) aligned with X")
    if np.isinf(C).any():
        raise ValueError("characteristics contain +-inf")
    return C


def inject(X, family, tau_star, I_target, params, rng):
    """Inject `family` from row tau_star on, earlier rows untouched; returns (X_tilde, delta, meta)."""
    _check_panel(X, finite=True)
    T, N = X.shape
    if family not in FAMILIES:
        raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")
    tau = operator.index(tau_star)
    if not 0 <= tau < T:
        raise ValueError(f"tau_star must lie in [0, {T}), got {tau}")
    if "calib" not in params:
        raise ValueError("params['calib'] = (start, stop) rows of the calibration window is required")
    start, stop = (operator.index(v) for v in params["calib"])
    if not (0 <= start and stop <= T and stop - start >= 2):
        raise ValueError(f"calibration rows [{start}, {stop}) must hold at least 2 rows within [0, {T})")
    if family in ("F1", "F2") and params.get("K") is None:
        raise ValueError(f"{family} needs params['K'], the number of PCA factors")
    if family.startswith("F4"):
        if I_target is not None:
            raise ValueError("F4 takes its amplitude from params (r or theta_deg); pass I_target=None")
    elif I_target is not None and not I_target > 0:
        raise ValueError(f"I_target must be positive (convention a) or None (convention b), got {I_target}")
    convention = None if family.startswith("F4") else "a" if I_target is not None else "b"
    if family == "F2":
        C = _characteristics(params, T, N)
        if convention == "b" and not (params.get("kappa") or 0) > 0:
            raise ValueError("F2 under convention (b) needs params['kappa'] > 0")
    K = params.get("K", 1) if family in ("F1", "F2") else 1
    fit = fit_background(X[start:stop], K)
    sigma = fit["sigma"]
    if family.startswith("F4"):
        return _second_order(X, family, tau, params, fit, rng, start, stop)
    meta_extra = {}
    if family == "F1":
        coef = _unit(rng, fit["B"].shape[1])
        D = fit["B"] @ coef
    elif family == "F2":
        missing = np.isnan(C)
        coef = _unit(rng, C.shape[2])
        D = gls_residual(np.where(missing, 0.0, C) @ coef, fit["B"], fit["psi"])
        meta_extra["c_nan_imputed"] = int(missing.sum())
    else:
        coef = np.ones(1)
        D = fit["eigvec"][:, 0] * math.sqrt(fit["eigval"][0])
    D_ref = D[start:stop] if family == "F2" else D
    q = _info(D_ref, sigma)
    if not q > 0:
        raise ValueError("drift direction carries no information under the calibration covariance")
    if convention == "a":
        s = math.sqrt(I_target / q)
        amplitude = {"I_target": float(I_target), "sr": fl.sharpe_from_kl(I_target)}
    else:
        kappa = float(params["kappa"]) if family == "F2" else None
        sharpe = math.sqrt(fl.TRADING_DAYS) * D_ref / np.sqrt(np.diag(sigma))
        s = SR_ASSET_B * (kappa if family == "F2" else 1.0) / math.sqrt(np.mean(sharpe ** 2))
        amplitude = {"kappa": kappa, "sr_asset": SR_ASSET_B}
    delta = s * (D[tau:] if family == "F2" else D)
    X_tilde = X.copy()
    X_tilde[tau:] += delta
    meta = {"family": family, "tau_star": tau, "convention": convention, "amplitude": amplitude, "seed": _seed(rng),
            "direction": (s * coef).tolist(), "direction_sha256": _sha256(delta), "info": _info(s * D_ref, sigma),
            "K": int(K) if family in ("F1", "F2") else None, "calib": [start, stop],
            "shrinkage": fit["shrinkage"], **meta_extra}
    return X_tilde, delta, meta


def _sha256(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def _second_order(X, family, tau, params, fit, rng, start, stop):
    """F4: X_tilde[tau:] = X[tau:] @ M.T, M an eigen-subspace deformation or a Givens rotation of two eigenvectors."""
    N = X.shape[1]
    V = fit["eigvec"]
    if family == "F4-deform":
        if "subspace" not in params or "r" not in params:
            raise ValueError("F4-deform needs params['subspace'] (eigenvector indices) and params['r'] > 0")
        sub = [operator.index(k) for k in params["subspace"]]
        r = float(params["r"])
        if not sub or len(set(sub)) != len(sub) or not all(0 <= k < N for k in sub) or not r > 0:
            raise ValueError(f"need distinct eigenvector indices in [0, {N}) and r > 0, got {sub}, {r}")
        E = (math.sqrt(r) - 1.0) * (V[:, sub] @ V[:, sub].T)
        amplitude = {"r": r, "subspace": sub}
    else:
        if "pair" not in params or "theta_deg" not in params:
            raise ValueError("F4-rotate needs params['pair'] = (i, j) and params['theta_deg']")
        i, j = (operator.index(k) for k in params["pair"])
        if i == j or not (0 <= i < N and 0 <= j < N):
            raise ValueError(f"need two distinct eigenvector indices in [0, {N}), got {i}, {j}")
        theta = math.radians(float(params["theta_deg"]))
        u, w = V[:, i], V[:, j]
        E = ((math.cos(theta) - 1.0) * (np.outer(u, u) + np.outer(w, w))
             + math.sin(theta) * (np.outer(w, u) - np.outer(u, w)))
        amplitude = {"theta_deg": float(params["theta_deg"]), "pair": [i, j]}
    M = np.eye(N) + E
    sigma = fit["sigma"]
    info = 0.5 * (2.0 * np.trace(E) + np.trace(np.linalg.solve(sigma, E @ sigma @ E.T)) - 2.0 * np.linalg.slogdet(M)[1])
    X_tilde = X.copy()
    X_tilde[tau:] = X[tau:] @ M.T
    meta = {"family": family, "tau_star": tau, "convention": None, "amplitude": amplitude, "seed": _seed(rng),
            "direction": None, "direction_sha256": _sha256(M), "info": float(info), "K": None, "calib": [start, stop],
            "shrinkage": fit["shrinkage"]}
    return X_tilde, M, meta


def draw_tau_star(t0, t_end, h_ref, h_det, rng):
    """Onset tau* drawn uniformly on the integers [t0 + h_ref, t_end - h_det], both bounds included."""
    lo, hi = t0 + h_ref, t_end - h_det
    if lo > hi:
        raise ValueError(f"empty onset range [{lo}, {hi}]")
    return int(rng.integers(lo, hi + 1))


def write_tau_star(path, records):
    """Write a tau_star.json record (dict) or a list of records: sorted keys, indent 2, trailing newline."""
    Path(path).write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
