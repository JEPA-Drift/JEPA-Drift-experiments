# Stream 28 — Runner `experiments/pca_drift_benchmark.py` — Plan révisé v2 (Phase A, lecture seule)

**Politique courante :** `prompts/POLICY-PCA-PLAN-ONLY.md`. L'implémentation candidate existe, mais sa clôture est suspendue aux deux corrections de `docs/audits/stream-28-codex-review.md`. Leur plan audité est enregistré à `prompts/plans/plan-28-closeout.md` ; approbation du plan uniquement, aucune exécution autorisée. Aucun nouveau code Claude ni plan aval avant finalisation du 28.

**Avenant prioritaire du chercheur :** `prompts/GO-stream-28-amendment-P0-P1.md`, enregistré avant reprise ciblée à 18:52 UTC. P0 prédictif puis P1 ; les fichiers applicatifs existants sont conservés. L'ancienne règle empirique est révoquée, le schéma /2 reste à auditer et sceller.

- **Cadre.** 2026-10-30, branche `stream-28`, base `e1f80847245b14498e331abda1e3d13cf415ec8f`. Les chemins sont relatifs à la racine du worktree ; `$MAIN` désigne l'arbre principal.
- **Statut.** Plan enregistré avant code, remplaçant v1 ; GO Codex accordé pour implémentation et smoke uniquement. La décision intégrée ci-dessous ferme les précisions normatives ; aucun résultat n'est encore produit.
- **Archive v1.** `logs/pca_drift_orchestration/PLAN-v1.md`, SHA-256 mesuré `6e1a6e5a9aa5d9d93702a981df3f0f0f0fd4b649982bab636603a8f53f7b7c5d`. La transcription initiale à 62 caractères dans le NO-GO a été corrigée avant ce GO d'après l'archive.

## 0. État vérifié
- **Base.** Depuis `dd28ed2`, seul `prompts/Protocole Codex.md` a changé (ajout de `--remote-control`). Le code scientifique est identique. `prompts/NO-GO-stream-28.md` n'est pas suivi : c'est la trace de Codex.
- **Invariants.** E2 : SHA-256 de `results/e2/e2_cells.csv` = `e315e537…570823` sur disque et dans l'index, 47 lignes CRLF, attribut `-text`. D8 : `C-e3-d8-fail` intact. `configs/FROZEN.json` absent.
- **D3.** `ret_wide.npy` 6 738 × 239 en float64 (ordre Fortran) ; `dates.npy` du 2000-01-03 au 2026-10-16. Segments : pretrain 2005-01-03..2015-12-31 ; calib 2016-04-07..2019-12-31 (941 lignes complètes) ; `monitor.first_day` = 2020-04-06 ; embargo de 65 séances. Empreintes dans `MANIFEST.json`.
- **Environnement `.venv`.** Python 3.12.9, NumPy 2.4.4 (scipy-openblas 0.3.31), SciPy 1.17.1, pandas 3.0.6, PyYAML 6.0.3, statsmodels 0.15.0.
- **Collision.** `prompt-28-e11.md` et `28_STREAM_PCA_DRIFT_RUNNER.md` portent tous deux le titre `## PROMPT 28 —`. `tools/check_prompts.py` (motif `^## PROMPT (\S+) —`) ne lit que `prompt-*.md`.
- **Lectures.** CLAUDE.md, DEVIATIONS, protocole Codex (Remote Control compris), prompts 12 révisé, 28 et 11, deck v4 (`$MAIN/slides/…`, lecture seule), NO-GO, v1. Les prompts 29 à 31 ne sont lus que comme consommateurs.

## 1. API lues
- `stats.covariance` : `ledoit_wolf(X) -> (sigma, shrinkage)` ; `eigh_desc(sigma) -> (eigval décroissantes, eigvec signés)`.
- `representations.pca` : `mp_edge(T, N)` ; `mp_count(X) -> (n_above, edge)` (corrélation, inégalité stricte) ; `pca_directions(X, K, mode, shrinkage) -> (eigval, eigvec, sel, stats)` avec `("mp", "full", "ledoit_wolf")`. Plus `representations.base._sha256(a)`.
- `monitors` : `eprocess.log_subgaussian_mixture(z, s2)` (τ = 1 seulement, référence de test) ; `cusum.cusum_trajectory_vec(x, delta)` ; `cusum.strict_cusum_vec(x, delta, threshold)` (alarme `S > λ`, indice 0-based, −1 sinon) ; `streams.energy_stream(r, mu, sigma)` ; `calibration.null_windows(x, length, n, rng, flip)`.
- Utilitaires : `stats.intervals.wilson(k, n)` ; `floors.mixture_multiplier(dim, gamma)` en contrôle ; `pipelines.save_fair_csv(df, path)`, `split_rows(dates, splits)`, `horizon_gamma(H, alpha)`, `ENERGY_DELTA`.
- `sim.garch_panel(T, N, 0.0, 0.0, nu, rng, factor_rho=0.4, burn=0)` : coupe i.i.d. équicorrélée, gaussienne (`nu=None`) ou t7 multivariée (un χ²₇ commun par jour).
- `injection.fit_background(X_fit, 1)` ; `injection.inject(X_fit, "F4-rotate", 0, None, {"calib": (0, T_fit), "fit": fit, "pair": (0, 1), "theta_deg": θ}, rng) -> (_, M, meta)`.
- `data_loader.sp500.load_splits("d3_239")` ; `_realize_segments(dates)` sert d'oracle de test.
- Non utilisés : `load_d3_239` (matérialise tout le panel) ; `bootstrap_threshold` (quantile interpolé, sans garantie de rang) ; `inject("F3")` (échelle LW).

## 2. Graphe d'appels
```
experiments/pca_drift_benchmark.py
main(argv): check_env → load_config(path, mode) → validate_config → identity_block → prepare_dirs(out, log_dir, resume)
├─ real_status_rows(cfg)            sp500.load_splits ; aucun rendement
├─ run_synthetic(cfg, store)        par fond : SYNTH_GAUSS_EQUICORR | SYNTH_T7_EQUICORR
│  ├─ draw_path(bg, role, i)        sim.garch_panel(..., rng(bg, role, i), ...) ; une graine par trajectoire
│  ├─ fit_basis(X_fit)              pca.pca_directions ; eigvalsh(corrcoef) ; base._sha256
│  ├─ population(basis)             Σ0, M_30 (injection.inject F4-rotate), C0, C1, μ en espace z (§6.1)
│  ├─ drifts(basis)                 Δ_A, Δ_C, M_30 (§6.4)
│  ├─ select_mean | select_cov      §7 ; mixture_cost (scipy.optimize.brentq) ; corde M(1)–M(20)
│  ├─ project(role, transform)      z = T(X) @ W20 ; m = T(X).mean(1)
│  ├─ fit_centering(bg)             Ĉ0 calculé sur le seul rôle `centering`
│  ├─ scan_statistic | vech_stream | energy (streams.energy_stream, cusum.*_vec)
│  └─ rank_threshold(maxima, alpha, rule) ; evaluate(...) (intervals.wilson) ; formula_checks(...)
├─ run_real(cfg, store)             mode full et --dataset real|both
│  ├─ read_pre2020_panel()          mmap ret_wide.npy + dates.npy ; SHA-256 vs MANIFEST ; tranche ≤ 2019-12-31
│  ├─ fit_basis(X_calib) ; r̄_calib ; stress_library() ; real_null(cohort) via null_windows(flip=True)
│  └─ evaluate_real_path(...)       jamais appelé sur des rendements REAL ≥ 2020 avant J4
└─ write_outputs()                  save_fair_csv ×6, puis manifest.json en dernier
tests/test_pca_drift_benchmark.py → runner ; références : log_subgaussian_mixture, mixture_multiplier, _realize_segments
```

## 3. Matrice de couverture
| Cas | MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM | COV_QUADRATIC_VECH_SCAN | ENERGY_INCREASE_CUSUM | Sélecteurs | Limites |
|---|---|---|---|---|---|
| Moyenne gaussienne (A, C) | éligible | — | — | PREFIX, CPV90, ORACLE_Q_MIX/AFFINE ; EXANTE `UNSUPPORTED` | quasi-vraisemblance (blanchiment estimé) |
| Moyenne t7 (A, C) | éligible | — | — | idem | proxys gaussiens |
| Covariance gaussienne, témoin (B30) | — | éligible | éligible | PREFIX, CPV90, COV_JOINT_ORACLE, COV_MARGINAL ; EXANTE `UNSUPPORTED` | M seulement en `HEURISTIC_COST` |
| Covariance t7 (B30) | — | éligible | éligible | idem | proxys gaussiens |
| Réel rétrospectif (moyenne) | code éligible ; évaluation `BLOCKED_PRE_J4` | `UNSUPPORTED` (pas de Σ1 réel) | `UNSUPPORTED` | PREFIX, CPV90, EXANTE (≤ 2019) ; ORACLE ex post bloqué | une trajectoire ; nul D6 approximatif |

Non retenus :
- signes exacts et e-détecteurs : canaux scalaires ;
- énergie P3-D : remplacée par l'indice EW, son nul relisant ses fenêtres (`C-P4D-null-insample`) ;
- P7 et GLR.

## 4. Schéma à sceller après avenant `pca_drift_benchmark/2`
**4.1 Fichiers**
- Répertoires `results/pca_drift_benchmark/{smoke_predictive_v2,full}/`, chacun avec `manifest.json`, `spectra.csv`, `selection.csv`, `calibration.csv`, `trials.csv`, `aggregates.csv`, `issues.csv`.
- Écriture CSV par `save_fair_csv` :
  - NA écrit `NaN`, jamais 0 ; lecture avec `float_precision="round_trip"` ;
  - S en JSON compact, trié, indexé à partir de 1 (`[1,2,10]`) ;
  - lignes triées par clé primaire (`mergesort`).
- `trials.csv` est normalisé. Au-delà de 50 Mo, il reste local et non suivi ; son SHA-256 figure au manifest ; ni compression ni ajout forcé.
- `manifest.json` est écrit en dernier (`sort_keys`, `indent=2`), sans horodatage, durée ni chemin absolu.

**4.2 Énumérations fermées.** Validées avant écriture ; une valeur inconnue lève une exception.
- `status` : OK | BLOCKED_PRE_J4 | NOT_EVALUABLE_STANDARD_SPLIT | DATA_UNAVAILABLE | UNSUPPORTED | BLOCKED_RESOURCE | CPV90_OUTSIDE_TOP20 | CALIBRATION_FAILED | PATH_TOO_SHORT ; `execution` : EXECUTED | NOT_EXECUTED.
- `source_kind` : SYNTHETIC_GAUSSIAN | SYNTHETIC_T7 | REAL_RETROSPECTIVE ; `claim_scope` : SYNTHETIC_MC | REAL_STANDARD_SPLIT | REAL_RETROSPECTIVE_EXPLORATORY.
- `dataset_id` : SYNTH_GAUSS_EQUICORR | SYNTH_T7_EQUICORR | D3_239 ; `cohort_id` : NA | cohort_standard_embargo | cohort_retrospective_covid.
- `event_id` : A_market_mean | B_cov_rotate30 | C_residual_mean | COVID_2020 | STYLE_2022H1 (15°/45° réservés au balayage différé) ; `event_window_id` : SYNTH_ONSET_ALIGNED | E_COVID_2020_ACUTE | E_STYLE_2022H1.
- `detector_family` :
  - MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM : maximum sur τ, sans récursion additive ;
  - COV_QUADRATIC_VECH_SCAN : tient le rôle du `COV_QUADRATIC_CUSUM` du prompt 28, mais c'est un scan, sans récursion additive ;
  - ENERGY_INCREASE_CUSUM : récursion de Page.
- `method` : BASELINE_PREFIX | BASELINE_CPV90 | ORACLE_Q_MIX | ORACLE_Q_AFFINE | EXANTE_QBAR | COV_JOINT_ORACLE | COV_MARGINAL_DIAGNOSTIC | ENERGY_INDEX_COMPARATOR.
- `objective_kind` : NONE | CPV90_RULE | MEAN_MIX_FLUID_SURROGATE | MEAN_AFFINE_SURROGATE | EXANTE_QBAR_MIX_FLUID_SURROGATE | COV_JOINT_AFFINE_SURROGATE | COV_JOINT_MIX_HEURISTIC | COV_MARGINAL_MIX_DIAGNOSTIC.
- `info_kind` : MEAN_GAUSS_PLUGIN_LW | MEAN_GAUSS_PLUGIN_LW_T7_PROXY | MEAN_GAUSS_POP_JOINT_EXACT | MEAN_GAUSS_POP_JOINT_T7_PROXY | COV_GAUSS_POP_JOINT_EXACT | COV_GAUSS_POP_JOINT_T7_PROXY | COV_GAUSS_MARGINAL | COV_GAUSS_MARGINAL_T7_PROXY | EXANTE_QBAR_PLUGIN_LW | REAL_EXPOST_PLUGIN_LW. Aucune valeur ne désigne une KL t7 ou une KL « observée ».
- `cost_kind` : MIX_FLUID_SURROGATE | AFFINE_SURROGATE | HEURISTIC_COST | NONE ; `metric_kind` : HOLDOUT_NULL_FPR | ALT_RMST | REAL_EVENT_PATH | GAUSS_FORMULA_CHECK (fond gaussien) | GAUSS_PROXY_CHECK_T7 (deux moments seulement, pas de KL t7).
- `role` (trials) : calibration | holdout_null | alternative | real_path (rôles de graine au manifest) ; `time_origin` : ONSET_ALIGNED | CONTINUOUS_RESTART_AFTER_ALARM.
- `claim_flag` (liste JSON) : NONE | ORACLE_INJECTED_DELTA | ORACLE_TRUE_SIGMA1 | EX_POST_ORACLE | COV_SURROGATE_EXPLORATORY | HEURISTIC_COST | RETROSPECTIVE_DIAGNOSTIC ; `oracle_input` : INJECTED_DELTA | TRUE_SIGMA1 | EXPOST_EVENT_DELTA | STRESS_LIBRARY_2008_2011 | NONE.
- `null_kind` : SYNTH_INDEPENDENT_PATHS | REAL_D6_SIGNFLIP_PRE_MONITOR_WINDOWS ; `null_validity` : EMPIRICAL_QUASI_LIKELIHOOD | EMPIRICAL_ENERGY | APPROXIMATE_D6_INSAMPLE_OVERLAPPING ; `stream_kind` : WHITENED_PCA_SCORES | VECH_QUADRATIC_CENTERED | EW_INDEX_ENERGY.
- `alarm_rule` : GE | GT ; `ci_kind` : NORMAL_DEFF1 | WILSON | NONE ; `severity` : BLOCKER | WARNING | INFO ; `comparability` : COMMON_20_AXIS_UNIVERSE | NOT_COMPARABLE_OUTSIDE_TOP20.

**4.3 Identité, provenance, identifiants**
- **`identity`** regroupe `schema_version`, `config_hash`, `code_hash` (octets triés du runner, de la config et des modules `jepadrift` importés), `env_hash` (versions, BLAS, threads, MKL_CBWR, PYTHONHASHSEED), `input_hash` (couples triés (chemin, SHA-256) des fichiers lus, dont `splits.yaml`) et `seed`. On en tire `run_fingerprint = SHA-256(identity)`.
- **`provenance`**, hors identité : SHA Git, branche, état sale, argv normalisé (`<OUT>`, `<LOG>`).
- **Après commit.** Tant que les octets de code, de configuration, d'entrée et d'environnement sont inchangés, `identity`, les ids et les CSV restent identiques ; seule `provenance` change. La reproductibilité compare donc les CSV et `identity`.
- **Empreintes** (SHA-256 complet) : `basis_hash` = eigval ‖ eigvec ; `centering_hash` = Ĉ0 ; `drift_hash` = Δ ou M ; `calibration_hash` = maxima ‖ seuil ; `split_hash` = rôles, ou splits + cohorte + fenêtres + politique.
- **Notation.** `sha16` = 16 premiers caractères hexadécimaux du SHA-256 du JSON canonique.
- `null_id = sha16{run_fingerprint, dataset_id, cohort_id, null_kind, clé de rôle, n, H}` ; `null_calibration_id = sha16{null_id, detector_family, params{p, s2, delta, alarm_rule}, centering_hash, basis_hash, S, alpha, "predictive_exchangeable_rank_v2"}`.
- `metric_id` : HOLDOUT `sha16{kind, null_calibration_id, clé holdout, n_null}` ; ALT `sha16{kind, null_calibration_id, event_id, drift_hash, event_window_id, clé alt, n_alt, H, time_origin}` ; REAL `sha16{kind, null_calibration_id, cohort_id, event_window_id, method, S, time_origin, policy}` ; CHECK `sha16{kind, run_fingerprint, dataset_id, event_id, drift_hash, n_alt, H}`.
- `selection_id = sha16{run_fingerprint, dataset_id, cohort_id, event_id, method, objective_kind, reservoir_k, S, basis_hash}`, sans étiquette d'expérience.
- **Conséquences.** Les préfixes E1 et E2 partagent ids et valeurs ; E3 ORACLE_Q_MIX = E2 à k = 20. Un S donné, pour une famille, une calibration et un scénario, n'a qu'un `metric_id`. Les cohortes ne partagent aucun id. Un doublon de clé à contenu différent lève une exception.

**4.4 Colonnes.** Communes à tous les fichiers (`NaN` si sans objet) : `schema_version, run_mode, run_fingerprint, source_kind, claim_scope, dataset_id, cohort_id, split_hash, event_window_id, event_id, detector_family, k, S, d, objective_kind, selection_id, metric_id, null_id, null_calibration_id, calibration_hash, config_hash, basis_hash, seed, status, execution`.
- **spectra** (clé : dataset_id, basis_hash, k = 1..N) : fit `N, T_fit, fit_first_day, fit_last_day, fit_rows, complete_rows, nan_cells` ; Ledoit-Wolf `lw_shrinkage, trace_lw, lambda_lw, whitening_scale, cpv_lw` ; corrélation `lambda_corr, mp_edge, mp_above, mp_count, kaiser_ge1, kaiser_count, cpv90_k_full, cpv90_status` ; population `pop_var_axis` (v̂ₖᵀΣ0v̂ₖ), `null_var_z` (pop_var_axis/λ̂ₖ) ; `x_fit_sha256`.
- **selection** (clé : selection_id, experiment, row_kind, d) :
  - `experiment, method, row_kind` (SELECTED, ou CANDIDATE pour chaque d = 1..k), `reservoir_k, rank_order, selection_exact, tie_broken, oracle_input` ;
  - `info_kind, I_objective, cost_kind, M_cost, C_affine, V_mix, V_affine, I_plugin_lw, I_pop_joint, I_cov_joint` ;
  - `I_cov_marginal_sum` (jamais lue comme jointe), `pop_offdiag_max, null_metric_id, claim_flag, cpv90_k_full, comparability`.
- **calibration** (clé : null_calibration_id) :
  - `null_kind, stream_kind, p, s2, s2_rule, cusum_delta, alarm_rule, H, alpha, n_cal, rank_r, threshold` ;
  - `calibration_alarms, calibration_fraction, threshold_rule, predictive_bound, guarantee_basis, maxima_sha256, centering_hash, centering_days, centering_pop_bias_max` ;
  - `anytime_valid` (= False), `null_validity, window_starts_distinct, in_sample_share`.
- **aggregates** (clé : metric_id) :
  - `metric_kind, null_metric_id, time_origin, H, n, deff, n_eff, alarms, fpr, fpr_lo, fpr_hi, target_fpr` ;
  - `rmst, rmst_sd, rmst_se, rmst_lo, rmst_hi, ci_kind, det_rate, det_lo, det_hi, censored_share` ;
  - réel : `monitor_armed_from, onset_date, event_end_date, n_event_sessions, alarm_dates` (JSON), `pre_onset_alarms, pre_onset_alarm_dates` (JSON, chaque alarme conservée), `detected_during_event, time_to_alarm_during_event, event_censored, post_onset_delay_h250, post_onset_alarm_date, post_event_alarm, path_supports_H` ;
  - contrôles : `check_estimate, check_se, check_reference, check_space` (= `WHITENED_Z20`) ;
  - `k` et `objective_kind` valent NaN : une métrique appartient au quadruplet (S, famille, calibration, scénario), pas à une méthode.
- **trials** (clé : group_id, role, replicate) : `group_id` (= `null_calibration_id` si role = calibration, `metric_id` sinon) ; `first_hit` (1-based, alarme incluse ; −1 sans alarme ≤ H) ; `censored_time = min(T, H)` ; `detected` ; `stat_max` (maximum sur H pour calibration et holdout, NaN pour alternative) ; `pre_onset_alarm` ; `detected_during_event`.
- **issues** (clé : issue_id) : `severity, code, scope, message, deviation_ref, detail`.
- **manifest** : `identity`, `provenance` ; `synthetic` (modèle, Σ0, mélange t7, Δ_A et Δ_C sur 239 flottants, sha256 de M_30, c, informations) ; `real` (fichiers et hachages, tranches indexées, cohortes, politiques, stress, nul) ; `detectors` ; `costs` (M(d) pour d = 1..20, a, c) ; `pre_j4` ; `outputs` (sha256, octets, lignes).

**4.5 Lignes réelles, émises à chaque exécution.** Elles ne dépendent que de la configuration et de `splits.yaml`, jamais d'un rendement.

| cohort_id | événement | status | execution |
|---|---|---|---|
| cohort_standard_embargo | COVID_2020 | NOT_EVALUABLE_STANDARD_SPLIT (2020-03-23 < 2020-04-06) | NOT_EXECUTED |
| cohort_standard_embargo | STYLE_2022H1 | BLOCKED_PRE_J4 | NOT_EXECUTED |
| cohort_retrospective_covid | COVID_2020 | BLOCKED_PRE_J4 (REAL_RETROSPECTIVE_EXPLORATORY) | NOT_EXECUTED |

Une ligne par méthode (PREFIX k = 1..20, CPV90, EXANTE, ORACLE ex post), métriques à NaN. `DATA_UNAVAILABLE` si un fichier manque ou si un hachage diverge.

**4.6 Document de schéma.** `docs/sections/pca_drift_benchmark.md`, en anglais, documente fichiers, clés, colonnes, types, énumérations, hachages, jointures, temps, censure et correspondance E1/E2/E3. Toute modification impose une nouvelle `schema_version` et l'accord de Codex.

## 5. Détecteurs, seuils, évaluation
**5.1 MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM**
- **Entrée.** z_t = W_Sᵀx_t, W = V̂Λ̂^{-1/2} gelée ; centrage par r̄_calib en réel seulement.
- **Statistique.**
  - S_0 = 0 et S_t = Σ_{i≤t} z_i ; pour 1 ≤ τ ≤ t, n = t − τ + 1 et D = S_t − S_{τ−1}.
  - logL(τ,t) = −(d/2)·log1p(n·s2) + s2·‖D‖²/(2(1 + n·s2)).
  - W_t = max_{τ=1..t} logL(τ,t) ; alarme à T_h = inf{t ≥ 1 : W_t ≥ h}.
- **Implémentation.** `scan_statistic(Z, s2, h=None) -> (W, first_hit)`, avec Z de forme (B, H, p) et S de forme (B, H+1, p). Les termes a_n = −(p/2)·log1p(n·s2) et b_n = s2/(2(1+n·s2)) sont précalculés.
  - À chaque t : D = S[:, t, None] − S[:, :t] ; q = (D·D).sum(−1) ; W[:, t−1] = max(a[t−1::−1] + b[t−1::−1]·q).
  - Tous les τ ∈ {1..t} sont évalués : ni fenêtre, ni GLR, ni récurrence O(1). L'arrêt anticipé n'existe qu'en mode premier franchissement.
  - Coût O(H²·p) par trajectoire ; résultats bit à bit identiques quel que soit B.
- **Prior.** s2(p) = 2·ln(H/α)/(H·p) = 2·I_ref/p, où I_ref = ln(γ_H)/H et γ_H = `horizon_gamma(H, α)` = 5 000. Fixé ex ante, sans donnée ni Δ, identique pour toutes les méthodes et cohortes.
- **Statut.** Le blanchiment estimé donne C0,S ≠ I, même pour un générateur gaussien. On est donc en quasi-vraisemblance : `anytime_valid=False`, pas de seuil log γ, calibration empirique seulement.

**5.2 COV_QUADRATIC_VECH_SCAN**
- **Flux.** y_t = vech_std(z_t z_tᵀ − Ĉ0,S), avec vech_std(A) = (A_kk/√2)_k ‖ (A_jk)_{j<k} et p = d(d+1)/2.
- **Centrage.** Ĉ0 est la moyenne de z zᵀ (20 × 20) sur un rôle de nuisance indépendant, `centering` (n_center trajectoires, graine propre, `centering_hash`).
  - Il est figé avant toute calibration et reste identique pour calibration, holdout et alternatives.
  - Aucune trajectoire de calibration n'y entre.
- **Pourquoi pas le fit.** Sur le fit, E_fit[z_k²] = ℓ_k/λ̂_k ; hors échantillon, E0[z_k²] = v̂ₖᵀΣ0v̂ₖ/λ̂_k. Le haut du bulk est gonflé d'un facteur ≈ (1+√(N/T))² ≈ 2,2 (approximation MP, à mesurer).
- **Biais résiduel.** Rapporté par `centering_pop_bias_max = max|Ĉ0 − C0_z|` ; le seuil reste empirique.
- **Noyau.** `scan_statistic(y, s2(p), h)`, sensible aux hausses, aux baisses et aux termes hors diagonale. Aucun Σ1 n'entre dans ce détecteur ex ante.

**5.3 ENERGY_INCREASE_CUSUM** (comparateur séparé)
- m_t = moyenne_i x_{t,i}, calculée avant l'ACP ; e_t = energy_stream(m_t, μ, σ), où μ et σ viennent de m² sur le fit.
- S_t = max(0, S_{t−1} + e_t − 0,5) ; alarme GT (S > λ) ; k = S = d = NaN.

**5.4 Seuil par rang** : `rank_threshold(maxima, alpha, rule) -> (threshold, r, alarms)`.
- **Validation.** ValueError si les maxima ne sont pas 1-D, sont vides ou non finis, si α ∉ (0, 1), ou si rule ∉ {GE, GT}.
- **Calcul.**
  - r = floor(Fraction(str(α))·(n+1)) − 1. Si r<0 : CALIBRATION_FAILED (effectif insuffisant), aucun seuil ni garantie. Sinon b = sort(maxima)[n−r−1] ;
  - h = b en GT, h = nextafter(b, +inf) en GE ; un h non fini donne `CALIBRATION_FAILED`.
- **Contrôle et portée.** alarms = #{maxima > b} ≤ r. Sous échangeabilité calibration/nouveau maximum : P(max_new>b) ≤ (r+1)/(n+1) ≤ α, égalités conservatrices. Garantie marginale sur calibration et nouvelle trajectoire, avec paramètres fit/nuisance figés ; absente pour fenêtres historiques chevauchantes. Ni boucle ULP, ni confusion avec FPR holdout.

**5.5 Évaluation**
- **Calibration** : n_cal trajectoires nulles indépendantes.
- **Holdout** : n_null trajectoires ; FPR = #{max ≥ h}/n, avec IC de Wilson ; aucun « 5 % » affirmé.
- **Alternatives** : n_alt trajectoires, onset au jour 1 ; RMST250 = mean(min(T, 250)) ; SE = sd/√(n/deff), deff = 1 ; det_rate avec IC de Wilson ; censurés = 1 − det_rate.
- **Graines** : clé [28, root, crc("path"), crc(bg), crc(role), i] ; les rôles fit, centering, calibration, holdout_null et alternative sont disjoints.
- **Trajectoires partagées** : toutes les méthodes lisent les mêmes trajectoires ; A, B et C partagent la base alternative. Les comptes portant sur des quantités dépendantes restent descriptifs.

## 6. Population ou LW ; information ; scénarios
**6.1 Espaces**
- Σ0 = (1−ρ)I + ρ11ᵀ, déclarée ; Σ0⁻¹ par Sherman–Morrison. λ1 = 96,2 et bulk à 0,6 (×238) : toute base de 1^⊥ diagonalise Σ0, donc l'ordre de v̂2..v̂20 n'est que du bruit.
- Σ̂ = Σ_LW(X_fit) est diagonalisée exactement par V̂.
- Chaîne x → u = V̂20ᵀx → z = Λ̂^{-1/2}u. KL et LLR sont calculés en z, avec C0 = W20ᵀΣ0W20, C1 = W20ᵀΣ1W20, μ = W20ᵀΔ. L'invariance u ↔ z est vérifiée par identité.

**6.2 Moyenne**
- Objectif : q̂_k = (v̂ₖᵀΔ)²/(2λ̂_k) = μ_k²/2 (plug-in LW, additif).
- Diagnostic : I_pop_joint(S) = ½·μ_Sᵀ·C0,S⁻¹·μ_S. Exacte pour le générateur gaussien, proxy en t7, non additive.
- I_pop_full = ½ΔᵀΣ0⁻¹Δ majore I_pop_joint(S), qui est monotone par inclusion. Aucune équivalence des optima n'est affirmée.
- En synthétique, q̂ vient des coefficients de conception (zéros exacts) et vaut V̂ᵀΔ à 1e−12 près.

**6.3 Covariance**
- Jointe : I_cov_joint(S) = ½[tr(C0,S⁻¹C1,S) − logdet(C0,S⁻¹C1,S) − |S|].
- Marginale : q_k^cov = ½(r_k − 1 − ln r_k), r_k = (C1)_kk/(C0)_kk ; leur somme reste un diagnostic.
- Une valeur dans [−1e−12·max(1,|I|), 0) est écrêtée à 0 et comptée ; en dessous, exception.

**6.4 Scénarios** (base propre à chaque fond ; injection dans les rendements avant projection)
- **A.** Δ_A = (4/√252)·√(v̂1ᵀΣ0v̂1)·v̂1, soit une projection standardisée de SR = 4 sous la population et une KL marginale de 16/504 exactement. I_plugin_lw et I_pop_full sont rapportés séparément, sans contrainte ; `injection.py` n'est pas modifié.
- **B30.** M_30 = rotation de Givens de (v̂1, v̂2) ; X_alt = X·M_30ᵀ.
- **C.** β_k = c pour k = 10..20, 0 ailleurs ; Δ_C = V̂β, orthogonal à v̂1.
  - c = √(6/(uᵀΣ0⁻¹u)) avec u = Σ_{10..20} v̂_k, d'où ½Δ_CᵀΣ0⁻¹Δ_C = 3,0 sous Σ0 (assert 1e−12).
  - Sont aussi rapportés I_plugin_lw, I_pop_joint({10..20}) et I_pop_joint(P_20).

**6.5 Contrôles de formule** (en z, descriptifs)
- Moyenne : LLR = μᵀC0⁻¹z − ½μᵀC0⁻¹μ, comparé à I_pop_joint(P_20).
- Covariance : LLR = −½zᵀ(C1⁻¹−C0⁻¹)z − ½(logdet C1 − logdet C0), comparé à I_cov_joint(P_20).
- SE = sd/√(n·H). En t7, `GAUSS_PROXY_CHECK_T7` ne vérifie que deux moments.

**6.6 M et s2.** M(d, 504) = x_d/ln 504, avec x_d = ln 504 + (d/2)·ln(1 + 2x_d/d). C'est un substitut fluide à prior apparié 2I/d, distinct du s2(p) fixe du détecteur, et non un ADD, un RMST ou un ARL0.

## 7. Sélections, coûts, spectres
- **ORACLE_Q_MIX / ORACLE_Q_AFFINE**
  - Pour chaque P_k : tri de q̂ décroissant (égalité → axe croissant) ; S_{k,d} = top-d pour tout d = 1..k, en lignes CANDIDATE.
  - d* = argmax V_mix, ou V_affine en E3 à k = 20 ; égalité → plus petit d.
  - `tie_broken` signale les cas où l'égalité a décidé. Exemple : C pour k < 10, où S* = {1} et V = 0.
- **EXANTE_QBAR** (réel uniquement)
  - Δ_e = r̄_e − r̄_calib, e ∈ {S2008 [2008-09-15, 2008-11-20], S2011 [2011-07-25, 2011-10-03]} ; q̄ équipondéré.
  - Ordre q̄ décroissant sur les axes 1..20 ; V̄(d) pour tout d.
  - Fenêtre incomplète → issue sans résultat et sans remplissage. Synthétique : `UNSUPPORTED`.
- **COV_JOINT_ORACLE**
  - Énumération exhaustive exacte des 2^20 − 1 sous-ensembles (`combinations` par d ; `slogdet`/`solve` par lots de 20 000).
  - Pour chaque (k, d) : argmax de I_cov_joint, égalité → ordre lexicographique.
  - d* par V_affine (principal) et par V_mix (`COV_JOINT_MIX_HEURISTIC`, `HEURISTIC_COST`) ; `selection_exact=True`, marque `ORACLE_TRUE_SIGMA1`.
  - nmax > 20 refusé (`# ponytail:` faisceau avec selection_exact=False si nmax augmente).
- **COV_MARGINAL_DIAGNOSTIC** : tri par q^cov, d* par Σq^cov/M à k = 20.
- **`mixture_cost(d, γ)`** : brentq sur f(x) = x − A − (d/2)·log1p(2x/d), avec f(0) = −A < 0 et f croissante.
  - Asserts : racine unique supérieure à A, M > 1.
  - Contrôles : `mixture_multiplier` et le deck (M(1) = 1,2239 ; M(4) = 1,5696 ; M(500) = 9,6427).
- **Coût affine** : corde de M entre d = 1 et d = 20, indépendante de nmax et du réservoir. c = (M(20) − M(1))/19, a = M(1) − c, a et c > 0 assertés ; nmax = 1 est admis.
- **Spectres** : CPV sur Σ_LW (trace complète) ; MP et Kaiser (λ_corr ≥ 1) sur la corrélation.
  - k90 > 20 → `CPV90_OUTSIDE_TOP20`, sans S ni métrique, `cpv90_k_full` renseigné.
  - Sinon, CPV90 = P_k90 avec le `metric_id` de la ligne E1.
- **Expériences**
  - E1 = préfixes k = 1..20, plus ENERGY.
  - E2 = préfixes (mêmes ids) + ORACLE_Q_MIX, ou COV_JOINT_ORACLE ×2.
  - E3 = CPV90, AFFINE, MIX (= E2 k20), EXANTE, COV ×2 (= E2 k20), MARGINAL, ENERGY.

## 8. Réel, garde pré-J4, cohortes
- **`read_pre2020_panel()`**, sans `load_d3_239` :
  - lit `dates.npy` ; hache les fichiers et compare à MANIFEST (`DATA_UNAVAILABLE` en cas d'écart) ;
  - `ret_wide.npy` en `mmap_mode="r"` ; [a, b) = lignes pre_monitor 2005-01-04..2019-12-31, moins l'exclusion déclarée 2005-01-03 ;
  - seule cette tranche est matérialisée (`np.array(mm[a:b], order="C")`), puis viennent `check_pre_j4` et le contrôle de finitude ; [a, b) est consigné au manifest.
- **Ajustement.** ACP LW sur les 941 lignes calib (assert), et r̄_calib.
- **Nul D6.** 2 000 fenêtres de 250 jours dans pre_monitor ; un signe de Rademacher par jour ; z centré par r̄_calib ; graines salées par cohorte.
  - Limites déclarées : 3 525 départs distincts qui se recouvrent ; une part tirée de l'ajustement ; dérive et levier effacés ; symétrie rejetée sur D3 PC1/PC2.
  - Aucun FPR holdout.
- **cohort_standard_embargo.** Surveillance dès `monitor.first_day`.
  - COVID_2020 → `NOT_EVALUABLE_STANDARD_SPLIT`.
  - STYLE_2022H1 en `ONSET_ALIGNED`, du premier jour ≥ 2022-01-01 au dernier jour ≤ 2022-06-30 ; lecture H250 séparée ; marque `RETROSPECTIVE_DIAGNOSTIC`.
- **cohort_retrospective_covid.** Gelée au 2019-12-31, armée au premier jour ≥ 2020-01-01 (vérifié sur le calendrier).
  - R1 : surveillance continue ; chaque alarme est enregistrée, suivie d'un redémarrage explicite (S = 0) le lendemain.
  - R2 : chaque alarme antérieure au 2020-02-24 est conservée et ne compte jamais comme détection.
  - R3 : détection = première alarme dans [2020-02-24, 2020-03-23], délai = index − onset + 1 ; sans alarme, `event_censored` au nombre de séances de la fenêtre.
  - R4 : lecture séparée sur [onset, onset + 249] (`post_onset_delay_h250`) ; une alarme après le 2020-03-23 donne `post_event_alarm` ; trajectoire trop courte → `PATH_TOO_SHORT`.
  - R5 : n = 1, donc ni IC ni FPR ; scope `REAL_RETROSPECTIVE_EXPLORATORY` ; déviation `C-pca-covid-retrospective`.
- **Garde.**
  - Δ_real = r̄_fenêtre − r̄_calib est marqué `EX_POST_ORACLE` et n'est jamais utilisé ex ante.
  - `evaluate_real_path` est testé sur un panneau factice daté (`FAKE_DATED_TEST`, jamais écrit sous `results/`).
  - REAL ≥ 2020-01-01 est refusé avant J4 ; aucun FROZEN.json n'est fabriqué.

## 9. Validation, ressources, smoke
- **`validate_config`** refuse :
  - dimensions : N < 2, nmax ∉ [1, min(20, N−1)], H < 1, T_fit < 2 ;
  - effectifs : n_center, n_cal, n_null ou n_alt < 1 ;
  - paramètres : α ∉ (0, 1), γ_M ≤ 1, minibatch < 1, limites de ressources ≤ 0.
- Si les axes de C sortent de [2, nmax], C devient `UNSUPPORTED`. Les tableaux doivent être float64, finis et non vides ; S doit être non vide, sans doublon, dans [1, nmax].
- **Ressources.** Le pic mémoire théorique est calculé avant l'exécution ; refus au-delà de 8 Gio. Si la durée est dépassée : arrêt à une frontière de partition, `BLOCKED_RESOURCE`, reprise par `--resume`, sans substitution d'algorithme.
- **Budget full (hypothèse).**
  - n·H(H+1)/2 = 6,275e7 paires par coordonnée et par rôle ;
  - moyenne ≈ 6,5e10 par fond ; covariance B30 ≈ 2,9e11 par fond ;
  - total ≈ 7,1e11, soit 0,5–1,5 CPU-h, pic < 2 Gio.
- **Smoke.** N = 239, H = 250, T_fit = 1 000, n_center = n_cal = n_null = n_alt = 40 ; deux fonds ; A, B30, C ; synthétique seul ; un processus, un thread BLAS. Seuls les n diffèrent du full ; pas de balayage ; `claims: none`.
- **trials full.** ≈ 0,79 M lignes, soit 50–55 Mo, gardé en local (§4.1).

## 10. Tests (`tests/test_pca_drift_benchmark.py`, identités déterministes, < 60 s)
1. `mixture_cost` égal à `mixture_multiplier` à 1e−10 ; valeurs du deck ; M > 1 ; refus de γ ≤ 1 et d < 1.
2. Corde affine M(1)–M(20) : a, c > 0, identique pour nmax ∈ {1, 6, 20}.
3. Identité de la KL dans la base propre du même Σ ; contre-exemple où l'ordre des variances diffère de l'ordre des informations.
4. Σ0 = diag(4, 1) tournée de 45° : KL jointe 0,5625 ≠ somme des marginales 0,3394.
5. I_pop_joint : borne DPI, monotonie, non-additivité ; invariance u ↔ z de la KL et du LLR à 1e−12.
6. Scan contre une double boucle à sommes directes (d ∈ {1, 2, 4}, H ≤ 12, tolérance 1e−12) : chaque logL(τ,t), W_t et première alarme ; τ = 1 égal à `log_subgaussian_mixture` ; cas sans alarme, alarme à t = 1, maxima égaux, argmax τ > 1 ; H(H+1)/2 candidats évalués.
7. Bit à bit identique pour B ∈ {1, 3, 7}.
8. `rank_threshold` prédictif : n40/alpha.05 -> r1, borne2/41 ; n2000 -> r99, borne100/2001 ; n1 et n5 à .05 -> CALIBRATION_FAILED. Ex aequo, GE/GT, seuils non finis ; garantie sur maxima échangeables uniquement, aucune garantie historique. Distinguer taux empirique, borne et FPR holdout ; adapter les fixtures sans modifier les paramètres du smoke.
9. `vech_std` sur une matrice connue ; moyenne de y nulle sur l'ensemble de centrage lui-même.
10. Énergie : aᵀMΣ0Mᵀa < aᵀΣ0a sous la rotation alors que la KL jointe est > 0 (analytique).
11. Rendements × 0,01 : λ_LW < 1 mais λ_corr ≥ 1 ; Kaiser et MP sur la corrélation ; MP = `mp_count` ; CPV monotone.
12. `CPV90_OUTSIDE_TOP20` sans plantage ; si k90 ≤ 20, CPV90 reprend le `metric_id` de E1.
13. Identités analytiques pour A, C et B30 ; Σ1 SPD avec termes hors diagonale ; KL plug-in = `meta["info"]`.
14. Top-q = exhaustif = glouton, avec balayage complet de d (k ≤ 12) et gestion des égalités.
15. Covariance exhaustive = force brute (nmax = 6) ; refus de nmax > 20.
16. t7 : étiquettes `T7_PROXY` ; `anytime_valid=False` ; jamais de seuil log γ.
17. Empoisonner calibration, holdout ou alternatives ne change ni base, ni spectres, ni sélection, ni `centering_hash` ; empoisonner `centering` change `centering_hash` seul.
18. Rôles et graines distincts ; régénération identique par clé ; trajectoires communes à toutes les méthodes.
19. Identifiants : S canonique sous permutation ; ids E1 = E2 ; E3 MIX = E2 k20 ; un axe décalé, une autre famille, cohorte ou centrage change l'id ; un seul `metric_id` par agrégat.
20. Permutation des actifs : λ et q̂ égaux à 1e−10.
21. Chaque cas invalide de §9 est refusé.
22. Faux memmap enregistreur : aucun index ≥ 2020 n'est lu ; lignes post-2019 à NaN → fit, q̄ et seuils restent finis.
23. Embargo égal à `_realize_segments` ; Covid → `NOT_EVALUABLE_STANDARD_SPLIT` ; cohorte rétrospective armée au premier jour ≥ 2020-01-01.
24. R1–R5 : alarmes pré-onset conservées, redémarrage, détection pendant l'événement, post-événement, censure, `PATH_TOO_SHORT`.
25. Stress : seules les fenêtres déclarées sont lues ; fenêtre incomplète → issue sans résultat.
26. `DATA_UNAVAILABLE` n'affecte pas le synthétique.
27. Refus d'écraser une sortie, y compris avec `--resume` quand le manifest existe.
28. `--resume` après interruption : octets identiques ; toute altération de l'identité bloque.
29. Deux répertoires neufs : CSV et `identity` identiques ; une autre graine change les agrégats.
30. `--mode smoke` refuse `real` et `both` et n'appelle jamais `read_pre2020_panel`.
31. Colonnes et énumérations exactes ; parseur de S.
32. `check_env` refuse un environnement non conforme (sous-processus) ; le bloc smoke respecte §9.

## 11. Invariants, ownership, collision, déviations
- **Invariants.**
  - E2 : CRLF et SHA-256 préservés sur disque et dans l'index ; aucune écriture dans `results/e2/`.
  - D8 préservé ; DEVIATIONS en ajout seulement ; aucun rerun.
  - Aucun fichier EUROFIDAI, aucun fichier > 50 Mo, aucun chemin serveur dans les fichiers suivis.
- **Ownership.**
  - Fichiers du stream : `experiments/pca_drift_benchmark.py`, `tests/test_pca_drift_benchmark.py`, `configs/pca_drift_benchmark.yaml`, `docs/sections/pca_drift_benchmark.md`, `results/pca_drift_benchmark/smoke_predictive_v2/`, `prompts/plans/plan-28.md`, `prompts/GO-stream-28.md`, `prompts/wrapups/wrapup-28.md`, ainsi que les ajouts à DEVIATIONS.
  - Non touchés : `jepadrift/`, `tools/`, INDEX, prompts 29–31.
- **Collision.** Après GO, la ligne 1 de `28_STREAM_PCA_DRIFT_RUNNER.md` devient `## PROMPT 28-PCA — …` ; E11 reste intact. Le stream 31 attendra {28-PCA, 29, 30, 31} ; une future exécution d'E11 aura la référence `28-e11`.
- **DEVIATIONS (rédigées en français).**
  - `C-pca-covid-retrospective` : cohorte sans embargo, règles R1–R5.
  - `C-pca-benchmark-design` : répertoires, trials normalisé, CLI, s2, objectif plug-in, A sous population, poids de C, centrage de nuisance, énergie EW, recherche exhaustive, corde 1–20, nul D6, fenêtres de stress, mmap, seuil par rang.
- **Langues.** Code, tests, schéma et wrapup en anglais.
- **CLI.** `--config`, `--out` (alias `--output-dir`), `--log-dir`, `--seed`, `--mode smoke|full`, `--dataset synthetic|real|both`, `--resume`. `--mode` remplace `--quick` ; pas d'option `--jobs`.

## 12. Phase B (après GO seulement)
- **Lancement par Codex.** `claude -c -p … --model opus --effort max --remote-control "stream-28"`. Si le CLI refuse cette option avec `-p`, la session s'arrête et le signale ; le flag n'est jamais retiré en silence. Une seule session de Phase B à la fois (limite sur les streams simultanés).
- **Environnement**, depuis la racine du worktree :
```bash
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
```
1. **B0.** `test "$(git rev-parse HEAD)" = e1f80847245b14498e331abda1e3d13cf415ec8f` ; `git status --porcelain` ne liste que `?? prompts/NO-GO-stream-28.md`, plus d'éventuelles sentinelles Codex ; `test "$(sha256sum < results/e2/e2_cells.csv | cut -d' ' -f1)" = e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, puis le même test sur `git show :results/e2/e2_cells.csv`.
2. **Avant tout code** : `prompts/plans/plan-28.md` (ce plan + « Décision GO intégrée ») et `prompts/GO-stream-28.md` (texte Codex verbatim, cadre en français).
3. **Schéma et configuration** : `docs/sections/pca_drift_benchmark.md`, `configs/pca_drift_benchmark.yaml`.
4. **TDD** par groupes de §10 (1–10, 11–21, 22–32). Après chaque groupe : `pytest -q tests/test_pca_drift_benchmark.py -k <groupe>` et `pyflakes` sur les deux fichiers ; pas de `make check` global.
5. **Smoke** dans deux répertoires neufs :
```bash
python experiments/pca_drift_benchmark.py --mode smoke --dataset synthetic --out results/pca_drift_benchmark/smoke_predictive_v2 --log-dir logs/pca_drift_benchmark/smoke_predictive_v2
python experiments/pca_drift_benchmark.py --mode smoke --dataset synthetic --out logs/pca_drift_benchmark/smoke_predictive_v2_repeat/out --log-dir logs/pca_drift_benchmark/smoke_predictive_v2_repeat/log
for f in manifest.json spectra.csv selection.csv calibration.csv trials.csv aggregates.csv issues.csv; do cmp results/pca_drift_benchmark/smoke_predictive_v2/$f logs/pca_drift_benchmark/smoke_predictive_v2_repeat/out/$f || exit 1; done
! python experiments/pca_drift_benchmark.py --mode smoke --dataset synthetic --out results/pca_drift_benchmark/smoke_predictive_v2 --log-dir logs/pca_drift_benchmark/smoke_predictive_v2_refuse
test -z "$(find results/pca_drift_benchmark -type f -size +50M)"
```
6. **Budget** : transmettre à Codex le débit mesuré (`run.log`) et l'extrapolation pour le full ; aucun run full.
7. **Déviations et identifiant** : les deux entrées DEVIATIONS (en français) et la ligne 1 du prompt 28 (D1).
8. **Contrôles finaux**, plus les tests SHA de B0 :
```bash
pyflakes experiments/pca_drift_benchmark.py tests/test_pca_drift_benchmark.py && pytest -q tests/test_pca_drift_benchmark.py
git diff --quiet -- results/e2/e2_cells.csv
test -z "$(git diff -- docs/DEVIATIONS.md | grep -E '^-[^-]')"
grep -qF 'relative gap +0.0528334213 > 0.05' docs/DEVIATIONS.md
test -z "$(git status --porcelain --untracked-files=all | grep -E 'eurofidai')"
```
9. **État attendu**, outre le NO-GO et les sentinelles : ` M docs/DEVIATIONS.md`, ` M prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`, `?? configs/pca_drift_benchmark.yaml`, `?? docs/sections/pca_drift_benchmark.md`, `?? experiments/pca_drift_benchmark.py`, `?? tests/test_pca_drift_benchmark.py`, `?? prompts/GO-stream-28.md`, `?? prompts/plans/plan-28.md`, `?? prompts/wrapups/wrapup-28.md`, `?? results/pca_drift_benchmark/`.
10. **Wrapup** : `prompts/wrapups/wrapup-28.md` en anglais, six sections, sans FPR ni RMST attribué au smoke.
11. **Arrêt** : ni commit, ni push, ni réindexation ; la clôture revient à Codex.

## 13. Décisions closes et blockers
**Arbitrages du NO-GO, appliqués sans exception :**
- D1–D7 : `28-PCA` ; répertoires smoke/full ; CSV de plus de 50 Mo gardés en local ; objectif plug-in, KL de population rapportée à part ; A sous la population ; C équipondéré sous Σ0 ; s2(p) = 2·ln(H/α)/(H·p).
- D8–D14 : centrage vech par un rôle de nuisance ; énergie EW ; recherche exhaustive ≤ 20 ; coût affine principal, M en heuristique ; corde 1–20 ; nul D6 pré-2020 ; fenêtres de stress de §7 ; 2022 aligné sur l'onset, à titre de diagnostic.
- D15–D20 : R1–R5 ; DEVIATIONS en français ; smoke de §9 ; mmap pré-2020 ; balayage 15°/45° différé ; contrôles descriptifs en z.
- Corrections techniques : seuil par rang (§5.4), centrage indépendant (§5.2), espace LLR cohérent (§6.5).

**Blockers réels :**
- (i) Sans procédure `FROZEN.json` (stream 21 suspendu), les lignes réelles restent `BLOCKED_PRE_J4` : c'est un statut attendu.
- (ii) Le full exige l'audit du smoke et l'accord budgétaire de Codex.
- (iii) La Phase B exige un GO explicite.

Aucune autre question n'est ouverte.

## 14. Hors périmètre
Tables, figures et contrats des streams 29–31 ; parallélisme ; Parquet ; GLR ; `ORACLE_PRIOR_SCALE` ; LR à Δ connu ; base de population ; recherche en faisceau ; énergie P3-D ; détecteurs de signes ; toute modification de `jepadrift/`.

## Décision GO intégrée

### Stream 28 — GO Codex après audit unitaire du plan v2

Date : 2026-10-30. Décision prise par Codex dans le périmètre de supervision et d'arbitrage explicitement délégué par le chercheur. Ce document ne constitue ni une approbation de résultats non produits ni une signature personnelle du chercheur.

#### Décision

**GO pour l'implémentation TDD du runner et ses tests, la documentation du schéma et deux exécutions smoke synthétiques.** Aucun GO pour un run full, une évaluation réelle post-2019, un commit, un push, une fusion sur main ou un autre stream.

Source auditée : PLAN.md v2, 365 lignes, SHA-256 `e3633497fb791bf3be336315a7ae553a0d392179d5bfa12b82126338ea2a9e3b`. Base `e1f80847245b14498e331abda1e3d13cf415ec8f`. Le plan canonique est enregistré avant code dans `prompts/plans/plan-28.md`, avec la présente décision intégrée.

#### Clôture des objections du NO-GO

1. Seuil choisi par statistique d'ordre et au plus un nextafter, sans boucle ULP ; validation des petits n, égalités, alpha et maxima non finis.
2. Centrage covariance appris sur le rôle indépendant centering, hashé et figé avant les trajectoires de calibration ; aucun ajustement sur holdout/alternatives.
3. mmap en lecture seule et matérialisation limitée au pré-2020 ; tests des indices effectivement lus ; les cohortes historiques restent bloquées avant J4.
4. Scénario A normalisé par v1.T@Sigma0@v1 pour un SR projeté réel de 4 ; information marginale 16/504 séparée des informations plug-in et jointes.
5. Moyennes, covariances et LLR exprimés dans le même espace z, avec tests d'invariance au blanchiment.
6. Proxy t7, identités scientifiques, bornes, langues et référence Git sont explicités dans v2. Le hash v1 tronqué dans la première revue a été corrigé d'après l'archive (64 caractères) ; aucun octet de l'archive n'a changé.

#### Décisions GO intégrées et précisions normatives

- Les arbitrages D1–D20 de v2 sont retenus avec les restrictions de cette décision. Le scan mélange évalue tous les tau ; ni GLR, ni troncature, ni substitution pour gagner du temps. La covariance jointe n'est jamais une somme marginale ; M n'est jamais un coût exact de délai.
- La normalisation des coefficients est : beta=V.T@Delta, mu=beta/sqrt(lambda), q_plugin=mu**2/2. L'égalité de contrôle de §6.2 porte sur beta, **pas sur q_plugin**. Employer les noms de coordonnées cohérents dans le code et les tests.
- Les colonnes communes de §4.4 s'appliquent aux tables détaillées. Pour trials.csv, le schéma normalisé comprend exactement group_id, role, replicate, first_hit, censored_time, detected, stat_max, pre_onset_alarm et detected_during_event. Les colonnes communes et identités sont retrouvées par les jointures documentées vers calibration/aggregates ; ne pas dupliquer des dizaines de chaînes sur chaque tirage. issue_id est la clé explicite d'issues.csv. Ces précisions doivent figurer dans le schéma avant exécution, sans ambiguïté de jointure.
- Defaults full : N=239, H=250, T_fit=1000, nmax=20, n_center=n_cal=n_null=n_alt=2000. Smoke : seuls ces quatre effectifs deviennent 40. A/B30/C et deux fonds ; seed déterministe pré-déclarée. Aucun tirage réel ou propriétaire dans le smoke, aucune donnée illustrative étiquetée réelle.
- Budget smoke : un processus, threads BLAS/OMP=1, plafond mémoire 8 Gio, limite murale de 30 minutes par invocation du runner, vérifiée aux frontières de partition. Un dépassement produit un état honnête BLOCKED_RESOURCE et un arrêt ; aucun changement de statistique ni de cible scientifique. Les tests utilisent des tailles minuscules et restent hors Monte Carlo de production. Transmettre le coût mesuré et l'extrapolation full, sans le lancer.
- Le .venv partagé et les versions épinglées restent inchangés ; aucune installation. Variables fixées avant NumPy : OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Toutes les commandes Python/tests/Make utilisent ce .venv.
- Schéma à publier : pca_drift_benchmark/2, sept fichiers sous results/pca_drift_benchmark/smoke_predictive_v2/, CSV FAIR, empreintes et règles de référence explicites. Les préfixes E1/E2 et MIX E3/E2 k20 réutilisent les mêmes métriques, sans recalcul. Le schéma n'est scellé pour les consommateurs qu'après audit du code, du smoke et intégration propre sur main.
- Autorisation limitée au titre du nouveau prompt 28-PCA ; ancien E11 intact. Ne pas toucher aux prompts, plans ou fichiers possédés par 29/30/31, ni à tools/check_prompts.py. Le futur Stream 31 traitera la découverte de {28-PCA,29,30,31}.
- DEVIATIONS en français et ajouts uniquement ; préserver l'échec E3/D8. Code, tests, schéma et wrapup en anglais. Aucun chemin personnel dans les fichiers destinés au commit ; pas d'identité supplémentaire ni de commentaire promotionnel.
- E2 conserve sur disque et dans l'index ses CRLF et son SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; aucune écriture dans results/e2/. Aucun fichier EUROFIDAI suivi, aucun fichier >50 Mo proposé au suivi.
- Le processus Claude réalise les contrôles ciblés, le double smoke et son rapport. Codex conserve les contrôles d'intégration make check, la réindexation, les opérations Git et l'autorisation du full ; tous les processus du stream devront être éteints à cette clôture.

#### Livrables et arrêt demandé

Runner, tests unitaires propres, configuration, document de schéma, sept artefacts smoke et hashes, plan/GO/trace NO-GO, déviations justifiées et wrapup anglais aux six sections du projet. Avant de s'arrêter, rapporter les commandes réellement exécutées, résultats, limites, SHA-256 et coût CPU/RSS, avec honnêteté sur les cas non exécutés.

Aucun autre stream n'est amorcé avant le gel du schéma, le smoke audité et l'intégration de 28 sur main. Selon la politique la plus récente, seuls les plans Claude 29, puis 30, puis 31 sont autorisés ensuite, en séquence et avec audits unitaires ; aucune implémentation Claude n'est autorisée. Les intégrations Git restent sérialisées.
