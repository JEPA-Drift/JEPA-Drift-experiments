"""Inspect declared and jepa-* tmux sessions without sending input; preserve alerts until Codex acknowledges them."""
import hashlib
import json
import math
import os
import re
import subprocess
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRUNE = {".git", ".venv", "external", "data", "graphify-out", ".pytest_cache", "__pycache__"}
OWN_LOGS = {"claude_surveillance.log", "NEEDS_CODEX_REVIEW", "claude_sessions.json", "daemon_monitor.log",
            "cron_monitor.log", "streams_status.log", ".claude_monitor.pid"}
ALERTS = {"PLAN_READY", "WAITING_INPUT", "QUOTA", "EXCEPTION", "EXIT", "STALLED", "REVIEW_READY", "MONITOR_ERROR"}


def command(*args):
    """Read a bounded host command without a shell or Git index refresh."""
    result = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=10,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    if result.returncode:
        if args[:2] == ("tmux", "list-panes") and "no server running" in result.stderr:
            return ""
        raise RuntimeError(f"{args[0]} failed ({result.returncode}): {result.stderr.strip()}")
    return result.stdout


def screen_state(screen, alive):
    """Classify screen evidence conservatively; these labels never authorize a reply or imply successful completion."""
    if not alive:
        return "EXIT"
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", screen)
    prompts = list(re.finditer(r"(?m)^[ \t]*❯[^\S\n]*\S", text))
    if prompts:
        text = text[prompts[-1].start():]

    def last(pattern):
        return max((match.start() for match in re.finditer(pattern, text, re.I | re.M)), default=-1)

    at, status = max([
        (last(r"Ready to code\?|Would you like to proceed\?"), "PLAN_READY"),
        (last(r"(?:hit your|weekly|usage|5-hour).*limit|quota.*(?:exceeded|épuis)"), "QUOTA"),
        (last(r"Do you want to|Allow this|trust the files|Enter to select"), "WAITING_INPUT"),
        (last(r"Traceback \(most recent call last\)|Unhandled.*(?:error|exception)|Segmentation fault"), "EXCEPTION"),
    ])
    if last(r"^[ \t]*[✻✽✢✳✶·].*…|esc to interrupt") > at:
        return "ACTIVE"
    # ponytail: screen heuristics only; ambiguous idle screens request review, never automated keystrokes
    if at >= 0:
        return status
    if any(line.rstrip().endswith(("?", "？")) for line in text.splitlines()[-40:]):
        return "WAITING_INPUT"
    if re.search(r"(?:arrêt|attente|stop|ready|await|waiting).*rev(?:ue|iew)|✻.* for .*· done", text, re.I):
        return "REVIEW_READY"
    return "IDLE"


def latest_write(worktree):
    """Return recent non-data file activity without following symlinks or counting the monitor's own writes."""
    newest = worktree.stat().st_mtime

    def failed(error):
        raise error

    for directory, dirs, files in os.walk(worktree, followlinks=False, onerror=failed):
        base = Path(directory)
        dirs[:] = [name for name in dirs if name not in PRUNE and not (base / name).is_symlink()]
        if base != worktree / "logs":
            try:
                newest = max(newest, base.stat().st_mtime)
            except FileNotFoundError:
                continue
        for name in files:
            path = base / name
            if name == ".git" or path.is_symlink():
                continue
            if base == worktree / "logs" and (name in OWN_LOGS or name.startswith(".claude_surveillance")):
                continue
            try:
                newest = max(newest, path.stat().st_mtime)
            except FileNotFoundError:
                continue
    return newest


def git_activity(worktree):
    """Observe bounded Git metadata, including fetches that leave HEAD and porcelain status unchanged."""
    directories = command("git", "-C", str(worktree), "rev-parse", "--path-format=absolute",
                          "--git-dir", "--git-common-dir").splitlines()
    newest = 0
    for directory in directories:
        for name in (".", "index", "HEAD", "FETCH_HEAD", "ORIG_HEAD", "packed-refs", "logs/HEAD",
                     "refs", "refs/heads", "refs/remotes", "refs/remotes/origin"):
            try:
                newest = max(newest, (Path(directory) / name).stat().st_mtime)
            except FileNotFoundError:
                continue
    return newest


def inspect(root, now):
    """Append timestamped session reports and unacknowledged alert excerpts, then save the observation baseline."""
    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    registry = logs / "claude_sessions.json"
    targets = json.loads(registry.read_text()) if registry.exists() else [
        {"name": "jepa-s31", "worktree": str(root.parent / "JEPA-stream-31"), "required": False}]
    if not isinstance(targets, list):
        raise ValueError("session registry must be a list")
    declared = {}
    for entry in targets:
        if (not isinstance(entry, dict) or not isinstance(entry.get("name"), str)
                or not entry["name"].startswith("jepa-") or not isinstance(entry.get("required"), bool)
                or not isinstance(entry.get("worktree"), str) or not Path(entry["worktree"]).is_absolute()
                or entry["name"] in declared):
            raise ValueError("invalid or duplicate session registry entry")
        declared[entry["name"]] = entry
    registered = set(declared)
    approved = {Path(line[9:]).resolve() for line in command(
        "git", "-C", str(root), "worktree", "list", "--porcelain").splitlines() if line.startswith("worktree ")}
    panes = []
    listing = command("tmux", "list-panes", "-a", "-F",
                      "#{session_name}\t#{pane_id}\t#{pane_pid}\t#{pane_current_command}\t#{pane_current_path}")
    for line in listing.splitlines():
        name, pane, pid, current, cwd = line.split("\t", 4)
        if name in declared or name.startswith("jepa-"):
            panes.append((name, pane, int(pid), current, cwd))
            declared.setdefault(name, {"name": name, "worktree": cwd, "required": True})
    processes = {}
    for line in command("ps", "-u", str(os.getuid()), "-o", "pid=,ppid=,comm=").splitlines():
        pid, parent, comm = line.split(None, 2)
        processes[int(pid)] = (int(parent), comm)
    state_path = logs / ".claude_surveillance_state.json"
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    if not isinstance(previous, dict):
        raise ValueError("observation cache must be an object")
    for old in previous.values():
        if (not isinstance(old, dict) or not isinstance(old.get("screen"), str)
                or not isinstance(old.get("git"), str)
                or any(isinstance(old.get(key), bool) or not isinstance(old.get(key), (int, float))
                       or not math.isfinite(old[key]) for key in ("terminal_at", "io_at"))):
            raise ValueError("invalid observation cache entry")
    next_state = {}
    reports = []
    timestamp = datetime.fromtimestamp(now, UTC).isoformat()
    for name, entry in declared.items():
        matches = [pane for pane in panes if pane[0] == name]
        for _, pane, pid, current, cwd in matches or [(name, "", 0, "", "")]:
            screen = ""
            record = {"timestamp": timestamp, "session": name, "pane": pane, "pid": pid}
            try:
                screen = command("tmux", "capture-pane", "-p", "-t", pane, "-S", "-80") if pane else ""
                family = {pid}
                while children := {p for p, (parent, _) in processes.items() if parent in family} - family:
                    family.update(children)
                alive = any(processes[p][1] == "claude" for p in family if p in processes)
                record["state"] = screen_state(screen, alive)
                if not pane and not entry["required"]:
                    record["state"] = "ABSENT_NOT_EXPECTED"
                if pane and alive:
                    worktree = Path(command("git", "-C", cwd, "rev-parse", "--show-toplevel").strip()).resolve()
                    if worktree not in approved or (name in registered and Path(entry["worktree"]).resolve() != worktree):
                        raise ValueError("pane is not in its approved repository worktree")
                    signature = command("git", "-C", str(worktree), "rev-parse", "HEAD") + command(
                        "git", "-C", str(worktree), "status", "--porcelain=v1", "--untracked-files=normal")
                    digest = hashlib.sha256(screen.encode()).hexdigest()
                    old = previous.get(name + pane, {})
                    terminal_at = now if old.get("screen") != digest else old["terminal_at"]
                    io_at = max(latest_write(worktree), git_activity(worktree), old.get("io_at", 0))
                    if old and old.get("git") != signature:
                        io_at = now
                    io_idle = max(0, now - io_at)
                    terminal_idle = max(0, now - terminal_at)
                    record.update(disk_git_idle_seconds=round(io_idle, 1), terminal_idle_seconds=round(terminal_idle, 1),
                                  disk_git_idle=io_idle > 1800, command=current)
                    if io_idle > 1800 and terminal_idle > 1800 and record["state"] in {"ACTIVE", "IDLE"}:
                        record["state"] = "STALLED"
                    next_state[name + pane] = {"screen": digest, "terminal_at": terminal_at,
                                               "git": signature, "io_at": io_at}
            except Exception as exc:
                record.update(state="MONITOR_ERROR", error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
            reports.append(record)
            with (logs / "claude_surveillance.log").open("a") as output:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
            if record["state"] in ALERTS:
                with (logs / "NEEDS_CODEX_REVIEW").open("a") as output:
                    output.write(json.dumps(record, ensure_ascii=False) + "\n" + screen + "\n\n")
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(next_state))
    temporary.replace(state_path)
    return reports


def main():
    """Run one inspection; monitoring errors also require review and never trigger a session restart."""
    try:
        reports = inspect(ROOT, time.time())
        for report in reports:
            print(json.dumps(report, ensure_ascii=False))
        return int(any(report["state"] == "MONITOR_ERROR" for report in reports))
    except Exception as exc:
        record = json.dumps({"timestamp": datetime.now(UTC).isoformat(), "state": "MONITOR_ERROR",
                             "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}, ensure_ascii=False)
        logs = ROOT / "logs"
        logs.mkdir(exist_ok=True)
        for name in ("claude_surveillance.log", "NEEDS_CODEX_REVIEW"):
            with (logs / name).open("a") as output:
                output.write(record + "\n")
        print(record)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
