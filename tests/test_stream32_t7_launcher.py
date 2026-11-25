import copy
import errno
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml


SOURCE = Path(__file__).resolve().parents[1] / "logs/stream-32-t7/t7-supervisor.py"
pytestmark = pytest.mark.skipif(
    not SOURCE.parent.is_dir(), reason="local T7 launcher artifacts are outside Git"
)
FILES = {
    "logs/stream-32-t7/t7-supervisor.py",
    "logs/stream-32-t7/t7-wall-guard.py",
    "logs/stream-32-t7/t7-worker.sh",
    "logs/stream-32-t7/run-t7.sh",
    "logs/stream-32-t7/check-t7-status.sh",
    "tools/ops/audit_stream32_t7.py",
    "experiments/pca_info_online.py",
    "jepadrift/sim.py",
}


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def launcher(tmp_path, monkeypatch):
    assert SOURCE.is_file(), "A2 isolated launcher has not been implemented"
    spec = importlib.util.spec_from_file_location("t7_launcher_fixture", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path / "repository"
    root.mkdir()
    monkeypatch.setattr(module, "ROOT", root)
    lock = tmp_path / "execution.lock"
    lock.touch()
    monkeypatch.setattr(module, "LOCK", lock)
    read_text = Path.read_text

    def controlled_boot(path, *args, **kwargs):
        if path == Path("/proc/sys/kernel/random/boot_id"):
            return "fixture-boot-id\n"
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", controlled_boot)
    monkeypatch.setattr(module, "unit_state", lambda unit: {
        "Id": unit, "ActiveState": "active", "ControlGroup": "/controlled/app.slice", "control_returncode": 0,
    })
    for name, value in module.ENV.items():
        monkeypatch.setenv(name, value)
    for rel in FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Neutral controlled fixture: {rel}\n", encoding="utf-8")
    return module


@pytest.fixture
def intent(launcher, monkeypatch):
    root = launcher.ROOT
    envelope = {"memory_max_gib": 8, "cpu_hours_max": 1, "wall_seconds_per_invocation": 30, "jobs_max": 2}
    cfg = {"seed": 3232, "envelope": envelope, "modes": {"smoke": {"null_plan": None}},
           "scope": {"setups": [["FITTED_LW_T7", 32, 0]]}, "authorization": None}
    desc = {"mode": "smoke", "envelope": envelope, "scope": cfg["scope"], "null_plan": None,
            "code": {name: _sha(root / name) for name in ("experiments/pca_info_online.py", "jepadrift/sim.py")},
            "seed_plan_sha256": "1" * 64}
    did = launcher.canonical_sha(desc)
    scientific = root / "configs/scientific.yaml"
    scientific.parent.mkdir()
    scientific.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    value = {"schema": "stream32-t7-launch/1", "stage": "qualification", "mode": "smoke",
             "design_id": did, "descriptor": desc, "seed_plan_sha256": desc["seed_plan_sha256"],
             "envelope": envelope, "scientific_config": {"path": "configs/scientific.yaml", "sha256": _sha(scientific)},
             "authorized_config": {"path": "configs/authorized.yaml", "sha256": "0" * 64},
             "go_reference": {"path": "prompts/GO-stream-32-t7-runtime-fixture.md", "sha256": "0" * 64},
             "artifacts": {name: _sha(root / name) for name in FILES},
             "qualification_cases": {"continuous": {"jobs": [1], "stop_after": None},
                                     "resumed": {"jobs": [1, 2], "stop_after": "CAL"}}}
    go = root / value["go_reference"]["path"]
    go.parent.mkdir()
    go.write_text("\n".join(["Synthetic controlled A2 fixture only", "T7_RUNTIME_GO ACCORDÉ",
                             "stage: qualification", f"design_id: {did}",
                             f"seed_plan_sha256: {desc['seed_plan_sha256']}",
                             f"approval_sha256: {launcher.approval_sha(value)}"]) + "\n", encoding="utf-8")
    value["go_reference"]["sha256"] = _sha(go)
    cfg["authorization"] = {"stage": "smoke", "design_id": did, "go_reference": value["go_reference"]}
    authorized = root / "configs/authorized.yaml"
    authorized.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    value["authorized_config"]["sha256"] = _sha(authorized)
    path = root / "intent.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    monkeypatch.setattr(launcher, "describe", lambda config, mode: {"design_id": did, "descriptor": copy.deepcopy(desc)})
    return value


def _save(launcher, value):
    (launcher.ROOT / "intent.json").write_text(json.dumps(value), encoding="utf-8")


def _approved(launcher, intent):
    return launcher.preflight("intent.json", 1)


def _sample(launcher, approved, invocation, result="success", status="0"):
    launcher.atomic_json(Path(invocation["sample_path"]), {
        "token": invocation["token"], "unit": invocation["unit"], "design_id": approved["intent"]["design_id"],
        "cgroup": "/controlled/" + invocation["unit"], "cpu_usec": 250000,
        "memory_peak": 4096, "memory_max": 8 * 1024 ** 3, "memory_events": {"oom": 0, "oom_kill": 0},
        "cpu_affinity": [invocation["cpu_affinity"]], "sampled_monotonic": invocation["started_monotonic"] + 0.25,
        "service_result": result, "exit_code": "exited", "exit_status": status,
    })


def _observation(invocation, drained=True):
    return {"drained": drained, "unit": invocation["unit"], "cgroup": "/controlled/" + invocation["unit"],
            "CPUUsageNSec": "300000000", "ActiveState": "inactive", "MainPID": "0"}


def _resume_file(launcher, approved, ledger, reconciliation=False, next_intent=None):
    previous = ledger["invocations"][-1]
    value = {"schema": "stream32-t7-resume/1", "stage": ledger["stage"], "design_id": ledger["design_id"],
             "previous_token": previous["token"], "intent_sha256": ledger["intent_sha256"],
             "receipt_sha256": previous["receipt_sha256"],
             "inventory_sha256": launcher.canonical_sha(launcher.inventory(approved)),
             "cpu_charged_seconds": ledger["cpu_charged_seconds"], "reconciliation": reconciliation}
    if ledger["stage"] == "qualification":
        value["case"] = approved["case"]
    if next_intent is not None:
        value["next_intent_sha256"] = next_intent
    go = launcher.ROOT / "prompts/GO-stream-32-t7-resume-fixture.md"
    lines = ["T7_RESUME_GO ACCORDÉ", *(f"{key}: {value[key]}" for key in (
        "stage", "design_id", "previous_token", "intent_sha256", "receipt_sha256", "inventory_sha256", "cpu_charged_seconds"))]
    if "case" in value:
        lines.append(f"case: {value['case']}")
    if reconciliation:
        lines.append("T7_RECONCILIATION_GO ACCORDÉ")
    if next_intent is not None:
        lines.append(f"next_intent_sha256: {next_intent}")
    go.write_text("\n".join(lines) + "\n", encoding="utf-8")
    value["go_reference"] = {"path": go.relative_to(launcher.ROOT).as_posix(), "sha256": _sha(go)}
    path = launcher.ROOT / "resume.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path.name


def test_preflight_is_read_only_and_derives_disposable_paths(launcher, intent):
    approved = _approved(launcher, intent)
    paths = approved["paths"]
    assert paths["run_root"] == launcher.ROOT / f"logs/stream-32-t7/qualification/{intent['design_id'][:16]}"
    assert paths["publication"] == paths["run_root"] / "cases/continuous/publication"
    assert not paths["run_root"].exists()
    assert approved["approval_sha256"] == launcher.approval_sha(intent)


@pytest.mark.parametrize("jobs", [0, -1, 2, True])
def test_jobs_fail_before_any_ledger_or_staging(launcher, intent, jobs):
    with pytest.raises(ValueError):
        launcher.preflight("intent.json", jobs)
    assert not (launcher.ROOT / "logs/stream-32-t7/qualification").exists()


@pytest.mark.parametrize("change", ["go", "artifact", "yaml", "descriptor", "environment", "draft_go"])
def test_preflight_rejects_changed_authority_before_effects(launcher, intent, monkeypatch, change):
    if change == "go":
        (launcher.ROOT / intent["go_reference"]["path"]).write_text("NO_RUNTIME_GO\n", encoding="utf-8")
    elif change == "artifact":
        (launcher.ROOT / "jepadrift/sim.py").write_text("altered", encoding="utf-8")
    elif change == "yaml":
        (launcher.ROOT / "configs/scientific.yaml").write_text("seed: 0\n", encoding="utf-8")
    elif change == "descriptor":
        monkeypatch.setattr(launcher, "describe", lambda config, mode: {"design_id": intent["design_id"], "descriptor": {}})
    elif change == "environment":
        monkeypatch.setenv("MPLBACKEND", "svg")
    else:
        intent["go_reference"]["path"] = "prompts/GO-stream-32-t7-tech-20261122.md"
        _save(launcher, intent)
    with pytest.raises((ValueError, OSError)):
        _approved(launcher, intent)
    assert not (launcher.ROOT / "logs/stream-32-t7/qualification").exists()


def test_exact_descriptor_scope_envelope_and_artifacts_are_required(launcher, intent):
    intent["envelope"] = {**intent["envelope"], "jobs_max": 3}
    _save(launcher, intent)
    with pytest.raises(ValueError):
        _approved(launcher, intent)
    assert not (launcher.ROOT / "logs/stream-32-t7/qualification").exists()


def test_symlink_ancestor_is_refused_before_effects(launcher, intent):
    outside = launcher.ROOT.parent / "foreign"
    outside.mkdir()
    (launcher.ROOT / "logs/stream-32-t7/qualification").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink|symbolic"):
        _approved(launcher, intent)
    assert not list(outside.iterdir())


def test_scientific_paths_are_fixed_and_distinct(launcher):
    did = "a" * 64
    paths = launcher.run_paths("pilot", did)
    assert paths["run_root"] == launcher.ROOT / f"logs/stream-32/t7/pilot/{did[:16]}"
    assert paths["publication"] == launcher.ROOT / "results/pca_info_online/t7-pilot"
    assert paths["publication"] != launcher.run_paths("full", did)["publication"]
    with pytest.raises(ValueError):
        launcher.run_paths("foreign", did)


def test_reservation_fits_cpu_remainder_with_shutdown_margin(launcher):
    admitted = launcher.limits(30, 32)
    assert admitted["cpu_capacity_cores"] == 1
    assert admitted["cpu_reservation_seconds"] == 32
    assert 0 < admitted["application_seconds"] < admitted["runtime_seconds"] < admitted["wall_seconds"]
    for remaining in (0, 31, math.nan):
        with pytest.raises(ValueError):
            launcher.limits(30, remaining)


def test_atomic_ledger_fsyncs_file_then_renames_then_fsyncs_parent(launcher, tmp_path, monkeypatch):
    events = []
    sync, rename = os.fsync, os.replace
    monkeypatch.setattr(launcher.os, "fsync", lambda fd: (events.append("fsync"), sync(fd))[1])
    monkeypatch.setattr(launcher.os, "replace", lambda a, b: (events.append("rename"), rename(a, b))[1])
    target = tmp_path / "ledger.json"
    launcher.atomic_json(target, {"state": "RUNNING"})
    assert json.loads(target.read_bytes()) == {"state": "RUNNING"}
    assert events == ["fsync", "rename", "fsync"]


def test_shared_lock_rejects_concurrent_entry_without_reserving(launcher, intent):
    approved = _approved(launcher, intent)
    with launcher.execution_lock():
        other = os.open(launcher.LOCK, os.O_RDONLY)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(other)
        invocation = launcher.reserve(approved, 1)
        ledger = launcher.read_json(approved["paths"]["ledger"])
        assert ledger["state"] == invocation["state"] == "RUNNING"
        assert ledger["invocations"][-1]["token"] == invocation["token"]
        assert ledger["cpu_reserved_seconds"] == invocation["limits"]["cpu_reservation_seconds"]
    assert not approved["paths"]["staging"].exists()


def test_orphaned_outputs_are_never_adopted(launcher, intent):
    approved = _approved(launcher, intent)
    approved["paths"]["publication"].mkdir(parents=True)
    with launcher.execution_lock(), pytest.raises(ValueError, match="orphan|prior|existing"):
        launcher.reserve(approved, 1)
    assert not approved["paths"]["ledger"].exists()


def test_scope_must_be_drained_before_running_is_replaced(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation)
        monkeypatch.setattr(launcher, "observe_scope", lambda row: _observation(row, drained=False))
        with pytest.raises(RuntimeError, match="drain"):
            launcher.settle(approved, invocation["token"])
        assert launcher.read_json(approved["paths"]["ledger"])["state"] == "RUNNING"
        assert not Path(invocation["receipt_path"]).exists()


@pytest.mark.parametrize("field", ["receipt_path", "sample_path", "unit"])
def test_tampered_token_paths_are_refused_before_io(launcher, intent, monkeypatch, tmp_path, field):
    approved = _approved(launcher, intent)
    foreign = tmp_path / "foreign.json"
    foreign.write_text("{}\n", encoding="utf-8")
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        path = approved["paths"]["ledger"]
        ledger = launcher.read_json(path)
        ledger["invocations"][-1][field] = "foreign.service" if field == "unit" else str(foreign)
        launcher.atomic_json(path, ledger)
        original = launcher.read_json

        def checked_read(candidate):
            assert candidate != foreign, "a foreign token path was read"
            return original(candidate)

        monkeypatch.setattr(launcher, "read_json", checked_read)
        monkeypatch.setattr(launcher, "observe_scope", lambda row: pytest.fail("tampered invocation reached cgroup"))
        with pytest.raises(ValueError, match="token paths"):
            launcher.settle(approved, invocation["token"])
        assert launcher.read_json(path) == ledger


@pytest.mark.parametrize("failure", ["forced", "parent_crash", "missing_sample"])
def test_interrupted_or_unmeasured_scope_is_charged_and_blocked(launcher, intent, monkeypatch, failure):
    approved = _approved(launcher, intent)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        if failure != "missing_sample":
            _sample(launcher, approved, invocation, result="timeout" if failure == "forced" else "success")
        monkeypatch.setattr(launcher, "observe_scope", _observation)
        monkeypatch.setattr(launcher, "inventory", lambda approved: {})
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        assert launcher.settle(approved, invocation["token"], crashed=failure == "parent_crash") == 4
        ledger = launcher.read_json(approved["paths"]["ledger"])
        assert ledger["state"] == "RECONCILIATION_REQUIRED"
        assert ledger["cpu_charged_seconds"] >= invocation["limits"]["cpu_reservation_seconds"]
        receipt = launcher.read_json(Path(invocation["receipt_path"]))
        assert receipt["scope_stopped"] is True
        assert receipt["cpu_measured_seconds"] != 0
        assert ledger["invocations"][-1]["receipt_sha256"] == _sha(Path(invocation["receipt_path"]))
        with pytest.raises(ValueError):
            launcher.reserve(approved, 1, resume=True)


def test_clean_pause_binds_inventory_and_requires_new_resume_authority(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    observed = {"run/checkpoint.json": "2" * 64}
    monkeypatch.setattr(launcher, "inventory", lambda approved: copy.deepcopy(observed))
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation, result="exit-code", status="2")
        status = approved["paths"]["staging"] / "status.json"
        status.parent.mkdir(parents=True)
        status.write_text(json.dumps({"design_id": intent["design_id"], "status": "BLOCKED_RESOURCE"}), encoding="utf-8")
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        assert launcher.settle(approved, invocation["token"]) == 2
        ledger = launcher.read_json(approved["paths"]["ledger"])
        assert ledger["state"] == "CLEAN_BLOCKED_RESOURCE"
        assert ledger["cpu_charged_seconds"] == 1
        assert ledger["invocations"][-1]["inventory"] == observed
        with pytest.raises(ValueError, match="resume.*authority|authority.*resume"):
            launcher.reserve(approved, 1, resume=True)
        observed["run/checkpoint.json"] = "3" * 64
        with pytest.raises(ValueError):
            launcher.reserve(approved, 1, resume=True, resume_authority="nonexistent.json")


def test_receipt_mutation_prevents_reentry(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation)
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        launcher.settle(approved, invocation["token"])
        Path(invocation["receipt_path"]).write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError):
            launcher.verify_receipts(launcher.read_json(approved["paths"]["ledger"]), approved["paths"]["ledger"])


def test_measurement_mutation_prevents_reentry(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation)
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        launcher.settle(approved, invocation["token"])
        Path(invocation["sample_path"]).write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match="sample|measurement"):
            launcher.verify_receipts(launcher.read_json(approved["paths"]["ledger"]), approved["paths"]["ledger"])


def test_receipt_survives_crash_before_ledger_settlement(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation)
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        atomic = launcher.atomic_json

        def interrupted(path, value):
            if path == approved["paths"]["ledger"]:
                raise OSError("controlled crash after receipt fsync")
            return atomic(path, value)

        monkeypatch.setattr(launcher, "atomic_json", interrupted)
        with pytest.raises(OSError, match="controlled crash"):
            launcher.settle(approved, invocation["token"])
        receipt_sha = _sha(Path(invocation["receipt_path"]))
        assert launcher.read_json(approved["paths"]["ledger"])["state"] == "RUNNING"
        monkeypatch.setattr(launcher, "atomic_json", atomic)
        assert launcher.settle(approved, invocation["token"], crashed=True) == 4
        assert _sha(Path(invocation["receipt_path"])) == receipt_sha
        ledger = launcher.read_json(approved["paths"]["ledger"])
        assert ledger["cpu_charged_seconds"] == invocation["limits"]["cpu_reservation_seconds"]
        launcher.verify_receipts(ledger, approved["paths"]["ledger"])


def test_clean_resume_consumes_only_a_bound_written_authority(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation, result="exit-code", status="2")
        status = approved["paths"]["staging"] / "status.json"
        status.parent.mkdir(parents=True)
        status.write_text(json.dumps({"design_id": intent["design_id"], "status": "BLOCKED_RESOURCE"}), encoding="utf-8")
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        assert launcher.settle(approved, invocation["token"]) == 2
        ledger = launcher.read_json(approved["paths"]["ledger"])
        authority = _resume_file(launcher, approved, ledger)
        resumed = launcher.reserve(approved, 1, resume=True, resume_authority=authority)
        new_ledger = launcher.read_json(approved["paths"]["ledger"])
        assert new_ledger["cpu_charged_seconds"] == ledger["cpu_charged_seconds"]
        assert resumed["token"] != invocation["token"] and resumed["resume"] is True
        assert new_ledger["state"] == "RUNNING"
        assert resumed["resume_authority"]["sha256"] == _sha(launcher.ROOT / authority)


def test_human_reconciliation_keeps_interrupted_receipt_and_authorizes_new_token(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        invocation = launcher.reserve(approved, 1)
        _sample(launcher, approved, invocation, result="timeout", status="9")
        monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
        assert launcher.settle(approved, invocation["token"]) == 4
    ledger = launcher.read_json(approved["paths"]["ledger"])
    authority = _resume_file(launcher, approved, ledger, reconciliation=True)
    receipt_sha = _sha(Path(invocation["receipt_path"]))
    assert launcher.reconcile("intent.json", authority) == 0
    with launcher.execution_lock():
        resumed = launcher.reserve(approved, 1, resume=True, resume_authority=authority)
    assert resumed["token"] != invocation["token"]
    assert _sha(Path(invocation["receipt_path"])) == receipt_sha


def test_native_scope_refuses_unknown_or_populated_cgroup(launcher, monkeypatch):
    monkeypatch.setattr(launcher, "unit_state", lambda unit: {"LoadState": "not-found"})
    assert launcher.observe_scope({"unit": "jepa-t7-fixture.service"})["drained"] is False


def _terminal_unit(invocation):
    return {
        "Id": invocation["unit"], "LoadState": "loaded", "ActiveState": "failed", "SubState": "failed", "Slice": "app.slice",
        "Result": "exit-code", "MainPID": "0", "ControlPID": "0", "ControlGroup": "",
        "CPUUsageNSec": "1165511000", "CPUAccounting": "yes", "CPUAffinity": str(invocation["cpu_affinity"]),
        "SystemCallFilter": "~sched_setaffinity", "SystemCallErrorNumber": "1",
        "ExecMainStartTimestampMonotonic": str(math.ceil(invocation["started_monotonic"] * 1_000_000)),
        "InvocationID": "b" * 32, "control_returncode": 0,
    }


@pytest.mark.parametrize("state", ["removed", "empty", "populated", "no-events", "error", "timeout", "unknown", "control-pid"])
def test_failed_unit_with_no_reported_group_or_sample(launcher, intent, monkeypatch, tmp_path, state):
    approved = _approved(launcher, intent)
    invocation = launcher.reserve(approved, 1)
    assert invocation["cgroup"] == "/controlled/app.slice/" + invocation["unit"]
    terminal = _terminal_unit(invocation)
    if state == "error":
        terminal["control_returncode"] = 1
    if state == "control-pid":
        terminal["ControlPID"] = "123"
    if state == "unknown":
        invocation.pop("cgroup")
    def read_state(unit):
        if state == "timeout":
            raise subprocess.TimeoutExpired("systemctl show", 10)
        return terminal

    monkeypatch.setattr(launcher, "unit_state", read_state)
    cgroup = tmp_path / invocation["unit"]
    monkeypatch.setattr(launcher, "_cgroup", lambda group, unit: cgroup)
    if state in ("empty", "populated", "no-events"):
        cgroup.mkdir()
        if state != "no-events":
            (cgroup / "cgroup.events").write_text(f"populated {int(state == 'populated')}\n")
    assert not Path(invocation["sample_path"]).exists()
    assert launcher.observe_scope(invocation)["drained"] == (state in ("removed", "empty"))


@pytest.mark.parametrize("condition", ["no-cpu", "no-stat", "cpu-no-quota", "cpu-over-quota", "affinity",
                                       "affinity-writable", "not-eperm", "memory"])
def test_cgroup_checks_on_memory_pids_host(launcher, intent, monkeypatch, tmp_path, condition):
    approved = _approved(launcher, intent)
    invocation = launcher.reserve(approved, 1)
    cg = tmp_path / invocation["unit"]
    cg.mkdir()
    controls = "cpu memory pids" if condition.startswith("cpu-") else "memory pids"
    (cg / "cgroup.controllers").write_text(controls)
    (cg / "memory.max").write_text("1" if condition == "memory" else str(8 * 1024**3))
    if condition != "no-stat":
        (cg / "cpu.stat").write_text("usage_usec 250000\n")
    if condition == "cpu-over-quota":
        (cg / "cpu.max").write_text("20000 10000\n")
    read = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda path, *a, **kw: (
        "0::" + invocation["cgroup"] if path == Path("/proc/self/cgroup") else read(path, *a, **kw)))
    monkeypatch.setattr(launcher, "_cgroup", lambda group, unit: cg)
    cpu = invocation["cpu_affinity"]
    monkeypatch.setattr(launcher.os, "sched_getaffinity", lambda pid: {cpu, cpu + 1} if condition == "affinity" else {cpu})
    attempted = []

    def set_affinity(pid, mask):
        attempted.append(mask)
        if condition != "affinity-writable":
            reason = errno.EACCES if condition == "not-eperm" else errno.EPERM
            raise PermissionError(reason, os.strerror(reason))

    monkeypatch.setattr(launcher.os, "sched_setaffinity", set_affinity)
    monkeypatch.setattr(launcher, "unit_state", lambda unit: {
        **_terminal_unit(invocation), "ActiveState": "active", "ControlGroup": invocation["cgroup"],
    })
    if condition in ("no-cpu", "no-stat"):
        assert launcher._require_cgroup(approved, invocation)[:2] == (cg, invocation["cgroup"])
        assert attempted == [{cpu}]
    else:
        with pytest.raises((OSError, ValueError)):
            launcher._require_cgroup(approved, invocation)


@pytest.mark.parametrize("proof", ["valid", "wrong-affinity", "wrong-unit", "no-filter", "sentinel", "foreign-boot"])
def test_late_recovery_without_sample_preserves_old_seal(launcher, intent, monkeypatch, proof):
    approved = _approved(launcher, intent)
    invocation = launcher.reserve(approved, 1)
    path = approved["paths"]["ledger"]
    before = launcher.read_json(path)
    row = before["invocations"][0]
    row.pop("cgroup", None)
    row.pop("intent_sha256", None)
    row.pop("approval_sha256", None)
    terminal = _terminal_unit(invocation)
    if proof == "wrong-affinity":
        terminal["CPUAffinity"] += " 2"
    if proof == "wrong-unit":
        terminal["InvocationID"] = ""
    if proof == "no-filter":
        terminal["SystemCallFilter"] = ""
    if proof == "sentinel":
        terminal["CPUUsageNSec"] = str(2**64 - 1)
    if proof == "foreign-boot":
        row["boot_id"] = "previous-boot"
    launcher.atomic_json(path, before)
    unit_state = launcher.unit_state
    monkeypatch.setattr(launcher, "unit_state", lambda unit: terminal if unit == invocation["unit"] else unit_state(unit))
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 10_000)
    (launcher.ROOT / "logs/stream-32-t7/t7-supervisor.py").write_text("authorized A2 changes")
    with pytest.raises(ValueError, match="changed"):
        _approved(launcher, intent)
    assert launcher.recover("intent.json", invocation["token"]) == 4
    ledger = launcher.read_json(path)
    receipt = launcher.read_json(Path(invocation["receipt_path"]))
    assert ledger["state"] == "RECONCILIATION_REQUIRED"
    assert ledger["cpu_reserved_seconds"] == 0
    assert receipt["intent_sha256"] == approved["intent_sha256"]
    assert receipt["cpu_measured_seconds"] == (1.165511 if proof == "valid" else None)
    charge = 2 if proof == "valid" else 3600 if proof == "foreign-boot" else 10_000
    assert receipt["cpu_charged_seconds"] == ledger["cpu_charged_seconds"] == charge
    launcher.verify_receipts(ledger, path)


def test_reconciliation_migrates_intent_with_unchanged_receipt(launcher, intent, monkeypatch):
    approved = _approved(launcher, intent)
    invocation = launcher.reserve(approved, 1)
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
    assert launcher.settle(approved, invocation["token"], crashed=True) == 4
    path = approved["paths"]["ledger"]
    before = launcher.read_json(path)
    receipt = Path(invocation["receipt_path"])
    receipt_sha = _sha(receipt)
    new = {**approved, "intent_sha256": "e" * 64, "approval_sha256": "f" * 64, "intent_path": "new-intent.json"}
    (launcher.ROOT / new["intent_path"]).write_bytes((launcher.ROOT / "intent.json").read_bytes())
    authority = _resume_file(launcher, approved, before, reconciliation=True)
    monkeypatch.setattr(launcher, "preflight", lambda *args, **kwargs: new)
    with pytest.raises(ValueError, match="authority"):
        launcher.reconcile(new["intent_path"], authority)
    assert launcher.read_json(path) == before
    authority = _resume_file(launcher, approved, before, reconciliation=True, next_intent=new["intent_sha256"])
    assert launcher.reconcile(new["intent_path"], authority) == 0
    after = launcher.read_json(path)
    assert after["state"] == "RECONCILED"
    assert after["intent_sha256"] == new["intent_sha256"]
    assert after["invocations"][0]["intent_sha256"] == approved["intent_sha256"]
    launcher.verify_receipts(after, path)
    assert _sha(receipt) == receipt_sha
    admitted = launcher.reserve(new, 1, resume=True, resume_authority=authority)
    assert admitted["token"] != invocation["token"]
    assert admitted["intent_sha256"] == new["intent_sha256"]
    assert launcher.read_json(path)["cpu_charged_seconds"] == before["cpu_charged_seconds"]


@pytest.mark.parametrize("staging_exists", [False, True])
def test_continuous_retry_only_passes_resume_for_existing_staging(launcher, intent, monkeypatch, staging_exists):
    approved = _approved(launcher, intent)
    invocation = launcher.reserve(approved, 1)
    invocation["resume"] = True
    if staging_exists:
        approved["paths"]["staging"].mkdir(parents=True)
    monkeypatch.setattr(launcher, "_load_running", lambda *args: (approved, invocation))
    monkeypatch.setattr(launcher, "_require_cgroup", lambda *args: None)
    monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"])
    monkeypatch.setattr(launcher.os, "chdir", lambda path: None)
    commands = []
    monkeypatch.setattr(launcher.os, "execvpe", lambda executable, argv, env: commands.append(argv))
    launcher.worker("intent.json", invocation["token"])
    assert len(commands) == 1
    assert ("--resume" in commands[0]) is staging_exists


def test_worker_explicitly_closes_lock_and_uses_local_python(tmp_path):
    script = SOURCE.with_name("t7-worker.sh")
    assert script.is_file(), "A2 worker wrapper has not been implemented"
    source = script.read_text(encoding="utf-8")
    assert "9>&-" in source and ".venv/bin/python" in source
    assert "Trading/bin/python" not in source
    folder = tmp_path / "logs/stream-32-t7"
    folder.mkdir(parents=True)
    worker = folder / script.name
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    probe = folder / SOURCE.name
    probe.write_text(
        "import errno, os, sys\n"
        "assert sys.argv[1:] == ['worker', 'neutral-fixture']\n"
        "try:\n"
        "    os.fstat(9)\n"
        "except OSError as exc:\n"
        "    assert exc.errno == errno.EBADF\n"
        "else:\n"
        "    raise AssertionError('FD 9 leaked into the worker')\n",
        encoding="utf-8",
    )
    lock = tmp_path / "local.lock"
    lock.touch()
    command = ["bash", "-ec", 'exec 9<"$1"; flock -n 9; exec bash "$2" neutral-fixture', "fixture", str(lock), str(worker)]
    worker.write_text(source.replace("9>&-", ""), encoding="utf-8")
    leaky = subprocess.run(command, capture_output=True, text=True, timeout=5)
    assert leaky.returncode == 1 and "FD 9 leaked" in leaky.stderr
    worker.write_text(source, encoding="utf-8")
    closed = subprocess.run(command, capture_output=True, text=True, timeout=5)
    assert closed.returncode == 0, closed.stderr


def test_native_launcher_has_no_inherited_scientific_authority():
    assert SOURCE.is_file(), "A2 isolated launcher has not been implemented"
    source = SOURCE.read_text(encoding="utf-8")
    expected_lock = Path.home() / "JEPA-Drift-experiments/logs/.jepa_execution.lock"
    assert str(expected_lock) in source
    assert all(value not in source for value in ("364e", "full-gaussian", "MANUAL_FALLBACK_VERIFIED"))


def test_qualification_cases_share_ledger_and_never_share_outputs(launcher, intent):
    continuous = launcher.preflight("intent.json", 1, case="continuous")
    resumed = launcher.preflight("intent.json", 1, case="resumed")
    assert continuous["paths"]["ledger"] == resumed["paths"]["ledger"]
    assert continuous["intent"]["design_id"] == resumed["intent"]["design_id"]
    assert continuous["paths"]["publication"] != resumed["paths"]["publication"]
    assert resumed["paths"]["publication"] == resumed["paths"]["run_root"] / "cases/resumed/publication"
    assert continuous["paths"]["staging"] != resumed["paths"]["staging"]
    with pytest.raises(ValueError):
        launcher.run_paths("pilot", intent["design_id"], case="continuous")


def test_qualification_case_plan_is_exact_and_in_the_approval(launcher, intent):
    original = launcher.approval_sha(intent)
    intent["qualification_cases"]["resumed"]["stop_after"] = "HOLD"
    assert launcher.approval_sha(intent) != original
    _save(launcher, intent)
    with pytest.raises(ValueError):
        launcher.preflight("intent.json", 1, case="resumed")


def _finish_controlled(launcher, approved, invocation, monkeypatch, paused=False):
    _sample(launcher, approved, invocation, result="exit-code" if paused else "success", status="2" if paused else "0")
    status = approved["paths"]["staging"] / "status.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(json.dumps({"design_id": approved["intent"]["design_id"],
                                  "status": "BLOCKED_RESOURCE" if paused else "PUBLISHED", "last_complete_phase": "CAL"}), encoding="utf-8")
    monkeypatch.setattr(launcher.time, "monotonic", lambda: invocation["started_monotonic"] + 1)
    return launcher.settle(approved, invocation["token"])


def test_qualification_cases_reuse_cumulative_debits_and_committed_prefixes(launcher, intent, monkeypatch):
    continuous = launcher.preflight("intent.json", 1, case="continuous")
    resumed = launcher.preflight("intent.json", 1, case="resumed")
    monkeypatch.setattr(launcher, "inventory", lambda approved: {"case.txt": approved["case"]})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        first = launcher.reserve(continuous, 1)
        with pytest.raises(ValueError):
            launcher.reserve(resumed, 1)
        assert _finish_controlled(launcher, continuous, first, monkeypatch) == 0
        receipt_sha = _sha(Path(first["receipt_path"]))
        with pytest.raises(ValueError):
            launcher.reserve(continuous, 1)
        second = launcher.reserve(resumed, 1)
        assert second["case"] == "resumed" and second["stop_after"] == "CAL"
        assert _finish_controlled(launcher, resumed, second, monkeypatch, paused=True) == 2
        ledger = launcher.read_json(resumed["paths"]["ledger"])
        assert ledger["cpu_charged_seconds"] == 2
        with pytest.raises(ValueError):
            launcher.reserve(continuous, 1)
        authority = _resume_file(launcher, resumed, ledger)
        with pytest.raises(ValueError):
            launcher.reserve(resumed, 1, resume=True, resume_authority=authority)
        third = launcher.reserve(resumed, 2, resume=True, resume_authority=authority)
        assert third["case"] == "resumed" and third["stop_after"] is None
        assert _finish_controlled(launcher, resumed, third, monkeypatch) == 0
        final = launcher.read_json(resumed["paths"]["ledger"])
        assert final["cpu_charged_seconds"] == 3
        assert [row["case"] for row in final["invocations"]] == ["continuous", "resumed", "resumed"]
        assert _sha(Path(first["receipt_path"])) == receipt_sha
        launcher.verify_receipts(final, resumed["paths"]["ledger"])
        with pytest.raises(ValueError):
            launcher.reserve(resumed, 1)


def test_qualification_rejects_second_case_before_first_and_foreign_case_files(launcher, intent, monkeypatch):
    resumed = launcher.preflight("intent.json", 1, case="resumed")
    with launcher.execution_lock(), pytest.raises(ValueError):
        launcher.reserve(resumed, 1)
    assert not resumed["paths"]["ledger"].exists()
    continuous = launcher.preflight("intent.json", 1, case="continuous")
    monkeypatch.setattr(launcher, "inventory", lambda approved: {})
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        first = launcher.reserve(continuous, 1)
        assert _finish_controlled(launcher, continuous, first, monkeypatch) == 0
        resumed["paths"]["case_root"].mkdir(parents=True)
        (resumed["paths"]["case_root"] / "foreign.txt").write_text("foreign", encoding="utf-8")
        with pytest.raises(ValueError):
            launcher.reserve(resumed, 1)


def test_completed_case_inventory_is_checked_before_the_next_case(launcher, intent, monkeypatch):
    continuous = launcher.preflight("intent.json", 1, case="continuous")
    resumed = launcher.preflight("intent.json", 1, case="resumed")
    observed = {"continuous": {"prefix": "original"}, "resumed": {}}
    monkeypatch.setattr(launcher, "inventory", lambda approved: copy.deepcopy(observed[approved["case"]]))
    monkeypatch.setattr(launcher, "observe_scope", _observation)
    with launcher.execution_lock():
        first = launcher.reserve(continuous, 1)
        assert _finish_controlled(launcher, continuous, first, monkeypatch) == 0
        observed["continuous"]["prefix"] = "changed"
        with pytest.raises(ValueError, match="inventory|prefix"):
            launcher.reserve(resumed, 1)
    assert len(launcher.read_json(continuous["paths"]["ledger"])["invocations"]) == 1


def test_cal_stop_uses_committed_native_prefix_and_leaves_cal_bytes_unchanged(tmp_path):
    spec = importlib.util.spec_from_file_location("t7_guard_fixture", SOURCE.with_name("t7-wall-guard.py"))
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    cal_path = tmp_path / "phases/CAL.json"
    events = []

    class ResourceStop(Exception):
        pass

    def cal(cfg, mode, context):
        cal_path.parent.mkdir()
        cal_path.write_text("committed CAL\n", encoding="utf-8")
        events.append("CAL_COMMITTED")
        return {"phase": "CAL"}

    def progress(staging, did, desc, plan, output):
        assert cal_path.read_text(encoding="utf-8") == "committed CAL\n"
        events.append("PREFIX_VERIFIED")
        return {"SETUP": {}, "DEV": {}, "CAL": {}}, [{"phase": "HOLD", "key": ["neutral"]}]

    def write(path, text):
        events.append("STATUS_COMMITTED")
        path.write_text(text, encoding="utf-8")

    producer = SimpleNamespace(require_budget=lambda *args: None, _score_requests=lambda *args: None,
                               cal_phase=cal, _staged_design=lambda staging: ("neutral", {}),
                               _planned_progress=progress, _write_atomic=write, ResourceBlocked=ResourceStop,
                               pdb=SimpleNamespace(canon=lambda value: json.dumps(value, sort_keys=True)))
    guard.install(producer, 10000, 30, stop_after="CAL")
    with pytest.raises(ResourceStop, match="CAL"):
        producer.cal_phase({}, "smoke", {"staging": tmp_path, "plan": {}})
    assert events == ["CAL_COMMITTED", "PREFIX_VERIFIED", "STATUS_COMMITTED"]
    assert cal_path.read_text(encoding="utf-8") == "committed CAL\n"
    assert json.loads((tmp_path / "status.json").read_bytes())["last_complete_phase"] == "CAL"


def test_qualification_resume_disables_the_cal_stop(tmp_path):
    spec = importlib.util.spec_from_file_location("t7_guard_resume_fixture", SOURCE.with_name("t7-wall-guard.py"))
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    original = lambda cfg, mode, context: "verified existing CAL"
    producer = SimpleNamespace(require_budget=lambda *args: None, _score_requests=lambda *args: None, cal_phase=original)
    guard.install(producer, 10000, 30, stop_after=None)
    assert producer.cal_phase is original
    assert producer.cal_phase({}, "smoke", {"staging": tmp_path}) == "verified existing CAL"
