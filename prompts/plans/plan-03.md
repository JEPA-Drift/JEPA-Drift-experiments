# Plan final — Stream 03 : D3 S&P 500, secteurs GICS et caractéristiques

Date : 2026-10-16. Statut : **GO** (décision du chercheur, `prompts/GO-stream-03.md`).
Ce fichier est le plan final ; le plan temporaire `prompts/plans/plan-03-temp.md` est conservé sans modification.

## 1. Résumé

Construire le jeu D3 (coupe transversale S&P 500, ~500 titres) : univers depuis CD-DFM/Wikipedia, cours
ajustés depuis Yahoo Finance (yfinance), log-rendements, caractéristiques datées (beta_252, vol_63,
mom_12_1, rev_21, one-hot GICS) connues à l'ouverture de t, sous-ensembles d3_239 et d3_500 au format D2,
chargeur `jepadrift/data_loader/sp500.py`, tests de contrat, profil descriptif et écarts documentés.
Bloquant pour J2 (25 octobre) et J3 (1er novembre).

## 2. Décisions d'architecture clés

| Question | Décision | Justification |
|---|---|---|
| Environnement Python | `.venv` (activé) pour tout : build, tests, `make check` | Cohérence avec le stream 02 ; `make check` utilise le venv activé |
| yfinance | Installer dans `.venv` via pip (`yfinance>=1.2.0`, pas de borne sup sur numpy/pandas — compatible avec numpy 2.4.4 / pandas 3.0.6) | Le build en a besoin ; les tests n'en ont pas besoin (import lazy) |
| Import yfinance | Lazy (dans les fonctions `_download_*`, pas en top-level) | `make check` (pyflakes + pytest) ne doit pas échouer si yfinance absent ; les tests testent les artefacts dérivés, pas le téléchargement |
| Parsing Wikipedia | `urllib.request` (stdlib) + `pandas.read_html` (lxml/bs4 déjà deps de yfinance) | Pas de dépendance supplémentaire ; page confirmée avec 1 wikitable |
| Clone CD-DFM | `git clone` dans `external/cd-dfm/` (gitignoré), commit épinglé dans le manifeste | `external/` est gitignoré ; le prompt exige le clone |
| Liste 239 titres CD-DFM | **Absente du dépôt** (données RavenPack/Compustat non redistribuables — confirmé par inspection du dépôt) | Consigner `C-D3-no239` ; règle déterministe de repli : 239 titres à l'historique le plus long depuis 2000-01-01 parmi les constituants actuels du S&P 500 |
| Univers d3_500 | Constituants actuels du S&P 500 (Wikipedia), ~500 titres | `C-D3-survivor` : constituants actuels, pas de biais de survie |
| GICS | Secteur GICS actuel (non point-in-time) depuis Wikipedia | `C-D3-gics-static` consigné |
| Calendrier | Union des jours de trading de tous les titres téléchargés | Comme D1 (union des calendriers) |
| Cache brut | `data/raw/d3_yf/<TICKER>.parquet` (gitignoré), SHA-256 par fichier | Reprise sans re-téléchargement sauf `--refresh` |
| Format de sortie | Identique à D2 : `panel.parquet`, `ret_wide.npy`, `dates.npy`, `assets.json`, `splits.yaml` + `chars.parquet` + `flags.csv` | Cohérence inter-jeux ; `splits.yaml` mêmes bornes que D2 |
| **Limite 50 Mo/fichier (GO)** | **Committer les deux panneaux d3_239 et d3_500.** Si un fichier dépasse 50 Mo : réécrire en parquet `compression='zstd'` avec dictionary encoding. `d3_500/chars.parquet` est le seul fichier à risque : si zstd ne suffit pas, sharder par année (`chars_YYYY.parquet`) et consigner `C-D3-shard`. Ne pas découper en plusieurs commits (la règle est par fichier). Ne pas utiliser Git LFS. | Données publiques (Yahoo/Wikipedia) ; l'ancrage reproductible est le panneau dérivé commité + hash de sortie, pas le re-téléchargement (Yahoo révise l'historique ajusté). |

## 3. Plan détaillé

### Phase 0 — Dépendances (prérequis)

```bash
source .venv/bin/activate
pip install yfinance           # installe yfinance + deps manquantes (bs4, lxml, requests, etc.)
pip freeze > requirements.lock  # met à jour le lock
# Ajouter "yfinance" dans requirements.txt
make check                      # vérifier non-régression (21 tests existants doivent rester verts)
```

Vérifier que pip n'a pas modifié numpy/pandas dans `.venv` (yfinance 1.2.0 exige `numpy>=1.16.5`,
`pandas>=1.3.0`, pas de borne sup).

### Phase 1 — Univers (item 1 du prompt)

**1a. Clone CD-DFM**
```bash
git clone https://github.com/alexouadi/CD-DFM external/cd-dfm
git -C external/cd-dfm rev-parse HEAD   # épingler le commit
```
Rechercher la liste des 239 tickers dans le dépôt (fichiers data, configs, scripts).
**Constaté : absente** (README : « We cannot redistribute the panel »). Consigner `C-D3-no239`.

**1b. Règle de repli déterministe pour les 239 titres**
- Depuis la liste Wikipedia des constituants actuels (~500 titres)
- Pour chaque ticker, télécharger l'historique depuis 2000-01-01 (Phase 2)
- Règle : prendre les 239 tickers avec le plus grand nombre de jours de trading depuis 2000-01-01 ;
  ex æquo, ordre alphabétique
- Documenter la règle dans le code et dans `docs/DEVIATIONS.md` sous `C-D3-no239`

**1c. Table Wikipedia**
- URL : `https://en.wikipedia.org/wiki/List_of_S&P_500_companies`
- Fetch via `urllib.request` avec User-Agent
- Parse via `pandas.read_html` (lxml)
- Colonnes attendues : Symbol, Security, GICS Sector, GICS Sub-Industry, Date first added, CIK, Founded
- Sauvegarder : `data/raw/d3_yf/sp500_wikipedia.csv` avec date de récupération et SHA-256 dans le log
- Normaliser les tickers : `BRK.B` → `BRK-B` (convention yfinance)

### Phase 2 — Cours (item 2 du prompt)

- Source : `yfinance` — par ticker : `yf.Ticker(tk).history(start='2000-01-01', auto_adjust=True)`
- Cache : `data/raw/d3_yf/<TICKER>.parquet` — colonnes `date, close` (ajusté), SHA-256 dans
  `data/raw/d3_yf/_hashes.json`
- Reprise : si le cache existe et `--refresh` absent, skip ; sinon télécharger
- Backoff exponentiel : en cas d'échec, attendre 2^n secondes (n = 1, 2, 3, max 60s), 5 tentatives max
- Journaliser chaque échec dans `logs/data/d3_build.log` (jamais silencieux)
- Ticker mapping : dictionnaire explicite `{'BRK.B': 'BRK-B', 'BF.B': 'BF-B', ...}` (Wikipedia → Yahoo)

### Phase 3 — Rendements (item 3 du prompt)

- Log-rendements : `r[t] = log(close[t] / close[t-1])`
- Pas de forward-fill
- `in_universe[t,i]` = vrai ssi close existe en t-1 et en t (donc r[t,i] non-NaN)
- Rendements nuls conservés ; `|r| > 0.5` signalé dans `flags.csv`
  (colonnes : `date, asset_id, ret, flag='abs_gt_0.5'`), sans suppression

### Phase 4 — Caractéristiques (item 4 du prompt)

Pour chaque jour t, en utilisant uniquement les rendements jusqu'à t-1 :

| Caractéristique | Formule | Fenêtre | Min obs |
|---|---|---|---|
| `beta_252` | Pente MCO de r_i sur r_mkt (équipondéré des titres présents) | 252 jours | 126 |
| `vol_63` | Écart-type des rendements | 63 jours | — |
| `mom_12_1` | Somme des rendements sur [t-252, t-22] | 231 jours | — |
| `rev_21` | Somme des rendements sur [t-21, t-1] | 21 jours | — |
| `gics_<sector>` | One-hot du secteur GICS (11 secteurs) | — | — |

- **Transformation en rangs** : chaque jour, chaque caractéristique continue est transformée en rang
  centré dans [-0.5, 0.5] : `rank_i / N - 0.5` (ex æquo moyennés — `method='average'` dans `pandas.rank`)
- Sortie : `chars.parquet` (long : `date, asset_id, c_beta_252, c_vol_63, c_mom_12_1, c_rev_21,
  c_gics_<sector>...`)
- **Non-anticipation** : toute caractéristique à la date t n'utilise que les rendements < t

### Phase 5 — Sous-ensembles (item 5 du prompt)

- `data/derived/d3_239/` : 239 titres (règle Phase 1b)
- `data/derived/d3_500/` : ~500 titres (tous les constituants Wikipedia avec données suffisantes)
- Chacun contient : `panel.parquet`, `ret_wide.npy`, `dates.npy`, `assets.json`, `chars.parquet`,
  `splits.yaml`, `flags.csv`
- `splits.yaml` : mêmes bornes nominales que D2 (pretrain 2005-2016, calib 2016-2020, monitor 2020-end,
  embargo 65 jours), dates réalisées sur le calendrier D3

### Phase 6 — Chargeur (item 6 du prompt)

`jepadrift/data_loader/sp500.py` :
- Structure miroir de `articleB.py` : constantes, `_sha256`, loaders, builders, `build()`, `main()`
  avec `--build` et `--refresh`
- Loaders : `load_d3_239()`, `load_d3_500()` → `(ret, dates, assets)` ; `load_chars(subset)` → DataFrame ;
  `load_splits(subset)` → dict
- Build : orchestre les Phases 1-5, écrit le profil (Phase 8), met à jour le manifeste (Phase 9)
- `import yfinance` en lazy (dans les fonctions de téléchargement uniquement)
- Set `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE` avant
  `import numpy` (pattern articleB.py)

### Phase 7 — Tests (item 7 du prompt)

`tests/test_data_d3.py` — 4 tests minimum :

1. **Non-anticipation** : perturber les rendements à partir d'une date s → les caractéristiques
   jusqu'à s restent identiques bit à bit.
2. **Pas de NaN** : quand `in_universe` est vrai, aucune caractéristique n'est NaN après la période
   d'amorçage (252 jours).
3. **Correspondance secteurs** : chaque asset_id a exactement un secteur GICS one-hot actif ; la
   somme des one-hot = 1 pour tout asset dans l'univers.
4. **Reconstruction depuis le cache** : SHA-256 des fichiers dérivés reconstruits = SHA-256 du manifeste.

Tests supplémentaires recommandés :
- Contrat loader (shape, dtype, dates)
- `splits.yaml` bornes et embargo (miroir du test D2)
- Au moins 450 titres dans d3_500 en 2020 (critère de succès du prompt)
- `chars.parquet` : colonnes, plage des rangs [-0.5, 0.5]

### Phase 8 — Rapport (item 8 du prompt)

`results/data/d3_profile.csv` — colonnes :
- `dataset` (d3_239, d3_500), `segment` (pretrain, calib, monitor)
- `days`, `assets` (titres par jour : moyenne, min, max)
- `coverage_annual` : fraction de jours où au moins X% des titres sont dans l'univers, par année
- `eta_2022_2024` : pour d3_239, une mesure de concentration (ex: k_eff = 1/mean_sign_corr) sur 2022-2024
- Note : CD-DFM rapporte R² = 0.36 pour son facteur de marché — valeur rapportée, non contrôlée

### Phase 9 — Écarts et manifeste (item 9 du prompt)

`docs/DEVIATIONS.md` — ajouter (en français, comme le fichier) :
- **C-D3-no239** : la liste des 239 titres CD-DFM est absente du dépôt (données non redistribuables) ;
  règle de repli déterministe appliquée
- **C-D3-survivor** : d3_500 = constituants actuels du S&P 500 (pas de biais de survie, contrairement à D2)
- **C-D3-gics-static** : secteur GICS actuel, non point-in-time
- **C-D3-shard** (si sharding de `chars.parquet`) : sharding par année si zstd insuffisant
- **Provenance** : les hashes des bruts Yahoo sont une provenance à date fixe ; l'ancrage reproductible
  est le panneau dérivé commité + hash de sortie. Le déterminisme bit-à-bit du parquet repose sur
  pyarrow épinglé + codec fixé + pas de timestamp embarqué.

`data/derived/MANIFEST.json` — étendre avec les entrées D3 :
- Source : yfinance 1.2.0, Wikipedia (date + SHA-256), CD-DFM (commit)
- Inputs : hashes des caches bruts (ou hash agrégé), table Wikipedia
- Outputs : SHA-256 de tous les fichiers dérivés d3_239 et d3_500

## 4. Fichiers à créer/modifier

### Créés

| Fichier | Description |
|---|---|
| `jepadrift/data_loader/sp500.py` | Chargeur + builder D3 |
| `tests/test_data_d3.py` | Tests de contrat D3 |
| `data/derived/d3_239/{panel.parquet,ret_wide.npy,dates.npy,assets.json,chars.parquet,splits.yaml,flags.csv}` | Sous-ensemble 239 titres |
| `data/derived/d3_500/{panel.parquet,ret_wide.npy,dates.npy,assets.json,chars.parquet,splits.yaml,flags.csv}` | Sous-ensemble ~500 titres |
| `results/data/d3_profile.csv` | Profil descriptif |
| `logs/data/d3_build.log` | Journal de build |
| `prompts/wrapups/wrapup-03.md` | Wrapup de fin de stream |

### Modifiés

| Fichier | Modification |
|---|---|
| `requirements.txt` | + `yfinance` |
| `requirements.lock` | + yfinance et deps transitives (pip freeze) |
| `data/derived/MANIFEST.json` | + entrées D3 (inputs, outputs, sources) |
| `docs/DEVIATIONS.md` | + C-D3-no239, C-D3-survivor, C-D3-gics-static, C-D3-shard (si applicable), provenance |

### Non commités (gitignorés)

- `data/raw/d3_yf/` (cache brut par ticker)
- `external/cd-dfm/` (clone CD-DFM)

## 5. Commandes de vérification

```bash
# Build (venv activé)
python -m jepadrift.data_loader.sp500 --build

# Tests ciblés
pytest -q tests/test_data_d3.py -v

# Tests complets + lint
make check

# Inspection rapide
python -c "import pandas as pd; c=pd.read_parquet('data/derived/d3_239/chars.parquet'); print(c.shape, c.date.min(), c.date.max())"
python -c "import pandas as pd; p=pd.read_parquet('data/derived/d3_500/panel.parquet'); print(p.asset_id.nunique())"
```

## 6. Critères de succès (du prompt)

- [ ] Au moins 450 titres dans `d3_500` en 2020
- [ ] Tests au vert (`pytest -q tests/test_data_d3.py`)
- [ ] Reconstruction déterministe (SHA-256 stable)
- [ ] Écarts consignés dans `docs/DEVIATIONS.md`
- [ ] `make check` vert (non-régression des 21 tests existants)
- [ ] Aucun fichier > 50 Mo dans le range pushé (vérifié avant push)

## 7. Risques et points de vigilance

| Risque | Mitigation |
|---|---|
| Rate limiting Yahoo Finance | yfinance a un retry interne ; backoff exponentiel ; cache par ticker ; reprise sans `--refresh`. ~500 téléchargements = long (estimer 30-90 min) |
| Tick ers Wikipedia ≠ Yahoo | Mapping explicite (`BRK.B`→`BRK-B`, etc.) ; tickers sans données Yahoo → exclus de d3_500, loggés |
| yfinance instable | Version figée (1.2.0) ; cache SHA-256 ; pas de re-téléchargement sans `--refresh` |
| Période d'amorçage | 252 jours pour beta_252 ; caractéristiques NaN avant → `in_universe` gère ; test de non-NaN après amorçage |
| **Fichier > 50 Mo (GO)** | Mesurer après build. Si dépassement : réécrire en `compression='zstd'` avec dictionary encoding. `d3_500/chars.parquet` seul à risque → sharder par année (`chars_YYYY.parquet`) + consigner `C-D3-shard`. Ne pas découper en commits. Ne pas utiliser Git LFS. |
| Non-anticipation | Test explicite requis ; toute fuite = CRITICAL |
| Déterminisme | Pas de `np.random` global ; pas de timestamps dans les artefacts ; SHA-256 stable |
| Wiki bloque le fetch | User-Agent explicite ; si 403, fallback sur `curl` avec headers |
| GitHub 100 Mo hard limit | Même gestion que 50 Mo ; zstd + sharding si nécessaire |

## 8. Chronologie proposée

| Phase | Contenu | Durée estimée |
|---|---|---|
| 0 | Dépendances (yfinance, lock, make check) | ~15 min |
| 1 | Clone CD-DFM, fetch Wikipedia, univers | ~30 min |
| 2 | Téléchargement cours (~500 tickers, backoff) | ~60-90 min |
| 3 | Rendements, in_universe, flags | ~15 min |
| 4 | Caractéristiques (beta, vol, mom, rev, GICS) | ~30 min |
| 5 | Sous-ensembles d3_239, d3_500, splits | ~15 min |
| 6 | Chargeur sp500.py (loaders + build CLI) | ~30 min |
| 7 | Tests test_data_d3.py | ~30 min |
| 8 | Profil d3_profile.csv | ~15 min |
| 9 | Deviations, manifeste, wrapup | ~15 min |
| 10 | make check, reindex, commit, push | ~15 min |

**Total estimé : 4-5 heures** (dont 1-1,5 h de téléchargement Yahoo).

## 9. Protocole de fin de stream (inchangé)

1. Wrapup enregistré dans `prompts/wrapups/wrapup-03.md`
2. `tools/reindex_graphify_jcodemunch.sh` (réindexe jCodeMunch et Graphify)
3. `make check` puis commit (Conventional Commits, sans trailer Co-authored-by)
4. `git push origin main` — après vérification du range (aucun chemin sous `data/raw/eurofidai/` ou
   `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo)
