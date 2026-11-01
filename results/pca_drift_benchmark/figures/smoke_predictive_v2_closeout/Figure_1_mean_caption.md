# Figure_1_mean — caption (schema pca_drift_figures/1)

- dataset `SYNTH_GAUSS_EQUICORR`: equicorrelated i.i.d. Gaussian panel, Sigma0 with rho = 0.4; N = 239, T_fit = 1000, H = 250, nmax = 20
- change of regime: residual mean shift on axes [10, 20] scaled to I_target = 3.0 nats/day (event `C_residual_mean`)
- reservoir: P_k = PCA axes 1..k of the frozen Ledoit-Wolf basis, k = 1..20
- information domain: plug-in LW proxy q (GAUSSIAN_PROXY; on the Gaussian background the population joint KL is exact, on t7 it is a proxy), info_kind of the block
- detector family: `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM`: W_t = max_{1<=tau<=t} [-(p/2) log1p(n s2) + s2 |S_t - S_{tau-1}|^2 / (2 (1 + n s2))], alarm W_t >= h, every start tau evaluated
- calibration: predictive_exchangeable_rank_v2, n_cal = 40, r = 1, bound (r+1)/(n_cal+1) = 0.0487805, distinct from the observed holdout FPR
- counts: smoke n = 40 per role; full 2000 per role planned, not executed
- FPR250 per series (observed holdout): RMST_prefix: FPR250 in [0, 0.075]; RMST_selected: FPR250 in [0, 0.1]
- RMST intervals: NORMAL_DEFF1, marginal, not truncated; no paired uncertainty is exported in this schema
- oracle flags: ORACLE_INJECTED_DELTA — diagnostic bound, not ex ante
- the 250-day cap is a natural axis limit, not evidence that a series reaches it
- missing k: none; FPR mismatch k: none

## Measured (this run)

RMST250 curves (prefix P_k vs selected S*_k, marginal intervals) and holdout FPR250 values above; smoke counts of 40 per role, SMOKE_NO_CLAIMS.

## Model-based (not tested here)

V = I/M curves are model-based, not observed detection speed; the whole right axis of the covariance figure is not applicable.

## Status and limits

Tags: SMOKE_NO_CLAIMS · GAUSSIAN_PROXY. SMOKE_NO_CLAIMS: no claim is made from these smoke counts.
