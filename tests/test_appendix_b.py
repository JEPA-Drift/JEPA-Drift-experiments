"""Tests of tools/appendix_b.py (lot 21-appendix): sentinel, link statuses, refusals, confinement and determinism."""
import ast
import hashlib
import sys
from pathlib import Path

import pytest

from tools import appendix_b as ab

E3, PCA, NOTE = "configs/e3.yaml", "configs/pca_drift_benchmark.yaml", "docs/sections/injection.md"
HEADING = "## D5 — Monte Carlo backgrounds"
SHA = {E3: "6e3857382200f0b7333419a1be33ea1623fe59b99e3e236abf6d97c615948b0b",
       PCA: "79d2b5e5570743840b181689c3076b399a89b314d01fc3c5d1a043f25d473e99",
       NOTE: "8708a1df9d55975a7774777a2f56accd6e89ddd296becd2f1cd5a9a199a884b7"}
PAIR, NU, RHO, BURN = "(0.08, 0.90)", "7, or `None` (Gaussian)", "0.40, or `None` (no factor)", "1000 days"
T7, GAUSS = "synthetic.backgrounds.SYNTH_T7_EQUICORR", "synthetic.backgrounds.SYNTH_GAUSS_EQUICORR"
BASELINE = [
    (E3, "d5.alpha", "0.08", "(α, β) [1]", PAIR, "MATCH"),
    (E3, "d5.beta", "0.9", "(α, β) [2]", PAIR, "MATCH"),
    (E3, "d5.burn", "1000", "burn-in [1]", BURN, "MATCH"),
    (E3, "d5.T_clean", "941", "—", "—", "UNMAPPED_CONFIG"),
    (E3, "d5.backgrounds", '["t7", "gaussian"]', "—", "—", "UNMAPPED_CONFIG"),
    (E3, "—", "—", "ν", NU, "UNMAPPED_DOC"),
    (E3, "—", "—", "ρ (`factor_rho`)", RHO, "UNMAPPED_DOC"),
    (PCA, "synthetic.rho", "0.4", "ρ (`factor_rho`) [1]", RHO, "MATCH"),
    (PCA, GAUSS, "null", "ν [2]", NU, "MATCH"),
    (PCA, T7, "7", "ν [1]", NU, "MATCH"),
    (PCA, "synthetic.sr_annual_A", "4.0", "—", "—", "UNMAPPED_CONFIG"),
    (PCA, "synthetic.rotation_deg", "30.0", "—", "—", "UNMAPPED_CONFIG"),
    (PCA, "synthetic.rotation_pair", "[1, 2]", "—", "—", "UNMAPPED_CONFIG"),
    (PCA, "synthetic.C_axes", "[10, 20]", "—", "—", "UNMAPPED_CONFIG"),
    (PCA, "synthetic.C_I_target", "3.0", "—", "—", "UNMAPPED_CONFIG"),
    (PCA, "—", "—", "(α, β)", PAIR, "UNMAPPED_DOC"),
    (PCA, "—", "—", "burn-in", BURN, "UNMAPPED_DOC"),
]
LINKED = [(E3, "d5.alpha", "(α, β) [1]"), (E3, "d5.beta", "(α, β) [2]"), (E3, "d5.burn", "burn-in [1]"),
          (PCA, "synthetic.rho", "ρ (`factor_rho`) [1]"), (PCA, T7, "ν [1]"), (PCA, GAUSS, "ν [2]")]
STATUSES = {"MATCH", "DIVERGENT", "UNSUPPORTED_DOC_VALUE", "UNMAPPED_CONFIG", "UNMAPPED_DOC"}
COUNTS = "17 rows: MATCH 6, DIVERGENT 0, UNSUPPORTED_DOC_VALUE 0, UNMAPPED_CONFIG 7, UNMAPPED_DOC 4"
D5_BLOCK = "d5:\n  alpha: 0.08\n  beta: 0.90\n  burn: 1000\n  T_clean: 941\n  backgrounds: [t7, gaussian]\n"
E3_TEXT = "alpha: 0.05\n" + D5_BLOCK + "arl0:\n  gamma: [20, 252]\n"
PCA_TEXT = ("seed: 42\nsynthetic:\n  rho: 0.4\n  backgrounds:\n"
            "    SYNTH_GAUSS_EQUICORR: null\n    SYNTH_T7_EQUICORR: 7\n"
            "  sr_annual_A: 4.0\n  rotation_deg: 30.0\n  rotation_pair: [1, 2]\n  C_axes: [10, 20]\n  C_I_target: 3.0\n"
            "real:\n  panel: data/raw/absent/panel.parquet\n")
BACKGROUNDS = "  backgrounds:\n    SYNTH_GAUSS_EQUICORR: null\n    SYNTH_T7_EQUICORR: 7\n"
ANCHORED = BACKGROUNDS.replace("backgrounds:", "backgrounds: &b")
ROWS =f"| (α, β) | {PAIR} |\n| ν | {NU} |\n| ρ (`factor_rho`) | {RHO} |\n| burn-in | {BURN} |\n"
NOTE_TEXT = (f"# Injections\n\n{HEADING}\n\n**GARCH panel.** Prose with 0.08 and 1000.\n\n"
             "| parameter | values |\n|---|---|\n" + ROWS
             + "\n## Amplitude conventions (F1–F3)\n\n| SR | I_target (nats/day) |\n|---|---|\n| 1 | 1.984127e-03 |\n")
OUT = Path("logs") / "21-appendix" / "appendix_b.md"


def _repo(root, changes=()):
    texts = {E3: E3_TEXT, PCA: PCA_TEXT, NOTE: NOTE_TEXT}
    for rel, old, new in changes:
        assert texts[rel].count(old) == 1, old
        texts[rel] = texts[rel].replace(old, new)
    for rel, text in texts.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode("utf-8"))
    (root / OUT).parent.mkdir(parents=True)
    return root


def _line(source, key, configured, row, documented, status):
    shown = key if key == "—" else f"`{key}`"
    return f"| `{source}` | {shown} | {configured} | {row} | {documented} | {status} |"


def _outside(rel, value):
    last = {E3: "arl0:\n", PCA: "real:\n"}[rel]
    return rel, last, f"outside: {value}\n{last}"


def test_current_inputs_sentinel_seventeen_rows():
    inputs, rows = ab.inventory(ab.ROOT)
    assert inputs == [(E3, "d5", SHA[E3]), (PCA, "synthetic", SHA[PCA]), (NOTE, HEADING, SHA[NOTE])]
    assert rows == BASELINE


def test_fixture_reads_only_the_selected_sections_and_table(tmp_path):
    inputs, rows = ab.inventory(_repo(tmp_path))
    assert rows == BASELINE
    assert [(rel, sha) for rel, _, sha in inputs] == [
        (rel, hashlib.sha256((tmp_path / rel).read_bytes()).hexdigest()) for rel in (E3, PCA, NOTE)]


def test_main_writes_one_new_deterministic_partial_fragment(tmp_path, monkeypatch, capsys):
    root = _repo(tmp_path / "repo")
    before = {rel: (root / rel).read_bytes() for rel in (E3, PCA, NOTE)}
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main([]) == 0
    first = (root / OUT).read_bytes()
    out = capsys.readouterr().out
    assert f"appendix-b: wrote logs/21-appendix/appendix_b.md sha256 {hashlib.sha256(first).hexdigest()}\n" in out
    assert f"appendix-b: {COUNTS}\n" in out
    assert ab.main([]) == 1
    assert "appendix-b: error: --out 'logs/21-appendix/appendix_b.md' exists; refusing to overwrite" in (
        capsys.readouterr().out)
    assert (root / OUT).read_bytes() == first
    assert ab.main(["--out", "logs/second.md"]) == 0
    assert (root / "logs" / "second.md").read_bytes() == first
    assert {rel: (root / rel).read_bytes() for rel in before} == before
    text = first.decode("utf-8")
    lines = text.split("\n")
    assert lines[0].startswith("# ") and "partial" in lines[0] and text.endswith("\n") and str(tmp_path) not in text
    assert any("Partial inventory" in line and "not the full F1–F4 schema" in line for line in lines)
    for rel, section in ((E3, "d5"), (PCA, "synthetic"), (NOTE, HEADING)):
        assert f"| `{rel}` | `{section}` | `{hashlib.sha256(before[rel]).hexdigest()}` |" in lines
    start = lines.index("| Source | Key | Configured | Row | Documented | Status |") + 2
    assert lines[start:start + 18] == [_line(*row) for row in BASELINE] + [""]
    assert f"Counts: {COUNTS}." in lines


def test_tool_imports_only_stdlib_yaml_and_the_trace_helpers():
    tree = ast.parse(Path(ab.__file__).read_text(encoding="utf-8"))
    modules = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    modules |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert {name for name in modules if name.split(".")[0] not in sys.stdlib_module_names} == {
        "yaml", "tools.trace_numbers"}


DAYS_ROW = "| burn-in | 1000 days |"
CASES = {
    "value-difference": ([(E3, "  beta: 0.90\n", "  beta: 0.85\n")],
                         [(E3, "d5.alpha", "0.08", "(α, β) [1]", PAIR, "MATCH"),
                          (E3, "d5.beta", "0.85", "(α, β) [2]", PAIR, "DIVERGENT")]),
    "alpha-beta-permutation": ([(E3, "  alpha: 0.08\n  beta: 0.90\n", "  alpha: 0.90\n  beta: 0.08\n")],
                               [(E3, "d5.alpha", "0.9", "(α, β) [1]", PAIR, "DIVERGENT"),
                                (E3, "d5.beta", "0.08", "(α, β) [2]", PAIR, "DIVERGENT")]),
    "decimal-equality": ([(PCA, "  rho: 0.4\n", "  rho: 0.40\n")], BASELINE),
    "grouped-against-1": ([(E3, "  burn: 1000\n", "  burn: 1\n"), (NOTE, DAYS_ROW, "| burn-in | 1,000 days |")],
                          [(E3, "d5.burn", "1", "burn-in [1]", "1,000 days", "UNSUPPORTED_DOC_VALUE")]),
    "exponent-against-1": ([(E3, "  burn: 1000\n", "  burn: 1\n"), (NOTE, DAYS_ROW, "| burn-in | 1e3 days |")],
                           [(E3, "d5.burn", "1", "burn-in [1]", "1e3 days", "UNSUPPORTED_DOC_VALUE")]),
    "grouped-against-1000": ([(NOTE, DAYS_ROW, "| burn-in | 1,000 days |")],
                             [(E3, "d5.burn", "1000", "burn-in [1]", "1,000 days", "UNSUPPORTED_DOC_VALUE")]),
    "changed-unit": ([(NOTE, DAYS_ROW, "| burn-in | 1000 weeks |")],
                     [(E3, "d5.burn", "1000", "burn-in [1]", "1000 weeks", "UNSUPPORTED_DOC_VALUE")]),
    "extra-number-after-unit": ([(NOTE, DAYS_ROW, "| burn-in | 1000 days (2 chains) |")],
                                [(E3, "d5.burn", "1000", "burn-in [1]", "1000 days (2 chains)",
                                  "UNSUPPORTED_DOC_VALUE")]),
    "pair-arity": ([(NOTE, f"| {PAIR} |", "| (0.08, 0.90, 0.1) |")],
                   [(E3, "d5.alpha", "0.08", "(α, β) [1]", "(0.08, 0.90, 0.1)", "UNSUPPORTED_DOC_VALUE"),
                    (E3, "d5.beta", "0.9", "(α, β) [2]", "(0.08, 0.90, 0.1)", "UNSUPPORTED_DOC_VALUE")]),
    "pair-malformed": ([(NOTE, f"| {PAIR} |", "| (0.08 0.90) |")],
                       [(E3, "d5.alpha", "0.08", "(α, β) [1]", "(0.08 0.90)", "UNSUPPORTED_DOC_VALUE"),
                        (E3, "d5.beta", "0.9", "(α, β) [2]", "(0.08 0.90)", "UNSUPPORTED_DOC_VALUE")]),
    "alternative-extra-number": ([(NOTE, "(Gaussian)", "(Gaussian 2)")],
                                 [(PCA, T7, "7", "ν [1]", "7, or `None` (Gaussian 2)", "UNSUPPORTED_DOC_VALUE"),
                                  (PCA, GAUSS, "null", "ν [2]", "7, or `None` (Gaussian 2)", "UNSUPPORTED_DOC_VALUE")]),
    "alternative-without-none": ([(NOTE, NU, "7, or 5 (Gaussian)")],
                                 [(PCA, T7, "7", "ν [1]", "7, or 5 (Gaussian)", "UNSUPPORTED_DOC_VALUE"),
                                  (PCA, GAUSS, "null", "ν [2]", "7, or 5 (Gaussian)", "UNSUPPORTED_DOC_VALUE")]),
    "absence-is-not-none": ([(PCA, "    SYNTH_GAUSS_EQUICORR: null\n", "")],
                            [(PCA, GAUSS, "—", "ν [2]", NU, "UNMAPPED_DOC"), (PCA, T7, "7", "ν [1]", NU, "MATCH")]),
    "number-against-none": ([(PCA, "SYNTH_GAUSS_EQUICORR: null", "SYNTH_GAUSS_EQUICORR: 5")],
                            [(PCA, GAUSS, "5", "ν [2]", NU, "DIVERGENT")]),
    "none-against-number": ([(PCA, "SYNTH_T7_EQUICORR: 7", "SYNTH_T7_EQUICORR: null")],
                            [(PCA, T7, "null", "ν [1]", NU, "DIVERGENT")]),
    "alpha-missing-beta-present": ([(E3, "  alpha: 0.08\n", "")],
                                   [(E3, "d5.alpha", "—", "(α, β) [1]", PAIR, "UNMAPPED_DOC"),
                                    (E3, "d5.beta", "0.9", "(α, β) [2]", PAIR, "MATCH")]),
    "burn-missing": ([(E3, "  burn: 1000\n", "")], [(E3, "d5.burn", "—", "burn-in [1]", BURN, "UNMAPPED_DOC")]),
    "documented-row-renamed": ([(NOTE, "| burn-in |", "| burn |")],
                               [(E3, "d5.burn", "1000", "burn-in [1]", "—", "UNMAPPED_CONFIG"),
                                (E3, "—", "—", "burn", BURN, "UNMAPPED_DOC"),
                                (PCA, "—", "—", "burn", BURN, "UNMAPPED_DOC")]),
    "new-config-key": ([(E3, "  T_clean: 941\n", "  T_clean: 941\n  extra: 3\n")],
                       [(E3, "d5.extra", "3", "—", "—", "UNMAPPED_CONFIG")]),
    "new-documented-row-not-matched-by-value": ([(NOTE, f"{DAYS_ROW}\n", f"{DAYS_ROW}\n| T | 941 |\n")],
                                                [(E3, "d5.T_clean", "941", "—", "—", "UNMAPPED_CONFIG"),
                                                 (E3, "—", "—", "T", "941", "UNMAPPED_DOC"),
                                                 (PCA, "—", "—", "T", "941", "UNMAPPED_DOC")]),
    "text-against-number": ([(E3, "  alpha: 0.08\n", "  alpha: '0.08'\n")],
                            [(E3, "d5.alpha", '"0.08"', "(α, β) [1]", PAIR, "DIVERGENT")]),
    "boolean-against-1": ([(E3, "  burn: 1000\n", "  burn: true\n"), (NOTE, DAYS_ROW, "| burn-in | 1 days |")],
                          [(E3, "d5.burn", "true", "burn-in [1]", "1 days", "DIVERGENT")]),
}


@pytest.mark.parametrize("changes, expected", list(CASES.values()), ids=list(CASES))
def test_link_statuses_compare_whole_cells_and_keep_absences_visible(tmp_path, changes, expected):
    rows = ab.inventory(_repo(tmp_path, changes))[1]
    for row in expected:
        assert row in rows, row
    assert {row[5] for row in rows} <= STATUSES
    for source, key, link in LINKED:
        assert sum(row[0] == source and row[1] == key and row[3] == link for row in rows) == 1, key
    assert all(row[2] == "—" for row in rows if row[5] == "UNMAPPED_DOC")
    assert all(row[4] == "—" and row[5] == "UNMAPPED_CONFIG" for row in rows if row[3] == "—")
    assert all(row[4] in (PAIR, NU, RHO, BURN) for row in rows if row[5] == "MATCH")


REFUSALS = {
    "duplicate-yaml-key": ((E3, "  beta: 0.90\n", "  beta: 0.90\n  beta: 0.85\n"), "duplicate key 'beta'"),
    "nan": ((E3, "  alpha: 0.08\n", "  alpha: .nan\n"), "non-finite or non-JSON value"),
    "inf-in-list": ((E3, "[t7, gaussian]", "[t7, .inf]"), "non-finite or non-JSON value"),
    "negative-inf": ((PCA, "  rho: 0.4\n", "  rho: -.inf\n"), "non-finite or non-JSON value"),
    "date": ((E3, "  T_clean: 941\n", "  T_clean: 2020-01-01\n"), "non-finite or non-JSON value"),
    "section-missing": ((E3, "d5:\n", "d6:\n"), "no non-empty mapping section 'd5'"),
    "section-not-mapping": ((E3, D5_BLOCK, "d5: [1, 2]\n"), "no non-empty mapping section 'd5'"),
    "section-empty": ((E3, D5_BLOCK, "d5: {}\n"), "no non-empty mapping section 'd5'"),
    "top-level-not-mapping": ((E3, E3_TEXT, "- 1\n"), "no non-empty mapping section 'd5'"),
    "nested-mapping-empty": ((PCA, BACKGROUNDS, "  backgrounds: {}\n"), "synthetic.backgrounds is an empty mapping"),
    "integer-key": ((E3, "  T_clean: 941\n", "  T_clean: 941\n  1: 2\n"), "is not a plain name"),
    "dotted-key": ((E3, "  T_clean: 941\n", "  T_clean: 941\n  a.b: 2\n"), "is not a plain name"),
    "pipe-in-key": ((E3, "  T_clean: 941\n", "  T_clean: 941\n  'a|b': 2\n"), "is not a plain name"),
    "pipe-in-value": ((E3, "[t7, gaussian]", "[t7, 'a|b']"), "has '|' in value"),
    "yaml-syntax": ((E3, "[t7, gaussian]", "[t7, gaussian"), "invalid YAML"),
    "heading-missing": ((NOTE, f"{HEADING}\n", "## D5 - Monte Carlo backgrounds\n"), "exactly one"),
    "heading-twice": ((NOTE, "## Amplitude conventions (F1–F3)\n", f"{HEADING}\n"), "exactly one"),
    "header-changed": ((NOTE, "| parameter | values |", "| name | values |"), "header"),
    "table-empty": ((NOTE, ROWS, ""), "no documented row"),
    "label-twice": ((NOTE, f"| ν | {NU} |\n", f"| ν | {NU} |\n| ν | 5 |\n"), "duplicate parameter label"),
    "label-empty": ((NOTE, "| burn-in |", "|  |"), "empty or duplicate parameter label"),
    "documented-inf": ((NOTE, DAYS_ROW, "| burn-in | inf days |"), "non-finite documented value"),
    "documented-nan": ((NOTE, f"| {PAIR} |", "| (NaN, 0.90) |"), "non-finite documented value"),
    "documented-infinity-sign": ((NOTE, f"| ν | {NU} |", "| ν | ∞, or `None` (Gaussian) |"),
                                 "non-finite documented value"),
    "ragged-row": ((NOTE, DAYS_ROW, "| burn-in | 1000 | days |"), "ragged"),
    "equal-keys-hex-and-decimal": (_outside(E3, "{0x10: first, 16: second}"), "duplicate key 16"),
    "equal-keys-octal-and-decimal": (_outside(E3, "{020: first, 16: second}"), "duplicate key 16"),
    "equal-keys-yes-and-true": (_outside(PCA, "{yes: first, true: second}"), "duplicate key True"),
    "equal-keys-tilde-and-null": (_outside(PCA, "{~: first, null: second}"), "duplicate key None"),
    "equal-keys-int-and-float": (_outside(E3, "{1: first, 1.0: second}"), "duplicate key 1.0"),
    "equal-keys-int-and-bool": (_outside(E3, "{1: first, true: second}"), "duplicate key True"),
    "equal-keys-in-unselected-list": (_outside(PCA, "[{0x10: first, 16: second}]"), "duplicate key 16"),
    "equal-keys-in-selected-list-leaf": ((E3, "[t7, gaussian]", "[t7, gaussian, {0x10: first, 16: second}]"),
                                         "duplicate key 16"),
    "equal-keys-in-selected-mapping": ((PCA, BACKGROUNDS, BACKGROUNDS + "    0x10: first\n    16: second\n"),
                                       "duplicate key 16"),
    "merge-key-overridden": ((E3, "  beta: 0.90\n", "  <<: {beta: 0.85}\n  beta: 0.90\n"), "duplicate key 'beta'"),
    "unhashable-sequence-key": (_outside(E3, "\n  ? [a, b]\n  : c"), "found unhashable key"),
    "unhashable-mapping-key": (_outside(E3, "\n  ? {a: 1}\n  : c"), "found unhashable key"),
    "unsupported-tagged-key": (_outside(E3, "\n  ? !!python/tuple [a, b]\n  : c"),
                               "could not determine a constructor"),
    "date-key": ((E3, "  T_clean: 941\n", "  T_clean: 941\n  2019-12-31: 2\n"), "is not a plain name"),
    "cyclic-section": ((E3, D5_BLOCK, "d5: &d {loop: *d}\n"), "section 'd5': Circular reference detected"),
    "cyclic-nested-mapping": ((PCA, BACKGROUNDS, ANCHORED + "    back: *b\n"),
                              "section 'synthetic': Circular reference detected"),
    "cyclic-list-leaf": ((E3, "[t7, gaussian]", "&l [t7, *l]"), "section 'd5': Circular reference detected"),
}


@pytest.mark.parametrize("change, match", list(REFUSALS.values()), ids=list(REFUSALS))
def test_invalid_inputs_refused_before_any_write(tmp_path, monkeypatch, capsys, change, match):
    root = _repo(tmp_path, [change])
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main([]) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"appendix-b: error: {change[0]}: ") and match in out
    assert not (root / OUT).exists()


ACCEPTED = {
    "int-and-str-keys-distinct": ([_outside(E3, "{1: first, '1': second}")], BASELINE),
    "merge-without-override": ([_outside(E3, "{<<: {k: first}, j: second}")], BASELINE),
    "cycle-outside-selected-sections": ([_outside(PCA, "&o {self: *o}")], BASELINE),
    "mapping-alias-reused-in-section": (
        [(PCA, BACKGROUNDS, ANCHORED + "  copy: *b\n")],
        BASELINE[:10] + [(PCA, "synthetic.copy.SYNTH_GAUSS_EQUICORR", "null", "—", "—", "UNMAPPED_CONFIG"),
                         (PCA, "synthetic.copy.SYNTH_T7_EQUICORR", "7", "—", "—", "UNMAPPED_CONFIG")]
        + BASELINE[10:]),
    "unselected-alias-reused-twice": (
        [(E3, "alpha: 0.05\n", "alpha: 0.05\nshared: &s {extra: 1}\n"),
         (E3, "  T_clean: 941\n", "  T_clean: 941\n  reuse: *s\n  again: *s\n")],
        BASELINE[:4] + [(E3, "d5.reuse.extra", "1", "—", "—", "UNMAPPED_CONFIG"),
                        (E3, "d5.again.extra", "1", "—", "—", "UNMAPPED_CONFIG")] + BASELINE[4:]),
}


@pytest.mark.parametrize("changes, expected", list(ACCEPTED.values()), ids=list(ACCEPTED))
def test_distinct_keys_finite_reuse_and_unselected_cycles_are_accepted(tmp_path, changes, expected):
    assert ab.inventory(_repo(tmp_path, changes))[1] == expected


@pytest.mark.parametrize("rel, match", [(E3, "invalid YAML"), (NOTE, "'utf-8' codec can't decode")])
def test_invalid_utf8_refused(tmp_path, monkeypatch, capsys, rel, match):
    root = _repo(tmp_path)
    (root / rel).write_bytes((root / rel).read_bytes() + b"\xff\n")
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main([]) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"appendix-b: error: {rel}: ") and match in out
    assert not (root / OUT).exists()


@pytest.mark.parametrize("rel, prefix", [(E3, "configs"), (PCA, "configs"), (NOTE, "docs")])
def test_input_escaping_through_a_link_or_missing_is_refused(tmp_path, monkeypatch, capsys, rel, prefix):
    root = _repo(tmp_path / "repo")
    outside = tmp_path / "outside.txt"
    outside.write_bytes((root / rel).read_bytes())
    (root / rel).unlink()
    (root / rel).symlink_to(outside)
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main([]) == 1
    assert f"appendix-b: error: {rel!r} resolves outside {prefix}/" in capsys.readouterr().out
    (root / rel).unlink()
    assert ab.main([]) == 1
    assert f"appendix-b: error: {rel!r} does not resolve" in capsys.readouterr().out
    assert not list((root / OUT).parent.iterdir())


@pytest.mark.parametrize("out", ["/appendix_b.md", "../appendix_b.md", "logs/../appendix_b.md", "./logs/appendix_b.md",
                                 "logs//appendix_b.md", "results/appendix_b.md", "logs/appendix_b.csv", "logs",
                                 "logs/absent/appendix_b.md", "logs/link/appendix_b.md", "logs/file/appendix_b.md"])
def test_out_path_outside_logs_or_unresolved_is_refused(tmp_path, monkeypatch, capsys, out):
    root = _repo(tmp_path / "repo")
    (tmp_path / "outside").mkdir()
    (root / "logs" / "link").symlink_to(tmp_path / "outside", target_is_directory=True)
    (root / "logs" / "file").write_bytes(b"")
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main(["--out", out]) == 1
    assert capsys.readouterr().out.startswith(f"appendix-b: error: --out {out!r}")
    assert not list((tmp_path / "outside").iterdir()) and not (tmp_path / "appendix_b.md").exists()
    assert sorted(path.name for path in (root / "logs").iterdir()) == ["21-appendix", "file", "link"]
    assert not list((root / OUT).parent.iterdir()) and not (root / "results").exists()


@pytest.mark.parametrize("kind", ["file", "dangling-link", "link-to-outside-file"])
def test_existing_target_is_never_overwritten(tmp_path, monkeypatch, capsys, kind):
    root = _repo(tmp_path / "repo")
    outside = tmp_path / "outside.md"
    outside.write_bytes(b"outside\n")
    target = root / OUT
    if kind == "file":
        target.write_bytes(b"kept\n")
    else:
        target.symlink_to(outside if kind == "link-to-outside-file" else tmp_path / "absent.md")
    monkeypatch.setattr(ab, "ROOT", root)
    assert ab.main([]) == 1
    assert "appendix-b: error: --out 'logs/21-appendix/appendix_b.md' exists; refusing to overwrite" in (
        capsys.readouterr().out)
    assert outside.read_bytes() == b"outside\n" and not (tmp_path / "absent.md").exists()
    assert kind != "file" or target.read_bytes() == b"kept\n"
