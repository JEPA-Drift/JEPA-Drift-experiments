"""Partial inventory of declared D5 parameters for Appendix B (lot 21-appendix), written to a new Markdown fragment.

`python -m tools.appendix_b [--out logs/<dir>/<name>.md]` reads three fixed inputs only: the leaves of the section d5
of configs/e3.yaml and of the section synthetic of configs/pca_drift_benchmark.yaml, and the numeric D5 table of
docs/sections/injection.md. Six manual links join a configured key to one position of a documented cell; a link is
compared only when the whole cell has its supported form (pair, number or `None` alternatives, number of days), else
it is UNSUPPORTED_DOC_VALUE. UNMAPPED_CONFIG and UNMAPPED_DOC describe these links only. Invalid YAML, equal keys in
any mapping of a file (merges included), cyclic sections, non-finite or non-JSON values, escaping paths and malformed
tables are refused before any write, and an existing fragment is never overwritten. Exit 0 means only that the
inventory was written: no KL, gain, delay or FPR is computed.
"""
import argparse
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path, PurePosixPath

import yaml

from tools.trace_numbers import confined, table

ROOT = Path(__file__).resolve().parents[1]
OUT = "logs/21-appendix/appendix_b.md"
SOURCES = (("configs/e3.yaml", "d5"), ("configs/pca_drift_benchmark.yaml", "synthetic"))
NOTE, HEADING = "docs/sections/injection.md", "## D5 — Monte Carlo backgrounds"
NUM = r"((?:0|[1-9][0-9]*)(?:\.[0-9]+)?)"
ALTERNATIVE = re.compile(NUM + r", or `(None)` \([^()0-9]+\)")
# ponytail: forms of the four known D5 rows only; a newly linked row needs its own form, no general cell parser
FORMS = {"(α, β)": re.compile(rf"\({NUM}, {NUM}\)"), "ν": ALTERNATIVE, "ρ (`factor_rho`)": ALTERNATIVE,
         "burn-in": re.compile(NUM + " days")}
LINKS = {("configs/e3.yaml", "d5.alpha"): ("(α, β)", 1), ("configs/e3.yaml", "d5.beta"): ("(α, β)", 2),
         ("configs/e3.yaml", "d5.burn"): ("burn-in", 1),
         ("configs/pca_drift_benchmark.yaml", "synthetic.rho"): ("ρ (`factor_rho`)", 1),
         ("configs/pca_drift_benchmark.yaml", "synthetic.backgrounds.SYNTH_T7_EQUICORR"): ("ν", 1),
         ("configs/pca_drift_benchmark.yaml", "synthetic.backgrounds.SYNTH_GAUSS_EQUICORR"): ("ν", 2)}
STATUSES = ("MATCH", "DIVERGENT", "UNSUPPORTED_DOC_VALUE", "UNMAPPED_CONFIG", "UNMAPPED_DOC")
NONFINITE = re.compile(r"(?i)\b(?:nan|inf(?:inity)?)\b|∞")
ABSENT = "—"
TITLE = "# Appendix B parameter inventory — partial, declared values"
CAVEAT = (
    "Partial inventory: the numeric D5 table of `docs/sections/injection.md` and the declared leaves of the sections "
    "`d5` of `configs/e3.yaml` and `synthetic` of `configs/pca_drift_benchmark.yaml`, joined by six manual links; "
    "not the full F1–F4 schema nor a complete Appendix B. Parameters in prose or in other tables of the note, values "
    "hard-coded in experiment code and executed configurations are not inventoried; this is not a J4 freeze.",
    "MATCH and DIVERGENT compare a configured value with position [k] of a whole documented cell of a supported form "
    "(a pair (x, y); x, or `None` (text); x days): Decimal equality for numbers, null only against an explicit `None`. "
    "Any other cell form is UNSUPPORTED_DOC_VALUE. UNMAPPED_CONFIG and UNMAPPED_DOC describe the six selected links "
    "only, never an absence from the whole note or code. No KL, gain, delay or FPR value is computed; writing this "
    "file certifies no scientific result.",
)


class _Loader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep)
        if len(mapping) < len(node.value):
            keys = [self.construct_object(key) for key, _ in node.value]
            repeated = next(key for index, key in enumerate(keys) if key in keys[:index])
            raise yaml.YAMLError(f"duplicate key {repeated!r} in the mapping at line {node.start_mark.line + 1}")
        return mapping


def leaves(rel, prefix, mapping):
    """(key, value, JSON text) of every leaf under prefix, in document order; bad names, empty maps, NaN/inf refused."""
    found = []
    for key, value in mapping.items():
        if not isinstance(key, str) or not key or set(key) & set(".|`\r\n"):
            raise ValueError(f"{rel}: key {key!r} under {prefix} is not a plain name")
        name = f"{prefix}.{key}"
        if isinstance(value, dict):
            if not value:
                raise ValueError(f"{rel}: {name} is an empty mapping")
            found += leaves(rel, name, value)
            continue
        try:
            text = json.dumps(value, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{rel}: {name} has a non-finite or non-JSON value {value!r}") from exc
        if "|" in text:
            raise ValueError(f"{rel}: {name} has '|' in value {text}")
        found.append((name, value, text))
    return found


def section(root, rel, name):
    """(SHA-256, leaves) of one acyclic selected YAML section; paths named in the file are never opened."""
    raw = confined(root, rel, "configs").read_bytes()
    try:
        doc = yaml.load(raw, Loader=_Loader)
    except yaml.YAMLError as exc:
        raise ValueError(f"{rel}: invalid YAML ({exc})") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get(name), dict) or not doc[name]:
        raise ValueError(f"{rel}: no non-empty mapping section {name!r}")
    try:
        json.dumps(doc[name], skipkeys=True, default=repr)
    except ValueError as exc:
        raise ValueError(f"{rel}: section {name!r}: {exc}") from exc
    return hashlib.sha256(raw).hexdigest(), leaves(rel, name, doc[name])


def documented(root):
    """(SHA-256, {label: cell}) of the D5 parameter table of the injection note, cells kept verbatim."""
    raw = confined(root, NOTE, "docs").read_bytes()
    try:
        header, rows = table(raw.decode("utf-8"), HEADING)
    except ValueError as exc:
        raise ValueError(f"{NOTE}: {exc}") from exc
    if header != ["parameter", "values"]:
        raise ValueError(f"{NOTE}: the D5 table header must be | parameter | values |")
    labels = [row["parameter"] for row in rows]
    if not labels:
        raise ValueError(f"{NOTE}: the D5 table has no documented row")
    if not all(labels) or len(set(labels)) != len(labels):
        raise ValueError(f"{NOTE}: empty or duplicate parameter label in the D5 table")
    if bad := [row["values"] for row in rows if NONFINITE.search(row["values"])]:
        raise ValueError(f"{NOTE}: non-finite documented value {bad[0]!r}")
    return hashlib.sha256(raw).hexdigest(), {row["parameter"]: row["values"] for row in rows}


def status(value, label, position, cell):
    """Status of a present linked key: whole-cell form first, then Decimal equality or explicit None at its position."""
    if cell is None:
        return "UNMAPPED_CONFIG"
    match = FORMS[label].fullmatch(cell)
    if not match:
        return "UNSUPPORTED_DOC_VALUE"
    token = match[position]
    if token == "None":
        return "MATCH" if value is None else "DIVERGENT"
    number = isinstance(value, (int, float)) and not isinstance(value, bool)
    return "MATCH" if number and Decimal(repr(value)) == Decimal(token) else "DIVERGENT"


def inventory(root):
    """(inputs, rows): per source its leaves, then its absent linked keys, then the documented rows it does not link."""
    note_sha, cells = documented(root)
    inputs, rows = [], []
    for rel, name in SOURCES:
        sha, found = section(root, rel, name)
        inputs.append((rel, name, sha))
        links = {key: link for (source, key), link in LINKS.items() if source == rel}
        for key, value, text in found:
            if key not in links:
                rows.append((rel, key, text, ABSENT, ABSENT, "UNMAPPED_CONFIG"))
                continue
            label, position = links[key]
            cell = cells.get(label)
            rows.append((rel, key, text, f"{label} [{position}]", ABSENT if cell is None else cell,
                         status(value, label, position, cell)))
        present = {key for key, _, _ in found}
        rows += [(rel, key, ABSENT, f"{label} [{position}]", cells.get(label, ABSENT), "UNMAPPED_DOC")
                 for key, (label, position) in links.items() if key not in present]
        linked = {label for label, _ in links.values()}
        rows += [(rel, ABSENT, ABSENT, label, cell, "UNMAPPED_DOC") for label, cell in cells.items()
                 if label not in linked]
    return inputs + [(NOTE, HEADING, note_sha)], rows


def counts(rows):
    """Row total and per-status counts in the fixed status order."""
    return f"{len(rows)} rows: " + ", ".join(f"{name} {sum(row[5] == name for row in rows)}" for name in STATUSES)


def render(inputs, rows):
    """Deterministic Markdown fragment: title, caveat, inputs with SHA-256, one line per row, counts."""
    lines = [TITLE, ""]
    for paragraph in CAVEAT:
        lines += [paragraph, ""]
    lines += ["| Input | Section | SHA-256 |", "|---|---|---|"]
    lines += [f"| `{rel}` | `{name}` | `{sha}` |" for rel, name, sha in inputs]
    lines += ["", "| Source | Key | Configured | Row | Documented | Status |", "|---|---|---|---|---|---|"]
    lines += [f"| `{source}` | {key if key == ABSENT else f'`{key}`'} | {text} | {row} | {cell} | {state} |"
              for source, key, text, row, cell, state in rows]
    return "\n".join(lines + ["", f"Counts: {counts(rows)}.", ""])


def target(root, rel):
    """Path of a new fragment: canonical relative POSIX .md path whose parent resolves to a directory in logs/."""
    path = PurePosixPath(rel)
    if (path.is_absolute() or ".." in path.parts or str(path) != rel or path.parts[:1] != ("logs",)
            or path.suffix != ".md"):
        raise ValueError(f"--out {rel!r} is not a canonical relative .md path under logs/")
    base = Path(root).resolve()
    try:
        parent = (base / path).parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"--out {rel!r}: parent directory does not resolve ({type(exc).__name__})") from exc
    if not parent.is_relative_to(base / "logs") or not parent.is_dir():
        raise ValueError(f"--out {rel!r}: parent resolves outside logs/ or is not a directory")
    return parent / path.name


def main(argv=None):
    """Write the inventory to a new --out file under logs/; print its SHA-256 and counts, or the refusal (exit 1)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=OUT, help=f"new Markdown file under logs/, never overwritten (default: {OUT})")
    args = parser.parse_args(argv)
    try:
        out = target(ROOT, args.out)
        inputs, rows = inventory(ROOT)
        data = render(inputs, rows).encode("utf-8")
        with open(out, "xb") as handle:
            handle.write(data)
    except FileExistsError:
        print(f"appendix-b: error: --out {args.out!r} exists; refusing to overwrite")
        return 1
    except (OSError, ValueError) as exc:
        print(f"appendix-b: error: {exc}")
        return 1
    print(f"appendix-b: wrote {args.out} sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"appendix-b: {counts(rows)}")
    print("appendix-b: partial inventory of declared values; exit 0 means only that it was written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
