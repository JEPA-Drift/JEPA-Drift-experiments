## PROMPT 3 — Jeu D3 : S&P 500, secteurs GICS et caractéristiques tirées des rendements

### Contexte
D3 est la coupe transversale principale de JEPA-Drift : jusqu'à 500 actions, avec des caractéristiques datées qui conditionnent les représentations (IPCA, CD-DFM, JEPA). Elle est requise pour l'audit et E1 (J2, 25 octobre), puis pour le pré-entraînement (J3, 1er novembre). Lire `CLAUDE.md`.

### Tâche
1. **Univers.**
   - (a) Cloner `https://github.com/alexouadi/CD-DFM` et épingler son commit. Y chercher la liste des 239 titres du S&P 500 utilisés par Alouadi & Lehalle (arXiv:2607.24410).
   - (b) Si elle est absente, consigner `C-D3-no239` et prendre les 239 titres à l'historique le plus long, selon une règle déterministe documentée.
   - (c) Récupérer la table publique Wikipedia « List of S&P 500 companies » : ticker, secteur et sous-industrie GICS, date d'entrée. La sauvegarder avec sa date de récupération et son SHA-256.
2. **Cours.**
   - Source : `yfinance` (version installée, figée dans `requirements.lock`), clôture ajustée quotidienne depuis 2000-01-01.
   - Cache brut par ticker dans `data/raw/d3_yf/<ticker>.parquet`, avec SHA-256.
   - Reprise avec attente exponentielle en cas d'échec ; aucun re-téléchargement sans `--refresh`.
   - Correspondance des tickers (`BRK.B` → `BRK-B`, etc.).
3. **Rendements.**
   - Log-rendements, sans remplissage vers l'avant.
   - `in_universe[t,i]` vaut vrai si et seulement si les cours existent en t−1 et en t.
   - Rendements nuls conservés ; |r| > 0,5 signalé dans `flags.csv`, sans suppression.
4. **Caractéristiques connues à l'ouverture de t** (rendements jusqu'à t−1 seulement) :
   - `beta_252` : pente MCO sur le rendement équipondéré des titres présents, 252 jours, au moins 126 observations ;
   - `vol_63` : volatilité sur 63 jours ;
   - `mom_12_1` : somme des rendements sur [t−252, t−22] ;
   - `rev_21` : somme sur [t−21, t−1] ;
   - secteur GICS en one-hot (actuel, non point-in-time).

   Chaque caractéristique continue est transformée chaque jour en rang centré dans [−0,5 ; 0,5], ex aequo moyennés. Écrire `chars.parquet` (`date, asset_id, c_*`).
5. **Sous-ensembles.** `data/derived/d3_239/` et `data/derived/d3_500/`, aux formats de D2. Mêmes `splits.yaml` que D2.
6. **Chargeur** `jepadrift/data_loader/sp500.py` avec `--build`.
7. **Tests** `tests/test_data_d3.py` :
   - non-anticipation : perturber les rendements à partir d'une date s laisse les caractéristiques jusqu'à s identiques bit à bit ;
   - aucune caractéristique NaN quand `in_universe` est vrai, après la période d'amorçage ;
   - correspondance des secteurs complète ;
   - reconstruction depuis le cache identique (SHA-256).
8. **Rapport** dans `results/data/d3_profile.csv` : titres par jour, couverture annuelle, η sur 2022–2024 pour `d3_239`. CD-DFM rapporte R² = 0,36 pour son facteur de marché ; la valeur est rapportée, non contrôlée.
9. **Écarts** dans `docs/DEVIATIONS.md` : `C-D3-survivor` (constituants actuels) ; `C-D3-gics-static`.

### Entrées
Internet (yfinance, Wikipedia, GitHub) ; `CLAUDE.md` ; `splits.yaml` de D2 comme gabarit.

### Livrables
`data/derived/{d3_239,d3_500}/{panel.parquet,ret_wide.npy,dates.npy,assets.json,chars.parquet,splits.yaml}`, `data/raw/d3_yf/` (ignoré par git), `jepadrift/data_loader/sp500.py`, `tests/test_data_d3.py`, `results/data/d3_profile.csv`, entrées du manifeste.

### Contraintes techniques
- Aucune donnée postérieure à t−1 dans une caractéristique datée t.
- Échecs de téléchargement journalisés, jamais silencieux.
- Les fichiers bruts ne sont pas commités.

### Critères de succès
- Au moins 450 titres dans `d3_500` en 2020.
- Tests au vert.
- Reconstruction déterministe.
- Écarts consignés.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.sp500 --build
pytest -q tests/test_data_d3.py
python -c "import pandas as pd; c=pd.read_parquet('data/derived/d3_239/chars.parquet'); print(c.shape, c.date.min(), c.date.max())"
```
