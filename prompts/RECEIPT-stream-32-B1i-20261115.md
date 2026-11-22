# Stream 32 — réception technique B1i, finalisation sur records vérifiés

Date : 15 novembre 2026. Décision Codex : **B1i REÇU, COMPOSANT DE FINALISATION UNIQUEMENT**.
Autorité : GO B-TDD et réception B1h ; plan v2.1 et toutes les portes scientifiques inchangés.
T60, B1 et B restent ouverts ; aucun GO de runtime ou de campagne.

Reçu : finalize(staging,output_dir,authority,build), après six records existants vérifiés avec
leurs partitions. Construction du handoff à partir des CSV réels, réalisation acyclique et
publication atomique reçue ; FINAL quatre champs séparé des phases et des identités scientifiques.
Le callback d'export reste de confiance ; les tests emploient le vrai export_selections et des
CSV synthétiques minuscules. Les fixtures GO full/pilot n'autorisent aucune campagne.

| Observation | Décision | Justification / tests |
|---|---|---|
| Identités et autorité | ACCEPTED | GO synthétique réellement autorisé avant les phases ; manifeste sept champs, SHA des octets et réalisation recalculée depuis les records ; même autorité à la reprise. |
| Préservation DEV/CAL | ACCEPTED | Chargement vérifié, copie des records fournie au builder, pièges de recalcul ; octets du staging et de la publication préservés. |
| Reprise avant/après rename et FINAL | ACCEPTED | Reconstruction du temporaire possédé avant rename ; après rename, zéro callback/réécriture publique puis FINAL ; idempotence et corruptions refusées. |
| Propriété du temporaire | MODIFIED | V1 non appliquée ; v2 refuse la simple revendication du DID et les notes étrangères. Marqueur privé strict/inventaire régulier ou publication complète correspondante avant suppression. |
| Taille50Mio avant contenu | MODIFIED | Défaut reproduit par EdgeRED puis garde inclusive avant tout hash ; contrôle à la limite accepté sans gros fichier réel. |
| Durabilité de reprise | MODIFIED | Défaut reproduit par EdgeRED puis fsync du parent avant engagement FINAL ; ordre des syscalls et préservation publique contrôlés. |
| Contre-revue | ACCEPTED | Revue indépendante initiale a identifié les deux défauts ; contre-revue finale Codex distincte de l'auteur. Sous-agent final indisponible sur quota : aucun avis supplémentaire inventé. |
| Réception T60/B1/B complète | REJECTED | Complétude des clés planifiées, INCOMPLETE/status/ressources, autres exports/T16 global et raccordements scientifiques/CLI/cohortes/T68 restent bloquants. |

Preuves sous .venv/environnement déterministe/verrou : REDv2 **17failed171passed en6.57s**,
GREEN initial188passed5.73s, EdgeRED **2failed189passed en6.45s**, puis
EdgeGREEN **191passed en5.93s**. Pyflakes et diff-check propres ; pytest/contrôles GREEN exit0.
Aucun test supprimé ou affaibli ; préfixes antérieurs inchangés, tests figés pendant les GREEN.

| Pièce | SHA-256 |
|---|---|
| Source finale | `c0ffe9cef6c3dd977555b2305e37b9f0a304eef47a7463804232003287f6e607` |
| Tests191cas/129932octets | `ff58fed89c922a1fe9364ef4148391991f4cda64e5ea61febd2a38c487c8f8c9` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture EdgeGREEN complète | `4d1edce95a27faf73d9b7441aa3465b8b9ec6a27ce8e05912dc0d36da48bddf4` |
| Journal pytest EdgeGREEN | `8d1f6d266a7a4159c3cfdf56ed633b67a319c6d56884d1be1949717d872e6852` |
| Journal contrôles EdgeGREEN | `cb7f259b7ed3713e8ca8083a077ce6a35ec8733becdd7453201fac5eaf46e609` |

Revues : REVIEW-stream-32-B1i-red-20261115.md et REVIEW-stream-32-B1i-green-20261115.md.
Scripts/preuves : check-B1i-*.sh et lot-B1i-* sous logs/stream-32.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; succès partiels non promus en contrats complets.

Suite bornée : témoins complémentaires des gardes de finalisation déjà présentes, tests seuls
avant toute éventuelle correction. Restent à témoigner : marqueurs/liens/non-régularité,
temporaire vide, FINAL présent avec publication absente ou autre GO, stage/mode/smoke.
Ces réserves doivent être suivies avant réception B1/B ; ni tests factices ni RED artificiel si
une garde existante passe déjà. La complétude planifiée/status/ressources reste une obligation
fonctionnelle distincte, non satisfaite par la vérification des seules partitions inscrites.
LOCAL_HASHED_ONLY raccordé, autres exports et T16 global, producteurs scientifiques/CLI/cohortes,
graines/T68 et reports A restent dus. TOCTOU hors portée du handoff local, callback de confiance.
LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation ou RemoteControl, aucun producteur scellé modifié.
