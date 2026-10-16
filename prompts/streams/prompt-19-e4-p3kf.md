## PROMPT 19 — E4 : lois d'échelle en N et antériorité PCA « queue » (P3-KF, SPLL)

### Contexte
La signature falsifiable de JEPA-Drift est la loi d'échelle du gain en fonction de la taille N de la coupe :
- N⁰ pour le pooling face à une dérive de marché ;
- N^{1/2} pour une dérive de largeur surveillée dans tout le résiduel ;
- N¹ pour une largeur portée par quelques directions de caractéristiques.

E4 la mesure et reproduit l'antériorité de Kuncheva (composantes de faible variance). Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e4_scaling.py` ; fenêtres antérieures à 2020 avant J4.
1. **Jeux** : D2, `d3_239`, `d3_500` [A] ; D4 [B, s'il est disponible] ; tous symétrisés (D6).
2. **Grille** : N ∈ {8, 16, 32, 64, 128, 239, 500}, borné par N_max ; 20 sous-ensembles emboîtés tirés avec graine.
3. **Familles**, convention (b) à amplitude par titre fixée :
   - F1, primes fixes sur K facteurs ;
   - F2, κ ∈ {0.25, 0.5, 1} ;
   - F3, SR de marché par titre = 1.
4. **Pipelines** : P2-C, P3-C (factoriel et complet), P3-KF, P3-CS, P4-C (IPCA ; CD-DFM si disponible).
5. **P3-KF**, dans `jepadrift/monitors/spll.py` : détecteur de log-vraisemblance semi-paramétrique de Kuncheva (2013, IEEE TKDE ; vérifier la référence) sur les composantes « tail10 » :
   - k-moyennes sur une fenêtre de référence ;
   - statistique sur une fenêtre glissante ;
   - seuil calibré sur des fenêtres nulles D6.
6. **Mesures.**
   - G_ADD_av rapporté à P1 (actif médian) et à P2-C ;
   - pentes de log G en log N avec IC bootstrap sur les sous-ensembles ;
   - comparaison aux exposants 0, 1/2 et 1 (Corollaire 2, `floors.py`) ;
   - audit réduit par sous-ensemble : spectre de Sharpe de dérive débiaisé.

### Entrées
Prompts 5, 7, 11, 17 (et 18) ; `CLAUDE.md`.

### Livrables
`experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`, `results/e4/{e4_cells.csv,e4_slopes.csv}`, `figures/e4/*`.

### Contraintes techniques
Mêmes graines de sous-ensembles pour tous les pipelines ; option `--quick`.

### Critères de succès
Pentes et IC produits pour chaque (famille, pipeline) ; P3-KF calibré dans l'IC de son niveau nominal sur fonds nuls.

### Commandes de vérification
```bash
python experiments/e4_scaling.py --quick --out results/e4_quick
python experiments/e4_scaling.py --out results/e4 && head results/e4/e4_slopes.csv
```
