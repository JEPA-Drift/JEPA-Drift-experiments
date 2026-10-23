2026-10-23

# Wrapup — stream 17: shared characteristic path (commit 1 of 2); IPCA and P4-C/P4-D to follow

## Context

- **Prompt and plan.**
  - Prompt: `prompts/streams/prompt-17-ipca.md`. Bootstrap: `prompts/amorcage-17.md`. Shared transfer:
    `prompts/handoff-14-to-17.md` (arbitration Q7: stream 17 lays the generic characteristic scaffold first).
  - Worktree `~/JEPA-stream-17`, branch `stream-17`, base `c284823` (local `main`, stream 8b merged at `33d847d`).
  - Plan: `prompts/plans/plan-17.md`, revision 3, with « Décision GO intégrée ».
  - GO: `prompts/GO-stream-17.md`, a verbatim transcript (in French) of the bootstrap, the session messages, the
    technical GO with its corrections and the final GO.
- **Decisions.**
  - Q1–Q10 granted. Q1: D4 exposed by per-file links. Q2: `c_beta_252` used as stored, its faulty denominator to be
    quantified. Q3: cash-neutral "constant" only. Q4: rows `C-repr-rows`. Q5: argmax of the held-out R², ties to the
    smaller K. Q6: D4 aggregate rows committed. Q7: `Z-1` kept. Q8: uncentered second moment. Q9: phantom ranks used
    as is. Q10: two lines of `CLAUDE.md`.
  - Final GO: deliver the shared characteristic component and its tests first, in a verified commit (this one), then
    notify stream 14; keep the D2/PCA gates effective and the pretrain/calib separation.
- **Environment.**
  - `.venv` only (Python 3.12.9, numpy 2.4.4, scipy 1.17.1, pandas 3.0.6).
  - `make` from `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`.
  - Every verification pins OMP/MKL/OPENBLAS threads to 1 and sets `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` and
    `MPLBACKEND=Agg`.
  - Graphify and jCodeMunch answered by call before the first write.

## Validated Results

1. **Q1 (worktree D4).**
   - The link `data/raw/eurofidai` is removed.
   - `data/derived/d4_eurofidai/` is now a real directory with 7 absolute per-file links to the main tree's derived
     files. Nothing is rebuilt and the manifest is unchanged.
   - `git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x` returns 0; before Q1 it returned 128,
     which made `make check` fail.
   - After writing the two traces, `git status --porcelain` showed exactly `?? prompts/GO-stream-17.md` and
     `?? prompts/plans/plan-17.md`.
   - Recorded as `C-worktree-d4`.
2. **Shared characteristic component.**
   - `base.Representation.missing` (default `False`): `_check(..., missing)` accepts NaN only under `missing` and
     always refuses ±inf.
   - `chars.load_universe(dataset, rows)` returns the `in_universe` mask of `panel.parquet` on the
     `dates.npy × assets.json` grid; absent pairs are False.
   - `chars.load_continuous_chars(dataset, rows)` returns the four `sp500.CONTINUOUS_CHARS` columns, selected by
     name, NaN kept.
   - `extract.NEEDS_C = frozenset()` and `extract.CHAR_DATASETS = {d3_500, d4_eurofidai}`. `extract.DATASETS` is
     unchanged, so the defaults of `audit_information.py`, E10 and the pipeline CLI do not move.
   - `extract(rep, X, dates, splits, out_dir, dataset, C=None)` refuses a misaligned C. It runs `rep.pretrain` (if
     present) on the pretrain rows, `fit` on the calib rows with their C, and transforms from the first pretrain day
     with `C[first:]`. The extraction-level key `c_sha256` is added only with C.
   - The CLI masks X by `in_universe` and loads C for `NEEDS_C` representations, and refuses `CHAR_DATASETS` to the
     other representations.
3. **Tests (10 new, red then green).**
   - `test_extract_char_path_alignment` (witness `_CharProbe`): rows of X, C and dates per segment; NaN passed
     through, not zero-filled; `c_sha256` present with C and absent without.
   - `test_extract_rejects_misaligned_C`, `test_missing_flag`.
   - `tests/test_chars.py`:
     - `test_load_universe_matches_finite_returns` for `d3_239`, `d3_500` and `d4_eurofidai`: on rows before 2020
       the mask equals `isfinite(ret)` on all three panels;
     - `test_load_universe_refuses_d2`;
     - `test_load_continuous_chars_selects_by_name`.
   - `tests/test_contracts.py`:
     - the D2 determinism script and `test_monitor_perturbation_keeps_state` loop on `REGISTRY − NEEDS_C`;
     - `CHAR_CASES = {}` and the fixture `d3_char_data()` (`d3_239` before 2020: the last 128 pretrain days, the
       first 120 calib days and the next 60, X masked, C four columns);
     - the meta-test `test_char_registries_agree`;
     - five contracts parametrized by `CHAR_CASES`: non-anticipation, oddness, determinism over 2 subprocesses, no
       test statistics, declared segment. They are skipped until a characteristic representation registers.
4. **D2/PCA gate.** The `pca --mode factor` re-extractions of `d2_us97` and `d3_239` into the scratchpad are
   byte-identical (`cmp`) to the committed reference files:

   | file | npz SHA-256 |
   |---|---|
   | `z_85147fd9…6f3d.{npz,json}` | `ea04f057db3889e27e21f2cbaf0376eebf2f1df472668b9d3991f574229beeb1` |
   | `z_6c44d64a…ce3f.{npz,json}` | `687ccc9dfd6268aec4f9c690354df950a673a45a56f5be176bdb5d182b4f0316` |

5. **`make check`** (`MPLBACKEND=Agg`): exit 0 in 201 s.
   - pyflakes clean.
   - Contracts and decoupling: 23 passed, 9 skipped (5 empty `CHAR_CASES`, 4 torch).
   - Other tests: 253 passed. The real-data EUROFIDAI tests now run in this worktree.

## Errors and Dead Ends

- **Plan review, revision 2.** It was rejected by the technical GO:
  - the step-0 status check could not be empty;
  - the D2/PCA check only printed hashes;
  - the cash-neutral R² lacked the "relative returns" label;
  - the GO file was framed in English;
  - `MPLBACKEND=Agg` was missing.

  All five corrections are in revision 3.
- **Rank rule.** The revision-1 formula λ_min(W_t) > λ_max(W_t)·(max(N_t, P)·ε)² put its tolerance below the
  rounding of `eigvalsh`. It is replaced by `matrix_rank` on C̃_t (plan R1; applied in the IPCA commit).

## Current State

- This commit carries the traces (plan, GO), Q1, the shared characteristic component, its tests, the interface and
  contract docs, and `C-worktree-d4`.
- Not yet done: `jepadrift/representations/ipca.py` with its registration in `REGISTRY`, `NEEDS_C` and
  `CHAR_CASES`; P4-C/P4-D in `pipelines.py`; `experiments/ipca_k_selection.py` and its CSVs; the extractions;
  `docs/sections/ipca.md`; the remaining deviation entries; `CLAUDE.md`. They go in commit 2.

## Vigilance Points

- **Q7 order.** Stream 14 integrates this commit and extends the same scaffold: `ca_tjepa` in `REGISTRY` and
  `NEEDS_C`, its builder in `CHAR_CASES`, `--ckpt` and `--D`. A second version of the C path must not appear. The
  meta-test fails whenever `NEEDS_C` and `CHAR_CASES` disagree.
- **Pretrain hook.** It is detected by `hasattr(rep, "pretrain")` in `extract`, and in `fit_pipeline` from commit 2
  on. A future representation must not use that attribute name for anything else.
- **Duration.** `make check` takes 201 s, under the 300 s cap. The IPCA tests of commit 2 must stay within the
  45 s budget.

## Recommendations

- **Stream 14.** Rebase on this commit and reuse `d3_char_data()` (128 + 120 + 60 days, same as plan 14 §2.8).
  `CHAR_CASES[name]` receives that dict and returns a fitted representation. Its subprocess determinism test
  imports `test_contracts` from `tests/`.
