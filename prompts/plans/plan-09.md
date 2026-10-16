# Plan — Stream 09 : BAF (Bank Account Fraud, variante Base), téléchargement, contrôle et découpage

Date : 2026-10-16. Statut : **GO** (décision du chercheur, `prompts/GO-stream-09.md`).
Ce fichier est le plan d'implémentation du stream 09 ; il est enregistré avant exécution
(règle `C-plan-recording`). Les clarifications du GO sont intégrées.

## 1. Résumé

Construire le jeu D7 (BAF — Bank Account Fraud, Jesus et al., NeurIPS 2022 Datasets and
Benchmarks) : téléchargement via l'API Kaggle, contrôles (6 variantes, 1M lignes, 32 colonnes,
8 mois), conversion de la variante Base en parquet prétraité (standardisation des numériques,
encodage des catégoriels, paramètres figés sur les mois 0–2), découpage `fit`/`calib`/`monitor`
par mois, chargeur `jepadrift/data_loader/baf.py`, tests de contrat, profil descriptif et écart
`C-BAF-synthetic`. Non bloquant pour J1/J2 ; requis pour T-JEPA (prompt 15) et E9.

## 2. Décisions d'architecture clés

| Question | Décision | Justification |
|---|---|---|
| Environnement Python | `.venv` (activé) pour tout : build, tests, `make check` | Cohérence avec les streams 02–06 ; `make check` utilise le venv activé |
| API Kaggle | Installer `kaggle==1.6.17` (épinglé) dans `.venv` ; import lazy (dans `_download_baf`) | `make check` ne doit pas échouer si kaggle absent ; version épinglée comme les autres dépendances |
| Identifiants Kaggle | Lus dans `~/.kaggle/access_token` (format `KGAT_…`) ou `~/.kaggle/kaggle.json` par l'API Kaggle | Jamais commités ; le fichier est hors dépôt |
| Identifiant dataset Kaggle | `sgpjesus/bank-account-fraud-dataset-neurips-2022` (vérifié contre la fiche Kaggle et le dépôt GitHub `feedzai/bank-account-fraud`) | Fiche technique officielle ; l'identifiant est confirmé dans le prompt |
| Cache brut | `data/raw/baf/` (gitigné, déjà couvert par `data/raw/`) | Le `.gitignore` ignore `data/raw/` ; les CSV bruts ne sont jamais commités |
| Fichier traité | Uniquement `Base.csv` (variante Base) ; les 5 autres variantes sont contrôlées (taille) mais non converties | Le prompt demande la conversion de Base uniquement |
| Format de sortie | `data/derived/d7_baf/base.parquet` — 32 colonnes (30 attributs + `fraud_bool` + `month`), index 0..999999, **compression zstd**, catégorielles en **int16**, **< 50 Mo** | Conversion + prétraitement dans le même fichier ; taille < 50 Mo bloquante pour le push |
| Prétraitement | Figé sur les mois 0–2 : standardisation z-score des 25 numériques (20 continus + 5 booléennes), encodage entier des 5 catégoriels (inconnues → −1 réservé), sentinelles −1 standardisées comme les autres (elles ne sont plus −1 après z-score) | Aucun paramètre estimé hors des mois 0–2 ; `preproc.json` sauvegarde les paramètres |
| Découpage | `splits.yaml` : `fit` mois 0–2, `calib` mois 3, `monitor` mois 4–7 ; pas d'embargo (dérive native) | Conforme au prompt ; les mois BAF sont natifs, pas des jours de trading |
| Profil | `results/data/baf_profile.csv` : **calculé sur les données BRUTES** (avant prétraitement) — effectifs, taux de fraude, moyennes brutes des 25 numériques par mois (28 colonnes) | GO-stream-09 : le profil décrit les données brutes, pas les z-scores |
| Manifeste | Étendre `data/derived/MANIFEST.json` avec les entrées D7 (préservation des entrées existantes via le mécanisme `C-D3-manifest-merge`) | Cohérence inter-jeux |
| Colonnes catégorielles | `payment_type`, `employment_status`, `housing_status`, `source`, `device_os` (5 catégorielles string) | D'après la fiche BAF ; à confirmer lors du build |
| Colonnes booléennes | `phone_home_valid`, `phone_mobile_valid`, `has_other_cards`, `foreign_request`, `keep_alive_session` (5 booléennes 0/1, traitées comme numériques) | Standardisées comme les autres numériques |
| Colonnes numériques continues | 20 attributs (voir §3 Phase 4) | Standardisation z-score |

## 3. Plan détaillé

### Phase 0 — Dépendances (prérequis)

```bash
source .venv/bin/activate
pip install kaggle==1.6.17     # version épinglée (GO)
pip freeze > requirements.lock
# Ajouter "kaggle==1.6.17" dans requirements.txt
make check                   # vérifier non-régression (tests existants doivent rester verts)
```

Vérifier que pip n'a pas modifié numpy/pandas/pyarrow dans `.venv`.

**Prérequis externe** : `~/.kaggle/access_token` (format `KGAT_…`) ou `~/.kaggle/kaggle.json`
doit exister. Si absent, le build échoue avec un message explicite. Les tests sont
skippés si les données ne sont pas construites.

### Phase 1 — Source (item 1 du prompt)

Télécharger le jeu BAF via l'API Kaggle :

```python
def _download_baf(log):
    """Télécharge le dataset BAF depuis Kaggle vers data/raw/baf/."""
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()  # lit ~/.kaggle/kaggle.json
    RAW_BAF.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(
        "sgpjesus/bank-account-fraud-dataset-neurips-2022",
        path=str(RAW_BAF),
        unzip=True,
    )
```

- Cache : si `data/raw/baf/Base.csv` existe déjà, skip le téléchargement (sauf `--refresh`).
- Le téléchargement produit 6 CSV (`Base.csv`, `Variant I.csv`, …, `Variant V.csv`) + métadonnées.
- Authentification : `KaggleApi().authenticate()` lit `~/.kaggle/access_token` (format `KGAT_…`)
  ou `~/.kaggle/kaggle.json`.
- Journaliser dans `logs/data/baf_build.log`.

### Phase 2 — Contrôles (item 2 du prompt)

Vérifier les 6 variantes :

| Contrôle | Méthode |
|---|---|
| 6 variantes présentes | Lister les fichiers CSV dans `data/raw/baf/` |
| 1 000 000 lignes chacune | `wc -l` (1 000 001 avec header) — ne pas charger les 6 CSV en mémoire |
| 30 attributs + `fraud_bool` + `month` = 32 colonnes | Lire l'en-tête CSV ; **validation stricte** : si les noms ne correspondent pas exactement aux 32 attendus, lever une erreur avec la liste des écarts |
| `month` ∈ {0,…,7} | `df["month"].unique()` trié |
| Schéma (types, catégories) | `df.dtypes` ; distinguer 20 numériques continus, 5 booléennes, 5 catégorielles string |
| **Validation stricte** | Colonne catégorielle avec > 50 valeurs uniques → warning. Colonne booléenne avec valeurs autres que {0, 1} → erreur |
| Licence | Lire la fiche Kaggle / dépôt GitHub ; consigner dans `docs/sections/data_baf.md` |
| Prévalence de fraude par mois | `df.groupby("month")["fraud_bool"].mean()` → profil CSV |

Consigner le schéma dans `docs/sections/data_baf.md` (tableau attribut / type / traitement).

### Phase 3 — Conversion (item 3 du prompt)

Lire `Base.csv` avec pandas (dtypes explicites), conserver l'ordre des lignes d'origine,
écrire `data/derived/d7_baf/base.parquet` :

- Lecture : `pd.read_csv(RAW_BAF / "Base.csv", dtype={...})` avec dtypes explicites pour
  garantir la reproductibilité (float64 pour les numériques, int64 pour `month` et
  `fraud_bool`, category pour les catégoriels string).
- L'index pandas (0..999999) préserve l'ordre des lignes d'origine.
- Le parquet est écrit **après prétraitement** (Phase 4) : le fichier final contient les
  valeurs prétraitées.
- **Format** : compression **`zstd`**, colonnes catégorielles encodées en **int16**,
  taille cible **< 50 Mo** (vérifiée après écriture).

### Phase 4 — Prétraitement figé (item 4 du prompt)

Appliquer le prétraitement appris **uniquement sur les mois 0–2** :

**4a. Standardisation des numériques**

- Pour chaque attribut numérique (20 continus + 5 booléens = 25) :
  - `mean`, `std` calculés sur les lignes où `month ∈ {0, 1, 2}`.
  - `std = 0` → remplacé par 1 (évite la division par zéro).
  - Transformation : `z = (x - mean) / std` appliqué à **toutes** les lignes.
- Les sentinelles −1 sont **standardisées comme les autres valeurs** (après z-score, elles
  ne sont plus égales à −1 ; c'est le comportement attendu). La liste des colonnes
  concernées est documentée dans `preproc.json` (section `sentinels`) et dans
  `docs/sections/data_baf.md`.

**4b. Encodage des catégoriels**

- Pour chaque attribut catégoriel string (5 : `payment_type`, `employment_status`,
  `housing_status`, `source`, `device_os`) :
  - Construire le vocabulaire sur les mois 0–2 uniquement : `vocab = sorted(unique(months 0-2))`.
  - Mapping `category → code` (0, 1, 2, …).
  - Inconnues (présentes en calib/monitor mais pas en fit) → code −1 (réservé).
- Le mapping est sauvegardé dans `preproc.json`.

**4c. Sauvegarde des paramètres**

`data/derived/d7_baf/preproc.json` :

```json
{
  "fit_months": [0, 1, 2],
  "numeric": {
    "income": {"mean": ..., "std": ...},
    ...
  },
  "categorical": {
    "payment_type": {"vocab": ["AA", "AB", ...], "unknown_code": -1},
    ...
  },
  "sentinels": {
    "description": "Les valeurs -1 dans les attributs listés sont des sentinelles documentees dans la fiche BAF (missing/not applicable). Elles sont standardisees comme les autres valeurs (z-score) ; apres pretraitement, elles ne sont plus egales a -1.",
    "columns": ["prev_address_months_count", "current_address_months_count", ...]
  }
}
```

### Phase 5 — Découpage (item 3 du prompt, suite)

`data/derived/d7_baf/splits.yaml` :

```yaml
dataset: d7_baf
convention: "fit months 0-2, calib month 3, monitor months 4-7; no embargo (native drift in a synthetic dataset)"
segments:
  fit:
    months: [0, 1, 2]
  calib:
    months: [3]
  monitor:
    months: [4, 5, 6, 7]
```

### Phase 6 — Chargeur (livrable `jepadrift/data_loader/baf.py`)

Structure miroir de `sp500.py` :

- Constantes : `REPO_ROOT`, `RAW_BAF`, `DERIVED`, `D7_DIR = "d7_baf"`, chemins.
- `_sha256(path)` : helper identique.
- `_download_baf(log)` : téléchargement Kaggle (import lazy).
- `_control_variants(log)` : contrôles Phase 2.
- `_fit_preproc(df)` : fit sur mois 0–2, retourne `(params, df_preprocessed)`.
- `_apply_preproc(df, params)` : applique le prétraitement.
- `build(refresh=False)` : orchestre les Phases 1–5, écrit le profil (Phase 8), met à jour
  le manifeste (Phase 9).
- Loaders :
  - `load_baf()` → `pd.DataFrame` (lit `base.parquet`).
  - `load_splits()` → `dict` (lit `splits.yaml`).
  - `load_preproc()` → `dict` (lit `preproc.json`).
- `main()` avec `--build` et `--refresh`.
- Set `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE` avant
  `import numpy` (pattern articleB.py).

### Phase 7 — Tests (livrable `tests/test_data_baf.py`)

Tests skippés si les données ne sont pas construites (fixture `_baf_built` sur `base.parquet`).

1. **Forme** : 1 000 000 lignes, 32 colonnes, index 0..999999.
2. **Mois** : `month` ∈ {0,…,7}, les 8 mois présents.
3. **Fraude** : `fraud_bool` ∈ {0, 1} ; taux de fraude global cohérent (~1 % d'après la fiche BAF).
4. **Pas de NaN** : aucune valeur NaN dans le parquet prétraité.
5. **Splits** : `load_splits()` retourne `fit`/`calib`/`monitor` avec les bons mois.
6. **Reproductibilité** : SHA-256 de `preproc.json` stable (rebuild → même hash).
7. **Contrat loader** : `load_baf()` retourne un DataFrame de 1M×32, dtypes corrects.
8. **Prétraitement figé** : sur les mois fit, moyennes ≈ 0 et écart-types ≈ 1 pour les
   25 numériques (vérifié sur le parquet prétraité).
9. **Catégoriels** : les codes sont dans {−1, 0, 1, …, |vocab|−1} ; les mois 0–2 n'ont pas de −1.
10. **Sentinelles** : les colonnes listées dans `preproc.json["sentinels"]["columns"]`
    sont bien des colonnes numériques ; après standardisation, les anciennes valeurs −1
    ne sont plus identifiables comme telles (pas de pic anormal à une valeur entière).
11. **Manifeste** : SHA-256 des fichiers D7 dans `MANIFEST.json` correspondent au disque ;
    les entrées D1/D2/D3 sont préservées (non-régression).
12. **Profil CSV** : `results/data/baf_profile.csv` existe, 8 lignes, 28 colonnes ;
    `fraud_rate` cohérent avec le parquet ; `mean_<feature>` sur données brutes
    (vérifier une valeur de référence : moyenne de `income` sur le mois 0, arrondie).
13. **Taille parquet** : `base.parquet` < 50 Mo.

### Phase 8 — Profil (item 5 du prompt)

`results/data/baf_profile.csv` — **calculé sur les données BRUTES** (avant prétraitement),
une ligne par mois (0–7) :

| Colonne | Description |
|---|---|
| `month` | 0–7 |
| `n_rows` | Effectif du mois |
| `fraud_rate` | Taux de fraude (`fraud_bool.mean()`) |
| `mean_<feature>` | Moyenne **brute** de chaque attribut numérique (25 colonnes) |

Total : 8 lignes × 28 colonnes.

### Phase 9 — Écarts et documentation (items 2 et 6 du prompt)

**`docs/DEVIATIONS.md`** — ajouter :

- **C-BAF-synthetic** : « dérive native d'un jeu synthétique » (BAF est généré à partir de
  données réelles mais reste un jeu synthétique). Ne jamais écrire « in-the-wild ».

**`docs/sections/data_baf.md`** — livrable : source (Kaggle, licence), schéma des 32 colonnes
(tableau attribut / type / traitement), contrôles effectués, prétraitement, découpage,
profil de fraude par mois.

**`data/derived/MANIFEST.json`** — **fusionner** avec le manifeste existant (ne pas écraser
les entrées `d1_etf4`, `d2_us97`, `d3_239`, `d3_500` ni les champs `generator` et `source`) :

```json
{
  "datasets": {
    "d7_baf": {
      "inputs": [{"path": "data/raw/baf/Base.csv", "sha256": "...", "rows": 1000000}],
      "outputs": [
        {"path": "data/derived/d7_baf/base.parquet", "sha256": "...", "rows": 1000000},
        {"path": "data/derived/d7_baf/splits.yaml", "sha256": "..."},
        {"path": "data/derived/d7_baf/preproc.json", "sha256": "..."}
      ]
    }
  },
  "results": {
    "baf_profile": {"path": "results/data/baf_profile.csv", "sha256": "...", "rows": 8}
  },
  "sources": {
    "d7_baf": {
      "kaggle_dataset": "sgpjesus/bank-account-fraud-dataset-neurips-2022",
      "kaggle_api": "1.6.17",
      "license": "...",
      "variants_checked": 6,
      "variant_converted": "Base"
    }
  }
}
```

## 4. Fichiers à créer/modifier

### Créés

| Fichier | Description |
|---|---|
| `jepadrift/data_loader/baf.py` | Chargeur + builder D7 |
| `tests/test_data_baf.py` | Tests de contrat D7 |
| `data/derived/d7_baf/base.parquet` | Variante Base prétraitée (1M×32) |
| `data/derived/d7_baf/splits.yaml` | Découpage fit/calib/monitor par mois |
| `data/derived/d7_baf/preproc.json` | Paramètres de prétraitement (figés sur mois 0–2) |
| `results/data/baf_profile.csv` | Profil descriptif (8 lignes) |
| `logs/data/baf_build.log` | Journal de build |
| `docs/sections/data_baf.md` | Documentation du jeu D7 |
| `prompts/wrapups/wrapup-09.md` | Wrapup de fin de stream |

### Modifiés

| Fichier | Modification |
|---|---|
| `requirements.txt` | + `kaggle==1.6.17` (épinglé) |
| `requirements.lock` | + kaggle et deps transitives (pip freeze) |
| `data/derived/MANIFEST.json` | + entrées D7 (inputs, outputs, sources, results) |
| `docs/DEVIATIONS.md` | + C-BAF-synthetic |

### Non commités (gitignorés)

- `data/raw/baf/` (CSV bruts Kaggle, ~500 Mo au total)

## 5. Commandes de vérification

```bash
# Build (venv activé, ~/.kaggle/access_token ou kaggle.json requis)
python -m jepadrift.data_loader.baf --build

# Taille du parquet (doit être < 50 Mo)
ls -lh data/derived/d7_baf/base.parquet

# Tests ciblés
pytest -q tests/test_data_baf.py -v

# Tests complets + lint
make check

# Inspection rapide
python -c "import pandas as pd; d=pd.read_parquet('data/derived/d7_baf/base.parquet'); print(d.shape, d.month.value_counts().sort_index().to_dict())"
python -c "import json; p=json.load(open('data/derived/d7_baf/preproc.json')); print(p['fit_months'], len(p['numeric']), len(p['categorical']), p['sentinels']['columns'])"
python -c "import pandas as pd; print(pd.read_csv('results/data/baf_profile.csv', float_precision='round_trip'))"

# Vérification git (aucun fichier sous data/raw/baf/ tracké)
git status --short data/raw/baf/
```

## 6. Critères de succès (du prompt + GO)

- [ ] 1 000 000 lignes, 32 colonnes, 8 mois (`month` ∈ {0,…,7})
- [ ] `base.parquet` < 50 Mo (compression zstd)
- [ ] Tests au vert (`pytest -q tests/test_data_baf.py`)
- [ ] Prétraitement reproductible au SHA-256 près (`preproc.json` stable)
- [ ] `make check` vert (non-régression des tests existants)
- [ ] Écart `C-BAF-synthetic` consigné dans `docs/DEVIATIONS.md`
- [ ] `docs/sections/data_baf.md` rédigé (avec licence)
- [ ] Manifeste fusionné sans perte des entrées existantes
- [ ] Aucun fichier > 50 Mo dans le range pushé ; `data/raw/baf/` non tracké

## 7. Risques et points de vigilance

| Risque | Mitigation |
|---|---|
| `~/.kaggle/access_token` ou `kaggle.json` absent | Message d'erreur explicite ; les tests sont skippés ; l'utilisateur doit fournir les identifiants |
| Téléchargement Kaggle lent (~500 Mo) | Cache dans `data/raw/baf/` ; reprise sans re-téléchargement sauf `--refresh` |
| Mémoire insuffisante (6 CSV × 1M lignes) | Ne charger que `Base.csv` ; les 5 autres variantes contrôlées par `wc -l` |
| Identifiant Kaggle incorrect | Vérifier contre la fiche Kaggle et le dépôt GitHub `feedzai/bank-account-fraud` avant le téléchargement |
| Fuite de prétraitement (paramètres estimés hors mois 0–2) | Test explicite : moyennes/std des mois fit ≈ 0/1 ; vérification dans `preproc.json` |
| Catégories inconnues en calib/monitor | Code −1 réservé ; test que les mois 0–2 n'ont pas de −1 |
| Sentinelles −1 | Standardisées comme les autres valeurs ; documentées dans `preproc.json` et `docs/sections/data_baf.md` |
| `base.parquet` > 50 Mo | Compression **zstd** dès le départ ; catégorielles en **int16** ; vérifier la taille après écriture |
| Validation stricte du schéma | Catégorielle > 50 uniques → warning ; booléenne hors {0,1} → erreur ; noms de colonnes ≠ 32 attendus → erreur |
| Colonnes catégorielles mal identifiées | Confirmer les dtypes lors du premier build ; ajuster les constantes `NUMERIC_COLS`, `CATEGORICAL_COLS`, `BOOLEAN_COLS` |
| Non-déterminisme du parquet | pyarrow épinglé (26.0.0) + codec fixé (zstd) + pas de timestamp embarqué ; SHA-256 stable |

## 8. Chronologie proposée

| Phase | Contenu | Durée estimée |
|---|---|---|
| 0 | Dépendances (kaggle, lock, make check) | ~10 min |
| 1 | Téléchargement Kaggle (~500 Mo) | ~5-15 min |
| 2 | Contrôles (6 variantes, schéma, licence, prévalence) | ~15 min |
| 3–4 | Conversion + prétraitement (lecture CSV, fit, apply, parquet, preproc.json) | ~20 min |
| 5 | Découpage (splits.yaml) | ~5 min |
| 6 | Chargeur baf.py (loaders + build CLI) | ~30 min |
| 7 | Tests test_data_baf.py | ~30 min |
| 8 | Profil baf_profile.csv | ~10 min |
| 9 | Documentation (data_baf.md, DEVIATIONS, manifeste) | ~20 min |
| 10 | make check, reindex, wrapup, commit, push | ~15 min |

**Total estimé : 2-2,5 heures** (dont 5-15 min de téléchargement Kaggle).

## 9. Protocole de fin de stream (inchangé)

1. Wrapup enregistré dans `prompts/wrapups/wrapup-09.md`
2. `tools/reindex_graphify_jcodemunch.sh` (réindexe jCodeMunch et Graphify)
3. `make check` puis commit (Conventional Commits, sans trailer Co-authored-by)
4. `git push origin main` — après vérification du range (aucun chemin sous `data/raw/eurofidai/`
   ou `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo, `data/raw/baf/` gitignoré donc non pushé)
