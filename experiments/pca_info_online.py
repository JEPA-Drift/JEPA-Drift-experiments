"""Stream 32 PCA-INFO-ONLINE kernels (plan prompts/plans/plan-32.md, lot A): cardinality costs and subset selection."""
import argparse
import hashlib
import io
import itertools
import json
import math
import os
import multiprocessing
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path, PurePosixPath

import numpy as np
import pandas
import scipy
import statsmodels
import yaml
from scipy.optimize import brentq
from scipy.stats import beta, norm

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import pca_drift_benchmark as pdb
from jepadrift import pipelines

mixture_cost = pdb.mixture_cost
ORDERS = ("INFO", "PREFIX")


def affine_ols(gamma, K, d_max=16):
    """(a, c, info): AFF_OLS_1_16, the OLS line of M(d, gamma) on d = 1..min(d_max, K), with its maximal residuals."""
    if not all(isinstance(v, (int, np.integer)) and not isinstance(v, bool) for v in (K, d_max)) or min(d_max, K) < 2:
        raise ValueError(f"the OLS cost needs integers K, d_max with min(d_max, K) >= 2, got K={K!r}, d_max={d_max!r}")
    n = int(min(d_max, K))
    d = np.arange(1.0, K + 1.0)
    M = np.array([mixture_cost(k, gamma) for k in range(1, K + 1)])
    dc = d[:n] - d[:n].mean()
    c = float(dc @ (M[:n] - M[:n].mean()) / (dc @ dc))
    a = float(M[:n].mean() - c * d[:n].mean())
    if not (math.isfinite(a) and math.isfinite(c) and a > 0.0 and c > 0.0):
        raise ArithmeticError(f"the OLS cost needs finite a, c > 0, got a={a!r}, c={c!r}")
    resid = np.abs(M - (a + c * d))
    return a, c, {"identity": "AFF_OLS_1_16", "range": (1, n), "max_abs_resid_fit": float(resid[:n].max()),
                  "max_abs_resid_1K": float(resid.max())}


def cost_vectors(gamma, K):
    """{"MIX": M(d, gamma), "AFF": a + c d} for d = 1..K, with (a, c) from affine_ols(gamma, K)."""
    a, c, _ = affine_ols(gamma, K)
    return {"MIX": np.array([mixture_cost(k, gamma) for k in range(1, K + 1)]), "AFF": a + c * np.arange(1, K + 1)}


def best_sets(q, cost, order):
    """(d (B,), mask (B, K)): argmax of I(S)/cost[|S|-1], INFO over top-q sets, PREFIX over prefixes, smallest d on ties."""
    q, cost = np.asarray(q, dtype=np.float64), np.asarray(cost, dtype=np.float64)
    if order not in ORDERS or q.ndim != 2 or q.shape[1] < 1 or cost.shape != (q.shape[1],):
        raise ValueError(f"need q (B, K >= 1), cost (K,) and order in {ORDERS}, got {q.shape}, {cost.shape}, {order!r}")
    if not (np.isfinite(q).all() and (q >= 0.0).all() and np.isfinite(cost).all() and (cost > 0.0).all()):
        raise ValueError("q must be finite and nonnegative, cost finite and positive")
    B, K = q.shape
    idx = np.argsort(-q, axis=1, kind="stable") if order == "INFO" else np.broadcast_to(np.arange(K), (B, K))
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        d = np.argmax(np.cumsum(np.take_along_axis(q, idx, axis=1), axis=1) / cost, axis=1) + 1
    mask = np.zeros((B, K), dtype=bool)
    np.put_along_axis(mask, idx, np.arange(K) < d[:, None], axis=1)
    return d, mask


def _scores(Y):
    Y = np.asarray(Y, dtype=np.float64)
    if Y.ndim != 3 or Y.shape[1] < 1 or Y.shape[2] < 1 or not np.isfinite(Y).all():
        raise ValueError(f"Y must be a finite (B, H, K) array with H, K >= 1, got shape {Y.shape}")
    return Y


def online_masks(Y, window, cost, order):
    """(B, H, K) predictable masks: axis 0 at t = 1, then best_sets of qhat from the last min(window, t - 1) scores."""
    Y, cost = _scores(Y), np.asarray(cost, dtype=np.float64)
    B, H, K = Y.shape
    if isinstance(window, bool) or not isinstance(window, (int, np.integer)) or window < 1:
        raise ValueError(f"window must be an integer >= 1, got {window!r}")
    if order not in ORDERS or cost.shape != (K,) or not (np.isfinite(cost).all() and (cost > 0.0).all()):
        raise ValueError(f"cost must be finite positive of shape ({K},) and order in {ORDERS}, got {order!r}")
    t = np.arange(1, H)
    m = np.minimum(min(int(window), H), t)
    C = np.zeros((B, H + 1, K))
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        np.cumsum(Y, axis=1, out=C[:, 1:])
        mean = (C[:, t] - C[:, t - m]) / m[:, None]
        q = 0.5 * np.maximum(0.0, mean * mean - 1.0 / m[:, None])
    M = np.zeros((B, H, K), dtype=bool)
    M[:, 0, 0] = True
    M[:, 1:] = best_sets(q.reshape(-1, K), cost, order)[1].reshape(B, H - 1, K)
    return M


def masked_scan(Y, M, s2, h=None):
    """(W, first): masked mixture log-likelihood maximized over all starts; first 1-based t with W_t >= h, else -1."""
    Y, M = _scores(Y), np.asarray(M)
    if M.dtype != bool or M.shape != Y.shape:
        raise ValueError(f"M must be a bool array of shape {Y.shape}, got {M.dtype} {M.shape}")
    if np.ndim(s2) != 0 or not (math.isfinite(s2) and s2 > 0.0):
        raise ValueError(f"s2 must be a finite positive scalar, got {s2!r}")
    if h is not None and (np.ndim(h) != 0 or math.isnan(h)):
        raise ValueError(f"h must be None or a scalar threshold, got {h!r}")
    B, H, K = Y.shape
    N, D, W = np.zeros((B, H + 1, K), dtype=np.int64), np.zeros((B, H + 1, K)), np.empty((B, H))
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        np.cumsum(M, axis=1, dtype=np.int64, out=N[:, 1:])
        np.cumsum(np.where(M, Y, 0.0), axis=1, out=D[:, 1:])
        for t in range(1, H + 1):
            n, d = N[:, t, None] - N[:, :t], D[:, t, None] - D[:, :t]
            W[:, t - 1] = (-0.5 * np.log1p(n * s2) + s2 * d * d / (2.0 * (1.0 + n * s2))).sum(axis=-1).max(axis=1)
    hit = np.zeros((B, H), dtype=bool) if h is None else W >= h
    return W, np.where(hit.any(axis=1), hit.argmax(axis=1) + 1, -1)


def _count(v, name, low=0):
    if isinstance(v, bool) or not isinstance(v, (int, np.integer)) or int(v) < low:
        raise ValueError(f"{name} must be an integer >= {low}, got {v!r}")
    return int(v)


def _tail(tail):
    if not (np.ndim(tail) == 0 and 0.0 < tail < 0.5):
        raise ValueError(f"tail must lie in (0, 0.5), got {tail!r}")
    return float(tail)


def _discordances(b, c, n):
    b, c, n = _count(b, "b"), _count(c, "c"), _count(n, "n", 1)
    if b + c > n:
        raise ValueError(f"need b + c <= n, got b={b}, c={c}, n={n}")
    return b, c, n


def _tango_qtilde(b, c, n, delta0):
    """Constrained MLE of p01 given p10 - p01 = delta0 [Tango, 1998]; roundoff below 1e-12 of the terms is absorbed."""
    b, c, n = _discordances(b, c, n)
    if not (np.ndim(delta0) == 0 and -1.0 < delta0 < 1.0):
        raise ValueError(f"delta0 must lie in (-1, 1), got {delta0!r}")
    d = float(delta0)
    if b + c == n:
        return (1.0 - d) / 2.0
    W, C = -b - c + (2 * n - b + c) * d, c * d * (1.0 - d)
    disc = W * W + 8 * n * C
    if disc < -1e-12 * (W * W + abs(8 * n * C)):
        raise ArithmeticError(f"materially negative Tango discriminant {disc!r}")
    s = math.sqrt(max(disc, 0.0))
    q = 2.0 * C / (W + s) if W > 0 else (s - W) / (4.0 * n)
    lo, hi = max(0.0, -d), (1.0 - d) / 2.0
    if not lo - 1e-12 <= q <= hi + 1e-12:
        raise ArithmeticError(f"constrained MLE {q!r} outside [{lo!r}, {hi!r}]")
    return min(max(q, lo), hi)


def _tango_score(b, c, n, delta0):
    """Tango score Z(delta0), stable variance form; only negative roundoff within 1e-12 of the terms is zeroed."""
    q, d = _tango_qtilde(b, c, n, delta0), float(delta0)
    v = 2.0 * (q + d) - d * (1.0 + d) if d < 0.0 else 2.0 * q + d * (1.0 - d)
    if v < -1e-12 * (2.0 * q + abs(d * (1.0 - d))):
        raise ArithmeticError(f"materially negative Tango variance {v!r} at delta0 = {d!r}")
    num = b - c - n * d
    if v <= 0.0:
        return 0.0 if num == 0.0 else math.copysign(math.inf, num)
    return num / math.sqrt(n * v)


def tango_interval(b, c, n, tail):
    """Asymptotic Tango score interval (lo, hi) for p10 - p01 [Tango, 1998]; no finite-sample coverage claim."""
    b, c, n = _discordances(b, c, n)
    z = float(norm.isf(_tail(tail)))
    if b == c == 0:
        h = z * z / (n + z * z)
        return -h, h
    dhat, a, e = (b - c) / n, math.nextafter(-1.0, 0.0), math.nextafter(1.0, 0.0)

    def score(x):
        return _tango_score(b, c, n, x)

    lo = -1.0 if dhat == -1.0 or score(a) <= z else brentq(lambda x: score(x) - z, a, min(dhat, e), xtol=1e-15)
    hi = 1.0 if dhat == 1.0 or score(e) >= -z else brentq(lambda x: score(x) + z, max(dhat, a), e, xtol=1e-15)
    return lo, hi


def cp_bounds(k, n, tail):
    """One-sided Clopper-Pearson bounds (lo, hi) of k/n at tail each; lo = 0 at k = 0 and hi = 1 at k = n."""
    k, n, tail = _count(k, "k"), _count(n, "n", 1), _tail(tail)
    if k > n:
        raise ValueError(f"need k <= n, got k={k}, n={n}")
    return (0.0 if k == 0 else float(beta.ppf(tail, k, n - k + 1)),
            1.0 if k == n else float(beta.isf(tail, k + 1, n - k)))


def null_status(k, n, alpha, eps, tail):
    """NULL_VALIDATED iff CP upper <= alpha + eps, NULL_FAILED iff CP lower > alpha + eps, else NULL_INCONCLUSIVE."""
    if not (np.ndim(alpha) == 0 and np.ndim(eps) == 0 and math.isfinite(alpha) and math.isfinite(eps)):
        raise ValueError(f"alpha and eps must be finite scalars, got {alpha!r}, {eps!r}")
    lo, hi = cp_bounds(k, n, tail)
    limit = alpha + eps
    return "NULL_VALIDATED" if hi <= limit else "NULL_FAILED" if lo > limit else "NULL_INCONCLUSIVE"


def null_score_bias(c, var0, m):
    """Offline diagnostic only: unclipped H0 mean 0.5 (c**2 + (var0 - 1)/m) of the window score before clipping."""
    m = _count(m, "m", 1)
    c, var0 = np.asarray(c, dtype=np.float64), np.asarray(var0, dtype=np.float64)
    if not (np.isfinite(c).all() and np.isfinite(var0).all() and (var0 >= 0.0).all()):
        raise ValueError("c must be finite and var0 finite and nonnegative")
    with np.errstate(over="raise", invalid="raise"):
        out = 0.5 * (c * c + (var0 - 1.0) / m)
    return float(out) if out.ndim == 0 else out


def _null_plan_counts(counts):
    if not (isinstance(counts, dict) and set(counts) == {"n", "pairs", "alarms"}):
        raise ValueError("counts must be a dict with exactly the keys n, pairs and alarms")
    pairs, alarms = counts["pairs"], counts["alarms"]
    if not (isinstance(pairs, dict) and isinstance(alarms, dict) and pairs and alarms):
        raise ValueError("counts['pairs'] and counts['alarms'] must be nonempty dicts")
    n = _count(counts["n"], "n", 1)
    ks = {name: _count(k, f"alarms[{name!r}]") for name, k in alarms.items()}
    if not all(isinstance(name, str) for name in ks) or max(ks.values()) > n:
        raise ValueError(f"alarms need policy-name keys and counts 0 <= k <= n = {n}")
    out = {}
    for name, row in pairs.items():
        first, second = name.split("|") if isinstance(name, str) and name.count("|") == 1 else (None, None)
        if first == second or first not in ks or second not in ks:
            raise ValueError(f"pair {name!r} must be 'A|B' over two distinct alarm policies")
        if not (isinstance(row, dict) and set(row) == {"b", "c"}):
            raise ValueError(f"pair {name!r} needs exactly the keys b and c")
        b, c, _ = _discordances(row["b"], row["c"], n)
        joint = ks[first] - b
        if joint != ks[second] - c or joint < 0 or n - joint - b - c < 0:
            raise ValueError(f"pair {name!r} is inconsistent with the alarm counts")
        out[name] = (b, c)
    return n, out, ks


def plan_holdout(counts, alpha, m, eps, eps_v, beta, eta, n_min, n_cap):
    """Per-contrast normal-approximation HOLDOUT size from null counts only; no family-power or finite-sample claim."""
    n, pairs, alarms = _null_plan_counts(counts)
    m, n_min, n_cap, eta = _count(m, "m", 1), _count(n_min, "n_min", 1), _count(n_cap, "n_cap", 1), _tail(eta)
    for name, v, high in (("alpha", alpha, 1.0), ("beta", beta, 1.0),
                          ("eps", eps, math.inf), ("eps_v", eps_v, math.inf)):
        if not (np.ndim(v) == 0 and 0.0 < v < high):
            raise ValueError(f"{name} must lie in (0, {high}), got {v!r}")
    if n_min > n_cap:
        raise ValueError(f"need n_min <= n_cap, got {n_min} > {n_cap}")
    za, zeq, zb, zv = (float(norm.isf(p)) for p in (alpha / m, beta / 2, beta, 0.05))
    if not all(math.isfinite(z) for z in (za, zeq, zb, zv)):
        raise ValueError(f"alpha/m, beta/2 and beta must give finite normal quantiles, got {(za, zeq, zb, zv)}")
    rows, policies = {}, {}
    for name, (b, c) in pairs.items():
        D, delta = cp_bounds(b + c, n, eta)[1], max(abs(x) for x in tango_interval(b, c, n, eta))
        rows[name] = {"D_plus": D, "delta_abs_plus": delta,
                      "n_eq": math.ceil(D * (za + zeq) ** 2 / (eps - delta) ** 2) if delta < eps else None}
    for name, k in alarms.items():
        F = cp_bounds(k, n, eta)[1]
        n_v = math.ceil(F * (1 - F) * (zv + zb) ** 2 / (alpha + eps_v - F) ** 2) if F < alpha + eps_v else None
        policies[name] = {"F_plus": F, "n_v": n_v}
    sizes = [n_min, *(row["n_eq"] for row in rows.values()), *(row["n_v"] for row in policies.values())]
    n_req = None if None in sizes else max(sizes)
    details = {"z_a": za, "z_eq": zeq, "z_b": zb, "z_v": zv, "n_req": n_req, "pairs": rows, "policies": policies}
    if n_req is not None and n_req <= n_cap:
        return n_req, "PLAN_ADEQUATE", details
    return n_cap, "PLAN_CAPPED_EXPECT_INCONCLUSIVE", details


class AuthorizationRefused(RuntimeError):
    """A design, GO reference or jobs count that does not match its authorization, refused before any side effect."""


SCHEMA_VERSION = "pca_info_online/1"
MODES = ("smoke", "pilot", "full")
SCIENCE = ("parameters", "applications", "families", "policies", "dev", "null_status", "bootstrap", "phi", "head")
CFG_KEYS = frozenset({*SCIENCE, "seed", "modes", "scope", "envelope"})
SIZE_ROLES = ("DEV_LIB", "DEV_NULL", "DEV_ALT", "CAL_NULL", "HOLD_NULL", "ALT")
PATH_ROLES = ("DEV_NULL", "DEV_ALT", "CAL_NULL", "NULL_PLAN", "HOLD_NULL", "ALT")
DEV_FAMILIES = ("F0_ISOTROPIC_RESIDUAL", "F1_TAIL_RESIDUAL", "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL")
ENVELOPE = ("memory_max_gib", "cpu_hours_max", "wall_seconds_per_invocation", "jobs_max")
CODE_ROOT = REPO_ROOT = pdb.REPO_ROOT
CODE_FILES = ("experiments/pca_info_online.py", "experiments/pca_drift_benchmark.py",
              *(module.replace(".", "/") + ".py" for module in pdb.CODE_MODULES))


def _word(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, np.integer)) or not 0 <= int(v) < 2 ** 32:
        raise ValueError(f"{name} must be an integer in [0, 2**32), got {v!r}")
    return int(v)


def _check_cfg(cfg, mode):
    if not (isinstance(cfg, dict) and set(cfg) - {"authorization"} == CFG_KEYS and mode in MODES):
        raise ValueError(f"need a mode in {MODES} and exactly the keys {sorted(CFG_KEYS)} plus authorization")
    run, scope, dev = cfg["modes"].get(mode), cfg["scope"], cfg["dev"]
    if not (isinstance(run, dict) and {"sizes", "null_plan"} <= set(run) <= {"sizes", "null_plan", "allocation"}
            and set(run["sizes"]) == set(SIZE_ROLES)):
        raise ValueError(f"modes[{mode!r}] needs a null_plan and sizes for exactly {SIZE_ROLES}")
    for role, n in run["sizes"].items():
        _word(n, f"sizes[{role!r}]")
    if "allocation" in run:
        _check_allocation(cfg, mode, run)
    for key in ("n_min", "n_plan", "n_cap") if run["null_plan"] is not None else ():
        _word(run["null_plan"][key], f"null_plan[{key!r}]")
    if set(scope) != {"setups", "applications", "families", "policies"}:
        raise ValueError("scope needs exactly setups, applications, families and policies")
    if not (set(scope["applications"]) <= set(cfg["applications"]) and set(scope["families"]) <= set(cfg["families"])):
        raise ValueError("scope applications and families must be declared in the configuration")
    for arm, N, fit_id in [*scope["setups"], cfg["phi"]["setup"]]:
        if not isinstance(arm, str):
            raise ValueError(f"a setup arm must be a label, got {arm!r}")
        _word(N, "N")
        _word(fit_id, "fit_id")
    logical = [[pdb.canon([label, int(size), int(fid)]) for label, size, fid in scope["setups"]],
               *([pdb.canon(entry) for entry in scope[name]] for name in ("applications", "families", "policies"))]
    if not all(entries and len(set(entries)) == len(entries) for entries in logical):
        raise ValueError("every scope member needs at least one entry and no duplicate canonical entry")
    if sorted(dev["families"]) != sorted(DEV_FAMILIES) or dev["n_lib"] != run["sizes"]["DEV_LIB"]:
        raise ValueError(f"DEV pools exactly {DEV_FAMILIES}, with n_lib equal to the consumed sizes['DEV_LIB']")
    if set(cfg["envelope"]) != set(ENVELOPE) or _word(cfg["envelope"]["jobs_max"], "jobs_max") < 1:
        raise ValueError(f"envelope needs exactly {ENVELOPE} with jobs_max >= 1")
    _word(cfg["seed"], "seed")


def _check_allocation(cfg, mode, run):
    allocation = run["allocation"]
    fields = {"primary_cal_null", "hold_block_rows", "fpr_equivalence", "fit_scope"}
    if not (isinstance(allocation, dict) and set(allocation) == fields):
        raise ValueError(f"allocation must have exactly the fields {sorted(fields)}")
    n_cal = _word(allocation["primary_cal_null"], "primary_cal_null")
    block = _word(allocation["hold_block_rows"], "hold_block_rows")
    if n_cal <= run["sizes"]["CAL_NULL"] or not 1 <= block <= 1000:
        raise ValueError("allocation needs primary_cal_null above CAL_NULL and hold_block_rows in [1, 1000]")
    if (allocation["fpr_equivalence"] != "TANGO_ASYMPTOTIC" or allocation["fit_scope"] != "FIT_CONDITIONAL"):
        raise ValueError("allocation requires TANGO_ASYMPTOTIC and FIT_CONDITIONAL")
    null_plan, phi, scope = run["null_plan"], cfg["phi"], cfg["scope"]
    if not (mode in ("smoke", "full") and isinstance(null_plan, dict)
            and set(null_plan) == {"eta", "beta", "n_min", "n_plan", "n_cap"}
            and phi["setup"] in scope["setups"] and phi["application"] == "RESIDUAL"
            and "RESIDUAL" in scope["applications"] and set(P_CONF) <= set(scope["policies"])):
        raise ValueError("allocation requires a scoped RESIDUAL primary, P_CONF and NULL_PLAN in smoke or full")
    n_min, n_plan, n_cap = (_word(null_plan[key], key) for key in ("n_min", "n_plan", "n_cap"))
    if not (0 < n_min == run["sizes"]["HOLD_NULL"] <= n_cap and n_plan > 0
            and all(arm in ("EXACT", "FITTED_LW_GAUSSIAN") and fit_id == 0 for arm, _, fit_id in scope["setups"])):
        raise ValueError("allocation requires Gaussian fit 0, positive n_plan and HOLD_NULL = n_min <= n_cap")


def _environment():
    blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
    return {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
            "pandas": pandas.__version__, "pyyaml": yaml.__version__, "statsmodels": statsmodels.__version__,
            "blas": [blas.get("name"), blas.get("version")],
            "variables": {k: os.environ.get(k) for k in pdb.REQUIRED_ENV}}


def seed_plan(cfg, mode):
    """All seed keys of a design known before any draw: sorted primitive tuples and the SHA-256 of their entropies."""
    _check_cfg(cfg, mode)
    campaign, seed, scope, dev = mode.upper(), int(cfg["seed"]), cfg["scope"], cfg["dev"]["families"]
    run = cfg["modes"][mode]
    sizes, null_plan, allocation = run["sizes"], run["null_plan"], run.get("allocation")
    setups, primary = [(arm, int(N), int(fid)) for arm, N, fid in scope["setups"]], tuple(cfg["phi"]["setup"])
    keys = [("frame", campaign, N) for N in sorted({s[1] for s in setups})]
    for s in setups:
        n = {role: int(sizes.get(role, 0)) for role in PATH_ROLES}
        if null_plan is not None and s == primary:
            n.update(NULL_PLAN=int(null_plan["n_plan"]), HOLD_NULL=int(null_plan["n_cap"]))
            if allocation is not None:
                n["CAL_NULL"] = int(allocation["primary_cal_null"])
        keys += [("fit", campaign, *s)] if s[0] != "EXACT" else []
        keys += [("path", campaign, *s, r, i) for r in PATH_ROLES for i in range(n[r])]
        keys += [("meta", campaign, *s, "DEV_ALT", f, i) for f in dev for i in range(n["DEV_ALT"])]
        keys += [("meta", campaign, *s, r, f, i) for r in ("CAL_NULL", "HOLD_NULL", "ALT")
                 for f in scope["families"] for i in range(int((sizes if allocation is not None else n)[r]))]
        keys += [("devlib", campaign, *s, f, i) for f in dev for i in range(int(sizes["DEV_LIB"]))]
        keys += [("boot", campaign, *s, a, f) for a in scope["applications"] for f in scope["families"]]
    keys = sorted(keys, key=pdb.canon)
    labels = sorted({p for k in keys for p in k if isinstance(p, str)})
    if len({pdb.label_code(label) for label in labels}) != len(labels):
        raise ValueError(f"CRC32 collision among the seed labels {labels}: rename a label")
    words = [[32, seed, pdb.label_code(k[1]), pdb.label_code(k[0]),
              *(pdb.label_code(p) if isinstance(p, str) else p for p in k[2:])] for k in keys]
    entropies = sorted(list(e) for e in pdb.check_entropies(words))
    return {"keys": keys, "sha256": hashlib.sha256(pdb.canon(entropies).encode()).hexdigest()}


def design_descriptor(cfg, mode):
    """Pre-execution design: science, mode sizes, scope, envelope, seed plan, spectrum, code bytes and environment."""
    _check_cfg(cfg, mode)
    run = cfg["modes"][mode]
    desc = {"schema_version": SCHEMA_VERSION, "mode": mode, "campaign": mode.upper(),
            "science": {key: cfg[key] for key in SCIENCE}, "sizes": run["sizes"], "null_plan": run["null_plan"],
            "scope": cfg["scope"], "envelope": cfg["envelope"], "seed": cfg["seed"],
            "seed_plan_sha256": seed_plan(cfg, mode)["sha256"],
            "spectrum_sha": hashlib.sha256(pdb.canon(cfg["parameters"]["spectrum"]).encode()).hexdigest(),
            "code": {rel: pdb.file_sha256(CODE_ROOT / rel) for rel in CODE_FILES}, "environment": _environment()}
    if "allocation" in run:
        desc["allocation"] = run["allocation"]
    return json.loads(json.dumps(desc, allow_nan=False))


def design_id(desc):
    """SHA-256 hex of the canonical JSON of a design descriptor; design_tag = run_id = its first 16 hex digits."""
    return hashlib.sha256(pdb.canon(desc).encode()).hexdigest()


def _relative_posix(rel):
    posix = PurePosixPath(rel) if isinstance(rel, str) and rel and "\x00" not in rel else None
    return posix is not None and not posix.is_absolute() and ".." not in posix.parts and str(posix) == rel


def _go_bytes(ref):
    rel = ref.get("path") if isinstance(ref, dict) and set(ref) == {"path", "sha256"} else None
    if not _relative_posix(rel):
        raise AuthorizationRefused(f"go_reference needs a normalized relative POSIX path and a sha256, got {ref!r}")
    path = REPO_ROOT / rel
    if not (path.is_file() and path.resolve().is_relative_to(REPO_ROOT.resolve())):
        raise AuthorizationRefused(f"GO file {rel!r} is missing or outside the repository root")
    with open(path, "rb") as handle:
        data = handle.read()
    if hashlib.sha256(data).hexdigest() != ref["sha256"]:
        raise AuthorizationRefused(f"GO file {rel!r} does not match its recorded SHA-256")
    return data


def authorize(mode, cfg, desc, jobs):
    """Pure guard before any effect: current descriptor, jobs <= jobs_max and a GO citing design_id (smoke: optional)."""
    if isinstance(jobs, bool) or not isinstance(jobs, (int, np.integer)):
        raise AuthorizationRefused(f"jobs must be an integer, got {jobs!r}")
    try:
        current = design_descriptor(cfg, mode)
    except ValueError as exc:
        raise AuthorizationRefused(f"invalid design configuration: {exc}") from exc
    if not 1 <= jobs <= current["envelope"]["jobs_max"] or pdb.canon(desc) != pdb.canon(current):
        raise AuthorizationRefused("jobs outside [1, jobs_max] or a descriptor that is not the current design")
    did, block = design_id(current), cfg.get("authorization")
    if block is None and mode == "smoke":
        return {"stage": "smoke", "design_id": did, "go_reference": None}
    if not (isinstance(block, dict) and set(block) == {"stage", "design_id", "go_reference"}
            and block["stage"] == mode and block["design_id"] == did):
        raise AuthorizationRefused(f"{mode} needs an authorization block with stage {mode!r} and design_id {did}")
    if did.encode() not in _go_bytes(block["go_reference"]):
        raise AuthorizationRefused(f"the GO file does not cite design_id {did}")
    return {"stage": mode, "design_id": did, "go_reference": dict(block["go_reference"])}


OutputExists = pdb.OutputExists


class StagingMismatch(RuntimeError):
    """An existing staging whose design record is missing, malformed or belongs to another full design_id."""


def _write_atomic(path, data):
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data.encode("utf-8") if isinstance(data, str) else data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def open_staging(log_dir, desc, resume):
    """<log_dir>/staging/<design_id[:16]> holding design.json; an existing staging needs resume and the same full id."""
    if not (isinstance(desc, dict) and desc.get("schema_version") == SCHEMA_VERSION):
        raise ValueError("open_staging needs a descriptor built by design_descriptor")
    did = design_id(desc)
    staging = Path(log_dir) / "staging" / did[:16]
    staging.parent.mkdir(parents=True, exist_ok=True)
    try:
        staging.mkdir()
    except FileExistsError:
        pass
    else:
        _write_atomic(staging / "design.json", pdb.canon({"design_id": did, "descriptor": desc}) + "\n")
        return staging
    if not resume:
        raise OutputExists(f"{staging} already exists: pass resume or use a distinct log directory")
    try:
        stored = json.loads((staging / "design.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise StagingMismatch(f"{staging}/design.json is missing or malformed") from exc
    if not (isinstance(stored, dict) and set(stored) == {"design_id", "descriptor"} and stored["design_id"] == did
            and pdb.canon(stored["descriptor"]) == pdb.canon(desc) and design_id(stored["descriptor"]) == did):
        raise StagingMismatch(f"{staging}/design.json does not record the full design_id {did}")
    return staging


PHASES = ("SETUP", "DEV", "CAL", "NULL_PLAN", "HOLD", "ALT")
PartitionMismatch = pdb.PartitionMismatch


class PhaseOrderError(RuntimeError):
    """A phase requested before the record of every preceding phase exists, or a load of an absent record."""


def _staged_design(staging):
    try:
        stored = json.loads((staging / "design.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise StagingMismatch(f"{staging}/design.json is missing or malformed") from exc
    did = stored.get("design_id") if isinstance(stored, dict) and set(stored) == {"design_id", "descriptor"} else None
    if not (isinstance(did, str) and staging.name == did[:16] and design_id(stored["descriptor"]) == did):
        raise StagingMismatch(f"{staging}/design.json is not a consistent design record for its tag")
    return did, stored["descriptor"]


def _partition_key(key):
    if not (isinstance(key, (list, tuple)) and key and all(
            isinstance(p, str) or (isinstance(p, (int, np.integer)) and not isinstance(p, bool)) for p in key)):
        raise ValueError(f"a partition key is a nonempty list of str or int labels, got {key!r}")
    return [p if isinstance(p, str) else int(p) for p in key]


def _partition_path(staging, did, upstream, key):
    identity = pdb.canon({"design_id": did, "key": key, "upstream": upstream})
    return staging / "partitions" / hashlib.sha256(identity.encode()).hexdigest()


def _verify_partition(staging, did, upstream, key):
    stem = _partition_path(staging, did, upstream, key)
    fingerprint = stem.name
    try:
        sidecar = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
        payload = stem.with_suffix(".npz")
        size = payload.stat().st_size
        if size >= MAX_PUBLISHED_BYTES and "allocation" in _staged_design(staging)[1]:
            raise PartitionMismatch(f"partition {key} holds {size} bytes at or above the published bound")
        data = payload.read_bytes()
    except (OSError, ValueError) as exc:
        raise PartitionMismatch(f"partition {key} is missing or unreadable under {stem.parent}") from exc
    claimed = {"design_id": did, "key": key, "upstream": upstream, "fingerprint": fingerprint,
               "payload_sha256": hashlib.sha256(data).hexdigest()}
    n_rows = sidecar.get("n_rows") if isinstance(sidecar, dict) and set(sidecar) == {*claimed, "n_rows"} else None
    if (isinstance(n_rows, bool) or not isinstance(n_rows, int) or n_rows < 0
            or pdb.canon({k: sidecar[k] for k in claimed}) != pdb.canon(claimed)):
        raise PartitionMismatch(f"partition {key}: sidecar disagrees with design, key, lineage or payload bytes")
    try:
        with np.load(io.BytesIO(data), allow_pickle=False) as archive:
            arrays = {name: archive[name] for name in archive.files}
    except Exception as exc:
        raise PartitionMismatch(f"partition {key}: the payload is not a readable NPZ archive") from exc
    if not arrays or any(not value.shape or value.shape[0] != n_rows for value in arrays.values()):
        raise PartitionMismatch(f"partition {key}: its arrays do not all hold n_rows = {n_rows} rows")
    return claimed["payload_sha256"], n_rows, arrays


def _partition_rows(staging, did, upstream, keys):
    if len({pdb.canon(key) for key in keys}) != len(keys):
        raise ValueError("partition keys must be distinct")
    rows = []
    for key in keys:
        sha, n_rows, _ = _verify_partition(staging, did, upstream, key)
        rows.append({"key": key, "sha256": sha, "n_rows": n_rows})
    return sorted(rows, key=lambda row: pdb.canon(row["key"]))


def _phase_digest(did, phase, upstream, rows, derived):
    pairs = sorted([pdb.canon(row["key"]), row["sha256"]] for row in rows)
    identity = {"design_id": did, "phase": phase, "upstream": upstream, "partitions": pairs, "derived": derived}
    return hashlib.sha256(pdb.canon(identity).encode()).hexdigest()


def _is_sha(value):
    return isinstance(value, str) and len(value) == 64 and set(value) <= set("0123456789abcdef")


def _plan_applies(desc):
    return desc["null_plan"] is not None and desc["science"]["phi"]["setup"] in desc["scope"]["setups"]


def _check_plan(desc, derived, keys):
    if not _plan_applies(desc):
        if pdb.canon(derived) != pdb.canon({"status": "NOT_APPLICABLE"}) or keys:
            raise ValueError("an inapplicable NULL_PLAN is exactly {'status': 'NOT_APPLICABLE'} without partitions")
        return
    bounds, fields = desc["null_plan"], {"status", "n_hold", "plan_id"}
    n_hold = derived.get("n_hold") if isinstance(derived, dict) and set(derived) == fields else None
    if (isinstance(n_hold, bool) or not isinstance(n_hold, int) or not bounds["n_min"] <= n_hold <= bounds["n_cap"]
            or derived["status"] not in ("PLAN_ADEQUATE", "PLAN_CAPPED_EXPECT_INCONCLUSIVE")
            or (derived["status"] == "PLAN_CAPPED_EXPECT_INCONCLUSIVE" and n_hold != bounds["n_cap"])
            or not _is_sha(derived["plan_id"]) or not keys):
        raise ValueError(f"invalid applicable NULL_PLAN state (status, n_hold, plan_id, partitions): {derived!r}")


def _hold_spans(desc, total):
    block, ordinary = desc["allocation"]["hold_block_rows"], desc["sizes"]["HOLD_NULL"]
    return [(start, min(start + block, stop))
            for begin, stop in ((0, min(ordinary, total)), (ordinary, total))
            for start in range(begin, stop, block)]


def _expected_rows(desc, phase, key, records):
    primary = desc["science"]["phi"]["setup"]
    if phase == "CAL" and "allocation" in desc:
        if key not in _cal_keys(desc):
            raise ValueError(f"{key} is not a CAL_NULL partition of this design")
        if len(key) == 7 and key[6] == "P_CONF":
            return desc["allocation"]["primary_cal_null"]
        return desc["sizes"]["CAL_NULL"]
    if phase == "NULL_PLAN":
        if not (_plan_applies(desc) and key[:4] == ["NULL_PLAN", *primary]):
            raise ValueError(f"{key} is not a NULL_PLAN partition of the primary setup under an applicable plan")
        return desc["null_plan"]["n_plan"]
    if phase == "HOLD":
        if not (key[0] == "HOLD_NULL" and key[1:4] in desc["scope"]["setups"]):
            raise ValueError(f"{key} is not a HOLD_NULL partition of a scope setup")
        plan = records["NULL_PLAN"]["derived"]
        if "allocation" in desc:
            if not (len(key) == 6 and key[4] in desc["scope"]["applications"] and type(key[5]) is int):
                raise ValueError(f"{key} is not a scoped HOLD_NULL block of an allocated design")
            total = desc["sizes"]["HOLD_NULL"]
            if [*key[1:4], key[4]] == [*primary, "RESIDUAL"]:
                total = plan["n_hold"]
            for start, stop in _hold_spans(desc, total):
                if start == key[5]:
                    return stop - start
            raise ValueError(f"{key} is not a realized HOLD_NULL block")
        if key[1:4] == primary and plan["status"] != "NOT_APPLICABLE":
            return plan["n_hold"]
        return desc["sizes"]["HOLD_NULL"]
    return None


def _state_limits(desc, phase, keys, derived, records):
    if phase == "NULL_PLAN":
        _check_plan(desc, derived, keys)
    if phase == "HOLD" and "allocation" in desc:
        active = _scheduled_keys(desc, phase, _hold_plan_keys(desc), records)
        if sorted(map(pdb.canon, keys)) != list(map(pdb.canon, active)):
            raise ValueError("HOLD needs exactly the allocated blocks of the committed NULL_PLAN")
    return {pdb.canon(key): _expected_rows(desc, phase, key, records) for key in keys}


def _check_rows(rows, limits):
    for row in rows:
        expected = limits[pdb.canon(row["key"])]
        if expected is not None and row["n_rows"] != expected:
            raise ValueError(f"partition {row['key']} holds {row['n_rows']} rows instead of the frozen {expected}")


def _lineage(staging, desc, did, phase):
    records = {}
    for prior in PHASES[:PHASES.index(phase)]:
        records[prior] = _load_phase(staging, desc, did, prior, dict(records))
    return records


def _load_phase(staging, desc, did, phase, records):
    lineage = {p: r["phase_digest"] for p, r in records.items()}
    path = staging / "phases" / f"{phase}.json"
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PhaseOrderError(f"no {phase} record under {path.parent}") from exc
    except (OSError, ValueError) as exc:
        raise PartitionMismatch(f"{path} is unreadable or malformed") from exc
    fields = {"design_id", "phase", "upstream", "partitions", "derived", "phase_digest"}
    rows = record.get("partitions") if isinstance(record, dict) and set(record) == fields else None
    if not (isinstance(rows, list)
            and all(isinstance(row, dict) and set(row) == {"key", "sha256", "n_rows"} for row in rows)):
        raise PartitionMismatch(f"{path} does not follow the phase record schema")
    if record["design_id"] != did or record["phase"] != phase or pdb.canon(record["upstream"]) != pdb.canon(lineage):
        raise PartitionMismatch(f"{path} does not belong to design {did}, phase {phase} and lineage {lineage}")
    try:
        json.dumps(record, allow_nan=False)
        rebuilt = _partition_rows(staging, did, lineage, [_partition_key(row["key"]) for row in rows])
    except ValueError as exc:
        raise PartitionMismatch(f"{path} holds invalid partition keys or non-strict JSON") from exc
    digest = _phase_digest(did, phase, lineage, rebuilt, record["derived"])
    if pdb.canon(rebuilt) != pdb.canon(rows) or digest != record["phase_digest"]:
        raise PartitionMismatch(f"{path} disagrees with its partition files or its phase_digest")
    try:
        _check_rows(rebuilt, _state_limits(desc, phase, [row["key"] for row in rebuilt], record["derived"], records))
    except ValueError as exc:
        raise PartitionMismatch(f"{path} violates the frozen {phase} state rules") from exc
    return record


def phase_record(staging, phase, upstream, partitions, derived):
    """Verified phase metadata record: an existing one is reloaded unchanged, a new one written atomically."""
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {PHASES}, got {phase!r}")
    staging = Path(staging)
    did, desc = _staged_design(staging)
    records = _lineage(staging, desc, did, phase)
    lineage = {p: r["phase_digest"] for p, r in records.items()}
    if upstream is not None and pdb.canon(upstream) != pdb.canon(lineage):
        raise PartitionMismatch(f"upstream {upstream} differs from the recorded lineage {lineage}")
    path = staging / "phases" / f"{phase}.json"
    if path.exists() or (partitions is None and derived is None):
        record = _load_phase(staging, desc, did, phase, records)
        if partitions is None and derived is None:
            return record
        stored = sorted(pdb.canon(row["key"]) for row in record["partitions"])
        given = None if partitions is None else sorted(pdb.canon(_partition_key(key)) for key in partitions)
        if given != stored or derived is None or pdb.canon(derived) != pdb.canon(record["derived"]):
            raise PartitionMismatch(f"{path} exists with other partitions or derived objects; it is never replaced")
        return record
    if partitions is None or derived is None:
        raise ValueError(f"a new {phase} record needs both partitions and derived objects")
    json.dumps(derived, allow_nan=False)
    keys = [_partition_key(key) for key in partitions]
    limits = _state_limits(desc, phase, keys, derived, records)
    rows = _partition_rows(staging, did, lineage, keys)
    _check_rows(rows, limits)
    record = {"design_id": did, "phase": phase, "upstream": lineage, "partitions": rows,
              "derived": json.loads(pdb.canon(derived)), "phase_digest": _phase_digest(did, phase, lineage, rows, derived)}
    path.parent.mkdir(exist_ok=True)
    _write_atomic(path, pdb.canon(record) + "\n")
    return record


def _npz_payload(arrays):
    if not (isinstance(arrays, dict) and arrays
            and all(isinstance(name, str) and name.isascii() and name.isidentifier()
                    and name not in ("file", "allow_pickle") for name in arrays)):
        raise ValueError("a partition payload is a nonempty dict of ASCII identifier names to arrays")
    for name, value in arrays.items():
        if not (isinstance(value, np.ndarray) and value.ndim >= 1 and value.dtype.kind in "biuf"):
            raise ValueError(f"array {name!r} must be a bool, int, uint or float ndarray with ndim >= 1")
        if value.dtype.kind == "f" and not np.isfinite(value).all():
            raise ValueError(f"array {name!r} holds non-finite values")
    rows = {value.shape[0] for value in arrays.values()}
    if len(rows) != 1:
        raise ValueError(f"partition arrays must share one leading row count, got {sorted(rows)}")
    buffer = io.BytesIO()
    np.savez(buffer, allow_pickle=False, **{name: arrays[name] for name in sorted(arrays)})
    return buffer.getvalue(), rows.pop()


def partition(staging, phase, upstream, key, produce, *, before_commit=None):
    """Phase partition arrays: verified reload, else one produce() call committed as NPZ first and sidecar JSON last."""
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {PHASES}, got {phase!r}")
    staging, key, prior = Path(staging), _partition_key(key), PHASES[:PHASES.index(phase)]
    did, desc = _staged_design(staging)
    if not (isinstance(upstream, dict) and set(upstream) == set(prior) and all(_is_sha(v) for v in upstream.values())):
        raise ValueError(f"upstream of {phase} needs the lowercase SHA-256 of exactly the phases {prior}")
    records = _lineage(staging, desc, did, phase)
    if pdb.canon(upstream) != pdb.canon({p: r["phase_digest"] for p, r in records.items()}):
        raise PartitionMismatch(f"upstream {upstream} differs from the verified lineage of {phase}")
    if (staging / "phases" / f"{phase}.json").exists():
        listed = {pdb.canon(row["key"]) for row in phase_record(staging, phase, upstream, None, None)["partitions"]}
        if pdb.canon(key) not in listed:
            raise PartitionMismatch(f"{key} is not a partition of the committed {phase} record")
        return _verify_partition(staging, did, upstream, key)[2]
    expected = _expected_rows(desc, phase, key, records)
    stem = _partition_path(staging, did, upstream, key)
    if stem.with_suffix(".json").exists():
        _, n_rows, arrays = _verify_partition(staging, did, upstream, key)
        if expected is not None and n_rows != expected:
            raise PartitionMismatch(f"cached partition {key} holds {n_rows} rows instead of the frozen {expected}")
        return arrays
    payload, n_rows = _npz_payload(produce())
    if expected is not None and n_rows != expected:
        raise ValueError(f"partition {key} must hold the frozen {expected} rows, the producer gave {n_rows}")
    if "allocation" in desc and len(payload) >= MAX_PUBLISHED_BYTES:
        raise ValueError(f"partition {key} would hold {len(payload)} bytes at or above the published bound")
    if before_commit is not None:
        before_commit()
    stem.parent.mkdir(exist_ok=True)
    _write_atomic(stem.with_suffix(".npz"), payload)
    sidecar = {"design_id": did, "key": key, "upstream": upstream, "fingerprint": stem.name,
               "payload_sha256": hashlib.sha256(payload).hexdigest(), "n_rows": n_rows}
    _write_atomic(stem.with_suffix(".json"), pdb.canon(sidecar) + "\n")
    return _verify_partition(staging, did, upstream, key)[2]


REALIZATION_EXCLUDED = ("manifest.json", "summary.md", "telemetry.json")


def _csv_name(name):
    return (isinstance(name, str) and name.endswith(".csv") and not name.startswith(".") and "\\" not in name
            and "\x00" not in name and PurePosixPath(name).name == name and name not in REALIZATION_EXCLUDED)


def _sha16(value):
    return isinstance(value, str) and len(value) == 16 and set(value) <= set("0123456789abcdef")


def _handoff_records(records):
    try:
        records = json.loads(json.dumps(records, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("realization records must be strict JSON") from exc
    if not (isinstance(records, dict) and set(records) == set(PHASES)
            and all(isinstance(record, dict) for record in records.values())):
        raise ValueError(f"realization needs exactly one record dict for each of {PHASES}")
    did = records["SETUP"].get("design_id")
    fields = {"design_id", "phase", "upstream", "partitions", "derived", "phase_digest"}
    for index, phase in enumerate(PHASES):
        record, lineage = records[phase], {p: records[p]["phase_digest"] for p in PHASES[:index]}
        rows = record.get("partitions") if set(record) == fields else None
        if not (_is_sha(did) and isinstance(rows, list) and record["design_id"] == did and record["phase"] == phase
                and pdb.canon(record["upstream"]) == pdb.canon(lineage)):
            raise ValueError(f"the {phase} record does not belong to design {did} with the lineage {lineage}")
        if not all(isinstance(row, dict) and set(row) == {"key", "sha256", "n_rows"} and _is_sha(row["sha256"])
                   and isinstance(row["n_rows"], int) and not isinstance(row["n_rows"], bool) and row["n_rows"] >= 0
                   for row in rows):
            raise ValueError(f"the {phase} record holds malformed partition rows")
        keys = {pdb.canon(_partition_key(row["key"])) for row in rows}
        digest = _phase_digest(did, phase, lineage, rows, record["derived"])
        if len(keys) != len(rows) or digest != record["phase_digest"]:
            raise ValueError(f"the {phase} record has duplicate partition keys or a stale phase_digest")
    return did, records


def realization(records, payload_shas):
    """(realization_id, descriptor): pure identity of verified phase records and scientific payload SHAs."""
    did, records = _handoff_records(records)
    try:
        payloads = json.loads(json.dumps(payload_shas, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("payload_shas must be strict JSON") from exc
    if not (isinstance(payloads, dict) and payloads):
        raise ValueError("payload_shas must be a nonempty dict of payload basenames")
    for name, sha in payloads.items():
        if not (_csv_name(name) and _is_sha(sha)):
            raise ValueError(f"payload {name!r} is not a .csv basename mapped to a lowercase SHA-256")
    dev, cal, plan = (records[p]["derived"] for p in ("DEV", "CAL", "NULL_PLAN"))
    dev_ids = dev.get("dev_ids") if isinstance(dev, dict) else None
    if not (isinstance(dev_ids, dict) and dev_ids
            and all(isinstance(label, str) and label and _sha16(value) for label, value in dev_ids.items())):
        raise ValueError("DEV.derived.dev_ids must map setup labels to lowercase sha16 identifiers")
    if not (isinstance(cal, dict) and "thresholds" in cal):
        raise ValueError("CAL.derived must carry the calibration thresholds")
    if pdb.canon(plan) == pdb.canon({"status": "NOT_APPLICABLE"}):
        null_digest, plan_id, n_hold = "NOT_APPLICABLE", None, None
    elif (isinstance(plan, dict) and set(plan) == {"status", "n_hold", "plan_id"} and _is_sha(plan["plan_id"])
          and isinstance(plan["n_hold"], int) and not isinstance(plan["n_hold"], bool)
          and plan["status"] in ("PLAN_ADEQUATE", "PLAN_CAPPED_EXPECT_INCONCLUSIVE")):
        null_digest, plan_id, n_hold = records["NULL_PLAN"]["phase_digest"], plan["plan_id"], plan["n_hold"]
    else:
        raise ValueError(f"NULL_PLAN.derived is neither NOT_APPLICABLE nor a frozen plan projection: {plan!r}")
    digests = {p: records[p]["phase_digest"] for p in PHASES}
    digests["NULL_PLAN"] = null_digest
    descriptor = {"design_id": did, "phase_digests": digests, "dev_ids": dev_ids,
                  "thresholds_sha": hashlib.sha256(pdb.canon(cal["thresholds"]).encode()).hexdigest(),
                  "plan_id": plan_id, "n_hold": n_hold, "payloads": payloads}
    return hashlib.sha256(pdb.canon(descriptor).encode()).hexdigest(), descriptor


MANIFEST_FIELDS = ("status", "design_id", "design_descriptor", "realization_id", "realization_descriptor", "authority",
                   "payloads")


def _fsync(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


MAX_PUBLISHED_BYTES = 50 * 1024 * 1024


def _authority_ok(auth, did, desc):
    shaped = isinstance(auth, dict) and set(auth) == {"stage", "design_id", "go_reference"}
    go = auth["go_reference"] if shaped else None
    cited = isinstance(go, dict) and set(go) == {"path", "sha256"} and _relative_posix(go["path"]) and _is_sha(go["sha256"])
    return bool(shaped and auth["design_id"] == did and isinstance(desc, dict) and auth["stage"] == desc.get("mode")
                and (cited or (go is None and auth["stage"] == "smoke")))


def _verified_publication(temp, out=None):
    if temp.is_symlink() or not temp.is_dir():
        raise ValueError(f"{temp} is not a prepared directory: missing, not a directory or a symbolic link")
    files = {path.name: path for path in temp.iterdir()}
    if any(path.is_symlink() or not path.is_file() or path.lstat().st_size > MAX_PUBLISHED_BYTES
           for path in files.values()):
        raise ValueError(f"{temp} must hold regular files of at most {MAX_PUBLISHED_BYTES} bytes, no symbolic links")
    try:
        data = (temp / "manifest.json").read_bytes()
        manifest = json.loads(data.decode("utf-8"))
        json.dumps(manifest, allow_nan=False)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{temp}/manifest.json is missing, unreadable or not strict UTF-8 JSON") from exc
    if not (data == (pdb.canon(manifest) + "\n").encode() and isinstance(manifest, dict)
            and set(manifest) == set(MANIFEST_FIELDS) and manifest["status"] == "COMPLETE"):
        raise ValueError(f"{temp}/manifest.json is not a canonical COMPLETE manifest with exactly {MANIFEST_FIELDS}")
    did, desc, rid, real, auth, payloads = (manifest[key] for key in MANIFEST_FIELDS[1:])
    if not (_is_sha(did) and design_id(desc) == did and isinstance(real, dict) and real.get("design_id") == did
            and _is_sha(rid) and hashlib.sha256(pdb.canon(real).encode()).hexdigest() == rid):
        raise ValueError(f"design_id {did!r} or realization_id {rid!r} disagrees with its descriptor")
    if "allocation" in desc and any(path.lstat().st_size >= MAX_PUBLISHED_BYTES for path in files.values()):
        raise ValueError(f"{temp} must hold files strictly below {MAX_PUBLISHED_BYTES} bytes")
    if out is not None and (temp.parent != out.parent or temp.name != f".{out.name}.publish-{did[:16]}.tmp"):
        raise ValueError(f"{temp} is not the prepared sibling .{out.name}.publish-{did[:16]}.tmp of {out}")
    if not _authority_ok(auth, did, desc):
        raise ValueError(f"authority {auth!r} is not the verified authorization handoff of design {did}")
    rows = payloads.values() if isinstance(payloads, dict) else [None]
    if not all(isinstance(row, dict) and set(row) == {"status", "sha256"} and _is_sha(row["sha256"])
               and row["status"] in ("PUBLISHED", "LOCAL_HASHED_ONLY") for row in rows):
        raise ValueError("manifest payloads map names to exactly {status, sha256}: a known status, a lowercase SHA-256")
    published = {name: row["sha256"] for name, row in payloads.items() if row["status"] == "PUBLISHED"}
    local = [name for name in payloads if name not in published]
    if not (published and all(_csv_name(name) for name in published) and published == real.get("payloads")
            and all(name.startswith("partitions/") and name.endswith(".npz") and _is_sha(name[11:-4]) for name in local)):
        raise ValueError("PUBLISHED names must be safe .csv basenames equal to the realization payloads, "
                         "LOCAL_HASHED_ONLY names partitions/<sha256>.npz")
    if set(files) != {*published, *REALIZATION_EXCLUDED} or any(path.is_symlink() or not path.is_file()
                                                                 for path in files.values()):
        raise ValueError(f"{temp} must hold exactly the PUBLISHED payloads and {REALIZATION_EXCLUDED} as regular files")
    if any(pdb.file_sha256(files[name]) != sha for name, sha in published.items()):
        raise ValueError(f"a PUBLISHED payload under {temp} differs from its manifest SHA-256")
    return manifest, files


def publish(temp_dir, output_dir):
    """Verified manifest of a prepared sibling handoff, fsynced and renamed onto an absent or empty output_dir."""
    temp, out = Path(temp_dir), Path(output_dir)
    if out.is_symlink() or (out.exists() and not (out.is_dir() and not any(out.iterdir()))):
        raise OutputExists(f"{out} exists and is not an empty directory: a publication is never replaced")
    manifest, files = _verified_publication(temp, out)
    for path in (*files.values(), temp):
        _fsync(path)
    os.replace(temp, out)
    _fsync(out.parent)
    return manifest


SELECTION_COLUMNS = ("design_id", "setup", "policy", "family", "info_basis", "metric_basis", "gamma_M", "horizon",
                     "d_mean", "I_mean", "M_mean", "V_bar")
SELECTION_KEYS = frozenset({"setup", "policy", "family", "info_basis", "gamma_M", "masks", "q"})
INFO_BASES = ("EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_SURROGATE", "ORACLE_DIAGONAL_GAUSSIAN_PROXY")


def export_selections(out_dir, design_id, entries):
    """selections.csv of frozen masks: full-horizon means of d, I(S), M(d, gamma_M) and I/M; returns its SHA-256."""
    if not (_is_sha(design_id) and isinstance(entries, list) and entries and Path(out_dir).is_dir()):
        raise ValueError("export_selections needs an existing out_dir, a lowercase 64-hex design_id and entries")
    rows = []
    for entry in entries:
        if not (isinstance(entry, dict) and set(entry) == SELECTION_KEYS and entry["info_basis"] in INFO_BASES
                and all(isinstance(entry[k], str) and entry[k] for k in ("setup", "policy", "family"))):
            raise ValueError(f"a selection entry needs exactly {sorted(SELECTION_KEYS)} and info_basis in {INFO_BASES}")
        gamma, q, masks = entry["gamma_M"], entry["q"], entry["masks"]
        if (isinstance(gamma, bool) or not isinstance(gamma, (int, float, np.integer, np.floating))
                or not (math.isfinite(gamma) and gamma > 1)):
            raise ValueError(f"gamma_M must be a finite real > 1, got {gamma!r}")
        if not (isinstance(q, np.ndarray) and q.ndim == 1 and q.size and q.dtype.kind in "fiu"
                and np.isfinite(q).all() and (q >= 0).all()):
            raise ValueError("q must be a nonempty finite nonnegative real vector")
        if not (isinstance(masks, np.ndarray) and masks.dtype == bool and masks.ndim in (1, 2) and masks.size
                and masks.shape[-1] == q.size):
            raise ValueError(f"masks must be a boolean ({q.size},) or (H, {q.size}) array")
        steps = masks.reshape(-1, q.size)
        d = steps.sum(axis=1)
        if not (d >= 1).all():
            raise ValueError("every mask row must select at least one axis")
        cost = {k: mixture_cost(k, float(gamma)) for k in set(d.tolist())}
        with np.errstate(over="ignore", invalid="ignore"):
            info = np.where(steps, q, 0.0).sum(axis=1)
            costs = np.array([cost[k] for k in d.tolist()])
            metrics = np.array([d.mean(), info.mean(), costs.mean(), (info / costs).mean()], dtype=np.float64)
        if not np.isfinite(metrics).all():
            raise ValueError("a derived selection metric is not finite")
        labels = [design_id, *(entry[k] for k in ("setup", "policy", "family", "info_basis")), "ANALYTIC_PROXY"]
        rows.append(dict(zip(SELECTION_COLUMNS, [*labels, float(gamma), len(steps), *map(float, metrics)])))
    path = Path(out_dir) / "selections.csv"
    pipelines.save_fair_csv(pandas.DataFrame(rows, columns=list(SELECTION_COLUMNS)), path)
    return pdb.file_sha256(path)


OWNER_MARKER = ".owner.json"


def _local_inventory(did, records):
    return {f"partitions/{_partition_path(Path(), did, record['upstream'], row['key']).name}.npz":
            {"status": "LOCAL_HASHED_ONLY", "sha256": row["sha256"]}
            for record in records.values() for row in record["partitions"]}


def _matching_publication(temp, did, desc, records, authority):
    try:
        manifest, _ = _verified_publication(temp)
        shas = {name: row["sha256"] for name, row in manifest["payloads"].items() if row["status"] == "PUBLISHED"}
        rid, real = realization(records, shas)
    except ValueError:
        return None
    local = {name: row for name, row in manifest["payloads"].items() if row["status"] == "LOCAL_HASHED_ONLY"}
    same = (manifest["design_id"] == did and pdb.canon(manifest["design_descriptor"]) == pdb.canon(desc)
            and manifest["realization_id"] == rid and pdb.canon(manifest["realization_descriptor"]) == pdb.canon(real)
            and pdb.canon(manifest["authority"]) == pdb.canon(authority) and local == _local_inventory(did, records))
    return manifest if same else None


def _marked_temp(temp, did):
    marker, expected = temp / OWNER_MARKER, (pdb.canon({"design_id": did}) + "\n").encode()
    entries = list(temp.iterdir())
    if not all(not path.is_symlink() and path.is_file()
               and (path.name in (OWNER_MARKER, *REALIZATION_EXCLUDED) or _csv_name(path.name)) for path in entries):
        return False
    return marker in entries and marker.lstat().st_size == len(expected) and marker.read_bytes() == expected


def _claimed_design(folder):
    path = folder / "manifest.json"
    if path.is_symlink() or not path.is_file() or path.lstat().st_size > MAX_PUBLISHED_BYTES:
        return None
    try:
        claimed = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, ValueError):
        return None
    return claimed.get("design_id") if isinstance(claimed, dict) else None


def _final_record(did, manifest, out):
    return {"status": "PUBLISHED", "design_id": did, "realization_id": manifest["realization_id"],
            "manifest_sha256": pdb.file_sha256(out / "manifest.json")}


def finalize(staging, output_dir, authority, build):
    """Publish the six verified phase records of a staging once, then write phases/FINAL.json; returns that record."""
    staging, out = Path(staging), Path(output_dir)
    did, desc = _staged_design(staging)
    if not _authority_ok(authority, did, desc):
        raise ValueError(f"authority {authority!r} is not the verified authorization handoff of design {did}")
    records = _lineage(staging, desc, did, PHASES[-1])
    records[PHASES[-1]] = _load_phase(staging, desc, did, PHASES[-1], dict(records))
    final_path = staging / "phases" / "FINAL.json"
    if os.path.lexists(final_path):
        manifest = _matching_publication(out, did, desc, records, authority)
        final = None if manifest is None else _final_record(did, manifest, out)
        if (final is None or final_path.is_symlink() or not final_path.is_file()
                or final_path.read_bytes() != (pdb.canon(final) + "\n").encode()):
            raise PartitionMismatch(f"{final_path} does not match an intact publication of design {did} at {out}")
        return final
    if out.is_symlink() or (out.exists() and not out.is_dir()):
        raise OutputExists(f"{out} exists and is not a publication directory")
    if out.exists() and any(out.iterdir()):
        if _claimed_design(out) != did:
            raise OutputExists(f"{out} holds foreign files or the publication of another design")
        manifest = _matching_publication(out, did, desc, records, authority)
        if manifest is None:
            raise PartitionMismatch(f"{out} holds a publication of {did} that disagrees with its staging or authority")
        final = _final_record(did, manifest, out)
        _fsync(out.parent)
        _write_atomic(final_path, pdb.canon(final) + "\n")
        return final
    temp = out.parent / f".{out.name}.publish-{did[:16]}.tmp"
    if os.path.lexists(temp):
        owned = (not temp.is_symlink() and temp.is_dir()
                 and (not any(temp.iterdir()) or _marked_temp(temp, did)
                      or _matching_publication(temp, did, desc, records, authority) is not None))
        if not owned:
            raise OutputExists(f"{temp} is not an empty or verified-owned publication directory of design {did}")
        for path in temp.iterdir():
            path.unlink()
        temp.rmdir()
    temp.mkdir()
    _write_atomic(temp / OWNER_MARKER, pdb.canon({"design_id": did}) + "\n")
    telemetry = build(temp, did, json.loads(pdb.canon(records)))
    try:
        strict = isinstance(telemetry, dict) and bool(json.dumps(telemetry, allow_nan=False))
    except (TypeError, ValueError):
        strict = False
    files = {path.name: path for path in temp.iterdir() if path.name != OWNER_MARKER}
    if not (strict and files and all(_csv_name(name) and not path.is_symlink() and path.is_file()
                                     for name, path in files.items())):
        raise ValueError(f"the payload builder must write safe regular .csv files into {temp} and return JSON telemetry")
    limit = MAX_PUBLISHED_BYTES - ("allocation" in desc)
    if any(path.lstat().st_size > limit for path in files.values()):
        raise ValueError(f"every payload under {temp} must hold at most {limit} bytes")
    shas = {name: pdb.file_sha256(path) for name, path in files.items()}
    rid, real = realization(records, shas)
    manifest = {"status": "COMPLETE", "design_id": did, "design_descriptor": desc, "realization_id": rid,
                "realization_descriptor": real, "authority": authority,
                "payloads": {**{name: {"status": "PUBLISHED", "sha256": sha} for name, sha in shas.items()},
                             **_local_inventory(did, records)}}
    summary = (f"# pca_info_online publication\n\ndesign_id: {did}\nstage: {authority['stage']}\n"
               f"payloads: {', '.join(sorted(shas))}\n")
    for name, text in (("manifest.json", pdb.canon(manifest) + "\n"), ("summary.md", summary),
                       ("telemetry.json", pdb.canon(telemetry) + "\n")):
        data = text.encode()
        if len(data) > limit:
            raise ValueError(f"{name} must hold at most {limit} bytes")
        (temp / name).write_bytes(data)
    (temp / OWNER_MARKER).unlink()
    final = _final_record(did, publish(temp, out), out)
    _write_atomic(final_path, pdb.canon(final) + "\n")
    return final


def _validated_plan(plan):
    if not (isinstance(plan, dict) and set(plan) == set(PHASES)):
        raise ValueError(f"a plan maps exactly the phases {PHASES} to lists of scheduled partition keys")
    for phase, keys in plan.items():
        if not (isinstance(keys, list) and all(isinstance(key, list) and key and all(
                type(p) is int or (type(p) is str and not set(p) & {"/", "\\", "\x00"}) for p in key) for key in keys)):
            raise ValueError(f"the {phase} plan needs nonempty keys of int or path-free str labels")
        canon = [pdb.canon(key) for key in keys]
        if canon != sorted(set(canon)):
            raise ValueError(f"the {phase} plan keys must be distinct and in canonical order")


def _cal_keys(desc):
    scope, campaign = desc["scope"], desc["campaign"]
    primary = desc["science"]["phi"]["setup"]
    keys = []
    for setup in scope["setups"]:
        for app in scope["applications"]:
            key = ["CAL_NULL", campaign, *setup, app]
            if "allocation" in desc and setup == primary and app == "RESIDUAL":
                keys.extend([*key, group] for group in ("P_CONF", "OTHER"))
            else:
                keys.append(key)
    return sorted(keys, key=pdb.canon)


def _hold_plan_keys(desc):
    scope, primary = desc["scope"], desc["science"]["phi"]["setup"]
    keys = []
    for setup in scope["setups"]:
        for app in scope["applications"]:
            cohort = ["HOLD_NULL", *setup, app]
            if "allocation" not in desc:
                keys.append(cohort)
                continue
            total = (desc["null_plan"]["n_cap"] if [*setup, app] == [*primary, "RESIDUAL"]
                     else desc["sizes"]["HOLD_NULL"])
            keys.extend([*cohort, start] for start, _ in _hold_spans(desc, total))
    return sorted(keys, key=pdb.canon)


def partition_plan(desc):
    """Return the canonical per-phase partition keys scheduled by the accepted design descriptor desc."""
    scope, campaign = desc["scope"], desc["campaign"]
    setups, apps, families = scope["setups"], scope["applications"], scope["families"]
    unknown = [f for f in families if f not in DRIFT_FAMILIES]
    if unknown:
        raise ValueError(f"the scoped families {unknown} are not in DRIFT_FAMILIES")
    tails = [("DEV_NULL", [])] + [(role, [f]) for role in ("DEV_LIB", "DEV_ALT") for f in DEV_FAMILIES]
    keys = {"SETUP": [["frame", campaign, N] for N in dict.fromkeys(s[1] for s in setups)]
                     + [["fit", campaign, *s] for s in setups if s[0] != "EXACT"],
            "DEV": [[role, campaign, *s, *tail] for s in setups for role, tail in tails] if "RESIDUAL" in apps else [],
            "CAL": _cal_keys(desc),
            "NULL_PLAN": [["NULL_PLAN", *desc["science"]["phi"]["setup"]]] if _plan_applies(desc) else [],
            "HOLD": _hold_plan_keys(desc),
            "ALT": [["ALT", *s, app, f] for s in setups for app in apps for f in families
                    if DRIFT_FAMILIES[f][0] == app]}
    plan = {phase: sorted(keys[phase], key=pdb.canon) for phase in PHASES}
    _validated_plan(plan)
    return plan


def _scheduled_keys(desc, phase, keys, records):
    if phase != "HOLD" or "allocation" not in desc or "NULL_PLAN" not in records:
        return keys
    primary = ["HOLD_NULL", *desc["science"]["phi"]["setup"], "RESIDUAL"]
    n_hold = records["NULL_PLAN"]["derived"]["n_hold"]
    starts = {start for start, _ in _hold_spans(desc, n_hold)}
    return [key for key in keys if key[:5] != primary or len(key) != 6 or key[5] in starts]


def _planned_progress(staging, did, desc, plan, out):
    records = {}
    for phase in PHASES:
        if not os.path.lexists(staging / "phases" / f"{phase}.json"):
            break
        records[phase] = _load_phase(staging, desc, did, phase, dict(records))
        scheduled = _scheduled_keys(desc, phase, plan[phase], records)
        if [pdb.canon(row["key"]) for row in records[phase]["partitions"]] != list(map(pdb.canon, scheduled)):
            raise PartitionMismatch(f"the committed {phase} partitions differ from its planned keys")
    if len(records) == len(PHASES):
        return records, []
    pending, later = PHASES[len(records)], PHASES[len(records) + 1:]
    if out is not None and out.is_symlink():
        raise OutputExists(f"{out} is a symbolic link, never a publication directory")
    if (any(os.path.lexists(staging / "phases" / f"{phase}.json") for phase in later)
            or os.path.lexists(staging / "phases" / "FINAL.json") or (out is not None and _claimed_design(out) == did)):
        raise PhaseOrderError(f"{pending} has no record while a later record, FINAL or its publication is committed")
    upstream, missing = {p: r["phase_digest"] for p, r in records.items()}, []
    for key in _scheduled_keys(desc, pending, plan[pending], records):
        expected = _expected_rows(desc, pending, key, records)
        if not os.path.lexists(_partition_path(staging, did, upstream, key).with_suffix(".json")):
            missing.append({"phase": pending, "key": key})
            continue
        n_rows = _verify_partition(staging, did, upstream, key)[1]
        if expected is not None and n_rows != expected:
            raise PartitionMismatch(f"cached partition {key} holds {n_rows} rows instead of the frozen {expected}")
    return records, missing + [{"phase": phase, "key": key} for phase in later for key in plan[phase]]


def finalize_planned(staging, output_dir, authority, plan, build):
    """INCOMPLETE status until every planned partition and phase record exists, then finalize; returns status or FINAL."""
    staging = Path(staging)
    did, desc = _staged_design(staging)
    if not _authority_ok(authority, did, desc):
        raise ValueError(f"authority {authority!r} is not the verified authorization handoff of design {did}")
    _validated_plan(plan)
    records, missing = _planned_progress(staging, did, desc, plan, Path(output_dir))
    if len(records) == len(PHASES):
        final = finalize(staging, output_dir, authority, build)
        status = {"status": "PUBLISHED", "design_id": did, "last_complete_phase": PHASES[-1], "missing_partitions": []}
        _write_atomic(staging / "status.json", pdb.canon(status) + "\n")
        return final
    status = {"status": "INCOMPLETE", "design_id": did, "last_complete_phase": [*records][-1] if records else None,
              "missing_partitions": missing}
    _write_atomic(staging / "status.json", pdb.canon(status) + "\n")
    return status


ResourceBlocked = pdb.ResourceBlocked


def _finite_nonnegative(value):
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def _cpu_total(values):
    try:
        return math.fsum(values)
    except OverflowError:
        return math.inf


def _cpu_journal(staging, did):
    path = staging / "resources.json"
    if not os.path.lexists(path):
        return None
    if path.is_symlink() or not path.is_file() or path.lstat().st_size > MAX_PUBLISHED_BYTES:
        raise PartitionMismatch(f"{path} is not a regular bounded resource journal")
    data = path.read_bytes()
    try:
        journal = json.loads(data.decode("utf-8"))
        json.dumps(journal, allow_nan=False)
    except ValueError as exc:
        raise PartitionMismatch(f"{path} is not strict UTF-8 JSON") from exc
    shaped = isinstance(journal, dict) and set(journal) == {"design_id", "cpu_seconds"}
    spent = journal["cpu_seconds"] if shaped else None
    if not (isinstance(spent, dict) and journal["design_id"] == did and data == (pdb.canon(journal) + "\n").encode()
            and all(token and _finite_nonnegative(seconds) for token, seconds in spent.items())
            and math.isfinite(_cpu_total(spent.values()))):
        raise PartitionMismatch(f"{path} is not the canonical CPU journal of design {did}")
    return spent


def charge_cpu(staging, token, cpu_seconds):
    """Record a token's CPU checkpoint (SELF+CHILDREN, monotone, never added twice); returns the cumulative CPU."""
    staging = Path(staging)
    did, _ = _staged_design(staging)
    if not (isinstance(token, str) and token and _finite_nonnegative(cpu_seconds)):
        raise ValueError(f"a CPU checkpoint needs a nonempty token and finite seconds >= 0: {token!r} {cpu_seconds!r}")
    spent = _cpu_journal(staging, did)
    if spent is None:
        if os.path.lexists(staging / "partitions") or os.path.lexists(staging / "phases"):
            raise PartitionMismatch(f"{staging} holds work without a resource journal: its spent CPU is unknown")
        spent = {}
    if cpu_seconds < spent.get(token, 0.0):
        raise ValueError(f"the CPU checkpoint {cpu_seconds!r} of {token!r} is below the recorded {spent[token]!r}")
    spent = {**spent, token: float(cpu_seconds)}
    total = _cpu_total(spent.values())
    if not math.isfinite(total):
        raise ValueError(f"the cumulative CPU of {staging} is not finite")
    _write_atomic(staging / "resources.json", pdb.canon({"design_id": did, "cpu_seconds": spent}) + "\n")
    return total


def require_budget(staging, authority, plan, started, progress=None):
    """Remaining CPU of the staged envelope, else a BLOCKED_RESOURCE status and ResourceBlocked; no other write."""
    staging = Path(staging)
    did, desc = _staged_design(staging)
    if not _authority_ok(authority, did, desc):
        raise ValueError(f"authority {authority!r} is not the verified authorization handoff of design {did}")
    _validated_plan(plan)
    spent = _cpu_journal(staging, did)
    if spent is None:
        raise PartitionMismatch(f"{staging} has no resource journal: its spent CPU is unknown")
    now = time.monotonic()
    elapsed = now - started if _finite_nonnegative(started) else math.nan
    if not (math.isfinite(elapsed) and elapsed >= 0):
        raise ValueError(f"the invocation start {started!r} is not a finite monotonic time before now")
    total, envelope = _cpu_total(spent.values()), desc["envelope"]
    cap, wall = envelope["cpu_hours_max"] * 3600, envelope["wall_seconds_per_invocation"]
    if total < cap and now < started + wall:
        return cap - total
    if progress is None or ("allocation" in desc and os.path.lexists(staging / "phases" / "NULL_PLAN.json")):
        records, missing = _planned_progress(staging, did, desc, plan, None)
        progress = ([*records][-1] if records else None, missing)
    last, missing = progress
    status = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": last, "missing_partitions": missing}
    _write_atomic(staging / "status.json", pdb.canon(status) + "\n")
    raise ResourceBlocked(f"design {did}: CPU {total} s of {cap} s or wall {elapsed} s of {wall} s is exhausted")


def _cpu_now():
    times = os.times()
    fields = (times.user, times.system, times.children_user, times.children_system)
    total = _cpu_total(fields) if all(_finite_nonnegative(value) for value in fields) else math.nan
    if not math.isfinite(total):
        raise ValueError(f"os.times() CPU fields {fields!r} are not finite nonnegative seconds")
    return total


def start_invocation(staging, authority, plan, token):
    """Operational context of one invocation: fresh journal token at 0 and its SELF+CHILDREN CPU and wall baselines."""
    staging = Path(staging)
    did, desc = _staged_design(staging)
    if not _authority_ok(authority, did, desc):
        raise ValueError(f"authority {authority!r} is not the verified authorization handoff of design {did}")
    _validated_plan(plan)
    spent = _cpu_journal(staging, did)
    if not (isinstance(token, str) and token) or token in (spent or {}):
        raise ValueError(f"invocation token {token!r} must be a nonempty name absent from the resource journal")
    cpu_start, started = _cpu_now(), time.monotonic()
    if not _finite_nonnegative(started):
        raise ValueError(f"the monotonic wall start {started!r} is not finite and nonnegative")
    charge_cpu(staging, token, 0.0)
    return {"staging": staging, "authority": authority, "plan": plan, "token": token, "cpu_start": cpu_start,
            "started": started}


def guarded_partition(context, phase, upstream, key, produce):
    """partition() behind a CPU checkpoint and require_budget; its joined CPU is checkpointed after return or error."""
    staging, token, cpu_start = context["staging"], context["token"], context["cpu_start"]
    def admit():
        charge_cpu(staging, token, _cpu_now() - cpu_start)
        require_budget(staging, context["authority"], context["plan"], context["started"])
    def producer(*args, **kwargs):
        try:
            return produce(*args, **kwargs)
        except ResourceBlocked:
            admit()
            raise
    admit()
    try:
        labels = _partition_key(key)
        if phase == "DEV" and labels[0] == "DEV_LIB":
            return partition(staging, phase, upstream, key, producer)
        return partition(staging, phase, upstream, key, producer, before_commit=admit)
    finally:
        charge_cpu(staging, token, _cpu_now() - cpu_start)


def population_frame(cfg, mode, N):
    """Population frame V, first column +1/sqrt(N) fixed before QR, and the configured spectrum lam for one N."""
    _check_cfg(cfg, mode)
    campaign = mode.upper()
    if isinstance(N, bool) or not isinstance(N, int) or ("frame", campaign, N) not in seed_plan(cfg, mode)["keys"]:
        raise ValueError(f"N must be an integer frame size planned for {mode}, got {N!r}")
    try:
        spec = cfg["parameters"]["spectrum"]
        tail = [spec["floor"] + spec["scale"] * math.exp(-(k - 2) / spec["decay"]) for k in range(2, N + 1)]
        lam = np.array([spec["lambda_1"], *tail], dtype=np.float64)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("the configured spectrum parameters cannot be evaluated") from exc
    if not (np.isfinite(lam).all() and (lam > 0).all() and (np.diff(lam) < 0).all()):
        raise ValueError(f"the configured spectrum is not finite, positive and strictly decreasing: {spec!r}")
    seq = np.random.SeedSequence([32, int(cfg["seed"]), pdb.label_code(campaign), pdb.label_code("frame"), N])
    A = np.column_stack([np.full(N, 1.0 / math.sqrt(N)), np.random.default_rng(seq).standard_normal((N, N - 1))])
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R)), lam


UNIVERSES = {"RESIDUAL": (2, 21), "MARKET": (1, 20)}


def _finite_cpv90(values):
    with np.errstate(over="ignore", invalid="ignore"):
        total, prefixes = np.sum(values), np.cumsum(values)
    if not (np.isfinite(total) and total > 0 and np.isfinite(prefixes).all()):
        raise ValueError("the trace and cumulative sums seen by pdb.cpv90 must be finite, with a positive trace")
    return pdb.cpv90(values)


def spectral_baselines(lam, application):
    """1-based universe E and FULL_K, EIGENMEAN, CPV90, RESIDUAL_CPV90 rows of one full nonincreasing spectrum."""
    if not (isinstance(application, str) and application in UNIVERSES):
        raise ValueError(f"application must be one of {sorted(UNIVERSES)}, got {application!r}")
    lo, hi = UNIVERSES[application]
    raw = np.asarray(lam)
    if raw.ndim != 1 or raw.dtype.kind not in "fiu" or raw.size < hi:
        raise ValueError(f"{application} needs a 1-D real spectrum of length >= {hi}, got {raw.dtype}{raw.shape}")
    with np.errstate(over="ignore"):
        lam = raw.astype(np.float64, copy=False)
    if not (np.isfinite(lam).all() and (lam > 0).all() and (np.diff(lam) <= 0).all()):
        raise ValueError("the spectrum must be finite, positive and nonincreasing in canonical PC order")
    eligible, within = list(range(lo, hi + 1)), lam[lo - 1:hi]
    exact = [Fraction(v) for v in within.tolist()]
    mean, k90 = sum(exact) / len(exact), _finite_cpv90(lam)
    cpv90 = {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}
    if lo == 1 and k90 <= hi:
        cpv90 = {"status": "RUNNABLE", "pcs": list(range(1, k90 + 1)), "k90": k90}
    residual = {"status": "UNSUPPORTED", "pcs": None}
    if application == "RESIDUAL":
        residual = {"status": "RUNNABLE", "pcs": eligible[:_finite_cpv90(within)]}
    rows = {"FULL_K": {"status": "RUNNABLE", "pcs": list(eligible)},
            "FIXED_EIGENMEAN_PREFIX": {"status": "RUNNABLE", "pcs": eligible[:sum(v >= mean for v in exact)]},
            "CPV90": cpv90, "RESIDUAL_CPV90": residual}
    return {"eligible": eligible, "baselines": rows}


def _policy_kind(policy, schemas):
    kind = policy.get("kind") if isinstance(policy, dict) else None
    if not (isinstance(kind, str) and kind in schemas and set(policy) == schemas[kind]):
        raise ValueError(f"a policy must be a dict of kind {' or '.join(schemas)} holding exactly that kind's keys")
    return kind


def nonoracle_masks(Y, policy):
    """(B, H, K) bool non-oracle masks: ONLINE delegates to online_masks, STATIC broadcasts its frozen mask."""
    kind = _policy_kind(policy, {"ONLINE": {"kind", "window", "cost", "order"}, "STATIC": {"kind", "mask"}})
    if kind == "ONLINE":
        return online_masks(Y, policy["window"], policy["cost"], policy["order"])
    Y, mask = _scores(Y), policy["mask"]
    if not (isinstance(mask, np.ndarray) and mask.dtype == bool and mask.shape == Y.shape[2:] and mask.any()):
        raise ValueError(f"a STATIC mask is a bool array of shape ({Y.shape[2]},) selecting at least one axis")
    return np.broadcast_to(mask, Y.shape)


def oracle_masks(q_true, policy):
    """(B, H, K) bool oracle masks: best_sets of the supplied q_true (B, K), constant over the policy's H steps."""
    _policy_kind(policy, {"ORACLE": {"kind", "H", "cost", "order"}})
    H = policy["H"]
    if isinstance(H, bool) or not isinstance(H, (int, np.integer)) or H < 1:
        raise ValueError(f"an ORACLE horizon H must be an integer >= 1, got {H!r}")
    mask = best_sets(q_true, policy["cost"], policy["order"])[1]
    return np.broadcast_to(mask[:, None, :], (mask.shape[0], int(H), mask.shape[1]))


DRIFT_FAMILIES = {"F0_ISOTROPIC_RESIDUAL": ("RESIDUAL", None), "F1_TAIL_RESIDUAL": ("RESIDUAL", (18, 19, 20, 21)),
                  "F2_STRUCTURED_RESIDUAL": ("RESIDUAL", (3, 9, 17, 21)),
                  "F_HEAD_RESIDUAL": ("RESIDUAL", (2, 3, 4, 5)), "F3_MARKET": ("MARKET", (1,))}


def _real_array(value, name, ndim):
    raw = np.asarray(value)
    if raw.ndim != ndim or raw.dtype.kind not in "fiu":
        raise ValueError(f"{name} must be a real {ndim}-D array, got {raw.dtype} of shape {raw.shape}")
    with np.errstate(over="ignore"):
        array = raw.astype(np.float64, copy=False)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must be finite in float64")
    return array


def population_drift(V, lam, application, eligible, family, I_star, draws):
    """Drifts delta and exact population q of a canonical family on supplied draws, given the frozen orthonormal V."""
    if not (isinstance(application, str) and application in UNIVERSES and isinstance(family, str)
            and family in DRIFT_FAMILIES):
        raise ValueError(f"need an application in {sorted(UNIVERSES)} and a family in {sorted(DRIFT_FAMILIES)}")
    (lo, hi), (home, fixed) = UNIVERSES[application], DRIFT_FAMILIES[family]
    if not (type(eligible) is list and eligible and all(type(k) is int for k in eligible)
            and eligible == list(range(lo, lo + len(eligible))) and eligible[-1] <= hi):
        raise ValueError(f"eligible must be a nonempty list of int forming a prefix of PC {lo}..{hi}")
    V, lam, draws = _real_array(V, "V", 2), _real_array(lam, "lam", 1), _real_array(draws, "draws", 2)
    N, width = lam.size, len(eligible) if fixed is None else len(fixed)
    if not (V.shape == (N, N) and N >= eligible[-1] and (lam > 0).all() and (np.diff(lam) <= 0).all()):
        raise ValueError("need V (N, N) and a positive nonincreasing lam (N,) with N >= the last eligible PC")
    if not (_finite_nonnegative(I_star) and I_star > 0 and draws.shape[1] == width):
        raise ValueError(f"need a finite I_star > 0 and draws with {width} columns for {family}")
    if not ((draws != 0).any(axis=1).all() if fixed is None else (np.abs(draws) == 1).all()):
        raise ValueError("F0 draws need nonzero rows and the other families signs exactly -1 or +1")
    support = list(eligible) if fixed is None else list(fixed)
    if home != application or not set(support) <= set(eligible):
        return {"status": "UNSUPPORTED", "support": None, "delta": None, "q": None}
    cols, b = np.array(support) - 1, np.zeros((draws.shape[0], N))
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        if fixed is None:
            norm = np.sqrt((draws * draws).sum(axis=1))
            if not (np.isfinite(norm).all() and (norm > 0).all()):
                raise ValueError("an F0 direction norm is not representable as a finite positive float64")
            b[:, cols] = math.sqrt(2.0 * I_star) * draws / norm[:, None]
        else:
            b[:, cols] = draws * math.sqrt(2.0 * I_star / len(fixed))
        delta, q = (b * np.sqrt(lam)) @ V.T, b[:, np.array(eligible) - 1] ** 2 / 2.0
    if not (np.isfinite(delta).all() and np.isfinite(q).all() and (delta != 0).any(axis=1).all()
            and (q > 0).any(axis=1).all()):
        raise ValueError("every drift row needs finite values, a nonzero delta coordinate and a positive q coordinate")
    return {"status": "SUPPORTED", "support": support, "delta": delta, "q": q}


PROJECTION_ARMS = dict(zip(("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7"), INFO_BASES))


def _frozen_record(record, name):
    if not (isinstance(record, dict) and set(record) == {"V", "lam", "mean"}):
        raise ValueError(f"{name} must be a dict with exactly the keys V, lam and mean")
    V = _real_array(record["V"], f"{name}.V", 2)
    lam, mean = _real_array(record["lam"], f"{name}.lam", 1), _real_array(record["mean"], f"{name}.mean", 1)
    if not (V.shape == (lam.size, lam.size) and mean.shape == lam.shape
            and (lam > 0).all() and (np.diff(lam) <= 0).all()):
        raise ValueError(f"{name} needs V (N, N), mean (N,) and a positive nonincreasing lam (N,)")
    return V, lam, mean


def projection_diagnostics(frame, fit, eligible, deltas, arm):
    """Offline projection diagnostics of supplied drifts; frame and fit bases are frozen and orthonormal."""
    if not (isinstance(arm, str) and arm in PROJECTION_ARMS):
        raise ValueError(f"arm must be one of {sorted(PROJECTION_ARMS)}")
    (V, lam, mean), (V_fit, lam_fit, mean_fit) = _frozen_record(frame, "frame"), _frozen_record(fit, "fit")
    deltas, N = _real_array(deltas, "deltas", 2), lam.size
    if not (type(eligible) is list and eligible and all(type(k) is int for k in eligible) and eligible[0] in (1, 2)
            and eligible == list(range(eligible[0], eligible[0] + len(eligible))) and len(eligible) <= 20
            and eligible[-1] <= N):
        raise ValueError("eligible must list 1 to 20 int PCs, a consecutive prefix from PC 1 or PC 2 within N")
    if lam_fit.size != N or deltas.shape[1] != N:
        raise ValueError(f"fit and deltas must share the frame dimension N = {N}")
    pairs = ((V, V_fit), (lam, lam_fit), (mean, mean_fit))
    if arm == "EXACT" and not all(np.array_equal(a, b) for a, b in pairs):
        raise ValueError("the EXACT arm needs a fit equal to the population frame")
    cols = np.array(eligible) - 1
    U, scale = V_fit[:, cols], lam_fit[cols]
    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        W = U / np.sqrt(scale)
        A = W.T @ (V * np.sqrt(lam))
        c, C0, beta, q = (mean - mean_fit) @ W, A @ A.T, deltas @ W, pdb.q_plugin(deltas @ U, scale)
        if not all(np.isfinite(x).all() for x in (A, c, C0, beta, q)):
            raise ValueError("a projected diagnostic is not finite in float64")
        I_joint = np.array([pdb.kl_mean(row, C0) for row in beta], dtype=np.float64)
    if not (np.isfinite(I_joint).all() and (I_joint[(beta != 0).any(axis=1)] > 0).all()):
        raise ValueError("joint information must be finite, and positive on each row with a nonzero projected beta")
    return {"A": A, "c": c, "C0": C0, "var0": np.diag(C0), "beta": beta, "q": q, "I_joint": I_joint,
            "oracle_basis": PROJECTION_ARMS[arm]}


def head_geometry(frame, fit, istar, universe):
    """Joint HEAD geometry of the 16 sign profiles on frozen orthonormal bases; no kappa classification."""
    N = _frozen_record(frame, "frame")[1].size
    if _frozen_record(fit, "fit")[1].size != N:
        raise ValueError(f"fit must have the frame dimension N = {N}")
    if not (type(universe) is list and 4 <= len(universe) <= 20 and all(type(k) is int for k in universe)
            and universe == list(range(2, 2 + len(universe))) and universe[-1] <= N):
        raise ValueError("universe must list 4 to 20 int PCs forming the residual prefix from PC 2 within N")
    if not (_finite_nonnegative(istar) and istar > 0):
        raise ValueError("istar must be a finite real > 0")
    signs = [list(profile) for profile in itertools.product((-1, 1), repeat=4)]
    drift = population_drift(frame["V"], frame["lam"], "RESIDUAL", universe, "F_HEAD_RESIDUAL", istar,
                             np.array(signs))
    delta = drift["delta"]
    I_E = projection_diagnostics(frame, fit, universe, delta, "FITTED_LW_GAUSSIAN")["I_joint"].tolist()
    I_P4 = projection_diagnostics(frame, fit, universe[:4], delta, "FITTED_LW_GAUSSIAN")["I_joint"].tolist()
    f_E, f_pop = [p / e if e > 0 else None for p, e in zip(I_P4, I_E)], [p / istar for p in I_P4]
    if not all(math.isfinite(x) for x in [*f_pop, *(x for x in f_E if x is not None)]):
        raise ValueError("a HEAD geometry fraction is not finite in float64")
    summary = {name: {"min": None, "mean": None, "max": None} if None in values
               else {"min": min(values), "mean": math.fsum(values) / len(values), "max": max(values)}
               for name, values in (("f_E", f_E), ("f_pop", f_pop))}
    return {"support": drift["support"], "signs": signs, "delta": delta, "I_E": I_E, "I_P4": I_P4, "f_E": f_E,
            "f_pop": f_pop, "summary": summary, "all_I_E_positive": all(e > 0 for e in I_E)}


def fit_record(X_fit, K):
    """Fit record {V, lam, mean} of supplied FIT_NULL rows: one sealed LW fit, row mean, T22 gap guard."""
    X, K = _real_array(X_fit, "X_fit", 2), _count(K, "K", 1)
    T, N = X.shape
    if not (T >= 2 and K <= 20 and N >= K + 2 and (X.max(axis=0) > X.min(axis=0)).all()):
        raise ValueError("need T >= 2 rows, 1 <= K <= 20, N >= K + 2 columns and no constant column")
    with np.errstate(over="ignore", invalid="ignore"):
        mean = X.mean(axis=0)
    if not np.isfinite(mean).all():
        raise ValueError("the row mean of X_fit is not finite in float64")
    fitted = pdb.fit_basis(X)
    V, lam, mean = _frozen_record({"V": fitted["eigvec"], "lam": fitted["eigval"], "mean": mean}, "fit")
    head = lam[:K + 2]
    if ((head[:-1] - head[1:]) / head[:-1] < 1e-10).any():
        raise ValueError(f"a relative LW eigengap among the first K + 2 = {K + 2} axes is below 1e-10 (T22)")
    return {"V": V, "lam": lam, "mean": mean}


def _setup_parameters(desc, setup):
    try:
        science, apps = desc["science"], list(desc["scope"]["applications"])
        params, kappa = science["parameters"], science["head"]["kappa_geo"]
        K, T_fit, istar = params["K"], params["T_fit"], params["I_star"]
        planned = type(setup) is list and pdb.canon(setup) in [pdb.canon(s) for s in desc["scope"]["setups"]]
        canonical = all(pdb.canon(science["applications"][app]) == pdb.canon(list(UNIVERSES[app])) for app in apps)
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must be a pre-execution descriptor and setup a planned JSON coordinate") from exc
    if not (desc.get("schema_version") == SCHEMA_VERSION and planned
            and setup[0] in ("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7")
            and canonical and type(K) is int and K == 20 and type(T_fit) is int and T_fit >= 2
            and _finite_nonnegative(istar) and istar > 0 and _finite_nonnegative(kappa)):
        raise ValueError("need a planned supported setup and valid K, T_fit, I_star, kappa_geo and universes in desc")
    return apps, K, T_fit, istar, kappa


def _setup_metadata(desc, frame, fit, setup):
    apps, _, _, istar, kappa = _setup_parameters(desc, setup)
    (arm, N, fit_id), (V, lam, mean) = setup, _frozen_record(frame, "frame")
    did, basis = design_id(desc), pdb.array_sha256(V, lam, mean)
    fit_hash = None if arm == "EXACT" else pdb.array_sha256(fit["V"], fit["lam"], fit["mean"])
    applications = {}
    for app in apps:
        universe = list(range(UNIVERSES[app][0], UNIVERSES[app][1] + 1))
        head = {"status": "NOT_APPLICABLE", "kappa_geo": None, "geometry": None}
        if app == "RESIDUAL":
            geometry = {k: v for k, v in head_geometry(frame, fit, istar, universe).items() if k != "delta"}
            aligned = geometry["all_I_E_positive"] and geometry["summary"]["f_E"]["min"] >= kappa
            head = {"status": "GEOMETRY_ALIGNED" if aligned else "DESIGN_CONTROL_INCONCLUSIVE", "kappa_geo": kappa,
                    "geometry": geometry}
        identity = {"design_id": did, "arm": arm, "N": N, "fit_id": fit_id, "application": app,
                    "universe_pcs": universe, "basis_sha": basis, "fit_hash": fit_hash}
        applications[app] = {"universe": universe, "setup_id": pdb.sha16(identity),
                             "baselines": spectral_baselines(fit["lam"], app)["baselines"], "head": head}
    metadata = {"design_id": did, "setup": list(setup), "basis_sha": basis, "fit_hash": fit_hash,
                "applications": applications}
    if arm == "FITTED_LW_T7":
        metadata["information_basis"] = "GAUSSIAN_PROXY"
    return metadata


def setup_bundle(desc, frame, X_fit, setup):
    """Gaussian or T7-proxy SETUP of a planned coordinate from supplied inputs: shared fit, baselines, HEAD, ids."""
    _, K, T_fit, _, _ = _setup_parameters(desc, setup)
    (arm, N, _), (V, lam, mean) = setup, _frozen_record(frame, "frame")
    exact = arm == "EXACT"
    if lam.size != N or (X_fit is not None if exact else np.shape(X_fit) != (T_fit, N)):
        raise ValueError(f"need a frame of dimension {N} and X_fit None for EXACT or of shape ({T_fit}, {N})")
    fit = {"V": V, "lam": lam, "mean": mean} if exact else fit_record(X_fit, K)
    fit = {key: fit[key] for key in ("V", "lam", "mean")}
    return {"metadata": _setup_metadata(desc, frame, fit, setup), "fit": fit}


def _setup_cache(arrays, key):
    V, lam, mean = _frozen_record(arrays, key[0])
    N = key[2] if key[0] == "frame" else key[3]
    if lam.size != N or (key[0] == "frame" and mean.any()):
        raise ValueError(f"{key} needs a {key[0]} record of its planned dimension {N}, a frame with a zero mean")
    return {"V": V, "lam": lam, "mean": mean}


def setup_phase(cfg, mode, context):
    """Verified SETUP phase record: guarded frame then FIT_NULL fit caches and shared metadata, or its reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    keys = sorted(([*key] for key in seed_plan(cfg, mode)["keys"] if key[0] in ("frame", "fit")), key=pdb.canon)
    if pdb.canon(plan["SETUP"]) != pdb.canon(keys):
        raise ValueError(f"the SETUP plan must schedule exactly the primitive frame and fit keys {keys}")
    setups, K, campaign = desc["scope"]["setups"], desc["science"]["parameters"]["K"], desc["campaign"]
    for setup in setups:
        _setup_parameters(desc, setup)

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def checked(arrays, key):
        try:
            return _setup_cache(arrays, key)
        except ValueError as exc:
            raise PartitionMismatch(f"the cached SETUP partition {key} is not a valid planned record") from exc

    try:
        records, missing = _planned_progress(staging, did, desc, plan, None)
        absent = {pdb.canon(entry["key"]) for entry in missing if entry["phase"] == "SETUP"}
        caches = {pdb.canon(key): checked(_verify_partition(staging, did, {}, key)[2], key)
                  for key in keys if pdb.canon(key) not in absent}
        if "SETUP" in records:
            derived = records["SETUP"]["derived"] if isinstance(records["SETUP"]["derived"], dict) else {}
            members = derived["setups"] if set(derived) == {"setups"} else None
            if not isinstance(members, dict) or sorted(members) != sorted(pdb.canon(s) for s in setups):
                raise PartitionMismatch(f"the committed SETUP record does not hold exactly the scoped setups {setups}")
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    if "SETUP" in records:
        return records["SETUP"]

    def produce(key):
        if key[0] == "frame":
            V, lam = population_frame(cfg, mode, key[2])
            return _setup_cache({"V": V, "lam": lam, "mean": np.zeros(key[2])}, key)
        fit = fit_record(null_returns(desc, caches[pdb.canon(["frame", campaign, key[3]])], tuple(key)), K)
        return _setup_cache({name: fit[name] for name in ("V", "lam", "mean")}, key)

    for key in sorted(keys, key=lambda k: k[0] != "frame"):
        if pdb.canon(key) not in caches:
            arrays = guarded_partition(context, "SETUP", {}, key, lambda key=key: produce(key))
            caches[pdb.canon(key)] = checked(arrays, key)
    checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    metadata = {}
    try:
        for setup in setups:
            frame = caches[pdb.canon(["frame", campaign, setup[1]])]
            fit = frame if setup[0] == "EXACT" else caches[pdb.canon(["fit", campaign, *setup])]
            metadata[pdb.canon(setup)] = _setup_metadata(desc, frame, fit, setup)
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    return phase_record(staging, "SETUP", {}, keys, {"setups": metadata})


def _planned_null_key(desc, key, arms):
    if not (type(key) is tuple and key and (key[0], len(key)) in (("fit", 5), ("path", 7))):
        raise ValueError(f"key must be ('fit', campaign, arm, N, fit_id) or ('path', ..., role, i), got {key!r}")
    (domain, campaign, arm), N, fit_id = key[:3], _word(key[3], "N"), _word(key[4], "fit_id")
    role, i = (key[5], _word(key[6], "i")) if domain == "path" else (None, None)
    try:
        seed, coordinate = _word(desc["seed"], "seed"), pdb.canon([arm, N, fit_id])
        planned = coordinate in [pdb.canon(setup) for setup in desc["scope"]["setups"]]
        primary = _plan_applies(desc) and coordinate == pdb.canon(desc["science"]["phi"]["setup"])
        cap = desc["sizes"].get(role, 0) if role in PATH_ROLES else 0
        if primary and role in ("NULL_PLAN", "HOLD_NULL"):
            cap = desc["null_plan"]["n_plan" if role == "NULL_PLAN" else "n_cap"]
        if primary and role == "CAL_NULL" and "allocation" in desc:
            cap = desc["allocation"]["primary_cal_null"]
        rows = desc["science"]["parameters"]["T_fit" if domain == "fit" else "H"]
        same = desc["campaign"] == campaign
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("desc must be a pre-execution design descriptor") from exc
    if not (same and arm in arms and planned
            and ((domain == "fit" and arm != "EXACT") or (role in PATH_ROLES and i < _word(cap, "cap")))):
        raise ValueError(f"{key!r} is not a planned {arms} fit or path key of this design within its plan cap")
    rows = _count(rows, "T_fit" if domain == "fit" else "H", 1)
    parts = (arm, N, fit_id) if domain == "fit" else (arm, N, fit_id, role, i)
    words = [32, seed, pdb.label_code(campaign), pdb.label_code(domain),
             *(pdb.label_code(part) if isinstance(part, str) else part for part in parts)]
    return words, rows, N, arm


def null_returns(desc, frame, key):
    """Drift-free (T_fit or H, N) returns of a planned FITTED fit or path seed key on a frozen orthonormal frame."""
    words, rows, N, arm = _planned_null_key(desc, key, ("FITTED_LW_GAUSSIAN", "FITTED_LW_T7"))
    V, lam, mean = _frozen_record(frame, "frame")
    if lam.size != N:
        raise ValueError(f"the frame dimension {lam.size} differs from the key dimension N = {N}")
    rng = np.random.default_rng(np.random.SeedSequence(words))
    g = pdb.sim.t_innov(rng, (rows, N)) if arm == "FITTED_LW_T7" else rng.standard_normal((rows, N))
    with np.errstate(over="ignore", invalid="ignore"):
        returns = mean + (g * np.sqrt(lam)) @ V.T
    if not np.isfinite(returns).all():
        raise ValueError("the drift-free returns are not finite in float64")
    return returns


def exact_scores(desc, key):
    """Standardized iid N(0, 1) null scores (H, 21) of population PC1..21 for a planned EXACT path seed key."""
    words, rows, N, _ = _planned_null_key(desc, key, ("EXACT",))
    K = desc["science"]["parameters"].get("K")
    if not (type(K) is int and K == 20 and N >= K + 1):
        raise ValueError(f"exact scores need K the Python int 20 and a planned N >= 21, got K = {K!r}, N = {N}")
    scores = np.random.default_rng(np.random.SeedSequence(words)).standard_normal((rows, K + 1))
    if not np.isfinite(scores).all():
        raise ValueError("the exact null scores are not finite in float64")
    return scores


def direction_draws(desc, key):
    """Raw (1, width) direction or sign row of a planned meta or devlib seed key, the draws of population_drift."""
    if not (type(key) is tuple and key and (key[0], len(key)) in (("meta", 8), ("devlib", 7))):
        raise ValueError(f"key must be ('meta', ..., role, family, i) or ('devlib', ..., family, l), got {key!r}")
    (domain, campaign, arm), N, fit_id = key[:3], _word(key[3], "N"), _word(key[4], "fit_id")
    meta = domain == "meta"
    role, family, index = (key[5], key[6], _word(key[7], "i")) if meta else ("DEV_LIB", key[5], _word(key[6], "l"))
    try:
        seed, coordinate = _word(desc["seed"], "seed"), pdb.canon([arm, N, fit_id])
        planned = coordinate in [pdb.canon(setup) for setup in desc["scope"]["setups"]]
        primary = _plan_applies(desc) and coordinate == pdb.canon(desc["science"]["phi"]["setup"])
        pool = desc["science"]["dev"]["families"] if role in ("DEV_LIB", "DEV_ALT") else desc["scope"]["families"]
        cap = desc["sizes"].get(role, 0)
        if primary and role == "HOLD_NULL" and "allocation" not in desc:
            cap = desc["null_plan"]["n_cap"]
        K, same = desc["science"]["parameters"].get("K"), desc["campaign"] == campaign
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("desc must be a pre-execution design descriptor") from exc
    if not (same and arm in ("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7") and planned and type(K) is int
            and K == 20 and N >= K + 1 and (not meta or role in ("DEV_ALT", "CAL_NULL", "HOLD_NULL", "ALT"))
            and isinstance(family, str) and family in DRIFT_FAMILIES and family in pool and index < _word(cap, "cap")):
        raise ValueError(f"{key!r} is not a planned meta or devlib key of this design within its plan cap")
    parts = (arm, N, fit_id, role, family, index) if meta else (arm, N, fit_id, family, index)
    words = [32, seed, pdb.label_code(campaign), pdb.label_code(domain),
             *(pdb.label_code(part) if isinstance(part, str) else part for part in parts)]
    fixed = DRIFT_FAMILIES[family][1]
    rng = np.random.default_rng(np.random.SeedSequence(words))
    row = rng.standard_normal((1, K)) if fixed is None else rng.choice((-1.0, 1.0), size=(1, len(fixed)))
    if not (np.isfinite(row).all() and row.any()):
        raise ValueError("a raw direction row must be finite and nonzero in float64")
    return row


def path_scores(desc, frame, fit, application, key, delta=None):
    """Observed (H, 20) universe scores of a planned path key: one received null draw, return delta, frozen fit."""
    if not (type(key) is tuple and len(key) == 7 and key[0] == "path"):
        raise ValueError(f"key must be a primitive ('path', campaign, arm, N, fit_id, role, i) tuple, got {key!r}")
    _, _, N, arm = _planned_null_key(desc, key, ("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7"))
    try:
        K, (lo, hi) = desc["science"]["parameters"].get("K"), UNIVERSES[application]
        scoped = application in desc["scope"]["applications"]
        canonical = pdb.canon(desc["science"]["applications"][application]) == pdb.canon([lo, hi])
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"application must be a scoped canonical universe of {sorted(UNIVERSES)}") from exc
    if not (type(K) is int and K == 20 and N >= K + 1 and scoped and canonical):
        raise ValueError(f"need K the int 20, a planned N >= 21 and a scoped canonical {application!r} universe")
    (V, lam, mean), (V_fit, lam_fit, mean_fit) = _frozen_record(frame, "frame"), _frozen_record(fit, "fit")
    exact = arm == "EXACT"
    same = all(np.array_equal(a, b) for a, b in ((V, V_fit), (lam, lam_fit), (mean, mean_fit)))
    if not (lam.size == lam_fit.size == N and (same or not exact)):
        raise ValueError("frame and fit need the planned dimension N, and an EXACT fit must equal the frame")
    shifted = key[5] in ("ALT", "DEV_ALT")
    if shifted:
        delta = _real_array(delta, "delta", 1)
    if not (delta.shape == (N,) and delta.any() if shifted else delta is None):
        raise ValueError("ALT and DEV_ALT need a finite nonzero return delta of shape (N,), null roles need None")
    cols = slice(lo - 1, hi)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        W = (V if exact else V_fit)[:, cols] / np.sqrt((lam if exact else lam_fit)[cols])
    if not np.isfinite(W).all():
        raise ValueError("the projection scaling V_E / sqrt(lam_E) is not finite in float64")
    with np.errstate(over="ignore", invalid="ignore"):
        if exact:
            draws = exact_scores(desc, key)[:, cols]
            scores = draws + delta @ W if shifted else draws.copy()
        else:
            X = null_returns(desc, frame, key)
            scores = ((X + delta if shifted else X) - mean_fit) @ W
    if not np.isfinite(scores).all():
        raise ValueError("the combined observations are not finite in float64")
    return scores


def _require_startup_env():
    """Raise RuntimeError carrying every startup environment problem reported by pdb.check_env."""
    problems = pdb.check_env()
    if problems:
        raise RuntimeError("; ".join(map(str, problems)))


def _path_deadline(deadline):
    """Return seconds left before an absolute monotonic deadline, raising ResourceBlocked once it has passed."""
    if deadline is None:
        return None
    left = deadline - time.monotonic()
    if left <= 0:
        raise ResourceBlocked("path scoring deadline expired")
    return left


def _score_path_block(task):
    """Score one bounded request block in a spawned worker after its own startup environment check."""
    desc, frame, fit, application, block = task
    _require_startup_env()
    return [path_scores(desc, frame, fit, application, key, delta) for key, delta in block]


def score_path_batch(desc, frame, fit, application, requests, *, jobs=1, deadline=None):
    """Score ordered (path key, delta) requests into one float64 stack of path_scores rows, locally or in a bounded spawn pool."""
    jobs = _count(jobs, "jobs", 1)
    cap = desc["envelope"]["jobs_max"]
    if jobs > cap:
        raise ValueError(f"jobs={jobs} exceeds envelope jobs_max={cap}")
    items = [(key, delta) for key, delta in requests]
    if not items:
        raise ValueError("requests must be a nonempty sequence of (key, delta) pairs")
    if deadline is not None and (isinstance(deadline, (bool, np.bool_)) or not _finite_nonnegative(deadline)):
        raise ValueError(f"deadline must be None or a finite nonnegative number, got {deadline!r}")
    _require_startup_env()
    _path_deadline(deadline)
    if jobs == 1:
        rows = []
        for key, delta in items:
            rows.append(path_scores(desc, frame, fit, application, key, delta))
            _path_deadline(deadline)
        stacked = np.stack(rows)
        _path_deadline(deadline)
        return stacked
    size = min(100, -(-len(items) // jobs))
    tasks = [(desc, frame, fit, application, items[i:i + size]) for i in range(0, len(items), size)]
    with multiprocessing.get_context("spawn").Pool(processes=min(jobs, len(tasks))) as pool:
        stream = pool.imap(_score_path_block, tasks, chunksize=1)
        rows = []
        try:
            for _ in tasks:
                rows.extend(stream.next(timeout=_path_deadline(deadline)))
        except multiprocessing.TimeoutError as error:
            raise ResourceBlocked("path scoring deadline expired") from error
        _path_deadline(deadline)
        pool.close()
        pool.join()
    stacked = np.stack(rows)
    _path_deadline(deadline)
    return stacked


def _score_requests(desc, frame, fit, application, requests, context):
    return score_path_batch(desc, frame, fit, application, requests, jobs=context.get("jobs", 1),
                            deadline=context["started"] + desc["envelope"]["wall_seconds_per_invocation"])


def direction_information(desc, frame, fit, setup, application, key):
    """One planned meta or devlib key: population return drift and its frozen-fit offline projection."""
    apps, _, _, istar, _ = _setup_parameters(desc, setup)
    arm, N, fit_id = setup
    if not (type(key) is tuple and (key[:1], len(key)) in ((("meta",), 8), (("devlib",), 7)) and application in apps):
        raise ValueError(f"need a planned meta or devlib tuple key and a scoped application of {apps}, got {key!r}")
    if [key[2], _word(key[3], "N"), _word(key[4], "fit_id")] != [arm, N, fit_id]:
        raise ValueError(f"{key!r} does not belong to the setup coordinate {setup}")
    (V, lam, mean), fitted = _frozen_record(frame, "frame"), _frozen_record(fit, "fit")
    same = all(np.array_equal(a, b) for a, b in zip((V, lam, mean), fitted))
    if lam.size != N or fitted[1].size != N or (arm == "EXACT" and not same):
        raise ValueError(f"frame and fit need the setup dimension N = {N}, and an EXACT fit must equal the frame")
    family = key[6] if key[0] == "meta" else key[5]
    universe = list(range(UNIVERSES[application][0], UNIVERSES[application][1] + 1))
    drift = population_drift(V, lam, application, universe, family, istar, direction_draws(desc, key))
    if drift["status"] != "SUPPORTED":
        return {"status": drift["status"], "family": family,
                **dict.fromkeys(("support", "delta", "q", "I_joint", "oracle_basis"))}
    out = projection_diagnostics(frame, fit, universe, drift["delta"], arm)
    return {"status": "SUPPORTED", "family": family, "support": drift["support"], "delta": drift["delta"][0],
            "q": out["q"][0], "I_joint": float(out["I_joint"][0]), "oracle_basis": out["oracle_basis"]}


def dev_qbar(desc, q_by_family):
    """Equal-weight DEV qbar: mean over the four DEV families of each family's mean q over its n_lib rows."""
    try:
        dev, K = desc["science"]["dev"], desc["science"]["parameters"]["K"]
        families, n_lib = sorted(dev["families"]), dev["n_lib"]
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must be a pre-execution descriptor holding the DEV families, n_lib and K") from exc
    known = isinstance(q_by_family, dict) and set(q_by_family) == set(DEV_FAMILIES)
    if not (known and families == sorted(DEV_FAMILIES)):
        raise ValueError(f"q_by_family must map exactly the four DEV families {DEV_FAMILIES} to their library q arrays")
    n_lib, K = _count(n_lib, "n_lib", 1), _count(K, "K", 1)
    pools = [_real_array(q_by_family[family], family, 2) for family in DEV_FAMILIES]
    if any(q.shape != (n_lib, K) or (q < 0).any() for q in pools):
        raise ValueError(f"each DEV family needs a nonnegative q array of shape (n_lib, K) = ({n_lib}, {K})")
    with np.errstate(over="ignore", invalid="ignore"):
        qbar = np.mean([q.mean(axis=0) for q in pools], axis=0)
    if not np.isfinite(qbar).all():
        raise ValueError("the equal-weight DEV qbar is not finite in float64")
    return qbar


def common_prior(desc):
    """Common detector prior 2 ln(H / alpha) / (H K) of the declared parameters, shared by every policy."""
    try:
        params = desc["science"]["parameters"]
        H, alpha, K, rule = params["H"], params["alpha"], params["K"], params["s2_rule"]
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must be a pre-execution descriptor holding H, alpha, K and s2_rule") from exc
    if rule != "2*ln(H/alpha)/(H*K)" or not (_finite_nonnegative(alpha) and 0 < alpha < 1):
        raise ValueError(f"need the rule 2*ln(H/alpha)/(H*K) and a real alpha in (0, 1), got {rule!r} and {alpha!r}")
    H, K = _count(H, "H", 1), _count(K, "K", 1)
    try:
        s2 = 2.0 * math.log(H / alpha) / (H * K)
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("the common prior of the declared H, alpha and K is not representable in float64") from exc
    if not (math.isfinite(s2) and s2 > 0):
        raise ValueError(f"the common prior {s2!r} is not a finite positive float")
    return s2


def frozen_policy(desc, application, label, baselines=None, qbar=None, d_dev=None):
    """Declared frozen policy of one application: outer label/status/prior bundle around the received mask schema."""
    s2, science = common_prior(desc), desc["science"]
    try:
        params, policies, grid = science["parameters"], science["policies"], science["dev"]["d_grid"]
        online, oracle, static = policies["online"], policies["oracle"], list(policies["static"])
        declared = {f"ONLINE_{o}_{c}_W{w}": ("ONLINE", o, c, w) for o in online["orders"] for c in online["costs"]
                    for w in online["windows"]}
        declared.update({f"ORACLE_{o}_{c}": ("ORACLE", o, c, None) for o in oracle["orders"] for c in oracle["costs"]})
        lo, hi = UNIVERSES[application]
        canonical = pdb.canon(science["applications"][application]) == pdb.canon([lo, hi])
        K, H, gamma = params["K"], params["H"], params["gamma_M"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"desc must declare the policies and a canonical universe for {application!r}") from exc
    if not (canonical and isinstance(label, str) and (label in declared or label in static) and K == hi - lo + 1):
        raise ValueError(f"{label!r} is not a declared policy of the canonical {application!r} universe of K = {K}")
    bundle = {"label": label, "application": application, "status": "RUNNABLE", "s2": s2, "policy": None}
    if label in declared:
        kind, order, cost, window = declared[label]
        costs = cost_vectors(gamma, K)
        if order not in ORDERS or cost not in costs:
            raise ValueError(f"{label!r} declares an order or a cost outside {ORDERS} and {sorted(costs)}")
        if kind == "ONLINE":
            policy = {"kind": "ONLINE", "window": _count(window, "window", 1), "cost": costs[cost], "order": order}
        else:
            policy = {"kind": "ORACLE", "H": H, "cost": costs[cost], "order": order}
        return {**bundle, "policy": policy}
    if label == "FULL_K":
        return {**bundle, "policy": {"kind": "STATIC", "mask": np.ones(K, dtype=bool)}}
    if label in ("FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90"):
        row = baselines.get(label) if isinstance(baselines, dict) else None
        status, pcs = (row.get("status"), row.get("pcs")) if isinstance(row, dict) else (None, None)
        if status in ("OUTSIDE_UNIVERSE", "UNSUPPORTED") and pcs is None:
            return {**bundle, "status": status}
        if not (status == "RUNNABLE" and type(pcs) is list and pcs and all(type(k) is int for k in pcs)
                and pcs == sorted(set(pcs)) and lo <= pcs[0] and pcs[-1] <= hi):
            raise ValueError(f"{label!r} needs its frozen status row, RUNNABLE with sorted unique PCs in {lo}..{hi}")
        mask = np.zeros(K, dtype=bool)
        mask[np.array(pcs) - lo] = True
        return {**bundle, "policy": {"kind": "STATIC", "mask": mask}}
    if label == "FIXED_DEV_PREFIX":
        if application != "RESIDUAL":
            return {**bundle, "status": "NOT_RUN"}
        if not (type(d_dev) is int and isinstance(grid, list) and d_dev in grid and 1 <= d_dev <= K):
            raise ValueError(f"FIXED_DEV_PREFIX needs a frozen int d_dev of the declared grid in 1..{K}, got {d_dev!r}")
        return {**bundle, "policy": {"kind": "STATIC", "mask": np.arange(K) < d_dev}}
    if label == "FIXED_EXANTE_QBAR_MIX":
        if application != "RESIDUAL":
            return {**bundle, "status": "UNSUPPORTED"}
        q = _real_array(qbar, "qbar", 1)
        if q.shape != (K,) or (q < 0).any():
            raise ValueError(f"FIXED_EXANTE_QBAR_MIX needs a frozen nonnegative qbar of shape ({K},)")
        mask = best_sets(q[None, :], cost_vectors(gamma, K)["MIX"], "INFO")[1][0]
        return {**bundle, "policy": {"kind": "STATIC", "mask": mask}}
    raise ValueError(f"{label!r} is a declared static label without a frozen policy definition")


def _scan_inputs(Y, bundle):
    shaped = isinstance(bundle, dict) and set(bundle) == {"label", "application", "status", "s2", "policy"}
    s2 = bundle["s2"] if shaped else None
    if not (shaped and bundle["status"] == "RUNNABLE" and isinstance(bundle["policy"], dict)
            and _finite_nonnegative(s2) and s2 > 0):
        raise ValueError("need a RUNNABLE frozen bundle {label, application, status, s2, policy} with a finite s2 > 0")
    Y = _real_array(Y, "Y", 3)
    if Y.shape[2] != 20:
        raise ValueError(f"Y must hold the local scores (B, H, 20) of a 20-axis application universe, got {Y.shape}")
    return Y, bundle["policy"], s2


def _scan_result(Y, M, s2, h):
    W, first = masked_scan(Y, M, s2, h)
    bits = (np.asarray(M, dtype=np.uint32) << np.arange(M.shape[2], dtype=np.uint32)).sum(axis=2, dtype=np.uint32)
    return {"W": W, "first": first, "mask_bits": bits}


def nonoracle_scan(Y, bundle, h=None):
    """Masked scan of supplied real local scores under a frozen ONLINE or STATIC bundle, s2 unchanged."""
    Y, policy, s2 = _scan_inputs(Y, bundle)
    return _scan_result(Y, nonoracle_masks(Y, policy), s2, h)


def oracle_scan(Y, q_true, bundle, h=None):
    """Oracle masked scan of supplied real local scores and true q under a frozen ORACLE bundle, s2 unchanged."""
    Y, policy, s2 = _scan_inputs(Y, bundle)
    q = _real_array(q_true, "q_true", 2)
    if q.shape != (Y.shape[0], 20) or (q < 0).any():
        raise ValueError(f"q_true must be a nonnegative real array of shape ({Y.shape[0]}, 20), got {q.shape}")
    return _scan_result(Y, oracle_masks(q, policy), s2, h)


def gamma_sensitivity_policy(desc, bundle):
    """gamma_M = H/alpha sensitivity of a primary bundle: new MIX cost for ONLINE_{INFO,PREFIX}_MIX_W128 only."""
    if not (isinstance(bundle, dict) and set(bundle) == {"label", "application", "status", "s2", "policy"}
            and _finite_nonnegative(bundle["s2"]) and bundle["s2"] > 0):
        raise ValueError("need a primary bundle {label, application, status, s2, policy} with a finite s2 > 0")
    label, status, policy = bundle["label"], bundle["status"], bundle["policy"]
    if label in ("FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90", "FIXED_DEV_PREFIX",
                 "FIXED_EXANTE_QBAR_MIX"):
        if status == "RUNNABLE":
            _policy_kind(policy, {"STATIC": {"kind", "mask"}})
            mask = policy["mask"]
            if not (isinstance(mask, np.ndarray) and mask.dtype == bool and mask.shape == (20,) and mask.any()):
                raise ValueError(f"a RUNNABLE {label!r} primary bundle needs a non-empty bool mask of shape (20,)")
        elif not (status in ("OUTSIDE_UNIVERSE", "UNSUPPORTED", "NOT_RUN") and policy is None):
            raise ValueError(f"a non-runnable {label!r} primary bundle needs a declared status and no policy")
        return bundle
    if label not in ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128") or status != "RUNNABLE":
        raise ValueError(f"no planned gamma_M sensitivity for {label!r} with status {status!r}")
    _policy_kind(policy, {"ONLINE": {"kind", "window", "cost", "order"}})
    cost = _real_array(policy["cost"], "cost", 1)
    if not (type(policy["window"]) is int and policy["window"] == 128 and policy["order"] == label.split("_")[1]
            and cost.shape == (20,) and (cost > 0).all()):
        raise ValueError(f"{label!r} needs its primary ONLINE window 128, order and a positive cost of shape (20,)")
    try:
        params = desc["science"]["parameters"]
        H, K = _count(params["H"], "H", 1), _count(params["K"], "K", 1)
        alpha, gamma = params["alpha"], params["gamma_M_sensitivity"]
        planned = H / alpha if _finite_nonnegative(alpha) and 0 < alpha < 1 else None
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError("desc must declare H, K, alpha and gamma_M_sensitivity") from exc
    if K != cost.size:
        raise ValueError(f"K = {K} differs from the primary cost of shape {cost.shape}")
    if not (planned is not None and _finite_nonnegative(gamma) and gamma > 1 and gamma == planned):
        raise ValueError(f"gamma_M_sensitivity {gamma!r} must be a finite real > 1 equal to H / alpha = {planned!r}")
    return {**bundle, "policy": {**policy, "cost": cost_vectors(planned, K)["MIX"]}}


DEV_PRIOR = "ISOTROPIC_ZERO_MEAN_GAUSSIAN"
P_CONF = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128", "FULL_K")


def policy_rule(desc, label, gamma_sensitivity=False, s2_sensitivity=False):
    """Pre-execution effective rule recipe of a declared policy label and its policy_rule_id = pdb.sha16(recipe)."""
    if type(gamma_sensitivity) is not bool:
        raise ValueError(f"gamma_sensitivity must be a bool, got {gamma_sensitivity!r}")
    if type(s2_sensitivity) is not bool:
        raise ValueError(f"s2_sensitivity must be a bool, got {s2_sensitivity!r}")
    try:
        science = desc["science"]
        params, policies = science["parameters"], science["policies"]
        s2_rule, online, oracle = params["s2_rule"], policies["online"], policies["oracle"]
        static = list(policies["static"])
        declared = {f"ONLINE_{o}_{c}_W{w}": ("ONLINE", o, c, w) for o in online["orders"] for c in online["costs"]
                    for w in online["windows"]}
        declared.update({f"ORACLE_{o}_{c}": ("ORACLE", o, c, None) for o in oracle["orders"] for c in oracle["costs"]})
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must declare science.parameters.s2_rule and the science.policies registry") from exc
    subsets = {"FULL_K": "FULL_K", "FIXED_EIGENMEAN_PREFIX": "EIGENMEAN", "CPV90": "CPV90",
               "RESIDUAL_CPV90": "RESIDUAL_CPV90", "FIXED_DEV_PREFIX": "DEV_PREFIX", "FIXED_EXANTE_QBAR_MIX": "EXANTE"}
    if not (isinstance(label, str) and (label in declared or (label in static and label in subsets))
            and isinstance(s2_rule, str)):
        raise ValueError(f"{label!r} is not a declared policy with a frozen rule, or s2_rule is not a string")
    recipe = {"kind": "STATIC", "order": None, "cost": None, "gamma_M": None, "window": None, "fallback": None,
              "ties": None, "s2_rule": s2_rule, "subset_rule": subsets.get(label)}
    if label == "FIXED_DEV_PREFIX":
        try:
            grid, criterion, ties = science["dev"]["d_grid"], science["dev"]["criterion"], science["dev"]["ties"]
        except (KeyError, TypeError) as exc:
            raise ValueError("FIXED_DEV_PREFIX needs the declared science.dev d_grid, criterion and ties") from exc
        if not (isinstance(grid, list) and grid and isinstance(criterion, str) and isinstance(ties, str)):
            raise ValueError("the declared DEV rule needs a non-empty d_grid list and string criterion and ties")
        candidates = sorted(_count(d, "d_grid", 1) for d in grid)
        if len(set(candidates)) != len(candidates):
            raise ValueError(f"the declared d_grid {grid!r} repeats a candidate")
        recipe["subset_rule"] = {"kind": "DEV_PREFIX", "d_grid": candidates, "criterion": criterion, "ties": ties}
    elif label in declared or label == "FIXED_EXANTE_QBAR_MIX":
        kind, order, cost, window = declared.get(label, ("STATIC", "INFO", "MIX", None))
        if order not in ORDERS or cost not in ("MIX", "AFF"):
            raise ValueError(f"{label!r} declares an order or a cost outside {ORDERS} and ('MIX', 'AFF')")
        if gamma_sensitivity and label in ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128"):
            try:
                H, alpha, gamma = _count(params["H"], "H", 1), params["alpha"], params["gamma_M_sensitivity"]
                planned = H / alpha if _finite_nonnegative(alpha) and 0 < alpha < 1 else None
            except (KeyError, OverflowError) as exc:
                raise ValueError("the gamma_M sensitivity needs declared H, alpha and gamma_M_sensitivity") from exc
            if not (planned is not None and _finite_nonnegative(gamma) and gamma > 1 and gamma == planned):
                raise ValueError(f"gamma_M_sensitivity {gamma!r} must be a finite real > 1 equal to H / alpha")
            gamma = planned
        elif gamma_sensitivity and label != "FIXED_EXANTE_QBAR_MIX":
            raise ValueError(f"no planned gamma_M sensitivity for {label!r}")
        else:
            gamma = params.get("gamma_M")
            if not (_finite_nonnegative(gamma) and gamma > 1):
                raise ValueError(f"the primary gamma_M must be a finite real > 1, got {gamma!r}")
        recipe.update(kind=kind, order=order, cost="MIX" if cost == "MIX" else "AFF_OLS_1_16", gamma_M=float(gamma),
                      window=None if window is None else _count(window, "window", 1),
                      fallback="MIN_E" if kind == "ONLINE" else None, ties="SMALLEST_D_THEN_INDEX",
                      subset_rule={"ONLINE": "ONLINE_QHAT", "ORACLE": "ORACLE_Q"}.get(kind, "EXANTE"))
    if s2_sensitivity:
        try:
            grid, criterion, ties = science["dev"]["s2_grid"], science["dev"]["criterion"], science["dev"]["ties"]
        except (KeyError, TypeError) as exc:
            raise ValueError("the s2_dev sensitivity needs the declared science.dev s2_grid, criterion and ties") from exc
        if gamma_sensitivity or label not in P_CONF:
            raise ValueError(f"no planned s2_dev sensitivity for {label!r}: P_conf only, never combined with gamma_M")
        if not (_dev_grid(grid, math.inf) and isinstance(criterion, str) and isinstance(ties, str)):
            raise ValueError(f"the s2_dev rule needs a unique positive int s2_grid, a criterion and ties, got {grid!r}")
        recipe["s2_rule"] = {"kind": "S2_DEV", "common": s2_rule, "s2_grid": sorted(grid), "criterion": criterion,
                             "ties": ties}
    return {"recipe": recipe, "policy_rule_id": pdb.sha16(recipe)}


def dev_library_block(desc, frame, fit, setup, family):
    """{'q': (n_lib, 20)} of one residual DEV family, stacked from the received direction_information rows."""
    apps = _setup_parameters(desc, setup)[0]
    try:
        dev, cap, campaign = desc["science"]["dev"], desc["sizes"]["DEV_LIB"], desc["campaign"]
        declared, n_lib = dev["families"], dev["n_lib"]
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must declare the DEV families, n_lib, sizes.DEV_LIB and the campaign") from exc
    if not ("RESIDUAL" in apps and isinstance(family, str) and family in DEV_FAMILIES and isinstance(campaign, str)
            and isinstance(declared, list) and all(isinstance(f, str) for f in declared)
            and sorted(declared) == sorted(DEV_FAMILIES)):
        raise ValueError(f"need a scoped RESIDUAL universe, a family of {DEV_FAMILIES} and exactly those declared")
    n_lib = _count(n_lib, "n_lib", 1)
    if n_lib != _word(cap, "sizes['DEV_LIB']"):
        raise ValueError(f"science.dev.n_lib = {n_lib} differs from sizes['DEV_LIB'] = {cap!r}")
    rows = []
    for index in range(n_lib):
        key = ("devlib", campaign, *setup, family, index)
        out = direction_information(desc, frame, fit, setup, "RESIDUAL", key)
        q = _real_array(out["q"], "q", 1) if out["status"] == "SUPPORTED" else None
        if q is None or q.shape != (20,) or (q < 0).any():
            raise ValueError(f"DEV_LIB row {index} of {family} needs a SUPPORTED finite nonnegative q of shape (20,)")
        rows.append(q)
    return {"q": np.array(rows, dtype=np.float64)}


def _library_q(arrays, n_lib, key, error):
    q = arrays.get("q") if isinstance(arrays, dict) and set(arrays) == {"q"} else None
    if not (isinstance(q, np.ndarray) and q.dtype == np.float64 and q.shape == (n_lib, 20)
            and np.isfinite(q).all() and (q >= 0).all()):
        raise error(f"DEV_LIB partition {key} needs exactly a finite nonnegative float64 q of shape ({n_lib}, 20)")
    return q


def _setup_provenance(did, apps, meta, setup, frame, fit):
    basis = pdb.array_sha256(frame["V"], frame["lam"], frame["mean"])
    fit_hash = None if setup[0] == "EXACT" else pdb.array_sha256(fit["V"], fit["lam"], fit["mean"])
    try:
        claimed = [meta["design_id"], meta["setup"], meta["basis_sha"], meta["fit_hash"]]
        claimed.append(sorted(meta["applications"]))
        ids = {app: meta["applications"][app]["setup_id"] for app in apps}
    except (KeyError, TypeError) as exc:
        raise PartitionMismatch(f"the committed SETUP metadata of {setup} is malformed") from exc
    same = pdb.canon(claimed) == pdb.canon([did, setup, basis, fit_hash, sorted(apps)])
    for app in apps:
        lo, hi = UNIVERSES[app]
        identity = {"design_id": did, "arm": setup[0], "N": setup[1], "fit_id": setup[2], "application": app,
                    "universe_pcs": list(range(lo, hi + 1)), "basis_sha": basis, "fit_hash": fit_hash}
        same = same and ids[app] == pdb.sha16(identity)
    if not same:
        raise PartitionMismatch(f"the SETUP provenance or setup ids of {setup} disagree with its cached frame and fit")
    return ids


def dev_library_cache(cfg, mode, context):
    """Verified DEV_LIB family batches of each scoped residual setup and their pooled qbar handoff; never DEV.json."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    keys = sorted(([*key] for key in seed_plan(cfg, mode)["keys"] if key[0] in ("frame", "fit")), key=pdb.canon)
    if pdb.canon(plan["SETUP"]) != pdb.canon(keys):
        raise ValueError(f"the SETUP plan must schedule exactly the primitive frame and fit keys {keys}")
    setups, campaign, apps = desc["scope"]["setups"], desc["campaign"], desc["scope"]["applications"]
    for setup in setups:
        _setup_parameters(desc, setup)
    residual, dev, scoped = "RESIDUAL" in apps, desc["science"]["dev"], {pdb.canon(s): s for s in setups}
    n_lib = _count(dev["n_lib"], "n_lib", 1) if residual else 0
    if residual and (n_lib != _word(desc["sizes"]["DEV_LIB"], "sizes['DEV_LIB']")
                     or sorted(dev["families"]) != sorted(DEV_FAMILIES)):
        raise ValueError(f"DEV_LIB needs n_lib equal to sizes['DEV_LIB'] and exactly the families {DEV_FAMILIES}")
    logical = sorted((["DEV_LIB", campaign, *s, f] for s in setups for f in DEV_FAMILIES if residual), key=pdb.canon)
    if pdb.canon([key for key in plan["DEV"] if key[0] == "DEV_LIB"]) != pdb.canon(logical):
        raise ValueError(f"the DEV plan must schedule exactly the DEV_LIB family batches {logical}")

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def frame_fit(setup):
        frame = caches[pdb.canon(["frame", campaign, setup[1]])]
        return frame, frame if setup[0] == "EXACT" else caches[pdb.canon(["fit", campaign, *setup])]

    def library(key):
        setup = scoped[pdb.canon(key[2:5])]
        block = dev_library_block(desc, *frame_fit(setup), setup, key[5])
        return {"q": _library_q(block, n_lib, key, ValueError)}

    caches, libraries, ids = {}, {}, {}
    try:
        records, missing = _planned_progress(staging, did, desc, plan, None)
        if "SETUP" not in records:
            raise PhaseOrderError(f"DEV_LIB needs the complete verified SETUP record of design {did}")
        derived = records["SETUP"]["derived"] if isinstance(records["SETUP"]["derived"], dict) else {}
        members = derived["setups"] if set(derived) == {"setups"} else None
        if not isinstance(members, dict) or sorted(members) != sorted(scoped):
            raise PartitionMismatch(f"the committed SETUP record does not hold exactly the scoped setups {setups}")
        for key in keys:
            arrays = _verify_partition(staging, did, {}, key)[2]
            try:
                caches[pdb.canon(key)] = _setup_cache(arrays, key)
            except ValueError as exc:
                raise PartitionMismatch(f"the cached SETUP partition {key} is not a valid planned record") from exc
        for name, setup in scoped.items():
            ids[name] = _setup_provenance(did, apps, members[name], setup, *frame_fit(setup))
        upstream = {"SETUP": records["SETUP"]["phase_digest"]}
        absent = {pdb.canon(entry["key"]) for entry in missing if entry["phase"] == "DEV"}
        for key in logical:
            if pdb.canon(key) not in absent:
                arrays = _verify_partition(staging, did, upstream, key)[2]
                libraries[pdb.canon(key)] = _library_q(arrays, n_lib, key, PartitionMismatch)
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    for key in logical:
        if pdb.canon(key) not in libraries:
            arrays = guarded_partition(context, "DEV", upstream, key, lambda key=key: library(key))
            libraries[pdb.canon(key)] = _library_q(arrays, n_lib, key, PartitionMismatch)
    handoff = {}
    try:
        for name, setup in (scoped.items() if residual else ()):
            batch = [key for key in logical if pdb.canon(key[2:5]) == name]
            qbar = dev_qbar(desc, {key[5]: libraries[pdb.canon(key)] for key in batch})
            rows, setup_id = _partition_rows(staging, did, upstream, batch), ids[name]["RESIDUAL"]
            pairs = [[pdb.canon(row["key"]), row["sha256"]] for row in rows]
            handoff[name] = {"setup_id": setup_id, "partitions": rows, "qbar": qbar.tolist(),
                             "qbar_sha": pdb.array_sha256(qbar),
                             "dev_library_id": pdb.sha16({"setup_id": setup_id, "partitions": pairs})}
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    return handoff


def _dev_grid(values, high):
    return (isinstance(values, list) and len(values) > 0 and all(type(v) is int and 1 <= v <= high for v in values)
            and len(set(values)) == len(values))


def _dev_candidate(Y_null, alts, bundle, alpha, H):
    h, r, alarms = pdb.rank_threshold(nonoracle_scan(Y_null, bundle)["W"].max(axis=1), alpha, "GE")
    rmst = {}
    for family, Y in alts.items():
        first = nonoracle_scan(Y, bundle, h)["first"]
        rmst[family] = float(np.where(first < 0, H, np.minimum(first, H)).mean())
    return {"h": float(h), "r": int(r), "alarms": int(alarms), "rmst_by_family": rmst}


def dev_choices(desc, Y_null, Y_alt_by_family, *, primary=False):
    """d_dev (and s2_dev if primary) minimizing equal-weight DEV RMST_H at the common nominal alpha (plan section 7)."""
    if type(primary) is not bool:
        raise ValueError(f"primary must be a bool, got {primary!r}")
    s2 = common_prior(desc)
    try:
        params, sizes, dev = desc["science"]["parameters"], desc["sizes"], desc["science"]["dev"]
        H, K, alpha, grid = _count(params["H"], "H", 1), params["K"], params["alpha"], dev["d_grid"]
        n_null, n_alt = _count(sizes["DEV_NULL"], "DEV_NULL", 1), _count(sizes["DEV_ALT"], "DEV_ALT", 1)
        multipliers = dev["s2_grid"] if primary else []
    except (KeyError, TypeError) as exc:
        raise ValueError("desc must declare H, K, alpha, DEV_NULL, DEV_ALT, d_grid and, if primary, s2_grid") from exc
    if not (K == 20 and _dev_grid(grid, K) and (not primary or _dev_grid(multipliers, math.inf))):
        raise ValueError(f"need K = 20, unique integer d_grid in 1..K and unique positive integer s2_grid, got {K!r}, "
                         f"{grid!r}, {multipliers!r}")
    if not (isinstance(Y_alt_by_family, dict) and set(Y_alt_by_family) == set(DEV_FAMILIES)):
        raise ValueError(f"Y_alt_by_family must map exactly the DEV families {DEV_FAMILIES}")
    Y0 = _real_array(Y_null, "Y_null", 3)
    alts = {family: _real_array(Y_alt_by_family[family], family, 3) for family in DEV_FAMILIES}
    if Y0.shape != (n_null, H, 20) or any(Y.shape != (n_alt, H, 20) for Y in alts.values()):
        raise ValueError(f"need Y_null of shape {(n_null, H, 20)} and every DEV family of shape {(n_alt, H, 20)}")
    prefixes = [(d, frozen_policy(desc, "RESIDUAL", "FIXED_DEV_PREFIX", d_dev=d)) for d in sorted(grid)]
    labels = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128", "FULL_K") if primary else ()
    bases = {label: frozen_policy(desc, "RESIDUAL", label) for label in labels}
    d_candidates = []
    for d, bundle in prefixes:
        row = _dev_candidate(Y0, alts, bundle, alpha, H)
        d_candidates.append({"d": d, "s2": s2, **row, "J": math.fsum(row["rmst_by_family"].values()) / len(alts)})
    s2_candidates = []
    for m in sorted(multipliers):
        policies = {label: _dev_candidate(Y0, alts, {**bundle, "s2": m * s2}, alpha, H)
                    for label, bundle in bases.items()}
        values = [v for p in policies.values() for v in p["rmst_by_family"].values()]
        s2_candidates.append({"s2": m * s2, "policies": policies, "J": math.fsum(values) / len(values)})
    s2_dev = min(s2_candidates, key=lambda c: (c["J"], c["s2"]))["s2"] if primary else None
    return {"d_dev": min(d_candidates, key=lambda c: (c["J"], c["d"]))["d"], "s2_dev": s2_dev,
            "qualification": "COMMON_NOMINAL_ALPHA_DEV", "d_candidates": d_candidates, "s2_candidates": s2_candidates}


def _dev_scores(arrays, n, H, key):
    Y = arrays.get("Y") if isinstance(arrays, dict) and set(arrays) == {"Y"} else None
    if not (isinstance(Y, np.ndarray) and Y.dtype == np.float64 and Y.shape == (n, H, 20) and np.isfinite(Y).all()):
        raise PartitionMismatch(f"DEV partition {key} needs exactly a finite float64 Y of shape ({n}, {H}, 20)")
    return Y


def _dev_row(rule_id, status, subset, s2):
    identity = {"policy_rule_id": rule_id, "subset": subset, "prior": DEV_PRIOR, "s2": s2}
    return {"status": status, **identity, "policy_id": pdb.sha16(identity) if status == "RUNNABLE" else None}


def _dev_choice_check(desc, choice, primary):
    prior, H, dev = common_prior(desc), desc["science"]["parameters"]["H"], desc["science"]["dev"]
    rank = pdb.predictive_rank(desc["sizes"]["DEV_NULL"], desc["science"]["parameters"]["alpha"])

    def scored(row, fields):
        rmst = row["rmst_by_family"] if isinstance(row, dict) and set(row) == fields else None
        if not (isinstance(rmst, dict) and set(rmst) == set(DEV_FAMILIES) and type(row["h"]) is float
                and math.isfinite(row["h"]) and type(row["r"]) is int and row["r"] == rank
                and type(row["alarms"]) is int and 0 <= row["alarms"] <= rank
                and all(type(v) is float and 1 <= v <= H for v in rmst.values())):
            raise ValueError(f"a stored DEV candidate row is malformed: {row!r}")
        return list(rmst.values())

    names = {"d_dev", "s2_dev", "qualification", "d_candidates", "s2_candidates"}
    if not (isinstance(choice, dict) and set(choice) == names and choice["qualification"] == "COMMON_NOMINAL_ALPHA_DEV"
            and isinstance(choice["d_candidates"], list) and isinstance(choice["s2_candidates"], list)):
        raise ValueError("the stored DEV choices do not follow the dev_choices schema")
    d_rows, s2_rows = choice["d_candidates"], choice["s2_candidates"]
    for c in d_rows:
        values = scored(c, {"d", "s2", "h", "r", "alarms", "rmst_by_family", "J"})
        if not (type(c["d"]) is int and type(c["s2"]) is float and c["s2"] == prior and type(c["J"]) is float
                and c["J"] == math.fsum(values) / len(values)):
            raise ValueError(f"the stored d candidate {c!r} disagrees with the common prior or its J")
    if not ([c["d"] for c in d_rows] == sorted(dev["d_grid"]) and type(choice["d_dev"]) is int
            and choice["d_dev"] == min(d_rows, key=lambda c: (c["J"], c["d"]))["d"]):
        raise ValueError("the stored d candidates or d_dev disagree with the declared grid and tie rule")
    if not primary:
        if s2_rows or choice["s2_dev"] is not None:
            raise ValueError("a non-primary DEV choice holds an s2_dev selection")
        return
    for c in s2_rows:
        policies = c["policies"] if isinstance(c, dict) and set(c) == {"s2", "policies", "J"} else None
        if not (isinstance(policies, dict) and set(policies) == set(P_CONF)):
            raise ValueError(f"the stored s2 candidate {c!r} does not hold exactly the P_conf policies")
        values = [v for label in P_CONF for v in scored(policies[label], {"h", "r", "alarms", "rmst_by_family"})]
        if not (type(c["s2"]) is float and type(c["J"]) is float and c["J"] == math.fsum(values) / len(values)):
            raise ValueError(f"the stored s2 candidate {c!r} disagrees with its J")
    if not ([c["s2"] for c in s2_rows] == [m * prior for m in sorted(dev["s2_grid"])]
            and type(choice["s2_dev"]) is float
            and choice["s2_dev"] == min(s2_rows, key=lambda c: (c["J"], c["s2"]))["s2"]):
        raise ValueError("the stored s2 candidates or s2_dev disagree with the declared grid and tie rule")


def _dev_derived(desc, staging, did, upstream, scoped, metas, handoff, choices, fixed=None):
    prior, campaign, n_null = common_prior(desc), desc["campaign"], desc["sizes"]["DEV_NULL"]
    main, lo = pdb.canon(desc["science"]["phi"]["setup"]), UNIVERSES["RESIDUAL"][0]

    def primary(name, app, label, meta, qbar, d_dev):
        rule_id = policy_rule(desc, label)["policy_rule_id"]
        if fixed is not None and app == "RESIDUAL" and label == "FIXED_EXANTE_QBAR_MIX":
            subset, hi = fixed[name][label]["subset"], UNIVERSES[app][1]
            if not (type(subset) is list and subset and all(type(k) is int for k in subset)
                    and subset == sorted(set(subset)) and lo <= subset[0] and subset[-1] <= hi):
                raise ValueError(f"the stored FIXED_EXANTE_QBAR_MIX subset {subset!r} is not a canonical PC list")
            return _dev_row(rule_id, "RUNNABLE", subset, prior)
        bundle = frozen_policy(desc, app, label, meta["baselines"], qbar, d_dev)
        mask = (bundle["policy"] or {}).get("mask")
        subset = None if mask is None else [int(k) + UNIVERSES[app][0] for k in np.flatnonzero(mask)]
        return _dev_row(rule_id, bundle["status"], subset, prior)

    def effective(name, label, s2, meta):
        base = primary(name, "RESIDUAL", label, meta, None, None)
        if s2 == prior:
            return base
        return _dev_row(policy_rule(desc, label, s2_sensitivity=True)["policy_rule_id"], "RUNNABLE", base["subset"], s2)

    setups, dev_ids = {}, {}
    for name, setup in scoped.items():
        setups[name] = {}
        for app in desc["scope"]["applications"]:
            meta, choice, library, cal_ids, status = metas[name][app], None, None, [], None
            policies = {"PRIMARY": {}, "GAMMA_M": {}, "S2_DEV": {}}
            if app == "RESIDUAL":
                choice, library = choices[name], handoff[name]
                null_sha = _verify_partition(staging, did, upstream, ["DEV_NULL", campaign, *setup])[0]
                prefix = policy_rule(desc, "FIXED_DEV_PREFIX")["policy_rule_id"]
                cands = [(_dev_row(prefix, "RUNNABLE", list(range(lo, lo + c["d"])), prior)["policy_id"], c)
                         for c in choice["d_candidates"]]
                cands += [(effective(name, label, c["s2"], meta)["policy_id"], p)
                          for c in choice["s2_candidates"] for label, p in c["policies"].items()]
                cal_ids = sorted(pdb.sha16({"setup_id": meta["setup_id"], "dev_null_sha": null_sha, "policy_id": pid,
                                            "rule": "GE", "n": n_null, "h": c["h"], "r": c["r"], "alarms": c["alarms"]})
                                 for pid, c in cands)
                if name == main:
                    status = "S2_DEV_EQUALS_COMMON" if choice["s2_dev"] == prior else "S2_DEV_DISTINCT"
                    policies["GAMMA_M"] = {label: _dev_row(policy_rule(desc, label, gamma_sensitivity=True)["policy_rule_id"],
                                                         "RUNNABLE", None, prior) for label in P_CONF[:2]}
                    policies["S2_DEV"] = {label: effective(name, label, choice["s2_dev"], meta) for label in P_CONF}
            qbar = None if library is None else library["qbar"]
            d_dev = None if choice is None else choice["d_dev"]
            policies["PRIMARY"] = {label: primary(name, app, label, meta, qbar, d_dev)
                                   for label in desc["scope"]["policies"]}
            identity = {"setup_id": meta["setup_id"], "dev_library_id": None if library is None else library["dev_library_id"],
                        "qbar_sha": None if library is None else library["qbar_sha"], "d_dev": d_dev,
                        "s2_dev": None if choice is None else choice["s2_dev"], "dev_calibration_ids": cal_ids}
            setups[name][app] = {"applicability": "NOT_APPLICABLE" if library is None else "SELECTED",
                                 "setup_id": meta["setup_id"], "library": library, "choices": choice,
                                 "s2_status": status, "dev_calibration_ids": cal_ids, "policies": policies,
                                 "dev_id": pdb.sha16(identity)}
            dev_ids[pdb.canon([*setup, app])] = setups[name][app]["dev_id"]
    return {"setups": setups, "dev_ids": dev_ids}


def _dev_reload(desc, staging, did, setup_record, logical, scoped, metas, n, H):
    record = _load_phase(staging, desc, did, "DEV", {"SETUP": setup_record})
    upstream, n_lib = record["upstream"], desc["sizes"]["DEV_LIB"]
    main = pdb.canon(desc["science"]["phi"]["setup"])
    if [pdb.canon(row["key"]) for row in record["partitions"]] != [pdb.canon(key) for key in logical]:
        raise PartitionMismatch(f"the committed DEV partitions of design {did} differ from its planned keys")
    handoff, choices, fixed = {}, {}, {}
    try:
        for key in logical:
            arrays = _verify_partition(staging, did, upstream, key)[2]
            if key[0] == "DEV_LIB":
                _library_q(arrays, n_lib, key, PartitionMismatch)
            else:
                _dev_scores(arrays, n[key[0]], H, key)
        for name in (scoped if "RESIDUAL" in desc["scope"]["applications"] else ()):
            stored = record["derived"]["setups"][name]["RESIDUAL"]
            _dev_choice_check(desc, stored["choices"], name == main)
            listed = stored["library"]["qbar"]
            qbar = _real_array(listed, "qbar", 1)
            if not (isinstance(listed, list) and all(type(v) is float for v in listed) and qbar.shape == (20,)
                    and (qbar >= 0).all()):
                raise ValueError(f"the stored qbar of {name} is not a finite nonnegative float list of length 20")
            batch = [key for key in logical if key[0] == "DEV_LIB" and pdb.canon(key[2:5]) == name]
            rows, setup_id = _partition_rows(staging, did, upstream, batch), metas[name]["RESIDUAL"]["setup_id"]
            pairs = [[pdb.canon(row["key"]), row["sha256"]] for row in rows]
            handoff[name] = {"setup_id": setup_id, "partitions": rows, "qbar": listed, "qbar_sha": pdb.array_sha256(qbar),
                             "dev_library_id": pdb.sha16({"setup_id": setup_id, "partitions": pairs})}
            choices[name], fixed[name] = stored["choices"], stored["policies"]["PRIMARY"]
        rebuilt = _dev_derived(desc, staging, did, upstream, scoped, metas, handoff, choices, fixed)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        raise PartitionMismatch(f"the committed DEV record of design {did} is not a valid derived projection") from exc
    if pdb.canon(rebuilt) != pdb.canon(record["derived"]):
        raise PartitionMismatch(f"the committed DEV identities of design {did} disagree with its stored fields")
    return record


def dev_phase(cfg, mode, context):
    """Verified DEV phase record: DEV_LIB/NULL/ALT batches, dev choices and frozen identities, or its verified reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    keys = sorted(([*key] for key in seed_plan(cfg, mode)["keys"] if key[0] in ("frame", "fit")), key=pdb.canon)
    if pdb.canon(plan["SETUP"]) != pdb.canon(keys):
        raise ValueError(f"the SETUP plan must schedule exactly the primitive frame and fit keys {keys}")
    setups, campaign, apps = desc["scope"]["setups"], desc["campaign"], desc["scope"]["applications"]
    for setup in setups:
        _setup_parameters(desc, setup)
    residual, scoped, H = "RESIDUAL" in apps, {pdb.canon(s): s for s in setups}, desc["science"]["parameters"]["H"]
    tails = [("DEV_NULL", [])] + [(role, [f]) for role in ("DEV_LIB", "DEV_ALT") for f in DEV_FAMILIES]
    logical = sorted(([role, campaign, *s, *tail] for s in setups for role, tail in tails if residual), key=pdb.canon)
    if pdb.canon(plan["DEV"]) != pdb.canon(logical):
        raise ValueError(f"the DEV plan must schedule exactly the DEV_LIB, DEV_NULL and DEV_ALT batches {logical}")
    n = {"DEV_NULL": desc["sizes"]["DEV_NULL"], "DEV_ALT": desc["sizes"]["DEV_ALT"]}

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def frame_fit(setup):
        frame = caches[pdb.canon(["frame", campaign, setup[1]])]
        return frame, frame if setup[0] == "EXACT" else caches[pdb.canon(["fit", campaign, *setup])]

    def batch(key):
        setup = scoped[pdb.canon(key[2:5])]
        frame, fit = frame_fit(setup)
        rows = []
        for i in range(n[key[0]]):
            delta = None
            if key[0] == "DEV_ALT":
                meta = ("meta", campaign, *setup, "DEV_ALT", key[5], i)
                info = direction_information(desc, frame, fit, setup, "RESIDUAL", meta)
                if info["status"] != "SUPPORTED":
                    raise ValueError(f"DEV_ALT draw {meta} needs a SUPPORTED drift, got {info['status']!r}")
                delta = info["delta"]
            rows.append((("path", campaign, *setup, key[0], i), delta))
        Y = _score_requests(desc, frame, fit, "RESIDUAL", rows, context)
        if not (Y.dtype == np.float64 and Y.shape == (n[key[0]], H, 20) and np.isfinite(Y).all()):
            raise ValueError(f"the produced DEV batch {key} is not a finite float64 Y of shape ({n[key[0]]}, {H}, 20)")
        return {"Y": Y}

    caches, scores, committed = {}, {}, None
    try:
        setup_record = _load_phase(staging, desc, did, "SETUP", {})
        if [pdb.canon(row["key"]) for row in setup_record["partitions"]] != [pdb.canon(key) for key in keys]:
            raise PartitionMismatch(f"the committed SETUP partitions of design {did} differ from its planned keys")
        derived = setup_record["derived"] if isinstance(setup_record["derived"], dict) else {}
        members = derived["setups"] if set(derived) == {"setups"} else None
        if not isinstance(members, dict) or sorted(members) != sorted(scoped):
            raise PartitionMismatch(f"the committed SETUP record does not hold exactly the scoped setups {setups}")
        for key in keys:
            try:
                caches[pdb.canon(key)] = _setup_cache(_verify_partition(staging, did, {}, key)[2], key)
            except ValueError as exc:
                raise PartitionMismatch(f"the cached SETUP partition {key} is not a valid planned record") from exc
        for name, setup in scoped.items():
            _setup_provenance(did, apps, members[name], setup, *frame_fit(setup))
        metas = {name: members[name]["applications"] for name in scoped}
        upstream = {"SETUP": setup_record["phase_digest"]}
        later = [p for p in (*PHASES[2:], "FINAL") if os.path.lexists(staging / "phases" / f"{p}.json")]
        if os.path.lexists(staging / "phases" / "DEV.json"):
            committed = _dev_reload(desc, staging, did, setup_record, logical, scoped, metas, n, H)
        elif later:
            raise PhaseOrderError(f"DEV of design {did} has no record while the later records {later} exist")
        else:
            for key in logical:
                stem = _partition_path(staging, did, upstream, key)
                if key[0] != "DEV_LIB" and os.path.lexists(stem.with_suffix(".json")):
                    arrays = _verify_partition(staging, did, upstream, key)[2]
                    scores[pdb.canon(key)] = _dev_scores(arrays, n[key[0]], H, key)
    finally:
        checkpoint()
    if committed is not None:
        future = [{"phase": p, "key": key} for p in PHASES[2:] for key in plan[p]]
        require_budget(staging, context["authority"], plan, context["started"], ("DEV", future))
        return committed
    require_budget(staging, context["authority"], plan, context["started"])
    handoff = dev_library_cache(cfg, mode, context) if residual else {}
    for key in logical:
        if key[0] != "DEV_LIB" and pdb.canon(key) not in scores:
            arrays = guarded_partition(context, "DEV", upstream, key, lambda key=key: batch(key))
            scores[pdb.canon(key)] = _dev_scores(arrays, n[key[0]], H, key)
    choices = {}
    try:
        for name, setup in (scoped.items() if residual else ()):
            alts = {f: scores[pdb.canon(["DEV_ALT", campaign, *setup, f])] for f in DEV_FAMILIES}
            choices[name] = dev_choices(desc, scores[pdb.canon(["DEV_NULL", campaign, *setup])], alts,
                                        primary=name == pdb.canon(desc["science"]["phi"]["setup"]))
        derived = _dev_derived(desc, staging, did, upstream, scoped, metas, handoff, choices)
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    return phase_record(staging, "DEV", upstream, logical, derived)


def _calibrate_ge(W, alpha):
    maxima = W.max(axis=1)
    h, r, alarms = pdb.rank_threshold(maxima, alpha, "GE")
    return {"h": h, "r": r, "alarms": alarms, "n": int(maxima.shape[0]), "maxima": maxima}


def calibrate_nonoracle(Y, bundle, alpha):
    """Return the GE rank calibration at level alpha of the non-oracle scan maxima of Y under bundle."""
    return _calibrate_ge(nonoracle_scan(Y, bundle)["W"], alpha)


def calibrate_oracle(Y, q_true, bundle, alpha):
    """Return the non-deployable GE rank calibration at level alpha of the oracle scan maxima of Y given q_true under bundle."""
    out = _calibrate_ge(oracle_scan(Y, q_true, bundle)["W"], alpha)
    out["label"] = "NON_DEPLOYABLE_ORACLE_CALIBRATION"
    return out


CAL_RULE = "predictive_exchangeable_rank_v2"
CAL_ORACLE = "NON_DEPLOYABLE_ORACLE_CALIBRATION"


def _cal_cells(desc, app, dev):
    params, prior = desc["science"]["parameters"], common_prior(desc)
    (lo, hi), K, H = UNIVERSES[app], params["K"], params["H"]
    families = [f for f in desc["scope"]["families"] if DRIFT_FAMILIES.get(f, (None,))[0] == app]
    policies, status = dev["policies"], dev["s2_status"]
    fields = {"status", "policy_rule_id", "subset", "prior", "s2", "policy_id"}
    if not (set(policies) == {"PRIMARY", "GAMMA_M", "S2_DEV"} and (status is None) == (not policies["S2_DEV"])
            and status in (None, "S2_DEV_EQUALS_COMMON", "S2_DEV_DISTINCT")):
        raise ValueError(f"the DEV policies of {app} do not follow the PRIMARY, GAMMA_M and S2_DEV schema")
    cells, seen = [], set()
    for variant in ("PRIMARY", "GAMMA_M", "S2_DEV"):
        for label, row in policies[variant].items():
            distinct = variant == "S2_DEV" and status == "S2_DEV_DISTINCT"
            rule = policy_rule(desc, label, gamma_sensitivity=variant == "GAMMA_M", s2_sensitivity=distinct)
            recipe, subset, s2, runnable = rule["recipe"], row["subset"], row["s2"], row["status"] == "RUNNABLE"
            identity = {"policy_rule_id": rule["policy_rule_id"], "subset": subset, "prior": DEV_PRIOR, "s2": s2}
            if not (set(row) == fields and row["policy_rule_id"] == rule["policy_rule_id"] and type(s2) is float
                    and math.isfinite(s2) and s2 > 0 and (s2 != prior) == distinct
                    and row["policy_id"] == (pdb.sha16(identity) if runnable else None)
                    and (runnable or (variant == "PRIMARY" and subset is None
                                      and row["status"] in ("OUTSIDE_UNIVERSE", "UNSUPPORTED", "NOT_RUN")))):
                raise ValueError(f"the DEV {variant} row of {label!r} in {app} disagrees with its frozen rule")
            if not runnable or row["policy_id"] in seen:
                continue
            seen.add(row["policy_id"])
            if recipe["kind"] == "STATIC":
                if not (type(subset) is list and subset and all(type(k) is int for k in subset)
                        and subset == sorted(set(subset)) and lo <= subset[0] and subset[-1] <= hi):
                    raise ValueError(f"the stored subset {subset!r} of {label!r} is not a PC list of {app}")
                mask = np.zeros(K, dtype=bool)
                mask[np.array(subset) - lo] = True
                policy = {"kind": "STATIC", "mask": mask}
            elif subset is None:
                cost = cost_vectors(recipe["gamma_M"], K)["MIX" if recipe["cost"] == "MIX" else "AFF"]
                head = {"window": recipe["window"]} if recipe["kind"] == "ONLINE" else {"H": H}
                policy = {"kind": recipe["kind"], **head, "cost": cost, "order": recipe["order"]}
            else:
                raise ValueError(f"the adaptive policy {label!r} of {app} stores a subset {subset!r}")
            bundle = {"label": label, "application": app, "status": "RUNNABLE", "s2": s2, "policy": policy}
            for family in (families if policy["kind"] == "ORACLE" else [None]):
                cells.append(("w_" + pdb.sha16([row["policy_id"], family]), row["policy_id"], family, bundle))
    return cells


def _cal_present(cells, arrays, n, key):
    names = set(arrays)
    if cells:
        good = names == {c[0] for c in cells} and all(arrays[c[0]].dtype == np.float64 and arrays[c[0]].shape == (n,)
                                                      and np.isfinite(arrays[c[0]]).all() for c in cells)
    else:
        index = arrays.get("index")
        good = (names == {"index"} and index.dtype.kind in "iu" and index.shape == (n,)
                and np.array_equal(index, np.arange(n)))
    if not good:
        raise PartitionMismatch(f"CAL partition {key} does not hold exactly the finite ({n},) maxima of its cells")
    return cells


def _cal_row(setup_id, cell, m, n, alpha, h, r, alarms):
    family = cell[2]
    tag = {} if family is None else {"family": family}
    base = {"setup_id": setup_id, "policy_id": cell[1], "n_cal": n, "maxima_sha256": pdb.array_sha256(m), **tag}
    h = float(h) if isinstance(h, float) else h
    b = np.nextafter(h, -np.inf) if type(h) is float and math.isfinite(h) else math.nan
    if not (type(r) is int and type(alarms) is int and r == pdb.predictive_rank(n, alpha) >= 0 and m.shape == (n,)
            and np.nextafter(b, np.inf) == h and (m == b).any()
            and int((m >= h).sum()) == alarms <= r < int((m >= b).sum())):
        raise ValueError(f"the CAL threshold of {cell[1]} {family} is not the GE rank threshold of its maxima")
    row = {**base, "h": h, "r": r, "alarms": alarms, **({} if family is None else {"qualification": CAL_ORACLE})}
    return pdb.sha16({**base, "rule": "GE"}), row


def _cal_table(cells, loaded, ids, ns, alpha, source):
    rows = {}
    for k, arrays in loaded.items():
        n = ns[k]
        for cell in _cal_present(cells[k], arrays, n, k):
            m = arrays[cell[0]]
            cid, row = _cal_row(ids[k], cell, m, n, alpha, *source(k, cell, m))
            if cid in rows:
                raise ValueError(f"the CAL calibration id {cid} repeats")
            rows[cid] = row
    return {"rule": CAL_RULE, "thresholds": rows}


def export_calibration(out_dir, did, record):
    """Write calibration.csv from an already verified CAL record of design did and return its SHA-256."""
    import os
    import pandas
    if not _is_sha(did):
        raise ValueError("the requested design id is not a SHA-256")
    if not (isinstance(record, dict) and record.get("design_id") == did and record.get("phase") == "CAL"):
        raise ValueError(f"the record is not the CAL record of design {did}")
    derived = record.get("derived")
    if not (isinstance(derived, dict) and set(derived) == {"rule", "thresholds"} and derived["rule"] == CAL_RULE
            and isinstance(derived["thresholds"], dict)):
        raise ValueError("the CAL record does not derive exactly the GE rank rule and its thresholds")
    if not os.path.isdir(out_dir):
        raise ValueError(f"the destination {out_dir} is not an existing directory")
    thresholds = derived["thresholds"]
    if not all(isinstance(cid, str) for cid in thresholds):
        raise ValueError("a CAL calibration id is not a string")
    keys = ("setup_id", "policy_id", "n_cal", "maxima_sha256", "h", "r", "alarms")
    header = ["design_id", "calibration_id", "setup_id", "policy_id", "family", "qualification", "rule",
              "n_cal", "maxima_sha256", "h", "r", "alarms"]
    rows = []
    for cid in sorted(thresholds):
        row = thresholds[cid]
        oracle = isinstance(row, dict) and "family" in row
        extra = {"family", "qualification"} if oracle else set()
        if not (isinstance(row, dict) and set(row) == set(keys) | extra and _is_sha(row["maxima_sha256"])
                and (not oracle or (row["family"] is not None and row["qualification"] == CAL_ORACLE))):
            raise ValueError(f"the CAL calibration row {cid} does not have the CAL row fields")
        tag = {"family": row["family"]} if oracle else {}
        base = {**{k: row[k] for k in keys[:4]}, **tag}
        if pdb.sha16({**base, "rule": "GE"}) != cid:
            raise ValueError(f"the CAL calibration id {cid} does not identify its row")
        rows.append({"design_id": did, "calibration_id": cid, "setup_id": row["setup_id"],
                     "policy_id": row["policy_id"], "family": row["family"] if oracle else None,
                     "qualification": row["qualification"] if oracle else None, "rule": derived["rule"],
                     "n_cal": row["n_cal"], "maxima_sha256": row["maxima_sha256"], "h": row["h"],
                     "r": row["r"], "alarms": row["alarms"]})
    path = os.path.join(out_dir, "calibration.csv")
    pipelines.save_fair_csv(pandas.DataFrame(rows, columns=header), path)
    return pdb.file_sha256(path)


def cal_phase(cfg, mode, context):
    """Verified CAL record: GE rank thresholds of CAL_NULL maxima per frozen policy and oracle family, or its reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    setups, campaign = desc["scope"]["setups"], desc["campaign"]
    keys = _cal_keys(desc)
    if pdb.canon(plan["CAL"]) != pdb.canon(keys):
        raise ValueError(f"the CAL plan must schedule exactly the CAL_NULL keys {keys}")
    ns = {pdb.canon(key): (desc["sizes"]["CAL_NULL"] if "allocation" not in desc
                          else _expected_rows(desc, "CAL", key, {})) for key in keys}
    params, phases = desc["science"]["parameters"], staging / "phases"
    alpha, H, scoped = params["alpha"], params["H"], {pdb.canon(s): s for s in setups}
    cells, ids, loaded, issued, inputs, stored, committed = {}, {}, {}, {}, {}, {}, None

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def recorded(k, cell, m):
        row = stored[(ids[k], cell[1], cell[2], pdb.array_sha256(m))]
        return row["h"], row["r"], row["alarms"]

    def setup_inputs(setup):
        if pdb.canon(setup) not in inputs:
            frame_key, fit_key = ["frame", campaign, setup[1]], ["fit", campaign, *setup]
            try:
                frame = _setup_cache(_verify_partition(staging, did, {}, frame_key)[2], frame_key)
                fit = frame if setup[0] == "EXACT" else _setup_cache(
                    _verify_partition(staging, did, {}, fit_key)[2], fit_key)
            except ValueError as exc:
                raise PartitionMismatch(f"the cached SETUP frame or fit of {setup} is not a valid planned record") from exc
            inputs[pdb.canon(setup)] = frame, fit
        return inputs[pdb.canon(setup)]

    def produce(key):
        k, setup, app = pdb.canon(key), scoped[pdb.canon(key[2:5])], key[5]
        n = ns[k]
        if not cells[k]:
            return {"index": np.arange(n)}
        frame, fit = setup_inputs(setup)
        Y = _score_requests(desc, frame, fit, app,
                            [(("path", campaign, *setup, "CAL_NULL", i), None) for i in range(n)], context)
        if not (Y.dtype == np.float64 and Y.shape == (n, H, 20) and np.isfinite(Y).all()):
            raise ValueError(f"the CAL_NULL scores of {key} are not a finite float64 Y of shape ({n}, {H}, 20)")
        q, out = {}, {}
        for name, pid, family, bundle in cells[k]:
            if family is not None and family not in q:
                draws = [("meta", campaign, *setup, "CAL_NULL", family, i) for i in range(n)]
                infos = [direction_information(desc, frame, fit, setup, app, draw) for draw in draws]
                if {info["status"] for info in infos} != {"SUPPORTED"}:
                    raise ValueError(f"the oracle family {family} of {key} is not SUPPORTED for every row")
                q[family] = _real_array([info["q"] for info in infos], f"the true q of {family} in {key}", 2)
                if not (q[family].shape == (n, 20) and np.isfinite(q[family]).all() and (q[family] >= 0).all()):
                    raise ValueError(f"the true q of {family} in {key} is not a finite nonnegative ({n}, 20) batch")
            if family is None:
                result = calibrate_nonoracle(Y, bundle, alpha)
            else:
                result = calibrate_oracle(Y, q[family], bundle, alpha)
            m = result["maxima"]
            if not (isinstance(m, np.ndarray) and m.dtype == np.float64 and m.shape == (n,) and np.isfinite(m).all()
                    and result["n"] == n and (family is None or result.get("label") == CAL_ORACLE)):
                raise ValueError(f"the issued calibration of {pid} {family} in {key} is not finite ({n},) maxima")
            out[name], issued[(k, name)] = m, (result["h"], result["r"], result["alarms"])
        return out or {"index": np.arange(n)}

    try:
        setup_record = _load_phase(staging, desc, did, "SETUP", {})
        if not os.path.lexists(phases / "DEV.json"):
            raise PhaseOrderError(f"CAL of design {did} has no committed DEV predecessor")
        dev_record = dev_phase(cfg, mode, context)
        upstream = {"SETUP": setup_record["phase_digest"], "DEV": dev_record["phase_digest"]}
        try:
            for key in keys:
                name, k, app = pdb.canon(key[2:5]), pdb.canon(key), key[5]
                meta = setup_record["derived"]["setups"][name]["applications"][app]
                dev = dev_record["derived"]["setups"][name][app]
                if dev["setup_id"] != meta["setup_id"]:
                    raise ValueError(f"the DEV row of {key} names another setup_id than its SETUP metadata")
                ids[k], group = meta["setup_id"], _cal_cells(desc, app, dev)
                if len(key) == 7:
                    conf_ids = {dev["policies"]["PRIMARY"][label]["policy_id"] for label in P_CONF}
                    if len(conf_ids) != len(P_CONF) or None in conf_ids:
                        raise ValueError("primary CAL needs distinct RUNNABLE P_CONF identities")
                    group = [cell for cell in group if (cell[2] is None and cell[1] in conf_ids) == (key[6] == "P_CONF")]
                cells[k] = group
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
            raise PartitionMismatch(f"the committed SETUP and DEV records of {did} do not define its CAL cells") from exc
        min_rows = min((ns[k] for k, group in cells.items() if group), default=math.inf)
        if min_rows < pdb.min_calibration_n(alpha):
            raise pdb.InsufficientCalibration(f"CAL holds {min_rows} admissible rows, below the sealed minimum "
                                              f"{pdb.min_calibration_n(alpha)} at alpha {alpha}")
        if os.path.lexists(phases / "CAL.json"):
            record = _load_phase(staging, desc, did, "CAL", {"SETUP": setup_record, "DEV": dev_record})
            if [pdb.canon(row["key"]) for row in record["partitions"]] != [pdb.canon(key) for key in keys]:
                raise PartitionMismatch(f"the committed CAL partitions of design {did} differ from its planned keys")
            try:
                stored.update({(r["setup_id"], r["policy_id"], r.get("family"), r["maxima_sha256"]): r
                               for r in record["derived"]["thresholds"].values()})
                arrays = {pdb.canon(key): _verify_partition(staging, did, upstream, key)[2] for key in keys}
                rebuilt = _cal_table(cells, arrays, ids, ns, alpha, recorded)
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise PartitionMismatch(f"the committed CAL thresholds of design {did} do not verify") from exc
            if pdb.canon(rebuilt) != pdb.canon(record["derived"]):
                raise PartitionMismatch(f"the committed CAL record of design {did} disagrees with its persisted maxima")
            committed = record
        elif any(os.path.lexists(phases / f"{p}.json") for p in (*PHASES[3:], "FINAL")):
            raise PhaseOrderError(f"CAL of design {did} has no record while a later record exists")
        else:
            for key in keys:
                if os.path.lexists(_partition_path(staging, did, upstream, key).with_suffix(".json")):
                    k = pdb.canon(key)
                    n = ns[k]
                    _, rows, arrays = _verify_partition(staging, did, upstream, key)
                    if rows != n:
                        raise PartitionMismatch(f"cached CAL partition {key} holds {rows} rows instead of {n}")
                    loaded[k] = arrays
                    _cal_present(cells[k], arrays, n, key)
    finally:
        checkpoint()
    if committed is not None:
        future = [{"phase": p, "key": key} for p in PHASES[3:] for key in plan[p]]
        require_budget(staging, context["authority"], plan, context["started"], ("CAL", future))
        return committed
    require_budget(staging, context["authority"], plan, context["started"])
    for key in keys:
        if pdb.canon(key) not in loaded:
            loaded[pdb.canon(key)] = guarded_partition(context, "CAL", upstream, key, lambda key=key: produce(key))
    try:
        derived = _cal_table(cells, loaded, ids, ns, alpha,
                             lambda k, cell, m: issued.get((k, cell[0])) or pdb.rank_threshold(m, alpha, "GE"))
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"])
    return phase_record(staging, "CAL", upstream, keys, derived)


def _null_plan_alarms(arrays, n, key):
    alarm = arrays.get("alarm") if isinstance(arrays, dict) and set(arrays) == {"alarm"} else None
    if not (isinstance(alarm, np.ndarray) and alarm.dtype == np.bool_ and alarm.shape == (n, len(P_CONF))):
        raise PartitionMismatch(f"NULL_PLAN partition {key} does not hold exactly the bool ({n}, {len(P_CONF)}) alarms")
    return alarm


def _null_plan_derived(desc, cal_digest, ids, alarm):
    n, rule, science = alarm.shape[0], desc["null_plan"], desc["science"]
    pairs = {f"{P_CONF[0]}|{P_CONF[j]}": {"b": int((alarm[:, 0] & ~alarm[:, j]).sum()),
                                          "c": int((~alarm[:, 0] & alarm[:, j]).sum())}
             for j in range(1, len(P_CONF))}
    counts = {"n": n, "pairs": pairs, "alarms": {label: int(alarm[:, j].sum()) for j, label in enumerate(P_CONF)}}
    n_hold, status, details = plan_holdout(counts, science["parameters"]["alpha"], science["phi"]["m"], 0.01,
                                           science["null_status"]["eps_v"], rule["beta"], rule["eta"], rule["n_min"],
                                           rule["n_cap"])
    content = {"cal_digest": cal_digest, "calibration_ids": ids, "counts": counts, "details": details,
               "status": status, "n_hold": n_hold}
    return {"status": status, "n_hold": n_hold, "plan_id": hashlib.sha256(pdb.canon(content).encode()).hexdigest()}


def null_plan_phase(cfg, mode, context):
    """Verified NULL_PLAN record: primary P_CONF null alarms at frozen CAL thresholds and the received plan, or its reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    applies, primary, campaign = _plan_applies(desc), desc["science"]["phi"]["setup"], desc["campaign"]
    keys, n = ([["NULL_PLAN", *primary]], desc["null_plan"]["n_plan"]) if applies else ([], 0)
    if pdb.canon(plan["NULL_PLAN"]) != pdb.canon(keys):
        raise ValueError(f"the NULL_PLAN plan must schedule exactly the keys {keys}")
    if applies and not (type(n) is int and n > 0 and "RESIDUAL" in desc["scope"]["applications"]
                        and all(_expected_rows(desc, "NULL_PLAN", key, {}) == n for key in keys)):
        raise ValueError("an applicable NULL_PLAN needs a positive n_plan and the scoped RESIDUAL primary setup")
    H, phases = desc["science"]["parameters"]["H"], staging / "phases"
    later = [{"phase": p, "key": key} for p in PHASES[4:] for key in plan[p]]
    bundles, ids, hs, alarm, committed = {}, {}, {}, None, None

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def produce():
        frame_key, fit_key = ["frame", campaign, primary[1]], ["fit", campaign, *primary]
        try:
            frame = _setup_cache(_verify_partition(staging, did, {}, frame_key)[2], frame_key)
            fit = frame if primary[0] == "EXACT" else _setup_cache(
                _verify_partition(staging, did, {}, fit_key)[2], fit_key)
        except ValueError as exc:
            raise PartitionMismatch(f"the cached SETUP frame or fit of {primary} is not a valid planned record") from exc
        Y = _score_requests(desc, frame, fit, "RESIDUAL",
                            [(("path", campaign, *primary, "NULL_PLAN", i), None) for i in range(n)], context)
        if not (Y.dtype == np.float64 and Y.shape == (n, H, 20) and np.isfinite(Y).all()):
            raise ValueError(f"the NULL_PLAN scores of {primary} are not a finite float64 Y of shape ({n}, {H}, 20)")
        out = np.zeros((n, len(P_CONF)), dtype=bool)
        for j, label in enumerate(P_CONF):
            first = nonoracle_scan(Y, bundles[label], hs[label])["first"]
            if not (isinstance(first, np.ndarray) and first.shape == (n,)):
                raise ValueError(f"the NULL_PLAN scan of {label} does not give ({n},) first alarm times")
            out[:, j] = first > 0
        return {"alarm": out}

    try:
        if not os.path.lexists(phases / "CAL.json"):
            raise PhaseOrderError(f"NULL_PLAN of design {did} has no committed CAL predecessor")
        cal = cal_phase(cfg, mode, context)
        records = _lineage(staging, desc, did, "NULL_PLAN")
        if pdb.canon(records["CAL"]) != pdb.canon(cal):
            raise PartitionMismatch(f"the verified CAL record of design {did} differs from its committed lineage")
        upstream = {p: r["phase_digest"] for p, r in records.items()}
        if applies:
            try:
                name = pdb.canon(primary)
                meta = records["SETUP"]["derived"]["setups"][name]["applications"]["RESIDUAL"]
                dev = records["DEV"]["derived"]["setups"][name]["RESIDUAL"]
                if dev["setup_id"] != meta["setup_id"]:
                    raise ValueError("the primary DEV row names another setup_id than its SETUP metadata")
                cells, thresholds = _cal_cells(desc, "RESIDUAL", dev), cal["derived"]["thresholds"]
                for label in P_CONF:
                    pid = dev["policies"]["PRIMARY"][label]["policy_id"]
                    if pid is None:
                        raise ValueError(f"the primary P_CONF policy {label} is not RUNNABLE")
                    [bundle] = [c[3] for c in cells if c[1] == pid and c[2] is None]
                    [(cid, row)] = [(c, r) for c, r in thresholds.items()
                                    if (r["setup_id"], r["policy_id"], "family" in r) == (meta["setup_id"], pid, False)]
                    if bundle["label"] != label:
                        raise ValueError(f"the CAL cell of {pid} is not the PRIMARY bundle of {label}")
                    bundles[label], ids[label], hs[label] = bundle, cid, row["h"]
            except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
                raise PartitionMismatch(f"the committed SETUP, DEV and CAL records of {did} do not define the "
                                        f"primary P_CONF calibrations") from exc
        if os.path.lexists(phases / "NULL_PLAN.json"):
            record = _load_phase(staging, desc, did, "NULL_PLAN", records)
            if [pdb.canon(row["key"]) for row in record["partitions"]] != [pdb.canon(key) for key in keys]:
                raise PartitionMismatch(f"the committed NULL_PLAN partitions of design {did} differ from its planned keys")
            rebuilt = {"status": "NOT_APPLICABLE"}
            if applies:
                try:
                    stored = _null_plan_alarms(_verify_partition(staging, did, upstream, keys[0])[2], n, keys[0])
                    rebuilt = _null_plan_derived(desc, cal["phase_digest"], ids, stored)
                except (KeyError, TypeError, ValueError, AttributeError) as exc:
                    raise PartitionMismatch(f"the committed NULL_PLAN alarms of design {did} do not verify") from exc
            if pdb.canon(rebuilt) != pdb.canon(record["derived"]):
                raise PartitionMismatch(f"the committed NULL_PLAN record of design {did} disagrees with its alarms")
            committed = record
        elif any(os.path.lexists(phases / f"{p}.json") for p in (*PHASES[4:], "FINAL")):
            raise PhaseOrderError(f"NULL_PLAN of design {did} has no record while a later record exists")
        elif applies and os.path.lexists(_partition_path(staging, did, upstream, keys[0]).with_suffix(".json")):
            _, rows, arrays = _verify_partition(staging, did, upstream, keys[0])
            if rows != n:
                raise PartitionMismatch(f"cached NULL_PLAN partition {keys[0]} holds {rows} rows instead of {n}")
            alarm = _null_plan_alarms(arrays, n, keys[0])
    finally:
        checkpoint()
    if committed is not None:
        require_budget(staging, context["authority"], plan, context["started"], ("NULL_PLAN", later))
        return committed
    pending = [{"phase": "NULL_PLAN", "key": key} for key in keys if alarm is None]
    require_budget(staging, context["authority"], plan, context["started"], ("CAL", pending + later))
    if applies and alarm is None:
        alarm = _null_plan_alarms(guarded_partition(context, "NULL_PLAN", upstream, keys[0], produce), n, keys[0])
    try:
        derived = _null_plan_derived(desc, cal["phase_digest"], ids, alarm) if applies else {"status": "NOT_APPLICABLE"}
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"], ("CAL", later))
    return phase_record(staging, "NULL_PLAN", upstream, keys, derived)


def _hold_valid(cells, arrays, n, H, K, start=None):
    names = {p + c[0] for c in cells for p in ("first_", "mask_")}
    if start is not None:
        names.add("path_index")
    elif not cells:
        names.add("index")
    if not (isinstance(arrays, dict) and set(arrays) == names
            and all(isinstance(value, np.ndarray) for value in arrays.values())):
        return False
    if start is not None:
        index = arrays["path_index"]
        if not (index.dtype.kind == "i" and np.array_equal(index, np.arange(start, start + n))):
            return False
    elif not cells:
        index = arrays["index"]
        return bool(index.dtype.kind in "iu" and index.shape == (n,) and np.array_equal(index, np.arange(n)))
    for cell in cells:
        first, mask = arrays["first_" + cell[0]], arrays["mask_" + cell[0]]
        if not (first.dtype.kind == "i" and first.shape == (n,) and mask.dtype == np.uint32 and mask.shape == (n, H)
                and ((first == -1) | ((first >= 1) & (first <= H))).all() and (mask > 0).all()
                and (mask < (1 << K)).all()):
            return False
    return True


def _hold_checks(desc, cells, loaded, ns):
    science = desc["science"]
    alpha, eps, tail = science["parameters"]["alpha"], science["null_status"]["eps_v"], science["null_status"]["tail"]
    identities, samples, alarms = {}, {}, {}
    for k in sorted(loaded):
        for cid, sid, pid, family, _, _ in cells[k]:
            identities[cid] = (sid, pid, family)
            samples[cid] = samples.get(cid, 0) + ns[k]
            alarms[cid] = alarms.get(cid, 0) + loaded[k][cid]
    rows = {}
    for cid, (sid, pid, family) in identities.items():
        n, k = samples[cid], alarms[cid]
        lo, hi = cp_bounds(k, n, tail)
        tag = {} if family is None else {"family": family, "qualification": "NON_DEPLOYABLE"}
        rows[cid] = {"setup_id": sid, "policy_id": pid, "n": n, "k": k, "lo": lo, "hi": hi,
                     "status": null_status(k, n, alpha, eps, tail), **tag}
    return {"null_checks": rows}


def hold_phase(cfg, mode, context):
    """Verified HOLD record: HOLD_NULL alarms of every frozen CAL cell at its h with CP null checks, or its reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    setups, campaign, apps = desc["scope"]["setups"], desc["campaign"], desc["scope"]["applications"]
    candidates = _hold_plan_keys(desc)
    if pdb.canon(plan["HOLD"]) != pdb.canon(candidates):
        raise ValueError(f"the HOLD plan must schedule exactly the HOLD_NULL keys {candidates}")
    params, phases = desc["science"]["parameters"], staging / "phases"
    H, K, scoped = params["H"], params["K"], {pdb.canon(s): s for s in setups}
    later = [{"phase": "ALT", "key": key} for key in plan["ALT"]]
    allocated, ordinary = "allocation" in desc, desc["sizes"]["HOLD_NULL"]
    cells, ns, loaded, inputs, committed = {}, {}, {}, {}, None

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def remember(key, rows, arrays):
        k = pdb.canon(key)
        if rows != ns[k] or not _hold_valid(cells[k], arrays, rows, H, K, key[5] if allocated else None):
            raise PartitionMismatch(f"HOLD partition {key} does not hold its exact {ns[k]} rows and cell arrays")
        loaded[k] = {cid: int((arrays["first_" + cid] > 0).sum()) for cid, *_ in cells[k]}

    def setup_inputs(setup):
        if pdb.canon(setup) not in inputs:
            frame_key, fit_key = ["frame", campaign, setup[1]], ["fit", campaign, *setup]
            try:
                frame = _setup_cache(_verify_partition(staging, did, {}, frame_key)[2], frame_key)
                fit = frame if setup[0] == "EXACT" else _setup_cache(
                    _verify_partition(staging, did, {}, fit_key)[2], fit_key)
            except ValueError as exc:
                raise PartitionMismatch(f"the cached SETUP frame or fit of {setup} is not a valid planned record") from exc
            inputs[pdb.canon(setup)] = frame, fit
        return inputs[pdb.canon(setup)]

    def produce(key):
        k, setup, app = pdb.canon(key), scoped[pdb.canon(key[1:4])], key[4]
        n = ns[k]
        start = key[5] if allocated else 0
        indices = range(start, start + n)
        if not cells[k]:
            return {"path_index" if allocated else "index": np.arange(start, start + n)}
        frame, fit = setup_inputs(setup)
        Y = _score_requests(desc, frame, fit, app,
                            [(("path", campaign, *setup, "HOLD_NULL", i), None) for i in indices], context)
        if not (Y.dtype == np.float64 and Y.shape == (n, H, 20) and np.isfinite(Y).all()):
            raise ValueError(f"the HOLD_NULL scores of {key} are not a finite float64 Y of shape ({n}, {H}, 20)")
        q, out = {}, {"path_index": np.arange(start, start + n)} if allocated else {}
        for cid, _, _, family, bundle, h in cells[k]:
            if family is not None and family not in q:
                draws = [("meta", campaign, *setup, "HOLD_NULL", family, i) for i in indices]
                infos = [direction_information(desc, frame, fit, setup, app, draw) for draw in draws]
                if {info["status"] for info in infos} != {"SUPPORTED"}:
                    raise ValueError(f"the oracle family {family} of {key} is not SUPPORTED for every row")
                q[family] = _real_array([info["q"] for info in infos], f"the true q of {family} in {key}", 2)
                if not (q[family].shape == (n, 20) and np.isfinite(q[family]).all() and (q[family] >= 0).all()):
                    raise ValueError(f"the true q of {family} in {key} is not a finite nonnegative ({n}, 20) batch")
            result = nonoracle_scan(Y, bundle, h) if family is None else oracle_scan(Y, q[family], bundle, h)
            out["first_" + cid], out["mask_" + cid] = result["first"], result["mask_bits"]
        if not _hold_valid(cells[k], out, n, H, K, start if allocated else None):
            raise ValueError(f"the HOLD scans of {key} are not valid ({n},) first alarms and ({n}, {H}) uint32 masks")
        return out

    try:
        if not os.path.lexists(phases / "NULL_PLAN.json"):
            raise PhaseOrderError(f"HOLD of design {did} has no committed NULL_PLAN predecessor")
        null = null_plan_phase(cfg, mode, context)
        records = _lineage(staging, desc, did, "HOLD")
        if pdb.canon(records["NULL_PLAN"]) != pdb.canon(null):
            raise PartitionMismatch(f"the verified NULL_PLAN record of design {did} differs from its committed lineage")
        upstream = {p: r["phase_digest"] for p, r in records.items()}
        keys = _scheduled_keys(desc, "HOLD", candidates, records)
        sequence = sorted(keys, key=lambda key: (pdb.canon(key[:5]), key[5])) if allocated else keys
        for key in keys:
            n = _expected_rows(desc, "HOLD", key, records)
            if not (type(n) is int and n > 0):
                raise ValueError(f"the HOLD partition {key} needs a positive integer row count, got {n!r}")
            ns[pdb.canon(key)] = n
        try:
            thresholds, index, used = records["CAL"]["derived"]["thresholds"], {}, []
            for cid, row in thresholds.items():
                ident = (row["setup_id"], row["policy_id"], row.get("family"))
                if ident in index:
                    raise ValueError(f"the CAL identity {ident} repeats")
                index[ident] = cid
            cohorts, primary_ids = {}, set()
            primary = desc["science"]["phi"]["setup"]
            for setup, app in itertools.product(setups, apps):
                name = pdb.canon(setup)
                meta = records["SETUP"]["derived"]["setups"][name]["applications"][app]
                dev = records["DEV"]["derived"]["setups"][name][app]
                if dev["setup_id"] != meta["setup_id"]:
                    raise ValueError(f"the DEV row of {setup} {app} names another setup_id than SETUP")
                cohort = []
                for _, pid, family, bundle in _cal_cells(desc, app, dev):
                    cid = index[(meta["setup_id"], pid, family)]
                    h = thresholds[cid]["h"]
                    if not (type(h) is float and math.isfinite(h)):
                        raise ValueError(f"the CAL threshold {cid} is not a finite float h")
                    cohort.append((cid, meta["setup_id"], pid, family, bundle, h))
                    used.append(cid)
                if allocated and setup == primary and app == "RESIDUAL":
                    primary_ids = {dev["policies"]["PRIMARY"][label]["policy_id"] for label in P_CONF}
                    if len(primary_ids) != len(P_CONF) or not primary_ids <= {
                            pid for _, _, pid, family, _, _ in cohort if family is None}:
                        raise ValueError("primary HOLD needs exactly three runnable P_CONF identities")
                cohorts[name, app] = cohort
            if sorted(used) != sorted(thresholds):
                raise ValueError("the planned HOLD cells do not match the CAL thresholds one to one")
            for key in keys:
                cohort = cohorts[pdb.canon(key[1:4]), key[4]]
                if allocated and key[5] >= ordinary:
                    cohort = [cell for cell in cohort if cell[3] is None and cell[2] in primary_ids]
                cells[pdb.canon(key)] = cohort
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
            raise PartitionMismatch(f"the committed SETUP, DEV and CAL records of {did} do not define its HOLD cells") from exc
        if os.path.lexists(phases / "HOLD.json"):
            record = _load_phase(staging, desc, did, "HOLD", records)
            if [pdb.canon(row["key"]) for row in record["partitions"]] != [pdb.canon(key) for key in keys]:
                raise PartitionMismatch(f"the committed HOLD partitions of design {did} differ from its planned keys")
            try:
                for key in keys:
                    _, rows, arrays = _verify_partition(staging, did, upstream, key)
                    remember(key, rows, arrays)
                    del arrays
                rebuilt = _hold_checks(desc, cells, loaded, ns)
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise PartitionMismatch(f"the committed HOLD null checks of design {did} do not verify") from exc
            if pdb.canon(rebuilt) != pdb.canon(record["derived"]):
                raise PartitionMismatch(f"the committed HOLD record of design {did} disagrees with its payloads")
            committed = record
        elif any(os.path.lexists(phases / f"{p}.json") for p in ("ALT", "FINAL")):
            raise PhaseOrderError(f"HOLD of design {did} has no record while a later record exists")
        else:
            for key in keys:
                if os.path.lexists(_partition_path(staging, did, upstream, key).with_suffix(".json")):
                    _, rows, arrays = _verify_partition(staging, did, upstream, key)
                    remember(key, rows, arrays)
                    del arrays
    finally:
        checkpoint()
    if committed is not None:
        require_budget(staging, context["authority"], plan, context["started"], ("HOLD", later))
        return committed
    pending = [{"phase": "HOLD", "key": key} for key in keys if pdb.canon(key) not in loaded]
    require_budget(staging, context["authority"], plan, context["started"], ("NULL_PLAN", pending + later))
    for key in sequence:
        k = pdb.canon(key)
        if k not in loaded:
            arrays = guarded_partition(context, "HOLD", upstream, key, lambda key=key: produce(key))
            remember(key, ns[k], arrays)
            del arrays
    try:
        derived = _hold_checks(desc, cells, loaded, ns)
    finally:
        checkpoint()
    require_budget(staging, context["authority"], plan, context["started"], ("NULL_PLAN", later))
    return phase_record(staging, "HOLD", upstream, keys, derived)


def _alt_valid(cells, arrays, n, H, K):
    joint = arrays.get("I_joint") if isinstance(arrays, dict) else None
    if not (isinstance(joint, np.ndarray) and joint.dtype == np.float64 and joint.shape == (n,)
            and np.isfinite(joint).all() and (joint >= 0).all()):
        return False
    scans = {name: value for name, value in arrays.items() if name != "I_joint"}
    return _hold_valid(cells, scans, n, H, K) if cells else not scans


ALT_CLAIMS = {"H1": "F2_STRUCTURED_RESIDUAL", "H2": "F_HEAD_RESIDUAL", "H3": "F2_STRUCTURED_RESIDUAL"}


def _alt_confirmatory(desc):
    phi = desc["science"]["phi"]
    declared = {"setup": phi.get("setup") if isinstance(phi, dict) else None, "application": "RESIDUAL",
                "window": 128, "cost": "MIX", "m": 3, "delta_NI": 0.1, "claims": ALT_CLAIMS}
    if not pdb.canon(phi) == pdb.canon(declared):
        raise ValueError("the declared confirmatory block is not RESIDUAL W128 MIX, m 3, delta_NI 0.10 "
                         f"with the claims {ALT_CLAIMS}")


def alt_phase(cfg, mode, context):
    """Verified ALT record: family trial alarms at every frozen CAL cell h with offline I_joint, or its reload."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    scope, campaign = desc["scope"], desc["campaign"]
    setups, apps = scope["setups"], scope["applications"]
    unknown = [f for f in scope["families"] if f not in DRIFT_FAMILIES]
    if unknown:
        raise ValueError(f"the scoped families {unknown} are not in DRIFT_FAMILIES")
    keys = sorted((["ALT", *s, app, f] for s in setups for app in apps for f in scope["families"]
                   if DRIFT_FAMILIES[f][0] == app), key=pdb.canon)
    if pdb.canon(plan["ALT"]) != pdb.canon(keys):
        raise ValueError(f"the ALT plan must schedule exactly the ALT keys {keys}")
    params, phases, n = desc["science"]["parameters"], staging / "phases", desc["sizes"]["ALT"]
    H, K, scoped = params["H"], params["K"], {pdb.canon(s): s for s in setups}
    if keys and not (type(n) is int and n > 0):
        raise ValueError(f"the planned ALT partitions need a positive integer n_alt, got {n!r}")
    if desc["science"]["phi"]["setup"] in setups:
        _alt_confirmatory(desc)
    cells, trials, loaded, inputs, committed = {}, {}, {}, {}, None

    def checkpoint():
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])

    def setup_inputs(setup):
        if pdb.canon(setup) not in inputs:
            frame_key, fit_key = ["frame", campaign, setup[1]], ["fit", campaign, *setup]
            try:
                frame = _setup_cache(_verify_partition(staging, did, {}, frame_key)[2], frame_key)
                fit = frame if setup[0] == "EXACT" else _setup_cache(
                    _verify_partition(staging, did, {}, fit_key)[2], fit_key)
            except ValueError as exc:
                raise PartitionMismatch(f"the cached SETUP frame or fit of {setup} is not a valid planned record") from exc
            inputs[pdb.canon(setup)] = frame, fit
        return inputs[pdb.canon(setup)]

    def produce(key):
        k, setup, app, family = pdb.canon(key), scoped[pdb.canon(key[1:4])], key[4], key[5]
        frame, fit = setup_inputs(setup)
        basis = PROJECTION_ARMS[setup[0]]
        infos = [direction_information(desc, frame, fit, setup, app, ("meta", campaign, *setup, "ALT", family, i))
                 for i in range(n)]
        if not all(isinstance(info, dict) and info.get("status") == "SUPPORTED" and info.get("family") == family
                   and info.get("oracle_basis") == basis for info in infos):
            raise ValueError(f"the ALT information of {key} is not SUPPORTED {family} on the {basis} basis for every row")
        deltas = _real_array([info["delta"] for info in infos], f"the raw ALT deltas of {key}", 2)
        if not (deltas.shape == (n, setup[1]) and np.isfinite(deltas).all() and deltas.any(axis=1).all()):
            raise ValueError(f"the raw ALT deltas of {key} are not finite real ({n}, {setup[1]}) deltas "
                             "that are nonzero in every row")
        out = {}
        if cells[k]:
            q = None
            if any(cell[3] is not None for cell in cells[k]):
                q = _real_array([info["q"] for info in infos], f"the true q of {key}", 2)
                if not (q.shape == (n, 20) and (q >= 0).all()):
                    raise ValueError(f"the true q of {key} is not a nonnegative ({n}, 20) array")
            Y = _score_requests(desc, frame, fit, app,
                                [(("path", campaign, *setup, "ALT", i), infos[i]["delta"]) for i in range(n)],
                                context)
            if not (Y.dtype == np.float64 and Y.shape == (n, H, 20) and np.isfinite(Y).all()):
                raise ValueError(f"the ALT scores of {key} are not a finite float64 Y of shape ({n}, {H}, 20)")
            for cid, _, _, cell_family, bundle, h in cells[k]:
                result = nonoracle_scan(Y, bundle, h) if cell_family is None else oracle_scan(Y, q, bundle, h)
                out["first_" + cid], out["mask_" + cid] = result["first"], result["mask_bits"]
        out["I_joint"] = _real_array([info["I_joint"] for info in infos], f"the I_joint of {key}", 1)
        if not _alt_valid(cells[k], out, n, H, K):
            raise ValueError(f"the ALT scans of {key} are not valid ({n},) first alarms, ({n}, {H}) uint32 masks "
                             f"and a ({n},) I_joint")
        return out

    try:
        if not os.path.lexists(phases / "HOLD.json"):
            raise PhaseOrderError(f"ALT of design {did} has no committed HOLD predecessor")
        hold = hold_phase(cfg, mode, context)
        records = _lineage(staging, desc, did, "ALT")
        if pdb.canon(records["HOLD"]) != pdb.canon(hold):
            raise PartitionMismatch(f"the verified HOLD record of design {did} differs from its committed lineage")
        upstream = {p: r["phase_digest"] for p, r in records.items()}
        try:
            thresholds, checks, index = records["CAL"]["derived"]["thresholds"], hold["derived"]["null_checks"], {}
            for cid, row in thresholds.items():
                ident = (row["setup_id"], row["policy_id"], row.get("family"))
                if ident in index:
                    raise ValueError(f"the CAL identity {ident} repeats")
                index[ident] = cid
            for key in keys:
                name, app, family, k = pdb.canon(key[1:4]), key[4], key[5], pdb.canon(key)
                meta = records["SETUP"]["derived"]["setups"][name]["applications"][app]
                dev = records["DEV"]["derived"]["setups"][name][app]
                head, sid = meta["head"], meta["setup_id"]
                if dev["setup_id"] != sid:
                    raise ValueError(f"the DEV row of {key} names another setup_id than its SETUP metadata")
                if app == "RESIDUAL" and not (head["status"] in ("GEOMETRY_ALIGNED", "DESIGN_CONTROL_INCONCLUSIVE")
                                              and isinstance(head["geometry"], dict)):
                    raise ValueError(f"the SETUP metadata of {key} does not carry its received HEAD geometry")
                cells[k] = []
                for _, pid, cell_family, bundle in _cal_cells(desc, app, dev):
                    if cell_family not in (None, family):
                        continue
                    cid = index[(sid, pid, cell_family)]
                    h, check = thresholds[cid]["h"], checks[cid]
                    if not (type(h) is float and math.isfinite(h)):
                        raise ValueError(f"the CAL threshold {cid} is not a finite float h")
                    if (check["setup_id"], check["policy_id"], check.get("family")) != (sid, pid, cell_family):
                        raise ValueError(f"the HOLD null check {cid} names another CAL cell")
                    cells[k].append((cid, sid, pid, cell_family, bundle, h))
                trials[k] = {"setup_id": sid, "family": family, "calibration_ids": [c[0] for c in cells[k]],
                             "oracle_basis": PROJECTION_ARMS[key[1]]}
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
            raise PartitionMismatch(f"the committed SETUP, DEV, CAL and HOLD records of {did} do not define its ALT "
                                    f"cells") from exc
        if os.path.lexists(phases / "ALT.json"):
            record = _load_phase(staging, desc, did, "ALT", records)
            if [pdb.canon(row["key"]) for row in record["partitions"]] != [pdb.canon(key) for key in keys]:
                raise PartitionMismatch(f"the committed ALT partitions of design {did} differ from its planned keys")
            for key in keys:
                _, rows, arrays = _verify_partition(staging, did, upstream, key)
                if rows != n or not _alt_valid(cells[pdb.canon(key)], arrays, rows, H, K):
                    raise PartitionMismatch(f"the committed ALT partition {key} does not hold its exact cell arrays")
            if pdb.canon({"trials": trials}) != pdb.canon(record["derived"]):
                raise PartitionMismatch(f"the committed ALT record of design {did} disagrees with its frozen trials")
            committed = record
        elif os.path.lexists(phases / "FINAL.json"):
            raise PhaseOrderError(f"ALT of design {did} has no record while a later record exists")
        else:
            for key in keys:
                if os.path.lexists(_partition_path(staging, did, upstream, key).with_suffix(".json")):
                    k = pdb.canon(key)
                    _, rows, arrays = _verify_partition(staging, did, upstream, key)
                    if rows != n or not _alt_valid(cells[k], arrays, rows, H, K):
                        raise PartitionMismatch(f"cached ALT partition {key} does not hold its exact {n} rows")
                    loaded[k] = arrays
    finally:
        checkpoint()
    if committed is not None:
        require_budget(staging, context["authority"], plan, context["started"], ("ALT", []))
        return committed
    pending = [{"phase": "ALT", "key": key} for key in keys if pdb.canon(key) not in loaded]
    require_budget(staging, context["authority"], plan, context["started"], ("HOLD", pending))
    for key in keys:
        k = pdb.canon(key)
        if k not in loaded:
            arrays = guarded_partition(context, "ALT", upstream, key, lambda key=key: produce(key))
            if not _alt_valid(cells[k], arrays, n, H, K):
                raise PartitionMismatch(f"ALT partition {key} does not hold its exact cell arrays")
            loaded[k] = arrays
    checkpoint()
    require_budget(staging, context["authority"], plan, context["started"], ("HOLD", []))
    return phase_record(staging, "ALT", upstream, keys, {"trials": trials})


def run_phases(cfg, mode, context):
    """Drive admitted phases in plan order and return verified records (plan §§2.3, 13, 15; amendment §§3.1, 3.5)."""
    staging = Path(context["staging"])
    did, desc = _staged_design(staging)
    if pdb.canon(design_descriptor(cfg, mode)) != pdb.canon(desc):
        raise StagingMismatch(f"staged design {did} does not match the current design descriptor")
    authority = authorize(mode, cfg, desc, context.get("jobs", 1))
    if authority != context["authority"]:
        raise AuthorizationRefused("authority does not match the staged design and mode")
    plan = context["plan"]
    _validated_plan(plan)
    if plan != partition_plan(desc):
        raise StagingMismatch("partition plan does not match the staged design")
    for controller in (setup_phase, dev_phase, cal_phase, null_plan_phase, hold_phase, alt_phase):
        controller(cfg, mode, context)
    records, missing = _planned_progress(staging, did, desc, plan, None)
    if tuple(records) != PHASES or missing:
        raise PhaseOrderError(f"phase order {tuple(records)} != {PHASES}; missing={missing}")
    return records


def head_control(u_prefix, geometry, kappa_det, kappa_geo, H):
    """Aligned iff all joint I_E > 0 and min f_E >= kappa_geo; detectable iff u_prefix <= kappa_det * H."""
    H = _count(H, "H", 1)
    if not (_finite_nonnegative(u_prefix) and 1 <= u_prefix <= H):
        raise ValueError(f"u_prefix must be a finite real in [1, {H}], got {u_prefix!r}")
    if not all(_finite_nonnegative(k) and 0 < k <= 1 for k in (kappa_det, kappa_geo)):
        raise ValueError(f"kappa_det and kappa_geo must be finite reals in (0, 1], got {kappa_det!r}, {kappa_geo!r}")
    try:
        positive, low = geometry["all_I_E_positive"], geometry["summary"]["f_E"]["min"]
    except (KeyError, TypeError) as exc:
        raise ValueError("geometry must carry all_I_E_positive and its summary f_E min") from exc
    if not (type(positive) is bool and (low is None or _finite_nonnegative(low))):
        raise ValueError("geometry needs a bool all_I_E_positive and a finite or None f_E min, "
                         f"got {positive!r}, {low!r}")
    aligned = bool(positive and low is not None and low >= kappa_geo)
    detectable = bool(u_prefix <= kappa_det * H)
    return {"geometry_status": "GEOMETRY_ALIGNED" if aligned else "DESIGN_CONTROL_INCONCLUSIVE",
            "prefix_status": "PREFIX_DETECTABLE" if detectable else "PREFIX_DETECTABILITY_NOT_ESTABLISHED",
            "valid": aligned and detectable, "kappa_det": kappa_det, "kappa_geo": kappa_geo, "H": H,
            "all_I_E_positive": positive, "f_E_min": low}


def confirmatory_inference(desc, hold_first, alt_first, null_states, boot_indices, geometry, *, preconditions=True):
    """Independent H1-H3 rows: Tango HOLD FPR contrast, paired bootstrap RMST_H bounds and the H2 HEAD control."""
    try:
        _alt_confirmatory(desc)
        science = desc["science"]
        H, alpha, B = science["parameters"]["H"], science["parameters"]["alpha"], science["bootstrap"]["B"]
        m, delta = science["phi"]["m"], science["phi"]["delta_NI"]
        kappa_det, kappa_geo = science["head"]["kappa_det"], science["head"]["kappa_geo"]
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("desc must carry H, alpha, bootstrap B, the frozen phi block and the HEAD kappas") from exc
    H, B = _count(H, "H", 1), _count(B, "B", 1)
    if not (_finite_nonnegative(alpha) and 0 < alpha < 1 and type(preconditions) is bool):
        raise ValueError(f"need a finite alpha in (0, 1) and a bool preconditions, got {alpha!r}, {preconditions!r}")
    tail, info = _tail(alpha / m), P_CONF[0]
    claims = (("H1", P_CONF[1]), ("H2", P_CONF[1]), ("H3", P_CONF[2]))
    try:
        states = {p: null_states[p] for p in P_CONF}
        hold = {p: np.asarray(hold_first[p]) for p in P_CONF}
        alt = {(ALT_CLAIMS[k], p): np.asarray(alt_first[ALT_CLAIMS[k]][p]) for k, c in claims for p in (info, c)}
        boot = {f: np.asarray(boot_indices[f]) for f in ALT_CLAIMS.values()}
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("need null states and HOLD first alarms of every P_CONF policy, the claimed ALT first "
                         "alarms and a bootstrap index matrix per claimed family") from exc

    def firsts(v, n):
        return (v.ndim == 1 and v.size == n > 0 and v.dtype.kind == "i"
                and bool(((v == -1) | ((v >= 1) & (v <= H))).all()))

    def bound(v, idx, p, n):
        s, r = np.sort(v[idx].sum(axis=1)), (B - 1) * p
        k = int(r)
        return float((int(s[k]) + (r - k) * int(s[min(k + 1, B - 1)] - s[k])) / n)

    q = Fraction(str(alpha)) / m
    known = ("NULL_VALIDATED", "NULL_INCONCLUSIVE", "NULL_FAILED")
    if not all(type(s) is str and s in known for s in states.values()):
        raise ValueError(f"the P_CONF null states must lie in {known}, got {states}")
    n_hold, n_alt = hold[info].size, {f: alt[f, info].size for f in boot}
    if not (all(firsts(v, n_hold) for v in hold.values()) and all(firsts(v, n_alt[f]) for (f, _), v in alt.items())):
        raise ValueError(f"HOLD and ALT first alarms must be nonempty aligned integer vectors of -1 or 1..{H}")
    if not all(b.ndim == 2 and b.shape == (B, n) and b.dtype.kind == "i" and bool(((b >= 0) & (b < n)).all())
               for b, n in ((boot[f], n_alt[f]) for f in boot)):
        raise ValueError(f"each claimed family needs an integer ({B}, n_alt) bootstrap matrix of in-range indices")
    T = {k: np.where(v == -1, H, v).astype(np.int64) for k, v in alt.items()}
    rows = {}
    for key, comp in claims:
        family = ALT_CLAIMS[key]
        a, c, idx = T[family, info], T[family, comp], boot[family]
        hit, other = hold[info] != -1, hold[comp] != -1
        b_n, c_n = int((hit & ~other).sum()), int((~hit & other).sum())
        lo, hi = tango_interval(b_n, c_n, n_hold, tail)
        diff = (a - c)[idx].mean(axis=1)
        row = {"family": family, "info_policy": info, "comparator_policy": comp, "m": m, "tail": tail, "deff": 1,
               "coverage_claim": "NONE_FINITE", "rmst_interval_label": "BOOTSTRAP_PERCENTILE_APPROX",
               "fpr_interval_label": "TANGO_SCORE_ASYMPTOTIC", "n_hold": n_hold, "n_alt": n_alt[family], "B": B,
               "fpr_b": b_n, "fpr_c": c_n, "fpr_delta": (b_n - c_n) / n_hold, "fpr_ci": (lo, hi),
               "fpr_equivalent": bool(-0.01 <= lo and hi <= 0.01), "rmst_info": float(a.mean()),
               "rmst_comparator": float(c.mean()), "rmst_difference": float(a.mean() - c.mean()),
               "rmst_ci": tuple(float(x) for x in np.quantile(diff, (0.025, 0.975))),
               "rmst_ratio_info_over_comparator": float(a.mean() / c.mean())}
        for name, p in (("info", info), ("comparator", comp)):
            hits = alt[family, p][alt[family, p] != -1]
            row[name + "_detected_fraction"] = hits.size / n_alt[family]
            row[name + "_censored_fraction"] = (n_alt[family] - hits.size) / n_alt[family]
            row[name + "_median_given_detection"] = float(np.median(hits)) if hits.size else None
        if key == "H2":
            ni = bound(10 * a - 11 * c, idx, 1 - q, 10 * n_alt[family])
            u = bound(c, idx, 1 - q, n_alt[family])
            control = head_control(u, geometry, kappa_det, kappa_geo, H)
            row.update(delta_NI=delta, ni_upper=ni, u_prefix=u, control=control)
            success, probative = ni < 0, control["valid"]
        else:
            row["gain_bound"] = bound(c - a, idx, q, n_alt[family])
            success, probative = row["gain_bound"] > 0, True
        valid = preconditions and "NULL_FAILED" not in (states[info], states[comp])
        row["status"] = ("INVALID_NULL_FAILED" if not valid else "NOT_ESTABLISHED" if not success
                         else "NONINFERIORITY_NOT_PROBATIVE" if not probative
                         else "CONFIRMED_AT_ATTAINED_COMPARABLE_FPR" if row["fpr_equivalent"]
                         else "CONFIRMED_AT_COMMON_NOMINAL_ALPHA_ONLY")
        rows[key] = row
    return rows


def _staged_hold_cells(staging, did, desc, records, base, kind, cids):
    hold = records["HOLD"]
    setup, app = base[1:4], base[4]
    name = pdb.canon(setup)
    sid = records["SETUP"]["derived"]["setups"][name]["applications"][app]["setup_id"]
    dev = records["DEV"]["derived"]["setups"][name][app]
    thresholds = records["CAL"]["derived"]["thresholds"]
    checks = hold["derived"]["null_checks"]
    ordinary = desc["sizes"]["HOLD_NULL"]
    n_hold = records["NULL_PLAN"]["derived"]["n_hold"]
    primary = setup == desc["science"]["phi"]["setup"] and app == "RESIDUAL"
    conf = {dev["policies"]["PRIMARY"][label]["policy_id"] for label in P_CONF} if primary else set()
    sizes = {}
    for cid, row in thresholds.items():
        if row["setup_id"] == sid:
            check = checks.get(cid)
            n = n_hold if row["policy_id"] in conf and row.get("family") is None else ordinary
            if check is None or (check["setup_id"], check["policy_id"], check.get("family"), check["n"]) != (
                    sid, row["policy_id"], row.get("family"), n):
                raise PartitionMismatch(f"HOLD cell {cid} does not match its frozen cohort")
            sizes[cid] = n
    cells = {cid: {"values": [], "paths": [], "blocks": []} for cid in cids}
    if not set(cells) <= sizes.keys():
        raise PartitionMismatch(f"HOLD cells of {base} refer to another setup or calibration")
    parts = sorted((part for part in hold["partitions"] if part["key"][:5] == base),
                   key=lambda part: part["key"][5])
    starts = [start for start, _ in _hold_spans(desc, n_hold if primary else ordinary)]
    if [part["key"] for part in parts] != [[*base, start] for start in starts]:
        raise PartitionMismatch(f"HOLD inventory of {base} does not match its realized block plan")
    for part in parts:
        key = part["key"]
        sha, n, arrays = _verify_partition(staging, did, hold["upstream"], key)
        index = arrays.get("path_index")
        start = key[5]
        expected = {"path_index"} | {f"{field}_{cid}" for cid, size in sizes.items() if start < size
                                     for field in ("first", "mask")}
        if (sha != part["sha256"] or n != part["n_rows"] or n != _expected_rows(desc, "HOLD", key, records)
                or set(arrays) != expected or index.dtype.kind != "i"
                or not np.array_equal(index, np.arange(start, start + n))):
            raise PartitionMismatch(f"HOLD block {key} does not match its verified paths and cells")
        for cid, cell in cells.items():
            if start < sizes[cid]:
                values = arrays[f"{kind}_{cid}"]
                if kind == "first" and (values.shape != (n,) or values.dtype.kind != "i"):
                    raise PartitionMismatch(f"HOLD block {key} has invalid first hits for {cid}")
                cell["values"].append(values)
                cell["paths"].append(index)
                cell["blocks"].append([key, sha])
        del arrays
    for cid, cell in cells.items():
        cell["values"] = np.concatenate(cell["values"])
        cell["paths"] = np.concatenate(cell["paths"])
        if not np.array_equal(cell["paths"], np.arange(sizes[cid])):
            raise PartitionMismatch(f"HOLD cell {cid} does not cover its frozen index prefix")
    return cells


def confirmatory_from_staging(cfg, mode, context):
    """Full-mode H1-H3 rows from the verified committed primary RESIDUAL lineage and one planned bootstrap per family."""
    if mode != "full":
        raise ValueError(f"confirmatory evaluation is full-mode only, got {mode!r}")
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    _alt_confirmatory(desc)
    setup, campaign, scope = desc["science"]["phi"]["setup"], desc["campaign"], desc["scope"]
    if not (isinstance(setup, (list, tuple)) and list(setup[:1]) == ["FITTED_LW_GAUSSIAN"]) or (
            setup not in scope["setups"] or "RESIDUAL" not in scope["applications"]):
        raise ValueError(f"the primary setup {setup} is not a scoped FITTED_LW_GAUSSIAN setup with RESIDUAL in design {did}")
    try:
        if not os.path.lexists(staging / "phases" / "ALT.json"):
            raise PhaseOrderError(f"design {did} has no committed ALT record")
        records, missing = _planned_progress(staging, did, desc, plan, None)
        if len(records) != len(PHASES):
            raise PhaseOrderError(f"design {did} has no committed {PHASES[len(records)]} record and "
                                  f"{len(missing)} pending planned partitions")
        upstream = {p: {q: records[q]["phase_digest"] for q in PHASES[:i]} for i, p in enumerate(PHASES)}
        if pdb.canon(alt_phase(cfg, mode, context)) != pdb.canon(records["ALT"]):
            raise PartitionMismatch(f"the verified ALT record of design {did} differs from its committed lineage")
        info, comparators = P_CONF[0], {"H1": P_CONF[1], "H2": P_CONF[1], "H3": P_CONF[2]}
        families, pairs = sorted(set(ALT_CLAIMS.values())), {(ALT_CLAIMS[k], c) for k, c in comparators.items()}
        labels = {f: [p for p in P_CONF if p == info or (f, p) in pairs] for f in families}
        name, n_alt, B = pdb.canon(setup), desc["sizes"]["ALT"], desc["science"]["bootstrap"]["B"]
        known = ("NULL_VALIDATED", "NULL_INCONCLUSIVE", "NULL_FAILED")
        try:
            meta = records["SETUP"]["derived"]["setups"][name]["applications"]["RESIDUAL"]
            dev = records["DEV"]["derived"]["setups"][name]["RESIDUAL"]
            thresholds, checks = records["CAL"]["derived"]["thresholds"], records["HOLD"]["derived"]["null_checks"]
            trials, sid, head = records["ALT"]["derived"]["trials"], meta["setup_id"], meta["head"]
            if not (dev["setup_id"] == sid and head["status"] in ("GEOMETRY_ALIGNED", "DESIGN_CONTROL_INCONCLUSIVE")
                    and isinstance(head["geometry"], dict) and type(B) is int and B > 0
                    and type(n_alt) is int and n_alt > 0):
                raise ValueError("the primary SETUP, DEV, bootstrap B or n_alt is not a committed confirmatory input")
            cids, states = {}, {}
            for p in P_CONF:
                pid = dev["policies"]["PRIMARY"][p]["policy_id"]
                [cid] = [c for c, t in thresholds.items()
                         if (t["setup_id"], t["policy_id"], t.get("family")) == (sid, pid, None)]
                check = checks[cid]
                if (check["setup_id"], check["policy_id"], check.get("family")) != (sid, pid, None) or not (
                        type(check["status"]) is str and check["status"] in known):
                    raise ValueError(f"the HOLD null check {cid} is not the family-free cell of {p}")
                cids[p], states[p] = cid, check["status"]
            if len(set(cids.values())) != len(P_CONF):
                raise ValueError(f"the P_CONF calibration ids {cids} are not distinct")
            base = ["HOLD_NULL", *setup, "RESIDUAL"]
            if "allocation" in desc:
                n_hold = records["NULL_PLAN"]["derived"]["n_hold"]
                held = _staged_hold_cells(staging, did, desc, records, base, "first", cids.values())
                hold = {p: held[cids[p]]["values"] for p in P_CONF}
            else:
                _, n_hold, held = _verify_partition(staging, did, upstream["HOLD"], base)
                hold = {p: held["first_" + cids[p]] for p in P_CONF}
            alt = {}
            for f in families:
                key = ["ALT", *setup, "RESIDUAL", f]
                trial = trials[pdb.canon(key)]
                if (trial["setup_id"], trial["family"]) != (sid, f) or not (
                        {cids[p] for p in labels[f]} <= set(trial["calibration_ids"])):
                    raise ValueError(f"the ALT trial {key} does not carry the P_CONF calibration ids")
                _, n_rows, arrays = _verify_partition(staging, did, upstream["ALT"], key)
                if n_rows != n_alt:
                    raise ValueError(f"the ALT partition {key} holds {n_rows} rows instead of {n_alt}")
                alt[f] = {p: arrays["first_" + cids[p]] for p in labels[f]}
            vectors = [(v, n_hold) for v in hold.values()] + [(v, n_alt) for row in alt.values() for v in row.values()]
            if not all(v.dtype.kind == "i" and v.shape == (n,) for v, n in vectors):
                raise ValueError("the committed HOLD and ALT first alarms are not aligned integer vectors")
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
            raise PartitionMismatch(f"the committed records of {did} do not define its primary confirmatory cells") from exc
        keys = {f: ["boot", campaign, *setup, "RESIDUAL", f] for f in families}
        planned = {tuple(k) for k in seed_plan(cfg, mode)["keys"]}
        if any(tuple(k) not in planned for k in keys.values()):
            raise ValueError(f"the bootstrap keys {keys} are not all in the seed plan of design {did}")
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])
        require_budget(staging, context["authority"], plan, context["started"], ("ALT", []))
        seed, boot = int(cfg["seed"]), {}
        cache = context.get("bootstrap_cache")
        for f, key in keys.items():
            boot[f] = _bootstrap_indices(seed, key, B, n_alt)
            if cache is not None:
                cache[tuple(key)] = boot[f]
        out = confirmatory_inference(desc, hold, alt, states, boot, head["geometry"], preconditions=True)
        claims = {k: {**out[k], "info_calibration_id": cids[info], "comparator_calibration_id": cids[c],
                      "info_null_status": states[info], "comparator_null_status": states[c],
                      **({"geometry": head["geometry"]} if k == "H2" else {}),
                      **({"hold_phase_digest": records["HOLD"]["phase_digest"]} if "allocation" in desc else {})}
                  for k, c in comparators.items()}
        result = {"design_id": did, "setup": list(setup), "setup_id": sid, "alt_phase_digest": records["ALT"]["phase_digest"],
                  "bootstrap_keys": keys, "claims": claims}
    finally:
        charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])
    require_budget(staging, context["authority"], plan, context["started"], ("ALT", []))
    return result


def _common_hold_prefix(mode, hold, hold_paths):
    if not isinstance(hold_paths, dict) or set(hold_paths) != set(hold):
        raise ValueError("hold_paths needs exactly the calibration ids of hold_first")
    common = None
    for cell, evidence in hold_paths.items():
        if not isinstance(evidence, (list, tuple)) or len(evidence) != 2:
            raise ValueError(f"hold_paths of {cell!r} needs a path-key prefix and indices")
        prefix, indices = evidence
        if not (isinstance(prefix, (list, tuple)) and len(prefix) == 6
                and all(type(prefix[i]) is str for i in (0, 1, 2, 5))
                and prefix[0] == "path" and prefix[1] == mode.upper() and prefix[5] == "HOLD_NULL"
                and prefix[2] in PROJECTION_ARMS and type(prefix[3]) is int and type(prefix[4]) is int
                and _word(prefix[3], "HOLD dimension") >= 21):
            raise ValueError(f"hold_paths of {cell!r} has an invalid primitive HOLD_NULL prefix")
        _word(prefix[4], "HOLD fit_id")
        prefix = tuple(prefix)
        if common is not None and common != prefix:
            raise ValueError("hold_paths cells must refer to one common path namespace")
        if not (isinstance(indices, np.ndarray) and indices.dtype.kind == "i"
                and np.array_equal(indices, np.arange(hold[cell].size))):
            raise ValueError(f"hold_paths of {cell!r} must carry its exact signed index prefix")
        common = prefix
    return common


def descriptive_contrasts(mode, H, family, cells, hold_first, alt_first, boot_indices, *, hold_paths=None):
    """Nominal paired contrasts of one study group versus its PRIMARY W128 baselines plus the separate oracle pair."""
    H = _count(H, "H", 1)
    if not (type(mode) is str and mode in MODES and type(family) is str and family in DRIFT_FAMILIES):
        raise ValueError(f"need a mode in {MODES} and a family in {DRIFT_FAMILIES}, got {mode!r}, {family!r}")
    known, variants = ("NULL_VALIDATED", "NULL_INCONCLUSIVE", "NULL_FAILED"), ("PRIMARY", "GAMMA_M", "S2_DEV")
    try:
        meta = {c: (v["policy_label"], v["variant"], v["policy_id"], v["calibration_family"], v["null_status"])
                for c, v in cells.items()}
        hold = {c: np.asarray(v) for c, v in hold_first.items()}
        alt = {c: np.asarray(v) for c, v in alt_first.items()}
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("cells and first alarms must be mappings keyed by calibration id") from exc
    for c, (label, variant, pid, fam, state) in meta.items():
        if not (all(type(x) is str and x for x in (c, label, pid, variant, state))
                and variant in variants and state in known):
            raise ValueError(f"cell {c!r} needs a nonempty policy id and label, a variant in {variants} "
                             f"and a null status in {known}")
        if (fam is None) == label.startswith("ORACLE_") or fam not in (None, family):
            raise ValueError(f"cell {c!r} labelled {label} carries calibration family {fam!r}; only ORACLE_ "
                             f"policies carry one and it must be {family}")
    if len({m[2] for m in meta.values()}) != len(meta):
        raise ValueError("each policy_id needs exactly one calibration id in the supplied group")
    if not (meta and set(meta) == set(hold) == set(alt)):
        raise ValueError("cells, hold_first and alt_first need the same nonempty calibration ids")
    n_hold, n_alt = (next(iter(d.values())).size for d in (hold, alt))
    path_prefix = None
    if hold_paths is not None:
        path_prefix = _common_hold_prefix(mode, hold, hold_paths)
        conf_sizes = {hold[c].size for c, (label, variant, _, fam, _) in meta.items()
                      if label in P_CONF and variant == "PRIMARY" and fam is None}
        if len(conf_sizes) > 1:
            raise ValueError("PRIMARY P_CONF cells must share the same realized HOLD size")

    def firsts(v, n):
        return (v.ndim == 1 and v.size == n > 0 and v.dtype.kind == "i"
                and bool(((v == -1) | ((v >= 1) & (v <= H))).all()))

    if not (all(firsts(v, n_hold if path_prefix is None else v.size) for v in hold.values())
            and all(firsts(v, n_alt) for v in alt.values())):
        raise ValueError(f"HOLD and ALT first alarms must be nonempty role-aligned integer vectors of -1 or 1..{H}")
    boot = np.asarray(boot_indices)
    if not (boot.ndim == 2 and boot.shape[0] > 0 and boot.shape[1] == n_alt and boot.dtype.kind == "i"
            and bool(((boot >= 0) & (boot < n_alt)).all())):
        raise ValueError(f"need a nonempty signed integer (B, {n_alt}) bootstrap matrix of in-range indices")

    def pick(label, fam):
        found = sorted(c for c, m in meta.items() if (m[0], m[1], m[3]) == (label, "PRIMARY", fam))
        if len(found) > 1:
            raise ValueError(f"ambiguous PRIMARY {label} cells {found}")
        return found[0] if found else None

    info, prefix, oracle = pick(P_CONF[0], None), pick(P_CONF[1], None), pick("ORACLE_INFO_MIX", family)
    nonoracle = sorted(c for c, m in meta.items() if m[3] is None)
    pairs = [(c, r) for r in (info, prefix) if r is not None for c in nonoracle if c != r]
    pairs += [(oracle, info)] if oracle is not None and info is not None else []
    status = "PILOT_ONLY" if mode == "pilot" else "DESCRIPTIVE_NOMINAL"
    T, rows = {c: np.where(v == -1, H, v).astype(np.int64) for c, v in alt.items()}, []
    for cand, ref in pairs:
        a, r = T[cand], T[ref]
        diff = (a - r)[boot].mean(axis=1)
        n_pair = min(hold[cand].size, hold[ref].size)
        row = {"family": family, "status": status, "deff": 1, "coverage_claim": "NONE_FINITE",
               "rmst_interval_label": "BOOTSTRAP_PERCENTILE_APPROX", "n_hold": n_pair, "n_alt": n_alt,
               "B": int(boot.shape[0]), "rmst_candidate": float(a.mean()), "rmst_reference": float(r.mean()),
               "rmst_difference": float(a.mean() - r.mean()),
               "rmst_ci": tuple(float(x) for x in np.quantile(diff, (0.025, 0.975))),
               "rmst_ratio_candidate_over_reference": float(a.mean() / r.mean())}
        if path_prefix is not None:
            row.update(candidate_n_hold=hold[cand].size, reference_n_hold=hold[ref].size,
                       hold_pairing={"path_key_prefix": list(path_prefix), "start": 0, "stop": n_pair})
        for name, c in (("candidate", cand), ("reference", ref)):
            label, variant, pid, fam, state = meta[c]
            hits = alt[c][alt[c] != -1]
            row.update({name + "_calibration_id": c, name + "_policy_id": pid, name + "_policy_label": label,
                        name + "_variant": variant, name + "_calibration_family": fam, name + "_null_status": state,
                        name + "_detected_fraction": hits.size / n_alt,
                        name + "_censored_fraction": (n_alt - hits.size) / n_alt,
                        name + "_median_given_detection": float(np.median(hits)) if hits.size else None})
        hit, other = hold[cand][:n_pair] != -1, hold[ref][:n_pair] != -1
        if cand == oracle:
            row.update(fpr_status="ORACLE_SEPARATE", candidate_fpr=float(hit.mean()),
                       reference_fpr=float(other.mean()))
        else:
            b_n, c_n = int((hit & ~other).sum()), int((~hit & other).sum())
            row.update(fpr_status="DESCRIPTIVE_NOMINAL", fpr_interval_label="TANGO_SCORE_ASYMPTOTIC", tail=0.025,
                       fpr_b=b_n, fpr_c=c_n, fpr_delta=(b_n - c_n) / n_pair,
                       fpr_ci=tuple(tango_interval(b_n, c_n, n_pair, 0.025)))
        rows.append(row)
    return rows


def _bootstrap_indices(seed, key, B, n_alt):
    words = [32, seed, pdb.label_code(key[1]), pdb.label_code(key[0]),
             *(pdb.label_code(p) if isinstance(p, str) else int(p) for p in key[2:])]
    rng = np.random.default_rng(np.random.SeedSequence(words))
    return rng.integers(0, n_alt, size=(B, n_alt), dtype=np.int64)


def _staged_descriptive_rows(staging, did, records, desc, bootstrap_cache, checkpoint):
    alt_rec, hold_rec = records["ALT"], records["HOLD"]
    trials = alt_rec["derived"]["trials"]
    thresholds = records["CAL"]["derived"]["thresholds"]
    null_checks = hold_rec["derived"]["null_checks"]
    setups = records["DEV"]["derived"]["setups"]
    B = desc["science"]["bootstrap"]["B"]
    H = desc["science"]["parameters"]["H"]
    seed = int(desc["seed"])
    digest = alt_rec["phase_digest"]
    allocated = "allocation" in desc
    group = hold = by_id = None
    for part in alt_rec["partitions"]:
        key = list(part["key"])
        trial = trials[pdb.canon(key)]
        if not trial["calibration_ids"]:
            continue
        if tuple(key[1:5]) != group:
            group = hold = by_id = None
        checkpoint()
        if group is None:
            base = ["HOLD_NULL", *key[1:5]]
            if allocated:
                ids = [cid for cid, check in null_checks.items() if check["setup_id"] == trial["setup_id"]]
                hold = _staged_hold_cells(staging, did, desc, records, base, "first", ids)
            else:
                _, _, hold = _verify_partition(staging, did, hold_rec["upstream"], base)
            policies = setups[pdb.canon(key[1:4])][key[4]]["policies"]
            by_id = {}
            for variant in ("PRIMARY", "GAMMA_M", "S2_DEV"):
                for label, row in policies[variant].items():
                    by_id.setdefault(row["policy_id"], (label, variant))
            group = tuple(key[1:5])
        _, n_alt, alt = _verify_partition(staging, did, alt_rec["upstream"], key)
        cells, hold_first, alt_first, paths = {}, {}, {}, {}
        for cid in trial["calibration_ids"]:
            cal = thresholds[cid]
            pid = cal["policy_id"]
            label, variant = by_id[pid]
            cells[cid] = {
                "policy_label": label,
                "variant": variant,
                "policy_id": pid,
                "calibration_family": cal.get("family"),
                "null_status": null_checks[cid]["status"],
            }
            if allocated:
                hold_first[cid] = hold[cid]["values"]
                paths[cid] = (("path", desc["campaign"], *key[1:4], "HOLD_NULL"), hold[cid]["paths"])
            else:
                hold_first[cid] = hold["first_" + cid]
            alt_first[cid] = alt["first_" + cid]
        bkey = ("boot", desc["campaign"], *key[1:])
        boot = bootstrap_cache.pop(bkey, None)
        if boot is None:
            boot = _bootstrap_indices(seed, bkey, B, n_alt)
        bkey_json = json.dumps(list(bkey), sort_keys=True, separators=(",", ":"), allow_nan=False)
        pairing = {"hold_paths": paths} if allocated else {}
        for row in descriptive_contrasts(desc["mode"], H, key[5], cells, hold_first, alt_first, boot, **pairing):
            if allocated:
                row["hold_phase_digest"] = hold_rec["phase_digest"]
            yield {
                "design_id": did,
                "setup_id": trial["setup_id"],
                "application": key[4],
                "family": key[5],
                "status": row["status"],
                "alt_phase_digest": digest,
                "record_kind": "DESCRIPTIVE_CONTRAST",
                "hypothesis": "",
                "bootstrap_key": bkey_json,
                "inference_json": json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False),
            }
        boot = alt = cells = hold_first = alt_first = None
    hold = by_id = None
    checkpoint()


def selection_telemetry(mask_bits, K, h):
    """Theoretical selection telemetry of committed nonzero (n, H) uint32 K-bit masks at the frozen threshold h."""
    if not (isinstance(K, (int, np.integer)) and not isinstance(K, (bool, np.bool_)) and 1 <= K <= 32):
        raise ValueError(f"K must be an integer in 1..32, got {K!r}")
    if not (isinstance(h, (int, float, np.integer, np.floating)) and not isinstance(h, (bool, np.bool_))
            and math.isfinite(h)):
        raise ValueError(f"h must be a finite signed real threshold, got {h!r}")
    if not (isinstance(mask_bits, np.ndarray) and mask_bits.dtype == np.uint32 and mask_bits.ndim == 2
            and min(mask_bits.shape) > 0):
        raise ValueError("mask_bits must be a nonempty 2-D uint32 (n, H) array")
    K = int(K)
    if not ((mask_bits != 0).all() and (mask_bits.astype(np.uint64) >> np.uint64(K) == 0).all()):
        raise ValueError(f"every mask word must be nonzero and fit in K = {K} bits")
    n, H = (int(v) for v in mask_bits.shape)
    bits = (mask_bits[:, :, None] >> np.arange(K, dtype=np.uint32)) & np.uint32(1)
    axes = [int(a) for a in bits.sum(axis=(0, 1))]
    sizes = np.bincount(bits.sum(axis=2).astype(np.int64).ravel(), minlength=K + 1)
    switches = (mask_bits[:, 1:] != mask_bits[:, :-1]).sum(axis=1)
    per = {"screening_reads": K * H, "scan_units": K * H * (H + 1) // 2, "selection_evaluations": H - 1}
    out = {"n": n, "H": H, "K": K, "h": float(h), "axis_counts": axes,
           "axis_frequencies": [a / (n * H) for a in axes], "d_counts": [int(c) for c in sizes],
           "switches_per_path": [int(s) for s in switches]}
    return {**out, **{k + "_per_path": v for k, v in per.items()}, **{k: n * v for k, v in per.items()}}


def hold_selection_telemetry(cfg, mode, context, key, calibration_id):
    """Read-only selection telemetry of one family-free ONLINE CAL cell from its verified committed HOLD_NULL mask."""
    staging = Path(context["staging"])
    did, staged = _staged_design(staging)
    desc = design_descriptor(cfg, mode)
    if pdb.canon(desc) != pdb.canon(staged):
        raise StagingMismatch(f"the current {mode} configuration is not the staged design {did}")
    if pdb.canon(authorize(mode, cfg, desc, 1)) != pdb.canon(context["authority"]):
        raise AuthorizationRefused(f"the invocation authority is not the current authorization of design {did}")
    plan = context["plan"]
    _validated_plan(plan)
    setups, apps = desc["scope"]["setups"], desc["scope"]["applications"]
    keys = sorted((["HOLD_NULL", *s, app] for s in setups for app in apps), key=pdb.canon)
    if pdb.canon(plan["HOLD"]) != pdb.canon(_hold_plan_keys(desc)):
        raise ValueError(f"the HOLD plan must schedule exactly the HOLD_NULL keys {keys}")
    key = _partition_key(key)
    if pdb.canon(key) not in [pdb.canon(k) for k in keys]:
        raise ValueError(f"{key} is not a scoped HOLD_NULL setup and application key of design {did}")
    params, name, app = desc["science"]["parameters"], pdb.canon(key[1:4]), key[4]
    H, K = params["H"], params["K"]
    records = _lineage(staging, desc, did, "HOLD")
    hold = records["HOLD"] = _load_phase(staging, desc, did, "HOLD", dict(records))
    for phase in PHASES[:PHASES.index("HOLD") + 1]:
        expected = _scheduled_keys(desc, phase, plan[phase], records)
        if [row["key"] for row in records[phase]["partitions"]] != expected:
            raise PartitionMismatch(f"the committed {phase} partitions of design {did} differ from its planned keys")
    try:
        meta = records["SETUP"]["derived"]["setups"][name]["applications"][app]
        dev = records["DEV"]["derived"]["setups"][name][app]
        sid, axis_pcs, (lo, hi) = meta["setup_id"], meta["universe"], UNIVERSES[app]
        if not (dev["setup_id"] == sid and type(sid) is str and type(K) is int and type(H) is int and H >= 1
                and type(axis_pcs) is list and axis_pcs == list(range(lo, hi + 1)) and len(axis_pcs) == K):
            raise ValueError(f"the committed SETUP and DEV rows of {key} disagree on setup_id, K or axis PCs")
        online = {pid for _, pid, family, bundle in _cal_cells(desc, app, dev)
                  if family is None and bundle["policy"]["kind"] == "ONLINE"}
        cells = {c: (t["setup_id"], t["policy_id"], t.get("family"), t["h"])
                 for c, t in records["CAL"]["derived"]["thresholds"].items()}
        if not all(type(c) is str and type(v[0]) is str and type(v[1]) is str for c, v in cells.items()):
            raise ValueError("the committed CAL identities are not str setup and policy ids")
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        raise PartitionMismatch(f"the committed SETUP, DEV and CAL records of {did} do not define "
                                f"the cells of {key}") from exc
    cell = cells.get(calibration_id) if type(calibration_id) is str else None
    if cell is None:
        raise ValueError(f"{calibration_id!r} is not a committed CAL calibration id of design {did}")
    if cell[0] != sid:
        raise ValueError(f"the CAL cell {calibration_id} belongs to setup_id {cell[0]}, not {sid} of {key}")
    if cell[2] is not None:
        raise ValueError(f"the CAL cell {calibration_id} is a non-deployable oracle calibration of {cell[2]}")
    if cell[1] not in online:
        raise ValueError(f"the CAL cell {calibration_id} is not a family-free ONLINE policy of {key}")
    h = cell[3]
    if [c for c, v in cells.items() if v[:3] == (sid, cell[1], None)] != [calibration_id] or not (
            type(h) is float and math.isfinite(h)):
        raise PartitionMismatch(f"the CAL cell {calibration_id} is not a unique finite float threshold of {key}")
    try:
        if "allocation" in desc:
            held = _staged_hold_cells(staging, did, desc, records, key, "mask", [calibration_id])[calibration_id]
            mask, rows = held["values"], held["paths"].size
            sha = hashlib.sha256(pdb.canon(held["blocks"]).encode()).hexdigest()
        else:
            sha, rows, arrays = _verify_partition(staging, did, hold["upstream"], key)
            [part] = [r for r in hold["partitions"] if pdb.canon(r["key"]) == pdb.canon(key)]
            if not (sha == part["sha256"] and rows == part["n_rows"] == _expected_rows(desc, "HOLD", key, records)):
                raise ValueError(f"the HOLD partition {key} does not match its record")
            mask = arrays.get("mask_" + calibration_id)
        if not (isinstance(mask, np.ndarray) and mask.dtype == np.uint32 and mask.shape == (rows, H)):
            raise ValueError(f"the HOLD partition {key} lacks a complete ({rows}, {H}) uint32 mask")
        telemetry = selection_telemetry(mask, K, h)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        raise PartitionMismatch(f"the committed HOLD mask of {calibration_id} in {key} does not verify") from exc
    return {"role": "HOLD_NULL", "setup_id": sid, "calibration_id": calibration_id, "axis_pcs": list(axis_pcs),
            "hold_phase_digest": hold["phase_digest"], "hold_payload_sha256": sha, "telemetry": telemetry}


def _masked_alt_paths(mask_bits, projection, fields, daily):
    if not (isinstance(projection, dict) and {"q", "beta", "C0", "oracle_basis"} <= set(projection)):
        raise ValueError("projection must be a dict carrying q, beta, C0 and oracle_basis")
    basis = projection["oracle_basis"]
    if not (isinstance(basis, str) and basis in INFO_BASES):
        raise ValueError(f"oracle_basis must be one of {INFO_BASES}, got {basis!r}")
    mask = np.asarray(mask_bits)
    if mask.dtype != np.uint32 or mask.ndim != 2 or min(mask.shape) == 0:
        raise ValueError(f"mask_bits must be a nonempty (n, H) uint32 array, got {mask.dtype} of shape {mask.shape}")
    q, beta, C0 = (_real_array(projection[k], k, 2) for k in ("q", "beta", "C0"))
    n, K = q.shape
    if not (1 <= K <= 32 and beta.shape == q.shape and C0.shape == (K, K) and mask.shape[0] == n):
        raise ValueError(f"shapes disagree: mask {mask.shape}, q {q.shape}, beta {beta.shape}, C0 {C0.shape}")
    if not (mask != 0).all() or ((mask.astype(np.uint64) >> np.uint64(K)) != 0).any():
        raise ValueError(f"every mask word must be nonzero with bits below K={K}")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        coherent = bool((q >= 0).all() and np.allclose(q, 0.5 * beta * beta, rtol=1e-10, atol=1e-12))
    if not coherent:
        raise ValueError("q must be nonnegative and equal 0.5*beta**2 up to float64 roundoff")
    if not np.array_equal(C0, C0.T):
        raise ValueError("C0 must be symmetric")
    try:
        np.linalg.cholesky(C0)
    except np.linalg.LinAlgError as err:
        raise ValueError("C0 must be numerically positive definite") from err
    exact = basis == INFO_BASES[0]
    if exact and not np.abs(C0 - np.eye(K)).max() <= 1e-12:
        raise ValueError(f"{basis} requires C0 numerically equal to the identity")
    H, supports, out = mask.shape[1], {}, np.empty((len(fields), n), dtype=np.float64)
    for i in range(n):
        seen, days = {}, []
        for word in mask[i].tolist():
            if word not in seen:
                if word not in supports:
                    supports[word] = np.array([j for j in range(K) if (word >> j) & 1], dtype=np.intp)
                S = supports[word]
                surrogate = math.fsum(q[i, S].tolist())
                try:
                    joint = pdb.kl_mean(beta[i, S], C0[np.ix_(S, S)])
                except np.linalg.LinAlgError as exc:
                    raise ValueError(f"joint information failed on path {i}") from exc
                valid = math.isfinite(surrogate) and math.isfinite(joint) and surrogate >= 0 and joint >= 0
                if not (valid and (joint > 0 or not beta[i, S].any())):
                    raise ValueError(f"information on path {i}, mask word {word} is not finite and valid")
                seen[word] = daily(len(S), surrogate, joint)
            days.append(seen[word])
        for k, column in enumerate(zip(*days)):
            try:
                out[k, i] = math.fsum(column) / H
            except OverflowError:
                scale = max(column)
                out[k, i] = math.fsum(x / scale for x in column) / H * scale
    if not np.isfinite(out).all():
        raise ValueError(f"path means of {', '.join(fields)} must be finite")
    return {"oracle_basis": basis, **{k: out[r].copy() for r, k in enumerate(fields)}}


def _prior_ratio(information, d, m2, e2):
    m1, e1 = math.frexp(information)
    try:
        return math.ldexp(2.0 * m1 / m2 / d, e1 - e2)
    except OverflowError as exc:
        raise ValueError(f"prior ratio 2*I/(|S|*s2_common) at |S|={d} is not representable in float64") from exc


def masked_alt_information(mask_bits, projection, gamma_M):
    """Return full-horizon per-path information and information-to-cost means for supplied ALT masks."""
    if isinstance(gamma_M, bool) or not isinstance(gamma_M, (int, float, np.integer, np.floating)):
        raise ValueError(f"gamma_M must be a real number, got {gamma_M!r}")
    gamma = float(gamma_M)
    if not (math.isfinite(gamma) and gamma > 1):
        raise ValueError(f"gamma_M must be finite and above 1, got {gamma_M!r}")
    costs = {}

    def daily(d, surrogate, joint):
        if d not in costs:
            cost = float(mixture_cost(d, gamma))
            if not (math.isfinite(cost) and cost > 0):
                raise ValueError(f"mixture cost for |S|={d} must be finite and positive, got {cost}")
            costs[d] = cost
        return surrogate, joint, surrogate / costs[d], joint / costs[d]

    return _masked_alt_paths(mask_bits, projection, ("I_surrogate", "I_joint", "vbar_surrogate", "vbar_joint"), daily)


def export_alt_selections(out_dir, staging, did, records):
    """Export committed ALT mask selection statistics to selections.csv and return its SHA-256."""
    out = Path(out_dir)
    if not out.is_dir():
        raise FileNotFoundError(f'out_dir does not exist: {out}')
    staging = Path(staging)
    staged_did, desc = _staged_design(staging)
    if staged_did != did:
        raise PartitionMismatch(f'staged design {staged_did!r} != {did!r}')
    supplied = dict(records)
    if 'FINAL' in supplied or len(supplied) != 6:
        raise PartitionMismatch('expected exactly the six non-FINAL phase records')
    committed, missing = _planned_progress(staging, did, desc, partition_plan(desc), None)
    if tuple(committed) != PHASES:
        raise PartitionMismatch(f'committed phases {tuple(committed)!r} != {PHASES!r}')
    if missing:
        raise PartitionMismatch(f'missing partition rows: {missing!r}')
    if supplied != committed:
        raise PartitionMismatch('supplied phase records do not match staging')
    verified = committed
    campaign = desc['campaign']
    params = desc['science']['parameters']
    alt = verified['ALT']
    trials = alt['derived']['trials']
    thresholds = verified['CAL']['derived']['thresholds']
    setup_rows = verified['SETUP']['derived']['setups']
    dev_rows = verified['DEV']['derived']['setups']
    frozen_n = desc['sizes']['ALT']
    H = params['H']
    rows = []
    loaded_setup = None
    frame = fit = None
    for part in alt['partitions']:
        key = list(part['key'])
        if len(key) != 6 or key[0] != 'ALT':
            raise PartitionMismatch(f'unexpected ALT partition key {key!r}')
        _, arm, N, fit_id, app, family = key
        sha, n, arrays = _verify_partition(staging, did, alt['upstream'], key)
        if sha != part['sha256']:
            raise PartitionMismatch(f'ALT partition {key!r} does not match its record')
        if n <= 0 or n != part['n_rows'] or n != frozen_n:
            raise PartitionMismatch(f'ALT partition {key!r} has {n} rows, expected {frozen_n}')
        setup = [arm, N, fit_id]
        name = pdb.canon(setup)
        sid = setup_rows[name]['applications'][app]['setup_id']
        trial = trials[pdb.canon(key)]
        if trial['setup_id'] != sid or trial['family'] != family:
            raise PartitionMismatch(f'ALT trial metadata does not match {key!r}')
        cids = list(trial['calibration_ids'])
        if not cids:
            continue
        if loaded_setup != name:
            frame = fit = None
            frame_key = ['frame', campaign, N]
            frame = _setup_cache(_verify_partition(staging, did, {}, frame_key)[2], frame_key)
            if arm == 'EXACT':
                fit = frame
            else:
                fit_key = ['fit', campaign, *setup]
                fit = _setup_cache(_verify_partition(staging, did, {}, fit_key)[2], fit_key)
            loaded_setup = name
        universe = setup_rows[name]['applications'][app]['universe']
        deltas = np.stack([
            np.asarray(direction_information(
                desc, frame, fit, setup, app,
                ('meta', campaign, *setup, 'ALT', family, i),
            )['delta'])
            for i in range(n)
        ])
        projection = projection_diagnostics(frame, fit, universe, deltas, arm)
        del deltas
        if projection['oracle_basis'] != trial['oracle_basis']:
            raise PartitionMismatch(f'oracle_basis mismatch for {key!r}')
        policies = dev_rows[name][app]['policies']
        for cid in cids:
            th = thresholds[cid]
            if th['setup_id'] != sid:
                raise PartitionMismatch(f'calibration {cid!r} is bound to another setup')
            bound = th.get('family')
            if bound is not None and bound != family:
                raise PartitionMismatch(f'calibration {cid!r} is bound to family {bound!r}')
            policy_id = th['policy_id']
            match = None
            for group in ('PRIMARY', 'GAMMA_M', 'S2_DEV'):
                for label, prow in (policies.get(group) or {}).items():
                    if prow.get('policy_id') == policy_id and prow.get('status') == 'RUNNABLE':
                        match = (group, label)
                        break
                if match is not None:
                    break
            if match is None:
                raise PartitionMismatch(f'policy {policy_id!r} not found for {name!r}/{app!r}')
            group, label = match
            gamma = float(params['gamma_M_sensitivity'] if group == 'GAMMA_M' else params['gamma_M'])
            mask = np.asarray(arrays['mask_' + cid])
            if mask.dtype != np.uint32 or mask.shape != (n, H):
                raise PartitionMismatch(f'mask_{cid} has unexpected shape or dtype')
            info = masked_alt_information(mask, projection, gamma)
            values, counts = np.unique(mask, return_counts=True)
            bits = np.array([bin(int(v)).count('1') for v in values], dtype=float)
            costs = np.array([float(mixture_cost(int(b), gamma)) for b in bits], dtype=float)
            total = float(counts.sum())
            rows.append({
                'design_id': did,
                'setup_id': sid,
                'application': app,
                'policy': label,
                'policy_id': policy_id,
                'calibration_id': cid,
                'family': family,
                'info_basis': projection['oracle_basis'],
                'metric_basis': 'ANALYTIC_PROXY',
                'gamma_M': gamma,
                'horizon': H,
                'n_alt': n,
                'alt_payload_sha256': sha,
                'd_mean': float((bits * counts).sum() / total),
                'I_mean': float(np.mean(info['I_surrogate'])),
                'M_mean': float((costs * counts).sum() / total),
                'V_bar': float(np.mean(info['vbar_surrogate'])),
                'I_joint_mean': float(np.mean(info['I_joint'])),
                'V_joint_bar': float(np.mean(info['vbar_joint'])),
            })
            del mask, info
        del arrays, projection
    columns = [
        'design_id', 'setup_id', 'application', 'policy', 'policy_id', 'calibration_id',
        'family', 'info_basis', 'metric_basis', 'gamma_M', 'horizon', 'n_alt',
        'alt_payload_sha256', 'd_mean', 'I_mean', 'M_mean', 'V_bar', 'I_joint_mean',
        'V_joint_bar',
    ]
    rows.sort(key=lambda r: (r['setup_id'], r['application'], r['family'], r['calibration_id']))
    df = pandas.DataFrame(rows, columns=columns)
    path = out / 'selections.csv'
    pipelines.save_fair_csv(df, path)
    return pdb.file_sha256(path)


def export_trial_summaries(out_dir, staging, did, records):
    """Write trials_summary.csv from committed HOLD/ALT first-hit payloads and return its SHA-256."""
    staging = Path(staging)
    staged_did, desc = _staged_design(staging)
    if staged_did != did:
        raise PartitionMismatch("trial summary design does not match the staged design")
    committed, missing = _planned_progress(staging, did, desc, partition_plan(desc), None)
    if missing or records != committed or tuple(committed) != PHASES:
        raise PartitionMismatch("trial summary records are incomplete or foreign")
    horizon = int(desc["science"]["parameters"]["H"])
    setups = committed["SETUP"]["derived"]["setups"]
    thresholds = committed["CAL"]["derived"]["thresholds"]
    null_checks = committed["HOLD"]["derived"]["null_checks"]
    trials = committed["ALT"]["derived"]["trials"]
    rows = []
    for role, prefix, width in (("HOLD", "HOLD_NULL", 5), ("ALT", "ALT", 6)):
        record = committed[role]
        allocated = role == "HOLD" and "allocation" in desc
        parts = record["partitions"]
        if allocated:
            parts = [{"key": list(key)} for key in dict.fromkeys(tuple(part["key"][:5]) for part in parts)]
        for part in parts:
            key = list(part["key"])
            if len(key) != width or key[0] != prefix:
                raise PartitionMismatch(f"unexpected {role} partition key {key!r}")
            setup_id = setups[pdb.canon(key[1:4])]["applications"][key[4]]["setup_id"]
            if role == "HOLD":
                cells = [cid for cid, check in null_checks.items() if check["setup_id"] == setup_id]
            else:
                cells = list(trials[pdb.canon(key)]["calibration_ids"])
            if allocated:
                held = _staged_hold_cells(staging, did, desc, committed, key, "first", cells)
            else:
                sha, n, arrays = _verify_partition(staging, did, record["upstream"], key)
                n = int(n)
                expected = (_expected_rows(desc, "HOLD", key, committed) if role == "HOLD"
                            else desc["sizes"]["ALT"])
                if sha != part["sha256"] or n != part["n_rows"] or n != expected:
                    raise PartitionMismatch(f"{role} partition {key!r} does not match its record")
                fields = {name for name in arrays if str(name).startswith("first_")}
                if fields != {"first_" + cid for cid in cells}:
                    raise PartitionMismatch(f"{role} partition {key!r} has unexpected first-hit fields")
                partition_key = pdb.canon(key)
            for cid in cells:
                if allocated:
                    cell = held[cid]
                    first, n = cell["values"], cell["paths"].size
                    partition_key = pdb.canon([block for block, _ in cell["blocks"]])
                    sha = hashlib.sha256(pdb.canon(cell["blocks"]).encode()).hexdigest()
                else:
                    first = np.asarray(arrays["first_" + cid])
                cal = thresholds.get(cid)
                check = null_checks.get(cid)
                if cal is None or check is None or n <= 0:
                    raise PartitionMismatch(f"{role} cell {cid!r} lacks calibration, null check or rows")
                family = check.get("family") if role == "HOLD" else key[5]
                if (
                    cal["setup_id"] != setup_id
                    or check["setup_id"] != setup_id
                    or check["policy_id"] != cal["policy_id"]
                    or check.get("family") != cal.get("family")
                    or cal.get("family") not in (None, family)
                ):
                    raise PartitionMismatch(f"{role} cell {cid!r} is not bound to partition {key!r}")
                if (
                    first.shape != (n,)
                    or not np.issubdtype(first.dtype, np.signedinteger)
                    or not np.all((first == -1) | ((first >= 1) & (first <= horizon)))
                ):
                    raise PartitionMismatch(f"{role} cell {cid!r} has an invalid first-hit vector")
                k = int(np.count_nonzero(first > 0))
                if role == "HOLD":
                    if check["n"] != n or check["k"] != k:
                        raise PartitionMismatch(f"HOLD cell {cid!r} null check does not match its vector")
                    rmst = None
                    median = None
                    null_lo, null_hi, null_status = check["lo"], check["hi"], check["status"]
                else:
                    rmst = float(np.where(first > 0, first, horizon).mean())
                    median = float(np.median(first[first > 0])) if k > 0 else None
                    null_lo = null_hi = null_status = None
                rows.append({
                    "design_id": did,
                    "role": prefix,
                    "setup_id": setup_id,
                    "application": key[4],
                    "family": family,
                    "policy_id": cal["policy_id"],
                    "calibration_id": cid,
                    "qualification": check.get("qualification"),
                    "partition_key": partition_key,
                    "partition_sha256": sha,
                    "horizon": horizon,
                    "n": n,
                    "k": k,
                    "n_censored": n - k,
                    "alarm_rate": k / n,
                    "rmst_h": rmst,
                    "median_detected_h": median,
                    "null_lo": null_lo,
                    "null_hi": null_hi,
                    "null_status": null_status,
                })
    rows.sort(key=lambda row: (row["role"], row["partition_key"], row["calibration_id"]))
    columns = [
        "design_id", "role", "setup_id", "application", "family", "policy_id",
        "calibration_id", "qualification", "partition_key", "partition_sha256",
        "horizon", "n", "k", "n_censored", "alarm_rate", "rmst_h", "median_detected_h",
        "null_lo", "null_hi", "null_status",
    ]
    path = Path(out_dir) / "trials_summary.csv"
    pipelines.save_fair_csv(pandas.DataFrame(rows, columns=columns), path)
    return pdb.file_sha256(path)


def masked_alt_prior_ratio(mask_bits, projection, s2_common):
    """Return full-horizon per-path means of daily 2*I/(|S|*s2_common) for supplied ALT masks."""
    if isinstance(s2_common, bool) or not isinstance(s2_common, (int, float, np.integer, np.floating)):
        raise ValueError(f"s2_common must be a real scalar, got {s2_common!r}")
    try:
        s2 = float(s2_common)
    except OverflowError as exc:
        raise ValueError(f"s2_common must be finite in float64, got {s2_common!r}") from exc
    if not (math.isfinite(s2) and s2 > 0):
        raise ValueError(f"s2_common must be finite and positive, got {s2_common!r}")
    m2, e2 = math.frexp(s2)

    def daily(d, surrogate, joint):
        return _prior_ratio(surrogate, d, m2, e2), _prior_ratio(joint, d, m2, e2)

    return _masked_alt_paths(mask_bits, projection, ("rho_surrogate", "rho_joint"), daily)


def oracle_mask_alignment(mask_bits, oracle_mask_bits, K):
    """Return per-path first exact match day with a static oracle mask and full-horizon mean daily Jaccard overlap."""
    if isinstance(K, bool) or not isinstance(K, (int, np.integer)) or not 1 <= K <= 32:
        raise ValueError(f"K must be an integer in 1..32, got {K!r}")
    mask, oracle = mask_bits, oracle_mask_bits
    for name, words in (("mask_bits", mask), ("oracle_mask_bits", oracle)):
        if not isinstance(words, np.ndarray) or words.dtype != np.uint32 or words.ndim != 2 or min(words.shape) == 0:
            got = f"{words.dtype} {words.shape}" if isinstance(words, np.ndarray) else type(words).__name__
            raise ValueError(f"{name} must be a nonempty (n, H) uint32 array, got {got}")
        if not (words != 0).all() or ((words.astype(np.uint64) >> np.uint64(K)) != 0).any():
            raise ValueError(f"every {name} word must be nonzero with bits below K={K}")
    if mask.shape != oracle.shape:
        raise ValueError(f"mask_bits {mask.shape} and oracle_mask_bits {oracle.shape} must share one shape")
    target = oracle[:, :1]
    if not (oracle == target).all():
        raise ValueError("oracle_mask_bits must hold one constant word per path over H")
    equal = mask == target
    first = np.where(equal.any(axis=1), equal.argmax(axis=1) + 1, -1).astype(np.int64)
    inter = np.bitwise_count(mask & target).astype(np.float64)
    union = np.bitwise_count(mask | target).astype(np.float64)
    H = mask.shape[1]
    jaccard = np.array([math.fsum(row) / H for row in (inter / union).tolist()], dtype=np.float64)
    return {"first_match": first, "jaccard_mean": jaccard}


def v_rmst_diagnostic(cells):
    """Return descriptive Spearman V/RMST correlations by setup and application across policy-family cells."""
    text = ("setup_id", "application", "policy_id", "family")
    if not isinstance(cells, (list, tuple)):
        raise ValueError("cells must be a list of row dictionaries")
    groups, keys = {}, set()
    for row in cells:
        if not (isinstance(row, dict) and all(isinstance(row.get(k), str) and row.get(k) for k in text)):
            raise ValueError(f"each cell needs nonempty text {text}, got {row!r}")
        values = []
        for name, low in (("vbar_h", 0.0), ("rmst_h", 1.0)):
            x = row.get(name)
            if (isinstance(x, bool) or not isinstance(x, (int, float, np.integer, np.floating))
                    or not math.isfinite(x) or x < low):
                raise ValueError(f"{name} must be finite and at least {low}, got {x!r}")
            values.append(float(x))
        key = tuple(row[k] for k in text)
        if key in keys:
            raise ValueError(f"repeated cell {key}")
        keys.add(key)
        groups.setdefault(key[:2], []).append((key[2:], *values))
    result = []
    for group in sorted(groups):
        rows, rho = sorted(groups[group]), None
        if len(rows) > 1:
            rv, rr = (scipy.stats.rankdata([r[c] for r in rows]).tolist() for c in (1, 2))
            mv, mr = math.fsum(rv) / len(rv), math.fsum(rr) / len(rr)
            sxy = math.fsum((a - mv) * (b - mr) for a, b in zip(rv, rr))
            sxx, syy = math.fsum((a - mv) ** 2 for a in rv), math.fsum((b - mr) ** 2 for b in rr)
            if sxx > 0 and syy > 0:
                rho = float(min(1.0, max(-1.0, sxy / math.sqrt(sxx * syy))))
        result.append({"setup_id": group[0], "application": group[1], "n_cells": len(rows), "spearman_rho": rho,
                       "status": "DESCRIPTIVE_V_RMST"})
    return result


def export_aggregates(out_dir, did, selections_sha, trials_sha, *, confirmation=None, descriptive_rows=()):
    """Write the descriptive V/RMST aggregate table from the verified FAIR payloads, plus the H1-H3 confirmatory rows when a verified report is supplied and any verified descriptive contrast rows, and return its SHA-256."""
    out_dir = Path(out_dir)
    if not (_is_sha(did) and _is_sha(selections_sha) and _is_sha(trials_sha)):
        raise ValueError("expected 64-hex SHA-256 inputs")
    keys = ["setup_id", "application", "policy_id", "calibration_id", "family"]
    specs = (
        ("selections.csv", selections_sha, ["design_id", *keys, "alt_payload_sha256"], ["V_bar", "V_joint_bar"]),
        ("trials_summary.csv", trials_sha, ["design_id", "role", *keys, "partition_sha256"], ["rmst_h"]),
    )
    payloads = []
    for name, sha, id_cols, value_cols in specs:
        data = (out_dir / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != sha:
            raise PartitionMismatch(f"{name} SHA-256 does not match the authorized input")
        payloads.append((name, data, id_cols, value_cols))
    frames = []
    for name, data, id_cols, value_cols in payloads:
        frame = pandas.read_csv(io.BytesIO(data), float_precision="round_trip", dtype={c: str for c in id_cols})
        missing = [c for c in id_cols + value_cols if c not in frame.columns]
        if missing:
            raise PartitionMismatch(f"{name} lacks columns {missing}")
        frame = frame[id_cols + value_cols]
        required = [c for c in id_cols if not (name == "trials_summary.csv" and c == "family")]
        if frame[required].isna().any().any() or (frame["design_id"] != did).any():
            raise PartitionMismatch(f"{name} has missing IDs or a foreign design_id")
        frames.append(frame)
    selections, trials = frames
    if not trials["role"].isin(["ALT", "HOLD_NULL"]).all():
        raise PartitionMismatch("trials_summary.csv has an unknown role")
    alt = trials[trials["role"] == "ALT"]
    if alt["family"].isna().any():
        raise PartitionMismatch("ALT rows missing family")
    if selections.duplicated(keys).any() or alt.duplicated(keys).any():
        raise PartitionMismatch("duplicate join keys")
    merged = selections.drop(columns=["design_id"]).merge(
        alt.drop(columns=["design_id", "role"]), on=keys, how="outer", indicator=True, validate="one_to_one"
    )
    if (merged["_merge"] != "both").any():
        raise PartitionMismatch("unmatched join keys")
    if (merged["alt_payload_sha256"] != merged["partition_sha256"]).any():
        raise PartitionMismatch("partition SHA-256 disagreement")
    records = merged.to_dict("records")

    def cells(column):
        return [
            {
                "setup_id": r["setup_id"],
                "application": r["application"],
                "policy_id": r["policy_id"],
                "family": r["family"],
                "vbar_h": float(r[column]),
                "rmst_h": float(r["rmst_h"]),
            }
            for r in records
        ]

    marginal = v_rmst_diagnostic(cells("V_bar"))
    joint = v_rmst_diagnostic(cells("V_joint_bar"))
    if len(marginal) != len(joint):
        raise PartitionMismatch("diagnostic groups disagree")
    rows = []
    for m_row, j_row in zip(marginal, joint):
        if (m_row["setup_id"], m_row["application"], m_row["n_cells"]) != (
            j_row["setup_id"], j_row["application"], j_row["n_cells"]
        ):
            raise PartitionMismatch("diagnostic groups disagree")
        rows.append(
            {
                "design_id": str(did),
                "setup_id": m_row["setup_id"],
                "application": m_row["application"],
                "n_cells": m_row["n_cells"],
                "spearman_rho": m_row["spearman_rho"],
                "spearman_joint_rho": j_row["spearman_rho"],
                "status": m_row["status"],
                "selections_sha256": selections_sha,
                "trials_sha256": trials_sha,
            }
        )
    columns = [
        "design_id", "setup_id", "application", "n_cells", "spearman_rho",
        "spearman_joint_rho", "status", "selections_sha256", "trials_sha256",
    ]
    dtype = None
    descriptive_rows = list(descriptive_rows)
    if confirmation is not None:
        claims = confirmation["claims"]
        if set(claims) != {"H1", "H2", "H3"}:
            raise ValueError("confirmatory report must contain exactly H1, H2 and H3")
    if confirmation is not None or descriptive_rows:
        columns = columns + [
            "record_kind", "hypothesis", "family", "alt_phase_digest",
            "bootstrap_key", "inference_json",
        ]
        for row in rows:
            row["record_kind"] = "DESCRIPTIVE_V_RMST"
        if confirmation is not None:
            bootstrap_keys = confirmation["bootstrap_keys"]
            for hypothesis in ("H1", "H2", "H3"):
                claim = claims[hypothesis]
                family = claim["family"]
                rows.append({
                    "design_id": did,
                    "setup_id": confirmation["setup_id"],
                    "application": "RESIDUAL",
                    "status": claim["status"],
                    "record_kind": "CONFIRMATORY",
                    "hypothesis": hypothesis,
                    "family": family,
                    "alt_phase_digest": confirmation["alt_phase_digest"],
                    "bootstrap_key": json.dumps(
                        bootstrap_keys[family], sort_keys=True, separators=(",", ":"), allow_nan=False,
                    ),
                    "inference_json": json.dumps(
                        claim, sort_keys=True, separators=(",", ":"), allow_nan=False,
                    ),
                })
        rows.extend(dict(row) for row in descriptive_rows)
        dtype = object
    path = out_dir / "aggregates.csv"
    pipelines.save_fair_csv(pandas.DataFrame(rows, columns=columns, dtype=dtype), path)
    return pdb.file_sha256(path)


def null_axis_bias_diagnostic(fitted_hold, exact_hold, projection, m):
    """Return per-axis HOLD frequencies, their fitted-to-exact ratios and the offline H0 bias terms."""
    frequencies, shapes, axes = [], [], []
    for name, hold in (("fitted_hold", fitted_hold), ("exact_hold", exact_hold)):
        if not (isinstance(hold, dict) and isinstance(hold.get("role"), str) and hold["role"] == "HOLD_NULL"
                and isinstance(hold.get("telemetry"), dict)):
            raise ValueError(f"{name} must be a HOLD_NULL reader output carrying a telemetry dict")
        tel, pcs = hold["telemetry"], hold.get("axis_pcs")
        counts = tel.get("axis_counts")
        n, H, K = (_count(tel.get(k), f"{name} telemetry {k}", 1) for k in ("n", "H", "K"))
        if K > 32:
            raise ValueError(f"{name} telemetry K must be at most 32, got {K}")
        if not (isinstance(pcs, (list, tuple)) and isinstance(counts, (list, tuple))
                and len(pcs) == len(counts) == K):
            raise ValueError(f"{name} needs exactly K = {K} axis_pcs and telemetry axis_counts")
        pcs = [_count(p, f"{name} axis PC", 1) for p in pcs]
        counts = [_count(a, f"{name} axis count") for a in counts]
        if len(set(pcs)) != K or max(counts) > n * H:
            raise ValueError(f"{name} needs distinct axis PCs and axis counts within [0, n*H = {n * H}]")
        frequencies.append([a / (n * H) for a in counts])
        shapes.append((H, K))
        axes.append(pcs)
    if shapes[0] != shapes[1] or axes[0] != axes[1]:
        raise ValueError(f"the holds disagree on (H, K) {shapes} or on the ordered axis_pcs {axes}")
    K = shapes[0][1]
    basis = projection.get("oracle_basis") if isinstance(projection, dict) else None
    if not (isinstance(basis, str) and basis in INFO_BASES[1:]):
        raise ValueError(f"projection must be a dict with oracle_basis in {INFO_BASES[1:]}, got {basis!r}")
    c, var0 = (_real_array(projection.get(k), k, 1) for k in ("c", "var0"))
    if not (c.shape == var0.shape == (K,) and (var0 >= 0.0).all()):
        raise ValueError(f"c and var0 must have length K = {K} and var0 must be nonnegative")
    m = _count(m, "m", 1)
    try:
        with np.errstate(over="raise", invalid="raise"):
            center_sq, variance_term = c * c, (var0 - 1.0) / m
        try:
            bias = null_score_bias(c, var0, m)
        except FloatingPointError:
            with np.errstate(over="raise", invalid="raise"):
                bias = 0.5 * center_sq + 0.5 * variance_term
    except (FloatingPointError, OverflowError) as exc:
        raise ValueError("the center, variance and bias terms must be finite in float64") from exc
    fitted, exact = frequencies
    return {"axis_pcs": axes[0], "oracle_basis": basis, "m": m, "fitted_frequency": fitted,
            "exact_frequency": exact, "fitted_over_exact": [f / e if e > 0 else None for f, e in zip(fitted, exact)],
            "center_sq": [float(x) for x in center_sq], "variance_term": [float(x) for x in variance_term],
            "bias": [float(x) for x in bias]}


def export_payloads(out_dir, staging, did, records, *, confirmation=None, descriptive_rows=()):
    """Write the five FAIR CSV payloads into the caller-owned sibling temp and return basename to SHA-256."""
    _, desc = _staged_design(Path(staging))
    hold_digest = records["HOLD"]["phase_digest"] if "allocation" in desc else None
    if confirmation is not None:
        if not isinstance(confirmation, dict):
            raise TypeError("confirmatory report must be a dict")
        if confirmation.get("design_id") != did:
            raise ValueError("confirmatory report design_id does not match the published design")
        if confirmation.get("alt_phase_digest") != records["ALT"]["phase_digest"]:
            raise ValueError("confirmatory report is not bound to the committed ALT phase digest")
        if hold_digest is not None and not all(
                claim.get("hold_phase_digest") == hold_digest for claim in confirmation["claims"].values()):
            raise ValueError("confirmatory report is not bound to the committed HOLD phase digest")
    descriptive_rows = tuple(descriptive_rows)
    for row in descriptive_rows:
        if not isinstance(row, dict):
            raise TypeError("descriptive row must be a dict")
        if row.get("design_id") != did:
            raise ValueError("descriptive row design_id does not match the published design")
        if row.get("alt_phase_digest") != records["ALT"]["phase_digest"]:
            raise ValueError("descriptive row is not bound to the committed ALT phase digest")
        if hold_digest is not None and json.loads(row["inference_json"]).get("hold_phase_digest") != hold_digest:
            raise ValueError("descriptive row is not bound to the committed HOLD phase digest")
    selections_sha = export_alt_selections(out_dir, staging, did, records)
    trials_sha = export_trial_summaries(out_dir, staging, did, records)
    calibration_sha = export_calibration(out_dir, did, records["CAL"])
    aggregates_sha = export_aggregates(
        out_dir, did, selections_sha, trials_sha, confirmation=confirmation,
        descriptive_rows=descriptive_rows,
    )
    columns = [
        "design_id",
        "phase",
        "setup_id",
        "policy_id",
        "calibration_id",
        "family",
        "status",
        "qualification",
    ]
    rows = []
    null_checks = records["HOLD"]["derived"]["null_checks"]
    for calibration_id in sorted(null_checks):
        check = null_checks[calibration_id]
        if check["status"] in ("NULL_FAILED", "NULL_INCONCLUSIVE"):
            rows.append(
                {
                    "design_id": did,
                    "phase": "HOLD",
                    "setup_id": check["setup_id"],
                    "policy_id": check["policy_id"],
                    "calibration_id": calibration_id,
                    "family": check.get("family"),
                    "status": check["status"],
                    "qualification": check.get("qualification"),
                }
            )
    if records["NULL_PLAN"]["derived"]["status"] == "PLAN_CAPPED_EXPECT_INCONCLUSIVE":
        rows.append(
            {
                "design_id": did,
                "phase": "NULL_PLAN",
                "setup_id": None,
                "policy_id": None,
                "calibration_id": None,
                "family": None,
                "status": "PLAN_CAPPED_EXPECT_INCONCLUSIVE",
                "qualification": None,
            }
        )
    issues_path = Path(out_dir) / "issues.csv"
    pipelines.save_fair_csv(pandas.DataFrame(rows, columns=columns), issues_path)
    return {
        "selections.csv": selections_sha,
        "trials_summary.csv": trials_sha,
        "calibration.csv": calibration_sha,
        "aggregates.csv": aggregates_sha,
        "issues.csv": pdb.file_sha256(issues_path),
    }


def load_config(path):
    """Read-only load of a UTF-8 YAML design configuration through yaml.safe_load."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main(argv=None):
    """CLI: python experiments/pca_info_online.py --mode smoke|pilot|full [--describe] [--jobs N] [--resume]."""
    ap = argparse.ArgumentParser(description="PCA-INFO-ONLINE design preflight and campaign runner (stream 32).")
    ap.add_argument("--config", type=Path, default=REPO_ROOT / "configs" / "pca_info_online.yaml",
                    help="YAML configuration (default configs/pca_info_online.yaml)")
    ap.add_argument("--mode", required=True, choices=MODES, help="campaign whose design is described or run")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes, at most envelope.jobs_max")
    ap.add_argument("--output-dir", type=Path, help="result directory")
    ap.add_argument("--log-dir", type=Path, help="log and staging directory")
    ap.add_argument("--resume", action="store_true", help="reuse staged records of this exact design")
    ap.add_argument("--describe", action="store_true", help="print the design_id and descriptor, then exit")
    args = ap.parse_args(argv)
    problems = pdb.check_env()
    if problems:
        print("environment refused: " + "; ".join(problems), file=sys.stderr)
        return 2
    try:
        cfg = load_config(args.config)
        desc = design_descriptor(cfg, args.mode)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"refused: invalid configuration {args.config}: {exc}", file=sys.stderr)
        return 2
    if args.describe:
        print(json.dumps({"design_id": design_id(desc), "descriptor": desc}, sort_keys=True, allow_nan=False))
        return 0
    try:
        grant = authorize(args.mode, cfg, desc, args.jobs)
    except AuthorizationRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    did = grant["design_id"]
    try:
        if args.output_dir:
            out = Path(args.output_dir)
        else:
            out = REPO_ROOT / "results" / "pca_info_online" / did[:16]
        if args.log_dir:
            log_dir = Path(args.log_dir)
        else:
            log_dir = REPO_ROOT / "logs" / "pca_info_online" / out.name
        if out.is_symlink():
            print(f"refused: output destination {out} is a symlink; nothing was run", file=sys.stderr)
            return 2
        populated = False
        if out.exists():
            if not out.is_dir():
                print(f"refused: output destination {out} is not a directory; nothing was run", file=sys.stderr)
                return 2
            if any(out.iterdir()):
                if not args.resume:
                    print(f"refused: output destination {out} is not empty; use --resume; nothing was run",
                          file=sys.stderr)
                    return 2
                if _claimed_design(out) != did:
                    print(f"refused: output destination {out} is not claimed by design {did}; nothing was run",
                          file=sys.stderr)
                    return 2
                populated = True
        plan = partition_plan(desc)
        staging = open_staging(log_dir, desc, args.resume)
        if populated:
            _planned_progress(staging, did, desc, plan, out)
        token = f"{os.getpid()}-{time.monotonic_ns()}"
        context = start_invocation(staging, grant, plan, token)
        context["jobs"] = args.jobs
        run_phases(cfg, args.mode, context)

        def checkpoint():
            cpu_total = charge_cpu(staging, context["token"], _cpu_now() - context["cpu_start"])
            require_budget(staging, grant, plan, context["started"], ("ALT", []))
            return cpu_total

        checkpoint()
        out.parent.mkdir(parents=True, exist_ok=True)

        def build(temp, design_id, records):
            if args.mode in ("pilot", "full"):
                bootstrap_cache = {}
                confirmation = None
                if args.mode == "full" and _plan_applies(desc):
                    confirmation = confirmatory_from_staging(
                        cfg, args.mode, dict(context, bootstrap_cache=bootstrap_cache),
                    )
                descriptive_rows = list(_staged_descriptive_rows(
                    staging, design_id, records, desc, bootstrap_cache, checkpoint,
                ))
                export_payloads(
                    temp, staging, design_id, records,
                    confirmation=confirmation, descriptive_rows=descriptive_rows,
                )
            else:
                export_payloads(temp, staging, design_id, records)
            cpu_total = checkpoint()
            peak_rss = pdb.peak_rss_bytes()
            return {
                "cpu_seconds_self_children_cumulative": float(cpu_total),
                "wall_seconds_elapsed": float(time.monotonic() - context["started"]),
                "jobs": int(args.jobs),
                "parent_peak_rss_bytes": None if peak_rss is None else int(peak_rss),
                "memory_peak_scope": "NOT_MEASURED",
            }

        status = finalize_planned(staging, out, grant, plan, build)
    except (AuthorizationRefused, OutputExists, StagingMismatch, PhaseOrderError, PartitionMismatch,
            ResourceBlocked, ValueError, OSError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    if status.get("status") != "PUBLISHED":
        print(f"refused: {args.mode} design {did} did not reach PUBLISHED (status {status.get('status')})",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
