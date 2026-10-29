# Wrapup — stream 12: E1, the detection problem on D6 backgrounds, pipelines 1 -> 2 -> 3 -> 3-CS and the J2 criteria

## Context

- Stream 12 (E1, Article C section 2), worktree `stream-12` from `c284823`, under the GO of 2026-10-28 transcribed
  verbatim in `prompts/GO-stream-12.md` (the GO of 2026-10-18 is kept there as a superseded specification) and the
  executed plan `prompts/plans/plan-12.md` (integrated GO decision, delta revision 2, revision 1).
- MCP servers reloaded and called before implementation and again at closure: graphify `graph_stats` (3,506 nodes,
  4,218 edges), jcodemunch `resolve_repo` (repository indexed, loadable).
- Interpreter `.venv/bin/python`; OMP/MKL/OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42,
  MPLBACKEND=Agg. Real rows read: 2005-01-04..2019-12-31 only (D2 rows [0, 3774), D3 absolute rows [1257, 5031)).
- Shared-code changes accepted by the GO (Q2): `inject` takes `params["fit"]` and `params["sr_asset"]`
  (C-e1-inject-cache); `cross_independence` is a Holm gate at family level 1 % (C-e1-holm-gate); `spy_phases`,
  `char_directions`, `projections`, `subspaces`, `N_PC`, `MAX_DIM` moved verbatim to `jepadrift/stats/drift.py`
  (C-e1-drift-move). Q10: F2 injected on `c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21` (C-e1-f2-chars).

## Validated Results

Full run, executed once: `.venv/bin/python experiments/e1_problem.py --jobs 24 --out results/e1 --fig-dir figures/e1
--log-dir logs/e1`, 3,118.7 s, exit 0 (blocks: J2I 13.8 s, A 279.2 s, S 169.5 s, G 750.3 s, B 1,212.9 s, C 690.9 s).
SHA-256 of the outputs (identical to the `sha256` lines of `logs/e1/e1.log`):

| file | rows | SHA-256 |
|---|---|---|
| `results/e1/e1_cells.csv` | 1,114 | `9ae7e261aada263c29fc446f3d3ad17577d9bbe553804db76069e423268cb8f3` |
| `results/e1/e1_slopes.csv` | 1,833 | `1a3a286c47a21d0124fbe8737436dd9fe2c58222146541a880cadb63992cd93c` |
| `results/e1/e1_real_phases.csv` | 66 | `9def4b35df1844e9369d1b1b05acfed6e7d06cd8494861086fa26e2411cc7346` |
| `results/e1/e1_null.csv` | 54 | `6ae5770c3265a27ccf4e83003705a38ed8a336a05352865bd4ee8dab1009353f` |
| `results/e1/e1_j2_summary.txt` | 20 lines | `a949acdca169c66ffbe1e7845641c9358955faa112df4b1194f71bf8fd3243a7` |

Figures (from the CSVs): `figures/e1/{e1_j2i_fpr,e1_arm_a_delays,e1_arm_b_slopes}.{png,pdf}`.

J2 criteria (`results/e1/e1_j2_summary.txt`):
- **J2(i) PASS.** 54 exact sign-stream controls (P1-C on `composition_for(5, N)`: D2 COST, SHW, SO, MDLZ, PSA; D3 CASY,
  KEY, GPC, ERIE, LRCX; the exact P3-C channels of the frozen factor basis, 6 on D2 and 11 on D3; H in {750, 2000}),
  2,000 replicates each, primary keys `[12, crc32("full|j2i|<dataset>|<H>")]`: 0 failures, max |FPR - lattice level| =
  0.00917 (tolerance 0.01), Holm 1 % rejections 0, outside the 99 % region 0. Drawn once, no rerun, no reseeding. The
  joint false-FAIL probability 0.813 and the 1.65 expected false FAILs are a priori computations conditional on exact
  sign streams and independent null draws (key lineage in C-e1-j2i: no entropy tuple shared between controls or
  replicates; the panel and the frozen basis are shared but deterministic), not observed probabilities.
- **J2(ii) PASS.** Slope of log G_ADD,H(P1 reference -> P2-C) on log N, F3, N >= 20: D2 0.001 [-0.039, 0.036]
  (per-asset SR 2), 0.003 [-0.041, 0.045] (SR 4); D3 0.102 [-0.016, 0.311], 0.063 [-0.039, 0.225].
- **J2(iii) PASS.** Slope of log G_ADD,H(P1 reference -> P3-C full) on log N, F2 on D3: 0.169 [0.141, 0.197]
  (kappa 2), 0.175 [0.138, 0.218] (kappa 4); the P1 reference is constant in N (slopes -0.000 [-0.016, 0.019] and
  -0.031 [-0.073, 0.014]); P3-CS (b) 0.165 [0.139, 0.194] and 0.160 [0.122, 0.206]; mixture where the Holm gate passes on
  the subset 0.265 [0.181, 0.352] (44 cells) and 0.321 [0.160, 0.483] (45 cells).
- **J2(iv) PASS.** Table 1 -> 2 -> 3 -> 3-CS at SR = 4 complete for the 5 (dataset, family) pairs with paired 95 % CIs,
  predictions or the label `not_directly_interpretable`.

Arm A, SR = 4, H = 2000, anytime-valid readings at gamma_H = 40,000 (add_h in days, detection rate in brackets; P1-C =
median asset): D2 F3 1090 (0.976) -> P2-C 548 (1.000) -> P3-C 599 (1.000) -> P3-CS (b) 1998 (0.001, no information) ->
P7 270; D2 F1 1805 (0.276) -> 1659 (0.395) -> 791 (0.996) -> 848 (0.954) -> 292; D3 F3 1297 (0.909) -> 623 -> 709 ->
1998 -> 255; D3 F1 1955 (0.075) -> 1880 (0.183) -> 908 (0.976) -> 900 (0.967) -> 304; D3 F2 1998 (0.001) -> 2000 ->
1998 (0.003) -> 1998 (0.003) -> P7 97. G_ADD,H at SR = 4: D2 F3 P1-C -> P2-C 1.988 [1.929, 2.051], P2-C -> P3-C 0.915
[0.897, 0.934]; D2 F1 P2-C -> P3-C 2.097 [2.023, 2.174]; D3 F3 2.082 [2.018, 2.152] and 0.879 [0.863, 0.896]; D3 F1
P2-C -> P3-C 2.071 [2.006, 2.137]; D3 F2 all ratios 1.00 (every non-oracle pipeline censored).

G_ADD,ex (exact readings at the same lattice level, P1-C median -> P3-C market channel for F3, best channel for F1/F2,
oracle): D2 F3 SR 4 2.515 [2.381, 2.652]; D3 F3 SR 4 2.699 [2.566, 2.847]; every cell is `equal_fa_not_shown` (the
paired 95 % interval of the H0 difference exceeds the +-0.01 margin at 1,000 H0 replicates).

G_SR (smallest SR detected within H with probability >= 1/2; 6 bisection steps of 200 onsets): D2 F3 P1-C 2.71, P2-C
1.61, P3-C 1.92, P3-CS (b) censored above 64, P7 1.35; D3 F3 2.95, 1.76, 2.09, censored, 1.24; D3 F2 P1-C 56.2, P2-C
censored, P3-C 19.87, P3-CS (b) 19.87, P7 0.74.

Attained FPR under the paired H0 arms (1,000 replicates per cell): P1-C exact 0.0461 (H = 2000, level 0.0457) and
0.0441 (H = 750, level 0.0439); P3-C exact 0.0455; anytime-valid e-detectors 0.0000-0.0016; P3-CS (a) at gamma = 20
0.016; P2-C bootstrap (R15 port) 0.003-0.170 (mean 0.068); P3-D 0.24-0.93.

Arm C (descriptive, upper bounds, `alignment_upper_bound_not_causal`): market budget shares 0.67-1.00 against
placebo means 0.02-0.06 (p <= 0.002) on both datasets and the three datings; residual_full 0.33-0.50 against
0.10-0.14; raw alarm shares at gamma_L = L / alpha: P1-C label stream 0.000-0.015, P3-C factor (recentred on the
rejected channels: D2 PC1, PC3; D3 PC1-PC3) 0.000. `results/audit/predicted_gains.csv` cited as is (SHA-256
`ac2568ae6c7136d557c66ff24ee57361cdcbf4c65dcb98a8ac233a831ba615e4`, NaN kept).

Determinism: the quick runs with `--jobs 8` and `--jobs 1` are byte-identical on the four CSVs and the summary, and the
quick run after the loader correction is byte-identical to both. Loader correction: the selected rows and arrays equal
the former selection on both datasets (SHA-256 of X, dates and rows: d2_us97
`55013c904019259b5ac6b498c7de327e5d8b34160a0a30718af66f0a3f9b14d3`, d3_239
`9047dfb6fb2c281b12dbb7794344a2eba3c10327c91560fb53745d2f010053bc`), so the full run was not repeated.

Tests: `tests/test_e1.py` 18 passed (window and loader guard with inserted dates, five assets of E3, refusal of
`--include-test-window`, CUSUM and e-detector reset at the onset, prefix invariance at each onset, phase reset, J2(i)
risk 0.0293 / 0.0319 / 0.813, delay summaries and censoring labels, chain references, F3 market column and full
information, sign efficiency with the Silverman bias, slope interval, arm C shares equal to `budget_share.csv` on D2,
CLI determinism across `--jobs`, 54 controls on the frozen basis); `tests/test_injection.py`, `tests/test_pipelines.py`
53 passed; `tests/test_drift_stats.py`, `tests/test_decoupling.py` 9 passed; `tests/test_audit.py` 31 passed;
`audit_information.py --quick` CSVs byte-identical before and after the move (9 files). `make check` (with the
loader correction): pyflakes clean, contracts and decoupling 22 passed / 4 skipped, suite 262 passed / 4 skipped in
228 s; `git diff --check` clean.

## Errors and Dead Ends

1. `pipelines.null_check` refits each P3-C spec on a symmetrization; its Marchenko-Pastur count gives 10 factor
   channels on d3_239 instead of 11, which crashed the first quick run (channel 10) and would have left 52 controls.
   Fixed before any primary draw: the J2(i) P3-C controls use the frozen raw-calib basis with the `null_check` loop.
2. The first `--jobs 1` quick run failed because my command chain removed its output directory while it ran; rerun.
3. `tests/test_audit.py` failed once (sidecar hash of the calib basis) while `audit_information.py --quick` ran
   concurrently with 8 processes; the rerun passed 31/31. Not reproduced.
4. The sign-efficiency test first assumed e = 2/pi; the Gaussian-kernel estimate carries the smoothing factor
   1 / (1 + h^2); the test states it.
5. `load_window` filtered on the window before `check_window`, which made the guard vacuous; corrected (explicit
   official split and D3 exclusion, gap and order checks), outputs unchanged.
6. The `dataviz` skill of the plan was not loaded before the plotting code (budget); the E10 palette is reused.

## Current State

- New: `experiments/e1_problem.py`, `configs/e1.yaml`, `tests/test_e1.py`, `results/e1/*`, `figures/e1/*`,
  `prompts/plans/plan-12.md`, `prompts/wrapups/wrapup-12.md`. Modified: `jepadrift/injection.py`,
  `jepadrift/pipelines.py`, `jepadrift/stats/drift.py`, `experiments/audit_information.py`, `tests/test_injection.py`,
  `tests/test_pipelines.py`, `tests/test_drift_stats.py`, `tests/test_audit.py`, `docs/DEVIATIONS.md` (C-e1-*),
  `docs/sections/injection.md`, `docs/sections/pipelines.md`, `prompts/GO-stream-12.md`.
- Local and ignored: `logs/e1/e1.log` (full run); the quick artifacts are preserved under `logs/e1/quick_jobs8/`,
  `logs/e1/quick_jobs1/` and `logs/e1/quick_after_loader_fix/`.
- One local commit on `stream-12`; no fetch, rebase, merge or push.
- `tools/reindex_graphify_jcodemunch.sh`: `graphify update .` rebuilt the AST graph (3,773 nodes, 4,647 edges);
  `jcodemunch-mcp index` failed ("Both local and git identity indexes already match this path"). No index was deleted,
  since the git-identity index may be shared with the parallel worktrees; the MCP still resolves the repository with
  its 2026-10-23 index, stale for the stream 12 files.

## Vigilance Points

- P2-C bootstrap (R15 port) is calibrated on one symmetrization: its null maxima depend on that day-sign path, and
  its attained FPR on D6 ranges 0.003-0.170; it carries no fixed level on D6 and stays secondary.
- P3-D null rates 0.24-0.93: the energy stream is not symmetrized and its windows are calibrated on the calm
  2016-2019 calib rows (same mechanism as the stream 17 P4-D/P3-D finding); descriptive only.
- F2 under convention (a) is not detected within 2,000 days by any non-oracle pipeline for SR <= 8, while P7 detects it
  (97 days at SR = 4): its information spreads over about 238 residual directions.
- The Holm gate fails on D2 factor (p_min 6.0e-5) and on D3 factor and full (p_min 4.7e-44): no mixture reading in arm
  A; arm B has mixture cells only where the gate passes on the subset.
- The arm B pilot moved kappa from {1, 2} to {2, 4} (kappa = 1 stays in the delay band only at N = 239); the F3
  amplitudes of the prompt are kept (C-e1-amplitude-grid).
- J2(i) maximum deviation 0.00917 against the 0.01 tolerance.
- Equal false alarm is not shown for any G_ADD,ex cell; every gain is at common nominal alpha.
- Predictions use e = 4 f(0)^2 with a downward smoothing bias of about 7 % at 941 calib days.
- Every cell is retrospective: the calib rows follow the onsets at H = 2000.
- Merge: append conflicts expected in `docs/DEVIATIONS.md` and `jepadrift/pipelines.py` (streams 13, 14, 17, 18, 23);
  E3 must keep the same five literal indices.

## Recommendations

- E3: assert the literal indices [24, 71, 56, 46, 75] and [60, 177, 141, 116, 184] in its tests.
- To claim equal false alarm for G_ADD,ex, size the paired H0 arm so that the 95 % interval of the difference fits
  within +-0.01 (about 4,000 replicates per cell).
- If the Article B bootstrap reading must carry a level on D6, calibrate it over fresh symmetrizations instead of one.
- Study the F2 gap between P7 and the dictionaries through a_max(N) before E5.
- Move the local delay helpers to `jepadrift/` after the merges of streams 12, 13 and 23.
