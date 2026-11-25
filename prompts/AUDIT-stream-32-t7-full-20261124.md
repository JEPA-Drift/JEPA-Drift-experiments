# Stream 32 Student-t7 — Full analysis

The Full T7 contains 240 `DESCRIPTIVE_NOMINAL` contrasts, four `DESCRIPTIVE_V_RMST` diagnostics and zero confirmatory rows. Of 87 HOLD cells, 28 are `NULL_VALIDATED` and 59 are `NULL_INCONCLUSIVE`. The complete FAIR exports preserve all cells, contrasts and issues. [Receipt and hashes](RECEIPT-stream-32-t7-full-20261124.md) · [Mapping](../docs/MAPPING.md#stream-32-student-t7-full)

## Calibration and achieved false-alarm rates

The design uses `FITTED_LW_T7` at N = 32 and 239 with `fit_id=0` (`FIT_CONDITIONAL`), RESIDUAL and MARKET, and horizon H = 250. All 87 CAL cells used 2,000 paths and `predictive_exchangeable_rank_v2`, with `r=99` and 99 CAL maxima at or above the realized GE threshold in each cell. The marginal new-path bound through day 250 is 100/2,001 (4.9975%), integrating over exchangeable CAL paths at the frozen fit. The FPR conditional on the realized threshold is estimated on the independent HOLD cohort. Each HOLD cell uses 2,000 paths with one-sided Clopper–Pearson bounds at tail 0.05. `NULL_VALIDATED` requires the upper bound to be at most 6%, `NULL_FAILED` requires the lower bound to exceed 6% for a valid design, and `NULL_INCONCLUSIVE` covers the remaining intervals. [Calibration](../results/pca_info_online/t7-full/calibration.csv) · [Amendment](AMENDMENT-stream-32-t7-20261122.md)

| N | Application | Setup ID | HOLD alarms per 2,000, min–max | Validated | Inconclusive | Failed |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 32 | RESIDUAL | `2c0071747a35050c` | 91–134 | 2 | 27 | 0 |
| 32 | MARKET | `6359fff6a3a68700` | 90–133 | 11 | 4 | 0 |
| 239 | RESIDUAL | `5c438adbba94afb6` | 89–126 | 8 | 21 | 0 |
| 239 | MARKET | `45083d2c9a7a85be` | 92–112 | 7 | 7 | 0 |
| **Total** | | | **89–134** | **28** | **59** | **0** |

Both roles of every contrast were joined to their HOLD rows by design, setup, application, policy, family where applicable and calibration ID. **`NULL_FAILED — NOT_CLAIMABLE` applies to zero Full T7 contrasts** (`not_claimable: []`). Seven contrasts have two validated HOLD cells, 68 have one inconclusive cell and 165 have two inconclusive cells. All 59 inconclusive HOLD rows appear in `issues.csv`. [Trials](../results/pca_info_online/t7-full/trials_summary.csv) · [Issues](../results/pca_info_online/t7-full/issues.csv) · [ALT report](../logs/stream-32/t7/full/03abb171a86076e1/audit-alt.json)

## ALT outcomes and paired contrasts

`RMST_250` is the mean of the first alarm day capped at 250. Censored paths contribute 250 days and remain distinct from alarms on day 250. The 165 ALT cells each use 2,000 paths. The paired difference is candidate minus reference. Its nominal 95% percentile interval uses 10,000 paired bootstrap replicates per ALT partition and `deff=1` for independent paths conditional on the fit. The count columns below classify the interval relative to zero and retain each direction and every unresolved interval. The full contrast rows also carry exact calibration keys, RMST ratios, detected and censored fractions, and medians given detection. [Entire trials table](../results/pca_info_online/t7-full/trials_summary.csv) · [Entire contrasts table](../results/pca_info_online/t7-full/aggregates.csv)

| N | Family | ALT cells | RMST range (days) | Detected range | Shorter | Longer | Includes zero |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | `F0_ISOTROPIC_RESIDUAL` | 17 | 74.427–122.029 | 96.45–100% | 10 | 14 | 1 |
| 32 | `F1_TAIL_RESIDUAL` | 17 | 61.788–247.124 | 5.15–100% | 11 | 11 | 3 |
| 32 | `F2_STRUCTURED_RESIDUAL` | 17 | 68.638–116.951 | 99.85–100% | 10 | 13 | 2 |
| 32 | `F3_MARKET` | 15 | 54.256–79.972 | 100% | 10 | 11 | 0 |
| 32 | `F_HEAD_RESIDUAL` | 17 | 60.829–79.305 | 100% | 16 | 9 | 0 |
| 239 | `F0_ISOTROPIC_RESIDUAL` | 17 | 74.618–111.036 | 98.75–100% | 6 | 17 | 2 |
| 239 | `F1_TAIL_RESIDUAL` | 17 | 68.911–247.061 | 5.55–100% | 10 | 15 | 0 |
| 239 | `F2_STRUCTURED_RESIDUAL` | 17 | 68.883–107.864 | 99.90–100% | 9 | 14 | 2 |
| 239 | `F3_MARKET` | 14 | 44.956–82.677 | 100% | 10 | 8 | 1 |
| 239 | `F_HEAD_RESIDUAL` | 17 | 55.846–80.025 | 100% | 15 | 9 | 1 |
| **Total** | | **165** | | | **107** | **121** | **12** |

The 230 deployable contrasts contribute 97 shorter, 121 longer and 12 intervals containing zero. Their paired HOLD FPR differences span −1.25 to +1.75 percentage points. Tango asymptotic 95% intervals include zero on 210 contrast rows, lie entirely below zero on 5 and entirely above zero on 15. Across 86 distinct ordered HOLD calibration pairs, the corresponding counts are 78, 2 and 6. Repeated families share their HOLD pairs. The 10 `ORACLE_SEPARATE` contrasts compare the non-deployable `ORACLE_INFO_MIX` with `ONLINE_INFO_MIX_W128`. Their RMST differences range from −19.260 to −8.364 days with all ten intervals below zero. Their separate HOLD FPRs are 4.45–6.30% for the oracle and 4.90–5.80% for the reference. [Contrasts and intervals](../results/pca_info_online/t7-full/aggregates.csv)

### INFO versus PREFIX at window 128

All ten `ONLINE_INFO_MIX_W128` minus `ONLINE_PREFIX_MIX_W128` comparisons detect 2,000 of 2,000 paths per policy. INFO is slower for F0 at both dimensions and faster on the other four families at both dimensions by the nominal RMST intervals. Each corresponding paired FPR interval includes zero. Every pair has at least one inconclusive HOLD cell. The intervals describe one fixed fit per dimension and support no general superiority or FPR equivalence claim. [Aggregate estimates and uncertainty](../results/pca_info_online/t7-full/aggregates.csv)

| N | Family | INFO RMST | PREFIX RMST | Difference [nominal 95% interval], days |
| ---: | --- | ---: | ---: | --- |
| 32 | `F0_ISOTROPIC_RESIDUAL` | 86.939 | 84.989 | +1.950 [+1.375, +2.535] |
| 32 | `F1_TAIL_RESIDUAL` | 75.746 | 88.356 | −12.610 [−13.134, −12.110] |
| 32 | `F2_STRUCTURED_RESIDUAL` | 84.447 | 89.962 | −5.516 [−6.095, −4.933] |
| 32 | `F3_MARKET` | 62.620 | 76.425 | −13.806 [−14.125, −13.484] |
| 32 | `F_HEAD_RESIDUAL` | 73.646 | 77.841 | −4.195 [−4.570, −3.815] |
| 239 | `F0_ISOTROPIC_RESIDUAL` | 87.933 | 86.215 | +1.718 [+1.161, +2.267] |
| 239 | `F1_TAIL_RESIDUAL` | 80.093 | 91.969 | −11.876 [−12.418, −11.336] |
| 239 | `F2_STRUCTURED_RESIDUAL` | 86.228 | 90.303 | −4.076 [−4.606, −3.542] |
| 239 | `F3_MARKET` | 64.216 | 79.400 | −15.184 [−15.515, −14.851] |
| 239 | `F_HEAD_RESIDUAL` | 72.910 | 80.025 | −7.115 [−7.505, −6.719] |

| N | Application | INFO / PREFIX calibration IDs | HOLD discordances (INFO only / PREFIX only) | ΔFPR [Tango interval], percentage points | HOLD INFO / PREFIX |
| ---: | --- | --- | ---: | --- | --- |
| 32 | RESIDUAL | `566dbdd95be5e464` / `73ec7911701c6cb7` | 70 / 60 | +0.50 [−0.626, +1.637] | Inconclusive / inconclusive |
| 32 | MARKET | `3147116e7cea5ed5` / `6a2969e750036ad5` | 47 / 55 | −0.40 [−1.412, +0.600] | Validated / inconclusive |
| 239 | RESIDUAL | `f99e484cc70a90d7` / `612c60b4dfc19121` | 55 / 59 | −0.20 [−1.264, +0.859] | Inconclusive / inconclusive |
| 239 | MARKET | `64a4d6a88f6ad734` / `9bc7446ea96af039` | 59 / 61 | −0.10 [−1.190, +0.987] | Inconclusive / inconclusive |

## Gaussian working-model proxies

`GAUSSIAN_PROXY` identifies the SETUP information and HEAD geometry. The pre-ALT audit replayed all 16 HEAD sign profiles for each RESIDUAL setup. The minimum prefix fractions `f_E` and `f_pop` are 0.8879 and 0.8875 for N = 32, and 0.8991 and 0.8815 for N = 239. Both minima exceed the design cutoff 0.8 at each dimension. All 165 selections carry `ORACLE_DIAGONAL_GAUSSIAN_PROXY` (`info_basis`) and `ANALYTIC_PROXY` (`metric_basis`). The four Spearman correlations compare the diagonal and joint information-to-cost diagnostics with RMST across ALT cells. Their interpretation is conditional on the fitted working model, with no exact Student-t7 KL or theoretical detection-time interpretation. [Amendment](AMENDMENT-stream-32-t7-20261122.md) · [Pre-ALT report](../logs/stream-32/t7/full/03abb171a86076e1/audit-pre-alt.json) · [Selections](../results/pca_info_online/t7-full/selections.csv)

| N | Application | Diagnostic cells | Spearman ρ, diagonal | Spearman ρ, joint |
| ---: | --- | ---: | ---: | ---: |
| 32 | RESIDUAL | 68 | −0.9306 | −0.9142 |
| 32 | MARKET | 15 | −0.6873 | −0.7091 |
| 239 | RESIDUAL | 68 | −0.9541 | −0.9453 |
| 239 | MARKET | 14 | −0.5775 | −0.6000 |

## Measured resources

| Invocation prefix | State | Cgroup CPU (s) | CPU debit (s) | Wall to stop (s) | Cgroup peak (bytes) |
| --- | --- | ---: | ---: | ---: | ---: |
| `965d0c78` | `CLEAN_BLOCKED_RESOURCE` | 2,161.560395 | 2,162 | 2,173.867 | 1,098,981,376 |
| `07a8a599` | `CLEAN_BLOCKED_RESOURCE` | 2,635.068142 | 2,636 | 2,650.470 | 1,064,960,000 |
| `7acab1a2` | `CLEAN_BLOCKED_RESOURCE` | 2,158.562622 | 2,159 | 2,171.298 | 1,214,898,176 |
| `d9ae2e6a` | `CLEAN_BLOCKED_RESOURCE` | 2,273.977111 | 2,274 | 2,287.414 | 1,471,590,400 |
| `d2017740` | `COMPLETE` | 1,016.536414 | 1,017 | 1,022.184 | 1,363,525,632 |
| **Total / maximum peak** | | **10,245.704684** | **10,248** | **10,305.233** | **1,471,590,400** |

The producer used one worker and one logical CPU per invocation. The CPU debit was 2.847 h against a 6 h cap, with zero reserved seconds outstanding. The maximum invocation wall time was 2,650.470 s against 2,700 s. Active invocation wall times sum to 2.863 h. Elapsed time from the first reservation to the terminal receipt was 16,250.961 s (4.514 h), including gaps between invocations. The maximum cgroup `memory.peak` was 1,403.42 MiB against 8 GiB, with zero OOM, OOM-kill or group-kill events. Producer telemetry reports 10,224.92 s cumulative CPU and 1,017.865 s application wall for the final invocation. [Ledger and receipt paths](../logs/stream-32/t7/full/03abb171a86076e1/supervisor/ledger.json) · [Producer telemetry](../results/pca_info_online/t7-full/telemetry.json)

| Retained footprint | Allocated bytes |
| --- | ---: |
| Staging | 655,220,736 |
| FAIR publication and metadata | 630,784 |
| Supervisor evidence | 200,704 |
| **Producer total** | **656,052,224 (625.66 MiB)** |
| Two independent audit JSON reports | 536,576 |

Disk values are post-run allocations from `du -B1`. Staging retains 90 files and the largest NPZ is 58,479,972 bytes. Publication contains 606,943 content bytes across eight files. Transient peak disk is unmeasured. The independent `--pre-alt` and `--alt` passes respectively used 22.50 and 188.09 process CPU seconds (user plus system), 22.60 and 189.01 wall seconds, and 419,844 and 858,284 KiB maximum RSS from `/usr/bin/time`. These audit measurements are outside the producer ledger. [Staging resource journal](../logs/stream-32/t7/full/03abb171a86076e1/run/staging/03abb171a86076e1/resources.json) · [Audit evidence](RECEIPT-stream-32-t7-full-20261124.md#pre-alt-seal)
