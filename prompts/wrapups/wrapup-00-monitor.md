# Stream 00-monitor — operational handover

## Context

The researcher authorized versioning revised E4 and deploying a deterministic host inspection every 30 minutes. Documentary and initial code phases are pushed. A subsequent execution order requires rootless reboot persistence; this checkpoint records the user-cron migration and minimal-environment launcher fix before their commit.

## Validated Results

- Revised bootstrap read and accepted unchanged. SHA-256: fac0da4eebe3ce861653fcdc634d9f04e53eacb34896872e9945f39495673689.
- The bootstrap was untracked, so the requested unstaged diff was empty. Documentary commit 4dfbe2a71b1d3e7bf5dbcc93755b900c01611d07 explicitly added it with the requested message and was pushed to main.
- Documentary pre-commit verification: 37 passed, then 730 passed in 496.06 seconds; no skipped test reported. Prompt check: 33/33.
- Harness TDD and regression checks: 23 passed; pyflakes and shell syntax checks passed. Independent review found seven concrete issues; each was corrected with regression evidence and the final bounded recheck reported no remaining blocker.
- Shell entry SHA-256 after the PATH fix: c29d3d39f42b8c81bb74ae8af0c13ed2a03384b57782d02a0efd2b30ac901837.
- Python inspector SHA-256: 7e4c19fe4278f9ab3974ff472587733336d9c738ace0e469532122c8b571ce0a.
- Test file SHA-256 after the cron regression witness: 62f990753cd4a15008fc5a21dcc456f138fc74950a3952f0055aba95a1c4e670.
- Option B deployed at 2026-11-07 00:31:03 UTC: detached bash PID 34317, PPID 1, SID 34317, child PID 34337 running sleep 1800. Its first inspection completed successfully. The old 20-minute user timer is disabled and inactive; cron was not used.
- Initial daemon output SHA-256 at the checkpoint: 7f061a015c6b781be03913b27db91d7404d3fba69ef7185fc7678f92ee09298f. The next daemon cycle appends to this ignored log.
- Local ignored registry SHA-256: 1950ae4bb899d8447e0e0374953d78b67ad46a84f8f5eb5902f0738fc08c2af3.
- Initial code commit 21aea53463cfd461532b3b47802fb20fe83fee01 passed 790 tests (37 + 753) and is pushed.
- Persistence correction: user crontab read/write succeeded; crond.service is active and enabled. Exactly one */30 entry calls the repository launcher and appends to logs/cron_monitor.log. No administrator operation or bashrc change was performed.
- The detached daemon 34317 and its sleep child 34337 were stopped after a successful clean-environment reception; the daemon lock is released and the stale PID file removed. This supersedes the historical Option B deployment above.
- Minimal-environment RED reproduced missing git. The launcher now prepends its project .venv and resolved base interpreter bin directory. GREEN: 24 targeted tests passed; pyflakes and bash syntax passed. A real env -i reception reports both workers REVIEW_READY. The new full hook remains pending at this checkpoint.
- J1 disk and index baseline SHA-256: e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823.
- E3/D8 baseline SHA-256: 1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3. Its historical failure is unchanged.
- The code commit's mandatory full verification is performed by the pre-commit hook; its outcome is not claimed in advance.
- End-of-lot reindex script exited 0: AST-only Graphify update completed; jCodeMunch indexed 2000 of 15166 discovered files and reported its existing file cap (13166 omitted). This is partial index coverage, not a full-index claim. No paid LLM operation or index exploration was performed.

## Errors and Dead Ends

The old snapshot was not an intervention channel. The first inspector incorrectly treated the native Cooked completion footer as idle; the observed fixture now reports REVIEW_READY. Review also corrected stale screen precedence, unapproved pane-directory traversal, per-session failure isolation, invalid cache handling, Git-only activity, silent scan errors and process-prefix false positives. A filesystem timestamp fixture was made explicit rather than assuming wall-clock resolution. The initial scheduler check used cron.service instead of this host's crond.service; the latter was active and enabled. A real clean-environment check then exposed the missing host-tool PATH, which was fixed at the shared shell entry rather than at individual subprocess calls.

## Current State

The executable shell entry calls the pinned .venv Python with the deterministic environment and a nonblocking flock. Its stdlib inspector captures tmux -S -80 and process identities, validates declared sessions and approved Git worktree roots, and records terminal and disk/Git activity separately. Data, environment and cache trees and symlinks are not traversed. Git activity includes bounded metadata for index, HEAD, fetches and refs.

The live registry declares 21-dpi and 21-appendix as required, and historical jepa-s31 as not expected. Discovery also observes jepa-* panes. At initialization both current workers are REVIEW_READY, with unchanged Claude PIDs 5301/5323 and Opus 5.5 Max launch arguments; jepa-s31 is ABSENT_NOT_EXPECTED. No success or stream closure is inferred. Their deliverables still require the normal audit and integration workflow.

Reports append to logs/claude_surveillance.log; pending excerpts append to logs/NEEDS_CODEX_REVIEW; observation state and the local registry are ignored. The persistent flag is the authorized intervention channel; the harness sends no keystroke, model request or implementation GO. One target failure produces MONITOR_ERROR without hiding other targets. Stagnation requires both clocks to exceed 1800 seconds; the first terminal observation initializes its baseline.

Initial source was developed in a clean, previously closed owned worktree while main ran the documentary hook, then copied byte-identically to main and pushed in 21aea53. No foreign worker file changed. The current PATH correction is an authorized operational fix on main; its full check, commit and push remain pending at this checkpoint. The two unrelated user-owned untracked prompts are excluded.

## Vigilance Points

Never infer successful completion from an absent session. Screen heuristics require human review; expected test tracebacks during active TDD must not be called process crashes. Disk/Git inactivity and terminal inactivity are distinct observations. Shared Git metadata activity can belong to another checkout. Pending alerts are not cleared merely because a later snapshot is active. Retire an expected session in the local registry only after its audited closure.

## Recommendations

Complete the mandatory full check, anonymous fix commit and push. Verify crontab -l, crond.service active/enabled, and an actual scheduled report in logs/cron_monitor.log. Do not restart the retired daemon or add a bashrc fallback while cron works. Acknowledge or archive NEEDS_CODEX_REVIEW only after the actual stream audits. Preserve every scientific exclusion and both pending stream reviews. Any index-cap remediation is a separate scoped decision; do not silently alter shared indexing configuration.
