# Stream 19-plan — N, k and d around the known Gaussian oracle, and primary-source audit of SPLL, 2026-11-07

## Scope and authority

- **Authority.** GO `prompts/GO-stream-19-plan.md`: the researcher's documentary GO of 2026-11-07, recorded by Codex.
  Canonical plan `prompts/plans/plan-19-plan.md`, which prevails over the native plan of the planning session.
- **Base.** `1440927b49463c13bdd0c819fcd73f30d6a32c31`, branch `stream-19-plan`.
- **Session.** Interactive Claude Code, `claude-opus-5-5`, effort max, no sub-agent.
- **Object.** This documentary note:
  - defines N, k and d;
  - restates the known Gaussian reference;
  - separates information, retention, dimension cost and alignment under explicit assumptions;
  - audits the primary sources of SPLL;
  - lists the prerequisites of any port.

  It closes no campaign: the E4 campaign stays `À_REPLANIFIER`.
- **Not done, as the GO requires.**
  - No code, test, import or execution of a repository module; no computation or simulation.
  - No return data, no row dated 2020 or later, no JEPA/VAE.
  - No `configs/FROZEN.json`, Makefile target, J4 step or PCA benchmark rerun.
  - No change to the paper, configurations, dependencies, memory, sealed results or historical audits, including
    `docs/audits/stream_19_replan_2026_11_06.md` and the 19-oracle files.
- **Status tags.**
  - **[D]** documented in a cited source: the repository at the base, or a primary PDF identified by URL and SHA-256.
  - **[A]** algebraic consequence of cited definitions, stated with its assumptions and a short derivation.
  - **[H]** hypothesis, interpretation or open item.

  No statement tagged [A] or [H] is a measured result or an operational guarantee.

## Sources

- **Repository,** read as text (SHA-256 under Hashes):
  - project memory and prompts: `CLAUDE.md`, the kickoff `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md` and
    `prompts/streams/prompt-19-e4-p3kf.md` ("prompt 19");
  - previous lots: `docs/audits/stream_19_replan_2026_11_06.md`, and the plans, GO and wrapups of lots 19 and
    19-oracle;
  - the oracle: `experiments/e4_oracle_reference.py`, its tests, and `docs/sections/e4_oracle_reference.md` ("oracle
    note");
  - the paper: `paper/sec3_theory.tex` ("Section 3") and `paper/articleC_biblio_addendum.bib`;
  - schemas and deviations: `docs/sections/pca_drift_benchmark.md` ("PCA schema"), `docs/sections/interface_Z.md`, and
    `docs/DEVIATIONS.md` (entries cited by identifier);
  - code, read as text only:
    - `jepadrift/pipelines.py` (`DEFAULTS`, `_columns`, `_stream_signs`, `_detect_p3c`);
    - the docstrings of `log_dictionary_edetector` and `log_subgaussian_mixture` in `jepadrift/monitors/eprocess.py`;
    - `subset_ctx` in `experiments/e1_problem.py`;
    - `jepadrift/floors.py`, lines 90–148;
  - the full-run manifest, read by line search.
- **Primary articles:** publisher-typeset PDFs hosted by the author, read in full on 2026-11-07. The local copies are
  outside the repository and untracked.

| Reference | URL | Bytes | SHA-256 |
|---|---|---|---|
| Kuncheva 2013, IEEE TKDE ("TKDE") | https://lucykuncheva.co.uk/papers/lktkde13a.pdf | 949,391 | `74acaba9eb8fdd1cd43dffdeafa37f872292ad2d05828aef6936c528adc6a052` |
| Kuncheva and Faithfull 2014, IEEE TNNLS ("KF14") | https://lucykuncheva.co.uk/papers/lkwfTNNLS14.pdf | 1,458,935 | `52c776175d8e85c68066355bbeb4ad9d71d23bf3c822a46652d5409793797112` |

- **Bibliographic concordance.** The Bangor University research-portal record of TKDE (vol. 25, no. 5,
  pp. 1175–1180, May 2013) and the author's publication page (https://lucykuncheva.co.uk/recent_publications.htm) give
  the same DOIs. Search-engine summaries served only to locate the PDFs.
- **Not consulted.**
  - the IEEE Xplore records and any errata;
  - the author's MATLAB code (repository `LucyKuncheva/Change-detection`, file `SPLL.m`), neither cloned, read nor
    run;
  - the ICPR 2012 precursor of KF14.
- **Quotations and paraphrase.**
  - At most 25 verbatim words per article.
  - About 200 words of paraphrase per article, bibliographic identification excluded.
  - The content of each article is summarized once, in Sections 5.2 and 5.3, and referred to elsewhere by item label.

## 1. N, k and d: distinct objects

| Symbol | Object | Domain and caveat | Source |
|---|---|---|---|
| N | assets; dimension of the return vector x_t | N ≥ 1 in the oracle; the sealed full run fixes N = 239 | `CLAUDE.md` glossary; oracle `N_GRID`; full manifest, line 33 |
| k | size of the candidate spectral reservoir P_k = axes 1..k | prefix of an ordered frozen basis; k ≤ N; k ≤ nmax = 20 in the full run | PCA schema, lines 101–102; manifest, line 45 |
| S, d | retained axes and the dimension of their subspace | S ⊆ P_k, 1 ≤ d ≤ k | PCA schema, line 25 |
| p | stream dimension of a benchmark detector | d for MEAN; d(d+1)/2 for COV, which does not make that stream Gaussian | PCA schema, line 151 |
| D | dimension of the block to which a cost M(D, γ) is applied | a residual block is not the channel combination of a pipeline; the cost's assumptions are checked block by block | Section 3, lines 68–84 |
| K_MP | residual factors kept at the Marčenko–Pastur edge, n_above_edge − 1 | PC1 is separate; factor mode needs K_MP ≥ 1; K_MP is neither k nor the SPLL cluster count | `interface_Z.md`, lines 152–156; C-repr-mp-K |
| m | components in the low-variance tail | depends on the spectrum and the selection rule; archived m = 46 (`d2_us97`) and 123 (`d3_239`) with Ledoit–Wolf eigenvalues; none recomputed | `interface_Z.md`, lines 157–158; C-repr-layout |

- [D] The sealed full run fixes N = 239 and compares k and d inside one frozen basis. It measures no slope in N
  (manifest, line 33; PCA schema, lines 101–102; replanning audit, F1).
- [D] The closed oracle holds neither an estimated prefix nor a detector. It gives I_N for a known market translation
  and a known covariance (oracle note, "Model and formulas").
- [A] These objects define no universal N/d/k ratio. The ratios actually defined in the sources are:
  - **information gain:** G(N) = I_N/I_1 (oracle);
  - **retention:** r(S) = I(S)/I_x ≤ 1 (Section 3, line 25), bounded by the data-processing inequality (line 20);
  - **costs:** the fluid mixture multiplier M(D, γ) and the dictionary bound (`prop:tax` (b)–(d), lines 70–78);
  - **alignment:** a_max or cos²ϑ (`CLAUDE.md` glossary; `prop:tax` (d));
  - **selection surrogate:** V(S) = I(S)/M(d, γ_M), with γ_M = 504 (PCA schema, line 135; manifest, line 38);
  - **conditional exponent:** a − b/2 (`cor:scaling`, lines 82–84);
  - **estimation regime:** N/T, which enters the Marčenko–Pastur edge (1 + √(N/T))² (PCA schema, line 111) but is not
    a law of the KL.

  A text search of `prompts/`, `docs/`, `paper/` and `CLAUDE.md` finds the phrase N/d/k only in the kickoff
  (line 180).
- [D] **Notation collisions.** ρ is both the equicorrelation and Siegmund's constant ≈ 0.583 (`prop:floor` (a)).
  - K: K_MP; the number of dictionary atoms; the matrix BᵀΨ⁻¹B of `cor:factor`; the IPCA K.
  - k: the reservoir size, or an axis index.

### 1.1 PC1 and the dimensions actually monitored

- [D] **Representation.** The PCA representation exposes the market channel v₁ᵀx/√λ₁ in column 0 in every mode,
  `tail10` included. The residual block has K_MP columns (factor), N − 1 (full) or m (`tail10`). The representation
  thus has K_MP + 1, N or m + 1 columns (`interface_Z.md`, lines 143–150).
- [D] **P3-C channels.**
  - P3-C defaults to `channels="all"` (`jepadrift/pipelines.py`, line 50).
  - `_columns` then returns every named column, market and residual alike (lines 286–290), and `_stream_signs` builds
    its sign streams on those columns (lines 300–302).
  - P3-C therefore monitors K_MP + 1 coordinates in factor mode and N in full mode.
- [D] **E1 arm B.** E1 builds P3-C with `mode="full"` and the default channels (`experiments/e1_problem.py`,
  line 504). That pipeline is therefore not a detector of the N − 1 residual coordinates only. Its mixture reading
  takes its prior from the residual columns (lines 519–524).
- [D] **Default anytime-valid reading.** P3-C passes every selected column to `log_dictionary_edetector`
  (`pipelines.py`, lines 308–309). That function is an equal-weight average of per-direction e-detectors, valid under
  any dependence (`eprocess.py`, lines 92–94).
- [D] **Mixture variant** (`pipelines.py`, lines 310–321).
  - It splits market and residual columns.
  - It sends the residual columns to `log_subgaussian_mixture`, which is documented as valid only if the coordinates
    are independent under H0 (`eprocess.py`, lines 99–102).
  - It averages the two e-detectors with weights proportional to the column counts.
- [D] **F3 direction.** The market channel is exactly the direction of the injected F3 drift, because representation
  and injector use the same eigen-decomposition (`interface_Z.md`, lines 136–139).
- [D] **P3-KF.** P3-KF is specified on the tail block of dimension m (prompt 19, lines 24–26; C-repr-layout). Its
  statistic is not implemented in the inspected tree, and its representation keeps the market column.
- [A] **Consequences.**
  - **PC1.** Zero information in a block orthogonal to the market direction does not extend to the complete P3-C
    pipeline, which carries PC1.
  - **Combination cost.** The cost of a multi-block pipeline is set by its combination rule.
    - In an average with weight w_j, a component that reaches γ/w_j triggers the alarm, since the average is at least
      w_j times that component. This sufficient condition adds ln(1/w_j) on the log-threshold scale.
    - In the full-mode mixture variant, the market block has weight 1/N.
    - The fluid mixture cost of the residual block alone is not the pipeline's cost.
  - **F3 injection.** With a shared fitted covariance, an F3 drift along the fitted v̂₁ shifts only column 0, since the
    other columns are orthogonal eigenvectors of the same matrix. This holds for that injection convention, not for an
    arbitrary market translation.
- [H] **Dictionary bound.** `prop:tax` (d) states it for Gaussian likelihood-ratio e-processes along fixed atoms. Its
  use for the sign-stream CUSUM e-detectors of P3-C is an approximation that a future note must justify.

## 2. Known Gaussian oracle

**Model.** Id is the N × N identity, 1 the vector of ones and δ the common per-asset amplitude. The oracle takes
Σ_N = ρ11ᵀ + (1−ρ)Id and Δμ = δ1, with N ≥ 1, 0 ≤ ρ < 1 and δ > 0.

- [D] I_1 = δ²/2 and I_N = δ²N/[2(1+(N−1)ρ)] nats per observation. G(N) = I_N/I_1 = N/[1+(N−1)ρ] (oracle note,
  "Model and formulas"; Section 3, line 61).
- [A] deff_N = 1+(N−1)ρ is N times the variance of the equal-weight mean of N unit-variance assets, so G(N) = N/deff_N.
- [D] At fixed ρ > 0, G increases towards 1/ρ. At ρ = 0, G = N with no finite ceiling (oracle note).
- [A] **Sufficient direction.** Σ_N⁻¹Δμ is proportional to 1 for every ρ ∈ [0, 1), so the equal-weight pool is
  sufficient for this change (d = 1, I_N retained).
- [A] **Equality case of the data-processing inequality.** For a linear map A, the KL of Ax equals I_N iff Σ⁻¹Δμ
  lies in the range of Aᵀ.
  - Derivation: with y = Σ^(−1/2)Δμ and B = AΣ^(1/2), the KL of Ax is ½‖Py‖², where P is the orthogonal projector onto
    the range of Bᵀ; y lies in that range iff Σ⁻¹Δμ lies in the range of Aᵀ.
  - Hence every projection whose row space contains 1 keeps I_N, and every projection explicitly inside 1^⊥ carries
    zero information.
- [A] **ρ > 0.** Population PC1 is the market direction 1/√N. A prefix that contains it keeps I_N for every k ≥ 1,
  even though the order of the N − 1 equal bulk eigenvalues is degenerate.
- [A/H] **ρ = 0 and estimated bases.**
  - At ρ = 0, all eigenvalues are equal, PC1 is not identified, and 1/√N is only one possible eigenvector. The residual
    or tail of an arbitrary or estimated PCA is not necessarily orthogonal to 1, so zero information is not guaranteed
    there.
  - With an estimated basis at ρ > 0, v̂₁ differs from v₁ in general. No leakage is quantified here.
- [A] **Edge cases.**
  - N = 1: no residual; Σ_1 = [1]; ρ is inert and G = 1.
  - d = 0: no stream.
  - ρ = 1 with N ≥ 2: Σ_N is singular. This value lies outside the oracle's domain, which is exactly the set of ρ for
    which Σ_N is positive definite at every N (−1/(N−1) < ρ < 1 for each N ≥ 2).
  - δ = 0: G is undefined (0/0), and the oracle rejects this value.
  - A complete invertible projection keeps the KL. No transformation increases information (Section 3, line 20).

## 3. Retention, dimension and alignment

- [D] **Monitor delay in Section 3** (line 68). A monitor that watches D latent coordinates without knowing the drift
  direction has delay M(D, γ) τ_γ / r_φ(D), with τ_γ computed from I_x. The design target is max_D r_φ(D)/M(D, γ).
- [D] **Assumptions of M.** `prop:tax` (lines 70–78) derives M(D, γ) for i.i.d. Gaussian whitened observations under
  the alternative, with post-onset mean θ, I = ‖θ‖²/2 and the matched prior s² = 2I/D. For a declared subspace S of
  dimension d whose coordinates are jointly whitened, this reads I(S) = ‖θ_S‖²/2 and s² = 2I(S)/d.
- [A] **Sign streams.** Part (a) of `prop:tax` also makes the mixture a test supermartingale for independent sign
  streams. The fluid multiplier of parts (b)–(c), however, assumes Gaussian observations under the alternative, so M
  does not apply directly to the P3-C sign streams. The criterion below stays fluid and carries no ADD guarantee.
- [A] **Fluid criterion and its decomposition.** Under these assumptions, let r(S) = I(S)/I_N.
  - The fluid criterion is T_fl(S) = M(d, γ) ln γ / I(S), with γ > 1 on the e-value scale.
  - Against a scalar reference with known direction (ln γ / I_1), its gain factors as G(N) · r(S) / M(d, γ):
    information, retention (at most 1) and dimension cost.
  - This is a ratio of fluid criteria, not a measured or exact ADD ratio.
- [A] **Against the full space** (d = N, r = 1), the fluid criterion favours S iff r(S) > M(d, γ)/M(N, γ). The form
  r(S) > √(d/N) is only an approximation, valid when d and N are large compared with ln γ, where M ≈ √(D/ln γ)
  (`prop:tax` (c)).
- [D/A] **Dictionaries and multi-block pipelines.** For dictionaries, dimension alone is not enough: the number of
  atoms K and the alignment cos²ϑ enter the bound (ln γ + ln K)/(cos²ϑ ln γ) (`prop:tax` (d)). A multi-block pipeline
  must also declare its combination rule (Section 1.1).

### 3.1 Amplitude and expectation

- [A] **Market drift.** With a fixed per-asset amplitude, its information is of constant order at fixed ρ > 0 and of
  order N at ρ = 0.
- [A] **Breadth drift with an isotropic second moment.** At fixed ρ, two amplitude conventions give different
  information exponents:
  - a fixed total-norm budget (prior covariance (σ²/N)Id, E‖Δμ‖² = σ²) gives E[I] = (σ²/2N) tr Σ⁻¹, which stays
    bounded in N (exponent 0);
  - a fixed per-asset RMS amplitude (prior covariance s²Id) gives E[I] = (s²/2) tr Σ⁻¹, which grows linearly
    (exponent 1).
- [A] **Bulk fraction.** In the equicorrelated bulk, the fraction m/(N − 1) of an m-dimensional bulk subspace is a
  ratio of expectations under an isotropic prior in 1^⊥. It is not the retention of each drift: a realized drift can
  be concentrated in the tail or orthogonal to it, even when the bulk is flat.
- [A] **Laws in N.** The laws N^(a − b/2), with I(N) of order N^a and D(N) of order N^b (`cor:scaling`), stay
  conditional on the amplitude convention, the alignment and the fluid criterion. They are not measured slopes.
- [H] **Estimated PCA at ρ = 0.** An expected retention such as k/N for a k-dimensional prefix needs an orthogonally
  equivariant subspace rule. That rule must break ties explicitly when eigenvalues are repeated, as in the
  rank-deficient case T ≤ N. No property of a numerical eigensolver is assumed.
- [D] **Historical protocol.** It fixes the per-asset amplitude: convention (b), prompt 19 lines 17–20, and
  C-inject-conv-b. This note changes no protocol.

## 4. Delay readings

- [D] **Budget.** ln γ / I is a lower bound on the expected delay of any test supermartingale started at the onset
  (`lem:budget`, lines 29–35).
- [D] **Anytime-valid.** The CUSUM e-detector has ARL0 ≥ γ (`prop:floor` (a)). Its Gaussian delay expression with
  Siegmund's correction, also coded in `jepadrift/floors.py`, is an approximation, not an exact finite-step ADD.
- [D] **Exact reading** (ARL0 calibrated to γ). Φ(γI)/I is a diffusion approximation (`prop:floor` (b)), not an exact
  bound at finite γ.
- [D] **Fluid approximations.** M(D, γ) τ_γ and the dictionary bound.
- [A] **The KL oracle alone** provides no ADD, no ARL0 and no FPR(H).

## 5. Primary-source audit of SPLL

### 5.1 Identification [D]

- **TKDE.** L. I. Kuncheva, "Change Detection in Streaming Multivariate Data Using Likelihood Detectors", IEEE
  Transactions on Knowledge and Data Engineering, vol. 25, no. 5, pp. 1175–1180, May 2013, DOI 10.1109/TKDE.2011.226.
  Published online 19 October 2011.
- **KF14.** L. I. Kuncheva and W. J. Faithfull, "PCA Feature Extraction for Change Detection in Multidimensional
  Unlabeled Data", IEEE Transactions on Neural Networks and Learning Systems, vol. 25, no. 1, pp. 69–80, January 2014,
  DOI 10.1109/TNNLS.2013.2248094. Its reference [28] cites TKDE in early-access form, "vol. 25, no. 99, p. 1, Oct.
  2011, DOI: 10.1109/TKDE.2011.226" (p. 80).
- **Repository bibliography.** `kuncheva_faithfull_2014` matches the printed header (title, journal, 25(1), 69–80,
  2014) and has no DOI field. There is no TKDE entry.
- **Prompt 19.** "Kuncheva (2013, IEEE TKDE)" is verified: 2013 is the issue year, and 2011 the early-access year of
  the same DOI.

### 5.2 TKDE in brief [D]

- **T1** (§1, p. 1175). Two given windows, W1 and W2, are compared; windowing is out of scope.
- **T2** (Proposition 1, p. 1176). For two normal laws with a common covariance, the per-observation log-likelihood
  ratio tends to ½(μ₂−μ₁)ᵀΣ⁻¹(μ₂−μ₁).
- **T3** (§2.3, eqs. 2–3, pp. 1176–1177). A c-component Gaussian mixture with a common covariance is fitted on W1 by
  "a single round of k-means clustering"
  and its likelihood is bounded. SPLL is then proportional to the mean over W2 of the squared Mahalanobis distance to
  the nearest centre. Stated reference law:
  "chi-square distribution with n degrees of freedom".
- **T4** (§3, pp. 1177–1179). ROC/AUC over pairs of disjoint windows from 30 static data sets, with M∈{50,100},
  K∈{2,3,7} and a swap of two features as the change.
- **T5** (§1 and §4).
  "we are not proposing a theoretical guarantee";
  a threshold for SPLL is left to future work.

### 5.3 KF14 in brief [D]

- **K1** (§III.A, eqs. 26–28, p. 73). SPLL uses c-means clusters on W1, with K = 3 reported adequate, and a
  "weighted intra-cluster covariance matrix".
  It keeps the larger of the two comparison directions, to
  "fold the criterion to make it monotonic".
  No threshold is set.
- **K2** (§IV.B, p. 75). PCA is fitted on W1 of standardized data. The rule is to
  "keep the components beyond the K% of dismissed variance",
  with K∈{0,50,80,85,90,95} % and M = 50.
- **K3** (p. 76). On 35 static data sets, AUC rises significantly over raw data at K = 90 % and 95 %, and falls at
  K = 0 %.
- **K4** (§V, pp. 78–79). A video example slides a 25-frame W2 past a fixed 50-frame W1 (PCA on W1 only) and plots
  criterion values without a threshold.

### 5.4 Elements of prompt 19 checked

| Element of prompt 19 | Verdict | Basis |
|---|---|---|
| "Kuncheva (2013, IEEE TKDE)" (line 24) | [D] verified | Section 5.1 |
| semi-parametric log-likelihood detector (line 24) | [D] consistent | T3 |
| k-means on the reference window (line 26) | [D] consistent; the naming differs in K1 | T3, K1 |
| number of clusters | not fixed by prompt 19 | T4, K1 |
| statistic on a sliding window (line 26) | [D] adaptation | T1, T3, K1, K4 |
| `tail10` inputs, m = 46 / 123 (line 25) | [A] rule of K2 at K = 90 % (equivalence below), applied by the project to the Ledoit–Wolf covariance of the unstandardized calib rows, fitted once; 46 / 123 (48 / 130 with empirical eigenvalues) are project values | K2; `interface_Z.md`, lines 136 and 157–158; C-repr-layout |
| threshold on D6 null windows for FPR(H) = α (line 27) | [D] project design: no calibrated threshold and no sequential FPR(H)/ARL0 guarantee in either article; ROC false-positive rates are per window pair | T4, T5, K1, K3 |
| prior art on low-variance components (line 9) | [D] not established as a sequential result | K3; KF14 §II.B, pp. 71–73 |

**Equivalence of the tail rules [A].** Let C_j be the cumulative variance share of the j leading components.
- K2 dismisses the shortest prefix with C_j ≥ 0.9, that is j* = min{j : C_j ≥ 0.9}.
- C-repr-layout keeps the longest tail with share ≤ 0.1. Since 1 − C_{n−m} ≤ 0.1 ⟺ C_{n−m} ≥ 0.9 and C is
  nondecreasing, m* = n − j*: both rules keep the same components.
- The rule removes a declared share of variance; it does not keep a fixed proportion of the components.
- [H] The wording at exact equality, and cumulative sums evaluated in floating point, are not settled.

### 5.5 Discrepancies and open items

1. [D] **Date.** 2011 (early access, KF14 [28]) and 2013 (issue) denote the same DOI.
2. [H] **Clustering variant.** The c-means variant of K1 is unspecified.
3. [D] **Two statistics.** The one-sided SPLL (T3) and the folded SPLL (K1) differ, so an unqualified "SPLL" is
   ambiguous.
4. [H] **Decision rule.** A p < 0.05 rule may exist in the author's code. This is known only from a search-engine
   summary and is not evidence.
5. [L] **Common covariance.** Neither article specifies its estimator (weights, divisor). This is open before any
   port.
6. [A] **Singularity.** A covariance estimated on W1 alone has rank at most M₁ − 1, and a pooled within-cluster
   covariance rank at most M₁ − K. TKDE Table 1 (p. 1178) includes n = 57 and n = 60 features, run with M = 50, where
   any such S is singular. [L] How S⁻¹ was formed is not stated; this is open before any port.
7. [D] **Time series.** The absence of time series, heteroscedasticity and sequential monitoring concerns the static
   AUC comparisons (T4, K3), not the video sequence of K4. No AUC is transferred to daily returns.

### 5.6 Consequences of the mathematical review

- [A] **χ² reference.**
  - With several centres, the distance to the nearest centre is pointwise at most the distance to the generating
    centre. With known parameters, it is stochastically dominated by the χ²_n law of the latter.
  - Estimation from W1 adds a further difficulty, and the χ²_n spread describes one distance, not the window mean.
  - The reference cannot serve as a calibration guarantee.
- [A] **Density and distance.** Before the common-covariance simplification, the component of largest density in the
  bound need not be the nearest in Mahalanobis distance, because of the determinant terms. The identification in T3 is
  exact only with a common covariance.
- [A] **Idealized moments.** Assume one component, known parameters and M₂ i.i.d. Gaussian observations, and write I_W
  for the per-observation KL in the monitored coordinates.
  - Under H0, the window mean has mean n and variance 2n/M₂.
  - Under a translation Δ, it has mean n + ΔᵀΣ⁻¹Δ = n + 2 I_W and variance (2n + 8 I_W)/M₂.
  - The standardized mean shift of a tail of dimension m, I_tail √(2M₂/m), exceeds that of the full input dimension
    n_full iff I_tail/I_full > √(m/n_full).
  - This compares standardized mean shifts only. Quantiles and variances under the alternative differ, so no dominance
    in power, ADD or FPR follows without a separate study.
  - The resemblance to the fluid form M(D, γ) ≈ √(D/ln γ) is not an identity.
- [A] **Parity.** For frozen centres and a common positive definite S, d(x) = min_i (x − μ_i)ᵀS⁻¹(x − μ_i) is even iff
  the centre set is symmetric, {μ_i} = {−μ_i}.
  - Proof: d ≥ 0, and d(x) = 0 iff x is a centre. If d is even, its zero set is symmetric. Conversely, reflecting a
    symmetric centre set leaves d unchanged.
- [A] **D6 signs on a given panel.** With a frozen reference, per-day D6 signs change SPLL(W1, W2) only if W2 contains
  rows with d(x_t) ≠ d(−x_t).
  - A non-symmetric centre set is necessary, not sufficient.
  - A refit on D6 windows, or the fold of K1, may add sign randomness without guaranteeing it in every configuration.
  - [H] Reading prompt 19, line 26, as "reference fitted once and frozen" is an interpretation.
- [A] **No calibration from sign randomness.** Even non-degenerate sign randomness resolves neither in-sample reuse nor
  the overlap of historical windows (C-P4D-null-insample; C-pca-predictive-rank). No D6 calibration is deduced from
  this property.
- **Variants and adaptation.** The one-sided and two-sided variants must be kept apart. A financial comparator built
  on these ideas will be a traced adaptation and will not claim to reproduce the original protocol.

### 5.7 Prerequisites before any port [H]

- **Variant.** Declared as one-sided (T3) or folded (K1), never mixed.
- **Clustering.**
  - The cluster count is fixed ex ante.
  - The number of k-means restarts is declared, with local SeedSequence seeds.
  - Results do not depend on the number of workers.
- **Covariance.** The common covariance estimator is declared. M₁ − K < n_in is refused explicitly; no pseudo-inverse or
  regularization is introduced silently.
- **Windows.** Window sizes, disjointness and contiguity are declared; sliding windows are an adaptation.
- **Representation.** Declared as raw, normalized, or the K2 tail. `tail10` on the Ledoit–Wolf PCA of the calib rows
  is a project variant.
- **Calibration.**
  - Any FPR(H) or ARL0 needs a declared null: either independent synthetic paths, under the predictive-rank guarantee,
    or historical D6 windows, which carry no established guarantee and need the support check of Section 5.6.
  - Nothing is taken from the χ²_n reference or from ROC false-positive rates.
  - States and thresholds are fitted on drift-free rows and frozen during monitoring.
- **Author's code and errata.** Neither was read or checked. Reading the code, without cloning or execution, needs a
  decision. Any discrepancy between code and article is recorded.

## 6. Future question and working assumptions [H]

- **Question retained.** Under a declared covariance, amplitude convention and projection rule, how do the information
  gain in N, the retention r(S), the dimension cost and the alignment separate? The market reference above can be used
  on paper now. Estimated bases, breadth priors and combined detectors need their own assumptions.
- **Design defaults.**
  - one audit note, this file;
  - the equicorrelated model first;
  - P3-KF keeps its identifier, with the qualifier "SPLL adaptation, not a reproduction".

  No further spectral model, oracle extension, SPLL port, simulation or new slope is part of this lot.
- **Extended proofs.** The proofs sketched in the planning phase are future work. Writing them must not turn
  hypotheses, ratios of expectations or moment criteria into operational guarantees.
- **Dependencies.**
  - No CD-DFM, JEPA or freeze deliverable is needed for this note; they stay open for the experiments that would need
    them.
  - A coded analytic extension needs a separate plan, GO and exclusive slot for `floors` and `pipelines`.
  - Any D5 or D6 campaign needs its own scientific authorization. Real D6 data and JEPA training stay outside the
    current mandate.

## 7. Not examined

- The author's MATLAB code, the IEEE Xplore records and errata, and the ICPR 2012 article.
- `jepadrift/monitors/eprocess.py` beyond the two docstrings cited, including the internals of `log_edetector`.
- Any return panel or row dated 2020 or later, the full-run `trials.csv`, and the PCA benchmark outputs beyond their
  manifest hashes.
- Whether the archived E1 arm B numbers would differ under a residual-only P3-C; nothing was rerun or compared.

## 8. Documentary controls

Shell commands only, appended to the ignored journal `logs/stream_19_plan/doc_checks.log`; no Python process. The
results go to the session's review message and the wrapup, not here, since this note cannot record its own hash.

- **C1.** HEAD equals the base, nothing is staged and no tracked file differs. The untracked set is exactly this note
  and the two Codex files.
- **C2.** The Codex plan and GO keep the SHA-256 recorded before any write.
- **C3.** J1: `results/e2/e2_cells.csv` keeps its expected SHA-256 on disk and in the index, with 47 CRLF lines and no
  bare LF.
- **C4.** The E3 CSV and the four sealed PCA manifests keep their SHA-256.
- **C5.** Every cited repository path exists. The historical E4 deliverables and `configs/FROZEN.json` are absent.
- **C6.** Every cited line anchor contains the cited text.
- **C7.** Every archived number cited is found in its source.
- **C8.** The local PDF copies keep the SHA-256 above. Verbatim words and the word counts of Sections 5.2 and 5.3 are
  counted per article.
- **C9.** This note contains no absolute home-directory path and no banned wording.

## Hashes

Recorded on 2026-11-07, before this note was written.

| File | SHA-256 |
|---|---|
| `prompts/plans/plan-19-plan.md` (Codex) | `09d43bdb9478fc6536c478bebe679e3905d0eca9fa4340c61d7de3f63e946ccd` |
| `prompts/GO-stream-19-plan.md` (Codex) | `4cd71b0762b44a6a2faceec02751ebceaa406ae9206d35bcd4ec87c6f6cdeaca` |
| `CLAUDE.md` | `e2e0d15888c2b235da3162427498a966d8ec18ae1f66b182a32601e4a016c473` |
| `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md` | `59fb089162ef9121679d8cb53afabe2c0813168b37c6de4c1184ac33b2d3f51b` |
| `prompts/streams/prompt-19-e4-p3kf.md` | `c184d789b184d37799f300382e42ffe214300685769d153006dbb033dea8f84c` |
| `docs/audits/stream_19_replan_2026_11_06.md` | `eac783b195f25cbb77265b7d2f392dca1802c53421380dacbd63fc14cef7cf71` |
| `experiments/e4_oracle_reference.py` | `181375944853cf3cecd274015fd5dd774007cbe295a86314510eb573bde92c93` |
| `tests/test_e4_oracle_reference.py` | `a79c65385eef97d4e4e2306c30f05d3a5b3cb7abe9c997a82fe4ec6d746f2c0f` |
| `docs/sections/e4_oracle_reference.md` | `4dca48c45236650793f745e82d82a8d7ce29fef8df45d565e5f7edfac1759270` |
| `paper/sec3_theory.tex` | `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` |
| `paper/articleC_biblio_addendum.bib` | `5b28489cce1cb14e8c7f1b208ae30e51acfb7a350a3aa56ac23c1edd75c001c7` |
| `docs/sections/pca_drift_benchmark.md` | `adae1ad1d068830a6eb7b69e6266ac99f2a9f7940099469ab44dc8d2938d9484` |
| `docs/sections/interface_Z.md` | `6b468a29139954f824e6d4626950c5974d3019ffa103ca9ab81105a306d75517` |
| `docs/DEVIATIONS.md` | `2c83037fda35f406a5660c9e33e7f50c0358f03e28e0870345a77ed886d68b30` |
| `jepadrift/pipelines.py` | `6eeffac88ee02cedd9c8e6c2739f0ae375aa951d8268c2609dc02a37a97771c9` |
| `jepadrift/monitors/eprocess.py` | `106f25b650f3e906d8884ab06d47a5384a3ead789bdd335cdbbabef75b986e1e` |
| `experiments/e1_problem.py` | `52c520ab70b418cd491015075dc2a15e7a28a278ff2a727e7f3ebabad9327e65` |
| `jepadrift/floors.py` | `49b36c5ef1b7995a274243180825731d42a61829c70e00fc7fc72841d39a9170` |
| `results/pca_drift_benchmark/full_2000_20261101/manifest.json` | `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47` |
| `results/pca_drift_benchmark/tables/full_2000_20261101/table_manifest.json` | `79804fcf434ee375446d2fdbeface8bda189fb1e7e530fb7095151ddde87f619` |
| `results/pca_drift_benchmark/figures/full_2000_20261101/figure_manifest.json` | `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |
| `results/pca_drift_benchmark/figures/full_2000_20261101_fix_smoke_no_claims/figure_manifest.json` | `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |
| `results/e2/e2_cells.csv` (J1) | `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` |
| `results/e3/e3_overshoot.csv` | `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3` |
| TKDE PDF (local copy) | `74acaba9eb8fdd1cd43dffdeafa37f872292ad2d05828aef6936c528adc6a052` |
| KF14 PDF (local copy) | `52c776175d8e85c68066355bbeb4ad9d71d23bf3c822a46652d5409793797112` |
