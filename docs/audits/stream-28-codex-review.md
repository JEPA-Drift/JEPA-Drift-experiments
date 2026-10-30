# Stream 28 — independent review and verification, 2026-10-30

Original review: **with fixes**. Current closeout re-review: **ready, subject to the final integration gates below**. No application code was changed by Codex.

## Original required correction (before Vibe closeout)

`experiments/pca_drift_benchmark.py:535` can produce a floating batch size from `mem_bytes // cov_batch_bytes(d)`. `range()` at line 540 then raises TypeError. Production memory limits and Run.available_bytes are floats; the existing reduced-memory test uses an integer and misses this path.

Codex reproduced the problem in the pinned project .venv with 6x6 identity/diagonal SPD matrices, chunk=20000 and mem_bytes=3.0*cov_batch_bytes(6)=5184.0. Result: `TypeError: 'float' object cannot be interpreted as an integer`. This is an engineering resource-boundary failure, not a failure of the statistical rank rule.

Required plan: preserve the exact search; normalize the effective batch size to an integer, test a floating budget that forces reduction, retain integer-budget tests and verify that an insufficient floating budget yields BLOCKED_RESOURCE. No approximate fallback.

## Original metadata correction (before Vibe closeout)

`configs/pca_drift_benchmark.yaml:1` still declares pca_drift_benchmark/1. The completed smoke manifest has root schema /2, identity schema /2 and config.schema_version /1. Align the configuration with /2 before sealing; never edit generated manifests manually. Configuration and code fingerprints change, so corrected evidence must be produced in fresh directories.

## Independently checked evidence

- Fresh `python -m pytest -q tests/test_pca_drift_benchmark.py`: **48 passed in 7.91s**, exit 0. This suite does not currently cover the floating-budget failure above.
- All seven current /2 files are byte-identical between results/pca_drift_benchmark/smoke_predictive_v2/ and logs/pca_drift_benchmark/smoke_predictive_v2_repeat/out/.
- Primary /2 manifest SHA-256: `45afe273f400c5a48aa8b29d49304c74e628f3547aa9340e2fe4fe63cbe25768`.
- E2 SHA-256 on disk and in index: `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`; Git reports i/crlf, w/crlf, attr/-text.
- Historical E3 D8 FAIL text remains present, including `relative gap +0.0528334213 > 0.05`.

The read-only reviewer found no further blocker in predictive rank/GE/GT, exchangeability scoping, holdout separation, scan equation, joint covariance objective or metric reuse. The default smoke does not exercise the reduced-memory crash. No make check integration gate, full run, reindex, commit, push or merge has been completed.

## Deferred judgments

Full-run cost remains an extrapolation, not a measured result. The schema and artifacts will be reconsidered after the two corrections and a fresh double smoke. Under the researcher's current policy, Claude Code may produce only the focused correction/closure plan; implementation awaits an authorized implementer. Streams 29–31 remain unopened.

## Closeout re-review and fresh parent verification

The researcher subsequently authorized Vibe large-4/high. Its completed closeout was independently re-reviewed: no blocking finding remains. The float batch cap is integral, insufficient finite budgets retain ResourceBlocked, non-finite budgets are refused, configuration resources are finite and positive, and configuration/schema version is checked against /2. The two regressions cover the production floating-budget path and homogeneous schema. No change was found in the exact search, batch resource checks, KL calculations, detectors or predictive rule.

Parent verification after Vibe exit:
- 50 stream tests passed in 7.95s; pyflakes exited 0.
- All seven closeout files are byte-identical to their repeat.
- Root, identity and configuration all declare pca_drift_benchmark/2.
- Current source/configuration/environment/input identity was recomputed and matches fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.
- Closeout manifest SHA-256: `0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9`.
- Actual Vibe export: version 3.0.4, alias large-4, model mistral-large-4, provider mistral, thinking high, outcome finished, exit 0.
- E2 disk/index SHA and CRLF and the original E3 D8 FAIL text were rechecked.

The final global make check, required AST-only/no-AI indexing and Git delivery gates must still complete before integration. Full runs and post-2019 real evaluations remain outside the authorized closeout. Earlier observations above are preserved as historical review evidence.
