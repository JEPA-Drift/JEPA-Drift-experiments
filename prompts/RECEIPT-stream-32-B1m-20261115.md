# Stream 32 — réception B1m, invocation et partition gardée

Date : 15 novembre 2026. Décision Codex : **B1m REÇU, COMPOSANT LIMITÉ**.
Autorité : GO B-TDD et réception B1l. Aucun GO runtime ou scientifique.
T46/T62, B1 et B restent ouverts ; seule la composition testée ci-dessous est reçue.

Reçu : _cpu_now, start_invocation et guarded_partition. L'invocation possède un jeton frais,
une ligne de base CPU SELF+CHILDREN et un départ mural ; une partition est précédée d'un
pointage et de require_budget, puis suivie d'un pointage après retour ou exception.
Contexte interne de confiance, callback revenu après jointure par contrat de l'appelant.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Mesure CPU | ACCEPTED | Quatre champs os.times validés individuellement puis sommés par fsum ; elapsed ignoré. Faux compteurs déterministes, aucune mesure de campagne. |
| Invocation et reprise | ACCEPTED | Autorité/plan/design contrôlés avant token0 ; CPU et mur finis/non négatifs, jeton existant refusé sans remise à zéro. Nouvelle invocation conserve les dépenses précédentes. |
| Producteur effectivement gardé | ACCEPTED | CPU/mur à leurs bornes bloquent avant partition/producer, statut véridique, caches intacts et aucune publication/FINAL. |
| Pointages et cache | ACCEPTED | Référence0.5s avant producteur,2s après retour,2.25s après succès de cache ; pas de double compte ni nouvelle production sur cache. |
| Exceptions et invalidité | ACCEPTED | Exception après travail partiel pointée à5.5s ; recul et non-finitude refusés sans baisser le journal ni engager une partition. |
| Réemploi et préservation | ACCEPTED | Ajouts seuls en fin de module, préfixe source63608octets identique ; aides reçues réemployées,235cas figés, aucune dépendance ou signature antérieure modifiée. |
| Contre-revue indépendante | ACCEPTED | Aucun défaut matériel dans le composant borné ; relecteur distinct, sans exécution/mutation. Conditions235passés et pyflakes observées séparément par Codex. |
| Épuisement post-unité | MODIFIED | Consommation pointée après unité, sans recontrôle du plafond dans ce composant. Garde à l'opération suivante et avant engagement/finalisation dans le driver reste obligatoire. |
| Double exception | MODIFIED | Échec du pointage final propagé avec l'erreur producteur dans le contexte Python ; aucun avalement ni reset. |
| Enforcement complet | REJECTED | CPU avant crash/hors checkpoints, borne externe dure, vrais workers/jointures/jobs, driver et mémoire agrégée restent bloquants. Aucune garantie réelle4CPUh déduite des fixtures. |
| Clôture globale | REJECTED | Calendrier scientifique/consommation, LOCAL_HASHED_ONLY, bundle/T16 global, CLI, cohortes/graines/raccordements A/T68 encore dus ; aucun contrat complet T46/T62/B1/B reçu. |

Sous .venv/environnement déterministe/verrou : RED **7failed228passed en8.94s**,
puis GREEN **235passed en7.82s**, pytest/contrôles GREEN exit0, pyflakes/diff-check propres.
Fichier de tests163443octets inchangé pendant GREEN ; campagne ciblée235cas dont9registre.
Patch46lignes source seule lu intégralement/appliqué nativement et relu après application.

| Pièce | SHA-256 |
|---|---|
| Source finale | `780d6c7cbeb700f8ac87b0c21fe3cc8ca68ca881a6676d2b70a08c8fd6d03488` |
| Tests figés | `dfa8c8a430186acbbd01b60a7ee162f697872c3641e904c7586d11e17bf845a3` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète | `2c36221324198ec16f5d8228109838385be4d87fa8d832f08e089faa6d82775f` |
| Journal pytest GREEN | `b55b7f50dc78fd6e7b525512d9338e6b2d53c349e84282a6e4b9a2d033eeeb05` |
| Journal contrôles GREEN | `826e8c89de8f830face00ec58b147451c3fb3ea48e7b498f151eddd8b1a4d0fc` |

Revue RED et dispositions : REVIEW-stream-32-B1m-red-20261115.md ; scripts check-B1m-*.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; succès partiels jamais promus en contrats complets.
Suite bornée : tests seuls du raccordement LOCAL_HASHED_ONLY aux partitions effectivement
vérifiées lors de la finalisation et de la reprise, sous tmp_path, sans nouvelle API de campagne.
Le contrôle global des ressources reste une condition de réception B avant tout runtime ; les
gardes d'engagement/finalisation devront être consommées par le driver enB4.
LotC/runtime/smoke de campagne/profilage/pilote/full, données réelles/2020+, JEPA et autres
streams fermés. Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
