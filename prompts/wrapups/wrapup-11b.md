2026-10-18T11:25:04Z

## 1. Context and Discussion Objectives

- Initial Queries: `prompts/GO-stream-11b.md`, follow-up of stream 11 (audit pushed as `9a36c2f`). It quantifies two caveats of wrapup-11 before section 2 of the paper cites them:
  - (1) the share of the N2 ratio due to the estimation noise of the 60-day Ledoit-Wolf Sigma_t;
  - (2) the selection bias of the market SR^2 at SPY turning points dated ex post.
  Both use the existing building blocks of `experiments/audit_information.py`. Constraints: window 2005-2019, SeedSequence only, SHA-256 determinism over two full runs, `save_fair_csv`, no new figure, existing CSV readers unbroken (new `variant` or `level` values rather than new columns).
- Requirement Evolution:
  - (1) Probes showed that D6 (`injection.symmetrize`) keeps second moments and therefore the dynamics of Sigma_t: on D6 the N2 ratio reproduces the full value (PC1: 5.44 against 5.54 on D2, 11.2 against 11.33 on D3).
  - (2) Researcher decisions (2026-10-18), given through the session's question tool:
    - noise background = random permutation of whole days of W, not D6;
    - `lw60_net = lw60 / lw60_shuffle`, not a difference;
    - placebo = circular rotation of the real SPY phase chain within W, with the rows of the phase crossing the seam pooled;
    - no new column in the existing CSVs; a dedicated CSV for the placebo selection.
  - (3) The GO asked to wait for the researcher's environment fix (pre-commit hook GIT_DIR, AGENTS.md worktree recipe). It had not reached `origin/main`, and the user said "continue": the work proceeded with the GO's own workarounds (`data/raw` subdirectory links; restore `data/derived/MANIFEST.json` and `logs/data/build.log` after hooked commits).
  - (4) Execution ruling: the placebo medians of the debiased market SR^2 are negative, so the real/placebo ratio of the GO is undefined. `selection_factor` is NaN when the placebo median is <= 0; `selection_excess` and `p_placebo` carry the result. The tests check excess > 0 and p < 0.05, not ratio > 1.
- Stylistic and Operational Constraints: as stream 11 (French for user, plan and `docs/DEVIATIONS.md`; English for code, this wrapup and the commit; no comment except `# ponytail:`; no `# noqa`; Conventional Commits without trailers; explicit staging; every Bash call behind `conda activate Trading` then `.venv`).

## 2. Uncompromising Analytical Assessment

- Validated Results:
  - N2 noise (median over 2000 day-permuted backgrounds):
    - D2, F1: `lw60` 3.63-5.54, noise 2.09-2.43, net 1.74-2.40;
    - D3, F1: `lw60` 5.21-11.33, noise 2.72-4.01, net 1.89-3.04;
    - D3, F2: beta 1.74, vol 1.62, momentum 1.45, GICS 1.58-1.88, reversal 0.94. The former 501 of `rev_21` was a denominator artefact: its noise ratio is 535.
  - Placebo, 2000 rotations, debiased market SR^2 (real median; placebo median, 95 % CI; excess; p):
    - D2 lt_spy: 40.77; -2.457 [-2.476, -2.423]; +43.2; p = 0.0010.
    - D2 strict_ps: 19.25; -1.685 [-1.725, -1.649]; +20.9; p = 0.0005.
    - D2 symmetric: 40.77; -2.461 [-2.480, -2.421]; +43.2; p = 0.0010.
    - D3 lt_spy: 38.18; -2.617 [-2.717, -2.476]; +40.8; p = 0.0005.
    - D3 strict_ps: 22.35; -1.744 [-1.777, -1.712]; +24.1; p = 0.0010.
    - D3 symmetric: 38.18; -2.519 [-2.635, -2.465]; +40.7; p = 0.0015.
    - Reading: under random alignment, the debiased market SR^2 between adjacent phases is about 0; the SR^2 at the dated boundaries is selection.
  - Non-regression: the CSVs that stream 11b does not touch (spectrum, eta_by_year, sign_corr, symmetry_tests, budget_share, predicted_gains) and the 8 figures are byte-identical to `9a36c2f`.
  - Tests: `tests/test_audit.py` 29 passed (about 30 s).
- Errors and Dead Ends:
  - D6 as noise background: invalid, see the evolution above (deviation `C-audit-n2-noise`).
  - Real/placebo ratio: undefined because the placebo medians are <= 0 (deviation `C-audit-placebo`).
  - The GO bound "noise ratio close to 1 on i.i.d. Gaussian data" is wrong at real dimensions (3 to 8 at N = 97/239 and 60 days): the ratio is the noise itself. The tested bound is net = 1 under a constant Sigma (1.01 measured).
- Investigated Pathways:
  - Parallel noise computation: `concurrent.futures` with the `spawn` context, as in `pipelines.run_pipeline`. One SeedSequence per background makes the result independent of the number of processes: `test_n2_noise_null_and_workers` compares 1 and 2 processes, and the two full runs used 48 and 7 processes.

## 3. Current State of the System and Handover

- Current System State:
  - Worktree `~/JEPA-Drift-stream-11b`, branch `stream-11b`, base `9a36c2f` (`origin/main`). The commit, rebase and `git push origin stream-11b:main` follow this wrapup.
  - Changed files:
    - `experiments/audit_information.py`: `_directions`, `_noise_chunk`, `n2_noise`, `rotate_phases`, `placebo_rows`, the `--jobs` option, `--quick` with 8 backgrounds and 50 rotations, the log lines;
    - `tests/test_audit.py`: 5 new tests;
    - `results/audit/channel_ceilings.csv` (variants `lw60_shuffle`, `lw60_net`), `results/audit/drift_sharpe_transitions.csv` (level `placebo`), new `results/audit/placebo_selection.csv`, `logs/audit/audit.log`;
    - `docs/DEVIATIONS.md` (`C-audit-n2-noise`, `C-audit-placebo`);
    - `prompts/plans/plan-11b.md`, `prompts/GO-stream-11b.md` (copy of the researcher's GO), this wrapup.
  - Old worktree `~/JEPA-Drift-stream-11` (branch `stream-11`, merged) is still present.
- Execution Environment: Python 3.12.9 `.venv` (numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, statsmodels 0.15.0, matplotlib 3.11.2) behind `conda activate Trading`. Threads = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42. 48 CPU cores; `--jobs` defaults to `os.cpu_count()`. A full run takes about 13 min, mostly the D3 noise: 2000 backgrounds of about 6 s CPU each.
- Critical Points of Vigilance:
  - The stream 11 predicted gains (2->3) divide by the market SR^2 at dated boundaries, which the placebo shows to be selection: the D2 ratios G(2->3, F2) understate the unselected ratio, and the market denominator is not a valid reference. No retroactive correction was made.
  - After each commit through the hook, restore `data/derived/MANIFEST.json` and `logs/data/build.log` (GIT_DIR exported to the hook), until the researcher's fix lands.
  - After the push, delete the untracked `prompts/GO-stream-11b.md` copy from the main tree before fast-forwarding `main` there.

## 4. Inventory of Attachments and Dependencies

### Files [.py]
- **experiments/audit_information.py:**
  - *Description:* stream 11 audit script with the stream 11b additions.
  - *Core Functionalities:*
    - `n2_noise(X, B, F2, keys, jobs)`: noise-only N2 ratios on day-permuted backgrounds, one row per key, spawned processes;
    - `_directions(B, F2, T)`: shared generator of the N2 directions;
    - `rotate_phases(phases, T, offset)`;
    - `placebo_rows(name, dating, phases, y, P, B) -> (placebo level row, placebo_selection row) | None`;
    - `ceiling_rows(d, proj, scales, n_noise, jobs)`.
  - *Inputs:* as stream 11; CLI `--jobs N` (default `os.cpu_count()`), `--quick`.
  - *Outputs:* 9 CSVs in `results/audit/` (new `placebo_selection.csv`: `dataset, dating, n_transitions, n_placebo, sr2_real_median, sr2_placebo_median, ci_lo, ci_hi, selection_factor, selection_excess, p_placebo`), figures unchanged, `audit.log` with the N2 and placebo lines.
- **tests/test_audit.py:**
  - *Description:* 29 tests; new in 11b:
    - `test_n2_noise_null_and_workers` (net within 0.05 of 1 under a constant Sigma, noise > 1, 1 vs 2 processes identical);
    - `test_n2_noise_volatility_regimes` (net > 1.5);
    - `test_rotate_phases`;
    - `test_placebo_controls` (positive control: excess > 0, p < 0.05, factor > 1; null: p in [0.025, 0.975]);
    - `test_placebo_selection_committed` (excess > 0 and p < 0.05 on the committed CSV for both datasets and the three datings).

### Files [.csv, .log, .md]
- **results/audit/{channel_ceilings,drift_sharpe_transitions,placebo_selection}.csv:** changed or new tables; the other six CSVs are unchanged.
- **logs/audit/audit.log:** journal of the committed run (48 processes, 809 s with a concurrent second run).
- **docs/DEVIATIONS.md:** `C-audit-n2-noise`, `C-audit-placebo`.
- **prompts/plans/plan-11b.md, prompts/GO-stream-11b.md:** plan with the integrated decisions; the researcher's GO.

## 5. Hypotheses and Conditional Decision Trees

- Missing Variables: none blocking. The researcher's environment fix (hook GIT_DIR, AGENTS.md worktree recipe) is still pending upstream.
- Decision Trees:
  - If section 2 needs an unselected market SR^2, use the placebo median (about 0) or a dating-free estimator. The real-boundary market SR^2 measures the dating, not the drift information.
  - If a selection ratio is required, a ratio on `sr2_raw` (always positive) or on the placebo mean is possible. Neither is implemented: the excess and p_placebo already answer the question.

## 6. Strategic Recommendations for the Next Instance

- Blind Spots:
  - The stream 11 predicted gains use the selection-inflated market SR^2 as denominator; E1 should compare measured and predicted gains on injected drifts, where no selection exists.
  - N2 net of noise is about 1.7-3.0 on the F1 directions: still above N1 (about 2) only for some directions. The conditional-covariance channel adds little beyond common volatility, and the characteristic-driven F2 net values (1.45-1.88; reversal 0.94) show no large time-varying-loading gain.
  - Move `debiased_sr2`, `mbb_indices`, `_ci`, `rotate_phases` to `jepadrift/stats/` when E4 needs them.
- The kernel modules referenced by the wrap-up protocol were not injected in this session; this handover follows the module's section skeleton, saved to file as the project rule requires.
