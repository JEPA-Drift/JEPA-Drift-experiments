# Stream 32 — réception technique B1a

Date : 14 novembre 2026. Décision Codex : **B1a REÇU, COUCHE PURE UNIQUEMENT**.
Autorité : notification16 et GO B distinct `GO-stream-32-B-20261114.md`, SHA-256
`5156ee158cac9f46f2aa225627a044b56e0055be0602da5d859a16786ec8dffa`.
Plan canonique v2.1 inchangé. Cette réception ne reçoit ni B1 entier ni lotB.

Reçus : `design_descriptor`, `design_id`, plan de graines pré-exécution et garde `authorize`,
sans tirage, worker ni écriture. Code/environnement réels, descripteur détaché du cfg,
DEV poolé F0/F1/F2/HEAD, clés primitives et contrôles CRC/entropies, HOLD au cap primaire.
GO relatif résolu sous racine, SHA sur les octets lus, citation et bloc exacts.
La comparaison du descripteur fourni est désormais canonique, cohérente avec `design_id`.

## Preuves et dispositions

| Étape | Résultat effectivement observé |
|---|---|
| Premier RED proposé | Non appliqué : quatre défauts de référence/traps/configuration/environnement, corrigés dans v2. |
| RED v2 | 6failed,46passed en1.72s, assertions de fonctions absentes ; autotest des pièges réussi. |
| GREEN initial | 52passed en1.45s ; réception suspendue après découverte indépendante de l'alias int/float/bool. |
| RED canonique | 2failed,52passed en1.67s, `DID NOT RAISE AuthorizationRefused` ; cfg/GO inchangés. |
| GREEN canonique final | **54passed en1.46s**, pyflakes et diff-check propres. |

Toutes les exécutions : .venv du projet, variables déterministes et verrou partagé.
Les45 tests antérieurs et les témoins supplémentaires ont été préservés, sans réduction de tolérance.
Contre-revues indépendantes : tests v2, garde de confiance/graines, témoin canonique et correctif final.
Le reviewer confirme la résolution du seul défaut bloquant B1a sous les preuves finales ci-dessus.

| Pièce finale | SHA-256 |
|---|---|
| Source | `8232da27f98c98aac7dc326d5fe144d4b5056a92bb947a06b70effb9d57e940b` |
| Tests, inchangés pendant le dernier GREEN | `f31493517f27567a1cbcf782281fe43ed65ab510c91ebb99a4ff5dc1a92c3314` |
| Producteur PCA /2, inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN final, exit0/erreur vide/is_error=false | `35f49b6f070d14e0fa38e053902e7daa7fd749b1ae9e380d1aa3bafafda257f8` |
| Journal pytest final | `c4f1c5109fc89b9cc021bc16cf08e5d70ecc6017baf1a8928a3def9eb35b0d6c` |
| Journal contrôles final, exit0 | `370684e11b1491cfc7300886fccd471ad9e501e650694cd8b0e059bc1195c640` |

Journaux : `logs/stream-32/lot-B1a-edge-green.*`, script `check-B1a-edge-green.sh`.
Revues détaillées avec ACCEPTED/MODIFIED/REJECTED : `REVIEW-stream-32-B1a-red-20261114.md`
et `REVIEW-stream-32-B1a-green-20261114.md`.

## Réserves bloquantes pour réception B

- Validation complète des schémas, valeurs et compatibilités applications/familles : B2–B4.
  La validation B1a est bornée ; un descripteur non sérialisable échoue bruyamment par TypeError.
- Consommation réelle des clés et tailles DEV_LIB, phases, NULL_PLAN/HOLD et identités dérivées : B2/B3.
- Staging/reprise, réalisation, publication, CLI, ressources et indépendance des sorties/jobs : B1/B4.
- T68 complet/AST du chargeur et réserve des lectures os.open non journalisées ; les lectures B1a
  utilisent les aides couvertes `pdb.file_sha256` et `open`, sans lecture des sorties précédentes.
- T10/T15/T16/T19/T21/T22 d'intégration restent dus, dont T16 sur les véritables exports FAIR.

Matrice exhaustive conservée : **18PASS,0FAIL,50NOT_RUN**,68contrats. T54/T55 reçus sur fixtures ;
les contrats partiels restent NOT_RUN avec succès de couche pure documentés. Aucun report implicite àC.

## Tranche suivante conditionnée

La réception B1a permet seulement de demander les **tests RED B1b du staging initial** :
`open_staging(log_dir,desc,resume)`, design complet/tag16, création/reprise/refus sur tmp_path.
La production B1b attendra son RED observé et sa revue. Phases scientifiques, realization_id,
publication et T16 seront traités dans les tranches suivantes ; aucun résultat factice ne les clôture.

LotC/runtime/smoke/profilage/pilote/full restent fermés. Aucun accès réel/2020+, JEPA,
producteur scellé modifié, autre stream, commit/push/réindexation ou RemoteControl.
