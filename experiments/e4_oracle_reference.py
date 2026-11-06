"""Stream 19-oracle: analytic oracle reference of the per-day KL I_N of a market drift in N, for E4.

Known Gaussian model: Sigma_N = rho 11' + (1 - rho) I_N, Delta_mu = delta 1. floors.factor_information returns the
quadratic form Delta_mu' Sigma_N^{-1} Delta_mu = 2 I_N; I_N is half of it. No estimation, no detector, no Monte Carlo:
no column is a delay, an ADD, an ARL0 or an FPR. ValueError, raised before factor_information whenever the inputs
decide it: out-of-domain or non-real parameters; rho or delta that the float64 conversion would round; delta^2/2
underflowing, overflowing or subnormal (a subnormal is representable but excluded for precision); 1/rho overflowing
for rho > 0; non-finite outputs.

`python experiments/e4_oracle_reference.py --out <new file>` writes the 16-row grid RHO_GRID x N_GRID at delta = DELTA
with save_fair_csv, by exclusive creation in an existing directory, and prints `<sha256>  <out>`.
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import math
import numbers
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl
from jepadrift.pipelines import save_fair_csv

N_GRID = (1, 8, 16, 32, 64, 128, 239, 500)
RHO_GRID = (0.0, 0.4)
DELTA = 1.0
QUALIFICATION = "ORACLE_KNOWN_SIGMA_DELTA"


def oracle_row(n, rho, delta=DELTA):
    """One reference row: I_N = (factor_term + breadth_term) / 2 nats/day, G = I_N / I_1 with I_1 = delta^2 / 2."""
    if isinstance(n, bool) or not isinstance(n, numbers.Integral) or n < 1:
        raise ValueError(f"N must be an integer >= 1, got {n!r}")
    if any(isinstance(v, bool) or not isinstance(v, numbers.Real) for v in (rho, delta)):
        raise ValueError(f"rho and delta must be non-boolean real scalars, got {rho!r} and {delta!r}")
    r, d = (v.item() if isinstance(v, np.generic) else v for v in (rho, delta))
    if not 0 <= r < 1:
        raise ValueError(f"rho must satisfy 0 <= rho < 1, got {rho!r}")
    if not 0 < d <= sys.float_info.max:
        raise ValueError(f"delta must be > 0 and at most the largest finite float64, got {delta!r}")
    if float(r) != r or float(d) != d:
        raise ValueError(f"rho and delta must be exactly representable in float64, got {rho!r} and {delta!r}")
    n, rho, delta = int(n), float(r), float(d)
    single = delta * delta / 2.0
    if not sys.float_info.min <= single < math.inf:
        raise ValueError(f"delta^2/2 = {single!r} is not a normal finite float64 (delta = {delta!r})")
    ceiling = 1.0 / rho if rho > 0.0 else math.inf
    if rho > 0.0 and not math.isfinite(ceiling):
        raise ValueError(f"1/rho overflows float64 (rho = {rho!r})")
    with np.errstate(over="ignore"):
        factor_term, breadth_term = fl.factor_information(np.ones((n, 1)), [[rho]], np.full(n, 1.0 - rho), [delta],
                                                          np.zeros(n))
    info = (factor_term + breadth_term) / 2.0
    gain = info / single
    if not (all(map(math.isfinite, (factor_term, breadth_term, info, gain))) and info > 0.0 and gain > 0.0):
        raise ValueError(f"I_N is not representable in float64 (N = {n}, rho = {rho!r}, delta = {delta!r})")
    return {"N": n, "rho": rho, "delta": delta, "factor_term": factor_term, "breadth_term": breadth_term,
            "info_nats": info, "gain_vs_single": gain, "gain_ceiling": ceiling, "qualification": QUALIFICATION}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Analytic oracle reference of I_N in N for E4; not a delay, ARL0 or FPR.")
    ap.add_argument("--out", type=Path, required=True, help="new CSV file in an existing directory")
    args = ap.parse_args(argv)
    df = pd.DataFrame([oracle_row(n, rho) for rho in RHO_GRID for n in N_GRID])
    with open(args.out, "x", newline="") as f:
        save_fair_csv(df, f)
    print(f"{hashlib.sha256(args.out.read_bytes()).hexdigest()}  {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
