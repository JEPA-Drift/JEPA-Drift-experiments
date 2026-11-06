# Stream 19-oracle — E4 analytic oracle reference: drift information in N

**Status: analytic reference, not an E4 result.** `experiments/e4_oracle_reference.py` serialises, for a known
Gaussian model, the per-day Kullback–Leibler divergence I_N of a market drift as a function of the cross-section size N,
and its gain over one asset. It estimates nothing, runs no detector and no Monte Carlo, and reads no data. No column is
a delay, an ADD, an ARL0 or an FPR. The E4 campaign of `prompts/streams/prompt-19-e4-p3kf.md` stays `À_REPLANIFIER`:
this lot does not close it.

## Model and formulas

Line numbers refer to `paper/sec3_theory.tex` at base `3467df4`.
- Known laws N(0, Σ_N) before the onset and N(Δμ, Σ_N) after it, with Σ_N = ρ11ᵀ + (1−ρ)I_N (unit variances,
  equicorrelation ρ) and Δμ = δ1 (market drift; δ in per-asset standard deviations).
- Since Σ_N1 = (1+(N−1)ρ)1, the quadratic form is ΔμᵀΣ_N⁻¹Δμ = δ²N/(1+(N−1)ρ). The KL is half of it:
  I_N = δ²N/[2(1+(N−1)ρ)] nats per day (factor ½ of `eq:hierarchy`, line 16; one-factor ratio of `cor:factor`,
  line 61).
- Gain over one asset: G(N) = I_N/I_1 = N/(1+(N−1)ρ), with I_1 = δ²/2 for every ρ. G does not depend on δ; I_N scales
  as δ².
- ρ > 0: G increases strictly towards the ceiling 1/ρ, with 1/ρ − G(N) = (1−ρ)/[ρ(1+(N−1)ρ)] and I_N ≤ δ²/(2ρ). The
  factor term is bounded in N (line 64).
- ρ = 0: G(N) = N, with no finite ceiling.

## Factor ½

`jepadrift/floors.py`, `factor_information`, is reused unchanged with B = 1 (N×1), Σ_F = [[ρ]], Ψ = (1−ρ)I_N, Δλ = δ
and Δα = 0. It returns the quadratic form ΔμᵀΣ_N⁻¹Δμ = 2 I_N, split into a factor term and a breadth term (here exactly
0). The script divides their sum by two; `floors` is never changed. Reading `factor_term` as a KL doubles the
information.

## Mathematical domain and float64 limits

- **Mathematical domain:** N integer ≥ 1, 0 ≤ ρ < 1, 0 < δ < ∞. `oracle_row` raises `ValueError` outside it: N boolean,
  non-integer (8.0 included) or < 1; ρ < 0, ρ ≥ 1 or non-finite; δ ≤ 0 or non-finite. A negative δ is rejected although
  I_N is even in δ. Python and NumPy integers are accepted for N.
- **Accepted types:** ρ and δ must be non-boolean real scalars (`numbers.Real`, which covers Python and NumPy integers
  and floats). Text, `None`, `Decimal`, complex numbers and booleans raise `ValueError` before any conversion; text is
  never parsed. NumPy scalars are converted to Python scalars (`.item()`) before any comparison, so a narrow dtype such
  as float16 or float32 never narrows the float64 bounds.
- **float64 limits inside the domain**, also rejected by `ValueError` and never returned as 0, `inf` or NaN:
  - ρ and δ must be exactly representable in float64, and δ at most the largest finite float64. A real that the
    float64 conversion would round is rejected before `factor_information` is called: for instance a high-precision ρ
    just below 1, which would become 1, a tiny positive ρ, which would become 0, or an integer δ such as 2^53 + 1.
  - δ²/2 must be a normal finite float64 (at least 2^−1022). A square that underflows to zero or overflows cannot be
    represented. A subnormal square can be represented but carries fewer significant bits, so it is excluded as a
    precision guard. All three cases are rejected before `factor_information` is called.
  - For ρ > 0, 1/ρ must be finite. A positive ρ whose inverse overflows is rejected, since `inf` would misstate a finite
    ceiling.
  - `factor_term`, `breadth_term`, `info_nats` and `gain_vs_single` must be finite, and the information and the gain
    strictly positive. An overflow inside `factor_information` ends in this `ValueError`, not in a warning or an
    unhandled exception.
- `gain_ceiling` is `inf` only for ρ = 0, where it states that no finite ceiling exists.

## Output

`python experiments/e4_oracle_reference.py --out <new file>` writes 16 rows, ρ ∈ {0, 0.4} × N ∈ {1, 8, 16, 32, 64, 128,
239, 500} at δ = 1, with `pipelines.save_fair_csv`. The file is created exclusively, so an existing file is never
overwritten, in a directory that the caller has created. The script prints one line in `sha256sum` format:
`<sha256>  <out>`.

| Column | Content |
|---|---|
| `N`, `rho`, `delta` | parameters |
| `factor_term`, `breadth_term` | outputs of `factor_information`; their sum is 2 I_N |
| `info_nats` | I_N, nats per day |
| `gain_vs_single` | G(N) = I_N/I_1 |
| `gain_ceiling` | 1/ρ, or `inf` at ρ = 0 |
| `qualification` | constant `ORACLE_KNOWN_SIGMA_DELTA`: Σ_N and Δμ known, analytic Gaussian KL |

The N grid is the historical E4 grid (`prompts/streams/prompt-19-e4-p3kf.md`, line 16) plus N = 1. ρ = 0 shows the
absence of a ceiling. ρ = 0.4 is the equicorrelation of `tests/test_floors.py::test_one_factor_keff` and of the
synthetic models in `results/pca_drift_benchmark/full_2000_20261101/manifest.json`. These are parameters of an analytic
reference, not detector settings.

## Reception

No CSV is tracked (GO 19-oracle, Q1). The reference is regenerated in a new directory, with the environment of
`CLAUDE.md` (`.venv/bin/python`, single-thread BLAS, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`):

```bash
D=$(mktemp -d) && .venv/bin/python experiments/e4_oracle_reference.py --out "$D/e4_oracle_reference.csv" \
  > "$D/ref.sha256" && sha256sum -c "$D/ref.sha256"
```

The SHA-256 of the regenerated file is then compared with the value recorded in `prompts/wrapups/wrapup-19-oracle.md`.
Bit-level receipt evidence exists for the pinned environment only.

`tests/test_e4_oracle_reference.py` checks `oracle_row` against the closed forms. Its tolerances are a relative 1e-12
against the closed forms, a relative 1e-10 against a dense solve, and an absolute 1e-12/ρ on the gap to 1/ρ. The tested
cases are:
- N ∈ {1, 2, 3, 5, 8, 13} × ρ ∈ {0, 0.25, 0.9} × δ ∈ {0.5, 2}, including the dense solve;
- N = 1 with δ = 2 and ρ ∈ {0, 0.4, 0.9}, for the factor ½;
- ρ = 0 at N ∈ {1, 8, 239, 500, 2^20};
- ρ ∈ {1 − 1e-6, 1 − 1e-12, largest float64 below 1} at N ∈ {1, 2, 500};
- ρ ∈ {0.1, 0.4} at N = 2^k for k = 0, …, 20, through the gap to 1/ρ;
- (N, ρ, δ) = (8, 0.4, 1e-150), (8, 0.4, 1e150), (8, 0.25, 2) and (2, 1e-300, 1);
- (N, ρ, δ) = (2, 0.25, 2) with ρ and δ given as NumPy float16, then float32, with warnings as errors;
- the 16 rows of the default grid, read back from the CSV.

These tests ran in the pinned environment only. They give no accuracy guarantee for untested inputs or other
environments. Values from `factor_information` can differ from the closed forms in their last digits.

## Not covered

The reference contains no delay (τ_γ, Φ, ADD), no ARL0 or FPR, no mixture M(D, γ) or dictionary cost, no measured slope
or exponent, no estimated covariance or PCA, no real or symmetrised returns, and no breadth drift. ρ < 0 (Σ_N stays
positive definite for ρ > −1/(N−1)) and heterogeneous variances lie outside the model. This note quotes no computed
number, so it adds no entry to `docs/MAPPING.md`.
