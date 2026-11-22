# Stream 32 — B4h receipt

20 November 2026. **FAIR CAL payload received on a fixture.**

One committed non-oracle threshold and one family-specific oracle
threshold round-trip exactly, including setup, policy and calibration
IDs, CAL maxima hashes and GE rank counts. The oracle retains
NON_DEPLOYABLE_ORACLE_CALIBRATION. Reversed threshold insertion order
produces an identical calibration.csv. Scoring and ranking are
trapped during export. The staging tree remains byte-identical.

Locked RED reported one expected missing-exporter failure and 1,022
passing in 60.40 s. Locked GREEN reported **1,023 passing in
55.91 s**. Exact reconstruction, frozen test prefix, producer
seal, pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `70a59e53709b21668cf8bd37803e04b0fa8a3041bcbcc81e27bf52a77431a655` |
| `tests/test_pca_info_online.py` | `582474fbb0c2988c991ac3ceeb366f0aa6816fb2dde1fad3d4b51a42b16df489` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4h-green.pytest.log` | `789f0573c26629d640d6aa814c88584d5f193ebd3c6e5feb73a8a9d4eaa262de` |
| `logs/stream-32/lot-B4h-green.checks.log` | `4a69e4312a5e41eb47e180c0d0757bb9310fc5da791ddd7097d5f14edad0c089` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `88e2282d6037719b42fdcbbd6d6254574ddfa4ef599a5adfc8325d165ff5765a` |
| Fixture calibration.csv, both exports | `2a363da39916f23961cfe34d13349fdbdfbbd46b6d14fbcec225564384384f6a` |

T16 receives partial scientific payload evidence. Selections from
committed ALT masks and the final publication bundle remain open.
Matrix totals are 35 PASS and 33 NOT_RUN.
