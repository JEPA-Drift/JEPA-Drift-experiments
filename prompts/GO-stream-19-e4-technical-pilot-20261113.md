# GO Codex — pilote technique de production E4, 13 novembre 2026

Autorité : GO 1 du chercheur dans `GO-stream-19-e4-full-20261112.md`, plan canonique et annexe, réceptions correctives.
Ce fichier autorise uniquement le pilote technique décrit ci-dessous. **Il n'active pas le GO 2 scientifique.**

Sources reçues : runner `402d23bf09a76c51f9dbcddaf4cd5edb3cbc476b14b42685871502e8b0826980`, tests
`d75d4350f0a3296605eec764169c28d860ce034ea14b427f6d5a373799008e79`, driver
`3ed5b9920dd3cb076369a55e1f532ffd4cdfbdf452d2cb3a7c535c837ace4af8`. Les quatre défauts résiduels sont clos par deux
revues en lecture seule ; Codex constate 155 PASS sans FAIL/SKIP, dont les trois anciens témoins RED. Les tests
officiels sont inchangés après cette réception. Le démarrage attend aussi un `make check` complet réussi avec torch
et PCA/G1, l'identité finale et les gardes disque. Les erreurs de collecte des copies d'audit temporaires sont conservées
dans le coût, puis corrigées par une extension d'archive sans modifier ni exclure les tests officiels.

## Enveloppe technique et séquence

- Plafond technique choisi : **21 600 CPU-secondes cumulées**, pilote ancien, ingénierie et tentatives inclus.
  Chaque appel du pilote passe `--cpu-ceiling-s 21600` au garde existant. Le plafond global reste 86 400 s. Un budget
  technique insuffisant impose arrêt et diagnostic ; aucune extension scientifique implicite.
- Imports des mesures déjà finalisées, avec provenance SHA et séparation tests/administration. L'export des tables
  d'import est lui-même une tentative administrative mesurée, finalisée avant les imports suivants. Aucun double compte.
- P1 : exactement neuf appels cost-kernels, 40 réplicats : Gaussian N8, Gaussian N500 et t7 N500, chacun dans les rôles
  calibration, holdout et alternative. Sorties exclusivement coûts/identité ; aucune performance de détection inspectée.
- Choisir 250 ou 125 à partir du coût, selon le critère de 900 s approuvé, puis figer P2. La grille, I*, H, alpha et
  tous les choix statistiques sont inchangés. Aucun repli de grille n'est appliqué.
- P2 : effectifs complets en mode COST_FIXTURE, K attendu 354 ou 690 ; barrière globale, interruption N500 alternative
  avant commit atomique, preuve tmp/sans final, recalcul, reprise jusqu'à code 10, verify, trois rejeux SKIPPED avec
  octets conservés, publication et audit autonome. Le wrapper réel `tools/run_e4_production.sh attempt` mesure chaque
  producteur ; les étapes du pilote sont séquencées séparément pour observer interruption et reprise.
- Rapports et preuves candidats puis finaux immuables, mesures de contrôle sans activation, coûts des queues comptables
  conservés. CPU/RSS/disque, octets finaux mesurés, bornes temporaires dérivées et pics non observés restent distincts.

Verrou partagé, `.venv`, environnement déterministe, 8 Gio, 30 minutes par appel et réserve disque de 1 Gio conservés.
Ne supprimer aucun artefact référencé par les preuves. Le bookkeeping stdlib non mesuré reste explicitement inconnu,
pas une mesure nulle. Le bilan final doit en porter la limite et toute borne justifiée séparément.

Après ce pilote seulement : bilan prévisionnel complet, contrôle d'identité, puis décision technique d'activation GO 2
dans l'autorisation conditionnelle déjà reçue. Aucun accès réel/privé/2020+, entraînement, J4 ou changement scientifique.

## Conditions de démarrage levées

R0009 : `make check` réussi, 37 PASS puis 1 308 PASS et les seuls 5 skips D4 attendus ; gardes torch et PCA/G1
exécutées, entrée PCA scellée vérifiée par SHA-256. Temps : 36,73 s puis 551,85 s ; GNU time : 586,60 + 30,61 =
617,21 CPU s, RSS maximal 3 838 968 Kio, sortie 0. Les trois sources reçues ci-dessus sont inchangées.
Le pilote technique peut commencer. Les erreurs de collecte R0008 (42,98 CPU s) restent comptées ; leurs archives
sont conservées avec leurs mêmes SHA sous l'extension `.py.source`. Le GO 2 reste inactif.
