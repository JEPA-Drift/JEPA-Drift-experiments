"""Tests of tools/trace_numbers.py (lot 21-trace): fixtures, current MAPPING and sentinel, rejection witnesses."""
import ast
import csv
import hashlib
import io
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


def test_current_mapping_six_read_match_and_sentinel(capsys):
    before = (tn.ROOT / E2_CSV).read_bytes()
    assert tn.main([]) == 0
    out = capsys.readouterr().out
    inputs, results = tn.check(tn.ROOT, _real())
    assert [(result["LaTeX location"], result["Literal"]) for result in results] == SENTINEL_PAIRS
    assert inputs["Key columns"].split(", ") == SENTINEL_KEY_COLUMNS
    assert (inputs["Entries"], inputs["Result-bearing occurrences"]) == ("6", "19")
    assert [result["status"] for result in results] == ["READ_MATCH"] * 6 and out.count("| READ_MATCH\n") == 6
    assert "6/6 entries READ_MATCH; verified subset 6 of 19 result-bearing occurrences, 13 of 19 not covered" in out
    assert (tn.ROOT / E2_CSV).read_bytes() == before


@pytest.mark.parametrize("old, new, index, status", [
    ("| `pred_delay` | `142.0388135314031` |", "| `mean_delay` | `142.0388135314031` |", 1, "MISMATCH"),
    ("| `pred_delay` | `16.71475236584297` |", "| `mean_delay` | `16.71475236584297` |", 0, "SOURCE_TEXT_MISMATCH"),
    ("| `17` |", "| `18` |", 0, "LITERAL_OCCURRENCES_0"),
], ids=["W1-entry2-mean_delay", "W1b-entry1-mean_delay", "W2-literal-18"])
def test_audit_witnesses_rejected_on_current_mapping(old, new, index, status):
    statuses = _statuses(tn.ROOT, _alter(_real(), old, new))
    assert statuses[index] == status and statuses.count("READ_MATCH") == 5


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
    assert _statuses(tn.ROOT, _alter(_real(), f"{key} |", f"{permuted} |")) == ["READ_MATCH"] * 6


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
