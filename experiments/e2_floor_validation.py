"""E2 (Section 5.1): Monte Carlo validation of Propositions 2-3, milestone J1.

Arms (drift starts at the onset, no pre-change data: Lorden's worst case)
  G1  Gaussian i.i.d., known direction (D = 1), three calibrations:
        onset   likelihood-ratio e-process started at the onset, stopped at gamma
        cusum_t CUSUM e-detector stopped at ln(gamma)  (anytime-valid, ARL0 >= gamma)
        cusum_x CUSUM calibrated to ARL0 = gamma        (Lorden-optimal)
  G2  Gaussian i.i.d., unknown direction in dimension D: isotropic mixture
      e-process started at the onset (Proposition 3)
  S1  symmetrised GARCH(1,1)-t7 background, exact sign stream (D = 1):
        fixed   Bernoulli likelihood ratio with p1 = E[p_t]
        oracle  predictable stakes 2 p_t - 1 (volatility known one step ahead)
  S2  symmetrised GARCH(1,1)-t7, D sign streams, sub-Gaussian mixture e-process
J1 rule. Gaussian arms: measured/predicted delay within [0.90, 1.10] (and the
realised ARL0 of cusum_x within 10% of gamma). GARCH arms: the information clock
sum_{t<=T} I_t at stopping within 10% of its prediction (Lemma 1, exact up to
overshoot); calendar delay within 10% whenever the predicted delay exceeds
CALENDAR_MIN days, below which the volatility-memory term (order CV^2 x tau_int
of I_t, about 10-15 days here) is reported, not gated.
The first-order floor ln(gamma)/I is reported next to each prediction.

Usage: python experiments/e2_floor_validation.py --reps 2000 --out results/e2
"""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import csv
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl  # noqa: E402
from jepadrift.sim import NU, T_SCALE, Garch

MASTER_SEED = 20261018
TOL = 0.10
CALENDAR_MIN = 150.0   # days


# ----------------------------------------------------------------------------- utils
def first_passage(step, threshold, reps, nmax, reflect=False):
    """Vectorised first passage of W_n = W_{n-1} + step(n) over threshold."""
    w = np.zeros(reps)
    stop = np.full(reps, np.nan)
    alive = np.ones(reps, dtype=bool)
    for n in range(1, nmax + 1):
        w = w + step(n)
        if reflect:
            np.maximum(w, 0.0, out=w)
        hit = alive & (w >= threshold)
        stop[hit] = n
        alive &= ~hit
        if not alive.any():
            break
    return stop, float(alive.mean())


def summarise(stop):
    x = stop[~np.isnan(stop)]
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(x.size))


def p_up(delta, sig):
    """P(y_t > 0 | sigma_t) for y_t = sigma_t * eps_t + delta, eps unit-variance t7."""
    return stats.t.cdf(delta / (sig * T_SCALE), NU)


def stationary_sign_info(rng, delta, alpha, beta, dim=1, reps=500, steps=2000):
    """E[p_t], E[kl(p_t || 1/2)] under the stationary GARCH law (design inputs)."""
    g = Garch(rng, reps, dim, alpha, beta)
    ps = []
    for _ in range(steps):
        _, sig = g.draw()
        ps.append(p_up(delta, sig))
    ps = np.concatenate(ps)
    return float(ps.mean()), float(fl.kl_bernoulli_half(ps).mean())


def row(clock_ratio=np.nan, **kw):
    kw["ratio"] = kw["mean_delay"] / kw["pred_delay"]
    half = 1.96 * kw["se_delay"] / kw["pred_delay"]
    kw["ratio_lo"], kw["ratio_hi"] = kw["ratio"] - half, kw["ratio"] + half
    kw["first_order_ratio"] = kw["first_order"] / kw["mean_delay"]
    kw["clock_ratio"] = clock_ratio
    ok = True
    if np.isnan(clock_ratio):                       # i.i.d. arms: calendar time is exact
        ok &= abs(kw["ratio"] - 1.0) <= TOL
        if kw.get("mode") == "cusum_x":
            ok &= abs(kw["arl0_mc"] / kw["arl0_pred"] - 1.0) <= TOL
    else:                                           # GARCH arms: information time first
        ok &= abs(clock_ratio - 1.0) <= TOL
        if kw["pred_delay"] >= CALENDAR_MIN:
            ok &= abs(kw["ratio"] - 1.0) <= TOL
    kw["pass"] = int(ok)
    return kw


# ------------------------------------------------------------------------------ arms
def arm_g1(seq, reps, srs, gammas):
    out = []
    for sr in srs:
        theta = sr / math.sqrt(fl.TRADING_DAYS)
        info = theta ** 2 / 2
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            post = lambda n: theta * (rng.standard_normal(reps) + theta) - 0.5 * theta ** 2
            pre = lambda n, r: theta * rng.standard_normal(r) - 0.5 * theta ** 2
            base = dict(arm="G1", background="gauss", dim=1, sr_annual=sr, gamma=gamma,
                        info=info, reps=reps, first_order=fl.first_order_floor(gamma, info))
            # onset e-process
            stop, cens = first_passage(post, a, reps, int(12 * a / info) + 200)
            m, se = summarise(stop)
            out.append(row(**base, mode="onset", mean_delay=m, se_delay=se,
                           pred_delay=fl.onset_lr_delay(gamma, info, theta),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=cens))
            # CUSUM e-detector at ln(gamma)
            ct = fl.cusum_threshold(gamma, theta)
            stop, cens = first_passage(post, ct["h"], reps, int(12 * a / info) + 200, reflect=True)
            m, se = summarise(stop)
            arl0 = np.nan
            if ct["arl0"] <= 2.5e5:
                r0 = 200
                s0, _ = first_passage(lambda n: pre(n, r0), ct["h"], r0, int(6 * ct["arl0"]), reflect=True)
                arl0 = float(np.nanmean(s0))
            out.append(row(**base, mode="cusum_t", mean_delay=m, se_delay=se, pred_delay=ct["add"],
                           arl0_mc=arl0, arl0_pred=ct["arl0"], censored=cens))
            # CUSUM calibrated to ARL0 = gamma
            cx = fl.cusum_exact(gamma, theta)
            if not cx["feasible"]:
                continue
            stop, cens = first_passage(post, cx["h"], reps, int(30 * gamma) + 2000, reflect=True)
            m, se = summarise(stop)
            r0 = 2000
            s0, _ = first_passage(lambda n: pre(n, r0), cx["h"], r0, int(30 * gamma), reflect=True)
            out.append(row(**base, mode="cusum_x", mean_delay=m, se_delay=se, pred_delay=cx["add"],
                           arl0_mc=float(np.nanmean(s0)), arl0_pred=float(gamma), censored=cens))
    return out


def arm_g2(seq, reps, dims, gammas, info=0.01):
    out = []
    for dim in dims:
        r = reps if dim <= 20 else max(reps // 2, 200)
        s2 = 2.0 * info / dim
        theta = np.full(dim, math.sqrt(2.0 * info / dim))
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            mult = fl.mixture_multiplier(dim, gamma)
            S = np.zeros((r, dim))
            stop = np.full(r, np.nan)
            alive = np.ones(r, dtype=bool)
            for n in range(1, int(10 * mult * a / info) + 200):
                S += rng.standard_normal((r, dim)) + theta
                ll = -0.5 * dim * math.log1p(n * s2) + s2 * np.einsum("ij,ij->i", S, S) / (2 * (1 + n * s2))
                hit = alive & (ll >= a)
                stop[hit] = n
                alive &= ~hit
                if not alive.any():
                    break
            m, se = summarise(stop)
            out.append(row(arm="G2", background="gauss", mode="mixture", dim=dim, sr_annual=fl.sharpe_from_kl(info),
                           gamma=gamma, info=info, reps=r, mean_delay=m, se_delay=se,
                           pred_delay=mult * a / info, first_order=fl.first_order_floor(gamma, info),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean())))
    return out


def arm_s1(seq, reps, srs, gammas, alpha, beta):
    out = []
    for sr in srs:
        delta = sr / math.sqrt(fl.TRADING_DAYS)
        rng_d = np.random.default_rng(seq.spawn(1)[0])
        p_bar, kl_bar = stationary_sign_info(rng_d, delta, alpha, beta)
        kl_fixed = float(fl.kl_bernoulli_half(p_bar))
        up, down = math.log(2 * p_bar), math.log(2 * (1 - p_bar))
        for gamma in gammas:
            a = math.log(gamma)
            for mode in ("fixed", "oracle"):
                rng = np.random.default_rng(seq.spawn(1)[0])
                g = Garch(rng, reps, 1, alpha, beta)
                info = kl_fixed if mode == "fixed" else kl_bar
                w, clock = np.zeros(reps), np.zeros(reps)
                stop, clk = np.full(reps, np.nan), np.full(reps, np.nan)
                alive = np.ones(reps, dtype=bool)
                for n in range(1, int(12 * a / info) + 200):
                    x, sig = g.draw()
                    p = p_up(delta, sig)
                    b = (x + delta) > 0
                    if mode == "fixed":
                        w += np.where(b, up, down)
                        clock += p * up + (1 - p) * down        # conditional drift of the walk
                    else:
                        w += np.where(b, np.log(2 * p), np.log(2 * (1 - p)))
                        clock += fl.kl_bernoulli_half(p)
                    hit = alive & (w >= a)
                    stop[hit], clk[hit] = n, clock[hit]
                    alive &= ~hit
                    if not alive.any():
                        break
                m, se = summarise(stop)
                target = a + 0.5 * up                            # ln(gamma) + mean lattice overshoot
                out.append(row(arm="S1", background=f"garch_t7_b{beta}", mode=mode, dim=1, sr_annual=sr,
                               gamma=gamma, info=info, reps=reps, mean_delay=m, se_delay=se,
                               pred_delay=target / info, first_order=fl.first_order_floor(gamma, info),
                               arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean()),
                               clock_ratio=float(np.nanmean(clk)) / target))
    return out


def arm_s2(seq, reps, dims, gammas, alpha, beta, info_target=0.01):
    out = []
    for dim in dims:
        # per-coordinate drift giving sum_k (2 p_k - 1)^2 / 2 = info_target (calibrated once)
        rng_d = np.random.default_rng(seq.spawn(1)[0])
        lo, hi = 1e-4, 2.0
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            p_bar, _ = stationary_sign_info(rng_d, mid, alpha, beta, dim=dim, reps=200, steps=500)
            val = dim * (2 * p_bar - 1) ** 2 / 2
            lo, hi = (mid, hi) if val < info_target else (lo, mid)
        delta = 0.5 * (lo + hi)
        p_bar, _ = stationary_sign_info(np.random.default_rng(seq.spawn(1)[0]), delta, alpha, beta, dim=dim)
        info = dim * (2 * p_bar - 1) ** 2 / 2
        s2 = 2.0 * info / dim
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            g = Garch(rng, reps, dim, alpha, beta)
            mult = fl.mixture_multiplier(dim, gamma)
            S = np.zeros((reps, dim))
            stop = np.full(reps, np.nan)
            alive = np.ones(reps, dtype=bool)
            clock, clk = np.zeros(reps), np.full(reps, np.nan)
            for n in range(1, int(10 * mult * a / info) + 200):
                x, sig = g.draw()
                S += np.where(x + delta > 0, 1.0, -1.0)
                clock += dim * (2 * p_up(delta, sig) - 1) ** 2 / 2
                ll = -0.5 * dim * math.log1p(n * s2) + s2 * np.einsum("ij,ij->i", S, S) / (2 * (1 + n * s2))
                hit = alive & (ll >= a)
                stop[hit], clk[hit] = n, clock[hit]
                alive &= ~hit
                if not alive.any():
                    break
            m, se = summarise(stop)
            out.append(row(arm="S2", background=f"garch_t7_b{beta}", mode="sign_mixture", dim=dim,
                           sr_annual=float("nan"), gamma=gamma, info=info, reps=reps, mean_delay=m, se_delay=se,
                           pred_delay=mult * a / info, first_order=fl.first_order_floor(gamma, info),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean()),
                           clock_ratio=float(np.nanmean(clk)) / (mult * a)))
    return out


def h0_sign_check(seq, alpha, beta, dim=5, reps=200, steps=5000):
    """Exactness of the sign streams under H0: mean 1/2, no serial or cross dependence."""
    g = Garch(np.random.default_rng(seq.spawn(1)[0]), reps, dim, alpha, beta)
    bits, sq = [], []
    for _ in range(steps):
        x, _ = g.draw()
        bits.append((x > 0).astype(float))
        sq.append(x[:, 0] ** 2)
    b = np.stack(bits)                      # steps x reps x dim
    e = 2 * b - 1
    n = e.shape[0] * e.shape[1]
    acf_bits = float((e[1:] * e[:-1]).mean())
    cross = float((e[..., 0] * e[..., 1]).mean())
    q = np.stack(sq)
    q = (q - q.mean(0)) / q.std(0)
    acf_sq = float((q[1:] * q[:-1]).mean())
    return dict(mean_bit=float(b.mean()), se=0.5 / math.sqrt(b.size), acf1_bits=acf_bits,
                cross_bits=cross, se_corr=1 / math.sqrt(n), acf1_squares=acf_sq)


# ------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=Path("results/e2"))
    ap.add_argument("--alpha", type=float, default=0.08)
    ap.add_argument("--beta", type=float, default=0.90)
    ap.add_argument("--quick", action="store_true", help="reduced grid for a smoke test")
    args = ap.parse_args(argv)
    seq = np.random.SeedSequence(MASTER_SEED)
    srs = (1.0, 4.0) if args.quick else (1.0, 2.0, 4.0)
    gammas = (20, 252)
    dims = (1, 5, 20) if args.quick else (1, 2, 5, 10, 20, 64)
    t0 = time.time()
    rows = []
    rows += arm_g1(seq, args.reps, srs, gammas)
    rows += arm_g2(seq, args.reps // 2, dims, gammas)
    rows += arm_s1(seq, args.reps, srs, gammas, args.alpha, args.beta)
    rows += arm_s2(seq, args.reps // 2, (5, 20), gammas, args.alpha, args.beta)
    h0 = h0_sign_check(seq, args.alpha, args.beta)
    args.out.mkdir(parents=True, exist_ok=True)
    cols = ["arm", "mode", "background", "dim", "sr_annual", "gamma", "info", "reps", "mean_delay", "se_delay",
            "pred_delay", "ratio", "ratio_lo", "ratio_hi", "first_order", "first_order_ratio",
            "clock_ratio", "arl0_mc", "arl0_pred", "censored", "pass"]
    with open(args.out / "e2_cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})
    n_pass = sum(r["pass"] for r in rows)
    worst = max(rows, key=lambda r: abs(r["ratio"] - 1))
    gate = "information clock" if not np.isnan(worst["clock_ratio"]) and worst["pred_delay"] < CALENDAR_MIN \
        else "calendar delay"
    h0_ok = (abs(h0["mean_bit"] - 0.5) < 4 * h0["se"] and abs(h0["acf1_bits"]) < 4 * h0["se_corr"]
             and abs(h0["cross_bits"]) < 4 * h0["se_corr"])
    lines = [f"E2 / J1 summary  (seed {MASTER_SEED}, reps {args.reps}, {time.time() - t0:.0f} s)",
             f"cells passing the J1 rule: {n_pass}/{len(rows)}",
             f"largest calendar deviation: {worst['arm']}/{worst['mode']} D={worst['dim']} SR={worst['sr_annual']} "
             f"gamma={worst['gamma']} delay ratio={worst['ratio']:.3f} (gated on the {gate})",
             f"H0 sign streams: mean={h0['mean_bit']:.4f} acf1={h0['acf1_bits']:+.4f} "
             f"cross={h0['cross_bits']:+.4f} (se {h0['se_corr']:.4f}); acf1 of squares={h0['acf1_squares']:+.3f}",
             f"J1: {'PASS' if n_pass == len(rows) and h0_ok else 'FAIL'}"]
    (args.out / "e2_j1_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if n_pass == len(rows) and h0_ok else 1


if __name__ == "__main__":
    sys.exit(main())
