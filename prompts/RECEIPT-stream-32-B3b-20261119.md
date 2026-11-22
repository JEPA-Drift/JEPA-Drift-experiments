# Stream 32 — B3b receipt

19 November 2026. **B3b ACCEPTED ON DETERMINISTIC FIXTURES** under the B-TDD GO.

`cal_phase` consumes verified SETUP and DEV, shares CAL_NULL observations within each
setup and application, and writes the finite maximum statistic for each effective cell.
The calibration table links a family-free non-oracle or a family-specific oracle identity
to its maxima and sealed GE threshold. Oracle rows carry
`NON_DEPLOYABLE_ORACLE_CALIBRATION`. The common-prior S2 alias reuses its primary cell.
The two gamma variants have their own cells. The committed record reloads without
new generation or calibration and a corrupted payload is refused.

| Step | Measured result | Pytest log SHA-256 |
| --- | --- | --- |
| RED | 2 expected absent-API failures and 854 passed in 24.44 s | `6e4c758556a34f8edb3b56c1092fa0e3fb2c84340ad7989cd175c0366835b29f` |
| GREEN | 856 passed in 21.09 s | `eb866361b855df15b603989d5b59f78bdd91c578136b27042bb0c0f0e0d97472` |

Pyflakes and git diff check were clean. A direct check verified the source append
whitespace and SHA, refusal of a missing oracle payload, and refusal at n=18 before
any CAL producer or scientific write. Check log SHA-256
`eefd47034bc69d23fb6b94dbc269276f80df4d5b75c8c793a2951f3f6264e60f`.

- Source SHA-256 `14e6300a0faaad636d884fa1d3d51668c651efedf9f60392726760889a15363c`.
- Tests SHA-256 `a060e2f48683c9334857353a653fb15b2af8960293266afffa5be3eea4906e45`.
- Sealed PCA producer SHA-256 `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

The terminal author capture came from the systemd user retry recorded in the GREEN review.
T10, T15, T19, T24, T26, T34 and T41 remain NOT_RUN with additional slice evidence.
The matrix retains 22 PASS and 46 NOT_RUN. Subsequent null evaluation, ALT and inference
remain open in B3.
