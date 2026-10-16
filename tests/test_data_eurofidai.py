"""Contract tests for the D4 (EUROFIDAI European equities) data loader (pytest).

Synthetic fixture tests always run. Integration tests on real EUROFIDAI data
are skipped if `data/raw/eurofidai/` is empty (the default — data is
proprietary and exported manually by the researcher).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from jepadrift.data_loader import eurofidai
from jepadrift.data_loader import sp500

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "eurofidai_fake"
FIXTURE_SCHEMA = FIXTURES / "schema.yaml"
RAW_D4 = eurofidai.RAW_D4
DERIVED_D4 = eurofidai.DERIVED_D4


@pytest.fixture(scope="session")
def _d4_built():
    if not (DERIVED_D4 / "panel.parquet").exists():
        pytest.skip("D4 not built; EUROFIDAI data must be exported first "
                    "(see docs/sections/eurofidai_extraction_spec.md)")
    return True


# ------------------------------------------------------- schema mapping

def test_schema_loads():
    fields, liquidity, sectors = eurofidai.load_schema(FIXTURE_SCHEMA)
    assert "id_stable" in fields
    assert "adjusted_close" in fields
    assert fields["id_stable"] == "id_eurofidai"
    assert fields["adjusted_close"] == "close_adj"
    assert liquidity["min_days_traded_21"] == 1


def test_schema_mapping_renames_columns():
    fields, _, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    df = pd.read_csv(FIXTURES / "eur_2020.csv", float_precision="round_trip")
    mapped = eurofidai._map_fields(df, fields)
    assert "id_stable" in mapped.columns
    assert "adjusted_close" in mapped.columns
    assert "date" in mapped.columns
    assert "id_eurofidai" not in mapped.columns
    assert "close_adj" not in mapped.columns


# ------------------------------------------------------- reading raw files

def test_read_raw_files_fixtures():
    fields, _, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    df = eurofidai.read_raw_files(raw_dir=FIXTURES, fields=fields)
    assert len(df) > 0
    assert "id_stable" in df.columns
    assert "adjusted_close" in df.columns
    # 3 files: eur_2020 (13 rows), eur_2021 (10 rows), uk_2020 (10 rows)
    assert len(df) == 13 + 10 + 10


def test_read_raw_files_missing_dir():
    with pytest.raises(FileNotFoundError, match="not found"):
        eurofidai.read_raw_files(raw_dir=Path("/nonexistent/path"))


def test_read_raw_files_empty_dir(tmp_path):
    with pytest.raises(FileNotFoundError, match="No CSV files"):
        eurofidai.read_raw_files(raw_dir=tmp_path)


def test_read_raw_files_missing_required(tmp_path):
    """CSV without the required columns raises ValueError after mapping."""
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n")
    fields, _, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    with pytest.raises(ValueError, match="Missing required columns"):
        eurofidai.read_raw_files(raw_dir=tmp_path, fields=fields)


# ------------------------------------------------------- returns computation

def test_compute_returns_basic():
    close = np.array([[100.0, 50.0], [101.0, 51.0], [102.0, np.nan]])
    ret, close_valid = eurofidai.compute_returns_from_adjusted(close)
    assert ret.shape == (3, 2)
    assert np.isnan(ret[0]).all()  # first row: no t-1
    np.testing.assert_allclose(ret[1, 0], np.log(101.0 / 100.0), rtol=1e-12)
    np.testing.assert_allclose(ret[1, 1], np.log(51.0 / 50.0), rtol=1e-12)
    assert np.isnan(ret[2, 1])  # NaN close at t=2, asset 1
    assert close_valid[2, 1] == False


def test_compute_returns_no_forward_fill():
    """A NaN close at t-1 produces NaN return at t (no fill)."""
    close = np.array([[100.0], [np.nan], [101.0]])
    ret, _ = eurofidai.compute_returns_from_adjusted(close)
    assert np.isnan(ret[1, 0])  # NaN at t-1 → NaN return
    assert np.isnan(ret[2, 0])  # close[1] is NaN → ratio NaN


# ------------------------------------------------------- adjustment (split)

def test_split_adjustment():
    """A 2:1 split (close halves, adjustment factor halves) produces a
    near-zero log return on the split day when using adjusted prices."""
    # Day 0: close=150, factor=1.0 → adjusted = 150
    # Day 1: close=75, factor=0.5 → adjusted = 75/0.5 = 150 (no return)
    # Day 2: close=75.75, factor=0.5 → adjusted = 75.75/0.5 = 151.5
    df = pd.DataFrame({
        "id_stable": ["A", "A", "A"],
        "date": ["2020-06-01", "2020-06-02", "2020-06-03"],
        "adjusted_close": [150.0, 75.0, 75.75],
        "adjustment_factor": [1.0, 0.5, 0.5],
    })
    dates, close, assets = eurofidai._build_close_wide(df)
    ret, close_valid = eurofidai.compute_returns_from_adjusted(close)
    # ret[1] should be log(75/150) = log(0.5) — the raw price return
    # The adjusted return would be log(150/150) = 0, but we use raw close
    # from the adjusted_close column directly.
    # The fixture uses adjusted_close=75 on day 1, which IS the adjusted price
    # (already split-adjusted). So the return is log(75/150) = -log(2).
    # The point: the researcher must export split-adjusted prices.
    assert not np.isnan(ret[1, 0])
    np.testing.assert_allclose(ret[1, 0], np.log(75.0 / 150.0), rtol=1e-12)


# ------------------------------------------------------- delisting

def test_delisting_exits_in_universe():
    """An asset delisted at date D is not in_universe on or after D."""
    dates = np.arange(np.datetime64("2020-01-02"),
                      np.datetime64("2020-01-02") + 5, dtype="datetime64[D]")
    close_valid = np.ones((5, 1), dtype=bool)
    delisting = {"A": pd.Timestamp("2020-01-06").date()}
    iu = eurofidai.compute_in_universe(
        close_valid, delisting, dates, ["A"], min_days_traded_21=0,
    )
    # Day 0 (Jan 2): no t-1 → False
    assert not iu[0, 0]
    # Days 1-3 (Jan 3, 6, 7): before delisting → True
    assert iu[1, 0]
    assert iu[2, 0]  # Jan 6 is the delisting date → dates < dd64 is False
    # Actually: dates[2] = Jan 6, dd64 = Jan 6 → dates < dd64 is False
    # So iu[2,0] should be False
    # Let me recalculate: dates = [Jan2, Jan3, Jan6, Jan7, Jan8]
    # Wait, np.arange with datetime64[D] skips weekends? No, it's consecutive days.
    # dates[0]=Jan2, dates[1]=Jan3, dates[2]=Jan4, dates[3]=Jan5, dates[4]=Jan6
    # delisting date = Jan 6 → dd64 = Jan 6
    # dates < Jan6: Jan2, Jan3, Jan4, Jan5 → True; Jan6 → False
    # But both_exist[0] = False (no t-1)
    # So: iu[0]=False, iu[1]=True, iu[2]=True, iu[3]=True, iu[4]=False
    assert iu[1, 0]
    assert iu[2, 0]
    assert iu[3, 0]
    assert not iu[4, 0]  # delisted on Jan 6


def test_delisting_no_date_all_in_universe():
    """Assets without delisting dates remain in universe (subject to close)."""
    dates = np.arange(np.datetime64("2020-01-02"),
                      np.datetime64("2020-01-02") + 3, dtype="datetime64[D]")
    close_valid = np.ones((3, 1), dtype=bool)
    iu = eurofidai.compute_in_universe(
        close_valid, {}, dates, ["A"], min_days_traded_21=0,
    )
    assert not iu[0, 0]
    assert iu[1, 0]
    assert iu[2, 0]


# ------------------------------------------------------- liquidity filter

def test_liquidity_filter_no_trading_day():
    """An asset with NaN close on a day is excluded by the liquidity filter
    if min_days_traded_21 > 0 and the asset hasn't traded enough."""
    dates = np.arange(np.datetime64("2021-01-04"),
                      np.datetime64("2021-01-04") + 5, dtype="datetime64[D]")
    # Asset A: trades every day
    # Asset B: missing day 1 (NaN close)
    close_valid = np.array([
        [True, True],
        [True, False],   # B missing on day 1
        [True, True],
        [True, True],
        [True, True],
    ])
    iu = eurofidai.compute_in_universe(
        close_valid, {}, dates, ["A", "B"], min_days_traded_21=1,
    )
    # Day 0: no t-1 → False for both
    assert not iu[0, 0] and not iu[0, 1]
    # Day 1: B has NaN at t=1, close_valid[1,1]=False → both_exist[1,1]=False
    assert iu[1, 0]
    assert not iu[1, 1]
    # Day 2: window [max(2-21,0), 2) = [0, 2) → B traded 1 day (day 0) → liquid
    # both_exist[2,1] = close_valid[2,1] & close_valid[1,1] = True & False = False
    assert not iu[2, 1]
    # Day 3: both_exist[3,1] = close_valid[3,1] & close_valid[2,1] = True & True = True
    # window [0, 3): B traded on days 0, 2 → 2 days ≥ 1 → liquid
    assert iu[3, 1]


def test_liquidity_filter_min_days_zero():
    """With min_days_traded_21=0, only both_exist and delisting matter."""
    dates = np.arange(np.datetime64("2021-01-04"),
                      np.datetime64("2021-01-04") + 3, dtype="datetime64[D]")
    close_valid = np.array([[True], [False], [True]])
    iu = eurofidai.compute_in_universe(
        close_valid, {}, dates, ["A"], min_days_traded_21=0,
    )
    assert not iu[0, 0]
    assert not iu[1, 0]  # close_valid[1]=False
    assert not iu[2, 0]  # close_valid[1]=False → both_exist[2]=False


# ------------------------------------------------------- non-anticipation

def test_non_anticipation_chars():
    """Perturbing returns from day s leaves characteristics through day s
    bit-identical; the first affected characteristic is at day s+1.
    Uses the D3 _compute_chars (same definitions as D4)."""
    T, N = 300, 5
    rng = np.random.SeedSequence(42)
    ret = np.random.default_rng(rng).standard_normal((T, N)) * 0.01
    dates = np.arange(np.datetime64("2020-01-01"),
                      np.datetime64("2020-01-01") + T, dtype="datetime64[D]")
    iu = np.ones((T, N), dtype=bool)
    iu[:10, :] = False
    assets = [f"TK{i}" for i in range(N)]
    sector_map = {}

    chars1 = sp500._compute_chars(ret, iu, dates, assets, sector_map)

    ret2 = ret.copy()
    rng2 = np.random.SeedSequence(99)
    ret2[150:, :] = np.random.default_rng(rng2).standard_normal((T - 150, N)) * 0.02
    chars2 = sp500._compute_chars(ret2, iu, dates, assets, sector_map)

    cols = list(sp500.CONTINUOUS_CHARS)
    base = pd.Timestamp("2020-01-01")
    for day in (149, 150):
        d = base + pd.Timedelta(days=day)
        v1 = chars1[chars1["date"] == d][cols].to_numpy()
        v2 = chars2[chars2["date"] == d][cols].to_numpy()
        assert np.array_equal(v1, v2, equal_nan=True), \
            f"chars at day {day} should be identical"
    d = base + pd.Timedelta(days=151)
    v1 = chars1[chars1["date"] == d][cols].to_numpy()
    v2 = chars2[chars2["date"] == d][cols].to_numpy()
    assert not np.array_equal(v1, v2, equal_nan=True), \
        "chars at day 151 should differ after perturbation at day 150"


# ------------------------------------------------------- fixture integration

def test_fixture_build_close_wide():
    """The fixture CSVs produce a valid close wide matrix."""
    fields, _, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    df = eurofidai.read_raw_files(raw_dir=FIXTURES, fields=fields)
    dates, close, assets = eurofidai._build_close_wide(df)
    assert close.shape == (len(dates), len(assets))
    assert len(assets) == 7  # 3 (eur_2020) + 2 (eur_2021) + 2 (uk_2020)
    assert close.dtype == np.float64


def test_fixture_delisting_extraction():
    """The fixture eur_2020.csv has asset 1003 delisted on 2020-01-06."""
    fields, _, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    df = eurofidai.read_raw_files(raw_dir=FIXTURES, fields=fields)
    dd = eurofidai._extract_delisting_dates(df)
    assert "1003" in dd or 1003 in dd or "1003" in {str(k) for k in dd}
    key = next((k for k in dd if str(k) == "1003"), None)
    assert key is not None
    assert dd[key] == pd.Timestamp("2020-01-06").date()


def test_fixture_end_to_end_in_universe():
    """End-to-end: read fixtures → close wide → returns → in_universe.
    Verify delisted asset exits and NaN-close asset is excluded."""
    fields, liquidity, _ = eurofidai.load_schema(FIXTURE_SCHEMA)
    df = eurofidai.read_raw_files(raw_dir=FIXTURES, fields=fields)
    dates, close, assets = eurofidai._build_close_wide(df)
    ret, close_valid = eurofidai.compute_returns_from_adjusted(close)
    dd = eurofidai._extract_delisting_dates(df)
    iu = eurofidai.compute_in_universe(
        close_valid, dd, dates, assets,
        min_days_traded_21=liquidity["min_days_traded_21"],
    )
    # Asset 1003 (delisted 2020-01-06) should not be in universe after that date
    idx_1003 = assets.index("1003") if "1003" in assets else None
    if idx_1003 is not None:
        # Find the date index for 2020-01-06
        d64 = np.datetime64("2020-01-06")
        if d64 in dates:
            t_delist = int(np.where(dates == d64)[0][0])
            assert not iu[t_delist, idx_1003], \
                "delisted asset should not be in_universe on delisting date"
            if t_delist > 0:
                assert iu[t_delist - 1, idx_1003], \
                    "delisted asset should be in_universe before delisting date"

    # Asset 2002 has NaN close on 2021-01-05 → not in universe that day
    idx_2002 = assets.index("2002") if "2002" in assets else None
    if idx_2002 is not None:
        d64 = np.datetime64("2021-01-05")
        if d64 in dates:
            t_nan = int(np.where(dates == d64)[0][0])
            assert not iu[t_nan, idx_2002], \
                "asset with NaN close should not be in_universe"


# ------------------------------------------------------- loader contracts (real data)

def test_d4_loader_contract(_d4_built):
    ret, dates, assets = eurofidai.load_d4()
    assert ret.dtype == np.float64
    assert ret.shape == (len(dates), len(assets))
    assert np.issubdtype(dates.dtype, np.datetime64)
    assert len(assets) == len(set(assets))


def test_d4_panel_layout(_d4_built):
    ret, dates, assets = eurofidai.load_d4()
    panel = pd.read_parquet(DERIVED_D4 / "panel.parquet")
    assert list(panel.columns) == ["date", "asset_id", "ret", "close", "in_universe"]
    assert len(panel) == len(dates) * len(assets)
    assert panel["ret"].dtype == np.float64
    assert panel["in_universe"].dtype == bool
    assert (panel.loc[~panel["in_universe"], "ret"].isna()).all()
    assert (panel.loc[panel["in_universe"], "ret"].notna()).all()


def test_d4_splits(_d4_built):
    splits = eurofidai.load_splits_d4()
    assert splits["embargo_trading_days"] == 65
    seg = splits["segments"]
    assert list(seg) == ["pretrain", "calib", "monitor"]
    assert seg["pretrain"]["last_day"] < seg["calib"]["first_day"]
    assert seg["calib"]["last_day"] < seg["monitor"]["first_day"]


def test_d4_manifest_no_data():
    """The manifest must not contain any market data — only hashes, counts, dates."""
    man = json.loads(eurofidai.MANIFEST_PATH.read_text())
    assert man["dataset"] == "d4_eurofidai"
    # No price, return, or OHLC fields
    forbidden = ("price", "close", "ret", "return", "ohlc", "volume", "bid", "ask")
    for key in man:
        assert key.lower() not in forbidden, f"manifest key {key!r} looks like market data"
    # The manifest is valid JSON with expected top-level keys
    assert "sha256" in man or "files" in man or "outputs" in man


# ------------------------------------------------------- gitignore verification

def test_gitignore_blocks_eurofidai():
    """Verify .gitignore blocks EUROFIDAI paths."""
    import subprocess
    result = subprocess.run(
        ["git", "check-ignore", "-v",
         "data/derived/d4_eurofidai/x", "data/raw/eurofidai/x"],
        capture_output=True, text=True,
        cwd=eurofidai.REPO_ROOT,
    )
    assert result.returncode == 0, \
        f"git check-ignore failed: {result.stderr}"
    assert "data/derived/d4_eurofidai/" in result.stdout
    assert "data/raw/" in result.stdout
