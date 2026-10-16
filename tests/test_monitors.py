"""Unit and Monte Carlo tests for jepadrift.monitors and jepadrift.stats (pytest)."""
import ast
import itertools
from pathlib import Path

import numpy as np
import pytest
from scipy.signal import lfilter
from scipy.stats import binom

from experiments.e2_floor_validation import Garch
from jepadrift.monitors import cusum, eprocess, gamma, lattice, streams
from jepadrift.stats import garch


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([4, *key]))


def _cusum_streams():
    rng = _rng(1)
    label = (rng.random((50, 400)) > 0.45).astype(float) - 0.55
    sign = np.where(rng.random((50, 400)) < 0.5, 0.5, -0.5)
    energy = (rng.standard_normal((50, 400)) ** 2 - 1.0) / np.sqrt(2.0)
    return {"label": (label, 0.1, 2.0), "sign": (sign, 0.1, 2.0), "energy": (energy, 0.5, 3.0)}


# ------------------------------------------------------------------ cusum

def test_vectorized_cusum_matches_scalar_ports():
    for x, delta, thr in _cusum_streams().values():
        traj = cusum.cusum_trajectory_vec(x, delta)
        first = cusum.strict_cusum_vec(x, delta, thr)
        bil = cusum.bilateral_delay_vec(x, delta, thr)
        peak = cusum.cusum_max_bilateral_vec(x, delta)
        uni = cusum.multiple_alarms_vec(x, delta, thr)
        two = cusum.multiple_alarms_vec(x, delta, thr, bilateral=True)
        assert first.shape == bil.shape == peak.shape == (50,) and first.dtype == np.int64
        assert (first >= 0).any() and (bil >= 0).any()
        assert max(int(a.sum()) for a in two) > 1
        for i in range(x.shape[0]):
            assert np.array_equal(traj[i], cusum.get_cusum_trajectory(x[i], delta))
            assert first[i] == cusum.strict_cusum(x[i], delta, thr)
            assert bil[i] == cusum.bilateral_delay(x[i], delta, thr)
            assert peak[i] == cusum.cusum_max_bilateral(x[i], delta)
            assert np.flatnonzero(uni[i]).tolist() == cusum.get_multiple_alarms(x[i], delta, thr)
            assert (np.flatnonzero(two[i]).tolist()
                    == cusum.get_multiple_alarms(x[i], delta, thr, bilateral=True))
        assert (cusum.strict_cusum_vec(x, delta, 1e9) == -1).all()
        assert cusum.strict_cusum_vec(x[0], delta, thr) == cusum.strict_cusum(x[0], delta, thr)


def test_vectorized_cusum_rejects_nan():
    x = np.zeros((2, 5))
    x[1, 3] = np.nan
    calls = (lambda: cusum.cusum_trajectory_vec(x, 0.1),
             lambda: cusum.strict_cusum_vec(x, 0.1, 1.0),
             lambda: cusum.bilateral_delay_vec(x, 0.1, 1.0),
             lambda: cusum.cusum_max_bilateral_vec(x, 0.1),
             lambda: cusum.multiple_alarms_vec(x, 0.1, 1.0, bilateral=True))
    for call in calls:
        with pytest.raises(ValueError):
            call()


def test_vectorized_cusum_rejects_empty_streams():
    calls = (lambda: cusum.cusum_trajectory_vec(np.zeros((2, 0)), 0.1),
             lambda: cusum.strict_cusum_vec(np.zeros(0), 0.1, 1.0),
             lambda: cusum.strict_cusum_vec(np.zeros((2, 0)), 0.1, 1.0),
             lambda: cusum.bilateral_delay_vec(np.zeros((2, 0)), 0.1, 1.0),
             lambda: cusum.cusum_max_bilateral_vec(np.zeros((2, 0)), 0.1),
             lambda: cusum.multiple_alarms_vec(np.zeros((2, 0)), 0.1, 1.0, bilateral=True))
    for call in calls:
        with pytest.raises(ValueError, match="at least one observation"):
            call()


def test_p1_constants():
    cb, cc, db = cusum.P1["P1-C/B"], cusum.P1["P1-C/C"], cusum.P1["P1-D/B"]
    assert (cb["stream"], cb["delta"], cb["threshold"], cb["bilateral"]) == ("label", 0.1, 10.0, True)
    assert cb["q_hat_window"] == ("2018-01-02", "2019-12-31") and cb["trailing_days"] == 250
    assert ((cc["stream"], cc["delta"], cc["threshold"], cc["bilateral"], cc["comparison"], cc["rule"])
            == ("exact_sign", 0.1, "lattice", True, "strict", "at_or_below"))
    assert (db["stream"], db["delta"], db["lambda_iid"], db["bilateral"]) == ("energy", 0.5, 65.0, False)
    assert db["gamma_hat_window"] == ("2018-01-02", "2019-12-31") and db["trailing_days"] == 250


# ------------------------------------------------------------------ streams

def test_streams_match_r01_expressions():
    r = _rng(2).standard_normal(500) * 0.01
    r[::50] = 0.0
    q_hat, mu, sigma = 0.55864811133200798, 1.3e-4, 2.1e-4
    assert np.array_equal(streams.label_stream(r, q_hat), (r > 0).astype(float) - q_hat)
    assert np.array_equal(streams.energy_stream(r, mu, sigma), (r**2 - mu) / sigma)


def test_exact_sign_stream_ties_and_determinism():
    y = np.concatenate([np.linspace(-1.0, 1.0, 101), np.zeros(10000)])
    s = streams.exact_sign_stream(y, _rng(3))
    assert s.dtype == np.float64 and np.array_equal(s, streams.exact_sign_stream(y, _rng(3)))
    assert set(np.unique(s).tolist()) == {-0.5, 0.5}
    nz = y != 0
    assert np.array_equal(s[nz], np.where(y[nz] > 0, 0.5, -0.5))
    assert abs((s[~nz] > 0).mean() - 0.5) < 0.02


def test_streams_reject_nan():
    r = np.array([0.01, np.nan])
    for call in (lambda: streams.label_stream(r, 0.5), lambda: streams.energy_stream(r, 0.0, 1.0),
                 lambda: streams.exact_sign_stream(r, _rng(4))):
        with pytest.raises(ValueError):
            call()


# ------------------------------------------------------------------ lattice

def _enumerate_maxima(H, a, b, q):
    out = []
    for bits in itertools.product((0, 1), repeat=H):
        sp = sn = m1 = m2 = 0
        for y in bits:
            sp, sn = (sp + a, max(0, sn - b)) if y else (max(0, sp - b), sn + a)
            m1, m2 = max(m1, sp), max(m2, sp, sn)
        k = sum(bits)
        out.append((m1, m2, q**k * (1 - q) ** (H - k)))
    return out


def test_lattice_steps():
    assert lattice.lattice_steps(0.1) == (2, 3, 0.2)
    assert lattice.lattice_steps(0.0) == (1, 1, 0.5)
    assert lattice.lattice_steps(0.25) == (1, 3, 0.25)
    for bad in (0.5, -0.1, 0.123456789, float("nan")):
        with pytest.raises(ValueError):
            lattice.lattice_steps(bad)


def test_exceedance_matches_enumeration():
    for H in (6, 9):
        for a, b in ((2, 3), (1, 1), (1, 3)):
            for q in (0.5, 0.3):
                paths = _enumerate_maxima(H, a, b, q)
                for L in range(8):
                    for sided in (1, 2):
                        strict = sum(p for m1, m2, p in paths if (m1, m2)[sided - 1] > L)
                        weak = sum(p for m1, m2, p in paths if (m1, m2)[sided - 1] >= L)
                        assert abs(lattice.exceedance(H, L, a, b, q, sided, "strict") - strict) < 1e-14
                        assert abs(lattice.exceedance(H, L, a, b, q, sided, "weak") - weak) < 1e-14
    assert lattice.exceedance(0, 3, 2, 3) == 0.0


def test_arl0_closed_form_and_mc():
    for L in range(11):
        assert abs(lattice.arl0(L, 1, 1, sided=1) / ((L + 1) * (L + 2)) - 1.0) < 1e-12
    for q in (0.5, 0.3):
        assert abs(lattice.arl0(0, 2, 3, q=q, sided=1) - 1.0 / q) < 1e-12
    assert lattice.arl0(0, 2, 3, comparison="weak") == 1.0
    s = np.where(_rng(5).random((20000, 600)) < 0.5, 0.5, -0.5)
    rl = cusum.bilateral_delay_vec(s, 0.1, 2.1) + 1.0
    assert (rl > 0).all()
    assert abs(rl.mean() - lattice.arl0(10, 2, 3, sided=2)) < 4.0 * rl.std() / np.sqrt(rl.size)


def test_select_threshold_r08_bracket():
    sel = lattice.select_threshold(0.05, H=5000, delta=0.1, sided=2)
    assert sel["units"] == 57 and sel["unit"] == 0.2 and abs(sel["lam"] - 11.4) < 1e-12
    assert sel["threshold"] == 57.5 * 0.2 and abs(sel["level"] / 0.043428228893176074 - 1.0) < 1e-12
    above = lattice.select_threshold(0.05, rule="at_or_above", H=5000, delta=0.1, sided=2)
    assert above["units"] == 56 and abs(above["level"] / 0.051020717214682557 - 1.0) < 1e-12
    weak = lattice.select_threshold(0.05, comparison="weak", H=5000, delta=0.1, sided=2)
    assert weak["units"] == 58 and weak["threshold"] == sel["threshold"] and weak["level"] == sel["level"]
    g = lattice.select_threshold(1.0 / 252, delta=0.1, sided=2)
    assert lattice.arl0(g["units"], 2, 3) >= 252 > lattice.arl0(g["units"] - 1, 2, 3)
    with pytest.raises(ValueError):
        lattice.select_threshold(0.05, rule="nearest", H=100)


def test_midpoint_threshold_reproduces_lattice_rule():
    s = np.where(_rng(6).random((4000, 2000)) < 0.5, 0.5, -0.5)
    m = cusum.cusum_max_bilateral_vec(s, 0.1)
    units = np.rint(m / 0.2)
    assert np.abs(m / 0.2 - units).max() < 1e-6
    for comparison in ("strict", "weak"):
        sel = lattice.select_threshold(0.05, comparison=comparison, H=2000, delta=0.1, sided=2)
        expected = units > sel["units"] if comparison == "strict" else units >= sel["units"]
        assert np.array_equal(m > sel["threshold"], expected)


def test_lattice_rejects_non_integer_units():
    for call in (lambda: lattice.exceedance(100, 11.4, 2, 3), lambda: lattice.arl0(11.4, 2, 3),
                 lambda: lattice.exceedance(-1, 5, 2, 3), lambda: lattice.exceedance(10.5, 5, 2, 3)):
        with pytest.raises(ValueError):
            call()

def test_attainable_levels_shape():
    lv = lattice.attainable_levels(H=200, delta=0.1, sided=2)
    assert lv.ndim == 2 and lv.shape[1] == 2
    assert np.allclose(lv[:, 0], 0.2 * np.arange(lv.shape[0]), rtol=0.0, atol=1e-12)
    assert (np.diff(lv[:, 1]) <= 0).all() and lv[-1, 1] <= 1e-3 < lv[-2, 1]
    assert lv[0, 1] == lattice.exceedance(200, 0, 2, 3)
    arl = lattice.attainable_levels(delta=0.1, sided=1)
    assert abs(arl[5, 1] - 1.0 / lattice.arl0(5, 2, 3, sided=1)) < 1e-15


# ------------------------------------------------------------------ garch

def test_compute_gamma_exact_spy():
    assert garch.compute_gamma_exact(0.211551, 0.729081) == 14.998367977816738


# ------------------------------------------------------------------ gamma

def _energy(z):
    return (z**2 - 1.0) / np.sqrt(2.0)


def test_gamma_spectral():
    rng = _rng(7)
    for n, L in ((100, 4), (1000, 6), (5000, 9)):
        x = rng.standard_normal(n)
        assert gamma.gamma_spectral(x) == gamma.gamma_spectral(x, L) != gamma.gamma_spectral(x, L + 1)
    phi, n = 0.5, 200_000
    x = lfilter([1.0], [1.0, -phi], rng.standard_normal(n))
    L = int(np.floor(4 * (n / 100) ** (2 / 9)))
    pop = 1 + 2 * sum((1 - k / (L + 1)) * phi**k for k in range(1, L + 1))
    assert abs(gamma.gamma_spectral(x) / pop - 1) < 0.03
    g = gamma.gamma_spectral(rng.standard_normal((3, 100_000)))
    assert g.shape == (3,) and (np.abs(g - 1) < 0.05).all()


def test_gamma_spectral_rejects_constant_series():
    for x in (np.ones(500), np.ones((3, 500))):
        with pytest.raises(ValueError):
            gamma.gamma_spectral(x)


def test_required_threshold_semantics():
    paths = _energy(_rng(8).standard_normal((2000, 400)))
    traj = cusum.cusum_trajectory_vec(paths, 0.5)

    def fpr(lam):
        return (traj[:, :300].max(axis=1) > lam).mean()

    def arl(lam):
        hit = traj > lam
        return np.where(hit.any(axis=1), hit.argmax(axis=1) + 1, traj.shape[1]).mean()

    lam = gamma.required_threshold(paths, 0.5, 0.05, criterion="fpr", H=300)
    assert fpr(lam) <= 0.05 < fpr(lam - 1e-6)
    lam = gamma.required_threshold(paths, 0.5, 60.0, criterion="arl0")
    assert arl(lam) >= 60.0 > arl(lam - 1e-6)
    with pytest.raises(ValueError):
        gamma.required_threshold(paths, 0.5, 0.05, criterion="median")


def test_gamma_operational():
    rng = _rng(9)
    iid, ref = _energy(rng.standard_normal((4000, 500))), _energy(rng.standard_normal((4000, 500)))
    lam_iid = gamma.required_threshold(ref, 0.5, 0.05, H=500)
    assert 0.9 < gamma.gamma_operational(iid, 0.5, lam_iid, 0.05, H=500) < 1.1
    z = lfilter([1.0], [1.0, -0.8], rng.standard_normal((4000, 600)), axis=1)[:, 100:] * np.sqrt(1 - 0.64)
    assert gamma.gamma_operational(_energy(z), 0.5, lam_iid, 0.05, H=500) > 1.3
    with pytest.raises(ValueError):
        gamma.required_threshold(iid[:, :100], 0.5, 1000.0, criterion="arl0")


# ------------------------------------------------------------------ eprocess

def _coins(seed, shape):
    return np.where(_rng(seed).random(shape) < 0.5, 1.0, -1.0)


def _ville_bound(alpha, n):
    return alpha + 3.0 * np.sqrt(alpha * (1.0 - alpha) / n)


def test_betting_eprocess():
    x = _coins(10, (2000, 2000))
    lk = eprocess.log_betting_eprocess(x, 0.3)
    assert np.array_equal(lk, np.cumsum(np.log1p(0.3 * x), axis=-1))
    assert np.array_equal(eprocess.log_betting_eprocess(x, np.full(x.shape, 0.3)), lk)
    assert (lk.max(axis=1) >= np.log(20)).mean() <= _ville_bound(0.05, 2000)
    for bad_x, bad_lam in ((x, 1.0), (x, -1.0), (x, np.nan), (1.5 * x, 0.3)):
        with pytest.raises(ValueError):
            eprocess.log_betting_eprocess(bad_x, bad_lam)


def test_mix_kernel_constants():
    st, inc1, inc0 = eprocess.build_mixture_kernel()
    assert st.size == inc1.size == inc0.size == eprocess.C_MIX == 96 and eprocess.MIX_W == 1.0 / 96
    assert np.array_equal(np.unique(st), np.linspace(0, 4999, 16, dtype=int)) and (st == 0).sum() == 6
    assert np.abs(0.5 * np.exp(inc1) + 0.5 * np.exp(inc0) - 1.0).max() < 1e-15


def test_mix_matches_direct_sum():
    x = _coins(11, (3, 700))
    got = eprocess.log_mix_eprocess(x)
    st, inc1, inc0 = eprocess.build_mixture_kernel()
    for r in range(3):
        for t in (0, 332, 333, 334, 699):
            total = sum(eprocess.MIX_W * np.exp(sum(inc1[c] if x[r, s] > 0 else inc0[c]
                                                    for s in range(st[c], t + 1)))
                        for c in range(96))
            assert abs(got[r, t] - np.log(total)) < 1e-12


def test_mix_ville():
    lm = eprocess.log_mix_eprocess(_coins(12, (1000, 5000)))
    assert (lm.max(axis=1) >= np.log(20)).mean() <= _ville_bound(0.05, 1000)


def test_edetector_recursions():
    x = _coins(13, (4, 50)) * np.linspace(0.2, 1.0, 50)
    lam = np.array([2 * side * e for e in eprocess.EDETECTOR_ETA0 for side in eprocess.SIDES])
    for kind in ("sr", "cusum"):
        got = eprocess.log_edetector(x, kind=kind)
        for r in range(4):
            m = np.zeros(lam.size)
            for t in range(50):
                m = ((1.0 + m) if kind == "sr" else np.maximum(1.0, m)) * (1.0 + lam * x[r, t])
                assert abs(got[r, t] - np.log(m.mean())) < 1e-12
    with pytest.raises(ValueError):
        eprocess.log_edetector(x, kind="shiryaev")


def test_edetector_strong_drift_finite():
    sr = eprocess.log_edetector(np.ones((2, 20000)), kind="sr")
    assert np.isfinite(sr).all() and (np.diff(sr, axis=-1) > 0).all()
    cu = eprocess.log_edetector(np.ones((1, 20000)), kind="cusum")
    assert np.isfinite(cu).all() and cu[0, -1] > 6000


def test_edetector_arl0_exceeds_gamma():
    for gam in (20, 100):
        T = 60 * gam
        x = _coins(14 + gam, (2000, T))
        for kind in ("sr", "cusum"):
            first = eprocess.first_alarm(eprocess.log_edetector(x, kind=kind), gam)
            assert np.where(first >= 0, first + 1, T).mean() > gam


def test_dictionary_average():
    x = 0.7 * _coins(15, (3, 300, 4))
    per = np.stack([eprocess.log_edetector(x[..., k]) for k in range(4)], axis=-1)
    got = eprocess.log_dictionary_edetector(x)
    assert np.allclose(got, np.log(np.exp(per).mean(axis=-1)), rtol=0.0, atol=1e-12)
    dup = np.repeat(x[..., :1], 5, axis=-1)
    assert np.allclose(eprocess.log_dictionary_edetector(dup), eprocess.log_edetector(x[..., 0]),
                       rtol=0.0, atol=1e-12)


def test_subgaussian_mixture():
    assert "independent under H0" in eprocess.log_subgaussian_mixture.__doc__
    z, s2 = _coins(16, (1, 40, 1)), 0.05
    got = eprocess.log_subgaussian_mixture(z, s2)[0]
    S = np.cumsum(z[0, :, 0])
    u = np.linspace(-3.0, 3.0, 600001)
    prior = np.exp(-u**2 / (2 * s2)) / np.sqrt(2 * np.pi * s2)
    for n in (1, 10, 40):
        integral = np.sum(np.exp(u * S[n - 1] - n * u**2 / 2) * prior) * (u[1] - u[0])
        assert abs(got[n - 1] - np.log(integral)) < 1e-8
    lm = eprocess.log_subgaussian_mixture(_coins(17, (1000, 2000, 5)), 0.02)
    assert (lm.max(axis=1) >= np.log(20)).mean() <= _ville_bound(0.05, 1000)


def test_first_alarm():
    lm = np.log(np.array([[1.0, 5.0, 25.0, 2.0], [1.0, 2.0, 3.0, 4.0]]))
    assert eprocess.first_alarm(lm, 20).tolist() == [2, -1]
    assert eprocess.first_alarm(lm, 5).tolist() == [1, -1]


def test_monitors_import_numpy_only():
    allowed = {"numpy", "math", "fractions"}
    for path in (Path(__file__).resolve().parents[1] / "jepadrift" / "monitors").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module]
            else:
                continue
            for name in names:
                assert name.split(".")[0] in allowed or name.startswith("jepadrift.monitors"), (path.name, name)


# ------------------------------------------------------------------ Monte Carlo control (prompt 04, item 10)

def test_lattice_calibrated_cusum_on_garch_sign_stream():
    sel = lattice.select_threshold(0.05, H=1000, delta=0.1, sided=2)
    alarms = 0
    for block in range(4):
        rng = _rng(7, block)
        g = Garch(rng, 5000, 1, 0.08, 0.90)
        y = np.stack([g.draw()[0] for _ in range(1000)], axis=1)
        s = streams.exact_sign_stream(y, rng)
        alarms += int((cusum.bilateral_delay_vec(s, 0.1, sel["threshold"]) >= 0).sum())
    lo, hi = binom.interval(0.99, 20000, sel["level"])
    assert lo <= alarms <= hi
