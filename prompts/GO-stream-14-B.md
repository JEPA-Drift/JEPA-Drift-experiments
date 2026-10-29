# GO-B — Stream 14, real D3 pretrain and Stream 17 integration

The reviewed GO-B plan is `/home/m53/.claude/plans/tu-reprends-uniquement-le-eager-hearth.md` revision 5, SHA-256 `9895b584a86794847d0cd09680c7eca1599e10863ce1b577d7bcc2ee261e26da`. This GO authorizes its C2 cleanup, local merge of Stream 17 commit `6ed8f8a`, real `d3_239` pretrain path, `ca_tjepa` registration, engineering checks, documentation, and local C3 commit, subject to the corrections below. Preserve GO-A, the Stream 17 worktree, and the dirty main checkout. Do not start Streams 16 or 22, fetch, push, or claim a J4 scientific result.

## Required plan corrections before implementation

1. Preserve the inherited Torch shim in `tests/test_contracts.py::_det_env()`. Its current `PYTHONPATH` assignment discards the shim, so characteristic determinism subprocesses will fail while `.pth` is deferred. Make the smallest change that retains both the repository import path and the inherited shim. Prove the subprocess test passes under the project `.venv` and shim; do not place `.pth` to bypass this test.
2. The filtered pretrain reader must validate the `ret_wide.npy` header: float64 dtype, expected two-dimensional shape, C order, and the exact number of prefix elements read. The adversarial truncated-monitor fixture must still pass when its pretrain prefix is complete. For each Parquet row group selected, require reliable date bounds and reject any group that overlaps `monitor`; never open a monitor row group. Row group 0 in the real D3 files contains some `calib` rows, so replace the statement “calib is never read” with the precise rule: only pretrain rows may reach training, frozen-state estimation, validation, hashes, or checkpoint selection. Add a perturbation witness showing that changing `calib` rows inside that read row group leaves the filtered pretrain arrays and checkpoint unchanged.
3. `CATJEPA` must explicitly reject extraction days with zero or one observed asset. Add tests for both cases. Keep NaN as an absent return and reject infinity as required by Z-1.

## Authorized sequence and gates

- Record these corrections and this decision in `prompts/plans/plan-14.md` before editing runnable code. Reconnect the `graphify` and `jcodemunch` MCP servers and make one safe connectivity call to each before leaving plan mode. Do not run Graphify LLM extraction or enable jCodeMunch AI summaries. Stop and report if either server is unavailable.
- Use `claude-opus-5-5` at effort `max`. Execute every project Python command through the shared project `.venv`, with the isolated Torch `PYTHONPATH` shim and `MPLBACKEND=Agg`. Keep the parent `.pth` deferred while another stream uses `.venv`.
- Follow the reviewed C2, merge, C3 boundaries. Keep commits local, with conventional messages, explicit staged paths, no coauthor trailers, and no `--no-verify`. Check the Stream 17 SHA and clean status before merging. If a gate fails, stop, preserve evidence, and report the precise failure; never tune parameters to force convergence.
- Accept Q1: the frozen `ca_tjepa` CLI extraction may transform all `C-repr-rows`, including `monitor`, into a temporary directory for deterministic shape and hash checks. Do not fit, select, tune, summarize performance, or infer drift from these rows. The pretraining script must never open monitor data.
- Keep P4-D and any P5-D bootstrap FPR outside calibrated J4 comparisons. Document the inherited `c_beta_252` and phantom-rank defects without silently modifying D3. Real-data smokes establish engineering feasibility only.
- Run the plan's targeted tests, D2/PCA byte comparisons, two deterministic extractions, four native-width smokes, `make check`, and the J1 CRLF/SHA-256 gate. Restore only the three J1 generated outputs from their snapshot. Report commands, counts, artifact paths, hashes, and residual limitations in the Stream 14 wrapup.

This GO does not authorize a push, work on any new experiment stream, or a calibrated scientific claim.
