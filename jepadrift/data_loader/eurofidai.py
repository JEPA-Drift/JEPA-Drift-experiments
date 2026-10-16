"""D4 (EUROFIDAI European equities) panel built from researcher-exported CSV files.

EUROFIDAI data is proprietary: it never leaves the researcher's machine.
The researcher exports CSV files manually from the EUROFIDAI portal (see
`docs/sections/eurofidai_extraction_spec.md`) into `data/raw/eurofidai/`.
This module reads those files, applies a field-name mapping from
`configs/eurofidai_schema.yaml`, computes log returns, point-in-time
in_universe, a liquidity filter, and characteristics (same definitions as D3,
reusing `sp500._compute_chars`).

`python -m jepadrift.data_loader.eurofidai --build` writes, under
`data/derived/d4_eurofidai/`:

- panel.parquet (long: date, asset_id, ret, close, in_universe),
  ret_wide.npy (float64, NaN where not in_universe), dates.npy (datetime64[D]),
  assets.json, chars.parquet (date, asset_id, c_*), splits.yaml, flags.csv.

The manifest `docs/manifests/d4_manifest.json` records SHA-256 hashes,
counts and dates — never any market data.
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from jepadrift.data_loader import sp500

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_D4 = REPO_ROOT / "data" / "raw" / "eurofidai"
DERIVED_D4 = REPO_ROOT / "data" / "derived" / "d4_eurofidai"
SCHEMA_PATH = REPO_ROOT / "configs" / "eurofidai_schema.yaml"
MANIFEST_PATH = REPO_ROOT / "docs" / "manifests" / "d4_manifest.json"
LOGS_D4 = REPO_ROOT / "logs" / "d4"

EMBARGO = 65
PRETRAIN_START = np.datetime64("2005-01-01")
CALIB_START = np.datetime64("2016-01-01")
MONITOR_START = np.datetime64("2020-01-01")

# Internal field names (keys in schema fields mapping)
_INTERNAL_FIELDS = (
    "id_stable", "isin", "market", "date", "adjusted_close",
    "adjustment_factor", "total_return", "market_cap",
    "listing_status", "delisting_date", "index_membership",
)

# Required internal fields for building the panel
_REQUIRED_FIELDS = ("id_stable", "date", "adjusted_close")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_schema(path=None):
    """Load the EUROFIDAI field-name mapping from YAML.
    Returns (fields_dict, liquidity_dict, sectors_dict)."""
    p = Path(path) if path else SCHEMA_PATH
    cfg = yaml.safe_load(p.read_text())
    fields = cfg.get("fields", {})
    liquidity = cfg.get("liquidity", {"min_volume": 0, "min_days_traded_21": 1})
    sectors = cfg.get("sectors", {"enabled": False, "mapping": {}})
    return fields, liquidity, sectors


def _map_fields(df, fields):
    """Rename EUROFIDAI CSV columns to internal names using the schema mapping.
    Returns a DataFrame with internal column names."""
    rename = {}
    for internal, eurofidai_name in fields.items():
        if eurofidai_name in df.columns:
            rename[eurofidai_name] = internal
    return df.rename(columns=rename)


def read_raw_files(raw_dir=None, fields=None):
    """Read all CSV files from the raw EUROFIDAI directory.
    Returns a single DataFrame with internal column names.
    Raises FileNotFoundError if the directory is empty or absent."""
    raw = Path(raw_dir) if raw_dir else RAW_D4
    if fields is None:
        fields, _, _ = load_schema()
    if not raw.exists() or not raw.is_dir():
        raise FileNotFoundError(
            f"EUROFIDAI raw directory not found: {raw}. "
            "Export CSV files from the EUROFIDAI portal first "
            "(see docs/sections/eurofidai_extraction_spec.md)."
        )
    csv_files = sorted(raw.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files in {raw}. "
            "Export CSV files from the EUROFIDAI portal first "
            "(see docs/sections/eurofidai_extraction_spec.md)."
        )
    frames = []
    for f in csv_files:
        df = pd.read_csv(f, float_precision="round_trip")
        df = _map_fields(df, fields)
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    # Validate required fields
    missing = [c for c in _REQUIRED_FIELDS if c not in combined.columns]
    if missing:
        raise ValueError(
            f"Missing required columns after schema mapping: {missing}. "
            f"Available columns: {list(combined.columns)}. "
            "Check configs/eurofidai_schema.yaml."
        )
    return combined


def compute_returns_from_adjusted(close_wide):
    """Log returns from adjusted close prices. No forward-fill.
    Returns (ret, close_valid) where close_valid[t,i] = not NaN."""
    T, N = close_wide.shape
    ret = np.full((T, N), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = close_wide[1:] / close_wide[:-1]
    ret[1:] = np.log(ratio)
    close_valid = ~np.isnan(close_wide)
    return ret, close_valid


def compute_in_universe(close_valid, delisting_dates, dates, assets,
                        min_days_traded_21=1):
    """Point-in-time in_universe mask.

    in_universe[t, i] is True iff:
    - close[t, i] and close[t-1, i] both exist (return computable)
    - the asset is not delisted at t (delisting_date > t or no delisting date)
    - the asset has traded at least `min_days_traded_21` days in the
      trailing 21-day window (liquidity filter)

    Returns in_universe (T, N) bool array.
    """
    T, N = close_valid.shape
    both_exist = np.zeros((T, N), dtype=bool)
    both_exist[1:] = close_valid[1:] & close_valid[:-1]

    # Delisting: asset not in universe on or after delisting date
    not_delisted = np.ones((T, N), dtype=bool)
    for j, asset in enumerate(assets):
        dd = delisting_dates.get(asset)
        if dd is not None:
            dd64 = np.datetime64(pd.Timestamp(dd).date())
            not_delisted[:, j] = dates < dd64

    in_universe = both_exist & not_delisted

    # Liquidity filter: at least min_days_traded_21 trading days in [t-21, t)
    if min_days_traded_21 > 0:
        traded = close_valid.astype(np.int64)
        cn = np.concatenate([np.zeros((1, N), dtype=np.int64),
                             np.cumsum(traded, axis=0)])
        t_idx = np.arange(T)
        start = np.maximum(t_idx - 21, 0)
        n_traded = cn[t_idx] - cn[start]
        liquid = n_traded >= min_days_traded_21
        in_universe = in_universe & liquid

    return in_universe


def _build_close_wide(df):
    """Pivot the long DataFrame into (dates, close_wide, assets).
    Uses adjusted_close as the price series."""
    df = df.dropna(subset=["adjusted_close"]).copy()
    df["date"] = pd.to_datetime(df["date"])
    pivot = df.pivot_table(index="date", columns="id_stable",
                          values="adjusted_close", aggfunc="last")
    dates = np.asarray(pivot.index.values, dtype="datetime64[D]")
    assets = list(pivot.columns)
    close = pivot.to_numpy(dtype=np.float64)
    return dates, close, assets


def _extract_delisting_dates(df):
    """Extract per-asset delisting dates from the raw DataFrame.
    Returns dict: asset_id -> delisting_date (datetime.date) or absent."""
    if "delisting_date" not in df.columns:
        return {}
    sub = df.dropna(subset=["delisting_date", "id_stable"])
    sub = sub[sub["delisting_date"].astype(str).str.strip() != ""]
    if sub.empty:
        return {}
    sub = sub.copy()
    sub["_dd"] = pd.to_datetime(sub["delisting_date"]).dt.date
    # Take the earliest delisting date per asset
    result = sub.groupby("id_stable")["_dd"].min().to_dict()
    return result


def _realize_segments(dates):
    def last_before(boundary):
        return dates[dates < boundary][-1].astype("datetime64[D]").astype(object)

    def first_after(boundary):
        return dates[dates > boundary][EMBARGO].astype("datetime64[D]").astype(object)

    pretrain_first = dates[dates >= PRETRAIN_START][0]
    return {
        "pretrain": {"nominal_start": "2005-01-01", "nominal_end": "2016-01-01",
                     "first_day": pretrain_first.astype("datetime64[D]").astype(object),
                     "last_day": last_before(CALIB_START)},
        "calib": {"nominal_start": "2016-01-01", "nominal_end": "2020-01-01",
                  "first_day": first_after(CALIB_START),
                  "last_day": last_before(MONITOR_START)},
        "monitor": {"nominal_start": "2020-01-01", "nominal_end": None,
                    "first_day": first_after(MONITOR_START),
                    "last_day": dates[-1].astype("datetime64[D]").astype(object)},
    }


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


def _write_splits(out_dir, dates):
    splits = {
        "dataset": "d4_eurofidai",
        "embargo_trading_days": EMBARGO,
        "convention": (
            "65 trading days after each internal boundary (2016-01-01, 2020-01-01) are "
            "embargoed and excluded from the following segment; pretrain starts at the first "
            "panel day on/after 2005-01-01"
        ),
        "segments": _realize_segments(dates),
    }
    (out_dir / "splits.yaml").write_text(yaml.safe_dump(splits, sort_keys=False))


def _write_chars(out_dir, chars):
    chars.to_parquet(out_dir / "chars.parquet", index=False)


def _update_manifest(raw_dir, out_dir, dates, assets, in_universe, ret):
    """Update docs/manifests/d4_manifest.json with hashes, counts, dates.
    Never includes any market data."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    man = json.loads(MANIFEST_PATH.read_text()) if MANIFEST_PATH.exists() else {}

    man["dataset"] = "d4_eurofidai"
    man["source"] = "EUROFIDAI (proprietary)"
    man["n_assets"] = len(assets)
    man["n_days"] = len(dates)
    man["first_date"] = str(dates[0])
    man["last_date"] = str(dates[-1])

    # Hash raw CSV files
    raw = Path(raw_dir) if raw_dir else RAW_D4
    raw_files = sorted(raw.glob("*.csv")) if raw.exists() else []
    man["files"] = [
        {"name": f.name, "sha256": _sha256(f), "rows": sum(1 for _ in open(f)) - 1}
        for f in raw_files
    ]
    man["markets"] = sorted({f.stem.rsplit("_", 1)[0] for f in raw_files})

    # Hash output files
    out = Path(out_dir) if out_dir else DERIVED_D4
    outputs = {}
    for fname in ("panel.parquet", "ret_wide.npy", "dates.npy",
                  "assets.json", "chars.parquet", "splits.yaml", "flags.csv"):
        p = out / fname
        if p.exists():
            e = {"sha256": _sha256(p)}
            if fname == "assets.json":
                e["assets"] = len(assets)
            elif fname == "dates.npy":
                e["rows"] = len(dates)
                e["first_date"] = str(dates[0])
                e["last_date"] = str(dates[-1])
            elif fname == "ret_wide.npy":
                e["shape"] = list(ret.shape)
            elif fname == "panel.parquet":
                e["rows"] = len(dates) * len(assets)
            outputs[fname] = e
    man["outputs"] = outputs

    MANIFEST_PATH.write_text(json.dumps(man, indent=2) + "\n")
    return MANIFEST_PATH


# ---------------------------------------------------------------- loaders

def load_d4():
    """D4 EUROFIDAI panel: (ret, dates, assets), same contract as load_d3_239."""
    ret = np.load(DERIVED_D4 / "ret_wide.npy")
    dates = np.load(DERIVED_D4 / "dates.npy")
    assets = json.loads((DERIVED_D4 / "assets.json").read_text())
    return ret, dates, assets


def load_chars_d4():
    """Characteristics long DataFrame for D4."""
    return pd.read_parquet(DERIVED_D4 / "chars.parquet")


def load_splits_d4():
    """Split definition of D4 as a dict; segment dates are datetime.date."""
    return yaml.safe_load((DERIVED_D4 / "splits.yaml").read_text())


# ---------------------------------------------------------------- build

def build(raw_dir=None, schema_path=None):
    """Build the D4 derived panel from raw EUROFIDAI CSV exports.

    Reads CSV files from `raw_dir` (default: data/raw/eurofidai/),
    applies the field mapping from `schema_path` (default:
    configs/eurofidai_schema.yaml), computes log returns, point-in-time
    in_universe with liquidity filter, characteristics (same definitions
    as D3), and writes derived artefacts to data/derived/d4_eurofidai/.
    """
    LOGS_D4.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    log("=== D4 (EUROFIDAI) build ===")

    # Phase 1: load schema
    fields, liquidity, sectors_cfg = load_schema(schema_path)
    log(f"[1] schema loaded: {len(fields)} field mappings")

    # Phase 2: read raw CSV files
    log("[2] reading raw EUROFIDAI CSV files")
    df = read_raw_files(raw_dir=raw_dir, fields=fields)
    log(f"  {len(df)} rows, columns: {list(df.columns)}")

    # Phase 3: build close wide matrix
    log("[3] building close wide matrix")
    dates, close, assets = _build_close_wide(df)
    T, N = close.shape
    log(f"  calendar: {dates[0]}..{dates[-1]} ({T} days), {N} assets")

    # Phase 4: compute returns
    log("[4] computing log returns")
    ret, close_valid = compute_returns_from_adjusted(close)

    # Phase 5: extract delisting dates and compute in_universe
    log("[5] computing in_universe (point-in-time + liquidity)")
    delisting_dates = _extract_delisting_dates(df)
    min_days = liquidity.get("min_days_traded_21", 1)
    in_universe = compute_in_universe(
        close_valid, delisting_dates, dates, assets,
        min_days_traded_21=min_days,
    )
    n_in = int(in_universe.sum())
    log(f"  in_universe: {n_in}/{T * N} ({100 * n_in / (T * N):.1f}%)")
    log(f"  delisted assets: {len(delisting_dates)}")

    # Phase 6: write panel
    log("[6] writing panel")
    DERIVED_D4.mkdir(parents=True, exist_ok=True)
    n_panel = _write_panel(DERIVED_D4, dates, assets, ret, close, in_universe)
    log(f"  panel.parquet: {n_panel} rows")

    # Phase 7: write splits
    _write_splits(DERIVED_D4, dates)
    log("  splits.yaml written")

    # Phase 8: write flags
    n_flags = _write_flags(DERIVED_D4, dates, assets, ret, in_universe)
    log(f"  flags.csv: {n_flags} rows")

    # Phase 9: compute characteristics (reuse D3 definitions)
    log("[9] computing characteristics (D3 definitions)")
    sector_map = {}
    if sectors_cfg.get("enabled") and sectors_cfg.get("mapping"):
        sector_map = sectors_cfg["mapping"]
    chars = sp500._compute_chars(ret, in_universe, dates, assets, sector_map)
    _write_chars(DERIVED_D4, chars)
    log(f"  chars.parquet: {len(chars)} rows")

    # Phase 10: update manifest
    log("[10] updating manifest")
    man_path = _update_manifest(raw_dir, DERIVED_D4, dates, assets, in_universe, ret)
    log(f"  {man_path.relative_to(REPO_ROOT)} updated")

    (LOGS_D4 / "d4_build.log").write_text("\n".join(log_lines) + "\n")
    log("=== D4 build complete ===")
    return DERIVED_D4


def main():
    parser = argparse.ArgumentParser(
        description="Build the D4 (EUROFIDAI European equities) dataset of Article C.")
    parser.add_argument("--build", action="store_true",
                        help="build the derived panel from raw EUROFIDAI CSV exports")
    parser.add_argument("--raw-dir", type=str, default=None,
                        help="override the raw EUROFIDAI CSV directory")
    parser.add_argument("--schema", type=str, default=None,
                        help="override the schema YAML path")
    args = parser.parse_args()
    if args.build:
        build(raw_dir=args.raw_dir, schema_path=args.schema)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
