# Number mapping

Project rule (CLAUDE.md): every reported number traces to a CSV and a script. This file lists only verified references: the six Entries at base `69d562419be77b17af9e56711a6ae069caa6bfc4` and the nine Source entries at base `1440927b49463c13bdd0c819fcd73f30d6a32c31` (lot 21-rest P, 2026-11-07). Stream 21 created it on 2026-11-06 without a repository checking tool. A one-off read-only check, which is not a tracked source or tool, verified the six correspondences (audit §3). The census, the unmapped classes and the gaps are in `docs/audits/stream_21_trace_scope_2026_11_06.md`.

## Coverage of `paper/*.tex` at the base

| Quantity | Count |
|---|---|
| Tagged numbers (`\E{}` macros) | 0 |
| Numeric tokens enumerated (`sec3_theory.tex` 222, `appA_proofs.tex` 285) | 507 |
| Result-bearing occurrences (manual classification, all in `sec3_theory.tex`) | 19 |
| Entries: mapped to a single cell of the sealed J1 CSV, status `READ_MATCH` | 6 of 19 |
| Source entries: mapped to a single cell of the Section 3 analytic CSV, status `READ_MATCH` | 9 of 19 |
| Not mapped: 4 range endpoints without an identified source (l. 111: `13`, `16`, `8`, `11`), status `UNSOURCED` | 4 of 19 |

`READ_MATCH` means only one thing: the LaTeX literal equals the source cell rounded by the rule below. It certifies no scientific conclusion, no ARL0, FPR or ADD reading beyond the column definitions, and no other sentence of the paper. It also does not claim that the current code reproduces the J1 CSV: neither lot 21 nor lot 21-rest P reran the J1 producer. For the Source entries, a test checks that a fresh run of the analytic producer rewrites the committed CSV byte for byte.

## Source of entries 1–6

- **CSV.** `results/e2/e2_cells.csv`, SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` (disk and Git index). It has 47 lines (header plus 46 rows) in native CRLF and is marked `-text`. It was written by the J1 run (`results/e2/J1_report.md`: `make j1`, master seed 20261018), added in `320dea7` and given its exact-path line-ending attribute in `67437b3`. It is read-only and never re-exported or normalised.
- **Producer script.** `experiments/e2_floor_validation.py`, function `arm_g1`, which evaluates the analytic formulas of `jepadrift/floors.py`.
- **LaTeX.** `paper/sec3_theory.tex`, SHA-256 `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013`. Line 52 is the paragraph after Proposition `prop:floor`, in subsection `sec:floor`. Line numbers are valid for this file hash only.
- **Rounding rule.** `{,}` is removed from the LaTeX literal; then `Decimal(cell).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)` must equal the literal at 0 decimals. None of the six cells sits on a tie. An empty, NaN or infinite cell is never mapped, and never as 0.

## Column definitions

The six entries come from analytic columns of the G1 arm: Gaussian i.i.d., known direction, D = 1, SR = 1, so I = SR²/504 nats/day. None of them is a measurement.

- **`first_order`** = ln(γ)/I, computed by `floors.first_order_floor`. It is numerically the evidence budget τ_γ of Lemma 1: **budget** reading. The value depends only on (γ, I), so the `onset`, `cusum_t` and `cusum_x` rows hold the same text. The key fixes `mode=onset` to select exactly one row.
- **`pred_delay`** is the analytic delay predicted for the row's detector:
  - mode `cusum_x`: `floors.cusum_exact`, the CUSUM whose threshold is calibrated to ARL0 = γ.
    - **exact** names this reading (ARL0 calibrated to γ), not the precision of the stored value.
    - The stored value is Φ(γI)/I, the diffusion approximation that `C-e1-readings` (`docs/DEVIATIONS.md`) reports as `add_diffusion_approx`. It is not an exact ADD at finite γ.
    - It certifies no attained ARL0: the CSV holds the Monte Carlo ARL0 separately, in `arl0_mc`.
  - mode `cusum_t`: `floors.cusum_threshold`, the CUSUM e-detector stopped at ln γ, with h' = ln γ + 2ρθ. This is the **anytime-valid** reading.
- **`mean_delay`** is the Monte Carlo mean over the replicates of each row, a measurement. It is not the source of any number in this file.
  - For entry 1 it rounds to the same literal (J1 report: measured 16.730, predicted 16.715). That entry is tied to `pred_delay` by the sentence ("Φ gives Lorden-optimal delays"), not by the rounded value.
  - For entries 2–6 the two columns round to different integers.

## Check inputs

`tools/trace_numbers.py` reads this table, the Entries table and, when both exist, the Sources and Source entries tables at the end of this file. It refuses, before any read, a CSV path outside `results/`, a LaTeX path outside `paper/` and a CSV declared twice, and it parses every CSV strictly. It exits 0 only when every SHA-256 value matches, every key names each Key column of its source once (in any order), each table holds exactly the declared number of rows and every entry is `READ_MATCH`. In the Entries table literals must be integers: the rounding rule covers 0 decimals, and a decimal literal is refused. Source entries are rounded half-even at the exponent of their literal. On its LaTeX line, a literal counts only as a complete unsigned numeral: digits inside a signed (`-`, `+`, `−`), exponent (`e`, `^`), leading-dot or comma-grouped number do not count. `tests/test_trace_numbers.py` runs the check at every `make check`. Its success covers only the verified subset, Entries plus Source entries of Result-bearing occurrences, and certifies no more than `READ_MATCH` does.

| Input | Value |
|---|---|
| CSV | `results/e2/e2_cells.csv` |
| CSV SHA-256 | `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` |
| Key columns | `arm, mode, background, dim, sr_annual, gamma` |
| LaTeX | `paper/sec3_theory.tex` |
| LaTeX SHA-256 | `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` |
| Entries | 6 |
| Result-bearing occurrences | 19 |

## Entries

| # | LaTeX location | Literal | Reading | Full key | Column | Source text | Rounded | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `paper/sec3_theory.tex:52` | `17` | exact | arm=G1, mode=cusum_x, background=gauss, dim=1, sr_annual=1.0, gamma=20 | `pred_delay` | `16.71475236584297` | 17 | `READ_MATCH` |
| 2 | `paper/sec3_theory.tex:52` | `142` | exact | arm=G1, mode=cusum_x, background=gauss, dim=1, sr_annual=1.0, gamma=252 | `pred_delay` | `142.0388135314031` | 142 | `READ_MATCH` |
| 3 | `paper/sec3_theory.tex:52` | `1{,}510` | budget | arm=G1, mode=onset, background=gauss, dim=1, sr_annual=1.0, gamma=20 | `first_order` | `1509.849065871212` | 1510 | `READ_MATCH` |
| 4 | `paper/sec3_theory.tex:52` | `2{,}787` | budget | arm=G1, mode=onset, background=gauss, dim=1, sr_annual=1.0, gamma=252 | `first_order` | `2786.832260105758` | 2787 | `READ_MATCH` |
| 5 | `paper/sec3_theory.tex:52` | `1{,}066` | anytime-valid | arm=G1, mode=cusum_t, background=gauss, dim=1, sr_annual=1.0, gamma=20 | `pred_delay` | `1066.2595750101377` | 1066 | `READ_MATCH` |
| 6 | `paper/sec3_theory.tex:52` | `2{,}322` | anytime-valid | arm=G1, mode=cusum_t, background=gauss, dim=1, sr_annual=1.0, gamma=252 | `pred_delay` | `2321.684670063548` | 2322 | `READ_MATCH` |

Verification: a read-only standard-library check, run on 2026-11-06 with exit 0; the CSV SHA-256 was identical before and after. The command, its output and three negative witnesses are in section 3 of the audit.

A new entry gives:
- the LaTeX file, line and file SHA-256, and the exact literal;
- the CSV path relative to the repository, with its SHA-256;
- a key that selects exactly one row, the column and the source text;
- the rounding rule, the reading and the producer script.
- the updated Entries count of Check inputs; the key names exactly its Key columns.

## Section 3 analytic values

Lot 21-rest P traces nine analytic values of `paper/sec3_theory.tex` to `results/sec3/sec3_analytic.csv` (SHA-256 in Sources), written by `experiments/sec3_analytic_values.py` through `save_fair_csv`. The producer evaluates `jepadrift/floors.py` only: no estimation, Monte Carlo arm or PRNG, and no read of `results/e2`. Its `--out` refuses an existing file. Each row is keyed by `quantity, parameters` and carries the `id`, `reading`, `approximation` and `anchor` that bind it to one occurrence.

- `mixture_multiplier`, D = 1, 10, 64, 500 and 128 at γ = 504 (l. 80): M(D, γ) of Proposition 3 (`floors.mixture_multiplier`), the fluid delay multiplier of the isotropic Gaussian mixture e-process stopped at the e-value threshold γ. Reading **anytime-valid**, approximation **fluid**, anchor `$M=`. The D = 128 row is the trunk multiplier of the sentence; the design bound `D\le16` stays outside the mapping.
- `absorption_ratio`, τ_a/τ_γ = 2.5, 4 and 8 (l. 105): the fluid absorption delay over τ_γ, −(r/2) ln(1 − 2/r) (`floors.absorption_delay(1, r)`). Reading **budget** (a ratio to τ_γ), approximation **fluid**, anchor `\tau_a/\tau_\gamma=`.
- `arl0_over_add_diffusion`, γ = 252 and SR = 1 (l. 52): γ over Φ(γI)/I with I = SR²/504 (`floors.cusum_exact`), the calibrated ARL0 over the diffusion approximation of the delay of the CUSUM calibrated to ARL0 = γ. Reading **exact** (the ARL0 calibration), approximation **diffusion**: not an exact ADD at finite γ. Its denominator equals the `pred_delay` cell of entry 2, which a test checks.

Rounding is half-even at the exponent of the literal, on the cell text: two decimals for `2.01`, one for `5.2` and `1.8`.

The literal `2.01` occurs twice: M at D = 10 on l. 80 and the absorption ratio at τ_a/τ_γ = 2.5 on l. 105. Both cells round to 2.01, so the value alone cannot tell the two occurrences apart. Their anchors are disjoint (`$M=` is absent from l. 105, `\tau_a/\tau_\gamma=` from l. 80), and the selected row must carry the ID, anchor, reading and approximation of the entry. Exchanging the two keys gives `BINDING_MISMATCH`; exchanging all their references gives `ANCHOR_ABSENT` (both tested). An anchor shows only that a text stands on the declared line; it certifies no sentence.

These entries certify that literal, analytic cell and rounding agree. They certify no measured delay, ARL0 or FPR and no reproduction of a measurement. The four range endpoints of l. 111 stay `UNSOURCED`.

## Sources

`tools/trace_numbers.py` reads this table and the Source entries table only when both are present. Each source is a CSV under `results/`, distinct from the CSV of Check inputs, with its SHA-256, its own Key columns and the number of Source entries that use it. Its header must hold the columns `id`, `anchor`, `reading` and `approximation`.

A Source entry gives:
- an occurrence ID, its source, the LaTeX location and literal (integer or decimal) and the anchor of its quantity;
- its reading (`budget`, `anytime-valid` or `exact`) and approximation (`fluid` or `diffusion`);
- a key that names exactly the Key columns of its source, the column, the source text and the rounded value.

The anchor must stand on the LaTeX line, and the selected row must carry the ID, anchor, reading and approximation of the entry.

| Source | CSV | CSV SHA-256 | Key columns | Entries |
|---|---|---|---|---|
| sec3_analytic | `results/sec3/sec3_analytic.csv` | `de6217be14498bb486458257f0d615261b818fea58e18dcfe94c910d4bf0921a` | `quantity, parameters` | 9 |

## Source entries

| ID | Source | LaTeX location | Literal | Anchor | Reading | Approximation | Full key | Column | Source text | Rounded | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ARL0ADD-G252-SR1 | sec3_analytic | `paper/sec3_theory.tex:52` | `1.8` | `expected run to a false alarm` | exact | diffusion | quantity=arl0_over_add_diffusion, parameters=gamma=252; sr_annual=1.0 | `value` | `1.7741629469770654` | 1.8 | `READ_MATCH` |
| M-D1-G504 | sec3_analytic | `paper/sec3_theory.tex:80` | `1.22` | `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=1; gamma=504 | `value` | `1.2239421009676335` | 1.22 | `READ_MATCH` |
| M-D10-G504 | sec3_analytic | `paper/sec3_theory.tex:80` | `2.01` | `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=10; gamma=504 | `value` | `2.0057517760705341` | 2.01 | `READ_MATCH` |
| M-D64-G504 | sec3_analytic | `paper/sec3_theory.tex:80` | `3.91` | `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=64; gamma=504 | `value` | `3.905601272609708` | 3.91 | `READ_MATCH` |
| M-D500-G504 | sec3_analytic | `paper/sec3_theory.tex:80` | `9.64` | `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=500; gamma=504 | `value` | `9.6426581917156557` | 9.64 | `READ_MATCH` |
| M-D128-G504 | sec3_analytic | `paper/sec3_theory.tex:80` | `5.2` | `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=128; gamma=504 | `value` | `5.2252126569106583` | 5.2 | `READ_MATCH` |
| ABS-R2.5 | sec3_analytic | `paper/sec3_theory.tex:105` | `2.01` | `\tau_a/\tau_\gamma=` | budget | fluid | quantity=absorption_ratio, parameters=tau_a/tau_gamma=2.5 | `value` | `2.0117973905426254` | 2.01 | `READ_MATCH` |
| ABS-R4 | sec3_analytic | `paper/sec3_theory.tex:105` | `1.39` | `\tau_a/\tau_\gamma=` | budget | fluid | quantity=absorption_ratio, parameters=tau_a/tau_gamma=4 | `value` | `1.3862943611198906` | 1.39 | `READ_MATCH` |
| ABS-R8 | sec3_analytic | `paper/sec3_theory.tex:105` | `1.15` | `\tau_a/\tau_\gamma=` | budget | fluid | quantity=absorption_ratio, parameters=tau_a/tau_gamma=8 | `value` | `1.1507282898071236` | 1.15 | `READ_MATCH` |
