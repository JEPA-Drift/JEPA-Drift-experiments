"""Contract tests for the D3 (S&P 500) derived datasets (pytest).

Integration tests require the D3 data to be built first:
    python -m jepadrift.data_loader.sp500 --build
They are skipped otherwise. The synthetic non-anticipation test always runs.
"""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from jepadrift.data_loader import sp500

D3_239 = sp500.DERIVED / "d3_239"
D3_500 = sp500.DERIVED / "d3_500"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="session")
def _d3_built():
    if not (D3_239 / "panel.parquet").exists() or not (D3_500 / "panel.parquet").exists():
        pytest.skip("D3 not built; run: python -m jepadrift.data_loader.sp500 --build")
    return True


# ------------------------------------------------------- non-anticipation

def test_non_anticipation_synthetic():
    """Perturbing returns from day s leaves characteristics through day s
    bit-identical; the first affected characteristic is at day s+1."""
    T, N = 300, 5
    rng = np.random.SeedSequence(42)
    ret = np.random.default_rng(rng).standard_normal((T, N)) * 0.01
    dates = np.arange(np.datetime64("2020-01-01"),
                      np.datetime64("2020-01-01") + T, dtype="datetime64[D]")
    iu = np.ones((T, N), dtype=bool)
    iu[:10, :] = False
    assets = [f"TK{i}" for i in range(N)]
    sectors = ["Energy", "Materials", "Industrials", "Financials", "Utilities"]
    sector_map = dict(zip(assets, sectors))

    chars1 = sp500._compute_chars(ret, iu, dates, assets, sector_map)

    ret2 = ret.copy()
    rng2 = np.random.SeedSequence(99)
    ret2[150:, :] = np.random.default_rng(rng2).standard_normal((T - 150, N)) * 0.02
    chars2 = sp500._compute_chars(ret2, iu, dates, assets, sector_map)

    cols = list(sp500.CONTINUOUS_CHARS)
    base = pd.Timestamp("2020-01-01")
    # Days 149 and 150: windows use returns strictly before the day, all < 150, unchanged
    for day in (149, 150):
        d = base + pd.Timedelta(days=day)
        v1 = chars1[chars1["date"] == d][cols].to_numpy()
        v2 = chars2[chars2["date"] == d][cols].to_numpy()
        assert np.array_equal(v1, v2, equal_nan=True), \
            f"chars at day {day} should be identical"
    # Day 151: window [151-252, 151) includes day 150 (perturbed) → must differ
    d = base + pd.Timedelta(days=151)
    v1 = chars1[chars1["date"] == d][cols].to_numpy()
    v2 = chars2[chars2["date"] == d][cols].to_numpy()
    assert not np.array_equal(v1, v2, equal_nan=True), \
        "chars at day 151 should differ after perturbation at day 150"


# ------------------------------------------------------- loader contracts

def test_d3_239_loader_contract(_d3_built):
    ret, dates, assets = sp500.load_d3_239()
    assert ret.dtype == np.float64
    assert ret.shape == (len(dates), 239)
    assert dates.shape == (len(dates),)
    assert np.issubdtype(dates.dtype, np.datetime64)
    assert len(assets) == 239 and len(set(assets)) == 239


def test_d3_500_loader_contract(_d3_built):
    ret, dates, assets = sp500.load_d3_500()
    assert ret.dtype == np.float64
    assert ret.shape == (len(dates), len(assets))
    assert np.issubdtype(dates.dtype, np.datetime64)
    assert len(assets) >= 450  # at least 450 tickers overall


# ------------------------------------------------------- panel layout

def test_d3_500_panel_layout(_d3_built):
    ret, dates, assets = sp500.load_d3_500()
    panel = pd.read_parquet(D3_500 / "panel.parquet")
    assert list(panel.columns) == ["date", "asset_id", "ret", "close", "in_universe"]
    assert len(panel) == len(dates) * len(assets)
    assert panel["ret"].dtype == np.float64
    assert panel["close"].dtype == np.float64
    assert panel["in_universe"].dtype == bool
    # close is populated where available (not all-NaN like D2)
    assert panel["close"].notna().any()
    # ret is NaN exactly where in_universe is False
    assert (panel.loc[~panel["in_universe"], "ret"].isna()).all()
    assert (panel.loc[panel["in_universe"], "ret"].notna()).all()


def test_d3_239_panel_layout(_d3_built):
    ret, dates, assets = sp500.load_d3_239()
    panel = pd.read_parquet(D3_239 / "panel.parquet")
    assert list(panel.columns) == ["date", "asset_id", "ret", "close", "in_universe"]
    assert len(panel) == len(dates) * 239


# ------------------------------------------------------- in_universe semantics

def test_in_universe_iff_both_closes(_d3_built):
    """in_universe[t,i] is True iff close[t-1,i] and close[t,i] both exist."""
    ret, dates, assets = sp500.load_d3_500()
    panel = pd.read_parquet(D3_500 / "panel.parquet")
    close_wide = panel.pivot(index="date", columns="asset_id", values="close")[assets].to_numpy()
    iu_wide = panel.pivot(index="date", columns="asset_id", values="in_universe")[assets].to_numpy()
    both = (~np.isnan(close_wide[1:])) & (~np.isnan(close_wide[:-1]))
    np.testing.assert_array_equal(iu_wide[1:], both)
    assert not iu_wide[0].any()  # first day: no t-1 close


# ------------------------------------------------------- no NaN after warmup

def test_no_nan_chars_after_warmup(_d3_built):
    """No continuous characteristic is NaN where in_universe is True and the
    asset has enough history for that characteristic (per-asset warmup)."""
    for subset, loader in (("d3_239", sp500.load_d3_239),
                           ("d3_500", sp500.load_d3_500)):
        ret, dates, assets = loader()
        panel = pd.read_parquet(sp500.DERIVED / subset / "panel.parquet")
        iu_wide = panel.pivot(index="date", columns="asset_id",
                              values="in_universe")[assets].to_numpy()
        chars = sp500.load_chars(subset)
        T, N = iu_wide.shape
        t_idx = np.arange(T)

        iu_int = iu_wide.astype(np.int64)
        cn = np.concatenate([np.zeros((1, N), dtype=np.int64),
                             np.cumsum(iu_int, axis=0)])

        def rolling_count(w):
            start = np.maximum(t_idx - w, 0)
            return cn[t_idx] - cn[start]

        count_252 = rolling_count(252)
        count_63 = rolling_count(63)
        start_mom = np.maximum(t_idx - 252, 0)
        end_mom = np.maximum(t_idx - 21, 0)
        count_mom = cn[end_mom] - cn[start_mom]
        start_rev = np.maximum(t_idx - 21, 0)
        count_rev = cn[t_idx] - cn[start_rev]

        conditions = {
            "c_beta_252": iu_wide & (count_252 >= 126),
            "c_vol_63": iu_wide & (count_63 >= 2),
            "c_mom_12_1": iu_wide & (count_mom >= 1),
            "c_rev_21": iu_wide & (count_rev >= 1),
        }
        for c in sp500.CONTINUOUS_CHARS:
            c_wide = chars.pivot(index="date", columns="asset_id",
                                 values=c)[assets].to_numpy()
            nan_where_ok = conditions[c] & np.isnan(c_wide)
            n_bad = int(nan_where_ok.sum())
            total_ok = int(conditions[c].sum())
            # beta_252: OLS slope is undefined (NaN) when the market return has
            # near-zero variance in the window (denominator ~ 0). Allow up to
            # 0.1% numerical edge cases; other characteristics are strict.
            tol = max(1, int(0.001 * total_ok)) if c == "c_beta_252" else 0
            assert n_bad <= tol, \
                f"{subset} {c}: {n_bad}/{total_ok} NaN where in_universe and enough history (tol {tol})"


# ------------------------------------------------------- GICS sectors

def test_gics_one_hot_complete(_d3_built):
    """Each (date, asset) row has exactly one GICS sector active; the sector
    is constant across dates for each asset."""
    for subset in ("d3_239", "d3_500"):
        chars = sp500.load_chars(subset)
        gics_cols = [c for c in chars.columns if c.startswith("c_gics_")]
        assert len(gics_cols) == 11
        gics_sum = chars[gics_cols].sum(axis=1)
        assert (gics_sum == 1.0).all(), \
            f"{subset}: {int((gics_sum != 1.0).sum())} rows with GICS sum != 1"
        # Sector consistency per asset
        for asset in chars["asset_id"].unique():
            sub = chars[chars["asset_id"] == asset]
            sectors = sub[gics_cols].idxmax(axis=1).unique()
            assert len(sectors) == 1, \
                f"{subset} {asset}: {len(sectors)} distinct sectors across dates"


# ------------------------------------------------------- chars rank range

def test_chars_rank_range(_d3_built):
    """Continuous characteristics are rank-transformed to approximately [-0.5, 0.5]."""
    for subset in ("d3_239", "d3_500"):
        chars = sp500.load_chars(subset)
        for c in sp500.CONTINUOUS_CHARS:
            vals = chars[c].dropna()
            assert len(vals) > 0, f"{subset} {c}: all NaN"
            assert vals.min() >= -0.5 - 1e-9, \
                f"{subset} {c}: min {vals.min()} < -0.5"
            assert vals.max() <= 0.5 + 1e-9, \
                f"{subset} {c}: max {vals.max()} > 0.5"


# ------------------------------------------------------- chars schema

def test_chars_schema(_d3_built):
    expected_cols = (["date", "asset_id"] + list(sp500.CONTINUOUS_CHARS)
                     + [f"c_gics_{s.lower().replace(' ', '_')}" for s in sp500.GICS_SECTORS])
    for subset in ("d3_239", "d3_500"):
        chars = sp500.load_chars(subset)
        assert list(chars.columns) == expected_cols, \
            f"{subset}: columns {list(chars.columns)} != {expected_cols}"


# ------------------------------------------------------- splits

@pytest.mark.parametrize("subset,loader", [
    ("d3_239", sp500.load_d3_239),
    ("d3_500", sp500.load_d3_500),
])
def test_splits_realized_dates(_d3_built, subset, loader):
    splits = sp500.load_splits(subset)
    assert splits["embargo_trading_days"] == 65
    seg = splits["segments"]
    assert list(seg) == ["pretrain", "calib", "monitor"]
    assert str(seg["pretrain"]["first_day"]) >= "2005-01-01"
    assert str(seg["pretrain"]["last_day"]) == "2015-12-31"
    assert str(seg["calib"]["last_day"]) == "2019-12-31"
    assert seg["pretrain"]["last_day"] < seg["calib"]["first_day"]
    assert seg["calib"]["last_day"] < seg["monitor"]["first_day"]

    _, dates, _ = loader()
    calendar = set(np.datetime_as_string(dates, unit="D"))
    for s in seg.values():
        assert s["first_day"].isoformat() in calendar
        assert s["last_day"].isoformat() in calendar
    for boundary, name in (("2016-01-01", "calib"), ("2020-01-01", "monitor")):
        after = dates[dates > np.datetime64(boundary)]
        assert str(after[65]) == seg[name]["first_day"].isoformat()


def test_load_splits_rejects_unknown_subset():
    with pytest.raises(ValueError):
        sp500.load_splits("d3_999")


def test_load_chars_rejects_unknown_subset():
    with pytest.raises(ValueError):
        sp500.load_chars("d3_999")


# ------------------------------------------------------- 450+ assets in 2020

def test_d3_500_assets_2020(_d3_built):
    """At least 450 distinct assets are in the universe at some point in 2020."""
    ret, dates, assets = sp500.load_d3_500()
    panel = pd.read_parquet(D3_500 / "panel.parquet")
    iu_wide = panel.pivot(index="date", columns="asset_id",
                          values="in_universe")[assets].to_numpy()
    m_2020 = ((dates >= np.datetime64("2020-01-01"))
              & (dates <= np.datetime64("2020-12-31")))
    n_assets_2020 = int(iu_wide[m_2020].any(axis=0).sum())
    assert n_assets_2020 >= 450, \
        f"d3_500: {n_assets_2020} assets in 2020, expected >= 450"


# ------------------------------------------------------- flags

def test_flags_csv(_d3_built):
    """flags.csv contains only rows with |ret| > 0.5, no suppression."""
    for subset in ("d3_239", "d3_500"):
        flags_path = sp500.DERIVED / subset / "flags.csv"
        assert flags_path.exists()
        flags = pd.read_csv(flags_path)
        if len(flags) > 0:
            assert list(flags.columns) == ["date", "asset_id", "ret", "flag"]
            assert (flags["flag"] == "abs_gt_0.5").all()
            assert (flags["ret"].abs() > 0.5).all()
        # Cross-check: all |ret| > 0.5 rows in the panel are in flags
        panel = pd.read_parquet(sp500.DERIVED / subset / "panel.parquet")
        big = panel[panel["in_universe"] & (panel["ret"].abs() > 0.5)]
        assert len(big) == len(flags), \
            f"{subset}: panel has {len(big)} |ret|>0.5 rows, flags.csv has {len(flags)}"


# ------------------------------------------------------- manifest integrity

def test_manifest_hashes(_d3_built):
    """SHA-256 of every D3 output file matches the manifest."""
    man = json.loads((sp500.DERIVED / "MANIFEST.json").read_text())
    assert "d3" in man.get("sources", {})
    for dataset in ("d3_239", "d3_500"):
        assert dataset in man["datasets"]
        for e in man["datasets"][dataset]["outputs"]:
            p = sp500.REPO_ROOT / e["path"]
            assert p.exists(), e["path"]
            assert _sha256(p) == e["sha256"], \
                f"{e['path']}: SHA-256 mismatch"


def test_manifest_sources(_d3_built):
    man = json.loads((sp500.DERIVED / "MANIFEST.json").read_text())
    src = man["sources"]["d3"]
    assert src["yfinance"] == "1.7.0"
    assert "wikipedia" in src
    assert "cd_dfm" in src
    assert src["tickers_downloaded"] >= 450
    assert src["start_date"] == "2000-01-01"


# ------------------------------------------------------- reconstruction from cache

def test_reconstruction_from_cache(_d3_built):
    """ret_wide.npy is bit-identical to the reconstruction from per-ticker caches."""
    for subset, loader in (("d3_239", sp500.load_d3_239),
                           ("d3_500", sp500.load_d3_500)):
        ret, dates, assets = loader()
        # Reconstruct from cache (d3_500 uses all cached tickers; d3_239 is a subset)
        if subset == "d3_500":
            download_df = pd.read_csv(sp500.RAW_D3 / "_download_stats.csv")
        else:
            download_df = pd.read_csv(sp500.RAW_D3 / "_download_stats.csv")
            # Filter to the 239 selected assets
            sel = json.loads((D3_239 / "selection.json").read_text())
            ok = download_df[download_df["yf_ticker"].isin(sel["assets"])]
            download_df = ok.reset_index(drop=True)
        dates2, close2, yf_tickers2, _ = sp500._load_close_wide(download_df)
        ret2, _ = sp500._compute_returns(close2)
        np.testing.assert_array_equal(dates, dates2)
        np.testing.assert_array_equal(ret, ret2)
        assert assets == yf_tickers2


# ------------------------------------------------------- profile CSV

def test_d3_profile_csv(_d3_built):
    df = pd.read_csv(sp500.RESULTS_DATA / "d3_profile.csv", float_precision="round_trip")
    assert list(df.columns) == ["dataset", "segment", "days", "assets_mean",
                                "assets_min", "assets_max", "zero_ret_share",
                                "mean_sign_corr", "k_eff", "coverage_0.5"]
    assert set(df["dataset"]) == {"d3_239", "d3_500"}
    assert {"pretrain", "calib", "monitor"} <= set(df["segment"])
    assert "eta_2022_2024" in set(df["segment"])
    assert (df["days"] > 0).all()
    assert ((df["assets_mean"] > 1)).all()
    # d3_500 should have more assets than d3_239
    a500 = df[df["dataset"] == "d3_500"]["assets_mean"].mean()
    a239 = df[df["dataset"] == "d3_239"]["assets_mean"].mean()
    assert a500 > a239
    # d3_239 should have ~239 assets
    assert 200 < a239 < 280


# ------------------------------------------------------- selection rule

def test_d3_239_selection(_d3_built):
    """d3_239 contains exactly 239 tickers, selected by longest history."""
    sel = json.loads((D3_239 / "selection.json").read_text())
    assert sel["n_selected"] == 239
    assert len(sel["assets"]) == 239
    assert len(set(sel["assets"])) == 239
    # All selected assets are in d3_500
    _, _, assets_500 = sp500.load_d3_500()
    assert set(sel["assets"]) <= set(assets_500)
    # Verify longest-history rule: no excluded asset has more days than a selected one
    download_df = pd.read_csv(sp500.RAW_D3 / "_download_stats.csv")
    ok = download_df[download_df["success"]]
    n_days = dict(zip(ok["yf_ticker"], ok["n_days"]))
    selected_days = [n_days.get(a, 0) for a in sel["assets"]]
    excluded = set(assets_500) - set(sel["assets"])
    excluded_days = [n_days.get(a, 0) for a in excluded]
    if excluded_days:
        assert min(selected_days) >= max(excluded_days), \
            "selection rule violated: an excluded ticker has more history"
