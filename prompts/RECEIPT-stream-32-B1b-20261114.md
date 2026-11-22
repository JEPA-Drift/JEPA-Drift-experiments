# Stream 32 — réception technique B1b, staging initial

Date : 14 novembre 2026. Décision Codex : **B1b REÇU, STAGING INITIAL UNIQUEMENT**.
Autorité : GO B-TDD distinct et réception préalable B1a, inchangés.
Plan canonique v2.1 et producteur PCA /2 préservés. Ni B1 entier ni lotB ne sont reçus.

Reçus : `open_staging(log_dir,desc,resume)`, `StagingMismatch`, réemploi de `pdb.OutputExists`
et écriture atomique minimale. Le tag16 détermine le chemin ; le record porte l'id complet
et le descripteur canonique. Aucun digest réalisé ni achèvement scientifique n'est nécessaire.

## Preuves

| Étape | Résultat observé sous .venv/environnement déterministe/verrou |
|---|---|
| RED | 9failed,54passed en1.98s ; assertions explicites de fonction absente. |
| GREEN | **63passed en1.51s** ; pyflakes et diff-check propres, pytest/checks exit0. |
| Préservation | Les54 tests antérieurs conservés octet pour octet au RED ; tests inchangés pendant GREEN. |
| Contre-revues | Tests acceptés avant application ; revue indépendante GREEN favorable après contrôle d'atomicité et reprise. |

| Pièce | SHA-256 |
|---|---|
| Source finale | `5f006002cf363771a913134fa75335e222a16a53b2625c8865ba7ebe59d7e0b4` |
| Tests | `96f6882a9783e2082c17e0279be001d06df511e51786afecba63066cf8284779` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète, exit0/erreur vide/is_error=false | `64f6c5f315823bdac9670fdff66fd501794f0e549e9725ba038ecfa40ecbb69e` |
| Journal pytest GREEN | `5815f154e40c02b5151024a3eb503de9222b17ff2fb8249f67dd84629b119b69` |
| Journal contrôles GREEN | `a3fbe9fc084cd22b6c52525c6e5ed24c303c934799a044fbaf63f5ead3e37c8b` |

Script `logs/stream-32/check-B1b-green.sh`, preuves `logs/stream-32/lot-B1b-green.*`.
Décisions détaillées : `REVIEW-stream-32-B1b-red-20261114.md`.

## Portée et réserves

Création par mkdir exclusif ; temporaire dans le même répertoire, flush/fsync puis os.replace.
Sans reprise, un staging existant est refusé. Avec reprise, vérification de l'id complet,
descripteur canonique et empreinte cohérente ; aucun octet réécrit. Corruptions, record absent,
collision de préfixe et répertoires indépendants couverts en fixtures.

Limite déclarée : une écriture initiale interrompue après mkdir peut laisser un staging sans
design.json ; la reprise le refuse, sans réinitialisation d'un état non vérifiable.
DESIGN_FIXED est implicite par le record initial ; status/phases/partitions ne sont pas encore reçus.

T56/T58/T61 restent partiels : **matrice68 conservée,18PASS/0FAIL/50NOT_RUN**.
Raccordement autorisation→staging, phases/partitions, reprise scientifique, réalisation,
publication, ressources, CLI et T16 sur vrais exports restent dus, ainsi que les reliquats A,
validation globale B2–B4 et T68/recorder os.open. Aucune réception globale déduite de ces63 tests.

Tranche suivante permise sous GO B : **tests RED B1c des records SETUP/DEV/CAL** sur fichiers
de fixture tmp_path, sans exécution de ces étapes scientifiques. Production après RED/revue seulement.
NULL_PLAN/HOLD/ALT, réalisation et publication restent des tranches ultérieures.
LotC/runtime/smoke/profilage/pilote/full restent fermés ; aucun accès réel/2020+, JEPA,
producteur scellé modifié, autre stream, commit/push/réindexation ou RemoteControl.
