# Stream 32 — réception B2k, scores nuls gaussiens EXACT direct21

Date : 16 novembre 2026. Décision Codex : **B2k REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD/plan v2.1 et réception B2j, empreintes vérifiées ; B2 complet non reçu.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture | ACCEPTED | Exit0/erreur vide/success/is_error=false, même session et dix SHA conformes ; code complet relu/appliqué nativement sur cible absolue364e. |
| Générateur EXACT | ACCEPTED | exact_scores(desc,key), PC1..21, exactement une RNG locale/SeedSequence et un tirage H×21 normal standard, brut et fini ; coût21H conservé pour N32 et N239. |
| Clés et isolation | ACCEPTED | CRC32/entropie manuels, N réel dans la clé, rejeu/ordre/répertoire/labels scientifiques sans effet parasite ; état global/descripteur inchangés. |
| Refus et plafonds | ACCEPTED | Tuple/words/coordonnée/campagne/bras/roles/finalcap avant RNG ; fit/FITTED refusés ; K strict20/H entier positif/N≥21 ; override primaire conforme au plan de graines. |
| Primaire EXACT technique | MODIFIED | Fixture φ=EXACT teste la branche d'override, sans modifier Φ confirmatoire FITTED du plan ni créer d'autorisation. |
| Factorisation | MODIFIED | Validation pure extraite dans _planned_null_key et réutilisée par deux consommateurs ; null_returns conserve validation du frame avant RNG et le calcul FITTED, seul le message générique de refus change. |
| Préservation | ACCEPTED | AST de tout le module hors trois fonctions concernées et suffixe RNG/calcul FITTED identiques ; aucune constante/import/autre noyau ni producteur scellé modifié.462tests figés. |
| Contre-revue | ACCEPTED | review_plan32 sans défaut matériel, acceptation sous réserve tests/lint/diff ; conditions réellement observées par Codex, aucune exécution du relecteur. |
| Couverture complète | REJECTED | Producteurs nuls reçus, pas encore de méta/DEV/cache/reprise/raccordements/proxyT7 ; T22/T41 et B2 restent partiels. |

Sous .venv/environnement déterministe/verrou : RED **13failed449passed12.77s**, puis
GREEN **462passed19.55s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Les variations de durée sont des journaux de tests, aucune mesure de débit de campagne.

| Pièce | SHA-256 |
|---|---|
| Source finale,86893octets | `f8b35cd74c52c3ffc779409495118a511a6aded2630bcc96303fa986a5b6f7cd` |
| Tests figés,306522octets/462cas | `b07a65ae4895d442fba6cd3c4c187080e40106740dd8b6453c23cf1733aaf952` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `94772acb84da4273907f87e827b3ee64e71488662d44dfde9bdbe5e44ad3d567` |
| Journal pytest GREEN | `e2a21a531d17e3eae2bd25001e474986e08d2accb15365ffa016c8900e9ca2f5` |
| Journal contrôles GREEN | `237900a243e3636a6970fb1aa0afd5b5ffaaad7ec079132b53752b609cdfa3a9` |
| AST hors fonctions concernées | `6a2138e59a588ef5ad3c145c2d2a68f4f9c65cf520fca639f339609839750902` |
| AST suffixe RNG/calcul FITTED | `9c76b255b42afde2876629d3fc3260d00a4a45a3286729e0faa3e4880359e425` |

Revue détaillée REVIEW-stream-32-B2k-red-20261116.md ; matrice68 :18PASS/0FAIL/50NOT_RUN,
aucun contrat partiel promu. Tous callbacks B2k traités ; ne pas réappliquer leurs patches.
Suite B2 : clés méta/devlib et directions, raccordement FIT_NULL/fit, projection vivante/
injection, SETUP cache/reprise/fit partagé/ordre, routage des proxys T7, DEV équilibré et
politiques/prior figés. Rééchantillonnage bootstrap effectif/inférence restent B3, plan
de graines connu ; aucune clôture T41 anticipée. Ressources/driver, T15/T16global, autres
exports/CLI/cohortes/T68 et raccordements restent bloquants avant B, sans report impliciteC.

Terminer B2 complet puis STOP et prompt de reprise pour une autre Codex modèle00du12novembre ;
aucun B3/B4 par cette instance. C/runtime/smoke de campagne/profilage/pilote/full,
réel/2020+/JEPA/autres streams/commit/push/réindexation/RemoteControl fermés.
