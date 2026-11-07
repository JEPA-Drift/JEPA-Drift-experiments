# Wrapup — Stream 21-F: freeze verifier on synthetic Git fixtures

## Context

- **Mandate.** Continuation bootstrap of 2026-11-07, Lot F of stream 21: the smallest complete standard-library `tools/freeze_config.py` with `tests/test_freeze_config.py`, tested only on synthetic temporary Git repositories. Excluded: a real `configs/FROZEN.json`, any Makefile change, data reads, monitor access, real runs and the J4 activation.
- **Session.** Base `47d85dc977547409fc6f6d71dcf5488eb935d7d5`, branch `stream-21-F`, worktree `~/.codex/worktrees/1a88/JEPA-Drift-experiments`, interactive session `jepa-s21-F` (UUID `921f284c-d6ae-4f31-b270-3f881fb33718`). Claude Code Opus 5.5, effort max, no subagent; model, effort and context unchanged from planning to this checkpoint.
- **Workflow.**
  - Native plan revision 0, then a Codex technical NO-GO (`prompts/NO-GO-stream-21-F.md`) with five bounded corrections: required roots, concurrent creation, owned-path validation, an exploitable RED, single-use freeze.
  - Native revision 1 (533 lines, SHA-256 `3b8a72a31b2d87793ca38d9636d86d24783fcff16ee8fa6423a259d4f504a086`), archived unchanged inside the canonical plan `prompts/plans/plan-21-F.md` (SHA-256 `9546d4225d93c054e2867263b6a5cf0b63c934b159f25e2bcd5c865062a1a34e`) with its « Décision GO intégrée ».
  - Separate GO `prompts/GO-stream-21-F.md` (SHA-256 `f1a794660ff0a881deb6244b24aef56efbf13c5dde48907ac19242d1e630175f`): a Codex GO under the delegated mandate, with no researcher signature.
  - TDD execution, then a Codex reception that reproduced three contract gaps (`logs/stream_21_F/codex-final-review.md`). They were corrected under the same GO, and Codex accepted the corrected implementation.
- **Execution protocol.**
  - Before every project run, the registry `~/JEPA-Drift-experiments/logs/orchestration_20261107/execution-19-21-state.json` was read; the run required `science_owner` = `stream-21-F` and `closeout_owner` = null. The command then ran under `flock -n -E 75` on the registry lock.
  - Interpreter `.venv/bin/python -B`, with `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and `MPLBACKEND=Agg`.
  - The two deliverables were edited with the native edit tools only.

## Validated Results

- **Deliverables (SHA-256), rechecked with shell hashes at this checkpoint:**
  - `tools/freeze_config.py` (new, 499 lines): `6e17eea2a1d3b974d3452dc9fe9f9acc634a0cf96450104a02861b67354cf6a3`
  - `tests/test_freeze_config.py` (new, 1006 lines, 190 tests): `aa51cc0299a66a88012d443bfe844433d8655df25b25889b501fd019a4771ec3`
- **Public API and CLI**, as in the accepted plan:
  - `FreezeError(code, detail)` with `.code` in `CODES` and `.detail`, where `str(err) == f"{code}: {detail}"`.
  - `check(root=ROOT)` returns `{commit, seal, approval, files, freeze_id}`.
  - `write(root, approval)` returns `{path, sha256, commit, files}`.
  - `main(argv=None) -> int`.
  - CLI: `python tools/freeze_config.py --check [--root DIR]` or `--write --approval prompts/GO-<id>.md [--root DIR]`. Exit 0 on success, 1 on a refusal printed as `freeze-config: error: CODE: detail`, 2 on usage. The 13 codes are ROOT, GIT, ABSENT, LINK, FORMAT, SEAL, CHANGED, COVERAGE, HASH, APPROVAL, EXISTS, PROJECT, IO.
- **Constants.**
  - `SCHEMA = "jepadrift-freeze/1"`, `FROZEN = "configs/FROZEN.json"`.
  - `POLICY` holds the eleven roots `Makefile`, `conda-torch.lock`, `configs`, `conftest.py`, `data/derived/MANIFEST.json`, `docs/manifests/d4_manifest.json`, `experiments`, `jepadrift`, `requirements.lock`, `requirements.txt` and `tools/freeze_config.py`.
  - `APPROVAL` is `prompts/GO-[A-Za-z0-9][A-Za-z0-9._-]*\.md`.
  - `PROJECT_ROOT_COMMIT = 32a55c8d6e16dc74f79f7cd17e61e5fb73d89332`, `MAX_FROZEN_BYTES = 1048576`, `GIT_TIMEOUT = 60`.
- **Semantics.**
  - **FROZEN format.** Canonical JSON `{schema, commit, files, approval{path, sha256}}`: sorted keys, compact separators, ASCII, final newline. Parsing is strict UTF-8 JSON that refuses duplicate keys, NaN and Infinity. `freeze_id` is the SHA-256 of the FROZEN bytes.
  - **Coverage.**
    - Every regular file under the eleven roots is covered. All eleven roots are required with their type, both in C and on disk, and a directory root must hold at least one covered file.
    - Directories named `__pycache__` are excluded identically on disk and in the tree.
    - Each covered file needs its SHA-256 equal to FROZEN and its Git blob id equal to C. Untracked, ignored and missing files are refused.
  - **Seal.**
    - C is a strict ancestor of HEAD, and `C..HEAD` is linear.
    - S is the first commit after C; it only adds FROZEN, with mode 100644.
    - The full history of C holds no FROZEN, so the schema serves once per lineage.
    - A per-commit rule applies after S: a commit touching the policy gives CHANGED, one touching FROZEN gives SEAL, one touching the approval gives APPROVAL.
  - **Approval.** A tracked 100644 file in C, untouched after C, whose disk bytes equal C. It is recorded as hashed provenance and never interpreted.
  - **Git isolation.**
    - Every inherited `GIT_*` variable is dropped. The tool sets `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CEILING_DIRECTORIES` (the parent of the root).
    - It also sets `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_LITERAL_PATHSPECS=1`, `GIT_TERMINAL_PROMPT=0` and `LC_ALL=C`.
    - Only plumbing commands run. Grafts, shallow repositories and non-SHA-1 object formats are refused.
  - **Links and races.**
    - Every open is relative to a descriptor, with `O_NOFOLLOW` at each component. Types are classified by `lstat` without following any link.
    - The `(st_dev, st_ino)` identity is compared between `lstat` and `fstat`. Files are opened with `O_NONBLOCK`.
  - **Write.**
    - Two fixture-only guards: the root must lie strictly under `tempfile.gettempdir()`, and the repository must not hold the project root commit.
    - Creation is exclusive (`O_CREAT|O_EXCL|O_NOFOLLOW`) and followed by `fsync`.
    - After a failure, the file is removed only if its name still designates the created inode.
- **TDD evidence** (ignored journals in `logs/stream_21_F/`).
  - **RED-0** (22:40:10Z): tests only, with no tool file and no skeleton; fixtures built by Git and the test oracle alone.
    - 176 tests and 0 collection or fixture errors; T0 passed.
    - 10 behavioural AssertionErrors: the four CLI witnesses, P7, L2 and four usage cases.
    - 164 ModuleNotFoundError and 1 FileNotFoundError, not counted as proof (`red0.log`).
  - **GREEN-1 to GREEN-5:** 60, 18, 26, 33 and 40 passed.
  - **First full run:** 176 passed. Three witnesses were then added after mutation run 1 (A4 reverted, K2 manifest-untracked, K1 untracked manifest), giving 179 passed (`green_final.log`).
  - **Corrections after the Codex reception** (`fix.log`):
    - Tracked-cache exclusion. RED: 2 failed, COVERAGE instead of OK, while 4 retention witnesses passed; GREEN: 185.
    - Root-descriptor I/O. RED: 4 failed, PermissionError escaped `check`, `write`, `main --check` and `main --write`; GREEN: 189.
    - Global five-path budget. RED: 10 paths cited; GREEN: 190.
  - **Final native run** (23:13:17Z): 190 passed in 8.69 s (8.86 s wall), max RSS 46,100 kB. No skip or xfail, pyflakes clean, no line over 120 characters.
  - **Codex independent final reception:** 190 passed in 9.58 s (9.75 s wall), RSS 46,064 kB, pyflakes clean (`codex-final-tests.log`). All six immutable Codex probes pass (`codex-probes-green.log`; the probe SHA-256 stays `7667b2ea70ecb1b08978dde02a39eeb83c26aaf8fc91ced6f7e588949f2cc7ac`).
- **Mutation testing: 15 killed plus M02 equivalent, not 16/16.**
  - Method: out-of-tree runner, mutated source executed in memory in a fresh process, tool and test files unchanged.
  - M02 equivalence proof: a JSON source holding a duplicate object key can never byte-equal the canonical serialization of the parsed dictionary, whose keys are unique.
  - The strict duplicate-key parser is kept, and no detail-message test was added; Codex accepted this (`fix_mutants.log`).
- **Integrity controls** (`fix_controls.log`, 21 of 21).
  - The read-only real `--check` exits 1 with `ABSENT: configs/FROZEN.json is absent`; the worktree index keeps its SHA-256 and mtime.
  - No real FROZEN exists.
  - J1 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` holds on disk and in the index, with 47 lines and 47 CRLF.
  - E3 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3` and the PCA full manifest `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47` are unchanged.
  - No tracked file changed; the four pinned Codex files and the three reception files are unchanged. Codex checked the same points independently.

## Errors and Dead Ends

- **Empty system-Python heredoc.** While classifying the RED-0 report, a shell command contained an empty `python3 -` heredoc, run with the system interpreter.
  - It held an empty program, imported no project code and changed no file.
  - It still departed from the interpreter rule; every other Python command used the project venv explicitly.
- **NO-GO on plan revision 0.**
  - An absent root could be frozen as absent.
  - The pre-existing-file witness W1 never reached `os.open`, so it could not kill the `O_EXCL` mutant.
  - The owned-path validation rejected legitimate Codex files.
  - RED-0 relied on a skeleton and on fixtures built by the tool.
  - Single use per lineage was not stated.
  - All five were corrected in revision 1.
- **Mutation run 1 survivors M14 and M16.** They revealed missing witnesses rather than redundant guards:
  - an approval modified and then restored by later commits;
  - a file root untracked in C but left on disk; without the tree check, the walk raised an uncaught KeyError.
  - The witnesses were added, and no guard was weakened.
- **Codex reception gaps, all corrected with permanent RED then GREEN witnesses:**
  1. A force-tracked file below a real `__pycache__` directory was counted in the tree but skipped on disk, so write and check refused COVERAGE.
  2. The root descriptor was opened outside the OSError handler, so a PermissionError escaped `check`, `write` and `main`.
  3. A COVERAGE refusal cited up to ten paths, because the missing and extra lists each had their own budget.
- **Deviations from the plan grouping.**
  - The grafts and shallow witnesses, and A3 and A4-committed, turned green one step earlier than planned.
  - The final test count is 190 against the plan estimate of about 100.
  - Journals are pytest JUnit XML written by pytest itself, plus summaries written with the native write tool; there were no shell writes.
- **No scientific divergence.** There was no sealed scientific reproduction failure, no threshold tuning and no actual freeze.

## Current State

- **Git.**
  - Branch `stream-21-F` at base `47d85dc977547409fc6f6d71dcf5488eb935d7d5`, pre-commit. Claude made no commit, staging or Git mutation in the real repository, and the tracked tree is unchanged.
  - Status read at 2026-11-07T23:31:56Z, before this file was written:
    - `?? docs/audits/streams_01_31_continuation_2026_11_07.md`
    - `?? prompts/GO-stream-21-F.md`
    - `?? prompts/NO-GO-stream-21-F.md`
    - `?? prompts/plans/plan-21-F.md`
    - `?? tests/test_freeze_config.py`
    - `?? tools/freeze_config.py`
    - this wrapup adds `?? prompts/wrapups/wrapup-21-F.md`.
- **Seven deliverables.**
  - The two Python files above.
  - Four Codex documents: the canonical plan; the GO; the historical NO-GO (`f5811396803a2b43db165a1f1f240bc312865060c8a3f91287354aafa9bf75e7`); the inventory report `docs/audits/streams_01_31_continuation_2026_11_07.md` (`5931a375e58add2232dfbbe02151f5e92193ffab9cbf5f23bb9ac39a20d60d5b`).
  - This wrapup.
  - The journals under `logs/stream_21_F/` remain ignored.
- **Registry at this checkpoint:** `science_owner` = null, `closeout_owner` = `stream-21-F`, `wrapup_allowed` = true.
- **Environment.**
  - Python 3.12.9 through `.venv/bin/python` (venv built on the Trading 3.12.9 base); pytest and pyflakes come from the venv.
  - git 2.51.1; Linux. Nothing was installed or updated.
- **Pending, owned by Codex.**
  - Orderly session exit and an AST-only reindex without AI summaries.
  - The full `make check` with the torch shim and the existing full trials path for G1.
  - Explicit staging and an anonymous Conventional Commit without trailers.
  - Range, size and private-path checks, then integration and push, then final reception.
- **Baseline.** Before this lot the suite gave 1,003 PASS and 5 D4 availability skips. This is not the closing result: the final `make check` has not run, and its count is not predicted here.

## Vigilance Points

- **What a passing check certifies.**
  - It pins the bytes of the policy files at C and of the approval document.
  - It reads no data file and does not verify data bytes against the hashed manifests, the installed dependencies or the environment. It does not verify the authority of the approval document either.
  - It authorizes no J4 run.
- **Write guards.** They make a real FROZEN impossible with this tool: the root must be in the temporary directory, and the repository must not hold the project root commit. The J4 activation must replace both under its own GO.
- **Strict rules.**
  - The eleven roots are required, and the schema serves once per lineage.
  - History must stay linear after C.
  - The per-commit rule keeps a modify-then-revert sequence refused.
- **Known limits.**
  - Ignored cache content (`__pycache__`) is not covered, and the disk executable bit is not compared.
  - Publish and cleanup are not atomic (stat then unlink).
  - A race remains between check and execution.
  - Hard links and a replacement of the root path itself are not detected.
  - Local history and the verifier are trusted. A consistent local rewrite of C and S is undetectable without the pushed remote, and a modified verifier can lie.
- **Coupling with existing code.**
  - A real FROZEN would change `pre_j4.frozen_json_present` in the PCA benchmark manifest and break `tests/test_pca_drift_benchmark.py:719`.
  - The pre-J4 guards of the experiments are unchanged and do not read FROZEN.
- **Probe dependency.** The immutable Codex probe `logs/stream_21_F/codex_probes.py` loads the test helpers `_build`, `_git`, `_commit`, `_copy`, `_seal`, `_canon`, `_record` and `APPROVAL`. Renaming them breaks the probe.

## Recommendations

- **Codex closeout.** Run the sequence listed in Current State and stage the seven deliverables by explicit path. Check that the pushed range holds no absolute or private path and no file over 50 MB.
- **Lot R (runner contract).**
  - Call `check()` immediately before importing a target, and record `freeze_id` in the run identity.
  - Settle the runner location (`jepadrift/` or `tools/`): `POLICY` v1 freezes only `tools/freeze_config.py` among `tools/`, so a runner outside `jepadrift/` needs a policy v2.
- **J4 activation, under a separate plan and GO.**
  - Replace the two write guards and handle `frozen_json_present` together with the PCA test.
  - Wire the e1, e3 and e10 guards, and name the approval document.
  - A re-freeze on an existing lineage needs a new schema or verifier.
- **Other streams.** They remain as in the continuation inventory: global 21 is partial, the R documentary contract is next, the four S endpoints stay UNSOURCED, and the 19 scientific protocol and the 23 reproduction keep their own gates. There is no universal experimental GO.
