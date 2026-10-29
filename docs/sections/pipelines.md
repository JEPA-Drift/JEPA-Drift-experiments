# Pipelines (stream 07) — P2-C, P3-C, P3-D, P3-CS, P4-C, P4-D, P7 and their calibrations

`jepadrift/pipelines.py` runs every cross-sectional pipeline through the same detection stack; only the representation
changes. `jepadrift/monitors/calibration.py` holds the threshold calibrations (numpy only), and the exact lattice
reading stays `jepadrift.monitors.lattice.select_threshold` (stream 04). Representations reach the monitors as arrays
(a returns panel X or a Z dict), never as objects: `pipelines.py` is the only module that imports both
`jepadrift.representations` and `jepadrift.monitors`.

## Registry and execution

`PIPELINES[id] = (representation, stream_builder, detector, calibration)`, four functions per pipeline that switch
on `spec["reading"]`.

| function | contract |
|---|---|
| `make_spec(pipeline, **kw)` | complete spec: common keys (`pipeline`, `reading`, `dataset`, `H` = 750, `gamma` = 20, `alpha`) and the pipeline's defaults, updated by `kw`; `ValueError` on an unknown key, pipeline, reading or value |
| `run_id(spec)` | first 16 hex digits of the SHA-256 of `json.dumps(spec, sort_keys=True)` |
| `split_rows(dates, splits)` | rows `[start, stop)` of `pretrain`, `calib` and `pre_monitor` (first pretrain day to last calib day) of a `splits.yaml` dict, plus `dates` |
| `fit_pipeline(spec, X_fit, splits, key=None)` | frozen state: representation fitted on the calib rows of `X_fit`, then the reading's calibration on the null rows of `X_fit` |
| `run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None)` | one alarms row per record `{"seed", "tau_star", "family"[, "delta"]}`; `data` is X (T, N) float64 or a Z dict `{"z_odd", "z_even"}` |
| `null_check(specs, X, splits, reps, key)` | D6 null replicates, returns (alarms rows, one summary row per spec) |
| `python -m jepadrift.pipelines --pipeline P --dataset D --null-check --reps n` | CLI of `null_check` |

**Fit rows.** `X_fit` is supplied by the caller and must be drift-free (Article C, Proposition "Absorption"). For D6
experiments it is a symmetrization independent of the monitored ones, so that the fitted directions do not depend
on the monitored signs and Lemma 2 stays exact. `run_pipeline(state=None)` fits on `data` itself and refuses any
injected record whose onset precedes the end of the calib rows.

**Monitoring.** The monitor starts at `tau_star` with its state reset (Lorden's worst case) and reads the rows
`[tau_star, tau_star + H)`. Only the P2-C bootstrap reading also reads the `H_ref` rows before `tau_star` (its
reference median and spread), and only frozen calib statistics enter the other streams. Records are stacked in chunks of
`CHUNK = 64` and every detector runs vectorized; `n_jobs > 1` maps the chunks on a spawn-context process pool, in
submission order. Every random draw is keyed: tie-breaking coins on `SeedSequence([*seed, 7])`, calibration on
`key + [0]` (and `key + [1, i]` for the i-th P2-C bootstrap window), so rows do not depend on `n_jobs` nor on how the
records are split (`test_parallel_and_partition_invariance`).

**`alarms.csv`.** Columns `run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold,
reading`, written by `save_fair_csv` (`%.17g`):
- `seed`: the record's integer key joined by `-`; `family`: `F1`…`F4-*`, or `H0` for a null run, where `tau_star`
  is the start of the monitored window;
- `alarm_index`: row of the first alarm in `[tau_star, tau_star + H)`, or −1;
- `delay = alarm_index − tau_star + 1`: monitored days up to and including the alarm (T_γ of Lemma 1, the E2 and
  `floors` convention); NaN without alarm. Article B's delays (`bilateral_delay`) are this value minus one
  (`C-pipe-delay`);
- `threshold`: γ for an anytime-valid reading, λ for a CUSUM reading.

The CLI also writes `runs_<pipeline>_<dataset>_null.json`: for each `run_id`, the spec, the null summary and the
frozen state (thresholds, ρ̂ and K_eff, Γ^op, σ̄, independence test, representation hash and fit dates).

## Readings and null guarantees

| reading | `threshold` | guarantee under H₀ | target of the H₀ tests (`null_target`) |
|---|---|---|---|
| `anytime-valid`, e-detector (P2-C, P3-C, P4-C, P3-CS b) | γ: alarm at log M ≥ log γ | ARL₀ ≥ γ [Shin, Ramdas & Rinaldo, 2024]; P₀(alarm ≤ H) ≤ H/γ (Lorden's decomposition) | FPR ≤ upper end of the 99 % region of min(1, H/γ), tested at γ = 20H |
| `anytime-valid`, e-process (P3-CS a) | γ | P₀(sup M ≥ γ) ≤ 1/γ [Ville, 1939] | FPR ≤ upper end of the 99 % region of 1/γ, tested at γ = 20 |
| `anytime-valid` (P7) | γ: CUSUM of the Gaussian LLR at ln γ | ARL₀ ≥ γ under the Gaussian i.i.d. model of Σ̂ only | none: P7 is a bound |
| `exact` (P3-C, P4-C, one channel) | lattice threshold (midpoint) | FPR(H) equal to the exact level, or ARL₀ = γ | two-sided 99 % region of the exact level |
| `bootstrap` (P2-C, P3-D, P4-D) | λ: quantile of null-window maxima | FPR(H) ≈ α over the window population; for P3-D and P4-D, over the calib windows that set λ (in sample) | two-sided 99 % region of α, calibration noise included for P2-C; the P3-D/P4-D D6 check re-reads those windows and cannot estimate an out-of-sample FPR (`C-P4D-null-insample`) |
| `randomization` (P3-CS a) | λ: quantile of sign-flipped null-window maxima | FPR(H) ≈ α; exact conditionally on the magnitudes under symmetry without leverage | two-sided 99 % region of α, calibration noise included |
| `budget` | — | τ_γ = ln γ / I (Lemma 1, exact) | analytic (`jepadrift/floors.py`), no monitor |

The 99 % region is p ± z√(p(1 − p)(1/n + 1/n_cal)), z = 2.5758293035489004; the 1/n_cal term (N_cal or B null draws)
is the variance of the level reached by an empirical quantile, and the overlap of windows is ignored
(`C-pipe-null-targets`). An e-detector at γ = 20 over 750 days alarms on most null paths (FPR 0.71 for P3-C, 0.29 for
P2-C in the D6 probes of `prompts/plans/plan-07.md`), as its ARL₀ guarantee allows; E3 measures ARL₀ against γ.

## Pipelines

| id | representation | stream | detector | calibration | readings |
|---|---|---|---|---|---|
| P2-C | columns `composition_for(K, N)` of X (K = N by default) | bootstrap: `fraction_stream` of the signs recentred on each window (median and std of the `H_ref` days before τ*); anytime-valid: x = 2·mean of the raw `exact_sign_stream` | bootstrap: strict bilateral CUSUM, δ = 0 (`bilateral_delay_vec`); anytime-valid: `log_edetector(x, "cusum")` | `N_cal` calls of `worker_null_window_real` on the null rows, then `bootstrap_threshold`; `sign_diagnostics` | `bootstrap` (default), `anytime-valid` |
| P3-C | `PCAOrthogonal(K, mode, shrinkage)`; `channels` ∈ {all, market, residual, [k]} | x = 2·`exact_sign_stream(z_odd[:, channels])` | anytime-valid: `log_dictionary_edetector(x, "cusum")`, equal weights on all channels; exact: strict bilateral CUSUM, δ = 0.1, one channel; option `mixture_s2` | exact: `select_threshold(α, H=H)` or `select_threshold(1/γ, H=None)` | `anytime-valid` (default), `exact` |
| P3-D | `PCAOrthogonal`, even head | q_t = (Σ_{k residual} z_even[t, k] − D)/√(2D) (`residual_energy`) | strict one-sided CUSUM, δ = 0.5 | all windows of length H of the calib rows, `required_threshold(·, 0.5, α, "fpr", H)`; λ_iid on i.i.d. (χ²_D − D)/√(2D); Γ^op = λ_req/λ_iid | `bootstrap` |
| P3-CS | `DegreeZero(b, K, mode)`; `variant` ∈ {a, b} (b by default) | (a) pivots z_odd ∈ [−1, 1]; (a, randomization) pivots over their calib RMS; (b) exact signs of z_odd and ‖Px‖ = z_even | (a) `log_average_betting_eprocess`; (a, randomization) first alarm over directions of `bilateral_delay_vec(δ = 0)`; (b) CUSUM e-detector with predictable stakes | randomization: `null_windows(flip=True)`, B = 2000, `bootstrap_threshold`; (b) σ̄ | `anytime-valid` (a, b), `randomization` (a) |
| P4-C | `IPCA(K="select", cash_neutral=None)`; C_t from `splits["C"]` | as P3-C, on the IPCA z_odd | as P3-C | as P3-C | `anytime-valid` (default), `exact` |
| P4-D | `IPCA`, even head | `residual_energy` of the IPCA z_even | as P3-D | as P3-D, calib rows transformed with C | `bootstrap` |
| P7 | Σ̂ = Ledoit–Wolf of the calib rows of `X_fit` | ℓ_t = w_tᵀx_t − ½w_tᵀΔ_t, w_t = Σ̂⁻¹Δ_t, Δ_t = `record["delta"]` | `cusum_trajectory_vec(ℓ, 0)`, alarm at S ≥ ln γ | none | `anytime-valid` (bound) |

Constants: `H_REF, H_DET, N_CAL, TARGET_FPR = 500, 750, 20000, 0.05` (R15 l.194–199), `MASTER_SEED = 42` (R15
l.201), `B_FLIPS = 2000`, `HALF_LIFE = 20`, `STAKE_CAP = 0.5` (prompt 07, item 6), `PIVOT_BETS = (0.1, 0.25, 0.5, 0.9)`,
`SIGN_DELTA = 0.1` (P1-C/C), `ENERGY_DELTA = 0.5`, `GAMMA = 20`, `CHUNK = 64`.

### P2-C — pooled signs (port of Article B R15)

- **Composition.** `composition_for(K, K_max)` is R15's frozen draw of the pooled assets, carried verbatim with its
  MD5 % 2³² seed: on D2 the pooled assets are exactly R15's (`C-P2C-port`).
- **Bootstrap reading (Article B).** On the window `[τ* − H_ref, τ* + H)`, each asset is recentred on the median and
  scaled by the standard deviation of its `H_ref` reference days, and f_t is the `fraction_stream` of the result: the
  lines of `worker_null_window_real` with a given start (`test_p2c_recentred_stream_matches_worker`). The strict bilateral
  CUSUM with δ = 0 alarms when S > λ_boot, the (1 − α) quantile of the maxima of `N_cal` null windows drawn uniformly
  in the null rows (`pre_monitor` before J4; R15 read the whole panel), one `SeedSequence` per draw.
- **Anytime-valid reading.** The fraction of raw exact signs (zero returns broken by fair coins; 2864 on D2 before
  2020) centred at 0: every average of exact bits centred at 1/2 is a bounded martingale difference under H₀, so the
  betting e-detector is valid whatever the cross-sectional correlation.
- **Diagnostics.** `sign_diagnostics(eps_K)` (R15 l.889–902) returns ρ̂_sign (mean pairwise correlation of the signs
  recentred on their median), K_eff_meas = 1/(4 Var f_t) and K_eff_ana = K/(1 + (K − 1)ρ̂), stored in the state.

### P3-C — PCA-orthogonal signs

Exact sign stream per channel, market (column 0) plus the residual directions of stream 06. Default detector: the
equal-weight dictionary average of CUSUM e-detectors over all channels (Article C, Remark "Combining channels"). The
exact reading monitors one channel with the lattice (no exact level exists for several dependent channels). The
option `mixture_s2 = s²` replaces the residual block by the sub-Gaussian mixture of Proposition 3, combined with the
market e-detector with weights |market|/D and |residual|/D; it is allowed only if every pair of residual sign streams
of the calib rows has |ρ̂| < 3/√T (`cross_independence`), else `ValueError`. On D2 the test fails in both modes
(factor: 1 of 10 pairs, max |ρ̂| = 0.1308 against 0.0978; full: 13 of 4560): the option is unavailable there, and in
full mode the literal rule fails by multiplicity alone (`C-P3C-mixture-gate`).

### P3-D — residual energy

q_t standardizes the residual energy of the whitened coordinates; the strict CUSUM uses δ = 0.5. Sign flips leave an
even statistic unchanged, so the threshold comes from the null windows of the calib segment, all enumerated. The state
reports λ_req, λ_iid, Γ_z^op = λ_req/λ_iid and Γ^spec of q on the calib rows. Windows longer than the calib segment raise
`ValueError`: on D2 and `d3_239` (941 calib days) an E1 horizon of 2000 days needs a decision in stream 12
(`C-P3D-windows`).

### P4-C and P4-D — IPCA (stream 17)

P4-C and P4-D reuse the streams, detectors and calibrations of P3-C and P3-D on the IPCA representation
(`docs/sections/ipca.md`). C_t travels in `split_rows(dates, splits, C)` (key `"C"`, aligned on the rows);
`fit_pipeline` calls `pretrain` on the pretrain rows, then `fit` on calib, with C; the CLI masks X by `in_universe`
and loads the four continuous characteristics. Monitoring takes a Z dict (`rep.transform_panel(X, C)`); an X panel
without C is refused (`needs C_t`). D6 null checks on `d3_239` (500 replicates, H = 750; `results/ipca/`,
`logs/ipca/`):

| spec | FPR | target | 99 % region | verdict |
|---|---|---|---|---|
| P4-C anytime-valid, dictionary, γ = 15 000 | 0.0020 | ≤ 0.05 | upper end 0.0751 | PASS |
| P4-C exact, channel 0 / channel 1 | 0.0420 / 0.0460 | = 0.043947 | [0.0203, 0.0676] | PASS |
| P4-D bootstrap, λ = 57.4642 (λ_iid = 12.3047, Γ^op = 4.670) | 0.0000 | ~ 0.05 | [0.0249, 0.0751] | FAIL |

The P4-D check re-reads the 192 calib windows that set λ, with no fresh D6 randomness in the even energy stream; all
192 windows share one CUSUM peak just below λ (`C-P4D-null-insample`). P4-D's FPR is therefore uncalibrated, and
neither P4-D nor the corresponding P3-D window diagnostic is a calibrated reference for J4 without a separately
approved control.

### P3-CS — degree-0 cross-section

- **(a) Pivot.** s_{t,k} = u_kᵀPx_t/‖Px_t‖ ∈ [−1, 1] (DegreeZero z_odd). Anytime-valid: the e-process
  `log_average_betting_eprocess`, mean over the bets ±`PIVOT_BETS` and the directions of Π(1 + λ s_{t,k}). Fixed-design
  CUSUM: first alarm over directions and sides of the bilateral δ = 0 CUSUM of the pivots divided by their calib RMS,
  threshold by sign-flip randomization (B = 2000 null windows, one Rademacher sign per day shared by all directions,
  which keeps their dependence).
- **(b) Predictable stake.** σ̄ = calib median of ‖Px_t‖; c_j = 2η₀_j σ̄ (η₀ ∈ `EDETECTOR_ETA0`); σ̂ restarts at σ̄
  on the first monitored day and follows an EWMA of half-life 20; λ_{t,j} = min(0.5, c_j/σ̂_{t|t−1}) (`stakes`). The
  CUSUM e-detector averages two sides, the four magnitudes and the directions; it is `log_dictionary_edetector` on
  Y = 2λ_t x_t with η₀ = 0.25 (factors 1 ± λ_t x_t, `test_p3cs_stakes_predictable`). On a median day the stake equals
  P3-C's bet.

The pivots are small in low-variance directions (median |p| = 0.057 in full mode on D2): with bets |λ| ≤ 0.4 the
e-process detected a strong F2 drift in 35 % of the probe replicates, and the unstandardized CUSUM in 17.5 %, against
100 % with the defaults (`C-P3CS-design`).

### P7 — oracle

w* = Σ̂⁻¹Δ with Δ known (the `delta` returned by `injection.inject`, time-varying for F2); CUSUM of the Gaussian
log-likelihood ratio at ln γ. P7 is reported as a bound only; its Σ̂ is the injector's covariance estimator on the
calib rows. Rebuilding Δ from `tau_star.json` is deferred: B·direction does not reproduce `direction_sha256` bit for
bit.

## Calibrations (`jepadrift/monitors/calibration.py`)

| calibration | functions | exactness |
|---|---|---|
| window bootstrap, port of R15 | `worker_null_window_real`, `worker_race_h1_real` (verbatim R15 l.431–478), `bootstrap_threshold` (quantile rule of R15 l.1062) | approximate: one real panel, overlapping windows |
| sign-flip randomization | `null_windows(x, length, n, rng, flip=True)`: windows drawn one by one, one Rademacher sign per day | exact conditionally on the magnitudes, under conditional symmetry without leverage |
| exact lattice | `lattice.select_threshold` (stream 04) | exact for a two-point stream |

## Article B R15 identity (prompt 07, item 3)

`python experiments/identity_articleB.py` recomputes R15 (b) from the D2 loader (bit-identical to
`R15_panel_logreturns.csv`) and writes `results/identity/articleB_R15.csv`, 56 cells, all within the relative gate
1e-12, 54 bit-identical. The full 2005–2025 panel serves this reproduction only.

| K | ρ̂_sign | K_eff_meas | λ_boot | FPR_boot | race at c = 0.25: DetRate, ADD |
|---|---|---|---|---|---|
| 5 | 0.2577415599534342 (bit-identical) | 2.461882379915166 | 34.2 | 0.053 | 1.0, 278.112 |
| 10 | 0.25904514047705113 (2.1e-16) | 3.006299797776757 | 24.599999999999966 | 0.0515 | 1.0, 192.467 |
| 20 | 0.28810195766064206 (bit-identical) | 3.091784464945219 | 19.900000000000006 | 0.05 | 1.0, 161.663 |

The compositions (35 cells) are equal; λ_boot, FPR_boot and the race use R15's own seeds (`get_deterministic_seed`,
verbatim). The one-ulp difference at K = 10 comes from the summation order of `np.corrcoef` (BLAS).

## Reference null check

`python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500` (rows 2005-01-04 to
2019-12-31; `results/pipelines/alarms_P3-C_d2_us97_null.csv`, `logs/pipelines/null_P3-C_d2_us97.log`), verdict PASS:

| spec | FPR | target | 99 % region |
|---|---|---|---|
| anytime-valid, dictionary, γ = 15 000 | 0.0000 | ≤ 0.05 | upper end 0.0751 |
| exact, channels 0 to 5 | 0.0300, 0.0320, 0.0460, 0.0400, 0.0400, 0.0380 | = 0.043947 | [0.0203, 0.0676] |

## Test diagnostics (not reported in the paper)

- `test_null_fpr_d6` (D2, 2000 D6 replicates, H = 750): exact channels 0.0385–0.0505 (level 0.043947); P3-C dictionary
  at γ = 15 000: 0.0015; P2-C anytime-valid (K = 97) at γ = 15 000: 0.0000; P3-CS (a) e-process at γ = 20: 0.0205;
  P3-CS (a) randomization: 0.0640 in [0.0322, 0.0678].
- `test_p2c_bootstrap_fpr` (raw D2, K = 20): λ_boot = 20.0525, held-out FPR 0.0505 in [0.0368, 0.0632]. On the rows before
  2020, ρ̂_sign = 0.2477, 0.2946, 0.2679 and K_eff_meas = 2.51, 3.04, 3.64 for K = 5, 20, 97.
- `test_strong_f2_detected` (SYM-D2, F2 with SR = 8, synthetic constant characteristics, H = 2000, γ = 20, 50
  replicates): detection 100 % for P3-C (full), P3-CS (b), P7, P3-CS (a) e-process and randomization; mean delays
  373, 446, 15, 1164 and 1147 days, maxima 913, 945, 56, 1782 and 1667.
- P3-D on the D2 calib (H = 500): Γ^op = 7.64 in factor mode (λ_req = 76.70, λ_iid = 10.04) and 25.19 in full mode;
  Γ^spec = 1.56 and 2.73. Windows over 2005–2019 would give Γ^op ≈ 191 and 2346 (the 2008 regime).

## Tests (`tests/test_pipelines.py`, `tests/test_identity_articleB.py`)

| guarantee | test |
|---|---|
| verbatim ports (R15, fair harness) | `test_ported_sources_byte_identical` |
| calibration helpers | `test_null_windows_draw_order_and_flip`, `test_bootstrap_threshold_rule`, `test_average_betting_eprocess` |
| alarms schema, one row per record | `test_alarms_schema_one_row_per_record` |
| independence from `n_jobs` and record partition | `test_parallel_and_partition_invariance` |
| X and Z inputs agree | `test_x_and_z_inputs_agree` |
| bounds, absorption guard, monitor reset | `test_guards_and_monitor_reset` |
| P2-C port and bootstrap at 5 % | `test_p2c_recentred_stream_matches_worker`, `test_p2c_bootstrap_fpr` |
| R15 identity | `test_r15_identity_rng_free`, `test_r15_bootstrap_identity_k5` |
| P3-D energy and Γ^op | `test_p3d_energy_and_gamma_op` |
| P4 wiring: defaults, C path, Z dict, lattice level, Γ^op of P4-D | `test_p4_wiring` |
| P3-CS stakes, e-process and randomization | `test_p3cs_stakes_predictable`, `test_p3cs_pivot_eprocess_and_randomization` |
| FPR under H₀ on D6 | `test_null_fpr_d6` |
| strong F2 detected | `test_strong_f2_detected` |
| mixture option gate | `test_cross_independence_gate` |
| CLI determinism | `test_cli_null_check_smoke` |

No test reads a row dated 2020-01-01 or later, except the R15 identity (reproduction of Article B's published values).

## Deferred

- The rank variant of P3-CS (a rank pivot carries no ‖Px‖ for the stake of (b)).
- Rebuilding P7's Δ from `tau_star.json`.
- An exact reading over several dependent channels.
- ARL₀ checks of the e-detectors (E3).

## Verification

```bash
pytest -q tests/test_pipelines.py tests/test_identity_articleB.py
python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500
python experiments/identity_articleB.py
```

## References

- [Page, 1954, Continuous inspection schemes]
- [Lorden, 1971, Procedures for reacting to a change in distribution]
- [Ville, 1939, Étude critique de la notion de collectif]
- [Shin, Ramdas & Rinaldo, 2024, E-detectors: a nonparametric framework for sequential change detection]
- [Waudby-Smith & Ramdas, 2024, Estimating means of bounded random variables by betting]
- [Künsch, 1989, The jackknife and the bootstrap for general stationary observations]
- Article B, R15 (`experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py`).
- Article C, Section 3 (`paper/sec3_theory.tex`): Lemma 1 (evidence budget), Lemma 2 (whitening by an odd encoder),
  Proposition 3 (dimension tax), Remark "Combining channels", Proposition "Absorption".
