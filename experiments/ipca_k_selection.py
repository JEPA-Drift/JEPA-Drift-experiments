"""Stream 17 (plan H12, R6): IPCA K selection on calib and characteristic audit, rows before 2020-01-01 only.

`python experiments/ipca_k_selection.py --out results/ipca --log-dir logs/ipca` writes k_selection.csv (one row per
dataset, protocol, cash-neutral variant and candidate K) and char_audit.csv (long: dataset, segment, metric, value).
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"
os.environ["MPLBACKEND"] = "Agg"

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift.data_loader import chars, sp500
from jepadrift.pipelines import save_fair_csv, split_rows
from jepadrift.representations.extract import CHAR_DATASETS, DATASETS
from jepadrift.representations.ipca import IPCA

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD = np.datetime64("2020-01-01")
PANELS = ("d3_239", "d3_500", "d4_eurofidai")
GICS_PANELS = ("d3_239", "d3_500")
SEGMENTS = ("pretrain", "calib")


def load_panel(dataset):
    """(ret, X, dates, splits) on the rows [0, calib end), X = ret where in_universe else NaN; refuses rows >= 2020."""
    load, load_splits = {**DATASETS, **CHAR_DATASETS}[dataset]
    ret, dates, _ = load()
    rows = slice(0, split_rows(dates, load_splits(dataset))["calib"][1])
    if not dates[rows][-1] < GUARD:
        raise SystemExit(f"pre-J4 guard: {dataset} rows reach {dates[rows][-1]} >= {GUARD}")
    ret, dates = ret[rows], dates[rows]
    return ret, np.where(chars.load_universe(dataset, rows), ret, np.nan), dates, split_rows(dates, load_splits(dataset))


def fit_ipca(X, C, dates, splits, **kw):
    """IPCA(**kw) pretrained on the pretrain rows and fitted on the calib rows of splits."""
    (p0, p1), (c0, c1) = splits["pretrain"], splits["calib"]
    return IPCA(**kw).pretrain(X[p0:p1], C[p0:p1], dates[p0:p1]).fit(X[c0:c1], C[c0:c1], dates[c0:c1])


def k_rows(dataset, protocol, names, rep):
    """One k_selection.csv row per candidate K of a fitted K="select" representation."""
    st, pre, cn = rep.stats, rep.pretrain_info, rep.config["cash_neutral"]
    for j, k in enumerate(st["candidates"]):
        run = pre["als"][str(k)]
        yield {"dataset": dataset, "protocol": protocol, "chars": "+".join(names), "cash_neutral": cn or "none",
               "r2_target": st["r2_target"], "K": k, "selected": k == st["K"],
               "r2_heldout_calib": st["r2_heldout_calib"][j], "r2_insample_calib": st["r2_insample_calib"][j],
               "r2_insample_pretrain": run["r2_insample"], "days_pretrain": pre["used_days"],
               "days_calib": st["used_days_calib"], "excluded_pretrain": len(pre["excluded"]),
               "excluded_calib": len(st["excluded_calib"]), "fold_skips": st["fold_skips"][j],
               "c_nan_imputed_pretrain": pre["c_nan_imputed"], "c_nan_imputed_calib": st["c_nan_imputed_calib"],
               "als_iterations": run["iterations"], "projector_change": run["projector_change"],
               "min_rcond_calib": st["min_rcond_calib"][j], "n_assets": rep.n_assets, "state_sha256": rep.state_hash()}


def rank_cs(raw):
    """Cross-sectional rank transform of sp500._compute_chars: average ranks / finite count - 0.5, NaN kept."""
    df = pd.DataFrame(raw)
    return (df.rank(axis=1, method="average", na_option="keep").div(df.notna().sum(axis=1), axis=0) - 0.5).to_numpy(
        dtype=np.float64)


def betas(ret, valid):
    """Raw beta_252 with the stored denominator sum m^2 - (sum r)^2 / n and with the OLS one sum m^2 - (sum m)^2 / n,
    as in sp500._compute_chars; plus the cells whose stored denominator is negative (n >= 126)."""
    mkt = sp500._market_return(ret, valid)
    stored, ols = np.full(ret.shape, np.nan), np.full(ret.shape, np.nan)
    negative = np.zeros(ret.shape, dtype=bool)
    for j in range(ret.shape[1]):
        sr, sm, srm, sm2, cnt = sp500._rolling_xy_sums(ret[:, j], mkt, valid[:, j], 252)
        n = np.maximum(cnt, 1)
        numer = srm - sr * sm / n
        for out, denom in ((stored, sm2 - sr ** 2 / n), (ols, sm2 - sm ** 2 / n)):
            with np.errstate(divide="ignore", invalid="ignore"):
                out[:, j] = np.where((cnt >= 126) & (denom > 1e-15), numer / denom, np.nan)
        negative[:, j] = (cnt >= 126) & (sm2 - sr ** 2 / n < 0)
    return stored, ols, negative


def char_audit(dataset, ret, X, splits):
    """char_audit.csv rows: beta denominator (Q2) and phantom ranks (Q9) per segment."""
    C = chars.load_continuous_chars(dataset, slice(0, len(ret)))
    valid = np.isfinite(X)
    raw_stored, raw_ols, negative = betas(ret, valid)
    rank_stored, rank_ols = rank_cs(raw_stored), rank_cs(raw_ols)
    out = []
    for seg in SEGMENTS:
        rows = slice(*splits[seg])
        s, f, o, rf, ro = C[rows, :, 0], rank_stored[rows], rank_ols[rows], raw_stored[rows], raw_ols[rows]
        both = np.isfinite(rf) & np.isfinite(ro)
        nz = both & (ro != 0)
        rel = np.abs(rf[nz] - ro[nz]) / np.abs(ro[nz])
        ranked = np.isfinite(f) & np.isfinite(o)
        metrics = {"beta_cells": s.size, "beta_stored_finite": int(np.isfinite(s).sum()),
                   "beta_reproduction_mismatch": int((~((f == s) | (np.isnan(f) & np.isnan(s)))).sum()),
                   "beta_rel_error_median": float(np.median(rel)), "beta_rel_error_p99": float(np.quantile(rel, 0.99)),
                   "beta_rel_error_max": float(rel.max()), "beta_ols_zero_cells": int((both & (ro == 0)).sum()),
                   "beta_rank_changed_share": float((f[ranked] != o[ranked]).mean()),
                   "beta_rank_shift_max": float(np.abs(f[ranked] - o[ranked]).max()),
                   "beta_nan_from_formula": int((np.isnan(rf) & np.isfinite(ro)).sum()),
                   "beta_negative_denominators": int(negative[rows].sum())}
        obs = valid[rows]
        for p, name in enumerate(sp500.CONTINUOUS_CHARS):
            c = C[rows, :, p]
            seen = np.where(obs & np.isfinite(c), c, np.nan)
            days = np.isfinite(seen).any(axis=1)
            metrics[f"phantom_cells_{name}"] = int((np.isfinite(c) & ~obs).sum())
            metrics[f"max_abs_mean_observed_rank_{name}"] = float(np.abs(np.nanmean(seen[days], axis=1)).max())
        out += [{"dataset": dataset, "segment": seg, "metric": k, "value": float(v)} for k, v in metrics.items()]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="IPCA K selection on calib and characteristic audit (rows < 2020).")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "ipca")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "ipca")
    args = ap.parse_args(argv)
    selection, audit = [], []
    lines = ["generator: python experiments/ipca_k_selection.py --out results/ipca --log-dir logs/ipca",
             "rows: [0, calib end) of each panel, all before 2020-01-01; Gamma on pretrain, K and R^2 on calib"]
    for dataset in PANELS:
        ret, X, dates, splits = load_panel(dataset)
        C = chars.load_continuous_chars(dataset, slice(0, len(ret)))
        groups = [("principal", list(sp500.CONTINUOUS_CHARS), C, cn, 4) for cn in (None, "constant")]
        if dataset in GICS_PANELS:
            C15, names = chars.load_chars_tensor(dataset, slice(0, len(ret)))
            groups.append(("retrospective_gics_static", names, C15, None, 6))
        for protocol, names, Cg, cn, K_max in groups:
            rep = fit_ipca(X, Cg, dates, splits, K_max=K_max, cash_neutral=cn)
            selection += list(k_rows(dataset, protocol, names, rep))
            lines.append(f"{dataset} {protocol} P={Cg.shape[2]} cash_neutral={cn or 'none'} "
                         f"target={rep.stats['r2_target']} K*={rep.stats['K']} r2_heldout="
                         + " ".join(f"{r:.4f}" for r in rep.stats["r2_heldout_calib"]))
        audit += char_audit(dataset, ret, X, splits)
    args.out.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    save_fair_csv(pd.DataFrame(selection), args.out / "k_selection.csv")
    save_fair_csv(pd.DataFrame(audit), args.out / "char_audit.csv")
    lines.append(f"rows written: k_selection.csv {len(selection)}, char_audit.csv {len(audit)}")
    (args.log_dir / "k_selection.log").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
