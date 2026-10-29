# GO-C4 — Stream 14 audit closure and decision provenance

This is a bounded continuation of existing Stream 14 after C3 `30fc19b`. It authorizes one contract fix and archival cleanup only. Do not start another experiment stream, rerun real smokes, adjust model parameters, fetch, push, or touch the dirty main checkout or Stream 17. Keep C1, C2, merge, and C3 intact.

## Contract fix

The GO-B2 requirement that real D3 training cannot create an unbound checkpoint still has one bypass: direct `ca_tjepa.train(..., data={"source": "d3_239"}, assets=None)` writes `assets_sha256: null`. Before any expensive training or checkpoint write, reject a declared non-synthetic data source when ordered asset IDs are absent. The existing synthetic calls (`data=None` or `source="synthetic:..."`) must continue to work. Add a focused failing test for the direct D3 call, then implement the smallest guard and verify the checkpoint is never written. State that arrays passed without truthful provenance cannot be identified as real data automatically; do not broaden the Z-1 API.

## Archive the GO-B2 decision

- Preserve the reviewed revision 6 Claude Code plan as `prompts/plans/plan-14-B2-revision6.md` with byte-identical content and SHA-256 `bf04f2fdb9af477720b363cced06f9f334409c9bf2d9567b6e3a7f52d256b459`. Use native `Read`/`Write` or `Edit` tools, never shell or Python file edits. Stop if the copy cannot match this hash.
- In the currently untracked `prompts/GO-stream-14-B2.md`, replace only the absolute local path to that plan with the repository-relative archived path. Keep the scientific authorization unchanged. Recompute its SHA-256 and update the GO-B2 reference in `prompts/plans/plan-14.md` and `prompts/wrapups/wrapup-14.md`. Commit this GO, `prompts/PLAN-stream-14-B2.md`, the archived plan, and this C4 instruction with explicit paths. Preserve `prompts/GO-stream-14-B.md` verbatim: it already contains a local path, which must be reported as a historical provenance defect before any future push, not rewritten in this C4.
- In the wrapup, distinguish J1's temporary regenerated CRLF CSV (`e315e537...`) from the restored tracked LF CSV (`206dbe3b...`). Record the local C4 commit, the exact remaining path defect in GO-B, and that 2-epoch real smokes have negative engineering gain (about -0.385 to -0.519) without a J4 inference.

## Verification and stop rules

Reconnect and make a safe connectivity call to the graphify and jcodemunch MCP servers before modifying files; do not run Graphify LLM extraction or enable jCodeMunch AI summaries. Use Claude Code Opus 5.5 at effort Max, project `.venv` plus Torch shim, and `MPLBACKEND=Agg`. Use native `Edit`/`Write` for file changes. Run the new RED test before the code fix, then targeted GREEN tests, `git diff --check`, and the repository's `make check` hook. Prior D2/PCA and J1 gates may be cited from C3 because this change does not touch their code or inputs. If the direct-call test or hook fails, stop with evidence; do not bypass a hook or suppress a test.

Create one local conventional C4 commit with explicitly staged files, no attribution trailer, and report a clean Stream 14 worktree. No push is authorized.
