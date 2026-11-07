# Avenant chercheur — stream 31 : levée ciblée de l'invariant d'amorçage n°2 et correctif D7b

Date : 2026-11-06. Émetteur : le chercheur. Destinataire : Codex (orchestrateur).
Base : worktree `/home/m53/JEPA-stream-31`, commit `20ad9e860a58373ec85405de6ee19a68322dd02e`.
Références : `docs/audits/PCA_CONTRACTS_VALIDATION.md` (STOP, 43 passed / 1 failed D7b),
`prompts/plans/plan-31.md`, `prompts/GO-stream-31.md`, `prompts/NO-GO-stream-31.md` (Q5),
`prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_06.md` (invariant n°2).

## 1. Constat retenu

D7b (`test_full_figure_text_sample_sizes_match_manifest`) échoue sur un défaut producteur
confirmé : « (n = 40) » en dur dans `experiments/figures/plot_figure_1.py:582`. Le manifeste
smoke déclare `n_cal = n_null = n_alt = 40` ; le manifeste full déclare 2000 par rôle.
Défaut d'étiquette cosmétique : les valeurs tracées sont intègres (D3). PDF/SVG/PNG sont
rendus depuis le même objet `Figure` (`plot_figure_1.py:688-690`) : libellé uniforme,
aucune divergence entre formats.

**Point tranché n°1 — les répertoires smoke n'ont pas le problème.** En smoke, n = 40 est
l'effectif réel du run (manifeste smoke), donc le libellé y est correct ; D7b ne contrôle
que les rendus FULL, et aucun test ne porte sur le texte des figures smoke. Avec le
correctif rendre le « n » dépendant du run, un re-render smoke produirait un contenu
identique (n = 40 lu du manifeste). **Les répertoires smoke ne sont donc pas re-rendus.**

## 2. Décision du chercheur

1. **Levée explicite et ciblée de l'invariant n°2** de l'amorçage pour ce seul cas :
   autorisation de remplacer les deux répertoires de figures **full** scellés,
   `results/pca_drift_benchmark/figures/full_2000_20261101` et
   `results/pca_drift_benchmark/figures/full_2000_20261101_fix_smoke_no_claims`,
   par un re-render complet depuis les tables scellées, avec nouveau `figure_manifest.json`.
   Les répertoires smoke, les tables, le runner et tout le reste de `results/` restent scellés.
   Les anciens octets demeurent dans l'historique git.
2. **Correctif code autorisé sur la seule ligne `plot_figure_1.py:582`** : le « n = x »
   imprimé devient une valeur dérivée du manifeste du run (2000 en full, 40 en smoke),
   plus aucune constante.

**Point tranché n°2 — délégation de l'implémentation.** L'implémentation du fix est déléguée
à une **instance Claude Code (Opus) en CLI**, sous supervision de Codex (GO, revue, git).
Justification : le lot 2 du stream 31 a été exécuté sous Opus 5.5 avec les workflows
superpowers `executing-plans` + `test-driven-development` (plan-31 v2, GO-stream-31) ;
reprendre le même harness réduit le risque de dérive des contrats. Le prompt d'implémentation
(`prompts/31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md`) est volontairement **agnostique du modèle**
et ne nomme aucun outil, afin de rester réutilisable par toute instance CLI de vibe coding.

## 3. Ce qui reste scellé (inchangé)

Runner, assembleur, tables, répertoires de figures smoke, `results/` hors les deux
répertoires de figures full, J1 (`e315e537…0823`, 47 CRLF, disque = index), D8 FAIL
+5.2833 %, `PLAN.md`, `prompts/streams/`, `docs/DEVIATIONS.md` (sauf entrée dédiée D7b si
requise), dépendances, `.venv`. Pas de re-run benchmark (runner/tables jamais réexécutés) ;
`trials.csv` full lu uniquement en lecture seule via `PCA_FULL2000_TRIALS`, sans copie ni lien.
Git, commits, revue : Codex uniquement. Aucun xfail ni skip.

## 4. Séquence exigée

1. Plan séparé + GO séparé (Codex) avant toute mutation.
2. Correctif ligne 582 ; preuve : rendu mémoire full imprime « n = 2000 », smoke « n = 40 » ;
   D7b passe ; `tests/test_plot_figure_1.py` toujours vert.
3. Re-render complet des figures **full uniquement**, depuis les tables scellées, commande
   enregistrée dans le manifeste :
   `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 .venv/bin/python experiments/figures/plot_figure_1.py --input-dir results/pca_drift_benchmark/full_2000_20261101 --tables-dir results/pca_drift_benchmark/tables/full_2000_20261101 --output-dir <OUT> --figure both --strict`
   avec le préfixe `export PATH="$PWD/.venv/bin:$PATH" … MPLBACKEND=Agg`. `OUTPUT_NOT_EMPTY`
   (`plot_figure_1.py:896`) interdit d'écrire dans un répertoire existant : rendre d'abord
   dans un répertoire neuf, vérifier, puis remplacer les deux anciens répertoires full
   (noms conservés, donc aucun changement de chemins dans les tests).
4. Vérifications : `verify_figures_dir` vert sur chaque répertoire de figures ; nouveau
   `figure_manifest.json` (nouveau hash du traceur, nouveau `figures_fingerprint`) ;
   PNG/PDF/SVG cohérents entre eux ; `make check` complet vert (le fichier QA peut alors
   être commité) ; pyflakes propre.
5. Mise à jour de `docs/audits/PCA_CONTRACTS_VALIDATION.md` : D7b passé, nouveaux SHA-256
   des sorties, annotation « `c40a5e77…` hash historique du traceur », puis commit par Codex.
6. Rapport final : hashs avant/après, `git diff`, commandes exécutées, codes de sortie.

## 5. Arrêt

STOP immédiat sur tout défaut nouveau non couvert par ce périmètre ; aucun rerun après STOP ;
aucune reformulation de contrat pour forcer un PASS.
