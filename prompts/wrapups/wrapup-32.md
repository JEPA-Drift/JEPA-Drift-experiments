# Wrapup — Stream 32 PCA-INFO-ONLINE Gaussian closeout

## Context

The fixture lots A and B, Lot C runtime checks, Gaussian Pilot, and separately authorized Full Gaussian campaign are complete. The Full campaign and its independent audit closed on 22 November 2026. This Git closeout records the received results and their scope. [Plan](../plans/plan-32.md) · [Amendment](../plans/plan-32-v2.1-amendment.md) · [Contract matrix](../MATRIX-stream-32-T1-T68-20261114.md)

## Validated Results

Historical counts and SHA-256 values below identify the corresponding received snapshots.

| Lot | Received evidence | Receipt SHA-256 | Runner SHA-256 at receipt |
| --- | --- | --- | --- |
| [B1n](../RECEIPT-stream-32-B1n-20261115.md) | 241 fixture cases passed and 18/68 matrix entries passed in the final B1 tranche. B1 integration was received with B4. | `be1fb118989d69d6f5da6fdca4cf06bca0f97d47031ac1c6cceaf9b33ca9da4d` | `a1c5b5b7304aa0247a160a50cfe71a830da3b79c13f33ff50f7ba4f408d4e364` |
| [B2](../RECEIPT-stream-32-B2-20261118.md) | 840 fixture cases passed, 21/68 matrix PASS. | `1ccf73349750f74f84919d18b96fafe10d389927cac84417aee7ad3e1f49b584` | `936afa0c13b59bb59d63591b5309c1b582a9b2594668b897a63e906021cb387d` |
| [B3](../RECEIPT-stream-32-B3-20261119.md) | 1,003 C0 cases passed, 34/68 matrix PASS. | `a501ce0f74f2033ff54fb9215c3fe217122020a00f3339953982c7f39f6560f1` | `6e680f222bac33832ce8351029c451371f6c4c8f70b7217318db5992fe4d1879` |
| [B4](../RECEIPT-stream-32-B4-20261120.md) | 68/68 matrix PASS, 34/34 registered prompts, 21 synthetic contract and decoupling cases and 1,063 PCA-INFO-ONLINE and prompt cases passed. | `fb8ebbe429765b8cc72885e99bf59977cf7d460406347293b2c61d3fcc510136` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |
| [C](../RECEIPT-stream-32-C-20261120.md) | C1 publication, C2 recovery at four cuts, C3 jobs 1/8 equality and C4 profiling at jobs 1/4/8/12 passed. C4 measured wall times of 300.54, 326.42, 326.67 and 326.67 s. | `ecef582b20dcd133db40e630b9fecd4be09928ce17cd0ac555f85a155d939e27` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |

Lot C verified five matching CSV hashes across C1–C3 for realization `d2fc7c1d8ff3f8471a639b557e38d1c0067018975f2fe73ebaee47ef7e99fd71`. All four C4 runs matched within realization `c286d3c584c38a00647c9a5ea286e0881635cde040a51cd3d1252c0446386246`. The C1–C4 audit SHA-256 values are, in order, `26c29abe8b06410fbcf038655449ff68bc857d52588f6c1adbdf377ab096dca3`, `9fe56526f0467597c0108f42e7698df828f30bb86d105c71fe2f6e731ffbf4b0`, `bba6f4ce47baea4d5953b0e0e84ff55b49c2238b920485e9e36de8faed634acd` and `023787c64848b287b1cfd4800827bd9e607cae0391164a754149985bf0c05a5f`.

- **Pilot.** One worker, 76 local partitions, and 200 CAL, HOLD and per-family ALT paths per planned cell. Among 99 non-oracle HOLD cells, 21 were `NULL_VALIDATED`, 74 `NULL_INCONCLUSIVE` and four `NULL_FAILED`. The failed cells alarmed on 19, 19, 24 and 26 of 200 paths. The 520 contrasts retain `PILOT_ONLY`. [Pilot receipt](../RECEIPT-stream-32-pilot-gaussian-20261120.md) · [Pilot null audit](../AUDIT-stream-32-pilot-null-20261120.md)
- **Full.** Four Gaussian setups at fit 0, 104 local partitions, ten invocations and 21,294 charged CPU-s. The three primary policies used 10,000 CAL and 20,000 HOLD paths each. Remaining cells used 2,000 CAL and HOLD paths. The audit recorded no `NULL_FAILED` cells and 106 `NULL_INCONCLUSIVE` cells across oracle and non-oracle policies. INFO attained 5.845% FPR on the primary HOLD cohort and remained individually `NULL_INCONCLUSIVE` with a 6.1251% upper bound. PREFIX and FULL_K attained 5.675% and 5.375%. [Full receipt](../RECEIPT-stream-32-full-gaussian-20261120.md) · [Full audit](../AUDIT-stream-32-full-gaussian-20261122.md)
- **Confirmatory comparisons.** H1 F2 INFO/PREFIX RMST was 86.570/91.249 days, with a 4.1163-day lower gain bound. H2 HEAD INFO/PREFIX RMST was 78.353/83.670 days, with a −13.2686-day upper bound on INFO minus 1.10 × PREFIX. H3 F2 INFO/FULL_K RMST was 86.570/87.579 days, with a 0.5250-day lower gain bound. Both Tango intervals fit inside the ±1 percentage-point margin. H1–H3 carry `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR`. [Full audit](../AUDIT-stream-32-full-gaussian-20261122.md)

| Identity or artifact | Gaussian Pilot SHA-256 | Gaussian Full SHA-256 |
| --- | --- | --- |
| Design | `750443a8413d477e0350c66061eed0c25784b9857cc7d3a6aa7ec2f62ca292e9` | `8a4af3ecd7864f167ac32b82f0751547dc68b8a4bf24cec0f6c7fefbb19895d4` |
| Realization | `ede212c81c5cd7f98475f271ae56499e47af1d03a4132bd4f3ae715c427c672d` | `d574db30705b7257567131dd5fdf3c26c4308b4de32f7a5382b34b853457646a` |
| `manifest.json` | `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8` | `16f5fdcfca5c08a97d8a6ff01a0cdf807b614b0d2321bf17b0abb0d9d86e0cbf` |
| Local `FINAL.json` | `178c80372d74ecab5bce39c425d14894a7e07a2ec9d0300fa2b3b5422838dc4c` | `d9a0c88bc845f589e5e7318dbb63e338b03ef119bd8036f591930c711a7dff4a` |
| `aggregates.csv` | `0b3f300e6c13af6392593479fcdfbb1d161c82d7bceb8ddc52f03af595447332` | `dac28abbe5434e6fcff410ebd39667e57afd977c8bcb32223e8a4cea8d0b6293` |
| `calibration.csv` | `fbe32e237508983425563a6d90d3ee5cad75ff1f10176cf980106cea2e6c1624` | `18ae7a421e8e66a846171935f39aa0f6f4eac2be7c17075a670c1bb6f7d69021` |
| `issues.csv` | `e953a3b2e05b50606cf88ccec64990cbb019f6e303759a0fc6b657c90fb257c6` | `4f5fd3d91b7fca4a263cf02db989a495da5d5a2f0ee4037acf0e8a542fecdcb9` |
| `selections.csv` | `c8d868123cc3eeef751a703cfdaa7acd747327070eedd910507543e9e9b4fc7c` | `19908ef428122e2c3cfbea0360ffc220fed6f718c6057c8396104b43a2fb4ac0` |
| `trials_summary.csv` | `65cdd4aa8a91227cf7bbab7b7c0212faeae2834638903937f7db0b098434c5f3` | `75ffa6713e618bee24934d5082a14188f54f6e625418184c493a38065d4129f1` |
| Campaign receipt | `57cd2c914a8d479c37e88d7729f54e7c976ba32932cf36f73b8ddf2b7400747b` | `36ec7a43b85928b276e9965441e0888c2a6f327ac7fa5675e497dc0ce65eb7b8` |

The Full audit Markdown SHA-256 is `1fe07c7562ce1d190787f78a6d43d6aee6148a40a68ea8c27fc26fe8bd72af13`. Both independent passes returned `PASS` with zero discrepancies. The sealed pre-ALT and ALT report hashes are `0a92180f4831f63db177bf3b274c8983755ded98359929eaebdfa40875754721` and `7ef843ae2a3b690ac9b1f84886998df075fac5d02f7e3b477f0fb4b09aba5588`. The separate Pilot null-audit JSON hash is `b61bc5ce727ddbbba51e02082bff05316f794c692deec9cc8a91c0481b9ec6f0`.

## Errors and Dead Ends

The Pilot failed the §18 null gate. Its four original failures stand and T7 remains closed. C4 required a separate authorization for the 12-worker profile. Nine Full invocations ended at clean resource checkpoints and resumed from verified staging. The tenth published the complete campaign. [Pilot null audit](../AUDIT-stream-32-pilot-null-20261120.md) · [Lot C receipt](../RECEIPT-stream-32-C-20261120.md) · [Full receipt](../RECEIPT-stream-32-full-gaussian-20261120.md)

The first closeout `make check` passed 37 contract and decoupling tests. Its second pass gave 2,412 passed, six skipped and two failures. `test_reconstruction_from_cache` and `test_d3_239_selection` both reported that `data/raw/d3_yf/_download_stats.csv` was missing in the stream worktree. The existing raw D3 cache is available in the main worktree.

## Current State

The delivered runner SHA-256 is `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec`. The sealed benchmark SHA-256 is `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`. This closeout ran repository checks only. The compact Pilot and Full publications are retained byte for byte. Logs, staging payloads and temporary runs stay local. The main worktree was clean and the shared lock was free at entry. Local machine paths were removed from the published copies of the Lot C GO, Full qualification GO and R3–R5 instructions. The original documents are archived locally. The two original GO document hashes are `e3590c79e27bfa028e66072e16b262daa350b922b81eaba561059e27d183b0b6` and `eccbb17c9d1c948c4c1252f24d97d651c0a69e7b2863cf76965c969a011f9395`, respectively. [Traceability](../../docs/MAPPING.md) · [Deviations](../../docs/DEVIATIONS.md)

## Vigilance Points

The Full inference is conditional on the frozen Gaussian fit. Tango and the paired percentile bootstrap carry their asymptotic qualifications. The individual INFO HOLD status and the paired FPR equivalence answer different questions. The 520 Full descriptive contrasts retain `DESCRIPTIVE_NOMINAL`. The Pilot gate and its four failures remain part of the historical record. [Full audit](../AUDIT-stream-32-full-gaussian-20261122.md)

## Recommendations

Cite the Full audit and compact FAIR outputs for H1–H3. Retain the sealed audits and staging locally for provenance. Keep T7 closed under the recorded §18 decision.
