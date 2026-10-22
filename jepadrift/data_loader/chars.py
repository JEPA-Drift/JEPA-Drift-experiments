"""Characteristics as a float64 (T, N, P) tensor on the ret_wide.npy grid of a panel (stream 8b)."""
import numpy as np
import pandas as pd

from jepadrift.data_loader import eurofidai, sp500

SOURCES = {"d3_239": (sp500.load_d3_239, lambda: sp500.load_chars("d3_239")),
           "d3_500": (sp500.load_d3_500, lambda: sp500.load_chars("d3_500")),
           "d4_eurofidai": (eurofidai.load_d4, eurofidai.load_chars_d4)}


def load_chars_tensor(dataset, rows=None):
    """(C, names): the c_* columns of chars.parquet in file order on dates.npy[rows] x assets.json, NaN kept."""
    if dataset == "d2_us97":
        raise ValueError("D2 has no characteristics")
    if dataset not in SOURCES:
        raise ValueError(f"unknown dataset {dataset!r}; expected one of {sorted(SOURCES)}")
    load_panel, load_long = SOURCES[dataset]
    _, dates, assets = load_panel()
    dates = dates if rows is None else dates[rows]
    long = load_long()
    names = [c for c in long.columns if c.startswith("c_")]
    idx = pd.MultiIndex.from_product([pd.DatetimeIndex(dates.astype("datetime64[ns]")), assets],
                                     names=["date", "asset_id"])
    C = long.set_index(["date", "asset_id"])[names].reindex(idx).to_numpy(dtype=np.float64)
    return C.reshape(len(dates), len(assets), len(names)), names


def impute_zero(C):
    """(C0, n_imputed): NaN characteristics read as 0 and their count, as in injection.inject (C-inject-F2-nan)."""
    missing = np.isnan(C)
    return np.where(missing, 0.0, C), int(missing.sum())
