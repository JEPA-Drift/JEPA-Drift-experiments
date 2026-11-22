# Stream 32 — B4j receipt

20 November 2026. **Compact FAIR trial payload received on a fixture.**

The file reports two HOLD_NULL cells and two ALT cells, with first
alarms traceable through canonical partition keys and SHA-256. The
mixed ALT cell has one hit on day 2 and two censored paths. Its
six-day RMST is 14/3 and its detected-only median is 2. The other
ALT cell is fully censored. HOLD retains the recorded null bounds
and inconclusive status. The oracle qualification is preserved.

Locked RED observed one expected missing-exporter failure and 1,024
passing in 61.34 s. Locked GREEN V2 measured **1,025 passing in
57.37 s**. Exact reconstruction, frozen tests, the producer seal,
pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `f07bf858b06496637d1b6339035fc5850e359afdbf05718ca975497509183393` |
| `tests/test_pca_info_online.py` | `230cdf08b7a2e0b7ab5fe68d97141009173df222b563cc0f33665d5c198ca970` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4j-green-v2.pytest.log` | `1f2bc49254ab6b7de45b104625906f0c6891cfc90462486f37ff1c68b44191e8` |
| `logs/stream-32/lot-B4j-green-v2.checks.log` | `69c7ca1d89a617bfb12051d56359dbf5ba1d18ab5f3b605c403b5c6cc3a96f65` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `3b925057dc0d4e2d100e68f6e3881b85eb8c860be3efee93c454cf79f069a184` |
| Fixture trials_summary.csv | `50f4c992f5158bfbcd670661d924d71a83e3feb67beae0c9124738e7e1ea14f1` |

T16, T19 and T49 receive partial evidence. Final publication and the
descriptive diagnostic join remain open. Matrix totals are 35 PASS
and 33 NOT_RUN.
