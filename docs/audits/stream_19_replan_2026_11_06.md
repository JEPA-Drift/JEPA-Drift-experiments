# Stream 19 replanning audit — E4 scaling in N and the P3-KF comparator, 2026-11-06

## Scope and authority

- Request: `logs/orchestration_20261106/plan-request.md` (ignored by Git). GO: `prompts/GO-stream-19.md` (2026-11-06,
  17:49 UTC; Codex within the mandate delegated by the researcher). Canonical plan: `prompts/plans/plan-19.md`. Its
  section 11, « Décision GO intégrée », settles Q1–Q4 and amends H2–H5, G4, C4 and C6. The reviewed native plan is
  archived as `logs/orchestration_20261106/native-plan-reviewed.md`.
- Review: `logs/stream_19/codex-review-round1.md` (Codex, round 1, ignored by Git) asked for six documentary
  corrections. They are applied here, with the GO and the scope unchanged:
  - the scope of variation in F1;
  - readings and restricted delay in F2;
  - the qualification of the factor term in F2;
  - absence and uniqueness statements bounded to the inspected tree and sources;
  - the meaning of read-only commands;
  - provenance in the wrapup.
- Base `69d562419be77b17af9e56711a6ae069caa6bfc4`, branch `stream-19`.
- Object: a documentary replanning of the historical stream 19 after the full PCA benchmark of streams 28–31. Stream
  19 is E4, scaling in N with the P3-KF comparator (`prompts/streams/prompt-19-e4-p3kf.md`). The GO states that the
  historical prompt is not an order to launch a campaign. This audit closes no E4 campaign.
- Outputs: this audit and `prompts/wrapups/wrapup-19.md`, plus the ignored logs `logs/stream_19/doc_checks.log` and
  `logs/stream_19/doc_checks_round1.log`.
- Not done, because outside the GO:
  - no benchmark, smoke, monitor, test, configuration or new data;
  - no new slope, cost extrapolation, grid or hyperparameter;
  - no read of returns (`ret_wide.npy` included) and no `make check`;
  - no change to code, results, figures, `paper/`, `docs/DEVIATIONS.md`, `docs/sections/`, `prompts/streams/`, the
    prompt master, the 01–27 audit, stream 21 files, memory files or dependencies;
  - no Git mutation, no reindexation and no external source (GO Q1).
- Vocabulary:
  - "Historical prompt" means prompt 19 as written.
  - "Proposal" means an option for a future plan, still to be arbitrated. A proposal never modifies the historical
    criteria (GO H3, H4).
  - "Partial historical overlap" is used instead of any claim of redundancy. A shared (dataset, family, pipeline)
    triple does not establish that a protocol is duplicated exactly (GO H2).

## Sources read

- **Read in full:**
  - `CLAUDE.md` (`AGENTS.md` is a symbolic link to it);
  - `logs/orchestration_20261106/plan-request.md`, `prompts/streams/prompt-19-e4-p3kf.md`;
  - `docs/audits/streams_01_27_relevance_2026_11_06.md`, `docs/audits/stream_18_closeout_2026_11_06.md`;
  - `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`, `paper/sec3_theory.tex`;
  - `prompts/wrapups/wrapup-18.md`, `prompts/GO-stream-19.md`, `prompts/plans/plan-19.md`;
  - `logs/stream_19/codex-review-round1.md`.
- **Read in part:**
  - `docs/DEVIATIONS.md`, lines 200–334, 548–772 and 886–985;
  - `prompts/streams/prompt-12-e1.md`, lines 1–64;
  - `prompts/plans/plan-12.md`, lines 399–438;
  - `prompts/wrapups/wrapup-12.md`, lines 20–139;
  - `docs/sections/pca_drift_benchmark.md`, lines 1–120, 255–275 and 336–350, plus matching lines;
  - `jepadrift/floors.py`, function list and lines 90–119;
  - `jepadrift/pipelines.py`, function list and lines 48–62;
  - `jepadrift/stats/drift.py`, function list;
  - `paper/articleC_biblio_addendum.bib`, lines 52–73;
  - `results/e1/e1_j2_summary.txt` and the header and first lines of `results/e1/e1_slopes.csv`;
  - the constants of `results/pca_drift_benchmark/full_2000_20261101/manifest.json`, by `grep`.
- **Matching or cited lines only:**
  - `prompts/streams/INDEX.md`, `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md`;
  - `prompts/wrapups/handover-01-27.md`, `prompts/wrapups/wrapup-01-11.md`, `prompts/wrapups/wrapup-06.md`,
    `prompts/wrapups/wrapup-31.md`;
  - `docs/audits/PCA_CONTRACTS_VALIDATION.md`;
  - `prompts/Prompts_Claude_Code_v5.md`, `prompts/Orchestration_Streams_v6.md`;
  - `prompts/Plan_Claude_Opus_v3.md`, `prompts/Plan_Claude_Opus_v4.md`, `prompts/Plan_Claude_Opus_v4_correction.md`.
- **Located by `grep` only, for their SPLL and tail10 mentions:** `prompts/GO-stream-06.md`, `prompts/plans/plan-06.md`,
  `docs/sections/interface_Z.md`, `prompts/session_JEPA_recuperee.md`.
- **Not opened:** any return series, any D4 or `d3_500` file, and the full-run `trials.csv`.

## Commands executed

All commands ran from the worktree root on 2026-11-06. None modified a source, a data file, a result, code or a Codex
file. No Python process was started and no repository module was imported. In this audit, "read-only" means exactly
that: no scientific, source or data mutation. The session's only writes were the two owned files and the ignored
journals under `logs/stream_19/`, created with `mkdir -p` and appended with `tee -a`. The native plan file of the plan
phase lies outside the repository.
- **Plan phase:** `ls`, `grep`, `sed -n`, `wc`, `git rev-parse`, `git log`, `git status` and `git check-ignore`.
- **After the GO, before any write:**
  - `sha256sum` of the Codex files, of the archived native plan and of the sources listed under Hashes;
  - `git ls-files --eol` on the E2 CSV;
  - `test -e` on the cited paths and on the historical E4 deliverables.
- **After writing:** the documentary controls C1–C7, appended to `logs/stream_19/doc_checks.log`.
- **After review round 1:** the same kinds of command, run on the corrected prose and on the newly cited source lines,
  appended to `logs/stream_19/doc_checks_round1.log`.

## F1 — What the full PCA benchmark measures

- **Fixed cross-section and horizon.** The manifest
  `results/pca_drift_benchmark/full_2000_20261101/manifest.json` records `"H": 250`, `"N": 239`, `"T_fit": 1000`,
  `"alpha": 0.05` and `"nmax": 20` (lines 32–45). It also records the synthetic equicorrelation `"rho": 0.4` (line
  93). Prompt 28 fixes the same defaults (line 20) and a 239-asset synthetic model (line 22).
- **Dimensional comparisons.** Inside one frozen basis, they vary two sizes while N stays fixed:
  - `k`, the size of the candidate reservoir P_k = axes 1..k;
  - `d`, the size of a selected subset S (`docs/sections/pca_drift_benchmark.md`, lines 25 and 101–102).
- **Other factors.** Rows also differ by factors other than dimension:
  - the dataset (`SYNTH_GAUSS_EQUICORR`, `SYNTH_T7_EQUICORR`, `D3_239`; line 262);
  - the scenario or event (line 264);
  - the detector family (line 266);
  - the selection method (lines 339–348).

  None of these factors is the size of the cross-section.
- **Synthetic rows and real cohorts.**
  - Synthetic rows come from independently generated paths (prompt 28, line 22). The predictive-rank threshold
    guarantee is established for such independent synthetic paths (C-pca-predictive-rank).
  - The real `D3_239` rows belong to two registered cohorts (line 263), and both stay `BLOCKED_PRE_J4`. They read no
    return after 2019-12-31, and their rows carry NA metrics (C-pca-covid-retrospective).
  - This audit did not examine which pre-2020 real quantities of the full run were computed.
- **Consequence.** N stays fixed at 239 in the full run, so the benchmark measures no law in N and yields no slope in
  N. This audit extracts none.
- **Status of the selection score.** V(S) = I(S)/M(d, γ) is a surrogate. Prompt 28 says M must never be called "an
  exact ADD/finite-ARL cost" (line 40). C-pca-benchmark-design keeps M as a fluid substitute, never an exact delay.
- **Guarantee on historical windows.** The predictive-rank guarantee is not established for overlapping historical
  D6 windows (C-pca-predictive-rank).
- **Use for stream 19.** The benchmark frames, at fixed N, the remark of Section 3 that ordering by variance differs
  from ordering by drift information (`paper/sec3_theory.tex`, line 68). It does so through spectral prefixes against
  information-selected subsets. No benchmark figure or aggregate is quoted.

## F2 — Six quantities kept apart

No quantity below is converted into another. In particular, no exact ADD is inferred from a fluid cost, and no slope
is computed.

1. **Conditional exponent.**
   - *Statement and source:* corollary `cor:scaling` (`paper/sec3_theory.tex`, lines 82–84). With I(N) ≍ N^a and
     D(N) ≍ N^b, and D ≫ ln γ when b > 0, the fluid gain over a single asset scales as N^(a−b/2). The three cases are:
     - N^0 for a market drift watched by pooling;
     - N^(1/2) for an unstructured breadth drift watched in the full residual;
     - N^1 for breadth carried by fixed characteristic directions.
   - *Validity:* fluid delays of proposition `prop:tax` (c), derived for an i.i.d. Gaussian whitened stream (lines
     70–78).
   - *Archived measurement:* none as an exponent in the sources read. The E1 slopes (F3) are restricted-delay slopes
     at a finite horizon.
2. **Information I(N).**
   - *Statement and source:* corollary `cor:factor` (lines 54–64).
     - The factor term is at most Δλ̃ᵀΣ_F⁻¹Δλ̃ (line 58), and Section 3 reads it as bounded in N (line 64). The exact
       condition for this bound to stay finite as N grows is sup_N Δλ̃_NᵀΣ_F,N⁻¹Δλ̃_N < ∞. Under it, the factor term
       is bounded in N.
     - A sufficient case is Σ_F fixed and positive definite, with Δλ̃ fixed or uniformly bounded in N.
     - An upper bound on Σ_F alone does not suffice: the quadratic form can diverge when the smallest eigenvalue of
       Σ_F,N tends to zero.
     - The bound is not uniform over drift scalings that depend on N.
     - The breadth term grows linearly in N when Δα⊥ spreads over many assets (line 64).
     - The one-factor ratio N/(1+(N−1)ρ) tends to 1/ρ (line 61).
     - Encoders create no information: I_z ≤ I_x (line 20).
   - *Validity:* E1 uses the Gaussian quadratic information of the injected drift, not the exact KL of D6 backgrounds
     (prompt 12, lines 10 and 19; C-e1-predictions).
   - *Archived measurement:* G_floor = I_B/I_A, computed from the injected drifts; an E1 design quantity.
3. **Alignment.**
   - *Statement and source:* a_max = max_k Δz_k²/‖Δz‖² (`CLAUDE.md`, lines 51–53; prompt 12, line 20). In
     `prop:tax` (d), the alignment is cos²ϑ to the nearest atom (line 76).
   - *Validity:* whitened coordinates of a frozen basis, computed from the injected drift.
   - *Archived measurement:* E1 arm B reports a_max(N), I_z(N) and K_eff(N) per (N, chain) (`prompts/plans/plan-12.md`,
     line 436).
4. **Mixture and dictionary costs.**
   - *Statement and source:*
     - Mixture: M(D, γ) = x*/ln γ with x* = ln γ + (D/2) ln(1 + 2x*/D) (`prop:tax` (b)–(c), lines 74–75;
       `jepadrift/floors.py`, `mixture_multiplier`, lines 94–105).
     - Dictionary of K atoms: at most (ln γ + ln K)/(cos²ϑ ln γ) times τ_γ (line 76; `dictionary_multiplier`, lines
       108–113).
   - *Validity:*
     - The mixture is a test supermartingale when z_t is conditionally sub-Gaussian with variance proxy I_D under P_0
       (line 73), with the matched prior s² = 2I/D (line 71). On real sign streams it needs the independence gate.
     - An average of test supermartingales remains one under any dependence (`rem:mixture`, line 99). The dictionary
       multiplier is a fluid upper bound.
   - *Archived use:* E1 predictions (`CLAUDE.md`, lines 51–53) and the PCA benchmark's selection surrogate. Never an
     exact ADD.
5. **Fluid budget.**
   - *Statement and source:* τ_γ = ln γ/I (lemma `lem:budget`, lines 29–35).
   - *Validity:* exact as a budget for a test supermartingale started at the onset. It is not the Lorden-optimal ADD
     Φ(γI)/I (`CLAUDE.md`, lines 15–17).
   - *Archived measurement:* analytic only.
6. **Calibrated readings, observed FPR and restricted delay.**
   - *Readings defined by prompt 12:* at horizon H, with nominal target α = 0.05 and the observed FPR(H) reported per
     cell (lines 14–17), there are three kinds:
     - anytime-valid: an e-detector stopped at γ_H = H/α, since P∞(alarm before H) ≤ H/γ;
     - exact: a sign CUSUM at the attainable lattice level ≤ α at horizon H, compared with the lattice midpoint
       `select_threshold(...)["threshold"]`, never with `lam`;
     - bootstrap (R15 port, H = 750) and randomization (sign flips): an empirical FPR(H) near α is targeted, with no
       automatic guarantee.
   - *Qualifications:*
     - Gains are at common nominal α.
     - "Equal false alarm" is reserved for G_ADD,ex, that is exact readings at the same lattice level, when the paired
       95 % interval of the H0 difference lies within ±0.01.
     - Paired H0 arms belong to arms A and S (C-e1-readings).
   - *Restricted delay, a metric and not a reading:*
     - ADD_H = mean(min(T, H)), written add_h, with min(T, H) = H for a path without alarm. It does not estimate the
       Lorden worst case, and the term "Lorden ADD" is reserved for analytic bounds (prompt 12, line 13).
     - G_ADD,H is the ratio of these restricted delays at equal reading and H, not a ratio of Lorden ADDs (line 18).
     - The PCA benchmark's RMST250 = mean(min(T, 250)) is the same kind of restricted mean (prompt 28, line 64).
     - Φ(γI)/I is a diffusion approximation, never an exact ADD bound at finite γ (C-e1-readings).
   - *Archived use:* the E1 arm B slopes quoted in F3 are slopes of add_h ratios under the anytime-valid reading, with
     H = 2000 and γ_H = 40,000 (plan 12, line 401). The sources read attribute no other reading to them.

## F3 — Archived evidence on slopes in N

Among the sources read, only E1 arm B (stream 12) reports slopes in N. The lines below are quoted verbatim from
`results/e1/e1_j2_summary.txt`. Its SHA-256 is under Hashes and matches the value recorded in
`prompts/wrapups/wrapup-12.md`, line 29.

> window 2005-01-04..2019-12-31; retrospective: the calib rows 2016-04-07..2019-12-31 follow every onset at H = 2000; add_h = mean(min(T, H)) is a restricted delay, Phi(gamma I) / I a diffusion approximation

> J2(ii): PASS - slope of log G_ADD,H(P1 ref -> P2-C) on log N, F3, N >= 20: CI contains 0 or upper < 0.15: d2_us97 amp 2: 0.001 [-0.039, 0.036]; d2_us97 amp 4: 0.003 [-0.041, 0.045]; d3_239 amp 2: 0.102 [-0.016, 0.311]; d3_239 amp 4: 0.063 [-0.039, 0.225]

> J2(iii): PASS - slope of log G_ADD,H(P1 ref -> P3-C full) on log N, F2: positive, CI excludes 0: d3_239 amp 2: 0.169 [0.141, 0.197]; d3_239 amp 4: 0.175 [0.138, 0.218]

Qualifications (GO Q2). These are archived results; this audit neither reproduces nor re-derives them.
- **Estimator.** OLS of log G_ADD,H(N) = log add_h(P1 ref.) − log add_h(P) on log N, with the (chain, N) cells
  pooled. Cells where P detects at most 50 % are excluded. The 95 % interval is a percentile bootstrap over the 20
  chains (plan 12, lines 404 and 430–435).
- **Reading.** Anytime-valid at γ_H = 40,000 with H = 2000 (plan 12, line 401), so the gains are at common nominal α.
  The sources read record paired H0 arms for arms A and S only (C-e1-readings). These slopes therefore say nothing
  about whether attained FPRs are comparable.
- **Retrospective.** In every cell, the calib rows follow the onsets (summary line 1; `prompts/wrapups/wrapup-12.md`,
  line 136).
- **Amplitudes.** After the pilot, the F2 amplitudes moved from κ ∈ {1, 2} to {2, 4}, while the F3 amplitudes of the
  prompt were kept (wrapup-12, lines 131–132; C-e1-amplitude-grid).
- **Mixture and P3-CS (b).** Mixture cells exist only where the Holm gate passes on the subset (wrapup-12, lines
  129–130). The P3-CS (b) and gated-mixture slopes are reported in wrapup-12, lines 45–46, and are not quoted here.
- **Characteristic defect.** The injected F2 uses the stored `c_beta_252` among its four continuous characteristics
  (C-e1-f2-chars). C-D3-beta-denominator describes that characteristic as computed with a faulty denominator. The
  sources read record no E1 rerun after a correction.

## F4 — Dependencies and bounds

For each stream: its delivery state (taken from the 01–27 audit), what prompt 19 requires, and what a future plan
might do. The last item is only a proposal, still to be arbitrated, and does not modify the historical criteria (GO
H3).

- **05, injections** (`jepadrift/injection.py`, `jepadrift/sim.py`).
  - Delivery state: `CLOS_VALIDÉ` (01–27 audit, line 25).
  - Prompt 19: F1, F2 (κ) and F3 under convention (b), on D6 backgrounds (lines 13–20).
  - Future plan: required for any injected family.
- **07, pipelines** (`jepadrift/pipelines.py`).
  - Delivery state: `CLOS_VALIDÉ` (line 27).
  - Prompt 19: P2-C, P3-C factorial and full, and P3-CS (b), read anytime-valid at γ_H = H/α with H = 2000 (lines
    21–23).
  - Future plan: required.
- **08b, hygiene** (`jepadrift/data_loader/chars.py`, `jepadrift/stats/drift.py`).
  - Delivery state: `CLOS_VALIDÉ` for the original scope (line 29).
  - Prompt 19: F2 characteristics, and a reduced per-subset audit with `debiased_sr2` and `mbb_indices` (line 31).
  - Future plan: required for F2. The per-subset audit could become optional.
- **11, audit** (`experiments/audit_information.py`).
  - Delivery state: `CLOS_VALIDÉ` (line 32).
  - Prompt 19: listed as an input (line 34).
  - Future plan: binding reading constraints only. Boundary selection applies, and
    `results/audit/predicted_gains.csv` stays descriptive with its NaN kept (`CLAUDE.md`, lines 69–74).
- **17, IPCA** (`jepadrift/representations/ipca.py`).
  - Delivery state: `CLOS_VALIDÉ` for the explicit engineering scope (line 37).
  - Prompt 19: P4-C (line 22).
  - Future plan: P4-C could become optional. P4-D, absent from the historical list, stays outside calibrated
    comparisons (C-P4D-null-insample).
- **18, CD-DFM.**
  - Delivery state: `BLOQUÉ` for model integration (line 48).
  - Prompt 19: "CD-DFM si disponible" (line 22), and "(et 18)" among the inputs (line 34).
  - Future plan: "non disponible", with no hidden replacement (`docs/audits/stream_18_closeout_2026_11_06.md`, line
    117; `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md`, line 26).

Bounds that bind any future lot; this audit corrects none of them:
- **Mixture gate.**
  - The literal independence rule fails on D2 in both modes. In full mode it would fail even under independence,
    through multiplicity (C-P3C-mixture-gate).
  - The Holm version still fails on D2 factor (C-e1-holm-gate) and on D3 factor and full (wrapup-12, line 129).
  - Prompt 19 therefore makes the dictionary the default detector (line 9). A mixture reading is a gated diagnostic
    with approximate validity.
  - The N^(1/2) case assumes a mixture over the full residual (prompt 19, line 6). Where the gate fails, it has no
    gated reading on these backgrounds, except on subsets where the gate passes (wrapup-12, line 130).
- **Beta denominator.**
  - `c_beta_252` is computed with a faulty denominator on D3 and D4. It is used as is, and its correction belongs to
    another stream (C-D3-beta-denominator).
  - `d3_239` is affected: against the OLS beta, 71.1 % / 75.6 % of the ranks change (pretrain / calib).
  - Every F2 cell (C-e1-f2-chars) and every IPCA row (C-IPCA-K) inherits the defect.
- **Phantom ranks.**
  - The audited pretrain and calib rows of `d3_239` contain no phantom cell. `d3_500` (momentum and reversal) and D4
    (four characteristics) do (C-D3-chars-phantom, `results/ipca/char_audit.csv`).
  - The absence on `d3_239` is not extended to any future window (GO H3).
- **In-sample null.** P4-D's D6 null check re-reads the windows that set its threshold. P4-D's FPR is uncalibrated,
  and the P3-D D6 window diagnostic is not an out-of-sample FPR estimate either (C-P4D-null-insample).
- **Window geometry.**
  - The calib segment holds 941 days, and a longer horizon raises a `ValueError` (C-P3D-windows).
  - The 99 % region of C-pipe-null-targets ignores window overlap.
  - Overlapping historical D6 windows carry no established predictive guarantee (C-pca-predictive-rank).
- **Panels.**
  - `d3_500` has 13 % NaN, and callers pick complete sub-panels.
  - D4 has no delisting dates and no GICS.
  - Current constituents form a survivorship-biased universe (`CLAUDE.md`, lines 63–67; C-D4-survivor,
    C-D3-survivor-correction).

## F5 — Coverage and necessity of the historical grid

The historical grid (prompt 19, lines 13–31) crosses:
- the datasets;
- N ∈ {8, 16, 32, 64, 128, 239, 500}, bounded by the sub-panel size, with 20 nested subsets per N;
- the families F1–F3;
- the pipelines P2-C, P3-C (factorial and full), P3-KF, P3-CS (b) and P4-C.

The table compares each historical component with E1 arm B (stream 12) and with the full PCA benchmark (streams
28–31), as documented in the sources read.

| Historical component | E1 arm B | Full PCA benchmark | Status |
|---|---|---|---|
| `d2_us97`, N ∈ {8, 16, 32, 64} (bounded by 97 assets) | N ∈ {8, 16, 32, 64, 97} | not covered | partial historical overlap |
| `d3_239`, N ∈ {8, 16, 32, 64, 128, 239} | N ∈ {8, 16, 32, 64, 128, 239} | N = 239 only | partial historical overlap |
| `d3_500`, N = 500 | not covered | not covered | not covered; blocked now (real returns, complete sub-panels, phantom ranks) |
| D4 (group B) | not covered | not covered | not covered; blocked now (proprietary and local, inherited characteristic defects) |
| F1, factor premia | arm A only, at fixed N (wrapup-12, lines 50–56) | not covered | not covered in N |
| F2, κ, on D3 | P3-C full, P3-CS (b), gated mixture | not covered | partial overlap for these pipelines only |
| F3, per-asset SR | P2-C | related market-mean scenario at N = 239 only (prompt 28, line 25) | partial overlap for P2-C only |
| P3-C factorial, P4-C, P3-KF | not covered | not covered | not covered |
| CD-DFM | not covered | not covered | unavailable (`BLOQUÉ`) |
| Slope with bootstrap CI over subsets | OLS of the log add_h ratio against a fixed P1 reference | none | estimator identity not established; prompt 19 asks for the opposite of the slope of the log median ADD (line 29) |
| Predicted exponents, dictionary forecast corrected by a_max(N) | a_max(N) reported per (N, chain); no per-N dictionary forecast identified in the sources read | none | not established |
| Per-subset audit (`debiased_sr2`, `mbb_indices`) | not in arm B | none | not covered |

The table records a partial overlap only. Identity between E1 arm B and the historical E4 text is not established on
the following dimensions (GO H2):
- **Windows.** E1 reads 2005-01-04..2019-12-31, retrospectively (summary line 1). Prompt 19 states only "seules les
  lignes antérieures à 2020 sont lues" (line 12).
- **Amplitudes.** E1 arm B used per-asset SR {2, 4} for F3 and κ {2, 4} for F2 after its pilot. Prompt 19 calls for
  its own application of the prompt 12 rule (line 17).
- **Horizons and readings.** Both name H = 2000 and the anytime-valid reading at γ_H = H/α. Prompt 19 adds exact
  channels as diagnostics (line 23).
- **Sampling units.** E1 arm B used 20 chains and 200 onsets per (chain, N, cell) (plan 12, lines 404 and 417). Prompt
  19 fixes 20 nested subsets per N (line 16) but no onset count.
- **Channels.** E1 arm B monitors the full residual for F2 (plan 12, line 415). Prompt 19 asks for both factorial and
  full P3-C (line 22).
- **Calibration.** Prompt 19 calibrates a P3-KF threshold on D6 null windows (line 27), a rule absent from E1 arm B.
- **Slope estimator.** See the table above.

No historical cell is declared redundant, and no rerun is authorized.

Elements of the historical grid with no archived evidence in the sources read:
- F1 in N;
- F3 beyond P2-C;
- F2 beyond P3-C full and P3-CS (b);
- P3-C factorial, P4-C and P3-KF;
- N = 500 and D4;
- per-N dictionary forecasts;
- the per-subset audit.

The sources contain two framings of whether E4 is necessary; this audit does not arbitrate between them:
- Prompt 19 calls the scaling law in N "La signature falsifiable de JEPA-Drift" (line 4).
- The 01–27 audit calls E4 a "Possible future appendix; expensive and potentially redundant without a new question"
  (line 49).

## F6 — P3-KF and the SPLL reference

- **Historical specification** (prompt 19, lines 24–27, 40 and 46):
  - a semi-parametric log-likelihood (SPLL) detector in `jepadrift/monitors/spll.py`, in numpy only, with k-means
    implemented in the module and seeds passed as arguments;
  - inputs: the "tail10" components (m = 46 on D2, 123 on `d3_239`);
  - k-means on the reference window, and the statistic computed on a sliding window;
  - threshold calibrated on D6 null windows for FPR(H) = α;
  - success criterion: "P3-KF dans la région à 99 % de α sur fonds nuls".
- **Present state.** None of the historical deliverables is present in the inspected worktree at the base. C4 checks
  that each path is absent: `experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`,
  `results/e4/`, `figures/e4/` and `logs/e4/`.
- **Representation** (C-repr-layout).
  - Column 0 of `z_odd` is the market channel in all three modes of `PCAOrthogonal`, "tail10" included. P3-KF reads
    the residual block only.
  - m = 46 on `d2_us97` and 123 on `d3_239` with Ledoit–Wolf eigenvalues; 48 and 130 with empirical eigenvalues.
- **Cost.** No measurement was found in the sources read. `prompts/wrapups/wrapup-06.md` (line 89) assigns "SPLL
  k-means cost and dimension effects" to stream 19.
- **Role in the historical plans.** P3-KF was meant to reproduce prior art for risk R3 ("P3-KF reproduit
  l'antériorité": `prompts/Plan_Claude_Opus_v3.md`, line 303; `prompts/Plan_Claude_Opus_v4.md`, line 342). Section 3
  already cites the low-variance observation (`paper/sec3_theory.tex`, line 68).
- **Calibration constraints for a future lot.**
  - At H = 2000, a D6 window cannot fit inside the 941-day calib segment (C-P3D-windows).
  - Windows of length H drawn from the 2005–2019 pre-monitor rows overlap unless that segment holds at least 2H rows.
  - Overlapping historical D6 windows carry no established predictive guarantee (C-pca-predictive-rank), and the 99 %
    region of C-pipe-null-targets ignores overlap.
  - C-P4D-null-insample documents how a statistic that is invariant under the D6 day signs re-reads its own
    calibration windows.
  - Whether the D6 signs randomize the SPLL statistic depends on how it behaves under x → −x. That cannot be assessed
    before its definition has been checked against the primary source (G8).
- **Reference status: unverified.**
  - Prompt 19 cites "Kuncheva (2013, IEEE TKDE ; vérifier la référence)" (line 24).
  - The reference is listed as unverified in `prompts/wrapups/handover-01-27.md` (lines 918 and 942),
    `prompts/wrapups/wrapup-01-11.md` (line 49), `prompts/Orchestration_Streams_v6.md` (line 593) and
    `prompts/Prompts_Claude_Code_v5.md` (line 1671).
  - No entry for it was found in `paper/articleC_biblio_addendum.bib`. That file's `kuncheva_faithfull_2014` entry (2014, IEEE
    Transactions on Neural Networks and Learning Systems) and its `qahtan_2015` entry (lines 54–65) differ in year and
    venue from the prompt's citation. They support the remark of Section 3, line 68.
  - `prompts/Plan_Claude_Opus_v4_correction.md` (line 924) lists the Qahtan et al. page numbers among metadata
    entered from memory.
  - No external source was consulted, and no title or attribution is proposed (GO Q1).
- **Proposal, to be arbitrated (GO H4).** P3-KF is a complementary prior-art comparator. The central claim of
  `CLAUDE.md` (lines 4–6) does not require it. It stays deferred behind gates, and it is not abandoned. This is neither
  a decision of the researcher nor a general exemption from comparators.

## F7 — Gates before any future scientific lot

These gates are described, not decided.
- **G1 — Question.** A falsifiable question not covered by the archived evidence. The candidates are:
  - F1 saturation in N;
  - extension to N = 500 and to D4;
  - P3-KF prior art;
  - dictionary forecast against a measured slope.

  The researcher chooses; this audit does not rank the candidates.
- **G2 — Sources.**
  - Rows before 2020-01-01 only.
  - A lot on D6 first needs a written lift of the current prohibition on real returns.
  - D4 stays local and is never tracked; `d3_500` needs complete sub-panels.
  - Synthetic D5 backgrounds apply where the object is a law in N with known I(N).
- **G3 — Independent calibration.** For every data-calibrated threshold, such as P3-KF on D6 windows or a bootstrap
  reading, the following are written down before any result (C-P4D-null-insample):
  - data source and independence unit;
  - calibration/evaluation split;
  - sample size and target;
  - uncertainty interval and verdict rule.
- **G4 — Freeze.**
  - `CLAUDE.md` currently requires, as a minimum, that scripts reading real rows refuse dates on or after 2020-01-01
    unless `configs/FROZEN.json` matches (lines 161–162).
  - Before J4, it forbids any hyperparameter, threshold or design choice that uses, or is evaluated on, the monitor
    window (lines 75–76).
  - These are minimum requirements of the current project memory. A future protocol may also choose to freeze a
    pre-2020 configuration (GO H5, G4).
  - Grids, seeds and nested subsets are fixed before any draw. So is the amplitude rule of prompt 12, a recorded
    degree of freedom (C-e1-amplitude-grid). No hyperparameter is chosen from monitor results.
- **G5 — Cost.** No E4 cost measurement was found in the sources read. The nearest archived measurement is the E1
  arm B block: 1,212.9 s within a full E1 run of 3,118.7 s (`prompts/wrapups/wrapup-12.md`, line 20). That run
  covered fewer pipelines and datasets than the historical E4 grid. No extrapolation is made.
- **G6 — Artifacts.** The historical deliverables (prompt 19, line 37) are deferred. Any future code must meet these
  conditions:
  - TDD, with witnesses on fake fixtures only;
  - the 44 sealed contracts of `tests/test_pca_drift_contracts.py` stay compatible and unchanged (1,509 lines and 44
    tests per `prompts/wrapups/wrapup-31.md`, line 236; SHA-256 under Hashes);
  - `jepadrift/monitors/` imports numpy only (`CLAUDE.md`, line 122);
  - CSV files are written through `save_fair_csv`, with SeedSequence keys and results independent of `--jobs`;
  - every reported number traces to a CSV and a script (`CLAUDE.md`, line 126).
- **G7 — Characteristics.** Before any F2 or P4-C cell, choose between two routes:
  - an upstream correction in a separate stream;
  - an explicit inheritance label (C-D3-beta-denominator, C-D3-chars-phantom).
- **G8 — SPLL reference.** Verify it on a primary source before any `spll.py` is written.

## Decision

- **Status.** This documentary replanning lot is complete once Codex has reviewed it. The E4 campaign stays
  `À_REPLANIFIER` (GO Q3): it is neither closed nor abandoned, and the same holds for its unexecuted historical
  components. Row 19 of the 01–27 audit is unchanged.
- **Downstream dependency.** Prompt 22 (E5) lists 19 among its dependencies (`prompts/streams/INDEX.md`, line 107;
  01–27 audit, line 52). This is recorded without arbitration.
- **Numbering.** Prompt 19 cites "Corollaire 2". `paper/sec3_theory.tex` uses one counter shared by propositions,
  lemmas, corollaries and remarks (line 4), so this audit names the statement by its label `cor:scaling`.

## Not examined

- The primary source of the SPLL reference (GO Q1).
- The rows of `results/e1/e1_slopes.csv` beyond its header and first lines, and `results/e1/e1_cells.csv`.
- The full-run `trials.csv`, and the contents of the other CSV files of the full run.
- Any return panel, and any D4 or `d3_500` file.
- Stream 21 files, the stream 23 branch and the other worktrees.
- Whether a future E4 cell would share windows, amplitudes, sampling units, readings, channels and calibration rules
  with an E1 arm B cell (F5).

## Test evidence

- **Not run in this session:** no test, `make check`, pyflakes or prompts-check (GO). Codex keeps the mandatory
  closing checks.
- **Prior reference evidence.** `logs/orchestration_20261106/plan-request.md` reports the base verification made
  before the worktrees were created: pyflakes clean, 37 + 589 tests passed, and five pre-existing D4 skips.

## Documentary controls

C1–C7 follow plan 19, section 7, as amended by GO C4 and C6. They use shell commands only.
- The first checkpoint's output, including its two C6 failures, is in `logs/stream_19/doc_checks.log`.
- The round-1 rechecks are in `logs/stream_19/doc_checks_round1.log`.
- The results are summarized in `prompts/wrapups/wrapup-19.md`.
- **C1.** HEAD equals the base and nothing is staged. The untracked files are this audit, the wrapup once written,
  and the two Codex files. The Codex files keep the SHA-256 recorded before any write.
- **C2.** No tracked file differs from the base (`git diff --quiet` on the whole tree).
- **C3.** `results/e2/e2_cells.csv` has the J1 SHA-256 below, on disk and in the index, with 47 CRLF lines and no bare
  LF.
- **C4.** Every cited repository path exists, except the historical E4 deliverables and `configs/FROZEN.json`, which
  must be absent. Owned outputs not yet written are listed as pending.
- **C5.** Every SHA-256 cited is recomputed.
- **C6.** Every archived number cited is found in its source. Theoretical expressions are tied to their equations by
  line number, without literal search.
- **C7.** Neither owned file contains an absolute home-directory path.

Preserved state:
- J1 is checked by C3.
- D8 remains FAIL at +5.2833 %, as the GO states; it was not examined further.
- The sealed contracts file is unchanged (C2, C5).

## Hashes

SHA-256 values were recorded on 2026-11-06, after the GO and before any write of this session. The review file's
value was recorded at review round 1, before the corrections.

| File | SHA-256 |
|---|---|
| `prompts/GO-stream-19.md` (Codex) | `8c91a47ce064add9ea193d9e3b1af730034452b64b63d68d2c119e68a85445c7` |
| `prompts/plans/plan-19.md` (Codex) | `098e1ca39088205fb56701d6dadff9e3623a42154ce6eea9607903b707d6d16a` |
| `logs/orchestration_20261106/native-plan-reviewed.md` | `d2cb81d9f55a1e87e1cf5765bf4aa740ce99e9b1a0cfaccabe715f9dad64db7e` |
| `logs/orchestration_20261106/plan-request.md` | `e07553e47ebf0aef63d8eed0aeb4b9c537c7181f4255b7a136bdcb3d384a5854` |
| `logs/stream_19/codex-review-round1.md` | `f87634fb9ccee05aab7a863f791cf5fd2c84cf7083be72daeb15dcc2e84e22d7` |
| `CLAUDE.md` | `e2e0d15888c2b235da3162427498a966d8ec18ae1f66b182a32601e4a016c473` |
| `prompts/streams/prompt-19-e4-p3kf.md` | `c184d789b184d37799f300382e42ffe214300685769d153006dbb033dea8f84c` |
| `prompts/streams/prompt-12-e1.md` | `55ec8fe77e3480c3bb5d82a9fc6a0f0b1c68d7576ca9e0f687aad004ccda65f8` |
| `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md` | `1dec0fc099c93d6508cdb876067991315d3056af12db0ebb7930cd7de8eec11b` |
| `prompts/streams/INDEX.md` | `06c7901135cfd42be2556e095950b6a992479fa6a5eb604c129b48c1be89543f` |
| `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md` | `7fc5ced579b1c12c03172c71edfe74546bd980b1109205f5d8dbd62a88c673a2` |
| `docs/audits/streams_01_27_relevance_2026_11_06.md` | `f10409d1eb5a3284822fc1773648ad3211050a311ad189cdce5aea0ef4ae7098` |
| `docs/audits/stream_18_closeout_2026_11_06.md` | `01942d99c1f040761bcc4a826a3789036320f6a7d7570b8d6bf62f0c62f49d55` |
| `docs/DEVIATIONS.md` | `2c83037fda35f406a5660c9e33e7f50c0358f03e28e0870345a77ed886d68b30` |
| `docs/sections/pca_drift_benchmark.md` | `adae1ad1d068830a6eb7b69e6266ac99f2a9f7940099469ab44dc8d2938d9484` |
| `paper/sec3_theory.tex` | `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` |
| `paper/articleC_biblio_addendum.bib` | `5b28489cce1cb14e8c7f1b208ae30e51acfb7a350a3aa56ac23c1edd75c001c7` |
| `jepadrift/floors.py` | `49b36c5ef1b7995a274243180825731d42a61829c70e00fc7fc72841d39a9170` |
| `jepadrift/pipelines.py` | `6eeffac88ee02cedd9c8e6c2739f0ae375aa951d8268c2609dc02a37a97771c9` |
| `jepadrift/stats/drift.py` | `4b7c576129ff6b904ee7ba9e8ca952e02292a67f0162b489ed9a367e30dec717` |
| `prompts/plans/plan-12.md` | `a035e0be6090cf5f7e9aaf6effc28e5dcdeb8205eb251c63f09c31d233e855f8` |
| `prompts/wrapups/wrapup-12.md` | `471f4ac9ae2ec60b08a1acc275c93985b7435d0db714202739d2780306b18f3e` |
| `prompts/wrapups/wrapup-06.md` | `6ace8a9c4615330dee8b257f8567fb63c709e445e981d0e2dfaa0f95bacc8df8` |
| `prompts/wrapups/wrapup-31.md` | `863618f625fd302b4552eca52d986f164a7a14de1072690d449545107110783a` |
| `prompts/wrapups/handover-01-27.md` | `97ea1568820ab58287d4b3fb8375e0507842a398a80bcfc205d68f8f7c3cb960` |
| `prompts/wrapups/wrapup-01-11.md` | `421a912e2d3d1a4236afcebb1a0e4fa4a2a3806870415e9428708d2ad390c4ab` |
| `prompts/Prompts_Claude_Code_v5.md` | `c84d560cfaf821a16892d11cb5ff854f941c09e50a2f07a70026e10d02bdceac` |
| `prompts/Orchestration_Streams_v6.md` | `a9ec37168659918f08dd8a671b1e0e0ee61962233cc50022bf1d2b7021f9d6fc` |
| `prompts/Plan_Claude_Opus_v3.md` | `6bd587d4ccb0aeba0b71767d56836629507781b9a23aba81fa723177b2b966be` |
| `prompts/Plan_Claude_Opus_v4.md` | `6f164e14bfc46d1a341beb6445a3a959877000a371f78e56bba61dd6b4b0a8d7` |
| `prompts/Plan_Claude_Opus_v4_correction.md` | `38d882f6d888e7795d655f2ffcb17534d1669d26fa7f352a03f8b52f91433f8b` |
| `results/e1/e1_j2_summary.txt` | `a949acdca169c66ffbe1e7845641c9358955faa112df4b1194f71bf8fd3243a7` |
| `results/e1/e1_slopes.csv` | `1a3a286c47a21d0124fbe8737436dd9fe2c58222146541a880cadb63992cd93c` |
| `results/pca_drift_benchmark/full_2000_20261101/manifest.json` | `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47` |
| `tests/test_pca_drift_contracts.py` | `2e488fe7eb175466e3d259b2f08cb3a236bb1f57ef33619da9d5efabd2c7f197` |
| `results/e2/e2_cells.csv` (J1) | `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` |
