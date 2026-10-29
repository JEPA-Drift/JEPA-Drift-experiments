# CA-T-JEPA (stream 14) — native compact representation, visible-only masking

Status: GO-A synthetic core, then GO-B and GO-B2 on the local Stream 17 base (`6ed8f8a`, merged as `93370e4`): real
`d3_239` pretrain reader, `ca_tjepa` registration, characteristic contracts and real-model torch guards. Real-data
smokes are engineering checks only. Governing text: the v2 directive `prompts/streams/01_STREAM_14_REWRITE_BOTTLENECK.md`
of the main checkout (SHA-256 `1b5f2f8e…62c3`), `prompts/GO-stream-14-A.md`, `prompts/GO-stream-14-B.md`,
`prompts/GO-stream-14-B2.md` and `prompts/plans/plan-14.md`.

## Architecture (`jepadrift/jepa/ca_tjepa.py`)
- **Frozen inputs.** On the internal estimation rows only: s_i = RMS of the observed returns (refused below
  `min_obs` = 63 observations); b = unit PC1 of the second-moment matrix of u = x / s with absent cells zero-filled
  (`stats.covariance.eigh_desc`, sign with Σb ≥ 0); four medians of the continuous characteristics. Coverage
  diagnostics are written to the checkpoint.
- **Visible-only neutralization.** f̂(V) = b_Vᵀu_V / (b_Vᵀb_V + λ_f), e_i = u_i − b_i f̂(V); no statistic of the full
  cross-section reaches the context. The EMA targets use the same f̂(V) without gradient.
- **Context encoder.** Token = MLP([e_i, C_i]) (C through `impute_zero`); masked and absent tokens are zeroed before
  the MLP and excluded by `src_key_padding_mask`; 3 pre-LN self-attention layers (d_model 64, 4 heads, FFN 256,
  dropout 0, GELU), final LayerNorm, no positional encoding, no BatchNorm.
- **Native bottleneck.** z_ctx = Linear(64 → d)(mean of the visible context tokens), d ∈ {2, 4, 8, 16} fixed before
  training. The predictor is a two-layer MLP on [z_ctx, C_j] for each masked asset j: it never sees individual
  context tokens.
- **Target encoder.** EMA copy of the token MLP and encoder, initialized equal to the context encoder, updated with
  a cosine momentum from 0.996 to 0.9995 over the planned steps [Grill et al., 2020]; L_JEPA is the latent MSE on
  masked tokens [Assran et al., 2023].
- **Extraction.** Frozen context encoder with mask=none (V = present assets): z_odd = [f̂(P), (g(x) − g(−x)) / 2]
  (d + 1 columns, `channels = {"market": [0], "residual": [1..d]}`), z_even = (g(x) + g(−x)) / 2 (d columns).
  Oddness is exact: both evaluations are deterministic and f̂ is linear.

| d | context | head | predictor | EMA target | total |
|---|---|---|---|---|---|
| 2 | 154,624 | 130 | 9,152 | 154,624 | 318,530 |
| 4 | 154,624 | 260 | 9,408 | 154,624 | 318,916 |
| 8 | 154,624 | 520 | 9,920 | 154,624 | 319,688 |
| 16 | 154,624 | 1,040 | 10,944 | 154,624 | 321,232 |

## Objective and fixed constants (`configs/ca_tjepa.yaml`)
L = L_JEPA + λ_var L_var + λ_cov L_cov + λ_market L_market. L_var (hinge std ≥ 1) and L_cov (off-diagonal energy over
d(d − 1)) apply to both extracted heads z_odd and z_even of the mask=none view across the days of a batch
[Bardes et al., 2022]; a batch with fewer than 2 days is an error. L_market (squared covariance with f̂) is implemented
with λ_market = 0. Fixed before any training: λ_var = 1, λ_cov = 0.04, λ_market = 0, λ_f = 1e-3, AdamW (lr 1e-3,
weight decay 0.01), batches of 64 days, at most 200 epochs, internal validation from 2014-01-01 with a 65-day embargo,
patience 10, mask share ρ ~ U[0.3, 0.5] per batch. Nothing is tuned on calib or monitor rows.

## Masks
- Dictionary frozen in the checkpoint: code = Σ_k 2^k 1{C_k > m_k} ∈ {0..15}; a tie C_k = m_k gives bit 0; any NaN
  characteristic gives `nochar` (16); an absent return puts the asset in no group (neither visible nor masked).
  Assignment uses C_t only, known at the open of day t.
- Selection per day with n present assets (days with n < 4 are not used): lo = ⌈0.3 n⌉, hi = ⌊0.5 n⌋,
  target = min(hi, max(lo, ⌈ρ n⌉)); the non-empty groups are visited in a random order, a whole group is added when it
  keeps the count ≤ hi (larger groups are skipped), the visit stops at the target; if the count stays below lo, a uniform
  fill reaches lo and the day is counted as partial. Empty groups consume no draw.
- `random` (diagnostic): ⌈ρ n⌉ uniform assets within [lo, hi]; `none`: extraction; `sector_pit`: refused
  (`C-D3-gics-static`).
- Local generators only: `SeedSequence([14, seed, usage])` with usages init 0, batches 1, train masks 2, eval masks 3,
  synthetic data 4; parameter initialization runs under `torch.random.fork_rng`, so the global RNG is untouched.

## Training, checkpoints and the no-coupling control (`experiments/jepa_pretrain.py`)
`--data {synthetic, control, d3_239}`; `--smoke` = 200 days and 2 epochs; `--d` fixes the width; `--fingerprints DIR`
writes `<hash>.json` (configuration, metrics and the SHA-256 of `config.json` and `weights.npy`, no weights); the script
prints `CHECKPOINT_PATH=<absolute directory>`. The training core refuses any row dated on or after 2016-01-01. A checkpoint
directory is named by SHA-256(config.json + weights.npy); `config.json` holds the resolved configuration, frozen state,
group dictionary, seed scheme, split, data fingerprints, versions and per-part weight checksums; `metrics.json` holds the
loss history, the selected epoch, head diagnostics (std, off-diagonal energy, RankMe [Garrido et al., 2023]) and the
constant-predictor baseline; `run.json` holds the wall time (outside the hash).
The control panel (`--data control`) has one Gaussian factor and i.i.d. idiosyncratic shocks with characteristics drawn
independently of returns: no residual coupling. The constant predictor is the mean training target (MSE-optimal
constant); L_model and L_const use the same validation days, masks and selected weights. Reading rule: residual coupling
is readable only when the gain 1 − L_model / L_const on a real panel exceeds the gain on the control, because the EMA
target also attends to visible assets (`coupling_readable`).

## Real `d3_239` pretrain path (`--data d3_239`)
`load_pretrain` returns (X, C, dates, assets) from the filtered Parquet row groups: `ret` and `in_universe` from
`panel.parquet`, the four continuous characteristics from `chars.parquet`, only from row groups whose date statistics
start before 2016-01-01; a selected row group reaching 2020-01-01, missing date statistics, rows outside their stated
bounds, duplicate, missing or extra date × asset keys, any infinity, a null `in_universe` or a NaN return inside the
universe stop the read. `ret_wide.npy` (Fortran order) is never opened; calib rows of row group 0 are dropped in Arrow.
Gates on the real panel: 2,769 dates (2005-01-03 → 2015-12-31) × 239 assets = 661,791 keys per file, C-order SHA-256 of
the returns `3115d872…4830` (bit-identical to `ret_wide.npy`), 8 NaN characteristics, all in `c_beta_252`.
`train_real` requires the ordered, unique asset IDs and the checkpoint keeps only their SHA-256 (`assets_sha256`);
`ca_tjepa.train` itself refuses a declared non-synthetic `data["source"]` without asset IDs, before any computation or
checkpoint write. Arrays passed without truthful provenance cannot be recognized as real data automatically; the Z-1
API is not broadened for that purpose. The smoke takes 200 contiguous pretrain days: 100 estimation days, the 65-day
embargo and 35 validation days.

Engineering results (one thread, 2 epochs): about 11–12 s per width d ∈ {2, 4, 8, 16}; two d = 8 runs give the same
checkpoint; two full CLI extractions with the d = 8 checkpoint are byte-identical. Smoke losses carry no scientific
reading. `c_beta_252` carries `C-D3-beta-denominator` into the tokens and the group dictionary (no correction);
`C-D3-chars-phantom` reports no phantom cell on `d3_239`.

## Representation (`jepadrift/jepa/representation.py`)
`CATJEPA(ckpt, D=None, assets=None)` verifies the checkpoint SHA-256 (D must equal d) and the asset identity before
`fit` or any extraction: a bound checkpoint needs the dataset's ordered IDs with the same digest (a same-size
permutation fails), an unbound synthetic checkpoint takes none. It sets `missing = True` and fits nothing on the fit
rows: `state = {s, b, weights}` (the arrays used at extraction), `stats` counts imputed characteristics and absent
cells, no `pretrain` hook, day-by-day `transform_panel` from the base class. An extraction day needs at least 2 observed
assets; ±inf in x or C is refused. Its `state_hash` does not move with the fit rows: `test_char_no_test_statistics`
requires exactly that for the members of `CALIB_FREE`. The registry entry `ca_tjepa` is a lazy factory; the CLI
requires `--ckpt` and relays the dataset's ordered asset IDs.

## Environment
torch 2.14.1 `cpu_generic_py312_h29917d7_0` and its 64 dependencies come from `conda-torch.lock` (`@EXPLICIT`, 65
conda-forge URLs with SHA-256), installed offline with `--copy` into `.venv/torch-cf` and reached through a
`PYTHONPATH` shim that appends its site-packages after the venv; numpy, scipy and pandas still resolve from `.venv`.
The parent `.pth` bridge is pending until no other stream uses `.venv`.

## Migration notes for streams 16 and 22 (not launched)
- One checkpoint per width d: the D sweep {2, 4, 8, 16} means four trainings per objective and seed; `--D` only asserts
  the checkpoint width. The PCA-whitened readout of the earlier design is an ablation (`post_pca_legacy`).
- z_odd has d + 1 columns (market column 0); z_even has d columns; extraction uses the frozen context encoder.
- `mae`, `temporal`, `post_pca_legacy` and `orthogonal_head` are not implemented under GO-A.
- Any bootstrap null reading of an even-head monitor on `d3_239` with H = 750 inherits the window degeneracy recorded by
  Stream 17 for P3-D and P4-D; no calibrated reading is claimed here.

## References
[Assran et al., 2023, Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture];
[Grill et al., 2020, Bootstrap Your Own Latent]; [Bardes, Ponce, LeCun, 2022, VICReg];
[Garrido et al., 2023, RankMe]; [Kelly, Pruitt, Su, 2019, Characteristics Are Covariances].
