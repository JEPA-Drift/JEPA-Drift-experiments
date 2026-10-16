"""Z extraction (docs/sections/interface_Z.md): `python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor` writes data/derived/<dataset>/z_<state_hash>.{npz,json}."""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from jepadrift.data_loader import articleB, sp500
from jepadrift.representations.base import _sha256
from jepadrift.representations.cross_section import CenteredRanks, DegreeZero
from jepadrift.representations.pca import PCAOrthogonal

REPO_ROOT = Path(__file__).resolve().parents[2]
DERIVED = REPO_ROOT / "data" / "derived"
FIT_SEGMENT = "calib"
REGISTRY = {"pca": PCAOrthogonal, "degree0": DegreeZero, "ranks": CenteredRanks}
DATASETS = {"d2_us97": (articleB.load_d2, articleB.load_splits),
            "d3_239": (sp500.load_d3_239, sp500.load_splits)}


def segment_rows(dates, segment):
    """Rows [start, stop) of `dates` from a split segment's first_day to its last_day, both included."""
    start = int(np.searchsorted(dates, np.datetime64(segment["first_day"])))
    stop = int(np.searchsorted(dates, np.datetime64(segment["last_day"]), side="right"))
    return start, stop


def extract(rep, X, dates, splits, out_dir, dataset):
    """Fit rep on the calib rows, transform the rows from the first pretrain day on, write z_<state_hash>.{npz,json}."""
    segments = splits["segments"]
    start, stop = segment_rows(dates, segments[FIT_SEGMENT])
    first = segment_rows(dates, segments["pretrain"])[0]
    rep.fit(np.ascontiguousarray(X[start:stop]), None, dates[start:stop])
    X_out = np.ascontiguousarray(X[first:])
    Z = rep.transform_panel(X_out)
    if not (np.isfinite(Z["z_odd"]).all() and np.isfinite(Z["z_even"]).all()):
        raise ValueError("representation produced non-finite values")
    h = rep.state_hash()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npz = out_dir / f"z_{h}.npz"
    np.savez(npz, Z_odd=Z["z_odd"], Z_even=Z["z_even"], dates=np.asarray(dates[first:], dtype="datetime64[D]"))
    sidecar = rep.sidecar()
    sidecar.update({"dataset": dataset, "fit_segment": FIT_SEGMENT, "rows": [first, len(X)],
                    "dates": [str(dates[first]), str(dates[-1])], "x_sha256": _sha256(X_out),
                    "z_sha256": {"Z_odd": _sha256(Z["z_odd"]), "Z_even": _sha256(Z["z_even"])}})
    (out_dir / f"z_{h}.json").write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
    return npz, sidecar


def _K(value):
    return value if value == "mp" else int(value)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fit a representation on the calib segment and write its Z panel.")
    parser.add_argument("--dataset", required=True, choices=sorted(DATASETS))
    parser.add_argument("--rep", required=True, choices=sorted(REGISTRY))
    parser.add_argument("--mode", help="pca: factor | full | tail10; degree0: factor | full")
    parser.add_argument("--K", type=_K, help="'mp' (Marchenko-Pastur edge) or an int")
    parser.add_argument("--shrinkage", choices=("ledoit_wolf", "none"), help="pca only")
    parser.add_argument("--b", choices=("pc1", "ones"), help="degree0 only")
    parser.add_argument("--out", type=Path, help="output directory (default data/derived/<dataset>)")
    args = parser.parse_args(argv)
    kwargs = {k: v for k, v in (("mode", args.mode), ("K", args.K), ("b", args.b)) if v is not None}
    if args.shrinkage is not None:
        kwargs["shrinkage"] = None if args.shrinkage == "none" else args.shrinkage
    load, load_splits = DATASETS[args.dataset]
    ret, dates, _ = load()
    npz, sidecar = extract(REGISTRY[args.rep](**kwargs), ret, dates, load_splits(args.dataset),
                           args.out or DERIVED / args.dataset, args.dataset)
    shown = npz.relative_to(REPO_ROOT) if npz.is_relative_to(REPO_ROOT) else npz
    print(f"{shown}: D={sidecar['heads']['z_odd']['dim']} D'={sidecar['heads']['z_even']['dim']} "
          f"rows={sidecar['rows']} sha256={hashlib.sha256(npz.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
