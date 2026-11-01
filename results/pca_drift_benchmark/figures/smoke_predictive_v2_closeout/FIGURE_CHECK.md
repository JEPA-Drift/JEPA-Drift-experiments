# FIGURE_CHECK

- input: `results/pca_drift_benchmark/smoke_predictive_v2_closeout` ; run_fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443` ; schema `pca_drift_benchmark/2` ; run_mode `smoke`
- tables: `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout` ; tables_schema `pca_drift_tables/1` ; tables_fingerprint `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1`
- strict checks: PASS
- code SHA-256: `experiments/figures/plot_figure_1.py` `f2a0e7f0d014fa9301ce71ae276949e79c2e2f5e5e8256dd5603091a862bb048`, `experiments/pca_drift_benchmark.py` `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`, `experiments/pca_drift_tables.py` `13d386fe12c24e0d9ddeb994a7a113043b541d5e2b52f9c497377eb7eb0f4c5c`

## Runner sources read (SHA-256)
- `spectra.csv`: `3718ed94123c0dad17505657383a1722d3e42d1f482b78b0d36f7efb28ca5e17`
- `selection.csv`: `f7b8406c7a73e0a19c905e9ef1104820b32d398269eecd6c40683c399f76655f`
- `aggregates.csv`: `6bd41250db9059abd19f4ec0976c8976fc54204e4321d66ad1b3a409c46e2f07`
- `calibration.csv`: `04d463b42556dfcd784ef4833c9f4cec789f194cb436c093ce8c25b370c4378d`
- `manifest.json`: `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9`

## Table files read (SHA-256)
- `Tableau_PCA_1.csv`: `5dff24854e9fff2f2c66a3db44bb124ad6a19db083b1c5c46e397cf4ec796952`
- `Tableau_PCA_2.csv`: `31ebd1482549271f9e186989b17a21a2b475d3ad9cfe2dde1a96c8976f3c229b`
- `Tableau_PCA_3.csv`: `57707849f68d5d6f3e6ce229001f5772420732a98abfa967bfe445a32daa9a4f`
- `table_lineage.csv`: `f83eeffa947c24a8e8c17f4d91d718de4a95dd20cf735f8219860d2d44f8e6c6`

## Refusal chain (plan §5), all enforced in memory before any write: PASS
ENV_INVALID / INPUT_INVALID / TABLES_INCOMPLETE / TABLES_STALE / TABLE_CONTRACT_MISMATCH / TABLES_NOT_STRICT / IDENTITY_STRICT_FAILED / CODE_DRIFT / NOT_PREDECLARED / REAL_FIGURE_NOT_EXECUTED_SCHEMA_2 / BLOCK_MISSING / K_DOMAIN / PREFIX_IDENTITY_FAILED / LINEAGE_UNRESOLVED / SOURCE_MISMATCH / HORIZON_INCOMPATIBLE / SERIES_PROTOCOL_MISMATCH / V_NOT_COMPARABLE / EMPTY_SERIES / OUTPUT_NOT_EMPTY

## Per-figure counters and render checks
### Figure_1_mean (mean, role PRIMARY)
- source rows: 100 ; fpr_mismatch_k: [] ; missing: {}
- render checks: text_in_frame PASS ; legend_disjoint PASS ; ylim_covers PASS ; font_min 6.0 pt ; PNG (1620, 1050) PASS ; issues: none
### Figure_1_mean_t7 (mean_t7, role ROBUSTNESS)
- source rows: 100 ; fpr_mismatch_k: [] ; missing: {}
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
