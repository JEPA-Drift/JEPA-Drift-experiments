2026-10-29

# Wrapup — stream 13: E3 calibration under H0, D8 overshoot gate FAIL archived

## Context

- **Prompt, plan and decisions.**
  - Prompt: `prompts/streams/prompt-13-e3.md`; bootstrap: `prompts/amorcage-13.md`.
  - Worktree `~/JEPA-stream-13`, branch `stream-13`, base `c284823` (stream 27 merged).
  - Plan: `prompts/plans/plan-13.md`, revision 4, with « Décision GO intégrée » of 2026-10-28 and the archive section
    of 2026-10-29.
  - GO: `prompts/GO-stream-13.md`, verbatim transcripts (revision 3 superseded, revision 4 in force).
  - Stop: `prompts/STOP-stream-13-D8.md` (2026-10-28), the stop before commit required by R4.3 item 7 after the D8
    FAIL; committed unchanged.
  - Archive GO: `prompts/GO-stream-13-archive.md` (2026-10-29). The researcher authorized, by a French directive,
    archiving the negative D8 result in one local commit with only the stop-before-commit clause lifted. The English
    text quoted verbatim there is the Codex orchestrator's operational prompt derived from that directive, not
    verbatim researcher text (label corrected before integration, Errors and Dead Ends 5).
- **Sessions.**
  - 2026-10-23 to 2026-10-28: plan revisions 1 to 4, TDD implementation, quick runs, the single full run (2026-10-28,
    about 19:11 to 19:32 UTC) and the stop.
  - 2026-10-29, archive: no experiment script, quick run, new draw or rerun. Artifacts verified, decision documents
    written, targeted tests, `make prompts-check` and `make check` run.
- **Environment.**
  - `.venv` only: Python 3.12.9, numpy 2.4.4, scipy 1.17.1, pandas 3.0.6; Trading never activated.
  - `make` comes from `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`.
  - Python calls pin OMP/MKL/OPENBLAS threads to 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and
    `MPLBACKEND=Agg`.
  - MCP checks before the first write of 2026-10-29: graphify `graph_stats` (3,506 nodes, 4,218 edges) and jcodemunch
    `menu` (91 actions). No Graphify LLM extraction; jCodeMunch `use_ai_summaries` stays false.

## Validated Results

1. **Deliverables.**
   - `experiments/e3_calibration.py` (1,160 lines), `configs/e3.yaml`, `tests/test_e3.py` (30 test functions).
   - `jepadrift/stats/intervals.py`: `wilson` moved verbatim from `experiments/e10_robustness.py`, which imports it
     (Q-A).
   - Deviations in `docs/DEVIATIONS.md` (English): `C-e3-design`, `C-e3-readings`, `C-e3-arl0`, `C-e3-overshoot`,
     `C-e3-encoders`, `C-e3-sizes` and `C-e3-d8-fail`.
2. **Full run** (single, 2026-10-28): `python experiments/e3_calibration.py --jobs 24 --out results/e3`, base commit
   `c284823`, 3,041 tasks, 1,265 s wall.
   - Config: `configs/e3.yaml` 6e3857382200f0b7333419a1be33ea1623fe59b99e3e236abf6d97c615948b0b.
   - Inputs: `data/derived/d2_us97/ret_wide.npy` 333d2b07…, `data/derived/d3_239/ret_wide.npy` a266fbab…. Raw bases
     85147fd9… (K = 5) and 6c44d64a… (K = 10), the audit and E10 values.
   - Strict window: 3,774 rows per panel, 2005-01-04..2019-12-31. D3 2005-01-03 is excluded and counted (1 row); D2
     excludes none.
   - Five tickers, literal in the tests: d2_us97 [24, 71, 56, 46, 75] = COST, SHW, SO, MDLZ, PSA; d3_239
     [60, 177, 141, 116, 184] = CASY, KEY, GPC, ERIE, LRCX.
   - Lattice targets: H = 750, threshold 9.1, exact level 0.0439467; H = 2,000, threshold 10.3, exact level 0.0456695.
3. **Outputs** (SHA-256). The six tables match `logs/e3/run.log` (`sha256sum -c`, 2026-10-29).
   - `results/e3/e3_cells.csv` (192 rows) c37a6652b299223d8abdec20bf6d93adbcaf74e58bfcc5c87fec22060b726657
   - `results/e3/e3_arl0.csv` (102 rows) e5095a796457f56de0fad55fb486bfe16a277c7a2eded681f1cbdcc6f3ddd2e1
   - `results/e3/e3_raw_placebo.csv` (130 rows) c3ab3c6d07dd49b125bbea68b9caa6f7ce79a0ecd6fdee5e28d048b36344bc69
   - `results/e3/e3_overshoot.csv` (12 rows) 1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3
   - `results/e3/e3_window_encoders.csv` (16 rows) 1b7a541db2ace99c81eedf2afaef8a3724d39679f69f750faa0bc7302f78ed92
   - `results/e3/e3_j2_check.txt` e1cf0992f8b2cf3066cf3ee6822cd9fd8ceae307d986e964e2736c93559bd63e
   - `figures/e3/arl0.png` b8b005848a3f3604c136bfaca2aa337effea4959c197e112bc4d5eb5e238f989
   - `figures/e3/arl0.pdf` 7f453346e9478f82d476dea25b2dc4eecdfe5b7991dc060816ad45b092cc7b2f
   - `figures/e3/fpr_cells.png` 07f15a7ed0f076d589b0f8ed0998b3accf8e2c66b3411d0a6876d37bf23efcb2
   - `figures/e3/fpr_cells.pdf` 7f4e6f7db440cad969764e7507e9cfaba07d612253a6839b0e7750cfda48bab4
   - `figures/e3/gamma.png` cd21643588704d83c581ecf364c873486df63f97be079a80b1ab0d5d77387a41
   - `figures/e3/gamma.pdf` 6ce764b8d6642775908c297cb9bad08ee1be9bfd583cc6ed1d021f9ea90dd565
   - `figures/e3/raw_placebo.png` 01c5d7e490d6c1ae9a8b1d8dfd33c6d0f0f67efe6fd065cfa7962a0f822ffb14
   - `figures/e3/raw_placebo.pdf` fc27b8fb66698b22bd2df8d3874fbfd44f151a4bcd4f043e739191aa3663fd39
   - `logs/e3/run.log` (not committed) f783c48153a4df9629cebf20dc9d592cb0226dd6c2005187577ace542c27c24d
   - Code as committed: `experiments/e3_calibration.py` 9c1e89ed…, `tests/test_e3.py` 160aa381…,
     `jepadrift/stats/intervals.py` c4f848d4…, `experiments/e10_robustness.py` de0c8f07….
4. **D8 primary overshoot gate: FAIL.** Replicates 0..1,999, |ARL0_MC/ref - 1| <= 0.05 for every cell, no censored
   path; one full run, no rerun.

   | background | statistic | ARL0_MC | SE | reference | relative gap | gate | Brook-Evans or lattice |
   |---|---|---|---|---|---|---|---|
   | iid | first_order_d0.5_l6 | 2,554.816 | 54.82 | 2,587 | -0.0124 | PASS | 2,553.11 |
   | iid | first_order_d1_l3 | 1,994.0665 | 43.59 | 1,894 | +0.0528 | **FAIL** | 1,962.79 |
   | iid | sign_d0.1_u16 | 220.4405 | 4.70 | 213 | +0.0349 | PASS | 213.09 |
   | garch | first_order_d0.5_l6 | 856.3675 | 20.25 | 889 | -0.0367 | PASS | — |
   | garch | first_order_d1_l3 | 643.4255 | 14.81 | 669 | -0.0382 | PASS | — |
   | garch | sign_d0.1_u16 | 208.9985 | 4.45 | 214 | -0.0234 | PASS | 213.09 |

   - The failing relative gap is +0.0528334213. The 20,000-path diagnostic (1,964.2627, SE 13.93) and the Brook-Evans
     value 1,962.7935 are descriptive only; attribution and its limits are in `C-e3-d8-fail`.
   - GARCH diagnostics, descriptive: Gamma^spec of x 0.994; lambda_req at the exact i.i.d. ARL0 8.706 and 4.588 on
     the primary paths, hence Gamma^op 1.451 (delta = 0.5, lambda = 6) and 1.529 (delta = 1, lambda = 3).
5. **ARL0 of the e-detectors (D9).** 66 rows PASS (lb99 >= gamma), 36 raw rows descriptive, none INDETERMINATE. The
   bounded stopping-time check has its per-row 99 % bound above 0 in none of the 66 rows, and certifies no violation
   at family-wise 1 % (Bonferroni, z = 3.613).
6. **Secondary calibration check** (`e3_j2_check.txt`, no J2 verdict; the primary J2 (i) verdict is E1's at 2,000
   replicates). 54 of 54 cells lie within 0.01 of their exact level. One of 54 lies outside its 99 % region: a
   descriptive count over cells that share draws, with expectation 0.546 under exactness by linearity. The union bound
   on at least one cell beyond 0.01 under exactness is 1.1e-09.
7. **Verification of 2026-10-29.**
   - `sha256sum -c`: the six full outputs against `logs/e3/run.log`, the six quick outputs against
     `logs/e3_quick/run.log`, `configs/e3.yaml` and both `ret_wide.npy` inputs against the full-run log: all OK.
   - D8 values asserted from `results/e3/e3_overshoot.csv` read with `float_precision="round_trip"`: one FAIL, five
     PASS, no censored primary or diagnostic path. `e3_arl0.csv` has no FAIL class and no certified violation.
   - `.venv/bin/pytest -q tests/test_e3.py tests/test_e10.py`: 45 passed in 44.1 s.
   - `make prompts-check`: 29/29.
   - `make check`, run after the wrapup and the reindex, in 3 min 42 s: pyflakes clean; 22 passed and 4 skipped
     (contracts and decoupling); 273 passed and 4 skipped (rest). `git status` was unchanged afterwards.
   - Provenance-label correction (amend of 33f5096): `git diff --check` clean. Against 33f5096 only
     `prompts/GO-stream-13-archive.md`, `prompts/plans/plan-13.md` and this wrapup differ; the English quote and the
     decision and application sections of the GO file are byte-identical (`cmp`). `make prompts-check` 29/29;
     `make check` in 3 min 44 s: pyflakes clean, 22 passed and 4 skipped, 273 passed and 4 skipped.

## Errors and Dead Ends

1. **D8 FAIL and stop.** The single full run failed D8 on `iid/first_order_d1_l3`. The instance stopped before the
   commit (R4.3 item 7), wrote `prompts/STOP-stream-13-D8.md` and left the worktree intact. The archive GO of
   2026-10-29 lifted only the stop-before-commit clause; nothing was rerun or retuned.
2. **Bounded stopping-time rule.** In the first `--quick` run, one coin row of 33 SR rows had a per-row 99 % lower
   bound of mean(M_sigma - sigma) above 0 (z = 3.04), a 1 % event per row under the exact SR equality. The rule became
   a family-wise Bonferroni bound before the full run (`C-e3-arl0`); no FPR, ARL0 or overshoot reading depends on it.
3. **Partial-code audit (R4.2, 2026-10-28).** `load_rows` masked D3 2005-01-03 silently before the window check;
   `e3_overshoot` and `e3_window_encoders` had no `deff` or `n_eff`; P1-D D5 calibrated and evaluated on the same
   paths; `j2_lines` wrote its own J2 verdict. The R4.3 corrections and their tests preceded the full run, whose log
   counts the exclusion and whose outputs carry `deff`, `n_cal`/`n_eval` and no verdict line.
4. **jCodeMunch reindex failed.** `tools/reindex_graphify_jcodemunch.sh` ran `graphify update .` (AST only, 182
   files: 3,751 nodes, 4,626 edges, 294 communities), then stopped at `jcodemunch-mcp index` with exit 1: "Both local
   and git identity indexes already match this path. Invalidate one of them before indexing or resolving this path."
   No index was invalidated: the git identity index may be shared with the other worktrees, and the archive GO allows
   only safe calls. The jCodeMunch index of this worktree is therefore not refreshed; `git status` was unchanged by the
   script.
5. **Provenance label of the archive GO.** Commit 33f5096 called the English prompt quoted in
   `prompts/GO-stream-13-archive.md` the researcher's verbatim GO. A review found that the Codex orchestrator wrote it
   from the researcher's French directive of 2026-10-29. Only the introductory attribution and the heading of that GO
   file and the attribution sentence of the plan's archive section were corrected. The quote, the decision, the STOP
   trace, the E3 code, configuration, tests, results and figures, the primary FAIL and the tolerances are unchanged,
   and the archive commit was amended with the same message.

## Current State

- Branch `stream-13` = `c284823` plus one local commit,
  `feat(e3): archive H0 calibration with failed D8 gate (stream 13)`. Not fetched, pushed or merged; `main` untouched.
- Committed:
  - code and config: `experiments/e3_calibration.py`, `configs/e3.yaml`, `tests/test_e3.py`,
    `jepadrift/stats/intervals.py`, `experiments/e10_robustness.py`;
  - outputs: `results/e3/` (six files), `figures/e3/{arl0,fpr_cells,gamma,raw_placebo}.{png,pdf}`;
  - documents: `docs/DEVIATIONS.md`, `prompts/plans/plan-13.md`, `prompts/GO-stream-13.md`,
    `prompts/GO-stream-13-archive.md`, `prompts/STOP-stream-13-D8.md`, `prompts/wrapups/wrapup-13.md`.
- Not committed, kept on disk:
  - `logs/e3/run.log`, ignored and excluded by the archive GO (SHA-256 above);
  - quick run of 2026-10-28 09:53 UTC (`--quick --jobs 8`): `results/e3_quick/`, `figures/e3_quick/`,
    `logs/e3_quick/run.log`. Its six tables match its log: e3_cells 6d05781e…, e3_arl0 418ffa34…, e3_raw_placebo
    c3ab3c6d…, e3_overshoot bb90d3f5…, e3_window_encoders 109eac37…, e3_j2_check 4de1499d….
- Expected `git status --porcelain` after the commit: exactly `?? figures/e3_quick/` and `?? results/e3_quick/`.

## Vigilance Points

- **D8 is a FAIL.** The overshoot table is not a reproduction of the plan v1 references. The attribution to the Monte
  Carlo error of the reference is a hypothesis, and the absence of a defect in the overshoot simulation is not
  established (`C-e3-d8-fail`).
- **Run provenance.** `logs/e3/run.log` records the base commit `c284823` and the config hash, not a hash of the then
  uncommitted script. The script and tests were last modified at 17:23 UTC, before the run start (19:32:36 UTC minus
  1,265 s): the link between the committed code and the archived outputs rests on file times.
- **Run log.** Unlike `logs/e10/run.log`, the E3 log is not committed; the committed tables carry every reported
  number, and the log hash is recorded above.
- **Quick outputs** predate the last modification of the script (09:53 against 17:23 UTC) and are not committed.
- **J2.** `e3_j2_check.txt` is a secondary check; the primary J2 (i) verdict is E1's (stream 12).
- **Shared draws (D10).** Counts over cells stay descriptive; joint probabilities only by the union bound.
- **Mixture cell (D7)** is deferred until the Holm gate of stream 12 is on `main`.

## Recommendations

- A new overshoot gate (for instance against the Brook-Evans values, with a Monte Carlo tolerance and new
  pre-registered seeds) needs a new plan revision and GO; it cannot re-grade this run.
- Add a reduced-size test comparing a Monte Carlo ARL0 of the overshoot simulator with its Brook-Evans value; it
  would address the insufficient-evidence point of `C-e3-d8-fail`.
- Write the SHA-256 of the experiment script to the run log, or run from a committed tree.
- Researcher decisions left open: force-adding `logs/e3/run.log` (precedent `logs/e10/run.log`) and deleting the quick
  outputs (plan section 11).
- Choose which jCodeMunch index of `~/JEPA-stream-13` (local or git identity) to invalidate, then rerun
  `tools/reindex_graphify_jcodemunch.sh`.
- Integration into `main` (fetch, rebase, `git push origin stream-13:main` after the pushed-range check) only on a
  separate instruction.
