# Stream 32 — B3h receipt

19 November 2026. **B3h ACCEPTED ON DETERMINISTIC FIXTURES** under the
B-TDD GO.

`descriptive_contrasts` takes one prepared group. It pairs non-oracle
members with the primary W128 baselines and uses one family bootstrap
matrix for the nominal RMST intervals. The planned oracle contrast
reports its FPR separately under `ORACLE_SEPARATE`. The actual committed
F2 fixture ties this result to the same-family non-deployable CAL
identity and excludes sibling calibrations. The literal pilot fixture is
labelled `PILOT_ONLY`. No pilot campaign was run.

The committed fixture identified a Tango cancellation at complete
discordance. The exact endpoint prerequisite was received separately
before the qualified RED. Prior Tango tests remained green.

| Step | Measured result | Pytest log SHA-256 |
| --- | --- | --- |
| Initial RED | 887 passed, 14 absent-API failures and one Tango endpoint failure in 44.73 s | `87c7431e43f9fe94c79bc5ca610820153bce59af10e4ef258b3bbb7bac339450` |
| Qualified RED | 887 passed and 15 absent-API failures in 40.94 s | `c24d3fd3ef3dd4081872313e77dbeb79cf2519723ee4982eef7f6ef6846782f6` |
| GREEN | 902 passed in 32.74 s | `b089c310a73e59e9cfe22f99947b29700f78fd5f1afe78f576686e55e6fcac05` |

Pyflakes, git diff --check and append whitespace checks passed. Direct
family and oracle-scope checks SHA-256
`efff635de81bcc29fb65ff794101cc7889feff181608ca8dfcc78163b80fcbd3`.
Direct frozen Phi and ALT poisoning checks SHA-256
`d1818c826472f6e01fa38584c272dfc9c5da9e65f6ecbdfa01cc26ef54f51ba8`.

- Source SHA-256 `0fc74f0189aaf8a35ddf2103d72777dc2c9a09b2974df9fa01455ded990e17d4`.
- Tests SHA-256 `32841e82db419ddf917100a64064e1bbdbc9964b5df093375624046299b36864`.
- Sealed producer SHA-256 `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

T26 and T30 pass. T15, T28, T34 and T41 retain pending integration
obligations. Matrix total is 32 PASS and 36 NOT_RUN. Offline diagnostic
fixtures remain in the open B3 scope.
