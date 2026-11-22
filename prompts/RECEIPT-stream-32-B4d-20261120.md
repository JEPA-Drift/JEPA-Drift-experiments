# Stream 32 — B4d receipt

20 November 2026. **Partition budget admission received on fixtures.**

After encoding a new partition and before the first write, the CPU
journal is checkpointed and the remaining budget is checked. The ALT
witnesses reach either the CPU cap or wall deadline during production
and leave the candidate NPZ and JSON absent. The first DEV_LIB batch
remains durable under the received between-batch rule. The analysis
retains the original B4d RED, the failed V1 and the corrected C0.

Locked RED had two expected failures and 1,017 passing in 48.96 s.
V1 passed both new tests but regressed DEV_LIB and was reverted before
consolidation. Locked GREEN V2 had **1,019 passing in 44.96 s**.
Direct serialization-boundary proof, AST, source reconstruction,
pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `bf2763e89ce45924706bffdb6e6bb7d923c1f0f1a94bb90dc1a2668a724cf358` |
| `tests/test_pca_info_online.py` | `56ef7998284d5c2f00f41e3db6fea52351107e8d16d99632ea5a0540785cc4dc` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4d-green-v2.pytest.log` | `de575964f8c0dd056465799bb80877563a379c9ef9c5a07aef1c756de214a04d` |
| `logs/stream-32/lot-B4d-green-v2.checks.log` | `21b71aa80b26bfd1c88065f8391f60adf35be54c17727ab0e433d6d4c2ec0159` |

T46/T62 gain this partition-level proof and remain partial pending
global driver budgets and resume. Matrix totals are 35 PASS and
33 NOT_RUN.
