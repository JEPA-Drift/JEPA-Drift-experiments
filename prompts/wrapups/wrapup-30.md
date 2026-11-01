# Wrapup — stream 30 (30-PCA-FIGURE): `Figure_1_mean`, `Figure_1_cov`, `Figure_1_mean_t7` from the sealed smoke artifact

## Context

- Execution GO for stream 30 (researcher/supervisor), implementing `prompts/plans/plan-30.md` (plan GO
  `prompts/GO-stream-30.md`, ancestor G0 `6f9322b`). Implementer: Mistral Vibe `large-4`, thinking `high`, in worktree
  `~/JEPA-stream-30`, branch `stream-30`, no Git mutation of any kind (no add/commit/push/rebase/merge/checkout); closure
  (reindex, `make check`, staging, commit, push) is left to the operator.
- Scope: `experiments/figures/plot_figure_1.py`, `tests/test_plot_figure_1.py`, `docs/sections/pca_drift_figures.md`,
  append-only French entry `C-pca-figures-design` in `docs/DEVIATIONS.md`, this wrapup, and the 17 outputs under
  `results/pca_drift_benchmark/figures/smoke_predictive_v2_closeout/`. Untouched: the runner
  `experiments/pca_drift_benchmark.py`, `experiments/pca_drift_tables.py`, `configs/`, `tools/`, `prompts/streams/`,
  `results/e2`, `results/e3`, the smoke input sources and the tables (verified by `git diff --quiet HEAD -- …`).
- Input: the sealed `/2` smoke artifact `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` (7 files, SHA-256
  verified against the plan §11.1 list; run_fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`)
  and its `pca_drift_tables/1` tables (`pdt.verify_output_dir` PASS, `tables_fingerprint`
  `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1`). E2 cells SHA-256 `e315e537…0823` on disk and in
  the index; `configs/FROZEN.json` absent. Environment: `.venv/bin/python` (Python 3.12.9, NumPy 2.4.4, pandas 3.0.6,
  matplotlib 3.11.2), thread vars at 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. The runner was never
  launched; no real return was read; no RMST/FPR was recomputed.
- Second corrective mission (2026-11-01): after visual inspection of the regenerated PNGs, two regressions were fixed:
  the RMST legend entries are now taken from the `ErrorbarContainer`s returned by `_errbar` (`ax_r.get_lines()` misses
  them), the H5 warning box moved to the lower-left of the top panel (`(0.04, 0.08)`, wrapped, clear of the axis line
  and ticks) with the full phrase kept on one line of the bottom text block, and the V axis top margin raised to
  `vmax * 1.20` so the selected curve clears the CPV90 annotation. Vertical margins rebalanced
  (`bottom=0.36, hspace=0.55`). The 17 outputs were regenerated and the full §12.1 sequence re-run green.
- Corrective mission (2026-11-01): after visual inspection reported critical graphic overlaps, the layout was reworked:
  two truly stacked panels with shared x, top panel as a full-width twin axis (`ax_v = ax_cpv.twinx()`), one merged
  top legend in the inter-panel gap, the bottom legend anchored below the x label (`bbox_to_anchor=(0.5, -0.30)`,
  `labelpad=2`), the descriptive text block as `fig.text` at the very bottom, the CPV90 annotation top-right of the
  full-width panel, the H5 warning box unwrapped at the bottom of the top panel. `render_checks` now also rejects any
  legend/axes, legend/x-label and figure-text/legend bbox overlap. All 17 outputs were regenerated (old output dir
  removed first) and the full §12.1 sequence re-run green.
- Gate G0 (plan §3, §12.1) executed programmatically and PASS: branch `stream-30`, `6f9322b` ancestor of HEAD,
  `experiments/pca_drift_tables.py` + `docs/sections/pca_drift_tables.md` present, `pdt.verify_output_dir(tables)` true.

## Validated Results

- TDD: `tests/test_plot_figure_1.py`, groups g1–g5, 39 tests. RED phase first (collection error
  `ModuleNotFoundError: No module named 'experiments.figures'`), then GREEN: **39 passed in ~90 s**; both phases and
  pyflakes (clean on both owned Python files) are recorded in `logs/pca_drift_figures/tdd.log`.
- Double execution with `--strict` into `results/…/figures/smoke_predictive_v2_closeout/` and into
  `logs/pca_drift_figures/repeat/`: **17 files, byte-identical octet per octet** (`cmp` on every file), same
  `figures_fingerprint` `fdb34c06bcbe1702803755ec83948a3345aedc163ecd9e77eb27258bf6b45aa7`. Re-invocation on the
  non-empty output is refused with exit 2 (`OUTPUT_NOT_EMPTY`, `logs/pca_drift_figures/refusal.log`). No `/home/` string
  in any output file. Round-trip test: re-rendering from `read_csv(⟨stem⟩_source.csv, float_precision="round_trip")`
  reproduces the SVG/PDF/PNG bytes exactly.
- In-process render checks (recorded in `FIGURE_CHECK.md`): text_in_frame PASS, legend_disjoint PASS, ylim_covers PASS,
  font_min 6.0 pt, PNG 1620×1050 (= 1050×1620 px at 300 dpi) PASS for all three figures; `strict checks: PASS`.
- External render checks (H11, results in `logs/pca_drift_figures/`): `pdftotext` finds `RMST250` and
  `model-based, not observed detection speed` in all three PDFs; `COV_SURROGATE_EXPLORATORY` present in
  `Figure_1_cov.pdf.txt` and absent from `Figure_1_mean` / `Figure_1_mean_t7`; `pdfinfo`, `pdftoppm -r 100 -png` and
  `rsvg-convert` previews generated (`Figure_1_*.pdf_preview-1.png`, `Figure_1_*.svg_preview.png`); programmatic sanity
  of the previews: ink coverage 0.09–0.15, expected shapes. **Visual inspection NOT PERFORMED by this CLI** (no image display); the non-collision is proven
  programmatically: `render_checks` PASS on all three figures (no legend/axes, legend/x-label or text/legend bbox
  overlap, all texts in frame, PNG 1620×1050) and the `pdftoppm`/`rsvg-convert` previews in `logs/` were regenerated;
  the operator performs the final human visual control citing the PNG SHA-256 below.
- Records (all `predeclared: true`, smoke): `mean` PRIMARY, tags `SMOKE_NO_CLAIMS, GAUSSIAN_PROXY`, claim_flags
  `ORACLE_INJECTED_DELTA`, 100 source rows; `mean_t7` ROBUSTNESS, tags + `T7_ROBUSTNESS`, 100 rows; `cov` PRIMARY, tags
  `SMOKE_NO_CLAIMS, COV_SURROGATE_EXPLORATORY, EXPLORATORY_HEURISTIC, DETECTOR_FAMILY_MISMATCH`, claim_flags
  `COV_SURROGATE_EXPLORATORY, HEURISTIC_COST, ORACLE_TRUE_SIGMA1`, 101 rows (energy row at k NA). `fpr_mismatch_k: []`,
  `missing_k: {}` on the three smoke entries (protocol identity P and Wilson overlap W hold at every k).
- SHA-256 of the deliverables after the second corrective pass (full list in `logs/pca_drift_figures/deliverables.sha256`):
  - `experiments/figures/plot_figure_1.py` `f2a0e7f0d014fa9301ce71ae276949e79c2e2f5e5e8256dd5603091a862bb048`
  - `tests/test_plot_figure_1.py` `40c07467178fb9c8f8423ee79328f16e3bb40a9123663febcfe4a084d62e93d4`
  - `docs/sections/pca_drift_figures.md` `b7711e2c314966ae0a1300e49fe936edf9a106e1b7afd83cb0d56600788c1998`
  - `docs/DEVIATIONS.md` `2c83037fda35f406a5660c9e33e7f50c0358f03e28e0870345a77ed886d68b30`
  - `results/…/Figure_1_mean.svg` `4a9c42649d8ffca6c0e9e0352cff78355aca6b0eb35f6e4feba557b822f97a0b`, `.png` `9d53b1f2f8db45073c8aa72da10f06fea56bf2c81f9dbc0caae8506278226a9d`, `.pdf` `64f1c2590342500e6d61f047d1b32aba8176c9ed5137a5933b076d7c42167b27`,
    `_source.csv` `c16347dc5ae9db2e7a707146273fc31fd3fd6a6f08ef77d189b575912ce8579d`, `_caption.md` `a9404e3dbff13d29aff1a7675d75054d825fbbcd8618282e9cf4046ae5b3680d`
  - `results/…/Figure_1_mean_t7.svg` `0ad452fbb41ab6fe5e699bfcebc5d6c73fbe923ad0fa1cf8d840ea89b00dffbf`, `.png` `925cc881c71f51944d535ff5111ce75bb0e932a09e88dd2a506a3109de7cb952`, `.pdf` `fe72a95ab9c090d17ff6724e9f2c850e59a14ca28252ae1a0c5969c5b349d1cf`,
    `_source.csv` `9704ec11b757d4a32d68bfa5d0cc1e136393f5dfddaf86594554f608cd72bbd7`, `_caption.md` `20b3e1155fb0a0e0bcb989790afbeb542eadd7e722e4a8d782fcafba21094d5b`
  - `results/…/Figure_1_cov.svg` `945bb913a86919471a146d8fd099950f05af66b680aef65d2df62bbe3b97077c`, `.png` `97293f04b924b944c796c0884bffdcbf6ae2244bd13be312002eb3a6c91b6d89`, `.pdf` `fad810009750d0936d30bbc8bd7b9052522cf98c1d27f067d5360708e42360b1`,
    `_source.csv` `88fc1d00a6ba016165730f6037f6138cf77dbe663d564583de151983a2315fdb`, `_caption.md` `f146e7d31c33c332b94734dc58cf274f20655310a17c9227c32d3f9ecedaedc0`
  - `results/…/FIGURE_CHECK.md` `daff376d5338a65de67711a87f2001d60a1d23598c349c7da9feec15836ae13e`, `figure_manifest.json` `bd7b40ec86f858cf24345fcbf1dbd7edc0156682a867b8c5459da4ae7e506029`
- Git invariants (§12.1): `docs/DEVIATIONS.md` is a pure append of HEAD (`cmp` on the HEAD-sized prefix OK); the runner,
  `pca_drift_tables.py`, `configs`, `tools`, `prompts/streams`, `results/e2`, `results/e3`, the smoke inputs and the tables
  are untouched (`git diff --quiet HEAD -- …` OK); nothing present before disappeared (`comm -23` empty); the new paths
  are exactly the 5 deliverables + the 17 outputs (`logs/` is gitignored). Status snapshots:
  `logs/pca_drift_figures/status_before.txt` / `status_after.txt`.

## Errors and Dead Ends

- `pdb.PRIMARY_KEYS` is keyed by file stem (`spectra`, not `spectra.csv`): first GREEN attempt failed with KeyError, fixed
  by normalizing the extension in `Ctx.run_index`/`run_row`.
- matplotlib 3.11 rejects `loc="outside …"` on axes legends and `constrained_layout` does not reserve room for
  `bbox_to_anchor` legends at 3.5 in width (layout collapse warnings, clipped ylabels in the cov figure). Resolution:
  explicit gridspec margins (`left/right/bottom/top/hspace/wspace`), legends anchored under each panel, the textual block
  as `fig.text` in the bottom margin, the V-panel legend dynamically shifted left to stay in frame, and long labels
  wrapped (`_wrap`); deviation recorded in `C-pca-figures-design`. All in-process frame/disjoint/font/ylim checks then PASS
  with zero warnings on mean, mean_t7 and cov.
- Test-fixture bugs fixed during GREEN: Wilson-disjoint FPR was applied to every k instead of k = 3; phrase assertions now
  normalize whitespace because long legend labels are wrapped across lines.
- pyflakes: three unused variables in the test file removed.

## Current State

- All deliverables are written; the 17 outputs are complete and hash-verified (`verify_figures_dir` true; the
  completeness function is exported for stream 31). Tests GREEN (39 passed), pyflakes clean on the two owned files,
  double run byte-identical, refusal paths exercised (exit 2 codes, exit 3 on simulated OSError without manifest).
- `make check` re-run after the corrective re-layout (full log `logs/pca_drift_figures/make_check3.log`, EXIT=0; the pre-pass run is `make_check2.log`):
  pyflakes clean over `jepadrift experiments tests tools` (including both owned files), then `37 passed` (contracts +
  decoupling) and `538 passed, 5 skipped` for the remaining suite — non-regression holds.
  Note for the operator: on this machine the second pytest phase alone exceeds the 5-minute guideline (447 s, of which
  `tests/test_plot_figure_1.py` ≈ 82 s with four full render runs); the Monte-Carlo-size rule is unchanged, this is
  wall-clock on a loaded box.
- No Git mutation was performed by this instance; the working tree holds only the deliverables listed above plus the
  pre-existing untracked plan/GO/audit files of the stream.

## Vigilance Points

- Smoke counts (n = 40 per role, shared trajectories): `SMOKE_NO_CLAIMS` on every page, legend and manifest record; no
  claim on RMST/FPR shapes. The full run (2000 per role) must regenerate toward
  `results/pca_drift_benchmark/figures/` with `--strict` and compare `figures_fingerprint` and `fpr_mismatch_k`.
- The right axis of `Figure_1_cov` is an exploratory heuristic (`mean-mixture M is not a covariance detector cost`); the
  energy comparator is a different detector family (`DETECTOR_FAMILY_MISMATCH`), not an apples-to-apples test.
- FPR comparability (P + Wilson W) is a descriptive filter at n = 40, not an equality test; `fpr_mismatch_k` is currently
  empty on all three smoke entries.
- Visual inspection of the PNGs was NOT performed by this instance (no image display in the CLI); the operator should
  inspect `Figure_1_*.png` (SHA-256 above) and the `logs/pca_drift_figures/*_preview.png` renders.
- Any evolution of the `pca_drift_tables/1` contract surfaces as `TABLE_CONTRACT_MISMATCH`; re-audit stream 30 then.

## Recommendations

- Stream 31 can reuse `verify_figures_dir` and the §5 refusal codes to keep the chain runner → tables → figure closed by
  one set of pointers.
- In a future producer schema (/3), export the paired per-replicate RMST difference prefix − S*; it is the only
  uncertainty that makes the vertical comparison of the two RMST curves inferential (recomputing it downstream stays out
  of scope here).
- After the full run, regenerate with `--strict` toward `results/pca_drift_benchmark/figures/` (prompt root) and compare
  `figures_fingerprint` / `fpr_mismatch_k` between smoke and full as an audit trace.
- Keep the explicit-margin layout (not `constrained_layout`) for any 3.5 in-wide two-panel figure with outside legends
  under matplotlib 3.11; the render checks in `FIGURE_CHECK.md` catch regressions.
