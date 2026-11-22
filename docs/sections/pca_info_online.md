# PCA information-ordered online selection (Stream 32)

This B technical note and its YAML config form a documentary preregistration
draft under B_TDD_ONLY, whose scope is B contract verification. Neither file is
a runtime GO. The runner implements this draft. The draft follows plan §12, the
v2.1 amendment §§5–6 and the T1–T68 matrix. The related files are the
[YAML config](../../configs/pca_info_online.yaml), the
[runner](../../experiments/pca_info_online.py), the
[Stream 32 plan](../../prompts/plans/plan-32.md), the
[v2.1 amendment](../../prompts/plans/plan-32-v2.1-amendment.md) and the
[T1–T68 matrix](../../prompts/MATRIX-stream-32-T1-T68-20261114.md).

## Purpose and design

- Synthetic mean drift is injected into returns and detected on a PCA basis.
  The ambient dimensions are N=32 and N=239.
- EXACT and FITTED_LW_GAUSSIAN at both N give four setups, all with fit ID 0.
  A later T7 campaign depends on the completeness, null qualification and
  invariance of this Gaussian stage ([plan](../../prompts/plans/plan-32.md)).
- The RESIDUAL application defines K=20 eligible PCs from components 2–21.
  The MARKET application defines K=20 eligible PCs from components 1–20. Each
  policy monitors a subset of these eligible PCs, and FULL_K selects all 20.
- The families are F0_ISOTROPIC_RESIDUAL, F1_TAIL_RESIDUAL,
  F2_STRUCTURED_RESIDUAL, F_HEAD_RESIDUAL and F3_MARKET.
- The policies are 8 ONLINE_{INFO,PREFIX}_{MIX,AFF}_W{32,128} policies,
  4 ORACLE_{INFO,PREFIX}_{MIX,AFF} policies and 6 static baselines (FULL_K,
  FIXED_EIGENMEAN_PREFIX, CPV90, RESIDUAL_CPV90, FIXED_DEV_PREFIX,
  FIXED_EXANTE_QBAR_MIX).
- INFO policies may change component order. PREFIX policies change only the
  prefix length.
- The ONLINE mask at day t is predictable and depends only on strictly past
  scores. Its adaptive day-one fallback is {min E}. Oracle and static masks
  follow their own rules, and static baselines are fixed in advance.
- The common isotropic prior variance is s2 = 2 ln(H/alpha)/(HK), based on K.
  gamma_M selects cost. CAL calibrates the separate alarm threshold h.
- DEV is disjoint from all later phases and frozen before CAL. The design
  must not be altered using ALT outputs.
- Root seed 3232 is the reproducible project's B draft choice.

## Command interface

The runner accepts the flags `--config`, `--mode smoke|pilot|full`, `--jobs`,
`--resume`, `--output-dir`, `--log-dir` and `--describe`. The project pins its
`.venv`. The following read-only example prints a descriptor-only view.

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
.venv/bin/python experiments/pca_info_online.py --config configs/pca_info_online.yaml --mode smoke --describe
```

- `design_id` hashes the canonical descriptor, which covers code, seed plan,
  scientific options, sizes, scope, envelope and environment. `design_tag` and
  `run_id` take the first 16 hex digits of `design_id`.
- The code admits `authorization: null` in smoke mode. The lot C procedure
  separately requires a Codex runtime GO that cites the exact `design_id`.
- Pilot and full each require a separate researcher GO. Before execution they
  require `stage`, `design_id` and `go_reference: {path, sha256}`.
- The `path` value names a repository-relative GO file that contains that
  `design_id` and a human-readable scope. The GO is authored from the design
  before any realization exists, so it contains no future identity.
- Each runtime mode requires its own distinct GO.

## Phases and results

- The phases run in the order SETUP, DEV, CAL, NULL_PLAN, HOLD, ALT and FINAL.
- The default log dir is `logs/pca_info_online/<output-basename>`. Committed
  staging for one design lives under `<log-dir>/staging/<design_tag>`, and
  lookup verifies the complete `design_id`. The runner refuses stale or
  foreign staging. `--resume` reuses only verified partitions.
- CAL computes a predictive exchangeable rank with a greater-or-equal boundary
  against independent finite-horizon null paths. Non-oracle policies share one
  CAL cell across families. Oracle policies calibrate by family and carry the
  label NON_DEPLOYABLE_ORACLE_CALIBRATION.
- NULL_PLAN bounds HOLD for the primary full run, and smoke uses a reduced
  plan.
- Realized identity binds canonical phase digests and the FAIR payload
  SHA-256. Jobs, paths, telemetry and GO bytes stay outside identities. The
  design includes the envelope and its `jobs_max`.
- The runner writes publication to a sibling temporary directory and
  atomically renames it to the output directory. The runner then writes FINAL
  against the SHA-256 of the published manifest. The runner refuses to publish
  INCOMPLETE and BLOCKED_RESOURCE runs.
- Resource accounting counts CPU cumulatively and wall time per invocation,
  and workers use spawn. Lot C will deliver the aggregate memory proof and
  profiling.

## Sizes and envelope

- The envelope (32 GiB, 4.0 CPU-hours, 2700 s wall per invocation, 8 jobs)
  is the proposed B draft, identified by `design_id`. The full envelope awaits
  pilot-based R3–R5.
- Full cohort sizes are draft R3 candidates. The current role-wide CAL_NULL
  key has 2000 rows in this draft. The distinct 10,000-row primary P_CONF CAL
  proposal awaits the R3 runtime decision and, if retained, a per-cell
  allocation design; this config does not implement it.
- Pilot awaits R2.

## Payloads

- `save_fair_csv` writes the CSV payloads `calibration.csv`,
  `selections.csv`, `trials_summary.csv`, `aggregates.csv` and `issues.csv`.
- `manifest.json`, `summary.md` and `telemetry.json` are three separate
  metadata files.
- Read CSVs with Pandas `float_precision="round_trip"` and keep every text ID
  as a string.
- Payloads are PUBLISHED. Local NPZ entries are LOCAL_HASHED_ONLY.
- `I_mean` is the mean of selected daily marginal (surrogate) information.
  `I_joint_mean` is the mean of selected daily joint Gaussian subset KL
  information.
- `V_bar` and `V_joint_bar` divide the respective daily information by
  M(|S_t|). They average over the entire horizon and all ALT paths.
- M and the fluid V are ANALYTIC_PROXY quantities and are separate from ADD.
  RMST_H is a censored finite-horizon detection summary.
- The KL information basis is ORACLE_DIAGONAL_SURROGATE for the FITTED
  Gaussian arm, EXACT_ADDITIVE_KL for the EXACT arm and
  ORACLE_DIAGONAL_GAUSSIAN_PROXY for the T7 arm.
- HOLD status uses tri-state null qualification.

## Inference scope

- Pilot contrasts are PILOT_ONLY.
- The full primary H1/H2/H3 block (FITTED_LW_GAUSSIAN, N=239, RESIDUAL,
  W128, MIX) uses multiplicity m=3. H2 additionally requires HEAD geometry and
  prefix detectability. Relevant confirmatory and descriptive contrasts use
  identical per-family bootstrap indices.
- B exercised deterministic recovery fixtures. These fixtures support contract
  verification only and yield no empirical detections or gains.
- Recovery at candidate campaign settings is deferred to C, along with live
  smoke, the jobs 1/8 comparison, profiling and aggregate memory. Real data
  remains outside this stream.

## Gaussian Full allocation

The R3-A configuration covers EXACT and FITTED_LW_GAUSSIAN at N=32 and N=239,
with fit ID 0, and requires a separate researcher authorization. The Gaussian
pilot retains its original configuration and realization. T7 remains gated.
[Full configuration](../../configs/pca_info_online_full.yaml)

- The primary RESIDUAL application calibrates the three distinct PRIMARY
  P_CONF cells on 10,000 paths. All other cells use 2,000 paths. Both CAL
  groups share their first 2,000 path keys and use separate NPZ payloads.
- The primary P_CONF HOLD cohort uses the size frozen by NULL_PLAN before HOLD,
  with a minimum of 2,000 and a cap of 20,000. Other cells use 2,000 paths.
  HOLD generates, scans and commits blocks of at most 1,000 paths. Block
  keys include the starting index. Each committed block binds its exact
  signed path indices to the design and upstream phase digests.
- Individual Clopper–Pearson bounds use each cell's complete HOLD cohort.
  Descriptive comparisons with mixed cohort sizes use the common path-key
  prefix. Their inference JSON records the individual and paired sizes,
  index range and HOLD phase digest. Confirmatory contrasts use the complete
  realized P_CONF cohort. The HOLD trial summary records the contributing
  block keys and the SHA-256 of their ordered key/hash pairs.
- R4 uses the asymptotic Tango score interval and claims no exact finite-sample
  coverage. R5 conditions inference on fit 0. All staged NPZ files and
  published payloads of the allocated design must be smaller than 50 MiB.
