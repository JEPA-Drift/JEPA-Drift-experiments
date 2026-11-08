# GO stream 21-R — contrat documentaire du runner global

Date : 8 novembre 2026. **GO Codex au titre du mandat délégué**, conformément à l'amorçage de continuation et à la demande autonome du chercheur. Aucune signature du chercheur ni autorisation scientifique n'est attribuée.

**GO DOCUMENTAIRE ACCORDÉ** au seul plan `prompts/plans/plan-21-R.md`, SHA-256 `0f838115917c0064f278a60141e07a2c0439ff608f9c7473d70b5f3a88884bc0`, avec sa « Décision GO intégrée ». Le NO-GO provisoire de la proposition native v0 est levé pour ce lot. Proposition native révisée et archivée à l'identique : SHA-256 `f3493029b7f6ede5bff7bde8926d37b83324f173779fae7a61adaf804c74d200`.

Base `26a2a5696a4412af8aceb6dbde3a9874e996aaad`, branche `stream-21-R`, session interactive `jepa-s21-R`, UUID `2142c482-a8fc-47e4-975b-dbf6c9bd1f80`. Même Opus 5.5, effort Max et contexte conservés. Aucun Agent/Task ni sous-agent. La session personnelle existante compte dans le plafond de deux Claude et reste intacte.

## Propriété et livrables

Claude peut créer et modifier uniquement :

1. `docs/sections/benchmark_runner_contract.md` : contrat anglais en douze sections, conforme à la proposition native révisée et aux précisions du plan canonique.
2. Journaux ignorés `logs/stream_21_R/` : contrôles documentaires, sorties et empreintes.
3. `prompts/wrapups/wrapup-21-R.md` : après revue Codex, attribution du créneau et invocation du wrap-up installé ; anglais et six rubriques du projet.

Codex possède le plan et le présent GO, l'inventaire de réception et toute la clôture. Lire le plan et le GO et relever leurs empreintes avant la première écriture. Lire tout fichier avant édition ; utiliser les outils d'édition natifs de la CLI, sans écriture manuelle par script ou shell.

## Arbitrages intégrés

- **YAML : restriction maintenue.** Refuser ancres, alias et étiquettes explicites, dont `!!str`, étiquettes locales et `%TAG`, par un futur refus CONFIG. Les types implicites compatibles avec les clés chaînes distinctes et les valeurs JSON finies restent admis. Distinguer construction syntaxique et caractère dans une chaîne littérale. Ne pas modifier le chargeur d'`appendix_b` ni écrire de chargeur maintenant.
- Les huit réponses à la revue sont reçues. Préserver la distinction entre `check().files` (nombre) et `snapshot.files` (dictionnaire), les limites de cohérence bornée, les variantes exactes, le cwd lié à ROOT, l'origine du code et les tentatives de sortie incomplètes.
- BLAS et dtype figurent dans l'identité proposée. Les descripteurs de protocole, de données et de preuve du lecteur, leur qualification et les mécanismes de collecte numérique et ORIGIN restent DEFERRED. Aucun exemple positif n'est présenté comme exécutable avec des champs nuls.
- Tous les candidats restent UNQUALIFIED ; le runner de production reste DEFERRED. Les futures identités attendues sont distinctes des octets effectivement vérifiés par un lecteur. Ni présence de FROZEN, ni chaîne de protocole, ni GO haché ne valent autorité scientifique.
- Appliquer les précisions du plan canonique sur les seuls échecs post-import, le suffixe `run_id[:16]`, les invariances limitées et les références factuelles versus chemins futurs. Les écarts `C-runner-*` restent proposés, sans changement de `docs/DEVIATIONS.md`.

## Validation et réception

Contrôles textuels et shell seulement : douze sections, langue, largeur, références factuelles, périmètre Git, empreintes du plan/GO/F et des scellés. Aucun Python, import, test applicatif, calcul ou simulation. Les futurs témoins de refus et de succès sont une spécification, jamais des résultats de tests.

Quand le document et les contrôles sont prêts, émettre `REVIEW_READY stream-21-R — awaiting Codex review`, puis rester sans édition ni exécution. Ne pas produire de wrapup avant le créneau explicite. Le contrôle complet, la réindexation, le commit et le push reviennent à Codex.

## Exclusions et intégrité

Aucun runner source, test nouveau, lecture de rendement, donnée privée ou 2020+, expérience E1/E3/E10/E4/E6/D6/PCA, entraînement JEPA/VAE, configuration E5, FROZEN réel, `make freeze` ni activation J4. Ne modifier aucune source, configuration, dépendance, mémoire, mapping ou sortie scellée. La date du 8 novembre ne vaut pas GO expérimental.

J1 disque/index : `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF, zéro LF isolé. E3 : `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, D8 reste FAIL. Manifeste PCA full : `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`.

Sortir du mode plan par le mécanisme officiel de cette même CLI, sans effacement du contexte ni bypass. Attendre le signal de démarrage après vérification du mode effectif par Codex. Après réception : wrap-up installé, arrêt contrôlé, réindexation AST sans résumé IA, `make check`, stage explicite, commit anonyme Conventional Commits sans trailer, audit de plage et push conforme. Aucun de ces actes de clôture n'est délégué à Claude.
