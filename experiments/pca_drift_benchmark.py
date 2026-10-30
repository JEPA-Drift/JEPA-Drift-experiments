"""Stream 28: PCA spectral prefixes versus information-selected subsets on mean and covariance drifts.

Plan prompts/plans/plan-28.md (GO prompts/GO-stream-28.md); output schema docs/sections/pca_drift_benchmark.md.
Synthetic backgrounds: equicorrelated i.i.d. Gaussian and multivariate Student t7 panels, a frozen Ledoit-Wolf PCA
fitted on an independent sample, independent centering, calibration, holdout-null and alternative roles shared by
every method. Real D3 rows are read up to 2019-12-31 only; post-2019 evaluations stay BLOCKED_PRE_J4.

Usage: python experiments/pca_drift_benchmark.py --mode smoke --dataset synthetic --out DIR --log-dir DIR
"""
import os

REQUIRED_ENV = {"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                "MKL_CBWR": "COMPATIBLE", "PYTHONHASHSEED": "42"}
ENV_AT_START = {_var: os.environ.get(_var) for _var in REQUIRED_ENV}
for _var, _value in REQUIRED_ENV.items():
    if _var != "PYTHONHASHSEED":
        os.environ.setdefault(_var, _value)

import argparse
import hashlib
import importlib
import itertools
import json
import math
import resource
import subprocess
import sys
import time
import zlib
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import injection, sim
from jepadrift import pipelines as pl
from jepadrift.monitors.calibration import null_windows
from jepadrift.monitors.cusum import cusum_trajectory_vec, strict_cusum_vec
from jepadrift.monitors.streams import energy_stream
from jepadrift.representations.extract import segment_rows
from jepadrift.representations.pca import pca_directions
from jepadrift.stats.intervals import wilson

STREAM = 28
SCHEMA_VERSION = "pca_drift_benchmark/2"
THRESHOLD_RULE = "predictive_exchangeable_rank_v2"
GUARANTEE = {"SYNTH_INDEPENDENT_PATHS": "EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA",
             "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS": "NOT_ESTABLISHED_HISTORICAL_WINDOWS"}
REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "pca_drift_benchmark.yaml"
SEED_ROLES = ("fit", "centering", "calibration", "holdout_null", "alternative")
COUNT_KEYS = ("n_center", "n_cal", "n_null", "n_alt")
MIXTURE_MAX_DOUBLINGS = 200
MAX_COV_CHUNK = 20000
COV_BATCH_DOUBLES = 6
SEED_DOMAINS = ("path", "inject", "real_null")


class CalibrationFailed(ValueError):
    """A calibration that cannot produce a finite threshold (status CALIBRATION_FAILED)."""


class InsufficientCalibration(CalibrationFailed):
    """n calibration maxima admit no predictive rank at alpha (floor(alpha (n + 1)) - 1 < 0): no threshold, no bound."""


def mixture_cost(d, gamma):
    """M(d, gamma) = x / ln(gamma), x the unique root above ln(gamma) of x = ln(gamma) + (d/2) log1p(2x/d): the fluid
    surrogate of a matched-prior Gaussian mixture, never an exact delay, RMST or ARL0. The bracket [ln(gamma), hi] is
    found by doubling hi, every bound and evaluation checked finite; no finite bracket raises ArithmeticError."""
    if (isinstance(d, bool) or not isinstance(d, (int, np.integer)) or not 1 <= d < 2 ** 53
            or not (math.isfinite(gamma) and gamma > 1)):
        raise ValueError(f"need an integer 1 <= d < 2**53 and a finite gamma > 1, got d={d!r}, gamma={gamma!r}")
    a, d = math.log(gamma), int(d)

    def f(x):
        return x - a - 0.5 * d * math.log1p(2.0 * x / d)

    hi, doublings = 2.0 * a, 0
    f_hi = f(hi)
    while math.isfinite(f_hi) and f_hi <= 0.0 and doublings < MIXTURE_MAX_DOUBLINGS:
        hi, doublings = 2.0 * hi, doublings + 1
        f_hi = f(hi) if math.isfinite(hi) else math.nan
    f_lo = f(a)
    if not (math.isfinite(f_lo) and f_lo < 0.0 and math.isfinite(hi) and math.isfinite(f_hi) and f_hi > 0.0):
        raise ArithmeticError(f"no finite bracket of the mixture root for d = {d}, gamma = {gamma} after {doublings} "
                              f"doublings: f({a!r}) = {f_lo!r}, f({hi!r}) = {f_hi!r}")
    x = brentq(f, a, hi, xtol=1e-13, rtol=4.0 * np.finfo(np.float64).eps, maxiter=500)
    if not (math.isfinite(x) and x > a):
        raise ArithmeticError(f"mixture root {x!r} is not finite above ln(gamma) = {a!r}")
    return x / a


def affine_costs(gamma):
    """Affine surrogate C(d) = a + c d: the chord of M(., gamma) between d = 1 and d = 20, fixed before any data."""
    m1, m20 = mixture_cost(1, gamma), mixture_cost(20, gamma)
    c = (m20 - m1) / 19.0
    a = m1 - c
    if not (a > 0.0 and c > 0.0):
        raise ArithmeticError(f"affine chord needs a, c > 0, got a={a!r}, c={c!r}")
    return a, c


def cost_tables(gamma, nmax):
    """(M(d, gamma), a + c d) for d = 1..nmax; the affine chord does not depend on nmax."""
    a, c = affine_costs(gamma)
    d = np.arange(1, nmax + 1)
    return np.array([mixture_cost(int(k), gamma) for k in d]), a + c * d


def q_plugin(beta, lam):
    """Plug-in Ledoit-Wolf Gaussian information per axis: mu = beta / sqrt(lam), q = mu**2 / 2."""
    mu = np.asarray(beta, dtype=np.float64) / np.sqrt(np.asarray(lam, dtype=np.float64))
    return 0.5 * mu * mu


def kl_mean(mu, C):
    """0.5 mu' C^{-1} mu: Gaussian KL of a mean shift mu under covariance C, both in the same coordinates."""
    mu = np.asarray(mu, dtype=np.float64)
    return float(0.5 * mu @ np.linalg.solve(np.asarray(C, dtype=np.float64), mu))


def clip_kl(raw):
    """(values, n_clipped): -1e-12 max(1, |I|) <= I < 0 becomes 0; a larger negative value raises ArithmeticError."""
    v = np.asarray(raw, dtype=np.float64)
    if (v < -1e-12 * np.maximum(1.0, np.abs(v))).any():
        raise ArithmeticError(f"material negative Gaussian KL {v.min()!r}")
    return np.where(v < 0.0, 0.0, v), int((v < 0.0).sum())


def kl_cov_raw(A0, A1):
    """0.5 [tr(A0^{-1} A1) - logdet(A0^{-1} A1) - d] over stacks (..., d, d) of SPD matrices, before clipping."""
    A0, A1 = np.asarray(A0, dtype=np.float64), np.asarray(A1, dtype=np.float64)
    s0, l0 = np.linalg.slogdet(A0)
    s1, l1 = np.linalg.slogdet(A1)
    if not ((s0 > 0).all() and (s1 > 0).all()):
        raise ValueError("covariance matrices must be positive definite")
    tr = np.trace(np.linalg.solve(A0, A1), axis1=-2, axis2=-1)
    return 0.5 * (tr - (l1 - l0) - A0.shape[-1])


def kl_cov_batch(A0, A1):
    """Joint Gaussian covariance KL of each pair of a stack (clipping rule of clip_kl); never a sum of marginals."""
    return clip_kl(kl_cov_raw(A0, A1))[0]


def kl_cov(C0, C1):
    """Joint Gaussian KL 0.5 [tr(C0^{-1} C1) - logdet(C0^{-1} C1) - d] of a covariance change."""
    return float(kl_cov_batch(np.asarray(C0)[None], np.asarray(C1)[None])[0])


def cov_marginals(C0, C1):
    """Marginal Gaussian KL 0.5 (r - 1 - ln r), r = C1_kk / C0_kk: a per-axis diagnostic, never a joint KL."""
    r = np.diag(C1) / np.diag(C0)
    return 0.5 * (r - 1.0 - np.log(r))


def llr_mean(Z, mu, C0):
    """Gaussian log-likelihood ratio of N(mu, C0) against N(0, C0) for each row of Z."""
    w = np.linalg.solve(C0, mu)
    return np.asarray(Z, dtype=np.float64) @ w - 0.5 * float(mu @ w)


def llr_cov(Z, C0, C1):
    """Gaussian log-likelihood ratio of N(0, C1) against N(0, C0) for each row of Z."""
    Z = np.asarray(Z, dtype=np.float64)
    D = np.linalg.inv(C1) - np.linalg.inv(C0)
    return -0.5 * np.einsum("...i,ij,...j->...", Z, D, Z) - 0.5 * (np.linalg.slogdet(C1)[1] - np.linalg.slogdet(C0)[1])


def _prefix(Z, s2):
    Z = np.asarray(Z, dtype=np.float64)
    if Z.ndim != 3 or Z.shape[1] < 1 or Z.shape[2] < 1 or not np.isfinite(Z).all():
        raise ValueError(f"Z must be a finite (B, H, p) array with H, p >= 1, got shape {Z.shape}")
    if not (math.isfinite(s2) and s2 > 0.0):
        raise ValueError(f"s2 must be finite and positive, got {s2!r}")
    B, H, p = Z.shape
    S = np.zeros((B, H + 1, p))
    np.cumsum(Z, axis=1, out=S[:, 1:])
    n = np.arange(1, H + 1, dtype=np.float64)
    return S, -0.5 * p * np.log1p(n * s2), s2 / (2.0 * (1.0 + n * s2))


def _scan_rows(S, a, b, t):
    D = S[:, t, None, :] - S[:, :t, :]
    return a[t - 1::-1] + b[t - 1::-1] * (D * D).sum(axis=-1)


def scan_statistic(Z, s2, h=None):
    """W_t = max over every start 1 <= tau <= t of logL(tau, t) = -(p/2) log1p(n s2) + s2 |S_t - S_{tau-1}|^2 /
    (2 (1 + n s2)), n = t - tau + 1, for Z (B, H, p); first_hit = first t (1-based) with W_t >= h, -1 if none.
    No window, no GLR, no O(1) recursion; with h set the loop stops once every path has alarmed (W NaN after)."""
    S, a, b = _prefix(Z, s2)
    B, H = S.shape[0], S.shape[1] - 1
    W = np.full((B, H), np.nan)
    first = np.full(B, -1, dtype=np.int64)
    for t in range(1, H + 1):
        W[:, t - 1] = _scan_rows(S, a, b, t).max(axis=1)
        if h is not None:
            hit = (first < 0) & (W[:, t - 1] >= h)
            first[hit] = t
            if (first >= 0).all():
                break
    return W, first


def segment_loglik(z, s2):
    """logL(tau, t) of one path z (H, p) by the scan kernel: row t - 1, column tau - 1, NaN for tau > t."""
    S, a, b = _prefix(np.asarray(z, dtype=np.float64)[None], s2)
    H = S.shape[1] - 1
    out = np.full((H, H), np.nan)
    for t in range(1, H + 1):
        out[t - 1, :t] = _scan_rows(S, a, b, t)[0]
    return out


def predictive_rank(n, alpha):
    """r = floor(alpha (n + 1)) - 1 with exact decimal alpha: the largest r with (r + 1)/(n + 1) <= alpha (-1 if none)."""
    return math.floor(Fraction(str(alpha)) * (n + 1)) - 1


def predictive_bound(r, n):
    """(r + 1)/(n + 1): bound on P(new maximum > b) for exchangeable calibration and new maxima, ties conservative."""
    return (r + 1) / (n + 1)


def min_calibration_n(alpha):
    """Smallest number of calibration maxima with a predictive rank r >= 0 at alpha: ceil(1/alpha) - 1."""
    return math.ceil(1 / Fraction(str(alpha))) - 1


def rank_threshold(maxima, alpha, rule):
    """(threshold, r, alarms) by the predictive exchangeable rank r = predictive_rank(n, alpha), b = sorted(maxima)
    [n - r - 1]; GT alarms iff m > b (threshold b), GE iff m >= nextafter(b, +inf). If the n calibration maxima and a
    new maximum are exchangeable, P(new > b) <= (r + 1)/(n + 1) <= alpha; r < 0 raises InsufficientCalibration."""
    m = np.asarray(maxima, dtype=np.float64)
    if m.ndim != 1 or m.size == 0 or not np.isfinite(m).all():
        raise ValueError("maxima must be a non-empty finite 1-D array")
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError(f"alpha must lie in (0, 1), got {alpha!r}")
    if rule not in ("GE", "GT"):
        raise ValueError(f"rule must be 'GE' or 'GT', got {rule!r}")
    n = m.size
    r = predictive_rank(n, alpha)
    if r < 0:
        raise InsufficientCalibration(
            f"n = {n} calibration maxima admit no predictive rank at alpha = {alpha}: floor(alpha (n + 1)) - 1 = {r} < 0; "
            f"at least {min_calibration_n(alpha)} are needed")
    b = float(np.sort(m)[n - r - 1])
    with np.errstate(over="ignore"):
        h = b if rule == "GT" else float(np.nextafter(b, np.inf))
    if not math.isfinite(h):
        raise CalibrationFailed(f"threshold above {b!r} is not finite")
    alarms = int((m > b).sum())
    if alarms > r:
        raise ArithmeticError(f"{alarms} calibration alarms exceed the rank budget {r}")
    return h, r, alarms


def vech_std(A):
    """Half-vectorization (..., d, d) -> (..., d(d+1)/2): diagonal / sqrt(2), then the upper off-diagonal row-major."""
    A = np.asarray(A, dtype=np.float64)
    iu = np.triu_indices(A.shape[-1], 1)
    return np.concatenate([np.diagonal(A, axis1=-2, axis2=-1) / math.sqrt(2.0), A[..., iu[0], iu[1]]], axis=-1)


def vech_stream(Z, C0):
    """Quadratic covariance stream y = vech_std(z z' - C0) of the rows of Z (..., d), C0 the frozen (d, d) centering:
    p = d (d + 1) / 2 coordinates, not presumed Gaussian isotropic (the scan on it is a calibrated quasi-likelihood)."""
    Z, C0 = np.asarray(Z, dtype=np.float64), np.asarray(C0, dtype=np.float64)
    d = Z.shape[-1]
    if C0.shape != (d, d):
        raise ValueError(f"the centering must be ({d}, {d}) for {d}-dimensional scores, got {C0.shape}")
    Y = vech_std(Z[..., :, None] * Z[..., None, :] - C0)
    if Y.shape[-1] != d * (d + 1) // 2:
        raise ArithmeticError(f"quadratic stream has {Y.shape[-1]} coordinates, expected d (d + 1) / 2 = {d * (d + 1) // 2}")
    return Y


def equicorrelation(N, rho):
    """Sigma0 = (1 - rho) I + rho 11'."""
    return (1.0 - rho) * np.eye(N) + rho * np.ones((N, N))


def equicorrelation_inverse(N, rho):
    """Sherman-Morrison inverse of Sigma0: (I - rho / (1 - rho + N rho) 11') / (1 - rho)."""
    return (np.eye(N) - rho / (1.0 - rho + N * rho) * np.ones((N, N))) / (1.0 - rho)


def rotation(X_fit, theta_deg, rng):
    """Givens rotation M of the first two Ledoit-Wolf eigenvectors of X_fit by theta (injection F4-rotate)."""
    fit = injection.fit_background(X_fit, 1)
    params = {"calib": (0, X_fit.shape[0]), "fit": fit, "pair": (0, 1), "theta_deg": float(theta_deg)}
    return injection.inject(X_fit, "F4-rotate", 0, None, params, rng)[1]


def _is_int(v):
    return isinstance(v, (int, np.integer)) and not isinstance(v, bool)


def load_config(path, mode):
    """Configuration with the smoke block merged when mode == 'smoke' (it may change the four role counts only)."""
    if mode not in ("smoke", "full"):
        raise ValueError(f"mode must be 'smoke' or 'full', got {mode!r}")
    cfg = yaml.safe_load(Path(path).read_text())
    smoke = cfg.pop("smoke")
    if set(smoke) - set(COUNT_KEYS):
        raise ValueError(f"the smoke block may only change {COUNT_KEYS}, got {sorted(smoke)}")
    if mode == "smoke":
        cfg["full_counts"] = {k: cfg[k] for k in COUNT_KEYS}
        cfg.update(smoke)
    cfg["mode"] = mode
    return cfg


def validate_config(cfg):
    """Refuse a schema_version other than SCHEMA_VERSION, invalid dimensions, role counts, alpha, gamma, minibatch,
    search chunk and non-finite or non-positive resource limits (ValueError)."""
    N, nmax, H, T = cfg["N"], cfg["nmax"], cfg["H"], cfg["T_fit"]
    res = cfg["resources"]
    checks = [(cfg.get("schema_version") == SCHEMA_VERSION, f"schema_version == {SCHEMA_VERSION!r}"),
              (_is_int(N) and N >= 2, "N >= 2"),
              (_is_int(N) and _is_int(nmax) and 1 <= nmax <= min(20, N - 1), "1 <= nmax <= min(20, N - 1)"),
              (_is_int(H) and H >= 1, "H >= 1"), (_is_int(T) and T >= 2, "T_fit >= 2"),
              (all(_is_int(cfg[k]) and cfg[k] >= 1 for k in COUNT_KEYS), f"{COUNT_KEYS} >= 1"),
              (0.0 < float(cfg["alpha"]) < 1.0, "0 < alpha < 1"), (float(cfg["gamma_M"]) > 1.0, "gamma_M > 1"),
              (_is_int(cfg["minibatch"]) and cfg["minibatch"] >= 1, "minibatch >= 1"),
              (_is_int(cfg["cov_search_chunk"]) and 1 <= cfg["cov_search_chunk"] <= MAX_COV_CHUNK,
               f"1 <= cov_search_chunk <= {MAX_COV_CHUNK}"),
              (_is_int(cfg["seed"]) and 0 <= cfg["seed"] < 2 ** 32, "0 <= seed < 2**32"),
              (math.isfinite(float(res["mem_limit_gib"])) and float(res["mem_limit_gib"]) > 0.0
               and math.isfinite(float(res["max_wall_minutes"])) and float(res["max_wall_minutes"]) > 0.0,
               "resource limits finite and > 0"),
              (0.0 <= float(cfg["synthetic"]["rho"]) < 1.0, "0 <= rho < 1")]
    failed = [msg for ok, msg in checks if not ok]
    if failed:
        raise ValueError("invalid configuration: " + "; ".join(failed))


def c_supported(cfg):
    """True iff the axes of scenario C lie in [2, nmax] (C is UNSUPPORTED otherwise)."""
    lo, hi = cfg["synthetic"]["C_axes"]
    return _is_int(lo) and _is_int(hi) and 2 <= lo <= hi <= cfg["nmax"]


def label_code(label):
    """CRC32 code of a seed-key label; its injectivity is checked on each run's finite vocabulary (seed_plan), not assumed."""
    return zlib.crc32(label.encode())


def seed_key(root, *parts):
    """SeedSequence entropy [28, root, *parts], string parts replaced by label_code (CRC32)."""
    return [STREAM, int(root), *(label_code(p) if isinstance(p, str) else int(p) for p in parts)]


def entropy_words(key):
    """Canonical SeedSequence entropy of a key of uint32 words: padded with zeros to the pool size 4, under which
    SeedSequence([x]) and SeedSequence([x, 0]) coincide."""
    words = [int(w) for w in key]
    if not all(0 <= w < 2 ** 32 for w in words):
        raise ValueError(f"seed-key words must lie in [0, 2**32), got {words}")
    return tuple(words + [0] * (4 - len(words)))


def check_entropies(keys):
    """Raise ValueError if two seed keys have the same canonical SeedSequence entropy."""
    canonical = [entropy_words(k) for k in keys]
    if len(set(canonical)) != len(canonical):
        raise ValueError("SeedSequence entropy collision among the planned seed keys")
    return canonical


def seed_plan(cfg, real):
    """Every seed key a run draws (roles fit, centering, calibration, holdout_null, alternative per background, the
    rotation key, and the real D6 nulls if real), checked before any draw: label_code injective on the run's label
    vocabulary and canonical entropies unique; a collision raises ValueError and no seed is changed."""
    backgrounds = list(cfg["synthetic"]["backgrounds"])
    vocab = sorted(set(SEED_DOMAINS) | set(backgrounds) | set(SEED_ROLES) | {"B"} | (set(COHORTS) if real else set()))
    codes = {}
    for label in vocab:
        codes.setdefault(label_code(label), []).append(label)
    clash = sorted(v for v in codes.values() if len(v) > 1)
    if clash:
        raise ValueError(f"CRC32 collision among the seed labels {clash}: rename a label; no seed is changed")
    counts = {"fit": 1, "centering": cfg["n_center"], "calibration": cfg["n_cal"], "holdout_null": cfg["n_null"],
              "alternative": cfg["n_alt"]}
    keys = [("path", bg, role, i) for bg in backgrounds for role in SEED_ROLES for i in range(counts[role])]
    keys += [("inject", bg, "B") for bg in backgrounds] + ([("real_null", c) for c in COHORTS] if real else [])
    canonical = check_entropies([seed_key(cfg["seed"], *k) for k in keys])
    return {"n_keys": len(keys), "keys": keys, "vocabulary": {label: label_code(label) for label in vocab},
            "sha256": hashlib.sha256(canon([list(c) for c in canonical]).encode()).hexdigest()}


def rng(root, *parts):
    """Local generator keyed on SeedSequence(seed_key(root, *parts)); no global state."""
    return np.random.default_rng(np.random.SeedSequence(seed_key(root, *parts)))


def draw_path(cfg, background, role, i, T):
    """Synthetic path (T, N): i.i.d. equicorrelated rows, Gaussian or multivariate t (one chi2 per day, unit variance)."""
    nu = cfg["synthetic"]["backgrounds"][background]
    return sim.garch_panel(T, cfg["N"], 0.0, 0.0, nu, rng(cfg["seed"], "path", background, role, i),
                           factor_rho=cfg["synthetic"]["rho"], burn=0)


def array_sha256(*arrays):
    """SHA-256 of the shapes and float64 bytes of the arrays, in order."""
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a, dtype=np.float64)
        h.update(f"{a.shape}|".encode())
        h.update(a.tobytes())
    return h.hexdigest()


def canon(obj):
    """Canonical JSON: sorted keys, compact separators."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha16(obj):
    """First 16 hex digits of the SHA-256 of the canonical JSON of obj."""
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


def S_json(axes0):
    """Canonical subset text: sorted 1-based axis indices as compact JSON."""
    return json.dumps(sorted(int(a) + 1 for a in axes0), separators=(",", ":"))


def parse_S(text, nmax):
    """Strict parser of S_json: non-empty, integers, strictly increasing, within [1, nmax]."""
    S = json.loads(text)
    if (not isinstance(S, list) or not S or not all(_is_int(a) for a in S) or S != sorted(set(S))
            or S[0] < 1 or S[-1] > nmax):
        raise ValueError(f"invalid axis subset {text!r} for nmax = {nmax}")
    return S


def cpv90(eigval):
    """First k (1-based) whose cumulative share of the full Ledoit-Wolf trace reaches 0.9."""
    cpv = np.cumsum(eigval) / np.sum(eigval)
    return int(np.argmax(cpv >= 0.9)) + 1


def cpv90_status(k90, nmax):
    """CPV90_IN_TOP20 if the full-spectrum CPV90 cutoff lies among the nmax candidate axes, else CPV90_OUTSIDE_TOP20."""
    return "CPV90_IN_TOP20" if k90 <= nmax else "CPV90_OUTSIDE_TOP20"


def fit_basis(X_fit):
    """Frozen Ledoit-Wolf PCA of the fit rows: covariance eigen-pairs and CPV, sample-correlation eigenvalues (MP edge,
    Kaiser), fingerprints."""
    eigval, eigvec, _, stats = pca_directions(X_fit, "mp", "full", "ledoit_wolf")
    lam_corr = np.linalg.eigvalsh(np.corrcoef(X_fit, rowvar=False))[::-1].copy()
    if int((lam_corr > stats["mp_edge"]).sum()) != stats["n_above_edge"]:
        raise ArithmeticError("correlation eigenvalues disagree with mp_count")
    eigvec = np.ascontiguousarray(eigvec)
    return {"eigval": eigval, "eigvec": eigvec, "lambda_corr": lam_corr, "mp_edge": stats["mp_edge"],
            "mp_count": stats["n_above_edge"], "kaiser_count": int((lam_corr >= 1.0).sum()),
            "cpv": np.cumsum(eigval) / eigval.sum(), "cpv90_k_full": cpv90(eigval), "lw_shrinkage": stats["shrinkage"],
            "trace_lw": stats["trace"], "basis_hash": array_sha256(eigval, eigvec), "x_fit_sha256": array_sha256(X_fit),
            "T_fit": int(X_fit.shape[0]), "N": int(X_fit.shape[1])}


def spectra_rows(basis, common, nmax, sigma0=None, extra=None):
    """One spectra.csv row per k = 1..N: LW eigenvalue and CPV, correlation eigenvalue with MP and Kaiser flags."""
    lam, lam_corr, N = basis["eigval"], basis["lambda_corr"], basis["N"]
    pop = ((sigma0 @ basis["eigvec"]) * basis["eigvec"]).sum(axis=0) if sigma0 is not None else np.full(N, np.nan)
    status = cpv90_status(basis["cpv90_k_full"], nmax)
    return [{**common, **(extra or {}), "k": k, "basis_hash": basis["basis_hash"], "N": N, "T_fit": basis["T_fit"],
             "lw_shrinkage": basis["lw_shrinkage"], "trace_lw": basis["trace_lw"], "lambda_lw": float(lam[k - 1]),
             "whitening_scale": math.sqrt(lam[k - 1]), "cpv_lw": float(basis["cpv"][k - 1]),
             "lambda_corr": float(lam_corr[k - 1]), "mp_edge": basis["mp_edge"],
             "mp_above": bool(lam_corr[k - 1] > basis["mp_edge"]), "mp_count": basis["mp_count"],
             "kaiser_ge1": bool(lam_corr[k - 1] >= 1.0), "kaiser_count": basis["kaiser_count"],
             "cpv90_k_full": basis["cpv90_k_full"], "cpv90_status": status, "pop_var_axis": float(pop[k - 1]),
             "null_var_z": float(pop[k - 1] / lam[k - 1]), "x_fit_sha256": basis["x_fit_sha256"]}
            for k in range(1, N + 1)]


def scenario_A(V, sigma0, sr_annual):
    """Market mean shift along the frozen v1 with population-standardized projected Sharpe sr_annual:
    beta = (sr / sqrt(252)) sqrt(v1' Sigma0 v1) e_1, Delta = V beta (marginal Gaussian KL sr^2 / 504)."""
    v1 = V[:, 0]
    beta = np.zeros(V.shape[1])
    beta[0] = sr_annual / math.sqrt(252.0) * math.sqrt(float(v1 @ sigma0 @ v1))
    return beta, V @ beta


def scenario_C(V, sigma0_inv, axes, I_target):
    """Residual mean shift with equal coefficients c on the frozen axes lo..hi (1-based), normalized on the declared
    population covariance: 0.5 Delta' Sigma0^{-1} Delta = I_target; returns (beta, Delta = V beta, c)."""
    lo, hi = axes
    u = V[:, lo - 1:hi].sum(axis=1)
    c = math.sqrt(2.0 * I_target / float(u @ sigma0_inv @ u))
    beta = np.zeros(V.shape[1])
    beta[lo - 1:hi] = c
    return beta, V @ beta, c


def select_top_q(q, k, cost):
    """Top-d plug-in subsets of P_k (order: q descending, then axis) for every d = 1..k, and the d maximizing
    V(d) = I(d) / cost[d - 1] (ties: smallest d); exact for an additive objective under a cardinality cost."""
    q = np.asarray(q, dtype=np.float64)[:k]
    order = sorted(range(k), key=lambda j: (-q[j], j))
    I = np.cumsum(q[order])
    V = I / np.asarray(cost, dtype=np.float64)[:k]
    winners = np.flatnonzero(V == V.max())
    d = int(winners[0]) + 1
    tie = winners.size > 1 or (d < k and q[order[d - 1]] == q[order[d]])
    cand = [{"d": j + 1, "S": sorted(order[:j + 1]), "I": float(I[j]), "V": float(V[j])} for j in range(k)]
    return cand, {"d": d, "S": sorted(order[:d]), "I": float(I[d - 1]), "V": float(V[d - 1]),
                  "tie_broken": bool(tie), "rank_order": order}


def cov_batch_bytes(d):
    """Bytes one d-subset may occupy in a search batch: COV_BATCH_DOUBLES (d, d) float64 arrays (two extractions, the
    solve output and the LU copies of solve and slogdet)."""
    return COV_BATCH_DOUBLES * 8 * d * d


def exhaustive_cov(C0, C1, nmax, chunk, check=None, mem_bytes=None):
    """Exact joint-KL maximizer over every subset of the axes 0..nmax-1 for every reservoir k and cardinality d:
    ({(k, d): (I_cov_joint, sorted S)}, clipped count); ties go to the lexicographically first subset. Each subset is
    evaluated once, in (batch, d, d) batches of at most min(chunk, floor(mem_bytes / cov_batch_bytes(d))) subsets (an
    integer; a non-finite mem_bytes raises ValueError), and its value serves every k; check(stage) runs before every
    batch (ResourceBlocked stops the search, never an approximation)."""
    if nmax > 20:
        raise ValueError(f"the exhaustive covariance search is limited to nmax <= 20, got {nmax}")
    if not (_is_int(chunk) and 1 <= chunk <= MAX_COV_CHUNK):
        raise ValueError(f"chunk must be an integer in [1, {MAX_COV_CHUNK}], got {chunk!r}")
    if mem_bytes is not None and not math.isfinite(mem_bytes):
        raise ValueError(f"mem_bytes must be finite, got {mem_bytes!r}")
    # ponytail: exhaustive over 2^nmax subsets; a beam search reported with selection_exact=False if nmax must exceed 20
    best, clipped = {}, 0
    for d in range(1, nmax + 1):
        size = chunk if mem_bytes is None else min(chunk, int(mem_bytes // cov_batch_bytes(d)))
        if size < 1:
            raise ResourceBlocked(f"one {d}-subset needs {cov_batch_bytes(d)} bytes, {mem_bytes} bytes are available")
        combos = np.array(list(itertools.combinations(range(nmax), d)), dtype=np.int64)
        vals = np.empty(len(combos))
        for i in range(0, len(combos), size):
            if check is not None:
                check(f"covariance search d={d} subsets {i}..{min(i + size, len(combos))} of {len(combos)}")
            c = combos[i:i + size]
            v, n = clip_kl(kl_cov_raw(C0[c[:, :, None], c[:, None, :]], C1[c[:, :, None], c[:, None, :]]))
            vals[i:i + len(c)] = v
            clipped += n
        for k in range(d, nmax + 1):
            j = int(np.argmax(np.where(combos[:, -1] < k, vals, -np.inf)))
            best[(k, d)] = (float(vals[j]), combos[j].tolist())
    return best, clipped


def select_from_best(best, k, cost):
    """(d, S, V, tie) maximizing best[(k, d)] / cost[d - 1] over d = 1..k, ties to the smallest d."""
    ratios = np.array([best[(k, d)][0] for d in range(1, k + 1)]) / np.asarray(cost, dtype=np.float64)[:k]
    winners = np.flatnonzero(ratios == ratios.max())
    d = int(winners[0]) + 1
    return d, best[(k, d)][1], float(ratios[d - 1]), bool(winners.size > 1)


MONITOR_START = np.datetime64("2020-01-01")
PRE_J4_END = np.datetime64("2019-12-31")
FROZEN_JSON = REPO_ROOT / "configs" / "FROZEN.json"
TABLES = ("spectra", "selection", "calibration", "trials", "aggregates", "issues")
MEAN, COV, ENERGY = "MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM", "COV_QUADRATIC_VECH_SCAN", "ENERGY_INCREASE_CUSUM"
SOURCE_KIND = {"SYNTH_GAUSS_EQUICORR": "SYNTHETIC_GAUSSIAN", "SYNTH_T7_EQUICORR": "SYNTHETIC_T7"}
Z95 = 1.959963984540054
COHORTS = {"cohort_standard_embargo": {"claim_scope": "REAL_STANDARD_SPLIT", "events": ("COVID_2020", "STYLE_2022H1")},
           "cohort_retrospective_covid": {"claim_scope": "REAL_RETROSPECTIVE_EXPLORATORY", "events": ("COVID_2020",)}}
EVENT_WINDOWS = {"COVID_2020": "E_COVID_2020_ACUTE", "STYLE_2022H1": "E_STYLE_2022H1"}
CONTINUOUS, ONSET_ALIGNED = "CONTINUOUS_RESTART_AFTER_ALARM", "ONSET_ALIGNED"
CODE_MODULES = ("jepadrift.floors", "jepadrift.injection", "jepadrift.sim", "jepadrift.pipelines",
                "jepadrift.monitors.calibration", "jepadrift.monitors.cusum", "jepadrift.monitors.streams",
                "jepadrift.representations.base", "jepadrift.representations.extract",
                "jepadrift.representations.pca", "jepadrift.stats.covariance", "jepadrift.stats.intervals")
STATUS = ("OK", "BLOCKED_PRE_J4", "NOT_EVALUABLE_STANDARD_SPLIT", "DATA_UNAVAILABLE", "UNSUPPORTED", "BLOCKED_RESOURCE",
          "CPV90_OUTSIDE_TOP20", "CALIBRATION_FAILED", "PATH_TOO_SHORT")
CLAIM_FLAGS = ("NONE", "ORACLE_INJECTED_DELTA", "ORACLE_TRUE_SIGMA1", "EX_POST_ORACLE", "COV_SURROGATE_EXPLORATORY",
               "HEURISTIC_COST", "RETROSPECTIVE_DIAGNOSTIC")
ENUMS = {
    "status": STATUS, "execution": ("EXECUTED", "NOT_EXECUTED"),
    "source_kind": ("SYNTHETIC_GAUSSIAN", "SYNTHETIC_T7", "REAL_RETROSPECTIVE"),
    "claim_scope": ("SYNTHETIC_MC", "REAL_STANDARD_SPLIT", "REAL_RETROSPECTIVE_EXPLORATORY"),
    "dataset_id": ("SYNTH_GAUSS_EQUICORR", "SYNTH_T7_EQUICORR", "D3_239"),
    "cohort_id": tuple(COHORTS),
    "event_id": ("A_market_mean", "B_cov_rotate15", "B_cov_rotate30", "B_cov_rotate45", "C_residual_mean",
                 "COVID_2020", "STYLE_2022H1"),
    "event_window_id": ("SYNTH_ONSET_ALIGNED", "E_COVID_2020_ACUTE", "E_STYLE_2022H1"),
    "detector_family": (MEAN, COV, ENERGY),
    "method": ("BASELINE_PREFIX", "BASELINE_CPV90", "ORACLE_Q_MIX", "ORACLE_Q_AFFINE", "EXANTE_QBAR",
               "COV_JOINT_ORACLE", "COV_MARGINAL_DIAGNOSTIC", "ENERGY_INDEX_COMPARATOR"),
    "objective_kind": ("NONE", "CPV90_RULE", "MEAN_MIX_FLUID_SURROGATE", "MEAN_AFFINE_SURROGATE",
                       "EXANTE_QBAR_MIX_FLUID_SURROGATE", "COV_JOINT_AFFINE_SURROGATE", "COV_JOINT_MIX_HEURISTIC",
                       "COV_MARGINAL_MIX_DIAGNOSTIC"),
    "info_kind": ("MEAN_GAUSS_PLUGIN_LW", "MEAN_GAUSS_PLUGIN_LW_T7_PROXY", "MEAN_GAUSS_POP_JOINT_EXACT",
                  "MEAN_GAUSS_POP_JOINT_T7_PROXY", "COV_GAUSS_POP_JOINT_EXACT", "COV_GAUSS_POP_JOINT_T7_PROXY",
                  "COV_GAUSS_MARGINAL", "COV_GAUSS_MARGINAL_T7_PROXY", "EXANTE_QBAR_PLUGIN_LW", "REAL_EXPOST_PLUGIN_LW"),
    "cost_kind": ("MIX_FLUID_SURROGATE", "AFFINE_SURROGATE", "HEURISTIC_COST", "NONE"),
    "metric_kind": ("HOLDOUT_NULL_FPR", "ALT_RMST", "REAL_EVENT_PATH", "GAUSS_FORMULA_CHECK", "GAUSS_PROXY_CHECK_T7"),
    "role": ("calibration", "holdout_null", "alternative", "real_path"),
    "time_origin": (ONSET_ALIGNED, CONTINUOUS),
    "oracle_input": ("INJECTED_DELTA", "TRUE_SIGMA1", "EXPOST_EVENT_DELTA", "STRESS_LIBRARY_2008_2011", "NONE"),
    "null_kind": ("SYNTH_INDEPENDENT_PATHS", "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS"),
    "null_validity": ("EMPIRICAL_QUASI_LIKELIHOOD", "EMPIRICAL_ENERGY", "APPROXIMATE_D6_INSAMPLE_OVERLAPPING"),
    "stream_kind": ("WHITENED_PCA_SCORES", "VECH_QUADRATIC_CENTERED", "EW_INDEX_ENERGY"),
    "alarm_rule": ("GE", "GT"), "ci_kind": ("NORMAL_DEFF1", "WILSON", "NONE"), "severity": ("BLOCKER", "WARNING", "INFO"),
    "comparability": ("COMMON_20_AXIS_UNIVERSE", "NOT_COMPARABLE_OUTSIDE_TOP20"),
    "experiment": ("E1", "E2", "E3"), "row_kind": ("SELECTED", "CANDIDATE"),
    "cpv90_status": ("CPV90_IN_TOP20", "CPV90_OUTSIDE_TOP20"),
    "code": STATUS + ("QUASI_LIKELIHOOD", "SMOKE_NO_CLAIMS", "REAL_NOT_RUN", "RETROSPECTIVE_DEVIATION",
                      "C_UNSUPPORTED", "TRIALS_LOCAL_ONLY"),
    "check_space": tuple(f"WHITENED_Z{n}" for n in range(1, 21)),
    "threshold_rule": (THRESHOLD_RULE,), "guarantee_basis": tuple(GUARANTEE.values()),
}
COMMON = ["schema_version", "run_mode", "run_fingerprint", "source_kind", "claim_scope", "dataset_id", "cohort_id",
          "split_hash", "event_window_id", "event_id", "detector_family", "k", "S", "d", "objective_kind",
          "selection_id", "metric_id", "null_id", "null_calibration_id", "calibration_hash", "config_hash",
          "basis_hash", "seed", "status", "execution"]
COLUMNS = {
    "spectra": COMMON + ["N", "T_fit", "fit_first_day", "fit_last_day", "fit_rows", "complete_rows", "nan_cells",
                         "lw_shrinkage", "trace_lw", "lambda_lw", "whitening_scale", "cpv_lw", "lambda_corr", "mp_edge",
                         "mp_above", "mp_count", "kaiser_ge1", "kaiser_count", "cpv90_k_full", "cpv90_status",
                         "pop_var_axis", "null_var_z", "x_fit_sha256"],
    "selection": COMMON + ["experiment", "method", "row_kind", "reservoir_k", "rank_order", "selection_exact",
                           "tie_broken", "oracle_input", "info_kind", "I_objective", "cost_kind", "M_cost", "C_affine",
                           "V_mix", "V_affine", "I_plugin_lw", "I_pop_joint", "I_cov_joint", "I_cov_marginal_sum",
                           "pop_offdiag_max", "null_metric_id", "claim_flag", "cpv90_k_full", "comparability"],
    "calibration": COMMON + ["null_kind", "stream_kind", "p", "s2", "s2_rule", "cusum_delta", "alarm_rule", "H",
                             "alpha", "n_cal", "rank_r", "threshold", "calibration_alarms", "calibration_fraction",
                             "threshold_rule", "predictive_bound", "guarantee_basis", "maxima_sha256", "centering_hash",
                             "centering_days", "centering_pop_bias_max", "anytime_valid", "null_validity",
                             "window_starts_distinct", "in_sample_share"],
    "trials": ["group_id", "role", "replicate", "first_hit", "censored_time", "detected", "stat_max",
               "pre_onset_alarm", "detected_during_event"],
    "aggregates": COMMON + ["metric_kind", "null_metric_id", "time_origin", "H", "n", "deff", "n_eff", "alarms", "fpr",
                            "fpr_lo", "fpr_hi", "target_fpr", "rmst", "rmst_sd", "rmst_se", "rmst_lo", "rmst_hi",
                            "ci_kind", "det_rate", "det_lo", "det_hi", "censored_share", "monitor_armed_from",
                            "onset_date", "event_end_date", "n_event_sessions", "alarm_dates", "pre_onset_alarms",
                            "pre_onset_alarm_dates", "detected_during_event", "time_to_alarm_during_event",
                            "event_censored", "post_onset_delay_h250", "post_onset_alarm_date", "post_event_alarm",
                            "path_supports_H", "check_estimate", "check_se", "check_reference", "check_space"],
    "issues": COMMON + ["issue_id", "severity", "code", "scope", "message", "deviation_ref", "detail"],
}
PRIMARY_KEYS = {"spectra": ("dataset_id", "basis_hash", "k"), "selection": ("selection_id", "experiment", "row_kind", "d"),
                "calibration": ("null_calibration_id",), "trials": ("group_id", "role", "replicate"),
                "aggregates": ("metric_id",), "issues": ("issue_id",)}
SORT_KEYS = {"spectra": ("dataset_id", "basis_hash", "k"),
             "selection": ("dataset_id", "cohort_id", "event_id", "detector_family", "experiment", "method",
                           "objective_kind", "reservoir_k", "row_kind", "d", "selection_id"),
             "calibration": ("dataset_id", "cohort_id", "detector_family", "d", "S", "null_calibration_id"),
             "trials": ("group_id", "role", "replicate"),
             "aggregates": ("dataset_id", "cohort_id", "event_id", "detector_family", "metric_kind", "d", "S",
                            "metric_id"),
             "issues": ("issue_id",)}


class OutputExists(RuntimeError):
    """The output directory holds a completed run or foreign files; outputs are immutable."""


class ResourceBlocked(RuntimeError):
    """The memory or wall-clock budget is exceeded (status BLOCKED_RESOURCE); completed partitions stay resumable."""


class PartitionMismatch(RuntimeError):
    """A stored partition belongs to another identity (code, configuration, inputs, environment or seed)."""


class DataUnavailable(RuntimeError):
    """A real input is missing, differs from its manifest hash or holds non-finite pre-2020 rows."""


class PreJ4Refused(RuntimeError):
    """Real rows dated after 2019-12-31 are refused before J4 (the FROZEN.json check belongs to stream 21)."""


class IncompleteWindow(ValueError):
    """A declared stress window has no row, a non-finite row or lies after 2019-12-31: no ex-ante result."""


def check_env():
    """Problems of the environment at interpreter start against REQUIRED_ENV (absent thread variables are set here)."""
    return [f"{k}={v!r} (required {REQUIRED_ENV[k]!r})" for k, v in ENV_AT_START.items()
            if v != REQUIRED_ENV[k] and not (v is None and k != "PYTHONHASHSEED")]


def check_pre_j4(days):
    """Raise PreJ4Refused if any real row is dated after 2019-12-31."""
    if (np.asarray(days, dtype="datetime64[D]") > PRE_J4_END).any():
        raise PreJ4Refused("real rows dated after 2019-12-31 are refused before J4 (configs/FROZEN.json check: stream 21)")


def file_sha256(path):
    """SHA-256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else path.name


def _json_default(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o).__name__}")


def identity_block(cfg, inputs):
    """Scientific identity: schema, resolved configuration (resource limits excluded), code bytes, environment, input
    file hashes and seed; independent of Git state."""
    code = sorted([_rel(__file__)] + [_rel(importlib.import_module(m).__file__) for m in CODE_MODULES])
    code_files = {c: file_sha256(REPO_ROOT / c) for c in code}
    blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
    env = {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
           "scipy": sys.modules["scipy"].__version__, "pyyaml": yaml.__version__,
           "statsmodels": sys.modules["statsmodels"].__version__, "blas": [blas.get("name"), blas.get("version")],
           "dtype": "float64", **{k: os.environ.get(k) for k in REQUIRED_ENV}}
    inputs = {_rel(p): file_sha256(p) for p in sorted(inputs, key=str)}
    sci = {k: v for k, v in cfg.items() if k != "resources"}
    return {"schema_version": SCHEMA_VERSION, "config_hash": hashlib.sha256(canon(sci).encode()).hexdigest(),
            "code_files": code_files, "code_hash": hashlib.sha256(canon(code_files).encode()).hexdigest(),
            "environment": env, "env_hash": hashlib.sha256(canon(env).encode()).hexdigest(), "inputs": inputs,
            "input_hash": hashlib.sha256(canon(inputs).encode()).hexdigest(), "seed": int(cfg["seed"])}


def provenance_block(command):
    """Git provenance outside the scientific identity: HEAD, branch, dirty flag, normalized command."""
    def git(*args):
        res = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
        return res.stdout.strip() if res.returncode == 0 else None

    status = git("status", "--porcelain")
    return {"git_sha": git("rev-parse", "HEAD"), "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "git_dirty": None if status is None else bool(status), "command": command}


def peak_rss_bytes():
    """Peak resident set size of this process in bytes (Linux ru_maxrss is in KiB)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


class Store:
    """Partitions of a run under <log-dir>/partitions (npz arrays + JSON sidecar with key and run fingerprint), reused
    only when both match; the wall-clock and memory budgets are checked before each new computation."""

    def __init__(self, path, fingerprint, deadline, clock, mem_limit):
        self.path, self.fingerprint, self.deadline, self.clock = Path(path), fingerprint, deadline, clock
        self.mem_limit = mem_limit
        self.computed = self.loaded = 0

    def check(self, stage):
        """Raise ResourceBlocked once the wall-clock deadline or the memory limit is exceeded."""
        if self.clock() > self.deadline:
            raise ResourceBlocked(f"wall-clock budget exceeded before {stage}")
        rss = peak_rss_bytes()
        if rss > self.mem_limit:
            raise ResourceBlocked(f"peak RSS {rss} bytes exceeds the {self.mem_limit}-byte limit before {stage}")

    def get(self, key, compute):
        name = sha16(key)
        data, meta = self.path / f"{name}.npz", self.path / f"{name}.json"
        if meta.exists():
            record = json.loads(meta.read_text())
            if record.get("fingerprint") != self.fingerprint or record.get("key") != key:
                raise PartitionMismatch(f"partition {name} does not match this run's identity; use fresh directories")
            with np.load(data) as z:
                self.loaded += 1
                return {k: z[k] for k in z.files}
        self.check(f"partition {key}")
        out = compute()
        np.savez(data, **out)
        meta.write_text(json.dumps({"fingerprint": self.fingerprint, "key": key}, sort_keys=True) + "\n")
        self.computed += 1
        return out


class Run:
    """Run context: configuration, identity fingerprint, partition store (None: compute directly), scan accounting."""

    def __init__(self, cfg, fingerprint, store=None, logger=None):
        self.cfg, self.fp, self.store, self.logger = cfg, fingerprint, store, logger
        self.units, self.scan_seconds, self.timers = 0, 0.0, {}
        self.failures = []

    def get(self, key, compute):
        return compute() if self.store is None else self.store.get(key, compute)

    def check(self, stage):
        if self.store is not None:
            self.store.check(stage)

    def available_bytes(self):
        return None if self.store is None else self.store.mem_limit - peak_rss_bytes()

    def log(self, msg):
        if self.logger is not None:
            self.logger(msg)


def prepare_dirs(out_dir, log_dir, resume):
    """Refuse a completed or foreign output directory, or stale partitions without --resume; returns the partition dir."""
    out_dir, log_dir = Path(out_dir), Path(log_dir)
    if (out_dir / "manifest.json").exists():
        raise OutputExists(f"{out_dir} holds a completed run; outputs are immutable, use a fresh --out")
    if out_dir.exists() and any(out_dir.iterdir()) and not resume:
        raise OutputExists(f"{out_dir} is not empty")
    parts = log_dir / "partitions"
    if parts.exists() and any(parts.iterdir()) and not resume:
        raise OutputExists(f"{parts} holds partitions; pass --resume or use a fresh --log-dir")
    out_dir.mkdir(parents=True, exist_ok=True)
    parts.mkdir(parents=True, exist_ok=True)
    return parts


def memory_estimate(cfg):
    """Theoretical peak bytes: six role arrays, scan and vech temporaries, covariance search chunk, paths and matrices."""
    H, nmax, N, B = cfg["H"], cfg["nmax"], cfg["N"], cfg["minibatch"]
    n = max(cfg[k] for k in COUNT_KEYS)
    p_max = nmax * (nmax + 1) // 2
    return 8 * (6 * n * H * (nmax + 1) + 4 * B * (H + 1) * p_max + 2 * B * H * nmax * nmax + 2 * n * H
                + 4 * cfg["cov_search_chunk"] * nmax * nmax + 4 * H * N + 2 * cfg["T_fit"] * N + 6 * N * N)


def first_index(hit):
    """First column (1-based) of each row of a boolean array that is True, -1 if none."""
    return np.where(hit.any(axis=1), hit.argmax(axis=1) + 1, -1).astype(np.int64)


def _offdiag(C):
    if C.shape[0] < 2:
        return None
    s = np.sqrt(np.diag(C))
    R = np.abs(C / np.outer(s, s))
    return float(R[~np.eye(C.shape[0], dtype=bool)].max())


def role_key(cfg, background, role):
    """Seed key prefix of a synthetic role (the replicate index is appended per path)."""
    return seed_key(cfg["seed"], "path", background, role)


def project(cfg, background, role, n, W, transforms=None):
    """Role paths projected on the frozen axes: (Z (n, H, nmax), m (n, H)) with m the equal-weight index, or one such
    pair per transform of the same base paths (returns before projection, injection before the frozen PCA)."""
    H = cfg["H"]
    names = list(transforms) if transforms else [None]
    out = {name: (np.empty((n, H, W.shape[1])), np.empty((n, H))) for name in names}
    for i in range(n):
        X = draw_path(cfg, background, role, i, H)
        for name in names:
            Xs = X if name is None else transforms[name](X)
            out[name][0][i] = Xs @ W
            out[name][1][i] = Xs.mean(axis=1)
    return out if transforms else out[None]


def _info(prep, scen, S):
    sc, (mix, aff), d = prep["scenarios"][scen], prep["costs"], len(S)
    ix = np.ix_(S, S)
    C0 = prep["C0"][ix]
    out = {"d": d, "M_cost": float(mix[d - 1]), "C_affine": float(aff[d - 1]), "pop_offdiag_max": _offdiag(C0),
           "I_plugin_lw": None, "I_pop_joint": None, "I_cov_joint": None, "I_cov_marginal_sum": None}
    if sc["kind"] == "mean":
        I = float(sc["q"][S].sum())
        out.update(info_kind="MEAN_GAUSS_PLUGIN_LW" + ("_T7_PROXY" if prep["t7"] else ""), I_plugin_lw=I,
                   I_pop_joint=kl_mean(sc["mu"][S], C0))
    else:
        C1 = prep["C1"][ix]
        I = kl_cov(C0, C1)
        out.update(info_kind="COV_GAUSS_POP_JOINT_" + ("T7_PROXY" if prep["t7"] else "EXACT"), I_cov_joint=I,
                   I_cov_marginal_sum=float(cov_marginals(C0, C1).sum()))
    return _with_objective(out, I)


def _with_objective(values, I):
    return {**values, "I_objective": float(I), "V_mix": float(I) / values["M_cost"],
            "V_affine": float(I) / values["C_affine"]}


def _order_json(order):
    return json.dumps([int(j) + 1 for j in order], separators=(",", ":"))


def _spec(scen, family, method, objective, row_kind, k, S, experiment, flags, oracle, cost_kind, values,
          status="OK", **extra):
    evaluated = status == "OK" and row_kind == "SELECTED" and (S is not None or family == ENERGY)
    return {"event_id": scen, "event_window_id": "SYNTH_ONSET_ALIGNED", "detector_family": family, "method": method,
            "objective_kind": objective, "row_kind": row_kind, "k": k, "reservoir_k": k, "experiment": experiment,
            "_S": S, "_eval": [family, S_json(S) if S is not None else None] if evaluated else None,
            "claim_flag": json.dumps(sorted(set(flags)), separators=(",", ":")), "oracle_input": oracle,
            "cost_kind": cost_kind, "selection_exact": True, "tie_broken": False, "rank_order": None,
            "cpv90_k_full": None, "comparability": None, "status": status, "info_kind": None, "d": None,
            **values, **extra}


def selection_specs(cfg, prep):
    """Selection rows of one background before evaluation (E1 prefixes, E2 per-reservoir oracles, E3 universe 1..nmax);
    _eval names the (family, S) whose metrics each selected row references."""
    nmax, (mix, aff) = cfg["nmax"], prep["costs"]
    k90 = prep["basis"]["cpv90_k_full"]
    specs = []
    for scen, sc in prep["scenarios"].items():
        mean = sc["kind"] == "mean"
        fam = MEAN if mean else COV
        base = ["NONE"] if mean else ["COV_SURROGATE_EXPLORATORY"]
        for k in range(1, nmax + 1):
            pre = _spec(scen, fam, "BASELINE_PREFIX", "NONE", "SELECTED", k, list(range(k)), "E1", base, "NONE", "NONE",
                        _info(prep, scen, list(range(k))))
            specs += [pre, {**pre, "experiment": "E2"}]
            if mean:
                cand, sel = select_top_q(sc["q"], k, mix)
                specs += _top_q_specs(prep, scen, "ORACLE_Q_MIX", "MEAN_MIX_FLUID_SURROGATE", k, cand, sel, "E2",
                                      ["ORACLE_INJECTED_DELTA"], "INJECTED_DELTA", "MIX_FLUID_SURROGATE", nmax)
            else:
                for objective, cost, cost_kind, extra_flags in (
                        ("COV_JOINT_AFFINE_SURROGATE", aff, "AFFINE_SURROGATE", []),
                        ("COV_JOINT_MIX_HEURISTIC", mix, "HEURISTIC_COST", ["HEURISTIC_COST"])):
                    flags = base + ["ORACLE_TRUE_SIGMA1"] + extra_flags
                    for d in range(1, k + 1):
                        I, Sd = prep["best"][(k, d)]
                        specs.append(_spec(scen, fam, "COV_JOINT_ORACLE", objective, "CANDIDATE", k, Sd, "E2", flags,
                                           "TRUE_SIGMA1", cost_kind, _with_objective(
                                               {**_info(prep, scen, Sd), "I_cov_joint": I}, I)))
                    d_star, S_star, _, tie = select_from_best(prep["best"], k, cost)
                    I = prep["best"][(k, d_star)][0]
                    chosen = _spec(scen, fam, "COV_JOINT_ORACLE", objective, "SELECTED", k, S_star, "E2", flags,
                                   "TRUE_SIGMA1", cost_kind, _with_objective({**_info(prep, scen, S_star),
                                                                              "I_cov_joint": I}, I), tie_broken=tie)
                    specs.append(chosen)
                    if k == nmax:
                        specs.append({**chosen, "experiment": "E3"})
        if k90 <= nmax:
            specs.append(_spec(scen, fam, "BASELINE_CPV90", "CPV90_RULE", "SELECTED", nmax, list(range(k90)), "E3", base,
                               "NONE", "NONE", _info(prep, scen, list(range(k90))), cpv90_k_full=k90,
                               comparability="COMMON_20_AXIS_UNIVERSE"))
        else:
            specs.append(_spec(scen, fam, "BASELINE_CPV90", "CPV90_RULE", "SELECTED", nmax, None, "E3", base, "NONE",
                               "NONE", {}, status="CPV90_OUTSIDE_TOP20", cpv90_k_full=k90,
                               comparability="NOT_COMPARABLE_OUTSIDE_TOP20"))
        specs.append(_spec(scen, fam, "EXANTE_QBAR", "EXANTE_QBAR_MIX_FLUID_SURROGATE", "SELECTED", nmax, None, "E3",
                           base, "STRESS_LIBRARY_2008_2011", "MIX_FLUID_SURROGATE", {}, status="UNSUPPORTED"))
        if mean:
            cand, sel = select_top_q(sc["q"], nmax, aff)
            specs += _top_q_specs(prep, scen, "ORACLE_Q_AFFINE", "MEAN_AFFINE_SURROGATE", nmax, cand, sel, "E3",
                                  ["ORACLE_INJECTED_DELTA"], "INJECTED_DELTA", "AFFINE_SURROGATE", None)
        else:
            qcov = cov_marginals(prep["C0"], prep["C1"])
            cand, sel = select_top_q(qcov, nmax, mix)
            flags = base + ["ORACLE_TRUE_SIGMA1", "HEURISTIC_COST"]
            for c in cand + [None]:
                S = sel["S"] if c is None else c["S"]
                values = _with_objective({**_info(prep, scen, S), "info_kind": "COV_GAUSS_MARGINAL" + (
                    "_T7_PROXY" if prep["t7"] else ""), "I_cov_marginal_sum": float(qcov[S].sum())}, float(qcov[S].sum()))
                specs.append(_spec(scen, fam, "COV_MARGINAL_DIAGNOSTIC", "COV_MARGINAL_MIX_DIAGNOSTIC",
                                   "SELECTED" if c is None else "CANDIDATE", nmax, S, "E3", flags, "TRUE_SIGMA1",
                                   "HEURISTIC_COST", values, rank_order=_order_json(sel["rank_order"]),
                                   tie_broken=bool(c is None and sel["tie_broken"])))
            energy = _spec(scen, ENERGY, "ENERGY_INDEX_COMPARATOR", "NONE", "SELECTED", None, None, "E1", ["NONE"],
                           "NONE", "NONE", {})
            specs += [energy, {**energy, "experiment": "E3"}]
    return specs


def _top_q_specs(prep, scen, method, objective, k, cand, sel, experiment, flags, oracle, cost_kind, e3_copy_at):
    order = _order_json(sel["rank_order"])
    out = [_spec(scen, MEAN, method, objective, "CANDIDATE", k, c["S"], experiment, flags, oracle, cost_kind,
                 _info(prep, scen, c["S"]), rank_order=order) for c in cand]
    chosen = _spec(scen, MEAN, method, objective, "SELECTED", k, sel["S"], experiment, flags, oracle, cost_kind,
                   _info(prep, scen, sel["S"]), rank_order=order, tie_broken=sel["tie_broken"])
    out.append(chosen)
    if k == e3_copy_at:
        out.append({**chosen, "experiment": "E3"})
    return out


def prepare_background(run, background):
    """Everything fixed before any calibration path, from the fit and centering roles only: frozen basis, population
    matrices in the whitened space z, drifts, information, costs, exact covariance search, selections, centering."""
    cfg = run.cfg
    N, nmax, rho = cfg["N"], cfg["nmax"], cfg["synthetic"]["rho"]
    X_fit = draw_path(cfg, background, "fit", 0, cfg["T_fit"])
    basis = fit_basis(X_fit)
    V, lam = basis["eigvec"], basis["eigval"]
    fit = injection.fit_background(X_fit, 1)
    if not (np.array_equal(fit["eigval"], lam) and np.array_equal(fit["eigvec"], V)):
        raise ArithmeticError("injection and PCA disagree on the Ledoit-Wolf eigen-pairs")
    W = np.ascontiguousarray(V[:, :nmax] / np.sqrt(lam[:nmax]))
    s0, s0inv = equicorrelation(N, rho), equicorrelation_inverse(N, rho)
    theta = float(cfg["synthetic"]["rotation_deg"])
    pair = tuple(int(a) - 1 for a in cfg["synthetic"]["rotation_pair"])
    params = {"calib": (0, cfg["T_fit"]), "fit": fit, "pair": pair, "theta_deg": theta}
    _, M, meta = injection.inject(X_fit, "F4-rotate", 0, None, params, rng(cfg["seed"], "inject", background, "B"))
    s1 = M @ s0 @ M.T
    C0, C1 = W.T @ s0 @ W, W.T @ s1 @ W
    scenarios = {}
    beta, delta = scenario_A(V, s0, float(cfg["synthetic"]["sr_annual_A"]))
    scenarios["A_market_mean"] = {"kind": "mean", "beta": beta, "delta": delta}
    if c_supported(cfg):
        beta, delta, c = scenario_C(V, s0inv, cfg["synthetic"]["C_axes"], float(cfg["synthetic"]["C_I_target"]))
        scenarios["C_residual_mean"] = {"kind": "mean", "beta": beta, "delta": delta, "c": c}
    rot = f"B_cov_rotate{int(round(theta))}"
    scenarios[rot] = {"kind": "cov", "M": M}
    for sc in scenarios.values():
        if sc["kind"] == "mean":
            sc["mu"] = sc["beta"][:nmax] / np.sqrt(lam[:nmax])
            sc["q"] = q_plugin(sc["beta"][:nmax], lam[:nmax])
            sc["drift_hash"] = array_sha256(sc["delta"])
        else:
            sc["drift_hash"] = array_sha256(sc["M"])
    t = time.perf_counter()
    Zc, _ = project(cfg, background, "centering", cfg["n_center"], W)
    flat = Zc.reshape(-1, nmax)
    C0hat = flat.T @ flat / flat.shape[0]
    m_fit = X_fit.mean(axis=1) ** 2
    best, clipped = exhaustive_cov(C0, C1, nmax, cfg["cov_search_chunk"], run.check, run.available_bytes())
    run.timers["search_and_centering"] = run.timers.get("search_and_centering", 0.0) + time.perf_counter() - t
    prep = {"basis": basis, "W": W, "sigma0": s0, "M": M, "C0": C0, "C1": C1, "scenarios": scenarios,
            "costs": cost_tables(float(cfg["gamma_M"]), nmax), "best": best, "clipped": clipped,
            "t7": cfg["synthetic"]["backgrounds"][background] is not None, "C0hat": C0hat,
            "centering_hash": array_sha256(C0hat), "centering_days": int(flat.shape[0]),
            "energy_mu": float(m_fit.mean()), "energy_sd": float(m_fit.std()), "inject_info": float(meta["info"]),
            "I_cov_pop_full": kl_cov(s0, s1)}
    prep["specs"] = selection_specs(cfg, prep)
    return prep


def role_data(run, background, prep):
    """Calibration, holdout-null and alternative projections; the alternative base paths are shared by A, B and C."""
    cfg, W = run.cfg, prep["W"]
    transforms = {}
    for scen, sc in prep["scenarios"].items():
        if sc["kind"] == "mean":
            transforms[scen] = (lambda d: (lambda X: X + d))(sc["delta"])
        else:
            transforms[scen] = (lambda M: (lambda X: X @ M.T))(sc["M"])
    return {"calibration": project(cfg, background, "calibration", cfg["n_cal"], W),
            "holdout_null": project(cfg, background, "holdout_null", cfg["n_null"], W),
            "alternative": project(cfg, background, "alternative", cfg["n_alt"], W, transforms)}


def _scan(run, batches, s2, h, p):
    Ws, firsts = [], []
    for Z in batches:
        if Z.shape[-1] != p:
            raise ValueError(f"stream dimension {Z.shape[-1]} differs from the declared p = {p} of s2")
        t = time.perf_counter()
        W, first = scan_statistic(Z, s2, h)
        run.scan_seconds += time.perf_counter() - t
        B, H, p = Z.shape
        t_end = H if h is None or (first < 0).any() else int(first.max())
        run.units += B * p * t_end * (t_end + 1) // 2
        Ws.append(W)
        firsts.append(first)
    return np.concatenate(Ws), np.concatenate(firsts)


def _detector(cfg, prep, family, S):
    """(stream, p, s2, rule, kind, validity) of a detector on subset S (S None for the index energy)."""
    H, alpha = cfg["H"], float(cfg["alpha"])
    if family == ENERGY:
        return (lambda Z, m: energy_stream(m, prep["energy_mu"], prep["energy_sd"])), None, None, "GT", \
            "EW_INDEX_ENERGY", "EMPIRICAL_ENERGY"
    d = len(S)
    p = d if family == MEAN else d * (d + 1) // 2
    s2 = 2.0 * math.log(pl.horizon_gamma(H, alpha)) / (H * p)
    if family == MEAN:
        return (lambda Z, m: Z[..., S]), p, s2, "GE", "WHITENED_PCA_SCORES", "EMPIRICAL_QUASI_LIKELIHOOD"
    C0S = prep["C0hat"][np.ix_(S, S)]
    return (lambda Z, m: vech_stream(Z[..., S], C0S)), p, s2, "GE", "VECH_QUADRATIC_CENTERED", \
        "EMPIRICAL_QUASI_LIKELIHOOD"


def _full_statistic(run, family, stream, Z, m, s2, p, delta):
    if family == ENERGY:
        return cusum_trajectory_vec(stream(Z, m), delta)
    B = run.cfg["minibatch"]
    return _scan(run, (stream(Z[i:i + B], m[i:i + B]) for i in range(0, len(Z), B)), s2, None, p)[0]


def detect_null(run, family, stream, Z, m, s2, p, rule, h=None):
    """stat_max over the horizon and first hits of null paths; h None: h is the predictive rank threshold of these
    maxima, and a failed calibration returns stat_max alone."""
    stat = _full_statistic(run, family, stream, Z, m, s2, p, float(run.cfg["energy_delta"]))
    out = {"stat_max": stat.max(axis=1)}
    if h is None:
        try:
            h = rank_threshold(out["stat_max"], float(run.cfg["alpha"]), rule)[0]
        except CalibrationFailed:
            return out
    out["first_hit"] = first_index(stat > h if rule == "GT" else stat >= h)
    return out


def calibrate(run, stat_max, rule, null_kind, scope):
    """(threshold or None, calibration fields) of one null sample by the predictive exchangeable rank; the bound is
    reported for exchangeable synthetic maxima only; a failure is recorded for issues.csv with every threshold field NA."""
    alpha, n = float(run.cfg["alpha"]), len(stat_max)
    fields = {"threshold_rule": THRESHOLD_RULE, "guarantee_basis": GUARANTEE[null_kind], "n_cal": n,
              "maxima_sha256": array_sha256(stat_max), "rank_r": None, "threshold": None, "calibration_alarms": None,
              "calibration_fraction": None, "predictive_bound": None, "calibration_hash": None,
              "status": "CALIBRATION_FAILED"}
    try:
        h, r, alarms = rank_threshold(stat_max, alpha, rule)
    except CalibrationFailed as exc:
        run.failures.append({**scope, "reason": "INSUFFICIENT_N" if isinstance(exc, InsufficientCalibration)
                             else "NON_FINITE_THRESHOLD", "message": str(exc), "n": n})
        return None, fields
    exchangeable = GUARANTEE[null_kind] == "EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA"
    return h, {**fields, "rank_r": r, "threshold": h, "calibration_alarms": alarms, "calibration_fraction": alarms / n,
               "predictive_bound": predictive_bound(r, n) if exchangeable else None, "status": "OK",
               "calibration_hash": hashlib.sha256(np.ascontiguousarray(stat_max).tobytes() + repr(h).encode()).hexdigest()}


def detect_alternative(run, family, stream, Z, m, s2, p, h):
    """First hits (1-based, -1 none) of alternative paths at threshold h; scans stop once every path has alarmed."""
    if family == ENERGY:
        f = strict_cusum_vec(stream(Z, m), float(run.cfg["energy_delta"]), h)
        return {"first_hit": np.where(f >= 0, f + 1, -1).astype(np.int64)}
    B = run.cfg["minibatch"]
    return {"first_hit": _scan(run, (stream(Z[i:i + B], m[i:i + B]) for i in range(0, len(Z), B)), s2, h, p)[1]}


def _trials(group, role, first, H, stat_max=None):
    return [{"group_id": group, "role": role, "replicate": i, "first_hit": int(f), "censored_time": int(f if f > 0 else H),
             "detected": bool(f > 0), "stat_max": None if stat_max is None else float(stat_max[i])}
            for i, f in enumerate(first)]


def _rmst_fields(first, H):
    n = len(first)
    ct = np.where(first > 0, first, H).astype(np.float64)
    det = int((first > 0).sum())
    sd = float(ct.std(ddof=1)) if n > 1 else None
    se = sd / math.sqrt(n / 1.0) if sd is not None else None
    lo, hi = wilson(det, n)
    rmst = float(ct.mean())
    return {"n": n, "deff": 1.0, "n_eff": float(n), "alarms": det, "rmst": rmst, "rmst_sd": sd, "rmst_se": se,
            "rmst_lo": None if se is None else rmst - Z95 * se, "rmst_hi": None if se is None else rmst + Z95 * se,
            "ci_kind": "NORMAL_DEFF1", "det_rate": det / n, "det_lo": lo, "det_hi": hi, "censored_share": 1.0 - det / n}


def evaluate_subset(run, background, prep, data, family, S, scenarios, tables, common):
    """Calibration (rank threshold), holdout FPR and alternative RMST of one (family, S) on shared paths; appends the
    calibration, trials and aggregates rows; returns the identifiers referenced by the selection rows."""
    cfg = run.cfg
    H, alpha = cfg["H"], float(cfg["alpha"])
    stream, p, s2, rule, kind, validity = _detector(cfg, prep, family, S)
    S_text = S_json(S) if S is not None else None
    centering = prep["centering_hash"] if family == COV else None
    params = {"p": p, "s2": s2, "delta": float(cfg["energy_delta"]) if family == ENERGY else None, "alarm_rule": rule}
    null_id = sha16({"fp": run.fp, "dataset": background, "cohort": None, "null_kind": "SYNTH_INDEPENDENT_PATHS",
                     "role_key": role_key(cfg, background, "calibration"), "n": cfg["n_cal"], "H": H})
    ncid = sha16({"null_id": null_id, "family": family, "params": params, "centering_hash": centering,
                  "basis_hash": prep["basis"]["basis_hash"], "S": S_text, "alpha": alpha, "rule": THRESHOLD_RULE})
    key = [background, family, S_text]
    Zc, mc = data["calibration"]
    cal = run.get(["calibration"] + key, lambda: detect_null(run, family, stream, Zc, mc, s2, p, rule))
    h, fields = calibrate(run, cal["stat_max"], rule, "SYNTH_INDEPENDENT_PATHS",
                          {"dataset_id": background, "cohort_id": None, "null_id": null_id})
    d = len(S) if S is not None else None
    ids = {**common, "detector_family": family, "S": S_text, "d": d, "null_id": null_id, "null_calibration_id": ncid,
           "calibration_hash": fields.pop("calibration_hash"), "status": fields.pop("status"), "execution": "EXECUTED"}
    sub = prep["C0hat"][np.ix_(S, S)] - prep["C0"][np.ix_(S, S)] if family == COV else None
    tables["calibration"].append({
        **ids, **fields, "null_kind": "SYNTH_INDEPENDENT_PATHS", "stream_kind": kind, "p": p, "s2": s2,
        "s2_rule": None if s2 is None else "2*ln(H/alpha)/(H*p)", "cusum_delta": params["delta"], "alarm_rule": rule,
        "H": H, "alpha": alpha, "centering_hash": centering,
        "centering_days": prep["centering_days"] if family == COV else None,
        "centering_pop_bias_max": None if sub is None else float(np.abs(sub).max()), "anytime_valid": False,
        "null_validity": validity})
    hold_id = sha16({"kind": "HOLDOUT_NULL_FPR", "ncid": ncid, "role_key": role_key(cfg, background, "holdout_null"),
                     "n": cfg["n_null"]})
    alt_ids = {scen: sha16({"kind": "ALT_RMST", "ncid": ncid, "event_id": scen,
                            "drift_hash": prep["scenarios"][scen]["drift_hash"], "event_window_id": "SYNTH_ONSET_ALIGNED",
                            "role_key": role_key(cfg, background, "alternative"), "n": cfg["n_alt"], "H": H,
                            "time_origin": ONSET_ALIGNED}) for scen in scenarios}
    res = {"null_id": null_id, "ncid": ncid, "calibration_hash": ids["calibration_hash"], "holdout": hold_id,
           "alt": alt_ids, "failed": h is None}
    if h is None:
        failed = {**ids, "execution": "NOT_EXECUTED"}
        tables["aggregates"].append({**failed, "metric_id": hold_id, "metric_kind": "HOLDOUT_NULL_FPR", "H": H})
        tables["aggregates"] += [{**failed, "metric_id": alt_ids[scen], "metric_kind": "ALT_RMST", "event_id": scen,
                                  "event_window_id": "SYNTH_ONSET_ALIGNED", "null_metric_id": hold_id,
                                  "time_origin": ONSET_ALIGNED, "H": H} for scen in scenarios]
        return res
    tables["trials"] += _trials(ncid, "calibration", cal["first_hit"], H, cal["stat_max"])
    Zn, mn = data["holdout_null"]
    hold = run.get(["holdout_null"] + key, lambda: detect_null(run, family, stream, Zn, mn, s2, p, rule, h))
    k_alarm = int((hold["first_hit"] > 0).sum())
    lo, hi = wilson(k_alarm, cfg["n_null"])
    tables["aggregates"].append({**ids, "metric_id": hold_id, "metric_kind": "HOLDOUT_NULL_FPR", "H": H,
                                 "n": cfg["n_null"], "deff": 1.0, "n_eff": float(cfg["n_null"]), "alarms": k_alarm,
                                 "fpr": k_alarm / cfg["n_null"], "fpr_lo": lo, "fpr_hi": hi, "target_fpr": alpha,
                                 "ci_kind": "WILSON"})
    tables["trials"] += _trials(hold_id, "holdout_null", hold["first_hit"], H, hold["stat_max"])
    for scen in scenarios:
        Za, ma = data["alternative"][scen]
        alt = run.get(["alternative"] + key + [scen],
                      lambda Za=Za, ma=ma: detect_alternative(run, family, stream, Za, ma, s2, p, h))
        tables["aggregates"].append({**ids, "metric_id": alt_ids[scen], "metric_kind": "ALT_RMST", "event_id": scen,
                                     "event_window_id": "SYNTH_ONSET_ALIGNED", "null_metric_id": hold_id,
                                     "time_origin": ONSET_ALIGNED, "H": H, **_rmst_fields(alt["first_hit"], H)})
        tables["trials"] += _trials(alt_ids[scen], "alternative", alt["first_hit"], H)
    return res


def synthetic_common(run, background, prep):
    """Common columns of the rows of one synthetic background."""
    cfg = run.cfg
    split = {"T_fit": cfg["T_fit"], "H": cfg["H"], "counts": {k: cfg[k] for k in COUNT_KEYS},
             "roles": {r: role_key(cfg, background, r) for r in SEED_ROLES}}
    return {"source_kind": SOURCE_KIND[background], "claim_scope": "SYNTHETIC_MC", "dataset_id": background,
            "split_hash": hashlib.sha256(canon(split).encode()).hexdigest(), "basis_hash": prep["basis"]["basis_hash"]}


def run_background(run, background, tables):
    """One synthetic background: preparation, spectra, shared role paths, every (family, S) evaluation, formula checks
    and the selection rows; returns its manifest block."""
    cfg = run.cfg
    t = time.perf_counter()
    prep = prepare_background(run, background)
    common = synthetic_common(run, background, prep)
    tables["spectra"] += spectra_rows(prep["basis"], {**common, "status": "OK", "execution": "EXECUTED",
                                                      "fit_rows": cfg["T_fit"], "complete_rows": cfg["T_fit"],
                                                      "nan_cells": 0}, cfg["nmax"], prep["sigma0"])
    t_gen = time.perf_counter()
    data = role_data(run, background, prep)
    run.timers["generation"] = run.timers.get("generation", 0.0) + time.perf_counter() - t_gen
    evals = {}
    for spec in prep["specs"]:
        if spec["_eval"] is not None:
            evals.setdefault(tuple(spec["_eval"]), set()).add(spec["event_id"])
    results = {}
    for family, S_text in sorted(evals, key=lambda e: (e[0], e[1] or "")):
        S = None if S_text is None else [a - 1 for a in json.loads(S_text)]
        results[(family, S_text)] = evaluate_subset(run, background, prep, data, family, S,
                                                    sorted(evals[(family, S_text)]), tables, common)
    check_kind = "GAUSS_PROXY_CHECK_T7" if prep["t7"] else "GAUSS_FORMULA_CHECK"
    for scen, sc in prep["scenarios"].items():
        Z = data["alternative"][scen][0].reshape(-1, cfg["nmax"])
        if sc["kind"] == "mean":
            llr, ref = llr_mean(Z, sc["mu"], prep["C0"]), kl_mean(sc["mu"], prep["C0"])
        else:
            llr, ref = llr_cov(Z, prep["C0"], prep["C1"]), kl_cov(prep["C0"], prep["C1"])
        tables["aggregates"].append({
            **common, "metric_id": sha16({"kind": check_kind, "fp": run.fp, "dataset": background, "event_id": scen,
                                          "drift_hash": sc["drift_hash"], "n": cfg["n_alt"], "H": cfg["H"]}),
            "metric_kind": check_kind, "event_id": scen, "event_window_id": "SYNTH_ONSET_ALIGNED",
            "status": "OK", "execution": "EXECUTED", "H": cfg["H"], "n": int(Z.shape[0]),
            "check_estimate": float(llr.mean()), "check_se": float(llr.std(ddof=1) / math.sqrt(llr.size)),
            "check_reference": ref, "check_space": f"WHITENED_Z{cfg['nmax']}"})
    for spec in prep["specs"]:
        row = {k: v for k, v in spec.items() if not k.startswith("_")}
        row.update(common)
        row["S"] = S_json(spec["_S"]) if spec["_S"] is not None else None
        row["selection_id"] = sha16({"fp": run.fp, "dataset": background, "cohort": None, "event": spec["event_id"],
                                     "method": spec["method"], "objective": spec["objective_kind"],
                                     "reservoir_k": spec["reservoir_k"], "S": row["S"],
                                     "basis_hash": common["basis_hash"]})
        res = results.get(tuple(spec["_eval"])) if spec["_eval"] is not None else None
        if res is None:
            row["execution"] = "NOT_EXECUTED"
        else:
            row.update(metric_id=res["alt"][spec["event_id"]], null_metric_id=res["holdout"], null_id=res["null_id"],
                       null_calibration_id=res["ncid"], calibration_hash=res["calibration_hash"],
                       execution="NOT_EXECUTED" if res["failed"] else "EXECUTED")
            if res["failed"]:
                row["status"] = "CALIBRATION_FAILED"
        tables["selection"].append(row)
    run.timers[background] = time.perf_counter() - t
    return _background_manifest(cfg, prep)


def _background_manifest(cfg, prep):
    b, nmax = prep["basis"], cfg["nmax"]
    out = {"basis_hash": b["basis_hash"], "x_fit_sha256": b["x_fit_sha256"], "lw_shrinkage": b["lw_shrinkage"],
           "trace_lw": b["trace_lw"], "mp_count": b["mp_count"], "mp_edge": b["mp_edge"],
           "kaiser_count": b["kaiser_count"], "cpv90_k_full": b["cpv90_k_full"],
           "centering": {"hash": prep["centering_hash"], "days": prep["centering_days"],
                         "pop_bias_max": float(np.abs(prep["C0hat"] - prep["C0"]).max())},
           "energy_standardization": {"mu": prep["energy_mu"], "sd": prep["energy_sd"]},
           "covariance_search": {"subsets": 2 ** nmax - 1, "clipped_negative_kl": prep["clipped"],
                                 "selection_exact": True}, "scenarios": {}}
    for scen, sc in prep["scenarios"].items():
        if sc["kind"] == "mean":
            entry = {"delta": sc["delta"].tolist(), "delta_sha256": sc["drift_hash"], "beta_nonzero": {
                str(int(j) + 1): float(sc["beta"][j]) for j in np.flatnonzero(sc["beta"])},
                "I_plugin_lw_top_nmax": float(sc["q"].sum()), "I_pop_joint_top_nmax": kl_mean(sc["mu"], prep["C0"]),
                "I_pop_full": kl_mean(sc["delta"], prep["sigma0"])}
            if scen == "A_market_mean":
                entry.update(sr_annual=cfg["synthetic"]["sr_annual_A"],
                             daily_shift_population_sd=cfg["synthetic"]["sr_annual_A"] / math.sqrt(252.0),
                             I_pop_axis1=0.5 * float(sc["mu"][0]) ** 2 / float(prep["C0"][0, 0]))
            else:
                entry.update(axes=cfg["synthetic"]["C_axes"], c=sc["c"], I_target=cfg["synthetic"]["C_I_target"],
                             constraint_matrix="Sigma0 = (1 - rho) I + rho 11' (Sherman-Morrison inverse)")
        else:
            entry = {"pair": cfg["synthetic"]["rotation_pair"], "theta_deg": cfg["synthetic"]["rotation_deg"],
                     "M_sha256": sc["drift_hash"], "I_plugin_full_inject": prep["inject_info"],
                     "I_cov_pop_full": prep["I_cov_pop_full"], "I_cov_joint_top_nmax": kl_cov(prep["C0"], prep["C1"])}
        out["scenarios"][scen] = entry
    return out


def cohort_definitions(cfg, splits, dates=None):
    """Both real cohorts from the configuration and splits.yaml; dates (a calendar only) arm the retrospective cohort."""
    seg = splits["segments"]
    monitor_first = str(seg["monitor"]["first_day"])
    armed = str(dates[dates >= MONITOR_START][0]) if dates is not None else None
    defs = {}
    for cohort, spec in COHORTS.items():
        standard = cohort == "cohort_standard_embargo"
        events = {}
        for event in spec["events"]:
            onset, end = (str(cfg["real"]["events"][event][x]) for x in ("onset", "end"))
            inside = standard and np.datetime64(end) < np.datetime64(monitor_first)
            status = "NOT_EVALUABLE_STANDARD_SPLIT" if inside else "BLOCKED_PRE_J4"
            origin = CONTINUOUS if not standard else (None if inside else ONSET_ALIGNED)
            events[event] = {"onset": onset, "end": end, "status": status, "time_origin": origin,
                             "event_window_id": EVENT_WINDOWS[event]}
        definition = {"cohort_id": cohort, "calib": [str(seg["calib"]["first_day"]), str(seg["calib"]["last_day"])],
                      "monitor_start": monitor_first if standard else "first_session_on_or_after_2020-01-01",
                      "embargo_after_2019": 65 if standard else 0, "events": events,
                      "pre_onset_policy": "keep_every_alarm_restart_next_day"}
        defs[cohort] = {"split_hash": hashlib.sha256(canon(definition).encode()).hexdigest(),
                        "monitor_armed_from": monitor_first if standard else armed,
                        "embargo_after_2019": definition["embargo_after_2019"], "claim_scope": spec["claim_scope"],
                        "events": events, "definition": definition}
    return defs


def manifest_hashes(cfg):
    """{file name: SHA-256} of the real dataset entries of the derived-data manifest."""
    path = REPO_ROOT / cfg["real"]["manifest"]
    if not path.exists():
        raise DataUnavailable(f"manifest {_rel(path)} is missing")
    outputs = json.loads(path.read_text())["datasets"][cfg["real"]["dataset"]]["outputs"]
    return {Path(o["path"]).name: o["sha256"] for o in outputs}


def read_pre2020_panel(cfg, expected, load=np.load):
    """Pre-monitor rows dated 2005-01-04..2019-12-31 only, from a read-only memmap: files hashed against the manifest,
    the calendar read, then the slice [a, b) alone materialized; rows after 2019-12-31 are never indexed."""
    d = REPO_ROOT / cfg["real"]["derived_dir"]
    files = {n: d / n for n in ("ret_wide.npy", "dates.npy", "assets.json", "splits.yaml")}
    missing = sorted(n for n, f in files.items() if not f.exists())
    if missing:
        raise DataUnavailable(f"missing real inputs {missing}")
    hashes = {n: file_sha256(f) for n, f in files.items()}
    bad = sorted(n for n in files if hashes[n] != expected.get(n))
    if bad:
        raise DataUnavailable(f"real inputs differ from the manifest: {bad}")
    dates = np.asarray(load(files["dates.npy"]), dtype="datetime64[D]")
    splits = yaml.safe_load(files["splits.yaml"].read_text())
    a, b = pl.split_rows(dates, splits)["pre_monitor"]
    excluded = np.asarray(cfg["real"]["exclude_days"], dtype="datetime64[D]")
    while a < b and np.isin(dates[a], excluded):
        a += 1
    days = dates[a:b]
    check_pre_j4(days)
    if days.size == 0 or days[0] < np.datetime64(cfg["real"]["window_start"]) or np.isin(days, excluded).any() \
            or (np.diff(days).astype(np.int64) <= 0).any():
        raise DataUnavailable("pre-monitor rows are empty, start early, hold an excluded day or are not increasing")
    mm = load(files["ret_wide.npy"], mmap_mode="r")
    X = np.array(mm[a:b], dtype=np.float64, order="C")
    del mm
    if not np.isfinite(X).all():
        raise DataUnavailable("pre-2020 rows hold non-finite returns")
    return {"X": X, "days": days, "rows": [int(a), int(b)], "splits": splits, "hashes": hashes,
            "assets": json.loads(files["assets.json"].read_text())}


def stress_library(X, days, windows, rbar, basis, nmax):
    """qbar: equal-weight mean over the declared stress windows of the plug-in information of
    Delta_e = mean(window) - rbar_calib in the frozen basis; incomplete or post-2019 windows raise IncompleteWindow."""
    V, lam = basis["eigvec"], basis["eigval"]
    qs, info = [], {}
    for name in sorted(windows):
        lo, hi = (np.datetime64(x) for x in windows[name])
        rows = (days >= lo) & (days <= hi)
        if hi > PRE_J4_END or not rows.any() or not np.isfinite(X[rows]).all():
            raise IncompleteWindow(f"stress window {name} is empty, incomplete or after 2019-12-31")
        delta = X[rows].mean(axis=0) - rbar
        qs.append(q_plugin((V.T @ delta)[:nmax], lam[:nmax]))
        info[name] = {"first_day": str(days[rows][0]), "last_day": str(days[rows][-1]), "rows": int(rows.sum()),
                      "delta_sha256": array_sha256(delta)}
    return np.mean(qs, axis=0), info


def run_real(run, tables):
    """Pre-2020 real computations of the full mode: frozen D3 basis on the calib rows, stress library, ex-ante
    selection and, per cohort, D6 sign-flip null thresholds; every post-2019 evaluation stays blocked."""
    cfg = run.cfg
    H, nmax, alpha = cfg["H"], cfg["nmax"], float(cfg["alpha"])
    panel = read_pre2020_panel(cfg, manifest_hashes(cfg))
    X, days, seg = panel["X"], panel["days"], panel["splits"]["segments"]
    c0, c1 = segment_rows(days, seg["calib"])
    if c1 - c0 != cfg["real"]["expected_calib_rows"]:
        raise DataUnavailable(f"{c1 - c0} calib rows, expected {cfg['real']['expected_calib_rows']}")
    X_cal = np.ascontiguousarray(X[c0:c1])
    basis = fit_basis(X_cal)
    rbar = X_cal.mean(axis=0)
    W = np.ascontiguousarray(basis["eigvec"][:, :nmax] / np.sqrt(basis["eigval"][:nmax]))
    common = {"source_kind": "REAL_RETROSPECTIVE", "dataset_id": "D3_239", "basis_hash": basis["basis_hash"]}
    tables["spectra"] += spectra_rows(basis, {**common, "status": "OK", "execution": "EXECUTED"}, nmax, None,
                                      {"fit_first_day": str(days[c0]), "fit_last_day": str(days[c1 - 1]),
                                       "fit_rows": c1 - c0, "complete_rows": c1 - c0, "nan_cells": 0})
    mix = cost_tables(float(cfg["gamma_M"]), nmax)[0]
    state = {"basis": basis, "k90": basis["cpv90_k_full"], "exante": None, "ncid": {}, "chash": {}}
    try:
        qbar, info = stress_library(X, days, cfg["real"]["stress_windows"], rbar, basis, nmax)
        _, sel = select_top_q(qbar, nmax, mix)
        state["exante"] = {"S": sel["S"], "d": sel["d"], "I": sel["I"], "V": sel["V"], "tie_broken": sel["tie_broken"],
                           "rank_order": _order_json(sel["rank_order"])}
        state["stress"] = {"windows": info, "qbar": qbar.tolist(), "weights": "equal"}
    except IncompleteWindow as exc:
        state["stress"] = {"error": str(exc)}
    subsets = {S_json(range(k)): list(range(k)) for k in range(1, nmax + 1)}
    if state["exante"] is not None:
        subsets[S_json(state["exante"]["S"])] = state["exante"]["S"]
    Zpre = (X - rbar) @ W
    n_real = cfg["real"]["n_null"]
    starts = Zpre.shape[0] - H + 1
    s_idx = np.arange(starts)
    in_sample = float(((s_idx < c1) & (s_idx + H > c0)).mean())
    defs = cohort_definitions(cfg, panel["splits"])
    for cohort in COHORTS:
        windows = null_windows(Zpre, H, n_real, rng(cfg["seed"], "real_null", cohort), flip=True)
        null_id = sha16({"fp": run.fp, "dataset": "D3_239", "cohort": cohort,
                         "null_kind": "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS",
                         "role_key": seed_key(cfg["seed"], "real_null", cohort), "n": n_real, "H": H})
        for S_text, S in sorted(subsets.items()):
            p = len(S)
            s2 = 2.0 * math.log(pl.horizon_gamma(H, alpha)) / (H * p)
            ncid = sha16({"null_id": null_id, "family": MEAN, "params": {"p": p, "s2": s2, "delta": None,
                                                                         "alarm_rule": "GE"},
                          "centering_hash": None, "basis_hash": basis["basis_hash"], "S": S_text, "alpha": alpha,
                          "rule": THRESHOLD_RULE})
            cal = run.get(["real_calibration", cohort, S_text],
                          lambda S=S, s2=s2, p=p: detect_null(run, MEAN, lambda Z, m: Z[..., S], windows,
                                                              np.zeros(windows.shape[:2]), s2, p, "GE"))
            h, fields = calibrate(run, cal["stat_max"], "GE", "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS",
                                  {"dataset_id": "D3_239", "cohort_id": cohort, "null_id": null_id})
            state["ncid"][(cohort, S_text)], state["chash"][(cohort, S_text)] = ncid, fields["calibration_hash"]
            tables["calibration"].append({
                **common, **fields, "claim_scope": COHORTS[cohort]["claim_scope"], "cohort_id": cohort,
                "split_hash": defs[cohort]["split_hash"], "detector_family": MEAN, "S": S_text, "d": p,
                "null_id": null_id, "null_calibration_id": ncid, "execution": "EXECUTED",
                "null_kind": "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS", "stream_kind": "WHITENED_PCA_SCORES", "p": p,
                "s2": s2, "s2_rule": "2*ln(H/alpha)/(H*p)", "alarm_rule": "GE", "H": H, "alpha": alpha,
                "anytime_valid": False, "null_validity": "APPROXIMATE_D6_INSAMPLE_OVERLAPPING",
                "window_starts_distinct": int(starts), "in_sample_share": in_sample})
            if h is not None:
                tables["trials"] += _trials(ncid, "calibration", cal["first_hit"], H, cal["stat_max"])
    state["manifest"] = {"files": {n: {"sha256": v} for n, v in panel["hashes"].items()},
                         "rows_indexed": panel["rows"], "first_day": str(days[0]), "last_day": str(days[-1]),
                         "calib": {"first_day": str(days[c0]), "last_day": str(days[c1 - 1]), "rows": c1 - c0},
                         "basis_hash": basis["basis_hash"], "cpv90_k_full": basis["cpv90_k_full"],
                         "stress_library": state["stress"],
                         "null": {"kind": "REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS", "n": n_real,
                                  "window_starts_distinct": int(starts), "in_sample_share": in_sample},
                         "limits": ["C-D3-no239", "C-D3-survivor", "C-D3-survivor-correction"]}
    return state


def real_status_rows(run, tables, defs, real=None, unavailable=False):
    """Selection and aggregate rows of both real cohorts, present in every run and never computed from a post-2019
    return: NOT_EVALUABLE_STANDARD_SPLIT, BLOCKED_PRE_J4 or DATA_UNAVAILABLE, metrics NA."""
    cfg = run.cfg
    nmax = cfg["nmax"]
    methods = [("BASELINE_PREFIX", "NONE", k, ("E1", "E2")) for k in range(1, nmax + 1)]
    methods += [("ORACLE_Q_MIX", "MEAN_MIX_FLUID_SURROGATE", k, ("E2", "E3") if k == nmax else ("E2",))
                for k in range(1, nmax + 1)]
    methods += [("BASELINE_CPV90", "CPV90_RULE", nmax, ("E3",)), ("ORACLE_Q_AFFINE", "MEAN_AFFINE_SURROGATE", nmax, ("E3",)),
                ("EXANTE_QBAR", "EXANTE_QBAR_MIX_FLUID_SURROGATE", nmax, ("E3",))]
    mix, aff = cost_tables(float(cfg["gamma_M"]), nmax)
    basis_hash = real["basis"]["basis_hash"] if real else None
    for cohort, spec in COHORTS.items():
        cdef = defs[cohort] if defs else None
        split_hash = cdef["split_hash"] if cdef else hashlib.sha256(canon({"cohort_id": cohort, "unavailable": True})
                                                                    .encode()).hexdigest()
        for event in spec["events"]:
            ev = cdef["events"][event] if cdef else {"status": "DATA_UNAVAILABLE", "time_origin": None,
                                                     "onset": str(cfg["real"]["events"][event]["onset"]),
                                                     "end": str(cfg["real"]["events"][event]["end"])}
            status = "DATA_UNAVAILABLE" if unavailable or cdef is None else ev["status"]
            ewid = EVENT_WINDOWS[event]
            common = {"source_kind": "REAL_RETROSPECTIVE", "claim_scope": spec["claim_scope"], "dataset_id": "D3_239",
                      "cohort_id": cohort, "split_hash": split_hash, "event_window_id": ewid, "event_id": event,
                      "detector_family": MEAN, "basis_hash": basis_hash, "status": status,
                      "execution": "NOT_EXECUTED"}
            for method, objective, k, experiments in methods:
                S, values, extra = None, {}, {}
                if method == "BASELINE_PREFIX":
                    S = list(range(k))
                elif method == "BASELINE_CPV90" and real:
                    extra = {"cpv90_k_full": real["k90"], "comparability": "COMMON_20_AXIS_UNIVERSE"
                             if real["k90"] <= nmax else "NOT_COMPARABLE_OUTSIDE_TOP20"}
                    S = list(range(real["k90"])) if real["k90"] <= nmax else None
                elif method == "EXANTE_QBAR" and real and real["exante"]:
                    ex = real["exante"]
                    S = ex["S"]
                    values = {"info_kind": "EXANTE_QBAR_PLUGIN_LW", "I_objective": ex["I"], "M_cost": float(mix[ex["d"] - 1]),
                              "C_affine": float(aff[ex["d"] - 1]), "V_mix": ex["V"],
                              "V_affine": ex["I"] / float(aff[ex["d"] - 1]), "I_plugin_lw": ex["I"],
                              "rank_order": ex["rank_order"], "tie_broken": ex["tie_broken"]}
                S_text = S_json(S) if S is not None else None
                ncid = real["ncid"].get((cohort, S_text)) if real and S_text else None
                chash = real["chash"].get((cohort, S_text)) if real and S_text else None
                metric_id = sha16({"kind": "REAL_EVENT_PATH", "ncid": ncid, "cohort": cohort, "event_window_id": ewid,
                                   "method": method, "k": k, "S": S_text, "time_origin": ev["time_origin"],
                                   "policy": "R1-R5"})
                flags = ["EX_POST_ORACLE"] if method.startswith("ORACLE") else ["NONE"]
                if event == "STYLE_2022H1":
                    flags = [f for f in flags if f != "NONE"] + ["RETROSPECTIVE_DIAGNOSTIC"]
                oracle = {"ORACLE_Q_MIX": "EXPOST_EVENT_DELTA", "ORACLE_Q_AFFINE": "EXPOST_EVENT_DELTA",
                          "EXANTE_QBAR": "STRESS_LIBRARY_2008_2011"}.get(method, "NONE")
                cost_kind = {"MEAN_MIX_FLUID_SURROGATE": "MIX_FLUID_SURROGATE", "MEAN_AFFINE_SURROGATE": "AFFINE_SURROGATE",
                             "EXANTE_QBAR_MIX_FLUID_SURROGATE": "MIX_FLUID_SURROGATE"}.get(objective, "NONE")
                ids = {**common, "S": S_text, "d": len(S) if S is not None else None, "metric_id": metric_id,
                       "null_calibration_id": ncid, "calibration_hash": chash}
                selection_id = sha16({"fp": run.fp, "dataset": "D3_239", "cohort": cohort, "event": event,
                                      "method": method, "objective": objective, "reservoir_k": k, "S": S_text,
                                      "basis_hash": basis_hash})
                for experiment in experiments:
                    tables["selection"].append({
                        **ids, "experiment": experiment, "method": method, "row_kind": "SELECTED", "k": k,
                        "reservoir_k": k, "objective_kind": objective, "selection_id": selection_id,
                        "selection_exact": True, "tie_broken": False, "oracle_input": oracle, "cost_kind": cost_kind,
                        "claim_flag": json.dumps(sorted(flags), separators=(",", ":")), **values, **extra})
                tables["aggregates"].append({
                    **ids, "metric_kind": "REAL_EVENT_PATH", "time_origin": ev["time_origin"], "H": cfg["H"],
                    "onset_date": ev["onset"], "event_end_date": ev["end"],
                    "monitor_armed_from": cdef["monitor_armed_from"] if cdef else None})


def scan_alarms(z, s2, h):
    """0-based alarm indices of the scan on one path z (L, p), restarted (S = 0) the day after each alarm (R1)."""
    alarms, start = [], 0
    while start < len(z):
        first = scan_statistic(z[None, start:], s2, h)[1][0]
        if first < 0:
            break
        start += int(first)
        alarms.append(start - 1)
    return alarms


def evaluate_real_path(z, dates, s2, h, onset, end, H, time_origin, source_kind):
    """Rules R1-R5 on one dated path: every alarm kept with a restart after it, pre-onset alarms never detections,
    detection within [onset, end] or window censoring, separate H-day post-onset reading, PATH_TOO_SHORT; a
    REAL_RETROSPECTIVE path dated after 2019-12-31 is refused before J4."""
    dates = np.asarray(dates, dtype="datetime64[D]")
    if source_kind == "REAL_RETROSPECTIVE":
        check_pre_j4(dates)
    elif source_kind != "FAKE_DATED_TEST":
        raise ValueError(f"unknown source_kind {source_kind!r}")
    oi = int(np.searchsorted(dates, np.datetime64(onset)))
    ei = int(np.searchsorted(dates, np.datetime64(end), side="right")) - 1
    alarms = scan_alarms(np.asarray(z, dtype=np.float64), s2, h)
    pre = [a for a in alarms if a < oi]
    acute = [a for a in alarms if oi <= a <= ei]
    post = [a for a in alarms if oi <= a < oi + H]
    supports = len(dates) - oi >= H
    n_event = ei - oi + 1
    continuous = time_origin == CONTINUOUS
    return {"monitor_armed_from": str(dates[0]), "onset_date": str(dates[oi]), "event_end_date": str(dates[ei]),
            "n_event_sessions": n_event, "alarm_dates": json.dumps([str(dates[a]) for a in alarms]),
            "pre_onset_alarms": len(pre) if continuous else None,
            "pre_onset_alarm_dates": json.dumps([str(dates[a]) for a in pre]) if continuous else None,
            "detected_during_event": bool(acute), "event_censored": not acute,
            "time_to_alarm_during_event": acute[0] - oi + 1 if acute else n_event,
            "post_onset_delay_h250": post[0] - oi + 1 if post else (H if supports else math.nan),
            "post_onset_alarm_date": str(dates[post[0]]) if post else None,
            "post_event_alarm": bool(post and post[0] > ei), "path_supports_H": supports,
            "status": "OK" if supports else "PATH_TOO_SHORT"}


def _typed(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return (0, 0.0, "")
    if isinstance(v, (bool, np.bool_, int, np.integer, float, np.floating)):
        return (1, float(v), "")
    return (2, 0.0, str(v))


def frame(name, rows, common):
    """Validated, deduplicated and sorted DataFrame of one table (closed enumerations, unique primary keys)."""
    cols = COLUMNS[name]
    rows = [{**{c: common.get(c) for c in COMMON if c in cols}, **r} if name != "trials" else r for r in rows]
    for r in rows:
        for col, allowed in ENUMS.items():
            v = r.get(col)
            if col in cols and v is not None and not (isinstance(v, float) and math.isnan(v)) and v not in allowed:
                raise ValueError(f"{name}.{col} = {v!r} is outside its closed enumeration")
        if name == "selection" and r.get("claim_flag") is not None and \
                not set(json.loads(r["claim_flag"])) <= set(CLAIM_FLAGS):
            raise ValueError(f"selection.claim_flag {r['claim_flag']!r} is outside its closed enumeration")
    unique = {}
    for r in rows:
        key = tuple(_typed(r.get(c)) for c in PRIMARY_KEYS[name])
        body = canon({c: r.get(c) for c in cols if not (isinstance(r.get(c), float) and math.isnan(r.get(c)))})
        if key in unique and unique[key][0] != body:
            raise ValueError(f"{name}: primary key {key} has two different rows")
        unique.setdefault(key, (body, r))
    ordered = sorted((r for _, r in unique.values()), key=lambda r: tuple(_typed(r.get(c)) for c in SORT_KEYS[name]))
    return pd.DataFrame(ordered, columns=cols)


def standard_issues(run, tables, flags):
    """issues.csv rows: closed codes, deterministic issue_id = sha16(code, scope)."""
    def add(code, severity, scope, message, deviation_ref=None, detail=None, **cols):
        scope = canon(scope)
        tables["issues"].append({**cols, "issue_id": sha16({"code": code, "scope": scope}), "severity": severity,
                                 "code": code,
                                 "scope": scope, "message": message, "deviation_ref": deviation_ref,
                                 "detail": None if detail is None else canon(detail),
                                 "status": code if code in STATUS else None})

    add("QUASI_LIKELIHOOD", "INFO", {"detector_family": [MEAN, COV]},
        "frozen Ledoit-Wolf whitening is estimated: scans are quasi-likelihoods, thresholds come from empirical "
        "calibration only (anytime_valid = False, no log-gamma threshold)", "C-pca-benchmark-design")
    if run.cfg["mode"] == "smoke":
        add("SMOKE_NO_CLAIMS", "INFO", {"mode": "smoke"},
            "smoke counts are 40 per role: no FPR or RMST claim; only the counts differ from the full configuration")
    if not flags["real_run"]:
        add("REAL_NOT_RUN", "INFO", {"dataset_id": "D3_239"},
            "pre-2020 real computations (basis, stress library, D6 null) not executed in this run: smoke or synthetic")
    if flags["real_unavailable"]:
        add("DATA_UNAVAILABLE", "BLOCKER", {"dataset_id": "D3_239"}, f"real inputs unavailable: {flags['real_error']}")
    add("BLOCKED_PRE_J4", "BLOCKER", {"cohort_id": list(COHORTS)},
        "real evaluations need returns dated after 2019-12-31: refused before J4 (configs/FROZEN.json check, stream 21)")
    add("NOT_EVALUABLE_STANDARD_SPLIT", "INFO", {"cohort_id": "cohort_standard_embargo", "event_id": "COVID_2020"},
        "2020-02-24..2020-03-23 lies inside the 65-session embargo after 2020-01-01")
    add("RETROSPECTIVE_DEVIATION", "WARNING", {"cohort_id": "cohort_retrospective_covid"},
        "exploratory no-embargo cohort armed on the first session of 2020, never a confirmatory test",
        "C-pca-covid-retrospective")
    add("UNSUPPORTED", "INFO", {"method": "EXANTE_QBAR", "source_kind": ["SYNTHETIC_GAUSSIAN", "SYNTHETIC_T7"]},
        "the ex-ante stress library is defined on 2008/2011 real windows only")
    add("UNSUPPORTED", "INFO", {"detector_family": [COV, ENERGY], "dataset_id": "D3_239"},
        "no real covariance event or Sigma1 is defined")
    alpha, groups = float(run.cfg["alpha"]), {}
    for f in run.failures:
        groups.setdefault((f["dataset_id"], f["cohort_id"], f["null_id"], f["reason"]), []).append(f)
    for (dataset, cohort, null_id, reason), fs in sorted(groups.items(), key=lambda kv: canon(list(kv[0]))):
        add("CALIBRATION_FAILED", "BLOCKER", {"dataset_id": dataset, "cohort_id": cohort, "null_id": null_id,
                                              "reason": reason},
            f"{len(fs)} calibration(s) of this null sample failed: {fs[0]['message']}", "C-pca-predictive-rank",
            {"failed_calibrations": len(fs), "n": fs[0]["n"], "alpha": alpha, "min_n_cal": min_calibration_n(alpha),
             "reason": reason}, dataset_id=dataset, cohort_id=cohort, null_id=null_id)
    if not c_supported(run.cfg):
        add("C_UNSUPPORTED", "WARNING", {"event_id": "C_residual_mean"}, "scenario C axes lie outside [2, nmax]")
    for row in tables["spectra"]:
        if row["k"] == 1 and row["cpv90_status"] == "CPV90_OUTSIDE_TOP20":
            add("CPV90_OUTSIDE_TOP20", "INFO", {"dataset_id": row["dataset_id"], "basis_hash": row["basis_hash"]},
                f"full-spectrum CPV90 cutoff k = {row['cpv90_k_full']} lies outside the candidate axes 1..{run.cfg['nmax']}")


def calibration_block(cfg):
    """Manifest description of the threshold rule, its hypotheses and the ranks of the configured null sample sizes."""
    alpha = float(cfg["alpha"])

    def configured(n, exchangeable):
        r = predictive_rank(n, alpha)
        return {"n": n, "rank_r": r if r >= 0 else None,
                "predictive_bound": predictive_bound(r, n) if r >= 0 and exchangeable else None}

    return {"threshold_rule": THRESHOLD_RULE, "alpha": alpha, "min_n_cal": min_calibration_n(alpha),
            "rank": "r = floor(alpha (n + 1)) - 1 with exact decimal alpha; r < 0 is CALIBRATION_FAILED (insufficient n)",
            "threshold": "b = sorted(maxima)[n - r - 1]; GT threshold b, GE threshold nextafter(b, +inf), one step; a "
                         "non-finite threshold is CALIBRATION_FAILED",
            "guarantee": "if the n calibration maxima and the maximum of a new null path are exchangeable, P(new maximum "
                         "> b) <= (r + 1)/(n + 1) <= alpha, ties conservative; marginal over the calibration sample and "
                         "the new path, conditional on the fit and nuisance (centering) choices frozen on independent "
                         "roles; neither conditional on a realized threshold nor an e-process property",
            "guarantee_basis": GUARANTEE,
            "real_event_path": "single historical path after overlapping historical null windows: no predictive "
                               "guarantee and no FPR",
            "holdout": "fpr, fpr_lo, fpr_hi and n are the observed holdout rate, an independent observation that may "
                       "differ from the bound; never replaced by alpha or the bound",
            "anytime_valid": False, "statistic": "quasi-likelihood scans and energy CUSUM, empirical calibration",
            "configured": {"n_cal": configured(cfg["n_cal"], True),
                           "real_n_null": configured(cfg["real"]["n_null"], False)}}


def run_benchmark(cfg, dataset, out_dir, log_dir, resume=False, command=None, clock=time.monotonic):
    """Run the benchmark into out_dir (seven files, manifest last); 0 on success, 3 on BLOCKED_RESOURCE (partitions kept
    for --resume, no manifest). Smoke mode is synthetic only; real computations run in full mode up to 2019-12-31."""
    validate_config(cfg)
    if dataset not in ("synthetic", "real", "both"):
        raise ValueError(f"dataset must be synthetic, real or both, got {dataset!r}")
    if cfg["mode"] == "smoke" and dataset != "synthetic":
        raise ValueError("smoke mode is synthetic only")
    real_wanted = cfg["mode"] == "full" and dataset in ("real", "both")
    plan = seed_plan(cfg, real_wanted)
    out_dir, log_dir = Path(out_dir), Path(log_dir)
    parts = prepare_dirs(out_dir, log_dir, resume)
    log_path = log_dir / "run.log"
    t0, wall0 = clock(), time.perf_counter()

    def logger(msg):
        with open(log_path, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}\n")

    def blocked(reason):
        report = {"status": "BLOCKED_RESOURCE", "reason": reason, "partitions": len(list(parts.glob("*.json")))}
        (log_dir / "blocked_resource.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
        logger(f"BLOCKED_RESOURCE: {reason}")
        return 3

    logger(f"start mode={cfg['mode']} dataset={dataset} resume={resume} command={command}")
    mem = memory_estimate(cfg)
    if mem > float(cfg["resources"]["mem_limit_gib"]) * 2 ** 30:
        return blocked(f"theoretical peak {mem / 2 ** 30:.2f} GiB exceeds {cfg['resources']['mem_limit_gib']} GiB")
    derived = REPO_ROOT / cfg["real"]["derived_dir"]
    inputs = [derived / "splits.yaml"] if (derived / "splits.yaml").exists() else []
    if real_wanted:
        inputs += [f for f in (derived / "ret_wide.npy", derived / "dates.npy", derived / "assets.json",
                               REPO_ROOT / cfg["real"]["manifest"]) if f.exists()]
    identity = identity_block(cfg, inputs)
    fp = hashlib.sha256(canon(identity).encode()).hexdigest()
    store = Store(parts, fp, t0 + 60.0 * float(cfg["resources"]["max_wall_minutes"]), clock,
                  float(cfg["resources"]["mem_limit_gib"]) * 2 ** 30)
    run = Run(cfg, fp, store, logger)
    tables = {name: [] for name in TABLES}
    flags = {"real_run": False, "real_unavailable": False, "real_error": None}
    try:
        synthetic = {bg: run_background(run, bg, tables) for bg in cfg["synthetic"]["backgrounds"]} \
            if dataset in ("synthetic", "both") else {}
        real = None
        if real_wanted:
            try:
                real = run_real(run, tables)
                flags["real_run"] = True
            except DataUnavailable as exc:
                flags.update(real_unavailable=True, real_error=str(exc))
        splits = yaml.safe_load((derived / "splits.yaml").read_text()) if (derived / "splits.yaml").exists() else None
        if splits is None:
            flags.update(real_unavailable=True, real_error=flags["real_error"] or "splits.yaml is missing")
        defs = cohort_definitions(cfg, splits) if splits is not None else None
        real_status_rows(run, tables, defs, real, unavailable=flags["real_unavailable"])
    except ResourceBlocked as exc:
        return blocked(str(exc))
    common = {"schema_version": SCHEMA_VERSION, "run_mode": cfg["mode"], "run_fingerprint": fp,
              "config_hash": identity["config_hash"], "seed": int(cfg["seed"])}
    outputs = {}
    for name in ("spectra", "selection", "calibration", "trials", "aggregates"):
        outputs[f"{name}.csv"] = _write(out_dir, name, tables[name], common)
    if outputs["trials.csv"]["bytes"] > 50 * 2 ** 20:
        flags["trials_large"] = True
    standard_issues(run, tables, flags)
    if flags.get("trials_large"):
        tables["issues"].append({"issue_id": sha16({"code": "TRIALS_LOCAL_ONLY"}), "severity": "WARNING",
                                 "code": "TRIALS_LOCAL_ONLY", "scope": canon({"file": "trials.csv"}),
                                 "message": "trials.csv exceeds 50 MB: keep it local and untracked (hash in manifest)"})
    outputs["issues.csv"] = _write(out_dir, "issues", tables["issues"], common)
    mix, aff = cost_tables(float(cfg["gamma_M"]), cfg["nmax"])
    a, c = affine_costs(float(cfg["gamma_M"]))
    manifest = {
        "schema_version": SCHEMA_VERSION, "run_mode": cfg["mode"], "dataset": dataset, "run_fingerprint": fp,
        "identity": identity, "provenance": provenance_block(command), "config": cfg,
        "differences_from_full": {k: {"smoke": cfg[k], "full": cfg["full_counts"][k]} for k in COUNT_KEYS}
        if cfg["mode"] == "smoke" else {}, "claims": "none: smoke counts of 40 per role" if cfg["mode"] == "smoke" else "see aggregates",
        "synthetic": {"model": {"N": cfg["N"], "rho": cfg["synthetic"]["rho"],
                                "Sigma0": "(1 - rho) I + rho 11' (unit variances)",
                                "t_mixing": "one chi2_7 draw per day shared by the factor and idiosyncratic parts "
                                            "(multivariate t, elliptical), rescaled to unit variance",
                                "backgrounds": cfg["synthetic"]["backgrounds"]}, "backgrounds": synthetic},
        "real": {"dataset": cfg["real"]["dataset"], "cohorts": defs,
                 "pre_onset_policy": "R1 continuous, every alarm kept, restart the next day; R2 pre-onset alarms never "
                                     "detections; R3 acute-window detection or censoring; R4 separate H-day "
                                     "post-onset reading; R5 single path, no interval or FPR",
                 **(real["manifest"] if real else {"executed": False, "reason": flags["real_error"]
                                                   or "smoke or synthetic run"})},
        "detectors": {MEAN: "W_t = max_{1<=tau<=t} [-(p/2) log1p(n s2) + s2 |S_t - S_{tau-1}|^2 / (2 (1 + n s2))], "
                            "alarm W_t >= h, every start tau evaluated",
                      COV: "same scan on y_t = vech_std(z_t z_t' - C0_centering), p = d (d + 1) / 2",
                      ENERGY: f"Page CUSUM S_t = max(0, S_{{t-1}} + e_t - {cfg['energy_delta']}), alarm S_t > lambda, "
                              "e_t = (m_t^2 - mu_fit) / sd_fit on the equal-weight index",
                      "s2_rule": "2 ln(H / alpha) / (H p)", "threshold_rule": THRESHOLD_RULE},
        "calibration": calibration_block(cfg),
        "costs": {"gamma_M": cfg["gamma_M"], "M": mix.tolist(), "affine": {"a": a, "c": c, "rule": "chord of M at d = 1 "
                  "and d = 20"}, "affine_values": aff.tolist()},
        "pre_j4": {"frozen_json_present": FROZEN_JSON.exists(), "status": "BLOCKED_PRE_J4",
                   "rule": "no real return dated after 2019-12-31 is read before J4"},
        "rng": {"bit_generator": "PCG64", "root_seed": int(cfg["seed"]), "key": "[28, seed, crc32(label), ...]",
                "roles": list(SEED_ROLES), "domains": list(SEED_DOMAINS),
                "plan": {"n_keys": plan["n_keys"], "sha256": plan["sha256"], "vocabulary": plan["vocabulary"],
                         "checks": "label CRC32 codes pairwise distinct on this vocabulary; canonical SeedSequence "
                                   "entropies (uint32 words zero-padded to 4) unique; checked before any draw; no "
                                   "universal CRC32 guarantee assumed"}},
        "outputs": outputs}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2, default=_json_default) + "\n")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20
    elapsed = time.perf_counter() - wall0
    logger(f"done in {elapsed:.1f} s; partitions computed {store.computed}, loaded {store.loaded}; scan units "
           f"{run.units} in {run.scan_seconds:.1f} s ({run.units / max(run.scan_seconds, 1e-9):.3e} per s); "
           f"timers {canon({k: round(v, 3) for k, v in run.timers.items()})}; ru_maxrss {rss:.3f} GiB")
    for name, meta in sorted(outputs.items()):
        logger(f"sha256 {name} {meta['sha256']} rows {meta['rows']} bytes {meta['bytes']}")
    logger(f"sha256 manifest.json {file_sha256(out_dir / 'manifest.json')}")
    return 0


def _write(out_dir, name, rows, common):
    df = frame(name, rows, common)
    path = out_dir / f"{name}.csv"
    pl.save_fair_csv(df, path)
    return {"sha256": file_sha256(path), "bytes": path.stat().st_size, "rows": int(len(df))}


def main(argv=None):
    """CLI: python experiments/pca_drift_benchmark.py --mode smoke|full [--dataset ...] [--out DIR] [--log-dir DIR]."""
    ap = argparse.ArgumentParser(description="PCA spectral prefixes versus information-selected subsets on mean and "
                                             "covariance drifts (stream 28).")
    ap.add_argument("--config", type=Path, default=CONFIG, help="YAML configuration (default configs/pca_drift_benchmark.yaml)")
    ap.add_argument("--mode", required=True, choices=("smoke", "full"), help="smoke: the four role counts become 40")
    ap.add_argument("--dataset", default="synthetic", choices=("synthetic", "real", "both"),
                    help="real computations run in full mode only, on rows dated up to 2019-12-31")
    ap.add_argument("--out", "--output-dir", dest="out", type=Path,
                    help="output directory (default results/pca_drift_benchmark/smoke_predictive_v2 or full)")
    ap.add_argument("--log-dir", type=Path,
                    help="log and partition directory (default logs/pca_drift_benchmark/smoke_predictive_v2 or full)")
    ap.add_argument("--seed", type=int, help="root seed overriding the configuration")
    ap.add_argument("--resume", action="store_true", help="reuse partitions whose fingerprint matches this run")
    args = ap.parse_args(argv)
    problems = check_env()
    if problems:
        print("environment refused: " + "; ".join(problems), file=sys.stderr)
        return 2
    if args.mode == "smoke" and args.dataset != "synthetic":
        ap.error("--mode smoke is synthetic only: use --dataset synthetic")
    cfg = load_config(args.config, args.mode)
    if args.seed is not None:
        cfg["seed"] = args.seed
    run_dir = "smoke_predictive_v2" if args.mode == "smoke" else "full"
    out = args.out or REPO_ROOT / "results" / "pca_drift_benchmark" / run_dir
    log_dir = args.log_dir or REPO_ROOT / "logs" / "pca_drift_benchmark" / run_dir
    raw = list(sys.argv[1:] if argv is None else argv)
    command = ["experiments/pca_drift_benchmark.py"] + [
        "<OUT>" if i > 0 and raw[i - 1] in ("--out", "--output-dir") else "<LOG>" if i > 0 and raw[i - 1] == "--log-dir"
        else v for i, v in enumerate(raw)]
    try:
        return run_benchmark(cfg, args.dataset, out, log_dir, args.resume, command)
    except (OutputExists, PartitionMismatch, PreJ4Refused) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
