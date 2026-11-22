# Stream 32 — B4l receipt

20 November 2026. **Five scientific payloads published on a fixture.**

The incomplete fixture writes a staged INCOMPLETE status and leaves
its publication destination absent. The complete fixture atomically
publishes the five scientific CSVs and three metadata files. Its
manifest records 13 LOCAL_HASHED_ONLY partitions. Both HOLD issues
retain their committed IDs, status and oracle qualification. The
complete replay checks the existing artifact and makes no new
export call. Path and size checks from B1 remain in C0.

Locked RED observed one expected missing-bundle failure and 1,026
passing in 62.69 s. Locked GREEN measured **1,027 passing in
58.33 s**. Exact reconstruction, frozen tests, producer seal,
pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `722b53910748925efc114a234a8b97a4c219e26a2ff66ec203dc177959c1adfa` |
| `tests/test_pca_info_online.py` | `cda38e04c375b63008114b2b34a3a81554802afc8715ddeb98f03e52dc22c4f5` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4l-green.pytest.log` | `b925ce8b65ceba9fbb205f5f14fa79e92344896866c1929f26e31a2b914ca1a0` |
| `logs/stream-32/lot-B4l-green.checks.log` | `4eceff668bac559dcb2a6cd43627793894fd32299d9a9a8b094d5b87c8b62d77` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `9a61443d886a07022dada776a45949dfacbd6a26a79b4800e3dbb4bece3dd13d` |
| Fixture manifest.json | `871c1dc447417bfa238fa2e3fa1b4e5d89788f6b5182b8ac3072b37fee2ceb82` |
| Fixture issues.csv | `21d357e8aee74131b4e63431a3d0b0d281f839a953ae72e390793990fad7c922` |
| Fixture realization ID | `ea8ff8d8edd0018ad98f660779f64c83828a5f8e16fa36b478dafb4d4cea7388` |

T16, T50 and T59 pass on fixtures. T60 receives partial evidence
while CLI crash recovery remains open. Matrix totals are 39 PASS
and 29 NOT_RUN.
