2026-10-17T00:31:19Z

## 1. Context and Discussion Objectives

- Initial Queries: `/plan prompts/streams/prompt-07-pipelines.md`, stream 07 (monitoring 2/3). Deliverables:
  - registry `PIPELINES[id] = (representation, stream_builder, detector, calibration)` and `run_pipeline(spec, X|Z, splits, onset_info) -> alarms.csv`, with columns `run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold, reading`;
  - P2-C, port of R15 (`composition_for`, `worker_null_window_real`, `worker_race_h1_real`): recentred fraction stream, bilateral CUSUM with delta = 0, bootstrap of N_cal = 20 000 windows, H_ref = 500, H_det = 750, FPR 5 %; an added anytime-valid betting e-detector on raw signs; rho_sign and K_eff reported;
  - R15 identity of `rho_sign_meas` and `K_eff_meas` for K in {5, 10, 20} at 1e-12;
  - P3-C: exact sign streams per channel, dictionary of CUSUM e-detectors, optional sub-Gaussian mixture behind a cross-independence gate;
  - P3-D: q_t = (||z_res||^2 - D)/sqrt(2D), strict CUSUM with delta = 0.5, threshold by bootstrap of calibration windows, Gamma_z^op;
  - P3-CS: (a) pivot betting e-process and fixed-design CUSUM calibrated by sign-flip randomization (B = 2000); (b) sign e-detector with predictable stake lambda_t = min(0.5, c/sigma_hat);
  - P7: Gaussian LR CUSUM oracle, reported as a bound;
  - calibrations in `jepadrift/monitors/calibration.py`;
  - tests: D6 null FPR, P2-C bootstrap at 5 %, 100 % detection of F2 at SR = 8;
  - `results/identity/articleB_R15.csv`, `docs/sections/pipelines.md`.

  Blocking for E1 and E3 (J2).
- Requirement Evolution:
  - (1) The plan was written in plan mode with 14 hypotheses H1-H14, each with a default, after read-only probes.
  - (2) `prompts/GO-stream-07.md`: verdict GO, all 14 defaults confirmed. Concurrency instructions: HEAD `672ce26` was local; foreign uncommitted files are never to be staged.
  - (3) The GO was integrated ("Décision GO intégrée", (Hn) -> (GO Hn)) and the plan recorded at `prompts/plans/plan-07.md` before any code; then inline execution (executing-plans, native, no subagent) on `main`.
  - (4) The user paused twice. The user asked twice for `conda activate Trading` and then chose "keep .venv, activate Trading first": every command now runs behind `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate` (memory updated).
  - (5) Incident at 23:49:52 UTC: another actor ran `git stash -u` on the shared tree, removing all uncommitted stream 07 work. Only its untracked files were restored. I restored my tracked files from `stash@{0}` and re-merged the two blocks added after the stash. The owner later dropped the stash. Backups are kept in the session scratchpad.
- Stylistic and Operational Constraints:
  - Language: French for user communication, the plan and `docs/DEVIATIONS.md`; English for code, docstrings, `docs/sections/pipelines.md`, this wrapup and the commit.
  - Code: no comment except `# ponytail:`; one-line docstrings in new code (verbatim ports keep their text); no `# noqa`; no AI watermark.
  - Git: Conventional Commits without any trailer; explicit staging by path; never stage foreign files.
  - Before each commit: `make check` with `.venv` activated and a wrapup.
  - End of stream: wrapup -> `tools/reindex_graphify_jcodemunch.sh` -> `make check` -> single commit -> range check -> `git push origin main`.
  - Isolation: `jepadrift/monitors/` imports numpy, math, fractions and `jepadrift.monitors` only. Seeds come from `SeedSequence` only, and results do not depend on `n_jobs`.
  - Pre-J4 discipline: tests and the CLI read rows up to 2019-12-31 only; the R15 identity reads 2005-2025 for reproduction only.

## 2. Uncompromising Analytical Assessment

- Validated Results:
  - R15 identity from the D2 loader: `load_d2()` is bit-identical to `R15_panel_logreturns.csv`, and `composition_for` matches `R15_panel_composition.csv` for all 10 K.
    - `results/identity/articleB_R15.csv`: 56 cells, all within 1e-12, 54 bit-identical. The two exceptions are rho_sign_meas and K_eff_ana at K = 10 (2.14e-16 and 1.48e-16; summation order of `np.corrcoef`).
    - lambda_boot (34.2 / 24.599999999999966 / 19.900000000000006), FPR_boot (0.053 / 0.0515 / 0.05) and the race at c = 0.25 (DetRate 1.0; ADD 278.112 / 192.467 / 161.663) are bit-identical with R15's own seeds.
    - `articleB_R01_R08.csv` is unchanged (SHA-256 `6d37a97a...`).
  - D6 null on D2, 2000 replicates, H = 750 (`test_null_fpr_d6`):
    - P3-C exact per channel: 0.0385-0.0505 against the exact level 0.043947, region [0.0321, 0.0558];
    - P3-C dictionary at gamma = 15 000: 0.0015;
    - P2-C anytime-valid (K = 97) at gamma = 15 000: 0;
    - P3-CS (a) e-process at gamma = 20: 0.0205;
    - P3-CS (a) randomization: 0.0640, inside [0.0322, 0.0678] (calibration-noise region).
  - F2 at SR = 8 on SYM-D2 (synthetic constant C, H = 2000, gamma = 20, 50 replicates): 100 % detection for P3-C full, P3-CS (b) full, P7, P3-CS (a) e-process and randomization; mean delays 373 / 446 / 15 / 1164 / 1147.
  - P2-C bootstrap on raw D2 at K = 20: lambda_boot 20.0525, held-out FPR 0.0505.
  - P3-D on the D2 calib (H = 500): Gamma^op = 7.64 (factor) and 25.19 (full).
  - Reference CLI run `python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500`: verdict PASS; the second run gives identical SHA-256.
  - `make check`: 186 passed, pyflakes clean, 142 s. 54 targeted tests pass with `-W error`.
- Errors and Dead Ends:
  - A chained comparison `a == b != c` in the P3-CS variant rule rejected every randomization spec (caught by a test, fixed).
  - A CSV round trip changes the `delay` dtype when no row is NaN (test compares values).
  - `fork` from multi-threaded pytest raised a DeprecationWarning; the pool now uses the `spawn` context.
  - The first CLI draft doubled `_null` in the log name.
  - `ast.get_source_segment` drops the trailing comment of R15 l.370 (outside the segment).
  - Probe-time dead ends:
    - P3-CS (a) with the stream-04 bets |lambda| <= 0.4 detects F2 at 35 %; the unstandardized CUSUM at 17.5 %.
    - P3-D windows over 2005-2019 give Gamma^op 191 / 2346 (2008 regime).
    - The literal cross-independence gate fails on D2 (factor 1/10 pairs, full 13/4560).
  - Self-review: three multi-line docstrings in new code against the plan constraint were fixed (AST scan 3 -> 0).
- Investigated Pathways:
  - Anytime-valid readings as e-detectors (GO H2), with the targets of GO H3.
  - Calibration-noise term 1/n_cal in the null regions.
  - Fitting D6 controls on a symmetrization independent of the replicates.
  - Vectorized null checks on stacked D6 blocks: the odd head is flipped, the even head kept, and the Z input is reused.
  - P3-CS (b) computed by `log_dictionary_edetector` on Y = 2 lambda x with eta0 = 0.25.
  - The final review was an author self-review (no subagent, per precedent).

## 3. Current State of the System and Handover

- Current System State: branch `main`; HEAD = `origin/main` = `22b86438d9652cd1851323a3654ce177d7e09a7d` (foreign commit `chore(gitignore): ignore __pycache__ directories and *.pyc files`; before it `611a1b9` stream 09 BAF and `672ce26` stream 10 EUROFIDAI, both pushed by their owners). Stream 07 is implemented and verified but NOT committed at the time of this wrapup.
  - Stream 07 working-tree changes, all to stage:
    - modified: `jepadrift/monitors/streams.py` (+`fraction_stream`), `jepadrift/monitors/eprocess.py` (+`log_average_betting_eprocess`), `experiments/identity_articleB.py` (R15 table, `get_deterministic_seed`, `_write_env_rows`, `--out-r15`; `save_fair_csv` now imported from `jepadrift.pipelines`), `tests/test_identity_articleB.py` (PORTS rows, two R15 tests), `docs/sections/monitors.md`, `docs/DEVIATIONS.md` (7 entries appended), `logs/identity/identity_articleB_venv.log`;
    - new: `jepadrift/pipelines.py`, `jepadrift/monitors/calibration.py`, `tests/test_pipelines.py`, `docs/sections/pipelines.md`, `results/identity/articleB_R15.csv`, `results/pipelines/alarms_P3-C_d2_us97_null.csv`, `results/pipelines/runs_P3-C_d2_us97_null.json`, `logs/pipelines/null_P3-C_d2_us97.log`, `prompts/plans/plan-07.md`, `prompts/GO-stream-07.md`, `prompts/wrapups/wrapup-07.md`.
  - Foreign working-tree changes, NEVER to stage:
    - `configs/eurofidai_schema.yaml` (modified before my `make check`);
    - `data/derived/MANIFEST.json`, `data/derived/d1_etf4/panel.parquet`, `data/derived/d2_us97/panel.parquet` and `results/data/d1_d2_profile.csv`, rewritten by the D1/D2 fixture of `tests/test_data_d1_d2.py` during `make check`, which does NOT restore the committed bytes contrary to the GO note;
    - `docs/manifests/d4_manifest.json` and `logs/d4/`, written by stream 10's tests or instance.
  - Remaining plan steps: (2) `tools/reindex_graphify_jcodemunch.sh`; (3) `make check`, then one commit `feat(pipelines): add P2-C, P3-C, P3-D, P3-CS and P7 pipelines, calibrations and Article B R15 identity` staging exactly the stream 07 files above; (4) range check `origin/main..HEAD` (no `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` path, no file > 50 MB), then `git push origin main`.
  - Ledger: `.superpowers/sdd/plan-07/progress.md` (git-ignored, deleted after the commit). Backups: tarballs in the session scratchpad `backup/`.
- Reference outputs (SHA-256): `articleB_R15.csv` `d78d13e0b0cabfcf3d0a0a90adb0d00956d5f70e7ed49d19d05a6c18b301f7bc`; `alarms_P3-C_d2_us97_null.csv` `0d892104428b1ca484fd99f6c9a2dab7db46483aef5fc0da63d19cd7840f66a0` (3500 rows); `runs_P3-C_d2_us97_null.json` `584bfac54fcfa84438d4b3775c393a14b414cbd42e3c1e4d9600c6e1a2eb6351`; `null_P3-C_d2_us97.log` `481ac9523b63e1bbc48bd187f8b108c00f6f5c45e9d91ef1f76e8176985979d5`; `articleB_R01_R08.csv` `6d37a97a64ba5d2e2c9b06c3b4f0746df81be06219d6782b4d3fd38b7e37bebb` (unchanged).
- Execution Environment:
  - Interpreter: Python 3.12.9; `.venv` built on `~/miniforge3/envs/Trading/bin/python`, each command behind `conda activate Trading` then `source .venv/bin/activate`.
  - `.venv` packages: numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, pyarrow 26.0.0, statsmodels 0.15.0, pytest 9.1.1, pyflakes 4.0.3, PyYAML 6.0.3, yfinance 1.7.0, kaggle 1.6.17 (added by stream 09). The Trading env alone has numpy 1.26.4 and serves Article B diagnostics only.
  - Machine: Linux 5.14.0-570.55.1.el9_6.x86_64, 48 CPUs, 187 GB RAM.
  - Runtime variables: OMP/MKL/OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42 (set by `pipelines.py` before numpy).
  - Article B: checkout `~/The-Whitening-Advantage-Experiments` at `a05f0d9`, read-only.
  - `make check` = `pyflakes $(filter-out jepadrift/stats/garch.py,$(shell find jepadrift experiments tests -name '*.py'))` then `pytest -q --ignore=external`.
- Critical Points of Vigilance:
  - (1) Concurrency: other instances stash, commit and push on the same `main` tree. Re-run `git status` before staging and stage by explicit path only. A foreign `git stash -u` already removed uncommitted work once.
  - (2) `make check` rewrites tracked D1/D2 data files (fixture side effect); never stage them in stream 07.
  - (3) The e-detector null targets are the weak bound H/gamma (GO H3). Sharp checks are the exact per-channel FPR, and ARL0 belongs to E3.
  - (4) The P3-CS (a) randomization null FPR at the fixed seeds (0.0640) sits near the upper end of its region (0.0678).
  - (5) P3-D cannot calibrate a horizon above 941 calib days (`ValueError`): E1's H_det = 2000 needs a decision in stream 12.
  - (6) The mixture option of P3-C raises on D2 (gate fails by design and by multiplicity in full mode).
  - (7) Deferred minors: `_null_block` has an unused parameter `X`; `null_check(reps=0)` raises ZeroDivisionError; the CLI counts P3-C channels on a raw fit while `null_check` fits on a symmetrization (D equal on both datasets); `log_average_betting_eprocess` materializes (J, K, T) per path (about 1.6 GB per chunk in full mode at H = 2000); about a dozen new lines exceed 120 characters.
  - (8) Unknown untracked foreign file `codes_results_v20251231_monde_1_name_9334.csv` appeared at the repo root and was later removed by its owner; it was never staged.

## 4. Inventory of Attachments and Dependencies

### Files [.py]
- **jepadrift/pipelines.py:**
  - *Description:* stream 07 registry and runner; the only module importing both representations and monitors.
  - *Core Functionalities:*
    - constants: `MASTER_SEED = 42`, `H_REF, H_DET, N_CAL, TARGET_FPR = 500, 750, 20000, 0.05`, `B_FLIPS, HALF_LIFE, STAKE_CAP = 2000, 20, 0.5`, `PIVOT_BETS = (0.1, 0.25, 0.5, 0.9)`, `SIGN_DELTA, ENERGY_DELTA = 0.1, 0.5`, `GAMMA = 20.0`, `CHUNK = 64`, `Z99 = 2.5758293035489004`, `COLUMNS`;
    - `COMMON`, `DEFAULTS`, `READINGS` per pipeline (P2-C bootstrap|anytime-valid; P3-C anytime-valid|exact; P3-D bootstrap; P3-CS anytime-valid|randomization; P7 anytime-valid);
    - verbatim ports: `save_fair_csv` (fair harness) and `composition_for` (R15 l.409-426);
    - `split_rows(dates, splits)` -> {pretrain, calib, pre_monitor, dates};
    - `make_spec(pipeline, **kw)` with validation; `run_id(spec)` = 16 hex digits of the SHA-256 of the canonical JSON;
    - `fit_pipeline(spec, X_fit, splits, key=None)` -> state; `run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None)` -> DataFrame (chunks of 64, spawn pool, absorption guard);
    - `sign_diagnostics(eps_K)` (R15 l.889-902); `cross_independence(signs, n_se=3.0)`; `residual_energy(z_even, cols)`; `stakes(norms, sigma_bar)`;
    - `PIPELINES` with `_rep_*`, `_stream_*`, `_detect_*`, `_cal_*` per pipeline;
    - `null_target(spec, state)` -> (p, kind in {"=", "<=", "~"}, n_cal); `summarize(rows, p, kind, n_cal=None)`; `null_specs(pipeline, dataset, n_channels)`;
    - `null_check(specs, X, splits, reps, key)` -> (rows, summary): stacked D6 blocks, seeds `key + [0]`, `key + [1, i]`, `key + [2, i, r]`;
    - `main(argv)`: CLI `--pipeline --dataset --null-check --reps --out --log-dir`; key `[7, crc32("null|P|D")]`.
  - *Inputs:* X (T, N) float64 finite, or a Z dict `{"z_odd", "z_even"}`; splits from `split_rows`; records `{"seed": [int], "tau_star": int, "family": str[, "delta": (N,) or (>= H, N)]}`.
  - *Outputs:* alarms DataFrame/CSV; CLI files `alarms_<P>_<D>_null.csv`, `runs_<P>_<D>_null.json`, `logs/pipelines/null_<P>_<D>.log`.
- **jepadrift/monitors/calibration.py:**
  - *Description:* calibrations (numpy only).
  - *Core Functionalities:* `worker_null_window_real`, `worker_race_h1_real` (R15 l.431-478, verbatim); `bootstrap_threshold(null_maxima, alpha)` = `float(np.quantile(m, 1 - alpha))`; `null_windows(x, length, n, rng, flip=False)` (start, then signs, window by window).
  - *Inputs:* eps_K (K, T); arrays (T, ...); a Generator.
  - *Outputs:* floats, int delays, (n, length, ...) arrays.
- **jepadrift/monitors/streams.py:**
  - *Description:* stream 04 module, plus `fraction_stream(eps)` (R15 l.368-370, AST segment).
  - *Core Functionalities:* `fraction_stream(eps)`.
  - *Inputs:* eps (K, T).
  - *Outputs:* (T,) = mean_k 1{eps > 0} - 1/2.
- **jepadrift/monitors/eprocess.py:**
  - *Description:* stream 04 module, plus `log_average_betting_eprocess(x, lam)`.
  - *Core Functionalities:* log of the mean over bets (J,) and directions of prod(1 + lam_j x_{t,k}).
  - *Inputs:* x (..., T, K) in [-1, 1]; lam 1-D with |lam| < 1.
  - *Outputs:* (..., T) logs.
- **experiments/identity_articleB.py:**
  - *Description:* Article B identity controls (R01, R08, R15).
  - *Core Functionalities:* `get_deterministic_seed` (R15 l.377-394, verbatim); `_r15_rng`; `r15_rows(ks=(5, 10, 20), bootstrap=True, race=True)`; `_write_env_rows(frame, path)`; `main` writes `articleB_R01_R08.csv` and `articleB_R15.csv` and the env log; verdict over d1_loader, R08 and R15 rows.
  - *Inputs:* D1/D2 loaders; Article B CSVs read with round_trip.
  - *Outputs:* identity CSVs (env rows replaced) and `logs/identity/identity_articleB_<env>.log`; about 44 s with R15.
- **tests/test_pipelines.py:**
  - *Description:* 16 tests.
  - *Core Functionalities:* null_windows, bootstrap_threshold, average betting e-process, alarms schema, parallel/partition invariance, X/Z agreement, guards and reset, P2-C worker equality and bootstrap FPR, P3-D energy and Gamma^op, P3-CS stakes and pivot/randomization, D6 null FPR, strong F2 detection, cross-independence gate, CLI smoke.
  - *Inputs:* D2 rows up to 2019-12-31.
  - *Outputs:* none.
- **tests/test_identity_articleB.py:**
  - *Description:* 7 tests.
  - *Core Functionalities:* PORTS extended with `fraction_stream`, the workers, `composition_for`, `get_deterministic_seed`, and `save_fair_csv` now in `pipelines.py`; `test_r15_identity_rng_free`; `test_r15_bootstrap_identity_k5`.
  - *Inputs:* Article B checkout.
  - *Outputs:* none.

### Files [.md, .csv, .json, .log]
- **docs/sections/pipelines.md:**
  - *Description:* registry, readings and guarantees, pipelines, calibrations, R15 identity, reference null check, test diagnostics, deferred items, references.
- **docs/sections/monitors.md:**
  - *Description:* ported-code rows and API lines for stream 07.
- **docs/DEVIATIONS.md:**
  - *Description:* `C-pipe-delay`, `C-pipe-null-targets`, `C-P2C-port`, `C-P3D-windows`, `C-P3CS-design`, `C-P3C-mixture-gate`, `C-identity-R15` appended in French.
- **results/identity/articleB_R15.csv:**
  - *Description:* 56 R15 identity cells, env venv.
- **results/pipelines/alarms_P3-C_d2_us97_null.csv, runs_P3-C_d2_us97_null.json; logs/pipelines/null_P3-C_d2_us97.log:**
  - *Description:* reference null check of P3-C on D2 (7 specs x 500 replicates).
- **prompts/plans/plan-07.md, prompts/GO-stream-07.md:**
  - *Description:* final plan with the integrated GO, and the GO review (decision trace).

## 5. Hypotheses and Conditional Decision Trees

- Missing Variables: none blocking for stream 07. H1-H14 were all confirmed at GO; this section holds downstream trees only.
- Decision Trees:
  - If E1 (stream 12) needs P3-D at H_det = 2000, then choose `null_rows="pre_monitor"` (Gamma^op about 191/2346 on D2) or another horizon or calibration rule, and record it.
  - If a consumer needs several dependent channels in an exact reading, then add a Bonferroni reading (level <= alpha, not exact).
  - If the mixture option is wanted on real data, then the gate needs a multiplicity correction (a specification change).
  - If E5 needs a rank variant of P3-CS, then define the rank pivot and a dispersion proxy for the stake of (b).
  - If E1 runtimes are dominated by the per-day loops (`stakes`, `transform_panel`), then vectorize them (`# ponytail:` ceilings mark the spots).

## 6. Strategic Recommendations for the Next Instance

- Blind Spots:
  - (1) Commit only by explicit path, after a fresh `git status`: foreign files keep appearing in the shared tree.
  - (2) The deferred minors of Section 3 (7) are cheap to close in a fix pass if the researcher approves.
  - (3) Stream 08's contracts should include `alarms.csv` determinism through `pl.main` and the import isolation of `pipelines.py`.
  - (4) E1/E3 should reuse `null_check` (stacked D6 blocks) and pass a `state` fitted on drift-free rows, never `state=None` with injected records.
- Module notes: the kernel referenced by the wrap-up module is not injected in this session (handover written with the module's own skeleton and recorded as a file per AGENTS.md); `ENG_DEWATERMARKING.md` is not injected (no suspension to confirm).
