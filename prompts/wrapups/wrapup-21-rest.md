# Wrapup — Stream 21-rest, Lot P: nine analytic values of Section 3 traced to a CSV

## Context

- **Mandate.** Codex framing of 2026-11-07 (user mandate) for the remainder of stream 21: map the 13 result-bearing occurrences of `paper/sec3_theory.tex` without a CSV source, and delimit a minimal runner and freeze architecture. Base `1440927b49463c13bdd0c819fcd73f30d6a32c31`, branch `stream-21-rest`, interactive session `jepa-s21-rest`.
- **Workflow.**
  - Claude wrote a native plan in plan mode with read-only commands, then a revision after the Codex review. The review covered FAIR levels, the two `2.01`, a verifiable freeze, runner identity and monitor reading.
  - The researcher approved the plan and granted the **GO for Lot P only (direct)**. Codex recorded the decision in `prompts/plans/plan-21-rest.md` (SHA-256 `6cde3a60a0167d71a8e4f3510dffe027d8301225864ad44e1118dcafa9bbb1b9`) and `prompts/GO-stream-21-rest.md` (`379bd67bfde3393ea33d2f8447363f61b59e8aee34fbe61a430eb432c6682e62`). Claude read both before any edit and did not modify them.
  - Lot A (intermediate code pins) was dropped. Lots F (freeze tool) and R (runner) and the J4 activation were not executed. Lot S (sources of the l. 111 ranges) belongs to Codex and the researcher.
- **Lot P scope.**
  - An analytic producer writes a new CSV through `save_fair_csv`.
  - `tools/trace_numbers.py` gains several sources, decimal literals, occurrence IDs and quantity anchors.
  - `docs/MAPPING.md` receives nine new entries.
  - Target: 15/19 result-bearing occurrences, counted only after real verification.
- **Execution protocol.** Before every project import or run, Claude read the shared registry in the main tree (`logs/orchestration_20261107/execution-19-21-state.json`). It required `science_owner` = `stream-21-rest` and `closeout_owner` = null, then ran the command under `flock -n -E 75` on the lock named there.
  - Interpreter: `.venv/bin/python -B`.
  - Environment: `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`, and `PYTHONPATH` prefixed with `external/torch-cf-shim`.
- **Agent.** Claude Code, Opus 5.5, effort max, one interactive session from planning to closure, no subagent. Codex accepted Lot P after an independent review that found no blocking or important defect. The wrap-up was invoked in the closeout slot that Codex allocated (`closeout_owner` = `stream-21-rest`).

## Validated Results

- **Deliverables (SHA-256)**, identical to the values received by Codex:
  - `experiments/sec3_analytic_values.py` (new): `043dadd41cd719263d8ecf6ad6a0e4bff72ab3aa908d4cad4fe0dcdf76caa7e7`
  - `results/sec3/sec3_analytic.csv` (new; header and 9 rows, LF line endings): `de6217be14498bb486458257f0d615261b818fea58e18dcfe94c910d4bf0921a`
  - `tools/trace_numbers.py`: `274a3d618cd02253baff288d57b1d61ea69f1d2c5d366460c9d616a7ec3afbc3` (base `e6a43a2d19456427814b6d332176d644f715459a85342cd462bef9e8f7b29548`)
  - `tests/test_trace_numbers.py`: `a9b76b469190adf3f20a9e4033288886b1363bdc7eb73eebf00a82a77d514807` (base `fa958e97c877b8b4134cb5ce619788b7bdf2ca014e6ed7976a97715eef635d2e`)
  - `docs/MAPPING.md`: `6dcf06ff393163c129ce17e2916e1a045cbdbe846c89f8722771f8b3b345492c` (base `edb3cb2b9681924bc6972a3712d0e3f07056ac5979ec8cd6a3cc0c501c875086`)
- **TDD.** All runs used `.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_trace_numbers.py`; journals are in `logs/stream_21_rest/`.
  - **RED-1** (13:33:06Z): tests written; producer absent; tool and MAPPING unchanged.
    - Result: **65 failed, 83 passed**. The 83 are the pre-existing cases left unchanged: 88 minus the 5 real-MAPPING cases whose expectations moved to 15 entries.
    - Every failure was behavioural: refusals not raised, Source entries ignored, `ModuleNotFoundError` for the producer, CSV absent.
  - **Producer** (13:33:40Z): 4 producer tests passed. The committed-CSV test kept failing until the CSV existed.
  - **CSV run** (13:33:50Z): `.venv/bin/python -B experiments/sec3_analytic_values.py --out results/sec3/sec3_analytic.csv`, exit 0.
  - **Checker extended** (13:35:48Z): 141 passed. The 7 tests on the real MAPPING kept failing, pending the MAPPING update.
  - **MAPPING updated** (13:37:25Z): 148 passed.
  - **Final GREEN** (13:38:44Z): **150 passed**, after adding the key-and-source-text exchange witness.
- **Real CLI.** `.venv/bin/python -B tools/trace_numbers.py` exits 0 with `15/15 entries READ_MATCH; verified subset 15 of 19 result-bearing occurrences, 4 of 19 not covered`. The six J1 entries are unchanged. The nine Source entries:

  | ID | Literal (line) | Cell | Rounded | Reading; approximation |
  |---|---|---|---|---|
  | `ARL0ADD-G252-SR1` | `1.8` (52) | `1.7741629469770654` | 1.8 | exact; diffusion |
  | `M-D1-G504` | `1.22` (80) | `1.2239421009676335` | 1.22 | anytime-valid; fluid |
  | `M-D10-G504` | `2.01` (80) | `2.0057517760705341` | 2.01 | anytime-valid; fluid |
  | `M-D64-G504` | `3.91` (80) | `3.905601272609708` | 3.91 | anytime-valid; fluid |
  | `M-D500-G504` | `9.64` (80) | `9.6426581917156557` | 9.64 | anytime-valid; fluid |
  | `M-D128-G504` | `5.2` (80) | `5.2252126569106583` | 5.2 | anytime-valid; fluid |
  | `ABS-R2.5` | `2.01` (105) | `2.0117973905426254` | 2.01 | budget; fluid |
  | `ABS-R4` | `1.39` (105) | `1.3862943611198906` | 1.39 | budget; fluid |
  | `ABS-R8` | `1.15` (105) | `1.1507282898071236` | 1.15 | budget; fluid |

  The four l. 111 endpoints (`13`, `16`, `8`, `11`) remain `UNSOURCED`.
- **The two `2.01`.** Both cells round to 2.01, so the value alone cannot separate them. The checker binds each Source entry instead:
  - the anchor of its quantity must stand on the declared LaTeX line (`$M=` on l. 80, `\tau_a/\tau_\gamma=` on l. 105, each absent from the other line);
  - the selected row must carry the entry's `id`, `anchor`, `reading` and `approximation`.
  - Witnesses, on a fixture and on the real MAPPING:
    - keys exchanged gives `BINDING_MISMATCH`;
    - keys and source texts exchanged gives `BINDING_MISMATCH`;
    - all references exchanged (ID, anchor, reading, approximation, key, source text; location and literal kept) gives `ANCHOR_ABSENT`.
- **Overwrite refusal and determinism.**
  - The producer opens `--out` by exclusive creation. An existing file and a dangling symlink are both refused with exit 1 and `sec3-analytic: error: <out> exists; refusing to overwrite it`; the existing bytes are kept and no link target is created.
  - Two runs into two new files are byte-identical.
  - A fresh run equals the committed CSV (`test_committed_sec3_csv_equals_a_fresh_run`).
- **Producer checks (tests).**
  - Absorption rows equal (5/4) ln 5, 2 ln 2 and 4 ln(4/3) at relative 1e-12.
  - Mixture rows satisfy x = A + (D/2) ln(1 + 2x/D), A = ln 504, at relative 1e-11.
  - The ratio row equals exactly 252 / `142.0388135314031`, the J1 `pred_delay` of MAPPING entry 2.
  - The only project imports are `jepadrift.floors` and `jepadrift.pipelines.save_fair_csv`, plus pandas.
  - There is no PRNG, no E2 arm and no read of `results/e2`.
- **Mutants** (13:38:45Z): 12 of 12 killed.
  - Method: each mutant was exec'd in memory into the imported module, in a fresh process, from a script in the session scratchpad outside the repository. The file hashes were checked unchanged afterwards.
  - Failures per checker mutant:
    - anchor check removed: 3, only the full-exchange and anchor-not-on-line witnesses;
    - binding check removed: 8;
    - half-up rounding: 5;
    - integer quantum: 25;
    - sources ignored: 62;
    - duplicate CSV allowed: 1;
    - decimal allowed in Entries: 1;
    - approximation unchecked: 1.
  - Failures per producer mutant:
    - anchors exchanged: 2;
    - overwrite allowed: 1;
    - non-finite value accepted: 1;
    - infeasible `cusum_exact` accepted: 1.
- **Targeted controls** (13:39:34Z):
  - **312 passed**: trace tests, `tests/test_dpi_lint.py`, `tests/test_appendix_b.py` and `test_e2_cells_crlf_disk_and_index_unchanged`.
  - pyflakes reports nothing on the three Python files. The only comments are `# ponytail:`, no line exceeds 120 characters, and the deliverables hold no absolute path.
  - `table()` and `confined()`, which `dpi_lint` and `appendix_b` import, are byte-identical to HEAD. So are the Check inputs and Entries tables of MAPPING.
- **Integrity.**
  - J1 disk = index = `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`: 47 lines, 47 CRLF, 0 isolated LF.
  - `results/e3/e3_overshoot.csv` is `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`. D8 remains FAIL at +5.2833 % and was not examined.
  - `paper/sec3_theory.tex` is `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013`.
  - No `configs/FROZEN.json`, and no tracked change outside the lot.

## Errors and Dead Ends

- **`sed -i` edit.** One line of `tests/test_trace_numbers.py` (line 56, the swap constants `SWAPS` and `SWAP_IDS`) was replaced with `sed -i` instead of the native edit tool, against the editing rule. The file was re-read and the change verified by the final GREEN run and the mutants. Codex then required native edits only, which every later edit used.
- **Plan phase.** One `python3 -c "pass"` ran by mistake with the system interpreter: no import, no file. It was declared in the native plan.
- **Corrections from the Codex review of the native plan.**
  - The nine code pins of the dropped Lot A could not close the CSV contract; coverage stayed 6/19 until Lot P.
  - A set of (location, literal) pairs could not reject an exchange of the two `2.01`.
  - The freeze, runner-identity and monitor-reading statements needed the precision given in revision 1.
- **Design choices against the plan text.**
  - Occurrence IDs carry no line number (`M-D10-G504`, not the illustrative `S80-M-D10`), so the producer does not depend on the paper's line numbering.
  - The witness with keys and source texts exchanged was added after the first GREEN. The key-only exchange is also caught by the source-text check; this witness alone isolates the binding check (binding mutant).
- **Refusal order.** In the Entries table, reading and declared status are now checked before the decimal-literal refusal, through the shared `located()` helper. Messages are unchanged.

## Current State

- **Git (pre-commit state).** Branch `stream-21-rest` at base `1440927b49463c13bdd0c819fcd73f30d6a32c31`. Claude ran no commit, staging, reindexation or push. The last recorded `git status --porcelain` (13:39:34Z) gave:
  - ` M docs/MAPPING.md`
  - ` M tests/test_trace_numbers.py`
  - ` M tools/trace_numbers.py`
  - `?? experiments/sec3_analytic_values.py`
  - `?? prompts/GO-stream-21-rest.md` (Codex)
  - `?? prompts/plans/plan-21-rest.md` (Codex)
  - `?? results/sec3/sec3_analytic.csv`
  - this wrapup adds `?? prompts/wrapups/wrapup-21-rest.md`.
- **Ignored journals** in `logs/stream_21_rest/`: `precheck`, `red1`, `green_producer`, `producer_run`, `green_tool`, `cli`, `green`, `green_final`, `mutants`, `controls` (`.log`).
- **Interfaces.**
  - **Producer.** `python experiments/sec3_analytic_values.py --out <new file>` writes 9 rows with the columns `id, quantity, parameters, reading, approximation, anchor, value` and prints `<sha256>  <out>`. It exits 1 when `--out` exists, and raises `ValueError` on a non-finite or non-positive value or on an infeasible `cusum_exact`.
  - **Checker.** `python tools/trace_numbers.py`.
    - The single-source format (Check inputs and Entries) is unchanged and still refuses decimal literals.
    - Two optional tables are added: `## Sources` (`Source | CSV | CSV SHA-256 | Key columns | Entries`) and `## Source entries` (`ID | Source | LaTeX location | Literal | Anchor | Reading | Approximation | Full key | Column | Source text | Rounded | Status`).
    - Statuses: `LITERAL_OCCURRENCES_n`, `ANCHOR_ABSENT`, `UNKNOWN_COLUMN`, `KEY_ROWS_n`, `BINDING_MISMATCH`, `EMPTY_OR_NON_FINITE`, `MISMATCH`, `SOURCE_TEXT_MISMATCH`, `READ_MATCH`.
    - `check()` returns `inputs` with an added `Sources` list.
- **Codex closure, not yet done:** AST reindexation without AI summaries, full `make check`, commit, fetch/rebase, pushed-range control and push. Under the later user order, every push is authorized without a new confirmation. Push 19 is integrated at `8b1f6db97878a539e1ecb7e16db05b21cf7f3efa`.
- **Environment.** Python 3.12.9 through `.venv/bin/python`, built on the Trading 3.12.9 base interpreter. pytest and pyflakes come from `.venv`, and `PYTHONPATH` is prefixed with `external/torch-cf-shim`. Nothing was installed.

## Vigilance Points

- **What a Source entry certifies.** A `READ_MATCH` certifies literal, analytic cell and rounding only: no measured delay, ARL0 or FPR, and no reproduction of a measurement. Readings and approximations stay named.
  - Mixture rows: anytime-valid, fluid.
  - Absorption rows: budget, fluid.
  - `1.8`: exact reading (ARL0 calibration) with the diffusion approximation Φ(γI)/I, not an exact ADD at finite γ.
- **Anchors are lexical.** They show that a text stands on the declared line, not the meaning of the sentence. If an equal literal ever shares its line with a homonymous quantity, separating them needs a positional rule under a new GO.
- **Tripwires.** Any byte change of `paper/sec3_theory.tex`, `results/e2/e2_cells.csv` or `results/sec3/sec3_analytic.csv` fails `make check` until MAPPING is re-verified. A change in the producer's output fails `test_committed_sec3_csv_equals_a_fresh_run`.
- **M(1, 504) differs across solvers.** `floors` gives `1.2239421009676335`; the sealed PCA manifest holds `1.2239421009676454` from `pdb.mixture_cost`, another solver. Both round to 1.22, and the existing PCA test bounds their relative gap at 1e-10. This is not a reproduction failure.
- **CLI caveat line.** It now ends with `; a Source entry keeps the fluid or diffusion approximation it names`. The CLI journal hashes recorded by lots 21-trace and 21-dpi no longer describe the current output.
- **Ceilings (`# ponytail:`).**
  - Contiguous numeric forms only.
  - One LaTeX file per MAPPING.
  - Decimal literals only through Source entries; Entries keep the zero-decimal contract.
- **Out of scope.**
  - The l. 111 ranges stay `UNSOURCED`: the CV²·τ_int definition, estimator, window, SR/γ/mode and producer are unknown. This is Lot S, for Codex and the researcher; Claude sent no external message.
  - Lots F and R are not implemented.
  - There is no `FROZEN.json`, Makefile change, J4 activation, PRNG, new simulation, real data or training.
  - E1 still loads its whole panel before restricting rows; a bounded reader before I/O has not been produced.

## Recommendations

- **Codex closure.**
  - Stage by explicit path: the five deliverables, this wrapup, the plan and the GO.
  - Run the full `make check` after the AST reindexation.
  - Re-check the J1 hash on disk and in the index, its 47 CRLF and the E3 hash.
  - In the pushed range, check that no path lies under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` and that no file exceeds 50 MB.
- **Deviations.** If wanted, record in `docs/DEVIATIONS.md` (Codex, French) the extension of the checker beyond the single-CSV contract of prompt 21, and the line-number-free occurrence IDs.
- **Lot S.** Request the definition and the producer behind the l. 111 ranges. Any source enters through a separate lot (producer, then CSV, then Source entries), under its own mandate if a simulation is needed.
- **Lots F and R.** Keep Lot F on fixtures under its own GO. Start Lot R only after the E5 protocol and a bounded reader before I/O.
