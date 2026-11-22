# Stream 32 — Independent Full Gaussian audit

22 November 2026. Both passes returned `PASS` with zero discrepancies. The auditor reads the committed maxima and first-hit vectors and recomputes the required statistics without importing decision functions from the experiment. The audit applies to Full Gaussian realization `d574db30705b7257567131dd5fdf3c26c4308b4de32f7a5382b34b853457646a`. [Full receipt](RECEIPT-stream-32-full-gaussian-20261120.md) · [Auditor](../logs/stream-32/audit-full-gaussian.py)

| Audit pass | UTC seal | Report SHA-256 |
| --- | --- | --- |
| Pre-ALT | `2026-11-22T14:23:14Z` | `0a92180f4831f63db177bf3b274c8983755ded98359929eaebdfa40875754721` |
| ALT | `2026-11-22T14:23:34Z` | `7ef843ae2a3b690ac9b1f84886998df075fac5d02f7e3b477f0fb4b09aba5588` |

The pre-ALT pass verified CAL ranks and thresholds, `NULL_PLAN`, HOLD cohorts and FPR, one-sided Clopper–Pearson bounds and status, paired discordances and Tango intervals, and the primary HEAD geometry. The ALT pass verified the pre-ALT report and input hashes before reading ALT. It then reproduced the H1–H3 RMST, bootstrap bounds, HEAD detectability and decisions. It checked all 20 ALT partitions and verified the CSV, manifest and FINAL bindings. [Pre-ALT JSON](../logs/stream-32/full-gaussian-audit-pre-alt.json) · [ALT JSON](../logs/stream-32/full-gaussian-audit-alt.json)

## Calibration and HOLD

CAL verified three cells at 10,000 paths and 176 at 2,000 paths. `NULL_PLAN` independently selected the 20,000 cap with `PLAN_CAPPED_EXPECT_INCONCLUSIVE`, plan ID `445d7561a4139ea0a65bcd42b35fd03e85aee86849d29069e367745cc62a27e7`. The three primary policies share all 20,000 realized HOLD path identities. Among 520 descriptive contrasts, 124 pair a 2,000-path candidate with a 20,000-path reference and use only the verified 2,000 common paths. Another 380 use two 2,000-path cells and 16 use two 20,000-path cells. Each individual bound uses its cell's full cohort. [CAL and HOLD audit](../logs/stream-32/full-gaussian-audit-pre-alt.json) · [Contrast provenance](../results/pca_info_online/full-gaussian/aggregates.csv)

| Policy at FITTED_LW_GAUSSIAN N239, fit 0, RESIDUAL | Calibration ID | Alarms / 20,000 | FPR | One-sided CP lower and upper bounds | Null status |
| --- | --- | ---: | ---: | --- | --- |
| `ONLINE_INFO_MIX_W128` | `850da9c349a89f9f` | 1,169 | 5.845% | 5.5744%, 6.1251% | `NULL_INCONCLUSIVE` |
| `ONLINE_PREFIX_MIX_W128` | `6479cb5c514fdabb` | 1,135 | 5.675% | 5.4082%, 5.9514% | `NULL_VALIDATED` |
| `FULL_K` | `37037fb9d51e227c` | 1,075 | 5.375% | 5.1150%, 5.6446% | `NULL_VALIDATED` |

| HOLD policy class | `NULL_VALIDATED` | `NULL_INCONCLUSIVE` | `NULL_FAILED` |
| --- | ---: | ---: | ---: |
| Non-oracle | 30 | 69 | 0 |
| Oracle, non-deployable | 43 | 37 | 0 |

The individual cutoff is 6%. INFO's upper CP bound exceeds that cutoff. Paired FPR equivalence uses the difference INFO minus comparator on the common HOLD cohort. The three claims satisfy the prespecified ±1 percentage-point margin at the attained FPRs. Tango and the paired percentile bootstrap carry their asymptotic qualifications. [HOLD check](../results/pca_info_online/full-gaussian/trials_summary.csv) · [Recorded issues](../results/pca_info_online/full-gaussian/issues.csv)

## Confirmatory results

All three rows use RMST to horizon 250 days and 10,000 paired bootstrap draws on 2,000 ALT trajectories per family. The table reports the estimated RMST difference as INFO minus comparator. The H1 and H3 bounds are one-sided lower bounds on the gain in days, defined as comparator minus INFO. The H2 bound is one-sided and upper for RMST(INFO) minus 1.10 × RMST(PREFIX). Entries are rounded from the sealed outputs. [Confirmatory rows](../results/pca_info_online/full-gaussian/aggregates.csv) · [Independent recomputation](../logs/stream-32/full-gaussian-audit-alt.json)

| Claim and comparator | INFO RMST | Comparator RMST | Difference (days) | Decision bound (days) | Paired Tango FPR bounds (percentage points) |
| --- | ---: | ---: | ---: | ---: | --- |
| H1, PREFIX on F2, superiority | 86.570 | 91.249 | −4.679 | Gain ≥ 4.1163 | [−0.1943, +0.5348] |
| H2, PREFIX on HEAD, 10% non-inferiority | 78.353 | 83.670 | −5.317 | Upper −13.2686 | [−0.1943, +0.5348] |
| H3, FULL_K on F2, superiority | 86.570 | 87.579 | −1.009 | Gain ≥ 0.5250 | [+0.1116, +0.8300] |

The paired HOLD discordance counts (INFO-only, comparator-only) are (602, 568) against PREFIX and (615, 521) against FULL_K. HEAD passes both gates. The minimum geometry fraction over the 16 profiles is 0.961824 against κ_geo = 0.80, and the upper PREFIX RMST bound is 84.396175 days against κ_det H = 200 days. The three published decisions are `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR`. They apply to the frozen Gaussian fit and the preregistered comparisons. The remaining 520 contrasts retain `DESCRIPTIVE_NOMINAL`, and the historical Pilot null failures remain separate. [HEAD and bootstrap evidence](../logs/stream-32/full-gaussian-audit-alt.json) · [Pilot audit](AUDIT-stream-32-pilot-null-20261120.md)
