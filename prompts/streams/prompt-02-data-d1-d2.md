## PROMPT 2 — Jeux D1 (ETF-4) et D2 (US-97) depuis le dépôt de l'Article B

### Contexte
JEPA-Drift compare des moniteurs séquentiels univariés, poolés et latents sur des rendements quotidiens. D1 (quatre ETF) et D2 (97 actions américaines survivantes) viennent du dépôt public de l'article précédent (« Article B »), avec trois datations des phases haussières et baissières. Ils alimentent E1, E3, l'audit et E8 ; bloquant pour J2 (25 octobre). Lire `CLAUDE.md`.

### Tâche
1. **Ne pas cloner le dépôt distant.** Le dépôt de l'Article B est déjà présent localement : `~/The-Whitening-Advantage-Experiments` (lecture seule, tel quel, à son commit courant ; ne pas modifier ce dépôt, ne pas changer son commit, ne pas cloner `github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments`). « Le dépôt B » désigne désormais `~/The-Whitening-Advantage-Experiments`.
2. Lire le §6 du `~/The-Whitening-Advantage-Experiments/README.md` et `~/The-Whitening-Advantage-Experiments/docs/DEVIATIONS.md`. Écrire un résumé de 20 lignes au plus dans `docs/sections/articleB_deviations_digest.md`, couvrant R00, R01, R08, R15 et R16, avec leurs identifiants.
3. **D1.** Lire `~/The-Whitening-Advantage-Experiments/data/derived_firstrate/R01_daily_{SPY,PFF,VNQ,BWX}.csv` (colonnes `Date,Close,log_ret`).
   - Écrire `data/derived/d1_etf4/panel.parquet` au format long : `date, asset_id, ret (float64 = log_ret), close, in_universe`.
   - Écrire aussi `ret_wide.npy` (NaN hors période), `dates.npy` et `assets.json`.
   - Effectifs attendus : SPY 6414 lignes du 2000-01-04 au 2025-07-07 ; PFF 4403 lignes dès 2007-12-27 ; VNQ 5014 dès 2005-01-04 ; BWX 4451 dès 2007-10-09 ; aucun NaN.
4. **Datations de D1.** Copier `~/The-Whitening-Advantage-Experiments/results/R16_regime_census/data/R16_regime_census.csv`, `..._strict_ps.csv` et `..._symmetric.csv` vers `data/derived/d1_etf4/phases_{lt_spy,strict_ps,symmetric}.csv`, avec une colonne `dating_variant` ajoutée.
   - `lt_spy` (66 phases) = Pagan–Sossounov sur PFF, VNQ et BWX, Lunde–Timmermann sur SPY.
   - `strict_ps` (48 phases) = Pagan–Sossounov sur les quatre ETF.
   - `symmetric` (102 phases) = variante symétrique.
5. **D2.** Lire `~/The-Whitening-Advantage-Experiments/data/derived_equities/R15_panel_logreturns.csv` : 5154 jours × 97 titres, du 2005-01-04 au 2025-06-30, sans NaN, environ 0,66 % de rendements nuls. Produire les mêmes formats dans `data/derived/d2_us97/`, avec `in_universe` toujours vrai.
6. **Découpages.** Écrire `splits.yaml` pour chaque jeu, avec les dates réelles de premier et dernier jour de bourse de chaque segment :
   - pretrain [2005-01-01, 2016-01-01) (D1 : depuis le début de chaque série) ;
   - calib [2016-01-01, 2020-01-01) ;
   - monitor [2020-01-01, fin] ;
   - embargo de 65 jours de bourse après chaque frontière.
7. **Chargeur** `jepadrift/data_loader/articleB.py` : `load_d1()`, `load_d2()`, `load_phases(variant)`, `load_splits(dataset)`. Ils renvoient des tableaux numpy float64, les dates et les identifiants, sans autre transformation. Ajouter un point d'entrée `--build` qui produit tous les fichiers ci-dessus.
8. **Profil descriptif** dans `results/data/d1_d2_profile.csv`, par jeu et par segment :
   - jours, actifs, part de rendements nuls ;
   - corrélation moyenne par paires des signes 1{r>0} sur D2 (proche de 0,26 attendu ; rapporté, non bloquant) ;
   - K_eff = 1/ρ̂ ;
   - part de variance de PC1 (η).
9. **Traçabilité.**
   - `data/derived/MANIFEST.json` : chemin source (`~/The-Whitening-Advantage-Experiments` + commit local), SHA-256 en entrée et en sortie, lignes, dates.
   - `docs/DEVIATIONS.md` : `C-D2-survivor` (97 titres survivants) ; `C-interface-f64` (ret stocké en float64 et non en f32, pour l'identité bit à bit avec l'Article B).

### Entrées
Dépôt de l'Article B local `~/The-Whitening-Advantage-Experiments` (lecture seule) ; `CLAUDE.md`.

### Livrables
`data/derived/{d1_etf4,d2_us97}/…`, `data/derived/MANIFEST.json`, `jepadrift/data_loader/articleB.py`, `tests/test_data_d1_d2.py`, `results/data/d1_d2_profile.csv`, `docs/sections/{articleB_deviations_digest,data_d1_d2}.md`.

### Contraintes techniques
- pandas et pyarrow ; aucune interpolation ni remplissage.
- Le dossier `external/` n'est jamais commité. Le dépôt `~/The-Whitening-Advantage-Experiments` est hors du projet : lecture seule, jamais commité ni modifié.
- Les fichiers dérivés de D1 et D2 sont publics et peuvent être commités.

### Critères de succès
- Effectifs et dates exacts.
- Aller-retour CSV → parquet → numpy identique bit à bit.
- 66, 48 et 102 phases.
- Tests au vert.
- Manifeste complet.

### Commandes de vérification
```bash
cd ~/JEPA-Drift-experiments && source .venv/bin/activate
python -m jepadrift.data_loader.articleB --build
pytest -q tests/test_data_d1_d2.py
python -c "from jepadrift.data_loader.articleB import load_d2; r,d,a=load_d2(); print(r.shape, d[0], d[-1])"
```
