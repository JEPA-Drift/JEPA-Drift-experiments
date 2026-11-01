# TABLES_VALIDATION

- input: `results/pca_drift_benchmark/full_2000_20261101` ; run_fingerprint `ea702d03b9faf332d0ae74a7746422189b92854fbe728ceff9cb842a3ce7985a` ; schema `pca_drift_benchmark/2` ; run_mode `full` ; tables_schema `pca_drift_tables/1`
- identity recomputation: PASS

## Counters (validated input)

- selection.csv: 2422 rows ; metric_id references 610 -> 275 distinct ; classes S-EVAL 418 / S-CALFAIL 0 / S-NOEVAL 12 / S-CAND 1800 (théorie I/M/V conservée: 1800) / S-REAL 192 (S NA: 72 ; null_calibration_id renseigné: 0)
- aggregates.csv: 387 rows ; ALT_RMST OK 146 ; HOLDOUT OK 106 ; GAUSS checks 6 (non tabulés) ; REAL_EVENT_PATH 129 ; calfail 0
- calibration.csv: 106 rows ; OK 106 ; CALIBRATION_FAILED 0
- trials.csv: 716000 rows (calibration 212000 ; holdout_null 212000 ; alternative 292000) ; real_path 0
- issues.csv: 9 rows

## Tables

- Tableau_PCA_1: 180 rows in 9 blocks ; NA reasons 60
- Tableau_PCA_2: 220 rows in 11 blocks ; NA reasons 60
- Tableau_PCA_3: 44 rows in 9 blocks ; NA reasons 28
- T3R (Markdown sub-table, real episodes): 12 rows
- table_lineage.csv: 25888 rows (exact equality with the exported cell keys; unique, SOURCE/MANIFEST pointers resolve)

## Source SHA-256 (7 files)

- `manifest.json` : `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`
- `spectra.csv` : `fa518118b12e75eae5901f6addf4272172332d4e1beea4f5cd61d6b11c4d42bc`
- `selection.csv` : `19189d60580f03ffcb914ab29f242ea5b33fdcad220924d5b24dc4e7d6b41a5c`
- `calibration.csv` : `430e1e1097b6283d575b2b5538d8b6af5008da9ba47d0ef97287629b89507b2f`
- `trials.csv` : `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`
- `aggregates.csv` : `54a705298f4335a4c1fbbf2aa1511ec97679cfe6e640140265a8a8e3645480f5`
- `issues.csv` : `52c7e06aa2902066a931c120e1ddfb3bdca34a02d5091d1f8d3c3cde59dcf445`

## Controls

- F1 files present: PASS
- F2 schema /2: PASS
- F3 run fingerprint: PASS
- F4 config hash: PASS
- F5 output hashes (checked before any CSV parsing): PASS
- F6 CSV headers: PASS
- CSV parse under the /2 reading rules (malformed -> CSV_PARSE_FAILED): PASS
- F7 run-wide cells: PASS
- F8 closed enumerations: PASS
- primary keys unique: PASS
- selection row classes (S-EVAL/S-CALFAIL/S-NOEVAL/S-CAND/S-REAL): PASS
- foreign keys and accords: PASS
- aggregate classes; finiteness per metric_kind and effective count: deff/n_eff and det_lo/det_hi required finite at every n (n = 1 included), only rmst_sd/rmst_se/rmst_lo/rmst_hi may be NA at n = 1 and are required finite at n > 1, never non-finite: PASS
- trial inventory: every expected (group_id, role) present with its exact n / n_cal count, wrong roles and orphans refused: PASS
- calibration-failure coherence in both directions (§3.6; real D6 exception keeps blocked real statuses): PASS
- horizon H present and exactly 250 (H14): PASS
- real contract /2 (H15): PASS
- spectra coherence: PASS
- L16 E2 prefix = E1: PASS
- L17 E3 oracle copies = E2 at k = nmax: PASS
- L18 H3 q sums and rank orders: PASS
- T1/T2/T3 block completeness: PASS
- lineage: exact equality of the (table, row_id, column) keys of the exported cells and the lineage rows (no missing, duplicate or orphan), SOURCE/MANIFEST pointers resolve: PASS
- filters applied to every table row, the T3R sub-table and the lineage (no provenance row is emitted for a filtered-out row): PASS

## Regeneration command (deterministic; <OUT> is the literal output directory)

```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
.venv/bin/python experiments/pca_drift_tables.py --input-dir results/pca_drift_benchmark/full_2000_20261101 --output-dir <OUT> \
  --format both --strict
```
