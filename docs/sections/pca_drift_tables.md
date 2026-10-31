# PCA drift tables (stream 29) — output contract `pca_drift_tables/1`

`experiments/pca_drift_tables.py` assembles `Tableau_PCA_1/2/3` (CSV + Markdown) from **one sealed
`pca_drift_benchmark/2` run directory** (`--input-dir`, the seven files of stream 28: `manifest.json`, `spectra.csv`,
`selection.csv`, `calibration.csv`, `trials.csv`, `aggregates.csv`, `issues.csv`). It is a read-only consumer: it never
runs the runner, reads no real return, recomputes no RMST/FPR, and never overwrites an existing output directory.
Plan `prompts/plans/plan-29.md` (GO `prompts/GO-stream-29.md`, execution GO `prompts/GO-stream-29-vibe.md`); tests
`tests/test_pca_drift_tables.py`; deviation `C-pca-tables-design`. This document is the contract for the consumers
(streams 30 figures, 31 contracts): they read these files and never redo the joins.

## 1. Files written

One output directory per invocation, containing exactly (default `--format both`):

| file | content |
|---|---|
| `Tableau_PCA_1.csv` / `.md` | spectral reference, one row per (block, k = 1..nmax) |
| `Tableau_PCA_2.csv` / `.md` | prefix P_k vs selected S*_k, one row per (block, objective, k) |
| `Tableau_PCA_3.csv` / `.md` | ablations and ex-ante selection, fixed row order per group; the `.md` adds the `T3R` real-episode sub-table |
| `table_lineage.csv` | one row per displayed cell (see §5) |
| `TABLES_VALIDATION.md` | English validation report: counters, source SHA-256, controls, identity line, regeneration command |
| `table_manifest.json` | written last (`.partial` + `os.replace`); its presence + hashes define completeness |

`--format csv` writes the three CSVs, the lineage, the validation and the manifest, but no `.md` table files.
CSVs are written by `jepadrift.pipelines.save_fair_csv` (`%.17g` floats, `NaN` for NA, LF, no index): a cell copied from
a source CSV is textually identical to the source cell. Column dtypes: `float` → float64, `int` → Int64, `str` → str
(NA stays NA). Read them with `pandas.read_csv(path, dtype=str, float_precision="round_trip")` for text comparison.
Markdown is display-only: `fmt` renders `.4g` for λ/q/I/V, `.4f` for M/C, percent with one decimal for CPV/FPR, RMST with
one decimal, intervals as `x [lo, hi]`, `S` compacted as `{1–3, 10}`, `NA` for missing, `NOT_MEASURED` when a target
alpha exists without a measured FPR. The CSVs keep the unrounded source values.

## 2. Input contract (what is validated before anything is written)

All validation and table building happen in memory; a refusal exits 2 and creates no directory. Refusal codes
(`Refused.code`, printed as `refused: CODE: …` on stderr):

- files/schema/identity: `INPUT_DIR_MISSING`, `FILE_MISSING`, `TRIALS_MISSING` (the 7 files are always required on
  disk, `trials.csv` included — `TRIALS_LOCAL_ONLY` means untracked, not dispensable), `MANIFEST_INVALID`,
  `SCHEMA_MISMATCH` (schema `/2` at manifest root, `identity`, `config`, and `pdb.SCHEMA_VERSION`), `FINGERPRINT_MISMATCH`
  (F3), `CONFIG_HASH_MISMATCH` (F4), `OUTPUT_UNLISTED`, `HASH_MISMATCH` (F5 sha256+bytes, checked **before any CSV
  parsing**), `HEADER_MISMATCH` (F6), `CSV_PARSE_FAILED` (a well-hashed but malformed CSV — e.g. non-numeric text in a
  numeric column — is refused in a controlled way, never an uncaught traceback), `ROW_COUNT_MISMATCH`,
  `CELL_MISMATCH` (F7 run-wide cells), `ENUM_VIOLATION` (F8 closed enumerations + `claim_flag`).
- semantics: `DUPLICATE_PRIMARY_KEY`, `INVALID_S`, `UNEXPECTED_ROW_STATE` (row classes outside §3.3, and
  method/detector-family applicability), `FOREIGN_KEY_MISSING`, `ACCORD_MISMATCH`, `FOREIGN_NULL`, `NON_FINITE_METRIC`
  (finiteness required per `metric_kind` and per effective count: never FPR in an ALT_RMST nor RMST in a HOLDOUT;
  `deff`/`n_eff` and the Wilson detection bounds `det_lo`/`det_hi` are required present and finite at every executed
  n, n = 1 included — the producer sets `deff` = 1, `n_eff` = n and defined Wilson bounds even at n = 1; only
  `rmst_sd`/`rmst_se`/`rmst_lo`/`rmst_hi` may be NA at n = 1 and are required finite at n > 1; no metric field is
  ever non-finite),
  `CALIBRATION_NOT_OK`, `ORPHAN_TRIALS`, `TRIALS_COUNT_MISMATCH` (trial count or role wrong on an existing group),
  `TRIALS_GROUP_MISSING` (an expected `(group_id, role)` is absent — the inventory of expected groups is exactly the OK
  calibrations with role `calibration`/`n_cal` plus the OK ALT/HOLDOUT aggregates with role `alternative`/`holdout_null`
  and count `n`; an empty `trials.csv` is refused), no `real_path` trials,
  `INCOHERENT_CALIBRATION_FAILURE` (§3.6 five conditions, checked in both directions — failed selections/aggregates
  must reference a `CALIBRATION_FAILED` calibration, and a failed calibration must have the full synthetic cascade;
  a failed real D6 calibration keeps its documented exception: the blocked real rows keep their runner status and no
  synthetic cascade is required; a corruption is never masked by NA cells),
  `HORIZON_INCOMPATIBLE` (H present and exactly 250 in `manifest.config`, every ALT/HOLDOUT/REAL aggregate and every
  calibration — no truncation of a fractional value, no NA skip; ALT `time_origin` ONSET_ALIGNED),
  `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2`
  (under `/2` every real path is NOT_EXECUTED with all metric/R1–R5 fields NA, whatever `pre_j4.frozen_json_present`),
  `COHORT_MISSING`, `COHORT_ID_SHARED` (the two Covid cohorts share no filled `selection_id`/`metric_id`/`split_hash`/
  `null_calibration_id`; content fingerprints may be equal), `REAL_STATUS_MISMATCH`, `SPECTRA_INCONSISTENT`,
  `L16_PREFIX_IDENTITY`, `L17_E3_COPY`, `L18_Q_CONTROL` (H3: `sum(q[S]) == I_plugin_lw` exactly, `rank_order` exact),
  `PREFIX_NOT_COMPARABLE`, `T1_BLOCK_INCOMPLETE`, `T2_BLOCK_INCOMPLETE`, `T3_ROW_MISSING`,
  `LINEAGE_DUPLICATE`, `LINEAGE_INCOMPLETE`, `LINEAGE_ORPHAN` (a lineage key pointing at no exported cell, e.g. a
  row removed by a filter), `LINEAGE_SOURCE_UNKNOWN`, `LINEAGE_KEY_INVALID`,
  `LINEAGE_SOURCE_UNRESOLVED`, `LINEAGE_COLUMN_UNKNOWN`, `LINEAGE_MANIFEST_UNRESOLVED`.
- output/CLI: `OUTPUT_EXISTS` (non-empty output directory, exit 2, nothing is ever deleted), `IDENTITY_MISMATCH`
  (`--strict`), `INPUT_PATH_INVALID` / `INPUT_HASH_MISMATCH` (a declared identity input must be a relative repository
  path present on disk with its declared SHA-256), argparse usage (unknown `--dataset/--scenario/--detector-family`
  value, exit 2). Exit 3 = incomplete write (I/O error): no `table_manifest.json`, partial files may remain,
  re-invocation on the directory is refused (2).

Reading rules for the input CSVs: `float_precision="round_trip"`; `str` dtype for `*_id`, `*_hash`, `*_sha256`,
`run_fingerprint`, `group_id`, `S`, `rank_order`, `claim_flag`, `scope`, `detail`, `alarm_dates`,
`pre_onset_alarm_dates`, `maxima_sha256` (an all-digit identifier such as `1005596464754033` stays a string);
`Int64` for `k`, `d`, `reservoir_k`. The declared `/2` date metadata fields `fit_first_day` and `fit_last_day`
(spectra) are free text (ISO dates, e.g. a pre-2020 fit window such as `2016-04-07`/`2019-12-31`) and are never
parsed as numbers. Any other non-enum, non-free-text column must parse as numeric: a text cell there is
`CSV_PARSE_FAILED`.

`--strict` recomputes `pdb.identity_block` with the **current producer code** from the artifact's **declared** config
(`manifest.config`) and **declared** input set (`manifest.identity.inputs`, each path resolved under the repository
and hash-checked), and requires equality with `manifest.identity` — legitimate custom-config or additional-input
artifacts are accepted, drift is refused. It no longer reloads the default config file nor assumes `splits.yaml` only.
`TABLES_VALIDATION.md` states `identity recomputation: PASS` or `NOT RUN (no --strict)`.

## 3. Identifiers

- `block_id` = `pdb.sha16` of the canonical JSON of the block key:
  - T1: `{table:"T1", dataset_id, cohort_id, event_id, detector_family, objective_kind:"NONE"}`;
  - T2: `{table:"T2", dataset_id, cohort_id, event_id, detector_family, objective_kind}`;
  - T3: `{table:"T3", dataset_id, cohort_id, event_id}`; T3R: `{table:"T3R", dataset_id:"D3_239", cohort_id, event_id}`.
  `cohort_id` is `null` for synthetic blocks.
- `row_id` = `"<T>:<block_id>:<k|ordre>"` (T1/T2: k; T3: ordre; T3R: method).
- Tables are sorted deterministically (block key, then k / ordre).
- Methods, objectives, families and statuses are the closed enumerations of the runner (`pdb.ENUMS`):
  `detector_family` ∈ {`MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM`, `COV_QUADRATIC_VECH_SCAN`, `ENERGY_INCREASE_CUSUM`};
  `method` ∈ {`BASELINE_PREFIX`, `BASELINE_CPV90`, `ORACLE_Q_MIX`, `ORACLE_Q_AFFINE`, `EXANTE_QBAR`, `COV_JOINT_ORACLE`,
  `COV_MARGINAL_DIAGNOSTIC`, `ENERGY_INDEX_COMPARATOR`}; `objective_kind` ∈ {`NONE`, `CPV90_RULE`,
  `MEAN_MIX_FLUID_SURROGATE`, `MEAN_AFFINE_SURROGATE`, `EXANTE_QBAR_MIX_FLUID_SURROGATE`, `COV_JOINT_AFFINE_SURROGATE`,
  `COV_JOINT_MIX_HEURISTIC`, `COV_MARGINAL_MIX_DIAGNOSTIC`}; `status` adds `CPV90_OUTSIDE_TOP20`, `UNSUPPORTED`,
  `CALIBRATION_FAILED`, `BLOCKED_PRE_J4`, `NOT_EVALUABLE_STANDARD_SPLIT`, `DATA_UNAVAILABLE`.

## 4. Tables (CSV columns, names and effective types)

`table` is the literal `T1`/`T2`/`T3` (`T3R` in the Markdown sub-table only). Types: `int` = Int64, `float` = float64,
`str` = string, NA = `NaN`/empty.

**Tableau_PCA_1** (smoke: 9 blocks × 20 = 180 rows): block = (dataset_id, cohort_id, event_id, detector_family) of the
E1 `BASELINE_PREFIX` rows. Columns (48): `table, row_id, block_id, k:int, d:int, dataset_id, cohort_id, event_id,
detector_family, lambda_lw:float, cpv_lw:float, criteria, mp_count:int, mp_edge:float, kaiser_count:int,
cpv90_k_full:int, cpv90_status, rmst:float, rmst_lo:float, rmst_hi:float, det_rate:float, censored_share:float,
n_alt:int, fpr_test_null:float, fpr_lo:float, fpr_hi:float, n_eval:int, fpr_calibration:float, n_cal:int,
predictive_bound:float, target_fpr:float, threshold_rule, guarantee_basis, selection_id, metric_id, null_metric_id,
null_id, null_calibration_id, calibration_hash, basis_hash, split_hash, config_hash, seed:int, source_kind,
claim_scope, status, execution, na_reason`.
`criteria` marks `MP (corr.)` at k = mp_count, `CPV 90 %` at k = cpv90_k_full if ≤ nmax, `Kaiser corr. λ≥1` at
k = kaiser_count if ≤ nmax, else `—`; it never prints `λ<1`. Real rows in a smoke run have the spectra cells NA
(`REAL_NOT_RUN`) and all measures NA with the runner status in `status`/`na_reason`; their identifiers
(`selection_id`, `metric_id`, `null_calibration_id` when present) are always kept, and the calibration provenance
(`fpr_calibration`, `n_cal`, `predictive_bound`, `threshold_rule`, `guarantee_basis`) is filled whenever the source
row references a calibration — a missing holdout metric never erases a D6 calibration provenance.

**Tableau_PCA_2** (smoke: 11 blocks × 20 = 220 rows): block = T1 block + `objective_kind` of the E2 selector
(`block_family` = `MEAN`|`COV`). The prefix columns are the **same objects** as the T1 row of the same (block, k):
`rmst_prefix*` = T1 `rmst*`, `fpr_prefix*` = T1 `fpr_test_null`/`fpr_lo`/`fpr_hi`, `metric_id_prefix`,
`null_metric_id_prefix`, `lambda_lw`; no new join, no recomputation, no rounding (prerequisite comparability:
same dataset/cohort/split/family/null/basis/event_window and equal H, time_origin, n — else `PREFIX_NOT_COMPARABLE`).
Columns (65): `table, row_id, block_id, k:int, dataset_id, cohort_id, event_id, detector_family, objective_kind,
block_family, lambda_lw:float, q_k:float, q_info_type, q_source, I_marginal_cum_prefix:float, I_prefix:float,
V_prefix:float, V_prefix_meaning, rmst_prefix:float, rmst_prefix_lo:float, rmst_prefix_hi:float, fpr_prefix:float,
fpr_prefix_lo:float, fpr_prefix_hi:float, metric_id_prefix, null_metric_id_prefix, selection_id_prefix, S_star,
d_star:int, I_star:float, V_star:float, V_star_meaning, rmst_selected:float, rmst_selected_lo:float,
rmst_selected_hi:float, fpr_selected:float, fpr_selected_lo:float, fpr_selected_hi:float, metric_id_subset,
null_metric_id_subset, selection_id_subset, I_pop_joint_prefix:float, I_pop_joint_star:float,
pop_offdiag_max_star:float, selector_kind, selection_exact, tie_broken, oracle_input, claim_flag, info_kind,
status_prefix, status_subset, null_calibration_id, null_calibration_id_subset, calibration_hash, basis_hash,
split_hash, config_hash, seed:int, n_alt:int, n_eval:int, n_cal:int, source_kind, claim_scope, na_reason`.
Mean q: `q_k` = H3 recipe `pdb.q_plugin(beta_nonzero, lambda_lw[:nmax])[k-1]` (`q_source = FORMULA_Q_PLUGIN`,
`q_info_type = MEAN_GAUSSIAN_PROXY`); `I_pop_joint_*` is shown separately (exact only on the Gaussian background).
Covariance: `q_k` NA (`q_source = NOT_EXPORTED_SCHEMA_2`), `q_info_type = COV_GAUSSIAN_MARGINAL_PROXY` describes the
diagnostic `I_marginal_cum_prefix` (= prefix `I_cov_marginal_sum`, never the joint KL); `V_*_meaning =
COV_HEURISTIC_SURROGATE` with a warning above and below the block in the Markdown. Blocked real rows keep
`metric_id_subset`/`selection_id_subset` (and `null_metric_id_subset` when the source has it); only the measures
(`rmst_selected*`, `fpr_selected*`, `n_alt`, `n_eval`) are NA.

**Tableau_PCA_3** (smoke: 9 groups, 44 rows): group = (dataset_id, cohort_id, event_id); fixed order per group —
mean and real groups: `0` BASELINE_CPV90, `1` ORACLE_Q_AFFINE, `2` ORACLE_Q_MIX, `3` EXANTE_QBAR; covariance groups add
`D1` COV_JOINT_ORACLE/AFFINE, `D2` COV_JOINT_ORACLE/MIX_HEURISTIC, `D3` COV_MARGINAL_DIAGNOSTIC, `C`
ENERGY_INDEX_COMPARATOR, and `1`/`2` are explicit `UNSUPPORTED` RULE rows (H7). Row (2) of a mean group reuses the
exact T2 objects at k = nmax (`S`, `d_star`, `V_star`, `rmst*`, `fpr*`, `metric_id`) with a single FORMULA lineage row
per cell. Columns (58): `table, row_id, block_id, ordre, method, objective_kind, detector_family, dataset_id,
cohort_id, event_id, event_window_id, S, d_star:int, I_star:float, info_kind, I_cov_joint:float,
I_cov_marginal_sum:float, M_cost:float, C_affine:float, cost_kind, V_denominator, V_star:float, V_star_meaning,
rmst:float, rmst_lo:float, rmst_hi:float, n_alt:int, det_rate:float, censored_share:float, fpr:float, fpr_lo:float,
fpr_hi:float, n_eval:int, fpr_calibration:float, n_cal:int, predictive_bound:float, target_fpr:float, metric_id,
null_metric_id, null_calibration_id, calibration_hash, selection_id, basis_hash, split_hash, config_hash, seed:int,
oracle_input, claim_flag, selection_exact, tie_broken, comparability, cpv90_k_full:int, status, execution,
source_kind, claim_scope, na_reason, footnotes`. Cost columns keep distinct source meanings: `M_cost` is the fluid
mixture cost M(d, γ_M), `C_affine` the affine chord C(d) = a + c d, and `V_denominator` names the cost column that
divides I in the source `V_star` (`C_affine` for `AFFINE_SURROGATE` objectives, `M_cost` for the mixture/heuristic
ones, NA for the energy comparator); V is never recomputed. The covariance diagnostic row (D3) shows the marginal sum
`I_cov_marginal_sum` next to the joint KL `I_cov_joint` of the same S (never additive). Core display order in the
Markdown: rupture, pipeline & rule, I(S)/type, I_cov_joint/I_cov_marginal_sum (covariance), M(d)/C(d)/applicability/
denominator, V(S)/meaning, RMST250, d*, FPR250.

**T3R** (Markdown sub-table of `Tableau_PCA_3.md` only, 12 rows in the smoke): one row per (cohort, event, method),
columns (33): `table, row_id, block_id, cohort_id, event_id, event_window_id, method, claim_scope, status,
calib_first_day, calib_last_day, monitor_start, embargo_after_2019:int, pre_onset_policy, monitor_armed_from,
onset_date, event_end_date, time_origin, n_event_sessions:int, alarm_dates, pre_onset_alarms:int,
pre_onset_alarm_dates, detected_during_event, time_to_alarm_during_event:float, event_censored,
post_onset_delay_h250:float, post_onset_alarm_date, post_event_alarm, path_supports_H, selection_id, metric_id,
claim_flag, footnotes`. All R1–R5 cells are NA (not executed under `/2` before J4); the retrospective cohort's
`monitor_armed_from` is NA and rendered as not armed. The two cohorts stay distinct and blocked.

## 5. Lineage

`table_lineage.csv`, **exactly one row per displayed cell** (every CSV cell of T1/T2/T3 and every T3R cell).
`validate_lineage` enforces **exact equality** between the key set of all exported cells and the key set of the
lineage rows: missing key → `LINEAGE_INCOMPLETE`, duplicate key → `LINEAGE_DUPLICATE`, extra key (a filtered-out
row must emit no provenance) → `LINEAGE_ORPHAN`. Columns: `table, row_id, column, kind,
source_file, source_key, source_column, formula, inputs` (all `str`). `kind` ∈ {`SOURCE`, `FORMULA`, `MANIFEST`,
`RULE`}. A `SOURCE` row points to a run CSV (`spectra.csv`/`selection.csv`/`calibration.csv`/`aggregates.csv`) with
`source_key` = canonical JSON of the source row's primary key (`pdb.PRIMARY_KEYS`) and `source_column` = the source
column; every such pointer resolves to an existing source row and column. A `MANIFEST` row carries `source_key` =
canonical JSON `{"path": [...]}` of the **exact** manifest path (no ellipsis), which must resolve by walking
`manifest.json`. `FORMULA` carries the formula text and `inputs` (e.g. the T1/T2 row id for identity copies).
Markdown cells are formatted views of CSV cells; document-level header text comes from the manifest.

## 6. Manifest, completeness, consumer API

`table_manifest.json`: `tables_schema = "pca_drift_tables/1"`; `input` (relative path, `run_fingerprint`,
`schema_version`, `run_mode`, SHA-256 of the 7 source files); `code` (SHA-256 of `experiments/pca_drift_tables.py`
and of the runner `experiments/pca_drift_benchmark.py`); `environment` (interpreter/library versions and the
deterministic variables, no absolute path); `filters`, `format`, `strict`, `command` (the regeneration gabarit, built
from the canonical options with the literal `<OUT>` — never from `argv`); `columns` (CSV name → French Markdown
title per table); `outputs` (SHA-256, bytes, rows of every other written file); `tables_fingerprint` =
SHA-256 of the canonical JSON (`pdb.canon`, sorted keys, compact separators) of
`{tables_schema, input, code, environment, filters, format, strict}` where **`input` is the full input object** of
the manifest (path, `run_fingerprint`, `schema_version`, `run_mode` and the per-file `sha256` map) — the exact
recipe is recomputable from the manifest fields alone and is identical across two renders of the same options.

Completeness definition: an output directory is complete iff `table_manifest.json` exists and every file listed in
its `outputs` exists with its SHA-256.

```python
from experiments.pca_drift_tables import verify_output_dir
assert verify_output_dir("results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout")
```

## 7. CLI

```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
.venv/bin/python experiments/pca_drift_tables.py --input-dir <rel_input> --output-dir <OUT> \
  --format both [--dataset …] [--scenario …] [--detector-family …] [--strict]
```

`--input-dir` is required; `--output-dir` defaults to `results/pca_drift_benchmark/tables/<basename(input-dir)>/`.
`--dataset`/`--scenario`/`--detector-family` are validated against the runner enumerations and applied to **every**
output row, the T3R sub-table and the lineage (a family filter keeps only the rows whose `detector_family` matches;
the T3R section is omitted when no real row survives). Filtering happens **before** any lineage emission, so a
filtered-out row leaves no provenance row and the lineage key set stays exactly equal to the exported cell key set. Block headers render the actual `run_mode` and each
independent role count (`n_center`/`n_cal`/`n_null`/`n_alt`); the `SMOKE_NO_CLAIMS` banner and the
"planned full, not executed" note appear only when `run_mode = smoke`. Exit codes: 0 success; 2 refusal (environment
via `pdb.check_env`, usage, integrity, horizon, real contract, `--strict` identity, non-empty output); 3 incomplete
write. No timestamp, duration or absolute path is ever written; two invocations with the same inputs and options
produce byte-identical files (verified octet per octet, manifest included).
