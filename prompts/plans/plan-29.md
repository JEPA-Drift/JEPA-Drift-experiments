# Plan d'implémentation révisé (v2) — stream 29 (PCA-TABLES) : `Tableau_PCA_1/2/3`

## 0. Statut, rôles et traçabilité de la revue

- **Étape courante : plans seulement.** Ce plan v2 est rédigé en lecture seule par Claude Code. Il remplace le plan v1, archivé par Codex (`logs/pca_drift_orchestration/PLAN-v1.md`, SHA-256 `85b47c17…9b01`), et intègre `prompts/NO-GO-stream-29.md`. Aucun fichier n'a été modifié, aucun test ni simulation n'a été lancé.
- **Rôles** (`prompts/POLICY-PCA-PLAN-ONLY.md`, répartition confirmée par le chercheur) :
  - Claude Code rédige les plans.
  - Codex audite, enregistre `prompts/plans/plan-29.md` et `prompts/GO-stream-29.md` (section « Décision GO intégrée »), puis conduit la clôture : réindexation, `make check` global, opérations Git, processus de stream éteints.
  - **Mistral Vibe `large-4`, thinking `high`, implémente** après le GO d'exécution. Il remet ses résultats à Codex sans aucune mutation Git (ni add, commit, stash, reset, checkout).
- **Correspondance avec le NO-GO** :

| Objection | Où elle est traitée |
|---|---|
| R1 : domaines des validations | §3.2 à §3.6 ; tests positifs g1 (§9) |
| R2 : essais absents, calibration incohérente | H10 révisée ; §3.5 et §3.6 ; g4 |
| R3 : horizon, autorisation réelle | H14 et H15 ; §3.7 et §3.8 ; §6 (sous-tableau réel) ; g4 |
| R4 : rôles, clôture, PATH, état Git | §0 ; §11 |
| R5 : commande déterministe, marqueur de complétude, codes de refus sous `set -e` | §7 ; §8 ; §11 ; g5 |

---

## 1. Faits vérifiés (lecture seule, 2026-10-30)

| Fait | Source | Statut |
|---|---|---|
| Worktree `~/JEPA-stream-29`, branche `stream-29`, HEAD = `main` = `fc533d0` (stream 28 intégré et poussé) | `git rev-parse` ; politique | établi |
| Écarts Git présents avant tout travail : ` M prompts/POLICY-PCA-PLAN-ONLY.md`, `?? prompts/NO-GO-stream-29.md` (modifications Codex) | `git status --porcelain` | établi |
| Artefact /2 scellé `results/pca_drift_benchmark/smoke_predictive_v2_closeout/` (7 fichiers suivis), fingerprint `9926b665…7443`, `run_mode=smoke`, 40 trajectoires par rôle, H = 250 dans `config`, dans les 387 agrégats et dans les 106 calibrations | `manifest.json`, CSV | établi |
| `selection.csv` : **610** références `metric_id` non vides pour **275** identifiants distincts (réutilisation E1/E2/E3 et entre méthodes, obligatoire). Aucun doublon de `metric_id` dans `aggregates.csv`, ni de `null_calibration_id` dans `calibration.csv` | pandas | établi |
| États des lignes synthétiques de `selection.csv` : CANDIDATE/OK/NOT_EXECUTED **1800** (sans `metric_id`, I/V théoriques présents dans les 1800) ; SELECTED/OK/EXECUTED **418** (avec métrique ; dont 4 lignes énergie où k, S et d sont NA) ; SELECTED/CPV90_OUTSIDE_TOP20 **6** et SELECTED/UNSUPPORTED **6**, tous NOT_EXECUTED et sans métrique | pandas | établi |
| Lignes réelles (`D3_239`) : **192**, toutes SELECTED/NOT_EXECUTED, de statut NOT_EVALUABLE_STANDARD_SPLIT ou BLOCKED_PRE_J4. Les 192 ont `metric_id` et `split_hash`, mais **ni** `null_calibration_id **ni** `null_metric_id`. **72** ont S manquant : 60 E2 ORACLE_Q_MIX, plus 3 lignes E3 pour chacune des méthodes CPV90, EXANTE, AFFINE et MIX | pandas | établi |
| Agrégats : ALT_RMST 146 et HOLDOUT 106, tous OK/EXECUTED, avec exactement `n` essais par groupe ; **6** GAUSS_FORMULA_CHECK/GAUSS_PROXY_CHECK_T7 sans calibration ni essais ; REAL_EVENT_PATH 129, tous NOT_EXECUTED à métriques NA. Les 106 calibrations ont exactement `n_cal` essais. Aucun groupe d'essais orphelin | pandas | établi |
| Le producteur /2 n'exécute jamais `evaluate_real_path` dans un run : `real_status_rows` écrit toujours NOT_EXECUTED. `pre_j4.frozen_json_present` est un constat de présence du fichier | `pca_drift_benchmark.py:1484-1552,1802` | établi |
| En mode full réel (non exécuté), les lignes réelles portent en plus `basis_hash`, des `null_calibration_id` D6 par cohorte (garantie NOT_ESTABLISHED, aucune ligne HOLDOUT) et des valeurs théoriques EXANTE (I, M, V) | `run_real:1408-1481` | établi (code) |
| Échec de calibration produit par le runner : la calibration est EXECUTED + CALIBRATION_FAILED, avec `rank_r`, `threshold`, `calibration_fraction`, `predictive_bound` et `calibration_hash` à NA ; ses agrégats sont CALIBRATION_FAILED/NOT_EXECUTED à métriques NA ; aucun essai (ni calibration, ni holdout, ni alternative) ; les lignes de sélection sont CALIBRATION_FAILED/NOT_EXECUTED | `calibrate:1112-1129`, `evaluate_subset:1160-1203` | établi (code) |
| q_k moyenne reconstruit par `q_plugin(beta, lambda_lw)` : Codex mesure **1168** lignes renseignées, **zéro** différence exacte sur Σq et **zéro** différence de classement | `NO-GO-stream-29.md` | établi par Codex |
| `tabulate` est absent ; `pyarrow` est présent. `logs/` est ignoré par Git, `results/pca_drift_benchmark/tables/` ne l'est pas. `.venv` est un lien absolu vers le venv partagé | `find_spec`, `git check-ignore` | établi |

---

## 2. Hypothèses explicites et défauts

H1 à H9 et H11 à H13 sont conservées comme validées par le NO-GO. H10 est révisée ; H14 et H15 sont nouvelles.

| Id | Défaut retenu |
|---|---|
| H1 | `--input-dir` est **obligatoire** et désigne un répertoire de run contenant `manifest.json`. `--output-dir` vaut par défaut `results/pca_drift_benchmark/tables/<basename(input-dir)>/`. |
| H2 | Import en lecture seule `from experiments import pca_drift_benchmark as pdb`, sans déplacer de code vers `jepadrift/` : déplacer modifierait `code_hash` et `run_fingerprint` de la preuve /2 scellée. Écart déclaré `C-pca-tables-design`. |
| H3 | q_k moyenne = `pdb.q_plugin(beta[:20], lambda_lw[:20])`, où beta est rempli depuis `beta_nonzero` (exactement 0 ailleurs). Contrôles bloquants : `np.sum(q[S]) == I_plugin_lw` à l'égalité exacte sur toutes les lignes moyenne renseignées, et `rank_order` égal à `sorted(range(k), key=(-q, axe))`. |
| H4 | q_k^cov par axe = NA, raison `NOT_EXPORTED_SCHEMA_2`. La colonne voisine affiche le cumul source `I_cov_marginal_sum(P_k)` (diagnostic, ≠ KL jointe). Aucune révision /3 du runner. |
| H5 | V covariance affiché sous `COV_HEURISTIC_SURROGATE` (I_cov_joint/M et corde affine), avec avertissements au-dessus et au-dessous du bloc. |
| H6 | La ligne E1 de l'énergie (k NA) ne figure pas dans le Tableau 1. Elle apparaît dans le Tableau 3 (copie E3) et dans les compteurs de validation. |
| H7 | Lignes (1) et (2) « oracle q » de la rotation B : lignes explicites `UNSUPPORTED`, sans métrique, lignée `RULE`. |
| H8 | Type `q_info_type` ∈ {`MEAN_GAUSSIAN_PROXY` (q plug-in LW, deux fonds), `MEAN_GAUSSIAN_EXACT` (seulement `I_pop_joint` sur fond gaussien), `COV_GAUSSIAN_MARGINAL_PROXY`}. L'`info_kind` du runner est recopié tel quel. |
| H9 | Markdown des tableaux en français ; `TABLES_VALIDATION.md`, `docs/sections/pca_drift_tables.md` et wrapup en anglais. Décimale : point. Entrée DEVIATIONS en français, comme les `C-pca-*`. |
| **H10 (révisée)** | Les 7 fichiers du run, `trials.csv` compris, sont **toujours obligatoires sur disque** avec un SHA-256 égal au manifest. `TRIALS_LOCAL_ONLY` signifie « non suivi par Git », pas « dispensé ». Leur absence est un refus (`TRIALS_MISSING`, exit 2) ; aucun chemin d'avertissement n'existe. `--strict` ajoute **seulement** le recalcul `pdb.identity_block(config, inputs) == manifest.identity`, qui détecte un artefact périmé par rapport au code courant. `TABLES_VALIDATION.md` indique si ce recalcul a été exécuté et son résultat, sans jamais l'annoncer s'il n'a pas eu lieu. |
| H11 | Pas de Parquet. Forme longue et lignée dans `table_lineage.csv`. |
| H12 | Les tableaux issus du smoke sont produits dans `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`. Leur commit est décidé par Codex. |
| H13 | Les tests lisent l'artefact suivi (immuable). Les mutations se font sur des copies en mémoire, ou sur des copies de fichiers dans `tmp_path` pour les contrôles de fichier. |
| **H14 (nouvelle)** | Horizon : les titres RMST250/FPR250 imposent `H = 250`. Toute source utilisée (manifest `config.H`, chaque agrégat ALT/HOLDOUT/REAL référencé, chaque calibration référencée) doit avoir `H == 250`, sinon refus `HORIZON_INCOMPATIBLE`. Aucune conversion, aucune extrapolation, aucun libellé variable. |
| **H15 (nouvelle)** | Mesures réelles : sous le schéma /2, une ligne REAL_EVENT_PATH n'est admise qu'à l'état NOT_EXECUTED avec tous ses champs empiriques et R1–R5 à NA. Toute autre forme est refusée (`REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2`), **quel que soit** `frozen_json_present`. Les tableaux n'implémentent aucun rendu de trajectoire réelle exécutée ; ce rendu exigera un nouveau schéma producteur et un nouveau plan après J4 (stream 21). |

---

## 3. Validation d'intégrité : domaines précis

**Principe.** Chaque règle s'applique à un fichier, une classe de lignes et un état donnés. Toute combinaison d'état hors des classes déclarées est refusée (`UNEXPECTED_ROW_STATE`). Une valeur légitimement NA n'est jamais exigée, et une réutilisation légitime d'identifiant n'est jamais refusée.

### 3.1 Contrôles de fichier (bloquants)

| Code | Contrôle |
|---|---|
| F1 | Les 7 fichiers sont présents (H10). |
| F2 | `schema_version` est identique à la racine du manifest, dans `identity` et dans `config`, et égal à `EXPECTED_SCHEMA = "pca_drift_benchmark/2"`. On exige aussi `pdb.SCHEMA_VERSION == EXPECTED_SCHEMA`. |
| F3 | `run_fingerprint == sha256(canon(identity))`. |
| F4 | `identity.config_hash == sha256(canon(config sans resources))`. |
| F5 | `manifest.outputs[f]` (SHA-256, octets, lignes) correspond aux fichiers. |
| F6 | En-têtes CSV identiques, dans l'ordre, à `pdb.COLUMNS[name]`. |
| F7 | Les cellules `schema_version`, `run_fingerprint`, `config_hash`, `seed` et `run_mode` égalent les valeurs du manifest, là où la colonne existe (pas dans `trials.csv`). |
| F8 | Énumérations fermées (`pdb.ENUMS`). `claim_flag` est une liste JSON dont les éléments appartiennent à `CLAIM_FLAGS`. |

**Lecture des CSV :** `float_precision="round_trip"`, type `str` pour les colonnes ID/JSON (`*_id`, `*_hash`, `run_fingerprint`, `group_id`, `S`, `rank_order`, `claim_flag`, `scope`, `detail`, `alarm_dates`, `pre_onset_alarm_dates`, `maxima_sha256`) intersectées avec les colonnes du fichier ; `k`, `d` et `reservoir_k` en `Int64`. Un identifiant tout en chiffres, comme `1005596464754033` dans le smoke, reste une chaîne.

### 3.2 Clés primaires (par fichier)

| Fichier | Clé unique (`pdb.PRIMARY_KEYS`) | Réutilisation légitime |
|---|---|---|
| `aggregates.csv` | `metric_id` | — |
| `selection.csv` | (`selection_id`, `experiment`, `row_kind`, `d`) | `metric_id`, `null_metric_id`, `null_calibration_id` et `selection_id` peuvent se répéter entre E1, E2 et E3, et entre méthodes (smoke : 610 références pour 275 `metric_id`) |
| `calibration.csv` | `null_calibration_id` | — |
| `spectra.csv` | (`dataset_id`, `basis_hash`, `k`) | — |
| `trials.csv` | (`group_id`, `role`, `replicate`) | — |
| `issues.csv` | `issue_id` | — |

### 3.3 Classes d'état de `selection.csv`

| Classe | Domaine (état) | Exigences | Interdits |
|---|---|---|---|
| S-EVAL | synthétique, SELECTED, OK, EXECUTED | `metric_id` → ALT_RMST ; `null_metric_id` → HOLDOUT ; `null_calibration_id` → calibration ; `parse_S(S, 20)` et `d == len(S)`, **sauf** pour la famille ENERGY, où k, S et d sont NA | — |
| S-CALFAIL | synthétique, SELECTED, CALIBRATION_FAILED, NOT_EXECUTED | les trois identifiants présents ; cohérence §3.6 | — |
| S-NOEVAL | synthétique, SELECTED, statut ∈ {CPV90_OUTSIDE_TOP20, UNSUPPORTED}, NOT_EXECUTED | S analysé seulement s'il est présent | `metric_id`, `null_metric_id` ou `null_calibration_id` non NA |
| S-CAND | synthétique, CANDIDATE, OK, NOT_EXECUTED | S présent et analysé ; valeurs théoriques I/M/C/V **conservées telles quelles** | `metric_id` non NA |
| S-REAL | `D3_239`, SELECTED, NOT_EXECUTED, statut ∈ {NOT_EVALUABLE_STANDARD_SPLIT, BLOCKED_PRE_J4, DATA_UNAVAILABLE} | `metric_id` → REAL_EVENT_PATH (§3.8) ; `split_hash` présent ; S analysé **seulement s'il est présent** ; `null_calibration_id` **facultatif** : s'il est présent (mode full), il doit exister dans la calibration avec `null_kind = REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS`, la même cohorte et le même `split_hash` ; `basis_hash` facultatif (s'il est présent, résolu dans spectra) | `null_metric_id` non NA (aucun FPR holdout réel) |

**Règle de séparation théorique / empirique** (contre la confusion R1). L'état `execution` ne gouverne que les **mesures empiriques**, qui sont des colonnes d'`aggregates.csv` : `n`, `alarms`, `fpr*`, `rmst*`, `det*`, `censored_share`, `n_eff`, et les champs R1–R5. Les **valeurs théoriques** de `selection.csv` et `spectra.csv` (λ, CPV, q, I, M, C, V, `I_pop_joint`, `pop_offdiag_max`) sont recopiées telles quelles, et ne sont NA que si la source est NA. Aucune règle ne les efface en raison de NOT_EXECUTED, de CANDIDATE ou d'un statut bloqué. Exemple : les valeurs EXANTE réelles du mode full s'affichent comme théoriques (pré-2020), avec un statut empirique bloqué.

### 3.4 Clés étrangères et accords (S-EVAL, S-CALFAIL, S-REAL)

- **Accord** : entre une ligne de sélection et son agrégat, sur `dataset_id, cohort_id, split_hash, event_window_id, event_id, detector_family, S, d, null_id, null_calibration_id, calibration_hash, basis_hash, config_hash, seed`, **seulement là où les deux côtés sont renseignés**. Aucune jointure sur k seul.
- **HOLDOUT** : le HOLDOUT référencé porte le même `null_calibration_id` que la ligne, et `ALT.null_metric_id == selection.null_metric_id`. Un FPR emprunté à un autre nul est refusé (`FOREIGN_NULL`).
- **Calibration** : la ligne de calibration référencée s'accorde sur `dataset_id, detector_family, S, basis_hash, null_id` et, si présent, `calibration_hash`.

### 3.5 Classes d'agrégats et essais

| Classe | Domaine | Exigences |
|---|---|---|
| A-EMP-OK | ALT_RMST ou HOLDOUT_NULL_FPR, OK, EXECUTED | métriques finies ; calibration liée OK avec seuil fini ; essais **présents** et exactement `n` lignes pour (`group_id = metric_id`, rôle `alternative` ou `holdout_null`) |
| A-EMP-FAIL | ALT_RMST ou HOLDOUT_NULL_FPR, CALIBRATION_FAILED, NOT_EXECUTED | cohérence §3.6 |
| A-CHECK | GAUSS_FORMULA_CHECK ou GAUSS_PROXY_CHECK_T7, OK, EXECUTED | aucune calibration ni groupe d'essais exigé ; **non tabulés** ; compteur « non tabulés : 6 » |
| A-REAL | REAL_EVENT_PATH | §3.8 |

- **Calibrations** : une calibration OK/EXECUTED (synthétique ou réelle) a exactement `n_cal` essais de rôle `calibration` ; une calibration EXECUTED/CALIBRATION_FAILED n'en a aucun. Tout groupe d'essais doit correspondre à un `metric_id` ou à un `null_calibration_id` existant.
- Ces contrôles **comptent** les essais ; ils ne recalculent ni RMST ni FPR.

### 3.6 Cohérence d'un échec de calibration (R2)

Un artefact CALIBRATION_FAILED est **cohérent**, et rendu comme tel, si et seulement si toutes ces conditions tiennent :
1. la calibration est EXECUTED/CALIBRATION_FAILED, `n_cal` et `maxima_sha256` présents, `rank_r`, `threshold`, `calibration_alarms`, `calibration_fraction`, `predictive_bound` et `calibration_hash` à NA ;
2. tous les agrégats ALT/HOLDOUT de ce `null_calibration_id` sont CALIBRATION_FAILED/NOT_EXECUTED, leurs identifiants sont conservés et toutes leurs métriques sont NA ;
3. aucun essai n'existe pour ce `null_calibration_id` ni pour ces `metric_id` ;
4. toutes les lignes de sélection qui les référencent sont CALIBRATION_FAILED/NOT_EXECUTED ;
5. `issues.csv` contient au moins une issue de code CALIBRATION_FAILED (contrôle par code, scope non interprété).

Toute violation (par exemple un agrégat numérique ou EXECUTED conservé, ou des essais présents) est **refusée** (`INCOHERENT_CALIBRATION_FAILURE`). Elle n'est jamais masquée par des cellules NA.

### 3.7 Horizon (R3, H14)

`manifest.config.H == 250` ; `H == 250` pour chaque agrégat ALT/HOLDOUT/REAL et chaque calibration référencés par un tableau ; `time_origin == ONSET_ALIGNED` pour chaque ALT_RMST. Sinon refus `HORIZON_INCOMPATIBLE`. Comparer les H de deux méthodes entre elles ne suffit pas.

### 3.8 Contrat réel /2 (R3, H15)

- Chaque REAL_EVENT_PATH doit être NOT_EXECUTED, avec un statut égal à celui de ses lignes de sélection, et tous ses champs empiriques NA. Les champs R1–R5 concernés sont `n_event_sessions`, `alarm_dates`, `pre_onset_alarms`, `pre_onset_alarm_dates`, `detected_during_event`, `time_to_alarm_during_event`, `event_censored`, `post_onset_delay_h250`, `post_onset_alarm_date`, `post_event_alarm` et `path_supports_H`.
- Aucun essai de rôle `real_path` n'est admis.
- `pre_j4.frozen_json_present` n'autorise rien.
- **Séparation des cohortes** : les deux cohortes Covid doivent être présentes, avec des `claim_scope` respectifs REAL_STANDARD_SPLIT et REAL_RETROSPECTIVE_EXPLORATORY ; la cohorte standard doit avoir le statut NOT_EVALUABLE_STANDARD_SPLIT pour COVID_2020. Leurs ensembles d'identifiants **effectivement renseignés** (`selection_id`, `metric_id`, `split_hash`, et `null_calibration_id`/`calibration_hash` lorsqu'ils sont présents) doivent être disjoints. Le smoke a 0 `null_calibration_id` renseigné ; le rapport l'indique sans inventer d'identifiant.

### 3.9 Spectres et identités inter-expériences

- **Spectres** : k = 1..N par base ; `lambda_lw > 0` et non croissant ; `cpv_lw` non décroissant ; `cpv_lw[20] ≤ 1` ; `mp_count == Σ mp_above` ; `kaiser_count == Σ kaiser_ge1` ; `cpv90_k_full` = premier k avec `cpv_lw ≥ 0,9` ; `cpv90_status` cohérent.
- **L16** : chaque ligne E2 `BASELINE_PREFIX` égale la ligne E1 sur `selection_id`, `metric_id`, `null_metric_id`, `null_calibration_id` et sur toutes les valeurs.
- **L17** : les copies E3 `ORACLE_Q_MIX` et `COV_JOINT_ORACLE` égalent les lignes E2 à k = 20. Pour la covariance, il s'agit d'un contrôle de réutilisation d'artefact, sans langage d'optimalité additive.
- **L18** : contrôle H3.

---

## 4. Tableau_PCA_1 — référence spectrale (k = 1..20)

**Bloc** = (`dataset_id`, `cohort_id`, `event_id`, `detector_family`) des lignes E1 `BASELINE_PREFIX`. Exactement 20 lignes par bloc, k croissant ; sinon refus. Smoke attendu : **9 blocs, 180 lignes** (6 synthétiques, 3 réels).

| Colonne CSV | Titre Markdown | Source |
|---|---|---|
| `k`, `d` | `Indice k`, `Dimension retenue` | selection E1 (`d = k`) |
| `lambda_lw` | `Valeur propre λ_k` | spectra (`dataset_id`, `basis_hash`, `k`) — covariance LW |
| `cpv_lw` | `Variance cumulée CPV_k (%)` | spectra (×100 à l'affichage seulement) |
| `mp_count, mp_edge, kaiser_count, cpv90_k_full, cpv90_status, criteria` | `Critères standard` | spectra : « MP (corr.) » à k = `mp_count` ; « CPV 90 % » à k = `cpv90_k_full` s'il est ≤ 20 ; « Kaiser corr. λ≥1 » à k = `kaiser_count` s'il est ≤ 20 ; « — » sinon. Note de bloc `CPV90_OUTSIDE_TOP20 (k90_full = …)`. Jamais « Kaiser λ<1 » |
| `rmst, rmst_lo, rmst_hi, det_rate, censored_share, n_alt` | `RMST250 préfixe (jours)` | ALT_RMST [`metric_id`] |
| `fpr_test_null, fpr_lo, fpr_hi, n_eval` | `FPR250 hors dérive` | HOLDOUT [`null_metric_id`] (Wilson) |
| `fpr_calibration, n_cal, predictive_bound, target_fpr, threshold_rule, guarantee_basis` | sous-tableau de provenance | calibration [`null_calibration_id`] (`calibration_fraction`, `alpha`) |
| `selection_id, metric_id, null_metric_id, null_id, null_calibration_id, calibration_hash, basis_hash, split_hash, config_hash, seed, source_kind, claim_scope, status, execution, na_reason` | provenance | selection ; issues pour `na_reason` |

Lignes réelles du smoke : λ et CPV à NA (`REAL_NOT_RUN`) ; mesures empiriques NA avec le statut du runner. En mode full, λ et CPV réels sont affichés (théoriques) ; `fpr_calibration` et `n_cal` D6 sont affichés en provenance, avec `guarantee_basis = NOT_ESTABLISHED_HISTORICAL_WINDOWS` ; `fpr_test_null` et `predictive_bound` restent NA.

---

## 5. Tableau_PCA_2 — préfixe P_k contre sous-ensemble S*_k ⊆ P_k

**Bloc** = clé du Tableau 1 + `objective_kind` du sélecteur E2 : `ORACLE_Q_MIX` en MEAN, `COV_JOINT_ORACLE` sous `COV_JOINT_AFFINE_SURROGATE` et `COV_JOINT_MIX_HEURISTIC` en COV, `ORACLE_Q_MIX` bloqué pour le réel. Smoke attendu : 4 blocs moyenne + 4 covariance + 3 réels = **11 blocs, 220 lignes**. Les familles sont nommées séparément (`block_family = MEAN | COV`).

**Invariant d'identité.** Les colonnes préfixe (`rmst_prefix*`, `fpr_prefix*`, `metric_id_prefix`, `null_metric_id_prefix`) **sont les objets** de l'enregistrement Tableau 1 de même (bloc T1, k) : pas de nouvelle jointure, pas de recalcul, pas d'arrondi. Prérequis de comparabilité entre préfixe et S*, refus sinon : mêmes `dataset_id, cohort_id, split_hash, detector_family, null_id, basis_hash, event_window_id`, et H (= 250), `time_origin` et `n` égaux pour ALT et HOLDOUT.

| Colonne CSV | Titre Markdown | Source |
|---|---|---|
| `k`, `lambda_lw` | `Indice PCA k`, `Variance λ_k (H0)` | selection, spectra |
| `q_k, q_info_type, q_source` | `Information marginale q_k (type)` | MEAN : H3 (`FORMULA_Q_PLUGIN`, `MEAN_GAUSSIAN_PROXY`) ; COV : NA `NOT_EXPORTED_SCHEMA_2` ; réel : NA |
| `I_marginal_cum_prefix` | `Σ_{j≤k} q_j^cov (diagnostic)` | COV : `I_cov_marginal_sum` de la ligne préfixe |
| `I_prefix, V_prefix, V_prefix_meaning` | `Score préfixe V(P_k)` | ligne préfixe : `V_mix` (bloc MIX) ou `V_affine` (bloc AFFINE) ; sens `MEAN_MIX_FLUID_SURROGATE` ou `COV_HEURISTIC_SURROGATE` |
| `rmst_prefix…`, `fpr_prefix…`, `metric_id_prefix` | `RMST250 préfixe`, `FPR250 préfixe` | **objets du Tableau 1** |
| `S_star, d_star, I_star, V_star, V_star_meaning` | `Sous-ensemble optimal S*_k`, `Score V(S*_k)`, `Dimension optimale d*_k` | E2 SELECTED (S recopié : JSON trié, base 1) |
| `rmst_selected…`, `fpr_selected…`, `metric_id_subset`, `null_metric_id_subset` | `RMST250 sélection`, `FPR250 sélection` | aggregates |
| `I_pop_joint_prefix, I_pop_joint_star, pop_offdiag_max_star` | provenance | MEAN : `MEAN_GAUSSIAN_EXACT` (fond gaussien) ou `MEAN_GAUSSIAN_PROXY` (t7) |
| `selector_kind, selection_exact, tie_broken, oracle_input, claim_flag, info_kind, status_prefix, status_subset, dataset_id, event_id, detector_family, objective_kind, cohort_id` | provenance | selection |

- **Moyenne** : « I(S) = Σ q_j, référence gaussienne diagonale plug-in LW » ; q et V sont des proxies sous fond t7. Le RMST est empirique. `I_pop_joint` est affiché à part, sans équivalence d'optima. Sur C gaussien, les deux grandeurs divergent : 1,589 contre 3,000 à P_20.
- **Covariance** : avertissements au-dessus et au-dessous du bloc. I_cov_joint n'est pas additif ; M est un coût fluide de mélange en moyenne, non validé pour la covariance ; le classement marginal n'est pas l'oracle covariance ; `selection_exact = True` résulte de la recherche exhaustive.

---

## 6. Tableau_PCA_3 — ablations et sélection ex ante

**Groupe** = (`dataset_id`, `cohort_id`, `event_id`). Ordre fixe des lignes :

| Ordre | « Pipeline & règle » | Méthode | Moyenne | Covariance B |
|---|---|---|---|---|
| (0) | Baseline CPV 90 % | `BASELINE_CPV90` | oui | oui |
| (1) | Oracle tri q + coût affine C(d) = a + c d | `ORACLE_Q_AFFINE` | oui | `UNSUPPORTED` (H7) |
| (2) | Oracle tri q + substitut fluide M(d, γ_M) — et non « coût exact » | `ORACLE_Q_MIX` (E3 = E2 à k = 20) | oui | `UNSUPPORTED` (H7) |
| (3) | Glouton ex ante q̄ (stress 2008/2011) | `EXANTE_QBAR` | synthétique `UNSUPPORTED` ; réel bloqué | `UNSUPPORTED` |
| (D1) | Recherche jointe covariance, coût affine (diagnostic oracle Σ1) | `COV_JOINT_ORACLE`/AFFINE | — | oui |
| (D2) | Recherche jointe covariance, coût M heuristique | `COV_JOINT_ORACLE`/MIX_HEURISTIC | — | oui |
| (D3) | Classement marginal q^cov (diagnostic, pas l'oracle covariance) | `COV_MARGINAL_DIAGNOSTIC` | — | oui |
| (C) | Comparateur énergie d'indice (famille de détecteur distincte) | `ENERGY_INDEX_COMPARATOR` | — | oui |

Smoke attendu : 4 × 4 + 2 × 8 + 3 × 4 = **44 lignes**.

**Colonnes principales** (d* entre RMST et FPR) : `Rupture testée | Pipeline & règle | Information I(S) / type | Coût M(d) / applicabilité | Score V(S) / sens | RMST250 (jours) | Dimension retenue d* | FPR250`.

**Colonnes ajoutées :** `n_alt, n_eval, n_cal, rmst_lo/hi, fpr_lo/hi, fpr_calibration, predictive_bound, det_rate, censored_share, event_window_id, oracle_input, claim_flag, null_calibration_id, calibration_hash, basis_hash, S, metric_id, null_metric_id, status, execution, comparability, cpv90_k_full` (diagnostique, jamais présenté comme une sélection concurrente), `footnotes`.

**Règles :**
- (2) moyenne : S, V_mix, d*, RMST et `metric_id` **sont les objets** de l'enregistrement Tableau 2 à k = 20 ; L17 contrôle de plus la copie E3.
- (0) hors des 20 premiers axes : métriques NA, `NOT_COMPARABLE_OUTSIDE_TOP20`.
- (D3) : la somme marginale (`COV_GAUSSIAN_MARGINAL_PROXY`) est affichée à côté d'`I_cov_joint` du même S.
- Valeurs théoriques recopiées selon §3.3.

**Sous-tableau « Épisodes réels (trajectoire unique) »**, une ligne par (cohorte, événement, méthode) :
- cohorte : `cohort_id`, `claim_scope`, statut ;
- découpage : calib 2016-04-07..2019-12-31, `monitor_start`, embargo (65 ou 0) et `pre_onset_policy`, tels que le manifest `real.cohorts` les donne ;
- armement : `monitor_armed_from`. Standard : 2020-04-06. Rétrospective : NA, rendue « non armé : évaluation non exécutée ; première séance de 2020 non lue avant J4 ». La date 2020-01-02 n'est pas affirmée ;
- `onset_date`, `event_end_date` ;
- colonnes R1–R5 (`time_to_alarm_during_event`, `detected_during_event`, `rmst250_post_onset`, `pre_onset_alarms`, `post_event_alarm`, `path_supports_H`) : **présentes et NA**, statut « non exécuté (schéma /2, avant J4) » ;
- FPR et intervalles réels : NA (R5), aucun pseudo-intervalle binomial ;
- étiquettes `EX_POST_ORACLE` et `RETROSPECTIVE_DIAGNOSTIC` reprises de `claim_flag`.

Les lignes standard et rétrospective ne partagent aucun identifiant renseigné (§3.8).

---

## 7. Rendu, lignée, validation, manifest, marqueur de complétude

**Affichage.** `fmt(value, kind)` : λ, q, I, V en `.4g` ; M et C en `.4f` ; CPV et FPR en `%` à une décimale ; RMST à une décimale ; intervalles au format `x [lo, hi]` ; S compacté (`{1–3, 10}`) ; `NA` pour une valeur absente ; `NOT_MEASURED` quand une cible existe sans FPR atteint. Les CSV gardent les valeurs source non arrondies, réécrites en `%.17g` via `save_fair_csv` (même texte que la cellule source) ; leurs colonnes numériques sont typées `float64`/`Int64` avant écriture.

**Markdown** (rendu minimal sans `tabulate`, `|` échappé), pour chaque bloc :
- **en tête** : dataset, N, T_fit/H ou dates réelles, loi (équicorrélée ρ = 0,4 ; t7 avec un χ²₇ par jour), dérive injectée et amplitude (manifest `scenarios`), famille de détecteur et calibration (`threshold_rule`, `rank_r`, borne, `alarm_rule`, `s2_rule`), H = 250, effectifs (smoke 40 ; complets prévus 2000, non exécutés), provenance de la sélection ;
- **en pied** : statut des substituts covariance, censure, égalités départagées (`tie_broken`), proxies t7 ;
- bannière `SMOKE_NO_CLAIMS` en mode smoke ;
- par document : section « Méthodologie et définitions », légende des abréviations, registre de notes à identifiants stables (des définitions, jamais d'interprétation) ;
- tableau principal aux titres français, plus un sous-tableau de provenance relié par `row_id`.

**Identifiants.** `block_id = pdb.sha16({table, dataset_id, cohort_id, event_id, detector_family, objective_kind})` ; `row_id = "<T>:<block_id>:<k|ordre>"`. Tri déterministe.

**`table_lineage.csv`.** Une ligne par cellule affichée : `table, row_id, column, kind (SOURCE|FORMULA|MANIFEST|RULE), source_file, source_key (JSON canonique de la clé primaire), source_column, formula, inputs`.

**Commande de régénération déterministe** (R5), identique dans `TABLES_VALIDATION.md` et dans `table_manifest.json`. Elle est construite à partir des options canoniques, jamais à partir d'`argv` :
```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
.venv/bin/python experiments/pca_drift_tables.py --input-dir <rel_input> --output-dir <OUT> \
  --format <fmt> [--dataset …] [--scenario …] [--detector-family …] [--strict]
```
`<rel_input>` est le chemin relatif au dépôt, normalisé par `pdb._rel` (le nom seul si le répertoire est hors du dépôt). La sortie est toujours le littéral `<OUT>`. Aucun chemin absolu, horodatage ou durée n'est écrit.

**`TABLES_VALIDATION.md`** (anglais) :
- compteurs par fichier et par classe d'état (§3.3, §3.5 : 1800/418/12/192, 146/106/6/129, 610 → 275) ;
- lignes par tableau et par bloc ; NA par raison ;
- blocs non tabulés et motifs ;
- SHA-256 des 7 sources ;
- liste des contrôles avec PASS/FAIL ; ligne « identity recomputation: PASS | NOT RUN (no --strict) » ;
- commande de régénération.

**`table_manifest.json`** : `tables_schema = "pca_drift_tables/1"`, `input` (`<rel_input>`, `run_fingerprint`, `schema_version`, `run_mode`, SHA des sources), `code` (SHA-256 de `pca_drift_tables.py` et du runner), `environment`, `filters`, `format`, `strict`, `command` (le gabarit), `columns` (nom CSV → titre français), `outputs` (SHA, octets, lignes de chaque autre fichier), `tables_fingerprint = sha256(canon({tables_schema, input, code, environment, filters, format, strict}))`.

**Ordre d'écriture et marqueur de complétude** (sans promesse d'atomicité de l'ensemble) :
1. Toute la validation et la construction se font en mémoire. Une erreur détectée à ce stade donne exit 2 et aucun répertoire créé.
2. Le répertoire de sortie doit être absent ou vide, sinon exit 2. Le script ne supprime jamais rien.
3. Écriture des CSV et MD, puis `table_lineage.csv`, puis `TABLES_VALIDATION.md`.
4. `table_manifest.json` est écrit en dernier, dans `table_manifest.json.partial`, puis renommé par `os.replace` (rename POSIX dans le même répertoire).
5. **Définition** : une sortie est complète si et seulement si `table_manifest.json` existe et que chaque fichier listé dans `outputs` existe avec son SHA-256. Un répertoire sans manifest, ou au contenu discordant, est incomplet.
6. Une erreur d'E/S pendant l'écriture donne exit 3 et un message « output incomplete (no table_manifest.json) ». Des fichiers partiels peuvent rester ; une nouvelle invocation sur ce répertoire est refusée (exit 2).

La fonction `verify_output_dir(path)` applique la définition du point 5. Elle est utilisée par les tests et documentée pour les consommateurs (streams 30 et 31).

---

## 8. CLI et codes de sortie

`--input-dir DIR` (obligatoire), `--output-dir DIR`, `--dataset {dataset_id}`, `--scenario {event_id}`, `--detector-family {famille}` (valeurs validées contre `pdb.ENUMS`), `--format csv|md|both` (défaut `both` ; validation, lignée et manifest toujours écrits), `--strict` (H10).

Codes de sortie :
- 0 : succès ;
- 2 : refus (usage, environnement via `pdb.check_env`, intégrité, horizon, contrat réel, essais absents, échec du recalcul d'identité sous `--strict`, sortie non vide) ;
- 3 : écriture incomplète.

---

## 9. Couverture et tests — `tests/test_pca_drift_tables.py`

**Couverture du smoke :**

| Cas | T1 | T2 | T3 |
|---|---|---|---|
| Moyenne gaussienne A, C | 2 × 20 | 2 × 20 MIX | 2 × 4 |
| Moyenne t7 A, C | 2 × 20 | 2 × 20 PROXY | 2 × 4 |
| Covariance B30 (Gauss, t7) | 2 × 20 | 2 × 2 × 20 heuristique | 2 × 8 |
| COVID standard / rétrospectif ; STYLE 2022 | 3 × 20 NA | 3 × 20 NA | 3 × 4 NA |
| Covariance réelle ; B15/B45 | — | — | notes (`UNSUPPORTED` ; balayage différé) |

**Tests.** Développement TDD, RED puis GREEN par groupe. Fixture de module chargée une fois ; mutations sur copies profondes en mémoire, ou sur copies de fichiers dans `tmp_path`. Les tests ne lancent pas le runner, ne lisent aucune donnée réelle et ne simulent rien. Durée visée : moins de 20 s.

| Groupe | Tests positifs (lignes légitimes) | Tests négatifs (corruptions) |
|---|---|---|
| g1 entrée | le smoke est accepté avec les compteurs de §1 : 610 références pour 275 `metric_id` acceptées ; 192 lignes réelles sans `null_calibration_id`/`null_metric_id` acceptées ; 72 lignes réelles avec S NA acceptées sans appel à `parse_S` ; 1800 CANDIDATE avec I/V conservés ; 6 contrôles GAUSS acceptés sans essais ; 12 lignes S-NOEVAL acceptées ; comptes d'essais égaux à `n`/`n_cal` ; identifiant tout en chiffres conservé | octet ajouté (copie) → `HASH_MISMATCH` ; schéma /1 → refus ; `run_fingerprint` altéré → refus ; `metric_id` dupliqué dans aggregates → refus ; énumération inconnue → refus ; CANDIDATE avec `metric_id` → `UNEXPECTED_ROW_STATE` ; ligne réelle avec `null_metric_id` → refus ; S-EVAL sans calibration → refus ; HOLDOUT d'un autre nul → `FOREIGN_NULL` ; `trials.csv` retiré (copie) → `TRIALS_MISSING`, exit 2, **sans** `--strict` ; un essai retiré (en mémoire) → refus |
| g2 T1 | 9 blocs × 20, k = 1..20 ; CPV non décroissant, `CPV_20 ≤ 1` ; `CPV90_OUTSIDE_TOP20` (158/152) sans marqueur dans 1..20 ; MP à k = 1 ; aucun « λ<1 » ; FPR égal à la cellule HOLDOUT source ; α dans une colonne distincte | bloc privé d'une ligne k → refus |
| g3 T2 | identité préfixe T1/T2 : mêmes objets en mémoire, texte des cellules CSV relues identique, `metric_id` égaux ; H3 exact (Σq, `rank_order`) ; q de A non nul seulement sur l'axe 1, q de C seulement sur 10..20 ; blocs COV : q_k NA `NOT_EXPORTED_SCHEMA_2`, sens `COV_HEURISTIC_SURROGATE`, avertissement présent dans le MD | ligne E2 de préfixe dont le `metric_id` diffère de E1 → refus L16 ; q dérivé discordant (beta altéré) → refus L18 |
| g4 T3 | T2[k=20] et T3 (2) : S, V, RMST et `metric_id` identiques sur A et C ; deux lignes Covid distinctes, standard à NA ; échec de calibration **cohérent** construit en mémoire (§3.6, conditions 1 à 5) rendu en NA avec statut CALIBRATION_FAILED et identifiants conservés ; valeurs théoriques EXANTE réelles (forme du mode full, en mémoire) affichées avec un statut empirique bloqué | ligne COV relabellisée `ORACLE_Q_MIX` → refus ; RMST numérique sur la ligne standard → refus ; `metric_id` partagé entre cohortes → refus ; échec **incohérent** (agrégats numériques ou EXECUTED conservés, ou essais conservés) → `INCOHERENT_CALIBRATION_FAILURE` ; H = 200 dans `config` et les agrégats → `HORIZON_INCOMPATIBLE` ; REAL_EVENT_PATH muté en EXECUTED avec valeurs numériques **et** `frozen_json_present = True` → `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2` |
| g5 écriture/CLI | cellules CSV égales au texte source ; MD arrondi selon `fmt` ; aucun `0` à la place d'un NA ; deux exécutions vers des répertoires différents donnent des fichiers identiques octet pour octet, `TABLES_VALIDATION.md` et `table_manifest.json` compris (commande gabarit avec `<OUT>`), et le même `tables_fingerprint` ; `verify_output_dir` vrai ; lignée complète (chaque cellule affichée a sa ligne, chaque pointeur SOURCE se résout) ; filtres ; `--format csv` sans `.md` de tableau ; `--strict` passe sur le smoke ; aucun `/home/` | sortie non vide → exit 2 ; échec d'E/S simulé (monkeypatch d'`OSError` après le premier fichier) → exit 3, pas de `table_manifest.json`, `verify_output_dir` faux, réinvocation → exit 2 ; valeur de filtre inconnue → exit 2 |

Les contrats inter-tableaux complets, dont l'énumération exhaustive pour k ≤ 12, restent au stream 31.

---

## 10. Livrables, documentation, écarts

**Livrables de l'implémenteur :**
- `experiments/pca_drift_tables.py`, `tests/test_pca_drift_tables.py` ;
- `docs/sections/pca_drift_tables.md` (anglais ; contrat `pca_drift_tables/1` pour les streams 30 et 31 : fichiers, colonnes, clés, `block_id`/`row_id`, lignée, statuts, définition de complétude, commande) ;
- `docs/DEVIATIONS.md`, **ajout seulement** : `C-pca-tables-design` (H1, H2, H3, H4, H6, H7, H8, H10, H11, H14, H15, libellé « substitut fluide ») ;
- `prompts/wrapups/wrapup-29.md` (anglais, six rubriques, SHA-256 des sorties) ;
- les 9 sorties de `results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout/`.

**Non touchés :** runner, `configs/`, `docs/sections/pca_drift_benchmark.md`, artefacts `results/pca_drift_benchmark/smoke*`, `results/e2`, `results/e3`, `tools/`, `prompts/streams/`, master des prompts, et les fichiers de Codex (politique, NO-GO, GO, plan-29).

---

## 11. Séquence d'exécution et vérifications

### 11.1 Phase Vibe, après le GO : implémentation et vérifications ciblées, sans mutation Git

```bash
set -euo pipefail
cd ~/JEPA-stream-29
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
export PATH="$PWD/.venv/bin:$PATH"
PY="$PWD/.venv/bin/python"; L=logs/pca_drift_tables; R=results/pca_drift_benchmark
IN=$R/smoke_predictive_v2_closeout; OUT=$R/tables/smoke_predictive_v2_closeout
mkdir -p "$L"
# g0 — préconditions et état initial (aucun fichier étranger caché)
test "$(git rev-parse --abbrev-ref HEAD)" = stream-29
git merge-base --is-ancestor fc533d003098a45c8ce533876642712d47038b31 HEAD
git status --porcelain=v1 --untracked-files=all | LC_ALL=C sort > "$L/status_before.txt"
cut -c4- "$L/status_before.txt" | while IFS= read -r p; do sha256sum -- "$p"; done > "$L/status_before.sha256"
(cd "$IN" && sha256sum -c --strict --quiet <<'EOF'
6bd41250db9059abd19f4ec0976c8976fc54204e4321d66ad1b3a409c46e2f07  aggregates.csv
04d463b42556dfcd784ef4833c9f4cec789f194cb436c093ce8c25b370c4378d  calibration.csv
d7a276f9a52e5ed798e7f0e59a8b73d5a36e1478dd7d4754618d4ded2ce72caf  issues.csv
f7b8406c7a73e0a19c905e9ef1104820b32d398269eecd6c40683c399f76655f  selection.csv
3718ed94123c0dad17505657383a1722d3e42d1f482b78b0d36f7efb28ca5e17  spectra.csv
3dcf83a82685a014fafef213358305239866eaf0851ffcc525cdbe6c455aa7be  trials.csv
0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9  manifest.json
EOF
)
E2=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
test "$(sha256sum results/e2/e2_cells.csv | cut -d' ' -f1)" = "$E2"
test "$(git show :results/e2/e2_cells.csv | sha256sum | cut -d' ' -f1)" = "$E2"
grep -qF "relative gap +0.0528334213 > 0.05" docs/DEVIATIONS.md
test ! -e configs/FROZEN.json
test ! -e "$OUT"
# g1–g5 — TDD (RED puis GREEN consignés dans $L/tdd.log)
"$PY" -m pytest -q tests/test_pca_drift_tables.py
"$PY" -m pyflakes experiments/pca_drift_tables.py tests/test_pca_drift_tables.py
# double rendu vers deux répertoires neufs
"$PY" experiments/pca_drift_tables.py --input-dir "$IN" --output-dir "$OUT" --strict > "$L/run.log" 2>&1
test ! -e "$L/repeat"
"$PY" experiments/pca_drift_tables.py --input-dir "$IN" --output-dir "$L/repeat" --strict > "$L/repeat.log" 2>&1
FILES="TABLES_VALIDATION.md Tableau_PCA_1.csv Tableau_PCA_1.md Tableau_PCA_2.csv Tableau_PCA_2.md Tableau_PCA_3.csv Tableau_PCA_3.md table_lineage.csv table_manifest.json"
test "$(ls -A "$OUT" | LC_ALL=C sort | tr '\n' ' ')" = "$FILES "
for f in $FILES; do cmp -- "$OUT/$f" "$L/repeat/$f"; done
# refus attendu (code 2) capturé sans sortie prématurée sous set -e
rc=0; "$PY" experiments/pca_drift_tables.py --input-dir "$IN" --output-dir "$OUT" > "$L/refusal.log" 2>&1 || rc=$?
test "$rc" -eq 2
if grep -rlF "/home/" "$OUT"; then exit 1; fi
# invariants : DEVIATIONS en ajout seul, fichiers protégés inchangés
cmp <(git show HEAD:docs/DEVIATIONS.md) <(head -c "$(git cat-file -s HEAD:docs/DEVIATIONS.md)" docs/DEVIATIONS.md)
git diff --quiet HEAD -- experiments/pca_drift_benchmark.py configs tools prompts/streams results/e2 results/e3 \
  "$IN" docs/sections/pca_drift_benchmark.md
# état Git final : entrées initiales intactes, nouvelles entrées = livrables exactement
git status --porcelain=v1 --untracked-files=all | LC_ALL=C sort > "$L/status_after.txt"
comm -23 "$L/status_before.txt" "$L/status_after.txt" > "$L/status_removed.txt"; test ! -s "$L/status_removed.txt"
sha256sum -c --strict --quiet "$L/status_before.sha256"
{ printf '%s\n' ' M docs/DEVIATIONS.md' '?? docs/sections/pca_drift_tables.md' '?? experiments/pca_drift_tables.py' \
    '?? prompts/wrapups/wrapup-29.md' '?? tests/test_pca_drift_tables.py'
  for f in $FILES; do printf '?? %s/%s\n' "$OUT" "$f"; done; } | LC_ALL=C sort > "$L/allowlist.txt"
comm -13 "$L/status_before.txt" "$L/status_after.txt" | cmp - "$L/allowlist.txt"
```

Vibe remet ensuite à Codex :
- le wrapup-29 ;
- les journaux `logs/pca_drift_tables/` (ignorés par Git, jamais stagés) ;
- la liste des livrables et de leurs SHA-256.

Vibe ne lance ni réindexation, ni `make check` global, ni opération Git.

### 11.2 Phase Codex : clôture, unitaire, processus de stream éteints

À titre de spécification. Codex conduit et adapte selon ses propres portes.

```bash
set -euo pipefail
cd ~/JEPA-stream-29
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin
export PATH="$MAKEBIN:$PWD/.venv/bin:$PATH"   # make épinglé, puis python/pytest/pyflakes du venv partagé
tools/reindex_graphify_jcodemunch.sh          # AST seul, sans résumés IA ; ambiguïté jCodeMunch connue, aucune invalidation
make check                                    # environnement global établi pour le 28 (shim torch C-torch-conda-forge si requis)
```

Ensuite :
- staging par chemins explicites : livrables du §10, plus les fichiers Codex retenus (plan-29, GO-29, NO-GO-29, politique). **Aucun journal**, aucun `git add -f` ;
- revue de `git diff --staged` ; aucun fichier de plus de 50 Mo ni chemin EUROFIDAI ;
- commit Conventional sans trailer, puis push et fast-forward selon le protocole du dépôt.

L'état Git final s'évalue par rapport à l'état initial consigné, sans supposer un nombre fixe de fichiers non suivis.

---

## 12. Points de vigilance

- **pandas 3 avec pyarrow.** Typage `str` des identifiants obligatoire. Les colonnes booléennes contenant des NaN sont lues en `object`. Un flottant dans une colonne `object` ne reçoit pas le `%.17g` et casserait l'identité textuelle.
- **Couplage au runner.** L'import charge scipy, yaml et `jepadrift`, et applique les `setdefault` d'environnement avant numpy. Si le runner passe à un schéma /3, `EXPECTED_SCHEMA` le refuse, ce qui impose un ré-audit.
- **Portée.** Les tableaux du smoke (n = 40, trajectoires partagées) ne fondent aucune conclusion sur FPR ou RMST. Les tableaux du full ne seront produits qu'après l'autorisation et la production du run full. Son `trials.csv` local, même au-delà de 50 Mo, doit être présent sur disque (H10).
- **Rendu réel.** Toute publication numérique d'une trajectoire réelle exige un schéma producteur postérieur à J4 et un nouveau plan. `frozen_json_present` n'en tient pas lieu.

**[Strategic Advice]**
- Faire relire par les streams 30 et 31 le contrat `pca_drift_tables/1` (`row_id`, `block_id`, `table_lineage.csv`, `verify_output_dir`) avant leurs plans, pour que la figure et les contrats consomment les mêmes pointeurs au lieu de refaire les jointures.
- La définition des classes d'état (§3.3 à §3.8) peut devenir la référence partagée du stream 31 : ses tests négatifs gagneraient à réutiliser les mêmes codes de refus.
- Après le run full, régénérer les tableaux dans `results/pca_drift_benchmark/tables/full/` avec `--strict`. La comparaison des `tables_fingerprint` entre smoke et full servira de trace d'audit.

## Décision GO intégrée

GO du **plan v2 uniquement**, décidé par Codex le 2026-10-30 dans le cadre de l'audit délégué. Les objections R1 à R5 du NO-GO v1 sont levées. Les défauts H1 à H15 sont retenus avec les précisions de domaine ci-dessous, qui priment sur les formulations générales du plan.

1. **Champs applicables et états.** La finitude s'exige pour les mesures pertinentes au `metric_kind` et à leur effectif ; FPR dans un ALT_RMST et RMST dans un HOLDOUT restent NA, comme les intervalles non définis par le producteur. Les valeurs théoriques ne sont pas des mesures exécutées. La cascade CALIBRATION_FAILED vers ALT/HOLDOUT du §3.6 concerne les mesures synthétiques ; une calibration D6 réelle échouée ne transforme pas les lignes réelles bloquées en évaluations exécutées, ni ne remplace leur statut fourni par le runner. Les tests positifs g1/g4 couvriront ces domaines sans compléter une valeur manquante.
2. **Séparation des cohortes.** Le contrôle de disjonction concerne les identifiants de sélection, de métrique, de split et de calibration effectivement renseignés. `calibration_hash`, `basis_hash` et `config_hash` sont des empreintes de contenu : leur égalité éventuelle n'est pas en elle-même un partage de cohorte. Ne pas imposer leur inégalité ni modifier des empreintes pour la produire ; conserver la provenance exacte et vérifier les liens de cohorte par leurs identifiants.

**Rôles et portée.** Claude Code rédige les plans en max/xhigh ; Codex audite et conduit la clôture/intégration ; Mistral Vibe `large-4`, thinking `high`, est l'implémenteur désigné. L'étape actuelle reste **plans seulement** : ce GO n'est pas un GO d'exécution Vibe. L'ordre de planification reste 29 → 30 → 31, audits unitaires.

Le runner et les artefacts /2 restent inchangés ; aucune révision /3, simulation, recalibration, exécution full ou évaluation réelle post-2019 n'est autorisée par cette décision. Aucun résultat du futur assembleur de tableaux n'a encore été exécuté ou contrôlé.

Décision de référence : `prompts/GO-stream-29.md`. La proposition Claude ci-dessus est conservée textuellement ; seules les décisions de revue sont ajoutées ici.

### Avenant d'exécution Vibe — 2026-10-31

Nouvelle instruction directe du chercheur : **GO d'implémentation Mistral Vibe large-4, thinking high, pour le 29 jusqu'à résultats audités ; puis le 30 après finalisation du 29.** Le stream 31 est suspendu jusqu'à nouvel ordre. Le document `prompts/GO-stream-29-vibe.md` précise le périmètre et prime sur les anciennes mentions plan-only pour cette exécution Vibe. Les hypothèses, corrections de revue et invariants scientifiques ci-dessus restent applicables. Aucun full ni nouveau résultat réel post-2019 n'est autorisé.
