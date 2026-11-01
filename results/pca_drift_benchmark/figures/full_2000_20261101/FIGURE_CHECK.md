# FIGURE_CHECK

- input: `results/pca_drift_benchmark/full_2000_20261101` ; run_fingerprint `ea702d03b9faf332d0ae74a7746422189b92854fbe728ceff9cb842a3ce7985a` ; schema `pca_drift_benchmark/2` ; run_mode `full`
- tables: `results/pca_drift_benchmark/tables/full_2000_20261101` ; tables_schema `pca_drift_tables/1` ; tables_fingerprint `06c5600b8468360fc555cc709d85c9965f071d6646e0c4c7c5675b66b7071f59`
- strict checks: PASS
- code SHA-256: `experiments/figures/plot_figure_1.py` `5346b314f858ed02621b5818a87902b09f79655302152f9ea151b9d32cdafa85`, `experiments/pca_drift_benchmark.py` `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`, `experiments/pca_drift_tables.py` `13d386fe12c24e0d9ddeb994a7a113043b541d5e2b52f9c497377eb7eb0f4c5c`

## Runner sources read (SHA-256)
- `spectra.csv`: `fa518118b12e75eae5901f6addf4272172332d4e1beea4f5cd61d6b11c4d42bc`
- `selection.csv`: `19189d60580f03ffcb914ab29f242ea5b33fdcad220924d5b24dc4e7d6b41a5c`
- `aggregates.csv`: `54a705298f4335a4c1fbbf2aa1511ec97679cfe6e640140265a8a8e3645480f5`
- `calibration.csv`: `430e1e1097b6283d575b2b5538d8b6af5008da9ba47d0ef97287629b89507b2f`
- `manifest.json`: `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`

## Table files read (SHA-256)
- `Tableau_PCA_1.csv`: `1db07a14dd58316cf6544fadc349b8655387687460002ed8f79c94e9a7d9e33e`
- `Tableau_PCA_2.csv`: `fa4523c28b91cac452dc9db476ffb3a0520d742cfbc955f2ddbeca76b8004ba7`
- `Tableau_PCA_3.csv`: `b91c7fd7a14b33cf8c5876baffe06c113f56f30831e3dffb40fe3dde64c1e345`
- `table_lineage.csv`: `bba1482eb3f1a03546220012f95c7d62edd00dc017b5b6f2d4554080970ad81a`

## Refusal chain (plan §5), all enforced in memory before any write: PASS
ENV_INVALID / INPUT_INVALID / TABLES_INCOMPLETE / TABLES_STALE / TABLE_CONTRACT_MISMATCH / TABLES_NOT_STRICT / IDENTITY_STRICT_FAILED / CODE_DRIFT / NOT_PREDECLARED / REAL_FIGURE_NOT_EXECUTED_SCHEMA_2 / BLOCK_MISSING / K_DOMAIN / PREFIX_IDENTITY_FAILED / LINEAGE_UNRESOLVED / SOURCE_MISMATCH / HORIZON_INCOMPATIBLE / SERIES_PROTOCOL_MISMATCH / V_NOT_COMPARABLE / EMPTY_SERIES / OUTPUT_NOT_EMPTY

## Per-figure counters and render checks
### Figure_1_mean (mean, role PRIMARY)
- source rows: 101 ; fpr_mismatch_k: [12] ; missing: {}
- render checks: text_in_frame PASS ; legend_disjoint PASS ; ylim_covers PASS ; font_min 6.0 pt ; PNG (1620, 1050) PASS ; issues: none
### Figure_1_mean_t7 (mean_t7, role ROBUSTNESS)
- source rows: 101 ; fpr_mismatch_k: [14] ; missing: {}
- render checks: text_in_frame PASS ; legend_disjoint PASS ; ylim_covers PASS ; font_min 6.0 pt ; PNG (1620, 1050) PASS ; issues: none
### Figure_1_cov (cov, role PRIMARY)
- source rows: 101 ; fpr_mismatch_k: [] ; missing: {}
- render checks: text_in_frame PASS ; legend_disjoint PASS ; ylim_covers PASS ; font_min 6.0 pt ; PNG (1620, 1050) PASS ; issues: none

## External render checks (results recorded in logs/pca_drift_figures/ and the wrapup)
- `pdftotext <OUT>/<stem>.pdf -` : expect `RMST250`, `model-based, not observed detection speed`
- `pdfinfo <OUT>/<stem>.pdf`
- `pdftoppm -r 100 -png <OUT>/<stem>.pdf <LOG>/<stem>.pdf_preview`
- `rsvg-convert -o <LOG>/<stem>.svg_preview.png <OUT>/<stem>.svg`
- `COV_SURROGATE_EXPLORATORY` present in the cov PDF text, absent from mean and mean_t7
