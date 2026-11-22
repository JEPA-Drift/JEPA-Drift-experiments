# Stream 32 — réception B2a, repère et spectre population

Date : 15 novembre 2026. Décision Codex : **B2a REÇU, PRIMITIVE LIMITÉE**.
Autorité : GO B-TDD et réception B1n. Aucun GO runtime ou scientifique.
Reçu : population_frame(cfg,mode,N) retournant V et lambda pour N32/N239 du plan,
avec colonne marché imposée avant QR et clé primitive frame32. Aucun fit réalisé.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Repère canonique | ACCEPTED | Première colonne dans l'entrée QR, orthogonalité, signes positifs et sortie finie testés ; aucune substitution après QR. |
| Spectre configurable | ACCEPTED | Référence scalaire1-based des paramètres cfg, défauts N32/N239 et variante decay4 ; valeurs matérialisées finies, positives et décroissantes avant RNG. |
| Graines | ACCEPTED | Entropie exacte [32,seed,crc(campaign),crc(frame),N], mêmes octets répétés ; racine/campagne/N distincts, aucun état global ou flux stream28. |
| Refus | ACCEPTED | N non planifié/booléen, mode/graine et spectres non ordonné/non positif/non fini refusés avant tirage et QR. |
| Corrections de témoins | MODIFIED | V1 jamais appliquée ; copies Q/R et variante de decay ajoutées en v2, critères/tolérances conservés. Préfixe241cas identique, append seulement. |
| Source minimale | ACCEPTED | Une fonction ajoutée, aides de configuration/seed-plan réemployées, aucun effet à l'import ni API existante modifiée. Préfixe66071octets source préservé. |
| Contre-revue indépendante | ACCEPTED | Aucun défaut matériel pour les Python int N32/N239 canoniques ; aucun test/import/mutation par le relecteur. Conditions252passés/pyflakes observées par Codex. |
| Domaine et dégénérescence | MODIFIED | N NumPy-int refusé par cette API, sans appelant antérieur ; R diagonal exactement nul non gardé, sans contre-exemple reproductible dans le domaine reçu. Pas d'extension de domaine ou de nouveaux tirages pour forcer un résultat ; validation complète de configuration/fit T22 reste due. |
| Autorisation et orchestration | REJECTED | Ce noyau ne remplace pas authorize du driver avant tirage ; persistance SETUP/IDs/fit/univers, autres rôles et consommation de toutes les graines restent à raccorder. |
| Réception globale | REJECTED | T22/T41/B1/B non clôturés ; familles/DEV/CAL/HOLD/ALT/HEAD, uint32, calendrier/bundle/T16 global, CLI/cohortes/A/T68 encore dus. Ressources B1m toujours bloquantes. |

Sous .venv/environnement déterministe/verrou : RED **11failed241passed en9.96s**,
puis GREEN **252passed en8.36s**, pytest/contrôles exit0, pyflakes/diff-check propres.
Patch29lignes source seule relu/appliqué nativement et append vérifié exactement ;
tests172475octets/252cas ciblés dont9registre inchangés pendant GREEN.

| Pièce | SHA-256 |
|---|---|
| Source finale | `95f64026eb60b3154f08f3cc59698326704eb60ee95c10d9b1c7550ab62e5a9d` |
| Tests figés | `f238b08b1c5ce87afb25393c52dc3f010ab9c32455609dc62b73938fd32a4154` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète | `1bb9ed1a00ad39b64022b3b1686cc6b31bd33f58fc4fd63024c5aa28857b1cf5` |
| Journal pytest GREEN | `cb0695e0d6f52f1c8424c40ea25b6b761910ea982620ae4528c8d486fcab7181` |
| Journal contrôles GREEN | `84d849c216b54be207487cfa97eab23019e1a2a03ce31227943692e5972a48fd` |

Revue/dispositions : REVIEW-stream-32-B2a-red-20261115.md ; scripts/preuves check-B2a-*.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; aucun contrat partiel promu en contrat complet.
Suite bornée : tests seuls des univers et baselines spectrales B2b (FULL_K, EIGENMEAN,
CPV90 global et résiduel), sans fit ni trajectoire. Pas de clôture B1/T16 ou report enC.
CPU hors checkpoints/crash/borne externe, workers/jointures/jobs, gardes driver avant
engagement/finalisation et mémoire agrégée restent bloquants avant réception B.
LotC/runtime/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
