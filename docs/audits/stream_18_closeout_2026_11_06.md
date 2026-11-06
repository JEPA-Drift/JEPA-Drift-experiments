# Stream 18 closeout audit — CD-DFM documentary diagnostic, 2026-11-06

## Scope and authority

- Request: `logs/orchestration_20261106/request.md` (ignored by Git, like the native-plan archive below). GO:
  `prompts/GO-stream-18.md` (2026-11-06, 12:22 UTC; Codex
  within the mandate delegated by the researcher, no personal researcher signature attributed). Canonical plan:
  `prompts/plans/plan-18.md` with its « Décision GO intégrée ». The reviewed native plan is archived as
  `logs/orchestration_20261106/native-plan-reviewed.md` (85 lines, SHA-256
  `c10fe4eb009bef8ac3793ba3e999a360e2f64d40256548fd9c4ce5469d04c001`, equal to the session's native plan file).
- Base `20ad9e860a58373ec85405de6ee19a68322dd02e`, branch `review/stream-18-20261106`.
- GO answers applied: Q1 the diagnostic stays at `docs/sections/cd_dfm.md`, with no competing diagnostic file; Q2 no
  causal hypothesis on the missing modules; Q3 documentary controls only in this session, `make check` and
  reindexation by Codex at closeout.
- Outputs: `docs/sections/cd_dfm.md` (rewritten), this audit, `prompts/wrapups/wrapup-18.md`.
- Not done, outside the GO: adapter, installation, environment creation, execution of external code, tests,
  training, reads of returns, experiments; changes to data, results, figures, configuration, memory files,
  `docs/DEVIATIONS.md`, the prompt master or the 01–27 audit; other worktrees; Git mutations; reindexation. No
  retroactive GO is attributed to the October diagnostic.
- Review amendments (2026-11-06, Codex reviews of the checkpoints, GO unchanged): the bytecode-cache observation and
  the absence statements of this audit and of the diagnostic were bounded to what the inspected perimeters show; the
  diagnostic's causal Z-1 sentence was then replaced by the rule of prompt 18, task 5 and the observation that no Z-1
  wrapper was found in the inspected project tree. No new inspection was run for these amendments.

## Sources read

`CLAUDE.md`; `prompts/streams/prompt-18-cddfm.md`; `prompts/amorcage-18.md`; `docs/sections/cd_dfm.md` as committed
in `d8e644b`; row 18 of `docs/audits/streams_01_27_relevance_2026_11_06.md`; `data/derived/MANIFEST.json`
(`sources.d3.cd_dfm`); section 2 of `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md`;
`jepadrift/data_loader/sp500.py`; `tests/test_data_d3.py`; `logs/data/d3_build.log`; the GO and the canonical plan.
In the clone, only Git objects of the pinned commit were read (`git show`, `git ls-tree`, `git grep`): `README.md`,
`.gitignore`, `requirements.txt`, `environment.yml`, `configs/data.yaml`, the import headers of `scripts/train.py`,
`scripts/preprocess_dataset.py`, `src/paths.py`, `tests/test_dataset.py` and `tests/test_preprocess.py`, and lines
1–30 of `scripts/benchmarks/run_sparse_pca.sh`. No raw-data directory and no return series were read.

## Commands executed

All commands were read-only and ran from the worktree root on 2026-11-06. Plan-phase reads (before the GO) used
`git show`, `git ls-tree`, `git grep`, `git log`, `grep`, `sed`, `ls` and `stat`; the post-GO assertion run below
re-asserts their findings on the pin, the clone and the cited sources. It ran as one chained command, reformatted
here one command per line with its `echo` lines omitted, and ended with `ALL-F-CHECKS-PASS`; `fail` prints its
argument and exits 1.

```bash
P=37a1dfb39974884df822aa2994854bbf1270e381; C=external/cd-dfm
test "$(git -C $C rev-parse HEAD)" = "$P" || fail F1-head
grep -n "\"commit\": \"$P\"" data/derived/MANIFEST.json || fail F1-manifest
git log --format='%h %ad %s' --date=short -S "$P" -- data/derived/MANIFEST.json
git -C $C log -1 --format='%H %ad %s' --date=iso $P
test -z "$(GIT_OPTIONAL_LOCKS=0 git -C $C status --porcelain=v1 --untracked-files=all)" || fail F1-clone-not-clean
GIT_OPTIONAL_LOCKS=0 git -C $C status --porcelain=v1 --ignored --untracked-files=all | grep -c '^!! '
N=$(git -C $C ls-tree -r --name-only $P | wc -l); test "$N" -eq 71 || fail F2-count
test -z "$(git -C $C ls-tree -r --name-only $P | grep -E '(^|/)(data|cddfm)(/|\.py$)')" || fail F2-data-or-cddfm-present
L=$(git -C $C grep -n 'from data\.dataset import' $P | wc -l); Fz=$(git -C $C grep -l 'from data\.dataset import' $P | wc -l)
test "$L" -eq 25 && test "$Fz" -eq 22 || fail F2-import-counts
git -C $C grep -n -E 'from data import preprocess_panel|from data\.preprocess import|from cddfm\.' $P
git -C $C grep -n 'from data\.dataset import' $P -- scripts/train.py src/train.py
git -C $C grep -n 'sys.path.insert' $P -- scripts/train.py
for d in src/model/ src/eval/ src/analysis/ src/paths.py src/train.py; do git -C $C ls-tree -r --name-only $P | grep -q "^$d" || fail "F2-missing $d"; done
git -C $C show $P:README.md | grep -n 'src/data/'
test -z "$(git -C $C ls-tree -r --name-only $P | grep -iE '(^|/)(licen[cs]e|copying|notice|copyright)([._-]|$)')" || fail F3-license-file-found
git -C $C show $P:README.md | grep -n -i 'licen'
git -C $C show $P:README.md | grep -n -E 'cannot redistribute|10 continuous|compositional|2 categorical'
sed -n '56p' jepadrift/data_loader/sp500.py
git -C $C show $P:README.md | sed -n '1p'
test "$(grep -c -i 'cifre' CLAUDE.md)" -eq 0 || fail cifre-in-CLAUDE
test -z "$(git -C $C grep -n -i -E 'kalman|state.space' $P)" || fail kalman-found
git -C $C show $P:README.md | grep -n 'Woodbury'
grep -c -F 'réellement disponible, licite, préspécifié et gelé avant J4 ; sinon diagnostic secondaire ou « non disponible » sans remplacement caché' prompts/streams/07_STREAM_22_E5_J4_REWRITE.md
stat -c '%y %n' $C/.git $C/.git/index
```

Other read-only commands of the session: `sha256sum` of the GO, the canonical plan, the native plan and its archive
before any write; `stat -c '%y %n'` on the 13 ignored bytecode files of the clone; `ls -d` on the clone's
`model_weights`, `results` and `data`; `git grep -l -i -E 'cd.?dfm'` over the tracked `results`, `logs`, `figures`,
`configs`, `experiments`, `jepadrift` and `tests`; `git log -S'--ignore=external' -- Makefile`, which lists `3e3a804`
(2026-10-16) and `f7bde91` (2026-10-17); the post-write checks recorded in `prompts/wrapups/wrapup-18.md`.

## Observations

- F1. The manifest pin (line 290) entered the repository in `3e3a804` (2026-10-16, D3 build), and
  `logs/data/d3_build.log` lines 3–5 record the clone at this commit and C-D3-no239. The pinned commit is dated
  2026-07-29 21:36:44 +0200 ("Update contact email"). The clone's HEAD equals the pin; `status` reports no tracked
  change, no untracked file outside the ignore rules and 13 ignored entries.
- The 13 ignored entries are bytecode cache files: 11 named `tests/__pycache__/*.cpython-312-pytest-9.1.1.pyc` and 2
  named `src/analysis/__pycache__/*.cpython-312.pyc`, with file modification times between 2026-10-16 15:02:59 and
  15:03:00 UTC. Their names and times establish neither an import, nor its success, nor the date of an execution, and
  no log among the sources read records the run that produced them. This session executed no external code. The
  clone's working tree has no `model_weights/`, `results/` or `data/` directory.
- The clone's `.git` directory has the modification time 2026-11-06 11:41:05 UTC and `.git/index` 2026-10-22
  15:23:16 UTC. Both values predate this session's first access to the clone and were unchanged at the end of the
  assertion run.
- F2. 71 paths are tracked at the pin; none has a `data` or `cddfm` directory component or is named `data.py`.
  `from data.dataset import` occurs in 25 statements across 22 files (e.g. `scripts/train.py:21`, `src/train.py:12`);
  `from data import preprocess_panel` at `scripts/preprocess_dataset.py:19`; `from data.preprocess import` at
  `tests/test_preprocess.py:9`; `from cddfm.data.dataset import` and `from cddfm.eval.benchmarks import` at
  `scripts/benchmarks/run_sparse_pca.sh:25-26`. `scripts/train.py:18` inserts the clone's `src/` in `sys.path`.
  `src/model/`, `src/eval/`, `src/analysis/`, `src/paths.py` and `src/train.py` are tracked. README line 38 lists
  `src/data/`.
- F3. No license-like file is tracked at the pin. README line 58 holds its only licensing sentence, which concerns
  the RavenPack and Compustat characteristics.
- F4. README lines 57–69 and `configs/data.yaml` define the upstream inputs; `jepadrift/data_loader/sp500.py:56`
  defines the four D3 continuous characteristics and lines 58–62 the 11 GICS sectors.
- Inspected perimeters for CD-DFM outputs. (a) The clone's working tree (status listing and `ls -d` above). (b) The
  tracked files under `jepadrift`, `experiments`, `tests`, `configs`, `results`, `figures` and `logs` that match
  `cd.?dfm` (case-insensitive): `jepadrift/data_loader/sp500.py` (clone and manifest code), `logs/data/d3_build.log`
  and `tests/test_data_d3.py:319` (manifest key check); none of them is an adapter, adapter test, pipeline entry,
  configuration, result or figure for CD-DFM. (c) The paths named by prompt 18 for the adapter, its test and the
  diagnostic (`jepadrift/representations/cddfm_adapter.py`, `tests/test_cddfm_adapter.py`,
  `docs/sections/cddfm_adapter.md`), absent at the plan-phase `ls`. Untracked and ignored project files were not
  inspected.

## Claim-by-claim correction of `d8e644b`

| Lines in `d8e644b` | Claim | Local evidence | Rewritten document |
|---|---|---|---|
| 3 | "Excluded from Primary J4 Confirmatoire Gate" | the J4 rule admits CD-DFM only if available, lawful, pre-specified and frozen | status "unavailable"; J4 reading in "J4 eligibility" |
| 5 | CD-DFM expanded as "Continuous-Discrete Dynamic Factor Model" | README title: "Characteristic-Driven Dynamic Factor Model" | name corrected |
| 5–7 | CD-DFM "was evaluated" as a baseline | no adapter, training or evaluation output found in the inspected perimeters (Observations) | planned by prompt 18 (P4 variants, channel N2); no training or evaluation output found in the inspected perimeters |
| 11–14 | no "explicit open-source license"; "All rights reserved"; vendoring "would violate" publication policies and "CIFRE confidentiality / IP compliance rules recorded in `CLAUDE.md`" | no license-like file at the pin; `CLAUDE.md` contains no "CIFRE" | observation only, explicitly not a legal conclusion; CIFRE claim removed |
| 15–19 | exclusion ground "Absence of Z-1 Data Ingestion Loader"; "full rewrite of its state-space ingestion layer" | the Z-1 wrapper is a project-side deliverable (prompt 18, task 3); no `kalman` or `state space` match at the pin | ground replaced by the `data` package missing at the pin (prompt 18, task 5) |
| 20–24 | protocol cited as `07_STREAM_22_E5_J4_REWRITE.md`; "Neither the license nor the Z-1 ingestion condition is met" | quotation verbatim at `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md:26`, section 2 | full path; only the availability condition judged unmet; lawfulness, pre-specification and freezing not assessed |
| 26–37 | Kalman transition dynamics; high estimation cost; JEPA frozen-inference contrast; "sufficient orthogonal coverage"; no "coverage gap" | no measurement found in the inspected perimeters; the README claims a Woodbury inversion in O(nK² + K³) with training linear in the number of assets | section removed; "Not established" paragraph |

## Workflow trace

- `d8e644b` (2026-10-30, "docs(stream-18): add documentary diagnostic and exclusion rationale for CD-DFM", one file,
  37 lines) is the only commit touching `docs/sections/cd_dfm.md` in the history of the base. No plan, GO or wrapup
  of stream 18 was present in the worktree at the base.
- `prompts/amorcage-18.md` (last changed in `c10b68a`, 2026-10-23) asked for `prompts/plans/plan-18.md` after a GO;
  none was present at the base, before Codex recorded its canonical plan on 2026-11-06.
- Branch `stream-18` points to `c284823` and has no commit outside `main`; no worktree is registered for it. It was
  not modified.
- Prompt 18, task 5 names `docs/sections/cddfm_adapter.md` for this diagnostic; per GO Q1 the diagnostic stays at
  `docs/sections/cd_dfm.md`, and no second diagnostic file was created. No `C-CDDFM-inputs` entry was written: on the stop
  path prompt 18 requires only the documentary diagnostic and the plan/wrapup, and `docs/DEVIATIONS.md` is outside
  this GO.
- Decision unchanged: `BLOQUÉ` for model integration. The 01–27 audit was not modified.

## Not examined

- Upstream dependencies (README: Python 3.11, PyTorch 2.5; `requirements.txt`: statsmodels, nonlinshrink and ipca,
  among others) against the project `.venv`: the task 5 stop already holds.
- Commits other than the pin, the remote repository and its hosting metadata (no fetch).
- The cause of the missing `data` package (GO Q2).

## Test evidence

No test, `make check` or experiment ran in this session. The request reports a passing `make check` at the base
(37 + 545 passed, 5 skipped); this is prior reference evidence, not a test executed here. `make check` and
reindexation are assigned to Codex at closeout (GO Q3).

## Hashes

- `docs/sections/cd_dfm.md` as committed in `d8e644b` (blob `c7a184fe550f00fcd06e010889949b22ef3784f7`): SHA-256
  `f07e95c82a95224f7034fa0790b83e39da19a581a69ba0cfabb806b9e4869988`.
- `docs/sections/cd_dfm.md` rewritten, after the review amendments (69 lines): SHA-256
  `4bbc37ce5d3cb0f4e0432a261724478ee611e87b9fc5e8340f5e07ae586954de`.
- Codex files, SHA-256 recorded before any write of this session: `prompts/GO-stream-18.md`
  `d57af17d55366c323ea2c78658bfbad70bed348e6d3841b6cd825a687a8ec47c`; `prompts/plans/plan-18.md`
  `4102cdcb17bda7e480bfab336d11e1d4dfd438abeb8d0641b364bb4e196fa3ee`. The post-write comparison is recorded in
  `prompts/wrapups/wrapup-18.md`.
