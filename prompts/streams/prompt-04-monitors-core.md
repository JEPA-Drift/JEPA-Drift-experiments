## PROMPT 4 — Surveillance (1/3) : noyau univarié, treillis exact et e-détecteurs, portage de l'Article B

### Contexte
La bibliothèque de surveillance est le socle de tous les pipelines de JEPA-Drift. Elle doit d'abord reproduire exactement les moniteurs du code public de l'Article B, puis fournir les détecteurs exacts de l'Article C. Bloquant pour J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **CUSUM strict** : S_t = max(0, S_{t−1} + s_t − δ), alarme si S_t > λ.
- **Flux d'étiquettes** : 1{r_t > 0} − q̂.
- **Flux de signe exact** : 1{y_t > 0} − 1/2, i.i.d. Bernoulli(1/2) sous toute hypothèse nulle à symétrie centrale.
- **Treillis** : niveaux de fausse alarme discrets d'un CUSUM sur un flux à deux points.
- **e-détecteur** : statistique M ≥ 0 telle que l'alarme à M ≥ γ garantit ARL₀ ≥ γ.
- **Γ** : facteur d'inflation de variance de la statistique surveillée, Γ = 1 + 2Σ_k ρ(k).

### Tâche
1. **`jepadrift/monitors/cusum.py`.**
   - Porter sans modification `strict_cusum`, `get_multiple_alarms` et `get_cusum_trajectory` (`~/The-Whitening-Advantage-Experiments/experiments/R01_real_world_backtest/exp_R01_real_world_backtest.py`, l. 110–142).
   - Porter `bilateral_delay` et `cusum_max_bilateral` (`~/The-Whitening-Advantage-Experiments/experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py`, l. 343–360).
   - Ajouter des versions vectorisées (R × T) aux résultats identiques.
2. **`lattice.py`.** Loi exacte d'un CUSUM sur un flux à incréments entiers +a / −b, avec P(+) = q, par chaîne de Markov :
   - FPR à l'horizon H et ARL₀ ;
   - unilatéral, et bilatéral par chaîne jointe (S⁺, S⁻) ;
   - comparaisons stricte et large ;
   - fonctions `attainable_levels()` et `select_threshold(nominal, rule="at_or_below", comparison="strict")`.
3. **`streams.py`.**
   - `label_stream(r, q_hat)` (R01) ;
   - `exact_sign_stream(y, rng)` : y = 0 tranché par une pièce équitable, `rng` passé explicitement ;
   - `energy_stream(r, mu, sigma)` = (r² − μ̂)/σ̂ (R01).
4. **`jepadrift/stats/garch.py`** (scipy autorisé ici, hors `monitors`) : porter sans modification `_garch_nll`, `fit_garch_qmle` et `compute_gamma_exact` (R01, l. 72–108).
5. **`gamma.py`.**
   - Γ̂ spectral = 1 + 2Σ_{k≤L}(1 − k/(L+1))ρ̂(k), avec L = ⌊4(n/100)^{2/9}⌋.
   - Γ^op = λ_requis/λ_iid à ARL₀ ou FPR fixé, par bissection monotone sur des trajectoires nulles fournies.
6. **`eprocess.py`.**
   - (a) e-processus de pari sur bits équitables, avec mise prévisible |λ_t| < 1.
   - (b) Portage de MIX depuis `build_mixture_kernel` (R09) : 16 départs `np.linspace(0, H-1, 16, dtype=int)` × η₀ ∈ {0.05, 0.10, 0.15} × côtés ±1, poids 1/96, valeur 1 avant le départ, H = 5000.
   - (c) e-détecteurs SR (M_n = (1 + M_{n−1})·f_n) et CUSUM (M_n = max(1, M_{n−1})·f_n), moyennés sur la grille de mises {0.05, 0.10, 0.15, 0.20} × côtés.
   - (d) Moyenne de dictionnaire sur des directions, valide quelle que soit leur dépendance.
   - (e) Mélange sous-gaussien fermé de la Prop. 3, documenté comme « valide si les coordonnées sont indépendantes sous H₀ ».
7. **Configurations P1.**
   - Concept, Article B : CUSUM bilatéral strict, δ = 0.1, λ = 10. q̂ est estimé sur 2018-01-02…2019-12-31 (mode réel) ou sur les 250 jours qui précèdent l'onset (mode injection).
   - Concept, Article C : flux exact centré en 1/2, λ issu du treillis.
   - Data, Article B : δ = 0.5, λ = 65·Γ̂, avec Γ̂ ajusté une seule fois sur 2018–2019 (écart R01-gamma-hat-refit du registre B).
8. **Contrôles d'identité, bloquants** (chargeur du prompt 2) :
   - reproduire `~/The-Whitening-Advantage-Experiments/results/R01_real_world_backtest/data/R01_{garch_models,covid_alarms,covid_trajectories,placebo_control,injection_summary,magnitude_sweep}.csv`. Exemple pour SPY : α = 0.211551, β = 0.729081, Γ̂ = 14.998367977816738, q̂ = 0.55864811133200798, aucune alarme en 2020 ;
   - reproduire la colonne `exact_level` des lignes `exact_survival` de `~/The-Whitening-Advantage-Experiments/results/R08_adverse_lattice/data/R08_lattice_exact_law.csv` à 1e-12 en relatif (H = 5000, λ de 10 à 13 par pas de 0.2, q = 0.5). Exemples : 0.051020717214682557 à λ = 11.2, 0.043428228893176074 à λ = 11.4.
9. **Deux environnements.** Exécuter les contrôles R01 dans `.venv` (numpy 2.4.4) et dans un second venv `external/articleB-venv/` créé côté projet (`python -m venv external/articleB-venv && external/articleB-venv/bin/pip install -r ~/The-Whitening-Advantage-Experiments/requirements.txt` : numpy 1.26.4, scipy 1.16.2). Le dépôt `~/The-Whitening-Advantage-Experiments` reste en lecture seule (le venv est hors de ce dépôt ; `external/` est ignoré par git). SLSQP peut différer d'une version de scipy à l'autre : tout écart va dans `docs/DEVIATIONS.md` sous `C-R01-env`.
10. **Contrôles Monte Carlo.**
    - Flux de signe exact sur GARCH(0.08 ; 0.90)-t₇ (importer `Garch` depuis `experiments/e2_floor_validation.py`) : le FPR du CUSUM calibré sur le treillis tombe dans l'IC binomial à 99 % du niveau exact (20 000 trajectoires, H = 1000).
    - e-détecteurs sur pièces équitables : ARL₀ moyen supérieur à γ pour γ ∈ {20, 100} (2000 trajectoires).
11. **`docs/sections/monitors.md`** : API et constantes portées, avec fichier et lignes source.

### Entrées
`~/The-Whitening-Advantage-Experiments/` (lecture seule) ; `data/derived/d1_etf4/` (prompt 2) ; `CLAUDE.md`.

### Livrables
`jepadrift/monitors/{cusum,lattice,streams,gamma,eprocess}.py`, `jepadrift/stats/garch.py`, `tests/test_monitors.py`, `tests/test_identity_articleB.py`, `results/identity/articleB_R01_R08.csv` (comparaisons cellule par cellule), `docs/sections/monitors.md`.

### Contraintes techniques
- `jepadrift/monitors/` importe numpy seulement.
- Aucun générateur aléatoire interne aux détecteurs.
- Calculs vectorisés en float64.
- Constantes de l'Article B non modifiées.

### Critères de succès
- Contrôles R01 et R08 identiques, ou écarts documentés imputables à l'environnement.
- Contrôles Monte Carlo passés.
- `make check` au vert.

### Commandes de vérification
```bash
pytest -q tests/test_monitors.py tests/test_identity_articleB.py
python -c "from jepadrift.monitors.lattice import attainable_levels as f; print(f(H=5000, delta=0.1, sided=1, q=0.5)[:5])"
```
