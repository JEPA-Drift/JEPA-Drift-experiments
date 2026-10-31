# Stream 29 implementation review — candidate 1

Date: 2026-10-31. Verdict: **WITH_FIXES — do not integrate this candidate**.

Mistral Vibe 3.0.4 export confirms mistral-large-4, alias large-4, provider mistral, thinking high, finished/exit 0. An isolated read-only Codex reviewer examined only plan 29 and its implementation/specification; no other full plan, scientific run or application mutation was performed by the reviewer. Parent fresh verification: **45 passed in 43.34s**, pyflakes exit 0. Passing tests do not cover the defects below.

## Preserved evidence

The first nine output files match their repeat byte-for-byte, but are not accepted. Source/code/tests/docs/outputs/logs were archived before correction as `logs/pca_drift_orchestration/audit1-candidate.tar`, SHA-256 `b6ba3c18de039ba8fe99aa8cd3666501357c98e7ddb665d9af1a3efd11d12655`. Original primary/repeat directories are retained as `logs/pca_drift_tables/audit1_primary/` and `audit1_repeat/`; the published candidate path was vacated for a fresh corrected rendering. Original Vibe export is retained in `vibe_implementation/`.

## Required corrections and regression coverage

References below are original line numbers in `experiments/pca_drift_tables.py`.

1. **Missing trial inventory (364–380).** The loop visits only existing groups. Parent reproduced acceptance after deleting all trials, deleting an entire calibration group, and relabeling that calibration group's role as alternative. Require every expected successful calibration/ALT/HOLDOUT `(group_id, role)` and exact count, including absent groups, and reject wrong roles/orphans. Test each missing role/group and the empty-frame case.
2. **Affine denominator (1001–1025).** T3 copies M_cost but selects V_affine for affine rows. Existing Gaussian C output: I=1.5890738650928768, displayed M=2.0649289783052449, V=0.83530918523691711; the actual C_affine is 1.9023780573443245. I/displayed cost is 0.7695537627628637, inconsistent with V. Covariance D1 has the same problem. Preserve distinct source M/C values and show the denominator belonging to the declared objective, without recomputing V. Document the final columns and test mean/covariance affine and mixture rows.
3. **Full-mode text (1303–1304).** Headers unconditionally say smoke and planned full/non-executed, even for a full source; full_counts is then absent. Render actual mode and each independent role count. A metadata-only full-shaped fixture must contain no false smoke/non-execution text.
4. **Failure coherence (665–723).** Check synthetic failure status in both directions: failed selections/NA aggregates cannot reference an OK calibration. A failed real D6 calibration must retain its documented exception and blocked real statuses; it must not require synthetic ALT/HOLDOUT/selection cascades. Add positive/negative fixtures for both domains.
5. **Exact horizon (610–622).** NA H is skipped and int(H) admits 250.5. Relevant H must be present and equal exactly 250; test missing and fractional values, without changing measurements.
6. **Lost provenance (538–540, 861–865, 1047–1051).** Parent confirmed all 60 blocked-real T2 rows lose both source metric_id_subset and selection_id_subset. Identifiers must remain when the source contains them, while unavailable measurements stay NA. Absence of a holdout metric must not erase legitimate D6 calibration provenance. Test both cases without reading real returns.
7. **Filters (958, 1083–1124).** T3 admits whole mixed-family groups and T3R ignores all filters. Apply requested dataset/scenario/family filters to every output row/sub-table and lineage. Cover all tables, not just T1.
8. **Strict identity (1495–1505).** Reloading default config and hashing only splits.yaml rejects legitimate custom-config or additional-input artifacts. Recompute identity from the artifact's declared config and input set using the current producer, retaining path and hash checks. Test legitimate nondefault identity metadata and drift refusal; no new scientific run.
9. **Lineage/fingerprint (1059–1062, 1572–1579).** There are 25,752 lineage records for 25,712 unique cell keys (40 duplicates). T3R MANIFEST paths contain literal ellipses and cannot resolve. Require one provenance entry per cell and resolvable exact paths. The documented full-input fingerprint computes `08578c410502a3f5cbef7d5d0a8bf1daaf0bac4f4ef12e0ffadc9c1bfae2a133`, but stored `74f289f4e27c668ec31abe5d6ca1d450c2edca32926889e28b9b3a348942aa0d` hashes a reduced input object. Implement/document one exact full-object recipe and test independent recomputation and second-render equality.
10. **Presentation completeness (1197, 1397).** T3 puts d* before I/RMST; require RMST then d* then FPR. T1 Markdown looks for nonexistent fpr_test_null_lo/hi instead of source fpr_lo/hi and drops holdout intervals. T3 marginal covariance diagnostic lacks its required joint-KL companion. Cover actual rendered output and source provenance.
11. **Controlled parsing refusal (186–191).** Check file hashes before numerical parsing; malformed numeric corruption must produce a controlled exit 2, including well-hashed malformed CSV, not an uncaught traceback.
12. **Legitimate n=1 (333).** Producer ALT RMST SD/SEM/intervals are undefined/NA at n=1. Require only the applicable finite fields and preserve those NAs. Add a valid one-alternative fixture.
13. **Tests and timing.** Replace the tautological `assert ... or True` at original test line 208 with a meaningful assertion. Do not weaken other tests. The wrapup's claim that 43s of new tests fits a five-minute global budget is unsupported: the pre-29 measured baseline was already about 324s. Report actual timing and leave global make check to Codex.

## Scope and decision

These corrections implement the accepted table contract; they authorize no detector/statistical redesign, new q-covariance export, recalibration, real evaluation or runner change. The producer /2 inputs and E2/E3 remain protected. No direct application fix was made by Codex; a focused correction is delegated to Vibe large-4/high. Integration, full execution and stream 30 remain gated until re-review of corrected 29.
