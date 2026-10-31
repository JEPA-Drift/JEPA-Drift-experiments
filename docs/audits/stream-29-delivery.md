# Stream 29 delivery acceptance

Date: 2026-10-31. Decision: **ACCEPT for the supported generation path**, subject to the mandatory serialized global check and Git closeout. An agent exit was not used as acceptance.

## Implementation and scope

Mistral Vibe 3.0.4 implemented the accepted plan with `large-4` (`mistral-large-4`), thinking `high`. The final execution export is `logs/pca_drift_orchestration/vibe_audit_fix2/export/export.json`: outcome finished, exit 0; wrapper and CLI processes exited. Codex authored control documents and audits, not application code. No Claude implementation, simulation, real-return evaluation or dependency change occurred in this stream.

The assembler consumes the sealed seven-file `pca_drift_benchmark/2` artifact and exports `pca_drift_tables/1`. Its final API and columns are recorded in `docs/sections/pca_drift_tables.md`. It copies source RMST/FPR and identifiers, preserves blocked real rows with NA measurements, distinguishes empirical calibration frequency, predictive bound and measured holdout FPR, and labels joint covariance information and heuristic costs without an additive or exact-delay claim.

## Fresh verification

- Parent: **85 passed in 79.47s**; measured wall 79.83s, maximum RSS 297140 KiB. Pyflakes passed on the assembler and tests. Logs: `logs/pca_drift_orchestration/audit2-parent-tests.log`.
- A separate read-only reviewer, holding only plan 29, found no remaining functional blocker after checking the three final repairs and the previous 13 findings. Earlier rejected candidates and their exports remain archived locally.
- Parent accepted valid pre-2020 spectrum date metadata, rejected all eight probed missing applicable ALT fields at n=40, and independently checked exact generated lineage key sets: **25888** default, **7932** covariance filter, **116** energy filter. Only four producer-undefined RMST dispersion/interval fields may be NA at n=1; `deff`, `n_eff` and applicable Wilson bounds remain required.
- Nine output files are byte-identical to their separate render. Every declared output, source-input and code hash matches. The complete manifest recipe independently reproduces the tables fingerprint. Default T1/T2/T3 have **180/220/44 rows**, **48/65/58 columns**; T3R has 12 Markdown rows. All 60 blocked-real T2 rows retain identifiers and NA empirical RMST.
- Rendering cost from the final Vibe measurements: **3.06s / 3.08s**, maximum RSS **238296 / 238740 KiB**. These are smoke table renders, not full Monte Carlo costs.
- E2 disk and index SHA-256 both equal `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`; Git reports `i/crlf w/crlf attr/-text`. Historical E3/D8 FAIL remains unchanged. Producer code/config/test and the sealed source artifact remain unchanged.

## Sealed table artifact

Directory: `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`.

- Input manifest SHA-256: `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9`.
- Input run fingerprint: `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.
- Tables fingerprint: `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1`.
- Table manifest SHA-256: `e3f8f448715bc1d6e7195a14e08d1224301b54551b57785449bf8bb8251af74f`.
- The table manifest records all eight other output hashes and all seven input hashes. The formal wrapup retains the full hash inventory.

## Bounded limitation and next phase

The internal `validate_lineage` helper compares equality for the four known tables. A manually injected `UNKNOWN`/`RULE` record can escape this comparison. Supported builders emit only the known literal table names, so supported CLI inputs cannot produce that record. The parent checked global equality on all actual default and filtered outputs. This nonblocking P3 is recorded for future contract hardening; stream 31 remains in user-directed standby.

Global `make check`, AST/no-AI indexing, commit and push remain Codex closeout gates, with no concurrent implementation or scientific process. Their results are recorded in the orchestration checkpoint and terminal Git evidence. After clean integration of 29, the user has authorized a fresh strictly synthetic full at 2000 paths per role, no operational duration ceiling and additional RAM as necessary. Audit full tables before Vibe implements stream 30. The smoke supports no full-run or real-data performance claim.
