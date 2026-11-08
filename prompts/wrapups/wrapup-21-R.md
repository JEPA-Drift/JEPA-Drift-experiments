# Wrapup — Stream 21-R: documentary contract of the global benchmark runner

UTC timestamp: 2026-11-08T00:49:09Z. Checkpoint written before the Codex closeout.

## Context

- **Mandate.** Lot R of stream 21: a minimal contract for the future `jepadrift/benchmark_runner.py`, documentary only.
  - It comes from the continuation bootstrap of 2026-11-07 (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_07.md:117`).
  - Authority: a Codex GO under the delegated mandate, limited to documentation. It carries no researcher signature and no scientific authority.
- **Session.** Interactive Claude Code session `jepa-s21-R`, UUID `2142c482-a8fc-47e4-975b-dbf6c9bd1f80`.
  - Opus 5.5, effort max, no subagent. Model, effort and context were unchanged from planning to this checkpoint.
  - Worktree `~/.codex/worktrees/2160/JEPA-Drift-experiments`, branch `stream-21-R`.
- **Base.** `26a2a5696a4412af8aceb6dbde3a9874e996aaad`, the published lot 21-F, whose parent is `47d85dc977547409fc6f6d71dcf5488eb935d7d5`.
  - Planning started on `47d85dc`. Codex fast-forwarded the idle, clean branch to `26a2a56`.
  - That commit only adds seven files: the lot F deliverables and an inventory report.
- **Workflow.**
  1. **Native plan, revision 0** (SHA-256 `9e4fd544b929884b88a3fdeb326ef535b700a9250675baa46333d1410960e1f8`). It received a Codex NO-GO.
  2. **Review** (`logs/stream_21_R/codex-plan-review-v0.md`, final eight-point version, SHA-256 `75a886719f0ff048a3f93726af3e427eebc4b10b3e2570eb0acef75753bbaeac`). It held six corrections, an independent two-point addendum and the arbitrations Q1–Q9.
  3. **Native plan, revision 1** (413 lines, SHA-256 `f3493029b7f6ede5bff7bde8926d37b83324f173779fae7a61adaf804c74d200`). It is archived unchanged in the canonical plan and in `logs/stream_21_R/native-plan-v1.md`.
  4. **Canonical plan** `prompts/plans/plan-21-R.md` (SHA-256 `0f838115917c0064f278a60141e07a2c0439ff608f9c7473d70b5f3a88884bc0`). Its « Décision GO intégrée » holds the final YAML decision and reception precisions 1–4.
  5. **Separate GO** `prompts/GO-stream-21-R.md` (SHA-256 `0a4b0a46bd9b8b1faf7f8890a09ed424074fb5d702ddfb0802feac9d9148b14a`).
  6. **Exit from plan mode** through the official ExitPlanMode in the same session. Documentary work started once Codex had verified the mode.
  7. **Contract.** Written, then reviewed by Codex in `logs/stream_21_R/codex-document-reception.md` (SHA-256 `8f848f6ed98351fb8b19505f885cfdbc1ac62ea23c369e5d09ec25a096b8a8e6`). The three clarifications it asked for were applied.
  8. **This checkpoint**, written in the slot that Codex granted in the registry.
- **Boundary.**
  - The global runner stays DEFERRED.
  - Every candidate target (e1, e3, e10) stays UNQUALIFIED.
  - No runner source, test, `configs/FROZEN.json`, J4 activation, E5 configuration or run was produced.

## Validated Results

- **Deliverable.** `docs/sections/benchmark_runner_contract.md`: 564 lines, SHA-256 `2414f1dafef18c638d0c799c923e4700d35c3f9df9283868a048da9f4be63481`, the version Codex received. It is in English, in twelve sections:
  1. **Status and scope.** DEFERRED, with the future paths listed.
  2. **Location and layering.** `jepadrift/benchmark_runner.py` is a leaf module that imports only the standard library at module level.
     - Late imports, in order: `tools.freeze_config`, the numerical library, then the target.
     - The working directory must be ROOT; the ORIGIN mechanism is DEFERRED.
  3. **Command-line interface.** `main(argv=None) -> int` with `--config`, `--jobs` (default 1, outside the identity) and `--include-test-window`.
     - Extras must be exact qualified variants; managed flags are refused.
     - Exit codes are 0, 1, 2 or 3.
  4. **Target table.** Variants plus DEFERRED descriptors `protocol`, `data` and `reader`.
     - The candidates are UNQUALIFIED.
     - The PCA, `ca_tjepa` and `eurofidai_schema` configurations are refused.
     - `run.json` is a name reserved to the runner.
  5. **Refusal order.** Sixteen steps, split into pre-import and post-import, with bounded consistency, F's authentication limits and closed codes. IO is limited to the runner's own filesystem operations; target import or `main` exceptions are TARGET_FAILED.
  6. **Identity.** Schema `jepadrift-runner/1`: canonical JSON, a full 64-hex `run_id`, `run16` for directory names, a conservative hash over the whole policy, and BLAS and dtype. `protocol` and `data` are DEFERRED, and `authorization` and `provenance` sit outside `run_id`.
  7. **Outputs.** Namespaces `{results,figures,logs}/benchmark_runner/<target>/run-<run16>/`.
     - `run.json` lives in the results namespace and never hashes itself.
     - Completion requires a valid canonical manifest; no atomic publication is claimed.
     - There is no unified per-replication CSV.
  8. **Test-window chain** (2020+).
  9. **Future witness specification**, in classes P, Q, A and S.
  10. **Gates G1–G10.**
  11. **Three pending departures.**
  12. **Not-executed list.**
- **Worker shell and textual checks** (journal `logs/stream_21_R/doc-checks.md`, SHA-256 `8971d31384a832c0af99082700040ec56d901d8f2ec331f6cecefc60d2050f90`).
  - **Before the first write:** the plan, GO and `tools/freeze_config.py` hashes were as expected, the contract was absent, and the status listed only the two Codex files.
  - **First pass, 2026-11-08T00:32:17Z:** 19 PASS and 1 FAIL (C5, width). After the fix, 20 PASS at 00:33:34Z, on 545 lines with SHA-256 `fd47ab59c0e27b3e622a1b1a786d859525c4b791ef3348f38b24ff08572d4e15`.
  - **After the reception clarifications, 00:46:02Z:** 23 PASS.
    - C1–C14 cover:
      - the plan, GO and F pins;
      - twelve sections and width at most 120 bytes;
      - no private path, and the markers DEFERRED, UNQUALIFIED and pending present;
      - nine future paths, absent and declared;
      - no tracked change, with the exact three-file status;
      - 41 cited factual paths present;
      - J1 on disk and in the index with 47 CRLF, E3 and the PCA manifest;
      - ASCII except the title, and no FROZEN.
    - K1–K3 check the three clarifications.
  - **Before this file, 00:49:09Z:** the J1, E3, PCA and contract hashes were confirmed, and the runner and FROZEN were confirmed absent.
- **Codex independent read-only reception** (`logs/stream_21_R/codex-document-reception.md`). These are Codex results, reported as received.
  - Codex's own fresh shell checks passed: twelve sections, width, the exact three-file untracked perimeter, unchanged plan, GO and F pins, E2 disk, index and CRLF, E3 and the PCA manifest.
  - The independent reviewer confirmed that the eight prior findings were addressed and supported the targeted claims about producers and F.
  - Neither reviewer ran Python, imports, tests or data reads. Codex then received the final contract `2414f1da…`.
- **Limits of the evidence.**
  - C11 checks that each cited path exists. It does not check that each cited line range states what the contract says.
  - That correspondence rests on targeted reads at `47d85dc` and `26a2a56`, recorded in the native plan trace.
  - Two read-only re-verifications were added:
    - `tools/freeze_config.py:90-151`, for the reading semantics;
    - `rg '[!&*]' configs/*.yaml`, which found no match.
  - The future witnesses are a specification, not passing tests.
  - This lot ran no Python, project import, application test, `make`, computation, simulation or scientific execution.

## Errors and Dead Ends

- **Revision 0 gaps.** Codex returned a NO-GO; revision 1 resolved every point.
  1. **F API.** `check().files`, which is a count, was indexed as a mapping. It is replaced by a FROZEN snapshot whose byte hash must equal `freeze_id`; only `snapshot.files` and `snapshot.approval.sha256` are used.
  2. **Qualification.** Non-null names qualified a target while the identity fields `protocol` and `data` stayed null. They are replaced by DEFERRED descriptors: expected declarations, a reader that verifies before computing, and evidence at acceptance.
  3. **Numerical environment.** BLAS and dtype were missing from the identity. They are added, with the fingerprint limits.
  4. **Extras.** Qualification by arity is replaced by exact qualified variants.
  5. **Witnesses.** Fixed points:
     - the A1 suffix;
     - A4 commits that touched policy files such as `docs/manifests/d4_manifest.json`;
     - the separation of pre-import and post-import classes;
     - an over-broad invariance claim.
  6. **Helper and deviation entries.** A YAML-helper move into the runner, which contradicted its leaf status, and new entries in `docs/DEVIATIONS.md` were proposed. They are replaced by semantic reuse and by pending departures listed in the contract.
  7. **Working directory and code origin** (addendum). The working directory was not bound to ROOT and no code-origin rule existed. CWD and ORIGIN are added, the ORIGIN mechanism DEFERRED, and F's verifier, bytecode and runtime limits are stated.
  8. **Output creation** (addendum). The non-atomic creation of the three namespaces was not stated. It is now a post-import failure that retains the incomplete attempt.
- **Gap in the revision-0 regex.** The base check for YAML constructs did not match local tags (`!x`). `rg '[!&*]' configs/*.yaml` closed the gap with no match, before the final wording.
- **Width.** One contract line held 121 bytes, the C5 FAIL of the first pass. It was wrapped with a native edit and the full suite was rerun with every check passing.
- **Reception clarifications.** Three documentary imprecisions were corrected:
  - the placement and self-reference of `run.json`;
  - the broad phrase « any `OSError` », which contradicted target-failure handling;
  - an unaudited exclusivity claim about the Parquet bounded reader.
- **Monitor alert.** Codex inspected a false ready alert from the passive monitor. It is not evidence of delivery; it is reported here by Codex, not observed by the worker.
- **No runtime or scientific failure:** nothing was executed.

## Current State

- **Git.**
  - Branch `stream-21-R` at `26a2a5696a4412af8aceb6dbde3a9874e996aaad`, with no tracked modification. The worker made no commit, staging or Git mutation.
  - Status before this file: `?? docs/sections/benchmark_runner_contract.md`, `?? prompts/GO-stream-21-R.md`, `?? prompts/plans/plan-21-R.md`. This checkpoint adds `?? prompts/wrapups/wrapup-21-R.md`.
- **Four new deliverables before commit:** the contract (`2414f1da…`), the canonical plan (`0f838115…`), the GO (`0a4b0a46…`) and this checkpoint.
- **Ignored journals** in `logs/stream_21_R/`.
  - Codex-owned:
    - `mission-plan.md` `ec4060b4f6350f4ae59ddbebb8b5eb14c7a00f91bc8e178afedef395518900da`;
    - `codex-plan-review-v0.md` `75a886719f0ff048a3f93726af3e427eebc4b10b3e2570eb0acef75753bbaeac`;
    - `native-plan-v1.md` `f3493029b7f6ede5bff7bde8926d37b83324f173779fae7a61adaf804c74d200`;
    - `codex-document-reception.md` `8f848f6ed98351fb8b19505f885cfdbc1ac62ea23c369e5d09ec25a096b8a8e6`;
    - `wrapup-instructions.md` `c569fc9a4443dec90cf269356c0839555e2ccd26edeb9e859281e9966a59a5e6`.
  - Worker-owned: `doc-checks.md` `8971d31384a832c0af99082700040ec56d901d8f2ec331f6cecefc60d2050f90`, unchanged by this checkpoint.
  - The native plan file `~/.claude/plans/lis-logs-stream-21-r-mission-plan-md-et-distributed-alpaca.md` has SHA-256 `f3493029…`.
- **Protected hashes** (shell, 2026-11-08T00:49:09Z):
  - `results/e2/e2_cells.csv`: `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, on disk and in the index, 47 lines, 47 CRLF;
  - `results/e3/e3_overshoot.csv`: `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, D8 stays FAIL at +5.2833 %;
  - `results/pca_drift_benchmark/full_2000_20261101/manifest.json`: `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`;
  - `tools/freeze_config.py`: `6e17eea2a1d3b974d3452dc9fe9f9acc634a0cf96450104a02861b67354cf6a3`;
  - `tests/test_freeze_config.py`: `aa51cc0299a66a88012d443bfe844433d8655df25b25889b501fd019a4771ec3`.
- **Absent:** `configs/FROZEN.json`, `jepadrift/benchmark_runner.py`, `tools/benchmark_runner.py`, `tests/test_benchmark_runner.py`, and a `make freeze` target.
- **Environment.**
  - Inherited labels, not remeasured: Python 3.12.9 through the shared `.venv` built on the Trading 3.12.9 base; NumPy 2.4.4, SciPy 1.17.1, pandas 3.0.6 and PyYAML 6.0.3; torch 2.14.1 CPU through the conda-forge bridge.
  - Last suite count reported by Codex after the F publication: 1,193 PASS and 5 D4 skips.
  - Reported by the shell: git 2.51.1 on Linux.
- **Still owed by Codex.** None of these has been performed or is claimed:
  - the optional reception append to `docs/audits/streams_01_31_continuation_2026_11_07.md`;
  - the session `/exit` and a controlled shutdown;
  - the AST reindex without AI summaries;
  - the full `make check`;
  - the explicit staging of the four deliverables;
  - an anonymous Conventional Commit without trailer;
  - the range, size and private-path audit;
  - the rebase and push protocol, and the final reception.

## Vigilance Points

- **Production gates G1–G10 remain open:**
  - G1, the E5 protocol;
  - G2, the monitor and holdout semantics;
  - G3, bounded readers;
  - G4, verification of the consumed bytes;
  - G5, the J4 activation;
  - G6, targets for 2020+;
  - G7, the upstream streams 16, 17, 19 and 23;
  - G8, the pre-2020 mandate;
  - G9, the descriptor and evidence schemas;
  - G10, the numerical collection and ORIGIN mechanisms.
- **Effective freeze versus fixture verifier.** F's `write` stays guarded to temporary fixture repositories. A production freeze needs the J4 activation GO, which must also handle `pre_j4.frozen_json_present` and `tests/test_pca_drift_benchmark.py:719`.
- **Authority versus provenance.** Neither the presence of FROZEN, nor a protocol string, nor a hashed GO is ever authority. The approval is recorded and never interpreted.
- **Expected versus consumed data.**
  - The identity binds expected declarations.
  - Only a bounded reader that verifies the consumed bytes before computation, with evidence at acceptance, can close the data gap.
  - Manifest hashes do not verify data bytes.
- **Fingerprint limits.**
  - Version strings and lock hashes do not verify installed binaries.
  - The instruction set, the MKL code path, the OS, the kernel and the C library are not fingerprinted.
  - The bytecode cache, the trusted verifier and a hostile runtime remain outside authentication.
- **Dispatch prerequisites.** A qualified reader and the origin checks must precede any dispatch, and the working directory must equal ROOT.
- **Incomplete attempts.** The runner retains incomplete output attempts and never deletes them. Completion means a valid canonical `run.json`, not the mere presence of its pathname.
- **YAML.** `tools/appendix_b.py` is unchanged. Final decision: explicit anchors, aliases, tags and `%TAG` are refused, and implicit JSON-finite types are admitted.
- **PCA namespace.** `run_id` never replaces `run_fingerprint`, `selection_id`, `metric_id` or `null_calibration_id`. PCA is not a target and is never rerun.
- **Sealed results.** The J1 CRLF line ends must not be normalized, and E3/D8 stays FAIL. No source, configuration, paper or result change; no real FROZEN or J4.
- **Line references.** The contract's line references are valid at `26a2a56`; a later base change may shift them.
- **Prompt 22.** It expects `results/e5/J4_gate.txt` in a default directory, which conflicts with gate G1.

## Recommendations

- **Next authorized scope.** The one-question stream 19 documentary protocol. Scientific campaigns, the stream 23 migration and any rerun still need a dedicated researcher authorization.
- **Section 3 sources.** The four 21-S endpoints of `paper/sec3_theory.tex` line 111 remain UNSOURCED, and the mapping stays at 15/19.
- **Runner implementation.**
  - It needs its own plan and GO, once gates G1–G10 are resolved, starting from this contract.
  - The pending departures `C-runner-identity`, `C-runner-outputs` and `C-runner-freeze-required` enter `docs/DEVIATIONS.md` only with that implementation approval.
- **Witness order.** In that future lot, the schema-independent class P and S witnesses can come first; classes Q and A wait for the descriptor schema. The placement of the strict YAML loader is decided in that plan.
- **Delivered by this lot.** No new algorithm, test, producer or run.
