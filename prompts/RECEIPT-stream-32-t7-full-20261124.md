# Stream 32 Student-t7 — Full audit receipt

## Pre-ALT seal

| Field | Recorded value |
| --- | --- |
| Verdict | `PASS` |
| Seal time (UTC) | `2026-11-25T04:06:05.028538+00:00` |
| Design ID | `03abb171a86076e1eaab777cc5d789d7e556646b09eb3c26c9cfa8f5094b1f96` |
| Auditor SHA-256 | `6c874cdb58a12787f538503fa42117d61e3582ae29597b9e8f5398115da54021` |
| Pre-ALT report SHA-256 | `eaf6e06cef969d9c993de46c55c00fd6e0daf10a37b00d64fac7a81e5b2d4259` |

The `--pre-alt` pass sealed 81 input hashes from SETUP through HOLD, independently checked 87 CAL thresholds and recounted 87 HOLD cells. It replayed path index 0 for each CAL and HOLD cell. The CLI digest matched a separate `sha256sum` and was recorded in this file before the audit first read staged ALT or the Full T7 publication. The producer had completed the run before the audit. [Pre-ALT report](../logs/stream-32/t7/full/03abb171a86076e1/audit-pre-alt.json) · [Auditor](../tools/ops/audit_stream32_t7.py)

## Completion and chain of custody

The `COMPLETE` ledger records four `CLEAN_BLOCKED_RESOURCE` invocations and one final `COMPLETE` invocation. All five invocation receipts and cgroup samples matched their recorded hashes. The four written resume authorities bind the preceding token, receipt, inventory and cumulative CPU debit. All 98 current files in the final inventory matched their SHA-256 values. The committed files from earlier inventories also matched, with `status.json` and `resources.json` tracked at their final versions. The intent, scientific and authorized YAMLs, GO and frozen source hashes matched their references. [Intent](INTENT-stream-32-t7-full-20261124.json) · [GO](GO-stream-32-t7-full-20261124.md) · [Ledger](../logs/stream-32/t7/full/03abb171a86076e1/supervisor/ledger.json)

`FINAL.json` is `PUBLISHED` and binds the `COMPLETE` manifest to realization `bc986fbd5d508a4d2acecb9c536a83c724690c6b93393be6e047d3720a0d1e35`. The manifest covers 40 partitions. The SETUP, DEV, CAL, NULL_PLAN, HOLD and ALT phases contain 4, 18, 4, 0, 4 and 10 partitions respectively. `NULL_PLAN=NOT_APPLICABLE`, with `plan_id=null` and `n_hold=null` in the realization descriptor. The HOLD cohort size is 2,000 per cell. [FINAL](../logs/stream-32/t7/full/03abb171a86076e1/run/staging/03abb171a86076e1/phases/FINAL.json) · [Manifest](../results/pca_info_online/t7-full/manifest.json)

| Evidence | SHA-256 |
| --- | --- |
| INTENT | `9451209da37b0a0337fddff05d3e017c5363a31b3d12831e00e4a4ee13faac71` |
| Ledger | `15f3ee02189c8f0f9ceb2a58c4803d9994b06bcd900fc902e6e0f7586878773a` |
| FINAL | `72a803323d0574f121390e608ab906fd0b313344b71f31e402dc66ded6658c6c` |
| Manifest | `30afa8dcd5c688fbcead107fc0efe44443892a1bf8aaee9e5137ff3a7345c172` |
| ALT audit report | `b3ace2ad5c72928dc9e5fe0c4faabc3df70679739026d0259c7e1b67cdb164c3` |

The `--alt` pass revalidated the SHA-256 and evidence of the pre-ALT seal before reading ALT. It returned `PASS` at `2026-11-25T04:09:45.842701+00:00`, binding 114 input hashes. It replayed the predeclared path index 0 for all 165 ALT cells, recounted all stored paths, reconstructed 10 nominal bootstrap matrices and checked the complete contents of all five FAIR CSVs. The replay used relative tolerance `5e-10` and absolute tolerance `1e-11`, with exact mask, first-hit and GE-boundary checks. [ALT report](../logs/stream-32/t7/full/03abb171a86076e1/audit-alt.json) · [Audit specification](SPEC-stream-32-t7-audit-and-runner-20261122.md)

## FAIR publication

| FAIR CSV | Data rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [aggregates.csv](../results/pca_info_online/t7-full/aggregates.csv) | 244 | 404,607 | `e539ecdfd6f0dfd187ee878ce8670d50ed0192310eba993b56eaade38e60964d` |
| [calibration.csv](../results/pca_info_online/t7-full/calibration.csv) | 87 | 23,675 | `49afc9e9e70ad2066b8861c310f1817a4266873708702166d4e44dfe768a5836` |
| [issues.csv](../results/pca_info_online/t7-full/issues.csv) | 59 | 9,491 | `73e38d6bb873eb1c0627745faff5a545f9339cfd667ca1b8b89d76cfee876929` |
| [selections.csv](../results/pca_info_online/t7-full/selections.csv) | 165 | 65,700 | `170f617a2fc0a3a59c057087c995369195cf857500064a908e7e2b8741dcb5db` |
| [trials_summary.csv](../results/pca_info_online/t7-full/trials_summary.csv) | 252 | 88,709 | `abbe301a6bd89af713b2c92630f9ad26f03a0b0271280284702c43da41f203b9` |

Each full-file digest matched the manifest and final inventory. Each CSV is below 50 MiB. The 240 contrasts are `DESCRIPTIVE_NOMINAL`. The other four aggregate rows are `DESCRIPTIVE_V_RMST`. SETUP uses `GAUSSIAN_PROXY`, and all 165 selection rows use `ORACLE_DIAGONAL_GAUSSIAN_PROXY` with `ANALYTIC_PROXY`. [Analysis](AUDIT-stream-32-t7-full-20261124.md) · [Mapping](../docs/MAPPING.md#stream-32-student-t7-full)

## Protected publications

All eight files in each Gaussian publication match the Git baseline `94b4e2a5d4abb2fcadbdec46adab47a45e6b927b` byte for byte. Both manifest digests match the A2 witness. All eight T7 Pilot publication files match its terminal inventory. The complete 98-file Pilot inventory, the five FAIR CSVs and the Pilot ledger, FINAL and audit digests also match the earlier receipt. [A2 receipt](RECEIPT-stream-32-t7-tech-A2-20261122.md#protected-inputs-and-next-gate) · [T7 Pilot receipt](RECEIPT-stream-32-t7-pilot-20261124.md)

The sealed JSON reports, supervisor receipts and staging evidence are retained locally under ignored `logs/` paths. The report and receipt identify them by path and SHA-256.
