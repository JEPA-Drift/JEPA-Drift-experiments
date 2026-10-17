# Plan — Stream 07 : pipelines transversaux P2-C, P3-C, P3-D, P3-CS, P7 et calibrations

> Exécution : Claude Code (routage INDEX : Opus, max), en session unique, sans sous-agent (précédents des streams 04 à 06). Méthode : `superpowers:executing-plans` en mode natif, `superpowers:test-driven-development` pour chaque tâche, `superpowers:verification-before-completion` avant toute annonce de fin. Cases `- [ ]` pour le suivi.

Date : 2026-10-16. Spécification : `prompts/streams/prompt-07-pipelines.md`. Base : `c9d93f1` (passe de correctifs du stream 06) ou un descendant. Au GO, HEAD = `672ce26` (stream 10, EUROFIDAI), commit local qui n'est pas encore poussé.

Statut : **GO**. La revue `prompts/GO-stream-07.md` (2026-10-16) est intégrée dans ce plan final, section « Décision GO intégrée ».
- (GO Hn) marque l'hypothèse n du plan initial, confirmée par la revue.
- **Étape préalable** (règle `C-plan-recording` ; instruction du GO) : enregistrer ce plan dans `prompts/plans/plan-07.md` avant toute ligne de code.

**Objectif.** Livrer le registre des pipelines transversaux. Chaque pipeline traverse la même pile de détection, et seule la représentation change. Livrer aussi les trois calibrations (inversion de signe, bootstrap de fenêtres porté de R15, treillis exact), ainsi que le contrôle d'identité R15 et les tests sous H₀ et sous dérive forte. Ce stream bloque E1 et E3 (J2).

**Architecture.**
- `jepadrift/monitors/calibration.py` (numpy seul) contient :
  - les deux workers R15, recopiés à l'identique ;
  - le seuil par quantile de R15 ;
  - le tirage de fenêtres nulles, avec ou sans inversion de signe par jour.

  Le treillis exact reste `lattice.select_threshold` (stream 04).
- `jepadrift/monitors/streams.py` reçoit `fraction_stream` (R15, recopiée à l'identique).
- `jepadrift/monitors/eprocess.py` reçoit `log_average_betting_eprocess`, l'e-processus de P3-CS (a).
- `jepadrift/pipelines.py` contient :
  - le registre `PIPELINES[id] = (representation, stream_builder, detector, calibration)` ;
  - `fit_pipeline`, `run_pipeline` et `null_check` ;
  - `composition_for` (R15, à l'identique) et `save_fair_csv`, déplacée depuis le script d'identité ;
  - la CLI.

  C'est le seul module qui réunit représentations et moniteurs. Les représentations y entrent sous forme de tableaux X ou Z.
- `experiments/identity_articleB.py` reçoit la table d'identité R15, écrite dans `results/identity/articleB_R15.csv`.

## Décision GO intégrée

Source : `prompts/GO-stream-07.md` (verdict : **GO**). Les quatorze valeurs par défaut sont confirmées et le contenu du plan ne change pas. Intégration :

| Point de la revue | Intégration dans ce plan |
|---|---|
| Instruction préalable : enregistrer `prompts/plans/plan-07.md` avant toute ligne de code | Statut et Tâche 0 |
| Revérification de la revue : ρ̂ et K_eff, recalculés depuis `load_d2` avec la composition figée de R15, sont identiques au bit près à K = 5 et K = 20, à un ulp près à K = 10 (2,14e-16 en relatif), dans la porte de 1e-12. λ_boot et FPR_boot du CSV de l'Article B sont cohérents | Sonde 1 inchangée |
| HEAD = `672ce26` (stream 10), commit local ; `origin/main` = `c9d93f1`. La plage `origin/main..HEAD` du push couvrira les deux commits. Contrôle de la revue : aucune donnée EUROFIDAI, aucun fichier > 50 Mo | Tâche 0 ; Tâche 9 (4) |
| Modifications étrangères non commitées : `data/derived/MANIFEST.json`, `data/derived/d1_etf4/panel.parquet`, `data/derived/d2_us97/panel.parquet`, `results/data/d1_d2_profile.csv`. `prompts/plans/plan-09.md` n'est pas suivi. **Aucun de ces fichiers n'est jamais indexé.** Le fixture de `tests/test_data_d1_d2.py`, exécuté par `make check`, reconstruit D1 et D2 à l'identique des octets commités | Tâche 0 ; Tâche 9 (3) |
| Fichiers du stream 04 modifiés par ajout seulement (`streams.py`, `eprocess.py`, script et test d'identité, `monitors.md`, journaux d'identité) : relus juste avant chaque édition. `tests/test_monitors.py` et `tests/test_injection.py` restent inchangés et au vert ; `articleB_R01_R08.csv` est réécrit à l'identique | Tâches 1, 3, 8 et 9 |
| (GO H1) à (GO H14) : les quatorze défauts sont confirmés | Marqueurs (GO Hn) |
| Points de vigilance 1 à 5 et risques : endossés | Inchangés |
| Trace de décision | `prompts/GO-stream-07.md` commité avec le stream (Tâche 9) |

## Contexte

- **Consommateurs.**
  - E1 (stream 12) : P2-C sur la grille de K, P3-C (marché plus factoriel, et complet pour F2), P3-D et P7 ; γ ∈ {20, 252}, H_det = 2000. Lectures : anytime-valid pour tous, exacte pour les CUSUM de signe, Article B pour P2-C.
  - E3 (stream 13) : FPR à H ∈ {750, 2000} et ARL₀ contre γ ; Γ^spec contre Γ^op.
  - E4 (stream 19) : P2-C, P3-C, P3-CS.
  - E5 (stream 22) : P3-C et P3-CS face à P5-C, à seuil anytime-valid égal.
  - E6 (stream 23) : P3-D, fenêtres nulles de calib, Γ_z^op.
  - E10 et E11 (streams 27 et 28).
  - Contrats (stream 08) : SHA-256 de `alarms.csv` identiques d'une exécution à l'autre.
- **Lectures** (AGENTS.md) :
  - budget : τ_γ = ln γ / I ;
  - anytime-valid : e-détecteur arrêté à γ, avec ARL₀ ≥ γ ;
  - exacte : ARL₀ calibré à γ ;
  - bootstrap (prompt 07) : FPR α à l'horizon H, sur fenêtres nulles réelles.
- **Briques réutilisées, sans réécriture.**
  - Stream 04, `cusum` : `bilateral_delay_vec`, `strict_cusum_vec`, `cusum_max_bilateral_vec`, `cusum_trajectory_vec`.
  - Stream 04, `eprocess` : `log_edetector`, `log_dictionary_edetector`, `log_subgaussian_mixture`, `first_alarm`, `EDETECTOR_ETA0`.
  - Stream 04, autres modules : `streams.exact_sign_stream`, `lattice.select_threshold`, `gamma.required_threshold`.
  - Stream 05 : `injection.symmetrize`, `inject` et `draw_tau_star` ; `stats.covariance.ledoit_wolf`.
  - Stream 06 : `PCAOrthogonal`, `DegreeZero`, `extract.segment_rows` et `extract.DATASETS`.

## Constats des sondes

Sondes en lecture seule, sans écriture de fichier ; statistiques limitées aux lignes ≤ 2019-12-31, sauf l'identité R15 (sonde 1).

1. **Identité R15.**
   - `load_d2()` est identique au bit près à `R15_panel_logreturns.csv` lu en `round_trip` : mêmes 97 tickers, même ordre.
   - `composition_for(K, 97)` redonne `R15_panel_composition.csv` pour les dix K.
   - Sur le panel complet, l'arithmétique de `run_diagnostics` (l.887–902) redonne `rho_sign_meas` et `K_eff_meas` :
     - K = 5 : identiques au bit près (0.2577415599534342 ; 2.461882379915166) ;
     - K = 10 : ρ̂ diffère d'un ulp (écart relatif 2,14e-16), K_eff est identique au bit près ;
     - K = 20 : identiques au bit près (0.28810195766064206 ; 3.091784464945219) ;
     - sur la grille entière, l'écart relatif reste ≤ 2,19e-16.
   - Avec les graines de R15 (`get_deterministic_seed("boot_calib", 1, i)`), on retrouve λ_boot = 34.2 (même flottant que 34.200000000000003) et FPR_boot = 0,053 pour K = 5. Les 20 000 fenêtres prennent 9,6 s.
2. **D2 avant 2020.** 3774 lignes, dont 2864 rendements exactement nuls (0,78 %) et aucun jour entièrement nul. Les égalités à zéro exigent les pièces de `exact_sign_stream` pour les signes bruts.
3. **Indépendance croisée des signes sur la calib de D2** (941 jours, 3 erreurs-types = 0,0978) :
   - mode factor : 10 paires résiduelles, max |ρ̂| = 0,1308, une paire au-delà ;
   - mode full : 4560 paires, max 0,1555, 13 paires au-delà.

   Le test littéral échoue donc dans les deux modes. En full, il échouerait même sous indépendance, par multiplicité : P ≈ 0,9973^4560 ≈ 4e-6.
4. **Nul D6 sur D2**, 2000 réplications, fenêtres de H = 750 jours, fit sur la calib.
   - Lecture exacte de P3-C canal par canal : δ = 0,1, bilatéral, L = 45, seuil 9,1, niveau 0,043947. Les FPR valent 0,049, 0,0385, 0,038, 0,0415, 0,0395 et 0,0465, tous dans la région à 99 % [0,0321 ; 0,0558].
   - E-détecteur de dictionnaire de P3-C : FPR 0,7075 à γ = 20, 0,001 à γ = 15 000.
   - E-détecteur de P2-C (K = 97, signes bruts) : 0,2935 à γ = 20, 0 à γ = 15 000.
   - E-processus de P3-CS (a) à γ = 20 : 0,003 avec les mises |λ| ≤ 0,4 ; 0,015 en factor et 0,002 en full avec la grille large de (GO H9) (1000 réplications).
   - E-détecteur de P3-CS (b), règle (GO H10) : 0,63 à γ = 20, 0 à γ = 15 000.
5. **F2 forte** : SR = 8, I = 0,12698 nat/jour ; SYM-D2, C synthétique constant (P = 4), K = 6 dans `inject`, γ = 20.

   | pipeline (mode) | H = 750, 60 rép. | H = 2000, 60 rép. | H = 2000, 100 rép. : détection ; délai moyen ; max |
   |---|---|---|---|
   | P3-C (full) | 98,3 % | 100 % | 100 % ; 350 ; 858 |
   | P3-CS (b) (full) | 93,3 % (σ̂ amorcé avant τ*) | 100 % (σ̂ amorcé avant τ*) | 100 % ; 462 ; 1292, règle (GO H10) |
   | P3-CS (a), e-processus à grille large (full) | — | — | 100 % ; 1185 ; 1755 |
   | P3-CS (a), CUSUM standardisé à seuil par inversion de signe (full) | — | — | 100 % ; 1157 ; 1734 |
   | P7 | 100 % | 100 % | 100 % ; 13 ; 46 |
   | P2-C (K = 97) | 28,3 % | 76,7 % | — |

   Variantes écartées (H = 2000, 40 rép.) :
   - e-processus (a) à mises |λ| ≤ 0,4 : 35 % (full) et 2,5 % (factor) ;
   - CUSUM (a) non standardisé : 17,5 % (full) ;
   - P3-C en mode factor : 85 % à H = 750.
6. **P3-D**, blanchi par la Σ̂ Ledoit–Wolf de la calib.
   - Moyenne de q_t : 0,024 sur la calib et 0,469 sur le pretrain en factor ; −0,332 et 9,47 en full. Γ^spec(calib) vaut 1,56 et 2,73.
   - Fenêtres de 2005–2019 (H = 750) : λ_req = 2026,8 et 19 911,7, contre λ_iid = 10,61 et 8,49, soit Γ^op = 191 et 2346. C'est le régime de 2008.
   - Fenêtres de la calib seule :
     - H = 250 : λ_req = 76,7 et 201,1, λ_iid = 9,03 et 7,22, soit Γ^op = 8,49 et 27,87 ;
     - H = 500 : Γ^op = 7,71 et 25,14.
7. **Bootstrap P2-C** (lignes 2005–2019, 2525 fenêtres distinctes, N_cal = 20 000, 2000 fenêtres tenues à part ; région à 99 % de 5 % : [0,0374 ; 0,0626]).

   | fond | K | λ_boot | FPR | durée |
   |---|---|---|---|---|
   | brut | 5 | 36,305 | 0,0405 | 10,6 s |
   | brut | 20 | 20,05 | 0,056 | 14,1 s |
   | brut | 97 | 21,795 | 0,055 | 49,8 s |
   | D6 | 5 | 29,0 | 0,0525 | 10,5 s |
   | D6 | 20 | 33,25 | 0,056 | 14,0 s |
   | D6 | 97 | 26,887 | 0,0545 | 32,1 s |

   Un seuil calibré sur le brut ne vaut donc pas pour un fond D6 : 20,05 contre 33,25 à K = 20.
8. **Vectorisation.** Les maxima des 3905 fenêtres distinctes se calculent en 0,4 s par `cusum_max_bilateral_vec`, au bit près égaux au worker scalaire.
9. **Lecture `randomization` de P3-CS (a) sous D6** (factor, H = 750, B = 2000, 2000 réplications, trois graines de calibration) : λ = 77,90, 77,65 et 77,34 ; FPR = 0,0435, 0,0475 et 0,0465. Tous sont dans la région à 99 % de 5 %, sans bruit de calibration [0,0374 ; 0,0626] comme avec [0,0322 ; 0,0678].

## Décisions

| Question | Décision | Raison |
|---|---|---|
| Registre | `PIPELINES[id] = (representation, stream_builder, detector, calibration)`, quatre fonctions par pipeline, qui aiguillent selon `spec["reading"]` | Forme du prompt (item 1) |
| Spécification | `make_spec(pipeline, **kw)` complète les défauts de `DEFAULTS[pipeline]`. Elle lève `ValueError` sur une clé ou une lecture inconnue, et sur une lecture exacte qui n'a pas un seul canal. `run_id(spec)` = 16 premiers hex du SHA-256 de `json.dumps(spec, sort_keys=True)` | Toute la configuration entre dans `run_id`, ce qui rend les lignes traçables |
| (GO H5) Ajustement | `fit_pipeline(spec, X_fit, splits, key=None) -> state` : la représentation est ajustée sur `splits["calib"]` de `X_fit`, puis la calibration tourne sur les lignes nulles de `X_fit`. `run_pipeline(state=None)` ajuste sur `data`, mais refuse un enregistrement injecté de τ* < fin de calib | Prop. « Absorption » ; consigne de `interface_Z.md` |
| Exécution | `run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None) -> DataFrame` :<br>• `data` est X (T, N) float64, ou Z, un dict `{"z_odd", "z_even"}` d'une représentation déjà appliquée ;<br>• une ligne par enregistrement ;<br>• flux empilés par paquets de `CHUNK = 64` enregistrements, détecteur vectorisé ;<br>• `n_jobs` > 1 répartit les paquets (`ProcessPoolExecutor.map`, ordre conservé) | Item 1 ; « résultats identiques quel que soit le nombre de processus » |
| `alarms.csv` | Colonnes `run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold, reading`.<br>• H₀ : `family = "H0"` et `tau_star` = début de surveillance.<br>• `seed` = clé entière jointe par « - ».<br>• `threshold` = γ (anytime-valid) ou λ (CUSUM).<br>Écriture par `save_fair_csv` ; JSON `runs` adjacent (`run_id` → spec et résumé d'état : seuils, ρ̂, K_eff, Γ^op, σ̄, test d'indépendance) | Colonnes du prompt ; un nombre rapporté doit se rattacher à un CSV |
| (GO H1) Délai | `delay = alarm_index − tau_star + 1`, soit le nombre de jours surveillés jusqu'à l'alarme incluse (T_γ du Lemme 1, convention d'E2). NaN si aucune alarme dans H | Comparaison mesuré/prévu d'E1 avec `floors` |
| Remise à zéro | La surveillance démarre à `tau_star` avec un état nul (pire cas de Lorden). Seuls la référence H_ref de P2-C bootstrap et les statistiques figées de la calib lisent avant `tau_star` | Glossaire (ADD) |
| Graines | `SeedSequence` uniquement.<br>• calibration : `key + [0]` ;<br>• tirage i du bootstrap P2-C : `key + [1, i]` ;<br>• pièces d'un enregistrement : `[*seed, 7]`.<br>`key` par défaut : `[7, int(run_id[:8], 16)]` | AGENTS.md ; indépendance vis-à-vis du découpage et du nombre de processus |
| (GO H2) Lectures anytime-valid | Les e-détecteurs CUSUM de `eprocess` pour P2-C, P3-C et P3-CS (b) ; un e-processus pour P3-CS (a) ; le CUSUM du LLR gaussien à ln γ pour P7 | Prop. « floors » (a) ; items 2, 4 et 6 |
| (GO H3) Cibles sous H₀ | Garantie propre à chaque lecture (table ci-dessous). Les cibles « ≤ » sont testées de façon unilatérale | Les garanties anytime-valid sont des inégalités |
| (GO H12) Portages | Recopie à l'identique (`ast.get_source_segment`, test d'octets) :<br>• `fraction_stream` (R15 l.368–370) → `monitors/streams.py` ;<br>• `worker_null_window_real` et `worker_race_h1_real` (l.431–478) → `monitors/calibration.py` ;<br>• `composition_for` (l.409–426) → `pipelines.py`, avec `MASTER_SEED = 42` (l.201) ;<br>• `get_deterministic_seed` (l.377–394) → script d'identité ;<br>• `save_fair_csv` → `pipelines.py`, importée par le script d'identité | Item 2 ; `monitors` ne peut importer ni `pipelines` ni hashlib |
| Langue | Anglais : code, docstrings, `docs/sections/pipelines.md`, wrapup, commit. Français : `docs/DEVIATIONS.md` et ce plan | Règles du projet |

**Lectures et garanties** (`docs/sections/pipelines.md`)

| lecture | `threshold` | garantie sous H₀ | cible des tests sous H₀ |
|---|---|---|---|
| `anytime-valid`, e-détecteur (P2-C, P3-C, P3-CS b) | γ (alarme dès log M ≥ log γ) | ARL₀ ≥ γ [Shin, Ramdas & Rinaldo, 2024] ; P₀(alarme ≤ H) ≤ H/γ (décomposition de Lorden) | ≤ borne haute de la région à 99 % de H/γ, à γ = 20H |
| `anytime-valid`, e-processus (P3-CS a) | γ | P₀(sup M ≥ γ) ≤ 1/γ [Ville, 1939] | ≤ borne haute de la région à 99 % de 1/γ, à γ = 20 |
| `anytime-valid` (P7) | ln γ (CUSUM du LLR) | ARL₀ ≥ γ sous le seul modèle gaussien i.i.d. de Σ̂ | aucune (borne) |
| `exact` (P3-C, un canal) | seuil du treillis (point milieu) | FPR(H) = niveau exact, ou ARL₀ = γ | région bilatérale à 99 % du niveau exact |
| `bootstrap` (P2-C, P3-D) | λ, quantile des maxima nuls | FPR(H) ≈ α sur la population de fenêtres | région bilatérale à 99 % de α, bruit de calibration inclus |
| `randomization` (P3-CS a) | λ, quantile des maxima à signes inversés | FPR(H) ≈ α ; exacte conditionnellement aux modules sous symétrie, sans levier | région bilatérale à 99 % de α, bruit de calibration inclus |
| `budget` | — | τ_γ = ln γ / I (Lemme 1) | analytique (`floors`), sans moniteur |

La région à 99 % est p ± z√(p(1−p)/n), avec z = 2,5758293035489004 (précédent du stream 04). Pour une lecture calibrée sur n_cal tirages nuls (N_cal ou B), la demi-largeur devient z√(p(1−p)(1/n + 1/n_cal)). La variance du niveau atteint par un quantile empirique est en effet ≈ α(1−α)/n_cal. Le recouvrement des fenêtres reste ignoré, et le CSV de la CLI le dit.

**Pipelines**

| id | représentation | flux | détecteur | calibration | lectures |
|---|---|---|---|---|---|
| P2-C | colonnes `composition_for(K, N)` de X (K = N par défaut) | bootstrap : `fraction_stream` des signes recentrés (médiane et écart-type sur les H_ref jours qui précèdent τ*, lignes du worker) ; anytime-valid : x = 2·moyenne des `exact_sign_stream` bruts | bootstrap : CUSUM bilatéral strict, δ = 0, `bilateral_delay_vec` ; anytime-valid : `log_edetector(x, "cusum")` | (GO H4) N_cal appels de `worker_null_window_real` sur les lignes nulles, puis `bootstrap_threshold` ; `sign_diagnostics` donne ρ̂_signe, K_eff_meas et K_eff_ana | bootstrap (défaut), anytime-valid |
| P3-C | `PCAOrthogonal(K, mode, shrinkage)` ; `channels` ∈ {all, market, residual, [k]} | x = 2·`exact_sign_stream(z_odd[:, cols])` | anytime-valid : `log_dictionary_edetector(x, "cusum")`, poids égaux sur tous les canaux ; (GO H6) exacte : CUSUM bilatéral strict, δ = 0,1, sur un canal ; (GO H7) option `mixture_s2` | exacte : `select_threshold(α, H=H)`, ou `(1/γ, H=None)` | anytime-valid (défaut), exact |
| P3-D | `PCAOrthogonal`, tête paire | (GO H8) q_t = (Σ_{k ∈ résiduel} z_even[t, k] − D)/√(2D) | CUSUM unilatéral strict, δ = 0,5, `strict_cusum_vec` | toutes les fenêtres de longueur H de la calib, puis `required_threshold(·, 0.5, α, "fpr", H)` ; λ_iid sur q i.i.d. χ²_D ; Γ^op = λ_req/λ_iid | bootstrap |
| P3-CS | `DegreeZero(b, K, mode)` ; `variant` ∈ {a, b}, b par défaut | (a) pivots z_odd ∈ [−1, 1] ; (a, randomization) pivots / RMS de calib ; (b) signes exacts et ‖Px‖ = z_even | (GO H9) (a) `log_average_betting_eprocess` ; (a, randomization) max sur directions et côtés de `bilateral_delay_vec(δ = 0)` ; (GO H10) (b) e-détecteur CUSUM à mise prévisible | randomization : `null_windows(flip=True)`, B = 2000, puis `bootstrap_threshold` ; (b) σ̄ | anytime-valid (a, b), randomization (a) |
| P7 | Σ̂ = `ledoit_wolf(X_fit[calib])[0]` | (GO H11) ℓ_t = w_tᵀx_t − ½w_tᵀΔ_t, w_t = Σ̂⁻¹Δ_t, Δ_t = `record["delta"]` | `cusum_trajectory_vec(ℓ, 0)`, puis `first_alarm(S, γ)` (S ≥ ln γ) | aucune | anytime-valid (borne) |

**Constantes de `pipelines.py`** :
- `H_REF, H_DET, N_CAL, TARGET_FPR = 500, 750, 20000, 0.05` (R15 l.194–199) ;
- `B_FLIPS = 2000` (prompt, item 6) ;
- `HALF_LIFE = 20` et `STAKE_CAP = 0.5` (prompt, item 6) ;
- `PIVOT_BETS = (0.1, 0.25, 0.5, 0.9)` (GO H9) ;
- `SIGN_DELTA = 0.1` (P1-C/C) et `ENERGY_DELTA = 0.5` (prompt, item 5) ;
- `GAMMA = 20.0`, `CHUNK = 64`, `Z99 = 2.5758293035489004`.

## Hypothèses — confirmées au GO (les quatorze défauts)

- **(GO H1) — Convention de délai.** Défaut : `delay = alarm_index − tau_star + 1`, soit T_γ du Lemme 1, la convention d'E2 et de `floors`. Les ports R15 gardent en interne leur délai en base 0, comme `bilateral_delay`. Alternative : base 0, comme l'Article B.
- **(GO H2) — Nature des lectures anytime-valid.** Défaut : e-détecteurs CUSUM pour P2-C, P3-C et P3-CS (b). Ce sont les e-détecteurs de la Prop. « floors » (a), d'où ARL₀ ≥ γ. Défaut aussi :
  - e-processus pour P3-CS (a), comme le prompt l'écrit ;
  - CUSUM du LLR à ln γ pour P7.

  Le prompt dit « e-processus » dans la propriété clé et « e-détecteur » à l'item 2 ; le défaut suit l'item 2 et le glossaire. Alternative : e-processus sans redémarrage pour toutes les lectures, d'où FPR ≤ 1/γ à tout horizon. Les délais ne seraient alors plus comparables aux planchers de l'e-détecteur CUSUM.
- **(GO H3) — Cibles des tests sous H₀.** Sonde 4 : à γ = 20, un e-détecteur dépasse 1/γ sur 750 jours (0,71 et 0,29), comme son ARL₀ le permet. Défaut :
  - (i) lecture exacte de P3-C canal par canal, région bilatérale du niveau du treillis : c'est le test net du Lemme 2 sur D6 ;
  - (ii) e-détecteurs à γ = 20H, contre la borne H/γ = 5 % ;
  - (iii) e-processus de P3-CS (a) à γ = 20, contre 1/γ ;
  - (iv) bootstrap et randomization : région bilatérale de α, avec la demi-largeur z√(α(1−α)(1/n + 1/n_cal)) (sondes 7 et 9).

  Alternative pour (ii) : tester l'ARL₀ ≥ γ (moyenne censurée), qu'E3 mesurera de toute façon.
- **(GO H4) — Bootstrap P2-C.**
  - Fenêtres nulles tirées dans les lignes pré-surveillance (pretrain jusqu'à la fin de la calib) de `X_fit` : avant J4, R15 lisait le panel complet.
  - Une `SeedSequence` par tirage, à la place des clés MD5 de R15.
  - `composition_for` garde la graine MD5 % 2³² de R15 : c'est la composition figée, recopiée à l'identique.
  - ρ̂_signe et K_eff sont calculés sur ces mêmes lignes, avec l'arithmétique de R15.
  - Pour la lecture anytime-valid, les signes bruts sont exacts : les zéros sont tranchés par pièce.

  Alternative : panel complet, interdit avant J4.
- **(GO H5) — Données d'ajustement.** `X_fit` est fourni par l'appelant et doit être sans dérive. Pour les contrôles D6 (tests, CLI), `X_fit` est une symétrisation indépendante de celles des réplications : W ne dépend pas des signes surveillés, ce qui garde exact le Lemme 2. La sonde 7 montre qu'un seuil P2-C calibré sur le brut ne vaut pas pour D6. Le test bootstrap P2-C suit le protocole de R15 (brut sur brut).
- **(GO H6) — Lecture exacte de P3-C.** Défaut : canal unique ; CUSUM bilatéral strict de δ = 0,1 sur le signe exact, règle `at_or_below`. Le seuil vient de `select_threshold(α, H=H)` si `alpha` est donné, sinon de `select_threshold(1/γ, H=None)`. Pas de lecture exacte multi-canal : la dépendance entre canaux interdit un niveau exact. Alternative : Bonferroni, de niveau ≤ α mais non exact.
- **(GO H7) — Option mélange de P3-C.**
  - `mixture_s2` est fourni par l'appelant, sans valeur par défaut.
  - Le test d'indépendance est littéral : |ρ̂| < 3/√T sur toutes les paires résiduelles des signes de la calib. Un échec lève `ValueError`.
  - Combinaison : log((|marché|/D)·M_marché + (|résiduel|/D)·L_résiduel).

  Constat de la sonde 3 : le test échoue sur D2 dans les deux modes. Alternative : correction de multiplicité, par exemple Bonferroni sur les paires.
- **(GO H8) — P3-D.**
  - Colonnes résiduelles seules.
  - Fenêtres nulles : toutes les fenêtres de longueur H de la calib, énumérées sans tirage.
  - λ_iid : N_cal trajectoires i.i.d. (χ²_D − D)/√(2D) tirées par `rng.chisquare`.
  - Critère de FPR à l'horizon H seulement ; H > longueur de la calib lève `ValueError`.

  Sonde 6 : sur les fenêtres de 2005–2019, Γ^op vaudrait 191 et 2346, à cause de la non-stationnarité. Alternative : `null_rows="pre_monitor"`, disponible en option.
- **(GO H9) — P3-CS (a).**
  - L'e-processus est la moyenne sur les mises ±`PIVOT_BETS` et sur les directions de Π(1 + λ s_{t,k}).
  - Le CUSUM « à design fixe » est le maximum, sur directions et côtés, du CUSUM bilatéral δ = 0 des pivots divisés par leur RMS de calib : les poids sont figés.
  - Seuil par inversion de signe : B = 2000 fenêtres nulles des lignes pré-surveillance, un signe par jour commun à toutes les directions, ce qui préserve leur dépendance.

  Sonde 5 : les pivots bruts sont petits (médiane |p| = 0,057 en full). Les mises |λ| ≤ 0,4 et le CUSUM non standardisé ne détectent F2 qu'à 35 % et 17,5 %, contre 100 % avec ce défaut. Alternative : grille du stream 04 et pivots bruts.
- **(GO H10) — P3-CS (b).**
  - σ̄ = médiane de ‖Px_t‖ sur la calib ; c_j = 2η₀_j·σ̄, η₀ ∈ `EDETECTOR_ETA0`. Un jour médian, la mise vaut donc celle de P3-C.
  - σ̂ repart de σ̄ au début de la surveillance, puis suit une moyenne exponentielle de demi-vie 20 ; la mise est λ_{t,j} = min(0,5 ; c_j/σ̂_{t|t−1}).
  - E-détecteur CUSUM à deux côtés, moyenne sur directions et magnitudes. Il est calculé sans nouveau code de moniteur : `log_dictionary_edetector(Y, eta0=(0.25,))` sur Y = 2λ_t·x_t ∈ [−1, 1] donne les facteurs 1 ± λ_t x_t.
  - (b) est la variante par défaut de P3-CS en lecture anytime-valid.

  Alternative : σ̂ amorcé sur les jours antérieurs à τ*. La sonde 5, faite avec cet amorçage, donnait 100 % ; délai moyen 446 et max 1040, contre 462 et 1292 avec le défaut.
- **(GO H11) — P7.** Σ̂ est le Ledoit–Wolf des lignes de calib de `X_fit`, la covariance de l'injecteur. Δ_t vient de l'enregistrement (`delta` renvoyé par `inject`, découpé à partir de τ*). La reconstruction depuis `tau_star.json` est reportée : un produit B·direction ne redonne pas `direction_sha256` au bit près. Seuil ln γ ; P7 est rapporté comme borne seulement.
- **(GO H12) — Emplacement des portages et périmètre de l'identité.** Emplacements selon la table des décisions. L'identité R15 est étendue, dans le script, au-delà de ρ̂ et K_eff, pour K ∈ {5, 10, 20} :
  - λ_boot et FPR_boot, avec les graines de R15 ;
  - DetRate et ADD de la course à c = 0,25.

  Dans les tests : partie sans aléa, plus λ_boot et FPR_boot à K = 5 (environ 11 s). Le panel complet 2005–2025 n'y sert qu'à reproduire l'Article B, comme R01 au stream 04. Alternative : ρ̂ et K_eff seuls, comme le prompt.
- **(GO H13) — Test F2.**
  - C synthétique constant (N × 4, gaussien) sur SYM-D2 ; H = 2000, γ = 20 ; 50 réplications empilées.
  - 100 % exigé pour P3-C (full), P3-CS (b) (full) et P7.
  - ≥ 90 % pour les deux lectures de P3-CS (a) : la queue des délais atteint 1755 jours sur 2000.
  - P2-C est exclu, car F2 est une dérive de largeur (sonde 5 : 77 %).

  Alternative : 100 % pour tous, au risque de faire échouer le test selon les graines.
- **(GO H14) — Hors périmètre et sorties.**
  - Variante « rangs » de P3-CS reportée : le pivot de rangs n'a pas de ‖Px‖ pour la mise de (b).
  - Les sorties de la commande de vérification de la CLI (P3-C, `d2_us97`, 500 réplications) sont commitées sous `results/pipelines/` et `logs/pipelines/`.

## Contraintes globales

- **Isolation.**
  - `jepadrift/monitors/*.py` n'importe que numpy, math, fractions et `jepadrift.monitors` ; `test_monitors_import_numpy_only` lit déjà tout le dossier.
  - `pipelines.py` est le seul module qui importe à la fois des représentations et des moniteurs.
  - Les moniteurs reçoivent des tableaux, jamais des objets `Representation`.
- **Aléa.** `SeedSequence` uniquement, aucun état global. Le résultat ne dépend ni de `n_jobs` ni du découpage des enregistrements (test).
- **Environnement.** OMP, MKL et OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE et PYTHONHASHSEED = 42 ; `pipelines.py` les fixe avant d'importer numpy, sur le modèle d'`extract.py`. Interpréteur : `.venv/bin/python`. `make` s'exécute après `source .venv/bin/activate`.
- **Fenêtre de surveillance avant J4.** Tests et CLI : lignes du premier jour de pretrain au 2019-12-31 seulement. Seule l'identité R15 lit 2020–2025, pour la reproduction (GO H12).
- **Entrées et sorties.** CSV lus avec `float_precision='round_trip'` et écrits par `save_fair_csv`.
- **Code nouveau.** Aucun commentaire, sauf `# ponytail:` ; docstrings d'une ligne ; aucune marque d'IA ; aucun `# noqa`. Les portages gardent leur texte.
- **Commit.** Conventional Commits, sans trailer. Indexation par chemins explicites, jamais `git add .` ni `-A` ; aucun `__pycache__`.

## Points de vigilance (Review Focus)

1. **Absorption.** `run_pipeline(state=None)` avec un enregistrement injecté de τ* < fin de calib → `ValueError`. Les tests et la CLI ajustent sur un `X_fit` sans dérive (Tâche 2).
2. **Anticipation.** Perturber les lignes ≥ t ne change ni les flux ni les mises jusqu'à t. Perturber les lignes antérieures à τ* (hors fenêtre H_ref de P2-C bootstrap) ne change aucune alarme. Les mises de P3-CS (b) ne lisent que les lignes < t (Tâches 2 et 5).
3. **Ex aequo.** Pièces par enregistrement, sur clé ; D2 compte 2864 zéros avant 2020. Le test nul de P2-C anytime-valid les traverse ; deux exécutions sont identiques (Tâches 3 et 6).
4. **Bornes de fenêtre** → `ValueError`, jamais de troncature silencieuse :
   - τ* < H_ref pour P2-C bootstrap ;
   - τ* + H > T ;
   - H > nombre de lignes nulles disponibles ;
   - données non finies (Tâches 2 et 4).
5. **Option mélange.** Un test d'indépendance en échec → `ValueError`, jamais de repli silencieux (Tâche 6).

## Fichiers

- **Créés** :
  - `jepadrift/pipelines.py`, `jepadrift/monitors/calibration.py` ;
  - `tests/test_pipelines.py`, `docs/sections/pipelines.md` ;
  - `results/identity/articleB_R15.csv` ;
  - `results/pipelines/alarms_P3-C_d2_us97_null.csv` et `runs_P3-C_d2_us97_null.json` ;
  - `logs/pipelines/null_P3-C_d2_us97.log` ;
  - `prompts/plans/plan-07.md`, `prompts/wrapups/wrapup-07.md`.
- **Fourni par le chercheur, commité avec le stream** : `prompts/GO-stream-07.md`.
- **Modifiés** :
  - `jepadrift/monitors/streams.py` : `fraction_stream` ;
  - `jepadrift/monitors/eprocess.py` : `log_average_betting_eprocess` ;
  - `experiments/identity_articleB.py` : table R15 et `get_deterministic_seed` ; `save_fair_csv` y est désormais importée de `pipelines.py` ;
  - `tests/test_identity_articleB.py` : `PORTS` et tests R15 ;
  - `docs/sections/monitors.md` : portages et API ;
  - `docs/DEVIATIONS.md` : entrées ajoutées en fin de fichier ;
  - `logs/identity/identity_articleB_venv.log`.
- **Non touchés** : `Makefile`, `requirements.*`, `AGENTS.md`, `jepadrift/representations/*`, `jepadrift/injection.py`, `jepadrift/data_loader/*`. `results/identity/articleB_R01_R08.csv` est réécrit à l'identique ; un `git diff` vide est attendu.

---

### Tâche 0 — Préconditions
- [x] Intégrer `prompts/GO-stream-07.md` dans la section « Décision GO intégrée » ; (Hn) remplacé par (GO Hn).
- [x] Enregistrer ce plan dans `prompts/plans/plan-07.md`, avant toute ligne de code.
- [ ] `git log --oneline -3` et `git status --short` : HEAD attendu `672ce26` ou un descendant. Fichiers étrangers connus au GO :
  - `data/derived/MANIFEST.json`, `data/derived/d1_etf4/panel.parquet` et `data/derived/d2_us97/panel.parquet` (modifiés) ;
  - `results/data/d1_d2_profile.csv` (modifié) ;
  - `prompts/plans/plan-09.md` (non suivi).

  Pour ces fichiers et tout autre fichier non commité d'un autre stream :
  - ne jamais les indexer ;
  - relire `docs/DEVIATIONS.md` juste avant de l'éditer ;
  - ne lancer que des tests ciblés tant que les fichiers étrangers sont présents.
- [ ] Référence « avant » : `pytest -q tests/test_monitors.py tests/test_identity_articleB.py`, tout au vert.

### Tâche 1 — Portages R15 et briques de calibration

**Interfaces.**
- `streams.fraction_stream(eps)` : eps (K, T), renvoie (T,).
- `eprocess.log_average_betting_eprocess(x, lam)` : x (..., T, K) ∈ [−1, 1], lam (J,) avec |lam| < 1, renvoie (..., T). C'est le log de la moyenne sur (j, k) de Π_{s≤t}(1 + lam_j x_{s,k}) ; `ValueError` sinon.
- `calibration.worker_null_window_real(rng, eps_K_full, H_ref, H_det) -> float` et `calibration.worker_race_h1_real(rng, eps_K_full, H_ref, H_det, c, lam_boot) -> int`, recopiés à l'identique.
- `calibration.bootstrap_threshold(null_maxima, alpha) -> float` : `float(np.quantile(null_maxima, 1 - alpha))` (R15 l.1062). `ValueError` si alpha ∉ (0, 1) ou si les maxima sont vides.
- `calibration.null_windows(x, length, n, rng, flip=False)` : x (T, ...), renvoie (n, length, ...).
  - Tirage fenêtre par fenêtre : le début (`rng.integers(0, T − length + 1)`), puis, si `flip`, un signe de Rademacher par jour.
  - `ValueError` si length > T ou si n < 1.

**Tests.**
- [ ] `tests/test_identity_articleB.py::PORTS` : ajouter (R15 → `monitors/streams.py`, `fraction_stream`), (R15 → `monitors/calibration.py`, les deux workers), (R15 → `pipelines.py`, `composition_for`) et (R15 → `experiments/identity_articleB.py`, `get_deterministic_seed`). Déplacer l'entrée `save_fair_csv` vers `jepadrift/pipelines.py`.
- [ ] Créer `tests/test_pipelines.py` : docstring `"""Tests for jepadrift.pipelines and jepadrift.monitors.calibration (pytest)."""`. Helpers :
  - `_rng(*key)` = `default_rng(SeedSequence([7, *key]))` ;
  - `_d2_pre()`, qui renvoie `(X, dates, splits)` sur les lignes allant du premier jour de pretrain au 2019-12-31, avec `splits = split_rows(dates, articleB.load_splits("d2_us97"))`.
- [ ] `test_null_windows_draw_order_and_flip` :
  - un appel n = 10 égale au bit près la concaténation d'appels n = 4 puis n = 6, avec la même suite de générateur ;
  - avec `flip`, |w| égale la fenêtre non inversée au bit près, et w/x est constant sur chaque jour ;
  - erreurs de bornes.
- [ ] `test_bootstrap_threshold_rule` : égalité avec `np.quantile(m, 0.95)` ; erreurs.
- [ ] `test_average_betting_eprocess` :
  - égalité à 1e-12 avec le log de la moyenne des `exp(log_betting_eprocess(x[..., k], lam_j))` ;
  - Ville : 2000 trajectoires de pièces ±1, T = 500, mises `PIVOT_BETS` ; la part qui atteint 20 reste ≤ 0,05 + 3 erreurs-types ;
  - |lam| ≥ 1 → `ValueError`.
- [ ] Échec attendu → implémentation → succès, avec `pytest -q tests/test_pipelines.py tests/test_identity_articleB.py -k "ported or null_windows or bootstrap_threshold or average_betting"`.

### Tâche 2 — Noyau de `pipelines.py` et P3-C

**Interfaces.**
- Constantes de la table des décisions et `COLUMNS`.
- `split_rows(dates, splits) -> {"pretrain", "calib", "pre_monitor"}` : plages [start, stop) calculées par `extract.segment_rows`. `pre_monitor` va du premier jour de pretrain au dernier jour de calib.
- `make_spec(pipeline, **kw) -> dict` et `run_id(spec) -> str`.
- `fit_pipeline(spec, X_fit, splits, key=None) -> state`.
- `run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None) -> DataFrame`. Un enregistrement est `{"seed": [int, ...], "tau_star": int, "family": str}`, plus `"delta"` pour P7.
- `PIPELINES["P3-C"]` : défauts `K="mp"`, `mode="factor"`, `shrinkage="ledoit_wolf"`, `channels="all"`, `reading="anytime-valid"`, `gamma=20.0`, `alpha=None`, `H=750`, `mixture_s2=None`.

**Tests** (fit sur la calib de `_d2_pre()`, lignes brutes, records H₀ à τ* tirés dans `pre_monitor`).
- [ ] `test_alarms_schema_one_row_per_record` :
  - colonnes = `COLUMNS` ; une ligne par enregistrement ; `run_id` unique et égal à `run_id(spec)` ;
  - `alarm_index` vaut −1 ou appartient à [τ*, τ* + H) ;
  - `delay` = alarm − τ* + 1, ou NaN ; `detected` = (alarm ≥ 0) ;
  - `threshold` = γ en anytime-valid ;
  - en exacte, `threshold` = `select_threshold(0.05, H=750, delta=0.1, sided=2)["threshold"]` ;
  - `onset_info` vide → cadre vide, colonnes `COLUMNS` ;
  - `out` écrit un CSV qui, relu en `round_trip`, égale le cadre.
- [ ] `test_parallel_and_partition_invariance` : huit enregistrements. `n_jobs=1` et `n_jobs=2` donnent des cadres égaux (`DataFrame.equals`), de même que [0:3] + [3:8] contre [0:8].
- [ ] `test_x_and_z_inputs_agree` : `run_pipeline` sur X et sur `state["rep"].transform_panel(X)` (dict) donne les mêmes lignes. Le test est étendu à P3-D et P3-CS aux Tâches 4 et 5.
- [ ] `test_guards_and_monitor_reset` :
  - τ* + H > T, données non finies, lecture exacte multi-canal, clé inconnue → `ValueError` ;
  - `state=None` avec un enregistrement `family="F1"` de τ* < fin de calib → `ValueError` ;
  - perturber les lignes < τ* ou ≥ τ* + H laisse les lignes d'alarmes inchangées.
- [ ] Échec attendu → implémentation → succès.

### Tâche 3 — P2-C et identité R15

**Interfaces.**
- `pipelines.composition_for(K, K_max)` et `MASTER_SEED = 42`, recopiés à l'identique.
- `pipelines.sign_diagnostics(eps_K) -> {"rho_sign": ..., "K_eff_meas": ..., "K_eff_ana": ...}` : eps_K (K, T), arithmétique de R15 l.887–902. ρ̂ = 0 si K = 1.
- `PIPELINES["P2-C"]` : défauts `K=None` (= N), `reading="bootstrap"`, `H_ref=500`, `H=750`, `alpha=0.05`, `N_cal=20000`, `gamma=20.0`, `null_rows="pre_monitor"`.
  - Flux bootstrap : lignes du worker, avec un début fixé, sur [τ* − H_ref, τ* + H).
  - État : `cols`, `threshold`, `diagnostics`.
- `identity_articleB.get_deterministic_seed` (à l'identique) et `identity_articleB.r15_rows(ks=(5, 10, 20), bootstrap=True, race=True) -> DataFrame`, avec les colonnes `COLUMNS` de l'identité et `input = "d2_loader"`. Cellules :
  - `R15_panel_composition` : `position_j`, une par position ;
  - `R15_panel_diagnostics` : `rho_sign_meas`, `K_eff_meas`, `K_eff_ana`, `lambda_boot`, `FPR_boot` ;
  - `R15_cross_sectional_race` : `DetRate`, `ADD` à c = 0,25.

  Le calcul suit R15 : `k_index` dans (1, 5, 10, 20, …), graines `("boot_calib", k, i)`, `("fpr_window", k, i)` et `("race_h1", k, 1, i)`, N_CAL = 20 000, N_RACE = 2000, porte `REL_TOL`.
- `identity_articleB.main` écrit en plus `results/identity/articleB_R15.csv` (en remplaçant les lignes de son environnement, `--out-r15`) et des lignes R15 dans le journal. Le verdict couvre aussi ces lignes.

**Tests.**
- [ ] `test_p2c_recentred_stream_matches_worker` : pour 20 débuts tirés par deux générateurs identiques (le procédé `window_start` de R15), `cusum_max_bilateral` du flux de P2-C égale au bit près `worker_null_window_real`.
- [ ] `test_p2c_bootstrap_fpr` (prompt) : brut `_d2_pre()`, K = 20, N_cal = 20 000, 2000 fenêtres tenues à part sur les clés `[7, 30, 1, i]`.
  - Le FPR tenu à part est dans la région bilatérale à 99 % de 0,05, avec n = 2000 et n_cal = 20 000, soit [0,0368 ; 0,0632].
  - `diagnostics` vérifie K_eff_meas = 1/(4·var(f)) et K_eff_ana = K/(1 + (K − 1)ρ̂).
- [ ] `tests/test_identity_articleB.py::test_r15_identity_rng_free` :
  - `r15_rows(bootstrap=False, race=False)` passe partout ;
  - ρ̂ vaut 0.25774155995343417, 0.25904514047705118 et 0.28810195766064206 à 1e-12 (valeurs du prompt) ;
  - compositions égales.
- [ ] `test_r15_bootstrap_identity_k5` : `r15_rows(ks=(5,), race=False)` ; λ_boot = 34.200000000000003 et FPR_boot = 0.053, égaux au bit près.
- [ ] Échec attendu → implémentation → succès. Puis `python experiments/identity_articleB.py`, avec ces contrôles :
  - `articleB_R15.csv`, 56 cellules, toutes `pass` ;
  - `git diff results/identity/articleB_R01_R08.csv` vide ;
  - journal mis à jour.

### Tâche 4 — P3-D

**Interfaces.** `PIPELINES["P3-D"]` : défauts `K="mp"`, `mode="factor"`, `shrinkage="ledoit_wolf"`, `channels="residual"`, `reading="bootstrap"`, `H=750`, `alpha=0.05`, `N_cal=20000`, `null_rows="calib"`. L'état porte :
- `threshold` (λ_req) ;
- `lam_iid` ;
- `gamma_op` = λ_req/λ_iid ;
- `gamma_spec` = `gamma_spectral(q_calib)`.

**Tests.**
- [ ] `test_p3d_energy_and_gamma_op` :
  - pour z i.i.d. N(0, I_D) (`sim.gaussian_latent`), q a une moyenne de 0 ± 4 erreurs-types et une variance de 1 ± 0,05 ;
  - sur la calib de D2 en factor, avec H = 500 : les fenêtres énumérées de la calib vérifient mean(max S > λ_req) ≤ 0,05, et mean(max S > λ_req·(1 − 1e-6)) > 0,05 ;
  - Γ^op > 1, fini, et égal à `threshold/lam_iid` ;
  - H = 942 → `ValueError`.
- [ ] Extension de `test_x_and_z_inputs_agree` à P3-D.
- [ ] Échec attendu → implémentation → succès.

### Tâche 5 — P3-CS

**Interfaces.** `PIPELINES["P3-CS"]` : défauts `K="mp"`, `mode="factor"`, `b="pc1"`, `variant="b"`, `reading="anytime-valid"`, `gamma=20.0`, `alpha=0.05`, `H=750`, `B=2000`, `null_rows="pre_monitor"`. L'état porte `sigma_bar` et `c` (b), `rms` (a, randomization) et `threshold`. `reading="randomization"` impose `variant="a"`.

**Tests.**
- [ ] `test_p3cs_stakes_predictable` : sur un flux de 300 jours, les mises λ_t sont inchangées quand on modifie les lignes ≥ t. On vérifie aussi :
  - λ ≤ 0,5 ;
  - λ = c_j/σ̄ au premier jour ;
  - égalité à 1e-12 du log-e-détecteur avec une boucle de référence sur les facteurs 1 ± λ_t x_t.
- [ ] `test_p3cs_pivot_eprocess_and_randomization` :
  - (a) anytime-valid égale `log_average_betting_eprocess` sur les pivots ;
  - (a) randomization : seuil = `bootstrap_threshold` des maxima de `null_windows(flip=True)` ; changer `B` change le seuil (le paramètre est lu).
- [ ] Extension de `test_x_and_z_inputs_agree` à P3-CS.
- [ ] Échec attendu → implémentation → succès.

### Tâche 6 — P7, contrôle nul D6, détection F2 et option mélange

**Interfaces.**
- `PIPELINES["P7"]` : défauts `reading="anytime-valid"`, `gamma=20.0`, `H=750`. `record["delta"]` est (N,) ou (≥ H, N) ; absent → `ValueError`.
- `null_check(specs, X, splits, reps, key) -> DataFrame`. Fonctionnement :
  - `X_fit = symmetrize(X, rng(key + [0]))` ajuste chaque spec i par `fit_pipeline(spec_i, X_fit, splits, key=key + [1, i])` ;
  - la réplication r de la spec i tire, avec `rng(key + [2, i, r])`, un début dans ses lignes nulles, puis un signe par jour ;
  - les blocs D6 de [début − pré, début + H) sont empilés par paquets de `CHUNK` ; pré vaut H_ref pour P2-C bootstrap et 0 sinon ;
  - pour P3-*, le bloc est Z_base ⊙ ε (tête impaire ; tête paire inchangée), avec Z_base = `rep.transform_panel(X)` ;
  - P7 → `ValueError` ;
  - `seed` = `key + [2, i, r]`.
- `null_target(spec, state) -> (p, kind, n_cal)` : kind est « = », « ≤ » ou « ≈ », selon la table des lectures ; n_cal vaut N_cal ou B pour une lecture calibrée, None sinon.
- `summarize(rows, p, kind, n_cal=None) -> dict(n, fpr, lo, hi, ok)`, avec la région à 99 % (bruit de calibration inclus si n_cal est donné).
- `cross_independence(signs, n_se=3.0) -> {"passed", "max_abs_rho", "se", "pairs", "over"}`.

**Tests.**
- [ ] `test_null_fpr_d6` (prompt) : `null_check` sur `_d2_pre()`, 2000 réplications, H = 750. Specs et attentes :
  - P3-C exacte, canal k pour k = 0..5, α = 0,05 : niveau 0,043947, chaque FPR dans la région bilatérale ;
  - P3-C anytime-valid, γ = 15 000 : FPR ≤ borne haute de 0,05 ;
  - P2-C anytime-valid (K = 97), γ = 15 000 : ≤ borne haute de 0,05 ;
  - P3-CS (a) anytime-valid, γ = 20 : ≤ borne haute de 0,05 ;
  - P3-CS (a) randomization, α = 0,05 : région bilatérale avec n_cal = B = 2000, soit [0,0322 ; 0,0678] ;
  - deux appels identiques, sur 200 réplications, donnent des cadres égaux.
- [ ] `test_strong_f2_detected` (prompt, GO H13) : 50 réplications, chacune avec `rng = _rng(40, r)`, `symmetrize`, `draw_tau_star(0, T − 1, 500, 2000, rng)` et `inject(F2, I = kl_from_sharpe(8), K = 6, C synthétique)`.
  - Les fenêtres [τ*, τ* + 2000) sont empilées dans un panel, avec les `delta` découpés.
  - Fit sur `_d2_pre()` brut, mode full.
  - Attentes : `detected` partout pour P3-C, P3-CS (b) et P7 ; taux ≥ 0,9 pour P3-CS (a), en anytime-valid comme en randomization.
- [ ] `test_cross_independence_gate` :
  - signes de `gaussian_latent` (T = 941, D = 5) : test réussi ;
  - signes résiduels de la calib de D2 en factor : test échoué (max |ρ̂| > 3/√941), et `make_spec("P3-C", mixture_s2=0.01)` → `ValueError` au fit ;
  - sur un panel gaussien i.i.d. de 97 colonnes, l'option tourne et renvoie des lignes valides.
- [ ] Échec attendu → implémentation → succès.

### Tâche 7 — CLI et contrôle de référence

**Interface.** `main(argv=None)` :
- options `--pipeline`, `--dataset` (clés de `extract.DATASETS`), `--null-check` (exigé), `--reps` (500), `--out` (`results/pipelines`) et `--log-dir` (`logs/pipelines`) ;
- specs par défaut `NULL_SPECS[pipeline]`, les mêmes que dans `test_null_fpr_d6` ;
- lignes ≤ 2019-12-31, clé `[7, crc32(f"null|{pipeline}|{dataset}")]` ;
- sorties : `alarms_<pipeline>_<dataset>_null.csv`, `runs_<pipeline>_<dataset>_null.json` et `null_<pipeline>_<dataset>.log` (une ligne par spec : `run_id`, lecture, paramètres, n, FPR, région, cible, verdict). Chemins relatifs au dépôt, aucun horodatage ;
- code de sortie 0 si toutes les specs passent ; P7 → `parser.error`.

**Étapes.**
- [ ] `test_cli_null_check_smoke` : `main([... "--reps", "50", "--out", tmp, "--log-dir", tmp])` renvoie 0. On vérifie :
  - CSV de 50 × |specs| lignes ;
  - JSON relu ;
  - deux exécutions → mêmes octets.
- [ ] `mkdir -p results/pipelines logs/pipelines`, puis `python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500`, à relancer une seconde fois : `sha256sum` identiques.

### Tâche 8 — Documentation et écarts
- [ ] Rédiger `docs/sections/pipelines.md` en anglais :
  - registre, spec, état, `fit`/`run` et entrées X|Z ;
  - schéma d'`alarms.csv` et JSON `runs` ;
  - graines et parallélisme ;
  - table des lectures et garanties ; table des pipelines ;
  - une section par pipeline (formules, défauts, constantes et sources) ;
  - calibrations : `calibration.py` et `lattice.select_threshold` ;
  - identité R15 (tableau tiré d'`articleB_R15.csv`) ;
  - contrôle nul de référence (tiré du CSV de la CLI) ;
  - diagnostics des tests : nombres annoncés comme diagnostics, absents de l'article (précédent de `monitors.md`) ;
  - constats de puissance (P3-CS, P3-D, test d'indépendance) ;
  - commandes de vérification.
  - Références :
    - [Page, 1954] ; [Lorden, 1971] ; [Ville, 1939] ;
    - [Shin, Ramdas & Rinaldo, 2024, E-detectors] ;
    - [Waudby-Smith & Ramdas, 2024, Estimating means of bounded random variables by betting] ;
    - [Künsch, 1989, The jackknife and the bootstrap for general stationary observations] ;
    - Article B (R15) ; Article C (Lemmes 1 et 2, Prop. 3, Remarque « Combining channels »).
- [ ] `docs/sections/monitors.md` : lignes de portage (`fraction_stream`, workers, `composition_for`, `get_deterministic_seed`, destination de `save_fair_csv`) et API (`fraction_stream`, `log_average_betting_eprocess`, `calibration.*`).
- [ ] `docs/DEVIATIONS.md` : relire juste avant l'édition, puis ajouter en fin de fichier, en français, en citant les sondes et le GO :
  - `C-pipe-delay` (GO H1) ;
  - `C-pipe-null-targets` (GO H2, GO H3) ;
  - `C-P2C-port` (GO H4, GO H5) ;
  - `C-P3D-windows` (GO H8) ;
  - `C-P3CS-design` (GO H9, GO H10) ;
  - `C-P3C-mixture-gate` (GO H7) ;
  - `C-identity-R15` (GO H12).

### Tâche 9 — Clôture (ordre AGENTS.md)
- [ ] Vérifications :
  - `pytest -q tests/test_pipelines.py tests/test_identity_articleB.py tests/test_monitors.py` ;
  - `source .venv/bin/activate && make check`. En cas d'échec : diagnostic, 3 tentatives au plus. Un échec imputable à un autre stream entraîne gel et signalement, sans commit ;
  - `git diff results/identity/articleB_R01_R08.csv` doit être vide. Le fixture de `tests/test_data_d1_d2.py` restaure les octets commités de D1, de D2 et du manifeste. Si un fichier étranger reste modifié, il n'est pas indexé.
- [ ] (1) Skill `wrap-up` → `prompts/wrapups/wrapup-07.md`.
- [ ] (2) `tools/reindex_graphify_jcodemunch.sh`.
- [ ] (3) `make check`, puis commit unique sans trailer : `feat(pipelines): add P2-C, P3-C, P3-D, P3-CS and P7 pipelines, calibrations and Article B R15 identity`.
  - Indexer explicitement les fichiers de la section « Fichiers », y compris `prompts/GO-stream-07.md`.
  - `git diff --staged` : aucun fichier d'un autre stream, aucun `__pycache__`, aucun chemin absolu du répertoire personnel, aucun fichier > 50 Mo.
- [ ] (4) Contrôler la plage `origin/main..HEAD`, qui inclut `672ce26` (stream 10) s'il n'est toujours pas poussé : aucun chemin sous `data/raw/eurofidai/` ni sous `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo. Puis `git push origin main`, et rapporter le hash du commit et l'état de l'arbre. Les fichiers étrangers éventuels sont signalés.

## Vérification de bout en bout

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
pytest -q tests/test_pipelines.py
python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500
python experiments/identity_articleB.py && grep -c True results/identity/articleB_R15.csv
make check
```

## Risques

| Risque | Parade |
|---|---|
| Durée de `make check` : environ +60 s (bootstrap P2-C à 14 s, λ_boot de R15 à 11 s, F2 et nuls D6 empilés) ; le script d'identité gagne environ 45 s | Empilement par blocs et détecteurs vectorisés ; K = 20 dans le test bootstrap |
| Cibles faibles pour les e-détecteurs (borne H/γ) | Test net du Lemme 2 par la lecture exacte canal par canal ; ARL₀ laissé à E3 (GO H3) |
| P3-D non stationnaire entre 2005 et 2019 (Γ^op ≈ 191/2346) | Fenêtres de calib par défaut ; E1 doit trancher pour H_det = 2000 > 941 (GO H8) |
| Queue des délais de P3-CS (a) (1755 sur 2000 jours) | Seuil ≥ 90 % dans le test F2 (GO H13) ; puissance documentée |
| ρ̂ sensible au BLAS (un ulp à K = 10) | Porte relative de 1e-12 ; valeurs attendues du prompt testées à 1e-12 |
| Modification de fichiers des streams 04 et 05 (`streams.py`, `eprocess.py`, script d'identité) | Ajouts seulement ; tests du stream 04 inchangés et au vert ; R01 réécrit à l'identique |
| `n_jobs` > 1 (fork) | Test d'invariance ; une seule copie des données par paquet |
| Hypothèse renversée au GO | Chaque choix est isolé dans une constante (`PIVOT_BETS`, `STAKE_CAP`), un défaut de `DEFAULTS`, ou une fonction de lecture (`null_target`) ; le changement reste local |
