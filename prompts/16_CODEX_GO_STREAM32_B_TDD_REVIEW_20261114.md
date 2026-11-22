# Notification du chercheur à Codex — Stream 32, réception A et activation conditionnée du lot B

**Décision : ACCORD DE PRINCIPE POUR B-TDD, sous vérifications de réception ci-dessous.**
Date : 14 novembre 2026.

Pièces examinées : `prompts/RECEIPT-stream-32-A-20261114.md`, `prompts/PROPOSAL-stream-32-B-TDD-20261114.md`, `prompts/plans/plan-32.md`, `prompts/plans/plan-32-v2.1-amendment.md`, `prompts/GO-stream-32.md`.

## 1. Statut du lot A

Je reconnais la **réception des noyaux A** telle que documentée par Codex : 45 tests ciblés réussis (36 A + 9 R), pyflakes et diff-check propres, producteur PCA `/2` préservé. Ce constat est une **réception technique rapportée**, non une certification indépendante du code par ma revue documentaire.

Ne pas qualifier A de « T1–T22 intégralement terminés ». Les obligations conservées dans le bilan A sont **transférées explicitement à la sortie bloquante du lot B** :
- T10 : raccordement `nonoracle_masks` / `oracle_masks`, préservation des politiques statiques ;
- T15 : calcul et transmission d'un `s2_common` fondé sur `K`, commun à toutes politiques et cardinalités ;
- T16 : contrôle réel des colonnes/libellés `ANALYTIC_PROXY` et du fait que M n'est ni ADD ni RMST, après construction des exports — aucun test sur constante factice ;
- T19/T21 : statuts de refus, NULL_PLAN et HOLD indépendants, `n_hold` figé avant tout HOLD ;
- T22 : refus de fit, eigenvalues, écarts spectraux, erreurs de configuration/identité.

Avant activation, revalider localement les SHA documentés pour la version reçue des sources et des tests A, ainsi que le GO A et les réceptions A1/A2/A3a/A3b. Si les différés T10/T15/T16/T19/T21/T22 n'étaient pas effectivement autorisés par le GO A, inscrire un écart explicite sans réécrire a posteriori le GO A.

## 2. Correction obligatoire dans la proposition B

**Nom exact du document :** remplacer `docs/sections/pca-info-online.md` par **`docs/sections/pca_info_online.md`**, conforme à `plan-32.md` §2.1. Ne pas créer les deux variantes.

Périmètre applicatif inchangé : `experiments/pca_info_online.py`, `tests/test_pca_info_online.py`, `configs/pca_info_online.yaml`, `docs/sections/pca_info_online.md`. Aucun changement scientifique du protocole, de l'Article B, d'E4, de PCA `/2` ou des résultats scellés.

## 3. Autorisation du lot B : TDD sur fixtures seulement

**J'autorise l'activation écrite par Codex du lot B-TDD**, après les deux vérifications précédentes. Cette autorisation du chercheur ne vaut pas activation automatisée ; Codex doit créer son GO B distinct, indiquer son périmètre et activer Claude Code dans la session/worktree existants, conformément au protocole.

Conserver le découpage proposé en sous-lots bornés et revus :
1. identités pré/post exécution, autorisation et staging/reprise, T16 sur vrais exports ;
2. générateurs exact/fitted, univers, familles F0/F1/F2/HEAD/F3, DEV et politiques non-oracles/oracles ;
3. CAL, NULL_PLAN, HOLD, inférence FPR/RMST/HEAD, calibrations réutilisées entre familles et prior commun ;
4. CLI, publication atomique, identités, seed plan et tests de refus/reprise/documentation.

**À la réception de B, fournir la matrice complète T1–T68** avec `PASS`, `FAIL`, `DEFERRED_TO_C_RUNTIME` ou `NOT_RUN`, justification, témoin et commande ; aucun test « applicable » ne peut disparaître sans disposition explicite. Les tests T52–T68 réalisables sur fixtures `tmp_path` doivent être effectués en B ; les vérifications de smoke/profilage réel restent C, sous GO runtime. Le passage RED→GREEN doit être enregistré pour chaque sous-lot.

Contrôles transversaux prioritaires :
- Non-oracle : aucune dépendance à `family`, `Δ`, `tau*`, covariance/centre vrais ; seuil et calibration invariants entre alternatives à setup/politique identiques.
- Masques prévisibles ; aucun rescoring historique ; scan à prior constant et comparaison scellée.
- `design_id` avant tout tirage/worker/écriture scientifique, `realization_id` après les payloads, signatures et reprises sans circularité.
- Graines et partitions déterministes indépendamment de `--jobs`, refus si empreintes incohérentes.
- Qualification oracle FITTED comme `ORACLE_DIAGONAL_SURROGATE`, non optimum KL joint ; HEAD non-infériorité non vacueuse et ses deux contrôles.
- Tests et sorties de fixtures uniquement, sans choix scientifique piloté par une puissance ALT.

## 4. Portes et clôture

**RESTENT FERMÉS :** `RUNTIME_GO`, smoke CLI de campagne, profilage, `PILOT_GO`, `FULL_GO`, accès réel/2020+, JEPA/J4, extension covariance, autres streams. Les simulations miniatures à l'intérieur de tests déterministes sont des **fixtures de TDD**, pas un GO de campagne.

Claude Code n'effectue ni commit/push ni reindexation ; Codex contrôle les patches, les logs, les SHA et, avant toute intégration, `make check` et les scellés. Chaque sous-lot B est soumis à une réception Codex ; un échec de contrat provoque STOP et diagnostic, pas une réduction silencieuse du test.

**Retour attendu :** (i) confirmation des préconditions A et du chemin documentaire corrigé ; (ii) référence du GO B écrit ; (iii) matrice des tests et réserves après chaque sous-lot ; (iv) signalement des blocages, sans lancer le lot C.
