# Plan — Stream 11 : audit informationnel des panels D2 et D3

> Exécution : Mistral Vibe (routage INDEX : Vibe, High). Spécification : `prompts/streams/prompt-11-audit.md`. Base : HEAD `be7d938` (correctif du stream 07). Arbre propre sauf `logs/d4/` non suivi.

Date : 2026-10-17.

Statut : **GO**. Ce plan est enregistré dans `prompts/plans/plan-11.md` avant toute ligne de code (règle AGENTS.md `C-plan-recording`).

**Objectif.** Écrire `experiments/audit_information.py` qui mesure, avant tout apprentissage, combien d'information de dérive existe dans chaque sous-espace de la coupe transversale (marché, facteurs, résiduel, caractéristiques) sur les fenêtres 2005–2019. Livrer les huit CSV de `results/audit/`, les figures de `figures/audit/` et le journal de `logs/audit/`.

**Architecture.**
- `experiments/audit_information.py` : script unique, argparse, `if __name__ == "__main__":`. Imports : numpy, pandas, scipy.stats, matplotlib (Agg), `jepadrift.floors`, `jepadrift.data_loader.{articleB,sp500}`, `jepadrift.representations.{pca,extract}`, `jepadrift.stats.covariance`.
- Fonctions internes au script (pas de nouveau module library) :
  - `_spectrum(X_calib)` : spectre avec et sans Ledoit–Wolf, η = λ₁/tr Σ par année, bord MP, K.
  - `_sign_stats(X)` : corrélation moyenne des signes ρ̂_signe, correspondance gaussienne, K_eff.
  - `_symmetry_tests(X, directions, sigma_fwd)` : test binomial exact, test des triplets de Randles, correction de Holm.
  - `_drift_sharpe(X, transitions, subspaces)` : SR_S² débiaisé par transition et sous-espace, IC bootstrap par blocs.
  - `_channel_ceilings(X_calib, directions)` : N1, N2, N3.
  - `_budget_share(phases, sharpe_by_phase_subspace, gammas)` : proportion des phases avec L·Î ≥ ln γ.
  - `_predicted_gains(...)` : évaluation de `jepadrift.floors` avec les estimations.
- Utilitaires partagés : `save_fair_csv` importée de `jepadrift.pipelines` ; `_rng(*key)` = `np.random.default_rng(np.random.SeedSequence([11, *key]))`.

## Contexte

- **Consommateurs.** E1 (stream 12) lit `predicted_gains.csv` comme entrée. Le §2 de l'article C utilise les chiffres de spectre, signes, symétrie et Sharpe de dérive. La décision J2 s'appuie sur ces résultats.
- **Fenêtres autorisées.** 2005-01-01 à 2019-12-31 uniquement (avant J4). Aucune donnée postérieure au 2019-12-31.
- **Briques réutilisées.**
  - `jepadrift.floors` : `kl_from_sharpe`, `sharpe_from_kl`, `first_order_floor`, `evidence_budget`, `cusum_exact`, `cusum_threshold`, `mixture_multiplier`, `dictionary_multiplier`, `kl_bernoulli_half`.
  - `jepadrift.stats.covariance` : `ledoit_wolf`, `eigh_desc`.
  - `jepadrift.representations.pca` : `mp_edge`, `mp_count`, `pca_directions`, `PCAOrthogonal`.
  - `jepadrift.representations.extract` : `segment_rows`, `DATASETS`.
  - `jepadrift.data_loader.articleB` : `load_d1`, `load_d2`, `load_phases`, `load_splits`.
  - `jepadrift.data_loader.sp500` : `load_d3_239`, `load_chars`, `load_splits`.
  - `jepadrift.pipelines` : `save_fair_csv`.

## Constats des sondes (lecture seule)

1. **Dimensions.** D2 : 5154 × 97, aucune NaN, pretrain lignes 0–2767, calib 2833–3773 (941 jours). D3_239 : 6738 × 239, seule la ligne 0 contient des NaN (239 valeurs), calib 4090–5030 (941 jours).
2. **Spectre sur calib.** D2 : N/T = 0.1031, λ₊ = 1.7452, K = 5. D3_239 : N/T = 0.254, λ₊ = 2.2619, K = 10. LW : δ̂ = 0.0192 (D2), 0.0252 (D3_239). Part PC1 : 33.1% (D2), 25.9% (D3_239).
3. **Phases SPY (strict_ps, MACRO, 2005–2019).** 14 phases MACRO dans la fenêtre. Les phases se chevauchent (datation hiérarchique) ; les frontières uniques triées forment une partition. Transitions = paires de frontières adjacentes.
4. **Caractéristiques D3.** 4 continues (`c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21`) + 11 indicatrices GICS. Format long (date, asset_id, c_*).
5. **Représentations Z disponibles.** `data/derived/d2_us97/z_<h>.npz` (D=6, mode factor, LW) et `data/derived/d3_239/z_<h>.npz` (D=11, mode factor, LW).
6. **scipy.stats** disponible : `multivariate_t`, `t.fit`, `binomtest`. statsmodels 0.14.5 disponible (non requis).

## Décisions

| Question | Décision | Raison |
|---|---|---|
| Fichier unique | `experiments/audit_information.py`, pas de nouveau module library | Le prompt demande un script ; les fonctions internes sont testables via import |
| Variantes de phases | `strict_ps` (Pagan–Sossounov) uniquement | C'est la datation canonique ; les autres variantes sont des sensibilité |
| Transitions | Frontières uniques triées des phases MACRO de `strict_ps` dans 2005–2019 ; paires adjacentes (n₁, n₂) | « frontières des phases » = boundary dates ; partition de l'axe temporel |
| Sous-espaces | marché (PC1), factoriel (PC2..PC(K+1)), résiduel complet (PC2..PCN), caractéristiques (4 continues orthogonalisées aux loadings) | Prompt item 4 ; d_S ≤ 30 |
| Caractéristiques | 4 continues, orthogonalisées à la matrice de loadings B (PC2..PC(K+1)) par projection résiduelle | F2 = C_t·dγ orthogonalized to loadings (glossaire) |
| Test de Randles | Triplets sur uᵀx_t/σ̂_{t|t−1} avec σ̂ GARCH(1,1) ajusté par `fit_garch_qmle` ; statistique = proportion de triplets monotones vs expectation sous symétrie | Randles et al. (1980), test de symétrie centrale |
| Correction de Holm | `statsmodels.stats.multitest.multipletests(method="holm")` sur les p-values des directions | Prompt item 3 |
| Bootstrap blocs | Blocs mobiles de 20 jours, 2000 tirages, graines `SeedSequence([11, cell, rep])` | Prompt item 4 |
| Dénominateur débiaisage | SR_S² = 252·[Δμ̂_Sᵀ Σ̂_S⁻¹ Δμ̂_S − d_S(1/n₁ + 1/n₂)]·(n − d_S − 1)/n | Prompt item 4, formule exacte |
| N1 | E[σ_t²]·E[σ_t⁻²] sur la dispersion transversale résiduelle (écart à la moyenne cross-sectionnelle) | Prompt item 5 |
| N2 | Ratio information conditionnelle (Σ_t LW glissant 60 jours, passé seulement) / information statique, pour directions F1 (PC1) et F2 (caractéristiques) | Prompt item 5 |
| N3 | ν̂ par ajustement t multivariée (MLE) sur résidus blanchis ; rapport J/Σ⁻¹ = (ν+1)ν/((ν+3)(ν−2)) par direction | Prompt item 5 |
| Budget share | Pour γ ∈ {20, 252}, proportion des phases avec L·Î ≥ ln γ où L = min(n₁, n₂) et Î = SR_S²/504 | Lecture budget, exacte par Lemme 1 |
| predicted_gains.csv | Colonnes : dataset, subspace, rho_hat, kappa_hat, spectrum_summary, gamma, predicted_add_budget, predicted_add_exact, predicted_add_anytime, G_floor, G_ADD_av, G_SR | Entrée d'E1 ; évaluation de `floors.py` |
| Figures | 5 figures PNG + PDF depuis les CSV uniquement : spectre (eigenvalues + MP edge), η par année, matrice de corrélation des signes, QQ-plot des triplets Randles, Sharpe de dérive par sous-espace | Prompt livrables |
| CSV | `save_fair_csv` de `jepadrift.pipelines` pour tous les CSV | Hash SHA-256 invariant |
| Langue | Anglais : code, docstrings, commit. Français : ce plan et `docs/DEVIATIONS.md` | Règles du projet |
| Commit | Unique : `feat(audit): add information audit of D2/D3 cross-sections` | Convention Conventional Commits |

## Livrables CSV

| Fichier | Colonnes principales |
|---|---|
| `spectrum.csv` | dataset, segment, year, shrinkage, lambda_1, trace, eta, mp_edge, K, n_above_edge, delta_lw |
| `eta_by_year.csv` | dataset, year, eta_raw, eta_lw, n_days |
| `sign_corr.csv` | dataset, segment, K, rho_sign, rho_gauss, K_eff_meas, K_eff_ana |
| `symmetry_tests.csv` | dataset, direction, n, q_hat, binom_p, randles_stat, randles_p, holm_reject |
| `drift_sharpe_transitions.csv` | dataset, transition_id, boundary_date, subspace, d_S, n1, n2, SR2_raw, SR2_debiased, IC_lo, IC_hi |
| `channel_ceilings.csv` | dataset, ceiling, subspace, value, detail |
| `budget_share.csv` | dataset, gamma, subspace, n_phases, n_detectable, share |
| `predicted_gains.csv` | dataset, subspace, rho_hat, info_per_day, gamma, add_budget, add_exact, add_anytime, G_floor, G_ADD_av, G_SR |

## Contraintes globales

- **Fenêtre temporelle.** Toutes les statistiques sur les lignes datées de 2005-01-01 à 2019-12-31. Aucune donnée postérieure.
- **Environnement.** OMP/MKL/OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42. Interpréteur : `.venv/bin/python` (ou `/home/m53/miniforge3/envs/Trading/bin/python`).
- **Aléa.** `SeedSequence` uniquement, clés `[11, cell, replicate]`. Aucun état global.
- **Figures.** `MPLBACKEND=Agg`, PNG + PDF, depuis les CSV uniquement.
- **Code nouveau.** Aucun commentaire sauf `# ponytail:`, docstrings d'une ligne, aucune marque d'IA, aucun `# noqa`.
- **Commit.** Conventional Commits, sans trailer. Indexation par chemins explicites, jamais `git add .`.
- **Determinisme.** Exécution déterministe au SHA-256 près (critère de succès).

## Points de vigilance

1. **Chevauchement des phases.** Les phases MACRO de `strict_ps` se chevauchent (datation hiérarchique). On extrait les frontières uniques triées pour former une partition.
2. **NaN dans D3.** La ligne 0 de D3_239 contient 239 NaN. Les exclure de toute statistique.
3. **D2 sans NaN.** Toutes les lignes de D2 sont utilisables.
4. **D3_239 vs D3_500.** Seul `d3_239` est audité (le prompt mentionne D2 et D3).
5. **Caractéristiques D3.** Format long ; pivot en wide (T × N × n_chars) puis orthogon cuartaux.
6. **Test de Randles.** Implémentation propre (pas de package dédié) : pour chaque direction u, calculer les triplets (y_{t-1}, y_t, y_{t+1}) avec y_t = uᵀx_t/σ̂_{t|t−1}, compter les triplets strictement croissants ou décroissants, comparer à l'expectation sous symétrie centrale.

## Fichiers

- **Créés** :
  - `experiments/audit_information.py` ;
  - `tests/test_audit.py` ;
  - `results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains}.csv` ;
  - `figures/audit/*.{png,pdf}` ;
  - `logs/audit/run.log` ;
  - `prompts/plans/plan-11.md`, `prompts/wrapups/wrapup-11.md`.
- **Modifiés** :
  - `docs/DEVIATIONS.md` : entrées en fin de fichier (si déviations).
- **Non touchés** : `Makefile`, `requirements.*`, `jepadrift/*` (sauf si bug bloquant), `AGENTS.md`.

---

### Tâche 0 — Préconditions
- [x] Enregistrer ce plan dans `prompts/plans/plan-11.md`, avant toute ligne de code.
- [ ] `git log --oneline -3` et `git status --short` : HEAD attendu `be7d938`. Fichier étranger connu : `logs/d4/` (non suivi, ne jamais indexer).
- [ ] Référence « avant » : `pytest -q tests/test_representations.py tests/test_pipelines.py tests/test_floors.py`, tout au vert.

### Tâche 1 — Squelette du script et CLI

**Interfaces.**
- `main(argv=None)` avec argparse : `--datasets` (défaut `d2_us97,d3_239`), `--out` (défaut `results/audit`), `--figures` (défaut `figures/audit`), `--log` (défaut `logs/audit`), `--seed` (défaut 11).
- Fonctions internes stubées (retour `NotImplementedError`) pour les 7 blocs du prompt.

- [ ] Créer `experiments/audit_information.py` avec :
  - `MPLBACKEND=Agg` avant import matplotlib ;
  - variables d'environnement thread avant import numpy ;
  - imports : numpy, pandas, scipy.stats, matplotlib.pyplot, pathlib, argparse, json, math, sys ;
  - imports jepadrift : `floors as fl`, `data_loader.{articleB,sp500}`, `representations.{pca,extract}`, `stats.covariance`, `pipelines.save_fair_csv` ;
  - `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` pour les imports.
- [ ] Tests dans `tests/test_audit.py` :
  - `test_imports` : le module s'importe sans erreur ;
  - `test_cli_help` : `main(["--help"])` retourne 0 (SystemExit) ;
  - `test_cli_defaults` : `main(["--datasets", "d2_us97", "--out", str(tmp_path)])` avec stubs retourne 0.
- [ ] `pytest -q tests/test_audit.py` au vert.

### Tâche 2 — Spectre (item 1)

**Interface.** `_spectrum(X_calib, dates_calib, dataset) -> list[dict]`.

- [ ] `spectrum.csv` : par dataset, segment=calib, shrinkage ∈ {none, ledoit_wolf} :
  - `lambda_1`, `trace`, `eta = lambda_1/trace`, `mp_edge`, `K` (n_above_edge − 1), `n_above_edge`, `delta_lw`.
- [ ] `eta_by_year.csv` : par année civile de la calib (2016, 2017, 2018, 2019) :
  - fenêtre glissante d'un an (252 jours), η avec et sans LW, `n_days`.
- [ ] Tests :
  - `test_spectrum_d2` : D2 calib, shrinkage=none → K=5, mp_edge ≈ 1.7452, eta = lambda_1/trace ;
  - `test_spectrum_d3` : D3_239 calib, shrinkage=none → K=10, mp_edge ≈ 2.2619 ;
  - `test_eta_by_year` : 4 années, n_days = 252 (sauf dernière année partielle).
- [ ] Figure `spectrum.png/pdf` : eigenvalues (log scale) + MP edge horizontal, par dataset et shrinkage.

### Tâche 3 — Signes (item 2)

**Interface.** `_sign_stats(X, dataset, segment) -> dict`.

- [ ] `sign_corr.csv` : par dataset, segment (calib), K ∈ {5, 10, 20, N} :
  - ρ̂_signe = corrélation moyenne des signes (arithmétique R15) ;
  - ρ_gauss = sin(π·ρ̂_signe/2) (correspondance gaussienne) ;
  - K_eff = 1/ρ̂_signe.
- [ ] Réutiliser `pipelines.composition_for` et `pipelines.sign_diagnostics` pour la cohérence avec R15.
- [ ] Tests :
  - `test_sign_corr_d2_k5` : ρ̂ ≈ 0.2577, K_eff ≈ 2.462 (valeurs R15) ;
  - `test_sign_corr_d2_k20` : ρ̂ ≈ 0.2881, K_eff ≈ 3.092 ;
  - `test_gauss_correspondence` : ρ = sin(π·ρ̂/2) pour ρ̂ connu.
- [ ] Figure `sign_corr.png/pdf` : ρ̂_signe et K_eff par K, par dataset.

### Tâche 4 — Symétrie centrale (item 3)

**Interface.** `_symmetry_tests(X, dates, dataset, splits) -> list[dict]`.

Directions figées : PC1–PC20 (de `pca_directions` sur calib, LW), directions de caractéristiques orthogonalisées (4 continues D3 uniquement).

- [ ] `symmetry_tests.csv` : par dataset, direction :
  - `q_hat` = moyenne de 1{uᵀx_t > 0} sur la calib ;
  - `binom_p` = p-value du test binomial exact contre 1/2 (`scipy.stats.binomtest`) ;
  - `randles_stat` = statistique des triplets de Randles et al. (1980) sur uᵀx_t/σ̂_{t|t−1} ;
  - `randles_p` = p-value asymptotique normale ;
  - `holm_reject` = rejet après correction de Holm (sur toutes les directions d'un dataset).
- [ ] σ̂_{t|t−1} : ajustement GARCH(1,1) par `jepadrift.stats.garch.fit_garch_qmle` sur chaque série uᵀx_t.
- [ ] Test de Randles : pour y_t = uᵀx_t/σ̂_{t|t−1}, compter les triplets (y_{t−1}, y_t, y_{t+1}) strictement monotones (croissants ou décroissants). Sous symétrie centrale, P(monotone) = 1/3. Statistique = (count − n/3) / √(n·2/9).
- [ ] Tests :
  - `test_symmetry_pc1_d2` : q̂ ≈ 0.5, |binom_p| > 0.01 ;
  - `test_randles_null` : sur données simulées symétriques (gaussiennes), randles_p > 0.01 dans 95% des cas ;
  - `test_holm_correction` : correction de Holm appliquée correctement (vérifier avec statsmodels).
- [ ] Figure `symmetry_tests.png/pdf` : QQ-plot des p-values binomiales et Randles par direction.

### Tâche 5 — Spectre de Sharpe de dérive débiaisé (item 4)

**Interface.** `_drift_sharpe(X, dates, transitions, subspaces, dataset, rng) -> list[dict]`.

- [ ] Transitions depuis `phases_strict_ps.csv` (MACRO, 2005–2019) : frontières uniques triées, paires adjacentes.
- [ ] Sous-espaces : marché (PC1), factoriel (PC2..PC(K+1)), résiduel complet, caractéristiques (D3 uniquement).
- [ ] `drift_sharpe_transitions.csv` : par dataset, transition, sous-espace :
  - `SR2_raw` = 252·Δμ̂_Sᵀ Σ̂_S⁻¹ Δμ̂_S ;
  - `SR2_debiased` = 252·[Δμ̂_Sᵀ Σ̂_S⁻¹ Δμ̂_S − d_S(1/n₁ + 1/n₂)]·(n − d_S − 1)/n ;
  - `IC_lo`, `IC_hi` = intervalle de confiance bootstrap par blocs (20 jours, 2000 tirages, 95%) ;
  - agrégation par médiane sur les transitions (colonne `median_SR2`).
- [ ] d_S ≤ 30 : le résiduel complet est tronqué à PC2..PC31 si N > 31.
- [ ] Tests :
  - `test_drift_sharpe_formula` : sur données simulées avec dérive connue, SR2_debiased ≈ SR² théorique ;
  - `test_drift_sharpe_no_drift` : sous H₀ (pas de dérive), SR2_debiased centré sur 0 ;
  - `test_bootstrap_ic` : IC couvre la vraie valeur dans 95% des cas sur simulation.
- [ ] Figure `drift_sharpe.png/pdf` : SR2 débiaisé par sous-espace, par dataset, avec IC.

### Tâche 6 — Plafonds des canaux (item 5)

**Interface.** `_channel_ceilings(X_calib, directions, dataset) -> list[dict]`.

- [ ] `channel_ceilings.csv` :
  - N1 : E[σ_t²]·E[σ_t⁻²] sur la dispersion transversale résiduelle (écart à la moyenne cross-sectionnelle, par jour) ;
  - N2 : ratio information conditionnelle / statique pour F1 (PC1) et F2 (caractéristiques), Σ_t = LW glissant 60 jours (passé seulement) ;
  - N3 : ν̂ par MLE t multivariée sur résidus blanchis, rapport J/Σ⁻¹ = (ν+1)ν/((ν+3)(ν−2)) par direction.
- [ ] Tests :
  - `test_n1_gaussian` : sur données i.i.d. gaussiennes, N1 ≈ 1 ;
  - `test_n1_heteroskedastic` : sur données à volatilité variable, N1 > 1 ;
  - `test_n3_t_distribution` : sur résidus t7 simulés, ν̂ ≈ 7, J/Σ⁻¹ ≈ (7+1)·7/((7+3)(7−2)).

### Tâche 7 — Part du budget (item 6)

**Interface.** `_budget_share(phases, sharpe_by_phase, gammas=(20, 252)) -> list[dict]`.

- [ ] `budget_share.csv` : par dataset, γ, sous-espace :
  - `n_phases` = nombre de transitions ;
  - `n_detectable` = nombre de transitions avec L·Î ≥ ln γ, où L = min(n₁, n₂) et Î = SR2_debiased/504 ;
  - `share` = n_detectable/n_phases.
- [ ] Lecture budget, exacte par le Lemme 1 (`floors.evidence_budget`).
- [ ] Tests :
  - `test_budget_share_bounds` : share ∈ [0, 1] ;
  - `test_budget_share_monotone` : share(γ=252) ≤ share(γ=20).

### Tâche 8 — Gains prévus (item 7)

**Interface.** `_predicted_gains(spectrum_stats, sign_stats, drift_stats, dataset) -> list[dict]`.

- [ ] `predicted_gains.csv` : évaluation de `jepadrift.floors` avec ρ̂, κ̂ et spectre estimés :
  - `add_budget` = `fl.evidence_budget(gamma, info)` (lecture budget) ;
  - `add_exact` = `fl.cusum_exact(gamma, theta)["add"]` (ARL₀ = γ, Lorden-optimal) ;
  - `add_anytime` = `fl.cusum_threshold(gamma, theta)["add"]` (e-détecteur CUSUM) ;
  - `G_floor` = I_B/I_A (ratio exact des informations) ;
  - `G_ADD_av` = ratio ADD à seuil anytime-valid égal ;
  - `G_SR` = ratio du plus petit SR détecté dans H jours avec probabilité ≥ 1/2.
- [ ] Tests :
  - `test_predicted_gains_columns` : toutes les colonnes présentes ;
  - `test_predicted_gains_consistency` : add_budget ≥ add_exact ≥ add_anytime (inégalité théorique).

### Tâche 9 — Figures finales et journal

- [ ] 5 figures PNG + PDF depuis les CSV uniquement :
  - `spectrum.png/pdf` : eigenvalues + MP edge ;
  - `eta_by_year.png/pdf` : η par année ;
  - `sign_corr.png/pdf` : ρ̂ et K_eff par K ;
  - `symmetry_tests.png/pdf` : QQ-plot p-values ;
  - `drift_sharpe.png/pdf` : SR2 par sous-espace avec IC.
- [ ] `logs/audit/run.log` : journal d'exécution avec `tee`.
- [ ] Vérification déterministe : relancer le script, `sha256sum results/audit/*.csv` identiques.

### Tâche 10 — Clôture (ordre AGENTS.md)
- [ ] Vérifications :
  - `pytest -q tests/test_audit.py` ;
  - `source .venv/bin/activate && make check`. En cas d'échec : diagnostic, 3 tentatives au plus ;
  - `python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit` exécuté avec succès ;
  - `ls results/audit && sha256sum results/audit/*.csv` ;
  - `git status --short` : seuls les fichiers du stream sont modifiés/créés.
- [ ] (1) Skill `wrap-up` → `prompts/wrapups/wrapup-11.md`.
- [ ] (2) `tools/reindex_graphify_jcodemunch.sh`.
- [ ] (3) `make check`, puis commit unique sans trailer :
  - indexer explicitement les fichiers créés et modifiés ;
  - `git diff --staged` : aucun fichier d'un autre stream, aucun `__pycache__`, aucun chemin absolu, aucun fichier > 50 Mo.
- [ ] (4) Contrôler la plage `origin/main..HEAD` : aucun chemin sous `data/raw/eurofidai/` ni sous `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo. Puis `git push origin main`, et rapporter le hash du commit et l'état propre de l'arbre.

## Vérification de bout en bout

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
ls results/audit && sha256sum results/audit/*.csv
pytest -q tests/test_audit.py
make check
```

## Risques

| Risque | Parade |
|---|---|
| Chevauchement des phases `strict_ps` | Extraction des frontières uniques triées pour partition temporelle |
| NaN dans D3 ligne 0 | Exclusion systématique de la ligne 0 (2000-01-03) |
| GARCH fit échoue sur certaines directions | Fallback sur σ̂ constant = écart-type empirique ; signaler dans le log |
| t multivariée MLE lent (N=239) | Ajustement sur les 20 premières PC uniquement (d_S ≤ 30) |
| Bootstrap 2000 tirages × 30 transitions × 4 sous-espaces | Vectorisation numpy ; parallélisation non requise (script unique) |
| Caractéristiques D3 : format long | Pivot en wide (T × N × 4) avant orthogonProjection |
| Figures non déterministes | `MPLBACKEND=Agg`, pas de date dans les figures, données depuis CSV uniquement |
