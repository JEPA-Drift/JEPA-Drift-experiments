# Stream 32 — B3e receipt

19 November 2026. **B3e ACCEPTED ON DETERMINISTIC FIXTURES** under the B-TDD GO.

`alt_phase` reads the verified HOLD lineage and reuses the same non-oracle CAL
identities and thresholds across four residual families. The family-permutation
witness preserves the same masks and hits for the supplied observations. The
fixture verifies raw return deltas passed unchanged under both arm coordinates,
separate ALT metadata keys, family-free noise keys and oracle-specific q. HEAD
geometry is stored before ALT. Joint information is retained after scans and
never enters selection. The phase supports committed replay without new paths
or scans.

| Step | Measured result | Pytest log SHA-256 |
| --- | --- | --- |
| RED | 2 expected absent-API failures and 860 passed in 28.53 s | `aeeef30e94fb49a90b3fc59f601335891a16a40c3a4f358a45fe1b4c93636e8c` |
| GREEN | 862 passed in 25.11 s | `9c39cbde63c969e1a78f9a86214508a949cb9cee1e11d4d0a53eac951e9b92e1` |

Pyflakes, git diff check and the append whitespace check were clean. Direct fixtures
trapped q reads in a non-oracle-only ALT, checked I_joint after scans, accepted a
descriptive MARKET scope under the frozen Phi check, refused a missing H2 and refused
an unknown scoped family before generation. Checks log SHA-256
`169de810def1736787031fa4fec9b453e3b2743222ddd8ad6a2acab5ac0cb86c`.

- Source SHA-256 `bb05ea7a4a4adc94239a285c35d9835f171195ec46d6465f3f56684f70d4741b`.
- Tests SHA-256 `4c02cdd6825cee02ee493ad8bea6d7caa06a75004879a3eb8feebf7105cb2fd8`.
- Sealed producer SHA-256 `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

T23 and T24 pass. Other ALT slices retain their pending obligations. The matrix
contains 25 PASS and 43 NOT_RUN. Inference and additional diagnostics remain open.
