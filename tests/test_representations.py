"""Tests for jepadrift.representations (pytest)."""
import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import rankdata

from jepadrift import injection
from jepadrift.data_loader import articleB, sp500
from jepadrift.representations import extract, pca
from jepadrift.representations.cross_section import CenteredRanks, DegreeZero
from jepadrift.representations.pca import PCAOrthogonal
from jepadrift.stats.covariance import eigh_desc, ledoit_wolf

REPO = Path(__file__).resolve().parents[1]
LOADERS = {"d2_us97": (articleB.load_d2, articleB.load_splits),
           "d3_239": (sp500.load_d3_239, sp500.load_splits)}


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([6, *key]))


def _rows(dates, segment):
    start = int(np.searchsorted(dates, np.datetime64(segment["first_day"])))
    stop = int(np.searchsorted(dates, np.datetime64(segment["last_day"]), side="right"))
    return start, stop


def _days(T):
    return np.datetime64("2016-01-04") + np.arange(T)


def _panel(dataset):
    load, splits = LOADERS[dataset]
    ret, dates, _ = load()
    return ret, dates, splits(dataset)["segments"]


def _calib(dataset):
    ret, dates, segments = _panel(dataset)
    start, stop = _rows(dates, segments["calib"])
    return np.ascontiguousarray(ret[start:stop]), dates[start:stop]


def _to_2019(dataset):
    ret, dates, segments = _panel(dataset)
    first = _rows(dates, segments["pretrain"])[0]
    stop = _rows(dates, segments["calib"])[1]
    return np.ascontiguousarray(ret[first:stop])


def _spiked(T, N, seed):
    g = _rng(3, seed)
    B = g.standard_normal((N, 4)) * np.array([3.0, 1.5, 1.2, 1.0])
    return g.standard_normal((T, 4)) @ B.T + g.standard_normal((T, N))


def _degree_zero_reps():
    return [DegreeZero(b=b, mode=m) for b in ("pc1", "ones") for m in ("factor", "full")]


def _odd_reps():
    return ([PCAOrthogonal(mode=m, shrinkage=s) for m in pca.MODES for s in pca.SHRINKAGES]
            + _degree_zero_reps() + [CenteredRanks()])


def test_eigh_desc_sorted_signed():
    X, _ = _calib("d3_239")
    sigma = ledoit_wolf(X)[0]
    eigval, eigvec = eigh_desc(sigma)
    assert np.all(np.diff(eigval) <= 0)
    assert np.all(eigvec.sum(axis=0) >= 0)
    assert np.abs(eigvec * eigval @ eigvec.T - sigma).max() <= 1e-12
    fit = injection.fit_background(X, 11)
    assert np.array_equal(fit["eigval"], eigval) and np.array_equal(fit["eigvec"], eigvec)


def test_ranks_values():
    rep = CenteredRanks().fit(_rng(1).standard_normal((10, 4)), None, _days(10))
    z = rep.transform_day(np.array([0.3, -0.1, 0.3, 0.0]))
    assert np.array_equal(z["z_odd"], [0.25, -0.375, 0.25, -0.125])
    assert np.array_equal(z["z_even"], z["z_odd"] ** 2)
    N = 239
    x = _rng(2).integers(-5, 6, size=N).astype(np.float64)
    rep = CenteredRanks().fit(_rng(3).standard_normal((20, N)), None, _days(20))
    assert np.array_equal(rep.transform_day(x)["z_odd"], (rankdata(x) - (N + 1) / 2) / N)


def test_transform_panel_day_by_day():
    X = 0.01 * _rng(4).standard_normal((50, 30))
    rep = CenteredRanks().fit(X[:20], None, _days(20))
    Z = rep.transform_panel(X)
    for key in ("z_odd", "z_even"):
        assert np.array_equal(Z[key], np.stack([rep.transform_day(x)[key] for x in X]))
    X2 = X.copy()
    X2[31:] = 0.01 * _rng(5).standard_normal((19, 30))
    Z2 = rep.transform_panel(X2)
    assert np.array_equal(Z2["z_odd"][:31], Z["z_odd"][:31])
    assert not np.array_equal(Z2["z_odd"][31:], Z["z_odd"][31:])


def test_inputs_rejected():
    X = 0.01 * _rng(6).standard_normal((20, 6))
    bad = X.copy()
    bad[3, 2] = np.nan
    for args, err in (((bad, None, _days(20)), ValueError), ((X[0], None, _days(1)), ValueError),
                      ((X[:1], None, _days(1)), ValueError), ((X.astype(np.float32), None, _days(20)), ValueError),
                      ((X, None, _days(19)), ValueError), ((X.tolist(), None, _days(20)), TypeError)):
        with pytest.raises(err):
            CenteredRanks().fit(*args)
    rep = CenteredRanks().fit(X, None, _days(20))
    for x in (X[0, :5], np.full(6, np.nan), X[0].astype(np.float32)):
        with pytest.raises(ValueError):
            rep.transform_day(x)
    with pytest.raises(TypeError):
        rep.transform_day(X[0].tolist())
    for kwargs in ({"b": "median"}, {"mode": "tail10"}, {"K": 0}):
        with pytest.raises(ValueError):
            DegreeZero(**kwargs)


def test_state_hash_and_sidecar():
    X = 0.01 * _rng(7).standard_normal((20, 6))
    rep = CenteredRanks().fit(X, None, _days(20))
    assert CenteredRanks().fit(X.copy(), None, _days(20)).state_hash() == rep.state_hash()
    assert CenteredRanks().fit(X[:, :5].copy(), None, _days(20)).state_hash() != rep.state_hash()
    side = rep.sidecar()
    assert json.loads(json.dumps(side)) == side
    assert side["state_sha256"] == rep.state_hash() and side["interface"] == "Z-1" and side["odd_head"] is True
    assert side["fit"] == {"first_day": "2016-01-04", "last_day": "2016-01-23", "days": 20,
                           "x_sha256": hashlib.sha256(X.tobytes()).hexdigest(), "c_sha256": None}
    assert side["heads"]["z_odd"]["parity"] == "odd" and side["heads"]["z_even"]["parity"] == "even"


def test_mp_rule():
    assert pca.mp_edge(1000, 60) == (1 + math.sqrt(0.06)) ** 2
    for seed in range(5):
        X = _spiked(1000, 60, seed)
        assert pca.mp_count(X)[0] == 4
        rep = PCAOrthogonal().fit(X, None, _days(1000))
        assert rep.stats["K"] == 3 and rep.transform_day(X[0])["z_odd"].shape == (4,)
    X = _rng(2, 0).standard_normal((941, 97))
    assert pca.mp_count(X)[0] <= 1
    with pytest.raises(ValueError):
        PCAOrthogonal().fit(X, None, _days(941))
    with pytest.raises(ValueError):
        PCAOrthogonal(K=97).fit(X, None, _days(941))
    for kwargs in ({"K": 0}, {"K": -1}, {"K": 2.5}, {"K": True}, {"K": "auto"}, {"mode": "tail"}, {"shrinkage": "oas"}):
        with pytest.raises(ValueError):
            PCAOrthogonal(**kwargs)


@pytest.mark.parametrize("dataset, K, m", [("d2_us97", 5, 46), ("d3_239", 10, 123)])
def test_pca_dimensions_real(dataset, K, m):
    X = _to_2019(dataset)
    Xc, dates = _calib(dataset)
    for mode, D in (("factor", K + 1), ("full", X.shape[1]), ("tail10", m + 1)):
        rep = PCAOrthogonal(mode=mode).fit(Xc, None, dates)
        Z = rep.transform_panel(X)
        assert Z["z_odd"].shape == Z["z_even"].shape == (X.shape[0], D)
        assert np.isfinite(Z["z_odd"]).all() and np.isfinite(Z["z_even"]).all()
        assert rep.sidecar()["channels"] == {"market": [0], "residual": list(range(1, D))}
        assert rep.stats.get("K", K) == K and rep.stats.get("tail_count", m) == m


def test_tail10_rule():
    X, dates = _calib("d3_239")
    rep = PCAOrthogonal(mode="tail10").fit(X, None, dates)
    eigval = eigh_desc(ledoit_wolf(X)[0])[0]
    m, tail = rep.stats["tail_count"], eigval[::-1]
    assert tail[:m].sum() <= 0.10 * eigval.sum() < tail[:m + 1].sum()
    assert rep.stats["eigval"] == [eigval[0], *eigval[-m:]]


def test_whitening():
    X, dates = _calib("d3_239")
    Z = PCAOrthogonal(mode="full", shrinkage=None).fit(X, None, dates).transform_panel(X)["z_odd"]
    Zc = Z - Z.mean(axis=0)
    assert np.abs(Zc.T @ Zc / X.shape[0] - np.eye(X.shape[1])).max() <= 1e-10
    rep = PCAOrthogonal(mode="full").fit(X, None, dates)
    _, delta, meta = injection.inject(X, "F1", 0, 0.01, {"calib": (0, X.shape[0]), "K": 11}, _rng(9))
    z = rep.transform_day(delta)["z_odd"]
    assert abs(0.5 * z @ z - meta["info"]) <= 1e-12 * meta["info"]
    _, delta, _ = injection.inject(X, "F3", 0, 0.01, {"calib": (0, X.shape[0])}, _rng(10))
    z = rep.transform_day(delta)["z_odd"]
    assert np.abs(z[1:]).max() <= 1e-12 * abs(z[0])


def test_odd_head():
    X, dates = _calib("d3_239")
    xs = np.vstack([X[::19][:50], 0.01 * _rng(11).standard_normal((50, X.shape[1]))])
    for rep in _odd_reps():
        rep.fit(X, None, dates)
        for x in xs:
            a, b = rep.transform_day(x), rep.transform_day(-x)
            assert np.abs(a["z_odd"] + b["z_odd"]).max() <= 1e-12
            assert np.abs(a["z_even"] - b["z_even"]).max() <= 1e-12


def test_normalization_from_declared_segment():
    ret, dates, segments = _panel("d3_239")
    start, stop = _rows(dates, segments["calib"])
    side = PCAOrthogonal().fit(np.ascontiguousarray(ret[start:stop]), None, dates[start:stop]).sidecar()
    a = int(np.searchsorted(dates, np.datetime64(side["fit"]["first_day"])))
    b = int(np.searchsorted(dates, np.datetime64(side["fit"]["last_day"]), side="right"))
    X = np.ascontiguousarray(ret[a:b])
    norm = side["normalization"]
    assert norm["eigval"] == eigh_desc(ledoit_wolf(X)[0])[0][:norm["K"] + 1].tolist()
    assert (norm["n_above_edge"], norm["mp_edge"]) == pca.mp_count(X)
    assert side["fit"]["days"] == b - a and side["fit"]["x_sha256"] == hashlib.sha256(X.tobytes()).hexdigest()


def test_degree_zero_invariance():
    X, dates = _calib("d3_239")
    xs = np.vstack([X[::47], 0.01 * _rng(12).standard_normal((20, X.shape[1]))])
    for rep in _degree_zero_reps() + [CenteredRanks()]:
        rep.fit(X, None, dates)
        for x in xs:
            z = rep.transform_day(x)
            for c in (0.5, 3.7, 1e3):
                zc = rep.transform_day(c * x)
                assert np.abs(zc["z_odd"] - z["z_odd"]).max() <= 1e-12
                if isinstance(rep, DegreeZero):
                    assert abs(zc["z_even"][0] - c * z["z_even"][0]) <= 1e-12 * c * z["z_even"][0]


def test_degree_zero_bounds_and_zero_day():
    X, dates = _calib("d3_239")
    for rep in _degree_zero_reps():
        Z = rep.fit(X, None, dates).transform_panel(X)["z_odd"]
        assert np.abs(Z).max() <= 1.0 + 1e-12
        if rep.config["b"] == "pc1" and rep.config["mode"] == "full":
            assert np.abs(np.linalg.norm(Z, axis=1) - 1.0).max() <= 1e-12
    zero = np.zeros(X.shape[1])
    for rep in _odd_reps():
        z = rep.fit(X, None, dates).transform_day(zero)
        assert not np.any(z["z_odd"]) and not np.any(z["z_even"])
        assert np.isfinite(z["z_odd"]).all() and np.isfinite(z["z_even"]).all()


@pytest.mark.parametrize("dataset, K", [("d2_us97", 5), ("d3_239", 10)])
def test_cross_section_dimensions_real(dataset, K):
    X = _to_2019(dataset)
    Xc, dates = _calib(dataset)
    N = X.shape[1]
    for rep, D, D_even in ((DegreeZero(), K, 1), (DegreeZero(b="ones", mode="full"), N - 1, 1),
                           (CenteredRanks(), N, N)):
        Z = rep.fit(Xc, None, dates).transform_panel(X)
        assert Z["z_odd"].shape == (X.shape[0], D) and Z["z_even"].shape == (X.shape[0], D_even)
        assert np.isfinite(Z["z_odd"]).all() and np.isfinite(Z["z_even"]).all()
    assert DegreeZero().fit(Xc, None, dates).state_hash() != PCAOrthogonal().fit(Xc, None, dates).state_hash()


def test_monitor_perturbation_keeps_state(tmp_path):
    ret, dates, _ = articleB.load_d2()
    splits = articleB.load_splits("d2_us97")
    cut = int(np.searchsorted(dates, np.datetime64("2020-01-01")))
    A = ret.copy()
    A[cut:] = 0.01 * _rng(13).standard_normal(A[cut:].shape)
    B = A.copy()
    B[cut:] = 0.01 * _rng(14).standard_normal(B[cut:].shape)
    C = A.copy()
    C[_rows(dates, splits["segments"]["calib"])[0] + 10] *= 1.5
    for name, cls in extract.REGISTRY.items():
        (pa, sa), (pb, sb), (_, sc) = (extract.extract(cls(), X, dates, splits, tmp_path / f"{name}{i}", "d2_us97")
                                       for i, X in enumerate((A, B, C)))
        assert sa["state_sha256"] == sb["state_sha256"]
        assert sa["normalization"] == sb["normalization"] and sa["fit"] == sb["fit"]
        assert sc["fit"]["x_sha256"] != sa["fit"]["x_sha256"]
        if cls is not extract.REGISTRY["ranks"]:
            assert sc["state_sha256"] != sa["state_sha256"]
        n = cut - sa["rows"][0]
        with np.load(pa) as za, np.load(pb) as zb:
            assert np.array_equal(za["Z_odd"][:n], zb["Z_odd"][:n]) and np.array_equal(za["Z_even"][:n], zb["Z_even"][:n])


def test_extract_deterministic(tmp_path):
    runs = []
    for k in ("1", "2"):
        assert extract.main(["--dataset", "d2_us97", "--rep", "pca", "--mode", "factor", "--out", str(tmp_path / k)]) == 0
        runs.append(sorted((tmp_path / k).iterdir()))
    (j1, n1), (j2, n2) = runs
    assert j1.read_bytes() == j2.read_bytes() and n1.read_bytes() == n2.read_bytes()
    side = json.loads(j1.read_text())
    assert (j1.name, n1.name) == (f"z_{side['state_sha256']}.json", f"z_{side['state_sha256']}.npz")
    _, dates, _ = articleB.load_d2()
    segments = articleB.load_splits("d2_us97")["segments"]
    first = _rows(dates, segments["pretrain"])[0]
    with np.load(n1) as z:
        assert set(z.files) == {"Z_odd", "Z_even", "dates"}
        assert z["Z_odd"].dtype == z["Z_even"].dtype == np.float64 and z["dates"].dtype == np.dtype("datetime64[D]")
        assert z["Z_odd"].shape == z["Z_even"].shape == (len(dates) - first, 6)
        assert np.array_equal(z["dates"], dates[first:])
    calib = segments["calib"]
    assert (side["fit"]["first_day"], side["fit"]["last_day"]) == (str(calib["first_day"]), str(calib["last_day"]))
    assert side["fit"]["days"] == 941 and side["fit_segment"] == "calib" and side["dataset"] == "d2_us97"


def test_check_K_accepts_numpy_integers():
    assert pca.check_K(np.int64(5)) == 5 and isinstance(pca.check_K(np.int32(3)), int)
    assert pca.check_K("mp") == "mp"
    for bad in (True, 0, -1, 2.5, "auto"):
        with pytest.raises(ValueError):
            pca.check_K(bad)
    X = 0.01 * _rng(15).standard_normal((30, 8))
    rep = PCAOrthogonal(K=np.int64(3)).fit(X, None, _days(30))
    assert rep.config["K"] == 3 and isinstance(rep.config["K"], int)
    assert json.loads(json.dumps(rep.sidecar()))["config"]["K"] == 3
    assert DegreeZero(K=np.int64(3)).fit(X, None, _days(30)).config["K"] == 3


def test_transform_panel_rejects_empty_panel():
    X = 0.01 * _rng(16).standard_normal((20, 6))
    for rep in (CenteredRanks().fit(X, None, _days(20)), PCAOrthogonal(K=2).fit(X, None, _days(20))):
        with pytest.raises(ValueError, match="at least one day"):
            rep.transform_panel(np.zeros((0, 6)))


def test_sidecar_is_detached_from_state():
    X = 0.01 * _rng(17).standard_normal((20, 6))
    rep = PCAOrthogonal(K=2).fit(X, None, _days(20))
    h = rep.state_hash()
    side = rep.sidecar()
    side["config"]["mode"] = "full"
    side["heads"]["z_odd"]["dim"] = 999
    side["normalization"]["trace"] = -1.0
    side["fit"]["days"] = -1
    side["channels"]["market"] = [9]
    fresh = rep.sidecar()
    assert fresh["config"]["mode"] == "factor" and fresh["heads"]["z_odd"]["dim"] == 3
    assert fresh["normalization"]["trace"] > 0 and fresh["fit"]["days"] == 20
    assert fresh["channels"]["market"] == [0]
    assert rep.state_hash() == h


def test_cli_rejects_options_the_representation_lacks():
    with pytest.raises(SystemExit):
        extract.main(["--dataset", "d2_us97", "--rep", "ranks", "--mode", "factor", "--out", "unused"])


def test_import_isolation():
    banned = ("jepadrift.monitors", "jepadrift.injection", "torch")
    for path in sorted((REPO / "jepadrift" / "representations").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""] + [f"{node.module}.{a.name}" for a in node.names]
            else:
                continue
            assert not any(n == b or n.startswith(b + ".") for n in names for b in banned), (path.name, names)
