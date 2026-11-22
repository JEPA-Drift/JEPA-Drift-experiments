# Stream 32 — B4f receipt

20 November 2026. **Admitted phase driver received on a synthetic fixture.**

Two independent staging directories ran the same tiny EXACT N=24
RESIDUAL/F2 design, once at jobs=1 and once with a real spawn pool at
jobs=3. Each recorded six phases and verified 13 partitions. The
partition counts in phase order were 1, 9, 1, 0, 1 and 1. NULL_PLAN
was explicitly inapplicable because the primary fitted setup was
outside the fixture scope. All durable files matched byte for byte.
A fresh token replayed the second staging without a new batch score.

RED under the shared lock observed one expected missing-driver
failure and 1,020 passing in 50.77 s. GREEN V2 under the same lock
reported **1,021 passing in 55.31 s**. Exact reconstruction, fixture
prefix, pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `5994eecbcff6cea62df2634c4966e72eb9c96f823820097ffbe16497856b22b6` |
| `tests/test_pca_info_online.py` | `993f4998ffdc26e3d17a9809dd7f7e56e8087772583d239f8d8a90ff6d78f7ad` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4f-green-v2.pytest.log` | `3700d62cefe2ec7df3ae57edd9821015ef4ce3ed1463d0a37138515ce2e05eec` |
| `logs/stream-32/lot-B4f-green-v2.checks.log` | `2ce69b66114dac3a0508871b81da5dceab246276ae293020a303c06dcae4026a` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `dbe298f2a51dbafcd56e065fae3cef8f7855afc8d34ed3b920d1247a677dacca` |
| Fixture design ID | `bb0a19a7d9112b54abd914289a9b669868c02a1d19819db0e7c3d644c85f2a38` |
| Fixture ALT phase digest | `e6b9c838da94f8114c27ee9a19d01aeb7deaf9e2461ac0edec35d10b7553fdc1` |

T44, T45, T47, T56 and T57 receive partial evidence. Interruption,
resource status, CLI and scientific publication remain open. Matrix
totals remain 35 PASS and 33 NOT_RUN.
