"""Freeze verifier of lot 21-F: byte identity of the policy files at a commit C, sealed by a later commit S.

`python tools/freeze_config.py --check [--root DIR]` verifies configs/FROZEN.json of the repository at DIR (default:
this repository) and changes nothing. `--write --approval prompts/GO-<id>.md [--root DIR]` creates FROZEN for HEAD = C,
only in a synthetic repository under the temporary directory; the seal S is then one commit whose only parent is C and
whose only change adds configs/FROZEN.json. FROZEN is canonical JSON {schema, commit, files, approval}: the SHA-256 of
every regular file under the eleven policy roots (all required with their type; __pycache__ directories excluded) and
the SHA-256 of a tracked approval document, recorded as provenance and never interpreted. A check refuses a symbolic
link at any component, a file untracked in or missing from the tree of C, a byte differing from FROZEN or from C, a
merge after C, a commit after S touching the policy, FROZEN or the approval, and any FROZEN in the history of C: the
schema serves once per lineage. Git runs without inherited GIT_* variables, global or system configuration and
replace objects; grafts and shallow repositories are refused. Exit 0 on success, 1 on a refusal printed as
`freeze-config: error: CODE: detail`, 2 on a usage error. A passing check reads no data file and authorizes no run.
"""
import argparse
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "jepadrift-freeze/1"
FROZEN = "configs/FROZEN.json"
POLICY = ("Makefile", "conda-torch.lock", "configs", "conftest.py", "data/derived/MANIFEST.json",
          "docs/manifests/d4_manifest.json", "experiments", "jepadrift", "requirements.lock", "requirements.txt",
          "tools/freeze_config.py")
APPROVAL = re.compile(r"prompts/GO-[A-Za-z0-9][A-Za-z0-9._-]*\.md")
PROJECT_ROOT_COMMIT = "32a55c8d6e16dc74f79f7cd17e61e5fb73d89332"
MAX_FROZEN_BYTES = 1048576
GIT_TIMEOUT = 60
CODES = ("ROOT", "GIT", "ABSENT", "LINK", "FORMAT", "SEAL", "CHANGED", "COVERAGE", "HASH", "APPROVAL", "EXISTS",
         "PROJECT", "IO")
CAVEAT = ("a passing check pins the bytes of the policy files at commit C and of the approval document; it reads no "
          "data file, verifies no data bytes against the manifests, does not interpret the approval document and "
          "authorizes no run")
_DIRECTORIES = ("configs", "experiments", "jepadrift")
_HEX40, _HEX64, _PART = re.compile(r"[0-9a-f]{40}"), re.compile(r"[0-9a-f]{64}"), re.compile(r"[A-Za-z0-9_.-]+")


class FreezeError(Exception):
    """Closed refusal: a code of CODES and a detail that never holds the absolute root path."""

    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail = code, detail


def _git(root, *args, ok=(0,), code="GIT"):
    """Completed plumbing command run in root without inherited GIT_* variables, global or system configuration."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_CEILING_DIRECTORIES=str(root.parent),
               GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0", GIT_LITERAL_PATHSPECS="1",
               GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    try:
        done = subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FreezeError("GIT", f"git {args[0]} did not complete ({type(exc).__name__})") from exc
    if done.returncode not in ok:
        raise FreezeError(code, f"git {args[0]} exited with status {done.returncode}")
    return done


def _root(root):
    """(resolved top level, HEAD) of a non-bare, non-shallow, graft-free work tree whose HEAD is a SHA-1 commit."""
    try:
        path = Path(root).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FreezeError("ROOT", f"--root does not resolve ({type(exc).__name__})") from exc
    if not path.is_dir():
        raise FreezeError("ROOT", "--root is not a directory")
    lines = _git(path, "rev-parse", "--is-bare-repository", "--is-shallow-repository", "--git-path", "info/grafts",
                 "--show-toplevel", code="ROOT").stdout.decode("utf-8", "surrogateescape").splitlines()
    if len(lines) != 4 or lines[0] != "false" or Path(lines[3]).resolve() != path:
        raise FreezeError("ROOT", "--root is not the top level of a Git work tree")
    if lines[1] != "false":
        raise FreezeError("ROOT", "shallow repository: the history is incomplete")
    if os.path.lexists(path / lines[2]):
        raise FreezeError("ROOT", "a grafts file rewrites the history")
    head = _git(path, "rev-parse", "--verify", "--quiet", "HEAD^{commit}", ok=(0, 1)).stdout.decode().strip()
    if not _HEX40.fullmatch(head):
        raise FreezeError("ROOT", "HEAD is not a SHA-1 commit")
    return path, head


def _open(dir_fd, name, rel, directory, missing, wrong):
    """(descriptor, fstat) of name in dir_fd without following any link: a link or a substitution is LINK."""
    try:
        before = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        raise FreezeError(missing, f"{rel} is absent") from None
    if stat.S_ISLNK(before.st_mode):
        raise FreezeError("LINK", f"{rel} is a symbolic link")
    if not (stat.S_ISDIR if directory else stat.S_ISREG)(before.st_mode):
        raise FreezeError(wrong, f"{rel} is not a {'directory' if directory else 'regular file'}")
    flags = os.O_RDONLY | os.O_NOFOLLOW | (os.O_DIRECTORY if directory else os.O_NONBLOCK)
    try:
        fd = os.open(name, flags, dir_fd=dir_fd)
    except OSError as exc:
        try:
            now = os.stat(name, dir_fd=dir_fd, follow_symlinks=False).st_mode
        except OSError:
            now = 0
        if stat.S_ISLNK(now):
            raise FreezeError("LINK", f"{rel} became a symbolic link") from exc
        if exc.errno in (errno.EACCES, errno.EPERM):
            raise FreezeError("IO", f"{rel} is not readable ({exc.strerror})") from exc
        raise FreezeError("LINK", f"{rel} changed during the check") from exc
    after = os.fstat(fd)
    if (after.st_dev, after.st_ino, stat.S_IFMT(after.st_mode)) != (before.st_dev, before.st_ino,
                                                                      stat.S_IFMT(before.st_mode)):
        os.close(fd)
        raise FreezeError("LINK", f"{rel} was substituted during the check")
    return fd, after


def _descend(root_fd, rel, directory, missing, wrong, last_wrong=None):
    """(descriptor, fstat) of rel below root_fd: real directories down to its last component, opened like _open."""
    parts, fd = rel.split("/"), root_fd
    try:
        for index, name in enumerate(parts[:-1]):
            sub, _ = _open(fd, name, "/".join(parts[:index + 1]), True, missing, wrong)
            if fd != root_fd:
                os.close(fd)
            fd = sub
        return _open(fd, parts[-1], rel, directory, missing, last_wrong or wrong)
    finally:
        if fd != root_fd:
            os.close(fd)


def _read_frozen(root_fd):
    """Bytes of configs/FROZEN.json, at most MAX_FROZEN_BYTES, read through descriptors that follow no link."""
    fd, info = _descend(root_fd, FROZEN, False, "ABSENT", "COVERAGE", "LINK")
    try:
        if info.st_size > MAX_FROZEN_BYTES:
            raise FreezeError("FORMAT", f"{FROZEN} exceeds {MAX_FROZEN_BYTES} bytes")
        chunks, total = [], 0
        while chunk := os.read(fd, MAX_FROZEN_BYTES + 1):
            chunks.append(chunk)
            total += len(chunk)
    finally:
        os.close(fd)
    if total != info.st_size:
        raise FreezeError("HASH", f"{FROZEN} changed while being read")
    return b"".join(chunks)


def _unique(pairs):
    """Object of a JSON pair list whose keys are distinct."""
    if len({key for key, _ in pairs}) != len(pairs):
        raise ValueError("duplicate key")
    return dict(pairs)


def _non_finite(name):
    """Refusal of NaN, Infinity and -Infinity."""
    raise ValueError(f"non-finite constant {name}")


def _canonical(record):
    """Canonical bytes: sorted keys, compact separators, ASCII, final newline."""
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
            + "\n").encode("ascii")


def _portable(rel):
    """Canonical relative POSIX path whose components are portable names other than . and .."""
    return all(_PART.fullmatch(part) and part not in (".", "..") for part in rel.split("/"))


def _in_policy(rel):
    """True for a covered path: a file root, or a portable path below a directory root, never FROZEN itself."""
    return rel != FROZEN and _portable(rel) and any(
        rel.startswith(f"{root}/") if root in _DIRECTORIES else rel == root for root in POLICY)


def _parse(raw):
    """FROZEN record after strict UTF-8 JSON, the exact schema and the canonical byte form."""
    try:
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_non_finite)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise FreezeError("FORMAT", f"{FROZEN} is not strict UTF-8 JSON ({type(exc).__name__})") from exc
    if not isinstance(record, dict) or set(record) != {"schema", "commit", "files", "approval"}:
        raise FreezeError("FORMAT", f"{FROZEN} keys must be exactly schema, commit, files and approval")
    files, approval = record["files"], record["approval"]
    if record["schema"] != SCHEMA or not isinstance(record["commit"], str) or not _HEX40.fullmatch(record["commit"]):
        raise FreezeError("FORMAT", f"{FROZEN} needs schema {SCHEMA} and a 40-digit lowercase commit")
    if not isinstance(files, dict) or not files or not all(
            _in_policy(rel) and isinstance(digest, str) and _HEX64.fullmatch(digest) for rel, digest in files.items()):
        raise FreezeError("FORMAT", f"{FROZEN} files must map covered policy paths to lowercase SHA-256 digests")
    if (not isinstance(approval, dict) or set(approval) != {"path", "sha256"} or not isinstance(approval["path"], str)
            or not APPROVAL.fullmatch(approval["path"]) or not isinstance(approval["sha256"], str)
            or not _HEX64.fullmatch(approval["sha256"])):
        raise FreezeError("FORMAT", f"{FROZEN} approval must be exactly a path matching {APPROVAL.pattern} and a "
                                    "lowercase SHA-256")
    if _canonical(record) != raw:
        raise FreezeError("FORMAT", f"{FROZEN} is not in canonical form")
    return record


def _hash(fd, size, rel):
    """(SHA-256, Git blob id) of exactly size bytes read from fd in 1 MiB blocks."""
    digest, blob, total = hashlib.sha256(), hashlib.sha1(b"blob %d\0" % size, usedforsecurity=False), 0
    while chunk := os.read(fd, 1 << 20):
        digest.update(chunk)
        blob.update(chunk)
        total += len(chunk)
    if total != size:
        raise FreezeError("HASH", f"{rel} changed while being read")
    return digest.hexdigest(), blob.hexdigest()


def _tree(root, commit, paths):
    """{path: (mode, blob id)} of commit under paths minus __pycache__ directories; links LINK, other modes COVERAGE."""
    entries = {}
    for item in _git(root, "ls-tree", "-r", "-z", commit, "--", *paths).stdout.split(b"\0")[:-1]:
        meta, _, name = item.partition(b"\t")
        mode, kind, oid = meta.decode().split(" ")
        rel = name.decode("utf-8", "surrogateescape")
        if "__pycache__" in rel.split("/")[:-1]:
            continue
        if mode == "120000":
            raise FreezeError("LINK", f"a tracked symbolic link lies under the policy in {commit[:12]}")
        if kind != "blob" or mode not in ("100644", "100755") or not _portable(rel):
            raise FreezeError("COVERAGE", f"a tracked entry of mode {mode} under the policy in {commit[:12]} is not "
                                          "a portable regular file")
        entries[rel] = (mode, oid)
    entries.pop(FROZEN, None)
    return entries


def _require_roots(entries, commit):
    """Every policy root in the tree of commit: file roots as files, directory roots holding a covered file."""
    for root in POLICY:
        if root in _DIRECTORIES:
            if root in entries or not any(rel.startswith(f"{root}/") for rel in entries):
                raise FreezeError("COVERAGE", f"{root} is not a directory holding a covered file in {commit[:12]}")
        elif root not in entries:
            raise FreezeError("COVERAGE", f"{root} is not a file in {commit[:12]}")


def _few(paths):
    """At most five paths, then the count of the others."""
    return ", ".join(paths[:5]) + (f" and {len(paths) - 5} more" if len(paths) > 5 else "")


def _file(fd, info, rel, expected):
    """SHA-256 of a covered regular file whose Git blob id equals the reference commit; fd is closed."""
    try:
        digest, blob = _hash(fd, info.st_size, rel)
    finally:
        os.close(fd)
    if blob != expected[rel][1]:
        raise FreezeError("HASH", f"{rel} differs from the reference commit")
    return digest


def _disk(root_fd, expected):
    """{path: SHA-256} of the covered files on disk: roots present with their type, no file outside the tree."""
    found = {}
    for root in POLICY:
        directory = root in _DIRECTORIES
        fd, info = _descend(root_fd, root, directory, "COVERAGE", "COVERAGE")
        if not directory:
            found[root] = _file(fd, info, root, expected)
            continue
        pending, count = [(root, fd)], 0
        while pending:
            prefix, dir_fd = pending.pop()
            if dir_fd is None:
                dir_fd, _ = _descend(root_fd, prefix, True, "LINK", "LINK")
            try:
                for name in sorted(os.listdir(dir_fd)):
                    rel = f"{prefix}/{name}"
                    if not _PART.fullmatch(name):
                        raise FreezeError("COVERAGE", f"{prefix}/ holds a non-portable name")
                    mode = os.stat(name, dir_fd=dir_fd, follow_symlinks=False).st_mode
                    if stat.S_ISDIR(mode):
                        if name != "__pycache__":
                            pending.append((rel, None))
                    elif not stat.S_ISREG(mode):
                        raise FreezeError("LINK", f"{rel} is a symbolic link or not a regular file")
                    elif rel != FROZEN:
                        if rel not in expected:
                            raise FreezeError("COVERAGE", f"{rel} is not tracked in the reference commit")
                        found[rel] = _file(*_open(dir_fd, name, rel, False, "LINK", "LINK"), rel, expected)
                        count += 1
            finally:
                os.close(dir_fd)
        if not count:
            raise FreezeError("COVERAGE", f"{root} holds no covered file on disk")
    missing = sorted(set(expected) - set(found))
    if missing:
        raise FreezeError("COVERAGE", f"{len(missing)} tracked file(s) absent on disk: {_few(missing)}")
    return found


def _approval(root, root_fd, commit, path):
    """SHA-256 of the approval document, tracked as a non-executable file in commit and identical on disk."""
    entry = _tree(root, commit, [path]).get(path)
    if entry is None or entry[0] != "100644":
        raise FreezeError("APPROVAL", f"{path} is not a tracked non-executable file in {commit[:12]}")
    fd, info = _descend(root_fd, path, False, "APPROVAL", "APPROVAL")
    try:
        digest, blob = _hash(fd, info.st_size, path)
    finally:
        os.close(fd)
    if blob != entry[1]:
        raise FreezeError("APPROVAL", f"{path} differs from {commit[:12]}")
    return digest


def _revs(root, span, *paths):
    """Commit ids of span that touch paths."""
    return _git(root, "rev-list", span, "--", *paths).stdout.decode().split()


def _blob(data):
    """Git blob id (SHA-1 object format) of bytes."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


def _seal(root, head, commit, raw):
    """Seal S: C strictly before HEAD on a linear line, S only adds FROZEN, FROZEN unseen before C and unchanged."""
    if _git(root, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}", ok=(0, 1)).stdout.strip() != (
            commit.encode()):
        raise FreezeError("SEAL", f"{commit[:12]} is not a commit of this repository")
    if commit == head or _git(root, "merge-base", "--is-ancestor", commit, head, ok=(0, 1)).returncode:
        raise FreezeError("SEAL", f"{commit[:12]} is not a strict ancestor of HEAD")
    chain = [line.split() for line in _git(root, "rev-list", "--topo-order", "--reverse", "--parents",
                                           f"{commit}..{head}").stdout.decode().splitlines()]
    if any(len(ids) != 2 for ids in chain) or chain[0][1] != commit:
        raise FreezeError("SEAL", f"the history after {commit[:12]} is not linear")
    seal = chain[0][0]
    if _git(root, "diff-tree", "-r", "-z", "--name-status", commit, seal).stdout != f"A\0{FROZEN}\0".encode():
        raise FreezeError("SEAL", f"the first commit after {commit[:12]} must only add {FROZEN}")
    entry = _git(root, "ls-tree", "-z", seal, "--", FROZEN).stdout
    if not entry.startswith(b"100644 blob "):
        raise FreezeError("SEAL", f"{FROZEN} is not a regular non-executable file in the seal")
    if _git(root, "rev-list", "--full-history", commit, "--", FROZEN).stdout:
        raise FreezeError("SEAL", f"{FROZEN} already appears in the history of {commit[:12]}: the schema serves once "
                                  "per lineage")
    if _revs(root, f"{commit}..{head}", FROZEN) != [seal] or _blob(raw) != entry[12:52].decode():
        raise FreezeError("SEAL", f"{FROZEN} changed after its seal")
    return seal


def check(root=ROOT):
    """Read-only verification of configs/FROZEN.json in root: its identity, or a FreezeError."""
    path, head = _root(root)
    root_fd = None
    try:
        root_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        raw = _read_frozen(root_fd)
        record = _parse(raw)
        commit, approval = record["commit"], record["approval"]["path"]
        seal = _seal(path, head, commit, raw)
        later = [rev for rev in _revs(path, f"{commit}..{head}", *POLICY) if rev != seal]
        if later:
            raise FreezeError("CHANGED", f"commit {later[0][:12]} after {commit[:12]} touches the frozen policy")
        if _revs(path, f"{commit}..{head}", approval):
            raise FreezeError("APPROVAL", f"{approval} changed after {commit[:12]}")
        expected = _tree(path, commit, POLICY)
        _require_roots(expected, commit)
        if set(record["files"]) != set(expected):
            absent, extra = sorted(set(expected) - set(record["files"])), sorted(set(record["files"]) - set(expected))
            cited_absent = absent[:5]
            cited_extra = extra[:5 - len(cited_absent)]
            raise FreezeError("COVERAGE", f"FROZEN files differ from {commit[:12]}: {len(absent)} missing "
                                          f"[{', '.join(cited_absent)}], {len(extra)} extra [{', '.join(cited_extra)}]")
        found = _disk(root_fd, expected)
        changed = sorted(rel for rel, digest in found.items() if digest != record["files"][rel])
        if changed:
            raise FreezeError("HASH", f"{_few(changed)} differ from FROZEN")
        if _approval(path, root_fd, commit, approval) != record["approval"]["sha256"]:
            raise FreezeError("APPROVAL", f"{approval} differs from FROZEN")
        return {"commit": commit, "seal": seal, "approval": approval, "files": len(found),
                "freeze_id": hashlib.sha256(raw).hexdigest()}
    except OSError as exc:
        raise FreezeError("IO", f"{type(exc).__name__} ({exc.strerror})") from exc
    finally:
        if root_fd is not None:
            os.close(root_fd)


def _create(dir_fd, data):
    """Exclusive creation of FROZEN.json in dir_fd; after a failure the name is removed only if it is still ours."""
    # ponytail: no atomic publish; a crash leaves a partial FROZEN that check refuses and write never replaces
    try:
        fd = os.open("FROZEN.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dir_fd)
    except FileExistsError as exc:
        raise FreezeError("EXISTS", f"{FROZEN} appeared before its creation; nothing was replaced") from exc
    created = os.fstat(fd)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    except OSError as exc:
        # ponytail: stat then unlink is not atomic; a substitution after this stat could still remove a foreign inode
        try:
            now = os.stat("FROZEN.json", dir_fd=dir_fd, follow_symlinks=False)
            ours = (now.st_dev, now.st_ino) == (created.st_dev, created.st_ino)
        except FileNotFoundError:
            ours = False
        if ours:
            os.unlink("FROZEN.json", dir_fd=dir_fd)
        raise FreezeError("IO", f"writing {FROZEN} failed ({exc.strerror}); " + (
            "the partial file was removed" if ours else "the name now designates another file, left untouched")
        ) from exc
    finally:
        os.close(fd)


def write(root, approval):
    """Creation of configs/FROZEN.json for HEAD = C, only in a synthetic repository under the temporary directory."""
    try:
        path = Path(root).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FreezeError("ROOT", f"--root does not resolve ({type(exc).__name__})") from exc
    temporary = Path(tempfile.gettempdir()).resolve()
    # ponytail: lot 21-F writes synthetic repositories only; the J4 activation GO must replace this guard and the next
    if path == temporary or not path.is_relative_to(temporary):
        raise FreezeError("PROJECT", "lot 21-F writes only synthetic repositories under the temporary directory")
    if not isinstance(approval, str) or not APPROVAL.fullmatch(approval):
        raise FreezeError("APPROVAL", f"--approval must match {APPROVAL.pattern}")
    path, head = _root(path)
    if not _git(path, "rev-parse", "--verify", "--quiet", f"{PROJECT_ROOT_COMMIT}^{{commit}}", ok=(0, 1)).returncode:
        raise FreezeError("PROJECT", "the repository holds the project root commit; lot 21-F writes synthetic "
                                     "repositories only")
    root_fd = configs = None
    try:
        root_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        configs, _ = _descend(root_fd, "configs", True, "COVERAGE", "COVERAGE")
        try:
            os.stat("FROZEN.json", dir_fd=configs, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise FreezeError("EXISTS", f"{FROZEN} exists; nothing was replaced")
        if _git(path, "rev-list", "--full-history", head, "--", FROZEN).stdout:
            raise FreezeError("SEAL", f"{FROZEN} already appears in the history of HEAD: the schema serves once per "
                                      "lineage")
        expected = _tree(path, head, POLICY)
        _require_roots(expected, head)
        found = _disk(root_fd, expected)
        data = _canonical({"schema": SCHEMA, "commit": head, "files": found,
                           "approval": {"path": approval, "sha256": _approval(path, root_fd, head, approval)}})
        if len(data) > MAX_FROZEN_BYTES:
            raise FreezeError("FORMAT", f"the canonical {FROZEN} would exceed {MAX_FROZEN_BYTES} bytes")
        _create(configs, data)
    except OSError as exc:
        raise FreezeError("IO", f"{type(exc).__name__} ({exc.strerror})") from exc
    finally:
        if configs is not None:
            os.close(configs)
        if root_fd is not None:
            os.close(root_fd)
    return {"path": FROZEN, "sha256": hashlib.sha256(data).hexdigest(), "commit": head, "files": len(found)}


def main(argv=None):
    """CLI: --check or --write; prints the identity or one refusal line; exit 0, 1 on refusal, 2 on usage error."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify configs/FROZEN.json; changes nothing")
    mode.add_argument("--write", action="store_true", help="create configs/FROZEN.json in a synthetic repository")
    parser.add_argument("--approval", help="tracked prompts/GO-<id>.md recorded as provenance (with --write only)")
    parser.add_argument("--root", default=str(ROOT), help="top level of the repository (default: this repository)")
    args = parser.parse_args(argv)
    if args.check and args.approval is not None:
        parser.error("--approval is only valid with --write")
    if args.write and args.approval is None:
        parser.error("--write needs --approval")
    try:
        if args.check:
            result = check(args.root)
            print(f"freeze-config: OK commit {result['commit']} seal {result['seal']} approval {result['approval']} "
                  f"files {result['files']} freeze_id {result['freeze_id']}")
        else:
            result = write(args.root, args.approval)
            print(f"freeze-config: wrote {FROZEN} sha256 {result['sha256']} commit {result['commit']} "
                  f"files {result['files']}")
            print(f"freeze-config: not committed; seal with one commit whose only parent is {result['commit']} and "
                  f"whose only change adds {FROZEN}")
    except FreezeError as exc:
        print(f"freeze-config: error: {exc}")
        return 1
    print(f"freeze-config: {CAVEAT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
