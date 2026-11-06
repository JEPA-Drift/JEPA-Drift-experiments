# Stream 21: traceability scope audit, 2026-11-06

**Authority.** `prompts/GO-stream-21.md` (Codex, 17:49 UTC) and the integrated GO decision in `prompts/plans/plan-21.md`.

**Base and branch.** Base `69d562419be77b17af9e56711a6ae069caa6bfc4`, branch `stream-21`.

**Scope.** This is a documentary lot. It adds no tool, test, run, figure, table, configuration, `paper/` edit or J4 work. Inputs were only read. Run journals are under `logs/stream_21/`, which Git ignores.

**Outputs.** This audit and `docs/MAPPING.md`.

**Out of scope.** Freeze, `FROZEN.json`, runner, figures and `appendix_b`.

## 1. Inputs and integrity

Pre-check at 2026-11-06T17:54:39Z: `HEAD` = base, and the only untracked files were the two Codex files (`prompts/GO-stream-21.md`, `prompts/plans/plan-21.md`).

| File | SHA-256 at the base |
|---|---|
| `paper/sec3_theory.tex` | `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` |
| `paper/appA_proofs.tex` | `4a5469c84f12bb5902fee9f68a783b64c45b77b11f1172c5bf4b81f7603c2a30` |
| `results/e2/e2_cells.csv` (disk and `git show :results/e2/e2_cells.csv`) | `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` |
| `results/e2/J1_report.md` | `7a53b80dce0d1c78f3e34d145e02d5a9a94f53e0bef2070f2197141aad7f1831` |
| `experiments/e2_floor_validation.py` | `f4360ac3961fcd01e36824cb10d3572be0ec83d767ee17bc56010840de4b46c7` |
| `jepadrift/floors.py` | `49b36c5ef1b7995a274243180825731d42a61829c70e00fc7fc72841d39a9170` |
| `tests/test_floors.py` | `0457f3e8f7828324986a384d0e53175061e54d010d95d99666c768369138dc29` |

- **J1.** 47 lines, all 47 end in CRLF, 0 lines lack a CR.
- **D8.** Remains FAIL at +5.2833 %; this audit does not re-examine it.

## 2. Census of numerals in `paper/*.tex`

### 2.1 Mechanical enumeration

```bash
command grep -noE '[0-9]+(\{,\}[0-9]{3})*(\.[0-9]+)?' paper/sec3_theory.tex paper/appA_proofs.tex
```

The command ran with GNU grep 3.6 and gave one token per match:
- a thousands-grouped literal such as `1{,}510` is one token;
- `\S3.1.7` yields `3.1` and `7`.

Result: 222 tokens in `sec3_theory.tex` and 285 in `appA_proofs.tex`, 507 in total.

`paper/` contains no `\E{}` macro and no `\newcommand`, so the number of tagged numbers is 0. The experimental sections that `sec3_theory.tex` cites (`sec:exp-floors`, `sec:problem`, `sec:method`) are not in `paper/`.

### 2.2 Classification rule

Every token was classified by reading its context. The class definitions are:

| Class | Content |
|---|---|
| R, result-bearing | A value the text states as the outcome of an evaluation, computation or measurement (delay, multiplier, ratio, order of a term). |
| P, stated parameter | An input of a stated computation or example: γ, D, SR, τ_a/τ_γ, GARCH order and coefficients, Student degrees of freedom, trunk dimension 128. |
| B, design bound | `D \le 16` (l. 80), a design choice drawn from the values of M, not a computed value. |
| K, literature constant | Siegmund's ρ: `0.583` in sec3 l. 42 and `0.5826` in appA l. 22 (`floors.RHO_GAUSS = 0.5826`). |
| C, citation year or pointer | Years inside citation keys; `\S3.1.7` and `Thm.~2` inside citation options. |
| L, list layout | `itemsep=1pt`, `topsep=2pt`. |
| S, proof-step label | `Step~1` to `Step~4`, `Steps~1 and~2`. |
| H, comment | LaTeX comment lines, not rendered. |
| F, formula and notation | Indices, exponents, labels (N1)–(N3), interval bounds, coefficients of stated formulas and asymptotic expansions (sec3 l. 47, appA l. 23), the symbolic exponents of Corollary `cor:scaling` (sec3 l. 83), and the constants 504 and 252 inside formulas (sec3 l. 37 and 48, appA l. 24). |

Counting rules:
- **Occurrences.** Each occurrence counts once. For example, `2.01` appears twice (l. 80 and l. 105) as two different quantities, and both count.
- **Ranges.** A range "a to b" counts as two endpoint occurrences.

### 2.3 Counts

| Class | `sec3_theory.tex` | `appA_proofs.tex` | Total |
|---|---|---|---|
| R result-bearing | 19 | 0 | 19 |
| P stated parameter | 18 | 0 | 18 |
| B design bound | 1 | 0 | 1 |
| K literature constant | 1 | 1 | 2 |
| C citation year or pointer | 16 | 13 | 29 |
| L list layout | 4 | 0 | 4 |
| S proof-step label | 0 | 7 | 7 |
| H comment | 10 | 5 | 15 |
| F formula and notation | 153 | 259 | 412 |
| **Total** | **222** | **285** | **507** |

A cross-check over the 68 lines that hold tokens found that, on every line, the class counts sum to the enumerated token count (`bad=0`, in `logs/stream_21/census_crosscheck.log`). This check covers the arithmetic only. The class assignment itself is manual; Appendix A lists it per line for review.

### 2.4 Result-bearing occurrences

The census finds 19 result-bearing occurrences, all in `paper/sec3_theory.tex`. This count was measured; it was not imposed.

| # | Line | Literal | Quantity stated | Status | Evidence |
|---|---|---|---|---|---|
| 1 | 52 | `17` | Lorden-optimal delay, SR = 1, γ = 20 | `READ_MATCH` | `MAPPING.md` entry 1 |
| 2 | 52 | `142` | Lorden-optimal delay, SR = 1, γ = 252 | `READ_MATCH` | entry 2 |
| 3 | 52 | `1{,}510` | τ_γ, SR = 1, γ = 20 | `READ_MATCH` | entry 3 |
| 4 | 52 | `2{,}787` | τ_γ, SR = 1, γ = 252 | `READ_MATCH` | entry 4 |
| 5 | 52 | `1{,}066` | anytime-valid CUSUM delay, SR = 1, γ = 20 | `READ_MATCH` | entry 5 |
| 6 | 52 | `2{,}322` | anytime-valid CUSUM delay, SR = 1, γ = 252 | `READ_MATCH` | entry 6 |
| 7 | 52 | `1.8` | "1.8 times shorter than its expected run to a false alarm", γ = 252 | `DERIVED_CANDIDATE` | §4.1 |
| 8 | 80 | `1.22` | M(1, γ = 504) | `ANALYTIC_TEST_REFERENCE` | §4.2 |
| 9 | 80 | `2.01` | M(10, γ = 504) | `ANALYTIC_TEST_REFERENCE` | §4.2 |
| 10 | 80 | `3.91` | M(64, γ = 504) | `ANALYTIC_TEST_REFERENCE` | §4.2 |
| 11 | 80 | `9.64` | M(500, γ = 504) | `ANALYTIC_TEST_REFERENCE` | §4.2 |
| 12 | 80 | `5.2` | M(128, γ = 504), JEPA trunk | `ANALYTIC_UNPINNED` | §4.3 |
| 13 | 105 | `2.01` | absorption fluid delay / τ_γ at τ_a/τ_γ = 2.5 | `ANALYTIC_TEST_REFERENCE` | §4.2 |
| 14 | 105 | `1.39` | same, τ_a/τ_γ = 4 | `ANALYTIC_UNPINNED` | §4.3 |
| 15 | 105 | `1.15` | same, τ_a/τ_γ = 8 | `ANALYTIC_UNPINNED` | §4.3 |
| 16 | 111 | `13` | lower endpoint, order of the volatility-memory term, GARCH(1,1) (0.08, 0.90), Student-t7 | `UNSOURCED` | §4.4 |
| 17 | 111 | `16` | upper endpoint of the same range | `UNSOURCED` | §4.4 |
| 18 | 111 | `8` | lower endpoint, "Section `sec:exp-floors` measures 8 to 11" | `UNSOURCED` | §4.4 |
| 19 | 111 | `11` | upper endpoint of the same range | `UNSOURCED` | §4.4 |

Per status, out of 19: 6 `READ_MATCH`, 1 `DERIVED_CANDIDATE`, 5 `ANALYTIC_TEST_REFERENCE`, 3 `ANALYTIC_UNPINNED`, 4 `UNSOURCED` (two ranges). No global coverage rate is stated.

### 2.5 Excluded stated values

These are excluded from R and listed so that the exclusions can be reviewed:

- **P (18).**
  - l. 52: `SR=1`, `\gamma=20`, `252`, `\gamma=252`.
  - l. 80: `\gamma=504`, `D=1`, `10`, `64`, `500`, `128`.
  - l. 105: `2.5`, `4`, `8`.
  - l. 111: the GARCH order `(1,1)` (two tokens), `(0.08,0.90)` and `t_7`.
- **B (1).** l. 80, `D\le16`.
- **K (2).** sec3 l. 42, `\rho\approx0.583`; appA l. 22, `\rho=0.5826`.

The remaining classes (C, L, S, H, F) are notation, layout or bibliography; Appendix A gives them per line.

## 3. Read check of the six single-cell correspondences

**Command.** `.venv/bin/python -I - < read_check_e2.py`, run at 2026-11-06T17:59:41Z under Python 3.12.9. The environment exports from `prompts/GO-stream-21.md` were set. The script is reproduced verbatim below; it is not a tracked source or tool. Its SHA-256 is `ea5d348bc040dfe20c91462e7b4ed9450d9862c929f2c0cf4a8a0eac3b0f61b1`.

**Script constraints.** It imports only the standard library: no project module, numpy or pandas. It opens the CSV read-only with `newline=""` and compares SHA-256 before and after the read. It computes no estimator.

```python
import csv
import hashlib
import re
import sys
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from pathlib import Path

CSV = Path("results/e2/e2_cells.csv")
TEX = Path("paper/sec3_theory.tex")
SHA = "e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823"
NUM = re.compile(r"[0-9]+(?:\{,\}[0-9]{3})*(?:\.[0-9]+)?")
BASE = {"arm": "G1", "background": "gauss", "dim": "1", "sr_annual": "1.0"}
ENTRIES = [
    ("17", 52, "cusum_x", "20", "pred_delay"),
    ("142", 52, "cusum_x", "252", "pred_delay"),
    ("1{,}510", 52, "onset", "20", "first_order"),
    ("2{,}787", 52, "onset", "252", "first_order"),
    ("1{,}066", 52, "cusum_t", "20", "pred_delay"),
    ("2{,}322", 52, "cusum_t", "252", "pred_delay"),
]

before = hashlib.sha256(CSV.read_bytes()).hexdigest()
lines = TEX.read_bytes().decode("utf-8").splitlines()
with CSV.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
ok = before == SHA
print(f"csv {CSV} sha256 {before} rows {len(rows)}")
print(f"tex {TEX} sha256 {hashlib.sha256(TEX.read_bytes()).hexdigest()}")
for literal, line, mode, gamma, column in ENTRIES:
    key = {**BASE, "mode": mode, "gamma": gamma}
    hits = [r for r in rows if all(r[k] == v for k, v in key.items())]
    count = NUM.findall(lines[line - 1]).count(literal)
    status, cell, rounded = "READ_MATCH", "", ""
    if count != 1:
        status = f"LITERAL_OCCURRENCES_{count}"
    elif len(hits) != 1:
        status = f"KEY_ROWS_{len(hits)}"
    else:
        cell = hits[0][column]
        try:
            value = Decimal(cell)
        except InvalidOperation:
            value = Decimal("NaN")
        if not value.is_finite():
            status = "EMPTY_OR_NON_FINITE"
        else:
            rounded = value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
            if rounded != Decimal(literal.replace("{,}", "")):
                status = "MISMATCH"
    ok &= status == "READ_MATCH"
    print(f"{TEX}:{line} literal {literal!r} | key {key} | column {column} | cell {cell!r} | rounded {rounded} | {status}")
after = hashlib.sha256(CSV.read_bytes()).hexdigest()
ok &= after == before
print(f"csv sha256 after {after} | unchanged {after == before} | expected {before == SHA}")
sys.exit(0 if ok else 1)
```

**Output, verbatim, exit code 0.**

```text
csv results/e2/e2_cells.csv sha256 e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823 rows 46
tex paper/sec3_theory.tex sha256 6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013
paper/sec3_theory.tex:52 literal '17' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'cusum_x', 'gamma': '20'} | column pred_delay | cell '16.71475236584297' | rounded 17 | READ_MATCH
paper/sec3_theory.tex:52 literal '142' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'cusum_x', 'gamma': '252'} | column pred_delay | cell '142.0388135314031' | rounded 142 | READ_MATCH
paper/sec3_theory.tex:52 literal '1{,}510' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'onset', 'gamma': '20'} | column first_order | cell '1509.849065871212' | rounded 1510 | READ_MATCH
paper/sec3_theory.tex:52 literal '2{,}787' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'onset', 'gamma': '252'} | column first_order | cell '2786.832260105758' | rounded 2787 | READ_MATCH
paper/sec3_theory.tex:52 literal '1{,}066' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'cusum_t', 'gamma': '20'} | column pred_delay | cell '1066.2595750101377' | rounded 1066 | READ_MATCH
paper/sec3_theory.tex:52 literal '2{,}322' | key {'arm': 'G1', 'background': 'gauss', 'dim': '1', 'sr_annual': '1.0', 'mode': 'cusum_t', 'gamma': '252'} | column pred_delay | cell '2321.684670063548' | rounded 2322 | READ_MATCH
csv sha256 after e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823 | unchanged True | expected True
```

**Negative witnesses.** The same script was altered in memory with `sed` and piped to `.venv/bin/python -I -`. No file was written. Each witness exited with code 1:
- **W1.** Entry 2 reads `mean_delay` (Monte Carlo mean) instead of `pred_delay`: cell `'145.081'`, rounded 145, `MISMATCH`. The two columns differ at the printed precision for this entry.
  - This does not hold for entry 1. `results/e2/J1_report.md` gives a measured 16.730 against a predicted 16.715, and both round to 17. The column choice for entry 1 therefore rests on the sentence ("Φ gives Lorden-optimal delays"), not on the rounded value.
- **W2.** Literal `17` replaced by `18`: `LITERAL_OCCURRENCES_0`.
- **W3.** `mode` removed from the key: `KEY_ROWS_3` for all six entries, which shows that the mode is required to select one row.

After the witnesses, `sha256sum` of the CSV still gave `e315e537…0823`.

**What `READ_MATCH` attests.** Literal, cell and rounding agree, for an analytic column (`pred_delay` or `first_order`). It is not a measured delay, not a Monte Carlo agreement and not a reproduction by the current code.

Entries 1 and 2 carry the reading name **exact** because the CUSUM threshold is calibrated to ARL0 = γ. Their stored value Φ(γI)/I is a diffusion approximation (`add_diffusion_approx` in `C-e1-readings`, `docs/DEVIATIONS.md`), not an exact ADD at finite γ. `READ_MATCH` certifies no attained ARL0.

## 4. Unmapped classes, reported without resolution

No number below is declared wrong for lack of a CSV. None is entered in `docs/MAPPING.md`.

### 4.1 Derived candidate: `1.8` (l. 52)

- **Candidate derivation (inferred from the sentence, not stated in the paper).** The ratio of the expected run to a false alarm to the expected delay of the calibrated CUSUM at γ = 252. Within the read scope, the operands would be the `arl0_pred` and `pred_delay` columns of the row `arm=G1, mode=cusum_x, background=gauss, dim=1, sr_annual=1.0, gamma=252`.
- **Status.** This lot neither evaluated nor rounded the ratio. The candidate is unverified, and the paper's wording is not interpreted further.

### 4.2 Analytic values with an existing test reference (5)

These values are referenced by `tests/test_floors.py`:
- l. 80, `1.22`, `2.01`, `3.91`, `9.64`: `test_mixture_multiplier_table` asserts `|floors.mixture_multiplier(D, 504) - ref| < 0.01` for D = 1, 10, 64, 500, with the same reference literals.
- l. 105, `2.01`: `test_absorption_threshold` asserts `|floors.absorption_delay(100, 250) / 100 - 2.012| < 1e-3`, i.e. τ_a/τ_γ = 2.5.

Neither test was run in this lot. Per the mandate, Codex verified the base before the worktrees were created: 37 + 589 tests passed, with 5 pre-existing D4 skips. A test reference ties these values to code, not to a CSV.

### 4.3 Analytic values without test or CSV (3)

- l. 80, `5.2`: the analytic function is `floors.mixture_multiplier` (D = 128, γ = 504).
- l. 105, `1.39` and `1.15`: the analytic function is `floors.absorption_delay` (τ_a/τ_γ = 4 and 8).

No test or CSV in the read scope holds these values, and this lot evaluated none of them.

### 4.4 Ranges without an identified source (2 ranges, 4 endpoints, l. 111)

- **`13` to `16`.** The text gives this range as the order CV²(I_t)·τ_int(I_t) for a GARCH(1,1) with (α, β) = (0.08, 0.90) and Student-t7 innovations. No CSV column, script output or documented formula in the read scope yields these endpoints.
  - Context only: the docstring of `experiments/e2_floor_validation.py` (l. 18–19) describes the same term as "about 10-15 days here". It is a comment, not a sourced value. The difference from the paper's endpoints is recorded here and resolved neither way.
- **`8` to `11`.** The text attributes this range to a measurement in Section `sec:exp-floors`, which is absent from `paper/`.
  - The S1/S2 rows of `results/e2/e2_cells.csv` are the GARCH-background measurements in the read scope. No document states which rows or which formula would yield these endpoints, so no candidate is proposed.
  - `paper/appA_proofs.tex` l. 32 also defers an error measurement to `sec:exp-floors`, without a numeral.

## 5. Existing traceability layers and overlap

| Layer | What it covers | Relation to `paper/` |
|---|---|---|
| PCA tables: `table_lineage.csv`, `table_manifest.json` (prompt 29 §5) | Every displayed cell of `Tableau_PCA_1–3` points to its source file and row key, or to a formula and its inputs; the manifest records code and source hashes | No PCA number is cited in `paper/` |
| PCA figures: `figure_manifest.json`, `Figure_1_*_source.csv` (prompt 30) | Each plotted point carries its upstream `metric_id` and the source fingerprints | No PCA figure is cited in `paper/` |
| Runner manifest `manifest.json` (prompt 28) and the 44 tests of `tests/test_pca_drift_contracts.py` (prompt 31) | Run fingerprint, cross-table identities, provenance; `E2_SHA` (l. 41) pins the J1 CSV hash | Pins the CSV used by entries 1–6; covers no LaTeX prose |
| E2/J1: `results/e2/J1_report.md` | Quotes the same six cells at 3 decimals, beside the Monte Carlo means | Source of `MAPPING.md` entries 1–6 |
| Analytic floors: `tests/test_floors.py` | Reference values of M at γ = 504 and of the absorption ratio at 2.5 | Covers 5 result occurrences by test reference (§4.2) |
| Data manifests: `data/derived/MANIFEST.json`, `docs/manifests/d4_manifest.json` | Input data hashes | No paper number |
| Wrapups | SHA-256 of stream outputs | Output provenance, not paper numbers |

- **Gap.** No existing layer maps LaTeX prose to a source; `docs/MAPPING.md` now does so for 6 of the 19 occurrences.
- **Context outside the census.** The CLAUDE.md glossary quotes 142 and 2,787 for SR = 1 and γ = 252, consistent with entries 2 and 4.

## 6. DPI wording scan

The scan used the two patterns of prompt 21 §5, plus the gapped form of the second one, in case-insensitive line mode (`command grep -nEi '<pattern>' paper/sec3_theory.tex paper/appA_proofs.tex`). Output is in `logs/stream_21/dpi_pattern_scan.log`.

| Pattern | Matching lines |
|---|---|
| `increase[sd]?.*(KL\|information\|divergence)` | 0 |
| `creates? information` (adjacent, the prompt's form) | 0 |
| `creates?.*information` (gapped) | 1: sec3 l. 25, match `creates no information` |

The single match is the sentence "An encoder creates no information", which correctly states the data-processing inequality by negation. It is therefore a false positive.

Limits of the scan:
- It matches per source line, and `sec3_theory.tex` stores whole paragraphs on single lines, so matches can span sentences.
- It does not handle negation.
- It does not see paraphrases.

This is a pattern scan of two files. It is not a semantic check, and nothing beyond these patterns is claimed.

## 7. Decision and future gates

**Decision (GO, Q1).** No repository checking tool now. The corpus has 0 tagged numbers, and the 6 single-cell correspondences are verified once, by the recorded and reproducible command of §3. A generic checker has no established need at this scope.

**Future gates**, each requiring its own GO:

- **G-T, `tools/trace_numbers.py` and `tests/test_tools.py`.**
  - *Opens:* at the first CSV-sourced number outside E2, or the first tagged number, in `paper/`.
  - *Minimal contract:*
    - standard library only, no numpy, pandas or `jepadrift` import;
    - relative POSIX paths under `paper/` and `results/`;
    - refusal before any open of absolute paths, `..`, `data/raw/**` and `data/derived/d4_eurofidai/**`;
    - one row per key;
    - NA, empty or non-finite cells refused, never read as 0;
    - explicit `Decimal` rounding;
    - each literal present once;
    - CSV read with `newline=""` and never rewritten;
    - counters reported with their denominators.
  - *Tests:* TDD on fake fixtures (positive case, altered number, ambiguous or absent key, NA, .5 tie, refused path), then pyflakes and the 44 sealed contracts.
- **G-D, `dpi_lint`.**
  - *Opens:* if the theoretical prose grows beyond `sec3_theory.tex` and `appA_proofs.tex`.
  - *Requirements:* negation handling, and a description as a pattern lint.
- **G-J4.**
  - *Covers:* freeze, `FROZEN.json`, runner, figure scripts and `appendix_b`.
  - *Requirements:* a distinct J4 GO, and one runner that reuses `experiments/pca_drift_benchmark.py`.
- **Gaps of §4.**
  - *Sources:* sources for the ranges of §4.4 come from the authors of `sec:exp-floors`.
  - *Tests:* tests for the values of §4.3 require a separate GO.

## 8. Limits of this audit

- No experiment, run, test or rebuild; no claim that the current code reproduces any CSV.
- The class assignment of §2 is manual. Only its arithmetic is cross-checked.
- `READ_MATCH` covers 6 occurrences and their analytic columns only. It certifies no ARL0, FPR or ADD reading, no scientific conclusion and no other sentence.
- The label **exact** on entries 1 and 2 names the ARL0-calibrated reading. Their values are diffusion approximations Φ(γI)/I (`C-e1-readings`), not exact ADD values at finite γ.
- The census covers `paper/*.tex` at the base hashes of §1. Other documents appear as context only.

## Appendix A. Per-line class assignment

`S` = `paper/sec3_theory.tex`, `A` = `paper/appA_proofs.tex`. Each entry gives a class letter and its count on that line, with the tokens in brackets where they are informative. The journal copy is `logs/stream_21/census_classes.log`.

```text
S:2 H5                S:5 H3                S:6 H2
S:11 F15 C3[1998 1939 2023]
S:16 F2   S:17 F2   S:18 F1   S:19 F2
S:25 F10 C2[2019 2026]
S:30 F4   S:32 F2   S:34 F1
S:37 F4[incl. 504 504] C3[2026 1998 2014]
S:40 F2
S:41 L2[itemsep=1pt topsep=2pt]
S:42 F3 C3[1971 2024 1985] K1[0.583]
S:43 F3 C1[1986]
S:45 F2   S:47 F8
S:48 F8[incl. 504 252 504]
S:52 F7 P4[SR=1, gamma=20, 252, gamma=252] R7[17 142 1{,}510 2{,}787 1{,}066 2{,}322 1.8]
S:55 F5   S:57 F1   S:58 F3   S:59 F1   S:61 F3
S:64 F1 C1[2026]
S:68 F2 C2[2014 2015]
S:71 F8
S:72 L2[itemsep=1pt topsep=2pt]
S:73 F3   S:74 F5   S:75 F3   S:76 F1
S:80 P6[gamma=504, D=1 10 64 500, 128] R5[1.22 2.01 3.91 9.64 5.2] B1[16]
S:83 F10  S:89 F11  S:93 F1
S:96 F1 C1[2026]
S:99 F7   S:103 F6
S:105 F4 R3[2.01 1.39 1.15] P3[2.5 4 8]
S:111 F1 P5[GARCH(1,1) 1 1, 0.08 0.90, t_7 7] R4[13 16 8 11]
A:2 H5
A:7 F5 C3[3.1 7 (S3.1.7) 2004]
A:8 F4
A:9 F2 C1[1959]
A:10 F13 C1[2006]
A:13 F4 S1   A:14 F11   A:15 F6 S1   A:16 F10 S1   A:17 F2 S2
A:18 F3   A:19 F2
A:22 F21 C4[2 (Thm.~2) 1971 1975 1985] K1[0.5826]
A:23 F35 C2[1986 1985]
A:24 F11[incl. 252 504 504]
A:27 F32
A:30 F17 C2[1970 2020]
A:31 F20  A:32 F7   A:33 F4   A:36 F3   A:39 F23  A:42 F6
A:45 F9 S2
A:46 F9
```
