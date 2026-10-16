# Article B deviations digest (README §6 + `docs/DEVIATIONS.md`)

Source: `~/The-Whitening-Advantage-Experiments` @ `a05f0d9c654b6692e626080c298acebc0f0a0b5c` (read-only). Register: 62 entries (15 D3, 25 D2, 4 D1, 18 without severity). Entries of the five streams that feed D1/D2:

- `R00-detection-label-stream` (D3): v87 describes the Concept stream as the sign-error stream of a Hoeffding Tree; no detector arm passes through a classifier — detectors monitor the label stream `1{r>0} - q_hat`, the error stream of a constant predictor. Null laws unchanged.
- `R01-concept-binarization` (D3): v87 recentres on the empirical conditional median; the R01 pipeline binarizes at zero and centres by the warm-up frequency of positive returns; no median is estimated.
- `R01-gamma-hat-refit` (D3): v87 refits `Gamma_hat` by QMLE at each onset; the pipeline fits it once per asset on the 2018–2019 warm-up and reuses that value at every onset.
- `R08-delivered-level-above-nominal` (D3): the selected `lambda* = 11.4` delivers an exact level of 5.10%, above the 5% nominal under the weak comparison.
- `R08-campaign-redraw` (D2): lattice levels move (4.29→4.32%, 5.03→5.08%), FPR collapse 0.86→0.95%, FPR inflation 20.8→21.0% under 128-bit re-keying.
- `R15-campaign-redraw` (D2): bootstrap FPR envelope 4.8–6.4% → 4.0–5.9%.
- `R15-scatter-sign` (D2): the caption claims `r >= 0.99`; the measured correlation is negative with |r| ≈ 0.99.
- `R16-dating-misdescription` (D3): v87 describes a Pagan–Sossounov dating with 66 phases; strict Pagan–Sossounov on the four ETF gives 48 — the 66 phases substitute Lunde–Timmermann for SPY.
- `R16-substitution-scope` (no severity): applied consistently, the substitution gives 102 phases (the `symmetric` arm copied to D1).
- `R16-out-of-budget-frac` (D1): 80% published vs 80.3% reproduced at Gamma = 20; floor envelope 55–92% → 50.1–92.1% (D2).

D1/D2 consume the regenerated (post-re-keying) series, not the v87 printed values.
