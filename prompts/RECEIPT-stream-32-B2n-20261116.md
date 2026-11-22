# Stream 32 — réception B2n, routage T7 des proxys gaussiens

Date : 16 novembre 2026. Décision Codex : **B2n REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD/plan v2.1/réception B2m, empreintes vérifiées ; B2 complet non reçu.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture/application | ACCEPTED | GREEN exit0/erreur vide/success/is_error=false, même session et onze SHA conformes ; patch relu/appliqué nativement sur cible absolue364e. |
| Périmètre | ACCEPTED | Deux constantes et setup_bundle seulement ; quatre régions ciblées, aucune nouvelle fonction/import/configuration, formules et autres noyaux inchangés ;503tests figés. |
| Information T7 | ACCEPTED | Même calcul gaussien pour A,c,C0,var0,beta,q,I_joint ; oracle_basis=ORACLE_DIAGONAL_GAUSSIAN_PROXY. q diagonal distinct du joint à C0 complet ; aucune vraie KL t7 ou correction nu ajoutée. |
| Export | ACCEPTED | Troisième libellé admis via INFO_BASES ; corps/12colonnes/ANALYTIC_PROXY/valeurs/FAIR/SHA inchangés, lecture round_trip et réécriture identique ; anciens libellés/refus inconnus PASS. |
| SETUP fourni | ACCEPTED | T7 planifié admis avec fit unique partagé, baselines/HEAD/identités/hashmean conservés ; seul T7 gagne information_basis=GAUSSIAN_PROXY, qui qualifie la géométrie sans conclusion de détectabilité. |
| Disposition du garde | MODIFIED | Le seul ancien refus T7 est devenu refus de PLAIN inconnu planifié, avant fit ;13cas/assertions/readonly conservés. Disposition écrite avant RED, aucun autre test affaibli ; garde et positif T7 PASS. |
| Vérification/contre-revue | ACCEPTED | 503passed9.36s, pyflakes/diff et conditions de review_plan32 effectivement observées sous .venv/environnement/verrou ; aucune exécution du relecteur. |
| Réception globale | REJECTED | Cache/reprise SETUP, DEV/politiques/prior, provenance des libellés au contrôleur et raccordements restent dus ; B2 complet non reçu. |

RED **3failed500passed11.34s**, GREEN **503passed9.36s** ; pytest/contrôles GREEN exit0.
Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Nouveaux témoins sur entrées fournies et CSV tmp_path ; aucun fit T7 réel, tirage T7,
cohorte ou campagne exécuté par cette extension. Producteurs stochastiques inchangés.

| Pièce | SHA-256 |
|---|---|
| Source finale,92025octets | `c2415f60feabff6bcd564f622bf841e87cd3e113fa472c27815b9190c3fbd85f` |
| Tests figés,356307octets/503cas | `7644ebe81153828322bff9da4b01dda7a7d2df4817583a5ea200cf7051191d16` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `fea36c558c84cea6b6c07c03e550ed67b2eea9bb39581fb6c0e1e29ef8227d2b` |
| Journal pytest GREEN | `b2c3cc251bfc3a4591348403751ece9811e94f1e1271552ed42b0e2568261162` |
| Journal contrôles GREEN | `4b97985411cd7ea32cad4097329b49683baa7b1699728b4d51e4c0215d7ce5ae` |

Matrice68 :18PASS/0FAIL/50NOT_RUN, aucun contrat partiel promu ; revue détaillée
REVIEW-stream-32-B2n-red-20261116.md. Tous callbacks B2n traités, ne réappliquer aucun patch.
Restent dus : FIT_NULL vers fit, SETUPcache/reprise/fit partagé/ordre/autorisation,
population_drift raccordé, DEV équilibré/politiques/prior, globalB/ressources/CLI/T15/T16/T68.
Terminer B2 complet puis STOP et prompt de reprise modèle00du12novembre ; aucun B3/B4
par cette instance. C/runtime/smoke de campagne/profilage/pilote/full/réel/2020+/JEPA/
autres streams/commit/push/réindexation/RemoteControl fermés. Portes de campagne T7 après
qualification gaussienne encore dues au contrôleur ultérieur ; aucun report implicite en C.
