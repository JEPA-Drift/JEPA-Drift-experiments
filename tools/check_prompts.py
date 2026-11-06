"""Fidelity of the stream prompts to the master collection prompts/Prompts_Claude_Code_v5.md.

The stream prompts are prompts/streams/prompt-*.md and prompts/streams/[0-9][0-9]_STREAM_PCA_DRIFT_*.md, read as UTF-8
bytes without newline translation; their `## PROMPT <id> —` titles are unique and their ids equal EXPECTED_IDS.
`python tools/check_prompts.py` (make prompts-check) requires each master block, found by its title, to equal its stream
file up to trailing newlines, the full file text to be present in the master and the ````markdown fences to be balanced.
`--sync-master` first replaces each block with its stream file and appends the missing blocks at the end of section 4;
the result is checked before anything is written.
"""
import argparse
import fnmatch
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "prompts" / "streams"
MASTER = ROOT / "prompts" / "Prompts_Claude_Code_v5.md"
PATTERNS = ("prompt-*.md", "[0-9][0-9]_STREAM_PCA_DRIFT_*.md")
EXPECTED_IDS = frozenset([*(str(i) for i in range(1, 29)), "8b", "28-PCA", "29", "30", "31"])
TITLE = re.compile(r"(?m)^## PROMPT (\S+) —")
FENCE = re.compile(r"(?m)````$")
OPEN = re.compile(r"(?m)^````markdown$")


def read_exact(path):
    """Text of a file decoded from its UTF-8 bytes, without newline translation."""
    return Path(path).read_bytes().decode("utf-8")


def discover(streams):
    """{name: text} of the stream prompts: prompt-*.md, then [0-9][0-9]_STREAM_PCA_DRIFT_*.md, each sorted by name."""
    return {p.name: read_exact(p) for pattern in PATTERNS for p in sorted(Path(streams).glob(pattern))}


def prompt_ids(prompts):
    """{id: name} of the first-line titles; a missing title or an id shared by two files raises ValueError."""
    ids = {}
    for name, text in prompts.items():
        m = TITLE.match(text)
        if m is None:
            raise ValueError(f"{name}: the first line is not a '## PROMPT <id> —' title")
        if m.group(1) in ids:
            raise ValueError(f"PROMPT {m.group(1)} titles both {ids[m.group(1)]} and {name}")
        ids[m.group(1)] = name
    return ids


def require_expected(ids, expected):
    """Raise ValueError unless the prompt ids are exactly the expected ones, naming the missing and unexpected ids."""
    missing, unexpected = sorted(set(expected) - set(ids)), sorted(set(ids) - set(expected))
    if missing or unexpected:
        raise ValueError(f"prompt ids differ from the expected set: missing {missing}, unexpected {unexpected}")


def blocks(master):
    """{id: (start, end)}: title to closing fence, next ````markdown opening or title; trailing newlines excluded."""
    titles = list(TITLE.finditer(master))
    spans = {}
    for i, m in enumerate(titles):
        stop = titles[i + 1].start() if i + 1 < len(titles) else len(master)
        opening = OPEN.search(master, m.end(), stop)
        stop = opening.start() if opening else stop
        fence = FENCE.search(master, m.start(), stop)
        if m.group(1) in spans:
            raise ValueError(f"PROMPT {m.group(1)} appears twice in the master")
        body = master[m.start():fence.start() if fence else stop].rstrip("\n")
        spans[m.group(1)] = (m.start(), m.start() + len(body))
    return spans


def check(master, prompts):
    """Prompts whose master block differs from their text up to trailing newlines, or whose text is absent."""
    spans = blocks(master)
    failed = []
    for name, text in prompts.items():
        m = TITLE.match(text)
        span = spans.get(m.group(1)) if m else None
        if span is None or master[span[0]:span[1]] != text.rstrip("\n") or text not in master:
            failed.append(name)
    return failed


def fences_balanced(master):
    """True iff the ````markdown openings and the ```` closings are equally many; a truncated master loses a closing."""
    return len(OPEN.findall(master)) == len(FENCE.findall(master))


def sync(master, prompts):
    """Master with each block replaced by its prompt and the blockless prompts appended to section 4, checked first."""
    keyed = {pid: prompts[name].rstrip("\n") for pid, name in prompt_ids(prompts).items()}
    spans = blocks(master)
    for pid, (start, end) in sorted(spans.items(), key=lambda item: item[1][0], reverse=True):
        if pid in keyed:
            master = master[:start] + keyed[pid] + master[end:]
    # ponytail: section 4 ends the master, so new blocks go at the end of file; locate its end if a section 5 appears
    synced = master + "".join(f"\n````markdown\n{text}\n````\n" for pid, text in keyed.items() if pid not in spans)
    failed = check(synced, prompts)
    if failed or not fences_balanced(synced):
        raise ValueError(f"the synchronized master fails its check: {failed or 'unbalanced ````markdown fences'}")
    return synced


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sync-master", action="store_true", help="rewrite the master blocks from the stream files first")
    args = ap.parse_args(argv)
    prompts = discover(STREAMS)
    master = read_exact(MASTER)
    try:
        ids = prompt_ids(prompts)
        require_expected(ids, EXPECTED_IDS)
        if args.sync_master:
            synced = sync(master, prompts)
            print(f"sync-master: master {'rewritten' if synced != master else 'unchanged'}")
            if synced != master:
                MASTER.write_bytes(synced.encode("utf-8"))
                master = synced
        failed = check(master, prompts)
        if not fences_balanced(master):
            raise ValueError("unbalanced ````markdown fences: truncated master")
    except ValueError as exc:
        print(f"prompts-check: error: {exc}")
        return 1
    pca = [pid for pid, name in ids.items() if fnmatch.fnmatch(name, PATTERNS[1])]
    print(f"prompts-check: {len(prompts) - len(failed)}/{len(prompts)} ({len(prompts) - len(pca)} {PATTERNS[0]} + "
          f"{len(pca)} {PATTERNS[1]}" + (f": {', '.join(pca)})" if pca else ")")
          + "".join(f"\n  not in the master: {name}" for name in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
