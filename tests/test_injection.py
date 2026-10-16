"""Tests for jepadrift.sim, jepadrift.injection and jepadrift.stats.covariance (pytest)."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy
import scipy.linalg

from experiments import e2_floor_validation as e2
from jepadrift import floors as fl
from jepadrift import injection, sim
from jepadrift.data_loader import sp500
from jepadrift.stats.covariance import ledoit_wolf

REPO = Path(__file__).resolve().parents[1]
MOVED_SOURCE_SHA256 = {
    "NU": "1cfff581049555d63312f5c5b1cf2fefadadde3fc5757a1e107ff9c91520cd90",
    "T_SCALE": "5fe894e1d876ef61d969723fe7107956d099539c2b2f708c85365cbd896d1c5c",
    "t_innov": "a50ac136f975c1b6f89023c2f6062ebdc02e2e0154e4af16be5e8bc3f021afdf",
    "Garch": "38af3cecb70b5fddbf0dd6de15e33e4e888b02bca7136b1b9b1bbf85ffa0b74c",
}
E2_QUICK_SHA256 = "7828e1a3c6b013476174e64b407cff0d07561fb85f5839963e1ebaaac8daa1f9"


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([5, *key]))


def _mean_offdiag_corr(X):
    R = np.corrcoef(X.T)
    n = R.shape[0]
    return (R.sum() - n) / (n * (n - 1))


def _d3_239_to_2019():
    ret, dates, _ = sp500.load_d3_239()
    seg = sp500.load_splits("d3_239")["segments"]["calib"]
    start = int(np.searchsorted(dates, np.datetime64(seg["first_day"])))
    stop = int(np.searchsorted(dates, np.datetime64(seg["last_day"]), side="right"))
    return ret[:stop], start, stop


def _d3_239_calib():
    X, start, stop = _d3_239_to_2019()
    _, dates, assets = sp500.load_d3_239()
    chars = sp500.load_chars("d3_239")
    cols = [c for c in chars.columns if c.startswith("c_")]
    idx = pd.MultiIndex.from_product([pd.DatetimeIndex(dates[start:stop].astype("datetime64[ns]")), assets],
                                     names=["date", "asset_id"])
    C = chars.set_index(["date", "asset_id"])[cols].reindex(idx).to_numpy(dtype=np.float64)
    return np.ascontiguousarray(X[start:stop]), C.reshape(stop - start, len(assets), len(cols))


def _synthetic():
    X = sim.garch_panel(1200, 30, 0.08, 0.90, 7, _rng(20), factor_rho=0.4) * 0.01
    return X, _rng(21).uniform(-0.5, 0.5, (1200, 30, 4))


def _lw_reference(X):
    Xc = X - X.mean(axis=0)
    n, p = Xc.shape
    S = Xc.T @ Xc / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = sum(np.sum((np.outer(x, x) - S) ** 2) for x in Xc) / n ** 2
    delta = min(b2, d2) / d2
    return (1 - delta) * S + delta * mu * np.eye(p), delta


# ------------------------------------------------------------------ sim and E2

def test_e2_uses_moved_generator():
    assert e2.Garch is sim.Garch and e2.T_SCALE is sim.T_SCALE and e2.NU == sim.NU
    src = (REPO / "jepadrift" / "sim.py").read_text()
    found = {}
    for node in ast.parse(src).body:
        name = node.targets[0].id if isinstance(node, ast.Assign) else getattr(node, "name", None)
        if name in MOVED_SOURCE_SHA256:
            found[name] = _sha256(ast.get_source_segment(src, node).encode())
    assert found == MOVED_SOURCE_SHA256


@pytest.mark.skipif((np.__version__, scipy.__version__) != ("2.4.4", "1.17.1"),
                    reason="E2 hash pinned in the reference environment (.venv: numpy 2.4.4, scipy 1.17.1)")
def test_e2_quick_sha256_unchanged(tmp_path):
    e2.main(["--quick", "--reps", "50", "--out", str(tmp_path)])
    assert _sha256((tmp_path / "e2_cells.csv").read_bytes()) == E2_QUICK_SHA256


# ------------------------------------------------------------------ D5 generators

def test_garch_panel_moments():
    X = sim.garch_panel(20_000, 50, 0.08, 0.90, 7, _rng(1), factor_rho=0.40)
    assert X.shape == (20_000, 50) and np.isfinite(X).all()
    assert abs(X.var() - 1.0) < 0.15
    assert 0.37 <= _mean_offdiag_corr(X) <= 0.43
    X = sim.garch_panel(20_000, 50, 0.08, 0.90, 7, _rng(2))
    m = (X ** 2).mean(axis=1)
    assert abs(_mean_offdiag_corr(X)) < 0.03
    assert np.corrcoef(m[1:], m[:-1])[0, 1] > 0.05
    X = sim.garch_panel(20_000, 50, 0.08, 0.90, None, _rng(3))
    assert abs(X.var() - 1.0) < 0.15
    X = sim.garch_panel(5_000, 1, 0.08, 0.90, None, _rng(4))
    assert X.shape == (5_000, 1) and np.isfinite(X).all()
    for kw in ({"alpha": -0.1}, {"beta": -0.1}, {"alpha": 0.1, "beta": 0.9}, {"nu": 2}, {"factor_rho": 1.0},
               {"factor_rho": -0.1}):
        args = {"alpha": 0.08, "beta": 0.90, "nu": 7, **kw}
        with pytest.raises(ValueError):
            sim.garch_panel(10, 3, args["alpha"], args["beta"], args["nu"], _rng(5), factor_rho=args.get("factor_rho"))


def test_generators_deterministic():
    a, b = sim.gaussian_latent(300, 4, _rng(6)), sim.gaussian_latent(300, 4, _rng(6))
    assert a.shape == (300, 4) and a.tobytes() == b.tobytes()
    a = sim.garch_panel(300, 4, 0.08, 0.90, 7, _rng(7), factor_rho=0.4)
    b = sim.garch_panel(300, 4, 0.08, 0.90, 7, _rng(7), factor_rho=0.4)
    assert a.tobytes() == b.tobytes()
    assert a.tobytes() != sim.garch_panel(300, 4, 0.08, 0.90, 7, _rng(8), factor_rho=0.4).tobytes()


# ------------------------------------------------------------------ covariance, calibration estimates, D6

def test_ledoit_wolf_matches_formula():
    rng = _rng(3)
    X = rng.standard_normal((40, 7)) @ rng.standard_normal((7, 7))
    sigma, shrink = ledoit_wolf(X)
    ref, ref_shrink = _lw_reference(X)
    assert np.abs(sigma - ref).max() <= 1e-12 and abs(shrink - ref_shrink) <= 1e-12
    assert 0.0 < shrink < 1.0
    np.testing.assert_allclose(sigma, sigma.T, rtol=1e-15, atol=0)
    np.linalg.cholesky(sigma)
    X = _rng(30, 40).standard_normal((40, 7))
    sigma, shrink = ledoit_wolf(X)
    assert _lw_reference(X)[1] == 1.0 and shrink == 1.0
    assert np.allclose(sigma, np.trace(sigma) / 7 * np.eye(7), rtol=0, atol=1e-15)
    assert ledoit_wolf(rng.standard_normal((4000, 5)) * np.array([3.0, 2.0, 1.0, 0.5, 0.25]))[1] < 0.05
    x = rng.standard_normal((50, 1))
    sigma, shrink = ledoit_wolf(x)
    assert shrink == 0.0 and np.isclose(sigma[0, 0], x.var(), rtol=1e-14)


def test_gls_residual_matches_corollary():
    rng = _rng(9)
    B, psi, a = rng.standard_normal((30, 3)), rng.uniform(0.5, 2.0, 30), rng.standard_normal(30)
    r = injection.gls_residual(a, B, psi)
    assert np.abs(B.T @ (r / psi)).max() <= 1e-12 * np.abs(B.T @ (a / psi)).max()
    breadth = fl.factor_information(B, np.eye(3), psi, np.zeros(3), a)[1]
    assert abs(r @ (r / psi) - breadth) <= 1e-12 * breadth
    A = rng.standard_normal((5, 30))
    R = injection.gls_residual(A, B, psi)
    assert R.shape == (5, 30)
    for t in range(5):
        np.testing.assert_allclose(R[t], injection.gls_residual(A[t], B, psi), rtol=1e-13, atol=1e-15)


def test_fit_background_conventions():
    X, start, stop = _d3_239_to_2019()
    Xc = X[start:stop]
    fit = injection.fit_background(Xc, 11)
    sigma, lam, V, B, psi = fit["sigma"], fit["eigval"], fit["eigvec"], fit["B"], fit["psi"]
    assert np.array_equal(sigma, ledoit_wolf(Xc)[0]) and fit["shrinkage"] == ledoit_wolf(Xc)[1]
    assert np.all(np.diff(lam) <= 0)
    assert np.abs(sigma @ V - V * lam).max() <= 1e-12 * lam[0]
    assert np.abs(V.T @ V - np.eye(V.shape[0])).max() <= 1e-12
    assert np.all(V.sum(axis=0) >= 0)
    assert B.shape == (239, 11)
    np.testing.assert_allclose(B.T @ B, np.diag(lam[:11]), rtol=0, atol=1e-12 * lam[0])
    assert np.all(psi > 0)
    np.testing.assert_allclose(psi + np.sum(B ** 2, axis=1), np.diag(sigma), rtol=1e-12, atol=0)
    for K in (0, 239):
        with pytest.raises(ValueError):
            injection.fit_background(Xc, K)


def test_symmetrize_abs_bitwise_one_sign_per_day():
    X = _d3_239_to_2019()[0].copy()
    X[10, :3] = np.nan
    X[11, 5] = -0.0
    X[12, 7] = 0.0
    assert np.isnan(X).any()
    Xs, eps = injection.symmetrize(X, _rng(10))
    assert eps.shape == (X.shape[0],) and eps.dtype == np.float64 and set(np.unique(eps)) == {-1.0, 1.0}
    assert np.array_equal(np.abs(Xs).view(np.uint64), np.abs(X).view(np.uint64))
    assert np.array_equal(np.isnan(Xs), np.isnan(X))
    live = np.isfinite(X) & (X != 0)
    assert np.all((np.sign(Xs * X) == eps[:, None]) | ~live)
    assert abs(eps.mean()) < 4 / np.sqrt(eps.size)


def test_inputs_rejected():
    Z = np.zeros((10, 3))
    for bad in ({"z_odd": Z}, Z.tolist()):
        with pytest.raises(TypeError):
            injection.symmetrize(bad, _rng(11))
    for bad in (Z.astype(np.float32), Z[:, 0]):
        with pytest.raises(ValueError):
            injection.symmetrize(bad, _rng(11))


def test_inputs_not_mutated():
    X = _d3_239_to_2019()[0][-941:].copy()
    before = X.tobytes()
    injection.symmetrize(X, _rng(12))
    assert X.tobytes() == before


# ------------------------------------------------------------------ inject: F1, F2, F3 (F4 below)

LOCATION = ("F1", "F2", "F3")


def _args(family, C, calib, K):
    if family == "F4-deform":
        return None, {"calib": calib, "subspace": (1,), "r": 1.5}
    if family == "F4-rotate":
        return None, {"calib": calib, "pair": (1, 2), "theta_deg": 30.0}
    return fl.kl_from_sharpe(1.0), {"calib": calib, "K": K, "C": C}


def test_f2_orthogonal_to_loadings():
    X, C = _d3_239_calib()
    Xs, Cs = _synthetic()
    for Xb, Cb, calib, tau, K in ((X, C, (0, 941), 600, 11), (Xs, Cs, (0, 600), 800, 3)):
        params = {"calib": calib, "K": K, "C": Cb}
        _, delta, _ = injection.inject(Xb, "F2", tau, fl.kl_from_sharpe(4.0), params, _rng(23))
        fit = injection.fit_background(Xb[calib[0]:calib[1]], K)
        assert delta.shape == (Xb.shape[0] - tau, Xb.shape[1])
        assert np.abs((delta / fit["psi"]) @ fit["B"]).max() < 1e-10


@pytest.mark.parametrize("family", LOCATION)
@pytest.mark.parametrize("sr", [0.5, 4.0])
def test_information_target(family, sr):
    X, C = _d3_239_calib()
    I_target = fl.kl_from_sharpe(sr)
    _, delta, meta = injection.inject(X, family, 600, I_target, {"calib": (0, 941), "K": 11, "C": C}, _rng(22))
    cho = scipy.linalg.cho_factor(ledoit_wolf(X)[0])
    fit = injection.fit_background(X, 11)
    direction = np.array(meta["direction"])
    if family == "F2":
        D = injection.gls_residual(np.where(np.isnan(C), 0.0, C) @ direction, fit["B"], fit["psi"])
        np.testing.assert_allclose(D[600:], delta, rtol=1e-12, atol=1e-12 * np.abs(delta).max())
        info = 0.5 * np.mean(np.sum(D * scipy.linalg.cho_solve(cho, D.T).T, axis=1))
    else:
        info = 0.5 * delta @ scipy.linalg.cho_solve(cho, delta)
        loadings = fit["B"] if family == "F1" else fit["B"][:, :1]
        np.testing.assert_allclose(loadings @ direction, delta, rtol=1e-13, atol=1e-13 * np.abs(delta).max())
    assert abs(info - I_target) <= 1e-10 and abs(info - I_target) <= 1e-12 * I_target
    assert abs(meta["info"] - I_target) <= 1e-12 * I_target
    assert meta["convention"] == "a" and meta["family"] == family and meta["tau_star"] == 600


@pytest.mark.parametrize("family", injection.FAMILIES)
def test_no_change_before_tau_star(family):
    X, C = _d3_239_calib()
    I_target, params = _args(family, C, (0, 941), 11)
    for tau in (0, 600, 940):
        Xt, delta, _ = injection.inject(X, family, tau, I_target, params, _rng(24))
        assert Xt[:tau].tobytes() == X[:tau].tobytes()
        assert np.array_equal(Xt[tau:], X[tau:] @ delta.T if family.startswith("F4") else X[tau:] + delta)
        assert not np.array_equal(Xt[tau:], X[tau:])


def test_convention_b_per_asset_amplitude():
    X, C = _d3_239_calib()
    sd = np.sqrt(np.diag(ledoit_wolf(X)[0]))
    for family, kappa, target in (("F1", None, 1.0), ("F3", None, 1.0), ("F2", 0.25, 0.25), ("F2", 0.5, 0.5),
                                  ("F2", 1.0, 1.0)):
        params = {"calib": (0, 941), "K": 11, "C": C, "kappa": kappa}
        _, delta, meta = injection.inject(X, family, 0 if family == "F2" else 600, None, params, _rng(25))
        rms = np.sqrt(np.mean((np.sqrt(252.0) * delta / sd) ** 2))
        assert abs(rms - target) <= 1e-12 * target
        assert meta["convention"] == "b"


def test_f2_nan_characteristics_imputed():
    X, C = _synthetic()
    C_nan, C_zero = C.copy(), C.copy()
    for pos in ((5, 1, 0), (100, 2, 1), (650, 3, 2), (900, 4, 3), (1100, 5, 0)):
        C_nan[pos], C_zero[pos] = np.nan, 0.0
    I_target = fl.kl_from_sharpe(1.0)
    a = injection.inject(X, "F2", 800, I_target, {"calib": (0, 600), "K": 3, "C": C_nan}, _rng(26))
    b = injection.inject(X, "F2", 800, I_target, {"calib": (0, 600), "K": 3, "C": C_zero}, _rng(26))
    assert a[0].tobytes() == b[0].tobytes() and a[1].tobytes() == b[1].tobytes()
    assert a[2]["c_nan_imputed"] == 5 and b[2]["c_nan_imputed"] == 0


def test_degenerate_direction_rejected():
    X, C = _synthetic()
    with pytest.raises(ValueError):
        injection.inject(X, "F2", 800, fl.kl_from_sharpe(1.0),
                         {"calib": (0, 600), "K": 3, "C": np.full_like(C, np.nan)}, _rng(27))


def test_inject_arguments_rejected():
    X, C = _synthetic()
    I_target = fl.kl_from_sharpe(1.0)
    ok = {"calib": (0, 600), "K": 3, "C": C}
    X_nan, C_inf = X.copy(), C.copy()
    X_nan[3, 2], C_inf[700, 1, 0] = np.nan, np.inf
    calls = [
        (X_nan, "F1", 800, I_target, ok),
        (X, "F5", 800, I_target, ok),
        (X, "F1", -1, I_target, ok),
        (X, "F1", 1200, I_target, ok),
        (X, "F1", 800, I_target, {"K": 3}),
        (X, "F1", 800, I_target, {"calib": (600, 600), "K": 3}),
        (X, "F1", 800, I_target, {"calib": (0, 1300), "K": 3}),
        (X, "F1", 800, I_target, {"calib": (0, 600)}),
        (X, "F2", 800, I_target, {"calib": (0, 600), "C": C}),
        (X, "F2", 800, I_target, {"calib": (0, 600), "K": 3}),
        (X, "F2", 800, I_target, {"calib": (0, 600), "K": 3, "C": C[:, :10]}),
        (X, "F2", 800, I_target, {"calib": (0, 600), "K": 3, "C": C_inf}),
        (X, "F2", 800, None, ok),
        (X, "F1", 800, 0.0, ok),
        (X, "F1", 800, -I_target, ok),
        (X, "F4-deform", 800, I_target, {"calib": (0, 600), "subspace": (1,), "r": 1.5}),
        (X, "F4-deform", 800, None, {"calib": (0, 600), "subspace": (1,)}),
        (X, "F4-deform", 800, None, {"calib": (0, 600), "subspace": (1,), "r": 0.0}),
        (X, "F4-deform", 800, None, {"calib": (0, 600), "subspace": (30,), "r": 1.5}),
        (X, "F4-deform", 800, None, {"calib": (0, 600), "subspace": (), "r": 1.5}),
        (X, "F4-rotate", 800, None, {"calib": (0, 600), "pair": (1, 1), "theta_deg": 30.0}),
        (X, "F4-rotate", 800, None, {"calib": (0, 600), "pair": (1, 2)}),
    ]
    for args in calls:
        with pytest.raises(ValueError):
            injection.inject(*args, _rng(28))


def test_k_ignored_for_f3_and_f4():
    X, _ = _synthetic()
    for family, base in (("F3", {"calib": (0, 600)}),
                         ("F4-deform", {"calib": (0, 600), "subspace": (1,), "r": 1.5})):
        I_target = None if family.startswith("F4") else fl.kl_from_sharpe(1.0)
        for k in (None, 10**6):
            _, _, meta = injection.inject(X, family, 800, I_target, {**base, "K": k}, _rng(33))
            assert meta["K"] is None and meta["family"] == family


def test_inject_does_not_mutate_inputs():
    X, C = _synthetic()
    X_before, C_before = X.tobytes(), C.tobytes()
    for family in injection.FAMILIES:
        injection.inject(X, family, 800, *_args(family, C, (0, 600), 3), _rng(29))
    assert X.tobytes() == X_before and C.tobytes() == C_before


def test_determinism():
    X, C = _synthetic()
    assert injection.symmetrize(X, _rng(30))[0].tobytes() == injection.symmetrize(X, _rng(30))[0].tobytes()
    for family in injection.FAMILIES:
        I_target, params = _args(family, C, (0, 600), 3)
        a = injection.inject(X, family, 800, I_target, params, _rng(31))
        b = injection.inject(X, family, 800, I_target, params, _rng(31))
        assert a[0].tobytes() == b[0].tobytes() and a[1].tobytes() == b[1].tobytes()
        assert json.dumps(a[2], sort_keys=True) == json.dumps(b[2], sort_keys=True)
        if family in ("F1", "F2"):
            assert injection.inject(X, family, 800, I_target, params, _rng(32))[2]["direction"] != a[2]["direction"]


# ------------------------------------------------------------------ inject: F4

def test_f4_deformation_and_rotation():
    X, _ = _d3_239_calib()
    fit = injection.fit_background(X, 1)
    lam, V = fit["eigval"], fit["eigvec"]
    for r in (1.25, 1.5, 2.0):
        for S in ((1,), (1, 2)):
            _, M, meta = injection.inject(X, "F4-deform", 600, None, {"calib": (0, 941), "subspace": S, "r": r},
                                          _rng(40))
            VS, rest = V[:, list(S)], np.delete(V, list(S), axis=1)
            assert np.abs(M @ VS - np.sqrt(r) * VS).max() <= 1e-12
            assert np.abs(M @ rest - rest).max() <= 1e-12
            kl = len(S) / 2 * (r - 1 - np.log(r))
            assert abs(meta["info"] - kl) <= 1e-10 * kl
            assert meta["direction"] is None and meta["convention"] is None
            assert meta["amplitude"] == {"r": r, "subspace": list(S)}
    for theta in (15.0, 30.0, 45.0):
        _, G, meta = injection.inject(X, "F4-rotate", 600, None,
                                      {"calib": (0, 941), "pair": (1, 2), "theta_deg": theta}, _rng(41))
        t, u, w = np.radians(theta), V[:, 1], V[:, 2]
        assert np.abs(G @ G.T - np.eye(G.shape[0])).max() <= 1e-12
        assert abs(np.linalg.det(G) - 1.0) <= 1e-12
        assert np.abs(G @ u - (np.cos(t) * u + np.sin(t) * w)).max() <= 1e-12
        kl = 0.5 * np.sin(t) ** 2 * (lam[1] - lam[2]) ** 2 / (lam[1] * lam[2])
        assert abs(meta["info"] - kl) <= 1e-10 * kl
        assert meta["amplitude"] == {"theta_deg": theta, "pair": [1, 2]}


# ------------------------------------------------------------------ onset and tau_star.json

def test_draw_tau_star_bounds():
    rng = _rng(50)
    draws = [injection.draw_tau_star(0, 10, 3, 4, rng) for _ in range(2000)]
    assert set(draws) == {3, 4, 5, 6} and all(type(t) is int for t in draws)
    with pytest.raises(ValueError):
        injection.draw_tau_star(0, 10, 6, 5, rng)


def test_tau_star_json_roundtrip(tmp_path):
    X, C = _synthetic()
    records = []
    for family in ("F1", "F4-rotate"):
        _, delta, meta = injection.inject(X, family, 800, *_args(family, C, (0, 600), 3), _rng(51))
        assert meta["direction_sha256"] == _sha256(np.ascontiguousarray(delta, dtype=np.float64).tobytes())
        assert meta["seed"] == {"entropy": [5, 51], "spawn_key": []}
        assert {"family", "tau_star", "convention", "amplitude", "seed", "direction_sha256"} <= set(meta)
        records.append(meta)
    child = np.random.default_rng(np.random.SeedSequence(5).spawn(2)[1])
    assert injection.inject(X, "F3", 800, *_args("F3", C, (0, 600), 3), child)[2]["seed"] == \
        {"entropy": 5, "spawn_key": [1]}
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    injection.write_tau_star(a, records)
    injection.write_tau_star(b, records)
    assert a.read_bytes() == b.read_bytes() and a.read_text().endswith("}\n]\n")
    assert json.loads(a.read_text()) == records
    injection.write_tau_star(a, records[0])
    assert json.loads(a.read_text()) == records[0]
