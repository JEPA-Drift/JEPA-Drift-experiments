"""Decoupling tests: AST-based import analysis (stream 08).

Enforces strict import boundaries:
  - jepadrift/monitors/** must not import torch, jepadrift.jepa, or jepadrift.representations
  - jepadrift/jepa/** must not import jepadrift.injection or jepadrift.monitors
  - jepadrift/injection.py must only accept return panels (assert on shape and dtype, refuse Z objects)
"""
import ast
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]


def _imports_of(path):
    """Return the set of fully-qualified module names imported by a Python file."""
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
            for alias in node.names:
                names.add(f"{module}.{alias.name}")
    return names


def _imports_of_dir(directory):
    """Yield (relative_path, import_names) for every .py file under a directory."""
    for py_file in sorted(directory.rglob("*.py")):
        rel = py_file.relative_to(REPO)
        yield rel, _imports_of(py_file)


def _has_forbidden_import(imports, forbidden_prefixes):
    """Check whether any import matches a forbidden prefix."""
    for imp in imports:
        for prefix in forbidden_prefixes:
            if imp == prefix or imp.startswith(prefix + "."):
                return imp, prefix
    return None


# ------------------------------------------------------------------ monitors isolation

def test_monitors_import_isolation():
    """jepadrift/monitors/** must not import torch, jepadrift.jepa, or jepadrift.representations."""
    forbidden = ("torch", "jepadrift.jepa", "jepadrift.representations")
    monitors_dir = REPO / "jepadrift" / "monitors"
    violations = []
    for rel, imports in _imports_of_dir(monitors_dir):
        hit = _has_forbidden_import(imports, forbidden)
        if hit:
            violations.append((str(rel), hit[0], hit[1]))
    assert not violations, f"monitors import violations: {violations}"


# ------------------------------------------------------------------ jepa isolation

def test_jepa_import_isolation():
    """jepadrift/jepa/** must not import jepadrift.injection or jepadrift.monitors."""
    jepa_dir = REPO / "jepadrift" / "jepa"
    if not jepa_dir.exists() or not list(jepa_dir.rglob("*.py")):
        pytest.skip("jepadrift/jepa/ has no Python files yet")
    forbidden = ("jepadrift.injection", "jepadrift.monitors")
    violations = []
    for rel, imports in _imports_of_dir(jepa_dir):
        hit = _has_forbidden_import(imports, forbidden)
        if hit:
            violations.append((str(rel), hit[0], hit[1]))
    assert not violations, f"jepa import violations: {violations}"


# ------------------------------------------------------------------ representations isolation (already tested in test_representations.py)

def test_representations_import_isolation():
    """jepadrift/representations/** must not import jepadrift.monitors, jepadrift.injection, or torch."""
    forbidden = ("torch", "jepadrift.monitors", "jepadrift.injection")
    rep_dir = REPO / "jepadrift" / "representations"
    violations = []
    for rel, imports in _imports_of_dir(rep_dir):
        hit = _has_forbidden_import(imports, forbidden)
        if hit:
            violations.append((str(rel), hit[0], hit[1]))
    assert not violations, f"representations import violations: {violations}"


# ------------------------------------------------------------------ injection: panel-only contract

def test_injection_accepts_only_return_panels():
    """jepadrift/injection.py must assert on shape and dtype, and refuse Z objects."""
    from jepadrift import injection

    # A valid 2-D float64 panel should pass
    X = np.zeros((10, 5), dtype=np.float64)
    injection.symmetrize(X, np.random.default_rng(0))  # should not raise

    # A Z object (dict) should be refused with TypeError
    Z = {"z_odd": np.zeros((10, 3)), "z_even": np.zeros((10, 3))}
    with pytest.raises(TypeError):
        injection.symmetrize(Z, np.random.default_rng(0))

    # A list should be refused
    with pytest.raises(TypeError):
        injection.symmetrize(X.tolist(), np.random.default_rng(0))

    # Wrong dtype (float32) should be refused
    with pytest.raises(ValueError):
        injection.symmetrize(X.astype(np.float32), np.random.default_rng(0))

    # 1-D array should be refused
    with pytest.raises(ValueError):
        injection.symmetrize(X[:, 0], np.random.default_rng(0))

    # 3-D array should be refused
    with pytest.raises(ValueError):
        injection.symmetrize(X.reshape(5, 2, 5), np.random.default_rng(0))


def test_injection_fit_background_rejects_z():
    """fit_background must also refuse Z-like inputs."""
    from jepadrift import injection

    Z = {"z_odd": np.zeros((10, 3))}
    with pytest.raises(TypeError):
        injection.fit_background(Z, 1)

    with pytest.raises(ValueError):
        injection.fit_background(np.zeros((10, 5), dtype=np.float32), 1)


# ------------------------------------------------------------------ AST source check for injection

def test_injection_source_has_panel_assertions():
    """The injection module source must contain explicit shape and dtype assertions."""
    src = (REPO / "jepadrift" / "injection.py").read_text()
    assert "isinstance" in src and "np.ndarray" in src, \
        "injection.py must assert isinstance(x, np.ndarray)"
    assert "ndim" in src and "float64" in src, \
        "injection.py must assert on ndim and dtype"
    assert "latent Z" in src or "Z objects" in src, \
        "injection.py must explicitly refuse Z objects"
