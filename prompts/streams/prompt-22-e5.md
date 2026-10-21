## PROMPT 22 — E5 : JEPA contre références linéaires, attribution et balayage de D (jalon J4)

### Contexte
E5 est le test central de JEPA-Drift. La tête impaire du JEPA (P5-C) doit détecter plus vite que les meilleures références linéaires, à fausse alarme égale, sur des dérives injectées dans des fonds D6. Les références sont :
- P3-C (ACP) ;
- P3-CS (b), coupe de degré 0 à mise prévisible, qui capte déjà le canal N1 ≈ 2 mesuré par l'audit ;
- P4-C (IPCA, CD-DFM).

La porte J4 (8 novembre) décide du titre de l'article. Lire `CLAUDE.md`.

Définitions :
- **Rétention** : r(D) = I_z/I_x.
- **Taxe** : M(D) (`floors.mixture_multiplier`) pour un mélange ; pour un dictionnaire, le multiplicateur de `floors.dictionary_multiplier` avec l'alignement mesuré a_max.
- **Lecture** : anytime-valid à γ_H = H/α, avec H = 2 000 (`CLAUDE.md`).

### Tâche
Écrire `experiments/e5_jepa.py`, exécuté via `jepadrift.benchmark_runner` avec la configuration gelée. Avant le gel, seules les lignes 2005–2019 sont lues.
1. **Jeux** : `d3_239` [A] ; `d2_us97` [B, F1 et F3 seulement] ; D4 [B, sous-panel complet, `C-D4-survivor`] ; fonds D6.
2. **Pipelines.**
   - P5-C (lecture D ∈ {2, 4, 8, 16}, 3 graines) contre P3-C, P3-CS (b) et P4-C.
   - Ablations P5-MAE et P5-TEMP ; P3-CS (a) en secondaire.
3. **Familles** : F1, F2, F3. Convention (a) avec SR ∈ {2, 4, 8} ; convention (b) avec les grilles consignées au prompt 12.
4. **G_ADD**, avec IC bootstrap sur les graines et les onsets. Mêmes lecture, onsets et fonds pour tous les pipelines.
5. **Rétention et alignement.**
   - Δz est mesuré par paires sur des fonds identiques : moyenne sur les jours de φ(x + Δ) − φ(x), à travers l'encodeur gelé.
   - I_z = ½ΔzᵀΣ_z⁻¹Δz, avec Σ_z estimé sur la calib ; I_x = ½ΔᵀΣ̂⁻¹Δ.
   - a_max est rapporté par pipeline.
   - D* est choisi sur `calib` seulement.
6. **Diagnostics** : RankMe, T(u) (prompt 20), dictionnaire contre sous-espace [C].
7. **Attribution** : P3-CS (b) figure dans chaque tableau principal ; l'écart P5 − P3-CS (b) est rapporté avec son IC.
8. **Porte J4.**
   - Condition : G_ADD(meilleur de P3-CS (b) et P4 → P5) ≥ 1,25 sur au moins deux familles parmi F1, F2 et F4, avec un IC à 95 % qui exclut 1.
   - F4 provient d'E6, phase 2 (P5-D).
   - Écrire `results/e5/J4_gate.txt` : « titre A » ou « titre B ».

### Entrées
Streams 16, 17, 19, 21 et 23 (phase 2), et en complément 18 et 20 ; `CLAUDE.md`.

### Livrables
`experiments/e5_jepa.py`, `configs/e5.yaml`, `results/e5/{e5_cells.csv,e5_retention.csv,J4_gate.txt}`, `figures/e5/*`, `logs/e5/`.

### Contraintes techniques
- Fenêtre de test interdite avant le gel.
- Mêmes graines d'onsets pour tous les pipelines.
- L'option mélange de P3-C est exclue des verdicts (validité approchée).

### Critères de succès
- Porte J4 évaluée avec ses IC.
- Tableaux principaux complets, P3-CS (b) compris.
- r(D), a_max et M(D) rapportés pour chaque D.

### Commandes de vérification
```bash
python -m jepadrift.benchmark_runner --config configs/e5.yaml --quick
python -m jepadrift.benchmark_runner --config configs/e5.yaml && cat results/e5/J4_gate.txt
```