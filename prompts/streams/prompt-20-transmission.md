## PROMPT 20 — Spectres de transmission T(u) et comparaison dictionnaire contre sous-espace

### Contexte
JEPA-Drift doit montrer ce que chaque représentation transmet d'une dérive. Le rapport de transmission vaut T(u) = ‖Σ_z^{−1/2} E[J_φ] u‖² / ‖Σ^{−1/2} u‖², avec J_φ la jacobienne de l'encodeur. La prédiction testée est T_JEPA > T_MAE sur les directions de faible variance. JEPA-Drift compare aussi deux priors sur la direction de dérive : dictionnaire d'atomes économiques contre mélange isotrope (Prop. 3d). Lire `CLAUDE.md`.

### Tâche
1. Écrire `experiments/transmission.py` :
   - E[J_φ]u ≈ moyenne sur les jours de `calib` de [φ(x + εu) − φ(x − εu)]/(2ε), avec ε = 1e-3·‖x‖ ;
   - Σ_z estimé sur `calib` ;
   - directions u : résiduelles PC2–PC51, facteurs CD-DFM (si disponibles), caractéristiques orthogonalisées, directions F1 et F2 injectées ;
   - représentations : JEPA, MAE, temporel, ACP, IPCA.
2. Écrire `experiments/dictionary_vs_subspace.py`, sur fonds D6 de `d3_239` avec F1 et F2 :
   - (A) moyenne de K e-détecteurs le long d'atomes, K ∈ {10, 20, 50} ;
   - (B) mélange isotrope sur le sous-espace résiduel de dimension D ;
   - mesurer cos²ϑ et les délais, puis comparer à `floors.dictionary_multiplier` et `floors.mixture_multiplier` (angles de bascule).

### Entrées
Prompts 16 à 18 ; `CLAUDE.md`.

### Livrables
`results/transmission/{spectra.csv,summary.csv}`, `results/dictionary/cells.csv`, `figures/{transmission,dictionary}/*`.

### Contraintes techniques
Aucune donnée de `monitor` ; graines fixées.

### Critères de succès
Spectres pour toutes les représentations disponibles ; écart entre délais mesurés et prédits rapporté (±10 % attendu en approximation fluide).

### Commandes de vérification
```bash
python experiments/transmission.py --out results/transmission
python experiments/dictionary_vs_subspace.py --quick --out results/dictionary_quick
```
