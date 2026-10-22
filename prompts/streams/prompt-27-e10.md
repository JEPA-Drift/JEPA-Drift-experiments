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

   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4), avec ses violations naturelles mesurées par l'audit (symétrie rejetée sur PC1, PC2, PC3 et `rev_21` selon le jeu, `CLAUDE.md`) et ses rendements nuls (2 864 sur D2 avant 2020, tranchés par pièce).
2. **Pipelines en deux étapes** : P1-C et P3-C dès maintenant, avec et sans recentrage sur q̂_u estimé sur `calib` ; P5-C seulement après disponibilité d'un point de contrôle gelé du stream 16. Une option explicite sélectionne l'étape et l'exécution initiale ne dépend pas de P5-C.
3. **Mesures** : FPR observé avec IC contre le niveau nominal et le niveau atteint sous le nul valide ; G_ADD sur F1, et F2 sur D3 uniquement (D2 n'a pas de caractéristiques), à γ_H = H/α. Sur les placebos bruts asymétriques, ne pas qualifier la lecture de garantie exacte. Rapporter le FPR atteint à côté de chaque gain ; si les FPR diffèrent, ne pas conclure à un gain à fausse alarme égale.

### Entrées
Étape initiale : prompts 5 et 7. Étape P5-C : stream 16 et son point de contrôle gelé ; `CLAUDE.md`.

### Livrables
`experiments/e10_robustness.py`, `configs/e10.yaml`, `results/e10/e10_cells.csv`, `figures/e10/*`.

### Contraintes techniques
Graines locales `SeedSequence` ; option `--quick` ; aucun accès aux lignes réelles datées de 2020 ou après avant J4.

### Critères de succès
Inflation du FPR quantifiée par violation, avec IC ; effet du recentrage rapporté.

### Commandes de vérification
```bash
python experiments/e10_robustness.py --stage linear --quick --out results/e10_quick
```
