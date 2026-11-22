# Stream 32 — B4e receipt

20 November 2026. **Six scoring routes received on staged fixtures.**

DEV_NULL, DEV_ALT, CAL_NULL, NULL_PLAN, HOLD_NULL and ALT forward their
existing seed keys and raw return deltas to the common batch evaluator.
The test checks the requested jobs and wall deadline, verifies the
expected inventory using committed payloads, and replays ALT without
making any new scoring calls or changing durable files.

Locked RED had one expected missing-route failure and 1,019 passing
in 50.02 s. Locked GREEN reported **1,020 passing in 46.46 s**.
Pyflakes, diff-check, scoped AST and exact source reconstruction passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `11264352df90dcc3994c1d3750667f6a75c89b93fbe4ce35fd46f8497a9470de` |
| `tests/test_pca_info_online.py` | `b6bba14c31071487561d8aac5c23c8ff3840d4836e252a5699577fd16a373489` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4e-green.pytest.log` | `c6b241ed3ad5437cbb9c503d9ef7058a35388f490e759b91837f1cffa0ca370c` |
| `logs/stream-32/lot-B4e-green.checks.log` | `667277c1170e5ffcd204549c92f03d292414f6a7ac279d2fd197ddd85cfdc38e` |

T41/T44/T46/T62 gain partial routing evidence. This receipt covers
the controllers with deterministic producer witnesses. Global
driver, artifact and resource acceptance remain open.
Matrix totals remain 35 PASS and 33 NOT_RUN.
