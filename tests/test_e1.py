"""Tests of stream 12, E1 (experiments/e1_problem.py): strict window, J2(i) assets and risk, per-window resets."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import e1_problem as e1
from jepadrift import floors as fl
from jepadrift import pipelines as pl
from jepadrift.injection import fit_background, inject, symmetrize
from jepadrift.monitors import eprocess
from jepadrift.monitors.cusum import cusum_trajectory_vec

REPO = Path(__file__).resolve().parents[1]


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([12, 99, *key]))


def test_window_strict_bounds():
    for name in ("d2_us97", "d3_239"):
        X, days, splits, assets, rows = e1.load_window(name)
        assert str(days[0]) == "2005-01-04" and str(days[-1]) == "2019-12-31" and X.shape == (3774, len(assets))
        assert splits["calib"] == (2833, 3774) and splits["pre_monitor"] == (0, 3774) and np.isfinite(X).all()
        assert np.asarray(e1.DATASETS[name][0]()[1], dtype="datetime64[D]").max() > np.datetime64("2020-01-01")
    rows = e1.load_window("d3_239")[4]
    assert (rows[0], rows[-1]) == (1257, 5030) and e1.EXCLUDED == {"d3_239": ("2005-01-03",)}
    for bad in ("2005-01-03", "2020-01-02"):
        with pytest.raises(ValueError):
            e1.check_window(np.array(["2010-06-01", bad], dtype="datetime64[D]"))


@pytest.mark.parametrize("bad", ["2004-12-31", "2010-06-01", "2020-01-02"])
def test_load_window_rejects_an_inserted_pre_monitor_date(monkeypatch, bad):
    load, load_splits = e1.DATASETS["d2_us97"]
    ret, dates, assets = load()
    d = np.insert(np.asarray(dates, dtype="datetime64[D]"), 1000, np.datetime64(bad))
    r = np.insert(ret, 1000, ret[1000], axis=0)
    monkeypatch.setitem(e1.DATASETS, "d2_us97", (lambda: (r, d, assets), load_splits))
    e1.load_window.cache_clear()
    try:
        with pytest.raises(ValueError, match="C-e1-window"):
            e1.load_window("d2_us97")
    finally:
        e1.load_window.cache_clear()


def test_j2i_assets_common_with_e3():
    assert e1.j2i_assets("d2_us97") == [24, 71, 56, 46, 75]
    assert e1.j2i_assets("d3_239") == [60, 177, 141, 116, 184]
    for name in ("d2_us97", "d3_239"):
        assert len(e1.p1_assets(name)) == 20 and not set(e1.j2i_assets(name)) & set(e1.p1_assets(name))


def test_include_test_window_refused(tmp_path):
    with pytest.raises(SystemExit) as exc:
        e1.main(["--include-test-window", "--out", str(tmp_path)])
    assert exc.value.code == 2


def test_p1c_cusum_resets_at_onset():
    H, tau = 750, 500
    sel, gamma = e1.lattice_selection(H), pl.horizon_gamma(H)
    X = np.concatenate([np.full((tau, 1), 0.01), 0.01 * _rng(1).standard_normal((H + 100, 1))])
    off, B = e1.p1c_window(X, tau, H, [0], _rng(2), sel, gamma)
    alone, B_alone = e1.p1c_window(np.ascontiguousarray(X[tau:tau + H]), 0, H, [0], _rng(2), sel, gamma)
    assert B.tobytes() == B_alone.tobytes() and all(off[k].tobytes() == alone[k].tobytes() for k in off)
    full = e1.coin_bits(X[:tau + H, 0], _rng(2))
    exact_from_zero = np.flatnonzero(cusum_trajectory_vec(full - 0.5, e1.DELTA)[tau:] > sel["threshold"])
    av_from_zero = np.flatnonzero(eprocess.log_edetector(2.0 * full - 1.0, "cusum")[tau:] >= math.log(gamma))
    assert exact_from_zero[0] == 0 and av_from_zero[0] == 0
    assert off["exact"][0] != 0 and off["anytime-valid"][0] != 0


def test_p1c_prefix_invariance_each_onset():
    H = 200
    sel, gamma = e1.lattice_selection(H), pl.horizon_gamma(H)
    X = 0.01 * _rng(3).standard_normal((900, 3))
    X[_rng(4).random(X.shape) < 0.01] = 0.0
    for r in range(40):
        Xm = symmetrize(X, _rng(5, r))[0]
        tau = 0 if r == 0 else len(X) - H if r == 1 else int(_rng(6, r).integers(0, len(X) - H + 1))
        ref, B_ref = e1.p1c_window(Xm, tau, H, [0, 1, 2], _rng(7, r), sel, gamma)
        outside = np.ones(len(X), dtype=bool)
        outside[tau:tau + H] = False
        for other in (np.zeros_like(Xm), -Xm, 0.01 * _rng(8, r).standard_normal(Xm.shape)):
            off, B = e1.p1c_window(np.where(outside[:, None], other, Xm), tau, H, [0, 1, 2], _rng(7, r), sel, gamma)
            assert B.tobytes() == B_ref.tobytes()
            assert all(off[k].tobytes() == ref[k].tobytes() for k in ref)


def test_phase_monitor_resets_at_each_boundary():
    x = np.clip(0.2 + _rng(9).standard_normal((600, 2)), -1.0, 1.0)
    phases = [np.arange(0, 200), np.arange(200, 450), np.arange(450, 600)]
    for dictionary in (False, True):
        ref = e1.phase_offsets(x, phases, 0.05, dictionary)
        for p, start in ((1, 200), (2, 450)):
            xp = x.copy()
            xp[:start] = -xp[:start]
            new = e1.phase_offsets(xp, phases, 0.05, dictionary)
            assert all(np.array_equal(a, b) for a, b in zip(new[p:], ref[p:]))


def test_j2i_risk():
    levels = [e1.lattice_selection(H)["level"] for H in (750, 2000)]
    risk = e1.j2i_risk(2000, [levels[0]] * 27 + [levels[1]] * 27, 0.01)
    assert risk["bounds"][0] == (68, 107) and risk["bounds"][27] == (72, 111)
    assert round(risk["p_fail"][0], 4) == 0.0293 and round(risk["p_fail"][27], 4) == 0.0319
    assert round(risk["p_any"], 3) == 0.813 and abs(risk["expected"] - 1.65) < 0.01
    assert e1.poisson_binomial_tail(risk["p_fail"], 0) == pytest.approx(1.0, abs=1e-12)
    assert e1.poisson_binomial_tail(risk["p_fail"], 1) == pytest.approx(risk["p_any"], abs=1e-12)


def test_delay_summary_and_labels():
    s = e1.delay_summary(np.array([-1, 0, 9, -1]), 10)
    assert s["add_h"] == 31 / 4 and s["det_rate"] == 0.5 and s["censored_share"] == 0.5
    assert s["mean_detected"] == 5.5 and math.isnan(s["median_delay"]) and s["det_lo"] < 0.5 < s["det_hi"]
    assert e1.delay_summary(np.array([4, 0, 9]), 10)["median_delay"] == 5.0
    assert e1.gain_label(1.0, 1.0) == "uncensored" and e1.gain_label(0.9, 1.0) == "lower_bound"
    assert e1.gain_label(1.0, 0.9) == "undetermined"


def test_b_chain_reference_fixed_before_injection():
    for s in range(3):
        p = e1.b_chain("d2_us97", s)
        assert sorted(p.tolist()) == list(range(97)) and e1.b_chain("d2_us97", s).tobytes() == p.tobytes()
        assert all(p[0] in np.sort(p[:N]) for N in (8, 16, 32, 64, 97))


def test_f3_market_column_and_full_information():
    X, _, splits, _, _ = e1.load_window("d2_us97")
    a, b = splits["calib"]
    state = pl.fit_pipeline(pl.make_spec("P3-C", mode="full"), X, splits)
    _, delta, meta = inject(X, "F3", 100, fl.kl_from_sharpe(4.0), {"calib": (a, b), "fit": fit_background(X[a:b], 6)},
                            _rng(10))
    dz = delta @ state["rep"].state["W"]
    assert np.abs(dz[1:]).max() < 1e-9 * abs(dz[0])
    assert 0.5 * dz @ dz == pytest.approx(fl.kl_from_sharpe(4.0), rel=1e-9) == meta["info"]


def test_sign_efficiency_and_recentred_stream():
    h = 1.06 * 20000 ** -0.2
    e = e1.sign_efficiency(_rng(11).standard_normal((20000, 2)))
    assert np.allclose(e, 2 / (math.pi * (1 + h * h)), atol=0.015) and np.allclose(e, 2 / math.pi, atol=0.03)
    B = (_rng(12).random((50, 3)) < 0.6).astype(np.float64)
    for q in (0.3, 0.5, np.array([0.2, 0.5, 0.9])):
        assert np.abs(e1.recentred(B, q)).max() <= 1.0
    assert np.array_equal(e1.recentred(B, 0.5), 2.0 * B - 1.0)


def test_slope_fit_known_slope():
    g = _rng(13)
    N, chain = np.tile([8, 16, 32, 64, 128], 20), np.repeat(np.arange(20), 5)
    y = 0.3 * np.log(N) + 0.01 * g.standard_normal(N.size) + np.repeat(0.05 * g.standard_normal(20), 5)
    slope, lo, hi = e1.slope_fit(np.log(N), y, chain, 500, _rng(14))
    assert abs(slope - 0.3) < 0.02 and lo < 0.3 < hi


def test_arm_c_d2_shares_match_audit():
    ref = pd.read_csv(REPO / "results" / "audit" / "budget_share.csv", float_precision="round_trip")
    ref = ref[(ref.dataset == "d2_us97") & (ref.dating == "lt_spy")]
    got = pd.DataFrame(e1.budget_shares("d2_us97", "lt_spy"))
    m = ref.merge(got, on=["subspace", "gamma"], suffixes=("_audit", "_e1"))
    assert len(m) == len(ref) == len(got)
    assert (m.share_audit == m.share_e1).all() and (m.n_phases_audit == m.n_phases_e1).all()


def test_cli_tiny_deterministic_across_jobs(tmp_path):
    cfg = yaml.safe_load((REPO / "configs" / "e1.yaml").read_text())
    cfg["datasets"] = ["d2_us97"]
    cfg["j2i"].update(reps=12, H=[750])
    cfg["A"].update(reps=6, sr=[4], families={"d2_us97": ["F3"]})
    cfg["chunk"], cfg["span"], cfg["boot"] = 4, 3, 50
    path = tmp_path / "tiny.yaml"
    path.write_text(yaml.safe_dump(cfg))
    for jobs in (1, 2):
        out = tmp_path / f"j{jobs}"
        assert e1.main(["--config", str(path), "--arms", "J2I,A", "--jobs", str(jobs), "--out", str(out),
                        "--fig-dir", str(out / "fig"), "--log-dir", str(out / "log")]) == 0
    for f in ("e1_cells.csv", "e1_null.csv", "e1_j2_summary.txt"):
        assert (tmp_path / "j1" / f).read_bytes() == (tmp_path / "j2" / f).read_bytes(), f
    cells = pd.read_csv(tmp_path / "j1" / "e1_cells.csv", float_precision="round_trip")
    assert {"P1-C", "P2-C", "P3-C", "P3-CS(b)", "P7"} <= set(cells.pipeline) and cells.retrospective.all()


def test_j2i_has_54_controls_on_the_frozen_basis():
    D = {n: len(e1.frozen_states(n, 750)["P3-C/factor"][1]["channels"]["residual"]) + 1 for n in ("d2_us97", "d3_239")}
    assert D == {"d2_us97": 6, "d3_239": 11} and 2 * sum(e1.N_J2I + d for d in D.values()) == 54
