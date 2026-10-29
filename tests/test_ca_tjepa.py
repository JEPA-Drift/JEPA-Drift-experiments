import copy
import itertools
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pytest
import torch
import yaml

from experiments import jepa_pretrain
from jepadrift.jepa import ca_tjepa as cj
from jepadrift.jepa.representation import CATJEPA
from jepadrift.monitors.streams import exact_sign_stream

REPO = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((REPO / "configs" / "ca_tjepa.yaml").read_text())
LAM = CFG["neutralization"]["lambda_f"]
RATIO = CFG["mask"]["ratio"]


def small_cfg(d=4, epochs=1, kind="group"):
    cfg = copy.deepcopy(CFG)
    cfg["model"]["d"], cfg["train"]["max_epochs"], cfg["mask"]["kind"] = d, epochs, kind
    return cfg


def panel(T=160, N=24, seed=0, coupling=1.0, start="2013-07-01"):
    return jepa_pretrain.synthetic_panel(T, N, start, np.random.default_rng(seed), coupling)


def state_bytes(net):
    return b"".join(t.detach().numpy().tobytes() for t in net.state_dict().values())


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    X, C, dates, _ = panel()
    path, metrics = cj.train(X, C, dates, small_cfg(), 0, tmp_path_factory.mktemp("ckpt"))
    return path, metrics, X, C, dates


@pytest.fixture(scope="module")
def rep(trained):
    path, _, X, C, dates = trained
    return CATJEPA(path).fit(X[-40:], C[-40:], dates[-40:])


def test_parameter_budget_and_bottleneck():
    cfg = copy.deepcopy(CFG["model"])
    cfg["d"] = 16
    net = cj.build(cfg, 0)
    assert sum(p.numel() for p in net.parameters()) <= 1_000_000
    assert net.predictor[0].in_features == cfg["d"] + cj.N_CHARS


def test_group_codes_ties_and_nochar():
    C = np.array([[0.1, 0.0, -0.1, 0.2], [0.0, 0.0, 0.0, 0.0], [np.nan, 0.3, 0.3, 0.3]])
    assert cj.group_codes(C, np.zeros(4)).tolist() == [1 + 8, 0, cj.NOCHAR]


@pytest.mark.parametrize("kind", ["group", "random"])
@pytest.mark.parametrize("n", [4, 5, 7, 10, 24, 239])
def test_mask_share_bounds(kind, n):
    rng = np.random.default_rng(n)
    codes = rng.integers(0, cj.NOCHAR + 1, n)
    lo, hi = cj.mask_bounds(n, RATIO)
    assert (lo, hi) == (math.ceil(0.3 * n - 1e-9), n // 2)
    for rho in (0.3, 0.37, 0.5):
        masked, _ = cj.draw_mask(np.ones(n, bool), codes, rho, rng, kind, RATIO)
        assert lo <= masked.sum() <= hi


def test_group_mask_oversized_empty_and_absent():
    n = 20
    codes = np.r_[np.full(15, 3), np.full(5, cj.NOCHAR)]
    masked, partial = cj.draw_mask(np.ones(n, bool), codes, 0.4, np.random.default_rng(0), "group", RATIO)
    assert partial and masked.sum() == 6 and masked[15:].all()
    present = np.r_[np.ones(n, bool), np.zeros(5, bool)]
    masked2, _ = cj.draw_mask(present, np.r_[codes, np.full(5, 7)], 0.4, np.random.default_rng(0), "group", RATIO)
    assert np.array_equal(masked2[:n], masked) and not masked2[n:].any()
    with pytest.raises(ValueError, match="at least 4"):
        cj.draw_mask(np.r_[np.ones(3, bool), np.zeros(5, bool)], np.zeros(8, int), 0.4, np.random.default_rng(0),
                     "group", RATIO)


def test_sector_pit_refused():
    with pytest.raises(ValueError, match="C-D3-gics-static"):
        cj.draw_mask(np.ones(8, bool), np.zeros(8, int), 0.4, np.random.default_rng(0), "sector_pit", RATIO)
    X, C, dates, _ = panel(T=120)
    with pytest.raises(ValueError, match="C-D3-gics-static"):
        cj.train(X, C, dates, small_cfg(kind="sector_pit"), 0, Path("unused"))


def _context_case(N, kind, degenerate):
    rng = np.random.default_rng(2)
    B = 3
    u = torch.from_numpy(rng.standard_normal((B, N)).astype(np.float32))
    C = torch.from_numpy(rng.uniform(-0.5, 0.5, (B, N, 4)).astype(np.float32))
    b = torch.from_numpy(np.abs(rng.standard_normal(N)).astype(np.float32))
    codes = np.zeros((B, N), int) if degenerate else cj.group_codes(C.numpy(), np.zeros(4))
    mask = torch.from_numpy(np.stack([cj.draw_mask(np.ones(N, bool), codes[t], 0.4, rng, kind, RATIO)[0]
                                      for t in range(B)]))
    other = torch.from_numpy(1e3 * rng.standard_normal((B, N)).astype(np.float32))
    return u, torch.where(mask, other, u), C, b, torch.ones(B, N, dtype=torch.bool), mask


@pytest.mark.parametrize("N,kind,degenerate", [(24, "group", False), (24, "random", False), (4, "group", True)])
def test_context_ignores_masked_returns(N, kind, degenerate):
    net = cj.build(small_cfg()["model"], 0)
    u, u2, C, b, present, mask = _context_case(N, kind, degenerate)
    visible = present & ~mask
    for a, c in zip(cj.context_pass(net, u, C, b, visible, LAM), cj.context_pass(net, u2, C, b, visible, LAM)):
        assert torch.equal(a, c)
    with torch.no_grad():
        ya = net.target(cj.features(u, C, b, visible, LAM)[0], present)
        yc = net.target(cj.features(u2, C, b, visible, LAM)[0], present)
    assert not torch.equal(ya[mask], yc[mask])


def test_full_section_statistic_before_masking_is_detected():
    net = cj.build(small_cfg()["model"], 0)
    u, u2, C, b, present, mask = _context_case(24, "group", False)
    visible = present & ~mask

    def faulty(v):
        feats, f = cj.features(v, C, b, present, LAM)
        return f, net.context(feats, visible)

    (fa, ha), (fc, hc) = faulty(u), faulty(u2)
    assert not torch.equal(fa, fc) and not torch.equal(ha, hc)


def test_parity_exact(rep, trained):
    _, _, X, C, _ = trained
    rng = np.random.default_rng(3)
    for x in (X[-1], np.zeros(X.shape[1]), 1e3 * X[-2], rng.permutation(X[-3]), 0.02 * rep.s * rep.b):
        p, m = rep.transform_day(x, C[-1]), rep.transform_day(-x, C[-1])
        assert np.array_equal(p["z_odd"], -m["z_odd"]) and np.array_equal(p["z_even"], m["z_even"])
    assert not rep.transform_day(np.zeros(X.shape[1]), C[-1])["z_odd"].any()
    assert set(np.unique(exact_sign_stream(np.zeros(500), np.random.default_rng(0)))) == {-0.5, 0.5}


def test_asset_permutation_equivariance(rep, trained):
    _, _, X, C, _ = trained
    p = np.random.default_rng(4).permutation(X.shape[1])
    a = cj.extract_day(rep.net, X[-1], C[-1], rep.s, rep.b, rep.lambda_f)
    c = cj.extract_day(rep.net, X[-1][p], C[-1][p], rep.s[p], rep.b[p], rep.lambda_f)
    for x, y in zip(a, c):
        np.testing.assert_allclose(x, y, rtol=0, atol=1e-5)


def test_extraction_is_frozen(trained):
    path, _, X, C, dates = trained
    rep = CATJEPA(path).fit(X[-40:], C[-40:], dates[-40:])
    before, h0 = state_bytes(rep.net), rep.state_hash()
    Z1, Z2 = rep.transform_panel(X[-20:], C[-20:]), rep.transform_panel(X[-20:], C[-20:])
    assert state_bytes(rep.net) == before and rep.state_hash() == h0
    assert all(np.array_equal(Z1[k], Z2[k]) for k in Z1)

    class EmaInDay(CATJEPA):
        def _day(self, x, C):
            cj.ema_step(self.net, 0.5)
            return super()._day(x, C)

    leaky = EmaInDay(path).fit(X[-40:], C[-40:], dates[-40:])
    ref = state_bytes(leaky.net)
    leaky.transform_panel(X[-5:], C[-5:])
    assert state_bytes(leaky.net) != ref


def test_training_is_deterministic_and_leaves_global_rng(tmp_path):
    X, C, dates, _ = panel()
    t_state, n_state = torch.random.get_rng_state(), np.random.get_state()
    a, _ = cj.train(X, C, dates, small_cfg(), 0, tmp_path / "a")
    assert torch.equal(torch.random.get_rng_state(), t_state)
    assert all(np.array_equal(x, y) for x, y in zip(np.random.get_state(), n_state))
    b, _ = cj.train(X, C, dates, small_cfg(), 0, tmp_path / "b")
    c, _ = cj.train(X, C, dates, small_cfg(), 1, tmp_path / "c")
    assert a.name == b.name
    for name in ("config.json", "weights.npy", "metrics.json"):
        assert (a / name).read_bytes() == (b / name).read_bytes()
    assert (a / "weights.npy").read_bytes() != (c / "weights.npy").read_bytes()
    torch.randn(1)
    assert not torch.equal(torch.random.get_rng_state(), t_state)


def test_rows_after_pretrain_refused_and_holdout_rows_unused(tmp_path):
    X, C, dates, _ = panel()
    with pytest.raises(ValueError, match="pretrain_end"):
        cj.train(np.vstack([X, X[-1:]]), np.concatenate([C, C[-1:]]), np.r_[dates, np.datetime64("2016-04-07")],
                 small_cfg(), 0, tmp_path / "x")
    est, _ = cj.internal_split(dates, CFG["train"]["validation_start"], CFG["train"]["embargo_days"])
    Xp, Cp = X.copy(), C.copy()
    Xp[~est] = 0.05 * np.random.default_rng(9).standard_normal(Xp[~est].shape)
    Cp[~est] = np.random.default_rng(10).uniform(-0.5, 0.5, Cp[~est].shape)
    a, _ = cj.train(X, C, dates, small_cfg(), 0, tmp_path / "a")
    b, _ = cj.train(Xp, Cp, dates, small_cfg(), 0, tmp_path / "b")
    ra, rb = (json.loads((p / "config.json").read_text()) for p in (a, b))
    assert ra["frozen"] == rb["frozen"]
    assert (a / "weights.npy").read_bytes() == (b / "weights.npy").read_bytes()


def test_variance_covariance_penalties():
    eps = CFG["loss"]["var_eps"]
    v, c = cj.var_cov(torch.ones(16, 4), eps)
    assert v > 0.98 and c == 0
    z = torch.tensor(list(itertools.product([-1.0, 1.0], repeat=4)))
    assert cj.var_cov(z, eps) == (0, 0)
    assert cj.var_cov(torch.cat([z[:, :1], z[:, :1], z[:, 2:]], 1), eps)[1] > 0
    with pytest.raises(ValueError, match="at least 2 days"):
        cj.var_cov(torch.ones(1, 4), eps)


def test_ema_momentum_schedule():
    m0, m1 = CFG["ema"]["m0"], CFG["ema"]["m1"]
    ms = [cj.momentum(k, 10, m0, m1) for k in range(11)]
    assert ms[0] == pytest.approx(m0) and ms[-1] == pytest.approx(m1) and (np.diff(ms) >= 0).all()


def test_constant_baseline_is_the_training_mean():
    rng = np.random.default_rng(6)
    yt = torch.from_numpy(rng.standard_normal((50, 8))).float()
    yv = torch.from_numpy(rng.standard_normal((30, 8)) + 0.3).float()
    assert cj.constant_baseline(yt, yv) == pytest.approx(float(((yv - yt.mean(0)) ** 2).mean()))
    best = float(((yt - yt.mean(0)) ** 2).mean())
    assert all(float(((yt - yt.mean(0) - delta) ** 2).mean()) > best for delta in (0.05, -0.05))
    assert cj.coupling_readable(0.2, 0.1)
    assert not cj.coupling_readable(0.1, 0.1) and not cj.coupling_readable(0.05, 0.1)


def test_control_has_no_residual_coupling():
    X, C, _, truth = panel(T=4000, N=12, coupling=0.0)
    eps = X / 0.01 - truth["f"][:, None] * truth["b"]
    r = np.corrcoef(eps.T)
    assert np.abs(r[~np.eye(len(r), dtype=bool)]).max() < 5 / np.sqrt(len(X))
    assert abs(np.corrcoef(eps.ravel(), C[..., 0].ravel())[0, 1]) < 5 / np.sqrt(eps.size)


def test_control_run_reports_constant_baseline(tmp_path):
    X, C, dates, _ = panel(coupling=0.0)
    _, metrics = cj.train(X, C, dates, small_cfg(), 0, tmp_path)
    base = metrics["baseline"]
    assert set(base) == {"L_model", "L_const", "gain", "val_tokens", "ref_tokens"}
    assert all(np.isfinite(v) for v in base.values()) and base["val_tokens"] > 0 and base["ref_tokens"] > 0


def test_checkpoint_integrity(trained, tmp_path):
    bad = tmp_path / trained[0].name
    shutil.copytree(trained[0], bad)
    w = bytearray((bad / "weights.npy").read_bytes())
    w[-1] ^= 1
    (bad / "weights.npy").write_bytes(bytes(w))
    with pytest.raises(ValueError, match="integrity"):
        cj.load_checkpoint(bad)


def test_representation_contract(trained, rep):
    path, _, X, C, dates = trained
    side = rep.sidecar()
    assert (side["heads"]["z_odd"]["dim"], side["heads"]["z_even"]["dim"]) == (5, 4)
    assert side["channels"] == {"market": [0], "residual": [1, 2, 3, 4]}
    assert set(rep.state) == {"s", "b", "weights"} and not hasattr(rep, "pretrain")
    assert CATJEPA(path).fit(1.5 * X[-60:-20], C[-60:-20], dates[-60:-20]).state_hash() == rep.state_hash()
    with pytest.raises(ValueError, match="does not match"):
        CATJEPA(path, D=8)
    Z = rep.transform_panel(X[-20:], C[-20:])
    Xp = X[-20:].copy()
    Xp[10:] *= -3.0
    Zp = rep.transform_panel(Xp, C[-20:])
    for k in Z:
        assert np.array_equal(Z[k][:10], Zp[k][:10]) and not np.array_equal(Z[k][10:], Zp[k][10:])


def test_cli_prints_checkpoint_path(tmp_path, capsys):
    cfg = copy.deepcopy(CFG)
    cfg["synthetic"].update(n_assets=12, start="2013-07-01")
    cfg["smoke"]["days"] = 160
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(cfg))
    jepa_pretrain.main(["--config", str(p), "--data", "control", "--smoke", "--d", "2", "--out", str(tmp_path / "ck")])
    line = [x for x in capsys.readouterr().out.splitlines() if x.startswith("CHECKPOINT_PATH=")][-1]
    path = Path(line.split("=", 1)[1])
    assert path.is_absolute() and json.loads((path / "config.json").read_text())["config"]["model"]["d"] == 2
