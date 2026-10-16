## PROMPT 11 — Audit informationnel des panels D2 et D3

### Contexte
Avant tout apprentissage, JEPA-Drift mesure combien d'information de dérive existe dans chaque sous-espace de la coupe : marché, facteurs, résiduel, directions de caractéristiques. Il mesure aussi si l'hypothèse de symétrie qui rend les flux de signe exacts tient. Ces chiffres nourrissent le §2 de l'article, les gains prévus d'E1 et la décision J2. Lire `CLAUDE.md`.

Définition : le Sharpe de dérive d'un sous-espace S vaut SR_S² = 252·Δμ_Sᵀ Σ_S⁻¹ Δμ_S, où Δμ est l'écart des moyennes entre deux phases adjacentes.

### Tâche
Écrire `experiments/audit_information.py`. Fenêtres autorisées avant J4 : 2005–2019 seulement.
1. **Spectre** de Σ̂ sur la calibration, avec et sans Ledoit–Wolf. Rapporter η = λ₁/tr Σ par année, le bord de Marčenko–Pastur et K.
2. **Signes.** Corrélation moyenne des signes ρ̂_signe, correspondance gaussienne ρ = sin(πρ̂_signe/2), K_eff = 1/ρ̂_signe.
3. **Symétrie centrale.** Pour chaque direction figée (PC1–PC20, directions de caractéristiques orthogonalisées) :
   - q̂_u = moyenne de 1{uᵀx_t > 0}, avec test binomial exact contre 1/2 ;
   - test des triplets de Randles et al. (1980) sur uᵀx_t/σ̂_{t|t−1} ;
   - correction de Holm.
4. **Spectre de Sharpe de dérive débiaisé.**
   - Transitions : frontières des phases des datations de SPY (`phases_*.csv`, prompt 2) comprises dans 2005–2019.
   - Pour chaque transition (n₁, n₂ jours) et chaque sous-espace S de dimension d_S :

     SR_S² = 252·[Δμ̂_Sᵀ Σ̂_S⁻¹ Δμ̂_S − d_S(1/n₁ + 1/n₂)]·(n − d_S − 1)/n.

   - IC par bootstrap par blocs mobiles (blocs de 20 jours, 2000 tirages) ; agrégation par médiane sur les transitions.
   - Sous-espaces : marché, factoriel (K), résiduel complet, caractéristiques ; d_S ≤ 30 pour limiter le biais de bruit.
5. **Plafonds des canaux.**
   - N1 = E[σ_t²]·E[σ_t⁻²], σ_t étant la dispersion transversale résiduelle.
   - N2 : rapport entre l'information conditionnelle (Σ_t Ledoit–Wolf glissant sur 60 jours, passé seulement) et l'information statique, pour des directions F1 et F2.
   - N3 : ν̂ d'une loi t multivariée ajustée sur les résidus blanchis, puis rapport J/Σ⁻¹ = (ν+1)ν/((ν+3)(ν−2)) par direction.
6. **Part du budget.** Pour chaque phase datée et chaque sous-espace, proportion des phases avec L·Î ≥ ln γ, pour γ ∈ {20, 252}. C'est la lecture budget, exacte par le Lemme 1.
7. **Gains prévus.** Évaluer `jepadrift/floors.py` avec ρ̂, κ̂ et le spectre estimés, et écrire `predicted_gains.csv` (entrée d'E1).

### Entrées
D1 (datations), D2, D3 ; représentations du prompt 6 ; `jepadrift/floors.py` ; `CLAUDE.md`.

### Livrables
`results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains}.csv`, `figures/audit/*.{png,pdf}`, `logs/audit/`.

### Contraintes techniques
- Aucune donnée postérieure au 2019-12-31.
- Bootstrap par blocs avec graines fixes.
- Figures produites depuis les CSV.

### Critères de succès
Toutes les sorties produites. Les estimations débiaisées sont rapportées même négatives (risque R9, signalé). Exécution déterministe au SHA-256 près.

### Commandes de vérification
```bash
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
ls results/audit && sha256sum results/audit/*.csv
```
