# PCA drift benchmark (stream 28) — output schema `pca_drift_benchmark/2`

`experiments/pca_drift_benchmark.py` compares spectral PCA prefixes with information-selected axis subsets on mean
and covariance drifts. Plan: `prompts/plans/plan-28.md` (GO `prompts/GO-stream-28.md`); configuration
`configs/pca_drift_benchmark.yaml`; tests `tests/test_pca_drift_benchmark.py`. This document is the schema contract.
It is sealed for consumers (streams 29-31) only after the Codex audit of the code and of the smoke outputs, and after
the stream is integrated on `main`. Any change to a file, column, key, enumeration or identifier recipe requires a new
`schema_version`. Version `/2` replaces `/1` for every new artifact. Its threshold rule is the predictive exchangeable
rank of the researcher amendment (`prompts/GO-stream-28-amendment-P0-P1.md`, deviation `C-pca-predictive-rank`).

## 1. Files and writing rules

- One directory per run: `results/pca_drift_benchmark/smoke_predictive_v2/` or `results/pca_drift_benchmark/full/`,
  holding `manifest.json`, `spectra.csv`, `selection.csv`, `calibration.csv`, `trials.csv`, `aggregates.csv`,
  `issues.csv`. The pre-amendment smoke under `results/pca_drift_benchmark/smoke/` is a `/1` artifact. It is kept byte
  for byte and is never mixed with `/2` cells or read as evidence for the predictive rule.
- `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` is the candidate `/2` evidence produced after the
  closeout fixes. `smoke_predictive_v2/` predates them: its manifest keeps `config.schema_version` `/1` (mixed
  metadata, artifact preserved as is and never edited by hand).
- CSV files are written by `jepadrift.pipelines.save_fair_csv`: `%.17g` floats, `NaN` for NA, LF line ends, no index.
  Read them with `pandas.read_csv(path, float_precision="round_trip")`.
- `NaN` means NA, either not applicable or not computed. It is never an empirical zero. Booleans are written
  `True`/`False`. JSON values stored in CSV cells are compact and quoted: `S`, `rank_order`, `claim_flag`,
  `alarm_dates`, `pre_onset_alarm_dates`, `scope`, `detail`.
- `S` is a sorted JSON list of 1-based axis indices of the frozen basis, for example `[1,2,10]`; `d` = len(S).
  `parse_S` rejects anything else.
- Rows are deduplicated on the primary key, and a duplicate key with different content raises an error. Rows are
  sorted by the sort key; NA sorts before numbers, and numbers before strings. Closed enumerations (section 5) are
  validated before writing, and an unknown value raises an error.
- `manifest.json` is written last (`sort_keys`, `indent=2`). Its presence marks a completed run. It holds no timestamp,
  no duration and no absolute path. Timings, throughput, RSS and output hashes go to `<log-dir>/run.log`.
- Outputs are immutable. A directory that holds `manifest.json` is refused, even with `--resume`. A non-empty
  directory is refused without `--resume`.
- A `trials.csv` above 50 MB stays local and untracked (issue `TRIALS_LOCAL_ONLY`). Its SHA-256 is in the manifest. It
  is neither compressed nor force-added.

## 2. Identity, provenance, identifiers

- `identity` (manifest) holds the following fields. `run_fingerprint` = SHA-256 of the canonical JSON (sorted keys,
  compact) of `identity`.
  - `schema_version`.
  - `config_hash`: SHA-256 of the resolved configuration without `resources`.
  - `code_files`: relative path to SHA-256, for the runner and the imported `jepadrift` modules; `code_hash`.
  - `environment`: Python, NumPy, pandas, SciPy, PyYAML and statsmodels versions, BLAS, dtype, and the five required
    variables (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_CBWR`, `PYTHONHASHSEED`); `env_hash`.
  - `inputs`: relative path to SHA-256 of every input file read; `input_hash`.
  - `seed`.
- Inputs read: synthetic runs read `data/derived/d3_239/splits.yaml` only (cohort definitions, no return). Full real
  runs also read `ret_wide.npy`, `dates.npy`, `assets.json` and `data/derived/MANIFEST.json`.
- `provenance` (Git HEAD, branch, dirty flag, argv with `<OUT>`/`<LOG>` placeholders) lies outside the identity. After
  a commit, the CSV files, `identity` and every identifier stay byte-identical as long as the code, configuration,
  input and environment bytes are unchanged. Only `provenance`, and hence the manifest bytes, change.
- `sha16(x)` = first 16 hex digits of the SHA-256 of the canonical JSON of `x`. `role_key` is the SeedSequence prefix
  `[28, seed, crc32("path"), crc32(dataset_id), crc32(role)]`.
- Seed plan (`seed_plan`, checked before any draw and before any directory is created):
  - Keys: `[28, seed, crc32(domain), ...]` with domains `path` (`dataset_id`, role, replicate), `inject`
    (`dataset_id`, `B`) and `real_null` (cohort). There are no paths or file names in a key.
  - The CRC32 codes must be pairwise distinct on the run's finite label vocabulary (domains, backgrounds, roles, `B`,
    cohorts). A collision raises an error; no universal CRC32 guarantee is assumed, and no seed is changed to avoid
    one.
  - The canonical SeedSequence entropies of the planned keys must be unique. Each key is a list of uint32 words
    zero-padded to the pool size 4, since `SeedSequence([x])` equals `SeedSequence([x, 0])`. The seed must lie in
    [0, 2^32).
  - The manifest `rng.plan` records the number of keys, the vocabulary codes and the SHA-256 of the canonical
    entropies.

| identifier | recipe |
|---|---|
| `null_id` | `sha16{fp: run_fingerprint, dataset, cohort, null_kind, role_key, n, H}` |
| `null_calibration_id` | `sha16{null_id, family, params{p, s2, delta, alarm_rule}, centering_hash, basis_hash, S, alpha, rule: "predictive_exchangeable_rank_v2"}` |
| `metric_id` HOLDOUT_NULL_FPR | `sha16{kind, ncid: null_calibration_id, role_key(holdout_null), n: n_null}` |
| `metric_id` ALT_RMST | `sha16{kind, ncid, event_id, drift_hash, event_window_id, role_key(alternative), n: n_alt, H, time_origin}` |
| `metric_id` check rows | `sha16{kind, fp, dataset, event_id, drift_hash, n: n_alt, H}` |
| `metric_id` REAL_EVENT_PATH | `sha16{kind, ncid, cohort, event_window_id, method, k: reservoir_k, S, time_origin, policy: "R1-R5"}` |
| `selection_id` | `sha16{fp, dataset, cohort, event, method, objective, reservoir_k, S, basis_hash}` (no experiment label) |
| `issue_id` | `sha16{code, scope}`, with `scope` the canonical JSON text of the issue scope |

Full SHA-256 fingerprints:
- `basis_hash`: LW eigenvalues followed by the eigenvectors. Arrays are hashed as their shape followed by their
  float64 bytes (`array_sha256`).
- `centering_hash`: the centering matrix C0hat.
- `drift_hash`: Delta (mean scenarios) or M (rotation).
- `maxima_sha256`: the calibration maxima in replicate order.
- `calibration_hash`: the maxima bytes followed by `repr(threshold)`.
- `x_fit_sha256`: the fit rows.
- `split_hash`: for synthetic rows, T_fit, H, role counts and role keys; for real rows, the cohort definition (calib
  segment, monitor start, embargo, events, pre-onset policy).

Consequences:
- The E1 and E2 prefix rows share `selection_id`, `metric_id` and every value.
- The E3 rows of ORACLE_Q_MIX and COV_JOINT_ORACLE equal the E2 rows at k = nmax.
- In synthetic rows, one (family, S, calibration, scenario) has a single ALT_RMST `metric_id`, whichever methods
  select S.
- The two real cohorts share no identifier.

## 3. Common columns

Every table except `trials.csv` starts with: `schema_version, run_mode, run_fingerprint, source_kind, claim_scope,
dataset_id, cohort_id, split_hash, event_window_id, event_id, detector_family, k, S, d, objective_kind, selection_id,
metric_id, null_id, null_calibration_id, calibration_hash, config_hash, basis_hash, seed, status, execution`. A column
without meaning for a row is NA. Synthetic rows have `cohort_id` NA. `k` is the size of the candidate reservoir
P_k = axes 1..k. `execution` is EXECUTED when the row's metric or calibration was computed in this run.

## 4. Tables

**spectra.csv**
- Key: (dataset_id, basis_hash, k), with one row per k = 1..N for each frozen basis.
- `N, T_fit`; real rows only: `fit_first_day, fit_last_day`; `fit_rows, complete_rows, nan_cells`.
- Ledoit-Wolf covariance: `lw_shrinkage`, `trace_lw`, `lambda_lw` (k-th eigenvalue), `whitening_scale` =
  sqrt(lambda_lw), `cpv_lw` (cumulative share of the full trace).
- Sample correlation: `lambda_corr`, `mp_edge` = (1 + sqrt(N/T))^2, `mp_above` (lambda_corr > mp_edge, strict),
  `mp_count`, `kaiser_ge1` (lambda_corr >= 1), `kaiser_count`.
- CPV90: `cpv90_k_full` is the first k with cpv_lw >= 0.9 over the full spectrum. `cpv90_status` is CPV90_IN_TOP20 if
  cpv90_k_full <= nmax, CPV90_OUTSIDE_TOP20 otherwise.
- Synthetic rows only: `pop_var_axis` = v_k' Sigma0 v_k and `null_var_z` = pop_var_axis / lambda_lw (null variance of
  z_k).
- `x_fit_sha256`.

**selection.csv**
- Key: (selection_id, experiment, row_kind, d).
- `experiment`; `method`.
- `row_kind`: SELECTED is the method's choice for reservoir k. CANDIDATE is the best subset of each cardinality
  d = 1..k under the method's ranking: top-d of q for the ORACLE_Q methods, the exact joint-KL maximizer for
  COV_JOINT_ORACLE, top-d of the marginal KL for COV_MARGINAL_DIAGNOSTIC.
- `reservoir_k` (= k).
- `rank_order`: 1-based axes by q descending, ties to the smaller axis.
- `selection_exact` is True: the methods are exhaustive, or exact for an additive objective.
- `tie_broken` is True when a tie decided the choice: V ties go to the smallest d, equal q at the cut goes to the
  smaller axis.
- `oracle_input`.
- Information and costs:
  - `info_kind` labels `I_objective`, the quantity the method maximizes. For prefix rows it is the family's quantity
    (plug-in q sum for MEAN, joint covariance KL for COV), descriptive only.
  - `cost_kind`; `M_cost` = M(d, gamma_M); `C_affine` = a + c d.
  - `V_mix` = I_objective / M_cost and `V_affine` = I_objective / C_affine.
- Diagnostics:
  - MEAN: `I_plugin_lw` (sum of q = (beta/sqrt(lambda))^2/2 over S, beta = V'Delta) and `I_pop_joint`
    (0.5 mu_S' C0_S^-1 mu_S in z).
  - COV: `I_cov_joint` (joint Gaussian KL of C1_S against C0_S) and `I_cov_marginal_sum`. The marginal sum is never a
    joint KL.
  - `pop_offdiag_max`: largest absolute off-diagonal population correlation of z_S. NA for d = 1.
- `null_metric_id`: the HOLDOUT_NULL_FPR row of the same calibration.
- `claim_flag`: a JSON list.
- `cpv90_k_full, comparability`: BASELINE_CPV90 rows.
- `metric_id` points to aggregates: ALT_RMST for synthetic rows, REAL_EVENT_PATH for real rows.

**calibration.csv**
- Key: null_calibration_id. One row per (dataset, cohort, family, S, null sample).
- Stream and detector:
  - `null_kind, stream_kind`.
  - `p`: stream dimension, d for MEAN and d(d+1)/2 for COV.
  - `s2` with `s2_rule` = 2 ln(H/alpha)/(H p).
  - `cusum_delta` = 0.5 (ENERGY only); `alarm_rule`; `H`; `alpha`.
- Threshold (section 6):
  - `threshold_rule` = `predictive_exchangeable_rank_v2`.
  - `n_cal`, and `rank_r` = floor(alpha (n_cal + 1)) - 1 with exact decimal alpha. `rank_r` + 1 and `n_cal` + 1 are
    the exact numerator and denominator of the bound.
  - `threshold`.
  - `calibration_alarms`: number of calibration paths with maximum > b, which is <= rank_r. `calibration_fraction` =
    calibration_alarms / n_cal is the empirical calibration alarm frequency.
  - `predictive_bound` = (rank_r + 1)/(n_cal + 1) <= alpha, given only where the guarantee applies, otherwise NA.
  - `guarantee_basis`: EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA for independent synthetic null paths;
    NOT_ESTABLISHED_HISTORICAL_WINDOWS for the real D6 windows.
  - `maxima_sha256`.
  - These three quantities are distinct: the empirical calibration rate, the predictive bound, and the observed
    holdout FPR (`aggregates.fpr`). None replaces another.
- Failure: a CALIBRATION_FAILED row keeps `n_cal`, `maxima_sha256`, `threshold_rule` and `guarantee_basis`. It has
  `rank_r`, `threshold`, `calibration_alarms`, `calibration_fraction`, `predictive_bound` and `calibration_hash` NA,
  and an issue explains it.
- Covariance centering: `centering_hash`, `centering_days` = n_center H, and `centering_pop_bias_max` =
  max|C0hat_S - C0_S|. These are set for COV only.
- `anytime_valid` is always False. `null_validity`.
- Real D6 rows only: `window_starts_distinct` and `in_sample_share`, the share of admissible starts whose window
  overlaps the calib rows the basis was fitted on.

**trials.csv**
- Key: (group_id, role, replicate). The schema is normalized: exactly `group_id, role, replicate, first_hit,
  censored_time, detected, stat_max, pre_onset_alarm, detected_during_event`.
- Join rules:
  - role `calibration`: group_id = `calibration.null_calibration_id`.
  - roles `holdout_null` and `alternative`: group_id = `aggregates.metric_id`.
  - role `real_path` is reserved for executed real evaluations; no row exists before J4.
  - Every other attribute (dataset, family, S, scenario, threshold, identities) comes from these joins.
- `replicate`: path index within the role, from 0.
- `first_hit`: 1-based day of the first alarm, the alarm day included; -1 if no alarm within H.
- `censored_time` = first_hit if detected, else H; `detected` = first_hit > 0.
- `stat_max`: maximum of the detector statistic over the H days, for calibration and holdout_null. It is NA for
  alternatives, whose scans stop once every path of a batch has alarmed.
- `pre_onset_alarm`, `detected_during_event`: real paths only, NA in synthetic rows.

**aggregates.csv**
- Key: metric_id. `k` and `objective_kind` are NA, since a metric belongs to (S, family, calibration, scenario) and
  not to a method. Synthetic metrics are shared by every selection row that references them; real metric ids include
  the method and k.
- `metric_kind` HOLDOUT_NULL_FPR:
  - `n` = n_null, `alarms`, `fpr` = alarms/n with Wilson `fpr_lo, fpr_hi`.
  - `target_fpr` = alpha, `deff` = 1, `n_eff` = n, `ci_kind` WILSON.
  - `fpr` is the rate observed on independent holdout paths. It may differ from `predictive_bound` and is never
    replaced by alpha or by the bound. No 5 % claim follows from it.
- Calibration failure: the HOLDOUT_NULL_FPR and ALT_RMST rows of a CALIBRATION_FAILED calibration keep their
  identifiers, with status CALIBRATION_FAILED, `execution` NOT_EXECUTED and every metric NA. They have no trial rows.
  The selection rows that reference them carry the same status.
- `metric_kind` ALT_RMST:
  - `event_id`; `event_window_id` SYNTH_ONSET_ALIGNED; `time_origin` ONSET_ALIGNED. The drift is present from day 1
    and the delay is first_hit.
  - `n` = n_alt, `alarms`.
  - `rmst` = mean of censored_time; `rmst_sd` (ddof 1); `rmst_se` = rmst_sd / sqrt(n / deff), deff = 1 (independent
    paths), `n_eff` = n.
  - `rmst_lo, rmst_hi` = rmst -/+ 1.959963984540054 rmst_se, with `ci_kind` NORMAL_DEFF1 for the RMST.
  - `det_rate` with Wilson `det_lo, det_hi`; `censored_share` = 1 - det_rate.
  - `null_metric_id`.
- `metric_kind` GAUSS_FORMULA_CHECK (Gaussian background) or GAUSS_PROXY_CHECK_T7 (t7 background). There is one row
  per (dataset, scenario):
  - `check_estimate` = mean Gaussian log-likelihood ratio over the n_alt H alternative days, in the space
    `check_space` = WHITENED_Z<nmax>.
  - `check_se` = sd / sqrt(n_alt H); `n` = n_alt H.
  - `check_reference`: Gaussian KL in the same space, I_pop_joint(P_nmax) or I_cov_joint(P_nmax).
  - Descriptive only. In t7 the reference matches two moments and is not a t7 KL.
- `metric_kind` REAL_EVENT_PATH: one row per (cohort, event, method, reservoir k).
  - Every run writes these rows, with `execution` NOT_EXECUTED and status NOT_EVALUABLE_STANDARD_SPLIT,
    BLOCKED_PRE_J4 or DATA_UNAVAILABLE. Every metric is NA.
  - `onset_date, event_end_date` and `time_origin` come from the configuration.
  - `monitor_armed_from` is the splits `monitor.first_day` for the standard cohort. For the retrospective cohort it is
    NA until a calendar-reading evaluation is executed.
  - The R1-R5 fields (section 7) are filled only by an executed evaluation: `n_event_sessions, alarm_dates,
    pre_onset_alarms, pre_onset_alarm_dates, detected_during_event, time_to_alarm_during_event, event_censored,
    post_onset_delay_h250, post_onset_alarm_date, post_event_alarm, path_supports_H`.

**issues.csv**
- Key: issue_id. Columns: `severity, code, scope, message, deviation_ref` (a `C-<topic>` entry of docs/DEVIATIONS.md,
  or NA) and `detail` (canonical JSON, or NA).
- `status` = code when the code is a status value. The other common columns carry the run values (schema, mode,
  fingerprint, config hash, seed) or NA.

**manifest.json**
- `schema_version, run_mode, dataset, run_fingerprint, identity, provenance`.
- `config`: resolved, with `full_counts` in smoke mode. `differences_from_full` (smoke: the four counts only);
  `claims`.
- `synthetic`:
  - The model: Sigma0 = (1 - rho) I + rho 11'. The t mixing uses one chi2_7 per day shared by the factor and
    idiosyncratic parts, rescaled to unit variance.
  - Per background: basis summary, centering, energy standardization, and covariance search counts (2^nmax - 1
    subsets, clipped negative KL, exactness).
  - Per scenario: Delta (N floats) and its hash, the non-zero beta, information values, c, and the M hash.
- `real`: cohorts with definitions and split hashes, plus the pre-onset policy. In full real runs it adds: file
  hashes, `rows_indexed` [a, b), first and last days, calib rows, basis, `stress_library` (windows, qbar, weights), the
  D6 null summary and the panel limits.
- `calibration`: the threshold rule, rank, threshold, guarantee statement and its hypotheses, `guarantee_basis` per
  null kind, the real-path and holdout readings, `min_n_cal`, and the rank and bound of the configured `n_cal` and real
  `n_null`.
- `detectors`, `costs` (M(d) for d = 1..nmax, affine a and c), `pre_j4` (`frozen_json_present`, status, rule), `rng`,
  `outputs` (SHA-256, bytes and rows of each CSV).

## 5. Closed enumerations

| column | values |
|---|---|
| status | OK, BLOCKED_PRE_J4, NOT_EVALUABLE_STANDARD_SPLIT, DATA_UNAVAILABLE, UNSUPPORTED, BLOCKED_RESOURCE, CPV90_OUTSIDE_TOP20, CALIBRATION_FAILED, PATH_TOO_SHORT |
| execution | EXECUTED, NOT_EXECUTED |
| source_kind | SYNTHETIC_GAUSSIAN, SYNTHETIC_T7, REAL_RETROSPECTIVE |
| claim_scope | SYNTHETIC_MC, REAL_STANDARD_SPLIT, REAL_RETROSPECTIVE_EXPLORATORY |
| dataset_id | SYNTH_GAUSS_EQUICORR, SYNTH_T7_EQUICORR, D3_239 |
| cohort_id | NA (synthetic), cohort_standard_embargo, cohort_retrospective_covid |
| event_id | A_market_mean, B_cov_rotate15, B_cov_rotate30, B_cov_rotate45, C_residual_mean, COVID_2020, STYLE_2022H1 (15 and 45 degrees are reserved for the deferred sweep) |
| event_window_id | SYNTH_ONSET_ALIGNED, E_COVID_2020_ACUTE, E_STYLE_2022H1 |
| detector_family | MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM, COV_QUADRATIC_VECH_SCAN, ENERGY_INCREASE_CUSUM |
| method | BASELINE_PREFIX, BASELINE_CPV90, ORACLE_Q_MIX, ORACLE_Q_AFFINE, EXANTE_QBAR, COV_JOINT_ORACLE, COV_MARGINAL_DIAGNOSTIC, ENERGY_INDEX_COMPARATOR |
| objective_kind | NONE, CPV90_RULE, MEAN_MIX_FLUID_SURROGATE, MEAN_AFFINE_SURROGATE, EXANTE_QBAR_MIX_FLUID_SURROGATE, COV_JOINT_AFFINE_SURROGATE, COV_JOINT_MIX_HEURISTIC, COV_MARGINAL_MIX_DIAGNOSTIC |
| info_kind | MEAN_GAUSS_PLUGIN_LW, MEAN_GAUSS_PLUGIN_LW_T7_PROXY, MEAN_GAUSS_POP_JOINT_EXACT, MEAN_GAUSS_POP_JOINT_T7_PROXY, COV_GAUSS_POP_JOINT_EXACT, COV_GAUSS_POP_JOINT_T7_PROXY, COV_GAUSS_MARGINAL, COV_GAUSS_MARGINAL_T7_PROXY, EXANTE_QBAR_PLUGIN_LW, REAL_EXPOST_PLUGIN_LW |
| cost_kind | MIX_FLUID_SURROGATE, AFFINE_SURROGATE, HEURISTIC_COST, NONE |
| metric_kind | HOLDOUT_NULL_FPR, ALT_RMST, REAL_EVENT_PATH, GAUSS_FORMULA_CHECK, GAUSS_PROXY_CHECK_T7 |
| role (trials) | calibration, holdout_null, alternative, real_path |
| time_origin | ONSET_ALIGNED, CONTINUOUS_RESTART_AFTER_ALARM |
| claim_flag (JSON list) | NONE, ORACLE_INJECTED_DELTA, ORACLE_TRUE_SIGMA1, EX_POST_ORACLE, COV_SURROGATE_EXPLORATORY, HEURISTIC_COST, RETROSPECTIVE_DIAGNOSTIC |
| oracle_input | INJECTED_DELTA, TRUE_SIGMA1, EXPOST_EVENT_DELTA, STRESS_LIBRARY_2008_2011, NONE |
| null_kind | SYNTH_INDEPENDENT_PATHS, REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS |
| null_validity | EMPIRICAL_QUASI_LIKELIHOOD, EMPIRICAL_ENERGY, APPROXIMATE_D6_INSAMPLE_OVERLAPPING |
| stream_kind | WHITENED_PCA_SCORES, VECH_QUADRATIC_CENTERED, EW_INDEX_ENERGY |
| alarm_rule | GE, GT |
| ci_kind | NORMAL_DEFF1, WILSON, NONE |
| severity | BLOCKER, WARNING, INFO |
| comparability | COMMON_20_AXIS_UNIVERSE, NOT_COMPARABLE_OUTSIDE_TOP20 |
| experiment | E1, E2, E3 |
| row_kind | SELECTED, CANDIDATE |
| cpv90_status | CPV90_IN_TOP20, CPV90_OUTSIDE_TOP20 |
| code (issues) | every status value, QUASI_LIKELIHOOD, SMOKE_NO_CLAIMS, REAL_NOT_RUN, RETROSPECTIVE_DEVIATION, C_UNSUPPORTED, TRIALS_LOCAL_ONLY |
| check_space | WHITENED_Z1 ... WHITENED_Z20 |
| threshold_rule | predictive_exchangeable_rank_v2 |
| guarantee_basis | EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA, NOT_ESTABLISHED_HISTORICAL_WINDOWS |

## 6. Detectors, thresholds, experiments

**Representation.**
- z_t = W_S' x_t, with W = V Lambda^{-1/2}. The Ledoit-Wolf basis is frozen on an independent fit sample: role
  `fit`, or the calib rows for D3.
- Real rows are centred by the calib mean. Population matrices live in the same z space: C0 = W'Sigma0 W,
  C1 = W'Sigma1 W, mu = W'Delta.

**Detectors.**
- MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM: W_t = max over every 1 <= tau <= t of
  -(p/2) log1p(n s2) + s2 |S_t - S_{tau-1}|^2 / (2 (1 + n s2)), with n = t - tau + 1. Alarm when W_t >= h.
  - There is no window, no GLR and no O(1) recursion.
  - s2 = 2 ln(H/alpha)/(H p) is fixed ex ante, identical for every method and cohort.
  - The whitening is estimated, so the scan is a quasi-likelihood: thresholds are empirical only, and there is no
    log-gamma threshold.
- COV_QUADRATIC_VECH_SCAN: the same scan on y_t = vech_std(z_t z_t' - C0hat_S), with p = d(d+1)/2. vech_std is the
  diagonal divided by sqrt(2), then the upper off-diagonal terms row-major.
  - The stream is not presumed Gaussian isotropic: the scan on it is a calibrated quasi-likelihood, and every tau is
    kept.
  - `vech_stream` checks that the centering is (d, d) and that the stream has d(d+1)/2 coordinates. The scan infers p
    from the stream's last axis, and the runner refuses a stream whose dimension differs from the p used in s2.
  - C0hat is the mean of z z' over the independent `centering` role. It is frozen before any calibration path and is
    the same for calibration, holdout and alternatives.
- ENERGY_INCREASE_CUSUM: Page CUSUM S_t = max(0, S_{t-1} + e_t - 0.5), with alarm when S_t > h. e_t =
  (m_t^2 - mu)/sd, where m_t is the equal-weight index of the returns and mu, sd are the moments of m^2 on the fit
  rows.

**Threshold `predictive_exchangeable_rank_v2`.**
- The rule applies to n finite calibration maxima, with alpha in (0, 1).
- r = floor(alpha (n + 1)) - 1, with exact decimal alpha. If r < 0, the calibration fails with InsufficientCalibration
  and status CALIBRATION_FAILED: no threshold and no guarantee. This happens below min_n_cal = ceil(1/alpha) - 1, which
  is 19 at alpha = 0.05.
- Otherwise b = sorted(maxima)[n - r - 1]. The GT threshold is b; the GE threshold is nextafter(b, +inf), a single step
  with no ULP loop. A non-finite threshold is CALIBRATION_FAILED. At most r calibration paths alarm.
- Guarantee: if the n calibration maxima and the maximum of a new null path are exchangeable, then
  P(new maximum > b) <= (r + 1)/(n + 1) <= alpha, and ties are conservative. The bound is 2/41 at n = 40 (r = 1) and
  100/2001 at n = 2,000 (r = 99).
- Scope of the guarantee:
  - It is marginal over the calibration sample and the new path.
  - It holds conditionally on the fit and nuisance (centering) choices frozen on independent roles.
  - It is not conditional on a realized threshold, and it is not an e-process property: `anytime_valid` stays False,
    and the scans remain quasi-likelihoods.
- It applies to independent synthetic null paths. It is not established for the overlapping historical D6 windows
  (`guarantee_basis` NOT_ESTABLISHED_HISTORICAL_WINDOWS, `predictive_bound` NA), nor for a real event path.
- The holdout FPR is an independent observation, reported as measured. It is never tuned toward 5 %.

**Selection methods.**

| method | experiments | rule |
|---|---|---|
| BASELINE_PREFIX | E1, E2 (same rows) | S = P_k, k = 1..nmax |
| ENERGY_INDEX_COMPARATOR | E1, E3 | equal-weight index energy, B scenarios; k, S, d NA |
| ORACLE_Q_MIX | E2 (every k), E3 (= E2 at k = nmax) | top-d of q in P_k, d* = argmax I/M(d) |
| COV_JOINT_ORACLE | E2 (every k), E3 (= E2 at k = nmax) | exact search over the 2^nmax - 1 subsets (batched, see below); d* by V_affine (COV_JOINT_AFFINE_SURROGATE) and by V_mix (COV_JOINT_MIX_HEURISTIC, HEURISTIC_COST) |
| BASELINE_CPV90 | E3 | P_{cpv90_k_full} if it lies within nmax, otherwise CPV90_OUTSIDE_TOP20 without S or metric |
| ORACLE_Q_AFFINE | E3 | top-d of q in P_nmax, d* = argmax I/(a + c d) |
| COV_MARGINAL_DIAGNOSTIC | E3 | top-d of the marginal KL 0.5 (r - 1 - ln r), d* by the sum over M(d) |
| EXANTE_QBAR | E3 | real: top-d of qbar (2008/2011 stress windows, equal weights) in P_nmax; synthetic: UNSUPPORTED |

**Exhaustive covariance search.**
- Each subset of the axes 1..nmax (nmax <= 20) is evaluated once. Its joint KL serves every reservoir k containing it.
- Evaluation runs in (batch, d, d) extractions with batched `solve`/`slogdet`. A batch holds at most
  min(`cov_search_chunk`, floor(available memory / (6 x 8 d^2 bytes))) subsets — an integer even when the available
  memory budget is a float; a non-finite budget raises ValueError — and `cov_search_chunk` is at most 20,000.
  Results do not depend on the batch size.
- The wall-clock and memory budgets are checked before every batch, also within one d. An overrun is BLOCKED_RESOURCE,
  never an approximate search.

**Costs.**
- M(d, gamma_M) = x/ln(gamma_M), where x is the root of x = ln(gamma_M) + (d/2) log1p(2x/d). It is a fluid surrogate,
  never an exact delay, RMST or ARL0.
- The root is found by brentq on [ln(gamma_M), hi], with hi doubled from 2 ln(gamma_M), at most 200 times.
  - The parameters (integer 1 <= d < 2^53, finite gamma_M > 1), the bounds and every evaluation are checked finite.
  - If no finite bracket is found, the computation fails explicitly.
- The affine cost is the chord of M between d = 1 and d = 20, independent of nmax.

## 7. Real cohorts, pre-J4 guard, rules R1-R5

**Pre-J4 guard.**
- No real return dated after 2019-12-31 is read before J4: `configs/FROZEN.json` is absent and owned by stream 21.
- `read_pre2020_panel` hashes the inputs against `data/derived/MANIFEST.json` and opens `ret_wide.npy` read-only as a
  memmap.
- It materializes only the pre-monitor rows [a, b): 2005-01-04..2019-12-31, minus the declared excluded day
  2005-01-03. Any non-finite cell raises DATA_UNAVAILABLE.

**Real pre-2020 computations (full mode).**
- LW basis on the 941 calib rows.
- Stress library qbar.
- Per cohort, a D6 sign-flip null: H-day windows of pre-monitor z, one Rademacher sign per day, cohort-salted seeds.
  - The windows overlap and partly cover the fit rows; the D6 transform erases drift and leverage.
  - No holdout FPR is claimed.

**Cohorts.**

| cohort | event | status before J4 | time origin |
|---|---|---|---|
| cohort_standard_embargo (claim REAL_STANDARD_SPLIT, armed at monitor.first_day after the 65-session embargo) | COVID_2020 (2020-02-24..2020-03-23) | NOT_EVALUABLE_STANDARD_SPLIT, inside the embargo | NA |
| cohort_standard_embargo | STYLE_2022H1 (2022-01-01..2022-06-30) | BLOCKED_PRE_J4, flag RETROSPECTIVE_DIAGNOSTIC | ONSET_ALIGNED |
| cohort_retrospective_covid (claim REAL_RETROSPECTIVE_EXPLORATORY, frozen at 2019-12-31, armed on the first session >= 2020-01-01, no embargo; C-pca-covid-retrospective) | COVID_2020 | BLOCKED_PRE_J4 | CONTINUOUS_RESTART_AFTER_ALARM |

**Rules R1-R5 (`evaluate_real_path`).**
- R1: monitoring is continuous. Every alarm is recorded, and the scan restarts (S = 0) on the next day.
- R2: alarms before the onset are kept (`pre_onset_alarms`, `pre_onset_alarm_dates`) and never count as detections.
- R3: detection is the first alarm in [onset, end], with `time_to_alarm_during_event` = index - onset + 1. Otherwise
  `event_censored` is set and the time equals `n_event_sessions`.
- R4: a separate H-day reading gives `post_onset_delay_h250` = first alarm in [onset, onset + H - 1] - onset + 1. It
  is H without an alarm, and NA (PATH_TOO_SHORT) when the path ends before H days without an alarm.
  `post_event_alarm` marks a first post-onset alarm after the event end.
- R5: a single path, so no interval and no FPR.
- Before J4 `evaluate_real_path` runs only on fake dated test panels (`FAKE_DATED_TEST`). A REAL_RETROSPECTIVE path
  dated after 2019-12-31 raises PreJ4Refused.

## 8. Execution, resources, resume

`python experiments/pca_drift_benchmark.py --mode smoke|full [--dataset synthetic|real|both] [--out DIR] [--log-dir DIR]
[--seed n] [--resume] [--config PATH]`.

- **Modes.** Smoke mode is synthetic only and changes only n_center, n_cal, n_null and n_alt (40 each). Smoke
  combined with `real` or `both` is a usage error (exit 2).
- **Default directories.** `results/pca_drift_benchmark/smoke_predictive_v2/` with
  `logs/pca_drift_benchmark/smoke_predictive_v2/` in smoke mode, and `.../full/` in full mode.
- **Environment.** It is checked at interpreter start. `PYTHONHASHSEED` must be 42. The three thread variables must
  be 1 and `MKL_CBWR` must be COMPATIBLE; when absent, they are set to these values before NumPy loads. Any other
  value makes the run exit 2 before creating a directory.
- **Partitions.** Stored in `<log-dir>/partitions/<sha16(key)>.npz`, with a JSON sidecar {fingerprint, key}. A
  partition is reused only if both match; otherwise PartitionMismatch is raised (exit 2).
- **Resource limits.**
  - The theoretical peak memory is checked before any computation; above `mem_limit_gib` the run is BLOCKED_RESOURCE.
  - The wall-clock limit (`max_wall_minutes`) applies per invocation. It is checked, together with the peak RSS
    against `mem_limit_gib`, before each new partition and before every batch of the exhaustive covariance search.
  - On BLOCKED_RESOURCE the run writes `<log-dir>/blocked_resource.json`, writes no manifest and exits 3.
- **Resume.** `--resume` continues with the same directories and gives outputs byte-identical to an uninterrupted
  run. No statistic or target changes under a resource limit.
- **Exit codes.** 0 success; 2 refusal (environment, usage, existing outputs, partition mismatch, pre-J4); 3
  BLOCKED_RESOURCE.
