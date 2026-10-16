"""D1 (ETF-4) and D2 (US-97) panels derived from the Article B repository.

The Article B checkout (~/The-Whitening-Advantage-Experiments, read-only, used
as-is at its current commit) is the sole input. `python -m
jepadrift.data_loader.articleB --build` writes, under data/derived/:

- d1_etf4/: panel.parquet (long format: date, asset_id, ret, close,
  in_universe), ret_wide.npy (float64, NaN outside each series), dates.npy
  (datetime64[D]), assets.json, phases_{lt_spy,strict_ps,symmetric}.csv and
  splits.yaml;
- d2_us97/: the same panel layout (close is NaN: the R15 panel carries log
  returns only) and splits.yaml;
- MANIFEST.json: source path and commit, SHA-256 of every input and output,
  row counts and date ranges;

and results/data/d1_d2_profile.csv (descriptive profile per dataset/segment).
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTICLE_B_REF = "~/The-Whitening-Advantage-Experiments"
ARTICLE_B = Path(ARTICLE_B_REF).expanduser()
DERIVED = REPO_ROOT / "data" / "derived"
RESULTS_DATA = REPO_ROOT / "results" / "data"
LOGS_DATA = REPO_ROOT / "logs" / "data"

D1_DIR = "d1_etf4"
D2_DIR = "d2_us97"
D1_ASSETS = ("SPY", "PFF", "VNQ", "BWX")
D1_EXPECTED = {"SPY": (6414, "2000-01-04"), "PFF": (4403, "2007-12-27"),
               "VNQ": (5014, "2005-01-04"), "BWX": (4451, "2007-10-09")}
D2_SHAPE = (5154, 97)
EMBARGO = 65
PRETRAIN_START = np.datetime64("2005-01-01")
CALIB_START = np.datetime64("2016-01-01")
MONITOR_START = np.datetime64("2020-01-01")

PHASE_VARIANTS = {"lt_spy": "R16_regime_census.csv",
                  "strict_ps": "R16_regime_census_strict_ps.csv",
                  "symmetric": "R16_regime_census_symmetric.csv"}
PHASE_COUNTS = {"lt_spy": 66, "strict_ps": 48, "symmetric": 102}

_DATASET_DIRS = {"d1": D1_DIR, "d2": D2_DIR, D1_DIR: D1_DIR, D2_DIR: D2_DIR}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _article_b_commit():
    out = subprocess.run(["git", "-C", str(ARTICLE_B), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def _as_date(x):
    return pd.Timestamp(x).date()


# ---------------------------------------------------------------- loaders

def _load_wide(out_dir):
    ret = np.load(out_dir / "ret_wide.npy")
    dates = np.load(out_dir / "dates.npy")
    assets = json.loads((out_dir / "assets.json").read_text())
    return ret, dates, assets


def load_d1():
    """D1 (ETF-4): (ret, dates, assets) with ret float64 (T, 4), dates
    datetime64[D] and assets as a list of str. No transformation applied."""
    return _load_wide(DERIVED / D1_DIR)


def load_d2():
    """D2 (US-97 survivors): (ret, dates, assets), same contract as load_d1."""
    return _load_wide(DERIVED / D2_DIR)


def load_phases(variant):
    """D1 regime phases as a DataFrame; variant in {'lt_spy', 'strict_ps',
    'symmetric'} (66, 48 and 102 phases respectively)."""
    if variant not in PHASE_VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {sorted(PHASE_VARIANTS)}")
    return pd.read_csv(DERIVED / D1_DIR / f"phases_{variant}.csv", float_precision="round_trip")


def load_splits(dataset):
    """Split definition of `dataset` ('d1', 'd2' or the directory name) as a
    dict; segment dates are datetime.date objects."""
    if dataset not in _DATASET_DIRS:
        raise ValueError(f"unknown dataset {dataset!r}; expected one of {sorted(_DATASET_DIRS)}")
    return yaml.safe_load((DERIVED / _DATASET_DIRS[dataset] / "splits.yaml").read_text())


# ---------------------------------------------------------------- builders

def _read_d1_frames():
    frames = {}
    for tk in D1_ASSETS:
        frames[tk] = pd.read_csv(ARTICLE_B / "data" / "derived_firstrate" / f"R01_daily_{tk}.csv",
                                 float_precision="round_trip")
    return frames


def _d1_wide(frames):
    dates = np.array(sorted(set().union(*(set(df["Date"]) for df in frames.values()))),
                     dtype="datetime64[D]")
    ret = np.full((len(dates), len(D1_ASSETS)), np.nan)
    close = np.full_like(ret, np.nan)
    in_universe = np.zeros(ret.shape, dtype=bool)
    for j, tk in enumerate(D1_ASSETS):
        df = frames[tk]
        frame_dates = np.asarray(pd.to_datetime(df["Date"]), dtype="datetime64[D]")
        idx = np.searchsorted(dates, frame_dates)
        if not (dates[idx] == frame_dates).all():
            raise ValueError(f"D1 {tk}: source dates are not a subset of the panel calendar")
        ret[idx, j] = df["log_ret"].to_numpy(dtype=np.float64)
        close[idx, j] = df["Close"].to_numpy(dtype=np.float64)
        in_universe[idx, j] = True
    return dates, ret, close, in_universe


def _write_panel(out_dir, dates, assets, ret, close, in_universe):
    T, N = ret.shape
    panel = pd.DataFrame({
        "date": pd.to_datetime(np.repeat(dates, N)).astype("datetime64[ns]"),
        "asset_id": np.tile(np.asarray(assets, dtype=object), T),
        "ret": ret.reshape(-1),
        "close": (np.full((T, N), np.nan) if close is None else close).reshape(-1),
        "in_universe": in_universe.reshape(-1),
    })
    panel.to_parquet(out_dir / "panel.parquet", index=False)
    np.save(out_dir / "ret_wide.npy", ret)
    np.save(out_dir / "dates.npy", dates)
    (out_dir / "assets.json").write_text(json.dumps(list(assets)) + "\n")
    return len(panel)


def _copy_phases():
    src_dir = ARTICLE_B / "results" / "R16_regime_census" / "data"
    out_dir = DERIVED / D1_DIR
    written = []
    for variant, fname in PHASE_VARIANTS.items():
        lines = (src_dir / fname).read_text().splitlines()
        dst = out_dir / f"phases_{variant}.csv"
        dst.write_text("\n".join([lines[0] + ",dating_variant"]
                                  + [ln + f",{variant}" for ln in lines[1:]]) + "\n")
        n = len(lines) - 1
        if n != PHASE_COUNTS[variant]:
            raise ValueError(f"phases_{variant}: {n} rows, expected {PHASE_COUNTS[variant]}")
        written.append((dst, n))
    return written


def _realize_segments(dates, pretrain_first):
    def last_before(boundary):
        return _as_date(dates[dates < boundary][-1])

    def first_after(boundary):
        return _as_date(dates[dates > boundary][EMBARGO])

    return {
        "pretrain": {"nominal_start": "2005-01-01", "nominal_end": "2016-01-01",
                     "first_day": _as_date(pretrain_first), "last_day": last_before(CALIB_START)},
        "calib": {"nominal_start": "2016-01-01", "nominal_end": "2020-01-01",
                  "first_day": first_after(CALIB_START), "last_day": last_before(MONITOR_START)},
        "monitor": {"nominal_start": "2020-01-01", "nominal_end": None,
                    "first_day": first_after(MONITOR_START), "last_day": _as_date(dates[-1])},
    }


def _write_splits(dataset, dates):
    if dataset == D1_DIR:
        pretrain_first = dates[0]  # D1: pretrain starts at the beginning of each series
    else:
        pretrain_first = dates[dates >= PRETRAIN_START][0]
    splits = {
        "dataset": dataset,
        "embargo_trading_days": EMBARGO,
        "convention": (
            "65 trading days after each internal boundary (2016-01-01, 2020-01-01) are "
            "embargoed and excluded from the following segment; pretrain starts at the first "
            "panel day (d1_etf4: start of each series; d2_us97: first day on/after 2005-01-01)"
        ),
        "segments": _realize_segments(dates, pretrain_first),
    }
    path = DERIVED / dataset / "splits.yaml"
    path.write_text(yaml.safe_dump(splits, sort_keys=False))
    return path


def _mean_pairwise_sign_corr(R):
    obs = ~np.isnan(R)
    if obs.all():
        corr = np.corrcoef((R > 0).astype(np.float64), rowvar=False)
        iu = np.triu_indices_from(corr, 1)
        return float(corr[iu].mean())
    n = R.shape[1]
    vals = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            m = obs[:, i] & obs[:, j]
            vals.append(float(np.corrcoef((R[m, i] > 0).astype(np.float64),
                                          (R[m, j] > 0).astype(np.float64))[0, 1]))
    return float(np.mean(vals))


def _pc1_var_share(R):
    obs = ~np.isnan(R)
    cols = obs.any(axis=0)
    X = R[obs[:, cols].all(axis=1)][:, cols]
    ev = np.linalg.eigvalsh(np.cov(X, rowvar=False))
    return float(ev[-1] / ev.sum())


def build_profile():
    rows = []
    for dataset in (D1_DIR, D2_DIR):
        ret, dates, _ = _load_wide(DERIVED / dataset)
        splits = load_splits(dataset)
        for seg in ("pretrain", "calib", "monitor"):
            s = splits["segments"][seg]
            m = ((dates >= np.datetime64(s["first_day"].isoformat()))
                 & (dates <= np.datetime64(s["last_day"].isoformat())))
            R = ret[m]
            obs = ~np.isnan(R)
            rho = _mean_pairwise_sign_corr(R)
            rows.append({"dataset": dataset, "segment": seg, "days": int(m.sum()),
                         "assets": int(obs.any(axis=0).sum()),
                         "zero_ret_share": float((R[obs] == 0).mean()),
                         "mean_sign_corr": rho, "k_eff": 1.0 / rho,
                         "pc1_var_share": _pc1_var_share(R)})
    df = pd.DataFrame(rows, columns=["dataset", "segment", "days", "assets", "zero_ret_share",
                                     "mean_sign_corr", "k_eff", "pc1_var_share"])
    RESULTS_DATA.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DATA / "d1_d2_profile.csv"
    df.to_csv(path, index=False)
    return path, len(df)


def _input_entry(path, rows, first_date=None, last_date=None):
    e = {"path": str(path).replace(str(Path.home()), "~"), "sha256": _sha256(path), "rows": rows}
    if first_date is not None:
        e["first_date"] = first_date
        e["last_date"] = last_date
    return e


def _build_manifest(frames, d2_frame):
    def out(rel, **kw):
        e = {"path": rel, "sha256": _sha256(REPO_ROOT / rel)}
        e.update(kw)
        return e

    d1_inputs = []
    for tk in D1_ASSETS:
        df = frames[tk]
        p = ARTICLE_B / "data" / "derived_firstrate" / f"R01_daily_{tk}.csv"
        d1_inputs.append(_input_entry(p, len(df), df["Date"].iloc[0], df["Date"].iloc[-1]))
    phase_src = ARTICLE_B / "results" / "R16_regime_census" / "data"
    for variant, fname in PHASE_VARIANTS.items():
        d1_inputs.append(_input_entry(phase_src / fname, PHASE_COUNTS[variant]))

    d2_path = ARTICLE_B / "data" / "derived_equities" / "R15_panel_logreturns.csv"
    d2_inputs = [_input_entry(d2_path, len(d2_frame),
                              d2_frame["Date"].iloc[0], d2_frame["Date"].iloc[-1])]

    def panel_outputs(dataset, ret, dates, assets):
        T, N = ret.shape
        outs = [out(f"data/derived/{dataset}/panel.parquet", rows=T * N,
                    first_date=str(dates[0]), last_date=str(dates[-1])),
                out(f"data/derived/{dataset}/ret_wide.npy", rows=T,
                    first_date=str(dates[0]), last_date=str(dates[-1])),
                out(f"data/derived/{dataset}/dates.npy", rows=int(dates.shape[0]),
                    first_date=str(dates[0]), last_date=str(dates[-1])),
                out(f"data/derived/{dataset}/assets.json", assets=N),
                out(f"data/derived/{dataset}/splits.yaml")]
        return outs

    d1_ret, d1_dates, d1_assets = _load_wide(DERIVED / D1_DIR)
    d1_outputs = panel_outputs(D1_DIR, d1_ret, d1_dates, d1_assets)
    for variant in PHASE_VARIANTS:
        ph = pd.read_csv(DERIVED / D1_DIR / f"phases_{variant}.csv", float_precision="round_trip")
        d1_outputs.append(out(f"data/derived/{D1_DIR}/phases_{variant}.csv",
                              rows=len(ph), first_date=ph["start_date"].min(),
                              last_date=ph["end_date"].max()))

    d2_ret, d2_dates, d2_assets = _load_wide(DERIVED / D2_DIR)
    d2_outputs = panel_outputs(D2_DIR, d2_ret, d2_dates, d2_assets)

    profile = pd.read_csv(RESULTS_DATA / "d1_d2_profile.csv")
    manifest = {
        "generator": "python -m jepadrift.data_loader.articleB --build",
        "source": {"path": ARTICLE_B_REF, "commit": _article_b_commit(), "access": "read-only"},
        "datasets": {D1_DIR: {"inputs": d1_inputs, "outputs": d1_outputs},
                     D2_DIR: {"inputs": d2_inputs, "outputs": d2_outputs}},
        "results": {"d1_d2_profile": out("results/data/d1_d2_profile.csv", rows=len(profile))},
    }
    # Preserve entries from other builders (e.g. D3 sp500) so that rebuilding
    # D1/D2 does not wipe them out of the shared manifest.
    man_path = DERIVED / "MANIFEST.json"
    if man_path.exists():
        existing = json.loads(man_path.read_text())
        for key in ("datasets", "results"):
            for k, v in existing.get(key, {}).items():
                if k not in manifest[key]:
                    manifest[key][k] = v
        if "sources" in existing:
            manifest["sources"] = existing["sources"]
    return manifest


def build():
    LOGS_DATA.mkdir(parents=True, exist_ok=True)
    log_lines = [f"source: {ARTICLE_B_REF} @ {_article_b_commit()} (read-only)"]

    def log(msg):
        print(msg)
        log_lines.append(msg)

    frames = _read_d1_frames()
    dates, ret, close, in_universe = _d1_wide(frames)
    for j, tk in enumerate(D1_ASSETS):
        n, first = D1_EXPECTED[tk]
        got = int(in_universe[:, j].sum())
        if got != n:
            raise ValueError(f"D1 {tk}: {got} rows, expected {n}")
        got_first = str(dates[np.flatnonzero(in_universe[:, j])[0]])
        if got_first != first:
            raise ValueError(f"D1 {tk}: first day {got_first}, expected {first}")
    if (str(dates[0]), str(dates[-1])) != ("2000-01-04", "2025-07-07"):
        raise ValueError(f"D1 calendar: {dates[0]}..{dates[-1]}, expected 2000-01-04..2025-07-07")
    d1_dir = DERIVED / D1_DIR
    d1_dir.mkdir(parents=True, exist_ok=True)
    n_panel = _write_panel(d1_dir, dates, D1_ASSETS, ret, close, in_universe)
    log(f"d1_etf4: panel.parquet {n_panel} rows; ret_wide.npy {ret.shape}; "
        f"dates {dates[0]}..{dates[-1]}")
    for dst, n in _copy_phases():
        log(f"d1_etf4: {dst.name} {n} phases")
    _write_splits(D1_DIR, dates)
    log("d1_etf4: splits.yaml written")

    d2_frame = pd.read_csv(ARTICLE_B / "data" / "derived_equities" / "R15_panel_logreturns.csv",
                           float_precision="round_trip")
    d2_dates = np.asarray(pd.to_datetime(d2_frame["Date"]), dtype="datetime64[D]")
    d2_assets = list(d2_frame.columns[1:])
    d2_ret = d2_frame[d2_assets].to_numpy(dtype=np.float64)
    if d2_ret.shape != D2_SHAPE:
        raise ValueError(f"D2: shape {d2_ret.shape}, expected {D2_SHAPE}")
    if np.isnan(d2_ret).any():
        raise ValueError("D2: unexpected NaN in R15_panel_logreturns.csv")
    if (str(d2_dates[0]), str(d2_dates[-1])) != ("2005-01-04", "2025-06-30"):
        raise ValueError(f"D2 calendar: {d2_dates[0]}..{d2_dates[-1]}, "
                         "expected 2005-01-04..2025-06-30")
    d2_dir = DERIVED / D2_DIR
    d2_dir.mkdir(parents=True, exist_ok=True)
    n_panel = _write_panel(d2_dir, d2_dates, d2_assets, d2_ret, None,
                           np.ones(d2_ret.shape, dtype=bool))
    log(f"d2_us97: panel.parquet {n_panel} rows; ret_wide.npy {d2_ret.shape}; "
        f"dates {d2_dates[0]}..{d2_dates[-1]}")
    _write_splits(D2_DIR, d2_dates)
    log("d2_us97: splits.yaml written")

    profile_path, profile_rows = build_profile()
    log(f"profile: {profile_path.relative_to(REPO_ROOT)} ({profile_rows} rows)")

    manifest = _build_manifest(frames, d2_frame)
    (DERIVED / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log("manifest: data/derived/MANIFEST.json written")

    (LOGS_DATA / "build.log").write_text("\n".join(log_lines) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Build and load the D1 (ETF-4) and D2 (US-97) datasets of Article C.")
    parser.add_argument("--build", action="store_true",
                        help="rebuild every file under data/derived/, the profile CSV and the manifest")
    args = parser.parse_args()
    if args.build:
        build()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
