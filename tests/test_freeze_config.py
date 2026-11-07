"""Tests of tools/freeze_config.py (lot 21-F) on synthetic temporary Git repositories only, never on the project."""
import ast
import errno
import hashlib
import importlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "freeze_config.py"
SCHEMA, FROZEN = "jepadrift-freeze/1", "configs/FROZEN.json"
APPROVAL = "prompts/GO-fixture-synthetic.md"
ROOTS = ("Makefile", "conda-torch.lock", "configs", "conftest.py", "data/derived/MANIFEST.json",
         "docs/manifests/d4_manifest.json", "experiments", "jepadrift", "requirements.lock", "requirements.txt",
         "tools/freeze_config.py")
FILES = {
    "Makefile": b"fixture:\n\t@true\n",
    "conda-torch.lock": b"synthetic-fixture-lock==0\n",
    "configs/a.yaml": b"alpha: 1\n",
    "configs/raw.yaml": b"{unclosed: [\n",
    "configs/sub/b.yaml": b"beta: 2\n",
    "conftest.py": b"",
    "data/derived/MANIFEST.json": b'{"synthetic_fixture": true}\n',
    "docs/manifests/d4_manifest.json": b'{"synthetic_fixture": true}\n',
    "experiments/e.py": b"VALUE = 1\n",
    "jepadrift/__init__.py": b"",
    "jepadrift/pkg/m.py": b"VALUE = 2\n",
    "requirements.lock": b"synthetic-fixture==0\n",
    "requirements.txt": b"synthetic-fixture\n",
    "tools/freeze_config.py": b"PLACEHOLDER = 'synthetic fixture, not the tool'\n",
}
FREE = {
    ".gitignore": b"__pycache__/\nignored.bin\n",
    APPROVAL: b"Synthetic fixture text for tests/test_freeze_config.py; not a GO, not an approval, no decision.\n",
    "data/derived/d0/panel.bin": b"synthetic\n",
    "docs/note.md": b"note\n",
    "paper/p.tex": b"x\n",
    "results/r.csv": b"a\n1\n",
    "tests/t.txt": b"t\n",
}
PYC = "jepadrift/__pycache__/m.cpython-312.pyc"


def _git(repo, *args, date=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(HOME=str(Path(repo).parent), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Fixture Synthetic", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Fixture Synthetic", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    if date is not None:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    result = subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, f"git {args[0]}: {result.stderr}"
    return result.stdout.strip()


def _write(root, files):
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)


def _date(repo):
    return f"{978307200 + 60 * int(_git(repo, 'rev-list', '--all', '--count'))} +0000"


def _commit(repo, message, *paths, add=True):
    if add:
        _git(repo, "add", "-A", "--", *paths) if paths else _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, date=_date(repo))


def _build(repo, message="C"):
    _write(repo, {**FILES, **FREE})
    _git(repo, "init", "-q", "-b", "main")
    _commit(repo, message)
    _write(repo, {PYC: b"\x00synthetic cache, ignored\n"})
    return repo


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _canon(record):
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
            + "\n").encode("ascii")


def _record(repo, files=None):
    return {"schema": SCHEMA, "commit": _git(repo, "rev-parse", "HEAD"),
            "files": {rel: _sha(data) for rel, data in (FILES if files is None else files).items()},
            "approval": {"path": APPROVAL, "sha256": _sha((repo / APPROVAL).read_bytes())}}


def _seal(repo, data):
    (repo / FROZEN).write_bytes(data)
    _commit(repo, "S", FROZEN)


def _copy(src, dst):
    shutil.copytree(src, dst, symlinks=True)
    return dst


@pytest.fixture(scope="module")
def templates(tmp_path_factory):
    base = tmp_path_factory.mktemp("freeze")
    unsealed = _build(base / "c" / "repo")
    sealed = _copy(unsealed, base / "s" / "repo")
    _seal(sealed, _canon(_record(sealed)))
    return unsealed, sealed


@pytest.fixture
def repo_c(templates, tmp_path):
    return _copy(templates[0], tmp_path / "repo")


@pytest.fixture
def repo_s(templates, tmp_path):
    return _copy(templates[1], tmp_path / "repo")


def _fc():
    return importlib.import_module("tools.freeze_config")


def _code(repo):
    fc = _fc()
    try:
        fc.check(repo)
    except fc.FreezeError as exc:
        return exc.code
    return "OK"


def _write_code(repo, approval=APPROVAL):
    fc = _fc()
    try:
        fc.write(repo, approval)
    except fc.FreezeError as exc:
        return exc.code
    return "OK"


def _cli(*args):
    result = subprocess.run([sys.executable, "-I", "-B", str(TOOL), *args], capture_output=True, text=True,
                            timeout=120)
    return result.returncode, result.stdout, result.stderr


def _flip(path, index=0):
    data = bytearray(path.read_bytes())
    data[index] ^= 0x01
    path.write_bytes(bytes(data))


def _hexflip(digest):
    return ("1" if digest[0] == "0" else "0") + digest[1:]


def _drop(repo, rel):
    path = repo / rel
    shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()


def _move_and_link(repo, rel, keep):
    (repo / keep).parent.mkdir(parents=True, exist_ok=True)
    os.rename(repo / rel, repo / keep)
    os.symlink(os.path.relpath(repo / keep, (repo / rel).parent), repo / rel)


def _snapshot(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(dirnames + filenames):
            path = Path(dirpath) / name
            info = path.lstat()
            digest = _sha(path.read_bytes()) if stat.S_ISREG(info.st_mode) else ""
            found.append((str(path.relative_to(root)), info.st_mode, info.st_size, info.st_mtime_ns, digest))
    return found


def _no_git(*args, **kwargs):
    raise AssertionError("git must not run before this refusal")


def test_fixture_is_built_by_git_and_the_oracle_without_the_tool(repo_s):
    seal, commit = _git(repo_s, "rev-list", "-n", "1", "--parents", "HEAD").split()
    assert _git(repo_s, "diff-tree", "-r", "--name-status", commit, seal) == f"A\t{FROZEN}"
    raw = (repo_s / FROZEN).read_bytes()
    record = json.loads(raw)
    assert raw == _canon(record) and record["commit"] == commit and record["schema"] == SCHEMA
    assert record["files"] == {rel: _sha(data) for rel, data in FILES.items()}
    assert record["approval"] == {"path": APPROVAL, "sha256": _sha(FREE[APPROVAL])}


def test_cli_check_accepts_the_sealed_fixture(repo_s):
    seal, commit = _git(repo_s, "rev-list", "-n", "1", "--parents", "HEAD").split()
    rc, out, err = _cli("--check", "--root", str(repo_s))
    assert rc == 0, out + err
    freeze_id = _sha((repo_s / FROZEN).read_bytes())
    assert out.splitlines()[0] == (f"freeze-config: OK commit {commit} seal {seal} approval {APPROVAL} files 14 "
                                   f"freeze_id {freeze_id}")


def test_cli_check_refuses_a_one_byte_change(repo_s):
    _flip(repo_s / "configs/a.yaml")
    rc, out, err = _cli("--check", "--root", str(repo_s))
    assert rc == 1 and out.startswith("freeze-config: error: HASH: "), out + err


def test_cli_check_reports_an_absent_freeze(repo_c):
    rc, out, err = _cli("--check", "--root", str(repo_c))
    assert rc == 1 and out.startswith("freeze-config: error: ABSENT: "), out + err


def test_cli_write_creates_the_oracle_bytes(repo_c):
    expected = _canon(_record(repo_c))
    rc, out, err = _cli("--write", "--approval", APPROVAL, "--root", str(repo_c))
    assert rc == 0, out + err
    assert (repo_c / FROZEN).read_bytes() == expected


def test_write_seal_then_check_round_trip(repo_c, capsys):
    fc = _fc()
    expected = _canon(_record(repo_c))
    commit = _git(repo_c, "rev-parse", "HEAD")
    assert fc.write(repo_c, APPROVAL) == {"path": FROZEN, "sha256": _sha(expected), "commit": commit, "files": 14}
    assert (repo_c / FROZEN).read_bytes() == expected
    _commit(repo_c, "S", FROZEN)
    seal = _git(repo_c, "rev-parse", "HEAD")
    assert fc.check(repo_c) == {"commit": commit, "seal": seal, "approval": APPROVAL, "files": 14,
                                "freeze_id": _sha(expected)}
    assert fc.main(["--check", "--root", str(repo_c)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == (f"freeze-config: OK commit {commit} seal {seal} approval {APPROVAL} files 14 "
                        f"freeze_id {_sha(expected)}")
    assert len(lines) == 2 and lines[1].startswith("freeze-config: ") and "authorizes no run" in lines[1]
    assert str(repo_c) not in "\n".join(lines)


def test_write_cli_lines(repo_c, capsys):
    fc = _fc()
    expected = _canon(_record(repo_c))
    commit = _git(repo_c, "rev-parse", "HEAD")
    assert fc.main(["--write", "--approval", APPROVAL, "--root", str(repo_c)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[:2] == [f"freeze-config: wrote {FROZEN} sha256 {_sha(expected)} commit {commit} files 14",
                         f"freeze-config: not committed; seal with one commit whose only parent is {commit} and "
                         f"whose only change adds {FROZEN}"]
    assert len(lines) == 3 and "does not interpret the approval document" in lines[2]
    assert str(repo_c) not in "\n".join(lines)


def test_check_writes_nothing_and_repeats_its_output(repo_s, capsys):
    fc = _fc()
    before = _snapshot(repo_s)
    assert fc.main(["--check", "--root", str(repo_s)]) == 0
    first = capsys.readouterr().out
    assert fc.main(["--check", "--root", str(repo_s)]) == 0
    assert capsys.readouterr().out == first
    assert _snapshot(repo_s) == before


def test_two_independent_fixtures_freeze_identically(tmp_path):
    fc = _fc()
    one, two = _build(tmp_path / "one" / "repo"), _build(tmp_path / "two" / "repo")
    assert _git(one, "rev-parse", "HEAD") == _git(two, "rev-parse", "HEAD")
    assert fc.write(one, APPROVAL) == fc.write(two, APPROVAL)
    assert (one / FROZEN).read_bytes() == (two / FROZEN).read_bytes()


@pytest.mark.parametrize("rel", ["docs/note.md", "results/r.csv", "paper/p.tex", "tests/t.txt", "prompts/other.md"])
def test_later_commits_outside_the_policy_are_accepted(repo_s, rel):
    (repo_s / rel).write_bytes(b"changed after the seal\n")
    _commit(repo_s, "free", rel)
    assert _code(repo_s) == "OK"


def test_amended_seal_message_is_accepted(repo_s):
    _git(repo_s, "commit", "--amend", "-q", "-m", "S amended", date=_date(repo_s))
    assert _code(repo_s) == "OK"


def test_cache_raw_yaml_and_data_files_are_not_frozen(repo_s, capsys):
    fc = _fc()
    assert (repo_s / PYC).exists()
    _write(repo_s, {"experiments/__pycache__/e.cpython-312.pyc": b"\x00",
                    "data/derived/d0/panel.bin": b"changed synthetic data\n"})
    assert fc.main(["--check", "--root", str(repo_s)]) == 0
    assert "verifies no data bytes against the manifests" in capsys.readouterr().out


def _unlink_frozen(repo):
    (repo / FROZEN).unlink()


def _flip_frozen_digit(repo):
    record = json.loads((repo / FROZEN).read_bytes())
    record["approval"]["sha256"] = _hexflip(record["approval"]["sha256"])
    (repo / FROZEN).write_bytes(_canon(record))


STATES = {"ok": lambda repo: None, "absent": _unlink_frozen, "hash": lambda repo: _flip(repo / "configs/a.yaml"),
          "seal": _flip_frozen_digit, "link": lambda repo: _move_and_link(repo, "configs/a.yaml", "docs/a.yaml")}


@pytest.mark.parametrize("state", sorted(STATES))
def test_cli_and_library_agree(repo_s, capsys, state):
    fc = _fc()
    STATES[state](repo_s)
    try:
        result, refusal = fc.check(repo_s), None
    except fc.FreezeError as exc:
        result, refusal = None, f"freeze-config: error: {exc}\n"
    rc = fc.main(["--check", "--root", str(repo_s)])
    out = capsys.readouterr().out
    assert rc == (1 if refusal else 0)
    if refusal:
        assert out == refusal and refusal.startswith(f"freeze-config: error: {state.upper()}: ")
    else:
        assert out.startswith(f"freeze-config: OK commit {result['commit']} seal {result['seal']} approval "
                              f"{result['approval']} files {result['files']} freeze_id {result['freeze_id']}\n")
    assert _cli("--check", "--root", str(repo_s))[:2] == (rc, out)


def test_protected_path_traps_are_never_walked(repo_s):
    for rel in ("data/raw/eurofidai/trap", "data/derived/d4_eurofidai/trap"):
        (repo_s / rel).parent.mkdir(parents=True)
        os.mkfifo(repo_s / rel)
    rc, out, err = _cli("--check", "--root", str(repo_s))
    assert rc == 0, out + err


@pytest.mark.parametrize("rel", ["configs/a.yaml", "jepadrift/pkg/m.py", "Makefile", "data/derived/MANIFEST.json",
                                 "tools/freeze_config.py"])
def test_one_byte_change_on_disk_is_refused_then_restored(repo_s, rel):
    original = (repo_s / rel).read_bytes()
    _flip(repo_s / rel)
    assert _code(repo_s) == "HASH"
    (repo_s / rel).write_bytes(original)
    assert _code(repo_s) == "OK"


@pytest.mark.parametrize("rel", ["configs/a.yaml", "experiments/e.py"])
def test_committed_change_after_the_seal_stays_refused_after_a_revert(repo_s, rel):
    original = (repo_s / rel).read_bytes()
    _flip(repo_s / rel)
    _commit(repo_s, "change", rel)
    assert _code(repo_s) == "CHANGED"
    (repo_s / rel).write_bytes(original)
    _commit(repo_s, "revert", rel)
    assert _code(repo_s) == "CHANGED"


@pytest.mark.parametrize("rel", ["configs/new.yaml", "jepadrift/pkg/new.py", "jepadrift/ignored.bin"])
def test_untracked_or_ignored_file_under_a_root_is_refused(repo_s, rel):
    (repo_s / rel).write_bytes(b"extra\n")
    assert _code(repo_s) == "COVERAGE"


def test_tracked_file_missing_on_disk_is_refused(repo_s):
    _drop(repo_s, "configs/sub/b.yaml")
    assert _code(repo_s) == "COVERAGE"


ENTRY_CASES = {"removed": {rel: data for rel, data in FILES.items() if rel != "configs/a.yaml"},
               "added": {**FILES, "configs/extra.yaml": b"extra\n"},
               "renamed": {("configs/a2.yaml" if rel == "configs/a.yaml" else rel): data
                           for rel, data in FILES.items()}}


@pytest.mark.parametrize("case", sorted(ENTRY_CASES))
def test_frozen_entries_must_equal_the_tree_of_c(repo_c, case):
    _seal(repo_c, _canon(_record(repo_c, ENTRY_CASES[case])))
    assert _code(repo_c) == "COVERAGE"


def test_coverage_refusal_cites_at_most_five_paths_in_total(repo_c):
    fc = _fc()
    record = _record(repo_c)
    missing, extra = sorted(record["files"])[:6], [f"configs/extra-{index}.yaml" for index in range(6)]
    for rel in missing:
        del record["files"][rel]
    record["files"].update({rel: "0" * 64 for rel in extra})
    _seal(repo_c, _canon(record))
    with pytest.raises(fc.FreezeError) as info:
        fc.check(repo_c)
    cited = sum(rel in info.value.detail for rel in missing + extra)
    assert info.value.code == "COVERAGE" and 1 <= cited <= 5
    assert "6 missing" in info.value.detail and "6 extra" in info.value.detail


def test_submodule_entry_in_c_is_refused(repo_c):
    _git(repo_c, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},jepadrift/lib")
    _commit(repo_c, "gitlink", add=False)
    _seal(repo_c, _canon(_record(repo_c)))
    assert _code(repo_c) == "COVERAGE"


def test_tracked_symlink_in_c_is_refused(repo_c):
    os.symlink("a.yaml", repo_c / "configs/link.yaml")
    _commit(repo_c, "link", "configs/link.yaml")
    _seal(repo_c, _canon(_record(repo_c)))
    assert _code(repo_c) == "LINK"


ROOT_CASES = ([f"absent:{root}" for root in ROOTS] + [f"cache-only:{root}" for root in ("configs", "experiments",
              "jepadrift")] + ["type:Makefile-directory", "type:experiments-file",
                               "untracked:data/derived/MANIFEST.json"])


@pytest.mark.parametrize("case", ROOT_CASES)
def test_write_requires_every_root_with_its_type(repo_c, case):
    kind, _, root = case.partition(":")
    if root == "Makefile-directory":
        _drop(repo_c, "Makefile")
        _write(repo_c, {"Makefile/x": b"x\n"})
    elif root == "experiments-file":
        _drop(repo_c, "experiments")
        _write(repo_c, {"experiments": b"x\n"})
    elif kind == "untracked":
        _git(repo_c, "rm", "-q", "--cached", root)
    else:
        _drop(repo_c, root)
        if kind == "cache-only":
            _write(repo_c, {f"{root}/__pycache__/x.cpython-312.pyc": b"\x00"})
    _commit(repo_c, case, add=kind != "untracked")
    assert _write_code(repo_c) == "COVERAGE"
    assert not os.path.lexists(repo_c / FROZEN)


@pytest.mark.parametrize("case", ["no-manifest", "manifest-untracked", "no-experiments", "makefile-tree"])
def test_check_requires_every_root_in_c(repo_c, case):
    files = dict(FILES)
    if case == "no-manifest":
        _drop(repo_c, "docs/manifests/d4_manifest.json")
        del files["docs/manifests/d4_manifest.json"]
    elif case == "manifest-untracked":
        _git(repo_c, "rm", "-q", "--cached", "docs/manifests/d4_manifest.json")
        del files["docs/manifests/d4_manifest.json"]
    elif case == "no-experiments":
        _drop(repo_c, "experiments")
        del files["experiments/e.py"]
    else:
        _drop(repo_c, "Makefile")
        _write(repo_c, {"Makefile/x": b"x\n"})
        del files["Makefile"]
    _commit(repo_c, case, add=case != "manifest-untracked")
    _seal(repo_c, _canon(_record(repo_c, files)))
    assert _code(repo_c) == "COVERAGE"


CACHES = {"jepadrift/__pycache__/tracked.cpython-312.pyc": b"synthetic tracked cache\n",
          "configs/sub/__pycache__/deep/tracked.pyc": b"synthetic nested tracked cache\n"}


def _track_caches(repo):
    _write(repo, CACHES)
    _git(repo, "add", "-f", "--", *CACHES)
    _commit(repo, "C with synthetic tracked caches", add=False)


def test_write_excludes_tracked_cache_directories(repo_c):
    _track_caches(repo_c)
    expected = _canon(_record(repo_c))
    assert _write_code(repo_c) == "OK"
    assert (repo_c / FROZEN).read_bytes() == expected


def test_check_excludes_tracked_cache_directories(repo_c):
    _track_caches(repo_c)
    _seal(repo_c, _canon(_record(repo_c)))
    assert _code(repo_c) == "OK"


def test_ordinary_file_named_pycache_stays_covered(repo_c):
    ordinary = b"ordinary file, not a cache directory\n"
    _write(repo_c, {"configs/__pycache__": ordinary})
    _commit(repo_c, "ordinary file named __pycache__", "configs/__pycache__")
    expected = _canon(_record(repo_c, {**FILES, "configs/__pycache__": ordinary}))
    assert _write_code(repo_c) == "OK"
    assert (repo_c / FROZEN).read_bytes() == expected


def test_symlink_named_pycache_is_refused(repo_s):
    os.symlink("sub", repo_s / "configs/__pycache__")
    assert _code(repo_s) == "LINK"


@pytest.mark.parametrize("operation", ["write", "check"])
def test_tracked_caches_cannot_satisfy_a_code_root(repo_c, operation):
    cache = "experiments/__pycache__/e.cpython-312.pyc"
    _drop(repo_c, "experiments")
    _write(repo_c, {cache: b"synthetic tracked cache\n"})
    _git(repo_c, "add", "-A")
    _git(repo_c, "add", "-f", "--", cache)
    _commit(repo_c, "experiments reduced to a tracked cache", add=False)
    if operation == "write":
        assert _write_code(repo_c) == "COVERAGE"
        assert not os.path.lexists(repo_c / FROZEN)
    else:
        _seal(repo_c, _canon(_record(repo_c, {rel: data for rel, data in FILES.items() if rel != "experiments/e.py"})))
        assert _code(repo_c) == "COVERAGE"


@pytest.mark.parametrize("case", ["manifest-deleted", "tool-deleted", "makefile-directory", "configs-file"])
def test_root_missing_or_retyped_on_disk_after_the_seal(repo_s, case):
    if case == "manifest-deleted":
        _drop(repo_s, "data/derived/MANIFEST.json")
    elif case == "tool-deleted":
        _drop(repo_s, "tools/freeze_config.py")
    elif case == "makefile-directory":
        _drop(repo_s, "Makefile")
        (repo_s / "Makefile").mkdir()
    else:
        os.rename(repo_s / "configs", repo_s / "docs/configs.moved")
        (repo_s / "configs").write_bytes(b"x\n")
    assert _code(repo_s) == "COVERAGE"


def test_root_removed_by_a_commit_after_the_seal(repo_s):
    _drop(repo_s, "requirements.txt")
    _commit(repo_s, "drop", "requirements.txt")
    assert _code(repo_s) == "CHANGED"


def _dump(record):
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _edit(record, change):
    record = json.loads(json.dumps(record))
    change(record)
    return _dump(record)


def _rename(record, new):
    record["files"][new] = record["files"].pop("Makefile")


BAD_PATHS = ["./Makefile", "configs//a.yaml", "/Makefile", "configs/../Makefile", "configs/sub/", "docs/note.md",
             "configs/FROZEN.json", "configs/a b.yaml", "configs"]
FORMAT_CASES = {
    "not-utf8": lambda r, t: t.encode().replace(b"Makefile", b"\xffakefile", 1),
    "invalid-json": lambda r, t: t[:-3].encode(),
    "bom": lambda r, t: b"\xef\xbb\xbf" + t.encode(),
    "duplicate-top-key": lambda r, t: t.replace("{", '{"schema":"jepadrift-freeze/1",', 1).encode(),
    "duplicate-file-key": lambda r, t: t.replace('"files":{', '"files":{"Makefile":"%s",' % r["files"]["Makefile"],
                                                 1).encode(),
    "nan": lambda r, t: t.replace('"jepadrift-freeze/1"', "NaN").encode(),
    "infinity": lambda r, t: t.replace('"jepadrift-freeze/1"', "Infinity").encode(),
    "minus-infinity": lambda r, t: t.replace('"jepadrift-freeze/1"', "-Infinity").encode(),
    "number": lambda r, t: t.replace('"jepadrift-freeze/1"', "1").encode(),
    "missing-key": lambda r, t: _edit(r, lambda x: x.pop("approval")),
    "extra-key": lambda r, t: _edit(r, lambda x: x.update(extra="x")),
    "approval-missing-key": lambda r, t: _edit(r, lambda x: x["approval"].pop("sha256")),
    "approval-extra-key": lambda r, t: _edit(r, lambda x: x["approval"].update(extra="x")),
    "files-list": lambda r, t: _edit(r, lambda x: x.update(files=sorted(x["files"]))),
    "commit-int": lambda r, t: _edit(r, lambda x: x.update(commit=123)),
    "approval-path-bool": lambda r, t: _edit(r, lambda x: x["approval"].update(path=True)),
    "schema-null": lambda r, t: _edit(r, lambda x: x.update(schema=None)),
    "commit-upper": lambda r, t: _edit(r, lambda x: x.update(commit=x["commit"].upper())),
    "commit-39": lambda r, t: _edit(r, lambda x: x.update(commit=x["commit"][:-1])),
    "commit-41": lambda r, t: _edit(r, lambda x: x.update(commit=x["commit"] + "0")),
    "commit-non-hex": lambda r, t: _edit(r, lambda x: x.update(commit="g" + x["commit"][1:])),
    "file-digest-upper": lambda r, t: _edit(r, lambda x: x["files"].update(Makefile=x["files"]["Makefile"].upper())),
    "schema-unknown": lambda r, t: _edit(r, lambda x: x.update(schema="jepadrift-freeze/2")),
    **{f"path:{bad}": (lambda bad: lambda r, t: _edit(r, lambda x: _rename(x, bad)))(bad) for bad in BAD_PATHS},
    "approval-off-pattern": lambda r, t: _edit(r, lambda x: x["approval"].update(path="docs/GO-x.md")),
    "indented": lambda r, t: (json.dumps(r, sort_keys=True, indent=1) + "\n").encode(),
    "unsorted": lambda r, t: (json.dumps(dict(reversed(list(r.items()))), separators=(",", ":")) + "\n").encode(),
    "no-final-newline": lambda r, t: t.rstrip("\n").encode(),
    "two-final-newlines": lambda r, t: (t + "\n").encode(),
    "unicode-escape": lambda r, t: t.replace("configs/a.yaml", "configs/\\u0061.yaml").encode(),
    "too-large": lambda r, t: t.encode() + b" " * (1 << 20),
    "deep-nesting": lambda r, t: b"[" * 200000 + b"]" * 200000,
    "empty-files": lambda r, t: _edit(r, lambda x: x.update(files={})),
}


@pytest.mark.parametrize("case", sorted(FORMAT_CASES))
def test_malformed_frozen_is_refused(repo_c, case):
    record = _record(repo_c)
    (repo_c / FROZEN).write_bytes(FORMAT_CASES[case](record, _canon(record).decode("ascii")))
    assert _code(repo_c) == "FORMAT"


LINK_CASES = {"frozen": (FROZEN, "docs/FROZEN.copy"), "configs-directory": ("configs", "configs.real"),
              "frozen-file": ("configs/a.yaml", "docs/a.yaml"), "frozen-subdirectory": ("jepadrift/pkg", "docs/pkg"),
              "data-derived": ("data/derived", "data/derived.real"), "prompts-directory": ("prompts", "prompts.real"),
              "approval": (APPROVAL, "docs/GO.copy")}


@pytest.mark.parametrize("case", sorted(LINK_CASES))
def test_symlink_at_any_component_is_refused(repo_s, case):
    _move_and_link(repo_s, *LINK_CASES[case])
    assert _code(repo_s) == "LINK"


def test_dangling_symlink_under_a_root_is_refused(repo_s):
    os.symlink("nowhere", repo_s / "configs/dangling.yaml")
    assert _code(repo_s) == "LINK"


def test_fifo_under_a_root_is_refused_without_blocking(repo_s):
    os.mkfifo(repo_s / "configs/pipe")
    rc, out, err = _cli("--check", "--root", str(repo_s))
    assert rc == 1 and out.startswith("freeze-config: error: LINK: "), out + err


RACES = {"file-to-link": ("m.py", "jepadrift/pkg/m.py", "docs/m.moved"),
         "directory-to-link": ("pkg", "jepadrift/pkg", "docs/pkg.moved"),
         "file-to-fifo": ("e.py", "experiments/e.py", None)}


@pytest.mark.parametrize("case", sorted(RACES))
def test_substitution_between_listing_and_open_is_refused(repo_s, monkeypatch, case):
    name, rel, keep = RACES[case]
    real_open, swapped = os.open, []

    def racing_open(path, flags, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) == name and not swapped:
            swapped.append(rel)
            if keep:
                _move_and_link(repo_s, rel, keep)
            else:
                (repo_s / rel).unlink()
                os.mkfifo(repo_s / rel)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", racing_open)
    assert _code(repo_s) == "LINK"
    assert swapped == [rel]


def test_frozen_not_committed_is_refused(repo_c):
    (repo_c / FROZEN).write_bytes(_canon(_record(repo_c)))
    assert _code(repo_c) == "SEAL"


def test_seal_adding_another_file_is_refused(repo_c):
    (repo_c / FROZEN).write_bytes(_canon(_record(repo_c)))
    (repo_c / "docs/note.md").write_bytes(b"also in the seal\n")
    _commit(repo_c, "S", FROZEN, "docs/note.md")
    assert _code(repo_c) == "SEAL"


def test_commit_between_c_and_the_seal_is_refused(repo_c):
    data = _canon(_record(repo_c))
    (repo_c / "docs/note.md").write_bytes(b"between C and S\n")
    _commit(repo_c, "between", "docs/note.md")
    _seal(repo_c, data)
    assert _code(repo_c) == "SEAL"


def test_frozen_changed_after_the_seal_is_refused(repo_s):
    _flip_frozen_digit(repo_s)
    _commit(repo_s, "edit", FROZEN)
    assert _code(repo_s) == "SEAL"


def test_frozen_deleted_then_re_added_is_refused(repo_s):
    data = (repo_s / FROZEN).read_bytes()
    _drop(repo_s, FROZEN)
    _commit(repo_s, "delete", FROZEN)
    (repo_s / FROZEN).write_bytes(data)
    _commit(repo_s, "re-add", FROZEN)
    assert _code(repo_s) == "SEAL"


def test_a_lineage_frozen_before_c_cannot_be_sealed_again(repo_c):
    (repo_c / FROZEN).write_bytes(b"{}\n")
    _commit(repo_c, "earlier freeze", FROZEN)
    _drop(repo_c, FROZEN)
    _commit(repo_c, "earlier freeze removed", FROZEN)
    _seal(repo_c, _canon(_record(repo_c)))
    assert _code(repo_c) == "SEAL"


def test_merge_after_c_is_refused(repo_s):
    _git(repo_s, "checkout", "-q", "-b", "side")
    (repo_s / "docs/side.md").write_bytes(b"side\n")
    _commit(repo_s, "side", "docs/side.md")
    _git(repo_s, "checkout", "-q", "main")
    (repo_s / "docs/main.md").write_bytes(b"main\n")
    _commit(repo_s, "main", "docs/main.md")
    _git(repo_s, "merge", "-q", "--no-ff", "-m", "merge", "side", date=_date(repo_s))
    assert _code(repo_s) == "SEAL"


def test_commit_absent_from_the_repository_is_refused(templates, tmp_path):
    other = _build(tmp_path / "other" / "repo", message="another C")
    _seal(other, (templates[1] / FROZEN).read_bytes())
    assert _code(other) == "SEAL"


def test_commit_field_naming_a_tree_is_refused(repo_c):
    record = _record(repo_c)
    record["commit"] = _git(repo_c, "rev-parse", "HEAD^{tree}")
    _seal(repo_c, _canon(record))
    assert _code(repo_c) == "SEAL"


def test_identical_content_on_an_orphan_branch_is_refused(repo_s):
    _git(repo_s, "checkout", "-q", "--orphan", "alt")
    _commit(repo_s, "orphan copy")
    assert _code(repo_s) == "SEAL"


def test_disk_frozen_differing_from_the_seal_is_refused(repo_s):
    _flip_frozen_digit(repo_s)
    assert _code(repo_s) == "SEAL"


def test_executable_frozen_in_the_seal_is_refused(repo_c):
    (repo_c / FROZEN).write_bytes(_canon(_record(repo_c)))
    os.chmod(repo_c / FROZEN, 0o755)
    _commit(repo_c, "S", FROZEN)
    assert _code(repo_c) == "SEAL"


def test_branch_back_at_c_has_no_freeze(repo_s):
    _git(repo_s, "checkout", "-q", "HEAD~1")
    assert not (repo_s / FROZEN).exists()
    assert _code(repo_s) == "ABSENT"


@pytest.mark.parametrize("name", ["GIT_DIR", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY", "GIT_INDEX_FILE",
                                  "GIT_CONFIG_PARAMETERS", "GIT_NAMESPACE"])
def test_inherited_git_environment_is_ignored(templates, repo_s, tmp_path, monkeypatch, name):
    fc = _fc()
    other = _copy(templates[0], tmp_path / "other")
    expected = fc.check(repo_s)
    values = {"GIT_DIR": other / ".git", "GIT_WORK_TREE": other, "GIT_OBJECT_DIRECTORY": other / ".git" / "objects",
              "GIT_INDEX_FILE": other / ".git" / "index", "GIT_CONFIG_PARAMETERS": "'core.bare'='true'",
              "GIT_NAMESPACE": "other"}
    monkeypatch.setenv(name, str(values[name]))
    assert fc.check(repo_s) == expected
    _flip(repo_s / "configs/a.yaml")
    assert _code(repo_s) == "HASH"


def test_replace_refs_cannot_hide_a_change(repo_s):
    seal = _git(repo_s, "rev-parse", "HEAD")
    original = (repo_s / "configs/a.yaml").read_bytes()
    _flip(repo_s / "configs/a.yaml")
    _commit(repo_s, "change", "configs/a.yaml")
    _git(repo_s, "replace", _git(repo_s, "rev-parse", "HEAD"), seal)
    (repo_s / "configs/a.yaml").write_bytes(original)
    assert _code(repo_s) == "CHANGED"


def test_grafts_file_is_refused(repo_s):
    (repo_s / ".git" / "info").mkdir(exist_ok=True)
    (repo_s / ".git" / "info" / "grafts").write_text(_git(repo_s, "rev-parse", "HEAD") + "\n")
    assert _code(repo_s) == "ROOT"


def test_shallow_clone_is_refused(repo_s, tmp_path):
    clone = tmp_path / "shallow"
    _git(tmp_path, "clone", "-q", "--depth", "1", repo_s.as_uri(), str(clone))
    assert _code(clone) == "ROOT"


def test_missing_git_binary_is_an_infrastructure_refusal(repo_s, tmp_path, monkeypatch):
    (tmp_path / "empty").mkdir()
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    assert _code(repo_s) == "GIT"


def test_git_timeout_is_an_infrastructure_refusal(repo_s, monkeypatch):
    monkeypatch.setattr(_fc(), "GIT_TIMEOUT", 1e-9)
    assert _code(repo_s) == "GIT"


def test_unreadable_frozen_file_is_an_io_refusal(repo_s):
    path = repo_s / "configs/a.yaml"
    path.chmod(0)
    try:
        assert _code(repo_s) == "IO"
    finally:
        path.chmod(0o644)


@pytest.mark.parametrize("approval", ["docs/GO-x.md", "prompts/sub/GO-x.md", "prompts/GO-x.txt", "prompts/go-x.md",
                                      "prompts/GO-.md"])
def test_off_pattern_approval_is_refused_before_git(repo_c, monkeypatch, approval):
    _fc()
    monkeypatch.setattr(subprocess, "run", _no_git)
    assert _write_code(repo_c, approval) == "APPROVAL"
    assert not os.path.lexists(repo_c / FROZEN)


def test_write_refuses_an_untracked_approval(repo_c):
    (repo_c / "prompts/GO-untracked.md").write_bytes(b"synthetic, untracked\n")
    assert _write_code(repo_c, "prompts/GO-untracked.md") == "APPROVAL"
    assert not os.path.lexists(repo_c / FROZEN)


def test_write_refuses_an_approval_modified_on_disk(repo_c):
    _flip(repo_c / APPROVAL)
    assert _write_code(repo_c) == "APPROVAL"
    assert not os.path.lexists(repo_c / FROZEN)


def test_approval_absent_from_c_is_refused(repo_c):
    later, content = "prompts/GO-later.md", b"synthetic, committed after the seal\n"
    record = _record(repo_c)
    record["approval"] = {"path": later, "sha256": _sha(content)}
    _seal(repo_c, _canon(record))
    (repo_c / later).write_bytes(content)
    _commit(repo_c, "later", later)
    assert _code(repo_c) == "APPROVAL"


@pytest.mark.parametrize("case", ["committed", "disk", "deleted", "reverted"])
def test_approval_changed_after_the_seal_is_refused(repo_s, case):
    if case == "deleted":
        _drop(repo_s, APPROVAL)
    else:
        original = (repo_s / APPROVAL).read_bytes()
        _flip(repo_s / APPROVAL)
        if case in ("committed", "reverted"):
            _commit(repo_s, "approval edited", APPROVAL)
        if case == "reverted":
            (repo_s / APPROVAL).write_bytes(original)
            _commit(repo_s, "approval restored", APPROVAL)
    assert _code(repo_s) == "APPROVAL"


def test_wrong_approval_digest_is_refused(repo_c):
    record = _record(repo_c)
    record["approval"]["sha256"] = _hexflip(record["approval"]["sha256"])
    _seal(repo_c, _canon(record))
    assert _code(repo_c) == "APPROVAL"


@pytest.mark.parametrize("kind", ["file", "dangling-link", "link-to-outside-file"])
def test_write_never_replaces_an_existing_frozen(repo_c, tmp_path, kind):
    outside, absent = tmp_path / "outside.json", tmp_path / "absent.json"
    outside.write_bytes(b"outside\n")
    if kind == "file":
        (repo_c / FROZEN).write_bytes(b"kept\n")
    else:
        os.symlink(outside if kind == "link-to-outside-file" else absent, repo_c / FROZEN)
    assert _write_code(repo_c) == "EXISTS"
    assert outside.read_bytes() == b"outside\n" and not absent.exists()
    assert kind != "file" or (repo_c / FROZEN).read_bytes() == b"kept\n"


@pytest.mark.parametrize("case, code", [("untracked", "COVERAGE"), ("modified", "HASH"), ("missing", "COVERAGE")])
def test_write_refuses_a_dirty_policy(repo_c, case, code):
    if case == "untracked":
        (repo_c / "configs/new.yaml").write_bytes(b"new\n")
    elif case == "modified":
        _flip(repo_c / "configs/a.yaml")
    else:
        _drop(repo_c, "configs/sub/b.yaml")
    assert _write_code(repo_c) == code
    assert not os.path.lexists(repo_c / FROZEN)


def test_write_refuses_a_lineage_already_frozen(repo_c):
    (repo_c / FROZEN).write_bytes(b"{}\n")
    _commit(repo_c, "earlier freeze", FROZEN)
    _drop(repo_c, FROZEN)
    _commit(repo_c, "earlier freeze removed", FROZEN)
    assert _write_code(repo_c) == "SEAL"
    assert not os.path.lexists(repo_c / FROZEN)


def test_write_refuses_an_unborn_head(tmp_path):
    repo = tmp_path / "repo"
    _write(repo, {**FILES, **FREE})
    _git(repo, "init", "-q", "-b", "main")
    assert _write_code(repo) == "ROOT"
    assert not os.path.lexists(repo / FROZEN)


def test_write_outside_the_temporary_directory_is_refused_before_git(repo_c, tmp_path, monkeypatch):
    _fc()
    (tmp_path / "elsewhere").mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "elsewhere"))
    monkeypatch.setattr(subprocess, "run", _no_git)
    assert _write_code(repo_c) == "PROJECT"
    assert not os.path.lexists(repo_c / FROZEN)


def test_write_refuses_a_repository_holding_the_project_root_commit(repo_c, monkeypatch):
    monkeypatch.setattr(_fc(), "PROJECT_ROOT_COMMIT", _git(repo_c, "rev-list", "--max-parents=0", "HEAD"))
    assert _write_code(repo_c) == "PROJECT"
    assert not os.path.lexists(repo_c / FROZEN)


def test_fsync_failure_removes_the_created_file(repo_c, monkeypatch):
    before = sorted(os.listdir(repo_c / "configs"))

    def failing_fsync(fd):
        raise OSError(errno.EIO, "synthetic fsync failure")

    monkeypatch.setattr(os, "fsync", failing_fsync)
    assert _write_code(repo_c) == "IO"
    assert sorted(os.listdir(repo_c / "configs")) == before


def test_concurrent_creation_is_refused_without_touching_the_foreign_file(repo_c, monkeypatch):
    real_open, foreign = os.open, {}

    def racing_open(path, flags, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) == "FROZEN.json" and flags & os.O_CREAT and not foreign:
            fd = real_open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, dir_fd=kwargs.get("dir_fd"))
            os.write(fd, b"foreign\n")
            os.close(fd)
            foreign["inode"] = os.stat(repo_c / FROZEN).st_ino
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", racing_open)
    assert _write_code(repo_c) == "EXISTS"
    assert foreign and (repo_c / FROZEN).read_bytes() == b"foreign\n"
    assert os.stat(repo_c / FROZEN).st_ino == foreign["inode"]


def test_fsync_failure_after_a_name_substitution_removes_nothing(repo_c, monkeypatch):
    seen = {}

    def substituting_fsync(fd):
        spare = repo_c / "configs" / "foreign.tmp"
        spare.write_bytes(b"foreign\n")
        seen["inode"] = spare.stat().st_ino
        os.replace(spare, repo_c / FROZEN)
        raise OSError(errno.EIO, "synthetic fsync failure")

    monkeypatch.setattr(os, "fsync", substituting_fsync)
    assert _write_code(repo_c) == "IO"
    assert (repo_c / FROZEN).read_bytes() == b"foreign\n"
    assert (repo_c / FROZEN).stat().st_ino == seen["inode"]


@pytest.mark.parametrize("operation", ["check", "write", "main-check", "main-write"])
def test_root_descriptor_failure_is_a_closed_io_refusal(templates, tmp_path, monkeypatch, capsys, operation):
    fc = _fc()
    repo = _copy(templates[1] if operation.endswith("check") else templates[0], tmp_path / "repo")
    resolved, real_open = str(repo.resolve()), os.open

    def deny_root(path, *args, **kwargs):
        if os.fspath(path) == resolved:
            raise PermissionError(errno.EACCES, "synthetic root open refusal")
        return real_open(path, *args, **kwargs)

    before = _snapshot(repo)
    monkeypatch.setattr(os, "open", deny_root)
    if operation in ("check", "write"):
        with pytest.raises(fc.FreezeError) as info:
            fc.check(repo) if operation == "check" else fc.write(repo, APPROVAL)
        assert info.value.code == "IO" and resolved not in str(info.value)
    else:
        args = ["--check"] if operation == "main-check" else ["--write", "--approval", APPROVAL]
        assert fc.main([*args, "--root", str(repo)]) == 1
        out, err = capsys.readouterr()
        assert out.startswith("freeze-config: error: IO: ") and out.count("\n") == 1 and not err
        assert resolved not in out and str(repo) not in out
    monkeypatch.undo()
    assert _snapshot(repo) == before


@pytest.mark.parametrize("case", ["missing", "file", "plain-directory", "subdirectory", "bare"])
def test_invalid_root_is_refused(repo_s, tmp_path, case):
    root = {"missing": tmp_path / "missing", "file": tmp_path / "file", "plain-directory": tmp_path / "plain",
            "subdirectory": repo_s / "configs", "bare": tmp_path / "bare.git"}[case]
    if case == "file":
        root.write_bytes(b"x\n")
    elif case == "plain-directory":
        root.mkdir()
    elif case == "bare":
        _git(tmp_path, "init", "-q", "--bare", str(root))
    assert _code(root) == "ROOT"


def test_root_given_through_a_symlink_is_resolved(repo_s, tmp_path):
    fc = _fc()
    os.symlink(repo_s, tmp_path / "link")
    assert fc.check(tmp_path / "link") == fc.check(repo_s)


@pytest.mark.parametrize("args", [[], ["--check", "--write"], ["--check", "--approval", APPROVAL], ["--write"]])
def test_usage_errors_exit_2(args):
    rc, out, err = _cli(*args)
    assert rc == 2 and "usage: freeze_config.py" in err, out + err


def test_tool_imports_only_the_standard_library():
    tree = ast.parse(TOOL.read_text(encoding="utf-8"))
    modules = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
               for alias in node.names}
    modules |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert modules and modules <= sys.stdlib_module_names
