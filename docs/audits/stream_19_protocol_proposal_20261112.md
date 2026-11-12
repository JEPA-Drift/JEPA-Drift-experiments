# Stream 19 protocol proposal — fixed-information N scan of an ex ante spectral dictionary, 2026-11-12

**Status: PROPOSED prospective protocol, not an E4 result.** Written under the delegated documentary GO
`prompts/GO-stream-19-protocol-20261112.md` for the canonical plan `prompts/plans/plan-19-protocol-20261112.md`, whose eight
integrated-GO clarifications prevail. Every scientific default below is PROPOSED for the researcher's separate scientific GO; a
point without a complete recipe is OPEN. Nothing here was simulated, computed, implemented or tested. Labels: [D] documented in
a cited source; [A] algebraic consequence, stated without computation; [H] hypothesis.

## 1. Scope

- Synthetic Monte Carlo only. The lot reads no data file: no D6, no real or private returns, nothing dated 2020 or later, no
  JEPA/VAE or trained model. A synthetic null certifies its own model only (C-P4D-null-insample) [D].
- Prior evidence, cited and not re-audited [D]. E1 arm B (stream 12) already reports slopes in N, with injected information
  and alignment diagnostics, on retrospective D6 panels at per-asset amplitude (`docs/audits/stream_19_replan_2026_11_06.md`,
  F2–F3). The sealed PCA benchmark compares k and d at N = 239 and yields no law in N (same audit, F1). The analytic oracle
  `docs/sections/e4_oracle_reference.md` gives the market-drift information I_N and holds no detector, delay, ARL0 or FPR.
- New object: a controlled synthetic comparison at fixed population Gaussian information. It does not claim to be the first
  analysis of N, information or alignment, nor a general separation of these quantities.
- SPLL/P3-KF is omitted: its choices remain unresolved (theory note `docs/audits/stream_19_theory_spll_20261107.md`, §5.7) [D].

## 2. Question and operational null (PROPOSED)

**Q.** In a Gaussian equicorrelated background, with a residual mean drift Δμ ⊥ 1 of isotropic direction in 1^⊥ and the same
daily Gaussian information I* for every N, does the restricted delay of the ex ante full spectral dictionary change with N
while the direction oracle O-dir stays invariant in law, and how does that change co-vary with the measured best channel?

- Operational null H0_op: β_Δ = 0, where β_Δ is the OLS slope on log N, over the fixed grid of Section 3, of
  Δ(N) = log RMST_H(SPEC-full) − log RMST_H(O-dir). H0_op is rejected when the paired 95 % bootstrap interval excludes 0.
- Scope of a rejection: it refutes H0_op under these choices (background, amplitude rule, fit, reading, grid) only. It says
  nothing about a general equivalence between information and delay, and β_Δ is not an exponent of `cor:scaling`.
- Pre-declared accounting identity: Δ = Δ_1 + Δ_2, with Δ_1 = log RMST_H(O-score1) − log RMST_H(O-dir) and
  Δ_2 = log RMST_H(SPEC-full) − log RMST_H(O-score1). Δ_1 and Δ_2 are not identified pure effects of alignment or dimension:
  alignment, basis estimation (N/T and the Ledoit–Wolf fit vary with N) and calibration are not causally separated.
- Choice among the G1 candidates (replanning audit, F7). F1 saturation concerns market information, already given by the oracle
  (G(N) → 1/ρ) [D]. D4 needs real data, whereas a synthetic N = 500 needs none and belongs to the proposed grid. P3-KF is
  omitted. The dictionary forecast against a measured slope is the candidate testable on synthetic data alone; the answer would
  fix a non-concentrated ex ante reference for a future learned representation.

## 3. Model (PROPOSED)

- Covariance Σ_N = ρ11ᵀ + (1 − ρ)I_N with ρ = 0.4, the value of the oracle and of the sealed benchmark [D]; i.i.d. days.
- Gaussian background: x_t = √ρ f_t 1 + √(1 − ρ) ε_t (+ Δμ on alternatives), (f_t, ε_t) ~ N(0, I_{1+N_max}). Keeping the
  first N columns gives exactly Σ_N [A].
- t7 sensitivity: the same innovations multiplied by one shared per-day factor s_t = √(5/χ²_7,t), of unit variance [A]. This
  is the shared-χ² construction of the sealed manifest (`docs/sections/pca_drift_benchmark.md`, §4) [D]. Under t7, I* is a
  two-moment Gaussian proxy, labelled INFO_GAUSS_PROXY_T7, never a t7 KL.
- Drift classes, by projection on the eigenspaces of Σ_N: market, Δμ ∈ span(1), with I_N bounded in N for ρ > 0 [D] and the
  EW index as its likelihood-ratio direction [A]; factor, identical to market in this one-factor model; residual, Δμ ⊥ 1, the
  primary class; mixed, whose Gaussian information splits exactly between the two parts since Σ_N⁻¹1 ∝ 1 [A]. Only the
  residual class enters the minimal lot.
- Residual drift: u_N = P g_{1:N} / ‖P g_{1:N}‖, with P the projector on 1^⊥ in R^N and g ~ N(0, I_{N_max}) drawn once per
  alternative replicate. The u_N are coupled across N through the same Gaussian prefixes g_{1:N}, then projected and
  normalized separately in each dimension; they are not identical normalized vector prefixes. Each u_N is uniform on the unit
  sphere of 1^⊥ [A]. Δμ = c u_N with c = √(2(1 − ρ) I*); since u_N is an eigenvector of Σ_N, the Gaussian information is
  exactly I* [A]. The drift is present from day 1 and is injected in return space. Descriptive identifier, PROPOSED: `SYNTH_RESIDUAL_ISOTROPIC_FIXED_INFO`; it is not F2, and its
  adoption is reserved to the scientific GO.
- Amplitude: fixed information, the restriction to 1^⊥ of the fixed total-norm budget of the theory note, §3.1 [D]. I* is set
  analytically, before any draw, by ln(γ_H)/I* = H/40, and is never adjusted on test or pilot effects. The historical
  convention (b) (C-inject-conv-b) is unchanged. For this residual family in this model it would give I ∝ N [A]; that
  statement does not extend to other families or models, and no universal amplitude law is declared. Leaving convention (b)
  is a proposal to the researcher.
- Grid, fixed before any scientific draw: N ∈ {8, 16, 32, 64, 128, 239, 500}. N = 500 depends on the cost-only pilot only
  (Section 8). N = 1 and N = 2 appear only in code witnesses.
- Fixed k and d: spectral prefix k = d = 8, the smallest N; full dictionary d = N, which varies by definition; O-score1 has a
  reservoir of all N axes and d = 1.
- Fit: T_fit = 2000 drift-free rows per background. One Ledoit–Wolf basis per (background, N), fitted on the first N columns of
  those rows, then frozen. N/T and the fitted basis vary with N; both are declared nuisances, and the PC1 leakage
  (v̂_1ᵀ1)²/N is recorded.
- Horizon and level: H = 2000, α = 0.05, γ_H = H/α (prompt 19 [D]; `pipelines.horizon_gamma`).

## 4. Methods (PROPOSED)

EW, SPEC-* and O-* feed exact sign streams b_t = 1{wᵀx_t > 0} (ties broken by fair coins, `exact_sign_stream`), passed as
2b − 1, to the existing bilateral CUSUM e-detector [D]. Its bets are λ = 2·side·η₀, with SIDES = [1, −1] and
EDETECTOR_ETA0 = (0.05, 0.10, 0.15, 0.20). A dictionary is the equal-weight average of the per-direction e-detectors
(`eprocess.log_dictionary_edetector`). The statistic is therefore invariant to the sign of each axis [A]. P3-CS(b) keeps its
own predictable stakes (C-P3CS-design), so the methods differ by more than direction and dimension.

| Method | Class | Fixed before day 1 | Monitored dimension |
|---|---|---|---|
| EW | ex ante | w = 1/√N; defined here, distinct from P2-C (a mean of signs, `pipelines.py:242-247`) | 1 |
| SPEC-prefix8 | ex ante | axes 1..8 of the fit basis, by decreasing variance | 8 |
| SPEC-full | ex ante | P3-C with `mode="full"`, all N axes including PC1 | N |
| P3-CS(b) full | ex ante | registry defaults except `mode="full"`; the fitted b̂ (PC1) is removed | N − 1 directions × stakes |
| O-dir | oracle | w = u_N, the injected direction; defined here, distinct from P7 (a Gaussian LLR, `pipelines.py:435-448`) | 1 |
| O-score1 | oracle | the fit-basis axis k* that maximizes J_k (below), computed from Δμ and the true Σ_N | 1 |

- EW is exactly blind to any translation orthogonal to 1 [A]: a negative control for the residual class.
- P3-CS(b) removes the estimated b̂, so it is exactly blind to the true market direction only when b̂ ∥ 1 [A]. Its registry
  default `mode="factor"` refuses K_MP = 0 (`jepadrift/representations/pca.py:55-59`) [D]; K_MP = 0 is expected in a
  one-factor model [H], hence `mode="full"`.
- Oracle diagnostics, recorded per trial and labelled ORACLE_*:
  - I*, and the closed-form sign-stream information of O-dir;
  - J_k = (v̂_kᵀΔμ)²/(2 v̂_kᵀΣ_N v̂_k), and the best channel a_best = max_k J_k / I*;
  - prefix retention: its projected joint Gaussian KL divided by I*. Empirical PCA coordinates are not independent under Σ_N,
    so Σ_k J_k is not I*, and a prefix retention is never a sum of J_k;
  - the glossary a_max (plug-in whitening), a separate model diagnostic; K_MP; the PC1 leakage;
  - `floors.dictionary_multiplier(n_atoms, gamma, cos2)`, as a descriptive fluid column outside every verdict.
- Timing of oracle inputs: u_N is fixed by the direction draw before the alternative path exists; k* is fixed before day 1
  from the frozen basis, Δμ and Σ_N. Neither input uses data from the monitored path.
- Information forbidden for any ex ante choice: the hidden evaluation drift, future alternatives, calibration outcomes and
  holdout outcomes. The selector-development role is empty. A non-oracle learned PCA selection is a separate future stream,
  never part of stream 19.

## 5. Roles, seeds, pairing, workers (PROPOSED recipe, not executed)

- Roles: `fit` (T_fit rows); `calibration` (n_cal null paths); `holdout` (n_hold null paths, untouched until the thresholds
  are frozen); `alternative` (n_alt drift paths). There is no centering role, since the drift is a mean drift. No two roles
  share an entropy.
- Keys follow the sealed seed-plan pattern (`docs/sections/pca_drift_benchmark.md`, §2) [D].
  - `[19, seed, crc32(domain), crc32(role), replicate]` serves three domains. `innov` holds the (1 + N_max)-dimensional normal
    innovations of a path, drawn once and shared by both backgrounds; this is a declared pairing, not a claim of
    independence. `chi2_t7` holds the per-day χ²_7 factor, for the t7 background only. `coins` holds the tie-breaking coins
    of the exact sign streams.
  - `[19, seed, crc32("direction"), replicate]` draws g, shared, as declared, across N and across backgrounds.
  - `boot` and `pilot` use their own domains; a `pilot` key never coincides with a scientific key.
- Checks before any draw, as in the sealed benchmark [D]: the CRC32 codes of the run vocabulary are pairwise distinct, and
  the canonical entropies (zero-padded uint32 words) are unique. No call presented as independent reuses an entropy to force
  a pairing.
- Paths are drawn at N_max and truncated to their first N columns, so trials are paired across N, methods and backgrounds.
  Outputs must be byte-identical for any `--jobs` and any replicate processing order.

## 6. Readings and metrics (PROPOSED)

- Primary reading, a proposal to the researcher: for each (method, N, background) cell, the threshold is the
  `predictive_exchangeable_rank_v2` order statistic of the n_cal calibration maxima of the log e-detector [D]. Its guarantee
  is marginal over the calibration sample; a realized threshold can have a conditional FPR above α. This lot does not
  extract, relocate or modify the sealed rule; a future reuse must preserve its hashes and the 44 sealed contracts.
- Calibration sharing, OPEN. Under any centrally symmetric null, an exact sign stream whose direction is fixed before the
  path, and independently of it, is i.i.d. Bernoulli(1/2) (Lemma 2, `CLAUDE.md` glossary) [D]. EW, O-dir and O-score1 would
  then share one null law across N and backgrounds [A], and a single calibration could serve all three. Whether to share it
  or to calibrate each cell separately is OPEN for the scientific GO; the oracle's name alone licenses no reuse. Dictionaries
  (SPEC-prefix8, SPEC-full, P3-CS(b)) are calibrated per cell: their joint null law depends on the fitted basis.
- Secondary reading, anytime-valid at horizon: the alarm fires when the e-detector reaches γ_H, and
  P∞(alarm before H) ≤ H/γ_H = α (`CLAUDE.md` glossary) [D]. This is a horizon bound, not Ville's inequality.
- Equal nominal α does not establish equal attained FPR. [H] Under the anytime-valid reading, the attained FPR of an
  equal-weight dictionary may drift with N and bias a slope.
- Metrics:
  - the delay counts monitored days up to and including the alarm: first_hit (C-pipe-delay) [D];
  - censored time min(T, H); RMST(H) is the mean censored time; detection rate = alarms/n_alt; FPR(H) = holdout
    alarms/n_hold;
  - per-cell intervals: Wilson for rates; normal for RMST, with deff = 1 across independent paths;
  - contrasts and slopes: paired percentile bootstrap over alternative replicates (B_boot draws), resampled jointly across N
    and methods. No independence is assumed between N values or between methods.
- Conditional uncertainty: fit and calibration are shared by all paths of a cell. Wilson intervals and the paired bootstrap are
  therefore conditional on them and omit their estimation variability. No conclusion about the ensemble of fits follows; an
  outer resampling level would be a separate scientific and budget decision.
- Five objects kept apart: the evidence budget ln(γ)/I, used for the amplitude rule only; the anytime-valid horizon bound;
  ARL0, not estimated; the diffusion approximation Φ(γI)/I, not used; RMST(H), a restricted mean, never a Lorden ADD.

## 7. Analysis and decision labels (PROPOSED)

- Every cell is kept and reported. r < 0 gives CALIBRATION_FAILED (deterministic sealed rule) [D].
- FPR_ABOVE_NOMINAL labels a holdout FPR whose Wilson lower bound exceeds α. It is a diagnostic, conditional on the fit and
  the calibration. It is not evidence of a violation or of a code defect, and it triggers no automatic scientific STOP. Only a
  deterministic integrity failure (a Section 9 witness, a hash or an identity mismatch) is a STOP.
- FPR comparability: "comparable attained FPR" holds only when the paired 95 % interval of the holdout-FPR difference lies
  within ±0.01 (precedent C-e1-readings) [D]; otherwise the contrast is labelled "common nominal α only". This is a label,
  never an exclusion; slopes keep the conditional qualification of Section 6 when comparability fails.
- Grid and censoring: slopes are descriptive and use the whole grid fixed in Section 3; no N is chosen after observation, and
  no subset is selected by detection rate. PROPOSED low-censoring qualification: the Wilson lower bound of the detection rate
  is ≥ 0.95 for each method of the contrast at every N of the grid. Otherwise the slope is NOT_IDENTIFIED for the intended
  interpretation, and its value is still reported. A slope of restricted means is local, never an exponent.
- Primary labels for β_Δ: COST_GROWS (interval above 0), NO_GROWTH_DETECTED (interval contains 0), COST_SHRINKS (interval
  below 0), NOT_IDENTIFIED (censoring qualification fails). Δ_1 and Δ_2 are reported with intervals as accounting terms, with
  no verdict and no causal attribution.
- Integrity warnings, which are not results: a non-zero O-dir slope, since the O-dir law is invariant in N [A]; an EW
  detection rate departing from its own holdout FPR under the residual class.

## 8. Sample sizes, resources, cost-only pilot (PROPOSED)

- n_cal = n_hold = n_alt = 2000 per background (sealed-benchmark precedent [D]); T_fit = 2000; B_boot = 2000; seed 42.
- Power, feasibility, runtime and cost are UNKNOWN until an authorized pilot, as is whether the ±0.01 margin can be met at
  n_hold = 2000. No campaign is added now to settle these points.
- Resource bounds: RAM ≤ 8 GiB; ≤ 30 min per invocation, with resumable partitions (sealed pattern) [D]; a PROPOSED total cap
  of 24 CPU-hours. An overrun is BLOCKED_RESOURCE, never an approximation.
- Cost-only pilot, run before any scientific draw: 40 replicates per role, in the disjoint `pilot` domain. It records wall
  time and peak RSS only, and writes or reads no delay, FPR or detection rate; its linear projection is an ESTIMATE.
- Fallbacks fixed now, in order: (1) drop N = 500; (2) run t7 on N ∈ {8, 64, 239} only; (3) STOP and return to the
  researcher. The pilot changes neither I*, H, thresholds nor methods; the grid changes only through these fallbacks.

## 9. Acceptance witnesses and TDD order for a future code lot (specification only)

A separate code plan and the researcher's scientific GO are required; nothing below is written or run.
- PROPOSED names: `experiments/e4_alignment.py`, `configs/e4_alignment.yaml`, `results/e4_alignment/`, `logs/e4_alignment/`, `tests/test_e4_alignment.py`.
- Reuse first: the registry, for P3-C full and P3-CS(b) full only; `eprocess`, `exact_sign_stream`, the Ledoit–Wolf PCA of
  `representations.pca` and `pipelines.save_fair_csv`; the sealed seed-plan, manifest and partition patterns. EW and O-dir
  are new formula-defined methods, never aliases of P2-C or P7. `jepadrift/monitors/` stays numpy-only.
- TDD order: each witness is written first and observed RED on small fake fixtures; the minimal implementation then turns it
  GREEN. `make check` stays under 5 minutes; the full check belongs to Codex.

Witnesses:
- (a) Finite dimensions. At N = 1 no non-zero residual direction exists, so the residual drift, the residual O-dir and
  P3-CS(b) are refused, and EW is a separate witness. N = 2 has a one-dimensional residual. k > N is refused.
- (b) Empty or invalid input, each refused explicitly: an empty grid; N non-integer, boolean or ≤ 0; I*, ρ, α or H
  non-finite or outside its domain; ν ≤ 2; n_cal below the rank-rule minimum, which is 19 at α = 0.05 [D].
- (c) No future access: changing x_{t+1..H} leaves every alarm ≤ t unchanged; stakes are predictable; no ex ante method
  receives the drift.
- (d) Stale source or hash: a mismatched config, code, environment, basis or calibration hash is refused; an output
  directory that already holds a manifest is refused; a partition with a different fingerprint is refused.
- (e) Independent roles: keys are distinct, a CRC32 collision raises, and calibration and holdout paths are disjoint.
- (f) Oracle labels: every O-dir, O-score1 or diagnostic row carries ORACLE_* and stays out of ex ante tables.
- (g) Seeds and workers: `--jobs 1` and `--jobs 3`, and a permuted replicate order, give byte-identical CSV; another seed
  changes the outputs.
- (h) Exact identities: nested truncation equals columns 1..N; with Δμ ⊥ 1, the EW stream equals its null stream on the same
  innovations; with a fixed basis, the paired t7 null gives the same sign streams as the Gaussian null [A]; first_hit,
  censoring and RMST match known alarm days; slopes use the fixed grid.

## 10. Exclusions and open choices

- Excluded from the minimal lot: the market and factor classes; D6, real or private data, anything dated 2020 or later and
  J4/FROZEN; SPLL/P3-KF, isotropic mixture detectors and non-oracle selection; JEPA/VAE; any change to sealed artifacts,
  DEVIATIONS, MAPPING or the paper.
- OPEN or PROPOSED, for the researcher (proposed default in brackets):
  1. amplitude convention [fixed information I*; leaving (b) is a proposal];
  2. primary reading [rank-calibrated, with anytime-valid as secondary];
  3. calibration sharing among the scalar sign-stream methods [OPEN];
  4. I* rule [ln(γ_H)/I* = H/40] and grid [historical; N = 500 gated by cost];
  5. sample sizes [2000 per role], and a larger n_hold if the ±0.01 margin must be conclusive;
  6. low-censoring qualification [Wilson ≥ 0.95 on the whole grid] and CPU cap [24 h];
  7. t7 sensitivity [same grid, secondary];
  8. adoption of `SYNTH_RESIDUAL_ISOTROPIC_FIXED_INFO`, and of a future C-<topic> entry for it;
  9. eigenvalue tie rule of the fitted basis [OPEN; `eigh_desc` not read]; the eigenvector sign does not affect bilateral
     statistics [A];
  10. an outer resampling level over fits [not proposed; a separate decision].

## 11. Documentary controls and hashes

Only read-only checks are used: `sha256sum`, `wc` and `grep`; `find -newer`, which is complementary only, since it cannot
detect a deletion or a restored date; Git with `GIT_OPTIONAL_LOCKS=0` (`status --porcelain`, `diff --quiet HEAD`,
`diff --name-only HEAD`). The observed outcomes are in the ignored journal `logs/stream_19_protocol/protocol-journal-20261112.md`.
A zero exit status of a counting command is not a PASS when a check fails. SHA-256 before drafting:

| Document | SHA-256 |
|---|---|
| `prompts/plans/plan-19-protocol-20261112.md` | `37c2f8ade0f6eb667c3fc34f12987c122f6fb20f85ef15a89e27552ae742f60a` |
| `prompts/GO-stream-19-protocol-20261112.md` | `60d001c6867293f3b12efd2d5266bf41b72af5531ba26379d4a63062913421aa` |
| `prompts/NO-GO-stream-19-protocol-20261112.md` | `307aadd40403d3919fb7e2c51eb2e879fd9237e03496101df75125f63f34a998` |
| `docs/audits/streams_01_31_continuation_2026_11_12.md` | `b5cbaf864a597b11641d0df31afa9e30ad45c46374efeaf1f41ae844d49476e2` |
| `docs/audits/stream_19_replan_2026_11_06.md` | `eac783b195f25cbb77265b7d2f392dca1802c53421380dacbd63fc14cef7cf71` |
| `docs/audits/stream_19_theory_spll_20261107.md` | `5f1d3ef11a91f05c314f520e80fee31b1cf0f3e9891b13c0bd2008552188b1fb` |
| `docs/sections/e4_oracle_reference.md` | `4dca48c45236650793f745e82d82a8d7ce29fef8df45d565e5f7edfac1759270` |
| `docs/sections/pca_drift_benchmark.md` | `adae1ad1d068830a6eb7b69e6266ac99f2a9f7940099469ab44dc8d2938d9484` |
| `docs/DEVIATIONS.md` | `2c83037fda35f406a5660c9e33e7f50c0358f03e28e0870345a77ed886d68b30` |
| `jepadrift/pipelines.py` | `6eeffac88ee02cedd9c8e6c2739f0ae375aa951d8268c2609dc02a37a97771c9` |
| `jepadrift/monitors/eprocess.py` | `106f25b650f3e906d8884ab06d47a5384a3ead789bdd335cdbbabef75b986e1e` |
| `jepadrift/representations/pca.py` | `a1314d104b69640f5e2ce4c57c5e63ab87c8ca14ec8ccc5fdbbde7338b559a4c` |

Other sources and the three seals (E2, E3, PCA full manifest) are hashed in the journal and match the continuation bootstrap.
