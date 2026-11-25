# Stream 32 Student-t7 — pilot audit receipt

## Pre-ALT seal

| Field | Recorded value |
| --- | --- |
| Audit verdict | `PASS` |
| Seal time (UTC) | `2026-11-24T17:32:50.909213+00:00` |
| Design ID | `2ac79300374b99ba1842c2d501c4a1d03ce890c623018ab9cc0f7a9cc20e1ddf` |
| Auditor SHA-256 | `6c874cdb58a12787f538503fa42117d61e3582ae29597b9e8f5398115da54021` |
| Pre-ALT report SHA-256 | `e6c7bee96e53ef9fbfe68efc3f4161a4fd516934ca8f1dcaabe7a276a672a549` |

The auditor ran `--pre-alt` against staged SETUP through HOLD and sealed 81 input hashes, including 87 independently checked CAL thresholds and 87 HOLD recounts in the report. The report SHA-256 was checked against the CLI output and entered in this receipt before the auditor's first access to staged ALT or the publication. The producer had already completed the pilot. [Pre-ALT report](../logs/stream-32/t7/pilot/2ac79300374b99ba/audit-pre-alt.json) · [Auditor](../tools/ops/audit_stream32_t7.py)

## Completion and FAIR payloads

The producer completed the authorized `PILOT_ONLY` run for `FITTED_LW_T7`, N = 32 and 239, `fit_id=0` (`FIT_CONDITIONAL`), at H = 250. The read-only launcher preflight checked the frozen intent, GO, YAMLs, source hashes and native descriptor. The ledger and its sole invocation are `COMPLETE`. The durable invocation receipt, cgroup sample and all 98 files in the recorded inventory matched their hashes. The manifest is `COMPLETE` and FINAL is `PUBLISHED`. They bind realization `d46eeb91029a69fc29574a322924cd202c3edf71541de8f34876cab7b7d914e2` to the same design. There are 40 local partitions (SETUP/DEV/CAL/NULL_PLAN/HOLD/ALT = 4/18/4/0/4/10). `NULL_PLAN=NOT_APPLICABLE` and the realization records `plan_id=null` and `n_hold=null`; each HOLD cell used 200 paths. [Intent](INTENT-stream-32-t7-pilot-20261124.json) · [Ledger](../logs/stream-32/t7/pilot/2ac79300374b99ba/supervisor/ledger.json) · [FINAL](../logs/stream-32/t7/pilot/2ac79300374b99ba/run/staging/2ac79300374b99ba/phases/FINAL.json) · [Manifest](../results/pca_info_online/t7-pilot/manifest.json)

| Evidence | SHA-256 |
| --- | --- |
| Ledger | `d977b6828d129d48ce56c96ae3adbc9a1e18dbfc4cf1cc375f9a7a317132c383` |
| Invocation receipt | `05d8d15fc7e3c1997e74dd79f373578fab8e50ee03cbdc64109d6bd76ea34d42` |
| Cgroup sample | `36eccf0adffdd048909b971c8fa75a2082a9b1d3ae99824a65fffc91de2c42e6` |
| FINAL | `fa3cbb5577219adfa6fec4585ccc822648019b825398b11bd783e03e320b6567` |
| Manifest | `9269b97739f145ee38c2dbfc2b1e5c3a88cae5378ac4d648075fc58b2c310dea` |
| ALT audit report | `363de848c94b6fc616ef5dceb0f476c2195dfa166f9c42502a2c7d25d14e6c5e` |

The `--alt` pass revalidated the seal before opening ALT and returned `PASS` at `2026-11-24T17:33:55.955864+00:00`. It verified 114 input hashes, all five FAIR CSVs, the manifest and FINAL. CAL and HOLD each replayed path index 0 for 87 cells. ALT replayed the same predeclared index for 165 cells and rebuilt the 10 nominal bootstrap matrices. The replay used relative tolerance `5e-10` and absolute tolerance `1e-11`, with exact checks for masks, first hits and the GE boundary. The auditor also recounted all stored HOLD and ALT paths. [ALT report](../logs/stream-32/t7/pilot/2ac79300374b99ba/audit-alt.json) · [Audit specification](SPEC-stream-32-t7-audit-and-runner-20261122.md)

| FAIR CSV | Data rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [calibration.csv](../results/pca_info_online/t7-pilot/calibration.csv) | 87 | 23,405 | `967f6cc1f2b74fa50b21e25ca7c4b46d24df15a1303a7d32c970eaee3272bf08` |
| [trials_summary.csv](../results/pca_info_online/t7-pilot/trials_summary.csv) | 252 | 87,903 | `5c058c2d503ed28d321fe6de89a3b14f0d643c50e3682509861c091a3682a079` |
| [selections.csv](../results/pca_info_online/t7-pilot/selections.csv) | 165 | 65,523 | `42490b063cfc408161fd78ad04e14443c59f4002e79db882bdbd43ac74d03c8f` |
| [aggregates.csv](../results/pca_info_online/t7-pilot/aggregates.csv) | 244 | 397,186 | `006beba33dfc2fe882619734026fbed2796f635d479bfe47204561cdf6a69cd1` |
| [issues.csv](../results/pca_info_online/t7-pilot/issues.csv) | 48 | 7,728 | `0f2e5ce91fd62f86ecec445a3d102b68ca6271e49ccfeec56cb36203349a5f96` |

All 240 contrast rows and their `inference_json.status` are `PILOT_ONLY`. The other four aggregate rows are `DESCRIPTIVE_V_RMST`. The confirmatory row count is zero. SETUP labels the information and HEAD geometry `GAUSSIAN_PROXY`, with 16 HEAD sign profiles per setup. All 165 selection rows carry `ORACLE_DIAGONAL_GAUSSIAN_PROXY` as the information basis and `ANALYTIC_PROXY` as the metric basis. These labels apply to Gaussian working-model diagnostics on Student-t7 paths. The run estimates finite-horizon alarm rates and `RMST_250` conditional on the frozen fit. [Amendment](AMENDMENT-stream-32-t7-20261122.md) · [Mapping](../docs/MAPPING.md#stream-32-student-t7-pilot)

## Clopper–Pearson null checks

Each CAL cell used 200 paths and the rule `predictive_exchangeable_rank_v2`, with `r=9` and nine CAL maxima at or above the realized threshold. The marginal new-path bound through H = 250 is 10/201. The HOLD status uses one-sided Clopper–Pearson bounds at tail 0.05 around the attained rate and compares them with `alpha + eps_v = 0.06`. Upper bound at most 0.06 gives `NULL_VALIDATED`. Lower bound above 0.06 gives `NULL_FAILED`. The remaining cells are `NULL_INCONCLUSIVE`. [Calibration CSV](../results/pca_info_online/t7-pilot/calibration.csv) · [Pre-ALT report](../logs/stream-32/t7/pilot/2ac79300374b99ba/audit-pre-alt.json)

| N | Application | Setup ID | Validated | Inconclusive | Failed |
| ---: | --- | --- | ---: | ---: | ---: |
| 32 | RESIDUAL | `a6848e270192f799` | 23 | 6 | 0 |
| 32 | MARKET | `48b27bc1b0817ab8` | 11 | 4 | 0 |
| 239 | RESIDUAL | `0202412e34dacf9a` | 0 | 28 | 1 |
| 239 | MARKET | `042b55f4d7fba12a` | 5 | 9 | 0 |
| **Total** | | | **39** | **47** | **1** |

The failure was the `NON_DEPLOYABLE` oracle `ORACLE_INFO_MIX` for `F2_STRUCTURED_RESIDUAL` (N = 239, calibration `251e4bb7d7d40c8b`). It alarmed on 20/200 HOLD paths (10.0%, lower/upper bounds 0.0672614 and 0.1419893). Its sole affected contrast pairs it with `ONLINE_INFO_MIX_W128` (calibration `06b23c71b58e0e43`, 11/200, bounds 0.0311469 and 0.0893961, `NULL_INCONCLUSIVE`). The ALT report marks that pair **`NULL_FAILED — NOT_CLAIMABLE`**. The contrast retains `PILOT_ONLY` and `ORACLE_SEPARATE` in the published CSV. The 47 inconclusive cells and the failure are all preserved in `issues.csv`. [Trials CSV](../results/pca_info_online/t7-pilot/trials_summary.csv) · [Issues CSV](../results/pca_info_online/t7-pilot/issues.csv) · [ALT report](../logs/stream-32/t7/pilot/2ac79300374b99ba/audit-alt.json)

## Measured pilot resources

| Measurement | Observed value |
| --- | ---: |
| Cgroup CPU | 699.682710 s |
| Ledger CPU debit / reservation remaining | 700 s / 0 s |
| Wall, reservation to cgroup drain | 703.648732 s |
| Aggregate `memory.peak` | 350,752,768 bytes (334.50 MiB) |
| Aggregate `memory.max` | 8 GiB |
| Cgroup OOM / OOM kill / group kill | 0 / 0 / 0 |
| Producer CPU / wall | 697.340 s / 701.186 s |
| Staging allocated disk | 84,570,112 bytes |
| Publication allocated disk | 614,400 bytes |
| Supervisor evidence allocated disk | 49,152 bytes |
| Allocated footprint total | 85,233,664 bytes (81.29 MiB) |

The resource receipt comes from one worker on one logical CPU, with a drained cgroup and exit status 0. Disk figures are post-run `du -B1 -s` measurements of the three directories, excluding the independent audit reports. The run recorded no transient peak-disk measurement. Staging retained 90 files and the largest NPZ was 8,000,256 bytes. Publication retained eight files with 596,513 bytes of content. [Invocation receipt](../logs/stream-32/t7/pilot/2ac79300374b99ba/supervisor/1e440a92db4841259b024cba7cb36d49.receipt.json) · [Cgroup sample](../logs/stream-32/t7/pilot/2ac79300374b99ba/supervisor/1e440a92db4841259b024cba7cb36d49.sample.json) · [Producer telemetry](../results/pca_info_online/t7-pilot/telemetry.json) · [Resource journal](../logs/stream-32/t7/pilot/2ac79300374b99ba/run/staging/2ac79300374b99ba/resources.json)

## Full T7 resource forecast

The pilot ran 72,600 scans under the specification's scan-count convention. The nominal Full grid has 705,600 scans, or 699,600 if one MARKET CPV90 cell is again ineligible. Applying the resulting 9.64–9.72 multiplier to measured cgroup CPU gives roughly 6,740–6,800 s (1.87–1.89 h). A cross-check using phase-file modification times gives about 6,800 s at the pilot's eligibility pattern. It scales the DEV interval (36.89 s) by 4.5, CAL/HOLD/ALT (162.65/162.66/310.64 s) by 10, and budgets ten times the finalization interval (26.96 s). The timings are differences between committed file timestamps. ALT contributes only its workload and duration to this forecast. [Scan counts and memory components](SPEC-stream-32-t7-audit-and-runner-20261122.md#comptes-et-ressources) · [Staged phases](../logs/stream-32/t7/pilot/2ac79300374b99ba/run/staging/2ac79300374b99ba/phases/)

Plan for **2–3 h of aggregate CPU and active wall time**, plus any pauses for written resume authorization. The application window is 2,000 s inside the 2,700 s outer limit, with 2,702 CPU seconds reserved per admission. At that window, budget **4–7 invocations** as a planning range for partition boundaries and prefix checks. Large-cohort replay, repeated prefix validation and finalization make the wall estimate uncertain. The existing 6 h CPU cap leaves at least 10,800 s above the upper CPU forecast for reservations and contingency.

Ten times the pilot's allocated footprint is 0.79 GiB. Allow **2 GiB free** for retained partitions, temporary writes and audit files. The specification's raw partition estimate is about 628 MiB, including a RESIDUAL HOLD partition of up to 55.76 MiB. The five summarized CSVs have the same order of row count as the pilot. For memory, the Gaussian Full's observed peak of about 3.78 GiB and the T7 Full array sizes give a planning range of **3–5 GiB**, including concurrent buffers and page cache. The largest bootstrap index matrix alone is 152.59 MiB. This is a forecast for the producer under the existing 8 GiB ceiling. [Resource specification](SPEC-stream-32-t7-audit-and-runner-20261122.md) · [Gaussian Full measurements](RECEIPT-stream-32-full-gaussian-20261120.md#resource-accounting-and-resume)

The Full YAML retains its prospective scientific settings and the existing 8 GiB, 6 h CPU, 2,700 s per invocation and one-worker envelope. `--describe` returned the original Full design and seed-plan hash. The Full decision remains pending under `NO_T7_FULL_GO`. [Full draft](DRAFT-stream-32-t7-full-20261124.md)
