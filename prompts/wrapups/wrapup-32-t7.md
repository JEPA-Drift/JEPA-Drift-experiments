# Wrapup — Stream 32 Student-t7 closeout

## Context

The written prospective amendment authorized Student-t7 A2 fixtures, followed by separately authorized runtime qualification, Pilot and Full. The campaigns used synthetic `FITTED_LW_T7`, dimensions 32 and 239, fit 0, horizon 250 and `FIT_CONDITIONAL`. The Gaussian §18 decision remains historical. The Git closeout uses the received publications and repository checks. [Amendment](../AMENDMENT-stream-32-t7-20261122.md) · [Gaussian closeout](wrapup-32.md)

## Validated Results

- A2 exercised deterministic native Pilot and Full, independent seals and audit replay, and resumption after publication and partition faults. The two audit pairs returned `PASS`. The receipt records 66 passing witnesses across its verification runs. [A2 receipt](../RECEIPT-stream-32-t7-tech-A2-20261122.md)
- Runtime qualification reached `COMPLETE` under `SMOKE_NO_CLAIMS`. Both cases share realization `43e5ff6c53fde65fa195e92a504614816e4025b48eccca76c4fb7eee6c5c22e1`. Their terminal inventories agree on 96 of 98 files, including all five FAIR exports. Telemetry and resource records differ across invocations. The ledger records 259.339556 measured and 1,162 charged CPU seconds. Both audit pairs returned `PASS`. [Runtime receipt](../RECEIPT-stream-32-t7-runtime-20261124.md)
- Pilot used 200 paths per CAL, HOLD and ALT cell and recorded 39 validated, 47 inconclusive and one failed HOLD cell. The failed non-deployable oracle affects one contrast, marked `NULL_FAILED — NOT_CLAIMABLE` in the audit. Full used 2,000 paths per cell and recorded 28 validated, 59 inconclusive and zero failed HOLD cells. Each publication has 87 CAL cells, 87 HOLD cells, 165 ALT cells, 240 descriptive contrasts, four information–RMST diagnostics and zero confirmatory rows. Both independent audit pairs returned `PASS`. [Pilot receipt](../RECEIPT-stream-32-t7-pilot-20261124.md) · [Full receipt](../RECEIPT-stream-32-t7-full-20261124.md) · [Full analysis](../AUDIT-stream-32-t7-full-20261124.md)

| Identity or artifact | Pilot SHA-256 | Full SHA-256 |
| --- | --- | --- |
| Design | `2ac79300374b99ba1842c2d501c4a1d03ce890c623018ab9cc0f7a9cc20e1ddf` | `03abb171a86076e1eaab777cc5d789d7e556646b09eb3c26c9cfa8f5094b1f96` |
| Realization | `d46eeb91029a69fc29574a322924cd202c3edf71541de8f34876cab7b7d914e2` | `bc986fbd5d508a4d2acecb9c536a83c724690c6b93393be6e047d3720a0d1e35` |
| `aggregates.csv` | `006beba33dfc2fe882619734026fbed2796f635d479bfe47204561cdf6a69cd1` | `e539ecdfd6f0dfd187ee878ce8670d50ed0192310eba993b56eaade38e60964d` |
| `calibration.csv` | `967f6cc1f2b74fa50b21e25ca7c4b46d24df15a1303a7d32c970eaee3272bf08` | `49afc9e9e70ad2066b8861c310f1817a4266873708702166d4e44dfe768a5836` |
| `issues.csv` | `0f2e5ce91fd62f86ecec445a3d102b68ca6271e49ccfeec56cb36203349a5f96` | `73e38d6bb873eb1c0627745faff5a545f9339cfd667ca1b8b89d76cfee876929` |
| `manifest.json` | `9269b97739f145ee38c2dbfc2b1e5c3a88cae5378ac4d648075fc58b2c310dea` | `30afa8dcd5c688fbcead107fc0efe44443892a1bf8aaee9e5137ff3a7345c172` |
| `selections.csv` | `42490b063cfc408161fd78ad04e14443c59f4002e79db882bdbd43ac74d03c8f` | `170f617a2fc0a3a59c057087c995369195cf857500064a908e7e2b8741dcb5db` |
| `summary.md` | `c0b2e65e754c7dda62e041b0d18c041f509454be36e0ebec07d32acb62ae804e` | `b76d33820b8244ff163b419b070bd1ab308e049cb8b161bc163e6c168a0dfda9` |
| `telemetry.json` | `7b4699fe59319e33c6b82125a5f4c2e61e2cfd963ac2554545c96581c26c1327` | `49dc916fed95db62c0f3098c5fa5c19d18a59ee04b99b9e5c61111df1e013b88` |
| `trials_summary.csv` | `5c058c2d503ed28d321fe6de89a3b14f0d643c50e3682509861c091a3682a079` | `abbe301a6bd89af713b2c92630f9ad26f03a0b0271280284702c43da41f203b9` |
| Local `FINAL.json` | `fa3cbb5577219adfa6fec4585ccc822648019b825398b11bd783e03e320b6567` | `72a803323d0574f121390e608ab906fd0b313344b71f31e402dc66ded6658c6c` |
| Local ledger | `d977b6828d129d48ce56c96ae3adbc9a1e18dbfc4cf1cc375f9a7a317132c383` | `15f3ee02189c8f0f9ceb2a58c4803d9994b06bcd900fc902e6e0f7586878773a` |
| Local pre-ALT report | `e6c7bee96e53ef9fbfe68efc3f4161a4fd516934ca8f1dcaabe7a276a672a549` | `eaf6e06cef969d9c993de46c55c00fd6e0daf10a37b00d64fac7a81e5b2d4259` |
| Local ALT report | `363de848c94b6fc616ef5dceb0f476c2195dfa166f9c42502a2c7d25d14e6c5e` | `b3ace2ad5c72928dc9e5fe0c4faabc3df70679739026d0259c7e1b67cdb164c3` |
| Execution intent | `740605cbf72c50b70226f773498a72cfe9e38f273556ab7a57146760c5830f1b` | `9451209da37b0a0337fddff05d3e017c5363a31b3d12831e00e4a4ee13faac71` |

Each campaign manifest lists the five FAIR exports and 40 local partition hashes. Each ledger lists all 98 terminal inventory hashes and links the invocation receipts. The closeout checked the hashes for both manifests and all 196 terminal inventory entries. [Pilot manifest](../../results/pca_info_online/t7-pilot/manifest.json) · [Full manifest](../../results/pca_info_online/t7-full/manifest.json)

| A2 or qualification audit | Pre-ALT SHA-256 | ALT SHA-256 |
| --- | --- | --- |
| A2 Pilot fixture | `f754739a24dcf6a828163d2df4ebd597f83843e6fda7282e985bb669e418129a` | `1c380a5a0b7cb279d6f88ca472c720564946c6f58d8ee4ac16d090fb72f4487d` |
| A2 Full fixture | `3fa5664a357cd0f502d0fb74ea9b33443b71cda5b8806a14d4656579d414389c` | `93a0db86691045c94dfc73e21f10b7bdf5368e002239a99ab5e261bdd60d2d2f` |
| Continuous qualification | `bd9dae0f1ee82163ebac3625be6a74c5db90b37f0a3dc59572373281d8a0836e` | `7983b63895b7bcd11f61eef883202e6029d7815ec2743eba079aa7d20e4b2f41` |
| Resumed qualification | `424bb123df53faea719c7a87e6278ebae5635a9bd7c762ed79aecb232374f0af` | `75807e5122a7a37ee3900c9ec3a1df4cf8b16a07577636fea98f27b063b30e16` |

| Qualification artifact retained locally | Common SHA-256 |
| --- | --- |
| `aggregates.csv` | `404451826738a81ea9960b2a7cf06e3e26fd1652e488d23736d967b647d32bbd` |
| `calibration.csv` | `55d24f15c07ae2d3a258b3e2ae65cb0590dfd2099db12dcdcd202ad7f2110dc6` |
| `issues.csv` | `fdd32ccbe38e0fd58cb8a492b84a67034e83e8ec1a493ebbc0518268e86eb2b5` |
| `selections.csv` | `0b297372e6a53e63a06d5b3c4cf328fb1c0d2985d8c4204ae946f5c21477f42e` |
| `trials_summary.csv` | `da5679e5de6790bd17d4be61dc4340d36ed69b966329702c6a508b2e26003fd6` |
| `manifest.json` | `ef94d43d5c0958f58f88cb2d4cae76c5816903c117cd681f1c5dd0f2aba96b71` |
| `FINAL.json` | `cbff2faa40f8227de39422323b3e7d973a84a025ed5575d68f3dec8578759b15` |
| Shared ledger | `ca9e2ff79df6051edb43e7bc74f9092e289025601a47ef3717a0e9d7ad95a20d` |

| Closeout evidence | SHA-256 |
| --- | --- |
| A2 receipt | `cc36f36cbd1dc640d24a66702213b989e914e84a1d1a687273de23864e558285` |
| Qualification receipt | `537004de03b31d3ae75753f2497166a6167388626cdae72115385ccedf58db7e` |
| Pilot receipt | `b9b5cfc2270a148a429aa98f14868c7b27e062e661924d151b414934d33aa51a` |
| Full receipt | `f933d088472785c51fd9e8e50efd169ec3792bf3693a7cc8da9ed0b2bcebb334` |
| Full analysis | `35bebdf0a80df614568e53508c1500e3f356de69a71c86f155d71be005e63542` |
| `tools/ops/audit_stream32_t7.py` | `6c874cdb58a12787f538503fa42117d61e3582ae29597b9e8f5398115da54021` |
| `tests/test_stream32_t7_audit.py` | `2e21c69ffe99961a5967bd14c7ff64e1f55dc10b127c2194c97384ebec17cb90` |
| `tests/test_stream32_t7_native.py` | `66bcd3cded02a2c2470018603c05708ef65e4c3724fe57d0c9b47bf654e767c9` |
| `tests/test_stream32_t7_launcher.py` | `71fa83990a704f45d46e7949d8f07431c320dcb88c0698590fae7e0cfe2d3e6c` |

## Errors and Dead Ends

The A2 synthetic pass found a historical panel fixture failure when its pytest temporary directory was inside the worktree. The targeted check passed with a separate logical source root. During qualification, recovery from an interrupted admission and a forced post-CAL kill required written reconciliation. The killed invocation was charged the full 902-second reservation. Full T7 completed after four clean resource stops and four written resume decisions. [A2 receipt](../RECEIPT-stream-32-t7-tech-A2-20261122.md) · [Runtime receipt](../RECEIPT-stream-32-t7-runtime-20261124.md) · [Full receipt](../RECEIPT-stream-32-t7-full-20261124.md)

## Current State

The two compact publications contain eight files each. Logs, qualification outputs and bulky staging remain local. The launcher's test module uses the local scripts when present and skips in a checkout without the local launcher directory. The A2 receipt preserves its historical launcher-test snapshot. The frozen scientific producer and simulator SHA-256 values are `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec` and `0d7d45068f85a3dd64f25caeee9e5aa079c61bb8bbf30dc847dea0ba18bc383d`. The Gaussian Pilot and Full manifest SHA-256 values are `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8` and `16f5fdcfca5c08a97d8a6ff01a0cdf807b614b0d2321bf17b0abb0d9d86e0cbf`. The two T7 bootstrap commits have patch equivalents on `main`. [Traceability](../../docs/MAPPING.md) · [Deviations](../../docs/DEVIATIONS.md)

The pre-commit closeout check covered 34 of 34 registered prompts. Under the shared lock, synthetic `make check` passed 22 contract and decoupling tests and 2,374 additional tests, including 91 T7 tests. The two passes recorded 144 deselections and one skip. The synthetic selection uses the local A2 plugin and a pytest temporary directory outside the worktree. The data-backed suite is scheduled on `main` after fast-forward integration.

## Vigilance Points

The T7 readings are descriptive at the frozen fits. The Gaussian working-model information diagnostics retain their proxy labels. Full INFO–PREFIX comparisons each have at least one inconclusive HOLD cell. The Pilot oracle failure stays visible in the audit and the FAIR issues table. [Pilot receipt](../RECEIPT-stream-32-t7-pilot-20261124.md) · [Full analysis](../AUDIT-stream-32-t7-full-20261124.md)

## Recommendations

Cite the compact CSVs with the receipts and audit qualifications. Retain the sealed reports, ledgers and staging locally so their individual hashes remain verifiable.
