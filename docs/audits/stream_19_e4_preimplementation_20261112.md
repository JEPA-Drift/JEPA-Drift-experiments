# Stream 19 E4: pre-implementation checks, 2026-11-12

Scope: the researcher's conditional GO, recorded in `prompts/GO-stream-19-e4-science-20261112.md`. No E4 code, cost pilot or
scientific campaign has run. The following source observations and analytic checks precede the separate code plan.

## Existing eigenpair convention

Read at `ef48fa299c9d3ca6c32022dc5af2e509df903c55`: `jepadrift/stats/covariance.py:17-21`, SHA-256
`0af9e66ce8e32dd45b148c37b789cbd20393febbd22c4544407de627e75cda47`.

`eigh_desc` calls `numpy.linalg.eigh`, reverses its ascending eigenvalue and eigenvector arrays, then multiplies each column by
-1 when its coordinate sum is negative. A zero sum keeps the solver's sign. It has no declared gap tolerance, canonical basis
for repeated eigenvalues, or ambiguity refusal. Reversing tied solver outputs is not a specified stable descending sort.

Callers were searched: `representations.pca`, `injection.fit_background`, `jepa.ca_tjepa` and representation tests. The existing
`test_eigh_desc_sorted_signed` requires nonnegative column sums and equality to the background fit. Changing the default sign
globally would alter those existing contracts. A local E4 convention or an explicitly reviewed opt-in must preserve historical
default calculations; the code plan must choose the smallest coherent approach and name every touched caller.

The proposed E4 tolerance is exactly 64 * eps_float64 * max(1, lambda_max), fixed before draws. Sort decreasing stably,
orient each column by its first maximum-absolute coordinate, and reject unresolved eigenvalue blocks. Sign choices alone do
not canonicalize a repeated-eigenvalue subspace. The plan must specify the refusal's cell scope and how missing grid cells
prevent an outcome-selected slope. No numerical rule establishes statistical identifiability of degenerate individual axes.

## Deterministic detectability diagnostic

This check uses algebra and distribution functions, with no random draw, fitted sample, null calibration or detector run.
Its complete numeric journal is `logs/stream_19_e4_code/analytic-precheck-20261112.txt`, SHA-256
`3175f210495fd5149477a6a4422c34f0491d390c84428c981df83d6783fbbf87`. A tested script and FAIR CSV reproduction must be
included in the code plan before numeric tables or a campaign report are published.

Let d = N - 1, P = I - 11'/N, u be uniform on the residual unit sphere independently of the null-fitted basis, and v any
unit fit direction. The Gaussian information fraction is

    a(v) = J(v)/I* = (1-rho) (v'u)^2 / ((1-rho) + rho (v'1)^2).

If Pv is nonzero, write w = Pv/||Pv||. Then a(v) <= (w'u)^2, whose distribution is Beta(1/2, (d-1)/2). If Pv is zero,
a(v) = 0. Thus, conditional on any independent fitted basis, a union bound over its N axes gives

    P_direction(max_j a(v_j) > q_N) <= eta,
    q_N = Beta.isf(eta/N, 1/2, (N-2)/2), eta = 0.05.

This bound does not assume independent empirical PCA coordinates or replace their joint KL by a sum of marginal KLs.
For the Gaussian model, a channel with information fraction a has sign probability Phi(sqrt(2 I* a)). For the unit-variance
shared-scale t7 construction it is F_t7(sqrt(7/5) * sqrt(2 I* a)); I* remains INFO_GAUSS_PROXY_T7, not t7 KL.

For the fixed scalar betting grid lambda in {0.1, 0.2, 0.3, 0.4}, a sign probability p >= 1/2 gives mean log increment

    g_lambda(p) = p log(1+lambda) + (1-p) log(1-lambda).

A diagnostic one-atom evidence clock is log(8 N gamma_H) / max_lambda g_lambda(p), using p at q_N for an optimistic
alignment envelope. The factor 8 N describes a single dominating signed bet in the dictionary average. This clock ignores
resets, finite-path fluctuations and simultaneous channel contributions. It is neither an RMST/ADD bound nor a power or
censoring guarantee. It applies to the fixed-bet spectral dictionary, not the distinct predictable stakes of P3-CS(b).

At the largest approved N values the deterministic check puts this one-atom secondary-reading clock beyond H, even at that
optimistic alignment envelope. This flags a material censoring risk; it does not establish failure of the primary rank reading,
whose threshold has not been calibrated. The direction oracle retains an N-invariant scalar law. The code plan must reproduce
these checks without simulation, retain the distinction between the two readings, and report the risk before requesting full GO.
I*, the grid and the low-censoring qualification are unchanged. No power-seeking pilot or hidden grid selection follows.

## Implementation risks for technical review

- A shared scalar calibration must be independent of every holdout/alternative and computed once, across N and backgrounds.
  Dictionary calibrations stay per cell. Sharing a threshold never merges holdout observations or licenses independent CIs
  for paired contrasts.
- Rank maxima and the strict/nextafter rule must stay in a consistent statistic space. Converting a log threshold through
  exp and log can erase its nextafter separation and turn a tie into an alarm. The plan must specify and test the comparator.
- The registry supports P3-C and P3-CS(b) anytime-valid detection, not an existing rank-calibrated reading. The plan must
  reconcile registry reuse, log-path access and frozen fit state explicitly, without mislabelling rank output as anytime-valid
  or changing the sealed rank-rule implementation. No unreviewed registry bypass or duplicated scientific kernel is approved.
- Numerical invariance across workers concerns scientific fixture CSVs; measured CPU times and RSS necessarily vary and must
  not be included in a byte-equality claim. Seed domains and identities must distinguish pilot from scientific roles.
- The pilot's persisted outputs are CPU/memory/cost evidence only. No delay, FPR, detection rate, slope, alignment result or
  monitored path may leak into its logs or outputs. Any cost-only fixtures for inference overhead must be declared as such.
- The later full campaign must be disabled in the present CLI. No real-data reader, effective FROZEN or J4 route is needed.
