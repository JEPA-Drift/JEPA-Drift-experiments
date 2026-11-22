# Stream 32 — B4q receipt

20 November 2026. **The CLI refuses seven stale or inconsistent staging states without mutation.**

The full fixture cases cover a conflicting full design ID under the
same tag, a bad upstream digest, both n_hold bounds, missing
NULL_PLAN before HOLD, and a modified or missing HOLD NPZ with its
original sidecar. The CLI refuses all seven before a new invocation
or scientific work. The staged and published trees retain every
byte after each refusal. All test activity is under tmp_path.

Tests-only locked C0 measured **1,043 passes in 83.59 seconds**.
The exact append, frozen test prefix, source and producer SHA-256,
pyflakes and diff-check were verified.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `1ac3087878237d32af7e44f5411d9589cc553b8a439c677d4fe9d93a4499646e` |
| `tests/test_pca_info_online.py` | `4400799c8b3f5c8d88bf8c05ad5da0d11fa1754d33938016f21ffa67b522a7cd` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4q-tests.pytest.log` | `a0acd2dfd182deb17e26bff3a1943a1b578b9a573620aaa3b9ec491288143760` |
| `logs/stream-32/lot-B4q-tests.checks.log` | `7755e5c15fb51b644a6df0507671037c863f8fcfe4c0a35207dfcf4bc3d8386b` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `316badbe440a5df68eb9a236047c84ca85cb17c91e764fe7329cc343191d25f2` |
| Seven unchanged fixture manifests | `b1a1d2766fd798773686eb4aa2212a95252a1f60351bf31df3fda91b1fbe7e04` |

T45 and T58 pass. Matrix totals are 47 PASS and 21 NOT_RUN.
The CLI budget-boundary witnesses remain open.
