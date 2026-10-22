"""Tests of tools/check_prompts.py (stream 8b) on a synthetic master collection."""
import pytest

from tools import check_prompts as cp

MASTER = ("# Prompts\n\n## 4. Prompts\n\n````markdown\n## PROMPT 1 — One\n\nold body\n````\n\n"
          "````markdown\n## PROMPT 2 — Two\n\nbody 2\n```bash\nmake\n```````\n\nclosing notes\n")
PROMPTS = {"prompt-01.md": "## PROMPT 1 — One\n\nnew body\n",
           "prompt-02.md": "## PROMPT 2 — Two\n\nbody 2\n```bash\nmake\n```",
           "prompt-03.md": "## PROMPT 3 — Three\n\nbody 3\n"}


def test_sync_replaces_appends_and_is_idempotent():
    assert cp.check(MASTER, PROMPTS) == ["prompt-01.md", "prompt-03.md"]
    synced = cp.sync(MASTER, PROMPTS)
    assert cp.check(synced, PROMPTS) == [] and "old body" not in synced
    assert "make\n```````\n\nclosing notes\n" in synced
    assert synced.endswith("closing notes\n\n````markdown\n## PROMPT 3 — Three\n\nbody 3\n````\n")
    assert cp.sync(synced, PROMPTS) == synced
    assert cp.sync(synced, {k: v for k, v in PROMPTS.items() if k != "prompt-03.md"}) == synced


def test_sync_rejects_bad_titles():
    with pytest.raises(ValueError, match="prompt-04.md"):
        cp.sync(MASTER, {"prompt-04.md": "PROMPT 4 without a title\n"})
    with pytest.raises(ValueError, match="twice"):
        cp.sync(MASTER + "\n## PROMPT 1 — One again\n", PROMPTS)
