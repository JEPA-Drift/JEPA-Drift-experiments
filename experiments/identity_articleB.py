"""Identity controls against the Article B reference code (prompt 04, item 8; prompt 07, item 3).

R01: the six output tables of exp_R01_real_world_backtest.py (phases 1-3, l.257-416) are rebuilt with the ported
primitives and the P1 constants, from the D1 loader (blocking control) and, as a diagnostic, from Article B's derived
CSVs read as R01 l.249 reads them. R08: the exact_level column of R08_lattice_exact_law.csv is recomputed by
jepadrift.monitors.lattice. R15 (b): the frozen compositions, the RNG-free diagnostics and, with R15's own seeds,
lambda_boot, FPR_boot and the race at c = 0.25 are recomputed from the D2 loader for K in {5, 10, 20}. Every cell is
compared; the rows of the running environment replace its previous rows in results/identity/articleB_R01_R08.csv and
results/identity/articleB_R15.csv, and logs/identity/identity_articleB_<env>.log summarises them.

Usage: python experiments/identity_articleB.py
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift.data_loader.articleB import ARTICLE_B, ARTICLE_B_REF, _article_b_commit, load_d1, load_d2
from jepadrift.monitors import lattice
from jepadrift.monitors.calibration import bootstrap_threshold, worker_null_window_real, worker_race_h1_real
from jepadrift.monitors.cusum import P1, get_cusum_trajectory, get_multiple_alarms, strict_cusum
from jepadrift.monitors.streams import energy_stream, label_stream
from jepadrift.pipelines import H_DET, H_REF, N_CAL, TARGET_FPR, composition_for, save_fair_csv, sign_diagnostics
from jepadrift.stats.garch import compute_gamma_exact, fit_garch_qmle

pd.set_option("compute.use_bottleneck", False)
pd.set_option("compute.use_numexpr", False)

REPO_ROOT = Path(__file__).resolve().parents[1]
R01_DATA = ARTICLE_B / "results" / "R01_real_world_backtest" / "data"
R08_CSV = ARTICLE_B / "results" / "R08_adverse_lattice" / "data" / "R08_lattice_exact_law.csv"
TICKERS = ("SPY", "PFF", "VNQ", "BWX")
R01_SOURCES = ("R01_garch_models", "R01_covid_alarms", "R01_covid_trajectories",
               "R01_placebo_control", "R01_injection_summary", "R01_magnitude_sweep")
INPUTS = ("d1_loader", "articleB_csv")
DATA_SOURCE = "firstrate"
LB_LAG, LB_LEVEL = 20, 0.05
COVID_WINDOW = ("2020-01-02", "2020-12-31")
INJECTION_WINDOW = ("2021-01-01", "2023-12-31")
HORIZON = 250
DELTAS = [0.0, 0.5, 1.0, 1.5]
R08_DELTA = 0.1
REL_TOL = 1e-12
PACKAGES = ("numpy", "scipy", "pandas", "statsmodels")
BLAS_SENSITIVE = ("lb_pvalue_warmup",)
COLUMNS = ["env", "input", "source", "row", "column", "reference", "reproduced", "rel_diff", "bit_identical", "pass"]
R15_DATA = ARTICLE_B / "results" / "R15_cross_sectional" / "data"
R15_K_GRID = (1, 5, 10, 20, 30, 40, 50, 60, 75, 97)
R15_C_GRID = (0.10, 0.25, 0.50, 0.75, 1.0)
R15_C_INDEX = 1
N_RACE = 2000


def wilson_ci(p_hat, n, z=1.96):
    if n == 0: return 0.0, 0.0
    center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
    half_width = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(0.0, min(1.0, center - half_width)), max(0.0, min(1.0, center + half_width))


def r01_frames(input_mode):
    """Per-ETF daily frames (index Date, column log_ret) from the D1 loader, or from Article B's CSVs as R01 reads them."""
    if input_mode == "d1_loader":
        ret, dates, assets = load_d1()
        frames = {}
        for j, tk in enumerate(assets):
            keep = ~np.isnan(ret[:, j])
            frames[tk] = pd.DataFrame({"log_ret": ret[keep, j]},
                                      index=pd.DatetimeIndex(dates[keep].astype("datetime64[ns]"), name="Date"))
        return frames
    if input_mode == "articleB_csv":
        return {tk: pd.read_csv(ARTICLE_B / "data" / "derived_firstrate" / f"R01_daily_{tk}.csv",
                                index_col="Date", parse_dates=True) for tk in TICKERS}
    raise ValueError(f"input_mode must be one of {INPUTS}, got {input_mode!r}")


def r01_models(frames):
    """R01 phase 1 (l.257-290): warm-up moments, q_hat, Ljung-Box gate and GARCH QMLE per ETF."""
    info, rows = {}, []
    for tk in TICKERS:
        df = frames[tk]
        r_wu = df.loc[slice(*P1["P1-D/B"]["gamma_hat_window"])]["log_ret"].values
        mu_f = np.mean(r_wu**2)
        sig_f = np.std(r_wu**2)
        q_hat = np.mean(r_wu > 0)
        p_val = acorr_ljungbox(label_stream(r_wu, q_hat), lags=[LB_LAG], return_df=True)["lb_pvalue"].iloc[0]
        (w, a, b), converged = fit_garch_qmle(r_wu - np.mean(r_wu))
        gamma = compute_gamma_exact(a, b)
        sig2_unc = w / (1 - a - b)
        info[tk] = {"mu_f": mu_f, "sig_f": sig_f, "q_hat": q_hat, "gamma": gamma, "sig_unc": np.sqrt(sig2_unc),
                    "concept_valid": p_val >= LB_LEVEL}
        rows.append({"data_source": DATA_SOURCE, "Ticker": tk, "omega": w, "alpha": a, "beta": b, "gamma_hat": gamma,
                     "sigma_unc": np.sqrt(sig2_unc), "q_hat": q_hat, "lb_pvalue_warmup": p_val,
                     "qmle_converged": converged, "data_start": df.index[0].strftime("%Y-%m-%d"),
                     "data_end": df.index[-1].strftime("%Y-%m-%d"), "n_days": len(df), "n_truncated_windows": 0})
    return info, pd.DataFrame(rows)


def injection_streams(frames, info):
    """R01 phase 3 streams (l.350-378): monthly onsets 2021-2023, trailing moments, shifted 250-day test streams."""
    trailing = P1["P1-C/B"]["trailing_days"]
    out = []
    for tk in TICKERS:
        df, m = frames[tk], info[tk]
        period = df.loc[slice(*INJECTION_WINDOW)]
        onsets = period.groupby([period.index.year, period.index.month]).head(1).index
        for onset in onsets:
            idx = df.index.get_loc(onset)
            df_wu = df.iloc[idx - trailing: idx]
            df_test = df.iloc[idx: idx + HORIZON]
            mu_loc = df_wu["log_ret"].pow(2).mean()
            sig_loc = max(df_wu["log_ret"].pow(2).std(), 1e-8)
            q_loc = (df_wu["log_ret"] > 0).mean()
            for delta_f in DELTAS:
                r_test = df_test["log_ret"].values + delta_f * m["sig_unc"]
                out.append({"ticker": tk, "onset": onset, "n_onsets": len(onsets), "delta_f": delta_f,
                            "energy": energy_stream(r_test, mu_loc, sig_loc), "label": label_stream(r_test, q_loc),
                            "thr_data": P1["P1-D/B"]["lambda_iid"] * m["gamma"]})
    return out


def replicate_r01(frames):
    """The six R01 output tables (l.257-416) rebuilt with the ported primitives and the P1 constants."""
    cb, db = P1["P1-C/B"], P1["P1-D/B"]
    info, models = r01_models(frames)

    covid = frames["SPY"].loc[slice(*COVID_WINDOW)]
    r_cov = covid["log_ret"].values
    m = info["SPY"]
    thr_data = db["lambda_iid"] * m["gamma"]
    e_cov = energy_stream(r_cov, m["mu_f"], m["sig_f"])
    s_cov = label_stream(r_cov, m["q_hat"])
    al_data = get_multiple_alarms(e_cov, delta_P=db["delta"], threshold=thr_data, bilateral=db["bilateral"])
    al_conc = (get_multiple_alarms(s_cov, delta_P=cb["delta"], threshold=cb["threshold"], bilateral=cb["bilateral"])
               if m["concept_valid"] else [])
    traj_conc = (np.maximum(get_cusum_trajectory(s_cov, cb["delta"]) / cb["threshold"],
                            get_cusum_trajectory(-s_cov, cb["delta"]) / cb["threshold"])
                 if m["concept_valid"] else np.zeros(len(e_cov)))
    trajectories = pd.DataFrame({"data_source": DATA_SOURCE, "Date": covid.index,
                                 "S_over_thr_Data": get_cusum_trajectory(e_cov, db["delta"]) / thr_data,
                                 "S_over_thr_Concept": traj_conc})
    close = covid["Close"] if "Close" in covid else pd.Series(np.nan, index=covid.index)
    alarms = pd.DataFrame([{"data_source": DATA_SOURCE, "Pipeline": name, "Date": covid.index[i], "Close": close.iloc[i]}
                           for name, idx in (("Data", al_data), ("Concept", al_conc)) for i in idx],
                          columns=["data_source", "Pipeline", "Date", "Close"])
    if alarms.empty:
        alarms = pd.DataFrame([{"data_source": DATA_SOURCE, "Pipeline": float("nan"), "Date": pd.NaT, "Close": np.nan,
                                "n_alarms": 0}])
    else:
        alarms["n_alarms"] = len(alarms)

    delays, n_onsets = {}, {}
    for rec in injection_streams(frames, info):
        n_onsets[rec["ticker"]] = rec["n_onsets"]
        data, concept = delays.setdefault((rec["ticker"], rec["delta_f"]), ([], []))
        d_al = strict_cusum(rec["energy"], db["delta"], rec["thr_data"])
        if d_al != -1:
            data.append(d_al)
        if info[rec["ticker"]]["concept_valid"]:
            valid = [x for x in (strict_cusum(rec["label"], cb["delta"], cb["threshold"]),
                                 strict_cusum(-rec["label"], cb["delta"], cb["threshold"])) if x != -1]
            if valid:
                concept.append(min(valid))

    placebo, sweep, summary = [], [], []
    for tk in TICKERS:
        n = n_onsets[tk]
        for delta_f in DELTAS:
            for pipeline, add in zip(("Data", "Concept"), delays[(tk, delta_f)]):
                if pipeline == "Concept" and not info[tk]["concept_valid"]:
                    continue
                rate = len(add) / n
                ci_low, ci_high = wilson_ci(rate, n)
                med = np.median(add) if len(add) > 0 else np.nan
                add_mean = np.mean(add) if len(add) > 0 else np.nan
                sem = (np.std(add, ddof=1) / np.sqrt(len(add))) if len(add) > 1 else 0.0
                if delta_f == 0.0:
                    placebo.append({"data_source": DATA_SOURCE, "ETF": tk, "Pipeline": pipeline, "AlarmRate": rate,
                                    "CI_low": ci_low, "CI_high": ci_high, "N_alarms": len(add), "MedianDelay": med})
                else:
                    sweep.append({"data_source": DATA_SOURCE, "ETF": tk, "DeltaFactor": delta_f, "Pipeline": pipeline,
                                  "DetRate": rate, "CI_low": ci_low, "CI_high": ci_high, "ADD": add_mean, "SEM": sem})
                if delta_f == 1.5:
                    summary.append({"data_source": DATA_SOURCE, "ETF": tk, "Pipeline": pipeline, "DetRate": rate,
                                    "ADD": add_mean, "SEM": sem})
    return {"R01_garch_models": models, "R01_covid_alarms": alarms, "R01_covid_trajectories": trajectories,
            "R01_placebo_control": pd.DataFrame(placebo), "R01_injection_summary": pd.DataFrame(summary),
            "R01_magnitude_sweep": pd.DataFrame(sweep)}


def _canon(v):
    if v is None or v is pd.NaT:
        return float("nan")
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return float(v)
    if isinstance(v, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(v).strftime("%Y-%m-%d")
    return str(v)


def _text(v):
    if isinstance(v, float):
        return "NaN" if np.isnan(v) else repr(v)
    return str(v)


def _cell(source, row, column, ref, new):
    a, b = _canon(ref), _canon(new)
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (a, b)):
        fa, fb = float(a), float(b)
        bit = fa == fb or (np.isnan(fa) and np.isnan(fb))
        if bit:
            rel = 0.0
        elif np.isnan(fa) or np.isnan(fb) or fa == 0.0:
            rel = float("inf")
        else:
            rel = abs(fb - fa) / abs(fa)
        passed = bit or rel <= REL_TOL
    else:
        bit = passed = a == b
        rel = float("nan")
    return {"source": source, "row": row, "column": column, "reference": _text(a), "reproduced": _text(b),
            "rel_diff": rel, "bit_identical": bool(bit), "pass": bool(passed)}


def compare_frames(source, ref, new):
    """Cell-by-cell comparison of a reproduced table with its Article B reference (same columns and row order)."""
    if list(new.columns) != list(ref.columns) or len(new) != len(ref):
        return pd.DataFrame([{"source": source, "row": -1, "column": "<shape>",
                              "reference": f"{ref.shape} {list(ref.columns)}",
                              "reproduced": f"{new.shape} {list(new.columns)}",
                              "rel_diff": float("nan"), "bit_identical": False, "pass": False}])
    return pd.DataFrame([_cell(source, i, col, ref[col].iloc[i], new[col].iloc[i])
                         for i in range(len(ref)) for col in ref.columns])


def r08_rows():
    """exact_level of R08_lattice_exact_law.csv recomputed by the bilateral strict lattice chain."""
    ref = pd.read_csv(R08_CSV, float_precision="round_trip")
    a, b, _ = lattice.lattice_steps(R08_DELTA)
    return pd.DataFrame([_cell("R08_lattice_exact_law", i, "exact_level", r.exact_level,
                               lattice.exceedance(int(r.H), int(r.lambda_units), a, b, q=float(r.q)))
                         for i, r in enumerate(ref.itertuples(index=False))])


def identity_table(inputs=INPUTS):
    """Long table of every compared cell, for the running environment."""
    refs = {s: pd.read_csv(R01_DATA / f"{s}.csv", float_precision="round_trip") for s in R01_SOURCES}
    parts = []
    for mode in inputs:
        new = replicate_r01(r01_frames(mode))
        parts += [compare_frames(s, refs[s], new[s]).assign(input=mode) for s in R01_SOURCES]
    parts.append(r08_rows().assign(input="n/a"))
    return pd.concat(parts, ignore_index=True).assign(env=Path(sys.prefix).name.lstrip("."))[COLUMNS]


def get_deterministic_seed(*args) -> int:
    """
    Derives a 128-bit collision-free seed from the semantic coordinates of a
    task, returned as a scalar integer so no entropy is discarded. This is the
    repository's canonical form, carried from exp_R11_multi_detector.py.

    Floats are formatted through .hex() rather than str(): the decimal repr of a
    float is platform-dependent at the last digit on some C libraries, which
    would silently re-key a cell across machines. The native hash() is randomly
    salted and is forbidden outright (§1.2).
    """
    def format_arg(arg):
        if isinstance(arg, (float, np.floating)):
            return float(arg).hex()
        return str(arg)

    s = "_".join(map(format_arg, args))
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)


def _r15_rng(*key):
    return np.random.default_rng(np.random.SeedSequence(get_deterministic_seed(*key)))


def r15_rows(ks=(5, 10, 20), bootstrap=True, race=True):
    """R15 (b) cells from the D2 loader: compositions, RNG-free diagnostics and, with R15's seeds, bootstrap and race."""
    eps_real_full = load_d2()[0].T
    comp = pd.read_csv(R15_DATA / "R15_panel_composition.csv", float_precision="round_trip")
    diag = pd.read_csv(R15_DATA / "R15_panel_diagnostics.csv", float_precision="round_trip").set_index("K")
    race_ref = pd.read_csv(R15_DATA / "R15_cross_sectional_race.csv", float_precision="round_trip")
    cells = []
    for K in ks:
        k_index = R15_K_GRID.index(K)
        idx = composition_for(K, eps_real_full.shape[0])
        ref_idx = comp[comp["K"] == K].sort_values("position")["asset_index"].to_numpy()
        cells += [_cell("R15_panel_composition", K, f"position_{j}", int(a), int(b))
                  for j, (a, b) in enumerate(zip(ref_idx, idx))]
        eps_K_full = eps_real_full[idx, :]
        diagnostics = sign_diagnostics(eps_K_full)
        cells += [_cell("R15_panel_diagnostics", K, col, diag.loc[K, col], diagnostics[name])
                  for col, name in (("rho_sign_meas", "rho_sign"), ("K_eff_meas", "K_eff_meas"),
                                    ("K_eff_ana", "K_eff_ana"))]
        if not bootstrap:
            continue
        cal = [worker_null_window_real(_r15_rng("boot_calib", k_index, i), eps_K_full, H_REF, H_DET)
               for i in range(N_CAL)]
        lam_boot = bootstrap_threshold(cal, TARGET_FPR)
        held = [worker_null_window_real(_r15_rng("fpr_window", k_index, i), eps_K_full, H_REF, H_DET)
                for i in range(N_RACE)]
        cells += [_cell("R15_panel_diagnostics", K, "lambda_boot", diag.loc[K, "lambda_boot"], lam_boot),
                  _cell("R15_panel_diagnostics", K, "FPR_boot", diag.loc[K, "FPR_boot"],
                        sum(1 for m in held if m > lam_boot) / N_RACE)]
        if not race:
            continue
        delays = [worker_race_h1_real(_r15_rng("race_h1", k_index, R15_C_INDEX, i), eps_K_full, H_REF, H_DET,
                                      R15_C_GRID[R15_C_INDEX], lam_boot) for i in range(N_RACE)]
        valid = [v for v in delays if v != -1]
        ref = race_ref[(race_ref["K"] == K) & (race_ref["c_index"] == R15_C_INDEX)].iloc[0]
        cells += [_cell("R15_cross_sectional_race", K, "DetRate", ref["DetRate"], len(valid) / len(delays)),
                  _cell("R15_cross_sectional_race", K, "ADD", ref["ADD"], np.mean(valid))]
    return pd.DataFrame(cells).assign(input="d2_loader", env=Path(sys.prefix).name.lstrip("."))[COLUMNS]


def _write_env_rows(frame, path):
    env = frame["env"].iloc[0]
    text = frame.assign(rel_diff=frame["rel_diff"].map(_text), **{"pass": frame["pass"].map(str)}).astype(str)
    if path.exists():
        old = pd.read_csv(path, dtype=str, keep_default_na=False)
        text = pd.concat([old[old["env"] != env], text], ignore_index=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_fair_csv(text.sort_values(["env", "input", "source"], kind="mergesort"), path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "identity" / "articleB_R01_R08.csv")
    ap.add_argument("--out-r15", type=Path, default=REPO_ROOT / "results" / "identity" / "articleB_R15.csv")
    ap.add_argument("--log-dir", type=Path, default=REPO_ROOT / "logs" / "identity")
    args = ap.parse_args(argv)
    r01, r15 = identity_table(), r15_rows()
    env = r01["env"].iloc[0]
    _write_env_rows(r01, args.out)
    _write_env_rows(r15, args.out_r15)
    table = pd.concat([r01, r15], ignore_index=True)

    ok = bool(table.loc[table["input"].isin(["d1_loader", "n/a", "d2_loader"]), "pass"].all())
    lines = ["generator: python experiments/identity_articleB.py",
             f"article_b: {ARTICLE_B_REF} @ {_article_b_commit()} (read-only)",
             f"env: {env}; python {sys.version.split()[0]}; " + "; ".join(f"{p} {version(p)}" for p in PACKAGES),
             f"gate: non-float cells equal; float cells bit-identical or rel_diff <= {REL_TOL:g}; NaN equals NaN"]
    for (inp, src), g in table.groupby(["input", "source"], sort=True):
        lines.append(f"{inp:12s} {src:24s} cells {len(g):5d}  pass {int(g['pass'].sum()):5d}  "
                     f"bit-identical {int(g['bit_identical'].sum()):5d}  max rel_diff {g['rel_diff'].fillna(0.0).max():.3g}")
    for (inp, src, col), g in table[~table["bit_identical"]].groupby(["input", "source", "column"], sort=True):
        lines.append(f"not bit-identical: {inp} {src}.{col}: {len(g)} cells, max rel_diff {g['rel_diff'].max():.3g}")
    lines.append(f"verdict (d1_loader, R08 and R15 rows): {'PASS' if ok else 'FAIL'}")
    args.log_dir.mkdir(parents=True, exist_ok=True)
    (args.log_dir / f"identity_articleB_{env}.log").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
