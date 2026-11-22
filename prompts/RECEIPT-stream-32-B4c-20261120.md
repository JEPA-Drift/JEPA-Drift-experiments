# Stream 32 — B4c receipt

20 November 2026. **Bounded spawn scoring received on deterministic fixtures.**

Score batches retain the existing path seed keys and the requested
trajectory order. Jobs 1 and 3 produced byte-identical EXACT and
FITTED results for the tiny witnesses. Separate parent and spawned
worker startup refusals were observed. Expired deadlines block before
work, and the iterator timeout fixture exercises cleanup. The rejected
V1 deadline and NumPy jobs defects are covered by direct probes.

Locked RED C0 recorded five absent-API failures and 1,012 passing
in 48.05 s. Locked GREEN C0 recorded **1,017 passing in 44.56 s**.
AST, source reconstruction, pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `2cb6b8be479527b0f8fddee3ef64b32f856daa252a05a92925fedbf2a23568c5` |
| `tests/test_pca_info_online.py` | `9e0a4888741e13db2dd37a545fa49ed0e10747e9cee298f016fb41fe304be3f6` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4c-green.pytest.log` | `8964a1d533e64f129b2f01c456e7728af8a5398956b826975fe263d6557b8580` |
| `logs/stream-32/lot-B4c-green.checks.log` | `a5d342d77654bc33ee1371b950cd261690243b0da2166e78531af4abc781f0bf` |

T44, T46 and T62 retain partial status. Integration into phase
controllers, durable budget checkpoints, CLI artifact comparison
and runtime measurement remain open. Matrix totals are 35 PASS
and 33 NOT_RUN.
