# JEPA-Drift (Article C) — project memory for coding agents

## Scientific purpose
Sequential detection of drifts in daily equity cross-sections. Claim under test: a representation
z_t = phi(x_t; C_t) concentrates the Kullback-Leibler (KL) divergence of a drift into a few directions,
so that exactly calibrated monitors detect it faster than univariate or pooled monitors.
The data-processing inequality (DPI) forbids any KL increase: gains come from concentration only.

## Glossary
- x_t in R^N: log returns of N assets on day t. C_t: characteristics known at the open of day t.
- ADD: average detection delay, Lorden worst case (monitor state reset at the onset).
- ARL0: average run length to a false alarm under H0. gamma: false-alarm budget.
- I: per-day KL of a drift (nats). With SR the annualized Sharpe ratio of the drift-tangent portfolio,
  I = SR^2/504.
- Evidence budget ("Sharpe ceiling"): tau_gamma = ln(gamma)/I = 504 ln(gamma)/SR^2 trading days is the
  expected time for a monitor that knows the onset and the direction to gather evidence gamma (exact,
  Lemma 1). It is NOT the Lorden-optimal ADD at ARL0 = gamma, which is Phi(gamma*I)/I
  (jepadrift/floors.py): 142 days instead of 2,787 for SR = 1, gamma = 252. Always state the reading:
  budget | anytime-valid (e-detector stopped at gamma) | exact (ARL0 calibrated to gamma).
- CUSUM (Article B convention): S_t = max(0, S_{t-1} + s_t - delta); alarm iff S_t > lambda (strict).
  Bilateral = one-sided CUSUMs on s_t and -s_t, the first alarm wins.
- Sign stream: b_t = 1{u_t' phi(x_t; C_t) > 0} with phi odd in x and u_t known at t-1. Under any
  centrally symmetric null it is i.i.d. Bernoulli(1/2) whatever the volatility (Lemma 2); ties are
  broken by an independent fair coin. Article B's Concept detectors monitor the label stream
  1{r_t > 0} - q_hat (a constant predictor), not a classifier's error stream.
- Lattice: a CUSUM on a two-point stream reaches only discrete false-alarm levels. Compute them exactly
  (jepadrift/monitors/lattice.py) and pick the nearest level <= nominal under the strict rule.
- e-detector: statistic M_n >= 0 with E_inf[M_tau] <= E_inf[tau]; alarm at M_n >= gamma gives
  ARL0 >= gamma and P_inf(alarm before H) <= H/gamma. Channels are combined by averaging
  e-detectors, never by multiplying them. e-process inputs live in [-1, 1]: pass
  2*exact_sign_stream(...), or 2*f for a fraction stream f.
- Readings at a fixed horizon H (location experiments, E1 onwards): anytime-valid = e-detector at
  gamma_H = H/alpha (`pipelines.horizon_gamma`), hence FPR(H) <= alpha = 0.05; exact = sign CUSUM
  at the attainable lattice level <= alpha at H, compared with `select_threshold(...)["threshold"]`
  (the lattice midpoint, C-lattice-midpoint), never with `lam`; bootstrap (R15 port, H = 750) and
  randomization (sign flips) target FPR(H) ~ alpha. ARL0 readings (gamma in {20, 252}) belong to
  E2 and E3 only: at gamma = 20 an e-detector alarms on most null paths within 750 days.
  Delays count monitored days up to the alarm included: delay = alarm_index - tau_star + 1
  (C-pipe-delay).
- Drift families, injected in return space only, never in z: F1 factor premia B_t*dlambda;
  F2 characteristic-driven breadth (C_t*dgamma) orthogonalized to the loadings; F3 market-mode
  translation; F4 second order (factor rotation or covariance deformation).
- Backgrounds: D5 Monte Carlo (Gaussian i.i.d. latent; GARCH(1,1)-t7); D6 symmetrized real panels
  (each whole day multiplied by one Rademacher sign: keeps |x|, correlations and volatility
  clustering; erases location drift and leverage).
- PCA-orthogonal: PC1 (market) is a separate monitored channel; the residual is PC2..PC(K+1) with K at
  the Marchenko-Pastur edge, or the full residual. PC1 is never discarded silently.
- Gains: G_floor = I_B/I_A (exact, from the injected drift); G_ADD_av = ADD ratio at equal
  gamma_H = H/alpha (primary); G_ADD_ex = ADD ratio at the same exact lattice level at H (exact
  sign streams only); G_SR = ratio of the smallest SR detected within H days with probability
  >= 1/2. Predicted gains use the injected drift, the measured channel alignment
  a_max = max_k dz_k^2/||dz||^2 and `floors` (dictionary multiplier for dictionaries, M(D) for
  mixtures), never `results/audit/predicted_gains.csv`.
- Pipelines: P1-C/P1-D univariate Concept/Data; P2-C pooled signs; P3-C/P3-D PCA-orthogonal; P3-KF
  PCA tail (prior art); P3-CS degree-0 cross-section and ranks; P4 IPCA/CD-DFM; P5 JEPA; P6 BAF;
  P7 oracle with known drift direction.

## Data, splits, leakage
- D1 ETF-4 (SPY, PFF, VNQ, BWX), D2 US-97 survivors, D3 S&P 500, D4 EUROFIDAI (proprietary),
  D7 BAF (synthetic tabular), D8 optional sensor panels.
- D2-D4 splits: pretrain [2005-01-01, 2016-01-01), calib [2016-01-01, 2020-01-01),
  monitor [2020-01-01, end]; embargo of 65 trading days after each boundary. BAF months: 0-2 / 3 / 4-7.
- Panel facts that bind every experiment: `d3_239` = the 239 longest-history current S&P 500
  constituents (C-D3-no239); current constituents form a survivorship-biased universe
  (C-D3-survivor-correction); `d3_500` has 13 % NaN and D4 covers 91 % of its cells (callers pick
  complete sub-panels; `injection.inject` needs a finite panel); D4 = 498 EUROFIDAI stocks with
  >= 5,000 observations, no delisting dates, no GICS, MIL missing 2024-2026 (C-D4-survivor);
  D2 has no characteristics (F2 runs on D3 or D4 only).
- Audit findings that bind every experiment (`results/audit/`, wrapups 11 and 11b): central
  symmetry is rejected on raw rows for D2 PC1 (binomial and triples) and PC3 (binomial), D3 PC1
  and PC2 (both tests), PC3 and char:rev_21 (binomial): exact sign streams hold on D6, raw-data
  sign monitors on these channels need q_hat recentring and claim no exactness. The market SR^2
  at dated SPY boundaries is selection (placebo rotations, p <= 0.0015) and the residual drift
  medians are noise-dominated (R9): `predicted_gains.csv` is descriptive and its NaN stay NaN.
- Before milestone J4 (2026-11-08) no hyperparameter, threshold, D* or design choice may use, or be
  evaluated on, the monitor window. After J4, test-window runs require the frozen configuration hash.
- EUROFIDAI data never leave this machine: data/raw/eurofidai/ and data/derived/d4_eurofidai/ are
  ignored and blocked by the pre-commit hook, and nothing under those paths may ever be committed,
  logged or pushed. `git push` of the rest of the repository is authorized (end-of-stream
  workflow, see Engineering rules) while the repository address is not shared publicly and not
  linked to a publication.

## Repository layout
- `jepadrift/`: library — `floors.py` (analytic floors, Article C section 3; frozen lot 1),
  `sim.py` (D5 generators), `injection.py` (D6 symmetrization, F1-F4), `pipelines.py` (registry
  P2-C, P3-C, P3-D, P3-CS, P7; the only module importing both representations and monitors) and
  the subpackages `monitors/` (numpy only: `cusum`, `streams`, `lattice`, `gamma`, `eprocess`,
  `calibration`), `representations/` (interface Z-1: `base`, `pca`, `cross_section`, `extract`),
  `jepa/` (torch), `data_loader/` (`articleB`, `sp500`, `baf`, `eurofidai`), `stats/`
  (`covariance`; `garch`, a verbatim R01 port excluded from pyflakes).
- `experiments/`: one script per experiment or audit (`e2_floor_validation.py`,
  `identity_articleB.py`, `audit_information.py`, then E1, E3, ...), argparse and
  `if __name__ == "__main__":`; a function moves to `jepadrift/` when a second consumer appears.
- `tests/`: unit and contract tests (pytest).
- `paper/`: Article C LaTeX sources (section 3, appendix A, bibliography addendum).
- `prompts/`: stream prompts and orchestration — `prompts/streams/` stores the prompts of the planned streams (one `prompt-NN-<slug>.md` per stream, plus `INDEX.md`: routing table and stream conventions); `prompts/plans/` stores the implementation plans of the streams (one `plan-[XX].md` per stream, [XX] = stream number, recorded before the plan's execution); `prompts/wrapups/` stores the processing summaries of the streams (one `wrapup-[XX].md` per stream, [XX] = stream number, written by the wrap-up directive before each commit); `prompts/GO-stream-[XX].md` stores the researcher's GO review of a stream plan (decision trace,
committed with the stream); the master collection `Prompts_Claude_Code_v5.md` (derived from
`prompts/streams/`, kept in sync by Mistral Vibe via `tools/check_prompts.py`) and
`Orchestration_Streams_v5.md` (historical wave plan, superseded by the routing table of
`prompts/streams/INDEX.md`) live at this level.
- `configs/`: experiment configurations (YAML); `FROZEN.json` after milestone J4.
- `tools/`: repository tooling — `reindex_graphify_jcodemunch.sh` (end-of-stream reindexation of jCodeMunch and Graphify), plus the `pre-commit`/`pre-push` hooks and the freeze/trace scripts added by later streams.
- `docs/`: `sections/` (section notes), `audits/` (lot audits), `manifests/` (hash manifests of
  proprietary data, e.g. `d4_manifest.json`), `DEVIATIONS.md` (deviations under `C-<topic>`),
  `MAPPING.md` (traceability of reported numbers, created by stream 21).
- `data/`: `raw/` (raw data, gitignored) and `derived/` (public derived panels; `derived/d4_eurofidai/` gitignored).
- `results/`: one CSV per stream under `results/<stream>/`.
- `figures/`: PNG + PDF per stream, drawn from CSVs only.
- `logs/`: one run journal per stream under `logs/<stream>/`.
- `external/`: external checkouts and side venvs (gitignored).
- `incoming/`: drop zone for incoming lots (gitignored).
- `.venv/`: Python 3.12 virtual environment (gitignored); `graphify-out/`: knowledge-graph cache (gitignored).
- Root: `CLAUDE.md` (canonical project memory; `AGENTS.md` is a relative symlink to it), `Makefile`, `requirements.txt`, `requirements.lock`, `.gitignore`, `conftest.py`.

## Engineering rules
- Python 3.12. Interpreter: `.venv/bin/python` — the venv is built on the Trading 3.12.9 binary
  (`/home/m53/miniforge3/envs/Trading/bin/python`); activating Trading then the venv is fine, but
  never run Trading's python alone: its numpy 1.26.4 breaks bit-reproducibility tests and rebuilds.
  Before importing numpy: OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1,
  MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42. Seeds: np.random.SeedSequence keyed on
  (stream, cell, replicate); results must not depend on the number of workers.
- jepadrift/monitors/ imports numpy only (never torch, jepadrift.jepa or jepadrift.representations).
  jepadrift/jepa/ never imports jepadrift.injection or jepadrift.monitors.
- Scripts: argparse, `if __name__ == "__main__":`, logs in logs/<stream>/, CSV in results/<stream>/,
  figures (PNG + PDF) in figures/<stream>/ drawn from CSVs only. No notebooks.
- Every reported number traces to a CSV and a script (docs/MAPPING.md). Deviations from the plan or
  from Article B go to docs/DEVIATIONS.md under an identifier C-<topic>.
- When an implementation plan is created for a stream [XX] (explicitly requested by the user in text, or directly via the `/plan` directive), it must be recorded at `prompts/plans/plan-[XX].md` BEFORE its execution.
- Run `make check` before every commit.
- Before every commit, the implementing instance (Mistral Vibe or Claude Code) invokes its wrap-up
  directive and records the summary at `prompts/wrapups/wrapup-[XX].md` ([XX] = the number or
  reference of the stream being processed; the file is refreshed before each commit).
- End of stream (once a stream's processing is finished), in this exact order: (1) the wrap-up
  summary is generated and recorded at `prompts/wrapups/wrapup-[XX].md` (rule above); (2)
  `tools/reindex_graphify_jcodemunch.sh` reindexes jCodeMunch and Graphify; (3) `make check`, then
  a single commit — or several if the stream's work is heterogeneous and part of the deliverables
  risks errors; (4) push — from `main`: `git push origin main`; from a worktree branch `stream-XX`:
  `git fetch origin`, rebase onto `origin/main`, `make check` again if the base moved, then
  `git push origin stream-XX:main` (never push the branch `stream-XX` itself). Push only while the repository address is
  not shared publicly and not linked to a publication (anonymous-submission companion: commits
  stay anonymized, no new author or institution identifiers), and only after checking that the
  pushed range contains no path under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` and
  no file over 50 MB.
- Article B reference code: ~/The-Whitening-Advantage-Experiments (local checkout, read-only, used as-is at commit a05f0d9c654b6692e626080c298acebc0f0a0b5c (recorded in
  data/derived/MANIFEST.json and checked by tests/test_data_d1_d2.py); never clone the remote
  github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments).
  Its code, not the text of its v87 manuscript, is the reference; read its docs/DEVIATIONS.md.
- Languages: French for user communication, plans, GO reviews and `docs/DEVIATIONS.md` entries;
  English for code, docstrings, `docs/sections/`, wrapups and commit messages.
- Code style: one-line docstrings on public functions (contract or provenance); no comment except
  `# ponytail:` (a deliberate ceiling); no `# noqa`; verbatim ports keep their own text and are
  frozen by byte-identity tests; no AI watermark; Conventional Commits without trailers; staging
  by explicit path only.
- Stream workflow: `/plan` with explicit hypotheses and defaults -> researcher's GO in
  `prompts/GO-stream-[XX].md` -> plan recorded at `prompts/plans/plan-[XX].md` with a "Décision GO
  intégrée" section -> TDD execution -> wrapup -> end of stream. The GO file is committed with the
  stream; an untracked copy left in the main tree is deleted after the push, before
  `git merge --ff-only origin/main` there.
- Wrapups (any agent): English, sections Context, Validated Results (numbers and SHA-256 of
  outputs), Errors and Dead Ends, Current State, Vigilance Points, Recommendations.
- Pre-J4 guard: experiment scripts reading real rows refuse dates >= 2020-01-01 unless
  `configs/FROZEN.json` (stream 21) matches; tests never read such rows (Article B identity
  reproductions excepted).
- Experiments call `pipelines.run_pipeline` / `pipelines.null_check` with a `state` fitted on
  drift-free rows (never `state=None` with injected records); `injection.fit_background` is cached
  per (dataset, window, K); characteristics come from `data_loader.chars`, drift statistics and
  phase placebos from `stats.drift` (stream 8b).
- torch lives only in `.venv` (CPU wheel pinned in `requirements.txt`, from stream 14 on), never
  the Trading environment's torch; once installed, the torch guards of `tests/test_contracts.py`
  must run, not skip.
- `make check` stays under 5 minutes: Monte Carlo tests use reduced sizes; full runs live in
  experiment scripts.

## Worktrees and parallel streams
- Each stream runs in its own git worktree on its own branch: `git worktree add <path> stream-XX`
  (two worktrees cannot check out the same branch). Sequential streams may share the main worktree.
- Shared local state (`.venv/`, `external/`) is exposed in each worktree by absolute symlinks, and
  `data/raw/` is a real directory holding one absolute symlink per raw subdirectory the stream
  reads (`d3_yf`, `baf`, `electricity`; `eurofidai` only when the stream needs D4), so a single
  pinned environment produces stable hashes. A single `data/raw` symlink breaks `git check-ignore` beyond a link: every worktree then
  fails `test_gitignore_blocks_eurofidai`.
- End of stream on `stream-XX`: commit, `make check`, then advance `main` by fast-forward —
  `git fetch origin`, rebase `stream-XX` onto `origin/main`, `git push origin stream-XX:main` —
  after the pushed-range check (no `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` path, no
  file over 50 MB).
- Never run `git stash`, `git checkout` or `git reset` in a worktree owned by another instance;
  never stage foreign files; re-run `git status` before every staging. The session fixture of
  `tests/test_data_d1_d2.py` rewrites the tracked D1/D2 files during `make check`; a rebuild in
  `.venv` reproduces the committed bytes — never stage those files.
