# Wrapup — Lot 21-appendix: partial inventory of declared D5 parameters (`tools/appendix_b.py`)

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md`: prompt 21, task 6 (`tools/appendix_b.py`), narrowed to the minimum tool plus one targeted test. The tool builds a deterministic inventory of DECLARED generation and injection parameters, with relative source, key or section, and SHA-256 of each input. Base `46c24923957ec505947016118def9453284bd1bc`, branch `stream-21-appendix`, Codex worktree. Lot 21-dpi is independent and provided no input.
- **Workflow.**
  - Claude wrote a native plan (SHA-256 `901eafc201486fa3f4e3231840908d9dfc4a4e05e9a90455803584184efe20b7`). Codex archived it as `logs/orchestration_20261106/native-plan-reviewed.md` and reviewed it in `logs/orchestration_20261106/codex-plan-review.md` (`1196916b5e0c2bbb8a906860959ef39ed6b67a41cbe13c2403a5cba8b99a13dc`).
  - The native plan proposal was declined in the CLI. Codex delivered the GO in chat and recorded `prompts/plans/plan-21-appendix.md` (`8bbf91b279c046bbcdaf8d7c3a40c0af469171e9c53bcfcfa3a8cca0a08c9a33`, with its section "Décision GO intégrée") and `prompts/GO-stream-21-appendix.md` (`323ded0d7bedca2ffaa29f16c3db02b9cdc29ec914942aef5f2270d919527041`). Both files are hashed before and after each phase and remain unchanged.
  - First execution phase (00:07–00:18Z): TDD, reception and targeted checks, then stop for review.
- **GO decisions.** The integrated decision prevails over the native plan.
  - Q1–Q6 keep their defaults: the D5 table only, plus the leaves of the two YAML sections. Exit 0 after a well-formed inventory is written, even with a divergence; exit 1 on refusal. `table` and `confined` are reused through a module CLI. Duplicate YAML keys are refused. A sentinel pins the three current inputs. These three sources only.
  - The title, caveat and statuses announce a **partial** inventory. NOT_DOCUMENTED became **UNMAPPED_CONFIG** and NOT_CONFIGURED became **UNMAPPED_DOC**. Both describe the six selected links only, never an absence from the whole note or code.
  - A deleted linked key is rendered as an absence, alpha alone included when beta stays present.
  - MATCH never comes from a numeric fragment. The whole documented cell must fit a bounded form: a pair, a number-or-`None` alternative, or a scalar with unit `days`. Positions and arity are checked. Any other form is **UNSUPPORTED_DOC_VALUE**.
- **Closeout review.** Codex's `logs/21-appendix/codex-final-review.md` (`082324293ac0abf608eff6e719c69284ad74d8694f0e7aca006eb0ff67ca56f8`) found two input-refusal gaps and gave a GO for two bounded corrections.
  - The YAML loader compared raw scalar key texts. `outside: {0x10: first, 16: second}` was accepted and its first entry silently lost.
  - `d5: &d {loop: *d}` reached `RecursionError` in `leaves` instead of the prefixed refusal.
  - Constraints: no new source, form, link, dependency, scientific output or shared-helper change. The baseline output stays byte-identical. Reception goes to a new ignored output path.
  - Execution came in two phases. The static phase allowed only reading files, hashing with shell tools and writing witnesses, with no Python, import, pytest, CLI, pyflakes or Git, while the root ran the 21-dpi full check on the shared helper. An explicit "GO runtime" message then granted the exclusive validation slot.
- **What the generation adds to the note.**
  - Provenance: relative path, `section.key` and SHA-256 of each input.
  - 7 configured leaves without a link (UNMAPPED_CONFIG).
  - 4 (source, row) pairs without a link (UNMAPPED_DOC): `d5` declares neither ν nor ρ, and `synthetic` declares neither (α, β) nor burn-in. In those places the experiments use code literals, which are not inventoried: E3 t7 goes through `sim.Garch` (`sim.NU = 7`); PCA calls `garch_panel(T, N, 0.0, 0.0, nu, ..., burn=0)`.
  - A whole-cell comparison for the six links.
- **Agent.** Claude Code, Opus 5.5 (`claude-opus-5-5`), one interactive session, effort max throughout, no subagent, no context purge.

## Validated Results

- **Outputs (SHA-256):**
  - `tools/appendix_b.py` (218 lines; standard library, PyYAML 6.0.3 and `tools.trace_numbers.{confined, table}` only): `4a0e0eaac374d4f6809fea2b177fc43a6f5712ec5cc54609a5b3006d8ca808a4`. The first-phase version was `436d8fc8bc632d4cc197c3c1e55519fadd7eedca5c0fbde3c0abacce0e2b220f`.
  - `tests/test_appendix_b.py` (339 lines, 92 test cases): `e64af80b76a6c5a8267f952c46c2da067ee40e8c5b150cc578f89d7f7fe3a339`. The first-phase version was `633386108fd0811cbc3c9d880c53a87789f1d65a4f089e8f6fc3bfac2bb62b6b` (70 cases).
  - The sealed fragment `logs/21-appendix/appendix_b.md` (ignored) is unchanged: `dabf3ca9482c4721ec84b8eea2d29d4f8a97449fd3fbe8c5ecb27bbc450803c2`. The closeout reception `logs/21-appendix/appendix_b-review.md` has the same SHA-256 and is byte-identical (`cmp`). So are `appendix_b-determinism.md` and `appendix_b-review-determinism.md`.
- **Closeout TDD** (`.venv/bin/python -B -m pytest -q -p no:cacheprovider`, environment `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`):
  - RED (01:55:30Z, `review-red.log`), run on the unchanged first-phase tool: 14 failed, 78 passed, exit 1. These are exactly the 14 failures predicted in the static phase:
    - 9 silent acceptances (exit 0): `0x10`/`16`, `020`/`16`, `yes`/`true`, `~`/`null`, `1`/`1.0`, `1`/`true`, equal keys in an unselected list, in the selected list leaf `d5.backgrounds`, and a `<<` merge overridden by an explicit `beta`.
    - `0x10`/`16` inside `synthetic.backgrounds` was refused for the wrong reason (`key 16 under synthetic.backgrounds is not a plain name`), after the silent overwrite.
    - The two mapping cycles raised `RecursionError`.
    - The list cycle was refused as `non-finite or non-JSON value ['t7', [...]]`.
    - `{1: first, '1': second}` was falsely refused (`duplicate key '1'`).
  - GREEN (01:56:13Z, `review-green.log`): `tests/test_appendix_b.py` and `tests/test_trace_numbers.py` give 180 passed (92 + 88). `pyflakes` reports nothing on both files, no line exceeds 120 characters, and no line ends in whitespace.
  - First phase, for the record: RED was a collection `ImportError` (00:14:08Z); GREEN gave 70 and then 158 passed; 12/12 mutants were killed.
- **The two corrections.**
  - `_Loader.construct_mapping` lets SafeLoader construct the mapping: it flattens `<<` merges, constructs the keys and refuses unhashable keys with a `ConstructorError`. The loader then refuses when the mapping holds fewer entries than key/value pairs. The message names the first constructed key equal to an earlier one: `duplicate key 16 in the mapping at line N`. This applies to every mapping of the file, including unselected ones and mappings inside lists.
  - `section()` runs `json.dumps(doc[name], skipkeys=True, default=repr)` before `leaves()`. A cycle in the selected section raises `ValueError`, rendered as `<rel>: section 'd5': Circular reference detected`. With `allow_nan` left at its default, `skipkeys` and `default=repr`, non-finite values, non-JSON values, bad key names and empty maps still reach `leaves()` and keep their own messages.
- **Closeout witnesses** (refused with exit 1, the relative input prefix and no output file, unless marked accepted):
  - Equal constructed keys: `{0x10: first, 16: second}` and `{020: first, 16: second}` give `duplicate key 16`. `{yes: first, true: second}` and `{1: first, true: second}` give `duplicate key True`. `{~: first, null: second}` gives `duplicate key None`, and `{1: first, 1.0: second}` gives `duplicate key 1.0`. The case `[{0x10: first, 16: second}]` covers an unselected list; the same mapping is also tested in the `d5.backgrounds` list and inside `synthetic.backgrounds`. `<<: {beta: 0.85}` followed by `beta: 0.90` gives `duplicate key 'beta'`.
  - Guards, green before and after: an unhashable sequence key and an unhashable mapping key (`found unhashable key`), a `!!python/tuple` key (`could not determine a constructor`), and a date key in `d5` (`is not a plain name`).
  - Cycles: `d5: &d {loop: *d}`, `back: *b` inside `synthetic.backgrounds`, and `backgrounds: &l [t7, *l]`.
  - Accepted: `{1: first, '1': second}` outside the sections, a merge without override, and a cycle outside the selected sections give the baseline rows. `copy: *b` reusing `synthetic.backgrounds` adds two UNMAPPED_CONFIG rows (`synthetic.copy.SYNTH_GAUSS_EQUICORR` null, `…SYNTH_T7_EQUICORR` 7). `shared: &s {extra: 1}`, reused twice in `d5`, adds `d5.reuse.extra` and `d5.again.extra`.
- **Mutation check** (`review-mutants.log`). A scratch script outside the repository exec'd each mutant of the source into the imported module, in a fresh process; the file on disk kept its hash. All 22 mutants were killed. Failures per mutant:

  | mutant | failures |
  |---|---|
  | `search` instead of `fullmatch` | 4 |
  | bool read as a number | 1 |
  | absent key read as null | 3 |
  | absence per documented row only | 2 |
  | membership instead of position | 1 |
  | overwrite allowed | 4 |
  | output link not confined | 1 |
  | unit not checked | 1 |
  | NaN accepted | 3 |
  | non-finite documented value accepted | 3 |
  | alpha/beta links swapped | 30 |
  | equal-key check removed | 11 |
  | raw-text key check (first-phase loader) | 11 |
  | type-aware `(type, key)` check | 2 |
  | key `set()` built before SafeLoader | 2 |
  | cycle check removed | 3 |
  | cycle check without `skipkeys` | 1 |
  | cycle check without `default` | 1 |
  | strict JSON pre-check (`allow_nan=False`) | 5 |
  | cycle check on the whole document | 1 |
  | encoder without `check_circular` | 3 |
  | shared mappings rejected | 2 |
- **First-phase witnesses** (still green).
  - `1,000 days` and `1e3 days` against 1, and `1,000 days` against 1000: UNSUPPORTED_DOC_VALUE. So are `1000 weeks`, `1000 days (2 chains)`, `(0.08, 0.90, 0.1)`, `(0.08 0.90)`, ``7, or `None` (Gaussian 2)`` and `7, or 5 (Gaussian)`.
  - Permuted alpha/beta give two DIVERGENT rows. `beta` 0.85 gives DIVERGENT, with both values visible. 5 against `None`, null against 7, text `'0.08'` against a number, and `true` against `1 days` all give DIVERGENT. An absent `SYNTH_GAUSS_EQUICORR` gives UNMAPPED_DOC, not MATCH.
  - Deleting `alpha` while `beta` stays gives UNMAPPED_DOC for `d5.alpha` and MATCH for `d5.beta`. A renamed row gives one UNMAPPED_CONFIG plus two UNMAPPED_DOC rows. A new row `T | 941` is not matched by value. `rho: 0.40` gives MATCH. In every case the six links stay visible exactly once.
  - Refusals: 25 input cases plus 2 invalid UTF-8 files, the confinement of the three inputs, 11 `--out` paths, and 3 existing targets, which are never overwritten.
- **Reception on the real inputs** (`review-reception.log`, `review-reception-rerun.log`, `review-reception-checks.log`):
  - `python -m tools.appendix_b --out logs/21-appendix/appendix_b-review.md` exits 0. The printed SHA-256 is `dabf3ca9…`, equal to the file's and to the sealed fragment's.
  - Counts: `17 rows: MATCH 6, DIVERGENT 0, UNSUPPORTED_DOC_VALUE 0, UNMAPPED_CONFIG 7, UNMAPPED_DOC 4`. The fragment holds 3 input rows plus 17 inventory rows, and no absolute path.
  - The rerun gives exit 1 (`exists; refusing to overwrite`) and leaves the bytes unchanged. A second output is byte-identical.
  - Rows of the fragment:

    | source | key | configured | row | documented | status |
    |---|---|---|---|---|---|
    | e3 | `d5.alpha` | 0.08 | (α, β) [1] | (0.08, 0.90) | MATCH |
    | e3 | `d5.beta` | 0.9 | (α, β) [2] | (0.08, 0.90) | MATCH |
    | e3 | `d5.burn` | 1000 | burn-in [1] | 1000 days | MATCH |
    | e3 | `d5.T_clean` | 941 | — | — | UNMAPPED_CONFIG |
    | e3 | `d5.backgrounds` | ["t7", "gaussian"] | — | — | UNMAPPED_CONFIG |
    | e3 | — | — | ν | 7, or `None` (Gaussian) | UNMAPPED_DOC |
    | e3 | — | — | ρ (`factor_rho`) | 0.40, or `None` (no factor) | UNMAPPED_DOC |
    | pca | `synthetic.rho` | 0.4 | ρ (`factor_rho`) [1] | 0.40, or `None` (no factor) | MATCH |
    | pca | `synthetic.backgrounds.SYNTH_GAUSS_EQUICORR` | null | ν [2] | 7, or `None` (Gaussian) | MATCH |
    | pca | `synthetic.backgrounds.SYNTH_T7_EQUICORR` | 7 | ν [1] | 7, or `None` (Gaussian) | MATCH |
    | pca | `synthetic.sr_annual_A` | 4.0 | — | — | UNMAPPED_CONFIG |
    | pca | `synthetic.rotation_deg` | 30.0 | — | — | UNMAPPED_CONFIG |
    | pca | `synthetic.rotation_pair` | [1, 2] | — | — | UNMAPPED_CONFIG |
    | pca | `synthetic.C_axes` | [10, 20] | — | — | UNMAPPED_CONFIG |
    | pca | `synthetic.C_I_target` | 3.0 | — | — | UNMAPPED_CONFIG |
    | pca | — | — | (α, β) | (0.08, 0.90) | UNMAPPED_DOC |
    | pca | — | — | burn-in | 1000 days | UNMAPPED_DOC |
- **Invariants checked in the closeout** (`review-verification.log`; no Git command, by instruction):
  - A SHA-256 manifest of 189 files, taken before RED, matches after reception (`review-protected-pre.sha256`). It covers `configs/`, `docs/`, `paper/`, `results/`, `Makefile`, `tools/trace_numbers.py`, the plan, the GO and the two earlier fragments.
  - `review-pre-hashes.log` matches for the plan, the GO, both Codex reviews and `tools/trace_numbers.py` (`e6a43a2d19456427814b6d332176d644f715459a85342cd462bef9e8f7b29548`). It also matches for `configs/e3.yaml` (`6e3857382200f0b7333419a1be33ea1623fe59b99e3e236abf6d97c615948b0b`), `configs/pca_drift_benchmark.yaml` (`79d2b5e5570743840b181689c3076b399a89b314d01fc3c5d1a043f25d473e99`) and `docs/sections/injection.md` (`8708a1df9d55975a7774777a2f56accd6e89ddd296becd2f1cd5a9a199a884b7`).
  - J1 `results/e2/e2_cells.csv` is `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` with 47 CRLF. The first phase also checked it in the index.
  - `.gitignore` line 9 ignores `logs/`. Since the runtime reference file, only `tools/appendix_b.py` and files in `logs/21-appendix/` changed (`find -newer`). No `__pycache__` or `.pytest_cache` was created.
  - Static check of the two real configurations: no anchor, alias or `<<` merge, and every key, flow mappings included, is a plain string. The stricter equality check therefore keeps the sentinel and the reception unchanged, as the runs confirmed.

## Errors and Dead Ends

- **Raw-text duplicate check (first phase, superseded).** The loader compared `ScalarNode.value` before merge flattening, which caused two defects.
  - It missed keys whose spellings differ but which build equal Python keys (`0x10`/`020`/`16`, `yes`/`true`, `~`/`null`, `1`/`1.0`/`true`), as well as merge overrides. PyYAML then kept the last value silently.
  - It refused distinct keys that share a text, such as `1` and `'1'`.
  - Fixed by comparing after SafeLoader construction (mutant `raw-text key check` killed).
- **Recursive flattening of a cyclic section (first phase, superseded).** `leaves` recursed through `d5: &d {loop: *d}` until `RecursionError`. That error is not caught by `main`, so the run ended with a traceback. It still exited 1 without writing, but gave no prefixed refusal. Fixed by a stdlib JSON circular-reference check before `leaves` (mutant `cycle check removed` killed).
- **Reading of "before any dictionary overwrite".** The check runs after SafeLoader has built the local dict of one mapping, and before that mapping is returned to the document. A reduced mapping therefore never reaches the inventory. Checking before the dict is built would mean reimplementing SafeLoader's key loop and its hashability check; the review asked to reuse SafeLoader instead.
- **Native absence rule and numeric tokens (plan phase, superseded by the GO).**
  - One absence row per documented row hid a deleted `alpha` while `beta` stayed present; each absent linked key now gets its own row.
  - A token regex allowed a false MATCH (`1,000 days` against 1); whole cells must now fit a bounded form.
- **First-phase details.** The plan expected RED as `ModuleNotFoundError`; the namespace package `tools` raised `ImportError` instead. The size estimate was about 110 lines, against 211 at the first phase and 218 now. Four test lines over 120 characters were rewrapped.
- No other failure, no repair loop, no circuit breaker reached.

## Current State

- `stream-21-appendix` is at `46c24923957ec505947016118def9453284bd1bc`, with no commit. Git was not run in the closeout, by instruction. The last `git status --porcelain --untracked-files=all` (first phase) listed these files; no other tracked path changed since, according to the manifest and `find -newer`:
  - `?? prompts/GO-stream-21-appendix.md` (Codex)
  - `?? prompts/plans/plan-21-appendix.md` (Codex)
  - `?? prompts/wrapups/wrapup-21-appendix.md` (this file)
  - `?? tests/test_appendix_b.py`
  - `?? tools/appendix_b.py`
- Ignored journals in `logs/21-appendix/`:
  - first phase: `pre-hashes.log`, `red.log`, `green-1.log`, `green.log`, `mutants.log`, `reception.log`, `reception-rerun.log`, `verification.log`, `appendix_b.md`, `appendix_b-determinism.md`;
  - Codex review: `codex-final-review.md`;
  - closeout: `review-pre-hashes.log`, `review-protected-pre.sha256`, `review-red.log`, `review-green.log`, `review-mutants.log`, `review-reception.log`, `review-reception-rerun.log`, `review-reception-checks.log`, `review-verification.log`, `appendix_b-review.md`, `appendix_b-review-determinism.md`.
- **Interface.** Run `python -m tools.appendix_b [--out logs/<dir>/<name>.md]` from the repository root; the default output is `logs/21-appendix/appendix_b.md`.
  - The output path must be canonical, relative, under `logs/` and end in `.md`. Its parent must already exist and resolve inside `logs/`. The tool creates no directory.
  - Writing is exclusive (`open(..., "xb")`).
  - Exit 0 means only that the inventory was written. Exit 1 is a refusal, and nothing is written.
  - Public functions: `leaves`, `section`, `documented`, `status`, `inventory`, `counts`, `render`, `target`, `main`. The private `_Loader` refuses equal constructed keys anywhere in a YAML file. `section()` refuses a cyclic selected section.
- **Contract.**
  - `SOURCES` lists `configs/e3.yaml` § `d5` and `configs/pca_drift_benchmark.yaml` § `synthetic`. `NOTE` is `docs/sections/injection.md`, read under the heading `## D5 — Monte Carlo backgrounds` with the exact header `parameter | values`.
  - `LINKS` holds 6 entries: `d5.alpha`→(α, β)[1], `d5.beta`→(α, β)[2], `d5.burn`→burn-in[1], `synthetic.rho`→ρ (`factor_rho`)[1], `…SYNTH_T7_EQUICORR`→ν[1], `…SYNTH_GAUSS_EQUICORR`→ν[2].
  - `FORMS` holds 4 entries, over numbers without a sign, exponent, grouping or leading zero: `(x, y)`, then ``x, or `None` (text without digits)`` for ν and ρ, then `x days`.
  - Rows are ordered per source: its leaves in document order, then its absent linked keys, then the documented rows it does not link.
  - The closeout changed neither forms, links, statuses, caveat, rendering nor output confinement.
- **Not run by Claude** (GO and review): the full `make check` (Codex's closing hook), reindexation, staging, commit, push and any branch or base change. The TDD skill's full-suite step is deferred to that hook. Only the lot's test file and `tests/test_trace_numbers.py` were run.

## Vigilance Points

- **Partial inventory.** Only declared values are listed. Code literals stay invisible: ν = `sim.NU` for E3 t7, and α = β = 0 with `burn=0` for the PCA synthetic paths. The fragment does not describe what the experiments run.
  - UNMAPPED_CONFIG and UNMAPPED_DOC are link-scoped. Some unmapped values occur elsewhere in the note, for instance SR 4 in the amplitude grid and θ = 30° in the F4 grid.
- **The sentinel breaks on purpose (Q5)** at any edit of the three inputs, since it pins their SHA-256 and the 17 rows. A lot that edits `configs/e3.yaml`, `configs/pca_drift_benchmark.yaml` or `docs/sections/injection.md` must update it.
- **Form ceiling** (`# ponytail:` in the tool). Only the four current D5 rows have forms. A reworded cell becomes UNSUPPORTED_DOC_VALUE, never MATCH. A newly linked row needs its own form.
- **Equal keys follow Python dict equality**, since that decides what PyYAML would overwrite.
  - `true` collides with `1`, and `1.0` with `1`.
  - A `<<` merge whose key is overridden is refused, although YAML 1.1 defines explicit keys as taking precedence. A merge without override is accepted.
  - The rule covers the whole file, unselected sections included.
- **Cycle scope.** Only the two selected sections are checked. A cycle elsewhere in the file is accepted, because it is never traversed. Finite alias reuse inside a section is accepted and listed once per path.
- **Residual uncontrolled paths, outside the two authorized corrections.** These come from a static reading of PyYAML 6.0.3 and were not executed.
  - PyYAML's recursive composer should raise `RecursionError` on YAML nested a few hundred levels deep, anywhere in a file. The run would then end with a traceback, exit 1 and no output, but without the prefixed refusal.
  - A decimal integer of more than 4,300 digits raises `ValueError` in the PyYAML constructor. The refusal would print without the input prefix.
- **Invocation.** Only `python -m tools.appendix_b` from the repository root works (Q3). `python tools/appendix_b.py` fails on the import of `tools.trace_numbers`.
- **Rendering.** Configured values appear as JSON of the parsed YAML: `0.90` appears as `0.9`, and YAML 1.1 idioms appear as parsed.
- **Helper messages.** Errors of `trace_numbers.table()` mention `MAPPING`, since the helper is unchanged; this tool prefixes them with the note path.
- **Untouched.** D8 remains FAIL at +5.2833 %, not examined. J1 is unchanged. No paper table, MAPPING entry, result, configuration, Makefile or shared helper was touched.

## Recommendations

- **Codex closeout.**
  - Run `make check` through the closing hook; the lot's tests read only the two configurations and the note, in under one second.
  - Stage by explicit path: `tools/appendix_b.py`, `tests/test_appendix_b.py`, `prompts/wrapups/wrapup-21-appendix.md`, the plan and the GO. Never stage `logs/21-appendix/`.
- **Residual paths.** If the prefixed-refusal promise must cover deep nesting and oversized integers too, catching `RecursionError` and `ValueError` around `yaml.load` in `section()` is a one-line change. It needs its own GO and witnesses.
- **F1–F4 grids.** If Appendix B needs the drift grids (r, θ, κ, SR), they need a new mandate and a structured source: a parameter table in the note, or a declared configuration section. Extracting them from prose stays out of scope.
- **Families table.** Linking `synthetic.rotation_deg` or `rotation_pair` to it would need a reader that keeps cells with several backtick pairs; `trace_numbers.table()` strips one pair and must stay unchanged.
