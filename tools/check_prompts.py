"""Fidelity of the stream prompts: every prompts/streams/prompt-*.md is an exact substring of the master collection.

`python tools/check_prompts.py` (make prompts-check) runs the check; `--sync-master` first replaces each block of
prompts/Prompts_Claude_Code_v5.md, found by its `## PROMPT <id> —` title, with the stream file and appends the blocks
missing from the master at the end of its section 4.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "prompts" / "streams"
MASTER = ROOT / "prompts" / "Prompts_Claude_Code_v5.md"
TITLE = re.compile(r"(?m)^## PROMPT (\S+) —")
FENCE = re.compile(r"(?m)````$")


def blocks(master):
    """{id: (start, end)} of each block: title to closing fence, next title or end, trailing newlines excluded."""
    titles = list(TITLE.finditer(master))
    spans = {}
    for i, m in enumerate(titles):
        stop = titles[i + 1].start() if i + 1 < len(titles) else len(master)
        fence = FENCE.search(master, m.start(), stop)
        if m.group(1) in spans:
            raise ValueError(f"PROMPT {m.group(1)} appears twice in the master")
        body = master[m.start():fence.start() if fence else stop].rstrip("\n")
        spans[m.group(1)] = (m.start(), m.start() + len(body))
    return spans


def check(master, prompts):
    """Names of the stream prompts that are not an exact substring of the master."""
    return [name for name, text in prompts.items() if text not in master]


def sync(master, prompts):
    """Master with each block replaced by its stream prompt and the prompts without a block appended to section 4."""
    keyed = {}
    for name, text in prompts.items():
        m = TITLE.match(text)
        if m is None:
            raise ValueError(f"{name}: the first line is not a '## PROMPT <id> —' title")
        keyed[m.group(1)] = text.rstrip("\n")
    spans = blocks(master)
    for pid, (start, end) in sorted(spans.items(), key=lambda item: item[1][0], reverse=True):
        if pid in keyed:
            master = master[:start] + keyed[pid] + master[end:]
    # ponytail: section 4 ends the master, so new blocks go at the end of file; locate its end if a section 5 appears
    return master + "".join(f"\n````markdown\n{text}\n````\n" for pid, text in keyed.items() if pid not in spans)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sync-master", action="store_true", help="rewrite the master blocks from the stream files first")
    args = ap.parse_args(argv)
    prompts = {p.name: p.read_text(encoding="utf-8") for p in sorted(STREAMS.glob("prompt-*.md"))}
    master = MASTER.read_text(encoding="utf-8")
    if args.sync_master:
        synced = sync(master, prompts)
        print(f"sync-master: master {'rewritten' if synced != master else 'unchanged'}")
        if synced != master:
            MASTER.write_text(synced, encoding="utf-8")
            master = synced
    failed = check(master, prompts)
    print(f"prompts-check: {len(prompts) - len(failed)}/{len(prompts)}"
          + "".join(f"\n  not in the master: {name}" for name in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
