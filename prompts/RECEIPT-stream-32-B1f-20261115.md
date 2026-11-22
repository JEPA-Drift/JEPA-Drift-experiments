# Stream 32 — réception technique B1f, identité pure de réalisation

Date : 15 novembre 2026. Décision Codex : **B1f REÇU, PROJECTION PURE UNIQUEMENT**.
Autorité : GO B-TDD distinct, après réception B1e et RED B1f observé.
Cette réception ne clôt ni B1 ni B ; publication, exportateur T16 et CLI restent dus.

## Preuves et dispositions

Capture `logs/stream-32/phase-b-B1f-green.raw.json` complète : exit0, erreur vide,
is_error=false, subtype=success, session PhaseB habituelle et six préconditions SHA conformes.
Patch source seule de78lignes intégralement lu puis appliqué avec apply_patch.
Réemplois de canon, _is_sha, _phase_digest et _partition_key ; aucun changement de tests.

| Observation | Décision | Justification / vérification |
|---|---|---|
| Handoff des six records | ACCEPTED | Schémas exacts, design, phases, lignée et digests revérifiés en mémoire ; clés uniques, SHA et nombres de lignes contrôlés. |
| Descripteur sans cycle | ACCEPTED | Référence indépendante sur records vérifiés et SHA de vrais CSV FAIR temporaires ; empreinte du descripteur canonique, sans identité future. |
| Plan sauté | ACCEPTED | NULL_PLAN normalisé en NOT_APPLICABLE dans les digests, plan_id/n_hold nuls. |
| Pureté et sortie détachée | ACCEPTED | Copie JSON stricte, aucune lecture/écriture/PRNG/worker sous pièges, entrées conservées. |
| Ordre des listes et noms publiables | MODIFIED | Inversion des dictionnaires couverte ; témoin direct d'inversion des listes et refus des noms non publiables, notamment NUL, exigés avec la publication. |
| Réception globale T53/T56/T59 ou T16 | REJECTED | Identité pure seulement ; manifeste, recalcul depuis fichiers publiés, exportateur scientifique et CLI encore absents. |

RED :4failed,100passed en2.53s. GREEN sous .venv/environnement déterministe/verrou :
**104passed en2.45s**, pyflakes et diff-check propres ; pytest et contrôles exit0.
Contre-revue indépendante du GREEN acceptée dans le contrat de records déjà vérifiés.
Les bornes descriptor-aware de n_hold restent contrôlées par phase_record ; aucune qualification
scientifique des métadonnées opaques DEV/CAL/NULL_PLAN n'est déduite de cette projection.

| Pièce | SHA-256 |
|---|---|
| Source finale | `32e86df7579d18850b4746dadb10e23d2a1b687c79b9951194e6bbf0e74e6191` |
| Tests inchangés depuis RED | `1c950e6da4cd3103062d77b634f89bc03d852cf197d65130d7cbaade5171b2f9` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `99690a5adc420a6fdf789493bc02f72855a167ecc3f7ee11ca1d4fd7b513f14c` |
| Journal pytest GREEN | `8647a1a5cbba3a0f3a75e22daf68c6d8502b4691d1433fc87c85333984f9129d` |
| Journal contrôles GREEN | `7e603fed0e782c544ff583eb75e7ea7d794979d1d3fb73e6e52009beedcf6b3d` |

Script : `logs/stream-32/check-B1f-green.sh`. Décisions RED :
`REVIEW-stream-32-B1f-red-20261115.md`. Matrice68 :18PASS/0FAIL/50NOT_RUN ;
les contrats partiels T53/T56/T59 ne sont pas déclarés PASS.

## Réserves et suite bornée

Tranche suivante permise : tests RED de publication atomique sur fixtures et de recalcul
de réalisation depuis les octets publiés, avec les réserves listes/noms ci-dessus.
Manifeste/FINAL/status, reprise, vrai exportateur T16, CLI/ressources, cohortes/rejeu,
consommation des graines, raccordements A et T68/os.open restent bloquants pour réception B.
Les fichiers CSV de fixture directe ne constituent pas le témoin de T16.

LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun producteur scellé modifié, commit/push/réindexation ou RemoteControl.
