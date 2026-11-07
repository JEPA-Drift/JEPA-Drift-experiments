"""Lexical DPI guard over paper/*.tex (lot 21-dpi): it requests review of wording and judges no sentence.

`python -m tools.dpi_lint`, run from the repository root, lists every paper/*.tex file (not recursive). It refuses the
whole run, before any read, when `tools.trace_numbers.confined` rejects one path, and it also refuses a missing or
empty corpus, an unreadable or non-UTF-8 file and a file with no text outside comments. A `%` preceded by an even
number of contiguous backslashes starts a comment; comments are blanked with spaces, so lines and columns stay those
of the source. A hit is a verb `increase` or `create` (with -s, -ed, -ing, or the noun `increase` or `creation`; not
after `non-`) followed, within 6 words and with no `. ; : ! ?` in between, by `KL`, `information` or `divergence`.
Each verb is read on its own. The hit is NEGATED when the word after the verb is `no` or `neither`, or when `no`,
`not`, `never`, `cannot`, `nor`, `neither` or `without` stands among the 3 words before the verb with no comma,
`. ; : ! ?`, `but`, `yet`, `however` or earlier candidate verb after it; `no less`, `no doubt`, `not only`,
`not merely` and `not just` never negate. Any other hit is a FLAG. Exit 0 only without refusal and without FLAG.
Zero FLAG does not establish semantic consistency with the DPI: passive or reversed order, paraphrases and
constructions outside the two windows are not seen. A FLAG is a review request, not a verdict on the sentence.
"""
import argparse
import re
from pathlib import Path

from tools.trace_numbers import confined

ROOT = Path(__file__).resolve().parents[1]
COMMENT = re.compile(r"(?<!\\)((?:\\\\)*)%[^\n]*")
STEM = r"(?:increas(?:e|es|ed|ing)|creat(?:e|es|ed|ing|ion))\b"
# ponytail: verb before object only; passive or reversed order ("information is created") needs a GO for a new pattern
VERB = re.compile(rf"(?<!non-)\b{STEM}", re.IGNORECASE)
TAIL = re.compile(r"(?:[^\w.;:!?]+\w+){0,6}?[^\w.;:!?]+(?:KL|information|divergences?)\b", re.IGNORECASE)
SKIP = r"(?:\\[A-Za-z]+|\W)+"
NO = rf"no\b(?!{SKIP}(?:less|doubt)\b)"
NOT = rf"not\b(?!{SKIP}(?:only|merely|just)\b)"
AFTER = re.compile(rf"\W+(?:{NO}|neither\b)", re.IGNORECASE)
CLAUSE = r"[^\w.,;:!?]+"
BEFORE = re.compile(rf"\b(?:{NO}|{NOT}|(?:never|cannot|nor|neither|without)\b)"
                    rf"(?:{CLAUSE}(?!(?:but|yet|however)\b|{STEM})\w+){{0,2}}{CLAUSE}\Z", re.IGNORECASE)
DIAGNOSTIC = ("wording suggests creating or increasing information/KL; review it against the DPI (KL of z <= KL of "
              "(x, C)); not a verdict on the sentence")
CAVEAT = ("pattern lint only: zero FLAG does not establish semantic consistency with the DPI, and a FLAG requests "
          "review without judging the sentence")


def blank(text):
    """Text whose LaTeX comments, from a `%` after an even run of backslashes to the line end, are set to spaces."""
    return COMMENT.sub(lambda m: m[1] + " " * (len(m[0]) - len(m[1])), text)


def find(text):
    """[(offset, words, negated)] of the verb-object hits of a LaTeX text; words is the hit with blanks normalized."""
    text = blank(text)
    hits = []
    for verb in VERB.finditer(text):
        tail = TAIL.match(text, verb.end())
        if tail:
            negated = bool(AFTER.match(text, verb.end()) or BEFORE.search(text, 0, verb.start()))
            hits.append((verb.start(), " ".join(text[verb.start():tail.end()].split()), negated))
    return hits


def scan(root):
    """(files, hits) of root/paper/*.tex; every path is confined before the first read, refusals raise ValueError."""
    names = [f"paper/{path.name}" for path in sorted((Path(root) / "paper").glob("*.tex"))]
    if not names:
        raise ValueError("no paper/*.tex file: nothing to lint")
    paths = [confined(root, name, "paper") for name in names]
    hits = []
    for name, path in zip(names, paths):
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"{name}: not UTF-8 ({exc.reason} at byte {exc.start})") from exc
        except OSError as exc:
            raise ValueError(f"{name}: not readable ({type(exc).__name__})") from exc
        if not blank(text).strip():
            raise ValueError(f"{name}: no text outside LaTeX comments")
        for offset, words, negated in find(text):
            hits.append((name, text.count("\n", 0, offset) + 1, offset - text.rfind("\n", 0, offset), words, negated))
    return names, hits


def main(argv=None):
    """CLI: print each hit, the summary lines and the caveat, or one error line; return 1 on refusal or FLAG, else 0."""
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        names, hits = scan(ROOT)
    except ValueError as exc:
        print(f"dpi-lint: error: {exc}")
        return 1
    for name, line, col, words, negated in hits:
        print(f"{name}:{line}:{col}: " + (f"NEGATED {words!r}" if negated else f"FLAG {words!r}: {DIAGNOSTIC}"))
    flagged = sum(not hit[4] for hit in hits)
    print(f"dpi-lint: files {len(names)} ({', '.join(names)}); hits {len(hits)}: FLAG {flagged}, "
          f"NEGATED {len(hits) - flagged}")
    if flagged:
        # ponytail: no waiver list; a reviewed FLAG that must stay needs a GO (rewording or a contract change)
        print(f"dpi-lint: FLAGGED: {flagged} of {len(hits)} hits to review")
    print(f"dpi-lint: {CAVEAT}")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
