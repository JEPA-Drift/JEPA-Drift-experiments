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

## Not covered under GO-A
Source-filtered reading of `d3_239` (no monitor row read by `jepa_pretrain`), the NaN path through the shared base
(`Representation.missing` of Stream 17), the registry entry and `--ckpt`/`--D` in `extract.py`, the characteristic
contracts and the four real-model guards in `tests/test_contracts.py`: GO-B, after the Stream 17 base is final.
