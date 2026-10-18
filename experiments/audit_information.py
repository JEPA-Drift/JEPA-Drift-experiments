"""Stream 11: information audit of the D2 and D3 cross-sections, rows dated 2005-2019 only (milestone J2).

Items (prompts/streams/prompt-11-audit.md)
  1 spectrum      calib eigenvalues of the sample and Ledoit-Wolf covariances and of the sample correlation,
                  Marchenko-Pastur edge and K; eta = lambda_1 / tr Sigma per calendar year
  2 signs         mean pairwise sign correlation, Gaussian map rho = sin(pi rho_sign / 2), K_eff = 1 / rho_sign
  3 symmetry      frozen directions (PC1-PC20, orthogonalised characteristics): exact binomial test of q_hat = 1/2,
                  triples test of Randles, Fligner, Policello & Wolfe (1980) on u'x_t / sigma_{t|t-1} (GARCH(1,1)),
                  Holm correction over the joint family of a dataset
  4 drift Sharpe  debiased SR_S^2 at the boundaries of the SPY datings, pooled within-phase covariance, subspaces of
                  dimension <= 30, moving-block bootstrap (20 days, 2000 draws), median over transitions; selection of
                  the market SR^2 against 2000 circular rotations of each phase chain (placebo_selection.csv)
  5 ceilings      N1 = E[s^2] E[s^-2] (idiosyncratic dispersion), N2 = conditional over static information
                  (rolling 60-day Ledoit-Wolf) with its noise on 2000 day-permuted backgrounds and the net ratio,
                  N3 = multivariate t fit and J / Sigma^-1 = (nu+1) nu / ((nu+3)(nu-2))
  6 budget        share of dated phases with L * I_hat >= ln(gamma), gamma in {20, 252} (budget reading, Lemma 1)
  7 gains         section 2.4 planning formulas evaluated on the estimates -> predicted_gains.csv (input of E1)
Outputs: results/audit/*.csv, figures/audit/*.{png,pdf} drawn from the CSVs only, logs/audit/audit.log.

Usage: python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
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
import zlib
from itertools import repeat
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import linalg, optimize, special, stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl
from jepadrift.data_loader import articleB, sp500
from jepadrift.injection import fit_background, gls_residual
from jepadrift.pipelines import save_fair_csv, sign_diagnostics
from jepadrift.representations.extract import DATASETS, segment_rows
from jepadrift.representations.pca import PCAOrthogonal, pca_directions
from jepadrift.stats.covariance import ledoit_wolf
from jepadrift.stats.garch import fit_garch_qmle

WINDOW = ("2005-01-01", "2019-12-31")
N_PC = 20
BLOCK = 20
BOOT = 2000
MAX_DIM = 30
MIN_PHASE = 20
LW_DAYS = 60
GAMMAS = (20, 252)
ALPHA = 0.05
DATINGS = ("lt_spy", "strict_ps", "symmetric")
STREAM = 11
REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVED = REPO_ROOT / "data" / "derived"
FROZEN = {"K": "mp", "mode": "factor", "shrinkage": "ledoit_wolf"}
AGGREGATES = ("market", "factor", "idio", "residual_full", "chars")
SERIES = ("#2a78d6", "#eb6834")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e5e4e0"
COLUMNS = {
    "spectrum": ["dataset", "matrix", "rank", "eigval", "share", "cum_share", "n_days", "mp_edge", "n_above_edge",
                 "K", "lw_shrinkage"],
    "eta_by_year": ["dataset", "year", "n_days", "eta_sample", "eta_lw", "lw_shrinkage"],
    "sign_corr": ["dataset", "segment", "n_days", "N", "rho_sign", "rho_gauss", "rho_ret", "K_eff", "K_eff_N",
                  "rho_sign_med", "K_eff_meas", "K_eff_ana"],
    "symmetry_tests": ["dataset", "direction", "n", "q_hat", "binom_p", "triples_T", "triples_z", "triples_p",
                       "garch_omega", "garch_alpha", "garch_beta", "garch_converged", "binom_p_holm",
                       "triples_p_holm", "binom_reject", "triples_reject"],
    "drift_sharpe_transitions": ["dataset", "dating", "level", "transition", "boundary", "n1", "n2",
                                 "n_transitions", "subspace", "d", "sr2_raw", "sr2_debiased", "sr2_spec", "ci_lo",
                                 "ci_hi", "n_boot"],
    "channel_ceilings": ["dataset", "ceiling", "variant", "direction", "value", "i_cond", "i_static", "nu",
                         "iterations", "converged", "n_days", "d"],
    "budget_share": ["dataset", "dating", "subspace", "gamma", "n_phases", "n_in_budget", "share"],
    "predicted_gains": ["dataset", "dating", "step", "gamma", "N", "K", "rho_ret", "rho_sign", "kappa_hat",
                        "sr2_market", "sr2_factor", "sr2_idio", "D_A", "D_B", "M_A", "M_B", "G_floor",
                        "G_floor_sign", "G_tax"],
    "placebo_selection": ["dataset", "dating", "n_transitions", "n_placebo", "sr2_real_median", "sr2_placebo_median",
                          "ci_lo", "ci_hi", "selection_factor", "selection_excess", "p_placebo"],
}


def window_rows(dates):
    """Boolean mask of the rows dated in the allowed window [2005-01-01, 2019-12-31]."""
    return (dates >= np.datetime64(WINDOW[0])) & (dates <= np.datetime64(WINDOW[1]))


def load(name):
    """Window rows of a dataset, its frozen calib basis (checked against the prompt 6 sidecar) and D3 characteristics."""
    loader, load_splits = DATASETS[name]
    ret, dates, assets = loader()
    w = window_rows(dates)
    X, days = np.ascontiguousarray(ret[w]), dates[w]
    if days.max() > np.datetime64(WINDOW[1]) or not np.isfinite(X).all():
        raise ValueError(f"{name}: the window must hold finite returns dated no later than {WINDOW[1]}")
    segments = load_splits(name)["segments"]
    seg = {k: segment_rows(days, segments[k]) for k in ("pretrain", "calib")}
    seg["window"] = (0, len(days))
    a, b = seg["calib"]
    state_hash = PCAOrthogonal(**FROZEN).fit(X[a:b], None, days[a:b]).state_hash()
    sidecars = [json.loads(p.read_text()) for p in sorted((DERIVED / name).glob("z_*.json"))]
    committed = [s["state_sha256"] for s in sidecars if s["config"] == FROZEN]
    if committed != [state_hash]:
        raise ValueError(f"{name}: refitted calib basis {state_hash[:16]} differs from the prompt 6 sidecar {committed}")
    eigval, eigvec, _, pca = pca_directions(X[a:b], "mp", "full", "ledoit_wolf")
    d = {"name": name, "X": X, "dates": days, "seg": seg, "eigval": eigval, "eigvec": eigvec,
         "K": pca["n_above_edge"] - 1, "n_above": pca["n_above_edge"], "mp_edge": pca["mp_edge"],
         "lw": pca["shrinkage"], "state_hash": state_hash, "C": None, "chars": []}
    if name == "d3_239":
        chars = sp500.load_chars(name)
        cols = [c for c in chars.columns if c.startswith("c_")]
        T, N = ret.shape
        if not ((chars["asset_id"].to_numpy() == np.tile(np.asarray(assets, dtype=object), T)).all()
                and (chars["date"].to_numpy().astype("datetime64[D]") == np.repeat(dates, N)).all()):
            raise ValueError(f"{name}: chars.parquet is not in the (date, asset) order of ret_wide.npy")
        C = chars[cols].to_numpy(dtype=np.float64).reshape(T, N, len(cols))[w]
        d["C"], d["chars"] = np.where(np.isnan(C), 0.0, C), cols
    return d


def spectrum_rows(d):
    """Calib eigenvalues of the sample and Ledoit-Wolf covariances and of the sample correlation (item 1)."""
    a, b = d["seg"]["calib"]
    Xc = d["X"][a:b]
    mats = {"cov_sample": np.cov(Xc, rowvar=False, bias=True), "cov_lw": ledoit_wolf(Xc)[0],
            "corr_sample": np.corrcoef(Xc, rowvar=False)}
    rows = []
    for matrix, A in mats.items():
        ev = np.linalg.eigvalsh(A)[::-1]
        share = ev / ev.sum()
        rows += [{"dataset": d["name"], "matrix": matrix, "rank": k, "eigval": e, "share": s, "cum_share": c,
                  "n_days": b - a, "mp_edge": d["mp_edge"], "n_above_edge": d["n_above"], "K": d["K"],
                  "lw_shrinkage": d["lw"]}
                 for k, (e, s, c) in enumerate(zip(ev, share, np.cumsum(share)), 1)]
    return rows


def eta_rows(d):
    """eta = lambda_1 / tr Sigma per calendar year of the window, sample and Ledoit-Wolf covariances (item 1)."""
    years = d["dates"].astype("datetime64[Y]").astype(int) + 1970
    rows = []
    for year in np.unique(years):
        Xy = d["X"][years == year]
        S = np.cov(Xy, rowvar=False, bias=True)
        L, delta = ledoit_wolf(Xy)
        rows.append({"dataset": d["name"], "year": int(year), "n_days": len(Xy),
                     "eta_sample": np.linalg.eigvalsh(S)[-1] / np.trace(S),
                     "eta_lw": np.linalg.eigvalsh(L)[-1] / np.trace(L), "lw_shrinkage": delta})
    return rows


def sign_rows(d):
    """Mean pairwise sign correlation, its Gaussian map, the return correlation and K_eff per segment (item 2)."""
    N = d["X"].shape[1]
    upper = np.triu_indices(N, 1)
    rows = []
    for segment in ("pretrain", "calib", "window"):
        a, b = d["seg"][segment]
        R = d["X"][a:b]
        rho = sp500._mean_pairwise_sign_corr(R)
        r15 = sign_diagnostics(R.T)
        rows.append({"dataset": d["name"], "segment": segment, "n_days": b - a, "N": N, "rho_sign": rho,
                     "rho_gauss": math.sin(math.pi * rho / 2),
                     "rho_ret": float(np.corrcoef(R, rowvar=False)[upper].mean()), "K_eff": 1 / rho,
                     "K_eff_N": N / (1 + (N - 1) * rho), "rho_sign_med": r15["rho_sign"],
                     "K_eff_meas": r15["K_eff_meas"], "K_eff_ana": r15["K_eff_ana"]})
    return rows


def triples_counts(y):
    """(T, sum_t B_t^2, sum_{s<t} B_st^2) of the triples statistic, O(n^2 log n) by pairs of the sorted sample."""
    x = np.sort(np.asarray(y, dtype=np.float64))
    n = x.size
    acc = np.zeros(n, dtype=np.int64)
    pair_sq = 0
    for p in range(n - 1):  # ponytail: one numpy pass per row of pairs, ~1 s at n = 3774; batch rows if n grows past 10^4
        q = np.arange(p + 1, n)
        between = q - p - 1
        low = 2 * x[p] - x[q]
        b = (p - np.minimum(np.searchsorted(x, low, "right"), p)) - np.minimum(np.searchsorted(x, low, "left"), p)
        mid = 0.5 * (x[p] + x[q])
        b += (np.clip(np.searchsorted(x, mid, "left") - p - 1, 0, between)
              - (between - np.clip(np.searchsorted(x, mid, "right") - p - 1, 0, between)))
        high = 2 * x[q] - x[p]
        b += ((n - q - 1 - np.maximum(np.searchsorted(x, high, "right") - q - 1, 0))
              - np.maximum(np.searchsorted(x, high, "left") - q - 1, 0))
        acc[p] += b.sum()
        acc[q] += b
        pair_sq += int(b @ b)
    bt = acc // 2
    return int(bt.sum() // 3), int((bt ** 2).sum()), pair_sq


def triples_test(y):
    """Triples test of symmetry (Randles, Fligner, Policello & Wolfe, 1980): (T, z, two-sided p), variance of NSM3::RFPW."""
    n = len(y)
    T, bt2, bst2 = triples_counts(y)
    var = ((n - 3) * (n - 4) / ((n - 1) * (n - 2)) * bt2 + (n - 3) / (n - 4) * bst2 + n * (n - 1) * (n - 2) / 6
           - (1 - (n - 3) * (n - 4) * (n - 5) / (n * (n - 1) * (n - 2))) * T ** 2)
    z = T / math.sqrt(var)
    return T, z, float(2 * stats.norm.sf(abs(z)))


def garch_filter(y, omega, alpha, beta):
    """sigma_{t|t-1} of a GARCH(1,1) started at its unconditional variance omega / (1 - alpha - beta), as R01's QMLE."""
    y2 = np.asarray(y, dtype=np.float64) ** 2
    s2 = np.empty_like(y2)
    s2[0] = omega / (1.0 - alpha - beta)
    for t in range(1, len(y2)):
        s2[t] = omega + alpha * y2[t - 1] + beta * s2[t - 1]
    return np.sqrt(s2)


def garch_scale(y):
    """GARCH(1,1) QMLE of R01 (fit_garch_qmle) on the series itself, then its sigma_{t|t-1}."""
    (omega, alpha, beta), converged = fit_garch_qmle(y)
    return garch_filter(y, omega, alpha, beta), {"omega": omega, "alpha": alpha, "beta": beta,
                                                 "converged": bool(converged)}


def char_directions(C, V_f):
    """u_{t,j} = P c_{t,j} / ||P c_{t,j}||, P = I - V_f V_f' (Euclidean projection on the idiosyncratic subspace)."""
    U = C - V_f @ (V_f.T @ C)
    norm = np.linalg.norm(U, axis=1, keepdims=True)
    if not (norm > 1e-10 * np.linalg.norm(C, axis=1, keepdims=True)).all():
        raise ValueError("a characteristic vanishes after projection on the idiosyncratic subspace")
    return U / norm


def projections(d, n_pc=N_PC):
    """Frozen-direction series y_t = u_t'x_t: PC1..PC<n_pc>, then the orthogonalised characteristics (D3)."""
    series = {f"PC{k + 1}": d["X"] @ d["eigvec"][:, k] for k in range(n_pc)}
    if d["C"] is not None:
        y = np.einsum("tnp,tn->tp", char_directions(d["C"], d["eigvec"][:, :d["K"] + 1]), d["X"])
        series.update({f"char:{c.removeprefix('c_')}": y[:, j] for j, c in enumerate(d["chars"])})
    return series


def symmetry_rows(name, series, scales):
    """Exact binomial test of q_hat = 1/2 and triples test on y / sigma_{t|t-1}, Holm over the joint family (item 3)."""
    rows = []
    for label, y in series.items():
        sigma, garch = scales[label]
        k, n = int((y > 0).sum()), int((y != 0).sum())
        T, z, p = triples_test(y / sigma)
        rows.append({"dataset": name, "direction": label, "n": n, "q_hat": k / n,
                     "binom_p": stats.binomtest(k, n, 0.5).pvalue, "triples_T": T, "triples_z": z, "triples_p": p,
                     "garch_omega": garch["omega"], "garch_alpha": garch["alpha"], "garch_beta": garch["beta"],
                     "garch_converged": garch["converged"]})
    m = len(rows)
    reject, adjusted, _, _ = multipletests([r["binom_p"] for r in rows] + [r["triples_p"] for r in rows],
                                           alpha=ALPHA, method="holm")
    for i, r in enumerate(rows):
        r.update(binom_p_holm=adjusted[i], triples_p_holm=adjusted[m + i], binom_reject=bool(reject[i]),
                 triples_reject=bool(reject[m + i]))
    return rows


def spy_phases(variant, dates):
    """SPY phases of a dating as (phase_id, start, end, window rows dated in (start, end]); empty phases dropped."""
    phases = articleB.load_phases(variant)
    out = []
    for r in phases[phases.ticker == "SPY"].itertuples():
        rows = np.flatnonzero((dates > np.datetime64(r.start_date)) & (dates <= np.datetime64(r.end_date)))
        if rows.size:
            out.append((int(r.phase_id), r.start_date, r.end_date, rows))
    return out


def transitions(phases):
    """Adjacent phase pairs with a boundary in [2005-01-01, 2019-12-31) and at least MIN_PHASE rows on each side."""
    return [(i, i + 1) for i in range(len(phases) - 1)
            if phases[i][2] == phases[i + 1][1] and WINDOW[0] <= phases[i][2] < WINDOW[1]
            and min(phases[i][3].size, phases[i + 1][3].size) >= MIN_PHASE]


def _sr2(delta, S, n1, n2):
    """Raw, exactly unbiased and prompt-formula SR^2 from mean differences and pooled covariances (leading axes broadcast)."""
    dim, nu, c = delta.shape[-1], n1 + n2 - 2, 1.0 / n1 + 1.0 / n2
    if nu <= dim + 1:
        raise ValueError(f"a pooled covariance with {nu} degrees of freedom cannot whiten {dim} dimensions")
    D2 = np.einsum("...i,...i->...", delta, np.linalg.solve(S, delta[..., None])[..., 0])
    k = (nu - dim - 1) / nu
    return 252 * D2, 252 * (D2 * k - dim * c), 252 * (D2 - dim * c) * k


def debiased_sr2(Y1, Y2):
    """(sr2_raw, sr2_debiased, sr2_spec) of the mean shift from phase 1 to phase 2, pooled within-phase covariance."""
    A, B = Y1 - Y1.mean(axis=0), Y2 - Y2.mean(axis=0)
    S = (A.T @ A + B.T @ B) / (len(Y1) + len(Y2) - 2)
    return tuple(float(v) for v in _sr2(Y2.mean(axis=0) - Y1.mean(axis=0), S, len(Y1), len(Y2)))


def mbb_indices(n, B, rng):
    """Moving-block bootstrap rows (Kunsch, 1989): ceil(n / BLOCK) uniform block starts, blocks concatenated, cut to n."""
    starts = rng.integers(0, n - BLOCK + 1, size=(B, -(-n // BLOCK)))
    return (starts[:, :, None] + np.arange(BLOCK)).reshape(B, -1)[:, :n]


def subspaces(d, proj):
    """Projections of item 4: market PC1, factor PC2..PC(K+1), idiosyncratic blocks of MAX_DIM PCs, characteristics."""
    Z, K = d["X"] @ d["eigvec"], d["K"]
    out = {"market": Z[:, :1], "factor": Z[:, 1:K + 1]}
    for b, j in enumerate(range(K + 1, Z.shape[1], MAX_DIM), 1):
        out[f"idio:b{b}"] = Z[:, j:j + MAX_DIM]
    chars = [y for label, y in proj.items() if label.startswith("char:")]
    if chars:
        out["chars"] = np.column_stack(chars)
    return out


def _moments(Y, idx):
    """Per-draw means and centred cross-products of the resampled rows Y[idx], in chunks of 100 draws."""
    B, dim = len(idx), Y.shape[1]
    mean, sscp = np.empty((B, dim)), np.empty((B, dim, dim))
    for c0 in range(0, B, 100):
        Yb = Y[idx[c0:c0 + 100]]
        mean[c0:c0 + 100] = Yb.mean(axis=1)
        Cb = Yb - mean[c0:c0 + 100, None, :]
        sscp[c0:c0 + 100] = np.matmul(Cb.transpose(0, 2, 1), Cb)
    return mean, sscp


def _ci(draws, estimate):
    """95 % percentile interval of the bootstrap draws shifted by the bootstrap bias mean(draws) - estimate."""
    shift = draws.mean() - estimate
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return lo - shift, hi - shift


def drift_rows(name, dating, phases, Ys, B):
    """Debiased drift Sharpe per transition and subspace, moving-block bootstrap CIs, medians over transitions (item 4)."""
    pairs = transitions(phases)
    if not pairs:
        return []
    used = sorted({i for pair in pairs for i in pair})
    draws = {i: mbb_indices(phases[i][3].size, B, np.random.default_rng(np.random.SeedSequence(
        [STREAM, zlib.crc32(name.encode()), zlib.crc32(dating.encode()), phases[i][0]]))) for i in used}
    point, boot = {}, {}
    for s, Y in Ys.items():  # ponytail: direct resampling (~10 s per dating on D3); precompute block sums if B grows
        moments = {i: _moments(Y[phases[i][3]], draws[i]) for i in used}
        for i, j in pairs:
            n1, n2 = phases[i][3].size, phases[j][3].size
            point[i, j, s] = np.array(debiased_sr2(Y[phases[i][3]], Y[phases[j][3]]))
            pooled = (moments[i][1] + moments[j][1]) / (n1 + n2 - 2)
            boot[i, j, s] = _sr2(moments[j][0] - moments[i][0], pooled, n1, n2)[1]
    dims = {s: Y.shape[1] for s, Y in Ys.items()}
    blocks = [s for s in Ys if s.startswith("idio:")]
    for target, parts in (("idio", blocks), ("residual_full", ["factor", "idio"])):
        dims[target] = sum(dims[s] for s in parts)
        for i, j in pairs:
            point[i, j, target] = sum(point[i, j, s] for s in parts)
            boot[i, j, target] = sum(boot[i, j, s] for s in parts)
    order = ["market", "factor", *blocks, "idio", "residual_full"] + (["chars"] if "chars" in Ys else [])
    base = {"dataset": name, "dating": dating}
    rows = []
    for i, j in pairs:
        for s in order:
            lo, hi = _ci(boot[i, j, s], point[i, j, s][1])
            rows.append({**base, "level": "transition", "transition": f"{phases[i][0]}-{phases[j][0]}",
                         "boundary": phases[i][2], "n1": phases[i][3].size, "n2": phases[j][3].size,
                         "n_transitions": 1, "subspace": s, "d": dims[s], "sr2_raw": point[i, j, s][0],
                         "sr2_debiased": point[i, j, s][1], "sr2_spec": point[i, j, s][2], "ci_lo": lo, "ci_hi": hi,
                         "n_boot": B})
    for s in order:
        med = np.median([point[i, j, s] for i, j in pairs], axis=0)
        lo, hi = _ci(np.median([boot[i, j, s] for i, j in pairs], axis=0), med[1])
        rows.append({**base, "level": "median", "transition": "median", "boundary": "", "n1": math.nan,
                     "n2": math.nan, "n_transitions": len(pairs), "subspace": s, "d": dims[s], "sr2_raw": med[0],
                     "sr2_debiased": med[1], "sr2_spec": med[2], "ci_lo": lo, "ci_hi": hi, "n_boot": B})
    return rows


def rotate_phases(phases, T, offset):
    """Phases moved by `offset` rows around the window (circular); a phase crossing the seam keeps its rows pooled."""
    return [(pid, start, end, np.sort((rows + offset) % T)) for pid, start, end, rows in phases]


def placebo_rows(name, dating, phases, y, P, B):
    """Selection of the market SR^2 by the dated boundaries: real median against P circular rotations of the chain."""
    pairs, T = transitions(phases), len(y)
    if not pairs:
        return None

    def chain_median(ph):
        return np.median([debiased_sr2(y[ph[i][3]], y[ph[j][3]]) for i, j in pairs], axis=0)

    key = [zlib.crc32(name.encode()), zlib.crc32(dating.encode())]
    offsets = np.random.default_rng(np.random.SeedSequence([STREAM, 12, *key])).integers(0, T, P)
    real = chain_median(phases)
    placebo = np.array([chain_median(rotate_phases(phases, T, o)) for o in offsets])
    med = np.median(placebo, axis=0)
    draws = np.random.default_rng(np.random.SeedSequence([STREAM, 13, *key])).integers(0, P, (B, P))
    lo, hi = np.percentile(np.median(placebo[draws, 1], axis=1), [2.5, 97.5])
    row = {"dataset": name, "dating": dating, "level": "placebo", "transition": "placebo", "boundary": "",
           "n1": math.nan, "n2": math.nan, "n_transitions": len(pairs), "subspace": "market", "d": y.shape[1],
           "sr2_raw": med[0], "sr2_debiased": med[1], "sr2_spec": med[2], "ci_lo": lo, "ci_hi": hi, "n_boot": B}
    selection = {"dataset": name, "dating": dating, "n_transitions": len(pairs), "n_placebo": P,
                 "sr2_real_median": real[1], "sr2_placebo_median": med[1], "ci_lo": lo, "ci_hi": hi,
                 "selection_factor": real[1] / med[1] if med[1] > 0 else math.nan,
                 "selection_excess": real[1] - med[1],
                 "p_placebo": (1 + int((placebo[:, 1] >= real[1]).sum())) / (1 + P)}
    return row, selection

def n1(Z):
    """N1 = mean(s^2) mean(1/s^2), s_t^2 = mean squared whitened idiosyncratic coordinate; raw and chi-square corrected."""
    s2 = (Z ** 2).mean(axis=1)
    raw = float(s2.mean() * (1.0 / s2).mean())
    return raw, raw * (Z.shape[1] - 2) / Z.shape[1]


def rolling_lw(X, days=LW_DAYS):
    """Ledoit-Wolf covariance of the `days` rows before t, for t = days .. len(X) - 1 (past rows only)."""
    for t in range(days, len(X)):
        yield ledoit_wolf(X[t - days:t])[0]


def _directions(B, F2, T):
    """Directions a_t (N, m) of N2 for t = LW_DAYS .. T - 1: the F1 loadings, then the day's F2 residuals (D3)."""
    for t in range(LW_DAYS, T):
        yield B if F2 is None else np.concatenate([B, F2[t]], axis=1)


def _noise_chunk(X, B, F2, keys):
    """Noise-only N2 ratios on day-permuted copies of X, one per key; the directions keep their calendar order."""
    return [info_ratio(_directions(B, F2, len(X)),
                       rolling_lw(X[np.random.default_rng(np.random.SeedSequence(key)).permutation(len(X))]))[0]
            for key in keys]


def n2_noise(X, B, F2, keys, jobs=1):
    """N2 ratio of each day-permuted background (one row per key) over `jobs` spawned processes; independent of jobs."""
    if jobs <= 1 or len(keys) < 2:
        return np.array(_noise_chunk(X, B, F2, keys))
    size = -(-len(keys) // jobs)
    chunks = [keys[i:i + size] for i in range(0, len(keys), size)]
    with concurrent.futures.ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("spawn")) as pool:
        parts = list(pool.map(_noise_chunk, repeat(X), repeat(B), repeat(F2), chunks))
    return np.array([ratio for part in parts for ratio in part])


def info_ratio(A, sigmas):
    """N2 per direction column: (1/2) mean_t a_t'S_t^-1 a_t over (1/2) a_bar' S_bar^-1 a_bar, S_bar = mean_t S_t."""
    q = s_sum = a_sum = 0.0
    n = 0
    for a, S in zip(A, sigmas):
        q = q + np.einsum("nm,nm->m", a, np.linalg.solve(S, a))
        s_sum, a_sum, n = s_sum + S, a_sum + a, n + 1
    a_bar = a_sum / n
    i_cond, i_stat = 0.5 * q / n, 0.5 * np.einsum("nm,nm->m", a_bar, np.linalg.solve(s_sum / n, a_bar))
    return i_cond / i_stat, i_cond, i_stat


def _nu_loss(nu, delta, dim):
    """Minus the multivariate t log-likelihood as a function of nu at a fixed scale matrix (constants dropped)."""
    return -(delta.size * (special.gammaln((nu + dim) / 2) - special.gammaln(nu / 2) - dim / 2 * math.log(nu))
             - (nu + dim) / 2 * np.log1p(delta / nu).sum())


def _mahalanobis(Z, S):
    return (linalg.solve_triangular(np.linalg.cholesky(S), Z.T, lower=True) ** 2).sum(axis=0)


def mvt_nu(Z, max_iter=500, tol=1e-6):
    """ECME fit (Liu & Rubin, 1995) of a zero-location multivariate t to the rows of Z: (nu, iterations, converged)."""
    n, dim = Z.shape
    S, nu = Z.T @ Z / n, 10.0
    for it in range(1, max_iter + 1):
        w = (nu + dim) / (nu + _mahalanobis(Z, S))
        S = (Z * w[:, None]).T @ Z / n
        new = float(optimize.minimize_scalar(_nu_loss, bounds=(2.01, 1000.0), args=(_mahalanobis(Z, S), dim),
                                             method="bounded", options={"xatol": 1e-8}).x)
        done, nu = abs(new - nu) < tol * new, new
        if done:
            return nu, it, True
    return nu, max_iter, False


def t_ratio(nu):
    """Location Fisher information of a Student t over its inverse variance, (nu+1) nu / ((nu+3)(nu-2)); NaN if nu <= 2."""
    return (nu + 1) * nu / ((nu + 3) * (nu - 2)) if nu > 2 else math.nan


def ceiling_rows(d, proj, scales, n_noise=BOOT, jobs=1):
    """Channel ceilings on the window (item 5): N1, N2 with its day-permutation noise, N3 (Student t fits)."""
    X, V, eigval, K = d["X"], d["eigvec"], d["eigval"], d["K"]
    T, N = X.shape
    Z = X @ (V[:, K + 1:] / np.sqrt(eigval[K + 1:]))
    dim = Z.shape[1]

    def row(ceiling, variant, direction, value, **kw):
        return {"dataset": d["name"], "ceiling": ceiling, "variant": variant, "direction": direction, "value": value,
                "i_cond": math.nan, "i_static": math.nan, "nu": math.nan, "iterations": math.nan,
                "converged": math.nan, "n_days": T, "d": dim, **kw}

    raw, corrected = n1(Z)
    rows = [row("N1", "raw", "idio", raw), row("N1", "chi2_corrected", "idio", corrected)]
    a, b = d["seg"]["calib"]
    fit = fit_background(X[a:b], K + 1)
    labels = [f"F1:PC{k + 1}" for k in range(K + 1)]
    F2 = None
    if d["C"] is not None:
        F2 = gls_residual(d["C"].transpose(0, 2, 1).reshape(-1, N), fit["B"], fit["psi"])
        F2 = F2.reshape(T, -1, N).transpose(0, 2, 1)
        labels += [f"F2:{c.removeprefix('c_')}" for c in d["chars"]]
    ratio, i_cond, i_stat = info_ratio(_directions(fit["B"], F2, T), rolling_lw(X))
    rows += [row("N2", "lw60", label, r, i_cond=ic, i_static=ist, n_days=T - LW_DAYS, d=N)
             for label, r, ic, ist in zip(labels, ratio, i_cond, i_stat)]
    keys = [[STREAM, 11, zlib.crc32(d["name"].encode()), b] for b in range(n_noise)]
    noise = np.median(n2_noise(X, fit["B"], F2, keys, jobs), axis=0)
    for variant, values in (("lw60_shuffle", noise), ("lw60_net", ratio / noise)):
        rows += [row("N2", variant, label, v, n_days=T - LW_DAYS, d=N) for label, v in zip(labels, values)]
    sigma = np.column_stack([garch_scale(Z[:, k])[0] for k in range(dim)])
    for variant, data in (("mvt_static", Z), ("mvt_garch", Z / sigma)):
        nu, iterations, converged = mvt_nu(data)
        rows.append(row("N3", variant, "idio", t_ratio(nu), nu=nu, iterations=iterations, converged=converged))
    for label, y in proj.items():
        nu = float(stats.t.fit(y / scales[label][0], floc=0)[0])
        rows.append(row("N3", "t_garch", label, t_ratio(nu), nu=nu, d=1))
    return rows


def budget_rows(drift):
    """Share of dated phases with L * I_hat >= ln(gamma), L = n2, I_hat = sr2_debiased / 504 (budget reading; item 6)."""
    tr = drift[(drift.level == "transition") & drift.subspace.isin(AGGREGATES)]
    rows = []
    for (name, dating, subspace), g in tr.groupby(["dataset", "dating", "subspace"], sort=False):
        evidence = g.n2.to_numpy() * g.sr2_debiased.to_numpy() / (2 * fl.TRADING_DAYS)
        for gamma in GAMMAS:
            k = int((evidence >= math.log(gamma)).sum())
            rows.append({"dataset": name, "dating": dating, "subspace": subspace, "gamma": gamma,
                         "n_phases": len(g), "n_in_budget": k, "share": k / len(g)})
    return rows


def planning_gains(N, K, rho, rho_sign, sr2_m, sr2_f, sr2_i, gamma):
    """Section 2.4 gains (one equicorrelated factor) on the estimates; a median <= 0 gives NaN, never a planning value."""
    def tax(D):
        return fl.mixture_multiplier(D, gamma)

    pool = N / (1 + (N - 1) * rho)
    g_f1 = sr2_f / sr2_m if sr2_m > 0 and sr2_f > 0 else math.nan
    kappa2 = (sr2_i / sr2_m) * (1 - rho) / (1 + (N - 1) * rho) if sr2_m > 0 and sr2_i > 0 else math.nan
    g_f2 = kappa2 * (1 + (N - 1) * rho) / (1 - rho)
    base = {"gamma": gamma, "N": N, "K": K, "rho_ret": rho, "rho_sign": rho_sign, "kappa_hat": math.sqrt(kappa2),
            "sr2_market": sr2_m, "sr2_factor": sr2_f, "sr2_idio": sr2_i, "D_A": 1}
    return [
        {"step": "1-2:F3", **base, "D_B": 1, "M_A": tax(1), "M_B": tax(1), "G_floor": pool,
         "G_floor_sign": N / (1 + (N - 1) * rho_sign), "G_tax": pool},
        {"step": "2-3:F1", **base, "D_B": K, "M_A": tax(1), "M_B": tax(K), "G_floor": g_f1, "G_floor_sign": math.nan,
         "G_tax": g_f1 * tax(1) / tax(K)},
        {"step": "2-3:F2", **base, "D_B": N - 1, "M_A": tax(1), "M_B": tax(N - 1), "G_floor": g_f2,
         "G_floor_sign": math.nan, "G_tax": g_f2 * tax(1) / tax(N - 1)},
        {"step": "1-3:F3+F2", **base, "D_B": math.nan, "M_A": tax(1), "M_B": math.nan,
         "G_floor": pool + kappa2 * N / (1 - rho), "G_floor_sign": math.nan, "G_tax": math.nan},
    ]


def predicted_rows(signs, drift, dims):
    """predicted_gains.csv: planning_gains per dataset, dating and gamma on rho over the window and median SR^2 (item 7)."""
    med = drift[drift.level == "median"].set_index(["dataset", "dating", "subspace"]).sr2_debiased
    rows = []
    for name, (N, K) in dims.items():
        w = signs[(signs.dataset == name) & (signs.segment == "window")].iloc[0]
        for dating in DATINGS:
            sr2 = [float(med.get((name, dating, s), math.nan)) for s in ("market", "factor", "idio")]
            for gamma in GAMMAS:
                rows += [{"dataset": name, "dating": dating, **r}
                         for r in planning_gains(N, K, float(w.rho_ret), float(w.rho_sign), *sr2, gamma)]
    return rows


def _save(plt, fig, fig_dir, stem):
    fig.tight_layout()
    fig.savefig(fig_dir / f"{stem}.png", dpi=150)
    fig.savefig(fig_dir / f"{stem}.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def plot(out, fig_dir):
    """Four figures drawn from the CSVs of `out` only, PNG + PDF: spectrum and eta, symmetry, drift Sharpe, budget."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
                         "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "axes.titlesize": 8})
    spec, eta, sym, drift, budget = (pd.read_csv(out / f"{stem}.csv", float_precision="round_trip") for stem in
                                     ("spectrum", "eta_by_year", "symmetry_tests", "drift_sharpe_transitions",
                                      "budget_share"))
    fig_dir.mkdir(parents=True, exist_ok=True)
    names, datings = list(dict.fromkeys(spec.dataset)), list(dict.fromkeys(drift.dating))

    fig, axes = plt.subplots(3, len(names), figsize=(3.6 * len(names), 7.5), squeeze=False)
    for c, name in enumerate(names):
        s, e = spec[spec.dataset == name], eta[eta.dataset == name]
        for color, matrix, label in ((SERIES[0], "cov_sample", "sample"), (SERIES[1], "cov_lw", "Ledoit-Wolf")):
            g = s[s.matrix == matrix]
            axes[0, c].plot(g["rank"], g.share, color=color, lw=1.2, label=label)
        axes[0, c].set(yscale="log", xlabel="rank", ylabel="share of the trace", title=f"{name}: calib covariance")
        g = s[s.matrix == "corr_sample"]
        axes[1, c].plot(g["rank"], g.eigval, color=SERIES[0], lw=1.2, marker="o", ms=2)
        axes[1, c].axhline(g.mp_edge.iloc[0], color=MUTED, lw=1, ls="--")
        axes[1, c].set(xscale="log", yscale="log", xlabel="rank", ylabel="eigenvalue",
                       title=f"{name}: correlation, MP edge {g.mp_edge.iloc[0]:.3f}, K = {g.K.iloc[0]}")
        for color, col, label in ((SERIES[0], "eta_sample", "sample"), (SERIES[1], "eta_lw", "Ledoit-Wolf")):
            axes[2, c].plot(e.year, e[col], color=color, lw=1.2, marker="o", ms=3, label=label)
        axes[2, c].set(xlabel="year", ylabel="eta = lambda_1 / tr Sigma", title=f"{name}: eta by calendar year")
        axes[0, c].legend()
        axes[2, c].legend()
    _save(plt, fig, fig_dir, "spectrum")

    fig, axes = plt.subplots(len(names), 2, figsize=(10, 2.9 * len(names)), squeeze=False)
    for r, name in enumerate(names):
        g = sym[sym.dataset == name].reset_index(drop=True)
        x = np.arange(len(g))
        panels = ((g.q_hat - 0.5, 1.96 * 0.5 / math.sqrt(g.n.max()), g.binom_reject, "q_hat - 1/2, exact binomial test"),
                  (g.triples_z, 1.96, g.triples_reject, "triples z on u'x / sigma_{t|t-1}"))
        for ax, (value, band, reject, title) in zip(axes[r], panels):
            reject = reject.to_numpy(dtype=bool)
            ax.axhspan(-band, band, color=GRID, lw=0)
            ax.axhline(0, color=MUTED, lw=0.8)
            ax.scatter(x[~reject], value[~reject], s=16, facecolors="none", edgecolors=SERIES[0], lw=1,
                       label="not rejected")
            ax.scatter(x[reject], value[reject], s=16, color=SERIES[0], label="rejected (Holm, 5 %)")
            ax.set_xticks(x, g.direction, rotation=90, fontsize=6)
            ax.set_title(f"{name}: {title} (band: 95 % under symmetry)")
        axes[r, 0].legend()
    _save(plt, fig, fig_dir, "symmetry")

    fig, axes = plt.subplots(len(names), len(datings), figsize=(3.6 * len(datings), 3.3 * len(names)), squeeze=False)
    for r, name in enumerate(names):
        for c, dating in enumerate(datings):
            ax = axes[r, c]
            g = drift[(drift.dataset == name) & (drift.dating == dating) & drift.subspace.isin(AGGREGATES)]
            subs = [s for s in AGGREGATES if s in set(g.subspace)]
            for k, s in enumerate(subs):
                t, m = g[(g.subspace == s) & (g.level == "transition")], g[(g.subspace == s) & (g.level == "median")]
                xs = k + (np.linspace(-0.25, 0.25, len(t)) if len(t) > 1 else np.zeros(len(t)))
                ax.vlines(xs, t.ci_lo, t.ci_hi, color=SERIES[0], lw=0.8, alpha=0.5)
                ax.scatter(xs, t.sr2_debiased, s=12, color=SERIES[0], zorder=3, label="transition" if k == 0 else None)
                ax.hlines(m.sr2_debiased, k - 0.35, k + 0.35, color=INK, lw=1.6, label="median" if k == 0 else None)
            ax.axhline(0, color=MUTED, lw=0.8)
            ax.set_yscale("symlog", linthresh=10)
            ax.set_xticks(range(len(subs)), subs, rotation=30, ha="right")
            ax.set_title(f"{name}, {dating}: debiased SR^2, 95 % CI")
        axes[r, 0].legend()
    _save(plt, fig, fig_dir, "drift_sharpe")

    fig, axes = plt.subplots(len(names), len(datings), figsize=(3.6 * len(datings), 2.9 * len(names)), squeeze=False)
    for r, name in enumerate(names):
        for c, dating in enumerate(datings):
            ax = axes[r, c]
            g = budget[(budget.dataset == name) & (budget.dating == dating)]
            subs = [s for s in AGGREGATES if s in set(g.subspace)]
            x = np.arange(len(subs))
            for k, gamma in enumerate(GAMMAS):
                h = g[g.gamma == gamma].set_index("subspace").reindex(subs)
                ax.bar(x + (k - 0.5) * 0.38, h.share, width=0.36, color=SERIES[k], label=f"gamma = {gamma}")
            ax.set_xticks(x, subs, rotation=30, ha="right")
            ax.set(ylim=(0, 1), ylabel="share of phases in budget", title=f"{name}, {dating}: L I_hat >= ln gamma")
        axes[r, 0].legend()
    _save(plt, fig, fig_dir, "budget_share")


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _shown(arg):
    p = Path(arg)
    return str(p.relative_to(REPO_ROOT)) if p.is_absolute() and p.is_relative_to(REPO_ROOT) else str(arg)


def _summary(frames):
    """Log lines: negative debiased estimates (R9), Holm rejections, fit flags, N3 variants and the two caveats."""
    drift, sym, ceil = frames["drift_sharpe_transitions"], frames["symmetry_tests"], frames["channel_ceilings"]
    lines = []
    tr = drift[(drift.level == "transition") & drift.subspace.isin(AGGREGATES)]
    for (name, dating), g in tr.groupby(["dataset", "dating"], sort=False):
        negative = {s: int((h.sr2_debiased < 0).sum()) for s, h in g.groupby("subspace", sort=False)}
        lines.append(f"R9 {name} {dating}: negative sr2_debiased over {g.transition.nunique()} transitions {negative}")
    med = drift[(drift.level == "median") & drift.subspace.isin(AGGREGATES)]
    lines += [f"R9 {r.dataset} {r.dating} median {r.subspace}: {r.sr2_debiased:.4g} [{r.ci_lo:.4g}, {r.ci_hi:.4g}]"
              for r in med.itertuples()]
    for name, g in sym.groupby("dataset", sort=False):
        lines.append(f"symmetry {name}: Holm rejections binomial {g.direction[g.binom_reject].tolist()}, "
                     f"triples {g.direction[g.triples_reject].tolist()}; "
                     f"GARCH not converged {g.direction[~g.garch_converged.astype(bool)].tolist()}")
    for (name, variant), g in ceil[ceil.variant.isin(["lw60", "lw60_shuffle", "lw60_net"])].groupby(
            ["dataset", "variant"], sort=False):
        lines.append(f"N2 {name} {variant}: " + ", ".join(f"{r.direction} {r.value:.3g}" for r in g.itertuples()))
    lines += [f"placebo {r.dataset} {r.dating}: real median {r.sr2_real_median:.4g}, placebo median "
              f"{r.sr2_placebo_median:.4g} [{r.ci_lo:.4g}, {r.ci_hi:.4g}], excess {r.selection_excess:.4g}, "
              f"p {r.p_placebo:.4g}, factor {r.selection_factor:.4g}" for r in frames["placebo_selection"].itertuples()]
    for r in ceil[ceil.variant.isin(["mvt_static", "mvt_garch"])].itertuples():
        cited = " (cited variant)" if r.variant == "mvt_static" else ""
        lines.append(f"N3 {r.dataset} {r.variant}{cited}: nu = {r.nu:.4g}, J/Sigma^-1 = {r.value:.4g}, "
                     f"{int(r.iterations)} ECME iterations, converged {r.converged}")
    lines += ["caveat: phase boundaries are SPY turning points dated ex post; the noise debiasing does not remove this "
              "selection, which inflates the market SR^2",
              "caveat: N2 with a 60-day Ledoit-Wolf Sigma_t also holds the Jensen gap of its estimation noise"]
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", nargs="+", choices=sorted(DATASETS), default=sorted(DATASETS))
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "audit")
    ap.add_argument("--fig-dir", type=Path, default=REPO_ROOT / "figures" / "audit")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "audit")
    ap.add_argument("--boot", type=int, default=BOOT, help="moving-block bootstrap draws per phase")
    ap.add_argument("--jobs", type=int, default=os.cpu_count(), help="processes for the N2 noise backgrounds")
    ap.add_argument("--quick", action="store_true", help="smoke test: 50 draws and rotations, 8 backgrounds, PC1-PC3")
    args = ap.parse_args(argv)
    if args.boot < 1 or args.jobs < 1:
        ap.error("--boot and --jobs must be >= 1")
    B, n_pc, n_noise, P = (50, 3, 8, 50) if args.quick else (args.boot, N_PC, args.boot, args.boot)
    started = time.time()
    shown = " ".join(_shown(a) for a in (sys.argv[1:] if argv is None else argv))
    log = [f"generator: python experiments/audit_information.py {shown}".rstrip(),
           f"window {WINDOW[0]}..{WINDOW[1]}; moving-block bootstrap, blocks of {BLOCK} days, B = {B}; phases >= "
           f"{MIN_PHASE} days; subspace blocks <= {MAX_DIM}; seeds SeedSequence([{STREAM}, crc32(dataset), "
           f"crc32(dating), phase_id]); N2 noise on {n_noise} day-permuted backgrounds; {P} circular rotations of each "
           f"phase chain"]
    tables = {stem: [] for stem in COLUMNS}
    dims = {}
    for name in args.datasets:
        d = load(name)
        X = d["X"]
        dims[name] = (X.shape[1], d["K"])
        log.append(f"{name}: {d['dates'][0]}..{d['dates'][-1]}, {X.shape[0]} days x {X.shape[1]} assets; calib rows "
                   f"{d['seg']['calib']}; K = {d['K']} ({d['n_above']} eigenvalues above the MP edge "
                   f"{d['mp_edge']:.6g}); calib basis {d['state_hash'][:16]} = prompt 6 sidecar")
        inputs = [DERIVED / name / "ret_wide.npy", *sorted((DERIVED / name).glob("z_*.json"))]
        inputs += [DERIVED / name / "chars.parquet"] if d["C"] is not None else []
        log += [f"  sha256 {_shown(path)} {_sha256(path)}" for path in inputs]
        tables["spectrum"] += spectrum_rows(d)
        tables["eta_by_year"] += eta_rows(d)
        tables["sign_corr"] += sign_rows(d)
        proj = projections(d, n_pc)
        scales = {label: garch_scale(y) for label, y in proj.items()}
        tables["symmetry_tests"] += symmetry_rows(name, proj, scales)
        Ys = subspaces(d, proj)
        chains = {}
        for dating in DATINGS:
            phases = spy_phases(dating, d["dates"])
            chains[dating] = [(p[1], p[2]) for p in phases]
            kept = transitions(phases)
            dropped = [f"{phases[i][2]} ({phases[i][3].size}/{phases[i + 1][3].size} days)"
                       for i in range(len(phases) - 1)
                       if WINDOW[0] <= phases[i][2] < WINDOW[1] and (i, i + 1) not in kept]
            log.append(f"  {dating}: {len(kept)} transitions kept, dropped (< {MIN_PHASE} days): "
                       f"{', '.join(dropped) or 'none'}")
            tables["drift_sharpe_transitions"] += drift_rows(name, dating, phases, Ys, B)
            placebo = placebo_rows(name, dating, phases, Ys["market"], P, B)
            if placebo is not None:
                tables["drift_sharpe_transitions"].append(placebo[0])
                tables["placebo_selection"].append(placebo[1])
        log.append(f"  lt_spy and symmetric SPY chains identical in the window: {chains['lt_spy'] == chains['symmetric']}")
        tables["channel_ceilings"] += ceiling_rows(d, proj, scales, n_noise, args.jobs)
    frames = {stem: pd.DataFrame(rows, columns=COLUMNS[stem]) for stem, rows in tables.items()}
    frames["budget_share"] = pd.DataFrame(budget_rows(frames["drift_sharpe_transitions"]),
                                          columns=COLUMNS["budget_share"])
    frames["predicted_gains"] = pd.DataFrame(predicted_rows(frames["sign_corr"], frames["drift_sharpe_transitions"],
                                                            dims), columns=COLUMNS["predicted_gains"])
    args.out.mkdir(parents=True, exist_ok=True)
    for stem, df in frames.items():
        save_fair_csv(df, args.out / f"{stem}.csv")
    plot(args.out, args.fig_dir)
    log += _summary(frames)
    log.append(f"duration {time.time() - started:.0f} s")
    log += [f"sha256 {stem}.csv {_sha256(args.out / f'{stem}.csv')}" for stem in COLUMNS]
    args.log_dir.mkdir(parents=True, exist_ok=True)
    (args.log_dir / "audit.log").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
