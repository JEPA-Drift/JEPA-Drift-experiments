# Plan — Stream 11 : audit informationnel des panels D2 et D3

> Exécution : Claude Code, en session unique, sans sous-agent. Méthode : `superpowers:executing-plans` en mode natif, `superpowers:test-driven-development` pour chaque tâche, `superpowers:verification-before-completion` avant toute annonce de fin. Le skill `dataviz` est chargé avant d'écrire le code des figures. Cases `- [ ]` pour le suivi.
> Chaque commande Bash commence par `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate` (règle « Interpreter » d'AGENTS.md ; le python de Trading n'est jamais lancé seul).

Date : 2026-10-17. Spécification : `prompts/streams/prompt-11-audit.md`. Base : `653ec8b` (`origin/main` au GO) ou un descendant.

Statut : **GO**. La revue `prompts/GO-stream-11.md` (2026-10-17) est intégrée dans ce plan final, section « Décision GO intégrée ».
- (GO Hn) marque l'hypothèse n du plan initial, confirmée par la revue ; pour (GO H12), la revue fixe en plus la variante citée.
- **Étape préalable** (règle `C-plan-recording`, instruction du GO) : enregistrer ce plan dans `prompts/plans/plan-11.md` du worktree avant toute ligne de code.

**Objectif.** Écrire `experiments/audit_information.py`. Le script mesure, sur 2005–2019 et pour `d2_us97` et `d3_239` :
- le spectre de covariance et η ;
- la corrélation des signes ;
- la symétrie centrale des directions figées ;
- le spectre de Sharpe de dérive débiaisé aux transitions des datations de SPY ;
- les plafonds des canaux N1 à N3 ;
- la part des phases dans le budget ;
- les gains prévus, entrée d'E1.

Livrables : les huit CSV de `results/audit/`, quatre figures PNG + PDF dans `figures/audit/`, le journal `logs/audit/audit.log` et les tests `tests/test_audit.py`.

**Architecture.**
- Un seul script, sans nouveau module de bibliothèque (le prompt dit « Écrire `experiments/audit_information.py` »). Les fonctions pures sont testées par `tests/test_audit.py` via `from experiments import audit_information as au`, comme `tests/test_injection.py` le fait pour E2.
- Enchaînement : calcul, puis CSV écrits par `save_fair_csv`, puis figures tracées depuis les CSV relus (`float_precision="round_trip"`).
- Base figée : la représentation du prompt 6, `PCAOrthogonal(K="mp", mode="factor", shrinkage="ledoit_wolf")` ajustée sur la calib. Son `state_hash` est comparé au sidecar commité `data/derived/<dataset>/z_<hash>.json`.

## Décision GO intégrée

Source : `prompts/GO-stream-11.md` (verdict : **GO**). Les seize valeurs par défaut sont confirmées. Pour H12, la revue retient `mvt_static` comme variante citée. Intégration :

| Point de la revue | Intégration dans ce plan |
|---|---|
| Instruction préalable : enregistrer `prompts/plans/plan-11.md` dans le worktree avant toute ligne de code | Statut et Tâche 0 |
| `origin/main` = `653ec8b`, et non `f7bde91`. Correctifs `424b199` (AGENTS.md épingle la chaîne d'interpréteur) et `8ae232e` (contrats en `.venv`, `skipif` sur les gardes torch, `test_reconstruction_from_cache` sauté hors de la pile de référence) | Base ; Tâche 0 (worktree créé depuis `origin/main`) |
| La panne de `test_reconstruction_from_cache` est résolue : aucune tâche n'y est consacrée | Sonde 11 inchangée ; aucune tâche |
| Interpréteur : chaîne `conda activate Trading` puis `.venv`. Pour `git` et `ls`, la chaîne conda seule suffit | Bandeau d'exécution, inchangé |
| Données EUROFIDAI restaurées (`653ec8b`), sans usage dans ce stream. Référence de `make check` : 22 tests réussis et 4 sautés au premier lancement de pytest, 187 réussis au second | Tâche 0 (référence « avant ») ; contraintes inchangées (aucune lecture EUROFIDAI) |
| Plan canonique : celui-ci, enregistré dans `prompts/plans/plan-11.md` du worktree ; une seule instance implémente le stream 11 | Statut |
| Après le push, retirer `prompts/GO-stream-11.md` de l'arbre principal avant d'y avancer `main` | Tâche 7 (5) ; Risques |
| (GO H1) à (GO H16) confirmés ; (GO H12) : variante citée `mvt_static`, `mvt_garch` et `t_garch` restent au CSV (colonne `variant`) | Marqueurs (GO Hn) ; Définitions opératoires (8) |
| Skill `dataviz` absent → poursuivre sans ; règles de déterminisme déjà fixées | Tâche 6 |
| Jamais indexés : liens du worktree, fichiers D1/D2 réécrits par le fixture, `logs/d4/` | Contraintes globales, Tâche 7 |
| Trace de décision | `prompts/GO-stream-11.md` commité avec le stream (Tâche 7) |

## Contexte

- **Consommateurs.**
  - E1 (stream 12) lit `predicted_gains.csv` : comparaison mesuré/prévu et point (iv) du résumé J2. Son bras réel reprend la lecture budget sur les mêmes datations.
  - §2 de l'article (spectre, ρ̂_signe, symétrie, Sharpe de dérive), décision J2 et contingence C1 (R10 : « SR de dérive faible dans tous les sous-espaces »).
  - E4 (stream 19) fera un « audit réduit par sous-ensemble ». Il réutilisera `debiased_sr2` et `mbb_indices`.
- **Définitions** (AGENTS.md et §3).
  - I = SR²/504.
  - Lecture budget : τ_γ = ln γ / I, exacte par le Lemme 1.
  - Corollaire 1 : terme factoriel plus terme de largeur.
  - Prop. « Dimension tax » : multiplicateur M(D, γ).
  - Lemme 2 : flux de signe exacts sous symétrie centrale.
- **Tableau « Gains prévus » du plan v4** (`prompts/Plan_Claude_Opus_v4.md`, l. 194–209).
  - Formules à un facteur équicorrélé.
  - Valeurs de planification : ρ = 0,40, ρ_signe = 0,26, κ ∈ {0,25 ; 0,5 ; 1}, ARL₀ = 252.
  - Consigne : le §2 publie « les formules évaluées sur ρ̂, le spectre résiduel et κ̂ estimés, jamais ces valeurs de planification ».
- **Risque R9** (plan v4). Le biais de bruit vaut 252·d·(1/n₁ + 1/n₂), soit ≈ 482 en SR² pour N = 239 et deux phases de 250 jours. Parades prévues : projections de dimension ≤ 30, agrégation sur les transitions, bootstrap. Le prompt exige de rapporter les estimations débiaisées même négatives.
- **Briques réutilisées, sans réécriture.**
  - `jepadrift.data_loader.articleB` : `load_d2`, `load_phases`, `load_splits`.
  - `jepadrift.data_loader.sp500` : `load_d3_239`, `load_chars`, `load_splits`, `_mean_pairwise_sign_corr` (la définition des profils de données).
  - `jepadrift.representations.extract` : `DATASETS`, `segment_rows`.
  - `jepadrift.representations.pca` : `PCAOrthogonal`, `pca_directions` (eigen-paires LW triées et signées), `mp_edge`.
  - `jepadrift.stats.covariance.ledoit_wolf`.
  - `jepadrift.stats.garch.fit_garch_qmle` : QMLE d'un GARCH(1,1) à ciblage de variance.
  - `jepadrift.injection` : `fit_background` (B = V Λ^{1/2}, ψ) et `gls_residual` (construction de F2).
  - `jepadrift.pipelines` : `save_fair_csv`, `sign_diagnostics` (arithmétique de R15).
  - `jepadrift.floors.mixture_multiplier`.
  - scipy : `stats.binomtest`, `stats.t.fit`, `optimize.minimize_scalar`, `special.gammaln`.
  - statsmodels : `stats.multitest.multipletests(method="holm")`.

## Constats des sondes

Sondes en lecture seule, sans écriture de fichier.

1. **Fenêtre 2005-01-01 – 2019-12-31.** D2 compte 3774 lignes (du 2005-01-04 au 2019-12-31), D3 en compte 3775. Aucune NaN. Rendements exactement nuls : 0,78 % (D2) et 0,84 % (D3).
2. **Base figée.** `PCAOrthogonal()` réajusté sur la calib (941 jours) redonne les `state_hash` commités : `85147fd9…` (D2) et `6c44d64a…` (D3).
   - K = 5 et 10 (n₊ = 6 et 11) ; λ₊ = 1,7452 et 2,2619.
   - δ_LW = 0,0192 et 0,0252 ; η_LW sur la calib = 0,331 et 0,259.
3. **Phases.**
   - Les trois `phases_*.csv` couvrent SPY, PFF, VNQ et BWX.
   - Les phases de SPY forment une chaîne : fin_k = début_{k+1}. `T_days` est le nombre de jours de D1 dans (début, fin].
   - Sur SPY, `lt_spy` et `symmetric` sont identiques : 30 phases, Lunde–Timmermann. `strict_ps` compte 12 phases (Pagan–Sossounov).
   - Frontières dans la fenêtre : 12 (`lt_spy`), 10 (`strict_ps`) et 12 (`symmetric`).
   - Phases découpées à la fenêtre et au moins 20 jours de chaque côté : il reste 9, 10 et 9 transitions. `lt_spy` perd 2008-10-27, 2008-11-04 et 2008-11-20, voisines de phases de 6 et 12 jours.
   - `strict_ps` sur D2 : (n₁, n₂) va de (696, 355) à 2007-10-09 jusqu'à (65, 256) à 2018-12-24.
4. **SR² débiaisé** (forme exacte, Σ̂ intra-phase poolée, sans bootstrap).
   - Marché : 5,8 à 96,6. Factoriel : −52 à 158. Somme des blocs idiosyncratiques : −589 à 2422.
   - Les valeurs extrêmes viennent des phases courtes (42 à 65 jours).
   - Médiane idiosyncratique sur `strict_ps` : +16 sur D2 et −52 sur D3. R9 se réalise.
5. **Test des triplets.**
   - L'algorithme par paires, en O(n² log n), donne les mêmes entiers que l'énumération en O(n³) : T, ΣB_t² et ΣB_st² à n = 37. Il tourne en 1,1 s à n = 3774.
   - Sous N(0,1), l'écart-type de z vaut 0,99 à 1,03 et le rejet à 5 % 5,25 à 6,25 % (n = 30 et 100, 2000 tirages).
   - Puissance de 100 % contre une loi exponentielle à n = 300.
   - La formule de variance est celle de `NSM3::RFPW`, le paquet compagnon de Hollander, Wolfe & Chicken (2014).
6. **Symétrie sur la fenêtre** (GARCH ajusté et convergé).
   - PC1 : q̂ = 0,549 (D2) et 0,546 (D3), p binomial de 2e-9 et 2e-8, z des triplets de −6,6 et −7,1.
   - PC2 de D3 est aussi rejeté (q̂ = 0,549, z = −5,6). PC20 ne l'est pas.
7. **ρ̂ sur la fenêtre.**
   - ρ̂_signe = 0,269 (D2) et 0,258 (D3) ; sin(πρ̂/2) = 0,409 et 0,394 ; ρ̂_rendements = 0,416 et 0,391.
   - Sur la calib, ρ̂_signe = 0,2038 et 0,1870, égaux aux profils `results/data/*_profile.csv`.
   - G(1→2) = 2,37 et 2,54 en KL gaussienne, 3,62 et 3,83 en flux de signes.
   - À γ = 252 : M(1)/M(K) = 0,728 et 0,598 ; M(1)/M(N−1) = 0,256 et 0,172.
8. **Plafonds.**
   - N1, sur l'énergie blanchie du bloc idiosyncratique : 1,968 (D2) et 1,998 (D3), soit 1,925 et 1,980 après correction χ².
   - GARCH(1,1) sur PC1 : α ≈ 0,11, β ≈ 0,87.
   - ν̂ d'une loi t univariée sur PC1 standardisé : 6,8 et 7,1 (2,6 et 2,5 sans standardisation).
   - ν̂ multivarié (ECME) sur le bloc idiosyncratique blanchi : 5,0 et 5,4 (145 à 154 itérations, 3 et 10 s). Après une standardisation prévisible : 8,7 et 9,3.
   - Ledoit–Wolf glissant sur 60 jours : 0,2 et 0,9 ms par jour.
9. **Caractéristiques.**
   - Celles de D3 sont au format long, triées par (date, titre) : `reshape(T, 239, 15)` est exact.
   - Dans la fenêtre, `c_beta_252` a 32 NaN et les 14 autres colonnes aucune. Les 11 secteurs GICS sont représentés, de 3 à 43 titres chacun.
   - D2 n'a pas de caractéristiques.
10. **Coût du bootstrap.** Les statistiques par phase de D3 (13 phases, 10 blocs) prennent 1,0 s à B = 200, soit environ 10 s par datation à B = 2000.
11. **Environnement.**
    - `test_reconstruction_from_cache`, signalé en échec par le message de `f7bde91`, passe dans `.venv` derrière `conda activate Trading` (4,9 s).
    - scipy 1.17.1 n'a pas de `multivariate_t.fit`.
    - `multipletests(method="holm")` est disponible (statsmodels 0.15.0).

## Définitions opératoires

Notation :
- W = lignes datées dans [2005-01-01, 2019-12-31] ; X est le panel (T_W × N) de ces lignes.
- calib = `segment_rows(dates, splits["segments"]["calib"])`.
- (λ_k, v_k) = `pca_directions(X_calib, "mp", "full", "ledoit_wolf")`, ordre décroissant, signes d'`eigh_desc`.
- K = n₊ − 1 ; V_f = [v₁ … v_{K+1}].

1. **Spectre (item 1).**
   - Sur la calib : valeurs propres de la covariance empirique (diviseur n, comme `ledoit_wolf`), de la covariance Ledoit–Wolf et de la corrélation empirique ; λ₊ = `mp_edge(941, N)`, n₊ et K.
   - η = λ₁/tr Σ̂ sur les lignes de chaque année civile de 2005 à 2019, avec et sans Ledoit–Wolf.
2. **Signes (item 2).** Segments pretrain et calib (lignes de `splits.yaml`), plus la fenêtre W.
   - ρ̂_signe = moyenne des corrélations de Pearson par paires des indicatrices 1{r > 0} (`sp500._mean_pairwise_sign_corr`).
   - ρ = sin(πρ̂_signe/2).
   - ρ̂_rend = moyenne des corrélations de Pearson par paires des rendements.
   - K_eff = 1/ρ̂_signe ; K_eff(N) = N/(1 + (N−1)ρ̂_signe).
   - Arithmétique de R15, par `sign_diagnostics(X.T)` : ρ̂ des signes centrés sur la médiane, K_eff_meas = 1/(4 Var x̄_t) et K_eff_ana.
3. **Directions figées (item 3).**
   - PC1 à PC20 : u = v_k.
   - Caractéristiques (D3) : c_{t,j}, une NaN valant 0. On pose u_{t,j} = P c_{t,j}/‖P c_{t,j}‖ avec P = I − V_f V_fᵀ, projection euclidienne sur le sous-espace idiosyncratique. u_{t,j} est connue à l'ouverture de t. Une norme nulle lève `ValueError`.
   - Série projetée : y_t = u_tᵀx_t.
4. **Symétrie.**
   - q̂ = #{y_t > 0}/#{y_t ≠ 0}, testé par `binomtest` bilatéral contre 1/2.
   - σ̂_{t|t−1} : `fit_garch_qmle(y)` sur W, puis le filtre σ̂²_1 = Var(y), σ̂²_t = ω + α y²_{t−1} + β σ̂²_{t−1}.
   - Test des triplets (Randles, Fligner, Policello & Wolfe, 1980, *JASA* 75(369), 168–172) sur e_t = y_t/σ̂_{t|t−1} :
     - g(i,j,k) = sign(e_i + e_j − 2e_k) + sign(e_i + e_k − 2e_j) + sign(e_j + e_k − 2e_i) ∈ {−1, 0, 1} ;
     - T = Σ_{i<j<k} g ; B_t = somme des g des triplets qui contiennent t ; B_{s,t} = somme des g des triplets qui contiennent s et t ;
     - σ̂²_T = (n−3)(n−4)/((n−1)(n−2))·Σ_t B_t² + (n−3)/(n−4)·Σ_{s<t} B_{s,t}² + n(n−1)(n−2)/6 − [1 − (n−3)(n−4)(n−5)/(n(n−1)(n−2))]·T² ;
     - z = T/σ̂_T et p = 2(1 − Φ(|z|)).
   - Calcul sur l'échantillon trié, par paires p < q : `np.searchsorted` compte les troisièmes points situés au-dessous, entre et au-dessus, aux seuils 2x_p − x_q, (x_p + x_q)/2 et 2x_q − x_p. Un ex aequo compte 0.
5. **Sharpe de dérive (item 4).**
   - Transition (k, k+1) d'une datation :
     - la phase k est l'ensemble des lignes de W datées dans (début_k, fin_k] ;
     - la frontière fin_k appartient à [2005-01-01, 2019-12-31) ;
     - n₁ ≥ 20 et n₂ ≥ 20.
   - Pour un sous-espace S de dimension d, avec Y ses projections :
     - δ̂ = ȳ₂ − ȳ₁ ;
     - Σ̂_S = (SC₁ + SC₂)/ν, où SC est la somme des produits croisés centrés d'une phase et ν = n₁ + n₂ − 2 ;
     - c = 1/n₁ + 1/n₂ ; D̂² = δ̂ᵀΣ̂_S⁻¹δ̂.
   - Trois estimations :
     - `sr2_raw` = 252·D̂² ;
     - `sr2_debiased` = 252·[D̂²(ν − d − 1)/ν − d·c]. Elle est sans biais, car E[Σ̂⁻¹] = ν/(ν − d − 1)·Σ⁻¹ ;
     - `sr2_spec` = 252·[D̂² − d·c]·(ν − d − 1)/ν. C'est la formule du prompt avec n := ν ; elle garde un biais de 252·d·c·(d + 1)/ν.
   - Sous-espaces :
     - `market` = PC1 ; `factor` = PC2..PC(K+1) ;
     - blocs `idio:b1`, `idio:b2`, … de 30 PC consécutives à partir de PC(K+2), le dernier en comptant 30 au plus ;
     - `idio` = somme des blocs ; `residual_full` = `factor` + `idio`, soit N − 1 dimensions ;
     - `chars` = les 15 séries y_{t,j} (D3).
   - Bootstrap par blocs mobiles (Künsch, 1989) :
     - blocs de 20 jours, B = 2000, rééchantillonnage à l'intérieur de chaque phase ;
     - k = ⌈n/20⌉ débuts uniformes sur {0, …, n − 20}, blocs concaténés puis tronqués à n jours ;
     - un tirage par phase, partagé par tous les sous-espaces et par les deux transitions qui touchent cette phase ;
     - IC percentile de 2,5 à 97,5 % sur `sr2_debiased`.
   - Agrégat : médiane de chaque colonne sur les transitions. Son IC est formé par les percentiles des médianes calculées tirage par tirage.
6. **N1.**
   - z_t = coordonnées blanchies du bloc idiosyncratique, v_kᵀx_t/√λ_k pour k ≥ K+2 ; d = N − K − 1.
   - s²_t = moyenne des z²_{t,k} sur le bloc ; N1 = moyenne(s²)·moyenne(1/s²) sur W.
   - Correction de la loi χ² : facteur (d − 2)/d.
7. **N2.**
   - Pour chaque ligne t ≥ 60 de W : Σ_t = `ledoit_wolf(X[t−60:t])`.
   - Directions F1 : a = colonnes de B = `fit_background(X_calib, K + 1)["B"]`, PC1 compris, comme le F1 de `inject`.
   - Directions F2 (D3) : a_t = `gls_residual(C[:, :, j], B, ψ)`.
   - I_cond = moyenne_t a_tᵀΣ_t⁻¹a_t ; I_stat = āᵀΣ̄⁻¹ā, avec Σ̄ = moyenne_t Σ_t et ā = moyenne_t a_t.
   - N2 = I_cond/I_stat. Le rapport est ≥ 1 exactement, par convexité jointe de (a, Σ) ↦ aᵀΣ⁻¹a.
8. **N3.**
   - Loi t multivariée de localisation nulle, ajustée par ECME (Liu & Rubin, 1995, *Statistica Sinica* 5, 19–39) :
     - poids w_t = (ν + d)/(ν + δ_t) et S = Σ_t w_t z_t z_tᵀ/n ;
     - ν est ensuite mis à jour en maximisant la log-vraisemblance observée sur [2,01 ; 1000] (`minimize_scalar`, méthode bornée) ;
     - arrêt quand |Δν| < 1e-6·ν, ou après 500 itérations.
   - Trois variantes :
     - `mvt_static` : bloc idiosyncratique blanchi par la calib (lecture littérale) ;
     - `mvt_garch` : chaque coordonnée du bloc divisée par son σ̂_{t|t−1} GARCH ;
     - `t_garch` : par direction (PC1 à PC20, caractéristiques), `stats.t.fit(e, floc=0)` sur les séries standardisées de l'item 3.
   - Rapport J/Σ⁻¹ = (ν + 1)ν/((ν + 3)(ν − 2)), NaN si ν ≤ 2.
   - Variante citée (GO H12) : `mvt_static`.
9. **Part du budget (item 6).** Pour chaque transition gardée et chaque sous-espace agrégé (`market`, `factor`, `idio`, `residual_full`, `chars`) :
   - L = n₂, la phase d'arrivée découpée à W ; Î = `sr2_debiased`/504 ;
   - la phase est dans le budget si et seulement si L·Î ≥ ln γ, pour γ ∈ {20, 252} ;
   - part = n_dans/n_phases.
10. **Gains prévus (item 7).** Une évaluation par (jeu, datation, γ). Entrées : ρ̂ = ρ̂_rend(W), ρ̂_s = ρ̂_signe(W), et les médianes SR²_m, SR²_f, SR²_i des sous-espaces `market`, `factor` et `idio`.
    - `1-2:F3` : G = N/(1 + (N−1)ρ̂) et G_signe = N/(1 + (N−1)ρ̂_s). Une seule dimension, donc G_tax = G.
    - `2-3:F1` : G = SR²_f/SR²_m ; G_tax = G·M(1, γ)/M(K, γ).
    - `2-3:F2` : κ̂² = (SR²_i/SR²_m)·(1 − ρ̂)/(1 + (N−1)ρ̂) ; G = κ̂²(1 + (N−1)ρ̂)/(1 − ρ̂), égal à SR²_i/SR²_m par construction ; G_tax = G·M(1, γ)/M(N−1, γ).
    - `1-3:F3+F2` : G = N/(1 + (N−1)ρ̂) + κ̂²·N/(1 − ρ̂). Pas de taxe : colonne vide, comme dans le tableau.
    - M = `floors.mixture_multiplier`.
    - Une médiane ≤ 0 rend κ̂ et le rapport NaN (R9). Aucune valeur de planification n'est substituée.

## Décisions

| Question | Décision | Raison |
|---|---|---|
| Fichier | Script unique et fonctions pures. Aucun module ajouté à `jepadrift/` | Le prompt demande un script ; E4 déplacera les estimateurs le jour où il en aura besoin |
| (GO H1) Fenêtre et lignes | Toutes les lignes de W, jours d'embargo compris. Contrôle bloquant : aucune date > 2019-12-31 après le découpage. Spectre et K sur la calib ; η par année civile de 2005 à 2019 | Prompt : « 2005–2019 seulement », « spectre … sur la calibration », « η par année ». L'embargo ne protège que la calibration des seuils |
| (GO H2) Base figée | Eigen-paires LW de la calib, celles de la représentation du prompt 6. `ValueError` si le `state_hash` réajusté diffère du sidecar | Entrée « représentations du prompt 6 » ; un seul jeu de directions pour tout l'audit |
| (GO H3) Signes | ρ̂_signe selon la définition des profils (1{r > 0}), ce qui donne un oracle de test sur la calib, plus l'arithmétique de R15. Trois segments. Les gains prévus prennent les valeurs de W | Cohérence avec `results/data/*_profile.csv` et R15. E1 injecte sur des fonds tirés de 2005–2019 |
| (GO H4) Caractéristiques | D3 seulement : 15 colonnes (4 continues, 11 GICS), NaN → 0 (lecture de `C-inject-F2-nan`), projection euclidienne sur le sous-espace idiosyncratique, normalisation chaque jour. Alternative : calculer les 4 caractéristiques continues de D2 par `sp500._compute_chars` ; `c_beta_252` manquerait alors sur environ 126 jours de 2005, ce qui donne des directions nulles à traiter | Le sous-espace « caractéristiques » reste disjoint du marché et des facteurs ; la décomposition est additive ; le prompt ne fournit pas de caractéristiques pour D2 |
| (GO H5) Symétrie | Fenêtre W. q̂ sur y brut, zéros exclus. Test binomial exact bilatéral. Triplets sur y/σ̂, avec un GARCH(1,1) ajusté sur la série elle-même. Holm à 5 % sur la famille jointe des 2D p-values d'un jeu : 40 pour D2, 70 pour D3 | Prompt, item 3. Le contrôle du taux d'erreur familial porte sur l'hypothèse « symétrie centrale dans toutes les directions » |
| (GO H6) Transitions | Lignes SPY des trois datations ; phase = (début, fin] ; frontière dans [2005-01-01, 2019-12-31) ; phases découpées à W ; n₁, n₂ ≥ 20, soit un bloc de bootstrap. `lt_spy` et `symmetric`, identiques sur SPY, sont traités tous deux sans déduplication ; le journal le signale | Prompt, item 4 ; convention de `T_days` |
| (GO H7) Sous-espaces | Résiduel complet découpé en blocs d'au plus 30 PC, puis sommé en ignorant les covariances entre blocs. Σ̂_S = covariance intra-phase poolée des deux phases (ν = n₁ + n₂ − 2) | Le « résiduel complet » a 96 et 238 dimensions, contre « d_S ≤ 30 ». Chaque estimation respecte la contrainte et reste définie (ν > d + 1). La somme est exacte si les blocs sont non corrélés |
| (GO H8) Débiaisage | `sr2_debiased` prend la forme exactement sans biais ; c'est la valeur par défaut, utilisée pour les IC, les agrégats, le budget et les gains. La formule du prompt est gardée dans `sr2_spec`. Écart `C-audit-debias` | La formule du prompt garde un biais de 252·d·c·(d + 1)/ν, soit 3,8 en SR² à d = 30 et n₁ = n₂ = 250. Le test Monte Carlo de la Tâche 3 le chiffre |
| (GO H9) Bootstrap | Blocs mobiles de 20 jours dans chaque phase ; B = 2000 ; tirages partagés ; graines `SeedSequence([11, crc32(jeu), crc32(datation), id de phase])` ; IC percentile à 95 % ; IC des médianes par tirage | Prompt, item 4 (« blocs de 20 jours, 2000 tirages », « graines fixes »). Les sommes de blocs et les médianes restent cohérentes |
| (GO H10) N1 | Énergie blanchie du bloc PC(K+2)..PCN : σ_t est estimé par la dispersion du jour, sans modèle de volatilité (§3, canal N1). Valeur brute et valeur corrigée de la loi χ² | « Dispersion transversale résiduelle » : résidu après le marché et les facteurs |
| (GO H11) N2 | Σ_t = LW des 60 lignes précédentes de W. F1 = colonnes de B ; F2 = résidus GLS des 15 caractéristiques, construction de `inject`. Σ̄ et ā sont moyennés sur les mêmes jours. Le rapport inclut la volatilité commune (canal N1), sans version normalisée | Prompt, item 5 ; Prop. 1 (Σ̄ = E[Σ_t]) ; le rapport est ≥ 1 exactement |
| (GO H12) N3 | Trois variantes : `mvt_static` (lecture littérale), `mvt_garch` et `t_garch` par direction. ECME de localisation nulle. Variante citée : `mvt_static` ; les deux autres restent au CSV (colonne `variant`) | Prompt : « loi t multivariée ajustée sur les résidus blanchis… par direction ». N3 porte sur la non-gaussianité conditionnelle (§3) ; la variante statique absorbe la volatilité commune (ν̂ ≈ 5 contre ≈ 9 après standardisation, sonde 8) |
| (GO H13) Part du budget | L = n₂ découpé ; Î de la transition d'arrivée ; sous-espaces agrégés seulement. Une phase sans transition d'arrivée gardée sort du décompte | Prompt, item 6. Aucune donnée postérieure à 2019 : le `T_days` d'une phase qui finit en 2020 en dépendrait |
| (GO H14) Gains prévus | Formules du tableau du plan v4, évaluées sur ρ̂ (rendements, W), ρ̂_signe (W), K, N et κ̂. κ̂ vient de l'inversion à un facteur de SR²_idio/SR²_market. Une ligne par (jeu, datation, étape, γ). NaN propagé si une médiane est ≤ 0. Un test reproduit les valeurs du tableau | Consigne du plan v4 citée au Contexte. Sous le modèle à un facteur, ce κ̂ est celui de la convention (b) (`C-inject-conv-b`) |
| (GO H15) Figures | Quatre figures (spectre et η ; symétrie ; Sharpe de dérive ; part du budget), tracées depuis les CSV relus, en PNG et en PDF, avec `metadata={"CreationDate": None}` pour le PDF. Pas de figure pour les signes, les plafonds et les gains, qui sont des tableaux | Livrable `figures/audit/*.{png,pdf}` |
| (GO H16) Exécution | Worktree `~/JEPA-Drift-stream-11` sur la branche `stream-11`, créée depuis `origin/main`. Liens absolus vers `.venv/`, `data/raw/` et `external/`. Fin par `git push origin stream-11:main` après rebase | Section « Worktrees and parallel streams » d'AGENTS.md ; les streams 17 et 18 de la même vague peuvent tourner en parallèle |
| CLI | `--datasets` (un ou deux noms parmi `d2_us97` et `d3_239`, les deux par défaut), `--out` (`results/audit`), `--fig-dir` (`figures/audit`), `--log-dir` (`logs/audit`), `--boot` (2000 ; une valeur < 1 déclenche `ap.error`), `--quick` (B = 50, PC1 à PC3 pour la symétrie et `t_garch`) | Commande de vérification du prompt ; `--quick` pour le test de fumée, comme E2 |
| Aléa et sorties | `SeedSequence` dans le bootstrap seulement. Les huit CSV sont écrits par `save_fair_csv`. Paramètres GARCH et drapeau de convergence dans les CSV ; un GARCH non convergé garde les valeurs initiales de `fit_garch_qmle`, avec son drapeau | AGENTS.md ; critère « déterministe au SHA-256 près » |

## Schémas des CSV

| Fichier | Colonnes |
|---|---|
| `spectrum.csv` | `dataset, matrix, rank, eigval, share, cum_share, n_days, mp_edge, n_above_edge, K, lw_shrinkage` ; `matrix` ∈ {`cov_sample`, `cov_lw`, `corr_sample`} |
| `eta_by_year.csv` | `dataset, year, n_days, eta_sample, eta_lw, lw_shrinkage` |
| `sign_corr.csv` | `dataset, segment, n_days, N, rho_sign, rho_gauss, rho_ret, K_eff, K_eff_N, rho_sign_med, K_eff_meas, K_eff_ana` ; `segment` ∈ {`pretrain`, `calib`, `window`} |
| `symmetry_tests.csv` | `dataset, direction, n, q_hat, binom_p, triples_T, triples_z, triples_p, garch_omega, garch_alpha, garch_beta, garch_converged, binom_p_holm, triples_p_holm, binom_reject, triples_reject` ; `direction` ∈ {`PC1`…`PC20`, `char:<nom>`} |
| `drift_sharpe_transitions.csv` | `dataset, dating, level, transition, boundary, n1, n2, n_transitions, subspace, d, sr2_raw, sr2_debiased, sr2_spec, ci_lo, ci_hi, n_boot` ; `level` ∈ {`transition`, `median`} ; `transition` = `<k>-<k+1>` ou `median` |
| `channel_ceilings.csv` | `dataset, ceiling, variant, direction, value, i_cond, i_static, nu, iterations, converged, n_days, d` ; `N1` : variantes `raw` et `chi2_corrected` ; `N2` : variante `lw60` ; `N3` : variantes `mvt_static`, `mvt_garch` et `t_garch` |
| `budget_share.csv` | `dataset, dating, subspace, gamma, n_phases, n_in_budget, share` |
| `predicted_gains.csv` | `dataset, dating, step, gamma, N, K, rho_ret, rho_sign, kappa_hat, sr2_market, sr2_factor, sr2_idio, D_A, D_B, M_A, M_B, G_floor, G_floor_sign, G_tax` ; `step` ∈ {`1-2:F3`, `2-3:F1`, `2-3:F2`, `1-3:F3+F2`} |

## Contraintes globales

- **Fenêtre.** Seules les lignes de W sont lues, sous contrôle bloquant : aucune ligne postérieure au 2019-12-31, aucune ligne du segment monitor.
- **Environnement.** En tête du script, avant l'import de numpy (comme `extract.py`) : threads à 1, `MKL_CBWR=COMPATIBLE`, `MPLBACKEND=Agg`. `PYTHONHASHSEED=42` est exporté par `make` et par les commandes de vérification.
- **Interpréteur.** `.venv/bin/python`, derrière `conda activate Trading`.
- **Aléa.** `SeedSequence` seulement ; aucun état global.
- **E/S.** CSV écrits par `save_fair_csv`. Toute lecture pandas se fait en `float_precision="round_trip"`.
- **Code.**
  - Anglais.
  - Docstring de module à la manière d'E2 ; docstrings d'une ligne sur les fonctions publiques, comme dans `pipelines.py`.
  - Aucun autre commentaire que `# ponytail:` ; aucun `# noqa` ; aucune marque d'IA.
- **Chemins.** Ni le journal ni les CSV ne contiennent de chemin absolu : chemins relatifs à la racine du dépôt.
- **Commit.**
  - Conventional Commits, sans trailer ni co-auteur ; indexation par chemins explicites.
  - Jamais indexés : les liens `.venv`, `data/raw` et `external` du worktree (le motif `.venv/` ne couvre pas un lien symbolique, qui apparaît donc comme non suivi), les fichiers D1/D2 réécrits par le fixture de `make check`, `logs/d4/`.
- **EUROFIDAI.** Aucune donnée lue ni indexée.

## Review Focus

1. **Phases trop courtes ou coupées par les bords de la fenêtre.** Exclues sous 20 jours, sinon découpées ; jamais étendues au-delà de 2019 ; comptées dans le journal. Test : `test_spy_transitions` (Tâche 3).
2. **Médianes débiaisées ≤ 0 (R9).** κ̂ et les gains F2 et 1→3 valent NaN et ne sont jamais remplacés. Test : `test_predicted_nan_on_nonpositive_median` (Tâche 5).
3. **Caractéristique manquante ou direction nulle.** Une NaN vaut 0 ; une norme nulle lève `ValueError`. Test : `test_char_directions` (Tâche 2).
4. **Lecture d'une ligne postérieure à 2019.** Contrôle bloquant (`test_window_and_frozen_basis`, Tâche 1) ; dates des CSV ≤ 2019-12-31 (`test_cli_quick_d2`, Tâche 6).
5. **Échec d'ajustement** (GARCH non convergé, ν̂ ≤ 2, ECME sans convergence). Drapeaux dans les CSV et rapport NaN. Tests : `test_t_ratio` et `test_mvt_nu_recovers_nu` (Tâche 4).

## Fichiers

- **Créés.**
  - `experiments/audit_information.py`, `tests/test_audit.py`.
  - `results/audit/` : les huit CSV ; `figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}` ; `logs/audit/audit.log`.
  - `prompts/plans/plan-11.md`, `prompts/wrapups/wrapup-11.md`, `prompts/GO-stream-11.md` (copie du GO du chercheur).
- **Modifié.** `docs/DEVIATIONS.md` : entrées `C-audit-*` ajoutées en fin de fichier.
- **Non touchés.** `jepadrift/**`, `Makefile`, `requirements*`, `AGENTS.md`, les données dérivées.

---

### Tâche 0 — Préconditions, worktree, enregistrement du plan

- [ ] Créer le worktree.
  - `git -C ~/JEPA-Drift-experiments fetch origin`.
  - `git -C ~/JEPA-Drift-experiments worktree add -b stream-11 ~/JEPA-Drift-stream-11 origin/main`.
  - `ln -s ~/JEPA-Drift-experiments/.venv ~/JEPA-Drift-stream-11/.venv` (chemin absolu développé), puis la même commande pour `data/raw` et `external`.
  - Toutes les commandes suivantes se lancent depuis `~/JEPA-Drift-stream-11`.
- [ ] `git log --oneline -3` : HEAD = `origin/main` (`653ec8b` ou un descendant). `git status --short` : seuls les trois liens apparaissent, non suivis.
- [ ] Référence « avant » : `make check` vert (pyflakes, contrats, tests). Attendu : 22 tests réussis et 4 sautés au premier lancement de pytest (contrats et découplage), 187 réussis au second. En cas d'échec : arrêt déclaré (disjoncteur) et rapport au chercheur. Aucun test d'un autre stream n'est corrigé.
- [ ] GO :
  - copier `prompts/GO-stream-11.md` dans le worktree ;
  - remplir la section « Décision GO intégrée » ;
  - écrire `prompts/plans/plan-11.md` avant toute ligne de code.

### Tâche 1 — Socle : fenêtre, base figée, spectre, η, signes (items 1 et 2)

**Fichiers.** Création de `experiments/audit_information.py` et de `tests/test_audit.py`.

**Interfaces produites.**
- Constantes : `WINDOW = ("2005-01-01", "2019-12-31")`, `N_PC = 20`, `BLOCK = 20`, `BOOT = 2000`, `MAX_DIM = 30`, `MIN_PHASE = 20`, `LW_DAYS = 60`, `GAMMAS = (20, 252)`, `ALPHA = 0.05`, `DATINGS = ("lt_spy", "strict_ps", "symmetric")`, `STREAM = 11`.
- `load(name: str) -> dict`.
  - Clés : `X` (T_W, N), `dates`, `cal` (début, fin de la calib dans W), `eigval`, `eigvec`, `K`, `n_above`, `mp_edge`, `lw`, `state_hash`, `C` (T_W, N, 15) ou None, `chars` (noms).
  - `ValueError` si une date > 2019-12-31 subsiste, ou si le hash diffère du sidecar dont `config` = {K: mp, mode: factor, shrinkage: ledoit_wolf}.
- `spectrum_rows(d) -> list[dict]`, `eta_rows(d) -> list[dict]` et `sign_rows(d, splits) -> list[dict]`, aux colonnes du schéma.

**Étapes.**
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_window_and_frozen_basis`, pour les deux jeux :
    - dates de W comprises entre 2005-01-01 et 2019-12-31 ;
    - K = 5 et 10 ;
    - `mp_edge` = 1.7452090047873516 et 2.261923854892941 (écart relatif ≤ 1e-12) ;
    - `state_hash` égal à `state_sha256` du sidecar (`85147fd9…`, `6c44d64a…`).
  - `test_spectrum_and_eta` :
    - la somme des valeurs propres LW égale la somme des valeurs propres empiriques (écart relatif ≤ 1e-12) ;
    - le nombre de valeurs propres de corrélation au-dessus de λ₊ vaut n₊ ;
    - 15 années ; η_LW ≤ η_emp chaque année.
  - `test_sign_corr_matches_profiles` :
    - ρ̂_signe de la calib égale `mean_sign_corr` (segment calib) de `results/data/d1_d2_profile.csv` pour D2 et de `d3_profile.csv` pour D3 (écart relatif ≤ 1e-12) ;
    - ρ_gauss = sin(πρ̂/2) ; K_eff = 1/ρ̂.
- [ ] Implémenter, puis `pytest -q tests/test_audit.py -k "window or spectrum or sign"` : vert.

### Tâche 2 — Symétrie centrale (item 3)

**Interfaces produites.**
- `triples_test(y) -> tuple[float, float, float]` : (T, z, p).
- `garch_filter(y, omega, alpha, beta) -> np.ndarray` : σ̂_{t|t−1}.
- `garch_scale(y) -> tuple[np.ndarray, dict]` : σ̂ et {`omega`, `alpha`, `beta`, `converged`}.
- `char_directions(C, V_f) -> np.ndarray` : tableau (T, N, P) de directions unitaires, orthogonales à V_f.
- `projections(d) -> dict[str, np.ndarray]` : séries `PC1` … `PC20` et `char:<nom>`.
- `symmetry_rows(name, series) -> list[dict]`.

**Étapes.**
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_triples_matches_brute_force` : échantillon de Student t(4), n = 37, `SeedSequence([11, 0])`. T, ΣB_t² et ΣB_st² sont égaux, comme entiers, à ceux d'une énumération en O(n³) écrite dans le test ; z suit la formule.
  - `test_triples_null_and_power` :
    - 400 échantillons N(0,1) de n = 100 (`SeedSequence([11, 1])`) : taux de rejet à 5 % dans [0,022 ; 0,078], la région binomiale à 99 % ;
    - 50 échantillons exponentiels de n = 100 : rejet ≥ 90 %.
  - `test_garch_filter_predictable` : à paramètres fixés, perturber y[t₀:] laisse σ̂[:t₀+1] identique au bit près.
  - `test_char_directions` : ‖V_fᵀu‖_∞ < 1e-12 et ‖u‖ = 1 ; une caractéristique contenue dans span(V_f) lève `ValueError`.
  - `test_symmetry_holm_joint` : quatre séries synthétiques, trois symétriques et une décalée. Seules les p-values de la série décalée rejettent. Les p-values ajustées égalent `multipletests(p_all, method="holm")[1]` sur la famille jointe.
- [ ] Implémenter ; tests verts.

### Tâche 3 — Transitions, SR² débiaisé, bootstrap (item 4)

**Interfaces produites.**
- `spy_phases(variant, dates) -> list[tuple[int, str, str, np.ndarray]]` : (id, début, fin, lignes de W).
- `transitions(phases) -> list[tuple[int, int]]` : paires de phases consécutives gardées.
- `debiased_sr2(Y1, Y2) -> tuple[float, float, float]` : (raw, debiased, spec). `ValueError` si ν ≤ d + 1.
- `mbb_indices(n, B, rng) -> np.ndarray` : tableau (B, n).
- `subspaces(d, proj) -> dict[str, np.ndarray]` : les blocs.
- `drift_rows(d, dating, Ys, B) -> list[dict]`.

**Étapes.**
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_debiased_sr2_unbiased` : Σ = I₃₀, n₁ = n₂ = 250, 252‖Δ‖² = 4, 2000 réplications indépendantes (`SeedSequence([11, 3])`, deff = 1).
    - |moyenne(`debiased`) − 4| < 4 SE ;
    - |moyenne(`spec`) − (4 + 252·c·d·(d + 1)/ν)| < 4 SE ;
    - avec Δ = 0 : |moyenne(`debiased`)| < 4 SE.
  - `test_mbb_indices` : forme (B, n), valeurs dans [0, n), séquences de 20 indices consécutifs (la dernière tronquée) ; une même graine redonne le même tableau.
  - `test_spy_transitions`, sur les dates de D2 :
    - `strict_ps` donne 10 transitions, la première à 2007-10-09 avec (696, 355), la dernière à 2018-12-24 avec (65, 256) ;
    - `lt_spy` en donne 9, sans 2008-10-27, 2008-11-04 ni 2008-11-20 ;
    - toutes les lignes sont ≤ 2019-12-31.
  - `test_drift_rows_sums` : panel synthétique (N = 70, K = 3, deux phases). Par transition et par tirage, `residual_full` = `factor` + `idio` = `factor` + somme des blocs. Chaque bloc a d ≤ 30.
- [ ] Implémenter ; tests verts.

### Tâche 4 — Plafonds N1 à N3 (item 5)

**Interfaces produites.**
- `n1(Z) -> tuple[float, float]` : valeur brute et valeur corrigée.
- `info_ratio(A, sigmas) -> tuple[np.ndarray, np.ndarray, np.ndarray]` : (rapport, I_cond, I_stat) par direction. A est (T, N, m) ou (N, m) diffusé ; `sigmas` est un itérable des Σ_t.
- `rolling_lw(X, days=LW_DAYS)` : générateur des Σ_t pour t ≥ `days`.
- `mvt_nu(Z, max_iter=500, tol=1e-6) -> tuple[float, int, bool]`.
- `t_ratio(nu) -> float`.
- `ceiling_rows(d, proj, scales) -> list[dict]`.

**Étapes.**
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_n1` : lignes de ±1 (s² ≡ 1) → N1 brut = 1 ; mélange d'échelles {1, 2} à parts égales → 1,5625.
  - `test_info_ratio` : Σ_t constant → rapport 1 (écart relatif ≤ 1e-12) ; Σ_t de Wishart et a_t aléatoires → rapport ≥ 1.
  - `test_mvt_nu_recovers_nu` : loi t multivariée, ν = 5, d = 5, n = 20 000 (`SeedSequence([11, 4])`). |ν̂ − 5| < 0,5, avec convergence.
  - `test_t_ratio` : t_ratio(5) = 1,25 ; t_ratio(2) = NaN ; t_ratio(1e6) = 1 à 1e-5 près.
- [ ] Implémenter ; tests verts.

### Tâche 5 — Part du budget et gains prévus (items 6 et 7)

**Interfaces produites.**
- `budget_rows(drift: pd.DataFrame) -> list[dict]`.
- `planning_gains(N, K, rho, rho_sign, sr2_m, sr2_f, sr2_i, gamma) -> list[dict]` : les quatre étapes.
- `predicted_rows(signs, drift, dims) -> list[dict]`.

**Étapes.**
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_budget_share` :
    - L = 300 et SR² = 10 donnent L·Î = 5,95 : dans le budget à γ = 20 comme à γ = 252 ;
    - SR² = 9 donne 5,36 : dans le budget à 20, hors budget à 252 ;
    - SR² < 0 : hors budget.
  - `test_planning_table_reproduced`, avec N = 97, ρ = 0,40, ρ_s = 0,26 et SR²_i/SR²_m choisi pour que κ² = 0,25 :
    - G(1→2) = 97/39,4 = 2,4619 ; G_signe = 97/25,96 = 3,7365 ;
    - G(2→3, F2) = 16,4167 ; G(1→3) = 42,879. Le tableau donne 2,5, 3,7, 16 et 43 ;
    - κ² = 1/16 et κ² = 1 donnent 4,104 et 65,67 ;
    - avec N = 239 : 10,02, 40,08 et 160,3, et G(1→3, κ = 0,5) = 102,07 ;
    - G_tax = G·M(1, γ)/M(D, γ), M calculé par `mixture_multiplier`.
  - `test_predicted_nan_on_nonpositive_median` :
    - SR²_i ≤ 0 : κ̂, G(2→3, F2) et G(1→3) valent NaN ; `1-2:F3` ne change pas ;
    - SR²_m ≤ 0 : toutes les étapes 2→3 et 1→3 valent NaN.
- [ ] Implémenter ; tests verts.

### Tâche 6 — CLI, CSV, journal, figures

**Interfaces produites.**
- `main(argv=None) -> int`, avec les options du tableau des décisions.
- `plot(out, fig_dir) -> None` : relit les CSV et écrit `spectrum`, `symmetry`, `drift_sharpe` et `budget_share` en PNG et en PDF.
- Journal `audit.log`, sans chemin absolu, qui consigne :
  - la commande lancée ;
  - le SHA-256 des entrées : `ret_wide.npy`, `phases_*.csv`, `chars.parquet`, sidecars Z ;
  - les lignes par jeu et K ;
  - les transitions gardées et exclues, avec le motif ;
  - le nombre d'estimations débiaisées négatives par sous-espace ;
  - les GARCH non convergés et l'état de l'ECME ;
  - la durée et le SHA-256 des huit CSV.

**Étapes.**
- [ ] Charger le skill `dataviz` avant d'écrire le code des figures ; s'il est absent, poursuivre sans (instruction du GO).
- [ ] Écrire les tests, qui doivent d'abord échouer.
  - `test_cli_quick_d2` : `main(["--datasets", "d2_us97", "--quick", "--out", …, "--fig-dir", …, "--log-dir", …]) == 0`.
    - huit CSV aux colonnes exactes du schéma ;
    - quatre PNG et quatre PDF ;
    - `str(REPO_ROOT)` absent du journal ;
    - toutes les `boundary` ≤ 2019-12-31 ;
    - durée visée : moins de 30 s.
  - `test_cli_rejects_bad_boot` : `--boot 0` → `SystemExit`.
- [ ] Implémenter ; tests verts.

### Tâche 7 — Exécution complète, déterminisme, documentation, clôture

- [ ] Lancer `python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit`, puis une seconde exécution vers un répertoire du scratchpad. Les SHA-256 des huit CSV doivent être identiques (critère de succès). Consigner la durée.
- [ ] Relire les sorties :
  - estimations négatives (R9) signalées dans le journal ;
  - cohérence avec les sondes : K, ρ̂, N1, ν̂.
- [ ] `docs/DEVIATIONS.md` : entrées `C-audit-debias`, `C-audit-subspaces`, `C-audit-transitions`, `C-audit-ceilings` et `C-audit-gains`, selon les décisions du GO.
- [ ] `pytest -q tests/test_audit.py`, puis `make check`.
- [ ] Fin de stream, dans l'ordre d'AGENTS.md.
  1. Skill `wrap-up` → `prompts/wrapups/wrapup-11.md`.
  2. `tools/reindex_graphify_jcodemunch.sh`.
  3. `make check`, puis `git status --short` et indexation par chemins explicites. Contrôle de `git diff --staged` : aucun lien, aucun fichier du fixture D1/D2, aucun chemin absolu, aucun fichier de plus de 50 Mo. Commit `feat(audit): add the information audit of D2 and D3 (stream 11)`, sans trailer.
  4. `git fetch origin` et `git rebase origin/main`. En cas de conflit sur `docs/DEVIATIONS.md`, garder les deux blocs. Relancer `make check` si la base a bougé. Contrôler la plage `origin/main..stream-11` : aucun chemin sous `data/raw/eurofidai/` ni `data/derived/d4_eurofidai/`, aucun fichier de plus de 50 Mo. Puis `git push origin stream-11:main`. Rapporter le hash du commit et l'état propre de l'arbre.
  5. Instruction du GO : retirer la copie non suivie `prompts/GO-stream-11.md` de l'arbre principal, désormais suivie dans `main`. Puis, si `git status` de cet arbre ne montre que les fichiers étrangers connus, l'avancer par `git merge --ff-only origin/main`.

## Vérification de bout en bout

Depuis `~/JEPA-Drift-stream-11` :

```bash
source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
ls results/audit && sha256sum results/audit/*.csv
S=<répertoire scratchpad de la session>
python experiments/audit_information.py --datasets d2_us97 d3_239 --out $S/audit2 --fig-dir $S/fig2 --log-dir $S/log2
diff <(cd results/audit && sha256sum *.csv) <(cd $S/audit2 && sha256sum *.csv)
pytest -q tests/test_audit.py
make check
```

## Risques

| Risque | Parade |
|---|---|
| R9 : bruit des blocs résiduels (sonde 4 : de −589 à 2422) et médianes négatives | Estimations rapportées telles quelles, avec IC bootstrap ; NaN propagé dans les gains ; décompte dans le journal. Le GO peut relever `MIN_PHASE` |
| Les points de retournement de SPY sont choisis ex post : le SR² du marché est gonflé, car le débiaisage ne corrige que le bruit. Les gains 2→3, rapports SR²_x/SR²_m, sont alors sous-estimés | Signalé dans le journal et le wrapup. Frontières placebo hors périmètre |
| Durée : triplets ≈ 1,1 s × 55 directions, ≈ 375 ajustements GARCH, bootstrap ≈ 60 s, ECME ≈ 30 s | Environ 3 à 5 minutes au total ; `--quick` pour le test (moins de 30 s) |
| Mémoire du bootstrap (statistiques par phase de D3) | Boucle par sous-espace, environ 200 Mo au plus. Commentaire `# ponytail:` sur le rééchantillonnage direct ; précalcul des sommes par bloc si la durée l'exige |
| GARCH non convergé, ν̂ ≤ 2, ECME sans convergence | Drapeaux et NaN dans les CSV, jamais de repli silencieux |
| Conflit au rebase avec un stream parallèle, sur `docs/DEVIATIONS.md` | Garder les deux blocs, relancer `make check` |
| Après le push, une copie non suivie du GO reste dans le worktree principal et bloquerait l'avance rapide de `main` dans ce worktree | Retirée après le push, avant l'avance rapide (Tâche 7, étape 5, instruction du GO) |
| Les liens du worktree apparaissent comme non suivis | Jamais indexés, puisque l'indexation se fait par chemins |

## Hors périmètre

- D3_500 et D4 (EUROFIDAI) ; caractéristiques de D2, différées (GO H4).
- `docs/MAPPING.md` : aucun nombre de l'article n'est encore cité. `docs/sections/` : le prompt ne demande pas de note.
- Déplacement de `debiased_sr2`, `mbb_indices` et `triples_test` vers `jepadrift/stats/`, à faire quand E4 en aura besoin.
- Prédictions à information égale (convention (a)) pour les directions injectées d'E1 : E1 dispose de ces directions.
- Frontières placebo pour mesurer le biais de sélection ; déduplication de `lt_spy` et `symmetric`.
