# Stream 32 — réception B2l, directions brutes méta/devlib

Date : 16 novembre 2026. Décision Codex : **B2l REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD/plan v2.1/réception B2k, empreintes vérifiées ; B2 complet non reçu.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture et application | ACCEPTED | GREEN exit0/erreur vide/success/is_error=false, même session et dix SHA conformes ; code complet relu/appliqué nativement sur cible absolue364e. |
| Périmètre et préservation | ACCEPTED | Une fonction31lignes ajoutée, anciens86893octets/AST/imports/constantes/producteurs de bruit/noyaux inchangés ;477tests figés, aucun test reçu affaibli. |
| Lois brutes | ACCEPTED | F0 normal1×20 non normalisé, F1/F2/HEAD signes1×4, F3 signe1×1 ; mêmes lois pour les trois bras, géométrie/I_star hors de cette fonction. |
| DEV et évaluation | ACCEPTED | DEV_LIB/DEV_ALT utilisent le pool DEV reçu à quatre familles, indépendamment de la portée d'évaluation ; CAL/HOLD/ALT suivent celle-ci pour les directions oracles. |
| Identités et plafonds | ACCEPTED | Entropie primitive d'origine, une SeedSequence/RNG/tirage local ; cap du bon domaine et override HOLD primaire, _word avant comparaison/RNG, pas de n_hold réalisé. |
| Refus et stabilité | ACCEPTED | Références indépendantes/spy de méthode-forme-compteur, rejeu/ordre/répertoire/types/labels ; zéro/inf/NaN refusés sans re-tirage ni écrêtage, état global/descripteurs inchangés. |
| Factorisation supplémentaire | MODIFIED | Pas d'extraction : les quelques lignes communes ne justifient pas d'élargir le parseur de bruit aux métadonnées. Helpers de mots/catalogues reçus réutilisés. |
| Contre-revue | ACCEPTED | review_plan32 ne relève aucun défaut matériel sur descripteurs reçus valides ; conditions477tests/lint/diff observées par Codex, aucune exécution du relecteur. |
| Premier quota | REJECTED | Capture initiale429 sans patch conservée rejetée ; reprise après reset valide, minuteur/service collectés, aucun retry restant. |
| Réception globale | REJECTED | FIT_NULL/raccordements/projections/injection/SETUP cache/reprise/proxyT7/DEV/politiques/prior encore dus ; T22/T41 et B2 partiels. |

Sous .venv/environnement déterministe/verrou : RED **15failed462passed13.62s**, puis
GREEN **477passed9.08s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Aucune campagne/mesure de puissance, aucun accès réel, fit ou injection dans ce composant.

| Pièce | SHA-256 |
|---|---|
| Source finale,89285octets | `e084b5a5ddd2609bd771acbcfe94ff1861e2c209fd9c6d6a0f68915607c41677` |
| Tests figés,323817octets/477cas | `de88dcab406db1e4360c8826ccf1fcf709727bbcf2ec5e6c42aac2a0f2625825` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `30a5d456cab202ea75a80baf442eaeb521cef27fc2350d072658e32d84b7a457` |
| Journal pytest GREEN | `02e5f76e362d0a369230e7290a92c0f59c56e4a4e9a1f4b019f63c385e2b2c75` |
| Journal contrôles GREEN | `5bf62963e48e734aa72a1e86e2ffa65077e5da908f34a82c5da5f0514ebd6cb7` |

Matrice68 :18PASS/0FAIL/50NOT_RUN, aucun contrat partiel promu ; revue détaillée
REVIEW-stream-32-B2l-red-20261116.md. Callbacks B2l traités, ne réappliquer aucun patch.
Bootstrap effectif/inférence reste B3 ; globalB/ressources/driver/T15/T16/CLI/T68 dus.
Terminer B2 complet puis STOP et prompt de reprise modèle00du12novembre ; aucun B3/B4
par cette instance. C/runtime/smoke de campagne/profilage/pilote/full/réel/2020+/JEPA/
autres streams/commit/push/réindexation/RemoteControl fermés, producteur scellé inchangé.
