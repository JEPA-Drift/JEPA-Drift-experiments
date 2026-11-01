# Plan d'implémentation — stream 30 (PCA-FIGURE) : `Figure_1_mean` et `Figure_1_cov`

## 0. Statut, rôles, portée

- **Étape courante : plans seulement.** Claude Code a rédigé ce plan en lecture seule. Aucun fichier n'a été modifié, aucun test ni aucune simulation n'a été lancé.
- **Rôles** (`prompts/POLICY-PCA-PLAN-ONLY.md`) :
  - Claude Code rédige les plans.
  - Codex audite, enregistre `prompts/plans/plan-30.md` et `prompts/GO-stream-30.md`, puis conduit la clôture (réindexation, `make check` global, Git, synchronisation des prompts).
  - Mistral Vibe `large-4`, thinking `high`, implémente après un GO d'exécution, sans aucune mutation Git.
- **Ordre de planification :** 28 → 29 → 30 → 31. L'exécution du 30 dépend de l'implémentation du 29, qui n'existe pas encore (§3, porte G0).
- **Transparence de l'inspection.** Pour lire le schéma, j'ai consulté :
  - les lignes `selection.csv` à k = 20 de `B_cov_rotate30` (S, d, V) ;
  - les trois premières lignes préfixe E2 de `C_residual_mean` (I, M, V théoriques).

  Je n'ai lu **aucune valeur RMST ni FPR**. Le registre du §4 repose sur des critères théoriques (exactitude du KL gaussien), jamais sur l'allure de courbes.

---

## 1. Faits vérifiés (lecture seule, 2026-10-30/31)

| Fait | Source |
|---|---|
| Worktree `~/JEPA-stream-30`, branche `stream-30`, HEAD = `main` = `fc533d0`, arbre propre | `git status`, `git worktree list` |
| `experiments/figures/` est absent. `experiments/` n'a pas d'`__init__.py` (paquet d'espace de noms) ; chaque script fait `sys.path.insert(0, parents[1])` | `ls`, `grep` |
| `experiments/pca_drift_tables.py` est absent ici. Le worktree 29 ne contient que le plan, le GO et le NO-GO, non suivis | `ls`, `git -C ../JEPA-stream-29 status` |
| Les 7 SHA-256 de `smoke_predictive_v2_closeout/` égalent la liste du plan 29 §11.1. E2 vaut `e315e537…0823` sur disque et dans l'index. `configs/FROZEN.json` est absent | `sha256sum`, `git show :` |
| Lignes préfixe E2 (`BASELINE_PREFIX`) : `objective_kind` NONE, `cost_kind` NONE, mais `M_cost`, `I_objective` et `V_mix` sont renseignés. `info_kind` vaut `MEAN_GAUSS_PLUGIN_LW` en moyenne gaussienne. V(P_k) = I/M(k) est donc disponible dans la source | `selection.csv` |
| Covariance B30 gaussienne : `COV_JOINT_ORACLE`, E2, SELECTED existe pour `COV_JOINT_AFFINE_SURROGATE` et pour `COV_JOINT_MIX_HEURISTIC`. `info_kind` vaut `COV_GAUSS_POP_JOINT_EXACT` ; `claim_flag` contient `COV_SURROGATE_EXPLORATORY`, `HEURISTIC_COST` (MIX) et `ORACLE_TRUE_SIGMA1` | `selection.csv` |
| Énergie : `ENERGY_INDEX_COMPARATOR` / `ENERGY_INCREASE_CUSUM`, avec k, S et d à NA. Les lignes E1 et E3 partagent un `metric_id` | `selection.csv` |
| Manifest : H = 250, N = 239, T_fit = 1000, nmax = 20, α = 0,05, γ_M = 504, ρ = 0,4. Smoke à 40 par rôle (2000 prévus en full). `claims` = « none: smoke counts of 40 per role ». Scénarios `B_cov_rotate30.theta_deg = 30.0`, `C_residual_mean.I_target = 3.0` et `axes` | `manifest.json` |
| Colonnes d'agrégats : `rmst, rmst_lo, rmst_hi, ci_kind, fpr, fpr_lo, fpr_hi, target_fpr, n, H, time_origin, det_rate, censored_share, null_metric_id` | en-tête `aggregates.csv` |
| `.venv` : matplotlib 3.11.2, pandas 3.0.6, numpy 2.4.4. Motif existant `_save(...)` avec `metadata={"CreationDate": None}` (e1, e3, e10, audit) | `site-packages`, `grep` |
| `save_fair_csv(df, path)` = `df.to_csv(path, float_format='%.17g', na_rep='NaN', lineterminator='\n', index=False)`. Elle accepte un tampon texte | `jepadrift/pipelines.py:67` |
| `make check` exécute pyflakes sur `find jepadrift experiments tests tools -name '*.py'`, ce qui couvre `experiments/figures/` | `Makefile:25` |
| `pdftotext`, `pdftoppm`, `pdfinfo` et `rsvg-convert` sont dans le PATH (binaires de l'environnement conda, aucun Python de Trading) | `which` |
| Les entrées `C-pca-*` de `docs/DEVIATIONS.md` sont rédigées en français | `grep` |

---

## 2. Hypothèses explicites et défauts

| Id | Défaut retenu |
|---|---|
| H1 | **Dépendance au 29.** L'exécution exige le 29 intégré sur `main` et `stream-30` rebasé dessus. Le contrat consommé est `pca_drift_tables/1`, tel que l'écrit `docs/sections/pca_drift_tables.md`. Une colonne attendue absente donne le refus `TABLE_CONTRACT_MISMATCH` et un retour à Codex, sans contournement ni reconstruction des jointures. |
| H2 | **Entrées et sorties.** `--input-dir` est obligatoire. `--tables-dir` est **ajouté**, avec pour défaut `results/pca_drift_benchmark/tables/<basename(input-dir)>/` (défaut H1 du 29). `--output-dir` vaut par défaut `results/pca_drift_benchmark/figures/<basename(input-dir)>/`. La racine `results/pca_drift_benchmark/figures/Figure_1_*` du prompt est réservée au run full : les figures smoke ne s'y écrivent jamais. |
| H3 | **Registre prédéclaré** (§4), en trois entrées : `mean` et `cov` (PRIMARY, fond gaussien) et `mean_t7` (ROBUSTNESS). Le fond gaussien est choisi parce que les KL gaussiens y sont exacts relativement à la covariance génératrice. `cov_t7` n'est pas produit, car il n'est pas demandé ; si Codex le veut, il suffit d'une ligne de registre. |
| H4 | **Rôle des options CLI.** `--dataset-id`, `--event-id`, `--detector-family`, `--objective-kind` et `--cohort-id` sont validées contre `pdb.ENUMS`, puis servent de **sélecteurs dans le registre**. Une combinaison hors registre donne `NOT_PREDECLARED` (exit 2). `D3_239`, ou toute valeur de `--cohort-id`, donne `REAL_FIGURE_NOT_EXECUTED_SCHEMA_2` (exit 2). Le schéma /2 ne contient aucune mesure réelle exécutée, et aucune figure vide n'est fabriquée. |
| H5 | **Axe droit de la covariance** : V_cov = I_cov_joint/M, objectif `COV_JOINT_MIX_HEURISTIC`, préfixe et S*_k lus dans `V_mix`. **Tout l'axe droit** porte `EXPLORATORY HEURISTIC: mean-mixture M is not a covariance detector cost`. Σq^cov n'est jamais tracé. L'option « courbe I_cov_joint sans V » est écartée ; si Codex la préfère, le changement tient en une ligne de registre. |
| H6 | **Incertitude** : intervalles marginaux du producteur (`rmst_lo/hi`, `NORMAL_DEFF1`, deff = 1 ; Wilson pour le FPR). Le schéma /2 n'exporte **aucune incertitude appariée**, et la recalculer depuis `trials.csv` serait une nouvelle statistique, hors du périmètre. La légende le dit. |
| H7 | **Critère de comparabilité FPR** (§6.3) : identité du protocole (P) et chevauchement des intervalles de Wilson (W). Il est calculé par le code et n'est jamais affirmé à la main. |
| H8 | **Axes.** Gauche : [0, 100] %, le domaine d'une part de variance, ce qui ne masque aucune valeur. Droite : [0, max] (V ≥ 0 par construction). Bas : [min(0, min lo), max(250, max hi)] plus une marge. Aucune borne ne tronque une valeur ou un intervalle ; un test le vérifie. |
| H9 | **Langues.** Figures, légendes, `FIGURE_CHECK.md`, `docs/sections/pca_drift_figures.md` et wrapup en anglais : le prompt fixe des libellés anglais, et l'article est en anglais. L'entrée de `DEVIATIONS` est en français, comme les `C-pca-*`. |
| H10 | **`--strict`** ajoute trois contrôles : (i) le recalcul `pdb.identity_block(config, inputs) == manifest.identity` ; (ii) `table_manifest.strict == true` ; (iii) l'égalité entre les SHA-256 courants du runner et de `pca_drift_tables.py` et ceux de `table_manifest.code`. Sans `--strict`, tous les contrôles d'intégrité du §5 restent bloquants. |
| H11 | **Inspection visuelle.** Elle n'est jamais écrite dans un fichier déterministe. `FIGURE_CHECK.md` contient les contrôles automatiques en processus et liste les commandes externes à lancer. Les résultats de ces commandes et l'inspection humaine ou agent vont dans `logs/pca_drift_figures/` et dans le wrapup, avec le SHA-256 du PNG inspecté. Aucune inspection n'est déclarée sans exécution. |
| H12 | **Police et version.** DejaVu Sans, livrée avec matplotlib, sans téléchargement. Le manifest enregistre la version de matplotlib et le nom de base et le SHA-256 du fichier de police (aucun chemin absolu). |
| H13 | **Format** : 3,5 × 5,4 in (colonne simple, 1050 × 1620 px à 300 dpi), police de base 7 pt, minimum 6 pt. Le rendu est vectoriel en double colonne. |
| H14 | **Mode smoke.** La bannière `SMOKE_NO_CLAIMS` figure sur chaque page, dans chaque légende et dans chaque enregistrement du manifest. |

---

## 3. Dépendance au 29 et porte G0

Le 30 consomme les sorties du 29, dans cette chaîne : octets runner → (SHA) → `table_manifest.json` → (SHA) → tableaux → figure. Il ne refait aucune jointure métier : chaque cellule tracée se résout par `table_lineage.csv`, ce qui suit le conseil stratégique du plan 29.

Éléments réutilisés :
- de `experiments.pca_drift_tables as pdt` : `verify_output_dir(path)` (nommée au plan 29 §7) et le lecteur CSV typé documenté par le contrat. Si le contrat n'exporte pas de lecteur, une fonction locale `_read(path)` applique **mot pour mot** les règles du plan 29 §3.1 (`round_trip`, identifiants en `str`, `k`/`d` en `Int64`), et l'écart est déclaré ;
- de `experiments.pca_drift_benchmark as pdb` : `check_env`, `ENUMS`, `SCHEMA_VERSION`, `file_sha256`, `_rel`, `sha16`, `canon`, `identity_block`. `pdb` est importé **avant** numpy et matplotlib, pour que ses `setdefault` d'environnement s'appliquent.

**Porte G0**, avant toute ligne de code. Un échec arrête Vibe, qui rend compte à Codex :
1. `git merge-base --is-ancestor <SHA_29> HEAD`. Le SHA d'intégration du 29 est fourni par Codex dans le GO-30.
2. `experiments/pca_drift_tables.py` et `docs/sections/pca_drift_tables.md` existent.
3. `pdt.verify_output_dir(results/pca_drift_benchmark/tables/smoke_predictive_v2_closeout)` est vrai. Si le répertoire est absent, c'est un blocage : Vibe ne le produit pas, car c'est un livrable du 29.
4. Les colonnes du §6.1 sont présentes dans `Tableau_PCA_1/2/3.csv` et dans `table_lineage.csv`.

---

## 4. Registre prédéclaré (constante de module `SPECS`, figée avant toute lecture de résultat)

| clé | rôle | `dataset_id` | `event_id` | famille | objectif S*_k | comparateur | stem | étiquettes |
|---|---|---|---|---|---|---|---|---|
| `mean` | PRIMARY | SYNTH_GAUSS_EQUICORR | C_residual_mean | MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM | MEAN_MIX_FLUID_SURROGATE (`ORACLE_Q_MIX`) | — | `Figure_1_mean` | `GAUSSIAN_PROXY` (q plug-in LW) |
| `mean_t7` | ROBUSTNESS | SYNTH_T7_EQUICORR | C_residual_mean | idem | idem | — | `Figure_1_mean_t7` | `GAUSSIAN_PROXY`, `T7_ROBUSTNESS` |
| `cov` | PRIMARY | SYNTH_GAUSS_EQUICORR | B_cov_rotate30 | COV_QUADRATIC_VECH_SCAN | COV_JOINT_MIX_HEURISTIC (`COV_JOINT_ORACLE`) | `ENERGY_INDEX_COMPARATOR` / ENERGY_INCREASE_CUSUM | `Figure_1_cov` | `COV_SURROGATE_EXPLORATORY`, `EXPLORATORY_HEURISTIC` |

- Le `cohort_id` est NA dans toutes les entrées. `--figure both` est le défaut et produit les trois entrées ; `--figure mean` produit `mean` et `mean_t7`.
- Moyenne et covariance ne partagent jamais une figure ni une courbe. Le t7 n'est jamais superposé au gaussien.

---

## 5. Chaîne de validation et codes de refus

Toute la validation se fait en mémoire, avant la création d'un répertoire. Un refus donne exit 2, sans aucun fichier écrit.

| Code | Contrôle |
|---|---|
| `ENV_INVALID` | `pdb.check_env()` |
| `INPUT_INVALID` | `manifest.json` et les quatre CSV lus (`spectra.csv`, `selection.csv`, `aggregates.csv`, `calibration.csv`) : présents ; SHA-256 des CSV vérifiés contre `manifest.outputs` ; SHA-256 du manifest vérifié contre `table_manifest.input` (`TABLES_STALE`) ; `schema_version == pdb.SCHEMA_VERSION == "pca_drift_benchmark/2"`, `run_fingerprint == sha256(canon(identity))`. `trials.csv` n'est pas lu par la figure (sa présence a été exigée et contrôlée par le 29). |
| `TABLES_INCOMPLETE` | `pdt.verify_output_dir(tables_dir)` est faux |
| `TABLES_STALE` | `table_manifest.input.run_fingerprint` ≠ celui du manifest runner, ou SHA d'une source lue ≠ `table_manifest.input`, ou `tables_schema` ≠ `pca_drift_tables/1` |
| `TABLE_CONTRACT_MISMATCH` | Colonne attendue absente (§6.1) |
| `TABLES_NOT_STRICT`, `IDENTITY_STRICT_FAILED`, `CODE_DRIFT` | `--strict` seulement (H10) |
| `NOT_PREDECLARED`, `REAL_FIGURE_NOT_EXECUTED_SCHEMA_2` | H4 |
| `BLOCK_MISSING` | Bloc T1, bloc T2 (clé + objectif) ou ligne (C) de T3 absent pour l'entrée du registre |
| `K_DOMAIN` | L'ensemble des k d'un bloc T1 ou T2 ≠ {1..20} |
| `PREFIX_IDENTITY_FAILED` | Pour tout k : `T2.metric_id_prefix == T1.metric_id`, `T2.null_metric_id_prefix == T1.null_metric_id`, et cellules RMST/FPR préfixe de T2 **textuellement identiques** à T1 (même artefact, aucune comparaison arrondie) |
| `LINEAGE_UNRESOLVED`, `SOURCE_MISMATCH` | Chaque cellule tracée a une ligne de lignée de type `SOURCE`, qui se résout dans le fichier runner (clé primaire JSON) ; la valeur runner est égale bit à bit à la cellule du tableau. Une cellule `FORMULA` ou `RULE` n'est jamais tracée. |
| `HORIZON_INCOMPATIBLE` | `H == 250` pour chaque agrégat et chaque calibration référencés ; `time_origin == ONSET_ALIGNED` pour chaque ALT_RMST |
| `SERIES_PROTOCOL_MISMATCH` | Dans une série, protocole non constant sur k (§6.3, P) |
| `V_NOT_COMPARABLE` | Les deux séries V n'ont pas le même `info_kind` ou n'utilisent pas la même fonction de coût M avec le même `gamma_M`. Pour chaque ligne, vérifier `M_cost == manifest.costs["M"][d - 1]` à sa propre dimension (`d = k` pour le préfixe, `d = d_star` pour la sélection), sans recalculer V. L'égalité numérique entre M(k) et M(d_star) n'est pas exigée ; le `cost_kind` NONE du préfixe reste légitime. Pour une entrée prédéclarée, c'est un refus, jamais un rendu dégradé. |
| `EMPTY_SERIES` | Une série tracée n'a aucun point fini : aucune figure vide n'est fabriquée |
| `OUTPUT_NOT_EMPTY` | Le répertoire de sortie existe et n'est pas vide (le script ne supprime jamais rien) |

L'égalité exacte des flottants est légitime ici, puisqu'elle compare des objets du **même artefact** (texte `%.17g`). Elle n'est jamais appliquée à un agrégat recalculé (NO-GO (h) de la mission 12).

---

## 6. Construction des séries

### 6.1 Sources par série (lues par `table_lineage.csv`, contrôlées dans le runner)

| Série | Panneau | Cellule de tableau | Source runner |
|---|---|---|---|
| `CPV` | haut, gauche | T1 `cpv_lw` (k = 1..20) | `spectra.cpv_lw` (part cumulée de la trace LW complète, N axes) |
| `V_prefix` | haut, droite | T2 `V_prefix` | `selection.V_mix`, ligne préfixe E2 |
| `V_selected` | haut, droite | T2 `V_star` | `selection.V_mix`, ligne SELECTED de l'objectif |
| `RMST_prefix` (± IC) | bas | T1 `rmst, rmst_lo, rmst_hi` | `aggregates`, ALT_RMST [`metric_id`] |
| `RMST_selected` (± IC) | bas | T2 `rmst_selected`, IC | `aggregates`, ALT_RMST [`metric_id_subset`] |
| `FPR_prefix`, `FPR_selected` | texte, bas | T1 `fpr_test_null, fpr_lo, fpr_hi` ; T2 `fpr_selected`, Wilson | `aggregates`, HOLDOUT [`null_metric_id`] |
| `RMST_energy`, `FPR_energy` (cov) | bas | T3, ligne (C) | `aggregates` (une valeur, k NA) |
| protocole | — | — | `calibration` [`null_calibration_id` de l'agrégat] : `threshold_rule, alpha, n_cal, alarm_rule, guarantee_basis, H` |

Les noms exacts des suffixes d'intervalle de T2 sont ceux du contrat 29. Ils figurent dans une constante de module, vérifiée par la porte G0.

### 6.2 Points manquants

- Une cellule NA reste NaN : la ligne est interrompue, sans interpolation, lissage ni extrapolation.
- Un marqueur « × » est placé sur le bord inférieur de l'axe concerné, avec une entrée de légende.
- La légende textuelle classe chaque k manquant :
  - **bloqué ou impossible** : `UNSUPPORTED, BLOCKED_*, NOT_EVALUABLE_STANDARD_SPLIT, DATA_UNAVAILABLE, CPV90_OUTSIDE_TOP20` ;
  - **mesure absente** : `CALIBRATION_FAILED, PATH_TOO_SHORT`.

### 6.3 Comparabilité FPR (H7)

- **(P) protocole** : égalité de (`detector_family, null_id, threshold_rule, alpha, n_cal, n` (holdout)`, H, alarm_rule, guarantee_basis, time_origin`).
  - Exigée **dans** chaque série, sur tous les k ; sinon `SERIES_PROTOCOL_MISMATCH`.
  - Exigée **entre** préfixe et sélection au même k.
- **(W)** : chevauchement des intervalles de Wilson, `max(lo_a, lo_b) ≤ min(hi_a, hi_b)`.
- Un k est comparable si et seulement si P et W tiennent. Sinon :
  - le marqueur `FPR mismatch` est posé à ce k ;
  - la liste des k figure dans la légende textuelle ;
  - une phrase est ajoutée : « RMST differences at these k are not interpretable as speed differences at equal false-alarm rate ».
- La légende précise que W est un **filtre descriptif**, et non un test d'égalité (faible puissance à n = 40).
- **Énergie contre scan vech** : P échoue par construction (famille différente). L'étiquette `DETECTOR_FAMILY_MISMATCH` est permanente, avec la phrase « not an apples-to-apples test of two equally general detectors ».
- Chaque courbe affiche son intervalle de FPR250 (min–max sur k, plus les bornes de Wilson) dans un petit texte sous le panneau bas et dans la légende textuelle.

---

## 7. Rendu (matplotlib, Agg, `matplotlib.rc_context`)

**Mise en page.**
- Deux panneaux empilés, x partagé, `constrained_layout`.
- `xlim` [0,5 ; 20,5], ticks {1, 2, 5, 10, 15, 20}.
- Libellé x : « k (reservoir P_k = PCA axes 1..k, frozen LW basis) ».

**Panneau haut.**
- Gauche : CPV en bleu `#0072B2`, trait plein, marqueur `o`, ticks en %, ticks et libellé en bleu. Libellé : « CPV_k (% of total LW variance, all N axes) ».
- Ligne fine à 90 %, toujours dans [0, 100].
- **Annotation conditionnelle unique**, générée par le code :
  - s'il existe k ≤ 20 avec `cpv_lw ≥ 0,9`, « CPV ≥ 90 % at k = ⟨premier k⟩ », avec contrôle de cohérence contre `cpv90_k_full` ;
  - sinon, si `cpv90_status == CPV90_OUTSIDE_TOP20`, la note « CPV90 not reached within top 20 (k90_full = ⟨valeur⟩) ».
- Droite (gris foncé) :
  - `V_prefix` en rouge `#D55E00`, tirets, marqueur `s` ;
  - `V_selected` en vert `#009E73`, trait plein, marqueur `^`.
  - Libellé moyenne : « V = I_plugin/M(d, γ) (nats/day), GAUSSIAN_PROXY ».
  - Libellé covariance : « EXPLORATORY HEURISTIC / V_cov = I_cov_joint/M(d, γ) », avec la phrase complète du H5 encadrée sur la zone de l'axe droit.
  - La légende de ces deux courbes contient « model-based, not observed detection speed ».

**Panneau bas.**
- `RMST_prefix` en rouge tirets `s` et `RMST_selected` en vert plein `^`, avec barres d'erreur exactes `rmst_lo/hi`.
- Covariance : `RMST_energy` en noir, tiret-point, ligne horizontale avec bande d'IC grise. Libellé : « ENERGY_INCREASE_CUSUM (equal-weight index, one-sided increase; no PCA axes; constant in k) ».
- Ligne pointillée « H = 250 (censoring cap) ».
- Libellé y : « RMST250 (days) = mean[min(T, 250)] ».

**Bandeaux.**
- Titre : « Figure 1 (mean|cov): ⟨event⟩, ⟨dataset⟩ ».
- Ligne d'étiquettes : `SMOKE_NO_CLAIMS`, `GAUSSIAN_PROXY` / `T7_ROBUSTNESS`, ou `COV_SURROGATE_EXPLORATORY`. Cette dernière n'apparaît **que** sur la covariance.
- Les légendes sont **hors des axes**, sous chaque panneau.

**Aucune autre annotation numérique.** Pas de pic, de plateau, de plancher, de « ≈ », ni de mot comparatif (`faster`, `outperform`, `superior`, `collapse`, `explode`).

**Niveaux de gris.** Chaque série a un couple (style de trait, marqueur) unique, ce que vérifie un test.

**Déterminisme.**
- `svg.hashsalt` fixe, `font.family = DejaVu Sans`, `pdf.fonttype = 42`, `svg.fonttype = path` (le texte reste interrogeable par les commentaires SVG).
- `savefig` avec `metadata` : PDF `{"CreationDate": None, "Keywords": tags}`, SVG `{"Date": None, "Keywords": tags}`, PNG `{"Keywords": tags}` à 300 dpi.
- Les trois formats sont enregistrés depuis **le même objet `Figure`**.

**Dessin depuis le CSV.**
1. Le cadre source est d'abord sérialisé par `save_fair_csv(frame, io.StringIO())`.
2. Ce texte est relu avec `float_precision="round_trip"`.
3. Le rendu se fait **uniquement** depuis ce cadre relu, avec, comme métadonnées, des chaînes issues du manifest.
4. Les mêmes octets texte sont écrits sur disque.

**Contrôles de rendu en processus**, consignés dans `FIGURE_CHECK.md` :
- toute étendue de `Text` visible est dans le cadre de la figure (aucune coupure) ;
- les légendes et bandeaux sont disjoints des zones de tracé ;
- la police est d'au moins 6 pt ;
- les limites y contiennent toutes les valeurs et tous les intervalles ;
- le PNG mesure 1050 × 1620 px ;
- les chaînes obligatoires sont présentes dans les commentaires SVG.

---

## 8. Sorties

Pour chacune des trois entrées du registre, dans `<OUT>/` :

1. `⟨stem⟩.svg`, `⟨stem⟩.pdf` et `⟨stem⟩.png`.
2. `⟨stem⟩_source.csv`, en format long, avec **seulement** les valeurs tracées et leurs pointeurs : `figure_key, panel, series, k, y, y_lo, y_hi, null_fpr, null_fpr_lo, null_fpr_hi, status, metric_id, null_metric_id, table, row_id, source_key`. L'énergie tient en une ligne à k NA ; les marqueurs `FPR_MISMATCH` et « non mesuré » ont `y` à NA.
3. `⟨stem⟩_caption.md` (anglais), générée depuis le manifest et le CSV source :
   - dataset, N, T_fit, H et loi (Σ0 équicorrélée ρ ; t7 avec un χ²₇ par jour) ;
   - définition du changement (C : `I_target` et axes ; B : `theta_deg` entre les axes 1 et 2) ;
   - réservoir k, domaine d'information (proxy plug-in LW ; KL joint exact relativement à la covariance génératrice sur fond gaussien, proxy en t7), famille et définition du détecteur ;
   - calibration (`predictive_exchangeable_rank_v2`, n_cal, r, borne (r+1)/(n_cal+1), distincte du FPR holdout observé) ;
   - effectifs (smoke 40 ; full 2000 prévus, non exécutés) ;
   - FPR250 par série, IC RMST (`NORMAL_DEFF1`, non tronqués), absence d'incertitude appariée ;
   - drapeaux oracle (`ORACLE_INJECTED_DELTA` / `ORACLE_TRUE_SIGMA1` : borne diagnostique, non ex ante) ;
   - phrase : « the 250-day cap is a natural axis limit, not evidence that a series reaches it » ;
   - trois sections séparées : *Measured (this run)*, *Model-based (not tested here)*, *Status and limits*.
4. `FIGURE_CHECK.md`, un seul fichier :
   - SHA-256 des sources runner et des fichiers de tableaux lus, `run_fingerprint`, `tables_fingerprint` ;
   - compteurs par série, k manquants et leur classe, résultats PASS/FAIL des §5 à §7 ;
   - ligne `strict checks: PASS | NOT RUN` ;
   - section « External render checks » : commandes à lancer, dont les résultats sont enregistrés dans `logs/` et le wrapup (H11).
5. `figure_manifest.json`, écrit **en dernier** via `.partial` puis `os.replace` :
   - `figures_schema = "pca_drift_figures/1"` ;
   - `input` et `tables` (chemins relatifs via `pdb._rel`, empreintes, SHA) ;
   - `code` (SHA de `plot_figure_1.py`, `pca_drift_tables.py`, runner) ;
   - `environment` (versions, police H12, les cinq variables, backend) ;
   - `filters`, `strict`, `command` (gabarit avec `<OUT>`, jamais `argv`) ;
   - `records` {`mean`, `cov`, `mean_t7`}, chacun avec `role`, `spec`, `predeclared: true`, `tags`, `claim_flags`, `fpr_mismatch_k`, `missing_k`, `outputs` ;
   - `outputs` global ;
   - `figures_fingerprint = sha256(canon({figures_schema, input, tables, code, environment, filters, strict}))`.

**Complétude** (même protocole que le 29). Une sortie est complète si et seulement si `figure_manifest.json` existe et que chaque fichier listé a son SHA-256. La fonction locale `verify_figures_dir(path)` applique cette définition. Une erreur d'E/S donne exit 3, « output incomplete (no figure_manifest.json) ». Une réinvocation sur un répertoire non vide donne exit 2.

---

## 9. CLI et codes de sortie

`experiments/figures/plot_figure_1.py` :
- `--input-dir DIR` (obligatoire) ;
- `--tables-dir DIR` (H2) ;
- `--output-dir DIR` ;
- `--figure mean|cov|both` (défaut `both`) ;
- `--dataset-id`, `--event-id`, `--cohort-id`, `--detector-family`, `--objective-kind` (H4) ;
- `--strict`.

Structure : argparse et `if __name__ == "__main__":`. L'en-tête fait `sys.path.insert(0, parents[2])` et n'ajoute pas d'`__init__.py`.

Codes : 0 succès ; 2 refus (§5, usage) ; 3 écriture incomplète.

---

## 10. Tests — `tests/test_plot_figure_1.py` (TDD, RED puis GREEN consignés)

**Fixtures** générées par la suite, aucune ne mimant les formes attendues :
- **(a) Fixture minuscule en mémoire** : cadres source à k = 1..20 aux valeurs neutres et déterministes. CPV linéaire de 20 % à 60 %, V linéaire croissant, RMST constant à 100 ± 5, un NaN à k = 6. Elle sert aux tests de rendu et de conditionnels.
- **(b) Fixture d'intégration** : `pdt` est lancé une fois par module sur l'artefact smoke suivi, vers `tmp_path`. La figure est ensuite produite vers `tmp_path`. Le runner n'est jamais lancé et aucune donnée réelle n'est lue.

Durée visée : moins de 40 s.

| Groupe | Tests positifs | Tests négatifs |
|---|---|---|
| g1 chaîne | (b) est acceptée ; trois enregistrements ; chaque point du CSV source égale la cellule runner résolue par `metric_id` ou clé primaire, à l'égalité exacte ; k = 1..20 sur chaque série k ; `verify_figures_dir` vrai | octet ajouté à une copie de `Tableau_PCA_2.csv` → `TABLES_INCOMPLETE` ; source runner copiée et altérée → `INPUT_INVALID`/`TABLES_STALE` ; `metric_id_prefix` altéré en mémoire → `PREFIX_IDENTITY_FAILED` ; RMST préfixe T2 décalé d'un ULP → `PREFIX_IDENTITY_FAILED` ; agrégat runner altéré → `SOURCE_MISMATCH` ; cellule tracée de type FORMULA → refus ; H = 200 → `HORIZON_INCOMPATIBLE` ; `n_cal` modifié à un k → `SERIES_PROTOCOL_MISMATCH` ; `info_kind` du préfixe modifié → `V_NOT_COMPARABLE` ; toute la série RMST sélection à NA → `EMPTY_SERIES`, sans répertoire créé |
| g2 CLI | `--figure mean` produit `mean` et `mean_t7` ; options égales au registre acceptées ; `--strict` passe sur (b) | `--event-id A_market_mean` → `NOT_PREDECLARED` ; `--dataset-id D3_239`, `--cohort-id cohort_retrospective_covid` → `REAL_FIGURE_NOT_EXECUTED_SCHEMA_2` ; valeur hors énumération → exit 2 ; tableaux non stricts sous `--strict` → `TABLES_NOT_STRICT` |
| g3 conditionnels | (a) avec un franchissement à k = 7 : annotation « k = 7 », cohérente avec `cpv90_k_full` ; sans franchissement : note OUTSIDE et aucune annotation de franchissement ; Wilson disjoints à k = 3 → marqueur et phrase `FPR mismatch` ; Wilson chevauchants → aucun marqueur | balayage de tous les `Text` et des légendes textuelles : aucune expression interdite (`peak`, `plateau`, `floor`, `≈`, `faster`, `outperform`, `superior`, `collapse`, `explod`) ; aucun « k = n » qui ne vienne pas du conditionnel |
| g4 rendu | NaN conservé dans le `Line2D` à k = 6, marqueur « × » présent, classe dans la légende ; limites y contenant tous les IC ; aucune coupure ; légendes hors des axes ; police ≥ 6 pt ; couples (trait, marqueur) uniques ; PNG 1050 × 1620 ; couleurs bleu, rouge, vert des séries | `COV_SURROGATE_EXPLORATORY` et la phrase complète du H5 sont présents dans le SVG, la légende, l'enregistrement et les métadonnées PDF/SVG de `cov`, et **absents** de `mean` et `mean_t7` ; `DETECTOR_FAMILY_MISMATCH` présent sur `cov` |
| g5 écriture | deux exécutions vers deux répertoires donnent des fichiers identiques octet pour octet (SVG, PDF, PNG, CSV, MD, manifest) et le même `figures_fingerprint` ; le rendu depuis `read_csv(source_csv)` redonne les mêmes octets ; aucun `/home/` | sortie non vide → exit 2 ; `OSError` simulée après le premier fichier → exit 3, sans manifest, `verify_figures_dir` faux, réinvocation → exit 2 |

---

## 11. Livrables, documentation, écarts

**Livrables Vibe :**
- `experiments/figures/plot_figure_1.py` et `tests/test_plot_figure_1.py` ;
- `docs/sections/pca_drift_figures.md` (anglais, court) : registre, sources, codes de refus, complétude, commande ;
- `docs/DEVIATIONS.md`, **ajout seulement**, entrée française `C-pca-figures-design`. Elle couvre H2 à H8, H10, H11, le chemin `results/…/figures/` à la place de `figures/<stream>/` (imposé par le prompt, SVG en plus) et l'option `--tables-dir` ;
- `prompts/wrapups/wrapup-30.md` (anglais, six rubriques, SHA-256 des sorties, résultats des contrôles externes et de l'inspection visuelle réellement exécutés) ;
- 17 sorties dans `results/pca_drift_benchmark/figures/smoke_predictive_v2_closeout/` : 3 stems × 5 fichiers, plus `FIGURE_CHECK.md` et `figure_manifest.json`.

**Non touchés :**
- le runner, `pca_drift_tables.py`, les tableaux et les artefacts `smoke*` ;
- `configs/`, `tools/`, `prompts/streams/` et le master ;
- `results/e2` et `results/e3` ;
- les fichiers de Codex.

---

## 12. Séquence d'exécution

### 12.1 Phase Vibe, après le GO d'exécution, sans mutation Git

```bash
set -euo pipefail
cd ~/JEPA-stream-30
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
export PATH="$PWD/.venv/bin:$PATH"
PY="$PWD/.venv/bin/python"; L=logs/pca_drift_figures; R=results/pca_drift_benchmark
IN=$R/smoke_predictive_v2_closeout; TB=$R/tables/smoke_predictive_v2_closeout; OUT=$R/figures/smoke_predictive_v2_closeout
mkdir -p "$L"
# G0
test "$(git rev-parse --abbrev-ref HEAD)" = stream-30
git merge-base --is-ancestor "$SHA_29" HEAD                       # SHA_29 fourni par Codex dans le GO-30
test -f experiments/pca_drift_tables.py && test -f docs/sections/pca_drift_tables.md
"$PY" -c 'import sys; sys.path.insert(0, "."); from experiments import pca_drift_tables as t; sys.exit(0 if t.verify_output_dir(sys.argv[1]) else 1)' "$TB"
git status --porcelain=v1 --untracked-files=all | LC_ALL=C sort > "$L/status_before.txt"
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
test ! -e configs/FROZEN.json && test ! -e "$OUT"
# TDD (RED puis GREEN dans $L/tdd.log)
"$PY" -m pytest -q tests/test_plot_figure_1.py
"$PY" -m pyflakes experiments/figures/plot_figure_1.py tests/test_plot_figure_1.py
# double rendu
"$PY" experiments/figures/plot_figure_1.py --input-dir "$IN" --tables-dir "$TB" --output-dir "$OUT" --strict > "$L/run.log" 2>&1
test ! -e "$L/repeat"
"$PY" experiments/figures/plot_figure_1.py --input-dir "$IN" --tables-dir "$TB" --output-dir "$L/repeat" --strict > "$L/repeat.log" 2>&1
test "$(ls -A "$OUT" | wc -l)" -eq 17
for f in $(ls -A "$OUT"); do cmp -- "$OUT/$f" "$L/repeat/$f"; done
rc=0; "$PY" experiments/figures/plot_figure_1.py --input-dir "$IN" --tables-dir "$TB" --output-dir "$OUT" > "$L/refusal.log" 2>&1 || rc=$?
test "$rc" -eq 2
if grep -rlaF "/home/" "$OUT"; then exit 1; fi
# contrôles de rendu externes (H11), consignés dans $L/render_qc.md
for s in Figure_1_mean Figure_1_mean_t7 Figure_1_cov; do
  pdftotext "$OUT/$s.pdf" - > "$L/$s.pdf.txt"; pdfinfo "$OUT/$s.pdf" > "$L/$s.pdfinfo.txt"
  grep -qF "RMST250" "$L/$s.pdf.txt"; grep -qF "model-based, not observed detection speed" "$L/$s.pdf.txt"
  pdftoppm -r 100 -png "$OUT/$s.pdf" "$L/$s.pdf_preview"; rsvg-convert -o "$L/$s.svg_preview.png" "$OUT/$s.svg"
done
grep -qF "COV_SURROGATE_EXPLORATORY" "$L/Figure_1_cov.pdf.txt"
if grep -qF "COV_SURROGATE_EXPLORATORY" "$L/Figure_1_mean.pdf.txt" "$L/Figure_1_mean_t7.pdf.txt"; then exit 1; fi
# invariants et état Git
cmp <(git show HEAD:docs/DEVIATIONS.md) <(head -c "$(git cat-file -s HEAD:docs/DEVIATIONS.md)" docs/DEVIATIONS.md)
git diff --quiet HEAD -- experiments/pca_drift_benchmark.py experiments/pca_drift_tables.py configs tools prompts/streams results/e2 results/e3 "$IN" "$TB"
git status --porcelain=v1 --untracked-files=all | LC_ALL=C sort > "$L/status_after.txt"
comm -23 "$L/status_before.txt" "$L/status_after.txt" | { ! grep -q .; }
{ printf '%s\n' ' M docs/DEVIATIONS.md' '?? docs/sections/pca_drift_figures.md' '?? experiments/figures/plot_figure_1.py' \
    '?? prompts/wrapups/wrapup-30.md' '?? tests/test_plot_figure_1.py'
  for f in $(ls -A "$OUT"); do printf '?? %s/%s\n' "$OUT" "$f"; done; } | LC_ALL=C sort > "$L/allowlist.txt"
comm -13 "$L/status_before.txt" "$L/status_after.txt" | cmp - "$L/allowlist.txt"
```

**Inspection visuelle.** Vibe examine les aperçus de `$L` et le PNG si son outillage le permet. Sinon, il écrit « visual inspection NOT PERFORMED » dans le wrapup, et Codex ou le chercheur l'exécute en citant le SHA-256 du PNG.

**Remise à Codex :** wrapup-30, journaux (ignorés par Git, jamais stagés), liste des livrables avec leurs SHA-256.

### 12.2 Phase Codex (spécification)

1. Réindexation (`tools/reindex_graphify_jcodemunch.sh`) et `make check` avec le PATH épinglé du plan 29 §11.2.
2. Staging par chemins explicites, sans journal ni `-f`.
3. Revue de `git diff --staged` : aucun fichier de plus de 50 Mo, aucun chemin EUROFIDAI.
4. Commit Conventional sans trailer, puis push selon le protocole du dépôt.
5. `tools/check_prompts.py --sync-master` après les intégrations (mission 12 §5).

---

## 13. Points de vigilance

- **Couplage au 29.** Une évolution du contrat `pca_drift_tables/1` (colonnes, `row_id`, lignée) impose un ré-audit du 30 ; `TABLE_CONTRACT_MISMATCH` la rend visible.
- **Lecture des figures smoke.** n = 40 et trajectoires partagées : aucune conclusion sur RMST ni FPR. Une figure plate ou contraire à l'hypothèse est un résultat publiable tel quel. Les formes du document source (CPV de 35 % à 95 %, k = 14, pic à k = 2, environ 12 jours, 250 à k = 20) ne figurent ni dans le code, ni dans les tests, ni dans les légendes.
- **Énergie sur B30.** La définition unilatérale (hausse de variance de l'indice) est énoncée, mais aucune phrase de « cécité » n'est générée sans conditionnel testé.
- **Oracle.** S*_k utilise Δ injecté (moyenne) ou Σ1 vrai (covariance). C'est une borne diagnostique, jamais une méthode ex ante, et la légende le répète.
- **pandas 3 et pyarrow.** Les identifiants doivent être typés `str`. Un flottant dans une colonne `object` casserait l'identité textuelle (plan 29 §12).

**[Strategic Advice]**
- Exporter dans un futur schéma producteur (/3, avec un nouveau plan) la différence appariée RMST(préfixe) − RMST(S*) par réplicat. C'est la seule incertitude qui rend la comparaison verticale des deux courbes inférentielle ; le recalcul en aval reste exclu.
- Après le run full, régénérer avec `--strict` vers `results/pca_drift_benchmark/figures/` (racine du prompt), puis comparer `figures_fingerprint` et les `fpr_mismatch_k` entre smoke et full comme trace d'audit.
- Le stream 31 peut réutiliser `verify_figures_dir` et les codes du §5 dans ses tests de contrat, pour que la chaîne runner → tableaux → figure reste fermée par un seul jeu de pointeurs.

## Décision GO intégrée

GO du **plan 30 uniquement**, le 2026-10-31, après audit Codex isolé et deux amendements mineurs autorisés directement par le chercheur. Les défauts du plan sont retenus. Aucun retour Claude n'est nécessaire pour ces précisions ; aucune logique scientifique ni sélection de scénario n'est changée.

Amendements intégrés dans le corps :
1. `V_NOT_COMPARABLE` vérifie une même fonction M et un même gamma, avec M évalué à la dimension propre de chaque ligne. Il n'exige pas M(k) = M(d_star) et ne recalcule pas V.
2. `INPUT_INVALID` vérifie les quatre CSV lus contre `manifest.outputs` ; le hash du manifest est contrôlé via la provenance d'entrée des tableaux. Le manifest producteur ne contient pas son propre hash.

La comparabilité FPR reste un filtre descriptif de protocole et d'intervalles : elle ne prouve pas l'égalité des FPR atteints. Les intervalles RMST marginaux ne sont pas des intervalles de différence appariée. Les API et sous-clés non encore fixées du futur assembleur 29 restent des préconditions G0 à vérifier lors de l'implémentation, sans prétendre qu'elles existent déjà.

**Portée : plans seulement.** Claude Code rédige les plans en max/xhigh ; Codex les audite et contrôle la clôture/intégration ; Mistral Vibe `large-4`, thinking `high`, est l'implémenteur désigné après GO d'exécution. Ce GO de plan autorise la planification du dernier stream 31, pas le démarrage d'une implémentation 30. Aucun full, nouvelle simulation, recalibration ou évaluation réelle post-2019 n'est autorisé.

Décision de référence : `prompts/GO-stream-30.md`. Les deux substitutions mineures sont tracées dans `docs/audits/stream-30-plan-review.md` ; le reste de la proposition Claude est conservé.

