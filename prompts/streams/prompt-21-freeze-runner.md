## PROMPT 21 — Gel de configuration, `benchmark_runner`, figures depuis CSV et traçabilité des nombres

### Contexte
Au jalon J4 (8 novembre), JEPA-Drift gèle sa configuration (empreinte unique) avant tout passage sur la fenêtre de test 2020–2025, pour supprimer les degrés de liberté a posteriori. Ensuite, chaque figure et chaque nombre de l'article doivent se régénérer depuis un CSV. Lire `CLAUDE.md`.

### Tâche
1. **`jepadrift/benchmark_runner.py`.**
   - Point d'entrée unique : `--config configs/<stream>.yaml`. Il appelle le `main(argv)` des scripts existants (`experiments/e1_problem.py`, `e3_calibration.py`, …) sans les réimplémenter.
   - `run_hash` = SHA-256 de la configuration en JSON canonique, du commit git et des empreintes du manifeste de données.
   - Sortie `results/<stream>/<run_hash>.csv`, une ligne par réplication : `seed, family, D, gamma, reading, ADD, alarm, ...`.
2. **`tools/freeze_config.py`.**
   - Écrit `configs/FROZEN.json` : empreintes de toutes les configurations d'expérience, commit, et empreintes de `data/derived/MANIFEST.json` et `docs/manifests/d4_manifest.json` ; cible `make freeze`.
   - Le runner refuse `--include-test-window` si l'empreinte courante diffère du gel.
3. **`figures/make_<fig>.py`** : un script par figure, lecture des CSV seulement, export PNG et PDF. Inclure la figure d'E2 : délais mesurés contre prédits, avec les trois lectures et le premier ordre.
4. **`tools/trace_numbers.py`.**
   - Analyse `paper/*.tex` : macros `\E{key}` ou nombres balisés.
   - Vérifie chaque nombre contre le CSV et la colonne déclarés dans `docs/MAPPING.md`, à l'arrondi près.
   - Échoue en cas d'écart.
5. **`tools/dpi_lint.py`** : signale toute phrase qui suggère une hausse de KL ou d'information (motifs : « increase(s|d) … (KL|information|divergence) », « create(s) information », etc.).
6. **`tools/appendix_b.py`** : produit les tableaux de paramètres des générateurs et des dérives depuis `configs/` et `docs/sections/injection.md`.

### Entrées
Scripts E1, E3 et suivants ; `CLAUDE.md`.

### Livrables
Les outils ci-dessus, `configs/FROZEN.json` (au J4), `docs/MAPPING.md` initialisé avec les nombres déjà cités (E2/J1, identités R01/R08/R15, audit, E1, E3), `tests/test_tools.py`.

### Contraintes techniques
Aucune figure lue depuis un état en mémoire ; aucun nombre saisi à la main dans `paper/`. `results/e2/e2_cells.csv` est en fins de ligne CRLF (empreinte de référence) : ne pas le normaliser ; `make j1` réécrit la ligne de durée du résumé. Fusion requise avant le stream 22 et avant toute exécution sur la fenêtre de test.

### Critères de succès
- Une exécution E1 via le runner reproduit `results/e1/e1_cells.csv` bit à bit.
- Le gel bloque un test sur la fenêtre 2020+ avec une configuration modifiée.
- `trace_numbers` détecte un nombre altéré (test).

### Commandes de vérification
```bash
pytest -q tests/test_tools.py
python tools/freeze_config.py --check
python tools/trace_numbers.py paper/ --mapping docs/MAPPING.md
```
