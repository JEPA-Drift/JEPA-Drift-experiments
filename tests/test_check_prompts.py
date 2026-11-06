"""Tests of tools/check_prompts.py (streams 8b and 31) on synthetic masters and on the repository's 33 prompts."""
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


LEGACY = ("# Prompts\n\n````markdown\n## PROMPT 1 — One\n\nbody 1\n````\n\n"
          "## PROMPT 2 — Two\n\nbody 2\n```bash\nmake\n```\n")
LEGACY_PROMPTS = {"prompt-01.md": "## PROMPT 1 — One\n\nbody 1\n",
                  "prompt-02.md": "## PROMPT 2 — Two\n\nbody 2\n```bash\nmake\n```\n",
                  "31_STREAM_PCA_DRIFT_X.md": "## PROMPT 31 — X\n\nbody x\n"}
PCA = {"28-PCA": "28_STREAM_PCA_DRIFT_RUNNER.md", "29": "29_STREAM_PCA_DRIFT_TABLES.md",
       "30": "30_STREAM_PCA_DRIFT_FIGURES.md", "31": "31_STREAM_PCA_DRIFT_CONTRACTS.md"}


def _repo_prompts():
    return {p.name: p.read_bytes().decode("utf-8")
            for pattern in ("prompt-*.md", "[0-9][0-9]_STREAM_PCA_DRIFT_*.md")
            for p in sorted(cp.STREAMS.glob(pattern))}


def test_cli_discovers_the_33_expected_ids():
    prompts = cp.discover(cp.STREAMS)
    ids = cp.prompt_ids(prompts)
    assert prompts == _repo_prompts() and len(prompts) == 33
    assert set(ids) == cp.EXPECTED_IDS and sum(name.startswith("prompt-") for name in prompts) == 29
    assert ids["28"] == "prompt-28-e11.md" and {pid: ids[pid] for pid in PCA} == PCA
    assert not {"01_STREAM_14_REWRITE_BOTTLENECK.md", "07_STREAM_22_E5_J4_REWRITE.md"} & set(prompts)
    cp.require_expected(ids, cp.EXPECTED_IDS)


def test_duplicate_unexpected_or_missing_titles_rejected():
    dup = {**PROMPTS, "prompt-02b.md": "## PROMPT 2 — Two again\n"}
    with pytest.raises(ValueError, match=r"prompt-02\.md and prompt-02b\.md"):
        cp.prompt_ids(dup)
    with pytest.raises(ValueError, match=r"prompt-02\.md and prompt-02b\.md"):
        cp.sync(MASTER, dup)
    with pytest.raises(ValueError, match="prompt-04.md"):
        cp.prompt_ids({"prompt-04.md": "PROMPT 4 without a title\n"})
    with pytest.raises(ValueError, match=r"missing \['3'\], unexpected \['4'\]"):
        cp.require_expected({"1": "a", "2": "b", "4": "c"}, {"1", "2", "3"})


def test_sync_idempotent_after_an_unfenced_legacy_tail():
    once = cp.sync(LEGACY, LEGACY_PROMPTS)
    assert once.startswith(LEGACY) and once.endswith("\n````markdown\n## PROMPT 31 — X\n\nbody x\n````\n")
    again = cp.sync(once, LEGACY_PROMPTS)
    assert len(again) == len(once) and again == once
    assert cp.check(once, LEGACY_PROMPTS) == [] and cp.fences_balanced(once)


def test_real_master_sync_append_only_idempotent_history_unchanged():
    master, prompts = cp.MASTER.read_bytes().decode("utf-8"), _repo_prompts()
    pids = {name: cp.TITLE.match(text).group(1) for name, text in prompts.items()}
    history = [name for name in prompts if name.startswith("prompt-")]
    spans = cp.blocks(master)
    assert len(history) == 29
    assert all(master[slice(*spans[pids[name]])] == prompts[name].rstrip("\n") for name in history)
    once = cp.sync(master, prompts)
    again = cp.sync(once, prompts)
    assert once.startswith(master) and len(again) == len(once) and again == once
    after = cp.blocks(once)
    assert all(once[slice(*after[pids[name]])] == master[slice(*spans[pids[name]])] for name in history)
    assert set(after) == cp.EXPECTED_IDS and cp.check(once, prompts) == [] and cp.fences_balanced(once)


def test_check_fails_on_modified_truncated_missing_or_incomplete():
    prompts = cp.discover(cp.STREAMS)
    once = cp.sync(cp.read_exact(cp.MASTER), prompts)
    name = PCA["31"]
    text = prompts[name]
    short = text[:text.rstrip("\n").rfind("\n") + 1]
    assert cp.check(once, {**prompts, name: text.replace("Codex", "Codex!", 1)}) == [name]
    assert short in once and cp.check(once, {**prompts, name: short}) == [name]
    with pytest.raises(ValueError, match=r"missing \['31'\], unexpected \[\]"):
        cp.require_expected(cp.prompt_ids({n: t for n, t in prompts.items() if n != name}), cp.EXPECTED_IDS)
    assert once.endswith("\n````\n")
    cut = once[:-len("````\n")]
    assert cp.check(cut, prompts) == [] and not cp.fences_balanced(cut)
    head = once[:cp.blocks(once)["8b"][1] - 10]
    assert "prompt-08b-hygiene.md" in cp.check(head, prompts)


def test_no_hidden_line_ending_normalization(tmp_path, monkeypatch, capsys):
    (tmp_path / "prompt-01.md").write_bytes("## PROMPT 1 — One\r\n\r\nbody 1\r\n".encode("utf-8"))
    master = tmp_path / "master.md"
    master.write_bytes("# M\n\n````markdown\n## PROMPT 1 — One\n\nbody 1\n````\n".encode("utf-8"))
    prompts = cp.discover(tmp_path)
    assert prompts["prompt-01.md"].endswith("body 1\r\n")
    assert cp.check(cp.read_exact(master), prompts) == ["prompt-01.md"]
    monkeypatch.setattr(cp, "STREAMS", tmp_path)
    monkeypatch.setattr(cp, "MASTER", master)
    monkeypatch.setattr(cp, "EXPECTED_IDS", frozenset({"1"}))
    assert cp.main([]) == 1
    assert cp.main(["--sync-master"]) == 0
    assert "## PROMPT 1 — One\r\n\r\nbody 1\r\n````\n".encode("utf-8") in master.read_bytes()
    assert "prompts-check: 1/1 " in capsys.readouterr().out


def test_main_reports_counts_exit_codes_and_writes_nothing_on_refusal(tmp_path, monkeypatch, capsys):
    streams, master = tmp_path / "streams", tmp_path / "master.md"
    streams.mkdir()
    for name, text in {**PROMPTS, "31_STREAM_PCA_DRIFT_X.md": "## PROMPT 31 — X\n\nbody x\n",
                       "01_STREAM_14_REWRITE_X.md": "## PROMPT 14 — not a stream prompt\n"}.items():
        (streams / name).write_bytes(text.encode("utf-8"))
    master.write_bytes(MASTER.encode("utf-8"))
    monkeypatch.setattr(cp, "STREAMS", streams)
    monkeypatch.setattr(cp, "MASTER", master)
    monkeypatch.setattr(cp, "EXPECTED_IDS", frozenset({"1", "2", "3", "31"}))
    assert cp.main([]) == 1
    out = capsys.readouterr().out
    assert "prompts-check: 1/4 (3 prompt-*.md + 1 [0-9][0-9]_STREAM_PCA_DRIFT_*.md: 31)" in out
    assert "not in the master: prompt-03.md" in out and master.read_bytes() == MASTER.encode("utf-8")
    assert cp.main(["--sync-master"]) == 0
    out = capsys.readouterr().out
    assert "sync-master: master rewritten" in out and "prompts-check: 4/4 " in out
    synced = master.read_bytes()
    assert cp.main(["--sync-master"]) == 0 and "sync-master: master unchanged" in capsys.readouterr().out
    master.write_bytes(synced[:-len("````\n")])
    assert cp.main([]) == 1
    out = capsys.readouterr().out
    assert "prompts-check: error: unbalanced ````markdown fences" in out and "4/4" not in out
    assert cp.main(["--sync-master"]) == 1 and master.read_bytes() == synced[:-len("````\n")]
    assert "4/4" not in capsys.readouterr().out
    master.write_bytes(synced)
    (streams / "32_STREAM_PCA_DRIFT_Y.md").write_bytes("## PROMPT 32 — Y\n".encode("utf-8"))
    assert cp.main(["--sync-master"]) == 1 and "unexpected ['32']" in capsys.readouterr().out
    (streams / "32_STREAM_PCA_DRIFT_Y.md").unlink()
    (streams / "31_STREAM_PCA_DRIFT_X.md").unlink()
    assert cp.main([]) == 1 and "missing ['31']" in capsys.readouterr().out
    assert master.read_bytes() == synced
