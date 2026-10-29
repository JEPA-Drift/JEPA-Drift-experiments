"""Tests of the characteristics pivot (stream 8b): jepadrift/data_loader/chars.py."""
import numpy as np
import pandas as pd
import pytest

from jepadrift.data_loader import chars, eurofidai, sp500
from test_injection import _d3_239_calib, _d3_239_to_2019

PRE_J4 = np.datetime64("2020-01-01")


@pytest.fixture(scope="module")
def d3_239():
    _, dates, assets = sp500.load_d3_239()
    rows = dates < PRE_J4
    C, names = chars.load_chars_tensor("d3_239", rows=rows)
    long = sp500.load_chars("d3_239")
    return C, names, dates[rows], assets, long[long["date"] < pd.Timestamp(PRE_J4)]


def test_alignment_on_sampled_pairs(d3_239):
    C, names, dates, assets, long = d3_239
    rows = long.set_index(["date", "asset_id"])[names]
    rng = np.random.default_rng(np.random.SeedSequence([82, 1]))
    for t, j in zip(rng.integers(0, len(dates), 50), rng.integers(0, len(assets), 50)):
        ref = rows.loc[[(pd.Timestamp(dates[t]), assets[j])]].to_numpy(dtype=np.float64)
        assert ref.shape == (1, len(names))
        assert np.array_equal(C[t, j], ref[0], equal_nan=True)


def test_shapes_and_nan_kept(d3_239):
    C, names, dates, assets, long = d3_239
    assert C.dtype == np.float64 and C.shape == (len(dates), 239, 15) and len(assets) == 239
    assert names == [c for c in long.columns if c.startswith("c_")] and len(long) == C.shape[0] * C.shape[1]
    assert int(np.isnan(C).sum()) == int(long[names].isna().to_numpy().sum()) > 0
    assert chars.load_chars_tensor("d3_239", rows=slice(100, 140))[0].tobytes() == C[100:140].tobytes()
    mask = np.zeros(len(sp500.load_d3_239()[1]), dtype=bool)
    mask[[5, 900, 4000]] = True
    assert chars.load_chars_tensor("d3_239", rows=mask)[0].tobytes() == C[[5, 900, 4000]].tobytes()
    _, dates500, assets500 = sp500.load_d3_500()
    C500, names500 = chars.load_chars_tensor("d3_500", rows=slice(4000, 4250))
    assert dates500[4249] < PRE_J4 and C500.shape == (250, len(assets500), 15) and names500 == names


def test_bit_equal_to_injection_pivot():
    _, start, stop = _d3_239_to_2019()
    C, _ = chars.load_chars_tensor("d3_239", rows=slice(start, stop))
    ref = _d3_239_calib()[1]
    assert C.shape == ref.shape and C.tobytes() == ref.tobytes()


def test_impute_zero(d3_239):
    C = d3_239[0][:300]
    before = C.tobytes()
    C0, n = chars.impute_zero(C)
    missing = np.isnan(C)
    assert n == int(missing.sum()) > 0 and not np.isnan(C0).any()
    assert (C0[missing] == 0.0).all() and C0[~missing].tobytes() == C[~missing].tobytes()
    assert C.tobytes() == before


def test_datasets_without_characteristics():
    with pytest.raises(ValueError, match="D2 has no characteristics"):
        chars.load_chars_tensor("d2_us97")
    with pytest.raises(ValueError, match="unknown dataset"):
        chars.load_chars_tensor("d1_etf4")


@pytest.mark.skipif(not (eurofidai.DERIVED_D4 / "chars.parquet").exists(), reason="D4 is not built in this tree")
def test_d4_shape():
    _, dates, assets = eurofidai.load_d4()
    C, names = chars.load_chars_tensor("d4_eurofidai", rows=slice(0, 20))
    assert dates[19] < PRE_J4 and C.shape == (20, len(assets), len(names))
    assert names[:4] == list(sp500.CONTINUOUS_CHARS)


LOADERS = {"d3_239": sp500.load_d3_239, "d3_500": sp500.load_d3_500, "d4_eurofidai": eurofidai.load_d4}


@pytest.mark.parametrize("dataset", sorted(LOADERS))
def test_load_universe_matches_finite_returns(dataset):
    if dataset == "d4_eurofidai" and not (eurofidai.DERIVED_D4 / "panel.parquet").exists():
        pytest.skip("D4 is not built in this tree")
    ret, dates, assets = LOADERS[dataset]()
    rows = dates < PRE_J4
    universe = chars.load_universe(dataset, rows=rows)
    assert universe.dtype == bool and universe.shape == (int(rows.sum()), len(assets))
    assert np.array_equal(universe, np.isfinite(ret[rows]))
    assert np.array_equal(chars.load_universe(dataset, rows=slice(1300, 1340)), universe[1300:1340])


def test_load_universe_refuses_d2():
    with pytest.raises(ValueError, match="D2 has no characteristics"):
        chars.load_universe("d2_us97")


def test_load_continuous_chars_selects_by_name(d3_239):
    C, names = d3_239[0], d3_239[1]
    C4 = chars.load_continuous_chars("d3_239", rows=slice(100, 140))
    assert C4.shape == (40, 239, 4) and C4.dtype == np.float64 and C4.flags["C_CONTIGUOUS"]
    for k, name in enumerate(sp500.CONTINUOUS_CHARS):
        assert np.array_equal(C4[..., k], C[100:140, :, names.index(name)], equal_nan=True)
