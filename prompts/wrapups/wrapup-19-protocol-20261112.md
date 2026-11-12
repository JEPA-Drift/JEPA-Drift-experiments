# Wrapup — stream 19-protocol-20261112 (documentary E4 protocol proposal)

## Context

- Mandate `logs/stream_19_protocol/mission-plan.md`, a documentary mission on stream 19. It was PLAN ONLY first, then
  drafting under a delegated documentary GO. No scientific GO was given, and none of the work below is an experiment.
- Session: `jepa-s19-protocol-20261112`, UUID `0a586401-6f3b-49b0-8900-d4f7cdff4a09`. Model Claude Opus 5.5 at effort max,
  without Agent/Task. Branch `stream-19-protocol-20261112`, worktree base `891cfa5f56c8ec20988f9a18efef4ed468e1c720`.
- Sequence:
  1. Native plan v0 and documentary NO-GO.
  2. Native plan v1, then the canonical French plan and the separate documentary GO.
  3. Official plan exit; Codex verified the mode and sent the drafting signal.
  4. English protocol drafted.
  5. Independent Codex review, with one editorial correction.
  6. Reception, then a closing slot allocated to stream 19.
- Codex owns the plan, GO, NO-GO, continuation inventory, Git, reindexation and full checks. This session wrote only the
  protocol, its ignored journal and this wrapup.

## Validated Results

- **Protocol**, received by Codex's independent review: `docs/audits/stream_19_protocol_proposal_20261112.md`, 249 lines,
  SHA-256 `602e7abcc50ac671464eb7323f578b1bdd8f002a5e04020e073b2c3764831e19`.
  - It states one PROPOSED synthetic question: whether, at fixed population Gaussian information I*, the restricted delay
    of the ex ante full spectral dictionary changes with N while the direction oracle O-dir stays invariant in law.
  - Setting: Gaussian equicorrelated model with ρ = 0.4, plus a t7 sensitivity whose I* is a two-moment Gaussian proxy.
    The drift is residual, Δμ ⊥ 1, with an isotropic direction; its identifier `SYNTH_RESIDUAL_ISOTROPIC_FIXED_INFO` is
    PROPOSED.
  - Operational null: β_Δ = 0 over a grid fixed before any draw. Δ = Δ_1 + Δ_2 is an accounting identity only.
  - Methods: EW, SPEC-prefix8, SPEC-full and P3-CS(b) full as ex ante methods; O-dir and O-score1 as oracles.
  - The rest is specification only, and every choice is PROPOSED or OPEN: roles and a key recipe; readings and decision
    labels; sizes and resources; a cost-only pilot; witnesses (a)–(h) for a future RED→GREEN lot.
- **Journal** (ignored): `logs/stream_19_protocol/protocol-journal-20261112.md`, SHA-256
  `4e7d999ec93b9edab9279a2fd3c5f5268f9f24cd6b98ae4c302d895597de2c3a` before this wrapup. It records the hashes,
  controls and reception.
- **Code facts, read-only.**
  - The dictionary e-detector is bilateral: `SIDES = [1, -1]`, `EDETECTOR_ETA0 = (0.05, 0.10, 0.15, 0.20)` (`eprocess.py`).
  - `pca_directions` in factor mode refuses K_MP = 0 (`pca.py:55-59`).
  - P2-C is a mean of signs and P7 a Gaussian LLR (Codex NO-GO, `pipelines.py:242-247` and `pipelines.py:435-448`).
- **Hashes at closeout, unchanged since before drafting.**
  - Canonical plan `37c2f8ade0f6eb667c3fc34f12987c122f6fb20f85ef15a89e27552ae742f60a`.
  - GO `60d001c6867293f3b12efd2d5266bf41b72af5531ba26379d4a63062913421aa`.
  - NO-GO `307aadd40403d3919fb7e2c51eb2e879fd9237e03496101df75125f63f34a998`.
  - E2 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`.
  - E3 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`.
  - PCA full manifest `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`.
- **Continuation inventory.** The protocol embeds its pre-drafting snapshot
  `b5cbaf864a597b11641d0df31afa9e30ad45c46374efeaf1f41ae844d49476e2`. Codex alone updated the inventory after reception; its
  current SHA-256 is `425b5ea99d0883c6541034121ecf6a34c1d5d6d94bd54c0ecb6c0b85439664c0`. The two values are not an
  inconsistency.
- **Drafting budget.** Codex sent the drafting signal at 13:07:42 UTC, and REVIEW_READY was given at 13:14, inside the
  20-minute bound (inventory). The editorial correction was controlled at 13:35:54Z.
- **Controls observed** (shell only):
  - final protocol: `wc -l` 249 (≤ 250), 11 sections, no APPROVED/proves/validates, no French letters, no absolute path;
  - during drafting, read-only Git with `GIT_OPTIONAL_LOCKS=0`: `diff --quiet HEAD` exit 0, `diff --name-only HEAD` empty;
  - no Git after the review, as instructed.

## Errors and Dead Ends

- **Generation incident, plan phase** (Codex records, API metadata; cause not established).
  - Output reached `max_tokens` at 128,000 tokens at 12:16 UTC.
  - A second response used 126,682 output tokens before the 178-line native plan v0 was written at 12:35 UTC (SHA-256
    `c8829ca27920a55ea5485050909536d430ff5be054e0fbab4306f37b86f13efc`).
  - Codex interrupted the generation, and later the first ExitPlanMode attempt. Session, model, effort and context were
    preserved.
- **Initial documentary NO-GO** on v0, with seven corrections:
  1. e-detectors use the horizon bound H/γ, not Ville's inequality; the rank guarantee is marginal, and a stochastic Wilson
     excess is not a defect;
  2. no N may be selected after observation; slopes use the fixed grid;
  3. marginal J_k and the best channel a_best replace `a_pop`; a prefix uses its projected joint KL;
  4. log contrasts are accounting identities, not causal effects;
  5. P3-CS(b) stakes and b̂ removal stated; P2-C and P7 not aliased;
  6. at N = 1 the residual methods are refused; no F2 label; synthetic N = 500 needs no data;
  7. no extraction of the sealed rank rule; power and cost unknown until a pilot.

  Native v1 (177 lines, SHA-256 `5be1de942a507b926932f60b9e5e4bc62468e931d74e65f29fbb36e254df495b`) applied them; the GO's
  eight integrated clarifications prevail.
- **Protocol size control** failed twice: 328, then 254 lines, against a limit of 250. A layout compaction and six targeted
  Edits brought it to 248 lines. That makes two corrections of one defect, under the limit of three.
- **Quoted French section title** in the first draft, replaced before the language check.
- **Codex review correction.** "u_N is nested in N" was imprecise. The u_N are coupled across N through the same Gaussian
  prefixes g_{1:N}, then projected and normalized separately in each dimension; they are not identical normalized vector
  prefixes. No formula or scientific choice changed.
- **`eigh_desc` not read**, given the bounded budget, so the eigenvalue tie rule of the fitted basis stays OPEN.

## Current State

- **Worktree:** still at the historical base `891cfa5`. Untracked files:
  - this session's deliverables: the protocol and this wrapup;
  - Codex files: plan, GO, NO-GO and continuation inventory.

  Nothing is committed by this session.
- **Published main:** `f1eb4e837704957c7d5c39d585125f9413407887`, the stream-21 documentary commit, verified by Codex.
  - Codex's fresh full check for stream 21: 1,193 passed, 5 skipped (D4 availability) and 0 failed, in 36.68 s + 495.73 s;
    prompts-check 33/33.
  - This is Codex's measurement for stream 21. It is not a test run by this session or within stream 19.
- **Remaining, NOT executed:**
  1. exit of this CLI;
  2. Codex fast-forwards branch 19 onto the documentary main;
  3. AST reindexation and a fresh mandatory full check;
  4. range audit, commit and publication, all by Codex.
- **Scientific status:** every choice remains PROPOSED or OPEN, with no researcher GO. There was no E4/SPLL code, pilot,
  simulation, data access, J4/FROZEN or model training. Stream 19 remains PARTIEL.
- **Environment, as reported by the Codex inventory and not re-measured here:** Python 3.12.9, NumPy 2.4.4, SciPy 1.17.1,
  pandas 3.0.6, PyYAML 6.0.3, pytest 9.1.1, torch 2.14.1 (conda-forge bridge).

## Vigilance Points

- **Guarantee limits.**
  - The rank-rule guarantee is marginal over calibration; a realized threshold may have a conditional FPR above α.
  - Wilson and paired-bootstrap intervals are conditional on the shared fit and calibration.
  - The anytime-valid reading is a horizon bound P∞(alarm before H) ≤ H/γ_H, not Ville's inequality.
  - RMST(H) is a restricted mean, not a Lorden ADD. Slopes are local and are not `cor:scaling` exponents.
  - Under t7, I* is a Gaussian proxy, never a t7 KL.
- **OPEN points:**
  - calibration sharing among the scalar sign-stream methods (EW, O-dir, O-score1);
  - the eigenvalue tie rule;
  - every PROPOSED default in protocol §10: amplitude convention, primary reading, I* rule, grid, sizes, censoring
    qualification, CPU cap, t7 scope, identifier adoption, outer resampling.
- **No aliases:** EW is not P2-C, and O-dir is not P7. P3-CS(b) is exactly blind to the true market only if b̂ ∥ 1.
- **Sealed artifacts:** the sealed rank rule must not be extracted or modified by a documentary lot. Any reuse must preserve
  its hashes and the 44 PCA contracts.
- **Inventory hash:** the hash `b5cbaf86…` in the protocol's §11 is a historical snapshot and must not be "corrected".
- **Check duration:** the Codex-reported full check takes 532.41 s, above the repository's five-minute target. No test or
  criterion was changed to shorten it.

## Recommendations

- **Researcher:** decide the protocol's §10 choices, or keep them OPEN, before any code lot. A scientific GO is required for
  any E4 implementation, cost pilot, simulation or campaign.
- **Codex:** finish the stream-19 closeout in order: fast-forward onto `f1eb4e8`, AST reindexation, full check, range audit,
  commit and push under the repository policy. Report only the totals actually observed.
- **Future code lot:**
  - write a separate plan;
  - write witnesses (a)–(h) first and observe them RED on fake fixtures;
  - reuse the registry only for P3-C full and P3-CS(b) full, and define EW and O-dir by formula;
  - run a cost-only pilot in the disjoint `pilot` seed domain before any scientific draw;
  - add a `C-<topic>` entry if the drift identifier is adopted.
