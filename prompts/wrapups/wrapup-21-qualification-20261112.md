# Wrapup — Stream 21-qualification-20261112: documentary qualification-gap map of the runner targets

UTC timestamp: 2026-11-12T13:13:00Z. Checkpoint written in the closeout slot that Codex allocated, before the Codex
closeout.

## Context

- **Mandate.** Stream 21 qualification of the candidate runner targets e1, e3 and e10, documentary only: priority P2
  of the 2026-11-12 continuation (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_12.md:119-123`) and the
  mission `logs/stream_21_qualification/mission-plan.md` (ignored, SHA-256
  `d947c7c02b8c0a7462a542dbb98d2d370d1d351814f04868cc8edc3d9a1fcaba`).
  - Authority: Codex documentary GO under the delegated mandate, then a Codex documentary amendment. No researcher
    signature and no scientific authority.
  - Lots 21-F (`26a2a56`) and 21-R (`3c7f8f3`) stay closed and were not redone.
- **Session.** Interactive Claude Code session `jepa-s21-qualification-20261112`, UUID
  `8d7f770c-0998-45fe-b18b-90a9201d646c`.
  - Opus 5.5, effort max, no subagent. Model, effort and context were unchanged from planning to this checkpoint.
  - Worktree `~/.codex/worktrees/5e00/JEPA-Drift-experiments`, branch `stream-21-qualification-20261112`, base
    `891cfa5f56c8ec20988f9a18efef4ed468e1c720`.
- **Workflow.**
  1. **Native plan v0** in plan mode (130 lines, SHA-256 `59b85c255f3973bbed6ab9df8a0062c0ad5d380ce31bad0226e94fd75dc60fcf`),
     reported as PLAN_READY without leaving plan mode.
  2. **Canonical plan** `prompts/plans/plan-21-qualification-20261112.md` (148 lines, SHA-256
     `d7e441320f23c6582959fb00ac61f54fa9185020f19436c7a74f553346d35b02`), written by Codex. Its « Décision GO intégrée »
     retains H1, H2, H4 and H5, replaces H3 with three Git read commands, keeps Q1-Q7 OPEN and adds seven reception
     precisions. The native v0 is archived unchanged as `logs/stream_21_qualification/native-plan-v0.md`.
  3. **Separate GO** `prompts/GO-stream-21-qualification-20261112.md` (45 lines, SHA-256
     `7e87e28d303a46e0367eaf50a21299f4cdef4e51e81d88223f339cc5a85dd3b6`).
  4. **Official exit from plan mode** in the same session; Codex verified the auto mode and gave the writing signal.
  5. **Document** written, checked (runs 1 and 2) and delivered as REVIEW_READY with SHA-256
     `97375cb3b8016c92ff898cb7564f83de725f4607d47eef1df9d25917c5dd3fe1` (223 lines).
  6. **Amendment** `prompts/GO-stream-21-qualification-20261112-amendment.md` (17 lines, SHA-256
     `4520bef72ab71a77b93ddf1e9d5403088a42cb451c82c0dc15f567406e37da1a`): three bounded semantic corrections. Codex
     archived the received document as `logs/stream_21_qualification/document-received-v0.md`.
  7. **Corrections** applied to the document only, run 3, REVIEW_READY with SHA-256
     `e2ea298775b869d04f85bf2957de6cfbd85abd33450971464d3c7846f005ebe9` (227 lines).
  8. **Codex independent reception** accepted the corrected document and allocated the closeout slot; this checkpoint.
- **Boundary.** The production runner stays DEFERRED; e1, e3 and e10 stay UNQUALIFIED; gates G1-G10 and questions
  Q1-Q7 stay OPEN. No runner, dispatcher, reader, fixture, schema activation, configuration, `configs/FROZEN.json`,
  `make freeze`, J4, E5 artifact, experiment or data read was produced.

## Validated Results

- **Deliverable.** `docs/audits/stream_21_qualification_20261112.md`: 227 lines, SHA-256
  `e2ea298775b869d04f85bf2957de6cfbd85abd33450971464d3c7846f005ebe9`, the version Codex accepted. English, ASCII,
  at most 120 bytes per line, eight sections:
  1. Status, authority and evidence rules.
  2. Cross-cutting facts: freeze verifier API, whole-file loaders, declared coverage, bounded precedent, import side
     effects, `spawn` pools, digests and guards, inputs outside POLICY.
  3. Candidate maps e1, e3, e10, then common descriptors, the three failure phases, collisions and evidence classes.
  4. Gate matrix G1-G10, every gate OPEN.
  5. Minimal future fixtures and refusals, PROPOSED / NOT EXECUTED.
  6. E5 gate file versus runner namespaces (question Q6 for the researcher).
  7. Exact pending decisions Q1-Q7, all OPEN.
  8. Not executed.
- **Documentary findings** (facts anchored `file:line` at `891cfa5` inside the document; no new scientific result):
  - The three producers load whole `ret_wide.npy` files through `DATASETS` before slicing `pre_monitor`. The
    manifest declares D2 rows up to 2025-06-30 and D3 rows from 2000-01-03 to 2026-10-16. No consumed byte is
    verified; digests are only logged.
  - With `--jobs > 1`, tasks that call the loaders run in `spawn` workers. Inferred, not executed: such a worker can
    re-import the target and reload whole files. A parent-only ORIGIN check does not qualify the children.
  - The E10 guard checks only the upper bound, so the D3 row of 2005-01-03 stays in E10 while E1 and E3 drop it:
    segment declarations are per target.
  - Audit CSV files under `results/audit/` and the `z_*.json` sidecars are read by producers but are neither POLICY
    roots nor manifest entries.
  - The E1 output set depends on `--arms`, the data and producer branches; the E3 and E10 sets are fixed. Token
    variants (`--arms` order, `--families F1 F1`) change the argv, not the computation.
  - Real windows of the three targets are retrospective or descriptive without an independent holdout; E3 also has a
    synthetic D5 P1-D control with separate calibration and evaluation roles and a Wilson interval, which certifies
    only its own model.
  - E5: prompt 22 writes `results/e5/J4_gate.txt` through the runner, while the proposed rewrite writes
    `results/e5/j4_verdict.json` by a direct script call; only a gate file declared in the runner namespace fits the
    contract as written.
- **Documentary checks actually observed** (shell only; journal `logs/stream_21_qualification/doc-checks.md`):
  - Run 1, 2026-11-12T12:53:10Z, document `59a9e0e382933345a2f8ac33309a1eb346e6723c4c9a4928fa90786ea2c22c96`:
    C1 FAIL (252 lines against 230; width 0 lines over 120 bytes); C2-C4 and C6-C10 PASS; C5 reviewed.
  - Run 2, 2026-11-12T12:57:14Z, document `97375cb3...d3fe1`, 223 lines: every check PASS (96 distinct full-path
    anchors, 0 bad).
  - Run 3, 2026-11-12T13:09:04Z, document `e2ea2987...ebe9`, 227 lines: every check PASS.
    - C1 227 lines, 0 over 120 bytes; C2 0 non-ASCII lines; C3 UNQUALIFIED, DEFERRED, PROPOSED, NOT EXECUTED and
      OPEN present; C4 10 distinct gates and 10 OPEN bullets; C5 manual review of 3 negations only.
    - C6 95 distinct full-path anchors exist within file bounds, 0 bad; C7 no private or absolute path; C8 the ten
      expected paths absent.
    - C9 J1 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` (47 lines, 47 CRLF), E3
      `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, PCA full manifest
      `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`.
    - C10a 36 protected paths and the amendment unchanged; C10b exactly four untracked paths (document, amendment, GO,
      plan); C10c `git diff --quiet HEAD` 0 and no name; C10e the Codex archive equals `97375cb3...d3fe1`; C10d
      `find -newer` lists only the document, the Codex archive and the amendment.
    - C11a 0 retired wordings; C11b the eight required correction markers present.
  - Each check prints its own PASS or FAIL; no global PASS is derived when a check fails.
- **Codex reception.** The independent reception of the corrected document was accepted. This is Codex's result,
  reported as received, not observed by the worker.

## Errors and Dead Ends

- **Initial C1 FAIL, kept on record.** C1 (length and width) failed in run 1 on its length component: 252 lines
  against 230; the width component passed. Worker format correction: full rewrite with the Write tool, same facts and
  anchors, merged bullets, compact gate matrix and no blank line after headings, giving 223 lines.
- **Codex semantic corrections** (amendment lines 9-11), distinct from the worker's format correction:
  1. **Holdout scope.** "No untouched holdout exists" was false for E3 as a whole: E3's synthetic D5 P1-D control has
     separate calibration and evaluation roles (`experiments/e3_calibration.py:4-7`, `tests/test_e3.py:196-217`).
     E3 now separates real windows from that control; the E1, E10, G2 and Q2 wordings are restricted to real windows.
  2. **DATA versus TARGET_FAILED.** The shortcut "a reader refusal before computation is DATA", present in the native
     plan and in the initial GO precision 6, contradicted the contract: any exception during the target import or
     `main`, a reader's included, is TARGET_FAILED (`docs/sections/benchmark_runner_contract.md:265-266`). The
     document now lists three phases: pre-import descriptor refusals (`:194-195`), TARGET_FAILED, and DATA for absent
     or mismatching reader evidence at acceptance (`:220-224`, `:378`). Escalation and evidence format stay DEFERRED.
  3. **Guards.** "Refuses unconditionally" overstated the guards. They refuse rows after 2019-12-31 and the
     test-window request without consulting any freeze; pre-2020 rows stay accepted within each target's bounds.
- **Canonical-plan wording corrections by Codex.** The Fortran precedent excludes only a contiguous C-order prefix
  read, not every bounded reader; `spawn` reads are conditional on tasks that call the loaders, never attributed to
  pure D5 tasks.
- **Plan-time Git read.** One read-only `git status --porcelain` ran during planning, before the GO defined Git use.
  It was disclosed at PLAN_READY; no Git mutation occurred.
- **No runtime or scientific failure:** nothing was executed.

## Current State

- **Git** (read-only commands with `GIT_OPTIONAL_LOCKS=0`).
  - Branch `stream-21-qualification-20261112` at `891cfa5f56c8ec20988f9a18efef4ed468e1c720`; `git diff --quiet HEAD`
    gives 0 and `git diff --name-only HEAD` lists nothing. The worker made no commit, staging or Git mutation.
  - Status before this file: `?? docs/audits/stream_21_qualification_20261112.md`,
    `?? prompts/GO-stream-21-qualification-20261112-amendment.md`, `?? prompts/GO-stream-21-qualification-20261112.md`,
    `?? prompts/plans/plan-21-qualification-20261112.md`. This checkpoint adds
    `?? prompts/wrapups/wrapup-21-qualification-20261112.md`.
- **Five deliverables before commit:** the document (`e2ea2987...ebe9`), the canonical plan (`d7e44132...5b02`), the
  GO (`7e87e28d...d3b6`), the amendment (`4520bef7...da1a`) and this checkpoint. The document, plan, initial GO and
  amendment are unchanged since the Codex reception.
- **Ignored journals** in `logs/stream_21_qualification/`.
  - Codex-owned: `mission-plan.md` `d947c7c02b8c0a7462a542dbb98d2d370d1d351814f04868cc8edc3d9a1fcaba`;
    `native-plan-v0.md` `59b85c255f3973bbed6ab9df8a0062c0ad5d380ce31bad0226e94fd75dc60fcf`;
    `document-received-v0.md` `97375cb3b8016c92ff898cb7564f83de725f4607d47eef1df9d25917c5dd3fe1`.
  - Worker-owned: `doc-checks.md` `e286857d708e3b8a0c58e293c933f7ef93538bf32c3fce51533ab1ff27748cc6`;
    `protected.sha256` `a9dd6b23ed6a501977c5183f5bbc40836c4df4e90910c68b484fa2ddf8a0b564` (36 paths);
    `protected-amendment.sha256` `52462cf63c98987e01132f284d4b6ba6faff2463e8c97e886b210e52e7880b03`.
  - The native plan file `~/.claude/plans/lis-logs-stream-21-qualification-mission-vast-storm.md` has SHA-256
    `59b85c25...0fcf`, equal to the archive.
- **Protected hashes** (shell, 2026-11-12T13:13:00Z): J1 `e315e537...0823` with 47 lines and 47 CRLF; E3
  `1ca7c3ae...68b3`, D8 stays FAIL; PCA full manifest `3b2299bc...2f47`; contract
  `2414f1dafef18c638d0c799c923e4700d35c3f9df9283868a048da9f4be63481`; `tools/freeze_config.py`
  `6e17eea2a1d3b974d3452dc9fe9f9acc634a0cf96450104a02861b67354cf6a3`; `tests/test_freeze_config.py`
  `aa51cc0299a66a88012d443bfe844433d8655df25b25889b501fd019a4771ec3`.
- **Absent:** `configs/FROZEN.json`, `configs/e5.yaml`, `jepadrift/benchmark_runner.py`, `tools/benchmark_runner.py`,
  `tests/test_benchmark_runner.py`, `results/e5`, `results/benchmark_runner`, `figures/benchmark_runner`,
  `logs/benchmark_runner`, `experiments/__init__.py`.
- **Environment.** Inherited labels, not remeasured, since no Python ran: Python 3.12.9 through the shared `.venv` on
  the Trading 3.12.9 base; NumPy 2.4.4, SciPy 1.17.1, pandas 3.0.6, PyYAML 6.0.3; torch 2.14.1 CPU through the
  conda-forge bridge (as reported in `prompts/wrapups/wrapup-21-R.md`). Linux 5.14.0-570.55.1.el9_6.x86_64.
- **Still owed by Codex, not yet performed and not claimed:** the controlled session exit; the AST reindex without AI
  summaries; the full `make check`; explicit staging of the five deliverables; an anonymous Conventional Commit
  without trailer; the range, size and private-path audit; the rebase and push protocol; the final reception. This
  lot ran no test; the last suite count (1,193 PASS and 5 D4 skips after 21-F) is historical.

## Vigilance Points

- **Nothing is closed or qualified.** G1-G10 are OPEN, e1, e3 and e10 UNQUALIFIED, production DEFERRED and Q1-Q7
  OPEN; Q7 belongs to a future Codex technical plan.
- **Failure phases.** Pre-import descriptor refusals (PROTOCOL, DATA, READER or TARGET) differ from any exception in
  the target import or `main`, a reader's included (TARGET_FAILED, exit 3), and from absent or mismatching reader
  evidence at acceptance (DATA). How a reader refusal is surfaced and the evidence format stay DEFERRED (G9, G10).
- **Holdout.** The real windows of all three targets have no independent holdout; E3's D5 P1-D control speaks only
  for its synthetic model.
- **Declared versus consumed bytes.** Manifest digests are declarations; whole files, 2020+ rows included, are
  loaded today; no bounded real reader exists. UNKNOWN: D2 memory order, Parquet row-group boundaries at 2020-01-01,
  `chars.parquet` coverage; no data file was opened.
- **Guards.** They refuse post-2019 rows and test-window requests without consulting a freeze; the rule at
  `CLAUDE.md:161-162` names a freeze check that no guard performs.
- **Workers and inputs.** `spawn` workers escape a parent-only ORIGIN check (Q7); audit CSV files and sidecars sit
  outside POLICY (Q4).
- **E5.** No fake `results/e5/J4_gate.txt`, link or shim; Q6 belongs to the researcher.
- **Anchors.** Line references are valid at `891cfa5`; a later base may shift them. C6 checks existence and bounds
  only; anchor meaning rests on targeted rereading.
- **Sealed results.** J1 CRLF line ends must not be normalized; E3/D8 stays FAIL; PCA artifacts stay unchanged.

## Recommendations

- **Codex closeout.** Run the owed sequence of Current State. Stage exactly the five deliverables by explicit path;
  the journals stay ignored. Check that the pushed range holds no absolute or private path and no file over 50 MB.
- **Next bounded tasks, each under its own plan and GO:**
  1. G9: a Codex proposal of the `protocol`, `data` and `reader` schemas and of the evidence format, then researcher
     approval (Q1).
  2. G3 and G4: a per-dataset bounded-reader design note, then a layout probe under its own GO (Q3).
  3. Q4: the treatment of audit CSV files and sidecars (a `data` entry or a POLICY v2 with a new verifier).
  4. Researcher decisions Q2 (holdout admissibility and variants), Q5 (post-2019 metadata) and Q6 (E5 gate file).
  5. Q7 in the future runner implementation plan.
- **Witness order.** Once an engineering GO exists, the schema-independent refusals R1-R8 can come first; any positive
  dispatch waits for an approved schema.
- **Not to do.** No rerun of 21-F or 21-R, and no E1, E3 or E10 reproduction without a pre-2020 mandate (G8).
- **Delivered by this lot:** one documentary gap map; no algorithm, test, producer, configuration or run.
