`````````````markdown
2026-10-31 02:56:16 UTC

# Wrapup — stream 29 (29-PCA-TABLES): accepted table assembler `pca_drift_tables/1`, precommit checkpoint

## Context

- Execution GO: `prompts/GO-stream-29-vibe.md` (2026-10-31), implementing the accepted plan `prompts/plans/plan-29.md`
  with the review precisions of `prompts/GO-stream-29.md`. Implementer: Mistral Vibe `large-4` / `mistral-large-4`,
  thinking `high`, sole implementer in worktree `JEPA-stream-29`, branch `stream-29`, base
  `fc533d003098a45c8ce533876642712d47038b31`. Claude remains plan-only; stream 31 is on standby until a new user
  instruction; stream 30 has not started. The actual audit-fix2 export confirms Vibe 3.0.4, model
  `mistral-large-4` (alias `large-4`), provider `mistral`, thinking `high`, finished with exit 0; its wrapper and CLI
  are off. Codex owns independent review, this formal precommit wrapup, and serialized closure/integration.
- Scope: `experiments/pca_drift_tables.py`, `tests/test_pca_drift_tables.py`, `docs/sections/pca_drift_tables.md`,
  an append-only French entry `C-pca-tables-design` in `docs/DEVIATIONS.md`, the nine outputs under
  `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`, this wrapup, and gitignored logs under
  `logs/pca_drift_tables/`. Codex-owned files (policy, NO-GO, GO, plan-29) untouched.
- Sole input: `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` (7 files, schema `pca_drift_benchmark/2`,
  run_fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`, smoke N=239 H=250,
  n_cal=n_null=n_alt=40). The runner was never launched; no real return was read; no PCA refit, recalibration,
  simulation or full run. Environment: shared `.venv` (Python 3.12.9, NumPy 2.4.4, pandas 3.0.6, SciPy 1.17.1),
  thread variables at 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`.
- Authorization evolution: after stream 29 is integrated, the researcher has authorized the synthetic full run
  with 2000 paths per role, no operational time ceiling and additional RAM as needed, followed by full tables and
  then stream 30 implemented by Mistral Vibe `large-4`/`mistral-large-4`, thinking `high`. None of these later
  executions has begun. No post-2019 real evaluation or stream-31 implementation is authorized.
- This refresh explicitly applies `~/.agents/skills/wrap-up/SKILL.md` under the project's six-section
  English wrapup contract; only this handover artifact is being edited. No new science, tests or source changes
  accompany the refresh.

## Validated Results

- Review history: the original 45-test candidate was rejected for 13 defects; audit-fix1 added 30 regression
  tests (`TestAudit1Corrections`, RED first with 24 failures, then GREEN: 75 passed in 73.9 s, pyflakes clean).
  References: `docs/audits/stream-29-implementation-review.md` and `prompts/REPAIR-stream-29-vibe-audit1.md`.
  Audit-fix1 was rejected for three remaining defects; its archived code/results and review remain available.
- Re-review cycle (`docs/audits/stream-29-implementation-rereview.md`, authorized by
  `prompts/REPAIR-stream-29-vibe-audit2.md`): 10 targeted regression tests added (`TestAudit2Corrections` plus the
  corrected n = 1 fixtures), each RED run first (10 failures reproducing the three remaining defects), then the
  minimal fix, then GREEN. `python -m pytest -q tests/test_pca_drift_tables.py` → **85 passed in 80.1 s**; `pyflakes`
  clean on both owned Python files. (1) spectra `fit_first_day`/`fit_last_day` are declared `/2` text date fields: a
  factice metadata CSV carrying 2016-04-07/2019-12-31 is accepted (`read_run_csv` and `load_run`), while a text cell
  in a genuinely numeric column is still `CSV_PARSE_FAILED`. (2) Finiteness by effective count: for executed
  ALT/HOLDOUT, `deff`/`n_eff` are required present and finite at every n; the applicable Wilson bounds are
  `det_lo`/`det_hi` for ALT and `fpr_lo`/`fpr_hi` for HOLDOUT (the producer gives deff = 1, n_eff = n and defined
  Wilson bounds even at n = 1); only `rmst_sd`/`rmst_se`/`rmst_lo`/
  `rmst_hi` may be NA at n = 1 and are required finite at n > 1; missing applicable fields are refused
  (`NON_FINITE_METRIC`) at n = 1 and n > 1, plus the positive n = 1 case with only the four undefined fields NA. The
  old fixture that NA'd deff/n_eff/det_lo/det_hi is corrected; the runner is untouched; source measures kept, no new
  SEM/CI estimator. (3) No lineage emission for a filtered-out row (the T3 family filter now runs before any `put`)
  and `validate_lineage` enforces equality of the `(table, row_id, column)` key sets for the four generated tables
  (missing `LINEAGE_INCOMPLETE`, duplicate `LINEAGE_DUPLICATE`, extra `LINEAGE_ORPHAN`); regressions for
  COV (8 orphan keys before the fix), ENERGY (56 before) and an injected orphan entry. Mechanical style cleanup:
  ordinary section comments removed from the two owned Python files (only `# ponytail` kept), public docstrings one
  line.
- Required generation-path corrections retained: (1) exact trial inventory incl. absent groups/empty frame (`TRIALS_GROUP_MISSING`);
  (2) T3 shows `M_cost`, `C_affine` and `V_denominator` (V never recomputed; Gaussian C k=20: I=1.5890738650928768,
  M=2.0649289783052449, C=1.9023780573443245, V=0.83530918523691711=I/C) and D3 keeps `I_cov_joint` beside
  `I_cov_marginal_sum`; (3) headers render the actual `run_mode` and per-role counts, smoke text only in smoke;
  (4) calibration-failure coherence in both directions with the real-D6 exception (blocked real statuses kept);
  (5) H present and exactly 250 (NA and 250.5 refused); (6) blocked-row identifiers kept (60 real T2 rows keep
  `metric_id_subset`/`selection_id_subset`) and D6 calibration provenance kept without a holdout metric;
  (7) filters applied to every table row, the T3R sub-table and the lineage; (8) `--strict` recomputes
  `pdb.identity_block` from the artifact's declared config and declared inputs (path + hash checked);
  (9) lineage unique per cell (25 888 rows, 25 888 keys; the 40 duplicates gone), MANIFEST paths exact and
  resolvable, `validate_lineage` enforces uniqueness/completeness/resolution, and `tables_fingerprint` hashes the full
  `input` object (recipe recomputable from the manifest alone, identical across renders); (10) T3 Markdown order
  RMST250 → d* → FPR250, T1 holdout intervals use the source `fpr_lo`/`fpr_hi`; (11) file hashes checked before
  parsing and malformed-but-well-hashed CSV refused as `CSV_PARSE_FAILED` (exit 2); (12) `deff`/`n_eff` remain
  mandatory finite for executed ALT and HOLDOUT, ALT Wilson detection bounds remain mandatory finite at every n,
  and only `rmst_sd`/`rmst_se`/`rmst_lo`/`rmst_hi` may be NA at n=1 (required finite at n>1);
  (13) the tautological `assert ... or True` replaced
  by a real contract assertion (Wilson interval brackets the observed FPR).
- Superseded audit-fix1 double render: both exit 0, all nine files byte-identical, `verify_output_dir` True,
  identity recomputation PASS, fingerprint
  `84fbbe5be0ef676b71c32c497326a7e2cad27620b4016160bb3fe1185f47fb2e`. Its bytes are retained under
  `logs/pca_drift_tables/audit_fix1_primary/` and `audit_fix1_repeat/`; timings remain in `repair_time_run.log` and
  `repair_time_repeat.log`. These are historical results, not the accepted current output bytes.
- Re-review double render, both fresh directories, `--strict` (`/usr/bin/time -v`, logs
  `logs/pca_drift_tables/rereview_time_run.log`, `rereview_time_repeat.log`): primary
  `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`, repeat `logs/pca_drift_tables/repeat/`.
  Exit 0 both; all nine files byte-identical (`cmp`), manifest included; `tables_fingerprint`
  `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1` (recomputed independently from the manifest
  fields, equal on both renders); `verify_output_dir` True on both; `identity recomputation: PASS` in
  `TABLES_VALIDATION.md`. Lineage: 25 888 unique keys = 25 888 exported cell keys (T1/T2/T3/T3R exact equality;
  COV filter 7 932 keys, ENERGY 116 keys, no orphans). Row counts unchanged: Tableau_PCA_1 **180** rows / 48 cols,
  Tableau_PCA_2 **220** / 65, Tableau_PCA_3 **44** / 58; `table_lineage.csv` **25 888** rows.
- Final independent Codex review: **ACCEPT for supported stream-29 generation**, with the nonblocking P3
  direct-validator limitation recorded below. Bounded CSV/JSON inspection found zero source-text mismatches for
  T1/T2 prefix RMST/FPR/IDs and T2(k=20)/T3 mean S/d/V/RMST/FPR/metric IDs; all 60 blocked-real T2 rows retain
  subset identifiers and NA empirical RMST. Current code hash matches `table_manifest.json`; the full-object
  fingerprint independently reproduces `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1`.
- Parent fresh verification of audit-fix2: **85 passed in 79.47 s**, wall **79.83 s**, max RSS **297140 KiB**;
  pyflakes exit **0**. All nine primary/repeat comparisons, output SHA-256 checks, source hashes and code hashes
  PASS. Parent independently checked global cell/lineage equality: **25888** keys unfiltered, **7932** with COV,
  **116** with ENERGY. Pre-2020 date metadata is accepted; **8/8** tested missing applicable n=40 fields are
  refused. These are parent measurements, not tests rerun by this wrapup instance.
- Row counts: Tableau_PCA_1 **180** (9 blocks × 20), Tableau_PCA_2 **220** (11 blocks × 20), Tableau_PCA_3 **44**
  (9 groups: 4 mean × 4 + 2 cov × 8 + 3 real × 4, now 58 columns), T3R Markdown sub-table 12 rows;
  `table_lineage.csv` **25 888** rows, all cell keys unique, every CSV cell covered, 17 860 SOURCE and 120 MANIFEST
  pointers resolved, no ellipsis.
- Cost (`/usr/bin/time -v`): audit-1 cycle wall 3.05 s / 3.07 s, max RSS 238 256 / 238 960 KiB (~233 MiB);
  re-review cycle wall 3.06 s / 3.08 s, max RSS 238 296 / 238 740 KiB (~233 MiB).
- SHA-256 of the nine outputs (directory `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`,
  re-review render): the seven table/lineage files keep their audit-fix1 hashes; only the validation report and the
  manifest changed (new control wording, new code hash of `pca_drift_tables.py`):

| File | SHA-256 |
|---|---|
| `TABLES_VALIDATION.md` | `fef1721fb173be470325cc3ea5efeda1051b463e045ce8f6e50dd6a84068c0af` |
| `Tableau_PCA_1.csv` | `5dff24854e9fff2f2c66a3db44bb124ad6a19db083b1c5c46e397cf4ec796952` |
| `Tableau_PCA_1.md` | `aae9f37b5f4d2c59aca2c2dae6ef9af19ec028f2cec55ec97eb64f70c064247e` |
| `Tableau_PCA_2.csv` | `31ebd1482549271f9e186989b17a21a2b475d3ad9cfe2dde1a96c8976f3c229b` |
| `Tableau_PCA_2.md` | `187aa376d4d6e0603296e87551800fa85e36be185b00c9c56f38120fc30431bc` |
| `Tableau_PCA_3.csv` | `57707849f68d5d6f3e6ce229001f5772420732a98abfa967bfe445a32daa9a4f` |
| `Tableau_PCA_3.md` | `2e67510cd789a7833265f0723b398b99b63fc6d870e047ac6db23eaa2cabee87` |
| `table_lineage.csv` | `f83eeffa947c24a8e8c17f4d91d718de4a95dd20cf735f8219860d2d44f8e6c6` |
| `table_manifest.json` | `e3f8f448715bc1d6e7195a14e08d1224301b54551b57785449bf8bb8251af74f` |

- Invariants checked (`logs/pca_drift_tables/status_repair.txt`, `repair_refusal.log`): the 7 input files unchanged
  (SHA-256 match, `git status` clean on the artefact); E2 CRLF/SHA-256
  `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` on disk and in the index, with CRLF preserved;
  historical E3/D8 FAIL kept
  (`relative gap +0.0528334213 > 0.05`); `configs/FROZEN.json` absent; re-run on the non-empty output refused with
  exit 2 (`OUTPUT_EXISTS`); no `/home/` in any output; `docs/DEVIATIONS.md` prefix byte-identical to HEAD (append
  only: `C-pca-tables-design`, `C-pca-tables-audit1`, `C-pca-tables-rereview`); runner, `configs/`, `tools/`,
  `prompts/streams/`, `results/e2`, `results/e3`,
  the /2 artefact and `docs/sections/pca_drift_benchmark.md` unchanged (`git diff --quiet HEAD`); Codex-owned files
  (policy, NO-GO, GO, plan-29, REPAIR prompt, audit report) untouched; the audit archives
  (`logs/pca_drift_orchestration/audit1-candidate.tar`, `logs/pca_drift_tables/audit1_primary/`, `audit1_repeat/`)
  untouched. Global `make check`, reindexation, commit and push remain **PENDING** for serialized parent closure;
  no such completion is claimed by this checkpoint.
- Review corrections kept: `metric_id` unique in aggregates but reusable in selection (610 refs → 275 ids);
  conditional FK/NA per row class; both Covid cohorts distinct and blocked with NA measures
  (`FROZEN.json` presence authorizes nothing); GAUSS checks need no trials; CANDIDATE rows keep theoretical I/M/V;
  trials mandatory on disk; corruption refused, never masked by NA; finiteness per `metric_kind` (no FPR required in
  ALT, no RMST in HOLDOUT); cohort id spaces separated while content fingerprints may coincide; T1/T2 prefix and
  T2(k=20)/T3(2) identities reuse the same objects, no RMST/FPR recomputation; q mean = verified H3 recipe, q cov per
  axis NA, `I_cov_joint` non-additive, M in covariance heuristic; `SMOKE_NO_CLAIMS` banner in all three Markdown files.

## Errors and Dead Ends

- First implementation (archived by Codex, not integrated): 13 defects of the audit report — see Validated Results for
  the fixes; the 45 original tests stayed green throughout (they did not cover the defects).
- Repair-cycle test fixtures: pandas degrades a corrupted numeric column to `str` silently (no exception), so
  `read_run_csv` now checks that every non-text column parses numeric (`CSV_PARSE_FAILED`); the text column set of
  schema /2 is `*_id`/`*_hash`/`*_sha256` + JSON columns + `pdb.ENUMS` keys + `schema_version`, `run_mode`, `s2_rule`,
  `message`, `deviation_ref`, `monitor_armed_from`, `onset_date`, `event_end_date`, `fit_first_day`, `fit_last_day`
  (the declared /2 date fields).
- The n=1 fixture must set `n = 1` on **all** ALT aggregates of a block (the ORACLE_Q_MIX subset metric is shared
  across k), otherwise `PREFIX_NOT_COMPARABLE` fires before the finiteness check.
- The tautology at old test line 208 (`assert ... or True`) is replaced by `fpr_lo <= fpr_test_null <= fpr_hi`.

## Current State

- Deliverables accepted by final independent Codex review for supported generation: the corrected assembler, its
  85 tests (fresh parent run: 85 passed in 79.47 s; wall 79.83 s; max RSS 297140 KiB; pyflakes exit 0), the
  contract doc `docs/sections/pca_drift_tables.md` (contract `pca_drift_tables/1` updated: final T3 columns
  `I_cov_joint`, `I_cov_marginal_sum`, `C_affine`, `V_denominator`; fingerprint recipe over the full `input` object;
  lineage exact-equality rule with `LINEAGE_ORPHAN`; refusal codes; mode-faithful headers; filter scope; `/2` text
  date fields `fit_first_day`/`fit_last_day`; finiteness by effective count), the French append-only deviation entries
  `C-pca-tables-design` + `C-pca-tables-audit1` + `C-pca-tables-rereview`, the nine fresh outputs, and the logs under
  `logs/pca_drift_tables/` (`rereview_*.log`). `git status` shows only the expected entries (Codex files, the runner,
  its config and the /2 artefact untouched; archives `audit1_*`/`audit_fix1_*`/`audit*-candidate.tar` intact,
  `audit-fix1-candidate.tar` SHA-256 `590c036eb8f903736b978b03bd4520eee5a77031bbb1cc9f8eb8aecdc7f76006`). Vibe
  audit-fix2 is finished with exit 0 and both wrapper/CLI off. No commit, no push, no reindexation, no global
  `make check` has completed: all remain PENDING for the parent, in serialized project closeout order after this
  formal checkpoint. No integration is claimed by acceptance of the supported generator.
- The accepted consumer contract is `pca_drift_tables/1`: consume `Tableau_PCA_*.csv`/`.md`, `table_lineage.csv`
  and `table_manifest.json` through `row_id`/`block_id` and `verify_output_dir` without redoing joins or
  recomputations. The current table fingerprint is
  `8c6524e3f294fd5c7a693bbc44fe666b6de8da4ccb8ece16b698f5ba8572e2f1`, and current `table_manifest.json` SHA-256 is
  `e3f8f448715bc1d6e7195a14e08d1224301b54551b57785449bf8bb8251af74f`. Actual unfiltered/COV/ENERGY output
  lineage has been globally checked by the parent; the direct-call unknown-table P3 below remains documented.
- File and dependency inventory:
  - Python files: `experiments/pca_drift_tables.py` is the read-only seven-file `/2` loader, semantic validator and
    CSV/Markdown assembler; its outputs are the three tables, cell lineage, validation report and last-written
    completion manifest. `tests/test_pca_drift_tables.py` contains 85 tests (45 original, 30 audit-1, 10 re-review).
    `experiments/pca_drift_benchmark.py` is the immutable producer imported for existing helpers only; no runner,
    detector, calibration, simulation, PCA fitting or scientific dependency was changed by stream 29.
  - Source directory: `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` contains mandatory
    `manifest.json`, `spectra.csv`, `selection.csv`, `calibration.csv`, `trials.csv`, `aggregates.csv`, `issues.csv`.
    Its schema is `pca_drift_benchmark/2`, fingerprint
    `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`; the six CSV hashes are checked against the
    producer manifest, and all seven source hashes are recorded in the table manifest. Trial files remain
    mandatory even if a future full file exceeds 50 MB and stays local/untracked (`TRIALS_LOCAL_ONLY`).
  - Output directory: `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/` contains exactly
    `Tableau_PCA_1.csv`, `Tableau_PCA_1.md`, `Tableau_PCA_2.csv`, `Tableau_PCA_2.md`, `Tableau_PCA_3.csv`,
    `Tableau_PCA_3.md`, `table_lineage.csv`, `TABLES_VALIDATION.md`, `table_manifest.json`; their current hashes
    are listed in Validated Results. The repeat is `logs/pca_drift_tables/repeat/`. Completion requires the
    last-written manifest and every listed output's matching SHA-256; non-empty output directories are refused.
  - Documentation and decision files: `docs/sections/pca_drift_tables.md` is the exact reader/column/status/
    provenance contract; `docs/sections/pca_drift_benchmark.md` remains unchanged. `docs/DEVIATIONS.md` preserves
    its HEAD prefix and appends `C-pca-tables-design`, `C-pca-tables-audit1`, `C-pca-tables-rereview`.
    `prompts/plans/plan-29.md`, `prompts/GO-stream-29.md`, `prompts/GO-stream-29-vibe.md`,
    `prompts/NO-GO-stream-29.md`, `prompts/IMPLEMENT-stream-29-vibe.md`, `prompts/REPAIR-stream-29-vibe-audit1.md`,
    `prompts/REPAIR-stream-29-vibe-audit2.md`, `docs/audits/stream-29-implementation-review.md`,
    `docs/audits/stream-29-implementation-rereview.md` and `prompts/POLICY-PCA-PLAN-ONLY.md` retain the authorization
    and review history; Vibe did not modify Codex-owned files. No other full stream plan was read by the reviewer.
    Parent additionally prepared `docs/audits/stream-29-delivery.md` and updated the execution policy to explicitly
    record the authorized synthetic full after stream-29 integration; these are parent-reported closure files.
  - Archives and logs: `logs/pca_drift_orchestration/audit1-candidate.tar` retains the rejected original candidate
    (SHA-256 `b6ba3c18de039ba8fe99aa8cd3666501357c98e7ddb665d9af1a3efd11d12655`);
    `logs/pca_drift_tables/audit1_primary/` and `audit1_repeat/` retain its outputs. The rejected audit-fix1
    candidate is `logs/pca_drift_orchestration/audit-fix1-candidate.tar` (SHA-256
    `590c036eb8f903736b978b03bd4520eee5a77031bbb1cc9f8eb8aecdc7f76006`), with outputs retained in
    `logs/pca_drift_tables/audit_fix1_primary/` and `audit_fix1_repeat/`. Vibe exports remain in
    `logs/pca_drift_orchestration/vibe_implementation/`, `vibe_audit_fix1/`, `vibe_audit_fix2/`; execution journals
    remain under `logs/pca_drift_tables/`, including `repair_time_run.log`, `repair_time_repeat.log`,
    `rereview_time_run.log`, `rereview_time_repeat.log`, `rereview_*.log`, `status_repair.txt`, `repair_refusal.log`.
    All logs, exports and archives remain gitignored and must never be staged.
  - Execution dependency: shared `.venv`, Python 3.12.9, NumPy 2.4.4, pandas 3.0.6, SciPy 1.17.1;
    `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`,
    `MPLBACKEND=Agg` before NumPy. Pinned dependencies are unchanged. `configs/FROZEN.json` is absent; no real
    post-2019 row was evaluated. `results/e2/e2_cells.csv` retains its canonical disk/index SHA-256 and CRLF;
    `results/e3` and the historical E3/D8 FAIL are unchanged.

## Vigilance Points

- Smoke status everywhere: n = 40 per role; the banner and the effectif notes stay visible; nothing here supports an
  empirical claim at n = 2000 or any post-2019 real evaluation. Real rows: measures and R1–R5 NA, both Covid cohorts
  blocked; `frozen_json_present` would not change that under schema /2.
- `q_k` mean is the H3 plug-in recipe (proxy on both backgrounds), not the population joint KL; covariance q per axis
  is NA by schema; `I_cov_joint` is not additive; M in covariance is a heuristic fluid cost (`COV_HEURISTIC_SURROGATE`).
  T3 now shows `M_cost` and `C_affine` side by side with `V_denominator`; V is a copied source value, never recomputed.
- The three rates stay distinct: empirical calibration rate, predictive bound (r+1)/(n_cal+1), observed holdout FPR.
- Applicable statistics stay mandatory: executed ALT/HOLDOUT `deff` and `n_eff`, ALT `det_lo`/`det_hi`, and HOLDOUT
  `fpr_lo`/`fpr_hi` are present and finite even at n=1. The n=1 exemption covers only `rmst_sd`, `rmst_se`,
  `rmst_lo`, `rmst_hi`; those four are finite again at n>1. No source RMST, FPR, SEM, CI or theoretical V is
  recomputed by the table assembler.
- Nonblocking P3: a caller can append a new `kind=RULE` lineage record whose `table` is `UNKNOWN`; the record
  bypasses `validate_lineage`'s per-known-table equality loops. Current builders emit only the four literals
  T1/T2/T3/T3R, so supported CLI inputs and filters cannot generate this state. This is a direct-validator
  hardening gap, not corruption of the accepted outputs: the parent independently checked their global cell-key
  equality (25888/7932/116 for unfiltered/COV/ENERGY). No source change was made for this P3 in this checkpoint.
- The runner artefact is immutable: any future `/3` schema or code change must be refused (`SCHEMA_MISMATCH` /
  `IDENTITY_MISMATCH` under `--strict`), forcing a re-audit.
- Tests take ~80 s (45 pre-existing + 30 audit-1 + 10 re-review tests): each `main()` re-loads and re-validates the
  2 422-row selection. The global `make check` budget has **not** been re-measured here (no global run was executed in
  this cycle); Codex owns that verification. The known pre-29 parent baseline was already approximately 324 s,
  above the five-minute target; do not infer budget compliance from the targeted test timings.
- No unresolved scientific input blocks the accepted generator. Pending operational gates are the parent-owned
  reindexation, global `make check`, explicit-path staging/review, commit and push, then integration. If a gate
  fails, report its evidence and leave subsequent execution pending; do not weaken scientific checks or infer
  completion. The full synthetic run and stream 30 remain unexecuted until the ordered prerequisites are met.

## Recommendations

- [Strategic Advice] Final review accepts supported generation. Parent closure must now proceed serially from
  this formal wrapup through the project's reindexation, global `make check`, audited explicit-path staging,
  Conventional Commit without trailers, push and integration. All these steps remain PENDING at this timestamp;
  do not stage ignored journals/archives, proprietary paths or oversized files.
- Stream 30 should read only `pca_drift_tables/1` outputs (figures from the CSVs), keyed by `row_id`, and re-run
  `verify_output_dir` before consuming; stream 31 can reuse the refusal codes and the row-class definitions (§3.3–§3.8)
  as its shared contract tests.
- After stream-29 integration, perform the already authorized synthetic full run at 2000 paths per role, with no
  operational time ceiling and additional RAM as needed, then regenerate the tables under
  `results/pca_drift_benchmark/tables/full/` with
  `--strict` (its `trials.csv` must be present on disk even if > 50 MB and untracked); the headers will then render
  the full mode and per-role counts without smoke text, and the `tables_fingerprint` comparison with the smoke one
  serves as an audit trace.
- Only after those audited full results, proceed to stream 30 with Mistral Vibe `large-4`/`mistral-large-4`,
  thinking `high`. Stream 31 remains on user-directed standby. Claude does not implement these streams.
- If future work exposes arbitrary lineage tables to direct validation, reject unknown table labels or compare
  global cell-key sets to close the documented P3. Do not expand this checkpoint into that source change.
- Any real trajectory rendering requires a producer schema after J4 and a new plan (stream 21 owns
  `configs/FROZEN.json`); do not extend `/2` tables with real numbers.
- The LIGHT kernel/container and `ENG_DEWATERMARKING.md` were not injected for this checkpoint; the installed
  wrap-up skill's self-contained protocol is applied with the project's six section headings. No stylistic
  perturbation or watermark-clearing tag is emitted; no pending variable is silently discarded.
`````````````
