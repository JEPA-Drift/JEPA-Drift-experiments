"""Tests of the IPCA representation (stream 17): jepadrift/representations/ipca.py and its extraction."""
import hashlib

import numpy as np
import pandas as pd
import pytest
from scipy.linalg import subspace_angles

from experiments import ipca_k_selection as ks
from jepadrift.data_loader import chars, sp500
from jepadrift.representations import extract, ipca
from jepadrift.representations.ipca import IPCA

GAMMA = np.linalg.qr(np.random.default_rng(np.random.SeedSequence([17, 0])).standard_normal((4, 2)))[0]


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([17, *key]))


def _days(T, start):
    return np.datetime64(start) + np.arange(T)


def _panel(T, N, seed):
    g = _rng(1, seed)
    C = g.uniform(-0.5, 0.5, (T, N, 4))
    F = g.standard_normal((T, 2)) * np.array([2.0, 1.0])
    X = np.einsum("tip,pk,tk->ti", C, GAMMA, F) + g.standard_normal((T, N))
    X[g.random((T, N)) < 0.15] = np.nan
    X[T // 4:T // 4 + 60, :20] = np.nan
    return X, C


@pytest.fixture(scope="module")
def synthetic():
    Xp, Cp = _panel(1200, 150, 1)
    Xc, Cc = _panel(600, 150, 2)
    return Xp, Cp, _days(1200, "2008-01-02"), Xc, Cc, _days(600, "2016-01-04")


def _fitted(data, **kw):
    Xp, Cp, dp, Xc, Cc, dc = data
    rep = IPCA(**kw)
    rep.pretrain(Xp, Cp, dp)
    return rep.fit(Xc, Cc, dc)


@pytest.fixture(scope="module")
def fitted(synthetic):
    return _fitted(synthetic)


@pytest.fixture(scope="module")
def fitted_cn(synthetic):
    return _fitted(synthetic, cash_neutral="constant")


def test_recovery_principal_angles(fitted):
    assert fitted.stats["K"] == 2 and fitted.stats["candidates"] == [1, 2, 3, 4]
    assert np.degrees(subspace_angles(fitted.state["Gamma"], GAMMA)).max() < 5.0
    assert fitted.stats["used_days_calib"] == 600 and fitted.stats["excluded_calib"] == []


def test_als_projector_stopping(synthetic):
    seg = ipca.segment(synthetic[0], synthetic[1], None)
    args = (seg["W"], seg["Y"], seg["n"], seg["ss"], 2)
    G, info = ipca.als(*args)
    objective = np.asarray(info["objective"])
    assert (np.diff(objective) <= 1e-12 * objective[:-1]).all() and info["projector_change"] <= ipca.TOL
    assert np.abs(G.T @ G - np.eye(2)).max() <= 1e-12
    M = ipca.factors(seg["W"], seg["Y"], G)
    M = M.T @ M
    assert abs(M[0, 1]) <= 1e-10 * M[0, 0] and M[0, 0] > M[1, 1]
    assert (G[np.abs(G).argmax(axis=0), [0, 1]] > 0).all()
    turn = np.array([[np.cos(1.0), -np.sin(1.0)], [np.sin(1.0), np.cos(1.0)]])
    for G0 in (-G, G @ turn):
        G2, _ = ipca.als(*args, G0=G0)
        assert np.abs(G2 @ G2.T - G @ G.T).max() <= 1e-8 and np.abs(G2 - G).max() <= 1e-8
    with pytest.raises(RuntimeError, match="converge"):
        ipca.als(*args, G0=_rng(4).standard_normal((4, 2)), max_iter=2)


def test_missing_is_not_zero(fitted, synthetic):
    C = synthetic[4][5]
    x = np.nan_to_num(synthetic[3][5], nan=0.01)
    x[7] = np.nan
    keep = np.isfinite(x)
    f = np.linalg.lstsq(C[keep] @ fitted.state["Gamma"], x[keep], rcond=None)[0]
    z = fitted.transform_day(x, C)["z_odd"]
    assert np.abs(z - fitted.state["W"] @ f).max() <= 1e-12
    zero = x.copy()
    zero[7] = 0.0
    assert np.abs(fitted.transform_day(zero, C)["z_odd"] - z).max() > 1e-8
    empty = fitted.transform_day(np.full(len(x), np.nan), C)
    assert not empty["z_odd"].any() and np.isfinite(empty["z_even"]).all()
    for bad_x, bad_C in ((np.where(keep, x, np.inf), C), (x, np.where(C > 0.4, np.inf, C))):
        with pytest.raises(ValueError, match="infinite"):
            fitted.transform_day(bad_x, bad_C)


def test_rank_bound_and_deficient_days(synthetic):
    Xp, Cp, dp, Xc, Cc, dc = synthetic
    with pytest.raises(ValueError, match="identifiable"):
        IPCA(K=5).pretrain(Xp, Cp, dp)
    assert sorted(IPCA(K_max=2).pretrain(Xp, Cp, dp).pretrain_info["als"]) == ["1", "2"]
    Xd, Cd = Xc.copy(), Cc.copy()
    Xd[10, 3:] = np.nan
    Cd[20, :, 1] = 0.3
    for cash_neutral, deficient in ((None, [10]), ("constant", [10, 20])):
        rep = _fitted((Xp, Cp, dp, Xd, Cd, dc), cash_neutral=cash_neutral)
        assert rep.stats["excluded_calib"] == [str(dc[t]) for t in deficient]
        Z = rep.transform_panel(Xd, Cd)["z_odd"]
        assert not Z[np.ix_(deficient, rep.channels["residual"])].any()
        G = rep.state["Gamma"]
        for t in sorted(set(range(len(Xd))) - set(deficient)):
            assert np.linalg.matrix_rank(ipca.design(Xd[t], Cd[t], cash_neutral)[0] @ G) == G.shape[1]


def _heldout_reference(X, C, G, cash_neutral):
    even = np.arange(X.shape[1]) % 2 == 0
    ssr = sst = 0.0
    for x, c in zip(X, C):
        for a in (even, ~even):
            ia, ib = np.isfinite(x) & a, np.isfinite(x) & ~a
            Ca, xa, Cb, xb = np.nan_to_num(c[ia]), x[ia], np.nan_to_num(c[ib]), x[ib]
            if cash_neutral:
                Ca, xa, Cb, xb = Ca - Ca.mean(axis=0), xa - xa.mean(), Cb - Cb.mean(axis=0), xb - xb.mean()
            f = np.linalg.lstsq(Ca @ G, xa, rcond=None)[0]
            ssr += np.sum((xb - Cb @ G @ f) ** 2)
            sst += np.sum(xb ** 2)
    return 1.0 - ssr / sst


@pytest.mark.parametrize("cash_neutral, target", [(None, "returns"), ("constant", "relative_returns")])
def test_heldout_r2_definition(synthetic, fitted, fitted_cn, cash_neutral, target):
    rep = fitted_cn if cash_neutral else fitted
    K = rep.stats["K"]
    want = _heldout_reference(synthetic[3], synthetic[4], rep.state["Gamma"], cash_neutral)
    assert abs(rep.stats["r2_heldout_calib"][K - 1] - want) <= 1e-10
    assert rep.stats["r2_target"] == target and rep.stats["fold_skips"] == [0, 0, 0, 0]


def test_whitening_uncentered(fitted, synthetic):
    Z = fitted.transform_panel(synthetic[3], synthetic[4])["z_odd"]
    assert np.abs(Z.T @ Z / len(Z) - np.eye(Z.shape[1])).max() <= 1e-10
    assert not fitted.transform_day(np.zeros(synthetic[3].shape[1]), synthetic[4][0])["z_odd"].any()


@pytest.mark.parametrize("cash_neutral", [None, "constant"])
def test_odd_head_exact(synthetic, fitted, fitted_cn, cash_neutral):
    rep = fitted_cn if cash_neutral else fitted
    Xc, Cc = synthetic[3], synthetic[4]
    assert np.isnan(Xc[::25]).any(axis=1).all()
    for x, c in zip(Xc[::25], Cc[::25]):
        a, b = rep.transform_day(x, c), rep.transform_day(-x, c)
        assert np.array_equal(b["z_odd"], -a["z_odd"]) and np.array_equal(b["z_even"], a["z_even"])


def test_cash_neutral_invariance(fitted_cn, synthetic):
    assert fitted_cn.channels == {"market": [0], "residual": [1, 2]}
    x, c = synthetic[3][7], synthetic[4][7]
    z = fitted_cn.transform_day(x, c)["z_odd"]
    for shift in (0.02, -1.5):
        moved = fitted_cn.transform_day(x + shift, c)["z_odd"]
        assert np.abs(moved[1:] - z[1:]).max() <= 1e-10
        assert abs(moved[0] - z[0] - shift / fitted_cn.state["s_market"][0]) <= 1e-10


def test_pretrain_calib_separation(synthetic):
    Xp, Cp, dp, Xc, Cc, dc = synthetic
    with pytest.raises(ValueError, match="pretrain"):
        IPCA().fit(Xc, Cc, dc)
    base = _fitted(synthetic, K=2)
    moved_calib, moved_pretrain = Xc.copy(), Xp.copy()
    moved_calib[30] *= 3.0
    moved_pretrain[30] *= 3.0
    rep = _fitted((Xp, Cp, dp, moved_calib, Cc, dc), K=2)
    assert np.array_equal(rep.state["Gamma"], base.state["Gamma"]) and not np.array_equal(rep.state["W"], base.state["W"])
    rep = _fitted((moved_pretrain, Cp, dp, Xc, Cc, dc), K=2)
    assert not np.array_equal(rep.state["Gamma"], base.state["Gamma"])
    side = base.sidecar()
    assert (side["pretrain"]["first_day"], side["pretrain"]["days"]) == (str(dp[0]), 1200)
    assert side["pretrain"]["x_sha256"] == hashlib.sha256(Xp.tobytes()).hexdigest()
    assert side["pretrain"]["c_sha256"] == hashlib.sha256(Cp.tobytes()).hexdigest()
    assert (side["fit"]["first_day"], side["fit"]["days"]) == (str(dc[0]), 600)


def test_extract_monitor_rows_do_not_move_state(tmp_path):
    ret, dates, _ = sp500.load_d3_239()
    splits = sp500.load_splits("d3_239")
    cut = int(np.searchsorted(dates, np.datetime64("2020-01-01")))
    X = np.where(chars.load_universe("d3_239"), ret, np.nan)
    C = chars.load_continuous_chars("d3_239")
    runs = []
    for k in (1, 2):
        Xk, Ck = X.copy(), C.copy()
        Xk[cut:] = 0.01 * _rng(10, k).standard_normal(Xk[cut:].shape)
        Ck[cut:] = _rng(11, k).uniform(-0.5, 0.5, Ck[cut:].shape)
        npz, side = extract.extract(IPCA(), Xk, dates, splits, tmp_path / str(k), "d3_239", C=Ck)
        with np.load(npz) as z:
            runs.append((z["Z_odd"], side))
    (Za, a), (Zb, b) = runs
    assert a["state_sha256"] == b["state_sha256"] and a["pretrain"] == b["pretrain"]
    assert a["normalization"] == b["normalization"] and a["c_sha256"] != b["c_sha256"]
    n = cut - a["rows"][0]
    assert np.array_equal(Za[:n], Zb[:n]) and not np.array_equal(Za[n:], Zb[n:])


def test_extract_cli_refuses_d2_and_plain_char_datasets():
    with pytest.raises(ValueError, match="D2 has no characteristics"):
        extract.main(["--dataset", "d2_us97", "--rep", "ipca", "--out", "unused"])
    with pytest.raises(SystemExit):
        extract.main(["--dataset", "d3_500", "--rep", "pca", "--out", "unused"])
    with pytest.raises(SystemExit):
        extract.main(["--dataset", "d3_239", "--rep", "pca", "--cash-neutral", "constant", "--out", "unused"])


@pytest.fixture(scope="module")
def d3_239_rows():
    return ks.load_panel("d3_239")


def _same(a, b):
    return bool(((a == b) | (np.isnan(a) & np.isnan(b))).all())


def test_real_d3_239_selection(d3_239_rows):
    ret, X, dates, splits = d3_239_rows
    rep = ks.fit_ipca(X, chars.load_continuous_chars("d3_239", slice(0, len(ret))), dates, splits)
    csv = pd.read_csv(ks.REPO_ROOT / "results" / "ipca" / "k_selection.csv", float_precision="round_trip")
    rows = csv[(csv["dataset"] == "d3_239") & (csv["protocol"] == "principal") & (csv["cash_neutral"] == "none")]
    st, pre = rep.stats, rep.pretrain_info
    assert rows["K"].tolist() == st["candidates"] == [1, 2, 3, 4]
    assert rows.loc[rows["selected"], "K"].tolist() == [st["K"]]
    assert rows["r2_heldout_calib"].tolist() == st["r2_heldout_calib"]
    assert rows["r2_insample_calib"].tolist() == st["r2_insample_calib"]
    assert (rows["r2_target"] == "returns").all() and st["r2_target"] == "returns"
    assert (rows["c_nan_imputed_pretrain"] == pre["c_nan_imputed"]).all()
    assert (rows["c_nan_imputed_calib"] == st["c_nan_imputed_calib"]).all()
    assert (rows["state_sha256"] == rep.state_hash()).all()
    assert (ks.REPO_ROOT / "data" / "derived" / "d3_239" / f"z_{rep.state_hash()}.npz").exists()


def test_beta_denominator_reproduces_stored(d3_239_rows):
    ret, X, dates, splits = d3_239_rows
    stored = chars.load_continuous_chars("d3_239", slice(0, len(ret)))[..., 0]
    raw_stored, raw_ols, _ = ks.betas(ret, np.isfinite(X))
    assert _same(ks.rank_cs(raw_stored), stored) and not _same(ks.rank_cs(raw_ols), stored)
    csv = pd.read_csv(ks.REPO_ROOT / "results" / "ipca" / "char_audit.csv", float_precision="round_trip")
    assert csv[csv["dataset"] == "d3_239"].to_dict("records") == ks.char_audit("d3_239", ret, X, splits)


def test_char_audit_values_are_finite():
    csv = pd.read_csv(ks.REPO_ROOT / "results" / "ipca" / "char_audit.csv", float_precision="round_trip")
    assert np.isfinite(csv["value"]).all(), csv[~np.isfinite(csv["value"])]
