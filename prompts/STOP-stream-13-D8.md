# STOP — Stream 13 D8 primary reproduction gate

Date: 2026-10-28. Preserve the completed E3 full run, all quick runs, source files, and uncommitted changes. No new E3 run, selective cell rerun, seed change, threshold change, reference change, or commit is authorized under the existing GO.

The pre-specified D8 primary gate uses the first 2,000 trajectories and requires `abs(ARL0_MC/reference - 1) <= 0.05` for every overshoot cell (`prompts/plans/plan-13.md:129-132,335-341`). The completed full run reports `iid/first_order_d1_l3` with `ARL0_MC=1994.0665`, reference `1894`, and relative gap `+0.052833421330517272`: **FAIL**. The other five primary cells pass. The 20,000-trajectory diagnostic (`1964.2627`) and exact iid value (`1962.7934931007508`) are non-blocking analyses and cannot replace the failed primary decision.

The source records are `logs/e3/run.log` and `results/e3/e3_overshoot.csv` (SHA-256 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`). All six E3 output hashes were independently compared with the run log. The secondary J2 calibration check is not a J2 verdict; the E1 Stream 12 decision remains primary.

The plan requires an immediate stop before commit on a D8 FAIL. Until a separate, written scientific decision is made, only read-only audits and a failure report are permitted. Do not modify code or parameters to make this result pass. The worktree and artifacts remain intact.
