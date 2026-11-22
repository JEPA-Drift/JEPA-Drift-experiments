# Stream 32 — B4 and final B receipt

20 November 2026. **Lot B is received under B_TDD_ONLY on deterministic fixtures.**
The ordered T1–T68 matrix has **68 PASS, 0 FAIL and 0 NOT_RUN**.
Four campaign-scale verifications are recorded separately as
`DEFERRED_TO_C_RUNTIME`.

## B4 acceptance

- The CLI accepts the configuration, all three modes, jobs, output and log
  directories, resume and describe. The description is available before any
  draw, worker, staging write or GO lookup. Pilot and full require matching
  pre-execution authorization. The mode authorizations in tests are synthetic
  files confined to pytest temporary directories.
- The fixture driver verifies partition and seed plans, spawn workers and
  deterministic BLAS/OMP/MKL settings. Jobs 1 and 3 produce identical
  scientific bytes through the CLI. The budget witnesses cover cumulative CPU,
  invocation wall time, exact publication boundaries and resumable refusal.
- Verified partitions support recovery after each applicable phase and
  across the atomic rename and FINAL boundaries. Stale design, phase or
  payload state is refused. The five FAIR CSVs carry design and calibration
  identities and are bound by manifest hashes. FINAL ties the published
  manifest to the realization. Resource and incomplete cases leave staging.
- The full synthetic CLI materializes H1–H3 from committed inputs. Full
  and pilot publish paired descriptive contrasts with per-family bootstrap
  reuse. The receipt covers publication, test-only values and preserved
  scientific qualifications.
- The final integration witnesses cover common prior, online fallback,
  refusal cases, population support, raw injection, the two CPV90 rules,
  separate gamma identities, surrogate and joint information, and the
  no-real-data and no-prior-output guards.

The technical note and YAML are delivered at
[docs/sections/pca_info_online.md](../docs/sections/pca_info_online.md)
and [configs/pca_info_online.yaml](../configs/pca_info_online.yaml).
The YAML fixes the B draft of R1 and amendment v2.1 with null authorization.
It declares four Gaussian setups, five drift families and 18 policies.
The root seed 3232 follows the reproducible fixture design. The candidate
full configuration uses a role-wide CAL count of 2,000. R3 retains the
separate proposal of 10,000 primary CAL rows and the per-cell allocation
design it would require. The full envelope remains provisional.

## Final Lot B disposition

| Sub-lot | Received evidence |
| --- | --- |
| B1 | Pre-execution design and authorization, hash-based stage lineage, realization and atomic publication primitives |
| B2 | Synthetic Gaussian and T7 proxy setup, population drifts, DEV libraries, frozen policies and HEAD geometry |
| B3 | Separate CAL, NULL_PLAN, HOLD and ALT roles, predictive rank, null qualification, paired inference and analytic diagnostics |
| B4 | CLI and workers, budgets, recovery, FAIR publication, final integration witnesses, YAML and the English schema note |

B3 entered B4 with 1,003 C0 tests passing and 34 PASS in the matrix.
Both accepted B2 and B3 test prefixes were checked byte for byte.
The benchmark producer retained its sealed SHA-256 throughout.
The inherited B2/B3 receipts and the matrix carry the intermediate
results. The final acceptance includes T10, T15, T16, T19, T21 and T22,
the six blocking integration contracts identified by the GO.
[Contract matrix](MATRIX-stream-32-T1-T68-20261114.md)

## Verification

- Locked `make prompts-check` completed with **34/34**.
- Locked `make check` completed with repository-wide pyflakes and pytest
  restricted to the authorized fixtures. The synthetic representation and
  decoupling subset reported **21 passed, 16 deselected in 1.64 s**. The
  PCA-INFO-ONLINE and prompt tests reported **1,063 passed in 93.99 s**.
  An initial collection traversed local archives and was terminated.
  The successful retry excluded the archive, result and data directories.
  The full repository pytest collection includes real panels and was
  outside the Lot B perimeter.
- Locked read-only descriptor checks verified all three modes and the
  pilot/full refusals with null authorization. The YAML values match the
  received draft. The note's relative references resolve. Git diff-check
  passed and the index is empty.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |
| `tests/test_pca_info_online.py` | `19f0925fd3f0079d82341f3920ae4b4248104eb0cb99f96679ebe93977295ea8` |
| Sealed `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| `configs/pca_info_online.yaml` | `63dc10ffb660272cff12bcac69b2fe1bf5754b0ffa207d4b4f415197bb095d56` |
| `docs/sections/pca_info_online.md` | `793c63aa23bcb841ea4ca3fb7286538ed32e7b8ab7eb63184c2e2415784252a7` |
| Contract matrix | `5c55919542b1fabf312abb4d74275da99ef4e5567e450ffc5d42242921081a30` |
| `logs/stream-32/lot-B4-final.make-check-v2.log` | `a167c1ba40d7494f9b728f2c442d4af2bea8e54b70baae7990f6d115caac4a12` |
| `logs/stream-32/lot-B4-final.config-check.log` | `f95ac7e45f781c6edd3e119752e6399815dd65352c491740fe4de21cfa09153c` |
| `logs/stream-32/lot-B4-final.checks.log` | `fcae84db80184a22efe5da3b5f7cb605b7dd8710532d41eda9616c3c75204677` |

## Runtime gates

The candidate-size smoke, recovery at those settings, jobs 1/8
invariance and resource profiling remain gated by a separate Lot C GO.
Pilot and full require their own researcher decisions. The B evidence
is functional and supplies no campaign power, resource measurements or
empirical gains. Work stops at this receipt. HEAD remains
`e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a` on
`stream-32-pca-info-online-20261114`.
