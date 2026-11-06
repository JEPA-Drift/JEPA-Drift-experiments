# PCA drift benchmark — contract validation (stream 31, lot 2 QA)

**Current status (2026-11-06, measured 15:43–15:53 UTC): D7b fixed, not committed.** The separate GO `prompts/GO-stream-31-fix.md` (15:32 UTC) and plan `prompts/plans/plan-31-fix.md` authorised the fix. The hard-coded footnote count is now the run's null holdout count from the manifest. The current measurement is 44 passed, 0 failed, 0 skipped, with G1 executed, and `make check` exits 0. The current tracer SHA-256 is `a38fc46b1b45ed3e6e257a53c4ce29f9152b8e956b68d9d55771c58ff48634f2`. Details are in §10.

**Historical record.** The status paragraph below and §1–9 record the lot 2 measurement of 13:35 UTC (43 passed, 1 failed on D7b, STOP). They are kept unchanged, with their logs and hashes. In them, `c40a5e77…` is the historical tracer hash, not the current one.

**Status: STOP.** The single final measurement ended on a confirmed producer defect: D7b, the hard-coded sample size printed in the full 2000 figures. Nothing is committed. Arbitration belongs to the researcher and Codex.

This report covers lot 2 only, under:
- the canonical plan `prompts/plans/plan-31.md` (§4–5, amended by §9 and §10);
- `prompts/GO-stream-31.md` (GO of 12:22 UTC and the resume of 13:25 UTC).

Base commit: `20ad9e860a58373ec85405de6ee19a68322dd02e`.

## 1. Commands and environment

Every command ran from the worktree root with this prefix:

```bash
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
       MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
```

Toolchain: `.venv/bin/python` (3.12.9) and pytest 9.1.1. No dependency was changed.

**Final measurement.** It is the only full run of the file, with D7b defined last:

```bash
PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv \
  .venv/bin/python -m pytest -q -rA -x --durations=0 tests/test_pca_drift_contracts.py \
  > logs/pca_drift_contracts/qa.log 2>&1
```

`--durations=0` is a reporting flag only. The exit code was 1. The log `logs/pca_drift_contracts/qa.log` (ignored) has SHA-256 `08fae1045616143925b4faf858ada49df2cf0bd92cbd2499674fd3c1b7d07328`.

`.venv/bin/pyflakes tests/test_pca_drift_contracts.py` printed nothing and exited 0 before the final run.

**Development runs.** Each group was run once with `-k` before the final measurement, which is the only full run. The logs sit under `logs/pca_drift_contracts/`, with the run ledger in `ledger.md`.

| Run | Log | Result |
|---|---|---|
| F + E | `q1_FE.log` | 5 passed |
| A | `q2q3_A.log` | 15 passed, 1 failed (A7) |
| A7 after correction 1 | `q2_A7_fix.log` | 1 passed |
| Targeted E control after the §10 corrections | `q_resume_E_control.log` | 3 passed |
| B | `q4_B.log` | 5 passed |
| C | `q5_C.log` | 11 passed |
| D1–D4, D7a | `q6_D.log` | 5 passed |
| G1 | `q7_G1.log` | 1 passed |
| Producer overlap tests | `overlap_producer_tests.log` | 8 passed |

D7b was not executed before the final measurement.

## 2. Final measurement

Pytest reported 43 passed and 1 failed in 28.58 s (29.04 s wall-clock). `-x` stopped after D7b, which is the last test.

| Group | PASS | FAIL | BLOCKED | Duration (s) |
|---|---:|---:|---:|---:|
| F historical invariants | 2 | 0 | 0 | 0.01 |
| E parser and numerics | 3 | 0 | 0 | 0.57 |
| A mathematics (A1–A16) | 16 | 0 | 0 | 13.96 |
| B exact reuse (B1–B5) | 5 | 0 | 0 | 3.05 |
| C time, leakage, sampling (C1–C11) | 11 | 0 | 0 | 3.64 |
| D provenance and figures (D1–D4, D7a, D7b) | 5 | **1 (D7b)** | 0 | 4.59 |
| G full 2000 integration (G1) | 1 | 0 | 0 | 1.02 |

How to read the durations:
- They sum the per-test call, setup and teardown durations printed by pytest; entries under 0.005 s are hidden by pytest.
- Module fixtures are charged to the first test that uses them. Most of group A comes from the two figure contexts built for A6, which group D reuses.

G1 ran for real with the variable set. No test is BLOCKED, and the file contains no xfail.

## 3. Verified hashes and data metadata

**Sealed artifacts and invariants**

| Object | SHA-256 | Check |
|---|---|---|
| `results/e2/e2_cells.csv` (J1) | `e315e537…0823` | disk = index (`git show :`); 47 CRLF, no bare LF; `-text` attribute (F1) |
| `results/e3/e3_overshoot.csv` | `1ca7c3ae…68b3` | primary `iid/first_order_d1_l3` gate FAIL, rel_gap +5.2833 % (F2) |
| `docs/DEVIATIONS.md` `C-e3-d8-fail` | — | "+0.0528334213 > 0.05" and "It is a FAIL by excess" present (F2) |
| FULL `manifest.json` | `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47` | D2 |
| SMOKE `manifest.json` | `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9` | fingerprint and identity recomputed (D2) |

**Full 2000 trials (G1).** File `../JEPA-full-2000/…/trials.csv`, SHA-256 `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`:
- size 48 317 020 B, 716 000 rows;
- read directly as a regular file, with no copy and no link.

**Producer code.** Unchanged and equal to the recorded hashes:
- runner `8324b47b…`;
- tables `13d386fe…`;
- figures `c40a5e77…`.

**Run outputs.** Every present output of SMOKE and FULL matches `manifest.outputs`. FULL has no local `trials.csv`, so `pdt.load_run(FULL)` is never called.

**Real-data metadata (C6).** Only dates and metadata were read; no return was read.
- `data/derived/d3_239/splits.yaml` and `dates.npy` match `data/derived/MANIFEST.json`.
- calib window 2016-04-07 to 2019-12-31, i.e. 941 sessions;
- embargo of 65 sessions;
- `monitor.first_day` = 2020-04-06;
- first session on or after 2020-01-01 = 2020-01-02.

**Cohorts (C6).**
- Standard cohort: COVID is `NOT_EVALUABLE_STANDARD_SPLIT`, embargo 65.
- Retrospective cohort: armed 2020-01-02, `REAL_RETROSPECTIVE_EXPLORATORY`, embargo 0.

**Post-run state.**
- `git diff --quiet HEAD` holds on `results`, `figures`, `experiments`, `jepadrift`, `configs`, `tools`, `prompts/streams`, `docs/DEVIATIONS.md`, `CLAUDE.md` and `Makefile`.
- `PLAN.md` = `ed14c47a…`, unchanged.

## 4. Contract → test → witness matrix

Every witness lives in memory or under `tmp_path`. No producer and no sealed file was altered to obtain a RED.

| ID | Test | Contract (prompt 31) | Negative witness / reference | Producer overlap |
|---|---|---|---|---|
| F1 | `test_e2_cells_crlf_disk_and_index_unchanged` | J1 bytes on disk and in the index | LF-normalized bytes change the SHA | — |
| F2 | `test_d8_fail_preserved_verbatim` | D8 FAIL +5.2833 % kept | text mutated to PASS is rejected | — |
| E1 | `test_axis_list_round_trip_and_d` | `S_json([i-1 for i in parse_S])` round trip, `d == len(S)` | off-by-one serialization shifts the axes | rejections in `TestG1Input` |
| E2 | `test_information_finite_nonnegative_positive_eigenvalues` | λ_LW > 0, whitening = sqrt(λ); required I fields present, finite, ≥ 0 on OK rows (§10) | required `I_plugin_lw` set to NaN is flagged | — |
| E3 | `test_clip_tolerance_and_documented_rejections` | sign-of-slogdet rejection; `clip_kl` tolerance −1e-12·max(1,\|I\|), not machine epsilon; finite KL ≥ 0 on SPD inputs | −2e-12 raises; diag(1,−1) raises; diag(−1,−1) is refused downstream by `clip_kl` | — |
| A1 | `test_mean_kl_eigenbasis_identity_and_order_counterexamples` | 0.5‖L⁻¹Δ‖² = Σ q_k in the eigenbasis of the same Σ; eigenvalue order ≠ information order | λ + 0.5 gives a relative gap > 1e-3; Δ on v_N selects {N} | `test_g1_mean_kl_identity…` |
| A2 | `test_nested_plugin_information_monotone` | nested information monotone (plug-in and joint DPI) | non-nested sequence violates monotonicity | `test_g1_pop_joint_dpi…` |
| A3 | `test_top_q_exhaustive_forward_exact_with_ties` | top-q = exhaustive = forward add, exactly (dyadic q, ties, 4 cost tables); `tie_broken` ⇔ ≥ 2 optimal subsets | ties found by enumeration | `test_g2_top_q_*` |
| A4 | `test_early_stop_greedy_not_equivalent` | no early-stop equivalence | early stop gives d = 1, exact search gives d = 3 | — |
| A5 | `test_rotation_joint_vs_marginal_spd_symmetry_energy` | joint 0.5625 ≠ marginal sum 0.33936; Σ1 SPD; off-diagonal 1.5; energy 4 → 2.5 with KL > 0 | at 0°, joint = sum = 0; measured asymmetry 0.0 | `test_g1_joint_cov_kl…`, `test_g1_index_energy…` |
| A6 | `test_t7_information_labels_are_gaussian_proxies` | t7 labels are `*_T7_PROXY` / `GAUSS_PROXY_CHECK_T7` / `*_PROXY`; effective tags `GAUSSIAN_PROXY` | `EXACT_T_KL` gives `ENUM_VIOLATION`; `COV_GAUSS_POP_JOINT_EXACT` on a t7 row is rejected by the QA verifier | `test_g3_t7_information…` |
| A7 | `test_mixture_cost_unique_positive_root` | unique positive root; M > 1; M(4) = 1.5696, M(500) = 9.6427 | contracting fixed-point reference | `test_g1_mixture_cost…` |
| A8 | `test_mixture_cost_labelled_surrogate` | no `EXACT_ADD`/`ARL0`/`COV_EXACT_COST`; MEAN uses `MIX_FLUID_SURROGATE`, COV uses `HEURISTIC_COST` | `EXACT_ADD` gives `ENUM_VIOLATION` | — |
| A9 | `test_v_surrogate_fixed_before_trials` | V = I/M and V_affine = I/C exactly; M = manifest cost | poisoned roles leave `selection.csv` byte-identical while the aggregates differ | — |
| A10 | `test_projection_equals_stored_transform` | V orthonormal; W = V/sqrt(λ); `project` = `draw_path @ W` | another role's basis has another `basis_hash` | — |
| A11 | `test_mp_kaiser_cpv_on_sealed_spectra_and_tables` | MP edge on correlation; Kaiser on λ_corr ≥ 1; CPV monotone, CPV_N = 1, CPV_20 < 0.9; population CPV14 = 104/239 | criteria mutated to "CPV 90 %" at k = 14 is rejected | `TestG2Table1::test_criteria_markers` |
| A12 | `test_scan_reference_on_required_path_classes` | logL(τ,t), W_t and first alarms against a direct fsum reference (d = 1, 2, 4; H = 12) | the GT rule moves the alarm from 1 to 11 on equal maxima | `test_g1_scan_matches_slow_reference` |
| A13 | `test_scan_full_history_instrumentation` | widths t = 1..250; > 250 starts under `CONTINUOUS_RESTART_AFTER_ALARM` | a 50-day window gives a different W | — |
| A14 | `test_scan_prefix_terms_and_ex_ante_s2` | S_0 = 0, a, b; s2 = 2 ln(H/α)/(Hp) ex ante; one calibration per (dataset, family, S) | matched s2 differs; `GLR_WINDOWED` gives `ENUM_VIOLATION` | — |
| A15 | `test_calibration_rank_recipe_and_data_flow` | rank recipe, maxima hash, `calibration_hash`, bound, holdout FPR recomputed from the SMOKE trials | holdout maxima give another threshold | `test_p0_*` |
| A16 | `test_no_exact_eprocess_claim_and_mandatory_holdout` | `anytime_valid` False everywhere; empirical null validity; holdout FPR finite | `anytime_valid` = True is rejected | — |
| B1 | `test_t1_t2_prefix_identity_measured_and_blocked` | T2 prefix = T1 = `aggregates.csv` cell, as text; measured and blocked-NA counts kept separate | — | `TestG3Table2::test_prefix_cells_are_t1_objects` |
| B2 | `test_identity_comparator_is_strict_text` | strict text comparator | a `nextafter` %.17g value and a `.4g` string are both detected | — |
| B3 | `test_e2_k20_e3_oracle_mix_identity_selected_rows` | E2 k = 20 = E3 `ORACLE_Q_MIX` (SELECTED rows); T2 = T3 order "2"; additive plug-in domain | — | `TestG4Table3::test_t3_oracle_mix_equals_t2_k20` |
| B4 | `test_reuse_negative_witnesses` | mutated reuse is refused | unsorted, base 0 and axis 21 → `INVALID_S`; shifted → `L17_E3_COPY`; family changed on E3 copy → `UNEXPECTED_ROW_STATE` (§10); family changed on E2 prefix copy → `L16_PREFIX_IDENTITY`; foreign null → `FOREIGN_NULL` | partly `TestG1Input::test_foreign_null_refused` |
| B5 | `test_cov_and_exante_outside_additive_equalities` | `ORACLE_Q_*` UNSUPPORTED or absent for covariance; synthetic `EXANTE_QBAR` UNSUPPORTED | `ORACLE_Q_MIX` on a covariance row → `UNEXPECTED_ROW_STATE` | `TestG4Table3::test_cov_row_relabeled_oracle_q_refused` |
| C1 | `test_seed_plan_matches_manifests_and_role_groups_disjoint` | `seed_plan` SHA = manifest `rng.plan`; role groups disjoint | seed 43 gives another SHA | `test_p1_seed_plan…` |
| C2 | `test_thresholds_never_consume_holdout_or_alternative` | ×10 poisoned holdout/alternative leave calibration and spectra byte-identical | aggregates and holdout trials differ | `test_g3_poisoned_test_roles…` |
| C3 | `test_alternatives_paired_across_subsets` | one alternative array per scenario, shared across families and S; replicates 0..n−1 | — | `test_g3_roles_never_share_paths…` |
| C4 | `test_horizon_rmst_censoring_on_sealed_trials` | H = 250; censored time; RMST = mean exactly; det + censored = 1; FPR = alarms/n (SMOKE: 146 ALT, 106 holdout) | a mutated censored time is detected | `test_g3_aggregates_follow_from_trials` |
| C5 | `test_continuous_statistic_not_reset_at_onset` | pre-onset drift: continuous delay 28 < restart-at-onset delay 38; pre-onset alarm counted once; post-event alarm is not an event detection | — | `test_g3_retrospective_rules_r1_to_r5` |
| C6 | `test_real_split_metadata_and_cohort_disjointness` | split metadata (§3); no ID shared between cohorts | — | `test_g3_cohort_definitions…` |
| C7 | `test_fake_confirmatory_status_rejected` | fake confirmatory states are refused | `COHORT_MISSING` ×2, `ENUM_VIOLATION`, `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2`, `COHORT_ID_SHARED` | `TestG4Table3` |
| C8 | `test_post2019_rows_never_reach_fit_thresholds_stress` | F-fake NaN versus 1e6 post-2019 rows: identical real numeric results, under the bounded §9 exception list | identities differ only in `inputs`/`input_hash`/`config_hash`; a perturbed calib row changes `basis_hash`; ID integrity checked per artifact | `test_g3_real_pre2020_pipeline…` |
| C9 | `test_stress_library_historical_and_qbar_not_oracle` | 2008/2011 windows only; 2020 and 2022 windows → `IncompleteWindow`; `EXANTE_QBAR` without oracle flag; qbar invariant to event dates | stress axis ≠ oracle axis gives a different S | `test_g3_stress_window…` |
| C10 | `test_oracle_labels_and_sigma1_absent_from_detector` | oracle input ⇔ oracle flag; `TRUE_SIGMA1` only on covariance oracle diagnostics; 2022 ⇔ `RETROSPECTIVE_DIAGNOSTIC`; detector streams blind to C1/M/μ | a 2022 row without the flag is rejected | — |
| C11 | `test_real_rows_na_never_zero_or_target` | real rows NA/BLOCKED in runs and T1–T3; `DATA_UNAVAILABLE` when inputs are absent; D6 bound NA | rmst = 0 on a real path → `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2` | `test_g3_missing_real_inputs…` |
| D1 | `test_reproducibility_hashes_exclude_time_and_paths` | no timestamp, duration or absolute path in identity or CSVs (SMOKE, FULL, F-tiny) | a planted timestamp and path are detected | double run covered by `test_g3_two_fresh_directories_are_byte_identical_and_the_seed_matters` (executed, passed) |
| D2 | `test_sealed_identity_recomputes_with_current_code` | fingerprint and `identity_block` recomputed with the current code; outputs match the manifest | — | — |
| D3 | `test_figure_points_trace_to_aggregates` | 301 finite points per run traced lineage → SOURCE → runner cell; RMST rows are ALT_RMST OK/EXECUTED; `null_fpr` = measured FPR; k = 1..20 | `null_fpr` replaced by the 0.05 target is detected | `TestG1Chain` |
| D4 | `test_cov_figure_exploratory_effective_labels` | effective tags and title carry `COV_SURROGATE_EXPLORATORY` for cov only; full effective tags without `SMOKE_NO_CLAIMS`; V from `COV_GAUSS_POP_JOINT_*` rows, never `I_cov_marginal_sum`; right axis carries H5 | — | `TestG4Render::test_cov_*` |
| D5 | conditional, abandoned (QR5) | stale or wrong source hash refused | — | `TestG1Chain::test_input_invalid_altered_runner_csv`, `::test_tables_incomplete_refused`, `::test_tables_stale_altered_source_with_updated_manifest`, `TestG1Input::test_hash_mismatch_refused` (executed, passed) |
| D6 | conditional, abandoned (QR5) | missing values become gaps, not interpolations | — | `TestG4Render::test_nan_marker_and_legend_class` (executed, passed) |
| D7a | `test_annotations_follow_values_and_status` (extension) | CPV annotation follows the data (crossing at 14 → "k = 14"); FPR text follows `null_fpr` | the unmodified full figure prints its own values | k = 7 and OUTSIDE cases: `TestG3Conditionals::test_cpv90_annotation_at_k7`, `::test_cpv90_outside_note` (executed, passed) |
| D7b | `test_full_figure_text_sample_sizes_match_manifest` | every printed "n = x" equals a manifest count | **FAIL, see §6** | — |
| G1 | `test_full2000_trials_read_only` | full trials hash, size and rows; group inventory; A15 recipe and C4 identities recomputed exactly | — | — |

**Overlap command.** The producer overlap tests were run once, before the final measurement:
- `.venv/bin/python -m pytest -q -rA <8 node ids>`, 8 passed;
- log: `logs/pca_drift_contracts/overlap_producer_tests.log`.

**G1 inventory.**
- 358 groups: 292 000 alternative rows, 212 000 calibration rows and 212 000 holdout rows.
- 106 OK calibrations recomputed exactly: rank, threshold, maxima hash, `calibration_hash`, bound and holdout FPR.
- 146 ALT_RMST and 106 HOLDOUT_NULL_FPR identities, exact.

## 5. Successful negative tests (kept, never erased)

- **Covariance is not additive.** The joint KL 0.5625 differs from the marginal sum 0.33936 (A5). The covariance `ORACLE_Q_*` rows are UNSUPPORTED or absent (B5).
- **Covid under the standard embargo** is `NOT_EVALUABLE_STANDARD_SPLIT`, with metrics NA (C6, C7, C11).
- **CPV90 lies outside the top 20.**
  - T3 rows are `CPV90_OUTSIDE_TOP20` / `NOT_COMPARABLE_OUTSIDE_TOP20`, with S and metrics NA.
  - Population CPV14 = 104/239 = 0.435146, not 0.902 (A11).

## 6. D7b FAIL and STOP state

- **Test.** `test_full_figure_text_sample_sizes_match_manifest`, defined last, failed in the final measurement.
- **Input.**
  - `pf.load_context(FULL, TAB_FULL)`, then `pf.build_entry` and `pf.render_figure` in memory for `mean` and `cov`.
  - FULL manifest counts: `n_cal = n_null = n_alt = 2000`.
- **Output.** Both rendered figures print "FPR comparability (P identity + Wilson W): descriptive filter, not an equality test (n = 40)".
- **Contract cited.** Prompt 31 §4 says no hard-coded figure text and figure claims traced to measured records; prompt 31 §3 says sample sizes are never artificially declared. The full figures state n = 40, while the data hold 2000 trajectories per role.
- **Diagnosis.**
  - The string is hard-coded and unconditional in `experiments/figures/plot_figure_1.py:582`.
  - It is not a QA fixture error. The same load, build and render path passed in D4 and D7a, and the failure message quotes the producer text.
  - It is a confirmed producer label defect, as already established in the plan.
- **What the defect does not touch.** The plotted values and intervals are full values, and D3 traced them to the runner cells.
- **Not rendered.** `mean_t7` was not rendered, within the budget of 3 in-memory renders; its footnote comes from the same unconditional line.
- **STOP actions.**
  - No xfail, no skip, no producer or figure change, no rerun.
  - No `make check`, hook, reindex or Git mutation.
  - No commit of the QA file.
- **Pending decision.** A fix needs a separate plan and GO from the researcher.

## 7. QA corrections and rulings

- **Correction 1 (A7, fixture error).**
  - Cause: the grid `linspace(4x/2000, 4x, 2000)` contains the root x, g(x) evaluated to 0.0, and the sign-change count saw two transitions.
  - Strict monotonicity held in that run.
  - Fix: count sign changes on non-zero signs, with at most one exact zero.
  - One attempt; it then passed.
- **§10 corrections (resume of 13:25 UTC).**
  - CSV text reader with `float_precision='round_trip'`.
  - E2 checks the required information fields per `info_kind` on OK rows before any filtering, with a NaN witness.
  - E3 prints the `O-E3-NONFINITE` observation as an observed limit.
  - Targeted control afterwards: E1–E3, 3 passed.
- **E3 ruling.** Only the documented rejections are asserted: the sign of slogdet and the `clip_kl` tolerance. Codex reproduced the non-finite behaviour (§10). It is reported in §8, not as a passed control.
- **B4 ruling, accepted in §10.** For the family mutation on the E3 copy, the documented applicability refusal (`UNEXPECTED_ROW_STATE`) precedes the L17 lineage control. The E2 witness that reaches `L16_PREFIX_IDENTITY` is kept.

## 8. Observations (not contracts; to be arbitrated separately)

1. **O-E3-NONFINITE.**
   - `kl_cov_raw(I, diag(NaN, 1))` and `kl_cov_raw(I, diag(inf, 1))` return NaN without an exception.
   - `clip_kl(NaN)` returns (NaN, 0).
   - The docstring requires SPD inputs; no automatic rejection is promised.
   - The sealed outputs contain no non-finite required information field (E2).
2. **SPD limit.** `kl_cov_raw(I, diag(−1, −1))` returns −2.0, since the determinant sign is positive. `kl_cov` then refuses it through `clip_kl` (`ArithmeticError`).
3. **`spec.tags`.** The registry copy keeps `SMOKE_NO_CLAIMS`; the effective full tags do not (D4).
4. **Covariance `EXANTE_QBAR` rows.** These UNSUPPORTED synthetic rows carry `cost_kind = MIX_FLUID_SURROGATE`. No selection or V is computed on them. A8 checks `HEURISTIC_COST` on the covariance rows that use M.
5. **FPR marker.** The full `Figure_1_mean` prints "FPR mismatch at k = [12]". It is a data-driven marker under the documented rule, not a defect.
6. **Untested areas.**
   - The O(L²) cost of long continuous real paths.
   - Floating near-ties of V outside dyadic q (A3 covers dyadic q only).
7. **Test runtime.** A6 dominates (≈ 12 s): it builds the SMOKE and FULL figure contexts, which group D reuses.

## 9. Files and state

- **Created.**
  - `tests/test_pca_drift_contracts.py` (44 tests, 1 502 lines, SHA-256 `dad74703d69f33ce1d5e6ce702b5eaaa2ca608eb15d8b7f2ea511bc0576e9c1a` at the final measurement);
  - this report;
  - ignored logs under `logs/pca_drift_contracts/`.
- **Codex files untouched.** `prompts/plans/plan-31.md` and `prompts/GO-stream-31.md` are unchanged by this lot.
- **Effect on the worktree.** The untracked QA file is collected by `make check` (`Makefile`, plain `pytest`). Until arbitration, every `make check` or pre-commit hook in this worktree will fail on D7b (QQA3).

## 10. D7b fix measurement (2026-11-06)

**Authority.**
- Researcher amendment `FIX-stream-31-nb-assets.md` (SHA-256 `ce91c1899db2fac30dcb88e64f3b1043861263adb7c2988d5394a706b84735e6`) and implementation prompt `31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` (`fbfccc96fc777b6fef600ae9b16239ba46a852b68444ec3b717ac1d0a8e36c4c`), archived unchanged under `logs/pca_drift_contracts/`.
- Codex GO `prompts/GO-stream-31-fix.md` (15:32 UTC) and plan `prompts/plans/plan-31-fix.md`, with the decisions of its §8.
- The GO lifts the D7b STOP only for the label fix and the replacement of the two full figure directories.

All logs of this section are under `logs/pca_drift_contracts/fix_d7b/` (ignored), with the run ledger in `ledger.md`.

**Producer change.** `experiments/figures/plot_figure_1.py`: 2 lines modified, none added (`git diff --numstat`: 2 2).
- L460, `build_entry`: `meta` gains `"n_null": int(ctx.manifest["config"]["n_null"])`, the run's null holdout count (SMOKE 40, FULL 2000).
- L582, `render_figure`: the footnote prints `(n = {meta['n_null']})` instead of the constant `(n = 40)`.
- Not used, because they are not the FPR sample size: `config.real.n_null` (2000 even in SMOKE), `config.N` (239 assets), `n_cal` and `n_alt`.
- Tracer SHA-256: `c40a5e77c4dbc54a17b8d5148b8271be46a5e1a16b8c99b9dcefd84ffe79a516` (historical, §1–9) → `a38fc46b1b45ed3e6e257a53c4ce29f9152b8e956b68d9d55771c58ff48634f2` (current). The runner `8324b47b…` and the tables `13d386fe…` are unchanged.
- `figure_manifest.json`: each `records.<key>.render` gains the additive field `n_null`; `figures_schema` stays `pca_drift_figures/1`.

**QA test change.** D7b is extended in place and stays last. The file keeps 44 tests (1 509 lines, SHA-256 `2e488fe7eb175466e3d259b2f08cb3a236bb1f57ef33619da9d5efabd2c7f197`).
- The full assertions are unchanged: every `n = x` printed by the in-memory FULL `mean` and `cov` renders must be a manifest count (2000).
- Added: the in-memory SMOKE `mean` render must print 40.
- Added: a probe must print 39. It is an in-memory copy of the SMOKE manifest with `n_null = 39` and `n_cal = n_alt = 40`.
- The probe separates the null holdout count from constants, `n_cal`, `n_alt`, `config.real.n_null` and N. Neither the shared fixture nor any sealed file is mutated.
- `mean_t7` was not in the initial D7b assertion; D7a only rendered an altered in-memory copy of it. The installed `mean_t7` PDF and SVG are checked by text extraction below.

**RED and GREEN.** D7b node ID: `tests/test_pca_drift_contracts.py::test_full_figure_text_sample_sizes_match_manifest`.

| Step | Selection | Exit | Result (log) |
|---|---|---:|---|
| RED, before the producer change | D7b | 1 | 1 failed: "sample sizes [40] != manifest counts [2000]"; smoke `{'SMOKE': [40], 'SMOKE_n_null_39': [40]}` (`red_d7b.log`) |
| GREEN | D7b | 0 | 1 passed: FULL [2000]; `{'SMOKE': [40], 'SMOKE_n_null_39': [39]}` (`green_d7b.log`) |
| GREEN | D2, D3, D4, D7a, D7b by node ID | 0 | 5 passed (`green_D.log`) |
| GREEN | `tests/test_plot_figure_1.py` | 0 | 39 passed (`plot_tests.log`) |
| GREEN | `pyflakes` on the tracer and the QA file | 0 | no output |

The RED shows only the known D7b regression; no other test failed.

**Re-render.** One command, from the sealed run and tables only, into a fresh ignored directory:

```bash
.venv/bin/python experiments/figures/plot_figure_1.py --input-dir results/pca_drift_benchmark/full_2000_20261101 \
  --tables-dir results/pca_drift_benchmark/tables/full_2000_20261101 \
  --output-dir logs/pca_drift_contracts/fix_d7b/render_full --figure both --strict
```

It exited 0 in 11.1 s and wrote 17 files. Neither the runner nor the tables were run again, and no return was read; `--strict` hashes the declared `splits.yaml`.

**Checks before replacement** (`render_checks.log`, `s4_text_checks.log`).
- `verify_figures_dir` is true, with the same 17 names as both full directories.
- `command` is identical to both sealed manifests: `--output-dir <OUT>`, relative input and tables paths, `--figure both --strict`.
- `figures_schema`, `input`, `tables`, `environment`, `filters` and `strict` equal the previous `_fix` manifest.
- `code`: the new tracer; the runner and the tables unchanged.
- `figures_fingerprint`, recomputed: `57a25a08dfcc2304ef7538ca3601b30d5e33185774da63a6c4aec3b343971b6c` (previous `_fix`: `df4e5c30…`).
- Records equal the previous `_fix` records except `render.n_null = 2000`; no `SMOKE_NO_CLAIMS` tag.
- Unchanged: the three source CSVs (`8a2ec3a4…` cov, `a4c343a2…` mean, `f8ec238c…` mean_t7) and the three captions. Changed: the 9 SVG/PDF/PNG, `FIGURE_CHECK.md` and `figure_manifest.json`.
- No file contains a home-directory or render-directory path, so the provenance does not depend on the final directory.
- `FIGURE_CHECK.md`: strict PASS. For the three figures: text_in_frame, legend_disjoint and ylim_covers PASS; font_min 6.0 pt; PNG (1620, 1050) PASS; no issue.
- Text, from pdftotext and the SVG with whitespace normalised:
  - each of `mean`, `mean_t7` and `cov` prints "equality test (n = 2000)" once in the PDF and once in the SVG, and "n = 40" never;
  - `SMOKE_NO_CLAIMS` never appears; `COV_SURROGATE_EXPLORATORY` appears only in `cov`;
  - the PDF page is 252 × 388.8 pt.
- Before replacement, the three PDFs and SVGs of both full directories printed "n = 40"; the older directory also printed `SMOKE_NO_CLAIMS`.

**Backup and installation.**
- Both directories were copied in full under `logs/pca_drift_contracts/fix_d7b/backup/` (34 files, `backup.sha256` `cb54e770…`). The copy equals the before inventory after prefix normalisation, and was checked before overwriting.
- Each final directory kept its name and the same 17 names. Its files were overwritten in place by `cp` from the verified render; nothing was removed.
- `sha256sum -c render.sha256`, run from inside each final directory: 17/17 OK for each.
- `verify_figures_dir` is true for both; both directories are byte-identical to the render, with mode 644.

**Inventory.** `inventory_before.txt` and `inventory_after.txt` have 136 lines each; `inventory.diff` holds their differences, which are only:
- the tracer;
- `full_2000_20261101`: 14 files (9 graphics, 3 captions from the older tracer `5346b314…`, `FIGURE_CHECK.md`, the manifest);
- `full_2000_20261101_fix_smoke_no_claims`: 11 files (9 graphics, `FIGURE_CHECK.md`, the manifest).

Unchanged:
- both SMOKE figure directories, byte for byte. They stay linked to their historical tracers `f2a0e7f0…` and `c40a5e77…`; no replay of their old `records.render` with the new code is claimed;
- the SMOKE and FULL runs and both table directories;
- J1: disk = index = `e315e537…0823`, 47 CRLF, no bare LF;
- D8: `1ca7c3ae…68b3`, still FAIL +5.2833 %;
- `docs/DEVIATIONS.md`, `PLAN.md` (`ed14c47a…`), the runner, the assembler and `tests/test_plot_figure_1.py`;
- the plan and GO files and the researcher's files;
- the lot 2 logs: `qa.log` `08fae104…`, `ledger.md` `83543c4f…`.

**Final measurement.**
- `PCA_FULL2000_TRIALS=… .venv/bin/python -m pytest -q -rA --durations=0 tests/test_pca_drift_contracts.py`, in `qa_after.log`:
  - exit 0, 44 passed, 0 failed, 0 skipped, no xfail, 33.63 s;
  - G1 ran: 716 000 rows, 358 groups, 106 calibrations, 146 ALT_RMST, 106 HOLDOUT_NULL_FPR;
  - D3 traced 301 values on the installed `_fix` directory.
- `PYTEST_ADDOPTS=-rs .venv/bin/make check`, with the same variable, in `make_check.log`:
  - exit 0 in 8 min 40 s; pyflakes silent;
  - 37 passed, then 589 passed and 5 skipped;
  - the five skips predate this fix and are D4 availability skips: `tests/test_chars.py:69` and `:83`, `tests/test_data_eurofidai.py:318`, `:326` and `:337`. None is a QA skip.
  - `-rs` only lists the skip reasons.

**State.**
- Nothing is staged or committed.
- `git status` shows ` M experiments/figures/plot_figure_1.py` and 25 ` M` figure files (14 + 11), plus the files already listed: the Codex plan and GO, the wrapup, this report and the QA file.
- The wrapup, AST reindexing, the hook-run `make check`, the commit and the push belong to Codex. The hook needs `PCA_FULL2000_TRIALS` exported; otherwise G1 skips for availability.

## 11. Codex review before integration (2026-11-06)

Independent read-only verification exited 0. Of the 83 files in the Codex pre-fix inventory, 25 changed within the two authorised full directories and 58 remained byte-identical. Both full directories contain identical files. All four figure directories pass `verify_figures_dir`, including output sizes and SHA-256 checks. The two full fingerprints were independently recomputed from canonical JSON and match their manifests.

For all three entries in both full directories, PDF text extracted by `pdftotext` and SVG text contain `equality test (n = 2000)` and no `n = 40` or `SMOKE_NO_CLAIMS`. PNG geometry is 1050 × 1620 pixels; visual inspection of the three PNGs confirms the new footnote. J1 disk and index agree byte for byte, with 47 CRLF lines; D8 and `PLAN.md` retain their reference hashes. No benchmark or table was rerun by Codex.

| Object | Before SHA-256 | After SHA-256 |
|---|---|---|
| Tracer | `c40a5e77c4dbc54a17b8d5148b8271be46a5e1a16b8c99b9dcefd84ffe79a516` | `a38fc46b1b45ed3e6e257a53c4ce29f9152b8e956b68d9d55771c58ff48634f2` |
| `full_2000_20261101/figure_manifest.json` | `d1dfe3c203860d00e82602e037712728804865a7564a52d1dd2654fb138cb877` | `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |
| `full_2000_20261101_fix_smoke_no_claims/figure_manifest.json` | `9e3b666fb40fc281bd77402214f6dafc55c1daa6a73c576e7feacb6a8be63984` | `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |

The new fingerprint of both full figure directories is `57a25a08dfcc2304ef7538ca3601b30d5e33185774da63a6c4aec3b343971b6c`; the previous fingerprints were `9c1fff931a1a1d3541128ae3cab9b0b4c9d77374a64c8041709968a5c3b86473` and `df4e5c30c9f891922e989a477a6fe608f111a171f6b658afc14929294737633d`, respectively. Individual output hashes are recorded in the manifests; the original bytes remain in Git history and in the verified ignored backups.

**Operational exception.** The auxiliary S4 text-reporting shell block returned 1 because its final metadata condition was false for the old directory. Its 21 result lines show no failed content check. This nonzero status is retained in the ledger and is not presented as a successful command. Codex's independent checks above use explicit assertions and subprocess exit checking, complete with exit 0, and confirm the installed content. No scientific statistic, tolerance or producer contract was changed to address this reporting error.
