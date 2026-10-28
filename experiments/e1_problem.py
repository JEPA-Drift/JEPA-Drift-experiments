"""Stream 12, E1 (Article C, section 2): detection cost of the pipelines P1-C -> P2-C -> P3-C -> P3-CS on symmetrized
real backgrounds (D6) dated 2005-01-04..2019-12-31, scaling laws in N and the J2 criteria (prompts/plans/plan-12.md).

Arms (--arms)
  J2I  exact sign streams under D6: P1-C on composition_for(5, N), the five assets of E3, and every exact P3-C factor
       channel, H in {750, 2000}; J2(i) PASS iff every |FPR - lattice level| <= 0.01 (54 controls)
  A    equal information (convention a), SR in {2, 4, 8}: F3 and F1 on d2_us97 and d3_239, F2 on d3_239, H = 2000
  S    secondary cells at H = 750: P1-C, P2-C anytime-valid and bootstrap (R15 port), P3-D factor and full
  B    scaling laws (convention b) on nested subsets of 20 seeded chains: P2-C on F3, P3-C and P3-CS (b) on F2
  G    G_SR: smallest SR detected within H with probability >= 1/2, by bisection on log2 SR
  C    real phases, descriptive: budget shares and alarm shares against circular placebo rotations
Every monitor reads rows [tau*, tau* + H) only and starts from zero at the onset (P2-C bootstrap also reads the H_ref
drift-free rows before it). Each cell carries a paired H0 arm: same background and onset, no drift. add_h = mean(min(T,
H)) is a restricted delay, not Lorden's ADD; Phi(gamma I) / I is a diffusion approximation, not an exact ADD bound at
finite gamma. The calib rows follow every onset at H = 2000: every cell is retrospective.
Outputs: <out>/{e1_cells,e1_slopes,e1_real_phases,e1_null}.csv (save_fair_csv), <out>/e1_j2_summary.txt,
<fig-dir>/{e1_j2i_fpr,e1_arm_a_delays,e1_arm_b_slopes}.{png,pdf} drawn from the CSVs, <log-dir>/e1.log.

Usage: python experiments/e1_problem.py [--quick] [--arms J2I,A,S,B,G,C] [--jobs 24] --out results/e1
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"
os.environ["MPLBACKEND"] = "Agg"

import argparse
import concurrent.futures
import copy
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
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl
from jepadrift import pipelines as pl
from jepadrift.data_loader.chars import load_chars_tensor
from jepadrift.data_loader.sp500 import CONTINUOUS_CHARS
from jepadrift.injection import draw_tau_star, fit_background, inject, symmetrize
from jepadrift.monitors import eprocess, lattice
from jepadrift.monitors.cusum import bilateral_delay_vec
from jepadrift.monitors.streams import exact_sign_stream
from jepadrift.representations.extract import DATASETS
from jepadrift.representations.pca import mp_count, pca_directions
from jepadrift.stats.drift import debiased_sr2, projections, rotate_phases, spy_phases, subspaces, transitions

STREAM = 12
REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVED = REPO_ROOT / "data" / "derived"
AUDIT = REPO_ROOT / "results" / "audit"
CONFIG = REPO_ROOT / "configs" / "e1.yaml"
FROZEN_JSON = REPO_ROOT / "configs" / "FROZEN.json"
WINDOW = (np.datetime64("2005-01-04"), np.datetime64("2019-12-31"))
EXCLUDED = {"d3_239": ("2005-01-03",)}
MAX_GAP_DAYS = 7
ALPHA = 0.05
DELTA = pl.SIGN_DELTA
N_J2I, N_P1 = 5, 20
FROZEN = {"K": "mp", "mode": "factor", "shrinkage": "ledoit_wolf"}
AGGREGATES = ("market", "factor", "idio", "residual_full", "chars")
LADDER = ("P1-C", "P2-C", "P3-C", "P3-CS(b)")
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#8a5cd6", "#d64a7a")
CELL_COLUMNS = ["row_type", "arm", "dataset", "family", "amplitude", "H", "gamma", "N", "chain", "pipeline", "reading",
                "unit", "asset_selection", "oracle", "n", "add_h", "det_rate", "det_lo", "det_hi", "censored_share",
                "mean_detected", "median_delay", "fpr", "fpr_lo", "fpr_hi", "fpr_target", "fpr_kind", "excess_rate",
                "info_x", "info_sub", "a_max", "e_sign", "info_realized", "c_nan_imputed", "pred_delay", "pred_lo",
                "budget_days", "add_diffusion_approx", "g_add_h", "g_lo", "g_hi", "g_label", "g_floor", "g_pred",
                "pred_comparable", "fpr_a", "fpr_b", "fa_diff_lo", "fa_diff_hi", "comparison", "sr_star", "sr_lo",
                "sr_hi", "retrospective", "status"]


def rng(*key):
    """Local generator keyed on SeedSequence([12, *key]); no global state."""
    return np.random.default_rng(np.random.SeedSequence([STREAM, *(int(k) for k in key)]))


def crc(label):
    """Integer key of a cell label."""
    return zlib.crc32(label.encode())


def check_window(days):
    """Refuse any row dated outside [2005-01-04, 2019-12-31], the strict real bound of E1 and E3 (pre-J4 guard)."""
    d = np.asarray(days, dtype="datetime64[D]")
    if d.min() < WINDOW[0] or d.max() > WINDOW[1]:
        raise ValueError(f"rows dated outside {WINDOW[0]}..{WINDOW[1]} are refused (C-e1-window)")


@functools.lru_cache(maxsize=None)
def load_window(name):
    """(X, days, splits, assets, rows): the official pre_monitor rows (first pretrain day to last calib day) minus the
    declared EXCLUDED dates, each checked against the strict window, contiguous in the source, strictly increasing with
    calendar gaps of at most MAX_GAP_DAYS; monitor rows are never selected (C-e1-window)."""
    load, load_splits = DATASETS[name]
    ret, dates, assets = load()
    dates, sp = np.asarray(dates, dtype="datetime64[D]"), load_splits(name)
    source = np.arange(*pl.split_rows(dates, sp)["pre_monitor"])
    excluded = np.asarray(EXCLUDED.get(name, ()), dtype="datetime64[D]")
    if np.setdiff1d(excluded, dates[source]).size:
        raise ValueError(f"{name}: a declared exclusion {excluded} is not a pre-monitor date (C-e1-window)")
    rows = source[~np.isin(dates[source], excluded)]
    if rows.size == 0:
        raise ValueError(f"{name}: no pre-monitor row")
    days = dates[rows]
    check_window(days)
    step = np.diff(days).astype(np.int64)
    if not np.array_equal(rows, np.arange(rows[0], rows[-1] + 1)) or (step <= 0).any() or step.max(initial=1) > \
            MAX_GAP_DAYS:
        raise ValueError(f"{name}: pre-monitor rows must be contiguous, strictly increasing, with calendar gaps of at "
                         f"most {MAX_GAP_DAYS} days (C-e1-window)")
    X = np.ascontiguousarray(ret[rows])
    if not np.isfinite(X).all():
        raise ValueError(f"{name}: the window rows must be finite")
    return X, days, pl.split_rows(days, load_splits(name)), list(assets), rows


@functools.lru_cache(maxsize=None)
def chars4(name):
    """The four continuous characteristics (Q10, C-e1-f2-chars) on the window rows, NaN kept (inject reads them as 0)."""
    C, names = load_chars_tensor(name, load_window(name)[4])
    return np.ascontiguousarray(C[:, :, [names.index(c) for c in CONTINUOUS_CHARS]])


def j2i_assets(name):
    """The five P1-C assets of J2(i), those of E3: pipelines.composition_for(5, N)."""
    return [int(c) for c in pl.composition_for(N_J2I, load_window(name)[0].shape[1])]


def p1_assets(name):
    """The 20 P1-C assets of arms A, S, G and C: the frozen R15 composition composition_for(20, N)."""
    return [int(c) for c in pl.composition_for(N_P1, load_window(name)[0].shape[1])]


def lattice_selection(H):
    """Exact reading at H: strict bilateral CUSUM, delta = 0.1, nearest attainable level at or below alpha."""
    return lattice.select_threshold(ALPHA, H=H, delta=DELTA, sided=2)


def coin_bits(y, gen):
    """B = 1{y > 0} as float64, every tie y == 0 replaced by a fair coin of gen."""
    return exact_sign_stream(y, gen) + 0.5


def recentred(B, c):
    """x = (B - c) / max(c, 1 - c) in [-1, 1]; 2B - 1 when c = 1/2."""
    return (B - c) / np.maximum(c, 1.0 - c)


def edetector_offsets(x, gamma):
    """First alarm offsets of the CUSUM e-detector along the last axis of x at gamma (-1 when none)."""
    return eprocess.first_alarm(eprocess.log_edetector(x, "cusum"), gamma)


def p1c_window(X, tau, H, cols, gen, sel, gamma, c=0.5):
    """P1-C on rows [tau, tau + H) of columns cols only (coins of gen drawn on these rows): exact reading (strict
    bilateral CUSUM from S_0 = 0) and anytime-valid reading (M_0 = 0); returns (offsets by reading, bits)."""
    if tau < 0 or tau + H > len(X):
        raise ValueError(f"rows [{tau}, {tau + H}) leave the {len(X)} rows")
    B = coin_bits(np.ascontiguousarray(X[tau:tau + H][:, cols]), gen)
    return {"exact": bilateral_delay_vec((B - c).T, DELTA, sel["threshold"]),
            "anytime-valid": edetector_offsets(recentred(B, c).T, gamma)}, B


def run_registry(spec, state, blocks, seeds, pre=0, deltas=None):
    """Alarm offsets of a registry reading by pipelines.run_pipeline on stacked blocks of pre + H rows, the onset at row
    pre of each block: every monitor starts from zero at the onset (pipelines._window)."""
    L = len(blocks[0])
    recs = [{"seed": s, "tau_star": j * L + pre, "family": "E1"} for j, s in enumerate(seeds)]
    for rec, d in zip(recs, deltas or []):
        rec["delta"] = d
    rows = pl.run_pipeline(spec, np.concatenate(blocks), None, recs, state)
    alarm = rows["alarm_index"].to_numpy()
    return np.where(alarm >= 0, alarm - rows["tau_star"].to_numpy(), -1)


def p3c_exact(state, blocks, seeds, sel):
    """Exact reading of every P3-C channel on the bits of run_pipeline (coins of SeedSequence([*seed, 7])): (reps, D)."""
    x = [coin_bits(state["rep"].transform_panel(W)["z_odd"], np.random.default_rng(np.random.SeedSequence([*s, 7]))).T
         - 0.5 for W, s in zip(blocks, seeds)]
    return bilateral_delay_vec(np.stack(x), DELTA, sel["threshold"])


def kde0(u):
    """Gaussian-kernel density at 0 of each column of u, Silverman bandwidth."""
    u = np.asarray(u, dtype=np.float64)
    h = 1.06 * u.std(axis=0) * len(u) ** -0.2
    return np.exp(-0.5 * (u / h) ** 2).sum(axis=0) / (len(u) * h * math.sqrt(2.0 * math.pi))


def sign_efficiency(u):
    """e = 4 f(0)^2 of each standardized column of u, the sign-test efficiency (2/pi under normality)."""
    u = np.asarray(u, dtype=np.float64)
    return 4.0 * kde0(u / u.std(axis=0)) ** 2


def wilson(k, n):
    """Wilson 95 % interval of k successes out of n."""
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return max(0.0, min(float(lo), k / n)), min(1.0, max(float(hi), k / n))


def restricted(off, H):
    """Delays restricted to H: offset + 1 when detected, H when censored."""
    off = np.asarray(off)
    return np.where(off >= 0, off + 1.0, float(H))


def delay_summary(off, H):
    """add_h = mean(min(T, H)), detection rate and Wilson interval, censored share, mean detected delay, median delay
    (NaN unless the detection rate exceeds 1/2)."""
    off = np.asarray(off)
    det = off >= 0
    n, k = det.size, int(det.sum())
    lo, hi = wilson(k, n)
    return {"n": n, "add_h": float(restricted(off, H).mean()), "det_rate": k / n, "det_lo": lo, "det_hi": hi,
            "censored_share": 1.0 - k / n, "mean_detected": float(off[det].mean() + 1.0) if k else math.nan,
            "median_delay": float(np.median(np.where(det, off + 1.0, np.inf))) if k / n > 0.5 else math.nan}


def gain_label(det_a, det_b):
    """Censoring label of add_h(A) / add_h(B): uncensored, lower_bound (A censored only), undetermined (B censored)."""
    return "undetermined" if det_b < 1.0 else "lower_bound" if det_a < 1.0 else "uncensored"


def paired_ci(stat, n, B, gen):
    """Percentile 95 % interval of stat(idx) over B paired resamples idx (B, n) of the n shared replicates."""
    lo, hi = np.percentile(stat(gen.integers(0, n, size=(B, n))), [2.5, 97.5])
    return float(lo), float(hi)


def j2i_risk(n, levels, tol):
    """Pass bounds and exact false-FAIL probability of |k / n - level| <= tol per control under exactness, expected
    false FAILs and P(at least one) for independent controls."""
    bounds, p_fail = [], []
    for lv in levels:
        lo, hi = math.ceil(n * (lv - tol) - 1e-9), math.floor(n * (lv + tol) + 1e-9)
        bounds.append((lo, hi))
        p_fail.append(float(stats.binom.cdf(lo - 1, n, lv) + stats.binom.sf(hi, n, lv)))
    return {"bounds": bounds, "p_fail": p_fail, "expected": float(sum(p_fail)),
            "p_any": float(1.0 - np.prod(1.0 - np.asarray(p_fail)))}


def poisson_binomial_tail(ps, k):
    """P(at least k successes) of independent Bernoulli(ps)."""
    pmf = np.array([1.0])
    for p in ps:
        pmf = np.convolve(pmf, [1.0 - p, p])
    return float(pmf[k:].sum())


def slope_fit(x, y, groups, B, gen):
    """OLS slope of y on x over the pooled cells and its 95 % percentile interval by resampling the groups (chains)."""
    x, y, groups = (np.asarray(a) for a in (x, y, groups))
    ids = np.unique(groups)
    members = [np.flatnonzero(groups == g) for g in ids]

    def slope(idx):
        xc = x[idx] - x[idx].mean()
        ss = float((xc * xc).sum())
        return float((xc * (y[idx] - y[idx].mean())).sum() / ss) if ss > 0 else math.nan

    draws = [slope(np.concatenate([members[i] for i in gen.integers(0, ids.size, ids.size)])) for _ in range(B)]
    lo, hi = np.nanpercentile(draws, [2.5, 97.5])
    return slope(np.arange(x.size)), float(lo), float(hi)


def b_chain(name, s):
    """Chain s of arm B, a permutation of the assets drawn before any injection; its first asset is the P1 reference."""
    return rng(crc(f"B|{name}"), s).permutation(load_window(name)[0].shape[1])


def phase_offsets(x, phases, alpha, dictionary):
    """First alarm offset in each phase (rows (L,) or rotations (P, L)) of the bounded stream x (T, m), restarted at
    every boundary: CUSUM e-detector per column, or their dictionary average, at gamma_L = L / alpha."""
    out = []
    for rows in phases:
        xp, g = x[rows], np.shape(rows)[-1] / alpha
        out.append(eprocess.first_alarm(eprocess.log_dictionary_edetector(xp, "cusum"), g) if dictionary
                   else edetector_offsets(np.moveaxis(xp, -1, -2), g))
    return out


@functools.lru_cache(maxsize=None)
def real_context(name):
    """Arm C inputs on the window: frozen calib eigenbasis (full mode), D3 characteristics as in the audit (15 columns,
    NaN read as 0, retrospective), frozen-direction projections and subspaces."""
    X, days, splits, _, rows = load_window(name)
    a, b = splits["calib"]
    _, eigvec, _, pca = pca_directions(X[a:b], "mp", "full", "ledoit_wolf")
    d = {"X": X, "eigvec": eigvec, "K": pca["n_above_edge"] - 1, "C": None, "chars": []}
    if name != "d2_us97":
        C, names = load_chars_tensor(name, rows)
        d["C"], d["chars"] = np.where(np.isnan(C), 0.0, C), names
    return subspaces(d, projections(d)), days


def budget_shares(name, dating, offset=None, gammas=(20, 252)):
    """Share of the dated transitions with n2 SR^2_debiased / 504 >= ln(gamma) per subspace (audit item 6 on the strict
    window, budget reading); `offset` rotates the phases (placebo)."""
    Ys, days = real_context(name)
    real = spy_phases(dating, days)
    pairs = transitions(real)
    ph = real if offset is None else rotate_phases(real, len(days), offset)
    sr2 = {(i, j, s): debiased_sr2(Y[ph[i][3]], Y[ph[j][3]])[1] for s, Y in Ys.items() for i, j in pairs}
    blocks = [s for s in Ys if s.startswith("idio:")]
    for i, j in pairs:
        sr2[i, j, "idio"] = sum(sr2[i, j, s] for s in blocks)
        sr2[i, j, "residual_full"] = sum(sr2[i, j, s] for s in ("factor", "idio"))
    rows = []
    for s in [s for s in AGGREGATES if s in Ys or s in ("idio", "residual_full")]:
        ev = np.array([ph[j][3].size for i, j in pairs]) * np.array([sr2[i, j, s] for i, j in pairs]) / (
            2 * fl.TRADING_DAYS)
        for g in gammas:
            k = int((ev >= math.log(g)).sum())
            rows.append({"dataset": name, "dating": dating, "subspace": s, "gamma": g, "n_phases": len(pairs),
                         "n_in_budget": k, "share": k / len(pairs)})
    return rows


@functools.lru_cache(maxsize=None)
def frozen_states(name, H, n_cal=None):
    """Reading states of one dataset at H, fitted once on the raw calib rows of the window (P3-C factor checked against
    the committed sidecar); with n_cal also P3-D and the P2-C bootstrap, calibrated on one symmetrization (retrospective)."""
    X, _, splits, _, _ = load_window(name)
    g, out = pl.horizon_gamma(H, ALPHA), {}

    def put(key, spec, X_fit=X):
        out[key] = (spec, pl.fit_pipeline(spec, X_fit, splits))

    put("P2-C", pl.make_spec("P2-C", reading="anytime-valid", gamma=g, H=H, dataset=name))
    put("P7", pl.make_spec("P7", gamma=g, H=H, dataset=name))
    for mode in ("factor", "full"):
        put(f"P3-C/{mode}", pl.make_spec("P3-C", mode=mode, gamma=g, H=H, dataset=name))
        put(f"P3-CS(b)/{mode}", pl.make_spec("P3-CS", mode=mode, gamma=g, H=H, dataset=name))
        put(f"P3-CS(a)/{mode}", pl.make_spec("P3-CS", mode=mode, variant="a", gamma=pl.GAMMA, H=H, dataset=name))
        if n_cal:
            put(f"P3-D/{mode}", pl.make_spec("P3-D", mode=mode, H=H, N_cal=n_cal, dataset=name))
    if n_cal:
        put("P2-C(boot)", pl.make_spec("P2-C", H=H, N_cal=n_cal, dataset=name),
            symmetrize(X, rng(crc(f"boot|{name}"), 0))[0])
    h = out["P3-C/factor"][1]["rep"].state_hash()
    sidecars = [json.loads(p.read_text()) for p in sorted((DERIVED / name).glob("z_*.json"))]
    if [s["state_sha256"] for s in sidecars if s["config"] == FROZEN] != [h]:
        raise ValueError(f"{name}: calib basis {h[:16]} differs from the committed sidecar")
    return out


def mixture_gate(name, state, X=None, splits=None):
    """Holm gate of the sub-Gaussian mixture on the residual sign streams of the calib rows (C-e1-holm-gate)."""
    X, splits = (X, splits) if X is not None else load_window(name)[::2][:2]
    a, b = splits["calib"]
    z = state["rep"].transform_panel(np.ascontiguousarray(X[a:b]))["z_odd"]
    return pl.cross_independence(np.sign(z[:, state["channels"]["residual"]]))


def basis_context(name, state, X, splits, cols):
    """Information inputs of plan section 8: calib Ledoit-Wolf sigma, P3 basis W and channel sign efficiencies,
    per-asset densities at 0 and sign efficiencies, K_eff."""
    a, b = splits["calib"]
    sigma = fit_background(np.ascontiguousarray(X[a:b]), 1)["sigma"]
    W = state["rep"].state["W"]
    return {"sigma": sigma, "W": W, "e_ch": sign_efficiency(X[a:b] @ W), "f0": kde0(X[a:b]),
            "e_asset": sign_efficiency(X[a:b]), "ones": float(sigma.sum()), "p1cols": cols}


def drift_info(bc, d, H, k_eff):
    """Design Gaussian information of the drift on the monitored rows: oracle I_x, channel energies of the P3 basis,
    P1-C assets, P2-C equal-weight and sign versions."""
    D = d[None, :] if d.ndim == 1 else d[:H]
    I_x = 0.5 * float(np.mean(np.sum(D * np.linalg.solve(bc["sigma"], D.T).T, axis=1)))
    p1 = np.mean(D[:, bc["p1cols"]] ** 2, axis=0) / (2.0 * np.diag(bc["sigma"])[bc["p1cols"]])
    return {"I_x": I_x, "energy": np.mean((D @ bc["W"]) ** 2, axis=0), "I_p1": p1,
            "I_ew": float(np.mean(D.sum(axis=1) ** 2)) / (2.0 * bc["ones"]),
            "I_sign": 2.0 * k_eff * float(np.mean((D @ bc["f0"] / D.shape[1]) ** 2))}


def mixture_prior(X, family, I_target, params, W, res, e_res, crc_key, draws, H):
    """s^2 = 2 e I_res / D of Proposition 3 matched to the injected amplitude (oracle): mean residual information of the
    first `draws` drift directions of the cell, at onset 0 over H rows."""
    vals = []
    for r in range(draws):
        d = inject(X, family, 0, I_target, params, rng(crc_key, r, 2))[1]
        D = d[None, :] if d.ndim == 1 else d[:H]
        vals.append(0.5 * float(np.mean(np.sum((D @ W[:, res]) ** 2, axis=1))))
    return 2.0 * float(np.mean(e_res)) * float(np.mean(vals)) / len(res)


def cell_task(ctx, span):
    """Replicates span of one cell: a fresh D6 symmetrization, a uniform onset, each amplitude injected from the onset
    (None = the paired H0 arm); every monitor reads the rows of its window only."""
    X = load_window(ctx["dataset"])[0]
    if ctx.get("cols") is not None:
        X = np.ascontiguousarray(X[:, ctx["cols"]])
    H, pre, fam = ctx["H"], ctx["pre"], ctx["family"]
    out = {"off": {a: {} for a in ctx["amps"]}, "info": {a: [] for a in ctx["amps"]}}
    for c0 in range(span[0], span[1], ctx["chunk"]):
        seeds, blocks, deltas, p1 = [], {a: [] for a in ctx["amps"]}, {a: [] for a in ctx["amps"]}, \
            {a: [] for a in ctx["amps"]}
        for r in range(c0, min(span[1], c0 + ctx["chunk"])):
            key = (ctx["crc"], *ctx.get("subkey", ()), r)
            Xm = symmetrize(X, rng(*key, 0))[0]
            tau = draw_tau_star(0, len(X), pre, H, rng(*key, 1))
            seeds.append([STREAM, *key])
            for amp in ctx["amps"]:
                Xt, d = Xm, None
                if amp is not None:
                    I_target, params = ctx["inject"][amp]
                    Xt, d, meta = inject(Xm, fam, tau, I_target, params, rng(*key, 2))
                    if ctx.get("bc") is not None:
                        out["info"][amp].append({**drift_info(ctx["bc"], d, H, ctx["k_eff"]),
                                                 "c_nan": float(meta.get("c_nan_imputed", 0))})
                    d = d if d.ndim == 1 else d[:H]
                blocks[amp].append(np.ascontiguousarray(Xt[tau - pre:tau + H]))
                deltas[amp].append(d)
                if ctx["p1"] is not None:
                    p1[amp].append(p1c_window(Xt, tau, H, ctx["p1"], rng(*key, 3), ctx["sel"], ctx["gamma"])[0])
        for amp in ctx["amps"]:
            res, W0 = out["off"][amp], [b[pre:] for b in blocks[amp]]
            if ctx["p1"] is not None:
                for rd in ("exact", "anytime-valid"):
                    res.setdefault(f"P1-C|{rd}", []).append(np.stack([o[rd] for o in p1[amp]]))
            for rd in ctx["readings"]:
                if (rd.get("drift_only") and amp is None) or rd.get("amp", amp) != amp and amp is not None:
                    continue
                spec, state = ctx["states"][rd["state"]]
                spec = {**spec, "mixture_s2": rd["s2"]} if "s2" in rd else spec
                res.setdefault(rd["label"], []).append(run_registry(
                    spec, state, blocks[amp] if rd.get("pre") else W0, seeds, pre if rd.get("pre") else 0,
                    deltas[amp] if rd.get("drift_only") else None))
            for mode in ctx.get("exact_modes", ()):
                res.setdefault(f"P3-C|exact|{mode}", []).append(
                    p3c_exact(ctx["states"][f"P3-C/{mode}"][1], W0, seeds, ctx["sel"]))
    out["off"] = {a: {k: np.concatenate(v) for k, v in d.items()} for a, d in out["off"].items()}
    return out


def j2i_task(ctx, arg):
    """J2(i) controls of one (dataset, H): every exact P3-C channel of the frozen factor basis (the loop of
    pipelines.null_check without its refit) and the five P1-C assets, each replicate on its own fresh D6 window
    (pipelines._null_block keyed [*key, 2 or 3, control, replicate], coins of pipelines._coins)."""
    name, H = arg
    X, _, splits, assets, _ = load_window(name)
    key = [STREAM, crc(f"{ctx['label']}|j2i|{name}|{H}")]
    sel, n = lattice_selection(H), ctx["reps"]
    lo, hi = splits["pre_monitor"]
    frozen = frozen_states(name, H)["P3-C/factor"][1]
    state = {**frozen, "threshold": sel["threshold"], "level": sel["level"], "lattice_units": sel["units"]}
    base, rows = frozen["rep"].transform_panel(X), []
    for k in range(len(frozen["channels"]["residual"]) + 1):
        spec, det = pl.make_spec("P3-C", reading="exact", channels=[k], alpha=ALPHA, H=H, dataset=name), []
        for c0 in range(0, n, pl.CHUNK):
            seeds = [key + [2, k, r] for r in range(c0, min(n, c0 + pl.CHUNK))]
            blocks = [pl._null_block(spec, state, base, s, lo, hi, 0)[1] for s in seeds]
            data = {"z_odd": np.concatenate([b[0] for b in blocks]), "z_even": np.concatenate([b[1] for b in blocks])}
            recs = [{"seed": s, "tau_star": j * H, "family": "H0"} for j, s in enumerate(seeds)]
            det.append(pl.run_pipeline(spec, data, splits, recs, state)["detected"].to_numpy())
        rows.append({"dataset": name, "H": H, "pipeline": "P3-C", "unit": f"ch{k}", "k": int(np.concatenate(det).sum()),
                     "n": n, "level": float(sel["level"])})
    for j, col in enumerate(j2i_assets(name)):
        bits = []
        for r in range(n):
            seed = key + [3, j, r]
            block = pl._null_block({"H": H}, {"rep": None}, X[:, [col]], seed, lo, hi, 0)[1]
            bits.append(coin_bits(block[:, 0], pl._coins({"seed": seed})))
        off = bilateral_delay_vec(np.stack(bits) - 0.5, DELTA, sel["threshold"])
        rows.append({"dataset": name, "H": H, "pipeline": "P1-C", "unit": assets[col], "k": int((off >= 0).sum()),
                     "n": n, "level": float(sel["level"])})
    return [{**r, "key": json.dumps(key)} for r in rows]


def subset_ctx(cfg, name, family, s, N, amps, reps, pilot):
    """Context of one (chain, N) cell of arm B: subset states fitted on its raw calib rows, injection geometry of the
    subset, keys shared by every N and amplitude of the chain."""
    X, _, splits, _, _ = load_window(name)
    perm = b_chain(name, s)
    cols = np.sort(perm[:N])
    Xs = np.ascontiguousarray(X[:, cols])
    a, b = splits["calib"]
    H, g = cfg["B"]["H"], pl.horizon_gamma(cfg["B"]["H"], ALPHA)
    K = int(min(max(mp_count(Xs[a:b])[0], 1), N - 1))
    params = {"calib": (a, b), "K": K, "fit": fit_background(Xs[a:b], K)}
    if family == "F2":
        params["C"] = np.ascontiguousarray(chars4(name)[:, cols, :])
    inj = {amp: (None, {**params, ("kappa" if family == "F2" else "sr_asset"): float(amp)}) for amp in amps}
    states, readings = {}, []
    if family == "F3":
        states["P2-C"] = (pl.make_spec("P2-C", reading="anytime-valid", gamma=g, H=H, dataset=name), None)
        readings.append({"label": "P2-C|anytime-valid", "state": "P2-C"})
    else:
        states["P3-C/full"] = (pl.make_spec("P3-C", mode="full", gamma=g, H=H, dataset=name), None)
        readings.append({"label": "P3-C|anytime-valid", "state": "P3-C/full"})
        if not pilot:
            states["P3-CS(b)/full"] = (pl.make_spec("P3-CS", mode="full", gamma=g, H=H, dataset=name), None)
            readings.append({"label": "P3-CS(b)|anytime-valid", "state": "P3-CS(b)/full"})
    splits_s = {**splits}
    states = {k: (spec, pl.fit_pipeline(spec, Xs, splits_s)) for k, (spec, _) in states.items()}
    ctx = {"dataset": name, "family": family, "H": H, "pre": 0, "amps": list(amps), "inject": inj, "states": states,
           "readings": readings, "cols": cols, "chunk": cfg["chunk"], "sel": lattice_selection(H), "gamma": g,
           "crc": crc(f"{'Bpilot' if pilot else 'B'}|{name}|{family}"), "subkey": (s,),
           "p1": None if pilot else [int(np.flatnonzero(cols == perm[0])[0])], "reps": reps}
    if family == "F2" and not pilot:
        st = states["P3-C/full"][1]
        ctx["gate"] = gate = mixture_gate(name, st, Xs, splits)
        ctx["bc"], ctx["k_eff"] = basis_context(name, st, Xs, splits, ctx["p1"]), 1.0
        if gate["passed"]:
            res = st["channels"]["residual"]
            for amp in amps:
                s2 = mixture_prior(Xs, family, None, inj[amp][1], st["rep"].state["W"], res, ctx["bc"]["e_ch"][res],
                                   ctx["crc"], cfg["B"]["mix_draws"], H)
                readings.append({"label": "P3-C(mix)|mixture", "state": "P3-C/full", "s2": s2, "amp": amp})
    return ctx


def b_task(cfg, arg):
    """One (chain, N) cell of arm B: offsets and mean information per amplitude, the subset context built in the worker."""
    name, family, s, N, amps, reps, pilot = arg
    ctx = subset_ctx(cfg, name, family, s, N, amps, reps, pilot)
    out = cell_task(ctx, (0, reps))
    out["gate"] = ctx.get("gate")
    out["a_max"] = {a: float(np.mean([i["energy"].max() / i["energy"].sum() for i in out["info"][a]]))
                    for a in amps} if out["info"].get(amps[0]) else {}
    out["info"] = {}
    return out


def run_task(task):
    """Dispatch one task (kind, context, argument) to its worker."""
    kind, ctx, arg = task
    return {"cell": cell_task, "j2i": j2i_task, "b": b_task}[kind](ctx, arg)


def run_tasks(tasks, jobs):
    """Run tasks in submission order, on a spawn-context process pool when jobs > 1."""
    if jobs > 1 and len(tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
            return list(pool.map(run_task, tasks))
    return [run_task(t) for t in tasks]


def merge(parts):
    """Concatenate the cell_task outputs of consecutive spans."""
    off = {a: {k: np.concatenate([p["off"][a][k] for p in parts]) for k in parts[0]["off"][a]} for a in parts[0]["off"]}
    return {"off": off, "info": {a: [i for p in parts for i in p["info"][a]] for a in parts[0]["info"]}}


def run_j2i(cfg, jobs, log):
    """The 54 J2(i) controls, their primary verdict, the a priori false-FAIL risk and the pre-registered diagnostics."""
    j = cfg["j2i"]
    ctx = {"label": j["label"], "reps": j["reps"]}
    parts = run_tasks([("j2i", ctx, (name, H)) for name in cfg["datasets"] for H in j["H"]], jobs)
    df = pd.DataFrame([r for p in parts for r in p])
    df["fpr"] = df.k / df.n
    df["abs_diff"] = (df.fpr - df.level).abs()
    df["pass"] = df.abs_diff <= j["tolerance"] + 1e-12
    risk = j2i_risk(int(df.n.iloc[0]), df.level.tolist(), j["tolerance"])
    df["p_fail_exact"] = risk["p_fail"]
    df["binom_p"] = [stats.binomtest(int(k), int(n), lv).pvalue for k, n, lv in zip(df.k, df.n, df.level)]
    df["holm_reject_1pct"] = multipletests(df.binom_p, alpha=0.01, method="holm")[0]
    half = pl.Z99 * np.sqrt(df.level * (1.0 - df.level) / df.n)
    df["lo99"], df["hi99"] = df.level - half, df.level + half
    df["in_99_region"] = (df.fpr >= df.lo99) & (df.fpr <= df.hi99)
    df["tolerance"] = j["tolerance"]
    n_fail = int((~df["pass"]).sum())
    verdict = {"pass": n_fail == 0, "n_fail": n_fail, "n": len(df), "p_any": risk["p_any"], "expected": risk["expected"],
               "p_tail": poisson_binomial_tail(risk["p_fail"], n_fail), "holm": int(df.holm_reject_1pct.sum()),
               "outside99": int((~df.in_99_region).sum()), "reps": int(df.n.iloc[0]), "label": j["label"]}
    log(f"J2(i): {verdict}")
    return df, verdict


def cell_contexts(cfg, arm, name, states, log):
    """Contexts of the arm A or S cells of one dataset: readings, injection parameters, information inputs and the
    mixture readings allowed by the Holm gate."""
    c = cfg[arm]
    H = c["H"]
    X, _, splits, _, _ = load_window(name)
    a, b = splits["calib"]
    g, sel = pl.horizon_gamma(H, ALPHA), lattice_selection(H)
    K = len(states["P3-C/factor"][1]["channels"]["residual"]) + 1
    fit = fit_background(X[a:b], K)
    k_eff = states["P2-C"][1]["diagnostics"]["K_eff_meas"]
    out = []
    for fam in c["families"].get(name, []):
        mode = "full" if fam == "F2" else "factor"
        params = {"calib": (a, b), "K": K, "fit": fit, **({"C": chars4(name)} if fam == "F2" else {})}
        ckey = crc(f"{arm}|{name}|{fam}|{H}")
        ctx = {"dataset": name, "family": fam, "H": H, "pre": pl.H_REF if arm == "S" else 0, "crc": ckey,
               "amps": [None, *c["sr"]], "inject": {sr: (fl.kl_from_sharpe(sr), params) for sr in c["sr"]},
               "states": states, "chunk": cfg["chunk"], "sel": sel, "gamma": g, "p1": p1_assets(name), "k_eff": k_eff,
               "mode": mode, "bc": basis_context(name, states[f"P3-C/{mode}"][1], X, splits, p1_assets(name))}
        if arm == "A":
            ctx["readings"] = [{"label": "P2-C|anytime-valid", "state": "P2-C"},
                               {"label": "P3-C|anytime-valid", "state": f"P3-C/{mode}"},
                               {"label": "P3-CS(b)|anytime-valid", "state": f"P3-CS(b)/{mode}"},
                               {"label": "P3-CS(a)|e-process", "state": f"P3-CS(a)/{mode}"},
                               {"label": "P7|anytime-valid", "state": "P7", "drift_only": True}]
            ctx["exact_modes"] = [mode]
            st = states[f"P3-C/{mode}"][1]
            gate = mixture_gate(name, st)
            ctx["gate"] = gate
            log(f"{name} {fam} mixture gate ({mode}): passed={gate['passed']} over={gate['over']}/{gate['pairs']} "
                f"p_min={gate['p_min']:.3g}")
            res = st["channels"]["residual"]
            if gate["passed"] and fam != "F3":
                for sr in c["sr"]:
                    s2 = mixture_prior(X, fam, fl.kl_from_sharpe(sr), params, st["rep"].state["W"], res,
                                       ctx["bc"]["e_ch"][res], ckey, c["mix_draws"], H)
                    ctx["readings"].append({"label": f"P3-C|mixture@{sr:g}", "state": f"P3-C/{mode}", "s2": s2,
                                            "amp": sr})
        else:
            ctx["readings"] = [{"label": "P2-C|anytime-valid", "state": "P2-C"},
                               {"label": "P2-C|bootstrap", "state": "P2-C(boot)", "pre": True}]
            if fam != "F3":
                ctx["readings"] += [{"label": f"P3-D|bootstrap|{m}", "state": f"P3-D/{m}"} for m in ("factor", "full")]
        out.append(ctx)
    return out


def units(label, off, H, assets):
    """(unit, offsets, selection, oracle) rows of one reading: P1-C median (rank 10 of 20 by add_h) and best asset,
    P3-C exact market channel and best channel; every unit under H0."""
    if off.ndim == 1:
        return [("", off, "", False)]
    add = restricted(off, H).mean(axis=0)
    order = np.argsort(add, kind="stable")
    name = (lambda k: assets[k]) if label.startswith("P1-C") else (lambda k: f"ch{k}")
    return [(name(order[(len(order) - 1) // 2]), off[:, order[(len(order) - 1) // 2]], "median", False),
            (name(order[0]), off[:, order[0]], "best", True)] + \
        ([(name(0), off[:, 0], "market", False)] if label.startswith("P3-C|exact") else [])


def predictions(label, info, ctx, unit_idx, N1):
    """(info_sub, a_max, e_sign, pred_delay, pred_lo) of one reading from the injected drift (plan section 8)."""
    g, bc = ctx["gamma"], ctx["bc"]
    e = info["energy"]
    if label.startswith("P1-C"):
        I = float(info["I_p1"][unit_idx])
        e_s = float(bc["e_asset"][bc["p1cols"][unit_idx]])
        return I, math.nan, e_s, fl.first_order_floor(g, e_s * I) if "anytime" in label and I > 0 else math.nan, math.nan
    if label.startswith("P2-C"):
        return info["I_ew"], math.nan, math.nan, fl.first_order_floor(g, info["I_sign"]) if info["I_sign"] > 0 else \
            math.nan, math.nan
    if label.startswith("P3-CS(b)"):
        er = e[1:]
        if not er.sum() > 0:
            return 0.0, math.nan, math.nan, math.nan, math.nan
        k = int(np.argmax(er))
        d = fl.dictionary_multiplier(er.size, g, er[k] / er.sum()) * fl.first_order_floor(
            g, bc["e_ch"][1 + k] * 0.5 * er.sum())
        return 0.5 * float(er.sum()), float(er[k] / er.sum()), float(bc["e_ch"][1 + k]), d, d / N1
    if label.startswith(("P3-CS(a)", "P3-D")):
        return math.nan, math.nan, math.nan, math.nan, math.nan
    if label.startswith("P3-C|exact"):
        return 0.5 * float(e[unit_idx]), float(e[unit_idx] / e.sum()), float(bc["e_ch"][unit_idx]), math.nan, math.nan
    if label.startswith("P3-C"):
        k = int(np.argmax(e))
        d = fl.dictionary_multiplier(e.size, g, e[k] / e.sum()) * fl.first_order_floor(g, bc["e_ch"][k] * 0.5 * e.sum())
        if "mixture" in label:
            er = e[1:].sum()
            d = fl.mixture_multiplier(e.size - 1, g) * fl.first_order_floor(g, float(np.mean(bc["e_ch"][1:])) * 0.5 * er) \
                if er > 0 else math.nan
        return 0.5 * float(e.sum()), float(e[k] / e.sum()), float(bc["e_ch"][k]), d, math.nan
    if label.startswith("P7"):
        return info["I_x"], math.nan, math.nan, fl.evidence_budget(g, info["I_x"]), math.nan
    return math.nan, math.nan, math.nan, math.nan, math.nan


def mean_info(infos):
    """Replicate means of the drift information (energies averaged per channel)."""
    if not infos:
        return None
    return {k: np.mean([i[k] for i in infos], axis=0) for k in infos[0]}


def cell_rows(arm, ctx, res, cfg, N1):
    """e1_cells rows of one arm A or S cell: delays, attained FPR of the paired H0 arm, information, predictions, and
    for arm A the gains 1 -> 2 -> 3 -> 3-CS with their censoring and false-alarm labels."""
    name, fam, H, g = ctx["dataset"], ctx["family"], ctx["H"], ctx["gamma"]
    assets = load_window(name)[3]
    base = {"row_type": "cell", "arm": arm, "dataset": name, "family": fam, "H": H, "gamma": g, "retrospective": True}
    h0, rows, gains = res["off"][None], [], []
    for amp, offs in res["off"].items():
        info = mean_info(res["info"][amp]) if amp is not None else None
        for label, off in offs.items():
            pipe, reading = label.split("|")[:2]
            us = units(label, off, H, [assets[c] for c in ctx["p1"]]) if amp is not None else (
                [("", off, "", False)] if off.ndim == 1 else
                [(assets[ctx["p1"][k]] if pipe == "P1-C" else f"ch{k}", off[:, k], "every", False)
                 for k in range(off.shape[1])])
            for unit, o, selection, oracle in us:
                k = unit_index(label, unit, ctx, assets)
                f = delay_summary(h0[label] if h0[label].ndim == 1 else h0[label][:, k], H) if label in h0 else \
                    {"det_rate": math.nan, "det_lo": math.nan, "det_hi": math.nan}
                tgt = target(label, ctx)
                row = {**base, "amplitude": math.nan if amp is None else amp, "pipeline": pipe, "reading": reading,
                       "unit": unit or label.split("|")[2] if label.count("|") > 1 else unit,
                       "asset_selection": selection, "oracle": oracle, **delay_summary(o, H), "fpr": f["det_rate"],
                       "fpr_lo": f["det_lo"], "fpr_hi": f["det_hi"], "fpr_target": tgt[0], "fpr_kind": tgt[1], "status": "H0" if amp is None else "drift"}
                if pipe == "P3-D" and amp is not None:
                    row["excess_rate"] = row["det_rate"] - f["det_rate"]
                if info is not None:
                    i_sub, a_max, e_s, pred, pred_lo = predictions(label, info, ctx, k, N1)
                    row.update(info_x=float(info["I_x"]), info_sub=i_sub, a_max=a_max, e_sign=e_s, pred_delay=pred,
                               pred_lo=pred_lo, info_realized=float(info["I_x"]), c_nan_imputed=float(info["c_nan"]),
                               budget_days=fl.evidence_budget(g, info["I_x"]),
                               add_diffusion_approx=fl.phi(g * info["I_x"]) / info["I_x"])
                    if fam == "F3" and pipe == "P3-CS(b)":
                        row["status"] = "no_information"
                rows.append(row)
    if arm == "A":
        gains = gain_rows(base, ctx, res, rows, cfg)
    return rows, gains


def unit_index(label, unit, ctx, assets):
    """Column of a unit in the offsets of its reading (asset position in ctx['p1'] or channel number)."""
    if label.startswith("P1-C"):
        return [assets[c] for c in ctx["p1"]].index(unit)
    if label.startswith("P3-C|exact"):
        return int(unit[2:])
    return 0


def target(label, ctx):
    """(target, kind) of the H0 false-alarm rate of a reading by H (pipelines.null_target conventions)."""
    if label.split("|")[1] == "exact":
        return ctx["sel"]["level"], "="
    if label.startswith("P3-CS(a)"):
        return 1.0 / pl.GAMMA, "<="
    if label.startswith(("P2-C|bootstrap", "P3-D")):
        return ALPHA, "~"
    if label.startswith("P7"):
        return math.nan, "none"
    return min(1.0, ctx["H"] / ctx["gamma"]), "<="


def gain_rows(base, ctx, res, rows, cfg):
    """Paired gains of arm A at each SR: the ladder 1 -> 2 -> 3 -> 3-CS and 1 -> 3 (anytime-valid, common nominal
    alpha), the oracle best asset, and G_ADD,ex at the same lattice level (equal false alarm if the paired H0 difference
    lies within +-0.01)."""
    H, out = ctx["H"], []
    gen = rng(crc(f"gain|{ctx['dataset']}|{ctx['family']}"))
    h0 = res["off"][None]
    exact_b = "market" if ctx["family"] == "F3" else "best"
    for amp in [a for a in res["off"] if a is not None]:
        cells = pd.DataFrame([r for r in rows if r["amplitude"] == amp])

        def pick(pipe, reading, selection):
            sub = cells[(cells.pipeline == pipe) & (cells.reading == reading)]
            sub = sub[sub.asset_selection == selection] if selection else sub
            return sub.iloc[0] if len(sub) else None

        ladder = [("P1-C", "anytime-valid", "median"), ("P2-C", "anytime-valid", ""), ("P3-C", "anytime-valid", ""),
                  ("P3-CS(b)", "anytime-valid", "")]
        pairs = list(zip(ladder, ladder[1:])) + [(ladder[0], ladder[2]), (("P1-C", "anytime-valid", "best"), ladder[2]),
                                                 (("P1-C", "exact", "median"), ("P3-C", "exact", exact_b))]
        for A, B in pairs:
            ra, rb = pick(*A), pick(*B)
            if ra is None or rb is None:
                continue
            oa, ob = (offsets_of(res, amp, r, ctx) for r in (ra, rb))
            da, db = restricted(oa, H), restricted(ob, H)
            lo, hi = paired_ci(lambda idx: da[idx].mean(axis=1) / db[idx].mean(axis=1), len(da), cfg["boot"], gen)
            comparable = ra.censored_share <= 0.05 and rb.censored_share <= 0.05
            row = {**base, "row_type": "gain", "amplitude": amp, "pipeline": f"{A[0]}->{B[0]}",
                   "reading": A[1] if A[1] == B[1] else f"{A[1]}->{B[1]}", "unit": f"{ra.unit}->{rb.unit}",
                   "asset_selection": A[2], "oracle": bool(ra.oracle or rb.oracle or (B[2] == "best")),
                   "n": len(da), "g_add_h": float(da.mean() / db.mean()), "g_lo": lo, "g_hi": hi,
                   "g_label": gain_label(ra.det_rate, rb.det_rate),
                   "g_floor": rb.info_sub / ra.info_sub if ra.info_sub > 0 else math.nan,
                   "g_pred": ra.pred_delay / rb.pred_delay if comparable else math.nan,
                   "pred_comparable": bool(comparable), "fpr_a": ra.fpr, "fpr_b": rb.fpr,
                   "comparison": "common_nominal_alpha"}
            if A[1] == "exact":
                ha, hb = (h0_of(h0, r, ctx) for r in (ra, rb))
                dlo, dhi = paired_ci(lambda idx: (ha[idx] >= 0).mean(axis=1) - (hb[idx] >= 0).mean(axis=1), len(ha),
                                     cfg["boot"], gen)
                row.update(fa_diff_lo=dlo, fa_diff_hi=dhi, comparison="equal_fa_verified" if -0.01 <= dlo and dhi <= 0.01
                           else "equal_fa_not_shown")
            if not comparable:
                row["status"] = "not_directly_interpretable"
            out.append(row)
    return out


def offsets_of(res, amp, row, ctx):
    """Offsets of the unit of a cells row."""
    label = f"{row.pipeline}|{row.reading}" + (f"|{ctx['mode']}" if row.pipeline == "P3-C" and row.reading == "exact"
                                                else "")
    off = res["off"][amp][label]
    return off if off.ndim == 1 else off[:, unit_index(label, row.unit, ctx, load_window(ctx["dataset"])[3])]


def h0_of(h0, row, ctx):
    """H0 offsets of the unit of a cells row (paired H0 arm of the same cell)."""
    label = f"{row.pipeline}|{row.reading}" + (f"|{ctx['mode']}" if row.pipeline == "P3-C" and row.reading == "exact"
                                                else "")
    off = h0[label]
    return off if off.ndim == 1 else off[:, unit_index(label, row.unit, ctx, load_window(ctx["dataset"])[3])]


def run_cells(cfg, arm, jobs, log):
    """Arm A or S: every cell of every dataset, spans of cfg['span'] replicates, merged in submission order."""
    c, rows, gains = cfg[arm], [], []
    N1 = n1_ceilings()
    for name in cfg["datasets"]:
        t0 = time.time()
        states = frozen_states(name, c["H"], c.get("n_cal"))
        ctxs = cell_contexts(cfg, arm, name, states, log)
        spans = [(r, min(c["reps"], r + cfg["span"])) for r in range(0, c["reps"], cfg["span"])]
        parts = run_tasks([("cell", ctx, sp) for ctx in ctxs for sp in spans], jobs)
        for i, ctx in enumerate(ctxs):
            r, gn = cell_rows(arm, ctx, merge(parts[i * len(spans):(i + 1) * len(spans)]), cfg, N1[name])
            rows += r
            gains += gn
        log(f"arm {arm} {name}: {len(ctxs)} cells x {c['reps']} replicates, {time.time() - t0:.1f} s")
    return rows + gains


def n1_ceilings():
    """N1 = E[sigma^2] E[sigma^-2] of the audit (raw variant), the P3-CS (b) ceiling of plan section 8."""
    cc = pd.read_csv(AUDIT / "channel_ceilings.csv", float_precision="round_trip")
    cc = cc[(cc.ceiling == "N1") & (cc.variant == "raw")]
    return dict(zip(cc.dataset, cc.value))


def amplitude_grid(cfg, jobs, log):
    """Pilot of arm B on disjoint keys: per family and dataset, the prompt amplitudes if the median delay of the measured
    pipeline stays in the band over the N grid, else the closest consecutive pair of the declared scale (C-e1-amplitude-grid)."""
    b, rows, grid = cfg["B"], [], {}
    tasks, keys = [], []
    for fam, cell in b["cells"].items():
        for name in cell["datasets"]:
            for s in range(b["pilot"]["chains"]):
                for N in b["N"][name]:
                    tasks.append(("b", cfg, (name, fam, s, N, tuple(cell["scale"]), b["pilot"]["reps"], True)))
                    keys.append((fam, name, s, N))
    parts = run_tasks(tasks, jobs)
    label = {"F3": "P2-C|anytime-valid", "F2": "P3-C|anytime-valid"}
    for fam, cell in b["cells"].items():
        for name in cell["datasets"]:
            ok = {}
            for amp in cell["scale"]:
                okN = []
                for N in b["N"][name]:
                    off = np.concatenate([p["off"][amp][label[fam]] for k, p in zip(keys, parts)
                                          if k[0] == fam and k[1] == name and k[3] == N])
                    s = delay_summary(off, b["H"])
                    good = s["det_rate"] > 0.5 and b["band"][0] <= s["median_delay"] <= b["band"][1]
                    okN.append(good)
                    rows.append({"kind": "pilot", "dataset": name, "family": fam, "amplitude": amp, "N": N,
                                 "pipeline": label[fam].split("|")[0], "det_rate": s["det_rate"],
                                 "median_delay": s["median_delay"], "rule_ok": good})
                ok[amp] = all(okN)
            prompt, scale = cell["amplitudes"], cell["scale"]
            pairs = [(scale[i], scale[i + 1]) for i in range(len(scale) - 1) if ok[scale[i]] and ok[scale[i + 1]]]
            if all(ok.get(a, False) for a in prompt):
                chosen, status = list(prompt), "prompt_amplitudes_in_rule"
            elif pairs:
                chosen = list(min(pairs, key=lambda p: sum(abs(math.log(x / y)) for x, y in zip(p, prompt))))
                status = "closest_pair_in_rule"
            else:
                chosen, status = list(prompt), "out_of_rule"
            grid[fam, name] = chosen
            rows.append({"kind": "grid", "dataset": name, "family": fam, "amplitudes": json.dumps(chosen),
                         "status": status})
            log(f"arm B pilot {fam} {name}: in-rule amplitudes {[a for a in scale if ok[a]]}, chosen {chosen} ({status})")
    return grid, rows


def run_b(cfg, jobs, log):
    """Arm B: pilot, frozen P1 references, (chain, N) cells, slopes of log G_ADD,H on log N and the verdicts (ii), (iii)."""
    b = cfg["B"]
    grid, rows = amplitude_grid(cfg, jobs, log)
    for name in sorted({n for cell in b["cells"].values() for n in cell["datasets"]}):
        for s in range(b["chains"]):
            ref = int(b_chain(name, s)[0])
            rows.append({"kind": "reference", "dataset": name, "chain": s, "ref_asset": load_window(name)[3][ref],
                         "ref_index": ref})
    tasks, keys = [], []
    for fam, cell in b["cells"].items():
        for name in cell["datasets"]:
            for s in range(b["chains"]):
                for N in b["N"][name]:
                    tasks.append(("b", cfg, (name, fam, s, N, tuple(grid[fam, name]), b["reps"], False)))
                    keys.append((fam, name, s, N))
    t0 = time.time()
    parts = run_tasks(tasks, jobs)
    log(f"arm B: {len(tasks)} cells x {b['reps']} replicates, {time.time() - t0:.1f} s")
    cells = []
    for (fam, name, s, N), p in zip(keys, parts):
        for amp in grid[fam, name]:
            for label, off in p["off"][amp].items():
                if label.startswith("P1-C") and label.endswith("exact"):
                    continue
                sm = delay_summary(off[:, 0] if off.ndim == 2 else off, b["H"])
                cells.append({"kind": "cell", "dataset": name, "family": fam, "amplitude": amp, "chain": s, "N": N,
                              "pipeline": label.split("|")[0], "reading": label.split("|")[1], **sm,
                              "a_max": p["a_max"].get(amp, math.nan),
                              "gate_passed": None if p["gate"] is None else bool(p["gate"]["passed"])})
    cdf = pd.DataFrame(cells)
    rows += cells
    gen, verdict = rng(crc("B|slopes")), {"ii": [], "iii": []}
    for (name, fam, amp), g in cdf.groupby(["dataset", "family", "amplitude"], sort=True):
        ref = g[g.pipeline == "P1-C"].set_index(["chain", "N"])
        for pipe in [p for p in g.pipeline.unique() if p != "P1-C"]:
            sub = g[g.pipeline == pipe].set_index(["chain", "N"])
            keep = sub.det_rate > 0.5
            for scope, nmin in (("all", 0), ("n_ge_min", b["n_min_ii"])):
                idx = sub.index[keep & (sub.index.get_level_values("N") >= nmin)]
                if fam == "F3" and scope == "all" or fam == "F2" and scope == "n_ge_min":
                    continue
                for target_, y in (("log_ratio", np.log(ref.loc[idx, "add_h"].to_numpy() / sub.loc[idx, "add_h"].to_numpy())),
                                   ("log_add_h", np.log(sub.loc[idx, "add_h"].to_numpy())),
                                   ("log_add_h_ref", np.log(ref.loc[idx, "add_h"].to_numpy()))):
                    x = np.log(idx.get_level_values("N").to_numpy(dtype=np.float64))
                    sl = slope_fit(x, y, idx.get_level_values("chain").to_numpy(), cfg["boot"], gen) if len(idx) > 2 \
                        else (math.nan, math.nan, math.nan)
                    row = {"kind": "slope", "dataset": name, "family": fam, "amplitude": amp, "pipeline": pipe,
                           "scope": scope, "target": target_, "slope": sl[0], "lo": sl[1], "hi": sl[2],
                           "n_cells": len(idx), "n_excluded": int((~keep).sum())}
                    rows.append(row)
                    if target_ == "log_ratio" and fam == "F3" and pipe == "P2-C":
                        verdict["ii"].append((name, amp, sl, (sl[1] <= 0 <= sl[2]) or sl[2] < 0.15))
                    if target_ == "log_ratio" and fam == "F2" and pipe == "P3-C":
                        verdict["iii"].append((name, amp, sl, sl[0] > 0 and sl[1] > 0))
    for k in ("ii", "iii"):
        rows.append({"kind": "verdict", "criterion": k, "status": "PASS" if verdict[k] and all(v[3] for v in verdict[k])
                     else "FAIL", "detail": json.dumps([[n, a, *[round(x, 6) for x in sl], ok]
                                                       for n, a, sl, ok in verdict[k]])})
    log(f"arm B verdicts: {verdict}")
    return rows, verdict


def run_g(cfg, jobs, log):
    """G_SR by bisection on log2 SR per (cell, pipeline): SR at which the detection rate within H reaches 1/2 (P1-C:
    median over its 20 assets), the same replicates at every step; censored above the upper end."""
    gcfg, rows = cfg["G"], []
    H = gcfg["H"]
    pipes = {"P1-C": None, "P2-C": "P2-C", "P3-C": "P3-C/{m}", "P3-CS(b)": "P3-CS(b)/{m}", "P7": "P7"}
    ctxs = {}
    for name, fam in gcfg["cells"]:
        if name not in cfg["datasets"]:
            continue
        states = frozen_states(name, H)
        X, _, splits, _, _ = load_window(name)
        a, b = splits["calib"]
        K = len(states["P3-C/factor"][1]["channels"]["residual"]) + 1
        params = {"calib": (a, b), "K": K, "fit": fit_background(X[a:b], K),
                  **({"C": chars4(name)} if fam == "F2" else {})}
        m = "full" if fam == "F2" else "factor"
        for pipe, st in pipes.items():
            ctxs[name, fam, pipe] = {"dataset": name, "family": fam, "H": H, "pre": 0, "crc": crc(f"G|{name}|{fam}"),
                                     "states": states, "chunk": cfg["chunk"], "sel": lattice_selection(H),
                                     "gamma": pl.horizon_gamma(H, ALPHA), "params": params,
                                     "p1": p1_assets(name) if pipe == "P1-C" else None,
                                     "readings": [] if st is None else [{"label": f"{pipe}|anytime-valid",
                                                                         "state": st.format(m=m),
                                                                         "drift_only": pipe == "P7"}]}
    lo = {k: float(gcfg["log2"][0]) for k in ctxs}
    hi = {k: float(gcfg["log2"][1]) for k in ctxs}
    censored = {}

    def rates(points):
        tasks = []
        for k, x in points.items():
            sr = 2.0 ** x
            tasks.append(("cell", {**ctxs[k], "amps": [sr], "inject": {sr: (fl.kl_from_sharpe(sr), ctxs[k]["params"])}},
                          (0, gcfg["reps"])))
        out = {}
        for (k, x), p in zip(points.items(), run_tasks(tasks, jobs)):
            off = p["off"][2.0 ** x][f"{k[2]}|anytime-valid"]
            out[k] = float(np.median((off >= 0).mean(axis=0))) if off.ndim == 2 else float((off >= 0).mean())
        return out

    top = rates(dict(hi))
    for k, r in top.items():
        censored[k] = r < 0.5
    active = [k for k in ctxs if not censored[k]]
    for _ in range(gcfg["steps"]):
        mids = {k: 0.5 * (lo[k] + hi[k]) for k in active}
        for k, r in rates(mids).items():
            (hi if r >= 0.5 else lo)[k] = mids[k]
    for (name, fam, pipe) in ctxs:
        k = (name, fam, pipe)
        rows.append({"row_type": "g_sr", "arm": "G", "dataset": name, "family": fam, "H": H,
                     "gamma": pl.horizon_gamma(H, ALPHA), "pipeline": pipe, "reading": "anytime-valid",
                     "n": gcfg["reps"], "sr_star": math.inf if censored[k] else 2.0 ** (0.5 * (lo[k] + hi[k])),
                     "sr_lo": 2.0 ** lo[k], "sr_hi": 2.0 ** hi[k], "retrospective": True,
                     "status": "censored_above_range" if censored[k] else "bisection",
                     "asset_selection": "median" if pipe == "P1-C" else ""})
    order = list(pipes)
    for name, fam in {(k[0], k[1]) for k in ctxs}:
        for A, B in zip(order, order[1:]):
            ra = next(r for r in rows if r["dataset"] == name and r["family"] == fam and r["pipeline"] == A)
            rb = next(r for r in rows if r["dataset"] == name and r["family"] == fam and r["pipeline"] == B)
            rows.append({"row_type": "g_sr_gain", "arm": "G", "dataset": name, "family": fam, "H": H,
                         "pipeline": f"{A}->{B}", "reading": "anytime-valid",
                         "g_add_h": ra["sr_star"] / rb["sr_star"], "retrospective": True,
                         "status": "G_SR = SR*_A / SR*_B"})
    log(f"G_SR: {[(r['dataset'], r['family'], r['pipeline'], r.get('sr_star')) for r in rows if r['row_type'] == 'g_sr']}")
    return rows


def run_c(cfg, log):
    """Arm C, descriptive: budget shares per subspace and alarm shares on raw rows (P1-C label stream with calib q_hat,
    P3-C factor recentred on calib q_hat where central symmetry is rejected), real against circular rotations."""
    c, rows = cfg["C"], []
    sym = pd.read_csv(AUDIT / "symmetry_tests.csv", float_precision="round_trip")
    for name in cfg["datasets"]:
        X, days, splits, assets, _ = load_window(name)
        a, b = splits["calib"]
        T = len(days)
        st = frozen_states(name, 2000)["P3-C/factor"][1]
        D = len(st["channels"]["residual"]) + 1
        lab = (X[:, p1_assets(name)] > 0).astype(np.float64)
        x1 = recentred(lab, lab[a:b].mean(axis=0))
        Bz = coin_bits(st["rep"].transform_panel(X)["z_odd"], rng(crc(f"C|{name}"), 0))
        s = sym[(sym.dataset == name) & sym.direction.isin([f"PC{k + 1}" for k in range(D)])].set_index("direction")
        rejected = np.array([bool(s.loc[f"PC{k + 1}", "binom_reject"] or s.loc[f"PC{k + 1}", "triples_reject"])
                             for k in range(D)])
        xz = recentred(Bz, np.where(rejected, Bz[a:b].mean(axis=0), 0.5))
        for dating in c["datings"]:
            phases = spy_phases(dating, days)
            pairs = transitions(phases)
            offsets = rng(crc(f"C|{name}|{dating}"), 1).integers(0, T, c["rotations"])
            real = budget_shares(name, dating, gammas=tuple(c["gammas"]))
            plac = [budget_shares(name, dating, int(o), tuple(c["gammas"])) for o in offsets]
            for i, r in enumerate(real):
                p = np.array([pl_[i]["share"] for pl_ in plac])
                rows.append(phase_row(name, dating, "budget", r["subspace"], r["gamma"], len(pairs), r["share"], p))
            rot = [rotate_phases(phases, T, int(o)) for o in offsets]
            mon = [phases[j][3] for _, j in pairs]
            mon_p = [np.stack([rp[j][3] for rp in rot]) for _, j in pairs]
            for monitor, x, dic in (("P1-C label (q_hat calib)", x1, False), ("P3-C factor (recentred where rejected)",
                                                                             xz, True)):
                real_share = float(np.mean([np.mean(o >= 0) for o in phase_offsets(x, mon, ALPHA, dic)]))
                p = np.mean([(o >= 0).reshape(len(offsets), -1).mean(axis=1) for o in phase_offsets(x, mon_p, ALPHA, dic)],
                            axis=0)
                rows.append(phase_row(name, dating, "alarm", monitor, "L/alpha", len(pairs), real_share, p))
        log(f"arm C {name}: rejected P3-C channels {np.flatnonzero(rejected).tolist()}")
    return rows


def phase_row(name, dating, kind, subspace, gamma, n, real, placebo):
    """One e1_real_phases row: real share against the placebo rotations (upper bounds, not causal fractions)."""
    lo, hi = np.percentile(placebo, [2.5, 97.5])
    return {"dataset": name, "dating": dating, "kind": kind, "subspace": subspace, "gamma": gamma, "n_phases": n,
            "share_real": real, "placebo_mean": float(placebo.mean()), "placebo_lo": float(lo), "placebo_hi": float(hi),
            "p_placebo": (1 + int((placebo >= real).sum())) / (1 + placebo.size), "n_placebo": int(placebo.size),
            "label": "alignment_upper_bound_not_causal", "retrospective": True}


def summary_lines(cfg, j2, bver, cells):
    """e1_j2_summary.txt: window and retrospective label, one PASS/FAIL line per criterion with its evidence."""
    lines = [f"window {WINDOW[0]}..{WINDOW[1]}; retrospective: the calib rows 2016-04-07..2019-12-31 follow every onset "
             f"at H = 2000; add_h = mean(min(T, H)) is a restricted delay, Phi(gamma I) / I a diffusion approximation"]
    if j2 is None:
        lines.append("J2(i): NOT RUN")
    else:
        lines.append(f"J2(i): {'PASS' if j2['pass'] else 'FAIL'} - {j2['n']} exact sign-stream controls x {j2['reps']} "
                     f"replicates ({j2['label']} keys), |FPR - lattice level| <= 0.01: {j2['n_fail']} failures; "
                     f"a priori model P(FAIL | all exact, independent keys) = {j2['p_any']:.3f} (computed, not "
                     f"measured), expected false FAILs {j2['expected']:.2f}, "
                     f"P(#FAIL >= {j2['n_fail']} | exact) = {j2['p_tail']:.3f}; Holm 1 % rejections {j2['holm']}; "
                     f"outside the 99 % region {j2['outside99']}; reported without rerun or reseeding")
    for k, what in (("ii", "slope of log G_ADD,H(P1 ref -> P2-C) on log N, F3, N >= 20: CI contains 0 or upper < 0.15"),
                    ("iii", "slope of log G_ADD,H(P1 ref -> P3-C full) on log N, F2: positive, CI excludes 0")):
        if bver is None:
            lines.append(f"J2({k}): NOT RUN")
            continue
        ok = bool(bver[k]) and all(v[3] for v in bver[k])
        lines.append(f"J2({k}): {'PASS' if ok else 'FAIL'} - {what}: " + "; ".join(
            f"{n} amp {a:g}: {sl[0]:.3f} [{sl[1]:.3f}, {sl[2]:.3f}]" for n, a, sl, _ in bver[k]))
    g = cells[(cells.row_type == "gain") & (cells.arm == "A")] if len(cells) else cells
    if not len(g):
        lines.append("J2(iv): NOT RUN")
        return lines
    g4 = g[(g.amplitude == 4) & g.pipeline.isin(["P1-C->P2-C", "P2-C->P3-C", "P3-C->P3-CS(b)"])
           & (g.asset_selection.fillna("").isin(["median", ""])) & (g.reading == "anytime-valid")]
    expected = {(d, f) for d in cfg["datasets"] for f in cfg["A"]["families"].get(d, [])}
    complete = all(len(g4[(g4.dataset == d) & (g4.family == f)]) == 3 for d, f in expected) and bool(
        (np.isfinite(g4.g_add_h) & np.isfinite(g4.g_lo) & (np.isfinite(g4.g_pred) | ~g4.pred_comparable.astype(bool))).all())
    lines.append(f"J2(iv): {'PASS' if complete else 'FAIL'} - gains 1 -> 2 -> 3 -> 3-CS at SR = 4 (convention a), "
                 f"measured with paired 95 % CI and predicted (or not_directly_interpretable), common nominal alpha:")
    for r in g4.itertuples():
        lines.append(f"  {r.dataset} {r.family} {r.pipeline}: G_ADD,H = {r.g_add_h:.3f} [{r.g_lo:.3f}, {r.g_hi:.3f}] "
                     f"({r.g_label}); G_floor = {r.g_floor:.3f}; predicted = {r.g_pred:.3f}; FPR {r.fpr_a:.4f} -> "
                     f"{r.fpr_b:.4f}{'' if r.pred_comparable else '; prediction not directly interpretable'}")
    return lines


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _save(plt, fig, fig_dir, stem):
    for ext in ("png", "pdf"):
        fig.savefig(fig_dir / f"{stem}.{ext}", dpi=150, bbox_inches="tight", metadata={"CreationDate": None}
                    if ext == "pdf" else {"Software": None})
    plt.close(fig)


def plot(out, fig_dir):
    """Figures from the CSVs only: J2(i) FPR against the lattice level, arm A restricted delays at SR = 4, arm B add_h
    against N."""
    import matplotlib.pyplot as plt
    fig_dir.mkdir(parents=True, exist_ok=True)
    if (out / "e1_null.csv").exists():
        nd = pd.read_csv(out / "e1_null.csv", float_precision="round_trip")
        fig, axes = plt.subplots(1, nd.H.nunique(), figsize=(5 * nd.H.nunique(), 3.4), squeeze=False)
        for ax, (H, g) in zip(axes[0], nd.groupby("H")):
            x = np.arange(len(g))
            lv, tol = g.level.iloc[0], g.tolerance.iloc[0]
            ax.axhspan(lv - tol, lv + tol, color="#d9d9d9", lw=0)
            ax.axhline(lv, color="#555555", lw=0.8)
            for i, (pipe, gg) in enumerate(g.groupby("pipeline")):
                ax.scatter(x[(g.pipeline == pipe).to_numpy()], gg.fpr, s=12, color=SERIES[i], label=pipe)
            ax.set_title(f"H = {H}: FPR per control")
            ax.set_xlabel("control")
            ax.set_ylabel("FPR(H)")
            ax.legend(frameon=False, fontsize=8)
        _save(plt, fig, fig_dir, "e1_j2i_fpr")
    if (out / "e1_cells.csv").exists():
        cd = pd.read_csv(out / "e1_cells.csv", float_precision="round_trip")
        a = cd[(cd.row_type == "cell") & (cd.arm == "A") & (cd.amplitude == 4) & (cd.reading == "anytime-valid")
               & cd.asset_selection.fillna("").isin(["median", ""])]
        if len(a):
            combos = sorted({(d, f) for d, f in zip(a.dataset, a.family)})
            fig, ax = plt.subplots(figsize=(1.6 * len(combos) + 3, 3.4))
            for i, pipe in enumerate(("P1-C", "P2-C", "P3-C", "P3-CS(b)", "P7")):
                v = [a[(a.dataset == d) & (a.family == f) & (a.pipeline == pipe)].add_h.mean() for d, f in combos]
                ax.bar(np.arange(len(combos)) + 0.16 * (i - 2), v, 0.16, color=SERIES[i], label=pipe)
            ax.set_xticks(np.arange(len(combos)), [f"{d}\n{f}" for d, f in combos], fontsize=8)
            ax.set_ylabel("add_h = mean(min(T, H)), days")
            ax.set_title("Arm A, SR = 4, H = 2000 (restricted delays)")
            ax.legend(frameon=False, fontsize=8, ncol=5)
            _save(plt, fig, fig_dir, "e1_arm_a_delays")
    if (out / "e1_slopes.csv").exists():
        sd = pd.read_csv(out / "e1_slopes.csv", float_precision="round_trip")
        c = sd[sd.kind == "cell"]
        if len(c):
            groups = sorted({(d, f, a) for d, f, a in zip(c.dataset, c.family, c.amplitude)})
            fig, axes = plt.subplots(1, len(groups), figsize=(3.2 * len(groups), 3.2), squeeze=False)
            for ax, (d, f, amp) in zip(axes[0], groups):
                g = c[(c.dataset == d) & (c.family == f) & (c.amplitude == amp)]
                for i, (pipe, gg) in enumerate(g.groupby("pipeline")):
                    m = gg.groupby("N").add_h.mean()
                    ax.plot(m.index, m.values, marker="o", ms=3, color=SERIES[i], label=pipe)
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.set_title(f"{d} {f} amp {amp:g}", fontsize=9)
                ax.set_xlabel("N")
            axes[0][0].set_ylabel("add_h (days)")
            axes[0][0].legend(frameon=False, fontsize=7)
            _save(plt, fig, fig_dir, "e1_arm_b_slopes")


def load_config(path, quick):
    """configs/e1.yaml, with the quick block merged one level down when --quick."""
    cfg = yaml.safe_load(Path(path).read_text())
    if quick:
        for k, v in cfg["quick"].items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    cfg[k][kk] = {**cfg[k][kk], **vv} if isinstance(vv, dict) and isinstance(cfg[k].get(kk), dict) \
                        else vv
            else:
                cfg[k] = v
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description="E1: the detection problem on D6 backgrounds and the J2 criteria.")
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--quick", action="store_true", help="smoke test: 100 onsets, SR = 4, N in {16, 64}")
    ap.add_argument("--arms", default="J2I,A,S,B,G,C")
    ap.add_argument("--jobs", type=int, default=24)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "e1")
    ap.add_argument("--fig-dir", type=Path, default=REPO_ROOT / "figures" / "e1")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "e1")
    ap.add_argument("--include-test-window", action="store_true", help="refused before J4 (configs/FROZEN.json)")
    args = ap.parse_args(argv)
    if args.include_test_window:
        ap.error(f"--include-test-window is refused: {FROZEN_JSON.name} is absent or unchecked before stream 21")  # ponytail: refusal until stream 21 defines the frozen-hash check
    arms = set(args.arms.split(","))
    if arms - {"J2I", "A", "S", "B", "G", "C"} or args.jobs < 1:
        ap.error("unknown arm in --arms or --jobs < 1")
    cfg = copy.deepcopy(load_config(args.config, args.quick))
    for d in (args.out, args.log_dir):
        d.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        log_lines.append(msg)
        print(msg, flush=True)

    t0 = time.time()
    log(f"generator: python experiments/e1_problem.py {' '.join(argv if argv is not None else sys.argv[1:])}")
    log(f"window {WINDOW[0]}..{WINDOW[1]}; datasets {cfg['datasets']}; arms {sorted(arms)}; "
        f"predicted_gains.csv sha256 {_sha256(AUDIT / 'predicted_gains.csv')} (cited as is, NaN kept)")
    j2 = bver = None
    cell_rows_, slope_rows, phase_rows = [], [], []
    if "J2I" in arms:
        t = time.time()
        null_df, j2 = run_j2i(cfg, args.jobs, log)
        pl.save_fair_csv(null_df, args.out / "e1_null.csv")
        log(f"block J2I {time.time() - t:.1f} s")
    for arm in ("A", "S"):
        if arm in arms:
            t = time.time()
            cell_rows_ += run_cells(cfg, arm, args.jobs, log)
            log(f"block {arm} {time.time() - t:.1f} s")
    if "G" in arms:
        t = time.time()
        cell_rows_ += run_g(cfg, args.jobs, log)
        log(f"block G {time.time() - t:.1f} s")
    cells = pd.DataFrame(cell_rows_, columns=CELL_COLUMNS)
    if len(cells):
        pl.save_fair_csv(cells, args.out / "e1_cells.csv")
    if "B" in arms:
        t = time.time()
        slope_rows, bver = run_b(cfg, args.jobs, log)
        pl.save_fair_csv(pd.DataFrame(slope_rows), args.out / "e1_slopes.csv")
        log(f"block B {time.time() - t:.1f} s")
    if "C" in arms:
        t = time.time()
        phase_rows = run_c(cfg, log)
        pl.save_fair_csv(pd.DataFrame(phase_rows), args.out / "e1_real_phases.csv")
        log(f"block C {time.time() - t:.1f} s")
    (args.out / "e1_j2_summary.txt").write_text("\n".join(summary_lines(cfg, j2, bver, cells)) + "\n")
    plot(args.out, args.fig_dir)
    for f in sorted(args.out.glob("e1_*")):
        log(f"sha256 {f.name} {_sha256(f)}")
    log(f"total {time.time() - t0:.1f} s")
    (args.log_dir / "e1.log").write_text("\n".join(log_lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
