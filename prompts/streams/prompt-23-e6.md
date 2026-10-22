## PROMPT 23 — E6 : dérives de second ordre F4 (rotations, déformations de covariance), en deux phases

### Contexte
L'audit montre deux choses aux transitions datées de SPY (wrapups 11 et 11b) :
- l'information de localisation hors marché y est noyée dans le bruit ;
- le SR² de marché y relève de la sélection.

La contingence C1 de JEPA-Drift, qui fait du second ordre l'axe principal, devient donc plausible. Dans le modèle gaussien de conception, un rapport de variance r porte ½(r − 1 − ln r) nat par jour et par direction : 24 fois le budget d'une dérive de SR = 1 pour r = 1,5, 77 fois pour r = 2. Ce n'est pas la KL exacte des fonds D5 à innovations t₇ ou D6. La phase 1 (capteurs linéaires) démarre sans attendre le JEPA ; la phase 2 ajoute la tête paire du JEPA. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e6_second_order.py` avec l'option `--phase {1,2}`.
1. **Fonds.**
   - Principal : fenêtres D6 de `d3_239` prises dans le segment de calib (2016-04 → 2019-12), avec H ∈ {250, 500}. L'énergie blanchie n'est pas stationnaire sur 2005–2019 : Γ^op ≈ 191 et 2 346, contre 7,6 et 25,2 en calib (`C-P3D-windows`). Les fenêtres se chevauchent et réutilisent les jours qui fixent les seuils : FPR D6 descriptif, sans IC inférentiel. Pour G_ADD, utiliser un `deff` ou bootstrap par blocs justifié ; si 941 jours ne permettent pas un IC fiable, rapporter `IC=NA` et sa raison. Ne pas assimiler `floor(941/H)` à une taille effective estimée.
   - Contrôle : panels D5 indépendants, N = 239 (`sim.garch_panel`, facteur équicorrélé ρ = 0,40, t₇). Si K est fixé plutôt qu'estimé sur D5, étiqueter l'analyse conditionnelle à ce choix et inclure K = 1 (facteur vrai) en sensibilité.
2. **Dérives F4** (`injection.inject`) :
   - déformation r ∈ {1,25 ; 1,5 ; 2} sur les sous-espaces des 3 premières PC résiduelles ou d'un facteur sectoriel ;
   - rotation θ ∈ {15°, 30°, 45°}, avec PC2–PC3 comme témoin négatif déclaré avant l'exécution ; cette paire a déjà été examinée sur D6 et reste exploratoire sur D6, mais peut être préspécifiée pour les panels de test D5 indépendants ; étiqueter les autres paires choisies après sonde comme exploratoires ;
   - information quadratique gaussienne de conception lue dans `meta`, sans l'appeler KL exacte des fonds non gaussiens.
3. **Pipelines.** CUSUM d'énergie, δ = 0,5 ; seuil calculé sur toutes les fenêtres nulles de calib, α = 0,05 à l'horizon H ; Γ_z^op rapporté.
   - Phase 1 immédiatement : P1-D (indice équipondéré) et P3-D (factoriel et complet). Ajouter P4-D (IPCA) seulement après fusion du stream 17 ; ne pas bloquer la livraison P1-D/P3-D.
   - P1-D reprend le flux d'énergie de l'Article B : `q_t = (r_t² − μ̂)/σ̂`, avec `μ̂ = mean(r²)` et `σ̂ = std(r²)` ajustés sur les lignes sans dérive. Ne pas le remplacer par `(z² − 1)/sqrt(2)` ni par une normalisation avec `std(r)`. Si le seuil P3-D issu de `fit_pipeline` est remplacé sur D5, recalculer `Γ_z^op = λ_D5/λ_iid` avec le seuil final.
   - Phase 2 : P5-D, tête paire du CA-T-JEPA (stream 16).
4. **Mesures.**
   - Délais, taux de détection, G_ADD et IC.
   - Comparaison au budget gaussien de conception, avec étiquette de modèle. Pour une rotation, rapporter l'information conjointe ; un partage égal entre directions est une convention comptable, pas une KL identifiée par direction. `floors.evidence_budget` reste un repère de conception, pas une borne de délai du CUSUM d'énergie.
   - Contribution à la porte J4 (famille F4, phase 2).

### Entrées
Phase 1 : streams 5 et 7 (et 17 pour P4-D). Phase 2 : stream 16. `CLAUDE.md`.

### Livrables
`experiments/e6_second_order.py`, `configs/e6.yaml`, `results/e6/{e6_cells_phase1.csv,e6_cells_phase2.csv}`, `figures/e6/*`, `logs/e6/`.

### Contraintes techniques
- Les statistiques paires ne se calibrent pas par inversion de signe : fenêtres nulles de calib uniquement.
- Graines fixées.
- Aucune ligne datée de 2020 ou après.
- Nouveaux comptes rendus d'audit, dont `docs/DEVIATIONS.md`, en anglais ; journaux locaux non indexés dans Git.

### Critères de succès
- FPR sous H₀ avec IC sur le contrôle D5 indépendant ; FPR D6 dans l'échantillon, descriptif et sans IC inférentiel.
- Rapport de délais restreints à H, avec censure étiquetée et IC bootstrap apparié sur les panels de test D5 indépendants ; pour D6, `IC=NA` motivé si la dépendance empêche une estimation fiable.
- Phase 1 P1-D/P3-D livrée avant J3, P4-D après le stream 17, phase 2 avant J4.

### Commandes de vérification
```bash
.venv/bin/python experiments/e6_second_order.py --phase 1 --quick --out results/e6_quick
.venv/bin/python experiments/e6_second_order.py --phase 1 --out results/e6
```
