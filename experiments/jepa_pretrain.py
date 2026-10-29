"""Pretrain CA-T-JEPA on synthetic panels (stream 14, GO-A); prints CHECKPOINT_PATH=<absolute checkpoint directory>."""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jepadrift import sim
from jepadrift.jepa import ca_tjepa


def synthetic_panel(T, N, start, rng, coupling):
    """x = 0.01 (f b' + eps + coupling g sign(C_1)), C = i.i.d. daily ranks; coupling = 0 is the no-coupling control."""
    dates = np.busday_offset(np.datetime64(start, "D"), np.arange(T), roll="forward")
    b = np.linspace(0.5, 1.5, N)
    f = sim.gaussian_latent(T, 1, rng)
    eps = sim.gaussian_latent(T, N, rng)
    C = (rng.random((T, N, ca_tjepa.N_CHARS)).argsort(axis=1).argsort(axis=1) + 0.5) / N - 0.5
    resid = coupling * sim.gaussian_latent(T, 1, rng) * np.sign(C[..., 0])
    return 0.01 * (f * b + eps + resid), C, dates, {"b": b, "f": f[:, 0]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data", choices=("synthetic", "control"), required=True)
    parser.add_argument("--smoke", action="store_true", help="smoke.days days and smoke.epochs epochs")
    parser.add_argument("--d", type=int, choices=(2, 4, 8, 16), help="native output width, fixed before training")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("ckpt"))
    args = parser.parse_args(argv)
    cfg = yaml.safe_load(args.config.read_text())
    if args.d is not None:
        cfg["model"]["d"] = args.d
    if args.smoke:
        cfg["train"]["max_epochs"] = cfg["smoke"]["epochs"]
    syn = cfg["synthetic"]
    coupling = 0.0 if args.data == "control" else syn["coupling"]
    X, C, dates, _ = synthetic_panel(cfg["smoke"]["days"] if args.smoke else syn["days"], syn["n_assets"],
                                     syn["start"], ca_tjepa.numpy_rng(args.seed, "data"), coupling)
    t0 = time.perf_counter()
    path, metrics = ca_tjepa.train(X, C, dates, cfg, args.seed, args.out,
                                   data={"source": f"synthetic:{args.data}", "coupling": coupling, "smoke": args.smoke})
    seconds = time.perf_counter() - t0
    (path / "run.json").write_text(json.dumps({"seconds": round(seconds, 3)}) + "\n")
    print(json.dumps({"best_epoch": metrics["best_epoch"], **metrics["baseline"], "seconds": round(seconds, 1)}))
    print(f"CHECKPOINT_PATH={path.resolve()}")


if __name__ == "__main__":
    main()
