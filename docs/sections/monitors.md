# Monitors (stream 04) — univariate core, exact lattice, e-detectors, Article B port

`jepadrift/monitors/` is the detection stack shared by every pipeline. It imports numpy and the
standard library only, holds no random generator (a `Generator` is always passed in), and computes
in float64 along the last axis of `(..., T)` arrays. `jepadrift/stats/garch.py` (scipy) carries the
GARCH primitives of Article B. `experiments/identity_articleB.py` checks the port against the Article
B outputs.

## Ported code (verbatim, Article B @ `a05f0d9`)

| function | Article B source | lines | here |
|---|---|---|---|
| `strict_cusum`, `get_multiple_alarms`, `get_cusum_trajectory` | `experiments/R01_real_world_backtest/exp_R01_real_world_backtest.py` | 110–142 | `jepadrift/monitors/cusum.py` |
| `bilateral_delay`, `cusum_max_bilateral` | `experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py` | 350–360 | `jepadrift/monitors/cusum.py` |
| `_garch_nll`, `fit_garch_qmle`, `compute_gamma_exact` | R01 (above) | 72–108 | `jepadrift/stats/garch.py` |
| `build_mixture_kernel` | `experiments/R09_eprocess_anytime/exp_R09_eprocess_anytime.py` | 317–336 | `jepadrift/monitors/eprocess.py` |
| `wilson_ci` | R01 (above) | 144–148 | `experiments/identity_articleB.py` |
| `save_fair_csv` | `experiments/common/fair_harness.py` | 84–88 | `jepadrift/pipelines.py` (stream 07; imported by `experiments/identity_articleB.py`) |
| `fraction_stream` | `experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py` | 368–370 | `jepadrift/monitors/streams.py` (stream 07) |
| `worker_null_window_real`, `worker_race_h1_real` | R15 (above) | 431–478 | `jepadrift/monitors/calibration.py` (stream 07) |
| `composition_for` | R15 (above) | 409–426 | `jepadrift/pipelines.py` (stream 07) |
| `get_deterministic_seed` | R15 (above), carried by R15 from R13 | 377–394 | `experiments/identity_articleB.py` (stream 07) |

`tests/test_identity_articleB.py::test_ported_sources_byte_identical` compares the source text of each
function (its `ast.get_source_segment`) with the Article B file, byte for byte; a comment after the last statement
of a function, such as the one of R15 l.370, lies outside the segment and is not carried. R15's own copy of `strict_cusum` (l.343–348) differs
from R01's in formatting only, and the same test checks that the two ASTs are equal. `make check` runs
pyflakes on every file except `jepadrift/stats/garch.py`: the verbatim `fit_garch_qmle` binds an
unused exception name (R01 l.99), and changing it would break byte identity (`C-garch-pyflakes`).

## Constants ported

| constant | value | Article B source |
|---|---|---|
| `P1["P1-C/B"]` (Concept, Article B) | label stream `1{r > 0} − q̂`, bilateral strict CUSUM, δ = 0.1, λ = 10; q̂ on 2018-01-02…2019-12-31 (real mode) or on the 250 days before the onset (injection mode) | R01 l.260–267, 304–305, 365, 374–376 |
| `P1["P1-D/B"]` (Data, Article B) | energy stream `(r² − μ̂)/σ̂`, one-sided strict CUSUM, δ = 0.5, λ = 65·Γ̂, Γ̂ fitted once on 2018–2019 (deviation B `R01-gamma-hat-refit`); trailing moments on 250 days | R01 l.271–273, 298–299, 363–370 |
| `P1["P1-C/C"]` (Concept, Article C) | exact sign stream `1{y > 0} − 1/2`, bilateral strict CUSUM, δ = 0.1, λ from the lattice (`select_threshold`, rule `at_or_below`) | Article C, Lemma 2 |
| MIX | H = 5000; starts `np.linspace(0, H − 1, 16, dtype=int)`; η₀ ∈ {0.05, 0.10, 0.15}; sides ±1; weight 1/96 | R09 l.160–176 |
| R08 lattice | δ = 0.1: steps +0.4 / −0.6, i.e. +2 / −3 units of 2δ = 0.2 | R08 l.185–188 |

## API

**`cusum.py`.** The five ports above, plus vectorized versions over the last axis that give the same
results bit for bit: `cusum_trajectory_vec`, `strict_cusum_vec` (−1 when no alarm),
`bilateral_delay_vec`, `cusum_max_bilateral_vec`, and `multiple_alarms_vec` (boolean mask; S⁺ and S⁻
restart at 0 after each alarm, as in `get_multiple_alarms`). These versions raise `ValueError` on
non-finite input, because Python's `max(0.0, nan)` returns 0.0 while `np.maximum` propagates NaN.

**`streams.py`.**
- `label_stream(r, q_hat)` returns `(r > 0) − q̂`.
- `exact_sign_stream(y, rng)` returns `1{y > 0} − 1/2`; each tie `y == 0` gets a fair coin from `rng`.
- `energy_stream(r, mu, sigma)` returns `(r² − μ)/σ`.
- `fraction_stream(eps)` (R15, stream 07) returns the cross-sectional fraction of positive entries of `eps` (K, T)
  minus 1/2, the pooled-sign stream of P2-C.

The first three raise `ValueError` on non-finite input.

**`lattice.py`.** This module computes the exact law of a CUSUM whose stream takes two values, with
integer steps +a/−b in lattice units and P(S⁺ steps +a) = q.
- Notation: M_H = max over t ≤ H of S⁺_t (`sided=1`) or of max(S⁺_t, S⁻_t) (`sided=2`, joint chain
  (S⁺, S⁻)). The strict rule alarms when S > L, the weak rule when S ≥ L.
- `lattice_steps(delta)` returns (a, b, unit) for the exact stream with reference δ. It computes them
  in exact rationals from the decimal form of δ (δ = 0.1 → (2, 3, 0.2)).
- `exceedance(H, L, a, b, q, sided, comparison)` returns P(M_H > L) or P(M_H ≥ L). It runs an
  absorbing-chain dynamic program that generalizes R08 l.521–549.
- `arl0(L, a, b, q, sided, comparison)` solves (I − Q)t = 1 exactly, on (L+1)^sided states. Bilateral
  thresholds are therefore limited to L ≤ 99, which covers γ up to about 10⁵.
- `attainable_levels(H=None, delta, sided, q, comparison, min_level=1e-3)` returns rows (λ = L·unit,
  level). The level is P(M_H > λ) by horizon H, or 1/ARL₀ when H is None.
- `select_threshold(nominal, rule="at_or_below", comparison="strict", *, H, delta, sided, q)` returns
  `units` (L), `lam` (L·unit), `threshold`, the exact `level` and `unit`. For an ARL₀ target γ, pass
  `nominal = 1/γ` and `H=None`.

The `threshold` is a midpoint (`C-lattice-midpoint`): (L + ½)·unit under the strict rule and
(L − ½)·unit under the weak rule, to use as `S > threshold` in floating point. Sums of +0.4/−0.6
accumulate rounding error, so a float CUSUM compared at the lattice point itself implements the weak
rule on some paths (deviation B `R08-delivered-level-above-nominal`). The midpoint leaves half a unit
of margin, and `test_midpoint_threshold_reproduces_lattice_rule` checks the equivalence path by path.
`P1-C/C` and the GARCH control below use `sel["threshold"]`.

Examples:

| H | rule | L | λ | threshold | exact level |
|---|---|---|---|---|---|
| 5000 | at_or_below | 57 | 11.4 | 11.5 | 0.043428228893176074 |
| 5000 | at_or_above | 56 | 11.2 | 11.3 | 0.051020717214682557 |
| 1000 | at_or_below | 47 | 9.4 | 9.5 | 0.042898 |

The H = 5000 rows are the R08 exact law; Article B's v87 manuscript prints λ* = 11.4.

**`gamma.py`.**
- `gamma_spectral(x, L=None)` returns Γ̂ = 1 + 2 Σ_{k≤L} (1 − k/(L+1)) ρ̂(k), with
  L = ⌊4(n/100)^{2/9}⌋ by default.
- `required_threshold(paths, delta, target, criterion, H)` returns the smallest λ for the strict
  one-sided CUSUM on the given null paths. Criterion `"fpr"` asks for a false-alarm rate by H ≤ target;
  criterion `"arl0"` asks for a mean run length (censored at T) ≥ target. The search is a monotone
  bisection, and it raises `ValueError` when the target cannot be met.
- `gamma_operational(...)` returns Γ^op = `required_threshold(...)` / λ_iid.

**`eprocess.py`.** Inputs are x ∈ [−1, 1]; for the exact sign stream, x = 2s. Every function returns
natural logarithms, so strong drifts cannot overflow.
- `log_betting_eprocess(x, lam)` returns log Π(1 + λ_t x_t), with |λ_t| < 1. The caller must keep
  λ_t predictable (computed from x before t).
- `log_mix_eprocess(x)` is the R09 MIX mixture. Bit = x > 0; each component holds 1 before its start.
- `log_edetector(x, kind)` averages 8 SR (M_n = (1 + M_{n−1}) f_n) or CUSUM (M_n = max(1, M_{n−1}) f_n)
  e-detectors, with f_n = 1 + λx_n and bets λ = 2·side·η₀, η₀ ∈ {0.05, 0.10, 0.15, 0.20}, sides ±1
  (R09's 2(½ ± η₀)). An alarm at M_n ≥ γ gives ARL₀ ≥ γ [Shin, Ramdas & Rinaldo, 2024].
- `log_dictionary_edetector(x)`, with x of shape (..., T, K), averages the e-detectors over K
  directions. The average is valid whatever the dependence between directions (Article C, Remark
  "Combining channels").
- `log_subgaussian_mixture(z, s2)` is the closed-form mixture of Proposition 3:
  log L_n = −(D/2) log(1 + n s²) + s²‖S_n‖²/(2(1 + n s²)). It is valid only if the coordinates are
  independent under H₀.
- `log_average_betting_eprocess(x, lam)` (stream 07), with x of shape (..., T, K) and bets lam (J,), |λ| < 1,
  returns the log of the mean over bets and directions of Π(1 + λ_j x_{t,k}): an e-process, the P3-CS (a) pivot
  monitor.
- `first_alarm(log_m, gamma)` returns the first index with log M ≥ log γ, or −1.

**`calibration.py`** (stream 07; `docs/sections/pipelines.md`). `worker_null_window_real` and `worker_race_h1_real`
(R15 verbatim), `bootstrap_threshold(null_maxima, alpha)` (the R15 quantile rule) and
`null_windows(x, length, n, rng, flip=False)` (random null windows, optionally sign-flipped day by day).

## Monte Carlo controls (prompt 04, item 10)

`tests/test_monitors.py` runs these controls with fixed seeds (`SeedSequence([4, …])`). Their figures
are test diagnostics and are not reported in the paper.

- **Lattice-calibrated sign CUSUM on GARCH(0.08, 0.90)-t₇.** The background is `Garch` from
  `experiments/e2_floor_validation.py`; the run uses 20,000 paths, H = 1000 and `P1-C/C` with
  nominal 5 %. Selected L = 47 (λ = 9.4, threshold 9.5), exact level 0.042898.
  - Monte Carlo FPR: 0.04275, inside the 99 % binomial acceptance region [0.03925, 0.04665].
  - A threshold one lattice step lower (the weak rule at L) gives 0.05115, outside that region.
- **e-detectors on fair coins.** The run uses 2,000 paths and T_max = 60γ. A censored mean is a lower
  bound on ARL₀.

| kind | γ | mean run length | SE | margin over γ | censored |
|---|---|---|---|---|---|
| SR | 20 | 21.87 | 0.11 | +9.3 % | 0 |
| SR | 100 | 110.91 | 1.36 | +10.9 % | 0 |
| CUSUM | 20 | ≥ 526.0 | 8.5 | — | 12.0 % |
| CUSUM | 100 | ≥ 2772.6 | 45.1 | — | 16.3 % |

The SR margin is thin by construction. For the SR e-detector, M_n − n is a martingale under H₀, so
E∞[τ] = E∞[M_τ], and ARL₀ exceeds γ only by the expected overshoot of M_τ above γ. With the fixed
seeds, the observed means lie 17 and 8 standard errors above γ. If a platform change makes this test
fail, record the deviation; do not rerun with new seeds until it passes.
- **Ville checks.** For each process, the share of paths that reach 20 at any time, against the bound
  1/20 = 0.05 (the tests allow 3 standard errors):

  | process | share reaching 20 |
  |---|---|
  | betting e-process, λ = 0.3 | 0.040 |
  | MIX over 5000 steps | 0.046 |
  | sub-Gaussian mixture, D = 5, s² = 0.02 | 0.042 |

## Identity controls (prompt 04, item 8)

`experiments/identity_articleB.py` rebuilds the six R01 output tables (phases 1–3, l.257–416) with the
ported primitives and the P1 constants. It also recomputes the `exact_level` column of
`R08_lattice_exact_law.csv`.

Each cell is compared with Article B's CSV, read with `round_trip`:
- non-float cells must be equal;
- float cells must be bit-identical, or within a relative difference of 1e-12;
- NaN equals NaN.

The script runs in two environments:
- `.venv`: numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, statsmodels 0.15.0;
- `external/articleB-venv`: built with `~/miniforge3/envs/Trading/bin/python -m venv`, then
  `pip install -r` of Article B's requirements and `pyyaml`; numpy 1.26.4, scipy 1.16.2, pandas 2.3.2,
  statsmodels 0.14.5.

Each run replaces its own rows in `results/identity/articleB_R01_R08.csv` (2,834 rows per environment)
and writes `logs/identity/identity_articleB_<env>.log`. The per-source summary is identical in both
environments.

| input | source | cells | pass | bit-identical | max rel. diff. |
|---|---|---|---|---|---|
| `d1_loader` (blocking) | R01_garch_models | 56 | 56 | 44 | 2.64e-14 (omega) |
| | R01_covid_trajectories | 1012 | 1012 | 792 | 1.97e-14 (S_over_thr_Data) |
| | R01_covid_alarms | 5 | 5 | 5 | 0 |
| | R01_placebo_control | 64 | 64 | 64 | 0 |
| | R01_injection_summary | 48 | 48 | 48 | 0 |
| | R01_magnitude_sweep | 216 | 216 | 216 | 0 |
| `articleB_csv` (diagnostic) | all six R01 tables | 1401 | 1401 | 1397 | 4.63e-15 (lb_pvalue_warmup) |
| — | R08_lattice_exact_law | 32 | 32 | 17 | 9.72e-15 |

SPY reproduces bit for bit: α = 0.211551, β = 0.729081, Γ̂ = 14.998367977816738,
q̂ = 0.55864811133200798, no alarm in 2020. Three effects account for every cell that is not
bit-identical:
1. **Input parsing (`C-R01-parse`).** R01 reads its CSVs with pandas' default float converter, and D1
   with `round_trip`. The two reads differ by up to 7356 ulp per return. This reaches ω, σ_unc and
   `S_over_thr_Data`; no discrete output changes.
2. **BLAS build (`C-R01-env`).** The Ljung–Box p-value goes through statsmodels' `acf(fft=False)`,
   i.e. `np.correlate`, whose result depends on the BLAS linked by numpy. The PyPI wheels (openblas64)
   used by both venvs differ by 7 ulp on Q from the conda-forge build that produced Article B's CSV.
   Under that conda build, the `articleB_csv` input is bit-identical in all 1401 cells (diagnostic run,
   not written).
3. **Summation order (R08).** The generalized lattice chain sums in a different order from R08's
   (a, b) = (2, 3) code, which accounts for the R08 cells that are not bit-identical.

## Verification

```bash
pytest -q tests/test_monitors.py tests/test_identity_articleB.py
python -c "from jepadrift.monitors.lattice import attainable_levels as f; print(f(H=5000, delta=0.1, sided=1, q=0.5)[:5])"
python experiments/identity_articleB.py
external/articleB-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_identity_articleB.py
external/articleB-venv/bin/python experiments/identity_articleB.py
```

## References

- [Page, 1954, Continuous inspection schemes]
- [Lorden, 1971, Procedures for reacting to a change in distribution]
- [Ville, 1939, Étude critique de la notion de collectif]
- [Robbins, 1970, Statistical methods related to the law of the iterated logarithm]
- [Howard, Ramdas, McAuliffe & Sekhon, 2020, Time-uniform Chernoff bounds via nonnegative supermartingales]
- [Ramdas, Grünwald, Vovk & Shafer, 2023, Game-theoretic statistics and safe anytime-valid inference]
- [Shin, Ramdas & Rinaldo, 2024, E-detectors: a nonparametric framework for sequential change detection]
- [Newey & West, 1994, Automatic lag selection in covariance matrix estimation]
