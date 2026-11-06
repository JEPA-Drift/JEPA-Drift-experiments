# Wrapup — Lot 21-trace: executable check of the six E2 correspondences of MAPPING

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md` (2026-11-06), on base `3467df4b7426fa15c1ab16ef94687f25a976636d`, in the Codex worktree of branch `stream-21-trace`. The lot is separate from documentary lot 21 and from the J4 freeze. Lot 19-oracle provides no input to it.
- **Problem.** The six `READ_MATCH` correspondences of `docs/MAPPING.md` (`paper/sec3_theory.tex` l. 52 against `results/e2/e2_cells.csv`) had one verification only: the archived one-shot read check of audit 21 §3. Nothing in `make check` reacted to an edit of the paper, of a key or of a column.
- **Workflow.**
  - Claude wrote a native plan. Codex archived it as `logs/orchestration_20261106/native-plan-reviewed.md` (SHA-256 `ddf45a147204320993758763ece4ee516c5b041ede13ecb8422c689ae4f568ca`).
  - Codex then recorded `prompts/plans/plan-21-trace.md` (SHA-256 `809c0a0f30f26989070b5d57e821103bd1db6c9f577ce9991ed25e67de512ced`), with its integrated GO decision, and `prompts/GO-stream-21-trace.md` (SHA-256 `42c06cae69f05d1af1f0aefa18c251caac3ff16f439e8e280bbcdc7c832bd517`), at 20:10 UTC.
  - Both files were read in full and hashed before the first write (pre-check at 20:17:32Z) and after each round. They are unchanged.
- **GO decisions.** The integrated decision prevails over the native plan.
  - Q1: Codex opened a reduced gate G-T. This revises Codex's own YAGNI decision of documentary lot 21; it is not attributed to the researcher.
  - Q2: a `Check inputs` block with seven rows, including `Key columns` = `arm, mode, background, dim, sr_annual, gamma`. The six Entries rows and the historical prose stay intact.
  - Q3: no separate validation note; the evidence is in this wrapup and in the ignored journals.
  - Q4: no `docs/DEVIATIONS.md` entry.
  - Q5: the test on the real MAPPING pins a sentinel: the counts 6 and 19, the six (location, literal) pairs and the six key-column names.
  - The GO revised two plan hypotheses. H2: every key names exactly the Key columns before row uniqueness is checked. H10: the full `make check` belongs to the Codex hook.
  - A decimal literal is refused explicitly.
- **Codex review, round 1** (`logs/stream_21_trace/codex-review-round1.md`, SHA-256 `14bf7c162fae925ebce58ca9655b4ea3d8d3d2e29cf495179101671939dacced`).
  - Codex replayed the 73 tests independently, all passing, then reproduced three false acceptances with the test fixture builder, each keeping only ROW1:
    - TeX `-17 and` returned `READ_MATCH`;
    - TeX `1e17 and` returned `READ_MATCH`;
    - a CSV row `G1,x,20,16.71,"16.7` with an unterminated quote returned `READ_MATCH`.
  - It required three bounded corrections, test-first:
    1. Match a complete unsigned integer numeral, and refuse unsupported numeric forms, including a Unicode-minus witness.
    2. Parse the CSV strictly, refusing an unterminated quote even outside the mapped column.
    3. Treat key completeness as set equality without duplicates, not as an order. A permuted key must pass.
  - All three were applied in the same session.
- **Agent.** Claude Code, Opus 5.5 (`claude-opus-5-5`), one interactive session, effort max throughout, no subagent. The CLI switched to auto mode after the GO was recorded.

## Validated Results

- **Outputs after review round 1 (SHA-256):**
  - `tools/trace_numbers.py` (196 lines, standard library only): `e6a43a2d19456427814b6d332176d644f715459a85342cd462bef9e8f7b29548`. Round 0: `aca0752509f2b1d9f6a13114c2a80f5b2909b1a926b9d61053db7c52353754ec`.
  - `tests/test_trace_numbers.py` (289 lines, 88 test cases): `fa958e97c877b8b4134cb5ce619788b7bdf2ca014e6ed7976a97715eef635d2e`. Round 0: `59908603b2cba41ecd3c6da9665b6d2e29c1473694d9845279e7668718e1626f`.
  - `docs/MAPPING.md`: `edb3cb2b9681924bc6972a3712d0e3f07056ac5979ec8cd6a3cc0c501c875086`. Round 0: `b91a0364d3bac772dea46552d2bb41b2283629bb1790d3c386697dea8b638abf`; base: `7e11e00fc8564186d780cfac1c882af04f60576abaa43d33405a9d312921910d`.
    - Against the base, `git diff --numstat` still gives +15/−0, and the six Entries rows are byte-identical (`diff` against `git show HEAD:docs/MAPPING.md`).
    - Round 1 rewrote only the usage paragraph that this lot had added. It now also states strict CSV parsing, keys in any order and the complete-numeral rule.
  - Real CLI journals `logs/stream_21_trace/cli.log` and `review1_cli.log`: both `ff21dacc6101fd740cfb1825206194bd405b31733fd939a2e030f33611481ecd`. The output did not change from round 0 to round 1 (`cmp`).
- **Round 0 TDD** (all runs with `.venv/bin/python -m pytest -q tests/test_trace_numbers.py`):
  - **RED-1** (20:23:58Z, MAPPING block already added, tool absent): collection error `ImportError: cannot import name 'trace_numbers' from 'tools'`, exit 2.
  - **RED-2** (20:24:34Z, complete tool with `entry_status` stubbed to return `READ_MATCH`): 21 failed and 52 passed.
    - All 21 failures are entry-level witnesses. Every positive case and every structural refusal passed, so the positive tests alone cannot detect a check that accepts everything.
  - **GREEN** (20:24:48Z): 73 passed.
- **Review round 1 TDD:**
  - **RED** (20:52:35Z, new tests against the unchanged round-0 tool): 11 failed and 77 passed.
    - Nine unsupported numeric forms still returned `READ_MATCH`.
    - The permuted key raised `must name exactly the Key columns …`.
    - The unterminated quote reported `DID NOT RAISE ValueError`.
    - The two range and difference acceptance cases and the three refusals for a missing, repeated or repeated-and-extra key name already passed; they guard against regressions.
  - **GREEN** (20:53:31Z, final run 20:54:21Z): 88 passed, 0 failed, 0 skipped, no `xfail`.
  - The test that refused a reordered key was removed. A test that accepts a permuted key, on a fixture and on the real MAPPING (entry 2, key order reversed), replaced it.
  - **Replay of the Codex reproductions** (`review1_codex_replay.log`, 20:53:44Z, fixtures under the session scratchpad, ROW1 only):
    - `-17 and`, `1e17 and` and `−17 and` (U+2212) each give `LITERAL_OCCURRENCES_0`;
    - the unterminated quote gives `results/r.csv: CSV syntax error (unexpected end of data)`.
- **Corrections, each made at the shared root cause.**
  - **Numerals.**
    - A `FORM` tokenizer replaced `NUM` for scanning the LaTeX line. A literal counts only when it equals a whole token.
    - Each token absorbs the numeric syntax attached to it:
      - a sign `-`, `+` or `−` (U+2212), unless the dash directly follows a digit or another dash;
      - an `e`/`E` exponent;
      - a `^` superscript before or after;
      - a leading `.`;
      - digit groups with `{,}` or `,`.
    - Witnesses, all `LITERAL_OCCURRENCES_0`: `-17`, `−17`, `+17`, `1e17`, `17e3`, `10^{17}`, `x^{17}`, `.17`, `17,000`.
    - Acceptance witnesses, both `READ_MATCH`: `13--17` (range) and `20-17` (difference).
    - On `paper/sec3_theory.tex` l. 52 the `FORM` tokens equal the former `NUM` tokens, so the six correspondences are unchanged. `NUM` still validates the declared literal, and the decimal-literal refusal is unchanged.
  - **CSV.**
    - `csv.DictReader(..., strict=True)`. Inside `check`, `csv.Error` becomes `ValueError("<csv>: CSV syntax error (<reason>)")`, so `main` handles every refusal through one `except ValueError` and prints `trace-numbers: error: …` with exit 1.
    - A test pins both the `check` refusal and the exact CLI output.
    - The real E2 CSV parses under strict mode: 46 rows.
  - **Keys.**
    - `sorted(names) == sorted(Key columns)`, with a value in every pair. Permutations pass. A missing, repeated, or repeated-and-extra name is refused; the last case has the same name set but one more element.
    - W3 and the `background` and `dim` removals are still refused.
- **Real CLI.** `.venv/bin/python tools/trace_numbers.py` exits 0. It confirms both declared SHA-256 values. The summary line reads `6/6 entries READ_MATCH; verified subset 6 of 19 result-bearing occurrences, 13 of 19 not covered (docs/MAPPING.md, Coverage)`, followed by the caveat line. Every key also holds `arm=G1, background=gauss, dim=1, sr_annual=1.0`.

  | Literal | Reading | Key | Column | Cell | Rounded | Status |
  |---|---|---|---|---|---|---|
  | `17` | exact | cusum_x, γ 20 | `pred_delay` | `16.71475236584297` | 17 | `READ_MATCH` |
  | `142` | exact | cusum_x, γ 252 | `pred_delay` | `142.0388135314031` | 142 | `READ_MATCH` |
  | `1{,}510` | budget | onset, γ 20 | `first_order` | `1509.849065871212` | 1510 | `READ_MATCH` |
  | `2{,}787` | budget | onset, γ 252 | `first_order` | `2786.832260105758` | 2787 | `READ_MATCH` |
  | `1{,}066` | anytime-valid | cusum_t, γ 20 | `pred_delay` | `1066.2595750101377` | 1066 | `READ_MATCH` |
  | `2{,}322` | anytime-valid | cusum_t, γ 252 | `pred_delay` | `2321.684670063548` | 2322 | `READ_MATCH` |

- **Witnesses on the current MAPPING** (in memory; each alteration asserts a unique match first):
  - W1, entry 2 read from `mean_delay`: `MISMATCH`, as in the audit.
  - W1b, entry 1 read from `mean_delay`: `SOURCE_TEXT_MISMATCH`. The cell `16.7295` rounds to `17` like the literal, so this detection is new.
  - W2, literal `18`: `LITERAL_OCCURRENCES_0`.
  - W3, `mode` removed from all six keys: structural refusal, raised before any row is selected. Without `mode`, three rows still match (asserted); the audit recorded this case as `KEY_ROWS_3`.
  - `background` or `dim` removed: refused, although the reduced key still selects one row (asserted).
  - Also refused:
    - a stale LaTeX SHA and a stale CSV SHA;
    - entry 6 deleted;
    - `Entries` set to 7.
- **Fixture matrix.**
  - Per-entry statuses:
    - an altered cell gives `MISMATCH`; an altered TeX literal gives `LITERAL_OCCURRENCES_0`; a literal present twice gives `LITERAL_OCCURRENCES_2`;
    - `Rounded` set to `18` or `17.0` gives `MISMATCH`; an altered `Source text` gives `SOURCE_TEXT_MISMATCH`;
    - an absent column gives `UNKNOWN_COLUMN`;
    - a key that matches two rows or none gives `KEY_ROWS_2` or `KEY_ROWS_0`;
    - an empty or non-finite cell (`""`, `NA`, `nan`, `inf`, `-Infinity`, `1e40`) gives `EMPTY_OR_NON_FINITE`, and an empty cell is never read as 0.
  - Rounding: half-even ties `16.5` → 16 and `17.5` → 18. The text `16.500000000000001` rounds to 17, whereas a float would round it to 16.
  - The decimal literal `17.0` is refused.
  - Structural refusals:
    - 11 path refusals, each before any read;
    - 27 MAPPING structure refusals;
    - 4 malformed CSV cases and the unterminated quote;
    - stale fingerprints after a file change.
  - `main` prints no coverage line after a failure or a refusal.
- **Targeted controls** (`logs/stream_21_trace/review1_controls.log`, 20:54:21Z). Each of the following was checked by an assertion:
  - 88 `PASSED` lines and no `xfail` or `skip`;
  - pyflakes reports nothing on the two files;
  - `tests/test_pca_drift_contracts.py::test_e2_cells_crlf_disk_and_index_unchanged` passes (1 passed);
  - J1 on disk and in the index is `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, with 47 lines, 47 CRLF and no isolated LF;
  - no protected tracked path changed (`paper`, `results`, `experiments`, `jepadrift`, the contract, floors and check-prompts tests, `tools/check_prompts.py`, `Makefile`, `docs/DEVIATIONS.md`, `docs/audits`, `CLAUDE.md`, `prompts/streams`, the master prompts);
  - the GO, the plan and the review file are unchanged;
  - `git status` shows exactly the six expected lines;
  - no absolute personal path appears;
  - the only comments are three `# ponytail:` ceilings (a `tokenize` assertion);
  - no line exceeds 120 characters.
- **D8** remains FAIL at +5.2833 % and was not examined.

## Errors and Dead Ends

- **Three false acceptances found by Codex review round 1.**
  - **Numerals.** `NUM.findall` cut tokens at the first non-digit character and ignored the syntax attached to a number. The digits of `-17`, `1e17` and `−17` therefore counted as the literal `17`. Fixed at the tokenizer, the shared root cause; no LaTeX parser was added.
  - **CSV.** `csv.DictReader` in its default non-strict mode accepted an unterminated quote: the field became `'16.7\r\n'` and the mapped cell still read `16.71`. Fixed with `strict=True` and an explicit refusal.
  - **Keys.** Requiring the declared order was Claude's own stricter reading of "exactement". The GO prescribes no order, so the check is now a set equality without duplicates. The round-0 wrapup point "strict key order" is withdrawn.
- **Error type at RED-1.** The plan expected `ModuleNotFoundError`. Because `tools` is a namespace package, the import raised `ImportError`; the cause is the same, the absent module.
- **Two defects in Claude's own round-0 control commands**, corrected before the round-0 delivery:
  1. `grep -nE … -P` failed with "conflicting matchers specified", and the `!` negation turned that error into a false success. A `tokenize` assertion replaced it. That run is kept as `logs/stream_21_trace/controls_run1.log`.
  2. Lines of the form `! grep …; echo` could not fail, because `set -e` ignores negated commands. They were re-asserted with `test -z "$(grep …)"`. Round 1 uses only failing forms.
- **Line width.** In round 0, three lines exceeded the 120-character width of `tools/check_prompts.py`. They were rewrapped without any logic change.
- **Plan hypotheses replaced by the GO.**
  - H2, a unique key, became an exact Key-columns contract; round 1 made it order-free.
  - H10, `make check` run by Claude, was removed.
  - The decimal literal, a fail-closed `MISMATCH` in the plan, became an explicit structural refusal.

## Current State

- **Git.** Branch `stream-21-trace` at the base. Claude made no commit, push, staging or reindexation.
- **`git status --porcelain`** (exactly):
  - ` M docs/MAPPING.md`
  - `?? prompts/GO-stream-21-trace.md` (Codex)
  - `?? prompts/plans/plan-21-trace.md` (Codex)
  - `?? prompts/wrapups/wrapup-21-trace.md`
  - `?? tests/test_trace_numbers.py`
  - `?? tools/trace_numbers.py`
- **Ignored journals** in `logs/stream_21_trace/`, all kept:
  - round 0: `precheck`, `mapping_diff`, `red1`, `red2`, `green`, `green_final`, `cli`, `controls_run1`, `controls`, `final_controls`;
  - round 1: `review1_red`, `review1_green`, `review1_codex_replay`, `review1_green_final`, `review1_cli`, `review1_controls`, `review1_final_controls` (all `.log`);
  - the Codex review file `codex-review-round1.md`.
- **Interface.**
  - CLI: `python tools/trace_numbers.py`, without options. It exits 0 only when there is no refusal and every entry is `READ_MATCH`.
    - A refusal, a CSV syntax error included, prints `trace-numbers: error: …`.
    - A failed entry prints `trace-numbers: FAILED: k of n entries not READ_MATCH`.
  - Library: `check(root, mapping_text)` returns `(inputs, results)`. Helpers: `table`, `confined` (path guard) and `entry_status`. The regexes are `NUM`, which validates the declared literal, and `FORM`, which tokenizes the LaTeX line.
- **Not run by Claude, per the GO:** the full `make check`, the reindexation and Git. Codex owns the review, the pre-commit `make check` after reindexation, the commit and the push.
- **Environment.** Python 3.12.9 (`.venv/bin/python`, built on the Trading 3.12.9 binary), with pytest and pyflakes from `.venv`, and the GO exports `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. Nothing was installed.

## Vigilance Points

- **Meaning of `READ_MATCH`.** It attests only that the literal, the cell and the rounding agree, for the verified subset of 6 of 19 result-bearing occurrences.
  - It certifies no ARL0, FPR or ADD reading, no scientific conclusion and no reproduction by the producer.
  - **exact** names the ARL0-calibrated reading. The stored Φ(γI)/I values are diffusion approximations (`C-e1-readings`).
- **Tripwire.** Each of the following now fails `make check` until the entries are re-verified and `Check inputs` is updated:
  - any byte change in `paper/sec3_theory.tex` or `results/e2/e2_cells.csv`;
  - a deleted entry, an incomplete key or a changed count in MAPPING;
  - a CSV syntax error.
- **Rule for an attached sign.** A dash directly after a digit or another dash is read as a range or a difference: `13--17` and `20-17` count `17`, as two tests pin. A dash after a letter or a brace, as in `x-17`, is read as a sign and is refused (fail-closed).
- **Ceilings** (three `# ponytail:` comments):
  - only contiguous numeric forms are recognized: in `2\times10^{3}` the mantissa `2` still counts;
  - one CSV and one LaTeX file per MAPPING;
  - integer literals at 0 decimals only.
- **Two copies of each SHA-256.** Both values appear in the "Source of entries 1–6" bullets (historical prose, not read by the tool) and in `Check inputs`, the only source the tool checks. After a paper edit, update the block.
- **Thirteen occurrences not covered**, unchanged and not qualified by this lot: `1.8`; the five analytic test references; `5.2`, `1.39` and `1.15`; the ranges 13–16 and 8–11.
- **W3.** Its outcome changed from `KEY_ROWS_3`, as recorded in audit §3, to a structural incomplete-key refusal. The audit stays historical and was not modified.
- **Codex closure.**
  - Review round 1 is answered; a new review is pending.
  - Commit the GO and the plan with the lot.
  - After reindexation, run `make check` through the hook; the pre-commit `make check` exceeds the 5-minute target, a known debt.
  - Check the J1 hash, the 47 CRLF, and the absence of `data/raw/eurofidai/`, `data/derived/d4_eurofidai/` and files over 50 MB in the pushed range.

## Recommendations

- Review the `FORM` tokenizer: its sign rule, its exponent and superscript forms, and the two acceptance cases for ranges and differences. Review also the MAPPING usage paragraph and the 88 test cases.
- If a literal written in macro-separated scientific notation (`\times10^{…}`, `\cdot10^{…}`) must ever be mapped, extend `FORM` under a GO and add its witness.
- A second CSV or LaTeX source needs a format change under its own GO, such as a per-entry source column, rather than a second block.
- Mapping a decimal literal (for example `1.8`, once verified) needs a GO that quantizes at the literal's exponent.
- Pinning `5.2`, `1.39` and `1.15` in `tests/test_floors.py`, and sourcing the ranges of l. 111, stay separate GOs.
- The J4 freeze, `FROZEN.json`, the runner, the figure scripts, `appendix_b` and `dpi_lint` stay under their own GOs.
