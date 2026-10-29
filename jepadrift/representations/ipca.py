"""IPCA representation (P4-C, P4-D) [Kelly, Pruitt & Su, 2019, Characteristics are covariances]: x_t = C_t Gamma f_t + e_t,
Gamma by ALS on pretrain, K and the whitening on calib, f_t regressed on the observed assets of day t (docs/sections/ipca.md)."""
import copy

import numpy as np

from jepadrift.representations.base import Representation, _check, _sha256

TOL, MAX_ITER, K_MAX, TIE = 1e-10, 10_000, 4, 1e-12
CASH_NEUTRAL = (None, "constant")


def _chars(C, shape):
    if not (isinstance(C, np.ndarray) and C.dtype == np.float64 and C.ndim == len(shape) + 1 and C.shape[:-1] == shape):
        raise ValueError(f"IPCA needs C_t: float64 characteristics of shape {shape} + (P,), got "
                         f"{getattr(C, 'shape', type(C).__name__)}")
    if np.isinf(C).any():
        raise ValueError("C has infinite values")
    return C


def design(x, C, cash_neutral):
    """(C~, x~, m, n_nan) of one day on O_t = {i: x_i finite}: NaN characteristics read as 0 and counted (C-inject-F2-nan);
    cash_neutral "constant" centres C and x by their means over O_t, m = the mean of x over O_t (else 0)."""
    obs = np.isfinite(x)
    c, xo = C[obs], x[obs]
    nan = np.isnan(c)
    c, m = np.where(nan, 0.0, c), 0.0
    if cash_neutral and len(xo):
        m = xo.mean()
        c, xo = c - c.mean(axis=0), xo - m
    return c, xo, m, int(nan.sum())


def usable(c):
    """A day is used iff rank(C~_t) = P, with numpy's SVD tolerance sigma_max max(N_t, P) eps."""
    return len(c) >= c.shape[1] and int(np.linalg.matrix_rank(c)) == c.shape[1]


def segment(X, C, cash_neutral):
    """Normal-equation blocks of the used days, W_t = C~'C~, y_t = C~'x~, N_t, ||x~||^2 and m_t; used mask, NaN imputed."""
    blocks, used, n_nan = [], np.zeros(len(X), dtype=bool), 0
    for t in range(len(X)):
        c, xo, m, k = design(X[t], C[t], cash_neutral)
        n_nan += k
        if usable(c):
            used[t] = True
            blocks.append((c.T @ c, c.T @ xo, len(xo), xo @ xo, m))
    if not blocks:
        raise ValueError("no day of the segment has rank(C~_t) = P")
    W, Y, n, ss, m = (np.array(b, dtype=np.float64) for b in zip(*blocks))
    return {"W": W, "Y": Y, "n": n, "ss": ss, "m": m, "used": used, "c_nan": n_nan}


def factors(W, Y, G):
    """f_t = (G' W_t G)^-1 G' y_t on every row: (T, K)."""
    return np.linalg.solve(G.T @ W @ G, (Y @ G)[..., None])[..., 0]


def objective(W, Y, ss, G):
    """sum_t (||x~_t||^2 - f_t' G' y_t): the residual sum of squares of the observed assets at the optimal f_t."""
    return float(ss.sum() - np.einsum("tk,tk->", factors(W, Y, G), Y @ G))


def normalize(W, Y, G):
    """Basis of span(G) with Gamma'Gamma = I, (1/T) sum f f' diagonal decreasing, largest |entry| of each column > 0."""
    Q = np.linalg.qr(G)[0]
    F = factors(W, Y, Q)
    G = Q @ np.linalg.eigh(F.T @ F / len(F))[1][:, ::-1]
    return G * np.sign(G[np.abs(G).argmax(axis=0), np.arange(G.shape[1])])


def als(W, Y, n, ss, K, G0=None, max_iter=MAX_ITER):
    """ALS for Gamma (P, K) from G0 or the K leading right singular vectors of [y_t / N_t]_t, stopped when
    ||QQ' - Q_Q_'||_F <= TOL; returns (normalized Gamma, {iterations, projector_change, objective trace})."""
    T, P = W.shape[:2]
    Q = np.linalg.qr(np.linalg.svd(Y / n[:, None], full_matrices=False)[2][:K].T if G0 is None else G0)[0]
    trace = []
    for it in range(1, max_iter + 1):
        F = factors(W, Y, Q)
        trace.append(float(ss.sum() - np.einsum("tk,tk->", F, Y @ Q)))
        FF = (F[:, :, None] * F[:, None, :]).reshape(T, K * K)
        lhs = (FF.T @ W.reshape(T, P * P)).reshape(K, K, P, P).transpose(0, 2, 1, 3).reshape(K * P, K * P)
        try:
            G = np.linalg.solve(lhs, (F.T @ Y).reshape(-1)).reshape(K, P).T
        except np.linalg.LinAlgError as err:
            raise ValueError(f"the Gamma step of ALS is singular for K = {K}") from err
        Q_new = np.linalg.qr(G)[0]
        change = float(np.linalg.norm(Q_new @ Q_new.T - Q @ Q.T))
        Q = Q_new
        if change <= TOL:
            break
    else:
        raise RuntimeError(f"ALS did not converge in {max_iter} iterations: projector change {change:.3g} > {TOL:g}")
    G = normalize(W, Y, Q)
    trace.append(objective(W, Y, ss, G))
    return G, {"iterations": it, "projector_change": change, "objective": trace}


def heldout_r2(X, C, used, gammas, cash_neutral):
    """Uncentred R^2 of x~_B by C~_B G f_A, f_A on the observed assets of one index-parity fold A only, both directions
    summed over the used days; (R^2 per G, directions skipped for rank(C~_A) < P)."""
    even = np.arange(X.shape[1]) % 2 == 0
    ssr, sst, skips = np.zeros(len(gammas)), 0.0, 0
    for t in np.flatnonzero(used):
        for a in (even, ~even):
            ca, xa, _, _ = design(np.where(a, X[t], np.nan), C[t], cash_neutral)
            if not usable(ca):
                skips += 1
                continue
            cb, xb, _, _ = design(np.where(a, np.nan, X[t]), C[t], cash_neutral)
            sst += xb @ xb
            for j, G in enumerate(gammas):
                r = xb - cb @ (G @ factors((ca.T @ ca)[None], (ca.T @ xa)[None], G)[0])
                ssr[j] += r @ r
    if not sst > 0:
        raise ValueError("the held-out R^2 needs a positive held-out sum of squares")
    return 1.0 - ssr / sst, skips


class IPCA(Representation):
    """z_odd = W f_t (cash_neutral "constant": [m_t / s_m, W f_t]), W = M^(-1/2) of the uncentred calib second moment of f;
    z = 0 on a day with rank(C~_t) < P."""

    missing = True

    def __init__(self, K="select", K_max=K_MAX, cash_neutral=None):
        if cash_neutral not in CASH_NEUTRAL:
            raise ValueError(f"cash_neutral must be one of {CASH_NEUTRAL}, got {cash_neutral!r}")
        for name, v in (("K", K), ("K_max", K_max)):
            if not (name == "K" and isinstance(v, str) and v == "select") and (
                    isinstance(v, bool) or not isinstance(v, (int, np.integer)) or v < 1):
                raise ValueError(f"{name} must be {'select or ' * (name == 'K')}an int >= 1, got {v!r}")
        self.config = {"K": K if isinstance(K, str) else int(K), "K_max": int(K_max), "cash_neutral": cash_neutral}

    def _target(self):
        return "relative_returns" if self.config["cash_neutral"] else "returns"

    def pretrain(self, X, C, dates):
        """Gamma_K by ALS on the pretrain rows for every candidate K <= min(K_max, P); returns self."""
        _check(X, 2, "X_pretrain", missing=True)
        C = _chars(C, X.shape)
        dates = np.asarray(dates, dtype="datetime64[D]")
        if dates.shape != (len(X),):
            raise ValueError(f"dates must hold one date per row of X ({len(X)}), got shape {dates.shape}")
        K, bound = self.config["K"], min(self.config["K_max"], C.shape[2])
        if K != "select" and K > bound:
            raise ValueError(f"K = {K} is not identifiable: K <= min(K_max, P) = {bound} with P = {C.shape[2]}")
        seg = segment(X, C, self.config["cash_neutral"])
        self.candidates = list(range(1, bound + 1)) if K == "select" else [K]
        self.gammas, runs = {}, {}
        for k in self.candidates:
            self.gammas[k], info = als(seg["W"], seg["Y"], seg["n"], seg["ss"], k)
            runs[str(k)] = {"iterations": info["iterations"], "projector_change": info["projector_change"],
                            "r2_insample": 1.0 - info["objective"][-1] / float(seg["ss"].sum())}
        self.pretrain_info = {"first_day": str(dates[0]), "last_day": str(dates[-1]), "days": len(X),
                              "x_sha256": _sha256(X), "c_sha256": _sha256(C), "n_assets": X.shape[1], "P": C.shape[2],
                              "used_days": int(seg["used"].sum()), "excluded": [str(d) for d in dates[~seg["used"]]],
                              "c_nan_imputed": seg["c_nan"], "r2_target": self._target(), "als": runs}
        return self

    def fit(self, X_fit, C_fit, dates_fit):
        """K by the held-out R^2 and the whitening on the calib rows, Gamma_K from pretrain; returns self."""
        self._fit_dates = np.asarray(dates_fit, dtype="datetime64[D]")
        return super().fit(X_fit, C_fit, dates_fit)

    def _fit(self, X, C):
        if not hasattr(self, "pretrain_info"):
            raise ValueError("IPCA.fit needs IPCA.pretrain first: Gamma comes from the pretrain segment")
        C = _chars(C, X.shape)
        if (X.shape[1], C.shape[2]) != (self.pretrain_info["n_assets"], self.pretrain_info["P"]):
            raise ValueError("the calib assets and characteristics must match the pretrain ones")
        cn = self.config["cash_neutral"]
        seg = segment(X, C, cn)
        gammas = [self.gammas[k] for k in self.candidates]
        r2, skips = heldout_r2(X, C, seg["used"], gammas, cn)
        K = self.candidates[int(np.flatnonzero(r2 >= r2.max() - TIE)[0])]
        F = factors(seg["W"], seg["Y"], self.gammas[K])
        M = F.T @ F / len(F)
        lam, V = np.linalg.eigh(M)
        if not lam.min() > 0:
            raise ValueError("the calib second moment of f is singular")
        self.state = {"Gamma": self.gammas[K], "W": (V / np.sqrt(lam)) @ V.T}
        rcond = [float(np.sqrt((lambda e: e[:, 0] / e[:, -1])(np.linalg.eigvalsh(g.T @ seg["W"] @ g))).min())
                 for g in gammas]
        total = float(seg["ss"].sum())
        self.stats = {"K": K, "candidates": list(self.candidates), "r2_target": self._target(),
                      "r2_heldout_calib": r2.tolist(),
                      "r2_insample_calib": [1.0 - objective(seg["W"], seg["Y"], seg["ss"], g) / total for g in gammas],
                      "fold_skips": [skips] * len(gammas), "min_rcond_calib": rcond,
                      "used_days_calib": int(seg["used"].sum()),
                      "excluded_calib": [str(d) for d in self._fit_dates[~seg["used"]]],
                      "c_nan_imputed_calib": seg["c_nan"], "second_moment": M.tolist()}
        if cn:
            s_m = float(np.sqrt(np.mean(seg["m"] ** 2)))
            if not s_m > 0:
                raise ValueError("the calib RMS of the market mean must be positive")
            self.state["s_market"], self.stats["s_market"] = np.array([s_m]), s_m
        D = K + bool(cn)
        self.heads = {"z_odd": {"dim": D, "parity": "odd", "degree": 1,
                                "definition": ("[m_t / s_m, " if cn else "[") + "W f_t], f_t = (Gamma' C~_t' C~_t Gamma)^-1 "
                                              "Gamma' C~_t' x~_t on O_t; 0 if rank(C~_t) < P"},
                      "z_even": {"dim": D, "parity": "even", "degree": 2, "definition": "z_odd ** 2"}}
        self.channels = {"market": [0], "residual": list(range(1, D))} if cn else {"residual": list(range(D))}

    def _day(self, x, C):
        c, xo, m, _ = design(x, _chars(C, x.shape), self.config["cash_neutral"])
        z = np.zeros(self.heads["z_odd"]["dim"])
        if usable(c):
            f = factors((c.T @ c)[None], (c.T @ xo)[None], self.state["Gamma"])[0]
            z[len(z) - len(f):] = self.state["W"] @ f
            if self.config["cash_neutral"]:
                z[0] = m / self.state["s_market"][0]
        return z, z * z

    def sidecar(self):
        """Base record plus the pretrain record (segment, fingerprints, ALS runs per candidate K)."""
        return {**super().sidecar(), "pretrain": copy.deepcopy(self.pretrain_info)}
