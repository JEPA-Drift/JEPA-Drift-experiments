"""Read check of docs/MAPPING.md (lot 21-trace): every Entries row against its LaTeX literal and its sealed CSV cell.

`python tools/trace_numbers.py` reads the Check inputs and Entries tables of docs/MAPPING.md. Before any read it
refuses a CSV path outside results/ and a LaTeX path outside paper/ (absolute, `..`, non-canonical or escaping through
a symlink). It then refuses stale SHA-256 fingerprints, CSV syntax errors (strict parsing), keys that do not name
each Key column exactly once (in any order), decimal literals, malformed CSV tables and empty, incomplete or
duplicated inventories. On its LaTeX line a literal counts only as a complete unsigned numeral: digits inside a
signed (-, +, U+2212), exponent (e, ^), leading-dot or comma-grouped number do not count. Each entry gets one status,
in the order of the audit 21 section 3 check: LITERAL_OCCURRENCES_n, UNKNOWN_COLUMN, KEY_ROWS_n, EMPTY_OR_NON_FINITE,
MISMATCH, SOURCE_TEXT_MISMATCH or READ_MATCH. Exit 0 only when every entry is READ_MATCH; READ_MATCH certifies the
literal, cell and rounding agreement of the verified subset only.
"""
import argparse
import csv
import hashlib
import io
import re
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MAPPING = "docs/MAPPING.md"
NUM = re.compile(r"[0-9]+(?:\{,\}[0-9]{3})*(?:\.[0-9]+)?")
# ponytail: contiguous numeric forms only; `2\times10^{3}` still exposes its mantissa, tokenize macros if one is mapped
FORM = re.compile(r"(?:\^\{?|\.)?(?:(?<![0-9\-−])[-+−])?[0-9]+(?:(?:\{,\}|,)[0-9]{3})*(?:\.[0-9]+)?"
                  r"(?:[eE][-+−]?[0-9]+|\^\{?[-+−]?[0-9]+)?")
LOCATION = re.compile(r"(.+):([1-9][0-9]*)")
SHA256 = re.compile(r"[0-9a-f]{64}")
COUNT = re.compile(r"[1-9][0-9]*")
INPUTS = ("CSV", "CSV SHA-256", "Key columns", "LaTeX", "LaTeX SHA-256", "Entries", "Result-bearing occurrences")
COLUMNS = ["#", "LaTeX location", "Literal", "Reading", "Full key", "Column", "Source text", "Rounded", "Status"]
READINGS = ("budget", "anytime-valid", "exact")
CAVEAT = ("READ_MATCH means literal, cell and rounding agree; it certifies no ARL0, FPR or ADD, no scientific "
          "conclusion and no reproduction by the producer; 'exact' names the ARL0-calibrated reading, not the "
          "precision of the value")


def table(text, heading):
    """(header, rows) of the first pipe table under a unique heading; one enclosing backtick pair is removed."""
    lines = text.split("\n")
    if lines.count(heading) != 1:
        raise ValueError(f"MAPPING needs exactly one {heading!r} heading")
    i = lines.index(heading) + 1
    while i < len(lines) and not lines[i].startswith(("|", "#")):
        i += 1
    block = []
    while i < len(lines) and lines[i].startswith("|"):
        block.append([cell.strip() for cell in lines[i].strip().strip("|").split("|")])
        i += 1
    if len(block) < 2 or not all(cell and set(cell) <= set(":-") for cell in block[1]):
        raise ValueError(f"no pipe table under {heading!r}")
    if any(len(row) != len(block[0]) for row in block[1:]):
        raise ValueError(f"ragged table row under {heading!r}")
    rows = [[cell[1:-1] if len(cell) > 1 and cell[0] == cell[-1] == "`" else cell for cell in row] for row in block[2:]]
    return block[0], [dict(zip(block[0], row)) for row in rows]


def confined(root, rel, prefix):
    """Regular file of a canonical relative POSIX path that resolves under root/prefix; refused before any read."""
    path = PurePosixPath(rel)
    if path.is_absolute() or ".." in path.parts or str(path) != rel or path.parts[:1] != (prefix,):
        raise ValueError(f"{rel!r} is not a canonical relative path under {prefix}/")
    base = Path(root).resolve()
    try:
        full = (base / path).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"{rel!r} does not resolve ({type(exc).__name__})") from exc
    if not full.is_relative_to(base / prefix) or not full.is_file():
        raise ValueError(f"{rel!r} resolves outside {prefix}/ or is not a regular file")
    return full


def entry_status(entry, line, header, rows, key):
    """(status, cell, rounded) of a validated entry, in the order of the audit 21 section 3 check plus two statuses."""
    count = FORM.findall(line).count(entry["Literal"])
    if count != 1:
        return f"LITERAL_OCCURRENCES_{count}", "", ""
    if entry["Column"] not in header:
        return "UNKNOWN_COLUMN", "", ""
    hits = [row for row in rows if all(row[name] == value for name, value in key.items())]
    if len(hits) != 1:
        return f"KEY_ROWS_{len(hits)}", "", ""
    cell = hits[0][entry["Column"]]
    try:
        value = Decimal(cell)
        rounded = str(value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)) if value.is_finite() else ""
    except InvalidOperation:
        rounded = ""
    if not rounded:
        return "EMPTY_OR_NON_FINITE", cell, ""
    if rounded != entry["Literal"].replace("{,}", "") or rounded != entry["Rounded"]:
        return "MISMATCH", cell, rounded
    if cell != entry["Source text"]:
        return "SOURCE_TEXT_MISMATCH", cell, rounded
    return "READ_MATCH", cell, rounded


def check(root, mapping):
    """(inputs, results) of the read check; a structural refusal raises ValueError and no file is read unchecked."""
    head, rows = table(mapping, "## Check inputs")
    if head != ["Input", "Value"] or sorted(row["Input"] for row in rows) != sorted(INPUTS):
        raise ValueError(f"Check inputs must hold exactly the rows {', '.join(INPUTS)}, once each")
    inputs = {row["Input"]: row["Value"] for row in rows}
    for name in ("CSV SHA-256", "LaTeX SHA-256"):
        if not SHA256.fullmatch(inputs[name]):
            raise ValueError(f"Check inputs: {name} must be 64 lowercase hexadecimal digits")
    for name in ("Entries", "Result-bearing occurrences"):
        if not COUNT.fullmatch(inputs[name]):
            raise ValueError(f"Check inputs: {name} must be a positive integer, got {inputs[name]!r}")
    declared, occurrences = int(inputs["Entries"]), int(inputs["Result-bearing occurrences"])
    if occurrences < declared:
        raise ValueError("Check inputs: Result-bearing occurrences is fewer than Entries")
    key_columns = inputs["Key columns"].split(", ")
    if not all(key_columns) or len(set(key_columns)) != len(key_columns):
        raise ValueError(f"Check inputs: Key columns must be distinct non-empty names, got {inputs['Key columns']!r}")
    head, entries = table(mapping, "## Entries")
    if head != COLUMNS:
        raise ValueError(f"Entries table header must be | {' | '.join(COLUMNS)} |")
    # ponytail: one CSV and one LaTeX file per MAPPING; add a per-entry source column when a second file is mapped
    paths = {"CSV": confined(root, inputs["CSV"], "results"), "LaTeX": confined(root, inputs["LaTeX"], "paper")}
    data = {name: path.read_bytes() for name, path in paths.items()}
    for name, raw in data.items():
        actual = hashlib.sha256(raw).hexdigest()
        if actual != inputs[f"{name} SHA-256"]:
            raise ValueError(f"stale fingerprint: {inputs[name]} has SHA-256 {actual}, "
                             f"MAPPING declares {inputs[f'{name} SHA-256']}")
    reader = csv.DictReader(io.StringIO(data["CSV"].decode("utf-8"), newline=""), strict=True)
    try:
        header, csv_rows = reader.fieldnames or [], list(reader)
    except csv.Error as exc:
        raise ValueError(f"{inputs['CSV']}: CSV syntax error ({exc})") from exc
    if not header or len(set(header)) != len(header):
        raise ValueError(f"{inputs['CSV']}: no header or duplicate column names")
    if missing := [name for name in key_columns if name not in header]:
        raise ValueError(f"{inputs['CSV']}: Key columns {missing} absent from the header")
    for number, row in enumerate(csv_rows, 2):
        if None in row or None in row.values():
            raise ValueError(f"{inputs['CSV']} line {number}: field count differs from the header")
    lines = data["LaTeX"].decode("utf-8").split("\n")
    if not entries:
        raise ValueError("the Entries table has no row: nothing is verified")
    if len(entries) != declared:
        raise ValueError(f"the Entries table has {len(entries)} rows, Check inputs declares {declared}")
    if len({(entry["LaTeX location"], entry["Literal"]) for entry in entries}) != len(entries):
        raise ValueError("duplicate (location, literal) pair in the Entries table")
    results = []
    for entry in entries:
        where, literal = f"entry {entry['#']}", entry["Literal"]
        location = LOCATION.fullmatch(entry["LaTeX location"])
        if not location or location[1] != inputs["LaTeX"] or int(location[2]) > len(lines):
            raise ValueError(f"{where}: location {entry['LaTeX location']!r} is not a line of {inputs['LaTeX']}")
        if not NUM.fullmatch(literal):
            raise ValueError(f"{where}: literal {literal!r} is not a numeral token")
        if "." in literal:
            # ponytail: integer literals at 0 decimals only; quantize to the literal's exponent when a decimal is mapped
            raise ValueError(f"{where}: decimal literal {literal!r} is outside the zero-decimal contract")
        if entry["Reading"] not in READINGS:
            raise ValueError(f"{where}: reading {entry['Reading']!r} is not one of {', '.join(READINGS)}")
        if entry["Status"] != "READ_MATCH":
            raise ValueError(f"{where}: declared status {entry['Status']!r} is not READ_MATCH")
        pairs = [part.partition("=") for part in entry["Full key"].split(", ")]
        names = sorted(name for name, _, _ in pairs)
        if names != sorted(key_columns) or not all(sep and value for _, sep, value in pairs):
            raise ValueError(f"{where}: key {entry['Full key']!r} must name exactly the Key columns "
                             f"{', '.join(key_columns)}, each once and with a value, in any order")
        key = {name: value for name, _, value in pairs}
        status, cell, rounded = entry_status(entry, lines[int(location[2]) - 1], header, csv_rows, key)
        results.append({**entry, "status": status, "cell": cell, "rounded": rounded})
    return inputs, results


def main(argv=None):
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        inputs, results = check(ROOT, confined(ROOT, MAPPING, "docs").read_bytes().decode("utf-8"))
    except ValueError as exc:
        print(f"trace-numbers: error: {exc}")
        return 1
    print(f"trace-numbers: csv {inputs['CSV']} sha256 {inputs['CSV SHA-256']} = declared")
    print(f"trace-numbers: tex {inputs['LaTeX']} sha256 {inputs['LaTeX SHA-256']} = declared")
    for r in results:
        print(f"{r['LaTeX location']} literal {r['Literal']!r} | reading {r['Reading']} | key {r['Full key']} | "
              f"column {r['Column']} | cell {r['cell']!r} | rounded {r['rounded']} | {r['status']}")
    failed, n = sum(r["status"] != "READ_MATCH" for r in results), len(results)
    if failed:
        print(f"trace-numbers: FAILED: {failed} of {n} entries not READ_MATCH")
        return 1
    total = int(inputs["Result-bearing occurrences"])
    print(f"trace-numbers: {n}/{n} entries READ_MATCH; verified subset {n} of {total} result-bearing occurrences, "
          f"{total - n} of {total} not covered ({MAPPING}, Coverage)")
    print(f"trace-numbers: {CAVEAT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
