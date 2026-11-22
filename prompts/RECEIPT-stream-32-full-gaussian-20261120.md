# Stream 32 — Full Gaussian campaign receipt

22 November 2026. The Full Gaussian campaign reached `COMPLETE` after ten invocations. All six staging phases were verified, with no pending partitions. The independent pre-ALT and ALT audits passed. The three preregistered claims carry `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR`. The primary INFO cell retains `NULL_INCONCLUSIVE` in the individual HOLD check. [Researcher GO](GO-stream-32-full-20261120.md) · [Independent scientific audit](AUDIT-stream-32-full-gaussian-20261122.md)

## Scope and identity

The campaign covers `EXACT` and `FITTED_LW_GAUSSIAN`, at N = 32 and 239, fit 0, with RESIDUAL and MARKET. The authorized descriptor matched the frozen descriptor byte for byte. R3-A uses 10,000 CAL paths for each of the three primary RESIDUAL policies and 2,000 CAL paths for each remaining cell. `NULL_PLAN` used 2,000 independent null paths and selected `n_hold = 20,000` at the cap for the same three policies. All remaining HOLD cells used 2,000 paths. ALT used 2,000 paths per family and setup. R4 uses asymptotic Tango and R5 conditions on the frozen fit. [Frozen configuration](../configs/pca_info_online_full.yaml) · [Authorized descriptor](../logs/stream-32/full-gaussian-authorized-describe.json)

| Identity | SHA-256 |
| --- | --- |
| `full_design_id` | `8a4af3ecd7864f167ac32b82f0751547dc68b8a4bf24cec0f6c7fefbb19895d4` |
| Seed plan | `88e7c755bb33cd48c57bab000959cac09f4efb9211545951e4fc89469979c450` |
| Realization | `d574db30705b7257567131dd5fdf3c26c4308b4de32f7a5382b34b853457646a` |
| `manifest.json` | `16f5fdcfca5c08a97d8a6ff01a0cdf807b614b0d2321bf17b0abb0d9d86e0cbf` |
| `FINAL.json` | `d9a0c88bc845f589e5e7318dbb63e338b03ef119bd8036f591930c711a7dff4a` |
| Frozen scientific YAML | `34d8addc6b4c91c821c94e0e075d2873952a7118203b3882942d99e46b278539` |
| Authorized YAML | `8c5cc30f0a3e269b557d4c576efb237d0dabd24a6cba21f1e0f795804eb8317a` |
| Scientific runner | `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec` |
| Researcher GO | `fbab945d08c4716176714b0d0f7d3ea57dad7085a52a49ece7ccd126bb9db2fb` |
| Independent auditor | `b908760845cef42ab707fbb6384f8e3bde78e64d342be1134803c6cd7dd999dc` |
| Terminal CPU ledger | `32dbedd42523b024713cdf40a00c1bda1a2baeb42da1e470ccd6fa0b8d05d154` |

The successful invocation `b03d7211a0a84efb9159abb2ac4485eb` recorded `PUBLISHED` with zero missing partitions. `FINAL.json` binds the `COMPLETE` manifest, and the independent auditor reproduced the realization ID. The local inventory contains 104 partitions across SETUP, DEV, CAL, NULL_PLAN, HOLD and ALT, in counts of 4, 36, 9, 1, 34 and 20. Every staged NPZ and published CSV remained below 50 MiB. [Manifest](../results/pca_info_online/full-gaussian/manifest.json) · [FINAL](../logs/stream-32/full-gaussian-staging/staging/8a4af3ecd7864f16/phases/FINAL.json)

| FAIR payload | Data rows | SHA-256 |
| --- | ---: | --- |
| `aggregates.csv` | 531 | `dac28abbe5434e6fcff410ebd39667e57afd977c8bcb32223e8a4cea8d0b6293` |
| `calibration.csv` | 179 | `18ae7a421e8e66a846171935f39aa0f6f4eac2be7c17075a670c1bb6f7d69021` |
| `issues.csv` | 107 | `4f5fd3d91b7fca4a263cf02db989a495da5d5a2f0ee4037acf0e8a542fecdcb9` |
| `selections.csv` | 350 | `19908ef428122e2c3cfbea0360ffc220fed6f718c6057c8396104b43a2fb4ac0` |
| `trials_summary.csv` | 529 | `75ffa6713e618bee24934d5082a14188f54f6e625418184c493a38065d4129f1` |

## Resource accounting and resume

All ten invocations used one worker. The first nine reached `CLEAN_BLOCKED_RESOURCE`, then resumed manually after checks of the CPU receipt, stopped scope, lock availability, staging inventory and memory events. Each invocation ran under the 2,700 s wall and 32 GiB memory ceilings. All receipt hashes matched. Every recorded memory-event counter was zero. The table uses `elapsed_to_stop_seconds` from the supervisor. The application guard uses a 700 s offset in the displayed application clock to request a clean stop at a checkpoint after 2,000 s real time. [CPU ledger](../logs/stream-32/full-gaussian-supervisor/ledger.json) · [Final invocation receipt](../logs/stream-32/full-gaussian-supervisor/b03d7211a0a84efb9159abb2ac4485eb.receipt.json)

| Measure | Observed value |
| --- | ---: |
| Measured CPU across scopes | 21,289.902 s |
| CPU charged, including conservative rounding | 21,294 s |
| CPU remaining from 36,000 s | 14,706 s |
| Cumulative time to scope stop across invocations | 21,443.877 s |
| Longest invocation | 2,530.046 s |
| Highest aggregate `memory.peak`, invocation 2 | 4,054,790,144 bytes |
| Staging disk allocated | 1,415,135,232 bytes |
| Publication disk allocated | 1,470,464 bytes |
| Largest staged NPZ | 44,380,368 bytes |
| Largest published CSV | 1,020,749 bytes |

## Audit and closure

The auditor SHA matched its qualification seal. The pre-ALT report was closed and sealed at `2026-11-22T14:23:14Z` with 174 verified staging input files. The ALT run rechecked that seal, reproduced the three decisions and published its report at `2026-11-22T14:23:34Z`. The ALT report binds 215 staging files and the publication hashes. Both reports record zero discrepancies. All 106 inconclusive HOLD checks and the capped-plan status remain in `issues.csv`. The Gaussian Pilot and its four null failures retain their own results. [Pre-ALT seal](../logs/stream-32/full-gaussian-audit-pre-alt.seal) · [ALT seal](../logs/stream-32/full-gaussian-audit-alt.seal) · [Traceability](../docs/MAPPING.md#stream-32-full-gaussian)

The shared lock was available and all ten experiment scopes had stopped at closeout. The authorized Full Gaussian campaign is closed. T7, real or `2020+` data, JEPA, wrap-up, reindexing, commit and push remain outside this mandate.
