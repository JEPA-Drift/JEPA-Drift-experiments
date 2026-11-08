# Global benchmark runner (stream 21, lot R) — documentary contract

Proposed contract for the future module `jepadrift/benchmark_runner.py`. Authority: plan `prompts/plans/plan-21-R.md`
and the Codex GO under the delegated mandate `prompts/GO-stream-21-R.md`, both limited to this documentary lot. This
document grants no scientific authority, qualifies no target and authorizes no run.

## 1. Status and scope

- **Status: DEFERRED.** This is a contract only. No runner source, test, configuration, freeze file, freeze activation
  or run is created or authorized by this lot. The production runner waits for the E5 configurations and for the
  monitor and holdout semantics (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_07.md:117`; section 10).
- **Base.** Facts cite `file:line` at commit `26a2a5696a4412af8aceb6dbde3a9874e996aaad`. This commit adds seven files
  to `47d85dc`, namely the lot F deliverables and an inventory report, and modifies no existing file. Earlier line
  references to producers therefore remain valid.
- **Facts and proposals.** A sentence that cites `file:line` states a fact read at the base. Every other normative
  sentence from section 2 onwards is a proposal for a future implementation lot. Every candidate target is
  UNQUALIFIED. Every item marked DEFERRED is an unresolved, blocking gate, not a decision.
- **Future paths.** These paths are proposed or future and do not exist at the base: `jepadrift/benchmark_runner.py`,
  `tests/test_benchmark_runner.py`, `configs/FROZEN.json`, `results/benchmark_runner/`, `figures/benchmark_runner/`,
  `logs/benchmark_runner/`, `experiments/fake_target.py` (in temporary fixture repositories only) and
  `results/e5/J4_gate.txt`. `tools/benchmark_runner.py` is a rejected location and is never created.
- **Alignment without reuse of code.** The contract aligns with the published freeze verifier `tools/freeze_config.py`
  (lot 21-F, SHA-256 `6e17eea2a1d3b974d3452dc9fe9f9acc634a0cf96450104a02861b67354cf6a3`) and with the sealed identity
  of the stream 28 PCA runner. The PCA runner is not imported, copied or rerun
  (`docs/audits/streams_01_31_continuation_2026_11_07.md:76`).
- **Not a second benchmark.** The runner is a thin dispatcher to existing producer `main(argv)` functions. It ports no
  algorithm and computes no statistic.

## 2. Location and layering

Facts:
- **Requested location.** `jepadrift/benchmark_runner.py` is requested by
  `prompts/streams/prompt-21-freeze-runner.md:7-10`, `prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_07.md:117`
  and `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md:163`.
- **Callers.** `prompts/streams/prompt-22-e5.md:54-55` and `prompts/streams/prompt-25-e8.md:57` call
  `python -m jepadrift.benchmark_runner --config configs/<name>.yaml`, with `--quick` or `--include-test-window`.
- **The `tools/` proposal was never approved.** `tools/benchmark_runner.py` was proposed in
  `prompts/plans/plan-21-rest.md:354` (question Q11, `:542`).
  - The 21-rest GO kept lot R deferred (`prompts/GO-stream-21-rest.md:12`).
  - Lot F removed that path from its policy because the location was undecided (`prompts/plans/plan-21-F.md:38`).
  - The frozen policy v1 covers `jepadrift/`, but under `tools/` only `tools/freeze_config.py`
    (`tools/freeze_config.py:29-31`; `prompts/plans/plan-21-F.md:518`). A runner under `tools/` would need a policy
    v2, hence a new verifier.
- **Current imports.** At the base, no module of `jepadrift/` imports `experiments` or `tools`. `experiments/` and
  `tools/` have no `__init__.py`, and `jepadrift/__init__.py` is empty.

Proposals:
- **One leaf module.** The runner is `jepadrift/benchmark_runner.py`, run as `python -m jepadrift.benchmark_runner`.
  - It is a leaf: no `jepadrift` module imports it.
  - There is no `tools/` shim, no second module, no wrapper layer, no loader abstraction and no process-global
    `chdir`.
- **Late imports.** Module-level imports are standard library only. Imports inside `main` happen in this order:
  1. `tools.freeze_config`, after the static gates;
  2. the numerical library, after the freeze and qualification gates;
  3. the target module, last.

  This confines the library-to-`experiments` inversion noted in `prompts/plans/plan-21-rest.md:354` to late imports.
- **Working directory.** The actual working directory must be ROOT, compared as `(st_dev, st_ino)`; otherwise the
  runner refuses with CWD before any target import.
  - Forwarded paths are relative to ROOT.
  - Producers resolve `--config`, `--out`, `--fig-dir` and `--log-dir` against the working directory
    (`experiments/e1_problem.py:1173-1175`, `experiments/e3_calibration.py:951`, `experiments/e10_robustness.py:750`).
  - They reach their other inputs through `REPO_ROOT`, derived from their own `__file__`
    (`experiments/e1_problem.py:62`, `experiments/e3_calibration.py:62`).
- **Code origin.** A fixed module name does not guarantee where the code comes from.
  - The target's resolved origin must be its declared frozen source file under ROOT, listed in the FROZEN snapshot
    (section 5, step 9).
  - A preloaded target (already in `sys.modules`) or a target of foreign origin is refused with ORIGIN before any of
    its code executes.
  - A working-directory check alone does not prevent substitution through the import search path or the bytecode
    cache.
  - The exact origin mechanism is DEFERRED to the implementation plan (gate G10).
- **Strict YAML intake.** This reuses the semantics of the existing strict-loader contract of `tools/appendix_b.py`,
  which refuses:
  - keys of one mapping that are equal by constructed value (`tools/appendix_b.py:54-61`);
  - non-finite or non-JSON values (`:64-83`);
  - cyclic sections (`:95-98`).
- **Restriction for this runner.** The runner refuses explicit anchors, aliases and tags, including standard tags such
  as `!!str`, local tags and `%TAG` directives, with CONFIG before any target import.
  - The refusal concerns syntactic constructs, not a character inside a literal string.
  - Implicit types remain admissible when the constructed document has distinct string keys and finite JSON values.
  - Duplicates, merge keys, cycles and non-JSON values stay refused.
- **No loader change in this lot.** No loader is written or moved, and `tools/appendix_b.py` is unchanged; its finite
  alias reuse remains accepted there. Code placement belongs to a future implementation plan.
- **Current configurations.** At the base, `configs/*.yaml` contain no anchor, alias, tag or unquoted date, and the
  largest file holds 1,582 bytes.

## 3. Command-line interface

Proposals:
- **Signature.** `main(argv=None) -> int`, parsed by argparse with `allow_abbrev=False`. Each runner option appears at
  most once; a repeat, including a `--option=value` spelling, is a usage error.
- **Runner options.**
  - `--config PATH` (required): canonical relative POSIX path of the form `configs/<name>.yaml`.
  - `--jobs N` (integer >= 1, default 1): resource flag, forwarded to the target and excluded from the identity.
  - `--include-test-window`: requests the test-window path (section 8).
- **Scientific extras.** All remaining tokens, with no bare separator, are scientific extras. They must equal, token
  for token and in order, one qualified variant of the target (section 4). Arity alone qualifies no value.
- **Managed producer flags.** These are refused in the extras with an explicit ARGV diagnostic, including their
  `--flag=value` spellings: `--config`, `--out`, `--output-dir`, `--fig-dir`, `--log-dir`, `--jobs`,
  `--include-test-window`, `--resume`, `--seed` and `--mode`.
- **Other mismatches are also ARGV:** an unknown or abbreviated token, a different order, an unqualified value, a
  bare `--` or a stray positional.
- **Forwarded argv.** The exact order is `--config <config> --out <R> --fig-dir <F> --log-dir <L> --jobs <N>`, then
  the variant tokens, then `--include-test-window` only when the target is qualified for it. `<R>`, `<F>` and `<L>`
  are the run namespaces of section 7, relative to ROOT.
- **Exit status.**

  | Code | Meaning |
  |---|---|
  | 0 | Completed run; `run.json` written last. |
  | 1 | Refusal, printed as one line `benchmark-runner: error: CODE: detail`. |
  | 2 | Usage error (argparse). |
  | 3 | TARGET_FAILED, see below. No `run.json` is written. |

  TARGET_FAILED covers a failed import attempt, a non-zero target status, and a `SystemExit` or any other exception
  raised during the target import or the target `main`, `OSError` included. The detail carries the target status.

Facts:
- **Producer conventions.** E1, E3 and E10 return 0 from `main(argv=None)` on success (`experiments/e1_problem.py:1251`,
  `experiments/e3_calibration.py:1156`, `experiments/e10_robustness.py:871`).
  - They refuse through `ap.error`, that is `SystemExit(2)` (`experiments/e1_problem.py:1198-1199`,
    `experiments/e10_robustness.py:743-746`; pinned by `tests/test_e1.py:59-62`).
  - Their other failures raise.
- **Jobs.** Producer outputs are pinned as independent of `--jobs` by `tests/test_e1.py:172-187`,
  `tests/test_e3.py:335-347` and `tests/test_e10.py:188-195`. Their own defaults differ: 24, 24 and `os.cpu_count()`
  (`experiments/e10_robustness.py:741`).
- **PCA runner.** The sealed PCA runner exits with 0, 2 or 3 (`docs/sections/pca_drift_benchmark.md:424-425`). It is
  not a target.

## 4. Target table and qualification

Proposals:
- **`TARGETS`.** A module constant, hence frozen code under the `jepadrift` policy root. Each entry has these fields:
  - `module` and `config`;
  - `variants`: a list of `{argv, outputs, expected_sha256}`, where `argv` is an exact token list, `outputs` is
    `{results: [...], figures: [...], logs: [...]}` and `expected_sha256` maps a relative output path to its digest;
  - `protocol`, `data` and `reader`, the DEFERRED descriptors below;
  - `test_window`, a boolean.
- **Variants.** A variant fixes the accepted resolved option values and the exact output set of that variant, for
  example the values of `--quick`, `--arms`, `--stage` and `--families`. Output names are unique within a variant.
  The name `run.json` in the results namespace is reserved to the runner: no variant may declare it, and it never
  belongs to a variant's output set (section 7).
- **DEFERRED descriptors (gate G9, blocking).**
  - `protocol`: an approved, immutable protocol descriptor, holdout included, whose bytes are pinned by the freeze.
  - `data`: expected dataset and segment declarations with their expected digests. These are declarations, not
    digests observed by the runner.
  - `reader`: a bounded reader owned by the target. It reads only the declared segments and verifies the exact bytes
    it consumes against `data` before any scientific computation. It produces evidence that is required at final
    acceptance.

  Their production schema, the format of the evidence and the qualification evidence are not decided here.
- **Qualification.** A target qualifies only with all of the following:
  - an exact variant match;
  - `protocol`, `data` and `reader` bound to descriptors that conform to the approved schema;
  - the qualification evidence.

  A non-empty string, a hashed GO document or the presence of `configs/FROZEN.json` is not authority and qualifies
  nothing. No completed production run and no accepted fake positive may use null descriptors.
- **Candidate rows.** These are examples, all UNQUALIFIED: no variant, null descriptors, `test_window` false.

  | Name | Module | Config |
  |---|---|---|
  | e1 | `experiments.e1_problem` | `configs/e1.yaml` |
  | e3 | `experiments.e3_calibration` | `configs/e3.yaml` |
  | e10 | `experiments.e10_robustness` | `configs/e10.yaml` |

  - No value of `--quick`, `--arms`, `--stage` or `--families` is qualified; only an approved protocol can fix them.
  - No claim is made of an equal-FPR P4-D comparator or of a trained P5 representation. E10 itself refuses
    `--stage jepa` and `F2` (`experiments/e10_robustness.py:743-746`).
- **Refused configurations (TARGET).**
  - `configs/pca_drift_benchmark.yaml` and `configs/pca_drift_benchmark_full_2000_resources.yaml`: sealed PCA runner,
    not a target.
  - `configs/ca_tjepa.yaml`: training.
  - `configs/eurofidai_schema.yaml`: loader schema.

  E2 (no `--config`, J1 sealed) and `experiments/jepa_pretrain.py` are not in the table.

## 5. Refusal order

Proposals. Steps 1 to 12, and the ORIGIN check of step 13, run before any target import or execution:
1. **ENV.** The six variables `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`,
   `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and `MPLBACKEND=Agg` must hold their values.
   - They are captured when the runner module is imported, before any non-standard-library import.
   - An absent or different value is refused, never defaulted.
2. **Usage.** argparse errors exit with 2.
3. **CWD.** The actual working directory must be ROOT.
4. **LINK or CONFIG.** The configuration path must be canonical, under `configs/`, with portable components.
   - It is opened without following a link at any component.
   - It must be a regular file of at most 1 MiB.
5. **TARGET.** The configuration must be listed in `TARGETS`.
6. **ARGV.** The extras must equal a qualified variant, and managed flags are refused (section 3).
7. **CONFIG.** Strict YAML (section 2): a mapping root, distinct string keys and finite JSON values.
8. **PROTOCOL, DATA, READER or TARGET.** The DEFERRED descriptors must be qualified. The test window is accepted only
   when `test_window` is true.
9. **FREEZE.** Call `check(ROOT)` from `tools/freeze_config.py:353-388`; the published API is unchanged.
   - It returns `{commit, seal, approval, files, freeze_id}`, where `files` is a count.
   - Next, read a snapshot of `configs/FROZEN.json` with the semantics of `_read_frozen`
     (`tools/freeze_config.py:136-151`): no link at any component, a regular file of at most 1 MiB.
   - Require the SHA-256 of the snapshot bytes to equal `freeze_id`, then parse the snapshot strictly (`:182-203`).
   - Use only `snapshot.files` (a mapping) and `snapshot.approval.sha256`.
   - `snapshot.files[<config path>]` must equal the SHA-256 of the bytes read at step 4, and every descriptor file
     must appear in `snapshot.files` with an equal digest.
   - A `FreezeError` surfaces as `FREEZE: <F code>: <detail>`.
10. **ENV, numerical.** Import the numerical library only, without the target, and collect the BLAS and dtype
    descriptors for the identity. Collection and verification are DEFERRED (gate G10).
11. **Identity.** Compute the identity and `run_id` (section 6).
12. **LINK or EXISTS, preflight.** The three parents are checked:
    - `results/benchmark_runner/<target>/`;
    - `figures/benchmark_runner/<target>/`;
    - `logs/benchmark_runner/<target>/`.

    Each must be a real directory reached without links, and the three `run-<run16>` names must be absent. Nothing is
    created at this step.
13. **ORIGIN, then TARGET_FAILED.** The resolved origin must equal the declared frozen source file, and the target
    must not be preloaded. This is checked before any target code executes; the mechanism is DEFERRED. Then the
    import is attempted; a failed attempt exits with 3, with nothing created.
14. **EXISTS, post-import.** Create the three run directories exclusively, in the order results, figures, logs.
15. **Dispatch.** Call the target `main(argv)`.
16. **TARGET_FAILED, FREEZE, OUTPUTS or DATA.**
    - The target status must be 0, else exit 3.
    - A second `check(ROOT)` must return the same `freeze_id`.
    - The outputs must be exactly the variant's set, with the declared `expected_sha256`.
    - The reader evidence must match (format DEFERRED).
    - `run.json` is then created exclusively in the results namespace, last (section 7).

Notes:
- **Before the target.** No pre-import refusal imports or executes the target, creates a namespace or accesses data.
  The runner itself never opens a data file.
  - Producers overwrite the thread variables when they are imported (`experiments/e1_problem.py:21-26`,
    `experiments/e3_calibration.py:24-29`, `experiments/e10_robustness.py:25-30`). The ENV check therefore precedes
    any target import, following `experiments/pca_drift_benchmark.py:12-17`.
  - `PYTHONHASHSEED` takes effect only at interpreter start.
- **Post-import failures.** These are a failed import attempt and failures at steps 14 to 16.
  - No `run.json` is written and nothing is deleted.
  - A collision at the second or third directory leaves the directories already created by this attempt. They are
    retained as an incomplete attempt.
  - A foreign or partial namespace is never deleted.
  - This phase makes no all-or-nothing or no-side-effect claim. A successful run writes `run.json` last.
- **Bounded consistency, not an atomic transaction.** The matched snapshot read and the second `check()` bound these
  gaps without closing them:
  - between check and read;
  - between read and import;
  - during the run;
  - a modify-then-restore sequence.

  The limits of lot F apply (`prompts/plans/plan-21-F.md:508-521`): hard links, substitution of the root path, and a
  trusted local history and verifier.
- **Trust assumptions.** The qualified target code is trusted and the workspace is controlled. The runner is not an
  operating-system sandbox and keeps no filesystem snapshot.
- **Authentication limits retained from F.**
  - The verifier is trusted; a modified verifier can lie.
  - The bytecode cache (`__pycache__`) is not covered.
  - A hostile runtime is not detected: `sitecustomize`, `.pth` files, preloaded or modified modules.
  - A filesystem hash does not authenticate arbitrary Python runtime state.
- **Freeze and approval.** The mere presence of `configs/FROZEN.json` unlocks nothing; a passing `check()` plus
  qualification is required.
  - The approval document is recorded as hashed provenance and never interpreted. Reading a GO document does not
    authenticate scientific authority.
  - The runner never calls `write`, never changes the two fixture guards of `tools/freeze_config.py:420-464` and never
    creates a freeze file.
- **Closed refusal codes.** ENV, CWD, ARGV, CONFIG, LINK, TARGET, PROTOCOL, DATA, READER, FREEZE, ORIGIN, EXISTS,
  OUTPUTS and IO. TARGET_FAILED is exit status 3.
  - IO covers an `OSError` raised by the runner's own filesystem operations that no more specific code covers.
  - An exception raised during the target import or the target `main`, `OSError` included, is TARGET_FAILED (exit 3),
    never IO.
  - Specific refusals keep their stated semantics. FREEZE wraps every `FreezeError` of lot F, its own IO code
    included, and EXISTS reports an existing namespace.

## 6. Identity, authorization and provenance

Proposed identity payload. Values in angle brackets are placeholders, not values:

```
{"schema": "jepadrift-runner/1",
 "target": <name>,
 "config": {"path": "configs/<name>.yaml", "sha256": <sha256>},
 "argv": [<token>, ...],
 "test_window": false,
 "policy_files_sha256": <sha256 of canon(snapshot.files)>,
 "environment": {"python": <x.y.z>,
                 "packages": {<distribution>: <version>},
                 "numeric": {"blas": <qualified descriptor>, "dtype": "float64"},
                 "variables": {"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                               "MKL_CBWR": "COMPATIBLE", "PYTHONHASHSEED": "42", "MPLBACKEND": "Agg"}},
 "protocol": <DEFERRED: approved descriptor bound to frozen bytes>,
 "data": <DEFERRED: expected segment declarations bound to frozen bytes>}
```

- **Canonical form.** `canon(x) = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
  allow_nan=False)`, encoded as ASCII. The identity holds no float.
  - It is F's `_canonical` without its final newline (`tools/freeze_config.py:165-168`).
  - It is also the PCA `canon` (`experiments/pca_drift_benchmark.py:420-422`) with `allow_nan=False`.
- **`run_id`.** The full SHA-256 hex digest (64 characters) of `canon(identity)`, recorded in `run.json`.
  `run16 = run_id[:16]` is used only in directory names, following the PCA `sha16` prefix
  (`experiments/pca_drift_benchmark.py:425-427`).
- **Conservative scope.** `policy_files_sha256` hashes the whole policy mapping of lot F, that is every file under the
  eleven roots of `tools/freeze_config.py:29-31`:
  - all configurations, unrelated ones and resource overlays included;
  - `experiments/` and `jepadrift/`;
  - the lock files and both manifests;
  - `Makefile`, `conftest.py` and `tools/freeze_config.py`.

  Any byte change there changes `run_id`; F already refuses such a change after the seal. The only resource
  invariance promised is to the excluded `--jobs` value. No invariance to resource overlays inside the policy is
  promised.
- **Outside the identity by construction.**
  - `--jobs`, timestamps and durations.
  - Output paths and absolute paths.
  - Git HEAD, branch and working-tree state.
  - The freeze commit C, the seal S and the approval document.
  - The host name.
- **`authorization`.** Stored in `run.json`, outside `run_id`, and verified before and after the run. It holds the
  `check()` result `{commit, seal, approval, files, freeze_id}` plus `snapshot.approval.sha256`.
- **`provenance`.** Stored in `run.json`, outside `run_id`. It holds:
  - HEAD, read by isolated Git plumbing as in lot F;
  - `jobs`;
  - the normalized command with the placeholders `<RESULTS>`, `<FIGURES>` and `<LOGS>`, following
    `experiments/pca_drift_benchmark.py:744-752` and `:1857-1860`.

How the identity relates to the inputs:
- **Code, configurations and manifests.** Their bytes are pinned by `snapshot.files` and verified on disk by `check()`
  before and after the run, within the bounds of section 5. `config` repeats the selected configuration to name the
  input.
- **Environment.** Lot F does not cover it (`prompts/plans/plan-21-F.md:509`). The identity records Python, the
  distribution versions read from package metadata, the qualified numerical descriptors and the six variables. BLAS
  and dtype follow the PCA precedent (`experiments/pca_drift_benchmark.py:726-741`).
  - Version strings and the hash of a dependency lock do not verify installed binary bytes: `site-packages`, `.venv`,
    the torch bridge, the BLAS and OpenMP libraries.
  - These are not fingerprinted: the instruction set and MKL code path beyond `MKL_CBWR=COMPATIBLE`, the operating
    system, the kernel and the C library.
  - The exact safe collection and verification are DEFERRED (gate G10).
- **Approval.** Recorded in `authorization` only, never in `run_id`, never interpreted.
- **Data.** Hashing a manifest pins the declared digests, not the bytes of the data files.
  - Lot F reads no data file (`tools/freeze_config.py:38-40`).
  - A targeted, non-exhaustive search found no load-time verification of data bytes against
    `data/derived/MANIFEST.json` (`prompts/plans/plan-21-rest.md:483`). E3 and E10 log a `ret_wide.npy` digest, which
    records without verifying.
  - Before dispatch, `identity.data` binds expected declarations, not observed digests. The bounded reader verifies
    those bytes before computation, and matching evidence is required at final acceptance (DEFERRED).
  - The runner's refusal to open return data supplies no such evidence.
  - No proprietary path or content enters the identity, `run.json` or the logs written by the runner.
- **PCA identifiers.** The sealed PCA identity (`docs/sections/pca_drift_benchmark.md:37-52`; identifiers at
  `:67-76`) keeps its own namespace.
  - The runner uses the schema tag `jepadrift-runner/1` and the key `run_id`, never `run_fingerprint`,
    `selection_id`, `metric_id` or `null_calibration_id`.
  - It never recomputes, rewrites or imports those identifiers, and the PCA runner is not a target.
  - A manifest written by a target is an output file hashed like any other.

## 7. Output namespaces and validation

Facts:
- **Overwrites.** Producers create their output directories with `exist_ok=True` and overwrite files
  (`experiments/e1_problem.py:1204-1205`, `experiments/e3_calibration.py:1104-1109`,
  `experiments/e10_robustness.py:840-845`).
- **Stale files.** E1 `plot()` reads CSV files already present in `--out` (`experiments/e1_problem.py:1122-1154`).
- **Aggregates only.** The producers write cell aggregates (`experiments/e1_problem.py:77-83`,
  `experiments/e3_calibration.py:78-96`, `experiments/e10_robustness.py:842-845`). No per-replication row exists on
  disk.

Proposals:
- **Namespaces.**
  - `results/benchmark_runner/<target>/run-<run16>/`;
  - `figures/benchmark_runner/<target>/run-<run16>/`;
  - `logs/benchmark_runner/<target>/run-<run16>/`.

  Never a producer default directory, and never `results/pca_drift_benchmark/`.
- **Creation.** Sequential and non-atomic, after the target import (section 5, step 14).
- **Validation after target status 0.**
  - Each namespace holds exactly the regular files declared by the qualified variant. A missing or extra file, a
    subdirectory or a link is OUTPUTS.
  - The reserved `run.json` is not part of that set. A file of that name written by the target is an extra output,
    hence OUTPUTS.
  - Declared `expected_sha256` values are compared. A mismatch is a scientific reproduction divergence (D3): stop and
    report, never change code or parameters to obtain a match.
  - Logs and figures are hashed and recorded, never compared. Logs hold durations and, for E3, Git HEAD
    (`experiments/e3_calibration.py:1113`).
  - The reader evidence must match `data`, else DATA (format DEFERRED).
- **`run.json`.** The manifest lives at `<results namespace>/run.json`, a name reserved to the runner. It holds
  canonical bytes plus a final newline, in F's `_canonical` form:
  `{schema, run_id, identity, authorization, provenance, exit_code, outputs: {relative path: {sha256, bytes}}}`.
  - `outputs` maps the files declared by the variant in the three namespaces. It excludes `run.json` itself, so the
    manifest never hashes itself.
  - It is created exclusively, without following links, and last, as the PCA manifest is written last
    (`docs/sections/pca_drift_benchmark.md:30-33`). No atomic publication is claimed.
  - Completion requires a valid canonical manifest, not the mere presence of the pathname:
    - its bytes are canonical;
    - its `identity` recomputes to `run_id`, and the namespace suffix equals `run_id[:16]`;
    - its `outputs` digests match the files on disk.
  - A namespace without such a manifest is an incomplete attempt.
  - The runner never overwrites, resumes or deletes anything. Removing an incomplete namespace is a human decision
    made outside the runner.
- **No unified per-replication CSV.** Prompt 21 asks for `results/<stream>/<run_hash>.csv` with one row per
  replication (`prompts/streams/prompt-21-freeze-runner.md:10`). The runner keeps the producers' files and derives no
  row (departure `C-runner-outputs`, section 11).
- **Consumer conflict.** Prompt 22 reads `results/e5/J4_gate.txt` in a default directory
  (`prompts/streams/prompt-22-e5.md:55`). This conflicts with exclusive namespaces and is left to gate G1.

## 8. Test-window path (2020+)

Facts:
- **Guards.** Every current guard refuses unconditionally and reads no freeze file:
  - E1 `check_window` (`experiments/e1_problem.py:96-100`) and its `--include-test-window` refusal (`:1196-1199`);
  - E3 (`experiments/e3_calibration.py:109-113`);
  - E10 (`experiments/e10_robustness.py:317-320`);
  - PCA (`experiments/pca_drift_benchmark.py:694-697`).
- **Unbounded loaders.** The producer loaders read the whole panel through `DATASETS`
  (`jepadrift/representations/extract.py:34-35`) before slicing the pre-monitor rows
  (`experiments/e1_problem.py:103-111`, `experiments/e3_calibration.py:117-130`,
  `experiments/e10_robustness.py:324-334`). None is bounded before I/O.
- **PCA reader.** It hashes whole files, 2020+ bytes included, before slicing a memmap
  (`experiments/pca_drift_benchmark.py:1359-1388`).
- **Bounded precedent.** The only bounded precedent identified in this lot is the Parquet row-group reader of
  `docs/DEVIATIONS.md:750-759` (C-jepa-d3-reader). That reader is established, but no repository-wide audit for
  other bounded readers was made, so no exclusivity is claimed.

Proposals:
- **Required chain, in order.**
  1. `--include-test-window`.
  2. A new target, frozen under its own GO, that declares `test_window`.
  3. A qualified variant and qualified descriptors, including a reader bounded before return I/O.
  4. A passing production `check()`.
  5. Only then the import.
- **Target guards.** They stay unchanged and remain the last barrier; the runner never patches them.
- **Today.** No target declares `test_window`; E1 refuses the flag itself, and E3 and E10 lack it. Every request is
  refused at step 8 at the latest. This contract leads to no 2020+ row read, J4 activation, freeze or E5 run. The J4
  date grants nothing.

## 9. Future witnesses (test specification)

This is a test specification for a future implementation lot. None of these witnesses exists or has been run.

- **Setup.**
  - One temporary Git repository per test, holding the policy roots, a fake target `experiments/fake_target.py`
    frozen with the fixture, and synthetic configurations.
  - FROZEN is created by `freeze_config.write`, which lot F allows only under the temporary directory, then sealed by
    a commit S.
  - `ROOT` and `TARGETS` are injected, and an import spy watches the target.
  - Every positive witness runs with the fixture ROOT as working directory.
  - No real data and no project experiment are imported.
- **Schema dependency.** Every witness that reaches step 9 needs a qualified fixture target whose descriptors conform
  to the approved schema (gate G9), never null placeholders. Such witnesses are specified now and can be written only
  once that schema exists.
- **Class P, pre-import refusals.** Each exits with 1 or 2 and prints a single message; the target is not imported
  and no namespace is created.
  - **ENV:** each of the six variables, absent or different.
  - **Usage:** `--config` missing or repeated; `--jobs 0`.
  - **CWD:** working directory in a copy of ROOT. A symbolic path to ROOT itself is accepted.
  - **LINK and CONFIG paths:** absolute path; `..`, `./` or `//`; outside `configs/`; linked file; linked `configs/`;
    FIFO; more than 1 MiB.
  - **CONFIG YAML:**
    - invalid YAML;
    - duplicate keys, including `0x10` versus `16` and `yes` versus `true`;
    - a merge key;
    - an anchor, an alias, an explicit tag (`!!str` or a local tag) or a `%TAG` directive;
    - NaN or infinity;
    - a non-mapping root.

    `&`, `*` or `!` inside a quoted literal string is accepted.
  - **TARGET:** unknown configuration; PCA configurations; test window not declared.
  - **ARGV:** each managed flag and its `=` spelling; abbreviation; unknown token; different order; unqualified value;
    bare `--`.
  - **PROTOCOL, DATA and READER:** null descriptors; the candidate rows e1, e3 and e10.
  - **After the schema exists:**
    - **FREEZE:** FROZEN absent; one byte changed (HASH); a commit touching `jepadrift/` (CHANGED); FROZEN replaced
      between `check()` and the snapshot read; configuration bytes differing from `snapshot.files`.
    - **Numerical ENV.**
    - **Preflight EXISTS:** each namespace present, even empty; a linked parent.
    - **ORIGIN:** a target preloaded in `sys.modules`, even from ROOT; a resolution outside ROOT through an earlier
      search-path entry. In both cases no target code executes.
- **Class Q, post-import failures and races.** These require the schema. The import was attempted, no `run.json` is
  written and nothing is deleted.
  - **Import failure:** exit 3, no namespace.
  - **Collision at the second or third directory:** EXISTS; the earlier directories of the attempt are retained.
  - **Target failure:** the target returns 1, raises or calls `ap.error`; exit 3.
  - **OUTPUTS:** a missing, extra, subdirectory, linked or wrong-hash output, including a `run.json` written by the
    target.
  - **DATA:** absent or mismatching reader evidence. Verifying before computing is a property of the reader, shown by
    its own qualification witnesses (DEFERRED); the runner checks only the final evidence.
  - **FREEZE:** a policy file changed by the target, caught by the second `check()`.
- **Class A, acceptance.** These require the schema.
  - **A1:** three directories, and `run.json` written last. It holds the full 64-character `run_id`, the directory
    suffix equals `run_id[:16]`, and `sha256(canon(identity))` equals `run_id`. Its `outputs` map excludes
    `run.json` and matches the files on disk. The forwarded argv is exact, and the working directory is the fixture
    ROOT.
  - **A2:** equal inputs give byte-identical identities. `--jobs 1` and `--jobs 2` give the same `run_id`; this is the
    only invariance promised.
  - **A3:** another qualified variant gives another `run_id`.
  - **A4:** a commit after S touching only paths outside the policy and outside the approval document (for example
    `results/` or `paper/`) keeps `run_id` and changes `provenance.head`.
    - Lot F refuses any policy change, `docs/manifests/d4_manifest.json` and resource overlays included.
    - No invariance to such a change is claimed.
- **Class S, static.**
  - Module-level imports are standard library only, and no `jepadrift` module imports the runner.
  - There is no `os.chdir` call.
  - There is no PCA entry. No variant holds a managed flag or declares the reserved `run.json`.
  - All current candidates are UNQUALIFIED.
  - `run.json` holds no absolute path and no fixture root.

## 10. Unresolved gates

Every gate below blocks a production implementation. None is resolved by this contract.
- **G1. E5 protocol (stream 22).**
  - No E5 configuration exists at the base.
  - Variants and output sets.
  - Placement of `results/e5/J4_gate.txt` inside the runner namespaces.
- **G2. Monitor and holdout semantics.**
  - The window from 2020-01-01 with the 65-session embargo.
  - Holdout segments and their use.
  - The standard and retrospective Covid cohorts (C-pca-covid-retrospective).
  - Readings at the horizon H; ARL0 readings restricted to E2 and E3.
- **G3. Bounded readers.** A reader bounded before I/O for each real dataset, with segment digests in the manifests.
- **G4. Byte verification.** Verification of the consumed bytes at load.
- **G5. J4 activation under a researcher GO.**
  - The approval document is named.
  - Code, configurations and qualified targets are committed in C.
  - F's two write guards are replaced.
  - `pre_j4.frozen_json_present` and `tests/test_pca_drift_benchmark.py:719` are handled
    (`prompts/wrapups/wrapup-21-F.md:152`).
  - A `make freeze` target is added.
- **G6. 2020+ targets.** E5 and E8 as new frozen code (`prompts/streams/prompt-22-e5.md:17`,
  `prompts/streams/prompt-25-e8.md:20`). The E1, E3 and E10 guards stay unchanged.
- **G7. Upstream dependencies.** Stream 16; stream 17 in receivable state; stream 19 if required; phase 2 of stream 23
  (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_07.md:146`).
- **G8. Pre-2020 mandate.** A real pre-2020 mandate for any E1, E3 or E10 reproduction through the runner.
  - This includes the prompt 21 criterion on `results/e1/e1_cells.csv`
    (`prompts/streams/prompt-21-freeze-runner.md:32`).
  - The reference digest prefix is `9ae7e261` (`prompts/plans/plan-21-rest.md:392`).
- **G9. Production formats (E5).** The schemas of the `protocol` and `data` descriptors, the format of the reader
  evidence and the qualification evidence.
- **G10. Implementation-plan methods.**
  - Safe collection and verification of the numerical descriptors.
  - The distribution list, with torch for E5.
  - The ORIGIN mechanism against preloading and against search-path and bytecode-cache substitution.

## 11. Proposed departures (pending)

These departures are pending future implementation approval. This lot does not record them in `docs/DEVIATIONS.md`,
and none is active.
- **`C-runner-identity`.** `run_id` excludes the Git commit and the approval document. Prompt 21 defines `run_hash`
  over the canonical configuration, the Git commit and the manifest digests
  (`prompts/streams/prompt-21-freeze-runner.md:9`).
- **`C-runner-outputs`.** Per-run directory namespaces hold the producers' files. Prompt 21 asks instead for
  `results/<stream>/<run_hash>.csv` with one row per replication (`prompts/streams/prompt-21-freeze-runner.md:10`).
- **`C-runner-freeze-required`.** Every dispatch, pre-2020 included, requires a valid effective freeze (Codex
  arbitration Q1). Prompt 21 ties only the test window to the freeze (`prompts/streams/prompt-21-freeze-runner.md:13`).

## 12. Not executed

- **Created by this lot.** No runner source, test, fixture, configuration, freeze file, `make freeze` target, J4
  activation or E5 configuration.
- **Not run or read.** No E1, E2, E3, E4, E6, D6 or PCA run; no JEPA or VAE training; no simulation; no read of
  returns, 2020+ rows or proprietary data.
- **How this document was written.** No Python, import, test or computation; the checks were textual and shell only.
- **Sealed artifacts unchanged.**
  - `results/e2/e2_cells.csv`, SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, with 47
    CRLF line ends.
  - `results/e3/e3_overshoot.csv`, SHA-256 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`; D8
    stays FAIL.
  - `results/pca_drift_benchmark/full_2000_20261101/manifest.json`, SHA-256
    `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`.
  - Upstream PCA identities and outputs are untouched.
- **Not changed.** `docs/DEVIATIONS.md`, `docs/MAPPING.md`, `tools/appendix_b.py`, and every other source,
  configuration, dependency and memory file.
