# Stream 32 — réception B2r, raccordement pur des scans

Date : 17 novembre 2026. Décision Codex distincte : **B2r REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD/plan v2.1 inchangés, réception limitée B2q conservée.
Cette réception porte sur nonoracle_scan/oracle_scan et leurs deux aides communes.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| TDD | ACCEPTED | Tests initiaux contre-revus/appliqués une fois, RED21failed585passed19.94s. GREENv1 refusé statiquement avant application ; sept témoins supplémentaires contre-revus/appliqués une fois, RED28failed585passed22.51s, toutes qualifications passantes. V2 complète seulement après RED. |
| Source | ACCEPTED |33lignes/deux fonctions publiques/deux aides privées ajoutées ; anciens104414octets/147nœuds AST/noyaux/imports/alias exacts.613cas figés, aucune suppression ni tolérance affaiblie, producteur scellé inchangé. |
| Frontière réelle | ACCEPTED | Validateur réel partagé pour Y des deux voies et pour q oracle avant primitives. Refus complexes/texte sans dispatch ; entiers signés/non signés valides et readonly conservés. Aucune correction des anciens noyaux nécessaire. |
| Transmission / résultat | ACCEPTED | Prior fourni inchangé pour tous masques et variante fois4 ; vrais masques et scan appelés une fois chacun. W/first sur horizon entier, GE/None/+inf/B0, erreurs numériques, bits uint32 locaux issus des masques utilisés ; références indépendantes passantes. |
| Vérification / contre-revue | ACCEPTED |613passed11.05s, pytest0/contrôles0, pyflakes/diff propres sous .venv/environnement/verrou. review_plan32 accepte avant application puis AC_ACCEPTLIMITED après preuves. |
| Portée | MODIFIED | Calculs purs sur tableaux et politiques fournis, sans cohorte/calibration/identité/stockage publié. V1 jamais exécutée ; son défaut était statique. Aucun contrat global T25 ou branche de campagne reçu. |
| Réception globale B2 | REJECTED | gamma_M_sensitivity, DEV/bibliothèque/liaison aux clés/cache/gel/d_dev/s2_dev/identités/poisoning et raccordements restent dus. B2 complet non reçu, aucune activation B3/B4. |

| Pièce | SHA-256 |
|---|---|
| Source106035octets | `81f36417248d648c61259e870efc072d9ba246ed9c229900bbe890df15246843` |
| Tests466299octets/613cas | `c5fadcfca4d4be9a174a177d2070996536cf1737a444032937217a9ea7f4f34b` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREENv2 | `42d061e4b0b223ebea00ccf49ac042ad6ffab3f415785608fbe3cf4e872cc94f` |
| Journal pytest GREENv2 | `09ec0aad37f3f1b1cae28d4c9bca72a805511139cfde00748850d799c5eed74b` |
| Journal contrôles GREENv2 | `220031c444e1ce072809691f2d1ddcaf98e6c5c3eecd139b37bed37049aa6304` |

Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Revues détaillées B2r-red, B2r-green(v1), B2r-guard-red et B2r-green-v2 du17novembre.
Matrice68 :18PASS/0FAIL/50NOT_RUN, parties intégrées encore dues. Callbacks B2r traités,
aucun patch/contrôle historique à rejouer. Suite B2 par tests seuls, revue/RED avant code.
Terminer B2 COMPLET puis STOP et prompt de reprise Codex sur modèle00du12novembre.
Aucun B3/B4 par cette instance. C/runtime/smoke de campagne/profilage/pilote/full/réel/
2020+/JEPA/autres streams/RemoteControl/commit/push/réindexation restent fermés.
