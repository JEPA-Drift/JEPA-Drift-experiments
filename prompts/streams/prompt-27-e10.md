## PROMPT 27 — E10 : robustesse (queues épaisses, levier, dépendance asymétrique, rendements nuls)

### Contexte
L'exactitude des flux de signe de JEPA-Drift suppose la symétrie centrale conditionnelle. E10 mesure jusqu'où les fausses alarmes et les gains tiennent quand elle est violée, et ce que corrige le recentrage sur un taux estimé q̂_u. Annexe D. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e10_robustness.py`.
1. **Fonds D5** :
   - t_ν avec ν ∈ {3, 4, 5, 7} ;
   - GJR-GARCH (levier ∈ {0, 0.05, 0.10}) ;
   - choc commun asymétrique (dépendance de queue asymétrique) ;
   - part de rendements nuls ∈ {0, 2 %, 5 %}, par arrondi.

   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4).
2. **Pipelines** : P1-C, P3-C, P5-C, avec et sans recentrage sur q̂_u estimé sur `calib`.
3. **Mesures** : FPR contre niveau nominal, G_ADD sur F1 et F2.

### Entrées
Prompts 5 et 7 (P5-C si disponible) ; `CLAUDE.md`.

### Livrables
`experiments/e10_robustness.py`, `configs/e10.yaml`, `results/e10/e10_cells.csv`, `figures/e10/*`.

### Contraintes techniques
Graines fixées ; option `--quick`.

### Critères de succès
Inflation du FPR quantifiée par violation, avec IC ; effet du recentrage rapporté.

### Commandes de vérification
```bash
python experiments/e10_robustness.py --quick --out results/e10_quick
```
