"""Stream 27, E10 linear stage (Appendix D): false alarms and F1 gains of the sign monitors P1-C and P3-C when
central symmetry fails, with and without recentring on a frozen calib rate q_hat_u (prompts/plans/plan-27.md).

Backgrounds, classified by null validity before any FPR is read
  D5     independent paths, T_calib calib rows then H monitored rows; base GARCH(0.08, 0.90) with multivariate t7
         innovations and an equicorrelated factor (rho = 0.40, N = 97); one factor varied at a time: t_nu; GJR
         leverage on the sign of the previous cross-sectional mean (alpha = 0.08 - gamma / 2, local generator);
         a compensated common negative jump in the factor (invalid null; its matched valid generator applies one
         Rademacher sign per day in the loop); rounding to a pilot tick (zero returns)
  D6     symmetrized d2_us97 and d3_239 rows 2005-2019, one Rademacher sign per day shared by all assets
  raw    every H-day window of the pretrain rows, fitted on the later calib rows: retrospective, descriptive
  coins  i.i.d. fair bits (design iid_scenario): fpr_iid_mc is a Monte Carlo estimate, within a 99 % binomial
         tolerance of the exact lattice level for the `half` exact reading of a single stream
Arms share the realized bits B = 1{y > 0}, every tie broken by a local fair coin: `half` centres B at 1/2, `qhat`
at the frozen calib rate. `zero_neg_half` and `zero_neg_qhat` apply Article B's zero = negative rule (P1-C only,
backgrounds with zeros): their sign-stream null is invalid and carries no FPR guarantee.
Readings: exact = strict bilateral CUSUM (delta = 0.1) at the lattice midpoint at H; anytime-valid = CUSUM
e-detector at gamma_H = H / alpha on x = (B - c) / max(c, 1 - c) in [-1, 1]. P3-C `half` runs through
pipelines.run_pipeline; P1-C (cusum.P1["P1-C/C"]) and the recentred arms run on the monitors core.
Outputs: <out>/e10_cells.csv and <out>/e10_gains.csv (save_fair_csv), <fig-dir>/{fpr_inflation,gains}.{png,pdf}
drawn from the CSVs, <log-dir>/run.log.

Usage: python experiments/e10_robustness.py --stage linear --families F1 [--quick] --out results/e10
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"
os.environ["MPLBACKEND"] = "Agg"

import argparse
import concurrent.futures
import functools
import hashlib
import json
import math
import multiprocessing
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl
from jepadrift import pipelines as pl
from jepadrift import sim
from jepadrift.injection import inject, symmetrize
from jepadrift.monitors import eprocess, lattice
from jepadrift.monitors.cusum import P1, bilateral_delay_vec
from jepadrift.monitors.gamma import gamma_spectral
from jepadrift.monitors.streams import exact_sign_stream
from jepadrift.representations.extract import DATASETS
from jepadrift.stats.intervals import wilson

STREAM = 27
REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVED = REPO_ROOT / "data" / "derived"
CONFIG = REPO_ROOT / "configs" / "e10.yaml"
WINDOW_END = np.datetime64("2019-12-31")
P1C = P1["P1-C/C"]
DELTA = P1C["delta"]
FROZEN = {"K": "mp", "mode": "factor", "shrinkage": "ledoit_wolf"}
ARMS = ("half", "qhat")
ZERO_ARMS = ("zero_neg_half", "zero_neg_qhat")
READINGS = ("exact", "anytime-valid")
REFERENCE_KINDS = ("level_exact", "self_valid", "matched_valid_generator", "symmetrized_window",
                   "descriptive_contrast", "none")
DESIGNS = ("prospective", "symmetrized", "retrospective", "iid_scenario")
NULL_VALID = ("valid", "invalid", "unknown")
CI_KINDS = ("wilson", "wilson_conditional_approx", "hac_bartlett", "paired_bootstrap", "na")
CHUNK_REPS, CHUNK_WINDOWS, CHUNK_COINS = 25, 128, 1000
Z95 = 1.959963984540054
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e5e4e0", "#fcfcfb"
CELL_COLUMNS = ["background", "dataset", "family", "sr", "pipeline", "unit", "arm", "reading", "null_valid", "design",
                "reference_kind", "n", "alarms", "rate", "rate_lo", "rate_hi", "ci_kind", "deff", "n_eff", "alpha",
                "level_exact", "fpr_iid_mc", "fpr_ref", "fpr_ref_lo", "fpr_ref_hi", "ref_ci_kind", "inflation",
                "inflation_lo", "inflation_hi", "inflation_ci_kind", "contrast_fpr", "contrast_lo", "contrast_hi",
                "q_hat", "q_mean", "fpr_pred_iid", "pred_gap", "zero_share", "rmst", "median_delay",
                "mean_delay_detected", "censored"]
GAIN_COLUMNS = ["background", "dataset", "sr", "arm", "asset_selection", "asset", "asset_index", "oracle",
                "exploratory", "null_valid", "n_f1", "n_h0", "rmst_p1", "rmst_p3", "rmst_ratio", "rmst_ratio_lo",
                "rmst_ratio_hi", "rmst_ratio_ci_kind", "bounds_add_ratio", "median_p1", "median_p3", "median_ratio",
                "det_p1", "det_p3", "cens_p3", "fpr_p1", "fpr_p1_lo", "fpr_p1_hi", "fpr_p3", "fpr_p3_lo",
                "fpr_p3_hi", "fpr_diff", "fpr_diff_lo", "fpr_diff_hi", "fpr_diff_ci_kind"]


def rng(*key):
    """Local generator keyed on SeedSequence([27, *key]); no global state."""
    return np.random.default_rng(np.random.SeedSequence([STREAM, *(int(k) for k in key)]))


def crc(label):
    """Integer key of a cell label."""
    return zlib.crc32(label.encode())


def d5_panel(T, N, alpha, beta, nu, rng, factor_rho=None, burn=1000, gjr=0.0, shock=None, day_signs=None):
    """sim.garch_panel plus a GJR term on the sign of the previous cross-sectional mean, a compensated common negative
    jump (w, p) in the factor and in-loop daily signs; gjr=0, shock=None, day_signs=None reproduce it bit for bit."""
    if alpha < 0 or beta < 0 or gjr < 0 or alpha + beta + gjr / 2.0 >= 1:
        raise ValueError(f"need alpha, beta, gjr >= 0 and alpha + beta + gjr / 2 < 1, got {alpha}, {beta}, {gjr}")
    if nu is not None and nu <= 2:
        raise ValueError(f"nu must exceed 2 for unit-variance innovations, got {nu}")
    if factor_rho is not None and not 0 <= factor_rho < 1:
        raise ValueError(f"factor_rho must lie in [0, 1), got {factor_rho}")
    if shock is not None and (factor_rho is None or not (0 < shock[0] < 1 and 0 < shock[1] < 1)):
        raise ValueError("the common shock (w, p) needs factor_rho and 0 < w, p < 1")
    omega = 1.0 - alpha - beta - gjr / 2.0
    s2, prev, prev_mean = 1.0, 0.0, 0.0
    out = np.empty((T, N))
    for t in range(burn + T):  # ponytail: one panel per call, a replicate axis if E10 runtime needs it
        s2 = omega + (alpha + gjr * (prev_mean < 0.0)) * prev + beta * s2
        z = rng.standard_normal(N)
        if factor_rho is not None:
            g = rng.standard_normal()
            if shock is not None:
                w, p = shock
                g = math.sqrt(1.0 - w) * g + math.sqrt(w) * (p - (rng.random() < p)) / math.sqrt(p * (1.0 - p))
            z = math.sqrt(factor_rho) * g + math.sqrt(1.0 - factor_rho) * z
        if nu is not None:
            z = z / math.sqrt(rng.chisquare(nu) / nu) * math.sqrt((nu - 2) / nu)
        x = math.sqrt(s2) * z
        prev, prev_mean = float(np.mean(x ** 2)), float(np.mean(x))
        if t >= burn:
            out[t - burn] = x if day_signs is None else x * day_signs[t - burn]
    return out


def d5_path(d5, bg, T, gen, day_signs=None):
    """A D5 background path: sim.garch_panel unless the background needs the GJR term, the shock or daily signs."""
    nu, gjr, w = bg.get("nu", d5["nu"]), bg.get("gjr", 0.0), bg.get("shock_w")
    alpha, kw = d5["alpha"] - gjr / 2.0, {"factor_rho": d5["factor_rho"], "burn": d5["burn"]}
    if gjr == 0.0 and w is None and day_signs is None:
        return sim.garch_panel(T, d5["N"], alpha, d5["beta"], nu, gen, **kw)
    return d5_panel(T, d5["N"], alpha, d5["beta"], nu, gen, gjr=gjr, shock=None if w is None else (w, d5["shock_p"]),
                    day_signs=day_signs, **kw)


def round_to_tick(X, tick):
    """Returns quoted on a tick, tick * round(X / tick): an odd map (half to even), zero returns become ties."""
    return tick * np.round(X / tick)


def pilot_tick(d5, share, key):
    """Tick 2 Q_share(|x|) on a pilot path of the D5 base generator, so that about `share` of the returns are zero."""
    X = sim.garch_panel(d5["pilot_days"], d5["N"], d5["alpha"], d5["beta"], d5["nu"], rng(*key),
                        factor_rho=d5["factor_rho"], burn=d5["burn"])
    return float(2.0 * np.quantile(np.abs(X), share))


def coin_bits(y, gen):
    """B = 1{y > 0} as float64, every tie y == 0 replaced by a fair coin of gen (exact_sign_stream + 1/2)."""
    return exact_sign_stream(y, gen) + 0.5


def p3c_bits(z, seed):
    """The bits of the P3-C `half` arm as pipelines.run_pipeline draws them: coins of SeedSequence([*seed, 7])."""
    return coin_bits(z, np.random.default_rng(np.random.SeedSequence([*(int(s) for s in seed), 7])))


def alarms(B, c, reading, thr, gamma):
    """First alarm offset along the last axis of the bits B centred at c (-1 when none): strict bilateral CUSUM at
    thr (exact) or CUSUM e-detector at gamma on x = (B - c) / max(c, 1 - c) in [-1, 1] (anytime-valid)."""
    if reading == "exact":
        return bilateral_delay_vec(B - c, DELTA, thr)
    x = (B - c) / np.maximum(c, 1.0 - c)
    return eprocess.first_alarm(eprocess.log_edetector(x, "cusum"), gamma)


def dictionary_alarm(B, c, gamma):
    """First alarm offset of the equal-weight CUSUM e-detector dictionary over the channels of B (..., T, D)."""
    x = (B - c) / np.maximum(c, 1.0 - c)
    return eprocess.first_alarm(eprocess.log_dictionary_edetector(x, "cusum"), gamma)


def lattice_selection(alpha, H):
    """The P1-C/C lattice reading at H: strict rule, nearest attainable level at or below alpha, delta = 0.1."""
    return lattice.select_threshold(alpha, rule=P1C["rule"], comparison=P1C["comparison"], H=H, delta=DELTA, sided=2)


def fpr_pred_iid(q, sel, H):
    """Exact FPR(H) of the `half` exact reading if the bits were i.i.d. Bernoulli(q): an iid reference, no criterion."""
    a, b, _ = lattice.lattice_steps(DELTA)
    return lattice.exceedance(H, sel["units"], a, b, float(q), sided=2)


def exact_state(state, sel):
    """The P3-C exact-reading state: the anytime-valid state with the lattice keys of pipelines._cal_p3c."""
    return {**state, "threshold": sel["threshold"], "level": sel["level"], "lattice_units": sel["units"]}


def run_p3c(spec, state, z, records):
    """Alarm offsets of the P3-C `half` arm by pipelines.run_pipeline on the Z panel z (-1 when none)."""
    rows = pl.run_pipeline(spec, {"z_odd": z, "z_even": z * z}, None, records, state)
    alarm = rows["alarm_index"].to_numpy()
    return np.where(alarm >= 0, alarm - rows["tau_star"].to_numpy(), -1)


def iid_tolerance(k, n, level):
    """The 99 % binomial tolerance of fpr_iid_mc around the exact lattice level (half, exact, single stream)."""
    half = pl.Z99 * math.sqrt(level * (1.0 - level) / n)
    return {"lo": level - half, "hi": level + half, "within": level - half <= k / n <= level + half}


def deff_rate_ci(ind, L):
    """(deff, n_eff, lo, hi, ci_kind) of the mean of an alarm-indicator series over overlapping windows: deff =
    gamma_spectral(ind, L) (Bartlett), Wilson on n_eff = n / deff; NA when the series is constant, the estimator fails
    or n_eff leaves [1, n]."""
    ind = np.asarray(ind, dtype=np.float64)
    try:
        deff = float(gamma_spectral(ind, L))
    except ValueError:
        return math.nan, math.nan, math.nan, math.nan, "na"
    n_eff = ind.size / deff if deff > 0 else math.nan
    if not (math.isfinite(n_eff) and 1.0 <= n_eff <= ind.size):
        return deff, n_eff, math.nan, math.nan, "na"
    return (deff, n_eff, *wilson(ind.mean() * n_eff, n_eff), "hac_bartlett")


def hac_mean_ci(d, L):
    """(mean, lo, hi, ci_kind): mean of d with the Wald interval of variance var(d) deff / n, deff Bartlett; NA as in
    deff_rate_ci."""
    d = np.asarray(d, dtype=np.float64)
    try:
        deff = float(gamma_spectral(d, L))
    except ValueError:
        return float(d.mean()), math.nan, math.nan, "na"
    n_eff = d.size / deff if deff > 0 else math.nan
    if not (math.isfinite(n_eff) and 1.0 <= n_eff <= d.size):
        return float(d.mean()), math.nan, math.nan, "na"
    half = Z95 * math.sqrt(d.var() / n_eff)
    return float(d.mean()), float(d.mean() - half), float(d.mean() + half), "hac_bartlett"


def bootstrap_ci(stat, n, B, gen):
    """Percentile 95 % interval of stat(idx) over B resamples idx (B, n) of n paired replicates."""
    lo, hi = np.percentile(stat(gen.integers(0, n, size=(B, n))), [2.5, 97.5])
    return float(lo), float(hi)


def restricted(off, H):
    """Delays restricted to H: offset + 1 when detected, H when censored."""
    off = np.asarray(off)
    return np.where(off >= 0, off + 1.0, float(H))


def delay_stats(off, H):
    """Detection rate, restricted mean (RMST), median delay (inf when detection <= 1/2), mean delay of detections."""
    off = np.asarray(off)
    det = off >= 0
    return {"rate": float(det.mean()), "rmst": float(restricted(off, H).mean()),
            "median_delay": float(np.median(np.where(det, off + 1.0, np.inf))),
            "mean_delay_detected": float(off[det].mean() + 1.0) if det.any() else math.nan,
            "censored": float(1.0 - det.mean())}


def gain_rows(f1, h0, H, gen, B):
    """Median and oracle assets against the P3-C dictionary at gamma_H: RMST ratio (restricted to H; a lower bound of
    the ADD ratio only when P3-C is never censored), median ratio, paired bootstrap CIs, H0 FPR of the same asset."""
    t3, t1 = restricted(f1["p3"], H), restricted(f1["p1"], H)
    m, n, n0 = t1.shape[1], len(t3), len(h0["p3"])
    order = np.lexsort((np.arange(m), t1.mean(axis=0)))
    s3 = delay_stats(f1["p3"], H)
    d3 = np.asarray(h0["p3"], dtype=np.float64)
    rows = []
    for selection, asset in (("median", int(order[(m - 1) // 2])), ("oracle", int(order[0]))):
        s1 = delay_stats(f1["p1"][:, asset], H)
        d1 = np.asarray(h0["p1"][:, asset], dtype=np.float64)
        lo, hi = bootstrap_ci(lambda idx: t1[idx, asset].mean(axis=1) / t3[idx].mean(axis=1), n, B, gen)
        dlo, dhi = bootstrap_ci(lambda idx: d1[idx].mean(axis=1) - d3[idx].mean(axis=1), n0, B, gen)
        (p1lo, p1hi), (p3lo, p3hi) = wilson(d1.sum(), n0), wilson(d3.sum(), n0)
        both = s1["rate"] > 0.5 and s3["rate"] > 0.5
        rows.append({"asset_selection": selection, "asset_index": asset, "oracle": selection == "oracle",
                     "exploratory": selection == "oracle", "n_f1": n, "n_h0": n0, "rmst_p1": s1["rmst"],
                     "rmst_p3": s3["rmst"], "rmst_ratio": s1["rmst"] / s3["rmst"], "rmst_ratio_lo": lo,
                     "rmst_ratio_hi": hi, "rmst_ratio_ci_kind": "paired_bootstrap",
                     "bounds_add_ratio": s3["censored"] == 0.0, "median_p1": s1["median_delay"],
                     "median_p3": s3["median_delay"],
                     "median_ratio": s1["median_delay"] / s3["median_delay"] if both else math.nan,
                     "det_p1": s1["rate"], "det_p3": s3["rate"], "cens_p3": s3["censored"], "fpr_p1": float(d1.mean()),
                     "fpr_p1_lo": p1lo, "fpr_p1_hi": p1hi, "fpr_p3": float(d3.mean()), "fpr_p3_lo": p3lo,
                     "fpr_p3_hi": p3hi, "fpr_diff": float(d1.mean() - d3.mean()), "fpr_diff_lo": dlo,
                     "fpr_diff_hi": dhi, "fpr_diff_ci_kind": "paired_bootstrap"})
    return rows


def coin_reference(chunks, chunk, H, T_calib, dims, sel, gamma, key):
    """fpr_iid_mc counts on i.i.d. fair bits (iid scenario): a single stream (`half`, `qhat`, both readings) and
    dictionaries of D independent channels; {(unit, arm, reading): (alarms, n)}."""
    out = {}

    def add(k, det):
        a, n = out.get(k, (0, 0))
        out[k] = (a + int(det.sum()), n + det.size)

    for i in chunks:
        g = rng(key, i)
        B = (g.random((chunk, H)) < 0.5).astype(np.float64)
        q = (g.random((chunk, T_calib)) < 0.5).mean(axis=1)[:, None]
        for arm, c in (("half", 0.5), ("qhat", q)):
            for reading in READINGS:
                add(("single", arm, reading), alarms(B, c, reading, sel["threshold"], gamma) >= 0)
        for D in dims:
            Bd = (g.random((chunk, H, D)) < 0.5).astype(np.float64)
            qd = (g.random((chunk, T_calib, D)) < 0.5).mean(axis=1)[:, None, :]
            for arm, c in (("half", 0.5), ("qhat", qd)):
                add((f"dict{D}", arm, "anytime-valid"), dictionary_alarm(Bd, c, gamma) >= 0)
    return out


def check_window(days):
    """Refuse any row dated after 2019-12-31 (pre-J4 guard, configs/FROZEN.json absent)."""
    if np.asarray(days, dtype="datetime64[D]").max() > WINDOW_END:
        raise ValueError(f"rows dated after {WINDOW_END} are refused before J4")


@functools.lru_cache(maxsize=None)
def load_real(name):
    """Rows from the first pretrain day to the last calib day (2005-2019), with their splits and assets."""
    load, load_splits = DATASETS[name]
    ret, dates, assets = load()
    sp = load_splits(name)
    a, b = pl.split_rows(dates, sp)["pre_monitor"]
    X, days = np.ascontiguousarray(ret[a:b]), dates[a:b]
    check_window(days)
    if not np.isfinite(X).all():
        raise ValueError(f"{name}: the pre-monitor rows must be finite")
    return X, days, pl.split_rows(days, sp), list(assets)


def p1_assets(name, N, m):
    """The P1-C assets of a real panel: m columns drawn once with SeedSequence([27, crc32(dataset), 1]), sorted."""
    return np.sort(rng(crc(name), 1).choice(N, m, replace=False))


@functools.lru_cache(maxsize=None)
def frozen_fit(name, H, gamma):
    """P3-C anytime-valid state fitted on the raw calib rows (K at the MP edge), checked against the committed
    sidecar of the frozen basis; returns (state, state hash)."""
    X, _, splits, _ = load_real(name)
    state = pl.fit_pipeline(pl.make_spec("P3-C", gamma=gamma, H=H, dataset=name), X, splits)
    h = state["rep"].state_hash()
    sidecars = [json.loads(p.read_text()) for p in sorted((DERIVED / name).glob("z_*.json"))]
    committed = [s["state_sha256"] for s in sidecars if s["config"] == FROZEN]
    if committed != [h]:
        raise ValueError(f"{name}: calib basis {h[:16]} differs from the committed sidecar {committed}")
    return state, h


def p3c_specs(K, H, gamma, alpha, dataset, D):
    """P3-C specs: the anytime-valid dictionary at gamma_H and one exact reading per channel."""
    av = pl.make_spec("P3-C", K=K, gamma=gamma, H=H, dataset=dataset)
    return av, [pl.make_spec("P3-C", reading="exact", channels=[k], alpha=alpha, K=K, H=H, dataset=dataset)
                for k in range(D)]


def monitor(ctx, X_fit, X_mon, tau, key, h0, zeros):
    """One replicate: P3-C fitted on the calib rows of X_fit, then P1-C and P3-C on rows [tau, tau + H) of X_mon; both
    arms on the same bits (zero_neg arms when zeros), both readings under H0, anytime-valid only under F1."""
    H, gamma, sel = ctx["H"], ctx["gamma"], ctx["sel"]
    a, b = ctx["splits"]["calib"]
    state = pl.fit_pipeline(ctx["spec"], X_fit, ctx["splits"])
    rep = state["rep"]
    z_cal = rep.transform_panel(np.ascontiguousarray(X_fit[a:b]))["z_odd"]
    z = rep.transform_panel(np.ascontiguousarray(X_mon[tau:tau + H]))["z_odd"]
    seed = [STREAM, *key]
    Bz, qz = p3c_bits(z, seed), coin_bits(z_cal, rng(*key, 5)).mean(axis=0)
    cols = ctx["assets"]
    Y, Yc = X_mon[tau:tau + H, cols], X_fit[a:b, cols]
    Ba, qa = coin_bits(Y, rng(*key, 3)), coin_bits(Yc, rng(*key, 4)).mean(axis=0)
    readings = READINGS if h0 else ("anytime-valid",)
    out = {"zeros": float((Y == 0).mean()), "ties_z": int((z == 0).sum())}
    p1 = {"half": (Ba, 0.5, qa), "qhat": (Ba, qa[:, None], qa)}
    if zeros:
        B0, q0 = (Y > 0).astype(np.float64), (Yc > 0).mean(axis=0)
        p1.update(zero_neg_half=(B0, 0.5, q0), zero_neg_qhat=(B0, q0[:, None], q0))
    for arm, (B, c, q) in p1.items():
        for reading in readings:
            out["P1-C", arm, reading] = alarms(B.T, c, reading, sel["threshold"], gamma)
        out["q_mean", "P1-C", arm], out["q_hat", "P1-C", arm] = B.mean(axis=0), q
    rec = [{"seed": seed, "tau_star": 0, "family": "H0" if h0 else "F1"}]
    out["P3-C", "half", "anytime-valid"] = run_p3c(ctx["spec"], state, z, rec)
    out["P3-C", "qhat", "anytime-valid"] = np.atleast_1d(dictionary_alarm(Bz, qz, gamma))
    if h0:
        st = exact_state(state, sel)
        out["P3-C", "half", "exact"] = np.concatenate([run_p3c(s, st, z, rec) for s in ctx["exact_specs"]])
        out["P3-C", "qhat", "exact"] = alarms(Bz.T, qz[:, None], "exact", sel["threshold"], gamma)
    for arm in ARMS:
        out["q_mean", "P3-C", arm], out["q_hat", "P3-C", arm] = Bz.mean(axis=0), qz
    return out


def d5_task(ctx, span):
    """D5 replicates r0..r1 of one cell: the background path, F1 at the first monitored row, rounding, monitoring,
    and for the shock under H0 the matched valid generator (one Rademacher sign per day in the loop)."""
    d5, T_cal, H = ctx["d5"], ctx["d5"]["T_calib"], ctx["H"]
    T, out = T_cal + H, []
    for r in range(*span):
        key = (ctx["crc"], r)
        X = d5_path(d5, ctx["bg"], T, rng(*key, 0))
        if ctx["family"] == "F1":
            X = inject(X, "F1", T_cal, fl.kl_from_sharpe(ctx["sr"]), {"calib": (0, T_cal), "K": d5["K"] + 1},
                       rng(*key, 2))[0]
        if ctx["tick"]:
            X = round_to_tick(X, ctx["tick"])
        res = {"main": monitor(ctx, X, X, T_cal, key, ctx["family"] == "H0", ctx["tick"] > 0)}
        if ctx["matched"]:
            Xs = d5_path(d5, ctx["bg"], T, rng(*key, 0), day_signs=rng(*key, 6).choice((-1.0, 1.0), size=T))
            res["sym"] = monitor(ctx, Xs, Xs, T_cal, (*key, 6), True, False)
        out.append(res)
    return out


def d6_task(ctx, span):
    """D6 replicates r0..r1 of one cell: independent symmetrizations for the fit and the monitored panel (one sign per
    day shared by all assets), a uniform onset, F1 injected on the monitored panel."""
    X, _, splits, _ = load_real(ctx["dataset"])
    H, out = ctx["H"], []
    for r in range(*span):
        key = (ctx["crc"], r)
        X_fit, X_mon = symmetrize(X, rng(*key, 1))[0], symmetrize(X, rng(*key, 0))[0]
        g = rng(*key, 2)
        tau = int(g.integers(0, len(X) - H + 1))
        if ctx["family"] == "F1":
            X_mon = inject(X_mon, "F1", tau, fl.kl_from_sharpe(ctx["sr"]), {"calib": splits["calib"], "K": ctx["D"]},
                           g)[0]
        out.append({"main": monitor(ctx, X_fit, X_mon, tau, key, ctx["family"] == "H0", True)})
    return out


def raw_context(name, cfg, sel):
    """Raw placebo inputs: the frozen calib fit, pretrain Z and P1-C bits drawn once per unit, frozen calib rates."""
    X, _, splits, assets = load_real(name)
    H, alpha = cfg["H"], cfg["alpha"]
    gamma = pl.horizon_gamma(H, alpha)
    state, h = frozen_fit(name, H, gamma)
    rep, (a, b), (p0, p1) = state["rep"], splits["calib"], splits["pretrain"]
    key = crc(f"raw|{name}")
    z_pre = rep.transform_panel(np.ascontiguousarray(X[p0:p1]))["z_odd"]
    z_cal = rep.transform_panel(np.ascontiguousarray(X[a:b]))["z_odd"]
    D = z_pre.shape[1]
    cols = p1_assets(name, X.shape[1], cfg["n_p1"])
    Y_pre, Yc = X[p0:p1, cols], X[a:b, cols]
    _, exact_specs = p3c_specs("mp", H, gamma, alpha, name, D)
    return {"dataset": name, "H": H, "gamma": gamma, "sel": sel, "state": state, "state_hash": h, "z_pre": z_pre,
            "exact_specs": exact_specs, "spec": pl.make_spec("P3-C", gamma=gamma, H=H, dataset=name), "crc": key,
            "qz": coin_bits(z_cal, rng(key, 0, 5)).mean(axis=0), "qa": coin_bits(Yc, rng(key, 0, 4)).mean(axis=0),
            "q0": (Yc > 0).mean(axis=0), "Ba": coin_bits(Y_pre, rng(key, 0, 3)), "B0": (Y_pre > 0).astype(np.float64),
            "Y_pre": Y_pre, "qz_mean": coin_bits(z_pre, rng(key, 0, 7)).mean(axis=0), "D": D,
            "unit_names": [assets[c] for c in cols], "zeros": float((Y_pre == 0).mean())}


def raw_task(ctx, starts):
    """Alarm offsets on raw pretrain windows and on the same windows symmetrized (one sign per day shared by all
    assets, same state and frozen calib rates), per pipeline, arm and reading."""
    H, gamma, sel, key, z_pre = ctx["H"], ctx["gamma"], ctx["sel"], ctx["crc"], ctx["z_pre"]
    thr, nW, out = sel["threshold"], len(starts), {}
    eps, Ys = [], []
    for w in starts:
        y, e = symmetrize(ctx["Y_pre"][w:w + H], rng(key, w, 6))
        Ys.append(y)
        eps.append(e)
    z_raw = np.stack([z_pre[w:w + H] for w in starts])
    z_sym = np.stack(eps)[:, :, None] * z_raw
    recs = {"raw": [{"seed": [STREAM, key, w], "tau_star": w, "family": "H0"} for w in starts],
            "sym": [{"seed": [STREAM, key, w, 6], "tau_star": j * H, "family": "H0"} for j, w in enumerate(starts)]}
    zs = {"raw": z_pre, "sym": z_sym.reshape(nW * H, -1)}
    st = exact_state(ctx["state"], sel)
    bits = {"raw": np.stack([ctx["Ba"][w:w + H] for w in starts]),
            "sym": np.stack([coin_bits(y, rng(key, w, 8)) for y, w in zip(Ys, starts)])}
    zero_bits = {"raw": np.stack([ctx["B0"][w:w + H] for w in starts]), "sym": (np.stack(Ys) > 0).astype(np.float64)}
    for part in ("raw", "sym"):
        out[part, "P3-C", "half", "anytime-valid"] = run_p3c(ctx["spec"], ctx["state"], zs[part], recs[part])[:, None]
        out[part, "P3-C", "half", "exact"] = np.stack([run_p3c(s, st, zs[part], recs[part])
                                                       for s in ctx["exact_specs"]], axis=1)
        Bz = np.stack([p3c_bits(z_raw[j] if part == "raw" else z_sym[j], rec["seed"])
                       for j, rec in enumerate(recs[part])])
        out[part, "P3-C", "qhat", "anytime-valid"] = dictionary_alarm(Bz, ctx["qz"], gamma)[:, None]
        out[part, "P3-C", "qhat", "exact"] = alarms(np.swapaxes(Bz, 1, 2), ctx["qz"][:, None], "exact", thr, gamma)
        Ba, B0 = np.swapaxes(bits[part], 1, 2), np.swapaxes(zero_bits[part], 1, 2)
        for arm, (B, c) in {"half": (Ba, 0.5), "qhat": (Ba, ctx["qa"][:, None]), "zero_neg_half": (B0, 0.5),
                            "zero_neg_qhat": (B0, ctx["q0"][:, None])}.items():
            for reading in READINGS:
                out[part, "P1-C", arm, reading] = alarms(B, c, reading, thr, gamma)
    return out


def run_task(task):
    """Dispatch one task (kind, context, argument) to its worker."""
    kind, ctx, arg = task
    if kind == "coins":
        return coin_reference([arg], ctx["chunk"], ctx["H"], ctx["T_calib"], ctx["dims"], ctx["sel"], ctx["gamma"],
                              ctx["crc"])
    return {"d5": d5_task, "d6": d6_task, "raw": raw_task}[kind](ctx, arg)


def run_tasks(tasks, jobs):
    """Run tasks in submission order, on a spawn-context process pool when jobs > 1."""
    if jobs > 1 and len(tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
            return list(pool.map(run_task, tasks))
    return [run_task(t) for t in tasks]


def _row(info, family, sr, pipeline, unit, arm, reading, alpha):
    row = dict.fromkeys(CELL_COLUMNS, math.nan)
    row.update(background=info["background"], dataset=info["dataset"], family=family, sr=sr, pipeline=pipeline,
               unit=unit, arm=arm, reading=reading, design=info["design"], alpha=alpha, ci_kind="na",
               ref_ci_kind="na", inflation_ci_kind="na", reference_kind="none",
               null_valid="invalid" if arm in ZERO_ARMS else info["null"])
    return row


def _units(info, pipeline, reading, n_units):
    if pipeline == "P1-C":
        return info["unit_names"]
    return ["dict"] if reading == "anytime-valid" else [f"ch{k}" for k in range(n_units)]


def _reference_kind(info, arm, reading, single):
    if info["kind"] == "raw":
        return "symmetrized_window" if arm == "half" else "descriptive_contrast"
    if arm in ZERO_ARMS:
        return "none"
    if info["null"] == "invalid":
        return "matched_valid_generator"
    return "level_exact" if arm == "half" and reading == "exact" and single else "self_valid"


def _stack(res, key):
    return np.array([np.atleast_1d(r[key]) for r in res])


def cell_rows(info, res, sym, cfg, sel, coins, family, sr, gen):
    """Cells rows of one D5 or D6 cell: per pipeline, arm, reading and unit, with the references of plan section 5."""
    H, alpha, B = cfg["H"], cfg["alpha"], cfg["reps"]["boot"]
    rows = []
    for key in [k for k in res[0] if isinstance(k, tuple) and k[0] in ("P1-C", "P3-C")]:
        pipeline, arm, reading = key
        offs = _stack(res, key)
        single = not (pipeline == "P3-C" and reading == "anytime-valid")
        q_mean = _stack(res, ("q_mean", pipeline, arm)).mean(axis=0)
        q_hat = _stack(res, ("q_hat", pipeline, arm)).mean(axis=0)
        for u, unit in enumerate(_units(info, pipeline, reading, offs.shape[1])):
            row = _row(info, family, sr, pipeline, unit, arm, reading, alpha)
            n, k = offs.shape[0], int((offs[:, u] >= 0).sum())
            lo, hi = wilson(k, n)
            row.update(n=n, alarms=k, rate=k / n, rate_lo=lo, rate_hi=hi, ci_kind="wilson", deff=1.0, n_eff=float(n),
                       zero_share=float(np.mean([r["zeros"] for r in res])))
            if single:
                row.update(q_mean=float(q_mean[u]), q_hat=float(q_hat[u]))
            if family == "F1":
                row.update({k_: v for k_, v in delay_stats(offs[:, u], H).items() if k_ != "rate"})
                rows.append(row)
                continue
            row["reference_kind"] = _reference_kind(info, arm, reading, single)
            if arm in ARMS:
                c = coins[("single" if single else f"dict{info['D']}", arm, reading)]
                row["fpr_iid_mc"] = c[0] / c[1]
            if arm == "half" and reading == "exact" and single:
                row["level_exact"] = sel["level"]
            if reading == "exact" and arm in ("half", "zero_neg_half") and single:
                row["fpr_pred_iid"] = fpr_pred_iid(q_mean[u], sel, H)
                row["pred_gap"] = row["rate"] - row["fpr_pred_iid"]
            if row["reference_kind"] == "level_exact":
                row.update(inflation=row["rate"] - sel["level"], inflation_lo=lo - sel["level"],
                           inflation_hi=hi - sel["level"], inflation_ci_kind="wilson")
            if row["reference_kind"] == "matched_valid_generator":
                a_, b_ = (offs[:, u] >= 0).astype(np.float64), (_stack(sym, key)[:, u] >= 0).astype(np.float64)
                rlo, rhi = wilson(b_.sum(), n)
                ilo, ihi = bootstrap_ci(lambda idx: a_[idx].mean(axis=1) - b_[idx].mean(axis=1), n, B, gen)
                row.update(fpr_ref=float(b_.mean()), fpr_ref_lo=rlo, fpr_ref_hi=rhi, ref_ci_kind="wilson",
                           inflation=float(a_.mean() - b_.mean()), inflation_lo=ilo, inflation_hi=ihi,
                           inflation_ci_kind="paired_bootstrap")
            rows.append(row)
    return rows


def raw_rows(name, cfg, sel, starts=None, jobs=1, coins=None):
    """Cells rows of the raw placebo of one dataset (every pretrain window by default): retrospective, descriptive;
    `half` is referred to the symmetrized window, the other arms form descriptive contrasts."""
    ctx = raw_context(name, cfg, sel)
    p0, p1 = load_real(name)[2]["pretrain"]
    starts = np.arange(0, p1 - p0 - cfg["H"] + 1) if starts is None else np.asarray(starts)
    chunks = [starts[i:i + CHUNK_WINDOWS] for i in range(0, len(starts), CHUNK_WINDOWS)]
    parts = run_tasks([("raw", ctx, [int(w) for w in c]) for c in chunks], jobs)
    res = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    info = {"background": "raw", "dataset": name, "design": "retrospective", "null": "unknown", "kind": "raw",
            "unit_names": ctx["unit_names"], "D": ctx["D"]}
    H, L, rows = cfg["H"], cfg["H"] - 1, []
    for (part, pipeline, arm, reading), offs in res.items():
        if part != "raw":
            continue
        sym = res["sym", pipeline, arm, reading]
        single = not (pipeline == "P3-C" and reading == "anytime-valid")
        if pipeline == "P1-C":
            q_mean = (ctx["B0"] if arm in ZERO_ARMS else ctx["Ba"]).mean(axis=0)
            q_hat = ctx["q0"] if arm in ZERO_ARMS else ctx["qa"]
        else:
            q_mean, q_hat = ctx["qz_mean"], ctx["qz"]
        for u, unit in enumerate(_units(info, pipeline, reading, offs.shape[1])):
            row = _row(info, "H0", 0, pipeline, unit, arm, reading, cfg["alpha"])
            ind, ind_s = (offs[:, u] >= 0).astype(np.float64), (sym[:, u] >= 0).astype(np.float64)
            deff, n_eff, lo, hi, kind = deff_rate_ci(ind, L)
            slo, shi = wilson(ind_s.sum(), len(ind_s))
            row.update(n=len(ind), alarms=int(ind.sum()), rate=float(ind.mean()), rate_lo=lo, rate_hi=hi, ci_kind=kind,
                       deff=deff, n_eff=n_eff, reference_kind=_reference_kind(info, arm, reading, single),
                       zero_share=ctx["zeros"])
            if single:
                row.update(q_mean=float(q_mean[u]), q_hat=float(q_hat[u]))
            if arm in ARMS and coins is not None:
                c = coins[("single" if single else f"dict{ctx['D']}", arm, reading)]
                row["fpr_iid_mc"] = c[0] / c[1]
            if arm == "half" and reading == "exact" and single:
                row["level_exact"] = sel["level"]
            if reading == "exact" and arm in ("half", "zero_neg_half") and single:
                row["fpr_pred_iid"] = fpr_pred_iid(q_mean[u], sel, H)
                row["pred_gap"] = row["rate"] - row["fpr_pred_iid"]
            if arm == "half":
                mean, ilo, ihi, ikind = hac_mean_ci(ind - ind_s, L)
                if kind == "na":
                    ilo, ihi, ikind = math.nan, math.nan, "na"
                row.update(fpr_ref=float(ind_s.mean()), fpr_ref_lo=slo, fpr_ref_hi=shi,
                           ref_ci_kind="wilson_conditional_approx", inflation=mean, inflation_lo=ilo,
                           inflation_hi=ihi, inflation_ci_kind=ikind)
            else:
                row.update(contrast_fpr=float(ind_s.mean()), contrast_lo=slo, contrast_hi=shi,
                           ref_ci_kind="wilson_conditional_approx")
            rows.append(row)
    return rows, ctx


def coin_rows(coins, sel, alpha):
    """Rows of the iid scenario (background ref_coins, design iid_scenario)."""
    info = {"background": "ref_coins", "dataset": "coins", "design": "iid_scenario", "null": "valid"}
    rows = []
    for (unit, arm, reading), (k, n) in sorted(coins.items()):
        row = _row(info, "H0", 0, "coins", unit, arm, reading, alpha)
        lo, hi = wilson(k, n)
        row.update(n=n, alarms=k, rate=k / n, rate_lo=lo, rate_hi=hi, ci_kind="wilson", deff=1.0, n_eff=float(n),
                   fpr_iid_mc=k / n)
        if (unit, arm, reading) == ("single", "half", "exact"):
            row.update(reference_kind="level_exact", level_exact=sel["level"], inflation=k / n - sel["level"],
                       inflation_lo=lo - sel["level"], inflation_hi=hi - sel["level"], inflation_ci_kind="wilson")
        rows.append(row)
    return rows


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _save(plt, fig, fig_dir, stem):
    fig.tight_layout()
    fig.savefig(fig_dir / f"{stem}.png", dpi=200)
    fig.savefig(fig_dir / f"{stem}.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def _bars(est, lo, hi):
    err = np.vstack([est - lo, hi - est])
    return np.clip(np.where(np.isfinite(err), err, 0.0), 0.0, None)


def plot(out, fig_dir):
    """FPR by background (exact market channel and anytime-valid dictionary of P3-C) and median-asset RMST ratios,
    drawn from the CSVs only."""
    import matplotlib.pyplot as plt

    cells = pd.read_csv(out / "e10_cells.csv", float_precision="round_trip")
    gains = pd.read_csv(out / "e10_gains.csv", float_precision="round_trip")
    fig_dir.mkdir(parents=True, exist_ok=True)
    saved = plt.rcParams.copy()
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE})
    try:
        h0 = cells[(cells["family"] == "H0") & (cells["pipeline"] == "P3-C")]
        h0 = h0.assign(label=np.where(h0["dataset"].isin(["d5"]), h0["background"],
                                      h0["background"] + ":" + h0["dataset"].str.replace("_", "", regex=False)))
        fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4))
        panels = ((axes[0], h0[(h0["unit"] == "ch0") & (h0["reading"] == "exact")], "exact reading, market channel ch0",
                   h0["level_exact"].dropna().iloc[0] if h0["level_exact"].notna().any() else None),
                  (axes[1], h0[(h0["unit"] == "dict") & (h0["reading"] == "anytime-valid")],
                   "anytime-valid dictionary at gamma_H", float(cells["alpha"].iloc[0])))
        for ax, df, title, ref in panels:
            labels = list(dict.fromkeys(df["label"]))
            x = np.arange(len(labels))
            for j, (arm, color) in enumerate(zip(ARMS, SERIES)):
                d = df[df["arm"] == arm].set_index("label").reindex(labels)
                err = _bars(d["rate"], d["rate_lo"], d["rate_hi"])
                ax.errorbar(x + (j - 0.5) * 0.25, d["rate"], yerr=err, fmt="o", ms=4, color=color, elinewidth=1,
                            capsize=0, label=arm)
            if ref is not None:
                ax.axhline(ref, color=MUTED, lw=1, ls="--")
            ax.set_xticks(x, labels, rotation=60, ha="right")
            ax.set_ylabel("FPR(H) under H0")
            ax.set_title(title, color=INK)
            ax.grid(axis="y", color=GRID, lw=0.6)
            ax.legend(frameon=False)
        _save(plt, fig, fig_dir, "fpr_inflation")
        g = gains[gains["asset_selection"] == "median"]
        g = g.assign(label=np.where(g["dataset"] == "d5", g["background"],
                                    g["background"] + ":" + g["dataset"].str.replace("_", "", regex=False)))
        fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
        for ax, arm in zip(axes, ARMS):
            df = g[g["arm"] == arm]
            labels = list(dict.fromkeys(df["label"]))
            x = np.arange(len(labels))
            for j, sr in enumerate(sorted(df["sr"].unique())):
                d = df[df["sr"] == sr].set_index("label").reindex(labels)
                err = _bars(d["rmst_ratio"], d["rmst_ratio_lo"], d["rmst_ratio_hi"])
                ax.errorbar(x + (j - 1) * 0.2, d["rmst_ratio"], yerr=err, fmt="o", ms=4, color=SERIES[j % len(SERIES)],
                            elinewidth=1, capsize=0, label=f"SR {sr:g}")
            ax.axhline(1.0, color=MUTED, lw=1, ls="--")
            ax.set_yscale("log")
            ax.set_xticks(x, labels, rotation=60, ha="right")
            ax.set_title(f"median asset vs P3-C, arm {arm}", color=INK)
            ax.grid(axis="y", color=GRID, lw=0.6)
            ax.legend(frameon=False)
        axes[0].set_ylabel("RMST ratio P1-C / P3-C (restricted to H)")
        _save(plt, fig, fig_dir, "gains")
    finally:
        plt.rcParams.update(saved)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=("linear", "jepa"))
    ap.add_argument("--families", required=True, nargs="+", choices=("F1", "F2"))
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--quick", action="store_true", help="reduced replicates and SR grid (the config's quick block)")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "e10")
    ap.add_argument("--fig-dir", type=Path, default=REPO_ROOT / "figures" / "e10")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "e10")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    args = ap.parse_args(argv)
    if args.stage == "jepa":
        ap.error("stage 'jepa' (P5-C) waits for the frozen checkpoint of stream 16")
    if "F2" in args.families:
        ap.error("F2 on D3 is outside this delivery (decision B1): a later plan revision adds it (data_loader.chars)")
    if args.jobs < 1:
        ap.error("--jobs must be >= 1")
    t0 = time.time()
    cfg = yaml.safe_load(args.config.read_text())
    if args.quick:
        cfg.update(sr=cfg["quick"]["sr"], reps=cfg["quick"]["reps"])
    H, alpha, reps, d5 = cfg["H"], cfg["alpha"], cfg["reps"], cfg["d5"]
    sel, gamma = lattice_selection(alpha, H), pl.horizon_gamma(H, alpha)
    families = [("H0", 0)] + [("F1", float(s)) for s in cfg["sr"]]
    cells, tasks = [], []

    def add_cell(kind, info, ctx, n):
        cells.append((info, ctx))
        tasks.extend((kind, ctx, (r0, min(r0 + CHUNK_REPS, n))) for r0 in range(0, n, CHUNK_REPS))

    m = cfg["n_p1"]
    d5_splits = {"calib": (0, d5["T_calib"]), "dates": np.arange(d5["T_calib"] + H).astype("datetime64[D]")}
    d5_spec, d5_exact = p3c_specs(d5["K"], H, gamma, alpha, "d5", d5["K"] + 1)
    ticks = {}
    for name, bg in d5["backgrounds"].items():
        if bg.get("zero_share"):
            ticks[name] = pilot_tick(d5, bg["zero_share"], (crc(f"d5|{name}|tick"), 10 ** 6))
        info = {"background": name, "dataset": "d5", "design": "prospective", "kind": "d5",
                "null": "invalid" if bg.get("shock_w") else "valid", "unit_names": [f"a{i:02d}" for i in range(m)],
                "D": d5["K"] + 1}
        for family, sr in families:
            label = f"d5|{name}|{family}|{sr:g}"
            ctx = {"d5": d5, "bg": bg, "H": H, "gamma": gamma, "sel": sel, "spec": d5_spec, "exact_specs": d5_exact,
                   "splits": d5_splits, "assets": np.arange(m), "crc": crc(label), "family": family, "sr": sr,
                   "tick": ticks.get(name, 0.0), "matched": family == "H0" and bool(bg.get("shock_w")), "label": label}
            add_cell("d5", info, ctx, reps["h0" if family == "H0" else "f1"])
    hashes = {}
    for name in cfg["d6"]:
        X, _, splits, assets = load_real(name)
        K = frozen_fit(name, H, gamma)[0]["rep"].stats["K"]
        spec, exact_specs = p3c_specs(K, H, gamma, alpha, name, K + 1)
        cols = p1_assets(name, X.shape[1], m)
        hashes[name] = _sha256(DERIVED / name / "ret_wide.npy")
        info = {"background": "d6", "dataset": name, "design": "symmetrized", "kind": "d6", "null": "valid",
                "unit_names": [assets[c] for c in cols], "D": K + 1}
        for family, sr in families:
            label = f"d6|{name}|{family}|{sr:g}"
            ctx = {"dataset": name, "H": H, "gamma": gamma, "sel": sel, "spec": spec, "exact_specs": exact_specs,
                   "splits": splits, "assets": cols, "crc": crc(label), "family": family, "sr": sr, "D": K + 1,
                   "label": label}
            add_cell("d6", info, ctx, reps["h0" if family == "H0" else "f1"])
    dims = sorted({info["D"] for info, _ in cells} | {frozen_fit(n, H, gamma)[0]["rep"].stats["K"] + 1
                                                        for n in cfg["raw"]})
    coin_ctx = {"chunk": min(CHUNK_COINS, reps["coins"]), "H": H, "T_calib": d5["T_calib"], "dims": tuple(dims),
                "sel": sel, "gamma": gamma, "crc": crc("coins")}
    n_coin_chunks = -(-reps["coins"] // coin_ctx["chunk"])
    tasks.extend(("coins", coin_ctx, i) for i in range(n_coin_chunks))
    results = run_tasks(tasks, args.jobs)
    by_label, coins = {}, {}
    for (kind, ctx, _), res in zip(tasks, results):
        if kind == "coins":
            for k, (a, n) in res.items():
                coins[k] = (coins.get(k, (0, 0))[0] + a, coins.get(k, (0, 0))[1] + n)
        else:
            by_label.setdefault(ctx["label"], []).extend(res)
    rows, gains, notes = coin_rows(coins, sel, alpha), [], []
    h0_by_background = {}
    for info, ctx in cells:
        res = by_label[ctx["label"]]
        main_res = [r["main"] for r in res]
        gen = rng(ctx["crc"], 10 ** 6 + 1)
        if ctx["family"] == "H0":
            sym = [r["sym"] for r in res] if ctx.get("matched") else None
            rows += cell_rows(info, main_res, sym, cfg, sel, coins, "H0", 0, gen)
            if sym is not None:
                sym_info = {**info, "background": f"{info['background']}:sym", "null": "valid"}
                rows += cell_rows(sym_info, sym, None, cfg, sel, coins, "H0", 0, gen)
            h0_by_background[info["background"], info["dataset"]] = main_res
            notes.append(f"{ctx['label']}: zero share {np.mean([r['zeros'] for r in main_res]):.4f}, "
                         f"ties in z {sum(r['ties_z'] for r in main_res)}")
            continue
        rows += cell_rows(info, main_res, None, cfg, sel, coins, "F1", ctx["sr"], gen)
        h0 = h0_by_background[info["background"], info["dataset"]]
        for arm in ARMS:
            f1 = {"p3": _stack(main_res, ("P3-C", arm, "anytime-valid"))[:, 0],
                  "p1": _stack(main_res, ("P1-C", arm, "anytime-valid"))}
            ref = {"p1": _stack(h0, ("P1-C", arm, "anytime-valid")) >= 0,
                   "p3": _stack(h0, ("P3-C", arm, "anytime-valid"))[:, 0] >= 0}
            for g in gain_rows(f1, ref, H, gen, reps["boot"]):
                g.update(background=info["background"], dataset=info["dataset"], sr=ctx["sr"], arm=arm,
                         asset=info["unit_names"][g["asset_index"]], null_valid=info["null"])
                gains.append(g)
    for name in cfg["raw"]:
        raw, ctx = raw_rows(name, cfg, sel, jobs=args.jobs, coins=coins)
        rows += raw
        hashes[name] = _sha256(DERIVED / name / "ret_wide.npy")
        notes.append(f"raw|{name}: frozen basis {ctx['state_hash']} matches the committed sidecar; "
                     f"{rows[-1]['n']} windows of {H} days, retrospective (fit on the later calib rows)")
    args.out.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    cells_df = pd.DataFrame(rows, columns=CELL_COLUMNS)
    gains_df = pd.DataFrame(gains, columns=GAIN_COLUMNS)
    pl.save_fair_csv(cells_df, args.out / "e10_cells.csv")
    pl.save_fair_csv(gains_df, args.out / "e10_gains.csv")
    plot(args.out, args.fig_dir)
    k, n = coins[("single", "half", "exact")]
    tol = iid_tolerance(k, n, sel["level"])
    shown = " ".join(argv) if argv is not None else " ".join(sys.argv[1:])
    lines = [f"command: python experiments/e10_robustness.py {shown}",
             f"config: {args.config.name} sha256 {_sha256(args.config)} (quick={args.quick}); jobs {args.jobs}",
             f"lattice: H={H}, delta={DELTA}, units L={sel['units']}, threshold {sel['threshold']:.6g}, "
             f"exact level {sel['level']:.12g}; gamma_H = H / alpha = {gamma:g}",
             f"fpr_iid_mc (Monte Carlo estimate, iid scenario; half, exact, single stream): {k}/{n} = {k / n:.5f}; "
             f"99 % binomial tolerance [{tol['lo']:.5f}, {tol['hi']:.5f}] -> "
             f"{'within' if tol['within'] else 'OUTSIDE'}",
             *(f"input {name}: ret_wide.npy sha256 {h}" for name, h in sorted(hashes.items())),
             *(f"tick {name}: {t:.6g}" for name, t in sorted(ticks.items())), *notes,
             "labels: reference_kind in " + ", ".join(REFERENCE_KINDS) + "; design in " + ", ".join(DESIGNS),
             "zero_neg arms: invalid sign-stream null on backgrounds with zeros, no FPR guarantee",
             "raw placebo: retrospective and descriptive; half refers to the symmetrized window (same state), "
             "qhat and zero_neg rows are descriptive contrasts without fpr_ref or inflation",
             "fpr_pred_iid: iid-bit reference at the observed mean bit rate, reported as pred_gap without criterion",
             "gains: RMST ratio restricted to H (a lower bound of the ADD ratio only when P3-C is never censored); "
             "oracle assets are exploratory; no equal-false-alarm claim (decision B2)",
             f"rows: {len(cells_df)} cells, {len(gains_df)} gains",
             *(f"{p.name} sha256 {_sha256(p)}" for p in (args.out / "e10_cells.csv", args.out / "e10_gains.csv")),
             f"duration: {time.time() - t0:.0f} s"]
    (args.log_dir / "run.log").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
