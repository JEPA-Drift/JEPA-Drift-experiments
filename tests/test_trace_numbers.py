"""Tests of tools/trace_numbers.py (lots 21-trace, 21-rest P) and of experiments/sec3_analytic_values.py (21-rest P)."""
import ast
import csv
import hashlib
import importlib
import io
import math
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from tools import trace_numbers as tn

E2_CSV = "results/e2/e2_cells.csv"
SENTINEL_PAIRS = [("paper/sec3_theory.tex:52", literal)
                  for literal in ("17", "142", "1{,}510", "2{,}787", "1{,}066", "2{,}322")]
SENTINEL_KEY_COLUMNS = ["arm", "mode", "background", "dim", "sr_annual", "gamma"]
ENTRY2_KEY = "arm=G1, mode=cusum_x, background=gauss, dim=1, sr_annual=1.0, gamma=252 |"
ENTRY3_KEY = "arm=G1, mode=onset, background=gauss, dim=1, sr_annual=1.0, gamma=20 |"
HEAD = ("| # | LaTeX location | Literal | Reading | Full key | Column | Source text | Rounded | Status |\n"
        "|---|---|---|---|---|---|---|---|---|\n")
CSV = "arm,mode,gamma,pred_delay,mean_delay\r\nG1,x,20,16.71,16.7\r\nG1,y,20,1509.85,1519.15\r\n"
TEX = "\\section{x}\nwe find 17 and 1{,}510 days, not 1.8\n"
ROW1 = "| 1 | `paper/t.tex:2` | `17` | exact | arm=G1, mode=x, gamma=20 | `pred_delay` | `16.71` | 17 | `READ_MATCH` |"
ROW2 = ("| 2 | `paper/t.tex:2` | `1{,}510` | budget | arm=G1, mode=y, gamma=20 | `pred_delay` | `1509.85` | 1510 | "
        "`READ_MATCH` |")
SEC3_CSV = "results/sec3/sec3_analytic.csv"
SEC3_COLUMNS = ["id", "quantity", "parameters", "reading", "approximation", "anchor", "value"]
ANCHORS = {"mixture_multiplier": "$M=", "absorption_ratio": "\\tau_a/\\tau_\\gamma=",
           "arl0_over_add_diffusion": "expected run to a false alarm"}
READS = {"mixture_multiplier": ("anytime-valid", "fluid"), "absorption_ratio": ("budget", "fluid"),
         "arl0_over_add_diffusion": ("exact", "diffusion")}
SEC3_PARAMETERS = (["gamma=252; sr_annual=1.0"] + [f"D={d}; gamma=504" for d in (1, 10, 64, 500, 128)]
                   + [f"tau_a/tau_gamma={r}" for r in ("2.5", "4", "8")])
SENTINEL_SOURCE = ([("ARL0ADD-G252-SR1", "paper/sec3_theory.tex:52", "1.8", ANCHORS["arl0_over_add_diffusion"])]
                   + [(f"M-D{d}-G504", "paper/sec3_theory.tex:80", literal, ANCHORS["mixture_multiplier"])
                      for d, literal in ((1, "1.22"), (10, "2.01"), (64, "3.91"), (500, "9.64"), (128, "5.2"))]
                   + [(f"ABS-R{r}", "paper/sec3_theory.tex:105", literal, ANCHORS["absorption_ratio"])
                      for r, literal in (("2.5", "2.01"), ("4", "1.39"), ("8", "1.15"))])
SHEAD = ("| ID | Source | LaTeX location | Literal | Anchor | Reading | Approximation | Full key | Column | "
         "Source text | Rounded | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n")
SRC_CSV = ("id,quantity,parameters,reading,approximation,anchor,value\n"
           "M-D1,mixture_multiplier,D=1; gamma=9,anytime-valid,fluid,$M=,1.2239\n"
           "M-D10,mixture_multiplier,D=10; gamma=9,anytime-valid,fluid,$M=,2.0057\n"
           "ABS-R2.5,absorption_ratio,tau_a/tau_gamma=2.5,budget,fluid,\\tau_a/\\tau_\\gamma=,2.0118\n")
SRC_TEX = TEX + "At $M=1.22$, $2.01$ for $D=1$, $10$.\nthat is $2.01$ times for $\\tau_a/\\tau_\\gamma=2.5$.\n"
SROW1 = ("| M-D1 | s | `paper/t.tex:3` | `1.22` | `$M=` | anytime-valid | fluid | "
         "quantity=mixture_multiplier, parameters=D=1; gamma=9 | `value` | `1.2239` | 1.22 | `READ_MATCH` |")
SROW2 = ("| M-D10 | s | `paper/t.tex:3` | `2.01` | `$M=` | anytime-valid | fluid | "
         "quantity=mixture_multiplier, parameters=D=10; gamma=9 | `value` | `2.0057` | 2.01 | `READ_MATCH` |")
SROW3 = ("| ABS-R2.5 | s | `paper/t.tex:4` | `2.01` | `\\tau_a/\\tau_\\gamma=` | budget | fluid | "
         "quantity=absorption_ratio, parameters=tau_a/tau_gamma=2.5 | `value` | `2.0118` | 2.01 | `READ_MATCH` |")
SWAPS = [((7,), "BINDING_MISMATCH"), ((7, 9), "BINDING_MISMATCH"), ((0, 4, 5, 6, 7, 9), "ANCHOR_ABSENT")]
SWAP_IDS = ["keys-exchanged", "keys-and-source-texts-exchanged", "references-exchanged"]


def _repo(root, csv_text=CSV, tex=TEX, rows=(ROW1, ROW2), csv_rel="results/r.csv"):
    files = {"results/r.csv": csv_text.encode("utf-8"), "paper/t.tex": tex.encode("utf-8")}
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)
    sha = {rel: hashlib.sha256(data).hexdigest() for rel, data in files.items()}
    inputs = {"CSV": f"`{csv_rel}`", "CSV SHA-256": f"`{sha['results/r.csv']}`", "Key columns": "`arm, mode, gamma`",
              "LaTeX": "`paper/t.tex`", "LaTeX SHA-256": f"`{sha['paper/t.tex']}`", "Entries": str(len(rows)),
              "Result-bearing occurrences": "5"}
    mapping = ("# Number mapping\n\n## Check inputs\n\nUsage.\n\n| Input | Value |\n|---|---|\n"
               + "".join(f"| {name} | {value} |\n" for name, value in inputs.items())
               + "\n## Entries\n\n" + HEAD + "".join(f"{row}\n" for row in rows) + "\nVerification: prose.\n")
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "MAPPING.md").write_bytes(mapping.encode("utf-8"))
    return root, mapping


def _alter(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _statuses(root, mapping):
    return [result["status"] for result in tn.check(root, mapping)[1]]


def _with_cell(tmp_path, cell, literal):
    row = ROW1.replace("`17`", f"`{literal}`").replace("`16.71`", f"`{cell}`").replace("| 17 |", f"| {literal} |")
    return _statuses(*_repo(tmp_path, csv_text=CSV.replace("16.71,", f"{cell},"),
                            tex=TEX.replace("17 and", f"{literal} and"), rows=(row, ROW2)))


def _real():
    return (tn.ROOT / tn.MAPPING).read_bytes().decode("utf-8")


def _rows_matching(key):
    rows = csv.DictReader(io.StringIO((tn.ROOT / E2_CSV).read_bytes().decode("utf-8"), newline=""))
    pairs = [part.split("=", 1) for part in key.split(", ")]
    return sum(all(row[name] == value for name, value in pairs) for row in rows)


def _repo_sources(root, src_csv=SRC_CSV, tex=SRC_TEX, srows=(SROW1, SROW2, SROW3), src_rel="results/s.csv"):
    root, mapping = _repo(root, tex=tex)
    (root / "results" / "s.csv").write_bytes(src_csv.encode("utf-8"))
    sha = hashlib.sha256(src_csv.encode("utf-8")).hexdigest()
    mapping += ("\n## Sources\n\nUsage.\n\n| Source | CSV | CSV SHA-256 | Key columns | Entries |\n"
                "|---|---|---|---|---|\n"
                f"| s | `{src_rel}` | `{sha}` | `quantity, parameters` | {len(srows)} |\n"
                "\n## Source entries\n\n" + SHEAD + "".join(f"{row}\n" for row in srows))
    (root / "docs" / "MAPPING.md").write_bytes(mapping.encode("utf-8"))
    return root, mapping


def _swap(text, id_a, id_b, cells):
    lines = text.split("\n")
    a, b = (next(i for i, line in enumerate(lines) if line.startswith(f"| {ident} |")) for ident in (id_a, id_b))
    left, right = lines[a].split(" | "), lines[b].split(" | ")
    for cell in cells:
        left[cell], right[cell] = right[cell], left[cell]
    lines[a], lines[b] = " | ".join(left), " | ".join(right)
    return "\n".join(lines)


def _sav():
    return importlib.import_module("experiments.sec3_analytic_values")


def _csv(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True))


def _j1_pred_delay_252():
    key = ("G1", "cusum_x", "gauss", "1", "1.0", "252")
    return next(row["pred_delay"] for row in _csv((tn.ROOT / E2_CSV).read_bytes())
                if tuple(row[name] for name in SENTINEL_KEY_COLUMNS) == key)


def test_fixture_read_match_via_main_bytes_unchanged_stdlib_only(tmp_path, monkeypatch, capsys):
    root, _ = _repo(tmp_path)
    before = (root / "results" / "r.csv").read_bytes()
    monkeypatch.setattr(tn, "ROOT", root)
    assert tn.main([]) == 0
    out = capsys.readouterr().out
    assert out.count("| READ_MATCH\n") == 2 and "paper/t.tex:2 literal '1{,}510' | reading budget | key arm=G1" in out
    assert "2/2 entries READ_MATCH; verified subset 2 of 5 result-bearing occurrences, 3 of 5 not covered" in out
    assert "certifies no ARL0, FPR or ADD" in out and "'exact' names the ARL0-calibrated reading" in out
    assert (root / "results" / "r.csv").read_bytes() == before
    tree = ast.parse(Path(tn.__file__).read_text(encoding="utf-8"))
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert imported and imported <= sys.stdlib_module_names


def test_current_mapping_fifteen_read_match_and_sentinel(capsys):
    before = {rel: (tn.ROOT / rel).read_bytes() for rel in (E2_CSV, SEC3_CSV)}
    assert tn.main([]) == 0
    out = capsys.readouterr().out
    inputs, results = tn.check(tn.ROOT, _real())
    assert [(result["LaTeX location"], result["Literal"]) for result in results if "#" in result] == SENTINEL_PAIRS
    assert [(result["ID"], result["LaTeX location"], result["Literal"], result["Anchor"])
            for result in results if "ID" in result] == SENTINEL_SOURCE
    assert inputs["Key columns"].split(", ") == SENTINEL_KEY_COLUMNS
    assert [(s["Source"], s["CSV"], s["Key columns"], s["Entries"]) for s in inputs["Sources"]] == [
        ("sec3_analytic", SEC3_CSV, "quantity, parameters", "9")]
    assert (inputs["Entries"], inputs["Result-bearing occurrences"]) == ("6", "19")
    assert [result["status"] for result in results] == ["READ_MATCH"] * 15 and out.count("| READ_MATCH\n") == 15
    assert "15/15 entries READ_MATCH; verified subset 15 of 19 result-bearing occurrences, 4 of 19 not covered" in out
    assert {rel: (tn.ROOT / rel).read_bytes() for rel in before} == before


@pytest.mark.parametrize("old, new, index, status", [
    ("| `pred_delay` | `142.0388135314031` |", "| `mean_delay` | `142.0388135314031` |", 1, "MISMATCH"),
    ("| `pred_delay` | `16.71475236584297` |", "| `mean_delay` | `16.71475236584297` |", 0, "SOURCE_TEXT_MISMATCH"),
    ("| `17` |", "| `18` |", 0, "LITERAL_OCCURRENCES_0"),
], ids=["W1-entry2-mean_delay", "W1b-entry1-mean_delay", "W2-literal-18"])
def test_audit_witnesses_rejected_on_current_mapping(old, new, index, status):
    statuses = _statuses(tn.ROOT, _alter(_real(), old, new))
    assert statuses[index] == status and statuses.count("READ_MATCH") == 14


def test_w3_mode_dropped_from_every_key_is_an_incomplete_key():
    text, dropped = re.subn(r"mode=[a-z_]+, ", "", _real())
    assert dropped == 6 and _rows_matching("arm=G1, background=gauss, dim=1, sr_annual=1.0, gamma=20") == 3
    with pytest.raises(ValueError, match="entry 1: key .* must name exactly the Key columns"):
        tn.check(tn.ROOT, text)


@pytest.mark.parametrize("key, dropped", [(ENTRY2_KEY, "background=gauss, "), (ENTRY3_KEY, "dim=1, ")],
                         ids=["background", "dim"])
def test_dropping_a_redundant_key_column_is_refused(key, dropped):
    reduced = key.replace(dropped, "")
    assert _rows_matching(reduced.removesuffix(" |")) == 1
    with pytest.raises(ValueError, match="must name exactly the Key columns"):
        tn.check(tn.ROOT, _alter(_real(), key, reduced))


def test_permuted_complete_key_accepted_on_fixture_and_current_mapping(tmp_path):
    row = ROW1.replace("arm=G1, mode=x, gamma=20", "gamma=20, arm=G1, mode=x")
    assert _statuses(*_repo(tmp_path, rows=(row, ROW2))) == ["READ_MATCH", "READ_MATCH"]
    key = ENTRY2_KEY.removesuffix(" |")
    permuted = ", ".join(reversed(key.split(", ")))
    assert _statuses(tn.ROOT, _alter(_real(), f"{key} |", f"{permuted} |")) == ["READ_MATCH"] * 15


def test_stale_fingerprints_and_incomplete_inventory_refused_on_current_mapping():
    text = _real()
    row6 = next(line for line in text.split("\n") if line.startswith("| 6 | "))
    for old, new, match in (
            ("| LaTeX SHA-256 | `6", "| LaTeX SHA-256 | `7", "stale fingerprint: paper/sec3_theory.tex"),
            ("| CSV SHA-256 | `e", "| CSV SHA-256 | `f", "stale fingerprint: results/e2/e2_cells.csv"),
            (row6 + "\n", "", "has 5 rows, Check inputs declares 6"),
            ("| Entries | 6 |", "| Entries | 7 |", "has 6 rows, Check inputs declares 7")):
        with pytest.raises(ValueError, match=match):
            tn.check(tn.ROOT, _alter(text, old, new))


@pytest.mark.parametrize("change, status", [
    ({"csv_text": CSV.replace("16.71,", "17.71,")}, "MISMATCH"),
    ({"tex": TEX.replace("17 and", "18 and")}, "LITERAL_OCCURRENCES_0"),
    ({"tex": TEX.replace("17 and", "17 and 17 and")}, "LITERAL_OCCURRENCES_2"),
    ({"rows": (ROW1.replace("| 17 |", "| 18 |"), ROW2)}, "MISMATCH"),
    ({"rows": (ROW1.replace("| 17 |", "| 17.0 |"), ROW2)}, "MISMATCH"),
    ({"rows": (ROW1.replace("`16.71`", "`16.710`"), ROW2)}, "SOURCE_TEXT_MISMATCH"),
    ({"rows": (ROW1.replace("`pred_delay`", "`pred_delayx`"), ROW2)}, "UNKNOWN_COLUMN"),
    ({"csv_text": CSV + "G1,x,20,16.9,16.8\r\n"}, "KEY_ROWS_2"),
    ({"rows": (ROW1.replace("gamma=20", "gamma=21"), ROW2)}, "KEY_ROWS_0"),
], ids=["cell", "literal-tex", "literal-twice", "rounded", "rounded-17.0", "source-text", "column-absent",
        "key-ambiguous", "key-absent"])
def test_entry_rejections_on_fixtures(tmp_path, change, status):
    assert _statuses(*_repo(tmp_path, **change)) == [status, "READ_MATCH"]


@pytest.mark.parametrize("cell, literal", [("", "17"), ("", "0"), ("NA", "17"), ("nan", "17"), ("inf", "17"),
                                           ("-Infinity", "17"), ("1e40", "17")])
def test_empty_or_non_finite_cell_refused_never_read_as_zero(tmp_path, cell, literal):
    assert _with_cell(tmp_path, cell, literal) == ["EMPTY_OR_NON_FINITE", "READ_MATCH"]


@pytest.mark.parametrize("cell, literal, status", [("16.5", "16", "READ_MATCH"), ("16.5", "17", "MISMATCH"),
                                                   ("17.5", "18", "READ_MATCH"),
                                                   ("16.500000000000001", "17", "READ_MATCH")])
def test_ties_round_half_even_on_the_cell_text(tmp_path, cell, literal, status):
    assert round(float("16.500000000000001")) == 16
    assert _with_cell(tmp_path, cell, literal) == [status, "READ_MATCH"]


@pytest.mark.parametrize("form", ["-17", "−17", "+17", "1e17", "17e3", "10^{17}", "x^{17}", ".17", "17,000"],
                         ids=["minus", "unicode-minus", "plus", "exponent", "mantissa", "power", "superscript",
                              "leading-dot", "comma-group"])
def test_literal_inside_an_unsupported_numeric_form_does_not_count(tmp_path, form):
    statuses = _statuses(*_repo(tmp_path, tex=TEX.replace("17 and", f"{form} and")))
    assert statuses == ["LITERAL_OCCURRENCES_0", "READ_MATCH"]


@pytest.mark.parametrize("form", ["13--17", "20-17"], ids=["range", "difference"])
def test_literal_after_a_range_or_difference_dash_still_counts(tmp_path, form):
    assert _statuses(*_repo(tmp_path, tex=TEX.replace("17 and", f"{form} and"))) == ["READ_MATCH", "READ_MATCH"]


def test_decimal_literal_refused_although_decimal_equality_holds(tmp_path):
    assert Decimal("17.0") == Decimal("17")
    row = ROW1.replace("`17`", "`17.0`")
    with pytest.raises(ValueError, match=r"entry 1: decimal literal '17\.0' is outside the zero-decimal contract"):
        tn.check(*_repo(tmp_path, tex=TEX.replace("17 and", "17.0 and"), rows=(row, ROW2)))


@pytest.mark.parametrize("rel", ["/etc/hosts", "../outside.csv", "results/../results/r.csv", "./results/r.csv",
                                 "results//r.csv", "data/raw/eurofidai/x.csv", "data/derived/d4_eurofidai/x.csv",
                                 "paper/t.tex", "results/out.csv", "results/data.csv", "results/missing.csv"])
def test_escaping_or_foreign_csv_path_refused_before_any_read(tmp_path, rel):
    root, mapping = _repo(tmp_path / "repo", csv_rel=rel)
    (tmp_path / "outside.csv").write_bytes(CSV.encode("utf-8"))
    (root / "data" / "raw").mkdir(parents=True)
    (root / "data" / "raw" / "x.csv").write_bytes(CSV.encode("utf-8"))
    (root / "results" / "out.csv").symlink_to(tmp_path / "outside.csv")
    (root / "results" / "data.csv").symlink_to(root / "data" / "raw" / "x.csv")
    with pytest.raises(ValueError, match=re.escape(repr(rel))):
        tn.check(root, mapping)


@pytest.mark.parametrize("old, new, match", [
    (ROW1 + "\n" + ROW2 + "\n", "", "has no row: nothing is verified"),
    ("| Entries | 2 |", "| Entries | 3 |", "has 2 rows, Check inputs declares 3"),
    ("| Entries | 2 |", "| Entries | 0 |", "Entries must be a positive integer"),
    ("| Result-bearing occurrences | 5 |", "| Result-bearing occurrences | 1 |", "fewer than Entries"),
    (ROW2, ROW1.replace("| 1 |", "| 2 |", 1), "duplicate"),
    ("| Key columns | `arm, mode, gamma` |\n", "", "exactly the rows"),
    ("| Entries | 2 |\n", "| Entries | 2 |\n| Entries | 2 |\n", "exactly the rows"),
    ("`arm, mode, gamma`", "`arm, , gamma`", "distinct non-empty"),
    ("`arm, mode, gamma`", "`arm, arm, gamma`", "distinct non-empty"),
    ("`arm, mode, gamma`", "`arm, mode, delta`", r"Key columns \['delta'\] absent"),
    ("arm=G1, mode=x, gamma=20 |", "arm=G1, mode=x, gamma=20, dim=1 |", "must name exactly the Key columns"),
    ("arm=G1, mode=x, gamma=20 |", "arm=G1, gamma=20 |", "must name exactly the Key columns"),
    ("arm=G1, mode=x, gamma=20 |", "arm=G1, mode=x, mode=x |", "must name exactly the Key columns"),
    ("arm=G1, mode=x, gamma=20 |", "arm=G1, mode=x, gamma=20, mode=x |", "must name exactly the Key columns"),
    ("mode=x", "mode x", "must name exactly the Key columns"),
    ("mode=x", "mode=", "must name exactly the Key columns"),
    ("| `17` |", "| `seventeen` |", "not a numeral token"),
    ("| exact |", "| approximate |", "reading 'approximate'"),
    ("| 17 | `READ_MATCH` |", "| 17 | `MISMATCH` |", "status 'MISMATCH'"),
    ("| 1 | `paper/t.tex:2` |", "| 1 | `paper/u.tex:2` |", "not a line of paper/t.tex"),
    ("| 1 | `paper/t.tex:2` |", "| 1 | `paper/t.tex:99` |", "not a line of paper/t.tex"),
    ("| 1 | `paper/t.tex:2` |", "| 1 | `paper/t.tex` |", "not a line of paper/t.tex"),
    ("| Source text |", "| Source |", "Entries table header"),
    ("| CSV SHA-256 | `", "| CSV SHA-256 | `zz", "64 lowercase hexadecimal"),
    ("| LaTeX | `paper/t.tex` |", "| LaTeX | `results/r.csv` |", "under paper/"),
    ("## Entries\n", "## Entry\n", "exactly one '## Entries' heading"),
    ("Verification: prose.\n", "Verification: prose.\n\n## Check inputs\n", "exactly one '## Check inputs' heading"),
], ids=["empty", "count-above", "count-zero", "occurrences-below", "duplicate-occurrence", "input-missing",
        "input-twice", "key-column-empty", "key-column-twice", "key-column-not-in-csv", "key-extra-pair",
        "key-missing", "key-repeated", "key-repeated-extra", "key-without-equals", "key-empty-value",
        "literal-not-numeral", "reading", "status", "location-file", "location-line", "location-no-line",
        "entries-header", "sha-format", "latex-prefix", "entries-heading", "inputs-heading-twice"])
def test_structural_refusals_on_fixtures(tmp_path, old, new, match):
    root, mapping = _repo(tmp_path)
    with pytest.raises(ValueError, match=match):
        tn.check(root, _alter(mapping, old, new))


@pytest.mark.parametrize("csv_text, match", [
    (CSV.replace("16.71,16.7", "16.71"), "line 2: field count"),
    (CSV.replace("16.71,16.7", "16.71,16.7,9"), "line 2: field count"),
    (CSV.replace("mean_delay", "pred_delay"), "no header or duplicate column names"),
    ("", "no header or duplicate column names"),
], ids=["short-row", "long-row", "duplicate-header", "empty-csv"])
def test_malformed_csv_refused(tmp_path, csv_text, match):
    with pytest.raises(ValueError, match=match):
        tn.check(*_repo(tmp_path, csv_text=csv_text))


def test_unterminated_quote_refused_outside_the_mapped_column(tmp_path, monkeypatch, capsys):
    csv_text = CSV.split("\r\n")[0] + '\r\nG1,x,20,16.71,"16.7\r\n'
    root, mapping = _repo(tmp_path, csv_text=csv_text, rows=(ROW1,))
    with pytest.raises(ValueError, match=r"results/r\.csv: CSV syntax error \(unexpected end of data\)"):
        tn.check(root, mapping)
    monkeypatch.setattr(tn, "ROOT", root)
    assert tn.main([]) == 1
    assert capsys.readouterr().out == "trace-numbers: error: results/r.csv: CSV syntax error (unexpected end of data)\n"


@pytest.mark.parametrize("rel", ["results/r.csv", "paper/t.tex"])
def test_stale_fingerprint_refused_after_a_file_change(tmp_path, rel):
    root, mapping = _repo(tmp_path)
    (root / rel).write_bytes((root / rel).read_bytes() + b"%")
    with pytest.raises(ValueError, match=f"stale fingerprint: {rel}"):
        tn.check(root, mapping)


def test_main_prints_no_coverage_line_on_failure_or_refusal(tmp_path, monkeypatch, capsys):
    root, mapping = _repo(tmp_path, csv_text=CSV.replace("16.71,", "17.71,"))
    monkeypatch.setattr(tn, "ROOT", root)
    assert tn.main([]) == 1
    out = capsys.readouterr().out
    assert "| MISMATCH\n" in out and "trace-numbers: FAILED: 1 of 2 entries not READ_MATCH" in out
    assert "verified subset" not in out and "certifies" not in out
    (root / "docs" / "MAPPING.md").write_bytes(_alter(mapping, "| Entries | 2 |", "| Entries | 3 |").encode("utf-8"))
    assert tn.main([]) == 1
    assert capsys.readouterr().out == "trace-numbers: error: the Entries table has 2 rows, Check inputs declares 3\n"


def test_sources_read_match_via_main_with_ids_anchors_and_decimals(tmp_path, monkeypatch, capsys):
    root, _ = _repo_sources(tmp_path)
    before = (root / "results" / "s.csv").read_bytes()
    monkeypatch.setattr(tn, "ROOT", root)
    assert tn.main([]) == 0
    out = capsys.readouterr().out
    assert out.count("| READ_MATCH\n") == 5 and "trace-numbers: csv results/s.csv sha256 " in out
    assert "= declared (source s)\n" in out
    assert ("paper/t.tex:4 literal '2.01' | id ABS-R2.5 | source s | reading budget | approximation fluid | "
            "anchor \\tau_a/\\tau_\\gamma= | key quantity=absorption_ratio, parameters=tau_a/tau_gamma=2.5 | "
            "column value | cell '2.0118' | rounded 2.01 | READ_MATCH\n") in out
    assert "5/5 entries READ_MATCH; verified subset 5 of 5 result-bearing occurrences, 0 of 5 not covered" in out
    assert (root / "results" / "s.csv").read_bytes() == before


@pytest.mark.parametrize("cells, status", SWAPS, ids=SWAP_IDS)
def test_two_equal_literals_cannot_exchange_their_sources_on_fixture(tmp_path, cells, status):
    root, mapping = _repo_sources(tmp_path)
    assert {str(Decimal(cell).quantize(Decimal("2.01"))) for cell in ("2.0057", "2.0118")} == {"2.01"}
    swapped = _swap(mapping, "M-D10", "ABS-R2.5", cells)
    assert swapped != mapping and _statuses(root, swapped) == ["READ_MATCH"] * 3 + [status] * 2


@pytest.mark.parametrize("cells, status", SWAPS, ids=SWAP_IDS)
def test_two_equal_literals_cannot_exchange_their_sources_on_current_mapping(cells, status):
    values = {row["id"]: row["value"] for row in _csv((tn.ROOT / SEC3_CSV).read_bytes())}
    assert {str(Decimal(values[ident]).quantize(Decimal("2.01"))) for ident in ("M-D10-G504", "ABS-R2.5")} == {"2.01"}
    results = tn.check(tn.ROOT, _swap(_real(), "M-D10-G504", "ABS-R2.5", cells))[1]
    by_place = {(result["LaTeX location"], result["Literal"]): result["status"] for result in results}
    assert by_place[("paper/sec3_theory.tex:80", "2.01")] == by_place[("paper/sec3_theory.tex:105", "2.01")] == status
    assert [result["status"] for result in results].count("READ_MATCH") == 13


@pytest.mark.parametrize("cell, literal, rounded, status", [
    ("2.015", "2.02", "2.02", "READ_MATCH"), ("2.025", "2.02", "2.02", "READ_MATCH"),
    ("2.025", "2.03", "2.03", "MISMATCH"), ("1.25", "1.2", "1.2", "READ_MATCH"), ("1.35", "1.4", "1.4", "READ_MATCH"),
    ("1.7741", "1.8", "1.8", "READ_MATCH"), ("1.22", "1.22", "1.220", "MISMATCH"), ("13.4", "13", "13", "READ_MATCH"),
    ("NaN", "1.22", "1.22", "EMPTY_OR_NON_FINITE"), ("", "1.22", "1.22", "EMPTY_OR_NON_FINITE"),
    ("inf", "1.22", "1.22", "EMPTY_OR_NON_FINITE"),
], ids=["half-even-up", "half-even-down", "half-even-not-up", "tenth-even", "tenth-odd", "ratio", "rounded-text",
        "integer", "nan", "empty", "inf"])
def test_source_cells_round_half_even_at_the_literal_exponent(tmp_path, cell, literal, rounded, status):
    src = SRC_CSV.replace(",1.2239\n", f",{cell}\n")
    row = SROW1.replace("`1.22`", f"`{literal}`").replace("`1.2239`", f"`{cell}`").replace("| 1.22 |", f"| {rounded} |")
    tex = SRC_TEX.replace("$M=1.22$", f"$M={literal}$")
    assert _statuses(*_repo_sources(tmp_path, src_csv=src, tex=tex, srows=(row, SROW2, SROW3)))[2] == status


@pytest.mark.parametrize("change, status", [
    ({"srows": (SROW1.replace("| M-D1 |", "| M-D2 |"), SROW2, SROW3)}, "BINDING_MISMATCH"),
    ({"src_csv": SRC_CSV.replace(",$M=,1.2239", ",M=,1.2239")}, "BINDING_MISMATCH"),
    ({"srows": (SROW1.replace("| anytime-valid | fluid |", "| budget | fluid |"), SROW2, SROW3)}, "BINDING_MISMATCH"),
    ({"srows": (SROW1.replace("| anytime-valid | fluid |", "| anytime-valid | diffusion |"), SROW2, SROW3)},
     "BINDING_MISMATCH"),
    ({"srows": (SROW1.replace("`$M=`", "`$N=`"), SROW2, SROW3)}, "ANCHOR_ABSENT"),
    ({"srows": (SROW1.replace("`value`", "`valuex`"), SROW2, SROW3)}, "UNKNOWN_COLUMN"),
    ({"src_csv": SRC_CSV + "M-D1,mixture_multiplier,D=1; gamma=9,anytime-valid,fluid,$M=,1.2239\n"}, "KEY_ROWS_2"),
    ({"srows": (SROW1.replace("parameters=D=1; gamma=9", "parameters=D=2; gamma=9"), SROW2, SROW3)}, "KEY_ROWS_0"),
], ids=["row-id", "row-anchor", "reading", "approximation", "anchor-not-on-line", "column-absent", "key-ambiguous",
        "key-absent"])
def test_source_entry_rejections_on_fixtures(tmp_path, change, status):
    assert _statuses(*_repo_sources(tmp_path, **change)) == ["READ_MATCH"] * 2 + [status] + ["READ_MATCH"] * 2


@pytest.mark.parametrize("old, new, match", [
    ("| Source | CSV | CSV SHA-256 | Key columns | Entries |", "| Source | CSV | SHA | Key columns | Entries |",
     "Sources table header"),
    ("| ID | Source |", "| Id | Source |", "Source entries table header"),
    ("\n## Source entries\n", "\n## Source entry\n", "exactly one '## Source entries' heading"),
    ("\n## Sources\n", "\n## Source\n", "exactly one '## Sources' heading"),
    ("| M-D1 | s |", "| M-D1 | t |", "unknown source 't'"),
    ("| M-D10 | s |", "| M-D1 | s |", "ID 'M-D1' must be unique"),
    ("| M-D1 | s |", "| M D1 | s |", "ID 'M D1'"),
    ("| `$M=` | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=1;",
     "|  | anytime-valid | fluid | quantity=mixture_multiplier, parameters=D=1;", "empty anchor"),
    ("| budget | fluid |", "| fixed | fluid |", "reading 'fixed'"),
    ("| budget | fluid |", "| budget | exact |", "approximation 'exact'"),
    ("| 1.22 | `READ_MATCH` |", "| 1.22 | `MISMATCH` |", "status 'MISMATCH'"),
    ("| M-D1 | s | `paper/t.tex:3` |", "| M-D1 | s | `paper/t.tex:9` |", "not a line of paper/t.tex"),
    ("| `1.22` | `$M=`", "| `x1.22` | `$M=`", "not a numeral token"),
    ("quantity=mixture_multiplier, parameters=D=1; gamma=9 |", "quantity=mixture_multiplier |",
     "must name exactly the Key columns"),
    ("| M-D1 | s | `paper/t.tex:3` | `1.22` |", "| M-D1 | s | `paper/t.tex:2` | `17` |", "duplicate"),
    ("| Result-bearing occurrences | 5 |", "| Result-bearing occurrences | 4 |", "fewer than Entries plus Source"),
    ("| `quantity, parameters` | 3 |", "| `quantity, parameters` | 4 |", "Sources declares 4 entries"),
    ("| `quantity, parameters` | 3 |", "| `quantity, parameters` | 0 |", "Entries must be a positive integer"),
    ("`quantity, parameters`", "`quantity, quantity`", "distinct non-empty"),
    ("`quantity, parameters`", "`quantity, kind`", r"Key columns \['kind'\] absent"),
    ("| s | `results/s.csv` | `", "| s | `results/s.csv` | `z", "64 lowercase hexadecimal"),
    ("| s | `results/s.csv` |", "| S! | `results/s.csv` |", "source name 'S!'"),
    (SROW1 + "\n" + SROW2 + "\n" + SROW3 + "\n", "", "at least one row"),
], ids=["sources-header", "entries-header", "entries-heading", "sources-heading", "unknown-source", "duplicate-id",
        "malformed-id", "empty-anchor", "reading", "approximation", "status", "location", "literal", "key",
        "duplicate-occurrence", "occurrences-below", "count-above", "count-zero", "key-column-twice",
        "key-column-not-in-csv", "sha-format", "source-name", "no-source-entry"])
def test_source_structural_refusals_on_fixtures(tmp_path, old, new, match):
    root, mapping = _repo_sources(tmp_path)
    with pytest.raises(ValueError, match=match):
        tn.check(root, _alter(mapping, old, new))


def test_source_declaration_refusals_and_stale_source_fingerprint(tmp_path):
    root, mapping = _repo_sources(tmp_path / "a")
    row = next(line for line in mapping.split("\n") if line.startswith("| s | "))
    with pytest.raises(ValueError, match="source name 's' must be a unique"):
        tn.check(root, _alter(mapping, row, f"{row}\n{row}"))
    with pytest.raises(ValueError, match="CSV is declared twice"):
        tn.check(*_repo_sources(tmp_path / "b", src_rel="results/r.csv"))
    no_binding = SRC_CSV.replace("approximation,", "").replace(",fluid,", ",")
    with pytest.raises(ValueError, match=r"results/s\.csv: binding columns \['approximation'\] absent"):
        tn.check(*_repo_sources(tmp_path / "c", src_csv=no_binding))
    (root / "results" / "s.csv").write_bytes((root / "results" / "s.csv").read_bytes() + b"%")
    with pytest.raises(ValueError, match="stale fingerprint: results/s.csv"):
        tn.check(root, mapping)


@pytest.mark.parametrize("rel", ["/etc/hosts", "../outside.csv", "results/../results/s.csv", "./results/s.csv",
                                 "data/raw/eurofidai/x.csv", "results/out.csv", "results/missing.csv"])
def test_escaping_or_foreign_source_csv_path_refused_before_any_read(tmp_path, rel):
    root, mapping = _repo_sources(tmp_path / "repo", src_rel=rel)
    (tmp_path / "outside.csv").write_bytes(SRC_CSV.encode("utf-8"))
    (root / "results" / "out.csv").symlink_to(tmp_path / "outside.csv")
    with pytest.raises(ValueError, match=re.escape(repr(rel))):
        tn.check(root, mapping)


def test_producer_writes_exclusive_deterministic_bound_rows(tmp_path, capsys):
    sav = _sav()
    paths = (tmp_path / "a.csv", tmp_path / "b.csv")
    for path in paths:
        assert sav.main(["--out", str(path)]) == 0
        assert capsys.readouterr().out == f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path}\n"
    assert paths[0].read_bytes() == paths[1].read_bytes()
    rows = _csv(paths[0].read_bytes())
    assert list(rows[0]) == SEC3_COLUMNS and [row["parameters"] for row in rows] == SEC3_PARAMETERS
    assert [row["id"] for row in rows] == [ident for ident, _, _, _ in SENTINEL_SOURCE]
    assert all(row["anchor"] == ANCHORS[row["quantity"]] for row in rows)
    assert all((row["reading"], row["approximation"]) == READS[row["quantity"]] for row in rows)
    values = {row["id"]: float(row["value"]) for row in rows}
    assert all(math.isfinite(value) and value > 0 for value in values.values())
    for ident, closed in (("ABS-R2.5", 1.25 * math.log(5)), ("ABS-R4", 2 * math.log(2)),
                          ("ABS-R8", 4 * math.log(4 / 3))):
        assert math.isclose(values[ident], closed, rel_tol=1e-12)
    a = math.log(504)
    for d in (1, 10, 64, 500, 128):
        x = values[f"M-D{d}-G504"] * a
        assert math.isclose(x, a + 0.5 * d * math.log1p(2 * x / d), rel_tol=1e-11)
    assert values["ARL0ADD-G252-SR1"] == 252 / float(_j1_pred_delay_252())


def test_producer_refuses_an_existing_out_and_leaves_it_intact(tmp_path, capsys):
    sav = _sav()
    kept, link = tmp_path / "kept.csv", tmp_path / "link.csv"
    kept.write_bytes(b"keep\n")
    link.symlink_to(tmp_path / "target.csv")
    for path in (kept, link):
        assert sav.main(["--out", str(path)]) == 1
        captured = capsys.readouterr()
        assert captured.out == "" and f"{path} exists; refusing to overwrite it" in captured.err
    assert kept.read_bytes() == b"keep\n" and not (tmp_path / "target.csv").exists()


def test_producer_refuses_non_finite_or_infeasible_values_before_any_write(tmp_path, monkeypatch):
    sav = _sav()
    out = tmp_path / "a.csv"
    monkeypatch.setattr(sav, "ABSORPTION_R", (2,))
    with pytest.raises(ValueError, match="ABS-R2: value inf is not finite and positive"):
        sav.main(["--out", str(out)])
    monkeypatch.undo()
    monkeypatch.setattr(sav.fl, "cusum_exact", lambda gamma, theta: {"add": 1.0, "feasible": False})
    with pytest.raises(ValueError, match="infeasible"):
        sav.main(["--out", str(out)])
    assert not out.exists()


def test_producer_imports_floors_and_save_fair_csv_only():
    tree = ast.parse(Path(_sav().__file__).read_text(encoding="utf-8"))
    froms = {(node.module, alias.name) for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
             for alias in node.names}
    plain = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert {pair for pair in froms if pair[0].split(".")[0] not in sys.stdlib_module_names} == {
        ("jepadrift", "floors"), ("jepadrift.pipelines", "save_fair_csv")}
    assert plain <= (sys.stdlib_module_names | {"pandas"}) - {"random", "secrets"}


def test_committed_sec3_csv_equals_a_fresh_run(tmp_path, capsys):
    out = tmp_path / "fresh.csv"
    assert _sav().main(["--out", str(out)]) == 0
    assert out.read_bytes() == (tn.ROOT / SEC3_CSV).read_bytes()
