"""Tests of experiments/pca_info_online.py (stream 32, lot A1): mixture and OLS costs, INFO/PREFIX sets."""
import importlib.util
import itertools
import math

import numpy as np
import pytest

from experiments import pca_drift_benchmark as pdb

GAMMA = 504.0
QS = np.array([[0.25, 0.5, 0.5, 0.0, 0.125, 0.0, 0.5, 0.0625],
               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               [0.375, 0.375, 0.375, 0.375, 0.0, 0.0, 0.0, 0.0],
               [2.0, 1.0, 0.0, 0.5, 0.5, 0.25, 0.0, 0.0]])


def pio():
    spec = importlib.util.find_spec("experiments.pca_info_online")
    assert spec is not None, "experiments/pca_info_online.py is missing: lot A kernels not implemented"
    return importlib.import_module("experiments.pca_info_online")


def _ols(gamma, K, d_max=16):
    fit = range(1, min(d_max, K) + 1)
    M = {d: pdb.mixture_cost(d, gamma) for d in range(1, K + 1)}
    d_bar, m_bar = math.fsum(fit) / len(fit), math.fsum(M[d] for d in fit) / len(fit)
    c = math.fsum((d - d_bar) * (M[d] - m_bar) for d in fit) / math.fsum((d - d_bar) ** 2 for d in fit)
    return m_bar - c * d_bar, c, M


def _costs(K):
    a, c, M = _ols(GAMMA, K)
    return {"MIX": [M[d] for d in range(1, K + 1)], "AFF": [a + c * d for d in range(1, K + 1)],
            "LIN": [float(d) for d in range(1, K + 1)], "FLAT": [1.0] * K}


def _exhaustive(q, cost):
    best = min((-math.fsum(q[j] for j in S) / cost[len(S) - 1], len(S), sorted((-q[j], j) for j in S))
               for d in range(1, len(q) + 1) for S in itertools.combinations(range(len(q)), d))
    return best[1], sorted(j for _, j in best[2])


def _greedy(q, cost):
    chosen, best = [], None
    for d in range(1, len(q) + 1):
        chosen.append(min((j for j in range(len(q)) if j not in chosen), key=lambda j: (-q[j], j)))
        v = math.fsum(q[j] for j in chosen) / cost[d - 1]
        if best is None or v > best[0]:
            best = (v, d, sorted(chosen))
    return best[1], best[2]


def _prefix(q, cost):
    v = [math.fsum(q[:d]) / cost[d - 1] for d in range(1, len(q) + 1)]
    d = v.index(max(v)) + 1
    return d, list(range(d))


def _rows(Q, cost, order):
    d, mask = pio().best_sets(np.asarray(Q, dtype=np.float64), np.asarray(cost, dtype=np.float64), order)
    assert d.shape == (len(Q),) and mask.shape == np.shape(Q) and mask.dtype == bool
    assert (mask.sum(axis=1) == d).all()
    return [(int(d[i]), np.flatnonzero(mask[i]).tolist()) for i in range(len(Q))]


def test_mixture_cost_is_reused():
    m = pio()
    assert m.mixture_cost is pdb.mixture_cost
    x, a = m.mixture_cost(4, GAMMA) * math.log(GAMMA), math.log(GAMMA)
    assert round(m.mixture_cost(4, GAMMA), 4) == 1.5696
    assert x == pytest.approx(a + 2.0 * math.log1p(x / 2.0), rel=1e-12)


@pytest.mark.parametrize("K", [2, 8, 20])
def test_affine_ols_distinct_from_chord(K):
    m = pio()
    a, c, info = m.affine_ols(GAMMA, K)
    ra, rc, M = _ols(GAMMA, K)
    assert a > 0 and c > 0 and a == pytest.approx(ra, rel=1e-12) and c == pytest.approx(rc, rel=1e-12)
    assert (a, c) != pytest.approx(pdb.affine_costs(GAMMA), rel=1e-3)
    assert info["identity"] == "AFF_OLS_1_16" and tuple(info["range"]) == (1, min(16, K))
    resid = [abs(M[d] - ra - rc * d) for d in range(1, K + 1)]
    assert info["max_abs_resid_fit"] == pytest.approx(max(resid[:16]), rel=1e-9, abs=1e-14)
    assert info["max_abs_resid_1K"] == pytest.approx(max(resid), rel=1e-9, abs=1e-14)
    costs = m.cost_vectors(GAMMA, K)
    assert sorted(costs) == ["AFF", "MIX"] and np.shape(costs["MIX"]) == np.shape(costs["AFF"]) == (K,)
    np.testing.assert_allclose(costs["MIX"], [M[d] for d in range(1, K + 1)], rtol=1e-14)
    np.testing.assert_allclose(costs["AFF"], a + c * np.arange(1, K + 1), rtol=1e-14)
    assert (np.asarray(costs["AFF"]) > 0).all()
    for bad in ((GAMMA, 1), (GAMMA, 20, 1)):
        with pytest.raises(ValueError):
            m.affine_ols(*bad)


@pytest.mark.parametrize("K", [2, 5, 8])
def test_info_sort_equals_greedy_equals_exhaustive(K):
    for name, cost in _costs(K).items():
        for q, sel in zip(QS[:, :K], _rows(QS[:, :K], cost, "INFO")):
            assert sel == _exhaustive(q, cost) == _greedy(q, cost), (name, q.tolist())


def test_adjacent_tie_strictly_decreasing_q():
    for order in ("INFO", "PREFIX"):
        assert _rows([[2.0, 1.0]], [2.0, 3.0], order) == [(1, [0])]


def test_prefix_full_enumeration_non_monotone():
    q = [0.0, 0.0, 3.0, 0.0, 1.0]
    cost = [pdb.mixture_cost(d, GAMMA) for d in range(1, 6)]
    assert _rows([q], cost, "PREFIX") == [_prefix(q, cost)] == [(5, [0, 1, 2, 3, 4])]
    v = [math.fsum(q[:d]) / cost[d - 1] for d in range(1, 6)]
    assert next(i + 1 for i in range(4) if v[i + 1] <= v[i]) == 1
    assert next(i + 1 for i in range(4) if v[i + 1] < v[i]) == 3
    assert _rows([q], cost, "INFO") == [(2, [2, 4])]
    for K in (2, 5, 8):
        for table in _costs(K).values():
            assert _rows(QS[:, :K], table, "PREFIX") == [_prefix(row, table) for row in QS[:, :K]]


def test_best_sets_matches_select_top_q():
    K = 7
    Q = np.maximum(0.0, np.random.default_rng(np.random.SeedSequence([32, 6])).normal(size=(40, K)))
    for cost in _costs(K).values():
        for q, sel in zip(Q, _rows(Q, cost, "INFO")):
            ref = pdb.select_top_q(q, K, np.asarray(cost))[1]
            assert sel == (ref["d"], ref["S"])


def test_refusals_selection_and_costs():
    m = pio()
    q, cost = np.array([[0.5, 0.25, 0.0]]), np.array([1.0, 1.5, 2.0])
    cases = [(np.zeros((1, 0)), cost[:0], "INFO"), (q[0], cost, "INFO"), (-q, cost, "INFO"),
             (q * np.nan, cost, "PREFIX"), (q, cost[:2], "INFO"), (q, cost * np.inf, "INFO"),
             (q, -cost, "PREFIX"), (q, cost * 0.0, "INFO"), (q, cost, "KAISER")]
    for args in cases:
        with pytest.raises(ValueError):
            m.best_sets(*args)
    for gamma, K in ((1.0, 4), (0.5, 4), (math.inf, 4), (math.nan, 4), (GAMMA, 0), (GAMMA, 1)):
        with pytest.raises(ValueError):
            m.cost_vectors(gamma, K)


def test_best_sets_refuses_overflow_and_accepts_k1():
    m = pio()
    for q, cost in (([[1e308, 1e308]], [1.0, 3.0]), ([[1.0, 0.0]], [1e-320, 1e-320])):
        for order in ("INFO", "PREFIX"):
            with pytest.raises(ArithmeticError):
                m.best_sets(np.array(q), np.array(cost), order)
    for order in ("INFO", "PREFIX"):
        d, mask = m.best_sets(np.array([[0.0], [0.5]]), np.array([1.0]), order)
        assert d.tolist() == [1, 1] and mask.dtype == bool and mask.shape == (2, 1) and mask.all()


S2 = 2.0 * math.log(12 / 0.05) / (12 * 4)
AXIS0 = [True, False, False, False]


def _kernel(name):
    module = pio()
    assert hasattr(module, name), f"experiments/pca_info_online.py lacks {name}: lot A2 kernel not implemented"
    return getattr(module, name)


def _paths():
    Y = np.random.default_rng(np.random.SeedSequence([32, 9])).integers(-6, 7, size=(4, 10, 4)) / 4.0
    Y[1] = 0.0
    Y[2, :, 2] = Y[2, :, 1]
    Y[3] = 0.0
    Y[3, :5, 3] = 2.0
    Y[3, 5:, 0] = 2.0
    return Y


def _ref_masks(Y, window, cost, order):
    select = _exhaustive if order == "INFO" else _prefix
    M = np.zeros(Y.shape, dtype=bool)
    for b, path in enumerate(Y):
        past = []
        for t, y in enumerate(path):
            m = min(window, len(past))
            if m == 0:
                S = [0]
            else:
                mean = [math.fsum(p[k] for p in past[-m:]) / m for k in range(Y.shape[2])]
                S = select([0.5 * max(0.0, mu * mu - 1.0 / m) for mu in mean], cost)[1]
            M[b, t, S] = True
            past.append(y)
    return M


def _scan_case():
    g = np.random.default_rng(np.random.SeedSequence([32, 12]))
    Y, M = g.integers(-4, 5, size=(5, 12, 4)) / 4.0, g.random((5, 12, 4)) < 0.5
    Y[0, :, 1], M[0] = 1.5, False
    M[0, :, 1] = True
    Y[1, :8, 2], M[1] = 9.0, False
    M[1, 8:, 2] = True
    M[2] = False
    M[:, :, 3] = False
    return Y, M


def _ref_loglik(y, m, s2):
    H, K = y.shape
    out = np.full((H, H), np.nan)
    for t in range(1, H + 1):
        for tau in range(1, t + 1):
            terms = []
            for k in range(K):
                sel = [float(y[i, k]) for i in range(tau - 1, t) if m[i, k]]
                n, D = len(sel), math.fsum(sel)
                terms.append(-0.5 * math.log1p(n * s2) + s2 * D * D / (2.0 * (1.0 + n * s2)))
            out[t - 1, tau - 1] = math.fsum(terms)
    return out


def _ref_W(Y, M, s2):
    return np.array([np.nanmax(_ref_loglik(y, m, s2), axis=1) for y, m in zip(Y, M)])


def _first(w, h):
    hit = np.flatnonzero(w >= h)
    return int(hit[0]) + 1 if hit.size else -1


def _safe_h(W):
    v = np.unique(W)
    i = int(np.argmax(np.diff(v)))
    return float(0.5 * (v[i] + v[i + 1]))


def test_online_masks_predictable():
    online, Y, cost = _kernel("online_masks"), _paths(), np.array(_costs(4)["MIX"])
    for order in ("INFO", "PREFIX"):
        M = online(Y, 3, cost, order)
        for t in (1, 4, 9):
            Z = Y.copy()
            Z[:, t - 1] += 8.0
            F = Z.copy()
            F[:, t:] *= -4.0
            N = online(Z, 3, cost, order)
            np.testing.assert_array_equal(N[:, :t], M[:, :t])
            np.testing.assert_array_equal(online(F, 3, cost, order)[:, :t], M[:, :t])
            assert (N[1, t] != M[1, t]).any()


def test_online_masks_onset_and_direction_invariance():
    import inspect
    online, Y, cost = _kernel("online_masks"), _paths(), np.array(_costs(4)["AFF"])
    assert list(inspect.signature(online).parameters) == ["Y", "window", "cost", "order"]
    drifts = ((6, np.array([2.0, 0.0, -1.0, 0.5])), (8, np.array([0.0, -2.0, 0.0, 1.5])))
    for order in ("INFO", "PREFIX"):
        base, outs = online(Y, 3, cost, order), []
        for tau, u in drifts:
            Z = Y.copy()
            Z[:, tau - 1:] += u
            outs.append(online(Z, 3, cost, order))
            np.testing.assert_array_equal(outs[-1][:, :tau], base[:, :tau])
        np.testing.assert_array_equal(outs[0][:, :6], outs[1][:, :6])
        assert (outs[0] != outs[1]).any()


@pytest.mark.parametrize("order", ["INFO", "PREFIX"])
def test_online_masks_match_scalar_reference(order):
    online, Y = _kernel("online_masks"), _paths()
    for window in (1, 3, 12):
        for name, cost in _costs(4).items():
            M = online(Y, window, np.array(cost), order)
            assert M.dtype == bool and M.shape == Y.shape
            np.testing.assert_array_equal(M, _ref_masks(Y, window, cost, order), err_msg=f"{name} window={window}")
    ref = _ref_masks(Y, 3, _costs(4)["MIX"], "INFO")
    assert np.flatnonzero(ref[3, 4]).tolist() == [3] and np.flatnonzero(ref[3, 9]).tolist() == [0]


def test_online_fallback_only_canonical_axis0():
    online, Y = _kernel("online_masks"), _paths()
    for order in ("INFO", "PREFIX"):
        for cost in _costs(4).values():
            for window in (1, 3):
                M = online(Y, window, np.array(cost), order)
                assert M[:, 0].tolist() == [AXIS0] * 4 and M[1].tolist() == [AXIS0] * 10
            assert online(np.full((2, 6, 4), 0.25), 3, np.array(cost), order).tolist() == [[AXIS0] * 6] * 2
    oracle = pio().best_sets(np.array([[0.0, 0.0, 1.0, 0.0]]), np.array(_costs(4)["MIX"]), "INFO")[1]
    assert oracle.tolist() == [[False, False, True, False]]


def test_masked_scan_static_equals_scan_statistic_same_s2():
    scan, Y = _kernel("masked_scan"), _scan_case()[0]
    for S in ([1], [0, 2], [0, 1, 2, 3]):
        M = np.zeros(Y.shape, dtype=bool)
        M[..., S] = True
        ref = pdb.scan_statistic(Y[..., S], S2)[0]
        np.testing.assert_allclose(scan(Y, M, S2)[0], ref, rtol=1e-12, atol=1e-12)
        h = _safe_h(ref)
        assert scan(Y, M, S2, h)[1].tolist() == pdb.scan_statistic(Y[..., S], S2, h)[1].tolist()


def test_masked_scan_bruteforce():
    scan, (Y, M) = _kernel("masked_scan"), _scan_case()
    W, first = scan(Y, M, S2)
    ref = _ref_W(Y, M, S2)
    assert W.shape == ref.shape == (5, 12) and first.tolist() == [-1] * 5
    np.testing.assert_allclose(W, ref, rtol=1e-12, atol=1e-12)
    assert all(int(np.nanargmax(row)) == 0 for row in _ref_loglik(Y[0], M[0], S2))
    for h in (_safe_h(ref), float(ref.max()) + 1.0):
        assert scan(Y, M, S2, h)[1].tolist() == [_first(w, h) for w in ref]


def test_masked_scan_unselected_y_entry_and_zero_counts():
    scan, (Y, M) = _kernel("masked_scan"), _scan_case()
    W = scan(Y, M, S2)[0]
    np.testing.assert_array_equal(scan(np.where(M, Y, Y + 64.0), M, S2)[0], W)
    np.testing.assert_array_equal(W[2], np.zeros(12))
    np.testing.assert_array_equal(W[1, :8], np.zeros(8))
    assert W[1, 8] == pytest.approx(-0.5 * math.log1p(S2) + S2 * Y[1, 8, 2] ** 2 / (2.0 * (1.0 + S2)), rel=1e-12)
    assert scan(Y[2:3], M[2:3], S2, 0.0)[1].tolist() == [1]
    assert scan(Y[2:3], M[2:3], S2, float(np.nextafter(0.0, 1.0)))[1].tolist() == [-1]


def test_masked_scan_column_pruning_exact():
    scan, (Y, M) = _kernel("masked_scan"), _scan_case()
    assert not M[..., 3].any()
    np.testing.assert_array_equal(scan(Y[..., :3], M[..., :3], S2)[0], scan(Y, M, S2)[0])


def test_masked_scan_fixed_common_s2_across_cardinalities():
    scan, Y = _kernel("masked_scan"), _scan_case()[0]
    for S in ([1], [0, 2], [0, 1, 2, 3]):
        M = np.zeros(Y.shape, dtype=bool)
        M[..., S] = True
        W = scan(Y, M, S2)[0]
        np.testing.assert_allclose(W, _ref_W(Y, M, S2), rtol=1e-12, atol=1e-12)
        if len(S) < 4:
            assert not np.allclose(W, _ref_W(Y, M, 2.0 * math.log(12 / 0.05) / (12 * len(S))), rtol=1e-6)


def test_refusals_online_masks_and_scan():
    online, scan, Y, (Z, M) = _kernel("online_masks"), _kernel("masked_scan"), _paths(), _scan_case()
    cost = np.array(_costs(4)["MIX"])
    for args in ((Y, 0, cost, "INFO"), (Y, -1, cost, "INFO"), (Y, 1.5, cost, "INFO"), (Y, True, cost, "INFO"),
                 (Y[0], 3, cost, "INFO"), (Y[:, :0], 3, cost, "INFO"), (Y[..., :0], 3, cost[:0], "INFO"),
                 (Y * np.nan, 3, cost, "PREFIX"), (Y, 3, cost[:3], "INFO"), (Y, 3, -cost, "PREFIX"),
                 (Y, 3, cost * np.inf, "INFO"), (Y, 3, cost, "KAISER")):
        with pytest.raises(ValueError):
            online(*args)
    for args in ((Z, M[..., :3], S2), (Z, M.astype(np.int8), S2), (Z[0], M[0], S2), (Z[:, :0], M[:, :0], S2),
                 (Z[..., :0], M[..., :0], S2), (np.where(M, np.inf, Z), M, S2), (Z, M, 0.0), (Z, M, -S2),
                 (Z, M, math.nan), (Z, M, math.inf), (Z, M, np.array([S2, S2]))):
        with pytest.raises(ValueError):
            scan(*args)


def test_online_masks_integer_window_types():
    online, Y, cost = _kernel("online_masks"), _paths(), np.array(_costs(4)["MIX"])
    for order in ("INFO", "PREFIX"):
        np.testing.assert_array_equal(online(Y, np.uint64(3), cost, order), online(Y, 3, cost, order))
        full = online(Y, Y.shape[1], cost, order)
        for window in (np.uint64(np.iinfo(np.uint64).max), 2 ** 80):
            np.testing.assert_array_equal(online(Y, window, cost, order), full)


TAIL6 = 0.05 / 6
DELTAS = (-0.99, -0.5, -0.1, -0.001, 0.0, 0.001, 0.1, 0.5, 0.99)
TANGO_AUDIT = ((0, 0, -0.0028573816149894036, 0.0028573816149894057),
               (1, 0, -0.00235881030576852, 0.003788727564317297),
               (0, 1, -0.0037887275643172977, 0.0023588103057685197),
               (50, 20, 0.005201831650522517, 0.025824086052418996),
               (20, 50, -0.025824086052418996, -0.005201831650522517),
               (1000, 1000, -0.05345448171071382, 0.05345448171071382),
               (2000, 0, 0.9942852367700168, 1.0),
               (0, 2000, -1.0, -0.9942852367699733),
               (999, 1001, -0.05445159767822129, 0.0524573124414512))


def _q_numeric(b, c, n, delta):
    from scipy.optimize import minimize_scalar
    lo, hi = max(0.0, -delta), (1.0 - delta) / 2.0

    def nll(q):
        terms = ((b, q + delta), (c, q), (n - b - c, 1.0 - 2.0 * q - delta))
        if any(count > 0 and p <= 0.0 for count, p in terms):
            return math.inf
        return -math.fsum(count * math.log(p) for count, p in terms if count > 0)

    x = minimize_scalar(nll, bounds=(lo, hi), method="bounded", options={"xatol": 1e-13}).x
    return min((lo, hi, float(x)), key=nll)


def test_tango_constrained_mle_and_audit_intervals():
    qtilde, tango = _kernel("_tango_qtilde"), _kernel("tango_interval")
    grids = ((2000, [(b, c) for b, c, _, _ in TANGO_AUDIT]), (1, [(0, 0), (1, 0), (0, 1)]))
    for n, counts in grids:
        for (b, c), delta in itertools.product(counts, DELTAS):
            q = qtilde(b, c, n, delta)
            assert max(0.0, -delta) <= q <= (1.0 - delta) / 2.0, (b, c, n, delta)
            assert abs(q - _q_numeric(b, c, n, delta)) <= 1e-7, (b, c, n, delta)
    for b, c, lo, hi in TANGO_AUDIT:
        got = tuple(tango(b, c, 2000, TAIL6))
        assert got == pytest.approx((lo, hi), abs=1e-12), (b, c)
        assert tuple(tango(c, b, 2000, TAIL6)) == pytest.approx((-hi, -lo), abs=1e-12), (b, c)
        assert -1.0 <= got[0] <= (b - c) / 2000 <= got[1] <= 1.0
    assert tango(2000, 0, 2000, TAIL6)[1] == 1.0 and tango(0, 2000, 2000, TAIL6)[0] == -1.0
    for tail in (TAIL6, 0.025):
        for b, c in ((1, 0), (0, 1), (0, 0)):
            lo, hi = tango(b, c, 1, tail)
            assert -1.0 <= lo <= b - c <= hi <= 1.0
            assert tuple(tango(c, b, 1, tail)) == pytest.approx((-hi, -lo), abs=1e-12)
        assert tango(1, 0, 1, tail)[1] == 1.0 and tango(0, 1, 1, tail)[0] == -1.0


def test_tango_zero_discordance_closed_form():
    from scipy.stats import norm
    tango = _kernel("tango_interval")
    for n, tail in ((2000, TAIL6), (1, TAIL6), (500, 0.025)):
        lo, hi = tango(0, 0, n, tail)
        z2 = norm.isf(tail) ** 2
        assert lo == -hi and hi > 0.0 and hi == pytest.approx(z2 / (n + z2), rel=1e-12), (n, tail)
    assert tango(0, 0, 2000, TAIL6)[1] == pytest.approx(0.002857381614961041, abs=1e-15)


def test_cp_bounds_and_null_tristate():
    from scipy.stats import binom
    from statsmodels.stats.proportion import proportion_confint
    cp, status = _kernel("cp_bounds"), _kernel("null_status")
    n, alpha, eps, tail = 2000, 0.05, 0.01, 0.05
    limit = alpha + eps
    assert limit == 0.060000000000000005

    def st(k):
        return status(k, n, alpha, eps, tail)

    for k, total in ((0, n), (1, n), (102, n), (103, n), (n - 1, n), (n, n), (0, 1), (1, 1)):
        ref = proportion_confint(k, total, alpha=2 * tail, method="beta")
        np.testing.assert_allclose(cp(k, total, tail), ref, rtol=1e-12, atol=1e-15, err_msg=f"k={k} n={total}")
    low, up = proportion_confint(np.arange(n + 1), n, alpha=2 * tail, method="beta")
    kstar = int(np.argmax(low > limit))
    assert int(np.flatnonzero(up <= limit).max()) == 102 and kstar > 103 and low[kstar - 1] <= limit
    ref_status = np.where(up <= limit, "NULL_VALIDATED", np.where(low > limit, "NULL_FAILED", "NULL_INCONCLUSIVE"))
    assert [st(k) for k in range(n + 1)] == ref_status.tolist()
    assert (st(102), st(103), st(kstar - 1), st(kstar)) == ("NULL_VALIDATED", "NULL_INCONCLUSIVE",
                                                           "NULL_INCONCLUSIVE", "NULL_FAILED")
    assert (st(0), st(n)) == ("NULL_VALIDATED", "NULL_FAILED")
    assert binom.cdf(102, n, alpha) == pytest.approx(0.6067391237795827, abs=1e-12)


def test_refusals_counts_tails_and_integer_types():
    names = ("_tango_qtilde", "tango_interval", "cp_bounds", "null_status")
    qtilde, tango, cp, status = [_kernel(name) for name in names]
    for b, c, n in ((0, 0, 0), (3, 0, 2), (-1, 0, 10), (0, -1, 10), (1.5, 0, 10), (True, 0, 10), (0, 0, True)):
        with pytest.raises(ValueError):
            tango(b, c, n, TAIL6)
        with pytest.raises(ValueError):
            qtilde(b, c, n, 0.0)
    for delta in (-1.0, 1.0, 1.5, math.nan):
        with pytest.raises(ValueError):
            qtilde(1, 0, 10, delta)
    for tail in (0.0, 0.5, -0.1, 1.0, math.nan, math.inf):
        for call, args in ((tango, (1, 0, 10, tail)), (cp, (1, 10, tail)), (status, (1, 10, 0.05, 0.01, tail))):
            with pytest.raises(ValueError):
                call(*args)
    for k, n in ((0, 0), (-1, 10), (11, 10), (1.5, 10), (True, 10), (1, True)):
        with pytest.raises(ValueError):
            cp(k, n, 0.05)
        with pytest.raises(ValueError):
            status(k, n, 0.05, 0.01, 0.05)
    for alpha, eps in ((math.nan, 0.01), (0.05, math.inf)):
        with pytest.raises(ValueError):
            status(1, 10, alpha, eps, 0.05)
    assert tango(np.uint64(20), np.uint64(50), np.uint64(2000), TAIL6) == tango(20, 50, 2000, TAIL6)
    assert cp(np.uint64(103), np.uint64(2000), 0.05) == cp(103, 2000, 0.05)
    assert status(np.int64(103), np.uint64(2000), 0.05, 0.01, 0.05) == "NULL_INCONCLUSIVE"


def test_affine_ols_refuses_nonpositive_or_nonfinite_line(monkeypatch):
    m = pio()
    for fake in (lambda d, gamma: 2.0 - 0.01 * d, lambda d, gamma: 0.1 * d - 0.5, lambda d, gamma: math.nan):
        monkeypatch.setattr(m, "mixture_cost", fake)
        with pytest.raises(ArithmeticError):
            m.affine_ols(GAMMA, 20)


def test_tango_score_finite_at_lower_endpoint():
    from scipy.stats import norm
    score, z, a = _kernel("_tango_score"), norm.isf(TAIL6), math.nextafter(-1.0, 0.0)
    for n in (1, 2000):
        neg, pos = score(0, n, n, a), score(n, 0, n, -a)
        assert math.isfinite(neg) and -z < neg < 0.0, (n, neg)
        assert math.isfinite(pos) and 0.0 < pos < z, (n, pos)


def _bias_enumeration(xs, ps, m):
    from fractions import Fraction
    mean = sum(p * x for x, p in zip(xs, ps))
    var = sum(p * (x - mean) ** 2 for x, p in zip(xs, ps))
    expect = Fraction(0)
    for draw in itertools.product(range(3), repeat=m):
        bhat = sum(xs[i] for i in draw) / m
        expect += math.prod(ps[i] for i in draw) * (bhat * bhat - Fraction(1, m)) / 2
    return mean, var, expect


def test_null_score_bias_exact_three_point_enumeration():
    from fractions import Fraction as Fr
    bias = _kernel("null_score_bias")
    quarter, eighth = (Fr(1, 4), Fr(1, 2), Fr(1, 4)), (Fr(1, 8), Fr(3, 4), Fr(1, 8))
    laws = (((-2, 0, 2), eighth), ((-1, 1, 3), quarter), ((0, 1, 2), eighth), ((-1, 0, 1), quarter),
            ((Fr(1, 2),) * 3, quarter))
    for (xs, ps), m in itertools.product(laws, (1, 2, 3)):
        mean, var, expect = _bias_enumeration([Fr(x) for x in xs], ps, m)
        assert expect == (mean * mean + (var - 1) / m) / 2, (xs, m)
        got = bias(float(mean), float(var), m)
        assert math.isclose(got, float(expect), rel_tol=1e-15, abs_tol=1e-16), (xs, m, got)
        assert (got < 0.0) == (expect < 0) and (got == 0.0) == (expect == 0), (xs, m, got)
    assert [bias(0.0, 1.0, m) for m in (1, 2, 3)] == [0.0, 0.0, 0.0]
    np.testing.assert_allclose(bias(np.array([0.0, 1.0, 0.5]), np.array([1.0, 2.0, 0.0]), 2), [0.0, 0.75, -0.125])
    for c, v, m in ((0.0, 1.0, 0), (0.0, 1.0, -1), (0.0, 1.0, 1.5), (0.0, 1.0, True), (math.nan, 1.0, 1),
                    (math.inf, 1.0, 1), (0.0, math.nan, 1), (0.0, -0.25, 1), (np.array([0.0, math.nan]), 1.0, 1)):
        with pytest.raises(ValueError):
            bias(c, v, m)


PLAN = {"alpha": 0.05, "m": 3, "eps": 0.01, "eps_v": 0.01, "beta": 0.2, "eta": 0.1, "n_min": 2000, "n_cap": 20000}


def _null_counts(n, b, c, k):
    return {"n": n, "pairs": {"INFO_MIX|PREFIX_MIX": {"b": b, "c": c}, "INFO_MIX|FULL_K": {"b": b, "c": c}},
            "alarms": {"INFO_MIX": k, "PREFIX_MIX": k, "FULL_K": k}}


def _plan_ref(counts, alpha, m, eps, eps_v, beta, eta, n_min, n_cap):
    from scipy.stats import norm
    from statsmodels.stats.proportion import proportion_confint
    tango, n = _kernel("tango_interval"), counts["n"]
    za, zeq, zb, zv = (float(norm.isf(p)) for p in (alpha / m, beta / 2, beta, 0.05))

    def upper(k):
        return float(proportion_confint(k, n, alpha=2 * eta, method="beta")[1])

    pairs, policies = {}, {}
    for name, bc in counts["pairs"].items():
        D, delta = upper(bc["b"] + bc["c"]), max(abs(x) for x in tango(bc["b"], bc["c"], n, eta))
        pairs[name] = math.ceil(D * (za + zeq) ** 2 / (eps - delta) ** 2) if delta < eps else None
    for name, k in counts["alarms"].items():
        F = upper(k)
        policies[name] = math.ceil(F * (1 - F) * (zv + zb) ** 2 / (alpha + eps_v - F) ** 2) if F < alpha + eps_v else None
    sizes = [n_min, *pairs.values(), *policies.values()]
    return (None if None in sizes else max(sizes)), pairs, policies


def test_plan_holdout_matches_independent_null_sizing():
    import inspect
    import json
    from scipy.stats import norm
    plan = _kernel("plan_holdout")
    params = ["counts", "alpha", "m", "eps", "eps_v", "beta", "eta", "n_min", "n_cap"]
    assert list(inspect.signature(plan).parameters) == params
    capped_pair = _null_counts(2000, 60, 20, 20)
    capped_pair["alarms"]["INFO_MIX"] = 60
    fixtures = [_null_counts(1_000_000, 25_000, 25_000, 50_000), _null_counts(1_000_000, 50_000, 50_000, 50_000),
                _null_counts(2000, 0, 0, 0), capped_pair, _null_counts(2000, 5, 5, 130)]
    outs = []
    for counts in fixtures:
        snapshot = json.dumps(counts, sort_keys=True)
        out = plan(counts, **PLAN)
        n_hold, status, details = out
        n_req, pairs, policies = _plan_ref(counts, **PLAN)
        assert plan(counts, **PLAN) == out and json.dumps(counts, sort_keys=True) == snapshot
        json.dumps(details, allow_nan=False)
        assert details["n_req"] == n_req and PLAN["n_min"] <= n_hold <= PLAN["n_cap"]
        assert {name: row["n_eq"] for name, row in details["pairs"].items()} == pairs
        assert {name: row["n_v"] for name, row in details["policies"].items()} == policies
        capped = n_req is None or n_req > PLAN["n_cap"]
        expected = (PLAN["n_cap"], "PLAN_CAPPED_EXPECT_INCONCLUSIVE") if capped else (n_req, "PLAN_ADEQUATE")
        assert (n_hold, status) == expected
        outs.append(out)
    (h25, s25, _), (h50, s50, _), (h0, s0, _), (_, s_pair, d_pair), (_, s_f, d_f) = outs
    assert s25 == s50 == s0 == "PLAN_ADEQUATE" and 2000 < h25 < h50 < 20000 and h0 == 2000
    assert s_pair == s_f == "PLAN_CAPPED_EXPECT_INCONCLUSIVE"
    assert {row["n_eq"] for row in d_pair["pairs"].values()} == {None}
    assert {row["n_v"] for row in d_f["policies"].values()} == {None}
    assert (d_f["z_a"], d_f["z_eq"], d_f["z_b"], d_f["z_v"]) == tuple(norm.isf(p) for p in (0.05 / 3, 0.1, 0.2, 0.05))


def test_plan_holdout_cap_boundary_and_beta_half_power():
    from scipy.stats import norm
    plan, counts = _kernel("plan_holdout"), _null_counts(1_000_000, 25_000, 25_000, 50_000)
    details = plan(counts, **PLAN)[2]
    n_req, za, zeq, zb = details["n_req"], details["z_a"], details["z_eq"], details["z_b"]
    assert 2000 < n_req < 20000
    assert plan(counts, **{**PLAN, "n_cap": n_req})[:2] == (n_req, "PLAN_ADEQUATE")
    assert plan(counts, **{**PLAN, "n_cap": n_req - 1})[:2] == (n_req - 1, "PLAN_CAPPED_EXPECT_INCONCLUSIVE")
    assert (za + zeq) ** 2 == pytest.approx(11.625350336726223, rel=1e-12)
    for D, delta, expected in ((0.095, 0.0, 11045), (0.05, 0.0, 5813), (0.095, 0.003, 22539)):
        assert math.ceil(D * (za + zeq) ** 2 / (0.01 - delta) ** 2) == expected
    for z, power in ((zeq, 0.8), (zb, 0.6)):
        n_star = 0.095 * (za + z) ** 2 / 0.01 ** 2
        assert 2.0 * norm.cdf(0.01 * math.sqrt(n_star / 0.095) - za) - 1.0 == pytest.approx(power, abs=1e-12)
    pair = details["pairs"]["INFO_MIX|PREFIX_MIX"]
    assert pair["n_eq"] > math.ceil(pair["D_plus"] * (za + zb) ** 2 / (0.01 - pair["delta_abs_plus"]) ** 2)


def test_plan_holdout_refusals():
    plan, counts = _kernel("plan_holdout"), _null_counts(2000, 5, 5, 10)
    pair, alarms = "INFO_MIX|PREFIX_MIX", counts["alarms"]
    bad = [{**counts, "n": 0}, {**counts, "n": True}, {**counts, "alt": {}}, {"n": 2000, "pairs": {}},
           {**counts, "pairs": {pair: {"b": -1, "c": 0}}}, {**counts, "pairs": {pair: {"b": 1500, "c": 600}}},
           {**counts, "pairs": {pair: {"b": 1}}}, {**counts, "alarms": {**alarms, "INFO_MIX": 2001}},
           {**counts, "alarms": {**alarms, "INFO_MIX": 1.5}}, {**counts, "pairs": {"x": {"b": 5, "c": 5}}},
           {**counts, "pairs": {"INFO_MIX|UNKNOWN": {"b": 5, "c": 5}}},
           {**counts, "pairs": {"INFO_MIX|INFO_MIX": {"b": 0, "c": 0}}},
           _null_counts(2000, 10, 0, 10), _null_counts(2000, 11, 11, 10), _null_counts(2000, 5, 5, 1998)]
    for value in bad:
        with pytest.raises(ValueError):
            plan(value, **PLAN)
    for key, value in (("alpha", 0.0), ("alpha", 1.0), ("alpha", math.nan), ("m", 0), ("m", 1.5), ("m", True),
                       ("eps", 0.0), ("eps", -0.01), ("eps", math.inf), ("eps_v", 0.0), ("beta", 0.0),
                       ("beta", 1.0), ("eta", 0.0), ("eta", 0.5), ("n_min", 0), ("n_min", 1.5), ("n_cap", 1999)):
        with pytest.raises(ValueError):
            plan(counts, **{**PLAN, key: value})


@pytest.mark.parametrize("parameter", ["beta", "alpha"])
def test_plan_holdout_refuses_nonfinite_quantiles(parameter):
    plan, counts = _kernel("plan_holdout"), _null_counts(2000, 60, 20, 20)
    counts["alarms"]["INFO_MIX"] = 60
    with pytest.raises(ValueError):
        plan(counts, **{**PLAN, parameter: math.nextafter(0.0, 1.0)})


DEV_FAMILIES = ("F0_ISOTROPIC_RESIDUAL", "F1_TAIL_RESIDUAL", "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL")


def _design_cfg():
    phi = ["FITTED_LW_GAUSSIAN", 239, 0]
    sizes = {"DEV_LIB": 1, "DEV_NULL": 1, "DEV_ALT": 1, "CAL_NULL": 2, "HOLD_NULL": 1, "ALT": 1}
    rad, rule = {"q": "I_star/4", "signs": "RADEMACHER_PER_AXIS_AND_PATH"}, {"eta": 0.1, "beta": 0.2}
    return {
        "seed": 3232,
        "parameters": {"H": 250, "alpha": 0.05, "K": 20, "T_fit": 1000, "I_star": 0.25, "gamma_M": 504,
                       "gamma_M_sensitivity": 5000, "windows": [32, 128], "primary_window": 128,
                       "s2_rule": "2*ln(H/alpha)/(H*K)", "affine": "AFF_OLS_1_16", "frame": "QR_FIRST_COLUMN_ONES",
                       "spectrum": {"lambda_1": 16.0, "floor": 0.05, "scale": 6.0, "decay": 8.0}},
        "applications": {"RESIDUAL": [2, 21], "MARKET": [1, 20]},
        "families": {"F0_ISOTROPIC_RESIDUAL": {"application": "RESIDUAL", "support": "UNIFORM_SPHERE"},
                     "F1_TAIL_RESIDUAL": {"application": "RESIDUAL", "support": [18, 19, 20, 21], **rad},
                     "F2_STRUCTURED_RESIDUAL": {"application": "RESIDUAL", "support": [3, 9, 17, 21], **rad},
                     "F_HEAD_RESIDUAL": {"application": "RESIDUAL", "support": [2, 3, 4, 5], **rad},
                     "F3_MARKET": {"application": "MARKET", "support": [1], "q": "I_star", "signs": "RADEMACHER"}},
        "policies": {"online": {"orders": ["INFO", "PREFIX"], "costs": ["MIX", "AFF"], "windows": [32, 128]},
                     "oracle": {"orders": ["INFO", "PREFIX"], "costs": ["MIX", "AFF"]},
                     "static": ["FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90", "FIXED_DEV_PREFIX",
                                "FIXED_EXANTE_QBAR_MIX"]},
        "dev": {"families": list(DEV_FAMILIES), "n_lib": 1, "d_grid": [1, 2, 4, 8, 16, 20], "s2_grid": [1, 4, 16, 64],
                "criterion": "MEAN_RMST_H_EQUAL_FAMILY_WEIGHTS", "ties": "SMALLEST"},
        "null_status": {"tail": 0.05, "eps_v": 0.01},
        "bootstrap": {"B": 10000},
        "phi": {"setup": phi, "application": "RESIDUAL", "window": 128, "cost": "MIX", "m": 3, "delta_NI": 0.1,
                "claims": {"H1": "F2_STRUCTURED_RESIDUAL", "H2": "F_HEAD_RESIDUAL", "H3": "F2_STRUCTURED_RESIDUAL"}},
        "head": {"kappa_geo": 0.8, "kappa_det": 0.8},
        "modes": {"smoke": {"sizes": sizes, "null_plan": {**rule, "n_min": 1, "n_plan": 1, "n_cap": 3}},
                  "pilot": {"sizes": {**sizes, "CAL_NULL": 3}, "null_plan": None},
                  "full": {"sizes": {**sizes, "CAL_NULL": 4},
                           "null_plan": {**rule, "n_min": 2, "n_plan": 2, "n_cap": 5}}},
        "scope": {"setups": [["EXACT", 32, 0], phi], "applications": ["RESIDUAL"],
                  "families": ["F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"],
                  "policies": ["ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128", "FULL_K", "ORACLE_INFO_MIX"]},
        "envelope": {"memory_max_gib": 32, "cpu_hours_max": 4.0, "wall_seconds_per_invocation": 2700, "jobs_max": 8},
        "authorization": None,
    }


def _nested_keys(obj):
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _nested_keys(v)}
    return {k for v in obj for k in _nested_keys(v)} if isinstance(obj, (list, tuple)) else set()


def _edited(cfg, path, value):
    import copy
    out = copy.deepcopy(cfg)
    target = out
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return out


def _no_side_effects(mp, record=None):
    import builtins
    import concurrent.futures
    import io
    import os
    import pathlib
    real_builtin_open, real_io_open, real_os_open = builtins.open, io.open, os.open
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

    def trap(name):
        def fail(*args, **kwargs):
            raise AssertionError(f"side effect before authorization: {name}")
        return fail

    def guarded(real):
        def opener(file, mode="r", *args, **kwargs):
            if set(mode) & set("wax+"):
                raise AssertionError(f"write before authorization: {file}")
            if record is not None:
                record.append(pathlib.Path(file).resolve())
            return real(file, mode, *args, **kwargs)
        return opener

    def guarded_os_open(path, flags, *args, **kwargs):
        if flags & write_flags:
            raise AssertionError(f"low-level write before authorization: {path}")
        return real_os_open(path, flags, *args, **kwargs)

    for owner, name in ((np.random, "SeedSequence"), (np.random, "default_rng"), (np.random, "seed"),
                        (concurrent.futures, "ProcessPoolExecutor"), (os, "mkdir"), (os, "makedirs"), (os, "replace"),
                        (pathlib.Path, "mkdir"), (pathlib.Path, "write_text"), (pathlib.Path, "write_bytes"),
                        (pdb, "seed_key")):
        mp.setattr(owner, name, trap(name))
    mp.setattr(builtins, "open", guarded(real_builtin_open))
    mp.setattr(io, "open", guarded(real_io_open))
    mp.setattr(os, "open", guarded_os_open)


def _dev_keys(keys):
    return {k for k in keys if k[0] == "devlib" or (k[0] in ("path", "meta") and k[5] in ("DEV_NULL", "DEV_ALT"))}


def _expected_smoke_keys():
    ev, ex, fi = ("F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"), ("EXACT", 32, 0), ("FITTED_LW_GAUSSIAN", 239, 0)
    roles = {ex: {"DEV_NULL": 1, "DEV_ALT": 1, "CAL_NULL": 2, "HOLD_NULL": 1, "ALT": 1},
             fi: {"DEV_NULL": 1, "DEV_ALT": 1, "CAL_NULL": 2, "NULL_PLAN": 1, "HOLD_NULL": 3, "ALT": 1}}
    keys = {("frame", "SMOKE", 32), ("frame", "SMOKE", 239), ("fit", "SMOKE", *fi)}
    for s, counts in roles.items():
        keys |= {("path", "SMOKE", *s, r, i) for r, n in counts.items() for i in range(n)}
        keys |= {("meta", "SMOKE", *s, r, f, i) for r, n in counts.items() if r in ("CAL_NULL", "HOLD_NULL", "ALT")
                 for f in ev for i in range(n)}
        keys |= {("meta", "SMOKE", *s, "DEV_ALT", f, 0) for f in DEV_FAMILIES}
        keys |= {("devlib", "SMOKE", *s, f, 0) for f in DEV_FAMILIES} | {("boot", "SMOKE", *s, "RESIDUAL", f) for f in ev}
    return keys


def _authorized(tmp_path, monkeypatch, cfg, mode):
    describe, ident = _kernel("design_descriptor"), _kernel("design_id")
    did = ident(describe(cfg, mode))
    go = tmp_path / "prompts" / f"GO-{mode}-fixture.md"
    go.parent.mkdir(parents=True, exist_ok=True)
    go.write_text(f"Synthetic {mode} GO fixture for design {did}\nScope: {pdb.canon(cfg['scope'])}\n")
    _kernel("REPO_ROOT")
    monkeypatch.setattr(pio(), "REPO_ROOT", tmp_path)
    ref = {"path": f"prompts/GO-{mode}-fixture.md", "sha256": pdb.file_sha256(go)}
    return {**cfg, "authorization": {"stage": mode, "design_id": did, "go_reference": ref}}, did


def test_side_effect_traps_block_io_path_and_os_writes(tmp_path, monkeypatch):
    import io
    import os
    probe, seen = tmp_path / "probe.txt", []
    probe.write_text("probe")
    with monkeypatch.context() as mp:
        _no_side_effects(mp, seen)
        with io.open(probe, "rb") as handle:
            assert handle.read() == b"probe" and probe.read_text() == "probe" and probe.read_bytes() == b"probe"
        for write in (lambda: io.open(probe, "w"), lambda: probe.open("a"), lambda: open(probe, "r+"),
                      lambda: os.open(probe, os.O_WRONLY | os.O_CREAT), lambda: probe.with_suffix(".x").touch()):
            with pytest.raises(AssertionError):
                write()
    assert probe.read_text() == "probe" and seen == [probe.resolve()] * 3


def test_design_id_computable_before_any_draw(monkeypatch):
    import hashlib
    import os
    import re
    import sys
    import pandas
    import scipy
    import statsmodels
    import yaml
    describe, ident, plan = _kernel("design_descriptor"), _kernel("design_id"), _kernel("seed_plan")
    root, files, cfg = _kernel("CODE_ROOT"), _kernel("CODE_FILES"), _design_cfg()
    blas = np.show_config(mode="dicts")["Build Dependencies"]["blas"]
    environment = {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                   "pandas": pandas.__version__, "pyyaml": yaml.__version__, "statsmodels": statsmodels.__version__,
                   "blas": [blas.get("name"), blas.get("version")],
                   "variables": {k: os.environ.get(k) for k in pdb.REQUIRED_ENV}}
    code = {rel: pdb.file_sha256(root / rel) for rel in files}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        desc, keys = describe(cfg, "full"), plan(cfg, "full")
        did = ident(desc)
    assert desc == describe(cfg, "full") and did == hashlib.sha256(pdb.canon(desc).encode()).hexdigest()
    assert re.fullmatch("[0-9a-f]{64}", did) and desc["seed_plan_sha256"] == keys["sha256"]
    assert set(desc) == {"schema_version", "mode", "campaign", "science", "sizes", "null_plan", "scope", "envelope",
                         "seed", "seed_plan_sha256", "spectrum_sha", "code", "environment"}
    science = ("parameters", "applications", "families", "policies", "dev", "null_status", "bootstrap", "phi", "head")
    assert desc["science"] == {key: cfg[key] for key in science} and desc["null_plan"]["n_cap"] == 5
    meta = [desc[k] for k in ("schema_version", "mode", "campaign", "seed")]
    assert meta == ["pca_info_online/1", "full", "FULL", 3232]
    assert [desc[k] for k in ("sizes", "null_plan")] == [cfg["modes"]["full"][k] for k in ("sizes", "null_plan")]
    assert (desc["scope"], desc["envelope"]) == (cfg["scope"], cfg["envelope"])
    assert desc["spectrum_sha"] == hashlib.sha256(pdb.canon(cfg["parameters"]["spectrum"]).encode()).hexdigest()
    assert {"experiments/pca_info_online.py", "experiments/pca_drift_benchmark.py", "jepadrift/pipelines.py",
            "jepadrift/representations/pca.py"} <= set(files)
    assert desc["code"] == code and desc["environment"] == environment
    assert not _nested_keys(desc) & {"authorization", "go_reference", "jobs", "output_dir", "log_dir", "resume",
                                     "telemetry", "basis_sha", "fit_hash", "dev_id", "thresholds", "n_hold",
                                     "partitions", "realization_id"}
    for bad, mode in (({**cfg, "code": {}}, "full"), ({**cfg, "environment": {}}, "full"),
                      ({k: v for k, v in cfg.items() if k != "head"}, "full"), (cfg, "campaign")):
        with pytest.raises(ValueError):
            describe(bad, mode)


def test_role_keys_disjoint_and_family_free_noise(monkeypatch):
    import hashlib
    import re
    plan, cfg = _kernel("seed_plan"), _design_cfg()
    wider_cfg = _edited(cfg, ("scope", "families"), ["F1_TAIL_RESIDUAL", "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"])
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        smoke, again, full, wider = plan(cfg, "smoke"), plan(cfg, "smoke"), plan(cfg, "full"), plan(wider_cfg, "smoke")
    expected, keys = _expected_smoke_keys(), smoke["keys"]
    assert len(keys) == len(set(keys)) == len(expected) == 58 and set(keys) == expected
    assert smoke == again and not set(keys) & set(full["keys"])
    assert _dev_keys(wider["keys"]) == _dev_keys(keys) and len(_dev_keys(keys)) == 20 and set(keys) < set(wider["keys"])
    assert {k[5] for k in keys if k[0] == "devlib"} == {k[6] for k in _dev_keys(keys) if k[0] == "meta"} == set(DEV_FAMILIES)
    entropies = sorted([32, 3232, pdb.label_code(k[1]), pdb.label_code(k[0]),
                        *(pdb.label_code(p) if isinstance(p, str) else p for p in k[2:])] for k in expected)
    pdb.check_entropies(entropies)
    assert smoke["sha256"] == hashlib.sha256(pdb.canon(entropies).encode()).hexdigest() != full["sha256"]
    assert all(not set(cfg["families"]) & set(k) for k in keys if k[0] == "path")
    primary_hold = [k for k in keys if k[0] == "path" and k[2:6] == ("FITTED_LW_GAUSSIAN", 239, 0, "HOLD_NULL")]
    assert len(primary_hold) == cfg["modes"]["smoke"]["null_plan"]["n_cap"] == 3
    assert ("boot", "SMOKE", "FITTED_LW_GAUSSIAN", 239, 0, "RESIDUAL", "F_HEAD_RESIDUAL") in keys
    assert not any(isinstance(p, str) and re.fullmatch("[0-9a-f]{16,64}", p) for k in keys for p in k)
    assert plan({**cfg, "seed": 3233}, "smoke")["sha256"] != smoke["sha256"]


def test_pilot_full_authorization_without_future_digests(tmp_path, monkeypatch):
    authorize, refused, describe = _kernel("authorize"), _kernel("AuthorizationRefused"), _kernel("design_descriptor")
    uncited = tmp_path / "prompts" / "GO-uncited.md"
    for mode, other in (("pilot", "full"), ("full", "pilot")):
        cfg, did = _authorized(tmp_path, monkeypatch, _design_cfg(), mode)
        block, desc, smoke_desc = cfg["authorization"], describe(cfg, mode), describe(cfg, "smoke")
        ref = block["go_reference"]
        uncited.write_text("Synthetic GO fixture without the design identifier\n")
        bad = [None, {**block, "stage": other}, {**block, "design_id": "0" * 64},
               {**block, "go_reference": {**ref, "sha256": "0" * 64}},
               {**block, "go_reference": {**ref, "path": "prompts/missing.md"}},
               {**block, "go_reference": {**ref, "path": str(tmp_path / ref["path"])}},
               {**block, "go_reference": {"path": "prompts/GO-uncited.md", "sha256": pdb.file_sha256(uncited)}}]
        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            for jobs in (1, 3):
                assert authorize(mode, cfg, desc, jobs) == {"stage": mode, "design_id": did, "go_reference": ref}
            for value in bad:
                with pytest.raises(refused):
                    authorize(mode, {**cfg, "authorization": value}, desc, 1)
            with pytest.raises(refused):
                authorize(mode, {k: v for k, v in cfg.items() if k != "authorization"}, desc, 1)
            for jobs in (9, 0, -1, 1.5, True):
                with pytest.raises(refused):
                    authorize(mode, cfg, desc, jobs)
            smoke = authorize("smoke", {**cfg, "authorization": None}, smoke_desc, 1)
        assert smoke == {"stage": "smoke", "design_id": _kernel("design_id")(smoke_desc), "go_reference": None}


def test_altered_design_code_seed_limit_refused_before_side_effects(tmp_path, monkeypatch):
    import shutil
    authorize, refused, describe = _kernel("authorize"), _kernel("AuthorizationRefused"), _kernel("design_descriptor")
    ident, root, code = _kernel("design_id"), _kernel("CODE_ROOT"), tmp_path / "code"
    for rel in _kernel("CODE_FILES"):
        (code / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, code / rel)
    monkeypatch.setattr(pio(), "CODE_ROOT", code)
    cfg, did = _authorized(tmp_path, monkeypatch, _design_cfg(), "full")
    desc = describe(cfg, "full")
    assert authorize("full", cfg, desc, 2)["design_id"] == did
    edits = ((("seed",), 3233), (("parameters", "I_star"), 0.5), (("modes", "full", "null_plan", "n_cap"), 6),
             (("envelope", "wall_seconds_per_invocation"), 2701), (("envelope", "jobs_max"), 9),
             (("scope", "families"), ["F1_TAIL_RESIDUAL", "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"]))
    for path, value in edits:
        bad = _edited(cfg, path, value)
        bad_desc = describe(bad, "full")
        assert ident(bad_desc) != did, path
        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            with pytest.raises(refused):
                authorize("full", bad, bad_desc, 2)
    victim = code / "experiments" / "pca_info_online.py"
    data = bytearray(victim.read_bytes())
    data[-1] ^= 1
    victim.write_bytes(bytes(data))
    fresh = describe(cfg, "full")
    assert fresh["code"] != desc["code"] and ident(fresh) != did
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for stale in (desc, fresh):
            with pytest.raises(refused):
                authorize("full", cfg, stale, 2)


def test_identities_independent_of_output_dir_jobs_and_telemetry(tmp_path, monkeypatch):
    import inspect
    describe, ident, authorize = _kernel("design_descriptor"), _kernel("design_id"), _kernel("authorize")
    assert list(inspect.signature(describe).parameters) == ["cfg", "mode"]
    cfg = _design_cfg()
    desc = describe(cfg, "smoke")
    did = ident(desc)
    for sub in ("out1", "out2"):
        (tmp_path / sub).mkdir()
        monkeypatch.chdir(tmp_path / sub)
        assert describe(cfg, "smoke") == desc
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        assert [authorize("smoke", cfg, desc, jobs)["design_id"] for jobs in (1, 3, 8)] == [did] * 3
    for path, value in ((("modes", "smoke", "sizes", "CAL_NULL"), 3), (("envelope", "cpu_hours_max"), 5.0),
                        (("envelope", "memory_max_gib"), 16), (("envelope", "jobs_max"), 9)):
        assert ident(describe(_edited(cfg, path, value), "smoke")) != did


def test_smoke_or_prior_outputs_cannot_inform_design(tmp_path, monkeypatch):
    import os
    describe, cfg = _kernel("design_descriptor"), _design_cfg()
    root, files = _kernel("CODE_ROOT"), _kernel("CODE_FILES")
    expected = {(root / rel).resolve() for rel in files}
    base = describe(cfg, "pilot")
    for rel in ("results/pca_info_online/smoke_j1/manifest.json", "logs/pca_info_online/old/staging/x/design.json"):
        (tmp_path / rel).parent.mkdir(parents=True)
        (tmp_path / rel).write_text(pdb.canon({"design_id": "f" * 64, "seed": 1, "n_hold": 7}))
    monkeypatch.chdir(tmp_path)
    opened = []
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for name in ("scandir", "listdir"):
            mp.setattr(os, name, lambda *args, **kwargs: pytest.fail("directory listing while describing a design"))
        assert describe(cfg, "pilot") == base
    assert opened and set(opened) == expected


@pytest.mark.parametrize("path, alias", [(("seed",), 3232.0), (("sizes", "DEV_LIB"), True)],
                         ids=["seed_int_as_float", "dev_lib_int_as_bool"])
def test_authorize_refuses_python_equal_noncanonical_descriptor(tmp_path, monkeypatch, path, alias):
    authorize, refused = _kernel("authorize"), _kernel("AuthorizationRefused")
    describe, ident = _kernel("design_descriptor"), _kernel("design_id")
    cfg, did = _authorized(tmp_path, monkeypatch, _design_cfg(), "full")
    current = describe(cfg, "full")
    altered = _edited(current, path, alias)
    assert altered == current and ident(current) == did and ident(altered) != did
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        assert authorize("full", cfg, current, 1)["design_id"] == did
        with pytest.raises(refused):
            authorize("full", cfg, altered, 1)


def _tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def _no_draws_or_workers(mp):
    import concurrent.futures

    def fail(*args, **kwargs):
        raise AssertionError("draw or worker while opening the staging")

    for owner, name in ((np.random, "SeedSequence"), (np.random, "default_rng"), (np.random, "seed"),
                        (concurrent.futures, "ProcessPoolExecutor"), (pdb, "seed_key")):
        mp.setattr(owner, name, fail)


def test_open_staging_creates_tagged_design_record(tmp_path, monkeypatch):
    import json
    stage, describe, ident = _kernel("open_staging"), _kernel("design_descriptor"), _kernel("design_id")
    desc = describe(_design_cfg(), "smoke")
    did = ident(desc)
    record, rel = {"design_id": did, "descriptor": desc}, f"staging/{did[:16]}/design.json"
    for name, resume in (("fresh", False), ("fresh_resume", True)):
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            path = stage(tmp_path / name, desc, resume)
        assert path == tmp_path / name / "staging" / did[:16]
        text = (path / "design.json").read_text()
        assert text == pdb.canon(record) + "\n" and json.loads(text) == record
        assert not _nested_keys(json.loads(text)) & {"realization_id", "authorization", "go_reference", "jobs",
                                                     "output_dir", "log_dir", "resume", "telemetry"}
    assert set(_tree(tmp_path)) == {f"fresh/{rel}", f"fresh_resume/{rel}"}


def test_open_staging_existing_requires_resume_and_preserves_bytes(tmp_path, monkeypatch):
    stage, exists = _kernel("open_staging"), _kernel("OutputExists")
    assert exists is pdb.OutputExists
    desc = _kernel("design_descriptor")(_design_cfg(), "smoke")
    path = stage(tmp_path, desc, False)
    (path / "sentinel.bin").write_bytes(b"\x00partition-fixture\xff")
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(exists):
            stage(tmp_path, desc, False)
        assert _tree(tmp_path) == before
        assert stage(tmp_path, desc, True) == path
    assert _tree(tmp_path) == before


@pytest.mark.parametrize("case", ["wrong_full_id", "tampered", "python_equal_alias", "malformed", "missing"])
def test_open_staging_resume_refuses_corrupt_or_foreign_design(tmp_path, monkeypatch, case):
    stage, mismatch = _kernel("open_staging"), _kernel("StagingMismatch")
    desc = _kernel("design_descriptor")(_design_cfg(), "smoke")
    did = _kernel("design_id")(desc)
    design = stage(tmp_path, desc, False) / "design.json"
    other = did[:16] + ("1" if did[16] == "0" else "0") + did[17:]
    records = {"wrong_full_id": {"design_id": other, "descriptor": desc},
               "tampered": {"design_id": did, "descriptor": _edited(desc, ("seed",), 3233)},
               "python_equal_alias": {"design_id": did, "descriptor": _edited(desc, ("seed",), 3232.0)}}
    if case == "missing":
        design.unlink()
    else:
        design.write_text("{" if case == "malformed" else pdb.canon(records[case]) + "\n")
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(mismatch):
            stage(tmp_path, desc, True)
    assert _tree(tmp_path) == before


def test_open_staging_distinct_log_dirs_are_independent(tmp_path):
    stage = _kernel("open_staging")
    desc = _kernel("design_descriptor")(_design_cfg(), "smoke")
    logs = [tmp_path / run / "logs" / "same_name" for run in ("run1", "run2")]
    first, second = (stage(log_dir, desc, False) for log_dir in logs)
    assert first.name == second.name and first != second
    assert (first / "design.json").read_bytes() == (second / "design.json").read_bytes()
    (first / "sentinel.txt").write_text("only in the first staging")
    assert not (second / "sentinel.txt").exists() and stage(logs[1], desc, True) == second
    assert set(_tree(second)) == {"design.json"}


def test_open_staging_tag_collision_checks_full_design_id(tmp_path, monkeypatch):
    stage, mismatch, exists = _kernel("open_staging"), _kernel("StagingMismatch"), _kernel("OutputExists")
    describe = _kernel("design_descriptor")
    _kernel("design_id")
    first, second = describe(_design_cfg(), "smoke"), describe(_design_cfg(), "pilot")
    ids = {pdb.canon(first): "ab" * 8 + "0" * 48, pdb.canon(second): "ab" * 8 + "1" * 48}
    monkeypatch.setattr(pio(), "design_id", lambda desc: ids[pdb.canon(desc)])
    path = stage(tmp_path, first, False)
    assert path == tmp_path / "staging" / ("ab" * 8)
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(exists):
            stage(tmp_path, second, False)
        with pytest.raises(mismatch):
            stage(tmp_path, second, True)
    assert _tree(tmp_path) == before and stage(tmp_path, first, True) == path


B1C_SETUP = "EXACT|32|0"
B1C_KEYS = {"SETUP": [["SETUP", "EXACT", 32, 0, "spectrum"]], "DEV": [["DEV_NULL", "EXACT", 32, 0, "maxima"]],
            "CAL": [["CAL_NULL", "EXACT", 32, 0, "ONLINE_INFO_MIX_W128"], ["CAL_NULL", "EXACT", 32, 0, "FULL_K"]]}
B1C_FORBIDDEN = {"path", "log_dir", "output_dir", "jobs", "telemetry", "realization_id"}


def _npz_bytes(**arrays):
    import io
    buffer = io.BytesIO()
    np.savez(buffer, **arrays)
    return buffer.getvalue()


B1C_SPECTRUM = np.array([16.0] + [0.05 + 6.0 * math.exp(-(k - 2) / 8.0) for k in range(2, 22)])
B1C_CAL_ROWS = _npz_bytes(w_max=np.arange(19) / 8.0, first=np.full(19, -1))
B1C_PAYLOADS = {"SETUP": [(_npz_bytes(lam=B1C_SPECTRUM), 21)], "DEV": [(_npz_bytes(w_max=np.array([0.5])), 1)],
                "CAL": [(B1C_CAL_ROWS, 19), (B1C_CAL_ROWS, 19)]}
B1C_DERIVED = {
    "SETUP": {"setups": {B1C_SETUP: {"universe_pcs": list(range(2, 22)), "basis_sha": "a" * 64, "fit_hash": None,
                                     "static_subsets": {"FULL_K": list(range(2, 22)),
                                                        "FIXED_EIGENMEAN_PREFIX": list(range(2, 10)),
                                                        "RESIDUAL_CPV90": list(range(2, 17))},
                                     "head_geometry": {"status": "GEOMETRY_ALIGNED", "f_E_min": 1.0}}}},
    "DEV": {"setups": {B1C_SETUP: {"qbar": [0.0125] * 20, "d_dev": 4, "s2_dev": 0.0034068772765664954}}},
    "CAL": {"rule": "predictive_exchangeable_rank_v2",
            "thresholds": {f"{B1C_SETUP}|{policy}": {"n_cal": 19, "r": 0, "h": 2.2500000000000004}
                           for policy in ("ONLINE_INFO_MIX_W128", "FULL_K")}}}


def _b1c_staging(root):
    cfg = _edited(_design_cfg(), ("scope", "setups"), [["EXACT", 32, 0]])
    desc = _kernel("design_descriptor")(_edited(cfg, ("modes", "smoke", "sizes", "CAL_NULL"), 19), "smoke")
    return _kernel("open_staging")(root, desc, False), _kernel("design_id")(desc)


def _partition_stem(staging, did, upstream, key):
    import hashlib
    identity = pdb.canon({"design_id": did, "key": key, "upstream": upstream})
    return staging / "partitions" / hashlib.sha256(identity.encode()).hexdigest()


def _put_partition(staging, did, upstream, key, payload, n_rows):
    import hashlib
    stem = _partition_stem(staging, did, upstream, key)
    stem.parent.mkdir(exist_ok=True)
    stem.with_suffix(".npz").write_bytes(payload)
    sidecar = {"design_id": did, "key": key, "upstream": upstream, "fingerprint": stem.name,
               "payload_sha256": hashlib.sha256(payload).hexdigest(), "n_rows": n_rows}
    stem.with_suffix(".json").write_text(pdb.canon(sidecar) + "\n")


def _b1c_digest(did, phase, upstream):
    import hashlib
    pairs = sorted([pdb.canon(key), hashlib.sha256(payload).hexdigest()]
                   for key, (payload, _) in zip(B1C_KEYS[phase], B1C_PAYLOADS[phase]))
    identity = {"design_id": did, "phase": phase, "upstream": upstream, "partitions": pairs,
                "derived": B1C_DERIVED[phase]}
    return hashlib.sha256(pdb.canon(identity).encode()).hexdigest()


def _phase_chain(root, monkeypatch, reverse=False):
    record = _kernel("phase_record")
    staging, did = _b1c_staging(root)
    records = {}
    for phase in ("SETUP", "DEV", "CAL"):
        upstream = {p: records[p]["phase_digest"] for p in records}
        for key, (payload, rows) in zip(B1C_KEYS[phase], B1C_PAYLOADS[phase]):
            _put_partition(staging, did, upstream, key, payload, rows)
        keys, derived = B1C_KEYS[phase], B1C_DERIVED[phase]
        if reverse:
            upstream, keys, derived = dict(reversed(upstream.items())), keys[::-1], dict(reversed(derived.items()))
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            records[phase] = record(staging, phase, upstream, keys, derived)
    return staging, did, records


def test_phase_records_chain_with_independent_digests(tmp_path, monkeypatch):
    import hashlib
    record = _kernel("phase_record")
    staging, did, records = _phase_chain(tmp_path, monkeypatch)
    upstream = {}
    for phase in ("SETUP", "DEV", "CAL"):
        digest = _b1c_digest(did, phase, upstream)
        rows = sorted(({"key": key, "sha256": hashlib.sha256(payload).hexdigest(), "n_rows": n}
                       for key, (payload, n) in zip(B1C_KEYS[phase], B1C_PAYLOADS[phase])),
                      key=lambda row: pdb.canon(row["key"]))
        expected = {"design_id": did, "phase": phase, "upstream": upstream, "partitions": rows,
                    "derived": B1C_DERIVED[phase], "phase_digest": digest}
        assert records[phase] == expected
        assert (staging / "phases" / f"{phase}.json").read_text() == pdb.canon(expected) + "\n"
        upstream = {**upstream, phase: digest}
    assert not _nested_keys(records) & B1C_FORBIDDEN
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        for phase in ("SETUP", "DEV", "CAL"):
            assert record(staging, phase, None, None, None) == records[phase]
            again = record(staging, phase, records[phase]["upstream"], B1C_KEYS[phase], B1C_DERIVED[phase])
            assert again == records[phase]
    assert _tree(staging) == before


def test_phase_digest_invariant_to_ordering_and_staging_location(tmp_path, monkeypatch):
    _, did, first = _phase_chain(tmp_path / "a", monkeypatch)
    _, other, second = _phase_chain(tmp_path / "b" / "logs", monkeypatch, reverse=True)
    assert did == other and first == second
    assert [first[p]["phase_digest"] for p in ("SETUP", "DEV", "CAL")] == [_b1c_digest(did, "SETUP", {}),
                                                                          first["DEV"]["phase_digest"],
                                                                          second["CAL"]["phase_digest"]]
    assert not _nested_keys(second) & B1C_FORBIDDEN


def test_phase_order_lineage_and_design_refusals(tmp_path, monkeypatch):
    import json
    record, order_error = _kernel("phase_record"), _kernel("PhaseOrderError")
    mismatch, staging_mismatch = _kernel("PartitionMismatch"), _kernel("StagingMismatch")
    assert mismatch is pdb.PartitionMismatch
    staging, did = _b1c_staging(tmp_path)

    def refused(exc, phase, upstream, keys, derived):
        before = _tree(staging)
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            with pytest.raises(exc):
                record(staging, phase, upstream, keys, derived)
        assert _tree(staging) == before

    refused(order_error, "DEV", {"SETUP": "0" * 64}, B1C_KEYS["DEV"], B1C_DERIVED["DEV"])
    (setup_payload, setup_rows), (dev_payload, dev_rows) = B1C_PAYLOADS["SETUP"][0], B1C_PAYLOADS["DEV"][0]
    _put_partition(staging, did, {}, B1C_KEYS["SETUP"][0], setup_payload, setup_rows)
    lineage = {"SETUP": record(staging, "SETUP", {}, B1C_KEYS["SETUP"], B1C_DERIVED["SETUP"])["phase_digest"]}
    refused(order_error, "CAL", {**lineage, "DEV": "0" * 64}, B1C_KEYS["CAL"], B1C_DERIVED["CAL"])
    refused(mismatch, "DEV", {"SETUP": "f" * 64}, B1C_KEYS["DEV"], B1C_DERIVED["DEV"])
    refused(mismatch, "DEV", lineage, B1C_KEYS["DEV"], B1C_DERIVED["DEV"])
    _put_partition(staging, did, lineage, B1C_KEYS["DEV"][0], dev_payload, dev_rows)
    sidecar = _partition_stem(staging, did, lineage, B1C_KEYS["DEV"][0]).with_suffix(".json")
    good = sidecar.read_text()
    sidecar.write_text(pdb.canon({**json.loads(good), "design_id": "e" * 64}) + "\n")
    refused(mismatch, "DEV", lineage, B1C_KEYS["DEV"], B1C_DERIVED["DEV"])
    sidecar.write_text(good)
    refused(ValueError, "DEV", lineage, B1C_KEYS["DEV"], {"setups": {B1C_SETUP: {"s2_dev": math.nan}}})
    design = staging / "design.json"
    stored = json.loads(design.read_text())
    design.write_text(pdb.canon({**stored, "descriptor": {**stored["descriptor"], "seed": 3233}}) + "\n")
    refused(staging_mismatch, "DEV", lineage, B1C_KEYS["DEV"], B1C_DERIVED["DEV"])


@pytest.mark.parametrize("case", ["record_digest", "upstream_lineage", "payload_byte", "missing_npz", "sidecar_rows",
                                  "replace_derived"])
def test_completed_phase_loaded_without_rewrite_and_corruption_refused(tmp_path, monkeypatch, case):
    import json
    record, mismatch = _kernel("phase_record"), _kernel("PartitionMismatch")
    staging, did, records = _phase_chain(tmp_path, monkeypatch)
    phases, derived = staging / "phases", B1C_DERIVED["CAL"]
    stems = {p: _partition_stem(staging, did, records[p]["upstream"], B1C_KEYS[p][0]) for p in records}
    if case == "record_digest":
        dev = json.loads((phases / "DEV.json").read_text())
        (phases / "DEV.json").write_text(pdb.canon({**dev, "phase_digest": "0" * 64}) + "\n")
    elif case == "upstream_lineage":
        setup = json.loads((phases / "SETUP.json").read_text())
        setup["derived"]["setups"][B1C_SETUP]["basis_sha"] = "b" * 64
        (phases / "SETUP.json").write_text(pdb.canon(setup) + "\n")
    elif case == "payload_byte":
        data = bytearray(stems["SETUP"].with_suffix(".npz").read_bytes())
        data[len(data) // 2] ^= 1
        stems["SETUP"].with_suffix(".npz").write_bytes(bytes(data))
    elif case == "missing_npz":
        stems["DEV"].with_suffix(".npz").unlink()
    elif case == "sidecar_rows":
        sidecar = json.loads(stems["CAL"].with_suffix(".json").read_text())
        stems["CAL"].with_suffix(".json").write_text(pdb.canon({**sidecar, "n_rows": 18}) + "\n")
    else:
        derived = {**derived, "rule": "another_rule"}
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(mismatch):
            if case == "replace_derived":
                record(staging, "CAL", records["CAL"]["upstream"], B1C_KEYS["CAL"], derived)
            else:
                record(staging, "CAL", None, None, None)
    assert _tree(staging) == before


B1D_KEY = ["SETUP", "EXACT", 32, 0, "frame"]
B1D_SIDECAR_EDITS = {"foreign_design": {"design_id": "e" * 64},
                     "foreign_key": {"key": ["SETUP", "EXACT", 32, 0, "other"]},
                     "foreign_upstream": {"upstream": {"SETUP": "0" * 64}},
                     "bad_sha": {"payload_sha256": "0" * 64}, "bad_rows": {"n_rows": 20}}


def _b1d_arrays():
    return {"lam": B1C_SPECTRUM.copy(), "pc": np.arange(1, 22, dtype=np.int64)}


def _counted(make):
    calls = []

    def produce():
        calls.append(len(calls))
        return make()

    return produce, calls


def _same_arrays(got, expected):
    return set(got) == set(expected) and all(got[k].dtype == v.dtype and np.array_equal(got[k], v)
                                             for k, v in expected.items())


def test_partition_computes_once_then_reloads_verified_bytes(tmp_path, monkeypatch):
    import hashlib
    part, record = _kernel("partition"), _kernel("phase_record")
    staging, did = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        first = part(staging, "SETUP", {}, B1D_KEY, produce)
        snapshot = _tree(staging)
        again = part(staging, "SETUP", {}, B1D_KEY, produce)
    assert len(calls) == 1 and _tree(staging) == snapshot
    assert _same_arrays(first, _b1d_arrays()) and _same_arrays(again, _b1d_arrays())
    stem = _partition_stem(staging, did, {}, B1D_KEY)
    payload = stem.with_suffix(".npz").read_bytes()
    sidecar = {"design_id": did, "key": B1D_KEY, "upstream": {}, "fingerprint": stem.name,
               "payload_sha256": hashlib.sha256(payload).hexdigest(), "n_rows": 21}
    assert stem.with_suffix(".json").read_text() == pdb.canon(sidecar) + "\n"
    assert set(_tree(staging / "partitions")) == {f"{stem.name}.npz", f"{stem.name}.json"}
    rows = record(staging, "SETUP", {}, [B1D_KEY], B1C_DERIVED["SETUP"])["partitions"]
    assert rows == [{"key": B1D_KEY, "sha256": sidecar["payload_sha256"], "n_rows": 21}]


def test_partition_bytes_independent_of_array_order_and_location(tmp_path):
    part, trees = _kernel("partition"), []
    makers = (_b1d_arrays, lambda: dict(reversed(_b1d_arrays().items())))
    for root, make in zip((tmp_path / "a", tmp_path / "b" / "logs"), makers):
        staging, _ = _b1c_staging(root)
        part(staging, "SETUP", {}, B1D_KEY, _counted(make)[0])
        trees.append(_tree(staging / "partitions"))
    assert trees[0] == trees[1] and len(trees[0]) == 2


@pytest.mark.parametrize("case", ["orphan_npz", "missing_npz", "corrupt_payload", *B1D_SIDECAR_EDITS])
def test_partition_orphan_recovery_and_integrity_refusals(tmp_path, monkeypatch, case):
    import json
    part, mismatch = _kernel("partition"), _kernel("PartitionMismatch")
    staging, did = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    part(staging, "SETUP", {}, B1D_KEY, produce)
    good, stem = _tree(staging), _partition_stem(staging, did, {}, B1D_KEY)
    npz, side = stem.with_suffix(".npz"), stem.with_suffix(".json")
    if case == "orphan_npz":
        side.unlink()
        npz.write_bytes(b"untrusted orphan bytes")
    elif case == "missing_npz":
        npz.unlink()
    elif case == "corrupt_payload":
        data = bytearray(npz.read_bytes())
        data[len(data) // 2] ^= 1
        npz.write_bytes(bytes(data))
    else:
        side.write_text(pdb.canon({**json.loads(side.read_text()), **B1D_SIDECAR_EDITS[case]}) + "\n")
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        if case == "orphan_npz":
            got = part(staging, "SETUP", {}, B1D_KEY, produce)
        else:
            with pytest.raises(mismatch):
                part(staging, "SETUP", {}, B1D_KEY, produce)
    if case == "orphan_npz":
        assert len(calls) == 2 and _tree(staging) == good and _same_arrays(got, _b1d_arrays())
    else:
        assert len(calls) == 1 and _tree(staging) == before


def test_partition_of_committed_phase_is_never_regenerated(tmp_path, monkeypatch):
    part, record, mismatch = _kernel("partition"), _kernel("phase_record"), _kernel("PartitionMismatch")
    staging, did = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    part(staging, "SETUP", {}, B1D_KEY, produce)
    record(staging, "SETUP", {}, [B1D_KEY], B1C_DERIVED["SETUP"])
    assert _same_arrays(part(staging, "SETUP", {}, B1D_KEY, produce), _b1d_arrays()) and len(calls) == 1
    _partition_stem(staging, did, {}, B1D_KEY).with_suffix(".json").unlink()
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        for key in (B1D_KEY, ["SETUP", "EXACT", 32, 0, "late_partition"]):
            with pytest.raises(mismatch):
                part(staging, "SETUP", {}, key, produce)
    assert len(calls) == 1 and _tree(staging) == before


def test_partition_commit_order_and_interrupted_json_recovery(tmp_path, monkeypatch):
    import os
    from pathlib import Path
    part = _kernel("partition")
    staging, did = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    stem, events, real_replace, real_fsync = _partition_stem(staging, did, {}, B1D_KEY), [], os.replace, os.fsync

    def replace(src, dst):
        events.append(("replace", Path(dst).name))
        if Path(dst).suffix == ".json" and len(calls) == 1:
            raise OSError("interrupted before the JSON commit")
        return real_replace(src, dst)

    def fsync(fd):
        events.append(("fsync",))
        return real_fsync(fd)

    with monkeypatch.context() as mp:
        mp.setattr(os, "replace", replace)
        mp.setattr(os, "fsync", fsync)
        with pytest.raises(OSError, match="interrupted"):
            part(staging, "SETUP", {}, B1D_KEY, produce)
        assert set(_tree(staging / "partitions")) == {f"{stem.name}.npz"}
        got = part(staging, "SETUP", {}, B1D_KEY, produce)
    commit = [("fsync",), ("replace", f"{stem.name}.npz"), ("fsync",), ("replace", f"{stem.name}.json")]
    assert events == commit * 2 and len(calls) == 2 and _same_arrays(got, _b1d_arrays())
    assert set(_tree(staging / "partitions")) == {f"{stem.name}.npz", f"{stem.name}.json"}


@pytest.mark.parametrize("payload", [{"obj": np.array([object(), object()], dtype=object)},
                                     {"a": np.zeros(3), "b": np.zeros(4)}, {"nan": np.array([0.0, math.nan])},
                                     {"scalar": np.float64(1.0)}, {}, {"../escape": np.zeros(2)}, [np.zeros(2)]],
                         ids=["object", "ragged", "nonfinite", "scalar", "empty", "escape_name", "not_mapping"])
def test_partition_refuses_invalid_producer_payload_before_commit(tmp_path, payload):
    part = _kernel("partition")
    staging, _ = _b1c_staging(tmp_path)
    with pytest.raises(ValueError):
        part(staging, "SETUP", {}, B1D_KEY, lambda: payload)
    assert set(_tree(staging)) == {"design.json"}


def test_partition_key_phase_and_upstream_are_strict(tmp_path):
    part = _kernel("partition")
    staging, _ = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    cases = (("SETUP", {}, ["SETUP", True]), ("SETUP", {}, []), ("SETUP", {"SETUP": "0" * 64}, B1D_KEY),
             ("DEV", {}, B1D_KEY), ("DEV", {"SETUP": "A" * 64}, B1D_KEY), ("HOLD", {}, B1D_KEY))
    for phase, upstream, key in cases:
        with pytest.raises(ValueError):
            part(staging, phase, upstream, key, produce)
    assert not calls and set(_tree(staging)) == {"design.json"}


def test_committed_phase_serves_only_listed_partitions(tmp_path, monkeypatch):
    part, record, mismatch = _kernel("partition"), _kernel("phase_record"), _kernel("PartitionMismatch")
    staging, _ = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    extra = ["SETUP", "EXACT", 32, 0, "extra"]
    for key in (B1D_KEY, extra):
        part(staging, "SETUP", {}, key, produce)
    record(staging, "SETUP", {}, [B1D_KEY], B1C_DERIVED["SETUP"])
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        assert _same_arrays(part(staging, "SETUP", {}, B1D_KEY, produce), _b1d_arrays())
        with pytest.raises(mismatch):
            part(staging, "SETUP", {}, extra, produce)
    assert len(calls) == 2 and _tree(staging) == before


def test_committed_phase_record_is_verified_before_serving(tmp_path, monkeypatch):
    import json
    part, record, mismatch = _kernel("partition"), _kernel("phase_record"), _kernel("PartitionMismatch")
    staging, _ = _b1c_staging(tmp_path)
    produce, calls = _counted(_b1d_arrays)
    part(staging, "SETUP", {}, B1D_KEY, produce)
    record(staging, "SETUP", {}, [B1D_KEY], B1C_DERIVED["SETUP"])
    path = staging / "phases" / "SETUP.json"
    path.write_text(pdb.canon({**json.loads(path.read_text()), "phase_digest": "0" * 64}) + "\n")
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(mismatch):
            part(staging, "SETUP", {}, B1D_KEY, produce)
    assert len(calls) == 1 and _tree(staging) == before


B1E_ORDER = ("SETUP", "DEV", "CAL", "NULL_PLAN", "HOLD", "ALT")
B1E_PRIMARY = ["FITTED_LW_GAUSSIAN", 239, 0]
B1E_PLAN_ID = "5a" * 32
B1E_SMOKE_PLAN = {"status": "PLAN_ADEQUATE", "n_hold": 2, "plan_id": B1E_PLAN_ID}
B1E_FULL_PLAN = {"status": "PLAN_CAPPED_EXPECT_INCONCLUSIVE", "n_hold": 5, "plan_id": B1E_PLAN_ID}
B1E_TAGS = ("EXACT|32|0", "FITTED_LW_GAUSSIAN|239|0")
B1E_DERIVED = {"SETUP": {"setups": {tag: {"universe_pcs": list(range(2, 22))} for tag in B1E_TAGS}},
               "DEV": {"setups": {tag: {"d_dev": 4, "s2_dev": 0.0034068772765664954} for tag in B1E_TAGS}},
               "CAL": {"rule": "predictive_exchangeable_rank_v2",
                       "thresholds": {f"{tag}|ONLINE_INFO_MIX_W128": {"n_cal": 19, "r": 0, "h": 2.2500000000000004}
                                      for tag in B1E_TAGS}},
               "HOLD": {"policies": ["ONLINE_INFO_MIX_W128"]}, "ALT": {"families": ["F2_STRUCTURED_RESIDUAL"]}}


def _b1e_parts(n_plan, n_hold):
    p, policy = B1E_PRIMARY, "ONLINE_INFO_MIX_W128"
    return {"SETUP": [(["SETUP", *p, "spectrum"], {"lam": B1C_SPECTRUM.copy()})],
            "DEV": [(["DEV_NULL", *p, "maxima"], {"w_max": np.array([0.5])})],
            "CAL": [(["CAL_NULL", *p, policy], {"w_max": np.arange(19) / 8.0})],
            "NULL_PLAN": [(["NULL_PLAN", *p, policy], {"alarm": np.zeros(n_plan, dtype=bool)})] if n_plan else [],
            "HOLD": [(["HOLD_NULL", *p, policy], {"alarm": np.zeros(n_hold, dtype=bool)}),
                     (["HOLD_NULL", "EXACT", 32, 0, policy], {"alarm": np.zeros(1, dtype=bool)})],
            "ALT": [(["ALT", *p, "F2_STRUCTURED_RESIDUAL"], {"first": np.array([3])})]}


def _b1e_staging(root, mode="smoke"):
    cfg = _edited(_design_cfg(), ("modes", mode, "sizes", "CAL_NULL"), 19)
    return _kernel("open_staging")(root, _kernel("design_descriptor")(cfg, mode), False)


def _b1e_chain(staging, monkeypatch, plan, parts, phases=B1E_ORDER):
    part, record, lineage = _kernel("partition"), _kernel("phase_record"), {}
    for phase in phases:
        for key, arrays in parts[phase]:
            part(staging, phase, dict(lineage), key, lambda arrays=arrays: arrays)
        derived = plan if phase == "NULL_PLAN" else B1E_DERIVED[phase]
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            lineage[phase] = record(staging, phase, dict(lineage), [k for k, _ in parts[phase]], derived)["phase_digest"]
    return lineage


def test_new_partition_requires_effective_predecessor_lineage(tmp_path, monkeypatch):
    import json
    part, record = _kernel("partition"), _kernel("phase_record")
    order_error, mismatch = _kernel("PhaseOrderError"), _kernel("PartitionMismatch")
    staging, _ = _b1c_staging(tmp_path)
    produce, calls = _counted(lambda: {"w_max": np.array([0.5])})
    key = ["DEV_NULL", "EXACT", 32, 0, "maxima"]

    def refused(exc, phase, upstream):
        before = _tree(staging)
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            with pytest.raises(exc):
                part(staging, phase, upstream, key, produce)
        assert not calls and _tree(staging) == before

    refused(order_error, "DEV", {"SETUP": "0" * 64})
    part(staging, "SETUP", {}, B1D_KEY, _counted(_b1d_arrays)[0])
    setup = record(staging, "SETUP", {}, [B1D_KEY], B1C_DERIVED["SETUP"])["phase_digest"]
    refused(mismatch, "DEV", {"SETUP": "f" * 64})
    refused(order_error, "CAL", {"SETUP": setup, "DEV": "0" * 64})
    path = staging / "phases" / "SETUP.json"
    path.write_text(pdb.canon({**json.loads(path.read_text()), "phase_digest": "0" * 64}) + "\n")
    for upstream in ({"SETUP": setup}, {"SETUP": "0" * 64}):
        refused(mismatch, "DEV", upstream)


@pytest.mark.parametrize("mode, n_plan, plan", [("smoke", 1, B1E_SMOKE_PLAN), ("full", 2, B1E_FULL_PLAN)],
                         ids=["smoke_adequate", "full_capped"])
def test_post_cal_chain_is_immutable_and_path_independent(tmp_path, monkeypatch, mode, n_plan, plan):
    record, part = _kernel("phase_record"), _kernel("partition")
    stagings = [_b1e_staging(root, mode) for root in (tmp_path / "a", tmp_path / "b" / "logs")]
    lineages = [_b1e_chain(staging, monkeypatch, plan, _b1e_parts(n_plan, plan["n_hold"])) for staging in stagings]
    first, second = stagings
    assert lineages[0] == lineages[1] and tuple(lineages[0]) == B1E_ORDER
    for sub in ("phases", "partitions"):
        assert _tree(first / sub) == _tree(second / sub)
    nulls, hold = record(first, "NULL_PLAN", None, None, None), record(first, "HOLD", None, None, None)
    assert nulls["derived"] == plan and nulls["upstream"] == {p: lineages[0][p] for p in B1E_ORDER[:3]}
    assert [row["n_rows"] for row in nulls["partitions"]] == [n_plan]
    assert [row["n_rows"] for row in hold["partitions"]] == [1, plan["n_hold"]]
    assert record(first, "ALT", None, None, None)["upstream"] == {p: lineages[0][p] for p in B1E_ORDER[:5]}
    before, (produce, calls) = _tree(first), _counted(lambda: {"alarm": np.zeros(plan["n_hold"], dtype=bool)})
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        assert [record(first, p, None, None, None)["phase_digest"] for p in B1E_ORDER] == list(lineages[0].values())
        upstream = {p: lineages[0][p] for p in B1E_ORDER[:4]}
        served = part(first, "HOLD", upstream, ["HOLD_NULL", *B1E_PRIMARY, "ONLINE_INFO_MIX_W128"], produce)
    assert not calls and served["alarm"].shape == (plan["n_hold"],) and _tree(first) == before


def test_full_hold_before_null_plan_record_is_refused(tmp_path, monkeypatch):
    part, order_error = _kernel("partition"), _kernel("PhaseOrderError")
    staging, parts = _b1e_staging(tmp_path, "full"), _b1e_parts(2, 5)
    lineage = _b1e_chain(staging, monkeypatch, None, parts, B1E_ORDER[:3])
    produce, calls = _counted(lambda: {"alarm": np.zeros(5, dtype=bool)})
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        with pytest.raises(order_error):
            part(staging, "HOLD", {**lineage, "NULL_PLAN": "0" * 64}, parts["HOLD"][0][0], produce)
    assert not calls and _tree(staging) == before


def test_null_plan_freezes_valid_n_hold_and_hold_consumes_it(tmp_path, monkeypatch):
    record, part = _kernel("phase_record"), _kernel("partition")
    order_error, mismatch = _kernel("PhaseOrderError"), _kernel("PartitionMismatch")
    staging, parts = _b1e_staging(tmp_path), _b1e_parts(1, 2)
    lineage = _b1e_chain(staging, monkeypatch, None, parts, B1E_ORDER[:3])
    [(null_key, null_arrays)] = parts["NULL_PLAN"]
    hold_key = parts["HOLD"][0][0]
    produce, calls = _counted(lambda: {"alarm": np.zeros(2, dtype=bool)})

    def refused(exc, call):
        before = _tree(staging)
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            with pytest.raises(exc):
                call()
        assert not calls and _tree(staging) == before

    pending = {**lineage, "NULL_PLAN": "0" * 64}
    refused(order_error, lambda: part(staging, "HOLD", pending, hold_key, produce))
    part(staging, "NULL_PLAN", dict(lineage), null_key, lambda: null_arrays)
    good = {"status": "PLAN_ADEQUATE", "n_hold": 2, "plan_id": B1E_PLAN_ID}
    bad = [{**good, "n_hold": 0}, {**good, "n_hold": 4}, {**good, "n_hold": 2.0}, {**good, "n_hold": True},
           {**good, "status": "PLAN_CAPPED_EXPECT_INCONCLUSIVE"}, {"status": "NOT_APPLICABLE"},
           {"status": "PLAN_ADEQUATE", "n_hold": 2}, {**good, "plan_id": "XYZ"}]
    for plan in bad:
        refused(ValueError, lambda: record(staging, "NULL_PLAN", dict(lineage), [null_key], plan))
    refused(ValueError, lambda: record(staging, "NULL_PLAN", dict(lineage), [], good))
    refused(order_error, lambda: part(staging, "HOLD", pending, hold_key, produce))
    prior = dict(lineage)
    lineage["NULL_PLAN"] = record(staging, "NULL_PLAN", prior, [null_key], good)["phase_digest"]
    refused(mismatch, lambda: record(staging, "NULL_PLAN", prior, [null_key], {**good, "n_hold": 3}))
    refused(mismatch, lambda: part(staging, "HOLD", {**lineage, "CAL": "0" * 64}, hold_key, produce))
    refused(ValueError, lambda: part(staging, "HOLD", dict(lineage), ["HOLD_NULL", "UNKNOWN", 1, 0, "x"], produce))
    refused(order_error, lambda: part(staging, "ALT", {**lineage, "HOLD": "0" * 64}, parts["ALT"][0][0], produce))
    wrong, wrong_calls = _counted(lambda: {"alarm": np.zeros(3, dtype=bool)})
    before = _tree(staging)
    with pytest.raises(ValueError):
        part(staging, "HOLD", dict(lineage), hold_key, wrong)
    assert len(wrong_calls) == 1 and _tree(staging) == before
    for key, arrays in parts["HOLD"]:
        part(staging, "HOLD", dict(lineage), key, lambda arrays=arrays: arrays)
    hold = record(staging, "HOLD", dict(lineage), [k for k, _ in parts["HOLD"]], B1E_DERIVED["HOLD"])
    assert [row["n_rows"] for row in hold["partitions"]] == [1, 2] and hold["upstream"] == lineage


def test_null_plan_not_applicable_for_pilot_and_scope_without_primary(tmp_path, monkeypatch):
    record, part = _kernel("phase_record"), _kernel("partition")
    skipped, adequate = {"status": "NOT_APPLICABLE"}, {"status": "PLAN_ADEQUATE", "n_hold": 1, "plan_id": B1E_PLAN_ID}
    pilot, parts = _b1e_staging(tmp_path / "pilot", "pilot"), _b1e_parts(0, 1)
    lineage = _b1e_chain(pilot, monkeypatch, skipped, parts)
    nulls, hold = record(pilot, "NULL_PLAN", None, None, None), record(pilot, "HOLD", None, None, None)
    assert nulls["derived"] == skipped and nulls["partitions"] == [] and tuple(lineage) == B1E_ORDER
    assert hold["upstream"]["NULL_PLAN"] == nulls["phase_digest"] and [r["n_rows"] for r in hold["partitions"]] == [1, 1]
    fresh = _b1e_staging(tmp_path / "pilot_fresh", "pilot")
    cal = _b1e_chain(fresh, monkeypatch, None, parts, B1E_ORDER[:3])
    produce, calls = _counted(lambda: {"alarm": np.zeros(1, dtype=bool)})
    before = _tree(fresh)
    for derived, keys in ((adequate, []), ({**skipped, "n_hold": 1}, []),
                          (skipped, [["NULL_PLAN", *B1E_PRIMARY, "ONLINE_INFO_MIX_W128"]])):
        with pytest.raises(ValueError):
            record(fresh, "NULL_PLAN", dict(cal), keys, derived)
    with pytest.raises(ValueError):
        part(fresh, "NULL_PLAN", dict(cal), ["NULL_PLAN", *B1E_PRIMARY, "ONLINE_INFO_MIX_W128"], produce)
    assert not calls and _tree(fresh) == before
    technical, _, records = _phase_chain(tmp_path / "exact_only", monkeypatch)
    upstream = {p: records[p]["phase_digest"] for p in records}
    with pytest.raises(ValueError):
        record(technical, "NULL_PLAN", upstream, [], adequate)
    assert record(technical, "NULL_PLAN", upstream, [], skipped)["derived"] == skipped


B1F_DEV_IDS = {"EXACT|32|0": "0123456789abcdef", "FITTED_LW_GAUSSIAN|239|0": "fedcba9876543210"}
B1F_DERIVED = {**B1E_DERIVED, "DEV": {**B1E_DERIVED["DEV"], "dev_ids": B1F_DEV_IDS}}
B1F_EXCLUDED = ("/tmp/x.csv", "../x.csv", "sub/x.csv", "manifest.json", "summary.md", "telemetry.json", "figure.png", "")


def _b1f_records(root, mode="full", derived=B1F_DERIVED):
    staging = _b1e_staging(root, mode)
    if mode == "full":
        plan, parts = B1E_FULL_PLAN, _b1e_parts(2, 5)
    else:
        plan, parts = {"status": "NOT_APPLICABLE"}, _b1e_parts(0, 1)
    part, record, lineage = _kernel("partition"), _kernel("phase_record"), {}
    for phase in B1E_ORDER:
        for key, arrays in parts[phase]:
            part(staging, phase, dict(lineage), key, lambda arrays=arrays: arrays)
        content = plan if phase == "NULL_PLAN" else derived[phase]
        lineage[phase] = record(staging, phase, dict(lineage), [k for k, _ in parts[phase]], content)["phase_digest"]
    return {phase: record(staging, phase, None, None, None) for phase in B1E_ORDER}


def _b1f_payloads(out_dir, did, rmst=3.0):
    import hashlib
    import pandas
    from jepadrift import pipelines
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = {"calibration.csv": pandas.DataFrame({"design_id": [did, did], "policy": ["ONLINE_INFO_MIX_W128", "FULL_K"],
                                                  "h": [2.2500000000000004, 2.2500000000000004]}),
              "aggregates.csv": pandas.DataFrame({"design_id": [did], "family": ["F2_STRUCTURED_RESIDUAL"],
                                                 "rmst": [rmst]})}
    for name, frame in frames.items():
        pipelines.save_fair_csv(frame, out_dir / name)
    return {name: hashlib.sha256((out_dir / name).read_bytes()).hexdigest() for name in frames}


def test_realization_descriptor_from_verified_records_and_fair_payloads(tmp_path, monkeypatch):
    import copy
    import hashlib
    realize = _kernel("realization")
    records = _b1f_records(tmp_path / "full")
    did = records["SETUP"]["design_id"]
    shas = _b1f_payloads(tmp_path / "out_full", did)
    thresholds_sha = hashlib.sha256(pdb.canon(B1E_DERIVED["CAL"]["thresholds"]).encode()).hexdigest()
    expected = {"design_id": did, "phase_digests": {p: records[p]["phase_digest"] for p in B1E_ORDER},
                "dev_ids": B1F_DEV_IDS, "thresholds_sha": thresholds_sha, "plan_id": B1E_PLAN_ID, "n_hold": 5,
                "payloads": shas}
    inputs, opened = copy.deepcopy((records, shas)), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        rid, desc = realize(records, shas)
    assert desc == expected and rid == hashlib.sha256(pdb.canon(expected).encode()).hexdigest()
    assert not opened and (records, shas) == inputs and "realization_id" not in _nested_keys(desc)
    texts = [(tmp_path / "out_full" / name).read_text() for name in shas]
    assert all(did in text and "realization_id" not in text for text in texts)
    pilot = _b1f_records(tmp_path / "pilot", "pilot")
    _, skipped = realize(pilot, _b1f_payloads(tmp_path / "out_pilot", pilot["SETUP"]["design_id"]))
    digests = {**{p: pilot[p]["phase_digest"] for p in B1E_ORDER}, "NULL_PLAN": "NOT_APPLICABLE"}
    assert skipped["phase_digests"] == digests and (skipped["plan_id"], skipped["n_hold"]) == (None, None)
    assert skipped["design_id"] == pilot["SETUP"]["design_id"] != did


def test_realization_id_ignores_locations_ordering_and_manifest_files(tmp_path):
    realize = _kernel("realization")
    first, second = _b1f_records(tmp_path / "a"), _b1f_records(tmp_path / "b" / "logs")
    did = first["SETUP"]["design_id"]
    folders = (tmp_path / "out_a", tmp_path / "x" / "out_b")
    shas_a, shas_b = (_b1f_payloads(folder, did) for folder in folders)
    rid = realize(first, shas_a)[0]
    for folder in folders:
        for name, text in (("manifest.json", '{"authority": "GO", "jobs": 8}'), ("summary.md", "host and time"),
                           ("telemetry.json", '{"cpu_seconds": 1}')):
            (folder / name).write_text(text)
    reordered = {p: second[p] for p in reversed(B1E_ORDER)}
    assert realize(reordered, dict(reversed(list(shas_b.items()))))[0] == rid
    assert realize(first, shas_a)[0] == rid and shas_a == shas_b


def test_realization_changes_with_scientific_payload_or_phase_content(tmp_path):
    realize = _kernel("realization")
    records = _b1f_records(tmp_path / "full")
    did = records["SETUP"]["design_id"]
    base = realize(records, _b1f_payloads(tmp_path / "out", did))[0]
    assert realize(records, _b1f_payloads(tmp_path / "out_changed", did, rmst=3.5))[0] != base
    thresholds = {name: {**row, "h": 2.5} for name, row in B1E_DERIVED["CAL"]["thresholds"].items()}
    moved = _b1f_records(tmp_path / "variant", derived={**B1F_DERIVED, "CAL": {**B1F_DERIVED["CAL"], "thresholds": thresholds}})
    rid, desc = realize(moved, _b1f_payloads(tmp_path / "out_variant", did))
    assert rid != base and desc["phase_digests"]["CAL"] != records["CAL"]["phase_digest"]
    assert [desc["phase_digests"][p] for p in ("SETUP", "DEV")] == [records[p]["phase_digest"] for p in ("SETUP", "DEV")]


def test_realization_refuses_inconsistent_handoff_and_excluded_names(tmp_path):
    import copy
    realize = _kernel("realization")
    records, pilot = _b1f_records(tmp_path / "full"), _b1f_records(tmp_path / "pilot", "pilot")
    shas = _b1f_payloads(tmp_path / "out", records["SETUP"]["design_id"])
    bad = [{p: r for p, r in records.items() if p != "ALT"}, {**records, "HOLD": pilot["HOLD"]}]
    for phase, field, value in (("ALT", "phase_digest", "0" * 64), ("HOLD", "derived", {"policies": ["FULL_K"]}),
                                ("ALT", "upstream", {**records["ALT"]["upstream"], "HOLD": "0" * 64})):
        broken = copy.deepcopy(records)
        broken[phase][field] = value
        bad.append(broken)
    variants = ({**B1F_DERIVED, "DEV": B1E_DERIVED["DEV"]},
                {**B1F_DERIVED, "DEV": {**B1F_DERIVED["DEV"], "dev_ids": {"EXACT|32|0": "XYZ"}}},
                {**B1F_DERIVED, "CAL": {"rule": "predictive_exchangeable_rank_v2"}})
    bad += [_b1f_records(tmp_path / f"variant{i}", derived=variant) for i, variant in enumerate(variants)]
    for records_bad in bad:
        with pytest.raises(ValueError):
            realize(records_bad, shas)
    for name in B1F_EXCLUDED:
        with pytest.raises(ValueError):
            realize(records, {**shas, name: "0" * 64})
    for payloads in ({}, {**shas, "issues.csv": "A" * 64}, {**shas, "issues.csv": "0" * 63}, {**shas, "issues.csv": 7}):
        with pytest.raises(ValueError):
            realize(records, payloads)


B1G_META = ("manifest.json", "summary.md", "telemetry.json")


def _b1g_prepare(root):
    import hashlib
    records = _b1f_records(root / "logs")
    did = records["SETUP"]["design_id"]
    desc = _kernel("design_descriptor")(_edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19), "full")
    assert _kernel("design_id")(desc) == did
    temp, out = root / f".published.publish-{did[:16]}.tmp", root / "published"
    rid, real = _kernel("realization")(records, _b1f_payloads(temp, did))
    go = {"path": "prompts/GO-stream-32-full-fixture.md",
          "sha256": hashlib.sha256(f"Synthetic full GO fixture citing {did}\n".encode()).hexdigest()}
    manifest = {"status": "COMPLETE", "design_id": did, "design_descriptor": desc, "realization_id": rid,
                "realization_descriptor": real, "authority": {"stage": "full", "design_id": did, "go_reference": go},
                "payloads": {n: {"status": "PUBLISHED", "sha256": s} for n, s in real["payloads"].items()}}
    (temp / "manifest.json").write_text(pdb.canon(manifest) + "\n")
    (temp / "summary.md").write_text(f"# Synthetic publication fixture\n\ndesign_id: {did}\n")
    (temp / "telemetry.json").write_text(pdb.canon({"wall_seconds": 0.25}) + "\n")
    return records, temp, out, manifest


def test_publish_moves_complete_prepared_sibling_with_verified_manifest(tmp_path, monkeypatch):
    import copy
    import hashlib
    import json
    publish, realize = _kernel("publish"), _kernel("realization")
    records, temp, out, manifest = _b1g_prepare(tmp_path)
    did, prepared = manifest["design_id"], _tree(temp)
    assert set(prepared) == {*B1G_META, *manifest["realization_descriptor"]["payloads"]}
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        assert publish(temp, out) == manifest
    assert not temp.exists() and _tree(out) == prepared
    published = json.loads((out / "manifest.json").read_text())
    assert published == manifest and published["status"] == "COMPLETE"
    assert _kernel("design_id")(published["design_descriptor"]) == did == records["SETUP"]["design_id"]
    shas = {n: hashlib.sha256(data).hexdigest() for n, data in _tree(out).items() if n not in B1G_META}
    real = published["realization_descriptor"]
    assert published["payloads"] == {n: {"status": "PUBLISHED", "sha256": s} for n, s in shas.items()}
    assert real["payloads"] == shas and real["design_id"] == did
    reference = hashlib.sha256(pdb.canon({**real, "payloads": shas}).encode()).hexdigest()
    flipped = copy.deepcopy(records)
    flipped["HOLD"]["partitions"].reverse()
    assert len(flipped["HOLD"]["partitions"]) == 2 and flipped["HOLD"]["partitions"] != records["HOLD"]["partitions"]
    inputs = copy.deepcopy((flipped, shas))
    assert realize(flipped, shas) == (reference, real) and (flipped, shas) == inputs
    assert reference == published["realization_id"] == realize(records, shas)[0]
    text = (out / "manifest.json").read_text()
    assert '"/' not in text and str(tmp_path) not in text
    for name in shas:
        csv = (out / name).read_text()
        assert did in csv and reference not in csv and "realization_id" not in csv


@pytest.mark.parametrize("state", ["absent", "empty"])
def test_publish_interrupted_before_replace_retries_and_refuses_nonempty_output(tmp_path, monkeypatch, state):
    import os
    from pathlib import Path
    publish, exists = _kernel("publish"), _kernel("OutputExists")
    _, temp, out, manifest = _b1g_prepare(tmp_path)
    if state == "empty":
        out.mkdir()
    prepared, seen, real_replace = _tree(temp), [], os.replace

    def replace(src, dst):
        if (Path(src), Path(dst)) == (temp, out):
            seen.append(sorted(out.iterdir()) if out.exists() else None)
            raise OSError("interrupted before the directory replace")
        return real_replace(src, dst)

    expected = [] if state == "empty" else None
    with monkeypatch.context() as mp:
        mp.setattr(os, "replace", replace)
        with pytest.raises(OSError, match="interrupted"):
            publish(temp, out)
    assert seen == [expected] and _tree(temp) == prepared
    assert (sorted(out.iterdir()) if out.exists() else None) == expected
    assert publish(temp, out) == manifest and not temp.exists() and _tree(out) == prepared
    temp.mkdir()
    for name, data in prepared.items():
        (temp / name).write_bytes(data)
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(exists):
            publish(temp, out)
    assert _tree(tmp_path) == before and _tree(temp) == prepared == _tree(out)


def _b1g_rid(descriptor):
    import hashlib
    return hashlib.sha256(pdb.canon(descriptor).encode()).hexdigest()


def _b1g_refused(monkeypatch, publish, temp, out):
    before = _tree(out.parent)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            publish(temp, out)
    assert _tree(out.parent) == before and temp.is_dir() and not out.exists()


B1G_HANDOFF = ("missing_manifest", "malformed_manifest", "noncanonical_manifest", "nan_manifest", "incomplete_status",
               "extra_field", "missing_field", "stale_design_id", "stale_design_descriptor", "stale_realization_id",
               "foreign_realization", "authority_design", "go_absolute", "go_traversing", "payload_sha",
               "payload_status", "payload_field", "missing_csv", "altered_csv", "unlisted_file", "missing_summary",
               "temp_tagged_by_realization", "temp_not_sibling")
B1G_NAMES = {"absolute": ("PUBLISHED", "/x.csv"), "traversing": ("PUBLISHED", "../x.csv"),
             "subdirectory": ("PUBLISHED", "sub/x.csv"), "hidden": ("PUBLISHED", ".x.csv"),
             "non_csv": ("PUBLISHED", "figure.png"), "nul": ("PUBLISHED", "x\x00.csv"),
             "local_absolute": ("LOCAL_HASHED_ONLY", "/partitions/" + "0" * 64 + ".npz"),
             "local_traversing": ("LOCAL_HASHED_ONLY", "../partitions/" + "0" * 64 + ".npz")}


@pytest.mark.parametrize("case", B1G_HANDOFF)
def test_publish_refuses_inconsistent_prepared_handoff_before_replace(tmp_path, monkeypatch, case):
    import json
    publish = _kernel("publish")
    _, temp, out, m = _b1g_prepare(tmp_path)
    did, real, auth, files = m["design_id"], m["realization_descriptor"], m["authority"], m["payloads"]
    entry, go = files["aggregates.csv"], auth["go_reference"]
    other = did[:16] + ("1" if did[16] == "0" else "0") + did[17:]
    nan, foreign, stale = {**real, "n_hold": math.nan}, {**real, "design_id": "f" * 64}, {**real, "design_id": other}
    edits = {"nan_manifest": {"realization_descriptor": nan, "realization_id": _b1g_rid(nan)},
             "incomplete_status": {"status": "INCOMPLETE"}, "extra_field": {"jobs": 1},
             "stale_design_id": {"design_id": other, "realization_descriptor": stale, "realization_id": _b1g_rid(stale),
                                 "authority": {**auth, "design_id": other}},
             "stale_design_descriptor": {"design_descriptor": _edited(m["design_descriptor"], ("seed",), 3233)},
             "stale_realization_id": {"realization_id": _b1g_rid({**real, "n_hold": 4})},
             "foreign_realization": {"realization_descriptor": foreign, "realization_id": _b1g_rid(foreign)},
             "authority_design": {"authority": {**auth, "design_id": "f" * 64}},
             "go_absolute": {"authority": {**auth, "go_reference": {**go, "path": "/prompts/GO.md"}}},
             "go_traversing": {"authority": {**auth, "go_reference": {**go, "path": "../GO.md"}}},
             "payload_sha": {"payloads": {**files, "aggregates.csv": {**entry, "sha256": "0" * 64}}},
             "payload_status": {"payloads": {**files, "aggregates.csv": {**entry, "status": "LOCAL_HASHED_ONLY"}}},
             "payload_field": {"payloads": {**files, "aggregates.csv": {**entry, "n_rows": 1}}}}
    removed = {"missing_manifest": "manifest.json", "missing_csv": "aggregates.csv", "missing_summary": "summary.md"}
    if case in edits:
        (temp / "manifest.json").write_text(pdb.canon({**m, **edits[case]}) + "\n")
    elif case == "missing_field":
        (temp / "manifest.json").write_text(pdb.canon({k: v for k, v in m.items() if k != "authority"}) + "\n")
    elif case in removed:
        (temp / removed[case]).unlink()
    elif case in ("malformed_manifest", "noncanonical_manifest"):
        (temp / "manifest.json").write_text("{" if case == "malformed_manifest" else json.dumps(m, indent=1) + "\n")
    elif case == "altered_csv":
        data = bytearray((temp / "aggregates.csv").read_bytes())
        data[len(data) // 2] ^= 1
        (temp / "aggregates.csv").write_bytes(bytes(data))
    elif case == "unlisted_file":
        (temp / "notes.txt").write_text("unlisted\n")
    else:
        target = (out.parent / "elsewhere" / temp.name if case == "temp_not_sibling"
                  else out.parent / f".published.publish-{m['realization_id'][:16]}.tmp")
        target.parent.mkdir(exist_ok=True)
        temp = temp.rename(target)
    _b1g_refused(monkeypatch, publish, temp, out)


@pytest.mark.parametrize("case", B1G_NAMES)
def test_publish_and_realization_refuse_unsafe_payload_names(tmp_path, monkeypatch, case):
    (status, name), (records, temp, out, m) = B1G_NAMES[case], _b1g_prepare(tmp_path)
    real, sha = m["realization_descriptor"], m["payloads"]["calibration.csv"]["sha256"]
    if status == "PUBLISHED":
        real = {**real, "payloads": {**real["payloads"], name: sha}}
        with pytest.raises(ValueError):
            _kernel("realization")(records, real["payloads"])
    bad = {**m, "realization_descriptor": real, "realization_id": _b1g_rid(real),
           "payloads": {**m["payloads"], name: {"status": status, "sha256": sha}}}
    (temp / "manifest.json").write_text(pdb.canon(bad) + "\n")
    _b1g_refused(monkeypatch, _kernel("publish"), temp, out)


def test_publish_keeps_local_only_metadata_and_identities_across_roots(tmp_path, monkeypatch):
    import hashlib
    from pathlib import Path
    publish, realize, runs = _kernel("publish"), _kernel("realization"), []
    for root, wall in ((tmp_path / "a", 0.25), (tmp_path / "x" / "b", 0.5)):
        records, temp, out, m = _b1g_prepare(root)
        did, hold = m["design_id"], records["HOLD"]
        row = hold["partitions"][-1]
        local = _partition_stem(Path(), did, hold["upstream"], row["key"]).with_suffix(".npz").as_posix()
        staged = root / "logs" / "staging" / did[:16] / local
        staged_bytes = staged.read_bytes()
        assert hashlib.sha256(staged_bytes).hexdigest() == row["sha256"] and local.startswith("partitions/")
        m = {**m, "payloads": {**m["payloads"], local: {"status": "LOCAL_HASHED_ONLY", "sha256": row["sha256"]}}}
        (temp / "manifest.json").write_text(pdb.canon(m) + "\n")
        (temp / "summary.md").write_text(f"# Synthetic publication fixture {root.name}\n")
        (temp / "telemetry.json").write_text(pdb.canon({"wall_seconds": wall}) + "\n")
        prepared = _tree(temp)
        with monkeypatch.context() as mp:
            _no_draws_or_workers(mp)
            assert publish(temp, out) == m
        assert _tree(out) == prepared and not (out / "partitions").exists() and staged.read_bytes() == staged_bytes
        published = {n: e["sha256"] for n, e in m["payloads"].items() if e["status"] == "PUBLISHED"}
        assert local not in published and realize(records, published)[0] == m["realization_id"]
        runs.append((m, {n: hashlib.sha256(data).hexdigest() for n, data in prepared.items()}))
    (first, shas_a), (second, shas_b) = runs
    assert first == second and [shas_a.pop(n) != shas_b.pop(n) for n in ("summary.md", "telemetry.json")] == [True] * 2
    assert shas_a == shas_b and set(shas_a) == {"manifest.json", *first["realization_descriptor"]["payloads"]}


def test_publish_fsync_order_and_failure_after_directory_replace(tmp_path, monkeypatch):
    import os
    from pathlib import Path
    publish, exists = _kernel("publish"), _kernel("OutputExists")
    _, temp, out, m = _b1g_prepare(tmp_path / "durable")
    labels = {(p.stat().st_dev, p.stat().st_ino): p.name for p in temp.iterdir()}
    labels.update({(d.stat().st_dev, d.stat().st_ino): tag for tag, d in (("<temp>", temp), ("<parent>", temp.parent))})
    events, real_fsync, real_replace = [], os.fsync, os.replace

    def fsync(fd):
        st = os.fstat(fd)
        events.append(labels.get((st.st_dev, st.st_ino), "<other>"))
        return real_fsync(fd)

    def replace(src, dst):
        events.append(("replace", Path(src), Path(dst)))
        return real_replace(src, dst)

    with monkeypatch.context() as mp:
        mp.setattr(os, "fsync", fsync)
        mp.setattr(os, "replace", replace)
        assert publish(temp, out) == m
    moves = [i for i, event in enumerate(events) if isinstance(event, tuple)]
    assert len(moves) == 1 and events[moves[0]] == ("replace", temp, out)
    assert set(events[:moves[0]]) >= {*B1G_META, *m["realization_descriptor"]["payloads"], "<temp>"}
    assert "<parent>" in events[moves[0] + 1:]
    _, late, target, _ = _b1g_prepare(tmp_path / "interrupted")
    prepared = _tree(late)

    def interrupted(src, dst):
        real_replace(src, dst)
        if (Path(src), Path(dst)) == (late, target):
            raise OSError("interrupted after the directory replace")

    with monkeypatch.context() as mp:
        mp.setattr(os, "replace", interrupted)
        with pytest.raises(OSError, match="interrupted after"):
            publish(late, target)
    assert not late.exists() and _tree(target) == prepared
    before = _tree(tmp_path)
    with pytest.raises(exists):
        publish(late, target)
    assert _tree(tmp_path) == before


def _b1g_referent_reads(mp, referent):
    import builtins
    import io
    import os
    from pathlib import Path
    attempts = []

    def guard(real):
        def opener(file, *args, **kwargs):
            target = Path(file).resolve() if isinstance(file, (str, os.PathLike)) else None
            if target is not None and (target == referent or referent in target.parents):
                attempts.append(target)
                raise AssertionError(f"content read of the symlink referent {target} before its refusal")
            return real(file, *args, **kwargs)
        return opener

    for owner in (builtins, io, os):
        mp.setattr(owner, "open", guard(owner.open))
    return attempts


def _b1g_sized(mp, path, size):
    import os
    real = os.stat(path)

    def view(observe):
        def observed(*args, **kwargs):
            st = observe(*args, **kwargs)
            if (st.st_dev, st.st_ino) != (real.st_dev, real.st_ino):
                return st
            cls, (fields, hidden) = st.__reduce__()
            return cls((*fields[:6], size, *fields[7:]), hidden)
        return observed

    for name in ("stat", "lstat", "fstat"):
        mp.setattr(os, name, view(getattr(os, name)))


@pytest.mark.parametrize("ending", [b"\r\n", b"\r"], ids=["crlf", "cr"])
def test_publish_refuses_manifest_bytes_with_a_translated_line_ending(tmp_path, monkeypatch, ending):
    publish = _kernel("publish")
    _, temp, out, m = _b1g_prepare(tmp_path)
    data = (temp / "manifest.json").read_bytes()
    assert data == (pdb.canon(m) + "\n").encode() and b"\r" not in data
    (temp / "manifest.json").write_bytes(data[:-1] + ending)
    _b1g_refused(monkeypatch, publish, temp, out)


@pytest.mark.parametrize("case", ["temp_dir", "manifest", "csv", "empty_output", "dangling_output"])
def test_publish_refuses_symlinks_before_reading_their_referents(tmp_path, monkeypatch, case):
    publish, exists = _kernel("publish"), _kernel("OutputExists")
    _, temp, out, _ = _b1g_prepare(tmp_path)
    referent = tmp_path / "referent"
    link = {"temp_dir": temp, "manifest": temp / "manifest.json", "csv": temp / "aggregates.csv"}.get(case, out)
    if case == "empty_output":
        referent.mkdir()
    elif case != "dangling_output":
        link.rename(referent)
    link.symlink_to(referent)
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        attempts = _b1g_referent_reads(mp, referent)
        with pytest.raises(exists if case.endswith("output") else ValueError):
            publish(temp, out)
    assert attempts == [] and _tree(tmp_path) == before and link.readlink() == referent
    assert case.endswith("output") or not (out.exists() or out.is_symlink())


@pytest.mark.parametrize("change", [{"stage": "pilot"}, {"go_reference": None}], ids=["stage_not_mode", "full_without_go"])
def test_publish_refuses_authority_stage_or_go_absence_against_full_design(tmp_path, monkeypatch, change):
    publish = _kernel("publish")
    _, temp, out, m = _b1g_prepare(tmp_path)
    assert m["design_descriptor"]["mode"] == m["authority"]["stage"] == "full" and m["authority"]["go_reference"]
    (temp / "manifest.json").write_text(pdb.canon({**m, "authority": {**m["authority"], **change}}) + "\n")
    _b1g_refused(monkeypatch, publish, temp, out)


@pytest.mark.parametrize("excess", [0, 1], ids=["at_limit", "over_limit"])
@pytest.mark.parametrize("name", ["aggregates.csv", "manifest.json"])
def test_publish_enforces_the_50_mib_limit_from_stat_metadata(tmp_path, monkeypatch, name, excess):
    import os
    publish, size = _kernel("publish"), 50 * 1024 * 1024 + excess
    _, temp, out, m = _b1g_prepare(tmp_path)
    prepared, real = _tree(temp), os.stat(temp / name)
    assert real.st_size == len(prepared[name]) < 1 << 16
    _b1g_sized(monkeypatch, temp / name, size)
    with open(temp / name, "rb") as handle:
        views = (os.stat(temp / name), os.lstat(temp / name), os.fstat(handle.fileno()))
    kept = (real.st_mode, real.st_ino, real.st_dev, real.st_nlink, real.st_mtime_ns)
    assert all(v.st_size == size and (v.st_mode, v.st_ino, v.st_dev, v.st_nlink, v.st_mtime_ns) == kept for v in views)
    if excess:
        _b1g_refused(monkeypatch, publish, temp, out)
    else:
        assert publish(temp, out) == m and _tree(out) == prepared and not temp.exists()


B1H_COLUMNS = ["design_id", "setup", "policy", "family", "info_basis", "metric_basis", "gamma_M", "horizon", "d_mean",
               "I_mean", "M_mean", "V_bar"]
B1H_INVALID = {"design_id": ("design_id", "AB" * 32), "info_basis": ("info_basis", "JOINT_KL_OPTIMAL"),
               "gamma_one": ("gamma_M", 1.0), "gamma_nan": ("gamma_M", math.nan), "gamma_bool": ("gamma_M", True),
               "label": ("setup", ""), "q_negative": ("q", np.array([0.5, -0.125, 0.125, 0.25, 0.0625])),
               "q_nan": ("q", np.array([0.5, math.nan, 0.125, 0.25, 0.0625])), "q_length": ("q", np.zeros(4)),
               "mask_dtype": ("masks", np.ones(5, dtype=np.int64)), "mask_empty_row": ("masks", np.zeros((2, 5), dtype=bool)),
               "mask_shape": ("masks", np.ones((1, 1, 5), dtype=bool)), "extra_key": ("h", 2.25), "no_entries": (None, None)}


def _b1h_frozen(values, dtype):
    out = np.array(values, dtype=dtype)
    out.setflags(write=False)
    return out


def _b1h_entries():
    q, fitted_q = _b1h_frozen([0.5, 0.0, 0.125, 0.25, 0.0625], float), _b1h_frozen([0.0, 0.375, 0.0, 0.0, 0.125], float)
    path = _b1h_frozen([[1, 0, 0, 0, 0], [1, 0, 0, 1, 0], [0, 1, 1, 1, 1], [1, 1, 1, 1, 0]], bool)
    base = {"setup": "EXACT|32|0", "family": "F2_STRUCTURED_RESIDUAL", "info_basis": "EXACT_ADDITIVE_KL", "q": q}
    return [{**base, "policy": "FIXED_EXANTE_QBAR_MIX", "gamma_M": 504.0, "masks": _b1h_frozen([1, 0, 1, 1, 0], bool)},
            {**base, "policy": "ONLINE_INFO_MIX_W128", "gamma_M": 504.0, "masks": path},
            {**base, "policy": "ONLINE_INFO_MIX_W128", "gamma_M": 5000.0, "masks": path},
            {**base, "setup": "FITTED_LW_GAUSSIAN|239|0", "policy": "ORACLE_INFO_MIX", "gamma_M": 504.0,
             "info_basis": "ORACLE_DIAGONAL_SURROGATE", "masks": _b1h_frozen([0, 1, 0, 0, 1], bool), "q": fitted_q}]


def _b1h_reference(entry):
    picked = [[k for k, keep in enumerate(row) if keep] for row in np.atleast_2d(entry["masks"]).tolist()]
    info = [math.fsum(float(entry["q"][k]) for k in s) for s in picked]
    costs = [pdb.mixture_cost(len(s), entry["gamma_M"]) for s in picked]
    ratios, n = [i / c for i, c in zip(info, costs)], len(picked)
    return {"horizon": n, "d_mean": math.fsum(len(s) for s in picked) / n, "I_mean": math.fsum(info) / n,
            "M_mean": math.fsum(costs) / n, "V_bar": math.fsum(ratios) / n}, ratios


def _b1h_plain(entries):
    return [{k: (v.dtype.str, v.tolist()) if isinstance(v, np.ndarray) else v for k, v in e.items()} for e in entries]


def test_export_selections_writes_full_horizon_analytic_values(tmp_path, monkeypatch):
    import hashlib
    import pandas
    from jepadrift import pipelines
    export, entries, out = _kernel("export_selections"), _b1h_entries(), tmp_path / "out"
    did, before = _kernel("design_id")(_kernel("design_descriptor")(_design_cfg(), "smoke")), _b1h_plain(entries)
    out.mkdir()
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        for owner, name in ((pio(), "best_sets"), (pio(), "online_masks"), (pio(), "masked_scan"), (pdb, "fit_basis"),
                            (pdb, "select_top_q"), (pdb, "scan_statistic"), (pdb, "q_plugin")):
            mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail("selection, scan or fit inside the exporter"))
        sha = export(out, did, entries)
    path = out / "selections.csv"
    data, frame = path.read_bytes(), pandas.read_csv(path, float_precision="round_trip")
    assert sha == hashlib.sha256(data).hexdigest() and set(_tree(out)) == {"selections.csv"}
    assert _b1h_plain(entries) == before and list(frame.columns) == B1H_COLUMNS and len(frame) == len(entries)
    assert b"realization" not in data
    pipelines.save_fair_csv(frame, tmp_path / "again.csv")
    assert (tmp_path / "again.csv").read_bytes() == data
    refs, rows = [_b1h_reference(entry) for entry in entries], frame.to_dict("records")
    for row, entry, (ref, _) in zip(rows, entries, refs):
        labels = [did, entry["setup"], entry["policy"], entry["family"], entry["info_basis"], "ANALYTIC_PROXY",
                  entry["gamma_M"], ref["horizon"]]
        assert [row[c] for c in B1H_COLUMNS[:8]] == labels
        assert all(row[c] == pytest.approx(ref[c], rel=1e-12, abs=0.0) for c in B1H_COLUMNS[8:])
    ratios = refs[1][1]
    assert all(math.fsum(ratios[:t]) / t != pytest.approx(rows[1]["V_bar"], rel=1e-9) for t in range(1, len(ratios)))
    assert rows[1]["V_bar"] != pytest.approx(rows[1]["I_mean"] / rows[1]["M_mean"], rel=1e-9)
    assert rows[2]["I_mean"] == rows[1]["I_mean"] and rows[2]["M_mean"] != pytest.approx(rows[1]["M_mean"], rel=1e-6)


def test_fluid_score_never_labelled_exact_delay(tmp_path):
    import pandas
    export, out = _kernel("export_selections"), tmp_path / "out"
    out.mkdir()
    export(out, "ab" * 32, _b1h_entries())
    frame = pandas.read_csv(out / "selections.csv", float_precision="round_trip")
    banned = {"delay", "add", "arl", "arl0", "rmst", "threshold", "calibrated", "h", "exact"}
    tokens = {t.lower() for text in (*frame.columns, *frame["metric_basis"]) for t in text.split("_")}
    assert not tokens & banned and set(frame["metric_basis"]) == {"ANALYTIC_PROXY"}
    assert {"M_mean", "V_bar", "gamma_M"} <= set(frame.columns) and sorted(set(frame["gamma_M"])) == [504, 5000]
    assert set(frame["info_basis"]) == {"EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_SURROGATE"}


@pytest.mark.parametrize("case", B1H_INVALID)
def test_export_selections_refuses_invalid_inputs_before_writing(tmp_path, monkeypatch, case):
    export, (key, value) = _kernel("export_selections"), B1H_INVALID[case]
    out, entries, did = tmp_path / "out", _b1h_entries(), "ab" * 32
    out.mkdir()
    if key == "design_id":
        did = value
    elif key is None:
        entries = []
    else:
        entries[1] = {**entries[1], key: value}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            export(out, did, entries)
    assert not any(out.iterdir())


def test_export_selections_refuses_finite_longdouble_metrics_beyond_float64(tmp_path, monkeypatch):
    export, out, entry = _kernel("export_selections"), tmp_path / "out", _b1h_entries()[0]
    big = np.longdouble(np.finfo(np.float64).max)
    q = _b1h_frozen(np.full(entry["q"].size, big), np.longdouble)
    assert q.dtype == np.longdouble and np.isfinite(q).all() and not q.flags.writeable
    assert np.isfinite(big * 4) and big * 4 > np.finfo(np.float64).max and int(entry["masks"].sum()) == 3
    out.mkdir()
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            export(out, "ab" * 32, [{**entry, "q": q}])
    assert not any(out.iterdir()) and not q.flags.writeable


def test_export_selections_accepts_moderate_longdouble_q_with_readonly_inputs(tmp_path):
    import hashlib
    import pandas
    export, out, entry = _kernel("export_selections"), tmp_path / "out", _b1h_entries()[0]
    entry = {**entry, "q": _b1h_frozen(entry["q"], np.longdouble)}
    q, masks = entry["q"], entry["masks"]
    before = (q.tobytes(), masks.tobytes())
    out.mkdir()
    sha = export(out, "ab" * 32, [entry])
    data = (out / "selections.csv").read_bytes()
    row = pandas.read_csv(out / "selections.csv", float_precision="round_trip").to_dict("records")[0]
    ref, _ = _b1h_reference(entry)
    assert sha == hashlib.sha256(data).hexdigest() and q.dtype == np.longdouble and row["metric_basis"] == "ANALYTIC_PROXY"
    assert all(math.isfinite(row[c]) and row[c] == pytest.approx(ref[c], rel=1e-12, abs=0.0) for c in B1H_COLUMNS[8:])
    assert not (q.flags.writeable or masks.flags.writeable) and (q.tobytes(), masks.tobytes()) == before


B1I_REFUSALS = ("idempotent", "other_design_output", "corrupt_publication", "corrupt_final", "corrupt_partition",
                "missing_phase", "foreign_authority", "changed_go_reference")
B1I_TEMPS = ("unowned_temp", "foreign_design_temp", "same_did_incomplete_manifest", "builder_interrupted",
             "interrupted_then_foreign_notes")


def _b1i_setup(root, monkeypatch, mode="full"):
    cfg = _edited(_design_cfg(), ("modes", mode, "sizes", "CAL_NULL"), 19)
    desc = _kernel("design_descriptor")(cfg, mode)
    cfg, did = _authorized(root, monkeypatch, cfg, mode)
    authority = _kernel("authorize")(mode, cfg, desc, 1)
    records = _b1f_records(root / "logs", mode)
    staging = root / "logs" / "staging" / did[:16]
    assert records["SETUP"]["design_id"] == did == authority["design_id"] and (staging / "design.json").is_file()
    return staging, root / "out", authority, records


def _b1i_builder(calls, fail=False):
    def build(temp, did, records):
        calls.append(did)
        assert set(records) == set(B1E_ORDER) and not (temp / "manifest.json").exists()
        _kernel("export_selections")(temp, did, _b1h_entries()[:2])
        if fail:
            raise RuntimeError("payload builder interrupted before the manifest")
        _b1f_payloads(temp, did)
        return {"wall_seconds": 0.25}
    return build


def _b1i_no_recompute(mp):
    _no_draws_or_workers(mp)
    for owner, name in ((pdb, "rank_threshold"), (pio(), "best_sets"), (pio(), "plan_holdout"), (pio(), "online_masks")):
        mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail("DEV, CAL or NULL_PLAN recomputed while finalizing"))


def _b1i_flip(path):
    data = bytearray(path.read_bytes())
    data[len(data) // 2] ^= 1
    path.write_bytes(bytes(data))


@pytest.mark.parametrize("mode", ["full", "pilot"])
def test_finalize_publishes_verified_phases_and_writes_final_marker(tmp_path, monkeypatch, mode):
    import hashlib
    import json
    finalize, realize = _kernel("finalize"), _kernel("realization")
    staging, out, authority, records = _b1i_setup(tmp_path, monkeypatch, mode)
    did, phases, calls = authority["design_id"], _tree(staging), []
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        final = finalize(staging, out, authority, _b1i_builder(calls))
    published = _tree(out)
    shas = {name: hashlib.sha256(data).hexdigest() for name, data in published.items() if name.endswith(".csv")}
    rid, real = realize(records, shas)
    manifest = json.loads(published["manifest.json"])
    assert set(manifest) == {"status", "design_id", "design_descriptor", "realization_id", "realization_descriptor",
                             "authority", "payloads"} and (manifest["status"], manifest["design_id"]) == ("COMPLETE", did)
    assert manifest["payloads"] == {**{name: {"status": "PUBLISHED", "sha256": sha} for name, sha in shas.items()},
                                    **_b1n_locals(staging, records)}
    expected = {"status": "PUBLISHED", "design_id": did, "realization_id": rid,
                "manifest_sha256": hashlib.sha256(published["manifest.json"]).hexdigest()}
    assert final == expected and (staging / "phases" / "FINAL.json").read_text() == pdb.canon(expected) + "\n"
    assert calls == [did] and set(published) == {"selections.csv", "calibration.csv", "aggregates.csv", *B1G_META}
    assert (manifest["realization_id"], manifest["realization_descriptor"], manifest["authority"]) == (rid, real, authority)
    assert manifest["design_descriptor"] == json.loads((staging / "design.json").read_text())["descriptor"]
    assert {name: data for name, data in _tree(staging).items() if name != "phases/FINAL.json"} == phases
    assert "FINAL" not in real["phase_digests"] and not list(tmp_path.glob(".out.publish-*"))
    assert (real["phase_digests"]["NULL_PLAN"] == "NOT_APPLICABLE") == (mode == "pilot")
    for name in (*shas, "summary.md"):
        assert rid.encode() not in published[name] and b"realization_id" not in published[name]
    assert all(did.encode() in published[name] for name in shas)


@pytest.mark.parametrize("case", ["before", "after"])
def test_finalize_recovers_a_crash_around_the_directory_replace(tmp_path, monkeypatch, case):
    import hashlib
    import json
    import os
    from pathlib import Path
    finalize, real_replace = _kernel("finalize"), os.replace
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    temp, calls, seen = out.parent / f".out.publish-{authority['design_id'][:16]}.tmp", [], []

    def replace(src, dst):
        if (Path(src), Path(dst)) == (temp, out):
            seen.append(_tree(temp))
            if case == "after":
                real_replace(src, dst)
            raise OSError(f"interrupted {case} the directory replace")
        return real_replace(src, dst)

    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(os, "replace", replace)
        with pytest.raises(OSError, match="interrupted"):
            finalize(staging, out, authority, _b1i_builder(calls))
    assert len(seen) == len(calls) == 1 and not (staging / "phases" / "FINAL.json").exists()
    if case == "before":
        assert not out.exists() and _tree(temp) == seen[0]
    else:
        assert not temp.exists() and _tree(out) == seen[0]
    stamps = {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()} if out.exists() else {}
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        final = finalize(staging, out, authority, _b1i_builder(calls))
    manifest = seen[0]["manifest.json"]
    assert _tree(out) == seen[0] and not temp.exists() and len(calls) == (2 if case == "before" else 1)
    assert final["realization_id"] == json.loads(manifest)["realization_id"]
    assert final["manifest_sha256"] == hashlib.sha256(manifest).hexdigest()
    assert case == "before" or {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()} == stamps


@pytest.mark.parametrize("case", B1I_REFUSALS)
def test_finalize_is_idempotent_and_refuses_foreign_or_corrupt_state(tmp_path, monkeypatch, case):
    finalize = _kernel("finalize")
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    did, calls, marker = authority["design_id"], [], staging / "phases" / "FINAL.json"
    other = did[:16] + ("1" if did[16] == "0" else "0") + did[17:]
    expected = {"other_design_output": _kernel("OutputExists"), "missing_phase": _kernel("PhaseOrderError"),
                "foreign_authority": ValueError}.get(case, _kernel("PartitionMismatch"))
    if case in ("idempotent", "corrupt_publication", "corrupt_final", "changed_go_reference"):
        first = finalize(staging, out, authority, _b1i_builder(calls))
    if case == "corrupt_publication":
        marker.unlink()
        _b1i_flip(out / "selections.csv")
    elif case == "corrupt_final":
        marker.write_text(pdb.canon({**first, "realization_id": "0" * 64}) + "\n")
    elif case == "changed_go_reference":
        marker.unlink()
        go = tmp_path / "prompts" / "GO-full-alternate.md"
        go.write_text(f"Alternate synthetic full GO fixture citing design {did}\n")
        ref = {"path": "prompts/GO-full-alternate.md", "sha256": pdb.file_sha256(go)}
        cfg = {**_edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19),
               "authorization": {"stage": "full", "design_id": did, "go_reference": ref}}
        changed = _kernel("authorize")("full", cfg, _kernel("design_descriptor")(cfg, "full"), 1)
        assert changed == {**authority, "go_reference": ref} and ref != authority["go_reference"]
        authority = changed
    elif case == "other_design_output":
        out.mkdir()
        (out / "manifest.json").write_text(pdb.canon({"design_id": other}) + "\n")
    elif case == "corrupt_partition":
        _b1i_flip(sorted((staging / "partitions").glob("*.npz"))[0])
    elif case == "missing_phase":
        (staging / "phases" / "ALT.json").unlink()
    elif case == "foreign_authority":
        authority = {**authority, "design_id": "f" * 64}
    before, had_out, done = _tree(tmp_path), out.exists(), len(calls)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        if case == "idempotent":
            assert finalize(staging, out, authority, _b1i_builder(calls)) == first
        else:
            with pytest.raises(expected):
                finalize(staging, out, authority, _b1i_builder(calls))
    assert _tree(tmp_path) == before and out.exists() == had_out and len(calls) == done
    assert not list(tmp_path.glob(".out.publish-*"))


@pytest.mark.parametrize("case", B1I_TEMPS)
def test_finalize_rebuilds_only_a_fully_owned_temp(tmp_path, monkeypatch, case):
    finalize, exists = _kernel("finalize"), _kernel("OutputExists")
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    did, calls = authority["design_id"], []
    temp = out.parent / f".out.publish-{did[:16]}.tmp"
    other = did[:16] + ("1" if did[16] == "0" else "0") + did[17:]
    if case in ("builder_interrupted", "interrupted_then_foreign_notes"):
        with pytest.raises(RuntimeError, match="interrupted"):
            finalize(staging, out, authority, _b1i_builder(calls, fail=True))
        assert "selections.csv" in _tree(temp) and not out.exists() and not (staging / "phases" / "FINAL.json").exists()
    else:
        temp.mkdir()
    claimed = {"foreign_design_temp": other, "same_did_incomplete_manifest": did}.get(case)
    if claimed:
        (temp / "manifest.json").write_text(pdb.canon({"design_id": claimed}) + "\n")
    if case in ("unowned_temp", "same_did_incomplete_manifest", "interrupted_then_foreign_notes"):
        (temp / "notes.txt").write_text("unrelated content\n")
    if case == "builder_interrupted":
        with monkeypatch.context() as mp:
            _b1i_no_recompute(mp)
            final = finalize(staging, out, authority, _b1i_builder(calls))
        assert len(calls) == 2 and not temp.exists() and final["design_id"] == did
        assert set(_tree(out)) == {"selections.csv", "calibration.csv", "aggregates.csv", *B1G_META}
        return
    before, done = _tree(tmp_path), len(calls)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        with pytest.raises(exists):
            finalize(staging, out, authority, _b1i_builder(calls))
    assert _tree(tmp_path) == before and len(calls) == done and not out.exists() and temp.is_dir()


@pytest.mark.parametrize("excess", [0, 1], ids=["at_limit", "over_limit"])
def test_finalize_checks_payload_size_metadata_before_reading_payloads(tmp_path, monkeypatch, excess):
    import hashlib
    finalize, realize = _kernel("finalize"), _kernel("realization")
    staging, out, authority, records = _b1i_setup(tmp_path, monkeypatch)
    phases, calls, attempts = _tree(staging), [], []
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)

        def build(temp, did, given):
            telemetry = _b1i_builder(calls)(temp, did, given)
            assert (temp / "aggregates.csv").stat().st_size < 1 << 16
            _b1g_sized(mp, temp / "aggregates.csv", 50 * 1024 * 1024 + excess)
            if excess:
                attempts.append(_b1g_referent_reads(mp, temp.resolve()))
            return telemetry

        if excess:
            with pytest.raises(ValueError):
                finalize(staging, out, authority, build)
        else:
            final = finalize(staging, out, authority, build)
    temp = out.parent / f".out.publish-{authority['design_id'][:16]}.tmp"
    assert len(calls) == 1 and {n: d for n, d in _tree(staging).items() if n != "phases/FINAL.json"} == phases
    if excess:
        assert attempts == [[]] and not out.exists() and not (staging / "phases" / "FINAL.json").exists()
        assert "manifest.json" not in _tree(temp)
    else:
        shas = {n: hashlib.sha256(d).hexdigest() for n, d in _tree(out).items() if n.endswith(".csv")}
        assert final["realization_id"] == realize(records, shas)[0] and not temp.exists()
        assert (staging / "phases" / "FINAL.json").read_text() == pdb.canon(final) + "\n"


def test_finalize_recovery_fsyncs_the_output_parent_before_committing_final(tmp_path, monkeypatch):
    import json
    import os
    from pathlib import Path
    finalize, real_replace, real_fsync = _kernel("finalize"), os.replace, os.fsync
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    temp, calls, events = out.parent / f".out.publish-{authority['design_id'][:16]}.tmp", [], []
    final_path = staging / "phases" / "FINAL.json"

    def crash(src, dst):
        real_replace(src, dst)
        if (Path(src), Path(dst)) == (temp, out):
            raise OSError("interrupted after the directory replace, before the parent fsync")

    with monkeypatch.context() as mp:
        mp.setattr(os, "replace", crash)
        with pytest.raises(OSError, match="interrupted after"):
            finalize(staging, out, authority, _b1i_builder(calls))
    published, stamps = _tree(out), {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()}
    assert not temp.exists() and not final_path.exists() and len(calls) == 1
    parent = (out.parent.stat().st_dev, out.parent.stat().st_ino)

    def fsync(fd):
        st = os.fstat(fd)
        events.append("parent_fsync" if (st.st_dev, st.st_ino) == parent else "other_fsync")
        return real_fsync(fd)

    def replace(src, dst):
        if Path(dst) == final_path:
            events.append("final_commit")
        return real_replace(src, dst)

    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(os, "fsync", fsync)
        mp.setattr(os, "replace", replace)
        final = finalize(staging, out, authority, _b1i_builder(calls))
    assert events.count("final_commit") == 1 and "parent_fsync" in events[:events.index("final_commit")]
    assert len(calls) == 1 and _tree(out) == published and final_path.read_text() == pdb.canon(final) + "\n"
    assert {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()} == stamps
    assert json.loads(published["manifest.json"])["authority"] == authority and final["design_id"] == authority["design_id"]


B1J_TEMPS = ("malformed_marker", "noncanonical_marker", "wrong_full_did_marker", "symbolic_marker", "symbolic_temp",
             "nonregular_child")


@pytest.mark.parametrize("case", B1J_TEMPS)
def test_finalize_refuses_unverifiable_temp_ownership_evidence(tmp_path, monkeypatch, case):
    finalize, exists = _kernel("finalize"), _kernel("OutputExists")
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    did, calls = authority["design_id"], []
    other = did[:16] + ("1" if did[16] == "0" else "0") + did[17:]
    temp, owner = out.parent / f".out.publish-{did[:16]}.tmp", (pdb.canon({"design_id": did}) + "\n").encode()
    markers = {"malformed_marker": b"{", "noncanonical_marker": owner[:-1] + b"\r",
               "wrong_full_did_marker": (pdb.canon({"design_id": other}) + "\n").encode()}
    referent = tmp_path / ("referent" if case == "symbolic_temp" else "referent.json")
    holder = referent if case == "symbolic_temp" else temp
    holder.mkdir()
    (holder / "selections.csv").write_text(f"design_id\n{did}\n")
    if case == "symbolic_temp":
        (referent / ".owner.json").write_bytes(owner)
        temp.symlink_to(referent)
    elif case == "symbolic_marker":
        referent.write_bytes(owner)
        (temp / ".owner.json").symlink_to(referent)
    else:
        (temp / ".owner.json").write_bytes(markers.get(case, owner))
        if case == "nonregular_child":
            (temp / "partitions").mkdir()
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1i_no_recompute(mp)
        attempts = _b1g_referent_reads(mp, referent)
        with pytest.raises(exists):
            finalize(staging, out, authority, _b1i_builder(calls))
    link = {"symbolic_temp": temp, "symbolic_marker": temp / ".owner.json"}.get(case)
    assert attempts == [] and not calls and _tree(tmp_path) == before and not out.exists()
    assert (link is None or link.readlink() == referent) and (case != "nonregular_child" or (temp / "partitions").is_dir())


@pytest.mark.parametrize("case", ["publication_absent", "changed_go_reference"])
def test_finalize_existing_final_requires_its_publication_and_authority(tmp_path, monkeypatch, case):
    finalize, mismatch = _kernel("finalize"), _kernel("PartitionMismatch")
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    did, calls = authority["design_id"], []
    finalize(staging, out, authority, _b1i_builder(calls))
    if case == "publication_absent":
        out.rename(tmp_path / "moved")
    else:
        go = tmp_path / "prompts" / "GO-full-alternate.md"
        go.write_text(f"Alternate synthetic full GO fixture citing design {did}\n")
        ref = {"path": "prompts/GO-full-alternate.md", "sha256": pdb.file_sha256(go)}
        cfg = {**_edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19),
               "authorization": {"stage": "full", "design_id": did, "go_reference": ref}}
        changed = _kernel("authorize")("full", cfg, _kernel("design_descriptor")(cfg, "full"), 1)
        assert changed == {**authority, "go_reference": ref} and ref != authority["go_reference"]
        authority = changed
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        with pytest.raises(mismatch):
            finalize(staging, out, authority, _b1i_builder(calls))
    assert _tree(tmp_path) == before and len(calls) == 1 and out.exists() == (case == "changed_go_reference")
    assert (staging / "phases" / "FINAL.json").is_file() and not list(tmp_path.glob(".out.publish-*"))


@pytest.mark.parametrize("change", [{"stage": "pilot"}, {"go_reference": None}], ids=["stage_not_mode", "full_without_go"])
def test_finalize_refuses_invalid_authority_handoff_before_effects(tmp_path, monkeypatch, change):
    finalize = _kernel("finalize")
    staging, out, authority, _ = _b1i_setup(tmp_path, monkeypatch)
    calls, before = [], _tree(tmp_path)
    assert authority["stage"] == "full" and authority["go_reference"] is not None
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1i_no_recompute(mp)
        with pytest.raises(ValueError):
            finalize(staging, out, {**authority, **change}, _b1i_builder(calls))
    assert not calls and _tree(tmp_path) == before and not out.exists() and not list(tmp_path.glob(".out.publish-*"))


@pytest.mark.parametrize("case", ["empty_temp", "smoke"])
def test_finalize_recovers_an_empty_temp_and_finalizes_a_smoke_design(tmp_path, monkeypatch, case):
    import hashlib
    import json
    finalize, realize = _kernel("finalize"), _kernel("realization")
    if case == "smoke":
        cfg = _edited(_design_cfg(), ("modes", "smoke", "sizes", "CAL_NULL"), 19)
        authority = _kernel("authorize")("smoke", cfg, _kernel("design_descriptor")(cfg, "smoke"), 1)
        staging, out, parts = _b1e_staging(tmp_path / "logs", "smoke"), tmp_path / "out", _b1e_parts(1, 2)
        part, record, lineage = _kernel("partition"), _kernel("phase_record"), {}
        for phase in B1E_ORDER:
            for key, arrays in parts[phase]:
                part(staging, phase, dict(lineage), key, lambda arrays=arrays: arrays)
            content = B1E_SMOKE_PLAN if phase == "NULL_PLAN" else B1F_DERIVED[phase]
            lineage[phase] = record(staging, phase, dict(lineage), [k for k, _ in parts[phase]], content)["phase_digest"]
        records = {phase: record(staging, phase, None, None, None) for phase in B1E_ORDER}
    else:
        staging, out, authority, records = _b1i_setup(tmp_path, monkeypatch)
    did, calls = authority["design_id"], []
    temp = out.parent / f".out.publish-{did[:16]}.tmp"
    if case == "empty_temp":
        temp.mkdir()
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        final = finalize(staging, out, authority, _b1i_builder(calls))
    published = _tree(out)
    rid, real = realize(records, {n: hashlib.sha256(d).hexdigest() for n, d in published.items() if n.endswith(".csv")})
    manifest = json.loads(published["manifest.json"])
    assert calls == [did] and not temp.exists() and final["realization_id"] == rid == manifest["realization_id"]
    assert (staging / "phases" / "FINAL.json").read_text() == pdb.canon(final) + "\n"
    assert "FINAL" not in real["phase_digests"] and manifest["authority"] == authority
    assert set(published) == {"selections.csv", "calibration.csv", "aggregates.csv", *B1G_META}
    if case == "smoke":
        assert authority == {"stage": "smoke", "design_id": did, "go_reference": None}
        assert records["SETUP"]["design_id"] == did and manifest["design_descriptor"]["mode"] == "smoke"
        assert real["phase_digests"]["NULL_PLAN"] == records["NULL_PLAN"]["phase_digest"] != "NOT_APPLICABLE"
        assert (real["plan_id"], real["n_hold"]) == (B1E_PLAN_ID, B1E_SMOKE_PLAN["n_hold"])


B1K_INTEGRITY = ("committed_npz_corrupt", "committed_npz_missing", "committed_digest_wrong", "plan_contradicts_committed",
                 "cached_alt_corrupt")
B1K_PLANS = ("foreign_phase", "duplicate_key", "bool_alias", "unsorted_keys", "path_label")


def _b1k_parts():
    parts = _b1e_parts(2, 5)
    return {**parts, "ALT": [*parts["ALT"], (["ALT", *B1E_PRIMARY, "F_HEAD_RESIDUAL"], {"first": np.array([7])})]}


def _b1k_setup(root, monkeypatch, complete=True):
    cfg = _edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19)
    desc = _kernel("design_descriptor")(cfg, "full")
    cfg, did = _authorized(root, monkeypatch, cfg, "full")
    authority = _kernel("authorize")("full", cfg, desc, 1)
    staging, parts = _b1e_staging(root / "logs", "full"), _b1k_parts()
    part, record, lineage = _kernel("partition"), _kernel("phase_record"), {}
    for phase in B1E_ORDER:
        commit = complete or phase != "ALT"
        for key, arrays in parts[phase] if commit else parts[phase][:1]:
            part(staging, phase, dict(lineage), key, lambda arrays=arrays: arrays)
        if commit:
            content = B1E_FULL_PLAN if phase == "NULL_PLAN" else B1F_DERIVED[phase]
            lineage[phase] = record(staging, phase, dict(lineage), [k for k, _ in parts[phase]], content)["phase_digest"]
    plan = {phase: sorted((k for k, _ in parts[phase]), key=pdb.canon) for phase in B1E_ORDER}
    assert staging.name == did[:16] and authority["design_id"] == did
    return staging, root / "out", authority, plan, lineage


def test_planned_gate_reports_incomplete_then_resumes_to_identical_publication(tmp_path, monkeypatch):
    import hashlib
    import json
    gate, part, record = _kernel("finalize_planned"), _kernel("partition"), _kernel("phase_record")
    staging, out, authority, plan, lineage = _b1k_setup(tmp_path / "run", monkeypatch, complete=False)
    did, calls, alt, status_path = authority["design_id"], [], _b1k_parts()["ALT"], staging / "status.json"
    before = _tree(staging)

    def incomplete(missing):
        expected = {"status": "INCOMPLETE", "design_id": did, "last_complete_phase": "HOLD",
                    "missing_partitions": [{"phase": "ALT", "key": key} for key in missing]}
        with monkeypatch.context() as mp:
            _b1i_no_recompute(mp)
            assert gate(staging, out, authority, plan, _b1i_builder(calls)) == expected
        assert status_path.read_text() == pdb.canon(expected) + "\n" and not calls and not out.exists()
        assert not list(out.parent.glob(".out.publish-*")) and not (staging / "phases" / "ALT.json").exists()
        assert not (staging / "phases" / "FINAL.json").exists()

    incomplete([alt[1][0]])
    assert {name: data for name, data in _tree(staging).items() if name != "status.json"} == before
    cached, cached_calls = _counted(lambda: alt[0][1])
    fresh, fresh_calls = _counted(lambda: alt[1][1])
    part(staging, "ALT", dict(lineage), alt[0][0], cached)
    part(staging, "ALT", dict(lineage), alt[1][0], fresh)
    assert not cached_calls and len(fresh_calls) == 1
    incomplete([])
    record(staging, "ALT", dict(lineage), [key for key, _ in alt], B1F_DERIVED["ALT"])
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        final = gate(staging, out, authority, plan, _b1i_builder(calls))
    done = {"status": "PUBLISHED", "design_id": did, "last_complete_phase": "ALT", "missing_partitions": []}
    assert calls == [did] and final == json.loads((staging / "phases" / "FINAL.json").read_text())
    assert status_path.read_text() == pdb.canon(done) + "\n"
    reference = _b1k_setup(tmp_path / "reference", monkeypatch)
    expected = gate(reference[0], reference[1], reference[2], plan, _b1i_builder([]))
    shas = [{n: hashlib.sha256(d).hexdigest() for n, d in _tree(folder).items() if n.endswith(".csv")}
            for folder in (out, reference[1])]
    assert final["realization_id"] == expected["realization_id"] and shas[0] == shas[1] and len(shas[0]) == 3


@pytest.mark.parametrize("case", B1K_INTEGRITY)
def test_planned_gate_refuses_corrupt_or_contradicted_state_instead_of_incomplete(tmp_path, monkeypatch, case):
    import json
    gate, mismatch = _kernel("finalize_planned"), _kernel("PartitionMismatch")
    staging, out, authority, plan, lineage = _b1k_setup(tmp_path, monkeypatch, complete=False)
    did, calls, parts = authority["design_id"], [], _b1k_parts()
    hold = _partition_stem(staging, did, {p: lineage[p] for p in B1E_ORDER[:4]}, parts["HOLD"][0][0]).with_suffix(".npz")
    cached = _partition_stem(staging, did, lineage, parts["ALT"][0][0]).with_suffix(".npz")
    assert hold.is_file() and cached.is_file()
    if case == "committed_npz_corrupt":
        _b1i_flip(hold)
    elif case == "committed_npz_missing":
        hold.unlink()
    elif case == "committed_digest_wrong":
        path = staging / "phases" / "HOLD.json"
        path.write_text(pdb.canon({**json.loads(path.read_text()), "phase_digest": "0" * 64}) + "\n")
    elif case == "plan_contradicts_committed":
        plan = {**plan, "HOLD": plan["HOLD"][:1]}
    else:
        _b1i_flip(cached)
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        with pytest.raises(mismatch):
            gate(staging, out, authority, plan, _b1i_builder(calls))
    assert _tree(tmp_path) == before and not calls and not out.exists() and not (staging / "status.json").exists()


@pytest.mark.parametrize("case", B1K_PLANS)
def test_planned_gate_refuses_invalid_plans_before_any_effect(tmp_path, monkeypatch, case):
    gate = _kernel("finalize_planned")
    staging, out, authority, plan, _ = _b1k_setup(tmp_path, monkeypatch, complete=False)
    alt, calls = plan["ALT"], []
    bad = {"foreign_phase": {**plan, "FINAL": []}, "duplicate_key": {**plan, "ALT": [alt[0], alt[0], alt[1]]},
           "bool_alias": {**plan, "ALT": [[*alt[0][:3], False, alt[0][4]], alt[1]]},
           "unsorted_keys": {**plan, "ALT": alt[::-1]},
           "path_label": {**plan, "ALT": [alt[0], [*alt[1][:4], "partitions/F_HEAD_RESIDUAL.npz"]]}}[case]
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1i_no_recompute(mp)
        with pytest.raises(ValueError):
            gate(staging, out, authority, bad, _b1i_builder(calls))
    assert _tree(tmp_path) == before and not calls and not out.exists()


def test_planned_gate_refuses_a_later_record_without_its_predecessor(tmp_path, monkeypatch):
    gate, order_error = _kernel("finalize_planned"), _kernel("PhaseOrderError")
    staging, out, authority, plan, _ = _b1k_setup(tmp_path, monkeypatch)
    calls = []
    assert all((staging / "phases" / f"{p}.json").is_file() for p in B1E_ORDER)
    (staging / "phases" / "NULL_PLAN.json").unlink()
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        with pytest.raises(order_error):
            gate(staging, out, authority, plan, _b1i_builder(calls))
    assert _tree(tmp_path) == before and not calls and not out.exists() and not (staging / "status.json").exists()
    assert not list(tmp_path.glob(".out.publish-*")) and not (staging / "phases" / "FINAL.json").exists()


def test_planned_gate_status_write_is_atomic_and_retried_truthfully(tmp_path, monkeypatch):
    import json
    import os
    from pathlib import Path
    gate, part = _kernel("finalize_planned"), _kernel("partition")
    staging, out, authority, plan, lineage = _b1k_setup(tmp_path, monkeypatch, complete=False)
    did, calls, alt, status_path = authority["design_id"], [], _b1k_parts()["ALT"], staging / "status.json"
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        gate(staging, out, authority, plan, _b1i_builder(calls))
    old = status_path.read_bytes()
    assert json.loads(old)["missing_partitions"] == [{"phase": "ALT", "key": alt[1][0]}]
    part(staging, "ALT", dict(lineage), alt[1][0], lambda: alt[1][1])
    before, events, real_fsync, real_replace = _tree(tmp_path), [], os.fsync, os.replace

    def fsync(fd):
        events.append(("fsync", os.fstat(fd).st_ino))
        return real_fsync(fd)

    def replace(src, dst):
        events.append(("replace", os.stat(src).st_ino, Path(dst).name))
        if Path(dst) == status_path:
            raise OSError("interrupted before the status replacement")
        return real_replace(src, dst)

    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(os, "fsync", fsync)
        mp.setattr(os, "replace", replace)
        with pytest.raises(OSError, match="interrupted before the status"):
            gate(staging, out, authority, plan, _b1i_builder(calls))
    attempt = [event for event in events if event[0] == "replace" and event[2] == "status.json"]
    assert len(attempt) == 1 and ("fsync", attempt[0][1]) in events[:events.index(attempt[0])]
    assert status_path.read_bytes() == old and _tree(tmp_path) == before and not calls and not out.exists()
    assert not list(tmp_path.glob(".out.publish-*")) and not (staging / "phases" / "ALT.json").exists()
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        status = gate(staging, out, authority, plan, _b1i_builder(calls))
    expected = {"status": "INCOMPLETE", "design_id": did, "last_complete_phase": "HOLD", "missing_partitions": []}
    assert status == expected and status_path.read_text() == pdb.canon(expected) + "\n"
    assert not calls and not out.exists() and not (staging / "phases" / "FINAL.json").exists()


@pytest.mark.parametrize("final_marker", [True, False], ids=["with_final", "published_without_final"])
def test_planned_gate_refuses_a_missing_alt_record_after_publication(tmp_path, monkeypatch, final_marker):
    import json
    gate, order_error = _kernel("finalize_planned"), _kernel("PhaseOrderError")
    staging, out, authority, plan, _ = _b1k_setup(tmp_path, monkeypatch)
    calls, final_path, status_path = [], staging / "phases" / "FINAL.json", staging / "status.json"
    final = gate(staging, out, authority, plan, _b1i_builder(calls))
    assert final_path.is_file() and final["status"] == "PUBLISHED" and len(calls) == 1
    assert json.loads(status_path.read_text())["status"] == "PUBLISHED"
    assert set(_tree(out)) == {"selections.csv", "calibration.csv", "aggregates.csv", *B1G_META}
    if not final_marker:
        final_path.unlink()
    (staging / "phases" / "ALT.json").unlink()
    before = _tree(tmp_path)
    stamps = {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1i_no_recompute(mp)
        with pytest.raises(order_error):
            gate(staging, out, authority, plan, _b1i_builder(calls))
    assert _tree(tmp_path) == before and len(calls) == 1 and final_path.exists() == final_marker
    assert {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in out.iterdir()} == stamps
    assert json.loads(status_path.read_text())["status"] == "PUBLISHED"


def test_planned_gate_refuses_a_symbolic_output_before_reading_its_referent(tmp_path, monkeypatch):
    import json
    gate, exists = _kernel("finalize_planned"), _kernel("OutputExists")
    staging, out, authority, plan, _ = _b1k_setup(tmp_path, monkeypatch)
    calls, referent, status_path = [], tmp_path / "published-referent", staging / "status.json"
    gate(staging, out, authority, plan, _b1i_builder(calls))
    assert len(calls) == 1 and json.loads(status_path.read_text())["status"] == "PUBLISHED"
    out.rename(referent)
    out.symlink_to(referent)
    (staging / "phases" / "FINAL.json").unlink()
    (staging / "phases" / "ALT.json").unlink()
    before = _tree(tmp_path)
    stamps = {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in referent.iterdir()}
    assert out.is_symlink() and out.readlink() == referent and "manifest.json" in stamps
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1i_no_recompute(mp)
        attempts = _b1g_referent_reads(mp, referent)
        with pytest.raises(exists):
            gate(staging, out, authority, plan, _b1i_builder(calls))
    assert attempts == [] and _tree(tmp_path) == before and len(calls) == 1 and out.readlink() == referent
    assert {p.name: (p.stat().st_ino, p.stat().st_mtime_ns) for p in referent.iterdir()} == stamps
    assert json.loads(status_path.read_text())["status"] == "PUBLISHED"
    assert not (staging / "phases" / "FINAL.json").exists() and not (staging / "phases" / "ALT.json").exists()


B1L_BOUNDARIES = ("cpu_at_cap", "cpu_below_cap", "wall_at_deadline", "wall_below_deadline")


def _b1l_setup(root, monkeypatch, used):
    cfg = _edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19)
    desc = _kernel("design_descriptor")(cfg, "full")
    cfg, did = _authorized(root, monkeypatch, cfg, "full")
    authority = _kernel("authorize")("full", cfg, desc, 1)
    staging, parts, charge = _b1e_staging(root / "logs", "full"), _b1k_parts(), _kernel("charge_cpu")
    assert charge(staging, "invocation-1", 0.0) == 0.0 and set(_tree(staging)) == {"design.json", "resources.json"}
    part, record, lineage = _kernel("partition"), _kernel("phase_record"), {}
    for phase in B1E_ORDER[:-1]:
        for key, arrays in parts[phase]:
            part(staging, phase, dict(lineage), key, lambda arrays=arrays: arrays)
        content = B1E_FULL_PLAN if phase == "NULL_PLAN" else B1F_DERIVED[phase]
        lineage[phase] = record(staging, phase, dict(lineage), [k for k, _ in parts[phase]], content)["phase_digest"]
    part(staging, "ALT", dict(lineage), parts["ALT"][0][0], lambda: parts["ALT"][0][1])
    assert charge(staging, "invocation-1", used) == used and authority["design_id"] == did
    plan = {phase: sorted((k for k, _ in parts[phase]), key=pdb.canon) for phase in B1E_ORDER}
    return staging, root / "out", authority, plan, lineage


@pytest.mark.parametrize("case", B1L_BOUNDARIES)
def test_require_budget_blocks_at_the_cpu_cap_and_the_wall_deadline(tmp_path, monkeypatch, case):
    import time
    require, blocked = _kernel("require_budget"), _kernel("ResourceBlocked")
    env = _design_cfg()["envelope"]
    cap, wall = env["cpu_hours_max"] * 3600, env["wall_seconds_per_invocation"]
    used = {"cpu_at_cap": cap, "cpu_below_cap": math.nextafter(cap, 0.0)}.get(case, 0.0)
    elapsed = {"wall_at_deadline": float(wall), "wall_below_deadline": math.nextafter(wall, 0.0)}.get(case, 0.0)
    staging, out, authority, plan, _ = _b1l_setup(tmp_path, monkeypatch, used)
    did, alt, before, status = authority["design_id"], _b1k_parts()["ALT"], _tree(staging), staging / "status.json"
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(time, "monotonic", lambda: elapsed)
        if "below" in case:
            remaining = require(staging, authority, plan, 0.0)
        else:
            with pytest.raises(blocked):
                require(staging, authority, plan, 0.0)
    assert blocked is pdb.ResourceBlocked and not out.exists() and not (staging / "phases" / "ALT.json").exists()
    if "below" in case:
        assert remaining == cap - used and not status.exists() and _tree(staging) == before
    else:
        expected = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": "HOLD",
                    "missing_partitions": [{"phase": "ALT", "key": alt[1][0]}]}
        assert status.read_text() == pdb.canon(expected) + "\n"
        assert {name: data for name, data in _tree(staging).items() if name != "status.json"} == before


def test_charge_cpu_accumulates_monotone_token_checkpoints_across_invocations(tmp_path, monkeypatch):
    import json
    charge = _kernel("charge_cpu")
    staging, _, authority, _, _ = _b1l_setup(tmp_path, monkeypatch, 2.5)
    journal, did = staging / "resources.json", authority["design_id"]
    assert journal.read_text() == pdb.canon({"design_id": did, "cpu_seconds": {"invocation-1": 2.5}}) + "\n"
    assert charge(staging, "invocation-1", 2.5) == 2.5 and charge(staging, "invocation-2", 0.0) == 2.5
    assert charge(staging, "invocation-2", 1.25) == 3.75 and charge(staging, "invocation-2", 2.0) == 4.5
    kept = journal.read_bytes()
    assert json.loads(kept) == {"design_id": did, "cpu_seconds": {"invocation-1": 2.5, "invocation-2": 2.0}}
    for token, seconds in (("invocation-2", 1.0), ("invocation-3", -0.5), ("invocation-3", math.nan),
                           ("invocation-3", math.inf), ("invocation-3", True), ("", 1.0)):
        with pytest.raises(ValueError):
            charge(staging, token, seconds)
    assert journal.read_bytes() == kept


@pytest.mark.parametrize("case", ["malformed", "wrong_design", "missing_with_work"])
def test_resource_journal_refusals_never_reset_the_spent_budget(tmp_path, monkeypatch, case):
    import time
    charge, require, mismatch = _kernel("charge_cpu"), _kernel("require_budget"), _kernel("PartitionMismatch")
    staging, _, authority, plan, _ = _b1l_setup(tmp_path, monkeypatch, 2.5)
    journal = staging / "resources.json"
    if case == "malformed":
        journal.write_text("{")
    elif case == "wrong_design":
        journal.write_text(pdb.canon({"design_id": "f" * 64, "cpu_seconds": {"invocation-1": 2.5}}) + "\n")
    else:
        journal.unlink()
    before = _tree(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(time, "monotonic", lambda: 0.0)
        for call in (lambda: charge(staging, "invocation-2", 0.0), lambda: require(staging, authority, plan, 0.0)):
            with pytest.raises(mismatch):
                call()
    assert _tree(tmp_path) == before and not (staging / "status.json").exists()


def test_resource_resume_keeps_spent_cpu_and_finishes_the_missing_work(tmp_path, monkeypatch):
    import json
    import time
    require, charge, blocked = _kernel("require_budget"), _kernel("charge_cpu"), _kernel("ResourceBlocked")
    gate, part, record = _kernel("finalize_planned"), _kernel("partition"), _kernel("phase_record")
    env = _design_cfg()["envelope"]
    cap, wall = env["cpu_hours_max"] * 3600, float(env["wall_seconds_per_invocation"])
    staging, out, authority, plan, lineage = _b1l_setup(tmp_path, monkeypatch, 600.0)
    did, alt, calls, status = authority["design_id"], _b1k_parts()["ALT"], [], staging / "status.json"
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(time, "monotonic", lambda: wall)
        with pytest.raises(blocked):
            require(staging, authority, plan, 0.0)
    assert json.loads(status.read_text())["status"] == "BLOCKED_RESOURCE"
    cached, (produce, made) = _tree(staging / "partitions"), _counted(lambda: alt[1][1])
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        mp.setattr(time, "monotonic", lambda: 5001.0)
        assert charge(staging, "invocation-2", 0.0) == 600.0
        assert require(staging, authority, plan, 5000.0) == cap - 600.0
        part(staging, "ALT", dict(lineage), alt[1][0], produce)
        assert charge(staging, "invocation-2", 30.0) == 630.0
        record(staging, "ALT", dict(lineage), [key for key, _ in alt], B1F_DERIVED["ALT"])
        assert require(staging, authority, plan, 5000.0) == cap - 630.0
        final = gate(staging, out, authority, plan, _b1i_builder(calls))
    done = {"status": "PUBLISHED", "design_id": did, "last_complete_phase": "ALT", "missing_partitions": []}
    assert len(made) == 1 and calls == [did] and final["design_id"] == did and json.loads(status.read_text()) == done
    assert {name: data for name, data in _tree(staging / "partitions").items() if name in cached} == cached
    spent = json.loads((staging / "resources.json").read_text())["cpu_seconds"]
    assert spent == {"invocation-1": 600.0, "invocation-2": 30.0}


def _b1m_clock(mp, state):
    import os
    import time

    def times():
        cpu = state["cpu"]
        return os.times_result((cpu / 8, cpu / 8, cpu / 4, cpu / 2, 1.0e6))

    mp.setattr(os, "times", times)
    mp.setattr(time, "monotonic", lambda: state["wall"])


def test_start_invocation_opens_a_fresh_token_from_self_and_children_cpu(tmp_path, monkeypatch):
    import json
    start = _kernel("start_invocation")
    cfg = _edited(_design_cfg(), ("modes", "full", "sizes", "CAL_NULL"), 19)
    desc = _kernel("design_descriptor")(cfg, "full")
    cfg, did = _authorized(tmp_path, monkeypatch, cfg, "full")
    authority = _kernel("authorize")("full", cfg, desc, 1)
    staging, parts = _b1e_staging(tmp_path / "logs", "full"), _b1k_parts()
    plan = {phase: sorted((k for k, _ in parts[phase]), key=pdb.canon) for phase in B1E_ORDER}
    journal, state = staging / "resources.json", {"cpu": math.nan, "wall": 100.0}
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        with pytest.raises(ValueError):
            start(staging, authority, plan, "invocation-A")
        assert not journal.exists()
        state["cpu"] = 10.0
        context = start(staging, authority, plan, "invocation-A")
        kept = journal.read_bytes()
        state.update(cpu=20.0, wall=200.0)
        with pytest.raises(ValueError):
            start(staging, authority, plan, "invocation-A")
    assert set(context) == {"staging", "authority", "plan", "token", "cpu_start", "started"}
    assert (context["token"], context["cpu_start"], context["started"]) == ("invocation-A", 10.0, 100.0)
    assert json.loads(kept) == {"design_id": did, "cpu_seconds": {"invocation-A": 0.0}} and journal.read_bytes() == kept
    assert set(_tree(staging)) == {"design.json", "resources.json"}


@pytest.mark.parametrize("case", ["cpu_exhausted", "wall_exhausted"])
def test_guarded_partition_blocks_before_running_its_producer(tmp_path, monkeypatch, case):
    import json
    start, guarded, blocked = _kernel("start_invocation"), _kernel("guarded_partition"), _kernel("ResourceBlocked")
    env = _design_cfg()["envelope"]
    cap, wall = env["cpu_hours_max"] * 3600, float(env["wall_seconds_per_invocation"])
    used = cap - 1.0 if case == "cpu_exhausted" else 0.0
    staging, out, authority, plan, lineage = _b1l_setup(tmp_path, monkeypatch, used)
    alt, state = _b1k_parts()["ALT"], {"cpu": 10.0, "wall": 100.0}
    produce, made = _counted(lambda: alt[1][1])
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = start(staging, authority, plan, "invocation-2")
        cached = _tree(staging / "partitions")
        state.update(cpu=11.0, wall=100.0 + (wall if case == "wall_exhausted" else 0.0))
        with pytest.raises(blocked):
            guarded(context, "ALT", dict(lineage), alt[1][0], produce)
    expected = {"status": "BLOCKED_RESOURCE", "design_id": authority["design_id"], "last_complete_phase": "HOLD",
                "missing_partitions": [{"phase": "ALT", "key": alt[1][0]}]}
    assert not made and _tree(staging / "partitions") == cached and not out.exists()
    assert json.loads((staging / "status.json").read_text()) == expected
    assert not (staging / "phases" / "ALT.json").exists() and not (staging / "phases" / "FINAL.json").exists()
    spent = json.loads((staging / "resources.json").read_text())["cpu_seconds"]
    assert spent == {"invocation-1": used, "invocation-2": 1.0}


def test_guarded_partition_charges_joined_cpu_and_reuses_the_cache(tmp_path, monkeypatch):
    import json
    start, guarded, record = _kernel("start_invocation"), _kernel("guarded_partition"), _kernel("phase_record")
    staging, _, authority, plan, lineage = _b1l_setup(tmp_path, monkeypatch, 5.0)
    did, alt, journal = authority["design_id"], _b1k_parts()["ALT"], staging / "resources.json"
    state, seen = {"cpu": 10.0, "wall": 100.0}, []

    def produce():
        seen.append(json.loads(journal.read_text())["cpu_seconds"]["invocation-2"])
        state["cpu"] += 1.5
        return alt[1][1]

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = start(staging, authority, plan, "invocation-2")
        state["cpu"] = 10.5
        arrays = guarded(context, "ALT", dict(lineage), alt[1][0], produce)
        after_unit = json.loads(journal.read_text())["cpu_seconds"]["invocation-2"]
        state["cpu"] = 12.25
        again = guarded(context, "ALT", dict(lineage), alt[1][0], produce)
        record(staging, "ALT", dict(lineage), [key for key, _ in alt], B1F_DERIVED["ALT"])
        state.update(cpu=50.0, wall=500.0)
        start(staging, authority, plan, "invocation-3")
    spent = json.loads(journal.read_text())["cpu_seconds"]
    assert seen == [0.5] and after_unit == 2.0 and spent == {"invocation-1": 5.0, "invocation-2": 2.25, "invocation-3": 0.0}
    assert _same_arrays(arrays, alt[1][1]) and _same_arrays(again, alt[1][1])
    assert _partition_stem(staging, did, lineage, alt[1][0]).with_suffix(".npz").is_file()
    assert (staging / "phases" / "ALT.json").is_file() and not (staging / "status.json").exists()


@pytest.mark.parametrize("case", ["producer_fails", "backwards_counter", "nonfinite_counter"])
def test_guarded_partition_checkpoints_failures_and_refuses_invalid_counters(tmp_path, monkeypatch, case):
    import json
    start, guarded = _kernel("start_invocation"), _kernel("guarded_partition")
    staging, _, authority, plan, lineage = _b1l_setup(tmp_path, monkeypatch, 5.0)
    did, alt, journal = authority["design_id"], _b1k_parts()["ALT"], staging / "resources.json"
    state, missing = {"cpu": 10.0, "wall": 100.0}, _partition_stem(staging, did, lineage, alt[1][0])

    def produce():
        state["cpu"] += 3.0
        raise RuntimeError("producer interrupted after partial work")

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = start(staging, authority, plan, "invocation-2")
        state["cpu"] = 12.0
        guarded(context, "ALT", dict(lineage), alt[0][0], produce)
        cached, kept = _tree(staging / "partitions"), journal.read_bytes()
        state["cpu"] = {"producer_fails": 12.5, "backwards_counter": 11.0, "nonfinite_counter": math.nan}[case]
        with pytest.raises(RuntimeError if case == "producer_fails" else ValueError):
            guarded(context, "ALT", dict(lineage), alt[1][0], produce)
    spent = json.loads(journal.read_text())["cpu_seconds"]
    assert _tree(staging / "partitions") == cached and not missing.with_suffix(".json").exists()
    if case == "producer_fails":
        assert spent == {"invocation-1": 5.0, "invocation-2": 5.5}
    else:
        assert journal.read_bytes() == kept and spent["invocation-2"] == 2.0


B1N_TAMPERS = ("exact_local", "missing_local", "wrong_local_sha", "foreign_local", "temp_wrong_local_sha")


def _b1n_locals(staging, records):
    import hashlib
    local = {}
    for record in records.values():
        for row in record["partitions"]:
            stem = _partition_stem(staging, record["design_id"], record["upstream"], row["key"])
            sha = hashlib.sha256(stem.with_suffix(".npz").read_bytes()).hexdigest()
            assert sha == row["sha256"]
            local[f"partitions/{stem.name}.npz"] = {"status": "LOCAL_HASHED_ONLY", "sha256": sha}
    return local


def test_finalize_local_inventory_is_staging_relative_and_outside_identity(tmp_path, monkeypatch):
    import hashlib
    import json
    import re
    finalize, realize = _kernel("finalize"), _kernel("realization")
    staging, out, authority, records = _b1i_setup(tmp_path, monkeypatch)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        final = finalize(staging, out, authority, _b1i_builder([]))
    published, local = _tree(out), _b1n_locals(staging, records)
    manifest = json.loads(published["manifest.json"])
    claimed = {name: row for name, row in manifest["payloads"].items() if row["status"] == "LOCAL_HASHED_ONLY"}
    csv = {name: hashlib.sha256(data).hexdigest() for name, data in published.items() if name.endswith(".csv")}
    rows = sum(len(record["partitions"]) for record in records.values())
    assert claimed == local and len(local) == rows > 0
    assert all(re.fullmatch(r"partitions/[0-9a-f]{64}\.npz", name) for name in local)
    assert str(tmp_path) not in published["manifest.json"].decode()
    assert manifest["realization_descriptor"]["payloads"] == csv and realize(records, csv)[0] == manifest["realization_id"]
    assert final["realization_id"] == manifest["realization_id"]
    assert set(final) == {"status", "design_id", "realization_id", "manifest_sha256"}
    assert set(published) == {*csv, *B1G_META} and not (out / "partitions").exists()


@pytest.mark.parametrize("case", B1N_TAMPERS)
def test_finalize_recovery_binds_local_claims_to_the_staged_records(tmp_path, monkeypatch, case):
    import hashlib
    import json
    import os
    import pathlib
    finalize, exists, mismatch = _kernel("finalize"), _kernel("OutputExists"), _kernel("PartitionMismatch")
    staging, out, authority, records = _b1i_setup(tmp_path, monkeypatch)
    calls, final_path = [], staging / "phases" / "FINAL.json"
    finalize(staging, out, authority, _b1i_builder(calls))
    manifest, local = json.loads((out / "manifest.json").read_text()), _b1n_locals(staging, records)
    payloads = {**{name: row for name, row in manifest["payloads"].items() if row["status"] == "PUBLISHED"}, **local}
    first = sorted(local)[0]
    if case.endswith("wrong_local_sha"):
        payloads[first] = {"status": "LOCAL_HASHED_ONLY", "sha256": "0" * 64}
    elif case == "missing_local":
        del payloads[first]
    elif case == "foreign_local":
        payloads[f"partitions/{'f' * 64}.npz"] = {"status": "LOCAL_HASHED_ONLY", "sha256": "e" * 64}
    (out / "manifest.json").write_text(pdb.canon({**manifest, "payloads": payloads}) + "\n")
    final_path.unlink()
    target = out.parent / f".out.publish-{authority['design_id'][:16]}.tmp" if case.startswith("temp_") else out
    if target != out:
        out.rename(target)
    before, done = _tree(tmp_path), len(calls)
    with monkeypatch.context() as mp:
        _b1i_no_recompute(mp)
        if case == "exact_local":
            final = finalize(staging, out, authority, _b1i_builder(calls))
        else:
            _no_side_effects(mp)
            for owner, name in ((pathlib.Path, "unlink"), (pathlib.Path, "rmdir"), (os, "unlink"), (os, "rmdir")):
                mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail(f"deletion attempted: {args!r}"))
            with pytest.raises(exists if case.startswith("temp_") else mismatch):
                finalize(staging, out, authority, _b1i_builder(calls))
    assert len(calls) == done == 1 and target.is_dir()
    if case == "exact_local":
        assert final_path.read_text() == pdb.canon(final) + "\n"
        assert final["manifest_sha256"] == hashlib.sha256((out / "manifest.json").read_bytes()).hexdigest()
        assert {n: d for n, d in _tree(tmp_path).items() if n != final_path.relative_to(tmp_path).as_posix()} == before
    else:
        assert _tree(tmp_path) == before and not final_path.exists()


B2A_INVALID = {"unplanned_n": ("N", 31), "bool_n": ("N", True), "mode": ("mode", "campaign"), "seed": ("seed", 2 ** 32),
               "unordered": ("lambda_1", 1.0), "nonpositive": ("floor", -10.0), "nonfinite": ("scale", math.inf)}


def _b2a_authorized(root, monkeypatch, decay=None):
    cfg = _design_cfg()
    if decay is not None:
        cfg = _edited(cfg, ("parameters", "spectrum", "decay"), decay)
    desc = _kernel("design_descriptor")(cfg, "full")
    cfg, did = _authorized(root, monkeypatch, cfg, "full")
    assert _kernel("authorize")("full", cfg, desc, 1)["design_id"] == did
    return cfg


@pytest.mark.parametrize("N, decay", [(32, None), (239, None), (32, 4.0)], ids=["N32", "N239", "N32_decay4"])
def test_population_frame_is_an_orthonormal_qr_frame_with_a_pre_qr_market_column(tmp_path, monkeypatch, N, decay):
    import copy
    frame = _kernel("population_frame")
    cfg = _b2a_authorized(tmp_path, monkeypatch, decay)
    spec, before, seen, real_qr = cfg["parameters"]["spectrum"], copy.deepcopy(cfg), [], np.linalg.qr

    def qr(a, *args, **kwargs):
        q, r = real_qr(a, *args, **kwargs)
        seen.append((np.array(a, copy=True), q.copy(), r.copy()))
        return q, r

    with monkeypatch.context() as mp:
        mp.setattr(np.linalg, "qr", qr)
        V, lam = frame(cfg, "full", N)
    assert cfg == before and V.shape == (N, N) and lam.shape == (N,) and np.isfinite(V).all() and np.isfinite(lam).all()
    [(a, q, r)] = seen
    root = 1.0 / math.sqrt(N)
    np.testing.assert_allclose(a[:, 0], root, rtol=0, atol=1e-15)
    np.testing.assert_allclose(V[:, 0], root, rtol=0, atol=1e-14)
    np.testing.assert_allclose(V.T @ V, np.eye(N), rtol=0, atol=1e-12)
    assert np.array_equal(V, q * np.sign(np.diag(r))) and (np.diag(V.T @ a) > 0).all()
    tail = [spec["floor"] + spec["scale"] * math.exp(-(k - 2) / spec["decay"]) for k in range(2, N + 1)]
    np.testing.assert_allclose(lam, [spec["lambda_1"], *tail], rtol=1e-14, atol=0)
    assert lam[0] == spec["lambda_1"] == 16.0 and (lam > 0).all() and (np.diff(lam) < 0).all()


def test_population_frame_seed_key_is_the_primitive_frame_entropy(tmp_path, monkeypatch):
    frame = _kernel("population_frame")
    cfg, entropies, real_seq = _b2a_authorized(tmp_path, monkeypatch), [], np.random.SeedSequence

    def seq(entropy=None, *args, **kwargs):
        entropies.append([int(word) for word in entropy])
        return real_seq(entropy, *args, **kwargs)

    def stream28(*args, **kwargs):
        pytest.fail("stream-28 seeding or global PRNG mutation used for the stream-32 frame")

    state = np.random.get_state()
    with monkeypatch.context() as mp:
        mp.setattr(np.random, "SeedSequence", seq)
        for owner, name in ((pdb, "seed_key"), (pdb, "rng"), (np.random, "seed")):
            mp.setattr(owner, name, stream28)
        first, again = frame(cfg, "full", 32), frame(cfg, "full", 32)
        other_seed, other_mode = frame({**cfg, "seed": 3233}, "full", 32), frame(cfg, "smoke", 32)
        wide = frame(cfg, "full", 239)
    after = np.random.get_state()
    full, smoke, label = pdb.label_code("FULL"), pdb.label_code("SMOKE"), pdb.label_code("frame")
    assert entropies == [[32, 3232, full, label, 32], [32, 3232, full, label, 32], [32, 3233, full, label, 32],
                         [32, 3232, smoke, label, 32], [32, 3232, full, label, 239]]
    assert pdb.array_sha256(*first) == pdb.array_sha256(*again) and np.array_equal(first[0], again[0])
    assert not np.array_equal(first[0], other_seed[0]) and not np.array_equal(first[0], other_mode[0])
    assert np.array_equal(first[1], other_seed[1]) and wide[0].shape == (239, 239)
    assert after[0] == state[0] and np.array_equal(after[1], state[1]) and after[2:] == state[2:]


@pytest.mark.parametrize("case", B2A_INVALID)
def test_population_frame_refuses_invalid_inputs_before_any_draw(monkeypatch, case):
    frame = _kernel("population_frame")
    (field, value), cfg, mode, N = B2A_INVALID[case], _design_cfg(), "full", 32
    if field == "N":
        N = value
    elif field == "mode":
        mode = value
    elif field == "seed":
        cfg["seed"] = value
    else:
        cfg = _edited(cfg, ("parameters", "spectrum", field), value)
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        mp.setattr(np.linalg, "qr", lambda *args, **kwargs: pytest.fail("QR before input validation"))
        with pytest.raises(ValueError):
            frame(cfg, mode, N)


B2B_UNIVERSES = {"RESIDUAL": list(range(2, 22)), "MARKET": list(range(1, 21))}
B2B_BASELINES = ("FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90")
B2B_ROOTS = (8, 6, 6, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1)
B2B_TIES = (8.0, *[3.0] * 5, *[2.0] * 10, *[1.0] * 5, *[0.5] * 3)
B2B_INVALID = ("application", "short_residual", "short_market", "matrix", "nonfinite", "nonpositive", "unordered")


def _b2b_spectrum(N):
    spec = _design_cfg()["parameters"]["spectrum"]
    tail = [spec["floor"] + spec["scale"] * math.exp(-(k - 2) / spec["decay"]) for k in range(2, N + 1)]
    return np.array([spec["lambda_1"], *tail])


def _b2b_k90(values):
    values = [float(v) for v in values]
    total = math.fsum(values)
    return next(k for k in range(1, len(values) + 1) if math.fsum(values[:k]) / total >= 0.9)


def _b2b_reference(lam, application):
    values, eligible = [float(v) for v in lam], list(B2B_UNIVERSES[application])
    within = [values[k - 1] for k in eligible]
    mean, k90 = math.fsum(within) / len(within), _b2b_k90(values)
    eigenmean = list(itertools.takewhile(lambda k: values[k - 1] >= mean, eligible))
    cpv90, residual = {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}, {"status": "UNSUPPORTED", "pcs": None}
    if application == "MARKET" and k90 <= eligible[-1]:
        cpv90 = {"status": "RUNNABLE", "pcs": list(range(1, k90 + 1)), "k90": k90}
    if application == "RESIDUAL":
        residual = {"status": "RUNNABLE", "pcs": eligible[:_b2b_k90(within)]}
    rows = {"FULL_K": {"status": "RUNNABLE", "pcs": eligible},
            "FIXED_EIGENMEAN_PREFIX": {"status": "RUNNABLE", "pcs": eigenmean},
            "CPV90": cpv90, "RESIDUAL_CPV90": residual}
    return {"eligible": eligible, "baselines": rows}


@pytest.mark.parametrize("N", [32, 239], ids=["N32", "N239"])
def test_spectral_baselines_fixed_universes_and_canonical_population_rows(monkeypatch, N):
    import inspect
    import json
    module, baselines, cfg = pio(), _kernel("spectral_baselines"), _design_cfg()
    assert list(inspect.signature(baselines).parameters) == ["lam", "application"]
    assert B2B_UNIVERSES == {app: list(range(lo, hi + 1)) for app, (lo, hi) in cfg["applications"].items()}
    assert set(B2B_BASELINES) <= set(cfg["policies"]["static"]) and cfg["parameters"]["K"] == 20
    lam, opened, outs = _b2b_spectrum(N), [], {}
    lam.flags.writeable = False
    before = lam.copy()

    def forbidden(*args, **kwargs):
        pytest.fail("frame draw, fit or decomposition inside the pure spectral baselines")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for owner, name in ((module, "population_frame"), (pdb, "fit_basis"), (np.linalg, "eigvalsh")):
            mp.setattr(owner, name, forbidden)
        for application in B2B_UNIVERSES:
            outs[application] = baselines(lam, application)
            assert all(baselines(lam * scale, application) == outs[application] for scale in (0.125, 3.0))
    assert np.array_equal(lam, before) and not lam.flags.writeable and not opened
    k90 = pdb.cpv90(lam)
    assert k90 == _b2b_k90(lam) and (k90 == 17 if N == 32 else k90 > 20)
    for application, out in outs.items():
        eligible, rows, text = B2B_UNIVERSES[application], out["baselines"], pdb.canon(out)
        assert out == _b2b_reference(lam, application) and json.loads(text) == out and "KAISER" not in text.upper()
        assert set(out) == {"eligible", "baselines"} and out["eligible"] == eligible and len(eligible) == 20
        assert set(rows) == set(B2B_BASELINES) and rows["FULL_K"] == {"status": "RUNNABLE", "pcs": eligible}
        for row in rows.values():
            pcs = row["pcs"]
            assert (row["status"] == "RUNNABLE") == (pcs is not None)
            assert pcs is None or (pcs and pcs == eligible[:len(pcs)] and all(type(k) is int for k in pcs))
    res, mkt = outs["RESIDUAL"]["baselines"], outs["MARKET"]["baselines"]
    assert res["FIXED_EIGENMEAN_PREFIX"]["pcs"] == list(range(2, 10))
    assert mkt["FIXED_EIGENMEAN_PREFIX"]["pcs"] == list(range(1, 8))
    assert res["RESIDUAL_CPV90"] == {"status": "RUNNABLE", "pcs": list(range(2, 17))}
    assert mkt["RESIDUAL_CPV90"] == {"status": "UNSUPPORTED", "pcs": None}
    assert res["CPV90"] == {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}
    market = {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}
    if N == 32:
        market = {"status": "RUNNABLE", "pcs": list(range(1, 18)), "k90": 17}
    assert mkt["CPV90"] == market


def test_spectral_baselines_eigenmean_on_covariance_is_not_correlation_kaiser():
    baselines, n = _kernel("spectral_baselines"), len(B2B_ROOTS)
    cov = np.diag(np.square(np.array(B2B_ROOTS, dtype=np.float64)))
    sd = np.sqrt(np.diag(cov))
    corr = cov / np.outer(sd, sd)
    lam, lam_corr = np.diag(cov).copy(), np.diag(corr).copy()
    assert np.array_equal(corr, np.eye(n)) and np.array_equal(cov, np.diag(lam)) and (np.diff(lam) <= 0).all()
    assert math.fsum(lam[1:21]) / 20 == lam[8] == 9.0 > lam[9]
    expected = {"RESIDUAL": (list(range(2, 10)), list(range(2, 12))), "MARKET": (list(range(1, 7)), None)}
    for application, (eigenmean, residual) in expected.items():
        out, eligible = baselines(lam, application), B2B_UNIVERSES[application]
        rows, kaiser = out["baselines"], [k for k in eligible if lam_corr[k - 1] > 1.0]
        assert out == _b2b_reference(lam, application) and "KAISER" not in pdb.canon(out).upper()
        assert kaiser == [] and [k for k in eligible if lam_corr[k - 1] >= 1.0] == eligible
        assert rows["FIXED_EIGENMEAN_PREFIX"]["pcs"] == eigenmean and eigenmean not in (kaiser, eligible)
        assert rows["CPV90"]["k90"] == 9 and rows["RESIDUAL_CPV90"]["pcs"] == residual


def test_spectral_baselines_keep_exact_mean_and_ninety_percent_ties():
    baselines, lam = _kernel("spectral_baselines"), np.array(B2B_TIES)
    within = lam[1:21]
    assert within.mean() == lam[15] == 2.0 > lam[16] and within[:16].sum() == 0.9 * within.sum() == 36.0
    outs = {application: baselines(lam, application) for application in B2B_UNIVERSES}
    assert all(out == _b2b_reference(lam, application) for application, out in outs.items())
    res, mkt = outs["RESIDUAL"]["baselines"], outs["MARKET"]["baselines"]
    assert res["FIXED_EIGENMEAN_PREFIX"]["pcs"] == list(range(2, 17))
    assert res["RESIDUAL_CPV90"]["pcs"] == list(range(2, 18))
    assert res["CPV90"] == {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": 18}
    assert mkt["FIXED_EIGENMEAN_PREFIX"]["pcs"] == list(range(1, 7))
    assert mkt["CPV90"] == {"status": "RUNNABLE", "pcs": list(range(1, 19)), "k90": 18}


@pytest.mark.parametrize("case", B2B_INVALID)
def test_spectral_baselines_refuse_invalid_inputs_without_effects(monkeypatch, case):
    baselines, lam, application = _kernel("spectral_baselines"), _b2b_spectrum(32), "RESIDUAL"
    if case == "application":
        application = "residual"
    elif case == "short_residual":
        lam = lam[:20]
    elif case == "short_market":
        lam, application = lam[:19], "MARKET"
    elif case == "matrix":
        lam = np.diag(lam)
    elif case == "nonfinite":
        lam[0] = math.inf
    elif case == "nonpositive":
        lam[-1], application = 0.0, "MARKET"
    else:
        lam[29], lam[30] = lam[30], lam[29]
    before, opened = lam.copy(), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        with pytest.raises(ValueError):
            baselines(lam, application)
    assert np.array_equal(lam, before) and not opened
    if case == "short_residual":
        assert baselines(lam, "MARKET") == _b2b_reference(lam, "MARKET")


def test_spectral_baselines_constant_non_dyadic_spectrum_keeps_every_eligible_axis(monkeypatch):
    baselines, lam, opened, outs = _kernel("spectral_baselines"), np.full(32, 0.1), [], {}
    lam.flags.writeable = False
    before, flags = lam.copy(), (lam.flags.writeable, lam.flags.c_contiguous, lam.flags.owndata)
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for application in B2B_UNIVERSES:
            outs[application] = baselines(lam, application)
    assert np.array_equal(lam, before) and (lam.flags.writeable, lam.flags.c_contiguous, lam.flags.owndata) == flags
    assert flags[0] is False and not opened
    k90 = pdb.cpv90(lam)
    for application, out in outs.items():
        eligible, rows = B2B_UNIVERSES[application], out["baselines"]
        assert set(out) == {"eligible", "baselines"} and out["eligible"] == eligible and len(eligible) == 20
        assert set(rows) == set(B2B_BASELINES) and rows["FULL_K"] == {"status": "RUNNABLE", "pcs": eligible}
        assert rows["FIXED_EIGENMEAN_PREFIX"] == {"status": "RUNNABLE", "pcs": eligible}
        assert rows["CPV90"] == {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90} and k90 > 20
    residual = {"status": "RUNNABLE", "pcs": B2B_UNIVERSES["RESIDUAL"][:pdb.cpv90(lam[1:21])]}
    assert outs["RESIDUAL"]["baselines"]["RESIDUAL_CPV90"] == residual
    assert outs["MARKET"]["baselines"]["RESIDUAL_CPV90"] == {"status": "UNSUPPORTED", "pcs": None}


B2B_TRACES = {"overflow_residual": (239, ("RESIDUAL",)), "overflow_market": (239, ("MARKET",)),
              "finite_control": (32, ("RESIDUAL", "MARKET"))}


@pytest.mark.parametrize("case", B2B_TRACES)
def test_spectral_baselines_refuse_an_overflowing_trace_before_the_received_cpv90(monkeypatch, case):
    baselines, received, (N, applications) = _kernel("spectral_baselines"), pdb.cpv90, B2B_TRACES[case]
    lam, overflow, opened, outs = np.full(N, np.finfo(np.float64).max / 64), N == 239, [], {}
    lam.flags.writeable = False
    data, flags = lam.tobytes(), (lam.flags.writeable, lam.flags.c_contiguous, lam.flags.owndata)
    with np.errstate(over="ignore"):
        full, parts = lam.sum(), [lam[e[0] - 1:e[-1]].sum() for e in B2B_UNIVERSES.values()]
    assert np.isfinite(lam).all() and np.isfinite(parts).all() and np.isfinite(full) != overflow

    def spy(*args, **kwargs):
        pytest.fail("the received pdb.cpv90 was called on an overflowing trace")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        if overflow:
            mp.setattr(pdb, "cpv90", spy)
        for application in applications:
            if overflow:
                with pytest.raises(ValueError):
                    baselines(lam, application)
            else:
                outs[application] = baselines(lam, application)
    assert pdb.cpv90 is received and lam.tobytes() == data and not opened and len(outs) == (0 if overflow else 2)
    assert (lam.flags.writeable, lam.flags.c_contiguous, lam.flags.owndata) == flags and flags[0] is False
    for application, out in outs.items():
        eligible, rows, k90 = B2B_UNIVERSES[application], out["baselines"], pdb.cpv90(lam)
        assert k90 == 29 and rows["CPV90"] == {"status": "OUTSIDE_UNIVERSE", "pcs": None, "k90": k90}
        assert rows["FIXED_EIGENMEAN_PREFIX"] == rows["FULL_K"] == {"status": "RUNNABLE", "pcs": eligible}
        residual = {"status": "UNSUPPORTED", "pcs": None}
        if application == "RESIDUAL":
            residual = {"status": "RUNNABLE", "pcs": eligible[:pdb.cpv90(lam[1:21])]}
        assert rows["RESIDUAL_CPV90"] == residual


class _B2cPoison:
    def _touched(self, *args, **kwargs):
        raise AssertionError("an unknown policy field value was read instead of a structural refusal")

    __bool__ = __len__ = __iter__ = __array__ = __float__ = __int__ = __index__ = _touched
    __eq__ = __ne__ = __hash__ = __repr__ = __str__ = __format__ = __getattr__ = _touched


B2C_REFUSALS = ("kind_unknown", "oracle_to_nonoracle", "online_to_oracle", "not_a_dict", "online_missing_window",
                "online_window_float", "online_cost_length", "online_order", "static_empty", "static_length",
                "static_nonbool", "static_nonfinite_y", "oracle_h_float", "oracle_h_bool", "oracle_h_zero",
                "oracle_q_negative", "oracle_q_shape")


def _b2c_same(policy, snapshot):
    return set(policy) == set(snapshot) and all(policy[key] is value for key, value in snapshot.items())


def _b2c_refusal(case):
    Y, cost = np.zeros((2, 3, 4)), np.array(_costs(4)["MIX"])
    q, mask = np.array([[0.0, 0.0, 3.0, 1.0], [0.5, 0.25, 0.0, 0.0]]), np.array([False, True, False, True])
    online, static = {"kind": "ONLINE", "window": 3, "cost": cost, "order": "INFO"}, {"kind": "STATIC", "mask": mask}
    truth = {"kind": "ORACLE", "H": 3, "cost": cost, "order": "PREFIX"}
    return {"kind_unknown": ("nonoracle_masks", Y, {"kind": "FIXED", "mask": mask}),
            "oracle_to_nonoracle": ("nonoracle_masks", Y, truth),
            "online_to_oracle": ("oracle_masks", q, online),
            "not_a_dict": ("nonoracle_masks", Y, tuple(static.items())),
            "online_missing_window": ("nonoracle_masks", Y, {k: v for k, v in online.items() if k != "window"}),
            "online_window_float": ("nonoracle_masks", Y, {**online, "window": 3.0}),
            "online_cost_length": ("nonoracle_masks", Y, {**online, "cost": cost[:3]}),
            "online_order": ("nonoracle_masks", Y, {**online, "order": "MIX"}),
            "static_empty": ("nonoracle_masks", Y, {**static, "mask": np.zeros(4, dtype=bool)}),
            "static_length": ("nonoracle_masks", Y, {**static, "mask": np.ones(5, dtype=bool)}),
            "static_nonbool": ("nonoracle_masks", Y, {**static, "mask": mask.astype(np.int64)}),
            "static_nonfinite_y": ("nonoracle_masks", np.full((2, 3, 4), np.nan), static),
            "oracle_h_float": ("oracle_masks", q, {**truth, "H": 3.0}),
            "oracle_h_bool": ("oracle_masks", q, {**truth, "H": True}),
            "oracle_h_zero": ("oracle_masks", q, {**truth, "H": 0}),
            "oracle_q_negative": ("oracle_masks", q - 0.25, truth),
            "oracle_q_shape": ("oracle_masks", q[None], truth)}[case]


@pytest.mark.parametrize("order", ["INFO", "PREFIX"])
def test_nonoracle_online_policy_delegates_unchanged_to_online_masks(monkeypatch, order):
    import inspect
    module, nonoracle, received = pio(), _kernel("nonoracle_masks"), _kernel("online_masks")
    Y, zero, seen = _paths(), np.zeros((2, 6, 4)), []
    Y.flags.writeable = False
    kept = Y.copy()

    def spy(*args, **kwargs):
        seen.append(inspect.signature(received).bind(*args, **kwargs).arguments)
        return received(*args, **kwargs)

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(module, "online_masks", spy)
        for window in (1, 3, 12):
            for values in _costs(4).values():
                cost = np.array(values)
                cost.flags.writeable = False
                policy = {"kind": "ONLINE", "window": window, "cost": cost, "order": order}
                snapshot, calls = dict(policy), len(seen)
                M, still, empty = nonoracle(Y, policy), nonoracle(zero, policy), nonoracle(Y[:0], policy)
                assert len(seen) == calls + 3 and _b2c_same(policy, snapshot) and not cost.flags.writeable
                for call, data in zip(seen[calls:], (Y, zero, Y[:0])):
                    assert set(call) == {"Y", "window", "cost", "order"} and np.array_equal(call["Y"], data)
                    assert call["window"] == window and np.array_equal(call["cost"], cost) and call["order"] == order
                assert M.dtype == bool and M.shape == Y.shape and empty.dtype == bool and empty.shape == (0, 10, 4)
                np.testing.assert_array_equal(M, received(Y, window, cost, order))
                np.testing.assert_array_equal(M, _ref_masks(Y, window, values, order))
                assert M[:, 0].tolist() == [AXIS0] * 4 and M[1].tolist() == [AXIS0] * 10
                assert still.tolist() == [[AXIS0] * 6] * 2 and np.array_equal(cost, values)
    assert np.array_equal(Y, kept) and not Y.flags.writeable


def test_nonoracle_static_policy_broadcasts_its_frozen_mask_without_selectors(monkeypatch):
    module, nonoracle = pio(), _kernel("nonoracle_masks")
    mask, unit, zero, altered = np.array([False, True, False, True]), np.array([True]), np.zeros((3, 6, 4)), _paths()
    frozen = (mask, unit, zero, altered)
    for array in frozen:
        array.flags.writeable = False
    kept, policy = [array.copy() for array in frozen], {"kind": "STATIC", "mask": mask}
    cases = [(zero, policy), (altered, policy), (altered[:0], policy), (np.zeros((2, 1, 4)), policy),
             (np.zeros((2, 3, 1)), {"kind": "STATIC", "mask": unit})]

    def forbidden(*args, **kwargs):
        pytest.fail("a selector was called for a frozen STATIC policy")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for name in ("online_masks", "best_sets"):
            mp.setattr(module, name, forbidden)
        outs = [nonoracle(Y, chosen) for Y, chosen in cases]
    assert not mask[0] and np.flatnonzero(mask).tolist() == [1, 3]
    assert _b2c_same(policy, {"kind": "STATIC", "mask": mask})
    for (Y, chosen), M in zip(cases, outs):
        assert M.dtype == bool and M.shape == Y.shape
        np.testing.assert_array_equal(M, np.broadcast_to(chosen["mask"], Y.shape))
    assert outs[1][:, 0].tolist() == [mask.tolist()] * 4 and outs[3].tolist() == [[mask.tolist()]] * 2
    assert all(np.array_equal(array, before) and not array.flags.writeable for array, before in zip(frozen, kept))


def test_oracle_policy_broadcasts_best_sets_constant_in_time_without_online_fallback(monkeypatch):
    module, oracle, best = pio(), _kernel("oracle_masks"), _kernel("best_sets")
    q = np.array([[0.0, 0.0, 3.0, 0.0, 1.0], [0.0] * 5, [0.375] * 4 + [0.0], [2.0, 1.0, 0.0, 0.5, 0.5]])
    q.flags.writeable = False
    kept, firsts = q.copy(), {}

    def forbidden(*args, **kwargs):
        pytest.fail("ONLINE selection or fallback inside the oracle masks")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(module, "online_masks", forbidden)
        for H in (1, np.int64(3)):
            for order in ("INFO", "PREFIX"):
                for name, values in _costs(5).items():
                    cost = np.array(values)
                    cost.flags.writeable = False
                    policy = {"kind": "ORACLE", "H": H, "cost": cost, "order": order}
                    snapshot = dict(policy)
                    M, empty = oracle(q, policy), oracle(q[:0], policy)
                    assert M.dtype == bool and M.shape == (4, int(H), 5) and empty.shape == (0, int(H), 5)
                    assert _b2c_same(policy, snapshot) and empty.dtype == bool
                    assert np.array_equal(cost, values) and not cost.flags.writeable
                    np.testing.assert_array_equal(M, np.broadcast_to(best(q, cost, order)[1][:, None], M.shape))
                    reference = _exhaustive if order == "INFO" else _prefix
                    for b in range(4):
                        subset = reference(q[b], values)[1]
                        assert all(np.flatnonzero(M[b, t]).tolist() == subset for t in range(int(H)))
                    firsts[order, name] = [np.flatnonzero(M[b, 0]).tolist() for b in range(4)]
    assert np.array_equal(q, kept) and not q.flags.writeable
    assert firsts["INFO", "MIX"][0] == [2, 4] and firsts["PREFIX", "MIX"][0] == [0, 1, 2, 3, 4]
    assert firsts["INFO", "MIX"][1] == firsts["PREFIX", "MIX"][1] == [0]


def test_mask_envelopes_are_thin_causal_and_refuse_unknown_fields_structurally():
    import inspect
    nonoracle, oracle = _kernel("nonoracle_masks"), _kernel("oracle_masks")
    assert list(inspect.signature(nonoracle).parameters) == ["Y", "policy"]
    assert list(inspect.signature(oracle).parameters) == ["q_true", "policy"]
    Y, values, poison = _paths(), _costs(4)["MIX"], _B2cPoison()
    cost = np.array(values)
    for order in ("INFO", "PREFIX"):
        policy = {"kind": "ONLINE", "window": 3, "cost": cost, "order": order}
        M = nonoracle(Y, policy)
        for t in (1, 4, 9):
            Z = Y.copy()
            Z[:, t - 1] += 8.0
            F = Z.copy()
            F[:, t:] *= -4.0
            N = nonoracle(Z, policy)
            np.testing.assert_array_equal(N[:, :t], M[:, :t])
            np.testing.assert_array_equal(nonoracle(F, policy)[:, :t], M[:, :t])
            np.testing.assert_array_equal(N, _ref_masks(Z, 3, values, order))
            assert (N[1, t] != M[1, t]).any()
    online = {"kind": "ONLINE", "window": 3, "cost": cost, "order": "INFO"}
    static = {"kind": "STATIC", "mask": np.array([False, True, False, True])}
    truth, q = {"kind": "ORACLE", "H": 2, "cost": cost, "order": "INFO"}, np.array([[0.0, 0.5, 0.0, 0.25]])
    probes = ((nonoracle, Y, online, "family"), (nonoracle, Y, online, "q_true"), (nonoracle, Y, online, "sigma0"),
              (nonoracle, Y, static, "delta"), (nonoracle, Y, static, "mu0"), (oracle, q, truth, "tau_star"),
              (oracle, q, truth, "meta"))
    for function, data, policy, field in probes:
        with pytest.raises(ValueError):
            function(data, {**policy, field: poison})


@pytest.mark.parametrize("case", B2C_REFUSALS)
def test_mask_envelopes_refuse_invalid_policies_and_inputs_without_effects(monkeypatch, case):
    name, data, policy = _b2c_refusal(case)
    function = _kernel(name)
    data.flags.writeable = False
    kept, snapshot = data.copy(), dict(policy) if isinstance(policy, dict) else None
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            function(data, policy)
    assert np.array_equal(data, kept, equal_nan=True) and not data.flags.writeable
    assert snapshot is None or _b2c_same(policy, snapshot)


B2D_FAMILIES = {"F0_ISOTROPIC_RESIDUAL": ("RESIDUAL", None), "F1_TAIL_RESIDUAL": ("RESIDUAL", [18, 19, 20, 21]),
                "F2_STRUCTURED_RESIDUAL": ("RESIDUAL", [3, 9, 17, 21]), "F_HEAD_RESIDUAL": ("RESIDUAL", [2, 3, 4, 5]),
                "F3_MARKET": ("MARKET", [1])}
B2D_REFUSALS = ("application_unknown", "family_unknown", "eligible_not_prefix", "eligible_too_long",
                "frame_not_square", "frame_nonfinite", "spectrum_nonpositive", "istar_bool", "istar_nonpositive",
                "f0_zero_row", "f0_nonfinite_row", "f0_wrong_width", "signs_zero", "signs_wrong_width", "signs_bool",
                "derived_overflow", "spectrum_unordered", "eligible_float", "eligible_bool")


def _b2d_frame(N):
    j, k = np.arange(N)[:, None], np.arange(N)[None, :]
    return np.sqrt(np.where(k == 0, 1.0, 2.0) / N) * np.cos(np.pi * (2 * j + 1) * k / (2 * N))


def _b2d_draws(family):
    if family == "F0_ISOTROPIC_RESIDUAL":
        alternating = [(-1) ** k * (k % 3 + 1.0) for k in range(20)]
        return np.array([np.arange(1.0, 21.0), alternating, [3.0] + [0.0] * 18 + [-4.0]])
    signs = np.array([[1, -1, 1, -1], [-1, -1, 1, 1], [1, 1, 1, 1]])
    return {"F3_MARKET": signs[:2, :1], "F2_STRUCTURED_RESIDUAL": signs.astype(np.float64)}.get(family, signs)


def _b2d_coordinates(support, E, row, I_star, N):
    b = [0.0] * N
    if support is None:
        norm = math.sqrt(math.fsum(x * x for x in row))
        for pc, x in zip(E, row):
            b[pc - 1] = math.sqrt(2.0 * I_star) * x / norm
    else:
        for pc, s in zip(support, row):
            b[pc - 1] = s * math.sqrt(2.0 * I_star / len(support))
    return b


def _b2d_refusal(case):
    V, lam, raw, big = _b2d_frame(24), _b2b_spectrum(24), np.ones((2, 20)), np.finfo(np.float64).max
    call = {"V": V, "lam": lam, "application": "RESIDUAL", "eligible": list(range(2, 22)), "family": "F_HEAD_RESIDUAL",
            "I_star": 0.25, "draws": np.array([[1, -1, 1, -1]])}
    f0 = {**call, "family": "F0_ISOTROPIC_RESIDUAL", "draws": raw}
    overflow = {"V": np.eye(21), "lam": np.array([big] + [1.0] * 20), "application": "MARKET",
                "eligible": list(range(1, 21)), "family": "F3_MARKET", "I_star": big, "draws": np.array([[1]])}
    market = {**call, "application": "MARKET", "eligible": list(range(1, 21)), "family": "F3_MARKET",
              "draws": np.array([[1]])}
    return {"application_unknown": {**call, "application": "residual"},
            "family_unknown": {**call, "family": "F4_ROTATION"},
            "eligible_not_prefix": {**call, "eligible": list(range(1, 21))},
            "eligible_too_long": {**call, "eligible": list(range(2, 23))},
            "frame_not_square": {**call, "V": V[:, :23]},
            "frame_nonfinite": {**call, "V": np.vstack([V[:23], np.full((1, 24), np.inf)])},
            "spectrum_nonpositive": {**call, "lam": np.append(lam[:23], 0.0)},
            "istar_bool": {**call, "I_star": True},
            "istar_nonpositive": {**call, "I_star": 0.0},
            "f0_zero_row": {**f0, "draws": np.vstack([raw[:1], np.zeros((1, 20))])},
            "f0_nonfinite_row": {**f0, "draws": np.vstack([raw[:1], np.full((1, 20), np.nan)])},
            "f0_wrong_width": {**f0, "draws": raw[:, :19]},
            "signs_zero": {**call, "draws": np.array([[1, 0, 1, -1]])},
            "signs_wrong_width": {**call, "draws": np.array([[1, -1, 1]])},
            "signs_bool": {**call, "draws": np.array([[True, True, True, True]])},
            "derived_overflow": overflow,
            "spectrum_unordered": {**call, "lam": lam[::-1]},
            "eligible_float": {**call, "eligible": [2.0, *range(3, 22)]},
            "eligible_bool": {**market, "eligible": [True, *range(2, 21)]}}[case]


@pytest.mark.parametrize("family", B2D_FAMILIES)
def test_population_drift_matches_literal_coordinates_and_exact_population_information(monkeypatch, family):
    drift = _kernel("population_drift")
    (application, support), V, lam, draws = B2D_FAMILIES[family], _b2d_frame(24), _b2b_spectrum(24), _b2d_draws(family)
    E, sigma0, cols = B2B_UNIVERSES[application], V @ np.diag(lam) @ V.T, np.array(B2B_UNIVERSES[application]) - 1
    np.testing.assert_allclose(V.T @ V, np.eye(24), rtol=0, atol=1e-13)
    assert not np.allclose(V, V.T) and np.allclose(V[:, 0], 24 ** -0.5) and (np.diff(lam) < 0).all()
    for array in (V, lam, draws):
        array.flags.writeable = False
    kept, eligible = [array.copy() for array in (V, lam, draws)], list(E)

    def forbidden(*args, **kwargs):
        pytest.fail("frame generation, fit or QR inside the population drift geometry")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for owner, name in ((pio(), "population_frame"), (pdb, "fit_basis"), (np.linalg, "qr")):
            mp.setattr(owner, name, forbidden)
        out = drift(V, lam, application, eligible, family, 0.25, draws)
        empty = drift(V, lam, application, eligible, family, 0.25, draws[:0])
    assert all(np.array_equal(a, k) and not a.flags.writeable for a, k in zip((V, lam, draws), kept)) and eligible == E
    assert set(out) == {"status", "support", "delta", "q"} and out["status"] == "SUPPORTED"
    assert out["support"] == (E if support is None else support) and out["delta"].dtype == out["q"].dtype == np.float64
    assert out["delta"].shape == (len(draws), 24) and out["q"].shape == (len(draws), 20)
    assert set(empty) == set(out) and empty["status"] == "SUPPORTED" and empty["support"] == out["support"]
    assert empty["delta"].dtype == empty["q"].dtype == np.float64
    assert empty["delta"].shape == (0, 24) and empty["q"].shape == (0, 20)
    for row, delta, q in zip(draws.tolist(), out["delta"], out["q"]):
        b = _b2d_coordinates(support, E, row, 0.25, 24)
        scalar = [math.fsum(V[n, k] * math.sqrt(lam[k]) * b[k] for k in range(24)) for n in range(24)]
        np.testing.assert_allclose(delta, scalar, rtol=1e-12, atol=1e-13)
        np.testing.assert_allclose(q, [b[pc - 1] ** 2 / 2.0 for pc in E], rtol=1e-12, atol=0)
        np.testing.assert_allclose((V.T @ delta) / np.sqrt(lam), b, rtol=0, atol=1e-12)
        np.testing.assert_allclose(pdb.q_plugin(V[:, cols].T @ delta, lam[cols]), q, rtol=1e-12, atol=1e-13)
        assert math.fsum(q) == pytest.approx(0.25, rel=1e-12)
        assert pdb.kl_mean(delta, sigma0) == pytest.approx(0.25, rel=1e-12)


def test_population_drift_unsupported_status_never_restricts_or_remaps_a_support(monkeypatch):
    import inspect
    drift = _kernel("population_drift")
    names = ["V", "lam", "application", "eligible", "family", "I_star", "draws"]
    assert list(inspect.signature(drift).parameters) == names
    V, lam, signs, raw = _b2d_frame(24), _b2b_spectrum(24), np.array([[1, -1, 1, -1]]), np.ones((1, 20))
    residual, market, short = B2B_UNIVERSES["RESIDUAL"], B2B_UNIVERSES["MARKET"], list(range(2, 20))
    cases = [("MARKET", market, "F0_ISOTROPIC_RESIDUAL", raw), ("MARKET", market, "F1_TAIL_RESIDUAL", signs),
             ("MARKET", market, "F2_STRUCTURED_RESIDUAL", signs), ("MARKET", market, "F_HEAD_RESIDUAL", signs),
             ("RESIDUAL", residual, "F3_MARKET", signs[:, :1]), ("RESIDUAL", short, "F2_STRUCTURED_RESIDUAL", signs),
             ("RESIDUAL", short, "F1_TAIL_RESIDUAL", signs)]
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        outs = [drift(V, lam, app, elig, fam, 0.25, data) for app, elig, fam, data in cases]
        head = drift(V, lam, "RESIDUAL", short, "F_HEAD_RESIDUAL", 0.25, signs)
    assert outs == [{"status": "UNSUPPORTED", "support": None, "delta": None, "q": None}] * len(cases)
    assert head["status"] == "SUPPORTED" and head["support"] == [2, 3, 4, 5] and head["delta"].shape == (1, 24)
    assert head["q"].shape == (1, 18) and not head["q"][0, 4:].any()
    np.testing.assert_allclose(head["q"][0, :4], [0.0625] * 4, rtol=1e-12, atol=0)


def test_population_drift_head_sign_profiles_and_golden_oracle_dimensions(monkeypatch):
    drift, best = _kernel("population_drift"), _kernel("best_sets")
    V, lam, E, cost = _b2d_frame(24), _b2b_spectrum(24), B2B_UNIVERSES["RESIDUAL"], np.array(_costs(20)["MIX"])
    sigma0, profiles = V @ np.diag(lam) @ V.T, np.array(list(itertools.product((-1, 1), repeat=4)))
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        head = drift(V, lam, "RESIDUAL", E, "F_HEAD_RESIDUAL", 0.25, profiles)
        tails = {family: drift(V, lam, "RESIDUAL", E, family, 0.25, profiles[:3])
                 for family in ("F1_TAIL_RESIDUAL", "F2_STRUCTURED_RESIDUAL")}
    assert profiles.shape == (16, 4) and (profiles[::-1] == -profiles).all() and head["support"] == [2, 3, 4, 5]
    np.testing.assert_allclose(head["delta"][::-1], -head["delta"], rtol=0, atol=1e-14)
    assert all(pdb.kl_mean(delta, sigma0) == pytest.approx(0.25, rel=1e-12) for delta in head["delta"])
    golden = {"F_HEAD_RESIDUAL": ([0, 1, 2, 3], 4), "F1_TAIL_RESIDUAL": ([16, 17, 18, 19], 20),
              "F2_STRUCTURED_RESIDUAL": ([1, 7, 15, 19], 20)}
    for family, out in (("F_HEAD_RESIDUAL", head), *tails.items()):
        (axes, d_prefix), rows = golden[family], len(out["q"])
        literal = [0.0625 if k in axes else 0.0 for k in range(20)]
        np.testing.assert_allclose(out["q"], [literal] * rows, rtol=1e-12, atol=0)
        assert _greedy(literal, list(cost)) == (4, axes) and _prefix(literal, list(cost))[0] == d_prefix
        (d_info, m_info), (d_pre, m_pre) = best(out["q"], cost, "INFO"), best(out["q"], cost, "PREFIX")
        assert d_info.tolist() == [4] * rows and d_pre.tolist() == [d_prefix] * rows
        assert all(np.flatnonzero(m).tolist() == axes for m in m_info)
        assert all(np.flatnonzero(m).tolist() == list(range(d_prefix)) for m in m_pre)


def test_population_drift_isotropic_direction_is_the_normalized_supplied_raw_vector(monkeypatch):
    drift, family = _kernel("population_drift"), "F0_ISOTROPIC_RESIDUAL"
    V, lam, E, raw = _b2d_frame(24), _b2b_spectrum(24), B2B_UNIVERSES["RESIDUAL"], _b2d_draws(family)
    short, sigma0 = list(range(2, 20)), V @ np.diag(lam) @ V.T
    raw.flags.writeable = False
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        out = drift(V, lam, "RESIDUAL", E, family, 0.25, raw)
        scaled = drift(V, lam, "RESIDUAL", E, family, 0.25, raw * 2.5)
        returned, refused = [scaled], []
        for scale in (1e-200, 1e200):
            try:
                result = drift(V, lam, "RESIDUAL", E, family, 0.25, raw * scale)
            except ValueError:
                refused.append(scale)
            else:
                returned.append(result)
        shorter = drift(V, lam, "RESIDUAL", short, family, 0.25, raw[:, :18])
    assert np.array_equal(raw, _b2d_draws(family)) and not raw.flags.writeable and len(returned) + len(refused) == 3
    assert isinstance(out, dict) and out["status"] == "SUPPORTED" and out["support"] == E
    np.testing.assert_allclose(out["q"][2], [0.09] + [0.0] * 18 + [0.16], rtol=1e-12, atol=0)
    assert all(abs(V[:, 0] @ delta) <= 1e-12 for delta in out["delta"])
    for other in returned:
        assert isinstance(other, dict) and other["status"] == "SUPPORTED" and other["support"] == E
        np.testing.assert_allclose(other["delta"], out["delta"], rtol=1e-12, atol=1e-13)
        np.testing.assert_allclose(other["q"], out["q"], rtol=1e-12, atol=1e-15)
    assert isinstance(shorter, dict) and shorter["status"] == "SUPPORTED" and shorter["support"] == short
    assert shorter["delta"].shape == (3, 24) and shorter["q"].shape == (3, 18)
    for row, delta, q in zip(raw[:, :18].tolist(), shorter["delta"], shorter["q"]):
        b = _b2d_coordinates(None, short, row, 0.25, 24)
        np.testing.assert_allclose(q, [b[pc - 1] ** 2 / 2.0 for pc in short], rtol=1e-12, atol=0)
        assert math.fsum(q) == pytest.approx(0.25, rel=1e-12)
        assert pdb.kl_mean(delta, sigma0) == pytest.approx(0.25, rel=1e-12)


@pytest.mark.parametrize("case", B2D_REFUSALS)
def test_population_drift_refuses_malformed_inputs_without_effects(monkeypatch, case):
    call = _b2d_refusal(case)
    drift = _kernel("population_drift")
    arrays = {key: value for key, value in call.items() if isinstance(value, np.ndarray)}
    for value in arrays.values():
        value.flags.writeable = False
    kept = {key: value.tobytes() for key, value in arrays.items()}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            drift(**call)
    assert all(value.tobytes() == kept[key] and not value.flags.writeable for key, value in arrays.items())


B2D_UNDERFLOW = ("head_q_zero", "isotropic_q_zero", "market_delta_zero", "market_subnormal_control")


def _b2d_underflow(case):
    eye, ones, residual, market = np.eye(24), np.ones(24), list(range(2, 22)), list(range(1, 21))
    return {"head_q_zero": (eye, ones, "RESIDUAL", residual, "F_HEAD_RESIDUAL", np.array([[1, -1, 1, -1]])),
            "isotropic_q_zero": (eye, ones, "RESIDUAL", residual, "F0_ISOTROPIC_RESIDUAL", np.ones((1, 20))),
            "market_delta_zero": (_b2d_frame(24), np.full(24, 2.0 ** -1074), "MARKET", market, "F3_MARKET",
                                  np.array([[1]])),
            "market_subnormal_control": (eye, ones, "MARKET", market, "F3_MARKET", np.array([[1]]))}[case]


@pytest.mark.parametrize("case", B2D_UNDERFLOW)
def test_population_drift_refuses_underflow_but_keeps_representable_subnormals(monkeypatch, case):
    drift, a = _kernel("population_drift"), 2.0 ** -1074
    V, lam, application, eligible, family, draws = _b2d_underflow(case)
    root, support = math.sqrt(2.0 * a), {"F_HEAD_RESIDUAL": [2, 3, 4, 5], "F3_MARKET": [1]}.get(family, eligible)
    np.testing.assert_allclose(V.T @ V, np.eye(24), rtol=0, atol=1e-13)
    assert a > 0.0 and (lam > 0).all() and (np.diff(lam) <= 0).all()
    if case == "head_q_zero":
        assert 2.0 * a / 4 == 0.0
    elif case == "isotropic_q_zero":
        assert root / math.sqrt(20.0) > 0.0 and (root / math.sqrt(20.0)) ** 2 / 2.0 == 0.0
    elif case == "market_delta_zero":
        weighted = root * math.sqrt(a)
        assert weighted == a and root * root / 2.0 == a and all(weighted * v == 0.0 for v in V[:, 0].tolist())
    else:
        assert root > 0.0 and root * root / 2.0 == a
    for array in (V, lam, draws):
        array.flags.writeable = False
    kept, listed = [array.tobytes() for array in (V, lam, draws)], list(eligible)

    def forbidden(*args, **kwargs):
        pytest.fail("frame generation, fit or QR inside the population drift geometry")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for owner, name in ((pio(), "population_frame"), (pdb, "fit_basis"), (np.linalg, "qr")):
            mp.setattr(owner, name, forbidden)
        empty = drift(V, lam, application, eligible, family, a, draws[:0])
        try:
            out, refused = drift(V, lam, application, eligible, family, a, draws), False
        except ValueError:
            out, refused = None, True
    assert [array.tobytes() for array in (V, lam, draws)] == kept and eligible == listed
    assert not (V.flags.writeable or lam.flags.writeable or draws.flags.writeable)
    assert isinstance(empty, dict) and set(empty) == {"status", "support", "delta", "q"}
    assert empty["status"] == "SUPPORTED" and empty["support"] == support
    assert empty["delta"].dtype == empty["q"].dtype == np.float64
    assert empty["delta"].shape == (0, 24) and empty["q"].shape == (0, 20)
    assert refused == (case != "market_subnormal_control")
    if not refused:
        assert isinstance(out, dict) and out["status"] == "SUPPORTED" and out["support"] == [1]
        assert out["delta"].dtype == out["q"].dtype == np.float64
        assert out["delta"].shape == (1, 24) and out["q"].shape == (1, 20) and np.isfinite(out["delta"]).all()
        assert np.count_nonzero(out["delta"]) == 1 and out["delta"][0, 0] > 0.0
        assert np.count_nonzero(out["q"]) == 1 and out["q"][0, 0] == a


B2E_FIELDS = ("A", "c", "C0", "var0", "beta", "q", "I_joint", "oracle_basis")
B2E_DELTAS = ((0.0, 2.0, 1.0, 0.0), (0.0, 0.0, 1.0, 0.0), (3.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 0.0))
B2E_EXPECTED = (
    {"A": [[0.0, 0.64, 0.24, 0.0], [0.0, -1.5, 1.0, 0.0]], "c": [0.28, 0.125], "C0": [[0.4672, -0.72], [-0.72, 3.25]],
     "projection": [[2.2, -0.4], [0.6, 0.8], [0.0, 0.0], [0.0, 0.0]],
     "beta": [[0.88, -0.5], [0.24, 1.0], [0.0, 0.0], [0.0, 0.0]],
     "q": [[0.3872, 0.125], [0.0288, 0.5], [0.0, 0.0], [0.0, 0.0]]},
    {"A": [[0.0, 1.2, 0.8, 0.0], [0.0, -3.2, 1.2, 0.0]], "c": [-0.3, 0.8], "C0": [[2.08, -2.88], [-2.88, 11.68]],
     "projection": [[2.0, -1.0], [0.8, 0.6], [0.0, 0.0], [0.0, 0.0]],
     "beta": [[2.0, -2.0], [0.8, 1.2], [0.0, 0.0], [0.0, 0.0]],
     "q": [[2.0, 2.0], [0.32, 0.72], [0.0, 0.0], [0.0, 0.0]]})
B2E_REFUSALS = ("frame_not_dict", "frame_unknown_field", "fit_missing_mean", "fit_size_mismatch", "basis_not_square",
                "basis_complex", "spectrum_nonpositive", "spectrum_increasing", "spectrum_overflow_after_cast",
                "mean_wrong_length", "deltas_nan", "deltas_wrong_width", "eligible_float", "eligible_bool",
                "eligible_gap", "eligible_start_three", "eligible_beyond_n", "eligible_too_long", "arm_unknown",
                "exact_other_basis", "exact_other_spectrum", "exact_other_mean", "derived_overflow")


def _b2e_exact():
    mean = np.array([(-1.0) ** n * (n % 5) / 4.0 for n in range(24)])
    return {"V": _b2d_frame(24), "lam": _b2b_spectrum(24), "mean": mean}


def _b2e_rotation(cosine, sine):
    rotation = np.eye(4)
    rotation[1:3, 1:3] = [[cosine, -sine], [sine, cosine]]
    return rotation


def _b2e_fitted():
    frame = {"V": np.eye(4), "lam": np.array([16.0, 4.0, 1.0, 0.25]), "mean": np.array([1.0, 2.0, -1.0, 0.5])}
    fits = ({"V": _b2e_rotation(0.8, 0.6), "lam": np.array([12.0, 6.25, 0.64, 0.5]),
             "mean": np.array([1.0, 1.5, -1.5, 0.5])},
            {"V": _b2e_rotation(0.6, 0.8), "lam": np.array([16.0, 1.0, 0.25, 0.0625]),
             "mean": np.array([1.0, 2.5, -1.0, 0.5])})
    return frame, fits, [2, 3], np.array(B2E_DELTAS)


def _b2e_reference(frame, fit, E, deltas):
    V, lam, mean, U, lam_hat, mean_hat = (record[key] for record in (frame, fit) for key in ("V", "lam", "mean"))
    N, K, cols = len(lam), len(E), [k - 1 for k in E]
    W = [[U[n, j] / math.sqrt(lam_hat[j]) for j in cols] for n in range(N)]
    A = [[math.fsum(W[m][i] * V[m, n] * math.sqrt(lam[n]) for m in range(N)) for n in range(N)] for i in range(K)]
    proj = [[math.fsum(row[n] * U[n, j] for n in range(N)) for j in cols] for row in deltas.tolist()]
    return {"A": A, "C0": [[math.fsum(x * y for x, y in zip(a, b)) for b in A] for a in A],
            "c": [math.fsum((mean[n] - mean_hat[n]) * W[n][i] for n in range(N)) for i in range(K)],
            "projection": proj, "beta": [[p / math.sqrt(lam_hat[j]) for p, j in zip(row, cols)] for row in proj],
            "q": [[p * p / (2.0 * lam_hat[j]) for p, j in zip(row, cols)] for row in proj]}


def _b2e_refusal(case):
    frame, fits, E, deltas = _b2e_fitted()
    fit, same, wide = fits[0], {key: value.copy() for key, value in frame.items()}, _b2e_exact()
    call = {"frame": frame, "fit": fit, "eligible": E, "deltas": deltas, "arm": "FITTED_LW_GAUSSIAN"}
    exact = {**call, "fit": same, "arm": "EXACT"}
    with np.errstate(over="ignore"):
        huge = np.array([np.longdouble(np.finfo(np.float64).max) * 4, 4.0, 1.0, 0.25], dtype=np.longdouble)
    larger = {"V": np.eye(5), "lam": np.array([16.0, 4.0, 1.0, 0.5, 0.25]), "mean": np.zeros(5)}
    return {"frame_not_dict": {**call, "frame": list(frame.items())},
            "frame_unknown_field": {**call, "frame": {**frame, "sigma0": _B2cPoison()}},
            "fit_missing_mean": {**call, "fit": {"V": fit["V"], "lam": fit["lam"]}},
            "fit_size_mismatch": {**call, "fit": larger},
            "basis_not_square": {**call, "fit": {**fit, "V": fit["V"][:, :3]}},
            "basis_complex": {**call, "frame": {**frame, "V": frame["V"] + 0j}},
            "spectrum_nonpositive": {**call, "fit": {**fit, "lam": np.array([12.0, 6.25, 0.64, 0.0])}},
            "spectrum_increasing": {**call, "frame": {**frame, "lam": frame["lam"][::-1]}},
            "spectrum_overflow_after_cast": {**call, "frame": {**frame, "lam": huge}},
            "mean_wrong_length": {**call, "fit": {**fit, "mean": fit["mean"][:3]}},
            "deltas_nan": {**call, "deltas": np.vstack([deltas[:1], np.full((1, 4), np.nan)])},
            "deltas_wrong_width": {**call, "deltas": deltas[:, :3]},
            "eligible_float": {**call, "eligible": [2.0, 3]},
            "eligible_bool": {**call, "eligible": [True, 2]},
            "eligible_gap": {**call, "eligible": [2, 4]},
            "eligible_start_three": {**call, "eligible": [3, 4]},
            "eligible_beyond_n": {**call, "eligible": [2, 3, 4, 5]},
            "eligible_too_long": {"frame": wide, "fit": {key: value.copy() for key, value in wide.items()},
                                  "eligible": list(range(1, 22)), "deltas": np.ones((1, 24)), "arm": "EXACT"},
            "arm_unknown": {**call, "arm": "fitted_lw_gaussian"},
            "exact_other_basis": {**exact, "fit": {**same, "V": fit["V"]}},
            "exact_other_spectrum": {**exact, "fit": {**same, "lam": fit["lam"]}},
            "exact_other_mean": {**exact, "fit": {**same, "mean": fit["mean"]}},
            "derived_overflow": {**call, "fit": {**fits[1], "lam": np.array([16.0, 1.0, 5e-324, 5e-324])}}}[case]


@pytest.mark.parametrize("application", ["RESIDUAL", "MARKET"])
def test_projection_diagnostics_exact_arm_is_additive_and_matches_scalar_references(monkeypatch, application):
    module, diagnostics = pio(), _kernel("projection_diagnostics")
    frame, E, opened = _b2e_exact(), list(B2B_UNIVERSES[application]), []
    fit, K = {key: value.copy() for key, value in frame.items()}, len(E)
    alternating = [(-1.0) ** n * (n % 3 + 1) for n in range(24)]
    deltas = np.array([np.arange(1.0, 25.0) / 8.0, alternating, np.zeros(24)])
    arrays = [*frame.values(), *fit.values(), deltas]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots, listed = [array.tobytes() for array in arrays], (dict(frame), dict(fit)), list(E)
    np.testing.assert_allclose(frame["V"].T @ frame["V"], np.eye(24), rtol=0, atol=1e-13)
    assert (frame["lam"] > 0).all() and (np.diff(frame["lam"]) < 0).all() and frame["mean"].any()

    def forbidden(*args, **kwargs):
        pytest.fail("frame generation, drift synthesis, fit or decomposition inside the projection diagnostics")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for owner, name in ((module, "population_frame"), (module, "population_drift"), (pdb, "fit_basis"),
                            (np.linalg, "qr"), (np.linalg, "eig"), (np.linalg, "eigh"), (np.linalg, "eigvalsh"),
                            (np.linalg, "svd")):
            mp.setattr(owner, name, forbidden)
        out = diagnostics(frame, fit, E, deltas, "EXACT")
        empty = diagnostics(frame, fit, E, deltas[:0], "EXACT")
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2c_same(frame, snapshots[0]) and _b2c_same(fit, snapshots[1]) and E == listed and not opened
    assert set(out) == set(B2E_FIELDS) and out["oracle_basis"] == "EXACT_ADDITIVE_KL"
    assert out["oracle_basis"] in _kernel("INFO_BASES")
    shapes = {"A": (K, 24), "c": (K,), "C0": (K, K), "var0": (K,), "beta": (3, K), "q": (3, K), "I_joint": (3,)}
    assert all(out[key].dtype == np.float64 and out[key].shape == shape for key, shape in shapes.items())
    ref, selection = _b2e_reference(frame, fit, E, deltas), np.zeros((K, 24))
    selection[np.arange(K), np.array(E) - 1] = 1.0
    for key, expected, atol in (("A", ref["A"], 1e-13), ("A", selection, 1e-12), ("C0", ref["C0"], 1e-13),
                                ("C0", np.eye(K), 1e-12)):
        np.testing.assert_allclose(out[key], expected, rtol=0, atol=atol)
    assert (out["c"] == 0.0).all() and np.array_equal(out["var0"], np.diag(out["C0"]))
    np.testing.assert_allclose(out["beta"], ref["beta"], rtol=1e-12, atol=1e-13)
    np.testing.assert_allclose(out["q"], ref["q"], rtol=1e-12, atol=1e-13)
    for beta, q, joint in zip(ref["beta"], ref["q"], out["I_joint"].tolist()):
        assert joint == pytest.approx(math.fsum(q), rel=1e-12, abs=1e-15)
        assert joint == pytest.approx(pdb.kl_mean(np.array(beta), np.array(ref["C0"])), rel=1e-12, abs=1e-15)
    assert out["I_joint"][0] > 0.0 and out["I_joint"][2] == 0.0 and not out["q"][2].any() and not out["beta"][2].any()
    assert set(empty) == set(out) and empty["oracle_basis"] == out["oracle_basis"]
    assert all(np.array_equal(empty[key], out[key]) for key in ("A", "c", "C0", "var0"))
    assert empty["beta"].shape == empty["q"].shape == (0, K) and empty["I_joint"].shape == (0,)
    assert all(empty[key].dtype == np.float64 for key in ("beta", "q", "I_joint"))


def test_projection_diagnostics_fitted_arm_labels_a_diagonal_surrogate_distinct_from_the_joint(monkeypatch):
    import inspect
    diagnostics, real_q, real_kl = _kernel("projection_diagnostics"), pdb.q_plugin, pdb.kl_mean
    assert list(inspect.signature(diagnostics).parameters) == ["frame", "fit", "eligible", "deltas", "arm"]
    frame, fits, E, deltas = _b2e_fitted()
    population = [real_kl(row, np.diag(frame["lam"])) for row in deltas]
    assert population == pytest.approx([1.0, 0.5, 2.28125, 0.0], rel=1e-12, abs=1e-15)
    for fit, expected in zip(fits, B2E_EXPECTED):
        A, C0, ref = np.array(expected["A"]), np.array(expected["C0"]), _b2e_reference(frame, fit, E, deltas)
        np.testing.assert_allclose(A @ A.T, C0, rtol=1e-12, atol=1e-15)
        joint = [real_kl(np.array(beta), C0) for beta in expected["beta"]]
        assert joint == pytest.approx([1.0, 0.5, 0.0, 0.0], rel=1e-12, abs=1e-15)
        for key in ("A", "C0", "c", "projection", "beta", "q"):
            np.testing.assert_allclose(ref[key], expected[key], rtol=1e-12, atol=1e-15)
    arrays = [*frame.values(), *(array for fit in fits for array in fit.values()), deltas]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots = [array.tobytes() for array in arrays], [dict(record) for record in (frame, *fits)]
    q_calls, kl_calls = [], []

    def q_spy(beta, lam):
        q_calls.append((np.array(beta, copy=True), np.array(lam, copy=True)))
        return real_q(beta, lam)

    def kl_spy(mu, C):
        kl_calls.append((np.array(mu, copy=True), np.array(C, copy=True)))
        return real_kl(mu, C)

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(pdb, "q_plugin", q_spy)
        mp.setattr(pdb, "kl_mean", kl_spy)
        outs = [diagnostics(frame, fit, E, deltas, "FITTED_LW_GAUSSIAN") for fit in fits]
    empty = diagnostics(frame, fits[0], E, deltas[:0], "FITTED_LW_GAUSSIAN")
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert all(_b2c_same(record, snapshot) for record, snapshot in zip((frame, *fits), snapshots))
    assert E == [2, 3] and len(q_calls) == 2 and len(kl_calls) == 8
    for i, (fit, out, expected) in enumerate(zip(fits, outs, B2E_EXPECTED)):
        assert set(out) == set(B2E_FIELDS) and out["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE"
        assert out["oracle_basis"] in _kernel("INFO_BASES")
        assert not any("OPTIM" in text for text in (*out, out["oracle_basis"]))
        for key in ("A", "c", "C0", "beta", "q"):
            np.testing.assert_allclose(out[key], expected[key], rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(out["I_joint"], [1.0, 0.5, 0.0, 0.0], rtol=1e-12, atol=1e-15)
        assert np.array_equal(out["var0"], np.diag(out["C0"])) and (np.abs(out["var0"] - 1.0) > 0.5).all()
        assert abs(out["C0"][0, 1]) > 0.5 and not out["I_joint"][2:].any()
        assert not out["beta"][2:].any() and not out["q"][2:].any()
        projected, scales = q_calls[i]
        np.testing.assert_allclose(projected, expected["projection"], rtol=1e-12, atol=1e-15)
        assert np.array_equal(scales, fit["lam"][1:3])
        assert all(np.array_equal(mu, row) and np.array_equal(C, out["C0"])
                   for (mu, C), row in zip(kl_calls[4 * i:4 * i + 4], out["beta"]))
        surrogate = out["q"].sum(axis=1)
        assert abs(surrogate[0] - out["I_joint"][0]) > 0.4 and abs(surrogate[1] - out["I_joint"][1]) > 0.02
    assert outs[0]["q"][0].sum() < outs[0]["I_joint"][0] and outs[0]["q"][1].sum() > outs[0]["I_joint"][1]
    assert not np.allclose(outs[0]["beta"][:2], outs[1]["beta"][:2])
    assert not np.allclose(outs[0]["q"][:2], outs[1]["q"][:2])
    np.testing.assert_allclose(outs[0]["I_joint"][:2], population[:2], rtol=1e-12, atol=0)
    assert outs[0]["I_joint"][2] == 0.0 < population[2]
    assert set(empty) == set(B2E_FIELDS) and empty["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE"
    assert all(np.array_equal(empty[key], outs[0][key]) for key in ("A", "c", "C0", "var0"))
    assert empty["beta"].shape == empty["q"].shape == (0, 2) and empty["I_joint"].shape == (0,)
    assert all(empty[key].dtype == np.float64 for key in ("beta", "q", "I_joint"))


def test_projection_offsets_feed_only_the_offline_null_bias_and_never_an_online_policy():
    diagnostics, bias = _kernel("projection_diagnostics"), _kernel("null_score_bias")
    nonoracle, poison = _kernel("nonoracle_masks"), _B2cPoison()
    frame, fits, E, deltas = _b2e_fitted()
    Y, policy = _paths(), {"kind": "ONLINE", "window": 3, "cost": np.array(_costs(4)["MIX"]), "order": "INFO"}
    before = nonoracle(Y, policy)
    exact = diagnostics(frame, {key: value.copy() for key, value in frame.items()}, E, deltas, "EXACT")
    fitted = diagnostics(frame, fits[0], E, deltas, "FITTED_LW_GAUSSIAN")
    assert np.array_equal(exact["A"], [[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]) and not exact["c"].any()
    assert np.array_equal(exact["C0"], np.eye(2)) and np.array_equal(exact["var0"], [1.0, 1.0])
    assert exact["oracle_basis"] == "EXACT_ADDITIVE_KL" and fitted["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE"
    np.testing.assert_array_equal(exact["I_joint"], [1.0, 0.5, 0.0, 0.0])
    np.testing.assert_allclose(exact["q"].sum(axis=1), exact["I_joint"], rtol=1e-12, atol=0)
    for m in (1, 32, 128):
        expected = [0.5 * (c * c + (v - 1.0) / m) for c, v in ((0.28, 0.4672), (0.125, 3.25))]
        centering, variance = bias(fitted["c"], np.ones(2), m), bias(np.zeros(2), fitted["var0"], m)
        np.testing.assert_allclose(bias(fitted["c"], fitted["var0"], m), expected, rtol=1e-12, atol=0)
        np.testing.assert_allclose(centering + variance, expected, rtol=1e-12, atol=0)
        np.testing.assert_allclose(centering, [0.5 * 0.28 ** 2, 0.5 * 0.125 ** 2], rtol=1e-12, atol=0)
        assert variance[0] < 0.0 < variance[1] and np.array_equal(bias(exact["c"], exact["var0"], m), [0.0, 0.0])
    np.testing.assert_array_equal(nonoracle(Y, policy), before)
    for field in ("c", "var0", "C0", "beta", "I_joint"):
        with pytest.raises(ValueError):
            nonoracle(Y, {**policy, field: poison})


@pytest.mark.parametrize("case", B2E_REFUSALS)
def test_projection_diagnostics_refuse_malformed_inputs_without_effects(monkeypatch, case):
    call = _b2e_refusal(case)
    diagnostics = _kernel("projection_diagnostics")
    records = [record for record in (call["frame"], call["fit"]) if isinstance(record, dict)]
    arrays = [value for record in records for value in record.values() if isinstance(value, np.ndarray)]
    arrays.append(call["deltas"])
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots = [array.tobytes() for array in arrays], [dict(record) for record in records]
    listed = list(call["eligible"])
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            diagnostics(**call)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert all(_b2c_same(record, snapshot) for record, snapshot in zip(records, snapshots))
    assert call["eligible"] == listed


B2E_UNDERFLOW = {"beta_a_false_zero_joint": (1.0, 1.0, 0.0), "beta_2a_positive_joint": (2.0, 4.0, 4.0),
                 "beta_zero_null_joint": (0.0, 0.0, 0.0)}


@pytest.mark.parametrize("case", B2E_UNDERFLOW)
def test_projection_diagnostics_refuses_a_false_zero_joint_but_keeps_subnormal_and_null_rows(monkeypatch, case):
    diagnostics, a = _kernel("projection_diagnostics"), 2.0 ** -1074
    (scale, exact, helper), root = B2E_UNDERFLOW[case], math.sqrt(a)
    frame = {"V": np.eye(2), "lam": np.array([a, a]), "mean": np.zeros(2)}
    fit = {"V": np.eye(2), "lam": np.array([1.0, 1.0]), "mean": np.zeros(2)}
    eligible, deltas, A, C0 = [1, 2], np.array([[scale * a, scale * a]]), np.diag([root, root]), a * np.eye(2)
    assert a > 0.0 and root == 2.0 ** -537 and root * root == a and 0.5 * (scale * a) * (scale * a) == 0.0
    assert 0.5 * math.fsum(b * (b / a) for b in deltas[0].tolist()) == exact * a
    assert np.array_equal(np.linalg.solve(C0, deltas[0]), [scale, scale])
    assert pdb.kl_mean(deltas[0], C0) == helper * a
    arrays = [*frame.values(), *fit.values(), deltas]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots, listed = [array.tobytes() for array in arrays], (dict(frame), dict(fit)), list(eligible)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        empty = diagnostics(frame, fit, eligible, deltas[:0], "FITTED_LW_GAUSSIAN")
        try:
            out, refused = diagnostics(frame, fit, eligible, deltas, "FITTED_LW_GAUSSIAN"), False
        except ValueError:
            out, refused = None, True
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2c_same(frame, snapshots[0]) and _b2c_same(fit, snapshots[1]) and eligible == listed
    assert set(empty) == set(B2E_FIELDS) and empty["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE"
    assert np.array_equal(empty["A"], A) and np.array_equal(empty["C0"], C0) and not empty["c"].any()
    assert np.array_equal(empty["var0"], [a, a])
    assert all(np.isfinite(empty[key]).all() for key in ("A", "c", "C0", "var0"))
    assert empty["beta"].shape == empty["q"].shape == (0, 2) and empty["I_joint"].shape == (0,)
    assert all(empty[key].dtype == np.float64 for key in ("beta", "q", "I_joint"))
    assert refused == (case == "beta_a_false_zero_joint")
    if not refused:
        assert isinstance(out, dict) and set(out) == set(B2E_FIELDS)
        assert out["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE"
        assert all(np.array_equal(out[key], empty[key]) for key in ("A", "c", "C0", "var0"))
        assert out["beta"].tolist() == [[scale * a, scale * a]] and out["q"].tolist() == [[0.0, 0.0]]
        assert out["I_joint"].dtype == np.float64 and out["I_joint"].tolist() == [exact * a]


B2F_FIELDS = ("support", "signs", "delta", "I_E", "I_P4", "f_E", "f_pop", "summary", "all_I_E_positive")
B2F_FITTED = {"misaligned": (6, [2, 3, 4, 5, 6], [0, 5, 2, 3, 4, 1], (1.0, 0.75, 0.75, 0.75)),
              "leakage": (7, [2, 3, 4, 5, 6], [0, 6, 2, 3, 4, 5, 1], (0.75, 0.75, 1.0, 0.75)),
              "true_zero": (8, [2, 3, 4, 5], [1, 0, 5, 6, 7, 2, 3, 4], (0.0, 0.0, None, 0.0)),
              "head_outside_p4": (9, [2, 3, 4, 5, 6], [2, 0, 5, 6, 7, 1, 3, 4, 8], (0.25, 0.0, 0.0, 0.0)),
              "rotation": (6, [2, 3, 4, 5, 6], None, (1.0, 12 / 13, 12 / 13, 12 / 13))}
B2F_REFUSALS = ("frame_not_dict", "fit_unknown_field", "fit_missing_mean", "fit_size_mismatch", "basis_complex",
                "spectrum_increasing", "universe_float", "universe_numpy_int", "universe_bool", "universe_gap",
                "universe_market", "universe_too_short", "universe_too_long", "universe_beyond_n",
                "istar_nonpositive", "istar_bool", "istar_nonfinite", "derived_overflow")


def _b2f_records(N, perm):
    frame = {"V": np.eye(N), "lam": 4.0 ** (4 - np.arange(N)), "mean": np.arange(N) * 0.5 - 1.0}
    V = np.eye(N) if perm is None else np.eye(N)[:, perm]
    if perm is None:
        V[2:4, 2:4], V[4:6, 4:6] = [[0.8, -0.6], [0.6, 0.8]], [[0.6, -0.8], [0.8, 0.6]]
    return frame, {"V": V, "lam": 1.5 * np.arange(N, 0, -1.0), "mean": frame["mean"] + 0.25}


def _b2f_deltas(frame, istar):
    V, lam, rows = frame["V"], frame["lam"], []
    for signs in itertools.product((-1, 1), repeat=4):
        scaled = {k: s * math.sqrt(2.0 * (istar / 4.0) * lam[k - 1]) for k, s in zip((2, 3, 4, 5), signs)}
        rows.append([math.fsum(value * V[n, k - 1] for k, value in scaled.items()) for n in range(len(lam))])
    return np.array(rows)


def _b2f_joint(frame, fit, columns, delta):
    U, sigma0 = fit["V"][:, [k - 1 for k in columns]], frame["V"] @ np.diag(frame["lam"]) @ frame["V"].T
    shift = U.T @ delta
    return 0.5 * float(shift @ np.linalg.solve(U.T @ sigma0 @ U, shift))


def _b2f_refusal(case):
    frame, fit = _b2f_records(6, [0, 5, 2, 3, 4, 1])
    wide = {"V": _b2d_frame(24), "lam": _b2b_spectrum(24), "mean": np.zeros(24)}
    call = {"frame": frame, "fit": fit, "istar": 2.0, "universe": [2, 3, 4, 5, 6]}
    return {"frame_not_dict": {**call, "frame": list(frame.items())},
            "fit_unknown_field": {**call, "fit": {**fit, "sigma0": _B2cPoison()}},
            "fit_missing_mean": {**call, "fit": {"V": fit["V"], "lam": fit["lam"]}},
            "fit_size_mismatch": {**call, "fit": _b2f_records(7, [0, 6, 2, 3, 4, 5, 1])[1]},
            "basis_complex": {**call, "fit": {**fit, "V": fit["V"] + 0j}},
            "spectrum_increasing": {**call, "frame": {**frame, "lam": frame["lam"][::-1]}},
            "universe_float": {**call, "universe": [2.0, 3, 4, 5, 6]},
            "universe_numpy_int": {**call, "universe": [np.int64(2), 3, 4, 5, 6]},
            "universe_bool": {**call, "universe": [True, 2, 3, 4, 5]},
            "universe_gap": {**call, "universe": [2, 3, 4, 6]},
            "universe_market": {**call, "universe": [1, 2, 3, 4, 5]},
            "universe_too_short": {**call, "universe": [2, 3, 4]},
            "universe_too_long": {"frame": wide, "fit": {key: value.copy() for key, value in wide.items()},
                                  "istar": 2.0, "universe": list(range(2, 23))},
            "universe_beyond_n": {**call, "universe": [2, 3, 4, 5, 6, 7]},
            "istar_nonpositive": {**call, "istar": 0.0},
            "istar_bool": {**call, "istar": True},
            "istar_nonfinite": {**call, "istar": math.inf},
            "derived_overflow": {**call, "fit": {**fit, "lam": np.array([9.0, 7.5, 6.0, 4.5, 3.0, 5e-324])}}}[case]


def test_head_geometry_exact_frame_keeps_every_profile_in_the_first_four_axes(monkeypatch):
    import inspect
    import json
    module, geometry, opened = pio(), _kernel("head_geometry"), []
    assert list(inspect.signature(geometry).parameters) == ["frame", "fit", "istar", "universe"]
    frame = {"V": _b2d_frame(8), "lam": _b2b_spectrum(8), "mean": np.linspace(-1.0, 2.5, 8)}
    fit, universe, istar = {key: value.copy() for key, value in frame.items()}, [2, 3, 4, 5, 6, 7], 0.25
    reference, listed = _b2f_deltas(frame, istar), list(universe)
    np.testing.assert_allclose(frame["V"].T @ frame["V"], np.eye(8), rtol=0, atol=1e-13)
    assert (np.diff(frame["lam"]) < 0).all() and frame["mean"].any()
    for delta in reference:
        coordinates = [math.fsum(frame["V"][n, k] * delta[n] for n in range(8)) for k in range(8)]
        for columns in (universe, universe[:4]):
            information = 0.5 * math.fsum(coordinates[k - 1] ** 2 / frame["lam"][k - 1] for k in columns)
            assert information == pytest.approx(istar, rel=1e-12)
    arrays = [*frame.values(), *fit.values()]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots = [array.tobytes() for array in arrays], (dict(frame), dict(fit))

    def forbidden(*args, **kwargs):
        pytest.fail("fit, decomposition, selection, scan, calibration or frame draw inside the HEAD geometry")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for owner, name in ((module, "population_frame"), (module, "best_sets"), (module, "online_masks"),
                            (module, "nonoracle_masks"), (module, "oracle_masks"), (module, "masked_scan"),
                            (pdb, "fit_basis"), (pdb, "select_top_q"), (pdb, "scan_statistic"),
                            (pdb, "rank_threshold"), (np.linalg, "qr"), (np.linalg, "eig"), (np.linalg, "eigh"),
                            (np.linalg, "eigvalsh"), (np.linalg, "svd")):
            mp.setattr(owner, name, forbidden)
        out, again = geometry(frame, fit, istar, universe), geometry(frame, fit, istar, universe)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2c_same(frame, snapshots[0]) and _b2c_same(fit, snapshots[1]) and universe == listed and not opened
    assert set(out) == set(B2F_FIELDS) and out["support"] == [2, 3, 4, 5] and out["all_I_E_positive"] is True
    assert out["signs"] == [list(signs) for signs in itertools.product((-1, 1), repeat=4)]
    assert out["delta"].dtype == np.float64 and out["delta"].shape == (16, 8)
    np.testing.assert_allclose(out["delta"], reference, rtol=1e-12, atol=1e-13)
    np.testing.assert_allclose(out["delta"][::-1], -out["delta"], rtol=0, atol=1e-14)
    for key in ("I_E", "I_P4"):
        assert out[key] == pytest.approx([istar] * 16, rel=1e-12, abs=0)
    for key in ("f_E", "f_pop"):
        assert out[key] == pytest.approx([1.0] * 16, rel=0, abs=1e-12)
        assert out[key] == pytest.approx(out[key][::-1], rel=1e-12, abs=0)
        assert out["summary"][key] == pytest.approx({"min": 1.0, "mean": 1.0, "max": 1.0}, rel=0, abs=1e-12)
    rest = {key: value for key, value in out.items() if key != "delta"}
    assert json.loads(json.dumps(rest, allow_nan=False)) == rest and set(rest["summary"]) == {"f_E", "f_pop"}
    assert np.array_equal(again["delta"], out["delta"]) and {k: v for k, v in again.items() if k != "delta"} == rest


@pytest.mark.parametrize("case", B2F_FITTED)
def test_head_geometry_fitted_fractions_match_independent_joint_references(monkeypatch, case):
    import json
    geometry = _kernel("head_geometry")
    N, universe, perm, (e_ratio, p4_ratio, f_E, f_pop) = B2F_FITTED[case]
    frame, fit = _b2f_records(N, perm)
    istar, listed, reference = 2.0, list(universe), _b2f_deltas(frame, 2.0)
    np.testing.assert_allclose(fit["V"].T @ fit["V"], np.eye(N), rtol=0, atol=1e-15)
    assert (np.diff(fit["lam"]) < 0).all() and (fit["mean"] - frame["mean"]).all()
    for delta in reference:
        assert _b2f_joint(frame, fit, universe, delta) == pytest.approx(e_ratio * istar, rel=1e-12, abs=0)
        assert _b2f_joint(frame, fit, universe[:4], delta) == pytest.approx(p4_ratio * istar, rel=1e-12, abs=0)
    if perm is None:
        sigma0, axes = np.diag(frame["lam"]), fit["V"][:, 1:5].T
        assert abs(axes[1] @ sigma0 @ axes[2]) > 1.0
        for delta in reference:
            diagonal = 0.5 * math.fsum((u @ delta) ** 2 / (u @ sigma0 @ u) for u in axes)
            surrogate = 0.5 * math.fsum((u @ delta) ** 2 / scale for u, scale in zip(axes, fit["lam"][1:5]))
            assert min(abs(diagonal - p4_ratio * istar), abs(surrogate - p4_ratio * istar)) > 0.1
    arrays = [*frame.values(), *fit.values()]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots = [array.tobytes() for array in arrays], (dict(frame), dict(fit))
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        out = geometry(frame, fit, istar, universe)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2c_same(frame, snapshots[0]) and _b2c_same(fit, snapshots[1]) and universe == listed
    assert set(out) == set(B2F_FIELDS) and out["support"] == [2, 3, 4, 5] and np.array_equal(out["delta"], reference)
    assert out["signs"] == [list(signs) for signs in itertools.product((-1, 1), repeat=4)]
    assert out["I_E"] == pytest.approx([e_ratio * istar] * 16, rel=1e-12, abs=0)
    assert out["I_P4"] == pytest.approx([p4_ratio * istar] * 16, rel=1e-12, abs=0)
    assert out["f_pop"] == pytest.approx([f_pop] * 16, rel=1e-12, abs=0)
    summary = {"min": f_pop, "mean": f_pop, "max": f_pop}
    assert out["summary"]["f_pop"] == pytest.approx(summary, rel=1e-12, abs=0)
    if f_E is None:
        assert out["f_E"] == [None] * 16 and out["summary"]["f_E"] == {"min": None, "mean": None, "max": None}
    else:
        assert out["f_E"] == pytest.approx([f_E] * 16, rel=1e-12, abs=0)
        assert out["summary"]["f_E"] == pytest.approx({"min": f_E, "mean": f_E, "max": f_E}, rel=1e-12, abs=0)
    assert out["all_I_E_positive"] is (e_ratio > 0)
    rest = {key: value for key, value in out.items() if key != "delta"}
    assert json.loads(json.dumps(rest, allow_nan=False)) == rest


@pytest.mark.parametrize("case", B2F_REFUSALS)
def test_head_geometry_refuses_malformed_inputs_without_effects(monkeypatch, case):
    call = _b2f_refusal(case)
    geometry = _kernel("head_geometry")
    records = [record for record in (call["frame"], call["fit"]) if isinstance(record, dict)]
    arrays = [value for record in records for value in record.values() if isinstance(value, np.ndarray)]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots = [array.tobytes() for array in arrays], [dict(record) for record in records]
    listed = list(call["universe"])
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        with pytest.raises(ValueError):
            geometry(**call)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert all(_b2c_same(record, snapshot) for record, snapshot in zip(records, snapshots))
    assert call["universe"] == listed


def test_head_geometry_sign_dependent_fractions_have_distinct_worst_mean_and_best_profiles(monkeypatch):
    import json
    frame, fit = _b2f_records(6, [0, 5, 2, 3, 4, 1])
    V = fit["V"].copy()
    V[:, 4:6] = fit["V"][:, 4:6] @ np.array([[0.8, -0.6], [0.6, 0.8]])
    fit, universe, istar = {**fit, "V": V}, [2, 3, 4, 5, 6], 2.0
    profiles, reference = list(itertools.product((-1, 1), repeat=4)), _b2f_deltas(frame, 2.0)
    expected = [(123 if signs[0] == signs[3] else 99) / 148 for signs in profiles]
    np.testing.assert_allclose(V.T @ V, np.eye(6), rtol=0, atol=1e-15)
    assert V[:, 4].tolist() == [0.0, 0.6, 0.0, 0.0, 0.8, 0.0]
    assert V[:, 5].tolist() == [0.0, 0.8, 0.0, 0.0, -0.6, 0.0]
    assert frame["lam"].tolist() == [256.0, 64.0, 16.0, 4.0, 1.0, 0.25] and (np.diff(fit["lam"]) < 0).all()
    assert V[:, 4] @ np.diag(frame["lam"]) @ V[:, 4] == pytest.approx(592 / 25, rel=1e-14)
    assert reference.tolist() == [[0.0, 8.0 * a, 4.0 * b, 2.0 * c, 1.0 * d, 0.0] for a, b, c, d in profiles]
    for signs, delta, value in zip(profiles, reference, expected):
        combined = (24 * signs[0] + 4 * signs[3]) ** 2 / 1184
        assert _b2f_joint(frame, fit, universe, delta) == pytest.approx(istar, rel=1e-12)
        assert _b2f_joint(frame, fit, universe[:4], delta) == pytest.approx(1.0 + combined, rel=1e-12)
        assert (1.0 + combined) / istar == pytest.approx(value, rel=1e-15)
    mean = math.fsum(expected) / 16
    assert expected.count(99 / 148) == expected.count(123 / 148) == 8 and expected == expected[::-1]
    assert min(expected) == 99 / 148 and max(expected) == 123 / 148 and mean == pytest.approx(0.75, rel=1e-15)
    assert min(expected) < mean < max(expected)
    arrays = [*frame.values(), *fit.values()]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshots, listed = [array.tobytes() for array in arrays], (dict(frame), dict(fit)), list(universe)
    geometry = _kernel("head_geometry")

    def forbidden(*args, **kwargs):
        pytest.fail("fit or decomposition inside the HEAD geometry")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for owner, name in ((pdb, "fit_basis"), (np.linalg, "qr"), (np.linalg, "eigh"), (np.linalg, "svd")):
            mp.setattr(owner, name, forbidden)
        out = geometry(frame, fit, istar, universe)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2c_same(frame, snapshots[0]) and _b2c_same(fit, snapshots[1]) and universe == listed
    assert set(out) == set(B2F_FIELDS) and np.array_equal(out["delta"], reference)
    assert out["signs"] == [list(signs) for signs in profiles] and out["support"] == [2, 3, 4, 5]
    assert out["all_I_E_positive"] is True and out["I_E"] == pytest.approx([istar] * 16, rel=1e-12, abs=0)
    assert out["I_P4"] == pytest.approx([istar * value for value in expected], rel=1e-12, abs=0)
    for key in ("f_E", "f_pop"):
        assert out[key] == pytest.approx(expected, rel=1e-12, abs=0)
        assert out[key] == pytest.approx(out[key][::-1], rel=1e-12, abs=0)
        summary = out["summary"][key]
        assert summary == pytest.approx({"min": 99 / 148, "mean": 0.75, "max": 123 / 148}, rel=1e-12, abs=0)
        assert summary["min"] < summary["mean"] < summary["max"]
    rest = {key: value for key, value in out.items() if key != "delta"}
    assert json.loads(json.dumps(rest, allow_nan=False)) == rest


B2G_GAPS = {"boundary_accept": (2, 2, "star", False), "boundary_refuse": (2, 2, "next", True),
            "last_checked_pair_refuse": (2, 3, "tiny", True), "beyond_prefix_accept": (2, 4, "tiny", False),
            "beyond_prefix_inside_k3_refuse": (3, 4, "tiny", True)}
B2G_REFUSALS = ("x_one_dimensional", "x_complex", "x_overflow_after_cast", "x_single_row", "x_constant_column",
                "mean_overflow", "k_bool", "k_float", "k_zero", "k_above_twenty", "n_below_k_plus_two",
                "eigval_nonfinite", "eigval_nonpositive", "eigval_unsorted", "eigvec_wrong_shape")


def _b2g_rows(shift):
    base = np.array([[4.0, 4.0, 4.0, 4.0], [2.0, -2.0, 2.0, -2.0], [1.0, 1.0, -1.0, -1.0], [0.5, -0.5, -0.5, 0.5]])
    return np.vstack([base, -base]) + np.array(shift)


def _b2g_boundary():
    b = 1.0 - 1e-10
    while 1.0 - b < 1e-10:
        b = float(np.nextafter(b, 0.0))
    while 1.0 - float(np.nextafter(b, 2.0)) >= 1e-10:
        b = float(np.nextafter(b, 2.0))
    return {"star": b, "next": float(np.nextafter(b, 2.0)), "tiny": 1.0 - 2.0 ** -40}


def _b2g_refusal(case):
    X, big = _b2g_rows([0.0, 0.0, 0.0, 0.0]), np.finfo(np.float64).max
    constant, wide, overflow = X.copy(), np.vstack([np.eye(24), -np.eye(24)]), X.astype(np.longdouble)
    constant[:, 3] = 1.5
    with np.errstate(over="ignore"):
        overflow[0, 0] = np.longdouble(big) * 4
    records = {"eigval_nonfinite": ([9.0, np.nan, 3.0, 1.0], np.eye(4)),
               "eigval_nonpositive": ([9.0, 4.0, 2.0, 0.0], np.eye(4)),
               "eigval_unsorted": ([4.0, 9.0, 2.0, 1.0], np.eye(4)),
               "eigvec_wrong_shape": ([9.0, 4.0, 2.0, 1.0], np.eye(4)[:, :3])}
    if case in records:
        lam, V = records[case]
        return X, 2, {"eigval": np.array(lam), "eigvec": V, "lambda_corr": _B2cPoison()}
    rows = {"x_one_dimensional": (X[0], 2), "x_complex": (X + 0j, 2), "x_overflow_after_cast": (overflow, 2),
            "x_single_row": (X[:1], 2), "x_constant_column": (constant, 2),
            "mean_overflow": (np.array([[big, 1.0, 2.0], [big / 2, 3.0, 5.0]]), 1), "k_bool": (X, True),
            "k_float": (X, 2.0), "k_zero": (X, 0), "k_above_twenty": (wide, 21), "n_below_k_plus_two": (X, 3)}
    return (*rows[case], None)


def test_fit_record_wraps_one_real_sealed_fit_of_the_supplied_rows(monkeypatch):
    import inspect
    first_shift, second_shift = [3.0, -1.5, 0.25, 2.0], [-8.0, 0.5, 1.0, -0.75]
    base, X, Y = _b2g_rows([0.0] * 4), _b2g_rows(first_shift), _b2g_rows(second_shift)
    c2, U = np.array([16.0, 4.0, 1.0, 0.25]), base[:4].T / (2.0 * np.array([4.0, 2.0, 1.0, 0.5]))
    mu, fourth = math.fsum(c2) / 4, math.fsum(math.fsum(v * v for v in row) ** 2 for row in base) / 8
    shrinkage = (fourth - math.fsum(c2 ** 2)) / 8 / math.fsum((c2 - mu) ** 2)
    reference = (1.0 - shrinkage) * c2 + shrinkage * mu
    np.testing.assert_allclose(base.T @ base / 8 @ U, U * c2, rtol=0, atol=1e-15)
    np.testing.assert_allclose(U.T @ U, np.eye(4), rtol=0, atol=1e-15)
    assert not base.sum(axis=0).any() and (X.max(axis=0) > X.min(axis=0)).all() and 0.0 < shrinkage < 1.0
    assert [math.fsum(column) / 8 for column in X.T] == first_shift
    assert [math.fsum(column) / 8 for column in Y.T] == second_shift
    assert min((reference[:-1] - reference[1:]) / reference[:-1]) > 0.05
    module, adapter, real, seen, opened = pio(), _kernel("fit_record"), pdb.fit_basis, [], []
    assert list(inspect.signature(adapter).parameters) == ["X_fit", "K"]
    for rows in (X, Y):
        rows.flags.writeable = False
    kept = [X.tobytes(), Y.tobytes()]

    def spy(rows):
        seen.append((rows.tobytes(), rows.dtype, rows.shape, real(rows)))
        return seen[-1][3]

    def forbidden(*args, **kwargs):
        pytest.fail("frame draw, selection, scan or calibration inside the fit adapter")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        mp.setattr(pdb, "fit_basis", spy)
        for owner, name in ((module, "population_frame"), (module, "best_sets"), (module, "online_masks"),
                            (module, "nonoracle_masks"), (module, "oracle_masks"), (module, "masked_scan"),
                            (pdb, "select_top_q"), (pdb, "scan_statistic"), (pdb, "rank_threshold")):
            mp.setattr(owner, name, forbidden)
        first = adapter(X, 2)
        single = len(seen)
        second, again = adapter(Y, 2), adapter(X, 2)
    fitted, shape = seen[0][3], (8, 4)
    assert single == 1 and not opened
    assert [entry[:3] for entry in seen] == [(kept[0], np.float64, shape), (kept[1], np.float64, shape),
                                             (kept[0], np.float64, shape)]
    assert all(rows.tobytes() == data and not rows.flags.writeable for rows, data in zip((X, Y), kept))
    assert set(first) == {"V", "lam", "mean"} and all(first[key].dtype == np.float64 for key in first)
    assert first["V"].shape == (4, 4) and first["lam"].shape == first["mean"].shape == (4,)
    assert np.array_equal(first["V"], fitted["eigvec"]) and np.array_equal(first["lam"], fitted["eigval"])
    assert first["lam"] == pytest.approx(reference, rel=1e-12)
    np.testing.assert_allclose(np.abs(first["V"].T @ U), np.eye(4), rtol=0, atol=1e-12)
    assert not np.allclose(first["lam"], fitted["lambda_corr"])
    assert math.fsum(fitted["lambda_corr"]) == pytest.approx(4.0, rel=1e-12)
    assert first["mean"].tolist() == first_shift and second["mean"].tolist() == second_shift
    assert np.array_equal(second["V"], first["V"]) and np.array_equal(second["lam"], first["lam"])
    assert all(np.array_equal(again[key], first[key]) for key in first)
    projection = _kernel("projection_diagnostics")(first, first, [2, 3], np.zeros((1, 4)), "EXACT")
    assert projection["I_joint"].tolist() == [0.0] and projection["oracle_basis"] == "EXACT_ADDITIVE_KL"


@pytest.mark.parametrize("case", B2G_GAPS)
def test_fit_record_applies_the_t22_relative_gap_to_the_first_k_plus_two_axes_only(monkeypatch, case):
    (K, pair, kind, refused), b = B2G_GAPS[case], _b2g_boundary()
    assert 1.0 - b["star"] >= 1e-10 > 1.0 - b["next"] and b["next"] == np.nextafter(b["star"], 2.0)
    assert 1.0 - b["tiny"] == 2.0 ** -40 < 1e-10
    lam = [16.0, 8.0, 4.0, 2.0, 1.0, 0.5]
    lam[pair] = lam[pair - 1] * b[kind]
    gaps = [(lam[k] - lam[k + 1]) / lam[k] for k in range(len(lam) - 1)]
    assert gaps[pair - 1] == 1.0 - b[kind] and all(gap >= 0.5 for k, gap in enumerate(gaps) if k != pair - 1)
    assert (min(gaps[:K + 1]) < 1e-10) is refused
    X, adapter = np.vstack([np.eye(6), -np.eye(6)]), _kernel("fit_record")
    X.flags.writeable = False
    kept = X.tobytes()
    for scale in (2.0 ** -30, 1.0, 2.0 ** 30):
        record, calls = {"eigval": scale * np.array(lam), "eigvec": np.eye(6), "lambda_corr": _B2cPoison()}, []

        def stub(rows, record=record, calls=calls):
            calls.append(rows.tobytes())
            return record

        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            mp.setattr(pdb, "fit_basis", stub)
            try:
                out, failed = adapter(X, K), False
            except ValueError:
                out, failed = None, True
        assert failed is refused and calls == [kept]
        if not refused:
            assert set(out) == {"V", "lam", "mean"} and np.array_equal(out["V"], np.eye(6))
            assert np.array_equal(out["lam"], record["eigval"]) and np.array_equal(out["mean"], np.zeros(6))
    assert X.tobytes() == kept and not X.flags.writeable


@pytest.mark.parametrize("case", B2G_REFUSALS)
def test_fit_record_refuses_bad_rows_before_and_bad_fits_after_one_sealed_fit(monkeypatch, case):
    X, K, record = _b2g_refusal(case)
    adapter, calls = _kernel("fit_record"), []
    X.flags.writeable = False
    kept = X.tobytes()

    def stub(rows):
        calls.append(rows.tobytes())
        assert record is not None, "the sealed fit was reached by rows that must be refused before it"
        return record

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(pdb, "fit_basis", stub)
        with pytest.raises(ValueError):
            adapter(X, K)
    assert calls == ([] if record is None else [kept]) and X.tobytes() == kept and not X.flags.writeable


B2H_PERMS = {"aligned": list(range(24)), "misaligned": [0, 5, 2, 3, 4, 1, *range(6, 24)],
             "true_zero": [1, 0, *range(5, 24), 2, 3, 4]}
B2H_HEAD = {"aligned": ("aligned", None, "GEOMETRY_ALIGNED"),
            "misaligned": ("misaligned", None, "DESIGN_CONTROL_INCONCLUSIVE"),
            "misaligned_kappa_07": ("misaligned", 0.7, "GEOMETRY_ALIGNED"),
            "true_zero": ("true_zero", None, "DESIGN_CONTROL_INCONCLUSIVE"),
            "boundary_equal": ("misaligned", "equal", "GEOMETRY_ALIGNED"),
            "boundary_above": ("misaligned", "above", "DESIGN_CONTROL_INCONCLUSIVE")}
B2H_REFUSALS = ("setup_unplanned_n", "setup_float_n", "setup_bool_fit_id", "arm_unsupported_planned", "frame_wrong_n",
                "exact_with_rows", "fitted_without_rows", "rows_wrong_shape", "kappa_bool", "universe_config_changed",
                "k_float", "t_fit_float", "i_star_zero")


def _b2h_desc(*edits):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [["EXACT", 24, 0], ["FITTED_LW_GAUSSIAN", 24, 0]]),
                        (("scope", "applications"), ["RESIDUAL", "MARKET"]), (("parameters", "T_fit"), 48), *edits):
        cfg = _edited(cfg, path, value)
    return _kernel("design_descriptor")(cfg, "full")


def _b2h_frame():
    return {"V": np.eye(24), "lam": _b2b_spectrum(24), "mean": np.linspace(-1.0, 1.0, 24)}


def _b2h_fit(perm, shift=0.0):
    mean = np.linspace(-0.5, 1.5, 24) + shift
    return {"V": np.eye(24)[:, perm], "lam": 1.5 * np.arange(24, 0, -1.0), "mean": mean}


def _b2h_setup_id(did, setup, application, basis, fit_hash):
    arm, N, fit_id = setup
    return pdb.sha16({"design_id": did, "arm": arm, "N": N, "fit_id": fit_id, "application": application,
                      "universe_pcs": B2B_UNIVERSES[application], "basis_sha": basis, "fit_hash": fit_hash})


def _b2h_refusal(case):
    frame, rows, fitted = _b2h_frame(), np.vstack([np.eye(24), -np.eye(24)]), ["FITTED_LW_GAUSSIAN", 24, 0]
    plain = [["EXACT", 24, 0], ["FITTED_LW_GAUSSIAN", 24, 0], ["FITTED_LW_PLAIN", 24, 0]]
    edits = {"arm_unsupported_planned": ((("scope", "setups"), plain),), "kappa_bool": ((("head", "kappa_geo"), True),),
             "universe_config_changed": ((("applications", "RESIDUAL"), [2, 20]),),
             "k_float": ((("parameters", "K"), 20.0),), "t_fit_float": ((("parameters", "T_fit"), 48.0),),
             "i_star_zero": ((("parameters", "I_star"), 0.0),)}.get(case, ())
    small = {"V": np.eye(23), "lam": _b2b_spectrum(23), "mean": np.zeros(23)}
    changes = {"setup_unplanned_n": {"setup": ["FITTED_LW_GAUSSIAN", 32, 0]},
               "setup_float_n": {"setup": ["FITTED_LW_GAUSSIAN", 24.0, 0]},
               "setup_bool_fit_id": {"setup": ["FITTED_LW_GAUSSIAN", 24, False]},
               "arm_unsupported_planned": {"setup": ["FITTED_LW_PLAIN", 24, 0]}, "frame_wrong_n": {"frame": small},
               "exact_with_rows": {"setup": ["EXACT", 24, 0]}, "fitted_without_rows": {"X_fit": None},
               "rows_wrong_shape": {"X_fit": rows[:47]}}
    return {"desc": _b2h_desc(*edits), "frame": frame, "X_fit": rows, "setup": fitted, **changes.get(case, {})}


@pytest.mark.parametrize("arm", ["EXACT", "FITTED_LW_GAUSSIAN"])
def test_setup_bundle_exact_uses_the_frame_and_fitted_shares_one_fit(tmp_path, monkeypatch, arm):
    import inspect
    import json
    import os
    desc, frame, rows, exact = _b2h_desc(), _b2h_frame(), np.vstack([np.eye(24), -np.eye(24)]), arm == "EXACT"
    (fit, X_fit), setup = ((frame, None) if exact else (_b2h_fit(B2H_PERMS["aligned"]), rows)), [arm, 24, 0]
    did, basis = _kernel("design_id")(desc), pdb.array_sha256(frame["V"], frame["lam"], frame["mean"])
    fit_hash = None if exact else pdb.array_sha256(fit["V"], fit["lam"], fit["mean"])
    reference = _kernel("head_geometry")(frame, fit, 0.25, B2B_UNIVERSES["RESIDUAL"])
    geometry = {key: value for key, value in reference.items() if key != "delta"}
    assert geometry["summary"]["f_E"]["min"] == pytest.approx(1.0, rel=1e-12)
    assert desc["scope"]["applications"] == ["RESIDUAL", "MARKET"] and desc["science"]["head"]["kappa_geo"] == 0.8
    for rel in ("results/pca_info_online/alt/ALT.csv", "logs/pca_info_online/smoke/staging/x/design.json"):
        (tmp_path / rel).parent.mkdir(parents=True)
        (tmp_path / rel).write_text(pdb.canon({"family": "F2_STRUCTURED_RESIDUAL", "kappa_geo": 0.1}))
    module, bundle, calls, opened = pio(), _kernel("setup_bundle"), [], []
    assert list(inspect.signature(bundle).parameters) == ["desc", "frame", "X_fit", "setup"]
    arrays = [*frame.values(), *([] if exact else [rows])]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshot = [array.tobytes() for array in arrays], pdb.canon(desc)

    def fit_spy(X_fit, K):
        calls.append((X_fit.tobytes(), K, type(K)))
        assert not exact, "the EXACT arm must not fit"
        return fit

    def forbidden(*args, **kwargs):
        pytest.fail("frame draw, listing, fit_basis, selection, scan or calibration inside the SETUP bundle")

    monkeypatch.chdir(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        mp.setattr(module, "fit_record", fit_spy)
        for owner, name in ((module, "population_frame"), (module, "best_sets"), (module, "online_masks"),
                            (module, "nonoracle_masks"), (module, "oracle_masks"), (module, "masked_scan"),
                            (pdb, "fit_basis"), (pdb, "select_top_q"), (pdb, "scan_statistic"),
                            (pdb, "rank_threshold"), (os, "scandir"), (os, "listdir")):
            mp.setattr(owner, name, forbidden)
        out, again = bundle(desc, frame, X_fit, setup), bundle(desc, frame, X_fit, setup)
    metadata, absent = out["metadata"], {"status": "NOT_APPLICABLE", "kappa_geo": None, "geometry": None}
    assert set(out) == {"metadata", "fit"} and set(out["fit"]) == {"V", "lam", "mean"} and not opened
    assert set(metadata) == {"design_id", "setup", "basis_sha", "fit_hash", "applications"}
    assert calls == ([] if exact else [(rows.tobytes(), 20, int)] * 2)
    assert [metadata[key] for key in ("design_id", "setup", "basis_sha", "fit_hash")] == [did, setup, basis, fit_hash]
    assert all(np.array_equal(out["fit"][key], fit[key]) for key in fit)
    assert list(metadata["applications"]) == ["RESIDUAL", "MARKET"]
    for application, entry in metadata["applications"].items():
        assert set(entry) == {"universe", "setup_id", "baselines", "head"}
        assert entry["universe"] == B2B_UNIVERSES[application]
        assert entry["baselines"] == _kernel("spectral_baselines")(fit["lam"], application)["baselines"]
        assert entry["setup_id"] == _b2h_setup_id(did, setup, application, basis, fit_hash)
    aligned = {"status": "GEOMETRY_ALIGNED", "kappa_geo": 0.8, "geometry": geometry}
    assert metadata["applications"]["RESIDUAL"]["head"] == aligned
    assert metadata["applications"]["MARKET"]["head"] == absent
    assert json.loads(json.dumps(metadata, allow_nan=False)) == metadata and again["metadata"] == metadata
    assert all(np.array_equal(again["fit"][key], out["fit"][key]) for key in out["fit"])
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert pdb.canon(desc) == snapshot and setup == [arm, 24, 0]


@pytest.mark.parametrize("case", B2H_HEAD)
def test_setup_bundle_head_status_reads_only_the_descriptor_kappa_geo(monkeypatch, case):
    shape, kappa, status = B2H_HEAD[case]
    frame, fit, rows = _b2h_frame(), _b2h_fit(B2H_PERMS[shape]), np.vstack([np.eye(24), -np.eye(24)])
    reference = _kernel("head_geometry")(frame, fit, 0.25, B2B_UNIVERSES["RESIDUAL"])
    geometry, f_min = {k: v for k, v in reference.items() if k != "delta"}, reference["summary"]["f_E"]["min"]
    if shape == "true_zero":
        assert f_min is None and reference["all_I_E_positive"] is False and not any(reference["I_E"])
    else:
        assert f_min == pytest.approx({"aligned": 1.0, "misaligned": 0.75}[shape], rel=1e-12)
    if kappa in ("equal", "above"):
        kappa = f_min if kappa == "equal" else float(np.nextafter(f_min, 2.0))
    desc = _b2h_desc(*(() if kappa is None else ((("head", "kappa_geo"), kappa),)))
    did, default = _kernel("design_id")(desc), _kernel("design_id")(_b2h_desc())
    assert (did == default) is (kappa is None) and desc["science"]["head"]["kappa_det"] == 0.8
    module, bundle, calls, setup = pio(), _kernel("setup_bundle"), [], ["FITTED_LW_GAUSSIAN", 24, 0]

    def fit_spy(X_fit, K):
        calls.append(K)
        return fit

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(module, "fit_record", fit_spy)
        out = bundle(desc, frame, rows, setup)
    metadata, kappa_geo = out["metadata"], desc["science"]["head"]["kappa_geo"]
    assert calls == [20] and all(np.array_equal(out["fit"][key], fit[key]) for key in fit)
    assert metadata["applications"]["RESIDUAL"]["head"] == {"status": status, "kappa_geo": kappa_geo,
                                                             "geometry": geometry}
    assert metadata["applications"]["MARKET"]["head"]["status"] == "NOT_APPLICABLE"
    basis = pdb.array_sha256(frame["V"], frame["lam"], frame["mean"])
    fit_hash = pdb.array_sha256(fit["V"], fit["lam"], fit["mean"])
    assert metadata["basis_sha"] == basis and metadata["fit_hash"] == fit_hash and metadata["design_id"] == did
    for application, entry in metadata["applications"].items():
        assert entry["universe"] == B2B_UNIVERSES[application]
        assert entry["baselines"] == _kernel("spectral_baselines")(fit["lam"], application)["baselines"]
        assert entry["setup_id"] == _b2h_setup_id(did, setup, application, basis, fit_hash)


def test_setup_bundle_fit_hash_tracks_the_learned_mean_and_kappa_det_never_routes_geometry(monkeypatch):
    import json
    desc, other = _b2h_desc(), _b2h_desc((("head", "kappa_det"), 0.5))
    frame, rows, setup = _b2h_frame(), np.vstack([np.eye(24), -np.eye(24)]), ["FITTED_LW_GAUSSIAN", 24, 0]
    first, moved = _b2h_fit(B2H_PERMS["misaligned"]), _b2h_fit(B2H_PERMS["misaligned"], 0.25)
    hashes = [pdb.array_sha256(record["V"], record["lam"], record["mean"]) for record in (first, moved)]
    assert np.array_equal(first["V"], moved["V"]) and np.array_equal(first["lam"], moved["lam"])
    assert not np.array_equal(first["mean"], moved["mean"]) and hashes[0] != hashes[1]
    assert _kernel("design_id")(desc) != _kernel("design_id")(other) and other["science"]["head"]["kappa_geo"] == 0.8
    module, bundle, runs = pio(), _kernel("setup_bundle"), []
    for current, record in ((desc, first), (desc, moved), (other, first), (desc, first)):
        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            mp.setattr(module, "fit_record", lambda X_fit, K, record=record: record)
            runs.append(bundle(current, frame, rows, setup)["metadata"])
    base, shifted, detached, replay = runs
    assert replay == base and [run["fit_hash"] for run in runs] == [hashes[0], hashes[1], hashes[0], hashes[0]]
    assert len({run["basis_sha"] for run in runs}) == 1 and detached["design_id"] != base["design_id"]
    for application in ("RESIDUAL", "MARKET"):
        entries = [run["applications"][application] for run in (base, shifted, detached)]
        assert len({entry["setup_id"] for entry in entries}) == 3
        assert entries[0]["baselines"] == entries[1]["baselines"] == entries[2]["baselines"]
        assert entries[0]["head"] == entries[1]["head"] == entries[2]["head"]
    assert base["applications"]["RESIDUAL"]["head"]["status"] == "DESIGN_CONTROL_INCONCLUSIVE"
    assert all(json.loads(json.dumps(run, allow_nan=False)) == run for run in runs)


@pytest.mark.parametrize("case", B2H_REFUSALS)
def test_setup_bundle_refuses_bad_coordinates_frames_rows_and_config_before_any_fit(monkeypatch, case):
    call = _b2h_refusal(case)
    module, bundle, calls = pio(), _kernel("setup_bundle"), []
    arrays = [*call["frame"].values(), *([] if call["X_fit"] is None else [call["X_fit"]])]
    for array in arrays:
        array.flags.writeable = False
    kept, setup, snapshot = [array.tobytes() for array in arrays], list(call["setup"]), pdb.canon(call["desc"])
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(module, "fit_record", lambda X_fit, K: calls.append(K))
        with pytest.raises(ValueError):
            bundle(**call)
    assert not calls and call["setup"] == setup and pdb.canon(call["desc"]) == snapshot
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))


B2I_BAD_SCOPES = ("setups_empty", "setups_duplicate", "applications_empty", "applications_duplicate",
                  "families_empty", "families_duplicate", "policies_empty", "policies_duplicate")


def _b2i_bad_cfg(case):
    field, kind = case.split("_")
    duplicate = {"setups": [["EXACT", 32, 0], ["FITTED_LW_GAUSSIAN", 239, 0], ["EXACT", 32, 0]],
                 "applications": ["RESIDUAL", "RESIDUAL"],
                 "families": ["F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL", "F2_STRUCTURED_RESIDUAL"],
                 "policies": ["ONLINE_INFO_MIX_W128", "FULL_K", "FULL_K"]}[field]
    return field, _edited(_design_cfg(), ("scope", field), [] if kind == "empty" else duplicate)


@pytest.mark.parametrize("case", B2I_BAD_SCOPES)
def test_shared_config_check_refuses_an_empty_or_duplicate_scope_before_any_producer(monkeypatch, case):
    (field, bad), module, opened = _b2i_bad_cfg(case), pio(), []
    entries, snapshot = bad["scope"][field], pdb.canon(bad)
    assert not entries or len({pdb.canon(entry) for entry in entries}) < len(entries)
    assert field != "setups" or not entries or (entries[0] is not entries[2] and entries[0] == entries[2])
    names = ("_check_cfg", "seed_plan", "design_descriptor", "population_frame")
    check, plan, describe, frame = (_kernel(name) for name in names)

    def forbidden(*args, **kwargs):
        pytest.fail("fit or frame decomposition reached through an invalid scope")

    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for owner, name in ((pdb, "fit_basis"), (module, "fit_record"), (np.linalg, "qr")):
            mp.setattr(owner, name, forbidden)
        for call in (lambda: check(bad, "smoke"), lambda: plan(bad, "smoke"), lambda: describe(bad, "smoke"),
                     lambda: frame(bad, "smoke", 32)):
            with pytest.raises(ValueError):
                call()
    assert pdb.canon(bad) == snapshot and not opened


@pytest.mark.parametrize("case", ["singleton", "distinct"])
def test_shared_config_check_keeps_singleton_and_distinct_scopes_with_their_seed_plans(monkeypatch, case):
    scope = {"singleton": {"setups": [["EXACT", 32, 0]], "applications": ["RESIDUAL"],
                           "families": ["F2_STRUCTURED_RESIDUAL"], "policies": ["FULL_K"]},
             "distinct": {**_design_cfg()["scope"], "applications": ["RESIDUAL", "MARKET"]}}[case]
    cfg, opened = _edited(_design_cfg(), ("scope",), scope), []
    snapshot, root, files = pdb.canon(cfg), _kernel("CODE_ROOT"), _kernel("CODE_FILES")
    check, plan, describe = (_kernel(name) for name in ("_check_cfg", "seed_plan", "design_descriptor"))
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        assert check(cfg, "smoke") is None
        first, again = plan(cfg, "smoke"), plan(cfg, "smoke")
        desc, replay = describe(cfg, "smoke"), describe(cfg, "smoke")
    frames = {key for key in first["keys"] if key[0] == "frame"}
    assert first == again and desc == replay and desc["seed_plan_sha256"] == first["sha256"]
    assert desc["scope"] == scope and sorted(desc["science"]["dev"]["families"]) == sorted(DEV_FAMILIES)
    assert frames == {("frame", "SMOKE", setup[1]) for setup in scope["setups"]}
    assert pdb.canon(cfg) == snapshot and set(opened) == {(root / rel).resolve() for rel in files}


B2J_ROLES = ("DEV_NULL", "DEV_ALT", "CAL_NULL", "NULL_PLAN", "HOLD_NULL", "ALT")
B2J_SETUPS = (("EXACT", 24, 0), ("FITTED_LW_GAUSSIAN", 24, 0), ("FITTED_LW_GAUSSIAN", 24, 1), ("FITTED_LW_T7", 24, 0))
B2J_PRIMARY = ("FITTED_LW_GAUSSIAN", 24, 0)
B2J_CAPS = {"smoke_primary": ("smoke", (), B2J_PRIMARY, (1, 1, 2, 1, 3, 1)),
            "smoke_nonprimary_t7": ("smoke", (), ("FITTED_LW_T7", 24, 0), (1, 1, 2, 0, 1, 1)),
            "pilot_primary": ("pilot", (), B2J_PRIMARY, (1, 1, 3, 0, 1, 1)),
            "full_primary": ("full", (), B2J_PRIMARY, (1, 1, 4, 2, 5, 1)),
            "full_primary_outside_scope": ("full", ((("phi", "setup"), ["FITTED_LW_GAUSSIAN", 239, 0]),), B2J_PRIMARY,
                                           (1, 1, 4, 0, 1, 1))}
B2J_REFUSALS = ("key_structure", "word_semantics", "unplanned_coordinates", "frame_rows_and_descriptor")


def _b2j_cfg(*edits):
    cfg, setups = _design_cfg(), [list(setup) for setup in B2J_SETUPS]
    for path, value in ((("scope", "setups"), setups), (("phi", "setup"), list(B2J_PRIMARY)),
                        (("parameters", "T_fit"), 5), (("parameters", "H"), 3), *edits):
        cfg = _edited(cfg, path, value)
    return cfg


def _b2j_desc(mode="smoke", *edits):
    return _kernel("design_descriptor")(_b2j_cfg(*edits), mode)


def _b2j_frame(N=24):
    frame = {"V": _b2d_frame(N), "lam": _b2b_spectrum(N), "mean": np.linspace(-0.75, 1.25, N)}
    for array in frame.values():
        array.flags.writeable = False
    return frame


def _b2j_path(role="CAL_NULL", i=0, arm="FITTED_LW_GAUSSIAN", N=24, fit_id=0, campaign="SMOKE"):
    return ("path", campaign, arm, N, fit_id, role, i)


def _b2j_words(seed, key):
    import zlib
    return [32, seed, zlib.crc32(key[1].encode()), zlib.crc32(key[0].encode()),
            *(zlib.crc32(part.encode()) if isinstance(part, str) else int(part) for part in key[2:])]


def _b2j_reference(frame, words, rows, t7=False):
    draw = np.random.default_rng(np.random.SeedSequence(words))
    latent = draw.standard_normal((rows, frame["lam"].size))
    if t7:
        latent = latent / np.sqrt(draw.chisquare(7, size=rows) / 7)[:, None] * math.sqrt(5 / 7)
    return frame["mean"] + (latent * np.sqrt(frame["lam"])) @ frame["V"].T, latent


def _b2j_same_state(before, after):
    return after[0] == before[0] and np.array_equal(after[1], before[1]) and after[2:] == before[2:]


def _b2j_seed_spy(entropies):
    real = np.random.SeedSequence

    def seq(entropy=None, *args, **kwargs):
        entropies.append([int(word) for word in entropy])
        return real(entropy, *args, **kwargs)

    return seq


def _b2j_forbid(mp, t7_allowed):
    module = pio()

    def forbidden(*args, **kwargs):
        pytest.fail("stream-28 seeding, global PRNG, seed-plan enumeration, identity hash or fit in null_returns")

    for owner, name in ((pdb, "seed_key"), (pdb, "rng"), (pdb, "draw_path"), (pdb, "fit_basis"), (pdb, "array_sha256"),
                        (pdb, "sha16"), (np.random, "seed"), (pdb.sim, "garch_panel"), (module, "seed_plan"),
                        (module, "design_descriptor"), (module, "design_id"), (module, "population_frame"),
                        (module, "fit_record"), *(() if t7_allowed else ((pdb.sim, "t_innov"),))):
        mp.setattr(owner, name, forbidden)


@pytest.mark.parametrize("fit_id", [0, 1])
def test_null_returns_fitted_gaussian_draws_one_local_seedsequence_per_primitive_key(monkeypatch, fit_id):
    import inspect
    import zlib
    desc, frame, arm = _b2j_desc(), _b2j_frame(), "FITTED_LW_GAUSSIAN"
    crc = {label: zlib.crc32(label.encode()) for label in ("SMOKE", "path", "fit", arm, "CAL_NULL")}
    path, fit = ("path", "SMOKE", arm, 24, fit_id, "CAL_NULL", 1), ("fit", "SMOKE", arm, 24, fit_id)
    words = {path: [32, 3232, crc["SMOKE"], crc["path"], crc[arm], 24, fit_id, crc["CAL_NULL"], 1],
             fit: [32, 3232, crc["SMOKE"], crc["fit"], crc[arm], 24, fit_id]}
    rows, order = {path: 3, fit: 5}, [path, fit]
    references = {key: _b2j_reference(frame, words[key], rows[key]) for key in order}
    assert all(words[key] == _b2j_words(3232, key) for key in order) and desc["campaign"] == "SMOKE"
    assert desc["seed"] == 3232 and [arm, 24, fit_id] in desc["scope"]["setups"]
    assert [desc["science"]["parameters"][name] for name in ("H", "T_fit")] == [3, 5]
    np.testing.assert_allclose(frame["V"].T @ frame["V"], np.eye(24), rtol=0, atol=1e-13)
    generate, entropies, snapshot = _kernel("null_returns"), [], pdb.canon(desc)
    assert list(inspect.signature(generate).parameters) == ["desc", "frame", "key"]
    kept, seq, state = [a.tobytes() for a in frame.values()], _b2j_seed_spy(entropies), np.random.get_state()
    with monkeypatch.context() as mp:
        mp.setattr(np.random, "SeedSequence", seq)
        _b2j_forbid(mp, t7_allowed=False)
        outputs = {key: generate(desc, frame, key) for key in order}
        replay = {key: generate(desc, frame, key) for key in order[::-1]}
    assert _b2j_same_state(state, np.random.get_state())
    assert entropies == [words[key] for key in order + order[::-1]]
    for key, (reference, latent) in references.items():
        out = outputs[key]
        assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (rows[key], 24)
        assert np.isfinite(out).all() and np.array_equal(replay[key], out)
        np.testing.assert_allclose(out, reference, rtol=0, atol=1e-12)
        recovered = (out - frame["mean"]) @ frame["V"] / np.sqrt(frame["lam"])
        np.testing.assert_allclose(recovered, latent, rtol=0, atol=1e-11)
    assert pdb.canon(desc) == snapshot
    assert all(a.tobytes() == data and not a.flags.writeable for a, data in zip(frame.values(), kept))


def test_null_returns_t7_scales_each_row_by_one_shared_chisquare_through_the_received_t_innov(monkeypatch):
    import zlib
    desc, frame, arm = _b2j_desc(), _b2j_frame(), "FITTED_LW_T7"
    crc = {label: zlib.crc32(label.encode()) for label in ("SMOKE", "path", "fit", arm, "HOLD_NULL")}
    path, fit = ("path", "SMOKE", arm, 24, 0, "HOLD_NULL", 0), ("fit", "SMOKE", arm, 24, 0)
    words = {path: [32, 3232, crc["SMOKE"], crc["path"], crc[arm], 24, 0, crc["HOLD_NULL"], 0],
             fit: [32, 3232, crc["SMOKE"], crc["fit"], crc[arm], 24, 0]}
    rows, references = {path: 3, fit: 5}, {}
    for key in (path, fit):
        draw = np.random.default_rng(np.random.SeedSequence(words[key]))
        normal, chi2 = draw.standard_normal((rows[key], 24)), draw.chisquare(7, size=rows[key])
        latent = normal / np.sqrt(chi2 / 7)[:, None] * math.sqrt(5 / 7)
        returns = frame["mean"] + (latent * np.sqrt(frame["lam"])) @ frame["V"].T
        gaussian = frame["mean"] + (normal * np.sqrt(frame["lam"])) @ frame["V"].T
        assert words[key] == _b2j_words(3232, key) and chi2.min() < chi2.max() and not np.allclose(returns, gaussian)
        references[key] = (returns, latent)
    generate, entropies, calls, real = _kernel("null_returns"), [], [], pdb.sim.t_innov

    def spy(rng, shape):
        calls.append((type(rng), tuple(shape)))
        return real(rng, shape)

    kept, seq, state = [a.tobytes() for a in frame.values()], _b2j_seed_spy(entropies), np.random.get_state()
    snapshot = pdb.canon(desc)
    with monkeypatch.context() as mp:
        mp.setattr(np.random, "SeedSequence", seq)
        _b2j_forbid(mp, t7_allowed=True)
        mp.setattr(pdb.sim, "t_innov", spy)
        first, again = [generate(desc, frame, key) for key in (path, fit)], generate(desc, frame, path)
    assert _b2j_same_state(state, np.random.get_state()) and np.array_equal(again, first[0])
    assert entropies == [words[path], words[fit], words[path]]
    assert calls == [(np.random.Generator, (3, 24)), (np.random.Generator, (5, 24)), (np.random.Generator, (3, 24))]
    for out, key in zip(first, (path, fit)):
        reference, latent = references[key]
        assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (rows[key], 24)
        assert np.isfinite(out).all()
        np.testing.assert_allclose(out, reference, rtol=0, atol=1e-12)
        recovered = (out - frame["mean"]) @ frame["V"] / np.sqrt(frame["lam"])
        np.testing.assert_allclose(recovered, latent, rtol=0, atol=1e-10)
    assert pdb.canon(desc) == snapshot
    assert all(a.tobytes() == data and not a.flags.writeable for a, data in zip(frame.values(), kept))


def test_null_returns_replay_any_call_order_and_separate_role_fit_seed_and_campaign_keys(tmp_path, monkeypatch):
    smoke, frame = _b2j_desc(), _b2j_frame()
    other_seed, pilot = _b2j_desc("smoke", (("seed",), 3233)), _b2j_desc("pilot")
    cases = [(smoke, _b2j_path("CAL_NULL", 0), 3232, 3), (smoke, _b2j_path("CAL_NULL", 1), 3232, 3),
             (smoke, _b2j_path("HOLD_NULL", 0), 3232, 3), (smoke, _b2j_path("ALT", 0), 3232, 3),
             (smoke, _b2j_path("DEV_NULL", 0), 3232, 3), (smoke, _b2j_path("CAL_NULL", 0, fit_id=1), 3232, 3),
             (smoke, _b2j_path("CAL_NULL", 0, arm="FITTED_LW_T7"), 3232, 3),
             (smoke, ("fit", "SMOKE", "FITTED_LW_GAUSSIAN", 24, 0), 3232, 5),
             (smoke, ("fit", "SMOKE", "FITTED_LW_GAUSSIAN", 24, 1), 3232, 5),
             (other_seed, _b2j_path("CAL_NULL", 0), 3233, 3),
             (pilot, _b2j_path("CAL_NULL", 0, campaign="PILOT"), 3232, 3)]
    order = [6, 10, 0, 8, 3, 9, 1, 5, 7, 2, 4]
    references = [_b2j_reference(frame, _b2j_words(seed, key), rows, key[2] == "FITTED_LW_T7")[0]
                  for _, key, seed, rows in cases]
    assert sorted(order) == list(range(len(cases))) and other_seed["seed"] == 3233 and pilot["campaign"] == "PILOT"
    assert len({pdb.canon(_b2j_words(seed, key)) for _, key, seed, _ in cases}) == len(cases)
    generate = _kernel("null_returns")
    first = [generate(desc, frame, key) for desc, key, _, _ in cases]
    monkeypatch.chdir(tmp_path)
    shuffled = {index: generate(cases[index][0], frame, cases[index][1]) for index in order}
    numpy_key = ("path", "SMOKE", "FITTED_LW_GAUSSIAN", np.int64(24), np.int64(0), "CAL_NULL", np.uint32(1))
    assert all(np.array_equal(shuffled[index], out) for index, out in enumerate(first))
    assert generate(smoke, frame, numpy_key).tobytes() == first[1].tobytes()
    assert len({out.tobytes() for out in first}) == len(cases)
    for out, reference, (_, _, _, rows) in zip(first, references, cases):
        assert out.dtype == np.float64 and out.shape == (rows, 24)
        np.testing.assert_allclose(out, reference, rtol=0, atol=1e-12)


def test_null_returns_common_keys_are_byte_identical_across_family_application_and_policy_choices():
    frame, ident = _b2j_frame(), _kernel("design_id")
    edits = {"base": (), "scope_families": ((("scope", "families"), ["F1_TAIL_RESIDUAL"]),),
             "scope_market": ((("scope", "applications"), ["MARKET"]), (("scope", "families"), ["F3_MARKET"])),
             "scope_policies": ((("scope", "policies"), ["FULL_K"]),),
             "family_support": ((("families", "F2_STRUCTURED_RESIDUAL", "support"), [3, 9, 17, 20]),),
             "phi_claim": ((("phi", "claims", "H1"), "F_HEAD_RESIDUAL"),)}
    descs = {name: _b2j_desc("smoke", *change) for name, change in edits.items()}
    keys = [("fit", "SMOKE", "FITTED_LW_GAUSSIAN", 24, 0), ("fit", "SMOKE", "FITTED_LW_T7", 24, 0),
            _b2j_path("NULL_PLAN", 0), _b2j_path("HOLD_NULL", 2), _b2j_path("ALT", 0),
            _b2j_path("DEV_ALT", 0, fit_id=1), _b2j_path("CAL_NULL", 1, arm="FITTED_LW_T7")]
    assert len({ident(desc) for desc in descs.values()}) == len(descs)
    assert len({pdb.canon(desc["scope"]) for desc in descs.values()}) == 4
    generate = _kernel("null_returns")
    for key in keys:
        assert len({generate(desc, frame, key).tobytes() for desc in descs.values()}) == 1, key


@pytest.mark.parametrize("case", B2J_CAPS)
def test_null_returns_index_caps_follow_the_preexecution_seed_plan_of_each_setup(monkeypatch, case):
    mode, edits, setup, counts = B2J_CAPS[case]
    cfg, frame, campaign, t7 = _b2j_cfg(*edits), _b2j_frame(), mode.upper(), setup[0] == "FITTED_LW_T7"
    desc, keys = _kernel("design_descriptor")(cfg, mode), set(_kernel("seed_plan")(cfg, mode)["keys"])
    caps, snapshots = dict(zip(B2J_ROLES, counts)), (pdb.canon(cfg), pdb.canon(desc))
    planned = {role: sorted(key[6] for key in keys if key[:5] == ("path", campaign, *setup) and key[5] == role)
               for role in B2J_ROLES}
    accepted = [("fit", campaign, *setup), *(("path", campaign, *setup, role, n - 1) for role, n in caps.items() if n)]
    refused = [("path", campaign, *setup, role, n) for role, n in caps.items()]
    assert planned == {role: list(range(n)) for role, n in caps.items()}
    assert set(accepted) <= keys and not set(refused) & keys
    assert _kernel("_plan_applies")(desc) is (case not in ("pilot_primary", "full_primary_outside_scope"))
    references = {key: _b2j_reference(frame, _b2j_words(3232, key), 5 if key[0] == "fit" else 3, t7)[0]
                  for key in accepted}
    generate = _kernel("null_returns")
    outputs = {key: generate(desc, frame, key) for key in accepted}
    for key, reference in references.items():
        assert outputs[key].dtype == np.float64 and outputs[key].shape == reference.shape
        np.testing.assert_allclose(outputs[key], reference, rtol=0, atol=1e-12)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2j_forbid(mp, t7_allowed=False)
        for key in refused:
            with pytest.raises(ValueError):
                generate(desc, frame, key)
    assert (pdb.canon(cfg), pdb.canon(desc)) == snapshots and all(not array.flags.writeable for array in frame.values())


def test_null_returns_refuses_planned_exact_path_keys_before_any_draw(monkeypatch):
    cfg, frame = _b2j_cfg(), _b2j_frame()
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    slots = (("DEV_NULL", 0), ("DEV_ALT", 0), ("CAL_NULL", 0), ("CAL_NULL", 1), ("HOLD_NULL", 0), ("ALT", 0))
    exact = [_b2j_path(role, i, arm="EXACT") for role, i in slots] + [("fit", "SMOKE", "EXACT", 24, 0)]
    fitted = [_b2j_path(role, i) for role, i in slots]
    assert ["EXACT", 24, 0] in desc["scope"]["setups"] and set(exact[:-1]) | set(fitted) <= planned
    assert exact[-1] not in planned and ("fit", "SMOKE", *B2J_PRIMARY) in planned
    references = [_b2j_reference(frame, _b2j_words(3232, key), 3)[0] for key in fitted]
    generate, snapshot = _kernel("null_returns"), pdb.canon(desc)
    for key, reference in zip(fitted, references):
        np.testing.assert_allclose(generate(desc, frame, key), reference, rtol=0, atol=1e-12)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2j_forbid(mp, t7_allowed=False)
        for key in exact:
            with pytest.raises(ValueError):
                generate(desc, frame, key)
    assert pdb.canon(desc) == snapshot and all(not array.flags.writeable for array in frame.values())


def _b2j_refusals(group):
    desc, frame, base = _b2j_desc(), _b2j_frame(), _b2j_path()
    fit, planned = ("fit", "SMOKE", *B2J_PRIMARY), set(_kernel("seed_plan")(_b2j_cfg(), "smoke")["keys"])
    if group == "key_structure":
        other = {"frame_key": ("frame", "SMOKE", 24),
                 "meta_key": ("meta", "SMOKE", *B2J_PRIMARY, "CAL_NULL", "F2_STRUCTURED_RESIDUAL", 0),
                 "devlib_key": ("devlib", "SMOKE", *B2J_PRIMARY, "F0_ISOTROPIC_RESIDUAL", 0),
                 "boot_key": ("boot", "SMOKE", *B2J_PRIMARY, "RESIDUAL", "F2_STRUCTURED_RESIDUAL")}
        assert set(other.values()) | {base, fit} <= planned
        keys = {**other, "list_key": list(base), "empty_key": (), "none_key": None, "string_key": "path",
                "path_without_index": base[:6], "path_with_extra_word": (*base, 0),
                "fit_with_role": (*fit, "CAL_NULL")}
        return {name: (desc, frame, key) for name, key in keys.items()}
    if group == "word_semantics":
        keys = {"fit_id_false": _b2j_path(fit_id=False), "n_float": _b2j_path(N=24.0),
                "index_true": _b2j_path(i=True), "index_float": _b2j_path(i=1.0),
                "index_numpy_float": _b2j_path(i=np.float64(1.0)), "index_numpy_bool": _b2j_path(i=np.bool_(True)),
                "index_negative": _b2j_path(i=-1), "index_beyond_word": _b2j_path(i=2 ** 32),
                "fit_key_fit_id_false": (*fit[:4], False),
                "fit_key_n_numpy_float": ("fit", "SMOKE", "FITTED_LW_GAUSSIAN", np.float64(24.0), 0)}
        aliases = {"fit_id_false", "n_float", "index_true", "index_float", "index_numpy_float", "fit_key_fit_id_false",
                   "fit_key_n_numpy_float"}
        assert aliases <= {name for name, key in keys.items() if key in planned}
        calls = {name: (desc, frame, key) for name, key in keys.items()}
        return {**calls, "seed_beyond_word": ({**desc, "seed": 2 ** 32}, frame, base),
                "seed_true": ({**desc, "seed": True}, frame, base)}
    if group == "unplanned_coordinates":
        plain_cfg = _b2j_cfg((("scope", "setups"), [*map(list, B2J_SETUPS), ["FITTED_LW_PLAIN", 24, 0]]))
        plain = _kernel("design_descriptor")(plain_cfg, "smoke")
        undeclared = {"arm_undeclared_path": _b2j_path(arm="FITTED_LW_PLAIN"),
                      "arm_undeclared_fit": ("fit", "SMOKE", "FITTED_LW_PLAIN", 24, 0)}
        assert set(undeclared.values()) <= set(_kernel("seed_plan")(plain_cfg, "smoke")["keys"])
        keys = {"campaign_pilot": _b2j_path(campaign="PILOT"), "campaign_lowercase": _b2j_path(campaign="smoke"),
                "campaign_none": _b2j_path(campaign=None), "n_unplanned": _b2j_path(N=32),
                "fit_id_unplanned": _b2j_path(fit_id=2), "fit_key_unplanned": (*fit[:4], 2),
                "exact_fit_key": ("fit", "SMOKE", "EXACT", 24, 0), "arm_absent": _b2j_path(arm="FITTED_LW_T5"),
                "arm_not_label": _b2j_path(arm=7), "role_dev_lib": _b2j_path("DEV_LIB"),
                "role_fit_null": _b2j_path("FIT_NULL"), "role_lowercase": _b2j_path("cal_null"),
                "role_not_label": _b2j_path(0), "null_plan_nonprimary": _b2j_path("NULL_PLAN", fit_id=1)}
        assert not set(keys.values()) & planned
        calls = {name: (desc, frame, key) for name, key in keys.items()}
        return {**calls, **{name: (plain, frame, key) for name, key in undeclared.items()}}
    nan_v = frame["V"].copy()
    nan_v[3, 5] = np.nan
    frames = {"frame_tuple": tuple(frame.values()), "frame_without_mean": {"V": frame["V"], "lam": frame["lam"]},
              "frame_extra_field": {**frame, "basis_sha": "0" * 64}, "frame_dimension_23": _b2j_frame(23),
              "frame_nonfinite_v": {**frame, "V": nan_v}, "frame_complex_v": {**frame, "V": frame["V"] + 0j},
              "frame_zero_lam": {**frame, "lam": np.append(frame["lam"][:23], 0.0)},
              "frame_increasing_lam": {**frame, "lam": frame["lam"][::-1]},
              "frame_short_mean": {**frame, "mean": frame["mean"][:23]}}
    for name, bad in frames.items():
        if name != "frame_dimension_23":
            with pytest.raises(ValueError):
                _kernel("_frozen_record")(bad, "frame")
    rows = {"h_float": (_b2j_desc("smoke", (("parameters", "H"), 3.0)), base),
            "h_zero": (_b2j_desc("smoke", (("parameters", "H"), 0)), base),
            "t_fit_true": (_b2j_desc("smoke", (("parameters", "T_fit"), True)), fit),
            "descriptor_without_scope": ({key: value for key, value in desc.items() if key != "scope"}, base)}
    calls = {name: (desc, bad, base) for name, bad in frames.items()}
    return {**calls, **{name: (bad, frame, key) for name, (bad, key) in rows.items()}}


@pytest.mark.parametrize("group", B2J_REFUSALS)
def test_null_returns_refuses_malformed_unplanned_or_misframed_inputs_before_any_draw(monkeypatch, group):
    calls = _b2j_refusals(group)
    frames = [frame.values() if isinstance(frame, dict) else frame for _, frame, _ in calls.values()]
    arrays = [array for frame in frames for array in frame if isinstance(array, np.ndarray)]
    kept, snapshots = [array.tobytes() for array in arrays], {name: pdb.canon(call[0]) for name, call in calls.items()}
    generate = _kernel("null_returns")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2j_forbid(mp, t7_allowed=False)
        for name, (desc, frame, key) in calls.items():
            try:
                generate(desc, frame, key)
            except ValueError:
                continue
            pytest.fail(f"{group}: {name} was accepted")
    assert {name: pdb.canon(call[0]) for name, call in calls.items()} == snapshots
    assert all(array.tobytes() == data for array, data in zip(arrays, kept))


def _b2j_stubbed_call(monkeypatch, generate, desc, frame, key, normal):
    import types
    real, entropies, created, received, draws = np.random.SeedSequence, [], [], [], []

    def seq(entropy=None, *args, **kwargs):
        entropies.append([int(word) for word in entropy])
        created.append(real(entropy, *args, **kwargs))
        return created[-1]

    def standard_normal(size=None, dtype=np.float64, out=None):
        draws.append(("standard_normal", tuple(size)))
        return np.full(size, normal)

    def chisquare(df, size=None):
        draws.append(("chisquare", df, size))
        return np.full(size, 7.0)

    def default_rng(seed=None):
        received.append(seed)
        return types.SimpleNamespace(standard_normal=standard_normal, chisquare=chisquare)

    with monkeypatch.context() as mp:
        mp.setattr(np.random, "SeedSequence", seq)
        mp.setattr(np.random, "default_rng", default_rng)
        _b2j_forbid(mp, t7_allowed=True)
        try:
            result = generate(desc, frame, key)
        except ValueError:
            result, exception_raised = None, True
        else:
            exception_raised = False
    return result, exception_raised, entropies, created, received, draws


@pytest.mark.parametrize("arm", ["FITTED_LW_GAUSSIAN", "FITTED_LW_T7"])
def test_null_returns_refuses_a_derived_overflow_after_exactly_one_stubbed_finite_draw(monkeypatch, arm):
    desc, frame, key, t7 = _b2j_desc(), _b2j_frame(), _b2j_path(arm=arm), arm == "FITTED_LW_T7"
    scale = math.sqrt(5 / 7) if t7 else 1.0
    expected = [("standard_normal", (3, 24)), *([("chisquare", 7, 3)] if t7 else [])]
    control = frame["mean"] + (np.full((3, 24), scale) * np.sqrt(frame["lam"])) @ frame["V"].T
    huge = np.full((3, 24), 2.0 ** 1023 * scale)
    _kernel("_frozen_record")(frame, "frame")
    np.testing.assert_allclose(frame["V"].T @ frame["V"], np.eye(24), rtol=0, atol=1e-13)
    assert frame["lam"][0] == 16.0 and np.isfinite(huge).all() and np.isfinite(control).all()
    with np.errstate(over="ignore", invalid="ignore"):
        assert not np.isfinite(frame["mean"] + (huge * np.sqrt(frame["lam"])) @ frame["V"].T).all()
    generate, words = _kernel("null_returns"), _b2j_words(3232, key)
    runs = {name: _b2j_stubbed_call(monkeypatch, generate, desc, frame, key, normal)
            for name, normal in (("control", 1.0), ("overflow", 2.0 ** 1023))}
    for name, (_, _, entropies, created, received, draws) in runs.items():
        assert entropies == [words] and len(created) == len(received) == 1 and received[0] is created[0], name
        assert draws == expected, name
    control_out, control_raised = runs["control"][:2]
    overflow_out, overflow_raised = runs["overflow"][:2]
    assert control_raised is False and overflow_raised is True
    assert type(control_out) is np.ndarray and control_out.dtype == np.float64 and control_out.shape == (3, 24)
    np.testing.assert_allclose(control_out, control, rtol=0, atol=1e-12)
    assert overflow_out is None and all(not array.flags.writeable for array in frame.values())


@pytest.mark.parametrize("role, field, value", [("CAL_NULL", ("sizes", "CAL_NULL"), "2"),
                                                ("CAL_NULL", ("sizes", "CAL_NULL"), True),
                                                ("HOLD_NULL", ("null_plan", "n_cap"), "3"),
                                                ("HOLD_NULL", ("null_plan", "n_cap"), 3.5)],
                         ids=["cal_cap_string", "cal_cap_bool", "primary_hold_cap_string", "primary_hold_cap_float"])
def test_null_returns_refuses_a_mistyped_final_role_cap_before_any_draw(monkeypatch, role, field, value):
    cfg, frame, key = _b2j_cfg(), _b2j_frame(), _b2j_path(role, 0)
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    original = desc[field[0]][field[1]]
    assert key in planned and _kernel("_plan_applies")(desc) and list(key[2:5]) == desc["science"]["phi"]["setup"]
    assert type(original) is int and original == {"CAL_NULL": 2, "HOLD_NULL": 3}[role] and original != value
    poisoned = _edited(desc, field, value)
    assert pdb.canon(_edited(poisoned, field, original)) == pdb.canon(desc) != pdb.canon(poisoned)
    snapshots, kept = (pdb.canon(desc), pdb.canon(poisoned)), [array.tobytes() for array in frame.values()]
    generate = _kernel("null_returns")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2j_forbid(mp, t7_allowed=False)
        with pytest.raises(ValueError):
            generate(poisoned, frame, key)
    assert (pdb.canon(desc), pdb.canon(poisoned)) == snapshots and poisoned[field[0]][field[1]] is value
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(frame.values(), kept))


B2K_EXACT = (("EXACT", 21, 0), ("EXACT", 32, 0), ("EXACT", 239, 0))
B2K_CAPS = {"smoke_exact_n32": ("smoke", (), ("EXACT", 32, 0), (1, 1, 2, 0, 1, 1)),
            "pilot_exact_n239": ("pilot", (), ("EXACT", 239, 0), (1, 1, 3, 0, 1, 1)),
            "full_exact_n32": ("full", (), ("EXACT", 32, 0), (1, 1, 4, 0, 1, 1)),
            "smoke_exact_primary": ("smoke", ((("phi", "setup"), ["EXACT", 32, 0]),), ("EXACT", 32, 0),
                                    (1, 1, 2, 1, 3, 1))}
B2K_REFUSALS = ("domains_and_arms", "word_semantics", "unplanned_coordinates_and_caps", "rows_k_n_and_descriptor")


def _b2k_cfg(*edits):
    return _b2j_cfg((("scope", "setups"), [*map(list, B2J_SETUPS), *map(list, B2K_EXACT)]), *edits)


def _b2k_desc(mode="smoke", *edits):
    return _kernel("design_descriptor")(_b2k_cfg(*edits), mode)


def _b2k_path(role="CAL_NULL", i=0, N=32, fit_id=0, campaign="SMOKE"):
    return ("path", campaign, "EXACT", N, fit_id, role, i)


def _b2k_reference(seed, key):
    return np.random.default_rng(np.random.SeedSequence(_b2j_words(seed, key))).standard_normal((3, 21))


def _b2k_forbid(mp):
    module = pio()
    _b2j_forbid(mp, t7_allowed=False)
    for owner, name in ((module, "null_returns"), (module, "_frozen_record"), (np.linalg, "qr")):
        mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail("frame, fitted-return or QR work in exact_scores"))


def _b2k_spied_call(monkeypatch, generate, desc, key):
    import types
    real_seq, real_rng = np.random.SeedSequence, np.random.default_rng
    entropies, created, received, draws = [], [], [], []

    def seq(entropy=None, *args, **kwargs):
        entropies.append([int(word) for word in entropy])
        created.append(real_seq(entropy, *args, **kwargs))
        return created[-1]

    def default_rng(seed=None):
        received.append(seed)
        generator = real_rng(seed)

        def standard_normal(size=None, dtype=np.float64, out=None):
            draws.append(tuple(size))
            return generator.standard_normal(size)

        return types.SimpleNamespace(standard_normal=standard_normal)

    with monkeypatch.context() as mp:
        mp.setattr(np.random, "SeedSequence", seq)
        mp.setattr(np.random, "default_rng", default_rng)
        _b2k_forbid(mp)
        result = generate(desc, key)
    return result, entropies, created, received, draws


@pytest.mark.parametrize("N", [21, 32, 239])
def test_exact_scores_draw_one_h_by_21_standard_normal_per_planned_exact_path_key(monkeypatch, N):
    import inspect
    import zlib
    cfg, key = _b2k_cfg(), _b2k_path("CAL_NULL", 1, N=N)
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    crc = {label: zlib.crc32(label.encode()) for label in ("SMOKE", "path", "EXACT", "CAL_NULL")}
    words = [32, 3232, crc["SMOKE"], crc["path"], crc["EXACT"], N, 0, crc["CAL_NULL"], 1]
    reference = np.random.default_rng(np.random.SeedSequence(words)).standard_normal((3, 21))
    params = desc["science"]["parameters"]
    assert key in planned and words == _b2j_words(3232, key) and ["EXACT", N, 0] in desc["scope"]["setups"]
    assert (params["H"], params["K"]) == (3, 20) and type(params["K"]) is int and desc["seed"] == 3232
    generate, snapshot, state = _kernel("exact_scores"), pdb.canon(desc), np.random.get_state()
    assert list(inspect.signature(generate).parameters) == ["desc", "key"]
    out, entropies, created, received, draws = _b2k_spied_call(monkeypatch, generate, desc, key)
    assert entropies == [words] and len(created) == len(received) == 1 and received[0] is created[0]
    assert draws == [(3, 21)] and _b2j_same_state(state, np.random.get_state()) and pdb.canon(desc) == snapshot
    assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (3, 21) and np.isfinite(out).all()
    assert np.array_equal(out, reference)


def test_exact_scores_replay_any_call_order_and_separate_role_index_n_seed_and_campaign_keys(tmp_path, monkeypatch):
    smoke, other_seed, pilot = _b2k_desc(), _b2k_desc("smoke", (("seed",), 3233)), _b2k_desc("pilot")
    slots = (("CAL_NULL", 0, 32), ("CAL_NULL", 1, 32), ("HOLD_NULL", 0, 32), ("ALT", 0, 32), ("DEV_NULL", 0, 32),
             ("DEV_ALT", 0, 32), ("CAL_NULL", 0, 239), ("CAL_NULL", 0, 24), ("CAL_NULL", 0, 21))
    cases = [*((smoke, _b2k_path(role, i, N=N), 3232) for role, i, N in slots), (other_seed, _b2k_path(), 3233),
             (pilot, _b2k_path(campaign="PILOT"), 3232)]
    order = [6, 10, 0, 8, 3, 9, 1, 5, 7, 2, 4]
    references = [_b2k_reference(seed, key) for _, key, seed in cases]
    assert sorted(order) == list(range(len(cases))) and other_seed["seed"] == 3233 and pilot["campaign"] == "PILOT"
    assert len({pdb.canon(_b2j_words(seed, key)) for _, key, seed in cases}) == len(cases)
    generate, state = _kernel("exact_scores"), np.random.get_state()
    first = [generate(desc, key) for desc, key, _ in cases]
    monkeypatch.chdir(tmp_path)
    shuffled = {index: generate(cases[index][0], cases[index][1]) for index in order}
    numpy_key = ("path", "SMOKE", "EXACT", np.int64(32), np.int64(0), "CAL_NULL", np.uint32(1))
    assert all(np.array_equal(shuffled[index], out) for index, out in enumerate(first))
    assert generate(smoke, numpy_key).tobytes() == first[1].tobytes() and _b2j_same_state(state, np.random.get_state())
    assert len({out.tobytes() for out in first}) == len(cases)
    for out, reference in zip(first, references):
        assert out.dtype == np.float64 and out.shape == (3, 21) and np.array_equal(out, reference)


def test_exact_scores_same_key_bytes_ignore_family_application_policy_and_scientific_labels():
    ident = _kernel("design_id")
    edits = {"base": (), "scope_families": ((("scope", "families"), ["F1_TAIL_RESIDUAL"]),),
             "scope_market": ((("scope", "applications"), ["MARKET"]), (("scope", "families"), ["F3_MARKET"])),
             "scope_policies": ((("scope", "policies"), ["FULL_K"]),),
             "family_support": ((("families", "F2_STRUCTURED_RESIDUAL", "support"), [3, 9, 17, 20]),),
             "phi_claim": ((("phi", "claims", "H1"), "F_HEAD_RESIDUAL"),),
             "kappa_geo": ((("head", "kappa_geo"), 0.7),)}
    descs = {name: _b2k_desc("smoke", *change) for name, change in edits.items()}
    keys = [_b2k_path("CAL_NULL", 1), _b2k_path("HOLD_NULL", 0, N=239), _b2k_path("DEV_ALT", 0, N=21)]
    assert len({ident(desc) for desc in descs.values()}) == len(descs)
    generate = _kernel("exact_scores")
    for key in keys:
        assert {generate(desc, key).tobytes() for desc in descs.values()} == {_b2k_reference(3232, key).tobytes()}, key


@pytest.mark.parametrize("case", B2K_CAPS)
def test_exact_scores_caps_follow_the_seed_plan_without_leaking_the_fitted_primary_plan(monkeypatch, case):
    mode, edits, setup, counts = B2K_CAPS[case]
    cfg, campaign, caps = _b2k_cfg(*edits), mode.upper(), dict(zip(B2J_ROLES, counts))
    desc, keys = _kernel("design_descriptor")(cfg, mode), set(_kernel("seed_plan")(cfg, mode)["keys"])
    planned = {role: sorted(key[6] for key in keys if key[:5] == ("path", campaign, *setup) and key[5] == role)
               for role in B2J_ROLES}
    accepted = [("path", campaign, *setup, role, n - 1) for role, n in caps.items() if n]
    refused = [("path", campaign, *setup, role, n) for role, n in caps.items()]
    assert planned == {role: list(range(n)) for role, n in caps.items()} and set(accepted) <= keys
    assert not set(refused) & keys and ("fit", campaign, *setup) not in keys
    assert (desc["science"]["phi"]["setup"] == list(setup)) is (case == "smoke_exact_primary")
    assert _kernel("_plan_applies")(desc) is (mode != "pilot")
    generate, snapshot = _kernel("exact_scores"), pdb.canon(desc)
    for key in accepted:
        assert np.array_equal(generate(desc, key), _b2k_reference(3232, key)), key
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2k_forbid(mp)
        for key in refused:
            with pytest.raises(ValueError):
                generate(desc, key)
    assert pdb.canon(desc) == snapshot


def _b2k_refusals(group):
    cfg, base = _b2k_cfg(), _b2k_path()
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    if group == "domains_and_arms":
        other = {"fitted_gaussian_path": _b2j_path(), "fitted_t7_path": _b2j_path(arm="FITTED_LW_T7"),
                 "fitted_fit": ("fit", "SMOKE", *B2J_PRIMARY), "frame_key": ("frame", "SMOKE", 32),
                 "meta_key": ("meta", "SMOKE", "EXACT", 32, 0, "CAL_NULL", "F2_STRUCTURED_RESIDUAL", 0),
                 "devlib_key": ("devlib", "SMOKE", "EXACT", 32, 0, "F0_ISOTROPIC_RESIDUAL", 0),
                 "boot_key": ("boot", "SMOKE", "EXACT", 32, 0, "RESIDUAL", "F2_STRUCTURED_RESIDUAL")}
        assert set(other.values()) | {base} <= planned and ("fit", "SMOKE", "EXACT", 32, 0) not in planned
        keys = {**other, "exact_fit": ("fit", "SMOKE", "EXACT", 32, 0), "list_key": list(base), "empty_key": (),
                "none_key": None, "path_without_index": base[:6], "path_with_extra_word": (*base, 0)}
        return {name: (desc, key) for name, key in keys.items()}
    if group == "word_semantics":
        keys = {"fit_id_false": _b2k_path(fit_id=False), "n_float": _b2k_path(N=32.0),
                "n_numpy_float": _b2k_path(N=np.float64(32.0)), "index_true": _b2k_path(i=True),
                "index_float": _b2k_path(i=1.0), "index_numpy_float": _b2k_path(i=np.float64(1.0)),
                "index_numpy_bool": _b2k_path(i=np.bool_(True)), "index_negative": _b2k_path(i=-1),
                "index_beyond_word": _b2k_path(i=2 ** 32)}
        aliases = {"fit_id_false", "n_float", "n_numpy_float", "index_true", "index_float", "index_numpy_float"}
        assert aliases <= {name for name, key in keys.items() if key in planned}
        calls = {name: (desc, key) for name, key in keys.items()}
        return {**calls, "seed_beyond_word": ({**desc, "seed": 2 ** 32}, base),
                "seed_true": ({**desc, "seed": True}, base)}
    if group == "unplanned_coordinates_and_caps":
        keys = {"campaign_pilot": _b2k_path(campaign="PILOT"), "campaign_none": _b2k_path(campaign=None),
                "n_unplanned": _b2k_path(N=33), "fit_id_unplanned": _b2k_path(fit_id=1),
                "role_dev_lib": _b2k_path("DEV_LIB"), "role_fit_null": _b2k_path("FIT_NULL"),
                "role_lowercase": _b2k_path("cal_null"), "role_not_label": _b2k_path(0),
                "null_plan_nonprimary": _b2k_path("NULL_PLAN"),
                "hold_beyond_generic_cap": _b2k_path("HOLD_NULL", 1), "cal_beyond_cap": _b2k_path("CAL_NULL", 2)}
        assert not set(keys.values()) & planned and desc["null_plan"]["n_cap"] == 3 > desc["sizes"]["HOLD_NULL"]
        mistyped = {"cal_cap_string": ("CAL_NULL", "2"), "cal_cap_bool": ("CAL_NULL", True),
                    "hold_cap_float": ("HOLD_NULL", 1.0)}
        calls = {name: (desc, key) for name, key in keys.items()}
        poisoned = {name: (_edited(desc, ("sizes", role), value), _b2k_path(role))
                    for name, (role, value) in mistyped.items()}
        return {**calls, **poisoned}
    n20_cfg = _b2k_cfg((("scope", "setups"), [*map(list, B2J_SETUPS), *map(list, B2K_EXACT), ["EXACT", 20, 0]]))
    assert _b2k_path(N=20) in set(_kernel("seed_plan")(n20_cfg, "smoke")["keys"])
    fields = {"h_float": ("H", 3.0), "h_zero": ("H", 0), "h_true": ("H", True), "k_float": ("K", 20.0),
              "k_nineteen": ("K", 19), "k_true": ("K", True)}
    calls = {name: (_edited(desc, ("science", "parameters", field), value), base)
             for name, (field, value) in fields.items()}
    return {**calls, "n_below_21_planned": (_kernel("design_descriptor")(n20_cfg, "smoke"), _b2k_path(N=20)),
            "descriptor_without_scope": ({key: value for key, value in desc.items() if key != "scope"}, base)}


@pytest.mark.parametrize("group", B2K_REFUSALS)
def test_exact_scores_refuse_fitted_unplanned_mistyped_or_undersized_inputs_before_any_draw(monkeypatch, group):
    calls = _b2k_refusals(group)
    snapshots = {name: pdb.canon(desc) for name, (desc, _) in calls.items()}
    generate = _kernel("exact_scores")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2k_forbid(mp)
        for name, (desc, key) in calls.items():
            try:
                generate(desc, key)
            except ValueError:
                continue
            pytest.fail(f"{group}: {name} was accepted")
    assert {name: pdb.canon(desc) for name, (desc, _) in calls.items()} == snapshots


B2L_F0, B2L_F1, B2L_F2, B2L_HEAD, B2L_F3 = (*DEV_FAMILIES, "F3_MARKET")
B2L_REFUSALS = ("domains_and_structure", "families_and_roles", "word_semantics", "caps_dimensions_and_descriptor")


def _b2l_cfg(*edits):
    lib = [(("modes", mode, "sizes", "DEV_LIB"), 3) for mode in ("smoke", "pilot", "full")]
    scope = ((("scope", "applications"), ["RESIDUAL", "MARKET"]), (("scope", "families"), [B2L_F2, B2L_HEAD, B2L_F3]))
    return _b2k_cfg((("dev", "n_lib"), 3), *lib, *scope, *edits)


def _b2l_desc(mode="smoke", *edits):
    return _kernel("design_descriptor")(_b2l_cfg(*edits), mode)


def _b2l_devlib(family, index, arm="FITTED_LW_GAUSSIAN", N=24, fit_id=0, campaign="SMOKE"):
    return ("devlib", campaign, arm, N, fit_id, family, index)


def _b2l_meta(role, family, index, arm="FITTED_LW_GAUSSIAN", N=24, fit_id=0, campaign="SMOKE"):
    return ("meta", campaign, arm, N, fit_id, role, family, index)


def _b2l_reference(seed, key):
    draw, family = np.random.default_rng(np.random.SeedSequence(_b2j_words(seed, key))), key[-2]
    if family == B2L_F0:
        return draw.standard_normal((1, 20))
    return draw.choice((-1.0, 1.0), size=(1, 1 if family == B2L_F3 else 4))


def _b2l_forbid(mp):
    module = pio()
    _b2k_forbid(mp)
    for name in ("exact_scores", "population_drift", "projection_diagnostics", "head_geometry"):
        mp.setattr(module, name, lambda *args, **kwargs: pytest.fail("geometry work in direction_draws"))


def _b2l_spy(mp, normal=None):
    import types
    real_seq, real_rng = np.random.SeedSequence, np.random.default_rng
    entropies, created, received, draws = [], [], [], []

    def seq(entropy=None, *args, **kwargs):
        entropies.append([int(word) for word in entropy])
        created.append(real_seq(entropy, *args, **kwargs))
        return created[-1]

    def default_rng(seed=None):
        received.append(seed)
        generator = real_rng(seed)

        def standard_normal(size=None, dtype=np.float64, out=None):
            draws.append(("standard_normal", tuple(size)))
            return generator.standard_normal(size) if normal is None else np.full(size, normal)

        def choice(a, size=None, replace=True, p=None, axis=0, shuffle=True):
            draws.append(("choice", tuple(a), tuple(size)))
            return generator.choice(a, size, replace, p, axis, shuffle)

        return types.SimpleNamespace(standard_normal=standard_normal, choice=choice)

    mp.setattr(np.random, "SeedSequence", seq)
    mp.setattr(np.random, "default_rng", default_rng)
    return entropies, created, received, draws


B2L_LAWS = {"devlib_f0": (_b2l_devlib(B2L_F0, 2), "standard_normal", 20),
            "devlib_f1_unscoped": (_b2l_devlib(B2L_F1, 0, fit_id=1), "choice", 4),
            "meta_dev_alt_head": (_b2l_meta("DEV_ALT", B2L_HEAD, 0), "choice", 4),
            "meta_cal_f2_exact": (_b2l_meta("CAL_NULL", B2L_F2, 1, "EXACT", 32), "choice", 4),
            "meta_hold_f3_t7": (_b2l_meta("HOLD_NULL", B2L_F3, 0, "FITTED_LW_T7"), "choice", 1)}
B2L_CAPS = {"library_vs_dev_alt": ((_b2l_devlib(B2L_F0, 2), _b2l_meta("DEV_ALT", B2L_F0, 0)),
                                   (_b2l_devlib(B2L_F0, 3), _b2l_meta("DEV_ALT", B2L_F0, 1))),
            "primary_hold_vs_exact_hold": ((_b2l_meta("HOLD_NULL", B2L_F2, 2),
                                            _b2l_meta("HOLD_NULL", B2L_F2, 0, "EXACT", 32)),
                                           (_b2l_meta("HOLD_NULL", B2L_F2, 3),
                                            _b2l_meta("HOLD_NULL", B2L_F2, 1, "EXACT", 32))),
            "cal_alt_and_roles_without_metadata": ((_b2l_meta("CAL_NULL", B2L_HEAD, 1), _b2l_meta("ALT", B2L_F3, 0)),
                                                   (_b2l_meta("CAL_NULL", B2L_HEAD, 2), _b2l_meta("ALT", B2L_F3, 1),
                                                    _b2l_meta("NULL_PLAN", B2L_F2, 0),
                                                    _b2l_meta("DEV_NULL", B2L_F2, 0)))}


@pytest.mark.parametrize("case", B2L_LAWS)
def test_direction_draws_take_one_raw_family_draw_per_planned_meta_or_devlib_key(monkeypatch, case):
    import inspect
    import zlib
    (key, method, width), cfg = B2L_LAWS[case], _b2l_cfg()
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    words = [32, 3232, zlib.crc32(b"SMOKE"), zlib.crc32(key[0].encode()),
             *(zlib.crc32(part.encode()) if isinstance(part, str) else part for part in key[2:])]
    draw = np.random.default_rng(np.random.SeedSequence(words))
    if method == "standard_normal":
        reference, expected = draw.standard_normal((1, width)), [("standard_normal", (1, width))]
    else:
        reference, expected = draw.choice((-1.0, 1.0), size=(1, width)), [("choice", (-1.0, 1.0), (1, width))]
    fixed, scope = _kernel("DRIFT_FAMILIES")[key[-2]][1], desc["scope"]["families"]
    assert key in planned and words == _b2j_words(3232, key) and desc["science"]["parameters"]["K"] == 20
    assert width == (20 if fixed is None else len(fixed)) and B2L_F3 in scope and not {B2L_F0, B2L_F1} & set(scope)
    assert sorted(desc["science"]["dev"]["families"]) == sorted(DEV_FAMILIES)
    generate, snapshot, state = _kernel("direction_draws"), pdb.canon(desc), np.random.get_state()
    assert list(inspect.signature(generate).parameters) == ["desc", "key"]
    with monkeypatch.context() as mp:
        entropies, created, received, draws = _b2l_spy(mp)
        _b2l_forbid(mp)
        out = generate(desc, key)
    assert entropies == [words] and len(created) == len(received) == 1 and received[0] is created[0]
    assert draws == expected and _b2j_same_state(state, np.random.get_state()) and pdb.canon(desc) == snapshot
    assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (1, width) and np.isfinite(out).all()
    assert np.array_equal(out, reference)
    assert out.any() if method == "standard_normal" else set(out.flat) <= {-1.0, 1.0}


def test_direction_draws_replay_any_order_and_separate_every_primitive_key_part(tmp_path, monkeypatch):
    smoke, other_seed, pilot = _b2l_desc(), _b2l_desc("smoke", (("seed",), 3233)), _b2l_desc("pilot")
    keys = [_b2l_devlib(B2L_F0, 0), _b2l_devlib(B2L_F0, 1), _b2l_devlib(B2L_F1, 0),
            _b2l_devlib(B2L_F0, 0, "EXACT", 239), _b2l_devlib(B2L_F0, 0, fit_id=1), _b2l_meta("DEV_ALT", B2L_F0, 0),
            _b2l_meta("CAL_NULL", B2L_F2, 0), _b2l_meta("CAL_NULL", B2L_F2, 1), _b2l_meta("ALT", B2L_F2, 0),
            _b2l_meta("HOLD_NULL", B2L_F2, 0, "EXACT", 21), _b2l_meta("CAL_NULL", B2L_HEAD, 0, "FITTED_LW_T7")]
    pilot_key = ("devlib", "PILOT", *keys[0][2:])
    cases = [*((smoke, key, 3232) for key in keys), (other_seed, keys[0], 3233), (pilot, pilot_key, 3232)]
    order = [12, 3, 7, 0, 10, 5, 1, 9, 2, 11, 6, 4, 8]
    references = [_b2l_reference(seed, key) for _, key, seed in cases]
    assert set(keys) <= set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert pilot_key in set(_kernel("seed_plan")(_b2l_cfg(), "pilot")["keys"])
    assert sorted(order) == list(range(len(cases))) and other_seed["seed"] == 3233 and pilot["campaign"] == "PILOT"
    assert len({pdb.canon(_b2j_words(seed, key)) for _, key, seed in cases}) == len(cases)
    generate, state = _kernel("direction_draws"), np.random.get_state()
    first = [generate(desc, key) for desc, key, _ in cases]
    monkeypatch.chdir(tmp_path)
    shuffled = {index: generate(cases[index][0], cases[index][1]) for index in order}
    numpy_key = ("devlib", "SMOKE", "FITTED_LW_GAUSSIAN", np.int64(24), np.int64(0), B2L_F0, np.uint32(1))
    assert all(np.array_equal(shuffled[index], out) for index, out in enumerate(first))
    assert generate(smoke, numpy_key).tobytes() == first[1].tobytes() and _b2j_same_state(state, np.random.get_state())
    assert all(out.dtype == np.float64 and np.array_equal(out, ref) for out, ref in zip(first, references))
    isotropic = [out.tobytes() for out, (_, key, _) in zip(first, cases) if key[-2] == B2L_F0]
    assert len(isotropic) == len(set(isotropic)) == 7


def test_direction_draws_same_key_bytes_ignore_application_policy_istar_and_threshold_labels():
    ident = _kernel("design_id")
    edits = {"base": (), "applications": ((("scope", "applications"), ["RESIDUAL"]),),
             "policies": ((("scope", "policies"), ["FULL_K"]),), "istar": ((("parameters", "I_star"), 0.5),),
             "kappa_geo": ((("head", "kappa_geo"), 0.7),), "phi_claim": ((("phi", "claims", "H1"), B2L_HEAD),)}
    descs = {name: _b2l_desc("smoke", *change) for name, change in edits.items()}
    keys = [_b2l_devlib(B2L_F1, 2), _b2l_meta("DEV_ALT", B2L_F0, 0), _b2l_meta("CAL_NULL", B2L_F2, 1, "EXACT", 32),
            _b2l_meta("HOLD_NULL", B2L_F3, 0, "FITTED_LW_T7")]
    assert len({ident(desc) for desc in descs.values()}) == len(descs)
    generate = _kernel("direction_draws")
    for key in keys:
        assert {generate(desc, key).tobytes() for desc in descs.values()} == {_b2l_reference(3232, key).tobytes()}, key


@pytest.mark.parametrize("case", B2L_CAPS)
def test_direction_draws_caps_follow_the_domain_specific_seed_plan(monkeypatch, case):
    (accepted, refused), cfg = B2L_CAPS[case], _b2l_cfg()
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    assert set(accepted) <= planned and not set(refused) & planned and _kernel("_plan_applies")(desc)
    sizes, plan = desc["sizes"], desc["null_plan"]
    assert (sizes["DEV_LIB"], sizes["DEV_ALT"], sizes["HOLD_NULL"], plan["n_cap"]) == (3, 1, 1, 3)
    assert desc["science"]["dev"]["n_lib"] == 3 and desc["science"]["phi"]["setup"] == list(B2J_PRIMARY)
    generate, snapshot = _kernel("direction_draws"), pdb.canon(desc)
    for key in accepted:
        assert np.array_equal(generate(desc, key), _b2l_reference(3232, key)), key
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2l_forbid(mp)
        for key in refused:
            with pytest.raises(ValueError):
                generate(desc, key)
    assert pdb.canon(desc) == snapshot


def _b2l_refusals(group):
    cfg, base, lib = _b2l_cfg(), _b2l_meta("CAL_NULL", B2L_F2, 0), _b2l_devlib(B2L_F0, 0)
    desc, planned = _kernel("design_descriptor")(cfg, "smoke"), set(_kernel("seed_plan")(cfg, "smoke")["keys"])
    if group == "domains_and_structure":
        other = {"fitted_path": _b2j_path(), "exact_path": _b2k_path(), "fitted_fit": ("fit", "SMOKE", *B2J_PRIMARY),
                 "frame_key": ("frame", "SMOKE", 24), "boot_key": ("boot", "SMOKE", *B2J_PRIMARY, "RESIDUAL", B2L_F2)}
        assert set(other.values()) | {base, lib} <= planned
        keys = {**other, "meta_as_list": list(base), "empty_key": (), "none_key": None, "meta_without_index": base[:7],
                "meta_with_extra_word": (*base, 0), "devlib_without_index": lib[:6],
                "devlib_with_extra_word": (*lib, 0)}
        return {name: (desc, key) for name, key in keys.items()}
    if group == "families_and_roles":
        f4_cfg = _b2l_cfg((("families", "F4_ROTATION"), {"application": "RESIDUAL", "support": [2, 3]}),
                          (("scope", "families"), [B2L_F2, B2L_HEAD, B2L_F3, "F4_ROTATION"]))
        f4_key = _b2l_meta("CAL_NULL", "F4_ROTATION", 0)
        assert f4_key in set(_kernel("seed_plan")(f4_cfg, "smoke")["keys"])
        assert "F4_ROTATION" not in _kernel("DRIFT_FAMILIES") and B2L_F3 in desc["scope"]["families"]
        keys = {"devlib_f3": _b2l_devlib(B2L_F3, 0), "dev_alt_f3": _b2l_meta("DEV_ALT", B2L_F3, 0),
                "cal_f0_unscoped": _b2l_meta("CAL_NULL", B2L_F0, 0),
                "hold_f1_unscoped": _b2l_meta("HOLD_NULL", B2L_F1, 0),
                "role_dev_null": _b2l_meta("DEV_NULL", B2L_F2, 0), "role_null_plan": _b2l_meta("NULL_PLAN", B2L_F2, 0),
                "role_dev_lib": _b2l_meta("DEV_LIB", B2L_F2, 0), "role_lowercase": _b2l_meta("cal_null", B2L_F2, 0),
                "role_not_label": _b2l_meta(0, B2L_F2, 0), "family_unknown": _b2l_meta("CAL_NULL", "F5_UNKNOWN", 0),
                "family_lowercase": _b2l_devlib(B2L_F0.lower(), 0), "family_not_label": _b2l_devlib(0, 0)}
        assert not set(keys.values()) & planned
        calls = {name: (desc, key) for name, key in keys.items()}
        return {**calls, "family_declared_not_canonical": (_kernel("design_descriptor")(f4_cfg, "smoke"), f4_key)}
    if group == "word_semantics":
        keys = {"meta_fit_id_false": _b2l_meta("CAL_NULL", B2L_F2, 0, fit_id=False),
                "meta_n_float": _b2l_meta("CAL_NULL", B2L_F2, 0, N=24.0),
                "meta_index_true": _b2l_meta("CAL_NULL", B2L_F2, True),
                "meta_index_float": _b2l_meta("CAL_NULL", B2L_F2, 1.0),
                "devlib_index_numpy_float": _b2l_devlib(B2L_F0, np.float64(2.0)),
                "devlib_n_numpy_float": _b2l_devlib(B2L_F0, 0, N=np.float64(24.0)),
                "devlib_index_numpy_bool": _b2l_devlib(B2L_F0, np.bool_(True)),
                "devlib_index_negative": _b2l_devlib(B2L_F0, -1),
                "devlib_index_beyond_word": _b2l_devlib(B2L_F0, 2 ** 32)}
        aliases = {"meta_fit_id_false", "meta_n_float", "meta_index_true", "meta_index_float",
                   "devlib_index_numpy_float", "devlib_n_numpy_float"}
        assert aliases <= {name for name, key in keys.items() if key in planned}
        calls = {name: (desc, key) for name, key in keys.items()}
        return {**calls, "seed_beyond_word": ({**desc, "seed": 2 ** 32}, base),
                "seed_true": ({**desc, "seed": True}, lib)}
    setups = [*map(list, B2J_SETUPS), *map(list, B2K_EXACT)]
    n20_cfg = _b2l_cfg((("scope", "setups"), [*setups, ["EXACT", 20, 0]]))
    plain_cfg = _b2l_cfg((("scope", "setups"), [*setups, ["FITTED_LW_PLAIN", 24, 0]]))
    n20_key, plain_key = _b2l_meta("CAL_NULL", B2L_F2, 0, "EXACT", 20), _b2l_devlib(B2L_F0, 0, "FITTED_LW_PLAIN")
    assert n20_key in set(_kernel("seed_plan")(n20_cfg, "smoke")["keys"])
    assert plain_key in set(_kernel("seed_plan")(plain_cfg, "smoke")["keys"])
    unplanned = {"campaign_pilot": _b2l_meta("CAL_NULL", B2L_F2, 0, campaign="PILOT"),
                 "n_unplanned": _b2l_devlib(B2L_F0, 0, N=33),
                 "fit_id_unplanned": _b2l_meta("CAL_NULL", B2L_F2, 0, fit_id=2)}
    assert not set(unplanned.values()) & planned
    poisoned = {"library_cap_string": (("sizes", "DEV_LIB"), "3", lib),
                "dev_alt_cap_bool": (("sizes", "DEV_ALT"), True, _b2l_meta("DEV_ALT", B2L_F0, 0)),
                "cal_cap_float": (("sizes", "CAL_NULL"), 2.0, base),
                "primary_hold_cap_string": (("null_plan", "n_cap"), "3", _b2l_meta("HOLD_NULL", B2L_F2, 0)),
                "k_float": (("science", "parameters", "K"), 20.0, base),
                "k_nineteen": (("science", "parameters", "K"), 19, lib),
                "k_true": (("science", "parameters", "K"), True, base)}
    calls = {name: (_edited(desc, field, value), key) for name, (field, value, key) in poisoned.items()}
    return {**calls, **{name: (desc, key) for name, key in unplanned.items()},
            "n_below_21_planned": (_kernel("design_descriptor")(n20_cfg, "smoke"), n20_key),
            "arm_planned_undeclared": (_kernel("design_descriptor")(plain_cfg, "smoke"), plain_key),
            "descriptor_without_scope": ({key: value for key, value in desc.items() if key != "scope"}, base)}


@pytest.mark.parametrize("group", B2L_REFUSALS)
def test_direction_draws_refuse_invalid_keys_families_caps_or_dimensions_before_any_draw(monkeypatch, group):
    calls = _b2l_refusals(group)
    snapshots = {name: pdb.canon(desc) for name, (desc, _) in calls.items()}
    generate = _kernel("direction_draws")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2l_forbid(mp)
        for name, (desc, key) in calls.items():
            try:
                generate(desc, key)
            except ValueError:
                continue
            pytest.fail(f"{group}: {name} was accepted")
    assert {name: pdb.canon(desc) for name, (desc, _) in calls.items()} == snapshots


def test_direction_draws_refuse_a_zero_or_nonfinite_isotropic_row_after_exactly_one_draw(monkeypatch):
    desc, key = _b2l_desc(), _b2l_devlib(B2L_F0, 0)
    words, expected = _b2j_words(3232, key), [("standard_normal", (1, 20))]
    assert key in set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    generate = _kernel("direction_draws")
    with monkeypatch.context() as mp:
        entropies, created, received, draws = _b2l_spy(mp, normal=1.0)
        _b2l_forbid(mp)
        control = generate(desc, key)
    assert entropies == [words] and len(created) == len(received) == 1 and received[0] is created[0]
    assert draws == expected and type(control) is np.ndarray and control.dtype == np.float64
    assert np.array_equal(control, np.ones((1, 20)))
    for value in (0.0, math.inf, math.nan):
        with monkeypatch.context() as mp:
            entropies, created, received, draws = _b2l_spy(mp, normal=value)
            _b2l_forbid(mp)
            with pytest.raises(ValueError):
                generate(desc, key)
        assert entropies == [words] and len(created) == len(received) == 1 and received[0] is created[0], value
        assert draws == expected, value


B2M_CASES = [(arm, application) for arm in ("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7")
             for application in ("RESIDUAL", "MARKET")]
B2M_REFUSALS = {"null_with_delta": ("EXACT", "CAL_NULL", "return"),
                "alt_without_delta": ("FITTED_LW_T7", "ALT", None),
                "alt_delta_of_score_length": ("FITTED_LW_GAUSSIAN", "ALT", "score")}


def _b2m_record(V, lam, mean):
    record = {"V": V, "lam": lam, "mean": mean}
    for array in record.values():
        array.flags.writeable = False
    return record


def _b2m_fit():
    return _b2m_record(_b2d_frame(24)[:, ::-1].copy(), np.linspace(30.0, 1.0, 24), np.linspace(0.5, -0.25, 24))


def _b2m_copy(record):
    return _b2m_record(*(np.array(record[name]) for name in ("V", "lam", "mean")))


def _b2m_arrays():
    arrays = (np.linspace(-2.0, 3.0, 72).reshape(3, 24), np.linspace(-3.0, 4.0, 63).reshape(3, 21),
              np.linspace(1.0, -0.5, 24))
    for array in arrays:
        array.flags.writeable = False
    return arrays


def _b2m_project(rows, center, record, application):
    columns, V, lam = [pc - 1 for pc in B2B_UNIVERSES[application]], record["V"], record["lam"]
    return np.array([[math.fsum((row[n] - center[n]) * V[n, k] for n in range(V.shape[0])) / math.sqrt(lam[k])
                      for k in columns] for row in np.atleast_2d(rows)])


def _b2m_forbid(mp):
    module = pio()
    _b2j_forbid(mp, t7_allowed=False)
    names = ("population_drift", "direction_draws", "projection_diagnostics", "head_geometry", "setup_bundle",
             "nonoracle_masks", "online_masks", "oracle_masks", "best_sets", "masked_scan", "open_staging", "partition",
             "phase_record")
    for owner, name in ((np.linalg, "qr"), (pdb, "scan_statistic"), (pdb, "rank_threshold"), (pdb, "select_top_q"),
                        *((module, name) for name in names)):
        mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail("fit, geometry or staging in path_scores"))


def _b2m_producers(mp, arm, X, Y21):
    module, calls, exact = pio(), [], arm == "EXACT"
    right, wrong = ("exact_scores", "null_returns") if exact else ("null_returns", "exact_scores")

    def producer(*args):
        calls.append(args)
        return Y21 if exact else X

    _no_side_effects(mp)
    _b2m_forbid(mp)
    mp.setattr(module, wrong, lambda *args, **kwargs: pytest.fail(f"path_scores called {wrong} for {arm}"))
    mp.setattr(module, right, producer)
    return calls


@pytest.mark.parametrize("arm, application", B2M_CASES)
def test_path_scores_project_one_null_draw_and_shift_alt_paths_in_return_space(monkeypatch, arm, application):
    import inspect
    desc, frame, (X, Y21, delta) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    exact, columns = arm == "EXACT", [pc - 1 for pc in B2B_UNIVERSES[application]]
    fit = _b2m_copy(frame) if exact else _b2m_fit()
    keys = {"null": _b2j_path("CAL_NULL", 0, arm=arm), "alt": _b2j_path("ALT", 0, arm=arm)}
    shift = np.repeat(_b2m_project(delta, np.zeros(24), frame if exact else fit, application), 3, axis=0)
    if exact:
        expected = {"null": Y21[:, columns], "alt": Y21[:, columns] + shift}
    else:
        expected = {"null": _b2m_project(X, fit["mean"], fit, application),
                    "alt": _b2m_project(X + delta, fit["mean"], fit, application)}
        assert not np.allclose(expected["null"], _b2m_project(X, frame["mean"], fit, application))
    np.testing.assert_allclose(expected["alt"] - expected["null"], shift, rtol=0, atol=1e-12)
    assert set(keys.values()) <= set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert application in desc["scope"]["applications"] and len(columns) == 20
    assert (columns[0], columns[-1]) == {"RESIDUAL": (1, 20), "MARKET": (0, 19)}[application]
    assert all(np.array_equal(fit[name], frame[name]) for name in frame) is exact
    assert _kernel("_frozen_record")(fit, "fit")[1].size == _kernel("_frozen_record")(frame, "frame")[1].size == 24
    generate, snapshot = _kernel("path_scores"), pdb.canon(desc)
    signature = inspect.signature(generate).parameters
    assert list(signature) == ["desc", "frame", "fit", "application", "key", "delta"]
    assert signature["delta"].default is None
    arrays = [*frame.values(), *fit.values(), X, Y21, delta]
    kept = [array.tobytes() for array in arrays]
    for name, supplied in (("null", None), ("alt", delta)):
        with monkeypatch.context() as mp:
            calls = _b2m_producers(mp, arm, X, Y21)
            out = generate(desc, frame, fit, application, keys[name], supplied)
        assert len(calls) == 1 and len(calls[0]) == (2 if exact else 3) and calls[0][0] is desc
        assert calls[0][-1] == keys[name] and (exact or calls[0][1] is frame)
        assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (3, 20) and np.isfinite(out).all()
        np.testing.assert_allclose(out, expected[name], rtol=0, atol=1e-12)
    assert pdb.canon(desc) == snapshot and [array.tobytes() for array in arrays] == kept


@pytest.mark.parametrize("case", B2M_REFUSALS)
def test_path_scores_refuse_role_inconsistent_or_score_length_deltas_before_any_producer(monkeypatch, case):
    arm, role, kind = B2M_REFUSALS[case]
    desc, frame, (_, _, delta) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    fit, key = (_b2m_copy(frame) if arm == "EXACT" else _b2m_fit()), _b2j_path(role, 0, arm=arm)
    supplied = {"return": delta, "score": delta[:20], None: None}[kind]
    assert key in set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert "RESIDUAL" in desc["scope"]["applications"] and _kernel("_frozen_record")(fit, "fit")[1].size == 24
    assert _kernel("_frozen_record")(frame, "frame")[1].size == 24
    assert supplied is None or supplied.shape == {"return": (24,), "score": (20,)}[kind]
    module, generate, snapshot = pio(), _kernel("path_scores"), pdb.canon(desc)
    arrays = [*frame.values(), *fit.values(), delta]
    kept = [array.tobytes() for array in arrays]
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2m_forbid(mp)
        for name in ("null_returns", "exact_scores"):
            mp.setattr(module, name, lambda *args, **kwargs: pytest.fail("a producer ran before the delta check"))
        with pytest.raises(ValueError):
            generate(desc, frame, fit, "RESIDUAL", key, supplied)
    assert pdb.canon(desc) == snapshot and [array.tobytes() for array in arrays] == kept


B2M_ROLES = {"dev_alt_t7_market": ("FITTED_LW_T7", "MARKET", "DEV_ALT", 0, True),
             "dev_alt_exact_market": ("EXACT", "MARKET", "DEV_ALT", 0, True),
             "dev_null_exact_residual": ("EXACT", "RESIDUAL", "DEV_NULL", 0, False),
             "null_plan_primary_market": ("FITTED_LW_GAUSSIAN", "MARKET", "NULL_PLAN", 0, False),
             "hold_null_primary_cap_residual": ("FITTED_LW_GAUSSIAN", "RESIDUAL", "HOLD_NULL", 2, False)}
B2M_GROUPS = ("alternate_domains_and_tuples", "aliases_plan_caps_and_dimensions", "applications_and_records",
              "alt_deltas")


def _b2m_invalid(group):
    desc, frame, (_, _, delta) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    fit, exact_fit, base = _b2m_fit(), _b2m_copy(frame), _b2j_path("CAL_NULL", 0)
    exact_key, planned = _b2k_path("CAL_NULL", 0, N=24), set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert {base, exact_key} <= planned
    if group == "alternate_domains_and_tuples":
        other = {"fit_key": ("fit", "SMOKE", *B2J_PRIMARY), "meta_key": _b2l_meta("CAL_NULL", B2L_F2, 0),
                 "devlib_key": _b2l_devlib(B2L_F0, 0), "frame_key": ("frame", "SMOKE", 24)}
        assert set(other.values()) <= planned
        keys = {**other, "list_key": list(base), "empty_key": (), "none_key": None, "path_without_index": base[:6],
                "path_with_extra_word": (*base, 0)}
        return {name: (desc, frame, fit, "RESIDUAL", key, None) for name, key in keys.items()}
    if group == "aliases_plan_caps_and_dimensions":
        keys = {"n_float": _b2j_path(N=24.0), "fit_id_false": _b2j_path(fit_id=False),
                "index_float": _b2j_path(i=1.0), "campaign_pilot": _b2j_path(campaign="PILOT"),
                "fit_id_unplanned": _b2j_path(fit_id=2), "index_beyond_cap": _b2j_path(i=2),
                "arm_absent": _b2j_path(arm="FITTED_LW_T5")}
        assert {"n_float", "fit_id_false", "index_float"} == {name for name, key in keys.items() if key in planned}
        poisons = {"cap_string": (("sizes", "CAL_NULL"), "2"), "cap_bool": (("sizes", "CAL_NULL"), True),
                   "cap_float": (("sizes", "CAL_NULL"), 2.0), "seed_bool": (("seed",), True),
                   "k_float": (("science", "parameters", "K"), 20.0), "h_zero": (("science", "parameters", "H"), 0)}
        setups = [*map(list, B2J_SETUPS), *map(list, B2K_EXACT), ["EXACT", 20, 0]]
        n20_cfg, frame20, n20_key = _b2l_cfg((("scope", "setups"), setups)), _b2j_frame(20), _b2k_path(N=20)
        assert n20_key in set(_kernel("seed_plan")(n20_cfg, "smoke")["keys"])
        calls = {name: (desc, frame, fit, "RESIDUAL", key, None) for name, key in keys.items()}
        calls.update({name: (_edited(desc, field, value), frame, fit, "RESIDUAL", base, None)
                      for name, (field, value) in poisons.items()})
        n20 = _kernel("design_descriptor")(n20_cfg, "smoke")
        return {**calls, "exact_n20_planned": (n20, frame20, _b2m_copy(frame20), "MARKET", n20_key, None)}
    if group == "applications_and_records":
        narrow, noncanonical = _b2k_desc(), _edited(desc, ("science", "applications", "RESIDUAL"), [2, 20])
        assert narrow["scope"]["applications"] == ["RESIDUAL"] and "MARKET" in narrow["science"]["applications"]
        assert base in set(_kernel("seed_plan")(_b2k_cfg(), "smoke")["keys"])
        small, nan_mean = _b2j_frame(23), np.array(fit["mean"])
        nan_mean[3] = np.nan
        other_mean = {**exact_fit, "mean": exact_fit["mean"] + 1.0}
        records = {"application_typo": (desc, frame, fit, "residual", base),
                   "application_unscoped": (narrow, frame, fit, "MARKET", base),
                   "universe_noncanonical": (noncanonical, frame, fit, "RESIDUAL", base),
                   "frame_without_mean": (desc, {"V": frame["V"], "lam": frame["lam"]}, fit, "RESIDUAL", base),
                   "fit_extra_field": (desc, frame, {**fit, "basis_sha": "0" * 64}, "RESIDUAL", base),
                   "fit_dimension_23": (desc, frame, small, "RESIDUAL", base),
                   "frame_dimension_23": (desc, small, fit, "RESIDUAL", base),
                   "fit_increasing_lam": (desc, frame, {**fit, "lam": fit["lam"][::-1]}, "RESIDUAL", base),
                   "fit_nan_mean": (desc, frame, {**fit, "mean": nan_mean}, "RESIDUAL", base),
                   "exact_fit_other_mean": (desc, frame, other_mean, "RESIDUAL", exact_key),
                   "exact_fit_learned_basis": (desc, frame, fit, "RESIDUAL", exact_key)}
        return {name: (*call, None) for name, call in records.items()}
    nan_delta = np.array(delta)
    nan_delta[4] = np.nan
    alt, dev_alt = _b2j_path("ALT", 0), _b2j_path("DEV_ALT", 0, arm="FITTED_LW_T7")
    exact_alt = _b2k_path("ALT", 0, N=24)
    assert {alt, dev_alt, exact_alt} <= planned
    deltas = {"nan": (alt, nan_delta), "zero": (dev_alt, np.zeros(24)), "complex": (alt, delta + 0j),
              "bool": (dev_alt, delta > 0), "row_matrix": (alt, delta[None, :]),
              "too_long": (alt, np.append(delta, 1.0)), "exact_nan": (exact_alt, nan_delta),
              "exact_row_matrix": (exact_alt, delta[None, :])}
    return {name: (desc, frame, exact_fit if key[2] == "EXACT" else fit, "RESIDUAL", key, value)
            for name, (key, value) in deltas.items()}


@pytest.mark.parametrize("group", B2M_GROUPS)
def test_path_scores_refuse_invalid_keys_descriptors_records_or_alt_deltas_before_any_producer(monkeypatch, group):
    calls = _b2m_invalid(group)
    records = [record for call in calls.values() for record in call[1:3] if isinstance(record, dict)]
    arrays = [value for record in records for value in record.values() if isinstance(value, np.ndarray)]
    arrays += [call[5] for call in calls.values() if isinstance(call[5], np.ndarray)]
    kept, snapshots = [array.tobytes() for array in arrays], {name: pdb.canon(call[0]) for name, call in calls.items()}
    module, generate = pio(), _kernel("path_scores")
    for name, call in calls.items():
        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            _b2m_forbid(mp)
            for producer in ("null_returns", "exact_scores"):
                mp.setattr(module, producer, lambda *args, **kwargs: pytest.fail("a producer ran before validation"))
            with pytest.raises(ValueError):
                generate(*call)
                pytest.fail(f"{group}: {name} was accepted")
    assert {name: pdb.canon(call[0]) for name, call in calls.items()} == snapshots
    assert all(array.tobytes() == data for array, data in zip(arrays, kept))


@pytest.mark.parametrize("case", B2M_ROLES)
def test_path_scores_admit_remaining_null_and_dev_alt_roles_with_one_producer_call(monkeypatch, case):
    arm, application, role, index, shifted = B2M_ROLES[case]
    desc, frame, (X, Y21, delta) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    exact, columns = arm == "EXACT", [pc - 1 for pc in B2B_UNIVERSES[application]]
    fit, key = (_b2m_copy(frame) if exact else _b2m_fit()), _b2j_path(role, index, arm=arm)
    supplied = delta if shifted else None
    if exact:
        push = np.repeat(_b2m_project(delta, np.zeros(24), frame, application), 3, axis=0)
        expected = Y21[:, columns] + push if shifted else Y21[:, columns]
    else:
        expected = _b2m_project(X + delta if shifted else X, fit["mean"], fit, application)
    planned = set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert key in planned and _b2j_path(role, index + 1, arm=arm) not in planned
    assert application in desc["scope"]["applications"] and desc["science"]["phi"]["setup"] == list(B2J_PRIMARY)
    assert _kernel("_plan_applies")(desc) and (role in ("ALT", "DEV_ALT")) is shifted
    generate, snapshot = _kernel("path_scores"), pdb.canon(desc)
    arrays = [*frame.values(), *fit.values(), X, Y21, delta]
    kept = [array.tobytes() for array in arrays]
    with monkeypatch.context() as mp:
        calls = _b2m_producers(mp, arm, X, Y21)
        out = generate(desc, frame, fit, application, key, supplied)
    assert len(calls) == 1 and len(calls[0]) == (2 if exact else 3) and calls[0][0] is desc and calls[0][-1] == key
    assert exact or calls[0][1] is frame
    assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == (3, 20) and np.isfinite(out).all()
    np.testing.assert_allclose(out, expected, rtol=0, atol=1e-12)
    assert pdb.canon(desc) == snapshot and [array.tobytes() for array in arrays] == kept


def test_path_scores_replay_the_real_received_null_generators_in_any_order(tmp_path, monkeypatch):
    desc, frame, fit = _b2l_desc(), _b2j_frame(), _b2m_fit()
    exact_fit = _b2m_copy(frame)
    cases = [("EXACT", "RESIDUAL", "CAL_NULL", 1), ("EXACT", "MARKET", "HOLD_NULL", 0),
             ("FITTED_LW_GAUSSIAN", "RESIDUAL", "HOLD_NULL", 2), ("FITTED_LW_GAUSSIAN", "MARKET", "NULL_PLAN", 0),
             ("FITTED_LW_T7", "RESIDUAL", "DEV_NULL", 0), ("FITTED_LW_T7", "MARKET", "CAL_NULL", 1)]
    calls = [(exact_fit if arm == "EXACT" else fit, application, _b2j_path(role, index, arm=arm))
             for arm, application, role, index in cases]
    references = []
    for record, application, key in calls:
        columns = [pc - 1 for pc in B2B_UNIVERSES[application]]
        if key[2] == "EXACT":
            references.append(_kernel("exact_scores")(desc, key)[:, columns])
        else:
            returns = _kernel("null_returns")(desc, frame, key)
            references.append(_b2m_project(returns, record["mean"], record, application))
    assert {key for _, _, key in calls} <= set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    generate, state, t_innov = _kernel("path_scores"), np.random.get_state(), pdb.sim.t_innov
    with monkeypatch.context() as mp:
        _b2m_forbid(mp)
        mp.setattr(pdb.sim, "t_innov", t_innov)
        first = [generate(desc, frame, record, application, key) for record, application, key in calls]
        mp.chdir(tmp_path)
        again = [generate(desc, frame, record, application, key) for record, application, key in calls[::-1]][::-1]
    assert _b2j_same_state(state, np.random.get_state())
    for out, replay, reference in zip(first, again, references):
        assert out.dtype == np.float64 and out.shape == (3, 20) and np.array_equal(out, replay)
        np.testing.assert_allclose(out, reference, rtol=0, atol=1e-12)


def test_path_scores_keep_one_supplied_return_delta_under_two_distinct_frozen_fits(monkeypatch):
    desc, frame, (X, Y21, delta) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    rolled = _b2m_record(_b2d_frame(24)[:, [*range(1, 24), 0]], np.linspace(12.0, 0.5, 24), np.linspace(-0.4, 0.9, 24))
    fits, application, kept = [_b2m_fit(), rolled], "MARKET", delta.tobytes()
    keys = {"null": _b2j_path("DEV_NULL", 0), "alt": _b2j_path("DEV_ALT", 0)}
    shifts = [_b2m_project(delta, np.zeros(24), fit, application) for fit in fits]
    oracle = _b2m_project(delta, np.zeros(24), frame, application)
    assert set(keys.values()) <= set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert not any(np.array_equal(fits[0][name], fits[1][name]) for name in ("V", "lam", "mean"))
    assert not np.allclose(shifts[0], shifts[1]) and not any(np.allclose(shift, oracle) for shift in shifts)
    generate = _kernel("path_scores")
    for fit, shift in zip(fits, shifts):
        outputs = {}
        for name, supplied in (("null", None), ("alt", delta)):
            with monkeypatch.context() as mp:
                calls = _b2m_producers(mp, "FITTED_LW_GAUSSIAN", X, Y21)
                outputs[name] = generate(desc, frame, fit, application, keys[name], supplied)
            assert len(calls) == 1 and calls[0][0] is desc and calls[0][1] is frame and calls[0][2] == keys[name]
        null_reference, alt_reference = (_b2m_project(rows, fit["mean"], fit, application) for rows in (X, X + delta))
        np.testing.assert_allclose(outputs["null"], null_reference, rtol=0, atol=1e-12)
        np.testing.assert_allclose(outputs["alt"], alt_reference, rtol=0, atol=1e-12)
        np.testing.assert_allclose(outputs["alt"] - outputs["null"], np.repeat(shift, 3, axis=0), rtol=0, atol=1e-12)
    assert delta.tobytes() == kept and not delta.flags.writeable


def test_path_scores_check_combined_observations_after_one_draw_without_a_standalone_delta_projection(monkeypatch):
    desc, frame, (_, Y21, _) = _b2l_desc(), _b2j_frame(), _b2m_arrays()
    fit = _b2m_record(_b2d_frame(24).copy(), np.linspace(1.0, 0.1, 24), np.linspace(0.5, -0.25, 24))
    key, application, W = _b2j_path("ALT", 0), "MARKET", fit["V"][:, :20] / np.sqrt(fit["lam"][:20])
    runs = {"moderate": (np.full((3, 24), 0.25), np.linspace(0.5, -0.5, 24)),
            "cancelling": (np.full((3, 24), -1.5e308), np.full(24, 1.5e308)),
            "overflowing": (np.full((3, 24), 1.5e308), np.full(24, 1.5e308))}
    for X, delta in runs.values():
        X.flags.writeable = delta.flags.writeable = False
    (cancel_X, cancel_delta), (over_X, over_delta) = runs["cancelling"], runs["overflowing"]
    with np.errstate(over="ignore", invalid="ignore"):
        assert all(np.isfinite(X).all() and np.isfinite(delta).all() and delta.all() for X, delta in runs.values())
        assert not np.isfinite(cancel_delta @ W).all() and not (cancel_X + cancel_delta).any()
        assert not np.isfinite(over_X + over_delta).all()
    references = {name: _b2m_project(runs[name][0] + runs[name][1], fit["mean"], fit, application)
                  for name in ("moderate", "cancelling")}
    assert key in set(_kernel("seed_plan")(_b2l_cfg(), "smoke")["keys"])
    assert _kernel("_frozen_record")(fit, "fit")[1].size == 24 and application in desc["scope"]["applications"]
    generate = _kernel("path_scores")
    for name, (X, delta) in runs.items():
        kept = [array.tobytes() for array in (X, delta, *fit.values())]
        with monkeypatch.context() as mp:
            calls = _b2m_producers(mp, "FITTED_LW_GAUSSIAN", X, Y21)
            if name == "overflowing":
                with pytest.raises(ValueError):
                    generate(desc, frame, fit, application, key, delta)
            else:
                out = generate(desc, frame, fit, application, key, delta)
                assert out.dtype == np.float64 and out.shape == (3, 20) and np.isfinite(out).all(), name
                np.testing.assert_allclose(out, references[name], rtol=0, atol=1e-12)
        assert len(calls) == 1 and calls[0][1] is frame and calls[0][2] == key, name
        assert [array.tobytes() for array in (X, delta, *fit.values())] == kept, name


def test_projection_diagnostics_return_received_gaussian_numbers_labelled_as_a_t7_proxy(monkeypatch):
    frame, fits, E, deltas = _b2e_fitted()
    references = [_b2e_reference(frame, fit, E, deltas) for fit in fits]
    for ref, expected in zip(references, B2E_EXPECTED):
        for key in ("A", "C0", "c", "beta", "q"):
            np.testing.assert_allclose(ref[key], expected[key], rtol=1e-12, atol=1e-15)
    arrays = [*frame.values(), *(array for fit in fits for array in fit.values()), deltas]
    for array in arrays:
        array.flags.writeable = False
    kept, state, module = [array.tobytes() for array in arrays], np.random.get_state(), pio()
    diagnostics = _kernel("projection_diagnostics")
    gaussian = [diagnostics(frame, fit, E, deltas, "FITTED_LW_GAUSSIAN") for fit in fits]
    assert all(out["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE" for out in gaussian)

    def forbidden(*args, **kwargs):
        pytest.fail("fit, drift synthesis, geometry, selection or t7 sampling inside the T7 projection proxy")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for owner, name in ((module, "population_frame"), (module, "population_drift"), (module, "head_geometry"),
                            (module, "best_sets"), (module, "online_masks"), (module, "nonoracle_masks"),
                            (pdb, "fit_basis"), (pdb, "select_top_q"), (pdb.sim, "t_innov"), (np.linalg, "qr"),
                            (np.linalg, "eigh"), (np.linalg, "svd")):
            mp.setattr(owner, name, forbidden)
        proxies = [diagnostics(frame, fit, E, deltas, "FITTED_LW_T7") for fit in fits]
        empty = diagnostics(frame, fits[0], E, deltas[:0], "FITTED_LW_T7")
        base = {"frame": frame, "fit": fits[0], "eligible": E, "deltas": deltas, "arm": "FITTED_LW_T7"}
        for change in ({"deltas": np.vstack([deltas[:1], np.full((1, 4), np.nan)])}, {"arm": "fitted_lw_t7"},
                       {"eligible": [2.0, 3]}, {"fit": {**fits[0], "lam": fits[0]["lam"][::-1]}}):
            with pytest.raises(ValueError):
                diagnostics(**{**base, **change})
    assert _kernel("INFO_BASES") == ("EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_SURROGATE", "ORACLE_DIAGONAL_GAUSSIAN_PROXY")
    for proxy, received, ref in zip(proxies, gaussian, references):
        assert set(proxy) == set(B2E_FIELDS) and proxy["oracle_basis"] == "ORACLE_DIAGONAL_GAUSSIAN_PROXY"
        assert all(np.array_equal(proxy[key], received[key]) for key in B2E_FIELDS[:-1])
        for key in ("A", "C0", "c", "beta", "q"):
            np.testing.assert_allclose(proxy[key], ref[key], rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(proxy["I_joint"], [1.0, 0.5, 0.0, 0.0], rtol=1e-12, atol=1e-15)
        assert abs(proxy["q"][0].sum() - proxy["I_joint"][0]) > 0.4 and not proxy["I_joint"][2:].any()
    assert set(empty) == set(B2E_FIELDS) and empty["oracle_basis"] == "ORACLE_DIAGONAL_GAUSSIAN_PROXY"
    assert empty["beta"].shape == empty["q"].shape == (0, 2) and empty["I_joint"].shape == (0,)
    assert all(array.tobytes() == data and not array.flags.writeable for array, data in zip(arrays, kept))
    assert _b2j_same_state(state, np.random.get_state())


def test_export_selections_round_trips_the_t7_gaussian_proxy_label_in_the_received_schema(tmp_path, monkeypatch):
    import hashlib
    import pandas
    from jepadrift import pipelines
    export, out, entries = _kernel("export_selections"), tmp_path / "out", _b1h_entries()
    entries.append({"setup": "FITTED_LW_T7|24|0", "policy": "ORACLE_INFO_MIX", "family": "F2_STRUCTURED_RESIDUAL",
                    "info_basis": "ORACLE_DIAGONAL_GAUSSIAN_PROXY", "gamma_M": 504.0,
                    "masks": _b1h_frozen([[0, 1, 0, 0, 1], [0, 1, 0, 0, 0]], bool),
                    "q": _b1h_frozen([0.0, 0.375, 0.0, 0.0, 0.125], float)})
    before, refs = _b1h_plain(entries), [_b1h_reference(entry)[0] for entry in entries]
    out.mkdir()
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        for owner, name in ((pio(), "best_sets"), (pio(), "online_masks"), (pio(), "masked_scan"),
                            (pio(), "projection_diagnostics"), (pdb, "fit_basis"), (pdb, "q_plugin"), (pdb, "kl_mean")):
            mp.setattr(owner, name, lambda *args, **kwargs: pytest.fail("projection inside the exporter"))
        sha = export(out, "ab" * 32, entries)
    path = out / "selections.csv"
    data, frame = path.read_bytes(), pandas.read_csv(path, float_precision="round_trip")
    rows = frame.to_dict("records")
    assert sha == hashlib.sha256(data).hexdigest() and set(_tree(out)) == {"selections.csv"} and b"STUDENT" not in data
    assert _b1h_plain(entries) == before and list(frame.columns) == B1H_COLUMNS and len(rows) == len(entries) == 5
    assert [row["info_basis"] for row in rows] == [entry["info_basis"] for entry in entries]
    assert set(frame["metric_basis"]) == {"ANALYTIC_PROXY"} and rows[-1]["setup"] == "FITTED_LW_T7|24|0"
    for row, entry, ref in zip(rows, entries, refs):
        assert [row[c] for c in ("gamma_M", "horizon")] == [entry["gamma_M"], ref["horizon"]]
        assert all(row[c] == pytest.approx(ref[c], rel=1e-12, abs=0.0) for c in B1H_COLUMNS[8:])
    pipelines.save_fair_csv(frame, tmp_path / "again.csv")
    assert (tmp_path / "again.csv").read_bytes() == data


def test_export_selections_refuse_unknown_t7_information_labels_without_writing(tmp_path, monkeypatch):
    import pandas
    export, entries, bad, good = _kernel("export_selections"), _b1h_entries(), tmp_path / "bad", tmp_path / "good"
    t7 = {**entries[-1], "setup": "FITTED_LW_T7|24|0"}
    labels = ("ORACLE_DIAGONAL_STUDENT_T_KL", "GAUSSIAN_PROXY", "oracle_diagonal_gaussian_proxy", "EXACT_T7_KL")
    bad.mkdir()
    good.mkdir()
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for label in labels:
            with pytest.raises(ValueError):
                export(bad, "ab" * 32, [{**t7, "info_basis": label}])
    assert not any(bad.iterdir())
    export(good, "ab" * 32, entries)
    frame = pandas.read_csv(good / "selections.csv", float_precision="round_trip")
    assert list(frame["info_basis"]) == [entry["info_basis"] for entry in entries]
    assert set(frame["info_basis"]) == {"EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_SURROGATE"}


def test_setup_bundle_admits_a_planned_t7_setup_as_a_fitted_gaussian_proxy(monkeypatch):
    setups = [["EXACT", 24, 0], ["FITTED_LW_GAUSSIAN", 24, 0], ["FITTED_LW_T7", 24, 0]]
    desc, frame, rows = _b2h_desc((("scope", "setups"), setups)), _b2h_frame(), np.vstack([np.eye(24), -np.eye(24)])
    fits = {"base": _b2h_fit(B2H_PERMS["aligned"]), "shifted": _b2h_fit(B2H_PERMS["aligned"], 0.25)}
    did, basis = _kernel("design_id")(desc), pdb.array_sha256(frame["V"], frame["lam"], frame["mean"])
    hashes = {name: pdb.array_sha256(fit["V"], fit["lam"], fit["mean"]) for name, fit in fits.items()}
    assert ["FITTED_LW_T7", 24, 0] in desc["scope"]["setups"]
    assert desc["scope"]["applications"] == ["RESIDUAL", "MARKET"] and hashes["base"] != hashes["shifted"]
    assert rows.shape == (desc["science"]["parameters"]["T_fit"], 24)
    module, bundle = pio(), _kernel("setup_bundle")
    arrays = [*frame.values(), rows, *(array for fit in fits.values() for array in fit.values())]
    for array in arrays:
        array.flags.writeable = False
    kept, snapshot, runs = [array.tobytes() for array in arrays], pdb.canon(desc), {}

    def forbidden(*args, **kwargs):
        pytest.fail("fit, noise, path, selection or calibration inside the supplied-input SETUP bundle")

    for name, arm, fit in (("gaussian", "FITTED_LW_GAUSSIAN", fits["base"]), ("t7", "FITTED_LW_T7", fits["base"]),
                           ("t7_shifted", "FITTED_LW_T7", fits["shifted"])):
        calls = []

        def fit_spy(X_fit, K, fit=fit, calls=calls):
            calls.append((X_fit.tobytes(), K, type(K)))
            return fit

        with monkeypatch.context() as mp:
            _no_side_effects(mp)
            mp.setattr(module, "fit_record", fit_spy)
            for owner, attr in ((module, "population_frame"), (module, "null_returns"), (module, "exact_scores"),
                                (module, "path_scores"), (module, "direction_draws"), (module, "best_sets"),
                                (module, "online_masks"), (module, "nonoracle_masks"), (module, "oracle_masks"),
                                (module, "masked_scan"), (pdb, "fit_basis"), (pdb, "select_top_q"),
                                (pdb, "scan_statistic"), (pdb, "rank_threshold"), (pdb.sim, "t_innov")):
                mp.setattr(owner, attr, forbidden)
            runs[name] = bundle(desc, frame, rows, [arm, 24, 0])
        assert calls == [(rows.tobytes(), 20, int)], name
    gaussian, t7, shifted = (runs[name]["metadata"] for name in ("gaussian", "t7", "t7_shifted"))
    assert set(gaussian) == {"design_id", "setup", "basis_sha", "fit_hash", "applications"}
    assert set(t7) == set(shifted) == set(gaussian) | {"information_basis"}
    assert t7["information_basis"] == shifted["information_basis"] == "GAUSSIAN_PROXY" and t7["setup"] == setups[2]
    assert [t7[key] for key in ("design_id", "basis_sha", "fit_hash")] == [did, basis, hashes["base"]]
    assert gaussian["fit_hash"] == t7["fit_hash"] != shifted["fit_hash"] == hashes["shifted"]
    for app in ("RESIDUAL", "MARKET"):
        entry, received, moved = t7["applications"][app], gaussian["applications"][app], shifted["applications"][app]
        baselines = _kernel("spectral_baselines")(fits["base"]["lam"], app)["baselines"]
        assert set(entry) == set(received) == {"universe", "setup_id", "baselines", "head"}
        assert entry["universe"] == received["universe"] == B2B_UNIVERSES[app]
        assert entry["baselines"] == received["baselines"] == baselines and entry["head"] == received["head"]
        assert entry["setup_id"] == _b2h_setup_id(did, setups[2], app, basis, hashes["base"]) != received["setup_id"]
        assert moved["setup_id"] == _b2h_setup_id(did, setups[2], app, basis, hashes["shifted"]) != entry["setup_id"]
    assert t7["applications"]["RESIDUAL"]["head"]["status"] == "GEOMETRY_ALIGNED"
    assert t7["applications"]["MARKET"]["head"] == {"status": "NOT_APPLICABLE", "kappa_geo": None, "geometry": None}
    assert all(np.array_equal(runs["t7"]["fit"][key], fits["base"][key]) for key in ("V", "lam", "mean"))
    assert pdb.canon(desc) == snapshot and all(array.tobytes() == data for array, data in zip(arrays, kept))


def test_setup_bundle_still_refuses_the_planned_unknown_arm_of_the_disposed_case_before_any_fit(monkeypatch):
    call = _b2h_refusal("arm_unsupported_planned")
    planned = [pdb.canon(setup) for setup in call["desc"]["scope"]["setups"]]
    assert call["setup"] == ["FITTED_LW_PLAIN", 24, 0] and pdb.canon(call["setup"]) in planned
    assert pdb.canon(["FITTED_LW_T7", 24, 0]) not in planned and len(B2H_REFUSALS) == 13
    assert "arm_unsupported_planned" in B2H_REFUSALS and "arm_unsupported_t7" not in B2H_REFUSALS
    module, bundle, calls = pio(), _kernel("setup_bundle"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        mp.setattr(module, "fit_record", lambda X_fit, K: calls.append(K))
        with pytest.raises(ValueError):
            bundle(**call)
    assert not calls and call["setup"] == ["FITTED_LW_PLAIN", 24, 0]


B2O_SETUPS = (("EXACT", 24, 0), ("FITTED_LW_GAUSSIAN", 24, 0), ("FITTED_LW_T7", 24, 0))
B2O_FITTED = ("FITTED_LW_GAUSSIAN", "FITTED_LW_T7")
B2O_KEYS = [["fit", "FULL", "FITTED_LW_GAUSSIAN", 24, 0], ["fit", "FULL", "FITTED_LW_T7", 24, 0],
            ["frame", "FULL", 24]]


def _b2o_frame():
    return {"V": np.eye(24), "lam": _b2b_spectrum(24), "mean": np.zeros(24)}


def _b2o_rows(arm):
    rows = np.vstack([np.eye(24), -np.eye(24)]) * (2.0 if arm == "FITTED_LW_T7" else 1.0)
    rows.flags.writeable = False
    return rows


def _b2o_fit(arm):
    return _b2h_fit(B2H_PERMS["aligned"], 0.25 if arm == "FITTED_LW_T7" else 0.0)


def _b2o_fixture(root, monkeypatch):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2O_SETUPS]),
                        (("scope", "applications"), ["RESIDUAL", "MARKET"]), (("parameters", "T_fit"), 48)):
        cfg = _edited(cfg, path, value)
    cfg = _authorized(root, monkeypatch, cfg, "full")[0]
    desc, primitive = _kernel("design_descriptor")(cfg, "full"), _kernel("seed_plan")(cfg, "full")["keys"]
    keys = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    plan = {phase: keys if phase == "SETUP" else [] for phase in _kernel("PHASES")}
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")("full", cfg, desc, 1), plan, staging


def _b2o_references(desc, monkeypatch):
    module, bundle, refs = pio(), _kernel("setup_bundle"), {}
    for setup in desc["scope"]["setups"]:
        rows = None if setup[0] == "EXACT" else _b2o_rows(setup[0])
        with monkeypatch.context() as mp:
            mp.setattr(module, "fit_record", lambda X_fit, K, arm=setup[0]: _b2o_fit(arm))
            refs[pdb.canon(setup)] = bundle(desc, _b2o_frame(), rows, setup)["metadata"]
    return refs


def _b2o_fakes(mp, state, log, want_cfg, want_desc):
    module = pio()
    real_head = module.head_geometry

    def population_frame(cfg, mode, N):
        assert pdb.canon(cfg) == pdb.canon(want_cfg) and mode == "full" and type(N) is int and N == 24
        log.append(("frame", N))
        state["cpu"] += 1.0
        return np.eye(24), _b2b_spectrum(24)

    def null_returns(desc, frame, key):
        assert pdb.canon(desc) == pdb.canon(want_desc) and type(key) is tuple and len(key) == 5
        assert all(type(part) is int for part in key[3:]) and _same_arrays(frame, _b2o_frame())
        log.append(("noise", *key))
        state["cpu"] += 0.5
        return _b2o_rows(key[2])

    def fit_record(X_fit, K):
        arms = [arm for arm in B2O_FITTED if np.array_equal(X_fit, _b2o_rows(arm))]
        assert type(K) is int and K == 20 and len(arms) == 1
        log.append(("fit", arms[0]))
        state["cpu"] += 2.0
        return _b2o_fit(arms[0])

    def head_geometry(frame, fit, istar, universe):
        log.append(("head", pdb.array_sha256(fit["V"], fit["lam"], fit["mean"])))
        return real_head(frame, fit, istar, universe)

    for fake in (population_frame, null_returns, fit_record, head_geometry):
        mp.setattr(module, fake.__name__, fake)


def _b2o_forbid(mp):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("frame, noise, fit, HEAD, baseline or bundle recomputation inside setup_phase")

    for owner, name in ((module, "population_frame"), (module, "null_returns"), (module, "fit_record"),
                        (module, "head_geometry"), (module, "spectral_baselines"), (module, "setup_bundle"),
                        (module, "exact_scores"), (pdb, "fit_basis"), (pdb.sim, "t_innov")):
        mp.setattr(owner, name, forbidden)


def _b2o_run(monkeypatch, state, log, fixture, token):
    cfg, desc, authority, plan, staging = fixture
    setup, start = _kernel("setup_phase"), _kernel("start_invocation")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _b2o_fakes(mp, state, log, cfg, desc)
        return setup(cfg, "full", start(staging, authority, plan, token))


def test_setup_phase_caches_one_frame_then_two_fits_and_commits_the_received_metadata(tmp_path, monkeypatch):
    import hashlib
    import io
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, refs, keys = _kernel("design_id")(desc), _b2o_references(desc, monkeypatch), plan["SETUP"]
    fits, state, log = {arm: _b2o_fit(arm) for arm in B2O_FITTED}, {"cpu": 10.0, "wall": 100.0}, []
    hashes = [pdb.array_sha256(fit["V"], fit["lam"], fit["mean"]) for fit in fits.values()]
    basis = pdb.array_sha256(*_b2o_frame().values())
    exact, gaussian, t7 = (pdb.canon(list(setup)) for setup in B2O_SETUPS)
    statuses = {key: meta["applications"]["RESIDUAL"]["head"]["status"] for key, meta in refs.items()}
    assert keys == B2O_KEYS and authority["go_reference"]["path"] == "prompts/GO-full-fixture.md"
    assert set(refs) == {exact, gaussian, t7} and statuses == dict.fromkeys(refs, "GEOMETRY_ALIGNED")
    assert [refs[key]["fit_hash"] for key in (exact, gaussian, t7)] == [None, *hashes] and len(set(hashes)) == 2
    assert all(np.array_equal(fits["FITTED_LW_GAUSSIAN"][k], fits["FITTED_LW_T7"][k]) for k in ("V", "lam"))
    assert {meta["basis_sha"] for meta in refs.values()} == {basis} and "information_basis" not in refs[gaussian]
    assert refs[t7]["information_basis"] == "GAUSSIAN_PROXY"
    assert all(list(meta["applications"]) == ["RESIDUAL", "MARKET"] for meta in refs.values())
    record = _b2o_run(monkeypatch, state, log, fixture, "invocation-1")
    calls = [("frame", 24), ("noise", "fit", "FULL", "FITTED_LW_GAUSSIAN", 24, 0), ("fit", "FITTED_LW_GAUSSIAN"),
             ("noise", "fit", "FULL", "FITTED_LW_T7", 24, 0), ("fit", "FITTED_LW_T7")]
    heads = sorted(entry for entry in log if entry[0] == "head")
    assert log[:5] == calls and len(log) == 8 and heads == sorted(("head", sha) for sha in (basis, *hashes))
    rows = []
    for key in keys:
        stem = _partition_stem(staging, did, {}, key)
        data = stem.with_suffix(".npz").read_bytes()
        sha, want = hashlib.sha256(data).hexdigest(), _b2o_frame() if key[0] == "frame" else fits[key[2]]
        with np.load(io.BytesIO(data), allow_pickle=False) as archive:
            arrays = {name: archive[name] for name in archive.files}
        sidecar = {"design_id": did, "key": key, "upstream": {}, "fingerprint": stem.name,
                   "payload_sha256": sha, "n_rows": 24}
        assert json.loads(stem.with_suffix(".json").read_text()) == sidecar and _same_arrays(arrays, want), key
        rows.append({"key": key, "sha256": sha, "n_rows": 24})
    derived = {"setups": refs}
    pairs = sorted([pdb.canon(row["key"]), row["sha256"]] for row in rows)
    identity = {"design_id": did, "phase": "SETUP", "upstream": {}, "partitions": pairs, "derived": derived}
    expected = {"design_id": did, "phase": "SETUP", "upstream": {}, "partitions": rows, "derived": derived,
                "phase_digest": hashlib.sha256(pdb.canon(identity).encode()).hexdigest()}
    assert record == expected == json.loads((staging / "phases" / "SETUP.json").read_text())
    assert _kernel("phase_record")(staging, "SETUP", {}, None, None) == record
    stems = [_partition_stem(staging, did, {}, key).name for key in keys]
    files = {"design.json", "resources.json", "phases/SETUP.json", *(f"partitions/{s}.npz" for s in stems),
             *(f"partitions/{s}.json" for s in stems)}
    outside = {name for name in _tree(tmp_path) if not name.startswith(f"logs/staging/{did[:16]}/")}
    assert set(_tree(staging)) == files and outside == {"prompts/GO-full-fixture.md"}
    journal = json.loads((staging / "resources.json").read_text())
    assert journal == {"design_id": did, "cpu_seconds": {"invocation-1": 6.0}}


def test_setup_phase_reloads_the_committed_setup_without_callbacks_or_scientific_rewrites(tmp_path, monkeypatch):
    import json
    import os
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    refs, state, log, replaced = _b2o_references(desc, monkeypatch), {"cpu": 10.0, "wall": 100.0}, [], []
    real_replace = os.replace

    def watched(src, dst, *args, **kwargs):
        replaced.append(os.path.basename(dst))
        return real_replace(src, dst, *args, **kwargs)

    assert plan["SETUP"] == B2O_KEYS and len(refs) == 3
    first = _b2o_run(monkeypatch, state, log, fixture, "invocation-1")
    before, setup = _tree(staging), _kernel("setup_phase")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        mp.setattr(os, "replace", watched)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
        again, twice = setup(cfg, "full", context), setup(json.loads(json.dumps(cfg)), "full", context)
    after = _tree(staging)
    assert first == again == twice == json.loads(after["phases/SETUP.json"]) and first["derived"] == {"setups": refs}
    assert len(log) == 8 and set(replaced) == {"resources.json"} and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    assert json.loads(after["resources.json"])["cpu_seconds"] == {"invocation-1": 6.0, "invocation-2": 0.0}


def test_setup_phase_refuses_a_canonical_setup_plan_missing_one_fit_key_before_any_effect(tmp_path, monkeypatch):
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, _, authority, plan, staging = fixture
    validated, state = _kernel("_validated_plan"), {"cpu": 10.0, "wall": 100.0}
    short = {**plan, "SETUP": [key for key in plan["SETUP"] if key[2] != "FITTED_LW_T7"]}
    assert plan["SETUP"] == B2O_KEYS and short["SETUP"] == [B2O_KEYS[0], B2O_KEYS[2]]
    assert validated(plan) is None and validated(short) is None
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    before, setup, poisoned = _tree(tmp_path), _kernel("setup_phase"), {**context, "plan": short}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1m_clock(mp, state)
        _b2o_forbid(mp)
        with pytest.raises(ValueError):
            setup(cfg, "full", poisoned)
    assert _tree(tmp_path) == before and set(_tree(staging)) == {"design.json", "resources.json"}


def _b2o_market(root, monkeypatch):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2O_SETUPS]),
                        (("scope", "applications"), ["MARKET"]), (("parameters", "T_fit"), 48)):
        cfg = _edited(cfg, path, value)
    cfg = _authorized(root, monkeypatch, cfg, "full")[0]
    desc, primitive = _kernel("design_descriptor")(cfg, "full"), _kernel("seed_plan")(cfg, "full")["keys"]
    keys = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    plan = {phase: keys if phase == "SETUP" else [] for phase in _kernel("PHASES")}
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")("full", cfg, desc, 1), plan, staging


def _b2o_cache(staging, key, arrays):
    return _kernel("partition")(staging, "SETUP", {}, key, lambda: arrays)


def _b2o_refused(monkeypatch, state, fixture, context, error):
    import json
    import os
    cfg, staging, replaced, real_replace = fixture[0], fixture[4], [], os.replace

    def watched(src, dst, *args, **kwargs):
        replaced.append(os.path.basename(dst))
        return real_replace(src, dst, *args, **kwargs)

    before, setup = _tree(staging), _kernel("setup_phase")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        mp.setattr(os, "replace", watched)
        with pytest.raises(error):
            setup(cfg, "full", context)
    after = _tree(staging)
    assert set(replaced) <= {"resources.json"} and set(after) == set(before) and "status.json" not in after
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    assert set(json.loads(after["resources.json"])["cpu_seconds"]) == {context["token"]}


def test_setup_phase_verifies_every_pending_cache_before_producing_a_missing_fit(tmp_path, monkeypatch):
    import hashlib
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, state, (gaussian, t7, frame) = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, B2O_KEYS
    verify, mismatch = _kernel("_verify_partition"), _kernel("PartitionMismatch")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    cached = {pdb.canon(frame): _b2o_frame(), pdb.canon(t7): _b2o_fit("FITTED_LW_T7")}
    for key in (frame, t7):
        _b2o_cache(staging, key, cached[pdb.canon(key)])
    progress = _kernel("_planned_progress")(staging, did, desc, plan, None)
    assert plan["SETUP"] == B2O_KEYS and progress == ({}, [{"phase": "SETUP", "key": gaussian}])
    assert all(_same_arrays(verify(staging, did, {}, key)[2], cached[pdb.canon(key)]) for key in (frame, t7))
    npz, sidecar = (_partition_stem(staging, did, {}, t7).with_suffix(ext) for ext in (".npz", ".json"))
    npz.write_bytes(npz.read_bytes() + b"x")
    assert json.loads(sidecar.read_text())["payload_sha256"] != hashlib.sha256(npz.read_bytes()).hexdigest()
    with pytest.raises(mismatch):
        verify(staging, did, {}, t7)
    _b2o_refused(monkeypatch, state, fixture, context, mismatch)


def test_setup_phase_refuses_a_dev_record_whose_setup_predecessor_was_removed(tmp_path, monkeypatch):
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    record, order, progress = _kernel("phase_record"), _kernel("PhaseOrderError"), _kernel("_planned_progress")
    did, refs, state = _kernel("design_id")(desc), _b2o_references(desc, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    dev_key = ["DEV_NULL", "FITTED_LW_GAUSSIAN", 24, 0, "maxima"]
    plan = {**plan, "DEV": [dev_key]}
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    lineage = {"SETUP": record(staging, "SETUP", {}, B2O_KEYS, {"setups": refs})["phase_digest"]}
    _kernel("partition")(staging, "DEV", lineage, dev_key, lambda: {"w_max": np.array([0.5])})
    dev = record(staging, "DEV", lineage, [dev_key], {"d_dev": 4})
    records, missing = progress(staging, did, desc, plan, None)
    assert dev["upstream"] == lineage and record(staging, "DEV", None, None, None) == dev
    assert list(records) == ["SETUP", "DEV"] and records["DEV"] == dev and missing == []
    (staging / "phases" / "SETUP.json").unlink()
    assert sorted(path.name for path in (staging / "phases").iterdir()) == ["DEV.json"]
    with pytest.raises(order):
        record(staging, "DEV", None, None, None)
    with pytest.raises(order):
        progress(staging, did, desc, plan, None)
    _b2o_refused(monkeypatch, state, fixture, context, order)


def test_setup_phase_refuses_a_storage_consistent_fit_cache_whose_basis_is_not_square(tmp_path, monkeypatch):
    fixture = _b2o_market(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, state, (gaussian, t7, frame) = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, B2O_KEYS
    verify, frozen = _kernel("_verify_partition"), _kernel("_frozen_record")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    bad = {**_b2o_fit("FITTED_LW_GAUSSIAN"), "V": np.eye(24, 23)}
    for key, arrays in ((gaussian, bad), (t7, _b2o_fit("FITTED_LW_T7")), (frame, _b2o_frame())):
        _b2o_cache(staging, key, arrays)
    _, rows, arrays = verify(staging, did, {}, gaussian)
    assert desc["scope"]["applications"] == ["MARKET"] and plan["SETUP"] == B2O_KEYS
    assert rows == 24 and arrays["V"].shape == (24, 23) and _same_arrays(arrays, bad)
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, [])
    assert [frozen(verify(staging, did, {}, key)[2], key[0])[1].size for key in (t7, frame)] == [24, 24]
    with pytest.raises(ValueError):
        frozen(arrays, "fit")
    _b2o_refused(monkeypatch, state, fixture, context, _kernel("PartitionMismatch"))


def test_setup_phase_refuses_a_valid_frame_record_stored_under_another_planned_n(tmp_path, monkeypatch):
    fixture = _b2o_market(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, state, (gaussian, t7, frame) = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, B2O_KEYS
    verify, frozen = _kernel("_verify_partition"), _kernel("_frozen_record")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    wide = {"V": np.eye(25), "lam": _b2b_spectrum(25), "mean": np.zeros(25)}
    for key, arrays in ((gaussian, _b2o_fit("FITTED_LW_GAUSSIAN")), (t7, _b2o_fit("FITTED_LW_T7")), (frame, wide)):
        _b2o_cache(staging, key, arrays)
    _, rows, arrays = verify(staging, did, {}, frame)
    lam = frozen(arrays, "frame")[1]
    assert desc["scope"]["applications"] == ["MARKET"] and plan["SETUP"] == B2O_KEYS and frame[2] == 24
    assert rows == lam.size == 25 and _same_arrays(arrays, wide)
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, [])
    assert [frozen(verify(staging, did, {}, key)[2], "fit")[1].size for key in (gaussian, t7)] == [24, 24]
    _b2o_refused(monkeypatch, state, fixture, context, _kernel("PartitionMismatch"))


def test_setup_phase_checkpoints_cached_validation_cpu_before_the_budget_gate_of_metadata(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    module, setup, real = pio(), _kernel("setup_phase"), _kernel("_setup_cache")
    did, state, verify = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, _kernel("_verify_partition")
    cap, bumped = desc["envelope"]["cpu_hours_max"] * 3600, []
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, []) and cap == 14400.0
    assert all(real(verify(staging, did, {}, key)[2], key)["lam"].size == 24 for key in B2O_KEYS)
    before = _tree(staging)

    def measured(arrays, key):
        checked = real(arrays, key)
        if not bumped:
            state["cpu"] += cap + 1.0
        bumped.append(key)
        return checked

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        mp.setattr(module, "_setup_cache", measured)
        with pytest.raises(_kernel("ResourceBlocked")):
            setup(cfg, "full", context)
    after, elapsed = _tree(staging), state["cpu"] - context["cpu_start"]
    status = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": None, "missing_partitions": []}
    assert bumped and elapsed >= cap and set(after) == set(before) | {"status.json"}
    assert json.loads(after["status.json"]) == status and "phases/SETUP.json" not in after
    assert json.loads(after["resources.json"]) == {"design_id": did, "cpu_seconds": {"invocation-1": elapsed}}
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_setup_phase_journals_the_current_cpu_of_each_complete_reload_without_double_counting(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, _, authority, plan, staging = fixture
    module, setup, real = pio(), _kernel("setup_phase"), _kernel("_setup_cache")
    state, log, journal, records = {"cpu": 10.0, "wall": 100.0}, [], staging / "resources.json", []
    first = _b2o_run(monkeypatch, state, log, fixture, "invocation-1")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
    old, before = json.loads(journal.read_text())["cpu_seconds"]["invocation-1"], _tree(staging)
    assert len(log) == 8 and (staging / "phases" / "SETUP.json").is_file() and old > 0

    def measured(arrays, key):
        state["cpu"] += 0.25
        return real(arrays, key)

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        mp.setattr(module, "_setup_cache", measured)
        for _ in range(2):
            records.append(setup(cfg, "full", context))
            elapsed, spent = state["cpu"] - context["cpu_start"], json.loads(journal.read_text())["cpu_seconds"]
            assert elapsed > 0 and spent == {"invocation-1": old, "invocation-2": elapsed}
    after = _tree(staging)
    assert records == [first, first] and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_setup_phase_journals_the_preflight_cpu_of_a_real_cache_integrity_error(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    module, setup, mismatch = pio(), _kernel("setup_phase"), _kernel("PartitionMismatch")
    real, did, state = _kernel("_verify_partition"), _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}
    npz, verified = _partition_stem(staging, did, {}, B2O_KEYS[1]).with_suffix(".npz"), []
    assert callable(_kernel("_setup_cache"))
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, [])
    npz.write_bytes(npz.read_bytes() + b"x")
    with pytest.raises(mismatch):
        real(staging, did, {}, B2O_KEYS[1])
    before = _tree(staging)

    def measured(*args):
        try:
            return real(*args)
        finally:
            verified.append(args[3])
            state["cpu"] += 0.25

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        mp.setattr(module, "_verify_partition", measured)
        with pytest.raises(mismatch):
            setup(cfg, "full", context)
    after, elapsed = _tree(staging), state["cpu"] - context["cpu_start"]
    assert B2O_KEYS[1] in verified and elapsed > 0 and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    assert json.loads(after["resources.json"]) == {"design_id": did, "cpu_seconds": {"invocation-1": elapsed}}


def _b2o_reloaded(tmp_path, monkeypatch):
    fixture, state, log = _b2o_fixture(tmp_path, monkeypatch), {"cpu": 10.0, "wall": 100.0}, []
    first = _b2o_run(monkeypatch, state, log, fixture, "invocation-1")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(fixture[4], fixture[2], fixture[3], "invocation-2")
    progress = _kernel("_planned_progress")(fixture[4], first["design_id"], fixture[1], fixture[3], None)
    assert len(log) == 8 and progress == ({"SETUP": first}, []) and first["phase"] == "SETUP"
    return fixture, state, first, context


def _b2o_blocked(monkeypatch, state, fixture, context, status, fakes=()):
    import json
    module, (cfg, desc), staging = pio(), fixture[:2], fixture[4]
    did, journal = _kernel("design_id")(desc), staging / "resources.json"
    kept = {k: v for k, v in json.loads(journal.read_text())["cpu_seconds"].items() if k != context["token"]}
    before, setup = _tree(staging), _kernel("setup_phase")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        for name, fake in fakes:
            mp.setattr(module, name, fake)
        with pytest.raises(_kernel("ResourceBlocked")):
            setup(cfg, "full", context)
    after, spent = _tree(staging), {**kept, context["token"]: state["cpu"] - context["cpu_start"]}
    assert "status.json" not in before and set(after) == set(before) | {"status.json"}
    assert json.loads(after["status.json"]) == {"status": "BLOCKED_RESOURCE", "design_id": did, **status}
    assert json.loads(after["resources.json"]) == {"design_id": did, "cpu_seconds": spent}
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_setup_phase_blocks_a_complete_reload_whose_current_cpu_reaches_the_cap(tmp_path, monkeypatch):
    fixture, state, first, context = _b2o_reloaded(tmp_path, monkeypatch)
    real, cap, bumped = _kernel("_setup_cache"), fixture[1]["envelope"]["cpu_hours_max"] * 3600, []
    assert cap == 14400.0 and context["token"] == "invocation-2"

    def measured(arrays, key):
        checked = real(arrays, key)
        if not bumped:
            state["cpu"] += cap + 1.0
        bumped.append(key)
        return checked

    status = {"last_complete_phase": "SETUP", "missing_partitions": []}
    _b2o_blocked(monkeypatch, state, fixture, context, status, (("_setup_cache", measured),))
    assert bumped and state["cpu"] - context["cpu_start"] >= cap
    assert _kernel("phase_record")(fixture[4], "SETUP", {}, None, None) == first


def test_setup_phase_blocks_a_complete_reload_after_the_invocation_wall_deadline(tmp_path, monkeypatch):
    fixture, state, first, context = _b2o_reloaded(tmp_path, monkeypatch)
    real, envelope = _kernel("_setup_cache"), fixture[1]["envelope"]
    assert context["started"] == state["wall"] == 100.0 and envelope["wall_seconds_per_invocation"] == 2700

    def measured(arrays, key):
        state["cpu"] += 0.25
        return real(arrays, key)

    state["wall"] = context["started"] + envelope["wall_seconds_per_invocation"] + 1.0
    status = {"last_complete_phase": "SETUP", "missing_partitions": []}
    _b2o_blocked(monkeypatch, state, fixture, context, status, (("_setup_cache", measured),))
    assert state["cpu"] - context["cpu_start"] < envelope["cpu_hours_max"] * 3600
    assert _kernel("phase_record")(fixture[4], "SETUP", {}, None, None) == first


def test_setup_phase_blocks_before_its_first_producer_when_a_prior_token_spent_the_cap(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, state = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}
    cap = desc["envelope"]["cpu_hours_max"] * 3600
    missing = [{"phase": "SETUP", "key": key} for key in plan["SETUP"]]
    assert _kernel("charge_cpu")(staging, "invocation-0", cap) == cap
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    journal = json.loads((staging / "resources.json").read_text())
    assert journal == {"design_id": did, "cpu_seconds": {"invocation-0": cap, "invocation-1": 0.0}}
    assert plan["SETUP"] == B2O_KEYS and set(_tree(staging)) == {"design.json", "resources.json"}
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, missing)
    _b2o_blocked(monkeypatch, state, fixture, context, {"last_complete_phase": None, "missing_partitions": missing})
    assert not (staging / "partitions").exists() and not (staging / "phases").exists()


def test_setup_phase_blocks_after_metadata_cost_reaches_the_cap_before_its_commit(tmp_path, monkeypatch):
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    did, refs, state = _kernel("design_id")(desc), _b2o_references(desc, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cap, want, calls = desc["envelope"]["cpu_hours_max"] * 3600, pdb.canon(desc), []
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, []) and len(refs) == 3
    assert callable(_kernel("_setup_metadata")) and cap == 14400.0

    def metadata(desc, frame, fit, setup):
        assert pdb.canon(desc) == want and pdb.canon(setup) in refs and _same_arrays(frame, _b2o_frame())
        assert _same_arrays(fit, _b2o_frame() if setup[0] == "EXACT" else _b2o_fit(setup[0]))
        if not calls:
            state["cpu"] += cap + 1.0
        calls.append(pdb.canon(setup))
        return refs[pdb.canon(setup)]

    status = {"last_complete_phase": None, "missing_partitions": []}
    _b2o_blocked(monkeypatch, state, fixture, context, status, (("_setup_metadata", metadata),))
    assert calls and set(calls) <= set(refs) and not (staging / "phases").exists()


B2O_INTERRUPTS = {"after_frame": (0, ["frame", "FULL", 24]),
                  "after_gaussian_fit": (1, ["fit", "FULL", "FITTED_LW_GAUSSIAN", 24, 0]),
                  "during_metadata": (2, None)}


def _b2o_producers(arms):
    return [entry for arm in arms for entry in (("noise", "fit", "FULL", arm, 24, 0), ("fit", arm))]


@pytest.mark.parametrize("point", B2O_INTERRUPTS)
def test_setup_phase_recovers_each_interruption_into_the_reference_record(tmp_path, monkeypatch, point):
    import json
    (n, stop), module = B2O_INTERRUPTS[point], pio()
    verify, progress = _kernel("_verify_partition"), _kernel("_planned_progress")
    reference = _b2o_fixture(tmp_path / "reference", monkeypatch)
    assert module.REPO_ROOT == tmp_path / "reference"
    expected = _b2o_run(monkeypatch, {"cpu": 10.0, "wall": 100.0}, [], reference, "reference")
    work = _b2o_fixture(tmp_path / "work", monkeypatch)
    _, desc, authority, plan, staging = work
    did, state, logs, fired = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, ([], []), []
    durable, missing = [*B2O_KEYS[:n], B2O_KEYS[2]], [{"phase": "SETUP", "key": key} for key in B2O_KEYS[n:2]]
    assert module.REPO_ROOT == tmp_path / "work" and did == expected["design_id"] and staging.name == did[:16]
    assert authority == reference[2] and plan == reference[3] and plan["SETUP"] == B2O_KEYS
    target = "_setup_metadata" if stop is None else "guarded_partition"
    real = getattr(module, target)

    def after(context, phase, upstream, key, produce):
        arrays = real(context, phase, upstream, key, produce)
        if key == stop and not fired:
            fired.append(key)
            raise OSError(f"interrupted after the durable SETUP partition {key}")
        return arrays

    def during(desc, frame, fit, setup):
        metadata = real(desc, frame, fit, setup)
        if not fired:
            fired.append(setup)
            state["cpu"] += 0.25
            raise OSError("interrupted during the SETUP metadata assembly")
        return metadata

    base = state["cpu"]
    with monkeypatch.context() as mp:
        mp.setattr(module, target, after if stop else during)
        with pytest.raises(OSError, match="interrupted"):
            _b2o_run(monkeypatch, state, logs[0], work, "invocation-1")
    spent = {"invocation-1": state["cpu"] - base}
    journal = json.loads((staging / "resources.json").read_text())
    assert fired and spent["invocation-1"] > 0 and journal == {"design_id": did, "cpu_seconds": spent}
    assert [entry for entry in logs[0] if entry[0] != "head"] == [("frame", 24), *_b2o_producers(B2O_FITTED[:n])]
    assert progress(staging, did, desc, plan, None) == ({}, missing) and not (staging / "phases").exists()
    for key in durable:
        _, rows, arrays = verify(staging, did, {}, key)
        assert rows == 24 and _same_arrays(arrays, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2])), key
    kept, base = _tree(staging / "partitions"), state["cpu"]
    assert len(kept) == 2 * len(durable)
    record = _b2o_run(monkeypatch, state, logs[1], work, "invocation-2")
    spent["invocation-2"], final = state["cpu"] - base, _tree(staging / "partitions")
    assert [entry for entry in logs[1] if entry[0] != "head"] == _b2o_producers(B2O_FITTED[n:])
    assert record == expected and _kernel("phase_record")(staging, "SETUP", {}, None, None) == record
    assert {name: final[name] for name in kept} == kept and final == _tree(reference[4] / "partitions")
    assert (staging / "phases" / "SETUP.json").read_bytes() == (reference[4] / "phases" / "SETUP.json").read_bytes()
    assert json.loads((staging / "resources.json").read_text()) == {"design_id": did, "cpu_seconds": spent}


B2O_ADMISSION = ("other_design_valid_go", "authorization_removed", "go_tampered", "context_authority_forged",
                 "extra_unplanned_fit", "malformed_plan")


@pytest.mark.parametrize("case", B2O_ADMISSION)
def test_setup_phase_refuses_each_poisoned_admission_axis_before_any_effect(tmp_path, monkeypatch, case):
    describe, authorize, validated = _kernel("design_descriptor"), _kernel("authorize"), _kernel("_validated_plan")
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    did, state = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}
    go = tmp_path / "prompts" / "GO-full-fixture.md"
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    staged = _kernel("_staged_design")(staging)
    assert staged[0] == did and pdb.canon(staged[1]) == pdb.canon(describe(cfg, "full")) == pdb.canon(desc)
    assert authorize("full", cfg, desc, 1) == authority == context["authority"] and context["plan"] is plan
    assert validated(plan) is None and plan["SETUP"] == B2O_KEYS and pio().REPO_ROOT == tmp_path
    current, poisoned, error = cfg, context, ValueError
    if case == "other_design_valid_go":
        other = _authorized(tmp_path / "other", monkeypatch, _edited(cfg, ("parameters", "H"), 251), "full")[0]
        other_desc = describe(other, "full")
        other_did = _kernel("design_id")(other_desc)
        assert pio().REPO_ROOT == tmp_path / "other" and other_did != did
        assert other_desc["science"]["parameters"]["H"] == 251 and other["authorization"]["design_id"] == other_did
        assert authorize("full", other, other_desc, 1)["design_id"] == other_did
        current, error = other, _kernel("StagingMismatch")
    elif case == "authorization_removed":
        current, error = {**cfg, "authorization": None}, _kernel("AuthorizationRefused")
        assert pdb.canon(describe(current, "full")) == pdb.canon(desc)
    elif case == "go_tampered":
        go.write_bytes(go.read_bytes() + b"Amended after the invocation started.")
        assert pdb.file_sha256(go) != authority["go_reference"]["sha256"]
        error = _kernel("AuthorizationRefused")
    elif case == "context_authority_forged":
        forged = {**authority, "go_reference": {**authority["go_reference"], "sha256": "0" * 64}}
        assert pdb.canon(forged) != pdb.canon(authority) == pdb.canon(authorize("full", cfg, desc, 1))
        poisoned, error = {**context, "authority": forged}, _kernel("AuthorizationRefused")
    elif case == "extra_unplanned_fit":
        extra = ["fit", "FULL", "FITTED_LW_GAUSSIAN", 24, 1]
        poisoned = {**context, "plan": {**plan, "SETUP": sorted([*plan["SETUP"], extra], key=pdb.canon)}}
        assert validated(poisoned["plan"]) is None and tuple(extra) not in _kernel("seed_plan")(cfg, "full")["keys"]
    else:
        poisoned = {**context, "plan": {phase: keys for phase, keys in plan.items() if phase != "ALT"}}
        with pytest.raises(ValueError):
            validated(poisoned["plan"])
    assert _kernel("_staged_design")(staging) == staged
    setup, before = _kernel("setup_phase"), _tree(tmp_path)
    inputs = pdb.canon([current, {**poisoned, "staging": str(poisoned["staging"])}])
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b1m_clock(mp, state)
        _b2o_forbid(mp)
        with pytest.raises(error):
            setup(current, "full", poisoned)
    assert _tree(tmp_path) == before
    assert pdb.canon([current, {**poisoned, "staging": str(poisoned["staging"])}]) == inputs


B2O_INTEGRITY_CASES = ("committed_npz_corrupt", "committed_npz_missing", "committed_wrong_inventory",
                       "committed_wrong_membership", "pending_json_without_npz")


@pytest.mark.parametrize("case", B2O_INTEGRITY_CASES)
def test_setup_phase_refuses_each_corrupt_or_foreign_setup_state_without_repair(tmp_path, monkeypatch, case):
    import hashlib
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    _, desc, authority, plan, staging = fixture
    record, verify, progress = _kernel("phase_record"), _kernel("_verify_partition"), _kernel("_planned_progress")
    did, refs, state = _kernel("design_id")(desc), _b2o_references(desc, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    (gaussian, t7, frame), mismatch = B2O_KEYS, _kernel("PartitionMismatch")
    t7_setup, pending = pdb.canon(list(B2O_SETUPS[2])), case == "pending_json_without_npz"
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in [t7, frame] if pending else B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
        assert _same_arrays(verify(staging, did, {}, key)[2], _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    if pending:
        assert progress(staging, did, desc, plan, None) == ({}, [{"phase": "SETUP", "key": gaussian}])
    else:
        keys = [gaussian, frame] if case == "committed_wrong_inventory" else B2O_KEYS
        members = {k: v for k, v in refs.items() if case != "committed_wrong_membership" or k != t7_setup}
        committed = record(staging, "SETUP", {}, keys, {"setups": members})
        assert record(staging, "SETUP", {}, None, None) == committed and len(committed["partitions"]) == len(keys)
    if case == "committed_wrong_inventory":
        assert [row["key"] for row in committed["partitions"]] == [gaussian, frame] != plan["SETUP"]
        with pytest.raises(mismatch):
            progress(staging, did, desc, plan, None)
    elif case == "committed_wrong_membership":
        assert progress(staging, did, desc, plan, None) == ({"SETUP": committed}, []) and len(refs) == 3
        assert sorted(committed["derived"]["setups"]) == sorted(set(refs) - {t7_setup})
    else:
        target = gaussian if case == "committed_npz_corrupt" else t7
        npz, sidecar = (_partition_stem(staging, did, {}, target).with_suffix(ext) for ext in (".npz", ".json"))
        if case == "committed_npz_corrupt":
            npz.write_bytes(npz.read_bytes() + b"x")
            assert json.loads(sidecar.read_text())["payload_sha256"] != hashlib.sha256(npz.read_bytes()).hexdigest()
        else:
            npz.unlink()
        assert sidecar.is_file() and npz.exists() == (case == "committed_npz_corrupt")
        with pytest.raises(mismatch):
            verify(staging, did, {}, target)
    _b2o_refused(monkeypatch, state, fixture, context, mismatch)
    spent = json.loads((staging / "resources.json").read_text())["cpu_seconds"]
    assert spent == {"invocation-1": state["cpu"] - context["cpu_start"]}


def test_setup_phase_reproduces_an_orphan_fit_npz_and_reuses_the_durable_frame(tmp_path, monkeypatch):
    import json
    module, verify, progress = pio(), _kernel("_verify_partition"), _kernel("_planned_progress")
    reference = _b2o_fixture(tmp_path / "reference", monkeypatch)
    assert module.REPO_ROOT == tmp_path / "reference"
    expected = _b2o_run(monkeypatch, {"cpu": 10.0, "wall": 100.0}, [], reference, "reference")
    work = _b2o_fixture(tmp_path / "work", monkeypatch)
    _, desc, authority, plan, staging = work
    did, state, log, (gaussian, t7, frame) = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, [], B2O_KEYS
    assert module.REPO_ROOT == tmp_path / "work" and did == expected["design_id"] and staging.name == did[:16]
    assert authority == reference[2] and plan == reference[3] and plan["SETUP"] == B2O_KEYS
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        first = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in (frame, gaussian):
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
        assert _same_arrays(verify(staging, did, {}, key)[2], _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    frame_stem, orphan = (_partition_stem(staging, did, {}, key) for key in (frame, gaussian))
    kept = {ext: frame_stem.with_suffix(ext).read_bytes() for ext in (".npz", ".json")}
    orphan.with_suffix(".json").unlink()
    missing = [{"phase": "SETUP", "key": key} for key in (gaussian, t7)]
    assert orphan.with_suffix(".npz").is_file() and not orphan.with_suffix(".json").exists()
    assert progress(staging, did, desc, plan, None) == ({}, missing) and not (staging / "phases").exists()
    prepared, base = state["cpu"] - first["cpu_start"], state["cpu"]
    record = _b2o_run(monkeypatch, state, log, work, "invocation-2")
    spent = {"invocation-1": prepared, "invocation-2": state["cpu"] - base}
    assert [entry for entry in log if entry[0] != "head"] == _b2o_producers(B2O_FITTED)
    assert record == expected and _kernel("phase_record")(staging, "SETUP", {}, None, None) == record
    assert {ext: frame_stem.with_suffix(ext).read_bytes() for ext in (".npz", ".json")} == kept
    assert _tree(staging / "partitions") == _tree(reference[4] / "partitions")
    assert (staging / "phases" / "SETUP.json").read_bytes() == (reference[4] / "phases" / "SETUP.json").read_bytes()
    assert json.loads((staging / "resources.json").read_text()) == {"design_id": did, "cpu_seconds": spent}


def _b2o_forbid_producers(mp):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("frame, noise, fit or exact-score producer called on fully cached SETUP partitions")

    for owner, name in ((module, "population_frame"), (module, "null_returns"), (module, "fit_record"),
                        (module, "exact_scores"), (pdb, "fit_basis"), (pdb.sim, "t_innov")):
        mp.setattr(owner, name, forbidden)


def test_setup_phase_propagates_a_real_t22_fit_refusal_without_rerolling_the_gaussian_key(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    module, adapter, verify = pio(), _kernel("fit_record"), _kernel("_verify_partition")
    did, state, (gaussian, _, frame) = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, B2O_KEYS
    lam, rows, calls = np.array([36.0, 36.0, *(1.5 * np.arange(22, 0, -1.0))]), _b2o_rows("FITTED_LW_GAUSSIAN"), []

    def sealed(X_fit):
        calls.append(("fit_basis", X_fit.tobytes()))
        state["cpu"] += 2.0
        return {"eigval": lam.copy(), "eigvec": np.eye(24), "lambda_corr": _B2cPoison()}

    def noise(desc, frame, key):
        assert type(key) is tuple and _same_arrays(frame, _b2o_frame())
        calls.append(("noise", key))
        state["cpu"] += 0.5
        return _b2o_rows(key[2])

    def forbidden(*args, **kwargs):
        raise AssertionError("frame, HEAD, baseline or bundle work after a refused Gaussian fit")

    with monkeypatch.context() as mp:
        mp.setattr(pdb, "fit_basis", sealed)
        with pytest.raises(ValueError, match="T22") as qualified:
            adapter(rows, 20)
    assert calls == [("fit_basis", rows.tobytes())] and lam.size == 24 and (np.diff(lam) <= 0).all()
    calls.clear()
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    _b2o_cache(staging, frame, _b2o_frame())
    missing = [{"phase": "SETUP", "key": key} for key in B2O_KEYS[:2]]
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, missing)
    assert _same_arrays(verify(staging, did, {}, frame)[2], _b2o_frame())
    setup, before, kept = _kernel("setup_phase"), _tree(staging), _tree(staging / "partitions")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        mp.setattr(pdb, "fit_basis", sealed)
        mp.setattr(module, "null_returns", noise)
        for owner, name in ((module, "population_frame"), (module, "exact_scores"), (module, "head_geometry"),
                            (module, "spectral_baselines"), (module, "setup_bundle"), (pdb.sim, "t_innov")):
            mp.setattr(owner, name, forbidden)
        with pytest.raises(ValueError, match="T22") as caught:
            setup(cfg, "full", context)
    after = _tree(staging)
    assert type(caught.value) is ValueError and str(caught.value) == str(qualified.value)
    assert calls == [("noise", tuple(gaussian)), ("fit_basis", rows.tobytes())] and len(kept) == 2
    assert set(after) == set(before) and _tree(staging / "partitions") == kept and not (staging / "phases").exists()
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    spent = json.loads(after["resources.json"])["cpu_seconds"]
    assert spent == {"invocation-1": state["cpu"] - context["cpu_start"]} and spent["invocation-1"] > 0


def test_setup_phase_propagates_a_real_market_metadata_trace_overflow_from_valid_caches(tmp_path, monkeypatch):
    import json
    fixture = _b2o_market(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    module, verify, checked = pio(), _kernel("_verify_partition"), _kernel("_setup_cache")
    real, did, state = _kernel("_setup_metadata"), _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}
    huge = {"V": np.eye(24), "lam": np.full(24, np.finfo(np.float64).max / 16), "mean": np.zeros(24)}
    records = dict(zip(map(pdb.canon, B2O_KEYS), (huge, _b2o_fit("FITTED_LW_T7"), _b2o_frame())))
    gaussian_setup, seen = list(B2O_SETUPS[1]), []
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, records[pdb.canon(key)])
        assert _same_arrays(checked(verify(staging, did, {}, key)[2], key), records[pdb.canon(key)])
    with np.errstate(over="ignore"):
        assert np.isfinite(huge["lam"]).all() and not np.isfinite(huge["lam"].sum())
    assert desc["scope"]["applications"] == ["MARKET"] and plan["SETUP"] == B2O_KEYS
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, [])
    with pytest.raises(ValueError) as qualified:
        real(desc, _b2o_frame(), huge, gaussian_setup)
    with pytest.raises(ValueError):
        _kernel("spectral_baselines")(huge["lam"], "MARKET")

    def metadata(desc, frame, fit, setup):
        seen.append(pdb.canon(setup))
        state["cpu"] += 0.25
        return real(desc, frame, fit, setup)

    setup, before = _kernel("setup_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid_producers(mp)
        mp.setattr(module, "_setup_metadata", metadata)
        with pytest.raises(ValueError) as caught:
            setup(cfg, "full", context)
    after = _tree(staging)
    assert type(caught.value) is ValueError and str(caught.value) == str(qualified.value)
    assert pdb.canon(gaussian_setup) in seen and set(after) == set(before) and not (staging / "phases").exists()
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    spent = json.loads(after["resources.json"])["cpu_seconds"]
    assert spent == {"invocation-1": state["cpu"] - context["cpu_start"]} and spent["invocation-1"] > 0


def test_setup_phase_commits_an_inconclusive_head_once_and_reloads_it_without_reroll(tmp_path, monkeypatch):
    import json
    fixture = _b2o_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    module, head, bundle = pio(), _kernel("head_geometry"), _kernel("setup_bundle")
    did, state, refs, seen = _kernel("design_id")(desc), {"cpu": 10.0, "wall": 100.0}, {}, []
    fits = {"FITTED_LW_GAUSSIAN": _b2h_fit(B2H_PERMS["misaligned"]), "FITTED_LW_T7": _b2o_fit("FITTED_LW_T7")}
    f_min = head(_b2o_frame(), fits["FITTED_LW_GAUSSIAN"], 0.25, B2B_UNIVERSES["RESIDUAL"])["summary"]["f_E"]["min"]
    assert f_min == pytest.approx(0.75, rel=1e-12) and f_min < desc["science"]["head"]["kappa_geo"] == 0.8
    for setup in desc["scope"]["setups"]:
        rows = None if setup[0] == "EXACT" else _b2o_rows(setup[0])
        with monkeypatch.context() as mp:
            mp.setattr(module, "fit_record", lambda X_fit, K, arm=setup[0]: fits[arm])
            refs[pdb.canon(setup)] = bundle(desc, _b2o_frame(), rows, setup)["metadata"]
    gaussian = pdb.canon(list(B2O_SETUPS[1]))
    statuses = {key: meta["applications"]["RESIDUAL"]["head"]["status"] for key, meta in refs.items()}
    assert statuses == {**dict.fromkeys(refs, "GEOMETRY_ALIGNED"), gaussian: "DESIGN_CONTROL_INCONCLUSIVE"}
    hashes = sorted(pdb.array_sha256(r["V"], r["lam"], r["mean"]) for r in (_b2o_frame(), *fits.values()))
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in B2O_KEYS:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else fits[key[2]])
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({}, []) and len(set(hashes)) == 3
    go, setup_phase = tmp_path / "prompts" / "GO-full-fixture.md", _kernel("setup_phase")
    inputs = [pdb.canon(cfg), pdb.canon(plan), go.read_bytes(), _kernel("_staged_design")(staging)]

    def counted(frame, fit, istar, universe):
        seen.append(pdb.array_sha256(fit["V"], fit["lam"], fit["mean"]))
        state["cpu"] += 0.25
        return head(frame, fit, istar, universe)

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid_producers(mp)
        mp.setattr(module, "head_geometry", counted)
        record = setup_phase(cfg, "full", context)
    first = state["cpu"] - context["cpu_start"]
    assert sorted(seen) == hashes and record["derived"] == {"setups": refs} and first > 0
    assert [row["key"] for row in record["partitions"]] == B2O_KEYS and record["design_id"] == did
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        again = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
        reloaded = setup_phase(cfg, "full", again)
    after, second = _tree(staging), state["cpu"] - again["cpu_start"]
    assert set(after) == set(before) and reloaded == record == _kernel("phase_record")(staging, "SETUP", {}, None, None)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    journal = json.loads(after["resources.json"])
    assert journal == {"design_id": did, "cpu_seconds": {"invocation-1": first, "invocation-2": second}}
    assert inputs == [pdb.canon(cfg), pdb.canon(plan), go.read_bytes(), _kernel("_staged_design")(staging)]


B2O_COORDINATES = (("EXACT", 24, 0), ("EXACT", 26, 0), ("FITTED_LW_GAUSSIAN", 24, 0), ("FITTED_LW_GAUSSIAN", 24, 1),
                   ("FITTED_LW_T7", 26, 0))


def _b2o_coord_frame(N):
    return {"V": np.eye(N), "lam": _b2b_spectrum(N), "mean": np.zeros(N)}


def _b2o_coord_fit(arm, N, fit_id):
    shift = 0.25 * fit_id + 0.5 * (arm == "FITTED_LW_T7")
    return {"V": np.eye(N), "lam": 1.5 * np.arange(N, 0, -1.0), "mean": np.linspace(-0.5, 1.5, N) + shift}


def _b2o_coord_rows(arm, N, fit_id):
    rows = np.vstack([np.eye(N), -np.eye(N)])[:48] * (1.0 + fit_id + 2.0 * (arm == "FITTED_LW_T7"))
    rows.flags.writeable = False
    return rows


def _b2o_coordinates(root, monkeypatch, mode):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2O_COORDINATES]),
                        (("scope", "applications"), ["RESIDUAL", "MARKET"]), (("parameters", "T_fit"), 48)):
        cfg = _edited(cfg, path, value)
    if mode == "full":
        cfg = _authorized(root, monkeypatch, cfg, mode)[0]
    else:
        monkeypatch.setattr(pio(), "REPO_ROOT", root)
    desc, primitive = _kernel("design_descriptor")(cfg, mode), _kernel("seed_plan")(cfg, mode)["keys"]
    keys = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    plan = {phase: keys if phase == "SETUP" else [] for phase in _kernel("PHASES")}
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")(mode, cfg, desc, 1), plan, staging


@pytest.mark.parametrize("mode", ["full", "smoke"])
def test_setup_phase_covers_two_n_and_two_fit_ids_in_full_and_no_go_smoke(tmp_path, monkeypatch, mode):
    import json
    module, verify, bundle, campaign = pio(), _kernel("_verify_partition"), _kernel("setup_bundle"), mode.upper()
    cfg, desc, authority, plan, staging = _b2o_coordinates(tmp_path, monkeypatch, mode)
    did, keys, state, log, refs = _kernel("design_id")(desc), plan["SETUP"], {"cpu": 10.0, "wall": 100.0}, [], {}
    fitted = [("fit", campaign, *setup) for setup in B2O_COORDINATES if setup[0] != "EXACT"]
    go, want = tmp_path / "prompts" / "GO-full-fixture.md", (pdb.canon(cfg), mode, pdb.canon(desc))
    assert keys == [[*key] for key in fitted] + [["frame", campaign, 24], ["frame", campaign, 26]]
    assert module.REPO_ROOT == tmp_path and authority["design_id"] == did and len(fitted) == 3
    if mode == "full":
        assert authority["go_reference"]["path"] == "prompts/GO-full-fixture.md" and go.is_file()
    else:
        assert cfg["authorization"] is None and authority == {"stage": "smoke", "design_id": did, "go_reference": None}
        assert not (tmp_path / "prompts").exists()
    for setup in desc["scope"]["setups"]:
        rows = None if setup[0] == "EXACT" else _b2o_coord_rows(*setup)
        with monkeypatch.context() as mp:
            mp.setattr(module, "fit_record", lambda X_fit, K, s=tuple(setup): _b2o_coord_fit(*s))
            refs[pdb.canon(setup)] = bundle(desc, _b2o_coord_frame(setup[1]), rows, setup)["metadata"]
    canon = {setup: pdb.canon(list(setup)) for setup in B2O_COORDINATES}
    entries = [entry for meta in refs.values() for entry in meta["applications"].values()]
    statuses = {key: meta["applications"]["RESIDUAL"]["head"]["status"] for key, meta in refs.items()}
    basis = {N: pdb.array_sha256(*_b2o_coord_frame(N).values()) for N in (24, 26)}
    hashes = {key[2:]: pdb.array_sha256(*_b2o_coord_fit(*key[2:]).values()) for key in fitted}
    gaussian = [_b2o_coord_fit("FITTED_LW_GAUSSIAN", 24, fit_id) for fit_id in (0, 1)]
    assert len(refs) == 5 and len(entries) == 10 and len({entry["setup_id"] for entry in entries}) == 10
    assert statuses == dict.fromkeys(refs, "GEOMETRY_ALIGNED") and basis[24] != basis[26]
    assert all(refs[canon[setup]]["basis_sha"] == basis[setup[1]] for setup in B2O_COORDINATES)
    assert [refs[canon[setup]]["fit_hash"] for setup in hashes] == list(hashes.values()) and len(set(hashes.values())) == 3
    assert all(refs[canon[setup]]["fit_hash"] is None for setup in B2O_COORDINATES if setup[0] == "EXACT")
    assert all(np.array_equal(gaussian[0][name], gaussian[1][name]) for name in ("V", "lam"))
    assert refs[canon[("FITTED_LW_T7", 26, 0)]]["information_basis"] == "GAUSSIAN_PROXY"
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")

    def inputs():
        return [pdb.canon(cfg), pdb.canon(plan), go.read_bytes() if go.exists() else None,
                _kernel("_staged_design")(staging), _kernel("seed_plan")(cfg, mode)["sha256"]]

    def population_frame(cfg, mode, N):
        assert (pdb.canon(cfg), mode) == want[:2] and type(N) is int
        log.append(("frame", N))
        state["cpu"] += 1.0
        return np.eye(N), _b2b_spectrum(N)

    def null_returns(desc, frame, key):
        assert pdb.canon(desc) == want[2] and type(key) is tuple and key in fitted
        assert _same_arrays(frame, _b2o_coord_frame(key[3]))
        log.append(("noise", *key))
        state["cpu"] += 0.5
        return _b2o_coord_rows(*key[2:])

    def fit_record(X_fit, K):
        match = [key for key in fitted if np.array_equal(X_fit, _b2o_coord_rows(*key[2:]))]
        assert type(K) is int and K == 20 and len(match) == 1 and not X_fit.flags.writeable
        log.append(("fit", *match[0][2:]))
        state["cpu"] += 2.0
        return _b2o_coord_fit(*match[0][2:])

    def forbidden(*args, **kwargs):
        raise AssertionError("genuine noise, exact-score or sealed fit work inside the coordinate fixture")

    kept, setup = inputs(), _kernel("setup_phase")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        for fake in (population_frame, null_returns, fit_record):
            mp.setattr(module, fake.__name__, fake)
        for owner, name in ((module, "exact_scores"), (pdb, "fit_basis"), (pdb.sim, "t_innov")):
            mp.setattr(owner, name, forbidden)
        record = setup(cfg, mode, context)
    first = state["cpu"] - context["cpu_start"]
    calls = [("frame", 24), ("frame", 26), *(entry for key in fitted for entry in (("noise", *key), ("fit", *key[2:])))]
    assert log == calls and [row["key"] for row in record["partitions"]] == keys and first > 0
    assert [row["n_rows"] for row in record["partitions"]] == [24, 24, 26, 24, 26] and record["design_id"] == did
    assert record["derived"] == {"setups": refs} and inputs() == kept
    for key in keys:
        _, rows, arrays = verify(staging, did, {}, key)
        N = key[2] if key[0] == "frame" else key[3]
        assert rows == N and _same_arrays(arrays, _b2o_coord_frame(N) if key[0] == "frame" else _b2o_coord_fit(*key[2:]))
    journal = json.loads((staging / "resources.json").read_text())
    assert journal == {"design_id": did, "cpu_seconds": {"invocation-1": first}}
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        again = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
        reloaded = setup(cfg, mode, again)
    after, second = _tree(staging), state["cpu"] - again["cpu_start"]
    assert reloaded == record == _kernel("phase_record")(staging, "SETUP", {}, None, None) and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    journal = json.loads(after["resources.json"])
    assert journal == {"design_id": did, "cpu_seconds": {"invocation-1": first, "invocation-2": second}}
    assert inputs() == kept and (tmp_path / "prompts").exists() == (mode == "full")
    assert all(name.startswith(("logs/", "prompts/")) for name in _tree(tmp_path))


B2P_HEAD, B2P_F2 = "F_HEAD_RESIDUAL", "F2_STRUCTURED_RESIDUAL"
B2P_SETUPS = (("EXACT", 24, 0), ("FITTED_LW_GAUSSIAN", 24, 0), ("FITTED_LW_T7", 24, 0))
B2P_FIELDS = {"status", "family", "support", "delta", "q", "I_joint", "oracle_basis"}
B2P_REFUSALS = ("key_arm_differs", "key_fit_id_differs", "frame_dimension", "fit_dimension", "exact_fit_not_frame",
                "application_unscoped", "path_key")
B2P_QBAR_REFUSALS = ("missing_family", "evaluation_families_only", "extra_family", "unbalanced", "empty",
                     "n_lib_mismatch", "wrong_k", "nonfinite", "negative", "pathwise", "not_a_mapping")


def _b2p_design(*edits):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2P_SETUPS]),
                        (("scope", "applications"), ["RESIDUAL", "MARKET"]), (("parameters", "T_fit"), 48), *edits):
        cfg = _edited(cfg, path, value)
    return cfg, _kernel("design_descriptor")(cfg, "full")


def _b2p_traps(mp):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("selection, scan, calibration, generation or fit inside offline DEV information")

    for owner, name in ((module, "best_sets"), (module, "online_masks"), (module, "nonoracle_masks"),
                        (module, "oracle_masks"), (module, "masked_scan"), (module, "population_frame"),
                        (module, "null_returns"), (module, "exact_scores"), (module, "path_scores"),
                        (module, "fit_record"), (pdb, "select_top_q"), (pdb, "scan_statistic"),
                        (pdb, "rank_threshold"), (pdb, "fit_basis"), (pdb.sim, "t_innov")):
        mp.setattr(owner, name, forbidden)


def _b2p_draw_stub(mp, desc, rows, calls):
    want = pdb.canon(desc)

    def direction_draws(desc, key):
        assert pdb.canon(desc) == want and type(key) is tuple and key in rows
        calls.append(key)
        return rows[key].copy()

    mp.setattr(pio(), "direction_draws", direction_draws)


def _b2p_frozen(*records):
    arrays = [array for record in records for array in (record.values() if isinstance(record, dict) else [record])]
    for array in arrays:
        array.flags.writeable = False
    return arrays, [array.tobytes() for array in arrays]


def _b2p_pool():
    scale = {"F0_ISOTROPIC_RESIDUAL": 3.0, "F1_TAIL_RESIDUAL": 2.0, "F2_STRUCTURED_RESIDUAL": 1.0, "F_HEAD_RESIDUAL": 0.0}
    return {family: np.array([[s * (r + 1) * (k % 4) / 8.0 for k in range(20)] for r in range(2)])
            for family, s in scale.items()}


def test_direction_information_projects_one_population_drift_of_each_original_key_on_its_frozen_fit(monkeypatch):
    cfg, desc = _b2p_design()
    planned, frame = set(_kernel("seed_plan")(cfg, "full")["keys"]), _b2o_frame()
    aligned, misaligned = _b2h_fit(B2H_PERMS["aligned"]), _b2h_fit(B2H_PERMS["misaligned"])
    signs, devlib = np.array([[1.0, -1.0, -1.0, 1.0]]), ("devlib", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, B2P_HEAD, 0)
    routes = [(["EXACT", 24, 0], frame, ("devlib", "FULL", "EXACT", 24, 0, B2P_HEAD, 0), "EXACT_ADDITIVE_KL"),
              (["FITTED_LW_GAUSSIAN", 24, 0], aligned, devlib, "ORACLE_DIAGONAL_SURROGATE"),
              (["FITTED_LW_GAUSSIAN", 24, 0], misaligned, devlib, "ORACLE_DIAGONAL_SURROGATE"),
              (["FITTED_LW_T7", 24, 0], aligned, ("meta", "FULL", "FITTED_LW_T7", 24, 0, "ALT", B2P_HEAD, 0),
               "ORACLE_DIAGONAL_GAUSSIAN_PROXY")]
    delta = np.zeros(24)
    delta[1:5] = signs[0] * np.sqrt(0.125 * frame["lam"][1:5])
    refs = [0.5 * (delta @ fit["V"][:, 1:21]) ** 2 / fit["lam"][1:21] for _, fit, _, _ in routes]
    assert all(key in planned for _, _, key, _ in routes) and desc["science"]["parameters"]["I_star"] == 0.25
    np.testing.assert_allclose(refs[0], [0.0625] * 4 + [0.0] * 16, rtol=1e-12, atol=0)
    assert refs[2][0] == 0.0 < refs[2][4] and np.array_equal(refs[1], refs[3]) and not np.allclose(refs[1], refs[2])
    assert abs(refs[1].sum() - 0.25) > 0.1 and frame["V"].tolist() == np.eye(24).tolist()
    arrays, kept = _b2p_frozen(frame, aligned, misaligned, signs)
    information, calls, snapshot = _kernel("direction_information"), [], pdb.canon(desc)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        _b2p_draw_stub(mp, desc, {key: signs for _, _, key, _ in routes}, calls)
        outs = [information(desc, frame, fit, setup, "RESIDUAL", key) for setup, fit, key, _ in routes]
    assert calls == [key for _, _, key, _ in routes] and [a.tobytes() for a in arrays] == kept
    for out, (_, _, _, label), ref in zip(outs, routes, refs):
        assert set(out) == B2P_FIELDS and out["status"] == "SUPPORTED" and out["family"] == B2P_HEAD
        assert out["support"] == [2, 3, 4, 5] and out["oracle_basis"] == label and out["q"].shape == (20,)
        np.testing.assert_allclose(out["delta"], delta, rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(out["q"], ref, rtol=1e-12, atol=1e-15)
        assert out["I_joint"] == pytest.approx(0.25, rel=1e-12) and np.array_equal(out["delta"], outs[0]["delta"])
    assert outs[0]["q"].sum() == pytest.approx(outs[0]["I_joint"], rel=1e-12) and outs[2]["q"][0] == 0.0
    assert not np.array_equal(outs[1]["q"], outs[2]["q"]) and abs(outs[1]["q"].sum() - outs[1]["I_joint"]) > 0.1
    assert pdb.canon(desc) == snapshot


def test_direction_information_keeps_the_received_unsupported_drift_without_projection(monkeypatch):
    cfg, desc = _b2p_design()
    frame, fit, drift = _b2o_frame(), _b2h_fit(B2H_PERMS["aligned"]), _kernel("population_drift")
    key, signs = ("devlib", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, B2P_F2, 0), np.array([[1.0, 1.0, -1.0, 1.0]])
    market, residual, setup = list(range(1, 21)), list(range(2, 22)), ["FITTED_LW_GAUSSIAN", 24, 0]
    assert key in set(_kernel("seed_plan")(cfg, "full")["keys"])
    assert drift(frame["V"], frame["lam"], "MARKET", market, B2P_F2, 0.25, signs)["status"] == "UNSUPPORTED"
    assert drift(frame["V"], frame["lam"], "RESIDUAL", residual, B2P_F2, 0.25, signs)["support"] == [3, 9, 17, 21]
    arrays, kept = _b2p_frozen(frame, fit, signs)
    module, information, calls, projected = pio(), _kernel("direction_information"), [], []
    real = module.projection_diagnostics

    def spy(*args, **kwargs):
        projected.append(True)
        return real(*args, **kwargs)

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        _b2p_draw_stub(mp, desc, {key: signs}, calls)
        mp.setattr(module, "projection_diagnostics", spy)
        unsupported = information(desc, frame, fit, setup, "MARKET", key)
        supported = information(desc, frame, fit, setup, "RESIDUAL", key)
    empty = dict.fromkeys(("support", "delta", "q", "I_joint", "oracle_basis"))
    assert unsupported == {"status": "UNSUPPORTED", "family": B2P_F2, **empty} and calls == [key, key]
    assert supported["status"] == "SUPPORTED" and supported["support"] == [3, 9, 17, 21] and len(projected) == 1
    assert supported["oracle_basis"] == "ORACLE_DIAGONAL_SURROGATE" and [a.tobytes() for a in arrays] == kept


@pytest.mark.parametrize("case", B2P_REFUSALS)
def test_direction_information_refuses_disagreeing_inputs_before_any_draw(monkeypatch, case):
    edits = ((("scope", "applications"), ["RESIDUAL"]),) if case == "application_unscoped" else ()
    cfg, desc = _b2p_design(*edits)
    planned = set(_kernel("seed_plan")(cfg, "full")["keys"])
    setup, application = ["FITTED_LW_GAUSSIAN", 24, 0], "RESIDUAL"
    key = ("devlib", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, B2P_HEAD, 0)
    frame, fit = _b2o_frame(), _b2h_fit(B2H_PERMS["aligned"])
    small = {"V": np.eye(23), "lam": _b2b_spectrum(23), "mean": np.zeros(23)}
    if case == "key_arm_differs":
        key = ("devlib", "FULL", "FITTED_LW_T7", 24, 0, B2P_HEAD, 0)
        assert key[2] != setup[0]
    elif case == "key_fit_id_differs":
        key = ("devlib", "FULL", "FITTED_LW_GAUSSIAN", 24, 1, B2P_HEAD, 0)
        assert key not in planned and key[4] != setup[2]
    elif case == "frame_dimension":
        frame = small
    elif case == "fit_dimension":
        fit = small
    elif case == "exact_fit_not_frame":
        setup, key = ["EXACT", 24, 0], ("devlib", "FULL", "EXACT", 24, 0, B2P_HEAD, 0)
        assert not np.array_equal(fit["mean"], frame["mean"])
    elif case == "application_unscoped":
        application = "MARKET"
        assert desc["scope"]["applications"] == ["RESIDUAL"] and "MARKET" in desc["science"]["applications"]
    else:
        key = ("path", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, "CAL_NULL", 0)
    assert small["lam"].size == 23 and (case == "key_fit_id_differs" or key in planned)
    arrays, kept = _b2p_frozen(frame, fit)
    information, calls, snapshot = _kernel("direction_information"), [], pdb.canon(desc)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        _b2p_draw_stub(mp, desc, {}, calls)
        with pytest.raises(ValueError):
            information(desc, frame, fit, setup, application, key)
    assert not calls and [a.tobytes() for a in arrays] == kept and pdb.canon(desc) == snapshot


def test_dev_qbar_averages_the_four_balanced_dev_families_with_equal_weights(monkeypatch):
    from fractions import Fraction
    _, desc = _b2p_design((("dev", "n_lib"), 2), (("modes", "full", "sizes", "DEV_LIB"), 2))
    pool = _b2p_pool()
    reference = [float(sum(Fraction(pool[f][r, k]) for f in pool for r in range(2)) / 8) for k in range(20)]
    assert sorted(desc["science"]["dev"]["families"]) == sorted(pool) == sorted(DEV_FAMILIES)
    assert desc["scope"]["families"] == [B2P_F2, B2P_HEAD] and desc["science"]["dev"]["n_lib"] == 2
    assert desc["science"]["parameters"]["K"] == 20 and not pool[B2P_HEAD].any() and reference[0] == 0.0
    assert reference[1:4] == [0.28125, 0.5625, 0.84375] and reference[1] != 2.25 / 6
    evaluation = desc["scope"]["families"]
    scoped = [float(sum(Fraction(pool[f][r, k]) for f in evaluation for r in range(2)) / 4) for k in range(20)]
    assert scoped[1:4] == [0.09375, 0.1875, 0.28125] and scoped != reference
    arrays, kept = _b2p_frozen(*pool.values())
    qbar, snapshot = _kernel("dev_qbar"), pdb.canon(desc)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        first, again = qbar(desc, pool), qbar(desc, dict(reversed(list(pool.items()))))
    assert first.dtype == np.float64 and first.shape == (20,) and first.tolist() == reference
    assert np.array_equal(first, again) and [a.tobytes() for a in arrays] == kept and pdb.canon(desc) == snapshot


@pytest.mark.parametrize("case", B2P_QBAR_REFUSALS)
def test_dev_qbar_refuses_unbalanced_foreign_or_invalid_family_pools_before_any_effect(monkeypatch, case):
    _, desc = _b2p_design((("dev", "n_lib"), 2), (("modes", "full", "sizes", "DEV_LIB"), 2))
    pool, (f0, f1, f2, _) = _b2p_pool(), DEV_FAMILIES
    assert sorted(pool) == sorted(DEV_FAMILIES) and desc["science"]["dev"]["n_lib"] == 2
    if case == "missing_family":
        del pool[f0]
    elif case == "evaluation_families_only":
        pool = {family: pool[family] for family in desc["scope"]["families"]}
    elif case == "extra_family":
        pool["F3_MARKET"] = np.zeros((2, 20))
    elif case == "unbalanced":
        pool[f1] = pool[f1][:1]
    elif case == "empty":
        pool = {family: np.zeros((0, 20)) for family in pool}
    elif case == "n_lib_mismatch":
        pool = {family: np.vstack([q, q[:1]]) for family, q in pool.items()}
    elif case == "wrong_k":
        pool[f0] = pool[f0][:, :19]
    elif case == "nonfinite":
        pool[f2] = np.where(np.arange(20) == 1, np.nan, pool[f2])
    elif case == "negative":
        pool[f1] = np.where(np.arange(20) == 2, -0.125, pool[f1])
    elif case == "pathwise":
        pool[f0] = pool[f0][:, :, None]
    else:
        pool = list(pool.values())
    arrays, kept = _b2p_frozen(*(pool.values() if isinstance(pool, dict) else pool))
    qbar = _kernel("dev_qbar")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        with pytest.raises(ValueError):
            qbar(desc, pool)
    assert [a.tobytes() for a in arrays] == kept


B2Q_PRIOR = 0.0034068772765664954
B2Q_FIELDS = {"label", "application", "status", "s2", "policy"}
B2Q_SPECTRAL = ("FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90")
B2Q_PRIOR_REFUSALS = {"h_zero": (("parameters", "H"), 0), "h_bool": (("parameters", "H"), True),
                      "h_float": (("parameters", "H"), 250.0), "h_overflow": (("parameters", "H"), 2 ** 1100),
                      "alpha_zero": (("parameters", "alpha"), 0.0), "alpha_one": (("parameters", "alpha"), 1.0),
                      "alpha_text": (("parameters", "alpha"), "0.05"), "k_zero": (("parameters", "K"), 0),
                      "k_float": (("parameters", "K"), 20.0), "rule_other": (("parameters", "s2_rule"), "2*I_star/d")}
B2Q_REFUSALS = {"obsolete_kaiser_label": ("RESIDUAL", "FIXED_KAISER_PREFIX", "none"),
                "undeclared_window": ("RESIDUAL", "ONLINE_INFO_MIX_W64", "none"),
                "undeclared_cost": ("MARKET", "ORACLE_INFO_LIN", "none"),
                "unknown_application": ("OTHER", "FULL_K", "none"),
                "spectral_rows_missing": ("RESIDUAL", "FIXED_EIGENMEAN_PREFIX", "none"),
                "runnable_row_without_pcs": ("RESIDUAL", "RESIDUAL_CPV90", "runnable_without_pcs"),
                "cpv90_trimmed_into_residual": ("RESIDUAL", "CPV90", "pc1_in_residual"),
                "d_dev_missing": ("RESIDUAL", "FIXED_DEV_PREFIX", "none"),
                "d_dev_off_grid": ("RESIDUAL", "FIXED_DEV_PREFIX", "d_dev_3"),
                "d_dev_bool": ("RESIDUAL", "FIXED_DEV_PREFIX", "d_dev_true"),
                "qbar_missing": ("RESIDUAL", "FIXED_EXANTE_QBAR_MIX", "none"),
                "qbar_wrong_k": ("RESIDUAL", "FIXED_EXANTE_QBAR_MIX", "qbar_short"),
                "qbar_negative": ("RESIDUAL", "FIXED_EXANTE_QBAR_MIX", "qbar_negative")}


def _b2q_desc(*edits):
    return _b2p_design(*edits)[1]


def _b2q_traps(mp, selection=False):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("mask, scan, calibration, DEV recomputation, generation or fit inside policy construction")

    owners = [(module, "online_masks"), (module, "nonoracle_masks"), (module, "oracle_masks"), (module, "masked_scan"),
              (module, "spectral_baselines"), (module, "dev_qbar"), (module, "direction_information"),
              (module, "direction_draws"), (module, "population_frame"), (module, "null_returns"),
              (module, "exact_scores"), (module, "path_scores"), (module, "fit_record"), (pdb, "scan_statistic"),
              (pdb, "rank_threshold"), (pdb, "fit_basis"), (pdb.sim, "t_innov")]
    for owner, name in owners + ([] if selection else [(module, "best_sets"), (pdb, "select_top_q")]):
        mp.setattr(owner, name, forbidden)


def test_common_prior_is_the_declared_two_log_h_over_alpha_over_h_k_scalar_for_every_variant(monkeypatch):
    desc = _b2q_desc()
    params = desc["science"]["parameters"]
    reference = 2.0 * math.log(params["H"] / params["alpha"]) / (params["H"] * params["K"])
    wrong = [2.0 * params["I_star"] / d for d in (1, 4, 20)]
    wrong += [pdb.mixture_cost(d, params["gamma_M"]) / params["H"] for d in (1, 4, 20)]
    assert (params["H"], params["alpha"], params["K"], params["s2_rule"]) == (250, 0.05, 20, "2*ln(H/alpha)/(H*K)")
    assert reference == pytest.approx(B2Q_PRIOR, rel=1e-15) and all(abs(v - B2Q_PRIOR) > 1e-4 for v in wrong)
    variants = [_b2q_desc(edit) for edit in ((("parameters", "gamma_M"), 5000), (("parameters", "I_star"), 0.5),
                                              (("dev", "d_grid"), [1, 2, 4]))]
    assert all(pdb.canon(variant) != pdb.canon(desc) for variant in variants)
    changed = _b2q_desc((("parameters", "H"), 125), (("parameters", "alpha"), 0.1))
    moved, expected = changed["science"]["parameters"], 2.0 * math.log(125 / 0.1) / (125 * 20)
    assert (moved["H"], moved["alpha"], moved["K"], moved["s2_rule"]) == (125, 0.1, 20, "2*ln(H/alpha)/(H*K)")
    assert math.isfinite(expected) and expected > 0 and abs(expected - B2Q_PRIOR) > 1e-4
    prior, snapshot = _kernel("common_prior"), [pdb.canon(d) for d in (desc, *variants)]
    kept = pdb.canon(changed)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        values = [prior(d) for d in (desc, *variants)]
        value = prior(changed)
    assert type(values[0]) is float and values[0] == pytest.approx(B2Q_PRIOR, rel=1e-15) and len(set(values)) == 1
    assert [pdb.canon(d) for d in (desc, *variants)] == snapshot
    assert type(value) is float and math.isfinite(value) and value == pytest.approx(expected, rel=1e-15)
    assert value != values[0] and pdb.canon(changed) == kept


@pytest.mark.parametrize("case", B2Q_PRIOR_REFUSALS)
def test_common_prior_refuses_undeclared_rules_and_invalid_counts_or_domains(monkeypatch, case):
    path, value = B2Q_PRIOR_REFUSALS[case]
    desc = _b2q_desc((path, value))
    stored = desc["science"]["parameters"][path[-1]]
    assert stored == value and type(stored) is type(value)
    snapshot, prior = pdb.canon(desc), _kernel("common_prior")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        with pytest.raises(ValueError):
            prior(desc)
    assert pdb.canon(desc) == snapshot


def test_frozen_policy_builds_declared_online_oracle_and_full_k_envelopes_with_the_common_prior(monkeypatch):
    desc = _b2q_desc()
    params, declared = desc["science"]["parameters"], desc["science"]["policies"]
    costs, online = _kernel("cost_vectors")(params["gamma_M"], params["K"]), declared["online"]
    labels = [f"ONLINE_{o}_{c}_W{w}" for o in online["orders"] for c in online["costs"] for w in online["windows"]]
    labels += [f"ORACLE_{o}_{c}" for o in declared["oracle"]["orders"] for c in declared["oracle"]["costs"]]
    assert len(labels) == 12 and "FULL_K" in declared["static"] and online["windows"] == [32, 128]
    assert not np.array_equal(costs["MIX"], costs["AFF"]) and (params["gamma_M"], params["H"]) == (504, 250)
    changed = _b2q_desc((("parameters", "H"), 125), (("parameters", "alpha"), 0.1))
    moved, expected = changed["science"]["parameters"], 2.0 * math.log(125 / 0.1) / (125 * 20)
    assert (moved["H"], moved["alpha"], moved["K"], moved["gamma_M"]) == (125, 0.1, 20, 504)
    assert changed["science"]["policies"] == declared and abs(expected - B2Q_PRIOR) > 1e-4
    picks = [("RESIDUAL", "ONLINE_INFO_MIX_W128"), ("MARKET", "ONLINE_PREFIX_AFF_W32"),
             ("RESIDUAL", "ORACLE_INFO_MIX"), ("MARKET", "ORACLE_PREFIX_AFF"),
             ("RESIDUAL", "FULL_K"), ("MARKET", "FULL_K")]
    assert all(label in labels or label == "FULL_K" for _, label in picks)
    factory = _kernel("frozen_policy")
    kept = pdb.canon(changed)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        bundles = {(app, label): factory(desc, app, label) for app in ("RESIDUAL", "MARKET")
                   for label in [*labels, "FULL_K"]}
        moved_bundles = {(app, label): factory(changed, app, label) for app, label in picks}
    for (app, label), bundle in moved_bundles.items():
        policy = bundle["policy"]
        assert set(bundle) == B2Q_FIELDS and [bundle["label"], bundle["application"]] == [label, app]
        assert bundle["status"] == "RUNNABLE" and type(bundle["s2"]) is float
        assert bundle["s2"] == pytest.approx(expected, rel=1e-15) and bundle["s2"] != B2Q_PRIOR
        if label == "FULL_K":
            assert set(policy) == {"kind", "mask"} and policy["kind"] == "STATIC"
            assert policy["mask"].dtype == bool and policy["mask"].tolist() == [True] * 20
        elif label.startswith("ONLINE"):
            assert set(policy) == {"kind", "window", "cost", "order"} and policy["kind"] == "ONLINE"
            assert policy["window"] == int(label.split("_W")[1]) and type(policy["window"]) is int
            assert np.array_equal(policy["cost"], costs[label.split("_")[2]])
        else:
            assert set(policy) == {"kind", "H", "cost", "order"} and policy["kind"] == "ORACLE"
            assert [policy["H"], type(policy["H"])] == [125, int]
            assert np.array_equal(policy["cost"], costs[label.split("_")[2]])
    assert len({bundle["s2"] for bundle in moved_bundles.values()}) == 1 and pdb.canon(changed) == kept
    for (app, label), bundle in bundles.items():
        policy, parts = bundle["policy"], label.split("_")
        assert set(bundle) == B2Q_FIELDS and [bundle["label"], bundle["application"]] == [label, app]
        assert bundle["status"] == "RUNNABLE" and bundle["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15)
        if label == "FULL_K":
            assert set(policy) == {"kind", "mask"} and policy["kind"] == "STATIC" and policy["mask"].dtype == bool
            assert policy["mask"].tolist() == [True] * 20
        elif parts[0] == "ONLINE":
            assert set(policy) == {"kind", "window", "cost", "order"} and policy["kind"] == "ONLINE"
            assert [policy["order"], policy["window"], type(policy["window"])] == [parts[1], int(parts[3][1:]), int]
            assert np.array_equal(policy["cost"], costs[parts[2]])
        else:
            assert set(policy) == {"kind", "H", "cost", "order"} and policy["kind"] == "ORACLE"
            assert [policy["order"], policy["H"], type(policy["H"])] == [parts[1], 250, int]
            assert np.array_equal(policy["cost"], costs[parts[2]])
    Y, residual, market = np.zeros((1, 3, 20)), "RESIDUAL", "MARKET"
    assert len(bundles) == 26 and len({bundle["s2"] for bundle in bundles.values()}) == 1
    assert _kernel("nonoracle_masks")(Y, bundles[(residual, "ONLINE_INFO_MIX_W128")]["policy"]).shape == (1, 3, 20)
    assert _kernel("nonoracle_masks")(Y, bundles[(market, "FULL_K")]["policy"]).all()
    oracle = _kernel("oracle_masks")(np.zeros((1, 20)), bundles[(residual, "ORACLE_PREFIX_AFF")]["policy"])
    assert oracle.shape == (1, 250, 20)


def test_frozen_policy_keeps_supplied_spectral_rows_as_local_static_masks_or_their_statuses(monkeypatch):
    desc, lam = _b2q_desc(), _b2b_spectrum(24)
    rows = {app: _kernel("spectral_baselines")(lam, app)["baselines"] for app in ("RESIDUAL", "MARKET")}
    pcs = {(app, label): rows[app][label]["pcs"] for app in rows for label in B2Q_SPECTRAL}
    statuses = {key: rows[key[0]][key[1]]["status"] for key in pcs}
    assert pcs == {("RESIDUAL", "FIXED_EIGENMEAN_PREFIX"): list(range(2, 10)), ("RESIDUAL", "CPV90"): None,
                   ("RESIDUAL", "RESIDUAL_CPV90"): list(range(2, 17)),
                   ("MARKET", "FIXED_EIGENMEAN_PREFIX"): list(range(1, 8)), ("MARKET", "CPV90"): list(range(1, 16)),
                   ("MARKET", "RESIDUAL_CPV90"): None}
    assert statuses[("RESIDUAL", "CPV90")] == "OUTSIDE_UNIVERSE"
    assert statuses[("MARKET", "RESIDUAL_CPV90")] == "UNSUPPORTED"
    lo, snapshot, factory = {"RESIDUAL": 2, "MARKET": 1}, pdb.canon(rows), _kernel("frozen_policy")
    expected = {key: None if value is None else [k + lo[key[0]] in value for k in range(20)]
                for key, value in pcs.items()}
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        out = {key: factory(desc, key[0], key[1], baselines=rows[key[0]]) for key in pcs}
    for key, bundle in out.items():
        assert set(bundle) == B2Q_FIELDS and bundle["status"] == statuses[key]
        assert bundle["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15)
        if expected[key] is None:
            assert bundle["policy"] is None and bundle["status"] != "RUNNABLE"
        else:
            assert set(bundle["policy"]) == {"kind", "mask"} and bundle["policy"]["kind"] == "STATIC"
            assert bundle["policy"]["mask"].dtype == bool and bundle["policy"]["mask"].tolist() == expected[key]
    assert {sum(mask) for mask in expected.values() if mask} == {7, 8, 15} and pdb.canon(rows) == snapshot


def test_frozen_policy_builds_residual_dev_prefix_and_exante_masks_and_market_dev_statuses(monkeypatch):
    desc = _b2q_desc()
    params, grid = desc["science"]["parameters"], desc["science"]["dev"]["d_grid"]
    mix = _kernel("cost_vectors")(params["gamma_M"], params["K"])["MIX"]
    qbar, zeros = np.zeros(20), np.zeros(20)
    qbar[[1, 4]] = 0.5
    selected = [pdb.select_top_q(q, 20, mix)[1]["S"] for q in (qbar, zeros)]
    assert grid == [1, 2, 4, 8, 16, 20] and selected == [[1, 4], [0]]
    arrays, kept = _b2p_frozen(qbar, zeros, mix)
    factory = _kernel("frozen_policy")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp, selection=True)
        prefixes = {d: factory(desc, "RESIDUAL", "FIXED_DEV_PREFIX", d_dev=d) for d in (1, 4, 20)}
        exante = [factory(desc, "RESIDUAL", "FIXED_EXANTE_QBAR_MIX", qbar=q) for q in (qbar, zeros)]
        market = [factory(desc, "MARKET", label) for label in ("FIXED_DEV_PREFIX", "FIXED_EXANTE_QBAR_MIX")]
    for d, bundle in prefixes.items():
        assert bundle["status"] == "RUNNABLE" and bundle["policy"]["mask"].tolist() == [k < d for k in range(20)]
    for bundle, chosen in zip(exante, selected):
        assert bundle["status"] == "RUNNABLE" and bundle["policy"]["mask"].tolist() == [k in chosen for k in range(20)]
    assert [(b["status"], b["policy"]) for b in market] == [("NOT_RUN", None), ("UNSUPPORTED", None)]
    bundles = [*prefixes.values(), *exante, *market]
    assert all(set(b) == B2Q_FIELDS and b["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15) for b in bundles)
    assert all(set(b["policy"]) == {"kind", "mask"} and b["policy"]["kind"] == "STATIC" for b in bundles[:5])
    assert all(b["policy"]["mask"].dtype == bool for b in bundles[:5]) and len({b["s2"] for b in bundles}) == 1
    assert [a.tobytes() for a in arrays] == kept


@pytest.mark.parametrize("case", B2Q_REFUSALS)
def test_frozen_policy_refuses_undeclared_labels_and_malformed_frozen_inputs_directly(monkeypatch, case):
    (application, label, kind), desc = B2Q_REFUSALS[case], _b2q_desc()
    declared, grid = desc["science"]["policies"], desc["science"]["dev"]["d_grid"]
    rows = _kernel("spectral_baselines")(_b2b_spectrum(24), "RESIDUAL")["baselines"]
    valid = np.linspace(0.0, 0.5, 20)
    poisoned = {"runnable_without_pcs": {**rows, "RESIDUAL_CPV90": {"status": "RUNNABLE", "pcs": None}},
                "pc1_in_residual": {**rows, "CPV90": {"status": "RUNNABLE", "pcs": list(range(1, 16)), "k90": 15}}}
    kwargs = {"d_dev_3": {"d_dev": 3}, "d_dev_true": {"d_dev": True}, "qbar_short": {"qbar": valid[:19]},
              "qbar_negative": {"qbar": np.where(np.arange(20) == 3, -0.125, valid)}}.get(kind, {})
    kwargs = {"baselines": poisoned[kind]} if kind in poisoned else kwargs
    assert "FIXED_KAISER_PREFIX" not in declared["static"] and 64 not in declared["online"]["windows"]
    assert "LIN" not in declared["oracle"]["costs"] and "OTHER" not in desc["science"]["applications"] and 3 not in grid
    assert rows["CPV90"]["status"] == "OUTSIDE_UNIVERSE" and rows["RESIDUAL_CPV90"]["status"] == "RUNNABLE"
    arrays, kept = _b2p_frozen(*(value for value in kwargs.values() if isinstance(value, np.ndarray)))
    plain = pdb.canon({key: value for key, value in kwargs.items() if not isinstance(value, np.ndarray)})
    factory, snapshot = _kernel("frozen_policy"), pdb.canon(desc)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        with pytest.raises(ValueError):
            factory(desc, application, label, **kwargs)
    assert [a.tobytes() for a in arrays] == kept and pdb.canon(desc) == snapshot
    assert pdb.canon({key: value for key, value in kwargs.items() if not isinstance(value, np.ndarray)}) == plain


B2R_FIELDS = {"W", "first", "mask_bits"}
B2R_REFUSALS = {"nonrunnable_status": ("nonoracle", True, 0), "runnable_without_policy": ("nonoracle", True, 0),
                "extra_bundle_field": ("nonoracle", True, 0), "missing_bundle_field": ("nonoracle", True, 0),
                "s2_bool": ("nonoracle", True, 0), "s2_zero": ("nonoracle", True, 0), "s2_nan": ("nonoracle", True, 0),
                "s2_text": ("oracle", True, 0), "inner_extra_field": ("nonoracle", False, 0),
                "oracle_bundle_to_nonoracle": ("nonoracle", False, 0), "online_bundle_to_oracle": ("oracle", False, 0),
                "local_width_19": ("nonoracle", False, 0), "scores_two_dimensional": ("nonoracle", False, 0),
                "scores_nonfinite": ("nonoracle", False, 0), "oracle_q_wrong_k": ("oracle", False, 0),
                "oracle_horizon_mismatch": ("oracle", False, 1), "threshold_nan": ("nonoracle", False, 1)}


def _b2r_static_scores():
    Y = np.zeros((2, 6, 20))
    Y[0, :, 0], Y[0, :, 19] = 4.0, 4.0
    return Y


def _b2r_online_ref(Y, window, cost, order):
    select, costs = (_greedy if order == "INFO" else _prefix), [float(c) for c in cost]
    M = np.zeros(Y.shape, dtype=bool)
    for b, path in enumerate(Y):
        for t in range(Y.shape[1]):
            m = min(window, t)
            if m == 0:
                S = [0]
            else:
                mean = [math.fsum(float(y[k]) for y in path[t - m:t]) / m for k in range(Y.shape[2])]
                S = select([0.5 * max(0.0, mu * mu - 1.0 / m) for mu in mean], costs)[1]
            M[b, t, S] = True
    return M


def _b2r_bits(M):
    B, H, K = M.shape
    rows = [[sum(1 << k for k in range(K) if M[b, t, k]) for t in range(H)] for b in range(B)]
    return np.array(rows, dtype=np.uint32).reshape(B, H)


def _b2r_spies(mp, calls):
    import inspect
    module = pio()
    real = {name: getattr(module, name) for name in ("nonoracle_masks", "oracle_masks", "masked_scan")}

    def spy(name):
        signature = inspect.signature(real[name])

        def wrapped(*args, **kwargs):
            calls.append((name, dict(signature.bind(*args, **kwargs).arguments)))
            return real[name](*args, **kwargs)

        return wrapped

    for name in real:
        mp.setattr(module, name, spy(name))


def _b2r_traps(mp):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("prior recomputation, policy regeneration, generation, fit or calibration inside a scan")

    for owner, name in ((module, "common_prior"), (module, "frozen_policy"), (module, "population_frame"),
                        (module, "null_returns"), (module, "exact_scores"), (module, "path_scores"),
                        (module, "direction_draws"), (module, "direction_information"), (module, "dev_qbar"),
                        (module, "fit_record"), (module, "spectral_baselines"), (pdb, "fit_basis"),
                        (pdb, "rank_threshold"), (pdb, "scan_statistic"), (pdb.sim, "t_innov")):
        mp.setattr(owner, name, forbidden)


def _b2r_freeze(bundle):
    policy = bundle["policy"] if isinstance(bundle.get("policy"), dict) else {}
    arrays = [value for value in policy.values() if isinstance(value, np.ndarray)]
    for array in arrays:
        array.flags.writeable = False
    plain = {key: value for key, value in policy.items() if not isinstance(value, np.ndarray)}
    outer = {key: value for key, value in bundle.items() if key != "policy"}
    return repr(outer), repr(plain), [array.tobytes() for array in arrays]


def test_nonoracle_scan_passes_the_supplied_prior_unchanged_to_one_real_static_scan(monkeypatch):
    desc, factory, scan = _b2q_desc(), _kernel("frozen_policy"), _kernel("masked_scan")
    s2, mix = _kernel("common_prior")(desc), _kernel("cost_vectors")(504, 20)["MIX"]
    qbar = np.zeros(20)
    qbar[[0, 19]] = 0.5
    bundles = {"dev_1": factory(desc, "RESIDUAL", "FIXED_DEV_PREFIX", d_dev=1),
               "dev_4": factory(desc, "RESIDUAL", "FIXED_DEV_PREFIX", d_dev=4),
               "full_k": factory(desc, "MARKET", "FULL_K"),
               "exante": factory(desc, "RESIDUAL", "FIXED_EXANTE_QBAR_MIX", qbar=qbar)}
    masks, Y = {name: bundle["policy"]["mask"] for name, bundle in bundles.items()}, _b2r_static_scores()
    bits = {name: _b2r_bits(np.broadcast_to(mask, Y.shape)) for name, mask in masks.items()}
    assert [int(mask.sum()) for mask in masks.values()] == [1, 4, 20, 2]
    assert pdb.select_top_q(qbar, 20, mix)[1]["S"] == [0, 19] and s2 == pytest.approx(B2Q_PRIOR, rel=1e-15)
    assert bits["exante"][0, 0] == 2 ** 0 + 2 ** 19 != 2 ** 2 + 2 ** 21
    assert bits["dev_4"][0, 0] == 15 != sum(2 ** (19 - k) for k in range(4)) and (bits["full_k"] == 2 ** 20 - 1).all()
    cases, expected = [(name, prior) for name in bundles for prior in (s2, 4.0 * s2)], {}
    for name, prior in cases:
        M = np.broadcast_to(masks[name], Y.shape)
        W = scan(Y, M, prior)[0]
        assert W[0, 0] < W[0, 1] < W[0, 2] < W[0, 3] and int(np.argmax(W[0])) == 5 and (W[1] < 0).all()
        expected[(name, prior)] = (M, W, W[0, 2], [_first(W[b], W[0, 2]) for b in range(2)])
    assert all(value[3] == [3, -1] for value in expected.values())
    assert all(not np.allclose(expected[(name, s2)][1], expected[(name, 4.0 * s2)][1]) for name in bundles)
    frozen = [_b2r_freeze(bundle) for bundle in bundles.values()]
    Y.flags.writeable = False
    nonoracle, calls, kept = _kernel("nonoracle_scan"), [], Y.tobytes()
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2r_spies(mp, calls)
        outs = {key: nonoracle(Y, {**bundles[key[0]], "s2": key[1]}, expected[key][2]) for key in cases}
    for key, out in outs.items():
        M, W, h, first = expected[key]
        assert set(out) == B2R_FIELDS and np.array_equal(out["W"], W) and out["first"].tolist() == first
        np.testing.assert_allclose(out["W"], _ref_W(Y, M, key[1]), rtol=1e-12, atol=1e-12)
        assert out["mask_bits"].dtype == np.uint32 and np.array_equal(out["mask_bits"], bits[key[0]])
    scans = [arguments for name, arguments in calls if name == "masked_scan"]
    assert [name for name, _ in calls] == ["nonoracle_masks", "masked_scan"] * len(cases)
    assert [(a["s2"], a.get("h")) for a in scans] == [(key[1], expected[key][2]) for key in cases]
    assert [_b2r_freeze(bundle) for bundle in bundles.values()] == frozen and Y.tobytes() == kept


def test_nonoracle_scan_keeps_one_real_online_mask_sequence_and_its_past_only_scan(monkeypatch):
    desc, factory, scan = _b2q_desc(), _kernel("frozen_policy"), _kernel("masked_scan")
    s2 = _kernel("common_prior")(desc)
    bundles = {order: factory(desc, "RESIDUAL", f"ONLINE_{order}_MIX_W128") for order in ("INFO", "PREFIX")}
    cost, Y = bundles["INFO"]["policy"]["cost"], np.zeros((2, 6, 20))
    Y[0, :, 7] = 3.0
    later = Y.copy()
    later[0, 4, 7] = -10.0
    refs = {order: _b2r_online_ref(Y, 128, cost, order) for order in bundles}
    assert refs["INFO"][0, 0].tolist() == [k == 0 for k in range(20)] == refs["PREFIX"][0, 0].tolist()
    assert refs["INFO"][0, 1:].sum(axis=0).tolist() == [5 * (k == 7) for k in range(20)]
    assert refs["PREFIX"][0, 1].tolist() == [k <= 7 for k in range(20)] and refs["INFO"][1].sum() == 6
    assert all(np.array_equal(_kernel("online_masks")(Y, 128, cost, order), refs[order]) for order in refs)
    cases, expected = [(order, prior) for order in bundles for prior in (s2, 4.0 * s2)], {}
    for order, prior in cases:
        W = scan(Y, refs[order], prior)[0]
        assert W[0, 0] < W[0, 1] < W[0, 2] < W[0, 3] < W[0, 4] < W[0, 5] and (W[1] < 0).all()
        expected[(order, prior)] = (W, W[0, 3], [_first(W[b], W[0, 3]) for b in range(2)])
    assert all(value[2] == [4, -1] for value in expected.values())
    assert not np.allclose(expected[("INFO", s2)][0], expected[("INFO", 4.0 * s2)][0])
    assert not np.array_equal(refs["INFO"], refs["PREFIX"])
    frozen = [_b2r_freeze(bundle) for bundle in bundles.values()]
    for array in (Y, later):
        array.flags.writeable = False
    nonoracle, calls, kept = _kernel("nonoracle_scan"), [], [Y.tobytes(), later.tobytes()]
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2r_spies(mp, calls)
        outs = {key: nonoracle(Y, {**bundles[key[0]], "s2": key[1]}, expected[key][1]) for key in cases}
        moved = nonoracle(later, bundles["INFO"], expected[("INFO", s2)][1])
    for key, out in outs.items():
        W, h, first = expected[key]
        assert set(out) == B2R_FIELDS and np.array_equal(out["W"], W) and out["first"].tolist() == first
        np.testing.assert_allclose(out["W"], _ref_W(Y, refs[key[0]], key[1]), rtol=1e-12, atol=1e-12)
        assert out["mask_bits"].dtype == np.uint32 and np.array_equal(out["mask_bits"], _b2r_bits(refs[key[0]]))
    base = outs[("INFO", s2)]
    assert np.array_equal(moved["W"][:, :4], base["W"][:, :4]) and moved["W"][0, 4] != base["W"][0, 4]
    assert np.array_equal(moved["mask_bits"][:, :5], base["mask_bits"][:, :5]) and moved["first"].tolist() == [4, -1]
    assert [name for name, _ in calls] == ["nonoracle_masks", "masked_scan"] * (len(cases) + 1)
    assert [a["s2"] for name, a in calls if name == "masked_scan"] == [key[1] for key in cases] + [s2]
    assert [_b2r_freeze(bundle) for bundle in bundles.values()] == frozen and [Y.tobytes(), later.tobytes()] == kept


def test_oracle_scan_uses_the_supplied_true_q_of_each_path_with_the_supplied_prior(monkeypatch):
    desc, scan = _b2q_desc((("parameters", "H"), 5)), _kernel("masked_scan")
    s2, bundle = _kernel("common_prior")(desc), _kernel("frozen_policy")(desc, "RESIDUAL", "ORACLE_INFO_MIX")
    cost, q_true, Y = bundle["policy"]["cost"], np.zeros((2, 20)), np.zeros((2, 5, 20))
    q_true[0, 3], q_true[1, [12, 17]], Y[0, :, 3], Y[1, :, 12] = 0.5, 0.5, 2.0, 1.0
    chosen, M = [_greedy(q.tolist(), cost.tolist())[1] for q in q_true], np.zeros((2, 5, 20), dtype=bool)
    M[0][:, chosen[0]], M[1][:, chosen[1]] = True, True
    assert chosen == [[3], [12, 17]] and bundle["policy"]["H"] == 5
    assert s2 == pytest.approx(2.0 * math.log(100.0) / 100.0, rel=1e-15)
    assert np.array_equal(_kernel("oracle_masks")(q_true, bundle["policy"]), M)
    expected = {}
    for prior in (s2, 4.0 * s2):
        W = scan(Y, M, prior)[0]
        assert W[0, 0] < W[0, 1] < W[0, 2] and (W[1] < W[0, 1]).all()
        expected[prior] = (W, W[0, 1], [_first(W[b], W[0, 1]) for b in range(2)])
    assert expected[s2][2] == expected[4.0 * s2][2] == [2, -1]
    assert not np.allclose(expected[s2][0], expected[4.0 * s2][0])
    frozen, kept = _b2r_freeze(bundle), [Y.tobytes(), q_true.tobytes()]
    for array in (Y, q_true):
        array.flags.writeable = False
    oracle, calls = _kernel("oracle_scan"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2r_spies(mp, calls)
        outs = {prior: oracle(Y, q_true, {**bundle, "s2": prior}, expected[prior][1]) for prior in expected}
    for prior, out in outs.items():
        W, h, first = expected[prior]
        assert set(out) == B2R_FIELDS and np.array_equal(out["W"], W) and out["first"].tolist() == first
        np.testing.assert_allclose(out["W"], _ref_W(Y, M, prior), rtol=1e-12, atol=1e-12)
        assert out["mask_bits"].dtype == np.uint32 and out["mask_bits"].tolist() == [[2 ** 3] * 5, [2 ** 12 + 2 ** 17] * 5]
    assert [name for name, _ in calls] == ["oracle_masks", "masked_scan"] * 2
    assert [(a["s2"], a.get("h")) for name, a in calls if name == "masked_scan"] == [(p, expected[p][1]) for p in expected]
    assert all(np.array_equal(a["q_true"], q_true) for name, a in calls if name == "oracle_masks")
    assert _b2r_freeze(bundle) == frozen and [Y.tobytes(), q_true.tobytes()] == kept


def test_scans_censor_none_and_infinite_thresholds_keep_empty_batches_and_numerical_errors(monkeypatch):
    desc, short, scan = _b2q_desc(), _b2q_desc((("parameters", "H"), 5)), _kernel("masked_scan")
    full = _kernel("frozen_policy")(desc, "MARKET", "FULL_K")
    oracle_bundle = _kernel("frozen_policy")(short, "RESIDUAL", "ORACLE_PREFIX_MIX")
    Y, big = _b2r_static_scores(), _b2r_static_scores()
    big[0, :, 0] = 1e200
    W = scan(Y, np.ones(Y.shape, dtype=bool), full["s2"])[0]
    assert [_first(W[b], -1.0) for b in range(2)] == [1, 1] and np.isfinite(W).all() and W.min() > -1.0
    with pytest.raises(ArithmeticError):
        scan(big, np.ones(big.shape, dtype=bool), full["s2"])
    nonoracle, oracle = _kernel("nonoracle_scan"), _kernel("oracle_scan")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        censored = [nonoracle(Y, full), nonoracle(Y, full, None), nonoracle(Y, full, math.inf)]
        negative = nonoracle(Y, full, -1.0)
        empty = nonoracle(np.zeros((0, 6, 20)), full, 0.5)
        empty_oracle = oracle(np.zeros((0, 5, 20)), np.zeros((0, 20)), oracle_bundle, 0.5)
        with pytest.raises(ArithmeticError):
            nonoracle(big, full, 0.5)
    for out in censored:
        assert set(out) == B2R_FIELDS and np.array_equal(out["W"], W) and out["first"].tolist() == [-1, -1]
    assert negative["first"].tolist() == [1, 1] and np.array_equal(negative["W"], W)
    for out, H in ((empty, 6), (empty_oracle, 5)):
        assert set(out) == B2R_FIELDS and out["W"].shape == (0, H) and out["W"].dtype == np.float64
        assert out["first"].shape == (0,) and out["first"].dtype.kind == "i"
        assert out["mask_bits"].shape == (0, H) and out["mask_bits"].dtype == np.uint32


@pytest.mark.parametrize("case", B2R_REFUSALS)
def test_scans_refuse_nonrunnable_or_malformed_bundles_scores_and_priors_without_fallback(monkeypatch, case):
    (kind, pre, allowed), factory = B2R_REFUSALS[case], _kernel("frozen_policy")
    desc, short = _b2q_desc(), _b2q_desc((("parameters", "H"), 5))
    full, online = factory(desc, "MARKET", "FULL_K"), factory(desc, "RESIDUAL", "ONLINE_INFO_MIX_W128")
    oracle_bundle = factory(short, "RESIDUAL", "ORACLE_INFO_MIX")
    not_run = factory(desc, "MARKET", "FIXED_DEV_PREFIX")
    Y, q_true, h = _b2r_static_scores(), np.zeros((2, 20)), 0.5
    if kind == "oracle" and case != "oracle_horizon_mismatch":
        Y = np.ascontiguousarray(Y[:, :5])
    assert (not_run["status"], not_run["policy"]) == ("NOT_RUN", None) and oracle_bundle["policy"]["H"] == 5
    assert _kernel("nonoracle_masks")(_b2r_static_scores(), full["policy"]).shape == (2, 6, 20)
    assert _kernel("oracle_masks")(q_true, oracle_bundle["policy"]).shape == (2, 5, 20)
    bundle = oracle_bundle if kind == "oracle" else full
    priors = {"s2_bool": True, "s2_zero": 0.0, "s2_nan": math.nan, "s2_text": "0.0034"}
    if case in priors:
        bundle = {**bundle, "s2": priors[case]}
    elif case == "nonrunnable_status":
        bundle = not_run
    elif case == "runnable_without_policy":
        bundle = {**full, "policy": None}
    elif case == "extra_bundle_field":
        bundle = {**full, "dev_id": "0" * 16}
    elif case == "missing_bundle_field":
        bundle = {key: value for key, value in full.items() if key != "label"}
    elif case == "inner_extra_field":
        bundle = {**full, "policy": {**full["policy"], "s2": full["s2"]}}
    elif case == "oracle_bundle_to_nonoracle":
        bundle = oracle_bundle
    elif case == "online_bundle_to_oracle":
        bundle = online
    elif case == "local_width_19":
        Y = np.ascontiguousarray(Y[:, :, :19])
    elif case == "scores_two_dimensional":
        Y = np.ascontiguousarray(Y[0])
    elif case == "scores_nonfinite":
        Y[1, 2, 5] = math.nan
    elif case == "oracle_q_wrong_k":
        q_true = np.zeros((2, 19))
    elif case == "threshold_nan":
        h = math.nan
    kept, arrays = _b2r_freeze(bundle), [Y, q_true]
    for array in arrays:
        array.flags.writeable = False
    data, calls = [array.tobytes() for array in arrays], []
    target = _kernel("oracle_scan" if kind == "oracle" else "nonoracle_scan")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2r_spies(mp, calls)
        with pytest.raises(ValueError):
            if kind == "oracle":
                target(Y, q_true, bundle, h)
            else:
                target(Y, bundle, h)
    assert sum(name == "masked_scan" for name, _ in calls) <= allowed and (not pre or not calls)
    assert _b2r_freeze(bundle) == kept and [array.tobytes() for array in arrays] == data


@pytest.mark.parametrize(("kind", "name", "poison"), [("nonoracle", "Y", "complex"), ("nonoracle", "Y", "text"),
                                                      ("oracle", "Y", "complex"), ("oracle", "Y", "text"),
                                                      ("oracle", "q_true", "complex"), ("oracle", "q_true", "text")])
def test_scans_refuse_complex_or_numeric_text_scores_and_true_q_before_masks_or_scan(monkeypatch, kind, name, poison):
    factory = _kernel("frozen_policy")
    full = factory(_b2q_desc(), "MARKET", "FULL_K")
    oracle_bundle = factory(_b2q_desc((("parameters", "H"), 5)), "RESIDUAL", "ORACLE_INFO_MIX")
    bundle, Y, q_true = (oracle_bundle if kind == "oracle" else full), _b2r_static_scores(), np.zeros((2, 20))
    q_true[0, 3], q_true[1, [12, 17]] = 0.5, 0.5
    if kind == "oracle":
        Y = np.ascontiguousarray(Y[:, :5])
        M = _kernel("oracle_masks")(q_true, bundle["policy"])
    else:
        M = _kernel("nonoracle_masks")(Y, bundle["policy"])
    W = _kernel("masked_scan")(Y, M, bundle["s2"])[0]
    assert M.shape == Y.shape == (2, 5 if kind == "oracle" else 6, 20) and np.isfinite(W).all()
    assert Y.dtype.kind == q_true.dtype.kind == "f" and np.isfinite(Y).all() and np.isfinite(q_true).all()
    arrays = {"Y": Y, "q_true": q_true}
    clean = arrays[name]
    bad = arrays[name] = clean + 1j if poison == "complex" else clean.astype(str)
    assert bad.shape == clean.shape and bad.dtype.kind == {"complex": "c", "text": "U"}[poison]
    if poison == "complex":
        assert (bad.imag == 1.0).all() and np.array_equal(bad.real, clean) and np.isfinite(bad).all()
    else:
        assert all(type(v) is str for v in bad.ravel().tolist()) and np.array_equal(bad.astype(np.float64), clean)
    kept = _b2r_freeze(bundle)
    for array in arrays.values():
        array.flags.writeable = False
    data, calls, target = [array.tobytes() for array in arrays.values()], [], _kernel(f"{kind}_scan")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2r_spies(mp, calls)
        with pytest.raises(ValueError):
            if kind == "oracle":
                target(arrays["Y"], arrays["q_true"], bundle, 0.5)
            else:
                target(arrays["Y"], bundle, 0.5)
    assert calls == [] and _b2r_freeze(bundle) == kept and [array.tobytes() for array in arrays.values()] == data


def test_scans_admit_real_integer_scores_and_true_q_against_scalar_and_bit_references(monkeypatch):
    factory, scan = _kernel("frozen_policy"), _kernel("masked_scan")
    static = factory(_b2q_desc(), "RESIDUAL", "FIXED_DEV_PREFIX", d_dev=4)
    bundle = factory(_b2q_desc((("parameters", "H"), 5)), "RESIDUAL", "ORACLE_INFO_MIX")
    Y6, Y5 = _b2r_static_scores().astype(np.int64), np.zeros((2, 5, 20), dtype=np.int64)
    q_true = np.zeros((2, 20), dtype=np.uint8)
    q_true[0, 3], q_true[1, [12, 17]], Y5[0, :, 3], Y5[1, :, 12] = 2, 1, 2, 1
    chosen = [_greedy(q.tolist(), bundle["policy"]["cost"].tolist())[1] for q in q_true]
    M6, M5 = np.broadcast_to(static["policy"]["mask"], Y6.shape), np.zeros(Y5.shape, dtype=bool)
    M5[0][:, chosen[0]], M5[1][:, chosen[1]] = True, True
    assert [Y6.dtype.kind, Y5.dtype.kind, q_true.dtype.kind] == ["i", "i", "u"] and chosen == [[3], [12, 17]]
    assert np.array_equal(Y6, _b2r_static_scores()) and bundle["policy"]["H"] == 5
    assert np.array_equal(_kernel("nonoracle_masks")(Y6, static["policy"]), M6)
    assert np.array_equal(_kernel("oracle_masks")(q_true, bundle["policy"]), M5)
    assert static["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15)
    assert bundle["s2"] == pytest.approx(2.0 * math.log(100.0) / 100.0, rel=1e-15)
    cases = [(Y6, M6, static["s2"]), (Y5, M5, bundle["s2"])]
    (W6, W5), bits = [scan(*case)[0] for case in cases], [_b2r_bits(M6), _b2r_bits(M5)]
    for (Y, M, s2), W in zip(cases, (W6, W5)):
        np.testing.assert_allclose(W, _ref_W(Y, M, s2), rtol=1e-12, atol=1e-12)
    h6, h5 = W6[0, 2], W5[0, 1]
    assert [[_first(W6[b], h6) for b in range(2)], [_first(W5[b], h5) for b in range(2)]] == [[3, -1], [2, -1]]
    assert (bits[0] == 15).all() and bits[1].tolist() == [[2 ** 3] * 5, [2 ** 12 + 2 ** 17] * 5]
    frozen, arrays = [_b2r_freeze(static), _b2r_freeze(bundle)], [Y6, Y5, q_true]
    for array in arrays:
        array.flags.writeable = False
    kept = [(array.dtype, array.tobytes()) for array in arrays]
    nonoracle, oracle = _kernel("nonoracle_scan"), _kernel("oracle_scan")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        outs = [nonoracle(Y6, static, None), nonoracle(Y6, static, h6), oracle(Y5, q_true, bundle, h5),
                oracle(Y5, q_true, bundle, math.inf)]
    expected = [(cases[0], W6, bits[0], [-1, -1]), (cases[0], W6, bits[0], [3, -1]),
                (cases[1], W5, bits[1], [2, -1]), (cases[1], W5, bits[1], [-1, -1])]
    for out, ((Y, M, s2), W, mask_bits, first) in zip(outs, expected):
        assert set(out) == B2R_FIELDS and np.array_equal(out["W"], W) and out["first"].tolist() == first
        np.testing.assert_allclose(out["W"], _ref_W(Y, M, s2), rtol=1e-12, atol=1e-12)
        assert out["mask_bits"].dtype == np.uint32 and np.array_equal(out["mask_bits"], mask_bits)
    assert [_b2r_freeze(static), _b2r_freeze(bundle)] == frozen and [(a.dtype, a.tobytes()) for a in arrays] == kept
    assert not any(array.flags.writeable for array in arrays)


def _b2s_forbid(mp, *names):
    def forbidden(*args, **kwargs):
        raise AssertionError("primary regeneration, prior, selection or cost computation inside gamma sensitivity")

    for owner, name in [(pio(), name) for name in names] + [(pdb, name) for name in names if hasattr(pdb, name)]:
        mp.setattr(owner, name, forbidden)


@pytest.mark.parametrize("order", ("INFO", "PREFIX"))
def test_gamma_sensitivity_policy_moves_only_the_online_mix_w128_cost_to_m_of_h_over_alpha(monkeypatch, order):
    configs = [_b2q_desc(), _b2q_desc((("parameters", "H"), 125), (("parameters", "alpha"), 0.1),
                                      (("parameters", "gamma_M_sensitivity"), 1250))]
    label, factory, prior = f"ONLINE_{order}_MIX_W128", _kernel("frozen_policy"), _kernel("common_prior")
    base, cases = [pdb.mixture_cost(d, 504) for d in range(1, 21)], []
    for desc in configs:
        params, primary = desc["science"]["parameters"], factory(desc, "RESIDUAL", label)
        gamma, policy = params["H"] / params["alpha"], primary["policy"]
        sens = [pdb.mixture_cost(d, gamma) for d in range(1, 21)]
        assert [params["K"], params["gamma_M"], params["gamma_M_sensitivity"]] == [20, 504, gamma]
        assert set(primary) == B2Q_FIELDS and primary["status"] == "RUNNABLE" and primary["s2"] == prior(desc)
        assert set(policy) == {"kind", "window", "cost", "order"} and policy["kind"] == "ONLINE"
        assert [policy["window"], type(policy["window"]), policy["order"]] == [128, int, order]
        assert np.array_equal(policy["cost"], base) and all(a != b for a, b in zip(sens, base))
        cases.append((desc, primary, sens, _b2r_freeze(primary), pdb.canon(desc)))
    assert [case[0]["science"]["parameters"]["gamma_M_sensitivity"] for case in cases] == [5000, 1250]
    assert all(a != b for a, b in zip(cases[0][2], cases[1][2])) and cases[0][1]["s2"] != cases[1][1]["s2"]
    sensitivity, fields = _kernel("gamma_sensitivity_policy"), ("label", "application", "status", "s2")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        _b2s_forbid(mp, "frozen_policy", "common_prior")
        outs = [sensitivity(desc, primary) for desc, primary, _, _, _ in cases]
    for out, (desc, primary, sens, frozen, kept) in zip(outs, cases):
        policy = out["policy"]
        assert set(out) == B2Q_FIELDS and [out[f] for f in fields] == [primary[f] for f in fields]
        assert set(policy) == {"kind", "window", "cost", "order"} and policy is not primary["policy"]
        assert [policy["kind"], policy["window"], policy["order"]] == ["ONLINE", 128, order]
        assert type(policy["window"]) is int and policy["cost"].dtype == np.float64
        assert np.array_equal(policy["cost"], sens)
        assert not np.array_equal(policy["cost"], primary["policy"]["cost"])
        assert _b2r_freeze(primary) == frozen and pdb.canon(desc) == kept
    assert not np.array_equal(outs[0]["policy"]["cost"], outs[1]["policy"]["cost"])


def test_gamma_sensitivity_policy_keeps_static_primary_bundles_without_selection_or_cost(monkeypatch):
    desc, factory = _b2q_desc(), _kernel("frozen_policy")
    rows = _kernel("spectral_baselines")(_b2b_spectrum(24), "RESIDUAL")["baselines"]
    qbar, mix = np.zeros(20), [pdb.mixture_cost(d, 504) for d in range(1, 21)]
    qbar[[0, 19]] = 0.5
    chosen = pdb.select_top_q(qbar, 20, mix)[1]["S"]
    bundles = [factory(desc, "RESIDUAL", "FULL_K"), factory(desc, "RESIDUAL", "FIXED_EXANTE_QBAR_MIX", qbar=qbar),
               factory(desc, "RESIDUAL", "CPV90", baselines=rows)]
    full, exante, outside = bundles
    assert chosen == [0, 19] and [rows["CPV90"]["status"], rows["CPV90"]["pcs"]] == ["OUTSIDE_UNIVERSE", None]
    assert [b["status"] for b in bundles] == ["RUNNABLE", "RUNNABLE", "OUTSIDE_UNIVERSE"]
    assert outside["policy"] is None and full["policy"]["mask"].tolist() == [True] * 20
    assert full["policy"]["kind"] == exante["policy"]["kind"] == "STATIC"
    assert exante["policy"]["mask"].tolist() == [k in chosen for k in range(20)]
    assert all(set(b) == B2Q_FIELDS and b["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15) for b in bundles)
    frozen, kept = [_b2r_freeze(b) for b in bundles], pdb.canon(desc)
    qbar.flags.writeable = False
    sensitivity, fields = _kernel("gamma_sensitivity_policy"), ("label", "application", "status", "s2")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        _b2s_forbid(mp, "frozen_policy", "common_prior", "cost_vectors", "affine_ols", "mixture_cost")
        outs = [sensitivity(desc, b) for b in bundles]
    for out, bundle in zip(outs, bundles):
        assert set(out) == B2Q_FIELDS and [out[f] for f in fields] == [bundle[f] for f in fields]
        if bundle["policy"] is None:
            assert out["policy"] is None
        else:
            assert set(out["policy"]) == {"kind", "mask"} and out["policy"]["kind"] == "STATIC"
            mask = out["policy"]["mask"]
            assert mask.dtype == bool and np.array_equal(mask, bundle["policy"]["mask"])
    assert outs[1]["policy"]["mask"].tolist() == [k in chosen for k in range(20)]
    assert [_b2r_freeze(b) for b in bundles] == frozen and pdb.canon(desc) == kept


B2S_GUARDS = {"static_unknown_status": ("MARKET", "FIXED_DEV_PREFIX", "bundle", "status", "PENDING"),
              "online_s2_bool": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "bundle", "s2", True),
              "online_s2_text": ("MARKET", "ONLINE_PREFIX_MIX_W128", "bundle", "s2", "0.0034"),
              "static_s2_nan": ("RESIDUAL", "FULL_K", "bundle", "s2", math.nan),
              "static_s2_zero": ("MARKET", "FULL_K", "bundle", "s2", 0.0),
              "extra_outer_field": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "bundle", "policy_rule_id", "0" * 16),
              "online_cost_19": ("RESIDUAL", "ONLINE_PREFIX_MIX_W128", "policy", "cost", "cut19"),
              "static_mask_19": ("RESIDUAL", "FULL_K", "policy", "mask", "cut19"),
              "static_mask_float": ("MARKET", "FULL_K", "policy", "mask", "float"),
              "online_desc_k19": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "desc", "K", 19),
              "gamma_stale_1250": ("RESIDUAL", "ONLINE_PREFIX_MIX_W128", "desc", "gamma_M_sensitivity", 1250),
              "gamma_bool": ("MARKET", "ONLINE_INFO_MIX_W128", "desc", "gamma_M_sensitivity", True),
              "gamma_text": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "desc", "gamma_M_sensitivity", "5000"),
              "gamma_nan": ("RESIDUAL", "ONLINE_PREFIX_MIX_W128", "desc", "gamma_M_sensitivity", math.nan),
              "gamma_missing": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "desc", "gamma_M_sensitivity", None),
              "h_float": ("MARKET", "ONLINE_PREFIX_MIX_W128", "desc", "H", 250.0),
              "alpha_text": ("RESIDUAL", "ONLINE_INFO_MIX_W128", "desc", "alpha", "0.05"),
              "online_aff_w128": ("RESIDUAL", "ONLINE_INFO_AFF_W128", "variant", None, None),
              "online_mix_w32": ("MARKET", "ONLINE_PREFIX_MIX_W32", "variant", None, None),
              "oracle_info_mix": ("RESIDUAL", "ORACLE_INFO_MIX", "variant", None, None)}


@pytest.mark.parametrize("case", B2S_GUARDS)
def test_gamma_sensitivity_policy_refuses_one_forged_field_or_unplanned_variant_before_any_cost(monkeypatch, case):
    (application, label, where, key, value), desc = B2S_GUARDS[case], _b2q_desc()
    params, module, calls = desc["science"]["parameters"], pio(), []
    base, real = _kernel("frozen_policy")(desc, application, label), module.cost_vectors
    online, target = label.endswith("_MIX_W128"), desc
    arrays = [v for v in (base["policy"] or {}).values() if isinstance(v, np.ndarray)]
    assert [params[k] for k in ("H", "alpha", "K", "gamma_M", "gamma_M_sensitivity")] == [250, 0.05, 20, 504, 5000]
    assert set(base) == B2Q_FIELDS and base["label"] == label and base["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15)
    assert base["status"] == ("NOT_RUN" if label == "FIXED_DEV_PREFIX" else "RUNNABLE")
    assert len(arrays) == (0 if base["policy"] is None else 1)
    assert all(a.shape == (20,) and a.dtype in (np.float64, bool) for a in arrays)
    frozen_base, bundle = _b2r_freeze(base), base
    if where == "desc":
        trimmed = {k: v for k, v in params.items() if k != key}
        target = _edited(desc, ("science", "parameters"), trimmed if value is None else {**trimmed, key: value})
        moved = target["science"]["parameters"]
        assert (key not in moved) if value is None else (moved[key] is value and params[key] is not value)
    elif where == "bundle":
        bundle = {**base, key: value}
        assert bundle[key] is value and base.get(key) is not value
    elif where == "policy":
        array = base["policy"][key]
        forged = array[:19] if value == "cut19" else array.astype(np.float64)
        bundle = {**base, "policy": {**base["policy"], key: forged}}
        assert (forged.shape, forged.dtype) == (((19,), array.dtype) if value == "cut19" else ((20,), np.float64))
        assert np.array_equal(forged, array[:forged.size])
    else:
        assert not online and base["policy"] is not None
    frozen, canons = _b2r_freeze(bundle), [pdb.canon(desc), pdb.canon(target)]
    sensitivity, fields = _kernel("gamma_sensitivity_policy"), ("label", "application", "status", "s2")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        _b2s_forbid(mp, "frozen_policy", "common_prior")
        mp.setattr(module, "cost_vectors", lambda gamma, K: calls.append((gamma, K)) or real(gamma, K))
        control = None if where == "variant" else sensitivity(desc, base)
        before = list(calls)
        with pytest.raises(ValueError):
            sensitivity(target, bundle)
    assert before == ([(5000.0, 20)] if online and control is not None else []) and calls == before
    assert control is None or [control[f] for f in fields] == [base[f] for f in fields]
    assert _b2r_freeze(base) == frozen_base and _b2r_freeze(bundle) == frozen
    assert [pdb.canon(desc), pdb.canon(target)] == canons


def test_gamma_sensitivity_policy_passes_remaining_static_bundles_through_without_the_gamma_field(monkeypatch):
    desc, factory, lo = _b2q_desc(), _kernel("frozen_policy"), {"RESIDUAL": 2, "MARKET": 1}
    params, fields = desc["science"]["parameters"], ("label", "application", "status", "s2")
    rows = {app: _kernel("spectral_baselines")(_b2b_spectrum(24), app)["baselines"] for app in lo}
    picks = [("RESIDUAL", "FIXED_EIGENMEAN_PREFIX", {"baselines": rows["RESIDUAL"]}),
             ("RESIDUAL", "RESIDUAL_CPV90", {"baselines": rows["RESIDUAL"]}),
             ("RESIDUAL", "FIXED_DEV_PREFIX", {"d_dev": 4}), ("MARKET", "FIXED_DEV_PREFIX", {}),
             ("MARKET", "FIXED_EXANTE_QBAR_MIX", {}), ("MARKET", "CPV90", {"baselines": rows["MARKET"]})]
    pcs = [rows["RESIDUAL"]["FIXED_EIGENMEAN_PREFIX"]["pcs"], rows["RESIDUAL"]["RESIDUAL_CPV90"]["pcs"],
           list(range(2, 6)), None, None, rows["MARKET"]["CPV90"]["pcs"]]
    bundles = [factory(desc, app, label, **kwargs) for app, label, kwargs in picks]
    assert [b["status"] for b in bundles] == ["RUNNABLE"] * 3 + ["NOT_RUN", "UNSUPPORTED", "RUNNABLE"]
    assert [len(p) for p in pcs if p] == [8, 15, 4, 15]
    for (app, _, _), bundle, chosen in zip(picks, bundles, pcs):
        assert set(bundle) == B2Q_FIELDS and bundle["s2"] == pytest.approx(B2Q_PRIOR, rel=1e-15)
        assert (bundle["policy"] is None) == (chosen is None)
        if chosen is not None:
            assert set(bundle["policy"]) == {"kind", "mask"} and bundle["policy"]["kind"] == "STATIC"
            assert bundle["policy"]["mask"].tolist() == [k + lo[app] in chosen for k in range(20)]
    trimmed = {k: v for k, v in params.items() if k != "gamma_M_sensitivity"}
    reduced = _edited(desc, ("science", "parameters"), trimmed)
    assert "gamma_M_sensitivity" in params and "gamma_M_sensitivity" not in reduced["science"]["parameters"]
    frozen, kept = [_b2r_freeze(b) for b in bundles], [pdb.canon(d) for d in (desc, reduced)]
    sensitivity = _kernel("gamma_sensitivity_policy")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        _b2s_forbid(mp, "frozen_policy", "common_prior", "cost_vectors", "affine_ols", "mixture_cost")
        outs = [sensitivity(reduced, b) for b in bundles]
    for out, bundle in zip(outs, bundles):
        assert set(out) == B2Q_FIELDS and [out[f] for f in fields] == [bundle[f] for f in fields]
        if bundle["policy"] is None:
            assert out["policy"] is None
        else:
            assert set(out["policy"]) == {"kind", "mask"} and out["policy"]["kind"] == "STATIC"
            mask = out["policy"]["mask"]
            assert mask.dtype == bool and np.array_equal(mask, bundle["policy"]["mask"])
    assert [_b2r_freeze(b) for b in bundles] == frozen and [pdb.canon(d) for d in (desc, reduced)] == kept


@pytest.mark.parametrize("order", ("INFO", "PREFIX"))
def test_gamma_sensitivity_online_bundle_changes_real_masks_and_scan_of_one_supplied_window(monkeypatch, order):
    desc, names, fields = _b2q_desc(), ("primary", "sensitivity"), ("label", "application", "status", "s2")
    params = desc["science"]["parameters"]
    costs = {name: [pdb.mixture_cost(d, g) for d in range(1, 21)] for name, g in zip(names, (504, 5000))}
    breaks = [costs[name][1] / costs[name][0] - 1.0 for name in names]
    r = 0.5 * (breaks[0] + breaks[1])
    assert [params[k] for k in ("H", "alpha", "K", "gamma_M", "gamma_M_sensitivity")] == [250, 0.05, 20, 504, 5000]
    assert all(map(math.isfinite, breaks)) and breaks[0] != breaks[1] and min(breaks) < r < max(breaks) and 0 < r < 1
    Y = np.zeros((1, 4, 20))
    Y[0, 0, :2] = [math.sqrt(3.0), math.sqrt(2.0 * r + 1.0)]
    assert np.allclose([0.5 * (y * y - 1.0) for y in Y[0, 0, :2]], [1.0, r], rtol=1e-12, atol=0.0)
    primary = _kernel("frozen_policy")(desc, "RESIDUAL", f"ONLINE_{order}_MIX_W128")
    s2, policy = primary["s2"], primary["policy"]
    assert set(primary) == B2Q_FIELDS and primary["status"] == "RUNNABLE" and s2 == _kernel("common_prior")(desc)
    assert set(policy) == {"kind", "window", "cost", "order"} and np.array_equal(policy["cost"], costs["primary"])
    assert [policy["kind"], policy["window"], policy["order"]] == ["ONLINE", 128, order]
    refs = {name: _b2r_online_ref(Y, 128, costs[name], order) for name in names}
    assert sorted(np.flatnonzero(refs[name][0, 1]).tolist() for name in names) == [[0], [0, 1]]
    assert int((refs["primary"] != refs["sensitivity"]).sum()) == 1
    assert all(np.array_equal(_kernel("online_masks")(Y, 128, np.array(costs[n]), order), refs[n]) for n in names)
    W = {name: _ref_W(Y, refs[name], s2) for name in names}
    assert not np.allclose(W["primary"], W["sensitivity"], rtol=1e-6, atol=1e-9)
    frozen_primary, sensitivity = _b2r_freeze(primary), _kernel("gamma_sensitivity_policy")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2q_traps(mp)
        _b2s_forbid(mp, "frozen_policy", "common_prior")
        moved = sensitivity(desc, primary)
    assert [moved[f] for f in fields] == [primary[f] for f in fields] and set(moved["policy"]) == set(policy)
    assert [moved["policy"][k] for k in ("kind", "window", "order")] == ["ONLINE", 128, order]
    assert np.array_equal(moved["policy"]["cost"], costs["sensitivity"])
    frozen_moved, kept, calls = _b2r_freeze(moved), Y.tobytes(), []
    Y.flags.writeable = False
    nonoracle = _kernel("nonoracle_scan")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2r_traps(mp)
        _b2s_forbid(mp, "cost_vectors", "affine_ols", "mixture_cost", "gamma_sensitivity_policy")
        _b2r_spies(mp, calls)
        outs = {name: nonoracle(Y, bundle, 0.0) for name, bundle in zip(names, (primary, moved))}
    assert [name for name, _ in calls] == ["nonoracle_masks", "masked_scan"] * 2
    assert [(a["s2"], a.get("h")) for name, a in calls if name == "masked_scan"] == [(s2, 0.0)] * 2
    for name, out in outs.items():
        assert set(out) == B2R_FIELDS and out["first"].tolist() == [_first(W[name][0], 0.0)]
        np.testing.assert_allclose(out["W"], W[name], rtol=1e-12, atol=1e-12)
        assert out["mask_bits"].dtype == np.uint32 and np.array_equal(out["mask_bits"], _b2r_bits(refs[name]))
    assert not np.array_equal(outs["primary"]["mask_bits"], outs["sensitivity"]["mask_bits"])
    assert not np.allclose(outs["primary"]["W"], outs["sensitivity"]["W"], rtol=1e-6, atol=1e-9)
    assert _b2r_freeze(primary) == frozen_primary and _b2r_freeze(moved) == frozen_moved and Y.tobytes() == kept


def _b2s_recipe(label, gamma, s2_rule, dev=None):
    static = {"FULL_K": "FULL_K", "FIXED_EIGENMEAN_PREFIX": "EIGENMEAN", "CPV90": "CPV90",
              "RESIDUAL_CPV90": "RESIDUAL_CPV90", "FIXED_DEV_PREFIX": "DEV_PREFIX", "FIXED_EXANTE_QBAR_MIX": "EXANTE"}
    recipe = {"kind": "STATIC", "order": None, "cost": None, "gamma_M": None, "window": None, "fallback": None,
              "ties": None, "s2_rule": s2_rule, "subset_rule": static.get(label, "ONLINE_QHAT")}
    if label == "FIXED_EXANTE_QBAR_MIX":
        recipe.update(order="INFO", cost="MIX", gamma_M=float(gamma), ties="SMALLEST_D_THEN_INDEX")
    elif label == "FIXED_DEV_PREFIX":
        recipe["subset_rule"] = {"kind": "DEV_PREFIX", "d_grid": sorted(dev["d_grid"]),
                                 "criterion": dev["criterion"], "ties": dev["ties"]}
    elif label not in static:
        recipe.update(kind="ONLINE", order=label.split("_")[1], cost="MIX", gamma_M=float(gamma), window=128,
                      fallback="MIN_E", ties="SMALLEST_D_THEN_INDEX")
    return recipe


def _b2s_reference(recipe):
    import hashlib
    import json
    text = json.dumps(recipe, sort_keys=True, separators=(",", ":"))
    return text, hashlib.sha256(text.encode()).hexdigest()[:16]


def _b2s_rule_traps(mp, opened):
    _no_side_effects(mp, opened)
    _b2q_traps(mp)
    _b2s_forbid(mp, "frozen_policy", "common_prior", "gamma_sensitivity_policy", "cost_vectors", "affine_ols",
                "mixture_cost", "design_descriptor", "design_id", "seed_plan", "_environment")


@pytest.mark.parametrize("order", ("INFO", "PREFIX"))
def test_policy_rule_hashes_the_effective_online_mix_w128_recipe_for_both_declared_budgets(monkeypatch, order):
    label, opened, expected = f"ONLINE_{order}_MIX_W128", [], {}
    twin = {"INFO": "PREFIX", "PREFIX": "INFO"}[order]
    configs = [_b2q_desc(), _b2q_desc((("parameters", "H"), 125), (("parameters", "alpha"), 0.1),
                                      (("parameters", "gamma_M_sensitivity"), 1250))]
    for index, desc in enumerate(configs):
        params, online = desc["science"]["parameters"], desc["science"]["policies"]["online"]
        assert [params["K"], params["gamma_M"], params["s2_rule"]] == [20, 504, "2*ln(H/alpha)/(H*K)"]
        assert params["gamma_M_sensitivity"] == params["H"] / params["alpha"] == (5000.0, 1250.0)[index]
        assert order in online["orders"] and "MIX" in online["costs"] and 128 in online["windows"]
        for flag in (False, True):
            gamma = params["H"] / params["alpha"] if flag else params["gamma_M"]
            recipe = _b2s_recipe(label, gamma, params["s2_rule"])
            expected[(index, flag)] = (recipe, *_b2s_reference(recipe))
    ids, s2_rule = {key: value[2] for key, value in expected.items()}, configs[0]["science"]["parameters"]["s2_rule"]
    assert ids[(0, False)] == ids[(1, False)] and len({ids[(0, False)], ids[(0, True)], ids[(1, True)]}) == 3
    assert [expected[(index, True)][0]["gamma_M"] for index in (0, 1)] == [5000.0, 1250.0]
    assert _b2s_reference(_b2s_recipe(f"ONLINE_{twin}_MIX_W128", 504, s2_rule))[1] != ids[(0, False)]
    rule, kept = _kernel("policy_rule"), [pdb.canon(desc) for desc in configs]
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        outs = {(index, flag): rule(desc, label, gamma_sensitivity=flag)
                for index, desc in enumerate(configs) for flag in (False, True)}
        default = [rule(desc, label) for desc in configs]
    for key, out in outs.items():
        recipe, text, sha = expected[key]
        assert set(out) == {"recipe", "policy_rule_id"} and out["recipe"] == recipe and out["policy_rule_id"] == sha
        assert _b2s_reference(out["recipe"]) == (text, sha) and type(out["recipe"]["gamma_M"]) is float
    assert default == [outs[(0, False)], outs[(1, False)]] and opened == []
    assert [pdb.canon(desc) for desc in configs] == kept


def test_policy_rule_keeps_each_declared_static_recipe_without_sensitivity_inputs_or_realized_values(monkeypatch):
    desc, opened = _b2q_desc(), []
    params, statics = desc["science"]["parameters"], desc["science"]["policies"]["static"]
    trimmed = {key: value for key, value in params.items() if key != "gamma_M_sensitivity"}
    reduced = _edited(desc, ("science", "parameters"), trimmed)
    dev, moved = desc["science"]["dev"], _edited(desc, ("science", "dev", "d_grid"), [1, 2, 4])
    grids = [dev["d_grid"], moved["science"]["dev"]["d_grid"]]
    assert statics == ["FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90", "FIXED_DEV_PREFIX",
                       "FIXED_EXANTE_QBAR_MIX"]
    assert "gamma_M_sensitivity" not in reduced["science"]["parameters"] and params["gamma_M"] == 504
    assert grids == [[1, 2, 4, 8, 16, 20], [1, 2, 4]] and all(type(d) is int for grid in grids for d in grid)
    assert [moved["science"]["dev"][k] for k in ("criterion", "ties")] == [dev["criterion"], dev["ties"]]
    assert [dev["criterion"], dev["ties"]] == ["MEAN_RMST_H_EQUAL_FAMILY_WEIGHTS", "SMALLEST"]
    assert pdb.canon(_edited(moved, ("science", "dev", "d_grid"), dev["d_grid"])) == pdb.canon(desc)
    expected = {label: _b2s_recipe(label, params["gamma_M"], params["s2_rule"], dev) for label in statics}
    refs = {label: _b2s_reference(recipe) for label, recipe in expected.items()}
    shifted = _b2s_recipe("FIXED_DEV_PREFIX", params["gamma_M"], params["s2_rule"], moved["science"]["dev"])
    shifted_ref = _b2s_reference(shifted)
    objects = [expected["FIXED_DEV_PREFIX"]["subset_rule"], shifted["subset_rule"]]
    assert len({sha for _, sha in refs.values()}) == len(statics) == 6
    assert [label for label, recipe in expected.items() if recipe["cost"] is not None] == ["FIXED_EXANTE_QBAR_MIX"]
    assert [expected["FIXED_EXANTE_QBAR_MIX"][k] for k in ("order", "cost", "gamma_M")] == ["INFO", "MIX", 504.0]
    assert objects == [{"kind": "DEV_PREFIX", "d_grid": grid, "criterion": dev["criterion"], "ties": dev["ties"]}
                       for grid in grids]
    assert shifted_ref[1] != refs["FIXED_DEV_PREFIX"][1] and shifted_ref[0] != refs["FIXED_DEV_PREFIX"][0]
    assert {**shifted, "subset_rule": None} == {**expected["FIXED_DEV_PREFIX"], "subset_rule": None}
    rule, kept = _kernel("policy_rule"), [pdb.canon(d) for d in (desc, reduced, moved)]
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        outs = {(label, name, flag): rule(source, label, gamma_sensitivity=flag) for label in statics
                for name, source in (("desc", desc), ("reduced", reduced)) for flag in (False, True)}
        changed = [rule(moved, "FIXED_DEV_PREFIX", gamma_sensitivity=flag) for flag in (False, True)]
    for (label, _, _), out in outs.items():
        assert set(out) == {"recipe", "policy_rule_id"} and out["recipe"] == expected[label]
        assert _b2s_reference(out["recipe"]) == refs[label] and out["policy_rule_id"] == refs[label][1]
    for out in changed:
        assert set(out) == {"recipe", "policy_rule_id"} and out["recipe"] == shifted
        assert _b2s_reference(out["recipe"]) == shifted_ref and out["policy_rule_id"] == shifted_ref[1]
    assert len(outs) == 24 and opened == [] and [pdb.canon(d) for d in (desc, reduced, moved)] == kept


def _b2s_primary(desc):
    science = desc["science"]
    params, policies, s2_rule = science["parameters"], science["policies"], science["parameters"]["s2_rule"]
    online, oracle = policies["online"], policies["oracle"]
    rules = {label: _b2s_recipe(label, params["gamma_M"], s2_rule, science["dev"]) for label in policies["static"]}
    entries = [("ONLINE", o, c, w) for o in online["orders"] for c in online["costs"] for w in online["windows"]]
    entries += [("ORACLE", o, c, None) for o in oracle["orders"] for c in oracle["costs"]]
    for kind, order, cost, window in entries:
        label = f"ONLINE_{order}_{cost}_W{window}" if kind == "ONLINE" else f"ORACLE_{order}_{cost}"
        rules[label] = {"kind": kind, "order": order, "cost": {"MIX": "MIX", "AFF": "AFF_OLS_1_16"}[cost],
                        "gamma_M": float(params["gamma_M"]), "window": window, "ties": "SMALLEST_D_THEN_INDEX",
                        "fallback": "MIN_E" if kind == "ONLINE" else None, "s2_rule": s2_rule,
                        "subset_rule": "ONLINE_QHAT" if kind == "ONLINE" else "ORACLE_Q"}
    return {label: (recipe, *_b2s_reference(recipe)) for label, recipe in rules.items()}


def test_policy_rule_hashes_all_eighteen_declared_primary_recipes_with_independent_references(monkeypatch):
    desc, opened = _b2q_desc(), []
    policies = desc["science"]["policies"]
    online, oracle, statics = policies["online"], policies["oracle"], policies["static"]
    assert [online["orders"], online["costs"], online["windows"]] == [["INFO", "PREFIX"], ["MIX", "AFF"], [32, 128]]
    assert [oracle["orders"], oracle["costs"]] == [["INFO", "PREFIX"], ["MIX", "AFF"]]
    assert statics == ["FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90", "FIXED_DEV_PREFIX",
                       "FIXED_EXANTE_QBAR_MIX"]
    labels = [f"ONLINE_{o}_{c}_W{w}" for o in ("INFO", "PREFIX") for c in ("MIX", "AFF") for w in (32, 128)]
    labels += [f"ORACLE_{o}_{c}" for o in ("INFO", "PREFIX") for c in ("MIX", "AFF")] + statics
    expected = _b2s_primary(desc)
    assert sorted(expected) == sorted(labels) and len(labels) == 18 and set(desc["scope"]["policies"]) < set(labels)
    assert len({sha for _, _, sha in expected.values()}) == 18
    picks = [expected[label][0] for label in ("ONLINE_PREFIX_AFF_W32", "ORACLE_INFO_AFF", "FULL_K")]
    assert [(r["kind"], r["cost"], r["gamma_M"], r["window"], r["fallback"]) for r in picks] == [
        ("ONLINE", "AFF_OLS_1_16", 504.0, 32, "MIN_E"), ("ORACLE", "AFF_OLS_1_16", 504.0, None, None),
        ("STATIC", None, None, None, None)]
    rule, kept = _kernel("policy_rule"), pdb.canon(desc)
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        outs = {label: rule(desc, label) for label in labels}
    for label, out in outs.items():
        recipe, text, sha = expected[label]
        assert set(out) == {"recipe", "policy_rule_id"} and out["recipe"] == recipe and out["policy_rule_id"] == sha
        assert _b2s_reference(out["recipe"]) == (text, sha)
    assert len(outs) == 18 and opened == [] and pdb.canon(desc) == kept


def test_policy_rule_primary_ids_ignore_declaration_order_scope_horizon_metadata_and_external_decoys(monkeypatch):
    desc, opened = _b2q_desc(), []
    science, base = desc["science"], _b2s_primary(desc)
    online, oracle = science["policies"]["online"], science["policies"]["oracle"]
    flips = {("policies", "online", "orders"): online["orders"], ("policies", "online", "costs"): online["costs"],
             ("policies", "online", "windows"): online["windows"], ("policies", "oracle", "orders"): oracle["orders"],
             ("policies", "oracle", "costs"): oracle["costs"], ("policies", "static"): science["policies"]["static"],
             ("dev", "d_grid"): science["dev"]["d_grid"]}
    flipped = desc
    for path, values in flips.items():
        flipped = _edited(flipped, ("science", *path), values[::-1])
    scoped = _edited(_edited(desc, ("scope", "families"), ["F_HEAD_RESIDUAL"]), ("scope", "policies"), ["FULL_K"])
    horizon = metadata = desc
    for key, value in (("H", 125), ("alpha", 0.1), ("gamma_M_sensitivity", 1250), ("I_star", 0.5)):
        horizon = _edited(horizon, ("science", "parameters", key), value)
    for path, value in ((("seed",), 77), (("seed_plan_sha256",), "0" * 64), (("code",), {"x.py": "0" * 64}),
                        (("environment",), {"python": "3.12"}), (("sizes", "CAL_NULL"), 9),
                        (("envelope", "jobs_max"), 1)):
        metadata = _edited(metadata, path, value)
    metadata = {**metadata, "authorization": {"go": "GO-stream-32.md"}, "telemetry": {"cpu_seconds": 1.5}}
    decoys = {**desc, "realized": {"qbar": [0.25] * 20, "d_dev": 4, "s2_dev": 0.0136, "prior": 0.0034, "h": 7.5,
                                   "policy_id": "0" * 16, "dev_id": "1" * 16, "calibration_id": "2" * 16}}
    clones, moved = [flipped, scoped, horizon, metadata, decoys], horizon["science"]["parameters"]
    assert flipped["science"]["dev"]["d_grid"] == [20, 16, 8, 4, 2, 1] and len(base) == 18
    assert [moved["H"], moved["alpha"], moved["gamma_M_sensitivity"], moved["I_star"]] == [125, 0.1, 1250, 0.5]
    assert [moved[k] for k in ("gamma_M", "s2_rule")] == [science["parameters"][k] for k in ("gamma_M", "s2_rule")]
    assert all(pdb.canon(clone) != pdb.canon(desc) for clone in clones)
    assert all(_b2s_primary(clone) == base for clone in clones)
    rule, kept = _kernel("policy_rule"), [pdb.canon(d) for d in (desc, *clones)]
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        outs = {(index, label): rule(clone, label) for index, clone in enumerate(clones) for label in base}
    for (_, label), out in outs.items():
        recipe, text, sha = base[label]
        assert set(out) == {"recipe", "policy_rule_id"} and out["recipe"] == recipe and out["policy_rule_id"] == sha
        assert _b2s_reference(out["recipe"]) == (text, sha)
    assert len(outs) == 90 and opened == [] and [pdb.canon(d) for d in (desc, *clones)] == kept


B2S_RULE_REFUSALS = {
    "undeclared_label": ("FIXED_KAISER_PREFIX", False, None, None, "keep"),
    "static_without_rule": ("FIXED_KAISER_PREFIX", False, ("policies", "static"), "FIXED_KAISER_PREFIX", "append"),
    "flag_int": ("ONLINE_INFO_MIX_W128", 1, None, None, "keep"),
    "aff_w128_sensitivity": ("ONLINE_INFO_AFF_W128", True, None, None, "keep"),
    "mix_w32_sensitivity": ("ONLINE_PREFIX_MIX_W32", True, None, None, "keep"),
    "oracle_sensitivity": ("ORACLE_INFO_MIX", True, None, None, "keep"),
    "gamma_bool": ("ONLINE_INFO_MIX_W128", False, ("parameters", "gamma_M"), True, "set"),
    "gamma_text": ("ONLINE_PREFIX_MIX_W128", False, ("parameters", "gamma_M"), "504", "set"),
    "gamma_nan": ("ONLINE_INFO_MIX_W128", False, ("parameters", "gamma_M"), math.nan, "set"),
    "gamma_one": ("ONLINE_PREFIX_MIX_W128", False, ("parameters", "gamma_M"), 1, "set"),
    "sensitivity_stale": ("ONLINE_INFO_MIX_W128", True, ("parameters", "gamma_M_sensitivity"), 1250, "set"),
    "sensitivity_bool": ("ONLINE_PREFIX_MIX_W128", True, ("parameters", "gamma_M_sensitivity"), True, "set"),
    "sensitivity_text": ("ONLINE_INFO_MIX_W128", True, ("parameters", "gamma_M_sensitivity"), "5000", "set"),
    "sensitivity_nan": ("ONLINE_PREFIX_MIX_W128", True, ("parameters", "gamma_M_sensitivity"), math.nan, "set"),
    "sensitivity_missing": ("ONLINE_INFO_MIX_W128", True, ("parameters", "gamma_M_sensitivity"), None, "drop"),
    "h_float": ("ONLINE_PREFIX_MIX_W128", True, ("parameters", "H"), 250.0, "set"),
    "alpha_text": ("ONLINE_INFO_MIX_W128", True, ("parameters", "alpha"), "0.05", "set"),
    "s2_rule_none": ("FULL_K", False, ("parameters", "s2_rule"), None, "set"),
    "dev_grid_empty": ("FIXED_DEV_PREFIX", False, ("dev", "d_grid"), [], "set"),
    "dev_grid_duplicate": ("FIXED_DEV_PREFIX", False, ("dev", "d_grid"), [1, 1], "set"),
    "dev_grid_bool": ("FIXED_DEV_PREFIX", False, ("dev", "d_grid"), [True, 2], "set"),
    "dev_grid_float": ("FIXED_DEV_PREFIX", False, ("dev", "d_grid"), [1.0, 2], "set"),
    "dev_criterion_int": ("FIXED_DEV_PREFIX", False, ("dev", "criterion"), 1, "set"),
    "dev_ties_bool": ("FIXED_DEV_PREFIX", False, ("dev", "ties"), True, "set"),
    "online_order_outside": ("ONLINE_RANDOM_MIX_W128", False, ("policies", "online", "orders"), "RANDOM", "append"),
    "online_cost_outside": ("ONLINE_INFO_LIN_W128", False, ("policies", "online", "costs"), "LIN", "append"),
}


def _b2s_at(desc, path):
    for key in ("science", *path):
        desc = desc[key]
    return desc


@pytest.mark.parametrize("case", B2S_RULE_REFUSALS)
def test_policy_rule_refuses_one_malformed_declaration_flag_or_unplanned_variant_before_hashing(monkeypatch, case):
    (label, flag, path, value, mode), desc = B2S_RULE_REFUSALS[case], _b2q_desc()
    base, opened, hashes, real, target = _b2s_primary(desc), [], [], pdb.sha16, desc
    control = label if label in base else ("FULL_K" if label.startswith("FIXED") else "ONLINE_INFO_MIX_W128")
    current = None if mode == "keep" else _b2s_at(desc, path)
    if mode == "set":
        target = _edited(desc, ("science", *path), value)
    elif mode == "append":
        target = _edited(desc, ("science", *path), [*current, value])
    elif mode == "drop":
        trimmed = {key: item for key, item in _b2s_at(desc, path[:-1]).items() if key != path[-1]}
        target = _edited(desc, ("science", *path[:-1]), trimmed)
    online = target["science"]["policies"]["online"]
    declared = {f"ONLINE_{o}_{c}_W{w}" for o in online["orders"] for c in online["costs"] for w in online["windows"]}
    assert control in base and (mode == "keep" or pdb.canon(target) != pdb.canon(desc))
    if mode == "set":
        assert _b2s_at(target, path) is value and current is not value
    elif mode == "append":
        assert _b2s_at(target, path) == [*current, value] and value not in current and label not in base
        assert value not in ("INFO", "PREFIX", "MIX", "AFF") and (label in declared or label in _b2s_at(target, path))
    elif mode == "drop":
        assert path[-1] in _b2s_at(desc, path[:-1]) and path[-1] not in _b2s_at(target, path[:-1])
    else:
        assert (label not in base) if case == "undeclared_label" else (label in base and flag is not False)
    kept, rule = [pdb.canon(desc), pdb.canon(target)], _kernel("policy_rule")
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        mp.setattr(pdb, "sha16", lambda obj: hashes.append(obj) or real(obj))
        out = rule(desc, control)
        before = len(hashes)
        with pytest.raises(ValueError):
            rule(target, label, gamma_sensitivity=flag)
    recipe, text, sha = base[control]
    assert out == {"recipe": recipe, "policy_rule_id": sha} and _b2s_reference(out["recipe"]) == (text, sha)
    assert before == 1 and len(hashes) == before and opened == [] and [pdb.canon(desc), pdb.canon(target)] == kept


@pytest.mark.parametrize("setup", B2P_SETUPS)
def test_dev_library_block_stacks_the_received_q_of_each_planned_devlib_key_in_order(monkeypatch, setup):
    import inspect
    cfg, desc = _b2p_design((("dev", "n_lib"), 2), (("modes", "full", "sizes", "DEV_LIB"), 2))
    frame, module, drawn, seen = _b2o_frame(), pio(), [], []
    fit = frame if setup[0] == "EXACT" else _b2h_fit(B2H_PERMS["aligned"])
    planned, istar = set(_kernel("seed_plan")(cfg, "full")["keys"]), desc["science"]["parameters"]["I_star"]
    supports = {"F0_ISOTROPIC_RESIDUAL": None, "F1_TAIL_RESIDUAL": (18, 19, 20, 21),
                "F2_STRUCTURED_RESIDUAL": (3, 9, 17, 21), "F_HEAD_RESIDUAL": (2, 3, 4, 5)}
    keys = [("devlib", "FULL", *setup, family, index) for family in DEV_FAMILIES for index in range(2)]
    rows, golds, dev = {key: _b2d_draws(key[5])[key[6]:key[6] + 1] for key in keys}, {}, desc["science"]["dev"]
    for key, row in rows.items():
        b = np.array(_b2d_coordinates(supports[key[5]], list(range(2, 22)), row[0].tolist(), istar, 24))
        delta = frame["V"] @ (np.sqrt(frame["lam"]) * b)
        golds.setdefault(key[5], []).append(0.5 * (delta @ fit["V"][:, 1:21]) ** 2 / fit["lam"][1:21])
    assert [dev["n_lib"], desc["sizes"]["DEV_LIB"], sorted(dev["families"])] == [2, 2, sorted(DEV_FAMILIES)]
    assert "RESIDUAL" in desc["scope"]["applications"] and set(desc["scope"]["families"]) < set(DEV_FAMILIES)
    assert all(key in planned for key in keys) and all((*key[:6], 2) not in planned for key in keys)
    assert all(g.shape == (20,) and np.isfinite(g).all() and (g >= 0).all() for q in golds.values() for g in q)
    assert not np.allclose(*golds["F0_ISOTROPIC_RESIDUAL"]) and list(setup) in desc["scope"]["setups"]
    arrays, kept = _b2p_frozen(frame, fit, *rows.values())
    snapshot, block, real = pdb.canon(desc), _kernel("dev_library_block"), module.direction_information
    signature = inspect.signature(real)

    def spy(*args, **kwargs):
        seen.append(signature.bind(*args, **kwargs).arguments)
        return real(*args, **kwargs)

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b2p_traps(mp)
        _b2s_forbid(mp, "cost_vectors", "affine_ols", "mixture_cost", "common_prior", "frozen_policy", "policy_rule",
                    "dev_qbar", "partition", "phase_record", "guarded_partition", "setup_phase", "design_id")
        _b2p_draw_stub(mp, desc, rows, drawn)
        mp.setattr(module, "direction_information", spy)
        outs = {family: block(desc, frame, fit, list(setup), family) for family in DEV_FAMILIES}
    assert drawn == keys and [a["key"] for a in seen] == keys and [a.tobytes() for a in arrays] == kept
    assert all(a["desc"] is desc and a["frame"] is frame and a["fit"] is fit for a in seen)
    assert all(list(a["setup"]) == list(setup) and a["application"] == "RESIDUAL" for a in seen)
    for family, out in outs.items():
        assert set(out) == {"q"} and out["q"].dtype == np.float64 and out["q"].shape == (2, 20)
        np.testing.assert_allclose(out["q"], np.array(golds[family]), rtol=1e-12, atol=1e-15)
    assert pdb.canon(desc) == snapshot


B2T_ADMISSION = {"family_market": ("family", "F3_MARKET"), "family_nontext": ("family", 1),
                 "declared_missing": (("dev", "families"), list(DEV_FAMILIES[:3])),
                 "declared_extra": (("dev", "families"), [*DEV_FAMILIES, "F3_MARKET"]),
                 "declared_duplicate": (("dev", "families"), [*DEV_FAMILIES, DEV_FAMILIES[0]]),
                 "declared_nontext": (("dev", "families"), [*DEV_FAMILIES[:3], 1]),
                 "n_lib_zero": (("dev", "n_lib"), 0), "n_lib_bool": (("dev", "n_lib"), True),
                 "n_lib_float": (("dev", "n_lib"), 2.0), "n_lib_text": (("dev", "n_lib"), "2"),
                 "cap_mismatch": ("cap", 1), "cap_bool": ("cap", True), "cap_float": ("cap", 2.0),
                 "cap_text": ("cap", "2"), "cap_overflow": ("cap", 2 ** 32),
                 "residual_unscoped": ("scope", ["MARKET"]), "setup_unplanned": ("setup", ["EXACT", 24, 1]),
                 "setup_tuple": ("setup", ("EXACT", 24, 0)), "campaign_nontext": ("campaign", None)}
B2T_OUTPUTS = {"unsupported": None, "q_nan": ((20,), "f", True, False, False),
               "q_negative": ((20,), "f", False, True, False), "q_short": ((19,), "f", False, False, False),
               "q_matrix": ((1, 20), "f", False, False, False), "q_complex": ((20,), "c", False, False, True),
               "producer_raises": None}


def _b2t_base(n_lib):
    cfg, desc = _b2p_design((("dev", "n_lib"), n_lib), (("modes", "full", "sizes", "DEV_LIB"), n_lib))
    family, setup, frame = "F2_STRUCTURED_RESIDUAL", ["EXACT", 24, 0], _b2o_frame()
    keys = [("devlib", "FULL", *setup, family, index) for index in range(n_lib)]
    qs = [np.linspace(0.0, 0.19, 20) * (index + 1) for index in range(n_lib)]
    for q in qs:
        q.flags.writeable = False
    planned = set(_kernel("seed_plan")(cfg, "full")["keys"])
    assert set(keys) <= planned and ("devlib", "FULL", *setup, family, n_lib) not in planned
    assert [desc["science"]["dev"]["n_lib"], desc["sizes"]["DEV_LIB"]] == [n_lib, n_lib]
    assert setup in desc["scope"]["setups"] and "RESIDUAL" in desc["scope"]["applications"]
    return desc, frame, setup, family, keys, qs


def _b2t_row(family, q):
    fields = ("support", "delta", "q", "I_joint", "oracle_basis")
    if q is None:
        return {"status": "UNSUPPORTED", "family": family, **dict.fromkeys(fields)}
    return {"status": "SUPPORTED", "family": family, "support": [3, 9, 17, 21], "delta": np.ones(24), "q": q,
            "I_joint": 0.25, "oracle_basis": "EXACT_ADDITIVE_KL"}


def _b2t_traps(mp, trace, script):
    _no_side_effects(mp)
    _b2p_traps(mp)
    _b2s_forbid(mp, "population_drift", "projection_diagnostics", "direction_draws", "cost_vectors", "common_prior",
                "frozen_policy", "policy_rule", "dev_qbar", "partition", "phase_record")

    def produce(desc, frame, fit, setup, application, key):
        trace.append((desc, frame, fit, setup, application, key))
        result = script.get(key[6], AssertionError("unexpected DEV_LIB producer call"))
        if isinstance(result, BaseException):
            raise result
        return result

    mp.setattr(pio(), "direction_information", produce)


def _b2t_control(block, desc, frame, setup, family, keys, qs, trace, script):
    script.update({index: _b2t_row(family, q) for index, q in enumerate(qs)})
    out = block(desc, frame, frame, setup, family)
    assert set(out) == {"q"} and out["q"].dtype == np.float64 and np.array_equal(out["q"], np.array(qs))
    assert [call[5] for call in trace] == keys and all(call[4] == "RESIDUAL" for call in trace)
    assert all(call[0] is desc and call[1] is frame and call[2] is frame and call[3] is setup for call in trace)
    trace.clear()
    script.clear()


@pytest.mark.parametrize("case", B2T_ADMISSION)
def test_dev_library_block_refuses_bad_admission_metadata_before_any_producer_call(monkeypatch, case):
    (where, value), (desc, frame, setup, family, keys, qs) = B2T_ADMISSION[case], _b2t_base(2)
    bad_setup, bad_family = (value if where == "setup" else setup), (value if where == "family" else family)
    paths = {"cap": ("sizes", "DEV_LIB"), "scope": ("scope", "applications"), "campaign": ("campaign",)}
    path = None if where in ("setup", "family") else paths.get(where, ("science", *where))
    target = desc if path is None else _edited(desc, path, value)
    if path is not None:
        holder = target
        for key in path:
            holder = holder[key]
        assert holder is value and pdb.canon(target) != pdb.canon(desc)
    elif where == "setup":
        tuple_case = type(value) is tuple and pdb.canon(value) == pdb.canon(setup)
        assert tuple_case if case == "setup_tuple" else (type(value) is list and value not in desc["scope"]["setups"])
    else:
        assert value not in DEV_FAMILIES
    assert [target is not desc, bad_setup is not setup, bad_family is not family].count(True) == 1
    if where == "scope":
        assert "RESIDUAL" not in value and set(value) <= set(desc["science"]["applications"])
    frozen, kept = _b2p_frozen(frame, *qs)
    snapshots, block, trace, script = [pdb.canon(desc), pdb.canon(target)], _kernel("dev_library_block"), [], {}
    with monkeypatch.context() as mp:
        _b2t_traps(mp, trace, script)
        _b2t_control(block, desc, frame, setup, family, keys, qs, trace, script)
        with pytest.raises(ValueError):
            block(target, frame, frame, bad_setup, bad_family)
    assert trace == [] and [a.tobytes() for a in frozen] == kept
    assert [pdb.canon(desc), pdb.canon(target)] == snapshots


@pytest.mark.parametrize("case", B2T_OUTPUTS)
def test_dev_library_block_stops_at_a_bad_second_producer_output_without_retry_or_partial_payload(monkeypatch, case):
    desc, frame, setup, family, keys, qs = _b2t_base(3)
    sentinel, bad_q = ArithmeticError("controlled DEV_LIB producer failure"), qs[1].copy()
    if case in ("q_nan", "q_negative"):
        bad_q[5] = math.nan if case == "q_nan" else -0.25
    bad_q = {"q_short": bad_q[:19], "q_matrix": bad_q[None, :], "q_complex": bad_q + 1j}.get(case, bad_q)
    bad = sentinel if case == "producer_raises" else _b2t_row(family, None if case == "unsupported" else bad_q)
    if B2T_OUTPUTS[case] is None:
        assert bad is sentinel if case == "producer_raises" else (bad["status"], bad["q"]) == ("UNSUPPORTED", None)
    else:
        q = bad["q"]
        facts = (q.shape, q.dtype.kind, bool(np.isnan(q).any()), bool((q.real < 0).any()), bool((q.imag != 0).any()))
        assert bad["status"] == "SUPPORTED" and facts == B2T_OUTPUTS[case]
    frozen, kept = _b2p_frozen(frame, *qs)
    snapshot, block, trace, script = pdb.canon(desc), _kernel("dev_library_block"), [], {}
    with monkeypatch.context() as mp:
        _b2t_traps(mp, trace, script)
        _b2t_control(block, desc, frame, setup, family, keys, qs, trace, script)
        script.update({0: _b2t_row(family, qs[0]), 1: bad, 2: _b2t_row(family, qs[2])})
        with pytest.raises(ArithmeticError if bad is sentinel else ValueError) as caught:
            block(desc, frame, frame, setup, family)
    assert [call[5] for call in trace] == keys[:2] and (bad is not sentinel or caught.value is sentinel)
    assert [a.tobytes() for a in frozen] == kept and pdb.canon(desc) == snapshot


def test_dev_library_block_keeps_legitimate_all_zero_q_rows_without_fallback(monkeypatch):
    desc, frame, setup, family, keys, _ = _b2t_base(2)
    zeros = [np.zeros(20), np.zeros(20)]
    frozen, kept = _b2p_frozen(frame, *zeros)
    assert all(z.shape == (20,) and not z.any() and not z.flags.writeable for z in zeros) and len(keys) == 2
    snapshot, block, trace, script = pdb.canon(desc), _kernel("dev_library_block"), [], {}
    with monkeypatch.context() as mp:
        _b2t_traps(mp, trace, script)
        _b2t_control(block, desc, frame, setup, family, keys, zeros, trace, script)
    assert [a.tobytes() for a in frozen] == kept and pdb.canon(desc) == snapshot


def _b2u_fixture(root, monkeypatch, drop=None):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2O_SETUPS]),
                        (("scope", "applications"), ["RESIDUAL", "MARKET"]), (("parameters", "T_fit"), 48),
                        (("dev", "n_lib"), 2), (("modes", "full", "sizes", "DEV_LIB"), 2)):
        cfg = _edited(cfg, path, value)
    cfg = _authorized(root, monkeypatch, cfg, "full")[0]
    desc, primitive = _kernel("design_descriptor")(cfg, "full"), _kernel("seed_plan")(cfg, "full")["keys"]
    plan = {phase: [] for phase in _kernel("PHASES")}
    plan["SETUP"] = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    logical = (["DEV_LIB", "FULL", *setup, family] for setup in desc["scope"]["setups"] for family in DEV_FAMILIES)
    plan["DEV"] = sorted((key for key in logical if key != drop), key=pdb.canon)
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")("full", cfg, desc, 1), plan, staging


def _b2u_first(tmp_path, monkeypatch, drop=None):
    fixture, state, log = _b2u_fixture(tmp_path, monkeypatch, drop), {"cpu": 10.0, "wall": 100.0}, []
    record = _b2o_run(monkeypatch, state, log, fixture, "invocation-1")
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(fixture[4], fixture[2], fixture[3], "invocation-2")
    assert len(log) == 8 and record["phase"] == "SETUP" and state["cpu"] == 16.0
    return fixture, state, record, context


def _b2u_q(setup, family):
    scale = 1.0 + DEV_FAMILIES.index(family) + 10.0 * [s[0] for s in B2O_SETUPS].index(setup[0])
    q = np.outer([1.0, 0.5], np.linspace(0.0, 0.019, 20)) * scale
    q.flags.writeable = False
    return q


def _b2u_qbar(setup):
    pools = [_b2u_q(setup, family) for family in DEV_FAMILIES]
    return [math.fsum(math.fsum(q[:, k]) / len(q) for q in pools) / len(pools) for k in range(20)]


def _b2u_qualify(fixture, record):
    cfg, desc, _, plan, staging = fixture
    setups, primitive = desc["scope"]["setups"], set(_kernel("seed_plan")(cfg, "full")["keys"])
    logical = sorted((["DEV_LIB", "FULL", *s, f] for s in setups for f in DEV_FAMILIES), key=pdb.canon)
    _kernel("_validated_plan")(plan)
    assert [desc["science"]["dev"]["n_lib"], desc["sizes"]["DEV_LIB"], len(setups)] == [2, 2, 3]
    assert set(desc["scope"]["families"]) < set(DEV_FAMILIES) and "RESIDUAL" in desc["scope"]["applications"]
    assert all(("devlib", "FULL", *s, f, index) in primitive for s in setups for f in DEV_FAMILIES for index in (0, 1))
    assert not any(tuple(key) in primitive for key in logical) and not (staging / "phases" / "DEV.json").exists()
    assert _kernel("phase_record")(staging, "SETUP", {}, None, None) == record
    assert sorted(record["derived"]["setups"]) == sorted(pdb.canon(s) for s in setups)
    assert len({_b2u_q(s, f).tobytes() for s in setups for f in DEV_FAMILIES}) == 12
    return logical


def _b2u_expected(staging, record, plan, setup):
    import hashlib
    import json
    did, upstream, rows = record["design_id"], {"SETUP": record["phase_digest"]}, []
    for key in (key for key in plan["DEV"] if key[2:5] == setup):
        data = _partition_stem(staging, did, upstream, key).with_suffix(".npz").read_bytes()
        rows.append({"key": key, "sha256": hashlib.sha256(data).hexdigest(), "n_rows": 2})
    setup_id = record["derived"]["setups"][pdb.canon(setup)]["applications"]["RESIDUAL"]["setup_id"]
    identity = {"setup_id": setup_id, "partitions": [[pdb.canon(row["key"]), row["sha256"]] for row in rows]}
    text = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return setup_id, rows, hashlib.sha256(text.encode()).hexdigest()[:16]


def _b2u_traps(mp, state, calls, reductions, want_desc, producer):
    module = pio()
    real_qbar = module.dev_qbar
    _b1m_clock(mp, state)
    _no_draws_or_workers(mp)
    _b2o_forbid(mp)
    _b2s_forbid(mp, "direction_information", "direction_draws", "population_drift", "projection_diagnostics")

    def dev_library_block(desc, frame, fit, setup, family):
        assert producer, "DEV_LIB producer call on a committed or refused library"
        want = _b2o_frame() if setup[0] == "EXACT" else _b2o_fit(setup[0])
        assert pdb.canon(desc) == pdb.canon(want_desc) and type(setup) is list and family in DEV_FAMILIES
        assert _same_arrays(frame, _b2o_frame()) and _same_arrays(fit, want)
        calls.append((pdb.canon(setup), family))
        state["cpu"] += 0.25
        return {"q": _b2u_q(setup, family)}

    def dev_qbar(desc, q_by_family):
        result = real_qbar(desc, q_by_family)
        reductions.append(({family: np.array(q) for family, q in q_by_family.items()}, result.copy()))
        return result

    mp.setattr(module, "dev_library_block", dev_library_block)
    mp.setattr(module, "dev_qbar", dev_qbar)


def test_dev_library_cache_commits_four_family_batches_per_setup_with_actual_hashes_and_qbar(tmp_path, monkeypatch):
    import io
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, _, plan, staging = fixture
    did, upstream, setups = record["design_id"], {"SETUP": record["phase_digest"]}, desc["scope"]["setups"]
    assert plan["DEV"] == _b2u_qualify(fixture, record) and len(plan["DEV"]) == 12
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, True)
        result = cache(cfg, "full", context)
    assert sorted(calls) == sorted((pdb.canon(s), f) for s in setups for f in DEV_FAMILIES) and len(calls) == 12
    assert json.loads(pdb.canon(result)) == result and set(result) == {pdb.canon(s) for s in setups}
    assert len(reductions) == 3 and all(sorted(pooled) == sorted(DEV_FAMILIES) for pooled, _ in reductions)
    for setup in setups:
        setup_id, rows, library_id = _b2u_expected(staging, record, plan, setup)
        pooled = [pair for pair in reductions
                  if all(np.array_equal(pair[0][f], _b2u_q(setup, f)) for f in DEV_FAMILIES)]
        out = result[pdb.canon(setup)]
        assert len(pooled) == 1 and set(out) == {"setup_id", "partitions", "qbar", "qbar_sha", "dev_library_id"}
        assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, rows, library_id]
        assert out["qbar"] == pooled[0][1].tolist() and out["qbar"] == pytest.approx(_b2u_qbar(setup), rel=1e-12)
        assert out["qbar_sha"] == pdb.array_sha256(np.array(out["qbar"], dtype=np.float64))
        for row in rows:
            stem = _partition_stem(staging, did, upstream, row["key"])
            with np.load(io.BytesIO(stem.with_suffix(".npz").read_bytes()), allow_pickle=False) as archive:
                arrays = {name: archive[name] for name in archive.files}
            sidecar = {"design_id": did, "key": row["key"], "upstream": upstream, "fingerprint": stem.name,
                       "payload_sha256": row["sha256"], "n_rows": 2}
            assert json.loads(stem.with_suffix(".json").read_text()) == sidecar
            assert _same_arrays(arrays, {"q": _b2u_q(setup, row["key"][5])})
    stems, after = {_partition_stem(staging, did, upstream, key).name for key in plan["DEV"]}, _tree(staging)
    assert set(after) == set(before) | {f"partitions/{s}.{e}" for s in stems for e in ("npz", "json")}
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    assert json.loads(after["resources.json"])["cpu_seconds"] == {"invocation-1": 6.0, "invocation-2": 3.0}


def test_dev_library_cache_reloads_committed_batches_without_producers_or_scientific_rewrites(tmp_path, monkeypatch):
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    assert plan["DEV"] == _b2u_qualify(fixture, record)
    cache, calls, reductions, reloads = _kernel("dev_library_cache"), [], [], []
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, True)
        first = cache(cfg, "full", context)
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reloads, desc, False)
        again = cache(cfg, "full", renewed)
    after = _tree(staging)
    assert again == first and len(calls) == 12 and len(reloads) <= 3 and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    for setup in desc["scope"]["setups"]:
        setup_id, rows, library_id = _b2u_expected(staging, record, plan, setup)
        out = again[pdb.canon(setup)]
        assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, rows, library_id]
    spent = json.loads(after["resources.json"])["cpu_seconds"]
    assert spent == {"invocation-1": 6.0, "invocation-2": 3.0, "invocation-3": 0.0}


def test_dev_library_cache_refuses_a_plan_missing_one_family_batch_before_any_effect(tmp_path, monkeypatch):
    drop = ["DEV_LIB", "FULL", "FITTED_LW_T7", 24, 0, "F_HEAD_RESIDUAL"]
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch, drop)
    cfg, desc, _, plan, staging = fixture
    logical = _b2u_qualify(fixture, record)
    assert drop in logical and plan["DEV"] == [key for key in logical if key != drop] and len(plan["DEV"]) == 11
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        with pytest.raises(ValueError):
            cache(cfg, "full", context)
    assert calls == [] and reductions == [] and _tree(staging) == before


@pytest.mark.parametrize(("index", "alias"), ((1, 24.0), (2, False)))
def test_dev_library_cache_refuses_a_setup_claim_equal_only_by_python_aliasing(tmp_path, monkeypatch, index, alias):
    import json
    fixture, state = _b2u_fixture(tmp_path, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cfg, desc, authority, plan, staging = fixture
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in plan["SETUP"]:
        _b2o_cache(staging, key, _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]))
    refs, planned, fit7 = _b2o_references(desc, monkeypatch), ["FITTED_LW_T7", 24, 0], _b2o_fit("FITTED_LW_T7")
    t7, poisoned = pdb.canon(planned), json.loads(pdb.canon(refs))
    poisoned[t7]["setup"][index] = alias
    record = _kernel("phase_record")(staging, "SETUP", {}, plan["SETUP"], {"setups": poisoned})
    claimed = record["derived"]["setups"][t7]["setup"]
    stored = json.loads((staging / "phases" / "SETUP.json").read_text())["derived"]["setups"][t7]["setup"]
    assert refs[t7]["setup"] == planned and [type(v) for v in refs[t7]["setup"]] == [str, int, int]
    assert claimed == planned and pdb.canon(claimed) != pdb.canon(planned) and type(stored[index]) is type(alias)
    assert [k for k in refs if pdb.canon(poisoned[k]) != pdb.canon(refs[k])] == [t7]
    assert [f for f in refs[t7] if pdb.canon(poisoned[t7][f]) != pdb.canon(refs[t7][f])] == ["setup"]
    assert refs[t7]["fit_hash"] == pdb.array_sha256(fit7["V"], fit7["lam"], fit7["mean"])
    assert record["derived"]["setups"][t7]["applications"] == refs[t7]["applications"]
    progress = _kernel("_planned_progress")(staging, record["design_id"], desc, plan, None)
    assert progress[0] == {"SETUP": record} and [entry["key"] for entry in progress[1]] == plan["DEV"]
    assert all(_kernel("_verify_partition")(staging, record["design_id"], {}, key)[1] == 24 for key in plan["SETUP"])
    assert plan["DEV"] == _b2u_qualify(fixture, record)
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        with pytest.raises(pdb.PartitionMismatch):
            cache(cfg, "full", context)
    after = _tree(staging)
    assert calls == [] and reductions == [] and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_dev_library_cache_refuses_a_missing_setup_record_without_generating_it(tmp_path, monkeypatch):
    fixture, state = _b2u_fixture(tmp_path, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cfg, desc, authority, plan, staging = fixture
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    setups, primitive = desc["scope"]["setups"], _kernel("seed_plan")(cfg, "full")["keys"]
    logical = sorted((["DEV_LIB", "FULL", *s, f] for s in setups for f in DEV_FAMILIES), key=pdb.canon)
    _kernel("_validated_plan")(plan)
    assert pdb.canon(_kernel("design_descriptor")(cfg, "full")) == pdb.canon(desc)
    assert pdb.canon(_kernel("authorize")("full", cfg, desc, 1)) == pdb.canon(authority)
    assert plan["SETUP"] == sorted(([*k] for k in primitive if k[0] in ("frame", "fit")), key=pdb.canon)
    assert plan["DEV"] == logical and len(logical) == 12
    assert set(_tree(staging)) == {"design.json", "resources.json"} and not (staging / "phases").exists()
    before, calls, reductions = _tree(staging), [], []
    cache, phase_order = _kernel("dev_library_cache"), _kernel("PhaseOrderError")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        _b2s_forbid(mp, "setup_phase")
        with pytest.raises(phase_order):
            cache(cfg, "full", context)
    after = _tree(staging)
    assert calls == [] and reductions == [] and set(after) == set(before)
    assert after["design.json"] == before["design.json"] and not (staging / "partitions").exists()


def test_dev_library_cache_refuses_a_float32_t7_batch_before_any_missing_producer(tmp_path, monkeypatch):
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, _, plan, staging = fixture
    did, upstream = record["design_id"], {"SETUP": record["phase_digest"]}
    t7, family = ["FITTED_LW_T7", 24, 0], "F0_ISOTROPIC_RESIDUAL"
    key, gaussian = ["DEV_LIB", "FULL", *t7, family], ["DEV_LIB", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, family]
    assert plan["DEV"] == _b2u_qualify(fixture, record) and plan["DEV"].index(gaussian) < plan["DEV"].index(key)
    _kernel("partition")(staging, "DEV", upstream, key, lambda: {"q": _b2u_q(t7, family).astype(np.float32)})
    sha, n_rows, arrays = _kernel("_verify_partition")(staging, did, upstream, key)
    q, progress = arrays["q"], _kernel("_planned_progress")(staging, did, desc, plan, None)
    pending = [entry["key"] for entry in progress[1]]
    assert set(arrays) == {"q"} and q.dtype == np.float32 and q.shape == (2, 20) and n_rows == 2 and len(sha) == 64
    assert np.isfinite(q).all() and (q >= 0).all() and np.array_equal(q, _b2u_q(t7, family).astype(np.float32))
    assert progress[0] == {"SETUP": record} and gaussian in pending and key not in pending
    assert pending == [k for k in plan["DEV"] if k != key]
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        with pytest.raises(pdb.PartitionMismatch):
            cache(cfg, "full", context)
    after = _tree(staging)
    assert calls == [] and reductions == [] and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


B2U_STORED = {"negative": ({"q"}, "float64", (2, 20)), "int64": ({"q"}, "int64", (2, 20)),
              "bool": ({"q"}, "bool", (2, 20)), "columns_19": ({"q"}, "float64", (2, 19)),
              "rows_3": ({"q"}, "float64", (3, 20)), "rank_1": ({"q"}, "float64", (2,)),
              "extra": ({"q", "extra"}, "float64", (2, 20)), "missing_q": ({"other"}, None, None)}
B2U_PRODUCER = {"none": ("NoneType", None, "NoneType"), "empty": ("dict", [], "NoneType"),
                "other_key": ("dict", ["other"], "NoneType"), "list": ("dict", ["q"], "list"),
                "complex": ("c", 16, (2, 20), 0, 0, 0), "text": ("U", 0, (2, 20), 0, 0, 0),
                "bool": ("b", 0, (2, 20), 0, 0, 0), "int64": ("i", 8, (2, 20), 0, 0, 0),
                "float32": ("f", 4, (2, 20), 0, 0, 0), "rows_3": ("f", 8, (3, 20), 0, 0, 0),
                "columns_19": ("f", 8, (2, 19), 0, 0, 0), "negative": ("f", 8, (2, 20), 1, 0, 0),
                "nan": ("f", 8, (2, 20), 0, 1, 0), "inf": ("f", 8, (2, 20), 0, 0, 1)}


def _b2u_stored(case):
    q = np.array(_b2u_q(["FITTED_LW_T7", 24, 0], "F0_ISOTROPIC_RESIDUAL"))
    if case == "negative":
        q[1, 3] = -0.25
    return {"negative": {"q": q}, "int64": {"q": np.arange(40, dtype=np.int64).reshape(2, 20)},
            "bool": {"q": q > 0.01}, "columns_19": {"q": q[:, :19]}, "rows_3": {"q": np.vstack([q, q[:1]])},
            "rank_1": {"q": q[:, 0]}, "extra": {"q": q, "extra": np.zeros((2, 1))}, "missing_q": {"other": q}}[case]


def _b2u_poison(case, q):
    bad = np.array(q)
    if case in ("negative", "nan", "inf"):
        bad[0, 5] = {"negative": -0.5, "nan": math.nan, "inf": math.inf}[case]
    shaped = {"complex": q + 1j, "text": q.astype(str), "bool": q > 0.01, "int64": (q * 100).astype(np.int64),
              "float32": q.astype(np.float32), "rows_3": np.vstack([q, q[:1]]), "columns_19": q[:, :19]}
    plain = {"none": None, "empty": {}, "other_key": {"other": q}, "list": {"q": q.tolist()}}
    return plain[case] if case in plain else {"q": shaped.get(case, bad)}


def _b2u_facts(value):
    q = value.get("q") if isinstance(value, dict) else None
    if not isinstance(q, np.ndarray):
        return type(value).__name__, sorted(value) if isinstance(value, dict) else None, type(q).__name__
    kind, floats = q.dtype.kind, q if q.dtype.kind == "f" else np.zeros(1)
    negatives = int((q < 0).sum()) if kind in "fi" else 0
    width = q.dtype.itemsize if kind in "fic" else 0
    return kind, width, q.shape, negatives, int(np.isnan(floats).sum()), int(np.isinf(floats).sum())


@pytest.mark.parametrize("case", B2U_STORED)
def test_dev_library_cache_refuses_a_stored_t7_batch_off_the_q_schema_before_production(tmp_path, monkeypatch, case):
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, _, plan, staging = fixture
    did, upstream = record["design_id"], {"SETUP": record["phase_digest"]}
    t7, family = ["FITTED_LW_T7", 24, 0], "F0_ISOTROPIC_RESIDUAL"
    key, gaussian = ["DEV_LIB", "FULL", *t7, family], ["DEV_LIB", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, family]
    assert plan["DEV"] == _b2u_qualify(fixture, record) and plan["DEV"].index(gaussian) < plan["DEV"].index(key)
    payload, snapshot = _b2u_stored(case), pdb.canon(desc)
    _kernel("partition")(staging, "DEV", upstream, key, lambda: payload)
    sha, n_rows, arrays = _kernel("_verify_partition")(staging, did, upstream, key)
    (names, dtype, shape), q = B2U_STORED[case], arrays.get("q")
    assert set(arrays) == names and len(sha) == 64 and n_rows == next(iter(arrays.values())).shape[0]
    assert (q is None and dtype is None) or (q.dtype.name, q.shape) == (dtype, shape)
    assert all(np.isfinite(a).all() for a in arrays.values() if a.dtype.kind == "f")
    assert sum(int((a < 0).sum()) for a in arrays.values() if a.dtype.kind in "fi") == int(case == "negative")
    progress = _kernel("_planned_progress")(staging, did, desc, plan, None)
    pending = [entry["key"] for entry in progress[1]]
    assert progress[0] == {"SETUP": record} and gaussian in pending and key not in pending
    assert pending == [k for k in plan["DEV"] if k != key]
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        with pytest.raises(pdb.PartitionMismatch):
            cache(cfg, "full", context)
    after = _tree(staging)
    assert calls == [] and reductions == [] and set(after) == set(before) and pdb.canon(desc) == snapshot
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


@pytest.mark.parametrize("case", B2U_PRODUCER)
def test_dev_library_cache_refuses_a_bad_producer_payload_before_serializing_it(tmp_path, monkeypatch, case):
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, _, plan, staging = fixture
    first, snapshot = plan["DEV"][0], pdb.canon(desc)
    setup, family = first[2:5], first[5]
    good = _b2u_q(setup, family)
    poison, kept = _b2u_poison(case, good), good.tobytes()
    assert plan["DEV"] == _b2u_qualify(fixture, record) and first[2:] == ["EXACT", 24, 0, "F0_ISOTROPIC_RESIDUAL"]
    assert _b2u_facts({"q": good}) == ("f", 8, (2, 20), 0, 0, 0) and not good.flags.writeable
    assert _b2u_facts(poison) == B2U_PRODUCER[case] != _b2u_facts({"q": good})
    progress = _kernel("_planned_progress")(staging, record["design_id"], desc, plan, None)
    assert progress[0] == {"SETUP": record} and [entry["key"] for entry in progress[1]] == plan["DEV"]
    module, before, calls, reductions = pio(), _tree(staging), [], []
    cache = _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, True)
        stub = module.dev_library_block

        def poisoned(*args, **kwargs):
            out = stub(*args, **kwargs)
            assert set(out) == {"q"} and np.array_equal(out["q"], good)
            return poison

        def forbidden(*args, **kwargs):
            raise AssertionError("a DEV_LIB payload was serialized before the producer schema guard")

        mp.setattr(module, "dev_library_block", poisoned)
        mp.setattr(module, "_npz_payload", forbidden)
        with pytest.raises(ValueError):
            cache(cfg, "full", context)
    after = _tree(staging)
    assert calls == [(pdb.canon(setup), family)] and reductions == [] and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    spent = json.loads(after["resources.json"])["cpu_seconds"]
    assert spent == {"invocation-1": 6.0, "invocation-2": 0.25} and good.tobytes() == kept
    assert pdb.canon(desc) == snapshot


B2U_EXACT_F0 = ["DEV_LIB", "FULL", "EXACT", 24, 0, "F0_ISOTROPIC_RESIDUAL"]
B2U_INVENTORY = {"setup_missing_fit": ("SETUP", ["fit", "FULL", "FITTED_LW_T7", 24, 0], None),
                 "setup_extra_fit": ("SETUP", None, ["fit", "FULL", "FITTED_LW_GAUSSIAN", 24, 1]),
                 "dev_lib_market_family": ("DEV", None, ["DEV_LIB", "FULL", "EXACT", 24, 0, "F3_MARKET"]),
                 "dev_lib_unscoped_n": ("DEV", B2U_EXACT_F0, [*B2U_EXACT_F0[:3], 26, *B2U_EXACT_F0[4:]]),
                 "dev_lib_primitive_index": ("DEV", B2U_EXACT_F0, [*B2U_EXACT_F0, 0])}
B2U_ADMISSION = ("other_design_valid_go", "authorization_removed", "go_tampered", "context_authority_forged",
                 "malformed_plan", *B2U_INVENTORY)


@pytest.mark.parametrize("case", B2U_ADMISSION)
def test_dev_library_cache_refuses_one_poisoned_admission_axis_before_any_effect(tmp_path, monkeypatch, case):
    describe, authorize, validated = _kernel("design_descriptor"), _kernel("authorize"), _kernel("_validated_plan")
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    did, go = record["design_id"], tmp_path / "prompts" / "GO-full-fixture.md"
    staged = _kernel("_staged_design")(staging)
    assert staged[0] == did and pdb.canon(staged[1]) == pdb.canon(describe(cfg, "full")) == pdb.canon(desc)
    assert authorize("full", cfg, desc, 1) == authority == context["authority"] and context["plan"] is plan
    assert validated(plan) is None and plan["SETUP"] == B2O_KEYS and pio().REPO_ROOT == tmp_path
    assert plan["DEV"] == _b2u_qualify(fixture, record) and context["token"] == "invocation-2"
    current, poisoned, error = cfg, context, ValueError
    if case == "other_design_valid_go":
        other = _authorized(tmp_path / "other", monkeypatch, _edited(cfg, ("seed",), cfg["seed"] + 1), "full")[0]
        other_desc = describe(other, "full")
        other_did = _kernel("design_id")(other_desc)
        assert pio().REPO_ROOT == tmp_path / "other" and other_did != did
        assert other_desc["science"] == desc["science"] and other_desc["seed"] == desc["seed"] + 1
        assert authorize("full", other, other_desc, 1)["design_id"] == other_did
        current, error = other, _kernel("StagingMismatch")
    elif case == "authorization_removed":
        current, error = {**cfg, "authorization": None}, _kernel("AuthorizationRefused")
        assert pdb.canon(describe(current, "full")) == pdb.canon(desc)
    elif case == "go_tampered":
        go.write_bytes(go.read_bytes() + b"Amended after the invocation started.")
        assert pdb.file_sha256(go) != authority["go_reference"]["sha256"]
        error = _kernel("AuthorizationRefused")
    elif case == "context_authority_forged":
        forged = {**authority, "go_reference": {**authority["go_reference"], "sha256": "0" * 64}}
        assert pdb.canon(forged) != pdb.canon(authority) == pdb.canon(authorize("full", cfg, desc, 1))
        poisoned, error = {**context, "authority": forged}, _kernel("AuthorizationRefused")
    elif case == "malformed_plan":
        poisoned = {**context, "plan": {phase: keys for phase, keys in plan.items() if phase != "ALT"}}
        with pytest.raises(ValueError):
            validated(poisoned["plan"])
    else:
        phase, remove, add = B2U_INVENTORY[case]
        changed = sorted([key for key in plan[phase] if key != remove] + ([add] if add else []), key=pdb.canon)
        poisoned = {**context, "plan": {**plan, phase: changed}}
        assert validated(poisoned["plan"]) is None and pdb.canon(changed) != pdb.canon(plan[phase])
        assert (remove is None or remove in plan[phase]) and (add is None or add not in plan[phase])
        assert add is None or tuple(add) not in set(_kernel("seed_plan")(cfg, "full")["keys"])
        if case == "dev_lib_market_family":
            assert "F3_MARKET" in desc["science"]["families"] and add[5] not in DEV_FAMILIES
        elif case == "dev_lib_unscoped_n":
            assert add[2:5] not in desc["scope"]["setups"] and add[3] == 26
        elif case == "dev_lib_primitive_index":
            assert len(add) == 7 and add[:6] == remove
    assert _kernel("_staged_design")(staging) == staged
    cache, before, calls, reductions = _kernel("dev_library_cache"), _tree(tmp_path), [], []
    inputs = pdb.canon([current, {**poisoned, "staging": str(poisoned["staging"])}])
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        _no_side_effects(mp)
        with pytest.raises(error):
            cache(current, "full", poisoned)
    root = tmp_path / "other" if case == "other_design_valid_go" else tmp_path
    assert _tree(tmp_path) == before and calls == [] and reductions == [] and pio().REPO_ROOT == root
    assert pdb.canon([current, {**poisoned, "staging": str(poisoned["staging"])}]) == inputs


def test_dev_library_cache_leaves_a_reserved_other_dev_role_pending_and_ungenerated(tmp_path, monkeypatch):
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, _, plan, staging = fixture
    did, upstream = record["design_id"], {"SETUP": record["phase_digest"]}
    reserved = ["DEV_NULL", "FULL", "FITTED_LW_GAUSSIAN", 24, 0, "fixture"]
    full = {**plan, "DEV": sorted([*plan["DEV"], reserved], key=pdb.canon)}
    library = {**full, "DEV": [key for key in full["DEV"] if key[0] == "DEV_LIB"]}
    assert plan["DEV"] == _b2u_qualify(fixture, record) == library["DEV"] and reserved in full["DEV"]
    assert _kernel("_validated_plan")(full) is None and len(full["DEV"]) == 13
    stem = _partition_stem(staging, did, upstream, reserved)
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, True)
        result = cache(cfg, "full", {**context, "plan": full})
    after, setups = _tree(staging), desc["scope"]["setups"]
    assert sorted(calls) == sorted((pdb.canon(s), f) for s in setups for f in DEV_FAMILIES) and len(reductions) == 3
    assert set(result) == {pdb.canon(s) for s in setups} and not (staging / "phases" / "DEV.json").exists()
    for setup in setups:
        setup_id, rows, library_id = _b2u_expected(staging, record, library, setup)
        out = result[pdb.canon(setup)]
        assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, rows, library_id]
        assert all(row["key"][0] == "DEV_LIB" for row in out["partitions"]) and len(rows) == 4
        assert out["qbar"] == pytest.approx(_b2u_qbar(setup), rel=1e-12)
        assert out["qbar_sha"] == pdb.array_sha256(np.array(out["qbar"], dtype=np.float64))
    progress = _kernel("_planned_progress")(staging, did, desc, full, None)
    stems = {_partition_stem(staging, did, upstream, key).name for key in library["DEV"]}
    assert progress[0] == {"SETUP": record} and [entry["key"] for entry in progress[1]] == [reserved]
    assert not stem.with_suffix(".json").exists() and not stem.with_suffix(".npz").exists()
    assert set(after) == set(before) | {f"partitions/{s}.{e}" for s in stems for e in ("npz", "json")}
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    assert json.loads(after["resources.json"])["cpu_seconds"] == {"invocation-1": 6.0, "invocation-2": 3.0}


B2U_SPENT = {"invocation-1": 6.0, "invocation-2": 0.0}


def _b2u_admitted(fixture, context):
    cfg, desc, authority, plan, staging = fixture
    setups, current = desc["scope"]["setups"], pdb.canon(_kernel("authorize")("full", cfg, desc, 1))
    logical = sorted((["DEV_LIB", "FULL", *s, f] for s in setups for f in DEV_FAMILIES), key=pdb.canon)
    staged = _kernel("_staged_design")(staging)[1]
    assert pdb.canon(_kernel("design_descriptor")(cfg, "full")) == pdb.canon(desc) == pdb.canon(staged)
    assert current == pdb.canon(authority) == pdb.canon(context["authority"]) and context["staging"] == staging
    assert context["plan"] is plan and _kernel("_validated_plan")(plan) is None and plan["SETUP"] == B2O_KEYS
    assert plan["DEV"] == logical and len(logical) == 12


def _b2u_refused(monkeypatch, state, fixture, context, error, spent):
    import json
    cfg, desc, _, _, staging = fixture
    inputs = pdb.canon([cfg, desc, {**context, "staging": str(context["staging"])}])
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, False)
        _b2s_forbid(mp, "setup_phase")
        with pytest.raises(error) as refused:
            cache(cfg, "full", context)
    after, now = _tree(staging), pdb.canon([cfg, desc, {**context, "staging": str(context["staging"])}])
    assert type(refused.value) is error and calls == [] and reductions == [] and now == inputs
    assert set(after) == set(before) and all(after[n] == data for n, data in before.items() if n != "resources.json")
    assert json.loads(after["resources.json"])["cpu_seconds"] == spent


def _b2u_paths(old, new, path=()):
    if not (isinstance(old, dict) and isinstance(new, dict)):
        return [] if pdb.canon(old) == pdb.canon(new) else [path]
    pairs = ((k, k in old and k in new) for k in sorted({*old, *new}))
    return [p for k, both in pairs for p in (_b2u_paths(old[k], new[k], (*path, k)) if both else [(*path, k)])]


B2U_DAMAGE = {"setup_fit_npz_missing": ("SETUP", False), "setup_fit_npz_corrupt": ("SETUP", True),
              "pending_dev_npz_missing": ("DEV", False), "pending_dev_npz_corrupt": ("DEV", True)}


@pytest.mark.parametrize("case", B2U_DAMAGE)
def test_dev_library_cache_refuses_a_missing_or_corrupt_npz_behind_its_kept_sidecar(tmp_path, monkeypatch, case):
    import hashlib
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    _, desc, _, plan, staging = fixture
    _b2u_admitted(fixture, context)
    did, upstream, (phase, corrupt) = record["design_id"], {"SETUP": record["phase_digest"]}, B2U_DAMAGE[case]
    verify, progress, t7 = _kernel("_verify_partition"), _kernel("_planned_progress"), ["FITTED_LW_T7", 24, 0]
    batch, gaussian = (["DEV_LIB", "FULL", *setup, DEV_FAMILIES[0]] for setup in (t7, B2O_SETUPS[1]))
    pending = [{"phase": "DEV", "key": key} for key in plan["DEV"]]
    assert plan["DEV"] == _b2u_qualify(fixture, record) and plan["DEV"].index(gaussian) < plan["DEV"].index(batch)
    assert progress(staging, did, desc, plan, None) == ({"SETUP": record}, pending)
    if phase == "SETUP":
        key, lineage, kept = B2O_KEYS[1], {}, _b2o_fit("FITTED_LW_T7")
    else:
        key, lineage, kept = batch, upstream, {"q": _b2u_q(t7, DEV_FAMILIES[0])}
        _kernel("partition")(staging, "DEV", upstream, key, lambda: kept)
        assert progress(staging, did, desc, plan, None)[1] == [entry for entry in pending if entry["key"] != batch]
    assert _same_arrays(verify(staging, did, lineage, key)[2], kept)
    npz, sidecar = (_partition_stem(staging, did, lineage, key).with_suffix(ext) for ext in (".npz", ".json"))
    claimed, stored = json.loads(sidecar.read_text())["payload_sha256"], sidecar.read_bytes()
    assert claimed == hashlib.sha256(npz.read_bytes()).hexdigest() and (staging / "phases" / "SETUP.json").is_file()
    if corrupt:
        npz.write_bytes(npz.read_bytes() + b"x")
        assert claimed != hashlib.sha256(npz.read_bytes()).hexdigest()
    else:
        npz.unlink()
    assert sidecar.read_bytes() == stored and npz.exists() == corrupt
    with pytest.raises(pdb.PartitionMismatch):
        verify(staging, did, lineage, key)
    _b2u_refused(monkeypatch, state, fixture, context, pdb.PartitionMismatch, B2U_SPENT)


B2U_SEMANTIC = {"frame_n25": None, "fit_t7_nonsquare": None, "t7_learned_mean": None, "t7_design_id": ("design_id",),
                "t7_basis_sha": ("basis_sha",), "t7_setup_id": ("applications", "RESIDUAL", "setup_id"),
                "t7_member_omitted": (), "t7_market_removed": ("applications", "MARKET"), "t7_member_none": ()}


@pytest.mark.parametrize("case", B2U_SEMANTIC)
def test_dev_library_cache_refuses_a_storage_valid_setup_with_one_semantic_poison(tmp_path, monkeypatch, case):
    import hashlib
    import json
    fixture, state, path = _b2u_fixture(tmp_path, monkeypatch), {"cpu": 10.0, "wall": 100.0}, B2U_SEMANTIC[case]
    _, desc, authority, plan, staging = fixture
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    _b2u_admitted(fixture, context)
    did, refs, setup_cache = _kernel("design_id")(desc), _b2o_references(desc, monkeypatch), _kernel("_setup_cache")
    (t7, frame), member = (pdb.canon(key) for key in B2O_KEYS[1:]), pdb.canon(list(B2O_SETUPS[2]))
    base = {pdb.canon(key): _b2o_frame() if key[0] == "frame" else _b2o_fit(key[2]) for key in B2O_KEYS}
    hashes = {name: pdb.array_sha256(a["V"], a["lam"], a["mean"]) for name, a in base.items()}
    claims = [refs[member][field] for field in ("design_id", "setup", "basis_sha", "fit_hash")]
    assert set(_tree(staging)) == {"design.json", "resources.json"} and B2O_KEYS[1][2:] == list(B2O_SETUPS[2])
    assert set(refs) == {pdb.canon(list(setup)) for setup in B2O_SETUPS} and member in refs
    assert all(_same_arrays(setup_cache(base[pdb.canon(key)], key), base[pdb.canon(key)]) for key in B2O_KEYS)
    assert claims == [did, list(B2O_SETUPS[2]), hashes[frame], hashes[t7]]
    assert sorted(refs[member]["applications"]) == ["MARKET", "RESIDUAL"] == sorted(desc["scope"]["applications"])
    arrays, members = dict(base), json.loads(pdb.canon(refs))
    meta, shaped = members[member], {"frame_n25": B2O_KEYS[2], "fit_t7_nonsquare": B2O_KEYS[1]}.get(case)
    if case == "frame_n25":
        arrays[frame] = {"V": np.eye(25), "lam": _b2b_spectrum(25), "mean": np.zeros(25)}
        assert [a.shape for a in arrays[frame].values()] == [(25, 25), (25,), (25,)]
        assert _same_arrays(setup_cache(arrays[frame], ["frame", "FULL", 25]), arrays[frame])
    elif case == "fit_t7_nonsquare":
        arrays[t7] = {**base[t7], "V": base[t7]["V"][:, :23]}
        assert [a.shape for a in arrays[t7].values()] == [(24, 23), (24,), (24,)] and base[t7]["V"].shape == (24, 24)
    elif case == "t7_learned_mean":
        arrays[t7] = {**base[t7], "mean": base[t7]["mean"] + 0.125}
        learned = pdb.array_sha256(arrays[t7]["V"], arrays[t7]["lam"], arrays[t7]["mean"])
        assert np.allclose(arrays[t7]["mean"] - base[t7]["mean"], 0.125) and learned != meta["fit_hash"] == hashes[t7]
    elif case in ("t7_design_id", "t7_basis_sha"):
        meta[path[0]] = hashlib.sha256(meta[path[0]].encode()).hexdigest()
        assert _kernel("_is_sha")(meta[path[0]])
    elif case == "t7_setup_id":
        residual = meta["applications"]["RESIDUAL"]
        residual["setup_id"] = hashlib.sha256(residual["setup_id"].encode()).hexdigest()[:16]
        assert len(residual["setup_id"]) == 16 and set(residual["setup_id"]) <= set("0123456789abcdef")
    elif case == "t7_member_omitted":
        del members[member]
    elif case == "t7_market_removed":
        del meta["applications"]["MARKET"]
        assert sorted(meta["applications"]) == ["RESIDUAL"]
    else:
        members[member] = None
    moved = [name for name in base if not _same_arrays(arrays[name], base[name])]
    assert moved == ({"frame_n25": [frame]}.get(case, [t7]) if path is None else [])
    assert _b2u_paths(refs, members) == ([] if path is None else [(member, *path)])
    assert (member in members) == (case != "t7_member_omitted")
    phase_record = _kernel("phase_record")
    for key in plan["SETUP"]:
        assert _same_arrays(_b2o_cache(staging, key, arrays[pdb.canon(key)]), arrays[pdb.canon(key)])
        if key == shaped:
            with pytest.raises(ValueError):
                setup_cache(arrays[pdb.canon(key)], key)
        else:
            assert _same_arrays(setup_cache(arrays[pdb.canon(key)], key), arrays[pdb.canon(key)])
    record = phase_record(staging, "SETUP", {}, plan["SETUP"], {"setups": members})
    progress = _kernel("_planned_progress")(staging, did, desc, plan, None)
    rows = [_kernel("_verify_partition")(staging, did, {}, key)[1] for key in plan["SETUP"]]
    assert phase_record(staging, "SETUP", {}, None, None) == record and record["derived"] == {"setups": members}
    assert progress[0] == {"SETUP": record} and [entry["key"] for entry in progress[1]] == plan["DEV"]
    assert rows == [24, 24, 25 if case == "frame_n25" else 24] and record["upstream"] == {}
    _b2u_refused(monkeypatch, state, fixture, context, pdb.PartitionMismatch, {"invocation-1": 0.0})


B2U_ENGAGED = ("dev_record_one_batch", "dev_record_int64_batch", "setup_record_removed")


@pytest.mark.parametrize("case", B2U_ENGAGED)
def test_dev_library_cache_refuses_an_engaged_synthetic_dev_state_without_rewriting_it(tmp_path, monkeypatch, case):
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    _, desc, _, plan, staging = fixture
    _b2u_admitted(fixture, context)
    did, upstream, phases = record["design_id"], {"SETUP": record["phase_digest"]}, staging / "phases"
    phase_record, progress = _kernel("phase_record"), _kernel("_planned_progress")
    batch, verify = ["DEV_LIB", "FULL", "FITTED_LW_T7", 24, 0, DEV_FAMILIES[0]], _kernel("_verify_partition")
    assert plan["DEV"] == _b2u_qualify(fixture, record) and batch in plan["DEV"] and len(plan["DEV"]) == 12
    assert [row["key"] for row in record["partitions"]] == plan["SETUP"] and record["upstream"] == {}
    keys = [batch] if case == "dev_record_one_batch" else plan["DEV"]
    for key in keys:
        wide = case == "dev_record_int64_batch" and key == batch
        q = np.arange(40, dtype=np.int64).reshape(2, 20) if wide else _b2u_q(key[2:5], key[5])
        _kernel("partition")(staging, "DEV", upstream, key, lambda q=q: {"q": q})
        assert _same_arrays(verify(staging, did, upstream, key)[2], {"q": q}) and (q.dtype == np.int64) == wide
    dev = phase_record(staging, "DEV", upstream, keys, {"fixture": "INTEGRITY_ONLY"})
    assert phase_record(staging, "DEV", upstream, None, None) == dev and dev["upstream"] == upstream
    assert [row["key"] for row in dev["partitions"]] == keys and all(row["n_rows"] == 2 for row in dev["partitions"])
    error = pdb.PartitionMismatch
    if case == "dev_record_one_batch":
        assert len(keys) == 1 != len(plan["DEV"])
        with pytest.raises(error):
            progress(staging, did, desc, plan, None)
    else:
        assert progress(staging, did, desc, plan, None) == ({"SETUP": record, "DEV": dev}, [])
    if case == "setup_record_removed":
        (phases / "SETUP.json").unlink()
        error = _kernel("PhaseOrderError")
        with pytest.raises(error):
            progress(staging, did, desc, plan, None)
        assert (phases / "DEV.json").is_file() and not (phases / "SETUP.json").exists()
    _b2u_refused(monkeypatch, state, fixture, context, error, B2U_SPENT)


B2U_CRASHES = {"npz_orphan": (".npz", 1, 0, 0.25, 3.0), "batch_durable": (".json", 1, 1, 0.25, 2.75),
               "reducer_error": (None, 12, 12, 3.125, 0.0)}


@pytest.mark.parametrize("case", B2U_CRASHES)
def test_dev_library_cache_recovers_each_interruption_into_the_reference_library(tmp_path, monkeypatch, case):
    import json
    (suffix, crashed, start, second, third), module = B2U_CRASHES[case], pio()
    cache, verify, progress = _kernel("dev_library_cache"), _kernel("_verify_partition"), _kernel("_planned_progress")
    ref_fixture, ref_state, ref_record, ref_context = _b2u_first(tmp_path / "reference", monkeypatch)
    ref_cfg, ref_desc, ref_authority, ref_plan, ref_staging = ref_fixture
    ref_calls, ref_reductions = [], []
    assert module.REPO_ROOT == tmp_path / "reference" and ref_plan["DEV"] == _b2u_qualify(ref_fixture, ref_record)
    _b2u_admitted(ref_fixture, ref_context)
    with monkeypatch.context() as mp:
        _b2u_traps(mp, ref_state, ref_calls, ref_reductions, ref_desc, True)
        _b2s_forbid(mp, "setup_phase")
        expected = cache(ref_cfg, "full", ref_context)
    assert ref_calls == [(pdb.canon(key[2:5]), key[5]) for key in ref_plan["DEV"]] and len(ref_reductions) == 3
    for setup in ref_desc["scope"]["setups"]:
        setup_id, rows, library_id = _b2u_expected(ref_staging, ref_record, ref_plan, setup)
        out = expected[pdb.canon(setup)]
        assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, rows, library_id]
        assert out["qbar"] == pytest.approx(_b2u_qbar(setup), rel=1e-12)
    reference = _tree(ref_staging)
    scientific = {name: data for name, data in reference.items() if name != "resources.json"}
    assert json.loads(reference["resources.json"])["cpu_seconds"] == {"invocation-1": 6.0, "invocation-2": 3.0}
    fixture, state, record, context = _b2u_first(tmp_path / "work", monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    did, upstream, snapshot = record["design_id"], {"SETUP": record["phase_digest"]}, pdb.canon([cfg, desc, plan])
    stems = [_partition_stem(staging, did, upstream, key).name for key in plan["DEV"]]
    first, pending = staging / "partitions" / stems[0], [{"phase": "DEV", "key": key} for key in plan["DEV"]]
    sidecar = json.loads(reference[f"partitions/{stems[0]}.json"])
    assert module.REPO_ROOT == tmp_path / "work" and record == ref_record and staging.name == ref_staging.name
    assert pdb.canon(desc) == pdb.canon(ref_desc) and authority == ref_authority and plan == ref_plan
    assert plan["DEV"] == _b2u_qualify(fixture, record) and plan["DEV"][0] == B2U_EXACT_F0
    _b2u_admitted(fixture, context)
    assert [sidecar["fingerprint"], sidecar["upstream"], sidecar["key"]] == [stems[0], upstream, B2U_EXACT_F0]
    assert progress(staging, did, desc, plan, None) == ({"SETUP": record}, pending)
    assert json.loads((staging / "resources.json").read_text())["cpu_seconds"] == B2U_SPENT
    sentinel, fired, calls, reductions = OSError("interrupted DEV_LIB library work"), [], [], []
    real_write, target = module._write_atomic, first.with_suffix(suffix) if suffix else None
    before = _tree(staging)

    def write(path, data):
        real_write(path, data)
        if path == target:
            fired.append(path)
            raise sentinel

    def reduce(given, q_by_family):
        spy(given, q_by_family)
        fired.append("qbar")
        state["cpu"] += 0.125
        raise sentinel

    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, True)
        _b2s_forbid(mp, "setup_phase")
        spy = module.dev_qbar
        mp.setattr(module, "_write_atomic", write)
        if suffix is None:
            mp.setattr(module, "dev_qbar", reduce)
        with pytest.raises(OSError) as caught:
            cache(cfg, "full", context)
    after, spent = _tree(staging), {"invocation-1": 6.0, "invocation-2": second}
    durable = {f"partitions/{s}.{e}" for s in stems[:start] for e in ("npz", "json")}
    durable |= {f"partitions/{stems[0]}.npz"} if suffix == ".npz" else set()
    pooled = {family: _b2u_q(desc["scope"]["setups"][0], family) for family in DEV_FAMILIES}
    assert caught.value is sentinel and fired == [target if suffix else "qbar"]
    assert calls == [(pdb.canon(key[2:5]), key[5]) for key in plan["DEV"][:crashed]]
    assert len(reductions) == int(suffix is None) and all(_same_arrays(q, pooled) for q, _ in reductions)
    assert set(after) - set(before) == durable and all(after[name] == reference[name] for name in durable)
    assert set(before) <= set(after) and all(after[n] == data for n, data in before.items() if n != "resources.json")
    assert json.loads(after["resources.json"])["cpu_seconds"] == spent and "phases/DEV.json" not in after
    assert progress(staging, did, desc, plan, None) == ({"SETUP": record}, pending[start:])
    for key in plan["DEV"][:start]:
        assert _same_arrays(verify(staging, did, upstream, key)[2], {"q": _b2u_q(key[2:5], key[5])})
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    kept, again, recovered = _tree(staging), [], []
    _b2u_admitted(fixture, renewed)
    assert json.loads(kept["resources.json"])["cpu_seconds"] == {**spent, "invocation-3": 0.0}
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, again, recovered, desc, start < len(plan["DEV"]))
        _b2s_forbid(mp, "setup_phase")
        result = cache(cfg, "full", renewed)
    final = _tree(staging)
    assert again == [(pdb.canon(key[2:5]), key[5]) for key in plan["DEV"][start:]] and len(recovered) == 3
    assert result == expected and progress(staging, did, desc, plan, None) == ({"SETUP": record}, [])
    assert all(final[name] == data for name, data in kept.items() if name != "resources.json")
    assert {name: data for name, data in final.items() if name != "resources.json"} == scientific
    assert json.loads(final["resources.json"])["cpu_seconds"] == {**spent, "invocation-3": third}
    assert pdb.canon([cfg, desc, plan]) == snapshot and "phases/DEV.json" not in final


def _b2u_budgeted(tmp_path, monkeypatch, complete):
    import json
    fixture, state, record, context = _b2u_first(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    did, handoff, calls, reductions = record["design_id"], None, [], []
    assert plan["DEV"] == _b2u_qualify(fixture, record)
    if complete:
        with monkeypatch.context() as mp:
            _b2u_traps(mp, state, calls, reductions, desc, True)
            handoff = _kernel("dev_library_cache")(cfg, "full", context)
        with monkeypatch.context() as mp:
            _b1m_clock(mp, state)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
        for setup in desc["scope"]["setups"]:
            setup_id, rows, library_id = _b2u_expected(staging, record, plan, setup)
            out = handoff[pdb.canon(setup)]
            assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, rows, library_id]
            assert out["qbar"] == pytest.approx(_b2u_qbar(setup), rel=1e-12)
    spent = {**B2U_SPENT, "invocation-2": 3.0, "invocation-3": 0.0} if complete else B2U_SPENT
    pending = [] if complete else [{"phase": "DEV", "key": key} for key in plan["DEV"]]
    cap = desc["envelope"]["cpu_hours_max"] * 3600
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        remaining = _kernel("require_budget")(staging, authority, plan, context["started"])
    _b2u_admitted(fixture, context)
    assert [len(calls), len(reductions), remaining] == [12 * complete, 3 * complete, cap - sum(spent.values())]
    assert json.loads((staging / "resources.json").read_text())["cpu_seconds"] == spent and remaining > 0
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({"SETUP": record}, pending)
    assert not {"status.json", "phases/DEV.json"} & set(_tree(staging))
    return fixture, state, record, context, handoff, cap


def _b2u_resource(monkeypatch, state, fixture, context, producer, fakes, error):
    import json
    module, (cfg, desc), staging = pio(), fixture[:2], fixture[4]
    spent, inputs = json.loads((staging / "resources.json").read_text())["cpu_seconds"], pdb.canon(fixture[:4])
    before, calls, reductions, cache = _tree(staging), [], [], _kernel("dev_library_cache")
    with monkeypatch.context() as mp:
        _b2u_traps(mp, state, calls, reductions, desc, producer)
        _b2s_forbid(mp, "setup_phase")
        for name, wrap in fakes:
            mp.setattr(module, name, wrap(getattr(module, name)))
        with pytest.raises(error) as caught:
            cache(cfg, "full", context)
    after = _tree(staging)
    spent[context["token"]] = state["cpu"] - context["cpu_start"]
    assert type(caught.value) is error and "status.json" not in before and pdb.canon(fixture[:4]) == inputs
    assert json.loads(after["resources.json"])["cpu_seconds"] == spent
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    return caught.value, calls, reductions, sorted(set(after) - set(before)), after


B2U_BLOCKED = {"empty_cpu": (False, None, 0, 0, 0, 1.0), "reload_wall": (True, None, 12, 0, 0, None),
               "reload_preflight_cpu": (True, "_setup_provenance", 12, 0, 0, 1.0),
               "reload_reduction_cpu": (True, "dev_qbar", 12, 0, 3, 1.0),
               "between_batches": (False, "dev_library_block", 1, 1, 0, 1.25)}


@pytest.mark.parametrize("case", B2U_BLOCKED)
def test_dev_library_cache_blocks_at_a_cpu_or_wall_checkpoint_with_the_exact_status(tmp_path, monkeypatch, case):
    import json
    (complete, wrapped, durable, produced, reduced, extra), bumped = B2U_BLOCKED[case], []
    fixture, state, record, context, _, cap = _b2u_budgeted(tmp_path, monkeypatch, complete)
    _, desc, _, plan, staging = fixture
    did, upstream = record["design_id"], {"SETUP": record["phase_digest"]}
    current = 0.0 if extra is None else cap + extra

    def once(real):
        def measured(*args):
            result = real(*args)
            if not bumped:
                bumped.append(len(args))
                state["cpu"] += cap + 1.0
            return result
        return measured

    if case == "empty_cpu":
        state["cpu"] = context["cpu_start"] + cap + 1.0
    if case == "reload_wall":
        state["wall"] = context["started"] + desc["envelope"]["wall_seconds_per_invocation"]
    fakes = [(wrapped, once)] if wrapped else []
    outcome = _b2u_resource(monkeypatch, state, fixture, context, produced > 0, fakes, _kernel("ResourceBlocked"))
    calls, reductions, added, after = outcome[1:]
    missing = [{"phase": "DEV", "key": key} for key in plan["DEV"][durable:]]
    stems = [_partition_stem(staging, did, upstream, key).name for key in plan["DEV"][:produced]]
    status = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": "SETUP"}
    assert json.loads(after["status.json"]) == {**status, "missing_partitions": missing}
    assert added == sorted(["status.json", *(f"partitions/{s}.{e}" for s in stems for e in ("npz", "json"))])
    assert calls == [(pdb.canon(key[2:5]), key[5]) for key in plan["DEV"][:produced]] and len(reductions) == reduced
    assert len(bumped) == int(wrapped is not None) and state["cpu"] - context["cpu_start"] == current
    for key in plan["DEV"][:produced]:
        sha, n_rows, arrays = _kernel("_verify_partition")(staging, did, upstream, key)
        assert _same_arrays(arrays, {"q": _b2u_q(key[2:5], key[5])}) and n_rows == 2 and len(sha) == 64


def test_dev_library_cache_charges_each_reload_once_per_token_without_double_counting(tmp_path, monkeypatch):
    import json
    fixture, state, _, context, handoff, _ = _b2u_budgeted(tmp_path, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    module, cache, checks, before = pio(), _kernel("dev_library_cache"), [], _tree(staging)
    real_provenance, start = module._setup_provenance, state["cpu"]

    def provenance(*args):
        ids = real_provenance(*args)
        checks.append(ids)
        state["cpu"] += 0.125
        return ids

    def run(current):
        calls, reductions = [], []
        with monkeypatch.context() as mp:
            _b2u_traps(mp, state, calls, reductions, desc, False)
            _b2s_forbid(mp, "setup_phase")
            spy = module.dev_qbar

            def reduce(*args):
                qbar = spy(*args)
                state["cpu"] += 0.125
                return qbar

            mp.setattr(module, "dev_qbar", reduce)
            mp.setattr(module, "_setup_provenance", provenance)
            result = cache(cfg, "full", current)
        assert result == handoff and calls == [] and len(reductions) == 3
        assert sorted(qbar.tolist() for _, qbar in reductions) == sorted(out["qbar"] for out in handoff.values())
        return json.loads((staging / "resources.json").read_text())["cpu_seconds"]

    assert run(context) == {"invocation-1": 6.0, "invocation-2": 3.0, "invocation-3": 0.75}
    assert run(context) == {"invocation-1": 6.0, "invocation-2": 3.0, "invocation-3": 1.5}
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        fresh = _kernel("start_invocation")(staging, authority, plan, "invocation-4")
    assert run(fresh) == {"invocation-1": 6.0, "invocation-2": 3.0, "invocation-3": 1.5, "invocation-4": 0.75}
    after, residual = _tree(staging), sorted(out["setup_id"] for out in handoff.values())
    assert len(checks) == 9 and checks[:3] == checks[3:6] == checks[6:] and state["cpu"] == start + 2.25
    assert sorted(ids["RESIDUAL"] for ids in checks[:3]) == residual and set(after) == set(before)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


B2U_UNMASKED = ("integrity_not_masked", "reduction_error_not_masked")


@pytest.mark.parametrize("case", B2U_UNMASKED)
def test_dev_library_cache_keeps_integrity_and_reducer_errors_unmasked_past_the_cap(tmp_path, monkeypatch, case):
    import json
    integrity, bumped, sentinel = case == "integrity_not_masked", [], OSError("reduction failed after its cost")
    fixture, state, record, context, _, cap = _b2u_budgeted(tmp_path, monkeypatch, not integrity)
    _, desc, _, plan, staging = fixture
    did, upstream, verify = record["design_id"], {"SETUP": record["phase_digest"]}, _kernel("_verify_partition")
    batch, gaussian = (["DEV_LIB", "FULL", *setup, DEV_FAMILIES[0]] for setup in (B2O_SETUPS[2], B2O_SETUPS[1]))
    poison = _b2u_q(batch[2:5], batch[5]).astype(np.float32)

    def first_read(real):
        def measured(*args):
            arrays = real(*args)
            if args[3] == batch and not bumped:
                bumped.append(args[3])
                state["cpu"] += cap + 1.0
            return arrays
        return measured

    def failing(real):
        def measured(*args):
            real(*args)
            bumped.append("qbar")
            state["cpu"] += cap + 1.0
            raise sentinel
        return measured

    if integrity:
        _kernel("partition")(staging, "DEV", upstream, batch, lambda: {"q": poison})
        sha, n_rows, arrays = verify(staging, did, upstream, batch)
        pending = [entry["key"] for entry in _kernel("_planned_progress")(staging, did, desc, plan, None)[1]]
        assert _same_arrays(arrays, {"q": poison}) and [n_rows, len(sha), poison.shape] == [2, 64, (2, 20)]
        assert np.isfinite(poison).all() and (poison >= 0).all() and pending == [k for k in plan["DEV"] if k != batch]
        assert plan["DEV"].index(gaussian) < plan["DEV"].index(batch)
    fake = ("_verify_partition", first_read) if integrity else ("dev_qbar", failing)
    error = pdb.PartitionMismatch if integrity else OSError
    raised, calls, reductions, added, after = _b2u_resource(monkeypatch, state, fixture, context, False, [fake], error)
    assert added == [] and calls == [] and len(reductions) == int(not integrity)
    assert bumped == [batch if integrity else "qbar"] and (integrity or raised is sentinel)
    assert json.loads(after["resources.json"])["cpu_seconds"][context["token"]] == cap + 1.0


def _b2u_coordinates(root, monkeypatch, mode, applications):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(setup) for setup in B2O_COORDINATES]),
                        (("scope", "applications"), applications), (("parameters", "T_fit"), 48),
                        (("dev", "n_lib"), 2), (("modes", mode, "sizes", "DEV_LIB"), 2)):
        cfg = _edited(cfg, path, value)
    if mode == "full":
        cfg = _authorized(root, monkeypatch, cfg, mode)[0]
    else:
        monkeypatch.setattr(pio(), "REPO_ROOT", root)
    desc, primitive = _kernel("design_descriptor")(cfg, mode), _kernel("seed_plan")(cfg, mode)["keys"]
    plan = {phase: [] for phase in _kernel("PHASES")}
    plan["SETUP"] = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    logical = [["DEV_LIB", desc["campaign"], *s, f] for s in desc["scope"]["setups"] for f in DEV_FAMILIES]
    plan["DEV"] = sorted(logical, key=pdb.canon) if "RESIDUAL" in applications else []
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")(mode, cfg, desc, 1), plan, staging


def _b2u_coord_setup(monkeypatch, state, fixture, mode):
    cfg, desc, authority, plan, staging = fixture
    arrays = {pdb.canon(k): _b2o_coord_frame(k[2]) if k[0] == "frame" else _b2o_coord_fit(*k[2:]) for k in plan["SETUP"]}
    frozen, kept = _b2p_frozen(*arrays.values())
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in plan["SETUP"]:
        _b2o_cache(staging, key, arrays[pdb.canon(key)])
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2p_traps(mp)
        record = _kernel("setup_phase")(cfg, mode, context)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
    metas, did = record["derived"]["setups"], record["design_id"]
    fitted = {pdb.canon(s): pdb.array_sha256(*_b2o_coord_fit(*s).values()) for s in B2O_COORDINATES if s[0] != "EXACT"}
    pending = [{"phase": "DEV", "key": key} for key in plan["DEV"]]
    assert [row["key"] for row in record["partitions"]] == plan["SETUP"] and len(plan["SETUP"]) == 5
    assert {name: meta["fit_hash"] for name, meta in metas.items() if meta["fit_hash"]} == fitted and len(metas) == 5
    assert all(sorted(meta["applications"]) == sorted(desc["scope"]["applications"]) for meta in metas.values())
    assert metas[pdb.canon(["FITTED_LW_T7", 26, 0])]["information_basis"] == "GAUSSIAN_PROXY"
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({"SETUP": record}, pending)
    assert [a.tobytes() for a in frozen] == kept and context["token"] == "invocation-2"
    return record, context, arrays


@pytest.mark.parametrize("mode", ["full", "smoke"])
def test_dev_library_cache_runs_the_real_block_on_five_coordinates_in_full_and_smoke(tmp_path, monkeypatch, mode):
    import json
    module, state, drawn, blocks, infos = pio(), {"cpu": 10.0, "wall": 100.0}, [], [], []
    fixture = _b2u_coordinates(tmp_path, monkeypatch, mode, ["RESIDUAL", "MARKET"])
    cfg, desc, authority, plan, staging = fixture
    record, context, arrays = _b2u_coord_setup(monkeypatch, state, fixture, mode)
    did, upstream, campaign = record["design_id"], {"SETUP": record["phase_digest"]}, desc["campaign"]
    istar, planned = desc["science"]["parameters"]["I_star"], set(_kernel("seed_plan")(cfg, mode)["keys"])
    keys = [("devlib", campaign, *k[2:5], k[5], i) for k in plan["DEV"] for i in (0, 1)]
    rows, golds, go = {key: _b2d_draws(key[5])[key[6]:key[6] + 1] for key in keys}, {}, tmp_path / "prompts"
    raw, kept = _b2p_frozen(*rows.values())
    setup_bytes = [a.tobytes() for fixed in arrays.values() for a in fixed.values()]
    for key, row in rows.items():
        frame = arrays[pdb.canon(["frame", campaign, key[3]])]
        fit = frame if key[2] == "EXACT" else arrays[pdb.canon(["fit", campaign, *key[2:5]])]
        b = np.array(_b2d_coordinates(B2D_FAMILIES[key[5]][1], list(range(2, 22)), row[0].tolist(), istar, key[3]))
        delta = frame["V"] @ (np.sqrt(frame["lam"]) * b)
        golds.setdefault(key[:6], []).append(0.5 * (delta @ fit["V"][:, 1:21]) ** 2 / fit["lam"][1:21])
    snapshot = [pdb.canon(cfg), pdb.canon(desc), pdb.canon(authority), _kernel("seed_plan")(cfg, mode)["sha256"]]
    assert len(plan["DEV"]) == 20 and len(keys) == 40 and set(keys) <= planned
    assert not any((*key[:6], 2) in planned for key in keys) and desc["sizes"]["DEV_LIB"] == 2
    assert desc["science"]["dev"]["n_lib"] == 2 and go.exists() == (mode == "full")
    assert (authority["go_reference"] is None) == (mode == "smoke") and authority["design_id"] == did
    assert all(g.shape == (20,) and np.isfinite(g).all() and (g >= 0).all() for q in golds.values() for g in q)
    assert all(not np.allclose(*golds[("devlib", campaign, *s, DEV_FAMILIES[0])]) for s in desc["scope"]["setups"])
    real_block, real_info, before = module.dev_library_block, module.direction_information, _tree(staging)

    def block(given, frame, fit, setup, family):
        blocks.append((pdb.canon(setup), family))
        state["cpu"] += 0.25
        return real_block(given, frame, fit, setup, family)

    def information(given, frame, fit, setup, application, key):
        want = arrays[pdb.canon(["frame", campaign, setup[1]])]
        assert application == "RESIDUAL" and _same_arrays(frame, want)
        assert _same_arrays(fit, want if setup[0] == "EXACT" else arrays[pdb.canon(["fit", campaign, *setup])])
        infos.append(key)
        return real_info(given, frame, fit, setup, application, key)

    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        _b2p_traps(mp)
        _b2s_forbid(mp, "setup_phase")
        _b2p_draw_stub(mp, desc, rows, drawn)
        mp.setattr(module, "dev_library_block", block)
        mp.setattr(module, "direction_information", information)
        result = _kernel("dev_library_cache")(cfg, mode, context)
    after = _tree(staging)
    stems = {_partition_stem(staging, did, upstream, key).name for key in plan["DEV"]}
    assert drawn == keys and infos == keys and [a.tobytes() for a in raw] == kept
    assert blocks == [(pdb.canon(k[2:5]), k[5]) for k in plan["DEV"]] and set(result) == set(record["derived"]["setups"])
    assert set(after) == set(before) | {f"partitions/{s}.{e}" for s in stems for e in ("npz", "json")} and len(stems) == 20
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    for key in plan["DEV"]:
        sha, n_rows, got = _kernel("_verify_partition")(staging, did, upstream, key)
        assert set(got) == {"q"} and got["q"].dtype == np.float64 and got["q"].shape == (2, 20) and n_rows == 2
        np.testing.assert_allclose(got["q"], np.array(golds[("devlib", campaign, *key[2:])]), rtol=1e-12, atol=1e-15)
    for setup in desc["scope"]["setups"]:
        setup_id, parts, library_id = _b2u_expected(staging, record, plan, setup)
        pools = [golds[("devlib", campaign, *setup, family)] for family in DEV_FAMILIES]
        qbar = [math.fsum(math.fsum(q[k] for q in pool) / 2 for pool in pools) / 4 for k in range(20)]
        out = result[pdb.canon(setup)]
        assert set(out) == {"setup_id", "partitions", "qbar", "qbar_sha", "dev_library_id"}
        assert [out["setup_id"], out["partitions"], out["dev_library_id"]] == [setup_id, parts, library_id]
        assert out["qbar"] == pytest.approx(qbar, rel=1e-12)
        assert out["qbar_sha"] == pdb.array_sha256(np.array(out["qbar"], dtype=np.float64))
    assert json.loads(after["resources.json"])["cpu_seconds"] == {"invocation-1": 0.0, "invocation-2": 5.0}
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    reloaded = _tree(staging)
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        _b2p_traps(mp)
        _b2s_forbid(mp, "setup_phase", "dev_library_block", "direction_information", "direction_draws",
                    "population_drift", "projection_diagnostics")
        again = _kernel("dev_library_cache")(cfg, mode, renewed)
    final = _tree(staging)
    spent = {"invocation-1": 0.0, "invocation-2": 5.0, "invocation-3": 0.0}
    assert again == result and set(final) == set(reloaded) and not (staging / "phases" / "DEV.json").exists()
    assert all(final[name] == data for name, data in reloaded.items() if name != "resources.json")
    assert json.loads(final["resources.json"])["cpu_seconds"] == spent and [a.tobytes() for a in raw] == kept
    assert [a.tobytes() for fixed in arrays.values() for a in fixed.values()] == setup_bytes
    assert snapshot == [pdb.canon(cfg), pdb.canon(desc), pdb.canon(authority), _kernel("seed_plan")(cfg, mode)["sha256"]]
    assert all(name.startswith(("logs/", "prompts/")) for name in _tree(tmp_path))


def test_dev_library_cache_returns_an_empty_library_for_a_market_only_scope(tmp_path, monkeypatch):
    import json
    state, fixture = {"cpu": 10.0, "wall": 100.0}, _b2u_coordinates(tmp_path, monkeypatch, "full", ["MARKET"])
    cfg, desc, authority, plan, staging = fixture
    record, context, _ = _b2u_coord_setup(monkeypatch, state, fixture, "full")
    forbidden = ("setup_phase", "dev_library_block", "direction_draws", "direction_information", "dev_qbar")
    cache, before, inputs = _kernel("dev_library_cache"), _tree(staging), pdb.canon([cfg, desc, authority, plan])
    assert plan["DEV"] == [] and desc["scope"]["applications"] == ["MARKET"] and len(record["derived"]["setups"]) == 5
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2o_forbid(mp)
        _b2p_traps(mp)
        _b2s_forbid(mp, *forbidden)
        first = cache(cfg, "full", context)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
        again = cache(cfg, "full", renewed)
    after, did = _tree(staging), record["design_id"]
    assert first == {} == again and set(after) == set(before) and pdb.canon([cfg, desc, authority, plan]) == inputs
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    spent = {"invocation-1": 0.0, "invocation-2": 0.0, "invocation-3": 0.0}
    assert json.loads(after["resources.json"])["cpu_seconds"] == spent and "phases/DEV.json" not in after
    assert _kernel("_planned_progress")(staging, did, desc, plan, None) == ({"SETUP": record}, [])


B2V_SIZES = {"DEV_LIB": 1, "DEV_NULL": 19, "DEV_ALT": 2, "CAL_NULL": 4, "HOLD_NULL": 1, "ALT": 1}
B2V_MULTS = (1, 4, 16, 64)
B2V_ONLINE = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128")
B2V_POLICIES = (("ONLINE", "INFO"), ("ONLINE", "PREFIX"), ("STATIC", 20))
B2V_ROWS = {1: (1, 1), 3: (2, 4), 4: (4, 4), 5: (5, 5), 6: (-1, 6)}
B2V_D = {1: (6, 6, 1, 1), 2: (5, 5, 5, 5), 4: (3, 3, 3, 3), 8: (4, 4, 4, 4), 16: (4, 4, 4, 4), 20: (6, 6, 1, 1)}
B2V_S2 = {1: ((6, 6, 1, 1), (6, 6, 6, 6)), 4: ((4, 4, 4, 4), (1, 1, 1, 1)), 16: ((4, 4, 4, 4), (4, 4, 4, 4)),
          64: ((5, 5, 5, 5), (5, 5, 5, 5))}
B2V_FIELDS = {"d_dev", "s2_dev", "qualification", "d_candidates", "s2_candidates"}
B2V_TRAPPED = ("oracle_masks", "oracle_scan", "population_frame", "null_returns", "exact_scores", "path_scores",
               "direction_draws", "direction_information", "dev_qbar", "fit_record", "open_staging", "partition",
               "phase_record", "_write_atomic", "design_id")
B2V_NOGRID = {key: value for key, value in _design_cfg()["dev"].items() if key != "s2_grid"}
B2V_INVALID = {
    "missing_family": ("alts", lambda Ys: {f: Ys[f] for f in DEV_FAMILIES[:3]}),
    "evaluation_families_only": ("alts", lambda Ys: {f: Ys[f] for f in DEV_FAMILIES[2:]}),
    "extra_family": ("alts", lambda Ys: {**Ys, "F3_MARKET": Ys[DEV_FAMILIES[0]]}),
    "not_a_mapping": ("alts", lambda Ys: list(Ys.values())),
    "unbalanced_family": ("family", np.zeros((3, 4, 20))),
    "empty_family": ("family", np.zeros((0, 4, 20))),
    "wrong_h_family": ("family", np.zeros((2, 3, 20))),
    "wrong_k_family": ("family", np.zeros((2, 4, 19))),
    "nonfinite_family": ("family", np.full((2, 4, 20), np.nan)),
    "empty_null": ("null", np.zeros((0, 4, 20))),
    "null_rows_not_dev_null": ("null", np.zeros((20, 4, 20))),
    "wrong_h_null": ("null", np.zeros((19, 5, 20))),
    "wrong_k_null": ("null", np.zeros((19, 4, 21))),
    "complex_null": ("null", np.zeros((19, 4, 20), dtype=complex)),
    "infinite_null": ("null", np.full((19, 4, 20), np.inf)),
    "d_grid_scalar": ("desc", (("dev", "d_grid"), 4)),
    "d_grid_empty": ("desc", (("dev", "d_grid"), [])),
    "d_grid_duplicate": ("desc", (("dev", "d_grid"), [1, 2, 2, 4])),
    "d_grid_bool": ("desc", (("dev", "d_grid"), [True, 2, 4])),
    "d_grid_float": ("desc", (("dev", "d_grid"), [1, 2.0, 4])),
    "d_grid_zero": ("desc", (("dev", "d_grid"), [0, 1, 2])),
    "d_grid_above_k": ("desc", (("dev", "d_grid"), [1, 2, 21])),
    "primary_int": ("primary", 1),
    "primary_none": ("primary", None),
    "primary_numpy_bool": ("primary", np.True_),
    "s2_grid_missing": ("desc", (("dev",), B2V_NOGRID)),
    "s2_grid_empty": ("desc", (("dev", "s2_grid"), [])),
    "s2_grid_duplicate": ("desc", (("dev", "s2_grid"), [1, 4, 4, 16])),
    "s2_grid_zero": ("desc", (("dev", "s2_grid"), [0, 1, 4])),
    "s2_grid_negative": ("desc", (("dev", "s2_grid"), [-1, 4])),
    "s2_grid_float": ("desc", (("dev", "s2_grid"), [1, 4.0, 16])),
    "s2_grid_bool": ("desc", (("dev", "s2_grid"), [True, 4])),
    "alpha_one": ("desc", (("parameters", "alpha"), 1.0)),
}


def _b2v_desc(H, *edits):
    return _b2q_desc((("parameters", "H"), H), (("modes", "full", "sizes"), B2V_SIZES), *edits)


def _b2v_inputs(H, marked):
    Y0, Ys = np.zeros((19, H, 20)), {family: np.zeros((2, H, 20)) for family in DEV_FAMILIES}
    if marked:
        Y0[:, 0, 1] = np.arange(19)
        for j, family in enumerate(DEV_FAMILIES):
            Ys[family][:, 0, 0], Ys[family][:, 0, 1] = j + 1, np.arange(2)
    return Y0, Ys


def _b2v_level(key):
    kind, axis, mult = key
    return 1 + axis / 32 + mult / 2 if kind == "STATIC" else 3 + mult / 2 + (axis == "PREFIX") / 4


def _b2v_rmst(key):
    kind, axis, mult = key
    if kind == "ONLINE":
        return B2V_S2[mult][1]
    return B2V_D[axis] if mult == 1 else B2V_S2[mult][0] if axis == 20 else None


def _b2v_entry(key):
    rmst = {family: float(v) for family, v in zip(DEV_FAMILIES, _b2v_rmst(key))}
    return {"h": float(np.nextafter(_b2v_level(key), np.inf)), "r": 0, "alarms": 0, "rmst_by_family": rmst}


def _b2v_traps(mp, *names):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("scan, calibration, oracle, draw, fit, I/O, phase or identity work inside dev_choices")

    owners = [(module, name) for name in (*B2V_TRAPPED, *names)]
    owners += [(np.random, "default_rng"), (np.random, "SeedSequence"), (np.random, "seed"), (pdb, "fit_basis"),
               (pdb, "scan_statistic"), (pdb, "sha16"), (pdb.sim, "t_innov")]
    for owner, name in owners:
        mp.setattr(owner, name, forbidden)
    return forbidden


def _b2v_spy(mp, calls):
    real = pdb.rank_threshold

    def rank_threshold(maxima, alpha, rule):
        calls.append((np.array(maxima, dtype=np.float64), alpha, rule))
        return real(maxima, alpha, rule)

    mp.setattr(pdb, "rank_threshold", rank_threshold)


def _b2v_stub(prior, mix, calls):
    def nonoracle_scan(Y, bundle, h=None):
        Y, policy, s2 = np.asarray(Y), bundle["policy"], bundle["s2"]
        mult = [m for m in B2V_MULTS if s2 == m * prior]
        assert bundle["application"] == "RESIDUAL" and bundle["status"] == "RUNNABLE" and len(mult) == 1
        if policy["kind"] == "STATIC":
            d = int(policy["mask"].sum())
            assert np.array_equal(policy["mask"], np.arange(20) < d)
            key = ("STATIC", d, mult[0])
        else:
            assert policy["window"] == 128 and policy["order"] in ("INFO", "PREFIX")
            assert np.array_equal(policy["cost"], mix)
            key = ("ONLINE", policy["order"], mult[0])
        level, rmst, t = _b2v_level(key), _b2v_rmst(key), np.arange(1, Y.shape[1] + 1)
        assert rmst is not None and Y.shape[2] == 20
        W = np.empty(Y.shape[:2])
        for b, row in enumerate(Y):
            code, i = int(row[0, 0]), int(row[0, 1])
            if code == 0:
                W[b] = level - (18 - i) / 64
            else:
                T = B2V_ROWS[rmst[code - 1]][i]
                W[b] = np.where((T > 0) & (t >= T), np.nextafter(level, np.inf), level)
        hit = np.zeros(W.shape, dtype=bool) if h is None else W >= h
        calls.append(key)
        return {"W": W, "first": np.where(hit.any(axis=1), hit.argmax(axis=1) + 1, -1),
                "mask_bits": np.zeros(W.shape, dtype=np.uint32)}

    return nonoracle_scan


def _b2v_shape(out):
    import json
    assert set(out) == B2V_FIELDS and out["qualification"] == "COMMON_NOMINAL_ALPHA_DEV"
    assert all(set(c) == {"d", "s2", "h", "r", "alarms", "rmst_by_family", "J"} for c in out["d_candidates"])
    assert all(set(c) == {"s2", "policies", "J"} and set(c["policies"]) == {*B2V_ONLINE, "FULL_K"}
               and all(set(p) == {"h", "r", "alarms", "rmst_by_family"} for p in c["policies"].values())
               for c in out["s2_candidates"])
    rows = out["d_candidates"] + [p for c in out["s2_candidates"] for p in c["policies"].values()]
    ints = [out["d_dev"], *(c["d"] for c in out["d_candidates"]), *(row[k] for row in rows for k in ("r", "alarms"))]
    floats = [c[k] for c in out["d_candidates"] + out["s2_candidates"] for k in ("s2", "J")] + [row["h"] for row in rows]
    floats += [v for row in rows for v in row["rmst_by_family"].values()]
    floats += [] if out["s2_dev"] is None else [out["s2_dev"]]
    assert all(type(v) is int for v in ints) and all(type(v) is float for v in floats)
    assert all(set(row["rmst_by_family"]) == set(DEV_FAMILIES) for row in rows)
    assert json.loads(json.dumps(out, allow_nan=False)) == out


def test_dev_choices_selects_d4_and_s2_times_4_from_controlled_scans_and_real_rank_calibration(monkeypatch):
    jd = {d: sum(v) / 4 for d, v in B2V_D.items()}
    js = {m: (sum(full) + 2 * sum(online)) / 12 for m, (full, online) in B2V_S2.items()}
    assert min(jd, key=lambda d: (jd[d], d)) == 4 and min(B2V_D, key=lambda d: (sum(B2V_D[d][2:]), d)) == 1
    assert min(js, key=lambda m: (js[m], m)) == 4 and min(B2V_S2, key=lambda m: (sum(B2V_S2[m][0]), m)) == 1
    assert B2V_D[20] == B2V_S2[1][0] and js[1] == pytest.approx(31 / 6, rel=1e-15)
    assert (jd[1], jd[4], jd[20], js[4]) == (3.5, 3, 3.5, 2)
    desc = _b2v_desc(6)
    reverse = _b2v_desc(6, (("dev", "d_grid"), [20, 16, 8, 4, 2, 1]), (("dev", "s2_grid"), [64, 16, 4, 1]))
    prior, choose = _kernel("common_prior")(desc), _kernel("dev_choices")
    mix = _kernel("cost_vectors")(504, 20)["MIX"]
    keys = [("STATIC", d, 1) for d in B2V_D] + [(kind, axis, m) for m in B2V_MULTS for kind, axis in B2V_POLICIES]
    want_d = [{"d": d, "s2": prior, **_b2v_entry(("STATIC", d, 1))} for d in B2V_D]
    want_s = [{"s2": m * prior, "policies": {label: _b2v_entry((kind, axis, m)) for label, (kind, axis)
                                             in zip((*B2V_ONLINE, "FULL_K"), B2V_POLICIES)}} for m in B2V_MULTS]
    Y0, Ys = _b2v_inputs(6, True)
    arrays, kept = _b2p_frozen(Y0, Ys)
    snapshot, outs = [pdb.canon(desc), pdb.canon(reverse)], []
    for given in (desc, reverse):
        scans, cal = [], []
        with monkeypatch.context() as mp:
            _b2v_traps(mp, "masked_scan", "online_masks", "nonoracle_masks")
            _b2v_spy(mp, cal)
            mp.setattr(pio(), "nonoracle_scan", _b2v_stub(prior, mix, scans))
            out = choose(given, Y0, Ys, primary=True)
        _b2v_shape(out)
        assert set(scans) == set(keys) and len(cal) == 18 and all(c[1:] == (0.05, "GE") for c in cal)
        assert all(np.array_equal(np.sort(c[0]), c[0].max() - np.arange(18, -1, -1) / 64) for c in cal)
        assert sorted(c[0].max() for c in cal) == sorted(_b2v_level(key) for key in keys)
        assert [{k: v for k, v in c.items() if k != "J"} for c in out["d_candidates"]] == want_d
        assert [{k: v for k, v in c.items() if k != "J"} for c in out["s2_candidates"]] == want_s
        assert [c["J"] for c in out["d_candidates"]] == pytest.approx(list(jd.values()), rel=1e-12)
        assert [c["J"] for c in out["s2_candidates"]] == pytest.approx(list(js.values()), rel=1e-12)
        full = out["s2_candidates"][0]["policies"]["FULL_K"]
        assert {k: out["d_candidates"][-1][k] for k in full} == full
        assert (out["d_dev"], out["s2_dev"]) == (4, 4 * prior)
        outs.append(out)
    assert outs[0] == outs[1] and [a.tobytes() for a in arrays] == kept
    assert snapshot == [pdb.canon(desc), pdb.canon(reverse)]


def test_dev_choices_real_zero_scores_censor_every_candidate_and_ties_pick_d1_and_the_common_prior(monkeypatch):
    desc, choose = _b2v_desc(4), _kernel("dev_choices")
    prior, before = _kernel("common_prior")(desc), pdb.canon(desc)
    nogrid = _b2v_desc(4, (("dev",), B2V_NOGRID))
    irrelevant = _b2v_desc(4, (("dev", "s2_grid"), "IRRELEVANT"))
    Y0, Ys = _b2v_inputs(4, False)
    arrays, kept = _b2p_frozen(Y0, Ys)
    cal = []
    with monkeypatch.context() as mp:
        _b2v_traps(mp)
        _b2v_spy(mp, cal)
        out = choose(desc, Y0, Ys, primary=True)
    _b2v_shape(out)
    rows = [(c["d"], prior, c) for c in out["d_candidates"]]
    rows += [(1 if label in B2V_ONLINE else 20, c["s2"], p)
             for c in out["s2_candidates"] for label, p in c["policies"].items()]
    assert [c["d"] for c in out["d_candidates"]] == [1, 2, 4, 8, 16, 20] and len(rows) == len(cal) == 18
    assert [c["s2"] for c in out["s2_candidates"]] == [m * prior for m in B2V_MULTS]
    assert all(c[1:] == (0.05, "GE") and np.ptp(c[0]) == 0 for c in cal)
    for d, s2, row in rows:
        w = -d / 2 * np.log1p(s2)
        assert row["rmst_by_family"] == dict.fromkeys(DEV_FAMILIES, 4.0) and (row["r"], row["alarms"]) == (0, 0)
        assert row["h"] == pytest.approx(w, rel=1e-12) and (d > 1 or row["h"] == float(np.nextafter(w, np.inf)))
    assert all(c["J"] == 4.0 for c in out["d_candidates"] + out["s2_candidates"])
    assert (out["d_dev"], out["s2_dev"]) == (1, prior)
    for given in (desc, nogrid, irrelevant):
        cal = []
        with monkeypatch.context() as mp:
            _b2v_traps(mp)
            _b2v_spy(mp, cal)
            plain, default = choose(given, Y0, Ys, primary=False), choose(given, Y0, Ys)
        _b2v_shape(plain)
        assert plain == default and len(cal) == 12 and plain["d_candidates"] == out["d_candidates"]
        assert (plain["d_dev"], plain["s2_dev"], plain["s2_candidates"]) == (1, None, [])
    assert [a.tobytes() for a in arrays] == kept and pdb.canon(desc) == before


@pytest.mark.parametrize("case", B2V_INVALID)
def test_dev_choices_refuses_a_malformed_input_before_any_scan_or_calibration(monkeypatch, case):
    target, value = B2V_INVALID[case]
    desc, choose = _b2v_desc(4), _kernel("dev_choices")
    Y0, Ys = _b2v_inputs(4, False)
    with monkeypatch.context() as mp:
        _b2v_traps(mp)
        assert choose(desc, Y0, Ys, primary=True)["d_dev"] == 1
    given = _b2v_desc(4, value) if target == "desc" else desc
    null = value if target == "null" else Y0
    alts = value(Ys) if target == "alts" else {**Ys, DEV_FAMILIES[3]: value} if target == "family" else Ys
    primary = value if target == "primary" else True
    with monkeypatch.context() as mp:
        forbidden = _b2v_traps(mp, "nonoracle_scan", "masked_scan", "online_masks", "nonoracle_masks")
        mp.setattr(pdb, "rank_threshold", forbidden)
        with pytest.raises(ValueError) as caught:
            choose(given, null, alts, primary=primary)
    assert not isinstance(caught.value, pdb.CalibrationFailed)


def test_dev_choices_propagates_the_real_insufficient_calibration_of_an_exact_sized_short_dev_null(monkeypatch):
    short = _b2v_desc(4, (("modes", "full", "sizes"), {**B2V_SIZES, "DEV_NULL": 18}))
    Y0, Ys, cal = np.zeros((18, 4, 20)), _b2v_inputs(4, False)[1], []
    choose = _kernel("dev_choices")
    with monkeypatch.context() as mp:
        _b2v_traps(mp)
        _b2v_spy(mp, cal)
        with pytest.raises(pdb.InsufficientCalibration):
            choose(short, Y0, Ys, primary=True)
    assert pdb.min_calibration_n(0.05) == 19 and [c[0].shape for c in cal] == [(18,)]


B2W_SETUPS = (["EXACT", 24, 0], ["FITTED_LW_GAUSSIAN", 24, 0])
B2W_POLICIES = ["FULL_K", "CPV90", "FIXED_DEV_PREFIX", "FIXED_EXANTE_QBAR_MIX", "ONLINE_INFO_MIX_W128", "ORACLE_INFO_MIX"]
B2W_PCONF = (*B2V_ONLINE, "FULL_K")
B2W_PRIOR = "ISOTROPIC_ZERO_MEAN_GAUSSIAN"
B2W_FAULTS = ("missing_null_key", "foreign_family_key", "stale_authority", "setup_missing", "short_later_null",
              "narrow_later_alt", "extra_null_array")
B2W_RULE_REFUSALS = {
    "int_flag": ("ONLINE_INFO_MIX_W128", {"s2_sensitivity": 1}, ()),
    "none_flag": ("FULL_K", {"s2_sensitivity": None}, ()),
    "numpy_flag": ("FULL_K", {"s2_sensitivity": np.True_}, ()),
    "dev_prefix": ("FIXED_DEV_PREFIX", {"s2_sensitivity": True}, ()),
    "exante": ("FIXED_EXANTE_QBAR_MIX", {"s2_sensitivity": True}, ()),
    "oracle": ("ORACLE_INFO_MIX", {"s2_sensitivity": True}, ()),
    "aff_cost": ("ONLINE_INFO_AFF_W128", {"s2_sensitivity": True}, ()),
    "window_32": ("ONLINE_PREFIX_MIX_W32", {"s2_sensitivity": True}, ()),
    "combined_online": ("ONLINE_PREFIX_MIX_W128", {"s2_sensitivity": True, "gamma_sensitivity": True}, ()),
    "combined_full": ("FULL_K", {"s2_sensitivity": True, "gamma_sensitivity": True}, ()),
    "grid_missing": ("FULL_K", {"s2_sensitivity": True}, ((("dev",), B2V_NOGRID),)),
    "grid_duplicate": ("ONLINE_INFO_MIX_W128", {"s2_sensitivity": True}, ((("dev", "s2_grid"), [1, 4, 4]),)),
    "grid_float": ("ONLINE_INFO_MIX_W128", {"s2_sensitivity": True}, ((("dev", "s2_grid"), [1, 4.0]),)),
}


def _b2w_sha16(value):
    return _b2s_reference(value)[1]


def _b2w_no_recompute(mp, *names):
    def forbidden(*args, **kwargs):
        raise AssertionError("DEV producer, qbar, choice, scan or calibration rerun on a committed DEV record")

    _b2s_forbid(mp, *names)
    mp.setattr(pdb, "rank_threshold", forbidden)


def _b2w_fixture(root, monkeypatch, mode="full", applications=("RESIDUAL", "MARKET")):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(s) for s in B2W_SETUPS]),
                        (("scope", "applications"), list(applications)), (("scope", "policies"), B2W_POLICIES),
                        (("parameters", "T_fit"), 48), (("parameters", "H"), 6),
                        (("parameters", "gamma_M_sensitivity"), 6 / 0.05), (("dev", "n_lib"), 2),
                        (("modes", mode, "sizes"), {**B2V_SIZES, "DEV_LIB": 2}), (("phi", "setup"), list(B2W_SETUPS[1]))):
        cfg = _edited(cfg, path, value)
    if mode == "full":
        cfg = _authorized(root, monkeypatch, cfg, mode)[0]
    else:
        monkeypatch.setattr(pio(), "REPO_ROOT", root)
    desc, primitive = _kernel("design_descriptor")(cfg, mode), _kernel("seed_plan")(cfg, mode)["keys"]
    plan, roles = {phase: [] for phase in _kernel("PHASES")}, [("DEV_NULL", [])]
    roles += [(role, [family]) for role in ("DEV_LIB", "DEV_ALT") for family in DEV_FAMILIES]
    plan["SETUP"] = sorted(([*key] for key in primitive if key[0] in ("frame", "fit")), key=pdb.canon)
    if "RESIDUAL" in applications:
        plan["DEV"] = sorted(([role, desc["campaign"], *s, *tail] for s in B2W_SETUPS for role, tail in roles),
                             key=pdb.canon)
    staging = _kernel("open_staging")(root / "logs", desc, False)
    return cfg, desc, _kernel("authorize")(mode, cfg, desc, 1), plan, staging


def _b2w_setup(monkeypatch, state, fixture):
    cfg, desc, authority, plan, staging = fixture
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    for key in plan["SETUP"]:
        _b2o_cache(staging, key, _b2o_coord_frame(key[2]) if key[0] == "frame" else _b2o_coord_fit(*key[2:]))
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        _no_draws_or_workers(mp)
        _b2p_traps(mp)
        record = _kernel("setup_phase")(cfg, desc["mode"], context)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-2")
    assert sorted(record["derived"]["setups"]) == sorted(pdb.canon(s) for s in B2W_SETUPS)
    return record, context


def _b2w_noise(key, width):
    assert type(key) is tuple and key[0] == "path" and key[5] in ("DEV_NULL", "DEV_ALT")
    return (np.arange(6.0)[:, None] - np.arange(width)) / 32 + key[6] / 4 + (key[5] == "DEV_ALT") / 2


def _b2w_scores(desc, key, scores):
    if scores != "bridge":
        Y0, Ys = _b2v_inputs(6, scores == "controlled")
        return Y0 if key[0] == "DEV_NULL" else Ys[key[5]]
    setup, frame, out = key[2:5], _b2o_coord_frame(24), []
    fit = frame if setup[0] == "EXACT" else _b2o_coord_fit(*setup)
    W = fit["V"][:, 1:21] / np.sqrt(fit["lam"][1:21])
    for i in range(19 if key[0] == "DEV_NULL" else 2):
        path, delta = ("path", desc["campaign"], *setup, key[0], i), np.zeros(24)
        if key[0] == "DEV_ALT":
            row, istar = _b2d_draws(key[5])[i].tolist(), desc["science"]["parameters"]["I_star"]
            b = np.array(_b2d_coordinates(B2D_FAMILIES[key[5]][1], list(range(2, 22)), row, istar, 24))
            delta = frame["V"] @ (np.sqrt(frame["lam"]) * b)
        if setup[0] == "EXACT":
            out.append(_b2w_noise(path, 21)[:, 1:21] + delta @ W)
        else:
            out.append((_b2w_noise(path, 24) + delta - fit["mean"]) @ W)
    return np.array(out)


def _b2w_producers(mp, state, calls, scores, prior, fail=None):
    module = pio()
    real_path, real_info, mix = module.path_scores, module.direction_information, module.cost_vectors(504, 20)["MIX"]
    _b1m_clock(mp, state)
    _no_draws_or_workers(mp)
    _b2o_forbid(mp)
    _b2s_forbid(mp, "setup_phase")

    def block(desc, frame, fit, setup, family):
        calls.append(("DEV_LIB", *setup, family))
        state["cpu"] += 0.25
        return {"q": _b2u_q(setup, family)}

    def information(desc, frame, fit, setup, application, key):
        assert application == "RESIDUAL" and key[:1] == ("meta",) and key[5] == "DEV_ALT" and list(key[2:5]) == setup
        calls.append(key)
        if scores == "bridge":
            return real_info(desc, frame, fit, setup, application, key)
        return {"status": "SUPPORTED", "family": key[6], "support": None, "q": np.zeros(20), "I_joint": 0.0,
                "delta": np.full(key[3], 1.0 + DEV_FAMILIES.index(key[6])), "oracle_basis": "EXACT_ADDITIVE_KL"}

    def path(desc, frame, fit, application, key, delta=None):
        assert application == "RESIDUAL" and key[:1] == ("path",) and key[5] in ("DEV_NULL", "DEV_ALT")
        calls.append((*key, None if delta is None else float(delta[0])))
        if fail is not None and calls[-1] == fail[0]:
            raise fail[1]
        if scores == "bridge":
            return real_path(desc, frame, fit, application, key, delta)
        Y = np.zeros((6, 20))
        if scores == "controlled":
            Y[0, 0], Y[0, 1] = 0.0 if delta is None else delta[0], key[6]
        return Y

    if scores == "bridge":
        mp.setattr(module, "exact_scores", lambda desc, key: _b2w_noise(key, 21))
        mp.setattr(module, "null_returns", lambda desc, frame, key: _b2w_noise(key, frame["lam"].size))
        mp.setattr(module, "direction_draws", lambda desc, key: _b2d_draws(key[6])[key[7]:key[7] + 1])
    elif scores == "controlled":
        mp.setattr(module, "nonoracle_scan", _b2v_stub(prior, mix, []))
    for name, fake in (("dev_library_block", block), ("direction_information", information), ("path_scores", path)):
        mp.setattr(module, name, fake)


def _b2w_expected(desc, setup_record, staging, plan, choices, qbars):
    import hashlib
    rule, frozen, prior = _kernel("policy_rule"), _kernel("frozen_policy"), _kernel("common_prior")(desc)
    did, upstream, C = setup_record["design_id"], {"SETUP": setup_record["phase_digest"]}, desc["campaign"]
    dev, lib_plan = desc["science"]["dev"], {"DEV": [key for key in plan["DEV"] if key[0] == "DEV_LIB"]}
    symbolic = {"kind": "S2_DEV", "common": desc["science"]["parameters"]["s2_rule"], "s2_grid": sorted(dev["s2_grid"]),
                "criterion": dev["criterion"], "ties": dev["ties"]}

    def row(rule_id, status, subset, s2):
        identity = {"policy_rule_id": rule_id, "subset": subset, "prior": B2W_PRIOR, "s2": s2}
        return {"status": status, **identity, "policy_id": _b2w_sha16(identity) if status == "RUNNABLE" else None}

    def primary(app, label, meta, qbar, d):
        bundle = frozen(desc, app, label, meta["baselines"], qbar, d)
        mask = (bundle["policy"] or {}).get("mask")
        subset = None if mask is None else [int(k) + {"RESIDUAL": 2, "MARKET": 1}[app] for k in np.flatnonzero(mask)]
        return row(rule(desc, label)["policy_rule_id"], bundle["status"], subset, prior)

    def effective(label, s2, meta):
        base = primary("RESIDUAL", label, meta, None, None)
        sensitivity = _b2w_sha16({**rule(desc, label)["recipe"], "s2_rule": symbolic})
        return base if s2 == prior else row(sensitivity, "RUNNABLE", base["subset"], s2)

    setups, dev_ids = {}, {}
    for s in B2W_SETUPS:
        name, metas = pdb.canon(s), setup_record["derived"]["setups"][pdb.canon(s)]["applications"]
        setups[name] = {}
        for app in desc["scope"]["applications"]:
            meta, choice, library, cal_ids, status = metas[app], None, None, [], None
            policies = {"PRIMARY": {}, "GAMMA_M": {}, "S2_DEV": {}}
            if app == "RESIDUAL":
                choice, qbar = choices[name], qbars[name]
                _, parts, library_id = _b2u_expected(staging, setup_record, lib_plan, s)
                library = {"setup_id": meta["setup_id"], "partitions": parts, "qbar": qbar, "dev_library_id": library_id,
                           "qbar_sha": pdb.array_sha256(np.array(qbar, dtype=np.float64))}
                stem = _partition_stem(staging, did, upstream, ["DEV_NULL", C, *s])
                null_sha = hashlib.sha256(stem.with_suffix(".npz").read_bytes()).hexdigest()
                prefix = rule(desc, "FIXED_DEV_PREFIX")["policy_rule_id"]
                cands = [(row(prefix, "RUNNABLE", list(range(2, 2 + c["d"])), prior)["policy_id"], c)
                         for c in choice["d_candidates"]]
                cands += [(effective(label, c["s2"], meta)["policy_id"], p)
                          for c in choice["s2_candidates"] for label, p in c["policies"].items()]
                cal_ids = sorted(_b2w_sha16({"setup_id": meta["setup_id"], "dev_null_sha": null_sha, "policy_id": pid,
                                             "rule": "GE", "n": 19, "h": c["h"], "r": c["r"], "alarms": c["alarms"]})
                                 for pid, c in cands)
                assert len(set(cal_ids)) == len(cal_ids) == 6 + 12 * (choice["s2_dev"] is not None)
                if s == B2W_SETUPS[1]:
                    status = "S2_DEV_EQUALS_COMMON" if choice["s2_dev"] == prior else "S2_DEV_DISTINCT"
                    policies["GAMMA_M"] = {label: row(rule(desc, label, gamma_sensitivity=True)["policy_rule_id"],
                                                      "RUNNABLE", None, prior) for label in B2V_ONLINE}
                    policies["S2_DEV"] = {label: effective(label, choice["s2_dev"], meta) for label in B2W_PCONF}
            qbar = None if library is None else library["qbar"]
            d_dev = None if choice is None else choice["d_dev"]
            policies["PRIMARY"] = {label: primary(app, label, meta, qbar, d_dev) for label in B2W_POLICIES}
            identity = {"setup_id": meta["setup_id"], "dev_library_id": library and library["dev_library_id"],
                        "qbar_sha": library and library["qbar_sha"], "d_dev": d_dev,
                        "s2_dev": choice and choice["s2_dev"], "dev_calibration_ids": cal_ids}
            setups[name][app] = {"applicability": "NOT_APPLICABLE" if library is None else "SELECTED",
                                 "setup_id": meta["setup_id"], "library": library, "choices": choice,
                                 "s2_status": status, "dev_calibration_ids": cal_ids, "policies": policies,
                                 "dev_id": _b2w_sha16(identity)}
            dev_ids[pdb.canon([*s, app])] = setups[name][app]["dev_id"]
    return {"setups": setups, "dev_ids": dev_ids}


@pytest.mark.parametrize("mode,scores", [("full", "controlled"), ("smoke", "controlled"), ("full", "zero"),
                                         ("full", "bridge")])
def test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them(tmp_path, monkeypatch, mode, scores):
    import hashlib
    import json
    fixture, state, calls = _b2w_fixture(tmp_path, monkeypatch, mode), {"cpu": 10.0, "wall": 100.0}, []
    cfg, desc, authority, plan, staging = fixture
    setup_record, context = _b2w_setup(monkeypatch, state, fixture)
    did, C, prior = setup_record["design_id"], desc["campaign"], _kernel("common_prior")(desc)
    upstream, snapshot = {"SETUP": setup_record["phase_digest"]}, pdb.canon([cfg, desc, authority, plan])
    paths = [("path", C, *s, r, i) for s in B2W_SETUPS for r, n in (("DEV_NULL", 19), ("DEV_ALT", 2)) for i in range(n)]
    metas = [("meta", C, *s, "DEV_ALT", f, i) for s in B2W_SETUPS for f in DEV_FAMILIES for i in range(2)]
    shared = sorted([p for p in paths if p[5] == "DEV_NULL"] + [p for p in paths if p[5] == "DEV_ALT" for _ in DEV_FAMILIES])
    assert set(paths + metas) <= set(_kernel("seed_plan")(cfg, mode)["keys"]) and len(plan["DEV"]) == 18
    assert set(desc["scope"]["families"]) < set(DEV_FAMILIES) and (authority["go_reference"] is None) == (mode == "smoke")
    assert desc["science"]["phi"]["setup"] == B2W_SETUPS[1] and not (staging / "phases" / "DEV.json").exists()
    phase = _kernel("dev_phase")
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, scores, prior)
        record = phase(cfg, mode, context)
    assert sorted(c[:7] for c in calls if c[0] == "path") == shared and all(
        (c[7] is None) == (c[5] == "DEV_NULL") for c in calls if c[0] == "path")
    assert sorted(c for c in calls if c[0] == "meta") == sorted(metas)
    assert sorted(c for c in calls if c[0] == "DEV_LIB") == sorted(("DEV_LIB", *s, f) for s in B2W_SETUPS for f in DEV_FAMILIES)
    assert scores == "bridge" or all(sorted(c[7] for c in calls if c[:7] == p) == [1.0, 2.0, 3.0, 4.0]
                                      for p in paths if p[5] == "DEV_ALT")
    rows, arrays = [], {}
    for key in plan["DEV"]:
        data = _partition_stem(staging, did, upstream, key).with_suffix(".npz").read_bytes()
        sha, n_rows, got = _kernel("_verify_partition")(staging, did, upstream, key)
        assert sha == hashlib.sha256(data).hexdigest() and n_rows == {"DEV_LIB": 2, "DEV_NULL": 19, "DEV_ALT": 2}[key[0]]
        rows.append({"key": key, "sha256": sha, "n_rows": n_rows})
        arrays[pdb.canon(key)] = got
        if key[0] != "DEV_LIB":
            assert set(got) == {"Y"} and got["Y"].dtype == np.float64 and got["Y"].shape == (n_rows, 6, 20)
            np.testing.assert_allclose(got["Y"], _b2w_scores(desc, key, scores), rtol=1e-12, atol=1e-12)
    choices, qbars = {}, {}
    with monkeypatch.context() as mp:
        if scores == "controlled":
            mp.setattr(pio(), "nonoracle_scan", _b2v_stub(prior, _kernel("cost_vectors")(504, 20)["MIX"], []))
        for s in B2W_SETUPS:
            alts = {f: arrays[pdb.canon(["DEV_ALT", C, *s, f])]["Y"] for f in DEV_FAMILIES}
            null = arrays[pdb.canon(["DEV_NULL", C, *s])]["Y"]
            choices[pdb.canon(s)] = _kernel("dev_choices")(desc, null, alts, primary=s == B2W_SETUPS[1])
            qbars[pdb.canon(s)] = record["derived"]["setups"][pdb.canon(s)]["RESIDUAL"]["library"]["qbar"]
            assert qbars[pdb.canon(s)] == pytest.approx(_b2u_qbar(s), rel=1e-12)
    picks = [(choices[pdb.canon(s)]["d_dev"], choices[pdb.canon(s)]["s2_dev"]) for s in B2W_SETUPS]
    gold = {"controlled": [(4, None), (4, 4 * prior)], "zero": [(1, None), (1, prior)]}
    assert scores == "bridge" or picks == gold[scores]
    derived = _b2w_expected(desc, setup_record, staging, plan, choices, qbars)
    pairs = sorted([pdb.canon(row["key"]), row["sha256"]] for row in rows)
    identity = {"design_id": did, "phase": "DEV", "upstream": upstream, "partitions": pairs, "derived": derived}
    want = {**identity, "partitions": rows, "phase_digest": hashlib.sha256(pdb.canon(identity).encode()).hexdigest()}
    assert record == want == json.loads((staging / "phases" / "DEV.json").read_text())
    main, equal = derived["setups"][pdb.canon(B2W_SETUPS[1])]["RESIDUAL"]["policies"], picks[1][1] == prior
    assert (main["S2_DEV"]["FULL_K"] == main["PRIMARY"]["FULL_K"]) == equal and (scores != "zero" or equal)
    assert (scores != "controlled" or not equal) and set(main["GAMMA_M"]) == set(B2V_ONLINE)
    assert main["GAMMA_M"]["ONLINE_INFO_MIX_W128"] != main["PRIMARY"]["ONLINE_INFO_MIX_W128"]
    labels = {pdb.canon([*s, app]) for s in B2W_SETUPS for app in ("RESIDUAL", "MARKET")}
    assert set(record["derived"]["dev_ids"]) == labels and len(set(record["derived"]["dev_ids"].values())) == 4
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    poisoned = (mode, scores) == ("full", "controlled")
    later = [f"{p}.json" for p in ("CAL", "NULL_PLAN", "HOLD", "ALT") if poisoned]
    for name in later:
        (staging / "phases" / name).write_bytes(b"{invalid later phase fixture\n")
    before, opened, real_open = _tree(staging), [], type(staging).open

    def guarded(path, *args, **kwargs):
        if path.parent == staging / "phases" and path.name in later:
            opened.append(path.name)
            raise AssertionError(f"reload of a committed DEV opened the later record {path.name}")
        return real_open(path, *args, **kwargs)

    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, scores, prior)
        _b2w_no_recompute(mp, "dev_library_cache", "dev_library_block", "direction_information", "direction_draws",
                          "path_scores", "exact_scores", "null_returns", "dev_qbar", "dev_choices", "nonoracle_scan",
                          "masked_scan", "best_sets")
        mp.setattr(type(staging), "open", guarded)
        again = phase(cfg, mode, renewed)
    assert opened == [] and len(later) == 4 * poisoned and all(f"phases/{name}" in before for name in later)
    after = _tree(staging)
    assert again == record and set(after) == set(before) and len(calls) == len(shared) + len(metas) + 8
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    spent = {"invocation-1": 0.0, "invocation-2": 2.0, "invocation-3": 0.0}
    assert json.loads(after["resources.json"])["cpu_seconds"] == spent
    assert pdb.canon([cfg, desc, authority, plan]) == snapshot
    if poisoned:
        cap = desc["envelope"]["cpu_hours_max"] * 3600
        state["cpu"] += cap + 1.0
        with monkeypatch.context() as mp:
            _b2w_producers(mp, state, calls, scores, prior)
            _b2w_no_recompute(mp, "dev_library_cache", "dev_library_block", "direction_information",
                              "direction_draws", "path_scores", "exact_scores", "null_returns", "dev_qbar",
                              "dev_choices", "nonoracle_scan", "masked_scan", "best_sets")
            mp.setattr(type(staging), "open", guarded)
            with pytest.raises(pdb.ResourceBlocked):
                phase(cfg, mode, renewed)
        blocked = _tree(staging)
        status = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": "DEV",
                  "missing_partitions": []}
        assert opened == [] and cap == 14400.0 and len(calls) == len(shared) + len(metas) + 8
        assert set(blocked) == set(before) | {"status.json"} and json.loads(blocked["status.json"]) == status
        assert all(blocked[name] == data for name, data in before.items() if name != "resources.json")
        assert json.loads(blocked["resources.json"])["cpu_seconds"] == {**spent, "invocation-3": cap + 1.0}


def test_dev_phase_commits_a_not_applicable_market_only_record_with_nonempty_dev_ids(tmp_path, monkeypatch):
    import hashlib
    fixture, state, calls = _b2w_fixture(tmp_path, monkeypatch, "full", ("MARKET",)), {"cpu": 10.0, "wall": 100.0}, []
    cfg, desc, authority, plan, staging = fixture
    setup_record, context = _b2w_setup(monkeypatch, state, fixture)
    derived, prior = _b2w_expected(desc, setup_record, staging, plan, {}, {}), _kernel("common_prior")(desc)
    rows = [entry["MARKET"]["policies"]["PRIMARY"] for entry in derived["setups"].values()]
    assert plan["DEV"] == [] and set(derived["dev_ids"]) == {pdb.canon([*s, "MARKET"]) for s in B2W_SETUPS}
    assert all(r["FIXED_DEV_PREFIX"]["status"] == "NOT_RUN" and r["FIXED_EXANTE_QBAR_MIX"]["status"] == "UNSUPPORTED"
               for r in rows)
    assert all(len(v) == 16 and set(v) <= set("0123456789abcdef") for v in derived["dev_ids"].values())
    upstream = {"SETUP": setup_record["phase_digest"]}
    identity = {"design_id": setup_record["design_id"], "phase": "DEV", "upstream": upstream, "partitions": [],
                "derived": derived}
    want = {**identity, "phase_digest": hashlib.sha256(pdb.canon(identity).encode()).hexdigest()}
    phase = _kernel("dev_phase")
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        _b2w_no_recompute(mp, "dev_qbar", "dev_choices", "nonoracle_scan")
        decoy = staging / "phases" / "CAL.json"
        decoy.write_text(pdb.canon({"decoy": "CAL without DEV"}) + "\n")
        before = _tree(staging)
        with pytest.raises(pio().PhaseOrderError):
            phase(cfg, "full", context)
        refused = _tree(staging)
        decoy.unlink()
        record, again = phase(cfg, "full", context), phase(cfg, "full", context)
    assert record == again == want == _kernel("phase_record")(staging, "DEV", None, None, None) and calls == []
    assert set(refused) == set(before) and "phases/DEV.json" not in refused and "phases/CAL.json" in before
    assert all(refused[name] == data for name, data in before.items() if name != "resources.json")


@pytest.mark.parametrize("case", B2W_FAULTS)
def test_dev_phase_refuses_inventory_authority_setup_or_cache_faults_before_any_dev_producer(tmp_path, monkeypatch, case):
    module, state, calls = pio(), {"cpu": 10.0, "wall": 100.0}, []
    fixture = _b2w_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    later, prior = ["DEV_NULL", desc["campaign"], *B2W_SETUPS[1]], _kernel("common_prior")(desc)
    if case == "setup_missing":
        with monkeypatch.context() as mp:
            _b1m_clock(mp, state)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-1")
    else:
        record, context = _b2w_setup(monkeypatch, state, fixture)
    caches = {"short_later_null": (later, {"Y": np.zeros((18, 6, 20))}),
              "narrow_later_alt": (["DEV_ALT", *later[1:], DEV_FAMILIES[3]], {"Y": np.zeros((2, 6, 19))}),
              "extra_null_array": (later, {"Y": np.zeros((19, 6, 20)), "q": np.zeros(19)})}
    if case in caches:
        key, arrays = caches[case]
        stored = _kernel("partition")(staging, "DEV", {"SETUP": record["phase_digest"]}, key, lambda: arrays)
        assert key in plan["DEV"] and _same_arrays(stored, arrays)
    foreign = sorted([*plan["DEV"], ["DEV_ALT", *later[1:], "F3_MARKET"]], key=pdb.canon)
    given = {"missing_null_key": {**context, "plan": {**plan, "DEV": [k for k in plan["DEV"] if k != later]}},
             "foreign_family_key": {**context, "plan": {**plan, "DEV": foreign}},
             "stale_authority": {**context, "authority": {**authority, "go_reference": None}}}.get(case, context)
    size = 18 + (case == "foreign_family_key") - (case == "missing_null_key")
    assert _kernel("_validated_plan")(given["plan"]) is None and len(given["plan"]["DEV"]) == size
    error = {"missing_null_key": ValueError, "foreign_family_key": ValueError,
             "stale_authority": module.AuthorizationRefused, "setup_missing": module.PhaseOrderError}
    phase, before = _kernel("dev_phase"), _tree(tmp_path)
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        _b2s_forbid(mp, "dev_qbar", "dev_choices")
        with pytest.raises(error.get(case, pdb.PartitionMismatch)):
            phase(cfg, "full", given)
    after, untouched = _tree(tmp_path), case in ("missing_null_key", "foreign_family_key", "stale_authority")
    assert calls == [] and set(after) == set(before) and not (staging / "phases" / "DEV.json").exists()
    assert all(after[name] == data for name, data in before.items() if untouched or not name.endswith("resources.json"))


@pytest.mark.parametrize("fault", ["deleted_payload", "forged_dev_id", "forged_candidate_prior"])
def test_dev_phase_rejects_a_corrupt_committed_dev_record_without_repair_or_recompute(tmp_path, monkeypatch, fault):
    import hashlib
    import json
    fixture, state = _b2w_fixture(tmp_path, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cfg, desc, authority, plan, staging = fixture
    _, context = _b2w_setup(monkeypatch, state, fixture)
    prior, phase = _kernel("common_prior")(desc), _kernel("dev_phase")
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, [], "controlled", prior)
        record = phase(cfg, "full", context)
    if fault == "deleted_payload":
        key = ["DEV_ALT", desc["campaign"], *B2W_SETUPS[0], DEV_FAMILIES[0]]
        _partition_stem(staging, record["design_id"], record["upstream"], key).with_suffix(".npz").unlink()
    else:
        derived, name = json.loads(pdb.canon(record["derived"])), pdb.canon(B2W_SETUPS[0])
        if fault == "forged_dev_id":
            derived["dev_ids"][pdb.canon([*B2W_SETUPS[0], "MARKET"])] = "0" * 16
            derived["setups"][name]["MARKET"]["dev_id"] = "0" * 16
        else:
            first = derived["setups"][name]["RESIDUAL"]["choices"]["d_candidates"][0]
            assert B2W_SETUPS[0] != desc["science"]["phi"]["setup"] and first["s2"] == prior
            first["s2"] = 4 * prior
        pairs = sorted([pdb.canon(row["key"]), row["sha256"]] for row in record["partitions"])
        identity = {"design_id": record["design_id"], "phase": "DEV", "upstream": record["upstream"],
                    "partitions": pairs, "derived": derived}
        forged = {**identity, "partitions": record["partitions"],
                  "phase_digest": hashlib.sha256(pdb.canon(identity).encode()).hexdigest()}
        (staging / "phases" / "DEV.json").write_text(pdb.canon(forged) + "\n")
        assert _kernel("phase_record")(staging, "DEV", None, None, None) == forged
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    before, calls = _tree(staging), []
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        _b2w_no_recompute(mp, "dev_qbar", "dev_choices", "nonoracle_scan")
        with pytest.raises(pdb.PartitionMismatch):
            phase(cfg, "full", renewed)
    after = _tree(staging)
    assert calls == [] and set(after) == set(before) and "status.json" not in after
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_dev_phase_resumes_only_missing_batches_after_an_interrupted_score_write(tmp_path, monkeypatch):
    import json
    state, ref = {"cpu": 10.0, "wall": 100.0}, _b2w_fixture(tmp_path / "reference", monkeypatch)
    ref_record, ref_context = _b2w_setup(monkeypatch, state, ref)
    prior, phase = _kernel("common_prior")(ref[1]), _kernel("dev_phase")
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, [], "controlled", prior)
        expected = phase(ref[0], "full", ref_context)
    fixture, state = _b2w_fixture(tmp_path / "interrupted", monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cfg, desc, authority, plan, staging = fixture
    record, context = _b2w_setup(monkeypatch, state, fixture)
    did, upstream, C = record["design_id"], {"SETUP": record["phase_digest"]}, desc["campaign"]
    batch, sentinel, calls = ["DEV_ALT", C, *B2W_SETUPS[1], DEV_FAMILIES[3]], RuntimeError("interrupted score"), []
    assert pdb.canon([cfg, desc, record]) == pdb.canon([ref[0], ref[1], ref_record]) and expected["upstream"] == upstream
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior, (("path", C, *B2W_SETUPS[1], "DEV_ALT", 1, 4.0), sentinel))
        with pytest.raises(RuntimeError) as caught:
            phase(cfg, "full", context)
    durable = [k for k in plan["DEV"] if _partition_stem(staging, did, upstream, k).with_suffix(".json").exists()]
    spent = json.loads((staging / "resources.json").read_text())["cpu_seconds"]
    assert caught.value is sentinel and durable == [k for k in plan["DEV"] if k[0] != "DEV_NULL" and k != batch]
    assert spent == {"invocation-1": 0.0, "invocation-2": 2.0} and not (staging / "phases" / "DEV.json").exists()
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    calls = []
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        resumed = phase(cfg, "full", renewed)
    made = {pdb.canon([c[5], C, *c[2:5], *([] if c[7] is None else [DEV_FAMILIES[int(c[7]) - 1]])])
            for c in calls if c[0] == "path"}
    metas = sorted(("meta", C, *B2W_SETUPS[1], "DEV_ALT", DEV_FAMILIES[3], i) for i in range(2))
    assert made == {pdb.canon(k) for k in plan["DEV"] if k not in durable} and len(made) == 3
    assert sorted(c for c in calls if c[0] == "meta") == metas and not any(c[0] == "DEV_LIB" for c in calls)
    assert resumed == expected and _tree(staging / "partitions") == _tree(ref[4] / "partitions")
    assert (staging / "phases" / "DEV.json").read_bytes() == (ref[4] / "phases" / "DEV.json").read_bytes()
    spent = {"invocation-1": 0.0, "invocation-2": 2.0, "invocation-3": 0.0}
    assert json.loads((staging / "resources.json").read_text())["cpu_seconds"] == spent


@pytest.mark.parametrize("case", ["budget", "choice"])
def test_dev_phase_blocks_on_budget_and_keeps_an_unmasked_choice_error_without_committing(tmp_path, monkeypatch, case):
    import json
    module, state, calls = pio(), {"cpu": 10.0, "wall": 100.0}, []
    fixture = _b2w_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    record, context = _b2w_setup(monkeypatch, state, fixture)
    did, upstream, prior = record["design_id"], {"SETUP": record["phase_digest"]}, _kernel("common_prior")(desc)
    cap, sentinel = desc["envelope"]["cpu_hours_max"] * 3600, RuntimeError("DEV choice failure")

    def choose(*args, **kwargs):
        state["cpu"] += cap + 1.0
        raise sentinel

    assert cap == 14400.0 and len(plan["DEV"]) == 18
    state["cpu"] += (cap + 1.0) * (case == "budget")
    phase, before = _kernel("dev_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        mp.setattr(module, "dev_choices", choose)
        with pytest.raises(Exception) as caught:
            phase(cfg, "full", context)
    after = _tree(staging)
    written = sorted(set(after) - set(before))
    assert json.loads(after["resources.json"])["cpu_seconds"]["invocation-2"] >= cap
    assert not (staging / "phases" / "DEV.json").exists()
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    if case == "budget":
        missing = [{"phase": "DEV", "key": key} for key in plan["DEV"]]
        status = {"status": "BLOCKED_RESOURCE", "design_id": did, "last_complete_phase": "SETUP",
                  "missing_partitions": missing}
        assert isinstance(caught.value, pdb.ResourceBlocked) and calls == [] and written == ["status.json"]
        assert json.loads(after["status.json"]) == status
    else:
        stems = {_partition_stem(staging, did, upstream, key).name for key in plan["DEV"]}
        assert caught.value is sentinel and written == sorted(f"partitions/{s}.{e}" for s in stems for e in ("npz", "json"))


def test_policy_rule_records_the_symbolic_s2_dev_recipe_before_execution_and_keeps_old_calls(monkeypatch):
    desc, opened = _b2q_desc(), []
    reverse = _b2q_desc((("dev", "s2_grid"), [64, 16, 4, 1]))
    params, dev = desc["science"]["parameters"], desc["science"]["dev"]
    symbolic = {"kind": "S2_DEV", "common": params["s2_rule"], "s2_grid": [1, 4, 16, 64], "criterion": dev["criterion"],
                "ties": dev["ties"]}
    old = {label: _b2s_recipe(label, params["gamma_M"], params["s2_rule"]) for label in B2W_PCONF}
    new = {label: {**recipe, "s2_rule": symbolic} for label, recipe in old.items()}
    gamma = {label: _b2s_recipe(label, params["H"] / params["alpha"], params["s2_rule"]) for label in B2V_ONLINE}
    ids = [_b2s_reference(recipe)[1] for recipe in (*old.values(), *new.values(), *gamma.values())]
    assert dev["s2_grid"] == [1, 4, 16, 64] and len(set(ids)) == 8 and pdb.canon(reverse) != pdb.canon(desc)
    rule, kept = _kernel("policy_rule"), [pdb.canon(desc), pdb.canon(reverse)]
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, opened)
        outs = [(label, rule(source, label, s2_sensitivity=True)) for label in B2W_PCONF for source in (desc, reverse)]
        plain = {label: [rule(desc, label), rule(desc, label, gamma_sensitivity=False, s2_sensitivity=False)]
                 for label in B2W_PCONF}
        moved = {label: rule(desc, label, gamma_sensitivity=True, s2_sensitivity=False) for label in B2W_PCONF}
    for label, out in outs:
        assert out == {"recipe": new[label], "policy_rule_id": _b2s_reference(new[label])[1]}
    for label in B2W_PCONF:
        want = {"recipe": old[label], "policy_rule_id": _b2s_reference(old[label])[1]}
        shifted = {"recipe": gamma[label], "policy_rule_id": _b2s_reference(gamma[label])[1]} if label in gamma else want
        assert plain[label] == [want, want] and moved[label] == shifted
    assert opened == [] and [pdb.canon(desc), pdb.canon(reverse)] == kept


@pytest.mark.parametrize("case", B2W_RULE_REFUSALS)
def test_policy_rule_refuses_an_unplanned_or_malformed_s2_sensitivity(monkeypatch, case):
    label, flags, edits = B2W_RULE_REFUSALS[case]
    given, rule = _b2q_desc(*edits), _kernel("policy_rule")
    assert rule(given, label)["recipe"]["s2_rule"] == "2*ln(H/alpha)/(H*K)"
    with monkeypatch.context() as mp:
        _b2s_rule_traps(mp, [])
        with pytest.raises(ValueError):
            rule(given, label, **flags)


def test_tiny_oracle_fluid_score_dominates():
    cost, select = _kernel("cost_vectors")(GAMMA, 8)["MIX"], _kernel("best_sets")
    (d, mask), prefix_mask = select(QS, cost, "INFO"), select(QS, cost, "PREFIX")[1]
    for q, k, chosen, prefix in zip(QS, d, mask, prefix_mask):
        values = [math.fsum(q[j] for j in S) / cost[len(S) - 1] for n in range(1, 9)
                  for S in itertools.combinations(range(8), n)]
        oracle = math.fsum(q[chosen]) / cost[int(k) - 1]
        fixed = math.fsum(q[prefix]) / cost[int(prefix.sum()) - 1]
        assert int(chosen.sum()) == k and len(values) == 255 and oracle == pytest.approx(max(values), rel=1e-12, abs=0.0)
        assert all(oracle >= v * (1 - 1e-12) for v in values) and fixed <= oracle * (1 + 1e-12)


def test_dev_phase_refuses_a_produced_dev_score_of_the_wrong_shape_before_serializing_it(tmp_path, monkeypatch):
    module, state, calls, attempts = pio(), {"cpu": 10.0, "wall": 100.0}, [], []
    fixture = _b2w_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    record, context = _b2w_setup(monkeypatch, state, fixture)
    did, upstream, prior = record["design_id"], {"SETUP": record["phase_digest"]}, _kernel("common_prior")(desc)
    libraries = [key for key in plan["DEV"] if key[0] == "DEV_LIB"]
    target = [key for key in plan["DEV"] if key[0] != "DEV_LIB"][0]
    for key in libraries:
        q = _b2u_q(list(key[2:5]), key[5])
        stored = _kernel("partition")(staging, "DEV", upstream, key, lambda q=q: {"q": q})
        assert _same_arrays(stored, {"q": q})
    assert len(libraries) == 8 and target == ["DEV_ALT", desc["campaign"], *B2W_SETUPS[0], DEV_FAMILIES[0]]
    assert [desc["sizes"]["DEV_ALT"], desc["science"]["parameters"]["H"]] == [2, 6]
    assert not (staging / "phases" / "DEV.json").exists()
    phase, before = _kernel("dev_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, calls, "controlled", prior)
        fake, real_npz = module.path_scores, module._npz_payload
        mark = 1.0 + DEV_FAMILIES.index(target[5])

        def narrow(desc, frame, fit, application, key, delta=None):
            Y = fake(desc, frame, fit, application, key, delta)
            hit = list(key[2:6]) == [*target[2:5], "DEV_ALT"] and delta is not None and delta[0] == mark
            return Y[:, :19] if hit else Y

        def serialize(arrays):
            if "Y" in arrays and np.shape(arrays["Y"])[1:] != (6, 20):
                attempts.append(np.shape(arrays["Y"]))
                raise AssertionError("an invalid produced DEV score reached the NPZ serializer")
            return real_npz(arrays)

        mp.setattr(module, "path_scores", narrow)
        mp.setattr(module, "_npz_payload", serialize)
        with pytest.raises(ValueError):
            phase(cfg, "full", context)
    after = _tree(staging)
    stems = {_partition_stem(staging, did, upstream, key).name for key in plan["DEV"] if key[0] != "DEV_LIB"}
    assert attempts == [] and not any(c[0] == "DEV_LIB" for c in calls)
    assert any(c[0] == "path" and list(c[2:6]) == [*target[2:5], "DEV_ALT"] for c in calls)
    assert set(after) == set(before) and "phases/DEV.json" not in after
    assert not any(name.startswith(f"partitions/{stem}") for stem in stems for name in after)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


B3A_ALPHA = 0.05
B3A_FIELDS = {"h", "r", "alarms", "n", "maxima"}
B3A_ORACLE_LABEL = "NON_DEPLOYABLE_ORACLE_CALIBRATION"
B3A_NONORACLE = {"FULL_K": ("MARKET", "FULL_K"), "ONLINE_INFO": ("RESIDUAL", "ONLINE_INFO_MIX_W128"),
                 "ONLINE_PREFIX": ("RESIDUAL", "ONLINE_PREFIX_MIX_W128")}
B3A_CROSSED = {"nonoracle": ("oracle_masks", "oracle_scan"),
               "oracle": ("nonoracle_masks", "online_masks", "nonoracle_scan")}


def _b3a_scores(n, H=6, axes=(0,), steps=3):
    Y = np.zeros((n, H, 20))
    for b in range(n):
        Y[b, :steps, axes[b % len(axes)]] = 2.0 + 0.25 * b
    return Y


def _b3a_rank(maxima, alpha):
    from fractions import Fraction
    values = sorted(float(v) for v in maxima)
    n = len(values)
    r = math.floor(Fraction(str(alpha)) * (n + 1)) - 1
    b = values[n - r - 1]
    return math.nextafter(b, math.inf), r, sum(v > b for v in values), b


def _b3a_masks(Y, bundle):
    policy = bundle["policy"]
    if policy["kind"] == "STATIC":
        return np.broadcast_to(policy["mask"], Y.shape)
    return _b2r_online_ref(Y, policy["window"], policy["cost"], policy["order"])


def _b3a_oracle_case(n):
    desc = _b2q_desc((("parameters", "H"), 5))
    bundle = _kernel("frozen_policy")(desc, "RESIDUAL", "ORACLE_INFO_MIX")
    Y, q_true, cost = _b3a_scores(n, H=5, axes=(3, 12), steps=2), np.zeros((n, 20)), bundle["policy"]["cost"]
    Y[:, :, 0] = 7.0
    q_true[0::2, 3], q_true[1::2, 12], q_true[1::2, 17] = 0.5, 0.5, 0.5
    M = np.zeros(Y.shape, dtype=bool)
    for b, q in enumerate(q_true):
        M[b][:, _greedy(q.tolist(), cost.tolist())[1]] = True
    return desc, bundle, Y, q_true, M


def _b3a_spies(mp, calls, *names):
    import inspect
    module = pio()

    def spy(owner, name):
        real = getattr(owner, name)
        signature = inspect.signature(real)

        def wrapped(*args, **kwargs):
            calls.append((name, dict(signature.bind(*args, **kwargs).arguments)))
            return real(*args, **kwargs)

        return wrapped

    for name in names:
        owner = pdb if name == "rank_threshold" else module
        mp.setattr(owner, name, spy(owner, name))


def _b3a_traps(mp, *names):
    module = pio()

    def forbidden(*args, **kwargs):
        raise AssertionError("prior recomputation, policy rebuild, crossed scan, DEV, generation or fit inside CAL")

    extras = tuple((module, extra) for extra in names)
    for owner, name in ((module, "common_prior"), (module, "frozen_policy"), (module, "population_frame"),
                        (module, "null_returns"), (module, "exact_scores"), (module, "path_scores"),
                        (module, "direction_draws"), (module, "direction_information"), (module, "dev_qbar"),
                        (module, "dev_choices"), (module, "fit_record"), (module, "spectral_baselines"),
                        (pdb, "fit_basis"), (pdb, "scan_statistic"), (pdb.sim, "t_innov"), *extras):
        mp.setattr(owner, name, forbidden)


@pytest.mark.parametrize("multiplier", [1.0, 4.0])
@pytest.mark.parametrize("policy", sorted(B3A_NONORACLE))
def test_calibrate_nonoracle_ranks_the_timewise_maxima_of_one_real_scan_at_the_sealed_ge_boundary(
        monkeypatch, policy, multiplier):
    desc, scan = _b2q_desc(), _kernel("masked_scan")
    prior = multiplier * _kernel("common_prior")(desc)
    bundle = {**_kernel("frozen_policy")(desc, *B3A_NONORACLE[policy]), "s2": prior}
    Y = _b3a_scores(39)
    M = _b3a_masks(Y, bundle)
    assert np.array_equal(_kernel("nonoracle_masks")(Y, bundle["policy"]), M) and M[:, :, 0].all()
    assert M.all() == (policy == "FULL_K")
    W = scan(Y, M, prior)[0]
    maxima = W.max(axis=1)
    h, r, alarms, b = _b3a_rank(maxima, B3A_ALPHA)
    assert (np.diff(maxima) > 0).all() and (maxima > W[:, -1]).all() and _b3a_rank(W[:, -1], B3A_ALPHA)[0] < h
    assert (r, alarms, b) == (1, 1, float(maxima[37])) and h == np.nextafter(b, np.inf) > b
    nonoracle = _kernel("nonoracle_scan")
    assert np.flatnonzero(nonoracle(Y, bundle, b)["first"] > 0).tolist() == [37, 38]
    assert np.flatnonzero(nonoracle(Y, bundle, h)["first"] > 0).tolist() == [38]
    frozen, kept = _b2r_freeze(bundle), Y.tobytes()
    Y.flags.writeable = False
    calibrate, calls = _kernel("calibrate_nonoracle"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp, *B3A_CROSSED["nonoracle"])
        _b3a_spies(mp, calls, "nonoracle_masks", "masked_scan", "rank_threshold")
        out = calibrate(Y, bundle, B3A_ALPHA)
    assert set(out) == B3A_FIELDS and type(out["h"]) is float and out["h"] == h
    assert all(type(out[key]) is int for key in ("r", "alarms", "n"))
    assert (out["r"], out["alarms"], out["n"]) == (r, alarms, 39) == (1, 1, 39)
    assert out["maxima"].dtype == np.float64 and np.array_equal(out["maxima"], maxima)
    assert [name for name, _ in calls] == ["nonoracle_masks", "masked_scan", "rank_threshold"]
    scanned, ranked = calls[1][1], calls[2][1]
    assert scanned["s2"] == prior and scanned.get("h") is None and np.array_equal(scanned["M"], M)
    assert np.array_equal(ranked["maxima"], maxima) and ranked["alpha"] == B3A_ALPHA and ranked["rule"] == "GE"
    assert _b2r_freeze(bundle) == frozen and Y.tobytes() == kept


def test_calibrate_nonoracle_is_invariant_to_cal_row_permutation_and_identical_on_replay(monkeypatch):
    bundle = _kernel("frozen_policy")(_b2q_desc(), "RESIDUAL", "ONLINE_INFO_MIX_W128")
    Y = _b3a_scores(39)
    perm = np.random.default_rng(np.random.SeedSequence([32, 43])).permutation(39)
    moved = Y[perm]
    maxima = _kernel("masked_scan")(Y, _b3a_masks(Y, bundle), bundle["s2"])[0].max(axis=1)
    h, r, alarms, _ = _b3a_rank(maxima, B3A_ALPHA)
    assert (perm != np.arange(39)).any() and len(np.unique(maxima)) == 39 and (r, alarms) == (1, 1)
    assert _b3a_rank(maxima[perm], B3A_ALPHA)[:3] == (h, r, alarms)
    for array in (Y, moved):
        array.flags.writeable = False
    calibrate = _kernel("calibrate_nonoracle")
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp, *B3A_CROSSED["nonoracle"])
        outs = [calibrate(Y, bundle, B3A_ALPHA), calibrate(moved, bundle, B3A_ALPHA), calibrate(Y, bundle, B3A_ALPHA)]
    first, shuffled, replay = outs
    for out in outs:
        assert set(out) == B3A_FIELDS and (out["h"], out["r"], out["alarms"], out["n"]) == (h, r, alarms, 39)
    assert np.array_equal(first["maxima"], maxima) and np.array_equal(shuffled["maxima"], maxima[perm])
    assert replay["maxima"].tobytes() == first["maxima"].tobytes()


@pytest.mark.parametrize("case, alarmed", [("top_pair", []), ("rank_pair", [38])])
def test_calibrate_nonoracle_counts_tied_maxima_conservatively_at_the_sealed_ge_boundary(monkeypatch, case, alarmed):
    bundle = _kernel("frozen_policy")(_b2q_desc(), "MARKET", "FULL_K")
    Y, tied = _b3a_scores(39), ([37, 38] if case == "top_pair" else [36, 37])
    Y[tied[0] if case == "rank_pair" else tied[1]] = Y[37]
    maxima = _kernel("masked_scan")(Y, _b3a_masks(Y, bundle), bundle["s2"])[0].max(axis=1)
    h, r, alarms, b = _b3a_rank(maxima, B3A_ALPHA)
    assert len(np.unique(maxima)) == 38 and maxima[tied[0]] == maxima[tied[1]] == b
    assert (r, alarms) == (1, len(alarmed)) and alarms <= r and h == np.nextafter(b, np.inf)
    nonoracle = _kernel("nonoracle_scan")
    assert np.flatnonzero(nonoracle(Y, bundle, b)["first"] > 0).tolist() == sorted({*tied, 38})
    assert np.flatnonzero(nonoracle(Y, bundle, h)["first"] > 0).tolist() == alarmed
    Y.flags.writeable = False
    calibrate, calls = _kernel("calibrate_nonoracle"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp, *B3A_CROSSED["nonoracle"])
        _b3a_spies(mp, calls, "rank_threshold")
        out = calibrate(Y, bundle, B3A_ALPHA)
    assert set(out) == B3A_FIELDS and (out["h"], out["r"], out["alarms"], out["n"]) == (h, 1, len(alarmed), 39)
    assert np.array_equal(out["maxima"], maxima) and [name for name, _ in calls] == ["rank_threshold"]
    assert np.flatnonzero(nonoracle(Y, bundle, out["h"])["first"] > 0).tolist() == alarmed


@pytest.mark.parametrize("kind", ["nonoracle", "oracle"])
def test_calibrations_raise_the_sealed_insufficient_calibration_at_18_rows_and_rank_19_at_r_zero(monkeypatch, kind):
    assert pdb.min_calibration_n(B3A_ALPHA) == 19 and [pdb.predictive_rank(n, B3A_ALPHA) for n in (18, 19)] == [-1, 0]
    cases = {}
    for n in (18, 19):
        if kind == "oracle":
            _, bundle, Y, q_true, M = _b3a_oracle_case(n)
            args = (Y, q_true, bundle, B3A_ALPHA)
        else:
            bundle, Y = _kernel("frozen_policy")(_b2q_desc(), "MARKET", "FULL_K"), _b3a_scores(n)
            M, args = _b3a_masks(Y, bundle), (Y, bundle, B3A_ALPHA)
        maxima = _kernel("masked_scan")(Y, M, bundle["s2"])[0].max(axis=1)
        assert len(np.unique(maxima)) == n
        cases[n] = (args, maxima)
    with pytest.raises(pdb.InsufficientCalibration):
        pdb.rank_threshold(cases[18][1], B3A_ALPHA, "GE")
    h, r, alarms, b = _b3a_rank(cases[19][1], B3A_ALPHA)
    assert (r, alarms, b) == (0, 0, float(cases[19][1].max())) and h == np.nextafter(b, np.inf)
    calibrate, calls = _kernel(f"calibrate_{kind}"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp, *B3A_CROSSED[kind])
        _b3a_spies(mp, calls, "rank_threshold")
        with pytest.raises(pdb.InsufficientCalibration) as short:
            calibrate(*cases[18][0])
        out = calibrate(*cases[19][0])
    assert short.type is pdb.InsufficientCalibration and [name for name, _ in calls] == ["rank_threshold"] * 2
    assert [np.shape(a["maxima"]) for _, a in calls] == [(18,), (19,)] and all(a["rule"] == "GE" for _, a in calls)
    assert np.array_equal(calls[0][1]["maxima"], cases[18][1]) and np.array_equal(out["maxima"], cases[19][1])
    assert (out["h"], out["r"], out["alarms"], out["n"]) == (h, 0, 0, 19)
    assert set(out) == (B3A_FIELDS | {"label"} if kind == "oracle" else B3A_FIELDS)


@pytest.mark.parametrize("multiplier", [1.0, 4.0])
def test_calibrate_oracle_ranks_one_real_scan_of_the_supplied_true_q_under_a_separate_non_deployable_label(
        monkeypatch, multiplier):
    desc, bundle, Y, q_true, M = _b3a_oracle_case(39)
    prior, scan, masks = multiplier * _kernel("common_prior")(desc), _kernel("masked_scan"), _kernel("oracle_masks")
    bundle = {**bundle, "s2": prior}
    assert np.array_equal(masks(q_true, bundle["policy"]), M)
    assert M[0::2, :, 3].all() and M[1::2][:, :, [12, 17]].all() and int(M.sum()) == 5 * (20 + 19 * 2)
    W = scan(Y, M, prior)[0]
    maxima = W.max(axis=1)
    h, r, alarms, b = _b3a_rank(maxima, B3A_ALPHA)
    top, decoy = int(np.argmax(maxima)), np.zeros_like(q_true)
    decoy[:, 0] = 0.5
    assert len(np.unique(maxima)) == 39 and (maxima > W[:, -1]).all() and (r, alarms) == (1, 1)
    assert b == float(np.sort(maxima)[37]) and h == np.nextafter(b, np.inf)
    assert _b3a_rank(scan(Y, masks(decoy, bundle["policy"]), prior)[0].max(axis=1), B3A_ALPHA)[0] != h
    oracle = _kernel("oracle_scan")
    assert np.flatnonzero(oracle(Y, q_true, bundle, h)["first"] > 0).tolist() == [top]
    assert len(np.flatnonzero(oracle(Y, q_true, bundle, b)["first"] > 0)) == 2
    frozen, kept = _b2r_freeze(bundle), [Y.tobytes(), q_true.tobytes()]
    for array in (Y, q_true):
        array.flags.writeable = False
    calibrate, calls = _kernel("calibrate_oracle"), []
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp, *B3A_CROSSED["oracle"])
        _b3a_spies(mp, calls, "oracle_masks", "masked_scan", "rank_threshold")
        out = calibrate(Y, q_true, bundle, B3A_ALPHA)
    assert set(out) == B3A_FIELDS | {"label"} and out["label"] == B3A_ORACLE_LABEL
    assert type(out["h"]) is float and (out["h"], out["r"], out["alarms"], out["n"]) == (h, 1, 1, 39)
    assert out["maxima"].dtype == np.float64 and np.array_equal(out["maxima"], maxima)
    assert [name for name, _ in calls] == ["oracle_masks", "masked_scan", "rank_threshold"]
    masked, scanned, ranked = (arguments for _, arguments in calls)
    assert np.array_equal(masked["q_true"], q_true) and scanned["s2"] == prior and scanned.get("h") is None
    assert np.array_equal(scanned["M"], M) and np.array_equal(ranked["maxima"], maxima) and ranked["rule"] == "GE"
    assert ranked["alpha"] == B3A_ALPHA and _b2r_freeze(bundle) == frozen and [Y.tobytes(), q_true.tobytes()] == kept


def test_calibrations_take_q_only_on_the_oracle_side_and_refuse_crossed_bundles_before_any_rank(monkeypatch):
    import inspect
    online = _kernel("frozen_policy")(_b2q_desc(), "RESIDUAL", "ONLINE_INFO_MIX_W128")
    _, oracle_bundle, Y5, q_true, _ = _b3a_oracle_case(39)
    Y6 = _b3a_scores(39)
    assert online["policy"]["kind"] == "ONLINE" and oracle_bundle["policy"]["kind"] == "ORACLE"
    with pytest.raises(ValueError):
        _kernel("nonoracle_scan")(Y5, oracle_bundle)
    with pytest.raises(ValueError):
        _kernel("oracle_scan")(Y6, q_true, online)
    nonoracle, oracle = _kernel("calibrate_nonoracle"), _kernel("calibrate_oracle")
    assert list(inspect.signature(nonoracle).parameters) == ["Y", "bundle", "alpha"]
    assert list(inspect.signature(oracle).parameters) == ["Y", "q_true", "bundle", "alpha"]

    def forbidden(*args, **kwargs):
        raise AssertionError("rank calibration of a crossed bundle")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        _b3a_traps(mp)
        mp.setattr(pdb, "rank_threshold", forbidden)
        with pytest.raises(ValueError):
            nonoracle(Y5, oracle_bundle, B3A_ALPHA)
        with pytest.raises(ValueError):
            oracle(Y6, q_true, online, B3A_ALPHA)


B3B_AXIS = {"F2_STRUCTURED_RESIDUAL": 0, "F_HEAD_RESIDUAL": 7}
B3B_TRAPPED = ("path_scores", "direction_information", "calibrate_nonoracle", "calibrate_oracle", "nonoracle_scan",
               "oracle_scan", "masked_scan")


def _b3b_Y(application, n):
    Y = np.zeros((n, 6, 20))
    Y[:, :3, 0] = 2.0 + 0.25 * np.arange(n)[:, None] + (application == "MARKET")
    return Y


def _b3b_guard(mp, state, *trapped):
    _b1m_clock(mp, state)
    _no_draws_or_workers(mp)
    _b2o_forbid(mp)
    _b2s_forbid(mp, "dev_library_cache", "dev_library_block", "dev_qbar", "dev_choices", "direction_draws")
    if trapped:
        _b2w_no_recompute(mp, *trapped)


def _b3b_fixture(root, monkeypatch, dev=True):
    monkeypatch.setitem(B2V_SIZES, "CAL_NULL", 39)
    monkeypatch.setitem(globals(), "B2W_POLICIES", [*B2W_POLICIES, "ONLINE_PREFIX_MIX_W128"])
    fixture, state = _b2w_fixture(root, monkeypatch), {"cpu": 10.0, "wall": 100.0}
    cfg, desc, authority, plan, staging = fixture
    plan["CAL"] = sorted((["CAL_NULL", desc["campaign"], *s, app] for s in B2W_SETUPS
                          for app in desc["scope"]["applications"]), key=pdb.canon)
    setup_record, context = _b2w_setup(monkeypatch, state, fixture)
    dev_record = None
    with monkeypatch.context() as mp:
        _b2w_producers(mp, state, [], "zero", _kernel("common_prior")(desc))
        if dev:
            dev_record = _kernel("dev_phase")(cfg, "full", context)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-3")
    return fixture, state, setup_record, dev_record, context


def _b3b_producers(mp, state, calls, adapters):
    module = pio()
    real_nonoracle, real_oracle = module.calibrate_nonoracle, module.calibrate_oracle
    _b3b_guard(mp, state)

    def path(desc, frame, fit, application, key, delta=None):
        assert key[0] == "path" and key[5] == "CAL_NULL" and delta is None
        calls.append((application, *key))
        return _b3b_Y(application, key[6] + 1)[-1]

    def information(desc, frame, fit, setup, application, key):
        assert key[0] == "meta" and key[5] == "CAL_NULL" and list(key[2:5]) == list(setup)
        calls.append((application, *key))
        return {"status": "SUPPORTED", "family": key[6], "support": None, "q": np.eye(20)[B3B_AXIS[key[6]]] / 2,
                "I_joint": 0.0, "delta": np.ones(key[3]), "oracle_basis": module.PROJECTION_ARMS[key[2]]}

    mp.setattr(module, "path_scores", path)
    mp.setattr(module, "direction_information", information)
    mp.setattr(module, "calibrate_nonoracle", lambda Y, bundle, alpha: adapters.append(
        ("nonoracle", bundle["label"])) or real_nonoracle(Y, bundle, alpha))
    mp.setattr(module, "calibrate_oracle", lambda Y, q_true, bundle, alpha: adapters.append(
        ("oracle", bundle["label"], int(np.argmax(np.asarray(q_true)[0])))) or real_oracle(Y, q_true, bundle, alpha))


def _b3b_expected(desc, setup_record, dev_record):
    frozen, gamma, want, adapters = _kernel("frozen_policy"), _kernel("gamma_sensitivity_policy"), {}, []
    n = desc["sizes"]["CAL_NULL"]
    for s, app in itertools.product(B2W_SETUPS, desc["scope"]["applications"]):
        meta = setup_record["derived"]["setups"][pdb.canon(s)]["applications"][app]
        dev, Y, work = dev_record["derived"]["setups"][pdb.canon(s)][app], _b3b_Y(app, n), []
        families = [f for f in desc["scope"]["families"] if desc["science"]["families"][f]["application"] == app]
        for label in desc["scope"]["policies"]:
            bundle = frozen(desc, app, label, meta["baselines"], dev["library"] and dev["library"]["qbar"],
                            dev["choices"] and dev["choices"]["d_dev"])
            work += [(dev["policies"]["PRIMARY"][label], bundle)] if bundle["status"] == "RUNNABLE" else []
            work += [(row, gamma(desc, bundle)) for key, row in dev["policies"]["GAMMA_M"].items() if key == label]
        for row, bundle in work:
            for family in (families if bundle["policy"]["kind"] == "ORACLE" else [None]):
                tag = {"family": family} if family else {}
                W = (_kernel("oracle_scan")(Y, np.tile(np.eye(20)[B3B_AXIS[family]] / 2, (n, 1)), bundle) if family
                     else _kernel("nonoracle_scan")(Y, bundle))["W"]
                h, r, alarms, _ = _b3a_rank(W.max(axis=1), B3A_ALPHA)
                base = {"setup_id": meta["setup_id"], "policy_id": row["policy_id"], "n_cal": n,
                        "maxima_sha256": pdb.array_sha256(W.max(axis=1)), **tag}
                want[pdb.sha16({**base, "rule": "GE"})] = {**base, "r": r, "h": h, "alarms": alarms,
                                                           **(tag and {"qualification": B3A_ORACLE_LABEL})}
                adapters.append(("oracle", bundle["label"], B3B_AXIS[family]) if family else ("nonoracle", bundle["label"]))
    return want, adapters


def test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses(
        tmp_path, monkeypatch):
    import json
    fixture, state, setup_record, dev_record, context = _b3b_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    C, apps, fams = desc["campaign"], desc["scope"]["applications"], desc["scope"]["families"]
    paths = sorted((a, "path", C, *s, "CAL_NULL", i) for s in B2W_SETUPS for a in apps for i in range(39))
    metas = sorted(("RESIDUAL", "meta", C, *s, "CAL_NULL", f, i) for s in B2W_SETUPS for f in fams for i in range(39))
    want, expected = _b3b_expected(desc, setup_record, dev_record)
    main, ids = dev_record["derived"]["setups"][pdb.canon(B2W_SETUPS[1])]["RESIDUAL"], [
        (row["setup_id"], row["policy_id"], row.get("family")) for row in want.values()]
    assert {c[1:] for c in paths + metas} <= set(_kernel("seed_plan")(cfg, "full")["keys"]) and len(plan["CAL"]) == 4
    assert desc["sizes"]["CAL_NULL"] == 39 and pdb.predictive_rank(39, B3A_ALPHA) == 1
    assert apps == ["RESIDUAL", "MARKET"] and fams == ["F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"]
    assert set(B2V_ONLINE) <= set(desc["scope"]["policies"]) and not (staging / "phases" / "CAL.json").exists()
    policies = main["policies"]
    assert main["s2_status"] == "S2_DEV_EQUALS_COMMON" and all(r == policies["PRIMARY"][k] for k, r in policies["S2_DEV"].items())
    assert set(policies["GAMMA_M"]) == set(B2V_ONLINE) and all(
        policies["GAMMA_M"][k]["policy_id"] != policies["PRIMARY"][k]["policy_id"] for k in B2V_ONLINE)
    assert len(set(ids)) == len(ids) == len(expected) and sum(f is not None for *_, f in ids) == 4
    phase, calls, adapters = _kernel("cal_phase"), [], []
    with monkeypatch.context() as mp:
        _b3b_producers(mp, state, calls, adapters)
        record = phase(cfg, "full", context)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-4")
    assert sorted(c for c in calls if c[1] == "path") == paths and sorted(c for c in calls if c[1] == "meta") == metas
    assert len(calls) == len(paths) + len(metas) and sorted(adapters) == sorted(expected)
    upstream = {"SETUP": setup_record["phase_digest"], "DEV": dev_record["phase_digest"]}
    assert record == json.loads((staging / "phases" / "CAL.json").read_text()) and record["upstream"] == upstream
    assert [row["key"] for row in record["partitions"]] == plan["CAL"]
    verified_maxima_digests = set()
    for key in plan["CAL"]:
        _, n_rows, arrays = _kernel("_verify_partition")(staging, record["design_id"], upstream, key)
        assert n_rows == 39
        verified_maxima_digests.update(
            pdb.array_sha256(array)
            for array in arrays.values()
            if array.shape == (39,) and array.dtype == np.float64 and np.isfinite(array).all()
        )
    assert all(row["maxima_sha256"] in verified_maxima_digests for row in want.values())
    thresholds = record["derived"]["thresholds"]
    assert record["derived"]["rule"] == "predictive_exchangeable_rank_v2" and set(thresholds) == set(want)
    assert all({k: thresholds[cid].get(k) for k in row} == row and ("family" in thresholds[cid]) == ("family" in row)
               for cid, row in want.items())
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        again = phase(cfg, "full", renewed)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-5")
    after = _tree(staging)
    assert again == record and set(after) == set(before) and len(calls) == len(paths) + len(metas)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")
    _partition_stem(staging, record["design_id"], upstream, plan["CAL"][0]).with_suffix(".npz").write_bytes(b"damaged")
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        with pytest.raises(pdb.PartitionMismatch):
            phase(cfg, "full", renewed)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after and len(calls) == len(paths) + len(metas)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_cal_phase_refuses_a_missing_dev_predecessor_before_any_cal_producer_or_write(tmp_path, monkeypatch):
    fixture, state, setup_record, dev_record, context = _b3b_fixture(tmp_path, monkeypatch, dev=False)
    cfg, desc, authority, plan, staging = fixture
    assert dev_record is None and len(plan["CAL"]) == 4 and (staging / "phases" / "SETUP.json").exists()
    assert not any((staging / "phases" / f"{p}.json").exists() for p in ("DEV", "CAL", "NULL_PLAN", "HOLD", "ALT"))
    phase, before = _kernel("cal_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        with pytest.raises(pio().PhaseOrderError):
            phase(cfg, "full", context)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


B3C_LABELS = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128", "FULL_K")


def _b3c_Y(i):
    Y = np.zeros((6, 20))
    Y[1, 19] = 40.0 * i
    return Y


def _b3c_fixture(root, monkeypatch, cal):
    fixture, state, setup_record, dev_record, context = _b3b_fixture(root, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    plan["NULL_PLAN"] = [["NULL_PLAN", *desc["science"]["phi"]["setup"]]]
    cal_record = None
    if cal:
        with monkeypatch.context() as mp:
            _b3b_producers(mp, state, [], [])
            cal_record = _kernel("cal_phase")(cfg, "full", context)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-4")
    return fixture, state, setup_record, dev_record, cal_record, context


def _b3c_no_future_reads(mp, staging):
    from pathlib import Path

    banned = {(Path(staging) / "phases" / name).resolve() for name in ("HOLD.json", "ALT.json")}
    real_open = Path.open
    real_read_text = Path.read_text
    real_read_bytes = Path.read_bytes

    def _check(path):
        if Path(path).resolve() in banned:
            raise AssertionError(f"B3c future phase read: {path}")

    def guarded_open(self, mode="r", *args, **kwargs):
        if "r" in mode or "+" in mode:
            _check(self)
        return real_open(self, mode, *args, **kwargs)

    def guarded_read_text(self, *args, **kwargs):
        _check(self)
        return real_read_text(self, *args, **kwargs)

    def guarded_read_bytes(self, *args, **kwargs):
        _check(self)
        return real_read_bytes(self, *args, **kwargs)

    mp.setattr(Path, "open", guarded_open)
    mp.setattr(Path, "read_text", guarded_read_text)
    mp.setattr(Path, "read_bytes", guarded_read_bytes)


def _b3c_pair(alarm, j):
    return {"b": int((alarm[:, 0] & ~alarm[:, j]).sum()), "c": int((~alarm[:, 0] & alarm[:, j]).sum())}


def test_null_plan_phase_freezes_primary_p_conf_alarms_under_the_received_plan_rule_then_reloads(
        tmp_path, monkeypatch):
    import hashlib
    import inspect
    import json
    fixture, state, setup_record, dev_record, cal_record, context = _b3c_fixture(tmp_path, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    C, primary, module = desc["campaign"], desc["science"]["phi"]["setup"], pio()
    rule = cfg["modes"]["full"]["null_plan"]
    n, seed = rule["n_plan"], set(_kernel("seed_plan")(cfg, "full")["keys"])
    paths = [("path", C, *primary, "NULL_PLAN", i) for i in range(n)]
    others = {k for k in seed if k[0] == "path" and k[5] in ("CAL_NULL", "HOLD_NULL", "ALT")}
    assert set(paths) <= seed and not set(paths) & others and n == desc["null_plan"]["n_plan"] == 2
    assert primary == list(B2W_SETUPS[1]) and context["plan"] is plan and plan["NULL_PLAN"] == [["NULL_PLAN", *primary]]
    assert (staging / "phases" / "CAL.json").exists() and not (staging / "phases" / "NULL_PLAN.json").exists()
    assert B3C_LABELS == _kernel("P_CONF")
    meta = setup_record["derived"]["setups"][pdb.canon(primary)]["applications"]["RESIDUAL"]
    dev = dev_record["derived"]["setups"][pdb.canon(primary)]["RESIDUAL"]
    thresholds, Y = cal_record["derived"]["thresholds"], np.array([_b3c_Y(i) for i in range(n)])
    ids, hs, alarm = {}, {}, np.zeros((n, 3), dtype=bool)
    for j, label in enumerate(B3C_LABELS):
        pid = dev["policies"]["PRIMARY"][label]["policy_id"]
        [ids[label]] = [cid for cid, row in thresholds.items()
                        if (row["setup_id"], row["policy_id"], row.get("family")) == (meta["setup_id"], pid, None)]
        hs[label] = thresholds[ids[label]]["h"]
        bundle = _kernel("frozen_policy")(desc, "RESIDUAL", label, meta["baselines"],
                                          dev["library"] and dev["library"]["qbar"],
                                          dev["choices"] and dev["choices"]["d_dev"])
        alarm[:, j] = _kernel("nonoracle_scan")(Y, bundle, hs[label])["first"] > 0
    assert [[bool(v) for v in row] for row in alarm] == [[False, False, False], [False, False, True]]
    counts = {"n": n, "pairs": {"ONLINE_INFO_MIX_W128|ONLINE_PREFIX_MIX_W128": _b3c_pair(alarm, 1),
                                "ONLINE_INFO_MIX_W128|FULL_K": _b3c_pair(alarm, 2)},
              "alarms": {label: int(alarm[:, j].sum()) for j, label in enumerate(B3C_LABELS)}}
    args = {"counts": counts, "alpha": cfg["parameters"]["alpha"], "m": cfg["phi"]["m"], "eps": 0.01,
            "eps_v": cfg["null_status"]["eps_v"], "beta": rule["beta"], "eta": rule["eta"], "n_min": rule["n_min"],
            "n_cap": rule["n_cap"]}
    real_plan, real_scan, calls, scans, plans = module.plan_holdout, module.nonoracle_scan, [], [], []
    n_hold, status, details = real_plan(**args)
    content = {"cal_digest": cal_record["phase_digest"], "calibration_ids": ids, "counts": counts, "details": details,
               "status": status, "n_hold": n_hold}
    derived = {"status": status, "n_hold": n_hold, "plan_id": hashlib.sha256(pdb.canon(content).encode()).hexdigest()}

    def path(desc, frame, fit, application, key, delta=None):
        assert application == "RESIDUAL" and delta is None and tuple(key) in paths
        calls.append(tuple(key))
        return _b3c_Y(key[6])

    def scan(Y, bundle, h=None):
        scans.append((bundle["label"], h, np.array(Y)))
        return real_scan(Y, bundle, h)

    def planned(*a, **k):
        plans.append(dict(inspect.signature(real_plan).bind(*a, **k).arguments))
        return real_plan(*a, **k)

    phase = _kernel("null_plan_phase")
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, "direction_information", "calibrate_nonoracle", "calibrate_oracle", "oracle_scan")
        _b3c_no_future_reads(mp, staging)
        mp.setattr(module, "path_scores", path)
        mp.setattr(module, "nonoracle_scan", scan)
        mp.setattr(module, "plan_holdout", planned)
        record = phase(cfg, "full", context)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-5")
    assert sorted(calls) == sorted(paths) and len(calls) == n and plans == [args]
    assert [s[:2] for s in scans] == [(label, hs[label]) for label in B3C_LABELS]
    assert all(np.array_equal(s[2], Y) for s in scans)
    upstream = {"SETUP": setup_record["phase_digest"], "DEV": dev_record["phase_digest"],
                "CAL": cal_record["phase_digest"]}
    assert record == json.loads((staging / "phases" / "NULL_PLAN.json").read_text()) and record["upstream"] == upstream
    assert record["phase"] == "NULL_PLAN" and [row["key"] for row in record["partitions"]] == plan["NULL_PLAN"]
    assert record["derived"] == derived
    _, n_rows, arrays = _kernel("_verify_partition")(staging, record["design_id"], upstream, plan["NULL_PLAN"][0])
    assert n_rows == n and set(arrays) == {"alarm"} and arrays["alarm"].dtype == bool
    assert np.array_equal(arrays["alarm"], alarm)
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3c_no_future_reads(mp, staging)
        again = phase(cfg, "full", renewed)
    after = _tree(staging)
    assert again == record and set(after) == set(before) and (len(calls), len(scans)) == (n, 3)
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


def test_null_plan_phase_refuses_a_missing_cal_predecessor_before_any_null_plan_producer_or_write(
        tmp_path, monkeypatch):
    fixture, state, setup_record, dev_record, cal_record, context = _b3c_fixture(tmp_path, monkeypatch, False)
    cfg, desc, authority, plan, staging = fixture
    phases = staging / "phases"
    assert cal_record is None and dev_record is not None and setup_record is not None and context["plan"] is plan
    assert plan["NULL_PLAN"] == [["NULL_PLAN", *desc["science"]["phi"]["setup"]]] and len(plan["CAL"]) == 4
    assert (phases / "SETUP.json").exists() and (phases / "DEV.json").exists()
    assert not any((phases / f"{p}.json").exists() for p in ("CAL", "NULL_PLAN", "HOLD", "ALT"))
    phase, before = _kernel("null_plan_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED, "plan_holdout")
        with pytest.raises(pio().PhaseOrderError):
            phase(cfg, "full", context)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[name] == data for name, data in before.items() if name != "resources.json")


B3D_PRIOR = ("SETUP", "DEV", "CAL", "NULL_PLAN")


def _b3d_Y(i):
    Y = np.zeros((6, 20))
    Y[i, 0] = 40.0
    return Y


def _b3d_fixture(root, monkeypatch, null_plan):
    fixture, state, setup_record, dev_record, cal_record, context = _b3c_fixture(root, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    primary, apps = desc["science"]["phi"]["setup"], desc["scope"]["applications"]
    plan["HOLD"] = sorted((["HOLD_NULL", *s, app] for s in B2W_SETUPS for app in apps), key=pdb.canon)
    null_record = None
    if null_plan:
        def path(desc, frame, fit, application, key, delta=None):
            assert application == "RESIDUAL" and delta is None and list(key[2:6]) == [*primary, "NULL_PLAN"]
            return _b3c_Y(key[6])

        with monkeypatch.context() as mp:
            _b3b_guard(mp, state, "direction_information", "calibrate_nonoracle", "calibrate_oracle", "oracle_scan")
            mp.setattr(pio(), "path_scores", path)
            null_record = _kernel("null_plan_phase")(cfg, "full", context)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-5")
    return fixture, state, [setup_record, dev_record, cal_record, null_record], context


def _b3d_cells(desc, setup_record, dev_record, thresholds):
    frozen, gamma, cells = _kernel("frozen_policy"), _kernel("gamma_sensitivity_policy"), {}
    for s, app in itertools.product(B2W_SETUPS, desc["scope"]["applications"]):
        meta = setup_record["derived"]["setups"][pdb.canon(s)]["applications"][app]
        dev = dev_record["derived"]["setups"][pdb.canon(s)][app]
        families = [f for f in desc["scope"]["families"] if desc["science"]["families"][f]["application"] == app]
        for label in desc["scope"]["policies"]:
            bundle = frozen(desc, app, label, meta["baselines"], dev["library"] and dev["library"]["qbar"],
                            dev["choices"] and dev["choices"]["d_dev"])
            work = [(dev["policies"]["PRIMARY"][label], bundle)] if bundle["status"] == "RUNNABLE" else []
            work += [(row, gamma(desc, bundle)) for key, row in dev["policies"]["GAMMA_M"].items() if key == label]
            for row, item in work:
                for family in (families if item["policy"]["kind"] == "ORACLE" else [None]):
                    [cid] = [c for c, t in thresholds.items() if (t["setup_id"], t["policy_id"], t.get("family"))
                             == (meta["setup_id"], row["policy_id"], family)]
                    cells[cid] = (list(s), app, item, family)
    return cells


def _b3d_no_alt(mp, staging):
    from pathlib import Path

    banned = (Path(staging) / "phases" / "ALT.json").resolve()
    for name in ("open", "read_text", "read_bytes"):
        def guarded(self, *args, _real=getattr(Path, name), **kwargs):
            assert Path(self).resolve() != banned, f"B3d ALT content read: {self}"
            return _real(self, *args, **kwargs)

        mp.setattr(Path, name, guarded)


def _b3d_spies(mp, state, staging, ns, calls, scans, checks):
    module, phases = pio(), staging / "phases"
    real = {name: getattr(module, name) for name in ("nonoracle_scan", "oracle_scan", "null_status")}
    _b3b_guard(mp, state, "calibrate_nonoracle", "calibrate_oracle")
    _b3d_no_alt(mp, staging)

    def ready(setup, i):
        assert i < ns[pdb.canon(list(setup))] and not (phases / "HOLD.json").exists()
        assert all((phases / f"{p}.json").exists() for p in B3D_PRIOR)

    def path(desc, frame, fit, application, key, delta=None):
        assert key[0] == "path" and key[5] == "HOLD_NULL" and delta is None
        ready(key[2:5], key[6])
        calls.append((application, *key))
        return _b3d_Y(key[6])

    def information(desc, frame, fit, setup, application, key):
        assert key[0] == "meta" and key[5] == "HOLD_NULL" and list(key[2:5]) == list(setup)
        assert application == "RESIDUAL"
        ready(setup, key[7])
        calls.append((application, *key))
        return {"status": "SUPPORTED", "family": key[6], "support": None, "q": np.eye(20)[B3B_AXIS[key[6]]] / 2,
                "I_joint": 0.0, "delta": np.ones(key[3]), "oracle_basis": module.PROJECTION_ARMS[key[2]]}

    def scan(Y, bundle, h=None):
        scans.append((bundle["label"], h, -1, np.asarray(Y, dtype=np.float64).tobytes()))
        return real["nonoracle_scan"](Y, bundle, h)

    def oracle(Y, q_true, bundle, h=None):
        q = np.asarray(q_true)
        assert (q == q[0]).all()
        scans.append((bundle["label"], h, int(np.argmax(q[0])), np.asarray(Y, dtype=np.float64).tobytes()))
        return real["oracle_scan"](Y, q_true, bundle, h)

    def status(k, n, alpha, eps, tail):
        checks.append((k, n, alpha, eps, tail))
        return real["null_status"](k, n, alpha, eps, tail)

    for name, fake in (("path_scores", path), ("direction_information", information), ("nonoracle_scan", scan),
                       ("oracle_scan", oracle), ("null_status", status)):
        mp.setattr(module, name, fake)


def test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads(
        tmp_path, monkeypatch):
    import collections
    import json
    fixture, state, records, context = _b3d_fixture(tmp_path, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    setup_record, dev_record, cal_record, null_record = records
    C, apps, fams, module = desc["campaign"], desc["scope"]["applications"], desc["scope"]["families"], pio()
    primary, phases, H = desc["science"]["phi"]["setup"], staging / "phases", desc["science"]["parameters"]["H"]
    alpha, eps, la = (desc["science"]["parameters"]["alpha"], desc["science"]["null_status"]["eps_v"],
                      desc["science"]["null_status"]["tail"])
    ns = {pdb.canon(list(s)): null_record["derived"]["n_hold"] if list(s) == primary else desc["sizes"]["HOLD_NULL"]
          for s in B2W_SETUPS}
    assert null_record["derived"]["n_hold"] == 5 and list(ns.values()) == [1, 5] and len(plan["HOLD"]) == 4
    assert all((phases / f"{p}.json").exists() for p in B3D_PRIOR) and not (phases / "HOLD.json").exists()
    paths = sorted((a, "path", C, *s, "HOLD_NULL", i) for s in B2W_SETUPS for a in apps
                   for i in range(ns[pdb.canon(list(s))]))
    metas = sorted(("RESIDUAL", "meta", C, *s, "HOLD_NULL", f, i) for s in B2W_SETUPS for f in fams
                   for i in range(ns[pdb.canon(list(s))]))
    seed = _kernel("seed_plan")(cfg, "full")["keys"]
    roles = {r: {k for k in seed if k[0] in ("path", "meta") and k[5] == r}
             for r in ("CAL_NULL", "NULL_PLAN", "HOLD_NULL")}
    assert {c[1:] for c in paths + metas} == roles["HOLD_NULL"] and (len(paths), len(metas)) == (12, 12)
    assert all(roles[a] and not roles[a] & roles[b] for a, b in itertools.combinations(roles, 2))
    thresholds = cal_record["derived"]["thresholds"]
    cells = _b3d_cells(desc, setup_record, dev_record, thresholds)
    assert set(cells) == set(thresholds) and sum(cell[3] is not None for cell in cells.values()) == 4
    want, refs, scans_want, keyed = {}, {}, collections.Counter(), collections.defaultdict(set)
    for cid, (s, app, bundle, family) in cells.items():
        n, h = ns[pdb.canon(s)], thresholds[cid]["h"]
        Y = np.array([_b3d_Y(i) for i in range(n)])
        if family:
            refs[cid] = module.oracle_scan(Y, np.tile(np.eye(20)[B3B_AXIS[family]] / 2, (n, 1)), bundle, h)
        else:
            refs[cid] = module.nonoracle_scan(Y, bundle, h)
        k = int((refs[cid]["first"] > 0).sum())
        lo, hi = module.cp_bounds(k, n, la)
        status = "NULL_VALIDATED" if hi <= alpha + eps else "NULL_FAILED" if lo > alpha + eps else "NULL_INCONCLUSIVE"
        want[cid] = {"setup_id": thresholds[cid]["setup_id"], "policy_id": thresholds[cid]["policy_id"], "n": n,
                     "k": k, "lo": lo, "hi": hi, "status": status, **({"family": family} if family else {})}
        scans_want[(bundle["label"], h, B3B_AXIS[family] if family else -1, Y.tobytes())] += 1
        keyed[pdb.canon(["HOLD_NULL", *s, app])].add(cid)
    name = pdb.canon(primary)
    sid = setup_record["derived"]["setups"][name]["applications"]["RESIDUAL"]["setup_id"]
    pid = dev_record["derived"]["setups"][name]["RESIDUAL"]["policies"]["PRIMARY"]["FULL_K"]["policy_id"]
    [full] = [c for c, r in want.items() if (r["setup_id"], r["policy_id"], r.get("family")) == (sid, pid, None)]
    [head] = [c for c, r in want.items() if (r["setup_id"], r.get("family")) == (sid, "F_HEAD_RESIDUAL")]
    assert refs[full]["first"].tolist() == [1, 2, 3, 4, 5] and refs[head]["first"].tolist() == [-1] * 5
    assert [want[c]["k"] for c in (full, head)] == [5, 0] and la == 0.05
    assert [want[c]["status"] for c in (full, head)] == ["NULL_FAILED", "NULL_INCONCLUSIVE"]
    assert want[full]["lo"] == pytest.approx(la ** 0.2) and want[head]["hi"] == pytest.approx(1 - la ** 0.2)
    phase, calls, scans, checks = _kernel("hold_phase"), [], [], []
    with monkeypatch.context() as mp:
        _b3d_spies(mp, state, staging, ns, calls, scans, checks)
        record = phase(cfg, "full", context)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-6")
    assert sorted(c for c in calls if c[1] == "path") == paths and sorted(c for c in calls if c[1] == "meta") == metas
    assert len(calls) == len(paths) + len(metas) and collections.Counter(scans) == scans_want
    assert len(scans) == len(checks) == len(thresholds) and all(c[2:] == (alpha, eps, la) for c in checks)
    assert collections.Counter(c[:2] for c in checks) == collections.Counter((r["k"], r["n"]) for r in want.values())
    upstream = {p: r["phase_digest"] for p, r in zip(B3D_PRIOR, records)}
    assert record == json.loads((phases / "HOLD.json").read_text()) and record["upstream"] == upstream
    assert record["phase"] == "HOLD" and [row["key"] for row in record["partitions"]] == plan["HOLD"]
    assert [row["n_rows"] for row in record["partitions"]] == [ns[pdb.canon(key[1:4])] for key in plan["HOLD"]]
    assert set(keyed) == {pdb.canon(key) for key in plan["HOLD"]}
    for key in plan["HOLD"]:
        _, n_rows, arrays = _kernel("_verify_partition")(staging, record["design_id"], upstream, key)
        ids = keyed[pdb.canon(key)]
        assert n_rows == ns[pdb.canon(key[1:4])]
        assert set(arrays) == {f"{p}_{c}" for c in ids for p in ("first", "mask")}
        for cid in ids:
            first, mask = arrays["first_" + cid], arrays["mask_" + cid]
            assert first.dtype.kind == "i" and first.shape == (n_rows,) and np.array_equal(first, refs[cid]["first"])
            assert mask.dtype == np.uint32 and mask.shape == (n_rows, H)
            assert np.array_equal(mask, refs[cid]["mask_bits"])
    checked = record["derived"]["null_checks"]
    assert set(checked) == set(want)
    for cid, row in want.items():
        got = checked[cid]
        assert {field: got.get(field) for field in row} == row and ("family" in got) == ("family" in row)
        assert got.get("qualification") == ("NON_DEPLOYABLE" if "family" in row else None)
        assert type(got["n"]) is type(got["k"]) is int
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3d_no_alt(mp, staging)
        again = phase(cfg, "full", renewed)
    after = _tree(staging)
    assert again == record and set(after) == set(before) and len(calls) == len(paths) + len(metas)
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")
    assert not (phases / "ALT.json").exists()


def test_hold_phase_refuses_a_missing_null_plan_predecessor_before_any_hold_producer_or_write(
        tmp_path, monkeypatch):
    fixture, state, records, context = _b3d_fixture(tmp_path, monkeypatch, False)
    cfg, desc, authority, plan, staging = fixture
    phases = staging / "phases"
    assert records[3] is None and None not in records[:3] and context["plan"] is plan and len(plan["HOLD"]) == 4
    assert all((phases / f"{p}.json").exists() for p in B3D_PRIOR[:3])
    assert not any((phases / f"{p}.json").exists() for p in ("NULL_PLAN", "HOLD", "ALT"))
    phase, before = _kernel("hold_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED, "plan_holdout", "null_status", "cp_bounds")
        _b3d_no_alt(mp, staging)
        with pytest.raises(pio().PhaseOrderError):
            phase(cfg, "full", context)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")


B3E_PRIOR = (*B3D_PRIOR, "HOLD")
B3E_AXIS = {"F0_ISOTROPIC_RESIDUAL": 3, "F1_TAIL_RESIDUAL": 12}


def _b3e_scores():
    A, B = np.zeros((6, 20)), np.full((6, 20), 0.25)
    A[1, 0], B[2, 12], B[4, 7] = 40.0, 9.0, 40.0
    return A, B


def _b3e_Y(family, i):
    return _b3e_scores()[(i + DEV_FAMILIES.index(family)) % 2]


def _b3e_delta(N, family, i):
    return (1.0 + DEV_FAMILIES.index(family)) * np.linspace(1.0, 2.0, N) + 10.0 * i


def _b3e_arm(setup):
    return [s[0] for s in B2W_SETUPS].index(setup[0])


def _b3e_q(setup, family, i):
    return np.eye(20)[(B3B_AXIS[family] + 5 * _b3e_arm(setup) + i) % 20] / 2


def _b3e_joint(setup, family, i):
    return 0.125 + DEV_FAMILIES.index(family) + 0.5 * i + 10.0 * _b3e_arm(setup)


def _b3e_fixture(root, monkeypatch, hold):
    base = _design_cfg
    monkeypatch.setitem(globals(), "_design_cfg", lambda: _edited(base(), ("scope", "families"), list(DEV_FAMILIES)))
    monkeypatch.setitem(B2V_SIZES, "ALT", 2)
    for family, axis in B3E_AXIS.items():
        monkeypatch.setitem(B3B_AXIS, family, axis)
    fixture, state, records, context = _b3d_fixture(root, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    science, apps = desc["science"]["families"], desc["scope"]["applications"]
    plan["ALT"] = sorted((["ALT", *s, app, f] for s in B2W_SETUPS for app in apps for f in desc["scope"]["families"]
                          if science[f]["application"] == app), key=pdb.canon)
    hold_record, primary = None, desc["science"]["phi"]["setup"]
    if hold:
        ns = {pdb.canon(list(s)): records[3]["derived"]["n_hold"] if list(s) == primary else desc["sizes"]["HOLD_NULL"]
              for s in B2W_SETUPS}
        with monkeypatch.context() as mp:
            _b3d_spies(mp, state, staging, ns, [], [], [])
            hold_record = _kernel("hold_phase")(cfg, "full", context)
            context = _kernel("start_invocation")(staging, authority, plan, "invocation-6")
    return fixture, state, [*records, hold_record], context


def _b3e_spies(mp, state, staging, calls, scans):
    module, phases = pio(), staging / "phases"
    real = {name: getattr(module, name) for name in ("nonoracle_scan", "oracle_scan")}
    _b3b_guard(mp, state, "calibrate_nonoracle", "calibrate_oracle")

    def ready():
        assert all((phases / f"{p}.json").exists() for p in B3E_PRIOR) and not (phases / "ALT.json").exists()

    def information(desc, frame, fit, setup, application, key):
        assert type(key) is tuple and len(key) == 8 and key[0] == "meta" and key[5] == "ALT"
        assert list(key[2:5]) == list(setup) and application == "RESIDUAL" and key[6] in DEV_FAMILIES
        ready()
        calls.append((application, *key))
        family, i = key[6], key[7]
        return {"status": "SUPPORTED", "family": family, "support": None, "q": _b3e_q(setup, family, i),
                "I_joint": _b3e_joint(setup, family, i), "delta": _b3e_delta(key[3], family, i),
                "oracle_basis": module.PROJECTION_ARMS[key[2]]}

    def path(desc, frame, fit, application, key, delta=None):
        assert type(key) is tuple and len(key) == 7 and key[0] == "path" and key[5] == "ALT"
        raw = np.asarray(delta, dtype=np.float64)
        assert raw.shape == (key[3],) and np.isfinite(raw).all()
        [(family, i)] = [(f, j) for f in DEV_FAMILIES for j in range(B2V_SIZES["ALT"])
                         if _b3e_delta(key[3], f, j).tobytes() == raw.tobytes()]
        assert i == key[6]
        ready()
        calls.append((application, *key, family))
        return _b3e_Y(family, i)

    def scan(Y, bundle, h):
        assert h is not None
        scans.append((bundle["label"], h, b"", np.asarray(Y, dtype=np.float64).tobytes()))
        return real["nonoracle_scan"](Y, bundle, h)

    def oracle(Y, q_true, bundle, h):
        assert h is not None
        scans.append((bundle["label"], h, np.asarray(q_true, dtype=np.float64).tobytes(),
                      np.asarray(Y, dtype=np.float64).tobytes()))
        return real["oracle_scan"](Y, q_true, bundle, h)

    for name, fake in (("path_scores", path), ("direction_information", information), ("nonoracle_scan", scan),
                       ("oracle_scan", oracle)):
        mp.setattr(module, name, fake)


def test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads(
        tmp_path, monkeypatch):
    import collections
    import json
    fixture, state, records, context = _b3e_fixture(tmp_path, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    setup_record, dev_record, cal_record, null_record, hold_record = records
    C, apps, fams, module = desc["campaign"], desc["scope"]["applications"], desc["scope"]["families"], pio()
    phases, H, n = staging / "phases", desc["science"]["parameters"]["H"], desc["sizes"]["ALT"]
    assert apps == ["RESIDUAL", "MARKET"] and sorted(fams) == sorted(DEV_FAMILIES) and (n, H) == (2, 6)
    assert all(desc["science"]["families"][f]["application"] == "RESIDUAL" for f in fams)
    assert context["plan"] is plan and len(plan["ALT"]) == 8
    assert plan["ALT"] == sorted((["ALT", *s, "RESIDUAL", f] for s in B2W_SETUPS for f in fams), key=pdb.canon)
    assert all((phases / f"{p}.json").exists() for p in B3E_PRIOR) and not (phases / "ALT.json").exists()
    upstream = {p: r["phase_digest"] for p, r in zip(B3E_PRIOR, records)}
    assert all(r == json.loads((phases / f"{p}.json").read_text()) for p, r in zip(B3E_PRIOR, records))
    assert hold_record["upstream"] == {p: upstream[p] for p in B3D_PRIOR}
    assert null_record["upstream"] == {p: upstream[p] for p in B3D_PRIOR[:3]}
    assert [row["key"] for row in hold_record["partitions"]] == plan["HOLD"]
    seed = _kernel("seed_plan")(cfg, "full")["keys"]
    metas = sorted(("RESIDUAL", "meta", C, *s, "ALT", f, i) for s in B2W_SETUPS for f in fams for i in range(n))
    paths = sorted(("RESIDUAL", "path", C, *s, "ALT", i, f) for s in B2W_SETUPS for f in fams for i in range(n))
    roles = {r: {k for k in seed if k[0] in ("path", "meta") and k[5] == r}
             for r in ("DEV_NULL", "DEV_ALT", "CAL_NULL", "NULL_PLAN", "HOLD_NULL", "ALT")}
    assert {c[1:] for c in metas} | {c[1:-1] for c in paths} == roles["ALT"] and len(roles["ALT"]) == 20
    assert all(not roles[a] & roles[b] for a, b in itertools.combinations(roles, 2))
    for s in B2W_SETUPS:
        head = setup_record["derived"]["setups"][pdb.canon(s)]["applications"]["RESIDUAL"]["head"]
        assert head["status"] in ("GEOMETRY_ALIGNED", "DESIGN_CONTROL_INCONCLUSIVE") and isinstance(head["geometry"], dict)
    thresholds, checks = cal_record["derived"]["thresholds"], hold_record["derived"]["null_checks"]
    cells = _b3d_cells(desc, setup_record, dev_record, thresholds)
    assert set(cells) == set(thresholds) == set(checks) and "NULL_FAILED" in {r["status"] for r in checks.values()}
    assert collections.Counter(c[3] for c in cells.values() if c[3]) == collections.Counter({f: 2 for f in fams})
    assert module.PROJECTION_ARMS["EXACT"] == "EXACT_ADDITIVE_KL"
    assert module.PROJECTION_ARMS["FITTED_LW_GAUSSIAN"] == "ORACLE_DIAGONAL_SURROGATE"
    want, keyed, refs, joint, scans_want, shared = {}, {}, {}, {}, collections.Counter(), {}
    for key in plan["ALT"]:
        s, app, family, k = key[1:4], key[4], key[5], pdb.canon(key)
        Y = np.array([_b3e_Y(family, i) for i in range(n)])
        Q = np.array([_b3e_q(s, family, i) for i in range(n)])
        meta = setup_record["derived"]["setups"][pdb.canon(s)]["applications"][app]
        keyed[k] = sorted(c for c, cell in cells.items() if cell[0] == s and cell[1] == app and cell[3] in (None, family))
        free = sorted(c for c in keyed[k] if cells[c][3] is None)
        assert shared.setdefault(pdb.canon(s), free) == free and len(keyed[k]) == len(free) + 1
        want[k] = {"setup_id": meta["setup_id"], "family": family, "oracle_basis": module.PROJECTION_ARMS[s[0]]}
        joint[k] = np.array([_b3e_joint(s, family, i) for i in range(n)])
        for cid in keyed[k]:
            bundle, h = cells[cid][2], thresholds[cid]["h"]
            if cells[cid][3]:
                refs[k, cid] = module.oracle_scan(Y, Q, bundle, h)
                scans_want[(bundle["label"], h, Q.tobytes(), Y.tobytes())] += 1
            else:
                refs[k, cid] = module.nonoracle_scan(Y, bundle, h)
                scans_want[(bundle["label"], h, b"", Y.tobytes())] += 1
    nonoracle = [refs[k, c] for k in keyed for c in keyed[k] if cells[c][3] is None]
    assert any((r["first"] > 0).any() for r in nonoracle) and any(r["first"][0] != r["first"][1] for r in nonoracle)
    for s in B2W_SETUPS:
        even, odd = (pdb.canon(["ALT", *s, "RESIDUAL", f]) for f in DEV_FAMILIES[:2])
        assert all(refs[even, c][field][::-1].tobytes() == refs[odd, c][field].tobytes()
                   for c in shared[pdb.canon(s)] for field in ("first", "mask_bits"))
    phase, calls, scans = _kernel("alt_phase"), [], []
    with monkeypatch.context() as mp:
        _b3e_spies(mp, state, staging, calls, scans)
        record = phase(cfg, "full", context)
        renewed = _kernel("start_invocation")(staging, authority, plan, "invocation-7")
    assert sorted(c for c in calls if c[1] == "meta") == metas and sorted(c for c in calls if c[1] == "path") == paths
    assert len(calls) == len(metas) + len(paths) and collections.Counter(scans) == scans_want
    assert record == json.loads((phases / "ALT.json").read_text()) and record["upstream"] == upstream
    assert record["phase"] == "ALT" and [row["key"] for row in record["partitions"]] == plan["ALT"]
    assert [row["n_rows"] for row in record["partitions"]] == [n] * len(plan["ALT"])
    trials = record["derived"]["trials"]
    assert set(trials) == set(want)
    for k, row in want.items():
        got = trials[k]
        assert {field: got.get(field) for field in row} == row and type(got["calibration_ids"]) is list
        assert sorted(got["calibration_ids"]) == keyed[k] and len(got["calibration_ids"]) == len(keyed[k])
        assert not {"Y", "q", "delta"} & set(got)
    stored = {}
    for key in plan["ALT"]:
        k = pdb.canon(key)
        _, n_rows, arrays = _kernel("_verify_partition")(staging, record["design_id"], upstream, key)
        assert n_rows == n and set(arrays) == {"I_joint", *(f"{p}_{c}" for c in keyed[k] for p in ("first", "mask"))}
        assert arrays["I_joint"].dtype == np.float64 and np.array_equal(arrays["I_joint"], joint[k])
        for cid in keyed[k]:
            first, mask = arrays["first_" + cid], arrays["mask_" + cid]
            assert first.dtype.kind == "i" and first.shape == (n,) and np.array_equal(first, refs[k, cid]["first"])
            assert mask.dtype == np.uint32 and mask.shape == (n, H) and np.array_equal(mask, refs[k, cid]["mask_bits"])
        stored[k] = arrays
    for s in B2W_SETUPS:
        even, odd = (stored[pdb.canon(["ALT", *s, "RESIDUAL", f])] for f in DEV_FAMILIES[:2])
        assert all(even[p + c][::-1].tobytes() == odd[p + c].tobytes()
                   for c in shared[pdb.canon(s)] for p in ("first_", "mask_"))
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        again = phase(cfg, "full", renewed)
    after = _tree(staging)
    assert again == record and set(after) == set(before) and len(calls) == len(metas) + len(paths)
    assert len(scans) == sum(scans_want.values())
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")


def test_alt_phase_refuses_a_missing_hold_predecessor_before_any_alt_producer_or_write(tmp_path, monkeypatch):
    fixture, state, records, context = _b3e_fixture(tmp_path, monkeypatch, False)
    cfg, desc, authority, plan, staging = fixture
    phases = staging / "phases"
    assert records[4] is None and None not in records[:4] and context["plan"] is plan and len(plan["ALT"]) == 8
    assert all((phases / f"{p}.json").exists() for p in B3D_PRIOR)
    assert not any((phases / f"{p}.json").exists() for p in ("HOLD", "ALT"))
    phase, before = _kernel("alt_phase"), _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        with pytest.raises(pio().PhaseOrderError):
            phase(cfg, "full", context)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")


B3F_H, B3F_TAIL = 250, 0.05 / 3
B3F_P = ("ONLINE_INFO_MIX_W128", "ONLINE_PREFIX_MIX_W128", "FULL_K")
B3F_F2, B3F_HEAD = "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"
B3F_ATT, B3F_NOM = "CONFIRMED_AT_ATTAINED_COMPARABLE_FPR", "CONFIRMED_AT_COMMON_NOMINAL_ALPHA_ONLY"
B3F_NE, B3F_INV, B3F_NP = "NOT_ESTABLISHED", "INVALID_NULL_FAILED", "NONINFERIORITY_NOT_PROBATIVE"


def _b3f_geom(low=0.8, positive=True):
    return {"all_I_E_positive": positive, "summary": {"f_E": {"min": low, "mean": max(low, 0.9), "max": 1.0},
                                                       "f_pop": {"min": 0.5, "mean": 0.7, "max": 0.9}}}


def _b3f_pct(values, q):
    s = sorted(float(v) for v in values)
    pos = q * (len(s) - 1)
    k = min(math.floor(pos), len(s) - 1)
    return s[k] + (pos - k) * (s[min(k + 1, len(s) - 1)] - s[k])


def _b3f_t(first):
    first = np.asarray(first)
    return np.where(first == -1, B3F_H, first).astype(np.float64)


def _b3f_desc(B):
    return _kernel("design_descriptor")(_edited(_design_cfg(), ("bootstrap", "B"), B), "full")


def _b3f_inputs(n_hold, f2, head, n_alt=4, B=5):
    hold = np.full(n_hold, -1, dtype=np.int64)
    hold[::40] = 17
    hold[1:2] = B3F_H
    alt = {B3F_F2: {p: np.full(n_alt, v, dtype=np.int64) for p, v in zip(B3F_P, f2)},
           B3F_HEAD: {p: np.full(n_alt, v, dtype=np.int64) for p, v in zip(B3F_P[:2], head)}}
    boot = {fam: np.array([[(b + k * i) % n_alt for i in range(n_alt)] for b in range(B)], dtype=np.int64)
            for fam, k in ((B3F_F2, 1), (B3F_HEAD, 3))}
    return {p: hold.copy() for p in B3F_P}, alt, dict.fromkeys(B3F_P, "NULL_VALIDATED"), boot


def _b3f_seal(monkeypatch):
    import builtins

    def trap(*args, **kwargs):
        raise AssertionError("B3f inference must not read files or draw random numbers")

    for owner, name in ((builtins, "open"), (np, "load"), (np.random, "default_rng"), (np.random, "choice"),
                        (np.random, "randint"), (np.random, "random"), (np.random, "seed")):
        monkeypatch.setattr(owner, name, trap)


@pytest.mark.parametrize("u, low, positive, geometry_status, prefix_status", [
    (200.0, 0.8, True, "GEOMETRY_ALIGNED", "PREFIX_DETECTABLE"),
    (float(np.nextafter(200.0, np.inf)), 0.8, True, "GEOMETRY_ALIGNED", "PREFIX_DETECTABILITY_NOT_ESTABLISHED"),
    (200.0, float(np.nextafter(0.8, 0.0)), True, "DESIGN_CONTROL_INCONCLUSIVE", "PREFIX_DETECTABLE"),
    (1.0, 1.0, False, "DESIGN_CONTROL_INCONCLUSIVE", "PREFIX_DETECTABLE"),
    (250.0, 0.5, True, "DESIGN_CONTROL_INCONCLUSIVE", "PREFIX_DETECTABILITY_NOT_ESTABLISHED"),
], ids=["both_at_threshold", "u_nextafter_above", "f_E_nextafter_below", "I_E_not_positive", "both_fail"])
def test_b3f_head_control_exact_thresholds_and_nextafter(monkeypatch, u, low, positive, geometry_status,
                                                         prefix_status):
    import copy
    assert 0.8 * B3F_H == 200.0 and float(np.nextafter(200.0, np.inf)) > 0.8 * B3F_H
    assert float(np.nextafter(0.8, 0.0)) < 0.8
    assert (positive and low >= 0.8) is (geometry_status == "GEOMETRY_ALIGNED")
    assert (u <= 0.8 * B3F_H) is (prefix_status == "PREFIX_DETECTABLE")
    geometry = _b3f_geom(low, positive)
    frozen = copy.deepcopy(geometry)
    control = _kernel("head_control")
    _b3f_seal(monkeypatch)
    out = control(u, geometry, 0.8, 0.8, B3F_H)
    assert (out["geometry_status"], out["prefix_status"]) == (geometry_status, prefix_status)
    assert out["valid"] is (geometry_status == "GEOMETRY_ALIGNED" and prefix_status == "PREFIX_DETECTABLE")
    assert geometry == frozen


B3F_HEAD_CASES = {
    "T63_all_head_paths_censored": (2000, (-1, -1), {}, True, B3F_NP, B3F_ATT, B3F_ATT),
    "T66_valid_control_info_slower": (2000, (150, 100), {}, True, B3F_NE, B3F_ATT, B3F_ATT),
    "T67_attained_zero_discordance_n2000": (2000, (50, 100), {}, True, B3F_ATT, B3F_ATT, B3F_ATT),
    "T67_nominal_zero_discordance_n1": (1, (50, 100), {}, True, B3F_NOM, B3F_NOM, B3F_NOM),
    "T67_prefix_rmst_at_kappa_det_H": (2000, (100, 200), {}, True, B3F_ATT, B3F_ATT, B3F_ATT),
    "T67_inconclusive_nulls_do_not_block": (2000, (50, 100), dict.fromkeys(B3F_P, "NULL_INCONCLUSIVE"), True,
                                            B3F_ATT, B3F_ATT, B3F_ATT),
    "T67_info_null_failed": (2000, (50, 100), {B3F_P[0]: "NULL_FAILED"}, True, B3F_INV, B3F_INV, B3F_INV),
    "T67_prefix_null_failed": (2000, (50, 100), {B3F_P[1]: "NULL_FAILED"}, True, B3F_INV, B3F_INV, B3F_ATT),
    "T67_preconditions_false": (2000, (50, 100), {}, False, B3F_INV, B3F_INV, B3F_INV),
}


@pytest.mark.parametrize("case", list(B3F_HEAD_CASES))
def test_b3f_head_claim_statuses_null_qualification_and_multiplicity(monkeypatch, case):
    from scipy.stats import norm
    n, head, nulls, pre, h2, h1, h3 = B3F_HEAD_CASES[case]
    rm_i, rm_p = (float(B3F_H if v == -1 else v) for v in head)
    ni, u, z2 = rm_i - 1.1 * rm_p, rm_p, float(norm.isf(B3F_TAIL)) ** 2
    ci = tuple(_kernel("tango_interval")(0, 0, n, B3F_TAIL))
    equivalent = -0.01 <= ci[0] and ci[1] <= 0.01
    assert ci == pytest.approx((-z2 / (n + z2), z2 / (n + z2)), rel=1e-12) and equivalent is (n == 2000)
    confirmed = B3F_ATT if equivalent else B3F_NOM
    failed = {p for p, s in nulls.items() if s == "NULL_FAILED"}
    pair_ok = pre and not failed & set(B3F_P[:2])
    assert h2 == (B3F_INV if not pair_ok else B3F_NE if ni >= 0 else B3F_NP if u > 0.8 * B3F_H else confirmed)
    assert h1 == (confirmed if pair_ok else B3F_INV)
    assert h3 == (confirmed if pre and not failed & {B3F_P[0], B3F_P[2]} else B3F_INV)
    assert head != (-1, -1) or (ni == pytest.approx(-0.1 * B3F_H) and u == B3F_H)
    hold, alt, states, boot = _b3f_inputs(n, (50, 100, 100), head)
    states.update(nulls)
    desc, geometry = _b3f_desc(5), _b3f_geom()
    infer, control = _kernel("confirmatory_inference"), _kernel("head_control")
    _b3f_seal(monkeypatch)
    out = infer(desc, hold, alt, states, boot, geometry, preconditions=pre)
    assert set(out) == {"H1", "H2", "H3"}
    row = out["H2"]
    assert (row["ni_upper"], row["u_prefix"]) == pytest.approx((ni, u), abs=1e-9)
    assert row["control"] == control(u, geometry, 0.8, 0.8, B3F_H)
    assert row["control"]["valid"] is (u <= 0.8 * B3F_H)
    assert (row["rmst_info"], row["rmst_comparator"], row["rmst_difference"]) == pytest.approx(
        (rm_i, rm_p, rm_i - rm_p), abs=1e-9)
    assert tuple(row["rmst_ci"]) == pytest.approx((rm_i - rm_p, rm_i - rm_p), abs=1e-9)
    for key, family, status in (("H1", B3F_F2, h1), ("H2", B3F_HEAD, h2), ("H3", B3F_F2, h3)):
        r = out[key]
        assert r["status"] == status, key
        assert (r["family"], r["m"], r["deff"], r["coverage_claim"]) == (family, 3, 1, "NONE_FINITE"), key
        assert r["tail"] == pytest.approx(B3F_TAIL, rel=1e-15), key
        labels = {v for v in r.values() if isinstance(v, str)}
        assert {"BOOTSTRAP_PERCENTILE_APPROX", "TANGO_SCORE_ASYMPTOTIC"} <= labels, key
        assert r["fpr_delta"] == 0.0 and tuple(r["fpr_ci"]) == pytest.approx(ci, rel=1e-12), key
        assert r["fpr_equivalent"] is equivalent, key
    assert (out["H1"]["gain_bound"], out["H3"]["gain_bound"]) == pytest.approx((50.0, 50.0), abs=1e-9)


@pytest.mark.parametrize("variant, kept", [("f2_prefix_slower", ("H2", "H3")), ("head_data", ("H1", "H3")),
                                           ("full_k_alt", ("H1", "H2")), ("full_k_hold", ("H1", "H2"))])
def test_b3f_full_k_claim_not_gated_and_family_data_isolated(monkeypatch, variant, kept):
    base_inputs = _b3f_inputs(2000, (100, 50, 200), (50, 100))
    hold, alt, states, boot = _b3f_inputs(2000, (100, 50, 200), (50, 100))
    assert 50.0 - 100.0 < 0.0 < 200.0 - 100.0 and 50.0 - 1.1 * 100.0 < 0.0 and 100.0 <= 0.8 * B3F_H
    if variant == "f2_prefix_slower":
        alt[B3F_F2][B3F_P[1]][:] = 150
    elif variant == "head_data":
        alt[B3F_HEAD][B3F_P[0]] = np.array([40, 150, -1, 250], dtype=np.int64)
        boot[B3F_HEAD] = np.array([[(b * i + 1) % 4 for i in range(4)] for b in range(5)], dtype=np.int64)
    elif variant == "full_k_alt":
        alt[B3F_F2][B3F_P[2]] = np.array([10, -1, 250, 30], dtype=np.int64)
    else:
        hold[B3F_P[2]][2:7] = 5
    changed = {"f2_prefix_slower": ("H1", "gain_bound", 50.0), "head_data": ("H2", "rmst_info", 172.5),
               "full_k_alt": ("H3", "rmst_comparator", 135.0), "full_k_hold": ("H3", "fpr_delta", -5 / 2000)}[variant]
    desc, geometry = _b3f_desc(5), _b3f_geom()
    infer = _kernel("confirmatory_inference")
    _b3f_seal(monkeypatch)
    base = infer(desc, *base_inputs, geometry)
    new = infer(desc, hold, alt, states, boot, geometry)
    assert [base[k]["status"] for k in ("H1", "H2", "H3")] == [B3F_NE, B3F_ATT, B3F_ATT]
    assert (base["H1"]["gain_bound"], base["H1"]["rmst_difference"]) == pytest.approx((-50.0, 50.0), abs=1e-9)
    assert (base["H3"]["gain_bound"], base["H3"]["rmst_difference"]) == pytest.approx((100.0, -100.0), abs=1e-9)
    assert base["H1"]["family"] == base["H3"]["family"] == B3F_F2 and base["H2"]["family"] == B3F_HEAD
    for key in kept:
        np.testing.assert_equal(new[key], base[key], err_msg=f"{variant} changed {key}")
    assert new[changed[0]][changed[1]] == pytest.approx(changed[2], abs=1e-9)
    assert variant != "f2_prefix_slower" or new["H1"]["status"] == B3F_ATT


def test_b3f_paired_bootstrap_bounds_follow_each_family_shared_index_matrix(monkeypatch):
    import copy
    tango, tail = _kernel("tango_interval"), B3F_TAIL
    idx = np.array([[0, 1, 2, 3, 4, 5], [0, 0, 1, 1, 2, 2], [5, 5, 5, 4, 4, 3], [2, 3, 2, 3, 0, 1],
                    [1, 4, 1, 4, 5, 5], [3, 3, 3, 3, 3, 3], [4, 0, 5, 1, 2, 0]], dtype=np.int64)
    boot = {B3F_HEAD: idx, B3F_F2: (idx + 1) % 6}
    raw = {B3F_F2: ([5, 20, -1, 8, 250, 15], [9, -1, 40, 30, 250, 60], [-1, 35, 70, 12, 100, 18]),
           B3F_HEAD: ([12, -1, 250, 40, 7, 199], [30, 60, -1, 25, 250, 110])}
    alt = {f: {p: np.array(v, dtype=np.int64) for p, v in zip(B3F_P, vals)} for f, vals in raw.items()}
    hold = {p: np.array(v, dtype=np.int64) for p, v in zip(B3F_P, ([-1, 3, -1, -1, 250, -1, -1, 7, -1, -1],
                                                                  [-1, -1, -1, -1, 250, -1, 9, 7, -1, -1],
                                                                  [1, 3, -1, -1, -1, -1, -1, -1, -1, -1]))}
    t = {(f, p): _b3f_t(a) for f in alt for p, a in alt[f].items()}

    def rows(x, family):
        return x[boot[family]].mean(axis=1)

    ti, tp = t[(B3F_HEAD, B3F_P[0])], t[(B3F_HEAD, B3F_P[1])]
    ni_rows, u_rows = rows(ti - 1.1 * tp, B3F_HEAD), rows(tp, B3F_HEAD)
    ni, u = _b3f_pct(ni_rows, 1 - tail), _b3f_pct(u_rows, 1 - tail)
    assert (ni, u) == pytest.approx((np.quantile(ni_rows, 1 - tail), np.quantile(u_rows, 1 - tail)), rel=1e-12)
    assert ni > 1.0 and u < 0.8 * B3F_H - 1.0 < _b3f_pct(rows(tp, B3F_F2), 1 - tail)
    ind = {p: hold[p] != -1 for p in B3F_P}
    expect = {}
    for key, family, comp in (("H1", B3F_F2, B3F_P[1]), ("H2", B3F_HEAD, B3F_P[1]), ("H3", B3F_F2, B3F_P[2])):
        a, c = t[(family, B3F_P[0])], t[(family, comp)]
        diff = rows(a - c, family)
        b_, c_ = int((ind[B3F_P[0]] & ~ind[comp]).sum()), int((~ind[B3F_P[0]] & ind[comp]).sum())
        expect[key] = {"rmst_info": a.mean(), "rmst_comparator": c.mean(), "rmst_difference": a.mean() - c.mean(),
                       "rmst_ci": (_b3f_pct(diff, 0.025), _b3f_pct(diff, 0.975)), "fpr_delta": (b_ - c_) / 10,
                       "fpr_ci": tuple(tango(b_, c_, 10, tail)), "bc": (b_, c_)}
        if key != "H2":
            expect[key]["gain_bound"] = _b3f_pct(rows(c - a, family), tail)
    assert [expect[k]["bc"] for k in ("H1", "H2", "H3")] == [(1, 1), (1, 1), (2, 1)]
    assert expect["H1"]["gain_bound"] < -1.0 and expect["H3"]["gain_bound"] < -1.0
    assert not any(-0.01 <= e["fpr_ci"][0] and e["fpr_ci"][1] <= 0.01 for e in expect.values())
    desc, geometry = _b3f_desc(7), _b3f_geom()
    frozen = copy.deepcopy((hold, alt, boot, geometry))
    infer = _kernel("confirmatory_inference")
    _b3f_seal(monkeypatch)
    out = infer(desc, hold, alt, dict.fromkeys(B3F_P, "NULL_VALIDATED"), boot, geometry)
    np.testing.assert_equal((hold, alt, boot, geometry), frozen)
    for key, e in expect.items():
        r = out[key]
        assert r["status"] == B3F_NE and r["fpr_equivalent"] is False, key
        for name in ("rmst_info", "rmst_comparator", "rmst_difference", "fpr_delta", "gain_bound"):
            assert name not in e or r[name] == pytest.approx(e[name], abs=1e-9), (key, name)
        for name in ("rmst_ci", "fpr_ci"):
            assert tuple(r[name]) == pytest.approx(e[name], abs=1e-9), (key, name)
    h2 = out["H2"]
    assert (h2["ni_upper"], h2["u_prefix"]) == pytest.approx((ni, u), abs=1e-9)
    assert (h2["control"]["geometry_status"], h2["control"]["prefix_status"], h2["control"]["valid"]) == (
        "GEOMETRY_ALIGNED", "PREFIX_DETECTABLE", True)


def test_b3f_t67_ni_upper_exact_zero_boundary_is_not_established(monkeypatch):
    hold, alt, states, boot = _b3f_inputs(2000, (50, 100, 100), (55, 50))
    info, prefix, idx = alt[B3F_HEAD][B3F_P[0]], alt[B3F_HEAD][B3F_P[1]], boot[B3F_HEAD]
    assert idx.shape == (5, 4) and int(idx.min()) >= 0 and int(idx.max()) < 4
    assert 10 * 55 - 11 * 50 == 0 and 55.0 - 1.1 * 50.0 < 0.0
    tenths = 10 * info[idx] - 11 * prefix[idx]
    assert tenths.dtype == np.int64 and not tenths.any()
    assert set(prefix[idx].ravel().tolist()) == {50} and 50 <= 0.8 * B3F_H
    desc, geometry = _b3f_desc(5), _b3f_geom()
    infer = _kernel("confirmatory_inference")
    _b3f_seal(monkeypatch)
    row = infer(desc, hold, alt, states, boot, geometry)["H2"]
    assert row["ni_upper"] == 0.0
    assert row["u_prefix"] == 50.0
    assert row["control"]["valid"] is True
    assert row["status"] == B3F_NE


B3G_B = 7
B3G_CLAIMS = {"H1": (B3F_F2, B3F_P[1]), "H2": (B3F_HEAD, B3F_P[1]), "H3": (B3F_F2, B3F_P[2])}
B3G_SIDE = ("publish", "finalize", "finalize_planned", "export_selections")
B3G_POISON = {"alt_record_absent": "PhaseOrderError", "alt_payload_poisoned": "PartitionMismatch",
              "alt_payload_missing": "PartitionMismatch", "hold_payload_poisoned": "PartitionMismatch"}


def _b3g_fixture(root, monkeypatch):
    base = _design_cfg
    monkeypatch.setitem(globals(), "_design_cfg", lambda: _edited(base(), ("bootstrap", "B"), B3G_B))
    fixture, state, records, context = _b3e_fixture(root, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    with monkeypatch.context() as mp:
        _b3e_spies(mp, state, staging, [], [])
        alt_record = _kernel("alt_phase")(cfg, "full", context)
        context = _kernel("start_invocation")(staging, authority, plan, "invocation-7")
    return fixture, state, [*records, alt_record], context


def _b3g_forbid(mp, *names):
    def forbidden(*args, **kwargs):
        raise AssertionError("B3g confirmatory staging reached a forbidden kernel, side effect or global PRNG")

    class ForbiddenRandomState(np.random.RandomState):
        def __new__(cls, *args, **kwargs):
            forbidden()

    for name in names:
        mp.setattr(pio(), name, forbidden)
    for name in ("random", "randint", "choice", "permutation", "shuffle", "standard_normal"):
        mp.setattr(np.random, name, forbidden)
    mp.setattr(np.random, "RandomState", ForbiddenRandomState)


def _b3g_references(fixture, records):
    import json
    cfg, desc, authority, plan, staging = fixture
    setup_record, dev_record, cal_record, null_record, hold_record, alt_record = records
    names, phases, did = _kernel("PHASES"), staging / "phases", _kernel("design_id")(desc)
    primary, C, verify = desc["science"]["phi"]["setup"], desc["campaign"], _kernel("_verify_partition")
    assert primary == list(B2W_SETUPS[1]) and primary[0] == "FITTED_LW_GAUSSIAN" and len(records) == len(names)
    assert all(r == json.loads((phases / f"{p}.json").read_text()) and r["design_id"] == did
               for p, r in zip(names, records))
    ups = {p: {q: r["phase_digest"] for q, r in zip(names[:i], records)} for i, p in enumerate(names)}
    assert all(r["phase"] == p and r["upstream"] == ups[p] for p, r in zip(names, records))
    name, other = pdb.canon(primary), pdb.canon(B2W_SETUPS[0])
    meta = setup_record["derived"]["setups"][name]["applications"]["RESIDUAL"]
    policies = dev_record["derived"]["setups"][name]["RESIDUAL"]["policies"]
    thresholds, checks = cal_record["derived"]["thresholds"], hold_record["derived"]["null_checks"]

    def free(setup_id, policy_id):
        return [c for c, t in thresholds.items()
                if (t["setup_id"], t["policy_id"], t.get("family")) == (setup_id, policy_id, None)]

    sid, cids = meta["setup_id"], {}
    for p in B3F_P:
        pid = policies["PRIMARY"][p]["policy_id"]
        [cids[p]] = free(sid, pid)
        check = checks[cids[p]]
        assert (check["setup_id"], check["policy_id"], check.get("family")) == (sid, pid, None)
    exact = setup_record["derived"]["setups"][other]["applications"]["RESIDUAL"]["setup_id"]
    xdev = dev_record["derived"]["setups"][other]["RESIDUAL"]["policies"]["PRIMARY"]
    aliases = {c for row in policies["GAMMA_M"].values() for c in free(sid, row["policy_id"])}
    aliases |= {c for p in B3F_P if p in xdev for c in free(exact, xdev[p]["policy_id"])}
    assert exact != sid and len(set(cids.values())) == 3 and len(aliases) >= 2 and not aliases & set(cids.values())
    _, n_hold, held = verify(staging, did, ups["HOLD"], ["HOLD_NULL", *primary, "RESIDUAL"])
    assert n_hold == null_record["derived"]["n_hold"] == 5
    hold = {p: held["first_" + cids[p]] for p in B3F_P}
    states = {p: checks[cids[p]]["status"] for p in B3F_P}
    n, alt, trials = desc["sizes"]["ALT"], {}, alt_record["derived"]["trials"]
    for family, labels in ((B3F_F2, B3F_P), (B3F_HEAD, B3F_P[:2])):
        key = ["ALT", *primary, "RESIDUAL", family]
        _, rows, arrays = verify(staging, did, ups["ALT"], key)
        assert rows == n == 2 and set(cids.values()) <= set(trials[pdb.canon(key)]["calibration_ids"])
        alt[family] = {p: arrays["first_" + cids[p]] for p in labels}
    assert all(v.dtype.kind == "i" and v.shape == (n_hold,) for v in hold.values())
    assert all(v.dtype.kind == "i" and v.shape == (n,) for row in alt.values() for v in row.values())
    geometry = meta["head"]["geometry"]
    assert meta["head"]["status"] in ("GEOMETRY_ALIGNED", "DESIGN_CONTROL_INCONCLUSIVE") and isinstance(geometry, dict)
    B, seed, planned = desc["science"]["bootstrap"]["B"], int(cfg["seed"]), _kernel("seed_plan")(cfg, "full")["keys"]
    keys = {f: ["boot", C, *primary, "RESIDUAL", f] for f in (B3F_F2, B3F_HEAD)}
    assert B == B3G_B and all(tuple(k) in planned for k in keys.values())
    words = {f: [32, seed, pdb.label_code(C), pdb.label_code("boot"), pdb.label_code(primary[0]), primary[1],
                 primary[2], pdb.label_code("RESIDUAL"), pdb.label_code(f)] for f in keys}
    boot = {f: np.random.default_rng(np.random.SeedSequence(w)).integers(0, n, size=(B, n), dtype=np.int64)
            for f, w in words.items()}
    assert not np.array_equal(boot[B3F_F2], boot[B3F_HEAD])
    return {"did": did, "primary": primary, "sid": sid, "cids": cids, "ups": ups, "hold": hold, "states": states,
            "alt": alt, "geometry": geometry, "keys": keys, "words": words, "boot": boot}


def _b3g_draws(mp, real, words, seen, phases):
    sequence, generator = real
    states = {f: sequence(w).generate_state(8).tobytes() for f, w in words.items()}

    def seq(entropy=None, **kwargs):
        assert not kwargs and [int(w) for w in entropy] in list(words.values()), entropy
        return sequence(entropy)

    def rng(seed=None):
        assert isinstance(seed, sequence) and not seed.spawn_key and (phases / "ALT.json").exists()
        [family] = [f for f, s in states.items() if seed.generate_state(8).tobytes() == s]
        seen.append(family)
        return generator(seed)

    mp.setattr(np.random, "SeedSequence", seq)
    mp.setattr(np.random, "default_rng", rng)


def _b3g_same_call(call, desc, ref):
    assert pdb.canon(call["desc"]) == pdb.canon(desc) and call["preconditions"] is True
    assert call["null_states"] == ref["states"] and call["geometry"] == ref["geometry"]
    assert set(call["hold_first"]) == set(B3F_P) and set(call["boot_indices"]) == set(ref["boot"])
    assert {f: set(v) for f, v in call["alt_first"].items()} == {f: set(v) for f, v in ref["alt"].items()}
    pairs = [(call["hold_first"][p], ref["hold"][p]) for p in B3F_P]
    pairs += [(call["alt_first"][f][p], v) for f, row in ref["alt"].items() for p, v in row.items()]
    pairs += [(call["boot_indices"][f], v) for f, v in ref["boot"].items()]
    for got, want in pairs:
        got = np.asarray(got)
        assert got.dtype.kind == "i" and got.shape == want.shape and np.array_equal(got, want)


def test_confirmatory_from_staging_bootstraps_each_claimed_family_once_on_committed_primary_cells_then_replays(
        tmp_path, monkeypatch):
    import collections
    import inspect
    real = np.random.SeedSequence, np.random.default_rng
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, module, phases = _b3g_references(fixture, records), pio(), staging / "phases"
    infer, info = _kernel("confirmatory_inference"), B3F_P[0]
    want = infer(desc, ref["hold"], ref["alt"], ref["states"], ref["boot"], ref["geometry"])
    assert set(want) == set(B3G_CLAIMS)
    assert all((want[k]["family"], want[k]["comparator_policy"]) == v for k, v in B3G_CLAIMS.items())
    signature, calls, seen, outs = inspect.signature(infer), [], [], []

    def spy(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        calls.append(dict(bound.arguments))
        return infer(*args, **kwargs)

    before = _tree(staging)
    for token in ("invocation-8", "invocation-9"):
        with monkeypatch.context() as mp:
            _b3b_guard(mp, state, *B3B_TRAPPED)
            _b3g_forbid(mp, *B3G_SIDE)
            _b3g_draws(mp, real, ref["words"], seen, phases)
            mp.setattr(module, "confirmatory_inference", spy)
            outs.append(_kernel("confirmatory_from_staging")(cfg, "full", context))
            context = _kernel("start_invocation")(staging, authority, plan, token)
        after = _tree(staging)
        assert set(after) == set(before) and len(calls) == len(outs) and len(seen) == 2 * len(outs)
        assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")
        assert sorted(seen[-2:]) == sorted([B3F_F2, B3F_HEAD])
    out, again = outs
    np.testing.assert_equal(again, out)
    assert collections.Counter(seen) == collections.Counter({B3F_F2: 2, B3F_HEAD: 2})
    for call in calls:
        _b3g_same_call(call, desc, ref)
    assert out["design_id"] == ref["did"] and list(out["setup"]) == ref["primary"] and out["setup_id"] == ref["sid"]
    assert out["alt_phase_digest"] == records[5]["phase_digest"]
    assert {f: list(k) for f, k in out["bootstrap_keys"].items()} == ref["keys"]
    claims = out["claims"]
    assert set(claims) == set(B3G_CLAIMS)
    for key, (family, comp) in B3G_CLAIMS.items():
        got, row = claims[key], want[key]
        extra = {"info_calibration_id": ref["cids"][info], "comparator_calibration_id": ref["cids"][comp],
                 "info_null_status": ref["states"][info], "comparator_null_status": ref["states"][comp],
                 **({"geometry": ref["geometry"]} if key == "H2" else {})}
        assert set(got) == set(row) | set(extra), key
        np.testing.assert_equal({k: got[k] for k in row}, row, err_msg=key)
        assert {k: got[k] for k in extra} == extra, key


@pytest.mark.parametrize("case", list(B3G_POISON))
def test_confirmatory_from_staging_refuses_an_absent_or_damaged_committed_input_before_any_bootstrap_or_kernel(
        tmp_path, monkeypatch, case):
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, phases, verify = _b3g_references(fixture, records), staging / "phases", _kernel("_verify_partition")
    did, primary, ups = ref["did"], ref["primary"], ref["ups"]
    target = (ups["HOLD"], ["HOLD_NULL", *primary, "RESIDUAL"]) if case.startswith("hold") else (
        ups["ALT"], ["ALT", *primary, "RESIDUAL", B3F_F2])
    payload = _partition_stem(staging, did, *target).with_suffix(".npz")
    assert payload.is_file() and verify(staging, did, *target)[1] in (2, 5)
    if case == "alt_record_absent":
        (phases / "ALT.json").unlink()
        assert all(verify(staging, did, ups["ALT"], key)[1] == 2 for key in plan["ALT"])
    elif case.endswith("missing"):
        payload.unlink()
    else:
        payload.write_bytes(b"damaged")
    if case != "alt_record_absent":
        with pytest.raises(pdb.PartitionMismatch):
            verify(staging, did, *target)
    assert (phases / "ALT.json").exists() is (case != "alt_record_absent")
    assert all((phases / f"{p}.json").exists() for p in B3E_PRIOR)
    raised = pio().PhaseOrderError if B3G_POISON[case] == "PhaseOrderError" else pdb.PartitionMismatch
    before = _tree(staging)
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3g_forbid(mp, "confirmatory_inference", "head_control", "tango_interval", *B3G_SIDE)
        api = _kernel("confirmatory_from_staging")
        with pytest.raises(raised):
            api(cfg, "full", context)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")


B3H_TAIL, B3H_ORACLE = 0.025, "ORACLE_INFO_MIX"
B3H_FORBIDDEN = (*B3B_TRAPPED, "direction_draws", "null_returns", "exact_scores", "partition", "guarded_partition",
                 "phase_record", "_verify_partition", "confirmatory_inference", "confirmatory_from_staging", *B3G_SIDE)
B3H_REFUSALS = ("foreign_oracle", "hold_keys", "alt_keys", "hold_ragged", "alt_ragged", "alt_zero", "hold_above_H",
                "alt_float", "boot_shape", "boot_range", "boot_negative", "boot_float", "boot_unsigned")


def _b3h_cell(label, variant, pid, family, status):
    return {"policy_label": label, "variant": variant, "policy_id": pid, "calibration_family": family,
            "null_status": status}


def _b3h_witness():
    cells = {"c_info": _b3h_cell(B3F_P[0], "PRIMARY", "p_info", None, "NULL_VALIDATED"),
             "c_prefix": _b3h_cell(B3F_P[1], "PRIMARY", "p_prefix", None, "NULL_INCONCLUSIVE"),
             "c_full": _b3h_cell(B3F_P[2], "PRIMARY", "p_full", None, "NULL_VALIDATED"),
             "c_gamma": _b3h_cell(B3F_P[0], "GAMMA_M", "p_gamma", None, "NULL_VALIDATED"),
             "c_s2": _b3h_cell(B3F_P[2], "S2_DEV", "p_s2", None, "NULL_INCONCLUSIVE"),
             "c_oracle": _b3h_cell(B3H_ORACLE, "PRIMARY", "p_oracle", B3F_F2, "NULL_VALIDATED")}
    raw_alt = {"c_info": [2, 10, -1, 4, 3], "c_prefix": [6, -1, 10, 9, 8], "c_full": [10, 5, -1, 1, 7],
               "c_gamma": [3, 10, 4, -1, 2], "c_s2": [1, 2, 3, 10, -1], "c_oracle": [1, 1, 2, 1, 10]}
    raw_hold = {"c_info": [-1, 3, -1, -1, 10, -1, -1, -1], "c_prefix": [-1, -1, -1, 7, -1, -1, -1, -1],
                "c_full": [1, 3, -1, -1, -1, 2, -1, -1], "c_gamma": [-1, 3, -1, -1, 10, -1, -1, -1],
                "c_s2": [-1, -1, 5, -1, -1, -1, -1, 10], "c_oracle": [-1, -1, -1, -1, -1, -1, 4, -1]}
    boot = np.array([[0, 1, 2, 3, 4], [0, 0, 1, 1, 2], [4, 4, 3, 3, 2], [1, 3, 1, 3, 0], [2, 2, 3, 3, 0],
                     [4, 0, 3, 1, 2]], dtype=np.int64)
    hold = {c: np.array(v, dtype=np.int64) for c, v in raw_hold.items()}
    alt = {c: np.array(v, dtype=np.int64) for c, v in raw_alt.items()}
    return 10, cells, hold, alt, boot


def _b3h_aligned(H, family, cells, hold, alt, boot):
    shapes = [{np.asarray(v).shape for v in d.values()} for d in (hold, alt)]
    arrays = [np.asarray(v) for d in (hold, alt) for v in d.values()]
    return bool(set(cells) == set(hold) == set(alt) and len(shapes[0]) == len(shapes[1]) == 1
                and all(v["calibration_family"] in (None, family) for v in cells.values())
                and all(a.ndim == 1 and a.dtype.kind == "i" and ((a == -1) | ((a >= 1) & (a <= H))).all()
                        for a in arrays)
                and boot.dtype.kind == "i" and boot.ndim == 2 and (boot.shape[1],) in shapes[1]
                and ((boot >= 0) & (boot < boot.shape[1])).all())


def _b3h_expect(H, hold, alt, boot, cand, ref, oracle):
    t = {c: np.where(alt[c] == -1, H, alt[c]).astype(np.float64) for c in (cand, ref)}
    diff = (t[cand] - t[ref])[boot].mean(axis=1)
    row = {"rmst_difference": float(t[cand].mean() - t[ref].mean()),
           "rmst_ci": (_b3f_pct(diff, 0.025), _b3f_pct(diff, 0.975))}
    hit = {c: hold[c] != -1 for c in (cand, ref)}
    n = hit[cand].size
    if oracle:
        return {**row, "candidate_fpr": float(hit[cand].mean()), "reference_fpr": float(hit[ref].mean())}
    b, c = int((hit[cand] & ~hit[ref]).sum()), int((~hit[cand] & hit[ref]).sum())
    ci = tuple(_kernel("tango_interval")(b, c, n, B3H_TAIL))
    return {**row, "bc": (b, c), "fpr_delta": (b - c) / n, "fpr_ci": ci}


def _b3h_check(out, cells, expect, status):
    assert isinstance(out, list) and all(isinstance(r, dict) for r in out)
    got = {(r["candidate_calibration_id"], r["reference_calibration_id"]): r for r in out}
    assert len(got) == len(out) and set(got) == set(expect)
    fpr_ok = ("DESCRIPTIVE_NOMINAL",) if status == "DESCRIPTIVE_NOMINAL" else ("DESCRIPTIVE_NOMINAL", "PILOT_ONLY")
    for (cand, ref), e in expect.items():
        r = got[cand, ref]
        assert (r["candidate_policy_id"], r["reference_policy_id"]) == (
            cells[cand]["policy_id"], cells[ref]["policy_id"]), (cand, ref)
        assert (r["candidate_null_status"], r["reference_null_status"]) == (
            cells[cand]["null_status"], cells[ref]["null_status"]), (cand, ref)
        assert r["deff"] == 1 and r["status"] == status, (cand, ref)
        assert r["rmst_difference"] == pytest.approx(e["rmst_difference"], abs=1e-9), (cand, ref)
        assert tuple(r["rmst_ci"]) == pytest.approx(e["rmst_ci"], abs=1e-9), (cand, ref)
        if "candidate_fpr" in e:
            assert r["fpr_status"] == "ORACLE_SEPARATE" and r.get("fpr_delta") is None and r.get("fpr_ci") is None
            assert (r["candidate_fpr"], r["reference_fpr"]) == pytest.approx(
                (e["candidate_fpr"], e["reference_fpr"]), abs=1e-12), (cand, ref)
        else:
            assert r["fpr_status"] in fpr_ok and r["fpr_delta"] == pytest.approx(e["fpr_delta"], abs=1e-12)
            assert tuple(r["fpr_ci"]) == pytest.approx(e["fpr_ci"], abs=1e-9), (cand, ref)
        words = [v for v in r.values() if isinstance(v, str)]
        assert not [v for v in words for w in ("CONFIRMED", "ESTABLISHED", "ATTAINED", "COMPARABLE") if w in v]
        assert not {"gain_bound", "ni_upper"} & set(r) and r.get("fpr_equivalent") in (None, False)


def test_b3h_descriptive_contrasts_pair_nonoracle_cells_with_primary_baselines_and_separate_the_oracle(monkeypatch):
    import copy
    H, cells, hold, alt, boot = _b3h_witness()
    nonoracle = ["c_info", "c_prefix", "c_full", "c_gamma", "c_s2"]
    pairs = [(c, r) for r in ("c_info", "c_prefix") for c in nonoracle if c != r] + [("c_oracle", "c_info")]
    assert len(set(pairs)) == len(pairs) == 9 and not [p for p in pairs if p[1] == "c_oracle"]
    assert [c for c, v in cells.items() if v["calibration_family"] is None] == nonoracle
    assert (cells["c_oracle"]["policy_label"], cells["c_oracle"]["calibration_family"]) == (B3H_ORACLE, B3F_F2)
    assert len({v["policy_id"] for v in cells.values()}) == len(cells) == 6
    assert _b3h_aligned(H, B3F_F2, cells, hold, alt, boot) and not _b3h_aligned(H, B3F_HEAD, cells, hold, alt, boot)
    assert all(np.unique(v).size > 1 for v in alt.values()) and len({tuple(sorted(r)) for r in boot.tolist()}) == 5
    assert all((v == H).any() for v in (alt["c_info"], alt["c_prefix"], hold["c_info"], hold["c_s2"]))
    expect = {p: _b3h_expect(H, hold, alt, boot, *p, p[0] == "c_oracle") for p in pairs}
    strong, orc = expect["c_info", "c_prefix"], expect["c_oracle", "c_info"]
    late = int(((hold["c_info"] >= 1) & (hold["c_info"] < H) & (hold["c_prefix"] == -1)).sum())
    assert strong["rmst_difference"] == pytest.approx(-2.8, abs=1e-12) and strong["rmst_ci"][1] < -1.0
    assert expect["c_prefix", "c_info"]["rmst_ci"][0] > 1.0 and strong["bc"] == (2, 1) and late == 1
    assert expect["c_gamma", "c_info"]["bc"] == (0, 0) and expect["c_full", "c_info"]["bc"] == (2, 1)
    assert all(e["rmst_ci"][0] < e["rmst_ci"][1] for e in expect.values())
    assert (orc["candidate_fpr"], orc["reference_fpr"]) == (1 / 8, 2 / 8)
    failed = copy.deepcopy(cells)
    failed["c_full"]["null_status"] = "NULL_FAILED"
    frozen = copy.deepcopy((cells, failed, hold, alt, boot))
    api = _kernel("descriptive_contrasts")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3H_FORBIDDEN)
        _b3f_seal(mp)
        full = api("full", H, B3F_F2, cells, hold, alt, boot)
        pilot = api("pilot", H, B3F_F2, failed, hold, alt, boot)
    np.testing.assert_equal((cells, failed, hold, alt, boot), frozen)
    _b3h_check(full, cells, expect, "DESCRIPTIVE_NOMINAL")
    _b3h_check(pilot, failed, expect, "PILOT_ONLY")


@pytest.mark.parametrize("case", B3H_REFUSALS)
def test_b3h_descriptive_contrasts_refuse_a_foreign_oracle_or_malformed_alignment_before_any_contrast(monkeypatch,
                                                                                                    case):
    H, cells, hold, alt, boot = _b3h_witness()
    if case == "foreign_oracle":
        cells["c_head"] = _b3h_cell(B3H_ORACLE, "PRIMARY", "p_head", B3F_HEAD, "NULL_VALIDATED")
        hold["c_head"], alt["c_head"] = hold["c_oracle"].copy(), alt["c_oracle"].copy()
    elif case == "hold_keys":
        del hold["c_s2"]
    elif case == "alt_keys":
        alt["c_extra"] = alt["c_info"].copy()
    elif case == "hold_ragged":
        hold["c_full"] = hold["c_full"][:-1]
    elif case == "alt_ragged":
        alt["c_gamma"] = alt["c_gamma"][:-1]
    elif case == "alt_zero":
        alt["c_s2"][0] = 0
    elif case == "hold_above_H":
        hold["c_prefix"][3] = H + 1
    elif case == "alt_float":
        alt["c_info"] = alt["c_info"].astype(np.float64)
    elif case == "boot_shape":
        boot = boot[:, :4]
    elif case == "boot_range":
        boot[2, 1] = 5
    elif case == "boot_negative":
        boot[0, 0] = -1
    else:
        boot = boot.astype(np.float64 if case == "boot_float" else np.uint64)
    assert not _b3h_aligned(H, B3F_F2, cells, hold, alt, boot)
    api = _kernel("descriptive_contrasts")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3H_FORBIDDEN, "tango_interval")
        _b3f_seal(mp)
        with pytest.raises(ValueError):
            api("full", H, B3F_F2, cells, hold, alt, boot)


def test_b3h_descriptive_contrasts_consume_committed_primary_f2_cells_and_keep_the_same_family_oracle_separate(
        tmp_path, monkeypatch):
    import copy
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, verify = _b3g_references(fixture, records), _kernel("_verify_partition")
    _, dev_record, cal_record, _, hold_record, alt_record = records
    did, primary, sid, ups = ref["did"], ref["primary"], ref["sid"], ref["ups"]
    H = desc["science"]["parameters"]["H"]
    thresholds, checks = cal_record["derived"]["thresholds"], hold_record["derived"]["null_checks"]
    policies = dev_record["derived"]["setups"][pdb.canon(primary)]["RESIDUAL"]["policies"]
    key = ["ALT", *primary, "RESIDUAL", B3F_F2]
    ids = alt_record["derived"]["trials"][pdb.canon(key)]["calibration_ids"]
    named, cells = {}, {}
    for variant in ("PRIMARY", "GAMMA_M", "S2_DEV"):
        for label, row in policies[variant].items():
            if row["policy_id"] is not None:
                named.setdefault(row["policy_id"], (label, variant))
    for c in ids:
        t = thresholds[c]
        cells[c] = _b3h_cell(*named[t["policy_id"]], t["policy_id"], t.get("family"), checks[c]["status"])
    free = {c for c, t in thresholds.items() if t["setup_id"] == sid and t.get("family") is None}
    nonoracle = [c for c in ids if cells[c]["calibration_family"] is None]
    [oracle] = [c for c in ids if cells[c]["calibration_family"] is not None]
    opid, info, prefix = policies["PRIMARY"][B3H_ORACLE]["policy_id"], ref["cids"][B3F_P[0]], ref["cids"][B3F_P[1]]
    siblings = {t["family"]: c for c, t in thresholds.items() if (t["setup_id"], t["policy_id"]) == (sid, opid)}
    foreign = sorted(c for f, c in siblings.items() if f != B3F_F2)
    assert len(set(ids)) == len(ids) and set(nonoracle) == free and set(ref["cids"].values()) <= free
    assert all((cells[c]["policy_label"], cells[c]["variant"]) == (p, "PRIMARY") for p, c in ref["cids"].items())
    assert {cells[c]["variant"] for c in nonoracle} >= {"PRIMARY", "GAMMA_M"} and len(nonoracle) >= 5
    assert (cells[oracle]["policy_label"], cells[oracle]["variant"], cells[oracle]["policy_id"]) == (
        B3H_ORACLE, "PRIMARY", opid)
    assert (cells[oracle]["calibration_family"], thresholds[oracle]["qualification"]) == (B3F_F2, B3A_ORACLE_LABEL)
    assert (checks[oracle]["family"], checks[oracle]["qualification"]) == (B3F_F2, "NON_DEPLOYABLE")
    assert set(siblings) == set(DEV_FAMILIES) and siblings[B3F_F2] == oracle and len(foreign) == 3
    assert not set(foreign) & set(ids)
    _, n_hold, held = verify(staging, did, ups["HOLD"], ["HOLD_NULL", *primary, "RESIDUAL"])
    _, n_alt, arrays = verify(staging, did, ups["ALT"], key)
    assert all("first_" + c in held and "first_" + c not in arrays for c in foreign)
    hold, alt = {c: held["first_" + c] for c in ids}, {c: arrays["first_" + c] for c in ids}
    boot = ref["boot"][B3F_F2]
    assert all(np.array_equal(hold[c], ref["hold"][p]) and np.array_equal(alt[c], ref["alt"][B3F_F2][p])
               for p, c in ref["cids"].items())
    assert (n_hold, n_alt) == (5, 2) and boot.dtype == np.int64 and boot.shape == (B3G_B, n_alt)
    assert _b3h_aligned(H, B3F_F2, cells, hold, alt, boot)
    alien = {**cells, **{c: _b3h_cell(B3H_ORACLE, "PRIMARY", opid, thresholds[c]["family"], checks[c]["status"])
                         for c in foreign}}
    alien_hold = {**hold, **{c: held["first_" + c] for c in foreign}}
    alien_alt = {**alt, **dict.fromkeys(foreign, alt[oracle])}
    assert not _b3h_aligned(H, B3F_F2, alien, alien_hold, alien_alt, boot)
    pairs = [(c, r) for r in (info, prefix) for c in nonoracle if c != r] + [(oracle, info)]
    assert len(set(pairs)) == len(pairs) == 2 * len(nonoracle) - 1
    expect = {p: _b3h_expect(H, hold, alt, boot, *p, p[0] == oracle) for p in pairs}
    frozen, before = copy.deepcopy((cells, hold, alt, boot)), _tree(staging)
    api = _kernel("descriptive_contrasts")
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3g_forbid(mp, *B3H_FORBIDDEN)
        _b3f_seal(mp)
        out = api("full", H, B3F_F2, cells, hold, alt, boot)
        with pytest.raises(ValueError):
            api("full", H, B3F_F2, alien, alien_hold, alien_alt, boot)
    assert _tree(staging) == before
    np.testing.assert_equal((cells, hold, alt, boot), frozen)
    _b3h_check(out, cells, expect, "DESCRIPTIVE_NOMINAL")


B3I_MASKS, B3I_H = ((1, 3, 3, 4), (1, 1, 6, 2)), -0.125
B3I_WITNESS = {"n": 2, "H": 4, "K": 3, "h": -0.125, "axis_counts": [5, 4, 2], "axis_frequencies": [0.625, 0.5, 0.25],
               "d_counts": [0, 5, 3, 0], "switches_per_path": [2, 2], "screening_reads_per_path": 12,
               "scan_units_per_path": 30, "selection_evaluations_per_path": 3, "screening_reads": 24, "scan_units": 60,
               "selection_evaluations": 6}
B3I_INVALID = ("zero_entry", "above_K", "K_zero", "K_33", "h_nan", "h_inf", "int64", "one_dim", "no_rows", "no_steps")
B3I_FORBIDDEN = (*B3G_SIDE, "online_masks", "alt_phase", "confirmatory_from_staging", "confirmatory_inference",
                 "descriptive_contrasts", "head_control", "tango_interval", "exact_scores", "null_returns",
                 "direction_draws")
B3I_OUT = {"role", "setup_id", "calibration_id", "axis_pcs", "hold_phase_digest", "hold_payload_sha256", "telemetry"}


def _b3i_valid(mask, K, h):
    return bool(isinstance(mask, np.ndarray) and mask.dtype == np.uint32 and mask.ndim == 2 and min(mask.shape) > 0
                and type(K) is int and 1 <= K <= 32 and (mask != 0).all()
                and (mask.astype(np.uint64) >> np.uint64(K) == 0).all()
                and isinstance(h, (int, float)) and not isinstance(h, bool) and math.isfinite(h))


def _b3i_invalid(case):
    mask, K, h = np.array(B3I_MASKS, dtype=np.uint32), 3, B3I_H
    if case == "zero_entry":
        mask[1, 2] = 0
    elif case == "above_K":
        mask[0, 3] = 8
    elif case == "K_zero":
        K = 0
    elif case == "K_33":
        K = 33
    elif case == "h_nan":
        h = math.nan
    elif case == "h_inf":
        h = -math.inf
    elif case == "int64":
        mask = mask.astype(np.int64)
    elif case == "one_dim":
        mask = mask[0]
    elif case == "no_rows":
        mask = mask[:0]
    else:
        mask = mask[:, :0]
    return mask, K, h


def _b3i_expect(mask, K, h):
    rows = [[int(v) for v in row] for row in np.asarray(mask).tolist()]
    n, H = len(rows), len(rows[0])
    axes, d = [0] * K, [0] * (K + 1)
    for row in rows:
        for v in row:
            d[bin(v).count("1")] += 1
            for j in range(K):
                axes[j] += (v >> j) & 1
    per = {"screening_reads": K * H, "scan_units": K * H * (H + 1) // 2, "selection_evaluations": H - 1}
    return {"n": n, "H": H, "K": K, "h": h, "axis_counts": axes, "axis_frequencies": [a / (n * H) for a in axes],
            "d_counts": d, "switches_per_path": [sum(a != b for a, b in zip(row, row[1:])) for row in rows],
            **{k + "_per_path": v for k, v in per.items()}, **{k: n * v for k, v in per.items()}}


def _b3i_check(out, want):
    assert isinstance(out, dict) and set(out) == set(want)
    for k, v in want.items():
        got = np.asarray(out[k])
        if k == "axis_frequencies":
            assert got.dtype.kind == "f" and got.tolist() == pytest.approx(v, abs=1e-15), k
        elif k == "h":
            assert got.dtype.kind == "f" and got.tolist() == v, k
        else:
            assert got.dtype.kind in "iu" and got.tolist() == v, k


def _b3i_no_reads(mp, banned):
    import builtins
    import os
    from pathlib import Path
    banned, real_open = {Path(p).resolve() for p in banned}, builtins.open

    def check(target):
        if isinstance(target, (str, os.PathLike)):
            assert Path(target).resolve() not in banned, f"B3i ALT content read: {target}"

    def opened(file, *args, **kwargs):
        check(file)
        return real_open(file, *args, **kwargs)

    for name in ("open", "read_text", "read_bytes"):
        def guarded(self, *args, _real=getattr(Path, name), **kwargs):
            check(self)
            return _real(self, *args, **kwargs)

        mp.setattr(Path, name, guarded)
    mp.setattr(builtins, "open", opened)


def _b3i_cells(desc, records):
    setup_record, dev_record, cal_record = records[:3]
    thresholds, out = cal_record["derived"]["thresholds"], []
    for s in (desc["science"]["phi"]["setup"], B2W_SETUPS[0]):
        name = pdb.canon(list(s))
        sid = setup_record["derived"]["setups"][name]["applications"]["RESIDUAL"]["setup_id"]
        rows = dev_record["derived"]["setups"][name]["RESIDUAL"]["policies"]["PRIMARY"]
        out.append((sid, {label: sorted(c for c, t in thresholds.items()
                                        if (t["setup_id"], t["policy_id"]) == (sid, row["policy_id"]))
                          for label, row in rows.items() if row["policy_id"] is not None}))
    return out


def test_b3i_selection_telemetry_counts_axes_sizes_switches_and_theoretical_units_on_hand_witnesses(monkeypatch):
    import copy
    import inspect
    mask = np.array(B3I_MASKS, dtype=np.uint32)
    wide = np.array([[2 ** 31, 2 ** 31 | 1, 2 ** 31 | 1], [5, 5, 5]], dtype=np.uint32)
    single = np.array([[5], [2], [7]], dtype=np.uint32)
    cases = [(mask, 3, B3I_H), (wide, 32, 0.0), (single, 3, 2.5)]
    assert all(_b3i_valid(*c) for c in cases) and _b3i_expect(mask, 3, B3I_H) == B3I_WITNESS
    w, s = _b3i_expect(wide, 32, 0.0), _b3i_expect(single, 3, 2.5)
    assert w["switches_per_path"] == [1, 0] and w["d_counts"][:3] == [0, 1, 5] and sum(w["d_counts"]) == 6
    assert [w["axis_counts"][j] for j in (0, 2, 31)] == [5, 3, 3] and sum(w["axis_counts"]) == 11
    assert len(w["d_counts"]) == 33 and (w["screening_reads"], w["scan_units"]) == (192, 384)
    assert s["switches_per_path"] == [0, 0, 0] and s["d_counts"] == [0, 1, 1, 1]
    assert (s["selection_evaluations_per_path"], s["selection_evaluations"], s["screening_reads"], s["scan_units"]) == (
        0, 0, 9, 9)
    frozen = copy.deepcopy(cases)
    api = _kernel("selection_telemetry")
    assert list(inspect.signature(api).parameters) == ["mask_bits", "K", "h"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3H_FORBIDDEN, *B3I_FORBIDDEN, "hold_phase")
        _b3f_seal(mp)
        outs = [api(*c) for c in cases]
    np.testing.assert_equal(cases, frozen)
    for out, c in zip(outs, cases):
        _b3i_check(out, _b3i_expect(*c))


@pytest.mark.parametrize("case", B3I_INVALID)
def test_b3i_selection_telemetry_refuses_an_invalid_mask_width_or_threshold_before_any_count(monkeypatch, case):
    args = _b3i_invalid(case)
    assert _b3i_valid(np.array(B3I_MASKS, dtype=np.uint32), 3, B3I_H) and not _b3i_valid(*args)
    api = _kernel("selection_telemetry")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3H_FORBIDDEN, *B3I_FORBIDDEN, "hold_phase")
        _b3f_seal(mp)
        with pytest.raises(ValueError):
            api(*args)


def test_b3i_hold_selection_telemetry_reads_the_full_committed_primary_online_info_mask_through_hold_only(
        tmp_path, monkeypatch):
    import hashlib
    import inspect
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, verify, phases = _b3g_references(fixture, records), _kernel("_verify_partition"), staging / "phases"
    setup_record, _, cal_record, _, hold_record, _ = records
    did, primary, sid, ups, cid = ref["did"], ref["primary"], ref["sid"], ref["ups"], ref["cids"][B3F_P[0]]
    H, K = desc["science"]["parameters"]["H"], desc["science"]["parameters"]["K"]
    key, thresholds = ["HOLD_NULL", *primary, "RESIDUAL"], cal_record["derived"]["thresholds"]
    meta = setup_record["derived"]["setups"][pdb.canon(primary)]["applications"]["RESIDUAL"]
    row = thresholds[cid]
    axis_pcs, h = meta["universe"], row["h"]
    assert (row["setup_id"], row.get("family"), meta["setup_id"], H, K) == (sid, None, sid, 6, 20)
    assert axis_pcs == list(range(2, 22)) and type(h) is float and math.isfinite(h)
    sha, n_hold, held = verify(staging, did, ups["HOLD"], key)
    payload = _partition_stem(staging, did, ups["HOLD"], key).with_suffix(".npz")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    [part] = [r for r in hold_record["partitions"] if r["key"] == key]
    assert sha == digest == part["sha256"] and n_hold == part["n_rows"] == 5
    mask = held["mask_" + cid]
    assert mask.dtype == np.uint32 and mask.shape == (n_hold, H) and _b3i_valid(mask, K, h)
    assert np.array_equal(held["first_" + cid], ref["hold"][B3F_P[0]])
    want = _b3i_expect(mask, K, h)
    assert (want["n"], want["H"], want["K"], want["h"]) == (5, 6, 20, h) and sum(want["d_counts"]) == n_hold * H
    assert sum(want["axis_counts"]) == sum(d * c for d, c in enumerate(want["d_counts"])) and want["d_counts"][0] == 0
    assert (want["screening_reads"], want["scan_units"], want["selection_evaluations"]) == (600, 2100, 25)
    assert hold_record["phase_digest"] == ups["ALT"]["HOLD"]
    alt_key = ["ALT", *primary, "RESIDUAL", B3F_F2]
    stem = _partition_stem(staging, did, ups["ALT"], alt_key)
    banned = [phases / "ALT.json", stem.with_suffix(".npz"), stem.with_suffix(".json")]
    assert all(p.is_file() for p in banned)
    banned[0].write_text("poisoned")
    banned[1].write_bytes(b"poisoned")
    with pytest.raises(pdb.PartitionMismatch):
        verify(staging, did, ups["ALT"], alt_key)
    before = _tree(staging)
    api = _kernel("hold_selection_telemetry")
    assert list(inspect.signature(api).parameters) == ["cfg", "mode", "context", "key", "calibration_id"]
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3g_forbid(mp, *B3I_FORBIDDEN)
        _b3i_no_reads(mp, banned)
        out = api(cfg, "full", context, list(key), cid)
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")
    assert isinstance(out, dict) and set(out) == B3I_OUT
    assert (out["role"], out["setup_id"], out["calibration_id"]) == ("HOLD_NULL", sid, cid)
    assert list(out["axis_pcs"]) == axis_pcs and out["hold_phase_digest"] == hold_record["phase_digest"]
    assert out["hold_payload_sha256"] == digest
    _b3i_check(out["telemetry"], want)


def test_b3i_hold_selection_telemetry_refuses_foreign_keys_or_cells_and_a_damaged_or_uncommitted_hold(
        tmp_path, monkeypatch):
    fixture, state, records, context = _b3e_fixture(tmp_path, monkeypatch, True)
    cfg, desc, authority, plan, staging = fixture
    phases, verify, did = staging / "phases", _kernel("_verify_partition"), _kernel("design_id")(desc)
    primary, thresholds = desc["science"]["phi"]["setup"], records[2]["derived"]["thresholds"]
    upstream = {p: r["phase_digest"] for p, r in zip(B3D_PRIOR, records)}
    (sid, own), (xsid, xown) = _b3i_cells(desc, records)
    [info], [static] = own[B3F_P[0]], own["FULL_K"]
    [oracle] = [c for c in own[B3H_ORACLE] if thresholds[c].get("family") == B3F_F2]
    foreign = sorted(c for label in B2V_ONLINE for c in xown.get(label, []) if thresholds[c].get("family") is None)
    hold_key, market = ["HOLD_NULL", *primary, "RESIDUAL"], ["HOLD_NULL", *primary, "MARKET"]
    alt_key, xkey = ["ALT", *primary, "RESIDUAL", B3F_F2], ["HOLD_NULL", *B2W_SETUPS[0], "RESIDUAL"]
    assert records[4]["upstream"] == upstream and not (phases / "ALT.json").exists() and xsid != sid and foreign
    assert market in plan["HOLD"] and xkey in plan["HOLD"] and alt_key in plan["ALT"]
    assert thresholds[info].get("family") is None and thresholds[static].get("family") is None
    assert thresholds[oracle]["qualification"] == B3A_ORACLE_LABEL
    _, n_hold, held = verify(staging, did, upstream, hold_key)
    _, _, xheld = verify(staging, did, upstream, xkey)
    assert all("mask_" + c in held for c in (info, static, oracle)) and "mask_" + foreign[0] in xheld
    bad = {"alt_key": (alt_key, info), "foreign_setup": (hold_key, foreign[0]), "foreign_application": (market, info),
           "oracle": (hold_key, oracle), "static": (hold_key, static)}
    payload = _partition_stem(staging, did, upstream, hold_key).with_suffix(".npz")
    good = payload.read_bytes()
    api = _kernel("hold_selection_telemetry")

    def refuse(raised, key, cid):
        before = _tree(staging)
        with monkeypatch.context() as mp:
            _b3b_guard(mp, state, *B3B_TRAPPED)
            _b3g_forbid(mp, *B3I_FORBIDDEN)
            _b3d_no_alt(mp, staging)
            with pytest.raises(raised):
                api(cfg, "full", context, key, cid)
        after = _tree(staging)
        assert set(after) == set(before) and "status.json" not in after, key
        assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json"), key

    for key, cid in bad.values():
        refuse(ValueError, key, cid)
    payload.write_bytes(b"damaged")
    with pytest.raises(pdb.PartitionMismatch):
        verify(staging, did, upstream, hold_key)
    refuse(pdb.PartitionMismatch, hold_key, info)
    assert payload.read_bytes() == b"damaged"
    payload.write_bytes(good)
    assert verify(staging, did, upstream, hold_key)[1] == n_hold == 5
    (phases / "HOLD.json").unlink()
    refuse(pio().PhaseOrderError, hold_key, info)
    assert not (phases / "HOLD.json").exists() and payload.read_bytes() == good


B3J_BASES = ("EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_SURROGATE", "ORACLE_DIAGONAL_GAUSSIAN_PROXY")
B3J_ARMS = {"EXACT": B3J_BASES[0], "FITTED_LW_GAUSSIAN": B3J_BASES[1], "FITTED_LW_T7": B3J_BASES[2]}
B3J_MASKS = ((1, 3, 7, 6), (4, 5, 2, 7))
B3J_EXACT_BETA = ((1.0, -2.0, 0.5), (0.5, 1.0, -1.0))
B3J_C0 = ((1.0, 0.5, 0.0), (0.5, 1.0, 0.25), (0.0, 0.25, 1.0))
B3J_BETA = ((1.0, 1.0, 0.0), (1.0, -1.0, 2.0))
B3J_Q = ((0.5, 0.5, 0.0), (0.5, 0.5, 2.0))
B3J_OUT = {"oracle_basis", "I_surrogate", "I_joint", "vbar_surrogate", "vbar_joint"}
B3J_FIELDS = ("I_surrogate", "I_joint", "vbar_surrogate", "vbar_joint")
B3J_FORBIDDEN = (*B3G_SIDE, "online_masks", "best_sets", "nonoracle_masks", "oracle_masks", "masked_scan",
                 "nonoracle_scan", "oracle_scan", "calibrate_nonoracle", "calibrate_oracle", "projection_diagnostics",
                 "fit_record", "population_frame", "population_drift", "direction_draws", "null_returns",
                 "exact_scores", "path_scores", "direction_information", "setup_bundle", "_verify_partition",
                 "partition", "guarded_partition", "phase_record", "alt_phase", "hold_phase",
                 "confirmatory_from_staging", "confirmatory_inference", "descriptive_contrasts",
                 "selection_telemetry", "hold_selection_telemetry")
B3J_INVALID = ("mask_zero", "mask_above_K", "mask_int64", "mask_one_dim", "mask_rows", "q_negative", "q_nan",
               "beta_shape", "beta_inf", "C0_asymmetric", "C0_indefinite", "C0_singular", "C0_shape", "C0_nan",
               "basis_foreign", "basis_none", "gamma_one", "gamma_nan", "gamma_inf", "K_33")
B3J_PF = (("p_info", B3F_F2), ("p_prefix", B3F_F2), ("p_full", B3F_F2), ("p_info", B3F_HEAD), ("p_prefix", B3F_HEAD))
B3J_GROUPS = {("s1", "RESIDUAL"): ((0.5, 2.0), (0.25, 5.0), (0.125, 6.0), (0.75, 1.5)),
              ("s1", "MARKET"): ((1.0, 3.0), (2.0, 4.0), (2.0, 2.0), (3.0, 6.0), (0.5, 1.0)),
              ("s2", "RESIDUAL"): ((0.5, 3.0),),
              ("s2", "MARKET"): ((0.5, 2.0), (0.5, 3.0), (0.5, 4.0)),
              ("s3", "RESIDUAL"): ((0.25, 2.0), (0.5, 2.0), (1.0, 2.0))}
B3J_V_INVALID = ("duplicate", "rmst_below_one", "rmst_nan", "vbar_inf")


def _b3j_projection(arm):
    if arm == "EXACT":
        beta = np.array(B3J_EXACT_BETA)
        return {"q": 0.5 * beta ** 2, "beta": beta, "C0": np.eye(3), "oracle_basis": B3J_ARMS[arm]}
    return {"q": np.array(B3J_Q), "beta": np.array(B3J_BETA), "C0": np.array(B3J_C0), "oracle_basis": B3J_ARMS[arm]}


def _b3j_kl_hand(b, S):
    b0, b1, b2 = (float(x) for x in b)
    full = 0.9375 * b0 * b0 + b1 * b1 + 0.75 * b2 * b2 - b0 * b1 + 0.25 * b0 * b2 - 0.5 * b1 * b2
    forms = {(0,): 0.5 * b0 * b0, (1,): 0.5 * b1 * b1, (2,): 0.5 * b2 * b2,
             (0, 1): (b0 * b0 - b0 * b1 + b1 * b1) * 2 / 3, (0, 2): 0.5 * (b0 * b0 + b2 * b2),
             (1, 2): (b1 * b1 - 0.5 * b1 * b2 + b2 * b2) * 8 / 15, (0, 1, 2): full * 8 / 11}
    return forms[tuple(S)]


def _b3j_kl_chol(b, C, S):
    idx = list(S)
    L = np.linalg.cholesky(np.asarray(C, dtype=np.float64)[np.ix_(idx, idx)])
    z = np.linalg.solve(L, np.asarray(b, dtype=np.float64)[idx])
    return 0.5 * math.fsum(float(x) * float(x) for x in z)


def _b3j_support(word, K):
    return [j for j in range(K) if (int(word) >> j) & 1]


def _b3j_expect(mask, q, beta, C0, gamma, kl):
    out, K = {k: [] for k in B3J_FIELDS}, np.asarray(q).shape[1]
    for i, row in enumerate(np.asarray(mask).tolist()):
        days = []
        for word in row:
            S = _b3j_support(word, K)
            M = pdb.mixture_cost(len(S), gamma)
            surrogate, joint = math.fsum(float(q[i][j]) for j in S), kl(beta[i], C0, S)
            days.append((surrogate, joint, surrogate / M, joint / M))
        for k, column in zip(B3J_FIELDS, zip(*days)):
            out[k].append(math.fsum(column) / len(row))
    return out


def _b3j_valid(mask, projection, gamma):
    if not (isinstance(projection, dict) and {"q", "beta", "C0", "oracle_basis"} <= set(projection)):
        return False
    q, beta, C0, basis = (projection[k] for k in ("q", "beta", "C0", "oracle_basis"))
    arrays = (mask, q, beta, C0)
    if not (all(isinstance(a, np.ndarray) for a in arrays) and mask.dtype == np.uint32 and mask.ndim == q.ndim == 2
            and all(a.dtype == np.float64 for a in arrays[1:])):
        return False
    K = q.shape[1]
    return bool(min(mask.shape) > 0 and mask.shape[0] == q.shape[0] and q.shape == beta.shape and 1 <= K <= 32
                and C0.shape == (K, K) and all(np.isfinite(a).all() for a in arrays[1:]) and (q >= 0).all()
                and np.array_equal(C0, C0.T) and np.linalg.eigvalsh(C0).min() > 0 and (mask != 0).all()
                and (mask.astype(np.uint64) >> np.uint64(K) == 0).all() and isinstance(basis, str)
                and basis in B3J_BASES and isinstance(gamma, (int, float)) and not isinstance(gamma, bool)
                and math.isfinite(gamma) and gamma > 1)


def _b3j_invalid(case):
    mask, projection, gamma = np.array(B3J_MASKS, dtype=np.uint32), _b3j_projection("FITTED_LW_GAUSSIAN"), GAMMA
    q, beta, C0 = projection["q"], projection["beta"], projection["C0"]
    if case == "mask_zero":
        mask[1, 2] = 0
    elif case == "mask_above_K":
        mask[0, 3] = 8
    elif case == "mask_int64":
        mask = mask.astype(np.int64)
    elif case == "mask_one_dim":
        mask = mask[0]
    elif case == "mask_rows":
        mask = mask[:1]
    elif case == "q_negative":
        q[0, 2] = -0.125
    elif case == "q_nan":
        q[1, 0] = math.nan
    elif case == "beta_shape":
        projection["beta"] = beta[:, :2]
    elif case == "beta_inf":
        beta[0, 1] = math.inf
    elif case == "C0_asymmetric":
        C0[0, 2] = 0.125
    elif case == "C0_indefinite":
        projection["C0"] = np.array([[1.0, 2.0, 0.0], [2.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    elif case == "C0_singular":
        projection["C0"] = np.array([[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    elif case == "C0_shape":
        projection["C0"] = np.eye(2)
    elif case == "C0_nan":
        C0[1, 1] = math.nan
    elif case.startswith("basis"):
        projection["oracle_basis"] = "JOINT_KL_OPTIMAL" if case == "basis_foreign" else None
    elif case.startswith("gamma"):
        gamma = {"gamma_one": 1.0, "gamma_nan": math.nan, "gamma_inf": math.inf}[case]
    else:
        projection = {"q": np.zeros((2, 33)), "beta": np.zeros((2, 33)), "C0": np.eye(33),
                      "oracle_basis": B3J_BASES[1]}
    return mask, projection, gamma


def _b3j_check(out, want, basis):
    assert isinstance(out, dict) and set(out) == B3J_OUT and out["oracle_basis"] == basis
    for k, v in want.items():
        got = np.asarray(out[k])
        assert got.dtype == np.float64 and got.shape == (len(v),) and np.isfinite(got).all(), k
        assert got.tolist() == pytest.approx(v, rel=1e-12, abs=1e-15), k


def _b3j_ranks(xs):
    order, ranks, i = sorted(range(len(xs)), key=lambda k: xs[k]), [0.0] * len(xs), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in order[i:j + 1]:
            ranks[k] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def _b3j_spearman(xs, ys):
    rx, ry = _b3j_ranks(xs), _b3j_ranks(ys)
    mx, my = math.fsum(rx) / len(rx), math.fsum(ry) / len(ry)
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx, syy = math.fsum((a - mx) ** 2 for a in rx), math.fsum((b - my) ** 2 for b in ry)
    return None if sxx == 0 or syy == 0 else sxy / math.sqrt(sxx * syy)


def _b3j_cells():
    return [{"setup_id": s, "application": a, "policy_id": B3J_PF[i][0], "family": B3J_PF[i][1], "vbar_h": v,
             "rmst_h": r} for (s, a), rows in B3J_GROUPS.items() for i, (v, r) in enumerate(rows)]


def _b3j_cells_valid(cells):
    keys = [(c["setup_id"], c["application"], c["policy_id"], c["family"]) for c in cells]
    finite = all(math.isfinite(c["vbar_h"]) and math.isfinite(c["rmst_h"]) and c["rmst_h"] >= 1 for c in cells)
    return bool(len(set(keys)) == len(keys) and finite)


def _b3j_v_invalid(case):
    cells = _b3j_cells()
    if case == "duplicate":
        cells.append(dict(cells[0], vbar_h=9.0, rmst_h=9.0))
    else:
        field, value = {"rmst_below_one": ("rmst_h", 0.5), "rmst_nan": ("rmst_h", math.nan),
                        "vbar_inf": ("vbar_h", math.inf)}[case]
        cells[2][field] = value
    return cells


def test_b3j_masked_alt_information_matches_hand_subset_kl_and_per_day_cost_on_exact_fitted_and_proxy_witnesses(
        monkeypatch):
    import copy
    import inspect
    assert tuple(pio().INFO_BASES) == B3J_BASES and pio().PROJECTION_ARMS == B3J_ARMS
    mask, M = np.array(B3J_MASKS, dtype=np.uint32), {d: pdb.mixture_cost(d, GAMMA) for d in (1, 2, 3)}
    assert len(set(M.values())) == 3 and all(math.isfinite(m) and m > 0 for m in M.values())
    sizes = [[len(_b3j_support(w, 3)) for w in row] for row in B3J_MASKS]
    assert sizes == [[1, 2, 3, 2], [1, 2, 1, 3]]
    cases = {arm: _b3j_projection(arm) for arm in B3J_ARMS}
    assert all(_b3j_valid(mask, p, GAMMA) for p in cases.values())
    exact = cases["EXACT"]
    assert np.array_equal(exact["q"], 0.5 * exact["beta"] ** 2) and np.array_equal(exact["C0"], np.eye(3))
    subsets = [S for d in (1, 2, 3) for S in itertools.combinations(range(3), d)]
    for b in B3J_BETA:
        assert all(_b3j_kl_hand(b, S) == pytest.approx(_b3j_kl_chol(b, B3J_C0, S), rel=1e-12) for S in subsets)
        assert _b3j_kl_hand(b, (0, 1, 2)) == pytest.approx(pdb.kl_mean(np.array(b), np.array(B3J_C0)), rel=1e-12)

    def hand(b, C, S):
        return _b3j_kl_hand(b, S)

    def diagonal(b, C, S):
        return 0.5 * math.fsum(float(b[j]) ** 2 for j in S)

    want = {arm: _b3j_expect(mask, p["q"], p["beta"], p["C0"], GAMMA, diagonal if arm == "EXACT" else hand)
            for arm, p in cases.items()}
    assert want["EXACT"]["I_surrogate"] == want["EXACT"]["I_joint"] == [1.9375, 0.6875]
    assert want["EXACT"]["vbar_joint"][0] == pytest.approx(
        (0.5 / M[1] + 2.5 / M[2] + 2.625 / M[3] + 2.125 / M[2]) / 4, rel=1e-12)
    assert want["EXACT"]["vbar_joint"][1] == pytest.approx(
        (0.5 / M[1] + 0.625 / M[2] + 0.5 / M[1] + 1.125 / M[3]) / 4, rel=1e-12)
    fitted = want["FITTED_LW_GAUSSIAN"]
    assert fitted["I_surrogate"] == [0.75, 2.0] and want["FITTED_LW_T7"] == fitted
    assert fitted["I_joint"] == pytest.approx(
        [(0.5 + 2 / 3 + 7.5 / 11 + 8 / 15) / 4, (2.0 + 2.5 + 0.5 + 59.5 / 11) / 4], rel=1e-12)
    assert all(abs(a - b) > 1e-3 for a, b in zip(fitted["I_joint"], fitted["I_surrogate"]))
    for i, row in enumerate(sizes):
        pooled = fitted["I_joint"][i] / (math.fsum(M[d] for d in row) / len(row))
        assert abs(fitted["vbar_joint"][i] - pooled) > 1e-9 * abs(pooled)
    frozen = copy.deepcopy((mask, cases))
    api = _kernel("masked_alt_information")
    assert list(inspect.signature(api).parameters) == ["mask_bits", "projection", "gamma_M"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        outs = {arm: api(mask, p, GAMMA) for arm, p in cases.items()}
    np.testing.assert_equal((mask, cases), frozen)
    for arm, out in outs.items():
        _b3j_check(out, want[arm], B3J_ARMS[arm])


@pytest.mark.parametrize("case", B3J_INVALID)
def test_b3j_masked_alt_information_refuses_invalid_masks_covariance_provenance_or_gamma_before_any_information(
        monkeypatch, case):
    mask, projection, gamma = _b3j_invalid(case)
    base = _b3j_projection("FITTED_LW_GAUSSIAN")
    assert _b3j_valid(np.array(B3J_MASKS, dtype=np.uint32), base, GAMMA) and not _b3j_valid(mask, projection, gamma)
    api = _kernel("masked_alt_information")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        with pytest.raises(ValueError):
            api(mask, projection, gamma)


def test_b3j_masked_alt_information_reads_the_full_committed_primary_alt_mask_only_after_its_hashes_verify(
        tmp_path, monkeypatch):
    import copy
    import hashlib
    import inspect
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, verify, alt_record = _b3g_references(fixture, records), _kernel("_verify_partition"), records[5]
    did, primary, ups, cid = ref["did"], ref["primary"], ref["ups"], ref["cids"][B3F_P[0]]
    params, n = desc["science"]["parameters"], desc["sizes"]["ALT"]
    H, K, gamma = params["H"], params["K"], float(params["gamma_M"])
    assert (H, K, n) == (6, 20, 2) and math.isfinite(gamma) and gamma > 1
    key = ["ALT", *primary, "RESIDUAL", B3F_F2]
    sha, rows, arrays = verify(staging, did, ups["ALT"], key)
    payload = _partition_stem(staging, did, ups["ALT"], key).with_suffix(".npz")
    [part] = [r for r in alt_record["partitions"] if r["key"] == key]
    assert sha == hashlib.sha256(payload.read_bytes()).hexdigest() == part["sha256"] and rows == part["n_rows"] == n
    assert alt_record["upstream"] == ups["ALT"]
    assert cid in alt_record["derived"]["trials"][pdb.canon(key)]["calibration_ids"]
    mask, first = arrays["mask_" + cid], arrays["first_" + cid]
    assert mask.dtype == np.uint32 and mask.shape == (n, H) and np.array_equal(first, ref["alt"][B3F_F2][B3F_P[0]])
    assert ((first == -1) | ((first >= 1) & (first <= H))).all()
    basis = B3J_BASES[1]
    assert pio().PROJECTION_ARMS[primary[0]] == basis
    frame_key = ["frame", desc["campaign"], primary[1]]
    fit_key = ["fit", desc["campaign"], *primary]
    setup = _kernel("_setup_cache")
    frame, fit = (setup(verify(staging, did, {}, k)[2], k) for k in (frame_key, fit_key))
    eligible = records[0]["derived"]["setups"][pdb.canon(primary)]["applications"]["RESIDUAL"]["universe"]
    delta = np.array([_b3e_delta(primary[1], B3F_F2, i) for i in range(n)])
    diag = _kernel("projection_diagnostics")(frame, fit, eligible, delta, primary[0])
    q, beta, C0 = (diag[k] for k in ("q", "beta", "C0"))
    assert diag["oracle_basis"] == basis and np.shape(q) == np.shape(beta)
    assert np.allclose(q, 0.5 * np.asarray(beta) ** 2, rtol=1e-10, atol=1e-12)
    projection = {"q": q, "beta": beta, "C0": C0, "oracle_basis": diag["oracle_basis"]}
    full = np.uint32((1 << K) - 1)
    tail = mask.copy()
    tail[:, -1] = np.where(tail[:, -1] == full, np.uint32(1), full)
    assert _b3j_valid(mask, projection, gamma) and _b3j_valid(tail, projection, gamma)
    assert not np.array_equal(tail[:, -1], mask[:, -1]) and np.array_equal(tail[:, :-1], mask[:, :-1])
    want, moved = (_b3j_expect(m, q, beta, C0, gamma, _b3j_kl_chol) for m in (mask, tail))
    assert all(abs(a - b) > 1e-9 for k in ("I_joint", "vbar_joint") for a, b in zip(want[k], moved[k]))
    before, frozen = _tree(staging), copy.deepcopy((mask, tail, projection))
    api = _kernel("masked_alt_information")
    assert list(inspect.signature(api).parameters) == ["mask_bits", "projection", "gamma_M"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        out, shifted = api(mask, projection, gamma), api(tail, projection, gamma)
    assert _tree(staging) == before
    np.testing.assert_equal((mask, tail, projection), frozen)
    _b3j_check(out, want, basis)
    _b3j_check(shifted, moved, basis)


def test_b3j_v_rmst_diagnostic_ranks_each_setup_application_group_apart_and_leaves_undefined_groups_none(monkeypatch):
    import copy
    import inspect
    cells = _b3j_cells()
    assert _b3j_cells_valid(cells) and len(cells) == 16
    want = {key: (len(rows), _b3j_spearman([v for v, _ in rows], [r for _, r in rows]))
            for key, rows in B3J_GROUPS.items()}
    assert want[("s1", "RESIDUAL")] == (4, -1.0) and want[("s2", "RESIDUAL")] == (1, None)
    assert want[("s1", "MARKET")][1] == pytest.approx(8 / math.sqrt(95), rel=1e-12)
    assert want[("s2", "MARKET")] == (3, None) and want[("s3", "RESIDUAL")] == (3, None)
    pooled = [row for key, rows in B3J_GROUPS.items() if key[0] == "s1" for row in rows]
    rho = _b3j_spearman([v for v, _ in pooled], [r for _, r in pooled])
    assert rho is not None and all(abs(rho - want[k][1]) > 1e-3 for k in (("s1", "RESIDUAL"), ("s1", "MARKET")))
    frozen = copy.deepcopy(cells)
    api = _kernel("v_rmst_diagnostic")
    assert list(inspect.signature(api).parameters) == ["cells"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        out, flipped = api(cells), api(cells[::-1])
    assert cells == frozen
    for got in (out, flipped):
        assert type(got) is list and len(got) == len(want)
        rows = {(r["setup_id"], r["application"]): r for r in got}
        assert set(rows) == set(want)
        for key, (n, rho) in want.items():
            row = rows[key]
            assert set(row) == {"setup_id", "application", "n_cells", "spearman_rho", "status"}, key
            assert row["n_cells"] == n and row["status"] == "DESCRIPTIVE_V_RMST", key
            if rho is None:
                assert row["spearman_rho"] is None, key
            else:
                assert isinstance(row["spearman_rho"], float), key
                assert row["spearman_rho"] == pytest.approx(rho, abs=1e-12), key


@pytest.mark.parametrize("case", B3J_V_INVALID)
def test_b3j_v_rmst_diagnostic_refuses_duplicate_cells_or_invalid_values_before_any_rank(monkeypatch, case):
    cells = _b3j_v_invalid(case)
    assert _b3j_cells_valid(_b3j_cells()) and not _b3j_cells_valid(cells)
    api = _kernel("v_rmst_diagnostic")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        with pytest.raises(ValueError):
            api(cells)


B3K_PCS = [2, 3, 4]
B3K_FITTED = ((1, 3), (2, 4))
B3K_VANISHING = ((1, 1), (2, 2))
B3K_EXACT = ((1, 1), (1, 3), (2, 2))
B3K_C, B3K_VAR0 = (0.5, -0.25, 0.0), (0.5, 2.0, 1.0)
B3K_WANT = {1: {"variance_term": [-0.5, 1.0, 0.0], "bias": [-0.125, 0.53125, 0.0]},
            4: {"variance_term": [-0.125, 0.25, 0.0], "bias": [0.0625, 0.15625, 0.0]}}
B3K_FIELDS = ("fitted_frequency", "exact_frequency", "fitted_over_exact", "center_sq", "variance_term", "bias")
B3K_OUT = {"axis_pcs", "oracle_basis", "m", *B3K_FIELDS}
B3K_FORBIDDEN = (*B3J_FORBIDDEN, "masked_alt_information", "v_rmst_diagnostic", "_setup_cache", "_lineage",
                 "_load_phase", "_staged_design")
B3K_INVALID = ("fitted_role", "exact_role", "axis_order", "axis_shift", "axis_length", "H_mismatch", "K_mismatch",
               "count_above", "count_negative", "count_length", "basis_exact", "basis_none", "c_nan", "c_length",
               "var0_inf", "var0_negative", "m_zero", "m_negative", "m_bool")
B3K_HUGE = 1.4e154


def _b3k_hold(masks, cid, K=3, pcs=B3K_PCS):
    telemetry = _kernel("selection_telemetry")(np.array(masks, dtype=np.uint32), K, B3I_H)
    return {"role": "HOLD_NULL", "setup_id": "setup-" + cid, "calibration_id": cid, "axis_pcs": list(pcs),
            "hold_phase_digest": "0" * 64, "hold_payload_sha256": "1" * 64, "telemetry": telemetry}


def _b3k_base():
    projection = {"c": np.array(B3K_C), "var0": np.array(B3K_VAR0), "oracle_basis": B3J_BASES[1]}
    return _b3k_hold(B3K_FITTED, "cal-fitted"), _b3k_hold(B3K_EXACT, "cal-exact"), projection, 4


def _b3k_valid(fitted, exact, projection, m):
    holds = (fitted, exact)
    if not all(isinstance(h, dict) and h.get("role") == "HOLD_NULL" and isinstance(h.get("telemetry"), dict)
               for h in holds):
        return False
    pcs, tels = fitted["axis_pcs"], [h["telemetry"] for h in holds]
    K, H = tels[0]["K"], tels[0]["H"]
    if not (type(pcs) is list and exact["axis_pcs"] == pcs and all(type(k) is int for k in pcs) and len(pcs) == K
            and all((t["K"], t["H"]) == (K, H) for t in tels)):
        return False
    for t in tels:
        counts, total = t["axis_counts"], t["n"] * t["H"]
        if not (type(counts) is list and len(counts) == K and all(type(a) is int and 0 <= a <= total for a in counts)):
            return False
    if not (isinstance(projection, dict) and projection.get("oracle_basis") in B3J_BASES[1:]):
        return False
    c, var0 = (np.asarray(projection.get(k)) for k in ("c", "var0"))
    if not all(v.dtype == np.float64 and v.shape == (K,) and np.isfinite(v).all() for v in (c, var0)):
        return False
    return bool((var0 >= 0).all() and type(m) is int and m >= 1)


def _b3k_invalid(case):
    fitted, exact, projection, m = _b3k_base()
    if case == "fitted_role":
        fitted["role"] = "ALT"
    elif case == "exact_role":
        exact["role"] = "CAL_NULL"
    elif case == "axis_order":
        exact["axis_pcs"] = [3, 2, 4]
    elif case == "axis_shift":
        exact["axis_pcs"] = [1, 2, 3]
    elif case == "axis_length":
        fitted["axis_pcs"], exact["axis_pcs"] = [2, 3], [2, 3]
    elif case == "H_mismatch":
        exact = _b3k_hold(((1, 1, 2), (3, 2, 1)), "cal-exact")
    elif case == "K_mismatch":
        exact = _b3k_hold(B3K_EXACT, "cal-exact", 4, [2, 3, 4, 5])
    elif case == "count_above":
        fitted["telemetry"]["axis_counts"][0] = 5
    elif case == "count_negative":
        exact["telemetry"]["axis_counts"][2] = -1
    elif case == "count_length":
        fitted["telemetry"]["axis_counts"] = fitted["telemetry"]["axis_counts"][:2]
    elif case.startswith("basis"):
        projection["oracle_basis"] = B3J_BASES[0] if case == "basis_exact" else None
    elif case == "c_nan":
        projection["c"][1] = math.nan
    elif case == "c_length":
        projection["c"] = projection["c"][:2]
    elif case == "var0_inf":
        projection["var0"][0] = math.inf
    elif case == "var0_negative":
        projection["var0"][0] = -0.5
    else:
        m = {"m_zero": 0, "m_negative": -4, "m_bool": True}[case]
    return fitted, exact, projection, m


def _b3k_check(out, want, rel=1e-12, tol=1e-15):
    assert isinstance(out, dict) and set(out) == B3K_OUT
    assert [int(k) for k in out["axis_pcs"]] == want["axis_pcs"] and out["oracle_basis"] == want["oracle_basis"]
    assert isinstance(out["m"], (int, np.integer)) and not isinstance(out["m"], bool) and out["m"] == want["m"]
    for k in B3K_FIELDS:
        got = list(out[k])
        assert len(got) == len(want[k]), k
        for g, w in zip(got, want[k]):
            if w is None:
                assert g is None, k
            else:
                assert isinstance(g, (float, np.floating)) and math.isfinite(g), k
                assert float(g) == pytest.approx(w, rel=rel, abs=tol), k


def test_b3k_null_axis_bias_diagnostic_reports_hand_frequencies_ratios_and_signed_window_bias_of_matching_holds(
        monkeypatch):
    import copy
    import inspect
    from fractions import Fraction
    fitted, exact, projection, _ = _b3k_base()
    vanishing = _b3k_hold(B3K_VANISHING, "cal-fitted")
    holds = {"fitted": (fitted, B3K_FITTED), "vanishing": (vanishing, B3K_VANISHING), "exact": (exact, B3K_EXACT)}
    for hold, masks in holds.values():
        _b3i_check(hold["telemetry"], _b3i_expect(np.array(masks, dtype=np.uint32), 3, B3I_H))
    freq = {k: [Fraction(a, h["telemetry"]["n"] * h["telemetry"]["H"]) for a in h["telemetry"]["axis_counts"]]
            for k, (h, _) in holds.items()}
    assert freq["fitted"] == [Fraction(1, 2), Fraction(1, 2), Fraction(1, 4)]
    assert freq["vanishing"] == [Fraction(1, 2), Fraction(1, 2), 0]
    assert freq["exact"] == [Fraction(2, 3), Fraction(1, 2), 0]
    assert [(h["telemetry"]["n"], h["telemetry"]["H"]) for h, _ in holds.values()] == [(2, 2), (2, 2), (3, 2)]
    c, var0 = [Fraction(x) for x in B3K_C], [Fraction(x) for x in B3K_VAR0]
    center = [x * x for x in c]
    assert center == [Fraction(1, 4), Fraction(1, 16), 0]
    terms = {}
    for m in (1, 4):
        term = [(v - 1) / m for v in var0]
        bias = [(a + b) / 2 for a, b in zip(center, term)]
        assert term[0] < 0 < term[1] and term[2] == 0
        assert [float(x) for x in term] == B3K_WANT[m]["variance_term"]
        assert [float(x) for x in bias] == B3K_WANT[m]["bias"]
        terms[m] = (term, bias)
    assert terms[1][1][0] < 0 < terms[4][1][0]
    calls, wants = [], []
    for basis in B3J_BASES[1:]:
        for m in (1, 4):
            for name in ("fitted", "vanishing"):
                ratio = [f / e if e else None for f, e in zip(freq[name], freq["exact"])]
                calls.append((holds[name][0], exact, {**projection, "oracle_basis": basis}, m))
                wants.append({"axis_pcs": B3K_PCS, "oracle_basis": basis, "m": m,
                              "fitted_frequency": [float(x) for x in freq[name]],
                              "exact_frequency": [float(x) for x in freq["exact"]],
                              "fitted_over_exact": [None if r is None else float(r) for r in ratio],
                              "center_sq": [float(x) for x in center],
                              "variance_term": [float(x) for x in terms[m][0]],
                              "bias": [float(x) for x in terms[m][1]]})
    assert wants[0]["fitted_over_exact"] == wants[1]["fitted_over_exact"] == [0.75, 1.0, None]
    assert wants[0]["fitted_frequency"] != wants[1]["fitted_frequency"]
    assert all(_b3k_valid(*call) for call in calls)
    frozen = copy.deepcopy(calls)
    api = _kernel("null_axis_bias_diagnostic")
    assert list(inspect.signature(api).parameters) == ["fitted_hold", "exact_hold", "projection", "m"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3K_FORBIDDEN)
        _b3f_seal(mp)
        outs = [api(*call) for call in calls]
    np.testing.assert_equal(calls, frozen)
    for out, want in zip(outs, wants):
        _b3k_check(out, want)
    for a, b in zip(outs[:2], outs[2:4]):
        assert all(list(a[k]) == list(b[k]) for k in B3K_FIELDS[:4])
        assert list(a["bias"]) != list(b["bias"])


@pytest.mark.parametrize("case", B3K_INVALID)
def test_b3k_null_axis_bias_diagnostic_refuses_incoherent_roles_axes_counts_bases_or_window_before_any_bias(
        monkeypatch, case):
    args = _b3k_invalid(case)
    assert _b3k_valid(*_b3k_base()) and not _b3k_valid(*args)
    api = _kernel("null_axis_bias_diagnostic")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3K_FORBIDDEN)
        _b3f_seal(mp)
        with pytest.raises(ValueError):
            api(*args)


def test_b3k_null_axis_bias_diagnostic_joins_verified_fitted_and_exact_hold_telemetry_with_the_frozen_fitted_center(
        tmp_path, monkeypatch):
    import copy
    import hashlib
    import inspect
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, verify, phases = _b3g_references(fixture, records), _kernel("_verify_partition"), staging / "phases"
    setup_record, dev_record, cal_record, _, hold_record, _ = records
    did, primary, sid, ups, cid = ref["did"], ref["primary"], ref["sid"], ref["ups"], ref["cids"][B3F_P[0]]
    params, thresholds = desc["science"]["parameters"], cal_record["derived"]["thresholds"]
    checks, label = hold_record["derived"]["null_checks"], B3F_P[0]
    H, K, m = params["H"], params["K"], int(label.rsplit("_W", 1)[1])
    assert (H, K, m) == (6, 20, 128) and B2W_SETUPS[0][0] == "EXACT" and primary == list(B2W_SETUPS[1])
    coords, cells = {"FITTED": primary, "EXACT": list(B2W_SETUPS[0])}, {}
    for arm, setup in coords.items():
        name = pdb.canon(setup)
        meta = setup_record["derived"]["setups"][name]["applications"]["RESIDUAL"]
        rows = dev_record["derived"]["setups"][name]["RESIDUAL"]["policies"]["PRIMARY"]
        assert label in rows and type(rows[label]["policy_id"]) is str
        triple = (meta["setup_id"], rows[label]["policy_id"], None)
        [c] = [c for c, t in thresholds.items() if (t["setup_id"], t["policy_id"], t.get("family")) == triple]
        assert (checks[c]["setup_id"], checks[c]["policy_id"], checks[c].get("family")) == triple
        h = thresholds[c]["h"]
        assert meta["universe"] == list(range(2, 22)) and type(h) is float and math.isfinite(h)
        cells[arm] = {"sid": meta["setup_id"], "cid": c, "h": h, "key": ["HOLD_NULL", *setup, "RESIDUAL"]}
    assert (cells["FITTED"]["sid"], cells["FITTED"]["cid"]) == (sid, cid)
    assert cells["EXACT"]["sid"] != sid and cells["EXACT"]["cid"] != cid
    for arm, cell in cells.items():
        sha, rows, arrays = verify(staging, did, ups["HOLD"], cell["key"])
        payload = _partition_stem(staging, did, ups["HOLD"], cell["key"]).with_suffix(".npz")
        [part] = [r for r in hold_record["partitions"] if r["key"] == cell["key"]]
        assert sha == hashlib.sha256(payload.read_bytes()).hexdigest() == part["sha256"] and rows == part["n_rows"] >= 1
        mask = arrays["mask_" + cell["cid"]]
        assert mask.dtype == np.uint32 and mask.shape == (rows, H) and _b3i_valid(mask, K, cell["h"])
        if arm == "FITTED":
            assert rows == 5 and np.array_equal(arrays["first_" + cid], ref["hold"][label])
        telemetry = _b3i_expect(mask, K, cell["h"])
        assert (telemetry["n"], telemetry["H"], telemetry["K"]) == (rows, H, K)
        assert sum(telemetry["d_counts"]) == rows * H and telemetry["d_counts"][0] == 0
        cell.update(sha=sha, n=rows, telemetry=telemetry, frequency=[a / (rows * H) for a in telemetry["axis_counts"]])
    frame_key, fit_key = ["frame", desc["campaign"], primary[1]], ["fit", desc["campaign"], *primary]
    setup_cache, N, eligible = _kernel("_setup_cache"), primary[1], list(range(2, 22))
    frame, fit = (setup_cache(verify(staging, did, {}, k)[2], k) for k in (frame_key, fit_key))
    projection = _kernel("projection_diagnostics")(frame, fit, eligible, np.empty((0, N)), primary[0])
    basis = B3J_BASES[1]
    assert projection["oracle_basis"] == basis == pio().PROJECTION_ARMS[primary[0]]
    assert projection["beta"].shape == projection["q"].shape == (0, K) and projection["I_joint"].shape == (0,)
    hand = _b2e_reference(frame, fit, eligible, np.empty((0, N)))
    c, var0 = hand["c"], [hand["C0"][i][i] for i in range(K)]
    np.testing.assert_allclose(projection["c"], c, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(projection["var0"], var0, rtol=1e-12, atol=1e-12)
    assert np.array_equal(projection["var0"], np.diag(projection["C0"]))
    assert any(x != 0.0 for x in c) and any(abs(v - 1.0) > 1e-9 for v in var0) and min(var0) > 0
    F, E = cells["FITTED"]["frequency"], cells["EXACT"]["frequency"]
    expect = {"axis_pcs": eligible, "oracle_basis": basis, "m": m, "fitted_frequency": F, "exact_frequency": E,
              "fitted_over_exact": [f / e if e > 0 else None for f, e in zip(F, E)],
              "center_sq": [x * x for x in c], "variance_term": [(v - 1.0) / m for v in var0],
              "bias": [0.5 * (x * x + (v - 1.0) / m) for x, v in zip(c, var0)]}
    alt_key = ["ALT", *primary, "RESIDUAL", B3F_F2]
    stem = _partition_stem(staging, did, ups["ALT"], alt_key)
    banned = [phases / "ALT.json", stem.with_suffix(".npz"), stem.with_suffix(".json")]
    assert all(p.is_file() for p in banned) and hold_record["phase_digest"] == ups["ALT"]["HOLD"]
    banned[0].write_text("poisoned")
    banned[1].write_bytes(b"poisoned")
    with pytest.raises(pdb.PartitionMismatch):
        verify(staging, did, ups["ALT"], alt_key)
    before, reader = _tree(staging), _kernel("hold_selection_telemetry")
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3g_forbid(mp, *B3I_FORBIDDEN)
        _b3i_no_reads(mp, banned)
        held = {arm: reader(cfg, "full", context, list(cell["key"]), cell["cid"]) for arm, cell in cells.items()}
    after = _tree(staging)
    assert set(after) == set(before) and "status.json" not in after
    assert all(after[rel] == data for rel, data in before.items() if rel != "resources.json")
    for arm, out in held.items():
        cell = cells[arm]
        assert isinstance(out, dict) and set(out) == B3I_OUT
        assert (out["role"], out["setup_id"], out["calibration_id"]) == ("HOLD_NULL", cell["sid"], cell["cid"])
        assert list(out["axis_pcs"]) == eligible and out["hold_phase_digest"] == hold_record["phase_digest"]
        assert out["hold_payload_sha256"] == cell["sha"]
        _b3i_check(out["telemetry"], cell["telemetry"])
    assert _b3k_valid(held["FITTED"], held["EXACT"], projection, m)
    frozen, quiet = copy.deepcopy((held, projection)), _tree(staging)
    api = _kernel("null_axis_bias_diagnostic")
    assert list(inspect.signature(api).parameters) == ["fitted_hold", "exact_hold", "projection", "m"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3K_FORBIDDEN)
        _b3f_seal(mp)
        _b3i_no_reads(mp, banned)
        out = api(held["FITTED"], held["EXACT"], projection, m)
    assert _tree(staging) == quiet
    np.testing.assert_equal((held, projection), frozen)
    _b3k_check(out, expect, rel=1e-9, tol=1e-12)


def test_b3k_masked_alt_information_keeps_a_finite_path_mean_when_repeated_near_max_days_overflow_a_daily_fsum(
        monkeypatch):
    import copy
    frame = {"V": np.eye(2), "lam": np.ones(2), "mean": np.zeros(2)}
    fit = {k: v.copy() for k, v in frame.items()}
    diag = _kernel("projection_diagnostics")(frame, fit, [1, 2], np.array([[B3K_HUGE, 0.0]]), "EXACT")
    basis, q, beta = diag["oracle_basis"], diag["q"], diag["beta"]
    assert basis == B3J_BASES[0] and np.array_equal(diag["C0"], np.eye(2)) and beta.tolist() == [[B3K_HUGE, 0.0]]
    big, cost = float(q[0, 0]), pdb.mixture_cost(1, GAMMA)
    assert q[0, 1] == 0.0 and math.isfinite(big) and big == pytest.approx(9.8e307, rel=1e-14)
    assert float(diag["I_joint"][0]) == pytest.approx(9.8e307, rel=1e-14) and math.isinf(big + big)
    assert math.isfinite(cost) and cost > 0
    projection = {k: diag[k] for k in ("q", "beta", "C0", "oracle_basis")}
    one, two = np.array([[1]], dtype=np.uint32), np.array([[1, 1]], dtype=np.uint32)
    assert _b3j_valid(one, projection, GAMMA) and _b3j_valid(two, projection, GAMMA)
    frozen = copy.deepcopy((one, two, projection))
    api = _kernel("masked_alt_information")
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        day = api(one, projection, GAMMA)
        _b3j_check(day, {"I_surrogate": [big], "I_joint": [big], "vbar_surrogate": [big / cost],
                         "vbar_joint": [big / cost]}, basis)
        for k in ("I_surrogate", "I_joint"):
            assert float(day[k][0]) == pytest.approx(9.8e307, rel=1e-14), k
        days = api(two, projection, GAMMA)
    np.testing.assert_equal((one, two, projection), frozen)
    _b3j_check(days, {k: day[k].tolist() for k in B3J_FIELDS}, basis)


def test_b3l_t65_h2_head_row_ignores_a_committed_f2_info_decoy_and_poisoned_smoke_outputs_on_staged_replay(
        tmp_path, monkeypatch):
    import collections
    import copy
    import hashlib
    import inspect
    real = np.random.SeedSequence, np.random.default_rng
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, module, phases, names = _b3g_references(fixture, records), pio(), staging / "phases", _kernel("PHASES")
    verify, digest_of, rows_of = (_kernel(n) for n in ("_verify_partition", "_phase_digest", "_partition_rows"))
    infer, info, H = _kernel("confirmatory_inference"), B3F_P[0], desc["science"]["parameters"]["H"]
    did, primary, ups, alt_record = ref["did"], ref["primary"], ref["ups"], records[5]
    prior, resources = names[:names.index("ALT")], (staging / "resources.json").relative_to(tmp_path).as_posix()
    signature, calls, seen, outs, holder = inspect.signature(infer), [], [], [], [context]
    monkeypatch.chdir(tmp_path)

    def spy(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        calls.append(dict(bound.arguments))
        return infer(*args, **kwargs)

    def full_only(name, received):
        def call(*args, **kwargs):
            mode = kwargs["mode"] if "mode" in kwargs else args[1]
            assert mode == "full", f"B3l staged replay reached {name} in mode {mode!r}"
            return received(*args, **kwargs)
        return call

    def invoke(token, banned):
        before = _tree(tmp_path)
        with monkeypatch.context() as mp:
            _b3b_guard(mp, state, *B3B_TRAPPED)
            _b3g_forbid(mp, *B3G_SIDE)
            _b3g_draws(mp, real, ref["words"], seen, phases)
            mp.setattr(module, "confirmatory_inference", spy)
            for name in ("design_descriptor", "seed_plan"):
                mp.setattr(module, name, full_only(name, getattr(module, name)))
            _b3i_no_reads(mp, banned)
            outs.append(_kernel("confirmatory_from_staging")(cfg, "full", holder[0]))
            holder[0] = _kernel("start_invocation")(staging, authority, plan, token)
        after = _tree(tmp_path)
        assert set(after) == set(before) and len(calls) == len(outs) and len(seen) == 2 * len(outs)
        assert all(after[rel] == data for rel, data in before.items() if rel != resources)
        assert sorted(seen[-2:]) == sorted([B3F_F2, B3F_HEAD])
        return outs[-1]

    out = invoke("invocation-8", [])
    _b3g_same_call(calls[0], desc, ref)
    assert out["alt_phase_digest"] == alt_record["phase_digest"] and set(out["claims"]) == set(B3G_CLAIMS)

    name = "first_" + ref["cids"][info]
    alt_key, head_key = (["ALT", *primary, "RESIDUAL", f] for f in (B3F_F2, B3F_HEAD))
    keys = [row["key"] for row in alt_record["partitions"]]
    assert alt_key in keys and head_key in keys and rows_of(staging, did, ups["ALT"], keys) == alt_record["partitions"]
    old_digest = digest_of(did, "ALT", ups["ALT"], alt_record["partitions"], alt_record["derived"])
    assert old_digest == alt_record["phase_digest"]
    old_sha, n_rows, old = verify(staging, did, ups["ALT"], alt_key)
    head_sha, _, head = verify(staging, did, ups["ALT"], head_key)
    first = old[name]
    assert first.dtype.kind == "i" and first.shape == (n_rows,) and np.array_equal(first, ref["alt"][B3F_F2][info])
    effective = np.where(first == -1, H, first)
    censor = bool((effective < H).any())
    decoy, poisoned = np.full_like(first, -1 if censor else 1), float(H) if censor else 1.0
    assert decoy.dtype == first.dtype and decoy.shape == first.shape
    assert float(np.where(decoy == -1, H, decoy).mean()) == poisoned != float(effective.mean())
    arrays, pre = {**old, name: decoy}, _tree(staging)
    payload = _npz_bytes(**arrays)
    _put_partition(staging, did, ups["ALT"], alt_key, payload, n_rows)
    new_sha, new_rows, got = verify(staging, did, ups["ALT"], alt_key)
    assert new_sha == hashlib.sha256(payload).hexdigest() != old_sha and new_rows == n_rows and set(got) == set(old)
    assert all(got[k].dtype == v.dtype and got[k].shape == v.shape and np.array_equal(got[k], v)
               for k, v in arrays.items())
    assert [k for k in sorted(old) if not np.array_equal(got[k], old[k])] == [name]
    record = copy.deepcopy(alt_record)
    [row] = [r for r in record["partitions"] if r["key"] == alt_key]
    row["sha256"] = new_sha
    record["phase_digest"] = digest_of(did, "ALT", ups["ALT"], record["partitions"], record["derived"])
    (phases / "ALT.json").write_text(pdb.canon(record) + "\n")
    assert record["phase_digest"] != alt_record["phase_digest"] and record["upstream"] == alt_record["upstream"]
    assert rows_of(staging, did, ups["ALT"], keys) == record["partitions"]
    assert [r["key"] for r, s in zip(record["partitions"], alt_record["partitions"]) if r != s] == [alt_key]
    assert _kernel("_load_phase")(staging, desc, did, "ALT", dict(zip(prior, records[:len(prior)]))) == record
    assert verify(staging, did, ups["ALT"], head_key)[0] == head_sha
    np.testing.assert_equal(verify(staging, did, ups["ALT"], head_key)[2], head)
    stem, mid = _partition_stem(staging, did, ups["ALT"], alt_key), _tree(staging)
    changed = {rel for rel in set(pre) | set(mid) if pre.get(rel) != mid.get(rel)}
    parts = {stem.with_suffix(s).relative_to(staging).as_posix() for s in (".npz", ".json")}
    assert changed == parts | {"phases/ALT.json"}
    assert all(mid[f"phases/{p}.json"] == pre[f"phases/{p}.json"] for p in prior)

    kappas = {k: desc["science"]["head"][k] for k in ("kappa_det", "kappa_geo")}
    wrong = {k: v / 2 for k, v in kappas.items()}
    assert all(wrong[k] != kappas[k] for k in kappas) and did != "f" * 64 and record["phase_digest"] != "d" * 64
    smoke = {"logs/pca_info_online/smoke/staging/x/design.json":
             {"design_id": "f" * 64, "descriptor": {"mode": "smoke", "science": {"head": wrong}}},
             "results/pca_info_online/smoke/manifest.json":
             {"status": "PUBLISHED", "design_id": "e" * 64, "alt_phase_digest": "d" * 64,
              "claims": {"H2": {"family": B3F_HEAD, "u_prefix": 1.0, "ni_upper": -1.0, "geometry": None,
                                "control": {"valid": True, **wrong}}}}}
    for rel, body in smoke.items():
        (tmp_path / rel).parent.mkdir(parents=True)
        (tmp_path / rel).write_text(pdb.canon(body))

    again = invoke("invocation-9", [tmp_path / rel for rel in smoke])
    assert collections.Counter(seen) == collections.Counter({B3F_F2: 2, B3F_HEAD: 2})
    decoyed = {**ref, "alt": {**ref["alt"], B3F_F2: {**ref["alt"][B3F_F2], info: decoy}}}
    _b3g_same_call(calls[1], desc, decoyed)
    assert set(again) == set(out) and all(again[k] == out[k] for k in ("design_id", "setup", "setup_id"))
    boot_keys = {f: list(k) for f, k in again["bootstrap_keys"].items()}
    assert boot_keys == {f: list(k) for f, k in out["bootstrap_keys"].items()} == ref["keys"]
    assert again["alt_phase_digest"] == record["phase_digest"] != out["alt_phase_digest"]
    h2 = out["claims"]["H2"]
    assert {"geometry", "delta_NI", "ni_upper", "u_prefix", "control"} <= set(h2) and h2["geometry"] == ref["geometry"]
    assert set(again["claims"]["H2"]) == set(h2)
    np.testing.assert_equal(again["claims"]["H2"], h2)
    for key in ("H1", "H3"):
        was, now = out["claims"][key], again["claims"][key]
        assert now["rmst_info"] == poisoned != was["rmst_info"] and now["rmst_comparator"] == was["rmst_comparator"]
    want = infer(desc, ref["hold"], decoyed["alt"], ref["states"], ref["boot"], ref["geometry"])
    for key in B3G_CLAIMS:
        np.testing.assert_equal({k: again["claims"][key][k] for k in want[key]}, want[key], err_msg=key)


B3M_MASKS = ((4, 3, 7, 6), (1, 6, 2, 5))
B3M_EXACT_BETA = ((1.0, -2.0, 0.0), (0.5, 1.0, -1.0))
B3M_S2 = 0.25
B3M_WANT = {"EXACT": ([37 / 6, 2.875], [37 / 6, 2.875]), "FITTED": ([13 / 6, 7.0], [91 / 55, 7.7])}
B3M_STATIC = (7.338098196831849, 73.3809819683185)
B3M_RATIO_OUT = {"oracle_basis", "rho_surrogate", "rho_joint"}
B3M_ALIGN_MASKS = ((1, 3, 4, 2), (4, 4, 1, 7), (2, 2, 2, 2))
B3M_ORACLE_WORDS = (3, 5, 2)
B3M_ALIGN_OUT = {"first_match", "jaccard_mean"}
B3M_FORBIDDEN = (*B3J_FORBIDDEN, "v_rmst_diagnostic", "null_axis_bias_diagnostic", "_setup_cache", "_lineage",
                 "_load_phase", "_staged_design", "common_prior", "mixture_cost", "design_descriptor", "seed_plan",
                 "frozen_policy")
B3M_RATIO_INVALID = ("s2_zero", "s2_negative", "s2_nan", "s2_inf", "s2_bool", "s2_text", "s2_array", "s2_none",
                     "mask_zero", "mask_above_K", "mask_int64", "mask_one_dim", "mask_rows", "q_negative", "q_nan",
                     "beta_shape", "C0_asymmetric", "C0_indefinite", "basis_foreign", "basis_none", "K_33")
B3M_ALIGN_INVALID = ("oracle_dynamic", "candidate_zero", "oracle_zero", "candidate_above_K", "oracle_above_K",
                     "oracle_shape", "candidate_int64", "oracle_int64", "one_dim", "no_steps", "K_zero", "K_33",
                     "K_bool")


def _b3m_exact():
    beta = np.array(B3M_EXACT_BETA)
    return {"q": 0.5 * beta ** 2, "beta": beta, "C0": np.eye(3), "oracle_basis": B3J_BASES[0]}


def _b3m_diagonal(b, C, S):
    return 0.5 * math.fsum(float(b[j]) ** 2 for j in S)


def _b3m_prior_valid(s2):
    return bool(isinstance(s2, (int, float, np.integer, np.floating)) and not isinstance(s2, (bool, np.bool_))
                and math.isfinite(s2) and s2 > 0)


def _b3m_ratio_expect(mask, q, beta, C0, s2, kl):
    out, K = {"rho_surrogate": [], "rho_joint": []}, np.asarray(q).shape[1]
    for i, row in enumerate(np.asarray(mask).tolist()):
        days = []
        for word in row:
            S = _b3j_support(word, K)
            surrogate, joint = math.fsum(float(q[i][j]) for j in S), kl(beta[i], C0, S)
            days.append((2 * surrogate / (len(S) * s2), 2 * joint / (len(S) * s2)))
        for k, column in zip(("rho_surrogate", "rho_joint"), zip(*days)):
            out[k].append(math.fsum(column) / len(row))
    return out


def _b3m_ratio_check(out, want, basis, rel=1e-12):
    assert isinstance(out, dict) and set(out) == B3M_RATIO_OUT and out["oracle_basis"] == basis
    for k, v in want.items():
        got = np.asarray(out[k])
        assert got.dtype == np.float64 and got.shape == (len(v),) and np.isfinite(got).all(), k
        assert got.tolist() == pytest.approx(v, rel=rel, abs=1e-15), k


def _b3m_ratio_invalid(case):
    if not case.startswith("s2_"):
        mask, projection, _ = _b3j_invalid(case)
        return mask, projection, B3M_S2
    s2 = {"s2_zero": 0.0, "s2_negative": -0.25, "s2_nan": math.nan, "s2_inf": math.inf, "s2_bool": True,
          "s2_text": "0.25", "s2_array": np.array([0.25]), "s2_none": None}[case]
    return np.array(B3M_MASKS, dtype=np.uint32), _b3j_projection("FITTED_LW_GAUSSIAN"), s2


def _b3m_static_oracle(words, H):
    return np.repeat(np.array(words, dtype=np.uint32)[:, None], H, axis=1)


def _b3m_align_valid(mask, oracle, K):
    if isinstance(K, bool) or not isinstance(K, int) or not 1 <= K <= 32:
        return False
    arrays = (mask, oracle)
    if not all(isinstance(a, np.ndarray) and a.dtype == np.uint32 and a.ndim == 2 and min(a.shape) > 0
               for a in arrays):
        return False
    fits = all((a != 0).all() and (a.astype(np.uint64) >> np.uint64(K) == 0).all() for a in arrays)
    return bool(mask.shape == oracle.shape and fits and (oracle == oracle[:, :1]).all())


def _b3m_align_expect(mask, oracle, K):
    first, means = [], []
    for row, orow in zip(np.asarray(mask).tolist(), np.asarray(oracle).tolist()):
        O, hit, scores = set(_b3j_support(orow[0], K)), -1, []
        for h, word in enumerate(row, start=1):
            S = set(_b3j_support(word, K))
            if hit == -1 and S == O:
                hit = h
            scores.append(len(S & O) / len(S | O))
        first.append(hit)
        means.append(math.fsum(scores) / len(scores))
    return first, means


def _b3m_align_check(out, first, means):
    assert isinstance(out, dict) and set(out) == B3M_ALIGN_OUT
    hit, mean = np.asarray(out["first_match"]), np.asarray(out["jaccard_mean"])
    assert hit.dtype.kind == "i" and hit.shape == (len(first),) and hit.tolist() == first
    assert mean.dtype == np.float64 and mean.shape == (len(means),) and np.isfinite(mean).all()
    assert mean.tolist() == pytest.approx(means, rel=1e-12, abs=1e-15)


def _b3m_align_invalid(case):
    mask = np.array(B3M_ALIGN_MASKS, dtype=np.uint32)
    oracle, K = _b3m_static_oracle(B3M_ORACLE_WORDS, mask.shape[1]), 3
    if case == "oracle_dynamic":
        oracle[1, 2] = 4
    elif case == "candidate_zero":
        mask[0, 1] = 0
    elif case == "oracle_zero":
        oracle[2, :] = 0
    elif case == "candidate_above_K":
        mask[1, 3] = 8
    elif case == "oracle_above_K":
        oracle[0, :] = 11
    elif case == "oracle_shape":
        oracle = oracle[:, :3]
    elif case == "candidate_int64":
        mask = mask.astype(np.int64)
    elif case == "oracle_int64":
        oracle = oracle.astype(np.int64)
    elif case == "one_dim":
        mask, oracle = mask[0], oracle[0]
    elif case == "no_steps":
        mask, oracle = mask[:, :0], oracle[:, :0]
    else:
        K = {"K_zero": 0, "K_33": 33, "K_bool": True}[case]
    return mask, oracle, K


def _b3m_seal(mp, *extra, kl=False):
    def trap(*args, **kwargs):
        raise AssertionError("B3m offline diagnostics reached mixture cost, subset KL, a forbidden kernel or a side effect")

    _b3g_forbid(mp, *B3M_FORBIDDEN, *extra)
    _b3f_seal(mp)
    mp.setattr(pdb, "mixture_cost", trap)
    if kl:
        mp.setattr(pdb, "kl_mean", trap)


def test_b3m_masked_alt_prior_ratio_averages_daily_selected_information_per_axis_over_the_prior_on_hand_witnesses(
        monkeypatch):
    import copy
    import inspect
    mask, s2 = np.array(B3M_MASKS, dtype=np.uint32), B3M_S2
    sizes = [[len(_b3j_support(w, 3)) for w in row] for row in B3M_MASKS]
    assert sizes == [[1, 2, 3, 2], [1, 2, 1, 2]] and _b3m_prior_valid(s2)
    cases = {"EXACT": _b3m_exact(), **{arm: _b3j_projection(arm) for arm in ("FITTED_LW_GAUSSIAN", "FITTED_LW_T7")}}
    assert [p["oracle_basis"] for p in cases.values()] == list(B3J_BASES)
    assert all(_b3j_valid(mask, p, GAMMA) for p in cases.values())
    assert all(p["q"][0, 2] == p["beta"][0, 2] == 0.0 for p in cases.values())
    exact = cases["EXACT"]
    assert np.array_equal(exact["q"], 0.5 * exact["beta"] ** 2) and np.array_equal(exact["C0"], np.eye(3))
    subsets = [S for d in (1, 2, 3) for S in itertools.combinations(range(3), d)]
    for b in B3J_BETA:
        assert all(_b3j_kl_hand(b, S) == pytest.approx(_b3j_kl_chol(b, B3J_C0, S), rel=1e-12) for S in subsets)

    def hand(b, C, S):
        return _b3j_kl_hand(b, S)

    kls = {arm: _b3m_diagonal if arm == "EXACT" else hand for arm in cases}
    want = {arm: _b3m_ratio_expect(mask, p["q"], p["beta"], p["C0"], s2, kls[arm]) for arm, p in cases.items()}
    for arm, key in (("EXACT", "EXACT"), ("FITTED_LW_GAUSSIAN", "FITTED"), ("FITTED_LW_T7", "FITTED")):
        surrogate, joint = B3M_WANT[key]
        assert want[arm]["rho_surrogate"] == pytest.approx(surrogate, rel=1e-12), arm
        assert want[arm]["rho_joint"] == pytest.approx(joint, rel=1e-12), arm
    fitted = want["FITTED_LW_GAUSSIAN"]
    assert all(abs(a - b) > 1e-3 for a, b in zip(fitted["rho_surrogate"], fitted["rho_joint"]))
    assert fitted["rho_surrogate"][0] == pytest.approx((0.0 + 4.0 + 8 / 3 + 2.0) / 4, rel=1e-12)
    assert abs(fitted["rho_surrogate"][0] - 5 / 2) > 1e-3
    for arm, p in cases.items():
        info = _b3j_expect(mask, p["q"], p["beta"], p["C0"], GAMMA, kls[arm])
        for i, row in enumerate(sizes):
            dbar = math.fsum(row) / len(row)
            for rho, field in (("rho_surrogate", "I_surrogate"), ("rho_joint", "I_joint")):
                pooled = 2 * info[field][i] / (dbar * s2)
                assert abs(pooled - want[arm][rho][i]) > 1e-3, (arm, i, rho)
    frozen = copy.deepcopy((mask, cases))
    api = _kernel("masked_alt_prior_ratio")
    assert list(inspect.signature(api).parameters) == ["mask_bits", "projection", "s2_common"]
    with monkeypatch.context() as mp:
        _b3m_seal(mp)
        outs = {arm: api(mask, p, s2) for arm, p in cases.items()}
        scalar = api(mask, cases["FITTED_LW_GAUSSIAN"], np.float64(s2))
    np.testing.assert_equal((mask, cases), frozen)
    for arm, out in outs.items():
        _b3m_ratio_check(out, want[arm], cases[arm]["oracle_basis"])
    _b3m_ratio_check(scalar, want["FITTED_LW_GAUSSIAN"], B3J_BASES[1])
    assert np.allclose(outs["EXACT"]["rho_surrogate"], outs["EXACT"]["rho_joint"], rtol=1e-12, atol=0)
    legacy = _kernel("masked_alt_information")
    assert list(inspect.signature(legacy).parameters) == ["mask_bits", "projection", "gamma_M"]
    with monkeypatch.context() as mp:
        _b3g_forbid(mp, *B3J_FORBIDDEN)
        _b3f_seal(mp)
        kept = {arm: legacy(mask, p, GAMMA) for arm, p in cases.items()}
    for arm, p in cases.items():
        _b3j_check(kept[arm], _b3j_expect(mask, p["q"], p["beta"], p["C0"], GAMMA, kls[arm]), p["oracle_basis"])


def test_b3m_masked_alt_prior_ratio_reproduces_the_plan_exact_static_quarter_information_ratios_at_the_common_prior(
        monkeypatch):
    import copy
    desc = _b2q_desc()
    params = desc["science"]["parameters"]
    H, alpha, K, istar = params["H"], params["alpha"], params["K"], params["I_star"]
    assert (H, alpha, K, istar, params["s2_rule"]) == (250, 0.05, 20, 0.25, "2*ln(H/alpha)/(H*K)")
    s2 = 2.0 * math.log(250 / 0.05) / (250 * 20)
    prior = _kernel("common_prior")(desc)
    assert type(prior) is float and prior == pytest.approx(s2, rel=1e-15) and _b3m_prior_valid(prior)
    assert [2 * istar / (d * s2) for d in (20, 2)] == pytest.approx(list(B3M_STATIC), rel=1e-12)
    beta = np.zeros((3, K))
    beta[0] = math.sqrt(2 * istar / K)
    beta[1, [0, 1]] = math.sqrt(istar)
    beta[2, [0, 5]] = math.sqrt(istar)
    q, full = 0.5 * beta ** 2, (1 << K) - 1
    mask = np.array([[full] * 3, [3] * 3, [3] * 3], dtype=np.uint32)
    selected = [math.fsum(q[i, _b3j_support(row[0], K)].tolist()) for i, row in enumerate(mask.tolist())]
    assert selected[0] == pytest.approx(istar, rel=1e-14) and selected[1] == istar and selected[2] == istar / 2 < istar
    assert all(math.fsum(row.tolist()) == pytest.approx(istar, rel=1e-14) for row in q)
    assert q[2, 5] > 0 and q[2, 1] == 0 and not (int(mask[2, 0]) >> 5) & 1
    projection = {"q": q, "beta": beta, "C0": np.eye(K), "oracle_basis": B3J_BASES[0]}
    assert _b3j_valid(mask, projection, GAMMA)
    static = [B3M_STATIC[0], B3M_STATIC[1], B3M_STATIC[1] / 2]
    hand = _b3m_ratio_expect(mask, q, beta, np.eye(K), prior, _b3m_diagonal)
    assert hand["rho_surrogate"] == pytest.approx(static, rel=1e-12) and hand["rho_joint"] == pytest.approx(static, rel=1e-12)
    frozen = copy.deepcopy((mask, projection, prior))
    api = _kernel("masked_alt_prior_ratio")
    with monkeypatch.context() as mp:
        _b3m_seal(mp)
        out = api(mask, projection, prior)
    np.testing.assert_equal((mask, projection, prior), frozen)
    _b3m_ratio_check(out, {"rho_surrogate": static, "rho_joint": static}, B3J_BASES[0])


@pytest.mark.parametrize("case", B3M_RATIO_INVALID)
def test_b3m_masked_alt_prior_ratio_refuses_an_invalid_prior_mask_or_projection_before_any_subset_kl(monkeypatch, case):
    mask, projection, s2 = _b3m_ratio_invalid(case)
    assert _b3j_valid(np.array(B3M_MASKS, dtype=np.uint32), _b3j_projection("FITTED_LW_GAUSSIAN"), GAMMA)
    assert _b3m_prior_valid(B3M_S2) and not (_b3j_valid(mask, projection, GAMMA) and _b3m_prior_valid(s2))
    api = _kernel("masked_alt_prior_ratio")
    with monkeypatch.context() as mp:
        _b3m_seal(mp, kl=True)
        with pytest.raises(ValueError):
            api(mask, projection, s2)


def test_b3m_oracle_mask_alignment_reports_first_exact_set_match_and_mean_daily_jaccard_of_static_oracle_rows(
        monkeypatch):
    import copy
    import inspect
    mask = np.array(B3M_ALIGN_MASKS, dtype=np.uint32)
    oracle = _b3m_static_oracle(B3M_ORACLE_WORDS, mask.shape[1])
    assert oracle.dtype == np.uint32 and oracle.shape == mask.shape == (3, 4) and _b3m_align_valid(mask, oracle, 3)
    assert [_b3j_support(w, 3) for w in B3M_ORACLE_WORDS] == [[0, 1], [0, 2], [1]]
    assert [[_b3j_support(w, 3) for w in row] for row in B3M_ALIGN_MASKS] == [
        [[0], [0, 1], [2], [1]], [[2], [2], [0], [0, 1, 2]], [[1], [1], [1], [1]]]
    assert set(_b3j_support(1, 3)) < set(_b3j_support(3, 3)) and set(_b3j_support(7, 3)) > set(_b3j_support(5, 3))
    first, means = _b3m_align_expect(mask, oracle, 3)
    assert first == [2, -1, 1] and means == pytest.approx([1 / 2, 13 / 24, 1.0], rel=1e-15)
    assert means[0] == pytest.approx((1 / 2 + 1 + 0 + 1 / 2) / 4) and means[1] == pytest.approx((3 / 2 + 2 / 3) / 4)
    assert all(abs(a - b) > 1e-3 for a, b in zip(means[:2], (4 / 9, 5 / 9)))
    assert _b3m_align_valid(mask, oracle, 32) and _b3m_align_expect(mask, oracle, 32) == (first, means)
    frozen = copy.deepcopy((mask, oracle))
    api = _kernel("oracle_mask_alignment")
    assert list(inspect.signature(api).parameters) == ["mask_bits", "oracle_mask_bits", "K"]
    with monkeypatch.context() as mp:
        _b3m_seal(mp, "masked_alt_information", kl=True)
        out, wide = api(mask, oracle, 3), api(mask, oracle, 32)
    np.testing.assert_equal((mask, oracle), frozen)
    for got in (out, wide):
        _b3m_align_check(got, first, means)


@pytest.mark.parametrize("case", B3M_ALIGN_INVALID)
def test_b3m_oracle_mask_alignment_refuses_dynamic_oracles_foul_words_shapes_dtypes_or_K(monkeypatch, case):
    mask, oracle, K = _b3m_align_invalid(case)
    base = np.array(B3M_ALIGN_MASKS, dtype=np.uint32)
    assert _b3m_align_valid(base, _b3m_static_oracle(B3M_ORACLE_WORDS, base.shape[1]), 3)
    assert not _b3m_align_valid(mask, oracle, K)
    api = _kernel("oracle_mask_alignment")
    with monkeypatch.context() as mp:
        _b3m_seal(mp, "masked_alt_information", kl=True)
        with pytest.raises(ValueError):
            api(mask, oracle, K)


def test_b3m_offline_diagnostics_compare_the_verified_primary_online_info_alt_mask_with_its_own_f2_oracle_on_all_days(
        tmp_path, monkeypatch):
    import copy
    import hashlib
    import inspect
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    ref, verify = _b3g_references(fixture, records), _kernel("_verify_partition")
    setup_record, dev_record, cal_record, _, hold_record, alt_record = records
    did, primary, sid, ups, info = ref["did"], ref["primary"], ref["sid"], ref["ups"], ref["cids"][B3F_P[0]]
    params, n = desc["science"]["parameters"], desc["sizes"]["ALT"]
    H, K, alpha, gamma = params["H"], params["K"], params["alpha"], float(params["gamma_M"])
    assert (H, K, n) == (6, 20, 2) and params["s2_rule"] == "2*ln(H/alpha)/(H*K)" and 0 < alpha < 1
    name = pdb.canon(primary)
    meta = setup_record["derived"]["setups"][name]["applications"]["RESIDUAL"]
    rows = dev_record["derived"]["setups"][name]["RESIDUAL"]["policies"]["PRIMARY"]
    thresholds, checks = cal_record["derived"]["thresholds"], hold_record["derived"]["null_checks"]
    ipid, opid = rows[B3F_P[0]]["policy_id"], rows[B3H_ORACLE]["policy_id"]
    assert meta["setup_id"] == sid and type(ipid) is str and type(opid) is str and ipid != opid
    triple = (sid, opid, B3F_F2)
    [oracle] = [c for c, t in thresholds.items() if (t["setup_id"], t["policy_id"], t.get("family")) == triple]
    assert (thresholds[info]["setup_id"], thresholds[info]["policy_id"], thresholds[info].get("family")) == (
        sid, ipid, None)
    assert thresholds[oracle]["qualification"] == B3A_ORACLE_LABEL and oracle != info
    assert (checks[oracle]["setup_id"], checks[oracle]["policy_id"], checks[oracle]["family"]) == triple
    key = ["ALT", *primary, "RESIDUAL", B3F_F2]
    sha, n_rows, arrays = verify(staging, did, ups["ALT"], key)
    payload = _partition_stem(staging, did, ups["ALT"], key).with_suffix(".npz")
    [part] = [r for r in alt_record["partitions"] if r["key"] == key]
    assert sha == hashlib.sha256(payload.read_bytes()).hexdigest() == part["sha256"] and n_rows == part["n_rows"] == n
    assert alt_record["upstream"] == ups["ALT"]
    assert {info, oracle} <= set(alt_record["derived"]["trials"][pdb.canon(key)]["calibration_ids"])
    mask, omask, first = arrays["mask_" + info], arrays["mask_" + oracle], arrays["first_" + info]
    assert np.array_equal(first, ref["alt"][B3F_F2][B3F_P[0]]) and arrays["first_" + oracle].shape == (n,)
    assert ((first == -1) | ((first >= 1) & (first <= H))).all()
    assert all(m.dtype == np.uint32 and m.shape == (n, H) for m in (mask, omask))
    assert _b3m_align_valid(mask, omask, K) and bool((omask == omask[:, :1]).all())
    universe = meta["universe"]
    assert universe == list(range(2, 2 + K))
    costs = [pdb.mixture_cost(d, gamma) for d in range(1, K + 1)]
    assert all(math.isfinite(c) and c > costs[0] > 0 for c in costs[1:])
    for i in range(n):
        [axis] = np.flatnonzero(_b3e_q(primary, B3F_F2, i)).tolist()
        assert omask[i].tolist() == [1 << axis] * H, i
    assert omask[0, 0] != omask[1, 0]
    assert np.asarray(arrays["I_joint"]).tolist() == [_b3e_joint(primary, B3F_F2, i) for i in range(n)]
    setup = _kernel("_setup_cache")
    frame_key, fit_key = ["frame", desc["campaign"], primary[1]], ["fit", desc["campaign"], *primary]
    frame, fit = (setup(verify(staging, did, {}, k)[2], k) for k in (frame_key, fit_key))
    delta = np.array([_b3e_delta(primary[1], B3F_F2, i) for i in range(n)])
    diag = _kernel("projection_diagnostics")(frame, fit, universe, delta, primary[0])
    basis = B3J_BASES[1]
    assert diag["oracle_basis"] == basis == pio().PROJECTION_ARMS[primary[0]]
    q, beta, C0 = (diag[k] for k in ("q", "beta", "C0"))
    assert np.allclose(q, 0.5 * np.asarray(beta) ** 2, rtol=1e-10, atol=1e-12)
    projection = {"q": q, "beta": beta, "C0": C0, "oracle_basis": basis}
    s2 = 2.0 * math.log(H / alpha) / (H * K)
    prior = _kernel("common_prior")(desc)
    assert type(prior) is float and prior == pytest.approx(s2, rel=1e-15) and _b3m_prior_valid(prior)
    assert all(_b3j_valid(m, projection, gamma) for m in (mask, omask))
    want = {label: _b3m_ratio_expect(m, q, beta, C0, prior, _b3j_kl_chol) for label, m in (("info", mask), ("oracle", omask))}
    hits, jaccard = _b3m_align_expect(mask, omask, K)
    before, frozen = _tree(staging), copy.deepcopy((mask, omask, projection, prior))
    ratio, align = _kernel("masked_alt_prior_ratio"), _kernel("oracle_mask_alignment")
    assert list(inspect.signature(ratio).parameters) == ["mask_bits", "projection", "s2_common"]
    assert list(inspect.signature(align).parameters) == ["mask_bits", "oracle_mask_bits", "K"]
    with monkeypatch.context() as mp:
        _b3b_guard(mp, state, *B3B_TRAPPED)
        _b3m_seal(mp)
        got = {"info": ratio(mask, projection, prior), "oracle": ratio(omask, projection, prior)}
        aligned = align(mask, omask, K)
    assert _tree(staging) == before
    np.testing.assert_equal((mask, omask, projection, prior), frozen)
    for label, out in got.items():
        _b3m_ratio_check(out, want[label], basis, rel=1e-9)
    _b3m_align_check(aligned, hits, jaccard)


def _b4a_yaml(path, cfg):
    import yaml
    text = yaml.safe_dump(cfg, sort_keys=True, default_flow_style=False)
    assert pdb.canon(yaml.safe_load(text)) == pdb.canon(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _b4a_snapshot(root):
    return _tree(root), sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


def _b4a_preflight_traps(mp, opened):
    import os
    import pathlib
    _no_side_effects(mp, opened)
    guarded, listed = os.open, []

    def read_witness(path, flags, *args, **kwargs):
        opened.append(pathlib.Path(os.fsdecode(path)).resolve())
        return guarded(path, flags, *args, **kwargs)

    def no_listing(*args, **kwargs):
        listed.append(args)
        raise AssertionError("directory listing during CLI preflight")

    mp.setattr(os, "open", read_witness)
    for name in ("scandir", "listdir"):
        mp.setattr(os, name, no_listing)
    mp.setattr(pdb, "check_env", lambda: [])
    return listed


def test_b4a_cli_describe_prints_the_pure_pilot_identity_without_go_outputs_or_prior_state(
        tmp_path, monkeypatch, capsys):
    import json
    main, describe, ident = _kernel("main"), _kernel("design_descriptor"), _kernel("design_id")
    root, files, cfg = _kernel("CODE_ROOT"), _kernel("CODE_FILES"), _design_cfg()
    assert cfg["authorization"] is None
    config = _b4a_yaml(tmp_path / "fixture" / "pca_info_online.yaml", cfg)
    desc = describe(cfg, "pilot")
    did = ident(desc)
    results, logs = tmp_path / "results" / "pca_info_online", tmp_path / "logs" / "pca_info_online"
    poisons = {results / "pilot" / "manifest.json": "POISON prior pilot manifest",
               results / "smoke" / "manifest.json": "POISON prior smoke manifest",
               logs / "pilot" / "staging" / did[:16] / "design.json": "POISON prior pilot staging",
               logs / "smoke" / "staging" / "design.json": "POISON prior smoke staging"}
    for path, label in poisons.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(pdb.canon({"poison": label, "seed": 1, "n_hold": 7, "descriptor": {"seed": 1}}))
    monkeypatch.setattr(pio(), "REPO_ROOT", tmp_path)
    monkeypatch.chdir(tmp_path)
    allowed = {config.resolve(), *((root / rel).resolve() for rel in files)}
    before = _b4a_snapshot(tmp_path)
    base = ["--config", str(config), "--mode", "pilot", "--describe"]
    extra = ["--jobs", "3", "--output-dir", str(results / "pilot"), "--log-dir", str(logs / "pilot"), "--resume"]
    for argv in (base, [*base, *extra]):
        opened = []
        with monkeypatch.context() as mp:
            listed = _b4a_preflight_traps(mp, opened)
            rc = main(argv)
        out, err = capsys.readouterr()
        assert rc == 0, err
        assert listed == []
        assert set(opened) == allowed, sorted(str(p) for p in set(opened) - allowed)
        assert not any(label in out for label in poisons.values())
        printed = json.loads(out)
        assert isinstance(printed, dict) and {"design_id", "descriptor"} <= set(printed)
        assert printed["design_id"] == did == ident(printed["descriptor"])
        assert pdb.canon(printed["descriptor"]) == pdb.canon(desc)
    assert _b4a_snapshot(tmp_path) == before


B4A_REFUSALS = ("pilot_missing_go", "full_missing_go", "full_seed_changed_after_go", "pilot_jobs_beyond_jobs_max")


@pytest.mark.parametrize("case", B4A_REFUSALS)
def test_b4a_cli_run_preflight_refuses_an_unauthorized_pilot_or_full_before_any_effect(
        tmp_path, monkeypatch, capsys, case):
    main, describe, ident = _kernel("main"), _kernel("design_descriptor"), _kernel("design_id")
    authorize, root, files = _kernel("authorize"), _kernel("CODE_ROOT"), _kernel("CODE_FILES")
    mode, cfg, jobs, go = case.split("_")[0], _design_cfg(), 1, set()
    if case.endswith("missing_go"):
        monkeypatch.setattr(pio(), "REPO_ROOT", tmp_path)
        assert cfg["authorization"] is None
        expected = ident(describe(cfg, mode))
    else:
        cfg, issued = _authorized(tmp_path, monkeypatch, cfg, mode)
        go = {(tmp_path / cfg["authorization"]["go_reference"]["path"]).resolve()}
        jobs_max = cfg["envelope"]["jobs_max"]
        assert authorize(mode, cfg, describe(cfg, mode), jobs_max)["design_id"] == issued
        if case == "full_seed_changed_after_go":
            cfg = _edited(cfg, ("seed",), cfg["seed"] + 1)
            expected = ident(describe(cfg, mode))
            assert expected != issued == cfg["authorization"]["design_id"]
        else:
            jobs, expected = jobs_max + 1, "jobs"
    config = _b4a_yaml(tmp_path / "fixture" / f"{case}.yaml", cfg)
    run = tmp_path / "runs" / case
    out_dir, log_dir = run / "out", run / "logs"
    monkeypatch.chdir(tmp_path)
    allowed = {config.resolve(), *((root / rel).resolve() for rel in files), *go}
    before = _b4a_snapshot(tmp_path)
    argv = ["--config", str(config), "--mode", mode, "--jobs", str(jobs),
            "--output-dir", str(out_dir), "--log-dir", str(log_dir)]
    opened = []
    with monkeypatch.context() as mp:
        listed = _b4a_preflight_traps(mp, opened)
        rc = main(argv)
    out, err = capsys.readouterr()
    assert rc == 2, (rc, out, err)
    assert err.strip() and "refus" in err.lower() and expected in err, err
    assert "before authorization" not in err and "directory listing" not in err and listed == []
    assert config.resolve() in opened and set(opened) <= allowed, sorted(str(p) for p in set(opened) - allowed)
    assert not run.exists() and not out_dir.exists() and not log_dir.exists()
    assert _b4a_snapshot(tmp_path) == before


B4B_E, B4B_G, B4B_P = ["EXACT", 32, 0], ["FITTED_LW_GAUSSIAN", 32, 1], ["FITTED_LW_GAUSSIAN", 239, 0]


def _b4b_cfg(setups=(B4B_G, B4B_P, B4B_E), applications=("RESIDUAL", "MARKET"),
             families=("F3_MARKET", "F2_STRUCTURED_RESIDUAL")):
    cfg = _design_cfg()
    for path, value in ((("scope", "setups"), [list(s) for s in setups]),
                        (("scope", "applications"), list(applications)), (("scope", "families"), list(families))):
        cfg = _edited(cfg, path, value)
    return cfg


def _b4b_expected(C):
    setups, apps = (B4B_E, B4B_P, B4B_G), ("MARKET", "RESIDUAL")
    alt = {"MARKET": "F3_MARKET", "RESIDUAL": "F2_STRUCTURED_RESIDUAL"}
    return {"SETUP": [["fit", C, *B4B_P], ["fit", C, *B4B_G], ["frame", C, 239], ["frame", C, 32]],
            "DEV": [*(["DEV_ALT", C, *s, f] for s in setups for f in DEV_FAMILIES),
                    *(["DEV_LIB", C, *s, f] for s in setups for f in DEV_FAMILIES),
                    *(["DEV_NULL", C, *s] for s in setups)],
            "CAL": [["CAL_NULL", C, *s, a] for s in setups for a in apps],
            "NULL_PLAN": [["NULL_PLAN", *B4B_P]],
            "HOLD": [["HOLD_NULL", *s, a] for s in setups for a in apps],
            "ALT": [["ALT", *s, a, alt[a]] for s in setups for a in apps]}


def test_b4b_partition_plan_schedules_the_hand_checked_scope_before_any_draw_output_or_write(tmp_path, monkeypatch):
    import copy
    import os
    cfg, names, validated = _b4b_cfg(), _kernel("PHASES"), _kernel("_validated_plan")
    describe, ident, partition_plan = _kernel("design_descriptor"), _kernel("design_id"), _kernel("partition_plan")
    desc, pilot_desc = describe(cfg, "smoke"), describe(cfg, "pilot")
    variants = [describe(_edited(cfg, path, value), "smoke") for path, value in (
        (("modes", "smoke", "null_plan", "n_plan"), 2), (("modes", "smoke", "null_plan", "n_cap"), 7),
        (("modes", "smoke", "sizes", "HOLD_NULL"), 4), (("envelope", "jobs_max"), 1))]
    primitive = sorted(([*k] for k in _kernel("seed_plan")(cfg, "smoke")["keys"] if k[0] in ("frame", "fit")),
                       key=pdb.canon)
    snapshot, opened = copy.deepcopy([desc, pilot_desc, variants]), []
    monkeypatch.chdir(tmp_path)
    with monkeypatch.context() as mp:
        _no_side_effects(mp, opened)
        for name in ("scandir", "listdir"):
            mp.setattr(os, name, lambda *args, **kwargs: pytest.fail("directory listing while planning partitions"))
        plan, again, pilot = partition_plan(desc), partition_plan(desc), partition_plan(pilot_desc)
        others = [partition_plan(d) for d in variants]
    expected = _b4b_expected("SMOKE")
    assert not opened and _tree(tmp_path) == {} and snapshot == [desc, pilot_desc, variants]
    assert cfg["authorization"] is None and desc["science"]["phi"]["setup"] == B4B_P and set(expected) == set(names)
    assert all(keys == sorted(keys, key=pdb.canon) for keys in expected.values())
    assert len({ident(d) for d in [desc, *variants]}) == 5
    assert plan == again == expected and all(other == expected for other in others)
    assert validated(plan) is None and validated(pilot) is None
    assert [len(plan[p]) for p in names] == [4, 27, 6, 1, 6, 6] and plan["SETUP"] == primitive
    assert pilot == {**_b4b_expected("PILOT"), "NULL_PLAN": []} and pilot_desc["null_plan"] is None
    assert pilot["HOLD"] == plan["HOLD"] and pilot["ALT"] == plan["ALT"] and pilot["DEV"] != plan["DEV"]


@pytest.mark.parametrize("mode", ["pilot", "smoke"])
def test_b4b_partition_plan_market_only_scope_plans_no_dev_and_no_null_plan(mode, monkeypatch):
    cfg, C = _b4b_cfg((B4B_E, B4B_G), ("MARKET",), ("F3_MARKET",)), mode.upper()
    desc = _kernel("design_descriptor")(cfg, mode)
    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        plan = _kernel("partition_plan")(desc)
    assert (desc["null_plan"] is None) == (mode == "pilot") and B4B_P not in desc["scope"]["setups"]
    assert plan == {"SETUP": [["fit", C, *B4B_G], ["frame", C, 32]], "DEV": [],
                    "CAL": [["CAL_NULL", C, *B4B_E, "MARKET"], ["CAL_NULL", C, *B4B_G, "MARKET"]], "NULL_PLAN": [],
                    "HOLD": [["HOLD_NULL", *B4B_E, "MARKET"], ["HOLD_NULL", *B4B_G, "MARKET"]],
                    "ALT": [["ALT", *B4B_E, "MARKET", "F3_MARKET"], ["ALT", *B4B_G, "MARKET", "F3_MARKET"]]}
    assert _kernel("_validated_plan")(plan) is None


def test_b4b_partition_plan_matches_the_committed_partition_keys_of_the_staged_b3g_fixture(tmp_path, monkeypatch):
    import json
    partition_plan = _kernel("partition_plan")
    fixture, _, records, _ = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    names, primary, C = _kernel("PHASES"), desc["science"]["phi"]["setup"], desc["campaign"]
    describe, ident = _kernel("design_descriptor"), _kernel("design_id")
    seed_plan = _kernel("seed_plan")
    assert pdb.canon(describe(cfg, "full")) == pdb.canon(desc) and primary == list(B2W_SETUPS[1]) and C == "FULL"
    generated, fresh = partition_plan(desc), partition_plan(describe(cfg, "full"))
    assert generated == fresh == plan and pdb.canon(generated) == pdb.canon(plan)
    assert _kernel("_validated_plan")(generated) is None
    stored = [json.loads((staging / "phases" / f"{p}.json").read_text()) for p in names]
    assert [r["phase"] for r in records] == [r["phase"] for r in stored] == list(names)
    for phase, record, written in zip(names, records, stored):
        committed = [row["key"] for row in record["partitions"]]
        assert committed == [row["key"] for row in written["partitions"]] == generated[phase], phase
    assert [len(generated[p]) for p in names] == [2, 18, 4, 1, 4, 8]
    keys = seed_plan(cfg, "full")["keys"]
    assert generated["SETUP"] == [["fit", C, *primary], ["frame", C, 24]]
    assert generated["SETUP"] == sorted(([*k] for k in keys if k[0] in ("frame", "fit")), key=pdb.canon)
    reserved = {pdb.canon(list(s)): sorted(k[6] for k in keys if k[0] == "path" and k[5] == "HOLD_NULL"
                                           and list(k[2:5]) == list(s)) for s in B2W_SETUPS}
    n_cap, n_hold = desc["null_plan"]["n_cap"], records[3]["derived"]["n_hold"]
    rows = {pdb.canon(row["key"]): row["n_rows"] for row in records[4]["partitions"]}
    assert reserved == {pdb.canon(list(B2W_SETUPS[0])): list(range(desc["sizes"]["HOLD_NULL"])),
                        pdb.canon(primary): list(range(n_cap))}
    assert rows[pdb.canon(["HOLD_NULL", *primary, "RESIDUAL"])] == n_hold <= n_cap
    assert all(len(key) == 5 and key[0] == "HOLD_NULL" for key in generated["HOLD"])
    edited = _edited(cfg, ("modes", "full", "null_plan", "n_cap"), n_cap + 4)
    capped, changed = describe(edited, "full"), seed_plan(edited, "full")
    assert ident(capped) != ident(desc) and partition_plan(capped) == generated
    assert capped["seed_plan_sha256"] == changed["sha256"] != desc["seed_plan_sha256"]
    assert sorted(k[6] for k in changed["keys"] if k[0] == "path" and k[5] == "HOLD_NULL"
                  and list(k[2:5]) == list(primary)) == list(range(n_cap + 4))


B4C_SIZES = ((("modes", "smoke", "sizes", "CAL_NULL"), 6), (("modes", "smoke", "sizes", "ALT"), 6))
B4C_ORDER = (4, 0, 5, 2, 1)


def _b4c_batch(name):
    if name == "exact_null":
        frame = _b2j_frame(32)
        return frame, frame, [(_b2k_path("CAL_NULL", i), None) for i in B4C_ORDER]
    deltas = [np.linspace(-0.5, 1.0, 24) * (j + 1) for j in range(len(B4C_ORDER))]
    for delta in deltas:
        delta.flags.writeable = False
    return _b2j_frame(24), _b2m_fit(), [(_b2j_path("ALT", i), delta) for i, delta in zip(B4C_ORDER, deltas)]


def _b4c_parent(mp, local=None):
    import concurrent.futures
    import inspect
    import multiprocessing
    module, real_context, contexts = pio(), multiprocessing.get_context, []
    real_path = module.path_scores

    def context(method=None):
        contexts.append(method)
        return real_context(method)

    def scored(*args, **kwargs):
        if local is None:
            pytest.fail("the parent scored a path owned by its spawned workers")
        local.append(inspect.signature(real_path).bind(*args, **kwargs).arguments)
        return real_path(*args, **kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail("a parent pool, global seed or draw outside the dispatch role of this jobs value")

    if local is None:
        traps = ((np.random, "SeedSequence"), (np.random, "default_rng"), (module, "exact_scores"),
                 (module, "null_returns"))
    else:
        traps = ((concurrent.futures, "ProcessPoolExecutor"), (multiprocessing, "Pool"))
    mp.setattr(multiprocessing, "get_context", context)
    mp.setattr(module, "path_scores", scored)
    for owner, name in ((pdb, "seed_key"), (np.random, "seed"), *traps):
        mp.setattr(owner, name, forbidden)
    return contexts


def _b4c_stopped(mp):
    import multiprocessing
    module = pio()

    def started(*args, **kwargs):
        pytest.fail("a pool or score task started before the refusal")

    _no_side_effects(mp)
    for owner, name in ((multiprocessing, "get_context"), (multiprocessing, "Pool"), (module, "path_scores"),
                        (module, "exact_scores"), (module, "null_returns")):
        mp.setattr(owner, name, started)


@pytest.mark.parametrize("batch", ["exact_null", "fitted_alt"])
def test_b4c_score_path_batch_jobs_one_and_three_stack_the_serial_path_scores_bytes_in_requested_order(
        monkeypatch, batch):
    import os
    import time
    score_path_batch, module = _kernel("score_path_batch"), pio()
    desc, (frame, fit, requests) = _b2k_desc("smoke", *B4C_SIZES), _b4c_batch(batch)
    keys, deltas, exact = [k for k, _ in requests], [d for _, d in requests if d is not None], batch == "exact_null"
    assert set(keys) <= set(_kernel("seed_plan")(_b2k_cfg(*B4C_SIZES), "smoke")["keys"]) and len(set(keys)) == 5
    assert [key[6] for key in keys] == list(B4C_ORDER) != sorted(B4C_ORDER)
    assert {key[2] for key in keys} == {"EXACT" if exact else "FITTED_LW_GAUSSIAN"} and (fit is frame) is exact
    assert len(deltas) == (0 if exact else 5) and len({delta.tobytes() for delta in deltas}) == len(deltas)
    assert all(delta.shape == (24,) and delta.any() and not delta.flags.writeable for delta in deltas)
    assert {name: os.environ.get(name) for name in pdb.REQUIRED_ENV} == pdb.REQUIRED_ENV and pdb.check_env() == []
    expected = np.stack([module.path_scores(desc, frame, fit, "RESIDUAL", key, delta) for key, delta in requests])
    assert expected.dtype == np.float64 and expected.shape == (5, 3, 20)
    assert len({rows.tobytes() for rows in expected}) == 5
    arrays, snapshot, state = [*frame.values(), *fit.values(), *deltas], pdb.canon(desc), np.random.get_state()
    kept = [array.tobytes() for array in arrays]
    for jobs in (1, 3):
        local, entropies = [], []
        with monkeypatch.context() as mp:
            contexts = _b4c_parent(mp, local if jobs == 1 else None)
            if jobs == 1:
                mp.setattr(np.random, "SeedSequence", _b2j_seed_spy(entropies))
                out = score_path_batch(desc, frame, fit, "RESIDUAL", requests, jobs=1)
            else:
                live = time.monotonic() + 30.0
                out = score_path_batch(desc, frame, fit, "RESIDUAL", requests, jobs=3, deadline=live)
        assert type(out) is np.ndarray and out.dtype == np.float64 and out.shape == expected.shape, jobs
        assert out.tobytes() == expected.tobytes(), jobs
        if jobs == 1:
            assert contexts == [] and entropies == [_b2j_words(desc["seed"], key) for key in keys]
            assert [(call["application"], call["key"]) for call in local] == [("RESIDUAL", key) for key in keys]
        else:
            assert contexts and set(contexts) == {"spawn"}
    assert pdb.canon(desc) == snapshot and [array.tobytes() for array in arrays] == kept
    assert _b2j_same_state(state, np.random.get_state())


def test_b4c_score_path_batch_bad_parent_startup_environment_refuses_before_any_pool_or_draw(monkeypatch):
    score_path_batch = _kernel("score_path_batch")
    desc, (frame, fit, requests) = _b2k_desc("smoke", *B4C_SIZES), _b4c_batch("fitted_alt")
    assert pdb.check_env() == []
    for jobs in (1, 3):
        with monkeypatch.context() as mp:
            mp.setitem(pdb.ENV_AT_START, "OMP_NUM_THREADS", "2")
            problems = pdb.check_env()
            _b4c_stopped(mp)
            with pytest.raises(RuntimeError) as refused:
                score_path_batch(desc, frame, fit, "RESIDUAL", requests, jobs=jobs)
        assert problems == ["OMP_NUM_THREADS='2' (required '1')"] and problems[0] in str(refused.value), jobs
        assert not isinstance(refused.value, pdb.ResourceBlocked), jobs
    assert pdb.check_env() == []


def test_b4c_score_path_batch_spawned_worker_refuses_its_own_bad_startup_environment(monkeypatch):
    import os
    import time
    score_path_batch = _kernel("score_path_batch")
    desc, (frame, fit, requests) = _b2k_desc("smoke", *B4C_SIZES), _b4c_batch("exact_null")
    assert pdb.check_env() == [] and os.environ.get("OPENBLAS_NUM_THREADS") == "1"
    with monkeypatch.context() as mp:
        mp.setenv("OPENBLAS_NUM_THREADS", "2")
        contexts, healthy = _b4c_parent(mp), pdb.check_env()
        with pytest.raises(RuntimeError) as refused:
            score_path_batch(desc, frame, fit, "RESIDUAL", requests, jobs=3, deadline=time.monotonic() + 30.0)
    assert healthy == [] and contexts and set(contexts) == {"spawn"}
    assert "OPENBLAS_NUM_THREADS='2' (required '1')" in str(refused.value)
    assert not isinstance(refused.value, pdb.ResourceBlocked) and os.environ.get("OPENBLAS_NUM_THREADS") == "1"


def test_b4c_score_path_batch_expired_monotonic_deadline_blocks_before_any_pool_or_score_task(monkeypatch):
    import inspect
    import time
    score_path_batch = _kernel("score_path_batch")
    params = inspect.signature(score_path_batch).parameters
    assert list(params) == ["desc", "frame", "fit", "application", "requests", "jobs", "deadline"]
    assert [(params[name].kind, params[name].default) for name in ("jobs", "deadline")] == [
        (inspect.Parameter.KEYWORD_ONLY, 1), (inspect.Parameter.KEYWORD_ONLY, None)]
    desc = _b2k_desc("smoke", *B4C_SIZES)
    assert pdb.check_env() == []
    for batch, jobs in itertools.product(("exact_null", "fitted_alt"), (1, 3)):
        frame, fit, requests = _b4c_batch(batch)
        expired = time.monotonic() - 1.0
        with monkeypatch.context() as mp:
            _b4c_stopped(mp)
            with pytest.raises(pdb.ResourceBlocked):
                score_path_batch(desc, frame, fit, "RESIDUAL", requests, jobs=jobs, deadline=expired)


@pytest.mark.parametrize("case", ["cpu_exhausted", "wall_exhausted"])
def test_guarded_partition_blocks_after_its_producer_exhausts_budget(tmp_path, monkeypatch, case):
    import json
    start, guarded = _kernel("start_invocation"), _kernel("guarded_partition")
    env = _design_cfg()["envelope"]
    cap, wall = env["cpu_hours_max"] * 3600, float(env["wall_seconds_per_invocation"])
    spent = 5.0 if case == "cpu_exhausted" else 1.0
    used = cap - spent if case == "cpu_exhausted" else 0.0
    staging, out, authority, plan, lineage = _b1l_setup(tmp_path, monkeypatch, used)
    alt, state, calls = _b1k_parts()["ALT"], {"cpu": 10.0, "wall": 100.0}, []

    def produce():
        calls.append(case)
        state.update(cpu=10.0 + spent, wall=100.0 + (wall if case == "wall_exhausted" else 0.0))
        return alt[1][1]

    stem = _partition_stem(staging, authority["design_id"], dict(lineage), alt[1][0])
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        context = start(staging, authority, plan, "invocation-2")
        before = {k: v for k, v in _tree(staging).items() if k not in {"resources.json", "status.json"}}
        with pytest.raises(pdb.ResourceBlocked):
            guarded(context, "ALT", dict(lineage), alt[1][0], produce)
    after = _tree(staging)
    expected = {"status": "BLOCKED_RESOURCE", "design_id": authority["design_id"], "last_complete_phase": "HOLD",
                "missing_partitions": [{"phase": "ALT", "key": alt[1][0]}]}
    journal = json.loads((staging / "resources.json").read_text())["cpu_seconds"]
    assert calls == [case] and journal["invocation-1"] == used and journal["invocation-2"] == spent
    assert json.loads((staging / "status.json").read_text()) == expected
    assert {k: after.get(k) for k in before} == before and not out.exists()
    assert not any((stem.parent / (stem.name + suffix)).exists() for suffix in (".npz", ".json"))


def test_b4e_phase_controllers_route_path_scores_through_score_path_batch(tmp_path, monkeypatch):
    from collections import Counter
    import math

    import numpy as np

    module = pio()
    real_start = module.start_invocation
    real_batch = module.score_path_batch
    invocations = []
    calls = []

    def start_invocation(staging, authority, plan, token):
        context = real_start(staging, authority, plan, token)
        invocations.append(dict(context))
        context["jobs"] = 3
        return context

    def score_path_batch(desc, frame, fit, application, requests, *, jobs=1, deadline=None):
        requests = list(requests)
        calls.append({
            "application": application,
            "keys": [tuple(key) for key, _ in requests],
            "deltas": [delta for _, delta in requests],
            "jobs": jobs,
            "deadline": deadline,
        })
        return real_batch(desc, frame, fit, application, requests, jobs=1, deadline=deadline)

    def durable(tree):
        return {path: data for path, data in tree.items() if str(path) != "resources.json"}

    monkeypatch.setattr(module, "start_invocation", start_invocation)
    monkeypatch.setattr(module, "score_path_batch", score_path_batch)
    fixture, state, records, context = _b3g_fixture(tmp_path, monkeypatch)
    cfg, desc, authority, plan, staging = fixture
    assert calls, "phase controllers did not route path scores through score_path_batch"

    wall = desc["envelope"]["wall_seconds_per_invocation"]
    assert invocations and wall is not None
    bounds = [float(invocation["started"]) + float(wall) for invocation in invocations]
    assert context["jobs"] == 3

    expected = Counter()
    for record in records:
        for row in record["partitions"]:
            key = list(row["key"])
            if key[0] in ("CAL_NULL", "HOLD_NULL", "ALT"):
                payload = module._verify_partition(staging, record["design_id"], record["upstream"], row["key"])[2]
                if key[0] == "ALT" and set(payload) == {"I_joint"}:
                    continue
                if key[0] != "ALT" and set(payload) == {"index"}:
                    continue
            if key[0] in ("DEV_NULL", "DEV_ALT") and len(key) >= 5:
                expected[(key[0], tuple(key[2:5]), "RESIDUAL", row["n_rows"])] += 1
            elif key[0] == "CAL_NULL" and len(key) >= 6:
                expected[("CAL_NULL", tuple(key[2:5]), key[5], row["n_rows"])] += 1
            elif key[0] == "NULL_PLAN" and len(key) >= 4:
                expected[("NULL_PLAN", tuple(key[1:4]), "RESIDUAL", row["n_rows"])] += 1
            elif key[0] in ("HOLD_NULL", "ALT") and len(key) >= 5:
                expected[(key[0], tuple(key[1:4]), key[4], row["n_rows"])] += 1

    planned = set(map(tuple, _kernel("seed_plan")(cfg, "full")["keys"]))
    remaining = Counter(expected)
    roles = set()
    for call in calls:
        keys = call["keys"]
        assert keys
        prefix = keys[0][:6]
        assert prefix[:2] == ("path", "FULL")
        assert all(key[:6] == prefix and key in planned for key in keys)
        assert [key[6] for key in keys] == list(range(len(keys)))
        role = prefix[5]
        item = (role, tuple(prefix[2:5]), call["application"], len(keys))
        assert remaining[item] > 0, item
        remaining[item] -= 1
        roles.add(role)
        if role in ("ALT", "DEV_ALT"):
            assert all(delta is not None and np.any(np.asarray(delta, dtype=float) != 0) for delta in call["deltas"])
        else:
            assert all(delta is None for delta in call["deltas"])
        assert call["jobs"] == 3
        assert call["deadline"] is not None
        assert any(math.isclose(float(call["deadline"]), bound, rel_tol=0.0, abs_tol=1e-9) for bound in bounds)
    assert roles == {"DEV_NULL", "DEV_ALT", "CAL_NULL", "NULL_PLAN", "HOLD_NULL", "ALT"}
    assert not +remaining

    seen = len(calls)
    before = durable(_tree(staging))
    with monkeypatch.context() as mp:
        _b1m_clock(mp, state)
        replay = _kernel("alt_phase")(cfg, "full", {**context, "jobs": 1})
    assert replay == records[-1]
    assert len(calls) == seen
    assert durable(_tree(staging)) == before


def _b4f_key_paths(node, name, prefix=()):
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = prefix + (key,)
            if key == name:
                found.append(path)
            found.extend(_b4f_key_paths(value, name, path))
    return found


def _b4f_assign(cfg, path, value):
    node = cfg
    for key in path[:-1]:
        node = node[key]
    assert path[-1] in node, path
    node[path[-1]] = value


def _b4f_smoke_cfg():
    import copy

    cfg = copy.deepcopy(_design_cfg())
    _b4f_assign(cfg, ("scope", "setups"), [["EXACT", 24, 0]])
    _b4f_assign(cfg, ("scope", "applications"), ["RESIDUAL"])
    _b4f_assign(cfg, ("scope", "families"), ["F2_STRUCTURED_RESIDUAL"])
    _b4f_assign(cfg, ("scope", "policies"), ["FULL_K", "ORACLE_INFO_MIX"])
    science = (
        ("H", 6),
        ("T_fit", 48),
        ("alpha", 0.05),
        ("gamma_M_sensitivity", 6 / 0.05),
    )
    for name, value in science:
        paths = _b4f_key_paths(cfg, name)
        assert paths, name
        for path in paths:
            _b4f_assign(cfg, path, value)
    sizes = {"DEV_NULL": 19, "DEV_ALT": 3, "CAL_NULL": 19, "HOLD_NULL": 3, "ALT": 3}
    for name, value in sizes.items():
        _b4f_assign(cfg, ("modes", "smoke", "sizes", name), value)
    return cfg


def _b4f_durable(staging):
    volatile = {"resources.json", "status.json"}
    return {
        name: data
        for name, data in _tree(staging).items()
        if name not in volatile
    }


def test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three(
    tmp_path, monkeypatch
):
    import collections
    import json
    import multiprocessing
    import sys
    from collections.abc import Mapping

    run_phases = _kernel("run_phases")
    module = sys.modules[run_phases.__module__]
    phases = list(module.PHASES)
    assert phases == ["SETUP", "DEV", "CAL", "NULL_PLAN", "HOLD", "ALT"]
    mode = "smoke"
    cfg = _b4f_smoke_cfg()
    desc = module.design_descriptor(cfg, mode)
    real_get_context = multiprocessing.get_context
    real_batch = module.score_path_batch
    active = {"jobs": None}
    requested = collections.defaultdict(list)
    batches = collections.Counter()

    def get_context_spy(method=None):
        requested[active["jobs"]].append(method)
        if active["jobs"] == 1 and method == "spawn":
            raise AssertionError("jobs=1 requested a spawn context")
        return real_get_context(method)

    def batch_spy(*args, **kwargs):
        batches[active["jobs"]] += 1
        return real_batch(*args, **kwargs)

    monkeypatch.setattr(multiprocessing, "get_context", get_context_spy)
    monkeypatch.setattr(module, "score_path_batch", batch_spy)
    results, durable = {}, {}
    for jobs in (1, 3):
        active["jobs"] = jobs
        grant = module.authorize(mode, cfg, desc, jobs)
        staging = module.open_staging(tmp_path / f"logs-jobs-{jobs}", desc, False)
        plan = module.partition_plan(desc)
        context = dict(module.start_invocation(staging, grant, plan, "invocation-1"))
        context["jobs"] = jobs
        results[jobs] = run_phases(cfg, mode, context)
        durable[jobs] = _b4f_durable(staging)
        did = module.design_id(desc)
        assert isinstance(results[jobs], dict)
        assert list(results[jobs]) == phases and len(phases) == 6
        expected = {"design.json"}
        for phase, record in results[jobs].items():
            assert isinstance(record, Mapping)
            assert json.loads(durable[jobs][f"phases/{phase}.json"]) == record
            expected.add(f"phases/{phase}.json")
            assert [row["key"] for row in record["partitions"]] == list(plan[phase])
            for row in record["partitions"]:
                sha, n_rows, _ = module._verify_partition(
                    staging, did, record["upstream"], row["key"]
                )
                assert row["sha256"] == sha and row["n_rows"] == n_rows
                assert n_rows > 0
                stem = (
                    module._partition_path(
                        staging, did, record["upstream"], row["key"]
                    )
                    .relative_to(staging)
                    .as_posix()
                )
                expected.update((stem + ".json", stem + ".npz"))
        null_plan = results[jobs]["NULL_PLAN"]
        assert null_plan["derived"] == {"status": "NOT_APPLICABLE"}
        assert not null_plan["partitions"]
        assert set(durable[jobs]) == expected
    active["jobs"] = None
    assert "spawn" not in requested[1]
    assert "spawn" in requested[3]
    assert batches[1] > 0 and batches[3] > 0
    assert set(durable) == {1, 3}
    assert durable[1] == durable[3]

    def batch_trap(*args, **kwargs):
        raise AssertionError("replay scored a new path batch")

    monkeypatch.setattr(module, "score_path_batch", batch_trap)
    active["jobs"] = "replay"
    grant = module.authorize(mode, cfg, desc, 3)
    staging = module.open_staging(tmp_path / "logs-jobs-3", desc, True)
    plan = module.partition_plan(desc)
    context = dict(module.start_invocation(staging, grant, plan, "invocation-2"))
    context["jobs"] = 3
    replay = run_phases(cfg, mode, context)
    assert list(replay) == phases
    assert replay == results[3]
    after = _b4f_durable(staging)
    assert after == durable[3]


def test_b4g_cal_scoring_deadline_records_blocked_status_then_resumes(tmp_path):
    import json

    module = pio()
    cfg = _b4f_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    plan = module.partition_plan(desc)
    real_score = module.score_path_batch

    reference_log = tmp_path / "reference"
    reference_log.mkdir()
    reference_state = {"wall": 1000.0, "cpu": 10.0}
    with pytest.MonkeyPatch.context() as mp:
        _b1m_clock(mp, reference_state)
        reference = module.open_staging(reference_log, desc, False)
        reference_grant = module.authorize(mode, cfg, desc, 1)
        reference_context = module.start_invocation(
            reference, reference_grant, plan, "reference"
        )
        reference_records = module.run_phases(cfg, mode, reference_context)
    reference_durable = _b4f_durable(reference)

    work_log = tmp_path / "work"
    work_log.mkdir()
    state = {"wall": 1000.0, "cpu": 10.0}
    seen = {"before": None}

    def interrupt(desc, frame, fit, application, requests, **kwargs):
        role = requests[0][0][5]
        if role == "CAL_NULL" and seen["before"] is None:
            seen["before"] = _b4f_durable(staging)
            state["wall"] = kwargs["deadline"]
            state["cpu"] += 8.0
        return real_score(desc, frame, fit, application, requests, **kwargs)

    with pytest.MonkeyPatch.context() as mp:
        _b1m_clock(mp, state)
        grant = module.authorize(mode, cfg, desc, 1)
        staging = module.open_staging(work_log, desc, False)
        mp.setattr(module, "score_path_batch", interrupt)
        context = module.start_invocation(staging, grant, plan, "interrupted")
        with pytest.raises(pdb.ResourceBlocked):
            module.run_phases(cfg, mode, context)

    assert seen["before"] is not None
    after = _b4f_durable(staging)
    assert after == seen["before"]
    assert set(after) < set(reference_durable)
    assert {rel: reference_durable[rel] for rel in after} == after
    phase_names = sorted(
        str(rel) for rel in after if str(rel).startswith("phases/")
    )
    assert phase_names == ["phases/DEV.json", "phases/SETUP.json"]

    ledger = json.loads((staging / "resources.json").read_text())
    assert ledger["cpu_seconds"]["interrupted"] == 8.0

    missing = [
        {"phase": phase, "key": key}
        for phase in ("CAL", "NULL_PLAN", "HOLD", "ALT")
        for key in plan[phase]
    ]
    status_path = staging / "status.json"
    assert status_path.is_file()
    assert json.loads(status_path.read_text()) == {
        "status": "BLOCKED_RESOURCE",
        "design_id": did,
        "last_complete_phase": "DEV",
        "missing_partitions": missing,
    }

    resume_roles = []
    dev_calls = []

    def resume_score(desc, frame, fit, application, requests, **kwargs):
        resume_roles.append(requests[0][0][5])
        return real_score(desc, frame, fit, application, requests, **kwargs)

    def trapped_dev_choices(*args, **kwargs):
        dev_calls.append((args, kwargs))
        raise AssertionError("dev_choices reran on resume")

    with pytest.MonkeyPatch.context() as mp:
        _b1m_clock(mp, state)
        mp.setattr(module, "score_path_batch", resume_score)
        mp.setattr(module, "dev_choices", trapped_dev_choices)
        resumed = module.open_staging(work_log, desc, True)
        resume_grant = module.authorize(mode, cfg, desc, 1)
        resume_context = module.start_invocation(resumed, resume_grant, plan, "resume")
        records = module.run_phases(cfg, mode, resume_context)

    assert resumed == staging
    assert dev_calls == []
    assert "CAL_NULL" in resume_roles
    assert [role for role in resume_roles if str(role).startswith("DEV")] == []
    assert records == reference_records
    assert _b4f_durable(resumed) == reference_durable
    resumed_ledger = json.loads((resumed / "resources.json").read_text())
    assert (
        resumed_ledger["cpu_seconds"]["interrupted"]
        == ledger["cpu_seconds"]["interrupted"]
    )


def test_b4h_export_calibration_fair_csv_byte_stable(tmp_path, monkeypatch):
    _kernel("export_calibration")
    import hashlib
    import json

    import pandas as pd

    module = pio()
    cfg = _b4f_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4h-token")
    module.setup_phase(cfg, mode, context)
    module.dev_phase(cfg, mode, context)
    record = module.cal_phase(cfg, mode, context)

    derived = record["derived"]
    thresholds = derived["thresholds"]
    assert derived["rule"] == "predictive_exchangeable_rank_v2"
    oracle_ids = [k for k, v in thresholds.items() if v.get("family") is not None]
    plain_ids = [k for k, v in thresholds.items() if v.get("family") is None]
    assert len(thresholds) == 2
    assert len(oracle_ids) == 1 and len(plain_ids) == 1
    assert thresholds[oracle_ids[0]]["family"] == "F2_STRUCTURED_RESIDUAL"
    assert (
        thresholds[oracle_ids[0]]["qualification"]
        == "NON_DEPLOYABLE_ORACLE_CALIBRATION"
    )
    assert thresholds[plain_ids[0]].get("qualification") is None

    order_before = list(thresholds)
    snapshot = json.dumps(record, sort_keys=True, default=repr)
    reversed_record = dict(record)
    reversed_record["derived"] = dict(derived)
    reversed_record["derived"]["thresholds"] = dict(
        reversed(list(thresholds.items()))
    )
    assert list(reversed_record["derived"]["thresholds"]) == order_before[::-1]
    assert list(reversed_record["derived"]["thresholds"]) != order_before
    assert list(record["derived"]["thresholds"]) == order_before

    real_save = module.pipelines.save_fair_csv
    save_calls = []

    def spy_save(*args, **kwargs):
        save_calls.append((args, kwargs))
        return real_save(*args, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("export_calibration must not score or rank")

    out_a = tmp_path / "publish" / "a"
    out_b = tmp_path / "publish" / "b"
    out_a.mkdir(parents=True)
    out_b.mkdir(parents=True)
    logs_before = _tree(tmp_path / "logs")
    with monkeypatch.context() as mp:
        _no_draws_or_workers(mp)
        mp.setattr(module, "score_path_batch", forbidden)
        mp.setattr(pdb, "rank_threshold", forbidden)
        mp.setattr(module.pipelines, "save_fair_csv", spy_save)
        sha_a = module.export_calibration(out_a, did, record)
        sha_b = module.export_calibration(out_b, did, reversed_record)

    assert len(save_calls) == 2
    assert _tree(tmp_path / "logs") == logs_before
    assert json.dumps(record, sort_keys=True, default=repr) == snapshot
    assert list(record["derived"]["thresholds"]) == order_before
    for out in (out_a, out_b):
        assert sorted(
            p.relative_to(out).as_posix() for p in out.rglob("*")
        ) == ["calibration.csv"]

    data_a = (out_a / "calibration.csv").read_bytes()
    data_b = (out_b / "calibration.csv").read_bytes()
    assert sha_a == hashlib.sha256(data_a).hexdigest()
    assert sha_b == hashlib.sha256(data_b).hexdigest()
    assert data_a == data_b
    assert sha_a == sha_b
    assert b"realization_id" not in data_a

    header = [
        "design_id",
        "calibration_id",
        "setup_id",
        "policy_id",
        "family",
        "qualification",
        "rule",
        "n_cal",
        "maxima_sha256",
        "h",
        "r",
        "alarms",
    ]
    id_cols = ["design_id", "calibration_id", "setup_id", "policy_id", "maxima_sha256"]
    frame = pd.read_csv(
        out_a / "calibration.csv",
        dtype={c: "string" for c in id_cols},
        float_precision="round_trip",
    )
    assert list(frame.columns) == header
    assert len(frame) == len(thresholds)
    expected_order = sorted(thresholds)
    assert frame["calibration_id"].tolist() == expected_order
    for row, cid in zip(frame.to_dict("records"), expected_order):
        exp = thresholds[cid]
        assert row["design_id"] == did
        assert row["rule"] == derived["rule"]
        for key in ("setup_id", "policy_id", "maxima_sha256"):
            assert row[key] == exp[key]
        for key in ("n_cal", "h", "r", "alarms"):
            assert row[key] == exp[key]
        if exp.get("family") is None:
            assert pd.isna(row["family"])
            assert pd.isna(row["qualification"])
        else:
            assert row["family"] == exp["family"]
            assert row["qualification"] == exp["qualification"]


def test_b4i_export_alt_selections_offline_from_staging(tmp_path, monkeypatch):
    import hashlib

    import numpy as np
    import pandas as pd
    import pytest

    export = _kernel("export_alt_selections")
    module = pio()
    mode = "smoke"
    cfg = _b4f_smoke_cfg()
    cfg["scope"]["setups"] = [["EXACT", 24, 0], ["FITTED_LW_T7", 24, 0]]
    cfg["scope"]["policies"] = ["FULL_K", "ORACLE_INFO_MIX", "ONLINE_INFO_MIX_W32"]
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4i-token")
    records = module.run_phases(cfg, mode, context)

    campaign = desc["campaign"]
    gamma = float(desc["science"]["parameters"]["gamma_M"])
    trials = records["ALT"]["derived"]["trials"]
    thresholds = records["CAL"]["derived"]["thresholds"]
    dev_setups = records["DEV"]["derived"]["setups"]
    setup_rows = records["SETUP"]["derived"]["setups"]
    caches = {}

    def cached(key):
        ck = pdb.canon(key)
        if ck not in caches:
            _, _, cache_arrays = module._verify_partition(staging, did, {}, key)
            caches[ck] = module._setup_cache(cache_arrays, key)
        return caches[ck]

    expected = []
    upstream = records["ALT"]["upstream"]
    for row in records["ALT"]["partitions"]:
        assert set(row) == {"key", "sha256", "n_rows"}
        key = row["key"]
        assert key[0] == "ALT"
        arm, n_cfg, fit_id, app, family = key[1:]
        setup = [arm, n_cfg, fit_id]
        trial = trials[pdb.canon(key)]
        assert trial["family"] == family
        assert trial["oracle_basis"] in (
            "EXACT_ADDITIVE_KL",
            "ORACLE_DIAGONAL_GAUSSIAN_PROXY",
        )
        sha, n, arrays = module._verify_partition(staging, did, upstream, key)
        assert sha == row["sha256"]
        assert n == row["n_rows"]
        assert n == desc["sizes"]["ALT"]
        frame = cached(["frame", campaign, n_cfg])
        fit = frame if arm == "EXACT" else cached(["fit", campaign, *setup])
        universe = setup_rows[pdb.canon(setup)]["applications"][app]["universe"]
        deltas = np.stack(
            [
                np.asarray(
                    module.direction_information(
                        desc,
                        frame,
                        fit,
                        setup,
                        app,
                        ("meta", campaign, *setup, "ALT", family, i),
                    )["delta"]
                )
                for i in range(n)
            ]
        )
        diag = module.projection_diagnostics(frame, fit, universe, deltas, arm)
        q, beta, C0 = diag["q"], diag["beta"], diag["C0"]
        primary = dev_setups[pdb.canon(setup)][app]["policies"]["PRIMARY"]
        labels = {value["policy_id"]: label for label, value in primary.items()}
        for cid in trial["calibration_ids"]:
            mask = np.asarray(arrays[f"mask_{cid}"])
            assert mask.dtype == np.uint32
            assert mask.shape == (n, 6)
            per_path = _b3j_expect(mask, q, beta, C0, gamma, _b3j_kl_chol)
            d = np.array(
                [bin(int(w)).count("1") for w in mask.ravel()], dtype=np.int64
            )
            costs = [float(pdb.mixture_cost(int(x), gamma)) for x in d]
            pid = thresholds[cid]["policy_id"]
            expected.append(
                {
                    "design_id": str(did),
                    "setup_id": str(trial["setup_id"]),
                    "application": str(app),
                    "policy": str(labels[pid]),
                    "policy_id": str(pid),
                    "calibration_id": str(cid),
                    "family": str(family),
                    "info_basis": str(trial["oracle_basis"]),
                    "metric_basis": "ANALYTIC_PROXY",
                    "gamma_M": gamma,
                    "horizon": 6,
                    "n_alt": n,
                    "alt_payload_sha256": str(sha),
                    "d_mean": float(np.mean(d)),
                    "I_mean": float(np.mean(per_path["I_surrogate"])),
                    "M_mean": float(np.mean(costs)),
                    "V_bar": float(np.mean(per_path["vbar_surrogate"])),
                    "I_joint_mean": float(np.mean(per_path["I_joint"])),
                    "V_joint_bar": float(np.mean(per_path["vbar_joint"])),
                }
            )

    def order_key(r):
        return (r["setup_id"], r["application"], r["family"], r["calibration_id"])

    expected.sort(key=order_key)
    assert len(expected) == 6
    assert len({order_key(r) for r in expected}) == len(expected)
    assert {r["info_basis"] for r in expected} == {
        "EXACT_ADDITIVE_KL",
        "ORACLE_DIAGONAL_GAUSSIAN_PROXY",
    }
    for basis in ("EXACT_ADDITIVE_KL", "ORACLE_DIAGONAL_GAUSSIAN_PROXY"):
        assert sorted(
            r["policy"] for r in expected if r["info_basis"] == basis
        ) == ["FULL_K", "ONLINE_INFO_MIX_W32", "ORACLE_INFO_MIX"], basis

    before = _tree(staging)

    def trap(*args, **kwargs):
        raise AssertionError("export_alt_selections must not recompute")

    for name in ("score_path_batch", "nonoracle_scan", "oracle_scan", "fit_record"):
        monkeypatch.setattr(module, name, trap)
    monkeypatch.setattr(pdb, "rank_threshold", trap)
    real_save = module.pipelines.save_fair_csv
    calls = []

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return real_save(*args, **kwargs)

    monkeypatch.setattr(module.pipelines, "save_fair_csv", spy)

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    digest = export(out_dir, staging, did, records)

    assert len(calls) == 1
    assert sorted(p.name for p in out_dir.iterdir()) == ["selections.csv"]
    path = out_dir / "selections.csv"
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert _tree(staging) == before

    header = [
        "design_id",
        "setup_id",
        "application",
        "policy",
        "policy_id",
        "calibration_id",
        "family",
        "info_basis",
        "metric_basis",
        "gamma_M",
        "horizon",
        "n_alt",
        "alt_payload_sha256",
        "d_mean",
        "I_mean",
        "M_mean",
        "V_bar",
        "I_joint_mean",
        "V_joint_bar",
    ]
    text_cols = header[:9] + ["alt_payload_sha256"]
    int_cols = ["horizon", "n_alt"]
    float_cols = [
        "gamma_M",
        "d_mean",
        "I_mean",
        "M_mean",
        "V_bar",
        "I_joint_mean",
        "V_joint_bar",
    ]
    df = pd.read_csv(
        path,
        float_precision="round_trip",
        dtype={c: str for c in text_cols},
    )
    assert list(df.columns) == header
    got = df.to_dict(orient="records")
    assert len(got) == len(expected)
    got_order = [order_key(r) for r in got]
    assert got_order == sorted(got_order)
    assert got_order == [order_key(r) for r in expected]
    assert set(df["metric_basis"]) == {"ANALYTIC_PROXY"}
    assert set(df["info_basis"]) == {
        "EXACT_ADDITIVE_KL",
        "ORACLE_DIAGONAL_GAUSSIAN_PROXY",
    }
    for g, e in zip(got, expected):
        for c in text_cols:
            assert g[c] == e[c], c
        for c in int_cols:
            assert g[c] == e[c], c
        for c in float_cols:
            assert float(g[c]) == pytest.approx(e[c], rel=1e-9, abs=1e-12), c


def test_b4j_export_trial_summaries_compact_hold_alt_rows(tmp_path, monkeypatch):
    import hashlib

    import numpy as np
    import pandas as pd
    import pytest

    _kernel("export_trial_summaries")
    module = pio()
    cfg = _b4f_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4j-token")
    records = module.run_phases(cfg, mode, context)
    horizon = desc["science"]["parameters"]["H"]
    assert horizon == 6
    header = [
        "design_id",
        "role",
        "setup_id",
        "application",
        "family",
        "policy_id",
        "calibration_id",
        "qualification",
        "partition_key",
        "partition_sha256",
        "horizon",
        "n",
        "k",
        "n_censored",
        "alarm_rate",
        "rmst_h",
        "median_detected_h",
        "null_lo",
        "null_hi",
        "null_status",
    ]
    thresholds = records["CAL"]["derived"]["thresholds"]
    checks = records["HOLD"]["derived"]["null_checks"]
    setups = records["SETUP"]["derived"]["setups"]
    expected = []
    mixed_alt = False
    for phase, role in (("HOLD", "HOLD_NULL"), ("ALT", "ALT")):
        upstream = records[phase]["upstream"]
        for row in records[phase]["partitions"]:
            assert set(row) == {"key", "sha256", "n_rows"}
            key = row["key"]
            assert key[0] == role
            assert len(key) == (6 if role == "ALT" else 5)
            sha, n_rows, arrays = module._verify_partition(staging, did, upstream, key)
            assert (sha, n_rows) == (row["sha256"], row["n_rows"])
            setup_id = setups[pdb.canon(key[1:4])]["applications"][key[4]]["setup_id"]
            for cid in thresholds:
                first = np.asarray(arrays["first_" + cid])
                assert first.shape == (n_rows,)
                assert all(v == -1 or 1 <= v <= horizon for v in first.tolist())
                hit = first > 0
                n = int(first.size)
                k = int(hit.sum())
                check = checks[cid]
                assert check.get("qualification") in (None, "NON_DEPLOYABLE")
                out = {
                    "design_id": did,
                    "role": role,
                    "setup_id": setup_id,
                    "application": key[4],
                    "family": key[5] if role == "ALT" else check.get("family"),
                    "policy_id": thresholds[cid]["policy_id"],
                    "calibration_id": cid,
                    "qualification": check.get("qualification"),
                    "partition_key": pdb.canon(key),
                    "partition_sha256": sha,
                    "horizon": horizon,
                    "n": n,
                    "k": k,
                    "n_censored": n - k,
                    "alarm_rate": k / n,
                    "rmst_h": None,
                    "median_detected_h": None,
                    "null_lo": None,
                    "null_hi": None,
                    "null_status": None,
                }
                if role == "HOLD_NULL":
                    assert (check["n"], check["k"]) == (n, k)
                    out["null_lo"] = check["lo"]
                    out["null_hi"] = check["hi"]
                    out["null_status"] = check["status"]
                else:
                    out["rmst_h"] = float(np.where(hit, first, horizon).mean())
                    if k:
                        out["median_detected_h"] = float(np.median(first[hit]))
                    if 0 < k < n and (first[hit] < horizon).any():
                        mixed_alt = True
                expected.append(out)
    expected.sort(key=lambda r: (r["role"], r["partition_key"], r["calibration_id"]))
    assert [r["role"] for r in expected] == ["ALT", "ALT", "HOLD_NULL", "HOLD_NULL"]
    assert mixed_alt

    real_save = module.pipelines.save_fair_csv
    saves = []

    def spy(*args, **kwargs):
        saves.append((args, kwargs))
        return real_save(*args, **kwargs)

    def recompute(*args, **kwargs):
        raise AssertionError("export recomputed trial results")

    monkeypatch.setattr(module.pipelines, "save_fair_csv", spy)
    _no_draws_or_workers(monkeypatch)
    for name in ("score_path_batch", "nonoracle_scan", "oracle_scan"):
        monkeypatch.setattr(module, name, recompute)
    monkeypatch.setattr(pdb, "rank_threshold", recompute)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    staged = _tree(staging)
    before = sorted(tmp_path.rglob("*"))
    digest = module.export_trial_summaries(out_dir, staging, did, records)
    csv_path = out_dir / "trials_summary.csv"
    assert sorted(tmp_path.rglob("*")) == sorted(before + [csv_path])
    assert _tree(staging) == staged
    assert len(saves) == 1
    assert digest == hashlib.sha256(csv_path.read_bytes()).hexdigest()
    text_cols = [
        "design_id",
        "role",
        "setup_id",
        "application",
        "family",
        "policy_id",
        "calibration_id",
        "qualification",
        "partition_key",
        "partition_sha256",
        "null_status",
    ]
    frame = pd.read_csv(
        csv_path,
        dtype={col: str for col in text_cols},
        float_precision="round_trip",
    )
    assert list(frame.columns) == header
    for col in ("horizon", "n", "k", "n_censored"):
        assert pd.api.types.is_integer_dtype(frame[col])
    approx_cols = {"alarm_rate", "rmst_h", "median_detected_h"}
    assert len(frame) == len(expected)
    for got, want in zip(frame.to_dict("records"), expected):
        for col in header:
            if want[col] is None:
                assert pd.isna(got[col]), col
            elif col in approx_cols:
                assert got[col] == pytest.approx(want[col]), col
            else:
                assert got[col] == want[col], col


def test_b4k_export_aggregates_descriptive_v_rmst(tmp_path, monkeypatch):
    _kernel("export_aggregates")
    module = pio()
    import hashlib
    import pandas as pd
    import pytest

    cfg = _b4f_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4k-token")
    records = module.run_phases(cfg, mode, context)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    sel_sha = module.export_alt_selections(out_dir, staging, did, records)
    trials_sha = module.export_trial_summaries(out_dir, staging, did, records)
    sel_path = out_dir / "selections.csv"
    trials_path = out_dir / "trials_summary.csv"

    str_fields = (
        "design_id",
        "setup_id",
        "application",
        "policy_id",
        "calibration_id",
        "family",
        "role",
        "alt_payload_sha256",
        "partition_sha256",
    )

    def read(path):
        head = pd.read_csv(path, nrows=0).columns
        return pd.read_csv(
            path,
            float_precision="round_trip",
            dtype={c: str for c in str_fields if c in head},
        )

    sel = read(sel_path)
    trials = read(trials_path)
    keys = ["setup_id", "application", "policy_id", "calibration_id", "family"]
    alt = trials[trials["role"] == "ALT"]
    merged = sel.merge(alt, on=keys, how="inner", validate="one_to_one")
    assert len(merged) == 2
    assert (merged["alt_payload_sha256"] == merged["partition_sha256"]).all()
    groups = merged[["setup_id", "application"]].drop_duplicates()
    assert len(groups) == 1
    setup_id, application = groups.iloc[0].tolist()
    for col in ("V_bar", "V_joint_bar", "rmst_h"):
        assert merged[col].nunique() == 2

    def spearman_pair(x, y):
        dx = x[1] - x[0]
        dy = y[1] - y[0]
        if dx == 0 or dy == 0:
            return None
        return 1.0 if (dx > 0) == (dy > 0) else -1.0

    rmst = merged["rmst_h"].tolist()
    expected_rho = spearman_pair(merged["V_bar"].tolist(), rmst)
    expected_joint_rho = spearman_pair(merged["V_joint_bar"].tolist(), rmst)
    assert expected_rho is not None
    assert expected_joint_rho is not None

    def trap(*args, **kwargs):
        raise AssertionError("simulation called during export_aggregates")

    for name in ("score_path_batch", "nonoracle_scan", "oracle_scan", "masked_alt_information"):
        monkeypatch.setattr(module, name, trap)
    monkeypatch.setattr(module.pdb, "rank_threshold", trap)
    calls = []
    real_save = module.pipelines.save_fair_csv

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return real_save(*args, **kwargs)

    monkeypatch.setattr(module.pipelines, "save_fair_csv", spy)

    def snapshot():
        return {
            str(p.relative_to(out_dir)): p.read_bytes()
            for p in out_dir.rglob("*")
            if p.is_file()
        }

    files_before = snapshot()
    tree_before = _tree(staging)
    agg_path = out_dir / "aggregates.csv"

    wrong_sel_sha = "0" * 64 if sel_sha != "0" * 64 else "1" * 64
    assert wrong_sel_sha != sel_sha
    with pytest.raises(module.PartitionMismatch):
        module.export_aggregates(out_dir, did, wrong_sel_sha, trials_sha)
    assert not agg_path.exists()
    assert calls == []
    assert snapshot() == files_before

    agg_sha = module.export_aggregates(out_dir, did, sel_sha, trials_sha)
    files_after = snapshot()
    assert set(files_after) - set(files_before) == {"aggregates.csv"}
    assert {k: v for k, v in files_after.items() if k != "aggregates.csv"} == files_before
    assert _tree(staging) == tree_before
    assert len(calls) == 1
    assert hashlib.sha256(agg_path.read_bytes()).hexdigest() == agg_sha

    agg = pd.read_csv(
        agg_path,
        float_precision="round_trip",
        dtype={
            c: str
            for c in (
                "design_id",
                "setup_id",
                "application",
                "status",
                "selections_sha256",
                "trials_sha256",
            )
        },
    )
    assert list(agg.columns) == [
        "design_id",
        "setup_id",
        "application",
        "n_cells",
        "spearman_rho",
        "spearman_joint_rho",
        "status",
        "selections_sha256",
        "trials_sha256",
    ]
    assert len(agg) == 1
    row = agg.iloc[0]
    assert row["design_id"] == did
    assert (row["setup_id"], row["application"]) == (setup_id, application)
    assert int(row["n_cells"]) == 2
    assert float(row["spearman_rho"]) == expected_rho
    assert float(row["spearman_joint_rho"]) == expected_joint_rho
    assert row["status"] == "DESCRIPTIVE_V_RMST"
    assert row["selections_sha256"] == sel_sha
    assert row["trials_sha256"] == trials_sha


def test_b4l_finalize_publishes_exported_scientific_payloads(tmp_path, monkeypatch):
    import hashlib
    import json
    from pathlib import Path, PurePosixPath

    import pandas as pd

    _kernel("export_payloads")
    module = pio()
    cfg = _b4f_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4l-token")
    output_dir = tmp_path / "b4l-publication"
    temp_dir = output_dir.parent / f".{output_dir.name}.publish-{did[:16]}.tmp"
    phases = Path(staging) / "phases"
    payloads = (
        "calibration.csv",
        "selections.csv",
        "trials_summary.csv",
        "aggregates.csv",
        "issues.csv",
    )
    metadata = ("manifest.json", "summary.md", "telemetry.json")
    columns = [
        "design_id",
        "phase",
        "setup_id",
        "policy_id",
        "calibration_id",
        "family",
        "status",
        "qualification",
    ]
    witness = {"memory_peak_scope": "NOT_MEASURED"}
    real_export = module.export_payloads
    exports = []
    builds = []

    def counting_export(*args):
        exports.append(args)
        return real_export(*args)

    def build(temp, build_did, records):
        shas = module.export_payloads(temp, staging, build_did, records)
        builds.append((Path(temp), build_did, records, shas))
        return witness

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    status_path = staging / "status.json"

    monkeypatch.setattr(module, "export_payloads", counting_export)

    first = module.finalize_planned(staging, output_dir, grant, plan, build)
    assert first == {
        "status": "INCOMPLETE",
        "design_id": did,
        "last_complete_phase": None,
        "missing_partitions": [
            {"phase": phase, "key": key}
            for phase in module.PHASES
            for key in plan[phase]
        ],
    }
    assert json.loads(status_path.read_text()) == first
    assert not output_dir.exists() and not temp_dir.exists()
    assert builds == [] and exports == []
    assert list(phases.glob("FINAL*")) == []

    module.run_phases(cfg, mode, context)
    second = module.finalize_planned(staging, output_dir, grant, plan, build)
    final_path = phases / "FINAL.json"
    final = json.loads(final_path.read_text())
    assert second == final and final["status"] == "PUBLISHED"
    assert json.loads(status_path.read_text()) == {
        "status": "PUBLISHED",
        "design_id": did,
        "last_complete_phase": "ALT",
        "missing_partitions": [],
    }
    assert len(builds) == 1 and len(exports) == 1
    temp, build_did, records, shas = builds[0]
    assert temp == temp_dir and build_did == did and not temp_dir.exists()
    assert Path(exports[0][0]) == temp_dir and exports[0][1] is staging
    assert exports[0][2] == did and exports[0][3] is records
    assert sorted(p.name for p in output_dir.iterdir()) == sorted(payloads + metadata)
    assert list(output_dir.rglob("*.npz")) == []

    actual = {name: sha(output_dir / name) for name in payloads}
    assert isinstance(shas, dict) and shas == actual
    manifest_bytes = (output_dir / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert all(set(row) == {"status", "sha256"} for row in manifest["payloads"].values())
    assert manifest["status"] == "COMPLETE" and manifest["authority"] == grant
    published = {
        name: row["sha256"]
        for name, row in manifest["payloads"].items()
        if row["status"] == "PUBLISHED"
    }
    assert published == actual
    assert all(sha(output_dir / name) == digest for name, digest in published.items())
    realization = manifest["realization_descriptor"]
    assert realization["payloads"] == actual
    rid = hashlib.sha256(pdb.canon(realization).encode()).hexdigest()
    assert manifest["realization_id"] == rid == final["realization_id"]
    assert manifest["design_id"] == did == final["design_id"]
    assert final["manifest_sha256"] == hashlib.sha256(manifest_bytes).hexdigest()
    telemetry = json.loads((output_dir / "telemetry.json").read_text())
    assert witness.items() <= telemetry.items()
    assert (output_dir / "summary.md").is_file()

    local = {
        name: row["sha256"]
        for name, row in manifest["payloads"].items()
        if row["status"] == "LOCAL_HASHED_ONLY"
    }
    assert not set(published) & set(local)
    assert set(published) | set(local) == set(manifest["payloads"])
    partition_files = sorted((staging / "partitions").glob("*.npz"))
    assert local == {p.relative_to(staging).as_posix(): sha(p) for p in partition_files}
    assert len(local) == sum(len(r["partitions"]) for r in records.values())
    assert local
    for name, digest in local.items():
        assert isinstance(name, str) and chr(92) not in name
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and ".." not in rel.parts and rel.as_posix() == name
        assert rel.name not in published and not (output_dir / rel.name).exists()

    issues = pd.read_csv(
        output_dir / "issues.csv",
        dtype={column: str for column in columns},
        float_precision="round_trip",
    )
    assert list(issues.columns) == columns
    checks = records["HOLD"]["derived"]["null_checks"]
    inconclusive = {
        str(cid): check
        for cid, check in checks.items()
        if check["status"] == "NULL_INCONCLUSIVE"
    }
    rows = issues.to_dict("records")
    assert len(inconclusive) == 2 and len(rows) == 2
    assert [row["calibration_id"] for row in rows] == sorted(inconclusive)
    missing = []
    for row in rows:
        check = inconclusive[row["calibration_id"]]
        assert (row["design_id"], row["phase"], row["status"]) == (did, "HOLD", check["status"])
        assert row["setup_id"] == str(check["setup_id"])
        assert row["policy_id"] == str(check["policy_id"])
        for field in ("family", "qualification"):
            if check.get(field) is None:
                assert pd.isna(row[field])
            else:
                assert row[field] == str(check[field])
        missing.append(check.get("family") is None and check.get("qualification") is None)
    assert sorted(missing) == [False, True]

    before = _tree(output_dir)
    final_bytes = final_path.read_bytes()
    third = module.finalize_planned(staging, output_dir, grant, plan, build)
    assert third == second == final
    assert len(builds) == 1 and len(exports) == 1
    assert _tree(output_dir) == before
    assert final_path.read_bytes() == final_bytes
    assert json.loads(final_path.read_text()) == final


def test_b4m_admitted_cli_serial_refusal_parallel_resume(tmp_path, monkeypatch):
    import json
    import multiprocessing

    module = pio()
    cfg = _b4f_smoke_cfg()
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr(module, "REPO_ROOT", project)
    did = module.design_id(module.design_descriptor(cfg, "smoke"))
    tag = did[:16]
    serial_out = tmp_path / "serial" / "study"
    parallel_out = tmp_path / "parallel" / "study"
    serial_out.parent.mkdir()
    parallel_out.parent.mkdir()
    parallel_logs = tmp_path / "parallel-logs"
    serial_staging = (
        module.REPO_ROOT / "logs" / "pca_info_online" / "study" / "staging" / tag
    )
    parallel_staging = parallel_logs / "staging" / tag

    base = ["--config", str(config), "--mode", "smoke"]
    serial_args = base + ["--output-dir", str(serial_out), "--jobs", "1"]
    refused_args = base + ["--output-dir", str(parallel_out), "--jobs", "3"]
    parallel_args = refused_args + ["--log-dir", str(parallel_logs)]
    resume_args = base + [
        "--output-dir",
        str(parallel_out),
        "--jobs",
        "1",
        "--log-dir",
        str(parallel_logs),
        "--resume",
    ]

    real_get_context = multiprocessing.get_context
    methods = []

    def spy_get_context(method=None):
        methods.append(method)
        return real_get_context(method)

    monkeypatch.setattr(multiprocessing, "get_context", spy_get_context)

    assert module.main(serial_args) == 0
    assert "spawn" not in methods
    assert serial_out.is_dir()
    assert serial_staging.is_dir()
    serial_tree = _tree(serial_out)
    serial_durable = _b4f_durable(serial_staging)

    before_refusal = len(methods)
    assert module.main(refused_args) != 0
    assert not parallel_out.exists()
    assert len(methods) == before_refusal
    assert _tree(serial_out) == serial_tree
    assert _b4f_durable(serial_staging) == serial_durable

    before_parallel = len(methods)
    assert module.main(parallel_args) == 0
    assert "spawn" in methods[before_parallel:]
    assert parallel_out.is_dir()
    assert parallel_staging.is_dir()
    parallel_tree = _tree(parallel_out)
    parallel_durable = _b4f_durable(parallel_staging)

    assert parallel_durable == serial_durable
    assert "phases/FINAL.json" in parallel_durable
    telemetry_name = "telemetry.json"
    serial_body = {k: v for k, v in serial_tree.items() if str(k) != telemetry_name}
    parallel_body = {k: v for k, v in parallel_tree.items() if str(k) != telemetry_name}
    assert len(serial_body) == len(serial_tree) - 1
    assert len(parallel_body) == len(parallel_tree) - 1
    assert parallel_body == serial_body

    serial_manifest = json.loads((serial_out / "manifest.json").read_text())
    parallel_manifest = json.loads((parallel_out / "manifest.json").read_text())
    assert serial_manifest["design_id"] == did
    assert parallel_manifest["design_id"] == did
    assert serial_manifest["realization_id"]
    assert parallel_manifest["realization_id"] == serial_manifest["realization_id"]
    csv_names = sorted(
        [
            "calibration.csv",
            "selections.csv",
            "trials_summary.csv",
            "aggregates.csv",
            "issues.csv",
        ]
    )
    for out in (serial_out, parallel_out):
        assert sorted(path.name for path in out.glob("*.csv")) == csv_names
    for manifest in (serial_manifest, parallel_manifest):
        payloads = manifest["payloads"]
        assert sorted({name for name, entry in payloads.items() if entry["status"] == "PUBLISHED"}) == csv_names

    for out, jobs in ((serial_out, 1), (parallel_out, 3)):
        telemetry = json.loads((out / "telemetry.json").read_text())
        assert telemetry["jobs"] == jobs
        assert telemetry["memory_peak_scope"] == "NOT_MEASURED"

    for staging in (serial_staging, parallel_staging):
        status = json.loads((staging / "status.json").read_text())
        assert status == {
            "status": "PUBLISHED",
            "design_id": did,
            "last_complete_phase": "ALT",
            "missing_partitions": [],
        }

    def trap(*args, **kwargs):
        raise AssertionError("resume must not score or publish")

    monkeypatch.setattr(module, "score_path_batch", trap)
    monkeypatch.setattr(module, "export_payloads", trap)
    assert module.main(resume_args) == 0
    assert _tree(parallel_out) == parallel_tree
    assert _b4f_durable(parallel_staging) == parallel_durable


@pytest.mark.parametrize("case", ["before", "after"])
def test_b4n_cli_recovers_each_atomic_publication_boundary(
    tmp_path, monkeypatch, capsys, case
):
    import hashlib
    import json
    import os
    from pathlib import Path

    module = pio()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    cfg = _b4f_smoke_cfg()
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    did = module.design_id(module.design_descriptor(cfg, "smoke"))
    tag = did[:16]
    out = tmp_path / "results" / "pca_info_online" / tag
    staging = tmp_path / "logs" / "pca_info_online" / tag / "staging" / tag
    temp = out.parent / f".{out.name}.publish-{tag}.tmp"
    final_path = staging / "phases" / "FINAL.json"
    argv = ["--config", str(config), "--mode", "smoke"]
    reason = f"b4n injected publication fault at {case} boundary"
    real_export = module.export_payloads
    exports = []

    def export_spy(*args, **kwargs):
        exports.append(args)
        return real_export(*args, **kwargs)

    monkeypatch.setattr(module, "export_payloads", export_spy)
    real_replace = os.replace
    hits = []
    captured = {}

    def faulty_replace(src, dst, *args, **kwargs):
        if (Path(src), Path(dst)) != (temp, out):
            return real_replace(src, dst, *args, **kwargs)
        hits.append((src, dst))
        captured.update(_tree(temp))
        if case == "after":
            real_replace(src, dst, *args, **kwargs)
        raise OSError(reason)

    with monkeypatch.context() as fault:
        fault.setattr(os, "replace", faulty_replace)
        code = module.main(argv)
    err = capsys.readouterr().err
    assert code == 2
    assert reason in err
    assert len(hits) == 1
    assert len(exports) == 1
    assert captured
    pre_resume = _b4f_durable(staging)
    phase_files = {f"phases/{phase}.json" for phase in module.PHASES}
    assert len(phase_files) == 6
    assert phase_files <= set(pre_resume)
    assert any(key.startswith("partitions/") and key.endswith(".npz") for key in pre_resume)
    assert "phases/FINAL.json" not in pre_resume
    assert not final_path.exists()
    if case == "before":
        assert not out.exists()
        assert _tree(temp) == captured
    else:
        assert not temp.exists()
        assert _tree(out) == captured
    rescored = []

    def no_rescore(*args, **kwargs):
        rescored.append(args)
        raise AssertionError("b4n resume must not rescore")

    monkeypatch.setattr(module, "score_path_batch", no_rescore)
    code = module.main([*argv, "--resume"])
    capsys.readouterr()
    assert code == 0
    assert rescored == []
    assert len(hits) == 1
    assert len(exports) == (2 if case == "before" else 1)
    assert not temp.exists()
    published = _tree(out)

    def without_telemetry(tree):
        return {key: value for key, value in tree.items() if key != "telemetry.json"}

    assert without_telemetry(published) == without_telemetry(captured)
    if case == "after":
        assert published == captured
    manifest_bytes = (out / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    captured_manifest = json.loads(captured["manifest.json"])
    final = json.loads(final_path.read_bytes())
    assert manifest["design_id"] == did
    assert manifest["realization_id"] == captured_manifest["realization_id"]
    assert final == {
        "status": "PUBLISHED",
        "design_id": did,
        "realization_id": manifest["realization_id"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    status = json.loads((staging / "status.json").read_bytes())
    assert status == {
        "status": "PUBLISHED",
        "design_id": did,
        "last_complete_phase": "ALT",
        "missing_partitions": [],
    }
    resumed = _b4f_durable(staging)
    assert {key: resumed.get(key) for key in pre_resume} == pre_resume


def _b4o_authorized_cfg(mode):
    module = pio()
    cfg = _b4f_smoke_cfg()
    setup = ['FITTED_LW_GAUSSIAN', 24, 0]
    cfg['scope']['setups'] = [list(setup)]
    cfg['phi']['setup'] = list(setup)
    cfg['scope']['families'] = ['F2_STRUCTURED_RESIDUAL', 'F_HEAD_RESIDUAL']
    cfg['scope']['policies'] = [*module.P_CONF, 'ORACLE_INFO_MIX']
    cfg['modes'][mode]['sizes'] = dict(cfg['modes']['smoke']['sizes'])
    cfg['bootstrap']['B'] = 7
    return cfg


@pytest.mark.parametrize('mode', ['pilot', 'full'])
def test_b4o_cli_pilot_and_full_authorize_before_realization(tmp_path, monkeypatch, capsys, mode):
    import copy
    import hashlib
    import json
    import re

    module = pio()
    assert module.P_CONF == ('ONLINE_INFO_MIX_W128', 'ONLINE_PREFIX_MIX_W128', 'FULL_K')
    base = _b4o_authorized_cfg(mode)
    probe = copy.copy(base)
    probe['seed'] = base['seed'] + 1
    probe_descriptor = module.design_descriptor(probe, mode)
    probe_did = module.design_id(probe_descriptor)
    cfg, did = _authorized(tmp_path, monkeypatch, copy.deepcopy(base), mode)
    assert probe_did != did

    auth = cfg['authorization']
    assert set(auth) == {'stage', 'design_id', 'go_reference'}
    assert auth['stage'] == mode
    assert auth['design_id'] == did
    assert set(auth['go_reference']) == {'path', 'sha256'}
    go_path = tmp_path / auth['go_reference']['path']
    go_bytes = go_path.read_bytes()
    expected_go = f"Synthetic {mode} GO fixture for design {did}\nScope: {pdb.canon(cfg['scope'])}\n"
    assert go_bytes == expected_go.encode()
    assert auth['go_reference']['sha256'] == hashlib.sha256(go_bytes).hexdigest()
    handoff = copy.deepcopy(auth)

    path = _b4a_yaml(tmp_path / 'config.yaml', cfg)
    output = tmp_path / 'published'
    logs = tmp_path / 'logs'
    staging = logs / 'staging' / did[:16]
    assert not output.exists()
    assert not staging.exists()

    rc = module.main([
        '--config', str(path),
        '--mode', mode,
        '--output-dir', str(output),
        '--log-dir', str(logs),
        '--jobs', '1',
    ])
    assert rc == 0, capsys.readouterr().err

    phases = staging / 'phases'
    records = {}
    for phase in module.PHASES:
        records[phase] = json.loads((phases / f'{phase}.json').read_bytes())
        assert records[phase]['phase'] == phase
    final = json.loads((phases / 'FINAL.json').read_bytes())
    manifest_bytes = (output / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)

    assert manifest['status'] == 'COMPLETE'
    assert manifest['authority'] == handoff
    assert manifest['design_id'] == did
    assert final['design_id'] == did
    rid = final['realization_id']
    assert isinstance(rid, str)
    assert re.fullmatch('[0-9a-f]{64}', rid)
    assert rid != did
    assert manifest['realization_id'] == rid
    assert rid.encode('ascii') not in go_bytes
    assert final['manifest_sha256'] == hashlib.sha256(manifest_bytes).hexdigest()
    assert final['status'] == 'PUBLISHED'

    for phase in ('SETUP', 'DEV', 'CAL', 'HOLD', 'ALT'):
        partitions = records[phase]['partitions']
        assert isinstance(partitions, list)
        assert len(partitions) > 0

    null_plan = records['NULL_PLAN']
    if mode == 'pilot':
        assert cfg['modes']['pilot']['null_plan'] is None
        assert null_plan['partitions'] == []
        assert null_plan['derived'] == {'status': 'NOT_APPLICABLE'}
    else:
        plan = cfg['modes']['full']['null_plan']
        assert plan['n_min'] == 2
        assert plan['n_plan'] == 2
        assert plan['n_cap'] == 5
        assert isinstance(null_plan['partitions'], list)
        assert len(null_plan['partitions']) == 1
        n_hold = null_plan['derived']['n_hold']
        assert plan['n_min'] <= n_hold <= plan['n_cap']

    assert go_path.read_bytes() == go_bytes


@pytest.mark.parametrize("stop_after", ("SETUP", "DEV", "CAL", "NULL_PLAN"))
def test_b4p_cli_resumes_after_each_committed_phase(tmp_path, monkeypatch, capsys, stop_after):
    import json

    module = pio()
    cfg, did = _authorized(tmp_path, monkeypatch, _b4o_authorized_cfg("full"), "full")
    config = tmp_path / "config.yaml"
    _b4a_yaml(config, cfg)
    stop = module.PHASES.index(stop_after)
    done = module.PHASES[: stop + 1]
    ref, work = tmp_path / "ref", tmp_path / "work"
    ref_staging, work_staging = (r / "logs" / "staging" / did[:16] for r in (ref, work))
    phases = work_staging / "phases"

    def run(root, *extra):
        out, logs = str(root / "out"), str(root / "logs")
        rc = module.main(["--config", str(config), "--mode", "full", "--jobs", "1",
                          "--output-dir", out, "--log-dir", logs, *extra])
        return rc, capsys.readouterr()

    def published(root):
        tree = _tree(root / "out")
        return {k: v for k, v in tree.items() if k != "telemetry.json"}

    rc, cap = run(ref)
    assert rc == 0, cap.out + cap.err
    ref_durable = _b4f_durable(ref_staging)
    real_record, fired = module.phase_record, []
    reason = f"b4p injected stop after {stop_after}"

    def record(staging, phase, upstream, partitions, derived):
        result = real_record(staging, phase, upstream, partitions, derived)
        commit = partitions is not None and derived is not None
        if commit and phase == stop_after and work_staging.samefile(staging):
            fired.append(phase)
            raise OSError(reason)
        return result

    with monkeypatch.context() as m:
        m.setattr(module, "phase_record", record)
        rc, cap = run(work)
    assert fired == [stop_after]
    assert rc == 2 and reason in cap.out + cap.err, cap.out + cap.err
    assert not (phases / "FINAL.json").exists()
    assert not (work / "out").exists()
    assert sorted(p.name for p in phases.glob("*.json")) == sorted(f"{p}.json" for p in done)
    records = {phase: json.loads((phases / f"{phase}.json").read_bytes()) for phase in done}
    for phase, record in records.items():
        for row in record["partitions"]:
            stem = module._partition_path(work_staging, did, record["upstream"], row["key"])
            npz, meta = stem.with_suffix(".npz"), stem.with_suffix(".json")
            assert npz.is_file() and meta.is_file(), (phase, row)
            assert pdb.file_sha256(npz) == row["sha256"], (phase, row)
    pre = _b4f_durable(work_staging)
    assert {k: ref_durable.get(k) for k in pre} == pre
    if stop_after == "NULL_PLAN":
        plan = records["NULL_PLAN"]
        derived = plan["derived"]
        n_hold = derived["n_hold"]
        bounds = cfg["modes"]["full"]["null_plan"]
        assert len(plan["partitions"]) == 1, plan["partitions"]
        assert derived["status"] in {"PLAN_ADEQUATE", "PLAN_CAPPED_EXPECT_INCONCLUSIVE"}, derived
        assert type(n_hold) is int and bounds["n_min"] <= n_hold <= bounds["n_cap"], n_hold
    owner = {"DEV_NULL": "DEV", "DEV_ALT": "DEV", "CAL_NULL": "CAL",
             "NULL_PLAN": "NULL_PLAN", "HOLD_NULL": "HOLD", "ALT": "ALT"}
    real_batch, roles = module.score_path_batch, []

    def batch(desc, frame, fit, application, requests, **kwargs):
        requests = list(requests)
        roles.extend(key[5] for key, _ in requests)
        return real_batch(desc, frame, fit, application, requests, **kwargs)

    def trap(*_args, **_kwargs):
        raise AssertionError("b4p resume recomputed committed work")

    with monkeypatch.context() as m:
        m.setattr(module, "score_path_batch", batch)
        if stop >= module.PHASES.index("DEV"):
            m.setattr(module, "dev_choices", trap)
        if stop >= module.PHASES.index("CAL"):
            m.setattr(pdb, "rank_threshold", trap)
        rc, cap = run(work, "--resume")
    assert rc == 0, cap.out + cap.err
    assert all(module.PHASES.index(owner[r]) > stop for r in roles), sorted(set(roles))
    post = _b4f_durable(work_staging)
    assert {k: post.get(k) for k in pre} == pre
    assert post == ref_durable
    ref_pub, work_pub = published(ref), published(work)
    assert work_pub == ref_pub
    rids = [json.loads((s / "phases" / "FINAL.json").read_bytes())["realization_id"]
            for s in (ref_staging, work_staging)]
    rids += [json.loads(p["manifest.json"])["realization_id"] for p in (ref_pub, work_pub)]
    assert isinstance(rids[0], str) and rids[0] and rids == [rids[0]] * 4


@pytest.mark.parametrize(
    "case",
    [
        "foreign_design",
        "wrong_upstream",
        "n_hold_above_cap",
        "n_hold_below_min",
        "hold_without_null_plan",
        "npz_flipped",
        "npz_missing",
    ],
)
def test_b4q_cli_refuses_stale_phase_and_partition_state(tmp_path, monkeypatch, capsys, case):
    import json

    module = pio()
    cfg, did = _authorized(tmp_path, monkeypatch, _b4o_authorized_cfg("full"), "full")
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = [
        "--config", str(config), "--mode", "full", "--jobs", "1",
        "--output-dir", str(out), "--log-dir", str(logs),
    ]
    staging = logs / "staging" / did[:16]
    phases = staging / "phases"

    def write(path, record):
        path.write_bytes((pdb.canon(record) + "\n").encode("utf-8"))

    def redigest(name, record):
        record["phase_digest"] = module._phase_digest(
            did, name, record["upstream"], record["partitions"], record["derived"]
        )

    code = module.main(argv)
    captured = capsys.readouterr()
    assert code == 0, captured.err
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "COMPLETE"
    final = json.loads((phases / "FINAL.json").read_text(encoding="utf-8"))
    assert final["status"] == "PUBLISHED"
    assert final["design_id"] == did
    published = _tree(out)
    assert published
    assert staging.is_dir() and phases.is_dir()

    if case == "foreign_design":
        path = staging / "design.json"
        record = json.loads(path.read_bytes())
        full = record["design_id"]
        assert full[:16] == did[:16]
        record["design_id"] = full[:16] + ("1" if full[16] == "0" else "0") + full[17:]
        assert record["design_id"][:16] == full[:16]
        assert record["design_id"][16] != full[16]
        write(path, record)
        expected = "does not record the full design_id"
    elif case == "wrong_upstream":
        path = phases / "CAL.json"
        record = json.loads(path.read_bytes())
        assert "DEV" in record["upstream"]
        record["upstream"]["DEV"] = "0" * 64
        redigest("CAL", record)
        write(path, record)
        expected = "and lineage"
    elif case in ("n_hold_above_cap", "n_hold_below_min"):
        bounds = cfg["modes"]["full"]["null_plan"]
        path = phases / "NULL_PLAN.json"
        record = json.loads(path.read_bytes())
        if case == "n_hold_above_cap":
            record["derived"]["n_hold"] = bounds["n_cap"] + 1
        else:
            record["derived"]["n_hold"] = bounds["n_min"] - 1
        redigest("NULL_PLAN", record)
        write(path, record)
        expected = "violates the frozen NULL_PLAN state rules"
    elif case == "hold_without_null_plan":
        assert (phases / "HOLD.json").is_file()
        (phases / "NULL_PLAN.json").unlink()
        expected = "NULL_PLAN has no record while a later record"
    else:
        record = json.loads((phases / "HOLD.json").read_bytes())
        npz = module._partition_path(
            staging, did, record["upstream"], record["partitions"][0]["key"]
        ).with_suffix(".npz")
        sidecar = npz.with_suffix(".json")
        assert npz.is_file()
        assert sidecar.is_file()
        sidecar_bytes = sidecar.read_bytes()
        if case == "npz_flipped":
            _b1i_flip(npz)
            expected = "sidecar disagrees"
        else:
            npz.unlink()
            expected = "is missing or unreadable"
        assert sidecar.read_bytes() == sidecar_bytes

    staged_before = _tree(staging)
    calls = []

    def trap(name):
        def raising(*args, **kwargs):
            calls.append(name)
            raise AssertionError(name + " reached on poisoned resume")

        return raising

    for name in ("start_invocation", "run_phases", "export_payloads"):
        monkeypatch.setattr(module, name, trap(name))

    code = module.main([*argv, "--resume"])
    captured = capsys.readouterr()
    assert code == 2, captured.err
    assert expected in captured.err
    assert calls == []
    assert _tree(staging) == staged_before
    assert _tree(out) == published


@pytest.mark.parametrize("axis", ["cpu", "wall"])
def test_b4r_cli_blocks_at_publication_budget_boundary(tmp_path, monkeypatch, capsys, axis):
    import json
    from pathlib import Path

    module = pio()
    cfg = _b4f_smoke_cfg()
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    did = module.design_id(module.design_descriptor(cfg, "smoke"))
    cpu_cap = cfg["envelope"]["cpu_hours_max"] * 3600
    wall_cap = cfg["envelope"]["wall_seconds_per_invocation"]
    edited = _edited(cfg, ("envelope", "wall_seconds_per_invocation"), wall_cap + 1)
    assert module.design_id(module.design_descriptor(edited, "smoke")) != did

    state = {"cpu": 10.0, "wall": 1000.0}
    _b1m_clock(monkeypatch, state)

    ref_out, ref_logs = tmp_path / "ref_out", tmp_path / "ref_logs"
    ref_argv = ["--config", str(config), "--mode", "smoke", "--jobs", "1",
                "--output-dir", str(ref_out), "--log-dir", str(ref_logs)]
    assert module.main(ref_argv) == 0
    capsys.readouterr()

    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", "smoke", "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    staging = logs / "staging" / did[:16]
    tmp = out.parent / f".{out.name}.publish-{did[:16]}.tmp"
    final_path = staging / "phases" / "FINAL.json"
    expected_status = {"status": "BLOCKED_RESOURCE", "design_id": did,
                       "last_complete_phase": "ALT", "missing_partitions": []}
    charge = cpu_cap if axis == "cpu" else 8.0

    real_export = module.export_payloads
    calls = []

    def exhausting_export(*args, **kwargs):
        calls.append(args)
        result = real_export(*args, **kwargs)
        if axis == "cpu":
            state["cpu"] = 10.0 + cpu_cap
        else:
            state["wall"] = 1000.0 + wall_cap
            state["cpu"] = 18.0
        return result

    monkeypatch.setattr(module, "export_payloads", exhausting_export)
    assert module.main(argv) == 2
    err = capsys.readouterr().err
    assert len(calls) == 1
    assert did[:16] in err
    assert "is exhausted" in err
    assert not out.exists()
    assert not final_path.exists()
    assert tmp.is_dir()
    csvs = sorted(tmp.rglob("*.csv"))
    assert csvs
    for path in csvs:
        assert path.read_bytes() == (ref_out / path.relative_to(tmp)).read_bytes()
    assert json.loads((staging / "status.json").read_text()) == expected_status
    resources = json.loads((staging / "resources.json").read_text())
    assert resources["design_id"] == did
    ledger = resources["cpu_seconds"]
    assert isinstance(ledger, dict)
    assert list(ledger.values()) == [charge]
    (initial_token,) = ledger
    before = _b4f_durable(staging)

    monkeypatch.setattr(module, "export_payloads", real_export)

    def no_rescore(*args, **kwargs):
        raise AssertionError("resume must not rescore")

    monkeypatch.setattr(module, "score_path_batch", no_rescore)

    if axis == "cpu":
        def no_export(*args, **kwargs):
            raise AssertionError("exhausted CPU must not export")

        monkeypatch.setattr(module, "export_payloads", no_export)
        assert module.main([*argv, "--resume"]) == 2
        err = capsys.readouterr().err
        assert did[:16] in err
        assert "is exhausted" in err
        assert not out.exists()
        assert not final_path.exists()
        assert json.loads((staging / "status.json").read_text()) == expected_status
    else:
        assert module.main([*argv, "--resume"]) == 0
        capsys.readouterr()

        def scientific(root):
            return {k: v for k, v in _tree(root).items() if Path(k).name != "telemetry.json"}

        assert scientific(out) == scientific(ref_out)
        manifest = json.loads((out / "manifest.json").read_text())
        final = json.loads(final_path.read_text())
        assert final["design_id"] == manifest["design_id"] == did
        assert final["realization_id"] == manifest["realization_id"]

    after = _b4f_durable(staging)
    assert {k: after.get(k) for k in before} == before
    resumed = json.loads((staging / "resources.json").read_text())
    assert resumed["design_id"] == did
    resumed_ledger = resumed["cpu_seconds"]
    assert len(resumed_ledger) == 2
    assert resumed_ledger[initial_token] == charge
    assert sum(resumed_ledger.values()) == charge


@pytest.mark.parametrize(
    "case", ["descriptor", "authority", "plan", "jobs", "go_digest"]
)
def test_b4s_phase_driver_refuses_bad_admission_before_effects(
    tmp_path, monkeypatch, case
):
    module = pio()
    mode = "full"
    cfg, did = _authorized(tmp_path, monkeypatch, _b4o_authorized_cfg(mode), mode)
    desc = module.design_descriptor(cfg, mode)
    grant = module.authorize(mode, cfg, desc, 1)
    plan = module.partition_plan(desc)
    staging = module.open_staging(tmp_path / "logs", desc, False)
    context = module.start_invocation(staging, grant, plan, "b4s-initial")
    context["jobs"] = 1
    if case == "descriptor":
        cfg = _edited(cfg, ("seed",), cfg["seed"] + 1)
        error = module.StagingMismatch
        pattern = "does not match the current design descriptor"
    elif case == "authority":
        authority = dict(grant)
        authority["stage"] = "pilot"
        context["authority"] = authority
        error = module.AuthorizationRefused
        pattern = "authority does not match the staged design and mode"
    elif case == "plan":
        assert plan["ALT"]
        poisoned = dict(plan)
        poisoned["ALT"] = []
        context["plan"] = poisoned
        error = module.StagingMismatch
        pattern = "partition plan does not match the staged design"
    elif case == "jobs":
        context["jobs"] = cfg["envelope"]["jobs_max"] + 1
        error = module.AuthorizationRefused
        pattern = "jobs outside"
    else:
        assert case == "go_digest"
        cfg = _edited(
            cfg, ("authorization", "go_reference", "sha256"), "0" * 64
        )
        error = module.AuthorizationRefused
        pattern = "does not match its recorded SHA-256"
    before = _tree(tmp_path)

    def _phase_reached(*args, **kwargs):
        raise AssertionError("phase controller reached before admission")

    with monkeypatch.context() as mp:
        _no_side_effects(mp)
        for name in (
            "setup_phase",
            "dev_phase",
            "cal_phase",
            "null_plan_phase",
            "hold_phase",
            "alt_phase",
        ):
            mp.setattr(module, name, _phase_reached)
        with pytest.raises(error, match=pattern):
            module.run_phases(cfg, mode, context)
    assert _tree(tmp_path) == before
    assert not [
        path
        for path in tmp_path.rglob("*")
        if path.is_dir() and path.name in ("phases", "partitions")
    ]


def test_no_real_data_access(tmp_path, monkeypatch, capsys):
    import ast
    import builtins
    import io
    import os
    import re
    from pathlib import Path, PurePath

    module = pio()
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    target = "jepadrift.data_loader"

    def reaches(name):
        return name == target or name.startswith(target + ".")

    def dotted(node):
        names = []
        while isinstance(node, ast.Attribute):
            names.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name):
            return None
        names.append(node.id)
        return ".".join(reversed(names))

    date = re.compile(
        r"(?<![0-9])([0-9]{4})-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])(?![0-9])"
    )
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if reaches(alias.name):
                    violations.append(("import", node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if reaches(base):
                violations.append(("from", node.lineno, base))
            for alias in node.names:
                qualified = f"{base}.{alias.name}" if base else alias.name
                if reaches(qualified):
                    violations.append(("from", node.lineno, qualified))
        elif isinstance(node, ast.Attribute):
            name = dotted(node)
            if name is not None and reaches(name):
                violations.append(("attribute", node.lineno, name))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if reaches(node.value):
                violations.append(("module string", node.lineno, node.value))
            if "data" in re.split(r"[\\/]", node.value):
                violations.append(("data path", node.lineno, node.value))
            for match in date.finditer(node.value):
                if int(match.group(1)) >= 2020:
                    violations.append(("date", node.lineno, match.group(0)))
    assert violations == []

    cfg, did = _authorized(
        tmp_path, monkeypatch, _b4o_authorized_cfg("full"), "full"
    )
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = [
        "--config", str(config), "--mode", "full", "--jobs", "1",
        "--output-dir", str(out), "--log-dir", str(logs),
    ]
    real_builtin_open = builtins.open
    real_io_open = io.open
    real_os_open = os.open
    real_scandir = os.scandir
    real_listdir = os.listdir
    blocked = []

    def guard(kind, path):
        if path is None or isinstance(path, int):
            return
        if not isinstance(path, (str, bytes, os.PathLike)):
            return
        text = os.fsdecode(path)
        for candidate in (
            os.path.normpath(os.path.abspath(text)),
            os.path.realpath(text),
        ):
            if "data" in PurePath(candidate).parts:
                blocked.append((kind, text, candidate))
                raise AssertionError(f"real data access blocked: {kind} {candidate}")

    def trap(kind, real, key):
        def wrapper(*args, **kwargs):
            guard(kind, args[0] if args else kwargs.get(key))
            return real(*args, **kwargs)

        return wrapper

    monkeypatch.chdir(tmp_path)
    with monkeypatch.context() as patch:
        patch.setattr(
            builtins, "open", trap("builtins.open", real_builtin_open, "file")
        )
        patch.setattr(io, "open", trap("io.open", real_io_open, "file"))
        patch.setattr(os, "open", trap("os.open", real_os_open, "path"))
        patch.setattr(os, "scandir", trap("os.scandir", real_scandir, "path"))
        patch.setattr(os, "listdir", trap("os.listdir", real_listdir, "path"))
        try:
            code = module.main(argv)
        except SystemExit as exc:
            code = exc.code
    captured = capsys.readouterr()
    diagnostics = (code, captured.out, captured.err, blocked)
    assert blocked == [], diagnostics
    assert type(code) is int and code == 0, diagnostics
    assert (out / "manifest.json").exists(), diagnostics
    final = logs / "staging" / did[:16] / "phases" / "FINAL.json"
    assert final.exists(), diagnostics


def test_b4t_design_and_config_ast_exclude_prior_outputs():
    import ast
    import re
    from pathlib import Path

    module = pio()
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    wanted = (
        "design_descriptor",
        "load_config",
        "seed_plan",
        "_check_cfg",
        "_environment",
    )
    selected = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in wanted
    ]
    assert sorted(node.name for node in selected) == sorted(wanted)
    functions = {node.name: node for node in selected}
    forbidden = {
        "_staged_design",
        "_claimed_design",
        "open_staging",
        "_planned_progress",
        "finalize",
        "finalize_planned",
        "export_payloads",
    }
    prior = {"results", "logs"}
    violations = []
    opens = []
    hashes = []
    for function in selected:
        for node in ast.walk(function):
            if isinstance(node, ast.Name) and node.id in forbidden:
                violations.append((function.name, node.lineno, node.id))
            elif isinstance(node, ast.Attribute) and node.attr in forbidden:
                violations.append((function.name, node.lineno, node.attr))
            elif isinstance(node, ast.alias) and (
                forbidden & set(node.name.split(".")) or node.asname in forbidden
            ):
                violations.append((function.name, function.lineno, node.name))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if prior & set(re.split(r"[\\/]", node.value)):
                    violations.append((function.name, node.lineno, node.value))
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called = node.func.id
                else:
                    called = getattr(node.func, "attr", None)
                if called == "open":
                    opens.append((function.name, node))
                elif called == "file_sha256":
                    hashes.append((function.name, node))
    assert violations == []
    stray = [(name, node.lineno) for name, node in opens if name != "load_config"]
    assert stray == []
    loader = functions["load_config"]
    params = loader.args.posonlyargs + loader.args.args
    config_opens = [node for name, node in opens if name == "load_config"]
    assert params and len(config_opens) == 1
    call = config_opens[0]
    assert isinstance(call.func, ast.Name) and call.func.id == "open"
    assert len(call.args) == 1 and isinstance(call.args[0], ast.Name)
    assert call.args[0].id == params[0].arg
    assert [
        (keyword.arg, getattr(keyword.value, "value", None))
        for keyword in call.keywords
    ] == [("encoding", "utf-8")]
    handles = [
        item.optional_vars.id
        for node in ast.walk(loader)
        if isinstance(node, ast.With)
        for item in node.items
        if item.context_expr is call and isinstance(item.optional_vars, ast.Name)
    ]
    loads = [
        node
        for node in ast.walk(loader)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "safe_load"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "yaml"
    ]
    assert len(handles) == 1 and len(loads) == 1
    assert [getattr(arg, "id", None) for arg in loads[0].args] == handles
    code_hashes = [node for name, node in hashes if name == "design_descriptor"]
    assert code_hashes
    for node in code_hashes:
        assert isinstance(node.func, ast.Attribute)
        assert isinstance(node.func.value, ast.Name) and node.func.value.id == "pdb"
        assert node.args and isinstance(node.args[0], ast.BinOp)
        assert isinstance(node.args[0].op, ast.Div)
        assert isinstance(node.args[0].left, ast.Name)
        assert node.args[0].left.id == "CODE_ROOT"
    assert any(
        isinstance(node, ast.Name) and node.id == "CODE_FILES"
        for node in ast.walk(functions["design_descriptor"])
    )


def test_b4u_nonoracle_dependency_ast():
    import ast
    from pathlib import Path

    tree = ast.parse(Path(pio().__file__).read_text(encoding="utf-8"))
    names = (
        "online_masks",
        "nonoracle_masks",
        "nonoracle_scan",
        "calibrate_nonoracle",
        "_scan_inputs",
        "_scan_result",
        "_calibrate_ge",
        "masked_scan",
        "best_sets",
    )
    forbidden = {
        "meta",
        "delta",
        "tau_star",
        "family",
        "oracle",
        "q_true",
        "sigma0",
        "mu0",
        "c_true",
        "var0",
        "C0",
        "oracle_masks",
        "oracle_scan",
        "population_drift",
        "path_scores",
        "null_returns",
        "direction_information",
        "projection_diagnostics",
    }
    defs = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert [name for name in names if name not in defs] == []
    for name in names:
        hits = []
        for node in ast.walk(defs[name]):
            if isinstance(node, ast.arg):
                found = node.arg
            elif isinstance(node, ast.Name):
                found = node.id
            elif isinstance(node, ast.Attribute):
                found = node.attr
            elif (
                isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                found = node.slice.value
            else:
                continue
            if found in forbidden:
                hits.append((type(node).__name__, found, node.lineno))
        assert hits == [], (name, hits)
    args = defs["online_masks"].args
    assert [arg.arg for arg in args.posonlyargs + args.args] == [
        "Y",
        "window",
        "cost",
        "order",
    ]
    assert args.vararg is None
    assert args.kwonlyargs == []
    assert args.kwarg is None


def test_b4u_alt_monitor_ignores_poisoned_simulator_metadata(
    tmp_path, monkeypatch, capsys
):
    module = pio()
    cfg = _b4o_authorized_cfg("full")
    cfg["scope"]["policies"] = list(module.P_CONF)
    cfg, did = _authorized(tmp_path, monkeypatch, cfg, "full")
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    fields = (
        "meta",
        "family",
        "delta",
        "tau_star",
        "q",
        "mu0",
        "sigma0",
        "c",
        "var0",
        "C0",
    )
    trapped = (
        "projection_diagnostics",
        "direction_information",
        "oracle_scan",
        "oracle_masks",
    )
    real_alt = module.alt_phase
    real_info = module.direction_information
    real_score = module.score_path_batch
    real_scan = module.nonoracle_scan
    pending = []
    batches = []
    leaks = []
    scans = []

    def trap(name):
        def fail(*args, **kwargs):
            raise AssertionError(f"nonoracle_scan reached {name}")

        return fail

    def scan(Y, bundle, h=None):
        scans.append(1)
        with monkeypatch.context() as inner:
            for name in trapped:
                inner.setattr(module, name, trap(name))
            return real_scan(Y, bundle, h=h)

    def info(desc, frame, fit, setup, application, key):
        value = real_info(desc, frame, fit, setup, application, key)
        if key[0] == "meta" and key[5] == "ALT":
            assert isinstance(value, dict)
            pending.append(value)
        return value

    def score(
        desc, frame, fit, application, requests, *, jobs=1, deadline=None
    ):
        scores = real_score(
            desc,
            frame,
            fit,
            application,
            requests,
            jobs=jobs,
            deadline=deadline,
        )
        alt = sum(1 for key, _ in requests if key[5] == "ALT")
        batches.append((len(pending), alt))
        for row in pending:
            for field in fields:
                row[field] = _B2cPoison()
        pending.clear()
        return scores

    def wrapped_alt(cfg, mode, context):
        with monkeypatch.context() as inner:
            inner.setattr(module, "direction_information", info)
            inner.setattr(module, "score_path_batch", score)
            inner.setattr(module, "nonoracle_scan", scan)
            try:
                return real_alt(cfg, mode, context)
            finally:
                leaks.append(len(pending))

    def run(name):
        out = tmp_path / name / "results"
        logs = tmp_path / name / "logs"
        code = module.main(
            [
                "--config",
                str(config),
                "--mode",
                "full",
                "--jobs",
                "1",
                "--output-dir",
                str(out),
                "--log-dir",
                str(logs),
            ]
        )
        captured = capsys.readouterr()
        assert type(code) is int and code == 0, captured.err
        stage = logs / "staging" / did[:16]
        durable = _b4f_durable(stage)
        assert "phases/ALT.json" in durable
        tree = _tree(out)
        return durable, {
            key: value
            for key, value in tree.items()
            if key != "telemetry.json"
        }

    reference = run("reference")
    with monkeypatch.context() as outer:
        outer.setattr(module, "alt_phase", wrapped_alt)
        work = run("work")
    assert work[0] == reference[0]
    assert work[1] == reference[1]
    assert scans
    assert leaks and set(leaks) == {0}
    assert batches and all(rows == alt for rows, alt in batches)
    total = sum(rows for rows, _ in batches)
    assert total == 2 * cfg["modes"]["full"]["sizes"]["ALT"]


def test_b4v_cli_full_publishes_committed_confirmatory_claims_once(tmp_path, monkeypatch, capsys):
    import json

    import pandas as pd

    module = pio()
    cfg, did = _authorized(tmp_path, monkeypatch, _b4o_authorized_cfg("full"), "full")
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", "full", "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    staging = logs / "staging" / did[:16]
    alt_path = staging / "phases" / "ALT.json"
    final_path = staging / "phases" / "FINAL.json"
    original = module.confirmatory_from_staging
    results, alts = [], []

    def witness(cfg_arg, mode_arg, context):
        assert alt_path.exists()
        assert not final_path.exists()
        assert not out.exists()
        alts.append(json.loads(alt_path.read_text(encoding="utf-8")))
        result = original(cfg_arg, mode_arg, context)
        results.append(result)
        return result

    monkeypatch.setattr(module, "confirmatory_from_staging", witness)
    code = module.main(argv)
    captured = capsys.readouterr()
    assert code == 0, (captured.out, captured.err)
    assert len(results) == 1
    assert len(alts) == 1
    result = results[0]

    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

    claims = result["claims"]
    assert set(claims) == {"H1", "H2", "H3"}
    assert result["design_id"] == did
    assert result["alt_phase_digest"] == alts[0]["phase_digest"]
    keys = result["bootstrap_keys"]
    assert set(keys) == {"F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"}
    planned_keys = module.seed_plan(cfg, "full")["keys"]
    for family in ("F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"):
        expected_key = ["boot", "FULL", *cfg["phi"]["setup"], "RESIDUAL", family]
        assert keys[family] == expected_key
        assert tuple(expected_key) in planned_keys
    planned = {
        "H1": keys["F2_STRUCTURED_RESIDUAL"],
        "H2": keys["F_HEAD_RESIDUAL"],
        "H3": keys["F2_STRUCTURED_RESIDUAL"],
    }
    assert "geometry" in claims["H2"] and "control" in claims["H2"]
    for name in ("H1", "H3"):
        assert "geometry" not in claims[name] and "control" not in claims[name]

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    payloads = manifest["payloads"]
    published = {
        name for name, entry in payloads.items()
        if entry["status"] == "PUBLISHED"
    }
    assert published == {
        "calibration.csv", "selections.csv", "trials_summary.csv",
        "aggregates.csv", "issues.csv",
    }
    assert any(
        entry["status"] == "LOCAL_HASHED_ONLY"
        for name, entry in payloads.items()
        if name not in published
    )

    aggregates_path = out / "aggregates.csv"
    sha = pdb.file_sha256(aggregates_path)
    assert payloads["aggregates.csv"]["sha256"] == sha
    assert manifest["realization_descriptor"]["payloads"]["aggregates.csv"] == sha

    text_columns = [
        "record_kind", "hypothesis", "family", "design_id", "setup_id",
        "application", "status", "alt_phase_digest", "bootstrap_key",
        "inference_json",
    ]
    frame = pd.read_csv(
        aggregates_path,
        float_precision="round_trip",
        dtype={column: str for column in text_columns},
        keep_default_na=False,
    )
    assert set(text_columns) <= set(frame.columns)
    assert "DESCRIPTIVE_V_RMST" in set(frame["record_kind"])
    confirmatory = frame[frame["record_kind"] == "CONFIRMATORY"]
    assert len(confirmatory) == 3
    assert len(frame) > 3
    assert set(confirmatory["hypothesis"]) == {"H1", "H2", "H3"}
    for row in confirmatory.to_dict("records"):
        name = row["hypothesis"]
        claim = claims[name]
        assert row["family"] == claim["family"]
        assert row["design_id"] == did
        assert row["setup_id"] == result["setup_id"]
        assert row["application"] == "RESIDUAL"
        assert row["status"] == claim["status"]
        assert row["alt_phase_digest"] == result["alt_phase_digest"]
        assert row["bootstrap_key"] == canonical(planned[name])
        assert row["inference_json"] == canonical(claim)

    snapshot = _tree(out)

    def trap(*args, **kwargs):
        raise AssertionError("confirmatory_from_staging called on resume")

    monkeypatch.setattr(module, "confirmatory_from_staging", trap)
    code = module.main(argv + ["--resume"])
    captured = capsys.readouterr()
    assert code == 0, (captured.out, captured.err)
    assert _tree(out) == snapshot
    assert len(results) == 1


def test_b4w_cli_publishes_descriptive_contrasts_with_shared_bootstrap(
    tmp_path, monkeypatch, capsys
):
    import collections
    import json

    import pandas as pd

    families = ("F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL")
    contrast_kind = "DESCRIPTIVE_CONTRAST"
    original_seed_sequence = np.random.SeedSequence

    def canon_text(value):
        text = pdb.canon(value)
        return text.decode("utf-8") if isinstance(text, bytes) else text

    for mode in ("full", "pilot"):
        root = tmp_path / mode
        root.mkdir()
        with monkeypatch.context() as mp:
            module = pio()
            cfg, did = _authorized(root, mp, _b4o_authorized_cfg(mode), mode)
            config = _b4a_yaml(root / "config.yaml", cfg)
            out, logs = root / "out", root / "logs"
            argv = [
                "--config", str(config), "--mode", mode, "--jobs", "1",
                "--output-dir", str(out), "--log-dir", str(logs),
            ]
            stage = logs / "staging" / did[:16]
            alt_path = stage / "phases" / "ALT.json"
            final_path = stage / "phases" / "FINAL.json"
            real_descriptive_contrasts = module.descriptive_contrasts
            calls = []
            rows_by_family = {}
            alt_snapshots = []
            seed_prefix = [
                32,
                cfg["seed"],
                pdb.label_code(mode.upper()),
                pdb.label_code("boot"),
            ]
            boot_entropies = []

            def witness(mode_arg, H, family, cells, hold_first, alt_first, boot_indices):
                assert str(mode_arg).lower() == mode
                assert alt_path.exists()
                assert not final_path.exists()
                assert family in families
                assert family not in rows_by_family
                calls.append(family)
                alt_snapshots.append(alt_path.read_bytes())
                result = real_descriptive_contrasts(
                    mode_arg, H, family, cells, hold_first, alt_first, boot_indices
                )
                rows_by_family[family] = list(result)
                return result

            def seed_sequence_spy(entropy=None, *args, **kwargs):
                if (
                    isinstance(entropy, (list, tuple))
                    and len(entropy) >= len(seed_prefix)
                    and all(
                        isinstance(x, (int, np.integer)) and not isinstance(x, bool)
                        for x in entropy
                    )
                    and [int(x) for x in entropy[: len(seed_prefix)]] == seed_prefix
                ):
                    boot_entropies.append(tuple(int(x) for x in entropy))
                return original_seed_sequence(entropy, *args, **kwargs)

            mp.setattr(module, "descriptive_contrasts", witness)
            mp.setattr(np.random, "SeedSequence", seed_sequence_spy)
            rc = module.main(argv)
            captured = capsys.readouterr()
            assert rc == 0, captured.out + captured.err
            assert len(calls) == 2
            assert sorted(calls) == sorted(families)
            assert len(set(alt_snapshots)) == 1
            alt_digest = json.loads(alt_snapshots[0])["phase_digest"]

            planned_keys = {
                family: ["boot", mode.upper(), *cfg["phi"]["setup"], "RESIDUAL", family]
                for family in families
            }
            expected_entropies = collections.Counter(
                tuple(
                    int(v)
                    for v in [
                        32,
                        cfg["seed"],
                        pdb.label_code(key[1]),
                        pdb.label_code(key[0]),
                        *[pdb.label_code(x) if isinstance(x, str) else x for x in key[2:]],
                    ]
                )
                for key in planned_keys.values()
            )
            assert len(expected_entropies) == len(families)
            assert collections.Counter(boot_entropies) == expected_entropies

            oracle_ids = {}
            for family in families:
                rows = rows_by_family[family]
                assert rows
                assert all(row["family"] == family for row in rows)
                separate = [row for row in rows if row["fpr_status"] == "ORACLE_SEPARATE"]
                assert len(separate) == 1
                oracle_ids[family] = separate[0]["candidate_calibration_id"]
            assert len(set(oracle_ids.values())) == len(families)
            for family in families:
                used = {row["candidate_calibration_id"] for row in rows_by_family[family]}
                used |= {row["reference_calibration_id"] for row in rows_by_family[family]}
                for other in families:
                    if other != family:
                        assert oracle_ids[other] not in used

            expected_status = "DESCRIPTIVE_NOMINAL" if mode == "full" else "PILOT_ONLY"
            expected_rows = {}
            for family in families:
                for row in rows_by_family[family]:
                    ident = (
                        row["family"],
                        row["candidate_calibration_id"],
                        row["reference_calibration_id"],
                    )
                    assert ident not in expected_rows
                    assert row["status"] == expected_status
                    expected_rows[ident] = row

            frame = pd.read_csv(
                out / "aggregates.csv",
                float_precision="round_trip",
                dtype=str,
                keep_default_na=False,
            )
            contrasts = frame[frame["record_kind"] == contrast_kind]
            seen = collections.Counter()
            for record in contrasts.to_dict("records"):
                inference = json.loads(record["inference_json"])
                ident = (
                    inference["family"],
                    inference["candidate_calibration_id"],
                    inference["reference_calibration_id"],
                )
                assert ident in expected_rows, ident
                seen[ident] += 1
                real_row = expected_rows[ident]
                assert record["inference_json"] == canon_text(real_row)
                assert record["bootstrap_key"] == canon_text(planned_keys[ident[0]])
                assert record["design_id"] == did
                assert record["application"] == "RESIDUAL"
                assert record["status"] == real_row["status"]
                assert record["status"] == expected_status
                assert record["alt_phase_digest"] == alt_digest
                assert record["hypothesis"] == ""
            assert seen == collections.Counter(dict.fromkeys(expected_rows, 1))

            descriptive = frame[frame["record_kind"] == "DESCRIPTIVE_V_RMST"]
            assert not descriptive.empty
            confirmatory = frame[frame["record_kind"] == "CONFIRMATORY"]
            if mode == "full":
                assert sorted(confirmatory["hypothesis"]) == ["H1", "H2", "H3"]
            else:
                assert confirmatory.empty
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            payloads = manifest["payloads"]
            published = {
                name for name, entry in payloads.items()
                if entry["status"] == "PUBLISHED"
            }
            assert published == {
                "calibration.csv", "selections.csv", "trials_summary.csv",
                "aggregates.csv", "issues.csv",
            }


def test_b4x_cli_fitted_oracle_reports_surrogate_and_joint_separately(tmp_path, monkeypatch, capsys):
    import hashlib
    import json

    import pandas

    module = pio()
    mode = "full"
    cfg, did = _authorized(tmp_path, monkeypatch, _b4o_authorized_cfg(mode), mode)
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", mode, "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    stage = logs / "staging" / did[:16]
    phases = stage / "phases"
    rc = module.main(argv)
    captured = capsys.readouterr()
    assert rc == 0, captured.err + captured.out

    setup_doc = json.loads((phases / "SETUP.json").read_text())
    alt_doc = json.loads((phases / "ALT.json").read_text())
    cal_doc = json.loads((phases / "CAL.json").read_text())
    desc = module.design_descriptor(cfg, mode)
    setup = cfg["phi"]["setup"]
    assert setup == ["FITTED_LW_GAUSSIAN", 24, 0]
    universe = setup_doc["derived"]["setups"][pdb.canon(setup)]["applications"]["RESIDUAL"]["universe"]
    frame_key = ["frame", "FULL", 24]
    fit_key = ["fit", "FULL", *setup]
    frame = module._setup_cache(module._verify_partition(stage, did, {}, frame_key)[2], frame_key)
    fit = module._setup_cache(module._verify_partition(stage, did, {}, fit_key)[2], fit_key)

    ids = {c: str for c in ("design_id", "setup_id", "application", "policy", "policy_id",
                            "calibration_id", "family", "alt_payload_sha256", "info_basis",
                            "metric_basis", "qualification", "rule", "maxima_sha256")}
    selections_path = out / "selections.csv"
    selections = pandas.read_csv(selections_path, float_precision="round_trip", dtype=ids)
    calibration = pandas.read_csv(out / "calibration.csv", float_precision="round_trip", dtype=ids)
    label_fields = (
        (selections, ["application", "policy", "policy_id", "family", "info_basis", "metric_basis"]),
        (calibration, ["policy_id", "family", "qualification", "rule"]),
    )
    for csv_frame, cols in label_fields:
        for label in ("KL_OPTIMAL", "JOINT_OPTIMUM"):
            hits = csv_frame[cols].apply(lambda col: col.str.contains(label, regex=False, na=False))
            assert not hits.any().any()
    assert set(selections["info_basis"]) == {"ORACLE_DIAGONAL_SURROGATE"}
    assert set(selections["metric_basis"]) == {"ANALYTIC_PROXY"}
    oracle = selections[selections["policy"] == "ORACLE_INFO_MIX"]
    assert len(oracle) == 2
    assert sorted(oracle["family"]) == ["F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL"]

    params = desc["science"]["parameters"]
    gamma_M = float(params["gamma_M"])
    H = int(params["H"])
    thresholds = cal_doc["derived"]["thresholds"]
    trials = alt_doc["derived"]["trials"]
    partitions = alt_doc["partitions"]
    setup_id = setup_doc["derived"]["setups"][pdb.canon(setup)]["applications"]["RESIDUAL"]["setup_id"]
    distinct = False
    for _, row in oracle.iterrows():
        family = row["family"]
        cid = row["calibration_id"]
        assert row["design_id"] == did
        assert row["application"] == "RESIDUAL"
        assert row["setup_id"] == setup_id
        assert float(row["gamma_M"]) == gamma_M

        match = calibration
        for col in ("design_id", "setup_id", "policy_id", "calibration_id", "family"):
            match = match[match[col] == row[col]]
        assert len(match) == 1
        cal_row = match.iloc[0]
        threshold = thresholds[cid]
        assert threshold["setup_id"] == row["setup_id"]
        assert threshold["policy_id"] == row["policy_id"]
        assert threshold["family"] == family
        assert threshold["qualification"] == "NON_DEPLOYABLE_ORACLE_CALIBRATION"
        assert cal_row["qualification"] == "NON_DEPLOYABLE_ORACLE_CALIBRATION"
        assert float(cal_row["h"]) == float(threshold["h"])

        alt_key = ["ALT", *setup, "RESIDUAL", family]
        sha, n, arrays = module._verify_partition(stage, did, alt_doc["upstream"], alt_key)
        records = [p for p in partitions if p["key"] == alt_key]
        assert records == [{"key": alt_key, "sha256": sha, "n_rows": n}]
        trial = trials[pdb.canon(alt_key)]
        assert trial["setup_id"] == row["setup_id"]
        assert trial["family"] == family
        assert cid in trial["calibration_ids"]
        assert row["alt_payload_sha256"] == sha
        assert n == int(row["n_alt"])
        mask = np.asarray(arrays["mask_" + cid])
        assert mask.shape == (n, H)
        deltas = np.stack([
            np.asarray(module.direction_information(
                desc, frame, fit, setup, "RESIDUAL",
                ("meta", "FULL", *setup, "ALT", family, i))["delta"])
            for i in range(n)
        ])
        projection = module.projection_diagnostics(frame, fit, universe, deltas, setup[0])
        expected = _b3j_expect(mask, projection["q"], projection["beta"],
                               projection["C0"], row["gamma_M"], _b3j_kl_chol)
        i_sur = float(np.mean(expected["I_surrogate"]))
        i_joint = float(np.mean(expected["I_joint"]))
        v_sur = float(np.mean(expected["vbar_surrogate"]))
        v_joint = float(np.mean(expected["vbar_joint"]))
        assert float(row["I_mean"]) == pytest.approx(i_sur, rel=1e-12)
        assert float(row["I_joint_mean"]) == pytest.approx(i_joint, rel=1e-12)
        assert float(row["V_bar"]) == pytest.approx(v_sur, rel=1e-12)
        assert float(row["V_joint_bar"]) == pytest.approx(v_joint, rel=1e-12)
        if abs(float(row["I_mean"]) - float(row["I_joint_mean"])) > 1e-10:
            distinct = True
    assert distinct

    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["design_id"] == did
    sha = hashlib.sha256(selections_path.read_bytes()).hexdigest()
    assert manifest["payloads"]["selections.csv"] == {"sha256": sha, "status": "PUBLISHED"}


def test_b4y_cli_keeps_spectral_subsets_and_unrunnable_statuses(tmp_path, capsys):
    import json

    import pandas as pd

    module = pio()
    mode = "smoke"
    cfg = _b4f_smoke_cfg()
    cfg["scope"]["setups"] = [["EXACT", 32, 0], ["EXACT", 239, 0], ["FITTED_LW_GAUSSIAN", 32, 0]]
    cfg["scope"]["applications"] = ["RESIDUAL", "MARKET"]
    cfg["scope"]["families"] = ["F2_STRUCTURED_RESIDUAL", "F3_MARKET"]
    cfg["scope"]["policies"] = ["FULL_K", "FIXED_EIGENMEAN_PREFIX", "CPV90", "RESIDUAL_CPV90"]
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", mode, "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    stage = logs / "staging" / did[:16]
    phases = stage / "phases"

    rc = module.main(argv)
    captured = capsys.readouterr()
    assert rc == 0, captured.out + captured.err

    def load(name):
        return json.loads((phases / f"{name}.json").read_text())

    setup_rec, dev_rec, cal_rec, hold_rec, alt_rec = (load(n) for n in ("SETUP", "DEV", "CAL", "HOLD", "ALT"))
    sel = pd.read_csv(
        out / "selections.csv",
        float_precision="round_trip",
        dtype={c: str for c in ("setup_id", "policy_id", "calibration_id", "design_id")},
    )
    assert not any("KAISER" in str(p) for p in sel["policy"])
    labels = cfg["scope"]["policies"]
    unrunnable = {"OUTSIDE_UNIVERSE", "UNSUPPORTED"}
    H = desc["science"]["parameters"]["H"]
    thresholds = cal_rec["derived"]["thresholds"]
    families = {"RESIDUAL": "F2_STRUCTURED_RESIDUAL", "MARKET": "F3_MARKET"}

    for setup in cfg["scope"]["setups"]:
        key = ["frame", "SMOKE", setup[1]] if setup[0] == "EXACT" else ["fit", "SMOKE", *setup]
        _, _, arrays = module._verify_partition(stage, did, {}, key)
        fit = module._setup_cache(arrays, key)
        for app in cfg["scope"]["applications"]:
            family = families[app]
            ref = _b2b_reference(fit["lam"], app)
            assert set(ref) == {"eligible", "baselines"}
            assert set(ref["baselines"]) == set(labels)
            exp = ref["baselines"]
            eligible = ref["eligible"]

            meta = setup_rec["derived"]["setups"][pdb.canon(setup)]["applications"][app]
            sid = meta["setup_id"]
            assert meta["universe"] == eligible
            assert meta["baselines"] == exp

            if setup[0] == "EXACT":
                prefix = exp["FIXED_EIGENMEAN_PREFIX"]
                assert prefix["status"] == "RUNNABLE"
                if app == "RESIDUAL":
                    assert prefix["pcs"] == list(range(2, 10))
                    assert exp["RESIDUAL_CPV90"]["status"] == "RUNNABLE"
                    assert exp["RESIDUAL_CPV90"]["pcs"] == list(range(2, 17))
                    assert exp["CPV90"]["status"] == "OUTSIDE_UNIVERSE"
                    assert exp["CPV90"]["pcs"] is None
                    assert 1 not in eligible
                else:
                    assert prefix["pcs"] == list(range(1, 8))
                    assert exp["RESIDUAL_CPV90"]["status"] == "UNSUPPORTED"
                    if setup[1] == 32:
                        assert exp["CPV90"]["status"] == "RUNNABLE"
                        assert exp["CPV90"]["pcs"] == list(range(1, 18))
                        assert exp["CPV90"]["k90"] == 17
                    else:
                        assert exp["CPV90"]["status"] == "OUTSIDE_UNIVERSE"
                        assert exp["CPV90"]["k90"] > 20

            policies = dev_rec["derived"]["setups"][pdb.canon(setup)][app]["policies"]["PRIMARY"]
            assert set(policies) == set(labels)
            expected = {}
            for lab in labels:
                row = policies[lab]
                assert row["status"] == exp[lab]["status"]
                if exp[lab]["status"] in unrunnable:
                    assert row["policy_id"] is None
                    assert row["subset"] is None
                else:
                    assert isinstance(row["policy_id"], str)
                    assert [int(p) for p in row["subset"]] == exp[lab]["pcs"]
                    assert set(exp[lab]["pcs"]) <= set(eligible)
                    expected[row["policy_id"]] = (lab, exp[lab]["pcs"])
            assert "FULL_K" in {lab for lab, _ in expected.values()}

            mine = [(cid, row) for cid, row in thresholds.items() if row["setup_id"] == sid]
            assert all(row["policy_id"] is not None for _, row in mine)
            assert sorted(row["policy_id"] for _, row in mine) == sorted(expected)
            assert all("family" not in row and "h" in row for _, row in mine)
            cid_by_policy = {row["policy_id"]: cid for cid, row in mine}
            assert len(cid_by_policy) == len(mine) == len(expected)

            cells = (
                (hold_rec, ["HOLD_NULL", *setup, app]),
                (alt_rec, ["ALT", *setup, app, family]),
            )
            for rec, cell_key in cells:
                _, n, arrs = module._verify_partition(stage, did, rec["upstream"], cell_key)
                for pid, (lab, pcs) in expected.items():
                    word = sum(1 << eligible.index(p) for p in pcs)
                    mask = arrs["mask_" + cid_by_policy[pid]]
                    assert mask.dtype == np.uint32
                    assert mask.shape == (n, H)
                    assert np.all(mask == np.uint32(word)), (cell_key, lab)

            rows = sel[sel["setup_id"] == sid]
            assert sorted(rows["policy"]) == sorted(lab for lab, _ in expected.values())
            for _, r in rows.iterrows():
                lab, pcs = expected[r["policy_id"]]
                assert r["policy"] == lab
                assert r["calibration_id"] == cid_by_policy[r["policy_id"]]
                assert r["family"] == family
                assert r["design_id"] == did
                assert r["d_mean"] == float(len(pcs))


def test_b4z_cli_keeps_fallback_prior_and_gamma_cells_separate(
        tmp_path, monkeypatch, capsys):
    import json
    import pandas as pd

    module = pio()
    mode = "full"
    base = _b4o_authorized_cfg(mode)
    base["dev"]["s2_grid"] = [1]
    cfg, did = _authorized(tmp_path, monkeypatch, base, mode)
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", mode, "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    stage = logs / "staging" / did[:16]
    phases = stage / "phases"
    setup = cfg["phi"]["setup"]
    params = cfg["parameters"]
    H, alpha, K = (params[k] for k in ("H", "alpha", "K"))
    prior = 2.0 * math.log(H / alpha) / (H * K)

    roles, cards = [], {}
    score_requests = module._score_requests
    masked_scan = module.masked_scan

    def score_spy(desc, frame, fit, application, requests, context):
        roles.append(requests[0][0][5])
        return score_requests(desc, frame, fit, application, requests,
                              context)

    def scan_spy(Y, M, s2, h=None):
        assert s2 == prior
        if roles and roles[-1] in ("CAL_NULL", "HOLD_NULL", "ALT"):
            first = np.asarray(M)[:, 0, :].sum(axis=1)
            cards.setdefault(roles[-1], set()).update(
                int(v) for v in first)
        return masked_scan(Y, M, s2, h=h)

    monkeypatch.setattr(module, "_score_requests", score_spy)
    monkeypatch.setattr(module, "masked_scan", scan_spy)
    rc = module.main(argv)
    captured = capsys.readouterr()
    assert rc == 0, captured.out + captured.err
    for role in ("CAL_NULL", "HOLD_NULL", "ALT"):
        assert {1, K} <= cards.get(role, set()), (role, cards)

    dev_rec, cal_rec, hold_rec, alt_rec = (
        json.loads((phases / f"{name}.json").read_text())
        for name in ("DEV", "CAL", "HOLD", "ALT"))
    dev = dev_rec["derived"]["setups"][pdb.canon(setup)]["RESIDUAL"]
    sid = dev["setup_id"]
    primary = dev["policies"]["PRIMARY"]
    gamma = dev["policies"]["GAMMA_M"]
    s2_dev = dev["policies"]["S2_DEV"]
    thresholds = cal_rec["derived"]["thresholds"]
    calibration_ids = {(row["policy_id"], row.get("family")): cid
                       for cid, row in thresholds.items()
                       if row["setup_id"] == sid}
    online_labels = list(module.P_CONF[:2])
    assert dev["s2_status"] == "S2_DEV_EQUALS_COMMON"
    assert s2_dev == {label: primary[label] for label in module.P_CONF}
    assert set(gamma) == set(online_labels)
    online_ids = []
    for label in online_labels:
        nominal, sensitivity = primary[label], gamma[label]
        nominal_cid = calibration_ids[(nominal["policy_id"], None)]
        sensitivity_cid = calibration_ids[(sensitivity["policy_id"], None)]
        assert sensitivity["policy_id"] != nominal["policy_id"]
        assert sensitivity["policy_rule_id"] != nominal["policy_rule_id"]
        assert sensitivity_cid != nominal_cid
        assert sensitivity["s2"] == nominal["s2"] == prior
        online_ids += [nominal_cid, sensitivity_cid]
    full_pid = primary["FULL_K"]["policy_id"]
    full_cids = [cid for (pid, _), cid in calibration_ids.items()
                 if pid == full_pid]
    assert full_cids == [calibration_ids[(full_pid, None)]]
    families = cfg["scope"]["families"]
    oracle_pid = primary["ORACLE_INFO_MIX"]["policy_id"]
    assert "ORACLE_INFO_MIX" not in gamma
    oracle_cids = {family: calibration_ids[(oracle_pid, family)]
                   for family in families}
    assert len(families) == 2
    assert len(set(oracle_cids.values())) == 2
    assert not set(oracle_cids.values()) & {full_cids[0], *online_ids}

    def masks(arrays, cids):
        found = {cid: arrays["mask_" + cid] for cid in cids}
        n = found[cids[0]].shape[0]
        for mask in found.values():
            assert mask.dtype == np.uint32 and mask.shape == (n, H)
        return found

    hold = module._verify_partition(stage, did, hold_rec["upstream"],
                                    ["HOLD_NULL", *setup, "RESIDUAL"])[2]
    partitions = [(hold, list(families))]
    for family in families:
        alt = module._verify_partition(
            stage, did, alt_rec["upstream"],
            ["ALT", *setup, "RESIDUAL", family])[2]
        partitions.append((alt, [family]))
    full_word = (1 << K) - 1
    for index, (arrays, oracle_families) in enumerate(partitions):
        oracle_ids = [oracle_cids[family] for family in oracle_families]
        found = masks(arrays, [full_cids[0], *online_ids, *oracle_ids])
        for cid in online_ids:
            assert np.all(found[cid][:, 0] == 1)
        assert np.all(found[full_cids[0]] == full_word)
        for cid in oracle_ids:
            assert np.all(found[cid] == found[cid][:, :1])
        if index:
            assert any(np.any(found[cid] != 1)
                       for cid in [*online_ids, *oracle_ids])

    selections = pd.read_csv(
        out / "selections.csv", float_precision="round_trip",
        dtype={"policy_id": str, "calibration_id": str})
    gamma_pids = {row["policy_id"] for row in gamma.values()}
    sensitivity_budget = H / alpha
    assert sensitivity_budget == 120
    assert sensitivity_budget != params["gamma_M"] == 504
    budgets = selections["gamma_M"]
    is_gamma = selections["policy_id"].isin(gamma_pids)
    sensitive = selections.loc[budgets == sensitivity_budget, "policy_id"]
    assert set(sensitive) == gamma_pids
    assert (budgets[is_gamma] == sensitivity_budget).all()
    assert (budgets[~is_gamma] == params["gamma_M"]).all()
    for row in selections.to_dict("records"):
        threshold = thresholds[row["calibration_id"]]
        assert threshold["policy_id"] == row["policy_id"]
        if row["policy_id"] == oracle_pid:
            assert threshold["family"] == row["family"]


def test_b4aa_cli_routes_population_drifts_and_preserves_fitted_injections(
    tmp_path, monkeypatch, capsys
):
    import json
    from collections import Counter

    module = pio()
    mode = "smoke"
    cfg = _b4f_smoke_cfg()
    exact = ["EXACT", 32, 0]
    fit0 = ["FITTED_LW_GAUSSIAN", 32, 0]
    fit1 = ["FITTED_LW_GAUSSIAN", 32, 1]
    cfg["scope"]["setups"] = [exact, fit0, fit1]
    cfg["scope"]["applications"] = ["RESIDUAL", "MARKET"]
    cfg["scope"]["families"] = [
        "F0_ISOTROPIC_RESIDUAL", "F1_TAIL_RESIDUAL",
        "F2_STRUCTURED_RESIDUAL", "F_HEAD_RESIDUAL", "F3_MARKET",
    ]
    cfg["scope"]["policies"] = ["FULL_K", "ORACLE_INFO_MIX", "ORACLE_PREFIX_MIX"]
    cfg["modes"]["smoke"]["sizes"]["ALT"] = 8
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out, logs = tmp_path / "out", tmp_path / "logs"
    argv = ["--config", str(config), "--mode", mode, "--jobs", "1",
            "--output-dir", str(out), "--log-dir", str(logs)]
    stage = logs / "staging" / did[:16]
    phases = stage / "phases"

    setups = [exact, fit0, fit1]
    applications = ["RESIDUAL", "MARKET"]
    families = list(cfg["scope"]["families"])
    home = {
        family: "MARKET" if family == "F3_MARKET" else "RESIDUAL"
        for family in families
    }
    supports = {
        "F0_ISOTROPIC_RESIDUAL": list(range(2, 22)),
        "F1_TAIL_RESIDUAL": [18, 19, 20, 21],
        "F2_STRUCTURED_RESIDUAL": [3, 9, 17, 21],
        "F_HEAD_RESIDUAL": [2, 3, 4, 5],
        "F3_MARKET": [1],
    }

    original = module._score_requests
    seen = Counter()

    def wrapped(desc, frame, fit, application, requests, context):
        for path_key, delta in requests:
            if len(path_key) == 7 and path_key[5] == "ALT":
                seen[(tuple(path_key), application, delta.tobytes())] += 1
        return original(desc, frame, fit, application, requests, context)

    monkeypatch.setattr(module, "_score_requests", wrapped)
    rc = module.main(argv)
    captured = capsys.readouterr()
    assert rc == 0, captured.out + captured.err
    assert seen

    def record(name):
        return json.loads((phases / f"{name}.json").read_text())

    setup_doc = record("SETUP")
    dev = record("DEV")
    cal = record("CAL")
    alt = record("ALT")

    for setup in setups:
        apps = setup_doc["derived"]["setups"][pdb.canon(setup)]["applications"]
        assert apps["RESIDUAL"]["universe"] == list(range(2, 22))
        assert apps["MARKET"]["universe"] == list(range(1, 21))

    parts = {tuple(part["key"]): part for part in alt["partitions"]}
    assert len(parts) == len(alt["partitions"])
    assert set(parts) == {
        ("ALT", *setup, home[family], family)
        for setup, family in itertools.product(setups, families)
    }
    assert {key[4] for key in parts} == set(applications)
    for part in parts.values():
        assert part["n_rows"] == 8
        assert isinstance(part["sha256"], str) and part["sha256"]

    i_star = desc["science"]["parameters"]["I_star"]
    assert math.isfinite(i_star) and i_star > 0

    def frozen(key):
        return module._setup_cache(
            module._verify_partition(stage, did, {}, key)[2], key)

    frame = frozen(["frame", "SMOKE", 32])
    fitted0 = frozen(["fit", "SMOKE", *fit0])
    fitted1 = frozen(["fit", "SMOKE", *fit1])
    local_fits = {
        tuple(exact): frame,
        tuple(fit0): fitted0,
        tuple(fit1): fitted1,
    }

    regenerated = Counter()
    head_signs = set()
    for key in sorted(parts, key=repr):
        setup = list(key[1:4])
        app, family = key[4], key[5]
        for i in range(parts[key]["n_rows"]):
            meta = ("meta", "SMOKE", *setup, "ALT", family, i)
            info = module.direction_information(
                desc, frame, local_fits[tuple(setup)], setup, app, meta)
            assert info["status"] == "SUPPORTED"
            assert info["family"] == family
            assert info["support"] == supports[family]
            delta = info["delta"]
            white = (delta @ frame["V"]) / np.sqrt(frame["lam"])
            nonzero = [int(j) + 1 for j in np.flatnonzero(np.abs(white) > 1e-12)]
            assert nonzero == supports[family]
            assert 0.5 * float(white @ white) == pytest.approx(i_star, rel=1e-12)
            if setup == exact and family == "F_HEAD_RESIDUAL":
                q = np.asarray(info["q"], dtype=float)
                assert q.shape == (20,)
                assert np.allclose(q[:4], i_star / 4, rtol=0, atol=1e-14)
                assert np.allclose(q[4:], 0.0, rtol=0, atol=1e-14)
                head_signs.add(tuple(np.sign(white[1:5]).tolist()))
            path_key = ("path", "SMOKE", *setup, "ALT", i)
            regenerated[(path_key, app, delta.tobytes())] += 1
    assert len(head_signs) >= 2
    assert regenerated == seen

    head_meta = ("meta", "SMOKE", *fit0, "ALT", "F_HEAD_RESIDUAL", 0)
    under0 = module.direction_information(
        desc, frame, fitted0, fit0, "RESIDUAL", head_meta)
    under1 = module.direction_information(
        desc, frame, fitted1, fit0, "RESIDUAL", head_meta)
    assert under0["delta"].dtype == under1["delta"].dtype
    assert under0["delta"].shape == under1["delta"].shape
    assert under0["delta"].tobytes() == under1["delta"].tobytes()

    def beta(fit, delta):
        return delta @ fit["V"][:, 1:21] / np.sqrt(fit["lam"][1:21])

    beta0 = beta(fitted0, under0["delta"])
    beta1 = beta(fitted1, under1["delta"])
    assert np.max(np.abs(beta0 - beta1)) > 1e-12

    primary = dev["derived"]["setups"][pdb.canon(exact)]["RESIDUAL"]["policies"]["PRIMARY"]
    setup_id = setup_doc["derived"]["setups"][pdb.canon(exact)]["applications"]["RESIDUAL"]["setup_id"]
    policy_ids = [
        primary[label]["policy_id"]
        for label in ("ORACLE_INFO_MIX", "ORACLE_PREFIX_MIX")
    ]
    assert len(set(policy_ids)) == 2
    arrays = module._verify_partition(
        stage, did, alt["upstream"],
        ["ALT", *exact, "RESIDUAL", "F_HEAD_RESIDUAL"])[2]
    for policy_id in policy_ids:
        matches = [
            (cid, row) for cid, row in cal["derived"]["thresholds"].items()
            if row["setup_id"] == setup_id
            and row["policy_id"] == policy_id
            and row.get("family") == "F_HEAD_RESIDUAL"
        ]
        assert len(matches) == 1
        cid, row = matches[0]
        assert row["qualification"] == "NON_DEPLOYABLE_ORACLE_CALIBRATION"
        assert math.isfinite(float(row["h"]))
        mask = np.asarray(arrays["mask_" + cid])
        assert mask.dtype == np.uint32
        assert mask.shape == (8, desc["science"]["parameters"]["H"])
        assert mask.size > 0
        assert np.all(mask == 15)


def test_b4ab_cli_rejects_missing_science_config_without_staging(tmp_path, monkeypatch, capsys):
    module = pio()
    cfg = _b4f_smoke_cfg()
    del cfg["head"]
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out = tmp_path / "out"
    logs = tmp_path / "logs"

    def trap(*args, **kwargs):
        pytest.fail("configuration refusal must precede staging and population")

    monkeypatch.setattr(module, "open_staging", trap)
    monkeypatch.setattr(module, "population_frame", trap)
    rc = module.main(["--config", str(config), "--mode", "smoke", "--jobs", "1",
                      "--output-dir", str(out), "--log-dir", str(logs)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "invalid configuration" in captured.err
    assert str(config) in captured.err
    assert captured.out == ""
    assert not out.exists()
    assert not logs.exists()


@pytest.mark.parametrize(
    ("case", "diagnostic"),
    [("nonpositive", "positive nonincreasing lam"),
     ("gap", "relative LW eigengap")],
)
def test_b4ab_cli_refuses_bad_lw_spectrum_without_reroll_or_publish(
        tmp_path, monkeypatch, capsys, case, diagnostic):
    module = pio()
    cfg = _b4f_smoke_cfg()
    cfg["scope"]["setups"] = [["FITTED_LW_GAUSSIAN", 24, 0]]
    config = _b4a_yaml(tmp_path / "config.yaml", cfg)
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    desc = module.design_descriptor(cfg, "smoke")
    did = module.design_id(desc)

    lam = np.arange(24.0, 0.0, -1.0)
    if case == "nonpositive":
        lam[-1] = 0.0
    else:
        lam[1] = lam[0]

    null_keys = []
    real_null_returns = module.null_returns

    def spy_null_returns(desc_, frame_, key_):
        null_keys.append(tuple(key_))
        return real_null_returns(desc_, frame_, key_)

    fit_calls = []

    def fake_fit_basis(X_fit):
        fit_calls.append(X_fit)
        return {"eigvec": np.eye(24), "eigval": lam}

    def trap(*args, **kwargs):
        pytest.fail("refused fit must not reach phase development or export")

    monkeypatch.setattr(module, "null_returns", spy_null_returns)
    monkeypatch.setattr(pdb, "fit_basis", fake_fit_basis)
    monkeypatch.setattr(module, "dev_phase", trap)
    monkeypatch.setattr(module, "export_payloads", trap)

    rc = module.main(["--config", str(config), "--mode", "smoke", "--jobs", "1",
                      "--output-dir", str(out), "--log-dir", str(logs)])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert diagnostic in captured.err
    assert null_keys == [("fit", "SMOKE", "FITTED_LW_GAUSSIAN", 24, 0)]
    assert len(fit_calls) == 1
    assert not out.exists()

    stage = logs / "staging" / did[:16]
    frame_key = ["frame", "SMOKE", 24]
    fit_key = ["fit", "SMOKE", "FITTED_LW_GAUSSIAN", 24, 0]
    module._verify_partition(stage, did, {}, frame_key)
    stem = module._partition_path(stage, did, {}, fit_key)
    assert not stem.with_suffix(".json").exists()
    assert not stem.with_suffix(".npz").exists()
    assert not list((stage / "phases").glob("*.json"))


def _r3_allocation(primary_cal_null, hold_block_rows):
    return {"primary_cal_null": primary_cal_null, "hold_block_rows": hold_block_rows,
            "fpr_equivalence": "TANGO_ASYMPTOTIC", "fit_scope": "FIT_CONDITIONAL"}


def _r3_full_cfg():
    import copy

    cfg = copy.deepcopy(_design_cfg())
    run = cfg["modes"]["full"]
    run["sizes"].update(CAL_NULL=2000, HOLD_NULL=2000, ALT=2000, DEV_NULL=1000, DEV_ALT=200)
    run["null_plan"].update(n_min=2000, n_plan=2000, n_cap=20000)
    run["allocation"] = _r3_allocation(10000, 1000)
    cfg["scope"]["applications"] = ["RESIDUAL", "MARKET"]
    cfg["scope"]["families"].append("F3_MARKET")
    return cfg


def test_full_r3_cal_allocation_plan_declares_group_sizes_and_seed_boundaries():
    import copy

    module = pio()
    cfg = _r3_full_cfg()
    desc = module.design_descriptor(cfg, "full")
    assert desc["allocation"] == cfg["modes"]["full"]["allocation"]
    plain = module.design_descriptor(_design_cfg(), "full")
    assert "allocation" not in plain and all(len(key) == 6 for key in module.partition_plan(plain)["CAL"])

    campaign, primary = "FULL", ["FITTED_LW_GAUSSIAN", 239, 0]
    groups = {g: ["CAL_NULL", campaign, *primary, "RESIDUAL", g] for g in ("P_CONF", "OTHER")}
    ordinary = (["CAL_NULL", campaign, "EXACT", 32, 0, "RESIDUAL"],
                ["CAL_NULL", campaign, "EXACT", 32, 0, "MARKET"],
                ["CAL_NULL", campaign, *primary, "MARKET"])
    plan = module.partition_plan(desc)
    assert {pdb.canon(key) for key in plan["CAL"]} == {pdb.canon(key) for key in (*groups.values(), *ordinary)}
    assert {pdb.canon(key) for key in plan["CAL"]}.isdisjoint(pdb.canon(key) for key in plan["NULL_PLAN"] + plan["HOLD"])
    assert module._expected_rows(desc, "CAL", groups["P_CONF"], {}) == 10000
    assert module._expected_rows(desc, "CAL", groups["OTHER"], {}) == 2000
    assert [module._expected_rows(desc, "CAL", key, {}) for key in ordinary] == [2000, 2000, 2000]
    for bad in (["CAL_NULL", campaign, "EXACT", 32, 0, "RESIDUAL", "P_CONF"],
                ["CAL_NULL", campaign, *primary, "MARKET", "OTHER"],
                ["CAL_NULL", campaign, *primary, "RESIDUAL"],
                ["CAL_NULL", campaign, *primary, "RESIDUAL", "P_CONFX"]):
        with pytest.raises(ValueError):
            module._expected_rows(desc, "CAL", bad, {})

    keys = module.seed_plan(cfg, "full")["keys"]

    def path_ids(arm, n, role):
        return {k[6] for k in keys if k[:6] == ("path", campaign, arm, n, 0, role)}

    assert path_ids("FITTED_LW_GAUSSIAN", 239, "CAL_NULL") == set(range(10000))
    assert path_ids("EXACT", 32, "CAL_NULL") == set(range(2000))
    assert path_ids("FITTED_LW_GAUSSIAN", 239, "HOLD_NULL") == set(range(20000))
    for role in ("CAL_NULL", "HOLD_NULL"):
        for family in cfg["scope"]["families"]:
            prefix = ("meta", campaign, *primary, role, family)
            assert {k[7] for k in keys if k[:7] == prefix} == set(range(2000))
            module.direction_draws(desc, (*prefix, 1999))
            with pytest.raises(ValueError):
                module.direction_draws(desc, (*prefix, 2000))
    assert all(p not in ("P_CONF", "OTHER") for k in keys for p in k if isinstance(p, str))

    arms = ("EXACT", "FITTED_LW_GAUSSIAN", "FITTED_LW_T7")
    module._planned_null_key(desc, ("path", campaign, "FITTED_LW_GAUSSIAN", 239, 0, "CAL_NULL", 9999), arms)
    module._planned_null_key(desc, ("path", campaign, "EXACT", 32, 0, "CAL_NULL", 1999), arms)
    for rejected in (("path", campaign, "FITTED_LW_GAUSSIAN", 239, 0, "CAL_NULL", 10000),
                     ("path", campaign, "EXACT", 32, 0, "CAL_NULL", 2000)):
        with pytest.raises(ValueError):
            module._planned_null_key(desc, rejected, arms)

    for override in ({"primary_cal_null": True}, {"primary_cal_null": 2000}, {"hold_block_rows": True},
                     {"fpr_equivalence": "NO_SUCH_EQUIVALENCE"}):
        broken = copy.deepcopy(cfg)
        broken["modes"]["full"]["allocation"] = {**cfg["modes"]["full"]["allocation"], **override}
        with pytest.raises(ValueError):
            module.design_descriptor(broken, "full")


def _r3_smoke_cfg():
    import copy

    cfg = copy.deepcopy(_b4f_smoke_cfg())
    cfg["phi"]["setup"] = ["EXACT", 24, 0]
    cfg["scope"]["policies"] = [*pio().P_CONF, "FIXED_DEV_PREFIX", "ORACLE_INFO_MIX"]
    cfg["modes"]["smoke"]["null_plan"].update(n_min=3, n_plan=3, n_cap=7)
    cfg["modes"]["smoke"]["allocation"] = _r3_allocation(39, 2)
    return cfg


def test_full_r3_cal_smoke_stages_primary_long_group_and_reloads_without_rescoring(tmp_path):
    module = pio()
    cfg = _r3_smoke_cfg()
    mode = "smoke"
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    plan = module.partition_plan(desc)
    alpha = cfg["parameters"]["alpha"]
    assert pdb.predictive_rank(19, alpha) == 0 and pdb.predictive_rank(39, alpha) == 1
    assert [key[-1] for key in plan["CAL"]] == ["OTHER", "P_CONF"]
    assert all(key[:6] == ["CAL_NULL", "SMOKE", "EXACT", 24, 0, "RESIDUAL"] for key in plan["CAL"])
    other, p_conf = plan["CAL"]

    work = tmp_path / "cal"
    work.mkdir()
    staging = module.open_staging(work, desc, False)
    context = module.start_invocation(staging, module.authorize(mode, cfg, desc, 1), plan, "first")
    real_calibrate = module.calibrate_nonoracle
    observed = {}

    def recording(scores, bundle, alpha):
        if bundle["s2"] == module.common_prior(desc):
            observed[bundle["label"]] = scores.copy()
        return real_calibrate(scores, bundle, alpha)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module, "calibrate_nonoracle", recording)
        setup_record = module.setup_phase(cfg, mode, context)
        dev_record = module.dev_phase(cfg, mode, context)
        cal_record = module.cal_phase(cfg, mode, context)
    expected = np.stack([module.exact_scores(desc, ("path", "SMOKE", "EXACT", 24, 0, "CAL_NULL", i))[:, 1:21]
                         for i in range(39)])
    assert np.array_equal(observed["FULL_K"], expected)
    assert np.array_equal(observed["FIXED_DEV_PREFIX"], expected[:19])

    upstream = {"SETUP": setup_record["phase_digest"], "DEV": dev_record["phase_digest"]}
    _, rows_p, arrays_p = module._verify_partition(staging, did, upstream, p_conf)
    _, rows_o, arrays_o = module._verify_partition(staging, did, upstream, other)
    assert (rows_p, rows_o) == (39, 19) and arrays_p and arrays_o
    assert all(a.shape == (39,) and np.isfinite(a).all() for a in arrays_p.values())
    assert all(a.shape == (19,) and np.isfinite(a).all() for a in arrays_o.values())
    thresholds = cal_record["derived"]["thresholds"]
    assert {row["n_cal"] for row in thresholds.values()} == {19, 39}
    assert {row["maxima_sha256"] for row in thresholds.values() if row["n_cal"] == 39} == {pdb.array_sha256(a) for a in arrays_p.values()}
    assert {row["maxima_sha256"] for row in thresholds.values() if row["n_cal"] == 19} == {pdb.array_sha256(a) for a in arrays_o.values()}
    assert all(row["r"] == 1 and row["alarms"] <= 1 for row in thresholds.values() if row["n_cal"] == 39)
    assert all(row["r"] == 0 and row["alarms"] == 0 for row in thresholds.values() if row["n_cal"] == 19)

    policies = dev_record["derived"]["setups"][pdb.canon(["EXACT", 24, 0])]["RESIDUAL"]["policies"]
    long_cells = [(row["policy_id"], row.get("family")) for row in thresholds.values() if row["n_cal"] == 39]
    short_cells = {(row["policy_id"], row.get("family")) for row in thresholds.values() if row["n_cal"] == 19}
    primary_ids = {(policies["PRIMARY"][label]["policy_id"], None) for label in module.P_CONF}
    assert len(long_cells) == 3 and set(long_cells) == primary_ids and primary_ids.isdisjoint(short_cells)
    assert (policies["PRIMARY"]["FIXED_DEV_PREFIX"]["policy_id"], None) in short_cells
    assert (policies["PRIMARY"]["ORACLE_INFO_MIX"]["policy_id"], "F2_STRUCTURED_RESIDUAL") in short_cells
    sensitivity_ids = {(row["policy_id"], None) for variant in ("GAMMA_M", "S2_DEV")
                       for row in policies[variant].values()} - primary_ids
    assert sensitivity_ids and sensitivity_ids <= short_cells

    def trapped(*args, **kwargs):
        raise AssertionError("the reopened CAL resume must not rescore paths or rederive ranks")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module, "score_path_batch", trapped)
        mp.setattr(pdb, "rank_threshold", trapped)
        reopened = module.open_staging(work, desc, True)
        resume = module.start_invocation(reopened, module.authorize(mode, cfg, desc, 1), plan, "resume")
        assert module.cal_phase(cfg, mode, resume)["phase_digest"] == cal_record["phase_digest"]

        (reopened / "phases" / "CAL.json").unlink()
        truncated = _npz_bytes(**{name: values[:-1] for name, values in arrays_p.items()})
        _put_partition(reopened, did, upstream, p_conf, truncated, 38)
        assert module._verify_partition(reopened, did, upstream, p_conf)[1] == 38
        with pytest.raises(module.PartitionMismatch, match="38.*39"):
            module.cal_phase(cfg, mode, resume)


def _r3_hold_spans(desc, n_hold):
    limit = desc["allocation"]["hold_block_rows"]
    ordinary = desc["sizes"]["HOLD_NULL"]
    return [(s, min(s + limit, ordinary if s < ordinary else n_hold))
            for s in [*range(0, ordinary, limit), *range(ordinary, n_hold, limit)]]


def _r3_hold_campaign(tmp_path, name, jobs=1, score=None):
    module = pio()
    cfg = _r3_smoke_cfg()
    mode = "smoke"
    cfg["modes"][mode]["null_plan"]["n_cap"] = 15
    desc = module.design_descriptor(cfg, mode)
    did = module.design_id(desc)
    plan = module.partition_plan(desc)
    root = tmp_path / name
    root.mkdir()
    staging = module.open_staging(root, desc, False)
    context = module.start_invocation(staging, module.authorize(mode, cfg, desc, jobs), plan, name)
    context["jobs"] = jobs
    with pytest.MonkeyPatch.context() as mp:
        if score is not None:
            mp.setattr(module, "score_path_batch", score)
        records = [getattr(module, f"{phase}_phase")(cfg, mode, context)
                   for phase in ("setup", "dev", "cal", "null_plan", "hold")]
    return module, cfg, desc, did, staging, plan, records


def test_full_r3_hold_plan_witness_and_block_allocation():
    module = pio()
    desc = module.design_descriptor(_r3_full_cfg(), "full")
    limit, ordinary = desc["allocation"]["hold_block_rows"], desc["sizes"]["HOLD_NULL"]
    primary = desc["science"]["phi"]["setup"]
    shared = np.zeros((2000, 3), dtype=bool)
    shared[:40] = True
    shared[40:50, 0] = True
    shared[50:60, 1:] = True
    wide = np.zeros((2000, 3), dtype=bool)
    wide[:40] = True
    wide[40:90, 0] = True
    wide[90:140, 1:] = True
    plans = [module._null_plan_derived(desc, "0" * 64, list(module.P_CONF), alarm)
             for alarm in (np.zeros((2000, 3), dtype=bool), shared, wide)]
    assert [(p["status"], p["n_hold"]) for p in plans] == [
        ("PLAN_ADEQUATE", 2000), ("PLAN_ADEQUATE", 3184), ("PLAN_CAPPED_EXPECT_INCONCLUSIVE", 20000)]
    key = ["HOLD_NULL", *primary, "RESIDUAL"]
    for derived, n_hold in zip(plans, (2000, 3184, 20000)):
        records = {"NULL_PLAN": {"derived": derived}}
        for start, stop in _r3_hold_spans(desc, n_hold):
            assert module._expected_rows(desc, "HOLD", [*key, start], records) == stop - start
        for bad in (n_hold, (n_hold - ordinary) // limit * limit + limit + ordinary, "0"):
            with pytest.raises(ValueError):
                module._expected_rows(desc, "HOLD", [*key, bad], records)
    for setup in (["EXACT", 32, 0], primary):
        for app in ("RESIDUAL", "MARKET"):
            if [*setup, app] == [*primary, "RESIDUAL"]:
                continue
            cohort = ["HOLD_NULL", *setup, app]
            assert [module._expected_rows(desc, "HOLD", [*cohort, s], records) for s in (0, 1000)] == [1000, 1000]
            with pytest.raises(ValueError):
                module._expected_rows(desc, "HOLD", [*cohort, 2000], records)
    expected = [["HOLD_NULL", *primary, "RESIDUAL", s] for s, _ in _r3_hold_spans(desc, 20000)]
    for setup in (["EXACT", 32, 0], primary):
        for app in ("RESIDUAL", "MARKET"):
            if [*setup, app] != [*primary, "RESIDUAL"]:
                expected += [["HOLD_NULL", *setup, app, s] for s, _ in _r3_hold_spans(desc, ordinary)]
    assert [pdb.canon(k) for k in module.partition_plan(desc)["HOLD"]] == [
        pdb.canon(k) for k in sorted(expected, key=pdb.canon)]


def test_full_r3_hold_smoke_blocks_resume_and_jobs(tmp_path, monkeypatch):
    import json

    module = pio()
    real_score = module.score_path_batch
    mode = "smoke"

    def adequate(*args, **kwargs):
        return 12, "PLAN_ADEQUATE", {"n_req": 12}

    monkeypatch.setattr(module, "plan_holdout", adequate)

    def recorder(batches, jobs=1, state=None):
        def score(d, frame, fit, app, requests, **kwargs):
            if requests and requests[0][0][5] == "HOLD_NULL":
                assert len(requests) <= 2, "HOLD paths must be generated in bounded blocks"
                assert kwargs["jobs"] == jobs
                batches.append([r[0][6] for r in requests])
                if state is not None and len(batches) == 2:
                    state["wall"] = kwargs["deadline"]
            return real_score(d, frame, fit, app, requests, **kwargs)
        return score

    ref_batches = []
    module, cfg, desc, did, ref, plan, (_, _, _, null_ref, hold_ref) = _r3_hold_campaign(
        tmp_path, "reference", 1, recorder(ref_batches))
    spans = _r3_hold_spans(desc, null_ref["derived"]["n_hold"])
    assert null_ref["derived"]["status"] == "PLAN_ADEQUATE"
    assert spans == [(0, 2), (2, 3), (3, 5), (5, 7), (7, 9), (9, 11), (11, 12)]
    assert ref_batches == [list(range(s, e)) for s, e in spans]
    keys = [["HOLD_NULL", *desc["science"]["phi"]["setup"], "RESIDUAL", s] for s, _ in spans]
    work = tmp_path / "work"
    work.mkdir()
    work_batches = []
    state = {"wall": 1000.0, "cpu": 10.0}
    with pytest.MonkeyPatch.context() as mp:
        _b1m_clock(mp, state)
        staging = module.open_staging(work, desc, False)
        context = module.start_invocation(staging, module.authorize(mode, cfg, desc, 1), plan, "work")
        mp.setattr(module, "score_path_batch", recorder(work_batches, state=state))
        setup = module.setup_phase(cfg, mode, context)
        dev = module.dev_phase(cfg, mode, context)
        cal = module.cal_phase(cfg, mode, context)
        null = module.null_plan_phase(cfg, mode, context)
        with pytest.raises(pdb.ResourceBlocked):
            module.hold_phase(cfg, mode, context)
    assert work_batches == [list(range(s, e)) for s, e in spans[:2]]
    upstream = {p: r["phase_digest"] for p, r in
                (("SETUP", setup), ("DEV", dev), ("CAL", cal), ("NULL_PLAN", null))}
    status = json.loads((staging / "status.json").read_text())
    assert status["status"] == "BLOCKED_RESOURCE" and status["last_complete_phase"] == "NULL_PLAN"
    assert {pdb.canon(row["key"]) for row in status["missing_partitions"] if row["phase"] == "HOLD"} == {
        pdb.canon(key) for key in keys[1:]}
    assert not (staging / "phases" / "HOLD.json").exists()
    original = module._partition_path(staging, did, upstream, keys[0]).with_suffix(".npz").read_bytes()
    _, rows0, arrays0 = module._verify_partition(staging, did, upstream, keys[0])
    _put_partition(staging, did, upstream, keys[0],
                   _npz_bytes(**{**arrays0, "path_index": arrays0["path_index"] + 1}), rows0)

    def trap_hold(d, frame, fit, app, requests, **kwargs):
        assert requests[0][0][5] != "HOLD_NULL"
        return real_score(d, frame, fit, app, requests, **kwargs)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module, "score_path_batch", trap_hold)
        staging = module.open_staging(work, desc, True)
        context = module.start_invocation(staging, module.authorize(mode, cfg, desc, 1), plan, "tampered")
        with pytest.raises(module.PartitionMismatch):
            module.hold_phase(cfg, mode, context)
    _put_partition(staging, did, upstream, keys[0], original, rows0)
    resume_batches = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module, "score_path_batch", recorder(resume_batches, jobs=3))
        staging = module.open_staging(work, desc, True)
        context = module.start_invocation(staging, module.authorize(mode, cfg, desc, 3), plan, "resume")
        context["jobs"] = 3
        resumed = module.hold_phase(cfg, mode, context)
    assert resume_batches == [list(range(s, e)) for s, e in spans[1:]]
    assert [pdb.canon(row["key"]) for row in resumed["partitions"]] == sorted(map(pdb.canon, keys))
    assert resumed["derived"]["null_checks"] == hold_ref["derived"]["null_checks"]
    assert _b4f_durable(staging) == _b4f_durable(ref)


def test_full_r3_hold_npz_path_index_and_scans(tmp_path):
    def bounded(desc, frame, fit, app, requests, **kwargs):
        if requests[0][0][5] == "HOLD_NULL":
            assert len(requests) <= 2, "HOLD paths must be generated in bounded blocks"
        return real_score(desc, frame, fit, app, requests, **kwargs)

    real_score = pio().score_path_batch
    module, cfg, desc, did, staging, _, (setup, dev, cal, null, hold) = _r3_hold_campaign(
        tmp_path, "scans", score=bounded)
    setup_id = desc["science"]["phi"]["setup"]
    ordinary, n_hold = desc["sizes"]["HOLD_NULL"], null["derived"]["n_hold"]
    spans = _r3_hold_spans(desc, n_hold)
    keys = [["HOLD_NULL", *setup_id, "RESIDUAL", s] for s, _ in spans]
    upstream = {p: r["phase_digest"] for p, r in
                zip(("SETUP", "DEV", "CAL", "NULL_PLAN"), (setup, dev, cal, null))}
    dev_res = dev["derived"]["setups"][pdb.canon(setup_id)]["RESIDUAL"]
    primary_ids = {dev_res["policies"]["PRIMARY"][label]["policy_id"] for label in module.P_CONF}
    thresholds = cal["derived"]["thresholds"]
    bundles = {(pid, family): bundle for _, pid, family, bundle in module._cal_cells(desc, "RESIDUAL", dev_res)}
    primary_cids = {cid for cid, row in thresholds.items()
                    if row.get("family") is None and row["policy_id"] in primary_ids}
    Y = np.stack([module.exact_scores(desc, ("path", desc["campaign"], *setup_id, "HOLD_NULL", i))[:, 1:21]
                  for i in range(n_hold)])
    frame_key = ["frame", desc["campaign"], setup_id[1]]
    frame = module._setup_cache(module._verify_partition(staging, did, {}, frame_key)[2], frame_key)
    oracle_q = {}
    for family in {row["family"] for row in thresholds.values() if row.get("family") is not None}:
        draws = [("meta", desc["campaign"], *setup_id, "HOLD_NULL", family, i) for i in range(ordinary)]
        oracle_q[family] = np.stack([module.direction_information(desc, frame, frame, setup_id, "RESIDUAL", d)["q"]
                                     for d in draws])
    expected = {}
    for cid, row in thresholds.items():
        family, h = row.get("family"), row["h"]
        rows = Y if cid in primary_cids else Y[:ordinary]
        scan = (module.nonoracle_scan(rows, bundles[(row["policy_id"], family)], h) if family is None
                else module.oracle_scan(rows, oracle_q[family], bundles[(row["policy_id"], family)], h))
        expected[cid] = (scan["first"], scan["mask_bits"])
    parts = []
    n_prefix = len(range(0, ordinary, desc["allocation"]["hold_block_rows"]))
    for (start, stop), key in zip(spans, keys):
        sha, rows, arrays = module._verify_partition(staging, did, upstream, key)
        stem = module._partition_path(staging, did, upstream, key)
        assert rows == stop - start and stem.with_suffix(".npz").stat().st_size < (50 << 20)
        assert sha == next(row["sha256"] for row in hold["partitions"] if row["key"] == key)
        assert arrays["path_index"].dtype.kind == "i" and np.array_equal(arrays["path_index"], np.arange(start, stop))
        cids = set(thresholds) if start < ordinary else primary_cids
        assert set(arrays) == {"path_index"} | {f"{p}{cid}" for cid in cids for p in ("first_", "mask_")}
        parts.append(arrays)
    assert np.array_equal(np.concatenate([a["path_index"] for a in parts]), np.arange(n_hold))
    assert np.array_equal(np.concatenate([a["path_index"] for a in parts[:n_prefix]]), np.arange(ordinary))
    for cid, (first, mask) in expected.items():
        blocks = parts if cid in primary_cids else parts[:n_prefix]
        assert np.array_equal(np.concatenate([a["first_" + cid] for a in blocks]), first)
        assert np.array_equal(np.concatenate([a["mask_" + cid] for a in blocks]), mask)
    checks = hold["derived"]["null_checks"]
    assert set(checks) == set(thresholds)
    for cid, row in checks.items():
        first = expected[cid][0]
        assert row["n"] == first.shape[0] and row["k"] == int((first > 0).sum())
        assert (row["lo"], row["hi"]) == module.cp_bounds(row["k"], row["n"], cfg["null_status"]["tail"])
    oracle_rows = [row for row in checks.values() if row.get("family") is not None]
    assert len(oracle_rows) == 1 and oracle_rows[0]["family"] in oracle_q and oracle_rows[0]["n"] == ordinary


_R3_PATH_PREFIX = ("path", "FULL", "FITTED_LW_GAUSSIAN", 239, 0, "HOLD_NULL")


def _r3_pair_fixture():
    family = "F2_STRUCTURED_RESIDUAL"
    conf = pio().P_CONF
    cells = {
        "INFO": {"policy_label": conf[0], "variant": "PRIMARY", "policy_id": "pid-info",
                 "calibration_family": None, "null_status": "NULL_VALIDATED"},
        "PREFIX": {"policy_label": conf[1], "variant": "PRIMARY", "policy_id": "pid-prefix",
                   "calibration_family": None, "null_status": "NULL_VALIDATED"},
        "FULL_K": {"policy_label": conf[2], "variant": "PRIMARY", "policy_id": "pid-fullk",
                   "calibration_family": None, "null_status": "NULL_VALIDATED"},
        "BASE": {"policy_label": "FIXED_DEV_PREFIX", "variant": "PRIMARY", "policy_id": "pid-base",
                 "calibration_family": None, "null_status": "NULL_VALIDATED"},
        "ORACLE": {"policy_label": "ORACLE_INFO_MIX", "variant": "PRIMARY", "policy_id": "pid-oracle",
                   "calibration_family": family, "null_status": "NULL_VALIDATED"},
    }
    hold = {
        "INFO": np.array([-1, 3, -1, 5, -1, 2, 4]),
        "PREFIX": np.array([-1, 3, -1, -1, 6, 2, -1]),
        "FULL_K": np.array([-1, 3, -1, 2, -1, -1, 7]),
        "BASE": np.array([3, -1, -1]),
        "ORACLE": np.array([1, -1, 2]),
    }
    alt = {
        "INFO": np.array([2, -1, 4, -1, 6]),
        "PREFIX": np.array([3, 5, -1, 2, -1]),
        "FULL_K": np.array([-1, 1, 3, 3, 8]),
        "BASE": np.array([4, 4, -1, 1, 2]),
        "ORACLE": np.array([1, 2, 3, 4, 5]),
    }
    boot = np.array([[0, 1, 2, 3, 4], [4, 0, 1, 2, 3], [0, 0, 2, 2, 4]])
    hold_paths = {c: (_R3_PATH_PREFIX, np.arange(v.size)) for c, v in hold.items()}
    return {"mode": "full", "H": 12, "family": family, "cells": cells, "hold": hold,
            "alt": alt, "boot": boot, "hold_paths": hold_paths}


def test_full_r3_pair_hold_paths_pairs_full_and_mixed_holds():
    fx = _r3_pair_fixture()
    rows = pio().descriptive_contrasts(fx["mode"], fx["H"], fx["family"], fx["cells"], fx["hold"],
                                       fx["alt"], fx["boot"], hold_paths=fx["hold_paths"])
    assert len(rows) == 7
    by_pair = {(r["candidate_calibration_id"], r["reference_calibration_id"]): r for r in rows}
    expected = {
        ("PREFIX", "INFO"): (1, 2, 7, 7, 7),
        ("INFO", "PREFIX"): (2, 1, 7, 7, 7),
        ("FULL_K", "INFO"): (0, 1, 7, 7, 7),
        ("FULL_K", "PREFIX"): (2, 2, 7, 7, 7),
        ("BASE", "INFO"): (1, 1, 3, 3, 7),
        ("BASE", "PREFIX"): (1, 1, 3, 3, 7),
    }
    assert set(by_pair) == set(expected) | {("ORACLE", "INFO")}
    tango = pio().tango_interval
    for (cand, ref), (b, c, n, cn, rn) in expected.items():
        row = by_pair[(cand, ref)]
        assert row["fpr_status"] == "DESCRIPTIVE_NOMINAL"
        assert (row["fpr_b"], row["fpr_c"]) == (b, c)
        assert row["fpr_delta"] == pytest.approx((b - c) / n)
        assert row["fpr_ci"] == pytest.approx(tuple(tango(b, c, n, 0.025)))
        assert all(math.isfinite(x) for x in row["fpr_ci"])
        assert (row["n_hold"], row["candidate_n_hold"], row["reference_n_hold"]) == (n, cn, rn)
        assert row["coverage_claim"] == "NONE_FINITE"
        assert row["fpr_interval_label"] == "TANGO_SCORE_ASYMPTOTIC" and row["tail"] == 0.025
        assert row["n_alt"] == 5 and row["B"] == 3
        assert row["rmst_interval_label"] == "BOOTSTRAP_PERCENTILE_APPROX"
        assert all(math.isfinite(x) for x in row["rmst_ci"])
        assert row["hold_pairing"] == {"path_key_prefix": list(_R3_PATH_PREFIX), "start": 0, "stop": n}
    oracle = by_pair[("ORACLE", "INFO")]
    assert oracle["fpr_status"] == "ORACLE_SEPARATE"
    assert oracle["candidate_fpr"] == pytest.approx(2 / 3)
    assert oracle["reference_fpr"] == pytest.approx(1 / 3)
    assert (oracle["n_hold"], oracle["candidate_n_hold"], oracle["reference_n_hold"]) == (3, 3, 7)
    assert oracle["coverage_claim"] == "NONE_FINITE"
    for absent in ("fpr_ci", "fpr_b", "fpr_c", "fpr_delta", "fpr_interval_label", "tail"):
        assert absent not in oracle
    assert oracle["hold_pairing"] == {"path_key_prefix": list(_R3_PATH_PREFIX), "start": 0, "stop": 3}


@pytest.mark.parametrize(("cell", "prefix", "indices"), [
    ("INFO", _R3_PATH_PREFIX, np.arange(1, 8)),
    ("FULL_K", _R3_PATH_PREFIX, np.array([0, 1, 2, 3, 4, 5, 5])),
    ("BASE", _R3_PATH_PREFIX, np.arange(2, -1, -1)),
    ("ORACLE", _R3_PATH_PREFIX, np.arange(3, dtype=float)),
    ("BASE", _R3_PATH_PREFIX, np.arange(3, dtype=np.uint32)),
    ("BASE", _R3_PATH_PREFIX, np.arange(3).reshape(3, 1)),
    ("BASE", _R3_PATH_PREFIX, [0, 1, 2]),
    ("PREFIX", _R3_PATH_PREFIX, np.arange(5)),
    ("INFO", ("path", "FULL", "FITTED_LW_GAUSSIAN", 32, 0, "HOLD_NULL"), np.arange(7)),
    ("ORACLE", ("path", "PILOT", "FITTED_LW_GAUSSIAN", 239, 0, "HOLD_NULL"), np.arange(3)),
    ("ORACLE", None, None),
], ids=["shifted", "duplicated", "reversed", "float", "unsigned", "two-dimensional",
        "no-array", "misaligned", "equal-sized-foreign-setup", "foreign-campaign", "missing-id"])
def test_full_r3_pair_hold_paths_rejects_tampered_and_foreign_evidence(cell, prefix, indices):
    fx = _r3_pair_fixture()
    if prefix is None:
        del fx["hold_paths"][cell]
    else:
        fx["hold_paths"][cell] = (prefix, indices)
    with pytest.raises(ValueError):
        pio().descriptive_contrasts(fx["mode"], fx["H"], fx["family"], fx["cells"], fx["hold"],
                                    fx["alt"], fx["boot"], hold_paths=fx["hold_paths"])


def test_full_r3_pair_legacy_uniform_holds_retain_legacy_rows():
    fx = _r3_pair_fixture()
    with pytest.raises(ValueError):
        pio().descriptive_contrasts(fx["mode"], fx["H"], fx["family"], fx["cells"], fx["hold"],
                                    fx["alt"], fx["boot"])
    hold3 = {c: v[:3].copy() for c, v in fx["hold"].items()}
    rows = pio().descriptive_contrasts(fx["mode"], fx["H"], fx["family"], fx["cells"], hold3,
                                       fx["alt"], fx["boot"])
    assert len(rows) == 7
    by_pair = {(r["candidate_calibration_id"], r["reference_calibration_id"]): r for r in rows}
    for row in rows:
        assert row["n_hold"] == 3
        for absent in ("hold_pairing", "candidate_n_hold", "reference_n_hold"):
            assert absent not in row
    assert (by_pair[("BASE", "INFO")]["fpr_b"], by_pair[("BASE", "INFO")]["fpr_c"]) == (1, 1)


def test_full_r3_pair_primary_policies_require_the_same_realized_size():
    fx = _r3_pair_fixture()
    fx["hold"]["PREFIX"] = fx["hold"]["PREFIX"][:-1]
    fx["hold_paths"]["PREFIX"] = (_R3_PATH_PREFIX, np.arange(6))
    with pytest.raises(ValueError, match="P_CONF"):
        pio().descriptive_contrasts(fx["mode"], fx["H"], fx["family"], fx["cells"], fx["hold"],
                                    fx["alt"], fx["boot"], hold_paths=fx["hold_paths"])


def _r3_full_campaign(tmp_path, monkeypatch, name, jobs=1, *, cap=13, interrupt=False):
    module = pio()
    cfg = _b4o_authorized_cfg("full")
    run = cfg["modes"]["full"]
    run["sizes"].update(CAL_NULL=19, HOLD_NULL=3, ALT=3)
    run["null_plan"].update(n_min=3, n_plan=3, n_cap=cap)
    run["allocation"] = _r3_allocation(39, 2)
    cfg["scope"]["policies"] = [*module.P_CONF, "FIXED_DEV_PREFIX", "ORACLE_INFO_MIX"]
    cfg, did = _authorized(tmp_path, monkeypatch, cfg, "full")
    desc = module.design_descriptor(cfg, "full")
    plan = module.partition_plan(desc)
    root = tmp_path / name
    root.mkdir()
    staging = module.open_staging(root, desc, False)
    authority = module.authorize("full", cfg, desc, jobs)
    context = module.start_invocation(staging, authority, plan, "integration")
    context.update(jobs=jobs, bootstrap_cache={})
    if interrupt:
        real_score = module.score_path_batch

        def interrupt_block(d, frame, fit, app, requests, **kwargs):
            if requests[0][0][5:] == ("HOLD_NULL", 2):
                raise pdb.ResourceBlocked("fixture interruption in the second HOLD block")
            return real_score(d, frame, fit, app, requests, **kwargs)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(module, "score_path_batch", interrupt_block)
            with pytest.raises(pdb.ResourceBlocked, match="fixture interruption"):
                module.run_phases(cfg, "full", context)
        assert (staging / "phases" / "NULL_PLAN.json").exists()
        assert not (staging / "phases" / "HOLD.json").exists()
        staging = module.open_staging(root, desc, True)
        context = module.start_invocation(staging, authority, plan, "resume")
        context.update(jobs=jobs, bootstrap_cache={})
    records = module.run_phases(cfg, "full", context)
    return module, cfg, desc, did, staging, plan, context, records


def _r3_read_hold_blocks(module, staging, did, records):
    hold = records["HOLD"]
    parts = sorted(hold["partitions"], key=lambda part: part["key"][-1])
    return [(part, module._verify_partition(staging, did, hold["upstream"], part["key"])[2]) for part in parts]


def _r3_collect_first(blocks, cid):
    name = "first_" + cid
    return np.concatenate([arrays[name] for _, arrays in blocks if name in arrays])


def test_full_r3_integration_confirmatory_reads_realized_hold(tmp_path, monkeypatch):
    module = pio()
    monkeypatch.setattr(module, "plan_holdout", lambda *args: (13, "PLAN_ADEQUATE", {"n_req": 13}))
    module, cfg, _, did, staging, _, context, records = _r3_full_campaign(
        tmp_path, monkeypatch, "confirm", cap=15)
    assert records["NULL_PLAN"]["derived"]["n_hold"] == 13
    assert records["NULL_PLAN"]["derived"]["status"] == "PLAN_ADEQUATE"
    result = module.confirmatory_from_staging(cfg, "full", context)
    assert result["design_id"] == did and set(result["claims"]) == {"H1", "H2", "H3"}
    blocks = _r3_read_hold_blocks(module, staging, did, records)
    checks = records["HOLD"]["derived"]["null_checks"]
    for claim in result["claims"].values():
        info, comp = claim["info_calibration_id"], claim["comparator_calibration_id"]
        a, b = (_r3_collect_first(blocks, cid) != -1 for cid in (info, comp))
        assert a.size == b.size == claim["n_hold"] == 13
        assert (claim["fpr_b"], claim["fpr_c"]) == (int((a & ~b).sum()), int((~a & b).sum()))
        assert (claim["info_null_status"], claim["comparator_null_status"]) == (
            checks[info]["status"], checks[comp]["status"])
        assert claim["hold_phase_digest"] == records["HOLD"]["phase_digest"]
        assert claim["coverage_claim"] == "NONE_FINITE"
    assert set(context["bootstrap_cache"]) == {tuple(key) for key in result["bootstrap_keys"].values()}


def test_full_r3_integration_descriptive_rows_pair_realized_hold(tmp_path, monkeypatch):
    import json

    module, cfg, desc, did, staging, _, _, records = _r3_full_campaign(tmp_path, monkeypatch, "descriptive")
    rows = list(module._staged_descriptive_rows(staging, did, records, desc, {}, lambda: None))
    blocks = _r3_read_hold_blocks(module, staging, did, records)
    prefix = ["path", "FULL", *cfg["phi"]["setup"], "HOLD_NULL"]
    denominators = set()
    for row in rows:
        infer = json.loads(row["inference_json"])
        assert row["alt_phase_digest"] == records["ALT"]["phase_digest"]
        assert infer["hold_phase_digest"] == records["HOLD"]["phase_digest"]
        cand, ref = infer["candidate_calibration_id"], infer["reference_calibration_id"]
        a, b = (_r3_collect_first(blocks, cid) != -1 for cid in (cand, ref))
        paired_n = min(a.size, b.size)
        denominators.add((paired_n, a.size, b.size))
        assert (infer["n_hold"], infer["candidate_n_hold"], infer["reference_n_hold"]) == (
            paired_n, a.size, b.size)
        assert infer["hold_pairing"] == {"path_key_prefix": prefix, "start": 0, "stop": paired_n}
        if infer["fpr_status"] != "ORACLE_SEPARATE":
            assert (infer["fpr_b"], infer["fpr_c"]) == (
                int((a[:paired_n] & ~b[:paired_n]).sum()), int((~a[:paired_n] & b[:paired_n]).sum()))
    assert {(3, 3, 13), (13, 13, 13)} <= denominators


def test_full_r3_integration_trials_summary_collapses_hold_blocks(tmp_path, monkeypatch):
    import hashlib
    import json

    import pandas as pd

    module, cfg, _, did, staging, _, _, records = _r3_full_campaign(tmp_path, monkeypatch, "trials")
    module.export_trial_summaries(tmp_path, staging, did, records)
    table = pd.read_csv(tmp_path / "trials_summary.csv", float_precision="round_trip",
                        dtype={"calibration_id": str, "partition_sha256": str})
    hold = table[table["role"] == "HOLD_NULL"]
    checks = records["HOLD"]["derived"]["null_checks"]
    parts = _r3_read_hold_blocks(module, staging, did, records)
    assert len(hold) == len(checks)
    for cid, check in checks.items():
        rows = hold[hold["calibration_id"] == cid]
        assert len(rows) == 1
        row = rows.iloc[0]
        sources = [part for part, arrays in parts if "first_" + cid in arrays]
        first = _r3_collect_first(parts, cid)
        k = int((first > 0).sum())
        assert (row["n"], row["k"]) == (first.size, k)
        assert (row["null_lo"], row["null_hi"]) == module.cp_bounds(k, first.size, cfg["null_status"]["tail"])
        assert row["null_status"] == check["status"]
        assert (None if pd.isna(row["qualification"]) else row["qualification"]) == check.get("qualification")
        assert json.loads(row["partition_key"]) == [part["key"] for part in sources]
        chain = [[part["key"], part["sha256"]] for part in sources]
        assert row["partition_sha256"] == hashlib.sha256(pdb.canon(chain).encode()).hexdigest()


def test_full_r3_integration_hold_selection_telemetry_numeric_order(tmp_path, monkeypatch):
    import hashlib

    module, cfg, desc, did, staging, _, context, records = _r3_full_campaign(tmp_path, monkeypatch, "telemetry")
    setup = cfg["phi"]["setup"]
    policies = records["DEV"]["derived"]["setups"][pdb.canon(setup)]["RESIDUAL"]["policies"]["PRIMARY"]
    thresholds = records["CAL"]["derived"]["thresholds"]
    parts = _r3_read_hold_blocks(module, staging, did, records)
    assert [part["key"][-1] for part, _ in parts] != sorted((part["key"][-1] for part, _ in parts), key=str)
    for label in module.P_CONF[:2]:
        cid, = (c for c, row in thresholds.items() if row["policy_id"] == policies[label]["policy_id"])
        masks = np.concatenate([arrays["mask_" + cid] for _, arrays in parts])
        reference = module.selection_telemetry(masks, desc["science"]["parameters"]["K"], thresholds[cid]["h"])
        result = module.hold_selection_telemetry(cfg, "full", context, ["HOLD_NULL", *setup, "RESIDUAL"], cid)
        assert result["telemetry"] == reference and result["telemetry"]["n"] == 13
        chain = [[part["key"], part["sha256"]] for part, _ in parts]
        assert result["hold_payload_sha256"] == hashlib.sha256(pdb.canon(chain).encode()).hexdigest()


def test_full_r3_integration_jobs_one_and_three_publish_identical_outputs(tmp_path, monkeypatch):
    import json

    runs = {}
    for jobs in (1, 3):
        module, cfg, desc, did, staging, plan, context, _ = _r3_full_campaign(
            tmp_path, monkeypatch, f"jobs{jobs}", jobs, interrupt=jobs == 3)
        out = tmp_path / f"jobs{jobs}" / "out"

        def build(temp, design, committed):
            confirm = module.confirmatory_from_staging(cfg, "full", context)
            rows = list(module._staged_descriptive_rows(
                staging, design, committed, desc, context["bootstrap_cache"], lambda: None))
            module.export_payloads(temp, staging, design, committed, confirmation=confirm, descriptive_rows=rows)
            return {}

        module.finalize_planned(staging, out, context["authority"], plan, build)
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["design_id"] == did
        assert manifest["realization_descriptor"]["n_hold"] == 13
        csvs = {path.name: pdb.file_sha256(path) for path in out.glob("*.csv")}
        assert set(csvs) == {"calibration.csv", "selections.csv", "trials_summary.csv", "aggregates.csv", "issues.csv"}
        runs[jobs] = (manifest["realization_id"], manifest["realization_descriptor"], manifest["payloads"], csvs)
        assert all(path.stat().st_size < (50 << 20) for path in (*staging.rglob("*.npz"), *out.glob("*.csv")))
    assert runs[1] == runs[3]


def test_full_r3_integration_npz_bound_refuses_exact_limit(tmp_path, monkeypatch):
    module = pio()
    desc = module.design_descriptor(_r3_smoke_cfg(), "smoke")
    did = module.design_id(desc)
    staging = module.open_staging(tmp_path, desc, False)
    key = ["frame", "SMOKE", 24]
    arrays = {"probe": np.arange(8, dtype=np.int64)}
    payload, n_rows = module._npz_payload(arrays)
    stem = module._partition_path(staging, did, {}, key)
    limit = len(payload)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(module, "MAX_PUBLISHED_BYTES", limit)
        with pytest.raises((module.PartitionMismatch, ValueError), match="bytes"):
            module.partition(staging, "SETUP", {}, key, lambda: arrays)
        assert not stem.with_suffix(".npz").exists() and not stem.with_suffix(".json").exists()
    module.partition(staging, "SETUP", {}, key, lambda: arrays)
    assert stem.with_suffix(".npz").stat().st_size == limit
    monkeypatch.setattr(module, "MAX_PUBLISHED_BYTES", limit)
    with pytest.raises((module.PartitionMismatch, ValueError), match="bytes"):
        module._verify_partition(staging, did, {}, key)
    monkeypatch.setattr(module, "MAX_PUBLISHED_BYTES", limit + 1)
    _, rows, read = module._verify_partition(staging, did, {}, key)
    assert rows == n_rows and np.array_equal(read["probe"], arrays["probe"])


def test_full_r3_integration_csv_bound_refuses_exact_limit(tmp_path, monkeypatch):
    module, _, _, _, staging, plan, context, _ = _r3_full_campaign(tmp_path, monkeypatch, "csv-bound")
    out = tmp_path / "out"
    limit = max(path.stat().st_size for path in staging.rglob("*") if path.is_file()) + 4096

    def build(temp, design, committed):
        (temp / "probe.csv").write_bytes(b"x\n" * (limit // 2) + b"x" * (limit % 2))
        return {}

    monkeypatch.setattr(module, "MAX_PUBLISHED_BYTES", limit)
    with pytest.raises(ValueError, match="bytes"):
        module.finalize_planned(staging, out, context["authority"], plan, build)
    assert not out.exists() and not (staging / "phases" / "FINAL.json").exists()
