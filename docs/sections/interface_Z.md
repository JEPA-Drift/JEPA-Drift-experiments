# Interface Z (stream 06) — contract of every representation, version Z-1

`jepadrift/representations/` connects every representation (PCA, degree-0 cross-section, ranks, and later IPCA,
CD-DFM and the JEPA) to the monitors through one contract. A representation is fitted on one calibration-type
segment only, encodes each day independently, and exposes a frozen, hashed state. The monitors receive arrays
(Z or X), never representation objects: `jepadrift/monitors/` imports none of these modules, and
`jepadrift/representations/` imports neither `jepadrift.monitors`, `jepadrift.injection` nor torch
(`test_import_isolation`). The version string `Z-1` is written in every sidecar (`"interface"`); a change of
this contract bumps it.

## API — `base.Representation`

| member | returns | contract |
|---|---|---|
| `fit(X_fit, C_fit, dates_fit)` | `self` | `X_fit`: (T, N) float64, finite (NaN allowed under `missing`), T ≥ 2, N ≥ 2; `dates_fit`: T dates. Receives the rows of **one** `pretrain` or `calib` segment, nothing else |
| `transform_day(x_t, C_t=None)` | `{"z_odd": (D,), "z_even": (D',)}` | `x_t`: (N,) float64, finite (NaN allowed under `missing`) |
| `transform_panel(X, C=None)` | `{"z_odd": (T, D), "z_even": (T, D')}` | the stack of `transform_day` over the rows of X, bitwise; no operation across days |
| `state_hash()` | hex SHA-256 | see below |
| `sidecar()` | JSON-serializable dict | see below |
| `odd_head` | `True` | the odd head exists and is odd in x |
| `missing` | `False` (class attribute) | `True` lets NaN mark an absent return (IPCA); ±inf is always refused |
| `pretrain(X, C, dates)` | — | optional hook of a representation estimated in two segments (IPCA: Γ on `pretrain`); called before `fit` |

Subclasses set `config` in `__init__` and implement `_fit(X, C)` (sets `state`, `stats`, `heads`, `channels`) and
`_day(x, C) -> (z_odd, z_even)`; validation, hashing, the sidecar and the panel loop live in the base class.

**Input contract.** Returns are float64 (`C-interface-f64`) and finite: a non-ndarray input raises `TypeError`; a
wrong dimension, dtype, length or a non-finite value raises `ValueError`. A class that sets `missing = True` reads
NaN as an absent return and drops it from its equations: a zero is an observation, never a fill value (stream 17).
`C_t` is part of the signature for the characteristic-driven representations (IPCA, CD-DFM, JEPA); none of the three
linear references reads it, and the extraction passes `C=None` to them.

**Heads.** The odd head satisfies φ(−x) = −φ(x); under any centrally symmetric null its sign streams
1{uᵀφ(x_t) > 0} are i.i.d. Bernoulli(1/2) whatever the volatility (Article C, lemma "Whitening by an odd
encoder"). The even head satisfies φ(−x) = φ(x) and feeds the energy (Data) pipelines. No centring, no
normalization over time and no state updated after `fit` is allowed: each would break oddness or non-anticipation.

**Fit rows.** `fit` must only see `pretrain` or `calib` rows (contract (4) of stream 08). A representation with a
`pretrain` hook receives the `pretrain` rows there and the `calib` rows in `fit`, never one segment in both. The interface cannot tell
whether those rows already carry an injected drift: when an experiment injects with τ* inside or before the fit
window (E1 with H_det = 2000), the caller (streams 07 and 12) chooses drift-free fit rows (pretrain, or rows
before τ*). A drift absorbed by the fit is invisible to every monitor (Article C, Proposition "Absorption").

## Frozen state and sidecar

`state_hash()` is the SHA-256 of the canonical JSON header `{"class", "config", "n_assets"}` (sorted keys),
followed, for each state array by sorted name, by `name|dtype|shape|` and the array bytes. The header keeps two
transforms with the same arrays (PCA factor and DegreeZero share eigenvectors) under different names.

| representation | state |
|---|---|
| `PCAOrthogonal` | `W` (N × D) |
| `DegreeZero` | `b` (N,), `U` (N × D) |
| `CenteredRanks` | none (the header carries N) |

`sidecar()` keys:

| key | content |
|---|---|
| `interface`, `representation`, `config`, `state_sha256`, `n_assets`, `odd_head` | identity |
| `heads` | for `z_odd` and `z_even`: `dim`, `parity` (`odd`/`even`), `degree` (homogeneity degree in x), `definition` |
| `channels` | name → columns of `z_odd` (`market`, `residual`, `assets`) |
| `fit` | `first_day`, `last_day`, `days`, `x_sha256` (SHA-256 of the float64 bytes of X_fit), `c_sha256` |
| `normalization` | frozen statistics of the fit rows (below); recomputable from the rows named by `fit` |

The extraction adds `dataset`, `fit_segment` (`"calib"`), `rows` ([first, stop) of the source panel), `dates`
(first and last day of Z), `x_sha256` (transformed rows) and `z_sha256` (`Z_odd`, `Z_even`); with characteristics,
also `c_sha256` (SHA-256 of the float64 bytes of the C rows transformed). Without C the sidecar bytes are unchanged.

## Extraction — `extract.py`

```bash
python -m jepadrift.representations.extract --dataset {d2_us97,d3_239,d3_500,d4_eurofidai} --rep {pca,degree0,ranks} \
    [--mode M] [--K mp|int] [--shrinkage ledoit_wolf|none] [--b pc1|ones] [--out DIR]
```

`extract(rep, X, dates, splits, out_dir, dataset, C=None)`: C is (T, N, P), row-aligned with X (`ValueError`
otherwise). The rows of each step are those of one segment: `rep.pretrain(X, C, dates)` on the `pretrain` rows when
the representation has that hook, `fit` on the `calib` rows, then the transformation of the rows from the first
`pretrain` day on with `C[first:]`.

- Fit on the `calib` rows of `splits.yaml` (first_day to last_day, both included).
- Transform the rows from the first `pretrain` day to the end of the panel (`C-repr-rows`): on `d3_239`, rows
  2000–2004 belong to no segment and row 0 has no return; on `d2_us97` every row is transformed. Non-finite
  input raises `ValueError`. `d3_500` (13 % missing) and `d4_eurofidai` (`CHAR_DATASETS`) are offered to the
  characteristic representations only; the CLI refuses them to the others, whose callers select a complete
  sub-panel.
- Write `data/derived/<dataset>/z_<state_hash>.npz` (`np.savez`: `Z_odd` float64 (T, D), `Z_even` float64
  (T, D'), `dates` datetime64[D]) and `z_<state_hash>.json` (`json.dumps(indent=2, sort_keys=True)` plus a
  newline). `np.savez` dates its zip entries 1980-01-01, so equal arrays give equal bytes; two runs give
  identical SHA-256 (`test_extract_deterministic`). Hashes depend on the numerical stack (LAPACK/BLAS): they are
  reproducible on the reference environment (`.venv`, numpy 2.4.4), not across builds.
- Only the options given are passed to the constructor.
- **Characteristic path** (`--rep` in `NEEDS_C`): C = `chars.load_continuous_chars(dataset)`, the four
  `sp500.CONTINUOUS_CHARS` columns, NaN kept; X = `np.where(chars.load_universe(dataset), ret, nan)`, the returns
  masked by `in_universe` of `panel.parquet` and never imputed. D2 raises `ValueError("D2 has no characteristics")`.

**Registry.** `extract.REGISTRY = {"pca": PCAOrthogonal, "degree0": DegreeZero, "ranks": CenteredRanks}` is the
registry of the contract tests (stream 08). A new representation (IPCA, stream 17; CD-DFM, stream 18; JEPA,
stream 14) subclasses `Representation`, keeps the contract above, adds its entry to `REGISTRY`, and documents its
heads here. A characteristic-driven representation also enters `extract.NEEDS_C` and declares its builder in
`tests/test_contracts.py::CHAR_CASES`; the meta-test `test_char_registries_agree` imposes
`NEEDS_C == set(CHAR_CASES) ⊆ REGISTRY`, and the D2 contracts loop on `REGISTRY − NEEDS_C`
(`docs/sections/contracts.md`). C_t and the mask come from the shared loader `jepadrift/data_loader/chars.py`.

**Reference extractions** (`pca`, mode `factor`, Ledoit–Wolf; `logs/representations/extract.log`):

| dataset | file | D = D' | rows |
|---|---|---|---|
| `d2_us97` | `z_85147fd9…6f3d.npz` | 6 (market + K = 5) | 0–5153 |
| `d3_239` | `z_6c44d64a…ce3f.npz` | 11 (market + K = 10) | 1256–6737 |

## Representations

### `pca.PCAOrthogonal(K="mp", mode="factor", shrinkage="ledoit_wolf")` — P3-C, P3-D, P3-KF

Σ̂ is the Ledoit–Wolf covariance of the fit rows [Ledoit & Wolf, 2004] (`shrinkage=None`: the centred sample
covariance divided by n). Its eigen-pairs come from `stats.covariance.eigh_desc` (decreasing eigenvalues, each
eigenvector signed to a nonnegative sum), the same function as `injection.fit_background`, so the market channel
is exactly the direction of the F3 drift. With V_sel and λ_sel the selected eigen-pairs:

z_odd = xᵀ V_sel diag(λ_sel)^(−1/2) (odd, degree 1), z_even = z_odd² (even, degree 2), D' = D.

Column 0 is the market channel v₁ᵀx/√λ₁ in every mode; `channels = {"market": [0], "residual": [1, …, D−1]}`
(`C-repr-layout`). PC1 is never discarded silently. No centring: a constant shift would make the map affine.

| mode | residual columns | D |
|---|---|---|
| `factor` | PC2..PC(K+1) | K + 1 |
| `full` | PC2..PCN | N |
| `tail10` | the m last components | m + 1 |

- **K at the Marčenko–Pastur edge** (`K="mp"`, `C-repr-mp-K`). On the sample correlation of the fit rows,
  λ₊ = σ²(1 + √(N/T))² with σ² = 1 (the trace over N of a correlation matrix) [Marčenko & Pastur, 1967];
  n₊ = #{λ > λ₊}, PC1 included, and K = n₊ − 1 (PC1 is the market channel, not a residual factor). K ≤ 0
  raises `ValueError`; an integer K needs 1 ≤ K ≤ N − 1. On the calib windows: K = 5 for `d2_us97`
  (λ₊ = 1.7452), K = 10 for `d3_239` (λ₊ = 2.2619).
- **tail10** (`C-repr-layout`): m = max{m : the m smallest eigenvalues of Σ̂ sum to at most 10 % of tr Σ̂}, after
  the low-variance components of [Kuncheva & Faithfull, 2014]. m = 46 for `d2_us97`, 123 for `d3_239`.
- **Whitening** (`C-repr-whiten-lw`). Coordinates are white with respect to Σ̂. With Ledoit–Wolf, for any drift δ
  in full mode, ½‖z_odd(δ)‖² = ½δᵀΣ̂⁻¹δ, the per-day information that `injection.inject` targets on the same rows
  (`test_whitening`); the calib variance of each coordinate is λ_S/λ_LW (0.49 to 1.03 on `d3_239`). With
  `shrinkage=None` the calib covariance of z is exactly the identity.
- `normalization`: `eigval` (selected), `trace`, `shrinkage` (δ̂ or null), `mp_edge`, `n_above_edge`, `K`
  (factor), `tail_count` and `tail_share` (tail10).

### `cross_section.DegreeZero(b="pc1", K="mp", mode="factor")` — P3-CS

With b a unit vector (`"pc1"`: v₁ of Σ̂_LW; `"ones"`: 1/√N), p = Px = x − b bᵀx and U the frozen residual
eigenvectors of the same decomposition (PC2..PC(K+1) in `factor`, PC2..PCN in `full`):

z_odd = Uᵀp/‖p‖ (odd, degree 0; 0 when ‖p‖ = 0), z_even = [‖p‖] (even, degree 1), D = K or N − 1, D' = 1.

|z_odd,k| ≤ 1, the bounded pivot of the betting e-process; in `full` mode with b = v₁, ‖z_odd‖ = 1. The even head
carries the day's dispersion ‖Px_t‖ that the predictable stake of P3-CS (b) needs (`C-repr-even-heads`). The
direction b is projected out: there is no market channel, and `normalization["b"]` declares which direction.
P3-CS watches the same directions as P3-C, so the comparison isolates the normalization (frozen Λ against the
day's ‖Px_t‖). `normalization`: `b`, `K` (factor), `mp_edge`, `n_above_edge`, `shrinkage`.

### `cross_section.CenteredRanks()` — P3-CS

z_odd,i = (r_i − (N+1)/2)/N with average ranks for ties (−0.0 and 0.0 tie), z_even = z_odd²; D = D' = N. Ranks of
−x mirror those of x, so the map is odd exactly; it is invariant to x → c·x for c > 0, and to a shift of all
returns by a common constant up to rounding ties. No state; `channels = {"assets": [0, …, N−1]}`.

## Guarantees and tests (`tests/test_representations.py`)

| guarantee | test |
|---|---|
| shared, signed eigen-decomposition; identical to `fit_background` | `test_eigh_desc_sorted_signed` |
| ranks equal to `scipy.stats.rankdata` (average) | `test_ranks_values` |
| panel = stack of days, bitwise; non-anticipation | `test_transform_panel_day_by_day` |
| input contract | `test_inputs_rejected` |
| hash and sidecar | `test_state_hash_and_sidecar`, `test_normalization_from_declared_segment` |
| MP rule (spiked model, i.i.d. null), K range | `test_mp_rule` |
| expected D, no NaN on D2 and `d3_239` (rows up to 2019-12-31) | `test_pca_dimensions_real`, `test_cross_section_dimensions_real` |
| tail10 rule | `test_tail10_rule` |
| whitening; injected information preserved; F3 in the market column | `test_whitening` |
| oddness ‖φ(−x) + φ(x)‖_∞ ≤ 1e-12, even head symmetric | `test_odd_head` |
| degree 0, bounded pivot, zero day | `test_degree_zero_invariance`, `test_degree_zero_bounds_and_zero_day` |
| monitor rows do not move the state | `test_monitor_perturbation_keeps_state` |
| deterministic files | `test_extract_deterministic` |
| no import of monitors, injection or torch | `test_import_isolation` |
| characteristic path: pretrain, calib and transformed rows of X and C aligned; NaN passed through, not zero-filled; `c_sha256` only with C | `test_extract_char_path_alignment` (witness `_CharProbe`), `test_extract_rejects_misaligned_C` |
| NaN accepted only under `missing`, ±inf always refused | `test_missing_flag` |
| `in_universe` mask ≡ `isfinite(ret)` before 2020 (`d3_239`, `d3_500`, D4 when built); four continuous columns by name | `tests/test_chars.py`: `test_load_universe_matches_finite_returns`, `test_load_continuous_chars_selects_by_name` |

No test computes a statistic on rows dated 2020-01-01 or later: the perturbation test replaces them with synthetic
draws, and the determinism test compares file bytes only.

## References

- Kuncheva, L. I. and Faithfull, W. J. (2014). PCA feature extraction for change detection in multidimensional
  unlabeled data. IEEE Transactions on Neural Networks and Learning Systems, 25(1).
- Laloux, L., Cizeau, P., Potters, M. and Bouchaud, J.-P. (2000). Random matrix theory and financial
  correlations. International Journal of Theoretical and Applied Finance, 3(3).
- Ledoit, O. and Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. Journal
  of Multivariate Analysis, 88(2).
- Marčenko, V. A. and Pastur, L. A. (1967). Distribution of eigenvalues for some sets of random matrices.
  Mathematics of the USSR-Sbornik, 1(4).
- Article C, Section 3: lemma "Whitening by an odd encoder", Remark "Combining channels", Proposition
  "Absorption".
