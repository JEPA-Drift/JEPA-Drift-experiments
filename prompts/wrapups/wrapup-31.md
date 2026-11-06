# Wrapup — stream 31, lot 1: prompt tooling (`tools/check_prompts.py`)

## Context

- **History.** Stream 31 (PCA benchmark scientific contracts) resumed on 2026-11-06 under Codex supervision. Plan v1 received a NO-GO (`prompts/NO-GO-stream-31.md`). Plan v2 received a GO for **lot 1 only** (`prompts/GO-stream-31-tooling.md`); the canonical plan is `prompts/plans/plan-31.md` (section 8, "Décision GO intégrée"). Base: `a0c576e13e8e647dfd61350eec52058ffc794dbf`.
- **Lot 1 scope.**
  - `tools/check_prompts.py` discovers the 29 historical `prompts/streams/prompt-*.md` and the 4 canonical `prompts/streams/[0-9][0-9]_STREAM_PCA_DRIFT_*.md` prompts (ids `28-PCA`, `29`, `30`, `31`).
  - The master `prompts/Prompts_Claude_Code_v5.md` receives their 4 blocks append-only, and `--sync-master` is idempotent.
  - The normal check refuses a truncated master, a missing or modified expected file, a duplicate title, and an incomplete or unexpected id set. It applies no line-ending normalization.
- **Out of scope (no GO).** Lot 2 QA (`tests/test_pca_drift_contracts.py`), PCA producers, figures, the D7b diagnosis, Git and reindexing.
- **Execution.** One interactive session, no sub-agent. TDD RED→GREEN.

## Validated Results

Commands ran from the worktree root with
`export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`
(Python 3.12.9, GNU Make 4.4.1 from `.venv/bin`).

**RED, before any tool change.** `.venv/bin/python -m pytest -q -rf tests/test_check_prompts.py` exited 1: 7 failed, 2 passed (the two pre-existing tests), pytest 0.20 s.
- T1, T2, T5, T6 and T7 failed on missing features (`discover`, `prompt_ids`, `EXPECTED_IDS`).
- T3: a synthetic master with an unfenced final block gave 129 ≠ 143 characters after a second sync.
- T4: the real master gave **184 875 ≠ 184 889** characters after a second sync. The unfenced final block 8b absorbed the next `\n\n````markdown`, 14 characters.
- The pre-check of the 29 historical blocks (exact span equality) passed. The master SHA-256 was unchanged by RED.

**GREEN.** The same command exited 0 with 9 passed (pytest 0.09 s); `.venv/bin/pyflakes tools/check_prompts.py tests/test_check_prompts.py` printed nothing. After re-wrapping three lines longer than 120 characters: 9 passed.

**Self-review witness, RED2 then GREEN3.**
- *Finding.* On a master whose final closing fence was lost, `main()` printed a `4/4` ratio line before the imbalance note, although it exited 1.
- *RED2.* T7 was extended with that case (exit 1, explicit error, no ratio line, refused `--sync-master` with no write) and gave 1 failed, 8 passed.
- *Fix.* A fence imbalance is now raised as an explicit error inside the validation block, before any ratio line.
- *GREEN3.* 9 passed, pyflakes silent.

**Pre-migration check (expected failure, captured).** `.venv/bin/python tools/check_prompts.py` exited 1 and printed `prompts-check: 29/33 (29 prompt-*.md + 4 [0-9][0-9]_STREAM_PCA_DRIFT_*.md: 28-PCA, 29, 30, 31)`, listing the 4 PCA prompts as not in the master. The master was unchanged.

**Migration.**
- *First sync.* `.venv/bin/python tools/check_prompts.py --sync-master` printed `sync-master: master rewritten` and `prompts-check: 33/33 (29 prompt-*.md + 4 [0-9][0-9]_STREAM_PCA_DRIFT_*.md: 28-PCA, 29, 30, 31)`.
- *Append-only.* `cmp` of `git show HEAD:prompts/Prompts_Claude_Code_v5.md` against the first 139 933 bytes of the new master found them identical. The 29 historical blocks and every pre-existing byte are unchanged.
- *Idempotence.* A second `--sync-master` printed `sync-master: master unchanged` and the bytes stayed identical.
- *Structure.* The master blocks equal `EXPECTED_IDS` (33 ids), the fences balance at 32/32, and ids `28` (Electricity) and `28-PCA` are distinct.
- *Make target.* `.venv/bin/make prompts-check` exited 0 with 33/33. After GREEN3, a third `--sync-master` still printed `unchanged`.

**Full suite.** `.venv/bin/make check` exited 0 in 488 s wall-clock (log `logs/prompts_tooling/make_check.log`). Pyflakes was clean. `tests/test_contracts.py` and `tests/test_decoupling.py` gave 37 passed in 36.45 s. The rest of the suite gave 545 passed and 5 skipped in 448.03 s. The pre-lot baseline was 538 passed and 5 skipped; the difference is the 7 new tooling tests.

**SHA-256 (before → after).**

| File | Before | After |
|---|---|---|
| `prompts/Prompts_Claude_Code_v5.md` | `5010cc23b247d99f39adc4646ee5e8645b7f524494f60f8db8740c74a334106f` (139 933 B) | `c84d560cfaf821a16892d11cb5ff854f941c09e50a2f07a70026e10d02bdceac` (188 955 B, +49 022 B) |
| `tools/check_prompts.py` | `025a9c4880656db98a4bcd006e9ff6a91f5916e2c52270673d9e42cd0cb42669` | `053930fd7a5d85560d3ed701f551999c5c9fc837dd21ace4a306d45498fbbf4c` |
| `tests/test_check_prompts.py` | `bde2c6a53a1a6fbb12ed6927a94fbad8316cb28150e64ce081b00efa9e1ff405` | `f65adbea5cd34281fb0955415d67fc6a4edc4121cf4290667941ee29c0ec844a` |

**Invariants checked.**
- `results/e2/e2_cells.csv` is `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, identical on disk and in the index (`cmp`).
- `PLAN.md` is `ed14c47a8df2898ec2cba4662fe7b39a0f0fd8316b9f9eaa299a31ae7b0730ac`, unchanged.
- The Codex files are unchanged (SHA-256 at pre-flight and after the migration):

  | File | SHA-256 |
  |---|---|
  | `prompts/plans/plan-31.md` | `70a1dde1…48fb` |
  | `prompts/GO-stream-31-tooling.md` | `687ce138…a8c7` |
  | `prompts/NO-GO-stream-31.md` | `d6627920…f473` |
  | `docs/audits/streams_01_27_relevance_2026_11_06.md` | `c598a4ad…f975` |

- `git diff --quiet HEAD` holds on `prompts/streams`, `experiments`, `jepadrift`, `configs`, `results`, `figures`, `docs/DEVIATIONS.md`, `CLAUDE.md` and `Makefile`.

## Errors and Dead Ends

- **Stopped first full run.** I stopped the first full `make check` during its second pytest phase after the self-review found the false-100 % ratio line. Phase 1 had already passed (37 tests); the log is `logs/prompts_tooling/make_check_aborted.log`. The suite was re-run on the final code.
- **No test errors.** No test or fixture error required a correction; the only re-run after GREEN followed a cosmetic line re-wrap.

## Current State

- **Lot 1 is implemented and verified, and nothing is committed.**
- **Codex closing controls** (reported by Codex on 2026-11-06, not re-run here): `tests/test_check_prompts.py` 9 passed, `make prompts-check` 33/33, and J1 (`results/e2/e2_cells.csv`) intact on disk and in the index.
- **Subsequent Codex checkpoint.** Codex independently repeated these controls at 11:30 UTC, verified the append-only master and the original test ASTs, completed the mandatory AST-only reindexation, and refreshed its own historical audit with these results and the researcher's 20-minute monitoring instruction. The audit hash in the pre-flight table above describes the implementer's earlier checkpoint, before that Codex update. The final full check will run in the active pre-commit hook; its output is retained in `logs/prompts_tooling/codex-commit.log`.
- **Modified files:** `tools/check_prompts.py`, `tests/test_check_prompts.py` (T1–T7 added; the two pre-existing tests unchanged) and `prompts/Prompts_Claude_Code_v5.md` (4 PCA blocks appended).
- **New file:** `prompts/wrapups/wrapup-31.md`.
- **Expected `git status --porcelain`.** My lines are the three ` M` lines for those files plus `?? prompts/wrapups/wrapup-31.md`. The untracked Codex files `docs/audits/streams_01_27_relevance_2026_11_06.md`, `prompts/GO-stream-31-tooling.md`, `prompts/NO-GO-stream-31.md` and `prompts/plans/plan-31.md` are unchanged.
- **Ignored run logs** live under `logs/prompts_tooling/`: ledger, red, green, pre, sync, ids, make_prompts_check, make_check.
- **Not done (no authorization):**
  - no Git operation, no reindex, no sub-agent;
  - no lot 2 file;
  - no producer, figure or data change.

## Vigilance Points

- **New CLI contract.** `EXPECTED_IDS` is a constant of the CLI. A future stream prompt must be added there, because the check refuses unexpected ids by design.
- **Stricter `check()`.** It now requires the exact block (trailing newlines aside) and the presence of the full file text. A prompt file ending with two or more newlines cannot pass inside a fenced block. None does today.
- **Block extraction.** A block now ends at the next `` ````markdown `` opening line (a four-backtick fence). No prompt body contains such a line today; if one did, the check would fail rather than pass silently.
- **Non-atomic write.** The master write is still not atomic, as before. A partial write is detected by the fence and exact-block checks and is recoverable from Git.
- **`CLAUDE.md` wording.** It still describes `check_prompts.py` as checking "exact substrings". It was not edited (Codex ownership).
- **Known label defect, out of scope.** `experiments/figures/plot_figure_1.py:582` prints a hard-coded "(n = 40)" in the full-run figures. It is lot 2 test D7b, and no fix is authorized.
- **Suite duration.** `make check` stays above the 5-minute guideline; this predates lot 1 (baseline 450.90 s for the second pytest phase).
- **Periodic collection.** The periodic collection the user requested runs outside the repository under Codex. Its timer is not part of lot 1 and was not touched.

## Recommendations

- **Codex.**
  - Review the diff.
  - Run the closing controls: the mandatory end-of-stream reindexation (`tools/reindex_graphify_jcodemunch.sh`), then explicit staging of `tools/check_prompts.py`, `tests/test_check_prompts.py`, `prompts/Prompts_Claude_Code_v5.md`, `prompts/wrapups/wrapup-31.md` and the Codex-owned stream files.
  - Make one Conventional Commit without trailers, for example `fix(tools): discover the PCA stream prompts and make master sync idempotent`.
- **Optional follow-up.** Align the `CLAUDE.md` description of `check_prompts.py` with the exact-block check.
- **Lot 2** (PCA contracts QA, its full-run integration and the D7b diagnosis) needs its own GO, after this commit. Its plan is section 4 of `prompts/plans/plan-31.md`.
