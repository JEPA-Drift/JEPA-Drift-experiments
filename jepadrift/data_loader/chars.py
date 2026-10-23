"""Characteristics tensor (T, N, P) and in_universe mask on the ret_wide.npy grid of a panel (streams 8b, 17)."""
import numpy as np
import pandas as pd

from jepadrift.data_loader import eurofidai, sp500


def _flags(directory):
    return pd.read_parquet(directory / "panel.parquet", columns=["date", "asset_id", "in_universe"])


SOURCES = {"d3_239": (sp500.load_d3_239, lambda: sp500.load_chars("d3_239"),
                      lambda: _flags(sp500.DERIVED / sp500.D3_239_DIR)),
           "d3_500": (sp500.load_d3_500, lambda: sp500.load_chars("d3_500"),
                      lambda: _flags(sp500.DERIVED / sp500.D3_500_DIR)),
           "d4_eurofidai": (eurofidai.load_d4, eurofidai.load_chars_d4, lambda: _flags(eurofidai.DERIVED_D4))}


def _grid(dataset, rows):
    if dataset == "d2_us97":
        raise ValueError("D2 has no characteristics")
    if dataset not in SOURCES:
        raise ValueError(f"unknown dataset {dataset!r}; expected one of {sorted(SOURCES)}")
    _, dates, assets = SOURCES[dataset][0]()
    dates = dates if rows is None else dates[rows]
    idx = pd.MultiIndex.from_product([pd.DatetimeIndex(dates.astype("datetime64[ns]")), assets],
                                     names=["date", "asset_id"])
    return idx, (len(dates), len(assets))


def load_chars_tensor(dataset, rows=None):
    """(C, names): the c_* columns of chars.parquet in file order on dates.npy[rows] x assets.json, NaN kept."""
    idx, shape = _grid(dataset, rows)
    long = SOURCES[dataset][1]()
    names = [c for c in long.columns if c.startswith("c_")]
    C = long.set_index(["date", "asset_id"])[names].reindex(idx).to_numpy(dtype=np.float64)
    return C.reshape(*shape, len(names)), names


def load_continuous_chars(dataset, rows=None):
    """(T, N, 4) float64: the sp500.CONTINUOUS_CHARS columns of load_chars_tensor, selected by name, NaN kept."""
    C, names = load_chars_tensor(dataset, rows)
    return np.ascontiguousarray(C[..., [names.index(c) for c in sp500.CONTINUOUS_CHARS]])


def load_universe(dataset, rows=None):
    """in_universe of panel.parquet as a bool (T, N) array on dates.npy[rows] x assets.json; absent pairs are False."""
    idx, shape = _grid(dataset, rows)
    flags = SOURCES[dataset][2]().set_index(["date", "asset_id"])["in_universe"]
    return flags.reindex(idx, fill_value=False).to_numpy(dtype=bool).reshape(shape)


def impute_zero(C):
    """(C0, n_imputed): NaN characteristics read as 0 and their count, as in injection.inject (C-inject-F2-nan)."""
    missing = np.isnan(C)
    return np.where(missing, 0.0, C), int(missing.sum())
