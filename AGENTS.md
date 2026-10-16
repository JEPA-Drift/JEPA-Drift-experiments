# JEPA-Drift (Article C) — project memory for coding agents

## Scientific purpose
Sequential detection of drifts in daily equity cross-sections. Claim under test: a representation
z_t = phi(x_t; C_t) concentrates the Kullback-Leibler (KL) divergence of a drift into a few directions,
so that exactly calibrated monitors detect it faster than univariate or pooled monitors.
The data-processing inequality (DPI) forbids any KL increase: gains come from concentration only.

## Glossary
- x_t in R^N: log returns of N assets on day t. C_t: characteristics known at the open of day t.
- ADD: average detection delay, Lorden worst case (monitor state reset at the onset).
- ARL0: average run length to a false alarm under H0. gamma: false-alarm budget.
- I: per-day KL of a drift (nats). With SR the annualized Sharpe ratio of the drift-tangent portfolio,
  I = SR^2/504.
- Evidence budget ("Sharpe ceiling"): tau_gamma = ln(gamma)/I = 504 ln(gamma)/SR^2 trading days is the
  expected time for a monitor that knows the onset and the direction to gather evidence gamma (exact,
  Lemma 1). It is NOT the Lorden-optimal ADD at ARL0 = gamma, which is Phi(gamma*I)/I
  (jepadrift/floors.py): 142 days instead of 2,787 for SR = 1, gamma = 252. Always state the reading:
  budget | anytime-valid (e-detector stopped at gamma) | exact (ARL0 calibrated to gamma).
- CUSUM (Article B convention): S_t = max(0, S_{t-1} + s_t - delta); alarm iff S_t > lambda (strict).
  Bilateral = one-sided CUSUMs on s_t and -s_t, the first alarm wins.
- Sign stream: b_t = 1{u_t' phi(x_t; C_t) > 0} with phi odd in x and u_t known at t-1. Under any
  centrally symmetric null it is i.i.d. Bernoulli(1/2) whatever the volatility (Lemma 2); ties are
  broken by an independent fair coin. Article B's Concept detectors monitor the label stream
  1{r_t > 0} - q_hat (a constant predictor), not a classifier's error stream.
- Lattice: a CUSUM on a two-point stream reaches only discrete false-alarm levels. Compute them exactly
  (jepadrift/monitors/lattice.py) and pick the nearest level <= nominal under the strict rule.
- e-detector: statistic M_n >= 0 with E_inf[M_tau] <= E_inf[tau]; alarm at M_n >= gamma gives
  ARL0 >= gamma. Channels are combined by averaging e-detectors, never by multiplying them.
- Drift families, injected in return space only, never in z: F1 factor premia B_t*dlambda;
  F2 characteristic-driven breadth (C_t*dgamma) orthogonalized to the loadings; F3 market-mode
  translation; F4 second order (factor rotation or covariance deformation).
- Backgrounds: D5 Monte Carlo (Gaussian i.i.d. latent; GARCH(1,1)-t7); D6 symmetrized real panels
  (each whole day multiplied by one Rademacher sign: keeps |x|, correlations and volatility
  clustering; erases location drift and leverage).
- PCA-orthogonal: PC1 (market) is a separate monitored channel; the residual is PC2..PC(K+1) with K at
  the Marchenko-Pastur edge, or the full residual. PC1 is never discarded silently.
- Gains: G_floor = I_B/I_A (exact); G_ADD_av = ADD ratio at equal anytime-valid threshold (primary);
  G_ADD_ex = ADD ratio at equal exact ARL0 (exact sign streams only); G_SR = ratio of the smallest SR
  detected within H days with probability >= 1/2.
- Pipelines: P1-C/P1-D univariate Concept/Data; P2-C pooled signs; P3-C/P3-D PCA-orthogonal; P3-KF
  PCA tail (prior art); P3-CS degree-0 cross-section and ranks; P4 IPCA/CD-DFM; P5 JEPA; P6 BAF;
  P7 oracle with known drift direction.

## Data, splits, leakage
- D1 ETF-4 (SPY, PFF, VNQ, BWX), D2 US-97 survivors, D3 S&P 500, D4 EUROFIDAI (proprietary),
  D7 BAF (synthetic tabular), D8 optional sensor panels.
- D2-D4 splits: pretrain [2005-01-01, 2016-01-01), calib [2016-01-01, 2020-01-01),
  monitor [2020-01-01, end]; embargo of 65 trading days after each boundary. BAF months: 0-2 / 3 / 4-7.
- Before milestone J4 (2026-11-08) no hyperparameter, threshold, D* or design choice may use, or be
  evaluated on, the monitor window. After J4, test-window runs require the frozen configuration hash.
- EUROFIDAI data never leave this machine: data/raw/eurofidai/ and data/derived/d4_eurofidai/ are
  ignored and blocked by the pre-commit hook, and nothing under those paths may ever be committed,
  logged or pushed. `git push` of the rest of the repository is authorized (end-of-stream
  workflow, see Engineering rules) while the repository address is not shared publicly and not
  linked to a publication.

## Engineering rules
- Python 3.12. Before importing numpy: OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1,
  MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42. Seeds: np.random.SeedSequence keyed on
  (stream, cell, replicate); results must not depend on the number of workers.
- jepadrift/monitors/ imports numpy only (never torch, jepadrift.jepa or jepadrift.representations).
  jepadrift/jepa/ never imports jepadrift.injection or jepadrift.monitors.
- Scripts: argparse, `if __name__ == "__main__":`, logs in logs/<stream>/, CSV in results/<stream>/,
  figures (PNG + PDF) in figures/<stream>/ drawn from CSVs only. No notebooks.
- Every reported number traces to a CSV and a script (docs/MAPPING.md). Deviations from the plan or
  from Article B go to docs/DEVIATIONS.md under an identifier C-<topic>.
- Run `make check` before every commit.
- End of stream (after each prompt/stream is processed): run `tools/reindex_graphify_jcodemunch.sh`,
  then `make check`, then an explicit commit (Conventional Commits), then `git push origin
  <current-branch>`. Push only while the repository address is not shared publicly and not
  linked to a publication (anonymous-submission companion: commits stay anonymized, no new author
  or institution identifiers), and only after checking that the pushed range contains no path
  under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` and no file over 50 MB.
- Article B reference code: ~/The-Whitening-Advantage-Experiments (local checkout, read-only, used as-is at its current
  commit; never clone the remote github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments).
  Its code, not the text of its v87 manuscript, is the reference; read its docs/DEVIATIONS.md.
