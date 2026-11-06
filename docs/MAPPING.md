# Number mapping

Project rule (CLAUDE.md): every reported number traces to a CSV and a script. This file lists only the references verified at base `69d562419be77b17af9e56711a6ae069caa6bfc4`. Stream 21 created it on 2026-11-06 without a repository checking tool. A one-off read-only check, which is not a tracked source or tool, verified the six correspondences (audit §3). The census, the unmapped classes and the gaps are in `docs/audits/stream_21_trace_scope_2026_11_06.md`.

## Coverage of `paper/*.tex` at the base

| Quantity | Count |
|---|---|
| Tagged numbers (`\E{}` macros) | 0 |
| Numeric tokens enumerated (`sec3_theory.tex` 222, `appA_proofs.tex` 285) | 507 |
| Result-bearing occurrences (manual classification, all in `sec3_theory.tex`) | 19 |
| Mapped below to a single cell of a sealed CSV, status `READ_MATCH` | 6 of 19 |
| Not mapped: 1 derived candidate, 5 analytic values with a test reference, 3 analytic values without test or CSV, 4 range endpoints without an identified source | 13 of 19 |

`READ_MATCH` means only one thing: the LaTeX literal equals the source cell rounded by the rule below. It certifies no scientific conclusion, no ARL0, FPR or ADD reading beyond the column definitions, and no other sentence of the paper. It also does not claim that the current code reproduces the CSV: this lot ran neither the producer nor any test.

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

`tools/trace_numbers.py` reads only this table and the Entries table. It refuses, before any read, a CSV path outside `results/` or a LaTeX path outside `paper/`, and it parses the CSV strictly. It exits 0 only when both SHA-256 values match, every key names each Key column once (in any order), the Entries table holds exactly the declared number of rows and every entry is `READ_MATCH`. Literals must be integers: the rounding rule covers 0 decimals, and a decimal literal is refused. On its LaTeX line, a literal counts only as a complete unsigned numeral: digits inside a signed (`-`, `+`, `−`), exponent (`e`, `^`), leading-dot or comma-grouped number do not count. `tests/test_trace_numbers.py` runs the check at every `make check`. Its success covers only the verified subset, Entries of Result-bearing occurrences, and certifies no more than `READ_MATCH` does.

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
