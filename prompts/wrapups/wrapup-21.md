# Wrapup — Stream 21: traceability scope (documentary lot)

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md` (2026-11-06), on base `69d562419be77b17af9e56711a6ae069caa6bfc4`, worktree and branch `stream-21`. Prompt 21 covered six items: J4 freeze, `benchmark_runner`, figures, `trace_numbers`, `dpi_lint` and `appendix_b`. The mandate reduced it to the traceability of numbers already reported, independent of stream 19 and of trained models.
- **Workflow.**
  - Claude produced a native plan. Codex archived it as `logs/orchestration_20261106/native-plan-reviewed.md` (SHA-256 `03da31042270fd859d7888683d40d628803d24f284dcb5312fd8b0f1f4f2c490`).
  - Codex then recorded `prompts/plans/plan-21.md`, with its integrated GO decision, and `prompts/GO-stream-21.md` (17:49 UTC).
- **GO decisions.**
  - Q1: audit and MAPPING without code.
  - Q2: `1.8` appears only in the audit, as an unverified derived candidate.
  - Q3: `docs/MAPPING.md` is a separate file with full keys, the CSV SHA-256 and the producer script.
  - Q4: the census is limited to `paper/*.tex` and measured by occurrence.
  - Q5: gaps are reported, not corrected.
  - A read-only standard-library check under `.venv/bin/python` was authorised.
- **Agent.** Claude Code, Opus 5.5 (`claude-opus-5-5`), interactive, effort max, no subagent. A usage limit interrupted the session once, after the audit and MAPPING edits. The user resumed it; the state was intact and nothing was re-run.
- **Codex review, round 1** (`logs/stream_21/codex-review-round1.md`). Three documentary clarifications were applied, with no new row, value, tool or test:
  1. MAPPING now says "without a repository checking tool" and points to the one-off read check.
  2. MAPPING and audit §3 and §8 now state that **exact** names the ARL0-calibrated reading. The stored Φ(γI)/I values are the diffusion approximation (`C-e1-readings`, `docs/DEVIATIONS.md`): neither an exact ADD at finite γ nor a certification of attained ARL0.
  3. The read-check script is now called "not a tracked source or tool"; its recorded command and evidence are kept.

  The read check was not re-run: its inputs were re-hashed at 19:11:54Z and found unchanged, and the six MAPPING rows are byte-identical.

## Validated Results

- **Census of `paper/*.tex`.**
  - Command: `command grep -noE '[0-9]+(\{,\}[0-9]{3})*(\.[0-9]+)?'` (GNU grep 3.6).
  - Tokens: 507 (`sec3_theory.tex` 222, `appA_proofs.tex` 285). Tagged numbers (`\E{}`): 0. `\newcommand`: 0.
  - The classification is manual. A per-line cross-check of class counts against token counts found `bad=0` over 68 lines.
  - Class totals: R 19, P 18, B 1, K 2, C 29, L 4, S 7, H 15, F 412.
  - The 19 result-bearing occurrences are all in `sec3_theory.tex`: l. 52 (7), l. 80 (5), l. 105 (3), l. 111 (4).
- **Status of the 19.** 6 `READ_MATCH`, 1 `DERIVED_CANDIDATE` (`1.8`), 5 `ANALYTIC_TEST_REFERENCE` (`1.22`, `2.01`, `3.91`, `9.64`, `2.01`), 3 `ANALYTIC_UNPINNED` (`5.2`, `1.39`, `1.15`), 4 `UNSOURCED` (the endpoints `13`, `16`, `8`, `11` of two ranges). No global rate is stated.
- **Read check.**
  - Command: `.venv/bin/python -I - < read_check_e2.py`, at 17:59:41Z. Script SHA-256 `ea5d348bc040dfe20c91462e7b4ed9450d9862c929f2c0cf4a8a0eac3b0f61b1`. The script is not a tracked source or tool; it is reproduced verbatim in audit §3.
  - Exit 0. Every key also holds `arm=G1, background=gauss, dim=1, sr_annual=1.0`.

    | Literal | Key | Column | Cell | Rounded | Status |
    |---|---|---|---|---|---|
    | `17` | cusum_x, γ 20 | `pred_delay` | `16.71475236584297` | 17 | `READ_MATCH` |
    | `142` | cusum_x, γ 252 | `pred_delay` | `142.0388135314031` | 142 | `READ_MATCH` |
    | `1{,}510` | onset, γ 20 | `first_order` | `1509.849065871212` | 1510 | `READ_MATCH` |
    | `2{,}787` | onset, γ 252 | `first_order` | `2786.832260105758` | 2787 | `READ_MATCH` |
    | `1{,}066` | cusum_t, γ 20 | `pred_delay` | `1066.2595750101377` | 1066 | `READ_MATCH` |
    | `2{,}322` | cusum_t, γ 252 | `pred_delay` | `2321.684670063548` | 2322 | `READ_MATCH` |

  - The CSV SHA-256 was identical before and after the read.
  - Three negative witnesses each exited with code 1:
    - W1 reads `mean_delay`: `MISMATCH`.
    - W2 uses literal `18`: `LITERAL_OCCURRENCES_0`.
    - W3 drops `mode` from the key: `KEY_ROWS_3`.
- **DPI pattern scan** (prompt 21 §5 patterns):
  - `increase[sd]?.*(KL|information|divergence)`: 0 lines.
  - `creates? information`: 0 lines.
  - `creates?.*information`: 1 line (sec3 l. 25, "creates no information"). This is a correct negation, so a false positive.
- **Integrity**, checked at 17:54:39Z, 18:21:47Z and 19:11:54Z, and again in the round-1 final controls (`logs/stream_21/final_controls_round1.log`):
  - `results/e2/e2_cells.csv` on disk and in the index = `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`; 47 lines, 47 CRLF, 0 without CR.
  - `HEAD` is the base, and no tracked file is modified.
  - The two documents contain no absolute personal path.
  - D8 remains FAIL at +5.2833 % and was not re-examined.
- **Outputs (SHA-256):**
  - `docs/MAPPING.md`: `7e11e00fc8564186d780cfac1c882af04f60576abaa43d33405a9d312921910d` (before review round 1: `62739d29dbb1815016c5d08615bca7670d22be878536a2269de44b0235cc9f5a`)
  - `docs/audits/stream_21_trace_scope_2026_11_06.md`: `40bfb66ceee50503cb9dcfa463b7277d315d1b4752471d685e880ee83b1fc8cb` (before review round 1: `1fb61a671182ac9758aef44c3ea2e889b5a1da53a5e382245286dcfff7142f09`)
- **Inputs (SHA-256 at the base):**
  - `paper/sec3_theory.tex`: `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013`
  - `paper/appA_proofs.tex`: `4a5469c84f12bb5902fee9f68a783b64c45b77b11f1172c5bf4b81f7603c2a30`
  - `experiments/e2_floor_validation.py`: `f4360ac3961fcd01e36824cb10d3572be0ec83d767ee17bc56010840de4b46c7`
  - `jepadrift/floors.py`: `49b36c5ef1b7995a274243180825731d42a61829c70e00fc7fc72841d39a9170`
  - `tests/test_floors.py`: `0457f3e8f7828324986a384d0e53175061e54d010d95d99666c768369138dc29`
  - `results/e2/J1_report.md`: `7a53b80dce0d1c78f3e34d145e02d5a9a94f53e0bef2070f2197141aad7f1831`

## Errors and Dead Ends

- **Plan-phase argument withdrawn by the GO.** The plan argued that fixture-only tests could not cover real numbers. GO Q1 withdrew that argument, because read checks on sealed CSVs are allowed. The no-code decision now rests on scope alone: 0 tagged numbers.
- **`1.8` ratio.** The plan wrote the operands as "252/142.04". The GO requires the candidate to stay unverified, so the audit names the operand columns and evaluates no ratio.
- **Entry 1 column choice.** For entry 1, `mean_delay` (16.730) and `pred_delay` (16.715) both round to 17. A draft sentence claiming the two columns differ at the printed precision in general was corrected before delivery. The audit and MAPPING now state that the entry is tied to `pred_delay` by the sentence ("Φ gives …"), not by the rounded value.
- **Cross-check bug.** The first per-line cross-check split the class file on `:` and reported 68 false mismatches. The checker was fixed to split on spaces and returned `bad=0`; the data did not change.
- **Shell `grep`.** The interactive `grep` is a shell function wrapping ugrep, which hit a regex complexity limit during planning. Every recorded command uses `command grep` (GNU grep 3.6).
- **Imprecisions found by Codex review round 1**, all corrected:
  - "without a checking tool" implied that no check occurred.
  - The **exact** reading label read as if the Φ(γI)/I value were an exact delay; `C-e1-readings` reserves that value as a diffusion approximation.
  - "not a repository file" was replaced by "not a tracked source or tool".

## Current State

- **Git.** Branch `stream-21` at the base, no commit by Claude.
- **Untracked files.**
  - Claude: `docs/MAPPING.md`, `docs/audits/stream_21_trace_scope_2026_11_06.md`, `prompts/wrapups/wrapup-21.md`.
  - Codex: `prompts/GO-stream-21.md`, `prompts/plans/plan-21.md`.
- **Ignored journals** in `logs/stream_21/`: `precheck`, `census_tokens`, `census_classes`, `census_crosscheck`, `read_check_e2`, `read_check_e2_witnesses`, `dpi_pattern_scan`, `postwrite_controls`, `final_controls`, `review_round1_controls` and `final_controls_round1` (`.log`). The Codex review file `codex-review-round1.md` sits in the same ignored directory.
- **Not run by Claude, per the GO:** pytest, `make check`, pyflakes, reindexation, Git. Codex owns review, `make check` through the pre-commit hook, the AST-only reindex (`tools/reindex_graphify_jcodemunch.sh`), commit and push.
- **Environment.** Python 3.12.9 (`.venv/bin/python`, built on the Trading 3.12.9 binary), GNU grep 3.6, GNU Awk 5.1.0, with the GO exports `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`.
- **Base verification**, recorded by Codex in the mandate: pyflakes clean, 37 + 589 passed, 5 pre-existing D4 skips, G1 enabled with `PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv`.

## Vigilance Points

- **Meaning of `READ_MATCH`.** It attests only literal = rounded analytic cell. It certifies no ARL0, FPR or ADD reading, no scientific conclusion and no other sentence, and it claims no reproduction by the current code.
  - For entries 1 and 2, **exact** names the ARL0-calibrated reading. Their values are Φ(γI)/I diffusion approximations (`C-e1-readings`), not exact ADD values at finite γ.
- **Locators.** MAPPING line numbers are valid only for `sec3_theory.tex` at SHA-256 `6bfebdd0…4013`. Any edit of `paper/` requires re-running the read check of audit §3.
- **Thirteen unmapped occurrences**, none declared wrong:
  - `1.8` is unverified.
  - The five test references come from tests that were not run in this lot.
  - `5.2`, `1.39` and `1.15` have no test or CSV.
  - The ranges 13–16 and 8–11 have no identified source. The E2 producer docstring says "about 10-15 days here" where the paper says "13 to 16"; the difference is recorded and left unresolved.
- **Manual classification.** The census classes are assigned by hand and may be reclassified on review: for example B `D\le16`, or the F exponents of `cor:scaling`.
- **Codex closure.**
  - The GO and plan files must be committed with the stream.
  - Check the J1 hash, the 47 CRLF, and the absence of `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` paths and of files over 50 MB in the pushed range.
  - The pre-commit `make check` exceeds the 5-minute target (a known debt).

## Recommendations

- Review audit Appendix A (classification) and the six MAPPING rows. The read check can be re-run from the verbatim script in audit §3.
- Open gate G-T (`tools/trace_numbers.py`, `tests/test_tools.py`) only when `paper/` gains a CSV-sourced number outside E2, or a tagged number. Until then, extend MAPPING by hand with its row contract and the same read check.
- Sources for the ranges in l. 111 come from the authors of `sec:exp-floors`. Pinning `5.2`, `1.39` and `1.15` in `tests/test_floors.py` needs a separate GO.
- Keep the freeze, `FROZEN.json`, runner, figure scripts and `appendix_b` under a distinct J4 GO, with a single runner that reuses `experiments/pca_drift_benchmark.py`.
