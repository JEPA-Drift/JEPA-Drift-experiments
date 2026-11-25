# Stream 32 Student-t7 — technical A2 receipt

22 November 2026 · `T7_TECHNICAL_GO` · `NO_RUNTIME_GO` · `NO_T7_PILOT_GO` · `NO_T7_FULL_GO`

Worktree and branch `JEPA-stream-32-Student-T7`, baseline `94b4e2a5d4abb2fcadbdec46adab47a45e6b927b`. The written decision approved the prospective descriptive amendment and the deterministic A2 work. The Gaussian §18 gate remains closed. [Written decision](GO-stream-32-t7-tech-20261122.md) · [Deviation](../docs/DEVIATIONS.md#c-pca-info-online-t7-prospective--extension-descriptive-student-t7-2026-11-22)

## Artifact fingerprints

| Path | SHA-256 |
| --- | --- |
| `tools/ops/audit_stream32_t7.py` | `6c874cdb58a12787f538503fa42117d61e3582ae29597b9e8f5398115da54021` |
| `tests/test_stream32_t7_audit.py` | `2e21c69ffe99961a5967bd14c7ff64e1f55dc10b127c2194c97384ebec17cb90` |
| `tests/test_stream32_t7_native.py` | `66bcd3cded02a2c2470018603c05708ef65e4c3724fe57d0c9b47bf654e767c9` |
| `tests/test_stream32_t7_launcher.py` | `bcb114eae53e6124ce51f6f14e53b0c89dae1da40f0055f01b54909637248011` |
| `logs/stream-32-t7/run-t7.sh` | `2c11edf1fdebc394c353e66c54219ec18f5cf759b3071db081bf64104c5b2115` |
| `logs/stream-32-t7/check-t7-status.sh` | `e624f3dce97fef765e20d4d9c9c2ca6c7a9f09bd3fd54f73746f651d98191f5d` |
| `logs/stream-32-t7/t7-worker.sh` | `8b7adb653721bcd103273b5e50aaf7bfeeda6bb18fb7273c4c8463c8e89565b5` |
| `logs/stream-32-t7/t7-wall-guard.py` | `c0688b6ab6ee5e07123d933517da2e450b3b132d4ef246893ed40bc677aa5719` |
| `logs/stream-32-t7/t7-supervisor.py` | `276d464275f6cad63395778a1f29e42fa3f3bda792e8dc1769658d9402f5480c` |
| `configs/pca_info_online_t7_qualification.yaml` | `0286dd3f5916254b1ab4c1d148361280206fadfb4efbe0569008f5ea5ff99d96` |
| `prompts/DRAFT-stream-32-t7-runtime-intent-20261122.json` | `b92556beabdbe2a10774bf5eef772defca37deb04e6253d57ecbb52e03c1c507` |

## Deterministic results

The native pilot and full fixtures used H = 250, both T7 dimensions and the canonical scope. Each committed `4/18/4/0/4/10` partitions for `SETUP/DEV/CAL/NULL_PLAN/HOLD/ALT`, with ordinary CAL, `NULL_PLAN=NOT_APPLICABLE`, no H1–H3 rows and 40 `LOCAL_HASHED_ONLY` payloads. The five FAIR exports retained their original machine statuses and all three information proxy labels were checked. The fixture identifiers are unrelated to future campaign authorizations.

| Fixture | `realization_id` | HOLD validated / inconclusive / failed | Descriptive contrasts marked `NOT_CLAIMABLE` |
| --- | --- | --- | ---: |
| Pilot | `b4fec42b65b092beafcaead22f6a289f8487d0cd7ad1259a90671b17ff992538` | 27 / 56 / 4 | 1 |
| Full | `3e518f6cdd344a6a2b4e8736e3cb4e2de62cea272d116a22ad6496a9872df32d` | 13 / 43 / 31 | 163 |

Both final report pairs have verdict `PASS`. The files are under `logs/stream-32-t7/a2/make-check-tmp/test_t7_native_unallocated_pub{0,1}/`.

| Fixture | Pre-ALT seal SHA-256 | ALT report SHA-256 |
| --- | --- | --- |
| Pilot | `f754739a24dcf6a828163d2df4ebd597f83843e6fda7282e985bb669e418129a` | `1c380a5a0b7cb279d6f88ca472c720564946c6f58d8ee4ac16d090fb72f4487d` |
| Full | `3fa5664a357cd0f502d0fb74ea9b33443b71cda5b8806a14d4656579d414389c` | `93a0db86691045c94dfc73e21f10b7bdf5368e002239a99ab5e261bdd60d2d2f` |

The pre-ALT replay uses index 0 per cohort and spans both dimensions, every runnable policy, and every applicable oracle family. All CAL maxima and HOLD first-hit vectors are counted. The independent direct segment scan checks the CAL maximum, HOLD/ALT masks and first hits. The relative and absolute replay tolerances are `5e-10` and `1e-11`. Masks, first hits and the stored GE threshold at the floating-point successor are tested exactly. The auditor verifies 16 HEAD sign profiles per residual setup. The report SHA is captured before the auditor accesses ALT. The native fixture runner already generated ALT at that point. The canary guards ALT records, ALT NPZ/sidecars and the publication. ALT verification joins raw first hits and information proxies to the exports, reproduces the paired bootstrap and V/RMST ranks, and marks failed-null contrasts in a separate strict JSON report.

The native tests exercise elliptic daily scaling, disjoint seed roles, metadata invariance of non-oracles, causal windows, GE ties, a refused design and the three HOLD classifications. Reduced-size limit fixtures exercise both sides of the 50 Mio boundary, including the allocated read rule. Faults injected after a partition commit and after publication rename preserve the committed prefixes and scientific outputs on resume. The launcher tests cover stage authorization, input and publication identity, concurrent lock refusal, file and directory `fsync`, conservative charging after loss of measurement, receipts and resume, and the qualification stop after CAL. The cgroup state evidence in A2 comes from controlled fixtures. Actual service admission, resource limits and forced termination remain measurements for the proposed runtime stage.

## Verification record

All fixture invocations used `.venv/bin/python`, the shared execution lock, `MPLBACKEND=Agg`, `PYTHONHASHSEED=42`, `MKL_CBWR=COMPATIBLE`, and one thread for OMP, MKL and OpenBLAS. RED, static review and GREEN records are under `logs/stream-32-t7/a2/`. The first native run reached both publications and detected a test expectation about FAIR `NaN` fields. The test was corrected. The independently reviewed RED cases also cover a missing DEV recomputation and missing sealed ALT refusal evidence. The A2 tests and sealed fixture reports reside under the worktree. The launcher artifacts are local scripts under the repository’s ignored `logs/` tree.

The initial launcher fixtures read the kernel boot identifier for the accounting witness. The final launcher test fixture supplies a controlled boot identifier. The final file-descriptor witness uses a neutral child process and a local fixture lock.

`make prompts-check` returned 0 for all 34 stream prompts. The A2 synthetic `make check` invocation used the local selection plugin `logs/stream-32-t7/a2/a2_pytest_scope.py` with SHA-256 `c408ea6ba86cc45f05110c6293c7c961ea3c0de47456fa9a4055c2aeb7533e11`. It lists each deselection and ignores the Article B identity module. This perimeter excludes real-panel tests, including the Torch contract cases that require the real D3 fixture. [Targeted log](../logs/stream-32-t7/a2/targeted.log) · [Make log](../logs/stream-32-t7/a2/make-check.log)

- The broad synthetic run passed 22 contract/decoupling tests with 15 deselections. Its second pytest invocation passed 2,345 tests, skipped one and deselected 129. It reported one historical test failure at `tests/test_pca_drift_contracts.py:1193` and exceeded the five-minute repository budget at 634.63 s. A2's two end-to-end T7 fixtures and all then-current A2 tests passed in that run.
- The historical test expects the two generated input panels outside the producer's logical repository, so their manifest keys reduce to common basenames. Keeping pytest temporary directories inside the worktree exposed two distinct relative paths. A narrowed `make check` passed the unchanged test and all 22 scoped contract/decoupling tests. It used the local test-only plugin `logs/stream-32-t7/a2/a2_pca_contract_root.py` with SHA-256 `cc36e39917691864dc31ab32e20d0dd11d3b91968c450642c17c155bc544804b` to provide a nested logical source root. The implementation, fixture data and assertion remained unchanged. [Recheck log](../logs/stream-32-t7/a2/make-recheck.log)
- The final targeted check passed 64 tests. A2 therefore has 66 passing witnesses including the two end-to-end fixtures from the broad run. The three final launcher RED cases required rejection of changed token paths or unit before consulting cgroup state. They passed after binding the sample, receipt and unit to the reserved token. Pyflakes and all three wrapper syntax checks returned 0. The draft runtime preflight refused admission with exit 3 and created no qualification or campaign destination. [Final targeted log](../logs/stream-32-t7/a2/post-check-green.log)

## Protected inputs and next gate

| Path | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec` |
| `jepadrift/sim.py` | `0d7d45068f85a3dd64f25caeee9e5aa079c61bb8bbf30dc847dea0ba18bc383d` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `results/pca_info_online/pilot-gaussian/manifest.json` | `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8` |
| `results/pca_info_online/full-gaussian/manifest.json` | `16f5fdcfca5c08a97d8a6ff01a0cdf807b614b0d2321bf17b0abb0d9d86e0cbf` |

The qualification design was read through `--describe`. The draft intent binds a continuous and a resumed case to one design and one cumulative CPU ledger. Each case has a separate publication root. The YAML carries `authorization: null`. The draft leaves the future GO and execution YAML SHA fields null. Activation requires a separate written decision. A2 ends before runtime, Pilot, Full, commit or push. [Runtime proposal](DRAFT-stream-32-t7-runtime-20261122.md) · [Draft intent](DRAFT-stream-32-t7-runtime-intent-20261122.json)
