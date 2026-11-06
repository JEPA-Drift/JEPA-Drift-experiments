# Wrapup — stream 31: lot 1 prompt tooling (committed), lot 2 PCA contracts QA (historical STOP) and D7b label fix (uncommitted)

## Context

- **History.** Stream 31 resumed on 2026-11-06 under Codex supervision.
  - Plan v1 received a NO-GO (`prompts/NO-GO-stream-31.md`).
  - Plan v2 received a GO for lot 1 only (`prompts/GO-stream-31-tooling.md`).
  - The canonical plan is `prompts/plans/plan-31.md`, owned by Codex.
- **Lot 1** (tooling, `tools/check_prompts.py`). Codex reviewed, committed and pushed it in `20ad9e860a58373ec85405de6ee19a68322dd02e` ("fix(tools): cover PCA prompts and preserve master sync history"). The pre-commit hook gave 37 + 545 passed and 5 skipped.
- **Lot 2** (PCA contracts QA). It ran under `prompts/GO-stream-31.md`: the GO of 12:22 UTC and the resume after the quota at 13:25 UTC.
  - Plan §9 records QQA1–QQA3 and P1–P5.
  - Plan §10 records the E3 reference correction, the E2 required-field finiteness, the B4 refusal order and the `float_precision='round_trip'` rule.
  - It ended at 13:35 UTC in a STOP on D7b (43 passed, 1 failed). That measurement is kept as the historical record.
- **D7b fix.** It was authorised after the STOP by the following documents.
  - Researcher amendment `FIX-stream-31-nb-assets.md` (SHA-256 `ce91c1899db2fac30dcb88e64f3b1043861263adb7c2988d5394a706b84735e6`).
  - Implementation prompt `31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` (`fbfccc96fc777b6fef600ae9b16239ba46a852b68444ec3b717ac1d0a8e36c4c`).
  - Both researcher documents are archived unchanged under `logs/pca_drift_contracts/` as `researcher-fix-amendment.md` and `researcher-fix-request.md`.
  - Claude's native plan (`10beef540aa3ac4b2810c5751dddd71e2c6d80342d7a21451ccef0a8fcd02451`, archived as `logs/pca_drift_contracts/fix-d7b-native-plan.md`).
  - Codex plan `prompts/plans/plan-31-fix.md`, whose §8 settles the questions QD1–QD7.
  - Codex GO `prompts/GO-stream-31-fix.md` (15:32 UTC).
  - The GO lifts the D7b STOP only for the label fix and the replacement of the two full figure directories.
- **Ownership.**
  - Lot 2 QA:
    - `tests/test_pca_drift_contracts.py`;
    - `docs/audits/PCA_CONTRACTS_VALIDATION.md`;
    - the ignored logs under `logs/pca_drift_contracts/`.
  - The D7b fix added:
    - two lines of `experiments/figures/plot_figure_1.py`;
    - the two full figure directories (generated artifacts only);
    - D7b in the QA file;
    - the report update;
    - `logs/pca_drift_contracts/fix_d7b/`.
  - This wrapup is refreshed on explicit Codex request.
- **Execution.**
  - One interactive session, with no sub-agent and an ignored ledger.
  - Sealed artifacts were read in place; neither the runner nor the tables were run again.
  - The QA uses only tiny synthetic fixtures with an oracle, all under `tmp_path`:
    - F-tiny;
    - F-poison, with the holdout and alternative roles ×10;
    - F-fake, a fully fake dated panel run with API mode `full`.
  - Real data: dates and metadata only; `--strict` hashes the declared `splits.yaml`. No real return was read.
- **Sibling streams.** Codex pushed the independent documentation closings of streams 23 (`03f1ced`) and 18 (`ef77886`) to main. Worktree 31 stays at `20ad9e8`.

## Validated Results

### Lot 1 (committed in `20ad9e8`)

- **Tooling.**
  - TDD: RED gave 7 failed and 2 passed, then GREEN gave 9 passed with pyflakes silent.
  - `make prompts-check` reports 33/33.
  - The master migration was append-only: the first 139 933 bytes are identical, the 29 historical blocks are unchanged, and a second `--sync-master` prints `unchanged`.
- **Suite.** The implementer's `make check` gave 37 passed, then 545 passed and 5 skipped. The pre-commit hook gave the same counts.

| File | Before | After |
|---|---|---|
| `prompts/Prompts_Claude_Code_v5.md` | `5010cc23b247d99f39adc4646ee5e8645b7f524494f60f8db8740c74a334106f` (139 933 B) | `c84d560cfaf821a16892d11cb5ff854f941c09e50a2f07a70026e10d02bdceac` (188 955 B) |
| `tools/check_prompts.py` | `025a9c4880656db98a4bcd006e9ff6a91f5916e2c52270673d9e42cd0cb42669` | `053930fd7a5d85560d3ed701f551999c5c9fc837dd21ace4a306d45498fbbf4c` |
| `tests/test_check_prompts.py` | `bde2c6a53a1a6fbb12ed6927a94fbad8316cb28150e64ce081b00efa9e1ff405` | `f65adbea5cd34281fb0955415d67fc6a4edc4121cf4290667941ee29c0ec844a` |

### Lot 2 QA — historical measurement (13:35 UTC, STOP)

**Environment.**
- Command prefix:
  `export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`.
- Versions: Python 3.12.9 and pytest 9.1.1 from `.venv/bin`.
- pyflakes on the test file printed nothing (exit 0).

**Single final measurement.** It ran at 2026-11-06T13:35:04Z:

```bash
PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv \
  .venv/bin/python -m pytest -q -rA -x --durations=0 tests/test_pca_drift_contracts.py
```

Exit 1: **43 passed, 1 failed (D7b)** in 28.58 s, 29.04 s wall-clock. `-x` stopped on D7b, defined last. There was no xfail, and no test was BLOCKED.

| Group | PASS | FAIL | Duration (s) |
|---|---:|---:|---:|
| F historical invariants | 2 | 0 | 0.01 |
| E parser and numerics | 3 | 0 | 0.57 |
| A mathematics A1–A16 | 16 | 0 | 13.96 |
| B exact reuse B1–B5 | 5 | 0 | 3.05 |
| C time, leakage, sampling C1–C11 | 11 | 0 | 3.64 |
| D provenance and figures (D1–D4, D7a, D7b) | 5 | 1 (D7b) | 4.59 |
| G1 full 2000 integration | 1 | 0 | 1.02 |

**G1, executed for real.** The trials file was read directly, with no copy and no link.
- Integrity: 48 317 020 B, SHA-256 `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`, **716 000 rows**.
- Inventory: 358 groups — alternative 292 000 rows, calibration 212 000, holdout 212 000.
- 106 OK calibrations recomputed exactly: rank, threshold, maxima hash, `calibration_hash`, bound and holdout FPR.
- 146 ALT_RMST and 106 HOLDOUT_NULL_FPR identities, exact.

**Other measured values.**

| Test | Result |
|---|---|
| B1 (SMOKE and FULL) | measured 160, blocked NA 60 |
| B4 | `INVALID_S` ×3, `L17_E3_COPY`, `UNEXPECTED_ROW_STATE`, `L16_PREFIX_IDENTITY`, `FOREIGN_NULL` |
| C4 (SMOKE) | ALT_RMST 146 and HOLDOUT 106, exact |
| C5 | continuous delay 28 < restart-at-onset delay 38 |
| C8 | identities differ only in `inputs`/`input_hash`/`config_hash`; real numeric results identical |
| D3 | 301 finite plotted values per run traced to SOURCE runner cells |
| A5 | measured asymmetry 0.0 |

**Producer overlaps.** One command ran 8 producer tests and they passed (`overlap_producer_tests.log`). They cover:
- D5, abandoned under QR5;
- D6, abandoned under QR5;
- the k = 7 and OUTSIDE cases of D7a;
- the D1 double run.

**Deliverables and logs at the historical measurement.** These SHA-256 values describe the state at 13:35 UTC. The test and the report have since changed (see the D7b fix); the logs are unchanged.

| File | SHA-256 |
|---|---|
| `tests/test_pca_drift_contracts.py` (1 502 lines, 44 tests), historical | `dad74703d69f33ce1d5e6ce702b5eaaa2ca608eb15d8b7f2ea511bc0576e9c1a` |
| `docs/audits/PCA_CONTRACTS_VALIDATION.md` (236 lines), historical | `fd6346ea2fe9b59e98b1055186789d4db026468a7633e8840987ee5d2623e0f6` |
| `logs/pca_drift_contracts/qa.log` (final measurement) | `08fae1045616143925b4faf858ada49df2cf0bd92cbd2499674fd3c1b7d07328` |
| `logs/pca_drift_contracts/ledger.md` | `83543c4f2d251126bb3f7e1559fe2fd40e7aa3e1ff9c8b2960b22079d35ee545` |
| `logs/pca_drift_contracts/overlap_producer_tests.log` | `074644e66540980adfc080a6a710338cdc6ab3d59fa53805837247c880bd2fa3` |
| `logs/pca_drift_contracts/q1_FE.log` | `3ca4c4da3a9d905fbf302dc3fe635f8c41b37272a4efe8e9398636d40cad4aad` |
| `logs/pca_drift_contracts/q2q3_A.log` | `71b6f9b62094d16eebd161bfb937ba8f2bae625dc2db70397920a53c25e29845` |
| `logs/pca_drift_contracts/q2_A7_fix.log` | `e6717541589c04b6fd02f330f77f5336df3b125cd163027885c9bef319352e0f` |
| `logs/pca_drift_contracts/q4_B.log` | `47dfca95b13fd2677741448ec4c3b4988ad997b22f7f4c768574831a64f75307` |
| `logs/pca_drift_contracts/q_resume_E_control.log` | `b513a15ff36d3f81c796f633e8fb3a739083998f404881ee012296d5f3e541cc` |
| `logs/pca_drift_contracts/q5_C.log` | `ac2d82ab8ead42d9da2075dadd05f6da84a683199a62a2c4a86a37c868dcf73a` |
| `logs/pca_drift_contracts/q6_D.log` | `7c1c33edc563f762c6ce2aa4b007548903dd805b00637780209d98ff4c618824` |
| `logs/pca_drift_contracts/q7_G1.log` | `8ade9676f99f354ebb3f29793757c46cb59f2483cd5841ef458085ab414b94f5` |

**Invariants at that time.** J1 `e315e537…0823` (disk = index, 47 CRLF); D8 FAIL +5.2833 %; `PLAN.md` `ed14c47a…`; FULL manifest `3b2299bc…`. Producer code: runner `8324b47b…`, tables `13d386fe…`, figures `c40a5e77…`, which is now the historical tracer hash.

### D7b fix (2026-11-06, 15:36–15:55 UTC, not committed)

**Producer change.** `experiments/figures/plot_figure_1.py`: 2 lines modified, none added (`git diff --numstat` 2 2).
- L460, `build_entry`: `meta` gains `"n_null": int(ctx.manifest["config"]["n_null"])`, the run's null holdout count (SMOKE 40, FULL 2000).
- L582, `render_figure`: the footnote prints `(n = {meta['n_null']})` instead of the constant `(n = 40)`.
- Sources rejected because they are not the FPR sample size: `config.real.n_null` (2000 even in SMOKE), `config.N` (239 assets), `n_cal` and `n_alt`.
- Tracer SHA-256: `c40a5e77c4dbc54a17b8d5148b8271be46a5e1a16b8c99b9dcefd84ffe79a516` (historical) → **`a38fc46b1b45ed3e6e257a53c4ce29f9152b8e956b68d9d55771c58ff48634f2`** (current). The runner and the tables are unchanged.
- `figure_manifest.json`: each `records.<key>.render` gains the additive field `n_null`; `figures_schema` stays `pca_drift_figures/1`.

**QA change.** D7b `test_full_figure_text_sample_sizes_match_manifest` is extended in place.
- Size: 2 lines modified and 7 added. The file keeps 44 tests and grows to 1 509 lines, SHA-256 `2e488fe7eb175466e3d259b2f08cb3a236bb1f57ef33619da9d5efabd2c7f197`.
- The full assertions are unchanged.
- Added: the in-memory SMOKE `mean` render must print 40.
- Added: a probe must print 39. It is an in-memory copy of the SMOKE manifest with `n_null = 39` and `n_cal = n_alt = 40`.
- No fixture or sealed file is mutated.
- `mean_t7` was not in the initial D7b assertion; D7a only rendered an altered in-memory copy. The installed `mean_t7` files are checked by text extraction.

**RED and GREEN.** Node IDs are used, because the prompt's `-k "D7b or D7 or D2 or D3 or D4"` matches no test name.

| Step | Selection | Exit | Result |
|---|---|---:|---|
| RED, before the producer change | D7b | 1 | 1 failed: "sample sizes [40] != manifest counts [2000]"; smoke `{'SMOKE': [40], 'SMOKE_n_null_39': [40]}`; only the known D7b regression |
| GREEN | D7b | 0 | 1 passed: FULL [2000], `{'SMOKE': [40], 'SMOKE_n_null_39': [39]}` |
| GREEN | D2, D3, D4, D7a, D7b by node ID | 0 | 5 passed in 58.45 s |
| GREEN | `tests/test_plot_figure_1.py`, one pass | 0 | 39 passed in 120.15 s |
| GREEN | pyflakes on the tracer and the QA file | 0 | no output |

**Re-render and checks before replacement.**
- Command, from the sealed run and tables only:
  `.venv/bin/python experiments/figures/plot_figure_1.py --input-dir results/pca_drift_benchmark/full_2000_20261101 --tables-dir results/pca_drift_benchmark/tables/full_2000_20261101 --output-dir logs/pca_drift_contracts/fix_d7b/render_full --figure both --strict`
- Result: exit 0, 11.1 s, 17 files.
- `render_checks.log`: every check PASS.
  - `verify_figures_dir` is true, with the same 17 names as both full directories.
  - The manifest `command` is identical to both sealed manifests: `--output-dir <OUT>`, relative input and tables paths, `--figure both --strict`.
  - `figures_schema`, `input`, `tables`, `environment`, `filters` and `strict` equal the previous `_fix` manifest.
  - `code` holds the new tracer; the runner and the tables are unchanged.
  - Records equal the previous ones except `render.n_null = 2000`, with no `SMOKE_NO_CLAIMS` tag.
  - Unchanged: the three source CSVs and the three captions. Changed: the 9 graphics, `FIGURE_CHECK.md` and the manifest.
  - No file contains a home-directory or render-directory path.
  - `FIGURE_CHECK.md`: strict PASS. For the three figures, text_in_frame, legend_disjoint and ylim_covers PASS; font_min 6.0 pt; PNG (1620, 1050) PASS.
- `figures_fingerprint`, recomputed: `57a25a08dfcc2304ef7538ca3601b30d5e33185774da63a6c4aec3b343971b6c` (previous `_fix`: `df4e5c30c9f891922e989a477a6fe608f111a171f6b658afc14929294737633d`).
- `s4_text_checks.log` (pdftotext and the SVG, whitespace normalised):
  - `mean`, `mean_t7` and `cov` each print "equality test (n = 2000)" once in the PDF and once in the SVG, and "n = 40" never;
  - `SMOKE_NO_CLAIMS` is absent; `COV_SURROGATE_EXPLORATORY` appears only in `cov`;
  - the PDF page is 252 × 388.8 pt.
  - Before replacement, all three figures of both full directories printed "n = 40"; the older directory also printed `SMOKE_NO_CLAIMS`.

**Backup and installation.**
- Backup: both directories were copied in full to `fix_d7b/backup/`, 34 files.
  - `backup.sha256` (`cb54e770…`) equals the before inventory after prefix normalisation; the diff is empty.
  - It was checked before overwriting.
- Installation: files were overwritten in place by `cp` from the verified render, with nothing removed and the names kept.
  - `sha256sum -c render.sha256`, run from inside each final directory: 17/17 OK for each.
  - `verify_figures_dir` is true for both.
  - Both directories are identical to the render and to each other, with mode 644.

**Inventory.** `inventory_before.txt` and `inventory_after.txt` have 136 lines each. Their only differences:
- the tracer;
- `full_2000_20261101`: 14 files (9 graphics, 3 captions from tracer `5346b314…`, `FIGURE_CHECK.md`, the manifest);
- `full_2000_20261101_fix_smoke_no_claims`: 11 files (9 graphics, `FIGURE_CHECK.md`, the manifest).

Everything else is unchanged:
- both SMOKE figure directories, both runs and both table directories;
- J1 (disk = index = `e315e537…0823`, 47 CRLF, 0 bare LF), D8 `1ca7c3ae…68b3` and `docs/DEVIATIONS.md` (`2c83037f…8b30`);
- `PLAN.md`, the runner, the assembler and `tests/test_plot_figure_1.py`;
- the plan and GO files, the lot 2 logs and the researcher's files.

**Final measurement.**
- `PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv .venv/bin/python -m pytest -q -rA --durations=0 tests/test_pca_drift_contracts.py`:
  - exit 0, **44 passed, 0 failed, 0 skipped**, no xfail, in 33.63 s;
  - G1 executed: 716 000 rows, 358 groups, 106 calibrations, 146 ALT_RMST, 106 HOLDOUT_NULL_FPR;
  - D3 traced 301 values on the installed `_fix` directory.
- `PYTEST_ADDOPTS=-rs .venv/bin/make check`, with the same variable exported (15:44:15 → 15:52:55 UTC):
  - exit 0, pyflakes silent;
  - **37 passed** (36.72 s), then **589 passed and 5 skipped** (479.36 s), where 589 = 545 + 44 QA;
  - the 5 skips are pre-existing D4 availability skips, not QA: `tests/test_chars.py:69` and `:83`; `tests/test_data_eurofidai.py:318`, `:326` and `:337`;
  - `-rs` only lists the skip reasons.

**Installed figure files (identical in both full directories; `render.sha256`).**

| File | SHA-256 |
|---|---|
| `FIGURE_CHECK.md` | `54bdab2478b95396856f85e9b09d6e298c2345f91d2b508f33168f37e3ec3f36` |
| `Figure_1_cov.pdf` | `750ec0575538adb4a1bf22ee9c669e53a484220927e92468b194d6437a06564a` |
| `Figure_1_cov.png` | `605b755671e2acdcf94a844891b2ee566664f3d59ae8d93711dc3feca324c174` |
| `Figure_1_cov.svg` | `1870a952accebd3d40591783bc942ccfd08de900d1906363894861162bcf7742` |
| `Figure_1_cov_caption.md` | `cdfdd68aa5cee2e2d93a6928664259f9c4cab6e575c4646470c97f43e12aea98` |
| `Figure_1_cov_source.csv` | `8a2ec3a4a9f8aebf770ee3b339b399ec178404ca8a7af073a9d3c9c2580cd586` |
| `Figure_1_mean.pdf` | `8dcc3d4bda33f38aebc06609a9fb378c5313dce1fd6e487d12ed3e579bfb0998` |
| `Figure_1_mean.png` | `912662d7ad1c41cf10d10c22de63c7f13b85a80af7c126472b9e379c49c685ea` |
| `Figure_1_mean.svg` | `27ca7737840d19a9c0483312d2d8ab3147fedf58fd0ae7357dc0881602230e65` |
| `Figure_1_mean_caption.md` | `8c0f7a26ce54d3a7a0be42298de6ede6a7b47c64b3004e3b1c2dc7cc237fe6e3` |
| `Figure_1_mean_source.csv` | `a4c343a2ee74b593bf29fafe37f19a0115f48d0a69b8b9c8e5a0c4ad0f64a004` |
| `Figure_1_mean_t7.pdf` | `87a8a5e22b8bd0d4e8163cb4def669f76cc8b0bfc9575a9264ffa4b27a4843fc` |
| `Figure_1_mean_t7.png` | `5a7fbd6abc5b5f4a9a0e55168fdc2ed5efd2ecd05d085d1b5974a194bcfa1390` |
| `Figure_1_mean_t7.svg` | `cbc9937059871db92ab0fdbb656b76a66ad6e258f4e88810e010e0cdf01ae42d` |
| `Figure_1_mean_t7_caption.md` | `fa6fe2817ac05425f3e7f39dea938836a05f48f63d679d26927b3753c6398006` |
| `Figure_1_mean_t7_source.csv` | `f8ec238cc85ce82250970a99163d3e89a9ee07ea3cfd8e4f1da5024f277d713b` |
| `figure_manifest.json` | `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |

**Deliverables after the fix.**

| File | SHA-256 |
|---|---|
| `experiments/figures/plot_figure_1.py` | `a38fc46b1b45ed3e6e257a53c4ce29f9152b8e956b68d9d55771c58ff48634f2` |
| `tests/test_pca_drift_contracts.py` (1 509 lines, 44 tests) | `2e488fe7eb175466e3d259b2f08cb3a236bb1f57ef33619da9d5efabd2c7f197` |
| `docs/audits/PCA_CONTRACTS_VALIDATION.md` (353 lines, current, with the Codex §11) | `595e3917ddb2976601f0aef96248192f34196a5b437cbde964acb44c60a7325b` |

- Claude's S9 version of the report had 337 lines (`f6b0d7aa9df0315062e63e256ac1b99a943da2f29cf55ef4e90313c8ce76314c`).
- Codex then appended §11, "Codex review before integration", at 16:19 UTC.
- The report keeps its historical text byte for byte: removing the four inserted head lines and §10–§11 reproduces `fd6346ea…e0f6`.

**Fix logs** (`logs/pca_drift_contracts/fix_d7b/`, ignored).

| File | SHA-256 |
|---|---|
| `ledger.md` | `76c848bb81a8d0b249d4d2158126ee36acf31be08436166a41000d44bd8f9e9e` |
| `red_d7b.log` | `a2a0678e4a7aa9ee577a9ff5e43a6a1c31b363aaae64f92056cc372855b65430` |
| `green_d7b.log` | `182d512454ed7eb9505958e4d833200ff95ae51b1d37d789239ff1f061d4dd30` |
| `green_D.log` | `973efd12a0034447baf5861e81bc29ba1f1b746619a4debd015418a1ef04d343` |
| `plot_tests.log` | `d7b14ecc6ebc2259cfeea2f417d0f365ea9bbb520deba486a8978dce4957864a` |
| `render.log` | `ae5d556ca60b300cb87b4704cbf20d3a77408a4ee8ec073e008730e93cc245bb` |
| `render_checks.log` | `43b76bdaa9fb934dd7ae6913749025d8771bcd7b308b25e56315ca1e3b21ef03` |
| `s4_text_checks.log` | `0f9c802ce1148e6314cdfb01de7ad2a10a9a3e57911192fc6b33d9f04b4423ee` |
| `render.sha256` | `2847d3e2c8161ce326a40e4f73a0d01df505172f0f15f386433f59f9a4352055` |
| `backup.sha256` | `cb54e77003ff2fb9d30485b7b321b1247a34ac2257f03076cab6d6d5d7b85afd` |
| `qa_after.log` | `35de632005e941dd637d4dde0284406fe06c90b5394808ff08702432ad93a108` |
| `make_check.log` | `b001db7008f7bc0cba5cd6d64b989408092cf0ccd77202a8966ba155b3655788` |
| `inventory_before.txt` | `7134828c571b389ce66cd05510eacc5163ff8d1f20240507b754c8ba116376fb` |
| `inventory_after.txt` | `d19f6b31b26047dd382743e9abb3f1ac02ba3ce94fd8e059786c8fd813180ebf` |
| `inventory.diff` | `0785f2b7b7add9e023e5a7242bf97c310d78ea85ceedf08b57ad61ed00f275c6` |
| `tracer.diff` | `d8d36d1df474087221466974839828f5b1f8f8cf611fb3227d9252ae00d3f266` |
| `s0_codex_before_fix_check.log` (Codex pre-fix list, 83/83 OK) | `98d47f986f3b1924eb34ea1f2226508c0f16236de6469ca30c0ea55ccb2e688d` |

## Errors and Dead Ends

- **Lot 1.** The first full `make check` was stopped after a self-review finding (a false 100 % ratio line). The suite was re-run on the final code.
- **Lot 2, correction 1 (A7, QA fixture error).**
  - Cause: the grid `linspace(4x/2000, 4x, 2000)` contains the root x, g(x) evaluated to 0.0, and the sign-change count saw two transitions.
  - Fix: count sign changes on non-zero signs.
  - One attempt, then pass. It was not a producer defect.
- **Lot 2, plan references corrected before execution (rulings arbitrated in §9 and §10).**
  - *E3.* The plan said `kl_cov_raw` rejects non-finite inputs. In fact it returns NaN; this is now the observation O-E3-NONFINITE, not a passed control.
  - *B4.* A family changed on the E3 oracle copy is refused with `UNEXPECTED_ROW_STATE` (documented applicability check), before L17. The E2 prefix witness, refused with `L16_PREFIX_IDENTITY`, is kept.
  - *C8.* The identifiers derived from `fp` change with the input hashes. They are compared under a bounded exception list (§9); everything else stays strict.
  - *P1.* `pdt.load_run(FULL)` raises `TRIALS_MISSING`, so FULL is read file by file after SHA checks.
  - *P2.* F-fake needs `mode = "full"`.
- **Lot 2 quota pause.** Work paused after 26 tests (F, E, A, B), with no partial final measurement. The resume added the §10 corrections, with a targeted E1–E3 control (3 passed); the 26 tests were not re-run.
- **Lot 2 D7b STOP.** It was a confirmed producer label defect: the hard-coded "(n = 40)" at `plot_figure_1.py:582`. It is now fixed under `GO-stream-31-fix.md`.
- **"One line if possible" was not achievable.**
  - `render_figure(src, meta)` receives neither the manifest nor the context, and `src` holds no count.
  - Inverting the Wilson bounds would give a guessed number, and global state or stack introspection were excluded.
  - So one `meta` field was needed, which means two lines in the same tracer. The GO §8 accepts this.
- **Vacant selector.** The implementation prompt's `-k "D7b or D7 or D2 or D3 or D4"` matches no test name, so it would deselect everything (exit 5). Real node IDs were used instead.
- **Exit 1 of the S4 text-extraction shell block: a reporting-script error, not a product failure.**
  - The status comes from the block's last command, the guard `[ $tag = render_full ] && pdfinfo …`. That guard is false on the final loop iteration (`old_before`, the pre-fix directory).
  - The 21 result lines show no failed content check, and every count matches the expectation.
  - The nonzero status is kept as such in the ledger and in report §11 ("Operational exception"). The block is not counted as a successful command.
  - No statistic, tolerance or producer contract was changed for it. Codex's independent checks, with explicit assertions and exit checking, exited 0.
- **Tool timeout, not a failure.** The single post-change run of `tests/test_plot_figure_1.py` exceeded the 120 s tool timeout and continued in the background. It finished with exit 0 (39 passed in 120.15 s) and was not re-run (GO §8 S7).
- **Fix QA corrections:** 0 of the 3 allowed.

## Current State

- **D7b is fixed and not committed.** `GO-stream-31-fix.md` lifted the STOP for this scope only.
  - The historical lot 2 record (43 passed, 1 failed, STOP) is kept in the report's head paragraph and §1–9, in `qa.log` and in `ledger.md`.
  - The current measurement is in report §10: 44 passed, 0 failed, 0 skipped with G1; `make check` exit 0 (37 + 589 passed, 5 pre-existing skips).
  - Nothing is staged or committed. No reindex was run.
  - After Claude's report update, Codex appended §11 to the report. This wrapup refresh is Claude's only change since then.
- **Codex review before integration (report §11).** Independent read-only verification exited 0.
  - Codex's 83-file pre-fix inventory: 25 files changed, all within the two authorised full directories; 58 are byte-identical.
  - Both full directories hold identical files, and all four figure directories pass `verify_figures_dir`.
  - Both full fingerprints were recomputed from canonical JSON and match their manifests.
  - PDF and SVG text of all three entries contain `equality test (n = 2000)`, with no `n = 40` and no `SMOKE_NO_CLAIMS`.
  - PNG geometry is 1050 × 1620 px; Codex visually inspected the three PNGs.
  - J1, D8 and `PLAN.md` keep their reference hashes.
  - `figure_manifest.json`: `d1dfe3c2…` (`full_2000_20261101`) and `9e3b666f…` (`_fix`) → `41b36c4e…` (both).
  - Previous fingerprints: `9c1fff931a1a1d3541128ae3cab9b0b4c9d77374a64c8041709968a5c3b86473` (`full_2000_20261101`) and `df4e5c30…` (`_fix`).
- **Worktree.** HEAD = `20ad9e860a58373ec85405de6ee19a68322dd02e`; worktree 31 must not move. Expected `git status --porcelain` after this refresh:

  ```
   M experiments/figures/plot_figure_1.py
   M prompts/plans/plan-31.md
   M prompts/wrapups/wrapup-31.md
   M results/pca_drift_benchmark/figures/full_2000_20261101/{FIGURE_CHECK.md, Figure_1_{cov,mean,mean_t7}.{pdf,png,svg}, Figure_1_{cov,mean,mean_t7}_caption.md, figure_manifest.json}   (14 lines)
   M results/pca_drift_benchmark/figures/full_2000_20261101_fix_smoke_no_claims/{FIGURE_CHECK.md, Figure_1_{cov,mean,mean_t7}.{pdf,png,svg}, figure_manifest.json}   (11 lines)
  ?? docs/audits/PCA_CONTRACTS_VALIDATION.md
  ?? prompts/GO-stream-31-fix.md
  ?? prompts/GO-stream-31.md
  ?? prompts/plans/plan-31-fix.md
  ?? tests/test_pca_drift_contracts.py
  ```

- **Codex files, untouched by Claude.** The current versions are cited here, not rewritten.
  - `prompts/plans/plan-31.md` (588 lines, `68dd3256e184590ef143a809a09dd6c999cd0d86ed10f833797e3e6076f9994d`). Its §11, "Réception après l'avenant D7b — 2026-11-06", records the following:
    - it keeps the initial 43/1 STOP with its evidence and logs;
    - the separate fix plan and GO replace the earlier tracer and full-directory prohibitions for this fix only, and the QA decisions of §9–10 are unchanged;
    - it takes delivery of 44/0/0 with G1, `make check` 37 + 589 with 5 pre-existing D4 skips, and the two-line tracer change;
    - reindexing, pre-commit checks, commit and integration remain with Codex.
  - `prompts/GO-stream-31.md` (29 lines, `227642279732057565967121e79d585e4f74a1f9474a5e2d678b31adff26e9df`).
  - `prompts/plans/plan-31-fix.md` (`1c83afabf059f41afe2f8ffb4d61f80e127674ef3becd7a6defb3ea8f7cfe97c`).
  - `prompts/GO-stream-31-fix.md` (`6e7945ebf4111e5f985ec8e96b353a085f30e7f1e0bdb31ff858d540a907eb54`).
  - Report §11, "Codex review before integration", is Codex-authored and sits in the report version `595e3917…7325b` cited above.
- **Researcher files, untouched (read only for their hashes).** The three untracked files in the main worktree's `prompts/` and `prompts/streams/`.
- **Smoke figure directories.** Unchanged byte for byte; they stay linked to their historical tracers `f2a0e7f0…` and `c40a5e77…`.
- **Ignored logs.**
  - Lot 2, historical and unchanged, under `logs/pca_drift_contracts/`: the ledger, `q1_FE`, `q2q3_A`, `q2_A7_fix`, `q4_B`, `q_resume_E_control`, `q5_C`, `q6_D`, `q7_G1`, `overlap_producer_tests` and `qa`.
  - Fix, under `logs/pca_drift_contracts/fix_d7b/`:
    - the ledger, the inventory script, both inventories and their diff;
    - the RED and GREEN logs, `plot_tests`, `render`, `render_checks` and `s4_text_checks` (with the extracted texts in `s4_text/`);
    - `render_full/` (the verified render) and `backup/` (both pre-fix full directories), each with its `.sha256` list;
    - `qa_after`, `make_check` and the git status/diff snapshots.
- **Execution environment.**
  - System: Linux 5.14 (EL9).
  - `.venv/bin/python` 3.12.9, a venv built on the Trading 3.12.9 binary.
  - Packages: pytest 9.1.1, numpy 2.4.4, pandas 3.0.6, matplotlib 3.11.2 (Agg); the DejaVuSans.ttf font.
  - poppler `pdftotext`/`pdfinfo` on PATH.
  - Prefix: `export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`.
  - G1: `PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv`, read in place.

## Vigilance Points

- **Hook-run `make check`.** Export `PCA_FULL2000_TRIALS` before the commit hook; otherwise G1 skips for availability. The 5 D4 skips are pre-existing and expected in this tree.
- **G1 dependency.** G1 depends on the neighbouring `../JEPA-full-2000/` file. It is BLOCKED (skip) only when the variable is unset or the path is absent; a hash or computation divergence is a FAIL.
- **Historical smoke manifests.**
  - They keep their historical tracers and have no `render.n_null`.
  - Replaying their `records.render` with the new tracer would raise `KeyError`. No consumer does, and no such replay is claimed.
  - Their labels are correct: their `n_null` is 40.
- **Additive manifest field.** `records.render.n_null` was added without a `figures_schema` bump (QD2).
- **`git diff --check`.** Its only warnings are trailing spaces in the generated SVGs.
  - Codex decided that no SVG byte is normalised.
  - Any whitespace normalisation, whether by an editor, a hook or a Git attribute, would break the SHA-256 values in `figure_manifest.json`, `verify_figures_dir` and `render.sha256`. Keep the SVGs as generated.
- **Former content of `full_2000_20261101`.** It held tracer `5346b314…` and a `SMOKE_NO_CLAIMS` banner. It is now identical to `_fix`; the old bytes remain in Git at `20ad9e8` and in `fix_d7b/backup/`.
- **Report reading.** The report head now carries the current status and a pointer to §10. Its §1–9 are historical, and in them `c40a5e77…` is the historical tracer hash.
- **O-E3-NONFINITE.**
  - `kl_cov_raw` returns NaN for NaN or inf entries.
  - `clip_kl(NaN)` returns (NaN, 0).
  - `kl_cov_raw(I, diag(−1, −1))` returns −2.0 (the determinant sign is positive), and `kl_cov` then refuses it through `clip_kl`.
  - These are observed limits outside the finite SPD prerequisite, to be arbitrated separately. Required information fields are finite in the sealed outputs (E2).
- **Other observations, not contracts.**
  - `spec.tags` copies keep `SMOKE_NO_CLAIMS` while the effective full tags do not.
  - The UNSUPPORTED covariance `EXANTE_QBAR` rows are labelled `MIX_FLUID_SURROGATE`.
  - The full `Figure_1_mean` prints "FPR mismatch at k = [12]"; it is a data-driven marker.
  - The in-memory D7b assertion covers FULL `mean` and `cov`, the SMOKE `mean` and the probe. The `mean_t7` label is checked only on the rendered files.
  - The O(L²) cost of long real paths is untested.
  - A3 covers dyadic q only.
- **Lot 1 points still valid.**
  - `EXPECTED_IDS` is a CLI constant: new stream prompts must be added there.
  - `check()` is stricter: exact block plus the presence of the full source text.
  - Block extraction stops at the next four-backtick opening fence.
  - The master write is not atomic.
  - `CLAUDE.md` still says "exact substrings".
  - `make check` exceeds the 5-minute guideline (8 min 40 s here; pre-existing).

## Recommendations

- **Codex.**
  - The review before integration is recorded in report §11.
  - Remaining steps it owns: approve this wrapup, AST-only reindex, then the hook-run `make check` with `PCA_FULL2000_TRIALS` exported, then commit and push.
  - Stage the tracer, the 25 figure files, the QA file, the report, this wrapup and the fix plan/GO by explicit path. Never stage `logs/`.
- **Researcher (optional).**
  - Decide whether O-E3-NONFINITE warrants an explicit validation contract (a producer change, under a separate GO).
  - Align the `CLAUDE.md` description of `check_prompts.py`.
- **Next instance.**
  - No new run, re-render, smoke change or contract change without a new written GO.
  - Smoke re-rendering is not needed: the labels are correct and the directories are sealed.
