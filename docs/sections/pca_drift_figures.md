# PCA drift figures (stream 30) — output schema `pca_drift_figures/1`

`experiments/figures/plot_figure_1.py` renders `Figure_1_mean`, `Figure_1_cov` and `Figure_1_mean_t7` (SVG + PDF +
PNG + long source CSV + caption each) from **one sealed `pca_drift_benchmark/2` run directory** and its
**`pca_drift_tables/1` tables**. It is a read-only consumer: it never runs the runner, never rebuilds the tables,
recomputes no RMST/FPR and never overwrites an existing output directory. Plan `prompts/plans/plan-30.md` (GO
`prompts/GO-stream-30.md`); tests `tests/test_plot_figure_1.py`; deviation `C-pca-figures-design`. Every plotted cell
is resolved through `table_lineage.csv` to a `SOURCE` pointer in the runner CSVs and compared bit for bit (same
artifact, `%.17g` text); a `FORMULA`/`RULE` cell is never plotted.

## 1. Predeclared registry

Three entries, frozen in the module constant `SPECS` before any result is read:

| key | role | dataset | event | detector family | T2 objective | comparator | stem | tags |
|---|---|---|---|---|---|---|---|---|
| `mean` | PRIMARY | `SYNTH_GAUSS_EQUICORR` | `C_residual_mean` | `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM` | `MEAN_MIX_FLUID_SURROGATE` | — | `Figure_1_mean` | `SMOKE_NO_CLAIMS`, `GAUSSIAN_PROXY` |
| `mean_t7` | ROBUSTNESS | `SYNTH_T7_EQUICORR` | `C_residual_mean` | same | same | — | `Figure_1_mean_t7` | + `T7_ROBUSTNESS` |
| `cov` | PRIMARY | `SYNTH_GAUSS_EQUICORR` | `B_cov_rotate30` | `COV_QUADRATIC_VECH_SCAN` | `COV_JOINT_MIX_HEURISTIC` | `ENERGY_INDEX_COMPARATOR` / `ENERGY_INCREASE_CUSUM` (T3 row C) | `Figure_1_cov` | + `COV_SURROGATE_EXPLORATORY`, `EXPLORATORY_HEURISTIC`, `DETECTOR_FAMILY_MISMATCH` |

Mean and covariance never share a figure or a curve; the t7 background is never overlaid on the Gaussian one. The
whole right axis of the covariance figure carries `EXPLORATORY HEURISTIC: mean-mixture M is not a covariance
detector cost`; `V_cov = I_cov_joint/M(d, γ)` uses the mean-mixture cost, and Σq^cov is never plotted.

## 2. CLI, defaults and exit codes

```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
.venv/bin/python experiments/figures/plot_figure_1.py --input-dir <run> [--tables-dir <tables>] \
  [--output-dir <OUT>] [--figure mean|cov|both] [--dataset-id ...] [--event-id ...] [--cohort-id ...] \
  [--detector-family ...] [--objective-kind ...] [--strict]
```

`--input-dir` is required; `--tables-dir` defaults to `results/pca_drift_benchmark/tables/<basename(input-dir)>/`;
`--output-dir` defaults to `results/pca_drift_benchmark/figures/<basename(input-dir)>/` (the
`results/pca_drift_benchmark/figures/Figure_1_*` root is reserved for the full run; smoke figures never land there).
`--figure both` (default) produces the three entries; `--figure mean` produces `mean` and `mean_t7`; `--figure cov`
produces `cov`. The selector options are validated against `pdb.ENUMS` and act as selectors inside the registry. Exit
codes: 0 success; 2 refusal (below, or argparse usage); 3 incomplete write (I/O error: no `figure_manifest.json`,
partial files may remain, re-invocation on the directory is refused with 2).

## 3. Refusal codes (all enforced in memory before any directory is created)

`ENV_INVALID` (`pdb.check_env`), `INPUT_INVALID` (manifest/CSV presence, SHA-256 of the four read runner CSVs against
`manifest.outputs`, schema `pca_drift_benchmark/2`, `run_fingerprint == sha256(canon(identity))`),
`TABLES_INCOMPLETE` (`pdt.verify_output_dir`), `TABLES_STALE` (tables schema, input fingerprint, per-file SHA-256 of the
runner sources and of `manifest.json` via the tables provenance), `TABLE_CONTRACT_MISMATCH` (expected columns),
`TABLES_NOT_STRICT` / `IDENTITY_STRICT_FAILED` / `CODE_DRIFT` (`--strict` only),
`NOT_PREDECLARED` (selector combination outside the registry), `REAL_FIGURE_NOT_EXECUTED_SCHEMA_2`
(`--dataset-id D3_239` or any `--cohort-id`: schema /2 contains no executed real figure and no empty figure is
produced), `BLOCK_MISSING`, `K_DOMAIN` (k ≠ {1..20}), `PREFIX_IDENTITY_FAILED` (T2 prefix cells textually identical to
the T1 row, same artifact), `LINEAGE_UNRESOLVED` / `SOURCE_MISMATCH` (plotted cells), `HORIZON_INCOMPATIBLE`
(H = 250 everywhere referenced, ALT `time_origin` `ONSET_ALIGNED`), `SERIES_PROTOCOL_MISMATCH` (protocol constant over
k inside a series), `V_NOT_COMPARABLE` (same `info_kind`, same cost table M at the row's own dimension
`M_cost == manifest.costs["M"][d-1]`, same `gamma_M`; V is never recomputed), `EMPTY_SERIES` (no empty figure),
`OUTPUT_NOT_EMPTY`.

FPR comparability between prefix and selected at the same k is computed, never asserted by hand: (P) protocol identity
(`detector_family, null_id, threshold_rule, alpha, n_cal, n_holdout, H, alarm_rule, guarantee_basis, time_origin`) and
(W) Wilson overlap `max(lo_a, lo_b) ≤ min(hi_a, hi_b)`. A non-comparable k gets an `FPR mismatch` marker, a legend line
and the sentence « RMST differences at these k are not interpretable as speed differences at equal false-alarm rate »;
W is labelled a descriptive filter, not an equality test. Energy vs vech scan fails (P) by construction and carries the
permanent `DETECTOR_FAMILY_MISMATCH` label with « not an apples-to-apples test of two equally general detectors ».

## 4. Outputs (per registry entry, in `<OUT>/`)

`⟨stem⟩.svg/.pdf/.png` (3.5 × 5.4 in, 1050 × 1620 px at 300 dpi, DejaVu Sans, base 7 pt / min 6 pt, saved from the same
`Figure` object with `CreationDate`/`Date` nulled and tags as `Keywords`), `⟨stem⟩_source.csv` (long format:
`figure_key, panel, series, k, y, y_lo, y_hi, null_fpr, null_fpr_lo, null_fpr_hi, status, metric_id, null_metric_id,
table, row_id, source_key`; the energy comparator is one row at k NA; `FPR_MISMATCH` and not-measured markers have y
NA), `⟨stem⟩_caption.md` (English, generated from the manifest and the source CSV, with the sections *Measured (this
run)* / *Model-based (not tested here)* / *Status and limits*), plus one `FIGURE_CHECK.md` (hashes, fingerprints,
counters, PASS/FAIL of the in-process render checks, external render-check commands) and `figure_manifest.json` written
last via `.partial` + `os.replace` (`figures_fingerprint = sha256(canon({figures_schema, input, tables, code,
environment, filters, strict}))`).

The figure is drawn only from the source CSV re-read with `float_precision="round_trip"` after a `save_fair_csv`
round-trip, with manifest-derived strings as metadata; the same bytes are written to disk. Missing cells stay NaN (line
interrupted, no interpolation), get a « × » marker on the lower edge of their panel and a legend class (`blocked or
impossible`: `UNSUPPORTED`, `BLOCKED_*`, `NOT_EVALUABLE_STANDARD_SPLIT`, `DATA_UNAVAILABLE`, `CPV90_OUTSIDE_TOP20`;
`missing measure`: `CALIBRATION_FAILED`, `PATH_TOO_SHORT`). No paired uncertainty is exported; RMST intervals are the
producer's marginal `rmst_lo/hi` (`NORMAL_DEFF1`), FPR intervals Wilson. Smoke runs carry `SMOKE_NO_CLAIMS` on every
page, in every legend and in every manifest record.

## 5. Completeness

`verify_figures_dir(path)` (consumer API): `figure_manifest.json` exists and every file listed in its `outputs` exists
with its SHA-256. Two invocations with the same inputs and options produce byte-identical files (SVG, PDF, PNG, CSV,
Markdown, manifest), verified octet per octet.
