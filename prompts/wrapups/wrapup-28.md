`````````````markdown
2026-10-30 21:00:21 UTC

2026-10-30

# Wrapup — stream 28 (28-PCA): PCA drift benchmark runner, predictive rank amendment (schema /2)

## Context

**Inputs**
- Prompt: `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`. Its title is now `## PROMPT 28-PCA — …`; only line 1
  changed, and E11 (`prompt-28-e11.md`) is untouched.
- Plan `prompts/plans/plan-28.md` (plan v2 with the integrated GO) and Codex GO `prompts/GO-stream-28.md`.
- NO-GO trace `prompts/NO-GO-stream-28.md`.
- Researcher amendment `prompts/GO-stream-28-amendment-P0-P1.md`. It takes priority over the plan's
  floor(alpha n) rule.

**Repository.** Worktree `JEPA-stream-28`, branch `stream-28`, base `e1f80847245b14498e331abda1e3d13cf415ec8f`. HEAD
is unchanged; nothing was committed.

**Sessions**
- Phase B, first session: the runner, configuration, schema and 41 tests were written test-first in groups g1–g3,
  and smoke `/1` ran. The session ended on quota.
- Targeted resumption at 2026-10-30 18:52 UTC: P0 (predictive exchangeable rank, schema `/2`) with its own tests and
  trace, then P1 (measured corrections). After that came the documentation and a new double smoke in fresh
  directories.
- Closeout session at 2026-10-30 20:08 UTC (Mistral Vibe, authorized by `prompts/GO-stream-28-closeout-vibe.md`,
  executing `prompts/plans/plan-28-closeout.md` after the Codex review `docs/audits/stream-28-codex-review.md`):
  the two established defects were corrected test-first (T0–T6), and a new double smoke ran in fresh closeout
  directories. Trace `logs/pca_drift_benchmark/closeout_fixes.log` (SHA-256 `1bf6cd25…275d7c`), diff
  `logs/pca_drift_benchmark/closeout.diff` (SHA-256 `7bbdd71f…0a94a`).

**Scope**
- Synthetic smoke only, with N = 239, H = 250, n_center = n_cal = n_null = n_alt = 40, alpha = 0.05, two backgrounds
  (Gaussian and t7 equicorrelated) and scenarios A, B30 and C.
- Not done: no full run, no real return read after 2019-12-31, no `make check`, no reindexation, no Git operation.

**Environment.** Shared `.venv` (Python 3.12.9, NumPy 2.4.4, pandas 3.0.6, SciPy 1.17.1) with the thread variables
at 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and `MPLBACKEND=Agg`.

**Formal Codex checkpoint.** The installed `$wrap-up` skill (`~/.agents/skills/wrap-up/SKILL.md`) was
explicitly invoked for this canonical precommit handover refresh. Existing state, environment, hashes and artifact
inventories are retained; the fresh verification below supplements the producer's historical observations.

**Actual Vibe execution export.** Mistral Vibe 3.0.4, model `mistral-large-4`, CLI alias `large-4`, provider `mistral`,
thinking `high`; outcome `finished`, exit 0. The closeout producer finished at 2026-10-30 20:17 UTC; completion
marker `logs/pca_drift_orchestration/vibe_closeout/status_done`. Claude remains plan-only. Codex owns review and
serial integration.

## Validated Results

**Tests**
- `python -m pytest -q tests/test_pca_drift_benchmark.py`: **50 passed** (7.9 s after the closeout; 48 before).
  `pyflakes` (4.0.3) is clean on the runner and the test file.
- Targeted repository checks: `tests/test_check_prompts.py` and `tests/test_decoupling.py` give 8 passed.
  `python tools/check_prompts.py`, in check mode, gives 29/29. (Run before the closeout; Codex re-runs them.)

**Codex fresh verification at this checkpoint (reported by the parent orchestration instance)**
- Stream tests: **50 passed in 7.95 s**; fresh `pyflakes` exit 0.
- All seven closeout files are byte-identical to the repeat: `manifest.json`, `spectra.csv`, `selection.csv`,
  `calibration.csv`, `trials.csv`, `aggregates.csv` and `issues.csv`.
- The current code, configuration, environment and input identity was recomputed through `identity_block` and
  matches the producer fingerprint exactly:
  `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.
- E2 was rechecked on disk and in the index: SHA-256
  `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, CRLF preserved. Historical E3/D8 remains
  FAIL; it has not been reinterpreted as a pass.
- Independent read-only closeout review: **Ready, no blocking findings**. The floating batch-size defect and
  mixed schema metadata are corrected without a scientific change.
- These fresh checks do not include final global `make check`, the required AST-only/no-AI reindexation, commit,
  push or the main-worktree fast-forward. Every one of those operations is still pending.

**P0 — predictive exchangeable rank.** Trace `logs/pca_drift_benchmark/p0_predictive_rank.log`; diff
`logs/pca_drift_benchmark/p0.diff` (SHA-256 `5060a6d856a5c7f1f3fdd2eed2d994edab88e4acce69fe1ef7e7512d155ce16f`).
- RED at 18:58:57Z: 4 failed for the expected reasons (no `predictive_rank`, schema still /1, no `guarantee_basis`,
  no failure path). GREEN at 19:02:26Z: 4 passed, and the whole file 44 passed.
- Rule: r = floor(alpha (n + 1)) - 1, with exact decimal alpha.
  - r < 0 raises `InsufficientCalibration`: status CALIBRATION_FAILED, no threshold, an explanatory issue. At
    alpha = 0.05, at least 19 maxima are needed.
  - Otherwise b = sorted(maxima)[n - r - 1]. The GT threshold is b; the GE threshold is a single nextafter step.
- Unit checks: n = 40 gives r = 1 and bound 2/41; n = 2,000 gives r = 99 and bound 100/2001 (deterministic maxima,
  no full run); n = 1, 5 and 18 fail; ties, GE/GT, a non-finite GE threshold and invalid inputs are covered.
- Pipeline checks:
  - Synthetic rows carry `guarantee_basis` EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA and `predictive_bound` =
    (rank_r + 1)/(n_cal + 1).
  - Real D6 rows carry NOT_ESTABLISHED_HISTORICAL_WINDOWS with `predictive_bound` NA, and real-path rows have no FPR.
  - The `null_calibration_id` recipe, recomputed from the CSV, uses `predictive_exchangeable_rank_v2`.
  - An insufficient n_cal = 8 gives CALIBRATION_FAILED rows with NA metrics and no trials.
- Test fixtures adapted without changing alpha: `tiny_cfg` n_cal 8 → 19 and the fake real n_null 6 → 19. The
  former floor(alpha n) unit test was replaced; its n = 5 case at alpha = 0.05 now expects CALIBRATION_FAILED.

**P1 — measured corrections.** Trace `logs/pca_drift_benchmark/p1_measured_corrections.log`; diff
`logs/pca_drift_benchmark/p1.diff` (SHA-256 `075b8769ccf5f22be9da485c4f020f4523228cd3aed628f91ed2caef1699f2eb`).
- RED at 19:05:24Z: 4 failed. GREEN at 19:07:54Z: 48 passed, after the one test adaptation described under Errors
  and Dead Ends.
- (1) `mixture_cost`: same equation and brentq.
  - The bracket is found by doubling, capped at `MIXTURE_MAX_DOUBLINGS` = 200.
  - Parameters (integer 1 <= d < 2^53, finite gamma > 1), bounds and evaluations are checked finite, and a missing
    bracket raises an explicit `ArithmeticError`.
  - For valid inputs the bracket sequence is unchanged.
- (2) Dimensions: `vech_stream` checks that the centering is (d, d) and that the stream has d(d+1)/2 coordinates.
  `_scan` refuses a stream whose dimension differs from the p used in s2, and the scan infers p from the last axis.
- (3) Exhaustive search:
  - (batch, d, d) extractions with batched solve/slogdet.
  - Batch size at most min(chunk, 20,000, available bytes / (6 x 8 d^2)); a chunk outside [1, 20,000] is refused.
  - Each subset is evaluated once and reused for every k: 63 evaluations for nmax = 6.
  - `check(stage)` runs before every batch, including within one d, and checks the wall clock and the peak RSS; an
    overrun is BLOCKED_RESOURCE.
  - Results are identical for chunks 1, 2, 7, 20, 64 and 20,000.
- (4) RNG: `seed_plan` runs before any draw and before any directory is created.
  - The CRC32 label codes must be distinct on the run's vocabulary. The collision "plumless"/"buckeroo" is refused.
  - Canonical entropies must be unique (uint32 words zero-padded to 4).
  - The seed must lie in [0, 2^32).
  - The keys drawn during a run equal the plan, each drawn exactly once (324 keys in the smoke).

**Smoke /2, double run in fresh directories**
- Primary run `--out results/pca_drift_benchmark/smoke_predictive_v2 --log-dir logs/pca_drift_benchmark/smoke_predictive_v2`:
  exit 0, wall 37.21 s, user 36.07 s, max RSS 322,068 KiB.
- Repeat run `--out logs/pca_drift_benchmark/smoke_predictive_v2_repeat/out --log-dir .../log`: exit 0, wall
  37.28 s, user 36.13 s, max RSS 322,824 KiB.
- Each run computed 358 partitions and 9,807,679,440 scan units in 21.9 s (4.48e8 units/s), with 11.9 s of
  covariance search and centering.
- `cmp` reports all seven files byte-identical. `identity` is equal; `run_fingerprint` =
  `b929d26b6884a085ac5df7568eb33a356becab0406ef3d8730a86772b4f53dcd`.
- SHA-256 of `results/pca_drift_benchmark/smoke_predictive_v2/`:

| file | SHA-256 |
|---|---|
| manifest.json | `45afe273f400c5a48aa8b29d49304c74e628f3547aa9340e2fe4fe63cbe25768` |
| spectra.csv | `c8ce52eb499658b8d9d8d093e07473ccd3df664e823f7309112d6b2a42759f3e` |
| selection.csv | `d4d1286de4f48813d886540c1f8e5578ec956d77d7d73c5ad401d243bd15d8eb` |
| calibration.csv | `c6dd73cd69f90467347d23f03f63cfd53dc460c0126c4568f396ef339d4ee3ab` |
| trials.csv | `56e6d98fd0fdcbf12c817e25a0de8fd06a1e4a1f487e58cc4c054c543356e5ff` |
| aggregates.csv | `fed8ef9cfcdc49bf0b8d94e9c35c8bb4289888c99258f4783ab6f952da2e1984` |
| issues.csv | `4d6f5b99e169a371c49a46f6a7fe0f27c8d2c480833c68a1a948d4d56605159f` |

**Smoke /2 content**
- 106 calibrations, all with status OK, n_cal = 40, rank_r = 1, predictive_bound = 2/41 = 0.04878048780487805, and
  an empirical calibration fraction of 1/40.
- The observed holdout FPR over 106 rows of n = 40 has mean 0.039 and range 0–0.15. It is descriptive only, since
  the rows share paths and n is small, and it supports no FPR or RMST claim.
- No `/home/` string appears in the outputs.
- Re-running into the primary directory is refused (exit 2) and creates no directory. No file exceeds 50 MB.

**Smoke /1 (pre-amendment)**
- `results/pca_drift_benchmark/smoke/`, with its log and 358 partitions, is kept byte for byte: the SHA-256 listing
  digest is `9492e1dd…0632`, before and after.
- It is not P0 evidence.

**Closeout fixes (2026-10-30, Vibe session authorized by `prompts/GO-stream-28-closeout-vibe.md`)**
- Défaut 1 (floating memory budget). RED: `test_p1_exhaustive_cov_floating_memory_budget` reproduced
  `TypeError: 'float' object cannot be interpreted as an integer` at `exhaustive_cov` line 540 with C0 = I6,
  C1 = diag(1..6), chunk = 20000, `mem_bytes = 3.0 * cov_batch_bytes(6) = 5184.0`. GREEN: `size` is now
  `min(chunk, int(mem_bytes // cov_batch_bytes(d)))`; a non-finite `mem_bytes` (NaN, ±inf) raises ValueError before
  the loop; `validate_config` requires finite resource limits. The test checks exact equality with the
  no-budget reference, the analytic optimum S(k,d) = axes k−d..k−1 with I = sum 0.5 (r − 1 − ln r) (rel 1e-12),
  63 batched evaluations each at most floor(5184 / cov_batch_bytes(d)), one `check` per batch, ResourceBlocked
  without any KL call at `mem_bytes = cov_batch_bytes(1) − 0.5`, and the production path through a `Store` with a
  floating `mem_limit` and monkeypatched `peak_rss_bytes` (`available_bytes() == 5184.0`).
- Défaut 2 (mixed schema metadata). RED: the YAML still declared `pca_drift_benchmark/1`. GREEN:
  `configs/pca_drift_benchmark.yaml` line 1 is now `/2`, and `validate_config` refuses any other
  `schema_version`. The test checks smoke and full configs, the refusal of `/1` and of infinite/NaN resource
  limits, `/2` at the manifest root, in `identity` and in `config`, and `/2` in the `schema_version` column of
  every CSV that carries it (`trials.csv` has no such column by schema design).
- Full suite after both fixes: **50 passed in 7.90 s**; `pyflakes` clean. No detector, threshold, KL or calibration
  rule was touched.

**Double smoke closeout, fresh directories**
- Primary `--out results/pca_drift_benchmark/smoke_predictive_v2_closeout --log-dir
  logs/pca_drift_benchmark/smoke_predictive_v2_closeout`: exit 0, wall 37.33 s, user 36.13 s, sys 1.03 s, 99% CPU,
  max RSS 324,596 KiB (`smoke_predictive_v2_closeout.time.log`).
- Repeat `--out logs/pca_drift_benchmark/smoke_predictive_v2_closeout_repeat/out --log-dir .../log`: exit 0, wall
  37.18 s, user 36.04 s, sys 0.97 s, 99% CPU, max RSS 322,404 KiB (`smoke_predictive_v2_closeout_repeat.time.log`).
- `cmp`: all seven files byte-identical between primary and repeat; `identity` equal; `run_fingerprint` =
  `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.
- Schema `/2` homogeneous: manifest root, `identity`, `config`, and the `schema_version` cell of every CSV that
  has the column.
- SHA-256 of `results/pca_drift_benchmark/smoke_predictive_v2_closeout/`:

| file | SHA-256 |
|---|---|
| manifest.json | `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9` |
| spectra.csv | `3718ed94123c0dad17505657383a1722d3e42d1f482b78b0d36f7efb28ca5e17` |
| selection.csv | `f7b8406c7a73e0a19c905e9ef1104820b32d398269eecd6c40683c399f76655f` |
| calibration.csv | `04d463b42556dfcd784ef4833c9f4cec789f194cb436c093ce8c25b370c4378d` |
| trials.csv | `3dcf83a82685a014fafef213358305239866eaf0851ffcc525cdbe6c455aa7be` |
| aggregates.csv | `6bd41250db9059abd19f4ec0976c8976fc54204e4321d66ad1b3a409c46e2f07` |
| issues.csv | `d7a276f9a52e5ed798e7f0e59a8b73d5a36e1478dd7d4754618d4ded2ce72caf` |

- Re-running into the primary directory is refused (exit 2, "holds a completed run") and creates nothing. No file
  exceeds 50 MB (max `selection.csv`, 2,030,235 bytes); no `/home/` path appears in the outputs.
- Descriptive comparison with the pre-fix `smoke_predictive_v2/` (non-identifying values, as measured): same row
  counts (478/2422/106/14320/387/10) and columns; `trials.csv` detected mean 0.336592 in both (per role:
  alternative 0.778596, calibration 0.025, holdout_null 0.039387); `stat_max` mean 0.811854 in both. The fixes
  change no computed value on the default path.
- Preservation: the T0 listing digests of `smoke/` (/1), `smoke_predictive_v2/`, `smoke_predictive_v2_repeat/` and
  all partitions are identical before and after the closeout (`9492e1dd…`, `594092da…`, `4ea477df…`, `146da691…`,
  `889ed666…`). The old `/2` manifest is untouched: SHA-256 `45afe273…25768`, `config.schema_version` still `/1`
  (pre-fix artifact, never edited by hand). No `--resume` was used with a modified fingerprint.

**Invariants**
- E2 `results/e2/e2_cells.csv` has SHA-256 `e315e537…570823` on disk and in the index, 47 CRLF lines, `text` unset,
  and no diff.
- `docs/DEVIATIONS.md` is append-only (prefix identical). Its D8 line "relative gap +0.0528334213 > 0.05" is
  present.
- `configs/FROZEN.json` is absent, and no EUROFIDAI path appears.

**Final file hashes**

| file | SHA-256 |
|---|---|
| runner | `8324b47b…c0b373` (closeout) |
| tests | `7d5bdbc2…973da` (closeout) |
| config | `79d2b5e5…473e99` (closeout: `/2`) |
| schema document | `adae1ad1…d9484` (closeout) |
| DEVIATIONS | `64874e64…b666f` |
| prompt 28 | `1dec0fc0…ec11b` |

**Full budget, extrapolated and not run**
- Synthetic part: 4.9e11 scan units (same early-stop profile) to 7.1e11 (no early stop).
- Time: 20.7–28.9 min wall in one process with one thread, plus at most 2.9e10 units (about 1.1 min) for the real
  pre-2020 D6 calibrations.
- Memory: the array-only theoretical peak (`memory_estimate`) is 1.03 GiB. Trial-row dicts are not counted, so the
  expected peak RSS is about 1.5–2.5 GiB, under 8 GiB.
- `trials.csv`: about 716,000 rows (about 45 MiB) synthetic; real calibrations add up to 84,000 rows (about 5 MiB).

## Errors and Dead Ends

**Smoke /1**
- Smoke `/1` (14:25 UTC) used the revoked floor(alpha n) rule. Under that rule n = 40 gives r = 2, and the
  exchangeable exceedance (r + 1)/(n + 1) = 3/41 = 0.073 exceeds alpha; at n = 2,000 it is 101/2001 = 0.0505. P0
  replaces the rule.
- Smoke `/1` also preceded the schema document, which the GO wanted before execution, and four small post-smoke
  cleanups:
  - energy comparator `claim_flag` NONE;
  - `full_counts` instead of a hard-coded 2000;
  - PreJ4Refused mapped to exit 2;
  - explicit module import for code hashing.
- Its artifacts therefore match neither the pre-P0 snapshot nor the final code. They are kept only as a
  pre-amendment record.

**Fixes during the work**
- First session: a scan edge-case test differed by 1 ulp between `math.log1p` and `np.log1p`; the test reference was
  fixed and the kernel left unchanged. An overflow warning from `nextafter(DBL_MAX)` is silenced with `np.errstate`.
- P1: once checks ran between every covariance-search batch, `test_g3_blocked_resource_then_resume_is_byte_identical`
  blocked inside the search before any partition (0 partitions).
  - The test now uses a 1.0-min tick budget instead of 0.2 min.
  - It also asserts that a 0.1-min budget stops between search batches with 0 partitions.
  - No runner statistic changed.

**Finding.** `SeedSequence([x])` equals `SeedSequence([x, 0])`, since the pool pads to 4 words. Raw entropy tuples are
therefore not a valid uniqueness test, and canonical zero-padded words are used.

**Tooling.** `apply_patch` is not available in this harness. Edits used the Edit tool or scripted exact replacements,
each asserting a unique match. The P0 and P1 diffs come from snapshots taken before each phase; the closeout diff
comes from exact reverse replacements of the four edited files (they are untracked, so `git diff` has no base).

**Closeout defects (Codex review, fixed by the Vibe closeout session)**
- `exhaustive_cov` computed `size = min(chunk, mem_bytes // cov_batch_bytes(d))`; with a float `mem_bytes`
  (production `Run.available_bytes()` is a float) and a binding memory ceiling, `range(..., size)` raised
  `TypeError: 'float' object cannot be interpreted as an integer`. It could only interrupt a run, never change a
  value; the existing reduced-memory test passed an integer and missed the path.
- `configs/pca_drift_benchmark.yaml` still declared `/1` while code and identity announced `/2`, so the `/2`
  manifest carried mixed metadata (`config.schema_version` `/1`). Fixed at the source (YAML + `validate_config`
  refusal); no generated artifact was edited by hand.

## Current State

**Codex indexing follow-up.** The first required Graphify AST + jCodeMunch pass completed with exit 0 and AI
summaries disabled. The later document refresh completed Graphify, but jCodeMunch returned the local/Git identity
ambiguity described in the closeout plan. No index was invalidated. The scientific source had already been
indexed in the successful pass; the last delivery-note refresh is recorded as blocked, not passed. Global
pre-commit make check and Git delivery still follow this checkpoint.

**Working tree** (from `git status`)
- Modified: `docs/DEVIATIONS.md` (three new `C-pca-*` entries, in French), `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`
  (line 1).
- Untracked, stream files: `configs/pca_drift_benchmark.yaml`, `docs/sections/pca_drift_benchmark.md`,
  `experiments/pca_drift_benchmark.py`, `tests/test_pca_drift_benchmark.py`, `prompts/wrapups/wrapup-28.md`.
- Untracked, smoke outputs: `results/pca_drift_benchmark/smoke/` (/1), `results/pca_drift_benchmark/smoke_predictive_v2/`
  (/2 pre-fix) and `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` (/2 candidate evidence).
- Untracked, Codex files: `prompts/GO-stream-28.md`, `prompts/GO-stream-28-amendment-P0-P1.md`, `prompts/NO-GO-stream-28.md`,
  `prompts/plans/plan-28.md`, plus the closeout files `prompts/GO-stream-28-closeout-vibe.md`,
  `prompts/GO-stream-28-closeout-plan.md`, `prompts/IMPLEMENT-stream-28-closeout-vibe.md`,
  `prompts/plans/plan-28-closeout.md`, `docs/audits/stream-28-codex-review.md`.
- Logs in `logs/pca_drift_benchmark/`: `tdd.log`, `checks.log`, `commands.log`; the P0 and P1 traces and diffs; the
  closeout trace `closeout_fixes.log` and `closeout.diff`; time and stdout logs of the five smokes; run directories
  `smoke/`, `smoke_predictive_v2/`, `smoke_predictive_v2_repeat/`, `smoke_predictive_v2_closeout/` and
  `smoke_predictive_v2_closeout_repeat/` (partitions included).

**Schema.** `pca_drift_benchmark/2` is documented and implemented, and now homogeneous in the closeout outputs
(root, identity, config, CSV cells). It is not sealed: sealing belongs to Codex and the researcher after the audit.

**Real cohorts.** Both are present in every run and blocked: COVID_2020 standard is NOT_EVALUABLE_STANDARD_SPLIT; the
standard 2022 event and the retrospective Covid cohort are BLOCKED_PRE_J4. Every metric is NA.

**Blockers left for Codex or the researcher**
- Full-run authorization.
- J4 / `FROZEN.json` (stream 21) for any real evaluation.
- `make check`, reindexation, commit and push.

**Checkpoint status clarification.** The historical working-tree inventory above is retained as the producer's
state record; this documentation refresh ran no Git or index command. The historical tooling paragraph describes
the producer harness; this Codex refresh uses `apply_patch` on this canonical wrapup only. Fresh stream tests,
pyflakes, byte identity, identity recomputation and E2/E3 checks are now recorded above. Final global `make check`,
AST-only/no-AI reindexation, commit/push and the main-worktree fast-forward remain pending. The parent must execute
the remaining project gates serially, with all stream execution processes stopped; this checkpoint is not an
integration or schema-sealing claim.

## Vigilance Points

**Smoke readings**
- Holdout FPR at n = 40 is noisy and computed on shared paths. Neither it nor any RMST supports a claim; only the
  calibration rule and the reproducibility are validated.
- B30 is very strong: I_cov_joint(P_20) is about 19.8 nats/day. Covariance comparisons saturate except S = {1}. The
  index-energy comparator cannot alarm (index variance decreases), which is the designed counterexample.
- CPV90 lies outside the 20 candidate axes for both synthetic backgrounds (k90 = 158 and 152), so the BASELINE_CPV90
  rows are NOT_COMPARABLE_OUTSIDE_TOP20.
- In scenario C, k < 10 gives ties (zero information, `tie_broken`).

**Guarantee scope.** The predictive bound is marginal and holds only for exchangeable synthetic maxima. It is not
claimed for D6 windows or a real path, and `anytime_valid` stays False.

**Artifact generations.** Three smoke generations coexist: `smoke/` (/1, pre-amendment), `smoke_predictive_v2/`
(/2 but pre-closeout: its manifest keeps `config.schema_version` /1 — labelled, never edited, not sealed
evidence), and `smoke_predictive_v2_closeout/` + repeat (/2 homogeneous, candidate evidence with fingerprint
`9926b665…7443`).

**Full run**
- The wall estimate, 21–29 min plus about 1 min, is close to the 30-min per-invocation limit. A BLOCKED_RESOURCE
  followed by `--resume` may be needed; the partitions make the resumed run byte-identical.
- The memory guard counts arrays only.
- With the real part, `trials.csv` may exceed 50 MB (issue TRIALS_LOCAL_ONLY: keep it local).

**Platform.** `peak_rss_bytes` relies on Linux `ru_maxrss` in KiB.

**Seed plan.** CRC32 injectivity is checked only on each run's finite vocabulary (cohort labels only in real runs).
No universal property is claimed.

## Recommendations

**Delivery selection.** Publish only the homogeneous closeout evidence under
`results/pca_drift_benchmark/smoke_predictive_v2_closeout/`. The old `smoke/` and `smoke_predictive_v2/`
generations, repeats, partitions and CLI exports remain local archives in the preserved stream-28 worktree;
they are not staged, and the old generations are excluded locally. No archive is overwritten or deleted.
The reindex wrapper now explicitly passes `--no-ai-summaries` to jCodeMunch; Graphify uses AST-only `update`.

- Codex:
  - Audit P0 and P1 separately through `p0.diff` and `p1.diff` and their RED/GREEN traces, and the closeout through
    `closeout.diff` (limited to `exhaustive_cov`, `validate_config`, YAML line 1, tests and the schema document) and
    `closeout_fixes.log` (T0–T6 with the verbatim RED TypeError).
  - Re-run the targeted checks (`tests/test_check_prompts.py`, `tests/test_decoupling.py`, `tools/check_prompts.py`),
    the stream tests (50 passed) and `make check`.
  - Verify on the closeout outputs: `/2` homogeneous (root, identity, config, CSV cells), seven files byte-identical
    primary/repeat, refusal of a re-run (exit 2), no file over 50 MB, E2 `e315e537…570823` disk and index with
    i/crlf w/crlf -text, E3 D8 FAIL unchanged with `git diff --quiet -- results/e3`.
  - Commit scope: exclude `logs/pca_drift_benchmark/*/partitions/` and the repeat output directory (duplicates of the
    primary smoke). Keep `run.log`, the time logs, the traces and the diffs. Decide whether smoke `/1` and the
    pre-fix `smoke_predictive_v2/` are committed as labelled pre-closeout records or left local.
  - `logs/` is gitignored (`.gitignore:9`; earlier streams force-added selected logs). The P0, P1 and closeout traces
    and diffs therefore enter the history only through an explicit `git add -f` by path.
- After the audit, seal schema `/2` and authorize the full run in two steps:
  - `--mode full --dataset synthetic` (about 21–29 min, 1 thread);
  - then `--dataset both`, which adds about 1 min of pre-2020 real calibration.
  - Keep `--resume` available for a 30-min block.
- Before any real evaluation, J4 requires `configs/FROZEN.json` (stream 21). The retrospective Covid cohort remains
  exploratory (`C-pca-covid-retrospective`).

**[Strategic Advice]** The original recommendations remain as the producer's transfer record. The fresh stream
tests, pyflakes, seven-file comparison, identity recomputation and E2/E3 checks have now been completed by the
parent. Finish the remaining gates serially after stream processes are off: required AST-only/no-AI reindexation,
final global `make check`, explicit staging and staged review, commit/push under the project's Git rules, and the
main-worktree fast-forward. Re-run `make check` if rebase changes the base. No full run or real post-2019 evaluation
is authorized by this handover; streams 29, 30 and 31 remain gated on effective completion of stream 28.

**Protocol context.** The LIGHT kernel was not injected; the installed skill's standalone checkpoint rules apply
with the project's six headings. `ENG_DEWATERMARKING.md` was not injected.
`````````````
