# GO addendum — Stream 17 D3 null-control incident

Date: 2026-10-28. This addendum preserves the original GO and its stop-on-FAIL rule. The P4-D D3 null result remains `FAIL`, with 0 alarms in 500 saved draws against its stated `~0.05` target. It must never be reported as a calibrated FPR PASS or used as a calibrated J4 comparator.

The fixed, read-only D0–D2 diagnostic is `/tmp/s17diag/diag.jsonl`, SHA-256 `76e9bf6e23f707d0c2f54da3cf6bcb625c43a8a583ecf573e826788638fe1e3f`. All 18 checked artifacts and the Git diff, status, and HEAD matched their pre-diagnostic snapshots. For both P4-D and P3-D, the 192 overlapping calibration windows have one identical peak, repeated 192 times, and zero exceedances. P4-D's 500 saved starts replay exactly. The even energy stream receives no fresh D6 randomness, so the saved check reuses the windows that determined its threshold. This establishes an invalid in-sample test for out-of-sample FPR; it does not establish the true D3 FPR or a failure of IPCA itself.

## Authorized continuation

- Complete the already approved shared C and IPCA engineering work, K selection, character audit, targeted tests, documentation, wrapup, and local commit 2. Preserve the saved P4-D FAIL and P4-C PASS artifacts. Record this incident and its limits in an English `C-<topic>` entry in `docs/DEVIATIONS.md` and in the Stream 17 results interpretation.
- Keep P4-D's FPR status **uncalibrated**. P3-D's corresponding D6 window diagnostic is also not an out-of-sample FPR estimate. Neither may be treated as a J4 calibrated reference without a later, separately approved control.
- Do not change `H`, `alpha`, `ENERGY_DELTA`, `null_rows`, `N_cal`, thresholds, seeds, data windows, or `null_target` to turn this FAIL into a PASS. Do not rerun the P4-D null CLI or select among new draws. No new null-control execution is authorized by this addendum.
- A future independent null control requires a separate written GO that fixes its data source, independence unit, calibration/evaluation split, sample size, target, uncertainty interval, and verdict rule **before** any result is observed. A synthetic D5 control would certify only its own model, not the real D3 FPR.

This is an engineering continuation only. If another pre-specified scientific gate fails, stop and report it. Run the planned focused tests and `make check`; audit output hashes and Git staging. Commit locally with a Conventional Commit message, explicit paths, and no attribution trailer. Do not fetch, merge, push, touch the Stream 14 worktree, or start another stream.
