# Stream 32 — réception B2i, validation commune des portées

Date : 16 novembre 2026. Décision Codex : **B2i REÇU ; RÉSERVE DE PORTÉE B2h LEVÉE**.
Autorité : GO B-TDD, plan v2.1 et réception B2h, empreintes vérifiées.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture/application | ACCEPTED | Exit0/erreur vide/success/is_error=false, même session, huit SHA conformes ; patch intégralement lu/appliqué nativement par cible absolue364e. |
| Cause commune | ACCEPTED | Quatre lignes dans _check_cfg, héritées par seed_plan/design_descriptor/population_frame ; aucune garde locale setup_bundle ni duplication par appelant. |
| Préservation | ACCEPTED | Tous les autres nœuds AST et octets de fonctions conservés ;428tests et producteur PCA/2 inchangés. Validations anciennes et collisions d'entropie intactes. |
| Canonicalisation | ACCEPTED | Après _word, coordonnées normalisées en valeurs entières pour la comparaison uniquement ; quatre listes logiques non vides/uniques. cfg n'est jamais normalisée, fusionnée ou réduite. |
| Refus et effets | ACCEPTED |8cas invalides refusés directement et par consommateurs, sans RNG/QR/fit/workers/lectures ; objets dupliqués distincts en mémoire, même sens canonique. |
| Contrôles positifs | ACCEPTED | Singleton et entrées distinctes, graines/rejeu/descripteur et pool DEV préservés ; lectures légitimes uniquement CODE_FILES, cfg intacte. |
| Hors domaine JSON | MODIFIED | Une politique objet non sérialisable peut propager TypeError ; elle reste hors du domaine JSON déclaré et n'impose aucune nouvelle règle de type dans cette correction ciblée. |
| Contre-revue | ACCEPTED | Validation après _word et absence de mutation relues ;428passés/pyflakes/diff propres observés par Codex. Aucune exécution du relecteur. |
| Portée de la levée | MODIFIED | Réserve statique B2h sur portées vides/dupliquées levée. Les autres validations de domaine/appelants et T22 restent partiels. |
| Réception complète | REJECTED | Cache/reprise/graines/générateurs/T7/DEV/politiques et ordre global restent dus. B2 complet et B non reçus ; B3/B4/runtime fermés. |

Sous .venv/environnement déterministe/verrou : RED **8failed420passed10.68s**, puis
GREEN **428passed8.68s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Aucune assertion ou tolérance modifiée en GREEN ; aucun tirage/fit/cohorte B2i nouveau.

| Pièce | SHA-256 |
|---|---|
| Source finale,83631octets | `52194c85236bad789c70922520ea8c42fefb6604a3f9af0932342c93d0bb6991` |
| Tests figés,268303octets | `b312b19b37d8cf68c11afbdb3cd80592a984e56c264164ccdc97fbf5714b088a` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `59ebe0e1990fde020bba16cbf16f62ca93056dd83d6f7ccffbf003e04938b157` |
| Journal pytest GREEN | `631176d444a3207b19fa32056363c32380f459479ab5e4e4b905266ee48387da` |
| Journal contrôles GREEN | `5976c295bbcb9ad702398abef37e01e6f25fb5827fe73b518169fbc436881505` |

Revue : REVIEW-stream-32-B2i-red-20261116.md. Matrice68 :18PASS/0FAIL/50NOT_RUN,
aucun contrat partiel promu. Callbacks B2i RED/GREEN traités, ne pas réappliquer.
Suite B2 : consommation déterministe des clés primitives et producteurs sur fixtures,
puis cache/reprise, T7, DEV/politiques et raccordements applicables, sans campagne.
Autres obligations scientifiques/CLI/T68 et CPU hors checkpoints/crash, borne externe,
workers/jobs, driver et mémoire agrégée maintenues avant B, sans report implicite en C.

Consigne chercheur : terminer B2 complet puis STOP et prompt de reprise pour une autre Codex
sur modèle00du12novembre ; aucun B3/B4 par cette instance. LotC/runtime/smoke de campagne/
profilage/pilote/full, données réelles/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation/RemoteControl ou changement de producteur scellé.
