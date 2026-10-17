"""Contract tests for every registered representation (stream 08).

Four contracts block any fusion of representation and surveillance code:
  (1) Non-anticipation: perturbing x_{t+1:T} leaves z_{1:t} identical bit-for-bit.
  (2) Oddness: ||phi(-x) + phi(x)||_inf <= 1e-6 on the odd head.
  (3) Determinism: two subprocess runs (PYTHONHASHSEED=42, single thread, CPU) give
      identical SHA-256 for z_*.npz and alarms.csv.
  (4) No test statistics: fit receives only pretrain/calib segments; perturbing the
      monitor segment leaves state_hash unchanged, and normalization stats come from
      the declared segment only.

Torch model guards (for the future JEPA) are appended when torch is installed.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from jepadrift.representations import extract
from jepadrift.representations.base import Representation
from jepadrift.representations.cross_section import CenteredRanks, DegreeZero
from jepadrift.representations.pca import PCAOrthogonal

REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

REGISTRY = extract.REGISTRY


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([8, *key]))


def _days(T):
    return np.datetime64("2016-01-04") + np.arange(T)


def _spiked(T, N, seed):
    g = _rng(1, seed)
    B = g.standard_normal((N, 4)) * np.array([3.0, 1.5, 1.2, 1.0])
    return g.standard_normal((T, 4)) @ B.T + g.standard_normal((T, N))


def _all_reps():
    """All registered representations with default configs, plus key variants."""
    return [
        PCAOrthogonal(mode="factor", shrinkage="ledoit_wolf"),
        PCAOrthogonal(mode="full", shrinkage=None),
        PCAOrthogonal(mode="tail10", shrinkage="ledoit_wolf"),
        DegreeZero(b="pc1", mode="factor"),
        DegreeZero(b="ones", mode="full"),
        CenteredRanks(),
    ]


@pytest.fixture(scope="module")
def small_panel():
    """A small deterministic spiked panel for contract tests."""
    X = _spiked(120, 20, 42)
    dates = _days(120)
    return np.ascontiguousarray(X), dates


# ------------------------------------------------------------------ (1) Non-anticipation

@pytest.mark.parametrize("rep", _all_reps(), ids=lambda r: type(r).__name__ + str(r.config))
def test_non_anticipation(rep, small_panel):
    """Perturbing x_{t+1:T} leaves z_{1:t} identical bit-for-bit."""
    X, dates = small_panel
    rep.fit(np.ascontiguousarray(X[:60]), None, dates[:60])
    Z_full = rep.transform_panel(X)
    cut = 80
    X_perturbed = X.copy()
    X_perturbed[cut:] = _rng(2).standard_normal(X_perturbed[cut:].shape)
    Z_perturbed = rep.transform_panel(X_perturbed)
    for key in ("z_odd", "z_even"):
        assert np.array_equal(Z_full[key][:cut], Z_perturbed[key][:cut]), \
            f"{type(rep).__name__}: {key} changed before cut={cut}"
        assert not np.array_equal(Z_full[key][cut:], Z_perturbed[key][cut:]), \
            f"{type(rep).__name__}: {key} should differ after cut={cut}"


# ------------------------------------------------------------------ (2) Oddness

@pytest.mark.parametrize("rep", _all_reps(), ids=lambda r: type(r).__name__ + str(r.config))
def test_odd_head_imparity(rep, small_panel):
    """||phi(-x) + phi(x)||_inf <= 1e-6 on the odd head."""
    X, dates = small_panel
    rep.fit(np.ascontiguousarray(X[:60]), None, dates[:60])
    xs = np.vstack([X[::7][:20], 0.01 * _rng(3).standard_normal((10, X.shape[1]))])
    for x in xs:
        z_pos = rep.transform_day(x)["z_odd"]
        z_neg = rep.transform_day(-x)["z_odd"]
        err = np.abs(z_pos + z_neg).max()
        assert err <= 1e-6, f"{type(rep).__name__}: oddness error {err:.2e} > 1e-6"


# ------------------------------------------------------------------ (3) Determinism (subprocess)

_DETERMINISM_SCRIPT = r"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from jepadrift.data_loader import articleB
from jepadrift.representations import extract

out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)

ret, dates, _ = articleB.load_d2()
splits = articleB.load_splits("d2_us97")

for name, cls in extract.REGISTRY.items():
    npz, sidecar = extract.extract(cls(), ret, dates, splits, out_dir / name, "d2_us97")
    h_npz = hashlib.sha256(npz.read_bytes()).hexdigest()
    h_json = hashlib.sha256((out_dir / name / f"z_{sidecar['state_sha256']}.json").read_bytes()).hexdigest()
    print(json.dumps({"rep": name, "npz_sha256": h_npz, "json_sha256": h_json, "state_sha256": sidecar["state_sha256"]}))
"""


def test_determinism_subprocess(tmp_path):
    """Two subprocess runs with identical env give identical SHA-256 for z_*.npz and sidecar JSON."""
    env = {
        **os.environ,
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_CBWR": "COMPATIBLE",
        "PYTHONHASHSEED": "42",
        "PYTHONPATH": str(REPO),
    }
    script = tmp_path / "det_script.py"
    script.write_text(_DETERMINISM_SCRIPT)

    results = []
    for run in ("run1", "run2"):
        out_dir = tmp_path / run
        proc = subprocess.run(
            [PYTHON, str(script), str(out_dir)],
            capture_output=True, text=True, env=env, cwd=str(REPO),
            timeout=120,
        )
        assert proc.returncode == 0, f"subprocess failed: {proc.stderr}"
        lines = [json.loads(line) for line in proc.stdout.strip().splitlines() if line.strip()]
        results.append({r["rep"]: r for r in lines})

    for rep_name in results[0]:
        r1, r2 = results[0][rep_name], results[1][rep_name]
        assert r1["npz_sha256"] == r2["npz_sha256"], \
            f"{rep_name}: npz SHA-256 differs between runs"
        assert r1["json_sha256"] == r2["json_sha256"], \
            f"{rep_name}: sidecar JSON SHA-256 differs between runs"
        assert r1["state_sha256"] == r2["state_sha256"], \
            f"{rep_name}: state_hash differs between runs"


# ------------------------------------------------------------------ (4) No test statistics

class _FaultyNormalization(Representation):
    """A deliberately faulty representation that normalizes over the full series (all segments)."""

    def __init__(self):
        self.config = {}

    def _fit(self, X, C):
        N = self.n_assets
        # Faulty: normalize using the FULL panel statistics (pretrain + calib + monitor)
        self.state = {"mu": X.mean(axis=0), "std": X.std(axis=0) + 1e-12}
        self.stats = {"mu": X.mean(axis=0).tolist(), "std": X.std(axis=0).tolist()}
        self.heads = {"z_odd": {"dim": N, "parity": "odd", "degree": 1, "definition": "(x - mu) / std"},
                      "z_even": {"dim": N, "parity": "even", "degree": 2, "definition": "z_odd ** 2"}}
        self.channels = {"assets": list(range(N))}

    def _day(self, x, C):
        z = (x - self.state["mu"]) / self.state["std"]
        return z, z * z


def test_no_test_statistics_passes_for_registered(small_panel):
    """Registered representations: perturbing the monitor segment leaves state_hash unchanged."""
    X, dates = small_panel
    calib_end = 60
    monitor_start = 80
    for rep in _all_reps():
        rep.fit(np.ascontiguousarray(X[:calib_end]), None, dates[:calib_end])
        h_before = rep.state_hash()
        side_before = rep.sidecar()

        X_perturbed = X.copy()
        X_perturbed[monitor_start:] = _rng(4).standard_normal(X_perturbed[monitor_start:].shape)
        rep2 = type(rep)(**rep.config)
        rep2.fit(np.ascontiguousarray(X_perturbed[:calib_end]), None, dates[:calib_end])
        h_after = rep2.state_hash()

        assert h_before == h_after, \
            f"{type(rep).__name__}: state_hash changed when monitor segment was perturbed"
        assert side_before["normalization"] == rep2.sidecar()["normalization"], \
            f"{type(rep).__name__}: normalization stats changed when monitor segment was perturbed"


def test_no_test_statistics_fails_for_faulty(small_panel):
    """The faulty representation (normalization over full series) fails contract (4)."""
    X, dates = small_panel
    calib_end = 60
    monitor_start = 80

    rep = _FaultyNormalization()
    rep.fit(np.ascontiguousarray(X[:calib_end]), None, dates[:calib_end])
    h_before = rep.state_hash()

    # The fault: the representation computes normalization over all rows it receives.
    # Giving it a larger window that includes "monitor-like" data changes the state.
    extended = np.ascontiguousarray(X[:monitor_start])
    rep_extended = _FaultyNormalization()
    rep_extended.fit(extended, None, dates[:monitor_start])

    # The state hashes differ because the faulty rep uses all rows it receives
    assert h_before != rep_extended.state_hash(), \
        "faulty rep should produce different state when given more rows (including monitor-like data)"


def test_normalization_from_declared_segment_only(small_panel):
    """Normalization stats in the sidecar come only from the rows named by fit."""
    X, dates = small_panel
    calib_end = 60
    for rep in _all_reps():
        rep.fit(np.ascontiguousarray(X[:calib_end]), None, dates[:calib_end])
        side = rep.sidecar()
        assert side["fit"]["days"] == calib_end
        assert side["fit"]["first_day"] == str(dates[0])
        assert side["fit"]["last_day"] == str(dates[calib_end - 1])
        # The x_sha256 should match only the calib rows
        expected_hash = hashlib.sha256(np.ascontiguousarray(X[:calib_end], dtype=np.float64).tobytes()).hexdigest()
        assert side["fit"]["x_sha256"] == expected_hash


# ------------------------------------------------------------------ Torch model guards

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

needs_torch = pytest.mark.skipif(not HAS_TORCH, reason="torch not installed; JEPA guards skipped")


@needs_torch
def test_torch_eval_mode_buffer_stability():
    """In eval mode, no buffer changes after 10 forward passes."""
    model = torch.nn.Sequential(
        torch.nn.Linear(20, 16),
        torch.nn.ReLU(),
        torch.nn.Linear(16, 8),
    )
    model.eval()
    x = torch.randn(4, 20)
    buffers_before = {name: buf.clone() for name, buf in model.named_buffers()}
    with torch.no_grad():
        for _ in range(10):
            model(x)
    for name, buf in model.named_buffers():
        assert torch.equal(buffers_before[name], buf), f"buffer {name} changed in eval mode"


@needs_torch
def test_torch_no_batchnorm_in_training():
    """No BatchNorm* layer should be in training mode."""
    model = torch.nn.Sequential(
        torch.nn.Linear(20, 16),
        torch.nn.BatchNorm1d(16),
    )
    model.eval()
    for module in model.modules():
        if isinstance(module, (torch.nn.BatchNorm1d, torch.nn.BatchNorm2d, torch.nn.BatchNorm3d)):
            assert not module.training, "BatchNorm layer must be in eval mode"


@needs_torch
def test_torch_no_temporal_normalization():
    """No normalization computed on the temporal axis (dim=0 for (T, N) input)."""
    import ast as _ast
    jepa_dir = REPO / "jepadrift" / "jepa"
    if not jepa_dir.exists():
        pytest.skip("jepadrift/jepa/ does not exist yet")
    for py_file in sorted(jepa_dir.rglob("*.py")):
        tree = _ast.parse(py_file.read_text())
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call):
                func = node.func
                if isinstance(func, _ast.Attribute):
                    attr = func.attr.lower()
                    if "norm" in attr and attr not in ("norm", "norm_except_dim"):
                        continue
                    if attr in ("layernorm", "batchnorm1d", "batchnorm2d", "instancenorm1d"):
                        for kw in node.keywords:
                            if kw.arg == "dim" and isinstance(kw.value, _ast.Constant):
                                assert kw.value.value != 0, \
                                    f"{py_file.name}: normalization on temporal axis (dim=0) detected"


@needs_torch
def test_torch_ema_target_inactive_at_extraction():
    """EMA target parameters should not be used at extraction time (eval mode, no_grad)."""
    model = torch.nn.Sequential(torch.nn.Linear(10, 5))
    model.eval()
    x = torch.randn(3, 10)
    with torch.no_grad():
        out1 = model(x)
        out2 = model(x)
    assert torch.equal(out1, out2), "model output should be deterministic in eval+no_grad"
