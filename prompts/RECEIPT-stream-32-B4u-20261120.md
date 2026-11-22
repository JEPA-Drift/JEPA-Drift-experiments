# Stream 32 — B4u receipt

20 November 2026. **The non-oracle monitor is invariant under post-score simulator metadata poisoning.**

The dependency AST covers non-oracle masking, calibration and
evaluation with the exact ONLINE signature. The synthetic ALT
fixture replaces six metadata rows with raising objects after the
real score batches. The monitor is also guarded against simulator
and oracle calls. Durable staging and the scientific publication
are byte-identical to the unpoisoned reference.

Tests-only locked C0 measured **1,054 passes in 88.70 seconds**.
Exact append, frozen test prefix, source and producer SHA-256,
pyflakes and diff-check were verified.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `1ac3087878237d32af7e44f5411d9589cc553b8a439c677d4fe9d93a4499646e` |
| `tests/test_pca_info_online.py` | `108a80532d7b5afcee744095363f30254a2a60f1cb44e2c904a01a2c680fad50` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4u-tests.pytest.log` | `72bf87dd570bad502377fe0c94ec28a63e6dae1f61d63a6121f00273a4590fd4` |
| `logs/stream-32/lot-B4u-tests.checks.log` | `341ab75f2f3db53cc5a1d348e25307a36358e2d0453c67aca68171ba6b058aec` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `e6b9b9806eacdf1fba65ab27ca892ec88be977d9bf729678163775926150fbbf` |
| Reference and poisoned fixture manifests | `5066154992bb748d2c12e2d4f3988e9401ef8aef51712409a3c59f215817709e` |

T25 and T38 pass. Matrix totals are 54 PASS and 14 NOT_RUN.
The full-mode confirmatory publication remains open.
