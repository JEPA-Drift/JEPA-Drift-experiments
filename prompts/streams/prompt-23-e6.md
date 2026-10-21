## PROMPT 23 — E6 : dérives de second ordre F4 (rotations, déformations de covariance), en deux phases

### Contexte
L'audit montre deux choses aux transitions datées de SPY (wrapups 11 et 11b) :
- l'information de localisation hors marché y est noyée dans le bruit ;
- le SR² de marché y relève de la sélection.

La contingence C1 de JEPA-Drift, qui fait du second ordre l'axe principal, devient donc plausible. Un rapport de variance r porte ½(r − 1 − ln r) nat par jour et par direction : 24 fois le budget d'une dérive de SR = 1 pour r = 1,5, 77 fois pour r = 2. La phase 1 (capteurs linéaires) démarre sans attendre le JEPA ; la phase 2 ajoute la tête paire du JEPA. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e6_second_order.py` avec l'option `--phase {1,2}`.
1. **Fonds.**
   - Principal : fenêtres D6 de `d3_239` prises dans le segment de calib (2016-04 → 2019-12), avec H ∈ {250, 500}. L'énergie blanchie n'est pas stationnaire sur 2005–2019 : Γ^op ≈ 191 et 2 346, contre 7,6 et 25,2 en calib (`C-P3D-windows`). Les fenêtres se chevauchent : le signaler.
   - Contrôle : panels D5 indépendants, N = 239 (`sim.garch_panel`, facteur équicorrélé ρ = 0,40, t₇).
2. **Dérives F4** (`injection.inject`) :
   - déformation r ∈ {1,25 ; 1,5 ; 2} sur les sous-espaces des 3 premières PC résiduelles ou d'un facteur sectoriel ;
   - rotation θ ∈ {15°, 30°, 45°} ;
   - information réalisée lue dans `meta`.
3. **Pipelines.** CUSUM d'énergie, δ = 0,5 ; seuil calculé sur toutes les fenêtres nulles de calib, α = 0,05 à l'horizon H ; Γ_z^op rapporté.
   - Phase 1 : P1-D (indice équipondéré), P3-D (factoriel et complet), et P4-D (IPCA) dès que le stream 17 est fusionné.
   - Phase 2 : P5-D, tête paire du CA-T-JEPA (stream 16).
4. **Mesures.**
   - Délais, taux de détection, G_ADD et IC.
   - Comparaison au budget KL par direction.
   - Contribution à la porte J4 (famille F4, phase 2).

### Entrées
Phase 1 : streams 5 et 7 (et 17 pour P4-D). Phase 2 : stream 16. `CLAUDE.md`.

### Livrables
`experiments/e6_second_order.py`, `configs/e6.yaml`, `results/e6/{e6_cells_phase1.csv,e6_cells_phase2.csv}`, `figures/e6/*`, `logs/e6/`.

### Contraintes techniques
- Les statistiques paires ne se calibrent pas par inversion de signe : fenêtres nulles de calib uniquement.
- Graines fixées.
- Aucune ligne datée de 2020 ou après.

### Critères de succès
- FPR sous H₀ dans la région à 99 % de α.
- G_ADD avec IC pour chaque cellule.
- Phase 1 livrée avant J3, phase 2 avant J4.

### Commandes de vérification
```bash
python experiments/e6_second_order.py --phase 1 --quick --out results/e6_quick
python experiments/e6_second_order.py --phase 1 --out results/e6
```