# TABLES_VALIDATION

- input: `results/pca_drift_benchmark/smoke_predictive_v2_closeout` ; run_fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443` ; schema `pca_drift_benchmark/2` ; run_mode `smoke` ; tables_schema `pca_drift_tables/1`
- identity recomputation: PASS

## Counters (validated input)

- selection.csv: 2422 rows ; metric_id references 610 -> 275 distinct ; classes S-EVAL 418 / S-CALFAIL 0 / S-NOEVAL 12 / S-CAND 1800 (théorie I/M/V conservée: 1800) / S-REAL 192 (S NA: 72 ; null_calibration_id renseigné: 0)
- aggregates.csv: 387 rows ; ALT_RMST OK 146 ; HOLDOUT OK 106 ; GAUSS checks 6 (non tabulés) ; REAL_EVENT_PATH 129 ; calfail 0
- calibration.csv: 106 rows ; OK 106 ; CALIBRATION_FAILED 0
- trials.csv: 14320 rows (calibration 4240 ; holdout_null 4240 ; alternative 5840) ; real_path 0
- issues.csv: 10 rows

## Tables

- Tableau_PCA_1: 180 rows in 9 blocks ; NA reasons 60
- Tableau_PCA_2: 220 rows in 11 blocks ; NA reasons 60
- Tableau_PCA_3: 44 rows in 9 blocks ; NA reasons 28
- T3R (Markdown sub-table, real episodes): 12 rows
- table_lineage.csv: 25888 rows (exact equality with the exported cell keys; unique, SOURCE/MANIFEST pointers resolve)

## Source SHA-256 (7 files)

- `manifest.json` : `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9`
- `spectra.csv` : `3718ed94123c0dad17505657383a1722d3e42d1f482b78b0d36f7efb28ca5e17`
- `selection.csv` : `f7b8406c7a73e0a19c905e9ef1104820b32d398269eecd6c40683c399f76655f`
- `calibration.csv` : `04d463b42556dfcd784ef4833c9f4cec789f194cb436c093ce8c25b370c4378d`
- `trials.csv` : `3dcf83a82685a014fafef213358305239866eaf0851ffcc525cdbe6c455aa7be`
- `aggregates.csv` : `6bd41250db9059abd19f4ec0976c8976fc54204e4321d66ad1b3a409c46e2f07`
- `issues.csv` : `d7a276f9a52e5ed798e7f0e59a8b73d5a36e1478dd7d4754618d4ded2ce72caf`

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
.venv/bin/python experiments/pca_drift_tables.py --input-dir results/pca_drift_benchmark/smoke_predictive_v2_closeout --output-dir <OUT> \
  --format both --strict
```
