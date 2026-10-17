2026-10-17T04:48:49Z

## 1. Context and Discussion Objectives

- Initial Queries: `/plan prompts/streams/prompt-11-audit.md`, stream 11 (information audit of D2 `d2_us97` and D3 `d3_239`, rows dated 2005-2019 only, before J4). Deliverables: `experiments/audit_information.py`; `results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains}.csv`; `figures/audit/*.{png,pdf}` drawn from the CSVs; `logs/audit/`. Items:
  - 1 spectrum of the calib covariance, with and without Ledoit-Wolf; eta = lambda_1 / tr Sigma per year; Marchenko-Pastur edge and K;
  - 2 mean sign correlation, Gaussian map rho = sin(pi rho_sign / 2), K_eff = 1 / rho_sign;
  - 3 central symmetry of frozen directions (PC1-PC20, orthogonalised characteristics): q_hat with an exact binomial test, triples test of Randles et al. (1980) on u'x_t / sigma_{t|t-1}, Holm;
  - 4 debiased drift Sharpe spectrum at the SPY phase boundaries, moving-block bootstrap (20 days, 2000 draws), median over transitions, subspaces with d_S <= 30;
  - 5 channel ceilings N1, N2 (rolling 60-day Ledoit-Wolf), N3 (multivariate t, J / Sigma^-1 = (nu+1) nu / ((nu+3)(nu-2)));
  - 6 share of dated phases with L * I_hat >= ln gamma, gamma in {20, 252};
  - 7 predicted gains from `jepadrift/floors.py`, written to `predicted_gains.csv` (input of E1).
  Success: all outputs; negative debiased estimates reported (risk R9); SHA-256 determinism.
- Requirement Evolution:
  - (1) The plan was written in plan mode with 16 hypotheses H1-H16, each with a default, after read-only probes; the user paused twice and asked for `conda activate Trading` (now applied to every Bash call, git and ls included; memory updated).
  - (2) `prompts/GO-stream-11.md`: verdict GO, all 16 defaults confirmed, H12 cites the `mvt_static` variant. Context update: `origin/main` = `653ec8b` (`424b199` pins the interpreter chain in AGENTS.md; `8ae232e` runs the contracts without torch and gates `test_reconstruction_from_cache`); EUROFIDAI data restored in the main tree (out of scope); after the push, delete the untracked `prompts/GO-stream-11.md` copy from the main tree before fast-forwarding `main` there.
  - (3) The GO was integrated ("Décision GO intégrée", (Hn) -> (GO Hn)) and the plan recorded at `prompts/plans/plan-11.md` in the worktree before any code; inline execution (superpowers executing-plans, native, TDD per task, no subagent) in the worktree `~/JEPA-Drift-stream-11`, branch `stream-11`.
- Stylistic and Operational Constraints:
  - French for user communication, the plan and `docs/DEVIATIONS.md`; English for code, docstrings, this wrapup and the commit.
  - Code: no comment except `# ponytail:`; one-line docstrings on public functions; module docstring in the E2 manner; no `# noqa`; no AI watermark.
  - Git: Conventional Commits without any trailer; explicit staging by path; never stage the worktree links (`.venv`, `external`), the D1/D2 files rewritten by the `make check` fixture, or `logs/d4/`.
  - End of stream: wrapup -> `tools/reindex_graphify_jcodemunch.sh` -> `make check` -> single commit -> `git fetch` + rebase on `origin/main` -> range check (no `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` path, no file > 50 MB) -> `git push origin stream-11:main`.
  - Pre-J4 discipline: only rows dated 2005-01-01..2019-12-31 are read (blocking check in `load`).

## 2. Uncompromising Analytical Assessment

- Validated Results:
  - Frozen basis: `PCAOrthogonal(K="mp", mode="factor", shrinkage="ledoit_wolf")` refitted on the calib rows reproduces the committed prompt 6 sidecars (`85147fd9...` D2, `6c44d64a...` D3); K = 5 / 10, MP edge 1.7452 / 2.2619, LW shrinkage 0.0192 / 0.0252.
  - Signs (window 2005-2019): rho_sign 0.2686 (D2) / 0.2577 (D3); sin map 0.409 / 0.394; return correlation 0.416 / 0.391; K_eff = 1/rho 3.72 / 3.88. Calib rho_sign equals `results/data/*_profile.csv` (0.2038 / 0.1870).
  - eta (Ledoit-Wolf) peaks in 2008 and 2011 (0.59) and bottoms in 2017 (0.18 D2, 0.13 D3).
  - Symmetry, Holm 5 % over the joint family: binomial rejects D2 PC1, PC3 and D3 PC1, PC2, PC3, char:rev_21 (q_hat 0.446); triples rejects PC1 (D2), PC1 and PC2 (D3). No GARCH fit failed.
  - Debiased drift Sharpe medians (sr2_debiased, 95 % CI): market D2 40.8 [26.5, 61.5] (lt_spy), 19.3 [8.9, 37.1] (strict_ps); D3 38.2 [22.0, 62.5], 22.3 [11.9, 38.9]. Factor medians around 0 (D2 -3.9 / -2.5; D3 -3.6 / +1.0). Idiosyncratic medians D2 +16.6 / +8.6, D3 -181.6 / -51.7 (R9). Characteristics (D3) +5.4 / +5.5.
  - Predicted gains (gamma = 252): G(1->2, F3) 2.37 / 2.54 Gaussian, 3.62 / 3.83 sign streams. D2: kappa_hat 0.076-0.080, G(2->3, F2) 0.41-0.45 (0.10-0.12 after the M(1)/M(N-1) tax), G(1->3) 3.3-3.4, F1 NaN (factor median < 0). D3: kappa_hat NaN (idiosyncratic median < 0), so F2 and 1->3 are NaN; F1 NaN except strict_ps (0.045).
  - Ceilings: N1 1.968 / 1.998 raw, 1.925 / 1.980 chi-square corrected. N3 `mvt_static` (cited) nu 5.03 / 5.43, J/Sigma^-1 1.247 / 1.207; `mvt_garch` nu 9.2 / 10.9; `t_garch` per direction nu median 6.6 / 8.0. N2 F1 ratios 3.6-5.5 (D2), 5.2-11.3 (D3); F2 GICS 2.9-5.1, beta 10.8, vol 12.0, momentum 70, reversal 501 (the time-averaged drift of a fast-rotating characteristic nearly cancels, so the static information is tiny).
  - Budget share (gamma 20 / 252): market 0.90-1.00 / 0.60-0.78; other subspaces 0.1-0.56 and noise-driven.
  - Determinism: two full runs give identical SHA-256 for the 8 CSVs and byte-identical figures (PNG and PDF); duration 200 s.
  - Tests: `tests/test_audit.py` 24 passed (about 24 s, of which about 19 s for the `--quick` CLI smoke test on D2).
- Errors and Dead Ends:
  - Plain percentile bootstrap CIs exclude the debiased estimate: each replicate re-adds sampling noise to the observed mean difference, so draws sit about 252 d c above the estimate (quick D2: idio median 16.6, plain CI [175, 582]). Fixed by shifting the percentile interval by the bootstrap bias mean(draws) - estimate (`_ci`); `test_drift_ci_brackets_the_estimate` is RED with the plain percentile and GREEN with the shift. Deviation `C-audit-debias`.
  - The AGENTS.md worktree recipe (one absolute link `data/raw`) breaks `tests/test_data_eurofidai.py::test_gitignore_blocks_eurofidai`: git refuses pathspecs beyond a symlink, also with `--no-index`. The worktree uses a real `data/raw/` holding links to `d3_yf` and `baf` only. Deviation `C-worktree-data-raw`.
  - The prompt's debiasing formula keeps a bias of 252 d c (d + 1) / nu (3.8 at d = 30, n1 = n2 = 250): kept as `sr2_spec`, not used downstream.
- Investigated Pathways:
  - Triples test: O(n^2 log n) pair counts with `np.searchsorted` on the sorted sample, equal to the O(n^3) enumeration; variance of NSM3::RFPW (Hollander, Wolfe & Chicken, 2014); about 1.1 s at n = 3774.
  - Multivariate t: ECME (Liu & Rubin, 1995) with zero location; scipy 1.17.1 has no `multivariate_t.fit`.

## 3. Current State of the System and Handover

- Current System State:
  - Worktree `~/JEPA-Drift-stream-11` on branch `stream-11`, base `653ec8b` (`origin/main` at GO). The stream commit, then rebase on `origin/main` and `git push origin stream-11:main`, follow this wrapup.
  - New files: `experiments/audit_information.py`, `tests/test_audit.py`, `results/audit/*.csv` (8), `figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}`, `logs/audit/audit.log`, `prompts/plans/plan-11.md`, `prompts/GO-stream-11.md` (copy of the researcher's GO), `prompts/wrapups/wrapup-11.md`. Modified: `docs/DEVIATIONS.md` (`C-audit-debias`, `C-audit-subspaces`, `C-audit-transitions`, `C-audit-ceilings`, `C-audit-gains`, `C-worktree-data-raw`).
  - CSV SHA-256 (results/audit): budget_share 80ac03d3d9c32f674010fa7d8f7a353152d5508a23b5cb443f3fd861224ff193; channel_ceilings 407539600581a9a5c0f77c191ff126de9dadacdd76f6f4b45c29082cb1f73c10; drift_sharpe_transitions b6a6715273428249bcaf62a4a80bee1d8617912b4aa8feec17ae6105da58d4e8; eta_by_year b3485185d6150011f88b5cf7ca1e9ecc057be3c178a0525ec0bfb9b109f0c53d; predicted_gains ac2568ae6c7136d557c66ff24ee57361cdcbf4c65dcb98a8ac233a831ba615e4; sign_corr 92560c88c821bd4182b4ca39b8757a666c85e181275199b60c800f66ee5af813; spectrum ee434bec8acecb19418b470033cd4d3cd40da66c99d8b3fbba5d9589a1dddf51; symmetry_tests 1bcd55d4c0a735ad1da2d0f78ed816dcfd0107e28ff62f1f99b3958b45272f20.
  - Baseline `make check` in the worktree (after the `data/raw` layout fix): 22 passed + 4 skipped (contracts and decoupling), 184 passed + 3 skipped (rest; the 3 EUROFIDAI real-data tests skip because D4 data are absent from the worktree).
- Execution Environment:
  - Every Bash call starts with `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate`; `.venv/bin/python` is Python 3.12.9 with numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, statsmodels 0.15.0, matplotlib 3.11.2, pyarrow 26.0.0 (`requirements.lock`).
  - Threads: OMP_NUM_THREADS = MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42, MPLBACKEND = Agg (set at the top of the script; PYTHONHASHSEED exported by `make`).
  - Worktree links: `.venv` -> `~/JEPA-Drift-experiments/.venv`, `external` -> `~/JEPA-Drift-experiments/external` (absolute links); `data/raw/` is a real directory with links `d3_yf` and `baf` to the main tree.
- Critical Points of Vigilance:
  - R9 materialised: the idiosyncratic and residual medians are noise-dominated; D3 kappa_hat and the F2 and 1->3 predicted gains are NaN. E1 must not substitute planning values.
  - The market SR^2 at SPY turning points includes the ex-post selection of the boundaries; the noise debiasing does not remove it, so ratios to the market SR^2 are biased downward.
  - N2 with a 60-day Ledoit-Wolf Sigma_t also contains the Jensen gap of its estimation noise: the ratio over-states the channel. `i_cond` and `i_static` are in the units of the unnormalised directions; only `value` is scale-free.
  - Sign streams: central symmetry is rejected for PC1 (and PC2 on D3) by both tests and for char:rev_21 by the binomial test; exact sign streams need the D6 symmetrised backgrounds on those directions.
  - After the push: delete the untracked `prompts/GO-stream-11.md` from the main tree before fast-forwarding `main` there (GO instruction).

## 4. Inventory of Attachments and Dependencies

### Files [.py]
- **experiments/audit_information.py:**
  - *Description:* stream 11 audit script (items 1-7), argparse, `if __name__ == "__main__":`.
  - *Core Functionalities:*
    - `load(name)`: window rows, refitted frozen calib basis checked against the prompt 6 sidecar, D3 characteristics (NaN -> 0);
    - `spectrum_rows`, `eta_rows`, `sign_rows`;
    - `triples_counts`, `triples_test`, `garch_filter`, `garch_scale`, `char_directions`, `projections`, `symmetry_rows`;
    - `spy_phases`, `transitions`, `debiased_sr2`, `mbb_indices`, `subspaces`, `drift_rows`, `_ci`;
    - `n1`, `rolling_lw`, `info_ratio`, `mvt_nu`, `t_ratio`, `ceiling_rows`;
    - `budget_rows`, `planning_gains`, `predicted_rows`;
    - `plot` (four figures from the CSVs), `main`.
  - *Inputs:* `data/derived/{d2_us97,d3_239}/{ret_wide.npy,dates.npy,assets.json,splits.yaml,z_*.json}`, `data/derived/d3_239/chars.parquet`, `data/derived/d1_etf4/phases_{lt_spy,strict_ps,symmetric}.csv`; CLI `--datasets d2_us97 d3_239 --out results/audit --fig-dir figures/audit --log-dir logs/audit --boot 2000 [--quick]`.
  - *Outputs:* the 8 CSVs (schemas in `COLUMNS`, written by `save_fair_csv`), 4 PNG + 4 PDF, `audit.log` (commands, input SHA-256, transitions kept and dropped, R9 counts, Holm rejections, N3 fits, caveats, CSV SHA-256).
- **tests/test_audit.py:**
  - *Description:* 24 tests: window and frozen basis, spectrum and eta, signs against the data profiles, triples test against brute force and its null and power, GARCH filter predictability, characteristic directions, joint Holm, unbiasedness of `debiased_sr2` (2000 Monte Carlo replicates) and the bias of the prompt formula, moving-block indices, SPY transitions on D2, block sums, CI bracketing, N1, rolling Ledoit-Wolf, N2 convexity, ECME recovery of nu = 5, t ratio, budget share, reproduction of the plan v4 gains table, NaN on non-positive medians, CLI smoke test and bad `--boot`.
  - *Core Functionalities:* contract of every public function and of the CSV schemas.
  - *Inputs:* committed derived data and `results/data/*_profile.csv`.
  - *Outputs:* none (temporary directories only).

### Files [.csv, .png, .pdf, .log, .md]
- **results/audit/*.csv:** the 8 audit tables (input of E1 for `predicted_gains.csv`).
- **figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}:** figures drawn from the CSVs; dataviz reference palette slots 1-2, validator ALL PASS (light).
- **logs/audit/audit.log:** run journal of the committed run.
- **docs/DEVIATIONS.md:** entries `C-audit-debias`, `C-audit-subspaces`, `C-audit-transitions`, `C-audit-ceilings`, `C-audit-gains`, `C-worktree-data-raw`.
- **prompts/plans/plan-11.md, prompts/GO-stream-11.md:** plan with the integrated GO; the researcher's GO.

## 5. Hypotheses and Conditional Decision Trees

- Missing Variables: none blocking. All 16 hypotheses were confirmed by the GO; two execution rulings remain for the researcher: the shifted-percentile CI (instead of the plain percentile of GO H9) and the worktree `data/raw` layout.
- Decision Trees:
  - If the researcher prefers the plain percentile CI, revert `_ci` to `np.percentile(draws, [2.5, 97.5])`; CIs will exclude the estimates on high-dimensional subspaces.
  - If J2 is judged on the predicted F2 gains, the D3 NaN (negative idiosyncratic medians) and D2 G(2->3, F2) < 1 point to contingency C1; MIN_PHASE (20 days) and the median aggregation are the levers that change the noise, not the estimator.

## 6. Strategic Recommendations for the Next Instance

- Blind Spots:
  - Quantify the noise part of N2: run `info_ratio` on a D6 symmetrised background (Sigma_t constant in truth) to get the noise-only ratio, then report N2 net of it.
  - Measure the selection bias of the market SR^2 with placebo boundaries (random dates with the same phase lengths).
  - E4 needs `debiased_sr2`, `mbb_indices` and `_ci` per subset: move them to `jepadrift/stats/` at that point, with their tests.
  - Amend the AGENTS.md worktree recipe: share `data/raw/<subdir>` links, not one `data/raw` link (see `C-worktree-data-raw`).
- The kernel modules referenced by the wrap-up protocol were not injected in this session; this handover follows the module's own section skeleton, saved to file as the project rule requires.
