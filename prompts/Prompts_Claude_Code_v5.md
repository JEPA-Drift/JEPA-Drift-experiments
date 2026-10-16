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
  - Le prompt 1 écrit `AGENTS.md` à la racine du dépôt et crée le lien symbolique relatif `CLAUDE.md` -> `AGENTS.md`.
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
9. Commit local `lot1: floors, E2, section 3; J1 run`. Aucun `git push`.

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
  ignored and blocked by the pre-commit hook. No `git push` until the IP agreement (LUSIS CIFRE)
  is recorded.

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
4. **Garde-fous git.** `tools/pre-commit` lance `make check`. Il refuse tout fichier sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/`, tout fichier de plus de 50 Mo, et tout `git push` signalé par un hook `pre-push` qui échoue avec un message rappelant l'accord de propriété intellectuelle. Installer les hooks avec `make hooks`.
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
## PROMPT 12 — E1 : le problème sur données réelles (§2), pipelines 1 → 2 → 3 et critères de J2

### Contexte
E1 mesure ce que coûte la détection d'une dérive pour un actif seul (P1), pour le pooling de signes (P2) et pour la projection orthogonale au marché (P3), puis compare ces gains aux prévisions de l'audit. Il fournit les chiffres du §2 et deux des trois critères de J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **ADD** : délai moyen de détection, pire cas de Lorden.
- **ARL₀** : durée moyenne avant fausse alarme.
- **Lecture anytime-valid** : e-détecteur arrêté à γ.
- **Lecture exacte** : CUSUM de signe calibré sur le treillis à ARL₀ = γ.
- **G_ADD = ADD_A/ADD_B**, à lecture et γ égaux.

### Tâche
Écrire `experiments/e1_problem.py` avec une option `--include-test-window`, refusée tant que la configuration n'est pas gelée (prompt 21). Fenêtres par défaut : 2005–2019.
1. **Bras injecté, sur fonds D6 (SYM-D2, SYM-`d3_239`).**
   - Familles F3, F1, F2 ; convention (a), SR ∈ {1, 2, 4}.
   - 1000 onsets par cellule ; H_det = 2000 jours.
   - Pipelines :
     - P1-C et P1-D sur chaque actif, en rapportant la médiane et le meilleur actif ;
     - P2-C, avec K ∈ {1, 5, 10, 20, 30, 40, 50, 60, 75, 97}, et jusqu'à 239 sur D3 ;
     - P3-C (marché plus résiduel factoriel, et résiduel complet pour F2) ;
     - P3-D ;
     - P7.
   - γ ∈ {20, 252}.
   - Lectures : anytime-valid pour tous ; exacte pour les CUSUM de signe ; Article B (λ = 10, bootstrap R15) pour P1-C et P2-C.
2. **Bras d'échelle, pour J2.** Convention (b), amplitude par titre fixée ; N ∈ {8, 16, 32, 64, 97} sur D2 et jusqu'à 239 sur D3 ; 20 sous-ensembles emboîtés par N. Mesurer les pentes de log G_ADD en log N :
   - P2-C sur F3 ;
   - P3-C sur F2.
3. **Bras réel.** Phases des trois datations comprises dans 2005–2019 :
   - part des phases dans le budget (L·Î ≥ ln γ) par pipeline ;
   - délais observés dans les phases.
4. **Mesures.**
   - ADD moyen et médian, taux de détection dans H_det, taux de censure ;
   - G_ADD_av, G_ADD_ex, G_floor (rapport des I de l'oracle) ;
   - G_SR : plus petit SR détecté dans 250 jours avec probabilité au moins 1/2, par bissection ;
   - K_eff ;
   - comparaison mesuré/prévu avec `results/audit/predicted_gains.csv`.
5. **Résumé J2** dans `results/e1/e1_j2_summary.txt` :
   - (i) FPR des flux de signe sur fonds D6 à ±1 point du niveau exact du treillis à l'horizon retenu (niveau calculé par `lattice.py`) ;
   - (ii) pente de P2-C sur F3 proche de 0 au-delà de N ≈ 20 (IC bootstrap à 95 % contenant 0, ou borne haute < 0.15) ;
   - (iii) pente de P3-C sur F2 positive, IC à 95 % excluant 0 ;
   - (iv) tableau des gains 1 → 2 → 3, mesurés et prévus.

### Entrées
Prompts 2 à 8 et 11 ; `CLAUDE.md`.

### Livrables
`experiments/e1_problem.py`, `configs/e1.yaml`, `results/e1/{e1_cells.csv,e1_slopes.csv,e1_real_phases.csv,e1_j2_summary.txt}`, `figures/e1/*`, `logs/e1/`.

### Contraintes techniques
- Graines par (cellule, réplication).
- Parallélisme par cellule sans effet sur les résultats.
- Option `--quick` (100 onsets, deux SR) pour un test de fumée en moins de 10 minutes.

### Critères de succès
Exécution complète déterministe ; résumé J2 rempli avec les IC ; chaque nombre du §2 présent dans un CSV.

### Commandes de vérification
```bash
python experiments/e1_problem.py --quick --out results/e1_quick
python experiments/e1_problem.py --out results/e1 && cat results/e1/e1_j2_summary.txt
```
````

````markdown
## PROMPT 13 — E3 : calibration sous H₀ (exactitude des flux, Γ spectral contre Γ opérationnel)

### Contexte
E3 vérifie, sans aucune dérive, que chaque moniteur de JEPA-Drift tient son taux de fausses alarmes. Les flux de signe sont exacts par construction. Les statistiques à amplitude subissent l'hétéroscédasticité : facteur Γ et pénalité de dépassement. E3 fournit le §5.2 et le premier critère de J2. Lire `CLAUDE.md`.

Définitions :
- **Γ^spec** = 1 + 2Σρ(k) de la statistique surveillée.
- **Γ^op** = λ_requis/λ_iid pour tenir l'ARL₀ visé.

### Tâche
Écrire `experiments/e3_calibration.py` ; fenêtres réelles limitées à 2005–2019.
1. **Fonds.**
   - D5 : GARCH(0.08 ; 0.90) à innovations t₇ et gaussiennes ;
   - D6 : SYM-D2, SYM-`d3_239` ;
   - placebo : D2 et D3 bruts.
2. **Pipelines.**
   - P1-C : flux d'étiquettes centré en q̂, et flux exact centré en 1/2 ;
   - P1-D : règle λ_iid × Γ̂, et seuil opérationnel ;
   - P2-C : CUSUM bootstrap, et e-détecteur de pari ;
   - P3-C, P3-D, P3-CS.
3. **Mesures.**
   - FPR à H ∈ {750, 2000} contre le niveau exact du treillis, pour les CUSUM de signe ;
   - ARL₀ Monte Carlo contre γ, pour les e-détecteurs ;
   - Γ^spec (Bartlett) contre Γ^op, pour chaque statistique à amplitude.
4. **Pénalité de dépassement**, à reproduire à ±5 % avec 2000 trajectoires. CUSUM de premier ordre sur x/σ_inconditionnel, GARCH(0.08 ; 0.90) gaussien :
   - δ = 0.5, λ = 6 : ARL₀ ≈ 2587 en i.i.d. contre ≈ 889 sous GARCH ;
   - δ = 1, λ = 3 : 1894 contre 669 ;
   - CUSUM de signe : 213 contre 214 (exact).
5. **Encodeurs à fenêtre.** z_t = moyenne sur L jours de uᵀx, L ∈ {5, 20, 60}. Montrer :
   - Γ_z^spec ≈ L ;
   - l'explosion du FPR d'un CUSUM calibré en i.i.d. ;
   - le rejet de Ljung–Box (20 retards) sur les signes de z.

   Cela justifie un chemin surveillé jour par jour.
6. **Contrôle J2.** Pour chaque flux de signe exact, |FPR − niveau du treillis| ≤ 1 point, écrit dans `results/e3/e3_j2_check.txt`.

### Entrées
Prompts 4 à 8 ; `CLAUDE.md`.

### Livrables
`experiments/e3_calibration.py`, `configs/e3.yaml`, `results/e3/{e3_cells.csv,e3_overshoot.csv,e3_window_encoders.csv,e3_j2_check.txt}`, `figures/e3/*`.

### Contraintes techniques
Au moins 20 000 trajectoires nulles par cellule de signe ; IC de Wilson ; option `--quick`.

### Critères de succès
Flux exacts dans l'IC du niveau exact ; valeurs de la pénalité reproduites ; contrôle J2 écrit.

### Commandes de vérification
```bash
python experiments/e3_calibration.py --quick --out results/e3_quick
python experiments/e3_calibration.py --out results/e3 && cat results/e3/e3_j2_check.txt
```
````

````markdown
## PROMPT 14 — CA-T-JEPA : modèle, pré-entraînement et extracteur (avec variantes MAE et prétexte temporel)

### Contexte
JEPA-Drift apprend une représentation de la coupe quotidienne par un JEPA transversal (Cross-Asset Temporal JEPA) :
- les actifs sont des jetons, conditionnés par leurs caractéristiques ;
- le masquage porte sur des actifs, avec prédiction dans l'espace latent et cible EMA.

Une tête impaire, obtenue par antisymétrisation, alimente les flux de signe exacts ; une tête paire alimente les capteurs d'énergie. Le code doit être prêt pour la campagne de J3 (1er novembre). Lire `CLAUDE.md`.

### Tâche
1. **`jepadrift/jepa/ca_tjepa.py`** (torch, CPU, au plus 1 M de paramètres) :
   - jeton i = MLP([x_{i,t}/s_i, C_{i,t}]), avec s_i l'échelle de l'actif figée sur `pretrain` ;
   - 2 à 4 couches d'auto-attention équivariantes par permutation, sans encodage de position (d_model = 64, 4 têtes) ;
   - encodeur de contexte sur les actifs visibles ; encodeur cible EMA (moment de 0.996 à 0.9995, calendrier cosinus) sur tous les actifs ;
   - prédicteur à 2 couches, dont les requêtes portent C_{i,t} des actifs masqués ;
   - perte L2 dans l'espace latent sur les jetons masqués, plus un terme de variance de type VICReg (charnière sur l'écart-type ≥ 1) ;
   - masquage aléatoire de 30 à 50 % des actifs, ou masquage par secteur (option).
2. **Têtes.**
   - φ_impair(x;C) = ½[g(x;C) − g(−x;C)], φ_pair = ½[g(x;C) + g(−x;C)], avec g le plongement poolé (moyenne sur les actifs) du tronc.
   - Lecture : ACP blanchissante apprise sur `calib`, D ∈ {2, 4, 8, 16} pour la tête impaire et D' identique pour la tête paire. Elle est linéaire, donc l'imparité est conservée.
3. **Variantes.**
   - `--objective mae` : décodeur qui reconstruit x_{i,t} masqué dans l'espace d'entrée.
   - `--objective temporal` : cibles = plongements du jour t+1, sur `pretrain` seulement. L'extraction n'utilise que le jour t.
4. **Script `experiments/jepa_pretrain.py`.**
   - Données : `d3_239`, segment `pretrain`.
   - AdamW (taux 1e-3), lots de 64 jours, au plus 200 époques, arrêt sur la perte JEPA de `calib`.
   - Écrit `ckpt/<hash>/` : poids, configuration, empreinte des données.
5. **Extracteur `jepadrift/jepa/extract.py`.**
   - `model.eval()`, sans gradient, sur CPU.
   - Écrit `z_<hash>.npz` et son JSON selon `docs/sections/interface_Z.md`.
   - Interdit : BatchNorm, normalisation d'instance temporelle (RevIN), EMA active.
6. **Enregistrement** dans le registre des représentations, pour que les tests de contrat du prompt 8 s'appliquent.
7. **Test de fumée** : 2 époques sur 200 jours, extraction, puis contrats.

### Entrées
D3 et caractéristiques (prompt 3) ; interface Z (prompt 6) ; contrats (prompt 8) ; `CLAUDE.md`.

### Livrables
`jepadrift/jepa/{ca_tjepa,extract}.py`, `experiments/jepa_pretrain.py`, `configs/ca_tjepa.yaml`, `tests/test_ca_tjepa.py`, `docs/sections/ca_tjepa.md` (architecture, nombre de paramètres, choix d'anti-effondrement).

### Contraintes techniques
- torch CPU, version figée.
- `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`, toutes les graines fixées.
- Aucune méthode non publiée.
- Aucune donnée de `monitor` vue à l'entraînement ou à l'ajustement de la lecture.

### Critères de succès
- Contrats au vert, dont imparité ≤ 1e-6.
- Deux extractions identiques au SHA-256 près.
- Nombre de paramètres ≤ 1 M.
- Test de fumée en moins de 10 minutes.

### Commandes de vérification
```bash
python experiments/jepa_pretrain.py --config configs/ca_tjepa.yaml --smoke
python -m jepadrift.jepa.extract --ckpt ckpt/<hash> --dataset d3_239
pytest -q tests/test_ca_tjepa.py tests/test_contracts.py
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
2. Entraîner sur les mois 0–2 de la variante Base (prétraitement `preproc.json`).
3. Plongement = moyenne des jetons, puis ACP blanchissante apprise sur le mois 3. D* ∈ {4, 8, 16}, choisi sur les mois 0–2 seulement (RankMe ≥ 0.5·D et perte de validation).
4. Extraire les plongements des mois 0–7 vers `data/derived/d7_baf/z_<hash>.npz`, avec le JSON de l'interface Z.
5. Références à produire avec le même extracteur : ACP sur attributs bruts standardisés (90 % de variance) et attributs bruts.

### Entrées
`data/derived/d7_baf/` (prompt 9) ; interface Z ; `CLAUDE.md`.

### Livrables
`jepadrift/jepa/tjepa.py` (ou une enveloppe), `experiments/tjepa_baf.py`, `configs/tjepa_baf.yaml`, plongements et JSON, `tests/test_tjepa.py`, `docs/sections/tjepa_baf.md` (source, écarts à l'article).

### Contraintes techniques
- CPU accepté ; déterminisme comme au prompt 14.
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
1. Entraîner, sur `d3_239` (segment `pretrain`), les objectifs `jepa`, `mae` et `temporal`, chacun avec 3 graines (0, 1, 2) ; enregistrer les points de contrôle.
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
CPU ; exécutions séquentielles déterministes ; durée totale consignée.

### Critères de succès
12 exécutions principales et 6 de variantes terminées ; porte J3 évaluée ; résultats reproductibles au SHA-256 près pour une graine relancée.

### Commandes de vérification
```bash
python experiments/jepa_campaign.py --dataset d3_239 --seeds 0 1 2 --objectives jepa mae temporal
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
   - normalisation ΓᵀΓ = I, facteurs orthogonaux ;
   - critère d'arrêt sur la variation relative de Γ (≤ 1e-8).
2. Apprendre Γ sur `pretrain` ; choisir K ∈ {1, …, 6} par R² hors échantillon sur `calib` ; blanchir f_t sur `calib`.
3. Option « cash-neutral » : retirer le facteur de marché (constante ou bêta) avant extraction.
4. Enregistrer la représentation et les pipelines P4-C (signes des facteurs, e-détecteur de dictionnaire) et P4-D (énergie).
5. **Tests** :
   - récupération sur données simulées : sous-espace de Γ retrouvé avec des angles principaux < 5° ;
   - imparité ; non-anticipation ; état figé ;
   - contrats du prompt 8.

### Entrées
`d3_239` et `d3_500` avec leurs caractéristiques ; interface Z ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/ipca.py`, `tests/test_ipca.py`, extractions, `results/ipca/k_selection.csv`, `docs/sections/ipca.md`.

### Contraintes techniques
numpy seul ; aucune donnée de `monitor`.

### Critères de succès
Tests au vert ; K choisi et consigné ; contrats passés.

### Commandes de vérification
```bash
pytest -q tests/test_ipca.py tests/test_contracts.py
python -m jepadrift.representations.extract --dataset d3_239 --rep ipca
```
````

````markdown
## PROMPT 18 — Adaptateur CD-DFM (facteurs cash-neutral et covariance conditionnelle)

### Contexte
CD-DFM (Alouadi & Lehalle, arXiv:2607.24410, code public) construit des facteurs cash-neutral à partir des caractéristiques et prévoit la covariance. JEPA-Drift l'utilise comme deuxième modèle latent piloté par les caractéristiques (P4) et comme blanchiment conditionnel (canal N2). Ses entrées d'origine (fondamentaux) ne sont pas disponibles : on l'adapte aux caractéristiques tirées des rendements. Lire `CLAUDE.md`.

### Tâche
1. Cloner `https://github.com/alexouadi/CD-DFM`, épingler le commit, lire la licence et les dépendances. Installer dans `external/cddfm/.venv` si les dépendances entrent en conflit.
2. Adapter les entrées : caractéristiques de `d3_239` (prompt 3) au format attendu. Entraîner sur `pretrain` selon la recette du dépôt, avec K = 11 (marché plus dix facteurs cash-neutral).
3. Extraire :
   - les rendements de facteurs, linéaires en x_t avec appartenances connues en t−1, donc impairs ;
   - la covariance prévue Σ̂(t), pour le blanchiment conditionnel.

   Emballer le tout dans l'interface Z, avec un JSON qui précise l'écart d'entrées.
4. Enregistrer P4-C et P4-D (variante CD-DFM).
5. Si le dépôt est inutilisable (code incomplet, dépendances introuvables), s'arrêter après un diagnostic écrit dans `docs/sections/cddfm_adapter.md`. Priorité B.

### Entrées
Dépôt CD-DFM ; D3 et caractéristiques ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/cddfm_adapter.py`, extractions, `tests/test_cddfm_adapter.py`, `docs/sections/cddfm_adapter.md`, entrée `C-CDDFM-inputs` dans `docs/DEVIATIONS.md`.

### Contraintes techniques
Code externe non modifié (adaptateur seulement) ; graines fixées ; CPU.

### Critères de succès
Imparité des rendements de facteurs ≤ 1e-6 ; contrats au vert ; écart d'entrées documenté.

### Commandes de vérification
```bash
pytest -q tests/test_cddfm_adapter.py tests/test_contracts.py
```
````

````markdown
## PROMPT 19 — E4 : lois d'échelle en N et antériorité PCA « queue » (P3-KF, SPLL)

### Contexte
La signature falsifiable de JEPA-Drift est la loi d'échelle du gain en fonction de la taille N de la coupe :
- N⁰ pour le pooling face à une dérive de marché ;
- N^{1/2} pour une dérive de largeur surveillée dans tout le résiduel ;
- N¹ pour une largeur portée par quelques directions de caractéristiques.

E4 la mesure et reproduit l'antériorité de Kuncheva (composantes de faible variance). Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e4_scaling.py` ; fenêtres antérieures à 2020 avant J4.
1. **Jeux** : D2, `d3_239`, `d3_500` [A] ; D4 [B, s'il est disponible] ; tous symétrisés (D6).
2. **Grille** : N ∈ {8, 16, 32, 64, 128, 239, 500}, borné par N_max ; 20 sous-ensembles emboîtés tirés avec graine.
3. **Familles**, convention (b) à amplitude par titre fixée :
   - F1, primes fixes sur K facteurs ;
   - F2, κ ∈ {0.25, 0.5, 1} ;
   - F3, SR de marché par titre = 1.
4. **Pipelines** : P2-C, P3-C (factoriel et complet), P3-KF, P3-CS, P4-C (IPCA ; CD-DFM si disponible).
5. **P3-KF**, dans `jepadrift/monitors/spll.py` : détecteur de log-vraisemblance semi-paramétrique de Kuncheva (2013, IEEE TKDE ; vérifier la référence) sur les composantes « tail10 » :
   - k-moyennes sur une fenêtre de référence ;
   - statistique sur une fenêtre glissante ;
   - seuil calibré sur des fenêtres nulles D6.
6. **Mesures.**
   - G_ADD_av rapporté à P1 (actif médian) et à P2-C ;
   - pentes de log G en log N avec IC bootstrap sur les sous-ensembles ;
   - comparaison aux exposants 0, 1/2 et 1 (Corollaire 2, `floors.py`) ;
   - audit réduit par sous-ensemble : spectre de Sharpe de dérive débiaisé.

### Entrées
Prompts 5, 7, 11, 17 (et 18) ; `CLAUDE.md`.

### Livrables
`experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`, `results/e4/{e4_cells.csv,e4_slopes.csv}`, `figures/e4/*`.

### Contraintes techniques
Mêmes graines de sous-ensembles pour tous les pipelines ; option `--quick`.

### Critères de succès
Pentes et IC produits pour chaque (famille, pipeline) ; P3-KF calibré dans l'IC de son niveau nominal sur fonds nuls.

### Commandes de vérification
```bash
python experiments/e4_scaling.py --quick --out results/e4_quick
python experiments/e4_scaling.py --out results/e4 && head results/e4/e4_slopes.csv
```
````

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
   - (B) mélange isotrope sur le sous-espace résiduel de dimension D ;
   - mesurer cos²ϑ et les délais, puis comparer à `floors.dictionary_multiplier` et `floors.mixture_multiplier` (angles de bascule).

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
   - Point d'entrée unique : `--config configs/<stream>.yaml`.
   - `run_hash` = SHA-256 de la configuration en JSON canonique, du commit git et des empreintes du manifeste de données.
   - Sortie `results/<stream>/<run_hash>.csv`, une ligne par réplication : `seed, family, D, gamma, reading, ADD, alarm, ...`.
2. **`tools/freeze_config.py`.**
   - Écrit `configs/FROZEN.json` (empreintes de toutes les configurations d'expérience plus commit).
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
Les outils ci-dessus, `configs/FROZEN.json` (au J4), `docs/MAPPING.md` initial, `tests/test_tools.py`.

### Contraintes techniques
Aucune figure lue depuis un état en mémoire ; aucun nombre saisi à la main dans `paper/`.

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
E5 est le test central de JEPA-Drift. La tête impaire du JEPA (P5-C) doit détecter plus vite que les meilleures références linéaires (P3-C, P3-CS, P4-C), à fausses alarmes égales, sur des dérives injectées. La porte J4 (8 novembre) décide du titre de l'article. Lire `CLAUDE.md`.

Définitions :
- **Rétention** r(D) = I_z/I_x.
- **Taxe dimensionnelle** M(D) (`floors.mixture_multiplier`).

### Tâche
Écrire `experiments/e5_jepa.py`, exécuté via le runner avec la configuration gelée.
1. **Jeux** : `d3_239` [A] ; D2 et D4 [B] ; fonds D6.
2. **Pipelines** : P5-C (D ∈ {2, 4, 8, 16}, 3 graines) contre P3-C, P3-CS et P4-C ; ablations P5-MAE et P5-TEMP.
3. **Familles** : F1, F2, F3. Convention (a) avec SR ∈ {1, 2, 4}, et convention (b).
4. **Lecture principale** : anytime-valid. G_ADD_av avec IC bootstrap sur graines et onsets.
5. **r(D)/M(D).**
   - I_z se mesure par injection traversant l'encodeur gelé : Δz = E[z | dérive] − E[z | nul], I_z = ½ΔzᵀΣ_z⁻¹Δz.
   - I_x = ½ΔᵀΣ⁻¹Δ.
   - D* est choisi sur `calib` seulement.
6. **Diagnostics** : RankMe, T(u) (prompt 20), dictionnaire contre sous-espace [C].
7. **Attribution** : P3-CS figure dans chaque tableau principal ; écart P5 − P3-CS rapporté avec son IC.
8. **Porte J4.** G_ADD_av(meilleur de P3-CS et P4 → P5) ≥ 1.25 sur au moins deux familles parmi F1, F2 et F4 (F4 provient d'E6, via P5-D), avec un IC à 95 % qui exclut 1. Écrire `results/e5/J4_gate.txt` : « titre A » ou « titre B ».

### Entrées
Prompts 16, 17, 19, 21 (et 18, 20, 23) ; `CLAUDE.md`.

### Livrables
`experiments/e5_jepa.py`, `configs/e5.yaml`, `results/e5/{e5_cells.csv,e5_retention.csv,J4_gate.txt}`, `figures/e5/*`.

### Contraintes techniques
Fenêtre de test interdite avant le gel ; mêmes graines d'onsets pour tous les pipelines.

### Critères de succès
Porte J4 évaluée avec ses IC ; tableaux principaux complets avec P3-CS.

### Commandes de vérification
```bash
python -m jepadrift.benchmark_runner --config configs/e5.yaml --quick
python -m jepadrift.benchmark_runner --config configs/e5.yaml && cat results/e5/J4_gate.txt
```
````

````markdown
## PROMPT 23 — E6 : dérives de second ordre F4 (rotations, déformations de covariance)

### Contexte
Si l'information de localisation manque sur les données réelles (contingence C1 de JEPA-Drift), l'axe empirique principal devient le second ordre. Un rapport de variance r porte ½(r − 1 − ln r) nat par jour et par direction : 24 fois le budget d'une dérive de SR = 1 pour r = 1.5, 77 fois pour r = 2. E6 compare les têtes paires. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e6_second_order.py`.
1. **Fonds** : D6 de `d3_239`.
2. **Dérives F4** (prompt 5) :
   - déformation r ∈ {1.25, 1.5, 2} sur les sous-espaces des 3 premières PC résiduelles ou d'un facteur sectoriel ;
   - rotation θ ∈ {15°, 30°, 45°}.
3. **Pipelines** : P1-D (indice), P3-D, P4-D et P5-D (tête paire). CUSUM d'énergie δ = 0.5, seuil par bootstrap de fenêtres nulles de calibration ; Γ_z^op rapporté.
4. **Mesures** :
   - G_ADD et taux de détection ;
   - comparaison au budget KL par direction ;
   - contribution d'E6 à la porte J4 (famille F4).

### Entrées
Prompts 5, 7, 16, 17 ; `CLAUDE.md`.

### Livrables
`experiments/e6_second_order.py`, `configs/e6.yaml`, `results/e6/e6_cells.csv`, `figures/e6/*`.

### Contraintes techniques
Les statistiques paires ne se calibrent pas par inversion de signe : utiliser le bootstrap de fenêtres. Graines fixées.

### Critères de succès
FPR sous H₀ dans l'IC de la cible ; G_ADD avec IC par cellule.

### Commandes de vérification
```bash
python experiments/e6_second_order.py --quick --out results/e6_quick
```
````

````markdown
## PROMPT 24 — E9 : dérives natives de BAF (P6-D données, P6-C concept)

### Contexte
E9 évalue la surveillance de JEPA-Drift hors finance, sur la dérive mensuelle native du jeu synthétique BAF. Deux cas : dérive des données, par martingale de test conforme sur plongements ; dérive de concept, par flux d'erreur d'un classifieur figé avec taux nul recentré. Les lignes d'un même mois sont traitées comme échangeables. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e9_baf.py`.
1. **P6-D.**
   - Score de non-conformité : distance au 10ᵉ plus proche voisin dans un échantillon de référence (50 000 lignes des mois 0–2), sur les plongements T-JEPA, ACP et bruts.
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
E8 confronte les pipelines de JEPA-Drift aux phases haussières et baissières réelles. Les datations disponibles sont Pagan–Sossounov strict (48 phases sur les quatre ETF), Lunde–Timmermann pour SPY avec Pagan–Sossounov ailleurs (66), et une variante symétrique (102). La lecture budget (exacte, Lemme 1) sert au recensement ; la lecture anytime-valid sert aux détections. Il ne s'exécute qu'avec la configuration gelée au J4. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e8_real_regimes.py`, lancé via le runner avec `--include-test-window`.
1. **Phases** : fichiers `phases_*.csv` de D1. Pour D2, D3 (et D4 [B]) : phases de l'indice SPY, plus une datation sectorielle par Pagan–Sossounov sur les indices sectoriels équipondérés de D3.
2. **Pipelines** : P1 à P5, avec D* et seuils gelés.
3. **Mesures par phase et par datation** :
   - Î débiaisé du sous-espace du pipeline ;
   - part dans le budget oracle (L·Î ≥ ln γ, γ ∈ {20, 252}) ;
   - détections dans la phase ;
   - fausses alarmes en phases calmes ;
   - délai depuis le début de phase.
4. **Rapport.** Résultats par datation, jamais agrégés en une seule preuve (peu de phases : appui seulement). Comparer à « 2 phases sur 66 » de l'Article B, en rappelant sa composition de datation.

### Entrées
Prompt 21 (gel) ; tous les pipelines ; `CLAUDE.md`.

### Livrables
`experiments/e8_real_regimes.py`, `configs/e8.yaml`, `results/e8/{e8_phases.csv,e8_summary.csv}`, `figures/e8/*`.

### Contraintes techniques
Refus d'exécution si `configs/FROZEN.json` ne correspond pas ; aucune retouche après lecture des résultats sans nouvelle empreinte consignée.

### Critères de succès
Trois datations traitées ; IC de Wilson sur les proportions ; empreinte de gel inscrite dans chaque CSV.

### Commandes de vérification
```bash
python tools/freeze_config.py --check && python -m jepadrift.benchmark_runner --config configs/e8.yaml --include-test-window
```
````

````markdown
## PROMPT 26 — E7 : absorption par un encodeur adaptatif et vieillissement de l'encodeur gelé

### Contexte
Un encodeur mis à jour en ligne absorbe la dérive. Le critère d'absorption de JEPA-Drift (Prop. 4) prévoit qu'il ne détecte presque sûrement que si τ_a > 2τ_γ, avec un délai fluide de −(τ_a/2)·ln(1 − 2τ_γ/τ_a). Un encodeur gelé n'absorbe rien, mais vieillit. E7 mesure les deux effets. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e7_absorption.py`.
1. **P5-ADAPT** : CA-T-JEPA ajusté en ligne sur une fenêtre glissante, avec un taux d'apprentissage qui fixe une mémoire effective. τ_a est mesuré empiriquement par la décroissance de Δz après l'onset.
2. **Comparaison avec P5-C gelé**, sur F1 et F2 injectées sur fonds D6 de `d3_239`, avec τ_a/τ_γ ∈ {0.5, 1, 2, 4, 8}. Comparer les délais mesurés à la prédiction calculée avec le τ_a mesuré (`floors.absorption_delay`).
3. **Vieillissement** : sous H₀, ARL₀ par tranche annuelle depuis la fin du pré-entraînement, sur fonds symétrisés.

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

   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4).
2. **Pipelines** : P1-C, P3-C, P5-C, avec et sans recentrage sur q̂_u estimé sur `calib`.
3. **Mesures** : FPR contre niveau nominal, G_ADD sur F1 et F2.

### Entrées
Prompts 5 et 7 (P5-C si disponible) ; `CLAUDE.md`.

### Livrables
`experiments/e10_robustness.py`, `configs/e10.yaml`, `results/e10/e10_cells.csv`, `figures/e10/*`.

### Contraintes techniques
Graines fixées ; option `--quick`.

### Critères de succès
Inflation du FPR quantifiée par violation, avec IC ; effet du recentrage rapporté.

### Commandes de vérification
```bash
python experiments/e10_robustness.py --quick --out results/e10_quick
```
````

````markdown
## PROMPT 28 — E11 : second domaine en coupe transversale (D8 : Electricity ; SWaT et WADI en option)

### Contexte
E11 teste la portée de JEPA-Drift sur des capteurs corrélés hors finance (Annexe D) : 370 clients électriques (UCI ElectricityLoadDiagrams20112014). SWaT et WADI exigent une demande d'accès à iTrust : ils ne sont traités que si les fichiers sont présents. Lire `CLAUDE.md`.

### Tâche
1. Télécharger le jeu depuis le dépôt UCI : chercher « ElectricityLoadDiagrams20112014 » sur archive.ics.uci.edu et consigner l'URL exacte. Agréger au pas quotidien ; prendre la log-différence de la charge quotidienne par client.
2. Désaisonnaliser (jour de semaine, saison annuelle) sur un segment d'apprentissage. Tester la symétrie centrale (prompt 11) ; si elle est rejetée, utiliser des flux recentrés sur q̂.
3. Construire des fonds D6 et des injections F1–F2.
4. Pipelines : P2-C, P3-C, et P5-C si un CA-T-JEPA est entraîné sur ce domaine (sans caractéristiques).
5. Mesurer G_ADD et le FPR.
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