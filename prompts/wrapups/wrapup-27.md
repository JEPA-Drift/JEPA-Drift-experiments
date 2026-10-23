2026-10-22

# Wrapup — stream 27: E10 linear stage (F1, P1-C and P3-C), sign streams outside central symmetry

## Context

- **Prompt and plan.**
  - Prompt: `prompts/streams/prompt-27-e10.md`, as tightened at `2b0b1cd`. That revision covers the gates, the
    bounded recentred e-process, the shared bits, the RMST ratio, the FPR comparison, the iid reference, the
    retrospective placebo and the oracle asset. The bootstrap prompt is `prompts/amorcage-27.md`.
  - Worktree `~/JEPA-stream-27`, branch `stream-27`. Base: `2b0b1cd`, the local `main` with stream 8b merged at
    `33d847d`.
  - Plan: `prompts/plans/plan-27.md`, revision 4, harmonized, with « Décision GO intégrée ».
  - GO: `prompts/GO-stream-27.md`, a verbatim transcript of the exploration instructions, the three plan reviews and
    their complement, the GO, the harmonization request and the start signal.
- **Decisions.**
  - B1: F1 only. F2 on D3 comes with a later plan revision; P5-C waits for the frozen checkpoint of stream 16.
  - B2: no equal-false-alarm claim.
  - B3: the GJR and shock generator is local to the script; `jepadrift/sim.py` is untouched.
  - H1–H5: H = 750 and γ_H = 15,000; SR ∈ {4, 8, 16}; the D5 grid; the `zero_neg` arm on P1-C over backgrounds
    with zeros; the H0 references of plan section 5; sizes 2,000 / 500 / 20,000.
- **Four harmonized labels**, kept in code, CSV and log:
  - `fpr_iid_mc` is a Monte Carlo estimate, checked within a 99 % binomial tolerance;
  - `design=iid_scenario`;
  - `reference_kind=symmetrized_window`;
  - `zero_neg` has an invalid sign-stream null and no FPR guarantee on backgrounds with zeros.
- **Environment.**
  - `.venv` only: `.venv/bin/python` 3.12.9 and `.venv/bin/pytest`; Trading never activated.
  - `make` comes from `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`.
  - Python calls pin OMP/MKL/OPENBLAS threads to 1, `MKL_CBWR=COMPATIBLE` and `PYTHONHASHSEED=42`.
  - Runs used 48 processes.

## Validated Results

1. **Deliverables.** `experiments/e10_robustness.py`, `configs/e10.yaml` and `tests/test_e10.py` (13 tests, 17 s).
   - P1-C runs on the monitors core (`cusum.P1["P1-C/C"]`) without a registry entry.
   - The P3-C `half` arm runs through `pipelines.run_pipeline` on a Z input. The `qhat` arm reuses the same bits
     (run_pipeline's coin convention `[*seed, 7]`, bit identity tested).
   - The exact state equals `fit_pipeline` on the exact spec (tested).
   - The local `d5_panel` reproduces `sim.garch_panel` bit for bit without GJR or shock (tested). For the shock, its
     in-loop daily signs equal the post-hoc symmetrization bit for bit (tested).
   - Deviations: `C-e10-backgrounds`, `C-e10-streams` and `C-e10-readings` in `docs/DEVIATIONS.md` (English).
2. **Full run.** `python experiments/e10_robustness.py --stage linear --families F1 --out results/e10` took 286 s on
   48 processes and wrote 4,004 cells rows and 144 gains rows.
   - `results/e10/e10_cells.csv` 9998f9422794078a515a7ba1a2701802ef9e162b3d183e42fc71e3ec1799da56
   - `results/e10/e10_gains.csv` 4225c18a8101412164b6e99eb78b0e5f4607d153427e276314c4c4e624d2843c
   - `figures/e10/fpr_inflation.png` f7ed3d2a9f7793982e9d33ac6b0ac808647f02b5e4924f8e030559404be89189
   - `figures/e10/fpr_inflation.pdf` 1e8f9a6b15cbfe26bfc3a0d8d7cf465d1f3d04e04b716ae95edd070ca03b0b68
   - `figures/e10/gains.png` 6439b41c546a7e47c9edbe28282fb6407a1bcc8eb55b19acb58b066b2df2e5d4
   - `figures/e10/gains.pdf` 11b017c99fb1b7712703a9a363d81862fd22e08e75f5ca7234d350b59a3d1c53
   - `logs/e10/run.log`: input hashes (`d2_us97` 333d2b07…, `d3_239` a266fbab…); frozen raw bases `85147fd9…` and
     `6c44d64a…`, equal to the committed sidecars; config `e10.yaml` ac8f135a….
3. **Exactness under valid nulls (Lemma 2).** The lattice level at H = 750 is 0.043947 (L = 45, threshold 9.1).
   - Valid backgrounds covered: t₃, t₄, t₅, t₇, GJR 0.05 and 0.10, zeros 2 % and 5 % with coin ties, the matched
     symmetric shock generators, and D6 on D2 and D3.
   - Across 317 single-stream `half` exact rows (P1-C assets and P3-C channels), 3 fall outside the 99 % binomial
     region; about 3.2 are expected under independence. The mean rate is 0.04425.
   - On the market channel ch0 the rates are 0.040–0.0555, all inside the 99 % region. GJR leverage, heavy tails and
     zero returns with coin ties leave the level unchanged.
4. **`fpr_iid_mc`** (Monte Carlo, iid scenario).
   - `half` exact, single stream: 880 / 20,000 = 0.0440, within the 99 % tolerance [0.0402, 0.0477].
   - Single stream: `half` anytime-valid 0.00115; `qhat` exact 0.0677; `qhat` anytime-valid 0.00515.
   - Dictionaries with independent channels: 6 channels, `half` 0.0008 and `qhat` 0.00715; 11 channels, `half` 0.0016
     and `qhat` 0.01025.
5. **Common asymmetric shock** (invalid null; matched valid generator in parentheses).
   - Market channel, `half` exact:
     - w = 0.25: 0.092 (0.048), inflation +0.044 with paired-bootstrap 95 % CI [0.029, 0.060]; `fpr_pred_iid` 0.0884
       at q = 0.5244.
     - w = 0.50: 0.3915 (0.0445), inflation +0.347 [0.323, 0.370]; `fpr_pred_iid` 0.390 at q = 0.5602.
     - The gaps to the iid reference are +0.0036 and +0.0015, reported without criterion.
   - Anytime-valid P3-C dictionary, `half`: 0.101 at w = 0.50 (0.0005), above α = 0.05 on an invalid null; 0.0025 at
     w = 0.25 (0.0020).
   - Recentring on calib q̂:
     - `qhat` exact on ch0: 0.073 (0.070) at w = 0.25 and 0.0605 (0.0615) at w = 0.50, inflation CIs covering 0;
     - `qhat` dictionary: 0.0085 and 0.0095.
6. **Cost of recentring on valid nulls.**
   - `qhat` exact: 0.059–0.0775 on ch0 and 0.064–0.071 for the median P1-C asset, against about 0.044 for `half`.
   - `qhat` dictionary: 0.0035–0.011, against 0–0.003 for `half`.
   - These rates match the `qhat` coin scenario (0.0677 exact). They are the price of the q̂ estimation error over
     941 calib days.
7. **Zero = negative arm** (P1-C; invalid sign-stream null).
   - `zero_neg_half` exact, median over the assets: 0.0902 at a 5 % zero share and 0.0515 at 2 %.
   - `zero_neg_qhat` exact: 0.064–0.068, the same as `qhat`.
   - On D6 the rates are 0.0435 (D2) and 0.046 (D3), at zero shares of 0.7–0.8 %.
8. **Raw placebo.** Retrospective and descriptive: 2,019 windows on D2 and 2,020 on D3, every fit made on the later
   calib rows.
   - ch0 `half` exact: no alarm in any window on either dataset, so the rate CI is NA (constant indicator).
   - Its symmetrized-window reference is 0.0431 on D2 and 0.0495 on D3. `fpr_pred_iid` at the pooled pretrain rates
     (0.5397, 0.5381) is 0.176 and 0.164: the raw PC1 bits are not i.i.d. Bernoulli at a constant rate.
   - ch0 `qhat` exact, with the raw calib q̂ (0.576, 0.5675):
     - D2: 0.432, with a HAC 95 % CI of [0.123, 0.805];
     - D3: 0;
     - descriptive contrasts on symmetrized windows: 0.622 and 0.509.
   - Other channels and assets: P3-C `half` exact up to 0.311 (D2) and 0.349 (D3); P1-C up to 0.235 (`half` exact) and
     0.583 (`qhat` exact).
9. **Gains** (median asset against the P3-C dictionary; RMST ratio restricted to H, paired-bootstrap 95 % CI).
   - SR 16:
     - D5: 7.1–7.9; D6: 5.5–5.7 on D2 and 6.3–6.4 on D3;
     - P3-C is never censored, so the ratio bounds the ADD ratio from below.
   - SR 8:
     - D5: 4.9–7.6, where P3-C is uncensored;
     - D6: 2.9–3.1, with P3-C censored in 0.2–1 % of replicates, so there is no bound.
   - SR 4:
     - D5: 1.8–4.7; D6: 1.2–1.4;
     - P3-C is censored on every D5 background except t₃, and in 28–51 % of D6 replicates, so this is the restricted
       estimand only.
   - FPR beside the gains:
     - on valid backgrounds, the same-asset H0 FPR is 0–0.008 and the P3-C dictionary's is 0–0.011;
     - under the w = 0.50 shock, `half` arm, the dictionary reaches 0.101 against ≤ 0.005 for the asset, and the paired
       difference CI excludes 0: those gains are at unequal false alarm.
   - Oracle assets are exploratory.
10. **Determinism.**
    - Two `--quick` runs (48 and 7 processes) give identical SHA-256: cells baa666d8…, gains 2932d412….
      Their figures are byte-identical.
    - The two full runs differ only in the 46 Wilson lower bounds fixed between them (Errors 3).
11. **`make check`** (`.venv` with conda-forge make on PATH), run after the wrapup and the reindex, in 3 min 16 s:
    pyflakes clean; 22 passed and 4 skipped (contracts and decoupling); 241 passed and 4 skipped (rest).
    `git status` was unchanged afterwards.

## Errors and Dead Ends

1. **deff test expectation.** An i.i.d. indicator series can give an estimated deff slightly below 1, hence
   n_eff > n. By the prompt's rule 1 ≤ n_eff ≤ n its interval is NA. The test now uses an autocorrelated series for the
   valid case and asserts NA for a negatively autocorrelated one.
2. **Raw inflation interval.** With a constant raw indicator, the HAC interval of raw minus symmetrized came from the
   symmetrized series alone. It is now NA whenever the raw rate interval is NA.
3. **First full run stopped in `plot()`.**
   - Cause: statsmodels' Wilson lower bound at k = 0 is 1.08e-19 instead of 0, so an error bar was negative.
   - Root fix: `wilson()` clamps the interval to contain k/n within [0, 1]. Figure bars are also clipped at 0, since a
     percentile bootstrap interval may exclude its estimate.
   - The two full runs differ only in those 46 lower bounds: 28 `rate_lo`, 6 `fpr_ref_lo`, 6 `fpr_p1_lo`,
     6 `fpr_p3_lo`.
4. **Graphify MCP did not connect in this session** (CONNECTION_CLOSED). Exploration used jCodeMunch and direct reads;
   the end-of-stream reindex uses the CLI script.

## Current State

- Branch `stream-27` = `2b0b1cd` plus one local Conventional Commit.
  - Not fetched, pushed or merged, as the GO asks.
  - A later publication uses `git push origin stream-27`.
- `results/e10_quick/` is removed and not committed.
- `logs/e10/run.log` is force-added: `logs/` is ignored, and earlier run journals are tracked the same way.
- Committed:
  - code and config: `experiments/e10_robustness.py`, `configs/e10.yaml`, `tests/test_e10.py`;
  - outputs: `results/e10/{e10_cells,e10_gains}.csv`, `figures/e10/{fpr_inflation,gains}.{png,pdf}`,
    `logs/e10/run.log`;
  - documents: `docs/DEVIATIONS.md`, `prompts/plans/plan-27.md`, `prompts/GO-stream-27.md`,
    `prompts/wrapups/wrapup-27.md`.

## Vigilance Points

- **No equal-false-alarm claim (B2).** Each gain carries the same-asset and dictionary H0 FPR with their paired
  difference. Under the w = 0.50 shock the `half` dictionary FPR is 0.101.
- **RMST ratio.** It bounds the ADD ratio from below only where P3-C is never censored: SR 16 everywhere, SR 8 on D5.
- **`qhat` arm.** It has no guarantee and costs about +0.02–0.03 on exact readings under valid nulls. On raw data q̂
  is not stationary (D2 PC1: 0.576 in calib against 0.540 in pretrain), and the recentred exact reading reaches 0.43
  on D2 ch0.
- **Raw placebo.** It is retrospective (fit on the later calib) and descriptive, and most of its rate intervals are
  NA. The `qhat` and `zero_neg` contrasts are not null references.
- **Reference scope.**
  - `fpr_iid_mc` estimates the exact law only for the `half` arm of a single stream. Dictionary coins are an iid
    scenario.
  - `fpr_pred_iid` is not a criterion.
- **Multiplicity.** The base D5 ch0 `half` exact rate (0.0555) lies inside the 99 % region, but its 95 % Wilson
  interval excludes 0.0439. Across the 317 valid single-stream rows, 3 fall outside the 99 % region, against 3.2
  expected.
- **K choices.** D6 fits P3-C with K fixed at the raw MP value (5 and 10); D5 uses K = 5 as an integer
  (`C-e10-backgrounds`).

## Recommendations

- **F2 complement on D3 (B1).** Use `jepadrift.data_loader.chars` through a new plan revision; `cell_rows` and
  `gain_rows` can be reused.
- **P5-C after the frozen checkpoint of stream 16.** `monitor()` takes any fitted state whose odd head yields `z_odd`.
- **E3 (stream 13).** Its raw-placebo arm overlaps `raw_rows`. Move `coin_bits`, `alarms`, `deff_rate_ci` and the
  Wilson clamp to `jepadrift/` when E3 becomes their second consumer.
- **Equal-FPR statement.** If one is ever needed, fix a margin and run a paired TOST (B2).
- **Optional.** A calibrated symmetrized null for `qhat` on raw data: same state, q̂ re-estimated on a symmetrized
  calib.
