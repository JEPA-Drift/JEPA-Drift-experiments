2026-10-22

# Wrapup — stream 8b: hygiene (shared modules, side-effect-free fixture, deviation register)

## Context

- Prompt: `prompts/streams/prompt-08b-hygiene.md`, as corrected at `5048a96` (worktree `.gitignore` item). Bootstrap
  prompt: `prompts/amorcage-08b.md`. Worktree `~/JEPA-stream-08b`, branch `stream-08b`, base `5048a96` (fast-forward of
  `main` from `53dbdd3`; the two commits differ in `prompts/` only).
- Plan: `prompts/plans/plan-08b.md` (« Décision GO intégrée »). GO: `prompts/GO-stream-08b.md`, a verbatim transcript of
  the orchestrator's two review rounds and of the GO given through the plan approval screen (2026-10-22).
- Decisions: Q1 = c (root-cause fix in `.gitignore`, no `.git/info/exclude`); Q2 (the audit's own characteristics pivot
  stays out of scope); Q3 (one-off read-only D4 check); Q4 (stop after the commit and the checks: no fetch, push or
  merge); QA (verbatim GO transcript); QB (H1, H9, H10 confirmed); QC (master blocks 19, 22, 25 kept as they are); QD
  (old `.gitignore` lines replaced); H11 (a single Conventional Commit after the refreshed wrapup and a full
  `make check`).
- Environment: every command runs through `.venv` (`.venv/bin/python`, `.venv/bin/pytest`; Trading never activated);
  `make` is `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin/make` (GNU Make 4.4.1) put first on PATH, also for
  `git commit`; direct Python calls pin OMP/MKL/OPENBLAS threads to 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`.

## Validated Results

1. **`jepadrift/stats/drift.py`** (numpy only) holds, moved verbatim from `experiments/audit_information.py`: `WINDOW`,
   `MIN_PHASE`, `BLOCK`, `transitions`, `_sr2`, `debiased_sr2`, `mbb_indices`, `rotate_phases`, and `_ci` exported as
   `shifted_percentile_ci` (only its `def` line changes). The audit imports the nine names (`shifted_percentile_ci as
   _ci`); `tests/test_audit.py` is unchanged (`git diff 5048a96` empty) and green (31 tests).
   - SHA-256 of `ast.get_source_segment` at `5048a96` and in `drift.py` (9/9 identical, frozen in
     `tests/test_drift_stats.py::MOVED_SOURCE_SHA256`): `WINDOW` 0c844c3c…, `BLOCK` 612bf35d…, `MIN_PHASE` d527a363…,
     `transitions` 4708587f…, `_sr2` 1381bb3d…, `debiased_sr2` 1d1e7c51…, `mbb_indices` ff28cd7c…, `_ci` 2008d9bb…,
     `rotate_phases` 2f3d1ae4….
   - Audit AST: the base module body minus the nine nodes equals the new body minus the one
     `from jepadrift.stats.drift import …` node (82 = 82 nodes).
   - `audit_information.py --datasets d2_us97 d3_239 --quick` (outputs, figures and log in the session scratchpad):
     the 9 CSV are identical at the SHA-256 before (122 s) and after (124 s) the move —
     `budget_share` 80ac03d3d9c32f674010fa7d8f7a353152d5508a23b5cb443f3fd861224ff193,
     `channel_ceilings` 235f370e2cd18dc7ddc25d08d192754020eedcb5cc7f8767bb22dac961cfc094,
     `drift_sharpe_transitions` 6ec9e1e0459b873d13bdec63950a5706687ea66e7bd421dc44eb1b3990c72aed,
     `eta_by_year` b3485185d6150011f88b5cf7ca1e9ecc057be3c178a0525ec0bfb9b109f0c53d,
     `placebo_selection` c0fa7dbf1d3cdf3404094e599aaa9eded788fcc164ea0fa038897783d2437832,
     `predicted_gains` ac2568ae6c7136d557c66ff24ee57361cdcbf4c65dcb98a8ac233a831ba615e4,
     `sign_corr` 92560c88c821bd4182b4ca39b8757a666c85e181275199b60c800f66ee5af813,
     `spectrum` ee434bec8acecb19418b470033cd4d3cd40da66c99d8b3fbba5d9589a1dddf51,
     `symmetry_tests` 5d51e35d85b3ea4673faf110a430c286712b1b9d5d21f8ad5d9ebcbaf6074c36.
   - The committed `results/audit/*`, `figures/audit/*` and `logs/audit/audit.log` are untouched.
2. **`jepadrift/data_loader/chars.py`**: `load_chars_tensor(dataset, rows=None) -> (C, names)` reindexes the `c_*`
   columns of `chars.parquet` on `dates.npy[rows] × assets.json` (float64, NaN kept, parquet column order) for `d3_239`,
   `d3_500` and `d4_eurofidai`; `d2_us97` raises `ValueError("D2 has no characteristics")`. `impute_zero(C)` returns
   `(C0, n_imputed)` with the code of `injection.inject`. `tests/test_chars.py`: 5 passed, 1 skipped (D4 absent from the
   worktree); on rows dated before 2020-01-01 only: d3_239 (5,031 pre-2020 days × 239 × 15) aligned on 50 seeded
   (date, asset) pairs, NaN count equal to the parquet's, slices and masks consistent, d3_500 (503 assets) shape,
   and a bit-equal match with the local pivot of `tests/test_injection.py` on the d3_239 calib rows.
3. **D4 one-off check (Q3)**, read-only from `~/JEPA-Drift-experiments/data/derived/d4_eurofidai` replaced in memory,
   nothing written: tensor (6541, 498, 15), NaN preserved (count equal to the parquet's), 50/50 seeded pairs aligned;
   the body of `test_d4_shape` (rows 0..19, 2001) passes against it.
4. **`pipelines.horizon_gamma(H, alpha=TARGET_FPR)`** = H/α, docstring citing P∞(alarm before H) ≤ H/γ;
   `test_horizon_gamma`: γ_H = 15,000 at H = 750, and `null_target` of an anytime-valid P3-C spec at γ_H gives α = 0.05.
5. **Side-effect-free D1/D2 fixture**: the session fixture `rebuilt` (no longer autouse) copies the committed
   `MANIFEST.json` into a `tmp_path_factory` root and runs `ab.build()` with `REPO_ROOT`, `DERIVED`, `RESULTS_DATA` and
   `LOGS_DATA` monkeypatched. The 16 rebuilt files (8 D1, 5 D2, `d1_d2_profile.csv`, `build.log`, `MANIFEST.json`) are
   identical at the SHA-256 to the committed ones, and the `d1_etf4`, `d2_us97`, `d1_d2_profile` and `source` manifest
   entries are equal. `make check` now writes nothing under `data/`, `results/`, `logs/` or `figures/`
   (`find -newer` empty), against the 16 files it rewrote at `5048a96`.
6. **`.gitignore`**: `/.venv` and `/external` replace `.venv/` and `external/`; `git check-ignore -v .venv external` points
   to `.gitignore`; the list of tracked files under an ignore rule is unchanged (16: 9 under `logs/`, 7 under
   `slides/`); the EUROFIDAI paths stay ignored.
7. **`tools/check_prompts.py`** (stdlib) and `make prompts-check`: `prompts-check: 29/29`; `--sync-master` leaves the
   master unchanged (`git diff --exit-code` empty; SHA-256 9ef7f5b09c7fa0918c33d356f99386ddd138cad6783f487d2b5c1735039be8dc).
   A block runs from its `## PROMPT <id> —` title to its closing fence (the last four backticks of a line), the next
   title or the end of file; absent blocks are appended at the end of section 4 in a `markdown` fence.
   `tests/test_check_prompts.py`: 2 passed; `tools/` joins the pyflakes scope of `make check`.
8. **Documents**: `docs/DEVIATIONS.md` ends with `C-D3-survivor-correction` and `C-D4-survivor` (verbatim from the prompt,
   checked as an exact substring) and `C-stats-drift`; `CLAUDE.md` lists `chars`, `drift` and `check_prompts.py`, and the
   sentence on the fixture rewriting the D1/D2 files is removed.
9. **`make check`**: 178 s at `5048a96` (215 passed, 3 skipped); 180 s after the stream (228 passed, 4 skipped: the
   3 EUROFIDAI real-data tests and `test_d4_shape`), under the 5-minute budget, with no file written in the repository.

## Errors and Dead Ends

- The first plan proposed a local `.git/info/exclude` (shared by every worktree of the clone) for the `.venv` and
  `external` links; the orchestrator chose the root-cause fix in `.gitignore`.
- The first plan prefixed every command with `conda activate Trading`; corrected to `.venv` only.
- The scratch segment-hash script crashed on the module-level `os.environ[...] = ...` assignments (subscript targets);
  target names are read with `getattr(..., "id", None)`, as in the frozen test.
- A naive master sync that stops at the first four backticks would cut the inner closing fence of blocks 19, 22 and 25
  (lines of seven backticks) and break idempotence; the closing fence is matched as four backticks at the end of a line.
- The first version of `tests/test_chars.py` read rows dated after 2019 (full d3_239 tensor, last 250 days of d3_500,
  last 20 days of D4), against the pre-J4 rule that tests never read such rows; the tests now use rows dated before
  2020-01-01 only. The one-off D4 check (item 3) read all D4 dates for metadata only (shape, NaN counts, alignment).
- The Graphify MCP server did not connect in this session; jCodeMunch and the CLIs served.

## Current State

- Single commit on `stream-08b` over `5048a96`, not pushed (Q4); hash reported in the handover.
- Created: `jepadrift/stats/drift.py`, `jepadrift/data_loader/chars.py`, `tools/check_prompts.py`,
  `tests/test_drift_stats.py`, `tests/test_chars.py`, `tests/test_check_prompts.py`, `prompts/plans/plan-08b.md`,
  `prompts/GO-stream-08b.md`, this wrapup.
- Modified: `.gitignore`, `experiments/audit_information.py`, `jepadrift/pipelines.py`, `tests/test_pipelines.py`,
  `tests/test_data_d1_d2.py`, `Makefile`, `docs/DEVIATIONS.md`, `CLAUDE.md`.
- Unchanged and checked: `tests/test_audit.py`, `tests/test_injection.py`, `jepadrift/monitors/`,
  `jepadrift/injection.py`, the loaders, the stream prompts and `prompts/Prompts_Claude_Code_v5.md`.

## Vigilance Points

- `transitions` stays bound to `WINDOW` (2005-01-01 to 2019-12-31) and `mbb_indices` to `BLOCK = 20`: a post-J4
  consumer (E8) needs parameters, which changes the frozen segment hashes by design (update `MOVED_SOURCE_SHA256` and
  record a deviation).
- The audit keeps its own characteristics pivot (Q2): a third copy remains until a later stream moves it.
- `data/derived/d4_eurofidai/` keeps the trailing-slash limit: a symbolic link of that name would be neither ignored
  nor blocked by the pre-commit path check.
- `tests/test_chars.py` imports two helpers from `tests/test_injection.py`, the first import between test modules; it
  relies on pytest's prepend import mode, which puts `tests/` on `sys.path`.
- Master blocks 19, 22 and 25 still end with lines of seven backticks (their stream files lack a final newline, QC).
- `.venv/bin/make` points to `envs/jepa-make`; commits must put the conda-forge `make` first on PATH, since the hook
  runs `make check`.

## Recommendations

- Orchestrator: audit the commit, then run the end-of-stream push (`git fetch origin`, rebase on `origin/main`,
  range check, `git push origin stream-08b:main`) and fast-forward `main`; then check that `chars.py`, `drift.py` and
  `check_prompts.py` exist before opening streams 12, 13, 14, 17 and 18.
- E1, E3, IPCA and CA-T-JEPA: take F2 characteristics from `chars.load_chars_tensor` (+ `impute_zero`), drift statistics
  and phase placebos from `stats.drift`, and γ_H from `pipelines.horizon_gamma`, rather than local copies.
- Keep `make prompts-check` at 29/29 whenever a stream prompt changes (`--sync-master`, then review the master diff).
