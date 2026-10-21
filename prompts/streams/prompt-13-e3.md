## PROMPT 13 — E3 : calibration sous H₀ (exactitude des flux, ARL₀ des e-détecteurs, Γ spectral contre Γ opérationnel)

### Contexte
E3 vérifie, sans aucune dérive, que chaque moniteur de JEPA-Drift tient sa garantie de fausse alarme :
- le niveau exact du treillis pour les flux de signe ;
- ARL₀ ≥ γ pour les e-détecteurs ;
- FPR(H) ≈ α pour les seuils bootstrap ou randomisés.

Il mesure aussi ce que coûtent l'hétéroscédasticité (Γ) et l'asymétrie des données brutes. E3 fournit le §5.2 et le critère (i) de J2. Lire `CLAUDE.md`.

Définitions :
- **Γ^spec** = 1 + 2Σρ(k) de la statistique surveillée (`monitors.gamma.gamma_spectral`).
- **Γ^op** = λ_requis/λ_iid pour tenir la cible.
- **Région à 99 %** : p ± z√(p(1 − p)(1/n + 1/n_cal)), avec z = 2,5758 (`C-pipe-null-targets`).

### Tâche
Écrire `experiments/e3_calibration.py`. Les lignes réelles sont limitées à 2005-01-04 → 2019-12-31, avec un contrôle bloquant.
1. **Fonds.**
   - D5 : GARCH(0,08 ; 0,90) à innovations t₇ et gaussiennes, via `sim.Garch` (vectorisé sur les réplications). Si un panel à facteur est nécessaire, ajouter un axe de réplication à `sim.garch_panel` sans changer ses sorties quand l'axe n'est pas utilisé (test de non-régression).
   - D6 : SYM-`d2_us97` et SYM-`d3_239`, par les blocs empilés de `pipelines.null_check`.
   - Placebo brut : `d2_us97` et `d3_239`.
2. **Pipelines et lectures.**
   - P1-C : flux d'étiquettes Article B (q̂ de calib) et flux exact centré en 1/2. CUSUM au treillis, comparé à `select_threshold(...)["threshold"]`.
   - P1-D : règle λ_iid × Γ̂ (Γ̂ issu du GARCH de R01) contre seuil opérationnel.
   - P2-C : bootstrap R15 (H = 750) et e-détecteur de pari sur la fraction des signes bruts.
   - P3-C : canaux exacts et dictionnaire d'e-détecteurs. Pour l'option mélange, avec la porte corrigée de la multiplicité (prompt 12), mesurer le FPR pour qualifier sa validité approchée.
   - P3-D : fenêtres nulles de calib (H ≤ 941). Pour H = 2 000, utiliser les fenêtres `pre_monitor` et rapporter la non-stationnarité de l'énergie (Γ^op ≈ 191 et 2 346 sur D2, `C-P3D-windows`).
   - P3-CS : (a) randomisation et e-processus ; (b) e-détecteur à mise prévisible.
3. **Mesures.**
   - FPR(H) pour H ∈ {750, 2 000}, avec région à 99 % ; 20 000 trajectoires nulles par cellule de signe. Référence : le niveau exact du treillis pour les flux de signe, α pour le bootstrap et la randomisation.
   - ARL₀ Monte Carlo des e-détecteurs, de types SR et CUSUM (P2-C, P3-C, P3-CS b) :
     - γ ∈ {20, 100, 252}, sur pièces équitables, D6 et brut ;
     - T_max = 60γ, avec la censure rapportée (une moyenne censurée est une borne inférieure) ;
     - la marge du type SR est mince par construction (E∞[τ] = E∞[M_τ]). Un échec imputable à la plateforme est consigné, jamais corrigé par un nouveau tirage de graines.
   - Γ^spec contre Γ^op pour chaque statistique à amplitude.
4. **Asymétrie des données brutes.**
   - Sur le placebo brut, mesurer le FPR de chaque canal de P3-C et de P1-C, en flux exact (1/2) et en flux recentré (q̂ de calib).
   - Une inflation du FPR est attendue sur les canaux dont la symétrie est rejetée (AGENTS.md). La relier à `results/audit/symmetry_tests.csv`.
5. **Pénalité de dépassement**, à reproduire à ±5 % avec 2 000 trajectoires. CUSUM de premier ordre sur x/σ_inconditionnel, GARCH(0,08 ; 0,90) gaussien :
   - δ = 0,5, λ = 6 : ARL₀ ≈ 2 587 en i.i.d. contre ≈ 889 sous GARCH ;
   - δ = 1, λ = 3 : 1 894 contre 669 ;
   - CUSUM de signe : 213 contre 214 (exact).
6. **Encodeurs à fenêtre.** Avec z_t = moyenne sur L jours de uᵀx, L ∈ {5, 20, 60}, mesurer :
   - Γ_z^spec, attendu ≈ L ;
   - le FPR d'un CUSUM calibré en i.i.d. ;
   - Ljung–Box (20 retards) sur les signes de z.

   Ces mesures justifient un chemin surveillé jour par jour.
7. **Contrôle J2** dans `results/e3/e3_j2_check.txt` : pour chaque flux de signe exact sur D6, |FPR − niveau du treillis| ≤ 1 point.

### Entrées
Streams 4 à 8 et 8b ; `results/audit/symmetry_tests.csv` ; `CLAUDE.md`.

### Livrables
`experiments/e3_calibration.py`, `configs/e3.yaml`, `results/e3/{e3_cells.csv,e3_arl0.csv,e3_raw_placebo.csv,e3_overshoot.csv,e3_window_encoders.csv,e3_j2_check.txt}`, `figures/e3/*`, `logs/e3/`.

### Contraintes techniques
- Graines `SeedSequence` par (13, cellule, réplication) ; résultats indépendants de `--jobs`.
- IC de Wilson ; option `--quick`.
- Aucune ligne datée de 2020 ou après.

### Critères de succès
- Flux exacts dans la région à 99 % du niveau exact.
- ARL₀ des e-détecteurs ≥ γ, ou censure documentée.
- Pénalité de dépassement reproduite.
- Inflation du FPR brut attribuée canal par canal.
- Contrôle J2 écrit.

### Commandes de vérification
```bash
python experiments/e3_calibration.py --quick --out results/e3_quick
python experiments/e3_calibration.py --out results/e3 && cat results/e3/e3_j2_check.txt
```