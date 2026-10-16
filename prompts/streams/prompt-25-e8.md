## PROMPT 25 — E8 : régimes réels et trois datations (après gel J4)

### Contexte
E8 confronte les pipelines de JEPA-Drift aux phases haussières et baissières réelles. Les datations disponibles sont Pagan–Sossounov strict (48 phases sur les quatre ETF), Lunde–Timmermann pour SPY avec Pagan–Sossounov ailleurs (66), et une variante symétrique (102). La lecture budget (exacte, Lemme 1) sert au recensement ; la lecture anytime-valid sert aux détections. Il ne s'exécute qu'avec la configuration gelée au J4. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e8_real_regimes.py`, lancé via le runner avec `--include-test-window`.
1. **Phases** : fichiers `phases_*.csv` de D1. Pour D2, D3 (et D4 [B]) : phases de l'indice SPY, plus une datation sectorielle par Pagan–Sossounov sur les indices sectoriels équipondérés de D3.
2. **Pipelines** : P1 à P5, avec D* et seuils gelés.
3. **Mesures par phase et par datation** :
   - Î débiaisé du sous-espace du pipeline ;
   - part dans le budget oracle (L·Î ≥ ln γ, γ ∈ {20, 252}) ;
   - détections dans la phase ;
   - fausses alarmes en phases calmes ;
   - délai depuis le début de phase.
4. **Rapport.** Résultats par datation, jamais agrégés en une seule preuve (peu de phases : appui seulement). Comparer à « 2 phases sur 66 » de l'Article B, en rappelant sa composition de datation.

### Entrées
Prompt 21 (gel) ; tous les pipelines ; `CLAUDE.md`.

### Livrables
`experiments/e8_real_regimes.py`, `configs/e8.yaml`, `results/e8/{e8_phases.csv,e8_summary.csv}`, `figures/e8/*`.

### Contraintes techniques
Refus d'exécution si `configs/FROZEN.json` ne correspond pas ; aucune retouche après lecture des résultats sans nouvelle empreinte consignée.

### Critères de succès
Trois datations traitées ; IC de Wilson sur les proportions ; empreinte de gel inscrite dans chaque CSV.

### Commandes de vérification
```bash
python tools/freeze_config.py --check && python -m jepadrift.benchmark_runner --config configs/e8.yaml --include-test-window
```
