"""Tests of the shared drift statistics (stream 8b): jepadrift/stats/drift.py, moved verbatim from the audit."""
import ast
import hashlib
from pathlib import Path

import numpy as np
import pytest

from experiments import audit_information as au
from jepadrift.stats import drift

REPO = Path(__file__).resolve().parents[1]
MOVED_SOURCE_SHA256 = {
    "WINDOW": "0c844c3c224e9ce1bb1e3969a9c69a318f3629e5fb4fa67561319a6b53d90353",
    "MIN_PHASE": "d527a3630b588186eda1840fb1b7947dc9883548009ff695e5aaaf274a43696a",
    "BLOCK": "612bf35d83c8534044ee64c1b697949afb3d19dfe4dc5b6ccd3d72293ff35cac",
    "transitions": "4708587fad45a2170495209d4d4c4f44131ee13baa2ed54aad993a9831c79f0e",
    "_sr2": "1381bb3d67dbfbc22ce4448ea40f238c654e0a12261ee5db72ebaf3173f3a7f0",
    "debiased_sr2": "1d1e7c512c00317c5fda51ffe81aa3dea5401d0628902c30eb5ca2895052e210",
    "mbb_indices": "ff28cd7c126afc2d296566c0aa6ef31883e228d326de0052266bd01a4e94199f",
    "shifted_percentile_ci": "2008d9bb52fed1c21bf3b238e4b7c28a52f48c0d043d191c85c7b8756c6b8f2d",
    "rotate_phases": "2f3d1ae483fb59dd5252fb81a0fb5175eac672366f0e5fb706a037c7ded3585f",
}
AUDIT_NAMES = {"shifted_percentile_ci": "_ci"}


def _top_level(src):
    nodes = {}
    for node in ast.parse(src).body:
        name = getattr(node.targets[0], "id", None) if isinstance(node, ast.Assign) else getattr(node, "name", None)
        if name is not None:
            nodes[name] = node
    return nodes


def test_moved_segments_unchanged():
    src = (REPO / "jepadrift" / "stats" / "drift.py").read_text()
    found = {}
    for name, node in _top_level(src).items():
        if name in MOVED_SOURCE_SHA256:
            segment = ast.get_source_segment(src, node)
            segment = segment.replace(f"def {name}(", f"def {AUDIT_NAMES.get(name, name)}(", 1)
            found[name] = hashlib.sha256(segment.encode()).hexdigest()
    assert found == MOVED_SOURCE_SHA256


def test_audit_reexports_shared_objects():
    for name in MOVED_SOURCE_SHA256:
        assert getattr(au, AUDIT_NAMES.get(name, name)) is getattr(drift, name), name
    defined = set(_top_level((REPO / "experiments" / "audit_information.py").read_text()))
    assert not defined & {AUDIT_NAMES.get(name, name) for name in MOVED_SOURCE_SHA256}


def test_shifted_percentile_ci():
    draws = np.arange(1.0, 101.0)
    assert drift.shifted_percentile_ci(draws, 50.0) == pytest.approx((2.975, 97.025), rel=1e-12)
    assert drift.shifted_percentile_ci(draws, 53.0) == pytest.approx((5.975, 100.025), rel=1e-12)
