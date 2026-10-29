# GO-A — Stream 14, isolated Torch environment and synthetic CA-T-JEPA core

This decision authorizes only P0, P1 and 2A of the reviewed Stream 14 plan. Phase 2B, real D3 data, shared source files, integration, fetch, merge, push, and streams 16/22 remain blocked. Preserve the Stream 17 worktree and all user files.

## Pre-implementation corrections

Before implementation, save the reviewed plan as `prompts/plans/plan-14.md` with these corrections:

1. U5: estimate four grouping medians on the internal pretrain training segment only; freeze a dictionary of 16 binary codes plus `nochar`, the local `SeedSequence` key scheme, tie rules, handling of empty/missing groups, and the reproducible selection/fallback that targets 30–50% masked assets. Save this state in the checkpoint. The synthetic tests must cover empty and oversized groups.
2. U9: `make j1` can change three tracked outputs: `results/e2/e2_cells.csv`, `results/e2/e2_j1_summary.txt`, and `logs/e2/run.log`. Snapshot their state before J1; verify the native CRLF reference and SHA-256, then restore only generated changes in these three files. Do not require an empty Git status while the new lock and implementation files are present.
3. U12: if any exact archive or source metadata is missing, stop; do not substitute a build, channel, or source. U13: use only the verified `solveB.json` with SHA-256 `df071043e438f5ef38e7bafdc104372db800c05eed8961c76f5fead05ef85ef9`. U14 remains for GO-B; no real data may be read under GO-A.

The v2 directive is `prompts/streams/01_STREAM_14_REWRITE_BOTTLENECK.md` in the main checkout, SHA-256 `1b5f2f8e92ba131f9e2845687e82a815b0c18674b85766af07662e008a9362c3`. Do not alter that source. The user's earlier MCP instruction requires explicit reconnection and a successful call to both graphify and jcodemunch before implementation.

## Authorized work and gates

- Create and independently verify an `@EXPLICIT` conda-forge lock with exactly 65 URL and SHA-256 entries from the exact locally cached solve and archives **before** installing `.venv/torch-cf`. Require the pinned `pytorch=2.14.1=cpu_generic*` build and the validated runtime builds. Install only from that lock; no package substitution.
- Access Torch from the project's `.venv` through the isolated `PYTHONPATH` shim. Run `make check` with all four real Torch guards and no skips, then `make j1` and verify SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` with native CRLF. Restore only the three expected J1 outputs after verification. Place the parent `.pth` only after these checks and after no other stream uses `.venv`; repeat the checks without the shim. If other streams still use `.venv`, leave `.pth` pending without polling them.
- Implement 2A with synthetic data only: a native context bottleneck feeding the predictor, visible-only context statistics, EMA target training and frozen context extraction, odd/even parity, deterministic local PRNGs, and a constant-predictor baseline for the no-residual-predictability control. Write RED tests before the relevant code. Keep the main model at or below one million parameters and verify deterministic CPU smoke outputs.
- Do not touch `extract.py`, `test_contracts.py`, `interface_Z.md`, shared loaders, `DEVIATIONS.md`, `CLAUDE.md`, `.gitignore`, or any real D3 data under this GO. Do not treat the Stream 17 P4-D null result as a calibrated PASS. Stop on any test or scientific failure without changing parameters to force convergence.

After the authorized checks, report exact commands, artifact hashes, files changed, and pending gates. A local conventional commit C1 is permitted only when its planned checks pass; stage paths explicitly and omit attribution trailers. A separate GO-B is required before any shared-file or real-data work.
