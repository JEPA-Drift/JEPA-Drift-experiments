# Stream 32 — B4s receipt

20 November 2026. **The phase driver rejects five invalid admission states before any effects.**

The real driver rejects an altered design descriptor, wrong
authority handoff, different planned ALT inventory, excessive
jobs and an invalid GO digest. The fixture trees are unchanged
under traps for writes, draws, workers and each phase controller.

Tests-only locked C0 measured **1,050 passes in 86.77 seconds**.
Exact append, frozen test prefix, source and producer SHA-256,
pyflakes and diff-check were verified.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `1ac3087878237d32af7e44f5411d9589cc553b8a439c677d4fe9d93a4499646e` |
| `tests/test_pca_info_online.py` | `47256756cdabcac6e9857c47e293358c2d3c0b62139fc18a7bb90b9af345779c` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4s-tests.pytest.log` | `f45ee3d605a7691263bb41216cf0cf8416e3b7d83e4f87ab4f8d1306df3fff73` |
| `logs/stream-32/lot-B4s-tests.checks.log` | `65e24112d8152aa2c753b25958016891bf9c2e90dfe97c4a851dc66d96221a65` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `35dd1d943706b73dba89336d219392ecd97442804500968d41be17c72cfb56e5` |

T47 passes. Matrix totals are 50 PASS and 18 NOT_RUN.
