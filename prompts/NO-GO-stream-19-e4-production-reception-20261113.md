# Revue Codex de réception — E4 production, 13 novembre 2026

**Réception GO 1 : NON ACQUISE. GO 2 scientifique : NON ACTIVÉ.**

Cette revue porte sur le script `experiments/e4_production.py`, SHA-256
`7deed3660d8fd9dfe066883d7b4282169790d6e62341c399d74e562c45b46aa3`, et les tests
`tests/test_e4_production.py`, SHA-256
`d83bd32c667b6230ccdcdaea95d3b5afd271509161331dc2d2fc317761e6803f`, reçus après le GO technique
`prompts/GO-stream-19-e4-production-20261112.md`. Les numéros de ligne ci-dessous désignent cette version.
Le plan et ses neuf précisions, le GO du chercheur et les sources du prototype restent les références.

## Éléments reçus et vérifiés

- Vérification Codex indépendante sous verrou : 140 tests réussis, aucun échec ni skip, en 44,43 s ; 101 tests du
  prototype et 39 nouveaux tests. GNU time : 47,58 s utilisateur + 5,68 s système ; RSS maximal 218 284 Kio.
- Les empreintes du prototype, de sa configuration et de ses 101 tests restent celles de `b18d8e5`.
- Deux revues indépendantes en lecture seule ne signalent pas de désaccord des noyaux scientifiques : clés et
  appariement globaux, calibration scalaire commune, barrière des seuils, pièces fraîches par méthode, trajectoires
  complètes, fusion canonique, refus de base et analyse appariée sont conservés.
- Trois témoins Codex sur fixtures bornées sont RED pour les défauts R1, R3 et R5 ci-dessous. Ce sont des contrôles
  d'ingénierie, pas des échecs de reproduction scientifique ni des observations de performance full.

Témoins locaux à intégrer aux tests autorisés :
`logs/stream_19_e4_production/codex-witnesses/test_publication_identity_gap.py` et
`logs/stream_19_e4_production/codex-witnesses/test_production_receipt_forecast_gaps.py`.
Commandes, sorties et mesures préservées dans `codex-runs/R0001`, `R0002` et `R0003` du même journal.

## Corrections bloquantes

### R1 — Identité de publication autonome

`verify_publication`, lignes 1078–1091, compare des chaînes `session_id` sans recalculer leur empreinte canonique ni
réconcilier domaine, mode et identités du plan, du manifeste, du lignage et des enregistrements producteurs.
Le témoin Codex change la graine de `session.json`, conserve son identifiant et actualise seulement son entrée dans
l'inventaire PUBLISHED : la vérification accepte cette publication incohérente.

Recalculer l'identité à partir du corps canonique ; contrôler mode/domaine et cohérence des artefacts porteurs
d'identité. Vérifier les empreintes des sources utilisées par l'audit avant d'annoncer leur vérification. Ajouter les
témoins de graine, mode/domaine, source et identité de lignage divergents. Aucune régénération scientifique nouvelle.

### R2 — Faits normalisés des reçus publiés

Les lignes 1080–1086 vérifient seulement les octets des reçus contre leurs SHA dans l'activation. Le test final,
lignes 1133–1146 des tests, accepte une activation factice à un seul reçu `tests` réduit à `kind` et `session_id`.
Cela ne satisfait pas la précision 8 du GO intégré.

Exiger l'ensemble prévu des quatre reçus lorsque l'activation est publiée et contrôler leurs faits normalisés :
type, identité, réussite, couverture des tests/pilotes et cohérence avec l'activation. Conserver l'audit autonome sans
accès aux journaux bruts omis de la publication ; les vérifications en ligne gardent leurs feuilles brutes. Remplacer
le témoin permissif par une fixture normalisée complète, puis tester les faits absents, étrangers ou contradictoires.

### R3 — Réconciliation de la prévision

`_forecast_problems`, lignes 1399–1426, vérifie une inclusion des partitions et l'arithmétique du total, sans vérifier
l'unicité et l'ensemble exact des partitions, la géométrie, `n_partitions`, ni la somme des coûts détaillés.
Le témoin Codex augmente un coût de partition de 100 s sans changer le total : aucune anomalie n'est signalée.

Réconcilier les identifiants, la géométrie, les comptes et les sommes avec les phases effectivement prévues, y compris
les phases de contrôle. Contrôler les valeurs finies non négatives et le plafond inchangé. Tester somme incohérente,
doublon, partition étrangère, bloc étranger et compte erroné. Les replis restent descriptifs, sans activation automatique.

### R4 — Coût des contrôles effectifs en full

Le full exécute `check_activation` et `_remaining` avant chaque invocation concernée (lignes 1828–1833), tandis que
les modes P1/P2 servant au coût fixe ne suivent pas ce chemin. La relecture des preuves et du préfixe du ledger n'est
donc pas comptée par leur simple transfert. En outre, chaque `verify_publication` régénère le scalaire, y compris
l'audit autonome et le rejeu de publication ; le forecast ne le charge qu'à `scalar_cal` et `phase:publish`.

Mesurer ou borner explicitement le coût des vérifications de preuves, avec un volume de ledger pertinent, et le
charger au nombre réel d'invocations full. Compter chaque audit scalaire obligatoire et les reprises effectivement
prévues. Distinguer MESURÉ, ESTIMATE et hypothèses non mesurées. Ne pas activer le GO full pour construire son propre
pilote de preuve ; utiliser les fonctions de vérification sur une preuve candidate explicitement technique, sans
écrire d'activation scientifique ni de partition science. Tester que les lignes de prévision couvrent ces appels.

### R5 — Preuve make check complète

`_make_check_problems`, lignes 1215–1225, accepte un seul résumé pytest positif. Le test d'activation emploie ainsi
un journal « 2 passed » pour attester make check. Le témoin Codex confirme cette acceptation.

Exiger les deux suites réussies du Makefile et la politique de skips approuvée ; un journal partiel ou un skip
inattendu doit être refusé. Les gardes torch et PCA/G1 doivent être exécutés dans la preuve réelle, conformément à
l'environnement épinglé. Ne pas modifier Makefile ni assouplir les tests globaux. Les fixtures de reçu doivent refléter
ce contrat complet plutôt que deux lignes arbitraires présentées comme une exécution réelle.

### R6 — Publication des mesures du pilote et coût cumulé

Le plan §7 prévoit les tentatives, coûts par étape et volumes publiés. `REPORT_FILES` et le writer, lignes 1266 et
1378–1379, ne livrent que les trois tables de prévision. Les partitions P1 locales et les colonnes `bytes/tmp_bytes`
ne remplacent pas le rapport de CPU, RSS, disque, reprise et sérialisation demandé.

Exporter les faits existants via les wrappers FAIR, avec schémas fermés, SHA et manifestes ; publier le registre des
tentatives sans perte et les tables de coûts par étape et de volumes. Séparer octets mesurés, maxima temporaires
observés et empreintes prévisionnelles. Aucun résultat de détection P1 ne doit être exporté ni inspecté.

Préserver et intégrer les mesures d'ingénierie avant le cutoff du forecast : 156,09 CPU s des 17 appels worker,
53,26 CPU s du contrôle Codex R0001, 1,50 CPU s de R0002 et 3,01 CPU s de R0003. Avec les 645,23 CPU s du pilote
publié, le sous-total mesuré à cette revue est 859,09 CPU s. Les futures mesures s'ajoutent ; aucun coût inconnu
n'est remplacé par zéro. Conserver la distinction entre producteurs, tests et bookkeeping administratif.

### R7 — Boucle hôte réellement vérifiée

Les tests utilisent un Host Python en processus, avec temps de fixture constants ; le journal déclare l'absence
de témoin pour la boucle shell K+1 et le code 9. Ce point est une lacune de vérification, pas un échec shell reproduit.

Vérifier le code hôte effectivement utilisé avec un producteur stub borné : K décimal valide avant l'arithmétique,
bloc reçu du plan, succès seulement sur code 10 suivi de verify, propagation d'erreur, borne épuisée → code 9,
anciens fichiers de tentatives inchangés après reprise. Une copie de la boucle dans un test ne suffit pas à vérifier
un autre driver. Si nécessaire, un unique script shell minimal peut matérialiser le driver approuvé ; aucune nouvelle
infrastructure générique, aucune modification scientifique ni changement des plafonds n'est demandé.

## GO technique correctif, distinct de l'activation scientifique

Les corrections R1–R7 sont autorisées au titre du GO 1 du chercheur, dans la même session interactive Opus Max.
Elles n'exigent pas de nouvel arbitrage scientifique. Avant les éditions, consigner dans le journal le périmètre
fini et les témoins RED prévus ; si un driver shell doit être ajouté, enregistrer son extension au plan avant son
implémentation. Les trois sources prototype/config/tests, dépendances, modules partagés et scellés restent intacts.

Périmètre : les deux nouveaux fichiers Python, les compléments documentaires strictement nécessaires et, si requis
pour R7, un seul driver shell minimal et ses tests. Éditions par l'outil natif ; tests ciblés uniquement sur fixtures
bornées, `.venv`, environnement déterministe et verrou commun. Chaque nouvelle invocation reste mesurée dans un
répertoire unique. RED puis GREEN observés, au plus trois corrections du même défaut avant arrêt déclaré.

Livrer de nouveau IMPLEMENTATION_READY avec SHA, commandes, JUnit, mesures cumulées et limites. Aucun pilote réel,
make check, reçu final, activation, campagne full, Git, wrapup ou stream 23/27 par le worker. Codex réceptionne les
corrections puis conserve ces étapes. Le GO scientifique conditionnel reste reçu mais inactif jusque-là.

**Transmission : en attente du rétablissement du plafond de deux instances Claude, toutes sessions comprises.**
La session E4 est au repos ; cinq autres sessions privées sont ouvertes. Aucune session privée n'est arrêtée ou
modifiée par Codex. Cette attente est une contrainte opérationnelle explicite du chercheur, pas une demande de GO
technique supplémentaire.

## Mise à jour — transmission autorisée le 13 novembre 2026

Le chercheur a précisé que le plafond est indicatif et ne concerne que les instances activement orchestrées par Codex ;
voir `prompts/GO-orchestration-parallelism-20261113.md`. L'attente opérationnelle ci-dessus est levée. Les corrections
R1–R7 et leur GO technique restent inchangés ; reprendre la conversation E4 conservée, sans toucher aux sessions privées.
Le sous-total mesuré de 859,09 s reste celui de la revue ; la comptabilité administrative R0004 ajoute 0,97 s, soit
860,06 CPU s connus avant la reprise. Ses preuves restent dans le journal ignoré, hors de l'instantané antérieur figé.
