# Injections (stream 05) — D5 Monte Carlo backgrounds, D6 symmetrized panels, drift families F1–F4

`jepadrift/sim.py`, `jepadrift/stats/covariance.py` and `jepadrift/injection.py` generate the backgrounds and the
controlled drifts of the experiments (E1, E3–E7, E10, E11). Every drift starts at an exact onset τ*, so delays and
false alarms are measured against an exact ground truth. Drifts live in return space only, never in a latent z. The
modules use numpy and the standard library; every random draw comes from a `np.random.Generator` passed by the
caller. This note is the basis of Appendix B.

## API

| function | returns | role |
|---|---|---|
| `sim.gaussian_latent(T, D, rng)` | array (T, D) | D5: i.i.d. N(0, I_D) latent stream (Propositions 2–3) |
| `sim.garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None, burn=1000)` | array (T, N) | D5: common-volatility GARCH(1,1) panel |
| `sim.NU`, `sim.T_SCALE`, `sim.t_innov`, `sim.Garch` | — | E2 generator, moved verbatim |
| `covariance.ledoit_wolf(X)` | (Σ̂, δ̂) | Ledoit–Wolf shrinkage |
| `injection.symmetrize(X, rng)` | (X̃, ε) | D6 background |
| `injection.fit_background(X_calib, K)` | dict | Σ̂, eigen-pairs, loadings B, residual variances Ψ̂ |
| `injection.gls_residual(A, B, psi)` | array shaped like A | GLS residual of the rows of A on B |
| `injection.inject(X, family, tau_star, I_target, params, rng)` | (X̃, delta, meta) | drift of one family from τ* |
| `injection.draw_tau_star(t0, t_end, h_ref, h_det, rng)` | int | onset |
| `injection.write_tau_star(path, records)` | — | `tau_star.json` |

**Input contract.** `symmetrize`, `fit_background` and `inject` accept a returns panel only: a 2-D float64
`numpy.ndarray` (T days × N assets). Any other object, such as a latent `{"z_odd": …, "z_even": …}` dict, raises
`TypeError`; a wrong dimension or dtype raises `ValueError`. `fit_background` and `inject` also require finite
values: on panels with gaps (`d3_500`, 13 % missing) the caller selects a complete sub-panel first. `symmetrize`
keeps NaN in place. No function modifies its inputs.

## D5 — Monte Carlo backgrounds

**Gaussian latent.** z_t ~ N(0, I_D), i.i.d.

**GARCH panel.** The N assets share one volatility σ_t, with unit unconditional variance [Bollerslev, 1986]:

σ_t² = ω + α·m_{t−1} + β·σ_{t−1}², ω = 1 − α − β, m_t = (1/N)·Σ_i x_{t,i}²,

started at σ² = 1 and m = 0, and run for `burn` days before the T days kept. x_t = σ_t·η_t, with η_t a multivariate
Student-t_ν of unit variance: η_t = z_t / √(χ²_ν/ν) · √((ν − 2)/ν), one χ² draw per day for the whole
cross-section (the law of `t_innov` in two dimensions). `nu=None` gives Gaussian innovations. With `factor_rho` = ρ,
z_t = √ρ·g_t·1 + √(1 − ρ)·u_t (g_t ~ N(0, 1), u_t ~ N(0, I_N)), so that corr(x_i, x_j) = ρ. The common χ² draw
keeps volatility clustering in the cross-sectional mean square when N is large. Requires α, β ≥ 0, α + β < 1,
ν > 2 and 0 ≤ ρ < 1. One call returns one panel; independent replicates take one call each (`# ponytail:` ceiling,
a replicate axis if E3's many-path loops dominate runtime).

| parameter | values |
|---|---|
| (α, β) | (0.08, 0.90) |
| ν | 7, or `None` (Gaussian) |
| ρ (`factor_rho`) | 0.40, or `None` (no factor) |
| burn-in | 1000 days |

**E2 generator.** `NU`, `T_SCALE`, `t_innov` and `Garch` moved from `experiments/e2_floor_validation.py` (commit
`3e3a804`) without a byte changed; E2 imports `NU`, `T_SCALE` and `Garch` from `jepadrift.sim`.
`results/e2/e2_cells.csv` keeps SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`
(`make j1` before and after the move; `C-e2-sim`).

## D6 — symmetrized real panels

X̃_t = ε_t·X_t, with ε_t i.i.d. Rademacher and one sign for the whole day (`rng.choice((-1.0, 1.0))`). The
transformation keeps |x_{t,i}| bit for bit, the cross-sectional correlations and volatility clustering, and erases
location drift and the leverage effect. Under a centrally symmetric conditional law, the sign stream of any odd
projection is then exact (Article C, Lemma 2). ε is returned for traceability.

## Calibration-window estimates

Every estimate uses the calibration rows `params["calib"] = (start, stop)` of the background X, before any drift is
added.

- **Covariance** [Ledoit & Wolf, 2004]: centred sample covariance S = X_cᵀX_c/n and target μI, μ = tr S/N;
  shrinkage δ̂ = min(b̄², d²)/d² with d² = ‖S − μI‖²_F and b̄² = n⁻²·Σ_t ‖x_t x_tᵀ − S‖²_F; Σ̂ = (1 − δ̂)·S + δ̂·μI
  (δ̂ = 0 when d² = 0, as for N = 1).
- **Principal directions**: eigen-pairs (λ_k, v_k) of Σ̂ in decreasing order of λ_k; each v_k is signed so that
  Σ_i v_{k,i} ≥ 0, which makes the directions independent of the LAPACK build. Shrinkage towards μI keeps the
  eigenvectors of S.
- **Loadings**: B = [v_1√λ_1, …, v_K√λ_K] (factors of unit variance, Σ_F = I; K counts PC1).
- **Residual variances**: Ψ̂ = diag(Σ̂ − BBᵀ) > 0.

## Drift families

For F1–F3, x̃_t = x_t + Δ_t for t ≥ τ*; for F4, x̃_t = M·x_t for t ≥ τ*. Rows before τ* are unchanged bit for bit.
The per-day Gaussian information is I = ½·ΔᵀΣ̂⁻¹Δ for a location drift and KL(N(0, MΣ̂Mᵀ) ‖ N(0, Σ̂)) for F4.

| family | `family` | drift | parameters |
|---|---|---|---|
| F1, factor premia | `"F1"` | Δ = B·Δλ, Δλ = s·u, u uniform on the unit sphere of R^K | `K` |
| F2, characteristic-driven breadth | `"F2"` | Δ_t = s·(C_t·g)_⊥, g uniform on the unit sphere of R^P | `K`, `C` (T, N, P) |
| F3, market-mode translation | `"F3"` | Δ = Δm·b_1, b_1 = v_1√λ_1, Δm > 0 | — |
| F4, deformation | `"F4-deform"` | M = I + (√r − 1)·V_S V_Sᵀ, V_S the eigenvectors of Σ̂ indexed by S | `subspace` (S), `r` |
| F4, rotation | `"F4-rotate"` | M = I + (cos θ − 1)(uuᵀ + wwᵀ) + sin θ·(wuᵀ − uwᵀ), (u, w) = (v_i, v_j) | `pair` (i, j), `theta_deg` |

**F2.** The GLS residual is a_⊥ = a − B(BᵀΨ̂⁻¹B)⁻¹BᵀΨ̂⁻¹a (Article C, Corollary 1), so BᵀΨ̂⁻¹Δ_t = 0: the drift
carries breadth information only. C_t holds the characteristics known at the open of day t (D3: centred ranks of
beta_252, vol_63, mom_12_1 and rev_21, plus 11 GICS indicators; characteristic-driven loadings as in [Kelly, Pruitt
& Su, 2019]). A missing characteristic counts as zero exposure, the neutral rank; the count of imputed entries is
recorded (`C-inject-F2-nan`).

**F4.** Deformation along eigenvectors: I = (d/2)·(r − 1 − ln r), d = |S|. Rotation of two eigenvectors:
I = ½·sin²θ·(λ_i − λ_j)²/(λ_i·λ_j). The code evaluates I = ½·[2 tr E + tr(Σ̂⁻¹EΣ̂Eᵀ) − 2 ln|det M|] with E = M − I,
which avoids subtracting N from a trace of order N. Grids: r ∈ {1.25, 1.5, 2} and θ ∈ {15°, 30°, 45°}.

| r | information per deformed dimension (nats/day) | multiple of I(SR = 1) = 1/504 |
|---|---|---|
| 1.25 | 0.013428 | 6.77 |
| 1.5 | 0.047267 | 23.82 |
| 2 | 0.153426 | 77.33 |

## Amplitude conventions (F1–F3)

The scale s is fixed on the calibration rows, never on the monitored rows.

**(a) Equal information** (`I_target` > 0): I_target = SR²/504 (`floors.kl_from_sharpe`) and

½·mean_{t ∈ calib}(Δ_tᵀΣ̂⁻¹Δ_t) = I_target.

For F1 and F3, Δ does not depend on t. For F2, the mean runs over the calibration days of the time-varying Δ_t: the
per-day information averages to I_target, the clock of Lemma 1 (`C-inject-F2-norm`). After τ*, the realised daily
information of F2 follows C_t.

| SR | I_target (nats/day) |
|---|---|
| 0.5 | 4.960317e-04 |
| 1 | 1.984127e-03 |
| 2 | 7.936508e-03 |
| 4 | 3.174603e-02 |

**(b) Fixed per-asset amplitude** (`I_target=None`; scaling laws of E1 and E4): the per-asset annualized Sharpe
ratio of the drift, √252·Δ_i/σ̂_i with σ̂_i² = Σ̂_ii, has a root mean square over the assets (and over the
calibration days for F2) equal to `SR_ASSET_B` = 1 for F1 and F3, and to κ·`SR_ASSET_B` for F2, with
κ ∈ {0.25, 0.5, 1} (`C-inject-conv-b`). κ is the ratio of the cross-sectional dispersion orthogonal to the loadings
to the market drift; under an equicorrelated one-factor model with equal volatilities, the breadth-to-market
information ratio is κ²·(1 + (N − 1)ρ)/(1 − ρ).

## Onset and `tau_star.json`

τ* is uniform on the integers t_0 + H_ref, …, t_end − H_det (`draw_tau_star`; both bounds included, `ValueError`
on an empty range), with t_0 and t_end the first and last rows of the window, H_ref the reference length before the
onset (R15: 500) and H_det the detection horizon (R15: 750; E1: 2000).

`inject` returns `meta`, the JSON-ready record that `write_tau_star(path, records)` writes (one dict or a list;
sorted keys, indent 2, trailing newline):

| key | content |
|---|---|
| `family` | `F1`, `F2`, `F3`, `F4-deform` or `F4-rotate` |
| `tau_star` | onset row |
| `convention` | `"a"`, `"b"`, or `null` for F4 |
| `amplitude` | (a) `{"I_target", "sr"}`; (b) `{"kappa", "sr_asset"}`; F4 `{"r", "subspace"}` or `{"theta_deg", "pair"}` |
| `seed` | `{"entropy", "spawn_key"}` of the generator's `SeedSequence` |
| `direction` | Δλ (F1), s·g (F2), [Δm] (F3); `null` for F4 |
| `direction_sha256` | SHA-256 of the float64 bytes of `delta` |
| `info` | per-day Gaussian information (F2: calibration mean) |
| `K`, `calib`, `shrinkage` | factor count, calibration rows, Ledoit–Wolf δ̂ |
| `c_nan_imputed` | F2 only: missing characteristics read as 0 |

`delta` is the applied drift: X̃[τ*:] = X[τ*:] + delta, of shape (N,) for F1 and F3 and (T − τ*, N) for F2, or
X̃[τ*:] = X[τ*:] @ deltaᵀ with delta = M for F4. The oracle P7 rebuilds Δ from `direction` and `fit_background` on
the same rows: Δ = B·direction (F1), Δ_t = (C_t·direction)_⊥ (F2), Δ = direction[0]·b_1 (F3). The seed identifies
the replicate's `SeedSequence`; replaying it requires the same sequence of calls on the generator (for example
`symmetrize`, then `draw_tau_star`, then `inject`).

## Guarantees and tests (`tests/test_injection.py`)

| guarantee | test |
|---|---|
| absolute values unchanged bit for bit, one sign per day (D6) | `test_symmetrize_abs_bitwise_one_sign_per_day` |
| ‖BᵀΨ̂⁻¹Δ_t‖_∞ < 1e-10 (F2) | `test_f2_orthogonal_to_loadings` |
| ½·ΔᵀΣ̂⁻¹Δ = I_target to 1e-10 (F1, F2, F3) | `test_information_target` |
| rows before τ* unchanged (all families, τ* ∈ {0, 600, T − 1}) | `test_no_change_before_tau_star` |
| same seed, same output | `test_determinism`, `test_generators_deterministic` |
| E2 SHA-256 unchanged | `test_e2_quick_sha256_unchanged`, `test_e2_uses_moved_generator`; `make j1` |
| convention (b) amplitudes | `test_convention_b_per_asset_amplitude` |
| F4 operators and information | `test_f4_deformation_and_rotation` |
| inputs never modified | `test_inputs_not_mutated`, `test_inject_does_not_mutate_inputs` |
| refused inputs | `test_inputs_rejected`, `test_inject_arguments_rejected`, `test_degenerate_direction_rejected` |
| missing characteristics | `test_f2_nan_characteristics_imputed` |
| Ledoit–Wolf, GLS residual, calibration estimates | `test_ledoit_wolf_matches_formula`, `test_gls_residual_matches_corollary`, `test_fit_background_conventions` |
| GARCH panel moments | `test_garch_panel_moments` |
| onset bounds, JSON record | `test_draw_tau_star_bounds`, `test_tau_star_json_roundtrip` |

The real-data tests read `d3_239` up to 2019-12-31 only, with estimates on its calibration segment
(2016-04-07 to 2019-12-31); nothing reads the monitoring window before J4. `test_e2_quick_sha256_unchanged` runs in
the reference environment only (numpy 2.4.4, scipy 1.17.1), since its hash depends on the numerical stack.

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16   # e315e537ead0f656
pytest -q tests/test_injection.py
```

## References

- [Bollerslev, 1986] T. Bollerslev, "Generalized autoregressive conditional heteroskedasticity", Journal of
  Econometrics 31(3), 307–327.
- [Kelly, Pruitt & Su, 2019] B. Kelly, S. Pruitt and Y. Su, "Characteristics are covariances: a unified model of
  risk and return", Journal of Financial Economics 134(3), 501–524.
- [Ledoit & Wolf, 2004] O. Ledoit and M. Wolf, "A well-conditioned estimator for large-dimensional covariance
  matrices", Journal of Multivariate Analysis 88(2), 365–411.
- Article C, Section 3 (`paper/sec3_theory.tex`): Lemma 1 (evidence budget, `lem:budget`), Proposition "Latent delay
  floors" (`prop:floor`), Corollary 1 (factor and breadth terms, `cor:factor`), Lemma 2 (whitening by an odd
  encoder, `lem:odd`).
