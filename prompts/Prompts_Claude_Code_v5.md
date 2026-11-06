[2026-10-16]

J'ai clos le stream en cours au stade de l'audit du code de l'Article B, sans écrire de nouveau code. Cet audit change la spécification du portage sur six points. Tous les streams non couverts deviennent 28 prompts Claude Code, rangés par urgence.

## 1. Streams en cours : état final

- **E2 / J1.** Terminé au lot 1, pré-exécution à 46/46. Il reste à l'exécuter de ton côté : c'est le prompt 1.
- **Lot 2 (bibliothèque de surveillance).** Je l'ai arrêté à la lecture du dépôt public de l'Article B (commit `998ffed`, lecture seule) et je clos ici cet audit. L'implémentation passe à Claude Code (prompts 4 à 8). Les six points ci-dessous corrigent le plan v4 et sont intégrés aux prompts.

| #   | Point                               | Plan v4 / texte v87              | Code de l'Article B                                                                                                                                                 | Intégration                                                                                                            |
| --- | ----------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 1   | Flux Concept (registre B : R00, D3) | erreur d'un Hoeffding Tree       | flux d'étiquettes 1{r>0} − q̂, soit un prédicteur constant                                                                                                           | P1-C et P2-C portés comme flux d'étiquettes ; variante classifieur optionnelle, avec attributs décalés d'un jour (R02) |
| 2   | Seuils de P1 (R01)                  | « niveau exact du treillis »     | Concept : CUSUM bilatéral strict, δ = 0,1, λ = 10, q̂ estimé sur 2018–2019. Data : δ = 0,5, λ = 65·Γ̂, Γ̂ en forme fermée depuis une QMLE GARCH ajustée une seule fois | portage identique, plus une version calibrée sur le treillis                                                           |
| 3   | Niveaux du treillis (R08)           | 4,29 % et 5,03 % (critère de J2) | loi exacte (H = 5 000, unilatéral, comparaison stricte) : 5,10 % à λ = 11,2 et 4,34 % à λ = 11,4                                                                    | la bibliothèque recalcule les niveaux ; le plan est à corriger                                                         |
| 4   | Datations (R16)                     | Pagan–Sossounov, 66 phases       | 66 phases = PS sur PFF, VNQ, BWX + Lunde–Timmermann sur SPY ; PS strict sur les quatre = 48 ; variante symétrique = 102                                             | trois fichiers repris tels quels ; le §1 de l'Article C doit nommer cette composition                                  |
| 5   | Pooling (R15)                       | bootstrap de fenêtres            | flux de fraction recentré par fenêtre (H_ref = 500), CUSUM bilatéral δ = 0, seuil par bootstrap (N_cal = 20 000), H_det = 750, FPR 5 %                              | portage, plus un e-détecteur exact : pari sur la fraction des signes, valide quelle que soit la corrélation            |
| 6   | MIX (R09)                           | e-processus MIX                  | 96 martingales de pari : 16 départs × η₀ ∈ {0,05 ; 0,10 ; 0,15} × 2 côtés, H = 5 000                                                                                | portage, plus e-détecteurs SR et CUSUM                                                                                 |

- **Lot 3** (§1 v0, Tableaux 1–3, T6–T7) : théorie et rédaction, sur la piste T. Je ne le convertis pas en prompts.

## 2. Écarts au gabarit `Prompt_Claude_Opus_v4.md`

- **Nombre de prompts.** Le gabarit en autorise au plus 7. Ton instruction demande de couvrir tous les streams, d'où 28 prompts.
- **Plancher de Sharpe.** Le gabarit le définit comme « ADD_min ≥ 504·ln(1/α₀)/SR² ». C'est faux à γ fini. Les prompts emploient le budget d'évidence (Lemme 1) et la fonction Φ (Prop. 2).
- **Flux de signe.** Le gabarit parle d'un flux d'erreurs de classifieur. Les détecteurs de l'Article B surveillent le flux d'étiquettes. Dans l'Article C, le flux de signe est le signe d'une projection impaire.
- **Contexte partagé.**
  - Le prompt 1 écrit `CLAUDE.md` à la racine du dépôt et crée le lien symbolique relatif `AGENTS.md` -> `CLAUDE.md`.
  - Chaque session lancée dans ce répertoire ou un sous-répertoire charge cette mémoire : Claude Code via `CLAUDE.md`, Mistral Vibe via `AGENTS.md`.
  - Chaque prompt garde quand même les définitions minimales dont il a besoin.
- **Format.** Les blocs extérieurs utilisent quatre accents graves, car les prompts contiennent des blocs à trois.

## 3. Ordre d'exécution

| #   | Stream                                             | Piste | Prio  | Échéance | Jalon   | Prérequis      |
| --- | -------------------------------------------------- | ----- | ----- | -------- | ------- | -------------- |
| 1   | Socle, lot 1, exécution d'E2                       | X     | A     | 18 oct.  | J1      | —              |
| 2   | D1 + D2 (dépôt B)                                  | X     | A     | 18 oct.  | J2      | 1              |
| 3   | D3 S&P 500                                         | X     | A     | 20 oct.  | J2, J3  | 1              |
| 4   | Surveillance : noyau, portage B                    | T→CC  | A     | 20 oct.  | J2      | 1, 2           |
| 5   | Injections F1–F4, fonds D5/D6                      | T→CC  | A     | 20 oct.  | J2      | 1, 2           |
| 6   | Représentations linéaires, interface Z             | T→CC  | A     | 21 oct.  | J2      | 2, 3           |
| 7   | Pipelines P2-C, P3-C/D, P3-CS, P7                  | T→CC  | A     | 21 oct.  | J2      | 4–6            |
| 8   | Tests de contrat, découplage                       | T→CC  | A     | 21 oct.  | fusions | 4–7            |
| 9   | BAF                                                | X     | B     | 25 oct.  | E9      | 1              |
| 10  | EUROFIDAI (D4)                                     | X     | B     | 25 oct.  | E4-EU   | 1              |
| 11  | Audit informationnel                               | T→CC  | A     | 23 oct.  | J2      | 2, 3, 6        |
| 12  | E1                                                 | T→CC  | A     | 23 oct.  | J2      | 4–8, 11        |
| 13  | E3                                                 | T→CC  | A     | 23 oct.  | J2      | 4–8            |
| 14  | CA-T-JEPA (code)                                   | T→CC  | A/B   | 25 oct.  | J3      | 3, 6, 8        |
| 15  | T-JEPA pour BAF (code)                             | T→CC  | B     | 25 oct.  | E9      | 9              |
| 16  | Pré-entraînement et RankMe                         | X     | A     | 1er nov. | J3      | 14             |
| 17  | IPCA                                               | T→CC  | A     | 28 oct.  | E4, E5  | 3, 6           |
| 18  | Adaptateur CD-DFM                                  | T→CC  | B     | 30 oct.  | E4, E5  | 3, 6           |
| 19  | E4 + P3-KF                                         | T→CC  | A/B   | 30 oct.  | J4      | 7, 11, 17      |
| 20  | Transmission T(u), dictionnaire                    | T→CC  | B/C   | 4 nov.   | J4      | 16, 17         |
| 21  | Gel de configuration, runner, figures, traçabilité | T→CC  | A     | 4 nov.   | J4, J6  | 12, 13         |
| 22  | E5                                                 | T→CC  | A/B/C | 6 nov.   | J4      | 16, 17, 19, 21 |
| 23  | E6                                                 | T→CC  | B     | 6 nov.   | J4      | 7, 16          |
| 24  | E9                                                 | T→CC  | B     | 6 nov.   | J5      | 9, 15          |
| 25  | E8                                                 | T→CC  | A/B   | 13 nov.  | J5      | 21             |
| 26  | E7                                                 | T→CC  | C     | 13 nov.  | J5      | 16             |
| 27  | E10                                                | T→CC  | C     | 13 nov.  | J5      | 7              |
| 28  | E11                                                | T→CC  | C     | 13 nov.  | J5      | 7, 14          |

T→CC : tâche de la piste T exécutée par Claude Code.

## 4. Prompts

````markdown
## PROMPT 1 — Socle du dépôt, intégration du lot 1 et exécution d'E2 (jalon J1)

### Contexte
JEPA-Drift (« Article C ») teste si une représentation de la coupe transversale des rendements d'actions concentre la divergence de Kullback–Leibler (KL) d'une dérive et accélère sa détection séquentielle à calibration exacte. Cette tâche installe le dépôt, intègre le module théorique et le script E2 déjà écrits (lot 1), puis exécute E2, la validation Monte Carlo qui conditionne le jalon J1 du dimanche 18 octobre 2026.

### Tâche
1. Racine `~/JEPA-Drift-experiments` (`git init` si nécessaire). Créer : `jepadrift/{monitors,representations,jepa,data_loader,stats}/` (avec `__init__.py`), `experiments/`, `tests/`, `paper/`, `configs/`, `tools/`, `docs/{sections,audits}/`, `data/{raw,derived}/`, `results/`, `figures/`, `logs/e2/`, `external/`, `incoming/`.
2. Écrire `CLAUDE.md` à la racine avec exactement le contenu du bloc ci-dessous, puis créer le lien symbolique relatif `AGENTS.md` -> `CLAUDE.md` (Claude Code lit `CLAUDE.md`, Mistral Vibe lit `AGENTS.md` : même configuration pour les deux).
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
9. Fin de stream (voir `CLAUDE.md`, règles d'ingénierie) : invoquer sa directive de wrapup et enregistrer le résumé dans `prompts/wrapups/wrapup-01.md`, puis `tools/reindex_graphify_jcodemunch.sh`, `make check`, commit explicite `lot1: floors, E2, section 3; J1 run`, `git push origin main`.

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
- `prompts/`: stream prompts and orchestration — `prompts/streams/` stores the prompts of the planned streams (one `prompt-NN-<slug>.md` per stream, plus `INDEX.md`: routing table and stream conventions); `prompts/plans/` stores the implementation plans of the streams (one `plan-[XX].md` per stream, [XX] = stream number, recorded before the plan's execution); `prompts/wrapups/` stores the processing summaries of the streams (one `wrapup-[XX].md` per stream, [XX] = stream number, written by the wrap-up directive before each commit); the master collection `Prompts_Claude_Code_v5.md` and `Orchestration_Streams_v5.md` live at this level.
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
- Root: `CLAUDE.md` (canonical project memory; `AGENTS.md` is a relative symlink to it), `Makefile`, `requirements.txt`, `requirements.lock`, `.gitignore`, `conftest.py`.

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
- When an implementation plan is created for a stream [XX] (explicitly requested by the user in text, or directly via the `/plan` directive), it must be recorded at `prompts/plans/plan-[XX].md` BEFORE its execution.
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
`CLAUDE.md` et `AGENTS.md` (lien symbolique relatif vers `CLAUDE.md`), `Makefile`, `requirements.txt`, `requirements.lock`, `.gitignore`, fichiers du lot 1 en place, `results/e2/{e2_cells.csv,e2_j1_summary.txt,J1_report.md}`, `logs/e2/run.log`.

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
````

````markdown
## PROMPT 2 — Jeux D1 (ETF-4) et D2 (US-97) depuis le dépôt de l'Article B

### Contexte
JEPA-Drift compare des moniteurs séquentiels univariés, poolés et latents sur des rendements quotidiens. D1 (quatre ETF) et D2 (97 actions américaines survivantes) viennent du dépôt public de l'article précédent (« Article B »), avec trois datations des phases haussières et baissières. Ils alimentent E1, E3, l'audit et E8 ; bloquant pour J2 (25 octobre). Lire `CLAUDE.md`.

### Tâche
1. **Ne pas cloner le dépôt distant.** Le dépôt de l'Article B est déjà présent localement : `~/The-Whitening-Advantage-Experiments` (lecture seule, tel quel, à son commit courant ; ne pas modifier ce dépôt, ne pas changer son commit, ne pas cloner `github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments`). « Le dépôt B » désigne désormais `~/The-Whitening-Advantage-Experiments`.
2. Lire le §6 du `~/The-Whitening-Advantage-Experiments/README.md` et `~/The-Whitening-Advantage-Experiments/docs/DEVIATIONS.md`. Écrire un résumé de 20 lignes au plus dans `docs/sections/articleB_deviations_digest.md`, couvrant R00, R01, R08, R15 et R16, avec leurs identifiants.
3. **D1.** Lire `~/The-Whitening-Advantage-Experiments/data/derived_firstrate/R01_daily_{SPY,PFF,VNQ,BWX}.csv` (colonnes `Date,Close,log_ret`).
   - Écrire `data/derived/d1_etf4/panel.parquet` au format long : `date, asset_id, ret (float64 = log_ret), close, in_universe`.
   - Écrire aussi `ret_wide.npy` (NaN hors période), `dates.npy` et `assets.json`.
   - Effectifs attendus : SPY 6414 lignes du 2000-01-04 au 2025-07-07 ; PFF 4403 lignes dès 2007-12-27 ; VNQ 5014 dès 2005-01-04 ; BWX 4451 dès 2007-10-09 ; aucun NaN.
4. **Datations de D1.** Copier `~/The-Whitening-Advantage-Experiments/results/R16_regime_census/data/R16_regime_census.csv`, `..._strict_ps.csv` et `..._symmetric.csv` vers `data/derived/d1_etf4/phases_{lt_spy,strict_ps,symmetric}.csv`, avec une colonne `dating_variant` ajoutée.
   - `lt_spy` (66 phases) = Pagan–Sossounov sur PFF, VNQ et BWX, Lunde–Timmermann sur SPY.
   - `strict_ps` (48 phases) = Pagan–Sossounov sur les quatre ETF.
   - `symmetric` (102 phases) = variante symétrique.
5. **D2.** Lire `~/The-Whitening-Advantage-Experiments/data/derived_equities/R15_panel_logreturns.csv` : 5154 jours × 97 titres, du 2005-01-04 au 2025-06-30, sans NaN, environ 0,66 % de rendements nuls. Produire les mêmes formats dans `data/derived/d2_us97/`, avec `in_universe` toujours vrai.
6. **Découpages.** Écrire `splits.yaml` pour chaque jeu, avec les dates réelles de premier et dernier jour de bourse de chaque segment :
   - pretrain [2005-01-01, 2016-01-01) (D1 : depuis le début de chaque série) ;
   - calib [2016-01-01, 2020-01-01) ;
   - monitor [2020-01-01, fin] ;
   - embargo de 65 jours de bourse après chaque frontière.
7. **Chargeur** `jepadrift/data_loader/articleB.py` : `load_d1()`, `load_d2()`, `load_phases(variant)`, `load_splits(dataset)`. Ils renvoient des tableaux numpy float64, les dates et les identifiants, sans autre transformation. Ajouter un point d'entrée `--build` qui produit tous les fichiers ci-dessus.
8. **Profil descriptif** dans `results/data/d1_d2_profile.csv`, par jeu et par segment :
   - jours, actifs, part de rendements nuls ;
   - corrélation moyenne par paires des signes 1{r>0} sur D2 (proche de 0,26 attendu ; rapporté, non bloquant) ;
   - K_eff = 1/ρ̂ ;
   - part de variance de PC1 (η).
9. **Traçabilité.**
   - `data/derived/MANIFEST.json` : chemin source (`~/The-Whitening-Advantage-Experiments` + commit local), SHA-256 en entrée et en sortie, lignes, dates.
   - `docs/DEVIATIONS.md` : `C-D2-survivor` (97 titres survivants) ; `C-interface-f64` (ret stocké en float64 et non en f32, pour l'identité bit à bit avec l'Article B).

### Entrées
Dépôt de l'Article B local `~/The-Whitening-Advantage-Experiments` (lecture seule) ; `CLAUDE.md`.

### Livrables
`data/derived/{d1_etf4,d2_us97}/…`, `data/derived/MANIFEST.json`, `jepadrift/data_loader/articleB.py`, `tests/test_data_d1_d2.py`, `results/data/d1_d2_profile.csv`, `docs/sections/{articleB_deviations_digest,data_d1_d2}.md`.

### Contraintes techniques
- pandas et pyarrow ; aucune interpolation ni remplissage.
- Le dossier `external/` n'est jamais commité. Le dépôt `~/The-Whitening-Advantage-Experiments` est hors du projet : lecture seule, jamais commité ni modifié.
- Les fichiers dérivés de D1 et D2 sont publics et peuvent être commités.

### Critères de succès
- Effectifs et dates exacts.
- Aller-retour CSV → parquet → numpy identique bit à bit.
- 66, 48 et 102 phases.
- Tests au vert.
- Manifeste complet.

### Commandes de vérification
```bash
cd ~/JEPA-Drift-experiments && source .venv/bin/activate
python -m jepadrift.data_loader.articleB --build
pytest -q tests/test_data_d1_d2.py
python -c "from jepadrift.data_loader.articleB import load_d2; r,d,a=load_d2(); print(r.shape, d[0], d[-1])"
```
````

````markdown
## PROMPT 3 — Jeu D3 : S&P 500, secteurs GICS et caractéristiques tirées des rendements

### Contexte
D3 est la coupe transversale principale de JEPA-Drift : jusqu'à 500 actions, avec des caractéristiques datées qui conditionnent les représentations (IPCA, CD-DFM, JEPA). Elle est requise pour l'audit et E1 (J2, 25 octobre), puis pour le pré-entraînement (J3, 1er novembre). Lire `CLAUDE.md`.

### Tâche
1. **Univers.**
   - (a) Cloner `https://github.com/alexouadi/CD-DFM` et épingler son commit. Y chercher la liste des 239 titres du S&P 500 utilisés par Alouadi & Lehalle (arXiv:2607.24410).
   - (b) Si elle est absente, consigner `C-D3-no239` et prendre les 239 titres à l'historique le plus long, selon une règle déterministe documentée.
   - (c) Récupérer la table publique Wikipedia « List of S&P 500 companies » : ticker, secteur et sous-industrie GICS, date d'entrée. La sauvegarder avec sa date de récupération et son SHA-256.
2. **Cours.**
   - Source : `yfinance` (version installée, figée dans `requirements.lock`), clôture ajustée quotidienne depuis 2000-01-01.
   - Cache brut par ticker dans `data/raw/d3_yf/<ticker>.parquet`, avec SHA-256.
   - Reprise avec attente exponentielle en cas d'échec ; aucun re-téléchargement sans `--refresh`.
   - Correspondance des tickers (`BRK.B` → `BRK-B`, etc.).
3. **Rendements.**
   - Log-rendements, sans remplissage vers l'avant.
   - `in_universe[t,i]` vaut vrai si et seulement si les cours existent en t−1 et en t.
   - Rendements nuls conservés ; |r| > 0,5 signalé dans `flags.csv`, sans suppression.
4. **Caractéristiques connues à l'ouverture de t** (rendements jusqu'à t−1 seulement) :
   - `beta_252` : pente MCO sur le rendement équipondéré des titres présents, 252 jours, au moins 126 observations ;
   - `vol_63` : volatilité sur 63 jours ;
   - `mom_12_1` : somme des rendements sur [t−252, t−22] ;
   - `rev_21` : somme sur [t−21, t−1] ;
   - secteur GICS en one-hot (actuel, non point-in-time).

   Chaque caractéristique continue est transformée chaque jour en rang centré dans [−0,5 ; 0,5], ex aequo moyennés. Écrire `chars.parquet` (`date, asset_id, c_*`).
5. **Sous-ensembles.** `data/derived/d3_239/` et `data/derived/d3_500/`, aux formats de D2. Mêmes `splits.yaml` que D2.
6. **Chargeur** `jepadrift/data_loader/sp500.py` avec `--build`.
7. **Tests** `tests/test_data_d3.py` :
   - non-anticipation : perturber les rendements à partir d'une date s laisse les caractéristiques jusqu'à s identiques bit à bit ;
   - aucune caractéristique NaN quand `in_universe` est vrai, après la période d'amorçage ;
   - correspondance des secteurs complète ;
   - reconstruction depuis le cache identique (SHA-256).
8. **Rapport** dans `results/data/d3_profile.csv` : titres par jour, couverture annuelle, η sur 2022–2024 pour `d3_239`. CD-DFM rapporte R² = 0,36 pour son facteur de marché ; la valeur est rapportée, non contrôlée.
9. **Écarts** dans `docs/DEVIATIONS.md` : `C-D3-survivor` (constituants actuels) ; `C-D3-gics-static`.

### Entrées
Internet (yfinance, Wikipedia, GitHub) ; `CLAUDE.md` ; `splits.yaml` de D2 comme gabarit.

### Livrables
`data/derived/{d3_239,d3_500}/{panel.parquet,ret_wide.npy,dates.npy,assets.json,chars.parquet,splits.yaml}`, `data/raw/d3_yf/` (ignoré par git), `jepadrift/data_loader/sp500.py`, `tests/test_data_d3.py`, `results/data/d3_profile.csv`, entrées du manifeste.

### Contraintes techniques
- Aucune donnée postérieure à t−1 dans une caractéristique datée t.
- Échecs de téléchargement journalisés, jamais silencieux.
- Les fichiers bruts ne sont pas commités.

### Critères de succès
- Au moins 450 titres dans `d3_500` en 2020.
- Tests au vert.
- Reconstruction déterministe.
- Écarts consignés.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.sp500 --build
pytest -q tests/test_data_d3.py
python -c "import pandas as pd; c=pd.read_parquet('data/derived/d3_239/chars.parquet'); print(c.shape, c.date.min(), c.date.max())"
```
````

````markdown
## PROMPT 4 — Surveillance (1/3) : noyau univarié, treillis exact et e-détecteurs, portage de l'Article B

### Contexte
La bibliothèque de surveillance est le socle de tous les pipelines de JEPA-Drift. Elle doit d'abord reproduire exactement les moniteurs du code public de l'Article B, puis fournir les détecteurs exacts de l'Article C. Bloquant pour J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **CUSUM strict** : S_t = max(0, S_{t−1} + s_t − δ), alarme si S_t > λ.
- **Flux d'étiquettes** : 1{r_t > 0} − q̂.
- **Flux de signe exact** : 1{y_t > 0} − 1/2, i.i.d. Bernoulli(1/2) sous toute hypothèse nulle à symétrie centrale.
- **Treillis** : niveaux de fausse alarme discrets d'un CUSUM sur un flux à deux points.
- **e-détecteur** : statistique M ≥ 0 telle que l'alarme à M ≥ γ garantit ARL₀ ≥ γ.
- **Γ** : facteur d'inflation de variance de la statistique surveillée, Γ = 1 + 2Σ_k ρ(k).

### Tâche
1. **`jepadrift/monitors/cusum.py`.**
   - Porter sans modification `strict_cusum`, `get_multiple_alarms` et `get_cusum_trajectory` (`~/The-Whitening-Advantage-Experiments/experiments/R01_real_world_backtest/exp_R01_real_world_backtest.py`, l. 110–142).
   - Porter `bilateral_delay` et `cusum_max_bilateral` (`~/The-Whitening-Advantage-Experiments/experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py`, l. 343–360).
   - Ajouter des versions vectorisées (R × T) aux résultats identiques.
2. **`lattice.py`.** Loi exacte d'un CUSUM sur un flux à incréments entiers +a / −b, avec P(+) = q, par chaîne de Markov :
   - FPR à l'horizon H et ARL₀ ;
   - unilatéral, et bilatéral par chaîne jointe (S⁺, S⁻) ;
   - comparaisons stricte et large ;
   - fonctions `attainable_levels()` et `select_threshold(nominal, rule="at_or_below", comparison="strict")`.
3. **`streams.py`.**
   - `label_stream(r, q_hat)` (R01) ;
   - `exact_sign_stream(y, rng)` : y = 0 tranché par une pièce équitable, `rng` passé explicitement ;
   - `energy_stream(r, mu, sigma)` = (r² − μ̂)/σ̂ (R01).
4. **`jepadrift/stats/garch.py`** (scipy autorisé ici, hors `monitors`) : porter sans modification `_garch_nll`, `fit_garch_qmle` et `compute_gamma_exact` (R01, l. 72–108).
5. **`gamma.py`.**
   - Γ̂ spectral = 1 + 2Σ_{k≤L}(1 − k/(L+1))ρ̂(k), avec L = ⌊4(n/100)^{2/9}⌋.
   - Γ^op = λ_requis/λ_iid à ARL₀ ou FPR fixé, par bissection monotone sur des trajectoires nulles fournies.
6. **`eprocess.py`.**
   - (a) e-processus de pari sur bits équitables, avec mise prévisible |λ_t| < 1.
   - (b) Portage de MIX depuis `build_mixture_kernel` (R09) : 16 départs `np.linspace(0, H-1, 16, dtype=int)` × η₀ ∈ {0.05, 0.10, 0.15} × côtés ±1, poids 1/96, valeur 1 avant le départ, H = 5000.
   - (c) e-détecteurs SR (M_n = (1 + M_{n−1})·f_n) et CUSUM (M_n = max(1, M_{n−1})·f_n), moyennés sur la grille de mises {0.05, 0.10, 0.15, 0.20} × côtés.
   - (d) Moyenne de dictionnaire sur des directions, valide quelle que soit leur dépendance.
   - (e) Mélange sous-gaussien fermé de la Prop. 3, documenté comme « valide si les coordonnées sont indépendantes sous H₀ ».
7. **Configurations P1.**
   - Concept, Article B : CUSUM bilatéral strict, δ = 0.1, λ = 10. q̂ est estimé sur 2018-01-02…2019-12-31 (mode réel) ou sur les 250 jours qui précèdent l'onset (mode injection).
   - Concept, Article C : flux exact centré en 1/2, λ issu du treillis.
   - Data, Article B : δ = 0.5, λ = 65·Γ̂, avec Γ̂ ajusté une seule fois sur 2018–2019 (écart R01-gamma-hat-refit du registre B).
8. **Contrôles d'identité, bloquants** (chargeur du prompt 2) :
   - reproduire `~/The-Whitening-Advantage-Experiments/results/R01_real_world_backtest/data/R01_{garch_models,covid_alarms,covid_trajectories,placebo_control,injection_summary,magnitude_sweep}.csv`. Exemple pour SPY : α = 0.211551, β = 0.729081, Γ̂ = 14.998367977816738, q̂ = 0.55864811133200798, aucune alarme en 2020 ;
   - reproduire la colonne `exact_level` des lignes `exact_survival` de `~/The-Whitening-Advantage-Experiments/results/R08_adverse_lattice/data/R08_lattice_exact_law.csv` à 1e-12 en relatif (H = 5000, λ de 10 à 13 par pas de 0.2, q = 0.5). Exemples : 0.051020717214682557 à λ = 11.2, 0.043428228893176074 à λ = 11.4.
9. **Deux environnements.** Exécuter les contrôles R01 dans `.venv` (numpy 2.4.4) et dans un second venv `external/articleB-venv/` créé côté projet (`python -m venv external/articleB-venv && external/articleB-venv/bin/pip install -r ~/The-Whitening-Advantage-Experiments/requirements.txt` : numpy 1.26.4, scipy 1.16.2). Le dépôt `~/The-Whitening-Advantage-Experiments` reste en lecture seule (le venv est hors de ce dépôt ; `external/` est ignoré par git). SLSQP peut différer d'une version de scipy à l'autre : tout écart va dans `docs/DEVIATIONS.md` sous `C-R01-env`.
10. **Contrôles Monte Carlo.**
    - Flux de signe exact sur GARCH(0.08 ; 0.90)-t₇ (importer `Garch` depuis `experiments/e2_floor_validation.py`) : le FPR du CUSUM calibré sur le treillis tombe dans l'IC binomial à 99 % du niveau exact (20 000 trajectoires, H = 1000).
    - e-détecteurs sur pièces équitables : ARL₀ moyen supérieur à γ pour γ ∈ {20, 100} (2000 trajectoires).
11. **`docs/sections/monitors.md`** : API et constantes portées, avec fichier et lignes source.

### Entrées
`~/The-Whitening-Advantage-Experiments/` (lecture seule) ; `data/derived/d1_etf4/` (prompt 2) ; `CLAUDE.md`.

### Livrables
`jepadrift/monitors/{cusum,lattice,streams,gamma,eprocess}.py`, `jepadrift/stats/garch.py`, `tests/test_monitors.py`, `tests/test_identity_articleB.py`, `results/identity/articleB_R01_R08.csv` (comparaisons cellule par cellule), `docs/sections/monitors.md`.

### Contraintes techniques
- `jepadrift/monitors/` importe numpy seulement.
- Aucun générateur aléatoire interne aux détecteurs.
- Calculs vectorisés en float64.
- Constantes de l'Article B non modifiées.

### Critères de succès
- Contrôles R01 et R08 identiques, ou écarts documentés imputables à l'environnement.
- Contrôles Monte Carlo passés.
- `make check` au vert.

### Commandes de vérification
```bash
pytest -q tests/test_monitors.py tests/test_identity_articleB.py
python -c "from jepadrift.monitors.lattice import attainable_levels as f; print(f(H=5000, delta=0.1, sided=1, q=0.5)[:5])"
```
````

````markdown
## PROMPT 5 — Injections F1–F4 et fonds D5 (Monte Carlo) et D6 (symétrisés)

### Contexte
Les expériences de JEPA-Drift injectent des dérives contrôlées, avec une date de rupture τ* exacte, sur des fonds réels symétrisés ou simulés. Elles mesurent ainsi délais et fausses alarmes avec une vérité terrain exacte. Bloquant pour E1 et E3 (J2). Lire `CLAUDE.md`.

Définitions :
- **D6** : chaque journée entière de la coupe est multipliée par un même signe de Rademacher. La transformation conserve |x|, les corrélations et la volatilité, et efface les dérives de localisation et l'effet de levier.
- **F1** : primes factorielles B Δλ.
- **F2** : largeur pilotée par les caractéristiques, (C_t Δγ) orthogonalisée aux chargements.
- **F3** : translation du mode de marché.
- **F4** : dérive de second ordre.

### Tâche
1. **Refactorisation.** Déplacer `Garch` et `t_innov` de `experiments/e2_floor_validation.py` vers `jepadrift/sim.py` ; E2 les importe désormais. Le SHA-256 de `results/e2/e2_cells.csv` doit rester identique : relancer `make j1` avant et après.
2. **Générateurs D5** dans `jepadrift/sim.py` :
   - `gaussian_latent(T, D, rng)` ;
   - `garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None)`, à volatilité commune, avec option de structure à un facteur équicorrélé (ρ = 0.40) plus un terme idiosyncratique.
3. **D6** dans `jepadrift/injection.py` : `symmetrize(X, rng)` renvoie (X̃ = ε_t X_t, ε). Les signes ε sont conservés pour la traçabilité.
4. **`inject(X, family, tau_star, I_target, params, rng)`**, appliqué aux rendements seulement, à partir de τ*. Σ̂ (Ledoit–Wolf), B (K facteurs, ACP) et Ψ̂ (variances résiduelles) sont estimés sur la fenêtre de calibration.
   - **F1** : Δ = B Δλ, Δλ de direction aléatoire, normalisé pour que ½ΔᵀΣ̂⁻¹Δ = I_target.
   - **F2** : Δ_t = (C_t Δγ)_⊥, résidu GLS de C_tΔγ sur B (pondération Ψ̂⁻¹), même normalisation sur la moyenne de calibration.
   - **F3** : Δ = Δm·b₁, b₁ = chargements de PC1.
   - **F4, déformation** : X̃ = X + (√r − 1) V_S V_Sᵀ X sur un sous-espace S, r ∈ {1.25, 1.5, 2}.
   - **F4, rotation** : rotation de Givens d'angle θ ∈ {15°, 30°, 45°} entre deux directions factorielles.
5. **Conventions d'amplitude.**
   - (a) Information égale : I_target = SR²/504, SR ∈ {0.5, 1, 2, 4}.
   - (b) Amplitude par titre fixée, pour les lois d'échelle : κ = dispersion transversale orthogonale aux chargements / dérive de marché, κ ∈ {0.25, 0.5, 1}.
6. **Onset.** τ* ~ U[t₀ + H_ref, t_fin − H_det]. Écrire `tau_star.json` : graine, famille, amplitude, convention, empreinte de la direction.
7. **Tests** `tests/test_injection.py` :
   - |X̃| = |X| bit à bit, un seul signe par jour ;
   - |BᵀΨ̂⁻¹Δ|_∞ < 1e-10 pour F2 ;
   - ½ΔᵀΣ̂⁻¹Δ = I_target à 1e-10 ;
   - aucune modification avant τ* ;
   - déterminisme pour une graine donnée ;
   - SHA-256 d'E2 inchangé.

### Entrées
Lot 1 (E2) ; D2 et D3 (prompts 2 et 3) ; `CLAUDE.md`.

### Livrables
`jepadrift/sim.py`, `jepadrift/injection.py`, E2 refactorisé, `tests/test_injection.py`, `docs/sections/injection.md` (formules et paramètres ; il servira de base à l'Annexe B).

### Contraintes techniques
- numpy et scipy.
- Aucune injection dans un espace latent.
- Générateurs aléatoires passés explicitement.

### Critères de succès
Tests au vert ; hash d'E2 identique ; documentation complète des quatre familles.

### Commandes de vérification
```bash
make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16
pytest -q tests/test_injection.py
```
````

````markdown
## PROMPT 6 — Représentations linéaires et interface Z (ACP orthogonale, coupe de degré 0, rangs)

### Contexte
Dans JEPA-Drift, toute représentation (ACP, IPCA, CD-DFM, JEPA) se branche sur les moniteurs par une même interface : apprentissage sur la seule fenêtre de calibration, transformation jour par jour, état figé et haché. Les représentations linéaires servent de références et fixent ce contrat avant l'arrivée du JEPA. Bloquant pour J2. Lire `CLAUDE.md`.

### Tâche
1. **Classe de base** `jepadrift/representations/base.py`, `Representation` :
   - `fit(X_fit, C_fit, dates_fit)` ;
   - `transform_day(x_t, C_t) -> {"z_odd": (D,), "z_even": (D',)}` ;
   - `transform_panel(X, C)`, appliquée jour par jour sans aucune opération temporelle ;
   - `state_hash()`, SHA-256 des tableaux d'état ;
   - attribut `odd_head = True` ;
   - `sidecar()`, JSON : empreintes de l'état et des données, dates d'apprentissage, drapeaux impair/pair, statistiques de normalisation figées.
2. **`pca.py`, `PCAOrthogonal(K="mp"|int, mode="factor"|"full"|"tail10", shrinkage="ledoit_wolf"|None)`.**
   - Canal marché : z_mkt = v₁ᵀx/√λ₁.
   - Résiduel factoriel : PC2..PC(K+1), K au bord de Marčenko–Pastur λ₊ = σ²(1 + √(N/T))² sur la corrélation.
   - Résiduel complet : N−1 directions.
   - « tail10 » : composantes des derniers 10 % de variance, pour P3-KF.
   - Toutes les sorties sont blanchies ; la tête paire contient les carrés des coordonnées blanchies.
3. **`cross_section.py`.**
   - `DegreeZero` : z = Uᵀ P x / ‖P x‖, avec P = I − b bᵀ/‖b‖² (b = chargements de PC1 ou vecteur de 1) et U un ensemble de directions résiduelles figé.
   - `CenteredRanks` : r_i − (N+1)/2, divisé par N, ex aequo moyennés. Cette transformation est impaire.
4. **Extraction** `python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor` : écrit `data/derived/<dataset>/z_<state_hash>.npz` (`Z_odd` T×D, `Z_even` T×D', `dates`) et le JSON associé.
5. **Tests** `tests/test_representations.py` :
   - imparité ‖φ(−x) + φ(x)‖_∞ ≤ 1e-12 ;
   - invariance de degré 0, z(c·x) = z(x) pour c > 0 ;
   - perturber la fenêtre de surveillance laisse `state_hash` identique ;
   - D attendu, pas de NaN.

### Entrées
D2 et D3 (`splits.yaml`, `ret_wide.npy`, `chars.parquet`) ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/{base,pca,cross_section,extract}.py`, `tests/test_representations.py`, extractions de référence pour D2 et `d3_239`, `docs/sections/interface_Z.md` (contrat d'interface, versionné).

### Contraintes techniques
- numpy (et scipy pour Ledoit–Wolf si besoin).
- Aucune statistique calculée sur la fenêtre de surveillance.
- Aucun import de `jepadrift.monitors` ou de `jepadrift.injection`.

### Critères de succès
Tests au vert ; deux exécutions donnent des `.npz` identiques au SHA-256 près ; contrat documenté.

### Commandes de vérification
```bash
python -m jepadrift.representations.extract --dataset d2_us97 --rep pca --mode factor
pytest -q tests/test_representations.py
sha256sum data/derived/d2_us97/z_*.npz
```
````

````markdown
## PROMPT 7 — Surveillance (2/3) : pipelines transversaux P2-C, P3-C, P3-D, P3-CS, P7 et calibrations

### Contexte
JEPA-Drift compare un actif seul (P1), le pooling de signes (P2), la projection orthogonale au marché (P3), la coupe normalisée de degré 0 (P3-CS) et un oracle (P7). Chaque pipeline traverse la même pile de détection ; seule la représentation change. Bloquant pour E1 et E3 (J2). Lire `CLAUDE.md`.

Propriété clé : toute moyenne de bits exacts centrés en 1/2 est une différence de martingale bornée sous H₀. Un e-processus de pari sur cette moyenne est donc exactement valide, quelle que soit la corrélation entre actifs.

### Tâche
1. **Registre** `jepadrift/pipelines.py` : `PIPELINES[id] = (representation, stream_builder, detector, calibration)`. Exécution via `run_pipeline(spec, X|Z, splits, onset_info) -> alarms.csv`, avec les colonnes `run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold, reading`.
2. **P2-C, portage de R15.**
   - Recopier `composition_for`, `worker_null_window_real` et `worker_race_h1_real` de `~/The-Whitening-Advantage-Experiments/experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py`.
   - Flux de fraction f_t = moyenne des 1{z_k > 0} − 0.5, avec médiane et écart-type par fenêtre sur H_ref = 500.
   - CUSUM bilatéral δ = 0 ; seuil par bootstrap de N_cal = 20 000 fenêtres réelles, H_det = 750, FPR cible 5 %.
   - Lecture anytime-valid ajoutée : e-détecteur de pari sur la fraction des signes bruts (centrés en 0, sans recentrage par médiane).
   - Rapporter ρ̂_signe et K_eff.
3. **Contrôle d'identité.** Reproduire `rho_sign_meas` et `K_eff_meas` de `~/The-Whitening-Advantage-Experiments/results/R15_cross_sectional/data/R15_panel_diagnostics.csv` pour K ∈ {5, 10, 20} à 1e-12. La fonction de calcul est à reprendre dans le script R15. Valeurs attendues de ρ̂ : 0.25774155995343417, 0.25904514047705118 et 0.28810195766064206.
4. **P3-C.**
   - Flux de signe exact par direction : canal marché plus directions résiduelles (prompt 6).
   - Détecteur par défaut : moyenne de dictionnaire des e-détecteurs CUSUM par direction, poids égaux sur tous les canaux.
   - Option : mélange sous-gaussien sur les directions résiduelles, autorisé seulement si le test d'indépendance croisée sous H₀ passe (|ρ̂| < 3 erreurs-types sur toutes les paires).
5. **P3-D.**
   - q_t = (‖z_res‖² − D)/√(2D) ; CUSUM strict δ = 0.5.
   - Seuil par bootstrap de fenêtres nulles de calibration. L'inversion de signe n'a aucun effet sur une statistique paire.
   - Rapporter Γ_z^op = λ_requis/λ_iid.
6. **P3-CS.**
   - (a) Pivot s_t = uᵀPx_t/‖Px_t‖ : e-processus de pari, et CUSUM à design fixe calibré par randomisation d'inversion de signe (B = 2000).
   - (b) e-détecteur de signe à mise prévisible λ_t = min(0.5, c/σ̂_{t|t−1}). σ̂ est une moyenne exponentielle (demi-vie 20 jours) de ‖Px_{t−1}‖ ; c est fixé sur la fenêtre de calibration.
7. **P7, oracle.** w* = Σ̂⁻¹Δ (Δ connu par `tau_star.json`) ; CUSUM du rapport de vraisemblance gaussien. P7 est rapporté comme borne seulement.
8. **Calibrations** dans `jepadrift/monitors/calibration.py` :
   - randomisation d'inversion de signe, exacte sous symétrie conditionnelle et sans effet de levier ;
   - bootstrap de fenêtres (port de R15) ;
   - treillis exact (prompt 4).
9. **Tests** `tests/test_pipelines.py` :
   - FPR sous H₀ sur fonds D6 dans l'IC binomial à 99 % de la cible, pour P3-C, P3-CS (pari) et la lecture anytime-valid de P2-C ;
   - P2-C par bootstrap à 5 % ± IC ;
   - détection à 100 % d'une injection F2 forte (SR = 8).

### Entrées
Prompts 2 à 6 ; `~/The-Whitening-Advantage-Experiments/` (lecture seule) ; `CLAUDE.md`.

### Livrables
`jepadrift/pipelines.py`, `jepadrift/monitors/calibration.py`, `tests/test_pipelines.py`, `results/identity/articleB_R15.csv`, `docs/sections/pipelines.md`, qui donne pour chaque pipeline sa lecture (budget, anytime-valid, exacte, bootstrap).

### Contraintes techniques
- `monitors` reste en numpy seul.
- Les représentations entrent sous forme de tableaux Z ou X, jamais comme objets importés dans `monitors`.
- Tâches parallélisables, mais résultats identiques quel que soit le nombre de processus.

### Critères de succès
Identité R15 exacte ; tests au vert ; une ligne d'`alarms.csv` par réplication.

### Commandes de vérification
```bash
pytest -q tests/test_pipelines.py
python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500
```
````

````markdown
## PROMPT 8 — Surveillance (3/3) : tests de contrat, règles de découplage et garde-fous

### Contexte
JEPA-Drift sépare strictement représentation et surveillance : un encodeur qui anticipe, n'est pas impair, n'est pas déterministe ou s'ajuste sur la fenêtre de test fausse toutes les mesures. Quatre tests de contrat bloquent donc toute fusion de code. Ils doivent s'appliquer automatiquement à toute représentation enregistrée, y compris le futur JEPA. Lire `CLAUDE.md`.

### Tâche
1. **`tests/test_contracts.py`**, paramétré sur toutes les représentations du registre :
   - **(1) Non-anticipation** : perturber x_{t+1:T} laisse z_{1:t} identique bit à bit.
   - **(2) Imparité** : ‖φ(−x) + φ(x)‖_∞ ≤ 1e-6 sur la tête impaire.
   - **(3) Déterminisme** : deux exécutions dans des sous-processus neufs (`PYTHONHASHSEED=42`, un thread, CPU) donnent des SHA-256 identiques pour `z_*.npz` et `alarms.csv`.
   - **(4) Absence de statistiques de test** : `fit` ne reçoit que les segments `pretrain` ou `calib`. Perturber le segment `monitor` laisse `state_hash` inchangé, et les statistiques de normalisation du JSON proviennent du seul segment déclaré.
2. **`tests/test_decoupling.py`**, par analyse `ast` des imports :
   - `jepadrift/monitors/**` n'importe ni torch, ni `jepadrift.jepa`, ni `jepadrift.representations` ;
   - `jepadrift/jepa/**` n'importe ni `jepadrift.injection`, ni `jepadrift.monitors` ;
   - `jepadrift/injection.py` n'accepte que des panels de rendements : `assert` sur la forme et le dtype, refus explicite d'un objet `Z`.
3. **Pour les modèles torch** (s'appliquera au JEPA) :
   - en mode `eval`, aucun buffer ne change après 10 passes avant ;
   - aucune couche `BatchNorm*` en mode entraînement ;
   - aucune normalisation calculée sur l'axe temporel ;
   - cible EMA inactive à l'extraction.

   Si torch n'est pas installé, ces tests sont marqués comme sautés.
4. **Garde-fous git.** `tools/pre-commit` lance `make check` et refuse tout fichier sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` ainsi que tout fichier de plus de 50 Mo. Le hook `pre-push` bloque tout push dont la plage contient un de ces fichiers et rappelle que les push ne sont autorisés que tant que l'adresse du dépôt n'est ni partagée publiquement ni liée à une publication (soumission anonyme) — voir `CLAUDE.md`. Installer les hooks avec `make hooks`.
5. **Étendre `make check`** : pyflakes, tests unitaires, tests de contrat et de découplage.

### Entrées
Prompts 4 à 7 ; `CLAUDE.md`.

### Livrables
`tests/test_contracts.py`, `tests/test_decoupling.py`, `tools/pre-commit`, `tools/pre-push`, cibles `hooks` et `check` du `Makefile`, `docs/sections/contracts.md`.

### Contraintes techniques
- Tests rapides (moins de 2 minutes au total), sur données réduites et déterministes.
- Aucune dépendance réseau.

### Critères de succès
Les quatre contrats passent pour PCA, DegreeZero et CenteredRanks. Une représentation volontairement fautive (fixture : normalisation sur toute la série) échoue au contrat (4). Le hook bloque un fichier factice placé sous `data/raw/eurofidai/`.

### Commandes de vérification
```bash
make hooks && make check
mkdir -p data/raw/eurofidai && echo x > data/raw/eurofidai/t.csv && git add -f data/raw/eurofidai/t.csv; git commit -m test || echo "bloqué : attendu"
git reset -q HEAD data/raw/eurofidai/t.csv && rm -r data/raw/eurofidai
```
````

````markdown
## PROMPT 9 — Jeu BAF (Bank Account Fraud, variante Base) : téléchargement, contrôle et découpage

### Contexte
JEPA-Drift ajoute un domaine tabulaire hors finance : BAF (Jesus et al., NeurIPS 2022 Datasets and Benchmarks). Ce sont des demandes d'ouverture de compte synthétiques, générées à partir de données réelles, sur huit mois, avec une dérive native. Requis pour T-JEPA (prompt 15) et E9 ; non bloquant pour J1 et J2. Lire `CLAUDE.md`.

### Tâche
1. **Source.** Lire la fiche technique officielle du jeu (dépôt `feedzai/bank-account-fraud` sur GitHub et page Kaggle associée ; vérifier l'identifiant Kaggle, par exemple `sgpjesus/bank-account-fraud-dataset-neurips-2022`). Télécharger par l'API Kaggle, avec des identifiants lus dans `~/.kaggle/kaggle.json`, jamais commités, vers `data/raw/baf/`.
2. **Contrôles.**
   - Six variantes (Base, Variant I à V) de 1 000 000 lignes chacune.
   - 30 attributs, plus `fraud_bool` et `month`, avec `month` ∈ {0,…,7}.
   - Consigner le schéma (types, catégories), la licence de la fiche et la prévalence de fraude par mois.
3. **Conversion.** Base vers `data/derived/d7_baf/base.parquet`, avec l'ordre des lignes d'origine conservé et un index de ligne. Découpage `splits.yaml` : `fit` mois 0–2, `calib` mois 3, `monitor` mois 4–7.
4. **Prétraitement figé, appris sur les mois 0–2 seulement** : standardisation des numériques, encodage des catégories (inconnues → modalité réservée), traitement des sentinelles −1 documentées dans la fiche. Sauvegarder les paramètres dans `preproc.json`.
5. **Profil** dans `results/data/baf_profile.csv` : effectifs, taux de fraude et moyennes des attributs par mois.
6. **Écarts.** `C-BAF-synthetic` : rédiger « dérive native d'un jeu synthétique », jamais « in-the-wild ».

### Entrées
Compte Kaggle du chercheur ; `CLAUDE.md`.

### Livrables
`data/raw/baf/` (ignoré par git), `data/derived/d7_baf/{base.parquet,splits.yaml,preproc.json}`, `jepadrift/data_loader/baf.py` (`--build`), `tests/test_data_baf.py`, `results/data/baf_profile.csv`, `docs/sections/data_baf.md`.

### Contraintes techniques
- pandas et pyarrow.
- Aucun paramètre de prétraitement estimé hors des mois 0–2.
- Données brutes non commitées.

### Critères de succès
1 000 000 lignes, 32 colonnes, 8 mois ; tests au vert ; prétraitement reproductible au SHA-256 près.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.baf --build
pytest -q tests/test_data_baf.py
python -c "import pandas as pd; d=pd.read_parquet('data/derived/d7_baf/base.parquet'); print(d.shape, d.month.value_counts().sort_index().to_dict())"
```
````

````markdown
## PROMPT 10 — EUROFIDAI (D4) : spécification d'extraction, ingestion locale et garde-fous

### Contexte
D4 (actions européennes, constituants point-in-time, jusqu'à environ 1000 titres) sert au test d'échelle en N et au recensement européen de JEPA-Drift. Les données sont propriétaires : elles ne quittent jamais la machine du chercheur, et seuls les scripts et les manifestes d'empreintes sont versionnés. Claude Code n'a pas d'accès au portail EUROFIDAI : il prépare l'extraction que le chercheur exécute, puis l'ingestion. Lire `CLAUDE.md`.

### Tâche
1. Rédiger `docs/sections/eurofidai_extraction_spec.md`, à exécuter sur le portail :
   - marchés de la zone euro et du Royaume-Uni ;
   - période 2000-01-01 → dernière date disponible ;
   - fréquence quotidienne ;
   - champs : identifiant stable, ISIN, marché, date, cours ajusté ou facteurs d'ajustement, rendement total si disponible, capitalisation, statut de cotation et dates de radiation (titres radiés inclus), appartenance aux indices si disponible ;
   - format CSV, un fichier par marché et par année ;
   - dépôt dans `data/raw/eurofidai/`.
2. `jepadrift/data_loader/eurofidai.py` :
   - lecture des fichiers exportés, avec une table de correspondance des champs dans `configs/eurofidai_schema.yaml`, modifiable si les noms diffèrent ;
   - rendements log à partir des cours ajustés, sans remplissage ;
   - `in_universe` point-in-time ;
   - filtre de liquidité documenté (jours sans échange) ;
   - caractéristiques tirées des rendements, avec la même définition que D3 (réutiliser le code de `sp500.py`) ;
   - sortie `data/derived/d4_eurofidai/` aux formats de D3.
3. **Manifeste versionné** `docs/manifests/d4_manifest.json` : empreintes, effectifs, dates, sans aucune donnée.
4. **Tests sur données synthétiques** (`tests/fixtures/eurofidai_fake/`) : schéma, ajustements, radiations, non-anticipation des caractéristiques. Les tests réels sont sautés si `data/raw/eurofidai/` est vide.
5. **Vérifier** que `.gitignore` et le hook du prompt 8 bloquent `data/raw/eurofidai/` et `data/derived/d4_eurofidai/`.

### Entrées
Export manuel du chercheur (plus tard) ; `CLAUDE.md` ; code de D3.

### Livrables
Spécification d'extraction, chargeur, configuration de schéma, fixtures et tests, manifeste vide prêt à remplir.

### Contraintes techniques
- Aucune donnée EUROFIDAI dans git, dans les journaux ou dans les CSV de `results/` (seulement des agrégats).
- Aucune requête automatisée vers le portail.

### Critères de succès
Tests sur fixtures au vert ; hook vérifié ; spécification exécutable telle quelle par le chercheur.

### Commandes de vérification
```bash
pytest -q tests/test_data_eurofidai.py
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
```
````

````markdown
## PROMPT 11 — Audit informationnel des panels D2 et D3

### Contexte
Avant tout apprentissage, JEPA-Drift mesure combien d'information de dérive existe dans chaque sous-espace de la coupe : marché, facteurs, résiduel, directions de caractéristiques. Il mesure aussi si l'hypothèse de symétrie qui rend les flux de signe exacts tient. Ces chiffres nourrissent le §2 de l'article, les gains prévus d'E1 et la décision J2. Lire `CLAUDE.md`.

Définition : le Sharpe de dérive d'un sous-espace S vaut SR_S² = 252·Δμ_Sᵀ Σ_S⁻¹ Δμ_S, où Δμ est l'écart des moyennes entre deux phases adjacentes.

### Tâche
Écrire `experiments/audit_information.py`. Fenêtres autorisées avant J4 : 2005–2019 seulement.
1. **Spectre** de Σ̂ sur la calibration, avec et sans Ledoit–Wolf. Rapporter η = λ₁/tr Σ par année, le bord de Marčenko–Pastur et K.
2. **Signes.** Corrélation moyenne des signes ρ̂_signe, correspondance gaussienne ρ = sin(πρ̂_signe/2), K_eff = 1/ρ̂_signe.
3. **Symétrie centrale.** Pour chaque direction figée (PC1–PC20, directions de caractéristiques orthogonalisées) :
   - q̂_u = moyenne de 1{uᵀx_t > 0}, avec test binomial exact contre 1/2 ;
   - test des triplets de Randles et al. (1980) sur uᵀx_t/σ̂_{t|t−1} ;
   - correction de Holm.
4. **Spectre de Sharpe de dérive débiaisé.**
   - Transitions : frontières des phases des datations de SPY (`phases_*.csv`, prompt 2) comprises dans 2005–2019.
   - Pour chaque transition (n₁, n₂ jours) et chaque sous-espace S de dimension d_S :

     SR_S² = 252·[Δμ̂_Sᵀ Σ̂_S⁻¹ Δμ̂_S − d_S(1/n₁ + 1/n₂)]·(n − d_S − 1)/n.

   - IC par bootstrap par blocs mobiles (blocs de 20 jours, 2000 tirages) ; agrégation par médiane sur les transitions.
   - Sous-espaces : marché, factoriel (K), résiduel complet, caractéristiques ; d_S ≤ 30 pour limiter le biais de bruit.
5. **Plafonds des canaux.**
   - N1 = E[σ_t²]·E[σ_t⁻²], σ_t étant la dispersion transversale résiduelle.
   - N2 : rapport entre l'information conditionnelle (Σ_t Ledoit–Wolf glissant sur 60 jours, passé seulement) et l'information statique, pour des directions F1 et F2.
   - N3 : ν̂ d'une loi t multivariée ajustée sur les résidus blanchis, puis rapport J/Σ⁻¹ = (ν+1)ν/((ν+3)(ν−2)) par direction.
6. **Part du budget.** Pour chaque phase datée et chaque sous-espace, proportion des phases avec L·Î ≥ ln γ, pour γ ∈ {20, 252}. C'est la lecture budget, exacte par le Lemme 1.
7. **Gains prévus.** Évaluer `jepadrift/floors.py` avec ρ̂, κ̂ et le spectre estimés, et écrire `predicted_gains.csv` (entrée d'E1).

### Entrées
D1 (datations), D2, D3 ; représentations du prompt 6 ; `jepadrift/floors.py` ; `CLAUDE.md`.

### Livrables
`results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains}.csv`, `figures/audit/*.{png,pdf}`, `logs/audit/`.

### Contraintes techniques
- Aucune donnée postérieure au 2019-12-31.
- Bootstrap par blocs avec graines fixes.
- Figures produites depuis les CSV.

### Critères de succès
Toutes les sorties produites. Les estimations débiaisées sont rapportées même négatives (risque R9, signalé). Exécution déterministe au SHA-256 près.

### Commandes de vérification
```bash
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
ls results/audit && sha256sum results/audit/*.csv
```
````

````markdown
## PROMPT 12 — E1 : le problème (§2) sur fonds réels symétrisés, pipelines 1 → 2 → 3 et critères de J2

### Contexte
E1 mesure le coût de détection selon le pipeline, à cible nominale commune et, seulement lorsque les FPR atteints le permettent, à fausse alarme appariée :
- un actif seul (P1) ;
- le pooling des signes (P2) ;
- la projection orthogonale au marché (P3) ;
- la coupe de degré 0 (P3-CS, canal N1).

Les dérives sont injectées dans des fonds réels symétrisés (D6) de 2005–2019. Les gains mesurés sont comparés à des prévisions calculées à partir des dérives injectées. Ces prévisions emploient une information quadratique gaussienne de conception, pas la KL exacte des fonds D6. E1 fournit les chiffres du §2 et les critères de J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **Délai** : `delay = alarm_index − tau_star + 1` pour une alarme observée (`C-pipe-delay`). Les onsets uniformes avec censure à H donnent `ADD_H = mean(min(T,H))`, avec `min(T,H)=H` pour une trajectoire sans alarme, puis la moyenne et la médiane des alarmes détectées et le taux de censure ; ils n'estiment pas le pire cas de Lorden. Réserver le terme ADD de Lorden aux bornes analytiques.
- **Lectures à horizon H**, avec cible nominale α = 0,05 et FPR(H) observé rapporté par cellule :
  - anytime-valid : e-détecteur arrêté à γ_H = H/α (`pipelines.horizon_gamma`), car P∞(alarme avant H) ≤ H/γ ;
  - exacte : CUSUM de signe au niveau atteignable du treillis ≤ α à l'horizon H. La statistique se compare à `select_threshold(...)["threshold"]` (point milieu), jamais à `lam` ;
  - bootstrap (portage R15, H = 750) et randomisation (inversion de signe) : FPR(H) empirique visé ≈ α, sans garantie automatique.
- **G_ADD,H** = ADD_H,A/ADD_H,B, rapport de délais restreints à lecture et H égaux ; rapporter la censure et ne pas le présenter comme le rapport des ADD de Lorden.
- **G_floor** = I_B/I_A, rapport des informations quadratiques gaussiennes de conception calculées à partir des Δ injectés.
- **Alignement** a_max = max_k Δz_k²/‖Δz‖² : part de cette information quadratique portée par le meilleur canal, en coordonnées blanchies.

### Tâche
Écrire `experiments/e1_problem.py`. Seules les lignes du 2005-01-04 au 2019-12-31 sont lues, avec un contrôle bloquant. L'option `--include-test-window` est refusée tant que `configs/FROZEN.json` est absent ou ne correspond pas (prompt 21).

0. **Socle.**
   - Briques à utiliser : `pipelines.run_pipeline` et `pipelines.null_check` ; `injection.symmetrize`, `inject` et `draw_tau_star` (avec un cache de `fit_background` par jeu, fenêtre et K) ; `data_loader.chars` ; `stats.drift` ; `floors`.
   - États des représentations : ajustés une seule fois par jeu et par représentation, sur les lignes de calib du panel d'origine. Ces lignes sont sans dérive, et D6 laisse les moments d'ordre 2 inchangés. Ces états sont passés à `run_pipeline` ; jamais `state=None` avec des enregistrements injectés.
   - À H = 2 000, tout onset qui tient avant fin 2019 précède la calib 2016–2019 : l'état est ajusté sur des dates ultérieures à l'onset. Cette lecture est rétrospective, sans interprétation prospective, même si les nouveaux tirages de signes D6 permettent un contrôle conditionnel du nul.
1. **Fonds et onsets.**
   - Une symétrisation D6 neuve par réplication.
   - τ* uniforme, tel que [τ*, τ* + H) tienne dans la fenêtre.
   - Jeux : `d2_us97` et `d3_239`.
   - F2 sur `d3_239` seulement (D2 n'a pas de caractéristiques), via `load_chars_tensor` ; NaN remplacés par 0 et comptés.
   - Rapporter l'information réalisée après τ* à partir de `delta`, puisque F2 suit C_t.
2. **Bras A — gains à information égale.**
   - Convention (a) : SR ∈ {2, 4, 8}. SR = 1 est exclu : il est censuré pour tous les pipelines, avec τ_γ ≈ 5 340 jours à γ_H = 40 000.
   - Familles F3, F1 et F2 ; 1 000 onsets par cellule ; H = 2 000 ; γ_H = 40 000.
   - Pipelines :
     - P1-C : flux de signe exact de chaque titre d'un échantillon de 20 titres tirés avec graine ; on rapporte la médiane et le meilleur titre, ce dernier étant un oracle post hoc choisi sur les mêmes réplications ;
     - P2-C : lecture anytime-valid avec K = N. La lecture Article B (bootstrap R15 recalibré sur une symétrisation, H = 750, `C-P2C-port`) figure en cellules secondaires ;
     - P3-C : dictionnaire d'e-détecteurs CUSUM sur le canal marché et le résiduel factoriel (résiduel complet pour F2). En diagnostic seulement : la lecture exacte du meilleur canal, oracle post hoc, et la lecture « mélange » (option `mixture_s2`), étiquetée « validité approchée ». Implémenter pour cette dernière la porte d'indépendance avec correction de Holm au niveau de famille de 1 % sur les p-valeurs des paires ; un non-rejet ne démontre pas l'indépendance ;
     - P3-CS : (b) mise prévisible ∝ 1/σ̂ en principal ; (a) e-processus pivot en secondaire ;
     - P7 : rapporté comme borne.
   - P3-D (capteur Data) est traité à part : H = 750, fenêtres nulles de calib (`C-P3D-windows`). Il est rapporté comme preuve d'orthogonalité, jamais dans les tableaux de gains de localisation.
3. **Bras B — lois d'échelle (J2).**
   - Convention (b) :
     - F3 avec un SR RMS par titre ∈ {2, 4}, sur `d2_us97` et `d3_239` ;
     - F2 avec κ ∈ {1, 2}, sur `d3_239`.
   - La grille d'amplitude est choisie sur les fonds 2005–2019 de sorte que le délai médian de P3-C reste dans [20 ; 0,8·H] sur toute la grille de N. Ce choix est un degré de liberté : le consigner.
   - N ∈ {8, 16, 32, 64, 97} pour D2 et {8, 16, 32, 64, 128, 239} pour D3. Par N : 20 sous-ensembles emboîtés tirés avec graine, communs à tous les pipelines, et 200 onsets par (sous-ensemble, cellule).
   - Pipelines : P2-C sur F3 ; P3-C (résiduel complet) et P3-CS (b) sur F2.
   - Pente :
     - figer avant les injections, par graine, un titre de référence P1 inclus dans tous les sous-ensembles emboîtés ; la pente de log G_ADD,H en log N n'est l'opposé de celle de log ADD_H de P3 que si cette référence reste effectivement constante en N ; sinon, estimer directement la pente du rapport ;
     - la médiane n'est définie que si le taux de détection dépasse 50 % ; sinon, la cellule est exclue et signalée ;
     - IC par bootstrap sur les sous-ensembles ;
     - a_max(N) est rapporté pour attribuer une pente faible à l'information ou à l'alignement.
4. **Bras C — phases réelles (descriptif).** Phases des trois datations comprises dans 2005–2019.
   - Part des phases dans le budget, par sous-espace : L·Î ≥ ln γ, γ ∈ {20, 252}, en lecture budget, avec `stats.drift.debiased_sr2`.
   - Parts placebo par `rotate_phases` (2 000 rotations). Les deux parts sont rapportées. L'Î intra-phase est gonflé par la sélection des frontières (`C-audit-placebo`) : les parts sont présentées comme des bornes supérieures. Le placebo teste l'alignement avec les datations choisies ; il n'identifie pas une fraction causale de la dérive.
   - Alarmes dans les phases sur données brutes :
     - P1-C, en flux d'étiquettes Article B avec q̂ de calib ;
     - P3-C, avec recentrage sur q̂ de calib pour les canaux dont la symétrie est rejetée (`CLAUDE.md`).

     Ce bras est descriptif : aucune exactitude n'est revendiquée.
   - `results/audit/predicted_gains.csv` est cité tel quel (NaN conservés), jamais complété.
5. **Prévisions, à partir des Δ injectés.**
   - Information quadratique gaussienne de conception de l'oracle : I_x = ½ΔᵀΣ̂⁻¹Δ. Ne pas l'appeler KL exacte des fonds D6.
   - Pour chaque pipeline : information de son sous-espace, avec Δz = WᵀΔ dans la base figée.
   - Délai prévu du dictionnaire : environ (ln γ_H + ln K_canaux)/(e·a_max·I_z). Ici e = 4f̂(0)² est l'efficacité du signe estimée sur la calib (2/π sous normalité).
   - Budget d'évidence de P7 : ln γ_H/I_x (Lemme 1), distinct d'un ADD prédit à seuil fini.
   - Rapporter les gains prévus et mesurés côte à côte seulement pour des estimands compatibles : prédiction restreinte à H ou cellules à censure négligeable ; sinon étiqueter la comparaison comme non directement interprétable. Pour P3-CS (b), rapporter la borne N1 = E[σ²]E[σ⁻²] de l'audit (≈ 1,97).
6. **Mesures.**
   - ADD_H, moyenne et médiane des alarmes détectées, taux de détection dans H et censure, sans les confondre.
   - G_ADD,H par lecture ; G_floor.
   - G_SR, en mesure secondaire, sur une grille réduite (F3 et F2 ; bissection en 6 pas de 200 onsets).
   - K_eff (`sign_diagnostics`).
   - FPR(H) observé et IC lorsque les réplications le permettent. Les fenêtres brutes chevauchantes restent descriptives, sans IC binomial indépendant. Qualifier les gains à seuil nominal commun de tels ; « à fausse alarme égale » exige une calibration iso-FPR sur données indépendantes ou une marge d'équivalence fixée avant test avec IC de la différence. Le simple chevauchement des IC ne suffit pas.
7. **Résumé J2** dans `results/e1/e1_j2_summary.txt`, une ligne PASS/FAIL par critère :
   - (i) flux de signe exacts sur D6 (P1-C sur 5 titres, canaux de P3-C), H ∈ {750, 2 000}, 2 000 réplications par `null_check` : |FPR − niveau du treillis| ≤ 1 point ;
   - (ii) pente de P2-C sur F3 pour N ≥ 20 : IC à 95 % contenant 0, ou borne haute < 0,15 ;
   - (iii) pente de P3-C sur F2 positive, avec un IC à 95 % excluant 0. En cas d'échec, consigner l'attribution (a_max, pente de P3-CS (b), lecture mélange) et renvoyer à la contingence C1 (prompt 23, phase 1) ;
   - (iv) tableau des gains 1 → 2 → 3 → 3-CS à SR = 4 (convention a), mesurés et prévus.

### Entrées
Streams 2 à 8, 8b et 11 ; `results/audit/*.csv` ; `CLAUDE.md`.

### Livrables
- `experiments/e1_problem.py`, `configs/e1.yaml`.
- `results/e1/{e1_cells.csv,e1_slopes.csv,e1_real_phases.csv,e1_null.csv,e1_j2_summary.txt}`, `figures/e1/*`, `logs/e1/`.
- Entrées `C-e1-*` de `docs/DEVIATIONS.md` pour tout choix de grille ou de lecture.

### Contraintes techniques
- Graines `SeedSequence` par (12, cellule, réplication) ; résultats indépendants de `--jobs` (pool `spawn`).
- Les e-détecteurs de dictionnaire sont traités par paquets : aucun tableau (J, K, T) au-delà de 2 Go par paquet.
- `--quick` (100 onsets, SR = 4, N ∈ {16, 64}) en moins de 10 minutes.
- Run complet visé en moins de 8 h sur 48 cœurs ; sinon, effectifs réduits et consignés.
- Aucune ligne datée de 2020 ou après.
- Bootstrap R15 à H = 750 : `H_ref + H = 1 500` dépasse les 941 jours de calib ; utiliser `null_rows=pre_monitor` et étiqueter cette calibration rétrospective. Rédiger les nouveaux audits en anglais.

### Critères de succès
- Deux runs `--quick` identiques au SHA-256.
- Résumé J2 rempli, avec IC et verdicts.
- Chaque nombre du §2 présent dans un CSV ; prévisions et mesures côte à côte.

### Commandes de vérification
```bash
.venv/bin/python experiments/e1_problem.py --quick --out results/e1_quick
.venv/bin/python experiments/e1_problem.py --quick --out /tmp/e1_quick2 && diff <(cd results/e1_quick && sha256sum *.csv) <(cd /tmp/e1_quick2 && sha256sum *.csv)
.venv/bin/python experiments/e1_problem.py --out results/e1 && cat results/e1/e1_j2_summary.txt
```
````

````markdown
## PROMPT 13 — E3 : calibration sous H₀ (exactitude des flux, ARL₀ des e-détecteurs, Γ spectral contre Γ opérationnel)

### Contexte
E3 mesure, sans aucune dérive, la calibration de chaque moniteur sous ses hypothèses de nul :
- le niveau exact du treillis pour les flux de signe ;
- ARL₀ ≥ γ pour les e-détecteurs ;
- FPR(H) empirique visé ≈ α pour les seuils bootstrap ou randomisés.

Il mesure aussi ce que coûtent l'hétéroscédasticité (Γ) et l'asymétrie des données brutes. L'exactitude des signes et la borne ARL₀ ne sont revendiquées que pour les flux satisfaisant les hypothèses conditionnelles ; les données brutes sont un diagnostic empirique. E3 fournit le §5.2 et le critère (i) de J2. Lire `CLAUDE.md`.

Définitions :
- **Γ^spec** = 1 + 2Σ_{k=1}^L (1 − k/(L+1))ρ(k), estimateur de Bartlett/Newey–West calculé sur le flux surveillé avec le même L que `monitors.gamma.gamma_spectral`.
- **Γ^op** = λ_requis/λ_iid pour tenir la cible.
- **Région à 99 %** : p ± z√(p(1 − p)(1/n + 1/n_cal)), avec z = 2,5758 (`C-pipe-null-targets`).

### Tâche
Écrire `experiments/e3_calibration.py`. Les lignes réelles sont limitées à 2005-01-04 → 2019-12-31, avec un contrôle bloquant.
1. **Fonds.**
   - D5 : GARCH(0,08 ; 0,90) à innovations t₇ et gaussiennes. `sim.Garch` couvre t₇ ; utiliser `sim.garch_panel(..., nu=None)` pour le cas gaussien, avec réplications par paquets et conservation bit à bit du chemin t₇. Si un panel à facteur est nécessaire, ajouter un axe de réplication à `sim.garch_panel` sans changer ses sorties quand l'axe n'est pas utilisé (test de non-régression).
   - D6 : SYM-`d2_us97` et SYM-`d3_239`, par les blocs empilés de `pipelines.null_check`.
   - Placebo brut : `d2_us97` et `d3_239`.
2. **Pipelines et lectures.**
   - P1-C : flux d'étiquettes Article B (q̂ de calib) et flux exact centré en 1/2. CUSUM au treillis, comparé à `select_threshold(...)["threshold"]`.
   - P1-D : flux Article B `monitors.streams.energy_stream(r, mu, sigma)` avec `mu = mean(r²)` et `sigma = std(r²)` ajustés sur des lignes propres ; comparer la règle λ_iid × Γ̂ (Γ̂ issu du GARCH de R01) au seuil opérationnel, sans substituer `(z²−1)/sqrt(2)`.
   - P2-C : bootstrap R15 (H = 750) et e-détecteur de pari sur la fraction des signes bruts. `H_ref + H = 1 500` dépasse les 941 jours de calib : utiliser explicitement `null_rows=pre_monitor` et rapporter le chevauchement des fenêtres.
   - P3-C : canaux exacts et dictionnaire d'e-détecteurs. Différer la cellule mélange jusqu'à l'intégration de la porte Holm à 1 % du stream 12 ; réutiliser cette porte sans la dupliquer et mesurer son FPR comme validité approchée. Un non-rejet ne démontre pas l'indépendance.
   - P3-D : fenêtres nulles de calib (H ≤ 941). Pour H = 2 000, utiliser les fenêtres `pre_monitor` et rapporter la non-stationnarité de l'énergie (Γ^op ≈ 191 et 2 346 sur D2, `C-P3D-windows`).
   - P3-CS : (a) randomisation et e-processus ; (b) e-détecteur à mise prévisible.
3. **Mesures.**
   - FPR(H) pour H ∈ {750, 2 000}, avec région à 99 % ; 20 000 trajectoires nulles par cellule de signe. Référence : le niveau exact du treillis pour les flux de signe valides, α comme cible empirique pour le bootstrap et la randomisation. Rapporter le niveau atteint et l'IC, y compris si la cible échoue.
   - IC binomiaux/Wilson sur réplications D5 indépendantes et, conditionnellement au panel fixé, sur nouvelles symétrisations D6 des flux de signe impairs seulement. P1-D/P3-D sont pairs et inchangés par les flips D6 : leurs fenêtres réelles chevauchantes restent descriptives, tout comme les placebos bruts ; ne pas les traiter comme 20 000 observations indépendantes.
   - ARL₀ Monte Carlo des e-détecteurs, de types SR et CUSUM (P2-C, P3-C, P3-CS b) :
     - γ ∈ {20, 100, 252}, sur pièces équitables, D6 et brut ;
     - T_max = 60γ, avec la censure rapportée (une moyenne censurée est une borne inférieure) ;
     - la marge du type SR est mince par construction (E∞[τ] = E∞[M_τ]). Un échec imputable à la plateforme est consigné, jamais corrigé par un nouveau tirage de graines.
   - Γ^spec contre Γ^op pour chaque statistique à amplitude.
4. **Asymétrie des données brutes.**
   - Sur le placebo brut, mesurer le FPR de chaque canal de P3-C et de P1-C, en flux exact (1/2) et en flux recentré (q̂ de calib).
   - Une inflation du FPR est attendue sur les canaux dont la symétrie est rejetée (`CLAUDE.md`). La relier à `results/audit/symmetry_tests.csv`.
5. **Pénalité de dépassement**, à reproduire à ±5 % avec 2 000 trajectoires. CUSUM de premier ordre sur x/σ_inconditionnel, GARCH(0,08 ; 0,90) gaussien :
   - δ = 0,5, λ = 6 : ARL₀ ≈ 2 587 en i.i.d. contre ≈ 889 sous GARCH ;
   - δ = 1, λ = 3 : 1 894 contre 669 ;
   - CUSUM de signe : 213 contre 214 (exact).
6. **Encodeurs à fenêtre.** Avec z_t = moyenne sur L jours de uᵀx, L ∈ {5, 20, 60}, mesurer :
   - Γ_z^spec, attendu ≈ L ;
   - le FPR d'un CUSUM calibré en i.i.d. ;
   - Ljung–Box (20 retards) sur les signes de z.

   Ces mesures justifient un chemin surveillé jour par jour.
7. **Contrôle J2** dans `results/e3/e3_j2_check.txt` : pour chaque flux de signe exact sur D6, |FPR − niveau du treillis| ≤ 1 point.

### Entrées
Streams 4 à 8 et 8b ; `results/audit/symmetry_tests.csv` ; `CLAUDE.md`.

### Livrables
`experiments/e3_calibration.py`, `configs/e3.yaml`, `results/e3/{e3_cells.csv,e3_arl0.csv,e3_raw_placebo.csv,e3_overshoot.csv,e3_window_encoders.csv,e3_j2_check.txt}`, `figures/e3/*`, `logs/e3/`.

### Contraintes techniques
- Graines `SeedSequence` par (13, cellule, réplication) ; résultats indépendants de `--jobs`.
- IC de Wilson là où les réplications sont indépendantes ; option `--quick` ; nouveaux audits en anglais.
- Aucune ligne datée de 2020 ou après.

### Critères de succès
- Flux exacts de D6 dans la région à 99 % du niveau exact ; sur les données brutes, écart quantifié sans revendication d'exactitude.
- ARL₀ des e-détecteurs ≥ γ, ou censure documentée.
- Pénalité de dépassement reproduite.
- Inflation du FPR brut attribuée canal par canal.
- Contrôle J2 écrit.

### Commandes de vérification
```bash
.venv/bin/python experiments/e3_calibration.py --quick --out results/e3_quick
.venv/bin/python experiments/e3_calibration.py --out results/e3 && cat results/e3/e3_j2_check.txt
```
````

````markdown
## PROMPT 14 — CA-T-JEPA : modèle, pré-entraînement et représentation (avec variantes MAE et prétexte temporel)

### Contexte
JEPA-Drift apprend une représentation de la coupe quotidienne par un JEPA transversal (Cross-Asset Temporal JEPA) :
- les actifs sont des jetons, conditionnés par leurs caractéristiques ;
- le masquage porte sur des actifs, avec prédiction dans l'espace latent et cible EMA.

Une tête impaire, obtenue par antisymétrisation, alimente les flux de signe exacts ; une tête paire alimente les capteurs d'énergie. Le code doit être prêt pour la campagne de J3 (1er novembre). Lire `CLAUDE.md`.

### Tâche
0. **Dépendance torch reproductible.**
   - GO d'isolation accordé : créer immédiatement `.venv/torch-cf` depuis le seul canal `conda-forge`, avec le verrou de 65 paquets et `pytorch=2.14.1=cpu_generic*`. `.venv` reste le venv Python 3.12.9 partagé ; ne pas lancer `conda install -p .venv` ni créer de second environnement de travail hors de `.venv`.
   - Développer d'abord via `PYTHONPATH` et un `sitecustomize.py` qui ajoute le site-packages de `.venv/torch-cf` en fin de `sys.path`. Contrôler que numpy 2.4.4, scipy 1.17.1 et pandas 3.0.6 proviennent toujours du venv parent. Ne poser aucun fichier `.pth` dans `.venv` à cette étape.
   - Avant le `.pth`, exécuter `make check` complet et régénérer J1 sous ce shim. Vérifier la signature CRLF native du CSV régénéré et son SHA-256 complet `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`. Le blob LF présent avant régénération n'est pas cette référence. Après ces contrôles seulement, poser le `.pth` et répéter les vérifications sans shim ; consigner les dépendances exactes dans le verrou approuvé.
   - Tous les tests et scripts du stream utilisent `.venv/bin/python`, jamais l'interpréteur Trading seul.
1. **`jepadrift/jepa/ca_tjepa.py`** (torch, CPU, au plus 1 M de paramètres) :
   - jeton i = MLP([x_{i,t}/s_i, C_{i,t}]), où s_i est l'échelle de l'actif, figée sur `pretrain`. C_{i,t} vient de `data_loader.chars.load_chars_tensor("d3_239")` ; le protocole principal utilise les 4 caractéristiques continues connues à t−1. Les 11 indicatrices GICS actuelles ne sont pas point-in-time (`C-D3-gics-static`) : elles ne peuvent servir qu'à une analyse rétrospective séparée et étiquetée. NaN → 0 comptés par `impute_zero` ;
   - 2 à 4 couches d'auto-attention équivariantes par permutation, sans encodage de position (d_model = 64, 4 têtes) ; LayerNorm autorisée, BatchNorm interdite ;
   - encodeur de contexte sur les actifs visibles ; encodeur cible EMA sur tous les actifs (moment de 0,996 à 0,9995, calendrier cosinus) ;
   - prédicteur à 2 couches, dont les requêtes portent C_{i,t} des actifs masqués ;
   - perte L2 dans l'espace latent sur les jetons masqués, plus un terme de variance de type VICReg (charnière sur l'écart-type ≥ 1) ;
   - masquage aléatoire de 30 à 50 % des actifs, ou masquage par secteur (option).
2. **Têtes.**
   - φ_impair(x;C) = ½[g(x;C) − g(−x;C)] et φ_pair = ½[g(x;C) + g(−x;C)], avec g le plongement poolé (moyenne sur les actifs) du tronc.
   - Lecture : ACP blanchissante apprise sur `calib`, D ∈ {2, 4, 8, 16}. Elle est linéaire, donc l'imparité est conservée.
3. **Variantes.**
   - `--objective mae` : un décodeur reconstruit x_{i,t} masqué.
   - `--objective temporal` : les cibles sont les plongements du jour t+1, sur `pretrain` seulement ; l'extraction n'utilise que le jour t.
4. **Script `experiments/jepa_pretrain.py`.**
   - Données : `d3_239`, segment `pretrain`.
   - AdamW (taux 1e-3), lots de 64 jours, au plus 200 époques, arrêt sur la perte JEPA de `calib`.
   - Écrit `ckpt/<hash>/` : poids, configuration, empreinte des données. `ckpt/` est ignoré par git ; ses empreintes sont versionnées.
5. **Représentation** `jepadrift/jepa/representation.py`, sous-classe de `representations.base.Representation` (interface Z-1) qui charge un point de contrôle figé :
   - `state_hash` inclut le SHA-256 du point de contrôle ;
   - `_fit` n'ajuste que la lecture, sur les lignes de calib ;
   - `_day` n'utilise que x_t et C_t ;
   - `transform_panel` peut traiter les jours par lots seulement si le résultat est identique au bit près à l'empilement de `transform_day` ; sinon, boucle jour par jour.
   - Étendre l'extraction pour passer les caractéristiques C alignées à la calib et à chaque jour, tout en conservant le chemin D2 sans caractéristiques et les segments distincts `pretrain`/`calib` ; ne pas ajuster le tronc ou le checkpoint sur la calib. Le stream 17 pose d'abord le socle C partagé ; intégrer son commit avant d'ajouter `ca_tjepa`, `--ckpt` et `--D` aux fichiers communs.
6. **Enregistrement et extraction.**
   - Ajouter une entrée paresseuse `ca_tjepa` dans `representations/extract.REGISTRY` : torch est importé dans la fabrique, jamais à l'import de `jepadrift.representations`.
   - Extraction par la CLI existante, étendue d'une option `--ckpt` : `python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt ckpt/<hash>`. Les lignes extraites suivent `C-repr-rows`.
7. **Contrats.** Les tests paramétrés sur le registre s'appliquent avec une fixture D3 et un checkpoint figé pour `ca_tjepa` : le parcours actuel de tout `REGISTRY` sur D2 avec `cls()` ne convient pas aux représentations qui demandent C et un checkpoint. Préserver les contrats D2/PCA ; coordonner `extract.py` et `tests/test_contracts.py` avec le stream 17. Les quatre gardes torch de `tests/test_contracts.py` doivent tourner dans `make check`, et non être sautées. Remplacer les gardes qui n'inspectent que des modèles jouets ou qui ne peuvent détecter une normalisation temporelle par des assertions sur le CA-T-JEPA réel ; une violation introduite intentionnellement doit faire échouer chaque garde concernée.
8. **Test de fumée** : 2 époques sur 200 jours, extraction, puis contrats.

### Entrées
D3 et caractéristiques (stream 3, chargeur partagé du stream 8b) ; interface Z (stream 6) ; contrats (stream 8) ; `CLAUDE.md`.

### Livrables
- Code : `jepadrift/jepa/{ca_tjepa,representation}.py` ; entrée `ca_tjepa` et option `--ckpt` de `jepadrift/representations/extract.py` ; `experiments/jepa_pretrain.py`.
- Configuration et tests : `configs/ca_tjepa.yaml`, `tests/test_ca_tjepa.py`, verrou d'environnement conda-forge et fichiers de dépendances du projet ajustés selon le plan approuvé.
- Documentation : `docs/sections/ca_tjepa.md` (architecture, nombre de paramètres, choix d'anti-effondrement).

### Contraintes techniques
- `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`, tirages stochastiques avec `torch.Generator` locaux alimentés par `SeedSequence` (initialisation, masques et ordre des lots inclus), sans `torch.manual_seed` global, CPU.
- Aucune méthode non publiée.
- Aucune donnée de `monitor` vue à l'entraînement ou à l'ajustement de la lecture.
- `jepadrift/jepa/` n'importe ni `jepadrift.injection` ni `jepadrift.monitors`.
- Nouveaux comptes rendus d'audit en anglais ; installation de la dépendance partagée sérialisée avec les autres streams.

### Critères de succès
- Contrats au vert, dont imparité ≤ 1e-6, avec les gardes torch exécutées.
- Deux extractions identiques au SHA-256 près.
- Nombre de paramètres ≤ 1 M.
- Test de fumée en moins de 10 minutes ; `make j1` inchangé.

### Commandes de vérification
```bash
.venv/bin/python experiments/jepa_pretrain.py --config configs/ca_tjepa.yaml --smoke
.venv/bin/python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt ckpt/<hash>
.venv/bin/pytest -q -rs tests/test_ca_tjepa.py tests/test_contracts.py
make check
make j1 && sha256sum results/e2/e2_cells.csv
```
````

````markdown
## PROMPT 15 — T-JEPA pour BAF : enveloppe tabulaire et plongements

### Contexte
Sur BAF, domaine tabulaire, JEPA-Drift utilise T-JEPA (Thimonier et al., ICLR 2025) : masquage de colonnes, encodeur cible EMA, prédiction latente, sans augmentation. Les plongements alimentent la surveillance de la dérive des données (P6-D) dans E9. Lire `CLAUDE.md`.

### Tâche
1. Chercher une implémentation officielle publique de T-JEPA. Si elle existe, l'utiliser à un commit épinglé, avec sa licence vérifiée et citée. Sinon, implémenter une version minimale fidèle à l'article dans `jepadrift/jepa/tjepa.py` :
   - un jeton par attribut (linéaire pour les numériques, plongement pour les catégories) ;
   - transformeur sur les jetons ;
   - masques de sous-ensembles de colonnes ;
   - cible EMA, prédicteur.
2. Entraîner sur les mois 0–2 de la variante Base (`preproc.json` : catégories inconnues codées −1 ; `device_fraud_count`, constant, exclu des jetons ; sentinelles −1 déjà standardisées). Licence du jeu : CC BY 4.0.
3. Plongement = moyenne des jetons, puis ACP blanchissante apprise sur le mois 3. D* ∈ {4, 8, 16}, choisi sur les mois 0–2 seulement (RankMe ≥ 0.5·D et perte de validation).
4. Extraire les plongements des mois 0–7 vers `data/derived/d7_baf/z_<hash>.npz`, avec le JSON de l'interface Z. Les lignes ne sont pas des jours : `dates` est remplacé par (`month`, `row`), écart `C-Z-baf`. Enregistrer la représentation par une entrée paresseuse du registre : torch n'est pas importé à l'import de `jepadrift.representations`.
5. Références à produire avec le même extracteur : ACP sur attributs bruts standardisés (90 % de variance) et attributs bruts.

### Entrées
`data/derived/d7_baf/` (prompt 9) ; interface Z ; `CLAUDE.md`.

### Livrables
`jepadrift/jepa/tjepa.py` (ou une enveloppe), `experiments/tjepa_baf.py`, `configs/tjepa_baf.yaml`, plongements et JSON, `tests/test_tjepa.py`, `docs/sections/tjepa_baf.md` (source, écarts à l'article).

### Contraintes techniques
- CPU ; torch installé dans `.venv` selon `CLAUDE.md` (par le stream 14 ; si ce stream démarre avant, l'installer à l'identique et réconcilier `requirements.lock` au rebase) ; déterminisme comme au prompt 14.
- Aucune information des mois 4–7 dans l'entraînement ou la lecture.

### Critères de succès
Contrats de non-anticipation, de déterminisme et d'absence de statistiques de test au vert. La tête impaire est sans objet en tabulaire : la marquer comme absente dans le JSON. RankMe rapporté.

### Commandes de vérification
```bash
python experiments/tjepa_baf.py --smoke
pytest -q tests/test_tjepa.py
```
````

````markdown
## PROMPT 16 — Campagne de pré-entraînement CA-T-JEPA et diagnostics d'effondrement (jalon J3)

### Contexte
J3 (1er novembre) exige une représentation non effondrée : le RankMe de la tête de lecture doit atteindre au moins 0.5·D. Cette campagne entraîne CA-T-JEPA et ses variantes sur trois graines et mesure le rang effectif, avant les comparaisons d'E5. Lire `CLAUDE.md`.

Définition : RankMe(Z) = exp(−Σ_k p_k log p_k), avec p_k = σ_k/Σσ + ε (Garrido et al., ICML 2023).

### Tâche
1. Entraîner, sur `d3_239` (segment `pretrain`), les objectifs `jepa`, `mae` et `temporal`, chacun avec 3 graines (0, 1, 2) ; une exécution par processus et un thread par exécution (`--jobs`, résultats indépendants du nombre de processus) ; enregistrer les points de contrôle. La lecture D ∈ {2, 4, 8, 16} est une ACP post hoc : un seul entraînement par (objectif, graine).
2. Pour chaque point de contrôle et chaque D ∈ {2, 4, 8, 16} :
   - ajuster la lecture sur `calib` et extraire Z ;
   - calculer le RankMe du tronc et de la lecture, la variance par dimension et la part de dimensions de variance inférieure à 1e-3.
3. **Porte J3** : RankMe(lecture) ≥ 0.5·D pour chaque D, sur l'objectif `jepa`. Résultat écrit dans `results/jepa_pretrain/J3_gate.txt`.
4. **Contingence si J3 échoue** : doubler le poids du terme de variance, réduire d_model à 32, relancer une fois et consigner les deux campagnes.
5. Construire le tableau des courbes de perte, à partir des journaux d'entraînement exportés en CSV.

### Entrées
Prompt 14 ; D3 ; `CLAUDE.md`.

### Livrables
`ckpt/<hash>/` (ignoré par git, empreintes versionnées), `results/jepa_pretrain/{runs.csv,rankme.csv,losses.csv,J3_gate.txt}`, `figures/jepa_pretrain/*`.

### Contraintes techniques
CPU (48 cœurs) ; exécutions parallèles déterministes, une par processus ; durée totale consignée ; contrats, dont les quatre gardes torch, au vert sur chaque point de contrôle extrait.

### Critères de succès
12 exécutions principales et 6 de variantes terminées ; porte J3 évaluée ; résultats reproductibles au SHA-256 près pour une graine relancée.

### Commandes de vérification
```bash
python experiments/jepa_campaign.py --dataset d3_239 --seeds 0 1 2 --objectives jepa mae temporal --jobs 9
cat results/jepa_pretrain/J3_gate.txt
```
````

````markdown
## PROMPT 17 — IPCA sur caractéristiques tirées des rendements (pipelines P4)

### Contexte
JEPA-Drift compare le JEPA à des facteurs latents pilotés par les caractéristiques. Le premier est l'IPCA (Kelly, Pruitt & Su, 2019) : x_t = C_t Γ f_t + ε_t, avec des chargements C_tΓ connus en t−1. Ses rendements de facteurs sont linéaires en x_t, donc impairs, et leurs flux de signe sont exacts. Lire `CLAUDE.md`.

### Tâche
1. Implémenter dans `jepadrift/representations/ipca.py` l'estimation par moindres carrés alternés :
   - f_t = (ΓᵀC_tᵀC_tΓ)⁻¹ΓᵀC_tᵀx_t, pour Γ donné ;
   - Γ mis à jour par la régression empilée ;
   - normalisation ΓᵀΓ = I, facteurs orthogonaux ; avec quatre caractéristiques principales, K ≤ 4 et `rank(C_t[in_universe_t] @ Γ) = K` doivent tenir chaque jour utilisé. Consigner les jours déficients et une règle d'exclusion ou de régularisation justifiée ; K = 5, 6 sont non identifiables en principal, sans recours aux GICS rétropolés ni pseudo-inverse silencieuse ;
   - critère d'arrêt sur l'objectif ou le projecteur ΓΓᵀ (ou Γ aligné par Procrustes), pas sur Γ brut sensible aux signes et rotations.
2. Caractéristiques : `data_loader.chars.load_chars_tensor` (stream 8b) ; protocole principal avec les 4 colonnes continues connues à t−1 sur D3 et D4. Les 11 GICS de D3 sont une classification actuelle rétropolée (`C-D3-gics-static`) : les 15 colonnes ne servent qu'à une sensibilité rétrospective explicitement étiquetée, jamais à une conclusion prospective. NaN des caractéristiques → 0 comptés. `d3_500` et D4 sont déséquilibrés : charger le masque `in_universe` aligné aux dates et titres, exclure les rendements manquants des équations et scores sans les imputer. `Representation._check` et `pipelines._panel` refusent les NaN : détailler une adaptation qui conserve les autres représentations et ne traite pas un zéro de remplissage comme une observation. Apprendre Γ sur `pretrain` ; choisir K parmi les rangs identifiables par R² sur actifs de `calib` tenus à l'écart : estimer f_t sur les actifs d'ajustement et scorer les actifs disjoints, avec partage déterministe. Ne pas appeler « hors échantillon » une reconstruction sur les actifs servant à estimer f_t. Blanchir f_t sur `calib` par une transformation linéaire homogène, sans centrage ni intercept de la tête impaire.
3. Option « cash-neutral » : retirer le facteur de marché (constante ou bêta) avant extraction.
4. Enregistrer la représentation et les pipelines P4-C (signes des facteurs, e-détecteur de dictionnaire) et P4-D (énergie). Étendre `extract.py` pour passer C aligné et séparer Γ appris sur `pretrain` de K/blanchiment ajustés sur `calib`, sans changer D2/PCA ; coordonner `extract.py` et `tests/test_contracts.py` avec le stream 14, et `pipelines.py` avec 23 avant les fusions.
5. **Tests** :
   - récupération sur données simulées : sous-espace de Γ retrouvé avec des angles principaux < 5° ;
   - imparité `φ(−x;C) = −φ(x;C)` avec C figé, y compris cash-neutral ; non-anticipation ; état figé ;
   - contrats du prompt 8.

### Entrées
`d3_239`, `d3_500` (et D4) avec leurs caractéristiques ; interface Z ; stream 8b ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/ipca.py`, `tests/test_ipca.py`, extractions, `results/ipca/k_selection.csv`, `docs/sections/ipca.md`.

### Contraintes techniques
numpy seul ; aucune donnée de `monitor` ; nouveaux audits en anglais.

### Critères de succès
Tests au vert ; K choisi et consigné ; contrats passés.

### Commandes de vérification
```bash
.venv/bin/pytest -q tests/test_ipca.py tests/test_contracts.py
.venv/bin/python -m jepadrift.representations.extract --dataset d3_239 --rep ipca
```
````

````markdown
## PROMPT 18 — Adaptateur CD-DFM (facteurs cash-neutral et covariance conditionnelle)

### Contexte
CD-DFM (Alouadi & Lehalle, arXiv:2607.24410, dépôt public) construit des facteurs cash-neutral à partir des caractéristiques et prévoit la covariance. JEPA-Drift l'utilise comme deuxième modèle latent piloté par les caractéristiques (P4) et comme blanchiment conditionnel (canal N2). Ses entrées d'origine (fondamentaux) ne sont pas disponibles : on l'adapte aux caractéristiques tirées des rendements. Lire `CLAUDE.md`.

### Tâche
1. Réutiliser le clone `external/cd-dfm/` du stream 3, dont le commit est épinglé dans `data/derived/MANIFEST.json` ; ne pas recloner. Lire la licence et les dépendances ; le README indique que le panel d'origine n'est pas redistribuable. Toute exécution du stream reste dans la `.venv` du projet ; si ses dépendances ne peuvent y être intégrées, suivre le chemin d'arrêt, sans créer un second environnement.
2. Adapter les entrées : les 4 caractéristiques continues de `d3_239`, connues à t−1 et lues par `data_loader.chars.load_chars_tensor` (stream 8b), au format attendu. Les 11 GICS actuels sont rétropolés (`C-D3-gics-static`) : les utiliser seulement en sensibilité rétrospective étiquetée. Entraîner sur `pretrain` selon la recette du dépôt, avec K = 11 (marché plus dix facteurs cash-neutral), ou documenter dans le plan pourquoi ce rang n'est pas identifiable avec les entrées disponibles.
3. Extraire :
   - les rendements de facteurs, linéaires en x_t avec appartenances connues en t−1, donc impairs ;
   - la covariance prévue Σ̂(t), pour le blanchiment conditionnel.

   Emballer le tout dans l'interface Z, avec un JSON qui précise l'écart d'entrées.
4. Enregistrer P4-C et P4-D (variante CD-DFM) après intégration de la variante IPCA du stream 17 dans le registre partagé ; l'adaptateur et ses tests peuvent être développés en parallèle.
5. Avant toute installation, vérifier au commit épinglé que la chaîne officielle d'entraînement est complète, notamment le module `data.dataset` et l'objet `preprocess_panel` importé depuis `data`. Si ces éléments manquent, livrer seulement un diagnostic factuel dans `docs/sections/cddfm_adapter.md` (commit, fichiers/imports absents, licence observée) ; ne créer ni adaptateur, ni extraction, ni entrée P4, ni remplacement local du code manquant. Même chemin d'arrêt si les dépendances sont introuvables. Priorité B.

### Entrées
Dépôt CD-DFM ; D3 et caractéristiques ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/cddfm_adapter.py`, extractions, `tests/test_cddfm_adapter.py`, `docs/sections/cddfm_adapter.md`, entrée `C-CDDFM-inputs` dans `docs/DEVIATIONS.md`.
Si la tâche 5 déclenche l'arrêt, seul le diagnostic documentaire et le plan/wrapup sont exigés ; les livrables de modèle et les critères de test ci-dessous ne s'appliquent pas.

### Contraintes techniques
Code externe non modifié (adaptateur seulement) ; graines fixées ; CPU ; nouveaux audits en anglais.

### Critères de succès
Imparité des rendements de facteurs ≤ 1e-6 ; contrats au vert ; écart d'entrées documenté.

### Commandes de vérification
```bash
.venv/bin/pytest -q tests/test_cddfm_adapter.py tests/test_contracts.py
```
````

````markdown
## PROMPT 19 — E4 : lois d'échelle en N et antériorité PCA « queue » (P3-KF, SPLL)

### Contexte
La signature falsifiable de JEPA-Drift est la loi d'échelle du gain en fonction de la taille N de la coupe (Corollaire 2) :
- N⁰ pour le pooling face à une dérive de marché ;
- N^{1/2} pour une dérive de largeur surveillée dans tout le résiduel par un mélange isotrope ;
- N¹ pour une largeur portée par quelques directions de caractéristiques.

Sur données réelles, le mélange isotrope n'est pas exactement valide (porte d'indépendance, `C-P3C-mixture-gate`). Le détecteur par défaut est donc le dictionnaire, dont la loi d'échelle dépend aussi de l'alignement. E4 mesure les pentes, les attribue, et reproduit l'antériorité de Kuncheva sur les composantes de faible variance. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e4_scaling.py`. Avant J4, seules les lignes antérieures à 2020 sont lues, avec un contrôle bloquant.
1. **Jeux.**
   - `d2_us97`, `d3_239`, `d3_500` [A] ; D4 [B], s'il est construit (`C-D4-survivor`) ; tous symétrisés (D6).
   - Pour `d3_500` et D4 : sous-panel complet sur chaque fenêtre (titres `in_universe` tous les jours de la fenêtre), tiré avec graine.
2. **Grille.** N ∈ {8, 16, 32, 64, 128, 239, 500}, borné par la taille du sous-panel. Par N : 20 sous-ensembles emboîtés, tirés avec graine et communs à tous les pipelines.
3. **Familles**, en convention (b). Les grilles d'amplitude suivent la règle du prompt 12 (délai médian dans [20 ; 0,8·H]) et sont consignées.
   - F1 : primes fixes sur K facteurs.
   - F2 : κ, sur D3 et D4 seulement ; D4 n'a que 4 caractéristiques continues.
   - F3 : SR RMS par titre fixé.
4. **Pipelines.**
   - P2-C, P3-C (factoriel et complet), P3-KF, P3-CS (b), P4-C (IPCA ; CD-DFM si disponible).
   - Lecture anytime-valid à γ_H = H/α, avec H = 2 000 ; canaux exacts en diagnostic.
5. **P3-KF**, dans `jepadrift/monitors/spll.py` : détecteur semi-paramétrique de log-vraisemblance de Kuncheva (2013, IEEE TKDE ; vérifier la référence).
   - Entrées : composantes « tail10 » (m = 46 sur D2, 123 sur `d3_239`).
   - k-moyennes sur la fenêtre de référence, statistique sur fenêtre glissante.
   - Seuil calibré sur des fenêtres nulles D6, pour FPR(H) = α.
6. **Mesures.**
   - Pente de log G_ADD en log N (opposée de la pente de log ADD médian, comme au prompt 12), avec IC bootstrap sur les sous-ensembles.
   - Exposants prévus par le Corollaire 2 (0, 1/2, 1). Pour le dictionnaire, prévision corrigée par l'alignement mesuré a_max(N) (`floors.dictionary_multiplier`).
   - Audit réduit par sous-ensemble, sur les sous-espaces marché, factoriel et résiduel : `stats.drift.debiased_sr2` et `mbb_indices` (stream 8b).

### Entrées
Streams 5, 7, 8b, 11 et 17 (et 18) ; `CLAUDE.md`.

### Livrables
`experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`, `results/e4/{e4_cells.csv,e4_slopes.csv,e4_audit_subsets.csv}`, `figures/e4/*`, `logs/e4/`.

### Contraintes techniques
- `jepadrift/monitors/spll.py` en numpy seul ; k-moyennes implémentées dans le module, graines passées en argument.
- Mêmes graines de sous-ensembles et d'onsets pour tous les pipelines.
- Résultats indépendants de `--jobs` ; option `--quick`.

### Critères de succès
- Pentes et IC pour chaque (jeu, famille, pipeline).
- P3-KF dans la région à 99 % de α sur fonds nuls.
- Chaque pente faible attribuée, à l'information ou à l'alignement.

### Commandes de vérification
```bash
python experiments/e4_scaling.py --quick --out results/e4_quick
python experiments/e4_scaling.py --out results/e4 && head results/e4/e4_slopes.csv
```````

````markdown
## PROMPT 20 — Spectres de transmission T(u) et comparaison dictionnaire contre sous-espace

### Contexte
JEPA-Drift doit montrer ce que chaque représentation transmet d'une dérive. Le rapport de transmission vaut T(u) = ‖Σ_z^{−1/2} E[J_φ] u‖² / ‖Σ^{−1/2} u‖², avec J_φ la jacobienne de l'encodeur. La prédiction testée est T_JEPA > T_MAE sur les directions de faible variance. JEPA-Drift compare aussi deux priors sur la direction de dérive : dictionnaire d'atomes économiques contre mélange isotrope (Prop. 3d). Lire `CLAUDE.md`.

### Tâche
1. Écrire `experiments/transmission.py` :
   - E[J_φ]u ≈ moyenne sur les jours de `calib` de [φ(x + εu) − φ(x − εu)]/(2ε), avec ε = 1e-3·‖x‖ ;
   - Σ_z estimé sur `calib` ;
   - directions u : résiduelles PC2–PC51, facteurs CD-DFM (si disponibles), caractéristiques orthogonalisées, directions F1 et F2 injectées ;
   - représentations : JEPA, MAE, temporel, ACP, IPCA.
2. Écrire `experiments/dictionary_vs_subspace.py`, sur fonds D6 de `d3_239` avec F1 et F2 :
   - (A) moyenne de K e-détecteurs le long d'atomes, K ∈ {10, 20, 50} ;
   - (B) mélange isotrope sur le sous-espace résiduel de dimension D, valide seulement si les coordonnées sont indépendantes : le comparer sur fonds D5 (coordonnées indépendantes) et, sur D6, rapporter l'état de la porte d'indépendance corrigée de la multiplicité (prompt 12) ;
   - mesurer cos²ϑ et les délais, puis comparer à `floors.dictionary_multiplier` et `floors.mixture_multiplier` (angles de bascule) ; lecture anytime-valid à γ_H = H/α (`CLAUDE.md`).

### Entrées
Prompts 16 à 18 ; `CLAUDE.md`.

### Livrables
`results/transmission/{spectra.csv,summary.csv}`, `results/dictionary/cells.csv`, `figures/{transmission,dictionary}/*`.

### Contraintes techniques
Aucune donnée de `monitor` ; graines fixées.

### Critères de succès
Spectres pour toutes les représentations disponibles ; écart entre délais mesurés et prédits rapporté (±10 % attendu en approximation fluide).

### Commandes de vérification
```bash
python experiments/transmission.py --out results/transmission
python experiments/dictionary_vs_subspace.py --quick --out results/dictionary_quick
```
````

````markdown
## PROMPT 21 — Gel de configuration, `benchmark_runner`, figures depuis CSV et traçabilité des nombres

### Contexte
Au jalon J4 (8 novembre), JEPA-Drift gèle sa configuration (empreinte unique) avant tout passage sur la fenêtre de test 2020–2025, pour supprimer les degrés de liberté a posteriori. Ensuite, chaque figure et chaque nombre de l'article doivent se régénérer depuis un CSV. Lire `CLAUDE.md`.

### Tâche
1. **`jepadrift/benchmark_runner.py`.**
   - Point d'entrée unique : `--config configs/<stream>.yaml`. Il appelle le `main(argv)` des scripts existants (`experiments/e1_problem.py`, `e3_calibration.py`, …) sans les réimplémenter.
   - `run_hash` = SHA-256 de la configuration en JSON canonique, du commit git et des empreintes du manifeste de données.
   - Sortie `results/<stream>/<run_hash>.csv`, une ligne par réplication : `seed, family, D, gamma, reading, ADD, alarm, ...`.
2. **`tools/freeze_config.py`.**
   - Écrit `configs/FROZEN.json` : empreintes de toutes les configurations d'expérience, commit, et empreintes de `data/derived/MANIFEST.json` et `docs/manifests/d4_manifest.json` ; cible `make freeze`.
   - Le runner refuse `--include-test-window` si l'empreinte courante diffère du gel.
3. **`figures/make_<fig>.py`** : un script par figure, lecture des CSV seulement, export PNG et PDF. Inclure la figure d'E2 : délais mesurés contre prédits, avec les trois lectures et le premier ordre.
4. **`tools/trace_numbers.py`.**
   - Analyse `paper/*.tex` : macros `\E{key}` ou nombres balisés.
   - Vérifie chaque nombre contre le CSV et la colonne déclarés dans `docs/MAPPING.md`, à l'arrondi près.
   - Échoue en cas d'écart.
5. **`tools/dpi_lint.py`** : signale toute phrase qui suggère une hausse de KL ou d'information (motifs : « increase(s|d) … (KL|information|divergence) », « create(s) information », etc.).
6. **`tools/appendix_b.py`** : produit les tableaux de paramètres des générateurs et des dérives depuis `configs/` et `docs/sections/injection.md`.

### Entrées
Scripts E1, E3 et suivants ; `CLAUDE.md`.

### Livrables
Les outils ci-dessus, `configs/FROZEN.json` (au J4), `docs/MAPPING.md` initialisé avec les nombres déjà cités (E2/J1, identités R01/R08/R15, audit, E1, E3), `tests/test_tools.py`.

### Contraintes techniques
Aucune figure lue depuis un état en mémoire ; aucun nombre saisi à la main dans `paper/`. `results/e2/e2_cells.csv` est en fins de ligne CRLF (empreinte de référence) : ne pas le normaliser ; `make j1` réécrit la ligne de durée du résumé. Fusion requise avant le stream 22 et avant toute exécution sur la fenêtre de test.

### Critères de succès
- Une exécution E1 via le runner reproduit `results/e1/e1_cells.csv` bit à bit.
- Le gel bloque un test sur la fenêtre 2020+ avec une configuration modifiée.
- `trace_numbers` détecte un nombre altéré (test).

### Commandes de vérification
```bash
pytest -q tests/test_tools.py
python tools/freeze_config.py --check
python tools/trace_numbers.py paper/ --mapping docs/MAPPING.md
```
````

````markdown
## PROMPT 22 — E5 : JEPA contre références linéaires, attribution et balayage de D (jalon J4)

### Contexte
E5 est le test central de JEPA-Drift. La tête impaire du JEPA (P5-C) doit détecter plus vite que les meilleures références linéaires, à fausse alarme égale, sur des dérives injectées dans des fonds D6. Les références sont :
- P3-C (ACP) ;
- P3-CS (b), coupe de degré 0 à mise prévisible, qui capte déjà le canal N1 ≈ 2 mesuré par l'audit ;
- P4-C (IPCA, CD-DFM).

La porte J4 (8 novembre) décide du titre de l'article. Lire `CLAUDE.md`.

Définitions :
- **Rétention** : r(D) = I_z/I_x.
- **Taxe** : M(D) (`floors.mixture_multiplier`) pour un mélange ; pour un dictionnaire, le multiplicateur de `floors.dictionary_multiplier` avec l'alignement mesuré a_max.
- **Lecture** : anytime-valid à γ_H = H/α, avec H = 2 000 (`CLAUDE.md`).

### Tâche
Écrire `experiments/e5_jepa.py`, exécuté via `jepadrift.benchmark_runner` avec la configuration gelée. Avant le gel, seules les lignes 2005–2019 sont lues.
1. **Jeux** : `d3_239` [A] ; `d2_us97` [B, F1 et F3 seulement] ; D4 [B, sous-panel complet, `C-D4-survivor`] ; fonds D6.
2. **Pipelines.**
   - P5-C (lecture D ∈ {2, 4, 8, 16}, 3 graines) contre P3-C, P3-CS (b) et P4-C.
   - Ablations P5-MAE et P5-TEMP ; P3-CS (a) en secondaire.
3. **Familles** : F1, F2, F3. Convention (a) avec SR ∈ {2, 4, 8} ; convention (b) avec les grilles consignées au prompt 12.
4. **G_ADD**, avec IC bootstrap sur les graines et les onsets. Mêmes lecture, onsets et fonds pour tous les pipelines.
5. **Rétention et alignement.**
   - Δz est mesuré par paires sur des fonds identiques : moyenne sur les jours de φ(x + Δ) − φ(x), à travers l'encodeur gelé.
   - I_z = ½ΔzᵀΣ_z⁻¹Δz, avec Σ_z estimé sur la calib ; I_x = ½ΔᵀΣ̂⁻¹Δ.
   - a_max est rapporté par pipeline.
   - D* est choisi sur `calib` seulement.
6. **Diagnostics** : RankMe, T(u) (prompt 20), dictionnaire contre sous-espace [C].
7. **Attribution** : P3-CS (b) figure dans chaque tableau principal ; l'écart P5 − P3-CS (b) est rapporté avec son IC.
8. **Porte J4.**
   - Condition : G_ADD(meilleur de P3-CS (b) et P4 → P5) ≥ 1,25 sur au moins deux familles parmi F1, F2 et F4, avec un IC à 95 % qui exclut 1.
   - F4 provient d'E6, phase 2 (P5-D).
   - Écrire `results/e5/J4_gate.txt` : « titre A » ou « titre B ».

### Entrées
Streams 16, 17, 19, 21 et 23 (phase 2), et en complément 18 et 20 ; `CLAUDE.md`.

### Livrables
`experiments/e5_jepa.py`, `configs/e5.yaml`, `results/e5/{e5_cells.csv,e5_retention.csv,J4_gate.txt}`, `figures/e5/*`, `logs/e5/`.

### Contraintes techniques
- Fenêtre de test interdite avant le gel.
- Mêmes graines d'onsets pour tous les pipelines.
- L'option mélange de P3-C est exclue des verdicts (validité approchée).

### Critères de succès
- Porte J4 évaluée avec ses IC.
- Tableaux principaux complets, P3-CS (b) compris.
- r(D), a_max et M(D) rapportés pour chaque D.

### Commandes de vérification
```bash
python -m jepadrift.benchmark_runner --config configs/e5.yaml --quick
python -m jepadrift.benchmark_runner --config configs/e5.yaml && cat results/e5/J4_gate.txt
```````

````markdown
## PROMPT 23 — E6 : dérives de second ordre F4 (rotations, déformations de covariance), en deux phases

### Contexte
L'audit montre deux choses aux transitions datées de SPY (wrapups 11 et 11b) :
- l'information de localisation hors marché y est noyée dans le bruit ;
- le SR² de marché y relève de la sélection.

La contingence C1 de JEPA-Drift, qui fait du second ordre l'axe principal, devient donc plausible. Dans le modèle gaussien de conception, un rapport de variance r porte ½(r − 1 − ln r) nat par jour et par direction : 24 fois le budget d'une dérive de SR = 1 pour r = 1,5, 77 fois pour r = 2. Ce n'est pas la KL exacte des fonds D5 à innovations t₇ ou D6. La phase 1 (capteurs linéaires) démarre sans attendre le JEPA ; la phase 2 ajoute la tête paire du JEPA. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e6_second_order.py` avec l'option `--phase {1,2}`.
1. **Fonds.**
   - Principal : fenêtres D6 de `d3_239` prises dans le segment de calib (2016-04 → 2019-12), avec H ∈ {250, 500}. L'énergie blanchie n'est pas stationnaire sur 2005–2019 : Γ^op ≈ 191 et 2 346, contre 7,6 et 25,2 en calib (`C-P3D-windows`). Les fenêtres se chevauchent et réutilisent les jours qui fixent les seuils : FPR D6 descriptif, sans IC inférentiel. Pour G_ADD, utiliser un `deff` ou bootstrap par blocs justifié ; si 941 jours ne permettent pas un IC fiable, rapporter `IC=NA` et sa raison. Ne pas assimiler `floor(941/H)` à une taille effective estimée.
   - Contrôle : panels D5 indépendants, N = 239 (`sim.garch_panel`, facteur équicorrélé ρ = 0,40, t₇). Si K est fixé plutôt qu'estimé sur D5, étiqueter l'analyse conditionnelle à ce choix et inclure K = 1 (facteur vrai) en sensibilité.
2. **Dérives F4** (`injection.inject`) :
   - déformation r ∈ {1,25 ; 1,5 ; 2} sur les sous-espaces des 3 premières PC résiduelles ou d'un facteur sectoriel ;
   - rotation θ ∈ {15°, 30°, 45°}, avec PC2–PC3 comme témoin négatif déclaré avant l'exécution ; cette paire a déjà été examinée sur D6 et reste exploratoire sur D6, mais peut être préspécifiée pour les panels de test D5 indépendants ; étiqueter les autres paires choisies après sonde comme exploratoires ;
   - information quadratique gaussienne de conception lue dans `meta`, sans l'appeler KL exacte des fonds non gaussiens.
3. **Pipelines.** CUSUM d'énergie, δ = 0,5 ; seuil calculé sur toutes les fenêtres nulles de calib, α = 0,05 à l'horizon H ; Γ_z^op rapporté.
   - Phase 1 immédiatement : P1-D (indice équipondéré) et P3-D (factoriel et complet). Ajouter P4-D (IPCA) seulement après fusion du stream 17 ; ne pas bloquer la livraison P1-D/P3-D.
   - P1-D reprend le flux d'énergie de l'Article B : `q_t = (r_t² − μ̂)/σ̂`, avec `μ̂ = mean(r²)` et `σ̂ = std(r²)` ajustés sur les lignes sans dérive. Ne pas le remplacer par `(z² − 1)/sqrt(2)` ni par une normalisation avec `std(r)`. Si le seuil P3-D issu de `fit_pipeline` est remplacé sur D5, recalculer `Γ_z^op = λ_D5/λ_iid` avec le seuil final.
   - Phase 2 : P5-D, tête paire du CA-T-JEPA (stream 16).
4. **Mesures.**
   - Délais, taux de détection, G_ADD et IC.
   - Comparaison au budget gaussien de conception, avec étiquette de modèle. Pour une rotation, rapporter l'information conjointe ; un partage égal entre directions est une convention comptable, pas une KL identifiée par direction. `floors.evidence_budget` reste un repère de conception, pas une borne de délai du CUSUM d'énergie.
   - Contribution à la porte J4 (famille F4, phase 2).

### Entrées
Phase 1 : streams 5 et 7 (et 17 pour P4-D). Phase 2 : stream 16. `CLAUDE.md`.

### Livrables
`experiments/e6_second_order.py`, `configs/e6.yaml`, `results/e6/{e6_cells_phase1.csv,e6_cells_phase2.csv}`, `figures/e6/*`, `logs/e6/`.

### Contraintes techniques
- Les statistiques paires ne se calibrent pas par inversion de signe : fenêtres nulles de calib uniquement.
- Graines fixées.
- Aucune ligne datée de 2020 ou après.
- Nouveaux comptes rendus d'audit, dont `docs/DEVIATIONS.md`, en anglais ; journaux locaux non indexés dans Git.

### Critères de succès
- FPR sous H₀ avec IC sur le contrôle D5 indépendant ; FPR D6 dans l'échantillon, descriptif et sans IC inférentiel.
- Rapport de délais restreints à H, avec censure étiquetée et IC bootstrap apparié sur les panels de test D5 indépendants ; pour D6, `IC=NA` motivé si la dépendance empêche une estimation fiable.
- Phase 1 P1-D/P3-D livrée avant J3, P4-D après le stream 17, phase 2 avant J4.

### Commandes de vérification
```bash
.venv/bin/python experiments/e6_second_order.py --phase 1 --quick --out results/e6_quick
.venv/bin/python experiments/e6_second_order.py --phase 1 --out results/e6
```
````

````markdown
## PROMPT 24 — E9 : dérives natives de BAF (P6-D données, P6-C concept)

### Contexte
E9 évalue la surveillance de JEPA-Drift hors finance, sur la dérive mensuelle native du jeu synthétique BAF. Deux cas : dérive des données, par martingale de test conforme sur plongements ; dérive de concept, par flux d'erreur d'un classifieur figé avec taux nul recentré. Les lignes d'un même mois sont traitées comme échangeables. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e9_baf.py`.
1. **P6-D.**
   - Score de non-conformité : distance au 10ᵉ plus proche voisin dans un échantillon de référence (50 000 lignes des mois 0–2), sur les plongements T-JEPA, ACP et bruts (`device_fraud_count`, constant, exclu).
   - Échangeabilité : tester l'ordre intra-mois (test des runs et autocorrélation des scores sur le mois 3) ; en cas de rejet, permuter les lignes de chaque mois avec une graine fixe et consigner `C-BAF-order`.
   - p-valeurs conformes lissées.
   - Martingale de puissance mélangée sur ε ∈ {0.1, …, 0.9} (Vovk et al., 2003), alarme à 1/α.
   - Mesures : délai en lignes après chaque frontière de mois ; FPR dans des mois stables (lignes permutées dans un mois).
2. **Confirmation hors ligne** : test MMD par permutation entre mois consécutifs (noyau RBF, heuristique de la médiane, 2000 lignes par mois, 1000 permutations).
3. **P6-C.**
   - `HistGradientBoostingClassifier` (`random_state` fixé) entraîné sur les mois 0–2, puis figé.
   - Flux d'erreur binaire au seuil choisi sur le mois 3 ; taux nul q̂ estimé sur le mois 3.
   - e-détecteur de pari recentré sur q̂.
   - Délai d'étiquetage simulé (étiquettes disponibles après L lignes, L ∈ {0, 10 000, 50 000}).
   - Ajouter des p-valeurs conformes sur l'erreur.

### Entrées
Prompts 9 et 15 ; bibliothèque de surveillance ; `CLAUDE.md`.

### Livrables
`experiments/e9_baf.py`, `configs/e9.yaml`, `results/e9/{e9_data_drift.csv,e9_concept_drift.csv,e9_mmd.csv}`, `figures/e9/*`.

### Contraintes techniques
Aucune donnée des mois 4–7 dans l'apprentissage ; scikit-learn autorisé ici ; graines fixées.

### Critères de succès
FPR dans les mois permutés au plus α (IC) ; délais rapportés par frontière ; MMD rapporté ; formulation « dérive native d'un jeu synthétique » dans le CSV de métadonnées.

### Commandes de vérification
```bash
python experiments/e9_baf.py --quick --out results/e9_quick
```
````

````markdown
## PROMPT 25 — E8 : régimes réels et trois datations (après gel J4)

### Contexte
E8 confronte les pipelines de JEPA-Drift aux phases haussières et baissières réelles. C'est un appui, jamais une preuve.

Trois datations sont disponibles :
- `lt_spy` (66 phases) : Lunde–Timmermann pour SPY, Pagan–Sossounov pour les autres ETF ;
- `strict_ps` (48 phases) : Pagan–Sossounov strict partout ;
- `symmetric` (102 phases) : variante symétrique.

Sur SPY, `lt_spy` et `symmetric` coïncident (30 phases).

Deux biais sont établis :
- les frontières datées ex post sélectionnent les phases. Placebo du stream 11b : SR² de marché réel de 19 à 41, contre ≈ −2,5 sous rotation, p ≤ 0,0015 ;
- D3 et D4 sont des univers de survivants (`C-D3-survivor-correction`, `C-D4-survivor`).

E8 ne s'exécute qu'avec la configuration gelée au J4. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e8_real_regimes.py`, lancé via le runner avec `--include-test-window`.
1. **Phases.**
   - Fichiers `phases_*.csv` de D1.
   - Pour D2, D3 (et D4 [B]) : phases de SPY, plus une datation Pagan–Sossounov sur les indices sectoriels équipondérés de D3.
2. **Placebo.** 2 000 rotations circulaires de chaque chaîne de phases (`stats.drift.rotate_phases`). Chaque mesure par phase est rapportée avec sa distribution placebo.
3. **Pipelines.**
   - P1 à P5, avec D* et seuils gelés.
   - Sur données brutes, les flux de signe sont recentrés sur q̂ de calib pour les canaux dont la symétrie est rejetée (`CLAUDE.md`). Aucune exactitude n'est revendiquée.
4. **Mesures**, par phase et par datation :
   - Î débiaisé du sous-espace du pipeline ;
   - part des phases dans le budget (L·Î ≥ ln γ, γ ∈ {20, 252}), en lecture budget. À cause de la sélection, c'est une borne supérieure ;
   - alarmes dans la phase (lecture anytime-valid γ_H) ;
   - fausses alarmes en phases calmes ;
   - délai depuis le début de phase ;
   - écart à la distribution placebo.
5. **Rapport.**
   - Résultats par datation, jamais agrégés en une seule preuve.
   - Comparaison au recensement de l'Article B (R16 : 80,3 % hors budget à γ = 20 sur 66 phases, `R16-out-of-budget-frac`), en rappelant sa datation et la sélection.

### Entrées
Stream 21 (gel) ; stream 8b (placebo, débiaisage) ; tous les pipelines ; `CLAUDE.md`.

### Livrables
`experiments/e8_real_regimes.py`, `configs/e8.yaml`, `results/e8/{e8_phases.csv,e8_placebo.csv,e8_summary.csv}`, `figures/e8/*`, `logs/e8/`.

### Contraintes techniques
- Refus d'exécution si `configs/FROZEN.json` ne correspond pas.
- Aucune retouche après lecture des résultats sans nouvelle empreinte consignée.

### Critères de succès
- Trois datations traitées.
- IC de Wilson sur les proportions.
- Chaque mesure accompagnée de son placebo.
- Empreinte de gel inscrite dans chaque CSV.

### Commandes de vérification
```bash
python tools/freeze_config.py --check && python -m jepadrift.benchmark_runner --config configs/e8.yaml --include-test-window
```````

````markdown
## PROMPT 26 — E7 : absorption par un encodeur adaptatif et vieillissement de l'encodeur gelé

### Contexte
Un encodeur mis à jour en ligne absorbe la dérive. Le critère d'absorption de JEPA-Drift (Prop. 4) prévoit qu'il ne détecte presque sûrement que si τ_a > 2τ_γ, avec un délai fluide de −(τ_a/2)·ln(1 − 2τ_γ/τ_a). Un encodeur gelé n'absorbe rien, mais vieillit. E7 mesure les deux effets. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e7_absorption.py`.
1. **P5-ADAPT** : CA-T-JEPA ajusté en ligne sur une fenêtre glissante, avec un taux d'apprentissage qui fixe une mémoire effective. τ_a est mesuré empiriquement par la décroissance de Δz après l'onset.
2. **Comparaison avec P5-C gelé**, sur F1 et F2 injectées sur fonds D6 de `d3_239`, avec τ_a/τ_γ ∈ {0.5, 1, 2, 4, 8}, en lecture anytime-valid à γ_H = H/α (`CLAUDE.md`). Comparer les délais mesurés à la prédiction calculée avec le τ_a mesuré (`floors.absorption_delay`).
3. **Vieillissement** : sous H₀, ARL₀ par tranche annuelle depuis la fin du pré-entraînement, sur fonds symétrisés. Avant J4, tranches 2016–2019 seulement ; 2020 et au-delà uniquement avec la configuration gelée.

### Entrées
Prompts 14 et 16 ; `CLAUDE.md`.

### Livrables
`experiments/e7_absorption.py`, `configs/e7.yaml`, `results/e7/{e7_absorption.csv,e7_aging.csv}`, `figures/e7/*`.

### Contraintes techniques
Mises à jour en ligne strictement causales ; graines fixées ; CPU.

### Critères de succès
Seuil τ_a ≈ 2τ_γ observé ou réfuté avec IC ; ARL₀ par âge rapporté.

### Commandes de vérification
```bash
python experiments/e7_absorption.py --quick --out results/e7_quick
```
````

````markdown
## PROMPT 27 — E10 : robustesse (queues épaisses, levier, dépendance asymétrique, rendements nuls)

### Contexte
L'exactitude des flux de signe de JEPA-Drift suppose la symétrie centrale conditionnelle. E10 mesure jusqu'où les fausses alarmes et les gains tiennent quand elle est violée, et ce que corrige le recentrage sur un taux estimé q̂_u. Annexe D. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e10_robustness.py`.
1. **Fonds D5** :
   - t_ν avec ν ∈ {3, 4, 5, 7} ;
   - GJR-GARCH (levier ∈ {0, 0.05, 0.10}) ;
   - choc commun asymétrique (dépendance de queue asymétrique) ;
   - part de rendements nuls ∈ {0, 2 %, 5 %}, par arrondi.

   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4), avec ses violations naturelles mesurées par l'audit (symétrie rejetée sur PC1, PC2, PC3 et `rev_21` selon le jeu, `CLAUDE.md`) et ses rendements nuls (2 864 sur D2 avant 2020, tranchés par pièce).
   Les innovations t_ν symétriques et un levier GJR prévisible avec innovations symétriques conservent la symétrie conditionnelle ; les égalités dues à l'arrondi sont départagées par des pièces indépendantes issues d'un PRNG local. Classer chaque fond par validité du nul avant d'interpréter son FPR.
2. **Pipelines par portes** : P1-C et P3-C sur F1 dès maintenant, avec et sans recentrage sur q̂_u estimé sur `calib` ; F2 sur D3 seulement après le chargeur partagé du stream 8b, sans pivot local dupliqué ; P5-C seulement après disponibilité d'un point de contrôle gelé du stream 16. Le P1-C existant est dans `monitors/cusum.py`, pas dans `pipelines.PIPELINES` : réutiliser ce noyau avant d'envisager une entrée de registre. Une option explicite sélectionne les familles et l'exécution initiale ne dépend ni de 8b ni de P5-C.
   Pour P3-C recentré, utiliser un flux borné `x = (B − q̂_u) / max(q̂_u, 1 − q̂_u)` avec `q̂_u ∈ [0, 1]` appris sur `calib` puis gelé. Ne pas transmettre `2(B − q̂_u)` à `eprocess._bounded` s'il sort de `[-1, 1]`. Le recentrage estimé est descriptif sans preuve de moyenne conditionnelle nulle tenant compte de son erreur d'estimation.
   Pour chaque paire de variantes P1-C et P3-C, départager les zéros par des pièces locales indépendantes, réutiliser les mêmes bits réalisés entre les bras et estimer q̂ sur `calib` avec cette même convention. Si la règle « zéro = négatif » de l'Article B est rapportée, en faire un bras distinct : elle ne doit pas confondre l'effet du recentrage.
3. **Mesures** : FPR observé avec IC contre le niveau nominal et le niveau atteint sous le nul valide ; G_ADD sur F1 immédiatement, puis F2 sur D3 uniquement (D2 n'a pas de caractéristiques), à γ_H = H/α. Sur les placebos bruts asymétriques, ne pas qualifier la lecture de garantie exacte. Rapporter le FPR atteint à côté de chaque gain ; si les FPR diffèrent, ne pas conclure à un gain à fausse alarme égale.
   Le rapport `RMST_P1/RMST_P3` est un rapport de délais restreints à H ; il ne borne le rapport d'ADD que si P3 n'est pas censuré. Le chevauchement des IC de FPR ne démontre pas leur équivalence : une revendication « à fausse alarme égale » exige une marge préspécifiée et un test d'équivalence valide. Les pièces indépendantes entre canaux ne fournissent qu'un scénario de référence iid, pas le FPR atteint universel du dictionnaire P3-C dépendant. Le placebo brut sur pretrain, ajusté sur une calib ultérieure, est rétrospectif ; un titre choisi sur les résultats F1 est un oracle exploratoire.

### Entrées
Étape initiale F1 : prompts 5 et 7. Complément F2 : stream 8b. Complément P5-C : stream 16 et son point de contrôle gelé ; `CLAUDE.md`.

### Livrables
`experiments/e10_robustness.py`, `configs/e10.yaml`, `results/e10/e10_cells.csv`, `figures/e10/*`.

### Contraintes techniques
Graines locales `SeedSequence` ; option `--quick` ; aucun accès aux lignes réelles datées de 2020 ou après avant J4. Pour les fenêtres brutes chevauchantes, n'utiliser un IC qu'avec un `deff` estimable et `1 ≤ n_eff ≤ n` ; si l'indicatrice est constante ou l'estimateur pathologique, indiquer `IC=NA`, sans fabriquer une précision binomiale avec `floor(lignes/H)`. Exporter tous les CSV par `save_fair_csv` ; rédiger les nouveaux comptes rendus d'audit en anglais.

### Critères de succès
Inflation du FPR quantifiée par violation, avec IC ; effet du recentrage rapporté.

### Commandes de vérification
```bash
.venv/bin/python experiments/e10_robustness.py --stage linear --families F1 --quick --out results/e10_quick
```
````

````markdown
## PROMPT 28 — E11 : second domaine en coupe transversale (D8 : Electricity ; SWaT et WADI en option)

### Contexte
E11 teste la portée de JEPA-Drift sur des capteurs corrélés hors finance (Annexe D) : 370 clients électriques (UCI ElectricityLoadDiagrams20112014). SWaT et WADI exigent une demande d'accès à iTrust : ils ne sont traités que si les fichiers sont présents. Lire `CLAUDE.md`.

### Tâche
1. Télécharger le jeu depuis le dépôt UCI : chercher « ElectricityLoadDiagrams20112014 » sur archive.ics.uci.edu et consigner l'URL exacte. Agréger au pas quotidien ; prendre la log-différence de la charge quotidienne par client. Dans un worktree, exposer `data/raw/electricity` par un lien absolu (`CLAUDE.md`).
2. Désaisonnaliser (jour de semaine, saison annuelle) sur un segment d'apprentissage. Tester la symétrie centrale (prompt 11) ; si elle est rejetée, utiliser des flux recentrés sur q̂.
3. Construire des fonds D6 et des injections F1–F2.
4. Pipelines : P2-C, P3-C, et P5-C si un CA-T-JEPA est entraîné sur ce domaine (sans caractéristiques).
5. Mesurer G_ADD (lecture γ_H = H/α) et le FPR.
6. Si `data/raw/swat` ou `data/raw/wadi` existent, appliquer le même protocole ; sinon, consigner l'absence.

### Entrées
Internet (UCI) ; prompts 5 et 7 (et 14) ; `CLAUDE.md`.

### Livrables
`jepadrift/data_loader/electricity.py`, `experiments/e11_sensors.py`, `results/e11/e11_cells.csv`, `figures/e11/*`.

### Contraintes techniques
Données brutes ignorées par git ; graines fixées.

### Critères de succès
Panel de 370 séries construit ; FPR dans l'IC ; G_ADD avec IC ; écarts consignés.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.electricity --build
python experiments/e11_sensors.py --quick --out results/e11_quick
```
````

**[Strategic Advice]**

- **Conformité au tour.** Aucun code d'implémentation n'a été écrit. Les seules commandes exécutées sont en lecture seule :
  - clonage et lecture du dépôt de l'Article B ;
  - lecture de la documentation de Claude Code.

  La mémoire chargée par `CLAUDE.md` est décrite à https://code.claude.com/docs/en/memory.
- **Écart au gabarit.** Le gabarit plafonnait à 7 prompts ; ton instruction de couvrir tous les streams l'emporte. Sa définition du plancher et du flux de signe est corrigée dans `CLAUDE.md`.
- **Prompts à relire avant lancement.**
  - Les prompts 1 à 13 sont exécutables tout de suite.
  - Les prompts 14 à 28 dépendent de sorties non encore produites et sont à relire après J2 et J3.
  - Si J2 déclenche la contingence C1, E6 passe avant E5 et les familles F1–F2 deviennent secondaires.
- **Corrections du plan v4 à reporter.**
  - Tableau 2 : P1-C et P2-C surveillent un flux d'étiquettes, pas un Hoeffding Tree.
  - J2 : remplacer 4,29 % et 5,03 % par les niveaux calculés par `lattice.py`. Le registre de l'Article B donne 4,34 % et 5,10 % à H = 5 000.
  - Phrase du §1 sur « 66 phases Pagan–Sossounov » : la datation de SPY est de Lunde–Timmermann.
  - Interface Z : float64 au lieu de f32.
- **Identifiants non vérifiés**, que les prompts demandent à Claude Code de contrôler :
  - identifiant Kaggle et licence de BAF ;
  - URL UCI d'Electricity ;
  - existence d'un dépôt officiel de T-JEPA ;
  - présence de la liste des 239 titres dans le dépôt CD-DFM ;
  - référence de Kuncheva (2013) pour SPLL ;
  - formule du test des triplets.
- **Environnements.**
  - Le hash de référence d'E2 suppose numpy 2.4.4.
  - Les contrôles d'identité de l'Article B supposent ses versions épinglées (numpy 1.26.4, scipy 1.16.2). Le prompt 4 prévoit donc deux environnements.
  - Un écart d'ajustement SLSQP entre versions de scipy est plausible ; il faut le documenter, pas le corriger.
- **Fuite de la fenêtre de test.** E1, E3, E4 et l'audit sont bornés à 2005–2019 jusqu'au gel J4. Cela repousse en S5 tout chiffre du §2 calculé sur 2020–2025, comme prévu par la grille finale du plan.
- **Calendrier de J1.** Le prompt 1 doit tourner avant dimanche ; il prend environ 75 secondes de calcul. Le prompt 2 conditionne les prompts 4 à 7 et devrait suivre dans la journée.

## PROMPT 8b — Hygiène avant la vague E1/E3/JEPA : modules partagés, fixture sans effet de bord, registre des écarts

### Contexte
JEPA-Drift (« Article C ») entre dans sa vague la plus parallèle : E1, E3, CA-T-JEPA et IPCA vont tourner en même temps dans des worktrees distincts. Trois briques qu'ils partagent n'existent qu'en copies locales : le pivot des caractéristiques, le débiaisage et le bootstrap de l'audit, et le placebo de phases. Par ailleurs, le fixture de `tests/test_data_d1_d2.py` réécrit des fichiers suivis à chaque `make check`. Ce stream court factorise ces briques avant le lancement de la vague. Lire `CLAUDE.md`.

### Tâche
1. **Pivot des caractéristiques** `jepadrift/data_loader/chars.py` :
   - `load_chars_tensor(dataset, rows=None) -> (C, names)` : C est un tableau float64 (T, N, P), aligné sur `ret_wide.npy`, `dates.npy` et `assets.json` du jeu (`d3_239`, `d3_500`, `d4_eurofidai` si construit). Les NaN sont conservés et l'ordre des colonnes suit `chars.parquet` ;
   - `impute_zero(C) -> (C0, n_imputed)` : remplace les NaN par 0 et en rend le compte (convention de `injection.inject`, `C-inject-F2-nan`) ;
   - pour `d2_us97`, lever `ValueError("D2 has no characteristics")` ;
   - tests `tests/test_chars.py` :
     - alignement exact sur 50 couples (date, titre) tirés avec graine, comparés à `chars.parquet` ;
     - formes attendues ; NaN conservés ;
     - égalité au bit près avec le pivot local de `tests/test_injection.py` sur la calib de `d3_239`.
2. **Statistiques de dérive partagées** `jepadrift/stats/drift.py`.
   - Déplacer sans modifier leur corps, depuis `experiments/audit_information.py` : `debiased_sr2`, `mbb_indices`, `_ci` (exporté sous le nom `shifted_percentile_ci`), `transitions` et `rotate_phases`.
   - L'audit les importe désormais et réexporte les anciens noms, de sorte que `tests/test_audit.py` reste inchangé.
   - Non-régression : `python experiments/audit_information.py --datasets d2_us97 d3_239 --quick` donne des CSV identiques au SHA-256 avant et après le déplacement.
3. **Lecture à horizon** dans `jepadrift/pipelines.py` :
   - ajouter `horizon_gamma(H, alpha=0.05) -> float`, égal à H/α ;
   - sa docstring cite la borne P∞(alarme avant H) ≤ H/γ ;
   - ajouter un test.
4. **Fixture sans effet de bord** (`tests/test_data_d1_d2.py`).
   - Le fixture de session reconstruit D1 et D2 sous une racine temporaire qui reproduit l'arborescence du dépôt. Il passe par un monkeypatch de `REPO_ROOT` et des chemins dérivés de `jepadrift.data_loader.articleB`, lus à l'appel.
   - Les tests comparent les SHA-256 des fichiers reconstruits à ceux des fichiers commités. Ils comparent aussi les entrées D1/D2 du manifeste reconstruit (jeux `d1_etf4` et `d2_us97`, résultat `d1_d2_profile`, source) à celles du manifeste commité.
   - Dans `.gitignore`, ignorer les nœuds `.venv` et `external` aussi lorsqu'ils sont des liens symboliques de worktree (les motifs actuels avec `/` final ne les couvrent pas). Vérifier `git check-ignore .venv external` dans un worktree, sans masquer d'autres modifications suivies.
   - Après `make check` sur un arbre propre, `git status --porcelain` doit être vide.
   - Dans `CLAUDE.md` (« Worktrees and parallel streams »), supprimer la phrase sur la réécriture des fichiers D1/D2 par le fixture.
5. **Fidélité des prompts** `tools/check_prompts.py`, avec une cible `make prompts-check`.
   - Mode par défaut : vérifier que chaque `prompts/streams/prompt-*.md` est une sous-chaîne exacte de `prompts/Prompts_Claude_Code_v5.md`.
   - `--sync-master` : remplacer dans le master chaque bloc de prompt (repéré par son titre `## PROMPT <id> —`) par le contenu du fichier de stream ; ajouter les blocs absents en fin de section 4.
   - Exécuter `--sync-master` (idempotent : le master est synchronisé depuis les fichiers stream), puis `make prompts-check` : 29/29.
6. **Registre des écarts** (`docs/DEVIATIONS.md`, en français, en fin de fichier) : ajouter verbatim les deux entrées du bloc ci-dessous.
7. **`CLAUDE.md`** (mémoire canonique ; `AGENTS.md` en est le lien symbolique) :
   - ajouter `chars` à la liste de `data_loader/` et `drift` à celle de `stats/` dans la puce `jepadrift/` du « Repository layout » ;
   - ajouter `check_prompts.py` à la puce `tools/`.

```markdown
## C-D3-survivor-correction — biais de survie de D3 (2026-10-18)

Correction de `C-D3-survivor`. Un univers formé des constituants actuels du S&P 500, projeté en
arrière jusqu'en 2000, est biaisé par la survie : un titre n'y figure que parce qu'il a survécu et a
rejoint l'indice. `d3_239` (les 239 plus longs historiques parmi ces constituants, `C-D3-no239`) l'est
doublement. Portée : les expériences sur fonds symétrisés D6 avec dérives injectées en dépendent peu ;
les mesures sur données brutes (recensement, E8, placebos) héritent du biais et servent d'appui, jamais
de preuve de détectabilité. Aucune donnée n'est modifiée.

## C-D4-survivor — sélection de D4 (2026-10-18)

D4 contient 498 titres EUROFIDAI retenus pour au moins 5 000 observations entre 2001 et 2026 (places
AMS, BRU, EPA, LSE, MIL, XET). Cette sélection sur la longueur d'historique est une sélection par la
survie ; l'export ne fournit ni date de radiation ni statut (radiations inférées par l'absence de
données), et MIL n'a pas de données pour 2024–2026. `in_universe` couvre 91 % des cellules : les
appelants choisissent des sous-panels complets sur leur fenêtre (`inject` exige un panel fini). D4 n'a
pas de secteur GICS : F2 n'y utilise que les quatre caractéristiques continues.
```

### Entrées
`experiments/audit_information.py`, `tests/test_injection.py` (pivot local), `jepadrift/data_loader/{articleB,sp500,eurofidai}.py`, `prompts/streams/`, `prompts/Prompts_Claude_Code_v5.md` ; `CLAUDE.md`.

### Livrables
- Code : `jepadrift/data_loader/chars.py`, `jepadrift/stats/drift.py`, `horizon_gamma` dans `jepadrift/pipelines.py`, `tools/check_prompts.py`.
- Tests : `tests/test_chars.py`, `tests/test_drift_stats.py`, fixture révisé de `tests/test_data_d1_d2.py`.
- Configuration : cible `prompts-check` du `Makefile`, master resynchronisé, `.gitignore` adapté aux liens de worktree, entrées de `docs/DEVIATIONS.md`, `CLAUDE.md` mis à jour.

### Contraintes techniques
- Déplacements sans modification de corps, contrôlés par `ast` sur les segments.
- Aucun changement de sortie de l'audit.
- `jepadrift/monitors/` reste inchangé ; numpy et pandas seulement.
- `make check` reste sous 5 minutes.

### Critères de succès
- Audit `--quick` identique au SHA-256.
- `tests/test_audit.py`, `tests/test_chars.py` et `tests/test_drift_stats.py` au vert.
- `git status --porcelain` vide après `make check` sur un arbre propre.
- `make prompts-check` : 29/29.
- Écarts et mise à jour de `CLAUDE.md` commités.

### Commandes de vérification
```bash
python experiments/audit_information.py --datasets d2_us97 d3_239 --quick --out /tmp/audit_q && sha256sum /tmp/audit_q/*.csv
pytest -q tests/test_chars.py tests/test_drift_stats.py tests/test_audit.py
make check && git status --porcelain
make prompts-check
```

````markdown
## PROMPT 28-PCA — PCA drift benchmark runner: data, selection, calibration, evaluation

**ROLE**: critical Claude Code implementation agent, supervised by Codex. **Implement only in your assigned isolated worktree after the read-only plan is approved**. Target: `experiments/pca_drift_benchmark.py`. Read `AGENTS.md`, `docs/DEVIATIONS.md`, `prompts/Protocole Codex.md` if found, the local PCA/monitor implementations, dataset manifests and `12_CODEX_AMORCAGE_PCA_EXPERIMENTS_2026_10_30.md`. The mission text `11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md` is the experimental request; scientific corrections in the kickoff are mandatory. Do not assume files, commands, versions or datasets exist without checking them.

### 1. Deliverable and boundaries

Build a deterministic CLI benchmark for **PCA spectral prefixes versus information-selected subsets** on mean and covariance changes, with an independent train/calibration/test separation. Preserve existing outputs and never rewrite the historical E2 CRLF file; do not rerun merged research streams. No code in other agents' ownership; publish an audited immutable data/output schema. Include docstrings and command help in English. Support `--config`, `--output-dir`, `--seed`, `--mode smoke|full`, `--dataset synthetic|real|both`, `--resume` with completed-partition fingerprint checking; if the repository has an established CLI convention, align to it and document the adjustment.

### 2. Existing components to inspect/reuse

- `jepadrift/representations/pca.py`: `PCAOrthogonal`, `pca_directions`, `mp_count`, Ledoit–Wolf fit and frozen projection; infer output structure, `channels={market:[0],residual:[...]}`; **do not accidentally remove PC1 from all mean comparisons**.
- `jepadrift/monitors/eprocess.py` plus current sequential monitors: inspect dimensional assumptions before reuse. Exact sign symmetry and the isotropic sub-Gaussian mixture are **not** guaranteed for correlated Student returns.
- Real data and time splitter: inspect `jepadrift/data_loader`, `data/derived/d3_239/`, `MANIFEST.json`, selection hash and feature timestamps. Never invent observation counts.
- Existing covariance/mean injection utilities, if any: reuse with deterministic seed IDs; do not silently recalculate past reported experiments.

At the start produce in the plan a file-level call graph and a coverage matrix of **mean Gaussian, mean Student, covariance Student, real retrospective** versus eligible detector families. Any missing case is labeled `UNSUPPORTED` with reason.

### 3. Inputs and exact models

Global constants (configurable but defaults fixed): `N=239`, `H=250`, `nmax=20`, `FPR_target=0.05`, `n_calibration=2000`, `n_test_null=2000`, `n_test_alt=2000`, `gamma=504` **only for analytic M-score**, and deterministic root seed. Set `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1` before NumPy import, or fail with a clear diagnostics if violated. Persist dtypes (`float64`) and version and seed manifests. Do not convert missing data to zeros silently.

**Synthetic model**: independently generate a PCA-fit sample of `T_fit=1000` trading days and independent calibration/test trajectory sets; each sample has 239 assets. Define an explicit single-factor common-correlation covariance `Σ0=(1−ρ)I+ρ·11^T`, `ρ=0.40`, with unit variances; generate standardized Student-t innovations with `ν=7`, rescaling for unit variance; record whether the common factor and idiosyncratic factors use independent t variables. Include **Gaussian synthetic control** with the same covariance to validate exact Gaussian formulas before using Student-t pseudo-information. Fit PCA to fit-only data, never refit on null test or alternatives.

Synthetic alternatives must operate on return vectors **before frozen PCA**:
- `A_market_mean`: `Δ || v1`, annualized SR=4 **of the standardized projected market score**; define resulting daily standardized shift `4/sqrt(252)` and write exact Δ in the manifest; under Gaussian control `I=SR²/504` per day.
- `B_cov_rotate30`: create `Σ1=R_{12}(30°)Σ0R_{12}^T(30°)` with `R` rotating the two empirical frozen PCA axes (or document population-eigenbasis alternative as distinct scenario). Record angles **15°, 30°, 45°** when the sweep is requested, with 30° primary. The rotation creates **off-diagonal** covariance in the fixed PC basis. Compute `Σ0,S`, `Σ1,S` and joint Gaussian proxy `I_cov(S) = 0.5[tr(Σ0,S^{-1}Σ1,S)−logdet(Σ0,S^{-1}Σ1,S)−|S|]`. Also report the per-axis marginal proxies `q_k^cov=0.5(r_k−1−log r_k)`, `r_k=Var1(z_k)/Var0(z_k)`, but **never sum them as actual joint KL**. In t7 model label them gaussian covariance proxies, not true t7 KL. Include a unit test that explicitly witnesses joint≠sum marginals.
- `C_residual_mean`: Δ orthogonal to PC1 and supported on frozen axes numbered 10..20 inclusive, normalized so `0.5·Δ^TΣ0^{-1}Δ=3.0` nats/day on the relevant Gaussian reference; record reproducible weights and inverse covariance used. If a sample covariance rather than population covariance defines the constraint, make that precise and separate the corresponding achieved theoretical value.

**Real data**: 239 asset S&P panel, fit Ledoit–Wolf PCA **only on actual documented 2016-04-07..2019-12-31 calibration segment (941 valid daily complete rows when manifest confirms)**; train period 2005–2015 is **not** a PCA fit. Monitoring starts after the actual 65 trading-session embargo. Record panel composition/survivorship limitations. **Two mandatory and incompatible historical cohorts** (both with covariance/whitening/thresholds frozen no later than 2019-12-31):
  - `cohort_standard_embargo`: preserve the 65-trading-day embargo after 2020-01-01, and emit a Covid row `NOT_EVALUABLE_STANDARD_SPLIT` (no spurious 0 or imputed missing RMST). This is the only cohort eligible for standard split claims.
  - `cohort_retrospective_covid`: **explicit separate retrospective exploratory deviation** recorded in manifest/issues and, subject to Codex approval, in `docs/DEVIATIONS.md`; monitor continuously from the first actual session `2020-01-02` with no post-2019 embargo, event onset `2020-02-24`, event end `2020-03-23`. Check all dates against the loaded market calendar rather than use a fixed observation count. This cohort is `REAL_RETROSPECTIVE_EXPLORATORY`, never `MAIN_TEST_VALID` or independent confirmation. No observations from 2020 onward may affect PCA fit, selection of ex-ante axes, null thresholds or detector parameters. Define pre-onset false-alarm and reset handling **before** computing detection: continuous monitoring carries its statistic from January into February; a preceding alarm is `PRE_ONSET_ALARM`, not silently erased. Report (i) first qualifying alarm **within** `[2020-02-24,2020-03-23]` and event-window censoring; (ii) separately, a `H=250` post-onset restricted delay if the path supports it, clearly labeling an alarm after 2020-03-23 as **post-event**. Never relabel a historical crash as a stationary enduring Gaussian mean shift. The 2022-01..2022-06 style rotation is retrospective, with exact observable sample days, no invented independent 2000 crises. Both real cohorts must carry unique `cohort_id`, `split_hash`, `event_window_id`, `status`, and `null_calibration_id` through all outputs; never reuse the cohort-standard metric or calibration IDs for the no-embargo cohort unless the configuration fingerprint proves the parameters and null reference are identically frozen. Event-difference Δ estimated with post-event returns is an **ex-post oracle diagnostic only**, never an ex-ante selection rule. If no manifest/series is available, report `DATA_UNAVAILABLE`; do not simulate and label real.

**Ex-ante selector:** build stress-library `qbar_k` only from predefined historical 2008/2011 windows and the 239 identities, using information observable by end-2019. PCA basis learned 2016–2019 may project older history, but never uses 2020/2022 event data to select. Stress events, window endpoints, missing-asset policy and weights must be frozen in config before evaluation. Missing coverage => no ex-ante result, issue row rather than hindsight backfill.

### 4. Spectral baselines, candidate sets, information

- Fit `Σ_LW` with repository function on PCA-fit data; `λ1≥…≥λN>0`, ordered signed eigenvectors; persist basis hash, whitening scales and trace.
- Prefix candidates `P_k={1,…,k}`, for **every** k=1..20; use same exact frozen eigenvectors, not rerun PCA per k. Compute `CPV_k = Σ_{j≤k}λ_j / tr Σ_LW`; record actual CPV and actual first k reaching 90% **over full spectrum**. If first 20 never reaches 90%, report `CPV90_OUTSIDE_TOP20`, do not insert `k=14` or pretend it is the CPV baseline within the restricted experiment.
- Marčenko–Pastur cutoff computed from sample **correlation** eigenvalues at `(1+sqrt(N/Tfit))²`, not from `Σ_LW`; Kaiser `corr_eig>=1` and only meaningful in the correlation scale. These count markers are descriptive and must not be hardcoded.
- For **mean Gaussian**, `q_k=(v_k^TΔ)^2/(2λ_k)` is additive only where the PCA basis diagonalizes the chosen reference covariance; detect/sample-vs-population mismatch, and either compute joint subspace KL or label sum a **surrogate**. Build top-q oracle subsets over `P_k` for all k; tie-break by ascending axis index; evaluate every cardinality d=1..k against `V(S)=I(S)/M(d,γ)`. The analytic `M` is the **Gaussian mean-mixture fluid multiplier**: solve `x=A+d/2*log(1+2x/d)`, `A=logγ`, `M=x/A`, with a reliable bracketing root solver and assertions for uniqueness/positivity. Never call it an exact ADD/finite-ARL cost.
- For covariance B, compute **joint subspace covariance Gaussian KL proxy** for each candidate S; its contribution is generally **not additive**. Provide a predeclared covariance selector (e.g. exhaustive only for small k, documented beam search otherwise), store `selection_exact=False` where approximate. Never claim oracle top-marginal-q is the joint optimum. The user's `q_k^cov` ranking may be reported in an **ablation diagnostic** but cannot inherit mean-oracle contracts.
- Ex-ante `qbar` greedy ranks an independently frozen stress-library information estimate. It cannot equal real-event oracle by design. All selectors restricted to axes 1..20 in experiment 3. For mean case, define `forward greedy` precisely as sorting/addition by fixed marginal qbar and evaluating **every** size, not early stopping on a local decline in score.
- Cost-affine oracle `C(d)=a+c d`, with `a,c>0` fixed before evaluation, separately labeled `AFFINE_SURROGATE`, not the mixture cost. Choose a/c in config with documented rationale; do not silently substitute the obsolete heuristic or relabel as a theorem.

### 5. Detector and calibration protocol — precise separation

**Critical:** `V(S)` is a selection **surrogate**. Actual empirical RMST must be measured by a **fully specified detector** with separate null calibration. In the implementation plan explicitly select which of the repository's detectors are usable, their predictive statistics, update equations and their null-validity domain.

Recommended families if existing code is insufficient:
1. **MANDATORY `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM` — no GLR fallback, no truncation of change-start candidates**. For selected whitened vectors `z_t in R^d`, prefix sums `S_0=0`, `S_t=sum_{i=1}^t z_i`, candidates `tau in {1,...,t}`, segment length `n=t-tau+1`, and segment sum `D_{tau:t}=S_t-S_{tau-1}`, compute **exactly (for the specified Gaussian-mixture statistic)**:

   ```text
   logL(tau,t) = -(d/2)*log1p(n*s2)
                 + s2*||D(tau:t)||_2^2 / [2*(1+n*s2)]
   W_t = max_{tau=1,...,t} logL(tau,t)
   T_h = inf{t>=1: W_t >= h}
   ```

   Use a **predeclared** positive prior variance `s2` for every eligible method, based exclusively on training / independent calibration; never tune `s2` from the test injection `Delta` except in a separately marked `ORACLE_PRIOR_SCALE` ablation. The theoretical `M(d,gamma)` uses an **alternative-matched** scale and is therefore only a model-based selector surrogate, not this scan-CUSUM's exact calibrated expected delay. Cache 0-based prefix sums with the correct tau-1 subtraction, and compute all `tau` candidates with stable vectorized NumPy operations (`log1p`, squared norms, deterministic tie handling). Complexity `O(t*d)` per step, `O(H^2*d)` over a horizon `H`, `O(H*d)` prefix storage for one evaluated subset; use bounded memory minibatches/shared prefixes for the 2,000-replicate and k=1..20 grid. The computational burden is not a license to replace the detector. If full mode exceeds an explicitly audited execution/resource budget, report `BLOCKED_RESOURCE` after a verified smoke run; do **not** silently switch to a windowed GLR.

   Distinguish this **scan/max over segment-mixture likelihoods** from the classical scalar additive CUSUM recursion; there is no claimed O(1) update for this statistic. Under an exact joint Gaussian null and correct fixed whitening it is constructed from valid likelihood-ratio e-process segments; under correlated/heavy-tailed Student t7 or imperfect historical whitening the same formula is a **quasi-likelihood**, without an unconditional e-process guarantee. For all experiment metrics, independently calibrate the threshold `h` to `FPR(250)<=0.05` and measure holdout FPR; never set `h=log(gamma)` merely because `gamma=504` was used for the analytic `M` score. The independent-null calibration and equal detector family are mandatory for all `k` and subsets. A known-Delta Gaussian LR detector is permitted **only** as an explicitly separate oracle diagnostic, never as the common comparator.
2. `COV_QUADRATIC_CUSUM`: calibrated quadratic covariance-change statistic sensitive to up/down and off-diagonal shifts; require explicit null/alternative matrices for any oracle version; no future Σ1 in an ex-ante detector. Include `ENERGY_INCREASE_CUSUM` separately as historical comparator to reveal its blind spots. **Do not reuse mean-mixture M as the justified covariance cost**; show it only as a clearly marked heuristic sensitivity analysis, or `NA` in covariance main table.

For each dataset/scenario/family/selected S, calibrate a threshold via **independent null trajectories** (`n=2000`, horizon 250), using maxima over the trajectory and a deterministic quantile/tie rule; report calibration fraction and independent holdout null FPR with binomial uncertainty. Target is `P0(T≤250)≤0.05`; do not force observed FPR to exactly 5%. Selectors are frozen before calibration test. **Pair data**: all methods and subsets for a replicate use the same generated return trajectory, injected Δ/Σ1, onset and seed. Save sample-level first-hit indices and censoring. Evaluate alternatives from a documented time origin (onset-aligned vs continuous pre-onset); do not silently conflate. `T=∞` if no alarm by 250, `RMST250=mean(min(T,250))`, plus detection fraction. For real history, do not claim a valid FPR for 2020/2022 without explicitly defining independent historical null windows and their limitations.

### 6. Reproducibility and artifacts (authoritative producer)

Write `results/pca_drift_benchmark/{manifest.json,spectra.csv,selection.csv,calibration.csv,trials.parquet,aggregates.csv,issues.csv}` or an exactly equivalent **schema approved in PLAN.md**. Include methods `BASELINE_PREFIX`, `ORACLE_Q_AFFINE`, `ORACLE_Q_MIX`, `EXANTE_QBAR` and, for covariance, explicit `COV_JOINT_ORACLE` / `COV_MARGINAL_DIAGNOSTIC` labels; every row includes `source_kind`, `cohort_id`, `split_hash`, `event_window_id`, `event_id`, `detector_family`, `k`, `S` (sorted JSON list, 1-based), `d`, `objective_kind`, `metric_id`, `config_hash`, `basis_hash`, `calibration_hash`, `null_calibration_id`, `seed`, `status`. Store numeric `FPR`, `RMST250`, n, confidence interval and censoring as computed, not as copy/pasted target values. All `metric_id` are unique to a true common trial group and deterministic on rerun. Do not write synthetic or computed quantities to fields named observed real KL.

**Experiment 1:** prefix rows k=1..20 per admissible dataset/scenario/detector. **Experiment 2:** same prefix **references exactly the same metrics/IDs and values** as experiment 1, plus oracle subset per P_k. **Experiment 3:** per event, baseline CPV90 (if eligible), affine oracle, mixture oracle and ex-ante; all candidate axes limited to 1..20. `ORACLE_Q_MIX` at k=20 must reuse the exact experiment 2 selection and metric ID, never re-evaluate and compare floats. Covariance additive-oracle column is diagnostic only, not presented as a joint oracle.

### 7. Required executable checks and handoff

- Smoke tests run without proprietary files; full mode requires actual datasets (and correctly fails or marks real rows blocked if unavailable).
- Determinism: same config/seed/inputs => identical rows and fingerprint; track source/checksums, RNG stream hierarchy, scalar vs batch equivalence, non-NaN, positive eigenvalues, calibrated null/test separation, no future leakage, honest missing data.
- Negative tests: rotation joint KL differs from sum of marginal KL; Student pseudo-info is not labeled true KL; Covid blocked in **standard** cohort and visible as **exploratory** in separate no-embargo cohort only; scan-CUSUM exact prefix-sum formula vs direct slow reference on short streams; Student null lacks a claimed anytime validity; `CPV90_OUTSIDE_TOP20` does not crash; raw covariance `lambda<1` not miscalled Kaiser; no predefined figure outcomes.
- Preserve historical `results/e2/e2_cells.csv` including CRLF and SHA; do not mutate `docs/DEVIATIONS.md` to erase prior failures. Tests of cross-table identity are owned by stream 31, but provide stable fingerprints and selectors for that stream.
- Run available non-regression checks in your worktree; log commands, results, sources, remaining unsupported cases. Produce a concise schema/reference handoff for streams 29/30/31. Commit only after protocol-mandated wrapup/check; Codex alone arbitrates integration.
````

````markdown
## PROMPT 29 — Three reproducible PCA benchmark tables (CSV and Markdown)

**ROLE**: Claude Code stream responsible exclusively for table assembly/formatting in an isolated worktree; Codex must approve the read-only plan first. Target `experiments/pca_drift_tables.py`. Read `11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md` §3, stream 28 schema handoff, kickoff scientific corrections, `AGENTS.md` and repository conventions. **Never simulate observations, refit PCA, calibrate thresholds, or recompute a detector here.** All scientific data must come from the runner's immutable outputs.

### 1. Inputs / outputs

CLI: `--input-dir results/pca_drift_benchmark`, `--output-dir results/pca_drift_benchmark/tables`, optional `--dataset`, `--scenario`, `--detector-family`, `--format csv|md|both`, and `--strict`. Validate `manifest.json`, `spectra.csv`, `selection.csv`, `aggregates.csv`, `calibration.csv`, `issues.csv` (or the exact signed schema from stream 28). Match on stable keys (`dataset_id`, `cohort_id`, `split_hash`, `event_window_id`, `event_id`, `null_id`, `detector_family`, `k`, `selection_id`, `metric_id`, `config_hash`, `basis_hash`, `calibration_hash`, `null_calibration_id`, `seed`). Reject duplicate metric keys and stale schema/fingerprint; never join only on k.

Write `Tableau_PCA_1.csv/.md`, `Tableau_PCA_2.csv/.md`, `Tableau_PCA_3.csv/.md` plus `TABLES_VALIDATION.md`, `table_manifest.json`, and optional `tables_long.parquet`. Numeric files UTF-8 and machine-readable, displayed decimals separate from unrounded source values. Source provenance and footnotes are **part of the result**, not cosmetic.

### 2. Tableau_PCA_1 — spectral variance baseline (k=1..20)

Per valid scenario/detector family, exactly 20 rows in ascending k or explicit `BLOCKED/NA` status. Schema/output columns (preserve French titles in Markdown):

1. `Indice k` (1..20);
2. `Valeur propre λ_k` from **Ledoit–Wolf covariance**, never eigenvalue from correlation disguised as covariance;
3. `Variance cumulée CPV_k (%)` from `Σ_{j≤k}λ_j/Σ_{j≤N}λ_j` on the same fit split;
4. `Critères standard` indicating MP count (**calculated on sample correlation**), 90% CPV when reached, Kaiser applicable only to correlation `λ>=1`, or `—`; do not print `Kaiser λ<1` as selection convention;
5. `RMST250 préfixe (jours)` measured from **actual first-alarm times**, not inferred from analytic V;
6. `Dimension retenue` = k for the prefix;
7. `FPR250 hors dérive` from **independent evaluation null** (never hardcode 5%);
8. `n_cal / n_eval / n_alt`, `detector_family`, `status`, `metric_id`, `CI`, `source_kind` (extra provenance columns or footnote).

The source table example's `k=14, CPV=90.2%`, sample λ, RMST and FPR numbers are **placeholders, not findings**. For a 239-dimensional equicorrelated covariance with ρ=0.4, even the *population* CPV of the first 14 eigenvalues is only `(96.2+13×0.6)/239≈43.5%`; do not force 90% at k=14. Calculate actual `k90_full` over all N. When `k90_full>20`, annotate `CPV90_OUTSIDE_TOP20`, with no fake baseline. If data unavailable or split invalid, use `NA` + explicit reason.

### 3. Tableau_PCA_2 — prefix versus selected subset within P_k

At each k, show the **same prefix** as Tableau 1 plus the best subset S*_k selected from axes 1..k under the declared objective. Required columns:

- `Indice PCA k`, `Variance λ_k (H0)`, `Information marginale q_k` **with information type** (`MEAN_GAUSSIAN_EXACT`, `MEAN_GAUSSIAN_PROXY`, `COV_GAUSSIAN_MARGINAL_PROXY`);
- `Score préfixe V(P_k)`, `RMST250 préfixe`;
- `Sous-ensemble optimal S*_k` serialized deterministically as 1-based sorted axis IDs, `Score V(S*_k)`, `RMST250 sélection`, `Dimension optimale d*_k`, `FPR250 préfixe`, `FPR250 sélection`;
- `metric_id_prefix`, `metric_id_subset`, `selector_kind`, `selection_exact`, `status`, `CI`, `dataset_id`, `event_id`, `detector_family`.

**Identity invariant**: matching `cohort_id`, `split_hash`, detector, null cohort and evaluation horizon are prerequisites. Prefix RMST/FPR and their `metric_id_prefix` are **retrieved as exact values from the corresponding Tableau 1 aggregate**, never recomputed, rounded then compared, or resimulated. The requested bitwise identity is attainable only by referencing the same source metric object/bytes.

**Mean shift**: for diagonal Gaussian reference in the fixed PCA basis, `I(S)=Σq_j`; at each k, optimal additive selection is top-`d` q by descending value for every d=1..k, then maximize `I(S_d)/M(d,γ)` with deterministic tie rules. Never stop before evaluating every d. If Student background, mark `q` and `V` as **Gaussian-model proxies**, even while empirical RMST is genuine.

**Covariance rotation**: report marginal `q_k^cov` for diagnostic only. A rotated alternative is not diagonal in fixed PCA coordinates; `Σ marginal KL` is **not** `I_cov_joint(S)`. The primary covariance selection uses runner-provided joint covariance Gaussian proxy and a declared approximate/exact subset search; mark `selection_exact` honestly. `M(d,γ)` is a mean-mixture fluid cost and **not theoretically validated as covariance-delay penalty**. Therefore either (a) present covariance `V=I_cov_joint/M` only as `COV_HEURISTIC_SURROGATE`, with explicit warning, or (b) print `NA` for theoretical V, alongside empirical covariance RMST. Do not call the marginal-q ranking the covariance oracle. Keep mean and covariance outputs in separate named blocks/files if necessary.

### 4. Tableau_PCA_3 — ablation and historical ex-ante selection

For each eligible scenario and **cohort_id**, show baseline CPV90, oracle q+affine surrogate, oracle q+Gaussian-mixture-fluid surrogate, ex-ante qbar greedy; in covariance add an explicitly marked joint-covariance-search diagnostic (do **not** conflate with additive oracle). Required user-facing core columns:

`Rupture testée | Pipeline & règle | Information I(S) / type | Coût M(d) / applicability | Score V(S) / meaning | RMST250 (jours) | Dimension retenue d* | FPR250`.

Append `n`, CI, detection rate, censoring, event window, oracle status, calibration ID, basis hash, selection axes, `metric_id`, `status` and footnotes. `d*` is printed after RMST and before FPR, as requested.

- Mean rows: ensure **same** `S*` and `V*` as Exp 2 at k=20 for `ORACLE_Q_MIX`, and **same** RMST/metric_id from the exact cached trial aggregate; no rerun.
- Affine oracle: `C(d)=a+cd`, a,c fixed, distinct from Gaussian-mixture M.
- Ex-ante greedy: qbar from 2008/2011 historic stresses, independent of 2020/2022 tested events; do not call it oracle. Return information proxy and RMST only after valid test.
- CPV90: if global cutoff exceeds top20, mark `OUTSIDE_TOP20` and `not_comparable_under_common_candidate_universe`, optionally show real full-spectrum CPV90 only in a separate diagnostic, not as a competing 20-axis selection.
- **Both Covid cohort rows are mandatory and must be distinct**: `cohort_standard_embargo` (65-session post-2020 embargo; `NOT_EVALUABLE_STANDARD_SPLIT`, `RMST=NA`, `FPR=NA`) and `cohort_retrospective_covid` (no post-2019 embargo; monitor starts `2020-01-02`; `REAL_RETROSPECTIVE_EXPLORATORY`; onset `2020-02-24`, episode ends `2020-03-23`). Include `cohort_id`, split dates, whether the monitor was armed and its pre-onset alarm/reset policy, and event-specific status columns. Display `time_to_alarm_during_event`, `detected_during_event`, and separately `RMST250_post_onset` **only when well-defined**; alarms after 2020-03-23 cannot be described as detection during the acute event. Historical real episodes are single paths, not 2,000 independent replicates; do not publish pseudo-binomial confidence intervals or a stand-alone independent null-FPR estimate from the single Covid trajectory. Ex-post Δ = diagnostic oracle, forbidden as ex-ante input. The standard and retrospective rows cannot share the `metric_id` or silently merge.
- Real 2022: any q from observed 2022 shift is **EX_POST_ORACLE** and not an ex-ante stress predictor. On real data, theoretical Gaussian proxy is not true observed KL, and event windows are not 2000 independent alternate samples.

### 5. Display and audit requirements

- Real measured results must never be inferred from prefilled 4.8/4.9/5.0/5.1/5.2% examples, ideal `d=2`, `12 days`, or any other target picture. Targets and results always use distinct fields.
- Show `FPR_calibration` and `FPR_test_null` distinctly. If only a target exists, show target and `NOT_MEASURED` for achieved FPR.
- All numeric `V`, `q`, `M`, CPV, RMST from the same compatible assumptions / model; no comparison of a Gaussian mean `M` against a covariance experiment as though it were theoretically exact.
- Each Markdown table includes above it: dataset, N, fit/cal/test dates or synthetic lengths, distribution, injected change and amplitude, detector family and threshold calibration, H, n and selection provenance. Under it: status of covariance surrogates and any selection/censoring caveat. Add methodology/definition section **inside** tables document, not hidden in slide notes.
- Leave missing cells `NA`, not `0`, not `...`, and not prefilled illustrative numbers.
- The rendering code must handle wide tables via concise abbreviations plus a legend, not by silently dropping required fields. CSV retains full precision and all provenance fields.
- Generate a machine-readable lineage map: every displayed cell has a pointer to source file + row ID or formula + inputs. Document exact command to regenerate from immutable runner results.

### 6. Tests / acceptance

Assert (1) 20 prefix rows per eligible dataset/scenario; (2) CPV nondecreasing, `CPV_20<=1`; (3) table 1 vs table 2 RMST/FPR/metric_id identity **from same artifact**; (4) table 2 at k=20 vs table 3 oracle-mixture S, V and RMST identical on compatible **mean** scenarios; (5) covariance oracle cannot masquerade as additive-q theorem; (6) real 2020 embargo preserved; (7) no result from a missing trial or uncalibrated detector; (8) CSV and MD values round only at display time; (9) stable ordering and SHA/fingerprint on second run. Provide `TABLES_VALIDATION.md` with counters, skipped blocks, source hashes and errors. Follow isolated-worktree plan/implementation protocol, prompt synchronization, historical SHA and wrapup requirements. Codex decides integration.
````

````markdown
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
````

````markdown
## PROMPT 31 — PCA benchmark scientific invariants and pytest contracts

**ROLE:** independent Claude Code QA stream, isolated worktree, supervised and merged by Codex only. Target `tests/test_pca_drift_contracts.py`, plus minimal local test fixtures/helpers under `tests/` if absolutely necessary. First produce a read-only `PLAN.md` that reads the accepted runner and tables schema and all relevant project tests. Never change production experiment logic to make a test pass without Codex's explicit approval. Preserve historical `results/e2/e2_cells.csv` byte-for-byte. No `xfail`/`skip` to conceal a scientific contract violation; if a dataset-dependent test cannot run, mark it separately as unavailable, and keep all mathematical/unit tests runnable offline.

### 1. Mathematical unit tests (offline, deterministic)

**Mean Gaussian KL**:
- For SPD `Σ`, Δ, confirm `I_full=Δ^TΣ^{-1}Δ/2`.
- In **the actual eigenbasis of the same Σ**, verify `I_full = Σ_k(v_k^TΔ)^2/(2 λ_k)` to numeric tolerance dictated by floating-point precision. Verify subspace cumulative information is monotone **for a fixed Δ** and fixed nested basis. Demonstrate covariance eigenvalue order alone does not guarantee information marginal order; craft counterexamples where only first or last axis carries Δ.
- For `q_k>=0` and cost depending only on cardinality, compare **exhaustive subset enumeration** for small k (k≤12), sorted top-d q optimization and forward-add-largest-q with full cardinality scan; ensure same deterministic selected set and V, with explicit tie-breaking. Do not assert 'early-stop greed' equivalence without a unimodality theorem. Ex-ante qbar differs from true-oracle q unless they happen to coincide.

**Covariance rotation**:
- Construct `Σ0=diag(4,1)` and `Σ1=R(45°)Σ0R(45°)^T`. Compute `KL_joint = 0.5[tr(Σ0^-1Σ1)-logdet(Σ0^-1Σ1)-2] = 0.5625` in this Gaussian example; compare with `Σ_k 0.5(r_k−1−log r_k)≈0.3393`: they are **not equal**. Reject a table that labels their sum `TRUE_KL` or uses the mean oracle's additive optimum on this rotation.
- Verify `Σ1` SPD, nonzero off-diagonal in original eigenbasis, exact symmetry of covariance, and that an energy-increase-only statistic can decrease under a rotation despite positive joint KL.
- On Student-t synthetic data, assert information fields are `GAUSSIAN_PROXY`, never `EXACT_T_KL`.

**Fluid Gaussian-mixture analytic cost**:
- Solve `x=A+(d/2)log1p(2x/d)` with `A=logγ>0`. Verify unique positive solution numerically by monotone function, residual tolerance, `M=x/A>1`, and finite for d=1,4,20,500; with γ=504 check M(4) approximately 1.5696, M(500) approximately 9.6427 to sensible numeric precision. Never label it `EXACT_ADD`, `ARL0`, or `COV_EXACT_COST`.
- Check `V(S)=I(S)/M(|S|,γ)` is *a surrogate ranking* and does not equal measured RMST by definition.

**Covariance and selection**:
- Sample covariance nonnegative, Ledoit–Wolf SPD as required, eigenvectors orthonormal, projected test values equal stored transform from same fitted calibration data. Sample-correlation cutoff `λ_MP=(1+sqrt(N/T))²` counts factors on correlation, not LW covariance. Kaiser `corr_eigenvalue>=1`, not a universal `raw_cov_eigenvalue<1`. Test `CPV_k` monotonic with full-spectrum trace and `CPV_20<0.9` possible; in population equicorrelation N=239,ρ=.4 first14 CPV≈0.435146, *not* 0.902. The test must allow `CPV90_OUTSIDE_TOP20`.

**Exact mean Gaussian-mixture scan-CUSUM (required, no GLR fallback):**
- For short deterministic vectors (`d=1,2,4`, `H<=12`) compute the slow nested loops over all pairs `1<=tau<=t` and compare *every* `logL(tau,t)`, `W_t`, and first-alarm index to the vectorized-prefix implementation, with strict floating-point tolerance (not bitwise equality across different summation orders). Include paths with no alarm, immediate alarm, repeated equal maxima, and nonzero-prefix candidate starts.
- Require `S_0=0`, `S_t=sum_{i<=t}z_i`, segment `S_t-S_{tau-1}`, length `n=t-tau+1`, and `log1p(n*s2)` with a `s2>0` fixed before null test. Complexity instrumentation verifies all t candidate starts are considered, including starts before t-H only when a longer full-monitoring convention is declared. At H=250 full history is 250.
- Student-t7/null from empirical Ledoit–Wolf whitened vectors must not be stamped `EXACT_EPROCESS` or assumed to satisfy Gaussian mgf bounds; holdout null FPR is obligatory. Explicit test rejects `GLR_WINDOWED` as the declared mean primary detector, and rejects alternative-matched `s2` on non-oracle test arms.

### 2. Cross-experiment exact-reuse contracts

Use the **same immutable trial/aggregate** and identical `metric_id` (not recomputation) for prefix P_k in Experiments 1 and 2. For every supported `(dataset_id,event_id,detector_family,k,config_hash,basis_hash,calibration_hash)`:

```text
Tableau_PCA_1.RMST250(P_k) == Tableau_PCA_2.RMST250_prefix(P_k)
Tableau_PCA_1.FPR250(P_k)  == Tableau_PCA_2.FPR250_prefix(P_k)
Tableau_PCA_1.metric_id   == Tableau_PCA_2.metric_id_prefix
```

Equality must be exact at the **source serialized precision**, because both reference one value; do not invoke independent Monte Carlo for the same cell. Do not compare independently formatted rounded strings against full-precision floats and call that bitwise equality.

For each eligible **additive Gaussian mean-shift** scenario at reservoir k=20:

```text
S_star_experiment2_k20 == S_star_experiment3_oracle_mix
V_star_experiment2_k20 == V_star_experiment3_oracle_mix
metric_id_experiment2_k20 == metric_id_experiment3_oracle_mix
RMST250_experiment2_k20 == RMST250_experiment3_oracle_mix
```

Make negative tests that fail when subset array order differs, axis indexing is off by one, the selected set includes an axis beyond 20, a detector family differs, or FPR was borrowed from a different null. **Do not apply these equalities to covariance surrogate selectors** where additive optimality fails or to a retrospective oracle versus ex-ante qbar.

### 3. Time, leakage, and sampling contracts

- Synthetic fit, independent null-calibration, independent null-test and alternative test IDs are **disjoint**; thresholds do not consume holdout null/alternative data. Ensure root-seed child streams are unique and reproducible. Paired trajectories across candidate methods have identical returns, injection, onset and replicate ID.
- Test `H=250`, independent null FPR from holdout, `RMST250 = arithmetic mean(min(hit_time,250))`, and `detect_rate + censored_rate = 1` within tolerance. Test no double-counting of false alarms before a documented onset; origin must be explicit.
- Real split: PCA fitting/calibration 2016-04-07 to 2019-12-31 where data manifest confirms. Test **two disjoint cohort identifiers**: `cohort_standard_embargo` retains 65 trading days and requires Covid `NOT_EVALUABLE_STANDARD_SPLIT`, with unavailable metrics; `cohort_retrospective_covid` uses monitor start `2020-01-02` and retrospective event `[2020-02-24,2020-03-23]`, allows `REAL_RETROSPECTIVE_EXPLORATORY` **only**, with a documented no-embargo deviation. Inject a deliberate fake confirmatory status to ensure the test fails. Assert no 2020 data in PCA fit/null thresholds/ex-ante stress library, and no metric-ID collision across cohorts. Ensure earlier alarms before Feb 24 are not silently reset; an event-window hit is not equated with a hit later in the 250-day horizon. The 2022 event requires `RETROSPECTIVE` status for any ex-post shift estimate. Ex-ante stress-library entries must be historical 2008/2011 and free from 2020/2022 labels/returns.
- Train/validation/test samples must be label-safe and feature-safe; selection on the event's Δ is an **oracle** and any use to create ex-ante qbar is a hard failure. Simulated true covariance Σ1 is allowed only in an explicitly labeled oracle diagnostic.
- Real missing/embargoed data => `NA/BLOCKED`, never 0 RMST or 5% FPR. Sample size on real events is not artificially declared 2000 independent paths.

### 4. Reproducibility, provenance, integration

- Run a tiny deterministic **fixture** suite for both mean and covariance that avoids proprietary files. Reproduce outputs twice with same seed/config and compare normalized CSV bytes/fingerprints; variation due to timestamps must be excluded from reproducibility-critical hashes or documented separately.
- Table/figure schema tests: **both** `Figure_1_mean` and `Figure_1_cov` must be generated from measured upstream records; the latter has mandatory `COV_SURROGATE_EXPLORATORY` metadata and visual legend and cannot label summed marginal covariance KL as joint KL. Every figure point traces to one aggregate row and validated table ID; wrong/stale source hash fails; absent data yields gap/NA not fabricated interpolation. Ensure the figure code cannot hardcode `CPV90 at 14`, `d*=2`, `selected RMST~12`, or FPR=5% measured merely from target.
- Validate parser of axis lists, `1<=axis<=20`, unique axes, sorted stable representation, `d==len(S)`, no silent zero eigenvalues, NaN or negative information for valid Gaussian KL. If severe numerical near-zero negative Gaussian KL arises, allow documented machine-epsilon clipping only after validation; never silently sanitize material negatives.
- Historical invariant: `sha256sum results/e2/e2_cells.csv` equals `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` and the Git index blob hash obtained with `git show :results/e2/e2_cells.csv` hashes identically. Native CRLF must remain unchanged. `docs/DEVIATIONS.md` retains historical D8 FAIL +5.2833%; no newly 'passed' rerun of that case.
- **Canonical filename and parser contract:** exact new paths `prompts/streams/{28,29,30,31}_STREAM_PCA_DRIFT_*.md` beginning with unique `## PROMPT 28 —` through `## PROMPT 31 —`. The CURRENT `tools/check_prompts.py` discovers only `prompt-*.md`; merely renaming would cause silently vacuous pass. Under an explicitly approved tooling change (separate from application code, Codex supervises), update it to collect `prompt-*.md` **and** `[0-9][0-9]_STREAM_PCA_DRIFT_*.md`; validate unique PROMPT IDs, reject duplicate aliases, check expected 28–31 ID set and **exact bytes of each** in `prompts/Prompts_Claude_Code_v5.md` after `--sync-master`. Add regression test: if one canonical prompt is deleted or modified relative to master, `make prompts-check` must fail. Only report 100% sync after demonstrating all four were discovered. After integration run `python tools/check_prompts.py --sync-master` and `make prompts-check`. Run `make check`, then the new test file, report actual outputs and time/split manifest. Do not claim CI success without execution.

### 5. Deliverables and failure policy

Commit `tests/test_pca_drift_contracts.py`, associated fixtures only where needed, and `PCA_CONTRACTS_VALIDATION.md` listing tests run, pass/fail/blocked counts, actual hash verification, and scientific decisions. No re-run of archived streams, no fabrication of future metrics, no modifying application code directly within QA stream except after explicit Codex approval with a new contract. An expected failure from the original mission's invalid assumptions (additive covariance q, Covid event embargo, CPV90 at k14) is a **successful negative test** and must not be erased to make the suite green. Follow read-only planning, headless implementation, worktree isolation, prompt sync and approved wrapup/merge protocol.
````
