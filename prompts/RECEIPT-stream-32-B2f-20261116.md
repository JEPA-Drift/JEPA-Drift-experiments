# Stream 32 — réception B2f, géométrie HEAD sur bases figées

Date : 16 novembre 2026. Décision Codex : **B2f REÇU, COMPOSANT PUR LIMITÉ**.
Autorité : GO B-TDD, plan v2.1 et réception B2e, empreintes vérifiées.
Reçu : head_geometry(frame,fit,istar,universe), sans fit, tirage ou campagne.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Capture GREEN | ACCEPTED | Exit0, erreur vide, success/is_error=false, même session PhaseB, huit SHA conformes ; patch intégralement lu. |
| Préservation | ACCEPTED | Un import stdlib itertools et une fonction ajoutée ; tous les anciens nœuds AST et octets de fonctions préservés.375tests figés et producteur scellé inchangés. |
| Validation | ACCEPTED | Records V/lam/mean reçus, même N, univers résiduel4..20 à int Python stricts, istar fini positif ;18refus de fixture passent. |
| Dérive et projections | ACCEPTED |16signes lexicographiques, support population PC2..5 et amplitude inchangés ; I_E et I_P4 sont joints via les aides reçues, P4 étant les quatre premiers axes ajustés éligibles. |
| Bras interne FITTED | ACCEPTED | Même calcul joint valable pour frame=fit ; le label interne n'est pas exporté. Aucun oracle diagonal annoncé comme joint, aucune fuite vers un sélecteur. Validation répétée sans refonte nécessaire. |
| Fractions et zéros | ACCEPTED | f_E conditionnel distinct de f_pop ; perte totale dans E rend f_E indéfini/None, P4 nul avec I_E positif donne0. Vrais zéros admis, garde B2e du faux zéro inchangée. |
| Agrégation des profils | MODIFIED | V1 non appliquée car fractions constantes ; V2 ajoute un seul témoin variable,24cas/API intacts.99/148 et123/148, huit profils chacun, min/mean/max distincts, moyenne3/4 ; référence indépendante avant le noyau. |
| Références et pureté | ACCEPTED | EXACT, rétention0.75, fuite hors E, nullité et rotation12/13 confrontées aux références ; readonly, rejeu, traps fit/RNG/sélecteurs/calibration/E/S passent. |
| Contre-revue | ACCEPTED | Formules, zéros, ratios et résumés relus ; conditions375passés/pyflakes/diff propres observées par Codex, aucune exécution du relecteur. |
| Portée de T64/T65 | MODIFIED | Noyau reçu seulement ; κ lu dans le descripteur, statut/persistance SETUP, un seul fit, ordre avant ALT et isolement restent dus. Aucun seuil ajouté dans la primitive. |
| Réception B2 complète | REJECTED | Générateurs/fits/graines/DEV/politiques figées/SETUP et raccordements encore dus. head_control/détectabilité/inférence sont B3, non activés ; B2f ne clôture pas B2. |

Sous .venv/environnement déterministe/verrou : REDv2 **25failed350passed13.56s**, puis
GREEN **375passed8.43s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Commande : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Application native par cible absolue364e. Aucune assertion ni tolérance modifiée en GREEN.

| Pièce | SHA-256 |
|---|---|
| Source finale,79305octets | `9273b20366639b75bd9af8f80e48728245de53d66875771e8faef22121f42c7b` |
| Tests figés,243973octets | `77aaa7301c13ab79d6bcd18cf822ebd1b39099f53f71f8502939325a357a2b1e` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `dfe111ffb59299ec2161ecf4f2abd6c29e320fb3a23f54b51b2ca390bc85bd0c` |
| Journal pytest GREEN | `1d7a55bbfb3fc3cfbe8e629a3a869108528c106d0419fe7269f2c4c53a10e20e` |
| Journal contrôles GREEN | `e9582db66e7a800999d55942a0ed83bdf1debf1cb123cba07bfa237aca07e845` |

Revue détaillée : REVIEW-stream-32-B2f-red-20261116.md. Matrice68 :18PASS/0FAIL/50NOT_RUN,
aucun contrat partiel promu. Callbacks B2f RED/V2/GREEN traités ; aucune réapplication ni minuteur.
Orthonormalité/provenance SETUP et écart propre appris restent des préconditions à raccorder.
T10/T15/T16global/T19/T21/T22 et autres raccordements scientifiques/CLI/T68 restent bloquants
pour B ; CPU hors checkpoints/crash, borne externe, workers/jobs, gardes driver et mémoire
agrégée également dus, sans report implicite en C.

Consigne chercheur : terminer B2 complet puis STOP et prompt de reprise pour une autre Codex
sur modèle00du12novembre ; aucun B3/B4 par cette instance. LotC/runtime/smoke de campagne/
profilage/pilote/full, données réelles/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
