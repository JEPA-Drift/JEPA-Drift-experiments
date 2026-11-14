# Revue Codex — NO-GO technique E4 production v0

12 novembre 2026. Plan natif `plan-natif-e4-production-velvet-emerson.md`, 272 lignes, SHA-256
`e536126b7fe412c6b62aba1442ff31f8dc03572e326548f2bfbb272272d8e9cb`, archivé à l'identique dans le journal ignoré.
Base `b18d8e5`, session interactive `11902018-0502-44da-892f-5a80735c42b7`, Opus 5.5 Max. Revue de Codex et de deux
contre-relecteurs indépendants en lecture seule. Aucun code, test, pilote ou calcul scientifique n'a été exécuté.

**Décision : NO-GO technique v0.** Le GO 1 du chercheur reste acquis et le GO 2 conditionnel reste NON ACTIVÉ. Les
corrections ci-dessous sont des décisions d'ingénierie dans le périmètre autorisé ; aucun nouvel arbitrage scientifique
ni confirmation humaine n'est nécessaire pour réviser ce plan. Aucun GO d'implémentation n'est encore donné.

## R1 — Blocs et terminaison de la boucle hôte

La formule de dernier bloc (§3) produit `[2000,2000)` quand n est divisible par le bloc, ce qui inclut 250 et 125.
Définir les intervalles par `start in range(0,n,block)`, `stop=min(start+block,n)`, sans queue vide. Tester n divisible,
n non divisible, block=1, block=n, et le dernier réplicat.

La borne fixe de 600 invocations (§9) ne couvre pas les 690 partitions de la grille avec bloc=125. Dériver la borne du
plan exact et de la géométrie retenue, transmettre cette taille réellement choisie au pilote hôte, et exiger un code
de fin complet (10) plus les couvertures attendues. Épuiser la borne ou rencontrer une erreur ne doit jamais sortir
silencieusement en succès. Les cellules refusées restent traitées comme prévu, sans calmax interdit.

## R2 — Compteur CPU persistant et tentative en cours

`seq 1..600` et `time -o` réécrivent les anciennes mesures à chaque reprise, violant le plafond cumulé. Réserver un
identifiant de tentative unique, non écrasable, commun aux reprises, au pilote et à la campagne ; distinguer RUNNING,
COMPLETE et arrêt attendu du test d'interruption. Le gate appelé par le processus ne peut lire sa propre mesure GNU
time encore vide comme une tentative complète. Exclure seulement la tentative active explicitement identifiée ; une
ancienne tentative sans mesure finale impose une qualification inconnue/STOP, jamais zéro CPU.

Conserver les coûts de chaque échec, reprise et contrôle/rejeu, même sans CSV, plus 645,23 s antérieurs. Le budget avant
lancement doit couvrir la prochaine invocation et le reste prévu ; finaliser la mesure avant d'autoriser la suivante.
Tester une reprise qui conserve tous les anciens octets, un arrêt sans CSV, une mesure active inachevée et une ancienne
mesure inconnue. Aucun nom de tentative ne contient de statistique scientifique ou de trajectoire.

## R3 — Pilote P1 exécutable sans affaiblir les barrières scientifiques

P1 annonce des essais avec seuil fixture mais ne produit pas la partition thresholds exigée par les phases normales.
Définir une entrée de coût distincte, avec signatures/CLI, qui appelle les vrais noyaux et jette les charges utiles.
Le seuil de comparaison COST_FIXTURE est alors explicite et limité à cette entrée ; les phases scientifiques gardent
leur barrière globale réelle intacte. Corriger « comme _pilot_cell » : celui-ci calibre les dictionnaires et réserve
son seuil fixture de repli aux scalaires. Décrire les neuf invocations et leurs phases réellement mesurées.

## R4 — Pilote P2 complet et domaine PRNG valide

`cost_fixture` est un mode d'exécution, pas un domaine admis par `e4.key`. L'appel direct `e4.analyse(..., cost_fixture)`
échoue. Suivre `analysis_fixture` : domaine numérique pilot, avec `n={alternative:n_alt, holdout:n_hold}` explicitement
passé pour les tableaux aux effectifs complets ; le défaut pilot_n=40 serait incorrect. Séparer mode et domaine dans
les signatures et les identités. Ne modifier ni les domaines scientifiques ni les clés du producteur historique.

Avant thresholds/merge/analysis/publish, définir la génération de fixtures COMPLETE cohérentes pour scalar_cal, tous
les fit, tous les calmax et trials attendus, avec schémas, types, nombres de lignes et dépendances exacts. Les maxima
uniformes finis sont compatibles avec cell_calibration ; le problème est la couverture et la provenance, pas leur
distribution. Faire passer ces maxima indexés par la vraie barrière de rang, sans seuil de substitution en science.

Une échéance arbitraire de cinq secondes ne démontre pas une interruption : le bloc peut avoir fini. Définir un arrêt
fixture déterministe avant validation atomique ; observer un tmp sans final, puis le recalcul attendu, en conservant le
coût des deux tentatives. Cette interruption intentionnelle est distinguée d'un arrêt de ressource réel de la campagne.

## R5 — Activation liée aux preuves effectivement reçues

Des fichiers hachés étiquetés tests/pilote/GO et une chaîne « N passed » ne démontrent pas les contrôles du GO 1.
Définir des reçus structurés liés à l'identité actuelle code/configuration/environnement/graines : commandes et sorties
effectives, codes de retour, couverture des tests requis, phases du pilote complètes, reprise et interruption prouvées,
inventaires et liens aux tableaux CPU/RSS/volumes. Garder les journaux bruts comme feuilles hachées de ces reçus.

Vérifier ces contenus et l'égalité à l'identité courante avant activation. Prévisions/coûts doivent être finis,
non négatifs et réconciliés au ledger et aux volumes ; aucune valeur NaN ou preuve périmée ne passe. Un journal RED
historique ou une phrase narrative ne constitue ni un GREEN actuel ni un échec actuel. La non-fuite contrôle des
ensembles fermés de fichiers/champs et le statut fixture, sans confondre les paramètres et coûts légitimes avec une
performance. Tester preuves anciennes malgré SHA valide, phases manquantes, couverture insuffisante et coût NaN.

## R6 — Portée de l'invariance et borne de l'analyse

Préciser H3/T3 : octets identiques des tables scientifiques canoniques fusionnées et de leur manifeste final, à géométrie
logique identique. Les records physiques portant les bornes et hashes de blocs, ainsi que les mesures CPU, diffèrent
légitimement entre tailles de blocs. Ne pas demander simultanément des SHA de dépendances différents et des octets
physiques identiques. La couverture, les hashes logiques et les résultats doivent rester exactement comparables.

L'analyse peut reconstruire les premiers hits compacts aux effectifs fixés ; déclarer sa borne explicite, contrôler
couverture/unicité avant analyse et ne jamais charger les J_k globaux. Conserver exactement les deux lectures, pièces
neuves par méthode, EWMA par chemin, calibrations, appariement, refus et critères du prototype. Aucun défaut scientifique
inévitable n'a été trouvé dans cette partie du plan.

## R7 — Publication et stockage vérifiables sans la racine logs

La liste blanche de publication doit être exacte. Des partition.json publiés qui référencent des charges utiles restées
uniquement dans logs ne constituent pas des partitions publiées vérifiables. Conserver les charges utiles requises, ou
définir une représentation finale sans perte, avec correspondance explicite et vérifiable ; inclure les maxima requis
pour la traçabilité des calibrations. Prévoir aussi les reçus/preuves d'activation nécessaires pour auditer le résultat
à partir des artefacts publiés et sources commitées, sans dépendance implicite à des fichiers ignorés absents.

Publier un marqueur de complétude seulement après vérification de tous les éléments attendus. Une copie interrompue
doit être reprise sans écrasement divergent ni COMPLETE prématuré. Mesurer les coexistences blocs/fusion/publication/
objets Git et les temporaires avant l'activation ; toute hypothèse de marge reste explicitement une estimation.

## Arbitrages proposés et révision

250 réplicats et cible de 900 s, 125 si la prévision le requiert avant activation, réserve disque 1 Gio, seuil fragment
45 Mio et réserve de trois blocs interrompus : défauts techniques recevables, à vérifier au pilote. L'activation peut
vivre sous logs, avec une copie auditable dans la publication finale. Les 8 Gio, 30 min et 24 CPU-heures ne changent pas.

Réviser le plan natif dans la même CLI, au plus 350 lignes, sans nouveau tour d'exploration ni code/runtime/Git.
Budget : 15 minutes à partir du signal de révision. Fournir chemin, SHA-256 et correspondance R1–R7, puis attendre le
GO technique séparé. L'exception historique de présentation préalable au chercheur est levée ; Codex peut poursuivre
directement la revue. La campagne et la vague 23/27 restent non lancées.
