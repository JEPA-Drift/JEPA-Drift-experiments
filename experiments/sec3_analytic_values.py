"""Stream 21-rest (lot P): analytic values of nine result-bearing occurrences of paper/sec3_theory.tex.

One row per occurrence, keyed by (quantity, parameters), with its occurrence id, reading, approximation and the anchor
text of its quantity on the paper line; tools/trace_numbers.py checks them against docs/MAPPING.md. Deterministic
evaluations of jepadrift.floors: no estimation, no Monte Carlo arm, no PRNG and no read of results/e2.
  mixture_multiplier       M(D, gamma) of Proposition 3: fluid delay multiplier of the isotropic Gaussian mixture
                           e-process stopped at the e-value threshold gamma (anytime-valid reading)
  absorption_ratio         fluid absorption delay over tau_gamma, -(r/2) ln(1 - 2/r) at r = tau_a/tau_gamma (budget)
  arl0_over_add_diffusion  gamma over Phi(gamma I)/I at SR = 1 (I = SR^2/504): the calibrated ARL0 over the diffusion
                           approximation of the delay of the CUSUM calibrated to ARL0 = gamma (exact reading); not an
                           exact ADD at finite gamma

`python experiments/sec3_analytic_values.py --out <new file>` writes the rows with save_fair_csv, by exclusive
creation in an existing directory, and prints `<sha256>  <out>`; an existing --out is refused and left unchanged.
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["MKL_CBWR"] = "COMPATIBLE"

import argparse
import hashlib
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl
from jepadrift.pipelines import save_fair_csv

GAMMA_M = 504
MIXTURE_D = (1, 10, 64, 500, 128)
ABSORPTION_R = (2.5, 4, 8)
GAMMA_X, SR_X = 252, 1.0
ANCHORS = {"mixture_multiplier": "$M=", "absorption_ratio": "\\tau_a/\\tau_\\gamma=",
           "arl0_over_add_diffusion": "expected run to a false alarm"}


def row(ident, quantity, parameters, reading, approximation, value):
    """One bound row; a non-finite or non-positive value is refused before any write."""
    if not (math.isfinite(value) and value > 0):
        raise ValueError(f"{ident}: value {value!r} is not finite and positive")
    return {"id": ident, "quantity": quantity, "parameters": parameters, "reading": reading,
            "approximation": approximation, "anchor": ANCHORS[quantity], "value": value}


def rows():
    """The nine rows, in the order of their occurrences in paper/sec3_theory.tex (lines 52, 80 and 105)."""
    exact = fl.cusum_exact(GAMMA_X, SR_X / math.sqrt(fl.TRADING_DAYS))
    if not exact["feasible"]:
        raise ValueError(f"cusum_exact is infeasible at gamma = {GAMMA_X}, SR = {SR_X}")
    out = [row(f"ARL0ADD-G{GAMMA_X}-SR{SR_X:g}", "arl0_over_add_diffusion", f"gamma={GAMMA_X}; sr_annual={SR_X}",
               "exact", "diffusion", GAMMA_X / exact["add"])]
    out += [row(f"M-D{d}-G{GAMMA_M}", "mixture_multiplier", f"D={d}; gamma={GAMMA_M}", "anytime-valid", "fluid",
                fl.mixture_multiplier(d, GAMMA_M)) for d in MIXTURE_D]
    out += [row(f"ABS-R{r}", "absorption_ratio", f"tau_a/tau_gamma={r}", "budget", "fluid",
                fl.absorption_delay(1.0, r)) for r in ABSORPTION_R]
    return out


def main(argv=None):
    """CLI: write the nine rows to a new --out file and print its SHA-256."""
    ap = argparse.ArgumentParser(description="Analytic values of nine Section 3 occurrences; no measurement.")
    ap.add_argument("--out", type=Path, required=True, help="new CSV file in an existing directory")
    args = ap.parse_args(argv)
    df = pd.DataFrame(rows())
    try:
        f = open(args.out, "x", newline="", encoding="utf-8")
    except FileExistsError:
        print(f"sec3-analytic: error: {args.out} exists; refusing to overwrite it", file=sys.stderr)
        return 1
    with f:
        save_fair_csv(df, f)
    print(f"{hashlib.sha256(args.out.read_bytes()).hexdigest()}  {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
