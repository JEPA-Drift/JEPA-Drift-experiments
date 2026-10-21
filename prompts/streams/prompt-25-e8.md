## PROMPT 25 — E8 : régimes réels et trois datations (après gel J4)

### Contexte
E8 confronte les pipelines de JEPA-Drift aux phases haussières et baissières réelles. C'est un appui, jamais une preuve.

Trois datations sont disponibles :
- `lt_spy` (66 phases) : Lunde–Timmermann pour SPY, Pagan–Sossounov pour les autres ETF ;
- `strict_ps` (48 phases) : Pagan–Sossounov strict partout ;
- `symmetric` (102 phases) : variante symétrique.

Sur SPY, `lt_spy` et `symmetric` coïncident (30 phases).

Deux biais sont établis :
- les frontières datées ex post sélectionnent les phases. Placebo du stream 11b : SR² de marché réel de 19 à 41, contre ≈ −2,5 sous rotation, p ≤ 0,0015 ;
- D3 et D4 sont des univers de survivants (`C-D3-survivor-correction`, `C-D4-survivor`).

E8 ne s'exécute qu'avec la configuration gelée au J4. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e8_real_regimes.py`, lancé via le runner avec `--include-test-window`.
1. **Phases.**
   - Fichiers `phases_*.csv` de D1.
   - Pour D2, D3 (et D4 [B]) : phases de SPY, plus une datation Pagan–Sossounov sur les indices sectoriels équipondérés de D3.
2. **Placebo.** 2 000 rotations circulaires de chaque chaîne de phases (`stats.drift.rotate_phases`). Chaque mesure par phase est rapportée avec sa distribution placebo.
3. **Pipelines.**
   - P1 à P5, avec D* et seuils gelés.
   - Sur données brutes, les flux de signe sont recentrés sur q̂ de calib pour les canaux dont la symétrie est rejetée (`CLAUDE.md`). Aucune exactitude n'est revendiquée.
4. **Mesures**, par phase et par datation :
   - Î débiaisé du sous-espace du pipeline ;
   - part des phases dans le budget (L·Î ≥ ln γ, γ ∈ {20, 252}), en lecture budget. À cause de la sélection, c'est une borne supérieure ;
   - alarmes dans la phase (lecture anytime-valid γ_H) ;
   - fausses alarmes en phases calmes ;
   - délai depuis le début de phase ;
   - écart à la distribution placebo.
5. **Rapport.**
   - Résultats par datation, jamais agrégés en une seule preuve.
   - Comparaison au recensement de l'Article B (R16 : 80,3 % hors budget à γ = 20 sur 66 phases, `R16-out-of-budget-frac`), en rappelant sa datation et la sélection.

### Entrées
Stream 21 (gel) ; stream 8b (placebo, débiaisage) ; tous les pipelines ; `CLAUDE.md`.

### Livrables
`experiments/e8_real_regimes.py`, `configs/e8.yaml`, `results/e8/{e8_phases.csv,e8_placebo.csv,e8_summary.csv}`, `figures/e8/*`, `logs/e8/`.

### Contraintes techniques
- Refus d'exécution si `configs/FROZEN.json` ne correspond pas.
- Aucune retouche après lecture des résultats sans nouvelle empreinte consignée.

### Critères de succès
- Trois datations traitées.
- IC de Wilson sur les proportions.
- Chaque mesure accompagnée de son placebo.
- Empreinte de gel inscrite dans chaque CSV.

### Commandes de vérification
```bash
python tools/freeze_config.py --check && python -m jepadrift.benchmark_runner --config configs/e8.yaml --include-test-window
```