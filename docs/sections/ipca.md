# IPCA (stream 17) — representation, K selection and the P4 pipelines

## Model

x_t = C_t Γ f_t + e_t, the restricted IPCA of [Kelly, Pruitt & Su, 2019, Characteristics are covariances] without
the intercept block. C_t (N × P) holds characteristics known at the open of day t: the four rank-transformed
`sp500.CONTINUOUS_CHARS` (P = 4), loaded by `chars.load_continuous_chars`. The loadings C_t Γ are known at t − 1 and
f_t is linear in x_t, hence odd: its sign streams are exact under a centrally symmetric null (Lemma 2). Choices that
differ from the published estimator: `C-IPCA-design` (`docs/DEVIATIONS.md`).

## Estimation (`jepadrift/representations/ipca.py`)

- **Mask.** X = `where(in_universe, ret, NaN)`: NaN is an absent return, a zero is an observation. Day t uses
  O_t = {i : x_{i,t} finite} and imputes nothing (`missing = True`). A NaN characteristic of an observed cell reads 0
  and is counted (`c_nan_imputed`).
- **Rank rule.** A day is used iff rank(C̃_t[O_t]) = P (`numpy.linalg.matrix_rank`). An unusable day is excluded from
  ALS, the K score and the whitening, listed by date in the sidecar, and gives z = 0. The rule depends on O_t and C_t
  only, so it is the same for x and −x.
- **ALS (pretrain).** f_t = (Γ'W_tΓ)⁻¹Γ'y_t with W_t = C̃_t'C̃_t, y_t = C̃_t'x̃_t; vec(Γ) = [Σ_t f_t f_t' ⊗ W_t]⁻¹
  vec(Σ_t y_t f_t'). Start: the K leading right singular vectors of [y_t / N_t]_t. Stop: ‖QQ' − Q₋Q₋'‖_F ≤ 1e-10
  (`RuntimeError` after 10,000 iterations). Normalization: Γ'Γ = I, (1/T) Σ f f' diagonal decreasing, largest |entry|
  of each column positive. The objective Σ_t (‖x̃_t‖² − f_t'Γ'y_t) is non-increasing.
- **Two segments.** `pretrain(X, C, dates)` estimates Γ_k on the pretrain rows for every k ≤ min(K_max = 4, P) and
  records dates, used and excluded days, `x_sha256`, `c_sha256`, imputed NaN, iterations and in-sample R². `fit`
  (calib) selects K and the whitening. The state hash covers Γ_K, W and, in cash-neutral mode, s_m.

## K selection (held-out R² on calib, `C-IPCA-K`)

Assets are split by index parity into folds A and B. For each used calib day and each direction, f_A is estimated on
O_t ∩ A only and predicts x̂_B = C̃_B Γ f_A; R²_ho = 1 − Σ‖x̃_B − x̂_B‖² / Σ‖x̃_B‖² (uncentred), both directions summed.
Principal mode targets returns; cash-neutral mode targets relative returns, each fold centred by its own observed
means. K* = argmax R²_ho; ties within 1e-12 go to the smallest K.

`results/ipca/k_selection.csv` (generator `experiments/ipca_k_selection.py`, log `logs/ipca/k_selection.log`, rows
before 2020-01-01; `test_real_d3_239_selection` links the `d3_239` rows to the code):

| panel | target | K = 1 | K = 2 | K = 3 | K = 4 | K* |
|---|---|---|---|---|---|---|
| `d3_239` | returns | 0.0547 | **0.0606** | 0.0566 | 0.0509 | 2 |
| `d3_239` | relative returns | 0.0728 | **0.0825** | 0.0810 | 0.0792 | 2 |
| `d3_500` | returns | 0.0456 | 0.0649 | **0.0688** | 0.0676 | 3 |
| `d3_500` | relative returns | 0.0676 | 0.0840 | 0.0864 | **0.0875** | 4 |
| D4 | returns | 0.0254 | **0.0266** | 0.0198 | 0.0158 | 2 |
| D4 | relative returns | 0.0273 | **0.0278** | 0.0228 | 0.0194 | 2 |

Retrospective static GICS sensitivity (P = 15, K_max = 6, returns, D3 only): K* = 6 on `d3_239` (R²_ho from 0.2480 at
K = 1 to 0.3147) and on `d3_500` (0.2465 to 0.3119). Neither the extraction nor P4 uses the GICS columns.

## Whitening and heads

M = (1/T_c) Σ f_t f_t' over the used calib days, uncentred; W = M^(−1/2), symmetric root, so (1/T_c) Σ z z' = I on
calib and z(0) = 0. `z_odd = W f_t`, `z_even = z_odd ** 2`, `channels = {"residual": [0..K−1]}`. Cash-neutral
`constant`: C̃_t = C_t[O_t] − 1c̄_t' and x̃_t = x_t[O_t] − m_t, `z_odd = [m_t / s_m, W f_t]` with s_m the uncentred calib
RMS of m_t, `channels = {"market": [0], "residual": [1..K]}`; z_factors(x + c·1) = z_factors(x).

## Extractions

`python -m jepadrift.representations.extract --dataset <d> --rep ipca` (log `logs/ipca/extract.log`; two fresh
extractions of each D3 panel are byte-identical to each other and to the committed files, `cmp` on 2026-10-28):
`d3_239` D = 2 (state `55a11b…`) and `d3_500` D = 3 (`183a37…`), committed under
`data/derived/`; D4 D = 2 (`301ec1…`), local and ignored. Rows run from the first pretrain day to the panel end
(`C-repr-rows`); no statistic is computed on rows dated 2020 or later.

## Characteristic audit

`results/ipca/char_audit.csv` (long format `dataset, segment, metric, value`; D3 and D4, pretrain and calib):

- beta denominator (`C-D3-beta-denominator`): the faulty formula reproduces the stored `c_beta_252` bit for bit on the
  three panels; against the OLS beta, 71–76 % of the `d3_239` ranks change; the NaN created by the formula are the
  negative faulty denominators (8 / 24 on `d3_239`);
- phantom ranks (`C-D3-chars-phantom`): none on `d3_239`; on `d3_500` the momentum and reversal ranks include
  219,639 / 27,945 cells without a return; on D4 the four characteristics do.

## P4 pipelines

P4-C and P4-D reuse the streams, detectors and calibrations of P3-C and P3-D on the IPCA representation, with C_t
carried by `split_rows(dates, splits, C)` (`docs/sections/pipelines.md`). D6 null checks on `d3_239` (500
replicates, H = 750; `results/ipca/runs_P4-{C,D}_d3_239_null.json`, `logs/ipca/null_P4-{C,D}_d3_239.log`):
P4-C anytime-valid 0.0020 (≤ 0.05) and exact channels 0.0420 and 0.0460 (= 0.043947), PASS; P4-D bootstrap 0 alarms
in 500 against `~ 0.05`, FAIL.

## Results interpretation

- **K and R².** At K*, the held-out R² of returns lies between 0.027 (D4) and 0.069 (`d3_500`); it peaks at K = 2 on
  `d3_239` and D4, at K = 3 on `d3_500`. Relative returns are another target and are not compared with returns.
  Two selections sit at their bound and are censored there: `d3_500` relative returns (K* = 4 = min(K_max, P)) and
  the GICS sensitivity (K* = 6 = K_max), whose higher R² rests on retrospective sector labels. The in-sample R² grows
  with K by construction and selects nothing.
- **Inherited data defects.** Every estimate uses the stored characteristics: the beta denominator defect on all
  panels and the phantom ranks on `d3_500` and D4. They are to be rerun after a data correction (another stream).
  The survivorship bias of D3 and D4 remains (`C-D3-survivor-correction`, `C-D4-survivor`).
- **P4-C.** Its null checks pass at their targets. They test the exact sign streams under fresh D6 signs; they do not
  certify the IPCA estimates beyond that property.
- **P4-D, uncalibrated.** Its saved null check is FAIL and stays so. A read-only replay (`C-P4D-null-insample`) found
  no code/artifact mismatch and showed that the check re-reads the 192 calib windows that set λ, with no fresh
  randomness in the even energy stream: all 192 windows share one CUSUM peak just below λ, for P4-D and for P3-D
  alike. The check therefore cannot estimate an out-of-sample FPR. It establishes neither the true D3 FPR of P4-D nor
  a failure of IPCA. P4-D, and the P3-D window diagnostic, are not calibrated references for J4 until a separately
  approved control, whose data source, independence unit, calibration/evaluation split, sample size, target,
  uncertainty interval and verdict rule are fixed before any result is seen.

## Tests

| guarantee | test |
|---|---|
| recovery of span(Γ) on synthetic data, `K="select"` | `tests/test_ipca.py::test_recovery_principal_angles` |
| ALS stopping rule, initialization independence, non-increasing objective | `test_als_projector_stopping` |
| NaN is an absent asset, never a zero | `test_missing_is_not_zero` |
| K bound, deficient days, rank of C̃_tΓ | `test_rank_bound_and_deficient_days` |
| held-out R² against an independent recomputation | `test_heldout_r2_definition` |
| uncentred whitening, z(0) = 0 | `test_whitening_uncentered` |
| odd head bit for bit, even head symmetric | `test_odd_head_exact` |
| cash-neutral invariance | `test_cash_neutral_invariance` |
| pretrain / calib separation | `test_pretrain_calib_separation` |
| monitor rows leave the extracted state unchanged | `test_extract_monitor_rows_do_not_move_state` |
| extraction CLI guards | `test_extract_cli_refuses_d2_and_plain_char_datasets` |
| `k_selection.csv` matches the code on `d3_239` | `test_real_d3_239_selection` |
| faulty beta formula reproduces the stored characteristic; audit CSV matches the code | `test_beta_denominator_reproduces_stored` |
| audit values finite | `test_char_audit_values_are_finite` |
| D3 contracts through `CHAR_CASES["ipca"]` | `tests/test_contracts.py` |
| P4 wiring | `tests/test_pipelines.py::test_p4_wiring` |

## References

- Kelly, B., Pruitt, S. and Su, Y. (2019). Characteristics are covariances: A unified model of risk and return.
  Journal of Financial Economics, 134(3), 501–524.
