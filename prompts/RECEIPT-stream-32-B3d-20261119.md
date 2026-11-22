# Stream 32 — B3d receipt

19 November 2026. **B3d ACCEPTED ON DETERMINISTIC FIXTURES** under the B-TDD GO.

`hold_phase` consumes the verified NULL_PLAN size and distinct HOLD_NULL keys
before evaluating the frozen CAL cells. The primary fixture draws five new paths
per application. CAL thresholds are reused and the oracle metadata are role- and
family-specific. The two reference examples include a FULL_K `NULL_FAILED` cell
and a censored HEAD oracle `NULL_INCONCLUSIVE` cell. The partition retains only
first-hit indices and full-H mask bits for each cell. Replay verifies the CP
projection without new paths or scans. A direct poisoned-ALT fixture confirmed the
same frozen NULL_PLAN and HOLD records and scientific bytes.

| Step | Measured result | Pytest log SHA-256 |
| --- | --- | --- |
| RED | 2 expected absent-API failures and 858 passed in 26.77 s | `1aa33cbf6e582b600e3cb9ad86ad441c3f2b971bb390cd9ab2546b2255b4d6f0` |
| GREEN | 860 passed in 23.00 s | `db9e18e7745ded58344c041665a4c6eff18791dcdec585ac9afab4d27e261f2a` |

Pyflakes, git diff check and the append whitespace check were clean. Direct checks
also refused a zero hit index and an out-of-universe mask. Check log SHA-256
`fb7d54477641bbe91fe095315cab36f13531f367fed4efe3bb4a44348f984aae`.

- Source SHA-256 `048d271b5b2f062516beba3b824010603d3f2066452cc6b3dbe302e2df05f9c2`.
- Tests SHA-256 `9c73a06edcf6cae8e14d8b64d4937f2d58923a0d3eb8caeac586b9867a13b85c`.
- Sealed PCA producer SHA-256 `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

T32 passes. Other HOLD slice evidence is recorded without closing the remaining
ALT or B4 obligations. The matrix contains 23 PASS and 45 NOT_RUN.
