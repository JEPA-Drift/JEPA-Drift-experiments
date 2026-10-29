# Audit — CA-T-JEPA leakage and mask handling (stream 14, GO-A, synthetic data)

## Dependency graph of the context side
x_masked → u_masked → (a) features of masked tokens: zeroed before the token MLP (`masked_fill`) and excluded from
attention keys (`src_key_padding_mask`); (b) f̂(V): computed from `u.masked_fill(~visible, 0)` and `b` on the visible
set only. Hence the context tokens, f̂(V), the bottleneck z_ctx and the predictions are functions of the visible
returns, all characteristics and the frozen state only. The masked returns reach the loss only through the EMA
targets, computed without gradient. Frozen constants (s, b, medians) come from the internal estimation rows; the
training core refuses rows dated on or after 2016-01-01.

## Evidence (`tests/test_ca_tjepa.py`, all passing under GO-A)
| Property | Test | Witness that must fail |
|---|---|---|
| Masked returns (×1000 noise) leave f̂(V), context tokens, z_ctx and predictions bit-identical, for `group` and `random` masks and a 4-asset day with one oversized group | `test_context_ignores_masked_returns` | targets of masked tokens do change (asserted) |
| A statistic of the full cross-section computed before masking leaks | `test_full_section_statistic_before_masking_is_detected` | f̂ and context tokens change (asserted) |
| Mask shares within [⌈0.3 n⌉, ⌊0.5 n⌋] for n ∈ {4, 5, 7, 10, 24, 239}; oversized and empty groups, absent assets, n < 4 refused | `test_mask_share_bounds`, `test_group_mask_oversized_empty_and_absent` | — |
| Ties, `nochar`, `sector_pit` refusal | `test_group_codes_ties_and_nochar`, `test_sector_pit_refused` | — |
| Rows after `pretrain_end` refused; validation and embargo rows change neither the frozen state nor the trained weights | `test_rows_after_pretrain_refused_and_holdout_rows_unused` | — |
| Exact oddness (zero, permutation, ×1000, market-only days); ties broken by the coin of `exact_sign_stream` | `test_parity_exact` | — |
| Permutation equivariance (float32 tolerance 1e-5) | `test_asset_permutation_equivariance` | — |
| Frozen extraction: weights and state unchanged, repeated extraction identical | `test_extraction_is_frozen` | an EMA update inside `_day` changes the weights (asserted) |
| Deterministic training, global torch and numpy RNG untouched | `test_training_is_deterministic_and_leaves_global_rng` | `torch.randn` changes the global state (asserted) |
| Checkpoint integrity | `test_checkpoint_integrity` | a flipped byte is refused |

## GO-B and GO-B2 additions (real `d3_239` pretrain path)
| Property | Test | Witness that must fail |
|---|---|---|
| The pretrain reader opens only row group 0 of each Parquet file and never `ret_wide.npy`; monitor rows (+inf) never reach the arrays | `test_pretrain_reader_never_opens_monitor`, `test_real_pretrain_reader` | a poison `ret_wide.npy` that `np.load` refuses |
| Overlap with monitor, missing date statistics, missing, duplicate or extra keys, ±inf, null `in_universe`, NaN return inside the universe stop the read | `test_pretrain_reader_validates_inputs` | — |
| Calib rows inside the read row group change neither the pretrain arrays nor the checkpoint | `test_calib_rows_of_a_read_group_do_not_reach_training` | — |
| Real-panel integrity gates (2,769 × 239, SHA-256 `3115d872…`, 8 NaN in `c_beta_252`) and equality with the Stream 17 fixture | `test_real_pretrain_reader` | — |
| Masked returns on real pretrain days leave the context side bit-identical, `group` and `random` masks | `test_context_ignores_masked_returns_on_real_days` | — |
| Asset identity bound before `fit`; permutation, missing list and unbound-with-IDs refused; registry and CLI options | `test_asset_identity_binding`, `test_registry_and_cli_options`, `test_real_training_requires_asset_ids` | — |
| Characteristic contracts with `CALIB_FREE` and the four real-model torch guards | `tests/test_contracts.py` | each guard's faulty witness |

Remaining limit: a direct Z-1 call `fit(X, C, dates)` on arrays cannot verify that the caller's columns follow the
checkpoint's asset order; the CLI relays the dataset's `assets.json` order and `CATJEPA` checks it.
