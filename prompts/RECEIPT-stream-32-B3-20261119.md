# Stream 32 — lot B3 receipt

19 November 2026. **B3 ACCEPTED ON DETERMINISTIC FIXTURES** under the
researcher's B-TDD GO and subsequent B3 instructions.

The worktree branch is `stream-32-pca-info-online-20261114`. The observed
HEAD is `e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a`. This receipt closes
the authorized fixture slice. The staging contracts use synthetic
authorization and payloads in test temporary directories.

| Receipts | Fixture evidence |
| --- | --- |
| B3a–B3e | CAL rank and frozen identities, one non-oracle calibration shared across families, family-specific oracle calibration, null-only sample sizing, independent HOLD cohort and verified ALT replay |
| B3f–B3h | Pair-specific FPR qualification, Tango and paired RMST bounds, H1–H3, frozen HEAD geometry and detectability, separate descriptive oracle contrasts |
| B3i–B3m | Full-horizon HOLD mask telemetry and H0 bias, ALT surrogate and joint information, descriptive V/RMST, HEAD isolation, matched-prior ratios and oracle alignment |

The thirteen tranche receipts and their counter-reviews record the
separate RED, GREEN and test-only evidence. Each tested source candidate
was reviewed before native application. B3l adds an isolation witness
that passed on the received source. The auxiliary independent reviewer
reached its quota during B3m. Codex performed the B3m counter-reviews and
locked verifications.

## Verification

The historical B2 result was **840 passed in 19.85 s**, with 21 PASS and
47 NOT_RUN in its matrix. The historical logs and receipt hashes were
checked directly. The final test file retains the exact 633738-byte B2
prefix with SHA-256
`73e931a1030a1587012d6b660a1b2b41a25d19e4da85f1d754c81ac51dbb4f59`.

Final B3m C0 ran both authorized test files under the shared execution
lock with the deterministic environment. It reported **1003 passed in
39.80 s**. Pyflakes, git diff-check, scoped AST and whitespace checks,
source and test prefix reconstruction and direct boundary fixtures
passed. The AST checks here are restricted to the affected definitions.
The final acceptance AST witnesses belong to B4.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `6e680f222bac33832ce8351029c451371f6c4c8f70b7217318db5992fe4d1879` |
| `tests/test_pca_info_online.py` | `c6e3522f422e63930d267f1acbf8a2695009a1fc43b2d7c85da3e9a08cd93dfc` |
| `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `76c8c81afc6f972c584be0f96d7b7c3ea9673970b5cf735fba40413257fdab9e` |
| `logs/stream-32/lot-B3m-green.pytest.log` | `00eafbacc44ab11234ec3db5dda9ae5ecc1f4094c99b7efb9f2433c4c58ec956` |
| `logs/stream-32/lot-B3m-green.checks.log` | `9bfefecc9ec37da99e4e82d1b41fd8685d269c92d15ace49137060f5e78fad33` |

## Matrix disposition

The 68 ordered rows contain **34 PASS and 34 NOT_RUN**. B3 added PASS
for T23, T24, T26, T30, T31, T32, T40, T43, T63, T64, T65, T66 and T67.
T10, T15, T19, T21, T22, T28, T29, T34, T38, T39, T41, T42 and T49
carry their B3 evidence under NOT_RUN pending their integration,
export or final AST obligations. T34 and T41 retain their partial status.

The diagnostic results are computed offline from caller-paired verified
fixture inputs. Production CLI, worker pool, publications, final exports
and section documentation are B4. Runtime execution, resource profiles,
real panels and campaign evaluation are outside this receipt.
