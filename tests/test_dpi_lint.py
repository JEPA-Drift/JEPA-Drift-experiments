"""Tests of tools/dpi_lint.py (lot 21-dpi): lexical witnesses, negation contract, comments, current corpus, refusals."""
import ast
import sys
from pathlib import Path

import pytest

from tools import dpi_lint as dl
from tools import trace_numbers as tn

SOURCES = ("paper/appA_proofs.tex", "paper/sec3_theory.tex")
SEC3 = "paper/sec3_theory.tex"
CAVEAT_LINE = ("dpi-lint: pattern lint only: zero FLAG does not establish semantic consistency with the DPI, and a "
               "FLAG requests review without judging the sentence")
DIAGNOSTIC = ("wording suggests creating or increasing information/KL; review it against the DPI (KL of z <= KL of "
              "(x, C)); not a verdict on the sentence")
FLAG_TEXT = "An encoder creates information.\n"
SENTINEL = (SEC3, 25, 12, "creates no information", True)
NEGATION = "No encoder creates information.\n"
NEUTRAL = "Neutral text.\n"


def _verdicts(text):
    return ["NEGATED" if negated else "FLAG" for _, _, negated in dl.find(text)]


def _paper(root, files):
    (root / "paper").mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (root / "paper" / name).write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return root


def _alter(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


@pytest.mark.parametrize("text", [
    "The map increases KL.",
    "It Increased the Kullback--Leibler divergence.",
    "IT INCREASES INFORMATION.",
    "There is an increase in the information rate.",
    "This holds by increasing $\\mathrm{KL}(P_1\\|P_0)$.",
    "An encoder creates information.",
    "An encoder Creates\ninformation.",
    "It creates new drift information.",
    "This is the creation of information.",
    "It increases, in the latent space, the KL.",
    "A 5\\% shift creates information.",
    "It creates % remark\ninformation.",
])
def test_prompt_pattern_variants_are_flagged(text):
    assert _verdicts(text) == ["FLAG"]


@pytest.mark.parametrize("text", [
    "An encoder creates no information.",
    "It creates neither KL nor information.",
    "No encoder creates information.",
    "A map cannot increase the KL.",
    "Processing never increases information.",
    "It does not increase the divergence.",
    "It works without creating information.",
    "There is no increase in information.",
    "not x y increases KL.",
])
def test_contract_negations_are_negated(text):
    assert _verdicts(text) == ["NEGATED"]


@pytest.mark.parametrize("text", [
    "The encoder not only increases the KL.",
    "The encoder not merely creates information.",
    "The encoder not just increases information.",
    "The encoder not \\emph{only} increases the KL.",
    "The encoder creates no less information than the data.",
    "The encoder no doubt increases the KL.",
])
def test_pseudo_negations_do_not_suppress_a_flag(text):
    assert _verdicts(text) == ["FLAG"]


@pytest.mark.parametrize("text, verdicts", [
    ("It does not create but increases information.", ["NEGATED", "FLAG"]),
    ("It does not fail but increases information.", ["FLAG"]),
    ("It does not fail yet increases information.", ["FLAG"]),
    ("It does not fail however increases information.", ["FLAG"]),
    ("It does not create and increases information.", ["NEGATED", "FLAG"]),
    ("It never creates or increases information.", ["NEGATED", "FLAG"]),
    ("It neither creates nor increases information.", ["NEGATED", "NEGATED"]),
    ("The encoder, not the data, creates information.", ["FLAG"]),
    ("not x y z increases KL.", ["FLAG"]),
    ("It increases a b c d e f KL.", ["FLAG"]),
    ("It increases a b c d e f g KL.", []),
    *((f"It increases{stop} the KL.", []) for stop in ".;:!?"),
])
def test_negation_scope_and_window_bounds(text, verdicts):
    assert _verdicts(text) == verdicts


@pytest.mark.parametrize("backslashes, first_line", [(0, []), (1, ["FLAG"]), (2, []), (3, ["FLAG"])])
def test_percent_comment_follows_backslash_parity(backslashes, first_line):
    text = "x " + "\\" * backslashes + "% creates information\nIt creates information.\n"
    blanked = dl.blank(text)
    assert len(blanked) == len(text) and blanked.split("\n")[1:] == text.split("\n")[1:]
    assert blanked.startswith("x " + "\\" * backslashes)
    assert ("creates" in blanked.split("\n")[0]) == bool(backslashes % 2)
    assert _verdicts(text) == first_line + ["FLAG"]
    assert dl.find(text)[-1][0] == text.index("creates information.")


@pytest.mark.parametrize("text", [
    "The KL divergence grows with $N$.",
    "It increases the Sharpe ratio.",
    "A non-increasing information sequence.",
    "% An encoder creates information.",
])
def test_text_without_pattern_has_no_hit(text):
    assert dl.find(text) == []


def test_main_reports_location_words_and_flag_exit(tmp_path, monkeypatch, capsys):
    root = _paper(tmp_path, {"a.tex": "Line one.\nLine two.\nThe map increases the\nKL here.\n"})
    monkeypatch.setattr(dl, "ROOT", root)
    assert dl.main([]) == 1
    assert capsys.readouterr().out.split("\n") == [
        f"paper/a.tex:3:9: FLAG 'increases the KL': {DIAGNOSTIC}",
        "dpi-lint: files 1 (paper/a.tex); hits 1: FLAG 1, NEGATED 0",
        "dpi-lint: FLAGGED: 1 of 1 hits to review",
        CAVEAT_LINE,
        "",
    ]


@pytest.mark.parametrize("extra, expected", [
    ({}, [SENTINEL]),
    ({"aaa.tex": NEGATION, "zzz.tex": NEUTRAL}, [("paper/aaa.tex", 1, 12, "creates information", True), SENTINEL]),
    ({"aaa.tex": NEUTRAL, "zzz.tex": NEGATION}, [SENTINEL, ("paper/zzz.tex", 1, 12, "creates information", True)]),
], ids=["current corpus", "negated file first", "negated file last"])
def test_current_corpus_keeps_its_negation_sentinel_and_zero_flag(tmp_path, monkeypatch, capsys, extra, expected):
    root = dl.ROOT
    if extra:
        corpus = {path.name: path.read_bytes() for path in (dl.ROOT / "paper").glob("*.tex")}
        root = _paper(tmp_path, {**corpus, **extra})
        monkeypatch.setattr(dl, "ROOT", root)
    before = {rel: (root / rel).read_bytes() for rel in SOURCES}
    assert dl.main([]) == 0
    out = capsys.readouterr().out
    files, hits = dl.scan(root)
    assert set(SOURCES) <= set(files) and set(expected) <= set(hits) and all(hit[4] for hit in hits)
    printed = set(out.split("\n"))
    assert all(f"{name}:{line}:{col}: NEGATED {words!r}" in printed for name, line, col, words, _ in expected)
    assert f"hits {len(hits)}: FLAG 0, NEGATED {len(hits)}\n" in out
    assert out.endswith(f"{CAVEAT_LINE}\n") and "FLAGGED" not in out
    assert {rel: (root / rel).read_bytes() for rel in SOURCES} == before


@pytest.mark.parametrize("new", ["creates information", "creates new information", "creates no less information"])
def test_mutated_copy_of_the_current_negation_is_flagged(tmp_path, new):
    text = _alter((dl.ROOT / SEC3).read_bytes().decode("utf-8"), "creates no information", new)
    root = _paper(tmp_path, {"sec3_theory.tex": text})
    assert dl.scan(root) == ([SEC3], [(SEC3, 25, 12, new, False)])


def _refusal_corpus(root, outside, case):
    if case == "bib only":
        _paper(root, {"refs.bib": "@misc{a, title={An encoder creates information}}\n"})
    if case in ("no paper", "bib only"):
        return root
    _paper(root, {"a.tex": FLAG_TEXT})
    x = root / "paper" / "x.tex"
    if case == "link outside the root":
        outside.write_text(FLAG_TEXT, encoding="utf-8")
        x.symlink_to(outside)
    elif case == "link to data/raw/eurofidai":
        target = root / "data" / "raw" / "eurofidai" / "x.tex"
        target.parent.mkdir(parents=True)
        target.write_text(FLAG_TEXT, encoding="utf-8")
        x.symlink_to(target)
    elif case == "broken link":
        x.symlink_to(root / "missing.tex")
    elif case == "directory":
        x.mkdir()
    elif case == "unreadable":
        x.write_text(FLAG_TEXT, encoding="utf-8")
        x.chmod(0)
    else:
        x.write_bytes({"empty": b"", "comments only": b"% An encoder creates information.\n   % more\n",
                       "not UTF-8": b"\xff An encoder creates information.\n"}[case])
    return root


@pytest.mark.parametrize("case, message", [
    ("no paper", "no paper/*.tex file: nothing to lint"),
    ("bib only", "no paper/*.tex file: nothing to lint"),
    ("link outside the root", "'paper/x.tex' resolves outside paper/ or is not a regular file"),
    ("link to data/raw/eurofidai", "'paper/x.tex' resolves outside paper/ or is not a regular file"),
    ("broken link", "'paper/x.tex' does not resolve (FileNotFoundError)"),
    ("directory", "'paper/x.tex' resolves outside paper/ or is not a regular file"),
    ("empty", "paper/x.tex: no text outside LaTeX comments"),
    ("comments only", "paper/x.tex: no text outside LaTeX comments"),
    ("not UTF-8", "paper/x.tex: not UTF-8 (invalid start byte at byte 0)"),
    ("unreadable", "paper/x.tex: not readable (PermissionError)"),
])
def test_refused_corpus_or_path_prints_one_error_line(tmp_path, monkeypatch, capsys, case, message):
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(dl, "ROOT", _refusal_corpus(root, tmp_path / "outside.tex", case))
    assert dl.main([]) == 1
    assert capsys.readouterr().out == f"dpi-lint: error: {message}\n"


def test_reuses_the_trace_path_guard_and_imports_stdlib_only():
    assert dl.confined is tn.confined
    tree = ast.parse(Path(dl.__file__).read_text(encoding="utf-8"))
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert "tools" in imported and imported - {"tools"} <= sys.stdlib_module_names
