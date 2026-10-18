2026-10-18T13:34:40Z

Merged wrapup: this document consolidates `wrapup-11.md` (stream 11, the information audit) and `wrapup-11b.md` (stream 11b, the two refinements) into a single homogeneous record; `wrapup-11b.md` is retired by this merge, and the references to it in `prompts/GO-stream-11b.md` and `prompts/plans/plan-11b.md` are historical and now resolve here.

## 1. Context and Discussion Objectives

- Initial Queries: `/plan prompts/streams/prompt-11-audit.md` (stream 11: information audit of D2 `d2_us97` and D3 `d3_239`, rows dated 2005-2019 only, before J4) and its follow-up `prompts/GO-stream-11b.md` (stream 11b: quantify the two caveats of wrapup-11 before section 2 of the paper cites N2 or the market SR^2). Deliverables: `experiments/audit_information.py`; `results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains}.csv` (8 at stream 11, 9 after 11b with `placebo_selection.csv`); `figures/audit/*.{png,pdf}` drawn from the CSVs; `logs/audit/`. Items: (1) spectrum of the calib covariance, with and without Ledoit-Wolf, eta = lambda_1 / tr Sigma per year, Marchenko-Pastur edge and K; (2) mean sign correlation, Gaussian map, K_eff; (3) central symmetry of frozen directions (PC1-PC20, orthogonalised characteristics): exact binomial test, triples test of Randles et al. (1980), Holm; (4) debiased drift Sharpe spectrum at the SPY phase boundaries, moving-block bootstrap (20 days, 2000 draws), median over transitions, subspaces with d_S <= 30; (5) channel ceilings N1, N2 (rolling 60-day Ledoit-Wolf), N3 (multivariate t); (6) budget share of dated phases with L * I_hat >= ln gamma; (7) predicted gains from `jepadrift/floors.py` (input of E1). Success: all outputs; negative debiased estimates reported (risk R9); SHA-256 determinism.
- Requirement Evolution:
  - (1) Stream 11: the plan was written in plan mode with 16 hypotheses H1-H16, each with a default, after read-only probes; the user paused twice and asked for `conda activate Trading` (now applied to every Bash call, git and ls included; memory updated).
  - (2) `prompts/GO-stream-11.md`: verdict GO, all 16 defaults confirmed, H12 cites the `mvt_static` variant. Context update: `origin/main` = `653ec8b` at GO time (`424b199` pins the interpreter chain in AGENTS.md; `8ae232e` runs the contracts without torch and gates `test_reconstruction_from_cache`); EUROFIDAI data restored in the main tree (out of scope). The GO was integrated ("Décision GO intégrée", (Hn) -> (GO Hn)) and the plan recorded at `prompts/plans/plan-11.md` in the worktree before any code; inline execution (superpowers executing-plans, native, TDD per task, no subagent) in the worktree `~/JEPA-Drift-stream-11`, branch `stream-11`.
  - (3) Stream 11 closed: commit `9a36c2f` pushed (`git push origin stream-11:main`, fast-forward); the untracked `prompts/GO-stream-11.md` copy was deleted from the main tree before fast-forwarding `main` there (GO instruction).
  - (4) Stream 11b (`prompts/GO-stream-11b.md`): quantify (1) the share of the N2 ratio due to the estimation noise of the 60-day Ledoit-Wolf Sigma_t, and (2) the selection bias of the market SR^2 at SPY turning points dated ex post — both realizable in `experiments/audit_information.py` with the existing building blocks. Constraints: window 2005-2019, SeedSequence only, SHA-256 determinism over two full runs, `save_fair_csv`, no new figure, existing CSV readers unbroken (new `variant` or `level` values rather than new columns).
  - (5) Probes before 11b: D6 (`injection.symmetrize`) keeps second moments and therefore the dynamics of Sigma_t — on D6 the N2 ratio reproduces the full value (PC1: 5.44 against 5.54 on D2, 11.2 against 11.33 on D3).
  - (6) Researcher decisions (2026-10-18), given through the session's question tool: noise background = random permutation of whole days of W, not D6; `lw60_net = lw60 / lw60_shuffle`, not a difference; placebo = circular rotation of the real SPY phase chain within W, with the rows of the phase crossing the seam pooled; no new column in the existing CSVs; a dedicated CSV for the placebo selection.
  - (7) The GO asked to wait for the researcher's environment fix (pre-commit hook GIT_DIR, AGENTS.md worktree recipe). It had not reached `origin/main`, and the user said "continue": 11b proceeded with the GO's own workarounds (`data/raw` subdirectory links; restore `data/derived/MANIFEST.json` and `logs/data/build.log` after hooked commits). The fix landed afterwards as `4ea0ee4` (hook + AGENTS.md recipe) and is verified: the hook no longer rewrites `MANIFEST.json`/`build.log`.
  - (8) Execution ruling: the placebo medians of the debiased market SR^2 are negative, so the real/placebo ratio of the GO is undefined. `selection_factor` is NaN when the placebo median is <= 0; `selection_excess` and `p_placebo` carry the result. The tests check excess > 0 and p < 0.05, not ratio > 1.
  - (9) Researcher fixes after the 11b push (`985353b`): `symmetry_rows` guard on degenerate series, `plot()` rcParams save/restore, +2 tests; no output change (the committed CSVs and figures are byte-identical).
- Stylistic and Operational Constraints:
  - French for user communication, the plan and `docs/DEVIATIONS.md`; English for code, docstrings, this wrapup and the commits.
  - Code: no comment except `# ponytail:`; one-line docstrings on public functions; module docstring in the E2 manner; no `# noqa`; no AI watermark.
  - Git: Conventional Commits without any trailer; explicit staging by path; never stage the worktree links (`.venv`, `external`), the D1/D2 files rewritten by the `make check` fixture, or `logs/d4/`.
  - End of stream: wrapup -> `tools/reindex_graphify_jcodemunch.sh` -> `make check` -> single commit -> `git fetch` + rebase on `origin/main` -> range check (no `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` path, no file > 50 MB) -> `git push origin stream-XX:main`.
  - Pre-J4 discipline: only rows dated 2005-01-01..2019-12-31 are read (blocking check in `load`).

## 2. Uncompromising Analytical Assessment

- Validated Results (stream 11):
  - Frozen basis: `PCAOrthogonal(K="mp", mode="factor", shrinkage="ledoit_wolf")` refitted on the calib rows reproduces the committed prompt 6 sidecars (`85147fd9...` D2, `6c44d64a...` D3); K = 5 / 10, MP edge 1.7452 / 2.2619, LW shrinkage 0.0192 / 0.0252.
  - Signs (window 2005-2019): rho_sign 0.2686 (D2) / 0.2577 (D3); sin map 0.409 / 0.394; return correlation 0.416 / 0.391; K_eff = 1/rho 3.72 / 3.88. Calib rho_sign equals `results/data/*_profile.csv` (0.2038 / 0.1870).
  - eta (Ledoit-Wolf) peaks in 2008 and 2011 (0.59) and bottoms in 2017 (0.18 D2, 0.13 D3).
  - Symmetry, Holm 5 % over the joint family: binomial rejects D2 PC1, PC3 and D3 PC1, PC2, PC3, char:rev_21 (q_hat 0.446); triples rejects PC1 (D2), PC1 and PC2 (D3). No GARCH fit failed.
  - Debiased drift Sharpe medians (sr2_debiased, 95 % CI): market D2 40.8 [26.5, 61.5] (lt_spy), 19.3 [8.9, 37.1] (strict_ps); D3 38.2 [22.0, 62.5], 22.3 [11.9, 38.9]. Factor medians around 0 (D2 -3.9 / -2.5; D3 -3.6 / +1.0). Idiosyncratic medians D2 +16.6 / +8.6, D3 -181.6 / -51.7 (R9). Characteristics (D3) +5.4 / +5.5.
  - Predicted gains (gamma = 252): G(1->2, F3) 2.37 / 2.54 Gaussian, 3.62 / 3.83 sign streams. D2: kappa_hat 0.076-0.080, G(2->3, F2) 0.41-0.45 (0.10-0.12 after the M(1)/M(N-1) tax), G(1->3) 3.3-3.4, F1 NaN (factor median < 0). D3: kappa_hat NaN (idiosyncratic median < 0), so F2 and 1->3 are NaN; F1 NaN except strict_ps (0.045).
  - Ceilings: N1 1.968 / 1.998 raw, 1.925 / 1.980 chi-square corrected. N3 `mvt_static` (cited) nu 5.03 / 5.43, J/Sigma^-1 1.247 / 1.207; `mvt_garch` nu 9.2 / 10.9; `t_garch` per direction nu median 6.6 / 8.0. N2 F1 ratios 3.6-5.5 (D2), 5.2-11.3 (D3); F2 GICS 2.9-5.1, beta 10.8, vol 12.0, momentum 70, reversal 501 (the time-averaged drift of a fast-rotating characteristic nearly cancels, so the static information is tiny).
  - Budget share (gamma 20 / 252): market 0.90-1.00 / 0.60-0.78; other subspaces 0.1-0.56 and noise-driven.
  - Determinism: two full runs give identical SHA-256 for the 8 CSVs and byte-identical figures (PNG and PDF); duration 200 s.
- Validated Results (stream 11b):
  - N2 noise (median over 2000 day-permuted backgrounds): D2 F1 `lw60` 3.63-5.54, noise (`lw60_shuffle`) 2.09-2.43, net (`lw60_net`) 1.74-2.40; D3 F1 `lw60` 5.21-11.33, noise 2.72-4.01, net 1.89-3.04; D3 F2 beta 1.74, vol 1.62, momentum 1.45, GICS 1.58-1.88, reversal 0.94. The former 501 of `rev_21` was a denominator artefact: its noise ratio is 535. Reading: once the estimation noise is removed, N2 is of the same order as N1 (about 2) — most of the conditional gain comes from common volatility, and the F2 net values show no large time-varying-loading gain.
  - Placebo, 2000 circular rotations per dating, debiased market SR^2 (real median; placebo median, 95 % CI; excess; p): D2 lt_spy 40.77; -2.457 [-2.476, -2.423]; +43.2; p = 0.0010. D2 strict_ps 19.25; -1.685 [-1.725, -1.649]; +20.9; p = 0.0005. D2 symmetric 40.77; -2.461 [-2.480, -2.421]; +43.2; p = 0.0010. D3 lt_spy 38.18; -2.617 [-2.717, -2.476]; +40.8; p = 0.0005. D3 strict_ps 22.35; -1.744 [-1.777, -1.712]; +24.1; p = 0.0010. D3 symmetric 38.18; -2.519 [-2.635, -2.465]; +40.7; p = 0.0015. Reading: under random alignment the debiased market SR^2 between adjacent phases is about 0 (slightly negative median); the SR^2 at the dated boundaries is selection — it measures the dating, not the drift information.
  - Non-regression: the CSVs that stream 11b does not touch (spectrum, eta_by_year, sign_corr, symmetry_tests, budget_share, predicted_gains) and the 8 figures are byte-identical to `9a36c2f`; the researcher fixes (`985353b`) change no output either.
  - Determinism (11b): two full runs at 48 and 7 processes give identical SHA-256 on the 9 CSVs and identical figures.
  - Tests: `tests/test_audit.py` 31 passed (24 at stream 11, +5 in 11b, +2 with the researcher fixes), about 35 s; `make check` 22 passed + 4 skipped (contracts and decoupling) and 218 passed (rest; the 3 EUROFIDAI real-data tests run in the main tree where D4 is present and skip in worktrees without D4).
- Errors and Dead Ends:
  - Plain percentile bootstrap CIs exclude the debiased estimate: each replicate re-adds sampling noise to the observed mean difference, so draws sit about 252 d c above the estimate (quick D2: idio median 16.6, plain CI [175, 582]). Fixed by shifting the percentile interval by the bootstrap bias mean(draws) - estimate (`_ci`); `test_drift_ci_brackets_the_estimate` is RED with the plain percentile and GREEN with the shift. Deviation `C-audit-debias`.
  - The AGENTS.md worktree recipe (one absolute link `data/raw`) breaks `tests/test_data_eurofidai.py::test_gitignore_blocks_eurofidai`: git refuses pathspecs beyond a symlink, also with `--no-index`. The worktrees use a real `data/raw/` holding links to `d3_yf` and `baf` only. Deviation `C-worktree-data-raw`; the recipe itself was fixed by the researcher (`4ea0ee4`).
  - The prompt's debiasing formula keeps a bias of 252 d c (d + 1) / nu (3.8 at d = 30, n1 = n2 = 250): kept as `sr2_spec`, not used downstream.
  - D6 as noise background: invalid (a daily Rademacher sign keeps the second moments, hence the dynamics of Sigma_t); deviation `C-audit-n2-noise`.
  - Real/placebo ratio: undefined because the placebo medians are <= 0; deviation `C-audit-placebo`.
  - The GO bound "noise ratio close to 1 on i.i.d. Gaussian data" is wrong at real dimensions (3 to 8 at N = 97/239 and 60 days): the ratio is the noise itself. The tested bound is net = 1 under a constant Sigma (1.01 measured), and net > 1.5 under volatility regimes.
  - The pre-commit hook exported GIT_DIR to `make check`: the session fixture of `tests/test_data_d1_d2.py` resolves the Article B commit with `git -C ~/The-Whitening-Advantage-Experiments rev-parse HEAD`, redirected to this repo's HEAD, so the rebuild rewrote `data/derived/MANIFEST.json` and `logs/data/build.log` with the wrong source commit (restored by hand after the stream 11 and 11b commits). Fixed by the researcher (`4ea0ee4`): the hook unsets `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` and `GIT_QUARANTINE_PATH` before `make check`; verified clean.
- Investigated Pathways:
  - Triples test: O(n^2 log n) pair counts with `np.searchsorted` on the sorted sample, equal to the O(n^3) enumeration; variance of NSM3::RFPW (Hollander, Wolfe & Chicken, 2014); about 1.1 s at n = 3774.
  - Multivariate t: ECME (Liu & Rubin, 1995) with zero location; scipy 1.17.1 has no `multivariate_t.fit`.
  - Parallel noise computation (11b): `concurrent.futures` with the `spawn` context, as in `pipelines.run_pipeline`. One SeedSequence per background makes the result independent of the number of processes: `test_n2_noise_null_and_workers` compares 1 and 2 processes, and the two full runs used 48 and 7 processes.

## 3. Current State of the System and Handover

- Current System State:
  - `main` = `origin/main` = `985353b`: `9a36c2f` (stream 11) -> `4974815` (stream 11b) -> `4ea0ee4` (researcher environment fix) -> `985353b` (researcher audit minors).
  - Worktrees `~/JEPA-Drift-stream-11` (branch `stream-11`, merged at `9a36c2f`) and `~/JEPA-Drift-stream-11b` (branch `stream-11b`, merged at `4974815`) are kept; the next stream creates its own worktree from `origin/main`.
  - New files: `experiments/audit_information.py`, `tests/test_audit.py`, `results/audit/*.csv` (9), `figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}`, `logs/audit/audit.log`, `prompts/plans/plan-11.md`, `prompts/plans/plan-11b.md`, `prompts/GO-stream-11.md`, `prompts/GO-stream-11b.md`, `prompts/wrapups/wrapup-11.md` (this merged document; `wrapup-11b.md` retired by the merge). Modified: `docs/DEVIATIONS.md` (`C-audit-debias`, `C-audit-subspaces`, `C-audit-transitions`, `C-audit-ceilings`, `C-audit-gains`, `C-worktree-data-raw`, `C-audit-n2-noise`, `C-audit-placebo`), `tools/pre-commit` and `AGENTS.md` (researcher environment fix).
  - CSV SHA-256 (results/audit): budget_share 80ac03d3d9c32f674010fa7d8f7a353152d5508a23b5cb443f3fd861224ff193; channel_ceilings ce6d159ec6c31b10bc60f9cfdbbed55209d64857993dcc47e47bd7cce97d5b10; drift_sharpe_transitions 4b196a3e003953bd0022d4985df9c985698c17d77953ca6259ead66975769b29; eta_by_year b3485185d6150011f88b5cf7ca1e9ecc057be3c178a0525ec0bfb9b109f0c53d; placebo_selection 9d56e2ca8ca1f358735c4a19a2878597893a6251d4823a9c357544f0d4e1eac0; predicted_gains ac2568ae6c7136d557c66ff24ee57361cdcbf4c65dcb98a8ac233a831ba615e4; sign_corr 92560c88c821bd4182b4ca39b8757a666c85e181275199b60c800f66ee5af813; spectrum ee434bec8acecb19418b470033cd4d3cd40da66c99d8b3fbba5d9589a1dddf51; symmetry_tests 1bcd55d4c0a735ad1da2d0f78ed816dcfd0107e28ff62f1f99b3958b45272f20.
  - Baseline `make check`: 22 passed + 4 skipped (contracts and decoupling), 218 passed (rest; the 3 EUROFIDAI real-data tests run in the main tree, skip in worktrees without D4).
- Execution Environment:
  - Every Bash call starts with `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate`; `.venv/bin/python` is Python 3.12.9 with numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, statsmodels 0.15.0, matplotlib 3.11.2, pyarrow 26.0.0 (`requirements.lock`).
  - Threads: OMP_NUM_THREADS = MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42 (exported by `make`; the audit tests also need this environment when pytest runs outside `make`), MPLBACKEND = Agg (set at the top of the script).
  - 48 CPU cores; the 11b CLI `--jobs` defaults to `os.cpu_count()`; a full run takes about 13 min, mostly the D3 noise (2000 backgrounds of about 6 s CPU each; the committed run took 809 s at 48 processes with a concurrent second run).
  - Worktree links: `.venv` -> `~/JEPA-Drift-experiments/.venv`, `external` -> `~/JEPA-Drift-experiments/external` (absolute links); `data/raw/` is a real directory with links `d3_yf` and `baf` to the main tree (AGENTS.md recipe, fixed by `4ea0ee4`).
- Critical Points of Vigilance:
  - R9 materialised: the idiosyncratic and residual medians are noise-dominated; D3 kappa_hat and the F2 and 1->3 predicted gains are NaN. E1 must not substitute planning values.
  - The market SR^2 at SPY turning points is selection, quantified by 11b (placebo median about -2, excess 21-43, p <= 0.0015 on both datasets and the three datings): it measures the dating, not the drift information. The stream 11 predicted gains (2->3) divide by this selection-inflated denominator, so the D2 ratios G(2->3, F2) understate the unselected ratio; no retroactive correction was made — E1 compares measured and predicted gains on injected drifts, where no selection exists.
  - N2 with a 60-day Ledoit-Wolf Sigma_t also contained the Jensen gap of its estimation noise: quantified by 11b (noise 2.1-4.0, net 1.7-3.0 on F1). The citable value for section 2 is `lw60_net`, presented as mostly common volatility, not the raw `lw60` (`rev_21`'s 501 was a denominator artefact; net 0.94).
  - `i_cond` and `i_static` are in the units of the unnormalised directions; only `value` is scale-free.
  - Sign streams: central symmetry is rejected for PC1 (and PC2 on D3) by both tests and for char:rev_21 by the binomial test; exact sign streams need the D6 symmetrized backgrounds on those directions.
  - The pre-commit hook no longer exports GIT_DIR to `make check` (`4ea0ee4`): `MANIFEST.json` and `build.log` stay byte-identical through hooked commits.
  - The untracked `prompts/GO-stream-11.md` and `prompts/GO-stream-11b.md` copies were deleted from the main tree before fast-forwarding `main` (GO instruction); the tracked copies live in the stream commits.

## 4. Inventory of Attachments and Dependencies

### Files [.py]
- **experiments/audit_information.py:**
  - *Description:* the audit script (items 1-7), argparse, `if __name__ == "__main__":`, with the stream 11b additions and the researcher's guards.
  - *Core Functionalities:*
    - `load(name)`: window rows, refitted frozen calib basis checked against the prompt 6 sidecar, D3 characteristics (NaN -> 0);
    - `spectrum_rows`, `eta_rows`, `sign_rows`;
    - `triples_counts`, `triples_test`, `garch_filter`, `garch_scale`, `char_directions`, `projections`, `symmetry_rows` (guard on degenerate series, `985353b`);
    - `spy_phases`, `transitions`, `debiased_sr2`, `mbb_indices`, `subspaces`, `drift_rows`, `_ci`;
    - `n1`, `rolling_lw`, `info_ratio`, `mvt_nu`, `t_ratio`, `ceiling_rows`;
    - `budget_rows`, `planning_gains`, `predicted_rows`;
    - `n2_noise(X, B, F2, keys, jobs)`: noise-only N2 ratios on day-permuted backgrounds, one row per key, spawned processes; `_directions(B, F2, T)`; `_noise_chunk`; `rotate_phases(phases, T, offset)`; `placebo_rows(name, dating, phases, y, P, B) -> (placebo level row, placebo_selection row) | None`;
    - `plot` (four figures from the CSVs; rcParams saved and restored, `985353b`), `main`.
  - *Inputs:* `data/derived/{d2_us97,d3_239}/{ret_wide.npy,dates.npy,assets.json,splits.yaml,z_*.json}`, `data/derived/d3_239/chars.parquet`, `data/derived/d1_etf4/phases_{lt_spy,strict_ps,symmetric}.csv`; CLI `--datasets d2_us97 d3_239 --out results/audit --fig-dir figures/audit --log-dir logs/audit --boot 2000 [--jobs N] [--quick]`.
  - *Outputs:* the 9 CSVs (schemas in `COLUMNS`, written by `save_fair_csv`), 4 PNG + 4 PDF, `audit.log` (commands, input SHA-256, transitions kept and dropped, R9 counts, Holm rejections, N3 fits, N2 noise and placebo lines, caveats, CSV SHA-256).
- **tests/test_audit.py:**
  - *Description:* 31 tests: window and frozen basis, spectrum and eta, signs against the data profiles, triples test against brute force and its null and power, GARCH filter predictability, characteristic directions, joint Holm, degenerate-series guard (`985353b`), unbiasedness of `debiased_sr2` (2000 Monte Carlo replicates) and the bias of the prompt formula, moving-block indices, SPY transitions on D2, block sums, CI bracketing, N1, rolling Ledoit-Wolf, N2 convexity, ECME recovery of nu = 5, t ratio, budget share, reproduction of the plan v4 gains table, NaN on non-positive medians, CLI smoke test and bad `--boot`, rcParams restoration (`985353b`), N2 noise null and worker invariance, N2 noise volatility regimes, `rotate_phases`, placebo controls (positive and null), `placebo_selection` on the committed CSV.
  - *Core Functionalities:* contract of every public function and of the CSV schemas.
  - *Inputs:* committed derived data and `results/data/*_profile.csv`.
  - *Outputs:* none (temporary directories only).

### Files [.csv, .png, .pdf, .log, .md]
- **results/audit/*.csv:** the 9 audit tables (8 at stream 11; `placebo_selection.csv` added by 11b; `channel_ceilings.csv` gained the `lw60_shuffle` and `lw60_net` variants; `drift_sharpe_transitions.csv` gained the `placebo` level) — `predicted_gains.csv` is the input of E1.
- **figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}:** figures drawn from the CSVs; dataviz reference palette slots 1-2, validator ALL PASS (light); the label overlap suspected at stream 11 was measured and cleared (0 overlapping tick-label bounding boxes on the 35-direction panel).
- **logs/audit/audit.log:** run journal of the committed run (48 processes, 809 s with a concurrent second run).
- **docs/DEVIATIONS.md:** entries `C-audit-debias`, `C-audit-subspaces`, `C-audit-transitions`, `C-audit-ceilings`, `C-audit-gains`, `C-worktree-data-raw`, `C-audit-n2-noise`, `C-audit-placebo`.
- **prompts/plans/plan-11.md, prompts/plans/plan-11b.md:** the plans with the integrated GOs.
- **prompts/GO-stream-11.md, prompts/GO-stream-11b.md:** the researcher's GOs.
- **prompts/wrapups/wrapup-11.md:** this merged wrapup (`wrapup-11b.md` retired by the merge).

## 5. Hypotheses and Conditional Decision Trees

- Missing Variables: none blocking. The researcher's environment fix landed (`4ea0ee4`); the audit minors are closed (`985353b`).
- Decision Trees:
  - If the researcher prefers the plain percentile CI, revert `_ci` to `np.percentile(draws, [2.5, 97.5])`; CIs will exclude the estimates on high-dimensional subspaces.
  - If J2 is judged on the predicted F2 gains, the D3 NaN (negative idiosyncratic medians) and D2 G(2->3, F2) < 1 point to contingency C1; MIN_PHASE (20 days) and the median aggregation are the levers that change the noise, not the estimator.
  - If section 2 needs an unselected market SR^2, use the placebo median (about 0) or a dating-free estimator. The real-boundary market SR^2 measures the dating, not the drift information.
  - If a selection ratio is required, a ratio on `sr2_raw` (always positive) or on the placebo mean is possible. Neither is implemented: the excess and p_placebo already answer the question.

## 6. Strategic Recommendations for the Next Instance

- Blind Spots:
  - E1 must compare measured and predicted gains on injected drifts (D6 backgrounds), where no selection exists; the market SR^2 at dated boundaries is selection and not a valid reference.
  - Section 2 must cite N2 net of noise (`lw60_net`), presented as mostly common volatility, and never the raw `lw60`; the market SR^2 at dated boundaries must be presented as a property of the dating.
  - E1 must not substitute planning values for the D3 NaN, and must use D6 backgrounds for the sign streams on the rejected directions (PC1, PC2 on D3, `rev_21`).
  - E4 needs `debiased_sr2`, `mbb_indices`, `_ci`, `rotate_phases` per subset: move them to `jepadrift/stats/` at that point, with their tests.
  - Hygiene left to the researcher: commit `logs/d4/d4_build.log` as the stream 10 journal, remove the stale untracked `prompts/plans/plan-11-vibe.md`, optionally clean the merged worktrees `~/JEPA-Drift-stream-11{,b}`.
  - When the audit tests run outside `make check`, export the thread/PYTHONHASHSEED environment (the frozen-basis hash is environment-sensitive; `make` exports it).
- The kernel modules referenced by the wrap-up protocol were not injected in this session; this handover follows the module's own section skeleton, saved to file as the project rule requires.
