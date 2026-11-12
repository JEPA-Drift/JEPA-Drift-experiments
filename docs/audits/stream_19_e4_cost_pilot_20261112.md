# Stream 19 E4: cost pilot report, 2026-11-12

**COST PILOT COMPLETE. SCIENTIFIC FULL NOT EXECUTED.** All 16 declared partitions completed: the deterministic analytic
precheck, the global `scalar_cal` cost partition and the 14 cost cells (two backgrounds × seven N). There were 17 measured
CLI attempts, including one identity-only precheck replay that returned `SKIPPED_COMPLETE` with unchanged outputs. None
was refused, timed out, blocked (`BLOCKED_RESOURCE`), tie-refused (`EIGENVALUE_TIE_UNRESOLVED`), retried or wrote to
stderr. This lot measures CPU and memory only. No delay, FPR, detection rate, threshold, alignment or monitored path from
the pilot was inspected or retained. The two full-size analysis fixtures ran on labelled `COST_FIXTURE` alarm arrays.

Sources: `logs/stream_19_e4_code/pilot-execution-20261112.md` (execution protocol and record) and
`results/e4_alignment/cost_report_20261112/` (FAIR tables, `manifest.json` SHA-256
`54f407aad07db8de12dd51af752b1f513070d5c943daeae4ebec54d1c0ac84f0`, label `COST_ONLY_NOT_SCIENTIFIC_E4`,
`full_campaign_executed: false`).

## 1. Authority and frozen identities

| Object | Path | SHA-256 |
|---|---|---|
| Scientific GO (conditional) | `prompts/GO-stream-19-e4-science-20261112.md` | `d815262bd55960c63422a00364643ebb49baf4dd47c9d9772d77fa3a70907aad` |
| Protocol (section 12 governs) | `docs/audits/stream_19_protocol_proposal_20261112.md` | `cd786a02d5d6407ccf9a88ba91cacce50c7dcc0f45655868bb32643c577ec657` |
| Pre-implementation checks | `docs/audits/stream_19_e4_preimplementation_20261112.md` | `986c71f545b28afe60a084fef5fb133b4fb03de211dbf87161d6c41874b3a9da` |
| Code plan (integrated GO) | `prompts/plans/plan-19-e4-code-20261112.md` | `9b11cb50d3273c36fd5bb937ad62a9dca846461d40ed7f6a407bfee1c5d0e819` |
| Technical GO | `prompts/GO-stream-19-e4-code-20261112.md` | `dab9ccd66437adb97bdcf2e0026d728ffc2917639641f2cebc3e7106bcc85565` |
| Review round 1 | `prompts/REVIEW-stream-19-e4-code-20261112-round1.md` | `0384991848ff4d2ce5e439f59be77e67c905ed21c25faf50184227fc5e6d4b7b` |
| Producer | `experiments/e4_alignment.py` | `e457ebae9011a5f1d1b0b9bc43d38f2ab97a70bccd64069dba07ad51996efd01` |
| Tests | `tests/test_e4_alignment.py` | `d8a19c9eed02d4da96a4a1d2de0de717550e0dd5e81e41461406837e2bae71f9` |
| Configuration | `configs/e4_alignment.yaml` | `5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2` |
| Source manifest (every hashed input) | `results/e4_alignment/cost_report_20261112/source_manifest.csv` | `dd7895b29b4b97d4300e4956559b4c10cd881f1ba525a2cf7061cb34a2346598` |

`source_manifest.csv` records each source file, size and SHA-256: the producer, configuration, tests, plan, both GOs, the
pre-implementation note, the reused modules (including `jepadrift/representations/extract.py`), every partition file and
both `session.json`. Session identities are `c068bc2490b6aa58830fb8a821cea7ecf2fd43e1c82fe2eb579ee6f5e4fd95f0` for the
precheck and `01fda9c895d958c2090ab12c3da592e03c751e084c64a37f82c5baa3d32be057` for the pilot.

The approved configuration is unchanged: equicorrelated Gaussian and shared-scale t7 backgrounds (rho = 0.4); I* fixed
by ln(H/alpha)/I* = H/40 with H = 2000 and alpha = 0.05; N in {8, 16, 32, 64, 128, 239, 500}; T_fit = n_cal = n_hold =
n_alt = B_boot = 2000, seed 42; six methods, O-dir and O-score1 being ORACLE. No I*, N, method or sample size changed
after the pilot. The pilot drew only from the `pilot` seed space, disjoint from the scientific one; the fits and
calibrations of a future scientific run are not yet realized. The pre-pilot engineering check, which is not an E4 run,
passed 37 contracts (36.42 s) and 1257 tests with five expected D4 skips (497.23 s): 1294 passed, no failure;
prompts-check 33/33; targeted E4 suite 101 passed in 9.56 s.

## 2. Execution conditions

- Serial (`--jobs 1`), `.venv/bin/python`, the shared execution lock and the deterministic thread, BLAS and hash variables.
- Each attempt ran under GNU `time` (user CPU, system CPU, elapsed time, peak RSS, exit status) and an external deadline,
  `timeout --signal=TERM --kill-after=10s 1790s`. Internal guards are cooperative: an 8 GiB RSS cap checked before
  allocations and between blocks of 8 paths, and a 1800 s `signal.alarm`.
- Order: precheck, precheck replay, `scalar_cal`, then the cells by increasing N, alternating Gaussian and t7. The pilot
  used 40 replicates per role with the approved H, N, T_fit and methods.
- The first aggregation command failed before writing any output (`load_config` needs an explicit path) and was corrected
  to `e.load_config(e.CONFIG)`. It is not a producer attempt; no producer output, parameter or seed changed.

## 3. Measured resources (MEASURED)

From `resource_summary.csv` (SHA-256 `afdd2ee23d1d8ca4f328d0f5d8e4f7a8de9bdbb8ecf3b87988aaa82ad1c2b4ce`):

| Metric | Value |
|---|---|
| CLI attempts / complete partitions | 17 / 16 |
| Consumed CPU, all attempts (external user + system) | 645.23 s = 0.179231 CPU-h |
| Precheck including its replay | 2.08 s |
| Cost pilot (`scalar_cal` and 14 cells) | 643.15 s |
| Peak external RSS | 463380 KiB = 0.441914 GiB (`scalar_cal`) |
| Longest invocation wall time | 112.08 s (`t7:500`) |

Per attempt, from `external_attempts.csv` (SHA-256 `45b79711c50eac4b286cfc9d8326b64dc241f2033c75cd07d0d83b4099b66925`;
time precision 0.01 s):

| Partition | CPU s | Wall s | Peak RSS KiB | Partition | CPU s | Wall s | Peak RSS KiB |
|---|---|---|---|---|---|---|---|
| precheck (first) | 1.04 | 1.05 | 200552 | precheck (replay) | 1.04 | 1.05 | 190412 |
| scalar_cal | 3.73 | 3.76 | 463380 | | | | |
| gaussian:8 | 23.63 | 23.72 | 207404 | t7:8 | 23.72 | 23.82 | 206564 |
| gaussian:16 | 25.07 | 25.16 | 212988 | t7:16 | 24.88 | 24.97 | 207292 |
| gaussian:32 | 27.07 | 27.18 | 215436 | t7:32 | 27.05 | 27.16 | 211736 |
| gaussian:64 | 32.15 | 32.27 | 214504 | t7:64 | 32.50 | 32.62 | 215296 |
| gaussian:128 | 40.84 | 41.00 | 237044 | t7:128 | 41.42 | 41.58 | 239724 |
| gaussian:239 | 59.08 | 59.31 | 277780 | t7:239 | 58.81 | 59.05 | 283256 |
| gaussian:500 | 111.57 | 112.03 | 382772 | t7:500 | 111.63 | 112.08 | 378976 |

**Consumed CPU and the stage rows.** Consumed CPU is the sum of the external totals of every attempt, the precheck
replay included. The external totals are not added to the stage rows, so nothing is counted twice. Each `cost.csv` also
holds an in-process `invocation` row (cumulative process CPU, imports included, read before the final bookkeeping) and an
`orchestration` residual. For example, `gaussian:500` shows 111.458802 s in file against 111.57 s externally; the
difference is the final write, hashing, rename, logging and interpreter exit.

**Where the cost goes at large N.** In `gaussian:500`, the most expensive stages per role (40 paths) are
`logpath:P3-CS(b)` (15.28–15.38 CPU s), `logpath:SPEC-full` (6.07–6.14 s) and `stream:P3-CS(b)` (4.38 s for holdout and
alternative). **Memory.** Peak RSS comes from the full-dimension analysis fixtures of `scalar_cal`; the largest cell
peak is 382772 KiB.

## 4. ESTIMATE scenarios (conditional, Q6 a)

From `forecast_scenarios.csv` (SHA-256 `b3267d0c8d43bde1e5c27e4748d0654c3d44dab3cd60e768c1d1d1aec63da4a3`). The total is
the consumed precheck and pilot CPU plus the projected future campaign, against the 24 CPU-hour total cap (86400 s).

| Scenario (approved order) | Cells | Total CPU s | Total CPU-h | Future CPU-h | Status |
|---|---|---|---|---|---|
| FULL_GRID | 14 | 31814.728159 | 8.837424 | 8.658194 | WITHIN_CAP |
| DROP_N500 | 12 | 20801.227958 | 5.778119 | 5.598888 | WITHIN_CAP |
| T7_ON_8_64_239 | 9 | 16297.119340 | 4.526978 | 4.347747 | WITHIN_CAP |

The manifest names `FULL_GRID` as the recommended cost scenario, and no fallback was applied. **These figures are
conditional ESTIMATEs, not a resource guarantee or an execution GO.** They rest on the following declared factors and
assumptions, all applied to measured serial costs:
- **×50 (2000/40), per role:** draw, stream, log path, readings and oracle diagnostics, scaled by n_role/pilot_n.
- **×50, once:** IO, and the shared scalar calibration.
- **n log n factor:** dictionary calibrations, (n_cal ln n_cal)/(pilot_n ln pilot_n).
- **×1:** the complete fit of each cell, and the two full-dimension analysis fixtures, already measured at final size.
- **Per future invocation:** start-up and orchestration CPU, charged once for each projected block of at most 1500 s of
  wall time.

The plan's resource limits stay in force: 8 GiB RSS and a 30-minute deadline per invocation, enforced externally. With
the ×50 factor, the projected wall time of the largest cells is well above one invocation. A future run therefore needs
replicate-block partitions, which are not implemented (section 5).

## 5. Unmeasured overhead and planned volumes (explicit unknowns)

`unmeasured_assumptions.csv` (SHA-256 `05830ac6f0b3d54700158eaa5fbb8a2c03f23de9fc0ca3afce8a406c68c8ee5e`) lists six
`UNMEASURED_ASSUMPTION` items with no CPU value, none counted as zero: parallel workers and concurrent memory (the pilot
ran with jobs=1); merging the partitions of a future campaign; recomputation after an interrupted partition; scientific
payload serialization and hashing; J_k and trial long-table assembly; and the memory of a complete scientific aggregation.

**Not built, not exercised.** The prototype `--mode full` remains refused before any write. Production partition
orchestration (replicate blocks, merge, restart) is neither implemented nor exercised.

**Planned volumes.** `planned_output_volume.csv` (SHA-256 `fc55a907d82bb95f8c9ac367e7ff3990b010ae6be0d4c2b7c2c881ef1a98e835`)
gives schema arithmetic only:
- `diagnostics_axes` at most 3948000 rows (2 backgrounds × the sum of N × n_alt);
- `trials` at most 672000 rows (14 cells × 6 methods × (n_hold + n_alt) × 2 readings);
- both counts assume no refused cell.

These are not measured payload sizes or full-run memory. The storage and Git policy of the J_k long table must be decided
before any full execution or staging.

## 6. Analytic censoring risk (deterministic precheck, no draw)

Source: `results/e4_alignment/precheck_20261112/partitions/precheck/analytic_precheck.csv` (SHA-256
`afe7164dee6e331d1ae132991a5514ad137671cac6ac9163636a9bcb7611e012`). The table reproduces the pre-plan journal
`logs/stream_19_e4_code/analytic-precheck-20261112.txt`.

**What the clock measures.** It divides log(8 N gamma_H) by the best fixed-bet mean log growth at the Beta union-bound
alignment envelope. This is a diagnostic one-atom evidence clock, not a hitting time. The table expresses it relative to H:

| N | 8 | 16 | 32 | 64 | 128 | 239 | 500 |
|---|---|---|---|---|---|---|---|
| Gaussian | 0.0798 | 0.1285 | 0.2162 | 0.3792 | 0.7371 | 1.2415 | 2.3742 |
| t7 (`INFO_GAUSS_PROXY_T7`) | 0.0657 | 0.0999 | 0.1675 | 0.3016 | 0.5368 | 1.0054 | 1.8017 |

**O-dir.** The `O_DIR_SCALAR` clocks are 107.16 days (Gaussian) and 91.24 days (t7), i.e. 0.0536 H and 0.0456 H. Their
`N = 1` is a scalar-dimension marker, not an approved one-asset residual cell.

**Reading.** At N = 239 and N = 500 the one-atom clock exceeds H for both backgrounds. This flags a material censoring
risk for the **secondary anytime-valid reading**. These clocks ignore resets, path fluctuations and simultaneous channels.
They are neither RMST, ADD nor power, and they do not show that the primary rank reading fails: its thresholds come from
calibration; the future scientific thresholds have not been produced. I* and the grid stay unchanged. Qualification
requires a Wilson lower detection bound >= 0.95 at every N for both methods of each contrast.

## 7. Scientific protocol of a future run (restated, not executed)

- **Readings:** primary predictive-rank reading (alpha = 0.05, H = 2000); secondary anytime-valid reading at
  gamma_H = H/alpha. Both use one first-hit contract, with days 1..H or −1.
- **Slope:** the fixed local slope is the OLS slope of log RMST on log N over the whole grid, never a Lorden ADD or a
  universal exponent. Delta = Delta_1 + Delta_2 is a descriptive identity with no causal attribution.
- **Uncertainty:** paired percentile bootstrap with common replicate indices for every N and method, conditional on the
  frozen fits and calibrations, with no outer resampling of the fits.
- **Qualification:** Wilson lower detection bound >= 0.95 at every N per contrast: SPEC-full/O-dir for Delta, O-score1/O-dir for Delta_1,
  SPEC-full/O-score1 for Delta_2. EW stays a negative control. `COST_GROWS`, `NO_GROWTH_DETECTED` and `COST_SHRINKS`
  label Delta only; a refused or unqualified cell gives `NOT_IDENTIFIED`, and every cell stays visible.
- **False alarms:** the holdout FPR is measured per method, background and N, with the `FPR_ABOVE_NOMINAL` label and the
  paired ±0.01 comparability rule. EW, O-dir and O-score1 share one frozen scalar threshold; dictionaries are calibrated
  per cell.
- **Scope labels:** oracle rows and diagnostics carry `ORACLE_*` and stay out of ex ante tables. Under t7, I* is the
  Gaussian proxy `INFO_GAUSS_PROXY_T7`, never a t7 KL. The O-dir sign-stream information is a Bernoulli KL, not a KL of
  the returns. K_MP counts residual axes after PC1.

## 8. Reproducing the forecast

The command below uses the aggregate CSVs and the existing `forecast` function. Codex executed it during reception;
the consumed CPU and all three scenario totals matched section 4.

```sh
flock -n "$(git rev-parse --path-format=absolute --git-common-dir)/../logs/.jepa_execution.lock" env OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg .venv/bin/python - <<'PY'
import pandas as pd
from experiments import e4_alignment as e
d = 'results/e4_alignment/cost_report_20261112/'
cfg = e.validate_config(e.load_config(e.CONFIG))
rows = pd.read_csv(d + 'cost_rows.csv', float_precision='round_trip')
att = pd.read_csv(d + 'external_attempts.csv', float_precision='round_trip')
totals = att.groupby('partition', sort=True)['cpu_s'].sum().to_dict()
f = e.forecast(rows, cfg, invocation_totals=totals)
print(f['consumed_cpu_s'])
print(f['scenarios'].to_string(index=False))
PY
```

It printed consumed CPU 645.23 s and the three totals of section 4. `cost_rows.csv` (SHA-256
`478238fb1471e18b7b043197a24d66b3a709618d5e724ef8beab07bc3235c5da`) concatenates the 16 partition cost tables.

## 9. Decision requested

The only decision requested from the researcher is the later **scientific execution GO**. Before giving it, the
researcher should weigh the technical overhead that remains open:
- production replicate-block partitioning, with its merge and restart, is not implemented;
- payload serialization and long-table assembly are unmeasured, including about 3.95 million planned J_k rows;
- parallel memory is unmeasured;
- the secondary-reading censoring risk at N in {239, 500} (section 6).

A numeric `WITHIN_CAP` does not authorize execution. This lot used no financial data, J4/FROZEN, JEPA/VAE training, E6
or sealed PCA/E2/E3 output.
