## PROMPT 23 — E6 : dérives de second ordre F4 (rotations, déformations de covariance)

### Contexte
Si l'information de localisation manque sur les données réelles (contingence C1 de JEPA-Drift), l'axe empirique principal devient le second ordre. Un rapport de variance r porte ½(r − 1 − ln r) nat par jour et par direction : 24 fois le budget d'une dérive de SR = 1 pour r = 1.5, 77 fois pour r = 2. E6 compare les têtes paires. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e6_second_order.py`.
1. **Fonds** : D6 de `d3_239`.
2. **Dérives F4** (prompt 5) :
   - déformation r ∈ {1.25, 1.5, 2} sur les sous-espaces des 3 premières PC résiduelles ou d'un facteur sectoriel ;
   - rotation θ ∈ {15°, 30°, 45°}.
3. **Pipelines** : P1-D (indice), P3-D, P4-D et P5-D (tête paire). CUSUM d'énergie δ = 0.5, seuil par bootstrap de fenêtres nulles de calibration ; Γ_z^op rapporté.
4. **Mesures** :
   - G_ADD et taux de détection ;
   - comparaison au budget KL par direction ;
   - contribution d'E6 à la porte J4 (famille F4).

### Entrées
Prompts 5, 7, 16, 17 ; `CLAUDE.md`.

### Livrables
`experiments/e6_second_order.py`, `configs/e6.yaml`, `results/e6/e6_cells.csv`, `figures/e6/*`.

### Contraintes techniques
Les statistiques paires ne se calibrent pas par inversion de signe : utiliser le bootstrap de fenêtres. Graines fixées.

### Critères de succès
FPR sous H₀ dans l'IC de la cible ; G_ADD avec IC par cellule.

### Commandes de vérification
```bash
python experiments/e6_second_order.py --quick --out results/e6_quick
```
