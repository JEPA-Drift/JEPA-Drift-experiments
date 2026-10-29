import copy
import hashlib
import io
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch
from torch import nn

from jepadrift.data_loader.chars import impute_zero
from jepadrift.stats.covariance import eigh_desc

N_CHARS = 4
NOCHAR = 2 ** N_CHARS
USAGES = {"init": 0, "batches": 1, "train_masks": 2, "eval_masks": 3, "data": 4}
MODEL_KEYS = ("d_model", "heads", "layers", "ffn", "d", "pred_hidden")
CHUNK = 64


def configure():
    """Single-threaded deterministic CPU torch."""
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def seed_sequence(seed, usage):
    """SeedSequence keyed on (stream 14, seed, usage)."""
    return np.random.SeedSequence([14, seed, USAGES[usage]])


def numpy_rng(seed, usage):
    """Local numpy Generator of one usage."""
    return np.random.default_rng(seed_sequence(seed, usage))


def torch_generator(seed, usage):
    """Local torch.Generator of one usage."""
    g = torch.Generator()
    g.manual_seed(int(seed_sequence(seed, usage).generate_state(1, dtype=np.uint64)[0]))
    return g


def internal_split(dates, validation_start, embargo):
    """(estimation, validation) row masks: validation from validation_start, estimation before it minus the embargo."""
    dates = np.asarray(dates, dtype="datetime64[D]")
    if (np.diff(dates) <= np.timedelta64(0, "D")).any():
        raise ValueError("dates must be strictly increasing")
    val = dates >= np.datetime64(validation_start)
    first = int(val.argmax()) if val.any() else len(dates)
    return np.arange(len(dates)) < first - embargo, val


def fit_frozen(X, C, min_obs):
    """Frozen constants of the estimation rows: RMS scales s, unit PC1 loading b of zero-filled u = x / s, char medians."""
    present = np.isfinite(X)
    n_obs = present.sum(axis=0)
    if (n_obs < min_obs).any():
        raise ValueError(f"assets {np.flatnonzero(n_obs < min_obs).tolist()} have fewer than {min_obs} observed returns")
    X0 = np.where(present, X, 0.0)
    s = np.sqrt((X0 ** 2).sum(axis=0) / n_obs)
    if not (s > 0).all():
        raise ValueError("an asset has a zero return scale")
    U = X0 / s
    b = eigh_desc(U.T @ U / len(U))[1][:, 0]
    known = present[..., None] & ~np.isnan(C)
    medians = np.array([np.median(C[..., k][known[..., k]]) if known[..., k].any() else np.nan
                        for k in range(N_CHARS)])
    if not np.isfinite(medians).all():
        raise ValueError("a characteristic has no observed value on the estimation rows")
    coverage = {"n_obs_min": int(n_obs.min()), "n_obs_max": int(n_obs.max()),
                "zero_filled_share": float(1.0 - present.mean()), "abs_b_min": float(np.abs(b).min())}
    return {"s": s, "b": b, "medians": medians}, coverage


def group_codes(C, medians):
    """Group code sum_k 2^k 1{C_k > m_k} in 0..15 (a tie gives bit 0); NOCHAR when a characteristic is NaN."""
    bits = (np.nan_to_num(C, nan=0.0) > medians).astype(np.int64)
    return np.where(np.isnan(C).any(axis=-1), NOCHAR, (bits << np.arange(N_CHARS)).sum(axis=-1))


def mask_bounds(n, ratio):
    """(ceil(r0 n), floor(r1 n)) masked assets, in exact rational arithmetic."""
    r0, r1 = (Fraction(str(r)) for r in ratio)
    return math.ceil(r0 * n), math.floor(r1 * n)


def check_mask_kind(kind):
    """Training masks are group (primary) or random (diagnostic); sector_pit is refused (C-D3-gics-static)."""
    if kind == "sector_pit":
        raise ValueError("mask=sector_pit is refused: no point-in-time sector history (C-D3-gics-static)")
    if kind not in ("group", "random"):
        raise ValueError(f"unknown mask kind {kind!r}")


def draw_mask(present, codes, rho, rng, kind, ratio):
    """Masked assets of one day: present only, share in [r0, r1]; returns (mask, partial group fill)."""
    check_mask_kind(kind)
    idx = np.flatnonzero(present)
    n = idx.size
    if n < 4:
        raise ValueError(f"a masked day needs at least 4 present assets, got {n}")
    lo, hi = mask_bounds(n, ratio)
    target = min(hi, max(lo, math.ceil(rho * n)))
    masked = np.zeros(present.shape, dtype=bool)
    if kind == "random":
        masked[rng.permutation(idx)[:target]] = True
        return masked, False
    count = 0
    for g in rng.permutation(np.unique(codes[idx])):
        if count >= target:
            break
        members = idx[codes[idx] == g]
        if count + members.size <= hi:
            masked[members] = True
            count += members.size
    partial = count < lo
    if partial:
        masked[rng.permutation(np.flatnonzero(present & ~masked))[:lo - count]] = True
    return masked, bool(partial)


def pool(h, keep):
    """Mean over the kept assets of each day."""
    return h.masked_fill(~keep[..., None], 0.0).sum(1) / keep.sum(1, keepdim=True)


class Encoder(nn.Module):
    def __init__(self, d_model, heads, layers, ffn):
        super().__init__()
        self.token = nn.Sequential(nn.Linear(1 + N_CHARS, d_model), nn.GELU(), nn.Linear(d_model, d_model))
        layer = nn.TransformerEncoderLayer(d_model, heads, ffn, dropout=0.0, activation="gelu", batch_first=True,
                                           norm_first=True)
        self.blocks = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, feats, keep):
        h = self.token(feats.masked_fill(~keep[..., None], 0.0))
        return self.norm(self.blocks(h, src_key_padding_mask=~keep))


class CATJEPANet(nn.Module):
    def __init__(self, d_model, heads, layers, ffn, d, pred_hidden):
        super().__init__()
        self.context = Encoder(d_model, heads, layers, ffn)
        self.head = nn.Linear(d_model, d)
        self.predictor = nn.Sequential(nn.Linear(d + N_CHARS, pred_hidden), nn.GELU(), nn.Linear(pred_hidden, d_model))
        self.target = Encoder(d_model, heads, layers, ffn)
        self.target.requires_grad_(False)

    def summary(self, feats, keep):
        h = self.context(feats, keep)
        return h, self.head(pool(h, keep))

    def predict(self, z, C):
        return self.predictor(torch.cat([z[:, None, :].expand(-1, C.shape[1], -1), C], dim=-1))


def build(model_cfg, seed):
    """Network initialized from the local init generator; the global torch RNG is left untouched."""
    with torch.random.fork_rng(devices=[]):
        net = CATJEPANet(**{k: model_cfg[k] for k in MODEL_KEYS})
    g = torch_generator(seed, "init")
    with torch.no_grad():
        for name, p in net.named_parameters():
            if name.startswith("target."):
                continue
            if p.dim() >= 2:
                nn.init.trunc_normal_(p, std=0.02, a=-0.04, b=0.04, generator=g)
            elif name.endswith("bias"):
                p.zero_()
            else:
                p.fill_(1.0)
        net.target.load_state_dict(net.context.state_dict())
    return net


def features(u, C, b, keep, lambda_f):
    """Visible-only neutralization: f = b_K'u_K / (b_K'b_K + lambda_f) over the kept assets K; features [u - b f, C]."""
    f = (b * u.masked_fill(~keep, 0.0)).sum(-1) / (torch.where(keep, b * b, 0.0).sum(-1) + lambda_f)
    return torch.cat([(u - b * f[..., None])[..., None], C], dim=-1), f


def context_pass(net, u, C, b, visible, lambda_f):
    """Context side of a step: f_hat(V), context tokens, bottleneck z_ctx and predictions, from visible assets only."""
    feats, f = features(u, C, b, visible, lambda_f)
    h, z = net.summary(feats, visible)
    return f, h, z, net.predict(z, C)


def jepa_errors(net, u, C, b, present, masked, lambda_f):
    """Per-token latent squared errors on masked assets; EMA targets see all present assets with the same f_hat(V)."""
    visible = present & ~masked
    pred = context_pass(net, u, C, b, visible, lambda_f)[3]
    with torch.no_grad():
        y = net.target(features(u, C, b, visible, lambda_f)[0], present)
    return ((pred - y) ** 2).mean(-1)[masked]


def heads(net, u, C, b, present, lambda_f):
    """Extraction view (context encoder, mask=none) on x and -x: (odd part of g, even part of g, f_hat(P))."""
    feats_p, f = features(u, C, b, present, lambda_f)
    gp = net.summary(feats_p, present)[1]
    gm = net.summary(features(-u, C, b, present, lambda_f)[0], present)[1]
    return (gp - gm) / 2, (gp + gm) / 2, f


def var_cov(z, eps):
    """VICReg terms: mean_k max(0, 1 - sqrt(Var_b z_k + eps)) and off-diagonal covariance energy / (d (d - 1))."""
    B, d = z.shape
    if B < 2:
        raise ValueError("variance and covariance terms need at least 2 days per batch")
    zc = z - z.mean(0)
    cov = zc.T @ zc / (B - 1)
    var = torch.relu(1.0 - torch.sqrt(torch.diagonal(cov) + eps)).mean()
    return var, (cov - torch.diag(torch.diagonal(cov))).pow(2).sum() / (d * (d - 1))


def market_cov(z, f):
    """Mean squared covariance between the coordinates of z and the market factor f across days."""
    return ((z - z.mean(0)) * (f - f.mean())[:, None]).sum(0).div(len(f) - 1).pow(2).mean()


def momentum(k, K, m0, m1):
    """Cosine EMA momentum from m0 at step 0 to m1 at step K [Grill et al., 2020]."""
    return m1 - (m1 - m0) * (math.cos(math.pi * min(k, K) / K) + 1) / 2


@torch.no_grad()
def ema_step(net, m):
    """target <- m target + (1 - m) context."""
    for pt, pc in zip(net.target.parameters(), net.context.parameters()):
        pt.mul_(m).add_(pc, alpha=1 - m)


def rankme(z, eps=1e-7):
    """Effective rank exp(H(sigma / ||sigma||_1)) of the day-by-coordinate matrix [Garrido et al., 2023]."""
    s = torch.linalg.svdvals(z)
    p = s / s.sum() + eps
    return float(torch.exp(-(p * torch.log(p)).sum()))


def constant_baseline(y_train, y_val):
    """Validation MSE of the constant predictor equal to the mean training target."""
    return float(((y_val - y_train.mean(0)) ** 2).mean())


def coupling_readable(gain, control_gain):
    """Residual coupling is readable only if the gain over the constant exceeds the gain on the no-coupling control."""
    return gain > control_gain


def _chunks(days):
    return [torch.from_numpy(c) for c in np.array_split(days, max(1, math.ceil(days.size / CHUNK)))]


@torch.no_grad()
def masked_targets(net, u, C, b, present, days, mask, lambda_f):
    """EMA targets of the masked tokens on days, chunked."""
    chunks = _chunks(days)
    return torch.cat([net.target(features(u[c], C[c], b, present[c] & ~m, lambda_f)[0], present[c])[m]
                      for c, m in zip(chunks, torch.split(mask, [len(c) for c in chunks]))])


@torch.no_grad()
def evaluate(net, u, C, b, present, days, mask, lambda_f):
    """Mean latent squared error over the masked tokens of days, chunked."""
    chunks = _chunks(days)
    return float(torch.cat([jepa_errors(net, u[c], C[c], b, present[c], m, lambda_f)
                            for c, m in zip(chunks, torch.split(mask, [len(c) for c in chunks]))]).mean())


def flat_weights(net):
    """All parameters and buffers in state-dict order as one float32 vector."""
    return np.concatenate([t.detach().numpy().ravel() for t in net.state_dict().values()]).astype(np.float32)


def _sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def assets_digest(assets):
    """Canonical SHA-256 of the ordered asset IDs (compact JSON list)."""
    return hashlib.sha256(json.dumps(list(assets), separators=(",", ":")).encode()).hexdigest()


def save_checkpoint(out_dir, record, net):
    """Write <out_dir>/<sha256(config.json + weights.npy)>/{config.json, weights.npy}; returns the directory."""
    sd = net.state_dict()
    record = {**record, "names": list(sd), "shapes": [list(t.shape) for t in sd.values()],
              "checksums": {part: _sha(np.concatenate([t.numpy().ravel() for k, t in sd.items()
                                                       if k.startswith(part + ".")]))
                            for part in ("context", "head", "predictor", "target")}}
    buf = io.BytesIO()
    np.save(buf, flat_weights(net))
    w = buf.getvalue()
    c = (json.dumps(record, sort_keys=True, indent=1) + "\n").encode()
    path = Path(out_dir) / hashlib.sha256(c + w).hexdigest()
    path.mkdir(parents=True, exist_ok=True)
    (path / "config.json").write_bytes(c)
    (path / "weights.npy").write_bytes(w)
    return path


def load_checkpoint(path):
    """(network frozen in eval mode, record) of a checkpoint whose directory name is its SHA-256."""
    path = Path(path)
    c, w = (path / "config.json").read_bytes(), (path / "weights.npy").read_bytes()
    if hashlib.sha256(c + w).hexdigest() != path.name:
        raise ValueError(f"checkpoint {path} fails its SHA-256 integrity check")
    record = json.loads(c)
    with torch.random.fork_rng(devices=[]):
        net = CATJEPANet(**{k: record["config"]["model"][k] for k in MODEL_KEYS})
    flat = torch.from_numpy(np.load(io.BytesIO(w)))
    parts = torch.split(flat, [math.prod(s) for s in record["shapes"]])
    net.load_state_dict({k: t.reshape(s) for k, t, s in zip(record["names"], parts, record["shapes"])})
    net.eval().requires_grad_(False)
    return net, record


@torch.no_grad()
def extract_day(net, x, C, s, b, lambda_f):
    """(z_odd, z_even) of one day from the frozen context encoder with mask=none; z_odd[0] = f_hat(P) in float64."""
    present = np.isfinite(x)
    if present.sum() < 2:
        raise ValueError(f"an extraction day needs at least 2 observed assets, got {int(present.sum())}")
    if np.isinf(C).any():
        raise ValueError(f"C has {int(np.isinf(C).sum())} infinite values")
    u = np.where(present, x / s, 0.0)
    f = (b * u)[present].sum() / ((b * b)[present].sum() + lambda_f)
    Ct = torch.from_numpy(impute_zero(C)[0].astype(np.float32))[None]
    keep = torch.from_numpy(present)[None]
    bt = torch.from_numpy(b.astype(np.float32))
    gp, gm = (net.summary(features(torch.from_numpy(v.astype(np.float32))[None], Ct, bt, keep, lambda_f)[0],
                          keep)[1][0].double().numpy() for v in (u, -u))
    return np.concatenate([[f], (gp - gm) / 2]), (gp + gm) / 2


def train(X, C, dates, cfg, seed, out_dir, data=None, assets=None):
    """Pretrain on rows dated before train.pretrain_end only; writes the checkpoint and metrics.json; (path, metrics)."""
    mk, tr, ls, lam = cfg["mask"], cfg["train"], cfg["loss"], cfg["neutralization"]["lambda_f"]
    check_mask_kind(mk["kind"])
    configure()
    dates = np.asarray(dates, dtype="datetime64[D]")
    if (dates >= np.datetime64(tr["pretrain_end"])).any():
        raise ValueError(f"rows on or after pretrain_end {tr['pretrain_end']} are refused")
    if X.shape != C.shape[:2] or C.shape[2] != N_CHARS or dates.shape != (len(X),):
        raise ValueError(f"X {X.shape}, C {C.shape} and dates {dates.shape} are not aligned")
    if np.isinf(X).any() or np.isinf(C).any():
        raise ValueError(f"X and C hold {int(np.isinf(X).sum())} and {int(np.isinf(C).sum())} infinite values")
    if assets is not None and (len(assets) != X.shape[1] or len(set(assets)) != len(assets)):
        raise ValueError(f"assets must hold the {X.shape[1]} ordered, unique asset IDs of the columns of X")
    est, val = internal_split(dates, tr["validation_start"], tr["embargo_days"])
    frozen, coverage = fit_frozen(X[est], C[est], tr["min_obs"])
    present_np = np.isfinite(X)
    u = torch.from_numpy(np.where(present_np, X / frozen["s"], 0.0).astype(np.float32))
    C0, n_imputed = impute_zero(C)
    Ct, present = torch.from_numpy(C0.astype(np.float32)), torch.from_numpy(present_np)
    b = torch.from_numpy(frozen["b"].astype(np.float32))
    codes = group_codes(C, frozen["medians"])
    usable = present_np.sum(1) >= mk["min_present"]
    train_days, val_days = np.flatnonzero(est & usable), np.flatnonzero(val & usable)
    if train_days.size < 2 or val_days.size < 2:
        raise ValueError("the internal split needs at least 2 usable estimation and 2 usable validation days")
    r0, r1 = mk["ratio"]
    rng_batches, rng_masks, rng_eval = (numpy_rng(seed, k) for k in ("batches", "train_masks", "eval_masks"))

    def masks(days, rng):
        rho = r0 + (r1 - r0) * rng.random()
        drawn = [draw_mask(present_np[t], codes[t], rho, rng, mk["kind"], mk["ratio"]) for t in days]
        return torch.from_numpy(np.stack([m for m, _ in drawn])), sum(p for _, p in drawn)

    val_mask, val_partial = masks(val_days, rng_eval)
    ref_mask, _ = masks(train_days, rng_eval)
    net = build(cfg["model"], seed)
    opt = torch.optim.AdamW([p for p in net.parameters() if p.requires_grad], lr=tr["lr"],
                            weight_decay=tr["weight_decay"])
    n_batches = math.ceil(train_days.size / tr["batch_days"])
    K, step, partial = tr["max_epochs"] * n_batches, 0, 0
    history, best, best_loss, best_epoch, stale = [], None, math.inf, 0, 0
    for epoch in range(1, tr["max_epochs"] + 1):
        net.train()
        sums = dict.fromkeys(("jepa", "var", "cov", "market", "total"), 0.0)
        for days in np.array_split(rng_batches.permutation(train_days), n_batches):
            mask, n_part = masks(days, rng_masks)
            partial += n_part
            t = torch.from_numpy(days)
            l_jepa = jepa_errors(net, u[t], Ct[t], b, present[t], mask, lam).mean()
            z_odd, z_even, f = heads(net, u[t], Ct[t], b, present[t], lam)
            (v_o, c_o), (v_e, c_e) = var_cov(z_odd, ls["var_eps"]), var_cov(z_even, ls["var_eps"])
            terms = (l_jepa, (v_o + v_e) / 2, (c_o + c_e) / 2, market_cov(z_odd, f))
            loss = terms[0] + ls["lambda_var"] * terms[1] + ls["lambda_cov"] * terms[2] + ls["lambda_market"] * terms[3]
            opt.zero_grad()
            loss.backward()
            opt.step()
            ema_step(net, momentum(step, K, cfg["ema"]["m0"], cfg["ema"]["m1"]))
            step += 1
            for key, v in zip(sums, (*terms, loss)):
                sums[key] += float(v.detach()) / n_batches
        net.eval()
        val_loss = evaluate(net, u, Ct, b, present, val_days, val_mask, lam)
        history.append({"epoch": epoch, **sums, "val_jepa": val_loss})
        if val_loss < best_loss:
            best, best_loss, best_epoch, stale = copy.deepcopy(net.state_dict()), val_loss, epoch, 0
        else:
            stale += 1
            if stale >= tr["patience"]:
                break
    net.load_state_dict(best)
    net.eval()
    y_ref = masked_targets(net, u, Ct, b, present, train_days, ref_mask, lam)
    y_val = masked_targets(net, u, Ct, b, present, val_days, val_mask, lam)
    l_const = constant_baseline(y_ref, y_val)
    with torch.no_grad():
        v = torch.from_numpy(val_days)
        z_odd, z_even, _ = heads(net, u[v], Ct[v], b, present[v], lam)
    diagnostics = {name: {"std": z.std(0).tolist(), "offdiag_energy": float(var_cov(z, ls["var_eps"])[1]),
                          "rankme": rankme(z)} for name, z in (("z_odd", z_odd), ("z_even", z_even))}
    metrics = {"history": history, "best_epoch": best_epoch, "diagnostics": diagnostics,
               "baseline": {"L_model": best_loss, "L_const": l_const, "gain": 1.0 - best_loss / l_const,
                            "val_tokens": int(y_val.shape[0]), "ref_tokens": int(y_ref.shape[0])},
               "masks": {"kind": mk["kind"], "partial_train_days": int(partial), "partial_val_days": int(val_partial)},
               "days": {"train": int(train_days.size), "validation": int(val_days.size),
                        "unusable": int(((est | val) & ~usable).sum())}}
    record = {"config": cfg, "seed": seed, "data": {**(data or {}), "x_sha256": _sha(X), "c_sha256": _sha(C),
                                                     "dates_sha256": _sha(dates.astype("int64")),
                                                     "c_nan_imputed": n_imputed},
              "frozen": {k: v.tolist() for k, v in frozen.items()}, "coverage": coverage,
              "groups": {"code": "sum_k 2^k 1{C_k > median_k} over the four continuous characteristics",
                         "tie": "C_k == median_k gives bit 0", "nochar": NOCHAR, "absent": "neither visible nor masked",
                         "empty": "not drawn", "fallback": "uniform fill to ceil(r0 n) when whole groups fall short"},
              "seeds": {"scheme": "SeedSequence([14, seed, usage])", "usages": USAGES},
              "split": {"estimation": [str(dates[est][0]), str(dates[est][-1]), int(est.sum())],
                        "validation": [str(dates[val][0]), str(dates[val][-1]), int(val.sum())]},
              "versions": {"torch": torch.__version__, "numpy": np.__version__},
              "assets_sha256": None if assets is None else assets_digest(assets)}
    path = save_checkpoint(out_dir, record, net)
    (path / "metrics.json").write_text(json.dumps(metrics, sort_keys=True, indent=1) + "\n")
    return path, metrics
