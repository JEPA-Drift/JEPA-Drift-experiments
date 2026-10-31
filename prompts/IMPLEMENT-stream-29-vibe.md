# Mission Vibe — Stream 29, tableaux PCA jusqu'à livraison technique

GO D'EXÉCUTION EXPLICITE du chercheur pour Mistral Vibe `large-4` / `mistral-large-4`, thinking `high`. Lis d'abord `prompts/GO-stream-29-vibe.md`, puis le plan accepté `prompts/plans/plan-29.md`, son GO et ses précisions `prompts/GO-stream-29.md`, `AGENTS.md` -> `CLAUDE.md`, le prompt 29 et le contrat scellé du runner. Le GO Vibe du 2026-10-31 est postérieur aux anciennes mentions plan-only : **implémente maintenant le plan accepté**, sans refaire un plan ni attendre une nouvelle confirmation. Claude reste réservé aux plans et le stream 31 est en standby.

Tu es l'unique implémenteur dans ce worktree, branche `stream-29`, base fc533d003098a45c8ce533876642712d47038b31. Reprends les états présents sans reset/stash. Les fichiers de politique, plan, GO et revue déjà présents appartiennent à Codex : conserve-les. Aucune autre session ou délégation, aucun lancement des streams 30/31.

Applique TDD par groupes g1–g5 du plan : tests RED réellement lancés, puis code minimal et GREEN, avec journaux `logs/pca_drift_tables/tdd.log`. Les cas négatifs doivent distinguer entrée corrompue à refuser et véritable état bloqué/échec cohérent à conserver. Lis les aides et leurs callers ; réutilise les outils existants, sans bibliothèque ni couche générique supplémentaires. Utilise les outils natifs Vibe réellement exposés, lecture avant écriture ; n'invente pas de schéma d'outil Codex/Claude.

Le périmètre applicatif est exactement :
- `experiments/pca_drift_tables.py` ;
- `tests/test_pca_drift_tables.py` ;
- `docs/sections/pca_drift_tables.md` ;
- `docs/DEVIATIONS.md`, en ajout seul pour C-pca-tables-design, en français ;
- neuf fichiers sous `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/` ;
- `prompts/wrapups/wrapup-29.md`, anglais, six rubriques projet et hashes réels ;
- journaux ignorés `logs/pca_drift_tables/`.

L'entrée unique est `results/pca_drift_benchmark/smoke_predictive_v2_closeout/`, les sept fichiers /2 déjà scellés. **Ne lance jamais le runner**, un détecteur, une nouvelle simulation, un refit PCA, une recalibration ou un full. Ne lis aucun retour réel, même pour compléter une cellule manquante. N=239/H=250, n_cal=n_null=n_alt=40 : la bannière SMOKE_NO_CLAIMS et les notes d'effectif doivent rester visibles. Rien ici n'autorise une conclusion empirique à n=2000 ni une évaluation réelle post-2019.

Conserve en particulier les corrections de revue intégrées :
- metric_id est unique dans aggregates, mais sa répétition dans selection est normale ; FK et NA sont conditionnels au type/état, pas imposés à toutes les lignes ;
- les deux cohortes Covid restent distinctes et bloquées, avec mesures NA ; FROZEN.json présent ne suffit pas à autoriser une mesure réelle ;
- les diagnostics GAUSS ne requièrent pas de calibration/groupe d'essais à leur metric_id ; les CANDIDATE conservent I/V théoriques ;
- essais sur disque obligatoires, absence ou calibration incohérente refusées ; ne masque pas une corruption en remplaçant les chiffres par NA ;
- finitude exigée par metric_kind, sans exiger FPR dans ALT ou RMST dans HOLDOUT ; respecter les NA de la source ;
- séparer les espaces d'identifiants de cohorte ; les empreintes de contenu peuvent être égales ;
- réutiliser exactement les préfixes T1/T2 et le mélange T2(k20)/T3 ; aucun recalcul RMST/FPR ;
- q moyenne est la recette H3 vérifiée, pas le KL joint de population ; q covariance par axe reste NA et I_cov_joint reste non additif ; M en covariance est heuristique.

Le contrat `pca_drift_tables/1` doit être documenté avec noms et types effectifs des colonnes/clés, identifiants de méthode/objectif/famille, `row_id`/`block_id`, provenance/lignée, manifest et API `verify_output_dir(path)`, pour que le stream 30 puisse ensuite consommer les résultats sans reprendre les calculs. L'assembleur 30 n'est pas ton périmètre. Ne touche ni tools/check_prompts.py ni le master des prompts : le stream 31 reste suspendu.

Environnement obligatoire pour tout Python/test/commande : `.venv/bin/python` du projet, et PATH avec `.venv/bin` en premier. Le lanceur fixe OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg ; conserve-les avant tout import NumPy. Depuis un sous-répertoire, utilise le .venv partagé, sans inscrire de chemin serveur absolu dans les livrables. Aucune installation/mise à jour de dépendances ; pas de Python Trading seul.

Après GREEN et pyflakes ciblé, applique les commandes de §11.1 du plan :
1. rendu primaire neuf sous `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`, avec `--strict` ;
2. répétition neuve sous `logs/pca_drift_tables/repeat/`, mêmes entrées et options, `--strict` ;
3. mesure chaque rendu par `/usr/bin/time -v` dans les logs ;
4. compare les neuf fichiers octet par octet, manifest compris, vérifie hashes/lignée/identités, 180/220/44 lignes T1/T2/T3 pour l'entrée complète, refus d'écraser et absence de chemin serveur ;
5. E2 CRLF/SHA sur disque ET index, E3/D8 FAIL, sept entrées /2 inchangées ; préfixe existant de DEVIATIONS intact.

Ne lance pas make check global, indexer Graphify/jCodeMunch ou Git de mutation. Ne modifie pas le runner, configs, jepadrift/, dépendances, anciens résultats, scripts des autres streams ou fichiers Codex. Pas de journal dans les livrables suivis. Au plus trois tentatives de réparation pour une erreur d'infrastructure ; ne force jamais une convergence scientifique ou un résultat cible.

Quand le périmètre est terminé, remets un rapport factuel : fichiers modifiés, commandes RED/GREEN et nombres de tests, double rendu et comparaison, temps/CPU/RSS, hashes des neuf sorties, limites/NA/statuts, invariants et contrat prêt pour 30. Écris le wrapup anglais aux six rubriques du projet. La directive formelle de clôture et Git restent gérés par Codex. **Termine alors ton processus pour l'audit Codex**, sans lancer un autre stream, sans commit ni push. En cas de blocker réel, signale-le explicitement sans inventer de résultat.
