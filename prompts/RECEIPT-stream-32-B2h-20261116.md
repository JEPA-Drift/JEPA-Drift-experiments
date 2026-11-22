# Stream 32 — réception B2h, bundle SETUP sur entrées fournies

Date : 16 novembre 2026. Décision Codex : **B2h REÇU COMME COMPOSANT LIMITÉ**.
Réserve bloquante avant B2 complet : validation partagée des portées vides ou dupliquées.
Autorité : GO B-TDD, plan v2.1 et réception B2g, empreintes vérifiées.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture/application | ACCEPTED | Exit0/erreur vide/success/is_error=false, même session, huit SHA conformes ; patch lu/appliqué nativement par cible absolue364e. |
| Préservation | ACCEPTED | Une fonction ajoutée,80281anciens octets/AST intacts ;418tests figés et producteur PCA/2 inchangé. |
| Validation avant fit | ACCEPTED | Coordonnées canoniques planifiées, schéma/frame/lignes/univers et paramètres vérifiés ;13refus passent, dont les trois cas K20.0/T_fit48.0/I_star0.0 ajoutés après revue. |
| Fit partagé/baselines | ACCEPTED | EXACT sans fit, FITTED un fit_record par bundle partagé RES/MARKET ; baselines sur le spectre ajusté, statuts sans repli/troncation. |
| Contrôle géométrique HEAD | ACCEPTED | κ_geo du descripteur, borne incluse/voisin supérieur, vrai zéro/None inconclusif et absence de refit ; MARKET non applicable. Détectabilité/inférence non activées. |
| Identités | ACCEPTED | basis_sha et fit_hash sur V/lam/mean, moyenne apprise incluse ; setup_id après fit selon table canonique, sans famille/chemin/realization ni retour vers les graines. |
| κ_det et isolement | MODIFIED | κ_det entre dans la canonicalisation de design_id, sans rôle dans la décision HEAD. Répertoires ALT/smoke empoisonnés, traps et readonly/rejeu passent. |
| Exceptions de structure | ACCEPTED | KeyError/TypeError des lectures de structure convertis en ValueError avec cause ; aucun autre noyau ou validateur réécrit dans ce composant. |
| Portées vides/dupliquées | MODIFIED | Réserve statique de contre-revue : corriger _check_cfg partagé avec design_descriptor/seed_plan/population_frame, puis témoins sous fils-pièges. La fusion silencieuse de clés par un dictionnaire ne vaut pas validation de configuration. Bloquant avant réception B2 complet, aucun report en C. |
| Contre-revue | ACCEPTED | Aucun autre défaut matériel sur les entrées du contrat ;418passés/pyflakes/diff propres observés par Codex, aucune exécution du relecteur. |
| Réception complète | REJECTED | Driver/cache/reprise/graines/générateurs/T7/DEV/politiques et ordre global restent dus. T22/T64/T65 partiels ; B2 et B non reçus en entier, B3/B4 fermés. |

Sous .venv/environnement déterministe/verrou : REDv2 **22failed396passed13.60s**, puis
GREEN **418passed8.72s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Nouveaux tests B2h : entrées/fit_record fournis par fixtures et espions, aucun fit réel nouveau,
tirage ou cohorte ; les trois fits8x4 du test B2g restent de simples fixtures techniques.

| Pièce | SHA-256 |
|---|---|
| Source finale,83226octets | `f3148c8f6b91e79104a8e008b9cbf40b158225560fcdc59710024ef1517e80b3` |
| Tests figés,264963octets | `6b219538f1711a9d083fd653251fd71ff0cd5c4133b23a85c89d44b0e2d9eb5d` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `ad3d9f83d4ab0569dc689a2a315bd8348d108565f2f1cb2cbae9ff35dbb686d7` |
| Journal pytest GREEN | `ebeb12c53b718d5cf846cab23afa7c4c371a293f6b1508a5ffc0cd2e15ab4d2e` |
| Journal contrôles GREEN | `6e64b9b6f247993d3ae31a56d8eb1f796e17c89d5e1eea351ab6a09864887e1e` |

Revue détaillée : REVIEW-stream-32-B2h-red-20261116.md. Matrice68 :18PASS/0FAIL/50NOT_RUN,
aucun contrat partiel promu. Callbacks B2h RED/V2/GREEN traités, sans réapplication/minuteur.
Suite immédiate B2i : tests seuls des portées dans le validateur partagé, correction de la
cause commune avant les producteurs scientifiques ; aucune garde locale répétée ni nouveau cadre.
Autres obligations scientifiques/CLI/T68 et CPU hors checkpoints/crash, borne externe,
workers/jobs, driver et mémoire agrégée maintenues avant B, sans report implicite en C.

Consigne chercheur : terminer B2 complet puis STOP et prompt de reprise pour une autre Codex
sur modèle00du12novembre ; aucun B3/B4 par cette instance. LotC/runtime/smoke de campagne/
profilage/pilote/full, données réelles/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation/RemoteControl ou changement de producteur scellé.
