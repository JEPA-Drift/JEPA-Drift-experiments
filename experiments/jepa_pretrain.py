import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jepadrift import sim
from jepadrift.data_loader import sp500
from jepadrift.jepa import ca_tjepa


def synthetic_panel(T, N, start, rng, coupling):
    """x = 0.01 (f b' + eps + coupling g sign(C_1)), C = i.i.d. daily ranks; coupling = 0 is the no-coupling control."""
    dates = np.busday_offset(np.datetime64(start, "D"), np.arange(T), roll="forward")
    b = np.linspace(0.5, 1.5, N)
    f = sim.gaussian_latent(T, 1, rng)
    eps = sim.gaussian_latent(T, N, rng)
    C = (rng.random((T, N, ca_tjepa.N_CHARS)).argsort(axis=1).argsort(axis=1) + 0.5) / N - 0.5
    resid = coupling * sim.gaussian_latent(T, 1, rng) * np.sign(C[..., 0])
    return 0.01 * (f * b + eps + resid), C, dates, {"b": b, "f": f[:, 0]}


def _parquet_rows(path, columns, start, end, monitor_start):
    pf = pq.ParquetFile(path)
    i = pf.schema_arrow.get_field_index("date")
    tables = []
    for g in range(pf.metadata.num_row_groups):
        st = pf.metadata.row_group(g).column(i).statistics
        if st is None or not st.has_min_max:
            raise ValueError(f"{path}: row group {g} has no date bounds")
        lo, hi = pd.Timestamp(st.min), pd.Timestamp(st.max)
        if lo >= end or hi < start:
            continue
        if hi >= monitor_start:
            raise ValueError(f"{path}: row group {g} [{lo}, {hi}] overlaps monitor from {monitor_start}")
        t = pf.read_row_group(g, columns=["date", "asset_id", *columns])
        if pd.Timestamp(pc.min(t["date"]).as_py()) < lo or pd.Timestamp(pc.max(t["date"]).as_py()) > hi:
            raise ValueError(f"{path}: row group {g} violates its date bounds")
        kind = t["date"].type
        keep = pc.and_(pc.greater_equal(t["date"], pa.scalar(start, kind)), pc.less(t["date"], pa.scalar(end, kind)))
        tables.append(t.filter(keep))
    if not tables:
        raise ValueError(f"{path}: no row group holds rows in [{start}, {end})")
    return pa.concat_tables(tables).to_pandas()


def _on_grid(df, grid, columns, path):
    keys = pd.MultiIndex.from_frame(df[["date", "asset_id"]])
    if keys.has_duplicates:
        raise ValueError(f"{path}: {int(keys.duplicated().sum())} duplicate date x asset keys")
    if (missing := grid.difference(keys).size):
        raise ValueError(f"{path}: {missing} missing date x asset keys")
    if (extra := keys.difference(grid).size):
        raise ValueError(f"{path}: {extra} extra date x asset keys")
    values = df.set_index(keys)[columns].reindex(grid)
    if "in_universe" in columns and values["in_universe"].isna().any():
        raise ValueError(f"{path}: in_universe has null values")
    numeric = values.select_dtypes("number").to_numpy(dtype=np.float64)
    if np.isinf(numeric).any():
        raise ValueError(f"{path}: {int(np.isinf(numeric).sum())} infinite values")
    return values


def load_pretrain(directory, segments):
    """Pretrain rows of a D3 panel from the filtered Parquet row groups: (X, C, dates, assets); monitor never opened."""
    start = pd.Timestamp(segments["pretrain"]["first_day"])
    end = pd.Timestamp(segments["pretrain"]["nominal_end"])
    monitor = pd.Timestamp(segments["monitor"]["nominal_start"])
    all_dates = np.load(directory / "dates.npy", mmap_mode="r")
    i0, i1 = np.searchsorted(all_dates, np.array([start.to_datetime64(), end.to_datetime64()]).astype(all_dates.dtype))
    dates = np.array(all_dates[i0:i1])
    assets = json.loads((directory / "assets.json").read_text())
    grid = pd.MultiIndex.from_product([pd.DatetimeIndex(dates.astype("datetime64[ns]")), assets],
                                      names=["date", "asset_id"])
    shape = (len(dates), len(assets))
    names = list(sp500.CONTINUOUS_CHARS)
    C = _on_grid(_parquet_rows(directory / "chars.parquet", names, start, end, monitor), grid, names,
                 directory / "chars.parquet").to_numpy(dtype=np.float64).reshape(*shape, len(names))
    panel = _on_grid(_parquet_rows(directory / "panel.parquet", ["ret", "in_universe"], start, end, monitor), grid,
                     ["ret", "in_universe"], directory / "panel.parquet")
    U = panel["in_universe"].to_numpy(dtype=bool).reshape(shape)
    ret = panel["ret"].to_numpy(dtype=np.float64).reshape(shape)
    if np.isnan(ret[U]).any():
        raise ValueError(f"{directory / 'panel.parquet'}: {int(np.isnan(ret[U]).sum())} NaN return inside the universe")
    return np.where(U, ret, np.nan), np.ascontiguousarray(C), dates.astype("datetime64[D]"), assets


def train_real(X, C, dates, assets, cfg, seed, out, data):
    """Real-data training: the ordered, unique asset IDs of every column are mandatory and bound to the checkpoint."""
    if assets is None or len(assets) != X.shape[1] or len(set(assets)) != len(assets):
        raise ValueError(f"real-data training needs the {X.shape[1]} ordered, unique asset IDs of its columns")
    return ca_tjepa.train(X, C, dates, cfg, seed, out, data=data, assets=list(assets))


def smoke_window(dates, cfg):
    """Rows of the real-data smoke: smoke.days contiguous days ending smoke.validation_days after validation_start."""
    stop = int(np.searchsorted(dates, np.datetime64(cfg["train"]["validation_start"]))) + cfg["smoke"]["validation_days"]
    return slice(stop - cfg["smoke"]["days"], stop)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data", choices=("synthetic", "control", "d3_239"), required=True)
    parser.add_argument("--smoke", action="store_true", help="smoke.days days and smoke.epochs epochs")
    parser.add_argument("--d", type=int, choices=(2, 4, 8, 16), help="native output width, fixed before training")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("ckpt"))
    parser.add_argument("--fingerprints", type=Path, help="directory for checkpoint fingerprints, without weights")
    args = parser.parse_args(argv)
    cfg = yaml.safe_load(args.config.read_text())
    if args.d is not None:
        cfg["model"]["d"] = args.d
    if args.smoke:
        cfg["train"]["max_epochs"] = cfg["smoke"]["epochs"]
    t0 = time.perf_counter()
    if args.data == "d3_239":
        X, C, dates, assets = load_pretrain(sp500.DERIVED / sp500.D3_239_DIR, sp500.load_splits("d3_239")["segments"])
        if args.smoke:
            w = smoke_window(dates, cfg)
            X, C, dates = X[w], C[w], dates[w]
        path, metrics = train_real(X, C, dates, assets, cfg, args.seed, args.out,
                                   {"source": "d3_239 pretrain rows of the filtered Parquet row groups",
                                    "smoke": args.smoke})
    else:
        syn = cfg["synthetic"]
        coupling = 0.0 if args.data == "control" else syn["coupling"]
        X, C, dates, _ = synthetic_panel(cfg["smoke"]["days"] if args.smoke else syn["days"], syn["n_assets"],
                                         syn["start"], ca_tjepa.numpy_rng(args.seed, "data"), coupling)
        path, metrics = ca_tjepa.train(X, C, dates, cfg, args.seed, args.out,
                                       data={"source": f"synthetic:{args.data}", "coupling": coupling,
                                             "smoke": args.smoke})
    seconds = time.perf_counter() - t0
    (path / "run.json").write_text(json.dumps({"seconds": round(seconds, 3)}) + "\n")
    if args.fingerprints is not None:
        c, w = (path / "config.json").read_bytes(), (path / "weights.npy").read_bytes()
        record = {"checkpoint_sha256": path.name, "config_sha256": _sha(c), "weights_sha256": _sha(w),
                  "config": json.loads(c), "metrics": json.loads((path / "metrics.json").read_text())}
        args.fingerprints.mkdir(parents=True, exist_ok=True)
        (args.fingerprints / f"{path.name}.json").write_text(json.dumps(record, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"best_epoch": metrics["best_epoch"], **metrics["baseline"], "seconds": round(seconds, 1)}))
    print(f"CHECKPOINT_PATH={path.resolve()}")


if __name__ == "__main__":
    main()
