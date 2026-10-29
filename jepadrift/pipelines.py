"""Cross-sectional pipelines (docs/sections/pipelines.md): PIPELINES[id] = (representation, stream_builder, detector,
calibration), fit on drift-free rows, one alarms row per monitored record.
`python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500` runs the D6 null check."""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import concurrent.futures
import hashlib
import json
import math
import multiprocessing
import zlib
from itertools import repeat
from pathlib import Path

import numpy as np
import pandas as pd

from jepadrift.data_loader import chars
from jepadrift.injection import symmetrize
from jepadrift.monitors import calibration, eprocess, lattice
from jepadrift.monitors.cusum import bilateral_delay_vec, cusum_max_bilateral_vec, cusum_trajectory_vec, strict_cusum_vec
from jepadrift.monitors.gamma import gamma_spectral, required_threshold
from jepadrift.monitors.streams import exact_sign_stream, fraction_stream
from jepadrift.representations.cross_section import DegreeZero
from jepadrift.representations.extract import DATASETS, _rows, segment_rows
from jepadrift.representations.ipca import IPCA
from jepadrift.representations.pca import PCAOrthogonal
from jepadrift.stats.covariance import ledoit_wolf

REPO_ROOT = Path(__file__).resolve().parents[1]
MASTER_SEED = 42
H_REF, H_DET, N_CAL, TARGET_FPR = 500, 750, 20000, 0.05
B_FLIPS, HALF_LIFE, STAKE_CAP = 2000, 20, 0.5
PIVOT_BETS = (0.1, 0.25, 0.5, 0.9)
SIGN_DELTA, ENERGY_DELTA = 0.1, 0.5
GAMMA = 20.0
CHUNK = 64
Z99 = 2.5758293035489004
COLUMNS = ["run_id", "pipeline", "dataset", "family", "seed", "tau_star", "alarm_index", "delay", "detected",
           "threshold", "reading"]
COMMON = {"pipeline": None, "reading": None, "dataset": "", "H": H_DET, "gamma": GAMMA, "alpha": None}
DEFAULTS = {
    "P2-C": {"reading": "bootstrap", "K": None, "H_ref": H_REF, "alpha": TARGET_FPR, "N_cal": N_CAL,
             "null_rows": "pre_monitor"},
    "P3-C": {"reading": "anytime-valid", "K": "mp", "mode": "factor", "shrinkage": "ledoit_wolf", "channels": "all",
             "mixture_s2": None},
    "P3-D": {"reading": "bootstrap", "K": "mp", "mode": "factor", "shrinkage": "ledoit_wolf", "alpha": TARGET_FPR,
             "N_cal": N_CAL, "null_rows": "calib"},
    "P3-CS": {"reading": "anytime-valid", "K": "mp", "mode": "factor", "b": "pc1", "variant": "b", "alpha": TARGET_FPR,
              "B": B_FLIPS, "null_rows": "pre_monitor"},
    "P4-C": {"reading": "anytime-valid", "K": "select", "cash_neutral": None, "channels": "all"},
    "P4-D": {"reading": "bootstrap", "K": "select", "cash_neutral": None, "alpha": TARGET_FPR, "N_cal": N_CAL,
             "null_rows": "calib"},
    "P7": {"reading": "anytime-valid"},
}
READINGS = {"P2-C": ("bootstrap", "anytime-valid"), "P3-C": ("anytime-valid", "exact"), "P3-D": ("bootstrap",),
            "P3-CS": ("anytime-valid", "randomization"), "P4-C": ("anytime-valid", "exact"), "P4-D": ("bootstrap",),
            "P7": ("anytime-valid",)}
CHAR_PIPELINES = ("P4-C", "P4-D")


def save_fair_csv(df: pd.DataFrame, path: Path):
    """
    Saves a DataFrame to CSV ensuring bit-for-bit reproducible floating point strings.
    """
    df.to_csv(path, float_format='%.17g', na_rep='NaN', lineterminator='\n', index=False)


def composition_for(K, K_max):
    """
    The three statements below are the delivered script's own, lines 186, 187
    and 190 of `run_real_experiment`, character for character. They are asserted
    against the witness source by `ast` at start-up AND re-executed from the
    witness text, so that this function cannot pass by resembling the witness.

    `% (2**32)` truncates a 128-bit digest to 32 bits and `default_rng` then
    expands it again. That is exactly the truncation the entropy migration
    exists to remove -- and it is kept here anyway, because what this draw
    selects is WHICH REAL SERIES ENTER THE PANEL, not a Monte-Carlo replicate.
    Re-keying it would draw a different set of equities and answer a different
    question from v87's.
    """
    cell_seed_base = int(hashlib.md5(f"real_{K}_{MASTER_SEED}".encode()).hexdigest(), 16) % (2**32)
    rng_diag = np.random.default_rng(cell_seed_base)
    assets_idx = rng_diag.choice(K_max, size=K, replace=False)
    return assets_idx


def split_rows(dates, splits, C=None):
    """Rows [start, stop) of the pretrain and calib segments of a splits.yaml dict, pre_monitor = [pretrain, calib end);
    characteristics C aligned with dates ride along under "C"."""
    pre, cal = segment_rows(dates, splits["segments"]["pretrain"]), segment_rows(dates, splits["segments"]["calib"])
    out = {"pretrain": pre, "calib": cal, "pre_monitor": (pre[0], cal[1]), "dates": np.asarray(dates, "datetime64[D]")}
    if C is not None:
        if len(C) != len(dates):
            raise ValueError(f"C must align with the {len(dates)} dates, got {len(C)} rows")
        out["C"] = C
    return out


def make_spec(pipeline, **kw):
    """Spec of one pipeline reading: COMMON and DEFAULTS[pipeline] updated by kw; ValueError on an unknown key or value."""
    if pipeline not in DEFAULTS:
        raise ValueError(f"unknown pipeline {pipeline!r}; expected one of {sorted(DEFAULTS)}")
    spec = {**COMMON, **DEFAULTS[pipeline], "pipeline": pipeline}
    unknown = sorted(set(kw) - set(spec) | ({"pipeline"} & set(kw)))
    if unknown:
        raise ValueError(f"{pipeline} does not accept: {', '.join(unknown)}")
    spec.update(kw)
    if spec["reading"] not in READINGS[pipeline]:
        raise ValueError(f"{pipeline} readings are {READINGS[pipeline]}, got {spec['reading']!r}")
    if not (spec["H"] == int(spec["H"]) >= 1 and spec["gamma"] > 1 and (spec["alpha"] is None or 0 < spec["alpha"] < 1)):
        raise ValueError("need an integer H >= 1, gamma > 1 and alpha in (0, 1) or None")
    spec["H"], spec["gamma"] = int(spec["H"]), float(spec["gamma"])
    if any(name in spec and not spec[name] == int(spec[name]) >= 1 for name in ("H_ref", "N_cal", "B")):
        raise ValueError("H_ref, N_cal and B must be integers >= 1")
    if spec.get("null_rows", "calib") not in ("pre_monitor", "calib"):
        raise ValueError(f"null_rows must be 'pre_monitor' or 'calib', got {spec['null_rows']!r}")
    if isinstance(spec.get("channels"), tuple):
        spec["channels"] = list(spec["channels"])
    if pipeline in ("P3-C", "P4-C") and spec["reading"] == "exact" and not (
            isinstance(spec["channels"], list) and len(spec["channels"]) == 1):
        raise ValueError("the exact reading monitors a single channel: channels=[k]")
    if spec.get("mixture_s2") is not None and not (spec["mixture_s2"] > 0 and spec["reading"] == "anytime-valid"):
        raise ValueError("mixture_s2 must be positive and belongs to the anytime-valid reading")
    if pipeline == "P3-CS" and (spec["variant"] not in ("a", "b") or (
            spec["reading"] == "randomization" and spec["variant"] != "a")):
        raise ValueError("P3-CS variant is 'a' or 'b'; the randomization reading belongs to variant 'a'")
    return spec


def run_id(spec):
    """First 16 hex digits of the SHA-256 of the canonical JSON of the spec."""
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]


def _panel(a, missing=False):
    if not isinstance(a, np.ndarray):
        raise TypeError(f"expected a returns panel as a numpy array, got {type(a).__name__}")
    if a.ndim != 2 or a.dtype != np.float64 or not (np.isfinite(a) | (missing & np.isnan(a))).all():
        raise ValueError(f"returns panel must be 2-D, float64 and {'without infinite values' if missing else 'finite'}")
    return a


def _coins(rec):
    return np.random.default_rng(np.random.SeedSequence([*(int(s) for s in rec["seed"]), 7]))


def _window(spec, state, data, rec, pre=0):
    tau, H = int(rec["tau_star"]), spec["H"]
    n = len(data["z_odd"]) if isinstance(data, dict) else len(data)
    if tau - pre < 0 or tau + H > n:
        raise ValueError(f"monitored rows [{tau - pre}, {tau + H}) leave the {n} rows of the data")
    if isinstance(data, dict):
        return {k: np.asarray(data[k][tau - pre:tau + H], dtype=np.float64) for k in ("z_odd", "z_even")}
    w = _panel(np.ascontiguousarray(data[tau - pre:tau + H]), getattr(state["rep"], "missing", False))
    return w if state["rep"] is None else state["rep"].transform_panel(w)


def fit_pipeline(spec, X_fit, splits, key=None):
    """Frozen state: representation pretrained (hook `pretrain`) on the pretrain rows and fitted on the calib rows of
    X_fit, with splits["C"] if present, then the reading's calibration on X_fit."""
    rep_fn, _, _, cal_fn = PIPELINES[spec["pipeline"]]
    rep = rep_fn(spec)
    X_fit = _panel(X_fit, getattr(rep, "missing", False))
    key = [7, int(run_id(spec)[:8], 16)] if key is None else [int(k) for k in key]
    start, stop = splits["calib"]
    state = {"rep": rep, "calib": [int(start), int(stop)], "n_assets": X_fit.shape[1]}
    if rep is not None:
        C = splits.get("C")
        if hasattr(rep, "pretrain"):
            a, b = splits["pretrain"]
            rep.pretrain(np.ascontiguousarray(X_fit[a:b]), _rows(C, a, b), splits["dates"][a:b])
        rep.fit(np.ascontiguousarray(X_fit[start:stop]), _rows(C, start, stop), splits["dates"][start:stop])
        state["channels"] = rep.channels
    state.update(cal_fn(spec, state, X_fit, splits, key))
    return state


def _row(spec, rid, rec, off, threshold):
    tau = int(rec["tau_star"])
    return {"run_id": rid, "pipeline": spec["pipeline"], "dataset": spec["dataset"], "family": rec["family"],
            "seed": "-".join(str(int(s)) for s in rec["seed"]), "tau_star": tau,
            "alarm_index": tau + off if off >= 0 else -1, "delay": float(off + 1) if off >= 0 else math.nan,
            "detected": off >= 0, "threshold": float(threshold), "reading": spec["reading"]}


def _run_chunk(spec, state, data, records):
    _, stream_fn, detect_fn, _ = PIPELINES[spec["pipeline"]]
    offsets = detect_fn(spec, state, np.stack([stream_fn(spec, state, data, rec) for rec in records]))
    rid = run_id(spec)
    return [_row(spec, rid, rec, int(off), state["threshold"]) for rec, off in zip(records, offsets)]


def run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None):
    """One alarms row per record of onset_info, monitored from tau_star on the panel or Z dict `data`."""
    records = list(onset_info)
    if state is None:
        if any(r["family"] != "H0" and int(r["tau_star"]) < splits["calib"][1] for r in records):
            raise ValueError("an injected onset precedes the end of the calib rows: fit on drift-free rows, pass state")
        state = fit_pipeline(spec, data, splits)
    size = CHUNK if n_jobs <= 1 else max(1, min(CHUNK, -(-len(records) // n_jobs)))
    chunks = [records[i:i + size] for i in range(0, len(records), size)]
    if n_jobs > 1 and len(chunks) > 1:
        with concurrent.futures.ProcessPoolExecutor(n_jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
            parts = list(pool.map(_run_chunk, repeat(spec), repeat(state), repeat(data), chunks))
    else:
        parts = [_run_chunk(spec, state, data, c) for c in chunks]
    rows = pd.DataFrame([row for part in parts for row in part], columns=COLUMNS)
    if out is not None:
        save_fair_csv(rows, Path(out))
    return rows


def sign_diagnostics(eps_K):
    """rho_sign_meas, K_eff_meas and K_eff_ana of eps_K (K, T) by the arithmetic of R15 run_diagnostics (l.889-902)."""
    eps_K_full = np.asarray(eps_K, dtype=np.float64)
    K = eps_K_full.shape[0]
    med_full = np.median(eps_K_full, axis=1, keepdims=True)
    eps_K_centered = eps_K_full - med_full
    x_diag = fraction_stream(eps_K_centered)
    rho_sign_meas = 0.0
    if K > 1:
        signs = np.sign(eps_K_centered)
        cm = np.corrcoef(signs)
        rho_sign_meas = cm[np.triu_indices(K, k=1)].mean()
    var_x = np.var(x_diag)
    K_eff_meas = 1.0 / (4.0 * var_x) if var_x > 0 else float('nan')
    K_eff_ana = K / (1.0 + (K - 1) * rho_sign_meas)
    return {"rho_sign": float(rho_sign_meas), "K_eff_meas": float(K_eff_meas), "K_eff_ana": float(K_eff_ana)}


def _rep_none(spec):
    return None


def _stream_p2c(spec, state, data, rec):
    cols = state["cols"]
    if spec["reading"] == "anytime-valid":
        return 2.0 * exact_sign_stream(_window(spec, state, data, rec)[:, cols], _coins(rec)).mean(axis=1)
    H_ref = spec["H_ref"]
    w = _window(spec, state, data, rec, pre=H_ref)[:, cols].T
    med = np.median(w[:, :H_ref], axis=1, keepdims=True)
    std = np.std(w[:, :H_ref], axis=1, keepdims=True)
    std[std == 0] = 1.0
    return fraction_stream((w - med) / std)[H_ref:]


def _detect_p2c(spec, state, x):
    if spec["reading"] == "anytime-valid":
        return eprocess.first_alarm(eprocess.log_edetector(x, "cusum"), spec["gamma"])
    return bilateral_delay_vec(x, 0.0, state["threshold"])


def _cal_p2c(spec, state, X_fit, splits, key):
    N = X_fit.shape[1]
    K = N if spec["K"] is None else spec["K"]
    if not (K == int(K) and 1 <= K <= N):
        raise ValueError(f"K must be an integer in [1, {N}], got {K}")
    cols = composition_for(int(K), N)
    start, stop = splits[spec["null_rows"]]
    eps = X_fit[start:stop, cols].T
    out = {"cols": [int(c) for c in cols], "diagnostics": sign_diagnostics(eps)}
    if spec["reading"] == "anytime-valid":
        return {**out, "threshold": spec["gamma"]}
    if spec["H_ref"] + spec["H"] > eps.shape[1]:
        raise ValueError(f"{eps.shape[1]} null rows cannot hold H_ref + H = {spec['H_ref'] + spec['H']} days")
    maxima = [calibration.worker_null_window_real(np.random.default_rng(np.random.SeedSequence(key + [1, i])), eps,
                                                  spec["H_ref"], spec["H"]) for i in range(spec["N_cal"])]
    return {**out, "threshold": calibration.bootstrap_threshold(maxima, spec["alpha"])}


def _rep_pca(spec):
    return PCAOrthogonal(K=spec["K"], mode=spec["mode"], shrinkage=spec["shrinkage"])


def _rep_ipca(spec):
    return IPCA(K=spec["K"], cash_neutral=spec["cash_neutral"])


def _columns(spec, state):
    named, ch = state["channels"], spec["channels"]
    every = sorted(c for cols in named.values() for c in cols)
    if ch == "all":
        return every
    if isinstance(ch, str):
        if ch not in named:
            raise ValueError(f"unknown channel set {ch!r}; the representation declares {sorted(named)}")
        return list(named[ch])
    if not ch or any(c not in every for c in ch):
        raise ValueError(f"channels must be columns of z_odd in {every}, got {ch}")
    return list(ch)


def _stream_signs(spec, state, data, rec):
    z = _window(spec, state, data, rec)["z_odd"][:, _columns(spec, state)]
    return 2.0 * exact_sign_stream(z, _coins(rec))


def _detect_p3c(spec, state, x):
    if spec["reading"] == "exact":
        return bilateral_delay_vec(x[..., 0] / 2.0, SIGN_DELTA, state["threshold"])
    if spec.get("mixture_s2") is None:
        return eprocess.first_alarm(eprocess.log_dictionary_edetector(x, "cusum"), spec["gamma"])
    residual = set(state["channels"]["residual"])
    cols = _columns(spec, state)
    res, mkt = [j for j, c in enumerate(cols) if c in residual], [j for j, c in enumerate(cols) if c not in residual]
    logs, weights = [], []
    if mkt:
        logs.append(eprocess.log_dictionary_edetector(x[..., mkt], "cusum"))
        weights.append(len(mkt))
    if res:
        logs.append(eprocess.log_subgaussian_mixture(x[..., res], spec["mixture_s2"]))
        weights.append(len(res))
    log_w = np.log(np.asarray(weights, dtype=np.float64) / sum(weights))
    return eprocess.first_alarm(np.logaddexp.reduce(np.stack(logs) + log_w[:, None, None], axis=0), spec["gamma"])


def cross_independence(signs, alpha=0.01):
    """Pairwise correlations of the sign streams in the columns of signs (T, D): two-sided p-values of sqrt(T) rho,
    Holm at family level alpha; passed iff no pair is rejected, i.e. min p > alpha / pairs (C-e1-holm-gate)."""
    s = np.asarray(signs, dtype=np.float64)
    se = 1.0 / math.sqrt(s.shape[0])
    rho = np.corrcoef(s, rowvar=False)[np.triu_indices(s.shape[1], 1)] if s.shape[1] > 1 else np.zeros(0)
    p = np.sort([math.erfc(abs(r) / se / math.sqrt(2.0)) for r in rho])
    over = next((i for i, q in enumerate(p) if q > alpha / (p.size - i)), int(p.size))
    return {"passed": over == 0, "max_abs_rho": float(np.abs(rho).max(initial=0.0)), "se": se, "pairs": int(rho.size),
            "over": int(over), "p_min": float(p[0]) if p.size else 1.0, "alpha": alpha}


def _cal_p3c(spec, state, X_fit, splits, key):
    cols = _columns(spec, state)
    if spec.get("mixture_s2") is not None:
        a, b = splits["calib"]
        res = [c for c in cols if c in state["channels"]["residual"]]
        gate = cross_independence(np.sign(state["rep"].transform_panel(np.ascontiguousarray(X_fit[a:b]))["z_odd"][:, res]))
        if not gate["passed"]:
            raise ValueError(f"cross-independence test failed: Holm rejects {gate['over']} of {gate['pairs']} residual "
                             f"pairs at family level {gate['alpha']} (min p = {gate['p_min']:.3g}): the sub-Gaussian "
                             f"mixture is not valid")
        return {"threshold": spec["gamma"], "gate": gate}
    if spec["reading"] != "exact":
        return {"threshold": spec["gamma"]}
    nominal, H = (spec["alpha"], spec["H"]) if spec["alpha"] is not None else (1.0 / spec["gamma"], None)
    sel = lattice.select_threshold(nominal, H=H, delta=SIGN_DELTA, sided=2)
    return {"threshold": sel["threshold"], "level": sel["level"], "lattice_units": sel["units"]}


def residual_energy(z_even, cols):
    """q_t = (sum over the residual columns of z_even - D) / sqrt(2 D), D = len(cols): the P3-D energy stream."""
    return (np.asarray(z_even, dtype=np.float64)[..., cols].sum(axis=-1) - len(cols)) / math.sqrt(2.0 * len(cols))


def _stream_p3d(spec, state, data, rec):
    return residual_energy(_window(spec, state, data, rec)["z_even"], state["channels"]["residual"])


def _detect_p3d(spec, state, q):
    return strict_cusum_vec(q, ENERGY_DELTA, state["threshold"])


def _cal_p3d(spec, state, X_fit, splits, key):
    start, stop = splits[spec["null_rows"]]
    cols, H = state["channels"]["residual"], spec["H"]
    q = residual_energy(state["rep"].transform_panel(np.ascontiguousarray(X_fit[start:stop]),
                                                     _rows(splits.get("C"), start, stop))["z_even"], cols)
    if H > len(q):
        raise ValueError(f"{len(q)} null rows cannot hold H = {H} days")
    lam_req = required_threshold(np.lib.stride_tricks.sliding_window_view(q, H), ENERGY_DELTA, spec["alpha"], "fpr", H)
    rng = np.random.default_rng(np.random.SeedSequence(key + [0]))
    iid = (rng.chisquare(len(cols), size=(spec["N_cal"], H)) - len(cols)) / math.sqrt(2.0 * len(cols))
    lam_iid = required_threshold(iid, ENERGY_DELTA, spec["alpha"], "fpr", H)
    return {"threshold": lam_req, "lam_iid": lam_iid, "gamma_op": lam_req / lam_iid, "gamma_spec": gamma_spectral(q)}


def stakes(norms, sigma_bar):
    """Stakes min(STAKE_CAP, 2 eta0_j sigma_bar / sigma_hat_{t|t-1}), sigma_hat an EWMA of ||Px|| restarted at sigma_bar."""
    a = 1.0 - 2.0 ** (-1.0 / HALF_LIFE)
    sig, s = np.empty(len(norms)), sigma_bar
    for t, v in enumerate(norms):  # ponytail: per-day EWMA loop, scipy.signal.lfilter if E1 runtime needs it
        sig[t] = s
        s = (1.0 - a) * s + a * v
    return np.minimum(STAKE_CAP, 2.0 * np.asarray(eprocess.EDETECTOR_ETA0)[None, :] * sigma_bar / sig[:, None])


def _rep_degree0(spec):
    return DegreeZero(b=spec["b"], K=spec["K"], mode=spec["mode"])


def _stream_p3cs(spec, state, data, rec):
    w = _window(spec, state, data, rec)
    if spec["variant"] == "a":
        return w["z_odd"] / state["rms"] if spec["reading"] == "randomization" else w["z_odd"]
    lam = stakes(w["z_even"][:, 0], state["sigma_bar"])
    x = 2.0 * exact_sign_stream(w["z_odd"], _coins(rec))
    return (2.0 * lam[:, None, :] * x[:, :, None]).reshape(len(x), -1)


def _detect_p3cs(spec, state, s):
    if spec["reading"] == "randomization":
        first = bilateral_delay_vec(np.moveaxis(s, -1, -2), 0.0, state["threshold"])
        return np.where((first >= 0).any(axis=-1), np.where(first >= 0, first, s.shape[1]).min(axis=-1), -1)
    if spec["variant"] == "a":
        bets = np.array([side * b for b in PIVOT_BETS for side in (1.0, -1.0)])
        return eprocess.first_alarm(eprocess.log_average_betting_eprocess(s, bets), spec["gamma"])
    return eprocess.first_alarm(eprocess.log_dictionary_edetector(s, "cusum", eta0=(STAKE_CAP / 2.0,)), spec["gamma"])


def _cal_p3cs(spec, state, X_fit, splits, key):
    a, b = splits["calib"]
    calib = state["rep"].transform_panel(np.ascontiguousarray(X_fit[a:b]))
    sigma_bar = float(np.median(calib["z_even"][:, 0]))
    if not sigma_bar > 0:
        raise ValueError("the calib median of ||Px|| must be positive")
    out = {"sigma_bar": sigma_bar, "c": (2.0 * np.asarray(eprocess.EDETECTOR_ETA0) * sigma_bar).tolist(),
           "rms": np.sqrt((calib["z_odd"] ** 2).mean(axis=0))}
    if spec["reading"] == "anytime-valid":
        return {**out, "threshold": spec["gamma"]}
    start, stop = splits[spec["null_rows"]]
    P = state["rep"].transform_panel(np.ascontiguousarray(X_fit[start:stop]))["z_odd"] / out["rms"]
    if spec["H"] > len(P):
        raise ValueError(f"{len(P)} null rows cannot hold H = {spec['H']} days")
    rng = np.random.default_rng(np.random.SeedSequence(key + [0]))
    maxima = [cusum_max_bilateral_vec(np.moveaxis(calibration.null_windows(P, spec["H"], min(CHUNK, spec["B"] - i), rng,
                                                                           flip=True), -1, -2), 0.0).max(axis=-1)
              for i in range(0, spec["B"], CHUNK)]
    return {**out, "threshold": calibration.bootstrap_threshold(np.concatenate(maxima), spec["alpha"])}


def _stream_p7(spec, state, data, rec):
    if "delta" not in rec:
        raise ValueError("P7 needs the applied drift of the record (rec['delta'], as returned by injection.inject)")
    x = _window(spec, state, data, rec)
    delta = np.asarray(rec["delta"], dtype=np.float64)
    d = np.broadcast_to(delta, x.shape) if delta.ndim == 1 else delta[:spec["H"]]
    if d.shape != x.shape:
        raise ValueError(f"delta must be (N,) or (>= H, N) for the {x.shape} monitored rows, got {delta.shape}")
    w = np.linalg.solve(state["sigma"], d.T).T
    return (w * x).sum(axis=1) - 0.5 * (w * d).sum(axis=1)


def _detect_p7(spec, state, llr):
    return eprocess.first_alarm(cusum_trajectory_vec(llr, 0.0), spec["gamma"])


def _cal_p7(spec, state, X_fit, splits, key):
    a, b = splits["calib"]
    return {"sigma": ledoit_wolf(np.ascontiguousarray(X_fit[a:b]))[0], "threshold": spec["gamma"]}


PIPELINES = {"P2-C": (_rep_none, _stream_p2c, _detect_p2c, _cal_p2c),
             "P3-C": (_rep_pca, _stream_signs, _detect_p3c, _cal_p3c),
             "P3-D": (_rep_pca, _stream_p3d, _detect_p3d, _cal_p3d),
             "P3-CS": (_rep_degree0, _stream_p3cs, _detect_p3cs, _cal_p3cs),
             "P4-C": (_rep_ipca, _stream_signs, _detect_p3c, _cal_p3c),
             "P4-D": (_rep_ipca, _stream_p3d, _detect_p3d, _cal_p3d),
             "P7": (_rep_none, _stream_p7, _detect_p7, _cal_p7)}


def horizon_gamma(H, alpha=TARGET_FPR):
    """gamma_H = H / alpha: an e-detector alarming at gamma_H has P_inf(alarm before H) <= H / gamma_H = alpha."""
    return H / alpha


def null_target(spec, state):
    """(p, kind, n_cal): the null guarantee of a reading as a false-alarm probability by the horizon H (pipelines.md)."""
    if spec["reading"] == "exact":
        if spec["alpha"] is not None:
            return state["level"], "=", None
        a, b, _ = lattice.lattice_steps(SIGN_DELTA)
        return lattice.exceedance(spec["H"], state["lattice_units"], a, b), "=", None
    if spec["reading"] == "bootstrap":
        return spec["alpha"], "~", spec["N_cal"] if spec["pipeline"] == "P2-C" else None
    if spec["reading"] == "randomization":
        return spec["alpha"], "~", spec["B"]
    if spec["pipeline"] == "P3-CS" and spec["variant"] == "a":
        return 1.0 / spec["gamma"], "<=", None
    return min(1.0, spec["H"] / spec["gamma"]), "<=", None


def summarize(rows, p, kind, n_cal=None):
    """False-alarm rate of null rows against the 99% binomial region of p (calibration noise 1/n_cal included)."""
    n, fpr = len(rows), float(rows["detected"].mean())
    half = Z99 * math.sqrt(p * (1.0 - p) * (1.0 / n + (1.0 / n_cal if n_cal else 0.0)))
    ok = fpr <= p + half if kind == "<=" else p - half <= fpr <= p + half
    return {"n": n, "fpr": fpr, "target": p, "kind": kind, "n_cal": n_cal, "lo": p - half, "hi": p + half, "ok": ok}


def null_specs(pipeline, dataset, n_channels):
    """Specs of the CLI null check, the targets of tests/test_pipelines.py (e-detectors at gamma = 20 H)."""
    kw, g = {"dataset": dataset}, 20.0 * H_DET
    if pipeline == "P2-C":
        return [make_spec("P2-C", **kw), make_spec("P2-C", reading="anytime-valid", gamma=g, **kw)]
    if pipeline in ("P3-C", "P4-C"):
        return [make_spec(pipeline, gamma=g, **kw)] + [make_spec(pipeline, reading="exact", channels=[k],
                                                                 alpha=TARGET_FPR, **kw) for k in range(n_channels)]
    if pipeline in ("P3-D", "P4-D"):
        return [make_spec(pipeline, **kw)]
    if pipeline == "P3-CS":
        return [make_spec("P3-CS", variant="a", **kw), make_spec("P3-CS", variant="a", reading="randomization", **kw),
                make_spec("P3-CS", gamma=g, **kw)]
    raise ValueError(f"{pipeline} has no null check (P7 needs a drift direction)")


def _null_block(spec, state, base, seed, lo, hi, pre):
    g = np.random.default_rng(np.random.SeedSequence(seed))
    start = int(g.integers(lo + pre, hi - spec["H"] + 1))
    eps = g.choice((-1.0, 1.0), size=pre + spec["H"])[:, None]
    span = slice(start - pre, start + spec["H"])
    return start, (base[span] * eps if state["rep"] is None else (base["z_odd"][span] * eps, base["z_even"][span]))


def null_check(specs, X, splits, reps, key):
    """D6 null check: one symmetrization of X fits, fresh ones are monitored; returns (alarms rows, summary per spec)."""
    if reps < 1:
        raise ValueError(f"reps must be >= 1, got {reps}")
    X, key = _panel(X, missing=True), [int(k) for k in key]
    X_fit, _ = symmetrize(X, np.random.default_rng(np.random.SeedSequence(key + [0])))
    frames, summary = [], []
    for i, spec in enumerate(specs):
        if spec["pipeline"] == "P7":
            raise ValueError("P7 needs a drift direction: it has no null check")
        state = fit_pipeline(spec, X_fit, splits, key=key + [1, i])
        pre = spec["H_ref"] if spec["pipeline"] == "P2-C" and spec["reading"] == "bootstrap" else 0
        lo, hi = splits[spec.get("null_rows", "pre_monitor")]
        if hi - lo < pre + spec["H"]:
            raise ValueError(f"the null rows [{lo}, {hi}) cannot hold {pre + spec['H']} days")
        base = X if state["rep"] is None else state["rep"].transform_panel(X, splits.get("C"))
        parts = []
        for c0 in range(0, reps, CHUNK):
            draws = [_null_block(spec, state, base, key + [2, i, r], lo, hi, pre)
                     for r in range(c0, min(reps, c0 + CHUNK))]
            blocks = [b for _, b in draws]
            data = (np.concatenate(blocks) if state["rep"] is None else
                    {"z_odd": np.concatenate([b[0] for b in blocks]), "z_even": np.concatenate([b[1] for b in blocks])})
            recs = [{"seed": key + [2, i, c0 + j], "tau_star": j * (pre + spec["H"]) + pre, "family": "H0"}
                    for j in range(len(draws))]
            part = run_pipeline(spec, data, splits, recs, state)
            starts = np.array([s for s, _ in draws])
            part["alarm_index"] = np.where(part["alarm_index"] >= 0, part["alarm_index"] - part["tau_star"] + starts, -1)
            part["tau_star"] = starts
            parts.append(part)
        rows = pd.concat(parts, ignore_index=True)
        summary.append({"run_id": run_id(spec), "pipeline": spec["pipeline"], "reading": spec["reading"],
                        "variant": spec.get("variant"), "channels": json.dumps(spec.get("channels")), "H": spec["H"],
                        "gamma": spec["gamma"], "alpha": spec["alpha"], "threshold": float(state["threshold"]),
                        **summarize(rows, *null_target(spec, state)),
                        "state": json.dumps(_state_summary(state), sort_keys=True, default=lambda o: o.tolist())})
        frames.append(rows)
    return pd.concat(frames, ignore_index=True), pd.DataFrame(summary)


def _state_summary(state):
    keep = ("calib", "cols", "diagnostics", "threshold", "level", "lattice_units", "lam_iid", "gamma_op", "gamma_spec",
            "sigma_bar", "c", "gate")
    out = {k: state[k] for k in keep if k in state}
    if state["rep"] is not None:
        out["representation"] = {"class": type(state["rep"]).__name__, "state_sha256": state["rep"].state_hash(),
                                 "fit": state["rep"].fit_info, **({"pretrain": state["rep"].pretrain_info}
                                                                  if hasattr(state["rep"], "pretrain_info") else {})}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="D6 null check of a pipeline on the rows before the monitor segment.")
    ap.add_argument("--pipeline", required=True, choices=sorted(PIPELINES))
    ap.add_argument("--dataset", required=True, choices=sorted(DATASETS))
    ap.add_argument("--null-check", action="store_true", help="D6 null replicates against each reading's target")
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "pipelines")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "pipelines")
    args = ap.parse_args(argv)
    if not args.null_check:
        ap.error("--null-check is the only mode")
    if args.pipeline == "P7":
        ap.error("P7 needs a drift direction: it has no null check")
    if args.reps < 1:
        ap.error("--reps must be >= 1")
    load, load_splits = DATASETS[args.dataset]
    ret, dates, _ = load()
    rows = slice(*split_rows(dates, load_splits(args.dataset))["pre_monitor"])
    X, days, C = np.ascontiguousarray(ret[rows]), dates[rows], None
    if args.pipeline in CHAR_PIPELINES:
        C = chars.load_continuous_chars(args.dataset, rows)
        X = np.where(chars.load_universe(args.dataset, rows), X, np.nan)
    splits = split_rows(days, load_splits(args.dataset), C)
    n_channels = (len(_columns(make_spec(args.pipeline), fit_pipeline(make_spec(args.pipeline), X, splits)))
                  if args.pipeline in ("P3-C", "P4-C") else 0)
    specs = null_specs(args.pipeline, args.dataset, n_channels)
    key = [7, zlib.crc32(f"null|{args.pipeline}|{args.dataset}".encode())]
    alarms, summary = null_check(specs, X, splits, args.reps, key)
    stem = f"{args.pipeline}_{args.dataset}_null"
    args.out.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    save_fair_csv(alarms, args.out / f"alarms_{stem}.csv")
    records = summary.astype(object).where(summary.notna(), None).to_dict("records")
    runs = {rec["run_id"]: {"spec": spec, "state": json.loads(rec.pop("state")), "summary": rec}
            for spec, rec in zip(specs, records)}
    (args.out / f"runs_{stem}.json").write_text(json.dumps(runs, indent=2, sort_keys=True) + "\n")
    lines = [f"generator: python -m jepadrift.pipelines --pipeline {args.pipeline} --dataset {args.dataset} --null-check "
             f"--reps {args.reps}",
             f"rows: {days[0]}..{days[-1]} ({len(X)} days before the monitor segment); D6 key {key}",
             "region: p +- z sqrt(p (1 - p) (1/n + 1/n_cal)), z = 2.5758 (99 %); overlap of windows ignored"]
    for r in records:
        lines.append(f"{r['run_id']} {r['pipeline']} {r['reading']} variant={r['variant']} channels={r['channels']} "
                     f"H={r['H']} gamma={r['gamma']:g} alpha={r['alpha']} threshold={r['threshold']:.6g} n={r['n']} "
                     f"fpr={r['fpr']:.4f} target {r['kind']} {r['target']:.6f} region [{r['lo']:.4f}, {r['hi']:.4f}] "
                     f"{'PASS' if r['ok'] else 'FAIL'}")
    ok = bool(summary["ok"].all())
    lines.append(f"verdict: {'PASS' if ok else 'FAIL'}")
    (args.log_dir / f"null_{args.pipeline}_{args.dataset}.log").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
