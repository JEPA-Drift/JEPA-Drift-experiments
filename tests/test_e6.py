"""Tests of E6 phase 1 (stream 23): experiments/e6_second_order.py."""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import e6_second_order as e6
from jepadrift import injection, sim
from jepadrift import pipelines as pl
from jepadrift.data_loader import sp500
from jepadrift.monitors import cusum, streams


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([23, *key]))


def _fake_d3(root, order="C"):
    days = np.arange(np.datetime64("2005-01-03"), np.datetime64("2020-07-01"))
    days = days[np.is_busday(days)]
    ret = np.asarray(_rng(96).standard_normal((days.size, 12)), order=order)
    d = root / "d3_239"
    d.mkdir()
    np.save(d / "dates.npy", days)
    np.save(d / "ret_wide.npy", ret)
    (d / "splits.yaml").write_text(yaml.safe_dump({"segments": sp500._realize_segments(days)}))
    return d, days, ret


def _spy(opened, keys):
    class Recorder(np.ndarray):
        def __getitem__(self, key):
            keys.append(key)
            return super().__getitem__(key)

    def load(path, mmap_mode=None):
        name = Path(path).name
        opened.append((name, mmap_mode))
        assert name != "ret_wide.npy" or mmap_mode == "r", f"{name} opened without mmap_mode='r'"
        a = np.load(path, mmap_mode=mmap_mode)
        return a.view(Recorder) if name == "ret_wide.npy" else a

    return load


def _bounded(keys, stop):
    return bool(keys) and all(isinstance(k, slice) and k.step in (None, 1) and k.stop is not None
                              and 0 <= (k.start or 0) <= k.stop <= stop for k in keys)


@pytest.fixture(scope="module")
def d6():
    return e6.load_d6()


def test_pre_j4_guard(d6):
    X, days, splits = d6
    assert days[-1] == np.datetime64("2019-12-31") and np.isfinite(X).all()
    assert splits["calib"] == (2834, 3775)
    with pytest.raises(ValueError, match="2020-01-01"):
        e6.load_d6(last_day="2020-01-02")


@pytest.mark.parametrize("order", ["C", "F"])
def test_bounded_reader_slices_no_return_row_after_last_day(tmp_path, monkeypatch, order):
    monkeypatch.setattr(e6, "DERIVED", tmp_path)
    d, days, ret = _fake_d3(tmp_path, order)
    first_2020 = int(np.searchsorted(days, np.datetime64("2020-01-01")))
    opened, keys = [], []
    X, got, splits = e6.load_d6(load=_spy(opened, keys))
    assert [m for n, m in opened if n == "ret_wide.npy"] == ["r"] and _bounded(keys, first_2020)
    assert got[0] == days[0] and got[-1] == np.datetime64("2019-12-31") and splits["calib"][1] == got.size
    assert X.flags["C_CONTIGUOUS"] and np.array_equal(X, ret[:first_2020])
    stop = int(np.searchsorted(days, np.datetime64("2018-06-29"), side="right"))
    keys.clear()
    X, got, _ = e6.load_d6(last_day="2018-06-29", load=_spy(opened, keys))
    assert _bounded(keys, stop) and got[-1] == np.datetime64("2018-06-29") and np.array_equal(X, ret[:stop])
    view = _spy(opened, keys)(d / "ret_wide.npy", mmap_mode="r")
    for bad in (slice(None, first_2020 + 1), slice(-5, None), slice(-5, first_2020), slice(None, 0, -1), slice(9, 5),
                slice(0, first_2020, 2)):
        keys.clear()
        view[bad]
        assert not _bounded(keys, first_2020)
    with pytest.raises(AssertionError, match="mmap_mode"):
        _spy(opened, keys)(d / "ret_wide.npy")


@pytest.mark.parametrize("case", ["name", "nat", "2020", "dates_2d", "dates_empty", "dates_nat",
                                  "dates_not_increasing", "dates_swapped", "bounds", "shape_rows", "shape_1d"])
def test_bounded_reader_refuses_before_any_return_copy(tmp_path, monkeypatch, case):
    monkeypatch.setattr(e6, "DERIVED", tmp_path)
    d, days, ret = _fake_d3(tmp_path)
    k = int(np.searchsorted(days, np.datetime64("2020-01-01")))
    bad = {"dates_2d": ("dates.npy", days.reshape(-1, 1)), "dates_empty": ("dates.npy", days[:0]),
           "dates_nat": ("dates.npy", np.where(np.arange(days.size) == 100, np.datetime64("NaT", "D"), days)),
           "dates_not_increasing": ("dates.npy", np.concatenate([days[:100], days[99:-1]])),
           "dates_swapped": ("dates.npy", days[np.r_[:k - 1, k, k - 1, k + 1:days.size]]),
           "shape_rows": ("ret_wide.npy", ret[:-1]), "shape_1d": ("ret_wide.npy", ret[:, 0])}
    if case in bad:
        np.save(d / bad[case][0], bad[case][1])
    kwargs = {"name": {"name": "d2_us97"}, "nat": {"last_day": "NaT"}, "2020": {"last_day": "2020-01-02"},
              "bounds": {"last_day": "2004-12-31"}}.get(case, {})
    opened, keys = [], []
    with pytest.raises(ValueError):
        e6.load_d6(load=_spy(opened, keys), **kwargs)
    names = [n for n, _ in opened]
    assert keys == [] and (case.startswith("shape") or "ret_wide.npy" not in names)
    assert case not in ("name", "nat", "2020") or names == []


def test_bounded_cli_hashes_no_return_panel(tmp_path, monkeypatch):
    monkeypatch.setattr(e6, "DERIVED", tmp_path)
    hashed = []
    monkeypatch.setattr(e6, "_sha256", lambda p: hashed.append(Path(p).name) or "0" * 64)
    monkeypatch.setattr(e6, "run_d6", lambda cfg, log: [])
    monkeypatch.setattr(e6, "run_d5", lambda cfg, jobs, log: [])
    monkeypatch.setattr(e6, "plot", lambda csv, fig_dir: None)
    out = tmp_path / "out"
    assert e6.main(["--phase", "1", "--out", str(out), "--fig-dir", str(out / "fig"), "--log-dir", str(out / "log"),
                    "--jobs", "1"]) == 0
    assert hashed == ["splits.yaml", "e6.yaml", "e6_cells_phase1.csv"]
    assert "ret_wide.npy" not in (out / "log" / "phase1.log").read_text()


def test_energy_streams_invariant_to_day_signs(d6):
    X, _, splits = d6
    a, b = splits["calib"]
    Xc = np.ascontiguousarray(X[a:b])
    Xs, eps = injection.symmetrize(Xc, _rng(90))
    assert (eps < 0).any()
    mu, sd = e6.p1d_moments(Xc)
    assert np.array_equal(e6.p1d_stream(Xc, mu, sd), e6.p1d_stream(Xs, mu, sd))
    state = pl.fit_pipeline(pl.make_spec("P3-D", H=250, N_cal=200), X, splits)
    assert np.array_equal(e6.p3d_stream(state, Xc), e6.p3d_stream(state, Xs))


def test_cell_injection_rows_match_per_onset_injection(d6):
    X, _, splits = d6
    a, b = splits["calib"]
    for cell in ({"family": "F4-deform", "params": {"subspace": [1, 2, 3], "r": 1.5}},
                 {"family": "F4-rotate", "params": {"pair": [0, 1], "theta_deg": 30.0}}):
        full, M, meta = e6.cell_injection(X, cell, a, (a, b))
        assert meta["convention"] is None and meta["info"] > 0
        for s in (a + 1, a + 300, b - 250):
            one, M_s, meta_s = injection.inject(X, cell["family"], s, None, {"calib": (a, b), **cell["params"]}, _rng(91))
            assert np.array_equal(M, M_s) and meta["info"] == meta_s["info"]
            assert np.array_equal(one[:s], X[:s])
            assert np.abs(one[s:] - full[s:]).max() <= 1e-12 * np.abs(X[a:b]).max()


def test_p1d_article_b_stream():
    X = sim.garch_panel(400, 30, 0.08, 0.90, 7, _rng(92), factor_rho=0.4)
    mu, sd = e6.p1d_moments(X[:300])
    r = X[:300].mean(axis=1)
    assert (mu, sd) == (float(np.mean(r ** 2)), float(np.std(r ** 2)))
    assert np.array_equal(e6.p1d_stream(X, mu, sd), streams.energy_stream(X.mean(axis=1), mu, sd))
    stacked = e6.p1d_stream(np.stack([X[:200], X[200:]]), mu, sd)
    assert stacked.shape == (2, 200) and np.array_equal(stacked[1], e6.p1d_stream(X[200:], mu, sd))


def test_iid_threshold_rule():
    lam = e6.iid_threshold(1, 100, 2000, [23, 93])
    rng = np.random.default_rng(np.random.SeedSequence([23, 93]))
    peaks = cusum.cusum_trajectory_vec((rng.chisquare(1, size=(2000, 100)) - 1.0) / math.sqrt(2.0), 0.5).max(axis=1)
    assert (peaks > lam).mean() <= 0.05 < (peaks > lam * (1.0 - 1e-6)).mean()


def test_first_alarms_and_delays():
    q = np.array([[0.0, 3.0, 3.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    off = e6.first_alarms(q, 4.0)
    assert off.tolist() == [2, -1]
    assert np.array_equal(e6.delays(off), np.array([3.0, np.nan]), equal_nan=True)


def test_censoring_rmst_and_labels():
    H = 10
    s = e6.delay_summary(np.array([1.0, 4.0, np.nan, 10.0]), H)
    assert (s["n"], s["det_rate"], s["censored_share"]) == (4, 0.75, 0.25)
    assert s["rmst_h"] == (1 + 4 + 10 + 10) / 4 and s["cond_mean"] == 5.0
    assert s["median_delay"] == 7.0 and not s["median_above_h"]
    low = e6.delay_summary(np.array([3.0, np.nan]), H)
    assert math.isnan(low["median_delay"]) and low["median_above_h"]
    full, cens = np.array([2.0, 3.0]), np.array([2.0, np.nan])
    assert e6.g_add(full, full, H) == (1.0, "exact")
    assert e6.g_add(cens, full, H) == (6.0 / 2.5, "lower_bound")
    assert e6.g_add(full, cens, H)[1] == "undetermined" and e6.g_add(cens, cens, H)[1] == "undetermined"


def test_d6_ci_rule():
    reason = e6.d6_ci_reason(692, 250)
    assert "2.77" in reason and "10" in reason
    assert "prespecified" in reason and "not a general requirement" in reason
    assert "0.88" in e6.d6_ci_reason(442, 500)
    assert e6.d6_ci_reason(2500, 250) is None


def test_wilson_and_paired_bootstrap():
    lo, hi = e6.wilson(50, 100)
    assert (round(lo, 4), round(hi, 4)) == (0.4038, 0.5962)
    assert e6.wilson(0, 200)[0] == 0.0 and e6.wilson(200, 200)[1] == pytest.approx(1.0)
    d_b = _rng(94).integers(1, 50, 300).astype(float)
    d_a = 2.0 * d_b
    d_a[:30] = np.nan
    g, _ = e6.g_add(d_a, d_b, 100)
    ci = e6.paired_bootstrap(d_a, d_b, 100, 500, _rng(95))
    assert ci[0] < g < ci[1] and ci == e6.paired_bootstrap(d_a, d_b, 100, 500, _rng(95))


def test_tie_share_and_alarm_mode():
    assert e6.tie_share(np.array([1.0, 2.0, 2.0, 2.0, 0.5]), 2.0) == 0.6
    dates = np.array(["2019-01-04", "2019-01-07", "2019-01-04", "2018-06-01"], dtype="datetime64[D]")
    assert e6.alarm_mode(dates) == ("2019-01-04", 0.75)
    mode, share = e6.alarm_mode(dates[:0])
    assert mode == "" and math.isnan(share)


def test_d5_roles_disjoint():
    g = {"N": 12, "alpha": 0.08, "beta": 0.90, "nu": 7, "factor_rho": 0.40, "burn": 50}
    cal = e6.d5_panel(1, 0, 30, g)
    assert cal.shape == (30, 12) and np.array_equal(cal, e6.d5_panel(1, 0, 30, g))
    assert not np.array_equal(cal, e6.d5_panel(2, 0, 30, g)) and not np.array_equal(cal, e6.d5_panel(1, 1, 30, g))


def test_phase2_refused():
    with pytest.raises(SystemExit):
        e6.main(["--phase", "2"])


def test_cli_tiny_deterministic_across_jobs(tmp_path, monkeypatch):
    monkeypatch.setattr(e6, "D5_CHUNK", 8)
    cfg = e6.load_config()
    cfg["H"] = [250]
    cfg["n_iid"], cfg["n_boot"] = 500, 50
    cfg["d5"].update(n_cal=16, n_test=16)
    cfg["cells"] = [c for c in cfg["cells"] if c["name"] in ("deform_r2", "rotate_pc2_pc3_45")]
    path = tmp_path / "e6_tiny.yaml"
    path.write_text(yaml.safe_dump(cfg))
    blobs = []
    for jobs in (1, 2):
        out = tmp_path / f"j{jobs}"
        assert e6.main(["--phase", "1", "--config", str(path), "--out", str(out), "--fig-dir", str(out / "fig"),
                        "--log-dir", str(out / "log"), "--jobs", str(jobs)]) == 0
        blobs.append((out / "e6_cells_phase1.csv").read_bytes())
    assert blobs[0] == blobs[1]
    out = tmp_path / "j1"
    df = pd.read_csv(out / "e6_cells_phase1.csv", float_precision="round_trip", keep_default_na=False,
                     na_values=["NaN"])
    assert list(df.columns) == e6.COLUMNS and len(df) == 3 * 3 + 4 * 3 + 4
    assert np.allclose(df.gamma_op, df.threshold / df.lam_iid)
    d6, d5 = df[df.background == "d6_d3_239"], df[df.background == "d5_garch_t7"]
    assert d6.in_sample.all() and not d5.in_sample.any()
    assert d6.fpr_lo.isna().all() and d6.g_lo.isna().all() and d6.det_lo.isna().all()
    assert (d6.ci_reason.str.len() > 0).all() and (d6.ci_method == "none").all()
    assert d6[d6.cell != "H0"].ci_reason.str.startswith("IC=NA").all()
    assert set(d6[d6.cell != "H0"].status) == {"exploratory"}
    assert set(d5[d5.cell == "rotate_pc2_pc3_45"].status) == {"prespecified"}
    assert set(d5[d5.cell == "rotate_pc2_pc3_45"].role) == {"negative_control"}
    h0 = d5[d5.cell == "H0"]
    assert sorted(set(h0.threshold_rule)) == ["d5_calibration_panels", "d6_rule_on_fit_panel"]
    assert h0.fpr_lo.notna().all() and h0[h0.threshold_rule == "d5_calibration_panels"].fpr_region_lo.notna().all()
    assert set(d5[d5["mode"] == "factor"].K_choice) == {"conditional", "sensitivity"}
    drift = d5[(d5.cell != "H0") & (d5.monitor == "P3-D")]
    assert drift.g_lo.notna().all() and (drift.ci_method == "paired_bootstrap_percentile").all()
    assert df[df.family == "F4-rotate"].info_per_direction.isna().all()
    assert (df[df.family == "F4-deform"].info_per_direction > 0).all()
    assert (df[df.cell != "H0"].info_model == "gaussian_design").all()
    for stem in ("e6_phase1_delays", "e6_phase1_gadd"):
        assert (out / "fig" / f"{stem}.png").exists() and (out / "fig" / f"{stem}.pdf").exists()
    assert (out / "log" / "phase1.log").exists()
