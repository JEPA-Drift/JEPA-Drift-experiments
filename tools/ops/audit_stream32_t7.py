import argparse
import hashlib
import io
import itertools
import json
import math
import os
import re
import stat
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
from scipy.linalg import solve, solve_triangular
from scipy.optimize import brentq
from scipy.stats import binom, norm, spearmanr


ROOT = Path(__file__).resolve().parents[2]
PHASES = ("SETUP", "DEV", "CAL", "NULL_PLAN", "HOLD", "ALT")
ROLES = ("DEV_LIB", "DEV_NULL", "DEV_ALT", "CAL_NULL", "HOLD_NULL", "ALT")
UNIVERSES = {"RESIDUAL": (2, 21), "MARKET": (1, 20)}
SUPPORTS = {"F0_ISOTROPIC_RESIDUAL": None, "F1_TAIL_RESIDUAL": (18, 19, 20, 21),
            "F2_STRUCTURED_RESIDUAL": (3, 9, 17, 21), "F_HEAD_RESIDUAL": (2, 3, 4, 5), "F3_MARKET": (1,)}
DEV_FAMILIES = tuple(SUPPORTS)[:-1]
STATIC = {"FULL_K": "FULL_K", "FIXED_EIGENMEAN_PREFIX": "EIGENMEAN", "CPV90": "CPV90",
          "RESIDUAL_CPV90": "RESIDUAL_CPV90", "FIXED_DEV_PREFIX": "DEV_PREFIX", "FIXED_EXANTE_QBAR_MIX": "EXANTE"}
ADAPTIVE = {f"ONLINE_{order}_{cost}_W{window}": ("ONLINE", order, cost, window)
            for order, cost, window in itertools.product(("INFO", "PREFIX"), ("MIX", "AFF"), (32, 128))}
ADAPTIVE.update({f"ORACLE_{order}_{cost}": ("ORACLE", order, cost, None)
                 for order, cost in itertools.product(("INFO", "PREFIX"), ("MIX", "AFF"))})
REFERENCES = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128")
ORACLE_BASIS = "ORACLE_DIAGONAL_GAUSSIAN_PROXY"
ORACLE_CAL = "NON_DEPLOYABLE_ORACLE_CALIBRATION"
CAL_RULE = "predictive_exchangeable_rank_v2"
PRIOR = "ISOTROPIC_ZERO_MEAN_GAUSSIAN"
CSV_NAMES = {"aggregates.csv", "calibration.csv", "issues.csv", "selections.csv", "trials_summary.csv"}
MAX_METADATA = 50 << 20
SCHEMA = "stream32-t7-audit/1"
RTOL, ATOL = 5e-10, 1e-11
REPLAY_INDEX = 0
CODE_FILES = {"experiments/pca_info_online.py", "experiments/pca_drift_benchmark.py"} | {
    "jepadrift/" + name + ".py" for name in (
        "floors", "injection", "sim", "pipelines", "monitors/calibration", "monitors/cusum", "monitors/streams",
        "representations/base", "representations/extract", "representations/pca", "stats/covariance", "stats/intervals")}


class AuditError(ValueError):
    pass


def _need(condition, message):
    if not condition:
        raise AuditError(message)


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _id(obj):
    return _sha(_canon(obj))[:16]


def _array_sha(*arrays):
    h = hashlib.sha256()
    for array in arrays:
        h.update(f"{array.shape}|".encode())
        h.update(np.ascontiguousarray(array, dtype=np.float64).tobytes())
    return h.hexdigest()


def _is_sha(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def _unique_pairs(items):
    out = dict(items)
    _need(len(items) == len(out), "duplicate JSON object key")
    return out


def _json(data, name, canonical=True):
    result = json.loads(data, object_pairs_hook=_unique_pairs)
    encoded = _canon(result) + b"\n"
    _need(not canonical or encoded == data, f"{name}: expected canonical JSON")
    return result


def _plain(path):
    path = Path(path).absolute()
    _need(".." not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)),
          f"symbolic link or noncanonical path at {path.name}")
    return path


def _read(path, limit=MAX_METADATA):
    path = _plain(path)
    try:
        info = path.lstat()
        _need(stat.S_ISREG(info.st_mode) and (limit is None or info.st_size <= limit),
              f"{path.name}: file type or size refused")
        data = path.read_bytes()
        _need(len(data) == info.st_size, f"{path.name}: size changed during read")
        return data
    except OSError as exc:
        raise AuditError(f"{path.name}: {exc.strerror}") from exc


def _same(expected, actual, label):
    if isinstance(expected, dict):
        _need(isinstance(actual, dict) and expected.keys() == actual.keys(), f"{label}: fields differ")
        for key, value in expected.items():
            _same(value, actual[key], f"{label}.{key}")
    elif isinstance(expected, (list, tuple)):
        _need(isinstance(actual, (list, tuple)) and len(expected) == len(actual), f"{label}: lengths differ")
        for index, (value, observed) in enumerate(zip(expected, actual)):
            _same(value, observed, f"{label}[{index}]")
    elif isinstance(expected, float):
        _need(type(actual) in (float, int) and math.isclose(expected, actual, rel_tol=RTOL, abs_tol=ATOL),
              f"{label}: expected {expected!r}, found {actual!r}")
    else:
        _need(expected == actual and type(expected) is type(actual), f"{label}: expected {expected!r}, found {actual!r}")


def _close(expected, actual, label):
    _need(np.shape(expected) == np.shape(actual) and np.allclose(expected, actual, rtol=RTOL, atol=ATOL),
          f"{label}: numerical replay differs")


def calibration(maxima, alpha):
    """Compute the GE rank boundary from every observed maximum."""
    maxima = np.asarray(maxima, dtype=np.float64)
    _need(maxima.ndim == 1 and np.isfinite(maxima).all() and 0 < alpha < 1, "invalid CAL maxima or alpha")
    n = maxima.size
    rank = math.floor(Fraction(str(alpha)) * (n + 1)) - 1
    _need(rank >= 0, f"no predictive rank for {n} maxima at alpha={alpha}")
    boundary = float(np.partition(maxima, n - rank - 1)[n - rank - 1])
    h = math.nextafter(boundary, math.inf)
    alarms = int(np.count_nonzero(maxima >= h))
    _need(math.isfinite(h) and alarms <= rank < np.count_nonzero(maxima >= boundary), "invalid GE boundary")
    return h, rank, alarms


def first_crossing(statistics, threshold):
    """Return the first GE hit in trading days or -1 for a censored path."""
    hits = np.flatnonzero(statistics >= threshold)
    return int(hits[0]) + 1 if hits.size else -1


def clopper_pearson(k, n, tail):
    """Invert the two binomial tail probabilities separately."""
    _need(0 <= k <= n and n > 0 and 0 < tail < 0.5, "invalid Clopper-Pearson inputs")
    low = 0.0 if k == 0 else brentq(lambda p: binom.sf(k - 1, n, p) - tail, 0, 1, xtol=1e-15)
    high = 1.0 if k == n else brentq(lambda p: binom.cdf(k, n, p) - tail, 0, 1, xtol=1e-15)
    return float(low), float(high)


def tango(b, c, n, tail):
    """Invert the paired score using the constrained likelihood in total discordance."""
    _need(b >= 0 and c >= 0 and 0 <= b + c <= n and n > 0 and 0 < tail < 0.5, "invalid Tango inputs")
    z = float(norm.isf(tail))
    if b == c == 0:
        bound = z * z / (n + z * z)
        return -bound, bound

    def term(count, probability):
        if not count:
            return 0.0
        return count / probability if probability > 0 else math.inf

    def score(delta):
        low = abs(delta)

        def derivative(s):
            return term(b, s + delta) + term(c, s - delta) - term(n - b - c, 1 - s)

        if derivative(low) <= 0:
            discordance = low
        elif derivative(1.0) >= 0:
            discordance = 1.0
        else:
            discordance = brentq(derivative, low, 1.0, xtol=1e-15)
        variance = (discordance - low) + low * (1 - low)
        return (b - c - n * delta) / math.sqrt(n * variance)

    estimate = (b - c) / n
    left, right = math.nextafter(-1.0, 0), math.nextafter(1.0, 0)
    low = -1.0 if estimate == -1 or score(left) <= z else brentq(
        lambda delta: score(delta) - z, left, min(estimate, right), xtol=1e-15)
    high = 1.0 if estimate == 1 or score(right) >= -z else brentq(
        lambda delta: score(delta) + z, max(estimate, left), right, xtol=1e-15)
    return float(low), float(high)


def _seed_words(seed, key):
    return [32, seed, *(zlib.crc32(item.encode()) if isinstance(item, str) else item
                        for item in (key[1], key[0], *key[2:]))]


def _rng(desc, key):
    return np.random.default_rng(np.random.SeedSequence(_seed_words(desc["seed"], key)))


def _seed_digest(desc):
    scope, sizes, campaign = desc["scope"], desc["sizes"], desc["campaign"]
    keys = [("frame", campaign, s[1]) for s in scope["setups"]]
    for setup in scope["setups"]:
        keys.append(("fit", campaign, *setup))
        keys.extend(("path", campaign, *setup, role, i) for role in ROLES[1:] for i in range(sizes[role]))
        for role in ("DEV_ALT", "CAL_NULL", "HOLD_NULL", "ALT"):
            families = DEV_FAMILIES if role == "DEV_ALT" else scope["families"]
            keys.extend(("meta", campaign, *setup, role, f, i) for f in families for i in range(sizes[role]))
        keys.extend(("devlib", campaign, *setup, f, i) for f in DEV_FAMILIES for i in range(sizes["DEV_LIB"]))
        keys.extend(("boot", campaign, *setup, app, f) for app in scope["applications"] for f in scope["families"])
    labels = {item for key in keys for item in key if isinstance(item, str)}
    words = [tuple(_seed_words(desc["seed"], key)) for key in keys]
    _need(len({zlib.crc32(label.encode()) for label in labels}) == len(labels) and len(set(words)) == len(words),
          "seed labels or seed roles overlap")
    return _sha(_canon(sorted(words)))


def _app(family):
    return "MARKET" if family == "F3_MARKET" else "RESIDUAL"


def _design_plan(desc):
    scope, campaign, science = desc["scope"], desc["campaign"], desc["science"]
    _need(set(desc) == {"mode", "schema_version", "campaign", "science", "sizes", "scope", "seed", "null_plan",
                        "envelope", "code", "environment", "seed_plan_sha256", "spectrum_sha"},
          "expected unallocated T7 design descriptor")
    _need(desc["schema_version"] == "pca_info_online/1" and desc["mode"] in ("pilot", "full", "smoke")
          and campaign == desc["mode"].upper() and desc["null_plan"] is None
          and science["phi"]["setup"] not in scope["setups"], "T7 requires an inapplicable NULL_PLAN and phi")
    members = {"setups": {("FITTED_LW_T7", 32, 0), ("FITTED_LW_T7", 239, 0)},
               "applications": set(UNIVERSES), "families": set(SUPPORTS), "policies": set(ADAPTIVE) | set(STATIC)}
    _need(set(scope) == set(members), "scope fields differ")
    for field, expected in members.items():
        actual = [tuple(s) for s in scope[field]] if field == "setups" else scope[field]
        _need(len(actual) == len(expected) and set(actual) == expected, f"unexpected T7 scope: {field}")
    p, sizes = science["parameters"], desc["sizes"]
    _need(science["applications"] == {k: list(v) for k, v in UNIVERSES.items()} and p["K"] == 20 and p["H"] == 250
          and p["I_star"] == 0.25 and p["alpha"] == 0.05 and p["T_fit"] == 1000 and p["gamma_M"] == 504
          and p["primary_window"] == 128 and p["windows"] == [32, 128]
          and p["frame"] == "QR_FIRST_COLUMN_ONES" and p["affine"] == "AFF_OLS_1_16"
          and p["s2_rule"] == "2*ln(H/alpha)/(H*K)"
          and science["null_status"] == {"tail": 0.05, "eps_v": 0.01}, "T7 scientific constants disagree")
    _need(set(sizes) == set(ROLES) and all(type(n) is int and n > 0 for n in sizes.values())
          and set(science["dev"]["families"]) == set(DEV_FAMILIES) and science["dev"]["n_lib"] == sizes["DEV_LIB"]
          and type(science["bootstrap"]["B"]) is int and science["bootstrap"]["B"] > 0
          and type(desc["seed"]) is int and 0 <= desc["seed"] < 2 ** 32, "invalid frozen cohort sizes or seed")
    _need(desc["spectrum_sha"] == _sha(_canon(p["spectrum"])) and desc["seed_plan_sha256"] == _seed_digest(desc),
          "design spectrum or seed plan hash differs")
    setups, apps, families = scope["setups"], scope["applications"], scope["families"]
    plan = {
        "SETUP": [["frame", campaign, s[1]] for s in setups] + [["fit", campaign, *s] for s in setups],
        "DEV": [["DEV_NULL", campaign, *s] for s in setups] + [[r, campaign, *s, f] for s in setups
                 for r in ("DEV_LIB", "DEV_ALT") for f in DEV_FAMILIES],
        "CAL": [["CAL_NULL", campaign, *s, a] for s in setups for a in apps],
        "NULL_PLAN": [],
        "HOLD": [["HOLD_NULL", *s, a] for s in setups for a in apps],
        "ALT": [["ALT", *s, _app(f), f] for s in setups for f in families],
    }
    return {phase: sorted(keys, key=_canon) for phase, keys in plan.items()}


class _Inputs:
    def __init__(self, sealed=None):
        self.sha = {}
        self.sealed = sealed

    def read(self, group, root, name, limit=MAX_METADATA):
        data = _read(root / name, limit)
        label = f"{group}/{name}"
        digest = _sha(data)
        self.sha[label] = digest
        if self.sealed is not None:
            _need(self.sealed.get(label) == digest, f"sealed input differs: {label}")
        return data


class _Stages:
    def __init__(self, staging, inputs):
        self.root, self.inputs = _plain(staging), inputs
        design = _json(self.read("design.json"), "design.json")
        self.did, self.desc = design["design_id"], design["descriptor"]
        _need(set(design) == {"design_id", "descriptor"} and self.did == _sha(_canon(self.desc))
              and self.root.name == self.did[:16], "design identity differs")
        self.plan = _design_plan(self.desc)
        self.records, self.local = {}, {}
        _need(set(self.desc["code"]) == CODE_FILES, "unexpected producer code paths")
        for name, expected in sorted(self.desc["code"].items()):
            _need(_sha(inputs.read("source", ROOT, name)) == expected, f"producer SHA-256 differs for {name}")
        self.script_sha = _sha(inputs.read("source", ROOT, "tools/ops/audit_stream32_t7.py"))

    def read(self, name, limit=MAX_METADATA):
        return self.inputs.read("staging", self.root, name, limit)

    def phase(self, phase):
        name = f"phases/{phase}.json"
        record = _json(self.read(name), name)
        upstream = {name: value["phase_digest"] for name, value in self.records.items()}
        _need(set(record) == {"design_id", "phase", "upstream", "partitions", "derived", "phase_digest"}
              and record["phase"] == phase and record["design_id"] == self.did
              and record["upstream"] == upstream, f"{phase}: phase schema or lineage differs")
        rows = record["partitions"]
        _need([row["key"] for row in rows] == self.plan[phase], f"{phase}: partition plan differs")
        members = [[_canon(row["key"]).decode(), row["sha256"]] for row in rows]
        digest = _sha(_canon({"design_id": self.did, "phase": phase, "upstream": upstream,
                              "partitions": members, "derived": record["derived"]}))
        _need(record["phase_digest"] == digest, f"{phase}: phase digest differs")
        parts = {}
        for row in rows:
            key = row["key"]
            identity = {"design_id": self.did, "key": key, "upstream": upstream}
            fingerprint = _sha(_canon(identity))
            base = f"partitions/{fingerprint}"
            sidecar = _json(self.read(base + ".json"), base)
            payload = self.read(base + ".npz", limit=None)
            sha = _sha(payload)
            n = key[-2] if key[0] == "fit" else key[-1] if key[0] == "frame" else self.desc["sizes"][key[0]]
            _same({"key": key, "sha256": sha, "n_rows": n}, row, f"{phase} partition")
            _same({**identity, "fingerprint": fingerprint, "payload_sha256": sha, "n_rows": n}, sidecar, base)
            try:
                with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
                    _need(len(set(archive.files)) == len(archive.files), f"{base}: duplicate array")
                    arrays = {name: archive[name] for name in archive.files}
            except (OSError, ValueError, KeyError) as exc:
                raise AuditError(f"{base}: unreadable NPZ") from exc
            _need(arrays and all(a.ndim and a.shape[0] == n and a.dtype.kind in "fiu" and np.isfinite(a).all()
                                 for a in arrays.values()), f"{base}: array type, rows or finiteness differs")
            self.local[base + ".npz"] = {"status": "LOCAL_HASHED_ONLY", "sha256": sha}
            parts[tuple(key)] = arrays, sha
        self.records[phase] = record
        return record["derived"], parts


def _float_array(value, shape, name):
    _need(value.dtype == np.float64 and value.shape == shape, f"{name}: expected float64 shape {shape}")
    return value


def _null(desc, frame, key, rows):
    rng = _rng(desc, key)
    normal = rng.standard_normal((rows, frame["lam"].size))
    shared_scale = np.sqrt(5.0 / rng.chisquare(7, size=rows))
    return frame["mean"] + (normal * shared_scale[:, None] * np.sqrt(frame["lam"])) @ frame["V"].T


def _cols(app):
    lo, hi = UNIVERSES[app]
    return np.arange(lo - 1, hi)


def _weights(fit, cols):
    return fit["V"][:, cols] / np.sqrt(fit["lam"][cols])


def _deltas(desc, frame, family, directions):
    fixed, level = SUPPORTS[family], desc["science"]["parameters"]["I_star"]
    axes = _cols(_app(family)) if fixed is None else np.asarray(fixed) - 1
    amplitudes = directions * math.sqrt(2.0 * level)
    amplitudes /= np.linalg.norm(directions, axis=1, keepdims=True)
    return amplitudes @ (frame["V"][:, axes] * np.sqrt(frame["lam"][axes])).T


def _directions(desc, setup, frame, role, family, indexes):
    keys = (("devlib", desc["campaign"], *setup, family, i) if role == "DEV_LIB"
            else ("meta", desc["campaign"], *setup, role, family, i) for i in indexes)
    support = SUPPORTS[family]
    draws = [_rng(desc, key).standard_normal(20) if support is None else
             _rng(desc, key).choice([-1.0, 1.0], size=len(support)) for key in keys]
    return _deltas(desc, frame, family, np.array(draws, dtype=np.float64))


def _projection(frame, fit, cols, deltas):
    weights = _weights(fit, cols)
    loadings = (frame["V"] * np.sqrt(frame["lam"])).T @ weights
    return deltas @ weights, loadings.T @ loadings


def _quadratic(beta, covariance):
    return 0.5 * np.einsum("ij,ji->i", beta, solve(covariance, beta.T, assume_a="pos"))


def _scores(desc, setup, frame, fit, app, role, delta=None):
    key = ("path", desc["campaign"], *setup, role, REPLAY_INDEX)
    rows = _null(desc, frame, key, desc["science"]["parameters"]["H"])
    if delta is not None:
        rows += delta
    return (rows - fit["mean"]) @ _weights(fit, _cols(app))


def _head(desc, frame, fit):
    family = "F_HEAD_RESIDUAL"
    signs = list(itertools.product((-1, 1), repeat=4))
    deltas = _deltas(desc, frame, family, np.asarray(signs))
    beta, cov = _projection(frame, fit, _cols("RESIDUAL"), deltas)
    energetic = _quadratic(beta, cov)
    prefix = _quadratic(beta[:, :4], cov[:4, :4])
    _need(np.all(energetic > 0), "HEAD profile has no projected information")
    fractions = {"f_E": (prefix / energetic).tolist(),
                 "f_pop": (prefix / desc["science"]["parameters"]["I_star"]).tolist()}
    summary = {k: {"min": min(v), "max": max(v), "mean": math.fsum(v) / len(v)} for k, v in fractions.items()}
    return {"support": list(SUPPORTS[family]), "signs": [list(sign) for sign in signs],
            "I_E": energetic.tolist(), "I_P4": prefix.tolist(), "all_I_E_positive": True,
            **fractions, "summary": summary}


def _cutoff(values):
    return int(np.searchsorted(np.cumsum(values) / values.sum(), 0.9, side="left")) + 1


def _baselines(lam, app):
    universe = (_cols(app) + 1).tolist()
    local = lam[_cols(app)]
    exact = [Fraction(value) for value in local]
    count = sum(value * len(exact) >= sum(exact) for value in exact)
    k90 = _cutoff(lam)
    return {
        "FULL_K": {"status": "RUNNABLE", "pcs": universe},
        "FIXED_EIGENMEAN_PREFIX": {"status": "RUNNABLE", "pcs": universe[:count]},
        "CPV90": ({"status": "RUNNABLE", "pcs": universe[:k90], "k90": k90}
                  if app == "MARKET" and k90 <= len(universe)
                  else {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}),
        "RESIDUAL_CPV90": ({"status": "RUNNABLE", "pcs": universe[:_cutoff(local)]} if app == "RESIDUAL"
                           else {"status": "UNSUPPORTED", "pcs": None}),
    }


def _basis_checks(desc, setup, frame, fit):
    n = setup[1]
    for record in (frame, fit):
        _need(set(record) == {"V", "lam", "mean"}, "basis fields differ")
        for name, shape in (("V", (n, n)), ("lam", (n,)), ("mean", (n,))):
            _float_array(record[name], shape, name)
        _need((record["lam"] > 0).all() and (np.diff(record["lam"]) <= 0).all(), "invalid spectrum order")
        _close(np.eye(n), record["V"].T @ record["V"], "orthonormal basis")
    params = desc["science"]["parameters"]
    spectrum = params["spectrum"]
    expected = [spectrum["lambda_1"]] + [spectrum["floor"] + spectrum["scale"] * math.exp(-i / spectrum["decay"])
                                         for i in range(n - 1)]
    _close(expected, frame["lam"], "population spectrum")
    rng = _rng(desc, ("frame", desc["campaign"], n))
    population, upper = np.linalg.qr(np.column_stack((np.full(n, n ** -0.5), rng.standard_normal((n, n - 1)))))
    _close(population * np.sign(np.diag(upper)), frame["V"], "population QR")
    _need(not frame["mean"].any(), "nonzero population center")
    rows = _null(desc, frame, ("fit", desc["campaign"], *setup), params["T_fit"])
    center = rows.mean(axis=0)
    centered = rows - center
    cov = centered.T @ centered / len(rows)
    target = np.eye(n) * np.trace(cov) / n
    spread = np.square(cov - target).sum()
    row_norm2 = np.einsum("ij,ij->i", centered, centered)
    noise = (np.square(row_norm2).mean() - np.square(cov).sum()) / len(rows)
    shrinkage = min(noise / spread, 1.0) if spread else 0.0
    _close(center, fit["mean"], "FIT_NULL center")
    _close((1 - shrinkage) * cov + shrinkage * target, (fit["V"] * fit["lam"]) @ fit["V"].T, "FIT_NULL LW covariance")
    _need((fit["V"].sum(axis=0) >= -ATOL).all()
          and np.all(-np.diff(fit["lam"][:22]) / fit["lam"][:21] >= 1e-10), "fit eigenvector signs or gap differ")


def _setup(stages):
    derived, parts = stages.phase("SETUP")
    expected, models, by_app, heads = {}, {}, {}, {}
    campaign = stages.desc["campaign"]
    for setup_list in stages.desc["scope"]["setups"]:
        setup = tuple(setup_list)
        arm, n, fit_id = setup
        frame, _ = parts[("frame", campaign, n)]
        fit, _ = parts[("fit", campaign, *setup)]
        _basis_checks(stages.desc, setup, frame, fit)
        models[setup] = frame, fit
        basis, fit_sha = (_array_sha(record["V"], record["lam"], record["mean"]) for record in (frame, fit))
        apps = {}
        geom = _head(stages.desc, frame, fit)
        kappa = stages.desc["science"]["head"]["kappa_geo"]
        for app in stages.desc["scope"]["applications"]:
            universe = (_cols(app) + 1).tolist()
            sid = _id({"design_id": stages.did, "arm": arm, "N": n, "fit_id": fit_id, "application": app,
                       "universe_pcs": universe, "basis_sha": basis, "fit_hash": fit_sha})
            head = {"status": "NOT_APPLICABLE", "kappa_geo": None, "geometry": None}
            if app == "RESIDUAL":
                head = {"status": "GEOMETRY_ALIGNED" if geom["summary"]["f_E"]["min"] >= kappa
                        else "DESIGN_CONTROL_INCONCLUSIVE", "kappa_geo": kappa, "geometry": geom}
                heads[sid] = geom
            apps[app] = {"universe": universe, "setup_id": sid, "head": head, "baselines": _baselines(fit["lam"], app)}
            by_app[(*setup, app)] = apps[app]
        expected[_canon(setup).decode()] = {"design_id": stages.did, "setup": list(setup), "basis_sha": basis,
                                            "fit_hash": fit_sha, "information_basis": "GAUSSIAN_PROXY",
                                            "applications": apps}
    _same({"setups": expected}, derived, "SETUP metadata")
    return models, by_app, heads


def _costs(gamma):
    log = math.log(gamma)
    mix = np.array([brentq(lambda x: x - log - d * math.log1p(2 * x / d) / 2, log, 2 * log + 2 * d,
                           xtol=1e-14) / log for d in range(1, 21)])
    d = np.arange(1.0, 21.0)
    line = np.polynomial.polynomial.polyfit(d[:16], mix[:16], 1)
    return {"MIX": mix, "AFF": np.polynomial.polynomial.polyval(d, line)}


def _top(q, cost, order):
    axes = np.argsort(-q, kind="stable") if order == "INFO" else np.arange(q.size)
    depth = int(np.argmax(np.cumsum(q[axes]) / cost)) + 1
    return np.sort(axes[:depth])


def _mask_word(axes):
    return sum(1 << int(axis) for axis in axes)


def _masks(scores, label, subset, app, costs, oracle_q=None):
    if label in STATIC:
        return np.full(len(scores), _mask_word(np.array(subset) - UNIVERSES[app][0]), dtype=np.uint32)
    kind, order, cost, window = ADAPTIVE[label]
    if kind == "ORACLE":
        return np.full(len(scores), _mask_word(_top(oracle_q, costs[cost], order)), dtype=np.uint32)
    masks = [1]
    for end in range(1, len(scores)):
        history = scores[max(0, end - window):end]
        q = np.maximum(0, np.square(history.mean(axis=0)) - 1 / len(history)) / 2
        masks.append(_mask_word(_top(q, costs[cost], order)))
    return np.array(masks, dtype=np.uint32)


def _scan(scores, masks, s2):
    selected = ((masks[:, None] >> np.arange(scores.shape[1])) & 1).astype(bool)
    masked = np.where(selected, scores, 0.0)
    w = np.empty(len(scores))
    for end in range(1, len(scores) + 1):
        counts = np.cumsum(selected[end - 1::-1], axis=0)
        totals = np.cumsum(masked[end - 1::-1], axis=0)
        log_likelihood = (np.square(totals) / (1 / s2 + counts) - np.log1p(s2 * counts)) / 2
        w[end - 1] = np.max(log_likelihood.sum(axis=1))
    return w


def _policy_row(desc, app, label, baselines, d_dev, qbar, costs):
    params, dev = desc["science"]["parameters"], desc["science"]["dev"]
    kind, order, cost, window = ADAPTIVE.get(label, ("STATIC", None, None, None))
    subset_rule, pcs, status = STATIC.get(label), None, "RUNNABLE"
    if label in baselines:
        status, pcs = (baselines[label][k] for k in ("status", "pcs"))
    elif label == "FIXED_DEV_PREFIX":
        subset_rule = {"kind": "DEV_PREFIX", "d_grid": sorted(dev["d_grid"]), "criterion": dev["criterion"],
                       "ties": dev["ties"]}
        status, pcs = ("RUNNABLE", (_cols(app)[:d_dev] + 1).tolist()) if app == "RESIDUAL" else ("NOT_RUN", None)
    elif label == "FIXED_EXANTE_QBAR_MIX":
        order, cost = "INFO", "MIX"
        status, pcs = (("RUNNABLE", (_top(qbar, costs["MIX"], "INFO") + UNIVERSES[app][0]).tolist())
                       if app == "RESIDUAL" else ("UNSUPPORTED", None))
    else:
        subset_rule = "ONLINE_QHAT" if kind == "ONLINE" else "ORACLE_Q"
    recipe = {"kind": kind, "order": order, "cost": "AFF_OLS_1_16" if cost == "AFF" else cost,
              "gamma_M": float(params["gamma_M"]) if cost else None, "window": window,
              "fallback": "MIN_E" if kind == "ONLINE" else None, "ties": "SMALLEST_D_THEN_INDEX" if cost else None,
              "s2_rule": params["s2_rule"], "subset_rule": subset_rule}
    prior = 2 * math.log(params["H"] / params["alpha"]) / (params["H"] * params["K"])
    identity = {"policy_rule_id": _id(recipe), "subset": pcs, "prior": PRIOR, "s2": prior}
    return {"status": status, **identity, "policy_id": _id(identity) if status == "RUNNABLE" else None}


def _dev_scans(scores, depths, s2):
    n, horizon, width = scores.shape
    result = np.empty((n, horizon, len(depths)))
    depth_indexes = np.asarray(depths) - 1
    for start in range(0, n, 32):
        block = scores[start:start + 32]
        sums = np.concatenate((np.zeros((len(block), 1, width)), block.cumsum(axis=1)), axis=1)
        for end in range(1, horizon + 1):
            lengths = np.arange(end, 0, -1)[:, None]
            totals = sums[:, end:end + 1] - sums[:, :end]
            terms = np.square(totals) / (1 / s2 + lengths) - np.log1p(s2 * lengths)
            result[start:start + len(block), end - 1] = terms.cumsum(axis=2)[:, :, depth_indexes].max(axis=1) / 2
    return result


def _verify_dev_choices(desc, choices, null_sha, setup_id, baselines, costs, batches):
    params, sizes, dev = desc["science"]["parameters"], desc["sizes"], desc["science"]["dev"]
    candidates = choices["d_candidates"]
    depths = sorted(dev["d_grid"])
    _need(set(choices) == {"d_dev", "s2_dev", "qualification", "d_candidates", "s2_candidates"}
          and choices["qualification"] == "COMMON_NOMINAL_ALPHA_DEV" and choices["s2_dev"] is None
          and not choices["s2_candidates"] and [c["d"] for c in candidates] == depths,
          "unexpected DEV candidate grid or primary sensitivity")
    s2 = 2 * math.log(params["H"] / params["alpha"]) / (params["H"] * params["K"])
    null_maxima = _dev_scans(batches[None], depths, s2).max(axis=1)
    alt_stats = {f: _dev_scans(batches[f], depths, s2) for f in DEV_FAMILIES}
    ids = []
    for index, c in enumerate(candidates):
        _need(set(c) == {"d", "s2", "h", "r", "alarms", "rmst_by_family", "J"}, "DEV candidate fields differ")
        row = _policy_row(desc, "RESIDUAL", "FIXED_DEV_PREFIX", baselines, c["d"], None, costs)
        h, r, alarms = calibration(null_maxima[:, index], params["alpha"])
        rmst = {}
        for family, values in alt_stats.items():
            hits = values[:, :, index] >= h
            rmst[family] = float(np.where(hits.any(axis=1), hits.argmax(axis=1) + 1, params["H"]).mean())
        _same({"d": c["d"], "s2": s2, "h": h, "r": r, "alarms": alarms,
               "rmst_by_family": rmst, "J": math.fsum(rmst.values()) / len(rmst)}, c, "DEV candidate scores")
        ids.append(_id({"setup_id": setup_id, "dev_null_sha": null_sha, "policy_id": row["policy_id"], "rule": "GE",
                        "n": sizes["DEV_NULL"], "h": c["h"], "r": r, "alarms": c["alarms"]}))
    _need(choices["d_dev"] == min(candidates, key=lambda c: (c["J"], c["d"]))["d"], "DEV tie rule or choice differs")
    return sorted(ids)


def _dev(stages, models, apps, costs):
    derived, parts = stages.phase("DEV")
    desc = stages.desc
    sizes, campaign = desc["sizes"], desc["campaign"]
    expected, dev_ids, policies = {}, {}, {}
    for setup, (frame, fit) in models.items():
        key = _canon(setup).decode()
        expected[key] = {}
        resid = apps[(*setup, "RESIDUAL")]
        library_rows, q_rows = [], []
        for family in DEV_FAMILIES:
            lib_key = ("DEV_LIB", campaign, *setup, family)
            arrays, sha = parts[lib_key]
            n_lib = sizes["DEV_LIB"]
            _need(set(arrays) == {"q"}, "DEV_LIB arrays differ")
            q = _float_array(arrays["q"], (n_lib, 20), "DEV_LIB q")
            _need(np.all(q >= 0), "DEV_LIB q is negative")
            delta = _directions(desc, setup, frame, "DEV_LIB", family, [REPLAY_INDEX])[0]
            _close(np.square(delta @ _weights(fit, _cols("RESIDUAL"))) / 2, q[REPLAY_INDEX], "DEV_LIB proxy replay")
            q_rows.append(q.mean(axis=0))
            library_rows.append({"key": list(lib_key), "sha256": sha, "n_rows": n_lib})
        qbar = np.mean(q_rows, axis=0)
        library_rows.sort(key=lambda row: _canon(row["key"]))
        library_id = _id({"setup_id": resid["setup_id"], "partitions": [
            [_canon(row["key"]).decode(), row["sha256"]] for row in library_rows]})
        lib = {"setup_id": resid["setup_id"], "partitions": library_rows, "dev_library_id": library_id,
               "qbar": qbar.tolist(), "qbar_sha": _array_sha(qbar)}
        batches = {}
        for role, family in [("DEV_NULL", None), *(("DEV_ALT", f) for f in DEV_FAMILIES)]:
            score_key = (role, campaign, *setup) + ((family,) if family else ())
            arrays, _ = parts[score_key]
            h = desc["science"]["parameters"]["H"]
            _need(set(arrays) == {"Y"}, f"{role} arrays differ")
            scores = _float_array(arrays["Y"], (sizes[role], h, 20), role)
            delta = _directions(desc, setup, frame, role, family, [REPLAY_INDEX])[0] if family else None
            _close(_scores(desc, setup, frame, fit, "RESIDUAL", role, delta), scores[REPLAY_INDEX], f"{role} replay")
            batches[family] = scores
        choices = derived["setups"][key]["RESIDUAL"]["choices"]
        null_sha = parts[("DEV_NULL", campaign, *setup)][1]
        dev_cal_ids = _verify_dev_choices(desc, choices, null_sha, resid["setup_id"], resid["baselines"], costs, batches)
        for app in desc["scope"]["applications"]:
            setup_id = apps[(*setup, app)]["setup_id"]
            residual = app == "RESIDUAL"
            d_dev, cal_ids = (choices["d_dev"], dev_cal_ids) if residual else (None, [])
            identity = {"setup_id": setup_id, "dev_library_id": library_id if residual else None,
                        "qbar_sha": lib["qbar_sha"] if residual else None, "d_dev": d_dev, "s2_dev": None,
                        "dev_calibration_ids": cal_ids}
            dev_id = _id(identity)
            primary = {label: _policy_row(desc, app, label, apps[(*setup, app)]["baselines"], d_dev, qbar, costs)
                       for label in sorted(desc["scope"]["policies"])}
            policies[(*setup, app)] = primary
            expected[key][app] = {"applicability": "SELECTED" if residual else "NOT_APPLICABLE", "setup_id": setup_id,
                                  "library": lib if residual else None, "choices": choices if residual else None,
                                  "s2_status": None, "policies": {"PRIMARY": primary, "GAMMA_M": {}, "S2_DEV": {}},
                                  "dev_calibration_ids": cal_ids, "dev_id": dev_id}
            dev_ids[_canon((*setup, app)).decode()] = dev_id
    _same({"setups": expected, "dev_ids": dev_ids}, derived, "DEV metadata")
    return policies


def _replay(desc, group, role, cells, models, costs, *, injected=None):
    setup, app = group[:3], group[3]
    frame, fit = models[setup]
    scores = _scores(desc, setup, frame, fit, app, role, injected)
    q_by_family = {}
    for cid, cell in cells.items():
        label, family = cell["label"], cell.get("family")
        kind = ADAPTIVE[label][0] if label in ADAPTIVE else "STATIC"
        if family and family not in q_by_family:
            delta = injected if injected is not None else _directions(desc, setup, frame, role, family, [REPLAY_INDEX])[0]
            q_by_family[family] = np.square(delta @ _weights(fit, _cols(app))) / 2
        masks = _masks(scores, label, cell["subset"], app, costs, q_by_family.get(family))
        w = _scan(scores, masks, cell["s2"])
        threshold = cell.get("h")
        data = {"role": role, "dimension": setup[1], "application": app, "kind": kind,
                "family": family, "policy": label, "calibration_id": cid,
                "index": REPLAY_INDEX, "maximum": float(w.max()), "mask_sha256": _sha(masks.tobytes())}
        if threshold is not None:
            data["first_hit"] = first_crossing(w, threshold)
        yield data, masks


def _cal(stages, models, apps, policies, costs):
    derived, parts = stages.phase("CAL")
    n, alpha = stages.desc["sizes"]["CAL_NULL"], stages.desc["science"]["parameters"]["alpha"]
    groups, all_rows, replay = {}, {}, []
    for part, (arrays, _) in parts.items():
        group, app = part[2:], part[-1]
        calibrated, columns = {}, {}
        for label, row in policies[group].items():
            if row["status"] != "RUNNABLE":
                continue
            families = [f for f in stages.desc["scope"]["families"] if _app(f) == app] if label.startswith("ORACLE_") else [None]
            for family in families:
                column = "w_" + _id([row["policy_id"], family])
                _need(column in arrays, f"CAL absent expected maxima {label} {family}")
                maxima = _float_array(arrays[column], (n,), column)
                h, r, alarms = calibration(maxima, alpha)
                base = {"setup_id": apps[group]["setup_id"], "policy_id": row["policy_id"], "n_cal": n,
                        "maxima_sha256": _array_sha(maxima)}
                if family is not None:
                    base["family"] = family
                cid = _id({**base, "rule": "GE"})
                projection = {**base, "h": h, "r": r, "alarms": alarms}
                if family is not None:
                    projection["qualification"] = ORACLE_CAL
                _need(cid not in all_rows, "CAL identity repeats")
                all_rows[cid] = projection
                calibrated[cid] = {**projection, "label": label, "subset": row["subset"], "s2": row["s2"]}
                columns[cid] = column
        _need(set(arrays) == set(columns.values()), "CAL maxima fields differ from frozen policies")
        for data, _ in _replay(stages.desc, group, "CAL_NULL", calibrated, models, costs):
            observed = arrays[columns[data["calibration_id"]]][REPLAY_INDEX]
            _close(data["maximum"], observed, "CAL maximum replay")
            data["received_maximum"] = float(observed)
            replay.append(data)
        groups[group] = calibrated
    _need(_canon({"rule": CAL_RULE, "thresholds": all_rows}) == _canon(derived),
          "CAL thresholds differ from their raw maxima and GE nextafter boundaries")
    return groups, all_rows, replay


def _scan_arrays(arrays, cells, n, horizon, app, role):
    scans = {p + cid for cid in cells for p in ("first_", "mask_")}
    _need(set(arrays) == (scans | ({"I_joint"} if role == "ALT" else set())), f"{role}: scan columns differ")
    for cid, cell in cells.items():
        first, mask = arrays["first_" + cid], arrays["mask_" + cid]
        _need(first.dtype.kind == "i" and first.shape == (n,) and np.all((first == -1) | ((first >= 1) & (first <= horizon)))
              and mask.dtype == np.uint32 and mask.shape == (n, horizon) and np.all((mask > 0) & (mask < 1 << 20)),
              f"{role}: invalid first-hit vector or packed mask for {cid}")
        if cell["label"] in STATIC:
            _need(np.all(mask == _mask_word(np.asarray(cell["subset"]) - UNIVERSES[app][0])), f"{role}: static mask {cid}")
        elif cell.get("family") is not None:
            _need(np.all(mask == mask[:, :1]), f"{role}: varying oracle mask {cid}")
        else:
            _need(np.all(mask[:, 0] == 1), f"{role}: predictable first-day fallback {cid}")


def _match_scan_replay(arrays, data, masks):
    cid, index, role = data["calibration_id"], data["index"], data["role"]
    _need(np.array_equal(masks, arrays["mask_" + cid][index]), f"{role}: mask replay differs for {cid}")
    _need(data["first_hit"] == arrays["first_" + cid][index], f"{role}: first-hit replay differs for {cid}")


def _hold(stages, models, groups, costs):
    derived, parts = stages.phase("HOLD")
    n = stages.desc["sizes"]["HOLD_NULL"]
    science = stages.desc["science"]
    horizon, alpha = (science["parameters"][k] for k in ("H", "alpha"))
    tail, eps = (science["null_status"][k] for k in ("tail", "eps_v"))
    checks, holds, replay = {}, {}, []
    for part, (arrays, payload_sha) in parts.items():
        group, app = part[1:], part[-1]
        cells = groups[group]
        _scan_arrays(arrays, cells, n, horizon, app, "HOLD_NULL")
        for data, mask in _replay(stages.desc, group, "HOLD_NULL", cells, models, costs):
            _match_scan_replay(arrays, data, mask)
            replay.append(data)
        for cid, cell in cells.items():
            first = arrays["first_" + cid]
            k = int(np.count_nonzero(first >= 1))
            lo, hi = clopper_pearson(k, n, tail)
            boundary = alpha + eps
            status = "NULL_VALIDATED" if hi <= boundary else "NULL_FAILED" if lo > boundary else "NULL_INCONCLUSIVE"
            check = {"setup_id": cell["setup_id"], "policy_id": cell["policy_id"], "n": n, "k": k,
                     "lo": lo, "hi": hi, "status": status}
            if "family" in cell:
                check.update(family=cell["family"], qualification="NON_DEPLOYABLE")
            checks[cid] = check
            holds[cid] = first, part, payload_sha
    _same({"null_checks": checks}, derived, "HOLD null checks")
    return checks, holds, replay


def _pairs(cells):
    by_label = {cell["label"]: cid for cid, cell in cells.items()}
    baseline, prefix = (by_label[label] for label in REFERENCES)
    nonoracle = (cid for cid, cell in cells.items() if "family" not in cell)
    pairs = [(cid, ref) for cid in nonoracle for ref in (baseline, prefix) if cid != ref]
    return pairs + [(by_label["ORACLE_INFO_MIX"], baseline)]


def _fpr(cand, ref, oracle):
    a, b = cand > 0, ref > 0
    if oracle:
        return {"fpr_status": "ORACLE_SEPARATE", "candidate_fpr": float(a.mean()), "reference_fpr": float(b.mean())}
    count_b, count_c = int(np.count_nonzero(a & ~b)), int(np.count_nonzero(~a & b))
    tail = 0.025
    return {"fpr_status": "DESCRIPTIVE_NOMINAL", "fpr_interval_label": "TANGO_SCORE_ASYMPTOTIC", "tail": tail,
            "fpr_b": count_b, "fpr_c": count_c, "fpr_delta": (count_b - count_c) / len(a),
            "fpr_ci": list(tango(count_b, count_c, len(a), tail))}


def _preflight(staging, inputs):
    stages = _Stages(staging, inputs)
    costs = _costs(stages.desc["science"]["parameters"]["gamma_M"])
    models, apps, heads = _setup(stages)
    policies = _dev(stages, models, apps, costs)
    groups, thresholds, cal_replay = _cal(stages, models, apps, policies, costs)
    disposition, null_parts = stages.phase("NULL_PLAN")
    _need(disposition == {"status": "NOT_APPLICABLE"} and not null_parts, "NULL_PLAN is applicable")
    checks, holds, hold_replay = _hold(stages, models, groups, costs)
    fpr, plan = {}, []
    for _, *group, family in stages.plan["ALT"]:
        cells = {cid: cell for cid, cell in groups[tuple(group)].items() if cell.get("family") in (None, family)}
        plan.append({"key": ["ALT", *group, family], "index": REPLAY_INDEX, "calibration_ids": list(cells)})
        for cand, ref in _pairs(cells):
            key = f"{cand}:{ref}"
            if key not in fpr:
                fpr[key] = _fpr(holds[cand][0], holds[ref][0], "family" in cells[cand])
    if inputs.sealed is not None:
        _need(inputs.sha == inputs.sealed, "sealed input inventory differs")
    evidence = {"design_id": stages.did, "auditor_sha256": stages.script_sha, "phase_digests": {
        name: value["phase_digest"] for name, value in stages.records.items()},
        "inputs": dict(inputs.sha), "seed_plan_sha256": stages.desc["seed_plan_sha256"], "head": heads, "hold": checks,
        "calibration": thresholds, "null_plan": disposition["status"], "hold_contrasts": fpr,
        "alt_replay_plan": plan, "replay": cal_replay + hold_replay,
        "replay_tolerance": {"relative": RTOL, "absolute": ATOL, "exact": ["mask", "first_hit", "GE_boundary"]}}
    return evidence, stages, models, groups, holds, costs


def _durations(first, horizon):
    return np.where(first >= 1, first, horizon)


def _trial(stages, part, sha, cid, first, check):
    role, app = part[0], part[4]
    horizon = stages.desc["science"]["parameters"]["H"]
    n, k = len(first), int(np.count_nonzero(first > 0))
    row = {"design_id": stages.did, "role": role, "application": app, "setup_id": check["setup_id"],
           "calibration_id": cid, "policy_id": check["policy_id"], "qualification": check.get("qualification"),
           "partition_key": _canon(part).decode(), "partition_sha256": sha, "horizon": horizon,
           "n": n, "k": k, "n_censored": n - k, "alarm_rate": k / n,
           "family": check.get("family") if role == "HOLD_NULL" else part[5]}
    if role == "HOLD_NULL":
        return {**row, "rmst_h": None, "median_detected_h": None, "null_lo": check["lo"],
                "null_hi": check["hi"], "null_status": check["status"]}
    return {**row, "rmst_h": float(_durations(first, horizon).mean()),
            "median_detected_h": float(np.median(first[first > 0])) if k else None,
            "null_lo": None, "null_hi": None, "null_status": None}


def _mask_information(masks, beta, covariance, costs):
    horizon = masks.shape[1]
    flat = masks.ravel()
    order = np.argsort(flat, kind="stable")
    layout = flat[order]
    boundaries = np.r_[0, np.flatnonzero(layout[1:] != layout[:-1]) + 1, flat.size]
    total = np.zeros(6)
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        word = int(layout[start])
        cols = [axis for axis in range(beta.shape[1]) if word & (1 << axis)]
        paths, counts = np.unique(order[start:end] // horizon, return_counts=True)
        projected = beta[np.ix_(paths, cols)].T
        cholesky = np.linalg.cholesky(covariance[np.ix_(cols, cols)])
        z = solve_triangular(cholesky, projected, lower=True, check_finite=False)
        marginal = float(counts @ np.square(projected).sum(axis=0)) / 2
        joint = float(counts @ np.square(z).sum(axis=0)) / 2
        cost = costs[len(cols) - 1]
        visits = end - start
        total += (visits * len(cols), marginal, visits * cost, marginal / cost, joint, joint / cost)
    return dict(zip(("d_mean", "I_mean", "M_mean", "V_bar", "I_joint_mean", "V_joint_bar"),
                    (total / flat.size).tolist()))


def _contrast(desc, family, cells, cid, rid, trials, durations, indices, checks, fpr):
    candidate, reference = (durations[key] for key in (cid, rid))
    a, r = (trials[key]["rmst_h"] for key in (cid, rid))
    diff = (candidate - reference)[indices].mean(axis=1)
    result = {"family": family, "status": "PILOT_ONLY" if desc["mode"] == "pilot" else "DESCRIPTIVE_NOMINAL",
              "deff": 1, "coverage_claim": "NONE_FINITE", "rmst_interval_label": "BOOTSTRAP_PERCENTILE_APPROX",
              "n_hold": desc["sizes"]["HOLD_NULL"], "n_alt": len(candidate), "B": len(indices),
              "rmst_candidate": a, "rmst_reference": r, "rmst_difference": a - r,
              "rmst_ci": np.quantile(diff, [0.025, 0.975], method="linear").tolist(),
              "rmst_ratio_candidate_over_reference": a / r, **fpr}
    for role, key in (("candidate", cid), ("reference", rid)):
        cell, trial = cells[key], trials[key]
        result.update({f"{role}_{name}": value for name, value in {
            "calibration_id": key, "policy_id": cell["policy_id"], "policy_label": cell["label"], "variant": "PRIMARY",
            "calibration_family": cell.get("family"), "null_status": checks[key]["status"],
            "detected_fraction": trial["alarm_rate"], "censored_fraction": trial["n_censored"] / trial["n"],
            "median_given_detection": trial["median_detected_h"]}.items()})
    return result


def _alternatives(stages, pre, models, groups, costs):
    derived, parts = stages.phase("ALT")
    desc, checks = stages.desc, pre["hold"]
    params = desc["science"]["parameters"]
    n, horizon = desc["sizes"]["ALT"], params["H"]
    trials, expected, replay, selections, contrasts, bootstrap = [], {}, [], [], [], []
    for item in pre["alt_replay_plan"]:
        part = tuple(item["key"])
        group, family = part[1:5], part[5]
        setup, app = group[:3], group[3]
        cells = {cid: cell for cid, cell in groups[group].items() if cell.get("family") in (None, family)}
        _need(item["index"] == REPLAY_INDEX and item["calibration_ids"] == list(cells), "ALT replay coverage differs")
        arrays, sha = parts[part]
        _scan_arrays(arrays, cells, n, horizon, app, "ALT")
        setup_id = next(iter(cells.values()))["setup_id"]
        expected[_canon(part).decode()] = {"setup_id": setup_id, "family": family,
                                           "calibration_ids": list(cells), "oracle_basis": ORACLE_BASIS}
        frame, fit = models[setup]
        deltas = _directions(desc, setup, frame, "ALT", family, range(n))
        beta, covariance = _projection(frame, fit, _cols(app), deltas)
        _close(_quadratic(beta, covariance), _float_array(arrays["I_joint"], (n,), "ALT joint proxy"), "ALT joint proxy")
        for data, masks in _replay(desc, group, "ALT", cells, models, costs, injected=deltas[REPLAY_INDEX]):
            _match_scan_replay(arrays, data, masks)
            replay.append({**data, "family": family})
        per_family, durations = {}, {}
        for cid, cell in cells.items():
            first = arrays["first_" + cid]
            row = _trial(stages, part, sha, cid, first, checks[cid])
            durations[cid] = _durations(first, horizon)
            per_family[cid] = row
            trials.append(row)
            info = _mask_information(arrays["mask_" + cid], beta, covariance, costs["MIX"])
            selections.append({"design_id": stages.did, "setup_id": setup_id, "application": app, "family": family,
                               "calibration_id": cid, "policy": cell["label"], "policy_id": cell["policy_id"],
                               "info_basis": ORACLE_BASIS, "metric_basis": "ANALYTIC_PROXY", "gamma_M": params["gamma_M"],
                               "horizon": horizon, "n_alt": n, "alt_payload_sha256": sha, **info})
        if desc["mode"] != "smoke":
            key = ("boot", desc["campaign"], *part[1:])
            b = desc["science"]["bootstrap"]["B"]
            indices = _rng(desc, key).integers(0, n, size=(b, n), dtype=np.int64)
            bootstrap.append({"key": list(key), "shape": [b, n], "sha256": _sha(indices.tobytes())})
            for cid, rid in _pairs(cells):
                comparison = _contrast(desc, family, cells, cid, rid, per_family, durations, indices, checks,
                                       pre["hold_contrasts"][f"{cid}:{rid}"])
                contrasts.append({"design_id": stages.did, "setup_id": setup_id, "application": app,
                                  "family": family, "status": comparison["status"], "hypothesis": "",
                                  "record_kind": "DESCRIPTIVE_CONTRAST", "bootstrap_key": _canon(key).decode(),
                                  "alt_phase_digest": stages.records["ALT"]["phase_digest"], "inference_json": comparison,
                                  "n_cells": None, "spearman_rho": None, "spearman_joint_rho": None,
                                  "selections_sha256": None, "trials_sha256": None})
    _same({"trials": expected}, derived, "ALT trial metadata")
    return trials, selections, contrasts, replay, bootstrap


def _inventory(path, names, label):
    path = _plain(path)
    _need(path.is_dir() and {item.name for item in path.iterdir()} == names, f"{label} inventory differs")


def _publication(stages, publication, authority_root):
    inputs = stages.inputs
    pub = {name: inputs.read("publication", publication, name) for name in sorted(CSV_NAMES)}
    shas = {name: _sha(data) for name, data in pub.items()}
    manifest_data = inputs.read("publication", publication, "manifest.json")
    manifest = _json(manifest_data, "manifest.json")
    _json(inputs.read("publication", publication, "telemetry.json"), "telemetry.json")
    inputs.read("publication", publication, "summary.md")
    authority = manifest["authority"]
    ref = authority["go_reference"]
    _need(set(authority) == {"stage", "design_id", "go_reference"} and authority["stage"] == stages.desc["mode"]
          and authority["design_id"] == stages.did and isinstance(ref, dict) and set(ref) == {"path", "sha256"},
          "publication authority differs")
    rel = PurePosixPath(ref["path"])
    _need(not rel.is_absolute() and len(rel.parts) and ".." not in rel.parts and str(rel) == ref["path"],
          "publication GO path differs")
    go_bytes = inputs.read("authority", _plain(authority_root), ref["path"])
    _need(_sha(go_bytes) == ref["sha256"] and stages.did.encode() in go_bytes, "publication GO SHA or design differs")
    phase_digests = {name: record["phase_digest"] for name, record in stages.records.items()}
    real = {"design_id": stages.did, "phase_digests": {**phase_digests, "NULL_PLAN": "NOT_APPLICABLE"},
            "dev_ids": stages.records["DEV"]["derived"]["dev_ids"], "payloads": shas,
            "thresholds_sha": _sha(_canon(stages.records["CAL"]["derived"]["thresholds"])), "plan_id": None, "n_hold": None}
    realization_id = _sha(_canon(real))
    expected = {"status": "COMPLETE", "design_id": stages.did, "design_descriptor": stages.desc,
                "realization_id": realization_id, "realization_descriptor": real, "authority": authority,
                "payloads": {**stages.local, **{k: {"status": "PUBLISHED", "sha256": v} for k, v in shas.items()}}}
    _need(_canon(expected) == _canon(manifest), "manifest identity, classifications or SHA-256 differ")
    final = _json(stages.read("phases/FINAL.json"), "FINAL.json")
    _same({"status": "PUBLISHED", "design_id": stages.did, "realization_id": realization_id,
           "manifest_sha256": _sha(manifest_data)}, final, "FINAL")
    status = _json(stages.read("status.json"), "status.json")
    _same({"status": "PUBLISHED", "design_id": stages.did, "last_complete_phase": "ALT", "missing_partitions": []},
          status, "staging status")
    return pub, shas, final


def _csv(data, expected_columns, name):
    text = {col: str for col in expected_columns if col.endswith(("_id", "sha256", "digest")) or
            col in {"policy", "family", "hypothesis", "inference_json", "bootstrap_key", "partition_key", "record_kind"}}
    integers = {col: "Int64" for col in expected_columns if col in {
        "horizon", "n", "n_alt", "n_cal", "k", "r", "alarms", "n_censored", "n_cells"}}
    frame = pd.read_csv(io.BytesIO(data), float_precision="round_trip", dtype={**text, **integers},
                        na_values=["NaN"], keep_default_na=False)
    _need(set(frame.columns) == set(expected_columns), f"{name}: CSV columns differ")
    return frame.astype(object).where(frame.notna(), None).to_dict("records")


def _match_rows(expected, actual, key, name):
    reference, observed = ({key(row): row for row in rows} for rows in (expected, actual))
    _need(len(expected) == len(reference) == len(actual) == len(observed) and reference.keys() == observed.keys(),
          f"{name}: missing, duplicate or foreign rows")
    for key, row in reference.items():
        _same(row, observed[key], f"{name} row {key}")


def _rho(values, durations):
    if len(set(values)) <= 1 or len(set(durations)) <= 1:
        return None
    return float(spearmanr(values, durations).statistic)


def _verify_csvs(stages, pub, shas, pre, holds, alt, selections, contrasts):
    checks = pre["hold"]
    cal = [{"design_id": stages.did, "calibration_id": cid, "rule": CAL_RULE,
            "family": None, "qualification": None, **row} for cid, row in pre["calibration"].items()]
    actual = _csv(pub["calibration.csv"], cal[0], "calibration")
    _match_rows(cal, actual, lambda row: row["calibration_id"], "calibration")
    trials = [_trial(stages, part, sha, cid, first, checks[cid]) for cid, (first, part, sha) in holds.items()] + alt
    actual_trials = _csv(pub["trials_summary.csv"], trials[0], "trials_summary")
    _match_rows(trials, actual_trials, lambda row: (row["role"], row["partition_key"], row["calibration_id"]), "trials_summary")
    issue_columns = ("design_id", "phase", "setup_id", "policy_id", "calibration_id", "family", "status", "qualification")
    issues = [{"design_id": stages.did, "phase": "HOLD", "calibration_id": cid, "family": check.get("family"),
               "qualification": check.get("qualification"), **{k: check[k] for k in ("setup_id", "policy_id", "status")}}
              for cid, check in checks.items() if check["status"] in ("NULL_FAILED", "NULL_INCONCLUSIVE")]
    actual = _csv(pub["issues.csv"], issue_columns, "issues")
    _match_rows(issues, actual, lambda row: row["calibration_id"], "issues")
    actual_selections = _csv(pub["selections.csv"], selections[0], "selections")

    def alt_key(row):
        return tuple(row[k] for k in ("setup_id", "application", "family", "calibration_id"))

    _match_rows(selections, actual_selections, alt_key, "selections")
    rmst = {alt_key(row): row["rmst_h"] for row in alt}
    v_groups = {}
    for row in actual_selections:
        key = alt_key(row)
        v_groups.setdefault(key[:2], []).append((row["V_bar"], row["V_joint_bar"], rmst[key]))
    v_rmst = []
    for (setup_id, app), samples in sorted(v_groups.items()):
        values, joint, times = zip(*samples)
        v_rmst.append({"design_id": stages.did, "setup_id": setup_id, "application": app, "n_cells": len(samples),
                       "spearman_rho": _rho(values, times), "spearman_joint_rho": _rho(joint, times),
                       "status": "DESCRIPTIVE_V_RMST", "selections_sha256": shas["selections.csv"],
                       "trials_sha256": shas["trials_summary.csv"]})
    detail = bool(contrasts)
    diagnostic = [{**row, "record_kind": "DESCRIPTIVE_V_RMST", **dict.fromkeys(("hypothesis", "family",
                   "alt_phase_digest", "bootstrap_key", "inference_json"))} for row in v_rmst] if detail else v_rmst
    actual_aggregates = _csv(pub["aggregates.csv"], diagnostic[0], "aggregates")
    for row in actual_aggregates:
        if row.get("inference_json") is not None:
            row["inference_json"] = _json(row["inference_json"].encode(), "inference_json", canonical=False)

    def aggregate_key(row):
        infer = row.get("inference_json") or {}
        return (row["setup_id"], row["application"], row.get("family"),
                infer.get("candidate_calibration_id"), infer.get("reference_calibration_id"))

    _match_rows(diagnostic + contrasts, actual_aggregates, aggregate_key, "aggregates")
    hold_rows = {row["calibration_id"]: row for row in actual_trials if row["role"] == "HOLD_NULL"}
    marked = []
    for row in actual_aggregates:
        if row.get("record_kind") != "DESCRIPTIVE_CONTRAST":
            continue
        inference = row["inference_json"]
        joined = {k: row[k] for k in ("setup_id", "application", "family")}
        for role in ("candidate", "reference"):
            cid = inference[f"{role}_calibration_id"]
            hold_row = hold_rows[cid]
            _need((hold_row["design_id"], hold_row["setup_id"], hold_row["application"], hold_row["policy_id"],
                   hold_row["family"], hold_row["null_status"]) == (
                   stages.did, row["setup_id"], row["application"], inference[f"{role}_policy_id"],
                   inference[f"{role}_calibration_family"], inference[f"{role}_null_status"])
                  and hold_row["family"] in (None, row["family"]), "contrast does not join its HOLD cell")
            joined[f"{role}_calibration_id"], joined[f"{role}_null_status"] = cid, hold_row["null_status"]
        if "NULL_FAILED" in (joined["candidate_null_status"], joined["reference_null_status"]):
            marked.append({**joined, "analysis_status": "NULL_FAILED — NOT_CLAIMABLE"})
    return v_rmst, marked


def _report_path(report, *inputs):
    report = _plain(report)
    _need(report.parent.is_dir() and not report.exists() and all(not report.is_relative_to(_plain(path)) for path in inputs),
          "report must be new and outside the input trees")
    return report


def _write_report(report, stage, verdict, fields):
    data = _canon({"schema": SCHEMA, "pass": stage, "verdict": verdict, "utc": datetime.now(timezone.utc).isoformat(),
                   **fields}) + b"\n"
    with tempfile.NamedTemporaryFile(dir=report.parent, prefix=f".{report.name}.") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        os.link(handle.name, report)
    fd = os.open(report.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return _sha(data)


def pre_alt(staging, report):
    """Recompute SETUP through HOLD with a plan-derived allowlist and seal the evidence."""
    report = _report_path(report, staging)
    inputs = _Inputs()
    try:
        evidence, *_ = _preflight(staging, inputs)
    except (ValueError, KeyError, OSError, TypeError, IndexError, ArithmeticError) as exc:
        _write_report(report, "pre-alt", "DESIGN_REFUSED", {"reason": str(exc), "inputs": inputs.sha})
        raise AuditError(str(exc)) from exc
    return _write_report(report, "pre-alt", "PASS", evidence)


def _alt_pass(staging, publication, seal, seal_sha256, authority_root, inputs):
    seal = _plain(seal)
    _need(not any(seal.is_relative_to(_plain(path)) for path in (staging, publication)), "pre-ALT seal is inside an input tree")
    seal_bytes = _read(seal)
    _need(_is_sha(seal_sha256) and _sha(seal_bytes) == seal_sha256, "pre-ALT seal SHA-256 differs")
    sealed = _json(seal_bytes, "pre-ALT seal")
    _need(sealed.get("schema") == SCHEMA and sealed.get("pass") == "pre-alt" and sealed.get("verdict") == "PASS",
          "pre-ALT verdict is not PASS")
    stamp = datetime.fromisoformat(sealed["utc"])
    _need(stamp.tzinfo is not None and stamp.utcoffset() == timezone.utc.utcoffset(stamp), "pre-ALT timestamp differs")
    inputs.sealed = sealed["inputs"]
    pre, stages, models, groups, holds, costs = _preflight(staging, inputs)
    _need(_canon({k: v for k, v in sealed.items() if k not in ("schema", "pass", "verdict", "utc")}) == _canon(pre),
          "pre-ALT seal evidence differs")
    inputs.sealed = None

    _inventory(publication, {*CSV_NAMES, "manifest.json", "telemetry.json", "summary.md"}, "publication")
    _inventory(stages.root, {"design.json", "phases", "partitions", "resources.json", "status.json"}, "staging")
    _inventory(stages.root / "phases", {f"{p}.json" for p in (*PHASES, "FINAL")}, "phase")
    alt, selections, contrasts, replay, bootstrap = _alternatives(stages, pre, models, groups, costs)
    part_names = {Path(name).name for name in stages.local}
    _inventory(stages.root / "partitions", part_names | {Path(name).stem + ".json" for name in part_names}, "partition")
    _json(stages.read("resources.json"), "resources.json")
    pub, shas, final = _publication(stages, _plain(publication), authority_root)
    v_rmst, marks = _verify_csvs(stages, pub, shas, pre, holds, alt, selections, contrasts)
    return {**final, "auditor_sha256": stages.script_sha, "pre_alt_sha256": seal_sha256, "inputs": inputs.sha,
            "alt_replay": replay, "bootstrap": bootstrap, "v_rmst": v_rmst, "not_claimable": marks,
            "rmst_250": [{k: r[k] for k in ("calibration_id", "family", "n", "k", "n_censored", "rmst_h",
                                            "median_detected_h")} for r in alt],
            "contrasts": [r["inference_json"] for r in contrasts]}


def audit_alt(staging, publication, seal, seal_sha256, report, *, authority_root=ROOT):
    """Revalidate a trusted pre-ALT seal before opening any ALT or publication input."""
    report = _report_path(report, staging, publication)
    inputs = _Inputs()
    try:
        evidence = _alt_pass(staging, publication, seal, seal_sha256, authority_root, inputs)
    except (ValueError, KeyError, OSError, TypeError, IndexError, ArithmeticError) as exc:
        _write_report(report, "alt", "DESIGN_REFUSED", {"reason": str(exc), "pre_alt_sha256": seal_sha256,
                                                       "inputs": inputs.sha})
        raise AuditError(str(exc)) from exc
    return _write_report(report, "alt", "PASS", evidence)


def main(argv=None):
    """Run one explicit audit pass and print the SHA-256 of its report."""
    parser = argparse.ArgumentParser(description="Independent two-pass audit of Student-t7 Stream 32.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pre-alt", action="store_true")
    group.add_argument("--alt", action="store_true")
    parser.add_argument("--staging", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--publication", type=Path)
    parser.add_argument("--seal", type=Path)
    parser.add_argument("--seal-sha256")
    args = parser.parse_args(argv)
    alt_args = (args.publication, args.seal, args.seal_sha256)
    if (args.alt and not all(alt_args)) or (args.pre_alt and any(alt_args)):
        parser.error("--publication, --seal and --seal-sha256 are required together for --alt")
    try:
        paths = (args.staging, args.report, args.publication, args.seal)
        _need(all(_plain(path).is_relative_to(ROOT) for path in paths if path is not None), "paths must be in the worktree")
        digest = (pre_alt(args.staging, args.report) if args.pre_alt else
                  audit_alt(args.staging, args.publication, args.seal, args.seal_sha256, args.report))
    except (ValueError, KeyError, OSError, TypeError, IndexError, ArithmeticError) as exc:
        print(f"DESIGN_REFUSED: {exc}", file=sys.stderr)
        return 2
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
