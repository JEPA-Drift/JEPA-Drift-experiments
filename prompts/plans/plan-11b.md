# Plan — Stream 11b : bruit d'estimation de N2 et biais de sélection du SR² de marché

> Exécution : Claude Code, session unique, sans sous-agent ; `superpowers:executing-plans` en mode natif, TDD par tâche. Chaque commande Bash commence par `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate`.

Date : 2026-10-18. Spécification : `prompts/GO-stream-11b.md`. Base : `9a36c2f` (`origin/main`, stream 11). Worktree `~/JEPA-Drift-stream-11b`, branche `stream-11b`, liens absolus `.venv` et `external`, `data/raw/` en liens par sous-dossier (`d3_yf`, `baf`).

Statut : **GO** (fichier GO et réponses du chercheur du 2026-10-18, intégrés ci-dessous). Le correctif d'environnement annoncé (hook pre-commit, recette worktree d'AGENTS.md) n'est pas encore sur `origin/main`. Le chercheur a demandé de continuer avec les contournements du GO : liens `data/raw` par sous-dossier ; restauration de `data/derived/MANIFEST.json` et `logs/data/build.log` après chaque commit passé par le hook (jamais indexés). Le rebase final intègre le correctif s'il est poussé entre-temps.

## Décision GO intégrée

| Point | Décision |
|---|---|
| Fond « bruit seul » de N2 | **Permutation aléatoire des jours entiers de W** (et non D6). D6 multiplie chaque jour par un signe : |x_t|, les corrélations et le clustering de volatilité survivent, donc la dynamique de Σ_t aussi. La sonde le confirme : D6 redonne le rapport complet (D2 PC1 5,44 contre 5,54 ; D3 PC1 11,2 contre 11,33). La permutation garde la coupe de chaque jour et efface la dynamique temporelle : chaque fenêtre LW de 60 jours estime le même Σ̄, et le rapport mesure l'écart de Jensen pur de l'estimation. Sonde : 2,27 (D2 PC1), 3,75 (D3 PC1) |
| Directions sous la permutation | Seules les lignes de X sont permutées. Les directions restent dans l'ordre du calendrier : F1 = colonnes de B, F2 = résidus GLS des 15 caractéristiques de D3 |
| Valeur nette | `value_net = value(lw60) / value(lw60_shuffle)`, car l'écart de Jensen est multiplicatif. Le rapport est sans échelle et vaut 1 sous le nul. Il annule aussi le facteur de variation des directions F2, qui ne dépend pas de l'ordre des jours. Écart au GO (qui écrivait `value − bruit`) → `C-audit-n2-noise` |
| Schéma N2 | Aucune nouvelle colonne. Nouvelles valeurs de `variant` dans `channel_ceilings.csv` : `lw60_shuffle` (médiane sur les B fonds du rapport bruit) et `lw60_net` |
| Borne gaussienne | Sur des données i.i.d. gaussiennes, le rapport bruit n'est pas proche de 1 aux dimensions réelles (sonde : 3 à 8 à N = 97/239 et 60 jours) : il mesure justement le bruit. Borne documentée et testée : sous un Σ constant, la valeur nette vaut 1 (sonde sur un petit panel : 1,01) ; avec des régimes de volatilité, elle dépasse 1 (sonde : 1,8 à 2,0) |
| Placebo | **Rotation circulaire** de la chaîne réelle des phases dans W : départ uniforme, retour au début de W. Le multiset des (n₁, n₂) et le nombre de transitions sont ceux de la datation réelle. La phase qui enjambe le joint est formée de deux segments dont les lignes sont rassemblées : `debiased_sr2` n'opère que sur des ensembles de lignes. Écart (raffinement) → `C-audit-placebo` |
| Schéma placebo | Niveau `placebo` dans `drift_sharpe_transitions.csv` (colonnes inchangées, `n_boot` suit `--boot`) et CSV dédié `results/audit/placebo_selection.csv` |
| Volume | B = 2000 fonds, P = 2000 rotations. Calcul parallèle par fond (`--jobs`, contexte `spawn` comme `pipelines.run_pipeline`) ; une graine `SeedSequence` par fond et par rotation, donc un résultat indépendant du nombre de processus |

## Constat des sondes (2026-10-18) et décision d'exécution

Sur 400 rotations, les médianes placebo du SR² de marché débiaisé sont **négatives** : −2,5 et −1,7 (D2), −2,6 et −1,8 (D3). Le débiaisage centre la moyenne, mais la loi de l'estimateur est asymétrique et sa médiane est négative près de 0. Les médianes réelles valent 40,8 et 19,3 (D2), 38,2 et 22,3 (D3). Avec p ≈ 0,0025–0,0075, la sélection est massive. Le rapport réel/placebo du GO n'a donc pas de sens (dénominateur ≤ 0). Décision :
- `selection_factor` = réel/placebo si la médiane placebo est > 0, sinon NaN (même règle que les gains prévus) ;
- deux colonnes ajoutées au CSV dédié :
  - `selection_excess` = réel − placebo, en unités de SR² ;
  - `p_placebo` = (1 + #{placebo ≥ réel})/(1 + P) ;
- le test « rapport > 1 sur les deux jeux » devient « excès > 0 et p_placebo < 0,05 sur les deux jeux et les trois datations » ;
- le contrôle nul (« ≈ 1 sur un panel i.i.d. ») devient : sur un panel sans structure, la médiane réelle se situe dans la masse centrale du placebo, p_placebo ∈ [0,025 ; 0,975]. Le rapport 0/0 n'est pas testable.
- Le tout est documenté dans `C-audit-placebo`.

## Définitions

1. **Bruit de N2.** Pour un fond b, X_b = X[π_b] avec π_b = `default_rng(SeedSequence([11, 11, crc32(jeu), b])).permutation(T)`. On calcule ensuite `info_ratio(directions, rolling_lw(X_b))`, sur les directions de N2 et sur les mêmes jours t ≥ 60.
   - `lw60_shuffle` = médiane sur b = 0..B−1, par direction.
   - `lw60_net` = `lw60` / `lw60_shuffle`.
2. **Placebo.** Phases réelles SPY de la datation dans W, partition des lignes [0, T).
   - Rotation d'un décalage o : lignes (r + o) mod T, triées. Les décalages viennent de `default_rng(SeedSequence([11, 12, crc32(jeu), crc32(datation)])).integers(0, T, P)`.
   - Transitions : les paires (i, j) gardées sur la chaîne réelle (`transitions`), appliquées aux phases tournées.
   - Statistique d'une chaîne : médiane, sur ses transitions, de `debiased_sr2` du sous-espace `market` (PC1).
   - IC de la médiane placebo : bootstrap i.i.d. des P médianes, B tirages, graine `SeedSequence([11, 13, crc32(jeu), crc32(datation)])`, percentile à 95 %.

## Schémas

- `channel_ceilings.csv` : colonnes inchangées. Lignes `N2` ajoutées, de variantes `lw60_shuffle` et `lw60_net`, par direction ; `n_days` et `d` comme pour `lw60`.
- `drift_sharpe_transitions.csv` : colonnes inchangées. Une ligne `level = placebo` par (jeu, datation), avec :
  - `transition = placebo`, `boundary` vide, `n1` et `n2` NaN, `n_transitions` = nombre de transitions par chaîne ;
  - `subspace = market`, `d = 1` ;
  - `sr2_raw`, `sr2_debiased` et `sr2_spec` = médianes sur les P chaînes ;
  - `ci_lo` et `ci_hi` = IC bootstrap de la médiane placebo de `sr2_debiased` ; `n_boot` = B.
- `placebo_selection.csv` (nouveau) : `dataset, dating, n_transitions, n_placebo, sr2_real_median, sr2_placebo_median, ci_lo, ci_hi, selection_factor, selection_excess, p_placebo`.
- Les lecteurs existants ne changent pas : `budget_rows`, `predicted_rows`, `_summary` et `plot` filtrent déjà les niveaux `transition` et `median`.

## Tâches

### Tâche 0 — Préconditions
- [x] Worktree, liens et copie du GO ; `git status` : seuls `.venv`, `external` et le GO apparaissent non suivis.
- [ ] Enregistrer ce plan, puis exécuter `make check` sur la base (référence).

### Tâche A — Bruit de N2 (`experiments/audit_information.py`)
- Interfaces :
  - `_directions(B, F2, T)` : générateur des a_t (N, m), F1 puis F2, t ≥ `LW_DAYS` ; réutilisé par `ceiling_rows`.
  - `_noise_chunk(X, B, F2, keys) -> list[np.ndarray]`.
  - `n2_noise(X, B, F2, keys, jobs) -> np.ndarray` (n_fonds, m), qui répartit des paquets de clés sur `jobs` processus (`spawn`).
  - `ceiling_rows(d, proj, scales, n_noise, jobs)` ajoute les lignes `lw60_shuffle` et `lw60_net`.
- Tests, d'abord en échec :
  - `test_n2_noise_null_and_workers` : panel i.i.d. (T = 400, N = 12), directions constantes, 8 fonds ; |net − 1| < 0,05 ; bruit > 1 ; résultat identique à `jobs = 1` et à `jobs = 2` ;
  - `test_n2_noise_volatility_regimes` : même panel, blocs de 100 jours de volatilité 1 ou 3 ; net > 1,5.

### Tâche B — Placebo
- Interfaces :
  - `rotate_phases(phases, T, offset)` ;
  - `placebo_rows(name, dating, phases, y, P, B) -> (ligne de niveau placebo, ligne de placebo_selection.csv)`.
- Tests, d'abord en échec :
  - `test_rotate_phases` : tailles conservées, partition de [0, T), décalage 0 = identité, phase du joint rassemblée ;
  - `test_placebo_controls` : contrôle positif (frontières réelles sur les vrais changements de moyenne du marché : excès > 0, p_placebo < 0,05, facteur > 1) ; contrôle nul (panel sans structure : p_placebo ∈ [0,025 ; 0,975]) ;
  - `test_placebo_selection_committed` : sur `results/audit/placebo_selection.csv` commité, excès > 0 et p_placebo < 0,05 pour les deux jeux et les trois datations.

### Tâche C — CLI, exécution, clôture
- CLI :
  - `--jobs` (par défaut `os.cpu_count()`) ;
  - `--quick` : 8 fonds et P = 50, en plus de B = 50 et de PC1 à PC3 ;
  - `COLUMNS` reçoit `placebo_selection` ;
  - le journal consigne bruit, net, excès et p.
- Le test de fumée CLI vérifie les 9 CSV et les variantes et niveaux nouveaux.
- Deux exécutions complètes : SHA-256 identiques sur les 9 CSV (critère du GO).
- `docs/DEVIATIONS.md` : `C-audit-n2-noise`, `C-audit-placebo`.
- Wrapup `prompts/wrapups/wrapup-11b.md`, réindexation, `make check`.
- Commit `feat(audit): quantify the N2 estimation noise on D6 and the market SR2 selection bias`. C'est le libellé du GO ; le corps du commit précise que le fond retenu est la permutation des jours.
- Restauration des fichiers réécrits par le hook, rebase, contrôle de plage, `git push origin stream-11b:main`, retrait de la copie du GO dans l'arbre principal, puis avance rapide.

## Vérification

```bash
pytest -q tests/test_audit.py
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
python experiments/audit_information.py --datasets d2_us97 d3_239 --out $SCRATCH/audit2 --fig-dir $SCRATCH/fig2 --log-dir $SCRATCH/log2
diff <(cd results/audit && sha256sum *.csv) <(cd $SCRATCH/audit2 && sha256sum *.csv)
make check
```

## Risques

- **Durée.** B = 2000 passages d'environ 5 s sur D3 donnent environ 10 000 s de CPU, soit environ 5 min sur 40 processus. `--jobs 1` reste correct mais lent.
- **Mémoire.** Directions F2 de D3 (108 Mo) envoyées une fois par paquet de travail.
- **Lecture des résultats.** La sélection rend le SR² de marché aux frontières datées inutilisable comme référence non sélectionnée, ce qui touche les dénominateurs des gains 2→3 du stream 11. Le résultat est rapporté, sans correction rétroactive des gains.
