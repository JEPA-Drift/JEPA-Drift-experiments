# Déploiement PCA full 2000 (worktree séparé)

Les deux fichiers opérationnels de ce paquet sont :

- `prompts/GO-stream-29-full-vibe.md` : GO d'amorçage et mandat Vibe ; ne remplace pas `GO-stream-29-vibe.md`.
- `ops/pca_full_2000.sh` : `check`, `run`, `audit`, `all`. Ne modifie pas les logiciels scientifiques.

Depuis le worktree `~/JEPA-full-2000`, créé à partir de `origin/main` :

1. Copier les deux fichiers aux chemins relatifs ci-dessus ; partager `.venv` via `ln -s ~/JEPA-Drift-experiments/.venv .venv` si nécessaire.
2. Créer une copie `configs/pca_drift_benchmark_full_2000_resources.yaml` du YAML original, avec uniquement `mem_limit_gib: 24.0` et `max_wall_minutes: 360.0`.
3. `bash ops/pca_full_2000.sh check` doit passer. Puis versionner prompt, script et copie YAML **avant** le run pour figer la provenance.
4. Depuis ce worktree, lancer `vibe --model large-4`, demander la lecture du GO et vérifier le niveau `high`. Après accord humain, lancer via tmux :
   `tmux new-session -d -s pca-full2000-20261101 -c "$HOME/JEPA-full-2000" 'bash ops/pca_full_2000.sh all > logs/pca_drift_benchmark/full_2000_20261101/operator-console.log 2>&1'`
5. Observer `tmux list-sessions` et les logs ; `operator_exit_code=0` avec deux manifests de tableaux scellés établit la clôture.
6. Si code 3 / BLOCKED_RESOURCE, relancer exactement la même commande (le script choisit `--resume` si partitions valides), sans toucher aux limites ressources.

`trials.csv` doit rester sur disque pour que `--strict` puisse auditer. Ne pas faire de `git add .` sur les artefacts scientifiques.
