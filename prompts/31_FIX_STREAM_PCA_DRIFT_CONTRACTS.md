# Prompt d'implémentation — correctif D7b du stream 31 (figures PCA full 2000)

Instance destinataire : toute instance CLI de vibe coding. Ce prompt est agnostique du
modèle et de l'outil ; il ne contient aucune règle spécifique à un produit. Supervision,
GO, revue et opérations git : Codex. Émetteur du mandat : le chercheur.

## 0. Contexte et mandat

- Worktree d'implémentation : `/home/m53/JEPA-stream-31`, base commit
  `20ad9e860a58373ec85405de6ee19a68322dd02e`. Ne travaillez que dans ce worktree.
- Le lot 2 QA du stream 31 s'est terminé en STOP : `docs/audits/PCA_CONTRACTS_VALIDATION.md`
  rapporte 43 passed / 1 failed. Le seul échec est **D7b**
  (`test_full_figure_text_sample_sizes_match_manifest`) : la figure full 2000 imprime
  « (n = 40) » en dur (`experiments/figures/plot_figure_1.py:582`) alors que le manifeste
  full déclare 2000 trajectoires par rôle. En smoke, n = 40 est correct (effectif réel du
  run smoke) : **les figures smoke ne sont pas concernées**.
- Le chercheur a émis l'avenant `prompts/FIX-stream-31-nb-assets.md` (dans
  `/home/m53/JEPA-Drift-experiments/prompts/`) qui **lève l'invariant d'amorçage n°2 pour
  ce cas précis** : il autorise le correctif de la ligne 582 et le remplacement des deux
  répertoires de figures full scellés par un re-render complet. Lisez cet avenant en
  premier ; il prime sur toute interdiction antérieure de toucher aux figures full.

## 1. Lectures obligatoires avant toute mutation

Depuis la racine du worktree `/home/m53/JEPA-stream-31` :

1. `prompts/FIX-stream-31-nb-assets.md` (avenant, dans `/home/m53/JEPA-Drift-experiments/prompts/`)
2. `docs/audits/PCA_CONTRACTS_VALIDATION.md` §6 (D7b FAIL et état STOP)
3. `prompts/plans/plan-31.md` §4.4 (D7b) et §5 (procédure STOP)
4. `prompts/GO-stream-31.md`
5. `experiments/figures/plot_figure_1.py` (ligne 582 et environs ; `OUTPUT_NOT_EMPTY` ligne 896)
6. `tests/test_pca_drift_contracts.py` (D7b ligne ~1492, fixtures `full_ctx`, `full_renders`)
7. `docs/sections/pca_drift_figures.md` §3–5 (contrat des sorties et complétude)

## 2. Tâche 1 — correctif code (diff minimal)

Rendre le « n = x » de `experiments/figures/plot_figure_1.py:582` dépendant du run :
valeur dérivée du manifeste (ex. `config` `n_cal`/`n_null`/`n_alt` du run courant),
jamais une constante. Comportement attendu : full → « n = 2000 », smoke → « n = 40 ».
Une seule ligne modifiée si possible. Aucun autre fichier producteur touché.

## 3. Tâche 2 — preuves unitaires

Préfixe obligatoire de chaque commande (racine du worktree) :

```bash
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
       MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
```

- `.venv/bin/python -m pytest -q -rA tests/test_pca_drift_contracts.py -k "D7b or D7 or D2 or D3 or D4"`
  : D7b doit passer (rendu mémoire full imprime « n = 2000 »).
- `.venv/bin/python -m pytest -q tests/test_plot_figure_1.py` : vert.
- `.venv/bin/pyflakes experiments/figures/plot_figure_1.py` : silence, code 0.

## 4. Tâche 3 — re-render complet des figures FULL uniquement

Commande enregistrée dans `figure_manifest.json` (à lancer depuis la racine du worktree) :

```bash
.venv/bin/python experiments/figures/plot_figure_1.py \
  --input-dir results/pca_drift_benchmark/full_2000_20261101 \
  --tables-dir results/pca_drift_benchmark/tables/full_2000_20261101 \
  --output-dir <OUT_NEUF> --figure both --strict
```

Procédure :
1. Rendre dans un **répertoire neuf** (ex. `results/pca_drift_benchmark/figures/full_2000_20261101_fix_n_label`)
   : `OUTPUT_NOT_EMPTY` refuse d'écrire dans un répertoire existant.
2. Vérifier le nouveau répertoire : `verify_figures_dir` vrai, PNG/PDF/SVG cohérents,
   le texte des figures imprime « n = 2000 ».
3. Remplacer les deux anciens répertoires full par les nouveaux contenus en conservant
   les noms d'origine (`full_2000_20261101`, `full_2000_20261101_fix_smoke_no_claims`) ;
   les anciens octets restent dans l'historique git. **Ne touchez à aucun répertoire smoke.**
4. Le nouveau `figure_manifest.json` enregistre le nouveau hash du traceur et le nouveau
   `figures_fingerprint` : c'est attendu et documenté dans l'avenant.

## 5. Tâche 4 — vérifications globales

- `.venv/bin/python -m pytest -q tests/test_pca_drift_contracts.py` : 44 passed, 0 failed.
- `make check` : vert au complet (le fichier QA non suivi est alors intégrable).
- `git status` / `git diff` : modifications limitées à `experiments/figures/plot_figure_1.py`,
  les deux répertoires de figures full, et éventuellement `tests/test_pca_drift_contracts.py`
  si un ajustement de test est strictement nécessaire (à justifier).

## 6. Interdictions (maintenues malgré l'avenant)

- Aucune modification du runner, de l'assembleur, des tables, de `results/` hors les deux
  répertoires de figures full ; aucun re-run benchmark ; `trials.csv` full lu uniquement
  en lecture seule via `PCA_FULL2000_TRIALS` (`/home/m53/JEPA-full-2000/…`), sans copie ni lien.
- J1 (`results/e2/e2_cells.csv`, SHA `e315e537…0823`, 47 CRLF) et D8 (FAIL +5.2833 %)
  inchangés ; `PLAN.md`, `prompts/streams/`, `docs/DEVIATIONS.md` inchangés ; aucune
  dépendance modifiée ; aucun xfail ni skip ; aucune nouvelle expérience.
- **Aucun commit, aucune branche, aucun push** : git appartient à Codex.

## 7. Livraison attendue

Rapport en fin de session : commandes exécutées avec codes de sortie, hashs SHA-256
avant/après des répertoires de figures, `git diff --stat`, résultat de `make check`,
preuve que D7b imprime « n = 2000 » en full et « n = 40 » en smoke. En cas de défaut
nouveau non couvert par l'avenant : **STOP immédiat**, rapport sans rerun.
