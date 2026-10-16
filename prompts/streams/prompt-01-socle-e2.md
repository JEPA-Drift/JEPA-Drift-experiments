## PROMPT 1 — Socle du dépôt, intégration du lot 1 et exécution d'E2 (jalon J1)

### Contexte
JEPA-Drift (« Article C ») teste si une représentation de la coupe transversale des rendements d'actions concentre la divergence de Kullback–Leibler (KL) d'une dérive et accélère sa détection séquentielle à calibration exacte. Cette tâche installe le dépôt, intègre le module théorique et le script E2 déjà écrits (lot 1), puis exécute E2, la validation Monte Carlo qui conditionne le jalon J1 du dimanche 18 octobre 2026.

### Tâche
1. Racine `~/JEPA-Drift-experiments` (`git init` si nécessaire). Créer : `jepadrift/{monitors,representations,jepa,data_loader,stats}/` (avec `__init__.py`), `experiments/`, `tests/`, `paper/`, `configs/`, `tools/`, `docs/{sections,audits}/`, `data/{raw,derived}/`, `results/`, `figures/`, `logs/e2/`, `external/`, `incoming/`.
2. Écrire `AGENTS.md` à la racine avec exactement le contenu du bloc ci-dessous, puis créer le lien symbolique relatif `CLAUDE.md` -> `AGENTS.md` (Claude Code lit `CLAUDE.md`, Mistral Vibe lit `AGENTS.md` : même configuration pour les deux).
3. Environnement Python 3.12 dans `.venv` : `numpy==2.4.4 scipy==1.17.1 pandas pyarrow statsmodels matplotlib pytest pyflakes`. Écrire `requirements.txt` (dépendances directes, numpy et scipy épinglés) et `requirements.lock` (`pip freeze`).
4. Déplacer depuis `incoming/lot1/`, sans modifier aucun fichier :
   - `floors.py` → `jepadrift/floors.py` ;
   - `test_floors.py` → `tests/` ;
   - `e2_floor_validation.py` → `experiments/` ;
   - `sec3_theory.tex`, `appA_proofs.tex` et `articleC_biblio_addendum.bib` → `paper/`.

   Si un fichier manque, écrire la liste des absents dans `docs/audits/lot1_missing.md` et s'arrêter.
5. `Makefile`, qui exporte les variables de déterminisme :
   - `test` : `pytest -q` ;
   - `j1` : `python experiments/e2_floor_validation.py --reps 2000 --out results/e2`, avec journal dans `logs/e2/run.log` ;
   - `check` : `pyflakes jepadrift experiments tests` puis `pytest -q`.
6. `.gitignore` : `.venv/`, `data/raw/`, `data/derived/d4_eurofidai/`, `external/`, `incoming/`.
7. Lancer `make test`, puis `make j1`.
8. Écrire `results/e2/J1_report.md` :
   - versions de Python, numpy, scipy et modèle de CPU ;
   - durée d'exécution ;
   - SHA-256 de `e2_cells.csv` ;
   - nombre de cellules qui passent ;
   - écart maximal par bras ;
   - tableau des six cellules G1 à SR = 1 (mesuré, prédit, premier ordre) ;
   - verdict J1.
9. Fin de stream (voir AGENTS.md, règles d'ingénierie) : invoquer sa directive de wrapup et enregistrer le résumé dans `prompts/wrapups/wrapup-01.md`, puis `tools/reindex_graphify_jcodemunch.sh`, `make check`, commit explicite `lot1: floors, E2, section 3; J1 run`, `git push origin main`.

```markdown
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

## Repository layout
- `jepadrift/`: library — `floors.py` (analytic floors, Article C section 3) and the subpackages `monitors/` (numpy only), `representations/`, `jepa/`, `data_loader/`, `stats/`; `sim.py` and `injection.py` are added by later streams.
- `experiments/`: one script per experiment (E2, E1, E3, ...), argparse and `if __name__ == "__main__":`.
- `tests/`: unit and contract tests (pytest).
- `paper/`: Article C LaTeX sources (section 3, appendix A, bibliography addendum).
- `prompts/`: stream prompts and orchestration — `prompts/streams/` stores the prompts of the planned streams (one `prompt-NN-<slug>.md` per stream, plus `INDEX.md`: routing table and stream conventions); `prompts/wrapups/` stores the processing summaries of the streams (one `wrapup-[XX].md` per stream, [XX] = stream number, written by the wrap-up directive before each commit); the master collection `Prompts_Claude_Code_v5.md` and `Orchestration_Streams_v5.md` live at this level.
- `configs/`: experiment configurations (YAML); `FROZEN.json` after milestone J4.
- `tools/`: repository tooling — `reindex_graphify_jcodemunch.sh` (end-of-stream reindexation of jCodeMunch and Graphify), plus the `pre-commit`/`pre-push` hooks and the freeze/trace scripts added by later streams.
- `docs/`: `sections/` (section notes), `audits/` (lot audits), `DEVIATIONS.md` (deviations under `C-<topic>`), `MAPPING.md` (traceability of reported numbers).
- `data/`: `raw/` (raw data, gitignored) and `derived/` (public derived panels; `derived/d4_eurofidai/` gitignored).
- `results/`: one CSV per stream under `results/<stream>/`.
- `figures/`: PNG + PDF per stream, drawn from CSVs only.
- `logs/`: one run journal per stream under `logs/<stream>/`.
- `external/`: external checkouts and side venvs (gitignored).
- `incoming/`: drop zone for incoming lots (gitignored).
- `.venv/`: Python 3.12 virtual environment (gitignored); `graphify-out/`: knowledge-graph cache (gitignored).
- Root: `AGENTS.md` (canonical project memory; `CLAUDE.md` is a relative symlink to it), `Makefile`, `requirements.txt`, `requirements.lock`, `.gitignore`, `conftest.py`.

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
- Before every commit, the implementing instance (Mistral Vibe or Claude Code) invokes its wrap-up
  directive and records the summary at `prompts/wrapups/wrapup-[XX].md` ([XX] = the number or
  reference of the stream being processed; the file is refreshed before each commit).
- End of stream (once a stream's processing is finished), in this exact order: (1) the wrap-up
  summary is generated and recorded at `prompts/wrapups/wrapup-[XX].md` (rule above); (2)
  `tools/reindex_graphify_jcodemunch.sh` reindexes jCodeMunch and Graphify; (3) `make check`, then
  a single commit — or several if the stream's work is heterogeneous and part of the deliverables
  risks errors; (4) `git push origin <current-branch>`. Push only while the repository address is
  not shared publicly and not linked to a publication (anonymous-submission companion: commits
  stay anonymized, no new author or institution identifiers), and only after checking that the
  pushed range contains no path under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/` and
  no file over 50 MB.
- Article B reference code: ~/The-Whitening-Advantage-Experiments (local checkout, read-only, used as-is at its current
  commit; never clone the remote github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments).
  Its code, not the text of its v87 manuscript, is the reference; read its docs/DEVIATIONS.md.
```

### Entrées
- `incoming/lot1/` : les six fichiers du lot 1, déposés par le chercheur.
- Référence d'exécution (Python 3.12.3, numpy 2.4.4, scipy 1.17.1) :
  - le SHA-256 de `e2_cells.csv` commence par `e315e537ead0f656` ; 46/46 cellules passent ;
  - G1, SR = 1, γ = 20 : onset 1519.152, cusum_t 1050.323, cusum_x 16.730 ;
  - G1, SR = 1, γ = 252 : onset 2815.446, cusum_t 2319.800, cusum_x 145.081 (ARL₀ mesuré 258.492) ;
  - écart maximal |ratio − 1| : G1 0.024, G2 0.047, S1 0.118 (contrôlé en temps d'information), S2 0.046.

### Livrables
`AGENTS.md` et `CLAUDE.md` (lien symbolique relatif vers `AGENTS.md`), `Makefile`, `requirements.txt`, `requirements.lock`, `.gitignore`, fichiers du lot 1 en place, `results/e2/{e2_cells.csv,e2_j1_summary.txt,J1_report.md}`, `logs/e2/run.log`.

### Contraintes techniques
Python 3.12, CPU, un seul thread BLAS. Pas de notebook. Les fichiers du lot 1 sont figés : toute anomalie est consignée, jamais corrigée en place.

### Critères de succès
- `make test` : 6 tests passent.
- `make j1` : code de sortie 0, « cells passing the J1 rule: 46/46 » et « J1: PASS ».
- Avec numpy 2.4.4 et scipy 1.17.1, le SHA-256 est identique.
- Avec d'autres versions : J1 PASS, chaque valeur de référence reproduite à ±2 %, et l'écart consigné dans `docs/DEVIATIONS.md` sous `C-E2-env`.
- Durée inférieure à 10 minutes sur un cœur.

### Commandes de vérification
```bash
cd ~/JEPA-Drift-experiments && source .venv/bin/activate
make test && make j1
sha256sum results/e2/e2_cells.csv | cut -c1-16
grep -E "46/46|J1: PASS" results/e2/e2_j1_summary.txt
```
