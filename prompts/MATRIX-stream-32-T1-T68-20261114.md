# Stream 32 — matrice exhaustive T1–T68

18 novembre 2026. B1a–B1n reçus comme composants. B2a–B2w reçus et B2 complet reçu sur fixtures sous GO B-TDD.
Autorité : `16_CODEX_GO_STREAM32_B_TDD_REVIEW_20261114.md` et `GO-stream-32-B-20261114.md`.
Plan v2.1 canonique inchangé. Cette matrice sera actualisée à chaque réception, jamais réduite.
Consigne chercheur du16novembre : arrêter cette instance après réception complète B2 et
rédiger le prompt de reprise ; aucune activation B3/B4 par cette instance.

Statuts autorisés : PASS, FAIL, NOT_RUN, DEFERRED_TO_C_RUNTIME. Un contrat partiel reste NOT_RUN,
avec preuve de sa partie reçue indiquée. « À écrire » désigne un témoin attendu, pas un test exécuté.
C0 : `.venv/bin/python -m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`,
sous environnement déterministe et verrou partagé. C0 historique B2w GREEN final, **840 passés en 19,85 s**.
Pytest exit 0, contrôles exit 0, pyflakes et diff-check propres. Contrôle direct des rangs DEV et trois refus dans les contrôles.
Preuves `logs/stream-32/lot-B2w-green-final.pytest.log` et `lot-B2w-green-final.checks.log`.
RED B2w consolidé 31 échecs ciblés et 807 passés. RED groupé 33 échecs ciblés et 807 passés en 34,98 s.
GREEN v1 jamais appliquée. V2 et correction de rang relues, assemblées et appliquées une seule fois.
Source finale `936afa0c`, tests `73e931a1`, scellé `8324b47b`. Réception B2w et bilan B2 écrits séparément.
T33, T37 et T51 passent. T34 et T41 restent partiels à cause des raccordements B3/B4.

19 novembre 2026. B3a reçu sur fixtures. C0 RED 14 échecs attendus et 840 passés en 30,39 s.
C0 GREEN 854 passés en 20,43 s, pyflakes et diff-check propres. T43 passe. Total 22 PASS, 46 NOT_RUN.
Preuves dans `RECEIPT-stream-32-B3a-20261119.md` et `logs/stream-32/lot-B3a-green.pytest.log`.

19 novembre 2026. B3b reçu sur fixtures. RED 2 échecs attendus et 854 passés en 24,44 s.
GREEN 856 passés en 21,09 s, pyflakes et diff-check propres. La matrice garde 22 PASS, 46 NOT_RUN.
Voir `RECEIPT-stream-32-B3b-20261119.md` et `logs/stream-32/lot-B3b-green.pytest.log`.

19 novembre 2026. B3c reçu sur fixtures. RED 2 échecs attendus et 856 passés en 25,66 s.
GREEN 858 passés en 21,74 s, pyflakes et diff-check propres. Total 22 PASS et 46 NOT_RUN.
Voir `RECEIPT-stream-32-B3c-20261119.md` et `logs/stream-32/lot-B3c-green.pytest.log`.

19 novembre 2026. B3d reçu sur fixtures. RED 2 échecs attendus et 858 passés en 26,77 s.
GREEN 860 passés en 23,00 s, pyflakes et diff-check propres. T32 passe. Total 23 PASS et 45 NOT_RUN.
Voir `RECEIPT-stream-32-B3d-20261119.md` et `logs/stream-32/lot-B3d-green.pytest.log`.

19 novembre 2026. B3e reçu sur fixtures. RED 2 échecs attendus et 860 passés en 28,53 s.
GREEN 862 passés en 25,11 s, pyflakes et diff-check propres. T23 et T24 passent.
Total 25 PASS et 43 NOT_RUN. Voir `RECEIPT-stream-32-B3e-20261119.md`.

19 novembre 2026. Lot B3 reçu sur fixtures déterministes après les réceptions B3f à B3m.
C0 final sous verrou 1003 passés en 39,80 s, pyflakes et diff-check propres.
Total 34 PASS, 34 NOT_RUN. Les contrats partiels gardent leur statut, dont T34 et T41.
Voir `RECEIPT-stream-32-B3-20261119.md` et `logs/stream-32/lot-B3m-green.pytest.log`.

20 novembre 2026. B4a reçu sur fixtures déterministes. C0 RED 5 échecs attendus sur `main` absent
et 1 003 passés en 46,95 s. C0 GREEN 1 008 passés en 40,23 s. Vérification du CLI direct et module,
refus OMP parent, pyflakes et diff-check réussis. T52 passe. Total 35 PASS et 33 NOT_RUN.
Voir `RECEIPT-stream-32-B4a-20261120.md` et `logs/stream-32/lot-B4a-green.final-checks.log`.

20 novembre 2026. B4b reçu sur fixtures déterministes. C0 RED 4 échecs attendus sur
`partition_plan` absent et 1 008 passés en 46,41 s. C0 GREEN 1 012 passés en 41,26 s.
Inventaire des six phases conforme aux partitions engagées. T41 reçoit cette preuve partielle,
dont la réservation HOLD jusqu'au plafond. Le driver et la consommation des rôles restent dus.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4b-20261120.md`.

20 novembre 2026. B4c reçu sur fixtures déterministes. C0 RED 5 échecs attendus sur
`score_path_batch` absent et 1 012 passés en 48,05 s. C0 GREEN 1 017 passés en 44,56 s.
Scores EXACT et FITTED identiques avec jobs1/3, refus parent/enfant et échéance testés.
T44/T46/T62 gardent un statut partiel. Total 35 PASS et 33 NOT_RUN.
Voir `RECEIPT-stream-32-B4c-20261120.md` et `logs/stream-32/lot-B4c-green.checks.log`.

20 novembre 2026. B4d reçu sur fixtures déterministes. C0 RED 2 échecs attendus
et 1 017 passés en 48,96 s. Une régression DEV_LIB a écarté la V1. C0 GREEN V2
1 019 passés en 44,96 s. CPU et mur vérifiés après encodage et avant écriture,
avec maintien de la borne entre lots DEV_LIB. T46/T62 gardent un statut partiel.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4d-20261120.md`.

20 novembre 2026. B4e reçu sur fixtures déterministes. C0 RED 1 échec attendu
de routage et 1 019 passés en 50,02 s. C0 GREEN 1 020 passés en 46,46 s.
Les six rôles transmettent leurs clés, les deltas, les jobs et l'échéance.
La reprise conserve les octets engagés. T41/T44/T46/T62 restent partiels.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4e-20261120.md`.

20 novembre 2026. B4f reçu sur fixture synthétique. RED 1 échec attendu et 1 020 passés en 50,77 s.
GREEN V2 1 021 passés en 55,31 s. Deux stagings indépendants à 1 et 3 workers ont les mêmes
octets engagés pour les six phases et 13 partitions. La reprise complète ne recalcule aucun score.
T44/T45/T47/T56/T57 reçoivent une preuve partielle. Total 35 PASS et 33 NOT_RUN.
Voir `RECEIPT-stream-32-B4f-20261120.md`.

20 novembre 2026. B4g reçu sur fixture synthétique. RED 1 échec attendu sur le statut absent et
1 021 passés en 59,50 s. GREEN 1 022 passés en 55,55 s. L'échéance CAL consigne `BLOCKED_RESOURCE`,
la charge CPU simulée et les trois partitions manquantes. La reprise conserve SETUP et DEV
et rejoint les octets de la référence. T45/T46/T57/T62 restent partiels. Total 35 PASS et 33 NOT_RUN.
Voir `RECEIPT-stream-32-B4g-20261120.md`.

20 novembre 2026. B4h reçu sur fixture synthétique. RED 1 échec attendu et 1 022 passés en 60,40 s.
GREEN 1 023 passés en 55,91 s. Le CSV FAIR CAL reprend les seuils engagés, leurs SHA et la
qualification de l'oracle. Inverser l'ordre du record restitue les mêmes octets. T16 reste partiel.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4h-20261120.md`.

20 novembre 2026. B4i reçu sur fixture synthétique EXACT et FITTED_LW_T7. RED 1 échec attendu
et 1 023 passés en 60,22 s. GREEN V2 1 024 passés en 56,23 s. Six lignes de sélection
depuis les masques ALT engagés concordent avec la référence. T16/T39/T42/T49 restent partiels.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4i-20261120.md`.

20 novembre 2026. B4j reçu sur fixture synthétique. RED 1 échec attendu et 1 024 passés en 61,34 s.
GREEN V2 1 025 passés en 57,37 s. Le résumé FAIR de quatre cellules conserve les premiers franchissements
via les références de partitions, la censure, les RMST et les bornes HOLD. T16/T19/T49 restent partiels.
Total 35 PASS et 33 NOT_RUN. Voir `RECEIPT-stream-32-B4j-20261120.md`.

20 novembre 2026. B4k reçu sur fixture synthétique. RED 1 échec attendu et 1 025 passés en 61,08 s.
GREEN V2 1 026 passés en 57,20 s. Le CSV descriptif V/RMST vérifie les SHA sources, joint les
cellules ALT concordantes et restitue les deux corrélations. T49 passe. Total 36 PASS et 32 NOT_RUN.
Voir `RECEIPT-stream-32-B4k-20261120.md`.

20 novembre 2026. B4l reçu sur fixture synthétique. RED 1 échec attendu et 1 026 passés en 62,69 s.
GREEN 1 027 passés en 58,33 s. Les cinq CSV sont publiés, 13 NPZ restent locaux et le rejeu
conserve les octets. T16, T50 et T59 passent. T60 reste partiel. Total 39 PASS et 29 NOT_RUN.
Voir `RECEIPT-stream-32-B4l-20261120.md`.

20 novembre 2026. B4m reçu sur fixture synthétique de bout en bout. RED 1 échec attendu
et 1 027 passés en 62,56 s. GREEN V2 1 028 passés en 67,49 s. Les publications à 1 et
3 workers ont les mêmes octets scientifiques. Le conflit de logs par défaut est refusé.
La reprise après FINAL ne recalcule ni scores ni exports. T44 et T56 passent.
Total 41 PASS et 27 NOT_RUN. Voir `RECEIPT-stream-32-B4m-20261120.md`.

20 novembre 2026. B4n reçu sur deux interruptions synthétiques autour du renommage
atomique de la publication CLI. C0 compte 1 030 tests passés en 72,38 s. La reprise
avant renommage reconstruit le temporaire. Après renommage, les fichiers publiés
restent intacts et FINAL est écrit sans export. T60 et T61 passent.
Total 43 PASS et 25 NOT_RUN. Voir `RECEIPT-stream-32-B4n-20261120.md`.

20 novembre 2026. B4o reçu sur fixtures synthétiques FITTED_LW_GAUSSIAN. C0 compte
1 032 passés en 74,30 s. Les GO de pilot et full ne citent que le design pré-exécution
et sa portée. Les manifestes lient les réalisations calculées à la publication.
NULL_PLAN est inapplicable en pilot et engage une partition en full avec n_hold=5.
T53 passe. Total 44 PASS et 24 NOT_RUN. Voir `RECEIPT-stream-32-B4o-20261120.md`.

20 novembre 2026. B4p reçu sur fixture full synthétique. C0 compte 1 036 passés
en 78,98 s. Les reprises après SETUP, DEV, CAL et NULL_PLAN conservent la réalisation,
les octets durables et les octets scientifiques de la référence. Aucun score engagé,
choix DEV ou seuil CAL n'est recalculé. T57 passe. Total 45 PASS et 23 NOT_RUN.
Voir `RECEIPT-stream-32-B4p-20261120.md`.

20 novembre 2026. B4q reçu sur sept refus CLI de reprise sur staging altéré.
C0 compte 1 043 passés en 83,59 s. Chaque refus conserve tous les octets du staging
et de la publication, avant ouverture d'une invocation de reprise. T45 et T58 passent.
Total 47 PASS et 21 NOT_RUN. Voir `RECEIPT-stream-32-B4q-20261120.md`.

20 novembre 2026. B4r reçu aux bornes CPU et mur après export sur fixture.
C0 compte 1 045 passés en 88,44 s. Le CLI bloque les deux publications et conserve
la charge CPU. La reprise après échéance mur retrouve la référence. T46 et T62 passent.
Total 49 PASS et 19 NOT_RUN. Voir `RECEIPT-stream-32-B4r-20261120.md`.

20 novembre 2026. B4s reçoit cinq refus à l'admission du pilote de phases.
C0 compte 1 050 passés en 86,77 s. Aucune écriture, consommation de graine,
création de pool ni exécution de phase. T47 passe. Total 50 PASS et 18 NOT_RUN.
Voir `RECEIPT-stream-32-B4s-20261120.md`.

20 novembre 2026. B4t reçoit les contrôles AST du périmètre synthétique et du
descripteur. C0 compte 1 052 passés en 87,67 s. Le CLI publie sur fixture full
sous les pièges d'accès aux données. Le descripteur et le YAML ignorent les sorties
précédentes. T48 et T68 passent. Total 52 PASS et 16 NOT_RUN.
Voir `RECEIPT-stream-32-B4t-20261120.md`.

20 novembre 2026. B4u reçoit l'isolation non-oracle par AST et fixture ALT.
C0 compte 1 054 passés en 88,70 s. Six métadonnées ALT sont empoisonnées après
production des scores. Les sorties scientifiques et le staging gardent les mêmes
octets. T25 et T38 passent. Total 54 PASS et 14 NOT_RUN.
Voir `RECEIPT-stream-32-B4u-20261120.md`.

20 novembre 2026. B4v reçoit la publication des trois lignes confirmatoires H1–H3
dans aggregates.csv. RED confirme un raccordement manquant. Après correction du type
de la clé dans le test, C0 compte 1 055 passés en 90,00 s. La fixture engage cinq
trajectoires HOLD et conserve le statut nul inconclusif. Aucun rejeu d'inférence après
FINAL. T19 et T21 passent. Total 56 PASS et 12 NOT_RUN.
Voir `RECEIPT-stream-32-B4v-20261120.md`.

20 novembre 2026. B4w reçoit les contrastes descriptifs sur fixtures full et pilot.
RED confirme l'absence du raccordement. GREEN V2 compte 1 056 passés en 87,79 s.
Chaque mode publie 30 contrastes et consomme une graine par clé de bootstrap.
La publication full conserve les trois revendications. T41 passe.
Total 57 PASS et 11 NOT_RUN. Voir `RECEIPT-stream-32-B4w-20261120.md`.

20 novembre 2026. B4x reçoit la distinction entre information diagonale et jointe pour
les deux familles de l’oracle gaussien ajusté. Les valeurs du CSV concordent avec les
calculs indépendants appliqués aux masques ALT vérifiés. C0 compte 1 057 passés en
92,81 s. T39 et T42 passent. Total 59 PASS et 9 NOT_RUN.
Voir `RECEIPT-stream-32-B4x-20261120.md`.

20 novembre 2026. B4y reçoit EIGENMEAN et les deux règles CPV90 sur trois setups
et deux univers. Les masques engagés et les cardinalités publiées correspondent aux
préfixes calculés indépendamment. Les statuts hors univers restent sans cellule CAL.
C0 compte 1 058 passés en 92,91 s. T35 et T36 passent. Total 61 PASS et 7 NOT_RUN.
Voir `RECEIPT-stream-32-B4y-20261120.md`.

20 novembre 2026. B4z reçoit le repli initial des politiques ONLINE, le prior commun
calculé sur K et les deux variantes gamma du CLI sur fixture. Les cellules de
sensibilité conservent leurs propres identités CAL. C0 compte 1 059 passés en 94,17 s.
T10, T15 et T34 passent. Total 64 PASS et 4 NOT_RUN.
Voir `RECEIPT-stream-32-B4z-20261120.md`.

20 novembre 2026. B4aa reçoit les supports et l’information des cinq familles sur
trois setups. Les 120 injections de 15 partitions ALT correspondent aux octets
régénérés par clé. Les deux oracles HEAD EXACT gardent PC2–5. Une même clé HEAD
garde sa dérive brute sous deux fits gaussiens et change de projection.
C0 compte 1 060 passés en 96,05 s. T27, T28 et T29 passent.
Total 67 PASS et 1 NOT_RUN. Voir `RECEIPT-stream-32-B4aa-20261120.md`.

20 novembre 2026. B4ab reçoit les refus CLI T22. La configuration incomplète
est bloquée avant staging. Une valeur propre nulle ou un écart LW insuffisant
laisse le repère engagé et refuse le fit après un seul tirage. C0 compte
1 063 passés en 95,70 s. Total 68 PASS sur fixtures et 0 NOT_RUN.
Voir `RECEIPT-stream-32-B4ab-20261120.md`.

Les paragraphes historiques suivants conservent le statut de chaque étape à sa date.
B2v GREEN a mesuré 806 passés en 17,33 s. RED B2v 36 échecs attendus et 770 passés en 36,06 s.
B2u et B2v reçus par leurs décisions `RECEIPT-stream-32-B2u-20261118.md` et `RECEIPT-stream-32-B2v-20261118.md`.
Première capture B2v refusée quota5h/HTTP429 sans patch ; reprise en nouvelle conversation
Claude d75b08ed/opus/high après reset20:20UTC du18novembre, capture recevable et RED observé.
Disposition REVIEW-stream-32-B2v-fresh-session-20261118.md ; revue RED-fresh du18novembre.
Trois fits8x4 de fixture dans le test B2g ; aucun tirage/cohorte ou fit de campagne.
Pyflakes et diff-check passent ;806cas figés SHAf93cdf90, sourceed3944fd,157anciens nœuds AST exacts ;
sept anciens RED éteints après sourcea9fc5141 ; autres noyaux et producteur scellé inchangés.
B2o : coreGREENv1 jamais appliqué ; v2 revu indépendamment et appliqué après RED réel.
Préflight/cache sémantique/reprise simple passent. Comptage CPU préflight/rechargement/
refus d'intégrité et checkpoint avant budget métadonnées passent après source d380377f.
Budget sur retour complet CPU/plafond et échéance mur PASS après source96a1e240 ;
budget avant premier producteur et avant commit métadonnées PASS. Décision :
REVIEW-stream-32-B2o-budget-green-20261117.md ; B2o non reçu, autres témoins dus.
Premier GuardRED refusé quota5h ; reprise unique après08:40UTC réussie, même session.
Revue des gardes et RED réel : REVIEW-stream-32-B2o-guard-red-20261117.md.
Reprises après frame/fit/métadonnées PASS, sans correctif source ni RED fabriqué :
REVIEW-stream-32-B2o-recovery-tests-20261117.md. Six refus avant effets PASS :
REVIEW-stream-32-B2o-authority-tests-20261117.md. Cinq refus d'intégrité engagée/pending
et reprise d'orphelin NPZ PASS, sans correctif source ni RED fabriqué :
REVIEW-stream-32-B2o-integrity-tests-20261117.md. Refus numériques réels T22 et trace
MARKET, comptabilité sur exception et HEAD inconclusif engagé/rechargé sans relance PASS :
REVIEW-stream-32-B2o-exception-tests-20261117.md. Deux fixtures full/smoke procédural,
N24/N26 et fit_id0/1, caches/identités/partage applications/reprise/CPU PASS :
REVIEW-stream-32-B2o-coordinate-tests-20261117.md. Bilan indépendant et décision distincte :
RECEIPT-stream-32-B2o-20261117.md ; aucun témoin B2o exigé restant manquant.
DEV/politiques/prior/raccordements restent dus pour B2, contrats globaux laissés partiels.
B2p REDv1 : capture complète valide mais patch de tests non appliqué après contre-revue.
Fixture qbar ne distinguant pas le pool quatre familles du seul scope évalué ; correction
ciblée des scales/qualification demandée à l'auteur,21cas/API et537anciens préservés.
Ce refus historique précède la v2 : REVIEW-stream-32-B2p-red-20261117.md.
Deux corrections auteur consolidées en mémoire, comparaison exacte et contre-revue,
puis application native unique :21failed537passed18.95s, toutes qualifications franchies.
Seules absences des deux fonctions au RED : REVIEW-stream-32-B2p-red-v2-20261117.md.
GREEN44lignes/deux fonctions,558passed10.70s et contre-revue avant réception limitée :
RECEIPT-stream-32-B2p-20261117.md. Aucune sélection ou provenance DEV de tableau nu
déduite ; cache/gel/prior/politiques/d_dev/s2_dev et raccordements restent dus.
Aucun contrat global partiel promu.
B2q REDv1 : capture complète valide, test proposé non appliqué après contre-revue :
positifs du prior tous au même tripletH250/alpha.05/K20, non discriminants d'une constante.
Deux corrections auteur demandées dans les positifs existants,27cas/API et558anciens
préservés. Ce refus historique précède la v2 : REVIEW-stream-32-B2q-red-20261117.md.
Deux blocs auteur consolidés en mémoire, comparaison exacte et contre-revue avant
application unique :27failed558passed21.63s, toutes qualifications franchies. Prior
et fabrique absents : REVIEW-stream-32-B2q-red-v2-20261117.md. GREEN76lignes/deux
fonctions,585passed10.78s et contre-revue avant réception limitée :
RECEIPT-stream-32-B2q-20261117.md. Prior dynamique et fabrique nominale PASS ;
sensibilité gamma_M, prior transmis aux scans et raccordements restent dus ; aucun
contrat global partiel promu par ces fonctions.
B2r : API/tests complets contre-revus, append291lignes/21cas appliqué nativement une fois.
RED21failed585passed19.94s ; toutes qualifications statiques/online/oracle/GE/priors
communs et fois4/bits locaux franchies, seules deux fonctions de scan absentes.
Revue détaillée : REVIEW-stream-32-B2r-red-20261117.md. Source inchangée, GREEN dû ;
aucune réception B2r/B2 ni contrat global partiel promu par ce RED.
B2r GREENv1 : capture valide, source NON APPLIQUÉE après revue statique et contre-revue.
Garde de dtype réel absente avant conversion des Y/q_true complexes ou textuels :
REVIEW-stream-32-B2r-green-20261117.md. Témoins complémentaires contre-revus/appliqués
une fois :84lignes/sept cas, RED28failed585passed22.51s, qualifications des six refus
réels et du contrôle entier passantes avant API absentes ;613cas figés.
Revue : REVIEW-stream-32-B2r-guard-red-20261117.md. Aucun comportement de v1 non
appliquée présenté comme reproduit ; aucun ancien test affaibli ni contrat global promu.
B2r GREENv2 complet contre4bc2be9a contre-revu/appliqué une fois,33lignes/deux wrappers
et deux aides communes ;613passed11.05s/pyflakes, refus dtype/contrôle entier/prior/
dispatch/bits locaux/horizon/bornes PASS. Bilan indépendant et réception limitée :
RECEIPT-stream-32-B2r-20261117.md. Aucun stockage/cohorte/calibration/identité reçu ;
sensibilité gamma_M et contrôleur DEV/raccordements restent dus, B2 incomplet.
B2s premier appel : capture refusée exit1/is_error=true/HTTP429/quota5h, sans patch.
REVIEW-stream-32-B2s-red-20261117.md ; reset annoncé18novembre00:50UTC, une reprise
préparée après reset dans la même session. Aucun test/code B2s appliqué/exécuté ;
613cas reçus inchangés, aucune nouvelle observation RED ni réception B2s/B2.
B2s après reset : exit124/raw et stderr vides après1200s, capture refusée sans patch.
Diagnostic de session effectué avant nouvelle action : lecture/rédaction active,
lecture trop large corrigée, aucun processus résiduel. Réduction ciblée du premier
groupe proposée à contre-revue pour un éventuel TROISIÈME ET DERNIER essai ; échec
supplémentaire de capture/outil/syntaxe/incomplétude ⇒ gel explicite et arrêt.
Revue : REVIEW-stream-32-B2s-red-after-reset-20261118.md.613cas/source inchangés,
identités/raccordements/réception B2s et B2 complet toujours dus.
B2s troisième capture ciblée réussie, trois cas complets contre-revus/appliqués une fois :
RED3failed613passed13.84s, seule API gamma_sensitivity_policy absente ; coûts Halpha
dynamiques/deux ordres et statiques sans recalcul qualifiés. Incident capture clos,
aucun gel déclenché ; source GREEN nouveau pas TDD après RED, pas de quatrième relance.
REVIEW-stream-32-B2s-red-focused-20261118.md ; identité/trajectoire/refus/autres statiques
et réception B2s/B2 restent dus, aucun contrat global partiel promu.
B2s coreGREEN contre-revu/appliqué une fois, une fonction/28lignes ;616passed10.99s/
pyflakes, ancien préfixe et tests figés. Domaine : bundles primaires valides du même
descripteur seulement. Refus de statuts/s2/K/coûts/masques falsifiés, variantes et
paramètres, autres statiques, trajectoire et identités restent dus avant réception B2s.
REVIEW-stream-32-B2s-green-core-20261118.md ; aucun contrat global partiel promu.
B2s GuardRED contre-revu/appliqué une fois :108lignes/21cas,9failed628passed15.23s.
Neuf DID NOT RAISE pour statut/s2/K/coût/masque falsifiés ; onze refus déjà gardés et
statiques restantes PASS sans gamma superflu ni recalcul. Source inchangée,637cas figés ;
correction des seules gardes désormais due : REVIEW-stream-32-B2s-guard-red-20261118.md.
Identité/trajectoire/DEV et réceptions B2s/B2 restent dues, aucun contrat global promu.
B2s GuardGREEN contre-revu/appliqué une fois : seule fonction gamma_sensitivity_policy,
637passed11.13s/pyflakes, tests figés et151autres nœuds AST/préfixe/scellé inchangés.
Gardes avant coût, statuts légitimes et statiques sans paramètre gamma superflu PASS ;
bilan indépendant limité : REVIEW-stream-32-B2s-guard-green-20261118.md.
Trajectoire discriminante et identité pré-exécution/SHA restent dues avant réception B2s ;
DEV/cache/gel/d_dev/s2_dev/raccordements et B2 complet toujours dus.
B2s trajectoire : append52lignes/deux cas contre-revu/appliqué une fois,
639passed12.88s/pyflakes, source inchangée et aucun RED fabriqué. Coûts504/5000,
masques et W distincts aux références scalaires, mêmes prior/seuil et horizon entier ;
bilan indépendant limité : REVIEW-stream-32-B2s-trajectory-tests-20261118.md.
Identité pré-exécution/SHA toujours due avant réception B2s ; DEV/raccordements et
B2 complet non reçus, aucun contrat global partiel promu.
B2s règle REDv1 : capture complète valide mais patch/API non appliqués après
contre-revue. Recette DEV_PREFIX sans grille/critère/égalités déclaratifs, non
discriminante de règles distinctes ; correction ciblée de cette seule branche et
témoin indépendant de grille demandés. Aucun RED ni nouveau C0 revendiqué ;
639cas/source inchangés. REVIEW-stream-32-B2s-rule-red-20261118.md.
V2 à comparer et contre-revoir avant application ; aucun contrat global promu.
B2s règle REDv2 : comparaison complète et contre-revue ACCEPTED puis application
native unique,104lignes/trois cas ;3failed639passed14.11s, seules absences policy_rule.
DEV_PREFIX déclaratif complet et grilles/SHA distincts, références/budgets/statiques
qualifiés avant absence du noyau ; source inchangée,642cas figés. Revue détaillée :
REVIEW-stream-32-B2s-rule-red-v2-20261118.md. GREEN nominal seul désormais demandé ;
refus/invariances/ORACLE-AFF-W32 et DEV/B2s/B2 toujours dus, aucun contrat global promu.
B2s règle GREEN nominale : une fonction/58lignes contre-revue puis appliquée une fois,
642passed11.09s/pyflakes, tests figés et152anciens nœuds AST/scellé exacts. Recette
pré-exécution/SHA pur et DEV déclaratif complet passants au domaine nominal ;
bilan indépendant limité : REVIEW-stream-32-B2s-rule-green-20261118.md.
Refus/invariances/branches primaires complémentaires puis DEV/raccordements restent
dus avant réceptions B2s/B2 ; aucun contrat global partiel promu.
B2s règles/invariances : append83lignes/deux tests contre-revu/appliqué une fois,
644passed13.02s/pyflakes, source inchangée et aucun RED fabriqué.18recettes primaires
et cinq clones JSON/90appels aux références indépendantes passants ; seule portée
scope.families modifiée, pas de T23 global/DEV/CAL reçu. Bilan limité :
REVIEW-stream-32-B2s-rule-invariance-tests-20261118.md. Refus d'entrée puis DEV/
raccordements restent dus avant réception B2s/B2, aucun contrat global promu.
B2s refus : append74lignes/26cas contre-revu/appliqué une fois,670passed13.14s/
pyflakes, source inchangée et aucun RED fabriqué. Contrôle indépendant/ValueError
direct/aucun SHA après refus passants. REVIEW-stream-32-B2s-rule-guard-tests-20261118.md.
Bilan indépendant puis décision distincte : RECEIPT-stream-32-B2s-20261118.md ;
aucun témoin propre aux deux fonctions pures restant manquant. DEV/bibliothèque/
cache/d_dev/s2_dev/identités réalisées/raccordements et B2 global restent dus.
B2t premier RED : append45lignes/trois bras contre-revu/appliqué une fois,
3failed670passed14.39s, seules absences dev_library_block. Clés DEV_LIB planifiées/
bornées, n_lib2/cap2 et q indépendants normalisés une fois qualifiés ; source inchangée,
673cas figés. REVIEW-stream-32-B2t-red-20261118.md. Réemploi réel du producteur à
mesurer après GREEN ; aucun cache/DEV complet ni contrat global reçu.
B2t GREEN nominal : append26lignes/une fonction contre-revue/appliquée une fois,
673passed11.29s/pyflakes, tests figés et153anciens nœuds AST/scellé exacts. Producteur
et géométrie/projection reçus réellement exécutés sur RAWdraws fournis, q aux golds,
clés/ordre/readonly passants. Journaux durables récupérés sans rejouer après cellule
expirée ; bilan limité : REVIEW-stream-32-B2t-green-20261118.md. Gardes d'admission,
sorties/échecs/zéros puis cache/DEV complet restent dus, B2t/B2 non reçus.
B2t gardes : append134lignes/27cas contre-revu/appliqué une fois,
700passed13.26s/pyflakes, source inchangée et aucun RED fabriqué.19admissions refusées
avant producteur,7erreurs au deuxième appel sans troisième appel/reroll/retour partiel,
et positif zéro PASS. Bilan indépendant puis réception limitée distincte :
RECEIPT-stream-32-B2t-20261118.md. Cache lié à SETUP/qbar effectif, phase DEV,
d_dev/s2_dev/gel/identités réalisées et B2 global restent dus, aucun contrat global promu.
B2u premier RED : append170lignes/trois tests contre-revu/appliqué une fois,
3failed700passed14.72s/pyflakes ; seules absences dev_library_cache. SETUP fourni et
engagé, n_lib/plafond2, douze clés/matrices q, inventaire incomplet valide qualifiés.
Taxonomie d'exceptions de l'API précisée sans changement de test :
REVIEW-stream-32-B2u-red-20261118.md. GREEN minimal dû ; assertions de caches/qbar/
reprise après API et gardes complémentaires restent à exécuter avant réception B2u.
B2 global non reçu, aucun contrat global partiel promu par le RED.
B2u coreGREEN v1 : capture complète valide, source NON APPLIQUÉE après revue statique.
Égalité Python de la provenance SETUP accepte potentiellement des types numériques
JSON différents, malgré les identités attendues depuis la coordonnée canonique.
Défaut statique confirmé ; aucun comportement de v1 non appliquée présenté comme
reproduit. REVIEW-stream-32-B2u-green-core-20261118.md. Témoins typés puis v2 complète
contre59fd084c dus ;703cas/source inchangés, aucun C0 GREEN ni réception B2u/B2.
B2u GuardRED : append87lignes/quatre cas contre-revu/appliqué une fois,
7failed700passed16.43s/pyflakes ; seules absences de l'API, qualifications des
deux alias JSON/SETUP absent/T7float32 génériquement valide passantes. V1 toujours
non appliquée ; aucune reproduction du défaut statique revendiquée.
REVIEW-stream-32-B2u-guard-red-20261118.md. V2 complète contre59fd084c due,
707cas figés ; gardes complémentaires et réception B2u/B2 toujours dues.
B2u coreGREEN v2 : comparaison exacte unique de provenance canonique, contre-revue
ACCEPTED puis application native unique ;707passed11.74s/pyflakes. Préfixe154AST,
tests et scellé conservés, contrôles cache/qbar/rechargement/alias/SETUP absent/
float32 avant producteur manquant réellement passants. Bilan nominal limité :
REVIEW-stream-32-B2u-green-core-v2-20261118.md. Gardes d'autorité/schémas/intégrité/
reprise/CPU/coordonnées/MARKET/vrai producteur encore dues ; B2u/B2 non reçus.
B2u schémas : append112lignes/22cas contre-revu/appliqué une fois,
729passed14.98s/pyflakes, source inchangée et aucun RED fabriqué. Huit caches
génériquement valides refusés avant producteur manquant, quatorze payloads refusés
avant sérialisation avec callback et CPU0.25 tracés ; octets scientifiques conservés.
REVIEW-stream-32-B2u-schema-tests-20261118.md. Autres gardes d'admission/intégrité/
reprise/ressources/coordonnées et vrai producteur restent dus, B2u/B2 non reçus.
B2u admission : append105lignes/onze cas contre-revu/appliqué une fois,
740passed15.59s/pyflakes, source inchangée et aucun RED fabriqué. Dix refus avant
effets dont autre GO correctement qualifié, et positif rôle DEV réservé/pending
non généré ; références filtrées en copie, identités/qbar/NPZ corrects.
REVIEW-stream-32-B2u-admission-tests-20261118.md. Intégrité/reprise/CPU/budgets/
coordonnées/MARKET/vrai producteur restent dus ; B2u/B2 non reçus.
B2u intégrité : premier appel refusé exit1/is_error=true/HTTP429/quota5h,
aucun patch. Reset annoncé18novembre15:20UTC ; reprise unique prévue15:21UTC
dans la même session/opus/max, mission et740cas inchangés. Contre-revue accepte
rejet et reprise, aucun nouveau test ou C0 revendiqué :
REVIEW-stream-32-B2u-integrity-tests-20261118.md. Toute nouvelle erreur exige
diagnostic avant action, pas de boucle automatique ; aucune réception B2u/B2.
B2u intégrité après reset : capture complète valide, append186lignes/16cas
contre-revu/appliqué une fois ;756passed16.74s/pyflakes, source inchangée et aucun
RED fabriqué. Quatre caches SETUP, sept provenances et cinq états DEV passent ;
stockage cohérent pour poisons sémantiques, aucun faux positif par SHA obsolète.
REVIEW-stream-32-B2u-integrity-tests-after-reset-20261118.md. Premier quota rejeté
conservé, reprise unique terminée, aucun timer actif. Reprise/ressources/autres
coordonnées/MARKET/vrai producteur restent dus avant réception B2u/B2.
B2u reprises : append97lignes/trois cas contre-revu/appliqué une fois,
759passed17.53s/pyflakes, source inchangée et aucun RED fabriqué. Interruptions
après NPZ, après JSON et pendant vraie réduction ; référence qualifiée avant
autre ROOT, reprise12/11/0 callbacks, bytes/handoff/CPU par token concordants.
REVIEW-stream-32-B2u-recovery-tests-20261118.md. Ressources/coordonnées/MARKET/
vrai producteur restent dus ; B2u/B2 non reçus.
Prompts-check34/34 reste la preuve de précondition `logs/stream-32/B-preconditions-checks.log` exit0.
Décompte des contrats :18PASS,0FAIL,50NOT_RUN. FAIL peut concerner une couche partielle ;
un succès partiel reste NOT_RUN jusqu'à ses raccordements, sans clôturer le contrat complet.
Aucune commande future associée à un témoin absent n'est déclarée exécutée.

B1f : premier appel quota rejeté ; reprise immédiate après reset confirmée par le chercheur,
capture après reset acceptée, RED puis GREEN observés. Anciens minuteurs annulés ; même session conservée.
T16 n'est pas couvert par les CSV directs de fixture ; témoin d'inversion des listes B1g maintenant PASS.

B1g : première capture rejetée (exit124, raw vide), reprise complète acceptée et contre-revue reçue.
Tests initiaux et extension refus/durabilité passent après GREEN ; JSON strict et garde NUL relus.
Défauts CRLF/liens/taille reproduits par EdgeRED puis corrigés et PASS après EdgeGREEN.
Publication bas niveau reçue, stage-mode/GO absent et autres liens PASS ; contrôleur/FINAL/T16 toujours dus.
Autorité de fixture synthétique uniquement ; aucun succès complet des contrats raccordés déduit de ces153passés.

EdgeRED v1 reçu, contre-revu mais non appliqué : précondition de fixture4Kio incompatible avec le
manifeste5851octets déjà produit. Révision64Kio ciblée, politique50Mio inchangée. Aucun nouveau test
exécuté ; décompte et dernière preuve C0 conservés, blocages de revue toujours ouverts.
V2 arrêtée par quota5h sans patch, reset annoncé16:00UTC15novembre ; une reprise unique
après reset est préparée. Aucune application ou preuve RED Edge par cette capture en erreur.
Reprise unique16:01UTC enregistrée/vérifiée, service encore inactif ; aucune attente active.
Après reset, capture v2 complète et contre-revue reçue, seule correction64Kio confirmée ;
append natif puis RED ci-dessus. Quota résolu, aucun minuteur restant ; aucun calcul scientifique.
Puis EdgeGREEN source seule appliqué et contre-revu,153passés ci-dessus ; réception B1g enregistrée.

B1h : v1 non appliquée ; correction unique du libellé en v2 confirmée exactement et contre-revue.
Append natif puis RED16failed153passed, GREEN169passed ; vrai CSV FAIR/valeurs/provenances vérifiés.
Débordement de conversion reproduit par EdgeRED sans CSV infini créé, puis corrigé après ce RED.
Composant reçu après171passés/contre-revue, longdouble modéré/readonly PASS ; T16 complet reste bloquant.

B1i : v1 non appliquée après contre-revue de la propriété du temporaire ; v2 ciblée reçue et contre-revue.
14cas conservés et trois refus ajoutés : revendication du DID insuffisante, notes étrangères après
interruption et autre GO à la reprise ; assertion des sept champs renforcée. Append natif puis RED
17failed171passed, tous sur finalize absent ; GREEN initial188passed5.73s, tests inchangés.
Réception suspendue après contre-revue : nouveaux CSV hachés avant garde50Mio et fsync du parent
non achevé en reprise post-rename avant FINAL. EdgeRED ciblé contre-revu et appliqué :
2failed189passed en6.45s, frontière50Mio verte ; T50/T60 FAIL reproduits puis corrigés.
EdgeGREEN trois lignes source,191passed5.93s et contre-revue Codex ; sous-agent final indisponible
sur quota, aucun avis supplémentaire revendiqué. B1i reçu comme composant seulement, gardes restantes
à témoigner et complétude/status/ressources dus. T60/B1/B restent ouverts.

B1j :12témoins supplémentaires des gardes existantes, relus/appliqués ;203passés6.87s sans
changement de production ni RED artificiel. Marqueurs/liens/non-régularité, FINAL avec sortie absente
ou GO différent, stage/GO absent, temporaire vide et smoke strictement unitaire passent.
NULL_PLAN de la fixture smoke est applicable et figé, sans aucune campagne. Réception bornée B1j ;
complétude des clés planifiées/INCOMPLETE/status/ressources et raccordements toujours dus.

B1k : v1 non appliquée, v2 ciblée reçue/revue ; onze cas initiaux conservés et deux tests ajoutés :
PhaseOrderError canonique et interruption fsync/replace de status.json. Application native puis RED
13failed203passed en8.29s, tous sur finalize_planned absent. API et frontière de confiance explicites ;
GREEN initial216passed7.13s, tests inchangés. Réception suspendue après contre-revue : ALT.json
absent après publication peut être réduit à INCOMPLETE malgré FINAL ou output complet déjà engagé.
EdgeRED ciblé avec/sans FINAL revu/appliqué :2failed216passed en8.03s, tentatives de mutation
du statut bloquées. T45/T60 FAIL reproduits ; garde GREEN minimale désormais demandable.
Première proposition EdgeGREEN non appliquée : nouvelle lecture du manifeste à travers un output
symbolique avant refus. Test complémentaire revu/appliqué :3failed216passed en8.25s, nouvelle
tentative d'écriture bloquée sur source inchangée ; candidat rejeté toujours non appliqué.
EdgeGREENv2 appliqué,219passed7.24s et contre-revue Codex, refus du lien avant lecture vérifié.
B1k reçu comme porte sur échéancier de fixture seulement ; énumération scientifique/consommation
et ressources toujours dues, aucun contrat global T45/T50/T60/B1/B clôturé par ce composant.

B1l : proposition comptable bornée revue puis tests seuls appliqués ;9failed219passed8.74s,
tous sur charge_cpu/require_budget absents. Checkpoints CPU monotones par token, cumul entre
invocations, bornes exactes CPU/mur, refus de reset et reprise sur horloge fictive. Pas d'opération
gardée ni de mesure système : ces raccordements et le CPU hors checkpoints restent bloquants.
GREEN après reset appliqué,228passed7.58s et contre-revue indépendante acceptée pour le composant
comptable borné ; pas de garantie runtime ou de vrais callbacks bloqués revendiquée.
Premier appel GREEN rejeté : quota5h, exit1/is_error=true, aucun patch. Reset annoncé21:00UTC
le15novembre ; reprise unique21:01UTC enregistrée/vérifiée dans la même session, empreintes requises.
Capture après reset complète acceptée ; quota résolu, aucun minuteur restant. Réception B1l limitée,
mesure SELF+CHILDREN/CPU hors checkpoints/worker-lifecycle et câblage réel toujours bloquants.

B1m : capture complète validée, API fonctionnelle et sept cas contre-revus sans défaut matériel,
append tests seul appliqué nativement ;7failed228passed en8.94s, tous sur start_invocation absent.
SELF+CHILDREN et mur simulés, jeton unique, garde avant callback, vrai cache NPZ, pointage cumulé
après retour/exception et refus de compteur invalide ; contexte interne à une invocation.
GREEN source seule appliqué,235passés7.82s et contre-revue indépendante acceptée : composant
reçu, CPU hors checkpoints/borne externe/workers/driver/mémoire et raccordements scientifiques
encore bloquants. Aucun contrat global ou nouvelle porte reçu. Gardes phasecommit/finalize à
consommer par le driverB4, pas d'enforcement complet déduit du pointage et du callback de fixture.

B1n : v1 non appliquée après contre-revue des pièges de suppression du temporaire. V2 comparée
exactement : seuls imports et quatre pièges locaux ajoutés ; contre-revue acceptée, tests seuls
appliqués nativement. Unique assertion reçue renforcée vers l'inventaire exact CSV+locals,
autres octets reçus préservés ;7failed234passed9.51s, exact_local positif déjà PASS.
Manques reproduits : locaux non émis, reprise acceptant une revendication absente/fausse/étrangère,
et temporaire incohérent jugé possédé (unlink intercepté avant effet). GREEN source seule appliqué,
241passés8.34s et contre-revue acceptée ; B1n reçu comme composant. Inventaire local complet et
sa correspondance de reprise PASS ; masques uint32/CLI/science/bundle et réserves B1m encore dus.

B2a : v1 non appliquée après contre-revue (spy QR par référence et decay8 seul). V2 complète
comparée/revue, copies Q/R et seul cas decay4 ajoutés avant autorisation de fixture. Append
natif, préfixe241cas intact ;11failed241passed9.96s, tous sur population_frame absent.
GREEN source seule appliqué,252passés8.36s et contre-revue acceptée pour N32/N239 ; B2a reçu
comme primitive. Repère/spectre/cléframe PASS, consommation de toutes les graines/driver encore due.
B1/T16/CLI/cohortes/ressources et reste scientifique encore ouverts, aucun report implicite enC.

B2b : v1 non appliquée, report du spectre constant non dyadique refusé. V2 comparée : seul
témoin readonly constant0.1 ajouté, onze cas v1 inchangés. Contre-revue après reset du quota
acceptée avant append natif ; préfixe252cas intact,12failed252passed10.20s, tous sur nouvelle
fonction spectral_baselines absente. API pure, univers/statuts et références explicités.
GREEN source seule appliqué,264passés8.38s ; réception suspendue après contre-revue : finitude
des valeurs propres insuffisante si trace déborde, CPV peut fournir fauxk90=1. Témoin EdgeRED
avant garde d'appelant demandé ; aucune reproduction déclarée avant son exécution.
Aucun fit/cohorte/campagne, B1/B et raccordements restent ouverts.
EdgeRED contre-revu/appliqué,2failed265passed9.28s : appels CPV non protégés interceptés pour
trace pleine infinie malgré éléments et traces éligibles finis. Contrôle grande trace finie PASS,
264cas antérieurs préservés. EdgeGREEN source seule appliqué et contre-revu : garde sum ET
cumsum avant les deux appels reçus,267passed8.31s, tests figés et scellé inchangé. B2b reçu
comme noyau seulement ; tous les raccordements scientifiques/politiques restent dus.

B2c : capture complète et schéma fonctionnel exact relus, contre-revue indépendante acceptée ;
append tests seul natif,183797octets/267cas préservés.22failed267passed11.63s, tous sur
nonoracle_masks/oracle_masks absents. STATIC sans sélection/repli, ORACLE constant dès t1,
ONLINE reçu/scalaire et causalité,readonly/refus/champs inconnus sont les assertions à exercer
après GREEN ; aucun succès métier de ces enveloppes revendiqué avant celui-ci.
T25/T38 gardent AST/appelants/simulateur dus, T15/T16 et réserves B/ressources inchangés.
GREEN source seule appliqué,289passed8.48s et contre-revue acceptée ; code reçu en composant
pur, sans autre contrat global clôturé. Repli uniquement ONLINE et STATIC/ORACLE conservés
PASS sur les fixtures. Fabrique/identités et consommation par CAL/évaluation encore dues.

B2d : capture v1 complète lue/contre-revue, NON APPLIQUÉE. Faux positif dans le témoin F0
extrême : return None confondu avec except ValueError, révision tests seule ciblée requise.
Choix techniques figés : lambda noncroissant, F0 préfixe court et B0 admis, indices int stricts ;
témoins à compléter sans changer campagne/K20/supports/références. Aucun RED B2d observé ;
source/tests289/scellé et dernière preuve C0 conservés, aucun contrat promu ou reporté en C.
V2 entièrement comparée/contre-revue, seules corrections et bornes demandées ajoutées ;
24cas initiaux et préfixe194236octets reçus préservés. Append natif puis RED27failed289passed12.64s,
tous sur population_drift absent. Assertions métier population/supports/KL/HEAD/refus à exercer
après GREEN ;316tests figés, source et scellé inchangés, aucune réception B2d/B anticipée.
GREEN initial source seule appliqué,316passed8.44s/pyflakes ; réception suspendue après revue
numérique : I*=2^-1074 peut produire q ou Delta entièrement nul avec statut SUPPORTED.
Trois cas algébriques relus, aucun RED de sous-flux encore observé ; EdgeRED tests seule à
demander, contrôle F3 subnormal représentable/B0 requis. Source121b7018/tests67130f8f figés.
EdgeRED lu/contre-revu/appliqué nativement :3failed317passed9.36s, trois ValueError manquantes
reproduites. Contrôle F3 subnormal et assertions B0 passants ;316cas précédents préservés.
Garde commune q ET Delta non nuls par ligne non vide encore due,320tests figés/e14ccade ;
aucune normalisation/seuil/arrondi scientifique modifié, aucune réception B2d/B2 anticipée.
EdgeGREEN un seul hunk,320passed8.42s et contre-revue acceptée ; garde commune par ligne q
positif ET Delta non nul, B0 et F3 subnormal préservés. B2d reçu en primitive seulement,
configuration/graines/fits/provenance SETUP et tous les autres raccordements B2 encore dus.

B2e : première capture rejetée pour quota cinq heures, exit1/is_error=true malgré subtype
success ; HTTP429 et résultat non structuré, aucun patch. Reset annoncé07:00UTC16novembre,
reprise unique07:01UTC enregistrée/vérifiée dans la même session, sans changement de modèle.
Minuteur chargé/actif/en attente, service inactif/ExecMainPID0 ; aucun nouvel appel lancé.
Aucun test B2e ou application ; dernière preuve320passed8.42s et tous les68statuts conservés.
Consigne STOP après B2 complet inchangée, pas de B3/B4 ou nouvelle autorisation de calcul.
Après reset : capture complète acceptée, sept SHA conformes (mission comprise), API/patch
entièrement lus et contre-revue indépendante reçue ; append natif,210277octets reçus préservés.
RED27failed320passed13.23s, tous sur projection_diagnostics absent.347tests figés ; source/scellé
inchangés. Minuteur collecté/inactif, aucun nouvel essai en attente. Références EXACT/FITTED,
q_plugin non standardisé/joint/biais/zeros/B0 à exercer via le noyau GREEN ; aucun fit/tirage.
GREEN initial source seule appliqué,347passed8.50s/pyflakes. Réception suspendue après
contre-revue numérique : a=2^-1074, basesI2, C0=aI2,beta=(a,a) renvoient I_joint0 alors que
le joint mathématique=a est représentable. Défaut reproduit sous .venv/verrou en audit unitaire
distinct, pas encore en pytest EdgeRED ; source d2874c53/tests6bc7bcbf figés. Aucun fit/tirage
ou campagne, helpers scellés inchangés ; témoins ciblés avant garde, projection nulle/B0 à préserver.
EdgeRED lu/contre-revu/appliqué :1failed349passed9.38s, ValueError manquante reproduite pour
beta non nul/joint nul. Joint positif avec q nul, vraie projection nulle et B0 passants ;
347cas reçus préservés,350tests a56eb359 figés. Garde finale commune encore due, aucun autre lot.
EdgeGREEN un hunk final :350passed8.51s, pyflakes/diff et contre-revue acceptés. Joint positif
pour beta projeté non nul, vrai beta0/B0 et q0avecjointpositif préservés ; B2e reçu comme
composant, T7/proxy/fits/metadata/exports/SETUP et autres raccordements B2 encore dus.

B2f REDv1 non appliqué après revue : fractions constantes ne discriminant pas min/mean/max.
REDv2 API et24cas identiques, une fonction ajoutée à fractions variables99/148 et123/148,
min/mean/max distincts ; contre-revue acceptée avant application native.25failed350passed
13.56s réels, uniquement absence de head_geometry, références pré-noyau franchies ; pytest
exit1 attendu/contrôles0, pyflakes/diff propres. Tests77aaa730/375cas figés, source0f77ce27
et scellé inchangés ; GREEN source seule encore due. κ/statut SETUP/fit unique/ordre et
isolement T64/T65 restent dus. Aucun fit, tirage ou campagne, B2 complet non reçu.
GREEN B2f import stdlib+primitive seule :375passed8.43s, pyflakes/diff et contre-revue
acceptés. Source9273b203, tests375/77aaa730 et scellé inchangés pendant vérification.
Géométrie pure reçue ; κ/statut/persistance SETUP/fit unique/ordre/isolement restent dus.

B2g tests seuls :21cas supplémentaires d'adaptateur de lignes FIT_NULL fournies, préservation
des375cas reçus ; contre-revue acceptée. Ratio T22 consigné avant GREEN : différence adjacente
divisée par la plus grande valeur propre, seuil1e−10 strict sur les K+2 premiers axes.
21failed375passed13.15s réels, uniquement absence de fit_record ; références préparatoires
franchies, aucun vrai fit exécuté au RED. Pytest exit1/contrôles0, pyflakes/diff propres ;
tests396/bb184466 figés, source9273b203/scellé inchangés. GREEN adaptateur minimal encore dû.
GREEN B2g append seul :396passed8.54s, pyflakes/diff et contre-revue acceptés ; source6845382a,
tests396/bb184466 et producteur scellé inchangés pendant vérification. Trois fits8x4 techniques
exécutés, aucun calcul de campagne. Adaptateur reçu ; SETUP/lignée/configuration et autres
raccordements encore dus, T22/T64/T65 partiels.

B2h V1 non appliquée après revue ; V2 ajoute seulement K20.0/T_fit48.0/I_star0.0 aux refus
avant fit,19cas/schéma/API conservés et κ_det clarifié comme non décisionnel pour HEAD.
Contre-revue acceptée avant application native absolue ;22failed396passed13.60s réels,
uniquement absence de setup_bundle. Tests418/6b219538 figés, anciens octets/AST préservés,
source6845382a/scellé inchangés ; pyflakes/diff propres, pytest1 attendu/contrôles0.
GREEN bundle fourni encore dû ; driver/cache/graines/T7/DEV et ordre global restent dus.
GREEN B2h append seul :418passed8.72s, pyflakes/diff et contre-revue acceptés ; sourcef3148c8f,
tests418/6b219538 et scellé inchangés. Bundle fourni reçu ; réserve bloquante avant B2 complet :
portées vides/dupliquées à corriger dans _check_cfg partagé, avec témoins avant producteurs.
Driver/cache/reprise/graines/générateurs/T7/DEV et ordre global encore dus, T22/T64/T65 partiels.

B2i tests seuls après contre-revue :8cas de portée vide/dupliquée et2positifs singleton/distinct,
appels au validateur commun et consommateurs sous fils-pièges.8failed420passed10.68s réels,
huit refus manquants dans _check_cfg ; contrôles positifs/CODE_FILES/rejeu/cfg intacts PASS.
Tests428/b312b19b figés, sourcef3148c8f/scellé inchangés ; pyflakes/diff propres, pytest1
attendu/contrôles0. GREEN partagé seul encore dû, pas de garde locale setup_bundle.
GREEN B2i quatre lignes communes :428passed8.68s, pyflakes/diff et contre-revue acceptés,
source52194c85, tests428/b312b19b et scellé inchangés pendant vérification. Réserve de portée
B2h levée ; autres validations/domaines et raccordements restent dus, B2 complet non reçu.

| Test | Statut | Contrat | Témoin / commande | Justification / réserve |
|---|---|---|---|---|
| T1 | PASS | M réemployé | test_mixture_cost_is_reused ; C0 | Noyau A reçu |
| T2 | PASS | OLS 1..16 distinct de la corde | test_affine_ols_distinct_from_chord ; test_affine_ols_refuses_nonpositive_or_nonfinite_line ; C0 | Noyau et garde OLS reçus |
| T3 | PASS | INFO exhaustif/glouton | test_info_sort_equals_greedy_equals_exhaustive ; C0 | K=2/5/8 et quatre coûts |
| T4 | PASS | Égalité adjacente | test_adjacent_tie_strictly_decreasing_q ; C0 | Plus petit d |
| T5 | PASS | Préfixe exhaustif | test_prefix_full_enumeration_non_monotone ; C0 | Maximum tardif |
| T6 | PASS | Sélection de référence | test_best_sets_matches_select_top_q ; C0 | Référence scellée |
| T7 | PASS | Prévisibilité | test_online_masks_predictable ; C0 | Présent/futur perturbés |
| T8 | PASS | Invariance avant début | test_online_masks_onset_and_direction_invariance ; C0 | Début et direction futurs |
| T9 | PASS | Estimateur scalaire | test_online_masks_match_scalar_reference ; C0 | Fenêtres 1/3/>H |
| T10 | PASS | Repli online et wrappers | test_nonoracle_scan_keeps_one_real_online_mask_sequence_and_its_past_only_scan ; test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b4z_cli_keeps_fallback_prior_and_gamma_cells_separate ; lot-B4z-tests.checks.log ; C0 | Repli {min E} au premier jour pour INFO et PREFIX, y compris leurs variantes gamma. HOLD et ALT conservent FULL_K et les masques oracle constants. La contre-vérification des partitions atteste les mots oracle distincts du repli. |
| T11 | PASS | Scan statique au même prior | test_masked_scan_static_equals_scan_statistic_same_s2 ; C0 | Producteur28 inchangé |
| T12 | PASS | Scan force brute | test_masked_scan_bruteforce ; C0 | Tous départs, math.fsum |
| T13 | PASS | Aucun rescoring | test_masked_scan_unselected_y_entry_and_zero_counts ; C0 | Entrée d'axe et comptes nuls |
| T14 | PASS | Élagage exact | test_masked_scan_column_pruning_exact ; C0 | Prior fourni conservé |
| T15 | PASS | Prior commun fondé surK | test_nonoracle_scan_passes_the_supplied_prior_unchanged_to_one_real_static_scan ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3h_descriptive_contrasts_pair_nonoracle_cells_with_primary_baselines_and_separate_the_oracle ; test_b3m_masked_alt_prior_ratio_averages_daily_selected_information_per_axis_over_the_prior_on_hand_witnesses ; test_b3m_masked_alt_prior_ratio_reproduces_the_plan_exact_static_quarter_information_ratios_at_the_common_prior ; lot-B3m-green.checks.log ; test_b4z_cli_keeps_fallback_prior_and_gamma_cells_separate ; C0 | B4z observe au noyau le même prior 2 ln(H/alpha)/(HK) pour les trois rôles et des cardinalités 1 et K. La fixture force l’alias S2_DEV au prior commun. Les sensibilités distinctes restent couvertes par B3b/B3h. |
| T16 | PASS | Libellés des vrais exports | test_export_selections_round_trips_the_t7_gaussian_proxy_label_in_the_received_schema ; test_b4h_export_calibration_fair_csv_byte_stable ; test_b4i_export_alt_selections_offline_from_staging ; test_b4j_export_trial_summaries_compact_hold_alt_rows ; test_b4k_export_aggregates_descriptive_v_rmst ; test_b4l_finalize_publishes_exported_scientific_payloads ; C0 | B4i vérifie sur les masques ALT les libellés ANALYTIC_PROXY et les bases EXACT et T7. B4j sépare les RMST observés. B4l publie les cinq CSV scientifiques avec les empreintes des données sources. |
| T17 | PASS | Tango EMV et symétrie | test_tango_constrained_mle_and_audit_intervals ; test_tango_score_finite_at_lower_endpoint ; C0 | 108cas, neuf audits, variance stable |
| T18 | PASS | Zéro discordance | test_tango_zero_discordance_closed_form ; C0 | Littéral corrigé explicitement ; tolérances conservées |
| T19 | PASS | Statut nul et refus de conception | test_cp_bounds_and_null_tristate ; test_calibrations_raise_the_sealed_insufficient_calibration_at_18_rows_and_rank_19_at_r_zero ; test_cal_phase_refuses_a_missing_dev_predecessor_before_any_cal_producer_or_write ; test_confirmatory_from_staging_refuses_an_absent_or_damaged_committed_input_before_any_bootstrap_or_kernel ; test_b4j_export_trial_summaries_compact_hold_alt_rows ; test_b4v_cli_full_publishes_committed_confirmatory_claims_once ; C0 ; lot-B3b-green.checks.log | Frontières CP et refus CAL/HOLD/ALT reçus. B4j et B4l publient les bornes, statuts et incidents. B4v conserve les qualifications nulles dans les trois lignes exactes dérivées des partitions engagées. |
| T20 | PASS | Biais de score avant clipping | test_null_score_bias_exact_three_point_enumeration ; C0 | Fraction exact |
| T21 | PASS | Dimensionnement et raccordement nul | test_plan_holdout_matches_independent_null_sizing ; test_null_plan_freezes_valid_n_hold_and_hold_consumes_it ; test_null_plan_phase_freezes_primary_p_conf_alarms_under_the_received_plan_rule_then_reloads ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_b4v_cli_full_publishes_committed_confirmatory_claims_once ; test_plan_holdout_cap_boundary_and_beta_half_power ; RECEIPT-stream-32-B4v-20261120.md ; C0 | Témoin indépendant du dimensionnement bilatéral, du plafonnement et du gel avant HOLD. B4v vérifie n_hold=5, cinq lignes HOLD et le statut plafonné publié sur fixture. |
| T22 | PASS | Refus numériques/fit/configuration | test_setup_phase_propagates_a_real_t22_fit_refusal_without_rerolling_the_gaussian_key ; test_setup_phase_covers_two_n_and_two_fit_ids_in_full_and_no_go_smoke ; test_b4ab_cli_rejects_missing_science_config_without_staging ; test_b4ab_cli_refuses_bad_lw_spectrum_without_reroll_or_publish ; C0 | Le CLI refuse une clé science manquante avant le staging. Chaque spectre LW invalide déclenche un seul tirage, aucun fit engagé et aucune publication. Les témoins de noyau couvrent les frontières numériques et les refus de configuration. |
| T23 | PASS | Permutation des familles non-oracles | test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; C0 | Les observations fournies traversent les quatre familles. La permutation F0/F1 conserve exactement les h, masques et franchissements par trajectoire. |
| T24 | PASS | Calibration non-oracle unique | test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; C0 | Une calibration par setup et identifiant de politique non-oracle, sans famille, et reprise vérifiée. HOLD commun et un scan par cellule reçus. Les quatre familles ALT réutilisent les mêmes calibration_id et seuils non-oracles. |
| T25 | PASS | Graphe sans métadonnées oracle | test_mask_envelopes_are_thin_causal_and_refuse_unknown_fields_structurally ; test_b4u_nonoracle_dependency_ast ; test_b4u_alt_monitor_ignores_poisoned_simulator_metadata ; C0 | AST des fonctions de masquage, calibration et scan. La fixture ALT altère famille, delta, q et autres métadonnées après scoring. Le staging et la publication scientifique restent identiques. |
| T26 | PASS | Calibration oracle séparée | test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3h_descriptive_contrasts_consume_committed_primary_f2_cells_and_keep_the_same_family_oracle_separate ; lot-B3h-green.checks.log ; C0 | Calibration par famille, clés méta CAL et libellé non déployable reçus. HOLD oracle par famille et NON_DEPLOYABLE reçus. ALT consomme l’oracle de la seule famille. Contraste de la fixture engagée avec FPR ORACLE_SEPARATE. FPR marginales et aucun Tango sur la paire oracle. |
| T27 | PASS | Support HEAD et information | test_direction_information_projects_one_population_drift_of_each_original_key_on_its_frozen_fit ; test_b4aa_cli_routes_population_drifts_and_preserves_fitted_injections ; C0 | B4aa observe PC2–5, q=I*/4 et KL pleine I* pour HEAD EXACT, avec plusieurs profils de signes. Les deux identités CAL oracle HEAD propres au setup mènent au même masque de cardinalité quatre. |
| T28 | PASS | Familles et univers | test_direction_information_keeps_the_received_unsupported_drift_without_projection ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; lot-B3h-green.checks.log ; test_b4aa_cli_routes_population_drifts_and_preserves_fitted_injections ; C0 | B4aa vérifie les cinq familles, leurs univers, supports et normes sur trois setups et 15 partitions ALT. F3 occupe seulement MARKET. Les cas hors univers restent couverts par les témoins purs du lot B2. |
| T29 | PASS | Injection indépendante du fit | test_path_scores_keep_one_supplied_return_delta_under_two_distinct_frozen_fits ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b4aa_cli_routes_population_drifts_and_preserves_fitted_injections ; C0 | B4aa compare les octets de 120 injections ALT au recalcul par clé. Les deux fits gaussiens engagés donnent le même delta brut et des projections distinctes sur une même clé HEAD. |
| T30 | PASS | Famille confirmatoire gelée | lot-B3e-green.checks.log ; test_b3f_paired_bootstrap_bounds_follow_each_family_shared_index_matrix ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_confirmatory_from_staging_bootstraps_each_claimed_family_once_on_committed_primary_cells_then_replays ; lot-B3g-green.checks.log ; lot-B3h-tango-green.checks.log ; test_b3h_descriptive_contrasts_pair_nonoracle_cells_with_primary_baselines_and_separate_the_oracle ; lot-B3h-green.phi.log ; test_b4v_cli_full_publishes_committed_confirmatory_claims_once ; C0 | Validation de Φ avant ALT, refus d’un H2 manquant et portée descriptive préservée. Les trois contrastes et α/3 sont reçus sur vecteurs fournis en B3f. Raccordement aux cellules engagées reçu et refus des bras EXACT et T7 avant inférence. Frontière Tango de discordance totale reçue pour la comparaison descriptive de la fixture. Trois contrastes confirmatoires seuls à α/3, autres cellules descriptives et pilote littéral PILOT_ONLY. Φ et m invariants après empoisonnement ALT. Trois blocs altérés refusés. |
| T31 | PASS | Comparaison FULL_K non conditionnée | test_b3f_full_k_claim_not_gated_and_family_data_isolated ; test_b3f_head_claim_statuses_null_qualification_and_multiplicity ; C0 | H3 calculée et rapportée sur F2 malgré l’échec de H1 ou le NULL_FAILED de PREFIX. Ses vecteurs et statuts restent propres à sa paire. |
| T32 | PASS | NULL_PLAN/HOLD indépendants | test_null_plan_phase_freezes_primary_p_conf_alarms_under_the_received_plan_rule_then_reloads ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; C0 ; lot-B3d-green.checks.log | Seuils CAL gelés, clés NULL_PLAN et HOLD disjointes. n_hold haché et engagé avant tout tirage HOLD. Exactement n_hold trajectoires neuves au primaire. Reprise sur ALT empoisonné sans effet ni lecture du contenu. |
| T33 | PASS | Prior DEV gelé | test_dev_qbar_averages_the_four_balanced_dev_families_with_equal_weights ; test_dev_library_block_stacks_the_received_q_of_each_planned_devlib_key_in_order ; test_dev_library_block_refuses_bad_admission_metadata_before_any_producer_call ; test_dev_library_block_stops_at_a_bad_second_producer_output_without_retry_or_partial_payload ; test_dev_library_block_keeps_legitimate_all_zero_q_rows_without_fallback ; test_dev_library_cache_commits_four_family_batches_per_setup_with_actual_hashes_and_qbar ; test_dev_library_cache_refuses_a_setup_claim_equal_only_by_python_aliasing ; test_dev_library_cache_refuses_a_float32_t7_batch_before_any_missing_producer ; test_dev_library_cache_runs_the_real_block_on_five_coordinates_in_full_and_smoke ; test_dev_library_cache_returns_an_empty_library_for_a_market_only_scope ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_dev_phase_rejects_a_corrupt_committed_dev_record_without_repair_or_recompute ; C0 | Le contrôleur fige qbar, d_dev, s2_dev et dev_id. Octets identiques au rechargement avec quatre phases ultérieures empoisonnées. Bibliothèque équilibrée et clés DEV disjointes. |
| T34 | PASS | Identités sensibilité gamma | test_gamma_sensitivity_policy_moves_only_the_online_mix_w128_cost_to_m_of_h_over_alpha ; test_gamma_sensitivity_policy_refuses_one_forged_field_or_unplanned_variant_before_any_cost ; test_gamma_sensitivity_online_bundle_changes_real_masks_and_scan_of_one_supplied_window ; test_policy_rule_hashes_the_effective_online_mix_w128_recipe_for_both_declared_budgets ; test_policy_rule_primary_ids_ignore_declaration_order_scope_horizon_metadata_and_external_decoys ; test_policy_rule_refuses_one_malformed_declaration_flag_or_unplanned_variant_before_hashing ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3h_descriptive_contrasts_pair_nonoracle_cells_with_primary_baselines_and_separate_the_oracle ; test_b4z_cli_keeps_fallback_prior_and_gamma_cells_separate ; C0 | B4z relie deux identités gamma distinctes aux seuils CAL et à quatre sélections au budget H/alpha. Huit sélections conservent 504. Les sensibilités gamma sont limitées aux deux politiques ONLINE MIX W128. |
| T35 | PASS | EIGENMEAN | test_frozen_policy_keeps_supplied_spectral_rows_as_local_static_masks_or_their_statuses ; test_b4y_cli_keeps_spectral_subsets_and_unrunnable_statuses ; C0 | B2b compare la moyenne de covariance à la règle de Kaiser sur corrélation. B4y vérifie les sous-ensembles attendus pour deux dimensions EXACT et un ajustement LW, leurs masques HOLD/ALT et leurs cardinalités publiées. |
| T36 | PASS | CPV global/résiduel | test_frozen_policy_keeps_supplied_spectral_rows_as_local_static_masks_or_their_statuses ; test_b4y_cli_keeps_spectral_subsets_and_unrunnable_statuses ; C0 | B4y vérifie CPV90 global et résiduel dans les deux univers sur trois setups. EXACT MARKET passe à k90=17 pour N=32 et reste hors univers pour N=239. Les statuts sans sous-ensemble n’ouvrent aucune cellule CAL. |
| T37 | PASS | Préfixe DEV unique | test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; C0 | Un d_dev par setup, calibré par candidat sur DEV_NULL, sélection équilibrée sur quatre familles, égalités déterministes et politique gelée. Témoin groupé B2w et choix purs B2v. |
| T38 | PASS | ONLINE isolé du simulateur | test_projection_offsets_feed_only_the_offline_null_bias_and_never_an_online_policy ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3i_hold_selection_telemetry_reads_the_full_committed_primary_online_info_mask_through_hold_only ; test_b3k_null_axis_bias_diagnostic_joins_verified_fitted_and_exact_hold_telemetry_with_the_frozen_fitted_center ; lot-B3k-green.checks.log ; test_b4u_nonoracle_dependency_ast ; test_b4u_alt_monitor_ignores_poisoned_simulator_metadata ; C0 | Signature ONLINE exacte et AST sans dépendance aux valeurs vraies. Les pièges bloquent les appels au simulateur et à l'oracle depuis le scan non-oracle. Les six métadonnées ALT modifiées laissent les résultats identiques. |
| T39 | PASS | Oracle FITTED surrogate | test_projection_diagnostics_return_received_gaussian_numbers_labelled_as_a_t7_proxy ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3j_masked_alt_information_matches_hand_subset_kl_and_per_day_cost_on_exact_fitted_and_proxy_witnesses ; lot-B3j-green.checks.log ; test_b4i_export_alt_selections_offline_from_staging ; test_b4x_cli_fitted_oracle_reports_surrogate_and_joint_separately ; C0 | B2n et B3j couvrent les projections Gaussian et T7. B4i relit les masques ALT EXACT et T7 et exporte les labels et les valeurs d'information jointes. B4x vérifie sur deux familles la publication FITTED, les qualifications et les mesures indépendantes avec masques ALT et identités CAL figés. |
| T40 | PASS | Télémétrie sélection et coût | test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_b3i_selection_telemetry_counts_axes_sizes_switches_and_theoretical_units_on_hand_witnesses ; test_b3i_hold_selection_telemetry_reads_the_full_committed_primary_online_info_mask_through_hold_only ; lot-B3i-green.checks.log ; test_b3m_oracle_mask_alignment_reports_first_exact_set_match_and_mean_daily_jaccard_of_static_oracle_rows ; test_b3m_offline_diagnostics_compare_the_verified_primary_online_info_alt_mask_with_its_own_f2_oracle_on_all_days ; lot-B3m-green.checks.log ; C0 | Masques HOLD stockés et égaux aux références sur tout H. Fréquences, cardinalités, commutations, seuil CAL et unités analytiques exacts. Fréquences H0 lues sur le masque HOLD engagé malgré ALT altéré et alarmes précoces. Atteinte exacte et Jaccard sur tout H vérifiés en B3m contre l’oracle de la même famille ALT. |
| T41 | PASS | Clés de rôles disjointes | test_setup_phase_covers_two_n_and_two_fit_ids_in_full_and_no_go_smoke ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_null_plan_phase_freezes_primary_p_conf_alarms_under_the_received_plan_rule_then_reloads ; test_hold_phase_draws_one_family_free_cohort_per_setup_and_checks_every_cal_cell_at_its_frozen_h_then_reloads ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_confirmatory_from_staging_bootstraps_each_claimed_family_once_on_committed_primary_cells_then_replays ; test_b3h_descriptive_contrasts_consume_committed_primary_f2_cells_and_keep_the_same_family_oracle_separate ; test_b4v_cli_full_publishes_committed_confirmatory_claims_once ; test_b4w_cli_publishes_descriptive_contrasts_with_shared_bootstrap ; C0 | Clés disjointes à toutes les phases et bruit sans famille. B4v rattache les clés bootstrap au plan. B4w vérifie par comptage un tirage par clé pour les contrastes full et pilot. Les revendications full partagent les matrices avec les contrastes descriptifs. |
| T42 | PASS | KL exact/surrogate distincts | test_projection_diagnostics_return_received_gaussian_numbers_labelled_as_a_t7_proxy ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3j_masked_alt_information_matches_hand_subset_kl_and_per_day_cost_on_exact_fitted_and_proxy_witnesses ; lot-B3j-green.checks.log ; test_b3k_masked_alt_information_keeps_a_finite_path_mean_when_repeated_near_max_days_overflow_a_daily_fsum ; lot-B3k-green.checks.log ; test_b4i_export_alt_selections_offline_from_staging ; test_b4x_cli_fitted_oracle_reports_surrogate_and_joint_separately ; C0 | B2n/B3j/B3k couvrent projections, gardes et valeurs de sous-ensembles. B4i exporte les informations additive et jointe dans deux colonnes, avec qualification EXACT et proxy T7. B4x vérifie sur la publication FITTED les moyennes jointes et diagonales reconstruites par Cholesky et leurs ratios quotidiens. Les deux informations diffèrent sur la fixture. |
| T43 | PASS | Calibration de rang | test_calibrate_nonoracle_ranks_the_timewise_maxima_of_one_real_scan_at_the_sealed_ge_boundary ; test_calibrate_nonoracle_is_invariant_to_cal_row_permutation_and_identical_on_replay ; test_calibrate_nonoracle_counts_tied_maxima_conservatively_at_the_sealed_ge_boundary ; C0 | Maxima temporels, seuil GE au nextafter exact, rangs et comptes, rejeu et égalités conservatrices vérifiés sur tableaux déterministes. |
| T44 | PASS | Invariance jobs sur fixture | test_b4c_score_path_batch_jobs_one_and_three_stack_the_serial_path_scores_bytes_in_requested_order ; test_b4e_phase_controllers_route_path_scores_through_score_path_batch ; test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; C0 | B4f vérifie les six phases et les 13 partitions. B4m compare ces octets et les publications scientifiques du CLI à 1 et 3 workers réels. Profilage en C. |
| T45 | PASS | Reprise et refus stale | test_setup_phase_refuses_each_corrupt_or_foreign_setup_state_without_repair ; test_setup_phase_reproduces_an_orphan_fit_npz_and_reuses_the_durable_frame ; test_setup_phase_covers_two_n_and_two_fit_ids_in_full_and_no_go_smoke ; test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three ; test_b4g_cal_scoring_deadline_records_blocked_status_then_resumes ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; test_b4n_cli_recovers_each_atomic_publication_boundary ; test_b4p_cli_resumes_after_each_committed_phase ; test_b4q_cli_refuses_stale_phase_and_partition_state ; C0 | Le CLI reprend après les quatre phases, de part et d'autre du renommage atomique et après FINAL. Sept états incohérents sont refusés sans effet sur le staging ni la publication. |
| T46 | PASS | Refus ressource reprenable | test_setup_phase_blocks_a_complete_reload_whose_current_cpu_reaches_the_cap ; test_setup_phase_blocks_a_complete_reload_after_the_invocation_wall_deadline ; test_guarded_partition_blocks_after_its_producer_exhausts_budget ; lot-B4d-green-v2.checks.log ; test_b4g_cal_scoring_deadline_records_blocked_status_then_resumes ; test_b4r_cli_blocks_at_publication_budget_boundary ; C0 | B4g couvre l'échéance dans CAL. B4r bloque les deux publications CLI aux bornes exactes après export. Le statut est reprenable après échéance mur. Le CPU cumulé à la borne reste bloquant. |
| T47 | PASS | Autorisation avant effets | test_setup_phase_refuses_each_poisoned_admission_axis_before_any_effect ; test_b4a_cli_run_preflight_refuses_an_unauthorized_pilot_or_full_before_any_effect ; test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; test_b4o_cli_pilot_and_full_authorize_before_realization ; test_b4s_phase_driver_refuses_bad_admission_before_effects ; C0 | Autorisation avant effets vérifiée en SETUP, dans le CLI et dans le pilote de phases. B4s refuse descripteur, autorité, plan, jobs et digest GO incohérents sous pièges. B4o publie les deux modes autorisés sur fixtures. |
| T48 | PASS | Aucun accès réel | test_no_real_data_access ; C0 | AST sans chargeur de données, chemin data ni date 2020+. Le CLI full de fixture publie sous pièges d'ouverture et d'énumération ciblant les chemins de données. |
| T49 | PASS | V/RMST diagnostic hors ligne | test_export_selections_writes_full_horizon_analytic_values ; test_b3j_masked_alt_information_reads_the_full_committed_primary_alt_mask_only_after_its_hashes_verify ; test_b3j_v_rmst_diagnostic_ranks_each_setup_application_group_apart_and_leaves_undefined_groups_none ; lot-B3j-green.checks.log ; test_b3k_masked_alt_information_keeps_a_finite_path_mean_when_repeated_near_max_days_overflow_a_daily_fsum ; lot-B3k-green.checks.log ; test_b4i_export_alt_selections_offline_from_staging ; test_b4j_export_trial_summaries_compact_hold_alt_rows ; test_b4k_export_aggregates_descriptive_v_rmst ; C0 | B3j/B3k vérifient Vbar et le Spearman DESCRIPTIVE_V_RMST par groupe. B4i exporte Vbar surrogate et joint sur tout H après vérification des masques. B4j fournit les RMST depuis ALT. B4k joint les cellules ALT et leurs SHA et vérifie le CSV descriptif sans simulation, rang CAL ou sélection. |
| T50 | PASS | Manifeste et chemins relatifs | test_finalize_local_inventory_is_staging_relative_and_outside_identity ; test_finalize_publishes_verified_phases_and_writes_final_marker ; test_publish_enforces_the_50_mib_limit_from_stat_metadata ; test_b4l_finalize_publishes_exported_scientific_payloads ; C0 | B4l compare les cinq CSV publiés et l'inventaire LOCAL_HASHED_ONLY des 13 partitions aux octets. Aucun NPZ n'est publié. Noms POSIX relatifs et limite de taille vérifiés par les tests B1. |
| T51 | PASS | Score fluide oracle | test_tiny_oracle_fluid_score_dominates ; C0 | Énumération des 255 sous-ensembles non vides sur huit axes dans C0. Résultat limité au score fluide. |
| T52 | PASS | Design avant tirage | test_design_id_computable_before_any_draw ; test_b4a_cli_describe_prints_the_pure_pilot_identity_without_go_outputs_or_prior_state ; lot-B4a-green.final-checks.log ; C0 | Descripteur sur liste blanche et identité déterministe sous pièges. Deux appels CLI avec YAML de fixture et GO nul, identité indépendante des options d'invocation, lectures limitées au YAML et aux sources hachées. CLI direct et module concordants. |
| T53 | PASS | Autorisation sans valeurs futures | test_finalize_publishes_verified_phases_and_writes_final_marker ; test_finalize_is_idempotent_and_refuses_foreign_or_corrupt_state ; test_b4o_cli_pilot_and_full_authorize_before_realization ; C0 | Les deux modes de fixture publient avec un GO émis depuis le seul design pré-exécution. Une modification de graine change ce design. Le GO reste intact et le manifeste lie le design autorisé à la réalisation calculée. |
| T54 | PASS | Design/code/graine/limites altérés | test_altered_design_code_seed_limit_refused_before_side_effects ; test_authorize_refuses_python_equal_noncanonical_descriptor ; test_b4a_cli_run_preflight_refuses_an_unauthorized_pilot_or_full_before_any_effect ; C0 | Altérations de cfg/code/limites et deux alias de type canoniques refusés sous pièges. Changement de graine après GO aussi refusé par le CLI. |
| T55 | PASS | GO absent/non concordant | test_pilot_full_authorization_without_future_digests ; test_b4a_cli_run_preflight_refuses_an_unauthorized_pilot_or_full_before_any_effect ; C0 | Cas absence/SHA/citation/stage/jobs et smoke procédural reçus. CLI testé pour GO nul en pilote et full, et dépassement de jobs. |
| T56 | PASS | Identités sans chemins/jobs/télémétrie | test_open_staging_distinct_log_dirs_are_independent ; test_publish_keeps_local_only_metadata_and_identities_across_roots ; test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; C0 | Deux publications CLI indépendantes à 1 et 3 workers avec basename commun et log-dir distincts. Même design, réalisation, manifeste et CSV. Télémétrie distincte. Logs partagés sans reprise refusés. |
| T57 | PASS | Reprise après phases | test_setup_phase_recovers_each_interruption_into_the_reference_record ; test_run_phases_drives_admitted_staging_identically_for_jobs_one_and_three ; test_b4g_cal_scoring_deadline_records_blocked_status_then_resumes ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; test_b4p_cli_resumes_after_each_committed_phase ; C0 | Quatre interruptions après les commits SETUP, DEV, CAL et NULL_PLAN réel. Chaque reprise retrouve les octets et la réalisation de sa référence. Les rôles déjà engagés, le choix DEV et les seuils CAL ne sont pas recalculés. |
| T58 | PASS | Phases/partitions incohérentes | test_setup_phase_refuses_each_corrupt_or_foreign_setup_state_without_repair ; test_b4q_cli_refuses_stale_phase_and_partition_state ; C0 | Sept refus par CLI couvrent le design étranger au même tag, le digest amont, les deux bornes de n_hold, HOLD sans NULL_PLAN et le NPZ HOLD modifié ou manquant avec sidecar intact. |
| T59 | PASS | Réalisation sans manifeste/chemins | test_finalize_publishes_verified_phases_and_writes_final_marker ; test_realization_id_ignores_locations_ordering_and_manifest_files ; test_b4l_finalize_publishes_exported_scientific_payloads ; C0 | B4l recalcule l'identité de réalisation depuis les empreintes des cinq CSV et vérifie FINAL. B1 couvre le déplacement et l'exclusion des fichiers de manifeste, résumé et télémétrie. |
| T60 | PASS | Publication atomique | test_finalize_recovery_binds_local_claims_to_the_staged_records[temp_wrong_local_sha] ; test_b4l_finalize_publishes_exported_scientific_payloads ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; test_b4n_cli_recovers_each_atomic_publication_boundary ; test_finalize_is_idempotent_and_refuses_foreign_or_corrupt_state ; C0 | B1 couvre les refus de destinations et temporaires étrangers. B4l vérifie INCOMPLETE sans publication. B4n injecte les interruptions autour du renommage du bundle. La reprise conserve les octets scientifiques et le manifeste lié à FINAL. |
| T61 | PASS | run_id alias pré-exécution | test_open_staging_creates_tagged_design_record ; test_publish_refuses_inconsistent_prepared_handoff_before_replace ; test_b4n_cli_recovers_each_atomic_publication_boundary ; C0 | B4n dérive le tag du design avant exécution et vérifie les chemins par défaut des résultats, des logs, du staging et du temporaire frère. La réalisation calculée à la publication ne figure dans aucun de ces chemins. |
| T62 | PASS | Enveloppe et identités | test_setup_phase_blocks_a_complete_reload_whose_current_cpu_reaches_the_cap ; test_setup_phase_blocks_a_complete_reload_after_the_invocation_wall_deadline ; test_dev_phase_blocks_on_budget_and_keeps_an_unmasked_choice_error_without_committing ; test_dev_phase_commits_role_scores_choices_and_frozen_ids_then_reloads_them ; test_b4g_cal_scoring_deadline_records_blocked_status_then_resumes ; test_b4m_admitted_cli_serial_refusal_parallel_resume ; test_b4r_cli_blocks_at_publication_budget_boundary ; C0 | B4r vérifie les bornes CPU et mur, le registre cumulatif sur deux invocations et la sensibilité du design au changement d'une limite. Jobs reste hors identité. Mesure agrégée et profilage en C. |
| T63 | PASS | HEAD censuré non probant | test_b3f_head_claim_statuses_null_qualification_and_multiplicity[T63_all_head_paths_censored] ; C0 | Tous les chemins censurés. U_PREFIX=H et borne NI brute négative. Contrôle invalide et statut NONINFERIORITY_NOT_PROBATIVE. |
| T64 | PASS | Géométrie HEAD | test_head_geometry_exact_frame_keeps_every_profile_in_the_first_four_axes ; test_head_geometry_fitted_fractions_match_independent_joint_references ; test_setup_phase_caches_one_frame_then_two_fits_and_commits_the_received_metadata ; test_setup_phase_commits_an_inconclusive_head_once_and_reloads_it_without_reroll ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_confirmatory_from_staging_bootstraps_each_claimed_family_once_on_committed_primary_cells_then_replays ; lot-B3f-green.checks.log ; C0 | 16 profils EXACT et symétrie, rotation FITTED inconclusive, information nulle inconclusive. Un fit par coordonnée, delta et support gelés. Géométrie engagée avant ALT, reprise sans refit et lecture de la géométrie engagée pour H2 en B3g. |
| T65 | PASS | Seuils HEAD gelés et isolés | test_setup_phase_commits_an_inconclusive_head_once_and_reloads_it_without_reroll ; test_setup_bundle_fit_hash_tracks_the_learned_mean_and_kappa_det_never_routes_geometry ; test_alt_phase_scores_each_family_trial_once_with_its_raw_delta_at_every_frozen_cal_cell_then_reloads ; test_b3f_head_control_exact_thresholds_and_nextafter ; test_confirmatory_from_staging_bootstraps_each_claimed_family_once_on_committed_primary_cells_then_replays ; test_setup_bundle_head_status_reads_only_the_descriptor_kappa_geo ; test_cal_phase_commits_one_family_free_threshold_per_policy_and_per_family_oracles_then_reloads_or_refuses ; test_b3l_t65_h2_head_row_ignores_a_committed_f2_info_decoy_and_poisoned_smoke_outputs_on_staged_replay ; lot-B3l-tests.checks.log ; C0 | Routage κ/identités, statut inconclusif sans relance et isolement local PASS ; isolement lors des scans ALT reçu. Détectabilité au seuil κ_det et frontière nextafter reçues en B3f. Géométrie SETUP et U_PREFIX raccordés en B3g. F2 modifié à provenance engagée cohérente et fichiers smoke de fixture sous pièges. Les RMST INFO H1/H3 changent. H2 complet, κ, géométrie, U_PREFIX et clés bootstrap restent identiques. |
| T66 | PASS | HEAD valide mais NI échouée | test_b3f_head_claim_statuses_null_qualification_and_multiplicity[T66_valid_control_info_slower] ; C0 | Contrôle HEAD valide, INFO plus lent et borne NI positive. Statut NOT_ESTABLISHED. |
| T67 | PASS | Frontières HEAD/nul/multiplicité | test_b3f_head_control_exact_thresholds_and_nextafter ; test_b3f_head_claim_statuses_null_qualification_and_multiplicity ; test_b3f_paired_bootstrap_bounds_follow_each_family_shared_index_matrix ; test_b3f_t67_ni_upper_exact_zero_boundary_is_not_established ; lot-B3f-green.checks.log ; C0 | Seuils inclusifs, qualification nulle par paire, α/3 et mêmes indices par famille. À la marge stricte, les zéros NI/gain restent nuls, y compris après interpolation. |
| T68 | PASS | Design indépendant des sorties | test_smoke_or_prior_outputs_cannot_inform_design ; test_b4a_cli_describe_prints_the_pure_pilot_identity_without_go_outputs_or_prior_state ; test_b4t_design_and_config_ast_exclude_prior_outputs ; C0 | Descripteur et YAML vérifiés par AST. Le CLI --describe reste indépendant des manifestes et stagings smoke/pilot empoisonnés sous les pièges d'accès fichiers. |

## Vérifications runtime du lot C

Les 68 contrats sont PASS dans le périmètre des fixtures B. Les quatre vérifications
runtime sont reçues sous les GO distincts [C1–C3](GO-stream-32-C-20261120.md)
et [C4](GO-stream-32-C4-20261120.md). [Réception du lot C](RECEIPT-stream-32-C-20261120.md)

| Vérification de campagne | Statut | Preuve mesurée |
| --- | --- | --- |
| Smoke de bout en bout avec les paramètres candidats et publication atomique | PASS | Code 0, cinq CSV FAIR vérifiés, renommage atomique avant FINAL. Le `NULL_PLAN` a engagé 40 lignes et fixé `n_hold=80`. [Audit C1](../logs/stream-32/lot-c-c1.audit.json) |
| Reprise après SETUP, DEV, CAL et NULL_PLAN aux tailles candidates | PASS | Quatre coupures au code 75, quatre reprises au code 0, zéro reproduction de partition engagée et zéro recalibration. Identité et empreintes identiques à C1. [Audit C2](../logs/stream-32/lot-c-c2.audit.json) |
| Identités et empreintes scientifiques identiques entre jobs 1 et 8 | PASS | Destinations et journaux distincts. Les deux designs, réalisations et jeux de cinq SHA-256 concordent avec C1. [Audit C3](../logs/stream-32/lot-c-c3.audit.json) |
| Profilage 1/4/8/12 et mesure agrégée des ressources | PASS | Quatre profils reçus sous le design C4, cinq SHA-256 identiques et zéro événement OOM. Temps mur 300,54 à 326,67 s, pic mémoire 195,20 à 1 435,47 Mio, empreinte 36,97 Mio. [Audit C4](../logs/stream-32/lot-c-c4.audit.json) |

Le pilote et le full exigent leurs propres décisions du chercheur.

Disposition des reports A : `docs/DEVIATIONS.md`, C-pca-info-online-A-integration-deferrals.
Les six seuils de réception B T10, T15, T16, T19, T21 et T22 sont couverts
par les témoins consignés dans leurs lignes.
