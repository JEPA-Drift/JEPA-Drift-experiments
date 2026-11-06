# Stream 23 phase 1 (E6): compatibility review against main, 2026-11-06

- Review reference: 23-review.
- Executable references: `prompts/GO-stream-23-review.md` and the integrated GO decision of
  `prompts/plans/plan-23-review.md`. Both are Codex files.
- Reviewed base: `20ad9e860a58373ec85405de6ee19a68322dd02e` on branch `review/stream-23-20261106`, equal to `main`.
- Historical branch: `stream-23` at `3d0bd2071cb86afc6b196b5020ff729204746a93`, forked from
  `2b0b1cd29bba1b1878d97b839110588e754a92b5`.

This review authorizes no merge, run or experiment. It does not presuppose integration or abandonment.

Evidence labels used below:

- **ARCHIVED**: a statement recorded in a historical artifact and not re-executed here. The artifacts are wrapup-23,
  `C-E6-phase1`, the stream 23 GO transcripts, commit messages, the 01–27 relevance audit and the review request.
- **PRESENT**: re-verified on 2026-11-06 by non-mutating Git commands, targeted reads, or venv Python reading Git blobs
  and parsing source ASTs.
- **STATIC**: an inference from source text (diff or AST). It says nothing about runtime behaviour.
- **NOT EXECUTED**: would require a run that the mandate forbids. Nothing labelled this way is certified.
- **HYPOTHESIS**: an interpretation that remains to be confirmed.

## Scope and sources

**Question.** Is there an E6 phase 1 that is compatible with the current `main` and still useful to integrate, and if
so under which exact conditions?

**Objects.** The two commits unique to `stream-23`:

- `7e4c7a1`: feat, E6 phase 1 with P1-D and P3-D;
- `3d0bd20`: fix, editorial correction of the D6 onset wording and of the CI criterion.

Together they touch 13 paths: the script, its configuration and tests, the CSV, four figures, `docs/DEVIATIONS.md`,
plan-23, GO-stream-23, GO-stream-23-audit and wrapup-23.

**Sources.**

- Historical objects, read with `git show stream-23:<path>` and `git show 7e4c7a1:<path>`: the 13 paths above, read
  without the historical worktree `../JEPA-stream-23`.
- Files at `HEAD`:
  - `CLAUDE.md` and `prompts/streams/prompt-23-e6.md`;
  - row 23 of `docs/audits/streams_01_27_relevance_2026_11_06.md` (file line 53);
  - the `docs/DEVIATIONS.md` entries `C-pipe-delay`, `C-P4D-null-insample`, `C-e3-d8-fail` and
    `C-pca-predictive-rank`;
  - the full PCA benchmark: `docs/sections/pca_drift_benchmark.md`, `configs/pca_drift_benchmark.yaml`, targeted
    lines of `experiments/pca_drift_benchmark.py` and the tracked `results/pca_drift_benchmark/` file list;
  - the `jepadrift/` sources, parsed as ASTs.

**Method.**

- Git: `rev-parse`, `log`, `rev-list`, `merge-base`, `merge-base --is-ancestor`, `branch --contains`, `diff`, `show`,
  `cat-file`, `ls-files` and `check-ignore`. No checkout, stash, reset, clean, rebase, merge, cherry-pick or
  merge-tree was run.
- Python: `.venv/bin/python` with OMP, MKL and OPENBLAS threads set to 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`
  and `MPLBACKEND=Agg`.
  - Blobs are read through `git show`.
  - The CSV is parsed with `pandas.read_csv(..., float_precision="round_trip")`, and as text with `dtype=str`.
  - Sources are parsed with `ast.parse`. No module of `jepadrift` or `experiments` was imported or executed.
  - The check script lived in the session scratchpad, outside the repository, and ended with exit 0.
- No return panel was read. Input identity relies on Git blob ids only.

## Verification matrix

| ID | Item | Evidence | Result on 2026-11-06 | Reading |
|---|---|---|---|---|
| V1 | Commits unique to `stream-23` | PRESENT | `HEAD..stream-23` holds exactly `7e4c7a1` and `3d0bd20`. Neither is an ancestor of `main`, and `stream-23` is the only branch containing `7e4c7a1`. Fork point: `2b0b1cd`. `rev-list --left-right --count HEAD...stream-23` gives 36 / 2: 35 commits up to `a0c576e` (the count of the 01–27 audit), plus `20ad9e8`. That commit touches only prompts, wrapup 31, the 01–27 audit, `tools/check_prompts.py` and its test | Confirmed |
| V2 | Sealed hashes | PRESENT | Each SHA-256 recomputed from the blobs equals the hash recorded in the wrapup-23 version of the same commit. **At `stream-23` (= `3d0bd20`):** CSV `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249`; `e6_phase1_delays.png` `ca929eee…e897`; `e6_phase1_delays.pdf` `cdffaf9e…c811`; `e6_phase1_gadd.png` `f14e06cb…4113`; `e6_phase1_gadd.pdf` `1ed21dc6…570b`; `configs/e6.yaml` `ca74d2e1…bcf5`. **At `7e4c7a1`:** CSV `1d16e6bd…b452`. Figures and configuration are byte-identical between the two commits; the script and the test differ. The quick-run hashes (`874be212…`, earlier `c3a6acc2…`) are ARCHIVED only, since quick outputs are not in Git | Confirmed |
| V3 | CSV schema | PRESENT | 190 rows × 50 columns; the header equals the script's `COLUMNS` constant (AST). D6 has 78 rows: 6 null rows (family `H0`) and 72 drift rows. D5 has 112 rows: 16 null rows (8 under the calibration-panel rule, 8 under `d6_rule_on_fit_panel`) and 96 drift rows. Compared as text, `7e4c7a1` and `3d0bd20` differ only in `ci_reason`, on exactly 72 rows, all of them D6 drift rows | Confirmed |
| V4 | Inputs | PRESENT (blob ids); ARCHIVED (hash prefixes) | `data/derived/d3_239/ret_wide.npy` and `splits.yaml` have one blob id each across `2b0b1cd`, `HEAD` and `stream-23`. Since the fork, the only change under `data/derived/d3_239/` is the added sidecar pair `z_55a11b75….{json,npz}`. wrapup-23 records the input prefixes `a266fbab…` and `3f3a65ba…` | Inputs unchanged |
| V5 | Imports and symbols | PRESENT (AST) | All 20 library roots that the script and test reference exist at `HEAD`. Of the 87 definitions they reach: 77 unchanged, 9 changed, 1 added after the fork (details in the next section). Byte-identical since the fork: `monitors/{cusum,gamma,streams}.py`, `floors.py`, `sim.py`, `representations/pca.py`, `stats/covariance.py`, `data_loader/{sp500,articleB}.py`, `Makefile`, `conftest.py`, `requirements.txt`, `requirements.lock` and `tests/test_decoupling.py`. `ENERGY_DELTA` (0.5) and `TARGET_FPR` (0.05) are unchanged | Statically compatible |
| V6 | Pipeline calls | STATIC | Every changed node is reached by E6 only through arguments that leave the fork's computation unchanged (table in the next section) | Static compatibility only; dynamic behaviour NOT EXECUTED |
| V7 | Determinism | STATIC; ARCHIVED | Every `default_rng` wraps a `SeedSequence` keyed on `STREAM = 23`: D5 panels `[23, role, i]` (role 0 fit, 1 calibration, 2 test); cell injection `[23, 6]`; bootstrap `[23, 4, ci, H]`; i.i.d. and fit keys passed as `key`. There is no global NumPy RNG and no stdlib `random`. The CSV is written by `pl.save_fair_csv` and the figures by `savefig` from the CSV. Process pools use `spawn`. ARCHIVED (wrapup-23): two full runs were identical, the quick run was identical with `--jobs` 1 and 48, and `test_cli_tiny_deterministic_across_jobs` exists | Determinism documented; not reproduced on `HEAD` |
| V8 | Thresholds and delays | PRESENT (reads) | Detailed under « Conventions » below the table | Delay and RMST conventions coincide; threshold rules differ |
| V9 | Overlap with the full PCA | PRESENT (reads) | Detailed under « Overlap with the full PCA » below the table, and in the utility section | Partial scenario overlap; no detector duplicate except the index comparator |
| V10 | Helper duplicates | STATIC | `e6.wilson` computes the closed-form Wilson interval with `math.sqrt`. `jepadrift/stats/intervals.wilson`, absent at the fork and added by stream 27, calls statsmodels `proportion_confint` and clamps the interval to contain k/n. Their numerical equality was not evaluated (no execution). `e6.iid_threshold` repeats the λ_iid construction that `pipelines._cal_p3d` performs inline; E6 needs it only for P1-D (D = 1), which has no pipeline entry, and takes the P3-D values from the fitted states. This review did not search exhaustively for other duplicates | Keep `e6.wilson` verbatim unless a GO orders harmonization under C3 |
| V11 | Git integration | PRESENT (paths); NOT EXECUTED (merge) | Only `docs/DEVIATIONS.md` changes on both sides. The base file has 458 lines and ends with `C-stats-drift`. `stream-23` appends `C-E6-phase1` (524 lines in total), while `HEAD` appends 39 entries (1159 lines). No other path of `stream-23` exists at `HEAD`. `HEAD` ignores `logs/`, which holds the E6 log, but not `results/e6_quick/` | A three-way merge would predictably conflict there; no merge was simulated, so this conflict is not reproduced |
| V12 | Cost | ARCHIVED (times); PRESENT (sizes) | Times from wrapup-23 (2026-10-22/23, 48 cores): full run 41 s; quick run 30 s (62 s with `--jobs 1`); `tests/test_e6.py` 13 tests in 8 s; `make check` 3 min 08 s (263 passed, 8 skipped). Sizes from `git cat-file -s`: 12 new files totalling 900,628 bytes, including 687,198 bytes of figures, and `docs/DEVIATIONS.md` +66 lines. The current baseline (37 + 545 passed, 5 skipped) is recorded by the review request, not re-run here | Low historical cost; times not re-measured |
| V13 | D6 FPR | PRESENT (CSV); ARCHIVED | All 78 D6 rows have `in_sample` = True, `ci_method` = `none` and threshold rule `calib_windows_in_sample`. The 6 D6 null rows have FPR 0, no FPR interval, and `ci_reason` equal to the script's `IN_SAMPLE` text. Thresholds are identical at H = 250 and 500: 36.090 (P1-D), 172.494 (P3-D factor, K = 10), 182.869 (P3-D full). `tie_share`, the next attainable in-sample level, is 0.277, 0.243 and 0.237 at H = 250, and 0.566, 0.525 and 0.502 at H = 500. The 72 D6 drift rows are exploratory and carry no G_ADD interval | D6 keeps a descriptive diagnostic role, without independent FPR |
| V14 | Ten-block rule | PRESENT (CSV) | Each of the 72 D6 drift rows states the « conservative prespecified reporting criterion of the protocol (plan-23, Q5), not a general requirement of a block bootstrap or a deff », with 2.77 blocks (H = 250) or 0.88 blocks (H = 500). None of them cites Künsch or Lahiri; all 72 did at `7e4c7a1` | A prespecified reporting criterion, not a universal deff requirement |
| V15 | PC1–PC2 contrast | PRESENT (CSV); ARCHIVED and STATIC readings | D5, H = 250, θ = 15°, 30°, 45°: P1-D detection rates are 0.040, 0.024 and 0.006, below its attained null FPR of 0.048. P3-D factor with K = 1 detects in every run, with G_ADD 14.59 [13.84, 15.42], 67.71 [65.10, 70.35] and 105.42 [102.04, 109.07], all labelled `lower_bound`. Three readings follow. (i) The ratio is bounded below by P1-D's blindness: its one-sided energy CUSUM does not respond to the variance decrease of the equal-weighted index (ARCHIVED, wrapup-23 vigilance 6). (ii) With K = 1 the monitored residual is PC2, a member of the rotated pair, so the cell aligns the channel with the drift by construction (STATIC). (iii) The PCA is fitted by `fit_pipeline` on the rows declared `calib`: the 941 D6 calibration days, or the 941-day D5 fit panel of seed role 0 | Measures neither JEPA nor the superiority of a trained encoder; no learned-representation gain is claimed |
| V16 | D8 and P4-D | PRESENT (reads) | At `HEAD`, `C-e3-d8-fail` keeps the D8 gate FAIL (relative gap +0.0528 > 0.05 on `iid/first_order_d1_l3`, archived without rerun). `C-P4D-null-insample` records that the D6 null check of P4-D re-reads its calibration windows (0 alarms in 500) | P4-D stays outside calibrated J4 comparisons and outside E6; D8 is unaffected |
| V17 | Phase 2 | PRESENT (reads) | The E6 CLI refuses `--phase 2` with « phase 2 (P5-D, even head of CA-T-JEPA) waits for stream 16 ». The 01–27 audit records stream 16 as `À_REPLANIFIER`, with no campaign and no trained model | P5-D and any J4 contribution stay blocked; out of scope |

### Conventions (V8)

**E6 (STATIC, from the script).**

- Monitors: strict one-sided CUSUM with δ = 0.5 on both energy streams.
- Threshold λ: the smallest value whose calibration FPR at horizon H is ≤ α, found by bisection
  (`required_threshold(..., "fpr", H)`). It is taken on the D6 in-sample windows, or on 2000 D5 calibration panels,
  where it admits up to ⌊α n⌋ = 100 calibration alarms.
- Delay: offset + 1, in [1, H] (`C-pipe-delay`). Censored runs count as H in RMST_H.

**Full PCA (PRESENT, from the section document and `C-pca-predictive-rank`).**

- δ = 0.5 applies only to its energy CUSUM comparator (ENERGY family, Page CUSUM, alarm S_t > λ). The mean mixture
  scan and the covariance vech scan use s2 = 2 ln(H/α)/(H p) and no δ.
- Thresholds follow `predictive_exchangeable_rank_v2`: r = ⌊α(n + 1)⌋ − 1 = 99 at n = 2000, with the marginal bound
  (r + 1)/(n + 1) under exchangeability.
- `first_hit` is 1-based, alarm day included. `censored_time` = H without alarm. RMST is the mean of `censored_time`,
  with deff = 1 for independent paths.

### Overlap with the full PCA (V9)

- The published full run (`full_2000_20261101` manifest) is synthetic only: datasets `SYNTH_GAUSS_EQUICORR` and
  `SYNTH_T7_EQUICORR`, with no D3_239 rows.
- Backgrounds: i.i.d. equicorrelated rows, ρ = 0.4, N = 239, H = 250.
- Basis: a frozen Ledoit-Wolf PCA fitted on an independent fit sample (T_fit = 1000).
- Scenarios:
  - mean drifts `A_market_mean` and `C_residual_mean`;
  - one covariance drift, `B_cov_rotate30`, injected by `injection.inject("F4-rotate")` with the configured
    `rotation_pair: [1, 2]`. The script converts these 1-based indices to (0, 1) (`pca_drift_benchmark.py`
    l.1007–1010), so the drift is a PC1–PC2 rotation at 30°.
- Detectors on the rotation: covariance vech scans on PCA subsets (prefixes, oracle subsets and diagnostic subsets),
  and the `ENERGY_INDEX_COMPARATOR`, which the full defines for its covariance scenario only. The comparator stream is
  `monitors.streams.energy_stream(m, mean, std)` = (m_t² − mean)/std, with mean and std (ddof 0) of the squared
  equal-weighted index m on the fit rows: the same stream definition as E6's P1-D.
- There is no residual-energy CUSUM analogue of P3-D.
- Axis-convention trap: E6 `pair: [1, 2]` is 0-based and means PC2–PC3, whereas the full's `rotation_pair: [1, 2]` is
  1-based and means PC1–PC2.

## Static comparison of the code paths reached by E6

**Method.**

- Roots: the 20 library symbols referenced by `experiments/e6_second_order.py` and `tests/test_e6.py`.
- Closure, computed on the `HEAD` sources: each reached definition contributes every module-level name it references,
  followed through `from jepadrift… import` statements and module aliases. Registries keyed by pipeline (`DEFAULTS`,
  `READINGS`, `PIPELINES`) are restricted to their `"P3-D"` entry, the only pipeline E6 uses.
- Comparison: each reached node is compared with its counterpart at `2b0b1cd` by `ast.dump`, after docstrings are
  stripped.
- Result: 87 definitions, of which 77 are unchanged. The ten nodes below are the 9 changed definitions and the one
  added after the fork.

| Node at `HEAD` | Change since the fork | Argument reached from E6 | Static reading |
|---|---|---|---|
| `pipelines.split_rows` | Optional `C` aligned with the dates, stored under `"C"` | `load_d6` passes no `C` | Same dict as at the fork |
| `pipelines.make_spec` | Single-channel check of the exact reading extended to P4-C | `"P3-D"` with the bootstrap reading | Branch not reached |
| `pipelines._panel` | `missing` flag admits NaN when True; new error text | `missing` = False: `PCAOrthogonal` inherits `Representation.missing = False` | Same acceptance set (finite values) |
| `pipelines._window` | Forwards `missing` to `_panel` for panel data | E6 passes a Z dict to `run_pipeline` | The dict branch returns before `_panel` |
| `pipelines.fit_pipeline` | Builds the representation first; optional `pretrain` hook; passes `_rows(C, …)` to `fit` | No `"C"` in the E6 splits (D6 from `split_rows`, D5 from a literal dict). Only `IPCA` defines `pretrain` | `rep.fit(X_calib, None, dates)`, as at the fork |
| `pipelines._cal_p3d` | Passes `_rows(splits.get("C"), …)` to `transform_panel` | No `"C"` | `transform_panel(X, None)`, the fork's default |
| `injection.inject` | Optional validated `params["fit"]`, and `params["sr_asset"]` | E6 cell params hold `calib` plus either `subspace, r` or `pair, theta_deg`. F4 returns through the unchanged `_second_order` before the `sr_asset` branch | `fit_background(X[calib], K)`, as at the fork |
| `representations.base._check` | `missing` flag | False for `PCAOrthogonal` | Same acceptance set |
| `representations.base.Representation` | Class attribute `missing = False`, forwarded to `_check` | Inherited by the unchanged `PCAOrthogonal` (`pca.py` is byte-identical) | Same behaviour on finite panels |
| `representations.extract._rows` (added) | Returns None for None, otherwise a contiguous slice | Called with None | Returns None |

At `HEAD`, `jepadrift.pipelines` also imports `data_loader.chars` and `representations.ipca` when it loads. They are
not on E6's computational path. The baseline `make check` recorded by the request imports `pipelines` in this worktree
layout (ARCHIVED for this review).

## Compatibility verdict

The verdict is composite, as required by the GO (Q1).

- **Static compatibility: compatible under conditions.** Every symbol is present, and 77 of the 87 reached
  definitions are unchanged. On static reading, the ten changed or added nodes are reached by E6 only through branches
  whose inputs leave the fork's computation unchanged. Those inputs are: no `C`, `missing` = False, no `pretrain`
  hook, no `fit` parameter, Z-dict windows and the F4 early return.
- **Reproduction: not executed.** No E6 run, test or `make check` took place on `HEAD`. The AST comparison certifies
  neither reproduction nor dynamic compatibility. Byte identity of the CSV after integration remains a HYPOTHESIS
  (H-repro), testable only under a new GO (C3).
- **Git:** one predictable textual conflict in `docs/DEVIATIONS.md`, not reproduced. No other path collides.
- **Scientific labels: unchanged and binding.**
  - D6 is an in-sample descriptive diagnostic, without independent FPR and with IC=NA.
  - D5 is conditional on a single fit panel: λ_D5 changed about threefold between two fit panels (ARCHIVED).
  - The information is the Gaussian design value, not the exact KL of the t7 or D6 backgrounds.
  - The PC1–PC2 contrast is not a learned-representation gain.

## Utility versus the full PCA benchmark

| Dimension | E6 phase 1 | Full PCA (`full_2000_20261101`) | Overlap |
|---|---|---|---|
| Backgrounds | D6: `d3_239` calibration windows, in-sample. D5: GARCH(0.08, 0.90)-t7 equicorrelated panels, ρ = 0.40, N = 239 | i.i.d. equicorrelated Gaussian and t7, ρ = 0.4, N = 239 | Equicorrelation and N only |
| PCA fit | `PCAOrthogonal` (Ledoit-Wolf) fitted on the `calib` rows (D6) or on the role-0 fit panel (D5). K from Marchenko–Pastur on D6 (10); on D5, K = 10 conditional and K = 1 as a sensitivity | Frozen Ledoit-Wolf PCA on an independent fit sample; prefixes k ≤ 20 and information-selected subsets | Different designs |
| Drifts | F4 rotations of PC2–PC3, PC1–PC2 and PC2–PC12 at 15°, 30° and 45°; deformations of PC2–PC4 with r = 1.25, 1.5 and 2 | Mean drifts A and C; one rotation, PC1–PC2 at 30° | One cell (`rotate_pc1_pc2_30`) |
| Monitors | P1-D: energy CUSUM of the equal-weighted index. P3-D: residual-energy CUSUM, factor or full | Mean mixture scan; covariance vech scan; energy comparator of the equal-weighted index | P1-D ≈ the energy comparator (same stream definition) |
| Horizons | H = 250 and 500 | H = 250 | H = 250 |
| Thresholds | Empirical calibration FPR(H) ≤ α | Predictive exchangeable rank, version 2 | None |
| Delay metric | RMST_H with censoring at H; G_ADD as an RMST ratio with a paired bootstrap on D5 | RMST of `censored_time` (= H when censored); normal CI with deff = 1 | Definitions coincide |

- **Complementary coverage.** E6 covers second-order F4 situations that the full does not: deformations, GARCH-t7, H =
  500, the contrast between K values, the PC2–PC3 negative control and PC2–PC12.
- **Limited overlap.** The shared cell is a scenario overlap (PC1–PC2 at 30°, with an index-energy comparator). The
  detectors and threshold rules differ, so the results are not duplicates and must not be pooled.
- **Current utility: complementary, non-critical.** No written request or GO requires E6 phase 1 at this date, and
  the 01–27 audit records `DIFFÉRER`.

## Exact conditions for a later integration (future, non-executory)

**Trigger (Q5).** A new targeted GO may follow one of three written events:

- a request for a linear F4 diagnostic absent from the full;
- a need to cite E6 linear F4 results in Article C or J4;
- the planning of phase 2 after stream 16.

No trigger authorizes an execution under the present mandate.

**Conditions.**

- **C1.** Work in a new isolated worktree created from `origin/main`, and apply `7e4c7a1` then `3d0bd20` there.
  `../JEPA-stream-23` and branch `stream-23` are never modified.
- **C2.** In `docs/DEVIATIONS.md`, append `C-E6-phase1` (the `3d0bd20` text) at the end of the file with an
  integration note. The existing entries of `main` stay unchanged.
- **C3.** Rerun phase 1 in full and quick mode under `.venv` with the project environment variables. Required hashes:
  CSV `4101c867…d249`, quick CSV `874be212…`, and the four figure hashes of wrapup-23. Any difference is a D3
  deviation: stop, and correct nothing. The quick output directory `results/e6_quick/` is not ignored and stays out of
  any commit.
- **C4.** `tests/test_e6.py` gives 13 passed, then the full `make check` passes. The current baseline already exceeds
  the five-minute target.
- **C5.** No P4-D or P5-D addition and no J4 contribution. The labels of the verdict above stay unchanged.
- **C6.** `e6.wilson` stays verbatim unless the GO orders harmonization under C3. The 0-based versus 1-based axis
  convention is documented wherever E6 and the full are cited together.
- **C7.** Codex applies the project push rules: pushed range, EUROFIDAI paths, 50 MB limit and anonymity.

## Recommendation

**Preserve and defer.**

- Keep branch `stream-23` (`3d0bd20`) and the worktree `../JEPA-stream-23` intact.
- Do not integrate, rerun or open a new GO now.
- Reopen only on a written trigger, through a new targeted GO that carries C1–C7.

This is not abandonment: phase 1 is a sealed, traceable and statically compatible deliverable, with second-order
coverage that the full does not provide.

**For a later integration:**

- static compatibility;
- unchanged inputs;
- low historical cost (times from wrapup-23, not re-measured);
- second-order coverage that no current experiment provides.

**Against an integration now:**

- the reproduction is not executed;
- the `DEVIATIONS.md` conflict needs a separate GO;
- D6 stays a descriptive diagnostic without independent FPR;
- D5 is conditional on one fit panel;
- the PC1–PC2 contrast is bounded by P1-D's blindness and by channel alignment, and its scenario overlaps the full;
- stream 31 has priority, and JEPA and J4 stay excluded.

**Distinctions kept, whatever the decision:**

- 0-based versus 1-based axes;
- in-sample versus independent nulls;
- static compatibility versus reproduction;
- historical versus current times;
- linear F4 results versus JEPA results.
