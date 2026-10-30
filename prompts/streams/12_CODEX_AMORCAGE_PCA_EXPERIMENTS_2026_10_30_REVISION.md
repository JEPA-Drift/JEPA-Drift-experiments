# CODEX — MISSION 12 — PCA baseline vs drift-information selection

**Date:** 2026-10-30. **Owner:** Codex, architectural supervisor / Git integrator only. **Scientific scope:** JEPA-Drift, mean and covariance changes in daily cross-sectional stock returns. **Working tree:** `~/JEPA-Drift-experiments`. **Source of authority:** `11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md`, `prompts/Protocole Codex.md` (or locate the exact current version), `AGENTS.md`, `docs/DEVIATIONS.md`, `DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md` and the current code/contracts. **This file specifies future actions; it does not attest that they have run.**

## 0. NON-NEGOTIABLE DECISION

Temporarily suspend JEPA heavy pretraining (16), N-scaling (19), freeze-runner (21), confirmatory J4 (22). Keep stream 23 dormant. Do **not** rerun merged streams 12, 13, 14, 17, 18. No changes to the historical failure recorded in `docs/DEVIATIONS.md`: E3 / D8 `iid/first_order_d1_l3` = **FAIL +5.2833%**, contractual tolerance 5%; preserve this status verbatim. Do not overwrite any existing results.

**Repository invariants:** preserve the exact byte stream (including CRLF) and SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` of `results/e2/e2_cells.csv` both on disk and in the Git index. Keep anonymized Git identity. Never track proprietary EUROFIDAI data; respect existing ignore/size/push rules. Avoid changes to production monitors or data loaders unless an audited adapter is strictly necessary.

## 1. SCIENTIFIC ARBITRATION — MUST BE IN PLAN AND OUTPUTS

1. **Information of a Gaussian mean shift** in a *fixed* PCA basis: `q_k = (v_k^T Δ)^2 / (2 λ_k)` and `I(S)=Σ_{k∈S}q_k`, if the covariance used in the information formula is diagonal in that basis. With real Student-t backgrounds, call this **Gaussian pseudo-information / surrogate**, not measured true KL. PCA variance order does not in general order `q_k` in either direction.
2. **Covariance rotation is not additive**: univariate `q_k^cov = (r_k-1-log r_k)/2`, `r_k=(v_k^T Σ1 v_k)/λ_k`, measures **marginal Gaussian KL** only. A rotation creates cross-coordinate covariance. The true Gaussian joint KL on selected coordinates is `I_cov(S)=0.5[tr(Σ0,S^{-1}Σ1,S)-logdet(Σ0,S^{-1}Σ1,S)-|S|]`, and is **not** generally `Σ q_k^cov`. On Student-t backgrounds even that is a **Gaussian covariance proxy**. Report joint, marginal and off-diagonal diagnostics separately. The mean-shift mixture cost must not be asserted as an exact covariance-change delay penalty.
3. **Mixture complexity** `M(d,γ)=x_d/logγ`, where `x_d=logγ + (d/2)log(1+2x_d/d)` describes the **fluid matching of expected Gaussian-mixture log evidence to a threshold**, with an alternative-matched prior. It is not exact ADD, RMST, or an exact finite-ARL CUSUM penalty. Use `V=I/M` strictly as **model-based selection surrogate**. A separate empirical test establishes any speed gain.
4. **No oracle leakage:** A and C synthetic mean-shift oracles can use injected Δ for a *diagnostic upper bound*. B covariance oracle uses true Σ1 solely as retrospective upper-bound; label it. Real 2020/2022 mean shifts estimated from event windows are **retrospective oracles**, never ex-ante methods. Ex-ante historical library must be confined to data available by end-2019, with its stress examples from 2008/2011, and with no feature/return information from test events.
5. **Time embargo conflict:** baseline monitor begins **after** the 65-session embargo following 2020-01-01. The requested event **2020-02-24 to 2020-03-23** is inside the embargo, not valid as a confirmatory test in that split. Mark this event `NOT_EVALUABLE_STANDARD_SPLIT`; **mandatory named secondary retrospective cohort** `cohort_retrospective_covid`: calibration ends 2019-12-31, monitoring starts 2020-01-02 with no embargo, acute event 2020-02-24..2020-03-23; status `REAL_RETROSPECTIVE_EXPLORATORY`, documented deviation and never main confirmatory. Standard `cohort_standard_embargo` continues to report `NOT_EVALUABLE_STANDARD_SPLIT`. Preserve pre-onset alarms and separately report acute-window detection and post-onset RMST250; no future-information selection.
6. **Do not predetermine findings:** no hardcoded `CPV_14=90.2%`, `d*=2`, `RMST=12`, `RMST>180`, `FPR=4.9/5.0/5.1%` or figure shapes. Report what runs produce, even if opposite to the hypothesis. If CPV90 is outside first 20 axes, label as `OUTSIDE_TOP20` and provide its true full-spectrum cutoff in an auxiliary field, not a fabricated in-range baseline. Kaiser criterion `λ>=1` is meaningful on correlation eigenvalues, **not** on raw covariance eigenvalues; report in its proper space.
7. **Combinatorics:** additive `q_k` plus a cost depending only on cardinality makes best size-`d` subset = top-`d` values (`q`-sort), with deterministic ties. Evaluate **all** d from 1..k (not early stop at first local decrease unless a unimodality proof applies); forward greedy here means sequentially adding the remaining largest fixed `q`. Ex-ante `qbar` greedy differs from true-oracle `q` ranking. This equivalence does **not** justify additive covariance selection or equality of realized RMST.
8. **Truthful status:** repository status at `d8e644b`, listed commits and archived outputs come from the mission document; verify actual Git state before depending on these assertions. A missing path, dataset, tag or necessary config is a **blocker**, not an invitation to invent fixtures and label them as real results.

## 2. WORKSTREAMS AND DEPENDENCIES

Create four Claude Code headless streams in **isolated Git worktrees**, with the exact corresponding prompt files copied or made available to each stream. New prompt identifiers must be unique and start with `## PROMPT <id> —`. **Important:** the current `tools/check_prompts.py` only globs `prompt-*.md`; stream 31, under Codex's explicit approval, must extend discovery to the canonical `28_STREAM_PCA_DRIFT_*.md` through `31_STREAM_PCA_DRIFT_*.md`, assert all four IDs are found, and prevent a vacuous `make prompts-check` success.

| Stream / prompt | Owned executable | Upstream dependency | Scientific gate |
|---|---|---|---|
| PCA-RUNNER `28_STREAM_PCA_DRIFT_RUNNER.md` | `experiments/pca_drift_benchmark.py` + deterministic raw artifacts | None | Calibrated and independent evaluation; no future information |
| PCA-TABLES `29_STREAM_PCA_DRIFT_TABLES.md` | `experiments/pca_drift_tables.py` + 3 CSV and Markdown tables | Runner schema frozen | Factual values, explicit `NA` and status, no fabricated cutoffs |
| PCA-FIGURE `30_STREAM_PCA_DRIFT_FIGURES.md` | `experiments/figures/plot_figure_1.py` + SVG/PDF/PNG | Runner data schema + tables | Real curves from CSV, never hand-shaped |
| PCA-CONTRACTS `31_STREAM_PCA_DRIFT_CONTRACTS.md` | `tests/test_pca_drift_contracts.py` | Frozen runner schema; may plan concurrently | Exact cross-table reuse + scientific negative tests |

**Ordering:** (i) plan/audit all contracts; (ii) implement runner; (iii) freeze immutable raw schema + evaluation fingerprint; (iv) parallelize tables / figure / contract tests after their plans are approved; (v) integrate with tests; (vi) run main experiment and render deliverables. A stream cannot reinterpret an upstream schema without an explicit revision agreed by Codex. Calibrated detectors, error handling and reproducibility are owned by the runner; downstream streams read but must not recalculate experiments.

## 3. HEADLESS CLAUDE CODE PROTOCOL — DO NOT BYPASS

1. Inventory repository and available executables: `git status --porcelain=v1`, `git rev-parse HEAD`, `git branch -a`, `git worktree list`, `AGENTS.md`, actual `prompts/` structure, `.venv`, `make check`, `.mcp.json`, read/write permissions. Identify exact attached data manifests and code API. **Do not assume** a process is dormant merely because the mission says so.
2. Create one branch/worktree per stream (unique names and paths), without modifying main during planning. Create `prompts/plans/plan-[XX].md` before implementation if the repository's plan-recording rule applies.
3. **Phase A / read-only plan**, run in that stream's worktree (models/flags per `Protocole Codex.md`; verify CLI compatibility instead of silently changing flags):

   ```bash
   cd "$WORKTREE_PATH"
   claude -p "MODE PLAN. Read the assigned prompt and code. Produce a mathematically checked, leakage-free, API-accurate implementation/test plan. Do not modify application files." \
     --model opus --effort max --permission-mode plan > PLAN.md 2> plan_error.log
   ```

   Codex audits `PLAN.md`: mean vs covariance distinction, actual detector, null calibration, embargo, source files, time split, preserved SHA, GPU/CPU resources, deterministic outputs and tests. **NO-GO** plans are returned to phase A with itemized objections; do not launch implementation.
4. **Phase B / isolated headless implementation** only after explicit GO. Generate `run_stream.sh` by the local protocol, using `claude -c -p ... --model opus --effort max --dangerously-skip-permissions`, stdout/stderr to `execution.log`, exit-code sentinels, PID, optional Codex notification; shell launches detached via `nohup`. Never run this unrestricted invocation outside an isolated, audited worktree. When there is no isolated safe environment, stop rather than run a dangerous command.
5. Poll **snapshots only**, no `sleep`, no waiting loops. Done: inspect commit/artifact/test report; Error: only tail 40 lines first. On merge check dead PID, resolved Git dir `index.lock`, plan + logs, lint and unit tests, scientific contracts and non-regression; then remove worktree sentinels, sync prompt master and follow repository's documented wrapped/approved commit-push policy. Codex is **supervisor and integrator**, not application-code author.

## 4. RUNNER CONTRACT TO FREEZE BEFORE IMPLEMENTATION

Agree an immutable **single source of truth** written only by the runner. Minimum files in `results/pca_drift_benchmark/` (exact output directory can be updated once during planning):
- `manifest.json`: two separately identified real cohorts, no-embargo retrospective deviation, event-window and pre-onset alarm policy; Git SHA, branch, source hashes, split dates and embargo, assets and selection hashes, definitions of each event, dimensions, calibration/test cohort IDs, numeric dtypes, BLAS/OMP threads, software versions, RNG hierarchy, fingerprints, commands, null definitions and provenance flags (`SYNTHETIC`, `REAL_RETROSPECTIVE`, `GAUSSIAN_THEORY`, etc.).
- `spectra.csv`: dataset / fold / `k` / eigenvalue from LW covariance / eigenvalue from sample correlation / CPV / MP and Kaiser applicability / basis fingerprint / panel coverage.
- `selection.csv`: dataset / scenario / method / reservoir k / selected axes (ordered JSON) / d / objective type / I (mean Gaussian proxy, covariance joint Gaussian proxy, marginal cov proxy or NA) / M-model cost / V proxy / selection provenance (true synthetic oracle vs ex-ante historical).
- `calibration.csv`: detector definition / parameters / selected S / calibration seed/cohort / threshold / achieved calibration null probability / target FPR / applicability and failure states.
- `trials.csv`: include `cohort_id`, `split_hash`, `event_window_id`, `pre_onset_alarm` and `detected_during_event` for retrospective paths; per replicate **shared by all** candidate methods, null/alternative flag, sample/fold/event, onset, simulation and scenario IDs, selector ID, detector ID, selected S, threshold fingerprint, first hit, censored time `min(T,250)`, detected indicator, provenance; full-size trials can be Parquet if documented.
- `aggregates.csv`: include both real cohorts with explicit missing/NA statuses; on synthetic independently replicated experiments include measured RMST250, empirical holdout-null FPR250, detection rate, censoring, n and uncertainty; **do not assign synthetic n=2000 or independent holdout-null FPR to single historical Covid trajectory**. `metric_id` / fingerprint must allow tables to **refer to the exact same aggregate, not recompute a different sample**.
- `issues.json` or `issues.csv`: every blocked/unsupported scenario, missing data, invalid calibration or split, without substituting illustrative numbers.

Use `H=250`, `nmax=20`, **2000 independent null calibration and 2000 independent null/alternative evaluation trials** where the data generator supports them; document differing sample requirements. In real historical episodes do not claim 2000 independent crisis histories; use honest retrospective windows and report the effective sample size / uncertainty limit.

**The detector must be specified and held constant within each comparison.** If no calibrated multivariate CUSUM matching the stated alternative exists, implement auditable alternatives in different `detector_family` cells: **mandatory exact Gaussian mean-mixture scan CUSUM**, `W_t=max_{tau<=t} log L_{tau:t}` using prefix-sum segment differences and fixed ex-ante `s2`, **no GLR fallback** (for mean), a quadratic covariance-shift CUSUM or GLR (for covariance), plus the historical energy benchmark; do not call all three one identical detector. True covariance-joint alternatives require a covariance-aware statistic; diagonal energy is a separate controlled baseline. Threshold per method/dimension must be selected on independent null calibration and evaluated on disjoint null trajectories. Never infer exact FPR from target 5%.

## 5. GO/NO-GO AND INTEGRATION CRITERIA

**Figure delivery:** two equal-rank outputs `Figure_1_mean.{pdf,svg,png}` (residual mean change C, fixed mix-scan-CUSUM) and `Figure_1_cov.{pdf,svg,png}` (30° covariance rotation B), the second explicitly flagged `COV_SURROGATE_EXPLORATORY`. No additive marginal covariance KL or preordained curve shapes.

**Scientific NO-GO:** (a) any covariance rotation treated as a sum of univariate marginal KL without a caveat; (b) any mean-mixture M described as exact expected CUSUM delay; (c) any future test-event-derived q used to select an ex-ante method; (d) COVID embargo silently bypassed; (e) CPV/Kaiser/MP cutoffs hard-coded; (f) pre-drawn figure; (g) identical metric labels masking different detectors/null regimes; (h) Python/NumPy float equality asserted for independently recomputed aggregates rather than shared artifact; (i) preexisting E3 FAIL altered.

**Delivery GO:** all unit and integration tests pass; manifest and checksums in place; every table value maps to raw immutable artifact and every plot to table/aggregate; exact prefix and top-q oracle reuse contracts confirmed; reproducible fresh offline invocation on available data; no contaminated real results. If missing inputs prevent full evaluation, ship truthful code/tests/schema and a clear `NOT_EXECUTED`/`BLOCKED` report—not invented empirical findings.

After all approved stream integrations, run from the repository's own environment:

```bash
python tools/check_prompts.py --sync-master
make prompts-check
make check
python -m pytest -q tests/test_pca_drift_contracts.py
sha256sum results/e2/e2_cells.csv
```

Also verify `git show :results/e2/e2_cells.csv` hashes identically. Record actual command output, not a claimed pass. Produce concise final handover including commits, remaining blocks, protocol deviations, data lineage and source files for each figure/table.
