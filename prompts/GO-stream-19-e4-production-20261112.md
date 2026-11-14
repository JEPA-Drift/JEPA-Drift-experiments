# GO technique Codex — E4 production, 13 novembre 2026

**GO 1 TECHNIQUE ACCORDÉ** au plan canonique `prompts/plans/plan-19-e4-production-20261112.md`, SHA-256
`22c71798b0bfd7b9cb396f30695ce991819a65c9983bc9ad2190798db2de6504`, dont les neuf précisions de la « Décision GO
intégrée » priment sur les raccourcis de la proposition native. Native v1 : 349 lignes, SHA-256
`1cdb3a6d1e86ca93045577ebffd732a27a76112634e50f0a91bd24ccd69e6099`, archive ignorée vérifiée par cmp.
Le NO-GO v0 `287a506a428ce13ec1f1b2e877c51a60a191168a6eb6a85a3a3b252fadb22764` reste une trace historique.

Autorité : décision explicite du chercheur reçue après `b18d8e5`, consignée dans
`prompts/GO-stream-19-e4-full-20261112.md`, SHA-256
`19d2697700bc9a0af5d98c9bd7c901129450aed385487582ef67c3f17e094746`. Codex exerce la revue technique déléguée.
Les deux revues indépendantes closent R1–R7 sous les précisions intégrées ; aucun arbitrage scientifique nouveau.
La précision 9 corrige la portée du writer plat avant tout démarrage ; son défaut a été confirmé par la revue source.
Les versions intermédiaires du canonique (90472e…) et de ce GO (14165a…) sont archivées dans le journal ignoré.

**Ce GO n'active pas le GO 2 full.** L'activation reste interdite avant preuves reçues, pilote technique, coût actualisé
dans 24 CPU-heures, ressources disponibles et identité finale. La vague 23/27 est différée jusqu'à E4 réussi et publié.

## Session, périmètre et séquence

Base `b18d8e5b01706bcb3dea8268c93fc0b9c361e441`, branche `stream-19-e4-production-20261112`, worktree natif réutilisé.
Même CLI `jepa-s19-e4-production-20261112`, UUID `11902018-0502-44da-892f-5a80735c42b7`, Opus 5.5 Max, aucun Agent/Task.

1. Lire le plan canonique et ce GO ; proposer la sortie officielle du mode plan dans cette même session. Attendre
   la vérification du mode et le signal distinct d'implémentation Codex avant toute écriture de code.
2. Créer seulement `experiments/e4_production.py` et `tests/test_e4_production.py`. Ajouter les deux entrées prévues à
   `docs/DEVIATIONS.md`, en français, sans réécrire l'historique. Tenir le journal anglais ignoré sous
   `logs/stream_19_e4_production/implementation-journal.md` avec RED/GREEN, commandes et limites effectives.
3. Préserver les trois fichiers du prototype, la configuration scientifique, tous les modules partagés, les dépendances,
   la mémoire, les hooks, Makefile, papier et scellés. Aucun accès aux données financières, privées ou 2020+.
4. Utiliser les skills installés de TDD/exécution. Tests signifiants et RED observé avant implémentation, puis GREEN,
   notamment les 22 contrats et les témoins ajoutés par le GO intégré. Pas de tests assouplis pour obtenir PASS.
5. Tous les calculs/tests sous le verrou partagé existant de l'arbre principal ; `.venv/bin/python` uniquement.
   Avant imports : OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42,
   MPLBACKEND=Agg, pont torch conda-forge existant conservé. Aucun pip/conda install.
6. Fixtures numériques N<=8, H<=60, n<=40, n_cal>=19 ; tableaux synthétiques explicitement COST_FIXTURE pour tester
   les compteurs et bornes, jamais des performances réelles. Les simulations grandeur finale, pilotes réels et reçus
   d'activation restent à Codex. Tests ciblés seuls : nouveaux tests et les 101 tests du prototype, avec JUnit et
   pyflakes des deux nouveaux fichiers. Pas de make check ni de campagne par le worker.
7. Budget : 120 minutes depuis le signal distinct, avec livrable préservé si incomplet. Trois corrections maximum
   du même défaut d'infrastructure/test, puis arrêt déclaré. Une rupture de reproduction scientifique ne se force pas.
8. Livrer IMPLEMENTATION_READY : fichiers/SHA-256, commandes et compteurs de tests réellement exécutés, JUnit, journal,
   état Git en lecture seule et limites. Arrêter les éditions pour réception. Aucun staging, commit, push, rebase,
   réindexation, wrapup, activation, full ou lancement des streams 23/27 par le worker.

## Précisions de démarrage et clôture

Les phases non scientifiques cost-kernels/cost_fixture/receipt/activate doivent pouvoir fonctionner avant l'activation,
avec gardes de ressources et budget technique borné ; elles ne doivent jamais exiger un faux forecast full pour
démarrer ni produire une partition science sans activation. Codex fixera l'enveloppe du pilote avant son lancement,
dans le plafond global inchangé. Les garde-fous full restent stricts si une preuve ou prévision est absente.

Après réception indépendante : contrôle global et non-fuite, nouveau pilote, bilan CPU/RSS/disque et reçus, puis
activation explicite par Codex seulement si tous les critères sont satisfaits. Aucun recalage de I*, de grille,
d'effectifs, de seuil de qualification ou d'estimand. Aucun repli automatique. Un blocage scientifique ou de ressources
effectif exige STOP motivé et retour au chercheur, conformément à son GO.

La clôture finale du lot exige les résultats scientifiques ou un arrêt formel, leur rapport et leur traçabilité,
wrapup installé, réindexation autorisée sans IA, tests, audit, commit et push contrôlés. Les étapes intermédiaires
d'ingénierie ne signifient pas que le stream 19 historique est entièrement terminé.
