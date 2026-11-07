# Wrapup — Lot 21-dpi: lexical DPI guard `tools/dpi_lint.py`

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md` (2026-11-06), prompt 21 task 5, on base `46c24923957ec505947016118def9453284bd1bc`, in the Codex worktree of branch `stream-21-dpi`. The lot is independent of lot 21-appendix, which provides no input and stayed inactive.
- **Problem.** The DPI wording rule ("no sentence may suggest a KL increase") was checked once, by the archived pattern scan of audit 21 §6. Its gapped pattern `creates?.*information` flags the correct sentence "An encoder creates no information" (`paper/sec3_theory.tex` l. 25), and nothing in `make check` reacted to new prose.
- **Gate.** Gate G-D of audit 21 §7 opened "if the theoretical prose grows"; that condition is not met. Codex opened a bounded G-D to replace the one-off scan by a reproducible guard. This revision is Codex's, not the researcher's.
- **Workflow.**
  - Claude wrote a native plan. Codex archived it as `logs/orchestration_20261106/native-plan-reviewed.md` (SHA-256 `a3ab3119e80cda29da3f2af3b176980edb9a4b54da6ec652fa0f93c08cf930d3`) and reviewed it in `logs/orchestration_20261106/codex-plan-review.md` (`e03d1eb622dc5132312a27f661f2fbd3812b35c6146484fb82cb4ad87c1df2bf`).
  - Codex then recorded `prompts/plans/plan-21-dpi.md` (`b05a1d04dc269211b8d56554fca4e56ecb17d4f86cb5b6c1b9e7fcc4fa0067e8`), whose "Décision GO intégrée" prevails over the native proposal, and `prompts/GO-stream-21-dpi.md` (`0ade7bfe65c6e1479e2273b7326607dd35261090bb153d27765590d45b944988`). First delivery: 2026-11-07, 00:03–00:19Z.
  - After its full check, Codex wrote the closeout review `logs/stream_21_dpi/codex-final-review.md` (`2ccd06516dc32cef70fe4cab802b34117799ea8d4d8e5e2655bc7720726b7264`). It is a GO for two bounded contract repairs, the H6 sentinel and the read-time `OSError` refusal, plus two editorial fixes, the caveat wording and the missing `main` docstring. It authorizes no lexical-rule expansion, no semantic certification and no change to the paper or the shared helper. Codex then granted the runtime slot; the corrections ran on 2026-11-07, 01:26–01:31Z.
  - The plan, the GO and both Codex reviews were read in full and hashed before the first write of each round and again in the controls. All are unchanged.
- **GO decisions.**
  - Q1: the current-corpus test requires zero FLAG; no waiver list. Native hypothesis H6, enforced by the closeout review: an added `paper/*.tex` file with no FLAG passes.
  - Q2: verb-before-object pattern, -ing and nominal forms included; no passive or reversed order.
  - Q3: reuse `confined` from `tools/trace_numbers.py` without copy or change; CLI `python -m tools.dpi_lint`.
  - Amendments: `not only`, `not merely`, `not just`, `no less` and `no doubt` must not suppress a FLAG; negation scope stops at `but`, `yet`, `however` and at an earlier candidate verb; a `%` starts a comment after an even number (zero included) of contiguous backslashes and is escaped after an odd number; witnesses before code; the output and the help state that zero FLAG does not establish semantic consistency with the DPI (wording set by the closeout review); no prose change.
- **Agent.** Claude Code, Opus 5.5 (`claude-opus-5-5`), one interactive session from the native plan to the corrections, effort max throughout, no subagent. Between the first wrap-up and the corrections, the harness compacted the conversation context automatically; there was no restart, purge or effort change. After the compaction, the closeout review, the plan, the GO, the tool, the test and this wrapup were re-read in full.

## Validated Results

- **Outputs (SHA-256):**
  - `tools/dpi_lint.py` (100 lines, standard library plus `tools.trace_numbers.confined`): `9e4fa393b8bbdf241e8f91302d59244c0bf2e65a6cd99b1d4c24ddbdcd1d834a`.
  - `tests/test_dpi_lint.py` (220 lines, 11 test functions, 69 cases): `e23750c8843c579722f26042ff806829fb3a297e9e4f30422729e0b05609815d`.
  - Ignored journals: real CLI output `logs/stream_21_dpi/cli_corrections.log` `38815705a44f5657c4860ac48446513fa0f3122ae2671b52f4c5bf2aabceb519`; `--help` output `cli_help_corrections.log` `9dab4fa036d84fcc3d113bf5855758a8e096923d7ce723257244a568e31db121`; correction diff with relative labels `corrections_diff.log` `7c1f6a2bd3473ae54c46c9dc94725c4fc0ccc828ca3b1bd1b30fe34c3c7351fa`.
  - Superseded first-delivery versions: tool `41b0b7abe9cbdf5ec15e075061661cd88b5e9886de277366c11bc8cc42f490dd`, test `7d3b862a2d0b27ba0012be355096dc72c4f9471e1dc3175483b7298fc35316ed`.
- **Contract as implemented.** The corrections leave the lexical rules unchanged; all regexes are `re.IGNORECASE` except `COMMENT`.
  - `COMMENT` `(?<!\\)((?:\\\\)*)%[^\n]*`: the even backslash run is kept, the rest of the line becomes spaces of the same length, newlines are kept, so lines and columns are those of the source.
  - `VERB` `(?<!non-)\b(?:increas(?:e|es|ed|ing)|creat(?:e|es|ed|ing|ion))\b`; `TAIL` `(?:[^\w.;:!?]+\w+){0,6}?[^\w.;:!?]+(?:KL|information|divergences?)\b`, matched at the verb end. Each verb is evaluated on its own.
  - NEGATED if the word right after the verb is `no` or `neither`, or if `no`, `not`, `never`, `cannot`, `nor`, `neither` or `without` stands among the 3 words before the verb with no comma, `. ; : ! ?`, `but`, `yet`, `however` or candidate verb between it and the verb. `no less`, `no doubt`, `not only`, `not merely` and `not just` never negate; the partner check skips non-word characters and LaTeX control words, so `not \emph{only}` is caught. Any other hit is a FLAG.
  - Refusals raise `ValueError`, printed as one `dpi-lint: error: …` line with exit 1. Causes: no `paper/*.tex`; any entry rejected by `confined`, checked for every path before the first content read; a file that cannot be read, reported as `paper/<name>: not readable (<exception type>)` with no absolute path; non-UTF-8 bytes; no text outside comments.
- **TDD, first delivery** (all runs `.venv/bin/python -m pytest -q tests/test_dpi_lint.py` with the GO exports):
  - RED-1 (00:13:10Z): `ImportError`, exit 2.
  - GREEN candidate: 66 passed.
  - RED-2, negation forced to `False`: 14 failed, 52 passed.
  - RED-3, negation forced to `True`: 35 failed, 31 passed.
  - RED-4, pre-GO native contract: 14 failed, 52 passed, exactly the GO witnesses.
  - GREEN (00:15:00Z): 66 passed, restoration asserted by hash.
- **TDD, corrections:**
  - **RED-H6** (01:26:47Z, unchanged tool `41b0b7ab…`): the current-corpus test was parametrized with two regression fixtures but kept its old assertion. Result: 2 failed, 66 passed. `[negated file first]` and `[negated file last]` both failed at the exact-hits assertion; the real-corpus case passed. This reproduces closeout finding 1 inside pytest.
  - **RED-2** (01:27:28Z, final tests, unchanged tool): 5 failed, 64 passed.
    - The `main` format test and the 3 current-corpus cases fail on the caveat line.
    - The `unreadable` refusal fails with an unhandled `PermissionError` from `read_bytes` (`tools/dpi_lint.py:67`, through `main`). Its message carries the absolute temporary path.
  - **GREEN** (01:28:15Z): 69 passed, 0 failed, 0 skipped, no `xfail`.
  - **Mutation check of the relaxed sentinel** (01:28:47Z, `relaxed_sentinel_stubs.log`). Each mutation was a temporary edit of the tool, restored from a copy and asserted by hash `9e4fa393…`.
    - Every hit forced to FLAG: 16 failed, 53 passed.
    - No hit at all: 48 failed, 21 passed.
    - Columns shifted by one: 7 failed, 62 passed.
    - Each mutation fails all three current-corpus cases.
- **Witness matrix (GREEN).**
  - 12 positives, one FLAG each: inflections, case, line break, noun forms, `\mathrm{KL}`, commas in the gap, `\%`, a comment between verb and object.
  - 9 contract negations, one NEGATED each, including the current sentence and a negator at the 3rd word before the verb.
  - 6 pseudo-negations, one FLAG each, including `not \emph{only}`.
  - Scope:
    - `does not create but increases information`: NEGATED for `create`, FLAG for `increases`.
    - `does not fail but/yet/however increases information`: FLAG.
    - `does not create and increases` and `never creates or increases`: NEGATED, then FLAG.
    - `neither creates nor increases`: two NEGATED.
  - Windows:
    - negator at the 4th word before the verb: FLAG;
    - `the encoder, not the data, creates information`: FLAG;
    - a 6-word gap: FLAG; a 7-word gap: no hit;
    - `. ; : ! ?` in the gap: no hit.
  - Comments with 0, 1, 2 and 3 backslashes before `%`: hit only for 1 and 3; length, newlines and the backslash run preserved; the offset of a later hit unchanged.
  - No hit: `The KL divergence grows with $N$`, `increases the Sharpe ratio`, `non-increasing information`, a comment line.
  - `main` on a 2-line hit: exact FLAG line `paper/a.tex:3:9: FLAG 'increases the KL': …`, summary, `FLAGGED`, caveat, exit 1.
  - Current corpus: three cases run through one assertion.
    - Case 1: the real corpus.
    - Case 2: a `tmp_path` copy of the real `paper/*.tex`, plus `aaa.tex` = `No encoder creates information.` (NEGATED, sorted before the sentinel) and a neutral `zzz.tex`.
    - Case 3: the same copy, with a neutral `aaa.tex` and the NEGATED sentence in `zzz.tex`.
    - The assertion requires exit 0 and both sources listed.
    - Among the hits it requires the sentinel `(paper/sec3_theory.tex, 25, 12, 'creates no information', NEGATED)` and, for cases 2 and 3, the hand-derived extra hit `(paper/aaa.tex or paper/zzz.tex, 1, 12, 'creates information', NEGATED)`. Every hit must be NEGATED.
    - On the output it requires each expected NEGATED line at any position, the summary `hits n: FLAG 0, NEGATED n`, the caveat last and no `FLAGGED`. Source bytes must be unchanged.
  - Mutated copies (`creates information`, `creates new information`, `creates no less information`) give a FLAG at `paper/sec3_theory.tex:25:12`.
  - 10 refusals, each a single `dpi-lint: error: …` line with exit 1.
    - No `paper/`; a `.bib` only.
    - The other 8 sit next to an `a.tex` that holds a FLAG sentence, so the exact output also shows that no partial hit or summary is printed. They are: a link outside the root; a link to `data/raw/eurofidai/x.tex` (target never printed); a broken link; a directory `x.tex`; an empty file; a comment-only file; non-UTF-8 bytes; a mode-000 file (`paper/x.tex: not readable (PermissionError)`).
  - `dpi_lint.confined is trace_numbers.confined`; imports are standard library plus `tools`.
- **Real CLI.** `.venv/bin/python -m tools.dpi_lint` exits 0 and prints exactly:

  ```text
  paper/sec3_theory.tex:25:12: NEGATED 'creates no information'
  dpi-lint: files 2 (paper/appA_proofs.tex, paper/sec3_theory.tex); hits 1: FLAG 0, NEGATED 1
  dpi-lint: pattern lint only: zero FLAG does not establish semantic consistency with the DPI, and a FLAG requests review without judging the sentence
  ```

- **Targeted controls** (`logs/stream_21_dpi/controls_corrections.log`, 01:29:41Z, each an assertion under `set -euo pipefail`):
  - Tests and lint: 158 passed (the 69 dpi cases, the 88 trace cases and `test_e2_cells_crlf_disk_and_index_unchanged`); pyflakes reports nothing on the two files.
  - CLI and help:
    - the real CLI output equals the 3 lines above (`diff`);
    - `--help` carries the new caveat wording and the unreadable-file refusal;
    - the earlier caveat wording is absent from the tool, the test, the help and the CLI output.
  - Code hygiene:
    - `blank`, `find`, `scan` and `main` have one-line docstrings;
    - the only comments are the two `# ponytail:` ceilings (a `tokenize` assertion);
    - no line over 120 characters and no absolute path in the tool or the test.
  - Hashes:
    - plan, GO, both Codex reviews, `tools/trace_numbers.py` `e6a43a2d19456427814b6d332176d644f715459a85342cd462bef9e8f7b29548`, `paper/sec3_theory.tex` `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` and `paper/appA_proofs.tex` `4a5469c84f12bb5902fee9f68a783b64c45b77b11f1172c5bf4b81f7603c2a30` are unchanged;
    - J1 on disk and in the index is `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 lines, 47 CRLF.
  - Git, read only:
    - `git diff --quiet HEAD` on `paper`, `results`, `docs`, `configs`, the trace tool and its test, `Makefile` and `CLAUDE.md`;
    - HEAD equals the base; `git status --porcelain` is exactly the 5 lines under Current State.
  - The wrapup checks ran after this file was written (`final_controls_corrections.log`).
- **D8** remains FAIL at +5.2833 % and was not examined.

## Errors and Dead Ends

- **H6 sentinel (closeout finding 1).**
  - What went wrong: the first delivery read GO item 5 ("exactly one NEGATED occurrence on the current corpus") as a pin of the whole hits list, the first output line and the count. The native H6, which the GO kept, says an added `.tex` file with no FLAG passes.
  - Codex's reproduction: with an added `aaa.tex` holding `No encoder creates information.`, the CLI exits 0 but the current-corpus test failed.
  - Fix: in the test only; the tool was already right.
- **Read-time OSError (closeout finding 2).**
  - What went wrong: `confined` checks the path shape and the regular-file status, not read permission. A mode-000 file passed confinement. Then `read_bytes` raised `PermissionError`, which escaped `scan` and `main` as a traceback carrying an absolute path.
  - Fix: at the single read site in `scan`.
- **Caveat wording.** The first wording could be read as a negative finding about consistency. It was replaced by "does not establish semantic consistency with the DPI" in the tool, the help, the test and this wrapup.
- **Control-script glitch.** The first RED-H6 check expected ` - assert` after each `FAILED` node id, but pytest printed bare ids for these failures. The check was rerun on the saved journal with exact-line matches; pytest was not rerun.
- **Rejected options in the corrections.**
  - Monkeypatching `Path.read_bytes` for the OSError witness: a mock would not exercise the real permission failure, and the review asked for a temporary-fixture witness.
  - Tests on the help text or the docstrings: these are prose for human readers, so the controls check them instead.
  - An exact hit count for the real corpus inside the test: it would contradict H6. The exact count stays in the targeted CLI control.
- **First delivery.**
  - A 121-character docstring line was rewrapped before the stub runs.
  - The first residual probe failed with a shell-quoting `SyntaxError` and was rewritten; the repository was not affected.
  - Rejected: one pseudo-partner list shared by all negators (stricter than the GO lists); skipping LaTeX control words after the verb (it would turn `creates \emph{no} information` into NEGATED).
  - Sequence notes:
    - the GREEN candidate ran before RED-2 to RED-4;
    - RED-4 was added to show that the GO witnesses discriminate;
    - the plan's verification block ran before the wrapup existed, so its `git status` check used four lines, and the five-line check followed in `final_controls.log`.

## Current State

- **Git.** Branch `stream-21-dpi` at the base `46c24923957ec505947016118def9453284bd1bc`. Claude made no commit, push, staging, branch or base change, or reindexation. Only read-only Git commands ran: `rev-parse`, `status`, `diff --quiet` and `show :path`.
- **`git status --porcelain`** (exactly):
  - `?? prompts/GO-stream-21-dpi.md` (Codex)
  - `?? prompts/plans/plan-21-dpi.md` (Codex)
  - `?? prompts/wrapups/wrapup-21-dpi.md`
  - `?? tests/test_dpi_lint.py`
  - `?? tools/dpi_lint.py`
- **Ignored journals** in `logs/stream_21_dpi/`:
  - first delivery: `precheck`, `red1`, `green_candidate`, `green_candidate_sha`, `red2`, `red3`, `red4_native_contract`, `green`, `controls`, `cli`, `cli_help`, `residual_probe`, `final_controls` (all `.log`); they keep the earlier caveat wording;
  - corrections: `precheck_corrections`, `red_h6`, `red_corrections`, `green_corrections`, `relaxed_sentinel_stubs`, `controls_corrections`, `cli_corrections`, `cli_help_corrections`, `corrections_diff`, `final_controls_corrections` (all `.log`);
  - Codex's `codex-final-review.md`, read only.
- **Interface.**
  - CLI: `python -m tools.dpi_lint` from the repository root, no option (`--help` prints the usage docstring). `python tools/dpi_lint.py` does not run, because the tool imports `tools.trace_numbers`.
  - Exit 0 only without refusal and without FLAG. A refusal prints `dpi-lint: error: …` alone; FLAGs add `dpi-lint: FLAGGED: k of n hits to review` after the summary.
  - Library: `blank(text)`; `find(text) -> [(offset, words, negated)]`; `scan(root) -> (files, hits)` with hits `(file, line, column, words, negated)`; `main(argv) -> int`, which now has a one-line docstring.
  - `scan` lists `root/paper/*.tex` (not recursive) and confines every entry before the first read. At the read, it turns `UnicodeDecodeError` and `OSError` into a `ValueError` that names the relative path.
- **Not run by Claude, per the GO:** the full `make check`, the reindexation and Git mutations. Codex owns the review, the pre-commit `make check` after reindexation, the commit and the push.
- **Environment.**
  - Python 3.12.9 (`.venv/bin/python`, built on the Trading 3.12.9 binary); pytest and pyflakes from `.venv`.
  - Exports: `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`.
  - The mutation runs wrote bytecode to a cache prefix outside the repository. Nothing was installed. The tests ran as uid 1004.

## Vigilance Points

- **Meaning.** Zero FLAG does not establish semantic consistency with the DPI. A FLAG is a review request, not a verdict on the sentence. NEGATED means a negation of the contract was recognized, not that the sentence is valid.
- **Sentinel.** The current-corpus test fails `make check` until review on any FLAG, a missing sentinel or a moved sentinel.
  - It requires the NEGATED sentinel at `paper/sec3_theory.tex:25:12`, zero FLAG, both sources listed and unchanged bytes.
  - Extra correctly NEGATED hits and neutral files pass, in any alphabetical position (H6).
  - The exact count of the unchanged corpus (1 NEGATED, 0 FLAG) is pinned by the targeted CLI control only, not by `make check`.
- **Unreadable witness.** It relies on POSIX permissions. Under root, with `CAP_DAC_OVERRIDE`, or on a filesystem that ignores mode bits, the mode-000 file stays readable. The case then fails loudly, printing FLAG lines instead of the error line; it cannot pass silently.
- **Residual false NEGATED.** Found after the first GREEN; not claimed as accepted limits. The closeout review keeps them documented, not extended (`logs/stream_21_dpi/residual_probe.log`). Each is read as NEGATED:
  - hedges: `does not necessarily increase the KL`, `does not always increase the KL`;
  - other focus or litotes partners: `not simply increases`, `without doubt increases`, `No other encoder increases`;
  - double negation and infinitive litotes: `not without creating information`, `does not fail to create information`;
  - sentence adverbials without a comma: `Not surprisingly it increases`, `No wonder it increases`;
  - a negated non-candidate verb joined by `and`: `does not lose and increases information`.
- **Review-direction false FLAG:**
  - `creates \emph{no} information`;
  - `never creates or increases information`: the second verb is flagged by the GO scope rule;
  - a comma inside the negation (`does not, in general, increase`);
  - `none`;
  - contractions.

  `does not create nor increase information` gives two NEGATED, which is correct because `nor` directly precedes the second verb.
- **Not seen** (declared limits):
  - passive and reversed order (`Information is created`, `The KL increases`);
  - paraphrases (`adds information`);
  - punctuation inside the gap (`by 0.5 nats`);
  - gaps over 6 words;
  - prefixed verbs (`recreates`);
  - files outside `paper/*.tex` (`.bib`, subdirectories, `.TEX`).
- **Ceilings** (two `# ponytail:` comments): verb-before-object patterns only; no waiver list.
- **Codex closure.**
  - Commit the GO, the plan, the tool, the test and this wrapup together.
  - Run `make check` through the hook after reindexation. The pre-commit `make check` exceeds the 5-minute target, a known debt.
  - Check the J1 hash and its 47 CRLF.
  - In the pushed range, check that no path is under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` and that no file exceeds 50 MB.

## Recommendations

- Decide on the residual false NEGATED forms. Each candidate is a closed-list addition with one witness, and each moves toward FLAG:
  - partners `simply`, `solely`, `necessarily` and `always` after `not`;
  - `doubt` after `without`;
  - `other` and `wonder` after `no`;
  - `surprisingly` after `not`;
  - stops `and`, `or` and `to`;
  - `without` refused right after `not`.
- If the exact count of the unchanged corpus must be enforced by `make check`, that needs a GO amending H6. Today only the targeted CLI control enforces it.
- Add a waiver list only when a reviewed FLAG has to stay, under its own GO.
- A passive or reversed-order pattern needs its own GO. It will flag legitimate growth statements (`the KL increases with N`).
- Extend the corpus under a GO if `paper/` gains subdirectories or `\input` files.
- The J4 freeze, `FROZEN.json`, the runner, the figure scripts and `appendix_b` stay under their own GOs.
