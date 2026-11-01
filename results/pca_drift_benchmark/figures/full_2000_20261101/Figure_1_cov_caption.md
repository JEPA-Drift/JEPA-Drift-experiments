# Figure_1_cov — caption (schema pca_drift_figures/1)

- dataset `SYNTH_GAUSS_EQUICORR`: equicorrelated i.i.d. Gaussian panel, Sigma0 with rho = 0.4; N = 239, T_fit = 1000, H = 250, nmax = 20
- change of regime: covariance rotation of axes [1, 2] by theta_deg = 30.0 (event `B_cov_rotate30`)
- reservoir: P_k = PCA axes 1..k of the frozen Ledoit-Wolf basis, k = 1..20
- information domain: plug-in LW proxy q (GAUSSIAN_PROXY; on the Gaussian background the population joint KL is exact, on t7 it is a proxy), info_kind of the block
- detector family: `COV_QUADRATIC_VECH_SCAN`: same scan on y_t = vech_std(z_t z_t' - C0_centering), p = d (d + 1) / 2
- calibration: predictive_exchangeable_rank_v2, n_cal = 2000, r = 99, bound (r+1)/(n_cal+1) = 0.049975, distinct from the observed holdout FPR
- counts: full n = 2000 per role
- FPR250 per series (observed holdout): RMST_prefix: FPR250 in [0.038, 0.0545]; RMST_selected: FPR250 in [0.042, 0.051]; RMST_energy: FPR250 in [0.049, 0.049]
- RMST intervals: NORMAL_DEFF1, marginal, not truncated; no paired uncertainty is exported in this schema
- oracle flags: COV_SURROGATE_EXPLORATORY, HEURISTIC_COST, ORACLE_TRUE_SIGMA1 — diagnostic bound, not ex ante
- the 250-day cap is a natural axis limit, not evidence that a series reaches it
- missing k: none; FPR mismatch k: none

## Measured (this run)

RMST250 curves (prefix P_k vs selected S*_k, marginal intervals) and holdout FPR250 values above; full counts of 2000 per role.

## Model-based (not tested here)

V = I/M curves are model-based, not observed detection speed; the whole right axis of the covariance figure is EXPLORATORY HEURISTIC: mean-mixture M is not a covariance detector cost.

## Status and limits

Tags: SMOKE_NO_CLAIMS · COV_SURROGATE_EXPLORATORY · EXPLORATORY_HEURISTIC · DETECTOR_FAMILY_MISMATCH. SMOKE_NO_CLAIMS: no claim is made from these smoke counts.
