# Wrapup — stream 23-review: documentary compatibility review of E6 phase 1 (2026-11-06)

## Context

- **Request.** `logs/orchestration_20261106/request.md` relays the researcher's instruction of 6 November through
  Codex. The mandate covers only the phase 1 already produced on `stream-23`. It excludes any phase 1 or phase 2 run,
  any P4-D or P5-D addition, and any merge of its commits.
- **Workflow.**
  - A native plan was written in plan mode. Codex rejected the exit from plan mode and answered through repository
    files.
  - The canonical plan is `prompts/plans/plan-23-review.md`, with its « Décision GO intégrée ».
  - The GO is `prompts/GO-stream-23-review.md` (2026-11-06, 12:22 UTC), given by Codex within the delegated mandate.
  - The answers to Q1–Q5:
    - Q1: a composite verdict.
    - Q2: Python limited to AST parsing and Git result blobs.
    - Q3: path analysis suffices, without claiming a reproduced merge.
    - Q4: the installed wrap-up directive is mandatory.
    - Q5: a reopening needs a written request and a new GO.
- **Mandatory precisions from the GO.**
  - δ = 0.5 belongs only to the full's energy CUSUM comparator.
  - The PCA is fitted on calibration rows, and no JEPA conclusion is drawn.
  - D6 is a descriptive diagnostic without independent FPR.
  - Cited times are historical.
  - The AST certifies neither reproduction nor dynamic compatibility.
- **Base.** `20ad9e860a58373ec85405de6ee19a68322dd02e` on branch `review/stream-23-20261106`, equal to `main`.
  `stream-23` stays at `3d0bd2071cb86afc6b196b5020ff729204746a93`, forked from `2b0b1cd`. The historical worktree
  `../JEPA-stream-23` was never accessed.
- **Ownership.** Claude owns `docs/audits/stream_23_compatibility_2026_11_06.md` and this wrapup. Codex owns the plan,
  the GO and Git.
- **Execution.** One interactive session in auto mode, set through the official control without bypass. No
  sub-agent, no Graphify or jCodeMunch, no import or execution of `jepadrift` or `experiments`, no return panel read
  and no Git mutation.

## Validated Results

Commands ran from the worktree root. Python checks ran under `.venv/bin/python` (Python 3.12.9, pandas 3.0.6) with
`OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`.
Git was 2.51.1. The check script read Git blobs through `git show` and parsed sources with `ast`. It lived in the
session scratchpad, outside the repository, and its final run exited 0.

- **V1, commits.** Only `7e4c7a1` and `3d0bd20` are unique to `stream-23`; neither is an ancestor of `main`.
  `HEAD...stream-23` gives 36 / 2: 35 commits up to `a0c576e`, plus `20ad9e8`, which is tooling only.
- **V2, sealed hashes.** Each SHA-256 recomputed from the blobs equals the hash recorded in the wrapup-23 version of
  the same commit.
  - CSV at `stream-23`: `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249`.
  - CSV at `7e4c7a1`: `1d16e6bde9a5b98966f9519f27474ed4d7084c8760c11ec90a7df2f249a4b452`.
  - The four figures and `configs/e6.yaml` are byte-identical between the two commits.
- **V3, CSV schema.** 190 rows × 50 columns, and the header equals the script's `COLUMNS`. D6 has 78 rows (6 null, 72
  drift); D5 has 112 rows (16 null, 96 drift). Between `7e4c7a1` and `3d0bd20`, only `ci_reason` changes, on the 72 D6
  drift rows.
- **V4, inputs.** Single blob ids across `2b0b1cd`, `HEAD` and `stream-23`: `ret_wide.npy` `0d69729b…`,
  `splits.yaml` `4753816d…`. Since the fork, the only change under `data/derived/d3_239/` is the added sidecar pair
  `z_55a11b75…`.
- **V5–V6, static compatibility.** All 20 library roots exist at `HEAD`. Of the 87 definitions they reach, 77 are
  unchanged, 9 changed and 1 added after the fork. Each changed node is reached by E6 only with arguments that leave the
  fork's computation unchanged: no `C`, `missing` = False, no `pretrain` hook, no `fit` parameter, Z-dict windows and
  the F4 early return.
- **V7, determinism (static).**
  - Every RNG is `default_rng(SeedSequence([23, …]))`; there is no global or stdlib RNG.
  - The CSV is written by `pl.save_fair_csv`, and the process pools use `spawn`.
  - Determinism across runs and `--jobs` values is ARCHIVED (wrapup-23), not re-executed.
- **V8, conventions.** Delay definitions coincide: offset + 1 for E6 and 1-based `first_hit` for the full, both with
  censoring at H. The threshold rules differ: E6 uses an empirical calibration FPR(H) ≤ α, the full
  `predictive_exchangeable_rank_v2`. The full uses δ = 0.5 only in its energy CUSUM comparator.
- **V9, overlap with the full.**
  - The published full run is synthetic only.
  - Its single covariance scenario is a PC1–PC2 rotation at 30°: `rotation_pair: [1, 2]` is converted from 1-based
    indices.
  - Its index-energy comparator has the same stream definition as P1-D.
  - It has no analogue of P3-D.
- **V10–V12.**
  - `e6.wilson` duplicates `stats/intervals.wilson`, added after the fork; their numerical equality was not
    evaluated.
  - `docs/DEVIATIONS.md` is the only path modified on both sides: a predictable textual conflict, not reproduced.
  - The 12 new files total 900,628 bytes, including 687,198 bytes of figures.
  - Times are historical (full run 41 s on 48 cores).
- **V13–V15, from the CSV.**
  - D6 is in-sample on all 78 rows. The null FPR is 0, with no interval.
  - All 72 `ci_reason` values state the prespecified ten-block criterion (2.77 and 0.88 blocks) and none cites
    Künsch or Lahiri.
  - For the D5 PC1–PC2 rotation at H = 250, P1-D detects at rates 0.040, 0.024 and 0.006, and P3-D factor with K = 1
    gives G_ADD 14.59, 67.71 and 105.42, all `lower_bound`.
- **V16–V17.** D8 remains FAIL, P4-D is not calibrated for J4, and `--phase 2` is refused until stream 16.
- **Verdict.**
  - Statically compatible under conditions.
  - Reproduction not executed.
  - Utility complementary and non-critical.
  - Recommendation: preserve and defer. Any reopening needs a written trigger and a new targeted GO with conditions
    C1–C7 of the audit.
- **SHA-256 of the deliverables.**
  - `docs/audits/stream_23_compatibility_2026_11_06.md`:
    `7bfe3acadb8322d26ed7268b5b02f7460312824018b72c0e55c0a7a9f77d8624` (248 lines).
  - This wrapup: hash reported in the closing message.
- **Codex files read, never written.** `prompts/GO-stream-23-review.md` `989b9a0b…4321`;
  `prompts/plans/plan-23-review.md` `19373230…4528`.

## Errors and Dead Ends

- **Check-definition error.** The first run of the check script failed one assertion. It assumed that `in_sample`
  held the script's `IN_SAMPLE` text. In fact `in_sample` is a boolean (True on the 78 D6 rows, False on the 112 D5
  rows), and the text sits in the `ci_reason` of the 6 D6 null rows. The assertion was corrected, not the data; the
  second run exited 0.
- **Plan-mode description corrected.** Row V9 of the native plan said that the full monitors spectral prefixes with
  an energy CUSUM. In the full, spectral subsets go through the mean mixture scan and the covariance vech scan, and
  δ = 0.5 belongs only to the index-energy comparator, as the GO states. The audit uses the corrected description.
- **Return-panel bytes during plan mode.** Before the GO, the blobs of `data/derived/d3_239/ret_wide.npy` and
  `splits.yaml` at three refs were streamed into `sha256sum` to compare hash prefixes with wrapup-23. No value was
  parsed or displayed. After the GO, input identity relied on Git blob ids only.
- **« Line 23 » of the relevance audit.** The literal file line 23 is the stream 03 row. The review used the stream 23
  row (file line 53), as stated in hypothesis H1 of the plan.

## Current State

- **Subsequent Codex closing checkpoint (2026-11-06).** After Claude's final read-only confirmation, Codex closed its idle review session and independently repeated the saved Git-blob/AST checks: all passed. The check source is retained locally as `logs/orchestration_20261106/review23_checks.py`, with explicit `round_trip` on its text CSV reads; output is `codex-independent-check.log`. `make prompts-check` returned 33/33, and J1 disk/index retained the recorded SHA. Codex mounted the existing `d3_yf` and `baf` raw subdirectories as separate absolute symlinks for the required closing regression suite; `data/raw` remains a real directory and no EUROFIDAI link was added. The final suite runs in the pre-commit hook, with output in `logs/orchestration_20261106/codex-commit.log`. These Codex actions postdate the implementing-session checkpoint below.
- **New untracked files owned by Claude:** `docs/audits/stream_23_compatibility_2026_11_06.md` and
  `prompts/wrapups/wrapup-23-review.md`.
- **Codex files:** `prompts/GO-stream-23-review.md` and `prompts/plans/plan-23-review.md`, untracked and unchanged by
  Claude.
- **Expected `git status --porcelain`:** these four `??` lines, plus the ignored `.venv`, `external` and
  `logs/orchestration_20261106/`. `git diff --quiet` holds, so no tracked file changed.
- **Historical state preserved.** `stream-23` stays at `3d0bd20`. No E6 run, test, `make check`, merge, rebase,
  cherry-pick or merge-tree took place. Code, configurations, CSV files, figures, `docs/DEVIATIONS.md` and memory are
  unchanged. No reindex and no commit took place.

## Vigilance Points

- **Static is not dynamic.** AST equality and branch reasoning do not certify reproduction. Hypothesis H-repro (a
  byte-identical CSV after integration) stays open until C3, under a new GO.
- **Axis conventions.** `[1, 2]` means PC2–PC3 in E6 (0-based) and PC1–PC2 in the full (1-based).
- **In-sample against independent.** D6 is an in-sample descriptive diagnostic without independent FPR, and its
  IC=NA follows a prespecified reporting criterion. D5 is conditional on one fit panel.
- **PC1–PC2.** The G_ADD values are lower bounds driven by P1-D's one-sided blindness and by the K = 1 channel
  alignment. The PCA is fitted on calibration rows: no JEPA or trained-encoder conclusion follows.
- **Thresholds.** E6 and full thresholds use different rules, so their rows must never be pooled.
- **Historical times.** The cited times come from wrapup-23 and were not re-measured.
- **Integration traps.**
  - `docs/DEVIATIONS.md` will conflict at its end.
  - `results/e6_quick/` is not ignored.
  - `C-E6-phase1` is in English, as prompt 23 required, whereas `CLAUDE.md` lists French for DEVIATIONS entries.
    Keep the archived text verbatim.
- **Suite duration.** The baseline `make check` already exceeds five minutes; integrating E6 would add 13 tests (8 s,
  historical).

## Recommendations

- **Codex.**
  - Review the two owned files.
  - Run the closing checks; Git closure is yours. Stage explicitly only the paths the commit owns.
- **Decision.** Preserve and defer. Keep `stream-23` and `../JEPA-stream-23` intact. Reopen only on a written trigger
  (Q5), through a new targeted GO that carries C1–C7.
- **If reopened.** Execute C3 first: rerun phase 1 and require CSV `4101c867…d249`, quick CSV `874be212…` and the
  four figure hashes. Stop on any mismatch, before any interpretation or `DEVIATIONS.md` edit.
- **Optional.** Harmonize `e6.wilson` with `stats/intervals.wilson` only together with C3.
