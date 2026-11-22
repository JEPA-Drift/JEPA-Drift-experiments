# Stream 32 — B4a receipt

20 November 2026. **CLI preflight accepted on deterministic fixtures.**

The CLI parses config, mode, jobs, output and log directories, resume
and describe. A null-authorization pilot fixture can be described
before any draw, worker launch, GO access or write. The printed ID and
descriptor agree with the pure design APIs, including after varying
invocation flags and poisoning earlier outputs. Pilot/full without a GO,
a changed seed and excess jobs are refused at the CLI with no effects.

Locked RED C0 reported five absent-main failures and 1,003 passing in
46.95 s. Locked GREEN C0 reported **1,008 passing in 40.23 s**. The
corrected standalone CLI check observed the same descriptor as module
invocation and the parent refused a mismatched OMP setting. Pyflakes
and diff-check passed. The first standalone check had counted a pytest
fixture symlink as a second fixture. The source and test suite were
unchanged during that correction.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `b864dfb2d616eed0a7a63681b199e600185d6411248e5765a558376cc0d1a140` |
| `tests/test_pca_info_online.py` | `99d2744fb1aba56ba81d71ae643c01a5d90cf754f70ddfe7c36492aedfde285c` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `logs/stream-32/lot-B4a-green.pytest.log` | `ee637d434a184a1d4f2e3832eac6f8d8af6baa5b40d7e4b8d221857f66f0078f` |
| `logs/stream-32/lot-B4a-green.final-checks.log` | `73e7f64a60842707d1bb3f77aa9f7726b309f2096860fa331f6e2d12a7b285b2` |

T52 passes. T54/T55 retain PASS with the CLI witnesses. The matrix
contains 35 PASS and 33 NOT_RUN. T47/T53/T61/T68 retain partial status
pending admitted driver execution and final guards. This receipt covers
preflight only. Worker enforcement, partition planning, execution,
recovery and publication on fixtures remain B4.
