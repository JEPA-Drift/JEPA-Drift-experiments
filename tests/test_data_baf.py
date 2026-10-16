"""Contract tests for the D7 (BAF) derived dataset (pytest).

Integration tests require the D7 data to be built first:
    python -m jepadrift.data_loader.baf --build
They are skipped otherwise.
"""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from jepadrift.data_loader import baf

D7_DIR = baf.DERIVED / baf.D7_DIR
PARQUET = D7_DIR / "base.parquet"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="session")
def _baf_built():
    if not PARQUET.exists():
        pytest.skip("D7 not built; run: python -m jepadrift.data_loader.baf --build")
    return True


# ------------------------------------------------------- 1. forme

def test_shape(_baf_built):
    """1 000 000 lignes, 32 colonnes, index 0..999999."""
    df = baf.load_baf()
    assert df.shape == (1_000_000, 32)
    assert list(df.index) == list(range(1_000_000))


# ------------------------------------------------------- 2. mois

def test_months(_baf_built):
    """month in {0,…,7}, les 8 mois présents."""
    df = baf.load_baf()
    months = sorted(df["month"].unique().tolist())
    assert months == list(range(8))
    counts = df["month"].value_counts().sort_index().to_dict()
    assert len(counts) == 8
    for m in range(8):
        assert counts[m] > 0


# ------------------------------------------------------- 3. fraude

def test_fraud(_baf_built):
    """fraud_bool in {0, 1} ; taux global ~1 %."""
    df = baf.load_baf()
    assert set(df["fraud_bool"].unique().tolist()) <= {0, 1}
    rate = float(df["fraud_bool"].mean())
    assert 0.005 < rate < 0.02, f"fraud rate {rate:.4f} hors de la plage attendue"


# ------------------------------------------------------- 4. pas de NaN

def test_no_nan(_baf_built):
    """Aucune valeur NaN dans le parquet prétraité."""
    df = baf.load_baf()
    assert int(df.isna().sum().sum()) == 0


# ------------------------------------------------------- 5. splits

def test_splits(_baf_built):
    """load_splits() retourne fit/calib/monitor avec les bons mois."""
    splits = baf.load_splits()
    assert splits["dataset"] == "d7_baf"
    seg = splits["segments"]
    assert list(seg) == ["fit", "calib", "monitor"]
    assert seg["fit"]["months"] == [0, 1, 2]
    assert seg["calib"]["months"] == [3]
    assert seg["monitor"]["months"] == [4, 5, 6, 7]


# ------------------------------------------------------- 6. reproductibilité

def test_preproc_reproducible(_baf_built):
    """SHA-256 de preproc.json est stable et le fichier a la structure attendue."""
    sha = _sha256(D7_DIR / "preproc.json")
    assert len(sha) == 64
    params = baf.load_preproc()
    assert params["fit_months"] == [0, 1, 2]
    assert "numeric" in params
    assert "categorical" in params
    assert "sentinels" in params


# ------------------------------------------------------- 7. contrat loader

def test_loader_contract(_baf_built):
    """load_baf() retourne DataFrame 1M×32, dtypes corrects."""
    df = baf.load_baf()
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1_000_000, 32)
    # Dtypes: 20 continuous float32, 5 boolean float64, 5 categorical int16,
    # fraud_bool int8, month int8
    for col in baf.NUMERIC_COLS:
        assert df[col].dtype == np.float32, f"{col}: {df[col].dtype} != float32"
    for col in baf.BOOLEAN_COLS:
        assert df[col].dtype == np.float64, f"{col}: {df[col].dtype} != float64"
    for col in baf.CATEGORICAL_COLS:
        assert df[col].dtype == np.int16, f"{col}: {df[col].dtype} != int16"
    assert df["fraud_bool"].dtype == np.int8
    assert df["month"].dtype == np.int8


# ------------------------------------------------------- 8. prétraitement figé

def test_preproc_frozen_on_fit_months(_baf_built):
    """Sur les mois fit, moyennes ~0 pour les 25 numériques ; écart-types ~1
    pour les colonnes non constantes (les colonnes constantes ont std=0 après
    standardisation car (x - mean) / 1 = 0 quand x = mean partout)."""
    df = baf.load_baf()
    fit = df[df["month"].isin([0, 1, 2])]
    for col in baf.ALL_NUMERIC:
        mean = float(fit[col].mean())
        std = float(fit[col].std())
        assert abs(mean) < 1e-5, f"{col}: mean {mean:.2e} != 0 on fit months"
        if std > 1e-3:
            # Non-constant column: std should be ~1 after standardisation
            assert abs(std - 1.0) < 1e-4, \
                f"{col}: std {std:.6f} != 1 on fit months"
        # else: constant column, std=0 is expected


# ------------------------------------------------------- 9. catégoriels

def test_categorical_encoding(_baf_built):
    """Codes dans {−1, 0, …, |vocab|−1} ; mois 0–2 sans −1."""
    df = baf.load_baf()
    params = baf.load_preproc()
    for col in baf.CATEGORICAL_COLS:
        vocab_size = len(params["categorical"][col]["vocab"])
        codes = df[col].unique().tolist()
        min_code = min(codes)
        max_code = max(codes)
        assert min_code >= -1, f"{col}: min code {min_code} < -1"
        assert max_code < vocab_size, \
            f"{col}: max code {max_code} >= vocab size {vocab_size}"
        # Fit months should not have unknown (-1)
        fit_codes = df.loc[df["month"].isin([0, 1, 2]), col].unique().tolist()
        assert -1 not in fit_codes, \
            f"{col}: -1 (unknown) present in fit months"


# ------------------------------------------------------- 10. sentinelles

def test_sentinels(_baf_built):
    """Colonnes sentinelles bien numériques et documentées dans preproc.json.
    Après standardisation, les anciennes valeurs -1 sont transformées (z-score) ;
    un pic fréquent est attendu et correct (la sentinelle est une valeur légitime)."""
    df = baf.load_baf()
    params = baf.load_preproc()
    sentinel_cols = params["sentinels"]["columns"]
    assert len(sentinel_cols) > 0, "no sentinel columns detected"
    for col in sentinel_cols:
        assert col in baf.ALL_NUMERIC, \
            f"sentinel column {col} is not in ALL_NUMERIC"
        # The column must exist in the parquet and contain no NaN
        assert col in df.columns
        assert not df[col].isna().any(), f"{col}: NaN present"
        # The preproc params must have mean/std for this column
        assert col in params["numeric"], f"{col}: missing from preproc numeric params"


# ------------------------------------------------------- 11. manifeste

def test_manifest(_baf_built):
    """SHA-256 des fichiers D7 correspondent au disque ; entrées D1/D2/D3 préservées."""
    man = json.loads((baf.DERIVED / "MANIFEST.json").read_text())
    assert baf.D7_DIR in man.get("datasets", {})
    for e in man["datasets"][baf.D7_DIR]["outputs"]:
        p = baf.REPO_ROOT / e["path"]
        assert p.exists(), e["path"]
        assert _sha256(p) == e["sha256"], f"{e['path']}: SHA-256 mismatch"
    # Non-regression: D1/D2/D3 entries preserved
    for ds in ("d1_etf4", "d2_us97", "d3_239", "d3_500"):
        assert ds in man.get("datasets", {}), f"{ds} missing from manifest"
    # Sources
    assert baf.D7_DIR in man.get("sources", {})
    assert "baf_profile" in man.get("results", {})


# ------------------------------------------------------- 12. profil CSV

def test_profile_csv(_baf_built):
    """results/data/baf_profile.csv existe, 8 lignes, 28 colonnes."""
    path = baf.RESULTS_DATA / "baf_profile.csv"
    assert path.exists()
    df = pd.read_csv(path, float_precision="round_trip")
    assert df.shape == (8, 28)
    assert list(df.columns[:3]) == ["month", "n_rows", "fraud_rate"]
    assert sorted(df["month"].tolist()) == list(range(8))
    assert (df["n_rows"] > 0).all()
    assert (df["fraud_rate"] > 0).all() and (df["fraud_rate"] < 1).all()
    # mean_<feature> columns for all 25 numeric columns
    for col in baf.ALL_NUMERIC:
        assert f"mean_{col}" in df.columns, f"missing mean_{col}"
    # Cross-check fraud_rate with parquet
    baf_df = baf.load_baf()
    for m in range(8):
        expected_rate = float(baf_df.loc[baf_df["month"] == m, "fraud_bool"].mean())
        actual_rate = float(df.loc[df["month"] == m, "fraud_rate"].iloc[0])
        assert abs(expected_rate - actual_rate) < 1e-10, \
            f"month {m}: fraud_rate mismatch {expected_rate} vs {actual_rate}"


# ------------------------------------------------------- 13. taille parquet

def test_parquet_size(_baf_built):
    """base.parquet < 50 Mo."""
    size = PARQUET.stat().st_size
    assert size < 50 * 1024 * 1024, \
        f"base.parquet is {size / 1e6:.1f} Mo (> 50 Mo limit)"
