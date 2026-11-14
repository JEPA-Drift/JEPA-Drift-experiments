# Stream 19 E4 production pilot and pre-activation resource report, 2026-11-13

Status at pre-activation review: technical cost evidence received; scientific FULL NOT ACTIVATED. The disk guard
failed at 14:28 UTC. The subsequent activation at 14:59 UTC is recorded at the end of this report.
Authority and the blocking decision are recorded in `prompts/STOP-stream-19-e4-disk-20261113.md`. The researcher's
conditional execution authority remains `prompts/GO-stream-19-e4-full-20261112.md`; this report grants no authority.
Base: published main `b18d8e5b01706bcb3dea8268c93fc0b9c361e441`. No scientific full run occurred during the
pre-activation pilot.

## Evidence and fixed sources

The technical pilot used the reviewed production plan and its corrective annex. Source SHA-256 values:

| File | SHA-256 |
|---|---|
| `experiments/e4_production.py` | `402d23bf09a76c51f9dbcddaf4cd5edb3cbc476b14b42685871502e8b0826980` |
| `tests/test_e4_production.py` | `d75d4350f0a3296605eec764169c28d860ce034ea14b427f6d5a373799008e79` |
| `tools/run_e4_production.sh` | `3ed5b9920dd3cb076369a55e1f532ffd4cdfbdf452d2cb3a7c535c837ace4af8` |
| `configs/e4_alignment.yaml` | `5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2` |
| original `experiments/e4_alignment.py` | `e457ebae9011a5f1d1b0b9bc43d38f2ab97a70bccd64069dba07ad51996efd01` |

The plan remains SHA-256 `22c71798b0bfd7b9cb396f30695ce991819a65c9983bc9ad2190798db2de6504` and its annex
`27d8c40d17526a03df0a14ec406cb5252242380f74ef2774d798f3086002f5ac`. The original 101 prototype tests are unchanged.
Execution used the project .venv, pinned numerical libraries and single-thread deterministic environment, with
the existing shared execution lock. The E4-specific tests, P1/P2 pilots and scientific producer use synthetic inputs.
This excludes R0009 make check, whose unchanged global baseline includes data-backed legacy tests, including 2020
universe checks and full-panel reconstruction. Some fixtures select pre-2020 rows after loading complete files;
others check whole-period data. Neither synthetic-only nor date-restricted I/O is established for that global
baseline. The source/log findings and limits are in `docs/audits/legacy_global_checks_data_scope_20261113.md`.
E4 has no real-panel reader in its scientific path and no J4/FROZEN or JEPA/VAE run.

The final immutable report is `results/e4_alignment/production_pilot_20261113/final1/report/`, generated through
`tools/run_e4_production.sh attempt --phase forecast --mode full --block 250`. Its MANIFEST SHA-256 is
`ccf1527c520cf7d986cfe7a34f3ff3fa6b3f752e4aa2716b0fe9eda12dde1c6d`; identity is
`6d1acbd629975285acc7df37cb3d02e5daf5f0b7339473af78d02757ef6066af`.
The manifest retains the complete eight-file set, schemas, row counts and hashes. The adjacent `receipts/` and
`evidence/` directories retain the tests, global check, pilot, non-leak and candidate timing evidence.

## Measured checks and pilot

- Codex R0007: 155 tests passed, no failures/skips; 152 official E4 tests and three former RED witnesses.
  Runtime 65.19 s, CPU 74.21 s, external peak RSS 220,492 KiB. Source: R0007 JUnit/log and its tests receipt.
- Codex R0009 `make check`: 37 contract tests and 1,308 other tests passed, five D4 availability skips only.
  Torch guards and PCA/G1 ran. Runtime 36.73 + 551.85 s, CPU 617.21 s, peak RSS 3,838,968 KiB.
  The earlier failed collection attempt R0008 cost 42.98 CPU s and remains counted. Six root-owned ignored audit
  copies were renamed with `.py.source`, preserving bytes; official tests and discovery settings were unchanged.
- P1: nine real-kernel cost calls, 40 replicates each, covering Gaussian N8, Gaussian N500 and t7 N500 in the
  calibration, holdout and alternative roles. All returned COMPLETE. Payloads were discarded; no delay, FPR,
  detection rate or scientific alignment result was inspected or persisted by this cost phase.
- Cost-only geometry selection chose 250 replicates. The declared initial upper estimate was 307.375 CPU s,
  below its 900 s target. The reconciled final maximum invocation forecast is 299.703863 CPU s. Both are estimates.
- P2: all 354 COST_FIXTURE partitions completed at full counts. The global calibration barrier was exercised.
  Attempt A0000143 deliberately returned 7 before atomic commit, leaving a temporary directory and no final
  partition. A0000144 recomputed it. Resume reached code 10, verification passed, and three replays were
  SKIPPED_COMPLETE with partition bytes unchanged. The fixture publication and independent publication audit passed:
  560 blocks audited, 42 calibration checks recomputed, 86 publication files, activation false.
- Candidate evidence checking, pending-cost parsing and a synthetic ledger of 1,000 entries all passed.
  Final measured CPU times were respectively 0.659072 s, 0.006932 s and 0.232769 s, below the declared 60 s
  per-invocation control allowance. This checks a technical candidate and writes no scientific activation.

Cost source tables include the former RED checks and failed attempts. The pre-existing pilot is counted once
as 645.23 CPU s. Forty-seven immutable provenance sources were imported: 1,315.51 tests CPU s and 0.97
administrative CPU s. Common attempts A0000001–A0000389 sum to 1,036.04 CPU s. Known measured cumulative cost
at that point is therefore **2,997.75 CPU s**. One previously declared unmeasured stdlib XML metadata read remains
administrative unknown; it is not represented as a measured zero. Shell-only metadata inspection is outside these
scientific Python measurements. The append-only ledger retains the exact commands, exits, GNU time and hashes.

## Conditional CPU forecast

Source: final `forecast.csv`, SHA-256 `4c826ae14a81e1a93ac296918ee66c255dd6ccdd5db80da06e4727a2cbd9ec28`.
Partition detail: `partition_forecast.csv`, SHA-256
`42261771906b6abdd6e57b1e830e08cac470286cae6d22e2a5f073221f516251`.

| Scenario | Full/control invocations | Consumed at A0000383 (CPU s) | Projected (CPU s) | Recompute reserve (CPU s) | Total (CPU s) |
|---|---:|---:|---:|---:|---:|
| FULL_GRID | 360 | 2,888.29 | 53,390.928 | 899.1115905 | 57,178.3295905 |
| DROP_N500 | 310 | 2,888.29 | 39,268.475225 | 899.1115905 | 43,055.8768155 |
| T7_ON_8_64_239 | 235 | 2,888.29 | 30,176.818700 | 899.1115905 | 33,964.2202905 |

All are WITHIN_CAP against 86,400 CPU s, conditionally. The 360 rows include 354 scientific partitions and six
control/verification/publication/accounting calls. Each row includes the declared 60 s control allowance. Scalar
calibration production and the two later audits are accounted separately. No fallback was applied.
Replacing the frozen consumed cost by the already measured A0000389 tail gives FULL_GRID **57,287.7895905 s**,
about **15.91 CPU hours**, leaving 29,112.2104095 s to the global cap. Later costs must remain counted.

This replaces the earlier 8.837424-hour estimate with measured production overhead. It is not a guarantee.
Linear per-path scaling, fixture overhead transfer, evidence self-reading, Git objects, scientific payload sizes,
temporary disk peaks and final accounting transfer retain their explicit assumptions in `unmeasured.csv`.
The next-invocation envelope, previous failures, memory observations, projected remaining cost and disk guard are
rechecked by the runner. Each invocation retains the 8 GiB and 30-minute limits, GNU timeout at 1,790 s and CPU
limits of 1,700/1,750 s. Full runs are single-process; no parallel-memory claim is made.

## Storage, RSS and blocking disk observation

The common technical attempts measured peak RSS 536,052 KiB and maximum whole-call wall time 52.97 s. The larger
global-check peak is 3,838,968 KiB, below 8 GiB. Full scientific aggregation RSS is not measured by a fixture pilot.

`volumes.csv` records 356 measured final-byte entries, totaling 163,645,540 bytes across partitions, leftover and
publication directories. Its SHA-256 is `843745bb0b16643afe8745b96c8fe9b8cceb66ea5882cbc100837f4435421e2c`.
The 57,043,729-byte merge temporary bound is derived from measured directory/plain-CSV sizes; its peak was not
observed. The full projection totals 107,933,096 bytes and has 7,333,882 additional temporary bytes. The activation
footprint rule gives **439,066,266 bytes** for blocks, fragments, publication and Git. These are conditional bounds,
with scientific-byte transfer assumptions retained separately; no unobserved peak is labelled MEASURED.

At 14:28 UTC the shared volume had **887,238,656 bytes available**. Footprint plus the 1 GiB reserve requires
**1,512,808,090 bytes**. The **625,569,434-byte deficit** blocks activation. Earlier free-space observations do not
override this later measurement. No artifacts were deleted and no private process was modified to bypass the guard.

The storage policy keeps deterministic compressed fragments, SHA-256, schemas and manifests. No file over 50 MB
may be committed; compressed CSVs require explicit documented force-add if ignored. J_k remains streamed;
trial analysis may hold up to 672,000 rows in RAM. Planned scientific maxima remain 3,948,000 J_k rows and
672,000 trials. The cost fixture's
tables are technical fixtures, not E4 scientific results, and are not promoted into scientific outputs.

## Scientific risks and next gate

The analytic precheck predates simulation and is unchanged. At N239/N500 its one-atom secondary-reading clocks
are 1.2415/2.3742 H for Gaussian and 1.0054/1.8017 H for t7 (INFO_GAUSS_PROXY_T7). They are design diagnostics,
not RMST bounds or power guarantees. Material censoring risk remains; rank-reading qualification is not inferred
from these clocks. No I*, grid, threshold or Wilson criterion was adapted.

Future inference remains conditional on the realized null fits and calibrations. The paired bootstrap, two distinct
readings, separate holdout FPR, ORACLE labels, full-grid qualification and NOT_IDENTIFIED statuses remain required.
This study estimates local log-RMST slopes, not Lorden ADD or a universal exponent; Delta decomposition is descriptive.

The disk STOP must be resolved and documented before the final identity/budget checks and explicit GO 2 activation.
There is no full campaign to close, no scientific result to publish yet, and stream 19 as a whole remains partial.
The latest instruction permits only two priority implementations (E4 and 23); 27 and 21 remain in planning/review.

## Subsequent disk restoration and explicit activation

The researcher restored disk space and requested immediate execution. A new shell observation found
26,862,768,128 available bytes. The unchanged final evidence was revalidated by activation attempt A0000390,
which returned ACTIVATED with exit 0 and measured 26,862,305,280 available bytes. Its CPU cost is 1.96 s.
The historical STOP document remains unchanged; `prompts/GO-stream-19-e4-activation-20261113.md` records its release.
The activation record SHA-256 is `e3edb7c8f71eabd55cf24d00f912186f1b86acaccf40dbe55698c96e34963e0c`.

The full scientific campaign started at 2026-11-13 14:59:28 UTC under `jepa-e4-full-20261113.service`, using the
existing shared lock, block size 250 and the complete frozen grid. Initial plan, common scalar calibration and null
fit partitions completed. This records launch, not scientific completion or acceptance of its future results.
Work root: `logs/stream_19_e4_production/full_20261113`; publication target: `results/e4_alignment/full_20261113`.
The service follows publication with its standalone audit and terminal accounting receipt. Resource and identity
guards remain active; no fallback or scientific choice changed. No other numerical work runs concurrently.
