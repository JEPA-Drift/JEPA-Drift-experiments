# Stream 32 — B4k receipt

20 November 2026. **Descriptive V/RMST aggregate table received on a fixture.**

Two verified ALT cells form one RESIDUAL group. The surrogate and joint
Spearman coefficients are both +1 in that fixture. The CSV records
DESCRIPTIVE_V_RMST, the group size and both source SHA-256 values.
A wrong source hash is rejected before writing. The source CSVs and
staging tree remain identical. No score, fit or calibration supplies
the diagnostic after the source CSVs exist.

Locked RED observed one expected missing-exporter failure and 1,025
passing in 61.08 s. Locked GREEN V2 measured **1,026 passing in
57.20 s**. Exact reconstruction, frozen tests, the producer seal,
pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `c3410f5244aa2507c7d1a065c3b8c4e8eebaec8cf81118f9cbfd2ef04fa2983d` |
| `tests/test_pca_info_online.py` | `6f040a6101f315e4312dc42fcdb50577dc075228e4a13b095a6d9dbeae0224f6` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4k-green-v2.pytest.log` | `4085638c20105fe228304707da5a78520d98898abf8ec6fdf9c3f1f7f0fcbdee` |
| `logs/stream-32/lot-B4k-green-v2.checks.log` | `5e25e1e28530a0f7a0855c6dbcebc75fe80dbc993bef6114bcccaa3a97ba6564` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `a12cc674a6b6af4ff81120c63fcfcdd0b1b9f113d3480f091dcb8c2dc272ba07` |
| Fixture aggregates.csv | `c34b5880fa7bda633d44fe57c062aabd1c22f4d52350b94d676d75061714713f` |

T49 passes on fixtures. T16 retains partial evidence until the
complete publication is witnessed. Matrix totals are 36 PASS
and 32 NOT_RUN.
