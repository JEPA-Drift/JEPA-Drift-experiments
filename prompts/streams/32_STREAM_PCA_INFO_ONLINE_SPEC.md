# STREAM 32 — PCA-INFO-ONLINE: Oracle vs. Non-Oracle Information/Dimension Selection

**Status:** Researcher-requested NEW priority, specification for planning and implementation. This file is **not** an execution result, a retroactive amendment to E4, or an unconditional GO for a full scientific campaign.

**Owner:** Claude Code implementation agent in an isolated worktree, supervised by Codex. Codex owns architecture review, the written GO, resource allocation, integration, and release. Read `CLAUDE.md`/`AGENTS.md`, `prompts/Protocole Codex.md`, the current stream-23 status, and applicable recent GO documents before modifying anything.

## 1. Context, priority, and falsifiable question

E4 (`docs/audits/stream_19_e4_full_20261114.md`) evaluated an **ex ante exhaustive spectral dictionary** under constant aggregate information and isotropic residual injections. It **did not** evaluate an information-selected PCA pipeline without an oracle. Do not describe E4 as such a test or rewrite its sealed protocol/results.

The earlier PCA benchmark (`experiments/pca_drift_benchmark.py`, stream 28, schema `pca_drift_benchmark/2`) implements oracle top-information subsets for Gaussian mean changes, and an ex-ante historical stress-library selector on pre-2020 data. Its synthetic `EXANTE_QBAR` branch is explicitly `UNSUPPORTED`; there is **no online non-oracle information selector**. Reuse audited mathematical utilities without modifying sealed producers.

**Primary question:** Can an *online, predictable, non-oracle* PCA selector that maximizes estimated drift information divided by dimension cost reduce sequential detection delay relative to spectral-prefix and fixed-subset comparators, at demonstrably comparable false-alarm performance?

**Secondary questions:**
- How much performance is lost from the true-information oracle to a past-only online estimate?
- How much does choosing axes by information outperform keeping their canonical decreasing-eigenvalue order?
- How often does the affine cost change the selected dimension and realized delay relative to the Gaussian-mixture fluid cost?
- When does online estimation fail (weak, diffuse, rotating, or unlearnable drifts; short horizons)?

**Scope:** first establish results on synthetic **mean shifts**. No JEPA training, no historical returns, no 2020+ access, no J4, no covariance-drift main claim, no rereading/rewriting E4, and no new real-data evaluation. Covariance changes are a separately specified future extension, because their joint Gaussian KL need not be additive and the mean-mixture dimension cost is not an established covariance cost.

## 2. Source hierarchy and theoretical conventions

Inspect exact current versions, not recollections. **The first three historical source notes may be supplied outside the Git repository (Project attachments or researcher's local files); they are not guaranteed to exist at the repository root.** If unavailable, record `REFERENCE_NOT_MOUNTED` and rely on the self-contained equations/contracts below rather than inventing a file path:
- `11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md` (original experimental intent and its old illustrative figure);
- `Réponses_Clarification_Gemini_JEPA_Drift_3.md`, especially §§4–6 around slides 39–40;
- `DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md`, especially slides 15–16 and appendices A6, A11, A12;
- `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`;
- `docs/sections/pca_drift_benchmark.md`, `docs/audits/PCA_CONTRACTS_VALIDATION.md`;
- `docs/audits/stream_19_e4_full_20261114.md`;
- the active stream-23 plans/GO and `docs/audits/stream_23_compatibility_2026_11_06.md`.

When sources disagree with current code, cite the precise conflict and ask Codex to arbitrate it before execution; do not silently blend incompatible contracts.

### 2.1 Definitions

Let `N` be the number of input assets, `K` the number of admissible PCA axes, `S ⊆ {1,…,K}` an axis subset, `d = |S|`, and `γ_M > 1` the **analytical cost** parameter.

For a Gaussian mean change `P0 = N(μ0, Σ0)`, `P1 = N(μ0+Δ, Σ0)` with `Σ0 ≻ 0` and equal covariance, a **population** PCA eigenpair `(v_k, λ_k)` satisfies:

`q_k = (v_k' Δ)^2/(2 λ_k)`, and `I(S) = Σ_{k∈S} q_k` when the chosen basis diagonalizes the *true* reference covariance. For an estimated Ledoit–Wolf basis that does not exactly diagonalize `Σ0`, the sum is a **plug-in diagonal surrogate**; report the true Gaussian joint projected information separately for diagnostic purposes:

`I_joint(S) = 1/2 Δ_S' [Cov0(z_S)]^{-1} Δ_S`.

Do not claim that `Σ q_k` equals joint KL in the empirical fitted basis, nor that the Gaussian expression is exact Student-t KL.

Define `A = log γ_M` and `x_d` as the unique positive root of

`x_d = A + (d/2) log(1 + 2*x_d/d)`,

and `M(d, γ_M) = x_d/A`. This is a **model-based fluid information budget multiplier**, not an exact finite-horizon ADD, fitted scan threshold, or universal delay cost. Reuse the tested root solver in the stream-28 runner.

Define two **selection objectives**:

- `C_MIX(d) = M(d, γ_M)`; `V_MIX(S) = I(S)/C_MIX(d)`. This is the principal theoretical selection score.
- `C_AFF(d) = a + c*d`, with `a,c > 0`; `V_AFF(S) = I(S)/C_AFF(d)`. This is a precommitted analytic approximation/ablation. Derive `a,c` deterministically from the computed `M(d,γ_M)` on a **predeclared calibration range** (pilot default `d=1..min(16,K)`), using the stated fitting method and record residuals and argmax disagreement. Do **not** copy the slide-note's claimed `R²>0.98` or regard an affine fit as an exact mixture cost. No fitting to test delays or injected test effects.

For any positive dimension-only cost and additive information, sorting `q_k` in decreasing order and evaluating all `d` is **globally exact**, not a different method from forward greedy. A dedicated test must establish sorting = greedy = exhaustive search for small `K`, including tie behavior. When consecutive objective values tie, select the smallest `d`, then lexicographically smallest sorted axis list. There is no unconditional unique `d*`: adjacent ties can exist even for strictly decreasing `q_k`.

## 3. Method matrix: separate information source, axis order, and cost

For both eligible-axis universes defined below, implement the **eight main cells** from this factorial design:

| Information source | Axis order | Objective | ID |
|---|---|---|---|
| True test injection (oracle) | Decreasing true `q_k` | `C_MIX` | `ORACLE_INFO_MIX` |
| True test injection (oracle) | Decreasing true `q_k` | `C_AFF` | `ORACLE_INFO_AFF` |
| True test injection (oracle) | Canonical eigenvalue-descending prefix | `C_MIX` | `ORACLE_PREFIX_MIX` |
| True test injection (oracle) | Canonical eigenvalue-descending prefix | `C_AFF` | `ORACLE_PREFIX_AFF` |
| Past-only online estimate | Decreasing estimated `qhat_{k,t-1}` | `C_MIX` | `ONLINE_INFO_MIX` |
| Past-only online estimate | Decreasing estimated `qhat_{k,t-1}` | `C_AFF` | `ONLINE_INFO_AFF` |
| Past-only online estimate | Canonical eigenvalue-descending prefix | `C_MIX` | `ONLINE_PREFIX_MIX` |
| Past-only online estimate | Canonical eigenvalue-descending prefix | `C_AFF` | `ONLINE_PREFIX_AFF` |

For `INFO` methods: sort descending marginal information, use cumulative sums and enumerate **every** `d=1..K`; select the maximizer. A separate "forward greedy" experimental line is **not** justified under additivity.

For `PREFIX` methods: preserve canonical PCA rank order and enumerate **every** prefix length. Do **not** compute an information-sorted `d*` and apply it to the prefix. The canonical `q_k` sequence is not necessarily monotone, so stopping on its first negative marginal gain is invalid.

**Required common benchmarks (same trajectories and detector):**
- `FIXED_PREFIX_D`: a dimension from predeclared null-only/variance rule, with its actual axis list and label;
- `FIXED_EXANTE_QBAR`: information learned solely from a **separate synthetic development stress library**, never from the evaluation change; frozen before null calibration/test. If no validated transfer-prior construction is possible, mark `UNSUPPORTED` rather than fabricating labels;
- `FULL_K`: all `K` available axes using the common detector; E4's published SPEC-full is **historical context only**, not a numerically comparable detector in this new study;
- `CPV90`: actual full-spectrum 90% cumulative-variance rule, with `OUTSIDE_UNIVERSE` if not feasible. Never fabricate a chosen rank;
- optional `ORACLE_DIRECTION_LR`: a **clearly distinct unattainable lower-bound diagnostic**, not one of the eight comparable methods.

**PC1 convention:** main *residual-only* experiment has eligible set `E={2,…,K+1}`; `d` counts residual axes only. An explicitly separate *market-inclusive* control has `E={1,…,K}`. Never silently drop PC1 in a market/mixed drift, and never compare methods with different candidate universes as if they shared the same attainable oracle.

## 4. Online information estimator and time contract

The PCA basis `(V,λ)`, center `μ0`, and null normalizations are learned **only on the independent reference fit** and frozen during each trajectory. **Do not refit PCA at every step in this first experiment**: only subset, dimension, and non-oracle information estimates may change. Dynamic PCA refitting is a later ablation with a separate protocol.

Let `y_{k,t}` be the null-standardized score for eligible axis `k` at monitoring time `t`. Under the exact-coordinate Gaussian control, `y_{k,t}|H0 ~ N(0,1)` independently. Let `F_{t-1}` be all information through the previous monitoring step.

At the **start** of step `t`, compute a windowed mean on strictly earlier steps:

```
m_t = min(w, t-1)
bhat_{k,t-1} = mean(y_{k,s}: t-m_t <= s <= t-1)
qhat_{k,t-1} = 0.5 * max(0, bhat_{k,t-1}**2 - 1/m_t)
```

for `m_t >= 1`. This is a bias-corrected squared-mean **surrogate** clipped at zero, not an unbiased estimator after clipping. More generally, under a frozen null variance `σ0,k²`, use the corresponding variance scaling and subtract `σ0,k²/m_t`; label the plug-in information surrogate. For `m_t=0`, use the same **predeclared fallback subset** across methods, never test-drift knowledge. Ties in estimated contributions use the smaller *canonical* axis index. Use all `K` past scores for screening; explicitly report that this policy reads the full past cross-section even though the detector consumes only selected coordinates at each step.

Set the new choice `S_t ∈ F_{t-1}` **before** observing `y_t`; evaluate the detector on `y_{S_t,t}` and only then update the estimator for step `t+1`. `S_t` must be identical across two paths with the same prefix through `t-1`, even if their current or future observations differ. Never use `tau*`, injected `Δ`, future outcomes, test-family labels, or post-event data to choose the online subset.

Pilot window grid **proposed and frozen before the first power inspection**: `w ∈ {32, 128}`. Choose a single primary window using independent development paths or predeclare both and account for multiplicity. The primary method is online recomputation **every day**; selection smoothing/hysteresis and multi-window tuning are secondary predeclared ablations, not an excuse for post-hoc tuning.

For `t < w`, the window uses only available history, **not** borrowed future or alternative-specific warm-up. A separate onset-at-`τ* > 1` design may carry a pre-onset null history, but must report pre-onset alarms and distinguish it from onset-aligned analysis.

## 5. Common detector: coherent adaptive Gaussian-mixture scan

To avoid treating a changing `S_t` as though it had been fixed retrospectively, implement the **predictably masked Gaussian mean-mixture scan** on all eligible coordinates.

For each time `i`, define `m_{ik}=1[k∈S_i]`. For a candidate change start `τ≤t`, let

`n_{k,τ:t} = Σ_{i=τ}^t m_{ik}` and `D_{k,τ:t} = Σ_{i=τ}^t m_{ik} y_{k,i}`.

Given a *fixed, predeclared* `s2>0` (prior variance per standardized coordinate, determined without injected test `Δ`), define

```
logL(τ,t) = Σ_{k=1}^K [
    -0.5 * log1p(n[k,τ:t]*s2)
    + s2 * D[k,τ:t]**2 / (2*(1+n[k,τ:t]*s2))
]
W_t = max_{1 <= τ <= t} logL(τ,t)
T_h = first t with W_t >= h
```

An axis with `n=0` contributes zero. Only scores observed while selected enter `D`, **never** rescore historical unselected samples when an axis enters `S_t`. This formula integrates a *time-constant but unknown* alternative mean for each coordinate under an independent Gaussian prior; under an exact independent Gaussian null and predictable masks, each fixed-`τ` likelihood ratio is a valid segment likelihood-ratio martingale. **The scan maximum itself is not an e-process**. Its finite-horizon false-alarm performance must be controlled by independent null calibration; a union bound may be recorded as a conservative diagnostic when its exact null assumptions hold.

For constant masks `S_i=S`, the statistic must reduce, within numerical tolerance, to the existing `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM` statistic for subset `S`. Explicitly check this algebraic and executable equivalence. Cache count and score prefix sums; do not silently replace the full segment scan by a truncated change-start window or use a known-`Δ` LR. If performance requires a different detector, propose it as a **separate labeled sensitivity study**, not a hidden substitution.

Pilot prior default: `s2 = 2*log(H/α)/(H*K)` **for all policies**, using the same `K` candidate axes even when the selected `d_t` differs; freeze it before alternative inspection. An independently tuned development-only prior is a separate registered sensitivity analysis, and must never use the injected test effect. This common prior is an engineering comparison choice, not the oracle-matched prior underpinning the derivation of `M`.

`γ_M` in `M(d,γ_M)` is only the analytic dimension-cost parameter (proposed default `504`). The operational alarm threshold `h` must be calibrated for the **entire policy**, including its adaptive selections, under independent null trajectories. Never set `h=log γ_M` by fiat. Do not claim a calibrated `FPR(H)` is the same as `ARL0`, or that minimizing the fluid score exactly minimizes empirical finite-horizon RMST.

**Null validity:** the conditional Gaussian martingale interpretation is justified only for the exact-coordinate iid Gaussian control. Student-t, shared-scale shocks, serial dependence, and imperfect LW whitening require empirical calibration and may not inherit that guarantee.

## 6. Synthetic scenarios and division of data

Use two clearly separated **model arms**:

1. **`EXACT_PC_GAUSSIAN` (mathematical control):** construct independent standardized Gaussian PC scores with an *exact, known* population PCA frame and a strictly separated positive spectrum `λ1>…>λN`; inject the mean change in that frame and map to input returns if needed. **Proposed reproducible spectrum:** `λ1=16` and `λk=0.05+6*exp(-(k-2)/8)` for `k=2,…,N`. Fix a seeded orthonormal basis with `v1=1/sqrt(N)` (equally weighted market) and a deterministic residual completion; freeze its signs and hash. This spectrum is a **new design decision**, not an empirical financial estimate. Mark the known representation as an analytical control, **not a learned deployment estimator**. This is where additive KL, top-`q` optimality, and masked scan null properties can be asserted exactly.
2. **`FITTED_LW_GAUSSIAN` (deployment analogue):** draw independent null training returns, estimate Ledoit–Wolf PCA once, then freeze it. Measure achieved `Cov0(z)`, diagonal plug-in `q`, and true projected joint Gaussian KL separately; acknowledge that `INFO` sorting is exact for the *additive surrogate*, not necessarily optimal for joint KL. The PCA basis is not refitted after injection.

After Gaussian gates pass, permit **`FITTED_LW_T7`** as a prespecified robustness arm; all Gaussian KL values there are **proxies**, not exact t7 KL.

Drift families, fixed before alternative results are inspected:
- `F0_ISOTROPIC_RESIDUAL`: random direction uniformly sampled in the eligible residual space, independent of fit and development. Mandatory negative control for **static ex-ante directional selection**; online methods may learn only from subsequent observations.
- `F1_SPARSE_LOW_VARIANCE`: sparse post-change mean supported on the last four axes of the eligible residual `K=20` universe (or the analogous last `min(4,K)` axes for other `K`); expose the support only to oracle/diagnostics, not online selectors.
- `F2_STRUCTURED_RESIDUAL`: concentrated information on nonconsecutive residual ranks proposed as `{3,9,17,21}` when admissible, with a predeclared positive weight profile and seeded signs; a separate development-family distribution must not reproduce the exact evaluation signs or direction seeds. Declare transfer vs. distribution-shift conditions.
- `F3_MARKET_OR_MIXED`: a separate PC1-inclusive control, not accidentally pooled with residual-only cells.
- `F0_NULL`: no drift, to validate FPR and selection stability.

Normalize Gaussian shifts to **equal full Gaussian information** within a designated comparison stratum; suggested pilot `I* = 0.25` nats/day and sensitivity values `0.10,0.50` *only after preregistered cost/performance review*. Do not choose magnitudes to make the preferred method win. Record both the nominal design KL and the achieved fitted-basis projected KL.

Pilot dimensions: `N∈{32,239}`, `K=20` eligible axes where feasible; optional `K=64` only as a subsequent scaling diagnostic, never silently substituted for the primary `K=20`. Suggested monitoring horizon `H=250`, `α=0.05`, independent `T_fit=1000` (where a fit is required). A fixed `H=500` sensitivity study is allowed only if predeclared with effect size held fixed **independently of H**, not redefined to keep a desired detection rate.

**Role separation per scenario and fit:**
- `FIT_NULL` (PCA/center/variance fit);
- `DEVELOPMENT` (precommitted estimator/window and synthetic stress-prior selection; never used to report test gains);
- `CAL_NULL` (threshold rank calibration);
- `HOLDOUT_NULL` (independent FPR test);
- `TEST_ALT` (alternative delay; never used for any selection hyperparameter);
- optional `OUTER_FIT` replicates for unconditional across-fit uncertainty.

Keep roles independent at trajectory and RNG level. Pair all compared policies on the **same** `HOLDOUT_NULL` and `TEST_ALT` paths. Within a model arm, freeze input generation, alternative and numerical settings across policies. Primary change onset: **monitoring day 1**, with online selection initially uninformed; separately label the `τ*>1` regime with a pre-onset null run-in and correct pre-alarm handling.

## 7. Calibration and inference

Use the established stream-28 `predictive_exchangeable_rank_v2` rule when its assumptions and orientation of the alarm score apply. Read its exact implementation and contract first. Suggested independent full sizes: `n_cal=2000`, `n_holdout_null=2000`, `n_alt=2000` trajectories per frozen scenario/policy; **do not launch these full sizes until an independently reviewed smoke/pilot and resource GO**.

Every distinct `(policy, cost, window, model arm, candidate universe, null fit, detector hyperparameters)` requires its own calibration ID and rank threshold. No in-sample null test, no reuse of a null calibration after policy changes. Target `FPR(H) <= 0.05`; preserve finite-sample predictive-rank qualifications and record independent holdout FPR with confidence intervals.

Primary outcome: `RMST_H = E[min(T,H)]` where `T` is the 1-based first post-onset alarm, with non-detections contributing `H`. Also report fraction detected, censoring fraction, median *conditional on detection* (clearly labeled), and `H`-specific paired delay ratios. Do not call RMST a Lorden ADD or infer an untruncated ADD from severely censored cells.

**Matched-false-alarm claim gate:** compare paired holdout false-alarm indicators; label `ATTAINED_FPR_COMPARABLE` only if a predeclared paired confidence interval for the difference is contained within `[-0.01,+0.01]` (1 percentage point) **and** both methods satisfy the stated null validity criterion. Otherwise report `COMMON_NOMINAL_ALPHA_ONLY`; no "gain at equal FPR" assertion. Record family multiplicity and use an explicitly declared adjustment for simultaneous confirmatory claims; nominal individual intervals alone do not control family error.

Intervals on RMST and gain: paired bootstrap of independent alternative trajectories, **conditional on the frozen fit and calibration**. If results are generalized across PCA fits, perform a second, genuinely independent outer-fit resampling layer and identify the estimand. Do not pretend 2000 paths under one PCA fit represent 2000 independent fitted representations.

**Secondary mechanisms:** estimated and true `q_k` (the latter **offline diagnostic only**); true information captured, true fluid-value regret of `S_t`, `d_t`, axis selection frequencies, selection switching, time to approach oracle subset/value, and wall/CPU/RSS cost. Logs must prove that none of the true-`q` diagnostics feed `ONLINE_*` paths.

## 8. Engineering, resources, and parallel execution

Use the existing `.venv`; preserve all existing sealed files (Article B, E2 J1 CRLF, E3 D8 FAIL, previous PCA benchmark, E4 outputs/manifests). Do not change `experiments/pca_drift_benchmark.py` or its output schema `/2`. Reuse read-only tested functions or create a new module that imports them with explicit contract tests.

Proposed new owned files (Codex may approve small changes only in a documented plan):
- `experiments/pca_info_online.py` — deterministic CLI (`--config`, `--mode smoke|pilot|full`, `--jobs`, `--resume`, `--output-dir`);
- `jepadrift/selection/pca_information.py` — exact sorting/prefix optimization and predictable online estimator;
- `jepadrift/monitors/adaptive_gaussian_mixture.py` — masked scan statistic (NumPy-only);
- `configs/pca_info_online.yaml` — all scenario/estimator/threshold/resource parameters and declared test family;
- `tests/test_pca_info_online.py` — numerical, statistical, non-leakage, replay, and schema tests;
- `docs/sections/pca_info_online.md` — protocol, estimands, coverage matrix, provenance and limitations;
- `results/pca_info_online/<run_id>/` and `figures/pca_info_online/<run_id>/`, with journals under ignored `logs/`.

Register the new canonical prompt in `prompts/streams/INDEX.md` and use the repository's approved `tools/check_prompts.py --sync-master` workflow **only after Codex has checked how it handles a new stream 32**. Do not hand-edit or overwrite historical master-prompt blocks, and do not claim prompt synchronization passed until `make prompts-check` runs.

Define immutable `schema_version=pca_info_online/1` distinct from PCA `/2`. Produce `manifest.json`, `selections.csv` (or partitioned columnar equivalent), `calibration.csv`, `trials.csv`/partitioned trials, `aggregates.csv`, `issues.csv`, and a compact `summary.md`. Per trial retain `policy`, `cost`, `window`, `N`, `K`, candidate universe, model/alternative IDs, drift information ID, fit and basis hashes, calibration/holdout IDs, `first_hit`, censoring, outcome, and deterministic replicate key. For adaptive policies store sufficient time-series selection telemetry or immutable partitions to reconstruct `S_t` and audit causality without exploding global memory. Every number/figure must have a producing script and CSV/manifest identity; no invented curves or post-hoc redrawing.

**Parallelism:** relax the historical E4 single-worker restriction for this *new* experiment, not for archived E4. Use independent **processes** with BLAS/OMP/MKL single-threaded in each worker, deterministic per-replicate seed assignments independent of job count, `spawn`, sorted aggregation, bounded chunks and atomic resumable partitions. Proposed shared-server **pilot default = 8 workers**, production target `12–16` only after throughput/RSS profiling and host-load checks; **24 physical cores are a hard upper planning limit absent exclusive allocation**, not a promise of 24 workers available. Never assume 48 SMT threads provide 48-way linear speedup or promise 20–40×.

Preflight: measure local CPU occupancy/available cores, memory, disk, PID/lock ownership; agree a new bounded **RAM/CPU-hour/wall-clock** envelope with Codex. Do not carry E4's 8 GiB, 30-minute invocation, or 24 CPU-hour cap over as if they were immutable for all experiments. However, do not silently override shared-server limits. Stage `--jobs 1/4/8/12/(16)` throughput and equal-output tests before full launch. Preserve the shared experiment lock while executing numerical campaigns, integration and global tests, as determined by current orchestration rules.

No test artifact >50 MB committed; store large trials locally with hashes, compact FAIR exports, explicit data-handling status. Resume must verify fingerprints and refuse stale/mismatched partitions. A failure/interrupt must not turn missing trials into successes or zero delays.

## 9. Test gates (TDD; hard failure on nonconformity)

1. **Math:** root equation and positive costs; exact top-`q` = forward greedy = exhaustive (small `K`), both costs; tie `d` rule; canonical prefix optimum found by full enumeration; unique-max is not asserted in tie cases.
2. **Time:** perturbing `y_t` or future `y_{>t}` leaves `S_t` unchanged; changing future injection onset or direction cannot change pre-change selections.
3. **Oracle isolation:** replacing true `Δ` after the setup must not change any `ONLINE_*` selected subset before the observation stream changes. Trace every method's input dependencies; forbid oracle metadata, `tau*` and test labels in online call signatures.
4. **Adaptive scan:** static mask matches existing Gaussian-mixture scan; zero counts contribute zero; no retroactive re-scoring of unselected historical data; tiny brute-force reference for every `τ,t`.
5. **Null:** Gaussian exact control with independently calibrated adaptive full pipeline; independent null FPR CI and rank coverage; no reuse of CAL_NULL paths as holdout.
6. **Signal:** synthetic true additive KL vs. top-`q` optimization; fitted LW mismatches labeled as surrogate and joint KL measured separately; Student proxy labels.
7. **Reproducibility:** smoke CSV/manifest scientific fields byte-identical for `--jobs 1` and `--jobs 3` or `8`, apart from expressly excluded wall-time/process metadata; deterministic resume/interruption.
8. **Seals:** J1 native CRLF and SHA, E3 D8 FAIL, PCA `/2`, E4 outputs/hashes unchanged; no 2020+ or real-return read.
9. **Failure controls:** invalid `K`, `d`, empty eligible axes, nonfinite/negative costs, zero-variance eigenvalues, eigenspace nonidentifiability in learned PCA, `γ_M<=1`, invalid window, missing input, inconsistent threshold/fit hashes, empty or stale partitions are refused.
10. **End-to-end:** on a tiny Gaussian diagnostic, true-information oracle's selected *fluid score* meets/exceeds all eligible subsets, but **do not assert** that its realized RMST must dominate every finite-sample policy on every draw.

Report all failed and negative controls. Never silently alter test amplitude, window, horizon, detector or readout to obtain a preferred scientific verdict.

## 10. Execution sequence and authorization gates

**Phase A — Audit/plan, immediately after stream 23 closeout.**
- Confirm actual current `main`, stream-23 scientific and Git closure, and head/worktree cleanliness locally; do not infer closure from an old report.
- Make a file-level call graph and a coverage table (`EXACT_PC_GAUSSIAN`, `FITTED_LW_GAUSSIAN`, `FITTED_LW_T7` × methods).
- Identify source/test conflicts, the proposed seed/key layout, feasible partitioning, RAM and CPU predictions.
- Store a native Claude Code plan for Codex review. No scientific execution in plan mode.

**Phase B — Technical GO and fixtures.**
- Written technical GO from Codex after review; implement TDD math, selector, adaptive scan, CLI, immutable schemas, reproducibility and artifact guards in an isolated worktree.
- No main merge without contract tests and sealed-file verification.

**Phase C — Separate bounded *synthetic* scientific pilot GO.**
- After code review, approve a pilot using independent synthetic paths (proposed 100–200 per role), both selector orders, cost variants, at least one structured residual drift plus isotropic negative control; record actual throughput, FPR, RMST, censoring and estimator diagnostics, with wide uncertainty explicitly labeled `PILOT_ONLY`.
- Choose/preregister primary window and feasible full grid **without looking at confirmatory TEST_ALT results**. If pilot is used for tuning, generate fresh independent test paths/seed domains.

**Phase D — Confirmatory full synthetic GO, distinct.**
- Only after a measured cost forecast and locked preregistration. Independent full calibration/null/alternative cohorts, resource-budget authority, proper FPR and multiplicity gate, scientific report. Publish inconclusive/negative outcomes unaltered.
- Real financial returns, 2020+, JEPA, covariance main experiments and J4 remain out of scope unless independently authorized.

The pilot is valuable even if no full GO is issued. Do not block structural implementation on the availability of real returns.

## 11. Deliverables, acceptance and final report

Produce:
1. An immutable machine-readable specification/config, with a visible *design decision log* distinguishing **SOURCE-BASED** rules from **NEW PROPOSED** settings (window, information amplitude, synthetic covariance spectrum, chosen fit method, numerical budget).
2. Selector and adaptive Gaussian-mixture scan with comprehensive tests and small exact-reference witnesses.
3. A calibrated **pilot** with raw role-separated metrics and null/alternative status, if Phase C authorized; otherwise explicit `AWAITING_SCIENTIFIC_PILOT_GO`.
4. A confirmatory full study only under Phase D GO, not inferred from code completion.
5. A report ranking the evidence: oracle upper reference; static ex-ante selection; online non-oracle; canonical prefix; variance-only; full-K. Separately show the cost ablation. No claim that oracle success validates the deployable method.
6. A release note for Codex: commit ids, tested configurations, seed/identity hashes, failed/blocked cells, unit-safety of the null thresholds, CPU-hours, wall time, memory and artifacts.
7. A manuscript-ready, English, self-contained methods paragraph and limitations paragraph **only after results exist**.

**Success is a qualified comparison, not a forced gain.** A negative or null result remains a valid scientific answer. A statistically comparable `ONLINE_INFO_MIX` advantage over `ONLINE_PREFIX_MIX` and strong baselines is the central positive finding; report uncertainty and transfer limits.

## 12. Verification commands (adjust only under documented Codex plan)

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42
.venv/bin/python -m pytest -q tests/test_pca_info_online.py
.venv/bin/python experiments/pca_info_online.py --config configs/pca_info_online.yaml \
    --mode smoke --jobs 1 --output-dir results/pca_info_online/smoke_j1
.venv/bin/python experiments/pca_info_online.py --config configs/pca_info_online.yaml \
    --mode smoke --jobs 8 --output-dir results/pca_info_online/smoke_j8
# Compare deterministic scientific artifacts by canonical content/hash, not by run-specific path or wall-time.
make prompts-check
make check
```

Before importing NumPy in worker processes, verify single-thread BLAS environment. `--mode pilot` and `--mode full` require their own explicit scientific authorization and measured resource budget.

**Non-goals:** interval search, daily PCA eigenbasis refit, retroactive E4 repair, covariance information greedy main claim, historical crash backtests, any new JEPA training.
