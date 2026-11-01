# GO inter-streams — Exécution synthétique full 2000 et tableaux PCA

**Date : 2026-11-01. Destinataire : Mistral Vibe `large-4`, niveau de raisonnement `high`.**

## Objet et autorisation

Décision explicite du chercheur : exécuter **uniquement le full synthétique** déjà autorisé dans `prompts/POLICY-PCA-PLAN-ONLY.md`, après l'intégration du stream 29 et avant la validation scientifique des figures du stream 30. Il ne s'agit **ni d'un nouveau stream 29**, ni d'une modification des streams 28, 29 ou 30. Les programmes scientifiques et les contrats de sortie sont gelés. Le chercheur assure lui-même l'orchestration et les opérations Git ; Vibe est opérateur de vérification et de lancement, pas intégrateur Git.

**Répertoire de travail obligatoire :** racine de `~/JEPA-full-2000`, branche locale `ops/pca-full-2000-20261101` créée depuis `origin/main` après l'intégration du stream 29. Ne pas récupérer, rouvrir ou réutiliser `~/JEPA-stream-29`. Ne pas intervenir sur `~/JEPA-stream-30` ni sur le worktree `main`.

## Périmètre autorisé

- Exécuter une seule fois le runner **existant** `experiments/pca_drift_benchmark.py --mode full --dataset synthetic` sur deux fonds, trois ruptures, `N=239`, `H=250`, `nmax=20`, quatre rôles de 2000 trajectoires, `seed=42`.
- Utiliser seulement la copie de configuration `configs/pca_drift_benchmark_full_2000_resources.yaml` qui diffère de la configuration intégrée par `mem_limit_gib: 24.0` et `max_wall_minutes: 360.0`. Les plafonds sont opérationnels et ne modifient pas l'identité scientifique. Si le temps est dépassé, `BLOCKED_RESOURCE` puis reprise **avec exactement le même fichier de configuration**, jamais contournement ou modification en cours de run.
- Conserver la reproductibilité : `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`, environnement `.venv` préexistant partagé, sans installation.
- Exécuter ensuite l'assembleur intégré `experiments/pca_drift_tables.py --strict --format both` **deux fois** dans des dossiers neufs ; vérifier l'identité octet par octet des neuf fichiers et `verify_output_dir`.
- Utiliser exclusivement le lanceur `ops/pca_full_2000.sh` préparé et auditable : `check` pour précontrôle, `all` pour run+tables, `audit` pour vérification/production après run scellé. Ne pas modifier les sources ou le lanceur pour faire passer un contrôle ; en cas de défaut, interrompre et signaler la cause.

## Interdictions

1. Aucun changement de `experiments/pca_drift_benchmark.py`, `experiments/pca_drift_tables.py`, `configs/pca_drift_benchmark.yaml`, `jepadrift/`, tests, prompts 28–31, politique du dépôt ou résultats historiques.
2. Aucune lecture de rendements postérieurs au 31 décembre 2019, aucune évaluation réelle, aucun `--dataset both|real`, aucune donnée EUROFIDAI.
3. Aucune réduction des effectifs, aucune simulation de remplacement, aucun GLR, aucune mutation du détecteur ou des seuils, aucun changement de seed ou de résultats déjà publiés.
4. Aucun `git add`, commit, push, merge, rebase, reset, stash, changement de branche ou suppression de worktree par Vibe ; ces actions reviennent au chercheur.
5. Aucun agent/subagent parallèle ni second processus full. Ne pas occuper le worktree actif du stream 30.
6. Conserver au bit près `results/e2/e2_cells.csv` sur disque **et dans l'index Git**, SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`; conserver l'échec historique E3/D8 et ses déviations.
7. Ne pas déclarer que `CPV90_OUTSIDE_TOP20` est une vraie baseline CPV90 évaluée ; conserver les statuts `UNSUPPORTED`, `BLOCKED_PRE_J4` et les réserves concernant la KL de covariance.

## Instructions opérationnelles de la session Vibe

**Phase A — Avant lancement.** Lire `docs/sections/pca_drift_benchmark.md`, `docs/sections/pca_drift_tables.md`, le `README` de ce GO, puis lancer `bash ops/pca_full_2000.sh check`. Vérifier le HEAD, les hashes des codes, la branche, le YAML et les ressources. Inspecter `tmux list-sessions` : ne pas démarrer de deuxième full si une session homonyme ou un processus runner full existe. Si le précontrôle échoue, **STOP avec le message précis**.

**Phase B — Lancement.** Avec l'accord explicite du chercheur dans la session, lancer une seule session `tmux` persistante nommée `pca-full2000-20261101` depuis le worktree autorisé, exécutant `bash ops/pca_full_2000.sh all`. Rediriger stdout/stderr dans `logs/pca_drift_benchmark/full_2000_20261101/operator-console.log`. Le processus doit survivre à la fermeture de Vibe et de SSH. Rapporter immédiatement l'identifiant de session et les commandes de surveillance (`tmux list-sessions`, `tail -n 50 -f ...`). Ne pas annoncer un succès avant `operator_exit_code=0` et présence des deux `table_manifest.json`.

**Phase C — Audit après fin de processus.** Lire `validation-summary.txt`, le log de durée/RSS, `TABLES_VALIDATION.md` et les trois CSV `Tableau_PCA_{1,2,3}.csv`. Vérifier que la sortie est `run_mode=full`, `n_center=n_cal=n_null=n_alt=2000`, que les sept sorties runner sont présentes, que les deux assembleurs sont identiques, et que les liens de métriques T1/T2/T3 sont valides. Faire un rapport chiffré synthétique (RMST, IC, FPR par fond/scénario, statut CPV90, méthodologies non disponibles), sans inventer ou forcer un gain. **Ne pas modifier automatiquement les figures du stream 30** ; informer le chercheur qu'une régénération depuis le full nécessite un ordre séparé.

**En cas d'échec.** Préserver les partitions, logs, fichiers et empreintes. `BLOCKED_RESOURCE` signifie qu'il faut la procédure `--resume` avec **configuration identique** ; le lanceur `all` sait détecter les partitions existantes. Le runner retourne 3 dans ce cas. Un refus 2, un `HASH_MISMATCH`, un YAML scientifique divergent ou un changement de code imposent un arrêt pour arbitrage du chercheur. Ne pas effacer les résultats existants.

**Livrables de cette opération :** sept artefacts de simulation sous `results/pca_drift_benchmark/full_2000_20261101/`, neuf artefacts de tableaux sous `results/pca_drift_benchmark/tables/full_2000_20261101/`, répétition dans le dossier `logs/`, logs temps et intégrité, compte rendu vérifiable. Il n'y a **aucune obligation de Git commit/push** des résultats avant l'audit et la décision explicite du chercheur.
