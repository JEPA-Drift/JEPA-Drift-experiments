# Revue de réception et GO technique résiduel — E4, 13 novembre 2026

**GO 1 non réceptionné ; GO 2 scientifique toujours inactif.** Cette revue porte sur la version corrective reçue :
runner `6c5e2a226b7d3d090d61129ea67cbd40d5ad1ec92acb372731ff9b7f97666920`, tests
`123ca7c79cfe7b79359c2a2979c545812962b134220479956f82b9850e93e1de`, driver
`41df126525fe4918c972d693f67bef9fefcea5d44864dde859f1dd32d0831cda`. Les trois fichiers sont archivés dans le journal
ignoré `received-v1-20261113/`. Le canonique et son annexe restent les références, sans nouvelle décision scientifique.

## Contrôles acquis

Codex a exécuté indépendamment les deux suites E4 : **148 PASS, aucun FAIL/SKIP, 55,53 s**, sous verrou et environnement
épinglé (R0005 : 55,62 + 8,98 = 64,60 CPU s ; RSS 220 764 Kio). Deux revues en lecture seule constatent que les noyaux
producteurs, jusqu'à la ligne 845, restent ceux de la version reçue. Les trois sources prototype/config/tests restent
inchangées. L'identité autonome R1, la preuve make check, la réconciliation détaillée du forecast, les trois évaluations
scalaires prévues et le driver K/code 10/code 9 sont reçus. La mesure sur preuve candidate est non circulaire et n'écrit
ni activation ni partition science.

Trois témoins supplémentaires sont RED, dans
`logs/stream_19_e4_production/codex-witnesses/test_import_and_pilot_residuals.py` ; commande, sortie et mesures R0006
préservées. Ce sont des fixtures isolées, pas une activation de la campagne E4. Leur CPU est 4,56 + 1,47 = 6,03 s.

## Quatre corrections résiduelles autorisées

1. **Imports réconciliés.** `read_imports` (lignes 858–873) ne rapproche pas CPU, nombre de lignes et identifiants du
   contenu CSV dont il vérifie pourtant le hash. Changer seulement `cpu_s` du JSON à zéro avant le premier snapshot
   sous-compte le budget sans refus. Recalculer ces faits depuis le CSV haché et les comparer ; tester CPU, rows et
   source_ids altérés. Le témoin Codex reproduit le défaut. Les anciennes sources restent immuables et un coût inconnu
   n'est jamais converti en zéro.

2. **Imports figés par instantané.** `consumed_through` (1565–1571) additionne tous les imports courants. Un import
   administratif ultérieur autorisé modifie donc rétroactivement les consommés des anciens cutoffs et fait refuser
   une activation inchangée. Le témoin reproduit ce refus. Utiliser l'appartenance des imports de chaque snapshot
   figé, notamment ceux du manifeste de rapport et de l'activation. Le ledger vivant compte toujours tous les imports
   ultérieurs pour son gate ; il ne les retranche pas du budget courant. Tester une queue après forecast et activation,
   une mutation du préfixe refusée, ainsi que le cas sans tentative mais avec imports.

3. **Complétude P2 des faits normalisés.** `_pilot_fact_problems` (1454–1466) ignore `p2.partitions` et sa géométrie.
   Le témoin montre qu'un nombre de partitions égal à zéro est accepté. Porter le bloc réellement attesté et exiger
   le nombre exact de partitions P2 ; réconcilier la géométrie avec le rapport/plan concerné dans les contrôles
   correspondants. Refuser champ absent, zéro, compte faux et géométrie contradictoire. La référence à la publication
   P2 doit être présente et de type SHA-256. L'audit autonome reste indépendant des journaux bruts.

4. **Volumes qualifiés correctement.** `_p2_volumes` (1598–1615) appelle `tmp_peak_bytes` la somme calculée du volume
   final et d'une taille CSV, et étiquette le tout MESURÉ. Ce n'est pas un pic temporaire observé ; la fusion ne fournit
   d'ailleurs pas ces tailles CSV dans ses objets. Distinguer les octets finaux mesurés, les bornes dérivées et les pics
   non observés dans les schémas et leurs labels. Un pic inconnu n'est ni zéro ni une mesure. Ajouter le témoin de cette
   distinction. Conserver les gardes disque et les plafonds.

Compléments mécaniques : retirer les quatre commentaires ordinaires d'en-tête du driver en conservant son shebang,
conformément au style du dépôt ; qualifier la séquence scalaire « une production + deux audits » dans le complément
DEVIATIONS. Aucun changement de logique scientifique ni nouvelle infrastructure.

## Périmètre et livraison

**GO technique Codex accordé** à ces corrections finies, dans la même session interactive, au titre du GO 1 du chercheur.
Même périmètre de code/documentation que le lot précédent. Journal avant code, RED puis GREEN sans affaiblissement,
mesures uniques W0033 et suivantes avec les commandes exactes ; verrou, `.venv`, variables déterministes et fixtures
bornées conservés. Au plus trois réparations du même défaut, puis arrêt déclaré.

Budget de cette passe : **45 minutes depuis le signal distinct**. Livrer à nouveau les SHA, JUnit des suites E4,
pyflakes, bash -n, journal et CPU réels, puis attendre réception. Aucun pilote réel, make check, reçu final, activation,
full, Git, wrapup, réindexation ou stream 23/27 par le worker.

Sous-total connu avant cette passe : **1 122,64 CPU s mesurées**. La lecture stdlib XML non mesurée déclarée dans le
journal reste une opération administrative distincte, de coût inconnu, jamais un import MEASURED à zéro. Conserver
cette limite dans le bilan ; toute borne proposée doit avoir une justification explicite. Les futurs appels de calcul,
tests et traitements des preuves utilisent les enveloppes mesurées. Le protocole scientifique est inchangé.
