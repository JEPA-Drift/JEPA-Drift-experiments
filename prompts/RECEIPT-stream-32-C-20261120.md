# Stream 32 — Lot C runtime receipt

20 November 2026. **Lot C accepted with four runtime checks passed.** The run used the `stream-32-pca-info-online-20261114` worktree at HEAD `e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a`. Every campaign used the shared experiment lock, the deterministic `.venv` environment and synthetic smoke settings under `SMOKE_NO_CLAIMS`.

## C1–C3

The [C1–C3 runtime GO](GO-stream-32-C-20261120.md) authorized design `9118b16cfb296c87e1e2d006c875001be45a1feee4cf495eb1a50475a5ccd65b`. The common realized identity is `d2fc7c1d8ff3f8471a639b557e38d1c0067018975f2fe73ebaee47ef7e99fd71`.

| Gate | Measured evidence |
| --- | --- |
| C1 | The uninterrupted smoke exited 0. The `COMPLETE` manifest bound the five FAIR CSV SHA-256 values. `FINAL.json` recorded the manifest SHA-256 `81f5cd4dfec71672b998ebfa21d329fe8d597e76a24654ba68d4049dd0e132e0`. The system call trace recorded one successful atomic directory rename before the FINAL rename. `NULL_PLAN` committed one 40-row partition and froze `n_hold=80` with `PLAN_CAPPED_EXPECT_INCONCLUSIVE`. |
| C2 | Cuts after SETUP, DEV, CAL and NULL_PLAN each exited 75 at the committed phase. The four resumed processes exited 0 and matched the C1 realization and five CSV hashes. SHA-256, inode and modification time stayed identical for 10, 83, 100 and 103 committed files, respectively. The guards detected zero prior-partition productions and zero recalibrations. |
| C3 | Separate fresh runs at jobs 1 and 8 each exited 0. Both independently verified publications matched the C1 design, realization and all five CSV hashes. The output and log directories were distinct. |

## C4 profile

The [supplemental C4 GO](GO-stream-32-C4-20261120.md) authorized a derived configuration with `envelope.jobs_max=12`. A locked `--describe` comparison verified that the rest of the descriptor and the seed plan matched C1–C3. All four C4 runs used design `d9b002579815c197daeea5cdcb2b8674c6c74556d2b073916788091e0ca3592c`, achieved realization `c286d3c584c38a00647c9a5ea286e0881635cde040a51cd3d1252c0446386246` and matched all five CSV hashes. Each scope exited 0 at an effective memory limit of 34,359,738,368 bytes. All recorded `memory.events` deltas were zero.

| Workers | Wall (s) | GNU `time` CPU (s) | Application CPU, self + children (s) | Aggregate peak (MiB) | Allocated disk (MiB) | Nominal units per application CPU-s (millions) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 300.54 | 299.01 | 297.89 | 195.20 | 36.97 | 66.23 |
| 4 | 326.42 | 500.65 | 499.48 | 615.82 | 36.97 | 39.50 |
| 8 | 326.67 | 694.81 | 693.67 | 1,035.86 | 36.97 | 28.44 |
| 12 | 326.67 | 877.42 | 876.28 | 1,435.47 | 36.97 | 22.51 |

GNU `time` measured user plus system CPU and wall time outside each scope. The scope recorded `memory.peak` and `memory.events` before teardown. Allocated disk includes publication and staging, 38,764,544 bytes in every run. Apparent disk usage was 38,343,255–38,343,279 bytes. The audit retains both measures per job.

One worker had the lowest wall time, application CPU and aggregate peak in these four smoke runs. The throughput column divides the nominal §17 smoke workload of 19,728,600,000 units by measured application CPU seconds. Applying the same CPU cost per nominal unit to the §17 Gaussian pilot workload gives an indicative 0.41, 0.69, 0.96 and 1.22 CPU-hours for 1, 4, 8 and 12 workers, respectively. This extrapolation assumes proportional CPU cost across cohort sizes. One measurement per job level is available. Pilot authorization remains a separate R2 decision.

## Audit evidence

| Artifact | SHA-256 |
| --- | --- |
| [C1 audit](../logs/stream-32/lot-c-c1.audit.json) | `26c29abe8b06410fbcf038655449ff68bc857d52588f6c1adbdf377ab096dca3` |
| [C1 rename trace](../logs/stream-32/lot-c-c1.strace.log) | `dc64bd178ba8b82beb30dfdc4d5481059cbd5dd8c91ad22378bffcaaf6d9c8ce` |
| [C2 audit](../logs/stream-32/lot-c-c2.audit.json) | `9fe56526f0467597c0108f42e7698df828f30bb86d105c71fe2f6e731ffbf4b0` |
| [C3 audit](../logs/stream-32/lot-c-c3.audit.json) | `bba6f4ce47baea4d5953b0e0e84ff55b49c2238b920485e9e36de8faed634acd` |
| [C4 audit](../logs/stream-32/lot-c-c4.audit.json) | `023787c64848b287b1cfd4800827bd9e607cae0391164a754149985bf0c05a5f` |
| [Derived C4 YAML](../logs/stream-32/lot-c-c4-profile.yaml) | `6c57d6c0251b1237515d96e17e70dfb07057b04a9209dba1b9ffb8838baece05` |

The C1 and C4 audit reruns under the shared lock reproduced their recorded JSON byte for byte. The B4 source, tests, sealed benchmark, source YAML and section note retained their receipt hashes. The [contract matrix](MATRIX-stream-32-T1-T68-20261114.md) records all four runtime outcomes. This receipt closes Lot C. The pilot, full and job 16 gates remain closed.
