# Stream 32 — réception technique B1c, records SETUP/DEV/CAL

Date : 14 novembre 2026. Décision Codex : **B1c REÇU, RECORDS DE MÉTADONNÉES UNIQUEMENT**.
Autorité : GO B-TDD distinct après réception B1b, plan canonique v2.1 inchangé.
Ni les producteurs SETUP/DEV/CAL, ni B1 entier, ni le lotB ne sont reçus par ce document.

Reçus : `phase_record`, vérification des records/prédécesseurs/partitions, digest canonique
sans chemin ni cycle, lecture vérifiée sans réécriture et écriture atomique après les gardes.
Les clés sont primitives et uniques ; les octets NPZ hachés sont ceux chargés sans pickle ;
n_rows est contrôlé sur chaque tableau. JSON strict pour les records et dérivés.

## Preuves et dispositions

| Étape | Résultat observé sous .venv/environnement déterministe/verrou |
|---|---|
| RED | 9failed,63passed en2.08s, assertions explicites de fonction absente. |
| GREEN | **72passed en1.64s**, pyflakes et diff-check propres, pytest/checks exit0. |
| Préservation | Préfixe53239octets des63 tests conservé au RED ; tests inchangés pendant GREEN. |
| Contre-revues | Tests acceptés avant application ; revue indépendante d'intégrité GREEN favorable. |

| Pièce | SHA-256 |
|---|---|
| Source finale | `d915a90d5d28f7912276ff7e1f661ae0d992592ed1b769966fb3967dc3f1f87b` |
| Tests | `4232ef788536ea3333845c0376af9efbfba6918f3ac00278afe6ab256f3b0b09` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète, exit0/erreur vide/is_error=false | `2fcc0c63156fc4515fa87bd939df9cfebd2ff667554ac6ee23757a29fee25e48` |
| Journal pytest GREEN | `07c701043f4e680221ad043015f341cc35bf1359904bf5b993bc83adb61384f9` |
| Journal contrôles GREEN | `62d33fc62284f584b077b41c8ab2c5b7761f32c2e8033a475b1b81ddebb359e6` |

Script `logs/stream-32/check-B1c-green.sh`, preuves `logs/stream-32/lot-B1c-green.*`.
Décisions détaillées : `REVIEW-stream-32-B1c-red-20261114.md`.

La contre-revue ne relève aucun défaut matériel sous le contrat de staging autorisé.
`_staged_design` vérifie cohérence du hash complet/tag ; la validité stricte du descripteur
initial est fournie par la construction/autorisation déjà reçue. La validation globale des
configurations et le chaînage CLI restent B4, pas étendus implicitement par cette réception.
L'absence de concurrence entre écritures est une condition du verrou partagé ; aucune
garantie de coordination entre invocations indépendantes hors verrou n'est revendiquée.

## Réserves et tranche suivante

Les dérivés sont des fixtures opaques de métadonnées, sans exécution scientifique ni nouvelle référence DEV/CAL.
Production atomique NPZ puis JSON, récupération des orphelins, états NULL_PLAN/HOLD/ALT/FINAL,
reprise des vrais producteurs, ressources/status, réalisation/publication/T16/CLI restent dus.
T50/T57/T58 restent partiels ; **matrice68 conservée,18PASS/0FAIL/50NOT_RUN**.
Tous les reliquats A, consommateurs de graines, validations scientifiques B2/B3 et T68/os.open restent bloquants B.

Tranche suivante permise : **tests RED B1d d'écriture/reprise des partitions NPZ/JSON** sur tmp_path,
avec producteurs de fixture déterministes seulement. API minimale à proposer pour revue, puis RED
avant production ; aucun Store générique ni modification de producteur scellé.
LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun commit/push/réindexation ou RemoteControl.
