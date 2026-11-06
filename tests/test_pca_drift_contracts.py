"""Stream 31 QA contracts of the PCA drift benchmark (prompt 31): independent references and negative witnesses."""
import copy
import hashlib
import io
import itertools
import json
import math
import os
import re
import subprocess
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import yaml

from experiments import pca_drift_benchmark as pdb
from experiments import pca_drift_tables as pdt
from experiments.figures import plot_figure_1 as pf
from jepadrift.data_loader import sp500
from jepadrift.representations.extract import segment_rows

REPO = Path(__file__).resolve().parents[1]
RES = REPO / "results" / "pca_drift_benchmark"
SMOKE = RES / "smoke_predictive_v2_closeout"
FULL = RES / "full_2000_20261101"
TAB_SMOKE = RES / "tables" / "smoke_predictive_v2_closeout"
TAB_FULL = RES / "tables" / "full_2000_20261101"
FIG_SMOKE_FIX = RES / "figures" / "smoke_predictive_v2_closeout_fix_smoke_no_claims"
FIG_FULL_FIX = RES / "figures" / "full_2000_20261101_fix_smoke_no_claims"
FULL_MANIFEST_SHA = "3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47"
TRIALS_ENV = "PCA_FULL2000_TRIALS"
TRIALS_SHA = "40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c"
TRIALS_BYTES = 48_317_020
TRIALS_ROWS = 716_000
E2_SHA = "e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823"
E3_OVERSHOOT_SHA = "1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3"
EPS = float(np.finfo(np.float64).eps)
SYNTH = ("SYNTH_GAUSS_EQUICORR", "SYNTH_T7_EQUICORR")
REAL_STATUSES = {"NOT_EVALUABLE_STANDARD_SPLIT", "BLOCKED_PRE_J4", "DATA_UNAVAILABLE"}
CSV_NAMES = ("spectra", "selection", "calibration", "aggregates", "issues")
INFO_COLS = ("I_objective", "I_plugin_lw", "I_pop_joint", "I_cov_joint", "I_cov_marginal_sum")
TABLE_FILES = {"T1": "Tableau_PCA_1.csv", "T2": "Tableau_PCA_2.csv", "T3": "Tableau_PCA_3.csv",
               "lineage": "table_lineage.csv"}


def _rng(*key):
    return np.random.default_rng(np.random.SeedSequence([31, *key]))


def _na(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or v in ("", "NaN")


def _num(v):
    return math.nan if _na(v) else float(v)


def _text(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, float_precision="round_trip")


def _flags(v):
    return set() if _na(v) else set(json.loads(v))


def _verified_outputs(run_dir, names):
    manifest = json.loads((run_dir / "manifest.json").read_text())
    frames = {}
    for name in names:
        path, meta = run_dir / f"{name}.csv", manifest["outputs"][f"{name}.csv"]
        assert pdb.file_sha256(path) == meta["sha256"] and path.stat().st_size == meta["bytes"], (run_dir.name, name)
        frames[name] = _text(path)
        assert len(frames[name]) == meta["rows"], (run_dir.name, name)
    return manifest, frames


def _tiny_cfg(**over):
    cfg = pdb.load_config(pdb.CONFIG, "smoke")
    cfg.update(N=24, H=12, T_fit=80, nmax=6, n_center=6, n_cal=19, n_null=8, n_alt=8, minibatch=3, cov_search_chunk=7)
    cfg["synthetic"]["C_axes"] = [3, 5]
    cfg.update(over)
    return cfg


def _run_dir(base, name, cfg, dataset="synthetic"):
    out, log = base / name / "out", base / name / "log"
    assert pdb.run_benchmark(cfg, dataset, out, log) == 0
    return out


def _frames(out, names=CSV_NAMES + ("trials",)):
    return {n: _text(out / f"{n}.csv") for n in names}


def _fake_panel(root, post2019):
    dates = np.arange(np.datetime64("2004-12-31"), np.datetime64("2023-12-30"))
    dates = dates[np.is_busday(dates)]
    g = _rng(8, 1)
    n_assets = 21
    X = 0.01 * (0.7 * g.standard_normal((len(dates), n_assets)) + 0.5 * g.standard_normal((len(dates), 1)))
    X[dates >= np.datetime64("2020-01-01")] = post2019
    d = root / "derived" / "fake"
    d.mkdir(parents=True)
    np.save(d / "ret_wide.npy", np.asfortranarray(X))
    np.save(d / "dates.npy", dates)
    (d / "assets.json").write_text(json.dumps([f"A{i}" for i in range(n_assets)]))
    segments = sp500._realize_segments(dates)
    (d / "splits.yaml").write_text(yaml.safe_dump({"dataset": "fake", "embargo_trading_days": 65,
                                                   "segments": segments}, sort_keys=False))
    outputs = [{"path": f"data/derived/fake/{n}", "sha256": pdb.file_sha256(d / n)}
               for n in ("ret_wide.npy", "dates.npy", "assets.json", "splits.yaml")]
    (root / "MANIFEST.json").write_text(json.dumps({"datasets": {"fake": {"outputs": outputs}}}))
    cfg = _tiny_cfg()
    cfg["mode"] = "full"
    a, b = segment_rows(dates, segments["calib"])
    cfg["real"].update(derived_dir=str(d), manifest=str(root / "MANIFEST.json"), dataset="fake", n_null=19,
                       expected_calib_rows=b - a)
    return cfg, dates, segments


@pytest.fixture(scope="module")
def sealed():
    assert not (FULL / "trials.csv").exists()
    return {"SMOKE": _verified_outputs(SMOKE, CSV_NAMES + ("trials",)), "FULL": _verified_outputs(FULL, CSV_NAMES)}


@pytest.fixture(scope="module")
def tables():
    out = {}
    for tag, d in (("SMOKE", TAB_SMOKE), ("FULL", TAB_FULL)):
        assert pdt.verify_output_dir(d), d
        out[tag] = {key: _text(d / name) for key, name in TABLE_FILES.items()}
    return out


@pytest.fixture(scope="module")
def smoke_run():
    return pdt.load_run(SMOKE)


@pytest.fixture(scope="module")
def ftiny(tmp_path_factory):
    base = tmp_path_factory.mktemp("ftiny")
    calls, orig_alt, orig_draw = [], pdb.detect_alternative, pdb.draw_path

    def spy(run, family, stream, Z, m, s2, p, h):
        calls.append((family, p, pdb.array_sha256(Z)))
        return orig_alt(run, family, stream, Z, m, s2, p, h)

    def poisoned(cfg, background, role, i, T):
        X = orig_draw(cfg, background, role, i, T)
        return 10.0 * X if role in ("holdout_null", "alternative") else X

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pdb, "detect_alternative", spy)
        tiny = _run_dir(base, "tiny", _tiny_cfg())
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pdb, "draw_path", poisoned)
        poison = _run_dir(base, "poison", _tiny_cfg())
    cfg_missing = _tiny_cfg()
    cfg_missing["real"]["derived_dir"] = str(base / "absent")
    missing = _run_dir(base, "missing", cfg_missing)
    return {"tiny": tiny, "poison": poison, "missing": missing, "alt_calls": calls}


@pytest.fixture(scope="module")
def tiny_prep():
    cfg = _tiny_cfg()
    return cfg, pdb.prepare_background(pdb.Run(cfg, "qa-31"), "SYNTH_GAUSS_EQUICORR")


@pytest.fixture(scope="module")
def ffake(tmp_path_factory):
    out = {}
    for tag, post in (("a", np.nan), ("b", 1e6)):
        root = tmp_path_factory.mktemp(f"ffake_{tag}")
        cfg, dates, segments = _fake_panel(root, post)
        o = _run_dir(root, "run", cfg, dataset="both")
        out[tag] = {"cfg": cfg, "dates": dates, "segments": segments, "out": o,
                    "manifest": json.loads((o / "manifest.json").read_text()), "frames": _frames(o)}
    return out


@pytest.fixture(scope="module")
def smoke_ctx():
    return pf.load_context(SMOKE, TAB_SMOKE)


@pytest.fixture(scope="module")
def full_ctx():
    return pf.load_context(FULL, TAB_FULL)


def _texts(fig):
    return [" ".join(t.get_text().split()) for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip()]


def _render(entry, src=None, meta=None):
    if src is None:
        src = pd.read_csv(io.StringIO(pf.save_fair_csv_text(entry["source"])), float_precision="round_trip")
    fig = pf.render_figure(src, meta or entry["meta"])
    out = {"texts": _texts(fig), "title": " ".join(fig.get_suptitle().split()),
           "ylabel_right": " ".join(fig.axes[1].get_ylabel().split())}
    plt.close(fig)
    return out


@pytest.fixture(scope="module")
def full_renders(full_ctx):
    out = {}
    for key in ("mean", "cov"):
        entry = pf.build_entry(full_ctx, key)
        out[key] = {"entry": entry, **_render(entry)}
    return out


def _trials_groups(path):
    t = pd.read_csv(path, dtype={"group_id": str, "role": str}, float_precision="round_trip")
    return {key: g.sort_values("replicate") for key, g in t.groupby(["group_id", "role"], sort=False)}, t


def test_e2_cells_crlf_disk_and_index_unchanged():
    disk = (REPO / "results" / "e2" / "e2_cells.csv").read_bytes()
    index = subprocess.run(["git", "show", ":results/e2/e2_cells.csv"], cwd=REPO, capture_output=True,
                           check=True).stdout
    assert hashlib.sha256(disk).hexdigest() == E2_SHA
    assert hashlib.sha256(index).hexdigest() == E2_SHA and index == disk
    assert disk.count(b"\r\n") == 47 and disk.count(b"\n") == 47
    assert "results/e2/e2_cells.csv -text" in (REPO / ".gitattributes").read_text().splitlines()
    assert hashlib.sha256(disk.replace(b"\r\n", b"\n")).hexdigest() != E2_SHA


def _d8_text_ok(text):
    return all(s in text for s in ("## C-e3-d8-fail", "+0.0528334213 > 0.05", "It is a FAIL by excess"))


def test_d8_fail_preserved_verbatim():
    text = (REPO / "docs" / "DEVIATIONS.md").read_text()
    assert _d8_text_ok(text)
    path = REPO / "results" / "e3" / "e3_overshoot.csv"
    assert pdb.file_sha256(path) == E3_OVERSHOOT_SHA
    df = _text(path)
    row = df[(df.background == "iid") & (df.statistic == "first_order_d1_l3") & (df.role == "primary")]
    assert len(row) == 1 and row.gate.iloc[0] == "FAIL"
    assert round(100.0 * float(row.rel_gap.iloc[0]), 4) == 5.2833
    assert not _d8_text_ok(text.replace("It is a FAIL by excess", "It is a PASS by excess"))


def test_axis_list_round_trip_and_d(sealed):
    checked = 0
    for tag, (manifest, frames) in sealed.items():
        nmax = int(manifest["config"]["nmax"])
        for name in ("selection", "calibration", "aggregates"):
            df = frames[name]
            for s, d in zip(df["S"], df["d"]):
                if _na(s):
                    continue
                axes = pdb.parse_S(s, nmax)
                assert pdb.S_json([i - 1 for i in axes]) == s, (tag, name, s)
                assert pdt._parse_S(s, nmax) == axes
                if not _na(d):
                    assert int(float(d)) == len(axes), (tag, name, s, d)
                checked += 1
    assert checked > 0
    assert pdb.S_json(pdb.parse_S("[1,2,3]", 20)) == "[2,3,4]"


MEAN_INFO = ("I_objective", "I_plugin_lw", "I_pop_joint")
COV_INFO = ("I_objective", "I_cov_joint", "I_cov_marginal_sum")
REQUIRED_INFO = {"MEAN_GAUSS_PLUGIN_LW": MEAN_INFO, "MEAN_GAUSS_PLUGIN_LW_T7_PROXY": MEAN_INFO,
                 "COV_GAUSS_POP_JOINT_EXACT": COV_INFO, "COV_GAUSS_POP_JOINT_T7_PROXY": COV_INFO,
                 "COV_GAUSS_MARGINAL": COV_INFO, "COV_GAUSS_MARGINAL_T7_PROXY": COV_INFO}


def _info_problems(sel):
    probs = []
    for r in sel[sel.status == "OK"].to_dict("records"):
        sid, ik = r["selection_id"], r["info_kind"]
        if _na(ik):
            required = ()
            if r["detector_family"] != pdb.ENERGY:
                probs.append((sid, "info_kind", "missing"))
        elif ik not in REQUIRED_INFO:
            probs.append((sid, "info_kind", ik))
            continue
        else:
            required = REQUIRED_INFO[ik]
        for col in INFO_COLS:
            if _na(r[col]):
                if col in required:
                    probs.append((sid, col, "missing"))
            elif not (math.isfinite(float(r[col])) and float(r[col]) >= 0.0):
                probs.append((sid, col, r[col]))
    return probs


def test_information_finite_nonnegative_positive_eigenvalues(sealed):
    for tag, (manifest, frames) in sealed.items():
        spe = frames["spectra"]
        lam = np.array([float(v) for v in spe["lambda_lw"]])
        assert np.isfinite(lam).all() and (lam > 0.0).all(), tag
        assert all(float(w) == math.sqrt(float(v)) for w, v in zip(spe["whitening_scale"], spe["lambda_lw"]))
        probs = _info_problems(frames["selection"])
        assert not probs, (tag, probs[:5])
        for bg, block in manifest["synthetic"]["backgrounds"].items():
            c = block["covariance_search"]["clipped_negative_kl"]
            assert isinstance(c, int) and not isinstance(c, bool) and c >= 0, (tag, bg, c)
    sel = sealed["SMOKE"][1]["selection"].copy()
    i = sel.index[(sel.status == "OK") & (sel.info_kind == "MEAN_GAUSS_PLUGIN_LW")][0]
    sel.loc[i, "I_plugin_lw"] = "NaN"
    assert (sel.loc[i, "selection_id"], "I_plugin_lw", "missing") in _info_problems(sel)


def test_clip_tolerance_and_documented_rejections():
    for raw in (-1e-13, -1e-12, -100.0 * EPS):
        v, n = pdb.clip_kl(np.array([raw, 0.25]))
        assert v.tolist() == [0.0, 0.25] and n == 1, raw
    with pytest.raises(ArithmeticError):
        pdb.clip_kl(np.array([-2e-12]))
    assert 1e-12 > 1000.0 * EPS
    for A0, A1 in ((np.eye(2), np.diag([1.0, -1.0])), (np.diag([1.0, -1.0]), np.eye(2))):
        with pytest.raises(ValueError, match="positive definite"):
            pdb.kl_cov_raw(A0, A1)
    with pytest.raises(ArithmeticError):
        pdb.kl_cov(np.eye(2), np.diag([-1.0, -1.0]))
    g = _rng(5, 3)
    for _ in range(5):
        A = g.standard_normal((4, 4))
        B = g.standard_normal((4, 4))
        kl = pdb.kl_cov(A @ A.T + 0.5 * np.eye(4), B @ B.T + 0.5 * np.eye(4))
        assert math.isfinite(kl) and kl >= 0.0
    with np.errstate(all="ignore"):
        observed = {"diag(-1,-1)": float(pdb.kl_cov_raw(np.eye(2), np.diag([-1.0, -1.0]))),
                    "nan": float(pdb.kl_cov_raw(np.eye(2), np.array([[np.nan, 0.0], [0.0, 1.0]]))),
                    "inf": float(pdb.kl_cov_raw(np.eye(2), np.array([[np.inf, 0.0], [0.0, 1.0]]))),
                    "clip_kl(nan)": [float(x) for x in pdb.clip_kl(np.array([np.nan]))[0]]}
    print(f"O-E3-NONFINITE observed limit outside the finite SPD prerequisite, not a passed control: {observed}")


def _spd(g, n, cond):
    Q, _ = np.linalg.qr(g.standard_normal((n, n)))
    S = (Q * np.linspace(cond, 1.0, n)) @ Q.T
    return 0.5 * (S + S.T)


def _desc_eigh(S):
    lam, V = np.linalg.eigh(S)
    return lam[::-1].copy(), V[:, ::-1].copy()


def test_mean_kl_eigenbasis_identity_and_order_counterexamples():
    g = _rng(1, 1)
    S = _spd(g, 6, 10.0)
    cond = float(np.linalg.cond(S))
    assert cond <= 10.0 + 1e-9
    tol = 64.0 * EPS * cond
    delta = g.standard_normal(6)
    y = np.linalg.solve(np.linalg.cholesky(S), delta)
    ref = 0.5 * float(y @ y)
    assert math.isclose(pdb.kl_mean(delta, S), ref, rel_tol=tol, abs_tol=0.0)
    lam, V = np.linalg.eigh(S)
    assert math.isclose(float(pdb.q_plugin(V.T @ delta, lam).sum()), ref, rel_tol=tol, abs_tol=0.0)
    assert abs(float(pdb.q_plugin(V.T @ delta, lam + 0.5).sum()) / ref - 1.0) > 1e-3
    lam_d, V_d = _desc_eigh(S)
    q_first = pdb.q_plugin(V_d.T @ (3.0 * V_d[:, 0]), lam_d)
    assert q_first[0] > 0.0 and q_first[1:].sum() <= 1e-24 * q_first[0]
    q_last = pdb.q_plugin(V_d.T @ (3.0 * V_d[:, -1]), lam_d)
    assert all(np.cumsum(q_last)[d - 1] <= 1e-24 * q_last[-1] for d in range(1, 6))
    _, sel = pdb.select_top_q(q_last, 6, pdb.cost_tables(504.0, 6)[0])
    assert sel["S"] == [5] and sel["d"] == 1


def _monotone(values):
    return all(b >= a - 4.0 * EPS * max(abs(a), abs(b)) for a, b in zip(values, values[1:]))


def test_nested_plugin_information_monotone():
    g = _rng(2, 1)
    S = _spd(g, 8, 20.0)
    delta = g.standard_normal(8)
    lam, V = _desc_eigh(S)
    assert _monotone(np.cumsum(pdb.q_plugin(V.T @ delta, lam)).tolist())
    R, _ = np.linalg.qr(g.standard_normal((8, 8)))
    Sr, dr = R.T @ S @ R, R.T @ delta
    joint = [pdb.kl_mean(dr[:k], Sr[:k, :k]) for k in range(1, 9)]
    assert _monotone(joint) and math.isclose(joint[-1], pdb.kl_mean(delta, S), rel_tol=1e-10)
    q = np.array([4.0, 0.5, 0.25])
    assert not _monotone([float(q[[0]].sum()), float(q[[1, 2]].sum())])


def _exhaustive_best(q, cost):
    scored = []
    for d in range(1, len(q) + 1):
        for S in itertools.combinations(range(len(q)), d):
            scored.append((float(sum(q[j] for j in S)) / float(cost[d - 1]), d, S))
    vmax = max(v for v, _, _ in scored)
    winners = sorted((d, S) for v, d, S in scored if v == vmax)
    return vmax, winners[0][0], winners[0][1], len(winners)


def _forward_add(q, cost):
    order = sorted(range(len(q)), key=lambda j: (-q[j], j))
    best = None
    for d in range(1, len(q) + 1):
        S = tuple(sorted(order[:d]))
        v = float(sum(q[j] for j in S)) / float(cost[d - 1])
        if best is None or v > best[0]:
            best = (v, d, S)
    return best


def test_top_q_exhaustive_forward_exact_with_ties():
    g = _rng(3, 1)
    mix, aff = pdb.cost_tables(504.0, 12)
    costs = {"M": mix, "affine": aff, "d": np.arange(1.0, 13.0),
             "nonconcave": np.array([1.0, 1.9, 2.0, 3.5, 3.6, 5.0, 5.1, 7.0, 7.2, 9.0, 9.1, 11.5])}
    pool = np.array([0, 0, 1, 1, 2, 16, 32, 64, 64, 128, 256]) / 64.0
    ties = 0
    for trial in range(40):
        k = int(g.integers(1, 13))
        q = g.choice(pool, size=k) if trial % 2 else g.integers(0, 257, size=k) / 64.0
        for name, cost in costs.items():
            ex_v, ex_d, ex_S, count = _exhaustive_best(q, cost)
            _, sel = pdb.select_top_q(q, k, cost)
            got = (sel["V"], sel["d"], tuple(sel["S"]))
            assert got == (ex_v, ex_d, ex_S) == _forward_add(q, cost), (name, q.tolist(), got)
            assert sel["tie_broken"] == (count >= 2), (name, q.tolist(), count)
            ties += count >= 2
    assert ties > 0


def test_early_stop_greedy_not_equivalent():
    q, cost = np.array([1.0, 1.0, 1.0]), np.array([1.0, 2.5, 2.9])
    _, sel = pdb.select_top_q(q, 3, cost)
    _, ex_d, ex_S, _ = _exhaustive_best(q, cost)
    assert sel["d"] == ex_d == 3 and tuple(sel["S"]) == ex_S == (0, 1, 2)
    d, v = 1, q[0] / cost[0]
    while d < 3 and q[:d + 1].sum() / cost[d] > v:
        d, v = d + 1, q[:d + 1].sum() / cost[d]
    assert d == 1


def _rot(theta_deg):
    t = math.radians(theta_deg)
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


def test_rotation_joint_vs_marginal_spd_symmetry_energy(tiny_prep):
    S0 = np.diag([4.0, 1.0])
    S1 = _rot(45.0) @ S0 @ _rot(45.0).T
    A = np.linalg.solve(S0, S1)
    closed = 0.5 * (float(np.trace(A)) - float(np.linalg.slogdet(A)[1]) - 2.0)
    joint = pdb.kl_cov(S0, S1)
    assert abs(joint - 0.5625) <= 1e-12 and abs(closed - 0.5625) <= 1e-12
    r = np.diag(S1) / np.diag(S0)
    marg = float(pdb.cov_marginals(S0, S1).sum())
    assert abs(marg - 0.33936) <= 1e-4 and abs(marg - float((0.5 * (r - 1.0 - np.log(r))).sum())) <= 1e-15
    assert joint - marg > 0.2
    for theta in (15.0, 30.0, 45.0):
        St = _rot(theta) @ S0 @ _rot(theta).T
        assert abs(pdb.kl_cov(S0, St) - float(pdb.cov_marginals(S0, St).sum())) > 1e-3, theta
    assert (np.linalg.eigvalsh(S1) > 0.0).all() and abs(S1[0, 1] - 1.5) <= 1e-12
    asym = float(np.abs(S1 - S1.T).max())
    assert asym <= 4.0 * EPS * float(np.abs(S1).max())
    print(f"A5 measured max|S1 - S1^T| = {asym!r}")
    assert S0[0, 0] == 4.0 and abs(S1[0, 0] - 2.5) <= 1e-12 and joint > 0.0
    assert abs(float(tiny_prep[1]["C1"][0, 1])) > 1e-3
    assert abs(pdb.kl_cov(S0, S0)) <= 1e-15 and float(pdb.cov_marginals(S0, S0).sum()) == 0.0


def _t7_label_problems(sel):
    return [(ds, ik) for ds, ik in zip(sel.dataset_id, sel.info_kind)
            if not _na(ik) and (ds == "SYNTH_T7_EQUICORR") != ik.endswith("_T7_PROXY")]


def test_t7_information_labels_are_gaussian_proxies(sealed, tables, smoke_run, smoke_ctx, full_ctx):
    for tag, (manifest, frames) in sealed.items():
        sel, agg = frames["selection"], frames["aggregates"]
        assert (sel.dataset_id == "SYNTH_T7_EQUICORR").any() and not _t7_label_problems(sel), tag
        checks = agg[agg.metric_kind.isin(["GAUSS_FORMULA_CHECK", "GAUSS_PROXY_CHECK_T7"])]
        kinds = {ds: set(g.metric_kind) for ds, g in checks.groupby("dataset_id")}
        assert kinds == {"SYNTH_GAUSS_EQUICORR": {"GAUSS_FORMULA_CHECK"}, "SYNTH_T7_EQUICORR": {"GAUSS_PROXY_CHECK_T7"}}
        qi = {v for v in tables[tag]["T2"].q_info_type if not _na(v)}
        assert qi and all(v.endswith("_PROXY") for v in qi), (tag, qi)
        assert "EXACT_T_KL" not in json.dumps(manifest) + sel.to_csv(index=False)
    for ctx in (smoke_ctx, full_ctx):
        assert "GAUSSIAN_PROXY" in pf.build_entry(ctx, "mean_t7")["meta"]["tags"]
    bad = copy.deepcopy(smoke_run)
    sel = bad.frames["selection"]
    i = sel.index[(sel.dataset_id == "SYNTH_T7_EQUICORR") & sel.info_kind.notna()][0]
    sel.loc[i, "info_kind"] = "EXACT_T_KL"
    with pytest.raises(pdt.Refused) as exc:
        pdt.check_enums(bad.frames)
    assert exc.value.code == "ENUM_VIOLATION"
    text = sealed["SMOKE"][1]["selection"].copy()
    j = text.index[(text.dataset_id == "SYNTH_T7_EQUICORR") & (text.info_kind == "COV_GAUSS_POP_JOINT_T7_PROXY")][0]
    text.loc[j, "info_kind"] = "COV_GAUSS_POP_JOINT_EXACT"
    assert _t7_label_problems(text) == [("SYNTH_T7_EQUICORR", "COV_GAUSS_POP_JOINT_EXACT")]


def test_mixture_cost_unique_positive_root():
    gamma = 504.0
    A = math.log(gamma)
    for d in (1, 4, 20, 500):
        M = pdb.mixture_cost(d, gamma)
        x = M * A

        def g(v, d=d):
            return v - A - 0.5 * d * math.log1p(2.0 * v / d)

        vals = np.array([g(v) for v in np.linspace(4.0 * x / 2000.0, 4.0 * x, 2000)])
        signs = np.sign(vals)
        assert (np.diff(vals) > 0.0).all() and int((signs == 0.0).sum()) <= 1, d
        assert int((np.diff(signs[signs != 0.0]) != 0.0).sum()) == 1 and signs[0] < 0.0 < signs[-1], d
        assert abs(g(x)) <= 1e-12 * x and math.isfinite(M) and M > 1.0, d
        xf = A
        for _ in range(100000):
            nxt = A + 0.5 * d * math.log1p(2.0 * xf / d)
            done = abs(nxt - xf) <= 1e-15 * nxt
            xf = nxt
            if done:
                break
        assert math.isclose(xf, x, rel_tol=1e-12), d
    assert abs(pdb.mixture_cost(4, gamma) - 1.5696) <= 5e-5 and abs(pdb.mixture_cost(500, gamma) - 9.6427) <= 5e-5


BANNED_COST_LABELS = ("EXACT_ADD", "ARL0", "COV_EXACT_COST")


def test_mixture_cost_labelled_surrogate(sealed, smoke_run):
    for tag, (manifest, frames) in sealed.items():
        sel = frames["selection"]
        for col in ("info_kind", "cost_kind", "objective_kind", "claim_flag", "method"):
            assert not any(b in v for v in sel[col] for b in BANNED_COST_LABELS), (tag, col)
        assert not any(b in json.dumps(manifest["costs"]) for b in BANNED_COST_LABELS)
        mean_mix = sel[(sel.detector_family == pdb.MEAN)
                       & sel.objective_kind.isin(["MEAN_MIX_FLUID_SURROGATE", "EXANTE_QBAR_MIX_FLUID_SURROGATE"])]
        assert len(mean_mix) and set(mean_mix.cost_kind) == {"MIX_FLUID_SURROGATE"}, tag
        cov_mix = sel[(sel.detector_family == pdb.COV)
                      & sel.objective_kind.isin(["COV_JOINT_MIX_HEURISTIC", "COV_MARGINAL_MIX_DIAGNOSTIC"])]
        assert len(cov_mix) and set(cov_mix.cost_kind) == {"HEURISTIC_COST"}, tag
        assert all("HEURISTIC_COST" in _flags(v) for v in cov_mix.claim_flag), tag
    bad = copy.deepcopy(smoke_run)
    sel = bad.frames["selection"]
    sel.loc[sel.index[sel.cost_kind.notna()][0], "cost_kind"] = "EXACT_ADD"
    with pytest.raises(pdt.Refused) as exc:
        pdt.check_enums(bad.frames)
    assert exc.value.code == "ENUM_VIOLATION"


def test_v_surrogate_fixed_before_trials(sealed, ftiny):
    for tag, (manifest, frames) in sealed.items():
        M, C = manifest["costs"]["M"], manifest["costs"]["affine_values"]
        n = 0
        for r in frames["selection"].itertuples(index=False):
            if _na(r.I_objective) or _na(r.M_cost):
                continue
            I, d = float(r.I_objective), int(float(r.d))
            assert float(r.V_mix) == I / float(r.M_cost) and float(r.V_affine) == I / float(r.C_affine), r.selection_id
            assert float(r.M_cost) == M[d - 1] and float(r.C_affine) == C[d - 1], r.selection_id
            n += 1
        assert n > 0, tag
    a, b = ftiny["tiny"], ftiny["poison"]
    assert (a / "selection.csv").read_bytes() == (b / "selection.csv").read_bytes()
    assert (a / "aggregates.csv").read_bytes() != (b / "aggregates.csv").read_bytes()


def test_projection_equals_stored_transform(tiny_prep):
    cfg, prep = tiny_prep
    basis, nmax, bg = prep["basis"], cfg["nmax"], "SYNTH_GAUSS_EQUICORR"
    lam, V = basis["eigval"], basis["eigvec"]
    assert np.isfinite(lam).all() and (lam > 0.0).all()
    assert np.abs(V.T @ V - np.eye(V.shape[1])).max() <= 1e-12
    assert np.array_equal(prep["W"], V[:, :nmax] / np.sqrt(lam[:nmax]))
    Z, m = pdb.project(cfg, bg, "holdout_null", 3, prep["W"])
    for i in range(3):
        X = pdb.draw_path(cfg, bg, "holdout_null", i, cfg["H"])
        assert np.array_equal(Z[i], X @ prep["W"]) and np.array_equal(m[i], X.mean(axis=1))
    other = pdb.fit_basis(pdb.draw_path(cfg, bg, "centering", 0, cfg["T_fit"]))
    assert other["basis_hash"] != basis["basis_hash"]


def _criteria_problems(t1, nmax):
    probs = []
    for r in t1.itertuples(index=False):
        if _na(r.criteria):
            continue
        k, k90, kaiser = int(r.k), int(float(r.cpv90_k_full)), int(float(r.kaiser_count))
        parts = (["MP (corr.)"] if k == int(float(r.mp_count)) else []) + \
            (["CPV 90 %"] if k90 <= nmax and k == k90 else []) + \
            (["Kaiser corr. λ≥1"] if kaiser <= nmax and k == kaiser else [])
        want = " ; ".join(parts) if parts else "—"
        if r.criteria != want or "λ<1" in r.criteria:
            probs.append((r.row_id, r.criteria, want))
    return probs


def test_mp_kaiser_cpv_on_sealed_spectra_and_tables(sealed, tables):
    edge = (1.0 + math.sqrt(239.0 / 1000.0)) ** 2
    for tag, (manifest, frames) in sealed.items():
        nmax = int(manifest["config"]["nmax"])
        for (ds, bh), g in frames["spectra"].groupby(["dataset_id", "basis_hash"]):
            g = g.assign(kk=g.k.astype(int)).sort_values("kk")
            assert all(abs(float(v) / edge - 1.0) <= 4.0 * EPS for v in g.mp_edge), (tag, ds)
            assert all((f == "True") == (float(v) >= 1.0) for f, v in zip(g.kaiser_ge1, g.lambda_corr)), (tag, ds)
            assert all((f == "True") == (float(v) > float(e)) for f, v, e in zip(g.mp_above, g.lambda_corr, g.mp_edge))
            cpv = np.array([float(v) for v in g.cpv_lw])
            assert len(cpv) == 239 and (np.diff(cpv) >= 0.0).all() and abs(cpv[-1] - 1.0) <= 1e-12, (tag, ds)
            assert cpv[19] < 0.9 and set(g.cpv90_status) == {"CPV90_OUTSIDE_TOP20"}, (tag, ds)
        t1 = tables[tag]["T1"]
        assert not _criteria_problems(t1, nmax) and not any("λ<1" in v for v in t1.criteria), tag
        t3 = tables[tag]["T3"]
        rows = t3[(t3.method == "BASELINE_CPV90") & t3.dataset_id.isin(SYNTH)]
        assert len(rows), tag
        for r in rows.itertuples(index=False):
            assert (r.status, r.S, r.rmst, r.fpr, r.comparability) == (
                "CPV90_OUTSIDE_TOP20", "NaN", "NaN", "NaN", "NOT_COMPARABLE_OUTSIDE_TOP20"), (tag, r.row_id)
    pop = np.sort(np.linalg.eigvalsh(pdb.equicorrelation(239, 0.4)))[::-1]
    cpv14 = float(pop[:14].sum() / pop.sum())
    assert abs(cpv14 - 104.0 / 239.0) <= 1e-12 and abs(cpv14 - 0.435146) <= 5e-7
    t1 = tables["SMOKE"]["T1"].copy()
    i = t1.index[(t1.k == "14") & ~t1.criteria.isin(["NaN", ""])][0]
    t1.loc[i, "criteria"] = "CPV 90 %"
    assert _criteria_problems(t1, 20)


def _ref_loglik(z, s2):
    H, p = z.shape
    out = np.full((H, H), np.nan)
    for t in range(1, H + 1):
        for tau in range(1, t + 1):
            n = t - tau + 1
            seg = [math.fsum(z[tau - 1:t, j]) for j in range(p)]
            out[t - 1, tau - 1] = (-0.5 * p * math.log1p(n * s2)
                                   + s2 * math.fsum(v * v for v in seg) / (2.0 * (1.0 + n * s2)))
    return out


def _first(W, h, ge=True):
    hits = [t for t in range(len(W)) if (W[t] >= h if ge else W[t] > h)]
    return hits[0] + 1 if hits else -1


def _scan_paths(d, H=12):
    g = _rng(12, d)
    a = 1.5
    alt = np.array([[a if t % 2 == 0 else -a] * d for t in range(H)])
    alt[10] = 3.0 * a
    late = np.zeros((H, d))
    late[4:7] = 1.25
    late[7:] = 0.125
    return {"no_alarm": 0.1 * g.standard_normal((H, d)), "immediate": np.vstack([np.full((1, d), 5.0),
            0.1 * g.standard_normal((H - 1, d))]), "equal_maxima": alt, "nonzero_start": late}


def test_scan_reference_on_required_path_classes():
    s2 = 0.3
    for d in (1, 2, 4):
        for name, z in _scan_paths(d).items():
            ref = _ref_loglik(z, s2)
            np.testing.assert_allclose(pdb.segment_loglik(z, s2), ref, rtol=1e-12, atol=1e-12)
            ref_W = np.nanmax(ref, axis=1)
            W = pdb.scan_statistic(z[None], s2)[0][0]
            np.testing.assert_allclose(W, ref_W, rtol=1e-12, atol=1e-12)
            levels = np.unique(ref_W)
            hs = [levels[-1] + 1.0] + [0.5 * (lo + hi) for lo, hi in zip(levels[:-1], levels[1:])]
            for h in hs:
                Wh, first = pdb.scan_statistic(z[None], s2, h)
                f = int(first[0])
                assert f == _first(ref_W, h), (d, name, h)
                if f > 0:
                    assert np.array_equal(Wh[0, :f], W[:f]) and np.isnan(Wh[0, f:]).all()
            if name == "no_alarm":
                assert int(pdb.scan_statistic(z[None], s2, 50.0)[1][0]) == -1
            if name == "immediate":
                assert int(pdb.scan_statistic(z[None], s2, 0.5 * W[0])[1][0]) == 1
            if name == "equal_maxima":
                assert (W[:10] == W[0]).all() and W[10] > W[0]
                assert int(pdb.scan_statistic(z[None], s2, W[0])[1][0]) == 1 == _first(W, W[0])
                assert _first(W, W[0], ge=False) == 11
            if name == "nonzero_start":
                assert int(np.nanargmax(ref[6])) + 1 == 5
                assert int(np.nanargmax(pdb.segment_loglik(z, s2)[6])) + 1 == 5


def _windowed_W(z, s2, w):
    H, p = z.shape
    S = np.vstack([np.zeros((1, p)), np.cumsum(z, axis=0)])
    out = np.empty(H)
    for t in range(1, H + 1):
        tau = np.arange(max(1, t - w + 1), t + 1)
        n = t - tau + 1.0
        D = S[t] - S[tau - 1]
        out[t - 1] = np.max(-0.5 * p * np.log1p(n * s2) + s2 * (D * D).sum(axis=1) / (2.0 * (1.0 + n * s2)))
    return out


def test_scan_full_history_instrumentation(monkeypatch):
    widths, orig = [], pdb._scan_rows

    def spy(S, a, b, t):
        out = orig(S, a, b, t)
        widths.append((t, out.shape[1]))
        return out

    monkeypatch.setattr(pdb, "_scan_rows", spy)
    z = np.zeros((1, 250, 1))
    z[0, :100, 0] = 0.4
    W = pdb.scan_statistic(z, 0.01)[0][0]
    assert widths == [(t, t) for t in range(1, 251)]
    widths.clear()
    assert pdb.scan_alarms(np.zeros((300, 1)), 0.01, 1e9) == []
    assert max(w for _, w in widths) == 300 > 250
    assert abs(_windowed_W(z[0], 0.01, 250)[-1] - W[-1]) <= 1e-12 * abs(W[-1])
    assert _windowed_W(z[0], 0.01, 50)[-1] < W[-1] - 1.0


def test_scan_prefix_terms_and_ex_ante_s2(sealed, smoke_run):
    Z = _rng(14, 1).standard_normal((2, 7, 3))
    s2 = 0.37
    S, a, b = pdb._prefix(Z, s2)
    n = np.arange(1, 8, dtype=np.float64)
    assert (S[:, 0, :] == 0.0).all() and np.abs(S[:, 1:, :] - np.cumsum(Z, axis=1)).max() <= 1e-14
    np.testing.assert_allclose(a, -0.5 * 3 * np.log1p(n * s2), rtol=4.0 * EPS, atol=0.0)
    np.testing.assert_allclose(b, s2 / (2.0 * (1.0 + n * s2)), rtol=4.0 * EPS, atol=0.0)
    for bad in (0.0, -0.1, math.nan, math.inf):
        with pytest.raises(ValueError):
            pdb._prefix(Z, bad)
    for tag, (manifest, frames) in sealed.items():
        cal = frames["calibration"]
        sc = cal[~cal.s2.isin(["", "NaN"])]
        assert len(sc), tag
        for r in sc.itertuples(index=False):
            H, alpha, p = float(r.H), float(r.alpha), int(float(r.p))
            want = 2.0 * math.log(H / alpha) / (H * p)
            assert abs(float(r.s2) / want - 1.0) <= 4.0 * EPS and r.s2_rule == "2*ln(H/alpha)/(H*p)", r.null_calibration_id
        syn = cal[cal.dataset_id.isin(SYNTH)]
        assert (syn.groupby(["dataset_id", "detector_family", "S"]).null_calibration_id.nunique() == 1).all(), tag
        nmax = int(manifest["config"]["nmax"])
        spe = frames["spectra"][frames["spectra"].dataset_id == "SYNTH_GAUSS_EQUICORR"]
        lam = {int(k): float(v) for k, v in zip(spe.k, spe.lambda_lw)}
        beta = manifest["synthetic"]["backgrounds"]["SYNTH_GAUSS_EQUICORR"]["scenarios"]["C_residual_mean"]["beta_nonzero"]
        mu = np.zeros(nmax)
        for ax, v in beta.items():
            mu[int(ax) - 1] = float(v) / math.sqrt(lam[int(ax)])
        row = cal[(cal.dataset_id == "SYNTH_GAUSS_EQUICORR") & (cal.detector_family == pdb.MEAN)
                  & (cal.S == pdb.S_json(range(nmax)))].iloc[0]
        assert abs(float((mu ** 2).sum()) / nmax / float(row.s2) - 1.0) > 1e-3, tag
    assert pf.SPECS["mean"]["detector_family"] == pdb.MEAN == "MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM"
    bad = copy.deepcopy(smoke_run)
    cal = bad.frames["calibration"]
    cal.loc[cal.index[cal.detector_family == pdb.MEAN][0], "detector_family"] = "GLR_WINDOWED"
    with pytest.raises(pdt.Refused) as exc:
        pdt.check_enums(bad.frames)
    assert exc.value.code == "ENUM_VIOLATION"


def _check_calibration_recipe(cal, groups, agg):
    hold = agg[agg.metric_kind == "HOLDOUT_NULL_FPR"]
    n_ok = 0
    for r in cal[cal.status == "OK"].itertuples(index=False):
        g = groups[(r.null_calibration_id, "calibration")]
        maxima = g.stat_max.to_numpy(dtype=np.float64)
        n, alpha = int(float(r.n_cal)), float(r.alpha)
        assert len(maxima) == n and g.replicate.tolist() == list(range(n)), r.null_calibration_id
        assert pdb.array_sha256(maxima) == r.maxima_sha256, r.null_calibration_id
        rank = math.floor(Fraction(str(alpha)) * (n + 1)) - 1
        assert int(float(r.rank_r)) == rank, r.null_calibration_id
        b = float(np.sort(maxima)[n - rank - 1])
        h = b if r.alarm_rule == "GT" else float(np.nextafter(b, np.inf))
        assert float(r.threshold) == h, r.null_calibration_id
        assert int(float(r.calibration_alarms)) == int((maxima > b).sum()) <= rank, r.null_calibration_id
        digest = hashlib.sha256(np.ascontiguousarray(maxima).tobytes() + repr(float(r.threshold)).encode()).hexdigest()
        assert r.calibration_hash == digest, r.null_calibration_id
        if r.null_kind == "SYNTH_INDEPENDENT_PATHS":
            assert float(r.predictive_bound) == (rank + 1) / (n + 1), r.null_calibration_id
        else:
            assert _na(r.predictive_bound), r.null_calibration_id
        hr = hold[hold.null_calibration_id == r.null_calibration_id]
        assert len(hr) == 1, r.null_calibration_id
        hr = hr.iloc[0]
        ht = groups[(hr.metric_id, "holdout_null")]
        hn, halarms = int(float(hr.n)), int(ht.detected.sum())
        assert len(ht) == hn and int(float(hr.alarms)) == halarms and float(hr.fpr) == halarms / hn, hr.metric_id
        hmax = np.sort(ht.stat_max.to_numpy(dtype=np.float64))
        hrank = math.floor(Fraction(str(alpha)) * (hn + 1)) - 1
        assert float(hmax[hn - hrank - 1]) != b, r.null_calibration_id
        n_ok += 1
    return n_ok


def test_calibration_rank_recipe_and_data_flow(sealed):
    groups, _ = _trials_groups(SMOKE / "trials.csv")
    frames = sealed["SMOKE"][1]
    assert _check_calibration_recipe(frames["calibration"], groups, frames["aggregates"]) > 0


def _eprocess_problems(manifest, frames):
    cal, agg = frames["calibration"], frames["aggregates"]
    probs = [("anytime_valid", v) for v in cal.anytime_valid if v != "False"]
    probs += [("null_validity", v) for v in cal.null_validity if v not in (
        "EMPIRICAL_QUASI_LIKELIHOOD", "EMPIRICAL_ENERGY", "APPROXIMATE_D6_INSAMPLE_OVERLAPPING")]
    probs += [("label", name) for name, df in frames.items() if "EXACT_EPROCESS" in df.to_csv(index=False)]
    probs += [("label", "manifest")] if "EXACT_EPROCESS" in json.dumps(manifest) else []
    hold = agg[agg.metric_kind == "HOLDOUT_NULL_FPR"]
    finite = {i for i, v in zip(hold.null_calibration_id, hold.fpr) if not _na(v) and math.isfinite(float(v))}
    probs += [("holdout", i) for i in cal.loc[cal.status == "OK", "null_calibration_id"] if i not in finite]
    return probs


def test_no_exact_eprocess_claim_and_mandatory_holdout(sealed):
    for tag, (manifest, frames) in sealed.items():
        assert not _eprocess_problems(manifest, frames), tag
        assert (frames["calibration"].status == "OK").any(), tag
    manifest, frames = sealed["SMOKE"]
    bad = dict(frames, calibration=frames["calibration"].copy())
    bad["calibration"].loc[bad["calibration"].index[0], "anytime_valid"] = "True"
    assert _eprocess_problems(manifest, bad) == [("anytime_valid", "True")]


T1_KEY = ("dataset_id", "cohort_id", "event_id", "detector_family", "k")
PREFIX_MAP = (("rmst_prefix", "rmst"), ("rmst_prefix_lo", "rmst_lo"), ("rmst_prefix_hi", "rmst_hi"),
              ("fpr_prefix", "fpr_test_null"), ("fpr_prefix_lo", "fpr_lo"), ("fpr_prefix_hi", "fpr_hi"),
              ("metric_id_prefix", "metric_id"), ("null_metric_id_prefix", "null_metric_id"),
              ("selection_id_prefix", "selection_id"))
SHARED_IDS = ("config_hash", "basis_hash", "split_hash", "calibration_hash", "null_calibration_id")
T1_VALUES = ("rmst", "rmst_lo", "rmst_hi", "fpr_test_null", "fpr_lo", "fpr_hi")


def _prefix_identity(t1, t2, agg):
    t1i = {tuple(r[c] for c in T1_KEY): r for r in t1.to_dict("records")}
    aggi = {r["metric_id"]: r for r in agg.to_dict("records")}
    measured, blocked, bad = {}, 0, []
    for b in t2.to_dict("records"):
        a = t1i[tuple(b[c] for c in T1_KEY)]
        if (a["status"] == "OK" and a["execution"] == "EXECUTED" and b["status_prefix"] == "OK"
                and all(not _na(a[c]) and math.isfinite(float(a[c])) for c in T1_VALUES)):
            bad += [(b["row_id"], c2) for c2, c1 in PREFIX_MAP if b[c2] != a[c1]]
            bad += [(b["row_id"], c) for c in SHARED_IDS if b[c] != a[c]]
            alt, hold = aggi[a["metric_id"]], aggi[a["null_metric_id"]]
            for c1, src, col in (("rmst", alt, "rmst"), ("rmst_lo", alt, "rmst_lo"), ("rmst_hi", alt, "rmst_hi"),
                                 ("fpr_test_null", hold, "fpr"), ("fpr_lo", hold, "fpr_lo"), ("fpr_hi", hold, "fpr_hi")):
                if a[c1] != src[col]:
                    bad.append((a["row_id"], c1))
            block = (b["dataset_id"], b["event_id"], b["detector_family"], b["objective_kind"])
            measured[block] = measured.get(block, 0) + 1
        else:
            bad += [(b["row_id"], c2) for c2, c1 in (("metric_id_prefix", "metric_id"),
                                                     ("selection_id_prefix", "selection_id"),
                                                     ("status_prefix", "status")) if b[c2] != a[c1]]
            bad += [(b["row_id"], c2) for c2, c1 in PREFIX_MAP[:6] if not (_na(b[c2]) and _na(a[c1]))]
            if _na(a["na_reason"]) or _na(b["na_reason"]):
                bad.append((b["row_id"], "na_reason"))
            blocked += 1
    return measured, blocked, bad


def test_t1_t2_prefix_identity_measured_and_blocked(sealed, tables):
    for tag in ("SMOKE", "FULL"):
        t2 = tables[tag]["T2"]
        measured, blocked, bad = _prefix_identity(tables[tag]["T1"], t2, sealed[tag][1]["aggregates"])
        assert not bad, (tag, bad[:5])
        blocks = {(b.dataset_id, b.event_id, b.detector_family, b.objective_kind)
                  for b in t2.itertuples(index=False) if b.dataset_id in SYNTH}
        assert blocks and all(measured.get(k, 0) > 0 for k in blocks) and blocked > 0, tag
        print(f"B1 {tag}: measured={sum(measured.values())} blocked_NA={blocked} synthetic_blocks={len(blocks)}")


def test_identity_comparator_is_strict_text(sealed, tables):
    t1, t2, agg = tables["SMOKE"]["T1"], tables["SMOKE"]["T2"], sealed["SMOKE"][1]["aggregates"]
    a = t1[t1.status == "OK"].iloc[0]
    x = float(a.rmst)
    up, short = "%.17g" % float(np.nextafter(x, np.inf)), format(x, ".4g")
    assert float(up) != x and up != a.rmst and short != a.rmst
    for text in (up, short):
        t2m = t2.copy()
        j = t2m.index[t2m.metric_id_prefix == a.metric_id][0]
        t2m.loc[j, "rmst_prefix"] = text
        assert (t2m.loc[j, "row_id"], "rmst_prefix") in _prefix_identity(t1, t2m, agg)[2]


B3_FIELDS = ("selection_id", "S", "d", "I_objective", "V_mix", "metric_id", "detector_family")
T2_T3 = (("S_star", "S"), ("d_star", "d_star"), ("V_star", "V_star"), ("I_star", "I_star"),
         ("metric_id_subset", "metric_id"), ("rmst_selected", "rmst"), ("rmst_selected_lo", "rmst_lo"),
         ("rmst_selected_hi", "rmst_hi"), ("fpr_selected", "fpr"), ("fpr_selected_lo", "fpr_lo"),
         ("fpr_selected_hi", "fpr_hi"))


def _e2e3_mismatches(sel, nmax=20):
    s = sel[(sel.row_kind == "SELECTED") & (sel.method == "ORACLE_Q_MIX") & sel.dataset_id.isin(SYNTH)]
    e2 = [r for r in s.to_dict("records") if r["experiment"] == "E2" and _num(r["reservoir_k"]) == nmax]
    e3 = {(r["dataset_id"], r["event_id"]): r for r in s.to_dict("records") if r["experiment"] == "E3"}
    assert len(e2) == len(e3) == 4
    return [(r["dataset_id"], r["event_id"], f) for r in e2 for f in B3_FIELDS
            if r[f] != e3[(r["dataset_id"], r["event_id"])][f]]


def test_e2_k20_e3_oracle_mix_identity_selected_rows(sealed, tables):
    for tag in ("SMOKE", "FULL"):
        sel = sealed[tag][1]["selection"]
        assert not _e2e3_mismatches(sel), tag
        s = sel[(sel.row_kind == "SELECTED") & (sel.method == "ORACLE_Q_MIX") & sel.dataset_id.isin(SYNTH)]
        assert set(s.info_kind) <= {"MEAN_GAUSS_PLUGIN_LW", "MEAN_GAUSS_PLUGIN_LW_T7_PROXY"}, tag
        assert (s.I_objective == s.I_plugin_lw).all() and set(s.event_id) == {"A_market_mean", "C_residual_mean"}
        t2, t3 = tables[tag]["T2"], tables[tag]["T3"]
        n = 0
        for ds in SYNTH:
            for ev in ("A_market_mean", "C_residual_mean"):
                b = t2[(t2.dataset_id == ds) & (t2.event_id == ev) & (t2.k == "20")
                       & (t2.objective_kind == "MEAN_MIX_FLUID_SURROGATE")]
                c = t3[(t3.dataset_id == ds) & (t3.event_id == ev) & (t3.ordre == "2")]
                assert len(b) == 1 and len(c) == 1 and c.method.iloc[0] == "ORACLE_Q_MIX", (tag, ds, ev)
                b, c = b.iloc[0], c.iloc[0]
                assert [x for x, y in T2_T3 if b[x] != c[y]] == [], (tag, ds, ev)
                n += 1
        assert n == 4


def _refusal(run, mutate):
    bad = copy.deepcopy(run)
    mutate(bad.frames)
    with pytest.raises(pdt.Refused) as exc:
        pdt.validate_run(bad)
    return exc.value.code


def _setter(name, idx, col, value):
    def mutate(frames):
        frames[name].loc[idx, col] = value
    return mutate


def test_reuse_negative_witnesses(sealed, smoke_run):
    pdt.validate_run(copy.deepcopy(smoke_run))
    sel, text = smoke_run.frames["selection"], sealed["SMOKE"][1]["selection"]
    base = (sel.dataset_id == "SYNTH_GAUSS_EQUICORR") & (sel.row_kind == "SELECTED")
    e3 = sel.index[base & (sel.method == "ORACLE_Q_MIX") & (sel.experiment == "E3")
                   & (sel.event_id == "C_residual_mean")][0]
    assert text.loc[e3, "selection_id"] == sel.loc[e3, "selection_id"]
    axes = pdb.parse_S(sel.loc[e3, "S"], 20)
    assert len(axes) >= 2 and axes[0] >= 2 and axes[-1] <= 20
    compact = (",", ":")
    cases = {"unsorted": (json.dumps([axes[1], axes[0]] + axes[2:], separators=compact), {"INVALID_S"}),
             "base0": (json.dumps([0] + axes[1:], separators=compact), {"INVALID_S"}),
             "axis21": (json.dumps(axes[:-1] + [21], separators=compact), {"INVALID_S"}),
             "shifted": (pdb.S_json([a - 2 for a in axes]), {"L18_Q_CONTROL", "L17_E3_COPY"})}
    for name, (new, codes) in cases.items():
        assert new != sel.loc[e3, "S"]
        mutated = text.copy()
        mutated.loc[e3, "S"] = new
        assert ("SYNTH_GAUSS_EQUICORR", "C_residual_mean", "S") in _e2e3_mismatches(mutated), name
        code = _refusal(smoke_run, _setter("selection", e3, "S", new))
        assert code in codes, (name, code)
        print(f"B4 {name}: {sel.loc[e3, 'S']} -> {new}: {code}")
    fam = text.copy()
    fam.loc[e3, "detector_family"] = pdb.COV
    assert ("SYNTH_GAUSS_EQUICORR", "C_residual_mean", "detector_family") in _e2e3_mismatches(fam)
    assert _refusal(smoke_run, _setter("selection", e3, "detector_family", pdb.COV)) == "UNEXPECTED_ROW_STATE"
    e2_prefix = sel.index[base & (sel.method == "BASELINE_PREFIX") & (sel.experiment == "E2")
                          & (sel.event_id == "C_residual_mean")][0]
    assert _refusal(smoke_run, _setter("selection", e2_prefix, "detector_family", pdb.COV)) == "L16_PREFIX_IDENTITY"
    r = sel.index[base & (sel.method == "ORACLE_Q_MIX") & (sel.experiment == "E2") & (sel.reservoir_k == 5)
                  & (sel.event_id == "C_residual_mean")][0]
    agg = smoke_run.frames["aggregates"]
    other = agg[(agg.metric_kind == "HOLDOUT_NULL_FPR") & (agg.dataset_id == "SYNTH_GAUSS_EQUICORR")
                & (agg.null_calibration_id != sel.loc[r, "null_calibration_id"])].metric_id.iloc[0]
    code = _refusal(smoke_run, _setter("selection", r, "null_metric_id", other))
    assert code in {"FOREIGN_NULL", "ACCORD_MISMATCH"}, code
    print(f"B4 foreign null: {code}")


def test_cov_and_exante_outside_additive_equalities(sealed, tables, smoke_run):
    for tag in ("SMOKE", "FULL"):
        t3 = tables[tag]["T3"]
        rows = t3[t3.event_id.str.startswith("B_cov") & t3.ordre.isin(["1", "2"])]
        assert len(rows) and set(rows.status) == {"UNSUPPORTED"}, (tag, set(rows.status))
        sel = sealed[tag][1]["selection"]
        oracle_q = sel.method.str.startswith("ORACLE_Q_")
        assert not ((sel.detector_family == pdb.COV) & oracle_q).any(), tag
        assert not (sel.event_id.str.startswith("B_cov") & oracle_q).any(), tag
        ex = sel[(sel.method == "EXANTE_QBAR") & sel.dataset_id.isin(SYNTH)]
        assert len(ex) and set(ex.status) == {"UNSUPPORTED"}, tag
    sel = smoke_run.frames["selection"]
    i = sel.index[(sel.detector_family == pdb.COV) & (sel.method == "COV_JOINT_ORACLE")
                  & (sel.row_kind == "SELECTED")][0]
    assert _refusal(smoke_run, _setter("selection", i, "method", "ORACLE_Q_MIX")) == "UNEXPECTED_ROW_STATE"


def test_seed_plan_matches_manifests_and_role_groups_disjoint(sealed):
    for tag, (manifest, frames) in sealed.items():
        real = manifest["run_mode"] == "full" and manifest["dataset"] in ("real", "both")
        plan = pdb.seed_plan(manifest["config"], real)
        assert plan["sha256"] == manifest["rng"]["plan"]["sha256"], tag
        assert plan["n_keys"] == manifest["rng"]["plan"]["n_keys"] and pdb.seed_plan(manifest["config"], real) == plan
        other = copy.deepcopy(manifest["config"])
        other["seed"] = 43
        assert pdb.seed_plan(other, real)["sha256"] != plan["sha256"], tag
    tri = sealed["SMOKE"][1]["trials"]
    roles = {role: set(g.group_id) for role, g in tri.groupby("role")}
    assert set(roles) == {"calibration", "holdout_null", "alternative"}
    assert all(not roles[a] & roles[b] for a, b in itertools.combinations(roles, 2))


def test_thresholds_never_consume_holdout_or_alternative(ftiny):
    a, b = ftiny["tiny"], ftiny["poison"]
    for name in ("calibration.csv", "spectra.csv"):
        assert (a / name).read_bytes() == (b / name).read_bytes(), name
    assert (a / "aggregates.csv").read_bytes() != (b / "aggregates.csv").read_bytes()
    ta, tb = _text(a / "trials.csv"), _text(b / "trials.csv")
    for role, same in (("calibration", True), ("holdout_null", False), ("alternative", False)):
        ra = ta[ta.role == role].reset_index(drop=True)
        rb = tb[tb.role == role].reset_index(drop=True)
        assert ra.equals(rb) == same, role


def test_alternatives_paired_across_subsets(ftiny):
    cfg = _tiny_cfg()
    run = pdb.Run(cfg, "qa-31")
    expected = {}
    for bg in cfg["synthetic"]["backgrounds"]:
        prep = pdb.prepare_background(run, bg)
        for scen, (Z, _) in pdb.role_data(run, bg, prep)["alternative"].items():
            expected[pdb.array_sha256(Z)] = (bg, scen)
    calls = ftiny["alt_calls"]
    assert calls and all(h in expected for _, _, h in calls)
    by = {}
    for family, p, h in calls:
        by.setdefault(expected[h], set()).add((family, p))
    assert set(by) == set(expected.values()) and all(len(v) >= 2 for v in by.values()), by
    frames = _frames(ftiny["tiny"], ("aggregates", "trials"))
    tri, agg = frames["trials"], frames["aggregates"]
    reps = tri[tri.role == "alternative"].groupby("group_id").replicate.agg(lambda s: sorted(int(x) for x in s))
    assert len(reps) and all(v == list(range(cfg["n_alt"])) for v in reps)
    alt = agg[agg.metric_kind == "ALT_RMST"]
    assert set(alt.time_origin) == {"ONSET_ALIGNED"} and set(alt.event_window_id) == {"SYNTH_ONSET_ALIGNED"}


def _check_horizon_rmst(agg, groups):
    n_alt = n_hold = 0
    rows = agg[(agg.status == "OK") & (agg.execution == "EXECUTED")
               & agg.metric_kind.isin(["ALT_RMST", "HOLDOUT_NULL_FPR"])]
    for r in rows.itertuples(index=False):
        assert float(r.H) == 250.0, r.metric_id
        role = "alternative" if r.metric_kind == "ALT_RMST" else "holdout_null"
        g = groups[(r.metric_id, role)]
        n = int(float(r.n))
        assert len(g) == n and g.replicate.tolist() == list(range(n)), r.metric_id
        fh, ct, det = g.first_hit.to_numpy(), g.censored_time.to_numpy(), g.detected.to_numpy(dtype=bool)
        assert (det == (fh > 0)).all() and (ct == np.where(fh > 0, fh, 250)).all(), r.metric_id
        k = int(det.sum())
        assert int(float(r.alarms)) == k, r.metric_id
        if role == "alternative":
            assert float(r.rmst) == float(np.asarray(ct, dtype=np.float64).mean()), r.metric_id
            assert float(r.det_rate) == k / n and abs(float(r.det_rate) + float(r.censored_share) - 1.0) <= 1e-15
            n_alt += 1
        else:
            assert float(r.fpr) == k / n, r.metric_id
            n_hold += 1
    return n_alt, n_hold


def test_horizon_rmst_censoring_on_sealed_trials(sealed):
    groups, _ = _trials_groups(SMOKE / "trials.csv")
    agg = sealed["SMOKE"][1]["aggregates"]
    n_alt, n_hold = _check_horizon_rmst(agg, groups)
    assert n_alt > 0 and n_hold > 0
    print(f"C4 SMOKE: ALT_RMST={n_alt} HOLDOUT_NULL_FPR={n_hold}")
    key = next(k for k, g in groups.items() if k[1] == "alternative" and (~g.detected).any())
    g = groups[key].copy()
    g.loc[g.index[~g.detected][0], "censored_time"] = 249
    with pytest.raises(AssertionError):
        _check_horizon_rmst(agg, {**groups, key: g})


def test_continuous_statistic_not_reset_at_onset():
    dates = np.arange(np.datetime64("2020-01-01"), np.datetime64("2021-06-30"))
    dates = dates[np.is_busday(dates)]
    oi = int(np.searchsorted(dates, np.datetime64("2020-02-24")))
    ei = int(np.searchsorted(dates, np.datetime64("2020-03-23"), side="right")) - 1
    s2, h = 0.3, 3.0
    args = (s2, h, "2020-02-24", "2020-03-23", 250, pdb.CONTINUOUS, "FAKE_DATED_TEST")
    z = np.zeros((len(dates), 1))
    z[oi - 10:] = 0.5
    r = pdb.evaluate_real_path(z, dates, *args)
    continuous = [a for a in pdb.scan_alarms(z, s2, h) if a >= oi][0] - oi + 1
    restarted = pdb.scan_alarms(z[oi:], s2, h)[0] + 1
    assert r["pre_onset_alarms"] == 0 and r["post_onset_delay_h250"] == continuous < restarted
    assert continuous > ei - oi + 1 and not r["detected_during_event"] and r["event_censored"] and r["post_event_alarm"]
    z[5] = 6.0
    r = pdb.evaluate_real_path(z, dates, *args)
    assert r["pre_onset_alarms"] == 1 and json.loads(r["alarm_dates"]).count(str(dates[5])) == 1
    assert json.loads(r["pre_onset_alarm_dates"]) == [str(dates[5])] and not r["detected_during_event"]
    print(f"C5 continuous delay {continuous} < restarted-at-onset delay {restarted}; event sessions {ei - oi + 1}")


def test_real_split_metadata_and_cohort_disjointness(sealed):
    cfg = pdb.load_config(pdb.CONFIG, "smoke")
    derived = REPO / cfg["real"]["derived_dir"]
    expected = pdb.manifest_hashes(cfg)
    for name in ("splits.yaml", "dates.npy"):
        assert pdb.file_sha256(derived / name) == expected[name], name
    splits = yaml.safe_load((derived / "splits.yaml").read_text())
    seg = splits["segments"]
    assert (str(seg["calib"]["first_day"]), str(seg["calib"]["last_day"])) == ("2016-04-07", "2019-12-31")
    assert splits["embargo_trading_days"] == 65 and str(seg["monitor"]["first_day"]) == "2020-04-06"
    dates = np.load(derived / "dates.npy", allow_pickle=False).astype("datetime64[D]")
    a, b = segment_rows(dates, seg["calib"])
    assert b - a == 941 == cfg["real"]["expected_calib_rows"]
    assert dates[dates >= np.datetime64("2020-01-01")][0] == np.datetime64("2020-01-02")
    defs = pdb.cohort_definitions(cfg, splits, dates)
    std, retro = defs["cohort_standard_embargo"], defs["cohort_retrospective_covid"]
    assert std["events"]["COVID_2020"]["status"] == "NOT_EVALUABLE_STANDARD_SPLIT" and std["embargo_after_2019"] == 65
    assert std["claim_scope"] == "REAL_STANDARD_SPLIT"
    assert retro["monitor_armed_from"] == "2020-01-02" and retro["claim_scope"] == "REAL_RETROSPECTIVE_EXPLORATORY"
    assert retro["embargo_after_2019"] == 0
    assert (retro["events"]["COVID_2020"]["onset"], retro["events"]["COVID_2020"]["end"]) == ("2020-02-24", "2020-03-23")
    for tag, (manifest, frames) in sealed.items():
        for name in ("selection", "aggregates"):
            real = frames[name][frames[name].dataset_id == "D3_239"]
            ids = {c: {f: {v for v in real.loc[real.cohort_id == c, f] if not _na(v)}
                       for f in ("selection_id", "metric_id", "split_hash", "null_calibration_id") if f in real}
                   for c in ("cohort_standard_embargo", "cohort_retrospective_covid")}
            assert all(not ids["cohort_standard_embargo"][f] & ids["cohort_retrospective_covid"][f]
                       for f in ids["cohort_standard_embargo"]), (tag, name)
            assert ids["cohort_standard_embargo"]["metric_id"] and ids["cohort_retrospective_covid"]["metric_id"]


def test_fake_confirmatory_status_rejected(smoke_run):
    sel, agg = smoke_run.frames["selection"], smoke_run.frames["aggregates"]
    retro = sel.index[sel.cohort_id == "cohort_retrospective_covid"]
    std_covid = sel.index[(sel.cohort_id == "cohort_standard_embargo") & (sel.event_id == "COVID_2020")]
    real_agg = agg.index[agg.metric_kind == "REAL_EVENT_PATH"]
    shared = sel.index[sel.selection_id == sel.loc[retro[0], "selection_id"]]

    def scope(f):
        f["selection"].loc[retro, "claim_scope"] = "REAL_STANDARD_SPLIT"

    def executed(f):
        f["aggregates"].loc[real_agg[0], "execution"] = "EXECUTED"
        f["aggregates"].loc[real_agg[0], "rmst"] = 5.0

    def covid(f):
        f["selection"].loc[std_covid, "status"] = "BLOCKED_PRE_J4"

    def metric(f):
        f["selection"].loc[shared, "metric_id"] = sel.loc[std_covid[0], "metric_id"]

    cases = {"retrospective scope relabelled standard": (scope, "COHORT_MISSING"),
             "MAIN_TEST_VALID status": (_setter("selection", retro[0], "status", "MAIN_TEST_VALID"), "ENUM_VIOLATION"),
             "executed real path with rmst": (executed, "REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2"),
             "standard Covid relabelled BLOCKED_PRE_J4": (covid, "COHORT_MISSING"),
             "metric_id shared across cohorts": (metric, "COHORT_ID_SHARED")}
    for name, (mutate, want) in cases.items():
        assert _refusal(smoke_run, mutate) == want, name


C8_ALLOWED = ("run_fingerprint", "config_hash", "null_id", "null_calibration_id", "selection_id", "metric_id",
              "null_metric_id")


def _id_integrity(frames):
    sel, agg, cal, tri = frames["selection"], frames["aggregates"], frames["calibration"], frames["trials"]
    agg_ids, cal_ids = set(agg.metric_id), set(cal.null_calibration_id)
    probs = [(c, v) for c, pool in (("metric_id", agg_ids), ("null_metric_id", agg_ids),
                                    ("null_calibration_id", cal_ids)) for v in sel[c] if not _na(v) and v not in pool]
    counts = tri[tri.role == "calibration"].groupby("group_id").size()
    probs += [("trials", r.null_calibration_id) for r in cal[cal.status == "OK"].itertuples(index=False)
              if int(counts.get(r.null_calibration_id, 0)) != int(float(r.n_cal))]
    return probs


def _real_rows(df):
    out = df[df.dataset_id == "D3_239"].drop(columns=[c for c in C8_ALLOWED if c in df.columns])
    return out.sort_values(list(out.columns)).reset_index(drop=True)


def test_post2019_rows_never_reach_fit_thresholds_stress(ffake):
    a, b = ffake["a"], ffake["b"]
    ca, cb = copy.deepcopy(a["cfg"]), copy.deepcopy(b["cfg"])
    assert ca["real"]["derived_dir"] != cb["real"]["derived_dir"]
    for c in (ca, cb):
        del c["real"]["derived_dir"], c["real"]["manifest"]
    assert ca == cb
    ia, ib = a["manifest"]["identity"], b["manifest"]["identity"]
    diff = {k for k in set(ia) | set(ib) if ia.get(k) != ib.get(k)}
    assert {"inputs", "input_hash"} <= diff <= {"inputs", "input_hash", "config_hash"}, diff
    assert set(ia["inputs"]) == set(ib["inputs"])
    assert {n for n in ia["inputs"] if ia["inputs"][n] != ib["inputs"][n]} == {"ret_wide.npy", "MANIFEST.json"}
    for name in ("spectra", "calibration", "selection"):
        ra, rb = _real_rows(a["frames"][name]), _real_rows(b["frames"][name])
        assert len(ra) and ra.equals(rb), name
    ma = {k: v for k, v in a["manifest"]["real"].items() if k != "files"}
    mb = {k: v for k, v in b["manifest"]["real"].items() if k != "files"}
    assert ma == mb and ma["calib"]["rows"] == a["cfg"]["real"]["expected_calib_rows"]
    assert a["manifest"]["real"]["files"]["ret_wide.npy"] != b["manifest"]["real"]["files"]["ret_wide.npy"]
    for run in (a, b):
        assert not _id_integrity(run["frames"])
    panel = pdb.read_pre2020_panel(a["cfg"], pdb.manifest_hashes(a["cfg"]))
    c0, c1 = segment_rows(panel["days"], panel["splits"]["segments"]["calib"])
    X = np.ascontiguousarray(panel["X"][c0:c1])
    assert pdb.fit_basis(X)["basis_hash"] == ma["basis_hash"]
    X[0, 0] += 1e-3
    assert pdb.fit_basis(X)["basis_hash"] != ma["basis_hash"]


def test_stress_library_historical_and_qbar_not_oracle(sealed, ffake):
    cfg = pdb.load_config(pdb.CONFIG, "full")
    for lo, hi in cfg["real"]["stress_windows"].values():
        assert np.datetime64("2008-01-01") <= np.datetime64(lo) <= np.datetime64(hi) <= np.datetime64("2011-12-31")
    days = np.arange(np.datetime64("2019-06-03"), np.datetime64("2022-12-31"))
    days = days[np.is_busday(days)]
    X = _rng(9, 1).standard_normal((len(days), 5))
    basis = pdb.fit_basis(X)
    for win in ({"S2020": ["2020-02-24", "2020-03-23"]}, {"S2022": ["2022-01-03", "2022-06-30"]}):
        with pytest.raises(pdb.IncompleteWindow):
            pdb.stress_library(X, days, win, X.mean(axis=0), basis, 3)
    frames_all = [frames for _, frames in sealed.values()] + [ffake["a"]["frames"]]
    for frames in frames_all:
        ex = frames["selection"][frames["selection"].method == "EXANTE_QBAR"]
        assert len(ex) and set(ex.oracle_input) == {"STRESS_LIBRARY_2008_2011"}
        assert not any(f.startswith("ORACLE") or f == "EX_POST_ORACLE" for v in ex.claim_flag for f in _flags(v))
    cfg_a = ffake["a"]["cfg"]
    base = pdb.run_real(pdb.Run(cfg_a, "qa-31"), {n: [] for n in pdb.TABLES})
    shifted = copy.deepcopy(cfg_a)
    shifted["real"]["events"] = {"COVID_2020": {"onset": "2020-03-02", "end": "2020-04-14"},
                                 "STYLE_2022H1": {"onset": "2022-02-01", "end": "2022-05-31"}}
    moved = pdb.run_real(pdb.Run(shifted, "qa-31"), {n: [] for n in pdb.TABLES})
    assert moved["stress"]["qbar"] == base["stress"]["qbar"] == ffake["a"]["manifest"]["real"]["stress_library"]["qbar"]
    assert moved["exante"] == base["exante"] is not None
    mix = pdb.cost_tables(504.0, 3)[0]
    stress_S = pdb.select_top_q(np.array([4.0, 0.25, 0.0]), 3, mix)[1]["S"]
    oracle_S = pdb.select_top_q(np.array([0.0, 0.25, 4.0]), 3, mix)[1]["S"]
    assert stress_S != oracle_S


def _oracle_label_problems(sel):
    probs = []
    for r in sel.to_dict("records"):
        flags, oi, sid = _flags(r["claim_flag"]), r["oracle_input"], r["selection_id"]
        if (oi == "INJECTED_DELTA") != ("ORACLE_INJECTED_DELTA" in flags):
            probs.append((sid, "INJECTED_DELTA"))
        if (oi == "TRUE_SIGMA1") != ("ORACLE_TRUE_SIGMA1" in flags):
            probs.append((sid, "TRUE_SIGMA1"))
        if oi == "TRUE_SIGMA1" and not (r["detector_family"] == pdb.COV
                                       and r["method"] in ("COV_JOINT_ORACLE", "COV_MARGINAL_DIAGNOSTIC")):
            probs.append((sid, "TRUE_SIGMA1 outside COV oracle diagnostics"))
        if (oi == "EXPOST_EVENT_DELTA") != ("EX_POST_ORACLE" in flags):
            probs.append((sid, "EX_POST_ORACLE"))
        if (r["event_id"] == "STYLE_2022H1") != ("RETROSPECTIVE_DIAGNOSTIC" in flags):
            probs.append((sid, "RETROSPECTIVE_DIAGNOSTIC"))
    return probs


def test_oracle_labels_and_sigma1_absent_from_detector(sealed, tiny_prep):
    for tag, (manifest, frames) in sealed.items():
        sel = frames["selection"]
        assert not _oracle_label_problems(sel), (tag, _oracle_label_problems(sel)[:5])
        assert (sel.event_id == "STYLE_2022H1").any() and (sel.oracle_input == "TRUE_SIGMA1").any(), tag
    cfg, prep = tiny_prep
    Z, m = pdb.project(cfg, "SYNTH_GAUSS_EQUICORR", "holdout_null", 4, prep["W"])
    blind = dict(prep, C1=np.full_like(prep["C1"], np.nan), M=np.full_like(prep["M"], np.nan),
                 scenarios={k: {**v, "mu": np.full_like(v["mu"], np.nan)} if "mu" in v else v
                            for k, v in prep["scenarios"].items()})
    for family, S in ((pdb.COV, [0, 2]), (pdb.MEAN, [1, 3, 4])):
        assert np.array_equal(pdb._detector(cfg, prep, family, S)[0](Z, m), pdb._detector(cfg, blind, family, S)[0](Z, m))
    sel = sealed["SMOKE"][1]["selection"].copy()
    i = sel.index[sel.event_id == "STYLE_2022H1"][0]
    sel.loc[i, "claim_flag"] = json.dumps(sorted(_flags(sel.loc[i, "claim_flag"]) - {"RETROSPECTIVE_DIAGNOSTIC"}) or
                                          ["NONE"], separators=(",", ":"))
    assert (sel.loc[i, "selection_id"], "RETROSPECTIVE_DIAGNOSTIC") in _oracle_label_problems(sel)


REAL_METRICS = ("n", "alarms", "fpr", "rmst", "det_rate", "censored_share", "time_to_alarm_during_event",
                "post_onset_delay_h250")
REAL_TABLE_COLS = {"T1": ("rmst", "fpr_test_null", "n_alt", "n_eval"),
                   "T2": ("rmst_prefix", "fpr_prefix", "rmst_selected", "fpr_selected", "n_alt", "n_eval"),
                   "T3": ("rmst", "fpr", "n_alt", "n_eval")}


def _real_na_problems(agg):
    real = agg[agg.dataset_id == "D3_239"]
    probs = [(r["metric_id"], "status") for r in real.to_dict("records")
             if r["status"] not in REAL_STATUSES or r["execution"] != "NOT_EXECUTED"]
    probs += [(r["metric_id"], c) for r in real.to_dict("records") for c in REAL_METRICS if not _na(r[c])]
    return probs, len(real)


def test_real_rows_na_never_zero_or_target(sealed, tables, ftiny, ffake, smoke_run):
    for tag, (manifest, frames) in sealed.items():
        probs, n = _real_na_problems(frames["aggregates"])
        assert n and not probs, (tag, probs[:5])
        real_sel = frames["selection"][frames["selection"].dataset_id == "D3_239"]
        assert len(real_sel) and set(real_sel.status) <= REAL_STATUSES, tag
        for t, cols in REAL_TABLE_COLS.items():
            df = tables[tag][t]
            rr = df[df.dataset_id == "D3_239"]
            if t != "T3":
                assert len(rr), (tag, t)
            assert all(_na(v) for c in cols for v in rr[c]) and not any(_na(v) for v in rr.na_reason), (tag, t)
    agg = _text(ftiny["missing"] / "aggregates.csv")
    probs, n = _real_na_problems(agg)
    assert n and not probs and set(agg[agg.dataset_id == "D3_239"].status) == {"DATA_UNAVAILABLE"}
    for run in ffake.values():
        cal = run["frames"]["calibration"]
        d6 = cal[cal.dataset_id == "D3_239"]
        assert len(d6) and set(d6.guarantee_basis) == {"NOT_ESTABLISHED_HISTORICAL_WINDOWS"}
        assert all(_na(v) for v in d6.predictive_bound)
        probs, n = _real_na_problems(run["frames"]["aggregates"])
        assert n and not probs
    real_agg = smoke_run.frames["aggregates"].index[smoke_run.frames["aggregates"].metric_kind == "REAL_EVENT_PATH"]
    assert _refusal(smoke_run, _setter("aggregates", real_agg[0], "rmst", 0.0)) == "REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2"


TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}")
ABS_RE = re.compile(r"(?:^|[\s\"'=:,\[])(?:/home/|/tmp/|/Users/|/root/|/var/|/mnt/)")


def _leaks(text):
    return TIME_RE.findall(text) + ABS_RE.findall(text)


def _all_keys(obj):
    if isinstance(obj, dict):
        return [k for k in obj] + [x for v in obj.values() for x in _all_keys(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in _all_keys(v)]
    return []


def test_reproducibility_hashes_exclude_time_and_paths(sealed, ftiny):
    runs = {"SMOKE": (sealed["SMOKE"][0], SMOKE, CSV_NAMES + ("trials",)), "FULL": (sealed["FULL"][0], FULL, CSV_NAMES),
            "F-tiny": (json.loads((ftiny["tiny"] / "manifest.json").read_text()), ftiny["tiny"],
                       CSV_NAMES + ("trials",))}
    for tag, (manifest, run_dir, names) in runs.items():
        ident = manifest["identity"]
        assert "provenance" not in ident and "provenance" in manifest, tag
        assert not _leaks(pdb.canon(ident)), (tag, _leaks(pdb.canon(ident))[:3])
        keys = " ".join(str(k).lower() for k in _all_keys(ident))
        assert not any(w in keys for w in ("time", "second", "elapsed", "duration", "wall", "rss")), tag
        for name in names:
            assert not _leaks((run_dir / f"{name}.csv").read_text()), (tag, name)
    planted = dict(sealed["SMOKE"][0]["identity"], built="2026-11-06T12:00:00Z", where="/home/user/run")
    assert len(_leaks(pdb.canon(planted))) == 2


def test_sealed_identity_recomputes_with_current_code(sealed):
    assert pdb.file_sha256(FULL / "manifest.json") == FULL_MANIFEST_SHA
    for tag, run_dir in (("SMOKE", SMOKE), ("FULL", FULL)):
        manifest = sealed[tag][0]
        ident = manifest["identity"]
        assert hashlib.sha256(pdb.canon(ident).encode()).hexdigest() == manifest["run_fingerprint"], tag
        assert pdb.identity_block(manifest["config"], [REPO / p for p in ident["inputs"]]) == ident, tag
        for name, meta in manifest["outputs"].items():
            if (run_dir / name).exists():
                assert pdb.file_sha256(run_dir / name) == meta["sha256"], (tag, name)
            else:
                assert (tag, name) == ("FULL", "trials.csv")


SERIES_COL = {"CPV": ("T1", "cpv_lw"), "V_prefix": ("T2", "V_prefix"), "V_selected": ("T2", "V_star"),
              "RMST_prefix": ("T1", "rmst"), "RMST_selected": ("T2", "rmst_selected"), "RMST_energy": ("T3", "rmst")}


def _trace_problems(src, tabs, run_frames):
    lin = {(r["table"], r["row_id"], r["column"]): r for r in tabs["lineage"].to_dict("records")}
    rows = {t: {r["row_id"]: r for r in tabs[t].to_dict("records")} for t in ("T1", "T2", "T3")}
    index = {name: {tuple(r[k] for k in pdb.PRIMARY_KEYS[name]): r for r in run_frames[name].to_dict("records")}
             for name in ("spectra", "selection", "calibration", "aggregates")}
    agg = index["aggregates"]
    probs, ks = [], {}
    for r in src.to_dict("records"):
        series = r["series"]
        if series not in SERIES_COL:
            continue
        if series != "RMST_energy":
            ks.setdefault(series, set()).add(int(float(r["k"])))
        if _na(r["y"]):
            continue
        table, col = SERIES_COL[series]
        lr = lin.get((table, r["row_id"], col))
        if r["table"] != table or lr is None or lr["kind"] != "SOURCE":
            probs.append((series, r["k"], "lineage"))
            continue
        want = json.loads(lr["source_key"])
        name = lr["source_file"][:-4]
        key = tuple("NaN" if want[k] is None else str(want[k]) for k in pdb.PRIMARY_KEYS[name])
        cell = rows[table][r["row_id"]][col]
        if index[name][key][lr["source_column"]] != cell:
            probs.append((series, r["k"], "runner"))
        if float(r["y"]) != float(cell):
            probs.append((series, r["k"], "y"))
        if series.startswith("RMST"):
            a, h = agg.get((r["metric_id"],)), agg.get((r["null_metric_id"],))
            if a is None or (a["metric_kind"], a["status"], a["execution"]) != ("ALT_RMST", "OK", "EXECUTED"):
                probs.append((series, r["k"], "alt"))
            if h is None or h["metric_kind"] != "HOLDOUT_NULL_FPR" or float(r["null_fpr"]) != float(h["fpr"]):
                probs.append((series, r["k"], "null_fpr"))
    probs += [(s, "k_domain") for s, k in ks.items() if k != set(range(1, 21))]
    return probs


def test_figure_points_trace_to_aggregates(sealed, tables):
    for tag, fig_dir in (("SMOKE", FIG_SMOKE_FIX), ("FULL", FIG_FULL_FIX)):
        assert pf.verify_figures_dir(fig_dir), fig_dir
        n = 0
        for stem in ("Figure_1_mean", "Figure_1_mean_t7", "Figure_1_cov"):
            src = _text(fig_dir / f"{stem}_source.csv")
            probs = _trace_problems(src, tables[tag], sealed[tag][1])
            assert not probs, (tag, stem, probs[:5])
            n += int((~src.y.isin(["NaN", ""])).sum())
        assert n > 0
        print(f"D3 {tag}: {n} finite plotted values traced to SOURCE runner cells")
    src = _text(FIG_FULL_FIX / "Figure_1_mean_source.csv")
    i = src.index[(src.series == "RMST_prefix") & ~src.null_fpr.isin(["NaN", ""])
                  & (src.null_fpr.map(_num) != 0.05)][0]
    src.loc[i, "null_fpr"] = "0.05"
    assert any(p[2] == "null_fpr" for p in _trace_problems(src, tables["FULL"], sealed["FULL"][1]))


def test_cov_figure_exploratory_effective_labels(full_renders, tables, sealed):
    cov, mean = full_renders["cov"], full_renders["mean"]
    tag = "COV_SURROGATE_EXPLORATORY"
    assert tag in cov["entry"]["meta"]["tags"] and tag in cov["title"]
    assert tag not in mean["entry"]["meta"]["tags"] and tag not in mean["title"]
    assert all(pf.SMOKE_BANNER in pf.SPECS[k]["tags"] for k in ("mean", "mean_t7", "cov"))
    assert all(pf.SMOKE_BANNER not in r["entry"]["meta"]["tags"] and pf.SMOKE_BANNER not in r["title"]
               for r in (cov, mean))
    assert "EXPLORATORY HEURISTIC" in cov["ylabel_right"] and any(pf.H5_PHRASE in t for t in cov["texts"])
    lin = {(r["table"], r["row_id"], r["column"]): r for r in tables["FULL"]["lineage"].to_dict("records")}
    sel = {tuple(r[k] for k in pdb.PRIMARY_KEYS["selection"]): r
           for r in sealed["FULL"][1]["selection"].to_dict("records")}
    src = cov["entry"]["source"]
    n = 0
    for r in src[src.series.isin(["V_prefix", "V_selected"]) & src.y.notna()].to_dict("records"):
        lr = lin[("T2", r["row_id"], SERIES_COL[r["series"]][1])]
        assert lr["source_file"] == "selection.csv" and lr["source_column"] != "I_cov_marginal_sum"
        want = json.loads(lr["source_key"])
        row = sel[tuple("NaN" if want[k] is None else str(want[k]) for k in pdb.PRIMARY_KEYS["selection"])]
        assert row["info_kind"].startswith("COV_GAUSS_POP_JOINT_") and row["I_objective"] == row["I_cov_joint"]
        assert float(row[lr["source_column"]]) == r["y"]
        n += 1
    assert n > 0


def test_annotations_follow_values_and_status(full_ctx, full_renders):
    entry = pf.build_entry(full_ctx, "mean_t7")
    src = pd.read_csv(io.StringIO(pf.save_fair_csv_text(entry["source"])), float_precision="round_trip")
    cpv = src.series == "CPV"
    src.loc[cpv, "y"] = np.where(src.loc[cpv, "k"] >= 14, 0.95, 0.5)
    src.loc[src.series == "RMST_prefix", "null_fpr"] = 0.0123
    out = _render(entry, src, dict(entry["meta"], cpv90_k_full=14, cpv90_status="CPV90_IN_TOP20"))
    joined = " | ".join(out["texts"])
    assert "CPV ≥ 90 % at k = 14" in joined and "CPV ≥ 90 % at k = 7" not in joined and "not reached" not in joined
    assert "prefix [0.0123, 0.0123]" in joined
    base = " | ".join(full_renders["mean"]["texts"])
    assert "FPR250: prefix [" in base and "prefix [0.0123, 0.0123]" not in base
    assert "CPV90 not reached within top 20 (k90_full = " in base


def test_full2000_trials_read_only(sealed):
    raw = os.environ.get(TRIALS_ENV)
    if not raw or not Path(raw).is_file():
        pytest.skip(f"BLOCKED_DATA_UNAVAILABLE: {TRIALS_ENV} unset or path absent")
    path = Path(raw)
    manifest, frames = sealed["FULL"]
    meta = manifest["outputs"]["trials.csv"]
    assert not path.is_symlink() and path.stat().st_size == TRIALS_BYTES == meta["bytes"]
    assert pdb.file_sha256(path) == TRIALS_SHA == meta["sha256"]
    groups, tri = _trials_groups(path)
    assert len(tri) == TRIALS_ROWS == meta["rows"] and list(tri.columns) == pdb.COLUMNS["trials"]
    cal, agg = frames["calibration"], frames["aggregates"]
    ok_cal = set(cal.loc[cal.status == "OK", "null_calibration_id"])
    executed = agg[(agg.status == "OK") & (agg.execution == "EXECUTED")]
    want = ({(i, "calibration") for i in ok_cal}
            | {(m, "alternative") for m in executed.loc[executed.metric_kind == "ALT_RMST", "metric_id"]}
            | {(m, "holdout_null") for m in executed.loc[executed.metric_kind == "HOLDOUT_NULL_FPR", "metric_id"]})
    assert set(groups) == want
    print(f"G1 inventory: groups={len(groups)} rows={len(tri)} by_role={tri.groupby('role').size().to_dict()}")
    assert _check_calibration_recipe(cal, groups, agg) == len(ok_cal)
    n_alt, n_hold = _check_horizon_rmst(agg, groups)
    assert n_alt == int((executed.metric_kind == "ALT_RMST").sum())
    assert n_hold == int((executed.metric_kind == "HOLDOUT_NULL_FPR").sum())
    print(f"G1 recomputed: calibrations={len(ok_cal)} ALT_RMST={n_alt} HOLDOUT_NULL_FPR={n_hold}")


def test_full_figure_text_sample_sizes_match_manifest(sealed, full_renders, smoke_ctx):
    cfg = sealed["FULL"][0]["config"]
    allowed = {int(cfg[k]) for k in ("n_cal", "n_null", "n_alt")}
    found = {}
    for key, r in full_renders.items():
        for t in r["texts"]:
            for m in re.finditer(r"\bn = (\d+)", t):
                found.setdefault(int(m.group(1)), []).append((key, t))
    sm = smoke_ctx.manifest
    probe = pf.Ctx(dict(sm, config=dict(sm["config"], n_null=39)), smoke_ctx.run_text, smoke_ctx.tables_text,
                   smoke_ctx.table_manifest, smoke_ctx.input_dir, smoke_ctx.tables_dir)
    side = {tag: sorted({int(x) for t in _render(pf.build_entry(c, "mean"))["texts"] for x in re.findall(r"\bn = (\d+)", t)})
            for tag, c in (("SMOKE", smoke_ctx), ("SMOKE_n_null_39", probe))}
    print(f"D7b printed n: FULL {sorted(found)} (manifest {sorted(allowed)}); {side}")
    assert allowed == {2000} and found
    wrong = {n: sorted({f"{k}: {t}" for k, t in v}) for n, v in found.items() if n not in allowed}
    assert not wrong and side == {"SMOKE": [40], "SMOKE_n_null_39": [39]}, (
        f"full 2000 figure text prints sample sizes {sorted(wrong)} != manifest counts {sorted(allowed)}: {wrong}; smoke {side}")
