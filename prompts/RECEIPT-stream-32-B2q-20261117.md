# Stream 32 — réception B2q, prior et fabrique de politiques nominaux

Date : 17 novembre 2026. Décision Codex distincte : **B2q REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD/plan v2.1 inchangés, réception limitée B2p conservée.
Cette réception porte exclusivement sur common_prior et frozen_policy nominaux.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| TDD | ACCEPTED | V1 non appliquée car positifs insuffisants pour distinguer un prior constant. Deux corrections auteur consolidées uniquement, inverse exacte et contre-revue avant application native unique. RED réel27failed558passed21.63s, toutes qualifications passantes, avant code. |
| Source | ACCEPTED | Deux fonctions,76lignes ajoutées ; préfixe99397octets/145nœuds AST, imports, alias, noyaux et producteur scellé inchangés.585tests figés, aucun affaiblissement pendant GREEN. |
| Prior | ACCEPTED | Deux configurations opérationnelles distinctes vérifient le calcul2ln(H/alpha)/(HK) ; mêmes valeurs pour tous d/politiques au sein d'une configuration, indépendantes de gamma_M/I_star/dgrid. Domaines, débordement et résultat fini positif contrôlés. |
| Fabrique nominale | ACCEPTED | Coûts primaires MIX/AFF reçus, enveloppes exactes et readonly ; masques statiques figés et indices locaux corrects, statuts sans repli, entrées de branche utiles seulement. Références spectrales/DEV/ex ante indépendantes et H oracle dynamique. |
| Vérification / contre-revue | ACCEPTED |585passed10.78s, pytest0/contrôles0, pyflakes/diff propres sous .venv/environnement/verrou. review_plan32 accepte la source et la réception limitée après lecture des preuves. |
| Domaine reçu | MODIFIED | Descripteurs JSON canoniques seulement ; aucun engagement supplémentaire sur np.integer ni statut spectral NOT_RUN absent du producteur. Aucune provenance DEV inférée de tableaux fournis. |
| Réception globale B2 | REJECTED | gamma_M_sensitivity, prior transmis aux scans, DEV/cache/gel/d_dev/s2_dev/identités et raccordements restent dus. Aucune réception B2 complète ni contrat global partiel promu. |

| Pièce | SHA-256 |
|---|---|
| Source,104414octets | `4bc2be9a46c2768358d713a252911b84ad4a63b3be183ee63a5e16e58527c640` |
| Tests figés,444292octets/585cas | `25024253d408cc9ec8e04279e9ef1e02e6b880c2aa8dfa1d34589d15a12b43f8` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN | `fa2cb37d91337ff09153dd1e70ef4e6d3c48d807d6c9b729129cffc61b285343` |
| Journal pytest GREEN | `c2b0a7bd2d32da1e3324588cc774c759e1c246dc7b4597bdda3db906749ca18b` |
| Journal contrôles GREEN | `09572c47a631205af9fba0ef0f1a23051ef53cc97a9fc2a24e62d299a7dcc976` |

Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Revues détaillées B2q-red, B2q-red-v2 et B2q-green du17novembre.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; parties nominales reçues, intégration encore due.
Tous callbacks B2q traités ; aucun patch/contrôle historique à rejouer.
Suite B2 autorisée par tests seuls, revue et RED avant nouvelle production.
Terminer B2 COMPLET puis STOP et prompt de reprise Codex sur modèle00du12novembre.
Aucun B3/B4 par cette instance. C/runtime/smoke de campagne/profilage/pilote/full/
réel/2020+/JEPA/autres streams/RemoteControl/commit/push/réindexation restent fermés.
