# Stream 32 — réception technique B1d, partitions atomiques

Date : 14 novembre 2026. Décision Codex : **B1d REÇU, CACHE DE PARTITIONS TECHNIQUE UNIQUEMENT**.
Autorité : GO B-TDD distinct après réception B1c, plan v2.1 inchangé.
Ni les producteurs scientifiques, ni B1 entier, ni le lotB ne sont reçus par cette décision.

Reçu : `partition(staging,phase,upstream,key,produce)`, chargement des tableaux depuis les mêmes
octets vérifiés que leur SHA, récupération des orphelins en phase incomplète, engagement atomique
NPZ puis sidecar JSON. Une phase engagée est rechargée/vérifiée avant la lecture d'une clé listée.
Aucune corruption n'entraîne un recalcul silencieux ; aucune nouvelle clé ne rejoint une phase engagée.

## Preuves et dispositions

| Étape | Résultat observé sous .venv/environnement déterministe/verrou |
|---|---|
| Premier RED proposé | Non appliqué ; deux témoins de phase engagée ajoutés après contre-revue. |
| RED v2 | 22failed,72passed en2.90s ; assertions explicites de fonction absente. |
| GREEN | **94passed en1.74s**, pyflakes et diff-check propres, pytest/checks exit0. |
| Préservation | Préfixe63219octets des72 tests conservé au RED ; tests inchangés pendant GREEN. |
| Contre-revues | Tests v2 acceptés avant application ; intégrité/atomicité GREEN acceptées après vérifications. |

| Pièce | SHA-256 |
|---|---|
| Source finale | `fb78971d391f02cac17fb36caacd3605d61952516e7e4cb75a4f5684c59b29c2` |
| Tests | `155fbdf12eadcd64a1cb4c0436fe664337e8877fee57e4d32870ccc4eeccc8c1` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète, exit0/erreur vide/is_error=false | `f0f0470ec01f01a28a19ea70cea5128c4a0339fcad8836124df5c89c9c989a42` |
| Journal pytest GREEN | `e9ee69c05e1f4902fc09b312e930e9cdd07c583347dd73d181c693556c0b6f06` |
| Journal contrôles GREEN | `1af35a3d98c18414db3dc18962cd128ffd7467cdd6535a46eb6f772dadf9f3bb` |

Script `logs/stream-32/check-B1d-green.sh`, preuves `logs/stream-32/lot-B1d-green.*`.
Décisions détaillées : `REVIEW-stream-32-B1d-red-20261114.md`.
Adaptations privées reçues : écriture atomique texte ou octets, chemin d'empreinte partagé,
retour des tableaux du vérificateur partagé ; schéma public B1c inchangé, appelants contrôlés.
NPZ déterministe par NumPy épinglé avec noms triés et pickle refusé, sans écrivain ZIP dédié.

## Réserves et tranche suivante

La validation de l'upstream des phases encore incomplètes reste syntaxique à ce stade.
Avant tout raccordement aux producteurs, la lignée effective de leurs prédécesseurs doit être
vérifiée avant callback/écriture ; cette obligation est transférée explicitement à la tranche B1e.
Les phases déjà engagées ont la validation complète reçue et couverte par les nouveaux témoins.

T45/T50/T57/T58 restent partiels ; **matrice68 conservée,18PASS/0FAIL/50NOT_RUN**.
États NULL_PLAN/HOLD/ALT/FINAL, reprise des producteurs, ressources/status, réalisation/publication,
T16 sur vrais exports, CLI, graines consommées, intégrations A et T68/os.open restent dus.
Aucune preuve de puissance, de FPR empirique ou de coût runtime produite par ces fixtures.

Tranche suivante permise : **tests RED B1e de la lignée effective et des états après CAL**,
sur fixtures de records et partitions seulement. Applicabilité de NULL_PLAN et n_hold enregistré
avant HOLD à spécifier pour revue ; aucune étape scientifique exécutée et aucun producteur ajouté.
LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun commit/push/réindexation ou RemoteControl.
