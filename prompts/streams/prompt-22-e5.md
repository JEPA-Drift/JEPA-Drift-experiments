## PROMPT 22 — E5 : JEPA contre références linéaires, attribution et balayage de D (jalon J4)

### Contexte
E5 est le test central de JEPA-Drift. La tête impaire du JEPA (P5-C) doit détecter plus vite que les meilleures références linéaires (P3-C, P3-CS, P4-C), à fausses alarmes égales, sur des dérives injectées. La porte J4 (8 novembre) décide du titre de l'article. Lire `CLAUDE.md`.

Définitions :
- **Rétention** r(D) = I_z/I_x.
- **Taxe dimensionnelle** M(D) (`floors.mixture_multiplier`).

### Tâche
Écrire `experiments/e5_jepa.py`, exécuté via le runner avec la configuration gelée.
1. **Jeux** : `d3_239` [A] ; D2 et D4 [B] ; fonds D6.
2. **Pipelines** : P5-C (D ∈ {2, 4, 8, 16}, 3 graines) contre P3-C, P3-CS et P4-C ; ablations P5-MAE et P5-TEMP.
3. **Familles** : F1, F2, F3. Convention (a) avec SR ∈ {1, 2, 4}, et convention (b).
4. **Lecture principale** : anytime-valid. G_ADD_av avec IC bootstrap sur graines et onsets.
5. **r(D)/M(D).**
   - I_z se mesure par injection traversant l'encodeur gelé : Δz = E[z | dérive] − E[z | nul], I_z = ½ΔzᵀΣ_z⁻¹Δz.
   - I_x = ½ΔᵀΣ⁻¹Δ.
   - D* est choisi sur `calib` seulement.
6. **Diagnostics** : RankMe, T(u) (prompt 20), dictionnaire contre sous-espace [C].
7. **Attribution** : P3-CS figure dans chaque tableau principal ; écart P5 − P3-CS rapporté avec son IC.
8. **Porte J4.** G_ADD_av(meilleur de P3-CS et P4 → P5) ≥ 1.25 sur au moins deux familles parmi F1, F2 et F4 (F4 provient d'E6, via P5-D), avec un IC à 95 % qui exclut 1. Écrire `results/e5/J4_gate.txt` : « titre A » ou « titre B ».

### Entrées
Prompts 16, 17, 19, 21 (et 18, 20, 23) ; `CLAUDE.md`.

### Livrables
`experiments/e5_jepa.py`, `configs/e5.yaml`, `results/e5/{e5_cells.csv,e5_retention.csv,J4_gate.txt}`, `figures/e5/*`.

### Contraintes techniques
Fenêtre de test interdite avant le gel ; mêmes graines d'onsets pour tous les pipelines.

### Critères de succès
Porte J4 évaluée avec ses IC ; tableaux principaux complets avec P3-CS.

### Commandes de vérification
```bash
python -m jepadrift.benchmark_runner --config configs/e5.yaml --quick
python -m jepadrift.benchmark_runner --config configs/e5.yaml && cat results/e5/J4_gate.txt
```
