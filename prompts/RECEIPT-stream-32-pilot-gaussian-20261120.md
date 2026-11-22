# Stream 32 — Gaussian pilot receipt

20 November 2026. The R2 Gaussian pilot completed and passed the publication, lineage and resource checks. The §18 null gate failed because four non-oracle calibration cells were `NULL_FAILED`. T7 stays closed. The scientific outputs retain their `PILOT_ONLY` qualification. [R2 authority](GO-stream-32-pilot-20261120.md) · [Plan](plans/plan-32.md) · [Audit results](../logs/stream-32/pilot-gaussian.audit.json)

## Scope and publication

| Identity | SHA-256 |
| --- | --- |
| Design | `750443a8413d477e0350c66061eed0c25784b9857cc7d3a6aa7ec2f62ca292e9` |
| Seed plan | `fe2184a6c6e5f2c30eb21eab36513fa8f63c9862bf204b0b174bd51b0451ac6e` |
| Realization | `ede212c81c5cd7f98475f271ae56499e47af1d03a4132bd4f3ae715c427c672d` |
| Manifest | `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8` |
| Authorization GO | `8bfc6019c86a053c068031b3234eda46f66e203948c8d96ad16f36dec17acbd2` |

The four configurations were `EXACT` and `FITTED_LW_GAUSSIAN` at N = 32 and 239, each with fit 0. CAL, HOLD and each ALT family used 200 paths per planned cell. DEV used the frozen 100/200/50 library, null and per-family ALT sizes. The primary `s2_dev` and `gamma_M` variants were included. The two YAML descriptors matched under the shared lock. The derived YAML changed only the authorization block. The R1 specifications and the sealed experiment sources kept their hashes. [Derived YAML](../logs/stream-32/pilot-gaussian.yaml) · [Descriptor](../logs/stream-32/pilot-gaussian.describe.json)

The auditor verified the `COMPLETE` manifest, the realization recomputed from staging, the `PUBLISHED` FINAL record and all 76 planned local payloads. SETUP, DEV, CAL, HOLD and ALT contributed 4, 36, 8, 8 and 20 partitions respectively. Pilot `NULL_PLAN` recorded `NOT_APPLICABLE` with zero partitions. Trace lines 422 and 423 show the single successful directory rename followed by the single successful FINAL rename. The largest campaign artifact was 8,000,256 bytes across the publication, staging and launcher evidence. The 50 MiB limit held. [Manifest](../results/pca_info_online/pilot-gaussian/manifest.json) · [FINAL](../logs/stream-32/pilot-gaussian-staging/staging/750443a8413d477e/phases/FINAL.json) · [Rename trace](../logs/stream-32/pilot-gaussian-attempt-1.strace.log)

| FAIR payload | Data rows | SHA-256 |
| --- | ---: | --- |
| `aggregates.csv` | 528 | `0b3f300e6c13af6392593479fcdfbb1d161c82d7bceb8ddc52f03af595447332` |
| `calibration.csv` | 179 | `fbe32e237508983425563a6d90d3ee5cad75ff1f10176cf980106cea2e6c1624` |
| `issues.csv` | 150 | `e953a3b2e05b50606cf88ccec64990cbb019f6e303759a0fc6b657c90fb257c6` |
| `selections.csv` | 350 | `c8d868123cc3eeef751a703cfdaa7acd747327070eedd910507543e9e9b4fc7c` |
| `trials_summary.csv` | 529 | `65cdd4aa8a91227cf7bbab7b7c0212faeae2834638903937f7db0b098434c5f3` |

All 520 descriptive contrast rows and their embedded inference records carry `PILOT_ONLY`. The eight V/RMST diagnostic rows carry `DESCRIPTIVE_V_RMST`. The auditor matched the planned role keys, fixed application universes, one family-free CAL and HOLD cell per non-oracle policy and application, and separate family-specific oracle calibration. ALT rows reuse their frozen CAL cell and the contrasts share bootstrap keys within each of the 20 setup/application/family groups. Seven targeted invariance fixture tests passed. Replay and cross-worker campaign equality were exercised in Lot C. This pilot used one worker in one invocation. [Fixture log](../logs/stream-32/pilot-gaussian.invariance-tests.log) · [Lot C receipt](RECEIPT-stream-32-C-20261120.md)

## Null qualification and HEAD

The auditor recounted all 179 HOLD cells from their first-hit vectors and reproduced their one-sided 95% Clopper–Pearson bounds and recorded status at the 0.06 cutoff.

| HOLD calibration | `NULL_VALIDATED` | `NULL_INCONCLUSIVE` | `NULL_FAILED` |
| --- | ---: | ---: | ---: |
| Non-oracle | 21 | 74 | 4 |
| Oracle, non-deployable | 8 | 72 | 0 |

| Setup, fit 0 | Application | Policy | Calibration ID | Alarms / 200 | CP lower bound |
| --- | --- | --- | --- | ---: | ---: |
| EXACT 239 | MARKET | `ONLINE_INFO_AFF_W128` | `902743ca294fea06` | 19 | 0.063106 |
| EXACT 239 | RESIDUAL | `ONLINE_INFO_AFF_W128` | `3c3eb9517a60d822` | 19 | 0.063106 |
| FITTED_LW_GAUSSIAN 239 | MARKET | `FIXED_EIGENMEAN_PREFIX` | `8491081f7f14e71a` | 24 | 0.084140 |
| FITTED_LW_GAUSSIAN 32 | MARKET | `FIXED_EIGENMEAN_PREFIX` | `3d21bbba6bd2cb96` | 26 | 0.092713 |

HEAD geometry was `GEOMETRY_ALIGNED` in each RESIDUAL setup, with κ_geo = 0.80 and 16 sign profiles. The audit JSON retains each profile and the full floating-point values. Table entries are rounded to six decimals. [SETUP record](../logs/stream-32/pilot-gaussian-staging/staging/750443a8413d477e/phases/SETUP.json)

| Setup, fit 0 | f_E min / mean / max | f_pop min / mean / max |
| --- | --- | --- |
| EXACT 32 | 1.000000 / 1.000000 / 1.000000 | 1.000000 / 1.000000 / 1.000000 |
| EXACT 239 | 1.000000 / 1.000000 / 1.000000 | 1.000000 / 1.000000 / 1.000000 |
| FITTED_LW_GAUSSIAN 32 | 0.954767 / 0.971219 / 0.987514 | 0.952807 / 0.970234 / 0.987381 |
| FITTED_LW_GAUSSIAN 239 | 0.953786 / 0.978417 / 0.991001 | 0.953628 / 0.977289 / 0.990221 |

The `PILOT_ONLY` replay of the primary HEAD prefix bound used the frozen bootstrap key, 10,000 index draws and 200 censored first-hit times. U_PREFIX was 84.11175 days at the one-sided 1 − 0.05/3 quantile. The descriptive classification was `PREFIX_DETECTABLE` at κ_det H = 200 days. Confirmatory H2 remains unissued. HOLD planning and the T7 entry decision use the null evidence exclusively. [Audit results](../logs/stream-32/pilot-gaussian.audit.json)

## R3 planning from primary HOLD_NULL

The primary FITTED_LW_GAUSSIAN N239, fit 0, RESIDUAL cohort had 200 aligned paths. Alarms were 12 for `ONLINE_INFO_MIX_W128` (`80ac6960b12838dc`), 10 for `ONLINE_PREFIX_MIX_W128` (`aca174986655b791`) and 13 for `FULL_K` (`ff8f1f9655543b09`).

| Pair, INFO first | b | c | Observed D | Observed Δ | D⁺ | Abs(Δ)⁺ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| INFO / PREFIX | 7 | 5 | 0.060 | 0.010 | 0.087618 | 0.033919 |
| INFO / FULL_K | 5 | 6 | 0.055 | −0.005 | 0.081826 | 0.027851 |

The conservative §10 calculation gives an unbounded n_eq for both pairs and an unbounded n_v for all three policies. The F⁺ values for INFO, PREFIX and FULL_K are 0.087618, 0.075990 and 0.093371 respectively. Applying the proposed cap gives a forecast of 20,000 with `PLAN_CAPPED_EXPECT_INCONCLUSIVE`. The full procedure requires fresh CAL followed by an independent NULL_PLAN, with the realized HOLD allocation frozen before HOLD. [HOLD record](../logs/stream-32/pilot-gaussian-staging/staging/750443a8413d477e/phases/HOLD.json) · [Audit results](../logs/stream-32/pilot-gaussian.audit.json)

The planning comparison below uses the predictive rank and the conditional Beta law for independent, identically distributed continuous CAL maxima at a fixed policy and fit. The gap SD assumes equal marginal variances and zero correlation. At correlation ρ the gap SD is sqrt(2(1 − ρ)) times the single-policy SD. The pilot does not identify the calibration-error correlation.

| n_cal | Conditional Beta parameters | Single-policy FPR SD | Gap SD at ρ = 0 |
| ---: | --- | ---: | ---: |
| 2,000 | (100, 1,901) | 0.004870 | 0.006887 |
| 5,000 | (250, 4,751) | 0.003081 | 0.004358 |
| 10,000 | (500, 9,501) | 0.002179 | 0.003082 |

The 10,000 proposal is per primary P_CONF cell, while the current full YAML draft exposes a role-wide CAL count of 2,000. The §17 workload assumes the proposed per-cell allocation and 2,000 ALT paths per family. The current runner also applies the primary HOLD cap to both applications at the primary setup. A full resource estimate must account for the finalized per-cell allocation. R4's finite-sample CP–Bonferroni option carries the plan's rough 2.5× HOLD sensitivity. R5's `OUTER_FIT` option requires explicit additional independent fits and a revised envelope. [Plan §§10, 17, 20](plans/plan-32.md)

## Measured resources and full projections

| Pilot measurement, one worker | Value |
| --- | ---: |
| Application SELF+CHILDREN | 1,489.34 CPU s |
| GNU time user + system outside scope | 1,505.36 CPU s |
| Wall, GNU time / application | 1,519.68 / 1,518.00 s |
| Aggregate peak / effective cgroup limit | 503,246,848 / 34,359,738,368 bytes |
| Parent peak RSS | 382,324,736 bytes |
| Results + staging allocated / apparent | 174,510,080 / 174,037,745 bytes |
| Launcher evidence allocated / apparent | 188,416 / 141,802 bytes |

All six cgroup memory event deltas were zero. The CPU journal matched the application's SELF+CHILDREN at its publication checkpoint. GNU time covers the wrapper, scope and trace as well as the application. The results and staging ledger excludes the launcher evidence, the continuation, Vibe and audit files. [Timing](../logs/stream-32/pilot-gaussian-attempt-1.time) · [Telemetry](../results/pca_info_online/pilot-gaussian/telemetry.json) · [Allocated disk](../logs/stream-32/pilot-gaussian.disk.allocated)

The table projects CPU and allocated disk in proportion to the §17 scan counts, using the observed 157,200-scan Gaussian pilot as the denominator. Different cohorts, compression, partitions, tracing and fixed overhead can change both ratios. T7 values are a separate Gaussian-rate extrapolation.

| §17 scenario | Nominal scans | Application CPU-h | GNU time CPU-h | Allocated GiB |
| --- | ---: | ---: | ---: | ---: |
| Primary at proposed cap | 518,400 | 1.36 | 1.38 | 0.54 |
| One descriptive setup | 352,800 | 0.93 | 0.94 | 0.36 |
| Four Gaussian setups | 1,576,800 | 4.15 | 4.19 | 1.63 |
| Two additional T7 setups, unmeasured | 705,600 | 1.86 | 1.88 | 0.73 |

At a single-worker 20,000-path primary HOLD cap, one float64 score stack is 800,000,000 bytes. Under the current runner's whole-setup HOLD allocation, the committed uint32 masks and int64 first hits would total 1,231,776,000 bytes across the Gaussian HOLD cells. At 2,000 ALT paths per family, those two array types total 705,600,000 bytes across the Gaussian ALT cells. These memory components exclude score construction copies, working buffers, bootstrap arrays and the interpreter. Full peak RAM and per-invocation wall time require profiling. The Gaussian CPU projection exceeds the pilot's four-hour allowance. [Audit results](../logs/stream-32/pilot-gaussian.audit.json)

## Evidence and disposition

| Audit evidence | SHA-256 |
| --- | --- |
| [Auditor](../logs/stream-32/audit-pilot-gaussian.py) | `b6303f188074a4b6ebc9312510cdc8a4696ecaf456ac593cd247b27c54ac8c29` |
| [Audit results](../logs/stream-32/pilot-gaussian.audit.json) | `3eb9fd0598283dd72bfffdf70ccb5e9ee7bec5e9da2b7060ed3b67ff2c504b5f` |
| [Invariance fixtures](../logs/stream-32/pilot-gaussian.invariance-tests.log) | `c9450db36834f29ff1fbee36db4c82debd78830b39f9fc1a58980d9611af1efc` |
| [Vibe retry export](../logs/stream-32/pilot-gaussian-vibe-a2/export.json) | `0404d8957a5ddd61bdbf22d44875a7f992a969810852632661403c4d5907782e` |

The initial Vibe request reached its 540 s deadline. The focused retry returned the audit helper and receipt draft with the effective model `zai-glm-5-3` at `max`. Codex reviewed the helper against the phase schemas, corrected partition-row and PRIMARY-policy lookups, and verified the results locally. The sealed experiment and its tests stayed unchanged. T7 remains closed on the observed null failures. Full remains subject to R3–R5 researcher decisions.
