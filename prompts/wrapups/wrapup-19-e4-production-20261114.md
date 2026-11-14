# Wrapup — stream 19-e4-production-20261114 (E4 production, full campaign and documentary closeout)

Handover timestamp: 2026-11-14T00:56:42Z (UTC, evaluated by `date -u` at the start of the wrap-up).

## Context

- Lot: stream 19, experiment E4 "fixed information and an ex ante spectral dictionary". It covers production engineering (runner, tests, host driver), a cost-only technical pilot, activation, the full scientific campaign, publication, the portable audit, the final report and MAPPING.
- Branch `stream-19-e4-production-20261112` in its own worktree, base `b18d8e5b01706bcb3dea8268c93fc0b9c361e441`. No commit of this lot exists yet.
- Roles: Claude Code (this worker) wrote the runner, tests and driver under TDD and delivered three IMPLEMENTATION_READY passes. Codex ran the receptions, `make check`, the pilots, receipts, activation, campaign and publication audit, wrote the final report and MAPPING, and owns staging, commit and publication. The worker's documentary-closeout mission was cancelled before any repository write; Codex finalized the report with the worker's AWK appendices.
- Question (protocol §2 and §12): how restricted monitoring time changes over N ∈ {8, 16, 32, 64, 128, 239, 500} when the Gaussian information of an isotropic residual drift is fixed (ln(H/α)/I* = H/40). The ex ante SPEC-full dictionary is compared with the ORACLE references O-dir and O-score1. This is not historical per-asset-amplitude E4 and not a learned non-oracle selection study.
- Constraints held throughout: no pilot, `make check`, activation, campaign, Git or reindex by the worker; tests under the shared lock with `.venv/bin/python`, single-thread deterministic variables and the torch shim; unique never-overwritten measurement directories; RED before GREEN; at most three repairs per defect; no private, real-return, J4/FROZEN or 2020+ data; an unknown cost is never zero. Language: French for user communication, plans, GO files and DEVIATIONS entries; English for code, audits and wrapups.

Authority and decision chain:

| Document | Path | SHA-256 |
|---|---|---|
| Protocol (§12 governs) | `docs/audits/stream_19_protocol_proposal_20261112.md` | `cd786a02d5d6407ccf9a88ba91cacce50c7dcc0f45655868bb32643c577ec657` |
| Researcher decision: GO 1 production engineering, GO 2 conditional full run | `prompts/GO-stream-19-e4-full-20261112.md` | `19d2697700bc9a0af5d98c9bd7c901129450aed385487582ef67c3f17e094746` |
| Codex technical GO, production plan | `prompts/GO-stream-19-e4-production-20261112.md` | `d9b367d2bec34cb2046e95edac0c2a5390bb708972af44f0e8711271dfdc17a1` |
| NO-GO of native plan v0 | `prompts/NO-GO-stream-19-e4-production-20261112-v0.md` | `287a506a428ce13ec1f1b2e877c51a60a191168a6eb6a85a3a3b252fadb22764` |
| Canonical plan (frozen) | `prompts/plans/plan-19-e4-production-20261112.md` | `22c71798b0bfd7b9cb396f30695ce991819a65c9983bc9ad2190798db2de6504` |
| NO-GO reception of the first delivery (R1–R7) | `prompts/NO-GO-stream-19-e4-production-reception-20261113.md` | `232bd54672e198d59e285d13a5203db32855680672f2992131fc5376eb950bde` |
| Corrective annex (R1–R7) | `prompts/plans/plan-19-e4-production-corrections-20261113.md` | `27d8c40d17526a03df0a14ec406cb5252242380f74ef2774d798f3086002f5ac` |
| Orchestration parallelism GO | `prompts/GO-orchestration-parallelism-20261113.md` | `15ca363c0eb8c03abe78044d717a56ca31b36606359bff751a5d5db1b023820c` |
| Residual GO (four corrections) | `prompts/GO-stream-19-e4-production-residuals-20261113.md` | `b4f0fcc1da9f47865ed38b5525444b366fd577e732a0209d5c992a2d30f54341` |
| Technical pilot GO | `prompts/GO-stream-19-e4-technical-pilot-20261113.md` | `ed810720f1fbbdd3d40f5dae2548c221dc9ddc5ddfba7f0d94459d28c1c3ee20` |
| Historical QA access request | `prompts/REQUEST-legacy-global-check-access-20261113.md` | `0af469995961deea66cd2d487e073617c5144a8143fd3ddeb82a0e5146ba7c53` |
| Historical QA exception GO (distinct) | `prompts/GO-legacy-global-check-access-20261113.md` | `5c81eb915837b3e2976840057a202b3045e3ce860711e4c602293d6e4aecde0e` |
| Disk STOP (historical) | `prompts/STOP-stream-19-e4-disk-20261113.md` | `630400feecefa833e4dedc353d61b4b2c9a44afde06a0366870165e77525b669` |
| Activation GO | `prompts/GO-stream-19-e4-activation-20261113.md` | `b8fde8985cc7863d82a9f29a8c36bdd78e86bd03488d5212ee104f4821701ca3` |
| Closeout accounting STOP (historical) | `prompts/STOP-stream-19-e4-closeout-accounting-20261114.md` | `d1156e360ff426eeda177ae86d6fc50261d7eddaa7a160c5d340b7d68dd5a69f` |
| Researcher finalization GO without cap certificate | `prompts/GO-stream-19-e4-finalization-accounting-reserve-20261114.md` | `1f5edab746e526aaf2b9543eace6947f0172750f1d968f46443e361822a5f5c7` |
| Wave 23/27 GO (after E4) | `prompts/GO-wave-23-27-after-e4-20261112.md` | `1e6ef745bf4821a1831930a7c623142afcc82f633459521534007468ddba4b4a` |

The researcher wrote "autorisation de finalisation E4 sans certificat du plafond": closure is authorized with the accounting reserve open.

## Validated Results

Engineering and tests, all run before the campaign; none was rerun at closeout:
- Worker deliveries: first lot W0001–W0017 (140 tests); corrective lot W0018–W0032 (148 tests); residual pass W0033–W0038. Final W0036 `pytest tests/test_e4_production.py tests/test_e4_alignment.py`: 152 passed (51 production, 101 prototype), JUnit `241176ee30aa62bf969dc952b5101051e50192f61a1cb71129b91cf83eb4123b`, `e4_session_id` `6d1acbd629975285acc7df37cb3d02e5daf5f0b7339473af78d02757ef6066af`. pyflakes and `bash -n` were clean.
- Codex receptions:
  - R0005: 148 PASS.
  - R0006: three RED witnesses, 6.03 CPU s.
  - R0007: 155 PASS (152 official E4 tests and 3 former RED witnesses); CPU 74.21 s, RSS 220,492 KiB.
  - R0008: failed collection, 42.98 CPU s, counted.
  - R0009 `make check`: 37 contract and 1,308 other tests passed, only 5 D4-availability skips, torch guards and PCA/G1 executed; CPU 617.21 s, RSS 3,838,968 KiB, 592.76 s.

Technical pilot (cost only; no detection result inspected or used):
- P1: nine real-kernel cost calls of 40 replicates (Gaussian N8, Gaussian N500 and t7 N500, each in the calibration, holdout and alternative roles). Selected geometry: 250 replicates per block.
- P2: 354 COST_FIXTURE partitions at full counts.
  - A0000143 returned rc 7 on purpose before commit (temporary left, no final); A0000144 recomputed it.
  - The resume reached code 10 and verification passed; three replays were SKIPPED_COMPLETE with unchanged bytes.
  - Fixture publication and portable audit: 560 blocks, 42 calibrations, 86 files, activation false.
- Conditional forecast FULL_GRID: 57,178.3295905 CPU s, or 57,287.7895905 with the tail up to A0000389.

Activation and campaign:
- A0000390 `--phase activate --mode full` wrote `logs/stream_19_e4_production/activation-full-20261113.json` (`e3edb7c8f71eabd55cf24d00f912186f1b86acaccf40dbe55698c96e34963e0c`). Disk was 26,862,305,280 B free for a projected footprint of 439,066,266 B plus a 1,073,741,824 B reserve.
- Service `jepa-e4-full-20261113.service` (transient user unit, wrapper `logs/stream_19_e4_production/run_full_20261113.sh`): started 2026-11-13T14:59:28Z, exit 0 at 2026-11-14T00:02:44Z, 32,596 s wall.
- Attempt sequence:
  - A0000391 plan (K = 354, block 250); A0000392 scalar_cal; A0000393–A0000406 the 14 fits; A0000407–A0000518 the 112 calibration-maximum blocks; A0000519 threshold barrier; A0000520–A0000743 the 224 trial blocks; A0000744 merge; A0000745 analysis.
  - A0000746 `next` returned 10 (DONE, 354 partitions, no leftover); A0000747 verify; A0000748 publish; A0000749 verify-publication; A0000750 accounting receipt.
  - Exit codes A0000391–A0000750: 359 × 0 and one 10; no retry and no failure.
- Completeness:
  - 354 partitions; 560 lineage blocks (224 trials, 112 calibration_maxima, 112 diagnostics, 112 diagnostics_axes); 42 recalibrations (3 dictionaries × 14 cells) recomputed by the portable audit.
  - 91 declared files with verified SHA-256 (92 physical files with `PUBLISHED.json`).
  - Rows: 672,000 trials, 84,000 calibration maxima, 28,000 diagnostics, 3,948,000 J_k axes; `holdout_fpr` 168; cells 84 per reading; contrasts 6 per reading; warnings 0.
  - Declared payload 59,901,450 B; largest file 13,651,324 B.
  - Codex's independent scientific and artifact review established no material anomaly.

Scientific results (synthetic only; conditional on the realized fits and calibrations; no outer fit resampling):
- 14/14 fits OK, with no EIGENVALUE_TIE_UNRESOLVED; 84/84 method-calibration records OK (predictive rank r = 99 of n_cal = 2,000). These reuse one shared scalar calibration and 42 dictionary-cell calibrations, not 84 independent calibrations. No fallback and no post hoc change.
- Cell construction: RMST_H is the mean of min(T, H). Its interval is NORMAL_DEFF1 (n = 2,000, deff = 1, endpoints not clipped to [1, H]). Detection and holdout FPR use pointwise Wilson 95 % intervals.
- Contrast construction: OLS slope on log N of log-RMST ratios over the whole grid, with a 95 % percentile interval from 2,000 paired bootstrap draws (common index matrix `0cf0285bad70251a457cb83cc8b69c485677cfadc69e78a798861debba38ed30`). Delta = Delta_1 + Delta_2 is a descriptive accounting identity of the point estimates.
- All twelve contrasts are NOT_IDENTIFIED (reason WILSON_DETECTION_BELOW_QUALIFICATION). Delta carries the label NOT_IDENTIFIED; Delta_1 and Delta_2 carry DESCRIPTIVE. The estimates below are descriptive only:

| Reading | Background | Delta [paired 95 %] | Delta_1 [paired 95 %] | Delta_2 [paired 95 %] |
|---|---|---|---|---|
| predictive_rank | gaussian | 0.631038 [0.625647, 0.636759] | 0.624497 [0.617347, 0.631926] | 0.006541 [0.000628, 0.012374] |
| predictive_rank | t7 | 0.650827 [0.645512, 0.656136] | 0.640240 [0.632957, 0.647139] | 0.010588 [0.004597, 0.017092] |
| anytime_valid_horizon | gaussian | 0.591621 [0.586736, 0.596564] | 0.581049 [0.575201, 0.587014] | 0.010572 [0.006763, 0.014527] |
| anytime_valid_horizon | t7 | 0.634316 [0.629900, 0.638679] | 0.621397 [0.615818, 0.627023] | 0.012919 [0.009076, 0.016762] |

- Large-N censoring, SPEC-full detection rates at N = 239 and N = 500: predictive gaussian 0.8815 and 0.3480; predictive t7 0.9885 and 0.5280; anytime gaussian 0.3215 and 0.0365; anytime t7 0.6175 and 0.0820.
- O-dir detects all 2,000 alternatives everywhere. Its RMST stays within 68.75–70.23 (predictive gaussian), 59.86–60.87 (predictive t7), 101.53–103.73 (anytime gaussian) and 88.00–88.97 (anytime t7). Neither WARN_ODIR_SLOPE nor WARN_EW_DETECTION was raised.
- Holdout FPR:
  - Predictive reading: 62/84 point FPRs above α and 14 FPR_ABOVE_NOMINAL flags (EW 2, O-dir 6, O-score1 5, SPEC-prefix8 1). The non-oracle flags are EW at N16 in both backgrounds and SPEC-prefix8 for t7 at N500.
  - Anytime reading: point FPRs between 0 and 0.0035, no flag.
  - `fpr_comparability`: COMMON_NOMINAL_ALPHA_ONLY for the six predictive contrasts; COMPARABLE_FPR (±0.01 paired margin) for the six anytime contrasts.

Accounting:
- MEASURED: terminal receipt cutoff A0000749, 34,995.28 CPU s, plus A0000750, 1.43 CPU s, gives 34,996.71 CPU s = 9.721308333 CPU-hours. This covers the initial pilot (645.23), the imports (1,316.48) and every attempt from A0000001 to A0000750, failures and RED runs included.
- Production maxima: peak RSS 538,020 KiB (A0000745) and maximum invocation wall 243.99 s (A0000737). The broader lot (R0009 at 3,838,968 KiB) is a different perimeter.
- Whole-service sample at 2026-11-13T23:30:25Z: 30,574,198,723,000 ns plus the pre-service baseline of 2,999.71 s gives 33,573.908723 CPU s. It includes the driver, wrappers, children and an active invocation, overlaps the ledger and is never added to it.
- DERIVED conditional envelope (not a measurement): 33,573.908723 + 2,056.48 (A0000736–A0000750) + 8 × 1,940 = 51,150.388723 CPU s = 14.208441312 CPU-hours. It covers the service and the recorded baseline only.
- UNKNOWN:
  - the final whole-service counter, lost with the transient unit (journal inaccessible; non-interactive sudo requires a password; no escalation);
  - pre-service and XML administrative overhead, including the worker's unmeasured stdlib XML read of a JUnit file.
- No exhaustive 24 CPU-hour certificate is given; no overrun is established and no budget increase is authorized.

Closeout outputs (Codex): `docs/audits/stream_19_e4_full_20261114.md` `34c450085c80bb6e9653c1d9737d0506f68d6120aac7d2de45e0c7c3d6c6d901`; `docs/MAPPING.md` `8420545d53a90ba24987699bcea64f239ec25b0a1b6f0155f86836ff8d0e7b92`. Codex removed one trailing blank line from the report after its initial reception; no result changed.

## Errors and Dead Ends

- Native plan v0 was refused (NO-GO v0). The defects were an empty block tail, K not derived from the plan, undefined attempt states in the ledger, cost kernels mixed with science, confusion between mode and domain, receipts not bound to the identity, no logical invariance and an unclosed publication. They led to plan v1 and the canonical plan.
- The first delivery (140 tests) was refused at reception (R1–R7). The corrective annex and W0018–W0032 fixed it.
- Residual GO: four defects reproduced by Codex witnesses (R0006 RED):
  - Import records were not reconciled with their hashed CSV, so a zeroed `cpu_s` was accepted.
  - `consumed_through` summed every live import, so a later administrative import invalidated a frozen activation.
  - The pilot receipt ignored the P2 partition count and block, so a count of 0 was accepted.
  - `volumes.csv` labelled a derived final+CSV sum as a MEASURED temporary peak.
- Fixes for these four (RED then GREEN, W0033–W0036):
  - import facts recomputed from the hashed CSV, with contiguous ids;
  - frozen import membership per snapshot;
  - P2 block, exact count and SHA-256 publication reference checked online and standalone;
  - volumes split into MEASURED_FINAL_BYTES, derived bounds with their basis, and NOT_OBSERVED peaks.
- The worker's own no-attempt witness exposed a code defect: `check_snapshot` raised FileNotFoundError on a ledger with imports but no attempts directory (W0034). It was fixed in W0035.
- Test defect (W0019): `save_fair_csv` writes 53.26 as 53.259999999999998, so a `replace("53.26", …)` tamper changed nothing. The tamper was rewritten; this was not a code defect.
- R0008: `make check` collection failed on root-owned, ignored audit copies named `test_*.py` under `logs/`. Codex renamed them `.py.source` with bytes and hashes unchanged; official tests and discovery settings did not change. The failed attempt (42.98 CPU s) stays counted.
- Historical QA scope: the unchanged global suite includes real-data integration checks, so a PASS there does not establish synthetic-only or pre-2020 I/O. Codex recorded this as C-legacy-global-check-scope. The researcher's distinct exception GO authorizes the unchanged baseline and hook for integrity and non-regression only.
- Disk STOP at 2026-11-13T14:28Z: 887,238,656 B available against 1,512,808,090 B required (439,066,266 B footprint plus the 1 GiB reserve). It was lifted after the researcher freed space (Codex then measured 26,862,768,128 B). The STOP file stays as history.
- Accounting dead end: systemd collected the transient unit at exit, and its final whole-service CPU counter went with it. The user journal was unreadable and no escalation was attempted. This led to the closeout accounting STOP, then to the researcher's finalization GO.
- Driver shell CPU (attempt-id scan, wrappers) lies outside the attempt ledger. Observed inter-attempt gaps grew from 0.914 s (after A0000392) to 1.564 s (after A0000669). Only the whole-service counter covers this cost; the gaps are an observation, not a ledger entry.
- Codex cancelled the worker's documentary-closeout mission before any repository write and reused its scratch AWK appendices.

## Current State

- The campaign is finished (exit 0 at 2026-11-14T00:02:44Z) and its service is gone. The shared lock is no longer held by E4, and no scientific restart is planned.
- Publication: `results/e4_alignment/full_20261113/` is immutable and verified locally (campaign verify, portable audit, inventory hashes).
- Git: no commit of this lot; this worker ran no Git command in the closeout missions. Codex owns explicit-path staging (with the documented force-add of the compressed publication fragments at validated paths only), the diff, size and range audit, the commit with the hook and controlled publication.
- Closing verification is FUTURE: AST-only reindexation and the unchanged global commit hook under the shared lock, after this wrapup. Their costs are measured separately and are not in the cutoff figures.
- Accounting: the reserve stays open with its UNKNOWN terms; finalization is authorized without a cap certificate.
- Execution environment (`session.json`):
  - OS Linux 5.14.0-570.55.1.el9_6.x86_64; `.venv` on the Trading Python 3.12.9 binary.
  - NumPy 2.4.4, pandas 3.0.6, SciPy 1.17.1, statsmodels 0.15.0; BLAS scipy-openblas 0.3.31.188.0.
  - Variables `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`; torch bridge `PYTHONPATH=external/torch-cf-shim` for the test suites.
  - Shared execution lock `logs/.jepa_execution.lock` of the main checkout, resolved from `git rev-parse --git-common-dir`.
  - Limits: 8 GiB RSS, 1,800 s per invocation (GNU timeout 1,790 s), 86,400 CPU s cumulative cap.

Inventory of attachments and dependencies:

### Files [.py]
- **experiments/e4_production.py** (`402d23bf09a76c51f9dbcddaf4cd5edb3cbc476b14b42685871502e8b0826980`, untracked until the commit):
  - *Description:* E4 production runner over the frozen prototype kernels.
  - *Core Functionalities:* production identity and session id; `block_ranges`, `parse_pid`, `plan_partitions` (K = 354 at block 250); phases plan, next, run, verify, publish, verify-publication, cost-kernels, forecast, receipt, activate; atomic partitions through `e4.run_partition`; global threshold barrier; merge into FAIR gzip fragments with `manifest.json` and `lineage.json`; analysis through `e4.analyse` and `e4.holdout_fpr`; attempt ledger with frozen snapshots and imports; gate on CPU cap, disk reserve, RSS and previous exit; structured receipts and activation checks; closed-list staged publication and portable audit.
  - *Inputs:* `configs/e4_alignment.yaml`; `E4_ATTEMPT_ID`; `--phase`, `--mode {full, production_pilot, cost_fixture}`, `--root`, `--activation`, `--block` (plan only), `--to`; receipts, imports, technical GO.
  - *Outputs:* partitions under the campaign root; publication tree; receipts; activation record; exit codes 0 processed, 10 nothing left, 3 activation refused, 4 resource or ENOSPC, 5 refusal, 6 gate STOP, 7 fixture interrupt, 8 reservation failure, 9 bound exhausted.
- **experiments/e4_alignment.py** (`e457ebae9011a5f1d1b0b9bc43d38f2ab97a70bccd64069dba07ad51996efd01`, committed, unchanged):
  - *Description:* frozen prototype kernels, statistics and analytic precheck.
  - *Core Functionalities:* `i_star`, `role_path`, `panel`, `t7_scale`, `residual_direction`, `drift_scale`, `fit_cell` with `canonical_eigh` (gap tolerance 64·eps·max(1, λ_max)), `method_log_path`, rank and horizon first hits, `cell_calibration`, `scalar_calibration`, `oracle_diagnostics`, `holdout_fpr`, `analyse` (NORMAL_DEFF1 cells, Wilson rates, paired-bootstrap contrasts, qualification, FPR comparability, warnings), `analytic_precheck`.
  - *Inputs:* validated configuration, space (`science` or `pilot`), background, N, role and replicate keys (SeedSequence `[19, 42, …]`).
  - *Outputs:* trial, calibration, cell, diagnostic and axis tables; analysis tables.
- **tests/test_e4_production.py** (`d75d4350f0a3296605eec764169c28d860ce034ea14b427f6d5a373799008e79`, untracked until the commit):
  - *Description:* 51 production tests (REQUIRED_TESTS of the tests receipt), Codex witnesses included.
  - *Core Functionalities:* geometry, identity, resume, interruption, tiling refusals, threshold barrier, FAIR fragments, streamed axes, analysis bounds, receipts, activation, ledger and gate, ENOSPC, publication, imports, frozen membership, P2 facts, volumes, identity stamp.
  - *Inputs:* bounded fixtures (N ≤ 8, H ≤ 60, n ≤ 40).
  - *Outputs:* JUnit carrying the `e4_session_id` property.
- **tests/test_e4_alignment.py** (`d8a19c9eed02d4da96a4a1d2de0de717550e0dd5e81e41461406837e2bae71f9`, committed, unchanged):
  - *Description:* 101 prototype tests.

### Files [.sh]
- **tools/run_e4_production.sh** (`3ed5b9920dd3cb076369a55e1f532ffd4cdfbdf452d2cb3a7c535c837ace4af8`, untracked until the commit, frozen):
  - *Description:* host driver.
  - *Core Functionalities:* shared `flock`; attempt reservation by atomic `mkdir` from A0000001 upwards; `cmd.txt`, GNU `time.txt`, `exit.txt`; `timeout` of 1,790 s; campaign loop of K + 1 `next` calls that must end on code 10 (else code 9), then verify and publish.
  - *Inputs:* `attempt ARGS…` or `campaign MODE ROOT BLOCK TARGET [ACTIVATION]`; optional `E4_LOCK`.
  - *Outputs:* attempt directories under `logs/stream_19_e4_production/attempts/`; exit codes.
- **logs/stream_19_e4_production/run_full_20261113.sh** (`3511d09c12beb37786429fa9d9ee6d3423d0947ff01613bbf296a8c4ca00008f`, ignored):
  - *Description:* service wrapper: SHA checks of the runner and driver, campaign, verify-publication, terminal accounting receipt, exit and finished markers.

### Files [.yaml]
- **configs/e4_alignment.yaml** (`5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2`, committed, frozen):
  - *Description:* grid, ρ = 0.4, H = 2000, α = 0.05, T_fit = n_cal = n_hold = n_alt = B_boot = 2000, pilot_n 40, prefix_k 8, info_divisor 40, backgrounds gaussian and t7 (ν = 7), fpr_margin 0.01, qualification 0.95, seed 42, limits.

### Files [.md]
- **docs/audits/stream_19_e4_full_20261114.md** (`34c450085c80bb6e9653c1d9737d0506f68d6120aac7d2de45e0c7c3d6c6d901`):
  - *Description:* final scientific report (Codex), sections 1–10 and appendices A–C (every cell of both readings, FPR point differences of the contrast pairs).
- **docs/MAPPING.md** (`8420545d53a90ba24987699bcea64f239ec25b0a1b6f0155f86836ff8d0e7b92`):
  - *Description:* number mapping, including the E4 full sources.
- **docs/audits/stream_19_e4_production_pilot_20261113.md** (`273d54b557a3a3f4ef4feb12dd442dfaa0a325342d4edb268e9c348d98bd5b28`):
  - *Description:* technical and resource report written before activation.
- **docs/DEVIATIONS.md** (`ef6c43948f908cd59834db81e7c633e00d7eb0831cff2b6c3799d708e37f90b3`):
  - *Description:* E4 production entries and C-legacy-global-check-scope.
- **logs/stream_19_e4_production/review-closeout-cost-20261114.md** (`bb5de51efa706bfbf49c647a8de1524c3ff824d7de39a312c19b93104e016e32`, ignored):
  - *Description:* Codex final reception, whole-service sample and derived envelope.
- **logs/stream_19_e4_production/implementation-journal.md** (ignored):
  - *Description:* worker journal (W0001–W0038 and closeout).
- **Decision files** (GO, NO-GO, STOP, REQUEST, plans):
  - *Description:* listed with their SHA-256 in the Context table.

### Files [.json, .jsonl, .csv, .csv.gz]
- **results/e4_alignment/full_20261113/** (session `6d1acbd629975285acc7df37cb3d02e5daf5f0b7339473af78d02757ef6066af`, label `E4_SCIENCE`):
  - *Description:* `PUBLISHED.json` `5c318af8768b7f1b83e08e30a20dd57067010ad05bf7b70a0cb31d3c03fd544d` (inventory of 91 files); `manifest.json` `b7514d600af40dc5e10ac8738333c25059218bd184c4a49008adbe2b5de6d69c`; `lineage.json` `c3445422fe4610927a681204f9e6832a19c9667f7f170e7b3034165124475b47`; `session.json` `71362a7c5a0d6348574ca2af6740dbae131af076f839ed5b3cffb7f6fc90c97b`; `campaign_plan.json` `d31d2ff30596fb3899421a688a911674cfc6a8ef67c3c1965307cb36fb801b01`; `activation/activation.json` `e3edb7c8f71eabd55cf24d00f912186f1b86acaccf40dbe55698c96e34963e0c`; `ledger/cpu_ledger.csv` `fdda5dc87675b45e8bd187a6cd1705babf8c0e83d664ccbf347548ffb3da51f0`; `ledger/attempts.jsonl` `b26536922e877b23bb75a20a40d6145fe51b22d02ff2c196208754e48a861ddb`; `records/thresholds/calibration.csv` `5dfa9852f26b73490e25b2d0259e6769872c11fecd300d8ae3b1e9a3a1c5b30c`; `records/thresholds/cells.csv` `e5696b76dc9d01a0825bf3e3241358bfa2da8d5d853d476b55b9c30dc30bfd6d`; `records/scalar_cal/scalar_calibration.csv` `b28019731218adb04c3f60670d42a519d70c4cdd3a608ab922440dda1dc36233`.
  - *Analysis CSVs:* `cells_predictive_rank.csv` `8ffa3c931f5e526addfb46732b9a5c87c4661454b3cb12462f69fd60e857c38b`; `cells_anytime_valid_horizon.csv` `961b97111f97347bb7357b992ac1cee632fe29d66f3a9742dae16b45ffb11324`; `holdout_fpr.csv` `20968b0bde02d9024f123e0f394d482dbd42ef2dfe21bff0e02ed84b426c117b`; `contrasts_predictive_rank.csv` `3270152cfd5573e67b984109ed5c8c73581212b9be58afde2ee5d359bc00a6bb`; `contrasts_anytime_valid_horizon.csv` `68addf59cb8defb1db12bf038d3c844bf5c8f338e74101f7a369dcb480aa4afe`; `warnings_predictive_rank.csv` and `warnings_anytime_valid_horizon.csv` `34c9998eb17be1f89bbdd921a10e835043f325ee31e7e4a446dd2d6aca3f4f41`.
  - *Fragments:* `.csv.gz` files of the 14 cells for trials, calibration_maxima, diagnostics and diagnostics_axes, hashed in `manifest.json` (`sha256_csv` per fragment, `sha256_whole` per table) and in `PUBLISHED.json`.
- **logs/stream_19_e4_production/full-terminal-accounting-20261113.json** (`5cfcaa46caf073ca9c2050183e542ec07be6a275a58fb77574e9ceb83b41afc8`, ignored):
  - *Description:* terminal accounting receipt (cutoff A0000749, 34,995.28 CPU s).
- **logs/stream_19_e4_production/full-20261113.log** (`d1c3ae8ea67b8aa8958739253ec4c4d1468069772c33156591fb358ecd975f15`, ignored):
  - *Description:* campaign log (phase statuses, verify and portable-audit summaries).
- **results/e4_alignment/precheck_20261112/partitions/precheck/analytic_precheck.csv** (`afe7164dee6e331d1ae132991a5514ad137671cac6ac9163636a9bcb7611e012`):
  - *Description:* analytic precheck fixed before simulation (one-atom clocks; not RMST, ADD or power).
- **results/e4_alignment/production_pilot_20261113/final1/**:
  - *Description:* pilot evidence cited by the activation: report `MANIFEST.json` `ccf1527c520cf7d986cfe7a34f3ff3fa6b3f752e4aa2716b0fe9eda12dde1c6d`, `forecast.csv` `4c826ae14a81e1a93ac296918ee66c255dd6ccdd5db80da06e4727a2cbd9ec28`, `partition_forecast.csv` `42261771906b6abdd6e57b1e830e08cac470286cae6d22e2a5f073221f516251`; receipts `tests.json` `5a4b547956c5523fc8365ad315afe42d24e83748c523255012564f57f8c7e411`, `make_check.json` `31f0c46ce1233b0e12cbc695b93eca3d627be85becda08fa85921023dda7e874`, `pilot.json` `30555fa9b91139d9850458f002a4f92db6a26c124530eed9b1c6379eecb871a9`, `nonleak.json` `8a2cad52a548a515745f382a4f365dcbc68eed1334174f1e80cfda3ebf6c7566`; `evidence/evidence_cost.csv` `39e21a6577ce1b0385f7eba9e522c4d40e720447d8847ead04681ee18a97b7e1`.
- **results/e4_alignment/cost_report_20261112/external_attempts.csv** (`45b79711c50eac4b286cfc9d8326b64dc241f2033c75cd07d0d83b4099b66925`):
  - *Description:* source of the initial pilot cost (645.23 CPU s).

## Vigilance Points

- Accounting reserve:
  - The 24 CPU-hour cap is not certified. The 51,150.388723 CPU s envelope is DERIVED, covers only the service and the recorded baseline, and excludes the UNKNOWN pre-service and XML overhead.
  - The whole-service sample overlaps the ledger and is never added to it.
  - No overrun is established and no budget increase is authorized.
- Closing verification has not run yet; R0007 and R0009 predate the campaign. Do not report the closeout hook, reindexation or `make check` as passed before Codex's measured receipts exist. Their CPU is outside the cutoff and is measured separately by Codex.
- Scientific reading limits:
  - Inference is conditional on the realized fits and calibrations (no outer fit resampling).
  - The twelve contrasts are NOT_IDENTIFIED; their estimates are descriptive only.
  - The slopes are local finite-grid log-RMST slopes: not Lorden ADD, not a universal exponent, not a `cor:scaling` exponent.
  - O-dir and O-score1 are ORACLE references, so no learned or non-oracle informational selection is shown.
  - The t7 rows use INFO_GAUSS_PROXY_T7, not an exact t7 KL; no KL increase is inferred.
  - `pc1_leakage` measures the alignment of the fitted PC1 with the market, not leakage of the injected drift.
- FPR:
  - The 14 predictive flags are dependent pointwise diagnostics, not independent or multiplicity-adjusted rejections.
  - The predictive contrasts compare methods at a common nominal α only; no gain claim at equal attained FPR is possible.
  - NORMAL_DEFF1 endpoints are not clipped to [1, H].
- Data and seals:
  - The producer is synthetic-only: no private data, real returns, J4/FROZEN or 2020+ scientific window. The QA exception is limited to historical global checks.
  - Seals unchanged: E2 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, E3 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, PCA manifest `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`.
  - The historical E3/D8 FAIL is unchanged.
- Git hygiene for the commit:
  - explicit paths only;
  - nothing under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/`;
  - no file over 50 MB (largest 13,651,324 B);
  - no ignored raw journal, cache or absolute server path;
  - the renamed `.py.source` copies under `logs/` stay ignored and unchanged.
- Scope:
  - This lot does not close the historical stream 19.
  - Stream 23 waits for the E4 Git publication, then reconciliation on published main, its own gates and an explicit runtime signal.
  - Stream 27 (P8) is not approved; stream 21 has no code; stream 16 has no training.
  - No fifth Claude instance.
  - The frozen runner and driver receive no change in this lot.

Unresolved variables and decision trees (carried forward, protected):
- Closing hook and `make check` under the lock: if they pass, Codex proceeds to the staging audit, commit and controlled publication. If they fail, STOP and report to the researcher; no source or parameter change to force a pass.
- UNKNOWN accounting terms: if a later source establishes their coverage, Codex documents it without changing the measured figures. Otherwise the reserve stays UNKNOWN in every report and is never converted to zero.
- E4 publication on main: if it succeeds, Codex may reconcile stream 23 and verify its own gates before a separate explicit runtime signal. The latest restrictions on 27, 21 and 16 remain in force; the historical wave GO does not lift them. Otherwise dependent streams stay blocked.

## Recommendations

- Codex, in order:
  1. AST-only reindexation, without AI summaries.
  2. Finish explicit-path staging, with the documented force-add of the compressed publication fragments.
  3. Diff, size and range audit.
  4. A Conventional Commit without trailers, whose unchanged global hook runs under the shared lock with measured host receipts before the commit is created.
  5. Controlled publication per CLAUDE.md.
- Next instances cite `docs/audits/stream_19_e4_full_20261114.md` and `docs/MAPPING.md` for every E4 number and treat the publication as immutable. Further scientific execution requires its applicable GO; these results imply no rerun authorization.
- [Strategic Advice] In future service-run campaigns of other lots, persist the unit's CPU counter before the unit exits; losing that counter is what left this reserve open. Downstream citations should keep the NOT_IDENTIFIED status, the ORACLE labels and the predictive-reading COMMON_NOMINAL_ALPHA_ONLY label attached to every E4 number they reuse.
- Protocol note: the LIGHT kernel referenced by the wrap-up module is not injected in this session, so this handover maps the module's skeleton onto the project's six wrapup sections. The de-watermarking module was not injected this turn and no stylistic perturbation was applied.
