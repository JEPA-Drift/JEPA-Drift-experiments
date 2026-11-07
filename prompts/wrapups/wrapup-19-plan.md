2026-11-07T13:44:25Z

# Wrapup — stream 19-plan: N, k and d theory note and primary-source audit of SPLL

## Context

- **Mandate.** Codex framing of 2026-11-07 for session `jepa-s19-plan`.
  - First phase, plan only: clarify N, k and d around the closed Gaussian oracle, audit the primary SPLL source, and
    isolate a non-redundant question.
  - Second phase: the researcher's documentary GO, recorded by Codex in `prompts/GO-stream-19-plan.md`, for one English
    note, `docs/audits/stream_19_theory_spll_20261107.md`.
- **Authority.** `prompts/plans/plan-19-plan.md` (Codex) prevails over the native plan. Base
  `1440927b49463c13bdd0c819fcd73f30d6a32c31`, branch `stream-19-plan`, worktree `~/JEPA-stream-19-plan`.
- **Session.** Interactive Claude Code, `claude-opus-5-5`, effort max throughout. Native plan mode was kept until the GO.
  No sub-agent and no Graphify or jCodeMunch call (the Graphify MCP server was not connected).
  - The 5-hour web quota was reached once during the source search; work resumed in the same session and context.
- **Planning rounds.**
  1. The native plan, v1 (559 lines, SHA-256 `05ff2c7f0c18bd7518382aa7278bd9951a850497f6ddd1f9e12d227976065d8d`, as
     recorded by Codex), drew a Codex review with five corrections:
     - ρ = 0 and degeneracy;
     - priors and amplitude conventions;
     - the SPLL moment criterion;
     - the D6 support condition;
     - sequential-guarantee wording and quotation limits.
  2. Revision 1 integrated them (final native SHA-256 `352e4be46f14f1b35c471bbccb974a9bfac8897f5228eafe6dd69ec9c3971883`,
     as recorded by Codex).
  3. Codex then consolidated the plan. Its corrections: P3-C keeps PC1, block dimensions, delay approximations, and a
     paraphrased audit. The GO followed.
- **Execution reviews.**
  1. Codex compaction:
     - at most 25 verbatim words and about 200 words of paraphrase per article;
     - one short summary per article, with no repetition across Sections 5.2–5.5;
     - the absence of time series limited to the static AUC comparisons, not the 2014 video example.
  2. Independent review:
     - the assumptions of M made explicit in Section 3: i.i.d. Gaussian whitened observations under the alternative,
       I(S) = ‖θ_S‖²/2 and matched prior s² = 2I(S)/d, with M not directly applicable to P3-C sign streams;
     - "any rotation" in the KF14 propositions too strong, so the propositions' detail was removed.
  3. Codex reception: no further substantive change requested.

## Validated Results

- **Note.** `docs/audits/stream_19_theory_spll_20261107.md`, 440 lines, SHA-256
  `5f1d3ef11a91f05c314f520e80fee31b1cf0f3e9891b13c0bd2008552188b1fb`, received by Codex. Statements carry the tags
  [D] documented, [A] algebraic under stated assumptions and [H] hypothesis or open item.
  - **N, k and d.** N, k, d, p, D, K_MP and m are defined. No universal N/d/k ratio exists; the ratios actually defined
    are listed. The sealed full run fixes N = 239 and yields no slope in N.
  - **Code facts, read as text.**
    - P3-C defaults to `channels="all"`, so it monitors K_MP + 1 coordinates (factor mode) or N (full mode), PC1
      included. E1 arm B keeps that default.
    - The default reading is an equal-weight dictionary of per-direction e-detectors.
    - The mixture variant averages a market dictionary and a residual mixture, with weights proportional to the column
      counts.
    - The F3 drift lies exactly along column 0.
  - **Oracle.** G(N) = N/deff_N. The equality case of the data-processing inequality gives: projections containing 1
    keep I_N, and projections explicitly inside 1^⊥ carry zero information, including at ρ = 0. An arbitrary or
    estimated PCA residual need not be that declared subspace; its retention is not established here. Edge cases are listed.
  - **Fluid criterion.** G·r/M, with explicit assumptions on M. Amplitude conventions change the exponent a. Delay
    readings are kept apart: no ADD, ARL0 or FPR(H) follows from the oracle.
  - **SPLL audit.**
    - Kuncheva, IEEE TKDE 25(5):1175–1180, 2013, DOI 10.1109/TKDE.2011.226, is verified as the primary source.
    - Kuncheva and Faithfull, IEEE TNNLS 25(1):69–80, 2014, DOI 10.1109/TNNLS.2013.2248094, is the source of the folded
      variant and of the variance-share PCA rule.
    - `tail10` applies the same rule at 90 % to a different matrix: the Ledoit–Wolf calib covariance, unstandardized
      and fitted once.
    - Neither article gives a calibrated threshold or a sequential FPR(H)/ARL0 guarantee, and the χ² reference is not a
      calibration guarantee.
    - Parity holds iff the centres are symmetric. On a given panel, D6 sign randomness needs rows with d(x) ≠ d(−x).
    - The prerequisites before any port are listed.
- **Primary PDFs** (local copies, untracked):
  - TKDE: https://lucykuncheva.co.uk/papers/lktkde13a.pdf, 949,391 bytes, SHA-256
    `74acaba9eb8fdd1cd43dffdeafa37f872292ad2d05828aef6936c528adc6a052`;
  - KF14: https://lucykuncheva.co.uk/papers/lkwfTNNLS14.pdf, 1,458,935 bytes, SHA-256
    `52c776175d8e85c68066355bbeb4ad9d71d23bf3c822a46652d5409793797112`.
- **Documentary controls.** Shell only, in the ignored journal `logs/stream_19_plan/doc_checks.log`. The final run, at
  2026-11-07T13:42:00Z, gave 159 PASS and 0 FAIL:
  - C1, Git state: HEAD equal to the base, no tracked diff, nothing staged, and an untracked set made of the note and
    the two Codex files;
  - C2, Codex file hashes: plan `09d43bdb9478fc6536c478bebe679e3905d0eca9fa4340c61d7de3f63e946ccd`, GO
    `4cd71b0762b44a6a2faceec02751ebceaa406ae9206d35bcd4ec87c6f6cdeaca`;
  - C3, J1 on disk and in the index, with 47 CRLF, 47 LF in total and no bare LF;
  - C4, the E3 CSV and the four sealed PCA manifests;
  - C5, cited paths present, historical E4 deliverables and `configs/FROZEN.json` absent;
  - C6, line anchors in code, Section 3, the prompt, the schema, the manifest and the oracle note;
  - C7, archived numbers;
  - C8, PDF hashes, quotations, summary word counts, M assumptions, the video clarification, and the absence of
    "any rotation";
  - C9, no home path and no banned wording.
- **Word budget.**
  - Verbatim words: 20 per article.
  - Paraphrase in the summaries: 103 words for TKDE and 96 for KF14.
  - Paraphrase elsewhere: 85 and 79 words, by a manual tally recorded in the journal. That tally counts shared
    statements once for each article and excludes derivations, code facts and labels.
  - Totals: about 188 and 175 words.

## Errors and Dead Ends

- **Native-plan overstatements, corrected in the Codex review.**
  - Zero information was attributed to residuals and tails for every ρ. This is wrong at ρ = 0 and for estimated bases.
  - m/(N−1) was presented as an exact retention, whereas it is a ratio of expectations.
  - "Flat bulk, so no tail advantage" ignores drifts concentrated in the chosen tail.
  - Exponents were stated without an amplitude convention: the pool has a = 0 at ρ > 0 but a = 1 at ρ = 0, and
    total-norm and per-asset conventions differ.
  - An inequality between standardized shifts was read as power superiority.
  - D6 randomness was asserted without a support condition.
  - "No FPR" was written where "no sequential FPR(H)/ARL0 guarantee" is meant.
  - Verbatim quotation was excessive.
- **Dimension error.** The native plan described P3-C full as a detector of N − 1 residual coordinates. The code keeps
  PC1 through `channels="all"`; the consolidated plan corrected this.
- **KF14 propositions.** "Any rotation" was too strong: in eq. 23 the factor a(1−a), with a = sin²θ, vanishes at θ = 0
  or π/2. The detail was removed rather than developed.
- **Controls.**
  - Run 1 (13:26:44Z) gave 1 FAIL. A quotation wrapped across two lines while the check read single lines. Quotations
    now sit on one line and the check reads line-joined text.
  - Run 2 (13:39:32Z) gave 0 FAIL, but the manual tally put KF14 near the 200-word limit. Restatements in the table and
    in Section 5.5 were replaced by item references.
  - Run 3 (13:42:00Z) gave 0 FAIL.
- **Plan mode.** Codex rejected ExitPlanMode twice with review messages before recording the GO, as the workflow
  provides.

## Current State

- **Pre-commit state.**
  - Branch `stream-19-plan`, HEAD `1440927b49463c13bdd0c819fcd73f30d6a32c31` (the base).
  - Nothing is staged and no tracked file is modified, as last checked by C1 at 13:42:00Z. No Git command was run
    after that.
- **Expected `git status --porcelain`**, exactly:

```text
?? docs/audits/stream_19_theory_spll_20261107.md
?? prompts/GO-stream-19-plan.md
?? prompts/plans/plan-19-plan.md
?? prompts/wrapups/wrapup-19-plan.md
```

- **Ignored journal.** `logs/stream_19_plan/doc_checks.log`.
- **Not yet done.** Codex runs these after this wrapup, in this order:
  1. the AST-only reindexation without AI summaries (`tools/reindex_graphify_jcodemunch.sh`);
  2. `make check`;
  3. commit;
  4. fetch and rebase;
  5. the pushed-range check;
  6. push, under user confirmation.

  None of these has been run.
- **Preserved.**
  - J1: `results/e2/e2_cells.csv` keeps SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` on
    disk and in the index, with 47 CRLF and no bare LF.
  - E3: `results/e3/e3_overshoot.csv` keeps SHA-256
    `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`. D8 stays FAIL at +5.2833 % and was not
    re-examined.
  - The four sealed PCA manifests are unchanged.
- **Excluded.**
  - No scientific code, test, simulation, computation or real data.
  - No row dated 2020 or later, no FROZEN or J4 step, no JEPA/VAE training, no PCA rerun.
  - No change to the plan, the GO, code, the paper, configurations, dependencies or memory. No change to the received
    note.
- **Environment.**
  - Linux 5.14.0-570.55.1.el9_6.x86_64.
  - Only shell tools ran: read-only `git`, `rg`, `grep`, `sed -n`, `tr`, `wc`, `sha256sum`, `test`, `mkdir`, `tee` and
    `date`. The project interpreter `.venv/bin/python` (Python 3.12.9) was not invoked.
  - The native plan `~/.claude/plans/pasted-content-id-f9d7-cadrage-merry-cocke.md` had its §14 updated with the GO;
    its hash therefore differs from `352e4be4…`.
  - The PDF copies sit in the session's tool-results cache under `~/.claude/projects/`.

## Vigilance Points

- **Documentary only.** [A] statements hold under their stated assumptions and [H] items stay open. There is no
  measured result and no ADD, ARL0 or FPR(H).
- **Word budget.** Compliance relies on the counting convention stated in the journal.
- **PDF values.** The implementing session checked them by reading page images; it did not extract PDF text.
  A re-download must reproduce the recorded SHA-256 before reuse.
- **Open before any SPLL port.**
  - The author's code was not read, and cloning or execution is excluded.
  - The common-covariance estimator and the handling of a singular S are unspecified.
  - Errata were not checked.
  - The c-means variant of KF14 is unspecified.
  - No D6 calibration is established.
- **E1 arm B.** Its archived P3-C full monitored N coordinates, PC1 included. Older wordings that describe it as
  residual-only should be read accordingly. Nothing was rerun or compared.

## Recommendations

- **Codex closeout.**
  1. Recompute the note SHA-256 (`5f1d3ef1…b1fb`) and this wrapup's SHA-256, reported in the session.
  2. Stage exactly the four untracked paths listed under Current State.
  3. Run the closing sequence of Current State. A suitable commit message is
     `docs(stream-19): record N/k/d theory note and SPLL source audit`.
- **Future lots.**
  - Decide whether to declare a non-degenerate spectral model before any analytic extension.
  - A coded extension needs its own plan and GO, and an exclusive slot for `floors` and `pipelines`.
  - Any SPLL port first settles the prerequisites of the note's Section 5.7.
  - D5 or D6 campaigns need a scientific authorization.
- **[Strategic Advice].** Before planning any E4 slope, fix the amplitude convention, per asset or total norm. It sets
  the exponent a of every predicted law; without it, measured and predicted slopes are not comparable.
