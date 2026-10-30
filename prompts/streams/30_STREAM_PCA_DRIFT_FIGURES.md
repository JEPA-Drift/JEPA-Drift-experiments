## PROMPT 30 — Two primary PCA figures: mean-shift comparison and covariance-rotation diagnostics

**ROLE**: Claude Code visualization stream working only in an isolated audited worktree. Implementation target: `experiments/figures/plot_figure_1.py`. Read experiment request §4, Codex kickoff, runner schema and table assembly contracts; plan in read-only mode first. Do not generate new simulated data or run new detectors from this script; **plot exactly the signed aggregate files**.

### 1. Scientific message and plot design

Both figures compare (a) **historical-variance selection** and model-based information selection from the **same 20 PCA candidate axes** and (b) **measured** restricted delays. User requests a top dual-y-axis panel and a lower delay panel, sharing x = `k=1..20` (index of spectral reservoir P_k).

**Top panel:** left y (blue continuous) `CPV_k` calculated from **all N eigenvalues** but accumulated only to k=20; thin 90% horizontal threshold if within y-range, with intersection annotation **only when actual CPV crosses** in top20. Right y: red dashed `V_pref(P_k)`, green solid `V_opt(S*_k)` from the **specified objective type**, both read from runner/table values; line legend includes `model-based, not observed detection speed`. Plot both V series **only** when they have comparable mathematical interpretation. Mean-shift Gaussian model is supported; Student background means Gaussian surrogate. Covariance figure, if requested, must use `I_cov_joint(S)` and explicitly label any `V=I_joint/M` as **exploratory heuristic**, not theorem; never plot `Σ q_k^cov` as true joint KL.

**Bottom panel:** red `RMST250(prefix P_k)` and green `RMST250(selected S*_k)`, with paired uncertainty if available. These are **actual recorded restricted delays**, not `1/V`, not interpolations, not values from illustrative examples. Explain `RMST250 = mean[min(T,250)]`, `FPR250` measured on **independent holdout null** and calibrated separately. Display FPR range for each curve/series in caption or small text; where methods are not FPR comparable, mark the mismatch and avoid a strong comparative claim. Censoring cap at 250 days is a natural y-axis limit, not proof that any particular series reaches 250.

**Most important instruction:** the source document's desired shapes (`CPV ~35→95%`, 90% at k14, V red maximum at k2, green plateau, RMST red >180 at k11, 250 at k20, selected ~12 days) are **hypotheses, not data**. Do not enforce, fake, smooth, interpolate, extrapolate or annotate these numbers unless actual aggregates support them. A flat or counterintuitive figure is a valid scientific result. No invented 95% confidence intervals.

### 2. Input and CLI

Read `results/pca_drift_benchmark/{manifest.json,spectra.csv,selection.csv,aggregates.csv}` and validated table data using the **same stable metric_id**; refuse invalid/missing fingerprint or if table 1/2 prefix identity fails. CLI should include:

```text
--input-dir
--output-dir
--dataset-id
--event-id
--figure mean|cov|both
--cohort-id
--detector-family
--objective-kind
--strict
```

Generate **two coequal primary figures** from the frozen runner outputs. Their scenarios are fixed before reading the results; do not select an experiment because its curves are visually convenient:

1. `Figure_1_mean` — predeclared primary synthetic scenario `C_residual_mean`, with a Gaussian control (KL exact only relative to the true generating covariance; sample-fit Ledoit–Wolf pseudo-information must be labeled `GAUSSIAN_PROXY`) and Student t7 as separately qualified robustness panel/output. For the mean Gaussian control the top information criterion is additive and `M(d,gamma)` is the Gaussian mean-mixture **fluid surrogate**; no assertion of perfect agreement between its ranking and empirical RMST until tested. The common detector is `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM`, no GLR substitution.
2. `Figure_1_cov` — predeclared synthetic rotation `B_cov_rotate30`, **30 degrees** between the first two fixed axes, tag exactly `COV_SURROGATE_EXPLORATORY` printed on the page and in metadata. Covariance changes create off-diagonal dependence in the frozen PCA basis. The joint Gaussian covariance KL `I_cov_joint(S)` drives the covariance-aware selector. Sum of one-dimensional covariance KL values must **never** be plotted as the joint information. If plotting `V_cov(S)=I_cov_joint(S)/M(|S|,gamma)`, mark the **entire** right axis `EXPLORATORY HEURISTIC: mean-mixture M is not a covariance detector cost`; otherwise omit V and plot a truthful joint-KL curve. The bottom panel compares measured covariance-aware detection with the historical **unilateral index-energy** baseline as a separate clearly named curve; do not call this an apples-to-apples test of two equally general detectors. Display empirical FPR and detector-family labels for each curve. The source panel may be Student-t7; in that case all Gaussian covariance KL values are proxies. It is valid and important to show that the historical baseline can be blind to a **decrease** of index variance, but this is not evidence of a universal information-theoretic PCA advantage. No prespecified performance shape is obligatory.

Do not blend mean and covariance panels into one curve. Both figures may be mentioned in the main report, with status labels and different inferential claims. Do not choose the scenario post hoc based on its prettiest looking curves. Real 2020 event blocked by embargo must not appear as confirmatory figure; 2022 is retrospective and requires qualified labeling.

### 3. Artifact format and presentation

Write:

- `results/pca_drift_benchmark/figures/Figure_1_mean.svg`, `.pdf` and `.png` (300 dpi), and `Figure_1_cov.svg`, `.pdf` and `.png`, all vector formats from the same plotted CSV data; metadata and hashes in `figure_manifest.json` with two separately keyed records;
- `Figure_1_mean_caption.md` and `Figure_1_cov_caption.md` each explaining the exact dataset, dates/horizon, N, k reservoir, change definition, mean/covariance proxy domain, detector family, threshold calibration, sample sizes, FPR and RMST uncertainty; separate tested outcomes from theory;
- `Figure_1_mean_source.csv` and `Figure_1_cov_source.csv`, each containing **only** plotted x/y/CI/null-FPR values and their upstream `metric_id`, and `FIGURE_CHECK.md` recording traceability, missing entries and visual inspection.

Use matplotlib or existing project style, accessible distinguishing colors **blue for CPV, red for prefix, green for selected**, different line dashes/markers even in grayscale. Upper panel contains a dual axis but colors, tick labels and titles must disambiguate CPV (percent) from V (information-per-cost). Lower panel labels the actual restricted delay and H=250. Chart must be publication readable in single-column and two-column contexts, with title/legend not overlapping data. Tick k=1,2,5,10,15,20 or a readable subset; candidate identifiers are 1-based. Never hardcode axis minimum/maximum to hide contrary values; lower y can be [0,250] but show observed bounds and uncertainty.

Missing k rows: leave gaps and annotate missing provenance, never fill by interpolation. Distinguish theoretically impossible/blocked from missing measurements in caption. Do not compute a 'best' curve by cherry-picking distinct detector families at each k; all points in a series must use the same detector and comparable null calibration protocol.

### 4. Reproducibility and quality assurance

- Compare each point in both `Figure_1_*_source.csv` to the corresponding aggregate/table row ID, not merely rounded values. Assert x=1..20 for eligible data or explicate missing rows.
- Both figures must display mandatory status `COV_SURROGATE_EXPLORATORY` only on covariance output; figure color/legend correctness; readable fonts; no clipping; SVG/PDF/PNG render same data; generated figures are deterministic up to documented metadata and font version. Use fonts already available in the environment; do not download or package proprietary fonts.
- Assert no label claims `k90=14`, `peak at 2`, `RMST≈12`, `250 days at k20`, etc., unless values actually establish that claim and a code-generated conditional checks it.
- Cross-check figure's reported FPR from holdout null with corresponding table FPR. If FPR comparability criterion fails, visually flag `FPR mismatch` and downgrade causal language.
- For both figures, assert captions, `figure_manifest.json`, data fingerprints and provenance flags; no empty fabricated figures if covariance metrics are missing. Automated smoke run with controlled tiny fixture generated by the **test suite**, not crafted to imitate desired real results. Visual QC: inspect exported PNG and PDF/SVG where tooling permits; log actual output checks rather than claim inspection without executing it.
- Preserve the historical CRLF/SHA guard and avoid modifications outside assigned files. Follow the approved bi-phase headless protocol, prompt sync and project wrapup before integration by Codex.
