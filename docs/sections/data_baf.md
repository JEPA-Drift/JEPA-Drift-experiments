# D7 (BAF — Bank Account Fraud) — derived dataset from Kaggle

D7 is the BAF (Bank Account Fraud) dataset of Jesus et al. (NeurIPS 2022 Datasets and
Benchmarks), downloaded from Kaggle (`sgpjesus/bank-account-fraud-dataset-neurips-2022`).
It is a synthetic tabular dataset of bank account opening requests, generated from real
data, spanning 8 months with a native drift. It is required for T-JEPA (prompt 15) and E9.

## Source and download

```bash
python -m jepadrift.data_loader.baf --build
```

The build downloads the dataset via the Kaggle API (credentials in `~/.kaggle/kaggle.json`
or `~/.kaggle/access_token`), verifies the six variants, converts the Base variant to a
preprocessed parquet, and writes the splits, preprocessing parameters, profile, and
manifest entries. Raw CSVs live under `data/raw/baf/` (gitignored).

- **Kaggle dataset**: `sgpjesus/bank-account-fraud-dataset-neurips-2022`
- **GitHub repo**: `feedzai/bank-account-fraud`
- **Paper**: Jesus et al., "BAF: A Benchmark for Bank Account Fraud Detection", NeurIPS 2022
  Datasets and Benchmarks
- **License**: CC BY 4.0 (Creative Commons Attribution 4.0 International)
- **Kaggle API**: `kaggle==1.6.17`

## Variants and controls

Six variants are downloaded, each with exactly 1 000 000 rows:

| Variant | Rows |
|---|---|
| `Base.csv` | 1 000 000 |
| `Variant I.csv` | 1 000 000 |
| `Variant II.csv` | 1 000 000 |
| `Variant III.csv` | 1 000 000 |
| `Variant IV.csv` | 1 000 000 |
| `Variant V.csv` | 1 000 000 |

Only `Base.csv` is converted. The other five are verified for presence and row count.

## Schema (32 columns)

| # | Column | Type | Treatment |
|---|---|---|---|
| 1 | `fraud_bool` | int (target) | Conservé tel quel (int8) |
| 2 | `income` | numeric (discrete, 9 values) | Standardisé (float32) |
| 3 | `name_email_similarity` | numeric continuous | Standardisé (float32) |
| 4 | `prev_address_months_count` | numeric (sentinel −1) | Standardisé (float32) |
| 5 | `current_address_months_count` | numeric (sentinel −1) | Standardisé (float32) |
| 6 | `customer_age` | numeric (discrete, 9 values) | Standardisé (float32) |
| 7 | `days_since_request` | numeric continuous | Standardisé (float32) |
| 8 | `intended_balcon_amount` | numeric continuous | Standardisé (float32) |
| 9 | `payment_type` | categorical (5: AA, AB, AC, AD, AE) | Encodé entier (int16) |
| 10 | `zip_count_4w` | numeric | Standardisé (float32) |
| 11 | `velocity_6h` | numeric continuous | Standardisé (float32) |
| 12 | `velocity_24h` | numeric continuous | Standardisé (float32) |
| 13 | `velocity_4w` | numeric continuous | Standardisé (float32) |
| 14 | `bank_branch_count_8w` | numeric | Standardisé (float32) |
| 15 | `date_of_birth_distinct_emails_4w` | numeric (discrete) | Standardisé (float32) |
| 16 | `employment_status` | categorical (7: CA–CG) | Encodé entier (int16) |
| 17 | `credit_risk_score` | numeric (sentinel −1) | Standardisé (float32) |
| 18 | `email_is_free` | numeric (0/1) | Standardisé (float32) |
| 19 | `housing_status` | categorical (7: BA–BG) | Encodé entier (int16) |
| 20 | `phone_home_valid` | boolean (0/1) | Standardisé (float64) |
| 21 | `phone_mobile_valid` | boolean (0/1) | Standardisé (float64) |
| 22 | `bank_months_count` | numeric (sentinel −1) | Standardisé (float32) |
| 23 | `has_other_cards` | boolean (0/1) | Standardisé (float64) |
| 24 | `proposed_credit_limit` | numeric (discrete, 12 values) | Standardisé (float32) |
| 25 | `foreign_request` | boolean (0/1) | Standardisé (float64) |
| 26 | `source` | categorical (2: INTERNET, TELEAPP) | Encodé entier (int16) |
| 27 | `session_length_in_minutes` | numeric (sentinel −1) | Standardisé (float32) |
| 28 | `device_os` | categorical (5: linux, macintosh, other, windows, x11) | Encodé entier (int16) |
| 29 | `keep_alive_session` | boolean (0/1) | Standardisé (float64) |
| 30 | `device_distinct_emails_8w` | numeric (sentinel −1) | Standardisé (float32) |
| 31 | `device_fraud_count` | numeric (constant 0) | Standardisé (float32, std=0) |
| 32 | `month` | int (0–7) | Conservé tel quel (int8) |

**Validation stricte au build** : les noms de colonnes doivent correspondre exactement
aux 32 attendus (erreur sinon) ; les colonnes catégorielles ne doivent pas dépasser 50
valeurs uniques (warning sinon) ; les colonnes booléennes doivent contenir uniquement
{0, 1} (erreur sinon).

## Sentinelles −1

Six colonnes contiennent des sentinelles −1 (missing/not applicable), détectées
automatiquement sur les mois 0–2 :

| Column | Fit rows with −1 | Description |
|---|---|---|
| `prev_address_months_count` | 280 119 | Pas d'adresse précédente |
| `current_address_months_count` | 1 595 | Moins d'un mois à l'adresse actuelle |
| `credit_risk_score` | 374 | Score de crédit non disponible |
| `bank_months_count` | 97 716 | Pas de compte bancaire précédent |
| `session_length_in_minutes` | 758 | Session non applicable |
| `device_distinct_emails_8w` | 184 | Information non disponible |

Les sentinelles sont standardisées comme les autres valeurs (z-score). Après
prétraitement, elles ne sont plus égales à −1. La liste est documentée dans
`preproc.json` (`sentinels.columns`).

## Prétraitement figé (appris sur les mois 0–2 uniquement)

- **Standardisation z-score** des 25 colonnes numériques (20 continues + 5 booléennes) :
  `mean` et `std` calculés sur les lignes `month ∈ {0, 1, 2}` ; `std = 0` remplacé par 1.
- **Encodage entier** des 5 catégorielles : vocabulaire construit sur les mois 0–2
  (`sorted(unique)`), mapping `category → code` (0, 1, 2, …). Inconnues en calib/monitor
  → code −1 (réservé).
- **Stockage** : 20 numériques continus en float32, 5 booléens en float64, 5 catégoriels
  en int16, `fraud_bool` en int8, `month` en int8. Compression zstd (niveau 19).

Les paramètres sont sauvegardés dans `data/derived/d7_baf/preproc.json`.

## Layout

```
data/derived/d7_baf/
├── base.parquet    # 1M × 32, zstd, 38.1 Mo (< 50 Mo)
├── splits.yaml     # fit/calib/monitor par mois
└── preproc.json    # paramètres de prétraitement
```

- `base.parquet` : index 0..999999 (ordre des lignes d'origine conservé), 32 colonnes.
- `splits.yaml` : `fit` mois 0–2, `calib` mois 3, `monitor` mois 4–7. Pas d'embargo
  (dérive native).
- `preproc.json` : `fit_months`, `numeric` (mean/std), `categorical` (vocab + unknown_code),
  `sentinels` (description + columns).

## Découpage

| Segment | Months | Rows |
|---|---|---|
| fit | 0, 1, 2 | 397 039 |
| calib | 3 | 150 936 |
| monitor | 4, 5, 6, 7 | 452 025 |

## Profil de fraude (données brutes)

`results/data/baf_profile.csv` (8 lignes × 28 colonnes) :

| month | n_rows | fraud_rate |
|---|---|---|
| 0 | 132 440 | 1.13 % |
| 1 | 127 620 | 0.94 % |
| 2 | 136 979 | 0.87 % |
| 3 | 150 936 | 0.92 % |
| 4 | 127 691 | 1.14 % |
| 5 | 119 323 | 1.18 % |
| 6 | 108 168 | 1.34 % |
| 7 | 96 843 | 1.47 % |

Le taux de fraude augmente de 0.87 % (mois 2) à 1.47 % (mois 7), cohérent avec la
**dérive native d'un jeu synthétique** (voir écart `C-BAF-synthetic`).

## Chargeur

```python
from jepadrift.data_loader import baf

df = baf.load_baf()          # DataFrame 1M × 32 (prétraité)
splits = baf.load_splits()   # dict (fit/calib/monitor)
params = baf.load_preproc()  # dict (paramètres de prétraitement)
```

## Notes

- `device_fraud_count` est constant à 0 sur l'ensemble du jeu (std=0). Après
  standardisation, toutes les valeurs sont 0.
- Les données brutes (`data/raw/baf/`) ne sont jamais commitées (gitigné par `data/raw/`).
- La dérive est **native** (synthetic dataset) : ne jamais la décrire comme « in-the-wild ».
