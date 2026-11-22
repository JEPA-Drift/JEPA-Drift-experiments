# Stream 32 — réception technique B1e, lignée et états après CAL

Date : 14 novembre 2026. Décision Codex : **B1e REÇU, ÉTATS DE MÉTADONNÉES UNIQUEMENT**.
Autorité : GO B-TDD distinct après réception B1d, plan canonique v2.1 inchangé.
Ni les producteurs/cohortes scientifiques, ni B1 entier, ni le lotB ne sont reçus par ce document.

Reçus : lignée effective des prédécesseurs avant callback des partitions incomplètes,
ordre SETUP→DEV→CAL→NULL_PLAN→HOLD→ALT, applicabilité issue du descripteur,
record NOT_APPLICABLE sans valeur réalisée, bornes/types/statut de n_hold et lignes HOLD gelées.
Les mêmes règles s'appliquent à la production de fixture, au cache, à l'engagement et au reload.

## Preuves et dispositions

| Étape | Résultat observé sous .venv/environnement déterministe/verrou |
|---|---|
| Premier RED proposé | Non appliqué ; fixture FULL plafonnée et refus FULL avant NULL_PLAN ajoutés après revue. |
| RED v2 | 6failed,94passed en2.45s ; manque de garde effective et de phases après CAL. |
| GREEN | **100passed en2.05s**, pyflakes et diff-check propres, pytest/checks exit0. |
| Préservation | Préfixe72404octets des94 tests conservé au RED ; tests inchangés pendant GREEN. |
| Contre-revues | Tests v2 et GREEN acceptés ; aucun défaut matériel identifié dans ce périmètre. |

| Pièce | SHA-256 |
|---|---|
| Source finale | `93e8319464bae949e14f5b69ab2e5328445fc9221e3aaa01cd3290daebc6a406` |
| Tests | `009feb1c5c83c2e985df6e1bfb4298fb395441c8c86dce73fbe4782c1de65db5` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète, exit0/erreur vide/is_error=false | `0b8a019a429ee7d04c7236c54f058eaffc83b0cbfd0048f9e5ade8d1b5634e7c` |
| Journal pytest GREEN | `385c80081a74aa94f6b45c07310c7f4053e12f8cd94a0a9ae5ea56dfc4fff1b5` |
| Journal contrôles GREEN | `743ba2d5e932e872bee72738f59dd3c1bc8b281a2804ef95aac0f0e4a33d3910` |

Script `logs/stream-32/check-B1e-green.sh`, preuves `logs/stream-32/lot-B1e-green.*`.
Décisions détaillées : `REVIEW-stream-32-B1e-red-20261114.md`.
Appelants de `_staged_design` et `_load_phase` recherchés et adaptés ; schémas publics antérieurs préservés.
Smoke adéquat, FULL plafonné (NULL_PLAN2/HOLD primaire5/EXACT1), pilote et portée sans primaire couverts en fixtures.

## Réserves et tranche suivante

La projection NULL_PLAN {status,n_hold,plan_id} est reçue pour les états seulement.
Comptes nuls, plug-ins, n_req, provenance de plan_id et cohortes indépendantes restent dus enB3.
Le digest du record NOT_APPLICABLE appartient à la lignée technique ; la réalisation doit encore
normaliser ce NULL_PLAN sauté en NOT_APPLICABLE selon §3.6. Aucun choix scientifique issu des fixtures.

T21/T45/T57/T58 restent partiels ; **matrice68 conservée,18PASS/0FAIL/50NOT_RUN**.
Rejeu des producteurs, FINAL/status/ressources, réalisation/publication, T16 sur vrais exports,
CLI, graines consommées, reliquats A et T68/os.open restent bloquants pour réception B.

Tranche suivante permise : **tests RED B1f de realization(records,payload_shas)**,
avec des records vérifiés et des payloads FAIR de fixture uniquement. Descripteur canonique,
exclusions, normalisation NOT_APPLICABLE et identités sans cycle ; production après RED/revue seulement.
Publication et T16 complet restent des tranches ultérieures, sans témoin sur constante factice.
LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun commit/push/réindexation ou RemoteControl.
