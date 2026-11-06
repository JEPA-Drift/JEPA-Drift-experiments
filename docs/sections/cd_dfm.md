# Stream 18 — CD-DFM: documentary diagnostic

**Status: unavailable.** `prompts/streams/prompt-18-cddfm.md` planned CD-DFM as a second characteristic-driven
latent model for P4 (P4-C and P4-D variants) and as a conditional whitening (channel N2). The stop condition of its
task 5 holds: the `data` package imported by the official training chain is not tracked at the pinned upstream
commit. No adapter, extraction, P4 entry, local replacement of the missing code, or CD-DFM training or evaluation
output was found in the perimeters inspected on 2026-11-06 (listed in `docs/audits/stream_18_closeout_2026_11_06.md`),
and no other pipeline is designated as a replacement for this comparator. Model integration is `BLOQUÉ` (row 18 of
`docs/audits/streams_01_27_relevance_2026_11_06.md`). This is a documentary diagnostic: nothing was measured.

## Pinned source

- CD-DFM is the Characteristic-Driven Dynamic Factor Model of [Alouadi and Lehalle, 2026, The Fundamental Structure
  of Risk: From Characteristics to Covariance, arXiv:2607.24410] (README title at the pinned commit).
- Repository `https://github.com/alexouadi/CD-DFM`, commit `37a1dfb39974884df822aa2994854bbf1270e381`
  (2026-07-29, "Update contact email"), recorded in `data/derived/MANIFEST.json` under `sources.d3.cd_dfm` with
  `access: read-only` since the D3 build (`3e3a804`).
- The local clone `external/cd-dfm/` (gitignored) has this commit as HEAD, no tracked change and no untracked file
  outside the upstream ignore rules (checked on 2026-11-06). Its working tree holds no checkpoint, `results/` or
  `data/` directory.

## Official training chain at the pinned commit

Scripts and tests prepend the clone's `src/` to `sys.path` (e.g. `scripts/train.py:18`), and the README layout table
lists `src/data/` as "Panel preprocessing and the windowed dataset".

| Module or object | Referenced by | Tracked at the pin |
|---|---|---|
| `data.dataset` (`load_panel_tensors`, `time_split`, `AnchorDataset`, `PanelTensors`, `batch_for_anchor`) | 25 import statements in 22 files, including `scripts/train.py:21` and `src/train.py:12` | no |
| `preprocess_panel`, imported by `from data import preprocess_panel` | `scripts/preprocess_dataset.py:19` | no |
| `data.preprocess` | `tests/test_preprocess.py:9` | no |
| package `cddfm` (`cddfm.data.dataset`, `cddfm.eval.benchmarks`) | `scripts/benchmarks/run_sparse_pca.sh:25-26` | no |
| `src/model/`, `src/eval/`, `src/analysis/`, `src/paths.py`, `src/train.py` | entry points and tests | yes |

None of the 71 paths tracked at the pin has a `data` or `cddfm` directory component or is named `data.py`. This
observation covers the pinned commit only; it says nothing about other commits or copies of the code, and the cause
of the absence is not established. The Z-1 wrapper is a project-side deliverable of prompt 18 (task 3). Task 5
forbids creating the adapter on the documented stop path; no Z-1 wrapper was found in the inspected project tree.

## License observation

No file named LICENSE, LICENCE, COPYING, NOTICE or COPYRIGHT (any case, any extension, any depth) is tracked at the
pinned commit, and the README states no license for the code; its only licensing sentence concerns the
characteristic data. This is an observation, not a legal conclusion. Remote repository metadata was not consulted.

## Input limit

The README and `configs/data.yaml` at the pin expect a panel with 10 continuous characteristics derived from
RavenPack and Compustat (`log_market_cap`, `book_to_market`, `leverage`, `roe`, `capex_rev`, `working_capital`,
`pe_proxy`, `news_flow`, `news_sentiment`, `news_buzz`), 11 compositional revenue shares, 2 categorical codes
(`gics_sector`, `exchg`) and daily log returns; the README states that this panel cannot be redistributed. For D3
the project holds 4 return-derived continuous characteristics (`CONTINUOUS_CHARS` in
`jepadrift/data_loader/sp500.py`: `c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21`) and 11 static GICS sector
indicators (`C-D3-gics-static`). No mapping between the two input sets was found in the inspected perimeters.

## J4 eligibility

Section 2 of `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md` admits CD-DFM to the primary comparison only if it is:

> réellement disponible, licite, préspécifié et gelé avant J4 ; sinon diagnostic secondaire ou « non disponible » sans remplacement caché

The availability condition is not met, so CD-DFM is recorded as « non disponible », with no replacement. Lawfulness,
pre-specification and freezing were not assessed.

## Not established

No local evidence supports a statement on the computational or estimation cost of CD-DFM, on an advantage of JEPA
or of any other pipeline over CD-DFM, on the sufficiency of IPCA (P4) or P3-CS(b) as comparators in its place, or on
the experimental coverage left by its absence. This document makes no such statement.
