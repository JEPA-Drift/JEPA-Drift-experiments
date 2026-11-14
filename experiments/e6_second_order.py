"""Stream 23: E6 phase 1, second-order F4 drifts monitored by the P1-D and P3-D energy CUSUMs (milestone J3).

Backgrounds (prompts/plans/plan-23.md)
  D6  calib rows of d3_239 (941 days, 2016-04-07..2019-12-31). One Rademacher sign per day leaves every even energy
      unchanged bit for bit, so the raw rows serve, with no sign-flip pseudo-sample; representation, moments,
      thresholds and evaluation share these days: in-sample, descriptive, CI = NA. Each window start s is an
      equivalent counterfactual onset: F4 is injected once from the first calib day with the matrix fitted on the clean
      calib rows, the same for every onset; F4 and the streams act day by day and the CUSUM restarts from 0 at s.
  D5  independent GARCH(0.08, 0.90)-t7 panels, N = 239, equicorrelated factor rho = 0.40, seed roles
      SeedSequence([23, role, i]): 0 fit panel (941 days), 1 calibration panels, 2 test panels (500 days each).
Monitors: strict one-sided CUSUM, delta = 0.5; threshold = smallest lambda with FPR(H) <= alpha on the null paths
  P1-D  Article B energy stream (r_t^2 - mean(r^2)) / std(r^2) of the equal-weighted index, moments on the fit rows
  P3-D  residual energy of PCAOrthogonal (factor PC2..PC(K+1), full PC2..PCN) through pipelines.run_pipeline
Drifts: injection.inject F4 with I_target=None; meta["info"] is the Gaussian design information, not the exact KL.
Delays restricted to H (censored runs count H); G_ADD = RMST_H(P1-D) / RMST_H(P3-D), paired on windows or panels.
Outputs: results/e6/e6_cells_phase1.csv, figures/e6/*.{png,pdf} drawn from the CSV only, logs/e6/phase1.log (local).

Usage: python experiments/e6_second_order.py --phase 1 --out results/e6
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"
os.environ["MPLBACKEND"] = "Agg"

import argparse
import concurrent.futures
import hashlib
import json
import math
import multiprocessing
import sys
import time
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors, sim
from jepadrift import pipelines as pl
from jepadrift.injection import inject
from jepadrift.monitors import cusum, streams
from jepadrift.monitors.gamma import gamma_spectral, required_threshold

STREAM = 23
REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "e6.yaml"
DERIVED = REPO_ROOT / "data" / "derived"
MONITOR_START = np.datetime64("2020-01-01")
DELTA, ALPHA = pl.ENERGY_DELTA, pl.TARGET_FPR
Z95 = NormalDist().inv_cdf(0.975)
MIN_BLOCKS = 10
MODE_DAYS = 7
D5_CHUNK = pl.CHUNK
LABELS = ("P1-D", "P3-D factor", "P3-D full", "P3-D factor K=1")
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
MARKERS = ("o", "s", "^", "D")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e5e4e0"
IN_SAMPLE = "in-sample: the threshold is fitted on these windows; descriptive FPR, no inferential CI"
COLUMNS = ["background", "H", "monitor", "mode", "K", "K_choice", "D", "cell", "family", "params", "role", "status",
           "threshold_rule", "in_sample", "threshold", "lam_iid", "gamma_op", "gamma_spec", "q_null_mean", "q_null_sd",
           "n_runs", "fpr", "fpr_lo", "fpr_hi", "fpr_region_lo", "fpr_region_hi", "fpr_verdict", "tie_share",
           "det_rate", "det_lo", "det_hi", "rmst_h", "censored_share", "median_delay", "cond_mean", "dq_mean",
           "info_gauss", "info_model", "n_directions", "info_per_direction", "budget_days", "budget_role", "g_add",
           "g_label", "g_lo", "g_hi", "ci_method", "ci_reason", "alarm_mode_date", "alarm_mode_share"]
TEXT = {"background", "monitor", "mode", "K_choice", "cell", "family", "params", "role", "status", "threshold_rule",
        "fpr_verdict", "info_model", "budget_role", "g_label", "ci_method", "ci_reason", "alarm_mode_date"}
_windows = np.lib.stride_tricks.sliding_window_view


def load_config(path=CONFIG, quick=False):
    """The E6 configuration as a dict; `quick` applies its `quick` block (sizes only)."""
    cfg = yaml.safe_load(Path(path).read_text())
    if quick:
        cfg["n_boot"] = cfg["quick"]["n_boot"]
        cfg["d5"].update(cfg["quick"]["d5"])
    return cfg


def load_d6(name="d3_239", last_day="2019-12-31", load=np.load):
    """Finite d3_239 rows from the first pretrain day to last_day and their splits; one memmap slice, 2020+ refused."""
    if name != "d3_239":
        raise ValueError(f"D6 reads d3_239 only, got {name!r}")
    if np.isnat(np.datetime64(last_day)):
        raise ValueError(f"last_day must be a date, got {last_day}")
    # ponytail: refuses 2020+ outright; accept them only once stream 21's configs/FROZEN.json exists and matches
    if np.datetime64(last_day) >= MONITOR_START:
        raise ValueError(f"rows dated 2020-01-01 or later are refused before J4 (no frozen configuration), got {last_day}")
    d = DERIVED / name
    dates = load(d / "dates.npy")
    if dates.ndim != 1 or dates.size == 0 or np.isnat(dates).any() or (dates[1:] <= dates[:-1]).any():
        raise ValueError(f"{name}: dates.npy is not a non-empty, NaT-free, strictly increasing calendar")
    sp = yaml.safe_load((d / "splits.yaml").read_text())
    first = pl.split_rows(dates, sp)["pretrain"][0]
    stop = int(np.searchsorted(dates, np.datetime64(last_day), side="right"))
    if not 0 <= first < stop <= dates.size:
        raise ValueError(f"{name}: rows [{first}, {stop}) are not a non-empty range of the {dates.size} calendar days")
    ret = load(d / "ret_wide.npy", mmap_mode="r")
    if ret.ndim != 2 or ret.shape[0] != dates.size:
        raise ValueError(f"{name}: return panel of shape {ret.shape} for {dates.size} calendar days")
    X, days = np.array(ret[first:stop], order="C"), dates[first:stop]
    del ret
    if not np.isfinite(X).all():
        raise ValueError(f"{name}: rows {days[0]}..{days[-1]} hold non-finite returns")
    return X, days, pl.split_rows(days, sp)


def p1d_moments(X_fit):
    """Article B moments of the equal-weighted index r on drift-free rows: (mean(r^2), std(r^2)), R01 l.271-273."""
    r2 = X_fit.mean(axis=1) ** 2
    return float(np.mean(r2)), float(np.std(r2))


def p1d_stream(X, mu, sd):
    """P1-D: Article B energy stream (r_t^2 - mu) / sd of the equal-weighted index r_t of X (..., T, N)."""
    return streams.energy_stream(X.mean(axis=-1), mu, sd)


def p3d_stream(state, X):
    """P3-D residual energy of the rows of X under a fitted P3-D state."""
    z = state["rep"].transform_panel(np.ascontiguousarray(X))["z_even"]
    return pl.residual_energy(z, state["channels"]["residual"])


def cell_injection(X, cell, tau, calib):
    """F4 cell injected from row tau by injection.inject with I_target=None: (X_tilde, M, meta)."""
    rng = np.random.default_rng(np.random.SeedSequence([STREAM, 6]))
    return inject(X, cell["family"], tau, None, {"calib": tuple(calib), **cell["params"]}, rng)


def iid_threshold(D, H, n, key):
    """lambda_iid: required threshold of the strict CUSUM on n i.i.d. paths (chi2_D - D) / sqrt(2 D) of length H."""
    rng = np.random.default_rng(np.random.SeedSequence(key))
    return required_threshold((rng.chisquare(D, size=(n, H)) - D) / math.sqrt(2.0 * D), DELTA, ALPHA, "fpr", H)


def first_alarms(q, lam):
    """First-alarm offsets of the strict one-sided CUSUM (delta = 0.5) along the last axis; -1 without alarm."""
    return cusum.strict_cusum_vec(q, DELTA, lam)


def delays(off):
    """Delays offset + 1 (monitored days up to the alarm included, C-pipe-delay); NaN without alarm."""
    return np.where(off >= 0, off + 1.0, np.nan)


def delay_summary(d, H):
    """Restricted mean RMST_H (censored runs count H), detection rate, censored share, median and conditional mean."""
    d = np.asarray(d, dtype=np.float64)
    hit = ~np.isnan(d)
    med = float(np.median(np.where(hit, d, np.inf)))
    return {"n": int(d.size), "det_rate": float(hit.mean()), "censored_share": float(1.0 - hit.mean()),
            "rmst_h": float(np.where(hit, d, float(H)).mean()), "median_delay": med if math.isfinite(med) else math.nan,
            "median_above_h": not math.isfinite(med), "cond_mean": float(d[hit].mean()) if hit.any() else math.nan}


def g_add(d_a, d_b, H):
    """RMST_H(A) / RMST_H(B) and its label: exact (no censoring), lower_bound (A censored only), undetermined (B censored)."""
    a, b = delay_summary(d_a, H), delay_summary(d_b, H)
    label = "undetermined" if b["censored_share"] > 0 else "lower_bound" if a["censored_share"] > 0 else "exact"
    return a["rmst_h"] / b["rmst_h"], label


def wilson(k, n, z=Z95):
    """Wilson score interval (95 % by default) of the binomial proportion k / n."""
    root = z * math.sqrt(z * z + 4.0 * k * (n - k) / n)
    den = 2.0 * (n + z * z)
    return max(0.0, (2.0 * k + z * z - root) / den), min(1.0, (2.0 * k + z * z + root) / den)


def paired_bootstrap(d_a, d_b, H, B, rng):
    """95 % percentile interval of RMST_H(A) / RMST_H(B) over B paired resamples of the runs."""
    a, b = (np.where(np.isnan(d), float(H), d) for d in (np.asarray(d_a), np.asarray(d_b)))
    idx = rng.integers(0, len(a), size=(B, len(a)))
    lo, hi = np.quantile(a[idx].mean(axis=1) / b[idx].mean(axis=1), [0.025, 0.975])
    return float(lo), float(hi)


def d6_ci_reason(n_windows, H):
    """IC=NA reason of the prespecified reporting criterion; None from MIN_BLOCKS blocks of length H on."""
    blocks = n_windows / H
    if blocks >= MIN_BLOCKS:
        return None
    return (f"IC=NA: windows less than H = {H} days apart share days and volatility clustering extends the dependence; "
            f"conservative prespecified reporting criterion of the protocol (plan-23, Q5), not a general requirement "
            f"of a block bootstrap or a deff: no D6 CI below {MIN_BLOCKS} blocks of length >= H; "
            f"here {n_windows} windows / H = {blocks:.2f} blocks")


def tie_share(peaks, lam):
    """Next attainable in-sample level above the threshold: share of null peaks above lam (1 - 1e-6)."""
    return float((np.asarray(peaks) > lam * (1.0 - 1e-6)).mean())


def alarm_mode(dates):
    """Most frequent alarm date and the share of alarms within MODE_DAYS days of it; ('', nan) without alarm."""
    dates = np.asarray(dates, dtype="datetime64[D]")
    if dates.size == 0:
        return "", math.nan
    u, c = np.unique(dates, return_counts=True)
    m = u[c.argmax()]
    return str(m), float((np.abs((dates - m).astype(np.int64)) <= MODE_DAYS).mean())


def d5_panel(role, i, T, g):
    """D5 panel (T, N) of seed role `role` (0 fit, 1 calibration, 2 test) and index i: SeedSequence([23, role, i])."""
    rng = np.random.default_rng(np.random.SeedSequence([STREAM, int(role), int(i)]))
    return sim.garch_panel(T, g["N"], g["alpha"], g["beta"], g["nu"], rng, factor_rho=g["factor_rho"], burn=g["burn"])


def _row(**kw):
    row = {c: "" if c in TEXT else math.nan for c in COLUMNS}
    row.update(kw)
    return row


def _cell_fields(cell, meta, H, status):
    """Cell identity and Gaussian design information: joint for a rotation, also per direction for a deformation."""
    sub, info = cell["params"].get("subspace"), float(meta["info"])
    return {"cell": cell["name"], "family": cell["family"], "params": json.dumps(cell["params"], sort_keys=True),
            "role": cell["role"], "status": cell[status], "info_gauss": info, "info_model": "gaussian_design",
            "n_directions": len(sub) if sub else 2, "info_per_direction": info / len(sub) if sub else math.nan,
            "budget_days": floors.evidence_budget(H / ALPHA, info), "budget_role": "design_reference"}


def _delay_fields(d, H):
    s = delay_summary(d, H)
    return {k: s[k] for k in ("det_rate", "rmst_h", "censored_share", "median_delay", "cond_mean")}


def _fit_p3d(mode, K, H, dataset, X, splits, n_iid, key):
    spec = pl.make_spec("P3-D", mode=mode, K=K, H=H, dataset=dataset, N_cal=n_iid)
    return spec, pl.fit_pipeline(spec, X, splits, key=key)


def _rep(fit, m, Hs):
    """Representation shared by the fits of monitor m at every H (same rows, same configuration)."""
    reps = [fit[m, H][1]["rep"] for H in Hs]
    if len({r.state_hash() for r in reps}) != 1:
        raise ValueError(f"{m}: the representations fitted at H = {Hs} differ")
    return reps[0]


def _p3d_offsets(spec, state, Z, recs, lam=None):
    """First-alarm offsets of P3-D by pipelines.run_pipeline on a Z dict, at the state's threshold or at lam."""
    rows = pl.run_pipeline(spec, Z, {}, recs, state if lam is None else {**state, "threshold": lam})
    return np.where(rows["detected"].to_numpy(), (rows["alarm_index"] - rows["tau_star"]).to_numpy(), -1)


def run_d6(cfg, log):
    """D6 rows: calib rows, in-sample thresholds, an equivalent counterfactual onset per window start; CI = NA."""
    name, Hs = cfg["d6"]["dataset"], cfg["H"]
    X, days, splits = load_d6(name, cfg["d6"]["last_day"])
    a, b = splits["calib"]
    Xc, T = np.ascontiguousarray(X[a:b]), b - a
    mu, sd = p1d_moments(Xc)
    log.append(f"D6 {name}: rows {days[0]}..{days[-1]}; calib rows [{a}, {b}) = {days[a]}..{days[b - 1]} ({T} days); "
               f"P1-D mean(r^2) {mu:.6g}, std(r^2) {sd:.6g}, std / (sqrt(2) mean) {sd / (math.sqrt(2.0) * mu):.4f}")
    log.append(f"D6 {name}: sha256 of the {X.shape[0]} x {X.shape[1]} return rows read, C order "
               f"{hashlib.sha256(X.tobytes()).hexdigest()}")
    modes = list(cfg["d6"]["modes"])
    fit = {(m, H): _fit_p3d(m, "mp", H, name, X, splits, cfg["n_iid"], [STREAM, 5, H, k])
           for H in Hs for k, m in enumerate(modes)}
    reps = {m: _rep(fit, m, Hs) for m in modes}
    cols = {m: fit[m, Hs[0]][1]["channels"]["residual"] for m in modes}
    q0 = {"ew": p1d_stream(Xc, mu, sd), **{m: p3d_stream(fit[m, Hs[0]][1], Xc) for m in modes}}
    cal = {}
    for H in Hs:
        lam = required_threshold(_windows(q0["ew"], H), DELTA, ALPHA, "fpr", H)
        lam_iid = iid_threshold(1, H, cfg["n_iid"], [STREAM, 3, H])
        cal["ew", H] = {"threshold": lam, "lam_iid": lam_iid, "gamma_op": lam / lam_iid,
                        "gamma_spec": gamma_spectral(q0["ew"]), "K": math.nan, "D": 1}
        for m in modes:
            st = fit[m, H][1]
            cal[m, H] = {"threshold": st["threshold"], "lam_iid": st["lam_iid"], "gamma_op": st["gamma_op"],
                         "gamma_spec": st["gamma_spec"], "K": float(st["rep"].stats["K"]) if m == "factor" else math.nan,
                         "D": len(cols[m])}
        for m in ("ew", *modes):
            peaks = cusum.cusum_trajectory_vec(_windows(q0[m], H), DELTA).max(axis=1)
            cal[m, H]["tie"] = tie_share(peaks, cal[m, H]["threshold"])
    conds = [None] + list(cfg["cells"])
    res, metas = {}, {}
    for ci, cell in enumerate(conds):
        if cell is None:
            Xd = Xc
        else:
            Xt, _, metas[ci] = cell_injection(X, cell, a, (a, b))
            Xd = np.ascontiguousarray(Xt[a:b])
        data = {"ew": (p1d_stream(Xd, mu, sd), None)}
        for m in modes:
            Z = reps[m].transform_panel(Xd)
            data[m] = (pl.residual_energy(Z["z_even"], cols[m]), Z)
        for H in Hs:
            fam = "H0" if cell is None else cell["family"]
            recs = [{"seed": [STREAM, 7, ci, s], "tau_star": s, "family": fam} for s in range(T - H + 1)]
            for m, (q, Z) in data.items():
                off = (first_alarms(_windows(q, H), cal[m, H]["threshold"]) if Z is None
                       else _p3d_offsets(*fit[m, H], Z, recs))
                res[ci, H, m] = off, float(q.mean() - q0[m].mean())
    rows = []
    for H in Hs:
        n_w = T - H + 1
        for ci, cell in enumerate(conds):
            ref = None
            for m in ("ew", *modes):
                c, (off, dq) = cal[m, H], res[ci, H, m]
                row = _row(background=f"d6_{name}", H=H, monitor="P1-D" if m == "ew" else "P3-D", mode=m, K=c["K"],
                           K_choice="mp" if m == "factor" else "", D=c["D"], threshold_rule="calib_windows_in_sample",
                           in_sample=True, threshold=c["threshold"], lam_iid=c["lam_iid"], gamma_op=c["gamma_op"],
                           gamma_spec=c["gamma_spec"], q_null_mean=float(q0[m].mean()), q_null_sd=float(q0[m].std()),
                           n_runs=n_w, tie_share=c["tie"], ci_method="none")
                if cell is None:
                    row.update(cell="H0", family="H0", role="null", status="descriptive",
                               fpr=float((off >= 0).mean()), ci_reason=IN_SAMPLE)
                    rows.append(row)
                    continue
                reason = d6_ci_reason(n_w, H)
                if reason is None:
                    raise ValueError(f"{n_w} windows at H = {H} would allow a D6 CI: the block bootstrap is not implemented")
                d, hit = delays(off), off >= 0
                mode_date, mode_share = alarm_mode(days[a + np.flatnonzero(hit) + off[hit]])
                row.update(**_cell_fields(cell, metas[ci], H, "status_d6"), **_delay_fields(d, H), dq_mean=dq,
                           ci_reason=reason, alarm_mode_date=mode_date, alarm_mode_share=mode_share)
                if ref is None:
                    ref = d
                else:
                    row.update(zip(("g_add", "g_label"), g_add(ref, d, H)))
                rows.append(row)
    return rows


def _d5_stream(ctx, m, X):
    """(q, Z) of monitor m on panels X (n, T, N): P1-D (Z = None) or the P3-D residual energy and its Z dict."""
    if m == "ew":
        return p1d_stream(X, ctx["mu"], ctx["sd"]), None
    n, T, N = X.shape
    Z = ctx["reps"][m].transform_panel(np.ascontiguousarray(X.reshape(n * T, N)))
    return pl.residual_energy(Z["z_even"], ctx["cols"][m]).reshape(n, T), Z


def _d5_task(task):
    """One chunk of D5 panels: monitor streams of calibration panels ('cal'), or first alarms and stream means of every
    condition on test panels ('test')."""
    kind, idx, ctx = task
    X = np.stack([d5_panel(1 if kind == "cal" else 2, i, ctx["Tp"], ctx["g"]) for i in idx])
    if kind == "cal":
        return {m: _d5_stream(ctx, m, X)[0] for m in ctx["mons"]}
    out = {}
    conds = [("H0", "H0", None)] + [(c["name"], c["family"], ctx["Ms"][c["name"]]) for c in ctx["cells"]]
    for ci, (name, family, M) in enumerate(conds):
        Xd = X if M is None else X @ M.T
        recs = [{"seed": [STREAM, 8, ci, i], "tau_star": k * ctx["Tp"], "family": family} for k, i in enumerate(idx)]
        for m in ctx["mons"]:
            q, Z = _d5_stream(ctx, m, Xd)
            for H in ctx["H"]:
                out["qmean", name, m, H] = q[:, :H].mean(axis=1)
                rules = [("main", ctx["lam"][m, H])] + ([("d6rule", ctx["lam_in"][m, H])] if M is None else [])
                for rule, lam in rules:
                    out["off", name, m, H, rule] = (first_alarms(q[:, :H], lam) if Z is None
                                                    else _p3d_offsets(*ctx["states"][m, H], Z, recs, lam))
    return out


def _map(fn, tasks, jobs):
    """fn over tasks in order, on `jobs` spawned processes when jobs > 1; results do not depend on jobs."""
    if jobs <= 1 or len(tasks) <= 1:
        return [fn(t) for t in tasks]
    with concurrent.futures.ProcessPoolExecutor(min(jobs, len(tasks)), mp_context=multiprocessing.get_context("spawn")) as pool:
        return list(pool.map(fn, tasks))


def run_d5(cfg, jobs, log):
    """D5 rows: thresholds on independent calibration panels, attained FPR and delays on disjoint test panels."""
    g, Hs, n_iid = cfg["d5"], cfg["H"], cfg["n_iid"]
    Ts, Tp = g["T_fit"], g["T_panel"]
    if max(Hs) > Tp:
        raise ValueError(f"D5 panels of {Tp} days cannot hold H = {max(Hs)}")
    P0 = d5_panel(0, 0, Ts, g)
    sp5 = {"calib": (0, Ts), "pretrain": (0, 0), "pre_monitor": (0, Ts), "dates": np.arange(Ts).astype("datetime64[D]")}
    mu, sd = p1d_moments(P0)
    mons = {"ew": ("ew", None, "")}
    mons.update({f"factor_K{K}": ("factor", int(K), choice) for K, choice in g["factor_K"].items()})
    mons["full"] = ("full", None, "")
    p3d = [m for m in mons if m != "ew"]
    fit = {(m, H): _fit_p3d(mons[m][0], mons[m][1] or "mp", H, "d5_garch_t7", P0, sp5, n_iid, [STREAM, 5, H, 10 + k])
           for H in Hs for k, m in enumerate(p3d)}
    reps = {m: _rep(fit, m, Hs) for m in p3d}
    cols = {m: fit[m, Hs[0]][1]["channels"]["residual"] for m in p3d}
    q_fit = p1d_stream(P0, mu, sd)
    log.append(f"D5: fit panel SeedSequence([{STREAM}, 0, 0]) of {Ts} days; P1-D mean(r^2) {mu:.6g}, std(r^2) {sd:.6g}, "
               f"std / (sqrt(2) mean) {sd / (math.sqrt(2.0) * mu):.4f}; {g['n_cal']} calibration and {g['n_test']} test "
               f"panels of {Tp} days")
    T0 = d5_panel(2, 0, Tp, g)
    Ms, metas = {}, {}
    for cell in cfg["cells"]:
        _, Ms[cell["name"]], metas[cell["name"]] = cell_injection(np.vstack([P0, T0]), cell, Ts, (0, Ts))
    ctx = {"g": g, "Tp": Tp, "H": Hs, "mu": mu, "sd": sd, "mons": list(mons), "reps": reps, "cols": cols,
           "cells": cfg["cells"], "Ms": Ms}

    def chunks(n):
        return [list(range(i, min(n, i + D5_CHUNK))) for i in range(0, n, D5_CHUNK)]

    parts = _map(_d5_task, [("cal", idx, ctx) for idx in chunks(g["n_cal"])], jobs)
    Q = {m: np.concatenate([p[m] for p in parts]) for m in mons}
    cal = {}
    for H in Hs:
        for m in mons:
            if m == "ew":
                base = {"lam_iid": iid_threshold(1, H, n_iid, [STREAM, 3, H]),
                        "lam_in": required_threshold(_windows(q_fit, H), DELTA, ALPHA, "fpr", H),
                        "gamma_spec": gamma_spectral(q_fit), "D": 1, "K": math.nan}
            else:
                st = fit[m, H][1]
                base = {"lam_iid": st["lam_iid"], "lam_in": st["threshold"], "gamma_spec": st["gamma_spec"],
                        "D": len(cols[m]), "K": float(mons[m][1]) if mons[m][1] else math.nan}
            cal[m, H] = {**base, "threshold": required_threshold(Q[m][:, :H], DELTA, ALPHA, "fpr", H),
                         "q_null_mean": float(Q[m][:, :H].mean()), "q_null_sd": float(Q[m][:, :H].std())}
    ctx.update(lam={k: v["threshold"] for k, v in cal.items()}, lam_in={k: v["lam_in"] for k, v in cal.items()},
               states=fit)
    parts = _map(_d5_task, [("test", idx, ctx) for idx in chunks(g["n_test"])], jobs)
    res = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    rows = []
    for H in Hs:
        for ci, cell in enumerate([None] + list(cfg["cells"])):
            name, ref = "H0" if cell is None else cell["name"], None
            for m, (mode, _, choice) in mons.items():
                c = cal[m, H]
                common = {"background": "d5_garch_t7", "H": H, "monitor": "P1-D" if m == "ew" else "P3-D", "mode": mode,
                          "K": c["K"], "K_choice": choice, "D": c["D"], "in_sample": False, "lam_iid": c["lam_iid"],
                          "gamma_spec": c["gamma_spec"], "q_null_mean": c["q_null_mean"],
                          "q_null_sd": c["q_null_sd"], "n_runs": g["n_test"]}
                hit = res["off", name, m, H, "main"] >= 0
                if cell is None:
                    s = pl.summarize(pd.DataFrame({"detected": hit}), ALPHA, "~", g["n_cal"])
                    rows.append(_row(**common, cell="H0", family="H0", role="null", status="prespecified",
                                     threshold_rule="d5_calibration_panels", threshold=c["threshold"],
                                     gamma_op=c["threshold"] / c["lam_iid"], fpr=float(hit.mean()),
                                     **dict(zip(("fpr_lo", "fpr_hi"), wilson(int(hit.sum()), hit.size))),
                                     fpr_region_lo=s["lo"], fpr_region_hi=s["hi"],
                                     fpr_verdict="PASS" if s["ok"] else "FAIL", ci_method="wilson"))
                    hit_in = res["off", name, m, H, "d6rule"] >= 0
                    rows.append(_row(**common, cell="H0", family="H0", role="null", status="prespecified",
                                     threshold_rule="d6_rule_on_fit_panel", threshold=c["lam_in"],
                                     gamma_op=c["lam_in"] / c["lam_iid"], fpr=float(hit_in.mean()),
                                     **dict(zip(("fpr_lo", "fpr_hi"), wilson(int(hit_in.sum()), hit_in.size))),
                                     ci_method="wilson", ci_reason="D6 in-sample rule on the fit panel, evaluated out of "
                                                                   "sample on the test panels"))
                    continue
                d = delays(res["off", name, m, H, "main"])
                row = _row(**common, **_cell_fields(cell, metas[name], H, "status_d5"), **_delay_fields(d, H),
                           threshold_rule="d5_calibration_panels", threshold=c["threshold"],
                           gamma_op=c["threshold"] / c["lam_iid"],
                           **dict(zip(("det_lo", "det_hi"), wilson(int(hit.sum()), hit.size))),
                           dq_mean=float(res["qmean", name, m, H].mean() - res["qmean", "H0", m, H].mean()),
                           ci_method="wilson")
                if ref is None:
                    ref = d
                else:
                    gv, label = g_add(ref, d, H)
                    lo, hi = paired_bootstrap(ref, d, H, cfg["n_boot"],
                                              np.random.default_rng(np.random.SeedSequence([STREAM, 4, ci, H])))
                    row.update(g_add=gv, g_label=label, g_lo=lo, g_hi=hi, ci_method="paired_bootstrap_percentile")
                rows.append(row)
    return rows


def read_cells(path):
    """The cells CSV with 'NaN' as the only missing value, so that empty and 'none' texts stay texts."""
    return pd.read_csv(path, float_precision="round_trip", keep_default_na=False, na_values=["NaN"])


def _series(df):
    lab = np.where(df["monitor"] == "P1-D", "P1-D", "P3-D " + df["mode"])
    return np.where(df["K_choice"] == "sensitivity", lab + " K=1", lab)


def _save(plt, fig, fig_dir, stem):
    fig.tight_layout()
    fig.savefig(fig_dir / f"{stem}.png", dpi=150)
    fig.savefig(fig_dir / f"{stem}.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def plot(csv, fig_dir):
    """Two figures drawn from the cells CSV only, PNG + PDF: detection rate and RMST_H per cell, and G_ADD."""
    import matplotlib.pyplot as plt
    saved = dict(plt.rcParams)
    plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
                         "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "axes.titlesize": 8})
    df = read_cells(csv)
    df["series"] = _series(df)
    drift = df[df.cell != "H0"]
    cells, bgs, Hs = list(dict.fromkeys(drift.cell)), list(dict.fromkeys(df.background)), sorted(set(df.H))
    x = np.arange(len(cells))
    fig_dir.mkdir(parents=True, exist_ok=True)

    def cut(bg, H, label):
        return drift[(drift.background == bg) & (drift.H == H) & (drift.series == label)].set_index("cell").reindex(cells)

    fig, axes = plt.subplots(2 * len(bgs), len(Hs), figsize=(5.2 * len(Hs), 5.6 * len(bgs)), squeeze=False)
    for r, bg in enumerate(bgs):
        hollow = bg.startswith("d6")
        for c, H in enumerate(Hs):
            for k, label in enumerate(LABELS):
                g = cut(bg, H, label)
                if g.series.isna().all():
                    continue
                xs = x + (k - 1.5) * 0.18
                for row, col, ci in ((2 * r, "det_rate", ("det_lo", "det_hi")), (2 * r + 1, "rmst_h", None)):
                    ax = axes[row, c]
                    ax.plot(xs, g[col], ls="none", marker=MARKERS[k], ms=4, color=SERIES[k],
                            mfc="none" if hollow else SERIES[k], label=label)
                    if ci and g[ci[0]].notna().any():
                        ax.vlines(xs, g[ci[0]], g[ci[1]], color=SERIES[k], lw=0.8)
            note = "in-sample, descriptive" if hollow else "Wilson 95 % CI"
            axes[2 * r, c].set(ylim=(-0.02, 1.02), ylabel="detection rate within H", title=f"{bg}, H = {H}: {note}")
            axes[2 * r + 1, c].set(ylim=(0, 1.04 * H), ylabel="RMST_H (days)",
                                   title=f"{bg}, H = {H}: censored runs count H")
            for ax in axes[2 * r:2 * r + 2, c]:
                ax.set_xticks(x, cells, rotation=60, ha="right", fontsize=6)
        axes[2 * r, 0].legend()
    _save(plt, fig, fig_dir, "e6_phase1_delays")

    fig, axes = plt.subplots(len(bgs), len(Hs), figsize=(5.2 * len(Hs), 3.2 * len(bgs)), squeeze=False)
    for r, bg in enumerate(bgs):
        hollow = bg.startswith("d6")
        for c, H in enumerate(Hs):
            ax = axes[r, c]
            for k, label in enumerate(LABELS[1:], start=1):
                g = cut(bg, H, label)
                if g.series.isna().all():
                    continue
                xs = x + (k - 2) * 0.22
                ax.plot(xs, g.g_add, ls="none", marker=MARKERS[k], ms=4, color=SERIES[k],
                        mfc="none" if hollow else SERIES[k], label=f"P1-D -> {label}")
                if g.g_lo.notna().any():
                    ax.vlines(xs, g.g_lo, g.g_hi, color=SERIES[k], lw=0.8)
            ax.axhline(1.0, color=MUTED, lw=0.8)
            ax.set_yscale("log")
            ax.set_xticks(x, cells, rotation=60, ha="right", fontsize=6)
            ax.set(ylabel="G_ADD = RMST_H(P1-D) / RMST_H(P3-D)",
                   title=f"{bg}, H = {H}: " + ("descriptive, CI = NA" if hollow else "95 % paired bootstrap CI"))
        axes[r, 0].legend()
    _save(plt, fig, fig_dir, "e6_phase1_gadd")
    plt.rcParams.update(saved)


def _summary(df):
    """Log lines: thresholds, Gamma_z^op and attained FPR of every null row, then detection and G_ADD per cell."""
    lines = []
    for r in df[df.cell == "H0"].itertuples():
        k = "" if math.isnan(r.K) else f" K={int(r.K)}"
        ci = "" if math.isnan(r.fpr_lo) else f" [{r.fpr_lo:.4f}, {r.fpr_hi:.4f}]"
        region = f" region [{r.fpr_region_lo:.4f}, {r.fpr_region_hi:.4f}] {r.fpr_verdict}" if r.fpr_verdict else ""
        tie = "" if math.isnan(r.tie_share) else f", next attainable level {r.tie_share:.4f}"
        lines.append(f"{r.background} H={r.H} {r.monitor} {r.mode}{k} {r.threshold_rule}: lambda {r.threshold:.6g}, "
                     f"lambda_iid {r.lam_iid:.6g}, Gamma_op {r.gamma_op:.4g}, Gamma_spec {r.gamma_spec:.4g}, q null mean "
                     f"{r.q_null_mean:.4g} sd {r.q_null_sd:.4g}; FPR {r.fpr:.4f}{ci}{region}{tie}")
    for r in df[df.cell != "H0"].itertuples():
        k = "" if math.isnan(r.K) else f" K={int(r.K)}"
        g = "" if math.isnan(r.g_add) else f", G_ADD {r.g_add:.4g} {r.g_label}"
        g += "" if math.isnan(r.g_lo) else f" [{r.g_lo:.4g}, {r.g_hi:.4g}]"
        mode = f", alarms near {r.alarm_mode_date} {r.alarm_mode_share:.2f}" if r.alarm_mode_date else ""
        lines.append(f"{r.background} H={r.H} {r.cell} ({r.status}) {r.monitor} {r.mode}{k}: info {r.info_gauss:.4g}, "
                     f"dq {r.dq_mean:+.4g}, det {r.det_rate:.3f}, RMST_H {r.rmst_h:.1f}{g}{mode}")
    return lines


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _shown(arg):
    p = Path(arg)
    return str(p.relative_to(REPO_ROOT)) if p.is_absolute() and p.is_relative_to(REPO_ROOT) else str(arg)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", type=int, choices=(1, 2), required=True)
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--quick", action="store_true", help="smoke test: the config's quick sizes; figures and log under --out")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "e6")
    ap.add_argument("--fig-dir", type=Path)
    ap.add_argument("--log-dir", type=Path)
    ap.add_argument("--jobs", type=int, default=os.cpu_count(), help="processes for the D5 panels")
    args = ap.parse_args(argv)
    if args.phase == 2:
        ap.error("phase 2 (P5-D, even head of CA-T-JEPA) waits for stream 16")
    if args.jobs < 1:
        ap.error("--jobs must be >= 1")
    fig_dir = args.fig_dir or (args.out / "figures" if args.quick else REPO_ROOT / "figures" / "e6")
    log_dir = args.log_dir or (args.out / "logs" if args.quick else REPO_ROOT / "logs" / "e6")
    cfg = load_config(args.config, args.quick)
    started = time.time()
    shown = " ".join(_shown(a) for a in (sys.argv[1:] if argv is None else argv))
    log = [f"generator: python experiments/e6_second_order.py {shown}".rstrip(),
           f"alpha {ALPHA}, delta {DELTA}, H {cfg['H']}, n_iid {cfg['n_iid']}, n_boot {cfg['n_boot']}; D5 seeds "
           f"SeedSequence([{STREAM}, role, i]), roles 0 fit, 1 calibration, 2 test"]
    inputs = [DERIVED / cfg["d6"]["dataset"] / "splits.yaml"]
    log += [f"sha256 {_shown(p)} {_sha256(p)}" for p in inputs + [args.config]]
    rows = run_d6(cfg, log)
    log.append(f"D6 rows done after {time.time() - started:.0f} s")
    rows += run_d5(cfg, args.jobs, log)
    args.out.mkdir(parents=True, exist_ok=True)
    csv = args.out / "e6_cells_phase1.csv"
    pl.save_fair_csv(pd.DataFrame(rows, columns=COLUMNS), csv)
    plot(csv, fig_dir)
    log += _summary(read_cells(csv))
    log.append(f"duration {time.time() - started:.0f} s")
    log.append(f"sha256 {_shown(csv)} {_sha256(csv)}")
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "phase1.log").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
