import json
import os
import subprocess
import time

import pytest

from tools.ops import monitor_claude_sessions as monitor


@pytest.mark.parametrize(("screen", "alive", "expected"), [
    ("✻ Doing… (15s · thinking with max effort)\n❯ ", True, "ACTIVE"),
    ("Ready to code?\nWould you like to proceed?\n1. Yes, and use auto mode", True, "PLAN_READY"),
    ("Do you want to allow this tool?\n1. Yes\n2. No", True, "WAITING_INPUT"),
    ("● Quel seuil retenir ?\n❯ ", True, "WAITING_INPUT"),
    ("You've hit your 5-hour limit · resets 11:20pm", True, "QUOTA"),
    ("Traceback (most recent call last):\nRuntimeError: lost connection\n❯ ", True, "EXCEPTION"),
    ("Traceback (most recent call last):\n✻ Doing… (30s · thinking with max effort)", True, "ACTIVE"),
    ("Question historique ?\n✻ Doing… (30s · thinking with max effort)", True, "ACTIVE"),
    ("Ready to code?\n✻ Doing… (30s · thinking with max effort)", True, "ACTIVE"),
    ("You've hit your 5-hour limit\n✻ Doing… (30s · thinking with max effort)", True, "ACTIVE"),
    ("Do you want to allow this tool?\n✻ Doing… (30s · thinking with max effort)", True, "ACTIVE"),
    ("✻ Doing… (30s · thinking with max effort)\nUnhandled exception: lost connection", True, "EXCEPTION"),
    ("Arrêt pour revue Codex.\n✻ Brewed for 2m · done\n❯ ", True, "REVIEW_READY"),
    ("✻ Cooked for 16m 49s · done 12:20 AM\n❯ ", True, "REVIEW_READY"),
    ("Prompt only\n❯ ", True, "IDLE"),
    ("Successful tests", False, "EXIT"),
])
def test_screen_states_request_review_without_answering(screen, alive, expected):
    assert monitor.screen_state(screen, alive) == expected


def test_file_activity_ignores_data_links_and_monitor_writes(tmp_path):
    now = time.time()
    logs = tmp_path / "logs"
    logs.mkdir()
    source = tmp_path / "source.py"
    source.write_text("pass\n")
    os.utime(source, (now - 4000, now - 4000))
    data = tmp_path / "data"
    data.mkdir()
    (data / "private").write_text("not inspected")
    (logs / "claude_surveillance.log").write_text("snapshot")
    (tmp_path / "linked").symlink_to(data, target_is_directory=True)
    os.utime(logs, (now - 4000, now - 4000))
    os.utime(tmp_path, (now - 4000, now - 4000))
    assert monitor.latest_write(tmp_path) <= now - 3999
    worker_log = logs / "worker.log"
    worker_log.write_text("new model work")
    os.utime(worker_log, (now + 1, now + 1))
    assert monitor.latest_write(tmp_path) >= now


def test_incomplete_file_scan_is_not_silent_inactivity(tmp_path, monkeypatch):
    def denied(path):
        raise PermissionError("scan denied")

    with monkeypatch.context() as patch:
        patch.setattr(monitor.os, "scandir", denied)
        with pytest.raises(PermissionError, match="scan denied"):
            monitor.latest_write(tmp_path)


def test_reports_persist_alerts_and_require_terminal_and_io_stagnation(tmp_path, monkeypatch):
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "claude_sessions.json").write_text(json.dumps([
        {"name": "jepa-s21-test", "worktree": str(tmp_path), "required": True},
    ]))
    screen = ["✻ Doing… (15s · thinking with max effort)"]
    now = time.time()

    def command(*args):
        if args[:2] == ("tmux", "list-panes"):
            return "jepa-s21-test\t%0\t123\tclaude\t" + str(tmp_path)
        if args[:2] == ("tmux", "capture-pane"):
            return screen[0]
        if args[0] == "ps":
            return "123 1 claude\n"
        if args[0] == "git":
            if "worktree" in args:
                return "worktree " + str(tmp_path) + "\n\n"
            if "--show-toplevel" in args:
                return str(tmp_path)
            return "stable HEAD and status"
        raise AssertionError(args)

    monkeypatch.setattr(monitor, "command", command)
    monkeypatch.setattr(monitor, "latest_write", lambda path: now - 4000)
    monkeypatch.setattr(monitor, "git_activity", lambda path: 0)
    first = monitor.inspect(tmp_path, now)
    assert first[0]["state"] == "ACTIVE"
    assert not (logs / "NEEDS_CODEX_REVIEW").exists()
    assert monitor.inspect(tmp_path, now + 1800)[0]["state"] == "ACTIVE"
    assert monitor.inspect(tmp_path, now + 1801)[0]["state"] == "STALLED"
    flag = logs / "NEEDS_CODEX_REVIEW"
    assert "STALLED" in flag.read_text() and screen[0] in flag.read_text()
    screen[0] = "✻ Doing… (new terminal output)"
    assert monitor.inspect(tmp_path, now + 1802)[0]["state"] == "ACTIVE"
    assert "STALLED" in flag.read_text()
    screen[0] = "● Quel seuil retenir ?\n❯ "
    assert monitor.inspect(tmp_path, now + 1803)[0]["state"] == "WAITING_INPUT"
    assert "Quel seuil" in flag.read_text()
    assert "timestamp" in json.loads((logs / "claude_surveillance.log").read_text().splitlines()[-1])
    assert json.loads((logs / ".claude_surveillance_state.json").read_text())


def test_registered_absence_is_an_alert_and_never_success(tmp_path, monkeypatch):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/claude_sessions.json").write_text(json.dumps([
        {"name": "jepa-missing", "worktree": str(tmp_path), "required": True},
    ]))
    monkeypatch.setattr(monitor, "command", lambda *args: "worktree " + str(tmp_path) if "worktree" in args else "")
    report = monitor.inspect(tmp_path, time.time())
    assert report[0]["state"] == "EXIT"
    assert "EXIT" in (tmp_path / "logs/NEEDS_CODEX_REVIEW").read_text()


def test_corrupt_cache_is_reported_instead_of_an_unhandled_monitor_exception(tmp_path, monkeypatch):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/.claude_surveillance_state.json").write_text("[]")
    monkeypatch.setattr(monitor, "ROOT", tmp_path)

    def command(*args):
        if args[:2] == ("tmux", "list-panes"):
            return "jepa-test\t%0\t123\tclaude\t" + str(tmp_path)
        if args[0] == "ps":
            return "123 1 claude\n"
        if "worktree" in args:
            return "worktree " + str(tmp_path) + "\n\n"
        if "--show-toplevel" in args:
            return str(tmp_path)
        return "stable"

    monkeypatch.setattr(monitor, "command", command)
    assert monitor.main() == 1
    assert "MONITOR_ERROR" in (tmp_path / "logs/NEEDS_CODEX_REVIEW").read_text()


def test_pane_failure_does_not_hide_other_session_or_scan_private_cwd(tmp_path, monkeypatch):
    def command(*args):
        if args[:2] == ("tmux", "list-panes"):
            return ("jepa-gone\t%0\t123\tclaude\t" + str(tmp_path) + "\n"
                    "jepa-live\t%1\t124\tclaude\t" + str(tmp_path / "data/raw/eurofidai") + "\n"
                    "jepa-helper\t%2\t125\tbash\t" + str(tmp_path))
        if args[:2] == ("tmux", "capture-pane"):
            if "%0" in args:
                raise RuntimeError("pane disappeared")
            return "✻ Doing… (15s · thinking with max effort)"
        if args[0] == "ps":
            return "123 1 claude\n124 1 claude\n125 1 bash\n126 125 claude-helper\n"
        if "worktree" in args:
            return "worktree " + str(tmp_path) + "\n\n"
        if "--show-toplevel" in args:
            return str(tmp_path)
        return "stable"

    def latest_write(path):
        assert path == tmp_path
        return time.time()

    monkeypatch.setattr(monitor, "command", command)
    monkeypatch.setattr(monitor, "latest_write", latest_write)
    monkeypatch.setattr(monitor, "git_activity", lambda path: 0)
    reports = {record["session"]: record for record in monitor.inspect(tmp_path, time.time())}
    assert reports["jepa-gone"]["state"] == "MONITOR_ERROR"
    assert reports["jepa-live"]["state"] == "ACTIVE"
    assert reports["jepa-helper"]["state"] == "EXIT"
    assert "pane disappeared" in (tmp_path / "logs/NEEDS_CODEX_REVIEW").read_text()


def test_git_only_activity_counts_without_changing_head_or_status(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    before = monitor.git_activity(tmp_path)
    fetched = tmp_path / ".git/FETCH_HEAD"
    fetched.write_text("metadata only\n")
    os.utime(fetched, (before + 100, before + 100))
    assert monitor.git_activity(tmp_path) >= before + 99
