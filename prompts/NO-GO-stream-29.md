# Stream 29 — décision NO-GO sur le plan v1

Date : 2026-10-30. Revue unitaire Codex, limitée au plan 29.

Plan Claude examiné : 346 lignes, SHA-256 `85b47c177e9529c52980cfc8a52c474ec76e2a46bc7d6eb709337d2710ae9b01`, archivé sans modification dans `logs/pca_drift_orchestration/PLAN-v1.md`.

Décision : **révision du plan requise ; aucune implémentation autorisée**. Claude rédige la révision depuis le prompt du stream et les objections ci-dessous ; Codex ne rédige pas un plan de remplacement. Mistral Vibe (`large-4`, thinking `high`) est l'implémenteur désigné, après le GO d'exécution approprié. Claude reste en mode plan.

## Constats conformes

- Distinction moyenne/covariance, KL jointe non additive, coûts covariance signalés comme substituts, aucune recalibration ni resimulation côté tableaux.
- Conservation des deux cohortes Covid, des valeurs manquantes et de la séparation taux de calibration / borne prédictive / FPR holdout. Aucun résultat empirique attribué au smoke comme conclusion scientifique.
- Les six CSV correspondent aux hashes du manifest /2 scellé ; l'identité producteur recalculée correspond à celle du manifest.
- Vérification bornée de H3 sur les artefacts : **1 168 lignes** moyennes renseignées, **zéro** différence exacte sur la somme des q reconstruits et **zéro** différence de classement. Cette recette peut être conservée ; il ne s'agit pas d'un recalcul des détecteurs ou des agrégats.
- Les défauts H1, H2, H4–H9 et H11–H13 peuvent être conservés sous réserve des corrections suivantes. Pas de révision /3 du runner ni d'extension scientifique pour fournir q covariance par axe.

## R1 — Validations conditionnelles au fichier, au type de ligne et à son état

Les règles L8 et L10–L14/L19 ne sont pas assez délimitées pour accepter l'artefact valide qu'elles prétendent valider.

- `selection.csv` contient **610 références metric_id non vides pour 275 IDs distincts**. Cette réutilisation est obligatoire entre E1/E2/E3 et entre méthodes. L'unicité de metric_id concerne `aggregates.csv`, où aucun doublon n'existe ; les autres fichiers gardent leur clé primaire propre.
- Les **192 lignes selection réelles bloquées** n'ont ni `null_calibration_id` ni `null_metric_id`, et **72** ont S manquant. Elles doivent rester présentes, avec métriques empiriques NA. `parse_S` ne peut pas recevoir ces NA ; les FK null/calibration ne peuvent pas être exigées comme pour une mesure synthétique exécutée. Pour la séparation des cohortes, vérifier les identifiants effectivement renseignés, sans inventer un identifiant de calibration absent.
- Les **six agrégats GAUSS_FORMULA_CHECK / GAUSS_PROXY_CHECK_T7** n'ont pas de calibration ni de groupe d'essais à leur metric_id. L13 doit distinguer ces diagnostics des agrégats empiriques effectivement repris dans les tableaux.
- Les valeurs théoriques I/V d'un CANDIDATE ne sont pas une mesure empirique exécutée. Une règle de NA ne doit pas les effacer par confusion avec `execution=NOT_EXECUTED`.

La révision doit énoncer les domaines précis de ces règles et les tests positifs sur les lignes légitimes, en plus des refus de corruption. Aucun durcissement ne doit éliminer les placeholders réels obligatoires ou la réutilisation des métriques.

## R2 — Essais absents et calibration incohérente

- H10/L1 autorisent des essais absents avec avertissement, tandis que L13 exige leur présence pour toute mesure empirique. Fermer cette contradiction : `TRIALS_LOCAL_ONLY` signifie non suivi par Git, pas dispensé de présence sur disque ni de vérification avant publication de mesures. Ne pas annoncer un contrôle réussi des essais absents.
- Le test g4 « calibration mutée en CALIBRATION_FAILED → cellules NA » peut masquer une entrée incohérente conservant des agrégats numériques exécutés. Une telle corruption doit être refusée. Distinguer ce cas d'un véritable artefact CALIBRATION_FAILED cohérent, avec identifiants conservés, mesures NA, absence d'essais et statuts concordants, qui doit être rendu comme tel.

## R3 — Horizon et autorisation réelle

- Les titres RMST250/FPR250 exigent un contrôle explicite de H dans les sources utilisées. La seule égalité de H entre deux méthodes ne suffit pas. Un run /2 à H différent doit être refusé comme incompatible ou rendu avec un libellé fidèle ; aucune conversion ou extrapolation à 250.
- `manifest.pre_j4.frozen_json_present` est un constat de présence, **pas** une preuve de configuration gelée conforme ni une autorisation. Le producteur /2 actuel garde les REAL_EVENT_PATH non exécutés. L14 ne peut autoriser leur publication numérique sur ce seul booléen. Respecter le contrat réellement supporté et les portes J4 ; les tests factices de rendu temporel ne créent aucune dérogation ni lecture réelle post-2019.

## R4 — Répartition des responsabilités et clôture

- Corriger le statut « implémenteur à désigner » : les rôles décidés par le chercheur sont Claude pour les plans, Codex pour l'audit/intégration, Mistral Vibe large-4/high pour l'implémentation. L'étape courante reste plans seulement.
- La séquence ne doit pas demander à Vibe de créer un commit puis de s'arrêter avant push. Vibe remet les résultats à Codex sans mutation Git. Réindexation de clôture, contrôle global et opérations Git sont conduits par Codex, unitairement et processus de stream éteints. Les vérifications ciblées pendant l'implémentation sont distinctes de cette clôture.
- Pour les commandes prévues de contrôle global, `PY=.venv/bin/python` ne suffit pas : le Makefile appelle aussi `pytest`, `pyflakes` et `python` depuis PATH. Préfixer PATH par le .venv partagé ; aucun Python Trading seul ni dépendance modifiée. Aucun journal ne doit entrer dans le staging prévu.
- Le contrôle d'état Git ne peut supposer exactement deux fichiers untracked alors que la revue et la politique sont aussi des modifications Codex tracées. Définir le périmètre attendu sans cacher de fichier étranger.

## R5 — Précisions de vérification

- Le double rendu compare aussi TABLES_VALIDATION.md : y inscrire une commande de régénération déterministe, sans dépendance au répertoire de sortie différent des deux essais. Ne pas recopier un argv variable dans un fichier annoncé identique.
- « Tout calculer en mémoire avant écriture » ne garantit pas l'absence de fichiers partiels lors d'une erreur d'I/O. Décrire exactement le marqueur de complétude du manifest écrit en dernier et le refus d'une sortie incomplète, sans promesse d'atomicité non réalisée.
- La vérification d'un refus attendu avec code 2 doit capturer ce code sans sortie prématurée sous `set -e`. Conserver des commandes exécutables dans l'environnement épinglé.

## Reprise autorisée

Une seule session Claude, `--permission-mode plan`, effort `xhigh` ou `max`, Remote Control nommé, pour une révision autonome intégrant ces corrections. Pas d'écriture applicative, test, simulation, autre stream, réindexation ou opération Git par Claude. Aucun lancement Vibe ou plan 30 avant nouvel audit unitaire du plan 29.
