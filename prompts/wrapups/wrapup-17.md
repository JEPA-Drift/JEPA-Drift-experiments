2026-10-29

# Wrapup — stream 17: shared characteristic path (commit 1), IPCA, P4-C/P4-D, K selection and the P4-D null incident (commit 2)

## Context

- **Prompt and plan.**
  - Prompt: `prompts/streams/prompt-17-ipca.md`. Bootstrap: `prompts/amorcage-17.md`. Shared transfer:
    `prompts/handoff-14-to-17.md` (arbitration Q7: stream 17 lays the generic characteristic scaffold first).
  - Worktree `~/JEPA-stream-17`, branch `stream-17`, base `c284823`.
  - Plan: `prompts/plans/plan-17.md`, revision 3, with « Décision GO intégrée ». GO: `prompts/GO-stream-17.md`
    (verbatim, French).
- **Decisions.** Q1–Q10 granted. Q1: D4 exposed by per-file links. Q2: `c_beta_252` used as stored, its faulty
  denominator quantified. Q3: cash-neutral "constant" only. Q4: rows `C-repr-rows`. Q5: argmax of the held-out R²,
  ties to the smaller K. Q6: D4 aggregate rows committed. Q7: `Z-1` kept. Q8: uncentred second moment. Q9: phantom
  ranks used as is. Q10: two lines of `CLAUDE.md`.
- **Sequence.**
  - Commit 1 (`f67accf`): shared characteristic component; stream 14 notified.
  - 2026-10-28, plan §6 step 3: the P4-D null check on `d3_239` returned FAIL; D3 stop and report, no tuning.
  - Read-only diagnostic D0–D2 under a limited GO (outputs in `/tmp` only).
  - Engineering continuation under the GO addendum `prompts/GO-stream-17-D3.md`: P4-D stays FAIL and
    uncalibrated; no null control is rerun, tuned or added.
- **Environment.** `.venv` only (Python 3.12.9, numpy 2.4.4, scipy 1.17.1, pandas 3.0.6); `make` from
  `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`; threads pinned to 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`,
  `MPLBACKEND=Agg`. Graphify (`graph_stats`: 3620 nodes, 4363 edges) and jCodeMunch (`resolve_repo`) answered by call
  at each session start; the jCodeMunch index dates from 2026-10-23 and predates the uncommitted work.

## Validated Results

1. **Commit 1 (`f67accf`).** `base.Representation.missing`, `chars.load_universe`, `chars.load_continuous_chars`,
   the C path of `extract` (`NEEDS_C`, `CHAR_DATASETS`, `pretrain` hook, `c_sha256`), `d3_char_data()`,
   `CHAR_CASES`, the meta-test and five D3 contracts; `C-worktree-d4`. D2/PCA gate byte-identical; `make check` exit 0
   in 201 s.
2. **IPCA** (`jepadrift/representations/ipca.py`, `docs/sections/ipca.md`, `C-IPCA-design`): restricted IPCA, Γ by
   ALS on pretrain, K and the uncentred whitening on calib, f_t on the observed assets, rank rule
   rank(C̃_t) = P. Registered as `REGISTRY["ipca"]`, `NEEDS_C = {"ipca"}`, `CHAR_CASES["ipca"]`.
3. **Extractions** (`logs/ipca/extract.log`): `d3_239` D = 2, `d3_500` D = 3 (committed); D4 D = 2 (local, ignored).
   On 2026-10-28, two fresh extractions of each D3 panel are byte-identical to each other and to the committed files
   (`cmp`), and the D2/PCA gate re-run after the IPCA registration is byte-identical on its four reference files.
4. **P4 null checks** (D6, `d3_239`, 500 replicates, H = 750; generator
   `python -m jepadrift.pipelines --pipeline P4-{C,D} --dataset d3_239 --null-check --reps 500`):

   | spec | FPR | target | 99 % region | verdict |
   |---|---|---|---|---|
   | P4-C anytime-valid, γ = 15 000 | 0.0020 | ≤ 0.05 | upper end 0.0751 | PASS |
   | P4-C exact, channel 0 / 1 | 0.0420 / 0.0460 | = 0.043947 | [0.0203, 0.0676] | PASS |
   | P4-D bootstrap, λ = 57.464158024122 | 0.0000 | ~ 0.05 | [0.0249, 0.0751] | FAIL |

5. **D0–D2 read-only replay** (2026-10-28; `C-P4D-null-insample`). Script `/tmp/s17diag/diag.py` (SHA-256
   `0874e319fca9345daf0dfe63ff4aa21686e87b6fc7beabefd0a58a8fc8a3185e`), output `/tmp/s17diag/diag.jsonl` (SHA-256
   `76e9bf6e23f707d0c2f54da3cf6bcb625c43a8a583ecf573e826788638fe1e3f`), 20.7 s.
   - D0: the 18 checked artifacts, the Git diff, status and HEAD matched their pre-diagnostic snapshots.
   - D1, P4-D: spec, `run_id`, the 35 saved state fields and λ replay exactly; the 500 saved starts (175 distinct, all
     in [2834, 3025]) equal the starts drawn from their saved seeds; the replayed alarms, alarm indices and FPR match
     row by row; max |q_fit − q_raw| = 0. The 192 calib windows share one CUSUM peak, 57.46415799519721, repeated 192
     times (argmax 2019-01-30, excursion from 2018-10-05); λ exceeds it by 2.9e-8; 0 exceedances.
   - D2, P3-D: same structure; one peak 175.53069329064513 repeated 192 times (argmax 2019-01-31, from 2018-10-02);
     λ exceeds it by 5.6e-8; 0 exceedances; Γ^op = 17.86.
   - Reading: the saved check re-reads the windows that set its threshold, with no fresh D6 randomness in the even
     energy stream. It cannot estimate an out-of-sample FPR; it establishes neither the true D3 FPR nor a failure of
     IPCA.
6. **K selection and characteristic audit** (`experiments/ipca_k_selection.py`, 24.9 s, rows before 2020):

   | panel | target | R²_ho at K = 1..4 | K* |
   |---|---|---|---|
   | `d3_239` | returns | 0.0547, 0.0606, 0.0566, 0.0509 | 2 |
   | `d3_239` | relative returns | 0.0728, 0.0825, 0.0810, 0.0792 | 2 |
   | `d3_500` | returns | 0.0456, 0.0649, 0.0688, 0.0676 | 3 |
   | `d3_500` | relative returns | 0.0676, 0.0840, 0.0864, 0.0875 | 4 (bound) |
   | D4 | returns | 0.0254, 0.0266, 0.0198, 0.0158 | 2 |
   | D4 | relative returns | 0.0273, 0.0278, 0.0228, 0.0194 | 2 |

   GICS sensitivity (P = 15): K* = 6 = K_max on both D3 panels (0.3147, 0.3119). The selected principal states equal
   the extraction states (`55a11b…`, `183a37…`, `301ec1…`). Beta audit: the faulty formula reproduces the stored
   `c_beta_252` bit for bit on the three panels; NaN from the formula = negative faulty denominators (8 / 24 on
   `d3_239`, 60 / 26 on `d3_500`, 4502 / 2231 on D4); 71.1 % / 75.6 % of the `d3_239` beta ranks change under OLS.
   Phantom ranks: none on `d3_239`; 219,639 / 27,945 cells on `d3_500` (momentum, reversal); all four
   characteristics on D4. `k_selection.csv` is byte-identical over two runs.
7. **Tests.** New audit tests red then green: `test_real_d3_239_selection`, `test_beta_denominator_reproduces_stored`,
   `test_char_audit_values_are_finite`. Targeted run (`tests/test_ipca.py`, `test_p4_wiring`): 17 passed in 10.5 s.
   Focused run (`test_ipca`, `test_contracts`, `test_representations`, `test_pipelines`, `test_chars`): 94 passed,
   4 skipped (torch), 235.6 s; pyflakes clean.
8. **`make check`** (`MPLBACKEND=Agg`): exit 0 in 212 s (under the 300 s cap). pyflakes clean; contracts and
   decoupling 28 passed, 4 skipped (torch), the five D3 contracts now running on `CHAR_CASES["ipca"]`; other tests
   270 passed. The pre-commit hook runs `make check` again on the staged tree.
9. **Output SHA-256.**

   | file | SHA-256 |
   |---|---|
   | `results/ipca/k_selection.csv` | `1e91128958cf5796d3e5949b2ffc23e4df6cb6185bfab349e47b9225381ba38e` |
   | `results/ipca/char_audit.csv` | `dfa7e7f37606ff54705c5e04fcb2c631675631d7c365d07d65bce26bec8f881a` |
   | `results/ipca/alarms_P4-C_d3_239_null.csv` | `5339bc9efdb3852b8b7aa3af79e172d4cd1ff1b5314dfd86b7ad7a1081a2b648` |
   | `results/ipca/runs_P4-C_d3_239_null.json` | `3c735ec3f21d7b59ffc03e1953cea45f98007a5428c45d243ce286c1046e7dda` |
   | `results/ipca/alarms_P4-D_d3_239_null.csv` | `6991a227a81c4d5ab6c98f1b75e2ce9cb4698ad0374ad9ad7055bf7ea20b7801` |
   | `results/ipca/runs_P4-D_d3_239_null.json` | `07df410a47d2e738565b8c72b5e60c1626530bb68963a95d2a2dcd6e17ecf146` |
   | `logs/ipca/k_selection.log` | `8544857c353f64ddfc8e18871f7254d27a403008e27f2f5ce26473f598d395ad` |
   | `logs/ipca/extract.log` | `a8c460647db12c51b9bca7c8f3bbd18699f912456b292484857e673cd41994cc` |
   | `logs/ipca/null_P4-C_d3_239.log` | `692c0522c4af5bba2d1a0b0c78459ea5b23e54eb19f9a7b67a982c4429b0dc57` |
   | `logs/ipca/null_P4-D_d3_239.log` | `d65246c18be09897b0bab8e0c67c73567541353ae4721465acfa3e4b74bba88e` |
   | `data/derived/d3_239/z_55a11b…fb.npz` | `935f6c3fee3f7a32e16d775b3dfa3e66a7516fa8eb7a5367be94de11ca4697be` |
   | `data/derived/d3_239/z_55a11b…fb.json` | `b05cbafb276434126a53e66a1a386f02db6bb0b2cce32f402c00d6bb32dcd0c4` |
   | `data/derived/d3_500/z_183a37…1a.npz` | `6549ed9df44ca8db6225a28103b6aefd7567e6cfaefec62760e3fbb038e7865b` |
   | `data/derived/d3_500/z_183a37…1a.json` | `6aa52fdd8f7fb7d85e20ca39fe97028dba98aaf16bdfd70e97362a251fc0a82c` |

## Errors and Dead Ends

- **Plan revision 2** was rejected by the technical GO (five corrections, all in revision 3).
- **Rank rule.** The revision-1 eigenvalue rule put its tolerance below the rounding of `eigvalsh`; replaced by
  `matrix_rank` (R1).
- **P4-D null check: FAIL, D3 stop.** First diagnostic plan drafted in plan mode overclaimed: robustness to seeds and
  replication count, "not an IPCA defect", and 941/750 read as an effective sample size. Corrected by the researcher:
  the replay establishes the in-sample reuse of the calibration windows and the common peak, nothing more.
- **`experiments/ipca_k_selection.py`** first failed with `ModuleNotFoundError: jepadrift`: unlike the other
  experiment scripts, it lacked `sys.path.insert(0, repo root)`; fixed with the repository pattern.
- **D4 relative beta error NaN.** The first audit run gave NaN median, p99 and max on D4 (0/0 where the OLS beta is
  exactly 0). `test_char_audit_values_are_finite` was written and failed first; the metric now excludes those cells
  and reports them (`beta_ols_zero_cells`: 9487 / 96 on D4, 0 on D3); `char_audit.csv` has 114 rows and
  `k_selection.csv` is unchanged.

## Current State

- Commit 2 carries IPCA, its registration, P4-C/P4-D, the K-selection script and CSVs, the D3 extractions, the P4
  null artifacts (P4-C PASS, P4-D FAIL), the tests, `docs/sections/ipca.md`, the interface, contract and pipeline
  docs, `C-IPCA-design`, `C-IPCA-K`, `C-D3-beta-denominator`, `C-D3-chars-phantom`, `C-P4D-null-insample`, the two
  `CLAUDE.md` lines, the GO addendum and this wrapup.
- P4-D's FPR status is **uncalibrated**: it is not a calibrated J4 comparator, and the P3-D D6 window diagnostic is
  not an out-of-sample FPR estimate.
- Not done, outside the authorized scope: `tools/reindex_graphify_jcodemunch.sh`, fetch, rebase, push.

## Vigilance Points

- **Independent null control.** Any future control of the P3-D/P4-D bootstrap reading needs a separate written GO
  fixing data source, independence unit, calibration/evaluation split, sample size, target, uncertainty interval and
  verdict rule before any result; a D5 control certifies its own model only.
- **Replay evidence outside the repository.** `/tmp/s17diag/` (script, output, snapshots) is not durable; the hashes
  above and in `C-P4D-null-insample` identify it.
- **Inherited data defects.** The beta denominator (all panels) and phantom ranks (`d3_500`, D4) enter Γ, K, the R²
  and the extractions; rerun after a data correction. D3 and D4 survivorship bias remains.
- **Censored selections.** `d3_500` relative returns (K* = 4 = min(K_max, P)) and the GICS sensitivity
  (K* = 6 = K_max).
- **Logs.** `logs/ipca/extract.log` and `k_selection.log` carry D4 aggregate lines (file name, hash, row range, R²),
  allowed by Q6 and R7; no path under `data/derived/d4_eurofidai/` is staged.
- **Merge with stream 14.** Conflicts are expected on `extract.py`, `tests/test_contracts.py`, `CLAUDE.md` and
  `docs/DEVIATIONS.md`; 14 rebases on 17 (Q7). The pretrain hook is detected by `hasattr(rep, "pretrain")`.

## Recommendations

- **Researcher.** Decide whether and how to control the P3-D/P4-D bootstrap reading out of sample (GO addendum
  conditions); until then report P4-D as uncalibrated.
- **Data stream.** Correct the `_compute_chars` beta denominator and the phantom ranks, then rerun
  `experiments/ipca_k_selection.py` and the IPCA extractions.
- **Stream 14.** Rebase on commit 2 and reuse `d3_char_data()` and `CHAR_CASES`.
- **End of stream.** Run `tools/reindex_graphify_jcodemunch.sh`; fetch, rebase and push only after an explicit GO.
