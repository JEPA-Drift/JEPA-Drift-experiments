## PROMPT 28 — E11 : second domaine en coupe transversale (D8 : Electricity ; SWaT et WADI en option)

### Contexte
E11 teste la portée de JEPA-Drift sur des capteurs corrélés hors finance (Annexe D) : 370 clients électriques (UCI ElectricityLoadDiagrams20112014). SWaT et WADI exigent une demande d'accès à iTrust : ils ne sont traités que si les fichiers sont présents. Lire `CLAUDE.md`.

### Tâche
1. Télécharger le jeu depuis le dépôt UCI : chercher « ElectricityLoadDiagrams20112014 » sur archive.ics.uci.edu et consigner l'URL exacte. Agréger au pas quotidien ; prendre la log-différence de la charge quotidienne par client. Dans un worktree, exposer `data/raw/electricity` par un lien absolu (AGENTS.md).
2. Désaisonnaliser (jour de semaine, saison annuelle) sur un segment d'apprentissage. Tester la symétrie centrale (prompt 11) ; si elle est rejetée, utiliser des flux recentrés sur q̂.
3. Construire des fonds D6 et des injections F1–F2.
4. Pipelines : P2-C, P3-C, et P5-C si un CA-T-JEPA est entraîné sur ce domaine (sans caractéristiques).
5. Mesurer G_ADD (lecture γ_H = H/α) et le FPR.
6. Si `data/raw/swat` ou `data/raw/wadi` existent, appliquer le même protocole ; sinon, consigner l'absence.

### Entrées
Internet (UCI) ; prompts 5 et 7 (et 14) ; `CLAUDE.md`.

### Livrables
`jepadrift/data_loader/electricity.py`, `experiments/e11_sensors.py`, `results/e11/e11_cells.csv`, `figures/e11/*`.

### Contraintes techniques
Données brutes ignorées par git ; graines fixées.

### Critères de succès
Panel de 370 séries construit ; FPR dans l'IC ; G_ADD avec IC ; écarts consignés.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.electricity --build
python experiments/e11_sensors.py --quick --out results/e11_quick
```
