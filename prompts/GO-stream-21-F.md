# GO stream 21-F — outil de gel sur fixtures synthétiques

Date : 7 novembre 2026. **GO Codex au titre du mandat délégué**, conformément à l'amorçage de continuation et à la demande autonome du chercheur. Aucune signature personnelle du chercheur n'est attribuée.

**GO TECHNIQUE ACCORDÉ** à `prompts/plans/plan-21-F.md`, SHA-256 `9546d4225d93c054e2867263b6a5cf0b63c934b159f25e2bcd5c865062a1a34e`, avec sa « Décision GO intégrée ». Cette décision lève le NO-GO de révision 0 pour ce seul lot. Source native révisée et archivée à l'identique : SHA-256 `3b8a72a31b2d87793ca38d9636d86d24783fcff16ee8fa6423a259d4f504a086`.

Base `47d85dc977547409fc6f6d71dcf5488eb935d7d5`, branche `stream-21-F`, session interactive `jepa-s21-F`, UUID `921f284c-d6ae-4f31-b270-3f881fb33718`. Même Claude Opus 5.5, effort Max, contexte conservé. Aucun Agent/Task ni sous-agent. La session personnelle existante compte dans le plafond de deux Claude et reste intacte.

## Livrables et propriété

Claude peut créer et modifier uniquement :

1. `tools/freeze_config.py` : standard library seule ; API et CLI du plan ; schéma canonique `jepadrift-freeze/1` ; onze racines requises, SHA-256 des octets et identité Git ; historique C/S ; approbation comme provenance ; refus fermés et gardes limitant l'écriture aux fixtures.
2. `tests/test_freeze_config.py` : dépôts Git synthétiques temporaires, fixtures indépendantes du code testé, cas positifs et refus du plan, sans données réelles ni contenu privé.
3. `prompts/wrapups/wrapup-21-F.md` : seulement après revue et attribution du créneau de clôture ; anglais et six rubriques du projet.
4. Journaux ignorés de `logs/stream_21_F/`, dont RED/GREEN, mutations, contrôles et empreintes des quatre fichiers Codex.

Codex possède le plan, le présent GO, le NO-GO historique, le rapport d'inventaire et toute la clôture Git. Ces quatre documents sont lus et leurs empreintes relevées avant la première écriture du lot ; Claude ne les modifie pas. Lire tout fichier avant édition ; utiliser les outils d'édition natifs de la CLI, jamais de substitution `sed -i` ni d'écriture manuelle par script ou shell.

## TDD et validation

- Charger et appliquer `test-driven-development` depuis Superpowers avec les outils effectivement exposés dans cette CLI. Aucun code d'implémentation avant les témoins RED ; aucune erreur de collecte ou de montage comptée comme preuve.
- Appliquer les réponses du plan à K1–K3, W9/W10, à la liste des fichiers Codex et au gel unique. Les précisions finales du plan sur LINK/ENOTDIR, les courses et les mutations priment sur toute ambiguïté du texte natif.
- Après RED observable, implémentation minimale puis GREEN des cas prévus, sans skip ni xfail dans le nouveau fichier. Les seize mutations portent sur les invariants ; ne pas supprimer une garde pour obtenir un nombre. Toute équivalence réelle est documentée et soumise à Codex avant réception.
- Exécuter les contrôles ciblés et pyflakes du plan. Le seul appel applicatif sur le dépôt réel est `--check`, en lecture seule, avec refus ABSENT attendu. Ne jamais y appeler `write` ni `--write`.
- Conserver les commandes, sorties, codes retour, durées et SHA-256. Dépassement des ressources du plan ou blocage d'infrastructure : signaler, sans boucle d'attente ni installations. Au plus trois corrections bornées pour un même problème d'infrastructure, puis gel déclaré. Le RED intentionnel n'est pas une tentative de reproduction scientifique.
- Quand les contrôles ciblés sont prêts : `REVIEW_READY stream-21-F — awaiting Codex review`, puis attente. Le `make check` complet revient à Codex ; aucune clôture ou mutation Git du dépôt réel par Claude. Les opérations Git nécessaires aux seules fixtures temporaires sont autorisées.

## Exclusivité et environnement

Avant chaque exécution applicative, lire le registre existant `~/JEPA-Drift-experiments/logs/orchestration_20261107/execution-19-21-state.json`. Exiger `science_owner == "stream-21-F"` et `closeout_owner == null`. La commande est exécutée sous le verrou indiqué dans ce registre, avec `flock -n`. Si indisponible, signaler et poursuivre seulement les lectures ou éditions autorisées ; aucune attente active.

Interpréteur du worktree : `.venv/bin/python`, avec `-B` pour les témoins prévus ; `PATH` commence par le `.venv` partagé. Environnement avant tout import : `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. Aucun changement des dépendances, du pont torch ou des environnements partagés.

La sortie du mode plan utilise le mécanisme officiel de cette même CLI, sans effacement du contexte ni bypass-permissions. Codex vérifie le changement effectif avant de transmettre le démarrage de l'exécution.

## Exclusions et intégrité

Aucun `configs/FROZEN.json` réel, cible `make freeze`, activation J4, câblage de garde, runner, lecture de rendements, accès 2020+, entraînement JEPA/VAE, E4, E6/D6, nouvelle campagne PCA ou régénération de sortie scellée. Le schéma du lot est à usage unique sur une lignée et n'est pas une approbation du protocole futur.

Ne modifier aucun fichier existant sous `configs`, `experiments`, `jepadrift`, `results`, `paper`, ni Makefile, mémoire, DEVIATIONS, MAPPING, autre outil ou autre test. Les chemins propriétaires ne sont ni parcourus ni journalisés ; les pièges synthétiques du plan ne contiennent aucune donnée.

J1 disque/index : `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF, zéro LF isolé. E3 : `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, D8 reste FAIL +5,2833 %. PCA full : manifeste `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`. Toute divergence scientifique scellée impose un arrêt et un constat, jamais une modification destinée à forcer PASS.

## Clôture réservée

Après revue de l'implémentation, Codex attribue le créneau de wrapup installé. Puis arrêt de la session contrôlée, réindexation AST sans résumés IA, contrôle complet avec torch et G1 actifs, stage explicite, commit anonyme Conventional Commits sans trailer, audit de toute la plage et push conforme au protocole du projet. Le GO ne délègue pas cette séquence à Claude.
