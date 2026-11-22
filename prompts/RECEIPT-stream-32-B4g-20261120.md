# Stream 32 — B4g receipt

20 November 2026. **Scoring deadline and reference replay received on a fixture.**

A simulated monotonic deadline reached the real scorer during CAL
after SETUP and DEV committed. The interruption recorded
BLOCKED_RESOURCE with CAL, HOLD and ALT keys pending, and retained
the injected 8.0-second CPU delta. The resumed invocation kept the
prior CPU entry, ran no new DEV choice or score, and finished with
the same durable bytes and phase records as the uninterrupted run.
The blocked status records the interrupted invocation. Publication
status remains the responsibility of finalization.

Locked RED reported one expected missing-status failure and 1,021
passing in 59.50 s. Locked GREEN reported **1,022 passing in
55.55 s**. Scope, exact B4f reconstruction, immutable test prefix,
producer seal, pyflakes and diff-check passed.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `fa8bd952d97a43acdc4b0e1f75f05b5b2d0f2d48e59cc8f2f70b6ca64dbb488e` |
| `tests/test_pca_info_online.py` | `e33cc5d2c9d89cc725ebf6781efd79797bb6e4e95f58f79d92be71ec5cc74532` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4g-green.pytest.log` | `0814846c3de8a2dff8206db9cbdcf722f248af513fb7d32d7635b279e1b9d6fe` |
| `logs/stream-32/lot-B4g-green.checks.log` | `64a39820f925de99d9f3e415ecd76b34c34e3de35d9cfcc5bc6d21888d0de492` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `c3b678514dacbb24162a2cd9ec5c22bb192b7e9fdfdf8b6ba1024cfe22c92746` |
| Fixture design ID | `42ddea67cb9c7ce48c3eca4c7fb9c6beddad4927c0e71b00f3003943534c1441` |
| Fixture ALT phase digest | `e4c6f19c1f2e817e3ba0acca32e1a33e91df85d1d348e843bb3a4c1f7999d22d` |

T45, T46, T57 and T62 receive partial evidence. CLI, publication,
remaining interruption coordinates and runtime measurement remain
open. Matrix totals are 35 PASS and 33 NOT_RUN.
