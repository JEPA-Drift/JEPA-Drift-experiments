## PROMPT 5 — Injections F1–F4 et fonds D5 (Monte Carlo) et D6 (symétrisés)

### Contexte
Les expériences de JEPA-Drift injectent des dérives contrôlées, avec une date de rupture τ* exacte, sur des fonds réels symétrisés ou simulés. Elles mesurent ainsi délais et fausses alarmes avec une vérité terrain exacte. Bloquant pour E1 et E3 (J2). Lire `CLAUDE.md`.

Définitions :
- **D6** : chaque journée entière de la coupe est multipliée par un même signe de Rademacher. La transformation conserve |x|, les corrélations et la volatilité, et efface les dérives de localisation et l'effet de levier.
- **F1** : primes factorielles B Δλ.
- **F2** : largeur pilotée par les caractéristiques, (C_t Δγ) orthogonalisée aux chargements.
- **F3** : translation du mode de marché.
- **F4** : dérive de second ordre.

### Tâche
1. **Refactorisation.** Déplacer `Garch` et `t_innov` de `experiments/e2_floor_validation.py` vers `jepadrift/sim.py` ; E2 les importe désormais. Le SHA-256 de `results/e2/e2_cells.csv` doit rester identique : relancer `make j1` avant et après.
2. **Générateurs D5** dans `jepadrift/sim.py` :
   - `gaussian_latent(T, D, rng)` ;
   - `garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None)`, à volatilité commune, avec option de structure à un facteur équicorrélé (ρ = 0.40) plus un terme idiosyncratique.
3. **D6** dans `jepadrift/injection.py` : `symmetrize(X, rng)` renvoie (X̃ = ε_t X_t, ε). Les signes ε sont conservés pour la traçabilité.
4. **`inject(X, family, tau_star, I_target, params, rng)`**, appliqué aux rendements seulement, à partir de τ*. Σ̂ (Ledoit–Wolf), B (K facteurs, ACP) et Ψ̂ (variances résiduelles) sont estimés sur la fenêtre de calibration.
   - **F1** : Δ = B Δλ, Δλ de direction aléatoire, normalisé pour que ½ΔᵀΣ̂⁻¹Δ = I_target.
   - **F2** : Δ_t = (C_t Δγ)_⊥, résidu GLS de C_tΔγ sur B (pondération Ψ̂⁻¹), même normalisation sur la moyenne de calibration.
   - **F3** : Δ = Δm·b₁, b₁ = chargements de PC1.
   - **F4, déformation** : X̃ = X + (√r − 1) V_S V_Sᵀ X sur un sous-espace S, r ∈ {1.25, 1.5, 2}.
   - **F4, rotation** : rotation de Givens d'angle θ ∈ {15°, 30°, 45°} entre deux directions factorielles.
5. **Conventions d'amplitude.**
   - (a) Information égale : I_target = SR²/504, SR ∈ {0.5, 1, 2, 4}.
   - (b) Amplitude par titre fixée, pour les lois d'échelle : κ = dispersion transversale orthogonale aux chargements / dérive de marché, κ ∈ {0.25, 0.5, 1}.
6. **Onset.** τ* ~ U[t₀ + H_ref, t_fin − H_det]. Écrire `tau_star.json` : graine, famille, amplitude, convention, empreinte de la direction.
7. **Tests** `tests/test_injection.py` :
   - |X̃| = |X| bit à bit, un seul signe par jour ;
   - |BᵀΨ̂⁻¹Δ|_∞ < 1e-10 pour F2 ;
   - ½ΔᵀΣ̂⁻¹Δ = I_target à 1e-10 ;
   - aucune modification avant τ* ;
   - déterminisme pour une graine donnée ;
   - SHA-256 d'E2 inchangé.

### Entrées
Lot 1 (E2) ; D2 et D3 (prompts 2 et 3) ; `CLAUDE.md`.

### Livrables
`jepadrift/sim.py`, `jepadrift/injection.py`, E2 refactorisé, `tests/test_injection.py`, `docs/sections/injection.md` (formules et paramètres ; il servira de base à l'Annexe B).

### Contraintes techniques
- numpy et scipy.
- Aucune injection dans un espace latent.
- Générateurs aléatoires passés explicitement.

### Critères de succès
Tests au vert ; hash d'E2 identique ; documentation complète des quatre familles.

### Commandes de vérification
```bash
make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16
pytest -q tests/test_injection.py
```
