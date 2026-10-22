## PROMPT 12 — E1 : le problème (§2) sur fonds réels symétrisés, pipelines 1 → 2 → 3 et critères de J2

### Contexte
E1 mesure le coût de détection selon le pipeline, à cible nominale commune et, seulement lorsque les FPR atteints le permettent, à fausse alarme appariée :
- un actif seul (P1) ;
- le pooling des signes (P2) ;
- la projection orthogonale au marché (P3) ;
- la coupe de degré 0 (P3-CS, canal N1).

Les dérives sont injectées dans des fonds réels symétrisés (D6) de 2005–2019. Les gains mesurés sont comparés à des prévisions calculées à partir des dérives injectées. Ces prévisions emploient une information quadratique gaussienne de conception, pas la KL exacte des fonds D6. E1 fournit les chiffres du §2 et les critères de J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **Délai** : `delay = alarm_index − tau_star + 1` pour une alarme observée (`C-pipe-delay`). Les onsets uniformes avec censure à H donnent `ADD_H = mean(min(T,H))`, avec `min(T,H)=H` pour une trajectoire sans alarme, puis la moyenne et la médiane des alarmes détectées et le taux de censure ; ils n'estiment pas le pire cas de Lorden. Réserver le terme ADD de Lorden aux bornes analytiques.
- **Lectures à horizon H**, avec cible nominale α = 0,05 et FPR(H) observé rapporté par cellule :
  - anytime-valid : e-détecteur arrêté à γ_H = H/α (`pipelines.horizon_gamma`), car P∞(alarme avant H) ≤ H/γ ;
  - exacte : CUSUM de signe au niveau atteignable du treillis ≤ α à l'horizon H. La statistique se compare à `select_threshold(...)["threshold"]` (point milieu), jamais à `lam` ;
  - bootstrap (portage R15, H = 750) et randomisation (inversion de signe) : FPR(H) empirique visé ≈ α, sans garantie automatique.
- **G_ADD,H** = ADD_H,A/ADD_H,B, rapport de délais restreints à lecture et H égaux ; rapporter la censure et ne pas le présenter comme le rapport des ADD de Lorden.
- **G_floor** = I_B/I_A, rapport des informations quadratiques gaussiennes de conception calculées à partir des Δ injectés.
- **Alignement** a_max = max_k Δz_k²/‖Δz‖² : part de cette information quadratique portée par le meilleur canal, en coordonnées blanchies.

### Tâche
Écrire `experiments/e1_problem.py`. Seules les lignes du 2005-01-04 au 2019-12-31 sont lues, avec un contrôle bloquant. L'option `--include-test-window` est refusée tant que `configs/FROZEN.json` est absent ou ne correspond pas (prompt 21).

0. **Socle.**
   - Briques à utiliser : `pipelines.run_pipeline` et `pipelines.null_check` ; `injection.symmetrize`, `inject` et `draw_tau_star` (avec un cache de `fit_background` par jeu, fenêtre et K) ; `data_loader.chars` ; `stats.drift` ; `floors`.
   - États des représentations : ajustés une seule fois par jeu et par représentation, sur les lignes de calib du panel d'origine. Ces lignes sont sans dérive, et D6 laisse les moments d'ordre 2 inchangés. Ces états sont passés à `run_pipeline` ; jamais `state=None` avec des enregistrements injectés.
   - À H = 2 000, tout onset qui tient avant fin 2019 précède la calib 2016–2019 : l'état est ajusté sur des dates ultérieures à l'onset. Cette lecture est rétrospective, sans interprétation prospective, même si les nouveaux tirages de signes D6 permettent un contrôle conditionnel du nul.
1. **Fonds et onsets.**
   - Une symétrisation D6 neuve par réplication.
   - τ* uniforme, tel que [τ*, τ* + H) tienne dans la fenêtre.
   - Jeux : `d2_us97` et `d3_239`.
   - F2 sur `d3_239` seulement (D2 n'a pas de caractéristiques), via `load_chars_tensor` ; NaN remplacés par 0 et comptés.
   - Rapporter l'information réalisée après τ* à partir de `delta`, puisque F2 suit C_t.
2. **Bras A — gains à information égale.**
   - Convention (a) : SR ∈ {2, 4, 8}. SR = 1 est exclu : il est censuré pour tous les pipelines, avec τ_γ ≈ 5 340 jours à γ_H = 40 000.
   - Familles F3, F1 et F2 ; 1 000 onsets par cellule ; H = 2 000 ; γ_H = 40 000.
   - Pipelines :
     - P1-C : flux de signe exact de chaque titre d'un échantillon de 20 titres tirés avec graine ; on rapporte la médiane et le meilleur titre, ce dernier étant un oracle post hoc choisi sur les mêmes réplications ;
     - P2-C : lecture anytime-valid avec K = N. La lecture Article B (bootstrap R15 recalibré sur une symétrisation, H = 750, `C-P2C-port`) figure en cellules secondaires ;
     - P3-C : dictionnaire d'e-détecteurs CUSUM sur le canal marché et le résiduel factoriel (résiduel complet pour F2). En diagnostic seulement : la lecture exacte du meilleur canal, oracle post hoc, et la lecture « mélange » (option `mixture_s2`), étiquetée « validité approchée ». Implémenter pour cette dernière la porte d'indépendance avec correction de Holm au niveau de famille de 1 % sur les p-valeurs des paires ; un non-rejet ne démontre pas l'indépendance ;
     - P3-CS : (b) mise prévisible ∝ 1/σ̂ en principal ; (a) e-processus pivot en secondaire ;
     - P7 : rapporté comme borne.
   - P3-D (capteur Data) est traité à part : H = 750, fenêtres nulles de calib (`C-P3D-windows`). Il est rapporté comme preuve d'orthogonalité, jamais dans les tableaux de gains de localisation.
3. **Bras B — lois d'échelle (J2).**
   - Convention (b) :
     - F3 avec un SR RMS par titre ∈ {2, 4}, sur `d2_us97` et `d3_239` ;
     - F2 avec κ ∈ {1, 2}, sur `d3_239`.
   - La grille d'amplitude est choisie sur les fonds 2005–2019 de sorte que le délai médian de P3-C reste dans [20 ; 0,8·H] sur toute la grille de N. Ce choix est un degré de liberté : le consigner.
   - N ∈ {8, 16, 32, 64, 97} pour D2 et {8, 16, 32, 64, 128, 239} pour D3. Par N : 20 sous-ensembles emboîtés tirés avec graine, communs à tous les pipelines, et 200 onsets par (sous-ensemble, cellule).
   - Pipelines : P2-C sur F3 ; P3-C (résiduel complet) et P3-CS (b) sur F2.
   - Pente :
     - figer avant les injections, par graine, un titre de référence P1 inclus dans tous les sous-ensembles emboîtés ; la pente de log G_ADD,H en log N n'est l'opposé de celle de log ADD_H de P3 que si cette référence reste effectivement constante en N ; sinon, estimer directement la pente du rapport ;
     - la médiane n'est définie que si le taux de détection dépasse 50 % ; sinon, la cellule est exclue et signalée ;
     - IC par bootstrap sur les sous-ensembles ;
     - a_max(N) est rapporté pour attribuer une pente faible à l'information ou à l'alignement.
4. **Bras C — phases réelles (descriptif).** Phases des trois datations comprises dans 2005–2019.
   - Part des phases dans le budget, par sous-espace : L·Î ≥ ln γ, γ ∈ {20, 252}, en lecture budget, avec `stats.drift.debiased_sr2`.
   - Parts placebo par `rotate_phases` (2 000 rotations). Les deux parts sont rapportées. L'Î intra-phase est gonflé par la sélection des frontières (`C-audit-placebo`) : les parts sont présentées comme des bornes supérieures. Le placebo teste l'alignement avec les datations choisies ; il n'identifie pas une fraction causale de la dérive.
   - Alarmes dans les phases sur données brutes :
     - P1-C, en flux d'étiquettes Article B avec q̂ de calib ;
     - P3-C, avec recentrage sur q̂ de calib pour les canaux dont la symétrie est rejetée (`CLAUDE.md`).

     Ce bras est descriptif : aucune exactitude n'est revendiquée.
   - `results/audit/predicted_gains.csv` est cité tel quel (NaN conservés), jamais complété.
5. **Prévisions, à partir des Δ injectés.**
   - Information quadratique gaussienne de conception de l'oracle : I_x = ½ΔᵀΣ̂⁻¹Δ. Ne pas l'appeler KL exacte des fonds D6.
   - Pour chaque pipeline : information de son sous-espace, avec Δz = WᵀΔ dans la base figée.
   - Délai prévu du dictionnaire : environ (ln γ_H + ln K_canaux)/(e·a_max·I_z). Ici e = 4f̂(0)² est l'efficacité du signe estimée sur la calib (2/π sous normalité).
   - Budget d'évidence de P7 : ln γ_H/I_x (Lemme 1), distinct d'un ADD prédit à seuil fini.
   - Rapporter les gains prévus et mesurés côte à côte seulement pour des estimands compatibles : prédiction restreinte à H ou cellules à censure négligeable ; sinon étiqueter la comparaison comme non directement interprétable. Pour P3-CS (b), rapporter la borne N1 = E[σ²]E[σ⁻²] de l'audit (≈ 1,97).
6. **Mesures.**
   - ADD_H, moyenne et médiane des alarmes détectées, taux de détection dans H et censure, sans les confondre.
   - G_ADD,H par lecture ; G_floor.
   - G_SR, en mesure secondaire, sur une grille réduite (F3 et F2 ; bissection en 6 pas de 200 onsets).
   - K_eff (`sign_diagnostics`).
   - FPR(H) observé et IC lorsque les réplications le permettent. Les fenêtres brutes chevauchantes restent descriptives, sans IC binomial indépendant. Qualifier les gains à seuil nominal commun de tels ; « à fausse alarme égale » exige une calibration iso-FPR sur données indépendantes ou une marge d'équivalence fixée avant test avec IC de la différence. Le simple chevauchement des IC ne suffit pas.
7. **Résumé J2** dans `results/e1/e1_j2_summary.txt`, une ligne PASS/FAIL par critère :
   - (i) flux de signe exacts sur D6 (P1-C sur 5 titres, canaux de P3-C), H ∈ {750, 2 000}, 2 000 réplications par `null_check` : |FPR − niveau du treillis| ≤ 1 point ;
   - (ii) pente de P2-C sur F3 pour N ≥ 20 : IC à 95 % contenant 0, ou borne haute < 0,15 ;
   - (iii) pente de P3-C sur F2 positive, avec un IC à 95 % excluant 0. En cas d'échec, consigner l'attribution (a_max, pente de P3-CS (b), lecture mélange) et renvoyer à la contingence C1 (prompt 23, phase 1) ;
   - (iv) tableau des gains 1 → 2 → 3 → 3-CS à SR = 4 (convention a), mesurés et prévus.

### Entrées
Streams 2 à 8, 8b et 11 ; `results/audit/*.csv` ; `CLAUDE.md`.

### Livrables
- `experiments/e1_problem.py`, `configs/e1.yaml`.
- `results/e1/{e1_cells.csv,e1_slopes.csv,e1_real_phases.csv,e1_null.csv,e1_j2_summary.txt}`, `figures/e1/*`, `logs/e1/`.
- Entrées `C-e1-*` de `docs/DEVIATIONS.md` pour tout choix de grille ou de lecture.

### Contraintes techniques
- Graines `SeedSequence` par (12, cellule, réplication) ; résultats indépendants de `--jobs` (pool `spawn`).
- Les e-détecteurs de dictionnaire sont traités par paquets : aucun tableau (J, K, T) au-delà de 2 Go par paquet.
- `--quick` (100 onsets, SR = 4, N ∈ {16, 64}) en moins de 10 minutes.
- Run complet visé en moins de 8 h sur 48 cœurs ; sinon, effectifs réduits et consignés.
- Aucune ligne datée de 2020 ou après.
- Bootstrap R15 à H = 750 : `H_ref + H = 1 500` dépasse les 941 jours de calib ; utiliser `null_rows=pre_monitor` et étiqueter cette calibration rétrospective. Rédiger les nouveaux audits en anglais.

### Critères de succès
- Deux runs `--quick` identiques au SHA-256.
- Résumé J2 rempli, avec IC et verdicts.
- Chaque nombre du §2 présent dans un CSV ; prévisions et mesures côte à côte.

### Commandes de vérification
```bash
.venv/bin/python experiments/e1_problem.py --quick --out results/e1_quick
.venv/bin/python experiments/e1_problem.py --quick --out /tmp/e1_quick2 && diff <(cd results/e1_quick && sha256sum *.csv) <(cd /tmp/e1_quick2 && sha256sum *.csv)
.venv/bin/python experiments/e1_problem.py --out results/e1 && cat results/e1/e1_j2_summary.txt
```
