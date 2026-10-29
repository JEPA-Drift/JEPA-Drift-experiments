# Wrap-up — stream 14 (CA-T-JEPA v2): GO-A core (C1), C2, Stream 17 merge, GO-B/GO-B2 real pretrain path (C3), GO-C4 (C4), GO-J1 (C5)

## Context
Stream 14 builds the CA-T-JEPA representation of Article C under the v2 directive imposed by the researcher (native
compact context bottleneck feeding the predictor, visible-only masking, EMA target in training, frozen context encoder at
extraction, separate market channel; post-JEPA PCA only as an ablation). Directive: main checkout
`prompts/streams/01_STREAM_14_REWRITE_BOTTLENECK.md`, SHA-256 `1b5f2f8e92ba131f9e2845687e82a815b0c18674b85766af07662e008a9362c3`
(unchanged). Decisions: `prompts/GO-stream-14-A.md` (synthetic core), `prompts/GO-stream-14-B.md` (Stream 17 base and
real `d3_239` path), `prompts/GO-stream-14-B2.md` (filtered Parquet reader and asset-order integrity after the GO-B stop), `prompts/GO-stream-14-C4.md` (contract fix and
decision provenance), `prompts/GO-stream-14-J1.md` (J1 CSV tracked as native CRLF).
The plan with every integrated decision is `prompts/plans/plan-14.md`. MCP graphify and jcodemunch were reconnected and
called (graph_stats; resolve_repo) at the start of each session before implementation. All project Python ran in
`.venv` with the `torch-cf` `PYTHONPATH` shim and `MPLBACKEND=Agg`.

## Validated Results
- **C1 `04aef07` (GO-A).** `conda-torch.lock` (SHA-256 `08e19b29…98fc`), 65 conda-forge URLs with SHA-256 serialized from
  the validated solve record `solveB.json` (`df071043…5ef9`), verified by `sha256sum -c` and an offline dry-run, then
  installed offline with `--copy` into `.venv/torch-cf` (installed records = lock; pre-existing `.venv` files and pip
  freeze unchanged). Synthetic core: 33 tests; parameters 318,530 / 318,916 / 319,688 / 321,232 for d = 2 / 4 / 8 / 16;
  synthetic smoke checkpoint `058a5d04…` reproducible.
- **C2 `7fbd43f`.** The 7 module and class docstrings of the GO-A Python files removed (one-line docstrings on public
  functions only); AST rule check and pyflakes clean; 33 tests passed; synthetic smoke checkpoint still `058a5d04…`;
  `make check` rc 0 in 202 s.
- **Merge `93370e4`.** `git merge --no-ff 6ed8f8a` (Stream 17 worktree clean at `6ed8f8a1…`); `PRE..HEAD` = Stream 17's
  35 files, `6ed8f8a..HEAD` = C1 + C2 only. After the merge: `make check` rc 0 in 217 s (32 + 298 passed, 5 skips),
  4 torch guards passed, the 4 D2/PCA reference files byte-identical, J1 PASS.
- **GO-B stop (documented).** `data/derived/d3_239/ret_wide.npy` is Fortran ordered (npy 1.0, float64, (6738, 239),
  SHA-256 `a266fbab…`); the C-order header gate of GO-B correction 2 refused it. Evidence: `external/torch-cf-logs/goB_stop.txt`.
- **GO-B2 implementation (C3).**
  - Reader `experiments/jepa_pretrain.py::load_pretrain`: `ret` and `in_universe` from `panel.parquet`, C from
    `chars.parquet`, row group 0 only on `d3_239`; checks of date statistics, monitor overlap, key coverage and
    uniqueness, infinities, null `in_universe`, NaN return inside the universe; `ret_wide.npy` never opened.
  - Real-panel gates (test `test_real_pretrain_reader`): 2,769 dates (2005-01-03 → 2015-12-31) × 239 assets = 661,791
    keys, C-order SHA-256 of the returns `3115d872421e2df0dc6d58d9093e4a8703b5b314cfcb4c9f1333f54e086c4830`, 8 NaN
    characteristics all in `c_beta_252`, no infinity, equality with the Stream 17 fixture, row groups read `[0, 0]`.
  - Asset identity: `train_real` requires the ordered, unique IDs; checkpoints store only `assets_sha256`; `CATJEPA`
    refuses a missing list, a same-size permutation and IDs passed to an unbound checkpoint before `fit`; the CLI relays
    the dataset's `assets.json` order and rejects unbound checkpoints. Real `d3_239` digest `13bc71b9…a123`.
  - Shared files: lazy `ca_tjepa` factory, `--ckpt`, `--D`, `NEEDS_C = {"ipca", "ca_tjepa"}`; `CHAR_CASES["ca_tjepa"]`,
    `CALIB_FREE = {"ca_tjepa"}` with a bidirectional `test_char_no_test_statistics`; `_det_env()` keeps the inherited
    `PYTHONPATH` (shim); the 4 torch guards rebuilt on the real `CATJEPA` with failing witnesses (temporal guard: days 0,
    7, 19, both heads).
  - Tests: RED first (6 failed, 6 errors), then targeted suites `test_ca_tjepa`, `test_contracts`, `test_decoupling`,
    `test_representations`, `test_chars`: 117 passed, 2 skipped (D4 not built in this tree).
  - Real smokes (`--data d3_239 --smoke`, 200 days: 100 estimation, 65 embargo, 35 validation; 2 epochs; one thread):
    d = 8 `fc0d21a9…` (twice, config, weights and metrics byte-identical), d = 2 `f20ab58e…`, d = 4 `f6216531…`,
    d = 16 `41ec87aa…`; 10.8–12.0 s wall each, peak RSS ≤ 1.44 GB. Fingerprints in `results/jepa_pretrain/checkpoints/`
    (`<hash>.json`, digest only, no asset ID, no absolute path). Losses are 2-epoch engineering values with no reading.
  - Two full CLI extractions (`--dataset d3_239 --rep ca_tjepa --ckpt <d = 8 smoke>`, all `C-repr-rows` per Q1, outputs
    under `external/torch-cf-logs/extract_real/`): `z_b53f7f6e…` npz and json byte-identical (npz SHA-256 `43c20798…`),
    D = 9, D' = 8, rows [1256, 6738], 82 s each; only shapes and hashes were recorded.
  - D2/PCA gate after the shared edits: the 4 reference files byte-identical.
  - `make check` rc 0 in 279 s (37 passed; 310 passed, 5 skips); torch guards 4 passed, 0 skipped.
  - J1 gate: `make j1` rc 0 in 74 s; the temporary regenerated `results/e2/e2_cells.csv` has the reference SHA-256
    `e315e537…0823` with native CRLF line endings; the tracked LF file (`206dbe3b…`) was then restored from the pre-J1
    snapshot; `e2_j1_summary.txt` and `logs/e2/run.log` unchanged; Git status equal to the pre-J1 status.
- **C3 file hashes (SHA-256 prefixes):** `experiments/jepa_pretrain.py` `1d51306f`, `jepadrift/jepa/ca_tjepa.py`
  `403dbfc5`, `jepadrift/jepa/representation.py` `be8043e8`, `jepadrift/representations/extract.py` `11e5605b`,
  `tests/test_ca_tjepa.py` `10f02379`, `tests/test_contracts.py` `2c6f8582`, `configs/ca_tjepa.yaml` `4fd90ba4`,
  `docs/sections/ca_tjepa.md` `f309a3e8`, `docs/audits/ca_tjepa_leakage.md` `f0c35847`,
  `docs/sections/interface_Z.md` `6b468a29`, `docs/sections/contracts.md` `4a29b93f`, `docs/DEVIATIONS.md` `7d805ddc`,
  `CLAUDE.md` `e2e0d158`, `.gitignore` `122dca34`, `prompts/plans/plan-14.md` `7aa9a3d7` (the GO-B2 record was not
  part of C3).
- **Real smoke gains.** The 2-epoch real smokes have negative engineering gains over the constant predictor
  (1 − L_model/L_const: d = 2 −0.385, d = 4 −0.460, d = 8 −0.519, d = 16 −0.456); no J4 or scientific inference is drawn.
- **C4 (GO-C4, `prompts/GO-stream-14-C4.md` `c9756d93…`).**
  - Contract fix: `ca_tjepa.train` refuses a declared non-synthetic `data["source"]` without ordered asset IDs before
    any computation or checkpoint write. RED first (`test_declared_real_source_requires_asset_ids`: "DID NOT RAISE"),
    then GREEN: `test_ca_tjepa`, `test_contracts`, `test_decoupling`, `test_representations` 109 passed; no checkpoint
    directory is created on refusal; `data=None` and `source="synthetic:..."` still train (`assets_sha256` null).
  - Archive: the reviewed revision 6 plan copied byte for byte to `prompts/plans/plan-14-B2-revision6.md`
    (SHA-256 `bf04f2fdb9af477720b363cced06f9f334409c9bf2d9567b6e3a7f52d256b459`, `cmp` identical to the reviewed file);
    `prompts/GO-stream-14-B2.md` keeps its authorization, only the absolute plan path replaced by that relative path
    (SHA-256 `9cc5c4749df42346a3f27df426c30d4f2045f62884fa96c70e514d6df9f25590`, `bd84e210…` before);
    `prompts/PLAN-stream-14-B2.md` (`0c3f29aa…`) and `prompts/GO-stream-14-C4.md` committed as records.
  - D2/PCA and J1 gates are cited from C3: C4 does not touch their code or inputs.
- **C5 (GO-J1, `prompts/GO-stream-14-J1.md` `7ea96abb…`): J1 CSV tracked as native CRLF.** C1 to C4 tracked
  `results/e2/e2_cells.csv` as an LF blob (`206dbe3b…`), and the C3/C4 entries above record that LF state: the global
  `core.autocrlf=input` normalized the CRLF output at staging, and each J1 gate restored the LF file after its check.
  C5 adds a root `.gitattributes` with the single exact-path rule `results/e2/e2_cells.csv -text`, regenerates J1 with
  `make j1` (rc 0, 74 s; only the CSV changed; `e2_j1_summary.txt` and `logs/e2/run.log` byte-identical, `999a6802…`)
  and stages the CRLF output. Working file and index blob (`git show :results/e2/e2_cells.csv | sha256sum`) both have
  SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`; `git ls-files --eol` gives
  `i/crlf w/crlf attr/-text`; the researcher's assertions (SHA-256, CRLF present, no bare LF) pass. No model code,
  parameter or threshold changed.

## Errors and Dead Ends
- GO-A: the first offline explicit install failed because conda matches `url#sha256` specs only through conda-written
  cache records; the stage was rebuilt from the conda-populated cache and verified before the second install.
- GO-A: the first J1 script hid the CRLF regeneration behind `git diff` EOL normalization; it now compares SHA-256 with
  the snapshot and checks the restore in its verdict.
- GO-A: the pre-commit hook runs `make check` without the shim; commits export the shim for the hook (no `--no-verify`).
- GO-B: the revision 5 plan stated, without reading the header, that `ret_wide.npy` was C ordered; the real file is
  Fortran ordered. The reader gate stopped execution as specified; GO-B2 switched to the Parquet sources.

## Current State
Local commits on `stream-14`: C1 `04aef07`, C2 `7fbd43f`, merge `93370e4`, C3 `30fc19b` (GO-B2), C4 `7204730` (GO-C4),
then C5 (GO-J1, this commit), after which the tracked J1 CSV is the native CRLF file `e315e537…`. Nothing fetched,
rebased or pushed; `stream-17` and the main checkout untouched. Remaining provenance defect:
line 3 of `prompts/GO-stream-14-B.md`, committed verbatim in C2, holds the absolute local path of the revision 5 plan
file (`~/.claude/plans/tu-reprends-uniquement-le-eager-hearth.md` under the user's home directory); per GO-C4 it is not
rewritten and must be reported before any push. The parent `torch-cf.pth` is **deferred**: a single snapshot found an active Claude Code session in
the `stream-18` worktree and Codex sessions in the main checkout, which share `.venv`. Out-of-repository artifacts:
`external/torch-cf-stage/`, `external/torch-cf-shim/`, `external/torch-cf-logs/` (J1 snapshots, make-check logs,
synthetic and real smoke checkpoints, real extractions, GO-B stop record).

## Vigilance Points
- `make check` now takes 279 s under the shim, close to the 300 s budget.
- Without the shim or the `.pth`, `tests/test_ca_tjepa.py` cannot import torch: every worktree that integrates these
  commits needs one of them before `make check` or the pre-commit hook.
- Real checkpoints are bound to the `d3_239` asset order; a direct Z-1 `fit(X, C, dates)` on arrays cannot verify a
  caller's column labels. The training guard relies on the declared `data["source"]`: arrays passed without truthful
  provenance cannot be recognized as real data automatically, and the Z-1 API is not broadened.
- `c_beta_252` carries `C-D3-beta-denominator` into the tokens and the group dictionary; P4-D and any P5-D bootstrap FPR
  reading on `d3_239` with H = 750 stay outside calibrated J4 comparisons (`C-P4D-null-insample`).
- The real smokes cover 200 days and 2 epochs; full pretraining, seeds, ablations and RankMe belong to stream 16 (not
  launched).

## Recommendations
- Place the `.pth` in a window agreed with the stream 18 owner, then rerun provenance, `make check` with the 4 live guards
  and J1 without the shim.
- Before the push, rebase on `origin/main` per the end-of-stream rule and re-run `make check`, the D2/PCA gate and J1.
- Keep the real smoke (about 11 s per width) as the CPU-cost reference for stream 16 planning.
