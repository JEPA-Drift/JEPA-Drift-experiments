# Stream 32 — réception B2v, choix DEV purs

18 novembre 2026. Décision Codex distincte : **B2v REÇU COMME COMPOSANT LIMITÉ**.
Autorité B-TDD et plan v2.1 inchangés ; nouvelle session autorisée par le chercheur.
Cette réception porte sur dev_choices ; **B2 global non reçu**.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| TDD | ACCEPTED |RED36failed770passed36.06s, absences dev_choices seulement, après contre-revue du patch de tests. GREEN source seul ensuite contre-revu et appliqué une fois ;806passed17.33s. Aucun test ni tolérance modifié. |
| Règle d_dev | ACCEPTED |Grille déclarée complète, préfixes canoniques, prior commun, calibration GE distincte et moyenne RMST_H équilibrée quatre familles. Plus petitd en égalité, invariance à l'ordre de déclaration. |
| Règle s2_dev | ACCEPTED |Branche primaire seule, grille prévue1/4/16/64×prior, calibration distincte pour chacune des trois politiques ; moyenne équilibrée politique/famille et plus petit s2 en égalité. Un seul choix commun, sans variante par famille. |
| Qualification | MODIFIED |COMMON_NOMINAL_ALPHA_DEV :alpha nominal partagé ; aucune comparaison annoncée àFPR atteints équivalents. Helper pur sur observations fournies uniquement. |
| Admission / preuve réelle | ACCEPTED |33refus avant scans/calibration, censure et égalités sur vrais noyaux, chemin non primaire sans grille s2 utile, propagation réelle d'InsufficientCalibration. Bornes et provenance des données restent la responsabilité du futur contrôleur. |
| Préservation / bilan | ACCEPTED |Préfixe source121394octets/157nœuds AST exact, tests595340octets/806cas et producteur scellé inchangés. Pytest0/contrôles0/pyflakes/diff propres sous .venv/environnement/verrou ; review_plan32 recommande la réception limitée après lecture des preuves. |
| Réception B2 global | REJECTED |Production DEV_NULL/ALT, provenance, gel, dev_id/policy_id, phaseDEV et intégration restent dus. T33/T34 demeurent partiels. B3/B4/runtime/campagnes et autres streams fermés. |

Source124874octets/160nœuds AST `ed3944fd39ef396d4bf33396f0c0e3872ba7e44fd553f23aaf884b347b922944`.
Tests595340octets/806cas `f93cdf90c27b5056e717aa2917c3372542b4d9d40ffef807b6659586c5ebb865`.
Scellé `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.
Pytest `3c6c31a6fc8dceec0b566d593a9916a69f272d21ea7bb85399d89b828993cdcb` ;
contrôles `2920b10382c22d5e84f12356e1d7feac296b065bbbdfc5ec3eff7919dd850240`.
Revues RED-fresh et GREEN du18novembre conservées ; matrice68,18PASS/0FAIL/50NOT_RUN.
Toutes notifications B2v précédentes traitées ; aucun patch ou contrôle à rejouer.

Suite regroupée : contrôleur DEV, provenance, gel/identités et intégration, dans un
contexte Claude borné conformément à la demande du chercheur. Terminer B2 COMPLET
puis STOP et prompt de reprise Codex modèle00du12novembre ; aucun B3/B4 par cette instance.
