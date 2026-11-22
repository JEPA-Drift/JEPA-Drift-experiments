# Wrapup 00 — stream-32 spec placement (exit of the prompt discovery globs)

## Context

Commit bce8f1e added `prompts/streams/prompt-32-pca-info-online.md`, a stream-32 specification whose
first line is an H1 title (`# STREAM 32 — ...`), not a `## PROMPT <id> —` title. The name matched the
discovery glob `prompt-*.md` of `tools/check_prompts.py`, so `prompt_ids` raised ValueError, three
tests of `tests/test_check_prompts.py` failed and the pre-commit hook (`make check`) blocked the
commit; it was forced with `--no-verify` at the researcher's request. Id `32` is not in
`EXPECTED_IDS` (1–28, 8b, 28-PCA, 29–31): the checker and the tests are pinned to 33 prompts and the
master `prompts/Prompts_Claude_Code_v5.md` holds no block 32, so the file was out of contract by
design (a specification, not an executed prompt).

## Validated Results

- `git mv prompts/streams/prompt-32-pca-info-online.md prompts/streams/32_STREAM_PCA_INFO_ONLINE_SPEC.md`
  (content byte-identical; SHA-256
  `db2ef8717e56d36b41a7ff805cea8a21c57ab9fcafd5d56ec96e9b21ab97201b`). The new name matches neither
  discovery pattern, like the existing `01_STREAM_14_REWRITE_BOTTLENECK.md` and
  `07_STREAM_22_E5_J4_REWRITE.md`.
- References updated (repo-wide grep, 2 hits): `prompts/PASSATION_CODEX_APRES_STREAM23_20261114.md`,
  `prompts/streams/13_CODEX_AMORCAGE_PCA_INFO_ONLINE_2026_11_14.md`.
- `.venv/bin/python tools/check_prompts.py`: `prompts-check: 33/33 (29 prompt-*.md + 4
  [0-9][0-9]_STREAM_PCA_DRIFT_*.md: 28-PCA, 29, 30, 31)`, exit 0.
- `.venv/bin/python -m pytest tests/test_check_prompts.py -q`: 9 passed.
- Full `make check` runs as the pre-commit hook of the commit carrying this wrapup.

## Errors and Dead Ends

- Retitling the spec as `## PROMPT 32 — ...` cannot restore a green hook alone: id 32 is outside
  `EXPECTED_IDS`, so full conformance would also require rewriting three tests (33 -> 34 prompts,
  29 -> 30 `prompt-*.md`) and appending an unexecuted specification to the master (a history of
  executed prompts). That contract evolution belongs to the stream-32 execution, not to a hygiene fix.

## Current State

- The pre-commit hook is green again without `--no-verify`; the 33-prompt contract is untouched.
- Stream 32 is specified but not executed: no plan, no GO, no code.

## Vigilance Points

- Any new file matching `prompt-*.md` or `[0-9][0-9]_STREAM_PCA_DRIFT_*.md` in `prompts/streams/`
  breaks the hook again.
- `prompts/streams/INDEX.md` is historical (the PASSATION document says so) and does not list the spec.
- The amorcage instruction "prise en charge du nouveau fichier par INDEX.md, le master dérivé et
  `tools/check_prompts.py`" now resolves to: outside the discovery globs until the contract evolves.

## Recommendations

- At stream-32 execution, evolve the contract in one commit: add `32` to `EXPECTED_IDS`, update
  `tests/test_check_prompts.py` (33 -> 34 prompts, 29 -> 30 `prompt-*.md`), retitle the spec as
  `## PROMPT 32 — ...` (or add a canonical prompt file), then `--sync-master`.
