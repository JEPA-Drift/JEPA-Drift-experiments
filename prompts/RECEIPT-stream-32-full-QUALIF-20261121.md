# Stream 32 — Full Gaussian Phase 1 qualification receipt

21 November 2026. **`READY_FOR_RESEARCHER_FULL_GO`**. Ten mandatory gates pass. The researcher transmitted an explicit Full Gaussian authorization for the frozen design and envelope. This receipt closes the qualification phase at its mandatory stop. [Qualification mandate](GO-stream-32-full-QUALIF-20261120.md)

| Frozen identity | SHA-256 |
| --- | --- |
| Full design | `8a4af3ecd7864f167ac32b82f0751547dc68b8a4bf24cec0f6c7fefbb19895d4` |
| Seed plan | `88e7c755bb33cd48c57bab000959cac09f4efb9211545951e4fc89469979c450` |
| Scientific YAML | `34d8addc6b4c91c821c94e0e075d2873952a7118203b3882942d99e46b278539` |
| Scientific runner | `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec` |
| Supervisor launcher | `a7a4a8ac7d42806227e93e69ea0710f02c5ee3924a3c1613e8ca55434da81b4c` |
| Supervisor implementation | `1682f87bcaf04be4b210fec4851848114d28f7bc338cb6bb3dd16578bfa099b8` |
| Status and reconciliation launcher | `de849b9aafafdba8adb854019e07cecde29bba8c3f09a9eb55d773c6e848f773` |
| Application wall guard | `58a98f231f906895e6a72ae80a934f8a77a751d7d5140a96c10b17c90640d33d` |
| Independent auditor | `b908760845cef42ab707fbb6384f8e3bde78e64d342be1134803c6cd7dd999dc` |

| Gate | Verdict | Observed evidence |
| --- | --- | --- |
| `T-LEDGER-DURABILITY` | PASS | The test executed file `fsync`, atomic replace and directory `fsync` in that order. The competing launcher observed the lock held with durable `RUNNING`. [Hardened log](../logs/stream-32/full-qualif-phase1-hardened.log) |
| `T-CPU` | PASS | Two children each used 0.7000 s and the parent used 0.2006 s. The scope recorded 1.749842 s and debited 2 s. Every process observed CPU 0 only. An altered receipt was refused on resume. [CPU ledger](../logs/stream-32/full-qualif-phase1-hardened/cpu/ledger.json) · [Hardened log](../logs/stream-32/full-qualif-phase1-hardened.log) |
| `T-WALL-CAP` | PASS | Under a 12 s cap, a worker and child ignoring SIGTERM were killed and the scope drained in 7.1693 s. [Wall ledger](../logs/stream-32/full-qualif-phase1-hardened/wall/ledger.json) |
| `T-SCOPE-LOCK` | PASS | Worker saw the shared lock held. The competing launcher was refused before it could create a ledger. [Hardened log](../logs/stream-32/full-qualif-phase1-hardened.log) |
| `T-SUPERVISOR-CRASH` | PASS | Separate SIGKILL tests of the supervisor parent and the active guardian drained scopes in 2.3029 s and 2.2901 s. Each interruption was charged and blocked pending reconciliation. [Parent ledger](../logs/stream-32/full-qualif-phase1-hardened/crash/ledger.json) · [Guardian ledger](../logs/stream-32/full-qualif-phase1-hardened/guardian-crash/ledger.json) |
| `MANUAL_FALLBACK_VERIFIED` | PASS | The status command reported the stopped scope and blocked resume. Verified staging evidence bound to the invocation token enabled manual reconciliation on the disposable fixture. [Forced-run ledger](../logs/stream-32/full-qualif-phase1-hardened/forced/ledger.json) |
| `Q-C1` | PASS | A clean resource stop after CAL preserved the complete committed prefix. The resume checked hashes, inodes and modification timestamps and rejected any attempt to produce earlier partitions. Altering the CPU receipt blocked resume. [Clean-run ledger](../logs/stream-32/full-qualif-phase1-hardened/clean/ledger.json) |
| `Q-C2` | PASS | Forced SIGKILL after CAL drained the hardened scope in 22.2430 s. Resume was refused before reconciliation. It then reproduced the continuous reference. [Forced-run ledger](../logs/stream-32/full-qualif-phase1-hardened/forced/ledger.json) |
| `T-2700-BOUNDARY` | PASS | The nominal test measured 2,695.2933 s including termination grace. The predecessor and hardened revisions use the same systemd runtime, start, memory and stop controls. The hardened short witness checked the revised settlement and recovery paths. [Nominal log](../logs/stream-32/full-qualif-phase1-boundary.log) · [Nominal ledger](../logs/stream-32/full-qualif-phase1-boundary/forced/ledger.json) |
| `T-AUDIT-PRIMITIVE` | PASS | Six primitive tests passed. The independent pre-ALT report preceded ALT access for each fixture. The two audits checked ranks, Clopper–Pearson, paired Tango, RMST, bootstrap and HEAD, including the three H1–H3 rows in the four-setup sizing fixture. The historical pilot retained its scope and four `NULL_FAILED`. [Pilot pre-ALT](../logs/stream-32/full-qualif-audit-pilot-pre-alt-a2.json) · [Pilot ALT](../logs/stream-32/full-qualif-audit-pilot-alt-a2.json) · [Sizing pre-ALT](../logs/stream-32/full-qualif-audit-sizing-pre-alt-a2.json) · [Sizing ALT](../logs/stream-32/full-qualif-audit-sizing-alt-a2.json) |

Both resume paths reproduced the uninterrupted realization `cc332e46877863132f9a1c4a4837c44c5e571c3555c50b1cc72422f27727d8c8` and all five scientific CSV hashes. This is a smoke fixture identity. The preflight refused `authorization: null` before creating a production ledger. [Continuous manifest](../logs/stream-32/full-qualif-phase1-hardened/baseline/out/manifest.json) · [Refusal](../logs/stream-32/full-qualif-preflight-null-a1.log)

The scientific limits remain 36,000 cumulative CPU seconds, 32 GiB aggregate memory, 2,700 seconds per invocation and at most eight workers, with one at initial launch. The application guard requests a clean stop from 2,000 s. Systemd has 2,693 s of runtime and 2 s of shutdown grace. An invocation requires 2,702 s of remaining CPU reservation. Accounting after the last readable sample uses the elapsed time until the scope is observed stopped as a conservative upper bound on the single enforced CPU. Staging integrity checks before admission and after scope stop run outside the timed scientific scope. A forced interruption still requires a separate human decision for production resume.

The shared lock was available and no Full scope was running or transitioning at inspection. The scientific YAML still carried `authorization: null`. The production ledger, staging, authorized execution YAML and publication directory were absent. The original YAML and pilot manifest still matched their receipt hashes. [Machine-readable readiness](../logs/stream-32/full-qualif-readiness.json) · [Auditor seal](../logs/stream-32/continuation.md)
