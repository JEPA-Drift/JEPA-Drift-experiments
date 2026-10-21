## PROMPT 26 — E7 : absorption par un encodeur adaptatif et vieillissement de l'encodeur gelé

### Contexte
Un encodeur mis à jour en ligne absorbe la dérive. Le critère d'absorption de JEPA-Drift (Prop. 4) prévoit qu'il ne détecte presque sûrement que si τ_a > 2τ_γ, avec un délai fluide de −(τ_a/2)·ln(1 − 2τ_γ/τ_a). Un encodeur gelé n'absorbe rien, mais vieillit. E7 mesure les deux effets. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e7_absorption.py`.
1. **P5-ADAPT** : CA-T-JEPA ajusté en ligne sur une fenêtre glissante, avec un taux d'apprentissage qui fixe une mémoire effective. τ_a est mesuré empiriquement par la décroissance de Δz après l'onset.
2. **Comparaison avec P5-C gelé**, sur F1 et F2 injectées sur fonds D6 de `d3_239`, avec τ_a/τ_γ ∈ {0.5, 1, 2, 4, 8}, en lecture anytime-valid à γ_H = H/α (AGENTS.md). Comparer les délais mesurés à la prédiction calculée avec le τ_a mesuré (`floors.absorption_delay`).
3. **Vieillissement** : sous H₀, ARL₀ par tranche annuelle depuis la fin du pré-entraînement, sur fonds symétrisés. Avant J4, tranches 2016–2019 seulement ; 2020 et au-delà uniquement avec la configuration gelée.

### Entrées
Prompts 14 et 16 ; `CLAUDE.md`.

### Livrables
`experiments/e7_absorption.py`, `configs/e7.yaml`, `results/e7/{e7_absorption.csv,e7_aging.csv}`, `figures/e7/*`.

### Contraintes techniques
Mises à jour en ligne strictement causales ; graines fixées ; CPU.

### Critères de succès
Seuil τ_a ≈ 2τ_γ observé ou réfuté avec IC ; ARL₀ par âge rapporté.

### Commandes de vérification
```bash
python experiments/e7_absorption.py --quick --out results/e7_quick
```
