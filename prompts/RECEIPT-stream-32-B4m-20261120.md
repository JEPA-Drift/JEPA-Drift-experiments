# Stream 32 — B4m receipt

20 November 2026. **Synthetic CLI publication is equivalent at jobs 1 and 3.**

The admitted CLI uses the existing phase driver and atomic finalizer.
A same-basename invocation that reuses the default log directory
without resume is refused. With independent logs, the serial and
three-worker runs publish identical scientific artifacts. A completed
resume verifies the existing publication without rescoring or
exporting. Operational telemetry contains jobs, cumulative
SELF+CHILDREN CPU, invocation wall time and parent peak RSS. Scope
peak remains NOT_MEASURED in this fixture.

Locked RED observed one expected unwired CLI failure and 1,027
passes in 62.56 seconds. Locked GREEN V2 measured **1,028 passes
in 67.49 seconds**. Exact source reconstruction, frozen tests,
producer seal, pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `1ac3087878237d32af7e44f5411d9589cc553b8a439c677d4fe9d93a4499646e` |
| `tests/test_pca_info_online.py` | `95b688f7699793b664c1fe8203588a00d2ae0e2ff27b69c2e7f4a75a52298f23` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4m-green-v2.pytest.log` | `9ba8a8d345faf2f511ae3d1aee26bb24a5941d737fa4e97483eeff657dca2862` |
| `logs/stream-32/lot-B4m-green-v2.checks.log` | `96186dc31aef7ff0d84859acef6eaaf406c4c870d03a7e66603d2577c6ab082a` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `c519ff6eec91177651d820928f60377fcc18690f46070843af606b34b7b4ad43` |
| Fixture manifest.json at jobs 1 and 3 | `423b9d3d771133ac57f9a4c3bd5dd3f9a024efdfab5f6826cdb7bced4ae55ccb` |

The fixture design ID is
`834eb1351c62cfc526941d7827612c40a771263b08d24ba0f11af7f5eeff1c95`.
The realization ID is
`eb3f8e3f047184d238bd19f6ce3cbb2199d2e1a5328e39d38504b8d50ffd8197`.
Each manifest records five PUBLISHED CSVs and 13 LOCAL_HASHED_ONLY
partitions. Both FINAL records bind that same manifest.

T44 and T56 pass on fixtures. CLI crash recovery, stale refusal,
positive pilot and full on fixtures, and CLI resource refusal
remain open. Matrix totals are 41 PASS and 27 NOT_RUN.
