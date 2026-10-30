## PROMPT 31 — PCA benchmark scientific invariants and pytest contracts

**ROLE:** independent Claude Code QA stream, isolated worktree, supervised and merged by Codex only. Target `tests/test_pca_drift_contracts.py`, plus minimal local test fixtures/helpers under `tests/` if absolutely necessary. First produce a read-only `PLAN.md` that reads the accepted runner and tables schema and all relevant project tests. Never change production experiment logic to make a test pass without Codex's explicit approval. Preserve historical `results/e2/e2_cells.csv` byte-for-byte. No `xfail`/`skip` to conceal a scientific contract violation; if a dataset-dependent test cannot run, mark it separately as unavailable, and keep all mathematical/unit tests runnable offline.

### 1. Mathematical unit tests (offline, deterministic)

**Mean Gaussian KL**:
- For SPD `Σ`, Δ, confirm `I_full=Δ^TΣ^{-1}Δ/2`.
- In **the actual eigenbasis of the same Σ**, verify `I_full = Σ_k(v_k^TΔ)^2/(2 λ_k)` to numeric tolerance dictated by floating-point precision. Verify subspace cumulative information is monotone **for a fixed Δ** and fixed nested basis. Demonstrate covariance eigenvalue order alone does not guarantee information marginal order; craft counterexamples where only first or last axis carries Δ.
- For `q_k>=0` and cost depending only on cardinality, compare **exhaustive subset enumeration** for small k (k≤12), sorted top-d q optimization and forward-add-largest-q with full cardinality scan; ensure same deterministic selected set and V, with explicit tie-breaking. Do not assert 'early-stop greed' equivalence without a unimodality theorem. Ex-ante qbar differs from true-oracle q unless they happen to coincide.

**Covariance rotation**:
- Construct `Σ0=diag(4,1)` and `Σ1=R(45°)Σ0R(45°)^T`. Compute `KL_joint = 0.5[tr(Σ0^-1Σ1)-logdet(Σ0^-1Σ1)-2] = 0.5625` in this Gaussian example; compare with `Σ_k 0.5(r_k−1−log r_k)≈0.3393`: they are **not equal**. Reject a table that labels their sum `TRUE_KL` or uses the mean oracle's additive optimum on this rotation.
- Verify `Σ1` SPD, nonzero off-diagonal in original eigenbasis, exact symmetry of covariance, and that an energy-increase-only statistic can decrease under a rotation despite positive joint KL.
- On Student-t synthetic data, assert information fields are `GAUSSIAN_PROXY`, never `EXACT_T_KL`.

**Fluid Gaussian-mixture analytic cost**:
- Solve `x=A+(d/2)log1p(2x/d)` with `A=logγ>0`. Verify unique positive solution numerically by monotone function, residual tolerance, `M=x/A>1`, and finite for d=1,4,20,500; with γ=504 check M(4) approximately 1.5696, M(500) approximately 9.6427 to sensible numeric precision. Never label it `EXACT_ADD`, `ARL0`, or `COV_EXACT_COST`.
- Check `V(S)=I(S)/M(|S|,γ)` is *a surrogate ranking* and does not equal measured RMST by definition.

**Covariance and selection**:
- Sample covariance nonnegative, Ledoit–Wolf SPD as required, eigenvectors orthonormal, projected test values equal stored transform from same fitted calibration data. Sample-correlation cutoff `λ_MP=(1+sqrt(N/T))²` counts factors on correlation, not LW covariance. Kaiser `corr_eigenvalue>=1`, not a universal `raw_cov_eigenvalue<1`. Test `CPV_k` monotonic with full-spectrum trace and `CPV_20<0.9` possible; in population equicorrelation N=239,ρ=.4 first14 CPV≈0.435146, *not* 0.902. The test must allow `CPV90_OUTSIDE_TOP20`.

**Exact mean Gaussian-mixture scan-CUSUM (required, no GLR fallback):**
- For short deterministic vectors (`d=1,2,4`, `H<=12`) compute the slow nested loops over all pairs `1<=tau<=t` and compare *every* `logL(tau,t)`, `W_t`, and first-alarm index to the vectorized-prefix implementation, with strict floating-point tolerance (not bitwise equality across different summation orders). Include paths with no alarm, immediate alarm, repeated equal maxima, and nonzero-prefix candidate starts.
- Require `S_0=0`, `S_t=sum_{i<=t}z_i`, segment `S_t-S_{tau-1}`, length `n=t-tau+1`, and `log1p(n*s2)` with a `s2>0` fixed before null test. Complexity instrumentation verifies all t candidate starts are considered, including starts before t-H only when a longer full-monitoring convention is declared. At H=250 full history is 250.
- Student-t7/null from empirical Ledoit–Wolf whitened vectors must not be stamped `EXACT_EPROCESS` or assumed to satisfy Gaussian mgf bounds; holdout null FPR is obligatory. Explicit test rejects `GLR_WINDOWED` as the declared mean primary detector, and rejects alternative-matched `s2` on non-oracle test arms.

### 2. Cross-experiment exact-reuse contracts

Use the **same immutable trial/aggregate** and identical `metric_id` (not recomputation) for prefix P_k in Experiments 1 and 2. For every supported `(dataset_id,event_id,detector_family,k,config_hash,basis_hash,calibration_hash)`:

```text
Tableau_PCA_1.RMST250(P_k) == Tableau_PCA_2.RMST250_prefix(P_k)
Tableau_PCA_1.FPR250(P_k)  == Tableau_PCA_2.FPR250_prefix(P_k)
Tableau_PCA_1.metric_id   == Tableau_PCA_2.metric_id_prefix
```

Equality must be exact at the **source serialized precision**, because both reference one value; do not invoke independent Monte Carlo for the same cell. Do not compare independently formatted rounded strings against full-precision floats and call that bitwise equality.

For each eligible **additive Gaussian mean-shift** scenario at reservoir k=20:

```text
S_star_experiment2_k20 == S_star_experiment3_oracle_mix
V_star_experiment2_k20 == V_star_experiment3_oracle_mix
metric_id_experiment2_k20 == metric_id_experiment3_oracle_mix
RMST250_experiment2_k20 == RMST250_experiment3_oracle_mix
```

Make negative tests that fail when subset array order differs, axis indexing is off by one, the selected set includes an axis beyond 20, a detector family differs, or FPR was borrowed from a different null. **Do not apply these equalities to covariance surrogate selectors** where additive optimality fails or to a retrospective oracle versus ex-ante qbar.

### 3. Time, leakage, and sampling contracts

- Synthetic fit, independent null-calibration, independent null-test and alternative test IDs are **disjoint**; thresholds do not consume holdout null/alternative data. Ensure root-seed child streams are unique and reproducible. Paired trajectories across candidate methods have identical returns, injection, onset and replicate ID.
- Test `H=250`, independent null FPR from holdout, `RMST250 = arithmetic mean(min(hit_time,250))`, and `detect_rate + censored_rate = 1` within tolerance. Test no double-counting of false alarms before a documented onset; origin must be explicit.
- Real split: PCA fitting/calibration 2016-04-07 to 2019-12-31 where data manifest confirms. Test **two disjoint cohort identifiers**: `cohort_standard_embargo` retains 65 trading days and requires Covid `NOT_EVALUABLE_STANDARD_SPLIT`, with unavailable metrics; `cohort_retrospective_covid` uses monitor start `2020-01-02` and retrospective event `[2020-02-24,2020-03-23]`, allows `REAL_RETROSPECTIVE_EXPLORATORY` **only**, with a documented no-embargo deviation. Inject a deliberate fake confirmatory status to ensure the test fails. Assert no 2020 data in PCA fit/null thresholds/ex-ante stress library, and no metric-ID collision across cohorts. Ensure earlier alarms before Feb 24 are not silently reset; an event-window hit is not equated with a hit later in the 250-day horizon. The 2022 event requires `RETROSPECTIVE` status for any ex-post shift estimate. Ex-ante stress-library entries must be historical 2008/2011 and free from 2020/2022 labels/returns.
- Train/validation/test samples must be label-safe and feature-safe; selection on the event's Δ is an **oracle** and any use to create ex-ante qbar is a hard failure. Simulated true covariance Σ1 is allowed only in an explicitly labeled oracle diagnostic.
- Real missing/embargoed data => `NA/BLOCKED`, never 0 RMST or 5% FPR. Sample size on real events is not artificially declared 2000 independent paths.

### 4. Reproducibility, provenance, integration

- Run a tiny deterministic **fixture** suite for both mean and covariance that avoids proprietary files. Reproduce outputs twice with same seed/config and compare normalized CSV bytes/fingerprints; variation due to timestamps must be excluded from reproducibility-critical hashes or documented separately.
- Table/figure schema tests: **both** `Figure_1_mean` and `Figure_1_cov` must be generated from measured upstream records; the latter has mandatory `COV_SURROGATE_EXPLORATORY` metadata and visual legend and cannot label summed marginal covariance KL as joint KL. Every figure point traces to one aggregate row and validated table ID; wrong/stale source hash fails; absent data yields gap/NA not fabricated interpolation. Ensure the figure code cannot hardcode `CPV90 at 14`, `d*=2`, `selected RMST~12`, or FPR=5% measured merely from target.
- Validate parser of axis lists, `1<=axis<=20`, unique axes, sorted stable representation, `d==len(S)`, no silent zero eigenvalues, NaN or negative information for valid Gaussian KL. If severe numerical near-zero negative Gaussian KL arises, allow documented machine-epsilon clipping only after validation; never silently sanitize material negatives.
- Historical invariant: `sha256sum results/e2/e2_cells.csv` equals `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` and the Git index blob hash obtained with `git show :results/e2/e2_cells.csv` hashes identically. Native CRLF must remain unchanged. `docs/DEVIATIONS.md` retains historical D8 FAIL +5.2833%; no newly 'passed' rerun of that case.
- **Canonical filename and parser contract:** exact new paths `prompts/streams/{28,29,30,31}_STREAM_PCA_DRIFT_*.md` beginning with unique `## PROMPT 28 —` through `## PROMPT 31 —`. The CURRENT `tools/check_prompts.py` discovers only `prompt-*.md`; merely renaming would cause silently vacuous pass. Under an explicitly approved tooling change (separate from application code, Codex supervises), update it to collect `prompt-*.md` **and** `[0-9][0-9]_STREAM_PCA_DRIFT_*.md`; validate unique PROMPT IDs, reject duplicate aliases, check expected 28–31 ID set and **exact bytes of each** in `prompts/Prompts_Claude_Code_v5.md` after `--sync-master`. Add regression test: if one canonical prompt is deleted or modified relative to master, `make prompts-check` must fail. Only report 100% sync after demonstrating all four were discovered. After integration run `python tools/check_prompts.py --sync-master` and `make prompts-check`. Run `make check`, then the new test file, report actual outputs and time/split manifest. Do not claim CI success without execution.

### 5. Deliverables and failure policy

Commit `tests/test_pca_drift_contracts.py`, associated fixtures only where needed, and `PCA_CONTRACTS_VALIDATION.md` listing tests run, pass/fail/blocked counts, actual hash verification, and scientific decisions. No re-run of archived streams, no fabrication of future metrics, no modifying application code directly within QA stream except after explicit Codex approval with a new contract. An expected failure from the original mission's invalid assumptions (additive covariance q, Covid event embargo, CPV90 at k14) is a **successful negative test** and must not be erased to make the suite green. Follow read-only planning, headless implementation, worktree isolation, prompt sync and approved wrapup/merge protocol.
