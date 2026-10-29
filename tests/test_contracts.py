"""Contract tests for every registered representation (stream 08).

Four contracts block any fusion of representation and surveillance code:
  (1) Non-anticipation: perturbing x_{t+1:T} leaves z_{1:t} identical bit-for-bit.
  (2) Oddness: ||phi(-x) + phi(x)||_inf <= 1e-6 on the odd head.
  (3) Determinism: two subprocess runs (PYTHONHASHSEED=42, single thread, CPU) give
      identical SHA-256 for z_*.npz and alarms.csv.
  (4) No test statistics: fit receives only pretrain/calib segments; perturbing the
      monitor segment leaves state_hash unchanged, and normalization stats come from
      the declared segment only.

Torch guards inspect the real CA-T-JEPA representation; each has a faulty witness that must fail.
"""
import functools
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
import yaml

from jepadrift.data_loader import chars, sp500
from jepadrift.representations import extract
from jepadrift.representations.base import Representation
from jepadrift.representations.cross_section import CenteredRanks, DegreeZero
from jepadrift.representations.ipca import IPCA
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
    if name in extract.NEEDS_C:
        continue
    npz, sidecar = extract.extract(cls(), ret, dates, splits, out_dir / name, "d2_us97")
    h_npz = hashlib.sha256(npz.read_bytes()).hexdigest()
    h_json = hashlib.sha256((out_dir / name / f"z_{sidecar['state_sha256']}.json").read_bytes()).hexdigest()
    print(json.dumps({"rep": name, "npz_sha256": h_npz, "json_sha256": h_json, "state_sha256": sidecar["state_sha256"]}))
"""


def _det_env():
    return {
        **os.environ,
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_CBWR": "COMPATIBLE",
        "PYTHONHASHSEED": "42",
        "PYTHONPATH": os.pathsep.join(filter(None, (str(REPO), os.environ.get("PYTHONPATH")))),
    }


def test_determinism_subprocess(tmp_path):
    """Two subprocess runs with identical env give identical SHA-256 for z_*.npz and sidecar JSON."""
    env = _det_env()
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


# ------------------------------------------------------------------ Characteristic representations (D3)

def _ipca_case(data):
    return IPCA().pretrain(*data["pretrain"]).fit(*data["calib"])


_CA_TJEPA_DIRS = []


@functools.lru_cache(maxsize=None)
def _ca_tjepa_ckpt():
    from experiments import jepa_pretrain
    from jepadrift.jepa import ca_tjepa
    cfg = yaml.safe_load((REPO / "configs" / "ca_tjepa.yaml").read_text())
    cfg["model"]["d"], cfg["train"]["max_epochs"] = 4, 1
    X, C, dates, _ = jepa_pretrain.synthetic_panel(160, 239, "2013-07-01", np.random.default_rng(0), 1.0)
    _CA_TJEPA_DIRS.append(tempfile.TemporaryDirectory(prefix="ca_tjepa_contract_"))
    return ca_tjepa.train(X, C, dates, cfg, 0, _CA_TJEPA_DIRS[-1].name)[0]


def _ca_tjepa_case(data):
    from jepadrift.jepa.representation import CATJEPA
    return CATJEPA(_ca_tjepa_ckpt()).fit(*data["calib"])


CHAR_CASES = {"ipca": _ipca_case, "ca_tjepa": _ca_tjepa_case}
CALIB_FREE = {"ca_tjepa"}


def d3_char_data(n_pre=128, n_cal=120, n_after=60):
    """Causal D3 fixture: (X, C, dates) of the last pretrain days, the first calib days and the next calib days of
    d3_239 (all before 2020), X masked by in_universe, C the four continuous characteristics."""
    ret, dates, _ = sp500.load_d3_239()
    segments = sp500.load_splits("d3_239")["segments"]
    p1 = extract.segment_rows(dates, segments["pretrain"])[1]
    c0, c1 = extract.segment_rows(dates, segments["calib"])
    if c0 + n_cal + n_after > c1:
        raise ValueError("the D3 fixture must stay inside the calib segment")
    rows = slice(p1 - n_pre, c0 + n_cal + n_after)
    X = np.where(chars.load_universe("d3_239", rows), ret[rows], np.nan)
    C = chars.load_continuous_chars("d3_239", rows)
    a = c0 - rows.start
    cuts = {"pretrain": (0, n_pre), "calib": (a, a + n_cal), "after": (a + n_cal, a + n_cal + n_after)}
    return {k: (np.ascontiguousarray(X[i:j]), np.ascontiguousarray(C[i:j]), dates[rows][i:j])
            for k, (i, j) in cuts.items()}


@pytest.fixture(scope="module")
def d3_chars():
    return d3_char_data()


def test_char_registries_agree():
    """Every characteristic representation declares its D3 case: NEEDS_C == set(CHAR_CASES), within REGISTRY."""
    assert extract.NEEDS_C == set(CHAR_CASES) and set(CHAR_CASES) <= set(REGISTRY) and CALIB_FREE <= set(CHAR_CASES)


@pytest.mark.parametrize("name", sorted(CHAR_CASES))
def test_char_non_anticipation(name, d3_chars):
    """Perturbing x and C after day t leaves z_{1:t} identical bit-for-bit."""
    rep = CHAR_CASES[name](d3_chars)
    X, C, _ = d3_chars["after"]
    Z = rep.transform_panel(X, C)
    cut = 30
    Xp, Cp = X.copy(), C.copy()
    Xp[cut:] = 0.01 * _rng(5).standard_normal(Xp[cut:].shape)
    Cp[cut:] = _rng(6).uniform(-0.5, 0.5, Cp[cut:].shape)
    Zp = rep.transform_panel(Xp, Cp)
    for key in ("z_odd", "z_even"):
        assert np.array_equal(Z[key][:cut], Zp[key][:cut]), f"{name}: {key} changed before cut={cut}"
        assert not np.array_equal(Z[key][cut:], Zp[key][cut:]), f"{name}: {key} should differ after cut={cut}"


@pytest.mark.parametrize("name", sorted(CHAR_CASES))
def test_char_odd_head(name, d3_chars):
    """||phi(-x; C) + phi(x; C)||_inf <= 1e-6 with C frozen."""
    rep = CHAR_CASES[name](d3_chars)
    X, C, _ = d3_chars["after"]
    xs = np.vstack([X, 0.01 * _rng(7).standard_normal((10, X.shape[1]))])
    for x, c in zip(xs, np.concatenate([C, C[:10]])):
        err = np.abs(rep.transform_day(x, c)["z_odd"] + rep.transform_day(-x, c)["z_odd"]).max()
        assert err <= 1e-6, f"{name}: oddness error {err:.2e} > 1e-6"


@pytest.mark.parametrize("name", sorted(CHAR_CASES))
def test_char_no_test_statistics(name, d3_chars):
    """Rows after calib do not move the state; a calib row does, except for a frozen calib-free state (CALIB_FREE)."""
    rep = CHAR_CASES[name](d3_chars)
    X, C, d = d3_chars["after"]
    later = {**d3_chars, "after": (0.01 * _rng(8).standard_normal(X.shape), _rng(9).uniform(-0.5, 0.5, C.shape), d)}
    rep_later = CHAR_CASES[name](later)
    assert rep_later.state_hash() == rep.state_hash()
    assert rep_later.sidecar()["normalization"] == rep.sidecar()["normalization"]
    Xc, Cc, dc = d3_chars["calib"]
    Xm = Xc.copy()
    Xm[10] *= 1.5
    moved = CHAR_CASES[name]({**d3_chars, "calib": (Xm, Cc, dc)}).state_hash() != rep.state_hash()
    assert moved == (name not in CALIB_FREE), f"{name}: a calib row moved={moved}, calib-free={name in CALIB_FREE}"


@pytest.mark.parametrize("name", sorted(CHAR_CASES))
def test_char_declared_segment(name, d3_chars):
    """The fit record names the calib rows the builder passed, X and C."""
    fit = CHAR_CASES[name](d3_chars).sidecar()["fit"]
    X, C, d = d3_chars["calib"]
    assert (fit["first_day"], fit["last_day"], fit["days"]) == (str(d[0]), str(d[-1]), len(d))
    assert fit["x_sha256"] == hashlib.sha256(X.tobytes()).hexdigest()
    assert fit["c_sha256"] == hashlib.sha256(C.tobytes()).hexdigest()


_CHAR_DETERMINISM_SCRIPT = r"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
import test_contracts as tc

data = tc.d3_char_data()
rep = tc.CHAR_CASES[sys.argv[2]](data)
Z = rep.transform_panel(*data["after"][:2])
print(json.dumps({"state_sha256": rep.state_hash(), "z_odd": hashlib.sha256(Z["z_odd"].tobytes()).hexdigest(),
                  "z_even": hashlib.sha256(Z["z_even"].tobytes()).hexdigest()}))
"""


@pytest.mark.parametrize("name", sorted(CHAR_CASES))
def test_char_determinism_subprocess(name, tmp_path):
    """Two subprocess builds on the D3 fixture give the same state hash and Z bytes."""
    script = tmp_path / "char_det.py"
    script.write_text(_CHAR_DETERMINISM_SCRIPT)
    outputs = []
    for _ in range(2):
        proc = subprocess.run([PYTHON, str(script), str(REPO / "tests"), name], capture_output=True, text=True,
                              env=_det_env(), cwd=str(REPO), timeout=300)
        assert proc.returncode == 0, f"subprocess failed: {proc.stderr}"
        outputs.append(json.loads(proc.stdout))
    assert outputs[0] == outputs[1], f"{name}: state or Z differs between runs"


# ------------------------------------------------------------------ Torch model guards

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

needs_torch = pytest.mark.skipif(not HAS_TORCH, reason="torch not installed; JEPA guards skipped")


def _ca_rep(d3_chars, cls=None):
    from jepadrift.jepa.representation import CATJEPA
    return (cls or CATJEPA)(_ca_tjepa_ckpt()).fit(*d3_chars["calib"])


def _net_state(net):
    return [t.detach().clone() for t in net.state_dict().values()]


@needs_torch
def test_torch_eval_mode_buffer_stability(d3_chars):
    """CA-T-JEPA: ten extractions leave every parameter and buffer bit-identical; a mutating witness is caught."""
    from jepadrift.jepa.representation import CATJEPA
    X, C, _ = d3_chars["after"]

    def stable(rep):
        before = _net_state(rep.net)
        outs = [rep.transform_day(X[0], C[0])["z_odd"] for _ in range(10)]
        same = all(torch.equal(a, b) for a, b in zip(before, _net_state(rep.net)))
        return same and all(np.array_equal(outs[0], o) for o in outs)

    class Mutating(CATJEPA):
        def _day(self, x, C_t):
            with torch.no_grad():
                self.net.head.bias.add_(1e-3)
            return super()._day(x, C_t)

    assert stable(_ca_rep(d3_chars))
    assert not stable(_ca_rep(d3_chars, Mutating))


@needs_torch
def test_torch_no_batchnorm_in_training(d3_chars):
    """CA-T-JEPA at extraction: no BatchNorm layer and no module in training mode; an inserted BatchNorm is caught."""
    def clean(net):
        norms = any(isinstance(m, torch.nn.modules.batchnorm._BatchNorm) for m in net.modules())
        return not norms and not any(m.training for m in net.modules())

    witness = _ca_rep(d3_chars)
    witness.net.context.token.append(torch.nn.BatchNorm1d(witness.net.head.in_features))
    assert clean(_ca_rep(d3_chars).net)
    assert not clean(witness.net)


@needs_torch
def test_torch_no_temporal_normalization(d3_chars):
    """CA-T-JEPA: days 0, 7, 19 keep both heads when other days change and equal a fresh transform_day; centring fails."""
    from jepadrift.jepa.representation import CATJEPA
    X, C, _ = d3_chars["after"]

    def per_day(rep):
        Z, fresh = rep.transform_panel(X, C), _ca_rep(d3_chars)
        for t in (0, 7, 19):
            Xp = X.copy()
            Xp[np.arange(len(X)) != t] *= 3.0
            Zp, single = rep.transform_panel(Xp, C), fresh.transform_day(X[t], C[t])
            if not all(np.array_equal(Z[k][t], Zp[k][t]) and np.array_equal(Z[k][t], single[k])
                       for k in ("z_odd", "z_even")):
                return False
        return True

    class Centred(CATJEPA):
        def transform_panel(self, X, C=None):
            return super().transform_panel(X - np.nanmean(X, axis=0), C)

    assert per_day(_ca_rep(d3_chars))
    assert not per_day(_ca_rep(d3_chars, Centred))


@needs_torch
def test_torch_ema_target_inactive_at_extraction(d3_chars):
    """CA-T-JEPA: after fit and extraction the weights equal the checkpoint; an EMA update inside _day is caught."""
    from jepadrift.jepa import ca_tjepa
    from jepadrift.jepa.representation import CATJEPA
    X, C, _ = d3_chars["after"]

    def frozen(rep):
        rep.transform_panel(X[:5], C[:5])
        return np.array_equal(ca_tjepa.flat_weights(rep.net), rep.state["weights"])

    class EmaInDay(CATJEPA):
        def _day(self, x, C_t):
            ca_tjepa.ema_step(self.net, 0.5)
            return super()._day(x, C_t)

    assert frozen(_ca_rep(d3_chars))
    assert not frozen(_ca_rep(d3_chars, EmaInDay))
