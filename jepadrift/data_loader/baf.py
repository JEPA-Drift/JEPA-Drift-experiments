"""D7 (BAF — Bank Account Fraud, Jesus et al., NeurIPS 2022) built from Kaggle.

`python -m jepadrift.data_loader.baf --build` downloads the BAF dataset via
the Kaggle API, verifies the six variants, converts the Base variant to a
preprocessed parquet (standardised numerics, encoded categoricals, parameters
fitted on months 0-2 only), and writes:

- data/derived/d7_baf/base.parquet (1M x 32, zstd, categoricals int16, < 50 Mo);
- data/derived/d7_baf/splits.yaml (fit months 0-2, calib month 3, monitor 4-7);
- data/derived/d7_baf/preproc.json (frozen preprocessing parameters);
- results/data/baf_profile.csv (per-month counts, fraud rate, raw feature means);
- data/derived/MANIFEST.json (merged with existing entries).

Raw CSV caches live under data/raw/baf/ (gitignored). The Kaggle package is
imported lazily inside the download function so that importing this module
(e.g. by the test suite) does not require kaggle.
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
RAW_BAF = REPO_ROOT / "data" / "raw" / "baf"
DERIVED = REPO_ROOT / "data" / "derived"
RESULTS_DATA = REPO_ROOT / "results" / "data"
LOGS_DATA = REPO_ROOT / "logs" / "data"

D7_DIR = "d7_baf"
KAGGLE_DATASET = "sgpjesus/bank-account-fraud-dataset-neurips-2022"
KAGGLE_API_VERSION = "1.6.17"

EXPECTED_COLUMNS = [
    "income", "name_email_similarity", "prev_address_months_count",
    "current_address_months_count", "customer_age", "days_since_request",
    "intended_balcon_amount", "payment_type", "zip_count_4w",
    "velocity_6h", "velocity_24h", "velocity_4w",
    "bank_branch_count_8w", "date_of_birth_distinct_emails_4w",
    "employment_status", "credit_risk_score", "email_is_free",
    "housing_status", "phone_home_valid", "phone_mobile_valid",
    "bank_months_count", "has_other_cards", "proposed_credit_limit",
    "foreign_request", "source", "session_length_in_minutes",
    "device_os", "keep_alive_session", "device_distinct_emails_8w",
    "device_fraud_count", "fraud_bool", "month",
]
EXPECTED_COL_SET = set(EXPECTED_COLUMNS)

NUMERIC_COLS = [
    "income", "name_email_similarity", "prev_address_months_count",
    "current_address_months_count", "customer_age", "days_since_request",
    "intended_balcon_amount", "zip_count_4w",
    "velocity_6h", "velocity_24h", "velocity_4w",
    "bank_branch_count_8w", "date_of_birth_distinct_emails_4w",
    "credit_risk_score", "email_is_free",
    "bank_months_count", "proposed_credit_limit",
    "session_length_in_minutes", "device_distinct_emails_8w",
    "device_fraud_count",
]

BOOLEAN_COLS = [
    "phone_home_valid", "phone_mobile_valid", "has_other_cards",
    "foreign_request", "keep_alive_session",
]

CATEGORICAL_COLS = [
    "payment_type", "employment_status", "housing_status",
    "source", "device_os",
]

ALL_NUMERIC = NUMERIC_COLS + BOOLEAN_COLS  # 25 columns standardised

VARIANT_FILES = [
    "Base.csv", "Variant I.csv", "Variant II.csv",
    "Variant III.csv", "Variant IV.csv", "Variant V.csv",
]

EXPECTED_ROWS = 1_000_000
EXPECTED_MONTHS = list(range(8))


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- download

def _download_baf(log):
    """Download the BAF dataset from Kaggle into data/raw/baf/."""
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    RAW_BAF.mkdir(parents=True, exist_ok=True)
    log(f"  downloading {KAGGLE_DATASET} -> {RAW_BAF.relative_to(REPO_ROOT)}/")
    api.dataset_download_files(KAGGLE_DATASET, path=str(RAW_BAF), unzip=True)
    log("  download complete")


# ---------------------------------------------------------------- controls

def _control_variants(log):
    """Verify the six CSV variants: presence, row count, and schema."""
    csv_files = sorted(RAW_BAF.glob("*.csv"))
    csv_names = [f.name for f in csv_files]
    log(f"  CSV files found: {csv_names}")

    # Check all six variants are present
    for vf in VARIANT_FILES:
        if vf not in csv_names:
            raise FileNotFoundError(f"Missing variant file: {vf} in {RAW_BAF}")

    # Row counts via wc -l (do not load all 6 CSVs into memory)
    for vf in VARIANT_FILES:
        path = RAW_BAF / vf
        out = subprocess.run(["wc", "-l", str(path)],
                             capture_output=True, text=True, check=True)
        n_lines = int(out.stdout.split()[0])
        n_rows = n_lines - 1  # subtract header
        log(f"  {vf}: {n_rows:,} rows")
        if n_rows != EXPECTED_ROWS:
            raise ValueError(
                f"{vf}: expected {EXPECTED_ROWS:,} rows, got {n_rows:,}")

    # Schema check on Base.csv (header + first rows)
    base_path = RAW_BAF / "Base.csv"
    header = pd.read_csv(base_path, nrows=0)
    cols = list(header.columns)
    log(f"  Base.csv columns ({len(cols)}): {cols}")

    if set(cols) != EXPECTED_COL_SET:
        missing = EXPECTED_COL_SET - set(cols)
        extra = set(cols) - EXPECTED_COL_SET
        raise ValueError(
            f"Column mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
    if len(cols) != 32:
        raise ValueError(f"Expected 32 columns, got {len(cols)}")

    # Read a sample for type validation
    sample = pd.read_csv(base_path, nrows=10000)
    log(f"  Sample dtypes: {dict(sample.dtypes.astype(str))}")

    # Strict validation: categorical columns should have limited cardinality
    for col in CATEGORICAL_COLS:
        n_unique = sample[col].nunique()
        log(f"  {col}: {n_unique} unique values in sample")
        if n_unique > 50:
            log(f"  WARNING: {col} has {n_unique} unique values (> 50); "
                f"verify it is truly categorical")

    # Strict validation: boolean columns must be {0, 1}
    for col in BOOLEAN_COLS:
        vals = set(sample[col].dropna().unique().tolist())
        log(f"  {col}: values {sorted(vals)}")
        if not vals <= {0, 1, 0.0, 1.0}:
            raise ValueError(
                f"{col}: expected boolean values {{0, 1}}, got {sorted(vals)}")

    # Month range
    months = sorted(sample["month"].unique().tolist())
    log(f"  month values in sample: {months}")

    return cols


# ---------------------------------------------------------------- preprocessing

def _detect_sentinels(df, log):
    """Detect columns containing -1 sentinel values in the fit months."""
    fit_mask = df["month"].isin([0, 1, 2])
    sentinel_cols = []
    for col in ALL_NUMERIC:
        n_minus_one = int((df.loc[fit_mask, col] == -1).sum())
        if n_minus_one > 0:
            sentinel_cols.append(col)
            log(f"  sentinel -1 detected in {col}: {n_minus_one:,} rows in fit months")
    return sentinel_cols


def _fit_preproc(df, sentinel_cols, log):
    """Fit preprocessing parameters on months 0-2 only.

    Returns (params_dict, df_preprocessed).
    """
    fit_mask = df["month"].isin([0, 1, 2])
    df_fit = df.loc[fit_mask]

    # --- standardisation of numerics ---
    numeric_params = {}
    for col in ALL_NUMERIC:
        mean = float(df_fit[col].mean())
        std = float(df_fit[col].std())
        if std == 0.0:
            std = 1.0
        numeric_params[col] = {"mean": mean, "std": std}

    # --- encodage of categoricals ---
    categorical_params = {}
    for col in CATEGORICAL_COLS:
        vocab = sorted(df_fit[col].dropna().unique().tolist())
        categorical_params[col] = {"vocab": vocab, "unknown_code": -1}
        log(f"  {col}: vocab size {len(vocab)}")

    params = {
        "fit_months": [0, 1, 2],
        "numeric": numeric_params,
        "categorical": categorical_params,
        "sentinels": {
            "description": (
                "Les valeurs -1 dans les attributs listes sont des sentinelles "
                "documentees dans la fiche BAF (missing/not applicable). Elles sont "
                "standardisees comme les autres valeurs (z-score) ; apres "
                "pretraitement, elles ne sont plus egales a -1."
            ),
            "columns": sentinel_cols,
        },
    }

    # --- apply preprocessing ---
    df_out = df.copy()

    for col in ALL_NUMERIC:
        mean = numeric_params[col]["mean"]
        std = numeric_params[col]["std"]
        df_out[col] = ((df[col].astype(np.float64) - mean) / std).astype(np.float64)

    for col in CATEGORICAL_COLS:
        vocab = categorical_params[col]["vocab"]
        unknown_code = categorical_params[col]["unknown_code"]
        mapping = {cat: i for i, cat in enumerate(vocab)}
        df_out[col] = (
            df[col].map(mapping).fillna(unknown_code).astype(np.int16)
        )

    # fraud_bool and month stay as-is (int)
    df_out["fraud_bool"] = df["fraud_bool"].astype(np.int8)
    df_out["month"] = df["month"].astype(np.int8)

    # Cast continuous numerics to float32 for parquet size (< 50 Mo);
    # boolean columns stay float64 per GO-stream-09.
    for col in NUMERIC_COLS:
        df_out[col] = df_out[col].astype(np.float32)

    return params, df_out


# ---------------------------------------------------------------- splits

def _write_splits():
    splits = {
        "dataset": D7_DIR,
        "convention": (
            "fit months 0-2, calib month 3, monitor months 4-7; "
            "no embargo (native drift in a synthetic dataset)"
        ),
        "segments": {
            "fit": {"months": [0, 1, 2]},
            "calib": {"months": [3]},
            "monitor": {"months": [4, 5, 6, 7]},
        },
    }
    out_dir = DERIVED / D7_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "splits.yaml"
    path.write_text(yaml.safe_dump(splits, sort_keys=False))
    return path


# ---------------------------------------------------------------- profile

def _write_profile(df_raw, log):
    """Write per-month profile on RAW (un-preprocessed) data."""
    rows = []
    for m in EXPECTED_MONTHS:
        sub = df_raw[df_raw["month"] == m]
        row = {
            "month": m,
            "n_rows": len(sub),
            "fraud_rate": float(sub["fraud_bool"].mean()),
        }
        for col in ALL_NUMERIC:
            row[f"mean_{col}"] = float(sub[col].mean())
        rows.append(row)

    cols = ["month", "n_rows", "fraud_rate"] + [f"mean_{c}" for c in ALL_NUMERIC]
    profile = pd.DataFrame(rows, columns=cols)
    RESULTS_DATA.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DATA / "baf_profile.csv"
    profile.to_csv(path, index=False)
    log(f"  {path.relative_to(REPO_ROOT)} ({len(profile)} rows)")
    return path


# ---------------------------------------------------------------- manifest

def _update_manifest(base_csv_sha, log):
    """Merge D7 entries into the existing MANIFEST.json."""
    man_path = DERIVED / "MANIFEST.json"
    man = json.loads(man_path.read_text()) if man_path.exists() else {}

    tag = "python -m jepadrift.data_loader.baf --build"
    gen = man.get("generator", "")
    man["generator"] = gen if tag in gen else (gen + "; " + tag if gen else tag)

    def out(rel, **kw):
        e = {"path": rel, "sha256": _sha256(REPO_ROOT / rel)}
        e.update(kw)
        return e

    out_dir = DERIVED / D7_DIR
    base_parquet = pd.read_parquet(out_dir / "base.parquet")
    outputs = [
        out("data/derived/d7_baf/base.parquet", rows=len(base_parquet)),
        out("data/derived/d7_baf/splits.yaml"),
        out("data/derived/d7_baf/preproc.json"),
    ]
    inputs = [
        {"path": "data/raw/baf/Base.csv", "sha256": base_csv_sha,
         "rows": EXPECTED_ROWS},
    ]
    man.setdefault("datasets", {})[D7_DIR] = {"inputs": inputs, "outputs": outputs}

    profile = pd.read_csv(RESULTS_DATA / "baf_profile.csv")
    man.setdefault("results", {})["baf_profile"] = out(
        "results/data/baf_profile.csv", rows=len(profile))

    man.setdefault("sources", {})[D7_DIR] = {
        "kaggle_dataset": KAGGLE_DATASET,
        "kaggle_api": KAGGLE_API_VERSION,
        "license": "CC BY 4.0 (see Kaggle dataset page)",
        "variants_checked": 6,
        "variant_converted": "Base",
    }

    man_path.write_text(json.dumps(man, indent=2) + "\n")
    return man_path


# ---------------------------------------------------------------- loaders

def load_baf():
    """Load the preprocessed BAF Base variant as a DataFrame (1M x 32)."""
    return pd.read_parquet(DERIVED / D7_DIR / "base.parquet")


def load_splits():
    """Split definition as a dict; segment months are lists of ints."""
    return yaml.safe_load((DERIVED / D7_DIR / "splits.yaml").read_text())


def load_preproc():
    """Preprocessing parameters as a dict (fitted on months 0-2)."""
    return json.loads((DERIVED / D7_DIR / "preproc.json").read_text())


# ---------------------------------------------------------------- build

def build(refresh=False):
    LOGS_DATA.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    log("=== D7 BAF build ===")
    log(f"refresh={refresh}")

    base_csv = RAW_BAF / "Base.csv"

    # Phase 1: download
    if not base_csv.exists() or refresh:
        log("[1] downloading BAF from Kaggle")
        _download_baf(log)
    else:
        log("[1] Base.csv already present; skipping download (use --refresh to force)")

    # Phase 2: controls
    log("[2] controls (6 variants, schema, strict validation)")
    _control_variants(log)

    # Phase 3: read Base.csv
    log("[3] reading Base.csv")
    dtype_map = {c: np.float64 for c in ALL_NUMERIC}
    dtype_map["fraud_bool"] = np.int64
    dtype_map["month"] = np.int64
    for c in CATEGORICAL_COLS:
        dtype_map[c] = "category"
    df = pd.read_csv(base_csv, dtype=dtype_map)
    log(f"  shape: {df.shape}")
    base_csv_sha = _sha256(base_csv)
    log(f"  Base.csv SHA-256: {base_csv_sha}")

    # Phase 4: preprocessing (fitted on months 0-2)
    log("[4] preprocessing (fitted on months 0-2)")
    sentinel_cols = _detect_sentinels(df, log)
    params, df_pre = _fit_preproc(df, sentinel_cols, log)

    out_dir = DERIVED / D7_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write preprocessed parquet (zstd, categoricals int16, continuous float32)
    log("  writing base.parquet (zstd)")
    df_pre.to_parquet(out_dir / "base.parquet", index=False,
                      compression="zstd", compression_level=19)
    parquet_size = (out_dir / "base.parquet").stat().st_size
    log(f"  base.parquet: {parquet_size / 1e6:.1f} Mo")
    if parquet_size > 50 * 1024 * 1024:
        raise ValueError(
            f"base.parquet is {parquet_size / 1e6:.1f} Mo (> 50 Mo limit)")

    # Write preproc.json
    preproc_path = out_dir / "preproc.json"
    preproc_path.write_text(json.dumps(params, indent=2) + "\n")
    log(f"  preproc.json written (sentinels: {len(sentinel_cols)} columns)")

    # Phase 5: splits
    log("[5] writing splits.yaml")
    _write_splits()

    # Phase 8: profile (on raw data)
    log("[8] writing baf_profile.csv (raw data)")
    _write_profile(df, log)

    # Phase 9: manifest
    log("[9] updating manifest")
    man_path = _update_manifest(base_csv_sha, log)
    log(f"  {man_path.relative_to(REPO_ROOT)} updated")

    (LOGS_DATA / "baf_build.log").write_text("\n".join(log_lines) + "\n")
    log("=== D7 BAF build complete ===")


def main():
    parser = argparse.ArgumentParser(
        description="Build and load the D7 (BAF) dataset of Article C.")
    parser.add_argument("--build", action="store_true",
                        help="rebuild every file under data/derived/d7_baf/")
    parser.add_argument("--refresh", action="store_true",
                        help="force re-download from Kaggle (ignore cache)")
    args = parser.parse_args()
    if args.build:
        build(refresh=args.refresh)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
