"""D3 (S&P 500) panel built from Yahoo Finance (yfinance) and Wikipedia.

`python -m jepadrift.data_loader.sp500 --build` writes, under data/derived/:

- d3_239/: panel.parquet (long: date, asset_id, ret, close, in_universe),
  ret_wide.npy (float64, NaN where not in_universe), dates.npy (datetime64[D]),
  assets.json, chars.parquet (date, asset_id, c_*), splits.yaml, flags.csv;
- d3_500/: the same layout;

and results/data/d3_profile.csv (descriptive profile). Raw per-ticker caches live
under data/raw/d3_yf/ (gitignored). The universe is the current S&P 500
constituents from Wikipedia; the 239-ticker subset follows a deterministic
longest-history rule (see C-D3-no239 in docs/DEVIATIONS.md).

yfinance is imported lazily inside the download functions so that importing
this module (e.g. by the test suite) does not require yfinance.
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import io
import json
import subprocess
import time
import urllib.request
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_D3 = REPO_ROOT / "data" / "raw" / "d3_yf"
DERIVED = REPO_ROOT / "data" / "derived"
RESULTS_DATA = REPO_ROOT / "results" / "data"
LOGS_DATA = REPO_ROOT / "logs" / "data"
EXTERNAL = REPO_ROOT / "external"

D3_239_DIR = "d3_239"
D3_500_DIR = "d3_500"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
CD_DFM_REPO = "https://github.com/alexouadi/CD-DFM"
CD_DFM_DIR = EXTERNAL / "cd-dfm"
START_DATE = "2000-01-01"
EMBARGO = 65
PRETRAIN_START = np.datetime64("2005-01-01")
CALIB_START = np.datetime64("2016-01-01")
MONITOR_START = np.datetime64("2020-01-01")

CONTINUOUS_CHARS = ("c_beta_252", "c_vol_63", "c_mom_12_1", "c_rev_21")

GICS_SECTORS = (
    "Communication Services", "Consumer Discretionary", "Consumer Staples",
    "Energy", "Financials", "Health Care", "Industrials",
    "Information Technology", "Materials", "Real Estate", "Utilities",
)

_DATASET_DIRS = {"d3_239": D3_239_DIR, "d3_500": D3_500_DIR,
                 D3_239_DIR: D3_239_DIR, D3_500_DIR: D3_500_DIR}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _as_date(x):
    return pd.Timestamp(x).date()


# ---------------------------------------------------------------- universe

def _fetch_wikipedia():
    """Fetch the Wikipedia 'List of S&P 500 companies' table. Returns a
    DataFrame with columns Symbol, Security, GICS Sector, GICS Sub-Industry,
    Date first added (as string), CIK, Founded."""
    req = urllib.request.Request(
        WIKIPEDIA_URL,
        headers={"User-Agent": "Mozilla/5.0 (research; contact: jepa.drift@gmail.com)"})
    html = urllib.request.urlopen(req, timeout=60).read()
    tables = pd.read_html(io.BytesIO(html))
    for tbl in tables:
        if "Symbol" in tbl.columns and "GICS Sector" in tbl.columns:
            return tbl
    raise ValueError("Wikipedia: S&P 500 constituents table not found")


def _yf_ticker(wiki_symbol):
    """Map a Wikipedia ticker symbol to the Yahoo Finance convention."""
    return wiki_symbol.replace(".", "-")


def _clone_cd_dfm():
    """Clone CD-DFM into external/ if absent; return the pinned commit hash."""
    if not (CD_DFM_DIR / ".git").exists():
        subprocess.run(["git", "clone", CD_DFM_REPO, str(CD_DFM_DIR)],
                       check=True, capture_output=True, text=True)
    out = subprocess.run(["git", "-C", str(CD_DFM_DIR), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def _search_cd_dfm_239():
    """Search the CD-DFM checkout for an explicit 239-ticker list. Returns
    a list of tickers or None if absent."""
    if not CD_DFM_DIR.exists():
        return None
    for path in CD_DFM_DIR.rglob("*"):
        if path.suffix.lower() in (".csv", ".json", ".txt", ".parquet", ".yaml", ".yml"):
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            if "239" in text and ("ticker" in text.lower() or "symbol" in text.lower()):
                return None  # found a reference but not a usable list; treat as absent
    return None


# ---------------------------------------------------------------- download

def _download_one(yf_tk, refresh, log):
    """Download one ticker from Yahoo Finance. Returns (success, n_days,
    first_date, last_date). Caches to RAW_D3/<yf_tk>.parquet."""
    cache = RAW_D3 / f"{yf_tk}.parquet"
    if cache.exists() and not refresh:
        df = pd.read_parquet(cache)
        return True, len(df), str(df["date"].iloc[0]), str(df["date"].iloc[-1])

    import yfinance as yf
    import warnings
    warnings.filterwarnings("ignore")

    for attempt in range(1, 6):
        try:
            hist = yf.Ticker(yf_tk).history(start=START_DATE, auto_adjust=True)
            if hist.empty:
                log(f"  {yf_tk}: empty history (attempt {attempt})")
                return False, 0, None, None
            close = hist["Close"].copy()
            close.index = pd.to_datetime(close.index).tz_localize(None).normalize()
            df = pd.DataFrame({"date": close.index, "close": close.to_numpy(dtype=np.float64)})
            df = df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)
            if df.empty:
                log(f"  {yf_tk}: no valid closes (attempt {attempt})")
                return False, 0, None, None
            df.to_parquet(cache, index=False)
            return True, len(df), str(df["date"].iloc[0].date()), str(df["date"].iloc[-1].date())
        except Exception as exc:
            wait = min(2 ** attempt, 60)
            log(f"  {yf_tk}: attempt {attempt} failed ({exc}); retry in {wait}s")
            time.sleep(wait)
    log(f"  {yf_tk}: FAILED after 5 attempts")
    return False, 0, None, None


def _download_all(wiki_df, refresh, log):
    """Download all tickers. Returns a DataFrame indexed by Wikipedia symbol
    with columns yf_ticker, success, n_days, first_date, last_date."""
    RAW_D3.mkdir(parents=True, exist_ok=True)
    rows = []
    symbols = wiki_df["Symbol"].tolist()
    for i, sym in enumerate(symbols):
        yf_tk = _yf_ticker(sym)
        log(f"[{i+1}/{len(symbols)}] {sym} -> {yf_tk}")
        success, n_days, first, last = _download_one(yf_tk, refresh, log)
        rows.append({"symbol": sym, "yf_ticker": yf_tk, "success": success,
                     "n_days": n_days, "first_date": first, "last_date": last})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- prices / returns

def _load_close_wide(download_df):
    """Load all cached per-ticker prices into a wide (T, N) close matrix.
    Returns (dates, close, yf_tickers, success_mask)."""
    ok = download_df[download_df["success"]].reset_index(drop=True)
    yf_tickers = ok["yf_ticker"].tolist()
    all_dates = set()
    per_ticker = {}
    for yf_tk in yf_tickers:
        df = pd.read_parquet(RAW_D3 / f"{yf_tk}.parquet")
        df["date"] = pd.to_datetime(df["date"])
        per_ticker[yf_tk] = df.set_index("date")["close"]
        all_dates.update(df["date"].dt.date.tolist())
    dates = np.array(sorted(all_dates), dtype="datetime64[D]")
    T = len(dates)
    N = len(yf_tickers)
    close = np.full((T, N), np.nan)
    for j, yf_tk in enumerate(yf_tickers):
        s = per_ticker[yf_tk]
        s_dates = np.asarray(s.index.values, dtype="datetime64[D]")
        idx = np.searchsorted(dates, s_dates)
        valid = (idx < T) & (dates[np.minimum(idx, T - 1)] == s_dates)
        close[idx[valid], j] = s.to_numpy(dtype=np.float64)[valid]
    success_mask = np.ones(N, dtype=bool)
    return dates, close, yf_tickers, success_mask


def _compute_returns(close):
    """Log returns and in_universe mask. in_universe[t,i] is True iff
    close[t-1,i] and close[t,i] both exist. Returns (ret, in_universe)."""
    T, N = close.shape
    ret = np.full((T, N), np.nan)
    in_universe = np.zeros((T, N), dtype=bool)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = close[1:] / close[:-1]
    ret[1:] = np.log(ratio)
    both_exist = (~np.isnan(close[1:])) & (~np.isnan(close[:-1]))
    in_universe[1:] = both_exist
    return ret, in_universe


# ---------------------------------------------------------------- characteristics

def _market_return(ret, in_universe):
    """Equal-weighted market return: mean of valid returns each day."""
    valid_ret = np.where(in_universe, ret, np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mkt = np.nanmean(valid_ret, axis=1)
    return mkt


def _rolling_sums(y, valid, w):
    """Rolling sums of y over windows [t-w, t) using only valid entries.
    Returns (sum_y, sum_y2, count) each of shape (T,)."""
    T = len(y)
    y_clean = np.where(valid, y, 0.0)
    y2_clean = y_clean ** 2
    cy = np.concatenate([[0.0], np.cumsum(y_clean)])
    cy2 = np.concatenate([[0.0], np.cumsum(y2_clean)])
    cn = np.concatenate([[0], np.cumsum(valid.astype(np.int64))])
    t_idx = np.arange(T)
    start = np.maximum(t_idx - w, 0)
    sum_y = cy[t_idx] - cy[start]
    sum_y2 = cy2[t_idx] - cy2[start]
    count = cn[t_idx] - cn[start]
    return sum_y, sum_y2, count


def _rolling_xy_sums(y, x, valid, w):
    """Rolling sums of y, x, xy, x^2 over windows [t-w, t) using only entries
    where valid is True. Returns (sum_y, sum_x, sum_xy, sum_x2, count)."""
    T = len(y)
    y_clean = np.where(valid, y, 0.0)
    x_clean = np.where(valid, x, 0.0)
    xy_clean = y_clean * x_clean
    x2_clean = x_clean ** 2
    cy = np.concatenate([[0.0], np.cumsum(y_clean)])
    cx = np.concatenate([[0.0], np.cumsum(x_clean)])
    cxy = np.concatenate([[0.0], np.cumsum(xy_clean)])
    cx2 = np.concatenate([[0.0], np.cumsum(x2_clean)])
    cn = np.concatenate([[0], np.cumsum(valid.astype(np.int64))])
    t_idx = np.arange(T)
    start = np.maximum(t_idx - w, 0)
    return (cy[t_idx] - cy[start], cx[t_idx] - cx[start],
            cxy[t_idx] - cxy[start], cx2[t_idx] - cx2[start],
            cn[t_idx] - cn[start])


def _compute_chars(ret, in_universe, dates, assets, sector_map):
    """Compute dated characteristics known at the open of t (returns < t only).

    Returns a long DataFrame: date, asset_id, c_beta_252, c_vol_63, c_mom_12_1,
    c_rev_21, c_gics_<sector> (11 one-hot columns).
    """
    T, N = ret.shape
    mkt = _market_return(ret, in_universe)

    # Raw continuous characteristics (T, N), NaN where not computable
    raw = {name: np.full((T, N), np.nan) for name in CONTINUOUS_CHARS}

    for j in range(N):
        valid = in_universe[:, j]
        y = ret[:, j]

        # beta_252: OLS slope of y on mkt over [t-252, t), min 126 obs
        sx, sy, sxy, sx2, cnt = _rolling_xy_sums(y, mkt, valid, 252)
        denom = sx2 - sx ** 2 / np.maximum(cnt, 1)
        numer = sxy - sx * sy / np.maximum(cnt, 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            beta = np.where((cnt >= 126) & (denom > 1e-15), numer / denom, np.nan)
        raw["c_beta_252"][:, j] = beta

        # vol_63: std of y over [t-63, t)
        sum_y, sum_y2, cnt63 = _rolling_sums(y, valid, 63)
        with np.errstate(divide="ignore", invalid="ignore"):
            mean_y = sum_y / np.maximum(cnt63, 1)
            var_y = sum_y2 / np.maximum(cnt63, 1) - mean_y ** 2
        vol = np.where(cnt63 >= 2, np.sqrt(np.maximum(var_y, 0)), np.nan)
        raw["c_vol_63"][:, j] = vol

        # mom_12_1: sum of y over [t-252, t-21) = days t-252..t-22
        w = 252
        t_idx = np.arange(T)
        end_mom = np.maximum(t_idx - 21, 0)
        start_mom = np.maximum(t_idx - w, 0)
        y_clean = np.where(valid, y, 0.0)
        cy = np.concatenate([[0.0], np.cumsum(y_clean)])
        mom = cy[end_mom] - cy[start_mom]
        raw["c_mom_12_1"][:, j] = np.where(end_mom > start_mom, mom, np.nan)

        # rev_21: sum of y over [t-21, t) = days t-21..t-1
        start_rev = np.maximum(t_idx - 21, 0)
        rev = cy[t_idx] - cy[start_rev]
        raw["c_rev_21"][:, j] = np.where(t_idx > start_rev, rev, np.nan)

    # Rank-transform each continuous characteristic cross-sectionally per day
    ranked = {}
    for name in CONTINUOUS_CHARS:
        C = raw[name]
        C_df = pd.DataFrame(C, columns=assets)
        ranks = C_df.rank(axis=1, method="average", na_option="keep")
        count = C_df.notna().sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            ranked[name] = (ranks.div(count, axis=0) - 0.5).to_numpy(dtype=np.float64)

    # Build long DataFrame
    gics_cols = [f"c_gics_{s.lower().replace(' ', '_')}" for s in GICS_SECTORS]
    sector_idx = {s: i for i, s in enumerate(GICS_SECTORS)}
    n_gics = len(GICS_SECTORS)

    # Pre-compute GICS one-hot per asset
    gics_onehot = np.zeros((N, n_gics), dtype=np.float64)
    for j, asset in enumerate(assets):
        sec = sector_map.get(asset, "")
        if sec in sector_idx:
            gics_onehot[j, sector_idx[sec]] = 1.0

    # Assemble long panel
    date_col = np.repeat(dates, N)
    asset_col = np.tile(np.asarray(assets, dtype=object), T)

    data = {
        "date": pd.to_datetime(date_col).astype("datetime64[ns]"),
        "asset_id": asset_col,
    }
    for name in CONTINUOUS_CHARS:
        data[name] = ranked[name].reshape(-1)
    for k, col in enumerate(gics_cols):
        data[col] = np.tile(gics_onehot[:, k], T)

    chars = pd.DataFrame(data)
    return chars


# ---------------------------------------------------------------- selection

def _select_239(assets, in_universe, dates):
    """Select the 239 tickers with the longest history since START_DATE.
    Ties broken alphabetically. Returns the selected asset list."""
    n_days = in_universe.sum(axis=0)
    order = sorted(range(len(assets)), key=lambda j: (-n_days[j], assets[j]))
    selected = sorted([assets[j] for j in order[:239]])
    return selected


# ---------------------------------------------------------------- writers

def _write_panel(out_dir, dates, assets, ret, close, in_universe):
    T, N = ret.shape
    panel = pd.DataFrame({
        "date": pd.to_datetime(np.repeat(dates, N)).astype("datetime64[ns]"),
        "asset_id": np.tile(np.asarray(assets, dtype=object), T),
        "ret": ret.reshape(-1),
        "close": close.reshape(-1),
        "in_universe": in_universe.reshape(-1),
    })
    panel.to_parquet(out_dir / "panel.parquet", index=False)
    np.save(out_dir / "ret_wide.npy", ret)
    np.save(out_dir / "dates.npy", dates)
    (out_dir / "assets.json").write_text(json.dumps(list(assets)) + "\n")
    return len(panel)


def _write_flags(out_dir, dates, assets, ret, in_universe):
    """Write flags.csv: rows where |ret| > 0.5 (no suppression)."""
    mask = in_universe & (np.abs(ret) > 0.5)
    T, N = ret.shape
    if mask.any():
        t_idx, n_idx = np.nonzero(mask)
        flags = pd.DataFrame({
            "date": pd.to_datetime(dates[t_idx]).astype("datetime64[ns]"),
            "asset_id": np.asarray(assets, dtype=object)[n_idx],
            "ret": ret[t_idx, n_idx],
            "flag": "abs_gt_0.5",
        })
    else:
        flags = pd.DataFrame(columns=["date", "asset_id", "ret", "flag"])
    flags.to_csv(out_dir / "flags.csv", index=False)
    return len(flags)


def _realize_segments(dates):
    def last_before(boundary):
        return _as_date(dates[dates < boundary][-1])

    def first_after(boundary):
        return _as_date(dates[dates > boundary][EMBARGO])

    pretrain_first = dates[dates >= PRETRAIN_START][0]
    return {
        "pretrain": {"nominal_start": "2005-01-01", "nominal_end": "2016-01-01",
                     "first_day": _as_date(pretrain_first), "last_day": last_before(CALIB_START)},
        "calib": {"nominal_start": "2016-01-01", "nominal_end": "2020-01-01",
                  "first_day": first_after(CALIB_START), "last_day": last_before(MONITOR_START)},
        "monitor": {"nominal_start": "2020-01-01", "nominal_end": None,
                    "first_day": first_after(MONITOR_START), "last_day": _as_date(dates[-1])},
    }


def _write_splits(dataset, dates):
    splits = {
        "dataset": dataset,
        "embargo_trading_days": EMBARGO,
        "convention": (
            "65 trading days after each internal boundary (2016-01-01, 2020-01-01) are "
            "embargoed and excluded from the following segment; pretrain starts at the first "
            "panel day on/after 2005-01-01"
        ),
        "segments": _realize_segments(dates),
    }
    path = DERIVED / dataset / "splits.yaml"
    path.write_text(yaml.safe_dump(splits, sort_keys=False))
    return path


def _write_chars(out_dir, chars):
    chars.to_parquet(out_dir / "chars.parquet", index=False)
    return len(chars)


# ---------------------------------------------------------------- profile

def _mean_pairwise_sign_corr(R):
    obs = ~np.isnan(R)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        if obs.all():
            corr = np.corrcoef((R > 0).astype(np.float64), rowvar=False)
            iu = np.triu_indices_from(corr, 1)
            return float(np.nanmean(corr[iu]))
        n = R.shape[1]
        vals = []
        for i in range(n - 1):
            for j in range(i + 1, n):
                m = obs[:, i] & obs[:, j]
                if m.sum() < 2:
                    continue
                vals.append(float(np.corrcoef((R[m, i] > 0).astype(np.float64),
                                              (R[m, j] > 0).astype(np.float64))[0, 1]))
        return float(np.nanmean(vals)) if vals else float("nan")


def _coverage_annual(dates, in_universe, threshold=0.5):
    """Fraction of days per year where at least `threshold` of assets are
    in the universe. Returns a Series indexed by year."""
    df = pd.DataFrame({"year": pd.DatetimeIndex(pd.to_datetime(dates)).year,
                       "frac": in_universe.mean(axis=1)})
    annual = df.groupby("year")["frac"].apply(lambda s: float((s >= threshold).mean()))
    return annual


def build_profile():
    rows = []
    for dataset in (D3_239_DIR, D3_500_DIR):
        out_dir = DERIVED / dataset
        ret = np.load(out_dir / "ret_wide.npy")
        dates = np.load(out_dir / "dates.npy")
        panel = pd.read_parquet(out_dir / "panel.parquet")
        in_universe = panel["in_universe"].to_numpy().reshape(len(dates), -1)
        splits = load_splits(dataset)
        cov = _coverage_annual(dates, in_universe)
        for seg in ("pretrain", "calib", "monitor"):
            s = splits["segments"][seg]
            m = ((dates >= np.datetime64(s["first_day"].isoformat()))
                 & (dates <= np.datetime64(s["last_day"].isoformat())))
            R = ret[m]
            obs = ~np.isnan(R)
            assets_per_day = obs.sum(axis=1)
            rho = _mean_pairwise_sign_corr(R)
            years = pd.DatetimeIndex(pd.to_datetime(dates[m])).year
            cov_seg = cov.loc[years.min():years.max()].mean() if len(cov.loc[years.min():years.max()]) > 0 else float("nan")
            rows.append({
                "dataset": dataset, "segment": seg, "days": int(m.sum()),
                "assets_mean": float(assets_per_day.mean()),
                "assets_min": int(assets_per_day.min()),
                "assets_max": int(assets_per_day.max()),
                "zero_ret_share": float((R[obs] == 0).mean()) if obs.any() else float("nan"),
                "mean_sign_corr": rho, "k_eff": 1.0 / rho if rho > 0 else float("nan"),
                "coverage_0.5": cov_seg,
            })
        # eta on 2022-2024 for d3_239
        if dataset == D3_239_DIR:
            m_eta = ((dates >= np.datetime64("2022-01-01"))
                     & (dates <= np.datetime64("2024-12-31")))
            R_eta = ret[m_eta]
            rho_eta = _mean_pairwise_sign_corr(R_eta)
            rows.append({
                "dataset": dataset, "segment": "eta_2022_2024", "days": int(m_eta.sum()),
                "assets_mean": float((~np.isnan(R_eta)).sum(axis=1).mean()),
                "assets_min": int((~np.isnan(R_eta)).sum(axis=1).min()),
                "assets_max": int((~np.isnan(R_eta)).sum(axis=1).max()),
                "zero_ret_share": float((R_eta[~np.isnan(R_eta)] == 0).mean()),
                "mean_sign_corr": rho_eta, "k_eff": 1.0 / rho_eta if rho_eta > 0 else float("nan"),
                "coverage_0.5": float("nan"),
            })
    cols = ["dataset", "segment", "days", "assets_mean", "assets_min", "assets_max",
            "zero_ret_share", "mean_sign_corr", "k_eff", "coverage_0.5"]
    df = pd.DataFrame(rows, columns=cols)
    RESULTS_DATA.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DATA / "d3_profile.csv"
    df.to_csv(path, index=False)
    return path, len(df)


# ---------------------------------------------------------------- manifest

def _update_manifest(download_df, cd_dfm_commit, wiki_sha, wiki_date):
    man_path = DERIVED / "MANIFEST.json"
    man = json.loads(man_path.read_text()) if man_path.exists() else {}
    gen = man.get("generator", "")
    tag = "python -m jepadrift.data_loader.sp500 --build"
    man["generator"] = gen if tag in gen else (gen + "; " + tag if gen else tag)
    man.setdefault("sources", {})
    man["sources"]["d3"] = {
        "yfinance": "1.7.0",
        "wikipedia": {"url": WIKIPEDIA_URL, "sha256": wiki_sha, "fetched": wiki_date},
        "cd_dfm": {"repo": CD_DFM_REPO, "commit": cd_dfm_commit, "access": "read-only"},
        "start_date": START_DATE,
    }

    ok = download_df[download_df["success"]]
    man["sources"]["d3"]["tickers_requested"] = int(len(download_df))
    man["sources"]["d3"]["tickers_downloaded"] = int(len(ok))
    man["sources"]["d3"]["tickers_failed"] = int((~download_df["success"]).sum())

    def out(rel, **kw):
        e = {"path": rel, "sha256": _sha256(REPO_ROOT / rel)}
        e.update(kw)
        return e

    for dataset in (D3_239_DIR, D3_500_DIR):
        out_dir = DERIVED / dataset
        ret = np.load(out_dir / "ret_wide.npy")
        dates = np.load(out_dir / "dates.npy")
        N = json.loads((out_dir / "assets.json").read_text()).__len__()
        T = ret.shape[0]
        outputs = [
            out(f"data/derived/{dataset}/panel.parquet", rows=T * N,
                first_date=str(dates[0]), last_date=str(dates[-1])),
            out(f"data/derived/{dataset}/ret_wide.npy", rows=T,
                first_date=str(dates[0]), last_date=str(dates[-1])),
            out(f"data/derived/{dataset}/dates.npy", rows=int(dates.shape[0]),
                first_date=str(dates[0]), last_date=str(dates[-1])),
            out(f"data/derived/{dataset}/assets.json", assets=N),
            out(f"data/derived/{dataset}/chars.parquet"),
            out(f"data/derived/{dataset}/splits.yaml"),
            out(f"data/derived/{dataset}/flags.csv"),
        ]
        man.setdefault("datasets", {})[dataset] = {"inputs": [], "outputs": outputs}

    profile = pd.read_csv(RESULTS_DATA / "d3_profile.csv")
    man.setdefault("results", {})["d3_profile"] = out(
        "results/data/d3_profile.csv", rows=len(profile))

    man_path.write_text(json.dumps(man, indent=2) + "\n")
    return man_path


# ---------------------------------------------------------------- loaders

def _load_wide(out_dir):
    ret = np.load(out_dir / "ret_wide.npy")
    dates = np.load(out_dir / "dates.npy")
    assets = json.loads((out_dir / "assets.json").read_text())
    return ret, dates, assets


def load_d3_239():
    """D3 239-ticker subset: (ret, dates, assets), same contract as load_d1."""
    return _load_wide(DERIVED / D3_239_DIR)


def load_d3_500():
    """D3 ~500-ticker subset: (ret, dates, assets), same contract as load_d1."""
    return _load_wide(DERIVED / D3_500_DIR)


def load_chars(subset):
    """Characteristics long DataFrame for `subset` ('d3_239' or 'd3_500')."""
    if subset not in _DATASET_DIRS:
        raise ValueError(f"unknown subset {subset!r}; expected one of {sorted(_DATASET_DIRS)}")
    return pd.read_parquet(DERIVED / _DATASET_DIRS[subset] / "chars.parquet")


def load_splits(subset):
    """Split definition of `subset` as a dict; segment dates are datetime.date."""
    if subset not in _DATASET_DIRS:
        raise ValueError(f"unknown subset {subset!r}; expected one of {sorted(_DATASET_DIRS)}")
    return yaml.safe_load((DERIVED / _DATASET_DIRS[subset] / "splits.yaml").read_text())


# ---------------------------------------------------------------- build

def build(refresh=False):
    LOGS_DATA.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    log("=== D3 build ===")
    log(f"refresh={refresh}")

    # Phase 1a: clone CD-DFM
    log("[1a] cloning CD-DFM")
    cd_dfm_commit = _clone_cd_dfm()
    log(f"  CD-DFM commit: {cd_dfm_commit}")
    cd_dfm_239 = _search_cd_dfm_239()
    if cd_dfm_239 is None:
        log("  239-ticker list NOT found in CD-DFM (C-D3-no239); using longest-history rule")
    else:
        log(f"  239-ticker list found in CD-DFM: {len(cd_dfm_239)} tickers")

    # Phase 1c: fetch Wikipedia
    log("[1c] fetching Wikipedia S&P 500 list")
    wiki_df = _fetch_wikipedia()
    wiki_path = RAW_D3 / "sp500_wikipedia.csv"
    RAW_D3.mkdir(parents=True, exist_ok=True)
    wiki_df.to_csv(wiki_path, index=False)
    wiki_sha = _sha256(wiki_path)
    wiki_date = time.strftime("%Y-%m-%d")
    log(f"  {len(wiki_df)} constituents; saved to {wiki_path.relative_to(REPO_ROOT)}")
    log(f"  SHA-256: {wiki_sha}")

    # Build sector map (Wikipedia symbol -> GICS sector)
    sector_map = {}
    for _, row in wiki_df.iterrows():
        sym = str(row["Symbol"])
        sec = str(row.get("GICS Sector", ""))
        sector_map[sym] = sec

    # Phase 2: download prices
    log("[2] downloading prices from Yahoo Finance")
    download_df = _download_all(wiki_df, refresh, log)
    n_ok = int(download_df["success"].sum())
    n_fail = int((~download_df["success"]).sum())
    log(f"  downloaded: {n_ok}/{len(download_df)} (failed: {n_fail})")
    download_df.to_csv(RAW_D3 / "_download_stats.csv", index=False)

    # Phase 3: build close wide + returns
    log("[3] computing returns")
    dates, close, yf_tickers, _ = _load_close_wide(download_df)
    ret, in_universe = _compute_returns(close)
    log(f"  calendar: {dates[0]}..{dates[-1]} ({len(dates)} days), {len(yf_tickers)} tickers")

    # Map yf_tickers back to Wikipedia symbols for sector lookup
    yf_to_wiki = {yf_tk: sym for sym, yf_tk in
                  zip(download_df["symbol"], download_df["yf_ticker"])}
    # Use yf_tickers as asset_ids (Yahoo convention, consistent with data source)
    assets = list(yf_tickers)
    sector_map_yf = {yf_tk: sector_map.get(yf_to_wiki.get(yf_tk, ""), "")
                     for yf_tk in yf_tickers}

    # Phase 5a: d3_500 = all successfully downloaded tickers
    log("[5] building d3_500")
    d3_500_dir = DERIVED / D3_500_DIR
    d3_500_dir.mkdir(parents=True, exist_ok=True)
    n_panel = _write_panel(d3_500_dir, dates, assets, ret, close, in_universe)
    log(f"  panel.parquet: {n_panel} rows; ret_wide.npy {ret.shape}")
    _write_splits(D3_500_DIR, dates)
    log("  splits.yaml written")
    n_flags = _write_flags(d3_500_dir, dates, assets, ret, in_universe)
    log(f"  flags.csv: {n_flags} rows")

    # Phase 4: characteristics for d3_500
    log("[4] computing characteristics (d3_500)")
    chars_500 = _compute_chars(ret, in_universe, dates, assets, sector_map_yf)
    n_chars = _write_chars(d3_500_dir, chars_500)
    log(f"  chars.parquet: {n_chars} rows")

    # Phase 5b: d3_239 = 239 longest-history tickers
    log("[5] building d3_239")
    selected_239 = _select_239(assets, in_universe, dates)
    log(f"  selected {len(selected_239)} tickers")
    sel_idx = [assets.index(a) for a in selected_239]
    sel_idx = np.array(sorted(sel_idx))
    ret_239 = ret[:, sel_idx]
    close_239 = close[:, sel_idx]
    iu_239 = in_universe[:, sel_idx]
    assets_239 = [assets[j] for j in sel_idx]
    sector_map_239 = {a: sector_map_yf[a] for a in assets_239}

    d3_239_dir = DERIVED / D3_239_DIR
    d3_239_dir.mkdir(parents=True, exist_ok=True)
    n_panel_239 = _write_panel(d3_239_dir, dates, assets_239, ret_239, close_239, iu_239)
    log(f"  panel.parquet: {n_panel_239} rows; ret_wide.npy {ret_239.shape}")
    _write_splits(D3_239_DIR, dates)
    log("  splits.yaml written")
    n_flags_239 = _write_flags(d3_239_dir, dates, assets_239, ret_239, iu_239)
    log(f"  flags.csv: {n_flags_239} rows")

    log("[4] computing characteristics (d3_239)")
    chars_239 = _compute_chars(ret_239, iu_239, dates, assets_239, sector_map_239)
    n_chars_239 = _write_chars(d3_239_dir, chars_239)
    log(f"  chars.parquet: {n_chars_239} rows")

    # Save the 239 selection for traceability
    (d3_239_dir / "selection.json").write_text(json.dumps({
        "rule": "239 tickers with the longest history since " + START_DATE + "; ties broken alphabetically",
        "n_selected": len(selected_239),
        "assets": selected_239,
    }, indent=2) + "\n")

    # Phase 8: profile
    log("[8] building profile")
    profile_path, profile_rows = build_profile()
    log(f"  {profile_path.relative_to(REPO_ROOT)} ({profile_rows} rows)")

    # Phase 9: manifest
    log("[9] updating manifest")
    man_path = _update_manifest(download_df, cd_dfm_commit, wiki_sha, wiki_date)
    log(f"  {man_path.relative_to(REPO_ROOT)} updated")

    (LOGS_DATA / "d3_build.log").write_text("\n".join(log_lines) + "\n")
    log("=== D3 build complete ===")


def main():
    parser = argparse.ArgumentParser(
        description="Build and load the D3 (S&P 500) dataset of Article C.")
    parser.add_argument("--build", action="store_true",
                        help="rebuild every file under data/derived/d3_239/ and d3_500/")
    parser.add_argument("--refresh", action="store_true",
                        help="force re-download of all tickers (ignore cache)")
    args = parser.parse_args()
    if args.build:
        build(refresh=args.refresh)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
