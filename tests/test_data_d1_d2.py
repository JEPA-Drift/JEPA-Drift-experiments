"""Contract tests for the D1 (ETF-4) and D2 (US-97) derived datasets (pytest)."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from jepadrift.data_loader import articleB as ab

ARTICLE_B = Path("~/The-Whitening-Advantage-Experiments").expanduser()
D1_EXPECTED = {"SPY": (6414, "2000-01-04"), "PFF": (4403, "2007-12-27"),
               "VNQ": (5014, "2005-01-04"), "BWX": (4451, "2007-10-09")}


@pytest.fixture(scope="session")
def rebuilt(tmp_path_factory):
    root = tmp_path_factory.mktemp("repo")
    (root / "data" / "derived").mkdir(parents=True)
    shutil.copyfile(ab.DERIVED / "MANIFEST.json", root / "data" / "derived" / "MANIFEST.json")
    with pytest.MonkeyPatch.context() as mp:
        for name, rel in (("REPO_ROOT", "."), ("DERIVED", "data/derived"), ("RESULTS_DATA", "results/data"),
                          ("LOGS_DATA", "logs/data")):
            mp.setattr(ab, name, root / rel)
        ab.build()
    return root


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_source_d1(tk):
    return pd.read_csv(ARTICLE_B / "data" / "derived_firstrate" / f"R01_daily_{tk}.csv",
                       float_precision="round_trip")


# ------------------------------------------------------------------ D1

def test_d1_loader_contract():
    ret, dates, assets = ab.load_d1()
    assert ret.dtype == np.float64
    assert ret.shape == (6414, 4)
    assert dates.shape == (6414,)
    assert np.issubdtype(dates.dtype, np.datetime64)
    assert dates[0] == np.datetime64("2000-01-04")
    assert dates[-1] == np.datetime64("2025-07-07")
    assert assets == ["SPY", "PFF", "VNQ", "BWX"]


def test_d1_panel_counts_and_ranges():
    panel = pd.read_parquet(ab.DERIVED / "d1_etf4" / "panel.parquet")
    assert list(panel.columns) == ["date", "asset_id", "ret", "close", "in_universe"]
    assert len(panel) == 6414 * 4
    assert panel["ret"].dtype == np.float64 and panel["close"].dtype == np.float64
    for tk, (n, first) in D1_EXPECTED.items():
        sub = panel[panel["asset_id"] == tk]
        obs = sub[sub["in_universe"]]
        assert len(obs) == n
        assert not obs["ret"].isna().any() and not obs["close"].isna().any()
        assert obs["date"].min() == pd.Timestamp(first)
        assert obs["date"].max() == pd.Timestamp("2025-07-07")
        out = sub[~sub["in_universe"]]
        assert out["ret"].isna().all() and out["close"].isna().all()


def test_d1_bit_exact_csv_parquet_numpy():
    ret, dates, assets = ab.load_d1()
    wide = np.full((6414, 4), np.nan)
    for j, tk in enumerate(assets):
        df = _read_source_d1(tk)
        idx = np.searchsorted(dates, np.asarray(pd.to_datetime(df["Date"]), dtype="datetime64[D]"))
        wide[idx, j] = df["log_ret"].to_numpy(dtype=np.float64)
    np.testing.assert_array_equal(ret, wide)
    panel = pd.read_parquet(ab.DERIVED / "d1_etf4" / "panel.parquet")
    piv = panel.pivot(index="date", columns="asset_id", values="ret")[assets]
    np.testing.assert_array_equal(piv.to_numpy(dtype=np.float64), ret)
    np.testing.assert_array_equal(piv.index.to_numpy(dtype="datetime64[D]"), dates)


# ------------------------------------------------------------------ D2

def test_d2_loader_contract():
    ret, dates, assets = ab.load_d2()
    assert ret.dtype == np.float64
    assert ret.shape == (5154, 97)
    assert dates[0] == np.datetime64("2005-01-04")
    assert dates[-1] == np.datetime64("2025-06-30")
    assert len(assets) == 97 and len(set(assets)) == 97
    assert not np.isnan(ret).any()


def test_d2_panel_layout():
    panel = pd.read_parquet(ab.DERIVED / "d2_us97" / "panel.parquet")
    assert len(panel) == 5154 * 97
    assert panel["in_universe"].all()
    assert panel["close"].isna().all()  # R15 carries log returns only
    assert not panel["ret"].isna().any()


def test_d2_zero_share_and_sign_corr_reference():
    ret, _, _ = ab.load_d2()
    zero_share = float((ret == 0).mean())
    assert 0.005 < zero_share < 0.008  # ~0.66% expected, reported not blocking
    corr = np.corrcoef((ret > 0).astype(np.float64), rowvar=False)
    iu = np.triu_indices_from(corr, 1)
    rho = float(corr[iu].mean())
    assert 0.20 < rho < 0.32  # ~0.26 expected, reported not blocking


def test_d2_bit_exact_csv_parquet_numpy():
    ret, _, assets = ab.load_d2()
    src = pd.read_csv(ARTICLE_B / "data" / "derived_equities" / "R15_panel_logreturns.csv",
                      float_precision="round_trip")
    assert list(src.columns[1:]) == assets
    np.testing.assert_array_equal(ret, src[assets].to_numpy(dtype=np.float64))
    panel = pd.read_parquet(ab.DERIVED / "d2_us97" / "panel.parquet")
    piv = panel.pivot(index="date", columns="asset_id", values="ret")[assets]
    np.testing.assert_array_equal(piv.to_numpy(dtype=np.float64), ret)


# ------------------------------------------------------------------ phases

def test_phases_variants():
    expected = {"lt_spy": (66, {"SPY": "lunde_timmermann", "*": "pagan_sossounov"}),
                "strict_ps": (48, {"*": "pagan_sossounov"}),
                "symmetric": (102, {"*": "lunde_timmermann"})}
    for variant, (n, algo) in expected.items():
        ph = ab.load_phases(variant)
        assert len(ph) == n
        assert (ph["dating_variant"] == variant).all()
        assert set(ph["ticker"]) <= {"SPY", "PFF", "VNQ", "BWX", "MACRO", "MESO_SPLIT"}
        for tk, a in ph[["ticker", "dating_algorithm"]].itertuples(index=False):
            assert a == algo.get(tk, algo["*"])


def test_phases_are_source_copy_plus_variant_column():
    src_dir = ARTICLE_B / "results" / "R16_regime_census" / "data"
    for variant, fname in ab.PHASE_VARIANTS.items():
        src = pd.read_csv(src_dir / fname, float_precision="round_trip")
        dst = ab.load_phases(variant)
        assert list(dst.columns) == list(src.columns) + ["dating_variant"]
        pd.testing.assert_frame_equal(dst[list(src.columns)], src)


def test_load_phases_rejects_unknown_variant():
    with pytest.raises(ValueError):
        ab.load_phases("nope")


# ------------------------------------------------------------------ splits

@pytest.mark.parametrize("dataset,pretrain_first,last_day", [
    ("d1", "2000-01-04", "2025-07-07"),
    ("d2", "2005-01-04", "2025-06-30"),
])
def test_splits_realized_dates(dataset, pretrain_first, last_day):
    splits = ab.load_splits(dataset)
    assert splits["embargo_trading_days"] == 65
    seg = splits["segments"]
    assert list(seg) == ["pretrain", "calib", "monitor"]
    assert str(seg["pretrain"]["first_day"]) == pretrain_first
    assert str(seg["pretrain"]["last_day"]) == "2015-12-31"
    assert str(seg["calib"]["first_day"]) == "2016-04-07"
    assert str(seg["calib"]["last_day"]) == "2019-12-31"
    assert str(seg["monitor"]["first_day"]) == "2020-04-06"
    assert str(seg["monitor"]["last_day"]) == last_day
    assert seg["pretrain"]["last_day"] < seg["calib"]["first_day"]
    assert seg["calib"]["last_day"] < seg["monitor"]["first_day"]

    _, dates, _ = ab.load_d1() if dataset == "d1" else ab.load_d2()
    calendar = set(np.datetime_as_string(dates, unit="D"))
    for s in seg.values():
        assert s["first_day"].isoformat() in calendar
        assert s["last_day"].isoformat() in calendar
    # embargo: the calib/monitor first day is the 66th trading day after the boundary
    for boundary, name in (("2016-01-01", "calib"), ("2020-01-01", "monitor")):
        after = dates[dates > np.datetime64(boundary)]
        assert str(after[65]) == seg[name]["first_day"].isoformat()


def test_load_splits_rejects_unknown_dataset():
    with pytest.raises(ValueError):
        ab.load_splits("d3")


# ------------------------------------------------------------------ profile

def test_profile_csv():
    df = pd.read_csv(ab.RESULTS_DATA / "d1_d2_profile.csv", float_precision="round_trip")
    assert list(df.columns) == ["dataset", "segment", "days", "assets", "zero_ret_share",
                                "mean_sign_corr", "k_eff", "pc1_var_share"]
    assert len(df) == 6
    assert set(df["dataset"]) == {"d1_etf4", "d2_us97"}
    assert set(df["segment"]) == {"pretrain", "calib", "monitor"}
    assert (df["days"] > 0).all()
    assert (df["assets"] > 1).all()
    assert ((df["zero_ret_share"] >= 0) & (df["zero_ret_share"] < 0.05)).all()
    assert np.allclose(df["k_eff"], 1.0 / df["mean_sign_corr"])
    assert ((df["pc1_var_share"] > 0) & (df["pc1_var_share"] < 1)).all()
    d2 = df[df["dataset"] == "d2_us97"]
    assert d2["assets"].eq(97).all()
    assert ((d2["mean_sign_corr"] > 0.15) & (d2["mean_sign_corr"] < 0.40)).all()


# ------------------------------------------------------------------ manifest

def test_manifest_hashes_and_source():
    man = json.loads((ab.DERIVED / "MANIFEST.json").read_text())
    assert man["source"]["path"] == "~/The-Whitening-Advantage-Experiments"
    head = subprocess.run(["git", "-C", str(ARTICLE_B), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    assert man["source"]["commit"] == head

    def resolve(p):
        return Path(p).expanduser() if p.startswith("~") else ab.REPO_ROOT / p

    entries = []
    for ds in ("d1_etf4", "d2_us97"):
        entries += man["datasets"][ds]["inputs"] + man["datasets"][ds]["outputs"]
    entries.append(man["results"]["d1_d2_profile"])
    assert len(entries) == 7 + 8 + 1 + 5 + 1
    for e in entries:
        p = resolve(e["path"])
        assert p.exists(), e["path"]
        assert _sha256(p) == e["sha256"], e["path"]

    d1_in = {e["path"].rsplit("/", 1)[-1]: e for e in man["datasets"]["d1_etf4"]["inputs"]}
    assert d1_in["R01_daily_SPY.csv"]["rows"] == 6414
    assert d1_in["R16_regime_census.csv"]["rows"] == 66
    assert d1_in["R16_regime_census_strict_ps.csv"]["rows"] == 48
    assert d1_in["R16_regime_census_symmetric.csv"]["rows"] == 102
    d2_in = man["datasets"]["d2_us97"]["inputs"][0]
    assert d2_in["rows"] == 5154
    assert d2_in["first_date"] == "2005-01-04" and d2_in["last_date"] == "2025-06-30"


def test_rebuild_reproduces_committed_files(rebuilt):
    files = sorted(p.relative_to(rebuilt) for p in rebuilt.rglob("*") if p.is_file())
    assert len(files) == 16
    for rel in files:
        assert _sha256(rebuilt / rel) == _sha256(ab.REPO_ROOT / rel), rel


def test_rebuild_manifest_matches_committed(rebuilt):
    new = json.loads((rebuilt / "data" / "derived" / "MANIFEST.json").read_text())
    old = json.loads((ab.DERIVED / "MANIFEST.json").read_text())
    assert new["source"] == old["source"]
    for ds in ("d1_etf4", "d2_us97"):
        assert new["datasets"][ds] == old["datasets"][ds], ds
    assert new["results"]["d1_d2_profile"] == old["results"]["d1_d2_profile"]
