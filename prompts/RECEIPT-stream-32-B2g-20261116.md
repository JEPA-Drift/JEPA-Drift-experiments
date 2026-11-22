# Stream 32 — réception B2g, record ajusté sur lignes fournies

Date : 16 novembre 2026. Décision Codex : **B2g REÇU, COMPOSANT LIMITÉ DE FIXTURE**.
Autorité : GO B-TDD, plan v2.1 et réception B2f, empreintes vérifiées.
Reçu : fit_record(X_fit,K), adaptateur des lignes FIT_NULL fournies vers V/lam/mean.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture | ACCEPTED | Exit0, erreur vide, success/is_error=false, même session PhaseB et huit SHA conformes ; patch intégralement lu. |
| Préservation | ACCEPTED | Une fonction ajoutée,79305octets et anciens nœuds AST préservés ;396tests figés et producteur PCA/2 inchangé. |
| Validation avant fit | ACCEPTED | X réel fini après conversion, T/N/K et colonnes non constantes, moyenne finie avant fit ;11refus sans atteindre le producteur. |
| Appel LW unique | ACCEPTED | Vrai producteur scellé enveloppé par espion, mêmes octets/dtype/forme, un appel par adaptateur ; covariance LW complète, sans corrélation/MP/rotation ni nouvelle tentative. |
| Centrage et référence | ACCEPTED | Fixture8x4Hadamard, shrinkage fermé et covariance qualifiés, deux décalages dyadiques et rejeu ; seules les moyennes changent. Trois vrais fits minuscules exécutés dans ce test technique. |
| Résultat ajusté | ACCEPTED | V/lam/mean stricts, formes et spectre fini positif ordonné via _frozen_record ;4refus après un unique fit, champs corrélation piégés ignorés. |
| Convention T22 | MODIFIED | Écart adjacent divisé par la plus grande valeur propre, clarification consignée avant GREEN ; seuil1e−10 strict et K+2 premiers axes inchangés. Aucun seuil d'orthogonalité ou conditionnement ajouté. |
| Frontière/préfixe | ACCEPTED | Voisins nextafter, dernière paire inspectée, paire hors préfixe puis incluse pour K augmenté, trois échelles ; aucun élargissement de la garde. |
| Contre-revue | ACCEPTED | Validations avant fit, appel unique et garde relus ;396passés/pyflakes/diff propres observés par Codex. Aucune exécution du relecteur. |
| Portée | MODIFIED | T22 reste partiel jusqu'aux appelants/SETUP/configuration. Orthonormalité/provenance des eigpairs garanties par le producteur de confiance, sans nouveau seuil local. |
| Réception complète | REJECTED | SETUP/lignée/graines/générateurs/κ HEAD/DEV/politiques/reprise et autres raccordements encore dus. B2 complet non reçu ; B3/B4 non activés. |

Sous .venv/environnement déterministe/verrou : RED **21failed375passed13.15s**, puis
GREEN **396passed8.54s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Application native par cible absolue364e ; aucune assertion ni tolérance modifiée en GREEN.

| Pièce | SHA-256 |
|---|---|
| Source finale,80281octets | `6845382a67790139c2ff36b4e053991e6d780159fec0bd5d0eebdf552b14bbc6` |
| Tests figés,252260octets | `bb184466b91413d7183a65eb07ecc8fc67ed6864f4fb89d4e4b7e05881551fd5` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `8bf3dd5239d0c2a56e6f323f3796334f117a7204741a4ca8b94392eaa28579c7` |
| Journal pytest GREEN | `919532bed0686b2e2294670b49e2b1d3ec2c4ddfc4becec858152ff217c67660` |
| Journal contrôles GREEN | `840046fa8741f212607829b61a099566c66b1add7a6202ad46a1a356abfda029` |

Revue : REVIEW-stream-32-B2g-red-20261116.md. Matrice68 :18PASS/0FAIL/50NOT_RUN,
aucun contrat partiel promu. Callbacks B2g RED/GREEN traités, sans réapplication ni minuteur.
Suite B2 : assemblage sur frame/lignes fournis, fit figé commun aux applications, identités
réalisées de SETUP, baselines et statut HEAD utilisant κ du descripteur. Tirages/graines,
cache/reprise/ordre et DEV restent à raccorder ; T64/T65 non reçus en entier.

T10/T15/T16global/T19/T21/T22 et autres raccordements/CLI/T68 restent bloquants pour B ;
CPU hors checkpoints/crash, borne externe, workers/jobs, gardes driver et mémoire agrégée
également dus, sans report implicite en C. Aucun fit de campagne, cohorte ou tirage exécuté.
Consigne chercheur : terminer B2 complet puis STOP et prompt de reprise pour une autre Codex
sur modèle00du12novembre ; aucun B3/B4 par cette instance. LotC/runtime/smoke de campagne/
profilage/pilote/full, données réelles/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation/RemoteControl ou changement de producteur scellé.
