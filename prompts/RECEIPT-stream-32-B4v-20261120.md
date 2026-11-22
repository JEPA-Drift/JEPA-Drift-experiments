# Stream 32 — B4v receipt

20 November 2026. **The full CLI publishes H1–H3 from committed synthetic data.**

The publication build calls the established confirmatory helper
once after ALT and before FINAL. The existing aggregates.csv
contains three CONFIRMATORY rows plus the descriptive V/RMST row.
The five-payload publication inventory is preserved. The claim
rows carry exact bootstrap keys, ALT digest and strict JSON
evidence. The file SHA binds both the manifest and the realization
descriptor. Completed resume preserves every published byte
without another inference call.

The fixture consumes exactly five HOLD rows from the capped
NULL_PLAN and retains NULL_INCONCLUSIVE. It records H1 and H3
NOT_ESTABLISHED and H2 NONINFERIORITY_NOT_PROBATIVE.

RED observed the expected missing call and 1,054 passes. An
intermediate GREEN test used the wrong key container type.
After the exact one-line test correction, locked C0 measured
**1,055 passes in 90.00 seconds**. Frozen source ranges, exact
test append and prefix, pyflakes, diff-check and producer seal
were verified.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `f551b6fb78dc27f8969b7a1ed457620d64f21122f62741a5a45fe4f416cecb37` |
| `tests/test_pca_info_online.py` | `cc0a72c18e854f9adb562bbf34c2a9fd0198234a9616e37908c3d1e4652afe4d` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4v-tests-v3.pytest.log` | `407978fe4cca7c2edc76d62e89539558c1fb1fc079d85d80f733100fd798a84f` |
| `logs/stream-32/lot-B4v-tests-v3.checks.log` | `7e87c1c9ba4a153f78cf1c128a8e32cdcbbad30220b677e5c372728632da0dd7` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `fa7c3f6a21ea358ec84083fdb7fed50679295ab156599b95963f55054d9e753f` |
| Full fixture manifest | `0506e77018c47d93ed4d380154022faf4c643f51b132dfbbd400ea666b651945` |
| Full fixture aggregates.csv | `1f0af9e5916bb16406d0688632adaa62d17f6ed7c22bf82f7d6e54cc00674356` |

T19 and T21 pass. Matrix totals are 56 PASS and 12 NOT_RUN.
T41 retains its pending descriptive bootstrap linkage.
