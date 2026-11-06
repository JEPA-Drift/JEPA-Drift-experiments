2026-11-06T19:22:11Z

# Wrapup — stream 19: E4 / P3-KF documentary replanning

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md` is a Codex request, ignored by Git. It asks for the
  smallest useful documentary lot on stream 19, after the full PCA benchmark and the closure of stream 31. Stream 19 is
  E4: scaling in N and the P3-KF/SPLL comparator. The work had to start in native plan mode, with nothing done before a
  written Codex GO: no test, no code, no experiment, no read of returns, no Git mutation.
- **Constraints carried forward.** The following stay excluded: PCA experiments without an oracle; real-return work;
  JEPA/VAE; freeze or J4; reruns of sealed outputs; Graphify, jCodeMunch and sub-agents. So do changes to the canonical
  prompts, the master, dependencies, `.venv`, scientific producers, representations, monitors, configurations and
  `docs/DEVIATIONS.md`.
- **Plan phase.** Claude wrote the native plan v1 in plan mode, and Codex archived it as
  `logs/orchestration_20261106/native-plan-reviewed.md`. During planning, Codex reframed the lot, acting under the
  researcher's delegated mandate: strictly documentary; no benchmark designed or rerun; stream 18 closed;
  `jepadrift/floors.py` read-only; scope of the request unchanged. The reframing was applied before the plan was
  finished.
- **GO.** The native approval screen was not the GO. Under the same delegated mandate, Codex recorded the canonical
  `prompts/plans/plan-19.md`, whose section 11 is « Décision GO intégrée », and the GO `prompts/GO-stream-19.md`, dated
  2026-11-06, 17:49 UTC.
- **Session.** One interactive Claude Code session ran the work: `claude-opus-5-5`, effort max, auto mode from the
  official mechanism. There was no sub-agent and no Graphify or jCodeMunch call.
- **GO answers.**
  - Q1: no external consultation. The SPLL reference stays unverified, with no supposed title and no new bibliographic
    attribution.
  - Q2: the archived E1 slopes may be cited with their SHA-256, their retrospective reading, the common nominal α and
    their source qualifications. They are neither a reproduction nor proof that attained FPRs are comparable.
  - Q3: the E4 campaign stays `À_REPLANIFIER`; it is neither closed nor abandoned.
  - Q4: Claude runs the documentary controls C1–C7. Codex runs the full suite, reindexation and Git. Claude runs no
    `make check`.
- **GO amendments.**
  - H2: "partial historical overlap" replaces "redundant".
  - H3: historical requirements and future options are kept apart. `d3_239` stays affected by the beta denominator, and
    the absence of phantom cells is not generalized.
  - H4: the claim that P3-KF is not indispensable is a proposal. It is neither a researcher decision nor an exemption
    from comparators.
  - H5 and G4: no new slope, cost extrapolation, grid or hyperparameter. The 2020+ guard is a minimum of the current
    memory.
  - C4 and C6: present paths are checked separately from absent future deliverables. Archived numbers are verified at
    their source, and theoretical expressions are tied to their equations.
- **Review round 1.** `logs/stream_19/codex-review-round1.md` (Codex, ignored by Git) kept the GO and the scope
  unchanged. It asked for six documentary corrections, all applied:
  1. F1: the scope of variation, keeping synthetic rows apart from the blocked real cohorts.
  2. F2: the readings, kept apart from the restricted-delay metric.
  3. F2: the assumptions behind the bounded factor term.
  4. The provenance recorded in this wrapup.
  5. Absence and uniqueness statements bounded to the inspected tree and sources, and the meaning of read-only commands.
  6. Removal of this wrapup's module note.
- **Final precision.** Before the stop, the factor-term condition was made exact in the two owned files. It is
  sup_N Δλ̃_NᵀΣ_F,N⁻¹Δλ̃_N < ∞. A sufficient case is Σ_F fixed and positive definite, with Δλ̃ fixed or uniformly
  bounded. An upper bound on Σ_F alone does not suffice when its smallest eigenvalue tends to zero. No code, number,
  GO or source changed.
- **Owned files.** `docs/audits/stream_19_replan_2026_11_06.md` and `prompts/wrapups/wrapup-19.md`, both in English,
  plus the ignored journals `logs/stream_19/doc_checks.log` and `logs/stream_19/doc_checks_round1.log`. Codex owns the
  plan, the GO, the review, reindexation and Git.
- **Base.** `69d562419be77b17af9e56711a6ae069caa6bfc4`, branch `stream-19`.

## Validated Results

Every command ran from the worktree root on 2026-11-06. No command modified a source, a data file, a result, code or a
Codex file. No Python process was started and no repository module was imported. The only writes were the two owned
files and the ignored journals under `logs/stream_19/`. The audit lists the sources, the commands and the hashes.

- **F1 — Full PCA benchmark.**
  - The manifest fixes `"N": 239`, `"H": 250`, `"T_fit": 1000`, `"alpha": 0.05` and `"nmax": 20` (lines 32–45).
  - Its dimensional comparisons vary the reservoir size `k` and the subset size `d` inside one frozen basis, while N
    stays fixed.
  - Rows also differ by dataset, scenario or event, detector family and selection method. None of these is the size
    of the cross-section.
  - Synthetic rows come from independently generated paths, the setting of the predictive-rank guarantee.
  - The real `D3_239` cohorts are registered but stay `BLOCKED_PRE_J4`, with NA metrics.
  - The benchmark therefore measures no law in N and yields no slope in N; none was extracted.
- **F2 — Six quantities kept apart.**
  - the conditional exponent (`cor:scaling`);
  - information I(N) (`cor:factor`). Its factor term stays bounded in N when sup_N Δλ̃_NᵀΣ_F,N⁻¹Δλ̃_N < ∞. A
    sufficient case is Σ_F fixed and positive definite, with Δλ̃ fixed or uniformly bounded; an upper bound on Σ_F
    alone does not suffice. The bound is not uniform over drift scalings that depend on N.
  - alignment (a_max, cos²ϑ);
  - mixture and dictionary costs (`prop:tax`, `mixture_multiplier`, `dictionary_multiplier`);
  - the fluid budget (`lem:budget`);
  - calibrated readings, observed FPR and restricted delay. The anytime-valid, exact-lattice and
    bootstrap/randomization readings of prompt 12 are kept apart from the restricted-delay metric add_h =
    mean(min(T, H)), which is not a Lorden ADD. The E1 arm B slopes use the anytime-valid reading, at H = 2000 and
    γ_H = 40,000.

  No exact ADD is inferred from a fluid cost.
- **F3 — Archived slopes in N.** Among the sources read, only E1 arm B reports any. The J2(ii) and J2(iii) lines are
  quoted verbatim from `results/e1/e1_j2_summary.txt` (SHA-256
  `a949acdca169c66ffbe1e7845641c9358955faa112df4b1194f71bf8fd3243a7`). They carry six qualifications: estimator,
  reading, retrospective scope, amplitudes, mixture gate and `c_beta_252`.
- **F4 — Dependencies.**
  - Streams 05, 07, 08b, 11 and 17 are delivered (`CLOS_VALIDÉ` in the 01–27 audit).
  - Stream 18 is `BLOQUÉ`, so CD-DFM is "non disponible", with no replacement.
  - Historical requirements and future proposals are kept apart.
  - Six bounds are recorded: mixture gate, beta denominator (which affects `d3_239`), phantom ranks (`d3_500`, D4),
    in-sample null (P4-D, P3-D), window geometry and panels.
  - No producer was corrected.
- **F5 — Coverage.**
  - Partial historical overlap with E1 arm B is limited to three triples: (D2, F3, P2-C); (D3 ≤ 239, F3, P2-C);
    (D3 ≤ 239, F2, P3-C full / P3-CS (b) / gated mixture).
  - Identity is not established on windows, amplitudes, horizons and readings, sampling units, channels, calibration
    and slope estimator. No cell is declared redundant, and no rerun is authorized.
  - In the sources read, these elements have no archived evidence: F1 in N; F3 beyond P2-C; F2 beyond P3-C full and
    P3-CS (b); P3-C factorial; P4-C; P3-KF; N = 500; D4; per-N dictionary forecasts; the per-subset audit.
  - The two framings of necessity (prompt 19, line 4; 01–27 audit, line 49) are recorded without arbitration.
- **F6 — P3-KF / SPLL.**
  - No code or result was found in the inspected worktree.
  - The tail10 input has m = 46 on `d2_us97` and 123 on `d3_239`.
  - No cost measurement was found in the sources read.
  - Its historical role is prior art for risk R3.
  - Calibration constraints: the 941-day calib segment, overlapping windows, and the C-P4D-null-insample mechanism.
  - The reference is unverified and has no entry in `paper/articleC_biblio_addendum.bib`.
  - The proposal that P3-KF is a complementary comparator remains to be arbitrated.
- **F7 — Gates G1–G8.** Described, not decided.
- **Decision.**
  - The documentary lot is complete once Codex has reviewed it.
  - The E4 campaign stays `À_REPLANIFIER`.
  - Row 19 of the 01–27 audit is unchanged.
  - Prompt 22's dependency on 19 is recorded without arbitration.
- **First-checkpoint controls** (`logs/stream_19/doc_checks.log`). These runs checked the superseded audit, 478 lines,
  SHA-256 `e77320ab75ad82c4c63c99af47a1a142cba89450001430683eb46ccffd7bc4fc`.
  - Run 1 (18:22:53Z) and run 2 (18:23:47Z) failed at C6.
  - Run 3 (2026-11-06T18:25:05Z) ended `ALL-CONTROLS-PASS`.
  - The post-wrapup rerun (18:27:55Z) ended `POST-WRAPUP-CONTROLS-PASS`.
- **Round-1 controls** (`logs/stream_19/doc_checks_round1.log`, 2026-11-06T19:16:03Z) ended
  `ROUND1-AUDIT-CONTROLS-PASS`:
  - C1: HEAD equals the base, nothing is staged, and the untracked set is as expected. The Codex GO, plan and review are
    unchanged.
  - C2: no tracked file differs from the base.
  - C3: J1 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` on disk and in the index, 47 CRLF and 47
    LF.
  - C4: 66 distinct cited paths; 59 present, 7 future deliverables absent as expected.
  - C5: 36 hashes recomputed.
  - C6: 3 verbatim quotes and 178 source literals found. This includes the newly cited lines: prompt 12, lines 13–18;
    prompt 28, lines 22 and 64; the PCA schema, lines 263–266, 339 and 348; `paper/sec3_theory.tex`, lines 58, 61 and
    64; and C-e1-readings, C-pca-covid-retrospective and C-pca-predictive-rank.
  - Eight superseded phrases are absent.
  - GO-Q1: no supposed SPLL title.
  - C7: no absolute home-directory path.

  The round-1 post-wrapup rerun first stopped at W-review-lines: the table gave 13 lines for the review file, but
  `wc -l` gives 12. After the correction, it ended `ROUND1-POST-WRAPUP-CONTROLS-PASS` at 2026-11-06T19:19:33Z.
- **Final-precision controls** (same journal, 2026-11-06T19:22:11Z) ended `FINAL-PRECISION-AUDIT-CONTROLS-PASS`:
  - C1 to C5 and C7 as in round 1, with 66 cited paths and 36 hashes;
  - the 3 verbatim quotes;
  - the factor bound tied to `paper/sec3_theory.tex`, lines 58 and 64;
  - the exact condition, the sufficient case and the caveat present in the audit;
  - the four ambiguous wordings absent;
  - GO-Q1.

  The post-wrapup rerun of this refresh is appended to the same journal.
- **Hashes.**

| File | Lines | SHA-256 |
|---|---|---|
| `docs/audits/stream_19_replan_2026_11_06.md` (corrected in round 1 and by the final precision) | 527 | `eac783b195f25cbb77265b7d2f392dca1802c53421380dacbd63fc14cef7cf71` |
| `prompts/GO-stream-19.md` (Codex, unchanged) | 26 | `8c91a47ce064add9ea193d9e3b1af730034452b64b63d68d2c119e68a85445c7` |
| `prompts/plans/plan-19.md` (Codex, unchanged) | 235 | `098e1ca39088205fb56701d6dadff9e3623a42154ce6eea9607903b707d6d16a` |
| `logs/stream_19/codex-review-round1.md` (Codex, unchanged) | 12 | `f87634fb9ccee05aab7a863f791cf5fd2c84cf7083be72daeb15dcc2e84e22d7` |
| `logs/orchestration_20261106/native-plan-reviewed.md` (Codex archive of the native plan) | — | `d2cb81d9f55a1e87e1cf5765bf4aa740ce99e9b1a0cfaccabe715f9dad64db7e` |
| `logs/orchestration_20261106/plan-request.md` (request) | — | `e07553e47ebf0aef63d8eed0aeb4b9c537c7181f4255b7a136bdcb3d384a5854` |

## Errors and Dead Ends

- **C6 failures on wrapped text (first checkpoint).**
  - Run 1 stopped on `never called the exact KL of D6`, and run 2 on `This choice is a degree of freedom`.
  - Both phrases wrap across two lines of `docs/DEVIATIONS.md` (lines 610–611 and 582–583), and the check searched one
    line at a time.
  - The audit was not changed; the check was.
  - A dry run of the remaining literals (102 checked, 0 missing) preceded run 3, which searched whole-file literals on
    line-joined text.
  - All runs stay in `logs/stream_19/doc_checks.log`. Run 3 was the third and last remediation attempt allowed by the
    circuit breaker.
- **First-checkpoint overstatements, corrected in review round 1.**
  1. F1 said that only the monitored dimension varies. It now says that the dimensional comparisons vary k and d at
     fixed N while other factors vary, and it keeps synthetic rows apart from the registered, blocked real cohorts.
  2. F2 listed add_h as a third way of reading. It is now a restricted-delay metric, kept apart from the anytime-valid,
     exact-lattice and bootstrap/randomization readings.
  3. F2 called the factor term bounded in N without its assumptions. It now states the condition
     sup_N Δλ̃_NᵀΣ_F,N⁻¹Δλ̃_N < ∞, the sufficient case (Σ_F fixed and positive definite, Δλ̃ fixed or uniformly
     bounded) and the non-uniformity over drift scalings that depend on N.
  4. Several absence statements ("exists", "not measured", "has no entry") were unbounded. They are now bounded to the
     inspected worktree and the sources read.
  5. "Read-only" was applied to commands that also created and appended ignored journals. It now means no scientific,
     source or data mutation.
  6. The first wrapup attributed the planning reframing to the researcher, called the GO process a rejection, and
     carried an irrelevant module note. All three are corrected here.
- **Round-1 wording of the factor condition.** The first round-1 text said "fixed or bounded" factor covariance. An
  upper bound on Σ_F does not bound Σ_F⁻¹ when its smallest eigenvalue tends to zero. The final precision replaced the
  wording with the exact condition and its sufficient case.
- **Review-file line count.** The round-1 table first gave 13 lines, read off a file viewer's trailing empty line.
  `wc -l` gives 12. The table was corrected before the passing rerun.
- **Native plan wording superseded by the GO.**
  - H2 "redondante" became "partial historical overlap".
  - The H3 phrase "`d3_239` indemne" was restricted to phantom cells in the audited perimeter.
  - H4 became a proposal, and G4 a minimum requirement.
  - The native plan, Q1, held a candidate SPLL title written from memory and labelled unverified. Following GO Q1, it
    is absent from the audit and from this wrapup.

## Current State

- **Lot written, corrected after review round 1 and by the final precision; nothing committed.** HEAD is
  `69d562419be77b17af9e56711a6ae069caa6bfc4`, nothing is staged, and no tracked file differs from the base.
- **Expected `git status --porcelain`:**
  - `?? docs/audits/stream_19_replan_2026_11_06.md`
  - `?? prompts/GO-stream-19.md`
  - `?? prompts/plans/plan-19.md`
  - `?? prompts/wrapups/wrapup-19.md`

  The two Codex files are untracked, unchanged and not owned by Claude. `logs/stream_19/` (review file and both
  journals) is ignored.
- **Not run here.** No test, `make check`, pyflakes, prompts-check, reindexation or Git operation. Prior reference
  evidence comes from the request: pyflakes clean, 37 + 589 tests passed, and five pre-existing D4 skips at the base.
- **Execution environment.**
  - Linux 5.14.0-570.55.1.el9_6.x86_64.
  - Besides shell builtins, only these ran: `git`, `grep`, `sed`, `tr`, `sort`, `cut`, `wc`, `head`, `ls`,
    `sha256sum`, `tee`, `mkdir`, `date` and `uname`.
  - The project interpreter `.venv/bin/python` (Python 3.12.9 on the Trading binary) was not invoked.
  - Codex's controls use `.venv/bin/make` with `PATH="$PWD/.venv/bin:$PATH"`,
    `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and
    `MPLBACKEND=Agg`.
- **Preserved state.**
  - J1 is unchanged (C3), and the D8 FAIL at +5.2833 % is untouched.
  - `tests/test_pca_drift_contracts.py` (44 sealed contracts) is unchanged.
  - Not touched: the 01–27 audit, `paper/`, `docs/DEVIATIONS.md`, `prompts/streams/`, the master, the memory files, the
    other worktrees and branches, and the Codex GO, plan and review files.

### Inventory of files [.md]

- **docs/audits/stream_19_replan_2026_11_06.md:**
  - *Description:* replanning audit, in English, corrected after review round 1 and by the final precision on the
    factor condition. Sections:
    - scope and authority, including the review;
    - sources;
    - commands, including the meaning of read-only;
    - F1: full benchmark (dimensional comparisons at fixed N, other factors, synthetic rows and blocked real cohorts);
    - F2: six quantities (readings kept apart from the restricted delay, exact factor condition);
    - F3: archived E1 slopes;
    - F4: dependencies and bounds;
    - F5: coverage;
    - F6: P3-KF/SPLL;
    - F7: gates;
    - decision, not examined, test evidence, documentary controls and hashes.
  - *Inputs:* the 36 files hashed in its table.
  - *Outputs:* 527 lines, SHA-256 above. Superseded versions:
    - first checkpoint: 478 lines, SHA-256 `e77320ab75ad82c4c63c99af47a1a142cba89450001430683eb46ccffd7bc4fc`;
    - round 1: 523 lines, SHA-256 `bde186474e04525d25036a16195c831e354ac242b7d4048c1583db7fbc8b9143`.
- **prompts/wrapups/wrapup-19.md:**
  - *Description:* this checkpoint, refreshed after review round 1 and the final precision.
- **prompts/GO-stream-19.md, prompts/plans/plan-19.md:**
  - *Description:* Codex GO and canonical plan. Read, not modified.
- **logs/stream_19/codex-review-round1.md:**
  - *Description:* Codex review round 1, with its six corrections. Ignored by Git; read, not modified.
- **logs/orchestration_20261106/plan-request.md, logs/orchestration_20261106/native-plan-reviewed.md:**
  - *Description:* the request and the archived native plan. Ignored by Git; read only.

### Inventory of files [.log]

- **logs/stream_19/doc_checks.log:**
  - *Description:* first-checkpoint journal, preserved unchanged: three C1–C7 runs (two FAIL at C6, one
    `ALL-CONTROLS-PASS`) and the post-wrapup rerun (`POST-WRAPUP-CONTROLS-PASS`).
- **logs/stream_19/doc_checks_round1.log:**
  - *Description:* round-1 journal, in order:
    - `ROUND1-AUDIT-CONTROLS-PASS`;
    - one post-wrapup FAIL at W-review-lines, then `ROUND1-POST-WRAPUP-CONTROLS-PASS`;
    - `FINAL-PRECISION-AUDIT-CONTROLS-PASS`;
    - the post-wrapup rerun of this refresh.

## Vigilance Points

- **Unverified SPLL title in the canonical plan.** `prompts/plans/plan-19.md` (section 9, Q1) keeps the native plan's
  candidate SPLL title, written from memory and labelled unverified. GO Q1 excludes any supposed title, and the GO-Q1
  check confirms the audit contains none. Any use of the reference first needs a primary-source check (G8).
- **Partial overlap is not duplication.** A future plan must not drop historical cells as redundant without first
  establishing that windows, amplitudes, horizons, sampling units, readings, channels, calibration and estimator are
  identical.
- **E1 arm B readings and FPR.** Paired H0 arms belong to arms A and S (C-e1-readings), so their attained FPRs must not
  be attributed to the arm B slopes. The sources read attribute no reading other than anytime-valid to those slopes,
  and add_h is a restricted delay, not a Lorden ADD.
- **Real cohorts of the full benchmark.** They are registered but blocked before J4. This audit did not examine which
  pre-2020 real quantities of the full run were computed.
- **Bounded factor term.** The bound stays finite in N exactly when sup_N Δλ̃_NᵀΣ_F,N⁻¹Δλ̃_N < ∞. A fixed positive
  definite Σ_F with fixed or uniformly bounded Δλ̃ suffices; an upper bound on Σ_F alone does not.
- **Characteristic defects.** `d3_239` is affected by C-D3-beta-denominator. The absence of phantom cells holds only
  within the audited perimeter.
- **Line counts and wrapped sources.** Literal checks against `docs/DEVIATIONS.md` must search line-joined text, and
  line counts must come from `wc -l`, not from a file viewer's display.
- **Unresolved variables (carried forward).**
  - the G1 question;
  - the primary-source verification of SPLL (G8);
  - a written lift of the real-return prohibition, if a D6 lot is wanted;
  - the route for the characteristic defects (G7);
  - a cost budget from an authorized smoke (G5);
  - the arbitration between the two framings of necessity;
  - the Codex review of round 1 and of the final precision;
  - the `make check` result at closeout.

## Recommendations

- **Codex closeout.**
  - Review the corrected audit and this wrapup.
  - Run `make check` and the AST-only reindexation.
  - Stage the audit, the wrapup and the Codex files by explicit path.
  - Make one Conventional Commit without trailers, for example `docs(stream-19): record the E4 replanning audit`.
  - Check the pushed range under the end-of-stream protocol.
- **Future lot.** Start from G1 with a question chosen by the researcher. Fix G3 in writing before any data-calibrated
  threshold is drawn.
- **[Strategic Advice]** Decide the data regime first, synthetic D5 or symmetrized real D6, before choosing among the
  G1 candidates. That one choice settles G2 (real-return authorization), G3 (whether exchangeable independent paths
  exist), G7 (whether the characteristic defects apply) and most of G5. The audit therefore leaves the candidates
  unranked.
