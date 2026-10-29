"""Z extraction (docs/sections/interface_Z.md): `python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor` writes data/derived/<dataset>/z_<state_hash>.{npz,json}."""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import inspect
import json
from pathlib import Path

import numpy as np

from jepadrift.data_loader import articleB, chars, eurofidai, sp500
from jepadrift.representations.base import _sha256
from jepadrift.representations.cross_section import CenteredRanks, DegreeZero
from jepadrift.representations.ipca import IPCA
from jepadrift.representations.pca import PCAOrthogonal

REPO_ROOT = Path(__file__).resolve().parents[2]
DERIVED = REPO_ROOT / "data" / "derived"
FIT_SEGMENT = "calib"
REGISTRY = {"pca": PCAOrthogonal, "degree0": DegreeZero, "ranks": CenteredRanks, "ipca": IPCA}
NEEDS_C = frozenset({"ipca"})
DATASETS = {"d2_us97": (articleB.load_d2, articleB.load_splits),
            "d3_239": (sp500.load_d3_239, sp500.load_splits)}
CHAR_DATASETS = {"d3_500": (sp500.load_d3_500, sp500.load_splits),
                 "d4_eurofidai": (eurofidai.load_d4, lambda _: eurofidai.load_splits_d4())}


def segment_rows(dates, segment):
    """Rows [start, stop) of `dates` from a split segment's first_day to its last_day, both included."""
    start = int(np.searchsorted(dates, np.datetime64(segment["first_day"])))
    stop = int(np.searchsorted(dates, np.datetime64(segment["last_day"]), side="right"))
    return start, stop


def _rows(a, start, stop):
    return None if a is None else np.ascontiguousarray(a[start:stop])


def extract(rep, X, dates, splits, out_dir, dataset, C=None):
    """rep.pretrain (if any) on pretrain, fit on calib, transform from the first pretrain day on, C aligned with X."""
    if C is not None and C.shape[:2] != X.shape:
        raise ValueError(f"C must align with the {X.shape} rows and assets of X, got {C.shape}")
    segments = splits["segments"]
    start, stop = segment_rows(dates, segments[FIT_SEGMENT])
    first, pre_stop = segment_rows(dates, segments["pretrain"])
    if hasattr(rep, "pretrain"):
        rep.pretrain(np.ascontiguousarray(X[first:pre_stop]), _rows(C, first, pre_stop), dates[first:pre_stop])
    rep.fit(np.ascontiguousarray(X[start:stop]), _rows(C, start, stop), dates[start:stop])
    X_out = np.ascontiguousarray(X[first:])
    Z = rep.transform_panel(X_out, _rows(C, first, len(X)))
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
    if C is not None:
        sidecar["c_sha256"] = _sha256(C[first:])
    (out_dir / f"z_{h}.json").write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
    return npz, sidecar


def _K(value):
    return value if value in ("mp", "select") else int(value)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fit a representation on the calib segment and write its Z panel.")
    parser.add_argument("--dataset", required=True, choices=sorted({**DATASETS, **CHAR_DATASETS}))
    parser.add_argument("--rep", required=True, choices=sorted(REGISTRY))
    parser.add_argument("--mode", help="pca: factor | full | tail10; degree0: factor | full")
    parser.add_argument("--K", type=_K, help="pca, degree0: 'mp' (Marchenko-Pastur edge) or an int; ipca: 'select' or an int")
    parser.add_argument("--shrinkage", choices=("ledoit_wolf", "none"), help="pca only")
    parser.add_argument("--b", choices=("pc1", "ones"), help="degree0 only")
    parser.add_argument("--cash-neutral", choices=("constant",), help="ipca only")
    parser.add_argument("--out", type=Path, help="output directory (default data/derived/<dataset>)")
    args = parser.parse_args(argv)
    kwargs = {k: v for k, v in (("mode", args.mode), ("K", args.K), ("b", args.b),
                                ("cash_neutral", args.cash_neutral)) if v is not None}
    if args.shrinkage is not None:
        kwargs["shrinkage"] = None if args.shrinkage == "none" else args.shrinkage
    cls = REGISTRY[args.rep]
    unknown = sorted(set(kwargs) - set(inspect.signature(cls).parameters) - {"self"})
    if unknown:
        parser.error(f"--rep {args.rep} does not accept: {', '.join('--' + k for k in unknown)}")
    if args.dataset in CHAR_DATASETS and args.rep not in NEEDS_C:
        parser.error(f"--dataset {args.dataset} serves the characteristic representations {sorted(NEEDS_C)} only")
    load, load_splits = {**DATASETS, **CHAR_DATASETS}[args.dataset]
    ret, dates, _ = load()
    C = None
    if args.rep in NEEDS_C:
        C = chars.load_continuous_chars(args.dataset)
        ret = np.where(chars.load_universe(args.dataset), ret, np.nan)
    npz, sidecar = extract(cls(**kwargs), ret, dates, load_splits(args.dataset),
                           args.out or DERIVED / args.dataset, args.dataset, C)
    shown = npz.relative_to(REPO_ROOT) if npz.is_relative_to(REPO_ROOT) else npz
    print(f"{shown}: D={sidecar['heads']['z_odd']['dim']} D'={sidecar['heads']['z_even']['dim']} "
          f"rows={sidecar['rows']} sha256={hashlib.sha256(npz.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
