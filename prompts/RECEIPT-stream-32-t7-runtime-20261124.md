# Stream 32 Student-t7 — runtime qualification receipt

24 November 2026 · `qualification/smoke` · `SMOKE_NO_CLAIMS` · `NO_T7_PILOT_GO`

## Pre-ALT seals

The independent auditor sealed SETUP through HOLD for each case. Both passes returned `PASS`. The SHA-256 values below were checked against the sealed files and recorded here before either `--alt` command.

| Case | UTC stamp | Pre-ALT seal SHA-256 |
| --- | --- | --- |
| [`continuous`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/audit-continuous-pre-alt.json) | `2026-11-24T16:49:04.713123+00:00` | `bd9dae0f1ee82163ebac3625be6a74c5db90b37f0a3dc59572373281d8a0836e` |
| [`resumed`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/audit-resumed-pre-alt.json) | `2026-11-24T16:49:04.710011+00:00` | `424bb123df53faea719c7a87e6278ebae5635a9bd7c762ed79aecb232374f0af` |

Auditor SHA-256 `6c874cdb58a12787f538503fa42117d61e3582ae29597b9e8f5398115da54021`.

The receipt was created at `2026-11-24T16:50:01.154106983Z`. Each ALT pass revalidated the SHA-256 from this receipt and its pre-ALT evidence before reading ALT and publication inputs.

| Case | ALT verdict | ALT report SHA-256 |
| --- | --- | --- |
| [`continuous`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/audit-continuous-alt.json) | `PASS` | `7983b63895b7bcd11f61eef883202e6029d7815ec2743eba079aa7d20e4b2f41` |
| [`resumed`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/audit-resumed-alt.json) | `PASS` | `75807e5122a7a37ee3900c9ec3a1df4cf8b16a07577636fea98f27b063b30e16` |

The auditor checked the committed ALT artifacts and five FAIR exports as qualification witnesses under `SMOKE_NO_CLAIMS`. This receipt records integrity and resource evidence.

## Ledger and scientific identity

The shared ledger is `COMPLETE`. Its SHA-256 is `ca9e2ff79df6051edb43e7bc74f9092e289025601a47ef3717a0e9d7ad95a20d`. The five token receipts, available samples and recorded authority references matched their ledger entries. The CPU debits sum to `2 + 113 + 45 + 902 + 100 = 1162 s`. Measured CPU totals 259.339556 s and the outstanding reservation is 0 s. [Ledger](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/ledger.json)

The two cases have the same `realization_id` `43e5ff6c53fde65fa195e92a504614816e4025b48eccca76c4fb7eee6c5c22e1`, manifest SHA-256 `ef94d43d5c0958f58f88cb2d4cae76c5816903c117cd681f1c5dd0f2aba96b71` and `FINAL.json` SHA-256 `cbff2faa40f8227de39422323b3e7d973a84a025ed5575d68f3dec8578759b15`. Both final records are `PUBLISHED` and bind the `COMPLETE` manifest. Each case has 98 staged and published files bound to its completion receipt. Of these, 96 have identical SHA-256 values, including the design, six phase records, 40 partition sidecars, 40 NPZs and all five FAIR CSVs. The differences are `telemetry.json` and `resources.json`, which record invocation-specific execution. [Continuous manifest](../logs/stream-32-t7/qualification/a565c473535afc70/cases/continuous/publication/manifest.json) · [Resumed manifest](../logs/stream-32-t7/qualification/a565c473535afc70/cases/resumed/publication/manifest.json)

| FAIR CSV | Common SHA-256 |
| --- | --- |
| `aggregates.csv` | `404451826738a81ea9960b2a7cf06e3e26fd1652e488d23736d967b647d32bbd` |
| `calibration.csv` | `55d24f15c07ae2d3a258b3e2ae65cb0590dfd2099db12dcdcd202ad7f2110dc6` |
| `issues.csv` | `fdd32ccbe38e0fd58cb8a492b84a67034e83e8ec1a493ebbc0518268e86eb2b5` |
| `selections.csv` | `0b297372e6a53e63a06d5b3c4cf328fb1c0d2985d8c4204ae946f5c21477f42e` |
| `trials_summary.csv` | `da5679e5de6790bd17d4be61dc4340d36ed69b966329702c6a508b2e26003fd6` |

## Cgroup resources and resumption

Wall intervals start at reservation and end when drainage was confirmed. The last column measures from the `ExecStopPost` sample to confirmed drainage and includes observation latency. All five receipts record `drained=true` and zero main and control PIDs.

| Token | Jobs | Settled state | CPU measured (s) | CPU charged (s) | `memory.peak` bytes (MiB) | OOM / kill / group kill | Reservation to drain (s) | Sample to drain (s) |
| --- | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: |
| [`0958186bcdfb4072b2e6cc51b1831d49`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/0958186bcdfb4072b2e6cc51b1831d49.receipt.json) | 1 | `RECONCILIATION_REQUIRED` | 1.165511 | 2 | Unavailable | Unavailable | 142589.293916 | — |
| [`f91b0f330cdf4da0afab2a15c001d6b6`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/f91b0f330cdf4da0afab2a15c001d6b6.receipt.json) | 1 | `COMPLETE` | 112.011852 | 113 | 153731072 (146.61) | 0 / 0 / 0 | 112.927525 | 0.125938 |
| [`fde8c70b672e462bab47465f87695c1c`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/fde8c70b672e462bab47465f87695c1c.receipt.json) | 1 | `CLEAN_BLOCKED_RESOURCE` | 44.065003 | 45 | 139063296 (132.62) | 0 / 0 / 0 | 44.399936 | 0.069643 |
| [`7b80185040e4482a83a4e93deb2af41f`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/7b80185040e4482a83a4e93deb2af41f.receipt.json) | 2 | `RECONCILIATION_REQUIRED` | 2.677096 | 902 | 139055104 (132.61) | 0 / 0 / 0 | 2.743667 | 0.021415 |
| [`6264e35cd0fb4d96b2e1eaf4290e14a6`](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/6264e35cd0fb4d96b2e1eaf4290e14a6.receipt.json) | 2 | `COMPLETE` | 99.420094 | 100 | 359391232 (342.74) | 0 / 0 / 0 | 100.100596 | 0.050558 |

The historical admission failure was settled later from the verified terminal systemd CPU value. Its reservation-to-confirmation interval includes that recovery delay. The four `ExecStopPost` samples all report `memory.max=8589934592` bytes, with a maximum observed peak of 359391232 bytes (342.74 MiB) and all observed OOM counters at zero.

After the clean CAL stop, the first two-job invocation committed `NULL_PLAN` and was killed. The ledger charged the full 902 s reservation under `CONSERVATIVE_RESERVED_OR_ELAPSED_ONE_CORE_BOUND` for 2.677096 s CPU measured. The kill was sent at `16:38:13.359357Z` and settlement was observed at `16:38:14.470077Z` (1.110720 s). The launcher refused a restart with the previous authority and refused reconciliation without new authority. Both commands exited 3 and left the ledger and inventory unchanged. The final invocation resumed the committed prefix and used 99.420094 s measured, 100 s charged and 100.100596 s from reservation to drainage. [Reconciliation and resume decision](GO-stream-32-t7-resume-case2-reconciliation-20261124.md)

The two post-CAL invocations together used **102.097190 s measured and 1002 s charged**. Including the clean CAL invocation, `resumed` used 146.162193 s measured and 1047 s charged. Compared with the completed one-job `continuous` invocation (112.011852 s measured and 113 s charged), the observed differences are **+34.150341 s measured and +934 s charged**. This comparison includes the forced stop, the two-job execution and their different scheduling costs.

## Wall intervals by partition

There is no per-partition CPU timer. The intervals below use the `st_mtime_ns` of the committed JSON sidecar, which is written before the atomic rename. Each interval starts at the preceding sidecar in that phase or the preceding phase record. For the first SETUP partition and the resumed HOLD partition, the anchor is the application start reconstructed from the monotonic journal token and the ledger timestamps. The intervals include work between commits and exclude the idle wait for written authority.

| Phase | Partition key | Rows | Continuous (s) | Resumed (s) |
| --- | --- | ---: | ---: | ---: |
| `SETUP` | `frame / SMOKE / 239` | 239 | 0.075 | 0.075 |
| `SETUP` | `frame / SMOKE / 32` | 32 | 0.015 | 0.016 |
| `SETUP` | `fit / SMOKE / FITTED_LW_T7 / 239 / 0` | 239 | 0.038 | 0.040 |
| `SETUP` | `fit / SMOKE / FITTED_LW_T7 / 32 / 0` | 32 | 0.008 | 0.007 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 239 / 0 / F0_ISOTROPIC_RESIDUAL` | 8 | 0.096 | 0.093 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 239 / 0 / F1_TAIL_RESIDUAL` | 8 | 0.011 | 0.011 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 239 / 0 / F2_STRUCTURED_RESIDUAL` | 8 | 0.010 | 0.010 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 239 / 0 / F_HEAD_RESIDUAL` | 8 | 0.011 | 0.011 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 32 / 0 / F0_ISOTROPIC_RESIDUAL` | 8 | 0.009 | 0.009 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 32 / 0 / F1_TAIL_RESIDUAL` | 8 | 0.009 | 0.009 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 32 / 0 / F2_STRUCTURED_RESIDUAL` | 8 | 0.010 | 0.009 |
| `DEV` | `DEV_LIB / SMOKE / FITTED_LW_T7 / 32 / 0 / F_HEAD_RESIDUAL` | 8 | 0.009 | 0.009 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 239 / 0 / F0_ISOTROPIC_RESIDUAL` | 4 | 0.023 | 0.022 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 239 / 0 / F1_TAIL_RESIDUAL` | 4 | 0.018 | 0.018 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 239 / 0 / F2_STRUCTURED_RESIDUAL` | 4 | 0.019 | 0.018 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 239 / 0 / F_HEAD_RESIDUAL` | 4 | 0.018 | 0.018 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 32 / 0 / F0_ISOTROPIC_RESIDUAL` | 4 | 0.011 | 0.011 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 32 / 0 / F1_TAIL_RESIDUAL` | 4 | 0.011 | 0.011 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 32 / 0 / F2_STRUCTURED_RESIDUAL` | 4 | 0.011 | 0.011 |
| `DEV` | `DEV_ALT / SMOKE / FITTED_LW_T7 / 32 / 0 / F_HEAD_RESIDUAL` | 4 | 0.011 | 0.011 |
| `DEV` | `DEV_NULL / SMOKE / FITTED_LW_T7 / 239 / 0` | 39 | 0.090 | 0.088 |
| `DEV` | `DEV_NULL / SMOKE / FITTED_LW_T7 / 32 / 0` | 39 | 0.029 | 0.028 |
| `CAL` | `CAL_NULL / SMOKE / FITTED_LW_T7 / 239 / 0 / MARKET` | 39 | 6.022 | 5.912 |
| `CAL` | `CAL_NULL / SMOKE / FITTED_LW_T7 / 239 / 0 / RESIDUAL` | 39 | 11.937 | 11.864 |
| `CAL` | `CAL_NULL / SMOKE / FITTED_LW_T7 / 32 / 0 / MARKET` | 39 | 5.981 | 5.957 |
| `CAL` | `CAL_NULL / SMOKE / FITTED_LW_T7 / 32 / 0 / RESIDUAL` | 39 | 11.135 | 11.792 |
| `HOLD` | `HOLD_NULL / FITTED_LW_T7 / 239 / 0 / MARKET` | 60 | 10.302 | 12.820 |
| `HOLD` | `HOLD_NULL / FITTED_LW_T7 / 239 / 0 / RESIDUAL` | 60 | 19.766 | 22.027 |
| `HOLD` | `HOLD_NULL / FITTED_LW_T7 / 32 / 0 / MARKET` | 60 | 10.550 | 12.227 |
| `HOLD` | `HOLD_NULL / FITTED_LW_T7 / 32 / 0 / RESIDUAL` | 60 | 19.755 | 22.202 |
| `ALT` | `ALT / FITTED_LW_T7 / 239 / 0 / MARKET / F3_MARKET` | 6 | 1.017 | 3.093 |
| `ALT` | `ALT / FITTED_LW_T7 / 239 / 0 / RESIDUAL / F0_ISOTROPIC_RESIDUAL` | 6 | 0.660 | 2.686 |
| `ALT` | `ALT / FITTED_LW_T7 / 239 / 0 / RESIDUAL / F1_TAIL_RESIDUAL` | 6 | 0.654 | 2.702 |
| `ALT` | `ALT / FITTED_LW_T7 / 239 / 0 / RESIDUAL / F2_STRUCTURED_RESIDUAL` | 6 | 0.660 | 2.681 |
| `ALT` | `ALT / FITTED_LW_T7 / 239 / 0 / RESIDUAL / F_HEAD_RESIDUAL` | 6 | 0.658 | 2.697 |
| `ALT` | `ALT / FITTED_LW_T7 / 32 / 0 / MARKET / F3_MARKET` | 6 | 0.576 | 2.605 |
| `ALT` | `ALT / FITTED_LW_T7 / 32 / 0 / RESIDUAL / F0_ISOTROPIC_RESIDUAL` | 6 | 0.640 | 2.663 |
| `ALT` | `ALT / FITTED_LW_T7 / 32 / 0 / RESIDUAL / F1_TAIL_RESIDUAL` | 6 | 0.644 | 2.661 |
| `ALT` | `ALT / FITTED_LW_T7 / 32 / 0 / RESIDUAL / F2_STRUCTURED_RESIDUAL` | 6 | 0.645 | 2.677 |
| `ALT` | `ALT / FITTED_LW_T7 / 32 / 0 / RESIDUAL / F_HEAD_RESIDUAL` | 6 | 0.657 | 2.672 |

## Pilot T7 resource projection

Both designs use H = 250, dimensions 32 and 239 and the same partition counts. The table scales whole phase intervals by prospective workload ratios. The single-job scenario uses `continuous`. The sensitivity scenario uses the larger measured phase interval between the two qualification cases and therefore includes the slower two-job HOLD and ALT timings. These are conditional planning scenarios.

| Phase | Size multiplier | Single-job reference (s) | Sensitivity scenario (s) |
| --- | ---: | ---: | ---: |
| `SETUP` | 1 | 0.1 | 0.1 |
| `DEV` | 12.50 | 80.8 | 80.8 |
| `CAL` | 200/39 | 180.0 | 182.3 |
| `NULL_PLAN` | 1 | 0.2 | 0.6 |
| `HOLD` | 200/60 | 201.5 | 231.1 |
| `ALT` | 200/6 | 229.1 | 906.6 |
| `FINAL` | 200/6 | 44.0 | 44.0 |
| Total | | **735.7** | **1445.6** |

DEV uses the largest planned ratio (100/8 or 50/4), covering the 200/39 DEV_NULL ratio. `FINAL` scales the shared export work by the largest sample ratio. The Pilot-only descriptive bootstrap adds unmeasured wall time. Its largest index matrix has 10000 × 200 int64 entries (15.26 MiB), with one group processed at a time. An indexed difference can require a second matrix of the same size. The HOLD/ALT first-alarm and mask arrays have a nominal aggregate bound of 48.83 MiB for 88 HOLD and 166 ALT cells at 200 paths. Fit, score buffers, serialization and interpreter memory add to these components. The qualification peak gives a reference for the 8 GiB cap.

Retain the provisional envelope of **8 GiB, 2 h cumulative CPU, 2700 s wall per invocation and `jobs_max=1`**. The launcher caps wall at 2700 s, enforces a 2000 s application deadline and reserves 2702 CPU s per invocation. The scenarios leave about 1264 s and 554 s of application wall capacity for Pilot-specific costs. Actual finalization and aggregate memory remain to be measured by the Pilot. Two fully charged reservations leave 1796 s, below the amount required to admit a third invocation under this envelope. The Pilot uses its own design ledger.

[Proposed Pilot decision](DRAFT-stream-32-t7-pilot-20261124.md) · [Scientific Pilot YAML](../configs/pca_info_online_t7_pilot.yaml)
