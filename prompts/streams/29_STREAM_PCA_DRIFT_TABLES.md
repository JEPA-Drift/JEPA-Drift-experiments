## PROMPT 29 — Three reproducible PCA benchmark tables (CSV and Markdown)

**ROLE**: Claude Code stream responsible exclusively for table assembly/formatting in an isolated worktree; Codex must approve the read-only plan first. Target `experiments/pca_drift_tables.py`. Read `11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md` §3, stream 28 schema handoff, kickoff scientific corrections, `AGENTS.md` and repository conventions. **Never simulate observations, refit PCA, calibrate thresholds, or recompute a detector here.** All scientific data must come from the runner's immutable outputs.

### 1. Inputs / outputs

CLI: `--input-dir results/pca_drift_benchmark`, `--output-dir results/pca_drift_benchmark/tables`, optional `--dataset`, `--scenario`, `--detector-family`, `--format csv|md|both`, and `--strict`. Validate `manifest.json`, `spectra.csv`, `selection.csv`, `aggregates.csv`, `calibration.csv`, `issues.csv` (or the exact signed schema from stream 28). Match on stable keys (`dataset_id`, `cohort_id`, `split_hash`, `event_window_id`, `event_id`, `null_id`, `detector_family`, `k`, `selection_id`, `metric_id`, `config_hash`, `basis_hash`, `calibration_hash`, `null_calibration_id`, `seed`). Reject duplicate metric keys and stale schema/fingerprint; never join only on k.

Write `Tableau_PCA_1.csv/.md`, `Tableau_PCA_2.csv/.md`, `Tableau_PCA_3.csv/.md` plus `TABLES_VALIDATION.md`, `table_manifest.json`, and optional `tables_long.parquet`. Numeric files UTF-8 and machine-readable, displayed decimals separate from unrounded source values. Source provenance and footnotes are **part of the result**, not cosmetic.

### 2. Tableau_PCA_1 — spectral variance baseline (k=1..20)

Per valid scenario/detector family, exactly 20 rows in ascending k or explicit `BLOCKED/NA` status. Schema/output columns (preserve French titles in Markdown):

1. `Indice k` (1..20);
2. `Valeur propre λ_k` from **Ledoit–Wolf covariance**, never eigenvalue from correlation disguised as covariance;
3. `Variance cumulée CPV_k (%)` from `Σ_{j≤k}λ_j/Σ_{j≤N}λ_j` on the same fit split;
4. `Critères standard` indicating MP count (**calculated on sample correlation**), 90% CPV when reached, Kaiser applicable only to correlation `λ>=1`, or `—`; do not print `Kaiser λ<1` as selection convention;
5. `RMST250 préfixe (jours)` measured from **actual first-alarm times**, not inferred from analytic V;
6. `Dimension retenue` = k for the prefix;
7. `FPR250 hors dérive` from **independent evaluation null** (never hardcode 5%);
8. `n_cal / n_eval / n_alt`, `detector_family`, `status`, `metric_id`, `CI`, `source_kind` (extra provenance columns or footnote).

The source table example's `k=14, CPV=90.2%`, sample λ, RMST and FPR numbers are **placeholders, not findings**. For a 239-dimensional equicorrelated covariance with ρ=0.4, even the *population* CPV of the first 14 eigenvalues is only `(96.2+13×0.6)/239≈43.5%`; do not force 90% at k=14. Calculate actual `k90_full` over all N. When `k90_full>20`, annotate `CPV90_OUTSIDE_TOP20`, with no fake baseline. If data unavailable or split invalid, use `NA` + explicit reason.

### 3. Tableau_PCA_2 — prefix versus selected subset within P_k

At each k, show the **same prefix** as Tableau 1 plus the best subset S*_k selected from axes 1..k under the declared objective. Required columns:

- `Indice PCA k`, `Variance λ_k (H0)`, `Information marginale q_k` **with information type** (`MEAN_GAUSSIAN_EXACT`, `MEAN_GAUSSIAN_PROXY`, `COV_GAUSSIAN_MARGINAL_PROXY`);
- `Score préfixe V(P_k)`, `RMST250 préfixe`;
- `Sous-ensemble optimal S*_k` serialized deterministically as 1-based sorted axis IDs, `Score V(S*_k)`, `RMST250 sélection`, `Dimension optimale d*_k`, `FPR250 préfixe`, `FPR250 sélection`;
- `metric_id_prefix`, `metric_id_subset`, `selector_kind`, `selection_exact`, `status`, `CI`, `dataset_id`, `event_id`, `detector_family`.

**Identity invariant**: matching `cohort_id`, `split_hash`, detector, null cohort and evaluation horizon are prerequisites. Prefix RMST/FPR and their `metric_id_prefix` are **retrieved as exact values from the corresponding Tableau 1 aggregate**, never recomputed, rounded then compared, or resimulated. The requested bitwise identity is attainable only by referencing the same source metric object/bytes.

**Mean shift**: for diagonal Gaussian reference in the fixed PCA basis, `I(S)=Σq_j`; at each k, optimal additive selection is top-`d` q by descending value for every d=1..k, then maximize `I(S_d)/M(d,γ)` with deterministic tie rules. Never stop before evaluating every d. If Student background, mark `q` and `V` as **Gaussian-model proxies**, even while empirical RMST is genuine.

**Covariance rotation**: report marginal `q_k^cov` for diagnostic only. A rotated alternative is not diagonal in fixed PCA coordinates; `Σ marginal KL` is **not** `I_cov_joint(S)`. The primary covariance selection uses runner-provided joint covariance Gaussian proxy and a declared approximate/exact subset search; mark `selection_exact` honestly. `M(d,γ)` is a mean-mixture fluid cost and **not theoretically validated as covariance-delay penalty**. Therefore either (a) present covariance `V=I_cov_joint/M` only as `COV_HEURISTIC_SURROGATE`, with explicit warning, or (b) print `NA` for theoretical V, alongside empirical covariance RMST. Do not call the marginal-q ranking the covariance oracle. Keep mean and covariance outputs in separate named blocks/files if necessary.

### 4. Tableau_PCA_3 — ablation and historical ex-ante selection

For each eligible scenario and **cohort_id**, show baseline CPV90, oracle q+affine surrogate, oracle q+Gaussian-mixture-fluid surrogate, ex-ante qbar greedy; in covariance add an explicitly marked joint-covariance-search diagnostic (do **not** conflate with additive oracle). Required user-facing core columns:

`Rupture testée | Pipeline & règle | Information I(S) / type | Coût M(d) / applicability | Score V(S) / meaning | RMST250 (jours) | Dimension retenue d* | FPR250`.

Append `n`, CI, detection rate, censoring, event window, oracle status, calibration ID, basis hash, selection axes, `metric_id`, `status` and footnotes. `d*` is printed after RMST and before FPR, as requested.

- Mean rows: ensure **same** `S*` and `V*` as Exp 2 at k=20 for `ORACLE_Q_MIX`, and **same** RMST/metric_id from the exact cached trial aggregate; no rerun.
- Affine oracle: `C(d)=a+cd`, a,c fixed, distinct from Gaussian-mixture M.
- Ex-ante greedy: qbar from 2008/2011 historic stresses, independent of 2020/2022 tested events; do not call it oracle. Return information proxy and RMST only after valid test.
- CPV90: if global cutoff exceeds top20, mark `OUTSIDE_TOP20` and `not_comparable_under_common_candidate_universe`, optionally show real full-spectrum CPV90 only in a separate diagnostic, not as a competing 20-axis selection.
- **Both Covid cohort rows are mandatory and must be distinct**: `cohort_standard_embargo` (65-session post-2020 embargo; `NOT_EVALUABLE_STANDARD_SPLIT`, `RMST=NA`, `FPR=NA`) and `cohort_retrospective_covid` (no post-2019 embargo; monitor starts `2020-01-02`; `REAL_RETROSPECTIVE_EXPLORATORY`; onset `2020-02-24`, episode ends `2020-03-23`). Include `cohort_id`, split dates, whether the monitor was armed and its pre-onset alarm/reset policy, and event-specific status columns. Display `time_to_alarm_during_event`, `detected_during_event`, and separately `RMST250_post_onset` **only when well-defined**; alarms after 2020-03-23 cannot be described as detection during the acute event. Historical real episodes are single paths, not 2,000 independent replicates; do not publish pseudo-binomial confidence intervals or a stand-alone independent null-FPR estimate from the single Covid trajectory. Ex-post Δ = diagnostic oracle, forbidden as ex-ante input. The standard and retrospective rows cannot share the `metric_id` or silently merge.
- Real 2022: any q from observed 2022 shift is **EX_POST_ORACLE** and not an ex-ante stress predictor. On real data, theoretical Gaussian proxy is not true observed KL, and event windows are not 2000 independent alternate samples.

### 5. Display and audit requirements

- Real measured results must never be inferred from prefilled 4.8/4.9/5.0/5.1/5.2% examples, ideal `d=2`, `12 days`, or any other target picture. Targets and results always use distinct fields.
- Show `FPR_calibration` and `FPR_test_null` distinctly. If only a target exists, show target and `NOT_MEASURED` for achieved FPR.
- All numeric `V`, `q`, `M`, CPV, RMST from the same compatible assumptions / model; no comparison of a Gaussian mean `M` against a covariance experiment as though it were theoretically exact.
- Each Markdown table includes above it: dataset, N, fit/cal/test dates or synthetic lengths, distribution, injected change and amplitude, detector family and threshold calibration, H, n and selection provenance. Under it: status of covariance surrogates and any selection/censoring caveat. Add methodology/definition section **inside** tables document, not hidden in slide notes.
- Leave missing cells `NA`, not `0`, not `...`, and not prefilled illustrative numbers.
- The rendering code must handle wide tables via concise abbreviations plus a legend, not by silently dropping required fields. CSV retains full precision and all provenance fields.
- Generate a machine-readable lineage map: every displayed cell has a pointer to source file + row ID or formula + inputs. Document exact command to regenerate from immutable runner results.

### 6. Tests / acceptance

Assert (1) 20 prefix rows per eligible dataset/scenario; (2) CPV nondecreasing, `CPV_20<=1`; (3) table 1 vs table 2 RMST/FPR/metric_id identity **from same artifact**; (4) table 2 at k=20 vs table 3 oracle-mixture S, V and RMST identical on compatible **mean** scenarios; (5) covariance oracle cannot masquerade as additive-q theorem; (6) real 2020 embargo preserved; (7) no result from a missing trial or uncalibrated detector; (8) CSV and MD values round only at display time; (9) stable ordering and SHA/fingerprint on second run. Provide `TABLES_VALIDATION.md` with counters, skipped blocks, source hashes and errors. Follow isolated-worktree plan/implementation protocol, prompt synchronization, historical SHA and wrapup requirements. Codex decides integration.
