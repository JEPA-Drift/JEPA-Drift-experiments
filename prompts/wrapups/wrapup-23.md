2026-10-23

# Wrapup — stream 23: E6 phase 1, second-order F4 drifts monitored by P1-D and P3-D

## Context

- Prompt: `prompts/streams/prompt-23-e6.md`, as corrected at `2b0b1cd`. Bootstrap prompt: `prompts/amorcage-23.md`.
  Worktree `~/JEPA-stream-23`, branch `stream-23`, base `2b0b1cd` (local `main`, stream 8b merged).
- Plan: `prompts/plans/plan-23.md`, revision 2 with « Décision GO intégrée ». GO: `prompts/GO-stream-23.md`, a verbatim
  transcript of the two exploration corrections, the review that suspended the first GO, and the GO.
- Audit correction of `7e4c7a1` (2026-10-23): GO `prompts/GO-stream-23-audit.md`, a verbatim transcript of the two
  audit messages, the bootstrap prompt, the resumptions, the plan review and the final GO. The plan stays local
  (`~/.claude/plans/amor-age-stream-proud-plum.md`, revision 2), uncommitted at the orchestrator's request. Bootstrap
  prompt: `prompts/amorcage-23.md` as committed on `main` at `c10b68a`, outside this branch.
- Decisions: Q1 to Q5 at their defaults.
  - Q1: D6 drift cells kept, descriptive, `IC=NA`.
  - Q2: no recentring of P3-D.
  - Q3: K = 1 as the D5 sensitivity.
  - Q4: the exploratory rotation pairs stay.
  - Q5: D6 `IC=NA` below 10 blocks of length H, the conservative prespecified reporting criterion of the protocol
    (not a general requirement of a block bootstrap or a deff).
- Scope: phase 1 only (P1-D, P3-D factor and full). P4-D waits for stream 17; P5-D and the J4 contribution (phase 2)
  wait for stream 16.
- Environment:
  - every command runs through `.venv` (`.venv/bin/python`, `.venv/bin/pytest`); Trading is never activated;
  - `make` is `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin/make` (GNU Make 4.4.1), first on PATH;
  - direct Python calls pin OMP/MKL/OPENBLAS threads to 1, with `MKL_CBWR=COMPATIBLE` and `PYTHONHASHSEED=42`.

## Validated Results

1. **Deliverables.**
   - `experiments/e6_second_order.py` (611 lines; `--phase {1,2}`, phase 2 refused before stream 16).
   - `configs/e6.yaml`.
   - `tests/test_e6.py`: 13 tests, 8 s.
   - `results/e6/e6_cells_phase1.csv`: 190 rows × 50 columns, 78 D6 and 112 D5.
   - `figures/e6/e6_phase1_{delays,gadd}.{png,pdf}`, drawn from the CSV only.
   - `logs/e6/phase1.log`, local and ignored, never staged.
   - No change to `jepadrift/`, `PIPELINES`, `.gitignore` or `Makefile`. P1-D uses `streams.energy_stream` and
     `cusum.strict_cusum_vec`; P3-D detection goes through `pipelines.run_pipeline` with states fitted on drift-free
     rows.
2. **Determinism.**
   - The full run twice gives the same CSV SHA-256, `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249`
     (`cmp`); the logs are identical apart from the durations.
   - The quick run gives the same CSV, `874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2`, with
     `--jobs` 1 and 48 (the default).
   - The full run takes 41 s on 48 cores; the quick run 30 s (62 s with `--jobs 1`).
3. **D6** (calib rows of `d3_239`: 941 days, rows [2834, 3775), 2016-04-07 → 2019-12-31). One sign per day leaves the
   energies unchanged bit for bit, so there is no pseudo-sample. Each window start is an equivalent counterfactual
   onset: F4 is injected once from the first calib day with the matrix fitted on the clean calib rows, the same for
   every onset; F4 and the streams act day by day, and the CUSUM restarts from 0 at each window start. Thresholds are
   taken on all 692 (H = 250) or 442 (H = 500) windows:

   | monitor | λ (H = 250 = H = 500) | λ_iid 250 / 500 | Γ_z^op 250 / 500 | Γ^spec | in-sample FPR | next attainable level 250 / 500 |
   |---|---|---|---|---|---|---|
   | P1-D, Article B (σ̂/(√2μ̂) = 1.759) | 36.0904 | 11.895 / 13.144 | 3.034 / 2.746 | 2.117 | 0 | 0.2775 / 0.5656 |
   | P3-D factor (K = 10) | 172.494 | 8.296 / 9.299 | 20.79 / 18.55 | 1.676 | 0 | 0.2428 / 0.5249 |
   | P3-D full (D = 238) | 182.869 | 6.902 / 7.672 | 26.50 / 23.83 | 3.399 | 0 | 0.2370 / 0.5023 |

   - Under drift, detection on D6 is membership of the tie block of the dominant episode. P1-D detects in 6 of 12
     cells at exactly the next level (0.277 and 0.566), always on 2019-01-04. P3-D's modal alarm dates run from
     2018-12-24 to 2019-02-07, with 75–100 % of alarms within 7 days of them.
   - PC2–PC3 is never detected.
   - D6 G_ADD ranges from 0.86 to 1.17, all `undetermined`; CI = NA under the conservative prespecified reporting
     criterion (2.77 and 0.88 blocks of length H, fewer than 10).
4. **D5 control** (fit panel `SeedSequence([23, 0, 0])`, 941 days; 2000 calibration panels in role 1 and 2000 test
   panels in role 2, 500 days each; Γ_z^op = λ_D5/λ_iid):

   | monitor | λ_D5 250 / 500 | Γ_z^op 250 / 500 | q null mean (H = 250) | FPR 250 [Wilson] | FPR 500 [Wilson] | D6 rule on the fit panel: λ_in, test FPR 250 / 500 |
   |---|---|---|---|---|---|---|
   | P1-D | 26.570 / 39.465 | 2.234 / 3.002 | −0.072 | 0.0480 [0.0395, 0.0583] | 0.0535 [0.0445, 0.0642] | 30.21: 0.0400 / 0.0795 |
   | P3-D factor K = 10 (conditional) | 9.856 / 15.236 | 1.183 / 1.636 | −1.639 | 0.0575 [0.0481, 0.0686] | 0.0570 [0.0477, 0.0680] | 960.3 / 984.4: 0 / 0 |
   | P3-D factor K = 1 (sensitivity) | 3.893 / 6.042 | 0.328 / 0.455 | −0.586 | 0.0550 [0.0458, 0.0659] | 0.0480 [0.0395, 0.0583] | 478.1: 0 / 0 |
   | P3-D full | 2866.7 / 4923.3 | 412.9 / 637.6 | +3.694 | 0.0550 [0.0458, 0.0659] | 0.0495 [0.0408, 0.0599] | 853.7 / 940.4: 0.4565 / 0.7310 |

   All eight main-rule FPRs are PASS in the 99 % region [0.0322, 0.0678] of α, calibration noise 1/2000 included.
5. **D5 drift cells, H = 250** (detection rate; G_ADD = RMST_H(P1-D)/RMST_H(P3-D) with its 95 % paired bootstrap CI):
   - **Rotation PC1–PC2** (exploratory; joint Gaussian design information 0.945, 3.53 and 7.06 nat/day).
     - P3-D factor K = 1 detects in every run: G_ADD 14.59 [13.84, 15.42], 67.71 [65.10, 70.35] and
       105.42 [102.04, 109.07], all `lower_bound`.
     - Factor K = 10 detects at 0.358, 0.965 and 1.000: G_ADD 1.238 and 3.932 (`undetermined`), then
       12.30 [11.66, 12.93] (`lower_bound`).
     - Full stays at the null level (≤ 0.069).
     - P1-D falls below its FPR (0.040, 0.024, 0.006): the rotation lowers the variance of the equal-weighted index,
       which a one-sided energy CUSUM cannot detect.
   - **Deformation of PC2–PC4** (prespecified; r = 1.25, 1.5, 2).
     - Factor K = 1: 0.098, 0.154, 0.287; G_ADD 1.031, 1.066, 1.161 (`undetermined`).
     - Factor K = 10: 0.065, 0.077, 0.098.
     - Full and P1-D stay at their FPR.
   - **PC2–PC3 negative control** (prespecified) and **PC2–PC12** (exploratory; bulk–bulk on an equicorrelated
     panel): detection at the null level for every monitor, G_ADD between 0.989 and 1.006 (both H).
   - H = 500 gives the same pattern, with PC1–PC2 at G_ADD 19.20, 105.97 and 177.30 (K = 1).
6. **Checks.**
   - `.venv/bin/pytest -q tests/test_e6.py`: 13 passed; the assertion added to `test_d6_ci_rule` by the audit
     correction failed before the fix (RED).
   - Old against new CSV (`read_csv(dtype=str)`): 190 × 50 in both; every cell outside `ci_reason` is identical as
     text; `ci_reason` differs on exactly the 72 D6 drift rows (36 per H); the four figure SHA-256 are unchanged.
   - `make check` (make 4.4.1, `.venv` tools): pyflakes clean; contracts 22 passed and 4 skipped; main suite 241
     passed and 4 skipped; 3 min 08 s.
   - Skip reasons, from `pytest -rs` on the three skipping files (`make check`: 263 passed, 8 skipped): the 4 contract
     skips are the torch guards (`tests/test_contracts.py`; torch is not installed before stream 14). The 4 main-suite
     skips need D4, absent from the worktree: `tests/test_data_eurofidai.py` l.318, 326, 337 and `tests/test_chars.py`
     l.69.
7. **SHA-256 of outputs.**
   - `results/e6/e6_cells_phase1.csv`: 4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249
   - `figures/e6/e6_phase1_delays.png`: ca929eee4cb9f7e3bad769241cb7df8145c3354f6f4da56c6491b73bebc9e897
   - `figures/e6/e6_phase1_delays.pdf`: cdffaf9eb2755a98f01193ce206010a57c4979556f79fe24c723e3b55b1dc811
   - `figures/e6/e6_phase1_gadd.png`: f14e06cb976cd8099e66daf826f76d474a67eebf512367c02375281c18b34113
   - `figures/e6/e6_phase1_gadd.pdf`: 1ed21dc6ee4317eabf0d0c2996d5b3d7b57bdfb00db8a2a91e04984a3777570b
   - inputs: `data/derived/d3_239/ret_wide.npy` a266fbab…, `data/derived/d3_239/splits.yaml` 3f3a65ba…,
     `configs/e6.yaml` ca74d2e117edb47b0ff11822501a20a381460c35c69e81b57a6d11de81a2bcf5.

## Errors and Dead Ends

- **Plan revision 1** (base `5048a96`) was rejected, and its GO suspended, for three reasons. It normalized P1-D as
  (z² − 1)/√2, whereas the Article B stream (r² − mean r²)/std(r²) is required. It treated ⌊941/H⌋ as an effective
  size. It gave D6 CIs from it. Revision 2 corrected all three before any code.
- **Interpreter.** The first exploration calls prefixed git and ls with `conda activate Trading` (no Python ran
  under Trading); the orchestrator then imposed `.venv` only.
- **D5 thresholds depend on the fit panel.** The planning probe used another fit panel (seeds `[23, 99, …]`): it gave
  λ_D5 = 88.8, 28.8 and 4953 at H = 250 (P1-D, factor K = 10, full), against 26.6, 9.86 and 2867 here. This is no
  defect of the run: the plan fixed a single fit panel.
- **Shell incidents.** The sandbox has no `$TMPDIR`: a redirect failed, and outputs went to the session scratchpad.
  GNU `nproc` printed 1 because it honours `OMP_NUM_THREADS`, although 48 CPUs are available.
- **Display artefact.** An ad hoc pandas string concatenation printed NaN for the D6 G_ADD (pandas 3 string dtype);
  the CSV itself holds the values.
- **Audit of `7e4c7a1`.** Two formulations went beyond the protocol. « Every window start is an onset » is an
  equivalent counterfactual onset: the F4 matrix is fitted on the clean calib rows and does not depend on the onset,
  F4 and the streams act day by day, and the CUSUM restarts at each window start. The 10-block D6 `IC=NA` rule was
  attributed to Künsch (1989) and Lahiri (2003) as a requirement of any block bootstrap or deff; it is the conservative
  prespecified reporting criterion of the protocol. The script docstrings, `ci_reason`, `C-E6-phase1` and this wrapup
  are corrected; only the `ci_reason` values of the 72 D6 drift rows change.
- **Correction plan, revision 1.** Its step 0 copied the plan into `prompts/plans/`, although the plan's own
  staged-diff check forbids the literal home path that it quoted. The orchestrator had the copy dropped from the
  commit (revision 2).
- **Language of the GO frame.** The approved plan framed `prompts/GO-stream-23-audit.md` in English; `CLAUDE.md`
  imposes French for GO reviews (restated in the stream 17 GO, 2026-10-23), so the frame is in French and the quoted
  messages stay verbatim.
- **jCodeMunch reindex refused.** `tools/reindex_graphify_jcodemunch.sh` updated Graphify (3469 nodes, 4114 edges,
  284 communities), then `jcodemunch-mcp index` stopped: « Both local and git identity indexes already match this
  path ». Two indexes claim the worktree: the local `local/JEPA-stream-23-482e4543` and the git-identity index
  `JEPA-Drift/JEPA-Drift-experiments` of the main tree, the same repository. The MCP `index_folder` and a
  path-limited CLI run gave the same refusal; `register_edit` only flags the two edited Python files
  `edited_uncommitted`. After these three attempts no index was invalidated, since the git-identity index serves the
  main tree.

## Current State

- `stream-23` = `2b0b1cd` plus two commits:
  - `7e4c7a1` `feat(e6): measure second-order F4 detection with P1-D and P3-D (stream 23, phase 1)`, which holds
    `experiments/e6_second_order.py`, `configs/e6.yaml`, `tests/test_e6.py`, `results/e6/e6_cells_phase1.csv`,
    `figures/e6/*`, `docs/DEVIATIONS.md` (new entry `C-E6-phase1`, in English), `prompts/plans/plan-23.md`,
    `prompts/GO-stream-23.md` and this wrapup;
  - `fix(e6): scope the D6 counterfactual onset and the prespecified CI criterion (stream 23)`, which holds the script,
    the test, the CSV, `docs/DEVIATIONS.md`, `prompts/GO-stream-23-audit.md` and this wrapup.
- Stopped before fetch, push and merge, for the orchestrator's audit. `logs/e6/phase1.log` stays local (ignored).
- Phase 1 P1-D/P3-D is delivered before J3 (2026-11-01). P4-D (stream 17) and phase 2 (stream 16) remain open.

## Vigilance Points

1. **D6 carries no drift information at δ = 0.5.**
   - The in-sample threshold is the peak of the late-2018 episode: the attained FPR is 0 and the next level 24–57 %.
   - Detections are the tie block, not evidence of the drift. Treat every D6 cell as descriptive; no G_ADD from D6
     enters a claim.
2. **D5 is conditional on one fit panel.** λ_D5 and Γ_z^op vary by a factor of about 3 between fit panels (probe
   against delivered run). The FPR control stays valid, since calibration and test panels are exchangeable given that
   panel.
3. **Out-of-sample whitening bias.**
   - On independent panels, the null mean of q is −1.64 (factor K = 10) and +3.69 (full): P3-D full is blind on D5
     (Γ_z^op 413–638).
   - The same bias awaits real monitoring after J4, where the representation is fitted on calib and monitors 2020+.
4. **Unequal attained FPRs** (0.048 to 0.0575, all within the 99 % region) move G_ADD off 1 on weak drifts. On the
   PC2–PC3 negative control, full gives 0.995 [0.991, 0.999] at H = 250. A G_ADD within a few percent of 1 is not a
   gain.
5. **The PC2–PC12 rotation is not comparable across backgrounds.** It is factor–bulk on D6 (information 0.124 to
   0.926) but bulk–bulk on the equicorrelated D5 (0.022 to 0.165).
6. **P1-D's one-sided energy CUSUM misses variance decreases.** For PC1–PC2 rotations its detection rate falls below
   the FPR, so those G_ADD values are lower bounds driven by P1-D's blindness.
7. **The budget is a design reference only.** `budget_days` = ln(H/α)/I is never a delay bound of the energy CUSUM,
   and the information is the Gaussian design value, not the KL of t₇ or D6 backgrounds.
8. **Rebase onto `main`.** Local `main` is at `c284823`: stream 27 appends 61 lines to the end of `docs/DEVIATIONS.md`,
   where `C-E6-phase1` also ends, so a conflict is expected there when `stream-23` is rebased.
9. **Stale jCodeMunch index.** `experiments/e6_second_order.py` and `tests/test_e6.py` are flagged `edited_uncommitted`
   in `local/JEPA-stream-23-482e4543` with their old symbols; refreshing them needs a choice of the colliding index
   to invalidate.

## Recommendations

1. **Before phase 2 (P5-D).** Decide whether energy streams are standardized on independent calibration data, a
   specification change of P3-D/P5-D: the out-of-sample whitening bias dominates the D5 thresholds.
2. **Replicate the D5 fit panel** (role 0, index r = 0…R−1) to estimate the spread of λ_D5 and of the D6 rule's
   out-of-sample FPR, instead of conditioning on one draw.
3. **Separate calibration from evaluation on real data.** That requires out-of-sample windows, for example a fit and
   thresholds on a pretrain sub-window and evaluation on calib. With 941 calib days, the conservative prespecified
   reporting criterion refuses every D6 CI.
4. **Variance-decrease drifts.** A two-sided or likelihood-ratio variance CUSUM would see the drifts that lower the
   index variance (PC1–PC2 rotations), which the one-sided energy statistic cannot.
5. **P4-D after stream 17.** Reuse `run_d6`/`run_d5` with the IPCA representation once it is registered; P5-D needs the
   stream 16 checkpoint.
6. **Weak-drift comparisons.** Compare G_ADD at matched attained FPR, or report it beside the null-level G_ADD of the
   negative control.
