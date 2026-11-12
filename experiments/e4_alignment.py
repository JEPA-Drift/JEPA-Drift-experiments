"""Stream 19 E4: fixed-information N scan of an ex ante spectral dictionary, prototype and cost-pilot route only.

Plan prompts/plans/plan-19-e4-code-20261112.md (GO prompts/GO-stream-19-e4-code-20261112.md). Synthetic equicorrelated
Gaussian and shared-scale t7 backgrounds, an isotropic residual mean drift of fixed Gaussian information I*, a frozen
Ledoit-Wolf basis per (background, N) under the local E4 eigen convention, the registry streams of P3-C full and
P3-CS(b) full read through log paths, and a scalar sign detector shared by EW, O-dir and O-score1. The full campaign is
refused by the CLI.

Usage: python experiments/e4_alignment.py --mode precheck|pilot --partition ID --out DIR --log-dir DIR [--jobs 1]
"""
import argparse
import concurrent.futures
import contextlib
import copy
import functools
import hashlib
import json
import math
import multiprocessing
import os
import platform
import resource
import signal
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import pca_drift_benchmark as pdb
from jepadrift import floors, pipelines
from jepadrift.monitors import eprocess
from jepadrift.monitors.streams import exact_sign_stream
from jepadrift.stats.intervals import wilson

STREAM = 19
REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "e4_alignment.yaml"
TIE_FACTOR = 64
SCALAR = ("EW", "O-dir", "O-score1")
DICTIONARY = ("SPEC-prefix8", "SPEC-full", "P3-CS(b)")
METHODS = ("EW", "SPEC-prefix8", "SPEC-full", "P3-CS(b)", "O-dir", "O-score1")
BASIS_METHODS = ("SPEC-prefix8", "SPEC-full", "P3-CS(b)", "O-score1")
ORACLE = {"O-dir": "ORACLE_DIRECTION", "O-score1": "ORACLE_SCORE1"}
ROLES = ("fit", "calibration", "holdout", "alternative", "scalar_calibration")
DOMAINS = ("innov", "chi2_t7", "coins", "direction", "boot", "scalar_cal", "pilot")
SPACES = ("science", "pilot")
READINGS = ("predictive_rank", "anytime_valid_horizon")
COINS_SUFFIX = 7


class EigenTieUnresolved(ValueError):
    """Fitted eigenvalue gaps at or below the declared tolerance: no canonical basis, the cell is refused."""

    def __init__(self, message, blocks, gaps):
        super().__init__(message)
        self.code, self.blocks, self.gaps = "EIGENVALUE_TIE_UNRESOLVED", blocks, gaps


def load_config(path):
    """YAML configuration of the E4 lot."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _integer(value, name, low):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < low:
        raise ValueError(f"{name} must be an integer >= {low}, got {value!r}")
    return int(value)


def _open_unit(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not (math.isfinite(value) and 0 < value < 1):
        raise ValueError(f"{name} must be a finite number in (0, 1), got {value!r}")
    return float(value)


def i_star(H, alpha, divisor=40.0):
    """Fixed daily Gaussian information I* such that ln(H/alpha)/I* = H/divisor (protocol section 3)."""
    return divisor * math.log(H / alpha) / H


def validate_config(cfg):
    """Validated copy of an E4 configuration; ValueError on an invalid grid, N, rho, alpha, H, I*, nu or count."""
    cfg = copy.deepcopy(cfg)
    if not cfg.get("grid"):
        raise ValueError("grid must be a non-empty list of dimensions")
    cfg["grid"] = [_integer(N, "N", 1) for N in cfg["grid"]]
    cfg["rho"], cfg["alpha"] = _open_unit(cfg["rho"], "rho"), _open_unit(cfg["alpha"], "alpha")
    for name in ("H", "T_fit", "n_hold", "n_alt", "B_boot", "pilot_n", "prefix_k", "seed"):
        cfg[name] = _integer(cfg[name], name, 0 if name == "seed" else 1)
    if _integer(cfg["n_cal"], "n_cal", 1) < pdb.min_calibration_n(cfg["alpha"]):
        raise ValueError(f"n_cal = {cfg['n_cal']} is below the rank-rule minimum {pdb.min_calibration_n(cfg['alpha'])}")
    divisor = cfg["info_divisor"]
    if isinstance(divisor, bool) or not isinstance(divisor, (int, float)) or not (math.isfinite(divisor) and divisor > 0):
        raise ValueError(f"info_divisor must be finite and positive, got {divisor!r}")
    info = i_star(cfg["H"], cfg["alpha"], divisor)
    if not (math.isfinite(info) and info > 0):
        raise ValueError(f"I* must be finite and positive, got {info!r}")
    for background, nu in cfg["backgrounds"].items():
        if nu is not None and (isinstance(nu, bool) or not isinstance(nu, (int, float)) or not (math.isfinite(nu) and nu > 2)):
            raise ValueError(f"background {background!r}: nu must be finite and > 2, got {nu!r}")
    return cfg


def key(cfg, space, *parts):
    """SeedSequence entropy [19, seed, ('pilot',) parts], string parts replaced by their CRC32 label code."""
    if space not in SPACES:
        raise ValueError(f"space must be one of {SPACES}, got {space!r}")
    parts = (("pilot",) if space == "pilot" else ()) + parts
    return [STREAM, int(cfg["seed"]), *(pdb.label_code(p) if isinstance(p, str) else int(p) for p in parts)]


def _rng(cfg, space, *parts):
    return np.random.default_rng(np.random.SeedSequence(key(cfg, space, *parts)))


def counts(cfg, space):
    """Replicates per role: the configured sizes in the scientific space, pilot_n for every role in the pilot space."""
    if space == "pilot":
        return {role: cfg["pilot_n"] for role in ("calibration", "holdout", "alternative")}
    return {"calibration": cfg["n_cal"], "holdout": cfg["n_hold"], "alternative": cfg["n_alt"]}


def planned_keys(cfg, space):
    """Every seed entropy a space draws, the registry coin suffix included."""
    n = counts(cfg, space)
    keys = [key(cfg, space, "innov", "fit", 0), key(cfg, space, "chi2_t7", "fit", 0)]
    for role in ("calibration", "holdout", "alternative"):
        for i in range(n[role]):
            keys += [key(cfg, space, "innov", role, i), key(cfg, space, "chi2_t7", role, i),
                     key(cfg, space, "coins", role, i) + [COINS_SUFFIX]]
    keys += [key(cfg, space, "direction", i) for i in range(max(n["holdout"], n["alternative"]))]
    keys += [key(cfg, space, "boot", role) for role in ("alternative", "holdout")]
    keys += [key(cfg, space, "scalar_cal", i) for i in range(n["calibration"])]
    return keys


def seed_plan(cfg):
    """Checked seed plan of both spaces: CRC32 injective on the label vocabulary and unique canonical entropies."""
    vocab = sorted(set(DOMAINS) | set(ROLES) | set(cfg["backgrounds"]))
    codes = {}
    for label in vocab:
        codes.setdefault(pdb.label_code(label), []).append(label)
    clash = sorted(v for v in codes.values() if len(v) > 1)
    if clash:
        raise ValueError(f"CRC32 collision among the seed labels {clash}: rename a label; no seed is changed")
    keys = planned_keys(cfg, "science") + planned_keys(cfg, "pilot")
    canonical = pdb.check_entropies(keys)
    return {"n_keys": len(keys), "vocabulary": {label: pdb.label_code(label) for label in vocab},
            "sha256": hashlib.sha256(pdb.canon([list(c) for c in canonical]).encode()).hexdigest()}


def draw_innov(cfg, space, role, i, T):
    """Standard normal innovations (T, 1 + N_max) of one path: column 0 the factor, then the idiosyncratic noise."""
    return _rng(cfg, space, "innov", role, i).standard_normal((T, 1 + max(cfg["grid"])))


def t7_scale(cfg, space, role, i, T, nu):
    """Shared per-day scale sqrt((nu - 2)/chi2_nu) of unit variance (the t background)."""
    return np.sqrt((nu - 2.0) / _rng(cfg, space, "chi2_t7", role, i).chisquare(nu, T))


def direction_draw(cfg, space, i):
    """Gaussian vector g of N_max coordinates whose prefixes define the residual directions of replicate i."""
    return _rng(cfg, space, "direction", i).standard_normal(max(cfg["grid"]))


def panel(innov, scale, N, rho):
    """Equicorrelated returns sqrt(rho) f 1' + sqrt(1 - rho) eps[:, :N], times the per-day scale if given."""
    x = math.sqrt(rho) * innov[:, :1] + math.sqrt(1.0 - rho) * innov[:, 1:N + 1]
    return x if scale is None else x * scale[:, None]


def role_path(cfg, space, background, role, i, N, T=None):
    """Drift-free path (T, N) of one role replicate; Gaussian and t backgrounds share the innovations."""
    T = cfg["H"] if T is None else T
    nu = cfg["backgrounds"][background]
    innov = draw_innov(cfg, space, role, i, T)
    return panel(innov, None if nu is None else t7_scale(cfg, space, role, i, T, nu), N, cfg["rho"])


def residual_direction(g, N):
    """u_N = P g_{1:N} / ||P g_{1:N}||, P the projector on the orthogonal of 1; refused for N < 2."""
    if N < 2:
        raise ValueError(f"N = {N} has no residual direction orthogonal to the market")
    v = np.asarray(g[:N], dtype=np.float64) - np.mean(g[:N])
    return v / np.linalg.norm(v)


def drift_scale(cfg):
    """c = sqrt(2 (1 - rho) I*): the drift c u_N carries the Gaussian information I* exactly."""
    return math.sqrt(2.0 * (1.0 - cfg["rho"]) * i_star(cfg["H"], cfg["alpha"], cfg["info_divisor"]))


def ew_weights(N):
    """EW direction 1/sqrt(N), defined for every N >= 1."""
    return np.full(N, 1.0 / math.sqrt(N))


def prefix_channels(k, N):
    """Columns of the first k fit axes; refused when k > N."""
    if not 1 <= k <= N:
        raise ValueError(f"spectral prefix k = {k} needs 1 <= k <= N = {N}")
    return list(range(k))


def canonical_eigh(eigval, eigvec):
    """E4 eigen convention: refuse gaps <= 64 eps max(1, lambda_max), stable order, sign by first max-abs entry."""
    eigval = np.array(eigval, dtype=np.float64)
    V = np.asarray(eigvec, dtype=np.float64)
    tol = TIE_FACTOR * np.finfo(np.float64).eps * max(1.0, float(eigval[0]))
    gaps = eigval[:-1] - eigval[1:]
    if (gaps < 0).any():
        raise ArithmeticError("eigenvalues are not in decreasing order")
    blocks = []
    for j in np.flatnonzero(gaps <= tol).tolist():
        if blocks and blocks[-1][1] == j:
            blocks[-1][1] = j + 1
        else:
            blocks.append([j, j + 1])
    if blocks:
        raise EigenTieUnresolved(f"EIGENVALUE_TIE_UNRESOLVED: eigenvalue blocks {blocks} have gaps <= {tol!r}",
                                 blocks, gaps[gaps <= tol].tolist())
    if not np.array_equal(np.argsort(-eigval, kind="stable"), np.arange(eigval.size)):
        raise ArithmeticError("the decreasing eigenvalue order is not stable")
    first = np.argmax(np.abs(V), axis=0)
    signs = np.where(V[first, np.arange(V.shape[1])] < 0, -1.0, 1.0)
    return eigval, V * signs, signs


def fit_splits(T):
    """Registry splits over T drift-free fit rows with synthetic dates before 2020."""
    return {"pretrain": (0, 0), "calib": (0, T), "pre_monitor": (0, T),
            "dates": np.arange(T).astype("datetime64[D]")}


def make_specs(cfg):
    """Registry specifications of the three dictionaries, anytime-valid at gamma_H = H / alpha."""
    g = pipelines.horizon_gamma(cfg["H"], cfg["alpha"])
    return {"SPEC-full": pipelines.make_spec("P3-C", mode="full", channels="all", H=cfg["H"], gamma=g),
            "SPEC-prefix8": pipelines.make_spec("P3-C", mode="full", channels=list(range(cfg["prefix_k"])),
                                                H=cfg["H"], gamma=g),
            "P3-CS(b)": pipelines.make_spec("P3-CS", mode="full", H=cfg["H"], gamma=g)}


def fit_rows(cfg, background, N, space):
    """Contiguous drift-free fit panel (T_fit, N) of a cell."""
    return np.ascontiguousarray(role_path(cfg, space, background, "fit", 0, N, cfg["T_fit"]))


def canonical_state(state, signs):
    """Deep copy of a registry state whose basis columns carry the E4 signs (W for PCA, U for DegreeZero)."""
    out = copy.deepcopy(state)
    rep = out["rep"]
    if "W" in rep.state:
        rep.state["W"] = rep.state["W"] * signs[:rep.state["W"].shape[1]]
    else:
        rep.state["U"] = rep.state["U"] * signs[1:]
    return out


def k_mp_residual(mp_count_total):
    """Residual K_MP: eigenvalues above the Marchenko-Pastur edge minus the market axis PC1, never negative."""
    return max(0, int(mp_count_total) - 1)


def fit_cell(cfg, background, N, space):
    """Frozen null fit of a (background, N) cell: canonical basis, hashes and registry states of the dictionaries."""
    if N < 2:
        raise ValueError(f"N = {N}: P3-CS(b), the residual drift and O-dir need N >= 2")
    prefix_channels(cfg["prefix_k"], N)
    X = fit_rows(cfg, background, N, space)
    basis = pdb.fit_basis(X)
    eigval, V_e4, signs = canonical_eigh(basis["eigval"], basis["eigvec"])
    specs, splits, sigma = make_specs(cfg), fit_splits(len(X)), pdb.equicorrelation(N, cfg["rho"])
    full = canonical_state(pipelines.fit_pipeline(specs["SPEC-full"], X, splits), signs)
    cs = canonical_state(pipelines.fit_pipeline(specs["P3-CS(b)"], X, splits), signs)
    if full["rep"].fit_info["x_sha256"] != cs["rep"].fit_info["x_sha256"]:
        raise ArithmeticError("the registry states were not fitted on the same rows")
    return {"background": background, "N": N, "eigval": eigval, "V_e4": V_e4, "signs": signs,
            "basis_hash_e4": pdb.array_sha256(eigval, V_e4), "basis_hash_legacy": basis["basis_hash"],
            "x_fit_sha256": basis["x_fit_sha256"], "k_mp": k_mp_residual(basis["mp_count"]),
            "mp_count_total": basis["mp_count"], "specs": specs,
            "states": {"SPEC-full": full, "SPEC-prefix8": full, "P3-CS(b)": cs}, "sigma": sigma,
            "vsv": (V_e4 * (sigma @ V_e4)).sum(axis=0)}


def coins_rec(cfg, space, role, i):
    """Registry record of one monitored path: onset at row 0 and the tie-breaking coin key."""
    return {"tau_star": 0, "seed": key(cfg, space, "coins", role, i), "family": role}


def kernel_log_path(spec, x):
    """Log e-detector paths (B, H) of a batch of registry streams x (B, H, D), with the kernels of the registry."""
    if spec["reading"] != "anytime-valid" or spec.get("mixture_s2") is not None:
        raise ValueError("only the anytime-valid dictionary readings of P3-C and P3-CS(b) are supported")
    if spec["pipeline"] == "P3-C":
        return eprocess.log_dictionary_edetector(x, "cusum")
    if spec["pipeline"] == "P3-CS" and spec["variant"] == "b":
        return eprocess.log_dictionary_edetector(x, "cusum", eta0=(pipelines.STAKE_CAP / 2.0,))
    raise ValueError(f"unsupported pipeline {spec['pipeline']!r}")


def rank_first_hit(log_m, h):
    """First monitored day 1..H with log M_t >= h (predictive rank reading), -1 if none."""
    return int(pdb.first_index((np.asarray(log_m, dtype=np.float64) >= h)[None, :])[0])


def horizon_first_hit(log_m, gamma):
    """First monitored day 1..H with M_t >= gamma (anytime-valid horizon reading), -1 if none."""
    off = int(eprocess.first_alarm(np.asarray(log_m, dtype=np.float64), gamma))
    return off + 1 if off >= 0 else -1


def censored_time(first_hit, H):
    """Restricted time min(T, H): the alarm day, or H without alarm."""
    return int(first_hit) if first_hit > 0 else int(H)


def cell_calibration(maxima, alpha):
    """Frozen predictive-rank threshold (GE, nextafter in log space) of calibration maxima, as pdb.calibrate fields."""
    maxima = np.asarray(maxima, dtype=np.float64)
    fields = {"threshold_rule": pdb.THRESHOLD_RULE, "n_cal": int(maxima.size), "maxima_sha256": pdb.array_sha256(maxima),
              "rank_r": None, "threshold_hex": None, "calibration_alarms": None, "calibration_hash": None,
              "status": "CALIBRATION_FAILED"}
    try:
        h, r, alarms = pdb.rank_threshold(maxima, alpha, "GE")
    except pdb.CalibrationFailed:
        return fields
    digest = hashlib.sha256(np.ascontiguousarray(maxima).tobytes() + h.hex().encode()).hexdigest()
    return {**fields, "rank_r": r, "threshold_hex": h.hex(), "calibration_alarms": alarms, "calibration_hash": digest,
            "status": "OK"}


TRIAL_COLUMNS = ["background", "N", "method", "role", "replicate", "reading", "first_hit", "claim_flag"]
TRIAL_KEYS = ["background", "N", "method", "role", "replicate", "reading"]
CAL_COLUMNS = ["background", "N", "method", "claim_flag", "status", "threshold_rule", "n_cal", "maxima_sha256",
               "rank_r", "threshold_hex", "calibration_alarms", "calibration_hash"]
CELL_COLUMNS = ["background", "N", "status", "basis_hash_e4", "basis_hash_legacy", "x_fit_sha256", "k_mp",
                "mp_count_total"]
DIAG_COLUMNS = ["background", "N", "replicate", "claim_flag", "i_star", "i_star_label", "odir_sign_p",
                "odir_sign_kl_bernoulli", "k_star", "a_best", "a_max_plugin", "prefix_retention", "pc1_leakage", "k_mp",
                "mp_count_total", "dictionary_multiplier"]
AXES_COLUMNS = ["background", "N", "replicate", "axis", "j_k", "claim_flag"]


def scalar_calibration(cfg, space):
    """Common frozen rank threshold of the scalar sign detector, from n_cal fair-coin paths 2B - 1 of length H."""
    n, H = counts(cfg, space)["calibration"], cfg["H"]
    B = np.stack([_rng(cfg, space, "scalar_cal", i).integers(0, 2, size=H) for i in range(n)])
    return cell_calibration(eprocess.log_edetector(2.0 * B - 1.0, "cusum").max(axis=1), cfg["alpha"])


def oracle_j(V, delta_mu, sigma, vsv=None):
    """ORACLE J_k = (v_k' dmu)^2 / (2 v_k' Sigma v_k); vsv reuses the fit-level v_k' Sigma v_k exactly."""
    return (V.T @ delta_mu) ** 2 / (2.0 * (np.einsum("ik,ij,jk->k", V, sigma, V) if vsv is None else vsv))


def oracle_k_star(V, delta_mu, sigma, vsv=None):
    """ORACLE fit-basis axis maximizing J_k (first index on ties); the argmax does not depend on the drift scale."""
    return int(np.argmax(oracle_j(V, delta_mu, sigma, vsv)))


def sign_probability(info, a, nu):
    """P(b_t = 1) of a channel holding the fraction a of I*: Phi(sqrt(2 I* a)), or the unit-variance t_nu CDF."""
    from scipy import stats
    z = math.sqrt(2.0 * info * a)
    return float(stats.norm.cdf(z)) if nu is None else float(stats.t.cdf(math.sqrt(nu / (nu - 2.0)) * z, nu))


def prefix_retention(V, k, delta_mu, sigma, info):
    """ORACLE joint Gaussian KL of the first k fit coordinates divided by I* (not a sum of the J_k)."""
    P = V[:, :k]
    a = P.T @ delta_mu
    return float(a @ np.linalg.solve(P.T @ sigma @ P, a) / 2.0 / info)


def oracle_diagnostics(cell, u, cfg):
    """ORACLE diagnostics of one alternative: labelled I*, O-dir sign Bernoulli KL, J_k, a_best, plug-in a_max."""
    nu = cfg["backgrounds"][cell["background"]]
    info = i_star(cfg["H"], cfg["alpha"], cfg["info_divisor"])
    V, N = cell["V_e4"], cell["N"]
    dmu = drift_scale(cfg) * u
    J = oracle_j(V, dmu, cell["sigma"], cell["vsv"])
    z = (V.T @ dmu) ** 2 / cell["eigval"]
    p = sign_probability(info, 1.0, nu)
    a_best = float(J.max() / info)
    return {"claim_flag": "ORACLE_DIAGNOSTIC", "i_star": info,
            "i_star_label": "GAUSSIAN_KL" if nu is None else "INFO_GAUSS_PROXY_T7", "odir_sign_p": p,
            "odir_sign_kl_bernoulli": float(floors.kl_bernoulli_half(p)), "k_star": int(np.argmax(J)), "a_best": a_best,
            "a_max_plugin": float(z.max() / z.sum()),
            "prefix_retention": prefix_retention(V, cfg["prefix_k"], dmu, cell["sigma"], info),
            "pc1_leakage": float((V[:, 0].sum()) ** 2 / N), "k_mp": cell["k_mp"],
            "mp_count_total": cell["mp_count_total"],
            "dictionary_multiplier": floors.dictionary_multiplier(N, pipelines.horizon_gamma(cfg["H"], cfg["alpha"]),
                                                                  a_best), "j_k": J}


def method_stream(method, cell, X, rec, u=None):
    """Monitored stream of one path: scalar signs 2b - 1 (EW, O-dir, O-score1) or the registry stream (H, D)."""
    if (method in ORACLE) != (u is not None):
        raise ValueError(f"{method}: only the oracle methods receive the injected direction")
    if method in DICTIONARY:
        spec = cell["specs"][method]
        return pipelines.PIPELINES[spec["pipeline"]][1](spec, cell["states"][method], X, rec)
    if method == "EW":
        w = ew_weights(cell["N"])
    elif method == "O-dir":
        w = u
    elif method == "O-score1":
        w = cell["V_e4"][:, oracle_k_star(cell["V_e4"], u, cell["sigma"], cell["vsv"])]
    else:
        raise ValueError(f"unknown method {method!r}")
    return 2.0 * exact_sign_stream(X @ w, pipelines._coins(rec))


def method_log_path(method, cell, X, rec, u=None):
    """Log e-detector path (H,) of one monitored path: the batch kernel for dictionaries, log_edetector otherwise."""
    x = method_stream(method, cell, X, rec, u)
    if method in DICTIONARY:
        return kernel_log_path(cell["specs"][method], x[None])[0]
    return eprocess.log_edetector(x, "cusum")


def _cell(cfg, space, background, N, scalar, permute=False):
    gamma_h = pipelines.horizon_gamma(cfg["H"], cfg["alpha"])
    n = counts(cfg, space)
    order = (lambda m: range(m - 1, -1, -1)) if permute else range
    try:
        cell, status = fit_cell(cfg, background, N, space), "OK"
    except EigenTieUnresolved:
        cell, status = {"N": N}, "EIGENVALUE_TIE_UNRESOLVED"
    methods = [m for m in METHODS if status == "OK" or m not in BASIS_METHODS]
    dictionaries = [m for m in DICTIONARY if m in methods]
    maxima = {m: np.empty(n["calibration"]) for m in dictionaries}
    for i in order(n["calibration"]):
        X, rec = role_path(cfg, space, background, "calibration", i, N), coins_rec(cfg, space, "calibration", i)
        for m in dictionaries:
            maxima[m][i] = method_log_path(m, cell, X, rec).max()
    cal = {**{m: dict(scalar) for m in SCALAR if m in methods},
           **{m: cell_calibration(maxima[m], cfg["alpha"]) for m in dictionaries}}
    h = {m: float.fromhex(f["threshold_hex"]) for m, f in cal.items() if f["status"] == "OK"}
    rows, diags, axes, scale = [], [], [], drift_scale(cfg)
    for role in ("holdout", "alternative"):
        for i in order(n[role]):
            u = residual_direction(direction_draw(cfg, space, i), N)
            X = role_path(cfg, space, background, role, i, N)
            if role == "alternative":
                X = X + scale * u
                if status == "OK":
                    d = oracle_diagnostics(cell, u, cfg)
                    axes += [{"background": background, "N": N, "replicate": i, "axis": k, "j_k": float(j),
                              "claim_flag": "ORACLE_DIAGNOSTIC"} for k, j in enumerate(d.pop("j_k"))]
                    diags.append({"background": background, "N": N, "replicate": i, **d})
            rec = coins_rec(cfg, space, role, i)
            for m in methods:
                log_m = method_log_path(m, cell, X, rec, u if m in ORACLE else None)
                base = {"background": background, "N": N, "method": m, "role": role, "replicate": i,
                        "claim_flag": ORACLE.get(m, "NONE")}
                if m in h:
                    rows.append({**base, "reading": "predictive_rank", "first_hit": rank_first_hit(log_m, h[m])})
                rows.append({**base, "reading": "anytime_valid_horizon", "first_hit": horizon_first_hit(log_m, gamma_h)})
    cal_rows = [{"background": background, "N": N, "method": m, "claim_flag": ORACLE.get(m, "NONE"),
                 **cal.get(m, {"status": status})} for m in METHODS]
    cell_row = {"background": background, "N": N, "status": status,
                **{k: cell.get(k) for k in ("basis_hash_e4", "basis_hash_legacy", "x_fit_sha256", "k_mp",
                                            "mp_count_total")}}
    return {"trials": rows, "calibration": cal_rows, "diagnostics": diags, "axes": axes, "cell": cell_row}


def run_cells(cfg, space="science", jobs=1, permute=False):
    """Prototype scientific route: one shared scalar calibration, then every (background, N) cell, as sorted tables."""
    scalar = scalar_calibration(cfg, space)
    tasks = [(cfg, space, bg, N, scalar, permute) for bg in cfg["backgrounds"] for N in cfg["grid"]]
    if jobs > 1:
        with concurrent.futures.ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
            parts = list(pool.map(_cell, *zip(*tasks)))
    else:
        parts = [_cell(*t) for t in tasks]
    def table(name, columns, keys):
        return pd.DataFrame([r for p in parts for r in p[name]], columns=columns).sort_values(
            keys, kind="stable").reset_index(drop=True)
    return {"trials": table("trials", TRIAL_COLUMNS, TRIAL_KEYS),
            "calibration": table("calibration", CAL_COLUMNS, ["background", "N", "method"]),
            "diagnostics": table("diagnostics", DIAG_COLUMNS, ["background", "N", "replicate"]),
            "diagnostics_axes": table("axes", AXES_COLUMNS, ["background", "N", "replicate", "axis"]),
            "cells": pd.DataFrame([p["cell"] for p in parts], columns=CELL_COLUMNS).sort_values(
                ["background", "N"], kind="stable").reset_index(drop=True)}


def holdout_fpr(trials):
    """Holdout false-alarm rate per (background, N, method, reading): alarms / n_hold with its Wilson interval."""
    rows = []
    for (bg, N, m, reading), g in trials[trials["role"] == "holdout"].groupby(
            ["background", "N", "method", "reading"], sort=True):
        alarms, n = int((g["first_hit"] > 0).sum()), len(g)
        lo, hi = wilson(alarms, n)
        rows.append({"background": bg, "N": N, "method": m, "reading": reading, "n_hold": n, "alarms": alarms,
                     "fpr": alarms / n, "fpr_lo": lo, "fpr_hi": hi, "claim_flag": ORACLE.get(m, "NONE")})
    return pd.DataFrame(rows)


def ex_ante(table):
    """Rows of the ex ante methods only (claim_flag NONE)."""
    return table[table["claim_flag"] == "NONE"]


def write_tables(directory, tables):
    """FAIR CSV export of named tables; returns the SHA-256 of each file."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, df in tables.items():
        pipelines.save_fair_csv(df, directory / f"{name}.csv")
        out[name] = pdb.file_sha256(directory / f"{name}.csv")
    return out


CONTRASTS = {"Delta": ("SPEC-full", "O-dir"), "Delta_1": ("O-score1", "O-dir"), "Delta_2": ("SPEC-full", "O-score1")}


def censored_times(first, H):
    """Restricted times min(T, H) of an array of first hits (H for a missing alarm)."""
    first = np.asarray(first)
    return np.where(first > 0, first, H).astype(np.int64)


def rmst_cell(first, H):
    """RMST with its normal interval (deff = 1) and the Wilson detection interval of one cell (pdb._rmst_fields)."""
    return pdb._rmst_fields(np.asarray(first, dtype=np.int64), H)


def boot_indices(cfg, space, role, n):
    """Paired bootstrap replicate indices (B_boot, n) of one role, common to every N and every method."""
    return _rng(cfg, space, "boot", role).integers(0, n, size=(cfg["B_boot"], n))


def ols_slope(x, y):
    """OLS slope of y on x along the last axis (y shifted by its first value, so constant rows give exactly 0)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    y = y - y[..., :1]
    xc = x - x.mean()
    return ((y - y.mean(axis=-1, keepdims=True)) * xc).sum(axis=-1) / (xc * xc).sum()


def _fpr_comparability(alarms, keys_a, keys_b, idx_h, margin):
    verdicts = []
    for ka, kb in zip(keys_a, keys_b):
        if ka not in alarms or kb not in alarms:
            return "NOT_EVALUATED"
        lo, hi = np.percentile(alarms[ka][idx_h].mean(axis=1) - alarms[kb][idx_h].mean(axis=1), [2.5, 97.5])
        verdicts.append(lo >= -margin and hi <= margin)
    return "COMPARABLE_FPR" if all(verdicts) else "COMMON_NOMINAL_ALPHA_ONLY"


def analyse(trials, cfg, space="science", reading="predictive_rank", n=None):
    """Cells and paired-bootstrap contrasts on the whole grid, conditional on the frozen fits and calibrations."""
    H, grid, alpha = cfg["H"], list(cfg["grid"]), cfg["alpha"]
    x = np.log(np.asarray(grid, dtype=np.float64))
    n = counts(cfg, space) if n is None else n
    idx, idx_h = boot_indices(cfg, space, "alternative", n["alternative"]), boot_indices(cfg, space, "holdout", n["holdout"])
    t = trials[trials["reading"] == reading]
    first, alarms = {}, {}
    for (bg, N, m, role), g in t.groupby(["background", "N", "method", "role"], sort=True):
        f = g.sort_values("replicate")["first_hit"].to_numpy()
        if role == "alternative":
            first[(bg, N, m)] = f
        elif role == "holdout":
            alarms[(bg, N, m)] = (f > 0).astype(np.float64)
    cells = []
    for k in sorted(first):
        f = rmst_cell(first[k], H)
        row = {"background": k[0], "N": k[1], "method": k[2], "reading": reading, "claim_flag": ORACLE.get(k[2], "NONE"),
               **{name: f[name] for name in ("n", "deff", "alarms", "rmst", "rmst_se", "rmst_lo", "rmst_hi", "det_rate",
                                              "det_lo", "det_hi")}}
        if k in alarms:
            hits = int(alarms[k].sum())
            lo, hi = wilson(hits, alarms[k].size)
            row.update({"fpr": hits / alarms[k].size, "fpr_lo": lo, "fpr_hi": hi,
                        "fpr_label": "FPR_ABOVE_NOMINAL" if lo > alpha else "NONE"})
        cells.append(row)
    boot_sha = pdb.array_sha256(idx, idx_h)
    rows, draws = [], {}
    for bg in sorted({k[0] for k in first}):
        for name, (a, b) in CONTRASTS.items():
            row = {"background": bg, "reading": reading, "contrast": name, "method_a": a, "method_b": b,
                   "estimate": math.nan, "lo": math.nan, "hi": math.nan, "boot_index_sha256": boot_sha}
            keys_a, keys_b = [(bg, N, a) for N in grid], [(bg, N, b) for N in grid]
            if len(grid) < 2 or not all(k in first for k in keys_a + keys_b):
                rows.append({**row, "qualification": "NOT_IDENTIFIED",
                             "reason": "FEWER_THAN_TWO_N" if len(grid) < 2 else "CELL_REFUSED_OR_MISSING",
                             "label": "NOT_IDENTIFIED" if name == "Delta" else "DESCRIPTIVE",
                             "fpr_comparability": "NOT_EVALUATED"})
                continue
            qualified = min(wilson(int((first[k] > 0).sum()), first[k].size)[0] for k in keys_a + keys_b) >= cfg[
                "qualification"]
            ct = {k: censored_times(first[k], H).astype(np.float64) for k in keys_a + keys_b}
            y = np.array([math.log(ct[ka].mean()) - math.log(ct[kb].mean()) for ka, kb in zip(keys_a, keys_b)])
            yb = np.stack([np.log(ct[ka][idx].mean(axis=1)) - np.log(ct[kb][idx].mean(axis=1))
                           for ka, kb in zip(keys_a, keys_b)], axis=-1)
            draws[(bg, name)] = yb
            lo, hi = np.percentile(ols_slope(x, yb), [2.5, 97.5])
            label = "DESCRIPTIVE"
            if name == "Delta":
                label = ("NOT_IDENTIFIED" if not qualified else "COST_GROWS" if lo > 0 else "COST_SHRINKS" if hi < 0
                         else "NO_GROWTH_DETECTED")
            rows.append({**row, "estimate": float(ols_slope(x, y)), "lo": float(lo), "hi": float(hi),
                         "qualification": "QUALIFIED" if qualified else "NOT_IDENTIFIED",
                         "reason": "" if qualified else "WILSON_DETECTION_BELOW_QUALIFICATION", "label": label,
                         "fpr_comparability": _fpr_comparability(alarms, keys_a, keys_b, idx_h, cfg["fpr_margin"])})
    warnings = []
    for bg in sorted({k[0] for k in first}):
        odir = [(bg, N, "O-dir") for N in grid]
        if len(grid) > 1 and all(k in first for k in odir):
            slopes = ols_slope(x, np.stack([np.log(censored_times(first[k], H).astype(np.float64)[idx].mean(axis=1))
                                            for k in odir], axis=-1))
            lo, hi = np.percentile(slopes, [2.5, 97.5])
            if lo > 0 or hi < 0:
                warnings.append({"background": bg, "N": None, "method": "O-dir", "warning": "WARN_ODIR_SLOPE"})
        for N in grid:
            k = (bg, N, "EW")
            if k in first and k in alarms:
                d_lo, d_hi = wilson(int((first[k] > 0).sum()), first[k].size)
                f_lo, f_hi = wilson(int(alarms[k].sum()), alarms[k].size)
                if d_lo > f_hi or d_hi < f_lo:
                    warnings.append({"background": bg, "N": N, "method": "EW", "warning": "WARN_EW_DETECTION"})
    return {"cells": pd.DataFrame(cells), "contrasts": pd.DataFrame(rows), "draws": draws,
            "warnings": pd.DataFrame(warnings, columns=["background", "N", "method", "warning"])}


def analytic_precheck(cfg):
    """Deterministic one-atom evidence clocks (no draw): a censoring risk, never an RMST, ADD or power."""
    from scipy import stats
    H, alpha = cfg["H"], cfg["alpha"]
    gamma, info, eta = pipelines.horizon_gamma(H, alpha), i_star(H, alpha, cfg["info_divisor"]), 0.05
    lam = 2.0 * np.asarray(eprocess.EDETECTOR_ETA0)

    def growth(p):
        return float(np.max(p * np.log1p(lam) + (1.0 - p) * np.log1p(-lam)))

    rows = []
    for N in cfg["grid"]:
        a = float(stats.beta.isf(eta / N, 0.5, (N - 2) / 2.0))
        for bg, nu in cfg["backgrounds"].items():
            p = sign_probability(info, a, nu)
            g = growth(p)
            clock = math.log(8 * N * gamma) / g
            rows.append({"row_kind": "DICTIONARY_ONE_ATOM", "background": bg if nu is None else f"{bg}_INFO_GAUSS_PROXY_T7",
                         "N": N, "a95_upper": a, "p95_upper": p, "best_grid_log_growth_upper": g,
                         "one_atom_anytime_clock_days": clock, "clock_over_H": clock / H})
    for bg, nu in cfg["backgrounds"].items():
        p = sign_probability(info, 1.0, nu)
        g = growth(p)
        clock = math.log(8 * gamma) / g
        rows.append({"row_kind": "O_DIR_SCALAR", "background": bg if nu is None else f"{bg}_INFO_GAUSS_PROXY_T7", "N": 1,
                     "a95_upper": 1.0, "p95_upper": p, "best_grid_log_growth_upper": g,
                     "one_atom_anytime_clock_days": clock, "clock_over_H": clock / H})
    out = pd.DataFrame(rows)
    out["reading_note"] = "SECONDARY_ANYTIME_CENSORING_RISK_NOT_RMST_ADD_OR_POWER"
    return out


COST_COLUMNS = ["partition", "stage", "n_paths", "n_runs", "cpu_s", "wall_s", "peak_rss_kib", "status"]
PARTITION_KEYS = {"partition", "session_id", "status", "files", "objects"}
SESSION_KEYS = {"session_id", "mode", "config", "code", "environment", "domains", "seed_plan_sha256"}
LOG_KEYS = {"event", "partition", "stage", "status", "session_id", "cpu_s", "wall_s", "peak_rss_kib"}
ENV_VARIABLES = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_CBWR", "PYTHONHASHSEED")
CODE_FILES = ("experiments/e4_alignment.py", "experiments/pca_drift_benchmark.py", "jepadrift/pipelines.py",
              "jepadrift/monitors/eprocess.py", "jepadrift/monitors/streams.py", "jepadrift/stats/covariance.py",
              "jepadrift/stats/intervals.py", "jepadrift/representations/base.py", "jepadrift/representations/pca.py",
              "jepadrift/representations/cross_section.py", "jepadrift/representations/extract.py",
              "jepadrift/floors.py")
CPU_CAP_HOURS = 24.0
INVOCATION_BLOCK_SECONDS = 1500.0
SCENARIOS = ("FULL_GRID", "DROP_N500", "T7_ON_8_64_239")
TOTAL_STAGES = ("invocation", "orchestration")
UNMEASURED = (("workers_parallel", "the pilot runs jobs=1: parallel worker overhead and concurrent memory are unmeasured"),
              ("merge_future_partitions", "merging the partitions of a future campaign is neither implemented nor measured"),
              ("resume_after_interruption", "recomputation after an interrupted partition is not measured"))


class PartitionBlocked(RuntimeError):
    """A BLOCKED_RESOURCE partition is final: its automatic re-run is refused and needs a decision."""


def env_snapshot():
    """Hashed environment snapshot (versions, BLAS, determinism variables), distinct from the pdb.check_env validation."""
    import scipy
    import statsmodels
    blas = np.show_config(mode="dicts").get("Build Dependencies", {}).get("blas", {})
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "pandas": pd.__version__, "statsmodels": statsmodels.__version__,
            "blas": {k: str(blas.get(k)) for k in ("name", "version")},
            "variables": {v: os.environ.get(v) for v in ENV_VARIABLES}}


def session_identity(cfg, mode):
    """Immutable session identity: mode, configuration, code and environment fingerprints, seed domains and plan."""
    body = {"mode": mode, "config": cfg, "code": {p: pdb.file_sha256(REPO_ROOT / p) for p in CODE_FILES},
            "environment": env_snapshot(), "domains": list(DOMAINS), "seed_plan_sha256": seed_plan(cfg)["sha256"]}
    return {"session_id": hashlib.sha256(pdb.canon(body).encode()).hexdigest(), **body}


def partition_dir(pid):
    """Directory of a partition id: '<background>:<N>' becomes '<background>_N<N>'."""
    if ":" in pid:
        background, N = pid.split(":")
        return f"{background}_N{int(N)}"
    return pid


def _write_atomic(path, text):
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def run_partition(out, pid, identity, compute):
    """Atomic partition run: skip a matching COMPLETE one, refuse BLOCKED or divergent ones before writing."""
    out = Path(out)
    parts, session = out / "partitions", out / "session.json"
    final = parts / partition_dir(pid)
    if session.exists() and json.loads(session.read_text(encoding="utf-8")) != identity:
        raise pdb.PartitionMismatch(f"{session} holds another session identity")
    leftovers = sorted(p.name for p in parts.glob(f"{partition_dir(pid)}.tmp-*")) if parts.is_dir() else []
    if final.exists():
        record = json.loads((final / "partition.json").read_text(encoding="utf-8"))
        names = sorted(p.name for p in final.iterdir())
        if (record["session_id"] != identity["session_id"] or record["partition"] != pid
                or names != sorted([*record["files"], "partition.json"])
                or any(pdb.file_sha256(final / f) != h for f, h in record["files"].items())):
            raise pdb.PartitionMismatch(f"partition {pid} differs from its record or from the session")
        if record["status"] != "COMPLETE":
            raise PartitionBlocked(f"partition {pid} is {record['status']}: its re-run needs a decision")
        return "SKIPPED_COMPLETE", leftovers
    if not session.exists():
        out.mkdir(parents=True, exist_ok=True)
        _write_atomic(session, pdb.canon(identity))
    parts.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"{partition_dir(pid)}.tmp-{os.getpid()}-", dir=parts))
    status, objects = compute(tmp)
    files = {p.name: pdb.file_sha256(p) for p in sorted(tmp.iterdir())}
    (tmp / "partition.json").write_text(pdb.canon({"partition": pid, "session_id": identity["session_id"],
                                                   "status": status, "files": files, "objects": objects}),
                                        encoding="utf-8")
    os.replace(tmp, final)
    return status, leftovers


class Meter:
    """Per-stage CPU (user + system), wall time and cumulative process peak RSS (RUSAGE_SELF), kept when interrupted."""

    def __init__(self):
        self.rows = {}

    @contextlib.contextmanager
    def stage(self, name, n_paths):
        r0, t0, finished = resource.getrusage(resource.RUSAGE_SELF), time.perf_counter(), False
        try:
            yield
            finished = True
        finally:
            r1, t1 = resource.getrusage(resource.RUSAGE_SELF), time.perf_counter()
            row = self.rows.setdefault(name, {"stage": name, "n_paths": 0, "n_runs": 0, "interrupted": 0,
                                              "cpu_s": 0.0, "wall_s": 0.0, "peak_rss_kib": 0})
            row["n_paths"] += n_paths if finished else 0
            row["n_runs"] += 1
            row["interrupted"] += 0 if finished else 1
            row["cpu_s"] += (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
            row["wall_s"] += t1 - t0
            row["peak_rss_kib"] = max(row["peak_rss_kib"], r1.ru_maxrss)


def process_cpu_s():
    """Cumulative CPU (user + system) of this process since its start, interpreter start-up and imports included."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def vm_rss_kib():
    """Current resident set size of this process in KiB (Linux /proc/self/status, VmRSS)."""
    with open("/proc/self/status", encoding="ascii") as fh:
        return next(int(line.split()[1]) for line in fh if line.startswith("VmRSS:"))


def guard(bytes_estimate, cfg, deadline):
    """Cooperative check before an allocation or between blocks: ResourceBlocked over the RSS cap or the deadline."""
    if vm_rss_kib() * 1024 + bytes_estimate > cfg["limits"]["rss_gib"] * 2 ** 30:
        raise pdb.ResourceBlocked(f"resident memory plus {bytes_estimate} bytes exceeds {cfg['limits']['rss_gib']} GiB")
    if time.monotonic() > deadline:
        raise pdb.ResourceBlocked("the invocation deadline is exceeded")


def analysis_fixture(cfg, reading):
    """COST_FIXTURE: the effective analyse() on constant alarm tables at the configured dimensions; outputs discarded."""
    n = {"alternative": cfg["n_alt"], "holdout": cfg["n_hold"]}
    parts = [pd.DataFrame({"background": bg, "N": N, "method": m, "role": role, "replicate": np.arange(n[role]),
                           "reading": reading, "first_hit": hit, "claim_flag": ORACLE.get(m, "NONE")},
                          columns=TRIAL_COLUMNS)
             for bg in cfg["backgrounds"] for N in cfg["grid"] for m in METHODS
             for role, hit in (("alternative", cfg["H"] // 2), ("holdout", -1))]
    analyse(pd.concat(parts, ignore_index=True), cfg, "pilot", reading, n)


def pilot_stages(methods=METHODS):
    """Ordered stage names of one pilot cell partition, for the six methods unless restricted."""
    stages = ["startup", "fit_cell"]
    for role in ("calibration", "holdout", "alternative"):
        ms = [m for m in methods if m in DICTIONARY] if role == "calibration" else list(methods)
        stages += [f"draw:{role}"] + [f"{kind}:{m}:{role}" for m in ms for kind in ("stream", "logpath")]
        stages += ["dict_calibration"] if role == "calibration" else [f"readings:{role}"]
    return stages + ["oracle_diagnostics:alternative", "io"]


def _pilot_cell(cfg, background, N, meter, deadline):
    space, n, block, H = "pilot", counts(cfg, "pilot"), cfg["limits"]["block_paths"], cfg["H"]
    gamma_h = pipelines.horizon_gamma(H, cfg["alpha"])
    # ponytail: scalar methods compare against log(gamma_H), a COST_FIXTURE value; no threshold crosses partitions
    done, thresholds, scale, refused = {"startup"}, {}, drift_scale(cfg), set()
    try:
        with meter.stage("fit_cell", 1):
            try:
                cell = fit_cell(cfg, background, N, space)
            except EigenTieUnresolved:
                cell = {"N": N}
                refused = {s for s in pilot_stages() if any(f":{m}:" in s for m in BASIS_METHODS)} | {
                    "draw:calibration", "dict_calibration", "oracle_diagnostics:alternative"}
        done.add("fit_cell")
        methods = [m for m in METHODS if not (refused and m in BASIS_METHODS)]
        for role in ("calibration", "holdout", "alternative"):
            ms = [m for m in methods if m in DICTIONARY] if role == "calibration" else methods
            if not ms:
                continue
            maxima = {m: [] for m in ms}
            for start in range(0, n[role], block):
                stop = min(start + block, n[role])
                guard((stop - start) * H * (1 + max(cfg["grid"])) * 8 * 4, cfg, deadline)
                for i in range(start, stop):
                    with meter.stage(f"draw:{role}", 1):
                        X = role_path(cfg, space, background, role, i, N)
                        u = residual_direction(direction_draw(cfg, space, i), N)
                        X = X + scale * u if role == "alternative" else X
                    rec = coins_rec(cfg, space, role, i)
                    for m in ms:
                        with meter.stage(f"stream:{m}:{role}", 1):
                            x = method_stream(m, cell, X, rec, u if m in ORACLE else None)
                        with meter.stage(f"logpath:{m}:{role}", 1):
                            log_m = (kernel_log_path(cell["specs"][m], x[None])[0] if m in DICTIONARY
                                     else eprocess.log_edetector(x, "cusum"))
                        if role == "calibration":
                            maxima[m].append(float(log_m.max()))
                            continue
                        with meter.stage(f"readings:{role}", 1):
                            rank_first_hit(log_m, thresholds.get(m, math.log(gamma_h)))
                            horizon_first_hit(log_m, gamma_h)
                    if role == "alternative" and not refused:
                        with meter.stage("oracle_diagnostics:alternative", 1):
                            oracle_diagnostics(cell, u, cfg)
            if role == "calibration":
                with meter.stage("dict_calibration", n[role]):
                    for m in ms:
                        fields = cell_calibration(np.asarray(maxima[m]), cfg["alpha"])
                        if fields["status"] == "OK":
                            thresholds[m] = float.fromhex(fields["threshold_hex"])
            done |= {s for s in pilot_stages() if s.endswith(f":{role}")
                     or (role == "calibration" and s == "dict_calibration")}
        status = "COMPLETE"
    except pdb.ResourceBlocked:
        status = "BLOCKED_RESOURCE"
    return status, pilot_stages(), done - refused, refused


def _cost_rows(pid, meter, stages, done, refused=frozenset()):
    rows = []
    for s in stages:
        if s in refused or s not in meter.rows:
            rows.append({"partition": pid, "stage": s, "n_paths": 0, "n_runs": 0, "cpu_s": math.nan,
                         "wall_s": math.nan, "peak_rss_kib": math.nan,
                         "status": "EIGENVALUE_TIE_UNRESOLVED" if s in refused else "NOT_MEASURED"})
        else:
            finished = s in done and not meter.rows[s]["interrupted"]
            rows.append({"partition": pid, **meter.rows[s], "status": "COMPLETE" if finished else "BLOCKED_RESOURCE"})
    return pd.DataFrame(rows, columns=COST_COLUMNS)


def _compute(cfg, pid, meter, deadline, tmp):
    done, refused = {"startup"}, set()
    if pid == "precheck":
        stages, status = ["startup", "precheck", "io"], "COMPLETE"
        with meter.stage("precheck", 1):
            pipelines.save_fair_csv(analytic_precheck(cfg), tmp / "analytic_precheck.csv")
        done.add("precheck")
    elif pid == "scalar_cal":
        stages = ["startup", "scalar_cal"] + [f"analysis_fixture:{r}" for r in READINGS] + ["io"]
        try:
            guard(counts(cfg, "pilot")["calibration"] * cfg["H"] * 8 * 4, cfg, deadline)
            with meter.stage("scalar_cal", counts(cfg, "pilot")["calibration"]):
                scalar_calibration(cfg, "pilot")
            done.add("scalar_cal")
            for reading in READINGS:
                guard(cfg["B_boot"] * (cfg["n_alt"] + cfg["n_hold"]) * 8 * 3, cfg, deadline)
                with meter.stage(f"analysis_fixture:{reading}", cfg["n_alt"]):
                    analysis_fixture(cfg, reading)
                done.add(f"analysis_fixture:{reading}")
            status = "COMPLETE"
        except pdb.ResourceBlocked:
            status = "BLOCKED_RESOURCE"
    else:
        background, N = pid.split(":")
        status, stages, cell_done, refused = _pilot_cell(cfg, background, int(N), meter, deadline)
        done |= cell_done
    with meter.stage("io", 1):
        pipelines.save_fair_csv(_cost_rows(pid, meter, stages, done, refused), tmp / "cost.csv")
    rows = _cost_rows(pid, meter, stages, done | {"io"}, refused)
    total = process_cpu_s()
    totals = pd.DataFrame([
        {"partition": pid, "stage": "invocation", "n_paths": 0, "n_runs": 1, "cpu_s": total, "wall_s": math.nan,
         "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "status": "MEASURED_PROCESS_TOTAL"},
        {"partition": pid, "stage": "orchestration", "n_paths": 0, "n_runs": 1,
         "cpu_s": total - float(rows["cpu_s"].sum()), "wall_s": math.nan, "peak_rss_kib": math.nan,
         "status": "MEASURED_RESIDUAL"}], columns=COST_COLUMNS)
    pipelines.save_fair_csv(pd.concat([rows, totals], ignore_index=True), tmp / "cost.csv")
    return status, {}


def _alarm(signum, frame):
    raise pdb.ResourceBlocked("the invocation time limit is reached")


def _log(path, partition, rows, status, session_id):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({"event": "stage", "partition": partition, "stage": r["stage"], "status": r["status"],
                                 "session_id": session_id, "cpu_s": r["cpu_s"], "wall_s": r["wall_s"],
                                 "peak_rss_kib": r["peak_rss_kib"]}, sort_keys=True) + "\n")
        usage = resource.getrusage(resource.RUSAGE_SELF)
        fh.write(json.dumps({"event": "invocation_end", "partition": partition, "stage": "all", "status": status,
                             "session_id": session_id, "cpu_s": usage.ru_utime + usage.ru_stime, "wall_s": None,
                             "peak_rss_kib": usage.ru_maxrss}, sort_keys=True) + "\n")


def stage_factor(stage, cfg):
    """Multiplier from the pilot to the future campaign for one measured stage (cost table of plan D8)."""
    full = {"calibration": cfg["n_cal"], "holdout": cfg["n_hold"], "alternative": cfg["n_alt"]}
    p = cfg["pilot_n"]
    if stage in ("startup", "fit_cell", "precheck") or stage.startswith("analysis_fixture:"):
        return 1.0
    if stage == "scalar_cal":
        return cfg["n_cal"] / p
    if stage == "dict_calibration":
        return cfg["n_cal"] * math.log(cfg["n_cal"]) / (p * math.log(p))
    if stage == "io":
        return cfg["n_alt"] / p
    kind, role = stage.split(":", 1)[0], stage.rsplit(":", 1)[-1]
    if kind in ("draw", "stream", "logpath", "readings", "oracle_diagnostics") and role in full:
        return full[role] / p
    raise ValueError(f"unmapped pilot stage {stage!r}")


def forecast(rows, cfg, invocation_totals=None):
    """ESTIMATE under Q6(a): consumed CPU (process totals, else stage sums) plus projections, in fallback order."""
    is_total = rows["stage"].isin(TOTAL_STAGES)
    consumed = 0.0
    partitions = set(rows["partition"])
    if invocation_totals is not None:
        partitions.update(invocation_totals)
    for pid in sorted(partitions):
        part = rows[rows["partition"] == pid]
        if invocation_totals is not None and pid in invocation_totals:
            consumed += float(invocation_totals[pid])
        elif (part["stage"] == "invocation").any():
            consumed += float(part.loc[part["stage"] == "invocation", "cpu_s"].sum())
        else:
            consumed += float(part.loc[part["status"].isin(["COMPLETE", "BLOCKED_RESOURCE"]), "cpu_s"].sum())

    def projected(pid):
        part = rows[(rows["partition"] == pid) & ~is_total]
        if part.empty or (part["status"] != "COMPLETE").any():
            return None
        work = part[part["stage"] != "startup"]
        factors = [stage_factor(s, cfg) for s in work["stage"]]
        wall = float((work["wall_s"] * factors).sum())
        fixed = float(part.loc[part["stage"] == "startup", "cpu_s"].sum()) + float(
            rows.loc[(rows["partition"] == pid) & (rows["stage"] == "orchestration"), "cpu_s"].sum())
        return float((work["cpu_s"] * factors).sum()) + fixed * max(1, math.ceil(wall / INVOCATION_BLOCK_SECONDS))

    heavy = [bg for bg, nu in cfg["backgrounds"].items() if nu is not None]
    grids = {"FULL_GRID": {bg: list(cfg["grid"]) for bg in cfg["backgrounds"]},
             "DROP_N500": {bg: [N for N in cfg["grid"] if N != 500] for bg in cfg["backgrounds"]},
             "T7_ON_8_64_239": {bg: [N for N in cfg["grid"] if N != 500 and (bg not in heavy or N in (8, 64, 239))]
                                for bg in cfg["backgrounds"]}}
    shared, cap, scenarios = projected("scalar_cal"), CPU_CAP_HOURS * 3600.0, []
    for name in SCENARIOS:
        parts = [projected(f"{bg}:{N}") for bg, Ns in grids[name].items() for N in Ns]
        if shared is None or any(p is None for p in parts):
            total, status = math.nan, "INCOMPLETE"
        else:
            total = consumed + shared + sum(parts)
            status = "WITHIN_CAP" if total <= cap else "OVER_CAP"
        scenarios.append({"scenario": name, "n_cells": len(parts), "total_cpu_s": total, "cap_cpu_s": cap,
                          "status": status})
    recommended = "STOP"
    for s in scenarios:
        if s["status"] == "INCOMPLETE":
            break
        if s["status"] == "WITHIN_CAP":
            recommended = s["scenario"]
            break
    items = list(UNMEASURED)
    if not set(rows["partition"]) <= set(rows.loc[rows["stage"] == "orchestration", "partition"]):
        items.append(("invocation_orchestration",
                      "interpreter, import and bookkeeping CPU outside the stages is unmeasured for some partitions"))
    if invocation_totals is None:
        items.append(("invocation_tail_after_last_measure",
                      "final cost.csv write, partition hashing, rename and logging; see the invocation_end log events"))
    unmeasured = pd.DataFrame([{"item": item, "assumption": text, "cpu_s": math.nan, "status": "UNMEASURED_ASSUMPTION"}
                               for item, text in items])
    return {"label": "ESTIMATE", "consumed_cpu_s": consumed, "scenarios": pd.DataFrame(scenarios),
            "unmeasured": unmeasured, "recommended": recommended}


def main(argv=None):
    """CLI: --mode precheck|pilot|full --partition ID --out DIR --log-dir DIR [--jobs 1] [--config PATH]."""
    ap = argparse.ArgumentParser(description="E4 fixed-information N scan: analytic precheck and cost pilot only")
    ap.add_argument("--mode", required=True, choices=("precheck", "pilot", "full"))
    ap.add_argument("--partition")
    ap.add_argument("--out")
    ap.add_argument("--log-dir")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--config", default=str(CONFIG))
    args = ap.parse_args(argv)
    if args.mode == "full":
        print("E4 full campaign refused: it requires the researcher's separate execution GO", file=sys.stderr)
        return 3
    if args.jobs != 1 or not args.out or not args.log_dir:
        print("the E4 precheck and pilot need --jobs 1, --out and --log-dir", file=sys.stderr)
        return 5
    problems = pdb.check_env()
    if problems:
        print("environment refused: " + "; ".join(problems), file=sys.stderr)
        return 5
    meter, started = Meter(), time.monotonic()
    with meter.stage("startup", 0):
        cfg = validate_config(load_config(args.config))
        identity = session_identity(cfg, args.mode)
    valid = {"precheck"} if args.mode == "precheck" else (
        {"scalar_cal"} | {f"{bg}:{N}" for bg in cfg["backgrounds"] for N in cfg["grid"]})
    if args.partition not in valid:
        print(f"unknown partition {args.partition!r} for mode {args.mode}", file=sys.stderr)
        return 5
    compute = functools.partial(_compute, cfg, args.partition, meter, started + cfg["limits"]["invocation_seconds"])
    previous = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(max(1, int(cfg["limits"]["invocation_seconds"])))
    try:
        status, leftovers = run_partition(args.out, args.partition, identity, compute)
    except (pdb.PartitionMismatch, PartitionBlocked) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 5
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
    if leftovers:
        print(f"incomplete temporary partitions left untouched: {leftovers}", file=sys.stderr)
    final = Path(args.out) / "partitions" / partition_dir(args.partition) / "cost.csv"
    rows = [] if status == "SKIPPED_COMPLETE" else pd.read_csv(final, float_precision="round_trip").to_dict("records")
    _log(Path(args.log_dir) / f"{Path(args.out).name}.jsonl", args.partition, rows, status, identity["session_id"])
    print(f"{args.partition}: {status}")
    return 0 if status in ("COMPLETE", "SKIPPED_COMPLETE") else 4


if __name__ == "__main__":
    sys.exit(main())
