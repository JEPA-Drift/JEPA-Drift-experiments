# Stream 29 re-review — audit-fix1 candidate

Date: 2026-10-31. Verdict: **WITH_FIXES**, limited to three remaining functional issues.

Actual Vibe export: 3.0.4, mistral-large-4/large-4, provider mistral, thinking high, finished exit 0. Parent fresh checks: **75 passed in 73.80s**, pyflakes exit 0. An isolated Codex reviewer rechecked the same plan 29 and all 13 previous findings without another full plan or application mutation.

## Corrections confirmed

Complete trial groups/roles, separate affine/mix costs, full-mode headers, bidirectional failure handling and D6 exception, exact H250, retained blocked identifiers/calibration metadata, actual declared identity, unique primary lineage and manifest paths, complete-input fingerprint, presentation/CI fixes and parsing refusal are present. T1/T2/T3 have 180/220/44 rows and 48/65/58 columns. Primary lineage has 25,888 unique cell keys; all 60 blocked-real T2 rows retain identifiers. The nine outputs match their repeat and declared hashes. The independently recomputed fingerprint equals `84fbbe5be0ef676b71c32c497326a7e2cad27620b4016160bb3fe1185f47fb2e`.

## Remaining issues

1. **Valid date metadata rejected** (`pca_drift_tables.py:88–104`). TEXT_EXTRA lacks spectra.fit_first_day/fit_last_day. Parent's in-memory CSV with 2016-04-07/2019-12-31 raises ValueError on fit_first_day; the loader would report CSV_PARSE_FAILED. Treat these declared `/2` date fields as text and test positive metadata parsing. No real returns are needed.
2. **Applicable fields made optional at every count** (`:37–40`, `:354–360`). Parent removed deff, n_eff, rmst_sd, rmst_se, rmst_lo and det_lo from executed n=40 ALT rows; each was accepted. Producer `_rmst_fields` always sets deff=1, n_eff=n and finite Wilson detection bounds. Only rmst_sd/rmst_se/rmst_lo/rmst_hi are undefined at n=1, and these must be finite at n>1. Restore count-dependent requirements for ALT, and required deff/n_eff for HOLDOUT as well. Correct the invalid n=1 fixture and the documentation/append-only deviation/wrapup interpretation. Never change the producer to fit a fixture.
3. **Orphan provenance after family filtering** (`:1053–1071`, `:1298–1302`). Four lineage records are emitted before a T3 row is filtered away. Parent reproduced **8 extra keys for COV** and **56 for ENERGY**, with zero missing keys; current validation only checks missing cells. Filter before emission and enforce exact equality of output-cell keys and lineage keys (including rejecting extras). Test both families and an injected extra record.

Keep the other corrected contracts intact. Ordinary section comments newly present in the owned Python files should also be removed, retaining only permitted ponytail comments; public function docstrings follow the project's one-line convention. This mechanical cleanup requires no extra test suite.

## Preserved candidate and decision

Archived before this correction as `logs/pca_drift_orchestration/audit-fix1-candidate.tar`, SHA-256 `590c036eb8f903736b978b03bd4520eee5a77031bbb1cc9f8eb8aecdc7f76006`. Primary/repeat are retained as `logs/pca_drift_tables/audit_fix1_primary/` and `audit_fix1_repeat/`; fresh target paths are free. Original Vibe audit-fix1 export and prior rejected candidate remain intact.

No integration/full/stream-30 execution is accepted yet. The next Vibe correction is scoped to these remaining points and regression coverage; no scientific redesign, detector/runner edit, new simulation, real evaluation or dependency change is authorized.
