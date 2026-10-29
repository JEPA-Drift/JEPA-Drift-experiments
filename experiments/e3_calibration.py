"""Stream 13, E3 (Article C section 5.2, J2 criterion i): calibration of the monitors under H0, without any drift
(prompts/plans/plan-13.md, GO prompts/GO-stream-13.md).

Backgrounds
  D5     independent GARCH(0.08, 0.90) paths with Student t7 (sim.Garch) or Gaussian (sim.garch_panel, nu=None)
         innovations: 941 clean days, then 2,000 monitored days (P1 readings) in two SeedSequence roles, calibration
         paths fixing the P1-D thresholds and independent evaluation paths carrying the FPR and its Wilson interval;
         i.i.d. or Gaussian GARCH paths for the overshoot penalty; i.i.d. paths for the window encoders
  D6     d2_us97 and d3_239 rows 2005-01-04..2019-12-31 (earlier pre-monitor rows excluded only as declared and
         counted: D3 2005-01-03), one Rademacher sign per day shared by all assets: odd streams are exact
         conditionally on the panel, even streams (P1-D, P3-D) are unchanged by the flips
  raw    every H-day window of the same rows: one trajectory, overlapping windows, descriptive without interval
  coins  independent fair +-1 coins: the ARL0 reference of the e-detectors
Every local CUSUM restarts at S_0 = 0 at the start of its window or path, and nothing is injected (family H0 only).
ARL0: restricted mean of min(T, 60 gamma); PASS iff its 99 % lower bound reaches gamma, else INDETERMINATE (no FAIL
without a tail bound); the bounded stopping-time check E[M_sigma] <= E[sigma] is tail-free. Counts over cells that
share draws are descriptive.
Outputs: <out>/{e3_cells,e3_arl0,e3_raw_placebo,e3_overshoot,e3_window_encoders}.csv (save_fair_csv) and
<out>/e3_j2_check.txt (secondary calibration check, no J2 verdict: the primary J2 (i) verdict is E1's, stream 12, at
2,000 replicates); <fig-dir>/{fpr_cells,arl0,raw_placebo,gamma}.{png,pdf} drawn from the CSVs; <log-dir>/run.log.

Usage: python experiments/e3_calibration.py [--quick] [--jobs 24] --out results/e3
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
import math
import multiprocessing
import subprocess
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import binom, norm
from statsmodels.stats.diagnostic import acorr_ljungbox

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import pipelines as pl
from jepadrift import sim
from jepadrift.injection import symmetrize
from jepadrift.monitors import eprocess, lattice
from jepadrift.monitors.cusum import P1, bilateral_delay_vec, cusum_trajectory_vec, strict_cusum_vec
from jepadrift.monitors.gamma import gamma_spectral, required_threshold
from jepadrift.monitors.streams import energy_stream, exact_sign_stream, label_stream
from jepadrift.representations.extract import DATASETS
from jepadrift.stats.garch import compute_gamma_exact, fit_garch_qmle
from jepadrift.stats.intervals import wilson

STREAM = 13
REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVED = REPO_ROOT / "data" / "derived"
AUDIT = REPO_ROOT / "results" / "audit" / "symmetry_tests.csv"
CONFIG = REPO_ROOT / "configs" / "e3.yaml"
WINDOW = (np.datetime64("2005-01-04"), np.datetime64("2019-12-31"))
N_TICKERS = 5
EXCLUDED_DAYS = {"d2_us97": (), "d3_239": ("2005-01-03",)}
SIGN_DELTA = P1["P1-C/C"]["delta"]
ENERGY_DELTA = P1["P1-D/B"]["delta"]
LAMBDA_R01 = P1["P1-D/B"]["lambda_iid"]
Z99_ONE = 2.3263478740408408
Z95 = 1.959963984540054
CELL_SEED = 10 ** 6
TYPES = ("sr", "cusum")
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e5e4e0", "#fcfcfb"
CELL_COLUMNS = ["block", "background", "dataset", "pipeline", "reading", "arm", "unit", "H", "gamma", "threshold", "n",
                "alarms", "fpr", "fpr_lo", "fpr_hi", "ci_kind", "deff", "n_eff", "target", "target_kind", "n_cal",
                "n_eval", "region_lo", "region_hi", "in_region", "validity", "n_windows", "n_disjoint",
                "in_sample_share", "null_rows", "lam_iid", "lam_req", "gamma_op", "gamma_spec", "gamma_spec_q1",
                "gamma_spec_q3", "gamma_hat", "gamma_exact", "converged_share", "q_hat", "q_mean_pretrain", "q_mean_calib"]
RAW_COLUMNS = ["dataset", "pipeline", "reading", "arm", "unit", "direction", "H", "threshold", "n_windows",
               "n_disjoint", "stride", "in_sample_share", "alarms", "rate", "target", "target_kind", "gap",
               "q_hat_calib", "q_mean", "zero_share", "audit_q_hat", "binom_p_holm", "triples_p_holm", "binom_reject",
               "triples_reject", "design"]
ARL_COLUMNS = ["background", "dataset", "pipeline", "columns", "type", "gamma", "cap", "n", "censored",
               "censored_share", "restricted_mean", "se", "deff", "n_eff", "lb99", "ratio", "median", "deficit",
               "deficit_lo", "deficit_hi", "classification", "ineq_mean", "ineq_se", "ineq_lb99", "ineq_lb_fw",
               "ineq_violated"]
OVER_COLUMNS = ["background", "statistic", "delta", "threshold", "role", "n", "censored", "arl0", "se", "deff", "n_eff",
                "arl0_lo", "arl0_hi", "reference", "rel_gap", "gate", "arl0_exact", "gamma_spec", "lam_req", "gamma_op"]
ENC_COLUMNS = ["background", "dataset", "L", "H", "n", "ci_kind", "deff", "n_eff", "n_cal", "gamma_spec",
               "gamma_spec_wide", "bandwidth_wide", "gamma_analytic", "sd", "lam_iid", "lam_req", "gamma_op",
               "fpr_cusum", "fpr_cusum_lo", "fpr_cusum_hi", "fpr_sign", "fpr_sign_lo", "fpr_sign_hi", "level_sign",
               "lb_reject", "lb_reject_lo", "lb_reject_hi", "lb_median_p", "lb_nan"]


def seed_key(*key):
    """[13, *key] with every string part replaced by its CRC32: the SeedSequence entropy of a cell or a replicate."""
    return [STREAM, *(zlib.crc32(k.encode()) if isinstance(k, str) else int(k) for k in key)]


def rng(*key):
    """Local generator keyed on SeedSequence(seed_key(*key)); no global state."""
    return np.random.default_rng(np.random.SeedSequence(seed_key(*key)))


def check_window(days):
    """Refuse any row outside [2005-01-04, 2019-12-31]: the strict real bound of E3 (pre-J4 guard)."""
    d = np.asarray(days, dtype="datetime64[D]")
    if d.size == 0 or d.min() < WINDOW[0] or d.max() > WINDOW[1]:
        raise ValueError(f"real rows must lie in [{WINDOW[0]}, {WINDOW[1]}]")


@functools.lru_cache(maxsize=None)
def load_rows(name):
    """Rows of the pre-monitor segment dated 2005-01-04..2019-12-31, with their splits and asset names; earlier rows are
    excluded only as declared in EXCLUDED_DAYS (any other early row raises), before the strict window check."""
    load, load_splits = DATASETS[name]
    ret, dates, assets = load()
    sp = load_splits(name)
    a, b = pl.split_rows(dates, sp)["pre_monitor"]
    days = np.asarray(dates[a:b], dtype="datetime64[D]")
    early = days < WINDOW[0]
    if tuple(str(d) for d in days[early]) != EXCLUDED_DAYS[name]:
        raise ValueError(f"{name}: rows before {WINDOW[0]} {[str(d) for d in days[early]]} differ from the declared "
                         f"exclusion {EXCLUDED_DAYS[name]}")
    X, days = np.ascontiguousarray(np.asarray(ret[a:b])[~early]), days[~early]
    check_window(days)
    if not np.isfinite(X).all():
        raise ValueError(f"{name}: the rows must be finite")
    return X, days, pl.split_rows(days, sp), list(assets)


def tickers(name):
    """The P1 assets of E3, those of E1's J2 (i): pipelines.composition_for(5, N)."""
    return [int(c) for c in pl.composition_for(N_TICKERS, load_rows(name)[0].shape[1])]


@functools.lru_cache(maxsize=None)
def raw_basis(name):
    """P3-C state fitted on the raw calib rows with K at the MP edge (the audit basis) and its Z panel of all rows."""
    X, _, splits, _ = load_rows(name)
    state = pl.fit_pipeline(pl.make_spec("P3-C", dataset=name), X, splits)
    return state, state["rep"].transform_panel(X)


def packets(n, size):
    """Replicate ranges [r0, r1) of at most `size` replicates: scheduling units only."""
    size = max(1, int(size))
    return [(r0, min(r0 + size, n)) for r0 in range(0, n, size)]


def window_counts(n, H, calib):
    """Number of H-day windows of n rows, number of disjoint windows, share of windows intersecting the calib rows."""
    starts = np.arange(n - H + 1)
    return int(starts.size), n // H, float(((starts + H > calib[0]) & (starts < calib[1])).mean())


def window_offsets(x, starts, H, delta, thr, sided=2):
    """First alarm offset (-1 when none) of the strict CUSUM restarted at S_0 = 0 on x[s:s + H] for each start s."""
    w = np.lib.stride_tricks.sliding_window_view(np.asarray(x, dtype=np.float64), H)[np.asarray(starts, dtype=np.int64)]
    return bilateral_delay_vec(w, delta, thr) if sided == 2 else strict_cusum_vec(w, delta, thr)


def window_peaks(x, starts, H, delta):
    """Peak of the one-sided CUSUM restarted at S_0 = 0 on x[s:s + H]: the strict rule alarms at lambda iff peak > lambda."""
    w = np.lib.stride_tricks.sliding_window_view(np.asarray(x, dtype=np.float64), H)[np.asarray(starts, dtype=np.int64)]
    return cusum_trajectory_vec(w, delta).max(axis=-1)


def fpr_threshold(peaks, alpha):
    """Smallest lambda with mean(peaks > lambda) <= alpha: the value monitors.gamma.required_threshold bisects towards."""
    p = np.sort(np.asarray(peaks, dtype=np.float64))
    return float(p[p.size - 1 - int(math.floor(alpha * p.size + 1e-9))])


def p1c_stream(y, q_hat=None, coins=None):
    """P1-C stream: Article B label stream 1{y > 0} - q_hat when q_hat is given, else the exact sign stream (ties by coin)."""
    return label_stream(y, q_hat) if q_hat is not None else exact_sign_stream(y, coins)


def p1d_fit(clean):
    """Article B P1-D constants on clean rows (R01 l.263-273): mu = mean(r^2), sigma = std(r^2), Gamma_hat, converged."""
    clean = np.asarray(clean, dtype=np.float64)
    (_, a, b), converged = fit_garch_qmle(clean - np.mean(clean))
    return float(np.mean(clean ** 2)), float(np.std(clean ** 2)), float(compute_gamma_exact(a, b)), bool(converged)


def encoder(y, L):
    """Window encoder z_t = mean of y over the L days ending at t (window-local sums), for t = L - 1, ..., last axis."""
    return np.lib.stride_tricks.sliding_window_view(np.asarray(y, dtype=np.float64), L, axis=-1).mean(axis=-1)


def run_lengths(paths, delta, thr, cap):
    """Run length (first alarm offset + 1) of the strict one-sided CUSUM restarted at S_0 = 0 on each path, cap when
    there is no alarm, and the censored flags."""
    off = strict_cusum_vec(paths, delta, thr)
    return np.where(off >= 0, off + 1, cap), off < 0


def brook_evans_arl0(k, h, m):
    """ARL0 of S = max(0, S + x - k), alarm S > h, x ~ N(0, 1), on an m-state Markov chain [Brook and Evans, 1972]."""
    w = h / (m - 0.5)
    cdf = norm.cdf((np.arange(m) + 0.5)[None, :] * w - (np.arange(m) * w)[:, None] + k)
    return float(np.linalg.solve(np.eye(m) - np.diff(cdf, axis=1, prepend=0.0), np.ones(m))[0])


def region(k, n, p, kind, n_cal=None):
    """pipelines.summarize on k alarms out of n: the 99 % binomial region of p and the membership flag."""
    return pl.summarize(pd.DataFrame({"detected": np.arange(n) < k}), p, kind, n_cal)


def edetector_log(x, pipeline, kind):
    """log M of the registry e-detector of a pipeline (P2-C single, P3-C dictionary, P3-CS (b) dictionary at eta0 =
    STAKE_CAP / 2), of type SR or CUSUM, on streams x (..., T) or (..., T, D)."""
    if pipeline == "P2-C":
        return eprocess.log_edetector(x, kind)
    if pipeline == "P3-C":
        return eprocess.log_dictionary_edetector(x, kind)
    return eprocess.log_dictionary_edetector(x, kind, eta0=(pl.STAKE_CAP / 2.0,))


def arl_lengths(log_m, gamma, cap, valid=None):
    """sigma = min(T, cap) with T the first index of log M >= log gamma plus 1 (alarms at or after `valid` ignored), the
    censored flags and M at sigma."""
    log_m = np.atleast_2d(log_m)
    lim = np.broadcast_to(np.minimum(cap, log_m.shape[-1] if valid is None else np.asarray(valid)), log_m.shape[:-1])
    hit = (log_m >= math.log(gamma)) & (np.arange(log_m.shape[-1]) < lim[..., None])
    alarm = hit.any(axis=-1)
    sigma = np.where(alarm, hit.argmax(axis=-1) + 1, lim).astype(np.int64)
    return sigma, ~alarm, np.exp(np.take_along_axis(log_m, (sigma - 1)[..., None], axis=-1)[..., 0])


def arl_read(x, pipeline, gammas, factor, valid=None):
    """(sigma, censored, M_sigma) of both e-detector types at every gamma, cap = factor * gamma, on streams x."""
    out = {}
    for kind in TYPES:
        log_m = edetector_log(x, pipeline, kind)
        for gamma in gammas:
            out[kind, gamma] = arl_lengths(log_m, gamma, int(factor * gamma), valid)
    return out


def classify_arl(sigma, censored, gamma, m_sigma=None, deff=1.0):
    """ARL0 row (D9): restricted mean of min(T, cap), SE = sd / sqrt(n_eff) with n_eff = n / deff (deff = 1 for
    independent replicates), one-sided 99 % lower bound, PASS iff it reaches gamma else INDETERMINATE (never FAIL),
    restricted-mean deficit, and the bounded stopping-time check."""
    s = np.asarray(sigma, dtype=np.float64)
    cz = np.asarray(censored, dtype=bool)
    n, mu = s.size, float(s.mean())
    n_eff = n / deff
    se = float(s.std(ddof=1) / math.sqrt(n_eff)) if n > 1 else math.nan
    lb = mu - Z99_ONE * se
    row = {"n": n, "censored": int(cz.sum()), "censored_share": float(cz.mean()), "restricted_mean": mu, "se": se,
           "deff": deff, "n_eff": n_eff, "lb99": lb, "ratio": mu / gamma,
           "median": float(np.median(s)) if cz.mean() < 0.5 else math.nan, "deficit": gamma - mu,
           "deficit_lo": gamma - (mu + pl.Z99 * se), "deficit_hi": gamma - (mu - pl.Z99 * se),
           "classification": "PASS" if lb >= gamma else "INDETERMINATE"}
    if m_sigma is not None:
        d = np.asarray(m_sigma, dtype=np.float64) - s
        dse = float(d.std(ddof=1) / math.sqrt(n_eff)) if n > 1 else math.nan
        dlb = float(d.mean()) - Z99_ONE * dse
        row.update(ineq_mean=float(d.mean()), ineq_se=dse, ineq_lb99=dlb)
    return row


def familywise_violations(arl, level=0.01):
    """Bounded stopping-time check over the m classified ARL0 rows: a violation of E[M_sigma] <= E[sigma] is certified
    only when the Bonferroni lower bound at family-wise level `level` (union bound, valid under any dependence) is above
    0; the per-row 99 % bound ineq_lb99 stays descriptive (the SR type has E[M_sigma] = E[sigma] exactly)."""
    arl = arl.copy()
    rows = arl["classification"] != "descriptive"
    z = float(norm.ppf(1.0 - level / max(1, int(rows.sum()))))
    arl["ineq_lb_fw"] = np.where(rows, arl["ineq_mean"] - z * arl["ineq_se"], np.nan)
    arl["ineq_violated"] = (arl["ineq_lb_fw"] > 0).where(rows)
    return arl, z


def circular_data(base, s, eps):
    """Unrolled D6 path of len(eps) days from row s: rows (s + t) mod n, one fresh sign per day on the odd part; the path
    is a single record, so detectors and EWMAs continue across the seam."""
    n = len(base["z_odd"]) if isinstance(base, dict) else len(base)
    idx = (s + np.arange(len(eps))) % n
    if isinstance(base, dict):
        return {"z_odd": base["z_odd"][idx] * eps[:, None], "z_even": base["z_even"][idx]}
    return base[idx] * eps[:, None]


def registry_specs(name, H, K, cfg, exact):
    """Registry readings at horizon H: exact P3-C channels (D6, K fixed), P3-C dictionary, P2-C bootstrap (R15 horizon)
    and anytime-valid, P3-CS (a) e-process and randomization, P3-CS (b); K=None keeps the MP edge."""
    alpha, g = cfg["alpha"], pl.horizon_gamma(H, cfg["alpha"])
    kw, k = {"dataset": name, "H": H}, ({} if K is None else {"K": K})
    specs = [pl.make_spec("P3-C", reading="exact", channels=[c], alpha=alpha, **k, **kw)
             for c in range(K + 1)] if exact else []
    specs.append(pl.make_spec("P3-C", gamma=g, **k, **kw))
    if H == cfg["p2c_bootstrap_H"]:
        specs.append(pl.make_spec("P2-C", null_rows="pre_monitor", N_cal=cfg["n_cal"], alpha=alpha, **kw))
    specs += [pl.make_spec("P2-C", reading="anytime-valid", gamma=g, **kw),
              pl.make_spec("P3-CS", variant="a", **k, **kw),
              pl.make_spec("P3-CS", variant="a", reading="randomization", B=cfg["b_flips"], alpha=alpha, **k, **kw),
              pl.make_spec("P3-CS", gamma=g, **k, **kw)]
    return specs


def reading_name(spec):
    """Reading label of a registry spec (P3-CS readings carry their variant)."""
    return f"{spec['reading']}_{spec['variant']}" if spec["pipeline"] == "P3-CS" else spec["reading"]


def d6_group_task(ctx, _):
    """D6 null check of one (dataset, H) group: one fit symmetrization, fresh ones monitored; per-spec summaries."""
    X, _, splits, _ = load_rows(ctx["dataset"])
    specs = registry_specs(ctx["dataset"], ctx["H"], ctx["K"], ctx["cfg"], exact=True)
    rows, summary = pl.null_check(specs, X, splits, ctx["reps"], seed_key(ctx["label"]))
    alarms = rows.groupby("run_id", sort=False)["detected"].sum()
    return [{**rec, "alarms": int(alarms[rec["run_id"]]), "spec": spec}
            for spec, rec in zip(specs, summary.to_dict("records"))]


def p1c_d6_task(ctx, span):
    """D6 replicates r0..r1 of P1-C on the five tickers: uniform start, H fresh daily signs, exact and label arms on the
    same replicates, CUSUM restarted at the window start; alarm counts per ticker and arm."""
    X = load_rows(ctx["dataset"])[0]
    H = ctx["H"]
    exact, label = [], []
    for r in range(*span):
        g = rng(ctx["label"], r)
        s = int(g.integers(0, len(X) - H + 1))
        Y = X[s:s + H][:, ctx["cols"]] * g.choice((-1.0, 1.0), size=H)[:, None]
        exact.append(p1c_stream(Y, coins=rng(ctx["label"], r, 7)))
        label.append(p1c_stream(Y, q_hat=ctx["q_hat"]))
    return {arm: (bilateral_delay_vec(np.swapaxes(np.stack(B), 1, 2), SIGN_DELTA, ctx["threshold"]) >= 0).sum(axis=0)
            for arm, B in (("exact", exact), ("label", label))}


def d5_path(background, d5, T, g):
    """One D5 path of T days: GARCH(alpha, beta), t7 innovations (sim.Garch, reps = 1) or Gaussian (garch_panel)."""
    if background == "t7":
        G = sim.Garch(g, 1, 1, d5["alpha"], d5["beta"], burn=d5["burn"])
        return np.array([G.draw()[0][0] for _ in range(T)])
    return sim.garch_panel(T, 1, d5["alpha"], d5["beta"], None, g, burn=d5["burn"])[:, 0]


def d5_label(background, role):
    """Cell label of the D5 P1 paths of one SeedSequence role: 'cal' fixes the P1-D thresholds, 'eval' is measured."""
    return f"d5|{background}|{role}"


def d5_task(ctx, span):
    """D5 replicates r0..r1: clean days then monitored days; P1-C exact and label alarms at each H (CUSUM from S_0 = 0),
    P1-D constants fitted on the clean days and the monitored energy stream."""
    d5, Hs = ctx["d5"], ctx["H"]
    T0, Hm = d5["T_clean"], max(Hs)
    bits, labels, energy, fits = [], [], [], []
    for r in range(*span):
        y = d5_path(ctx["background"], d5, T0 + Hm, rng(ctx["label"], r))
        clean, mon = y[:T0], y[T0:]
        mu, sigma, gh, conv = p1d_fit(clean)
        bits.append(p1c_stream(mon, coins=rng(ctx["label"], r, 7)))
        labels.append(p1c_stream(mon, q_hat=float(np.mean(clean > 0))))
        energy.append(energy_stream(mon, mu, sigma))
        fits.append((mu, sigma, gh, float(conv)))
    det = {(arm, H): bilateral_delay_vec(np.stack(B)[:, :H], SIGN_DELTA, ctx["thresholds"][H]) >= 0
           for arm, B in (("exact", bits), ("label", labels)) for H in Hs}
    return {"det": det, "energy": np.stack(energy), "fits": np.array(fits, dtype=np.float64)}


def p1d_real_task(ctx, _):
    """P1-D on one real ticker (descriptive): constants on the calib rows, every H-day window from S_0 = 0, lambda_req on
    the windows (in sample), lambda_iid on i.i.d. bootstrap paths of the standardized energies."""
    X, _, splits, assets = load_rows(ctx["dataset"])
    (a, b), alpha = splits["calib"], ctx["alpha"]
    r = X[:, ctx["col"]]
    mu, sigma, gh, conv = p1d_fit(r[a:b])
    e = energy_stream(r, mu, sigma)
    rows = []
    for H in ctx["H"]:
        n_w, n_d, share = window_counts(len(e), H, (a, b))
        peaks = window_peaks(e, np.arange(n_w), H, ENERGY_DELTA)
        iid = e[rng(ctx["label"], H, CELL_SEED).integers(0, len(e), size=(ctx["n_iid"], H))]
        lam_iid = fpr_threshold(cusum_trajectory_vec(iid, ENERGY_DELTA).max(axis=-1), alpha)
        lam_req = fpr_threshold(peaks, alpha)
        gs = gamma_spectral(np.lib.stride_tricks.sliding_window_view(e, H))
        for reading, thr in (("rule_iid_x_gamma_hat", lam_iid * gh), ("iid", lam_iid),
                             ("r01_65_x_gamma_hat", LAMBDA_R01 * gh)):
            k = int((peaks > thr).sum())
            rows.append({"block": "real_even", "background": "real", "dataset": ctx["dataset"], "pipeline": "P1-D",
                         "reading": reading, "arm": "energy", "unit": assets[ctx["col"]], "H": H, "threshold": thr,
                         "n": n_w, "alarms": k, "fpr": k / n_w, "ci_kind": "na", "target": alpha, "target_kind": "~",
                         "validity": "descriptive", "n_windows": n_w, "n_disjoint": n_d, "in_sample_share": share,
                         "null_rows": "pre_monitor", "lam_iid": lam_iid, "lam_req": lam_req,
                         "gamma_op": lam_req / lam_iid, "gamma_spec": float(np.median(gs)),
                         "gamma_spec_q1": float(np.quantile(gs, 0.25)), "gamma_spec_q3": float(np.quantile(gs, 0.75)),
                         "gamma_hat": gh, "converged_share": float(conv)})
    return rows


def p3d_task(ctx, _):
    """P3-D (factor, descriptive): registry fit for (H, null_rows), its thresholds applied to every pre-monitor window of
    length H from S_0 = 0, and the segment means of the residual energy."""
    X, _, splits, _ = load_rows(ctx["dataset"])
    H, nr = ctx["H"], ctx["null_rows"]
    spec = pl.make_spec("P3-D", H=H, null_rows=nr, N_cal=ctx["n_iid"], dataset=ctx["dataset"])
    state = pl.fit_pipeline(spec, X, splits, key=seed_key(ctx["label"]))
    q = pl.residual_energy(state["rep"].transform_panel(X)["z_even"], state["channels"]["residual"])
    n_w, n_d, share = window_counts(len(q), H, splits["calib"])
    peaks = window_peaks(q, np.arange(n_w), H, ENERGY_DELTA)
    (p0, p1), (a, b) = splits["pretrain"], splits["calib"]
    rows = []
    for reading, thr in (("lam_req", state["threshold"]), ("iid", state["lam_iid"])):
        k = int((peaks > thr).sum())
        rows.append({"block": "real_even", "background": "real", "dataset": ctx["dataset"], "pipeline": "P3-D",
                     "reading": reading, "arm": "energy", "unit": "residual", "H": H, "threshold": thr, "n": n_w,
                     "alarms": k, "fpr": k / n_w, "ci_kind": "na", "target": spec["alpha"], "target_kind": "~",
                     "validity": "descriptive", "n_windows": n_w, "n_disjoint": n_d, "in_sample_share": share,
                     "null_rows": nr, "lam_iid": state["lam_iid"], "lam_req": state["threshold"],
                     "gamma_op": state["gamma_op"], "gamma_spec": state["gamma_spec"],
                     "q_mean_pretrain": float(q[p0:p1].mean()), "q_mean_calib": float(q[a:b].mean())})
    return rows


def raw_units_task(ctx, _):
    """Raw placebo of the exact (1/2) and recentred (calib q_hat, Article B rule) arms of each P3-C channel and P1-C
    ticker over the H-day windows (retrospective, descriptive), CUSUM restarted at each window start."""
    name, H, thr = ctx["dataset"], ctx["H"], ctx["threshold"]
    X, _, splits, assets = load_rows(name)
    _, Z = raw_basis(name)
    a, b = splits["calib"]
    n_w, n_d, share = window_counts(len(X), H, (a, b))
    starts = np.arange(0, n_w, ctx["stride"])
    units = [("P3-C", f"ch{k}", f"PC{k + 1}", Z["z_odd"][:, k]) for k in range(Z["z_odd"].shape[1])]
    units += [("P1-C", assets[c], "", X[:, c]) for c in ctx["cols"]]
    rows = []
    for j, (pipeline, unit, direction, y) in enumerate(units):
        q = float(np.mean(y[a:b] > 0))
        for arm, x in (("exact", p1c_stream(y, coins=rng(ctx["label"], j, 7))), ("recentred", p1c_stream(y, q_hat=q))):
            k = int((window_offsets(x, starts, H, SIGN_DELTA, thr) >= 0).sum())
            rows.append({"dataset": name, "pipeline": pipeline, "reading": "exact_lattice", "arm": arm, "unit": unit,
                         "direction": direction, "H": H, "threshold": thr, "n_windows": int(starts.size),
                         "n_disjoint": n_d, "stride": ctx["stride"], "in_sample_share": share, "alarms": k,
                         "rate": k / starts.size, "target": ctx["level"], "target_kind": "=",
                         "gap": k / starts.size - ctx["level"], "q_hat_calib": q, "q_mean": float(np.mean(y > 0)),
                         "zero_share": float(np.mean(y == 0)), "design": "retrospective_descriptive"})
    return rows


def raw_registry_task(ctx, _):
    """One registry reading on the raw H-day windows (retrospective, descriptive): fit on the raw rows, run_pipeline from
    each window start."""
    name, H = ctx["dataset"], ctx["H"]
    X, _, splits, _ = load_rows(name)
    spec = registry_specs(name, H, None, ctx["cfg"], exact=False)[ctx["index"]]
    state = pl.fit_pipeline(spec, X, splits, key=seed_key(ctx["label"]))
    data = X if state["rep"] is None else state["rep"].transform_panel(X)
    pre = spec["H_ref"] if spec["pipeline"] == "P2-C" and spec["reading"] == "bootstrap" else 0
    starts = np.arange(pre, len(X) - H + 1, ctx["stride"])
    recs = [{"seed": seed_key(ctx["label"], int(s)), "tau_star": int(s), "family": "H0"} for s in starts]
    det = pl.run_pipeline(spec, data, splits, recs, state)["detected"].to_numpy()
    p, kind, _ = pl.null_target(spec, state)
    k = int(det.sum())
    return {"dataset": name, "pipeline": spec["pipeline"], "reading": reading_name(spec), "arm": "half",
            "unit": "pooled" if spec["pipeline"] == "P2-C" else "dictionary", "direction": "", "H": H,
            "threshold": float(state["threshold"]), "n_windows": int(starts.size), "n_disjoint": len(X) // (pre + H),
            "stride": ctx["stride"], "in_sample_share": window_counts(len(X) - pre, H, splits["calib"])[2],
            "alarms": k, "rate": k / starts.size, "target": p, "target_kind": kind, "gap": k / starts.size - p,
            "design": "retrospective_descriptive"}


def arl_coins_task(ctx, span):
    """Fair-coin replicates r0..r1 of one e-detector structure: one path of T steps per replicate, read at every gamma
    with cap 60 gamma, for both types; P3-CS (b) has constant stakes 2 eta0_j (sigma_hat = sigma_bar)."""
    pipeline, D, T = ctx["pipeline"], ctx["D"], ctx["T"]
    lam = np.minimum(pl.STAKE_CAP, 2.0 * np.asarray(eprocess.EDETECTOR_ETA0))
    xs = []
    for r in range(*span):
        c = rng(ctx["label"], r).choice((-1.0, 1.0), size=(T, D))
        xs.append(c[:, 0] if pipeline == "P2-C" else c if pipeline == "P3-C" else
                  (2.0 * lam[None, None, :] * c[:, :, None]).reshape(T, -1))
    return arl_read(np.stack(xs), pipeline, ctx["gammas"], ctx["factor"])


@functools.lru_cache(maxsize=None)
def arl_state(name, pipeline, K, T, label, symmetrized):
    """Registry state of a pipeline at horizon T, fitted on one symmetrization of the rows (K fixed) or on the raw rows
    (K at the MP edge), and the base it monitors."""
    X, _, splits, _ = load_rows(name)
    kw = {} if pipeline == "P2-C" or K is None else {"K": K}
    spec = pl.make_spec(pipeline, reading="anytime-valid", H=T, dataset=name, **kw)
    X_fit = symmetrize(X, rng(label, CELL_SEED))[0] if symmetrized else X
    state = pl.fit_pipeline(spec, X_fit, splits, key=seed_key(label))
    return spec, state, (X if state["rep"] is None else state["rep"].transform_panel(X))


def arl_d6_task(ctx, span):
    """Circular D6 replicates r0..r1: start s ~ U[0, n), rows (s + t) mod n, fresh daily signs, one unrolled record per
    replicate through the registry stream builder, so that the detector and the EWMA continue at the seam."""
    spec, state, base = arl_state(ctx["dataset"], ctx["pipeline"], ctx["K"], ctx["T"], ctx["label"], True)
    n = len(base["z_odd"]) if isinstance(base, dict) else len(base)
    build = pl.PIPELINES[ctx["pipeline"]][1]
    xs = []
    for r in range(*span):
        g = rng(ctx["label"], r)
        s = int(g.integers(0, n))
        data = circular_data(base, s, g.choice((-1.0, 1.0), size=ctx["T"]))
        xs.append(build(spec, state, data, {"seed": seed_key(ctx["label"], r), "tau_star": 0, "family": "H0"}))
    return arl_read(np.stack(xs), ctx["pipeline"], ctx["gammas"], ctx["factor"])


def arl_raw_task(ctx, starts):
    """Raw starts (descriptive): the registry stream from each start to the end of the rows (P3-CS (b) restarts its EWMA
    there), zero padding whose alarms are ignored, sigma capped at min(60 gamma, n - s)."""
    name, pipeline = ctx["dataset"], ctx["pipeline"]
    n = len(load_rows(name)[0])
    spec, state, data = arl_state(name, pipeline, None, n, ctx["label"], False)
    build = pl.PIPELINES[pipeline][1]
    full = None if pipeline == "P3-CS" else build(spec, state, data, {"seed": seed_key(ctx["label"], 0),
                                                                       "tau_star": 0, "family": "H0"})
    xs = []
    for s in starts:
        if full is None:
            sub = pl.make_spec(pipeline, reading="anytime-valid", H=n - s, dataset=name)
            x = build(sub, state, data, {"seed": seed_key(ctx["label"], int(s)), "tau_star": int(s), "family": "H0"})
        else:
            x = full[s:]
        pad = np.zeros((n,) + x.shape[1:])
        pad[:n - s] = x
        xs.append(pad)
    return arl_read(np.stack(xs), pipeline, ctx["gammas"], ctx["factor"], valid=n - np.asarray(starts))


def overshoot_path(ctx, r):
    """Overshoot path r: i.i.d. N(0, 1) or Gaussian GARCH(alpha, beta) of unit unconditional variance (sigma_inc = 1)."""
    g = rng(ctx["label"], r)
    if ctx["background"] == "iid":
        return g.standard_normal(ctx["T_max"])
    d5 = ctx["d5"]
    return sim.garch_panel(ctx["T_max"], 1, d5["alpha"], d5["beta"], None, g, burn=d5["burn"])[:, 0]


def overshoot_task(ctx, span):
    """Overshoot replicates r0..r1: one path per replicate shared by the first-order CUSUMs on x / sigma_inc and the sign
    CUSUM, each restarted at S_0 = 0; run lengths, censored flags and Gamma^spec of x."""
    P = np.stack([overshoot_path(ctx, r) for r in range(*span)])
    out = {"gamma_spec": gamma_spectral(P[:, :ctx["spec_days"]])}
    for row in ctx["rows"]:
        x = P if row["kind"] == "first_order" else np.stack(
            [p1c_stream(p, coins=rng(ctx["label"], r, 7)) for p, r in zip(P, range(*span))])
        out[row["name"]] = run_lengths(x, row["delta"], row["threshold"], ctx["T_max"])
    return out


def overshoot_lam_task(ctx, _):
    """lambda_req of the first-order CUSUMs on the primary GARCH paths at the exact i.i.d. ARL0 (required_threshold,
    criterion arl0; an upper bound when paths are censored)."""
    P = np.stack([overshoot_path(ctx, r) for r in range(ctx["n_primary"])])
    return {row["name"]: required_threshold(P, row["delta"], ctx["targets"][row["name"]], "arl0")
            for row in ctx["rows"] if row["kind"] == "first_order"}


@functools.lru_cache(maxsize=None)
def market_channel(name):
    """Market channel u'x (column 0 of z_odd, PC1) of the raw calib basis over all rows."""
    return raw_basis(name)[1]["z_odd"][:, 0].copy()


def encoder_task(ctx, span):
    """Encoder replicates r0..r1: one base path of L_max - 1 + H_max days (i.i.d. N(0, 1), or the D6 market channel from
    a uniform start with fresh daily signs), z for every L over the same monitored days, CUSUMs from S_0 = 0."""
    Ls, Hs = ctx["L"], ctx["H"]
    Lm, Hm = max(Ls), max(Hs)
    Y = []
    for r in range(*span):
        g = rng(ctx["label"], r)
        if ctx["background"] == "d5":
            Y.append(g.standard_normal(Lm - 1 + Hm))
        else:
            u = market_channel(ctx["dataset"])
            s = int(g.integers(Lm - 1, len(u) - Hm + 1))
            Y.append(u[s - Lm + 1:s + Hm] * g.choice((-1.0, 1.0), size=Lm - 1 + Hm))
    Y = np.stack(Y)
    out = {}
    for L in Ls:
        Z = encoder(Y, L)[:, Lm - L:Lm - L + Hm]
        bits = np.stack([p1c_stream(z, coins=rng(ctx["label"], r, L, 7)) for z, r in zip(Z, range(*span))])
        for H in Hs:
            z = Z[:, :H]
            out[L, H] = {"peak": cusum_trajectory_vec(z / ctx["sd"][L], ctx["delta"]).max(axis=-1),
                         "sign": bilateral_delay_vec(bits[:, :H], SIGN_DELTA, ctx["thresholds"][H]) >= 0,
                         "lb_p": np.array([acorr_ljungbox(np.sign(v), lags=[ctx["lb_lags"]])["lb_pvalue"].iloc[0]
                                           for v in z]),
                         "g_default": gamma_spectral(z),
                         "g_wide": gamma_spectral(z, L=min(ctx["wide_factor"] * L, H - 1))}
    return out


WORKERS = {"d6_group": d6_group_task, "p1c_d6": p1c_d6_task, "d5": d5_task, "p1d_real": p1d_real_task,
           "p3d": p3d_task, "raw_units": raw_units_task, "raw_registry": raw_registry_task,
           "arl_coins": arl_coins_task, "arl_d6": arl_d6_task, "arl_raw": arl_raw_task, "overshoot": overshoot_task,
           "overshoot_lam": overshoot_lam_task, "encoder": encoder_task}


def run_task(task):
    """Dispatch one task (kind, context, argument) to its worker; returns its result and its CPU seconds."""
    kind, ctx, arg = task
    t0 = time.process_time()
    out = WORKERS[kind](ctx, arg)
    return out, time.process_time() - t0


def run_tasks(tasks, jobs):
    """Run tasks in submission order, on a spawn-context process pool when jobs > 1; results do not depend on jobs."""
    if jobs > 1 and len(tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
            return list(pool.map(run_task, tasks))
    return [run_task(t) for t in tasks]


def registry_cell(rec):
    """Cells row of one D6 registry reading from its null_check summary (Wilson conditional on the panel)."""
    spec = rec["spec"]
    lo, hi = wilson(rec["alarms"], rec["n"])
    kind = rec["kind"]
    validity = {"=": "exact", "<=": "bound"}.get(kind, "calibrated_conditional" if spec["pipeline"] == "P2-C"
                                                 else "calibrated")
    unit = f"ch{spec['channels'][0]}" if spec["reading"] == "exact" else (
        "pooled" if spec["pipeline"] == "P2-C" else "dictionary")
    return {"block": "d6_registry", "background": "d6", "dataset": spec["dataset"], "pipeline": spec["pipeline"],
            "reading": reading_name(spec), "arm": "half", "unit": unit, "H": spec["H"], "gamma": spec["gamma"],
            "threshold": rec["threshold"], "n": rec["n"], "alarms": rec["alarms"], "fpr": rec["fpr"], "fpr_lo": lo,
            "fpr_hi": hi, "ci_kind": "wilson_conditional", "deff": 1.0, "n_eff": float(rec["n"]),
            "target": rec["target"], "target_kind": kind, "n_cal": rec["n_cal"], "region_lo": rec["lo"],
            "region_hi": rec["hi"], "in_region": bool(rec["ok"]), "validity": validity,
            "null_rows": spec.get("null_rows", "pre_monitor")}


def sign_cells(block, background, dataset, unit, H, threshold, level, counts, n, ci_kind, q_hat=math.nan):
    """Cells rows of the exact and label arms of one P1-C unit: exact = lattice level, label = reference only."""
    rows = []
    for arm in ("exact", "label"):
        k = int(counts[arm])
        lo, hi = wilson(k, n)
        reg = region(k, n, level, "=")
        exact = arm == "exact"
        rows.append({"block": block, "background": background, "dataset": dataset, "pipeline": "P1-C",
                     "reading": "exact", "arm": arm, "unit": unit, "H": H, "threshold": threshold, "n": n,
                     "alarms": k, "fpr": k / n, "fpr_lo": lo, "fpr_hi": hi, "ci_kind": ci_kind, "deff": 1.0,
                     "n_eff": float(n), "target": level, "target_kind": "=" if exact else "ref",
                     "region_lo": reg["lo"], "region_hi": reg["hi"], "in_region": bool(reg["ok"]) if exact else math.nan,
                     "validity": "exact" if exact else "reference_only", "q_hat": math.nan if exact else q_hat})
    return rows


def d5_cells(background, cal, ev, cfg, sels, label):
    """Cells rows of one D5 background: P1-C arms on the evaluation paths; P1-D lambda_req and lambda_iid (global
    permutation) calibrated on the calibration paths `cal`, their FPR and Wilson intervals measured on the independent
    evaluation paths `ev` (distinct SeedSequence roles), with Gamma^op, Gamma^spec and Gamma_hat."""
    alpha = cfg["alpha"]
    det = {k: np.concatenate([p["det"][k] for p in ev]) for k in ev[0]["det"]}
    E_cal = np.concatenate([p["energy"] for p in cal])
    E = np.concatenate([p["energy"] for p in ev])
    fits = np.concatenate([p["fits"] for p in ev])
    gh, conv = fits[:, 2], fits[:, 3]
    perm = rng(label, CELL_SEED).permutation(E_cal.ravel()).reshape(E_cal.shape)
    g_exact = float(compute_gamma_exact(cfg["d5"]["alpha"], cfg["d5"]["beta"]))
    rows = []
    for H in sorted(sels):
        counts = {arm: int(det[arm, H].sum()) for arm in ("exact", "label")}
        rows += sign_cells("d5", f"d5_{background}", "d5", "path", H, sels[H]["threshold"], sels[H]["level"], counts,
                           len(E), "wilson")
        lam_req = fpr_threshold(cusum_trajectory_vec(E_cal[:, :H], ENERGY_DELTA).max(axis=-1), alpha)
        lam_iid = fpr_threshold(cusum_trajectory_vec(perm[:, :H], ENERGY_DELTA).max(axis=-1), alpha)
        peaks = cusum_trajectory_vec(E[:, :H], ENERGY_DELTA).max(axis=-1)
        gs = gamma_spectral(E_cal[:, :H])
        for reading, thr in (("lam_req", np.full(len(E), lam_req)), ("rule_iid_x_gamma_hat", lam_iid * gh),
                             ("iid", np.full(len(E), lam_iid)), ("r01_65_x_gamma_hat", LAMBDA_R01 * gh)):
            k = int((peaks > thr).sum())
            lo, hi = wilson(k, len(E))
            rows.append({"block": "d5", "background": f"d5_{background}", "dataset": "d5", "pipeline": "P1-D",
                         "reading": reading, "arm": "energy", "unit": "path", "H": H,
                         "threshold": float(np.median(thr)), "n": len(E), "alarms": k, "fpr": k / len(E),
                         "fpr_lo": lo, "fpr_hi": hi, "ci_kind": "wilson", "deff": 1.0, "n_eff": float(len(E)),
                         "target": alpha, "target_kind": "~", "n_cal": len(E_cal), "n_eval": len(E),
                         "validity": "out_of_sample", "lam_iid": lam_iid,
                         "lam_req": lam_req, "gamma_op": lam_req / lam_iid, "gamma_spec": float(np.median(gs)),
                         "gamma_spec_q1": float(np.quantile(gs, 0.25)), "gamma_spec_q3": float(np.quantile(gs, 0.75)),
                         "gamma_hat": float(np.median(gh)), "gamma_exact": g_exact,
                         "converged_share": float(conv.mean())})
    return rows


def arl_rows(info, parts, gammas, factor, descriptive):
    """ARL0 rows of one (background, structure): classification D9 on coins and D6, descriptive on raw starts."""
    rows = []
    for kind in TYPES:
        for gamma in gammas:
            sigma, cz, m = (np.concatenate([p[kind, gamma][i] for p in parts]) for i in range(3))
            if descriptive:
                row = {"n": sigma.size, "censored": int(cz.sum()), "censored_share": float(cz.mean()),
                       "restricted_mean": float(sigma.mean()), "ratio": float(sigma.mean()) / gamma,
                       "median": float(np.median(sigma)) if cz.mean() < 0.5 else math.nan,
                       "classification": "descriptive"}
            else:
                row = classify_arl(sigma, cz, gamma, m)
            rows.append({**info, "type": kind, "gamma": gamma, "cap": int(factor * gamma), **row})
    return rows


def overshoot_rows(background, parts, ctx, cfg, exact, lam_req, quick=False):
    """Overshoot rows of one background: the D8 gate on replicates 0..n_primary - 1 of the full run (censored cells
    INDETERMINATE unless the restricted mean already exceeds the band), the diagnostic on all replicates; under --quick
    the first rows are a quick_diagnostic without gate. SE = sd / sqrt(n_eff), n_eff = n / deff, deff = 1 (independent
    replicates)."""
    tol, n_primary, deff = cfg["overshoot"]["tolerance"], ctx["n_primary"], 1.0
    gs = float(np.median(np.concatenate([p["gamma_spec"] for p in parts])))
    rows = []
    for row in ctx["rows"]:
        rl, cz = (np.concatenate([p[row["name"]][i] for p in parts]) for i in range(2))
        ref = float(row["ref"][background])
        for role, m in (("quick_diagnostic" if quick else "primary", n_primary), ("diagnostic", len(rl))):
            x, c = rl[:m].astype(np.float64), cz[:m]
            n_eff = m / deff
            arl, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(n_eff))
            gap = arl / ref - 1.0
            if role != "primary":
                gate = "na"
            elif c.sum() == 0:
                gate = "PASS" if abs(gap) <= tol else "FAIL"
            else:
                gate = "FAIL" if gap > tol else "INDETERMINATE"
            lam = lam_req.get(row["name"], math.nan)
            rows.append({"background": background, "statistic": row["name"], "delta": row["delta"],
                         "threshold": row["threshold"], "role": role, "n": m, "censored": int(c.sum()), "arl0": arl,
                         "se": se, "deff": deff, "n_eff": n_eff, "arl0_lo": arl - Z95 * se,
                         "arl0_hi": arl + Z95 * se, "reference": ref,
                         "rel_gap": gap, "gate": gate, "arl0_exact": exact.get((background, row["name"]), math.nan),
                         "gamma_spec": gs, "lam_req": lam, "gamma_op": lam / row["threshold"]})
    return rows


def encoder_rows(background, dataset, parts, ctx, lam_iid, levels, alpha_lb, n_cal):
    """Encoder rows of one background: Gamma_z^spec (default and wide bandwidth), lambda_iid (n_cal independent i.i.d.
    paths) against lambda_req, FPR of the i.i.d.-calibrated CUSUM and of the lattice sign CUSUM, Ljung-Box rejection of
    the signs; Wilson intervals on independent replicates (conditional on the panel for D6), deff = 1."""
    rows = []
    for L in ctx["L"]:
        for H in ctx["H"]:
            v = {k: np.concatenate([p[L, H][k] for p in parts]) for k in parts[0][L, H]}
            n = v["peak"].size
            lam_req = fpr_threshold(v["peak"], ctx["alpha"])
            k_c, k_s = int((v["peak"] > lam_iid[H]).sum()), int(v["sign"].sum())
            finite = np.isfinite(v["lb_p"])
            k_lb = int((v["lb_p"][finite] < alpha_lb).sum())
            (c_lo, c_hi), (s_lo, s_hi) = wilson(k_c, n), wilson(k_s, n)
            lb_lo, lb_hi = wilson(k_lb, int(finite.sum())) if finite.any() else (math.nan, math.nan)
            rows.append({"background": background, "dataset": dataset, "L": L, "H": H, "n": n,
                         "ci_kind": "wilson" if background == "d5" else "wilson_conditional", "deff": 1.0,
                         "n_eff": float(n), "n_cal": n_cal,
                         "gamma_spec": float(np.median(v["g_default"])), "gamma_spec_wide": float(np.median(v["g_wide"])),
                         "bandwidth_wide": min(ctx["wide_factor"] * L, H - 1),
                         "gamma_analytic": float(L) if background == "d5" else math.nan, "sd": ctx["sd"][L],
                         "lam_iid": lam_iid[H], "lam_req": lam_req, "gamma_op": lam_req / lam_iid[H],
                         "fpr_cusum": k_c / n, "fpr_cusum_lo": c_lo, "fpr_cusum_hi": c_hi, "fpr_sign": k_s / n,
                         "fpr_sign_lo": s_lo, "fpr_sign_hi": s_hi, "level_sign": levels[H],
                         "lb_reject": k_lb / max(1, int(finite.sum())), "lb_reject_lo": lb_lo, "lb_reject_hi": lb_hi,
                         "lb_median_p": float(np.median(v["lb_p"][finite])) if finite.any() else math.nan,
                         "lb_nan": int((~finite).sum())})
    return rows


def join_audit(rows):
    """Attach the audit's symmetry tests (results/audit/symmetry_tests.csv) to the raw P3-C rows by (dataset, PC)."""
    audit = pd.read_csv(AUDIT, float_precision="round_trip").set_index(["dataset", "direction"])
    for row in rows:
        key = (row["dataset"], row.get("direction", ""))
        if key in audit.index:
            a = audit.loc[key]
            row.update(audit_q_hat=float(a["q_hat"]), binom_p_holm=float(a["binom_p_holm"]),
                       triples_p_holm=float(a["triples_p_holm"]), binom_reject=bool(a["binom_reject"]),
                       triples_reject=bool(a["triples_reject"]))
    return rows


def j2_lines(cells, quick):
    """Secondary calibration check of prompt 13 item 7 on the exact sign streams of D6: gap to the lattice level, the
    1-point rule and the 99 % region per cell, descriptive counts; no J2 verdict (the primary J2 (i) verdict is E1's)."""
    ex = cells[(cells["background"] == "d6") & (cells["validity"] == "exact")]
    lines = [f"sizes: {'quick' if quick else 'full'}",
             "secondary calibration check (prompt 13 item 7), not a J2 verdict: the primary J2 (i) verdict is E1 "
             "(stream 12) at 2,000 replicates",
             "exact sign streams on D6, |FPR - lattice level| <= 0.01 per cell; region = pipelines.summarize 99 %"]
    exits, expect, union, fails = 0, 0.0, 0.0, 0
    for r in ex.itertuples(index=False):
        n, gap = int(r.n), abs(r.fpr - r.target)
        ok = gap <= 0.01
        fails += not ok
        exits += not bool(r.in_region)
        k = np.arange(n + 1)
        pmf = binom.pmf(k, n, r.target)
        expect += float(pmf[(k / n < r.region_lo) | (k / n > r.region_hi)].sum())
        union += float(pmf[np.abs(k / n - r.target) > 0.01].sum())
        lines.append(f"{r.dataset} H={int(r.H)} {r.pipeline} {r.unit}: n={n} fpr={r.fpr:.5f} level={r.target:.6f} "
                     f"|gap|={gap:.5f} within_1pt={'yes' if ok else 'no'} "
                     f"region99={'in' if bool(r.in_region) else 'OUT'}")
    m = len(ex)
    lines += [f"cells within 0.01: {m - fails} of {m} (descriptive count)",
              f"region exits: {exits} of {m} (descriptive count: the cells share symmetrizations, panels and "
              f"replicates; no binomial law, no p-value, no joint probability under independence)",
              f"sum of the marginal exit probabilities under exactness (expectation by linearity, valid under any "
              f"dependence): {expect:.3f}",
              f"union bound on at least one cell beyond 0.01 under exactness (valid under any dependence): {union:.1e}"]
    return lines


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _save(plt, fig, fig_dir, stem):
    fig.tight_layout()
    fig.savefig(fig_dir / f"{stem}.png", dpi=200)
    fig.savefig(fig_dir / f"{stem}.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def _style(ax, title):
    ax.set_title(title, color=INK)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def plot(out, fig_dir):
    """fpr_cells, arl0, raw_placebo and gamma figures, drawn from the CSVs only."""
    import matplotlib.pyplot as plt

    def read(name):
        return pd.read_csv(out / name, float_precision="round_trip")

    cells, arl, raw = read("e3_cells.csv"), read("e3_arl0.csv"), read("e3_raw_placebo.csv")
    over, enc = read("e3_overshoot.csv"), read("e3_window_encoders.csv")
    fig_dir.mkdir(parents=True, exist_ok=True)
    saved = plt.rcParams.copy()
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE})
    try:
        Hs = sorted(cells["H"].dropna().unique())
        ex = cells[cells["validity"] == "exact"].copy()
        ex["group"] = np.where(ex["background"] == "d6", "D6 " + ex["dataset"].astype(str), "D5")
        groups = ["D5"] + sorted(g for g in ex["group"].unique() if g != "D5")
        fig, axes = plt.subplots(1, len(Hs), figsize=(4.8 * len(Hs), 3.6), squeeze=False)
        for ax, H in zip(axes[0], Hs):
            d = ex[ex["H"] == H].reset_index(drop=True)
            if len(d):
                ax.axhspan(d["region_lo"].median(), d["region_hi"].median(), color=GRID, lw=0)
                ax.axhline(d["target"].iloc[0], color=MUTED, lw=1, ls="--")
            for j, grp in enumerate(groups):
                s = d[d["group"] == grp]
                err = np.clip(np.vstack([s["fpr"] - s["fpr_lo"], s["fpr_hi"] - s["fpr"]]), 0.0, None)
                ax.errorbar(s.index, s["fpr"], yerr=err, fmt="o", ms=4, color=SERIES[j % 3], elinewidth=1,
                            capsize=0, label=grp)
            ax.set_xticks(d.index, d["unit"].astype(str) + " " + d["background"].str.replace("d5_", ""),
                          rotation=90, fontsize=5)
            ax.set_ylabel("FPR(H) under H0")
            _style(ax, f"exact sign streams, H = {int(H)} (band: 99 % region)")
            ax.legend(frameon=False)
        _save(plt, fig, fig_dir, "fpr_cells")

        bgs = ["coins", "d6", "raw"]
        arl = arl.assign(label=arl["pipeline"] + np.where(arl["dataset"].fillna("") != "", " " + arl["dataset"].fillna(""),
                                                          " D=" + arl["columns"].astype(int).astype(str)))
        fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.8), sharey=True)
        for ax, kind in zip(axes, TYPES):
            d = arl[arl["type"] == kind].reset_index(drop=True)
            labels = list(dict.fromkeys(d["label"] + " g" + d["gamma"].astype(int).astype(str)))
            pos = {lab: i for i, lab in enumerate(labels)}
            for j, bg in enumerate(bgs):
                s = d[d["background"] == bg]
                x = [pos[lab] for lab in s["label"] + " g" + s["gamma"].astype(int).astype(str)]
                passed = s["classification"] == "PASS"
                ax.scatter(np.asarray(x)[passed.to_numpy()], s["ratio"][passed], s=16, color=SERIES[j], label=f"{bg}")
                ax.scatter(np.asarray(x)[~passed.to_numpy()], s["ratio"][~passed], s=16, facecolors="none",
                           edgecolors=SERIES[j], label=f"{bg}, not PASS")
            ax.axhline(1.0, color=MUTED, lw=1, ls="--")
            ax.set_yscale("log")
            ax.set_xticks(range(len(labels)), labels, rotation=90, fontsize=5)
            ax.set_ylabel("restricted mean of min(T, 60 gamma) / gamma")
            _style(ax, f"e-detector ARL0, {kind} type (open: not PASS)")
            ax.legend(frameon=False, fontsize=6)
        _save(plt, fig, fig_dir, "arl0")

        panels = list(raw[["dataset", "H"]].drop_duplicates().itertuples(index=False))
        fig, axes = plt.subplots(1, len(panels), figsize=(4.2 * len(panels), 3.6), squeeze=False)
        units = raw[raw["reading"] == "exact_lattice"]
        for ax, (name, H) in zip(axes[0], panels):
            d = units[(units["dataset"] == name) & (units["H"] == H)]
            names = list(dict.fromkeys(d["unit"]))
            for j, arm in enumerate(("exact", "recentred")):
                s = d[d["arm"] == arm].set_index("unit").reindex(names)
                rej = (s["binom_reject"].astype(str) == "True") | (s["triples_reject"].astype(str) == "True")
                x = np.arange(len(names)) + (j - 0.5) * 0.3
                ax.scatter(x[rej.to_numpy()], s["rate"][rej], s=16, color=SERIES[j], label=f"{arm}, symmetry rejected")
                ax.scatter(x[~rej.to_numpy()], s["rate"][~rej], s=16, facecolors="none", edgecolors=SERIES[j],
                           label=f"{arm}")
            if len(d):
                ax.axhline(d["target"].iloc[0], color=MUTED, lw=1, ls="--")
            ax.set_xticks(range(len(names)), names, rotation=90, fontsize=6)
            ax.set_ylabel("raw window FPR (descriptive)")
            _style(ax, f"raw placebo {name}, H = {int(H)}")
            ax.legend(frameon=False, fontsize=6)
        _save(plt, fig, fig_dir, "raw_placebo")

        sets = [("P1-D", cells[(cells["pipeline"] == "P1-D") & (cells["reading"] == "iid")], "background", "dataset"),
                ("P3-D", cells[(cells["pipeline"] == "P3-D") & (cells["reading"] == "iid")], "dataset", None),
                ("window encoders", enc.assign(background=enc["background"]), "background", None),
                ("overshoot (GARCH, ARL0 criterion)", over[(over["role"] != "diagnostic") & over["gamma_op"].notna()],
                 "background", None)]
        fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.4))
        for ax, (title, d, col, alt) in zip(axes, sets):
            keys = list(dict.fromkeys(d[col].astype(str)))
            for j, key in enumerate(keys[:3]):
                s = d[d[col].astype(str) == key]
                ax.scatter(s["gamma_spec"], s["gamma_op"], s=16, color=SERIES[j], label=key)
            lim = [0.5, max(2.0, float(np.nanmax(np.r_[d["gamma_spec"], d["gamma_op"]])) * 1.5) if len(d) else 2.0]
            ax.plot(lim, lim, color=MUTED, lw=1, ls="--")
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("Gamma^spec (Bartlett, default bandwidth)")
            ax.set_ylabel("Gamma^op = lambda_req / lambda_iid")
            _style(ax, title)
            if keys:
                ax.legend(frameon=False, fontsize=6)
        _save(plt, fig, fig_dir, "gamma")
    finally:
        plt.rcParams.update(saved)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--quick", action="store_true", help="the config's quick sizes: not a J2 verdict")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "e3")
    ap.add_argument("--fig-dir", type=Path, help="default figures/<name of --out>")
    ap.add_argument("--log-dir", type=Path, help="default logs/<name of --out>")
    ap.add_argument("--jobs", type=int, default=24)
    args = ap.parse_args(argv)
    if args.jobs < 1:
        ap.error("--jobs must be >= 1")
    t0 = time.time()
    cfg = yaml.safe_load(args.config.read_text())
    if args.quick:
        cfg["reps"].update(cfg["quick"]["reps"])
        cfg.update({k: v for k, v in cfg["quick"].items() if k != "reps"})
    fig_dir = args.fig_dir or REPO_ROOT / "figures" / args.out.name
    log_dir = args.log_dir or REPO_ROOT / "logs" / args.out.name
    alpha, Hs, names, reps = cfg["alpha"], sorted(int(h) for h in cfg["H"]), cfg["datasets"], cfg["reps"]
    sels = {H: lattice.select_threshold(alpha, H=H, delta=SIGN_DELTA, sided=2) for H in Hs}
    thresholds, levels = {H: sels[H]["threshold"] for H in Hs}, {H: sels[H]["level"] for H in Hs}
    reg_cfg = {k: cfg[k] for k in ("alpha", "p2c_bootstrap_H", "n_cal", "b_flips")}
    arl_cfg, over_cfg, enc_cfg = cfg["arl0"], cfg["overshoot"], cfg["encoders"]
    gammas, factor = [float(g) for g in arl_cfg["gammas"]], arl_cfg["horizon_factor"]
    T_arl = int(factor * max(gammas))
    tasks, blocks = [], []

    def add(block, info, kind, ctx, args_list):
        blocks.append((block, info, ctx, len(tasks), len(tasks) + len(args_list)))
        tasks.extend((kind, ctx, a) for a in args_list)

    for name in names:
        for H in Hs:
            add("d6_registry", {}, "d6_group", {"dataset": name, "H": H, "K": cfg["K"][name], "reps": reps["sign"],
                                                 "label": f"d6|{name}|H{H}", "cfg": reg_cfg}, [None])
    a_, b_, unit_ = lattice.lattice_steps(over_cfg["rows"][-1]["delta"])
    over_rows = [{**row, "threshold": float(row["lam"]) if row["kind"] == "first_order"
                  else (row["units"] + 0.5) * unit_} for row in over_cfg["rows"]]
    exact = {}
    for row in over_rows:
        if row["kind"] == "first_order":
            exact["iid", row["name"]] = brook_evans_arl0(row["delta"], row["lam"], over_cfg["brook_evans_m"])
        else:
            for bg in ("iid", "garch"):
                exact[bg, row["name"]] = lattice.arl0(row["units"], a_, b_, sided=1)
    n_primary = min(reps["overshoot_primary"], reps["overshoot"])
    over_ctx = {bg: {"background": bg, "label": over_cfg["seed_labels"][bg], "T_max": int(over_cfg["T_max"][bg]), "d5": cfg["d5"],
                     "rows": over_rows, "spec_days": over_cfg["spec_days"], "n_primary": n_primary,
                     "targets": {r["name"]: exact["iid", r["name"]] for r in over_rows if r["kind"] == "first_order"}}
                for bg in ("iid", "garch")}
    add("overshoot_lam", {}, "overshoot_lam", over_ctx["garch"], [None])
    for bg in cfg["d5"]["backgrounds"]:
        for role, n_role in (("cal", reps["iid"]), ("eval", reps["sign"])):
            add("d5", {"background": bg, "role": role}, "d5", {"background": bg, "label": d5_label(bg, role),
                                                               "d5": cfg["d5"], "H": Hs, "thresholds": thresholds},
                packets(n_role, cfg["packets"]["d5"]))
    for bg in ("iid", "garch"):
        add("overshoot", {"background": bg}, "overshoot", over_ctx[bg],
            packets(reps["overshoot"], cfg["packets"]["overshoot"]))
    structures = [("P2-C", 1)] + [(p, cfg["K"][name] + (1 if p == "P3-C" else 0)) for name in names
                                  for p in ("P3-C", "P3-CS")]
    for pipeline, D in dict.fromkeys(structures):
        ctx = {"pipeline": pipeline, "D": D, "T": T_arl, "gammas": gammas, "factor": factor,
               "label": f"arl|coins|{pipeline}|{D}"}
        size = max(1, int(arl_cfg["max_elements"] // (T_arl * D * (4 if pipeline == "P3-CS" else 1))))
        add("arl", {"background": "coins", "dataset": "", "pipeline": pipeline, "columns": D * (4 if pipeline ==
                                                                                                 "P3-CS" else 1)},
            "arl_coins", ctx, packets(reps["arl0"], size))
    for name in names:
        X, days, splits, assets = load_rows(name)
        for pipeline in arl_cfg["pipelines"]:
            D = {"P2-C": 1, "P3-C": cfg["K"][name] + 1, "P3-CS": 4 * cfg["K"][name]}[pipeline]
            ctx = {"dataset": name, "pipeline": pipeline, "K": cfg["K"][name], "T": T_arl, "gammas": gammas,
                   "factor": factor, "label": f"arl|d6|{name}|{pipeline}"}
            add("arl", {"background": "d6", "dataset": name, "pipeline": pipeline, "columns": D}, "arl_d6", ctx,
                packets(reps["arl0"], max(1, int(arl_cfg["max_elements"] // (T_arl * D)))))
            raw_ctx = {"dataset": name, "pipeline": pipeline, "gammas": gammas, "factor": factor,
                       "label": f"arl|raw|{name}|{pipeline}"}
            starts = np.arange(0, len(X), cfg["raw_stride"])
            add("arl", {"background": "raw", "dataset": name, "pipeline": pipeline, "columns": D}, "arl_raw", raw_ctx,
                [starts[i:i + arl_cfg["raw_packet"]] for i in range(0, len(starts), arl_cfg["raw_packet"])])
    p1_cols, q_hats = {}, {}
    for name in names:
        X, days, splits, assets = load_rows(name)
        cols = tickers(name)
        a, b = splits["calib"]
        X_fit = symmetrize(X, rng(f"p1c|{name}", CELL_SEED))[0]
        p1_cols[name], q_hats[name] = cols, (X_fit[a:b][:, cols] > 0).mean(axis=0)
        for H in Hs:
            add("p1c_d6", {"dataset": name, "H": H}, "p1c_d6",
                {"dataset": name, "H": H, "cols": cols, "q_hat": q_hats[name], "threshold": thresholds[H],
                 "label": f"p1c|{name}|H{H}"}, packets(reps["sign"], cfg["packets"]["p1c"]))
        for col in cols:
            add("p1d_real", {}, "p1d_real", {"dataset": name, "col": col, "H": Hs, "alpha": alpha,
                                             "n_iid": reps["iid"], "label": f"p1d|{name}|{assets[col]}"}, [None])
        for H, nr in cfg["p3d_settings"]:
            add("p3d", {}, "p3d", {"dataset": name, "H": int(H), "null_rows": nr, "n_iid": reps["iid"],
                                   "label": f"p3d|{name}|H{int(H)}|{nr}"}, [None])
        for H in Hs:
            add("raw_units", {}, "raw_units", {"dataset": name, "H": H, "cols": cols, "threshold": thresholds[H],
                                               "level": levels[H], "stride": cfg["raw_stride"],
                                               "label": f"raw|{name}"}, [None])
            for i in range(len(registry_specs(name, H, None, reg_cfg, exact=False))):
                add("raw_registry", {}, "raw_registry", {"dataset": name, "H": H, "index": i, "cfg": reg_cfg,
                                                         "stride": cfg["raw_stride"],
                                                         "label": f"raw|{name}|H{H}|{i}"}, [None])
    enc_name = enc_cfg["d6_dataset"]
    Xe, _, splits_e, _ = load_rows(enc_name)
    u = market_channel(enc_name)
    u2 = float(np.mean(u[splits_e["calib"][0]:splits_e["calib"][1]] ** 2))
    Ls = [int(L) for L in enc_cfg["L"]]
    enc_ctx = {}
    for bg, sd in (("d5", {L: 1.0 / math.sqrt(L) for L in Ls}), ("d6", {L: math.sqrt(u2 / L) for L in Ls})):
        enc_ctx[bg] = {"background": bg, "dataset": enc_name, "L": Ls, "H": Hs, "sd": sd, "delta": enc_cfg["delta"],
                       "thresholds": thresholds, "lb_lags": enc_cfg["lb_lags"], "wide_factor": enc_cfg["wide_factor"],
                       "alpha": alpha, "label": f"encoder|{bg}"}
        add("encoder", {"background": bg}, "encoder", enc_ctx[bg], packets(reps["sign"], cfg["packets"]["encoders"]))

    timed = run_tasks(tasks, args.jobs)
    results = [out for out, _ in timed]

    cells, raw, arl, over, enc, lam_req, notes, d5_parts, cost = [], [], [], [], [], {}, [], {}, {}
    for block, info, ctx, i0, i1 in blocks:
        parts = results[i0:i1]
        key = ctx["label"] if block == "d5" else block
        cost[key] = cost.get(key, 0.0) + sum(dt for _, dt in timed[i0:i1])
        if block == "d6_registry":
            cells += [registry_cell(rec) for rec in parts[0]]
        elif block == "overshoot_lam":
            lam_req = parts[0]
        elif block == "d5":
            bg = info["background"]
            d5_parts[bg, info["role"]] = parts
            if (bg, "cal") in d5_parts and (bg, "eval") in d5_parts:
                cells += d5_cells(bg, d5_parts[bg, "cal"], d5_parts[bg, "eval"], cfg, sels, d5_label(bg, "cal"))
        elif block == "overshoot":
            over += overshoot_rows(info["background"], parts, ctx, cfg, exact,
                                   lam_req if info["background"] == "garch" else {}, args.quick)
        elif block == "arl":
            arl += arl_rows(info, parts, gammas, factor, info["background"] == "raw")
        elif block == "p1c_d6":
            name, H = info["dataset"], info["H"]
            counts = {arm: np.sum([p[arm] for p in parts], axis=0) for arm in ("exact", "label")}
            assets = load_rows(name)[3]
            for j, col in enumerate(p1_cols[name]):
                cells += sign_cells("d6_p1c", "d6", name, assets[col], H, thresholds[H], levels[H],
                                    {arm: counts[arm][j] for arm in counts}, reps["sign"], "wilson_conditional",
                                    float(q_hats[name][j]))
        elif block in ("p1d_real", "p3d"):
            cells += parts[0]
        elif block == "raw_units":
            raw += parts[0]
        elif block == "raw_registry":
            raw.append(parts[0])
        elif block == "encoder":
            bg = info["background"]
            lam_iid = {H: fpr_threshold(cusum_trajectory_vec(rng(f"encoder|iid|H{H}", CELL_SEED).standard_normal(
                (reps["iid"], H)), enc_cfg["delta"]).max(axis=-1), alpha) for H in Hs}
            enc += encoder_rows(bg, "" if bg == "d5" else enc_name, parts, ctx, lam_iid, levels, enc_cfg["lb_level"],
                                reps["iid"])
    cells_df = pd.DataFrame(cells, columns=CELL_COLUMNS)
    raw_df = pd.DataFrame(join_audit(raw), columns=RAW_COLUMNS)
    arl_df, z_fw = familywise_violations(pd.DataFrame(arl, columns=ARL_COLUMNS))
    over_df = pd.DataFrame(over, columns=OVER_COLUMNS)
    enc_df = pd.DataFrame(enc, columns=ENC_COLUMNS)
    args.out.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    outputs = {"e3_cells.csv": cells_df, "e3_arl0.csv": arl_df, "e3_raw_placebo.csv": raw_df,
               "e3_overshoot.csv": over_df, "e3_window_encoders.csv": enc_df}
    for fname, df in outputs.items():
        pl.save_fair_csv(df, args.out / fname)
    j2 = j2_lines(cells_df, args.quick)
    (args.out / "e3_j2_check.txt").write_text("\n".join(j2) + "\n")
    plot(args.out, fig_dir)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
    shown = " ".join(argv) if argv is not None else " ".join(sys.argv[1:])
    for name in names:
        X, days, splits, assets = load_rows(name)
        state, _ = raw_basis(name)
        notes += [f"rows {name}: excluded before {WINDOW[0]}: {len(EXCLUDED_DAYS[name])} {list(EXCLUDED_DAYS[name])}",
                  f"rows {name}: {days[0]}..{days[-1]} ({len(X)} rows), pretrain {splits['pretrain']}, calib "
                  f"{splits['calib']}; ret_wide.npy sha256 {_sha256(DERIVED / name / 'ret_wide.npy')}",
                  f"tickers {name}: {p1_cols[name]} = {[assets[c] for c in p1_cols[name]]}",
                  f"raw basis {name}: K = {state['rep'].stats['K']}, state sha256 {state['rep'].state_hash()}"]
    gates = over_df[over_df["role"] == "primary"]
    lines = [f"command: python experiments/e3_calibration.py {shown}", f"commit: {commit}",
             f"config: {args.config.name} sha256 {_sha256(args.config)} (quick={args.quick}); jobs {args.jobs}; "
             f"tasks {len(tasks)}",
             *(f"lattice H={H}: units {sels[H]['units']}, threshold {sels[H]['threshold']:.6g}, exact level "
               f"{sels[H]['level']:.12g}; gamma_H = H / alpha = {pl.horizon_gamma(H, alpha):g}" for H in Hs),
             *notes,
             f"overshoot exact iid ARL0 (Brook-Evans, m = {over_cfg['brook_evans_m']}) and sign row (lattice): "
             + ", ".join(f"{bg}/{s} {v:.2f}" for (bg, s), v in sorted(exact.items())),
             (f"overshoot D8 gate (first {n_primary} trajectories, |ARL0/ref - 1| <= 5 %, no rerun): "
              + ", ".join(f"{r.background}/{r.statistic} {r.gate} ({r.rel_gap:+.4f})" for r in gates.itertuples()))
             if not args.quick else
             f"overshoot: no D8 gate under --quick; the first {n_primary} trajectories are a quick_diagnostic (gaps "
             + ", ".join(f"{r.background}/{r.statistic} {r.rel_gap:+.4f}" for r in over_df[over_df["role"] ==
                                                                                  "quick_diagnostic"].itertuples())
             + "); the pre-specified D8 decision uses the first 2,000 trajectories of the full run",
             "ARL0 (D9: PASS iff the 99 % lower bound of the restricted mean reaches gamma, else INDETERMINATE; never "
             f"FAIL): {dict(arl_df['classification'].value_counts().sort_index())}",
             f"bounded stopping-time check over {int((arl_df['classification'] != 'descriptive').sum())} classified "
             f"rows: per-row 99 % bound above 0 in {int((arl_df['ineq_lb99'] > 0).sum())} rows (descriptive); "
             f"certified violations at family-wise 1 % (Bonferroni, z = {z_fw:.3f}, valid under any dependence): "
             f"{int((arl_df['ineq_lb_fw'] > 0).sum())}",
             *j2[-4:],
             f"D5 P1: {reps['iid']} calibration paths (P1-D thresholds) and {reps['sign']} independent evaluation paths "
             "(FPR, Wilson) per background, distinct SeedSequence roles",
             "cpu seconds by block: " + ", ".join(f"{k} {v:.0f}" for k, v in cost.items()),
             "labels: D5 and coin intervals use independent replicates (deff = 1); D6 Wilson intervals are conditional "
             "on the panel; raw and real-even rows are descriptive (overlapping windows of one trajectory, no "
             "interval); counts over cells sharing draws are descriptive",
             *(f"{f} sha256 {_sha256(args.out / f)}" for f in [*outputs, "e3_j2_check.txt"]),
             f"duration: {time.time() - t0:.0f} s"]
    (log_dir / "run.log").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
