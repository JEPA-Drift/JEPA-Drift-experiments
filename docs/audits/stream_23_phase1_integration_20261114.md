# Stream 23 — bounded E6 phase-1 reproduction and integration receipt

Date: 2026-11-14. Scope: integration of the historical linear P1-D/P3-D covariance-drift experiment, with a
bounded pre-2020 input reader. No new scientific exploration, parameter search or learned representation.

## Authority and lineage

The researcher's E6 phase-1 GO permits bounded historical D5/D6 reproduction on available pre-2020 data.
The current kickoff13 prioritizes actual stream23 closure, then stream32. E4 was published at
461f2b13894be2cca954676dc3aab10e0b640a2b before runtime. The independent compatibility audit's C1–C7 and
the canonical plan prompts/plans/plan-23-phase1-20261113.md govern this receipt.

Codex materialized historical commits 7e4c7a11f10eb96abc3fe587aaed9edd19c673c7 and
3d0bd2071cb86afc6b196b5020ff729204746a93 in that order, then reconciled onto published E4 main.
The historical worktree and branch remain intact. The 1324-line DEVIATIONS prefix of main and the 66-line
historical C-E6-phase1 entry were verified verbatim before the new integration entry was appended.
The three D3 input Git blob IDs, pinned dependency files, shared library, Makefile and conftest.py are unchanged
between b18d8e5 and the published integration base. This blob comparison did not read return values.

The only production changes are the approved input path and consumed-row provenance. Numerical routines,
configuration, seeds, cohorts, windows, estimands, Wilson implementation and historical outputs remain unchanged.

| Register | Object | SHA-256 |
|---|---|---|
| Historical source | experiments/e6_second_order.py at 3d0bd20 | 072b7b0c03754b41c8a489359a46de26e3597f208c07f5dd2623e92dd098c750 |
| Technical source | experiments/e6_second_order.py after P-IO | 5af91240df658f8ec7e8f45139cf74144ed9c6665d52bc6f8aec67da42902855 |
| Received tests | tests/test_e6.py | 39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc |
| Frozen configuration | configs/e6.yaml | ca74d2e117edb47b0ff11822501a20a381460c35c69e81b57a6d11de81a2bcf5 |

## Reader and temporal boundary

The historical reader loaded the whole return panel before slicing; the CLI also hashed that whole file.
P-IO refuses foreign dataset names, NaT/2020+ end dates, invalid calendars, empty or inconsistent bounds and
panel shapes before any return-value copy. The panel is opened read-only through a memmap; only the selected
pre-2020 rows are copied in C order with the original dtype. Only consumed return rows are hashed.
Full dates.npy and splits.yaml remain calendar metadata under the explicitly accepted H-cal convention.
The contract concerns values indexed/copied/hashed, not operating-system page-cache behavior.

Observed consumed rows: 3775 x 239, 2005-01-03 through 2019-12-31. Calibration rows [2834,3775) are 941 days,
2016-04-07 through 2019-12-31. Consumed-row SHA-256:
d18ddc3b541ea3037ae9a817b40bd43ee9568c71e62eeeb095fda8c2bd2a4b6c.

## Tests and exact reproduction

R0 confirmed six numerical dependency versions against requirements.lock and their origins in the shared
project .venv. Historical reproduction ran without the torch/NumPy shim, with the deterministic single-thread
BLAS environment. All numerical invocations were serialized under the shared execution lock.

| Step | Observed result |
|---|---|
| Initial synthetic RED on historical source | 14 expected missing-DERIVED failures, before reader invocation |
| P-IO synthetic GREEN | 14 passed in 0.64 s; no real fixture |
| Full-opening mutation witness | 2 expected failures at the read-only-memmap spy |
| Complete E6 test file | 27 passed in 8.53 s, including 13 unchanged historical tests |
| pyflakes | Passed, no output |
| Quick, jobs=1 | CSV exactly matches archived SHA-256 |
| Full, jobs=48, bounded resource amendment | CSV and all four figures exactly match archived SHA-256 |
| R6 provenance | All four expected counts matched: 0,2,1,1 |

Independent code review found no material issue in the approved patch. Outside I/O/log changes, production
source text is identical to the historical source. Codex independently rechecked all five full hashes and
compared the reproduced CSV byte-for-byte with the archived CSV.

| Scientific artifact | Expected and reproduced SHA-256 |
|---|---|
| Quick CSV | 874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2 |
| Full CSV, results/e6/e6_cells_phase1.csv | 4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249 |
| e6_phase1_delays.png | ca929eee4cb9f7e3bad769241cb7df8145c3354f6f4da56c6491b73bebc9e897 |
| e6_phase1_delays.pdf | cdffaf9eb2755a98f01193ce206010a57c4979556f79fe24c723e3b55b1dc811 |
| e6_phase1_gadd.png | f14e06cb976cd8099e66daf826f76d474a67eebf512367c02375281c18b34113 |
| e6_phase1_gadd.pdf | 1ed21dc6ee4317eabf0d0c2996d5b3d7b57bdfb00db8a2a91e04984a3777570b |

The full table remains 190 rows x 50 columns: 112 D5 and 78 D6 rows. Reproduction files stay under ignored
logs/23-phase1/; archived scientific files are not overwritten or replaced by the quick run.

## Resource failure, disposition and measured cutoffs

The first full attempt at jobs=48 hit the Codex-chosen aggregate MemoryMax=8G envelope after 18.45 wall seconds.
The failed unit reports oom-kill; no complete scientific output existed. This is an infrastructure failure,
not an observed numerical reproduction mismatch. Its STOP remains recorded. Codex recovered its aggregate
CPU counter: 280.250667 CPU seconds. Its GNU-time report was empty and is not counted as zero.

The written resource amendment allowed one retry only at MemoryMax=64G, with jobs=48, timeout=1200 seconds,
code, configuration and all C3 targets unchanged. Preflight required >=96 GiB available RAM, >=5 GiB disk
and the exclusive lock. No further retry or parameter change was permitted.

The successful retry took 44.89 wall seconds and 815.51 GNU-time CPU seconds. Its aggregate peak memory was
14849028096 bytes; oom and oom_kill counters were zero. The maximum per-process RSS was 666432 KiB, a different
quantity. The preserved scope CPU sample was 815.577751 seconds before scope exit and overlaps the GNU-time
measure; they must not be added. The failed first attempt remains a separate consumed cost.

Covered invocation CPU before closure QA is 1182.820667 seconds: R0/initial RED2.92, P-IO GREEN/pyflakes0.98,
R1–R4 83.16, failed R5 aggregate280.250667, successful R5 GNU-time815.51. Administrative shell costs outside
those receipts are not represented as measured zero. Closeout reindex/hook costs have a separate later cutoff.

An administrative JSONL inspection by the worker used /usr/bin/python3 outside the requested interpreter.
It imported no project code and supplied no scientific result; the deviation is retained, and Codex required
.venv-only practice thereafter. It caused no scientific rerun.

## Scientific interpretation retained

D6 shares calibration rows across representation, energy moments, thresholds and evaluation. Its FPR is
in-sample and descriptive, without a confidence interval. The 72 D6 drift rows retain unavailable G_ADD intervals
under the historical prespecified reporting criterion, not a general theorem requiring ten bootstrap blocks.

D5 uses 2000 independent calibration panels and 2000 independent test panels, conditional on one fit panel.
Its paired intervals describe that conditional experiment. Reported G_ADD is a restricted-time ratio with the
archived censoring labels, not Lorden ADD and not a gain demonstrated at equal attained FPR.
The Gaussian design information is not exact t7 KL. The aligned K=1 sensitivity is not a learned-representation
claim. E6 PCA indices are zero-based; the sealed PCA benchmark uses one-based indices.

Phase2, P4-D/P5-D, JEPA, J4/FROZEN, private data and new 2020+ scientific access remain excluded. E2, E3/D8 and
the sealed PCA/E4 artifacts remain unchanged. The next scientific priority is stream32 under its separate gates.

## Integration gates at this report's cutoff

C1–C3 and C5–C6 are received; targeted C4 passes. The unchanged global commit hook must still complete C4,
with torch/PCA-G1 active and only authorized historical QA access. Native wrapup, authorized AST-only reindex,
explicit staging/range/size/anonymity checks and controlled publication complete C7. None is claimed passed
before its actual receipt. Codex integrates only after these steps; phase1 closure never closes phase2.
