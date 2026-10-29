# Wrap-up — stream 14 (CA-T-JEPA v2), GO-A: isolated torch environment and synthetic core (commit C1)

## Context
Stream 14 builds the CA-T-JEPA representation of Article C under the v2 directive imposed by the researcher (native
compact context bottleneck feeding the predictor, visible-only masking, EMA target in training, frozen context encoder at
extraction, separate market channel; post-JEPA PCA only as an ablation). Directive: main checkout
`prompts/streams/01_STREAM_14_REWRITE_BOTTLENECK.md`, SHA-256 `1b5f2f8e92ba131f9e2845687e82a815b0c18674b85766af07662e008a9362c3`
(unchanged). GO-A (`prompts/GO-stream-14-A.md`) authorizes P0, P1 and the synthetic phase 2A only. MCP graphify and
jcodemunch were reconnected and called (graph_stats; resolve_repo) at the start of each session before implementation.

## Validated Results
- **P1 lock.** `conda-torch.lock` (SHA-256 `08e19b29d8ec3930b5a3086f487f9f2f1f92f9ed7a8461e084eeb7201ac398fc`) is a
  serialization of the validated solve record `solveB.json` (SHA-256 `df071043…5ef9`): 65 conda-forge URLs with SHA-256,
  pytorch `2.14.1-cpu_generic_py312_h29917d7_0`, python `3.12.9-h9e4cc4f_0_cpython`, numpy `2.4.4-py312h33ff503_0`,
  libstdcxx/libgcc `15.1.0` (`h8f9b012_5`/`h767d61c_5`). Verified before installation: 65/65 archive hashes by coreutils
  `sha256sum -c`; lock = `solveB.json` FETCH = offline dry-run FETCH (65); offline dry-run LINK = `solveB.json` LINK (name,
  version, build, channel).
- **P1 install.** `conda create --offline --copy -p .venv/torch-cf --file conda-torch.lock` (rc 0); installed records =
  lock (65); fingerprint of the pre-existing `.venv` files `038d8517…a7be6c` and pip freeze `308f5ae7…9b64` (54 dists)
  unchanged; no `.pth` in the parent site-packages.
- **P1 shim.** `external/torch-cf-shim/sitecustomize.py` appends the `torch-cf` site-packages; torch 2.14.1 (CPU, no
  CUDA) from `torch-cf`, numpy 2.4.4 / scipy 1.17.1 / pandas 3.0.6 from `.venv`, in both import orders.
- **P1 checks under the shim.** `make check` rc 0 (294 s; contracts/decoupling 26 passed; other suites 241 passed,
  4 unrelated skips); `pytest -rs tests/test_contracts.py -k torch`: the 4 torch guards executed, 4 passed, 0 skipped.
  `make j1` rc 0 in 74 s: `results/e2/e2_cells.csv` SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`,
  native CRLF; `e2_j1_summary.txt` and `logs/e2/run.log` unchanged (`999a6802…`); the regenerated `e2_cells.csv` was
  restored from the byte-exact pre-J1 snapshot (`206dbe3b…`); Git status equal to the pre-J1 status.
- **2A tests** (`tests/test_ca_tjepa.py`, 33 tests, written RED first: collection failed before the modules existed): all
  pass in 4.5 s. Coverage: no-leak under group and random masks with a negative witness, mask bounds with empty,
  oversized and absent groups, ties and `nochar`, `sector_pit` refusal, exact parity, permutation equivariance, frozen
  extraction with an EMA witness, deterministic training with untouched global RNG, refusal of rows after
  `pretrain_end`, holdout rows unused, VICReg terms, EMA schedule, constant-predictor baseline, no-coupling control,
  checkpoint integrity, Z-1 sidecar, CLI `CHECKPOINT_PATH`.
- **Final `make check` with the 2A files under the shim:** rc 0 in 201 s; 26 passed; 274 passed, 4 unrelated skips;
  torch guards 4 passed, 0 skipped; tree unchanged by the run.
- **Parameters** (EMA copy included): d = 2: 318,530; 4: 318,916; 8: 319,688; 16: 321,232 (≤ 1 M).
- **Synthetic smoke** (N = 239, 200 days, 2 epochs, one thread): 9.1 s of training per width d ∈ {2, 4, 8, 16}
  (10.95 s wall, peak RSS 1.27 GB for d = 8); two d = 8 runs give the same checkpoint
  `058a5d04ad14fbf620fa16b5335ffa90b94d3087de7cd3af115acbbf74572201` with byte-identical config, weights and metrics; two
  extractions through `CATJEPA` give identical digests, z_odd (30, 9), z_even (30, 8), oddness error 0.0. The smoke and
  control-smoke losses (gain −0.165 and −0.265 at the selected epoch) are 2-epoch engineering values with no scientific
  reading.
- **Files (SHA-256):** `configs/ca_tjepa.yaml` `e3d5dd64…`, `jepadrift/jepa/ca_tjepa.py` `441d85d4…`,
  `jepadrift/jepa/representation.py` `79325d36…`, `experiments/jepa_pretrain.py` `f5b44930…`, `tests/test_ca_tjepa.py`
  `4d567d63…`, `docs/sections/ca_tjepa.md` `04025c18…`, `docs/audits/ca_tjepa_leakage.md` `5bac640d…`,
  `prompts/plans/plan-14.md` `24e3bcb6…`, `prompts/GO-stream-14-A.md` `35acb12b…`.

## Errors and Dead Ends
- A first explicit offline install from bare archives failed (OfflineError): for `url#sha256` specs conda matches cached
  packages only through records that carry both url and sha256 (`urls.txt` and `info/repodata_record.json` written by
  conda itself). The partial prefix was removed; the stage was rebuilt as a copy of the conda-populated source cache and
  verified (urls.txt = lock URLs, 65 `repodata_record.json` url#sha256 = lock, 26,346 extracted files = their `paths.json`
  SHA-256) before the second, successful install. No package, build, channel or source changed.
- The first J1 gate script detected changed outputs with `git diff --quiet`, which hides the CRLF regeneration behind
  EOL normalization: `e2_cells.csv` was left regenerated and the script still printed PASS. It was restored by hand from
  the snapshot and the script now compares SHA-256 against the snapshot and includes the restore check in its verdict.
- `experiments/jepa_pretrain.py` first failed to import `jepadrift` when run as a script; it now inserts the repository
  root on `sys.path` like the other experiment scripts.
- The first `git commit` was refused by the pre-commit hook: its `make check` ran without the shim, so
  `tests/test_ca_tjepa.py` could not import torch (the torch guards were skipped there). C1 was committed with the shim
  exported for the hook (`PYTHONPATH` = `external/torch-cf-shim`, `.venv/bin` first on `PATH`); no `--no-verify`.

## Current State
GO-B (`prompts/GO-stream-14-B.md`) in progress. C2 removed the 7 module and class docstrings of the GO-A Python files
(AGENTS rule: one-line docstrings on public functions only); AST rule check clean, pyflakes clean, 33 tests
passed, synthetic smoke checkpoint unchanged (`058a5d04…`), `make check` rc 0 in 202 s under the shim.
Local commit C1 on `stream-14` (not fetched, rebased, merged or pushed). `.venv/torch-cf` installed; the parent
`torch-cf.pth` is **pending**: a single snapshot found an active Claude Code session in the `stream-18` worktree, which
shares `.venv`. Out-of-repository artifacts: `external/torch-cf-stage/` (solve record, 65 archives, repodata cache,
dry-run), `external/torch-cf-shim/`, `external/torch-cf-logs/` (J1 snapshots and logs, make-check logs, smoke checkpoints).

## Vigilance Points
- Once C1 is integrated anywhere, `tests/test_ca_tjepa.py` imports torch: `make check` then needs the shim or the
  `.pth` in every worktree.
- The `.pth` must be placed only after other streams release `.venv`, followed by provenance, `make check` with 4 live
  guards and J1 (snapshot, SHA-256, CRLF, restore) without the shim.
- GO-B items remain open: source-filtered `d3_239` reading, NaN path through `Representation.missing`, coverage audit
  with the 63-observation stop, protocol smokes, `extract.py` registration, reconciliation of
  `test_char_no_test_statistics` (the CA-T-JEPA state does not move with the fit rows), real-model torch guards, U14.
- The Stream 17 P4-D result is a D3 stop, not a calibrated PASS; any bootstrap null reading of an even head on `d3_239`
  with H = 750 is affected.

## Recommendations
- Place the `.pth` in a window agreed with the stream 18 owner, then rerun the P1 checks without the shim.
- Start GO-B only after the Stream 17 base is final and audited; keep loader changes backward compatible.
- Keep the synthetic smoke as the CPU-cost reference: about 9 s for 2 epochs on 200 days × 239 assets per width.
