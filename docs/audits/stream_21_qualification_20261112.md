# Stream 21 qualification gaps (2026-11-12): targets e1, e3, e10

Documentary map of what blocks the qualification of the candidate runner targets. Authority: the Codex
documentary GO (`prompts/GO-stream-21-qualification-20261112.md:5`) on the canonical plan, whose GO decision
prevails over the native proposal (`prompts/plans/plan-21-qualification-20261112.md:132-148`), and the amendment
(`prompts/GO-stream-21-qualification-20261112-amendment.md:3`, `:9-11`). This document grants no scientific
authority, qualifies no target, closes no gate and authorizes no run.

## 1. Status, authority and evidence rules
- **Status.** The production runner stays DEFERRED (`docs/sections/benchmark_runner_contract.md:9-11`).
  Candidates e1, e3 and e10 stay UNQUALIFIED (`:160-170`); gates G1-G10 all stay OPEN (`:500-534`); Q1-Q7 of
  section 7 stay OPEN (`prompts/plans/plan-21-qualification-20261112.md:136`).
- **Base.** Facts cite `file:line` read at `891cfa5f56c8ec20988f9a18efef4ed468e1c720`; `:N` repeats the last file
  cited in the same bullet; shell observations are labelled and replayed in the worker journal. Pinned: contract
  `2414f1da...3481` and `tools/freeze_config.py` `6e17eea2...f6a3` (`prompts/wrapups/wrapup-21-R.md:32`, `:126`).
- **Evidence rules.** Manifest digests are declared values, never consumed bytes; no data file, `.npy` header or
  Parquet metadata was opened. Every schema, witness and fixture below is PROPOSED / NOT EXECUTED.
- **Distinctions kept.** Declared versus consumed data; approval provenance versus authority; byte verification
  versus scientific qualification; the three failure phases of section 3.4. No OS sandbox or atomic transaction
  is promised (`docs/sections/benchmark_runner_contract.md:240-255`). The four UNSOURCED section 3 endpoints are
  out of scope (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_12.md:125`).

## 2. Cross-cutting facts
- **Freeze verifier.** `check()` returns `files` as a count, with `freeze_id` (`tools/freeze_config.py:382-383`);
  the FROZEN record holds `files` as a mapping (`:452-453`). A passing check reads no data file and authorizes no
  run (`:38-40`). POLICY has eleven roots: no `results/` path and no data file besides
  `data/derived/MANIFEST.json` (`:29-31`). The two fixture write guards stay unchanged (`:426-429`, `:433-435`).
- **Loaders.** `DATASETS` maps d2_us97 and d3_239 to whole-file loaders
  (`jepadrift/representations/extract.py:34-35`): `np.load` of `ret_wide.npy` and `dates.npy`
  (`jepadrift/data_loader/articleB.py:80-84`, `:93-95`; `jepadrift/data_loader/sp500.py:582-591`). `pre_monitor`
  spans the first pretrain day to the last calib day of `splits.yaml` (`jepadrift/pipelines.py:94-98`;
  `jepadrift/data_loader/articleB.py:106-111`; `jepadrift/data_loader/sp500.py:606-610`).
- **Declared coverage, not observed.** `ret_wide.npy` rows up to 2025-06-30 for D2
  (`data/derived/MANIFEST.json:128-132`) and from 2000-01-03 to 2026-10-16 for D3 (`:163-167`); SPY phase files
  up to 2025 (`:87-105`); no date range for D3 `chars.parquet` (`:182-183`).
- **Bounded precedent.** A pretrain-only reader opens the Parquet row groups starting before 2016-01-01 and
  refuses a selected row group reaching 2020-01-01 (`docs/DEVIATIONS.md:753-756`). D3 `ret_wide.npy` is
  Fortran-ordered, so a contiguous prefix read assuming C order is impossible (`:752`); no other bounded reader is
  ruled out. UNKNOWN: D2 memory order, row-group boundaries at 2020-01-01, `chars.parquet` coverage.
- **Import side effects.** Each producer overwrites the thread variables at import
  (`experiments/e1_problem.py:21-26`, `experiments/e3_calibration.py:24-29`, `experiments/e10_robustness.py:25-30`)
  and puts ROOT first on `sys.path` (`experiments/e1_problem.py:48`, `experiments/e3_calibration.py:49`,
  `experiments/e10_robustness.py:48`). Shell: `experiments/__init__.py` does not exist.
- **Process pools.** With `jobs > 1` and several tasks, each producer maps its tasks on a `spawn` pool
  (`experiments/e1_problem.py:546-551`, `experiments/e3_calibration.py:613-618`,
  `experiments/e10_robustness.py:503-508`); some task functions call the whole-file loaders
  (`experiments/e1_problem.py:402-405`, `experiments/e3_calibration.py:313-315`,
  `experiments/e10_robustness.py:420-423`). Inferred, not executed: such a worker can re-import the target and
  reload whole files; no return read is attributed to pure D5 tasks. Established: ORIGIN checks the runner's
  own import (`docs/sections/benchmark_runner_contract.md:215-217`); limited to the parent, it does not qualify
  the children's code or reads.
- **Digests and guards.** `save_fair_csv` writes CSV files without hashing them (`jepadrift/pipelines.py:67-71`);
  the producers log digests and verify none (section 3). Pre-J4 guards refuse rows after 2019-12-31 and the
  test-window request without consulting the freeze named by `CLAUDE.md:161-162`; rows within each target's
  pre-2020 bounds stay accepted (`docs/sections/benchmark_runner_contract.md:402-406`, `:425`; section 3).
- **Inputs outside POLICY.** The audit CSV files under `results/audit/` and the `z_*.json` sidecars read by the
  producers (section 3) are not POLICY roots (`tools/freeze_config.py:29-31`). Shell grep finds no `z_` and no
  `results/audit` entry in the manifest, which declares the `splits.yaml` digests
  (`data/derived/MANIFEST.json:147-148`, `:186-187`).

## 3. Candidate maps
### 3.1 e1 (`experiments.e1_problem`, `configs/e1.yaml`)
- **CLI and variants.** `main(argv=None)` (`experiments/e1_problem.py:1187`) parses `--config`, `--quick`,
  `--arms`, `--jobs` (default 24), `--out`, `--fig-dir`, `--log-dir`, `--include-test-window` (`:1189-1196`).
  The test-window flag, an unknown arm and `--jobs < 1` end in `ap.error` (`:1198-1202`). `--arms` becomes a set
  (`:1200`): token order and duplicates change the argv, not the computation. `--quick` merges the `quick` block
  (`:1173-1184`; `configs/e1.yaml:44-51`). The `window` key (`configs/e1.yaml:3`) is not read; the window is a
  constant (`experiments/e1_problem.py:67`).
- **Configuration and directories.** The target re-reads its configuration with `yaml.safe_load`
  (`experiments/e1_problem.py:1175`), a gap bounded by the second `check()`
  (`docs/sections/benchmark_runner_contract.md:240-246`). `--out` and `--log-dir` are created with `exist_ok`
  (`experiments/e1_problem.py:1204-1205`), `--fig-dir` inside `plot` (`:1122`).
- **Output set.** It depends on `--arms`, the data and producer branches: `e1_null.csv` with J2I
  (`experiments/e1_problem.py:1218-1221`); `e1_cells.csv` only if A, S or G yield rows (`:1223-1234`);
  `e1_slopes.csv` with B (`:1235-1238`); `e1_real_phases.csv` with C (`:1240-1243`); `e1_j2_summary.txt` and
  `e1.log` always (`:1245`, `:1250`). Figures depend on the CSV files present in `--out` and on row filters
  (`:1123`, `:1138-1142`, `:1153-1156`); digests are logged for every `e1_*` file in `--out` (`:1247-1248`).
- **Data.** `load_window` loads whole files, slices `pre_monitor`, drops the declared D3 date 2005-01-03 and
  checks the window and contiguity (`experiments/e1_problem.py:103-128`, `:68`, `:96-100`). Characteristics
  (`:131-135`, `:305-307`) reload `ret_wide.npy` and read the whole `chars.parquet`
  (`jepadrift/data_loader/chars.py:24`, `:34`; `jepadrift/data_loader/sp500.py:599-603`). SPY phases are read
  whole, then filtered by date (`jepadrift/stats/drift.py:78-83`; `jepadrift/data_loader/articleB.py:98-103`).
  Other inputs: sidecars (`experiments/e1_problem.py:356-358`) and audit CSV files (`:836`, `:1023`); only the
  `predicted_gains.csv` digest is logged (`:1215`). No consumed byte is verified.
- **Holdout.** Every cell is retrospective: the calib rows follow every onset (`experiments/e1_problem.py:12-15`).
  Arm S includes P3-D (`:8`, `:350-351`), whose D6 null check re-reads its calibration windows
  (`docs/DEVIATIONS.md:707-718`). No independent real holdout exists in E1.

### 3.2 e3 (`experiments.e3_calibration`, `configs/e3.yaml`)
- **CLI and variants.** `main(argv=None)` (`experiments/e3_calibration.py:939`) parses `--config`, `--quick`,
  `--out`, `--fig-dir`, `--log-dir` and `--jobs` (default 24) (`:941-946`); argparse would reject
  `--include-test-window`. `--quick` updates the replicate counts (`:952-954`; `configs/e3.yaml:46-47`). Figure
  and log defaults derive from the `--out` name (`experiments/e3_calibration.py:955-956`); the runner forwards
  both (`docs/sections/benchmark_runner_contract.md:104-106`).
- **Output set.** Five CSV files (`experiments/e3_calibration.py:1106-1109`), `e3_j2_check.txt` (`:1111`), four
  figures in PNG and PDF (`:821-824`, `:868`, `:891`, `:912`, `:934`) and `run.log` (`:1154`); directories are
  created after the computation (`:1104-1105`); the log records Git HEAD through a subprocess (`:1113`).
- **Data.** `load_rows` loads whole files, slices `pre_monitor`, drops the declared D3 date and checks the strict
  window (`experiments/e3_calibration.py:116-133`, `:68`, `:109-113`). It reads `results/audit/symmetry_tests.csv`
  (`:64`, `:775`) and logs the whole-file `ret_wide.npy` digest after the computation (`:1120`).
- **Holdout.** Real D6 rows and raw windows (2005-2019, raw rows descriptive) have no independent holdout
  (`experiments/e3_calibration.py:9-12`). A separate synthetic D5 P1-D control has calibration and evaluation
  roles and a Wilson interval (`:4-7`; `tests/test_e3.py:196-217`); it certifies only its own synthetic model.

### 3.3 e10 (`experiments.e10_robustness`, `configs/e10.yaml`)
- **CLI and variants.** `main(argv=None)` (`experiments/e10_robustness.py:732`) requires `--stage` and
  `--families` (`:734-735`) and refuses `jepa` and `F2` (`:743-746`). `--families` serves only that refusal
  (`:745`): `F1` and `F1 F1` run the same computation. `--jobs` defaults to `os.cpu_count()` (`:741`); `--quick`
  swaps the SR grid and replicate counts (`:751-752`; `configs/e10.yaml:8-10`).
- **Output set.** `e10_cells.csv` and `e10_gains.csv` (`experiments/e10_robustness.py:844-845`), figures
  `fpr_inflation` and `gains` in PNG and PDF (`:659-662`, `:706`, `:727`) and `run.log` (`:869`); directories
  are created late (`:840-841`).
- **Data.** `load_real` loads whole files and slices `pre_monitor` (`experiments/e10_robustness.py:323-334`).
  Its guard checks the upper bound only (`:317-320`), so the D3 row of 2005-01-03, first pretrain day
  (`docs/DEVIATIONS.md:531-533`), stays in E10 while E1 and E3 drop it: segments are per target. Sidecars are
  checked (`experiments/e10_robustness.py:349-352`); whole-file `ret_wide.npy` digests are logged (`:784`,
  `:837`, `:857`).
- **Holdout.** The real raw windows of the pretrain rows are fitted on the later calib rows, hence retrospective
  (`experiments/e10_robustness.py:11`); this says nothing about the synthetic D5 paths (`:5`).

### 3.4 Descriptors, failures, collisions and evidence classes (all three targets)
- **Descriptors needed (PROPOSED).** `protocol`: exact variant tokens and holdout plan. `data`: per-target
  segments and every consumed file (`splits.yaml`, sidecars, audit CSV files, phases, characteristics).
  `reader`: none exists and the contract makes it target-owned
  (`docs/sections/benchmark_runner_contract.md:148-150`), hence a producer change under its own GO.
- **Failure phases.** (1) Before import, descriptor refusals give PROTOCOL, DATA, READER or TARGET
  (`docs/sections/benchmark_runner_contract.md:194-195`). (2) Any exception in the target import or `main`, a
  reader's included, is TARGET_FAILED, exit 3 (`:116-117`, `:265-266`); today window, exclusion and sidecar
  mismatches and missing files raise in the producers (section 3). (3) At acceptance, absent or mismatching
  reader evidence is DATA (`:220-224`, `:378`). How a reader refusal is surfaced and the evidence format stay
  DEFERRED (G9, G10). No current check detects a stale audit CSV file.
- **Collisions.** Fresh namespaces are checked, then created exclusively
  (`docs/sections/benchmark_runner_contract.md:208-218`); producer `exist_ok` creation is compatible (`:353-355`).
  E1 `plot` and its digest glob read whatever `--out` holds (`experiments/e1_problem.py:1123`, `:1247`).
- **Evidence classes.** (a) Specifiable now on synthetic fake fixtures: the schema-independent refusals of
  section 5. (b) Separate bounded engineering GO: readers and their evidence, routing of every read (workers
  included), schema activation, a fixture dispatcher. (c) Researcher decision: variants, holdout, segments, the
  pre-2020 mandate, J4. Outputs depend exactly on arms, content and producer branches; this map qualifies no
  variant (`prompts/plans/plan-21-qualification-20261112.md:144`).

## 4. Gate matrix G1-G10 (every gate OPEN)
Fields: Ev(idence), Block(er), Owner, Next bounded task, Witness (PROPOSED), Auth(orization): R = researcher GO,
E = engineering GO.
- **G1 E5 protocol: OPEN.** Ev: no E5 configuration (shell), section 6 conflict. Block: E5 protocol and gate file
  undecided (`docs/sections/benchmark_runner_contract.md:503-506`). Owner: researcher; streams 16, 17, 19, 23
  (`prompts/streams/prompt-22-e5.md:37`). Next: Q6 note. Witness: gate file declared in the E5 namespace. Auth: R.
- **G2 Monitor and holdout: OPEN.** Ev: splits (`CLAUDE.md:61-62`); retrospective real windows (section 3); contract
  G2 (`docs/sections/benchmark_runner_contract.md:507-511`). Block: no approved semantics. Owner: researcher.
  Next: PROPOSED `holdout` fields (Q2). Witness: a descriptor without a holdout plan is refused. Auth: R.
- **G3 Bounded readers: OPEN.** Ev: precedent (`docs/DEVIATIONS.md:750-759`), whole-file loaders (section 2).
  Block: no reader bounded to `pre_monitor`; layouts UNKNOWN. Owner: Codex; researcher for re-materialized files.
  Next: per-dataset design note, then a layout probe under its own GO. Witness: a fake panel straddling 2020-01-01
  is refused before any later row is read. Auth: E.
- **G4 Byte verification: OPEN.** Ev: F reads no data (`tools/freeze_config.py:38-40`); logged, unverified digests
  (section 3); whole-file declared digests only (`data/derived/MANIFEST.json:128-132`). Block: no segment digest.
  Owner: Codex and researcher. Next: PROPOSED segment declarations (Q3). Witness: a segment altered by one byte is
  refused before computation. Auth: E; R to hash real segments.
- **G5 J4 activation: OPEN.** Ev: fixture-only guards (`tools/freeze_config.py:426-429`, `:433-435`); `pre_j4`
  coupling (`prompts/wrapups/wrapup-21-F.md:152`). Block: no J4 GO. Owner: researcher. Next: none here. Auth: R.
- **G6 2020+ targets: OPEN.** Ev: post-2019 guards reading no freeze (section 2); E5 and E8 as new frozen code
  (`docs/sections/benchmark_runner_contract.md:521-522`). Block: E5 and E8 absent; G5. Owner: researcher;
  streams 22, 25. Next: none here. Auth: R.
- **G7 Upstream streams: OPEN.** Ev: 16 to replan, 17 with an uncalibrated P4-D, 19 and 23 partial
  (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_12.md:84-91`). Block: those streams. Owner: their
  owners. Next: none here. Auth: one GO per stream.
- **G8 Pre-2020 mandate: OPEN.** Ev: no mandate (`docs/sections/benchmark_runner_contract.md:525-528`); prompt 21
  wants a bit-identical `results/e1/e1_cells.csv` (`prompts/streams/prompt-21-freeze-runner.md:32`).
  Block: no mandate. Owner: researcher. Next: PROPOSED candidate variants (Q2). Witness: declared digests
  reproduced, a mismatch stops and is reported (`docs/sections/benchmark_runner_contract.md:374-375`). Auth: R.
- **G9 Production formats: OPEN.** Ev: DEFERRED descriptors (`docs/sections/benchmark_runner_contract.md:144-152`;
  `prompts/GO-stream-21-R.md:23`). Block: no approved schema. Owner: Codex proposes, researcher approves (Q1).
  Next: the section 5 list. Witness: null and placeholder descriptors are refused. Auth: documentary GO, then E.
- **G10 Implementation methods: OPEN.** Ev: ORIGIN DEFERRED (`docs/sections/benchmark_runner_contract.md:65-72`);
  `sys.path` and `spawn` (section 2). Block: mechanisms, worker coverage (Q7). Owner: Codex. Next: future
  implementation plan. Witness: a preloaded target, or a worker resolving it outside ROOT, is refused. Auth: E.

## 5. Minimal future fixtures and refusals (PROPOSED / NOT EXECUTED)
- **Blocking rule.** No positive fixture dispatch before an approved descriptor and evidence schema and a separate
  bounded engineering GO (`docs/sections/benchmark_runner_contract.md:441-443`). A null descriptor, a non-empty
  placeholder, a hashed GO document or the presence of `configs/FROZEN.json` qualifies nothing (`:153-159`).
- **Schema-independent refusals** (pre-import phase; synthetic fixtures, no producer import; classes P and S of
  `docs/sections/benchmark_runner_contract.md:444-470`, `:493-498`). R1: rows e1, e3, e10 with null descriptors
  give PROTOCOL, DATA or READER (`:463`). R2: placeholders (`"TBD"`, a GO path or digest) give the same refusal.
  R3: a managed flag among the extras, `=` spelling included, gives ARGV (`:99-101`). R4: `--stage jepa`,
  `--families F2`, an unknown arm or an unqualified `--quick` give ARGV (`:168`). R5: `--include-test-window` on
  e1, e3 or e10 gives TARGET (`:194-195`, `:425-426`). R6: PCA, `ca_tjepa`, `eurofidai_schema` configurations give
  TARGET (`:171-176`). R7: strict YAML refusals give CONFIG (`:451-459`). R8 (static): every candidate
  UNQUALIFIED, no variant declares `run.json`, no producer default directory is forwarded.
- **Minimum schema requirements** (a list, not a format; Q1). `protocol`: exact variant tokens, configuration
  digest, holdout plan, hashed approval reference. `data`: each consumed file and its declared digest, per-target
  segment (first and last day, rows), auxiliary inputs (`splits.yaml`, sidecars, audit CSV files, phases,
  characteristics). `reader`: read unit, refusal of any unit reaching 2020-01-01, consumed-byte evidence per process.
- **Reader fixtures** (after an engineering GO only): a fake panel straddling 2020-01-01, a segment altered by one
  byte, a stale sidecar, a `spawn` worker task calling the loader. A refusal witness checks only that no
  computation follows; its exit code awaits the DEFERRED escalation rule (G9, G10) and the phases of section 3.4.

## 6. E5 gate file versus runner namespaces
- **Facts.** Prompt 22 runs E5 through the runner and writes `results/e5/J4_gate.txt`
  (`prompts/streams/prompt-22-e5.md:17`, `:34`, `:54-55`), the routed prompt (`prompts/streams/INDEX.md:107`). A
  proposed full replacement writes `results/e5/j4_verdict.json` from a direct call with `--out`
  (`prompts/streams/07_STREAM_22_E5_J4_REWRITE.md:3`, `:56`, `:71`). The contract's proposed namespaces exclude
  default directories (`docs/sections/benchmark_runner_contract.md:367`), leave the conflict to G1 (`:396-397`),
  and a pending departure requires a valid freeze for every dispatch (`:545-546`).
- **Decision needed (Q6; researcher; no default).** As written, the contract fits only a gate file declared by
  the E5 variant inside `results/benchmark_runner/e5/run-<run16>/` and listed by `run.json`
  (`docs/sections/benchmark_runner_contract.md:363-367`, `:379-385`); `results/e5/` (absent, shell) would need an
  amendment. Decide (i) the canonical E5 prompt, (ii) the gate artifact name and format, (iii) its location and
  (iv) the consuming command. No fake file, link or compatibility shim is created.

## 7. Exact pending decisions (all OPEN)
Listing decides nothing (`prompts/plans/plan-21-qualification-20261112.md:136`); none other arose while writing.
- **Q1 (G9).** Schemas of `protocol`, `data`, `reader` and the evidence format: Codex proposes, researcher approves.
- **Q2 (G2, G8).** Can a candidate whose real windows lack an independent holdout qualify; which variants?
- **Q3 (G3, G4).** Reader strategy (re-materialized `pre_monitor` files, Parquet row groups, or `.npy` offsets
  once the layout is known); who declares segment digests, and under which GO real segments are hashed.
- **Q4.** Inputs outside POLICY (audit CSV files, sidecars): `data` entries, or a POLICY v2 with a new verifier.
- **Q5.** Pre-J4 admissibility of opening post-2019 metadata (phase files declared up to 2025) for pre-2020 use.
- **Q6 (G1).** Items (i) to (iv) of section 6.
- **Q7 (G10, Codex).** `--jobs > 1` under the runner: refused, or covered by ORIGIN and reader evidence per worker.

## 8. Not executed
- Not created: runner, dispatcher, reader, fixture, test, schema, configuration, FROZEN, `make freeze`, J4 or E5
  artifact. Not run: Python, import, test, `make`, computation, E1, E3, E10, E4, E6, D6, PCA. Not opened: data
  files, `.npy` headers, Parquet metadata, returns, 2020+ or private rows (`data/derived/MANIFEST.json` read as
  POLICY metadata). Git: the three read commands of the GO (`prompts/GO-stream-21-qualification-20261112.md:33`).
- Sealed, checked in the worker journal: J1 `e315e537...0823` (47 CRLF); E3 `1ca7c3ae...68b3`, D8 stays FAIL; PCA
  full manifest `3b2299bc...2f47`. Sources, tests, configurations, DEVIATIONS, MAPPING, paper, memory unchanged.
