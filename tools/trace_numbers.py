"""Read check of docs/MAPPING.md (lots 21-trace, 21-rest P): every entry against its LaTeX literal and its CSV cell.

`python tools/trace_numbers.py` reads the Check inputs and Entries tables of docs/MAPPING.md and, when both exist, its
Sources and Source entries tables. Before any read it refuses a CSV path outside results/ and a LaTeX path outside
paper/ (absolute, `..`, non-canonical or escaping through a symlink) and a CSV declared twice. It then refuses stale
SHA-256 fingerprints, CSV syntax errors (strict parsing), keys that do not name each Key column of their source exactly
once (in any order), decimal literals in the Entries table, malformed tables and empty, incomplete or duplicated
inventories. On its LaTeX line a literal counts only as a complete unsigned numeral: digits inside a signed (-, +,
U+2212), exponent (e, ^), leading-dot or comma-grouped number do not count. A Source entry also names an occurrence ID
and the anchor text of its quantity: the anchor must be on the LaTeX line, and the selected row must carry the same id,
anchor, reading and approximation, so two equal literals cannot exchange their sources. Each entry gets one status:
LITERAL_OCCURRENCES_n, ANCHOR_ABSENT, UNKNOWN_COLUMN, KEY_ROWS_n, BINDING_MISMATCH, EMPTY_OR_NON_FINITE, MISMATCH,
SOURCE_TEXT_MISMATCH or READ_MATCH; the cell is rounded half-even at the exponent of the literal. Exit 0 only when
every entry is READ_MATCH; READ_MATCH certifies the literal, cell and rounding agreement of the verified subset only.
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
NAME = re.compile(r"[a-z0-9_]+")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]*")
INPUTS = ("CSV", "CSV SHA-256", "Key columns", "LaTeX", "LaTeX SHA-256", "Entries", "Result-bearing occurrences")
COLUMNS = ["#", "LaTeX location", "Literal", "Reading", "Full key", "Column", "Source text", "Rounded", "Status"]
SOURCES = ["Source", "CSV", "CSV SHA-256", "Key columns", "Entries"]
SOURCE_COLUMNS = ["ID", "Source", "LaTeX location", "Literal", "Anchor", "Reading", "Approximation", "Full key",
                  "Column", "Source text", "Rounded", "Status"]
BOUND = {"id": "ID", "anchor": "Anchor", "reading": "Reading", "approximation": "Approximation"}
READINGS = ("budget", "anytime-valid", "exact")
APPROXIMATIONS = ("fluid", "diffusion")
CAVEAT = ("READ_MATCH means literal, cell and rounding agree; it certifies no ARL0, FPR or ADD, no scientific "
          "conclusion and no reproduction by the producer; 'exact' names the ARL0-calibrated reading, not the "
          "precision of the value; a Source entry keeps the fluid or diffusion approximation it names")


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


def key_columns(where, text):
    """Distinct non-empty names of a comma-separated Key columns cell."""
    names = text.split(", ")
    if not all(names) or len(set(names)) != len(names):
        raise ValueError(f"{where}: Key columns must be distinct non-empty names, got {text!r}")
    return names


def full_key(where, text, names):
    """{column: value} of a Full key that names each Key column exactly once, with a value, in any order."""
    pairs = [part.partition("=") for part in text.split(", ")]
    if sorted(name for name, _, _ in pairs) != sorted(names) or not all(sep and value for _, sep, value in pairs):
        raise ValueError(f"{where}: key {text!r} must name exactly the Key columns {', '.join(names)}, "
                         "each once and with a value, in any order")
    return {name: value for name, _, value in pairs}


def parse_csv(rel, raw, names, bound=()):
    """(header, rows) of a strictly parsed CSV whose header holds its Key columns and the bound columns."""
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
    try:
        header, rows = reader.fieldnames or [], list(reader)
    except csv.Error as exc:
        raise ValueError(f"{rel}: CSV syntax error ({exc})") from exc
    if not header or len(set(header)) != len(header):
        raise ValueError(f"{rel}: no header or duplicate column names")
    if missing := [name for name in names if name not in header]:
        raise ValueError(f"{rel}: Key columns {missing} absent from the header")
    if missing := [name for name in bound if name not in header]:
        raise ValueError(f"{rel}: binding columns {missing} absent from the header")
    for number, row in enumerate(rows, 2):
        if None in row or None in row.values():
            raise ValueError(f"{rel} line {number}: field count differs from the header")
    return header, rows


def source_tables(mapping, primary):
    """(sources, Source entries, Key columns per source): both tables absent, or both present and consistent."""
    if not {"## Sources", "## Source entries"} & set(mapping.split("\n")):
        return [], [], {}
    head, sources = table(mapping, "## Sources")
    if head != SOURCES:
        raise ValueError(f"Sources table header must be | {' | '.join(SOURCES)} |")
    head, entries = table(mapping, "## Source entries")
    if head != SOURCE_COLUMNS:
        raise ValueError(f"Source entries table header must be | {' | '.join(SOURCE_COLUMNS)} |")
    if not sources or not entries:
        raise ValueError("the Sources and Source entries tables need at least one row each")
    names = [source["Source"] for source in sources]
    columns = {}
    for source in sources:
        name = source["Source"]
        if not NAME.fullmatch(name) or names.count(name) != 1:
            raise ValueError(f"source name {name!r} must be a unique lowercase name ({NAME.pattern})")
        if not SHA256.fullmatch(source["CSV SHA-256"]):
            raise ValueError(f"source {name}: CSV SHA-256 must be 64 lowercase hexadecimal digits")
        if not COUNT.fullmatch(source["Entries"]):
            raise ValueError(f"source {name}: Entries must be a positive integer, got {source['Entries']!r}")
        columns[name] = key_columns(f"source {name}", source["Key columns"])
    paths = [primary] + [source["CSV"] for source in sources]
    if len(set(paths)) != len(paths):
        raise ValueError("a CSV is declared twice across Check inputs and Sources")
    ids = [entry["ID"] for entry in entries]
    for entry in entries:
        if not IDENT.fullmatch(entry["ID"]) or ids.count(entry["ID"]) != 1:
            raise ValueError(f"source entry ID {entry['ID']!r} must be unique and match {IDENT.pattern}")
        if entry["Source"] not in names:
            raise ValueError(f"source entry {entry['ID']}: unknown source {entry['Source']!r}")
    for source in sources:
        count = sum(entry["Source"] == source["Source"] for entry in entries)
        if count != int(source["Entries"]):
            raise ValueError(f"source {source['Source']}: Sources declares {source['Entries']} entries, "
                             f"Source entries has {count}")
    return sources, entries, columns


def located(where, entry, latex, lines):
    """LaTeX line of an entry, after checks of its location, numeral literal, reading and declared status."""
    location = LOCATION.fullmatch(entry["LaTeX location"])
    if not location or location[1] != latex or int(location[2]) > len(lines):
        raise ValueError(f"{where}: location {entry['LaTeX location']!r} is not a line of {latex}")
    if not NUM.fullmatch(entry["Literal"]):
        raise ValueError(f"{where}: literal {entry['Literal']!r} is not a numeral token")
    if entry["Reading"] not in READINGS:
        raise ValueError(f"{where}: reading {entry['Reading']!r} is not one of {', '.join(READINGS)}")
    if entry["Status"] != "READ_MATCH":
        raise ValueError(f"{where}: declared status {entry['Status']!r} is not READ_MATCH")
    return lines[int(location[2]) - 1]


def entry_status(entry, line, header, rows, key):
    """(status, cell, rounded) of a validated entry: audit 21 section 3 order, plus the anchor and binding checks."""
    count = FORM.findall(line).count(entry["Literal"])
    if count != 1:
        return f"LITERAL_OCCURRENCES_{count}", "", ""
    bound = "ID" in entry
    if bound and entry["Anchor"] not in line:
        return "ANCHOR_ABSENT", "", ""
    if entry["Column"] not in header:
        return "UNKNOWN_COLUMN", "", ""
    hits = [row for row in rows if all(row[name] == value for name, value in key.items())]
    if len(hits) != 1:
        return f"KEY_ROWS_{len(hits)}", "", ""
    cell = hits[0][entry["Column"]]
    if bound and any(hits[0][column] != entry[name] for column, name in BOUND.items()):
        return "BINDING_MISMATCH", cell, ""
    literal = entry["Literal"].replace("{,}", "")
    try:
        value = Decimal(cell)
        rounded = str(value.quantize(Decimal(literal), rounding=ROUND_HALF_EVEN)) if value.is_finite() else ""
    except InvalidOperation:
        rounded = ""
    if not rounded:
        return "EMPTY_OR_NON_FINITE", cell, ""
    if rounded != literal or rounded != entry["Rounded"]:
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
    names = key_columns("Check inputs", inputs["Key columns"])
    head, entries = table(mapping, "## Entries")
    if head != COLUMNS:
        raise ValueError(f"Entries table header must be | {' | '.join(COLUMNS)} |")
    sources, source_entries, columns = source_tables(mapping, inputs["CSV"])
    if occurrences < declared + len(source_entries):
        raise ValueError("Check inputs: Result-bearing occurrences is fewer than Entries plus Source entries")
    # ponytail: one LaTeX file per MAPPING; add a per-entry LaTeX column when a second paper file is mapped
    files = [(inputs["CSV"], inputs["CSV SHA-256"], "results"), (inputs["LaTeX"], inputs["LaTeX SHA-256"], "paper")]
    files += [(source["CSV"], source["CSV SHA-256"], "results") for source in sources]
    paths = [confined(root, rel, prefix) for rel, _, prefix in files]
    data = {}
    for (rel, declared_sha, _), path in zip(files, paths):
        data[rel] = path.read_bytes()
        actual = hashlib.sha256(data[rel]).hexdigest()
        if actual != declared_sha:
            raise ValueError(f"stale fingerprint: {rel} has SHA-256 {actual}, MAPPING declares {declared_sha}")
    tables = {inputs["CSV"]: parse_csv(inputs["CSV"], data[inputs["CSV"]], names)}
    for source in sources:
        tables[source["CSV"]] = parse_csv(source["CSV"], data[source["CSV"]], columns[source["Source"]], BOUND)
    lines = data[inputs["LaTeX"]].decode("utf-8").split("\n")
    if not entries:
        raise ValueError("the Entries table has no row: nothing is verified")
    if len(entries) != declared:
        raise ValueError(f"the Entries table has {len(entries)} rows, Check inputs declares {declared}")
    pairs = [(entry["LaTeX location"], entry["Literal"]) for entry in entries + source_entries]
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate (location, literal) pair in the Entries or Source entries tables")
    results = []
    for entry in entries:
        where = f"entry {entry['#']}"
        line = located(where, entry, inputs["LaTeX"], lines)
        if "." in entry["Literal"]:
            # ponytail: the Entries table keeps the zero-decimal contract of lot 21-trace; decimals go to Source entries
            raise ValueError(f"{where}: decimal literal {entry['Literal']!r} is outside the zero-decimal contract")
        key = full_key(where, entry["Full key"], names)
        status, cell, rounded = entry_status(entry, line, *tables[inputs["CSV"]], key)
        results.append({**entry, "status": status, "cell": cell, "rounded": rounded})
    by_name = {source["Source"]: source for source in sources}
    for entry in source_entries:
        where = f"source entry {entry['ID']}"
        line = located(where, entry, inputs["LaTeX"], lines)
        if not entry["Anchor"]:
            raise ValueError(f"{where}: empty anchor")
        if entry["Approximation"] not in APPROXIMATIONS:
            raise ValueError(f"{where}: approximation {entry['Approximation']!r} is not one of "
                             f"{', '.join(APPROXIMATIONS)}")
        key = full_key(where, entry["Full key"], columns[entry["Source"]])
        status, cell, rounded = entry_status(entry, line, *tables[by_name[entry["Source"]]["CSV"]], key)
        results.append({**entry, "status": status, "cell": cell, "rounded": rounded})
    inputs["Sources"] = sources
    return inputs, results


def main(argv=None):
    """CLI: one line per input file and entry, then the counts with their denominators; exit 0 only if all match."""
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        inputs, results = check(ROOT, confined(ROOT, MAPPING, "docs").read_bytes().decode("utf-8"))
    except ValueError as exc:
        print(f"trace-numbers: error: {exc}")
        return 1
    print(f"trace-numbers: csv {inputs['CSV']} sha256 {inputs['CSV SHA-256']} = declared")
    for s in inputs["Sources"]:
        print(f"trace-numbers: csv {s['CSV']} sha256 {s['CSV SHA-256']} = declared (source {s['Source']})")
    print(f"trace-numbers: tex {inputs['LaTeX']} sha256 {inputs['LaTeX SHA-256']} = declared")
    for r in results:
        bound = (f" | id {r['ID']} | source {r['Source']} | reading {r['Reading']} | approximation {r['Approximation']}"
                 f" | anchor {r['Anchor']}") if "ID" in r else f" | reading {r['Reading']}"
        print(f"{r['LaTeX location']} literal {r['Literal']!r}{bound} | key {r['Full key']} | column {r['Column']} | "
              f"cell {r['cell']!r} | rounded {r['rounded']} | {r['status']}")
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
