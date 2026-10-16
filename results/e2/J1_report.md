# J1 report — E2 floor validation (milestone J1)

Stream E2 (`experiments/e2_floor_validation.py`), milestone J1 (gate 2026-10-18). Run date: 2026-10-16.

## Environment
- Python 3.12.9 — `/home/m53/JEPA-Drift-experiments/.venv` (reference run: 3.12.3; patch-level difference only)
- numpy 2.4.4 (pinned; matches reference)
- scipy 1.17.1 (pinned; matches reference)
- CPU: AMD EPYC 8224P 24-Core Processor; single-threaded BLAS via OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42

## Run
- Command: `make j1` = `python experiments/e2_floor_validation.py --reps 2000 --out results/e2`
- Master seed 20261018 (`np.random.SeedSequence`); 2000 replicates per G1/S1 cell, 1000 per G2/S2 cell (500 for G2 at D = 64)
- Duration: 73 s script-reported, 73.4 s wall clock (single core; limit 10 min)
- Exit code 0; journal `logs/e2/run.log` (5 lines)

## Results
- SHA-256 of `results/e2/e2_cells.csv`: `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` — prefix `e315e537ead0f656` matches the reference exactly (bit-identical under numpy 2.4.4 / scipy 1.17.1)
- Cells passing the J1 rule: 46/46
- Largest calendar deviation: S1/oracle, D=1, SR=4.0, gamma=20, delay ratio 1.118 (gated on the information clock)
- H0 sign streams: mean 0.4998, acf1 +0.0002, cross -0.0009 (se 0.0010); acf1 of squares +0.067

### Largest |ratio - 1| by arm (calendar delay)
| Arm | measured | reference |
| --- | -------- | --------- |
| G1  | 0.024    | 0.024     |
| G2  | 0.047    | 0.047     |
| S1  | 0.118    | 0.118     |
| S2  | 0.046    | 0.046     |

S1 is controlled in information time (clock_ratio within 10% of its prediction); its calendar ratio is reported, not gated, below CALENDAR_MIN = 150 days.

### G1 cells at SR = 1 — measured / predicted / first-order floor
I = SR^2/504 = 0.00198413 nats/day; first-order floor = ln(gamma)/I.

| gamma | mode    | measured | predicted | first-order |
| ----- | ------- | -------- | --------- | ----------- |
| 20    | onset   | 1519.152 | 1528.346  | 1509.849    |
| 20    | cusum_t | 1050.323 | 1066.260  | 1509.849    |
| 20    | cusum_x | 16.730   | 16.715    | 1509.849    |
| 252   | onset   | 2815.446 | 2805.329  | 2786.832    |
| 252   | cusum_t | 2319.800 | 2321.685  | 2786.832    |
| 252   | cusum_x | 145.081  | 142.039   | 2786.832    |

Reference values reproduced exactly (onset 1519.152 / 2815.446; cusum_t 1050.323 / 2319.800; cusum_x 16.730 / 145.081). cusum_x at gamma = 252: measured ARL0 = 258.4925 vs calibrated 252 (+2.6%, within the 10% gate).

## Verdict
J1: PASS. 46/46 cells pass the J1 rule, the H0 sign streams are exact, every reference value is reproduced, and the SHA-256 of `e2_cells.csv` is identical to the reference under the pinned numpy 2.4.4 / scipy 1.17.1. No C-E2-env deviation to record: the only version difference is the Python patch level (3.12.9 here vs 3.12.3 in the reference run) and it has no observable effect (identical SHA-256).
