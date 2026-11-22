# Stream 32 — B4o receipt

20 November 2026. **Both authorized CLI modes publish with a pre-execution design GO.**

The pilot and full synthetic fixtures use one fitted Gaussian
setup, 24 assets, six monitored observations and one serial worker.
Changing only the seed changes the design ID. Each GO derives
from the pre-execution design and its scope. The published manifest
and FINAL bind the new realization without rewriting the GO.
Pilot records NULL_PLAN as NOT_APPLICABLE. Full records one
NULL_PLAN partition and n_hold=5 under PLAN_CAPPED_EXPECT_INCONCLUSIVE.

Tests-only locked C0 measured **1,032 passes in 74.30 seconds**.
Frozen test prefix, explicit source and producer hashes, pyflakes
and diff-check were verified. Both CLI invocations use tmp_path.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `1ac3087878237d32af7e44f5411d9589cc553b8a439c677d4fe9d93a4499646e` |
| `tests/test_pca_info_online.py` | `3a3610182495f7a145ef1d146c3436ea93e95b32a0b798efeeff4b9aa2f5bff8` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4o-tests.pytest.log` | `68eea1532477bb0eb007116cb2c51f4d81ba7fea80a2a3ec55d323a789184960` |
| `logs/stream-32/lot-B4o-tests.checks.log` | `59d46d84cb156179967853d41dea8a36858d445e6d91df123bdfa3969c801bc9` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `755ad2c259aab5a119dfa0734a75f25bde8f05f77277afcc44af15db8c339f40` |
| Pilot fixture manifest | `d16588623c2070af00075e363deec5e36835e76cb8ac6be39b5d432fd4c6a503` |
| Full fixture manifest | `b1a1d2766fd798773686eb4aa2212a95252a1f60351bf31df3fda91b1fbe7e04` |

T53 passes. Matrix totals are 44 PASS and 24 NOT_RUN.
Driver refusal and phase interruption witnesses remain open.
