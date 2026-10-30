# JEPA-Drift — Revision PCA benchmark prompts (2026-10-30)

These files are **revised orchestration instructions**, not evidence that Code Mode, Claude Code, simulations, or integration have been executed. Original delivered prompts remain unchanged. Submit the revised kickoff to Codex and place four canonical files under the repository's `prompts/streams/` **only after** checking for clashes with local repository names.

## Files

- `12_CODEX_AMORCAGE_PCA_EXPERIMENTS_2026_10_30_REVISION.md` — revised kickoff prompt;
- `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md` — no GLR fallback for mean; exact Gaussian-mixture segment-scan CUSUM; two real cohorts;
- `prompts/streams/29_STREAM_PCA_DRIFT_TABLES.md` — distinct Covid cohort rows and event-window metrics;
- `prompts/streams/30_STREAM_PCA_DRIFT_FIGURES.md` — two peer figures, mean and 30-degree covariance rotation;
- `prompts/streams/31_STREAM_PCA_DRIFT_CONTRACTS.md` — exact scan reference tests, covariance diagnostics, dual-cohort guard and canonical-name parser tests.

## Essential conditions

1. The scan statistic `W_t=max_{tau<=t}log L_{tau:t}` is **exactly** implemented for the chosen Gaussian-mixture statistic using prefix sums, including every change start. It is not the conventional O(1) scalar CUSUM recursion. Complexity O(H*d) per step, O(H^2*d) over H, with H=250. No fixed-window GLR substitution.
2. Gaussian LR on Student-t7 or on returns whitened with an estimated covariance is a **quasi-likelihood**, not automatically a valid e-process. The analytic `M(d,gamma)` remains a fluid-model selection surrogate and is not the calibrated scan detector's exact delay penalty.
3. Figure_1_cov is labeled `COV_SURROGATE_EXPLORATORY`. Joint covariance KL must be computed on the selected subspace, not summed from axis-wise marginal KL values. Neither figure has a preordained peak or delay.
4. `cohort_standard_embargo` reports historical Covid event `NOT_EVALUABLE_STANDARD_SPLIT`. `cohort_retrospective_covid` starts monitoring on 2020-01-02 without the post-calibration embargo, is explicitly marked `REAL_RETROSPECTIVE_EXPLORATORY`, and distinguishes alarm during acute event from later hits. The historical sample is a **single path**, not 2,000 replications; do not claim an independent FPR measured from that path.
5. The repository `tools/check_prompts.py` currently uses `STREAMS.glob('prompt-*.md')`. Without an explicit tooling change canonical numeric filenames are ignored and `make prompts-check` may pass vacuously. Stream 31 must amend tooling under Codex approval and prove all four IDs are discovered and matched into the master.
6. Historical E2 CRLF SHA-256, `docs/DEVIATIONS.md`, frozen worktree protocol and existing archive remain protected.

## Integration status

No repository file has been changed; no Claude Code subprocess, experiment, test or CI has been run. Static package integrity was checked locally before delivery. The reported status of the current Git repository must be reverified by Codex before taking action.
