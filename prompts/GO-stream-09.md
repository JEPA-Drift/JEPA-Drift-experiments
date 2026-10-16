## PROMPT GO — Stream 09 : BAF (Bank Account Fraud, variante Base)

Ce prompt est le lancement du stream 09. Il reprend le prompt original
(`prompts/streams/prompt-09-baf.md`) et intègre les clarifications et améliorations
issues de la revue du plan (`prompts/plans/plan-09.md`). Lire `CLAUDE.md` (AGENTS.md).

---

### Contexte

JEPA-Drift ajoute un domaine tabulaire hors finance : BAF (Jesus et al., NeurIPS 2022
Datasets and Benchmarks). Ce sont des demandes d'ouverture de compte synthétiques,
générées à partir de données réelles, sur huit mois, avec une dérive native. Requis pour
T-JEPA (prompt 15) et E9 ; non bloquant pour J1 et J2.

Identifiant Kaggle confirmé : `sgpjesus/bank-account-fraud-dataset-neurips-2022`.

---

### Tâche

1. **Source.** Télécharger le jeu BAF via l'API Kaggle (`kaggle` installé dans `.venv`,
   import lazy dans la fonction de téléchargement) vers `data/raw/baf/` (gitigné).
   Identifiants lus dans `~/.kaggle/kaggle.json`, jamais commités.
   Vérifier que le téléchargement produit bien 6 fichiers CSV (`Base.csv`,
   `Variant I.csv` à `Variant V.csv`).

2. **Contrôles.**
   - Six variantes présentes, 1 000 000 lignes chacune (vérifier par `wc -l` ou
     lecture partielle — ne pas charger les 6 CSV en mémoire simultanément).
   - 30 attributs + `fraud_bool` + `month` = 32 colonnes ; `month` ∈ {0,…,7}.
   - Schéma (types, catégories) : distinguer 20 numériques continus, 5 booléennes
     (`phone_home_valid`, `phone_mobile_valid`, `has_other_cards`, `foreign_request`,
     `keep_alive_session`), 5 catégorielles string (`payment_type`,
     `employment_status`, `housing_status`, `source`, `device_os`).
   - **Validation stricte au premier build** : si une colonne identifiée comme
     catégorielle contient > 50 valeurs uniques, émettre un warning. Si une colonne
     identifiée comme booléenne contient des valeurs autres que {0, 1}, lever une
     erreur. Si les noms de colonnes ne correspondent pas exactement aux 32 attendus,
     lever une erreur avec la liste des écarts.
   - Licence de la fiche Kaggle (consigner dans `docs/sections/data_baf.md`).
   - Prévalence de fraude par mois.

3. **Conversion.** `Base.csv` → `data/derived/d7_baf/base.parquet`, ordre des lignes
   conservé, index 0..999999. Le parquet est écrit **après prétraitement**.

4. **Prétraitement figé, appris sur les mois 0–2 uniquement** :
   - **Standardisation z-score** des 25 colonnes numériques (20 continus + 5 booléennes) :
     `mean` et `std` calculés sur les lignes `month ∈ {0, 1, 2}`, `std = 0` remplacé par 1.
   - **Sentinelles −1** : les valeurs −1 dans les colonnes numériques documentées comme
     contenant des sentinelles (ex: `prev_address_months_count`,
     `current_address_months_count`, `bank_months_count`, etc. — liste à établir depuis
     la fiche BAF lors du premier build) sont **standardisées comme les autres valeurs**.
     Après standardisation, elles ne sont plus égales à −1 ; c'est le comportement attendu.
     La liste des colonnes concernées est documentée dans `preproc.json` (section
     `sentinels`) et dans `docs/sections/data_baf.md`.
   - **Encodage des catégoriels** (5 colonnes) : vocabulaire construit sur les mois 0–2
     (`sorted(unique)`), mapping `category → code` (0, 1, 2, …). Inconnues en calib/monitor
     → code −1 (réservé). Le mapping est sauvegardé dans `preproc.json`.
   - **Sauvegarde** : `data/derived/d7_baf/preproc.json` avec `fit_months`, `numeric`
     (mean/std par colonne), `categorical` (vocab + unknown_code par colonne),
     `sentinels` (description + liste des colonnes).

5. **Découpage.** `data/derived/d7_baf/splits.yaml` : `fit` mois 0–2, `calib` mois 3,
   `monitor` mois 4–7. Pas d'embargo (dérive native).

6. **Profil** `results/data/baf_profile.csv` — **calculé sur les données BRUTES**
   (avant prétraitement), une ligne par mois (0–7) :
   - `month`, `n_rows`, `fraud_rate`
   - `mean_<feature>` pour les 25 attributs numériques (moyennes brutes, pas z-scores)
   Total : 8 lignes × 28 colonnes.

7. **Écarts.** `C-BAF-synthetic` dans `docs/DEVIATIONS.md` : « dérive native d'un jeu
   synthétique », jamais « in-the-wild ».

---

### Livrables

| Fichier | Description |
|---|---|
| `jepadrift/data_loader/baf.py` | Chargeur + builder D7 (CLI `--build`, `--refresh`) |
| `tests/test_data_baf.py` | Tests de contrat D7 (skippés si données non construites) |
| `data/derived/d7_baf/base.parquet` | Variante Base prétraitée (1M×32, **< 50 Mo**) |
| `data/derived/d7_baf/splits.yaml` | Découpage fit/calib/monitor |
| `data/derived/d7_baf/preproc.json` | Paramètres de prétraitement figés |
| `results/data/baf_profile.csv` | Profil descriptif sur données brutes (8 lignes) |
| `logs/data/baf_build.log` | Journal de build |
| `docs/sections/data_baf.md` | Documentation du jeu D7 (source, licence, schéma, contrôles) |
| `prompts/wrapups/wrapup-09.md` | Wrapup de fin de stream |

Fichiers modifiés : `requirements.txt` (+ `kaggle` **épinglé**, ex: `kaggle==1.6.17`),
`requirements.lock` (pip freeze), `data/derived/MANIFEST.json` (fusion, voir ci-dessous),
`docs/DEVIATIONS.md` (+ C-BAF-synthetic).

Non commités : `data/raw/baf/` (gitigné par `data/raw/`).

---

### Contraintes techniques

- **Environnement** : `.venv` activé pour tout (build, tests, `make check`).
- **Import lazy** : `kaggle` importé uniquement dans `_download_baf()` ;
  `make check` (pyflakes + pytest) ne doit pas échouer si kaggle absent.
- **Version épinglée** : `kaggle==1.6.17` (ou dernière version stable) dans
  `requirements.txt`, comme les autres dépendances.
- **Taille du parquet < 50 Mo** (bloquant pour le push) :
  - Compression **`zstd`** (pas snappy) dès le départ.
  - Colonnes catégorielles encodées en **int16** après mapping (pas float64).
  - Colonnes booléennes : standardisées en float64 (inchangé, 5 colonnes seulement).
  - Vérifier la taille après écriture ; si > 50 Mo, investiguer avant de continuer.
- **Reproductibilité** : pyarrow épinglé, codec fixé (zstd), pas de timestamp embarqué.
  SHA-256 de `preproc.json` stable entre deux builds.
- **Manifeste** (`data/derived/MANIFEST.json`) : **fusionner** avec le manifeste existant.
  Ne pas écraser les entrées `d1_etf4`, `d2_us97`, `d3_239`, `d3_500` ni les champs
  `generator` et `source`. Ajouter `d7_baf` dans `datasets` avec `inputs` (chemin
  `data/raw/baf/Base.csv`, sha256, rows=1000000) et `outputs` (base.parquet,
  splits.yaml, preproc.json avec sha256). Ajouter une section `results` avec
  `baf_profile` et une section `sources` avec les métadonnées Kaggle si elles
  n'existent pas déjà.
- **Pas de NaN** dans le parquet prétraité.
- **Aucun paramètre de prétraitement estimé hors des mois 0–2.**
- **Données brutes non commitées** (vérifier `git status` avant commit).
- Threads : `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`,
  `MKL_CBWR=COMPATIBLE` avant `import numpy` (pattern `sp500.py`).

---

### Tests (`tests/test_data_baf.py`)

Skippés si `base.parquet` absent (fixture sur le fichier).

1. **Forme** : 1 000 000 lignes, 32 colonnes, index 0..999999.
2. **Mois** : `month` ∈ {0,…,7}, 8 mois présents.
3. **Fraude** : `fraud_bool` ∈ {0, 1} ; taux global ~1 %.
4. **Pas de NaN** dans le parquet prétraité.
5. **Splits** : `load_splits()` retourne fit/calib/monitor avec les bons mois.
6. **Reproductibilité** : SHA-256 de `preproc.json` stable (rebuild → même hash).
7. **Contrat loader** : `load_baf()` retourne DataFrame 1M×32, dtypes corrects.
8. **Prétraitement figé** : sur les mois fit, moyennes ≈ 0 et écart-types ≈ 1 pour les
   25 numériques (vérifié sur le parquet prétraité).
9. **Catégoriels** : codes dans {−1, 0, …, |vocab|−1} ; mois 0–2 sans −1.
10. **Sentinelles** : les colonnes listées dans `preproc.json["sentinels"]["columns"]`
    sont bien des colonnes numériques ; après standardisation, les anciennes valeurs −1
    ne sont plus identifiables comme telles (vérifier que la distribution ne montre pas
    de pic anormal à une valeur entière).
11. **Manifeste** : SHA-256 des fichiers D7 correspondent au disque ; les entrées
    D1/D2/D3 sont préservées (non-régression).
12. **Profil CSV** : existe, 8 lignes, 28 colonnes ; `fraud_rate` cohérent avec le parquet ;
    `mean_<feature>` calculés sur données brutes (vérifier une valeur de référence :
    moyenne de `income` sur le mois 0, arrondie).
13. **Taille parquet** : `base.parquet` < 50 Mo.

---

### Critères de succès

- [ ] 1 000 000 lignes, 32 colonnes, 8 mois (`month` ∈ {0,…,7})
- [ ] `base.parquet` < 50 Mo (compression zstd)
- [ ] Tests au vert (`pytest -q tests/test_data_baf.py`)
- [ ] Prétraitement reproductible au SHA-256 près (`preproc.json` stable)
- [ ] `make check` vert (non-régression)
- [ ] Écart `C-BAF-synthetic` consigné dans `docs/DEVIATIONS.md`
- [ ] `docs/sections/data_baf.md` rédigé (avec licence)
- [ ] Manifeste fusionné sans perte des entrées existantes
- [ ] Aucun fichier > 50 Mo dans le range pushé ; `data/raw/baf/` non tracké

---

### Commandes de vérification

```bash
# Build (venv activé, ~/.kaggle/kaggle.json requis)
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

---

### Protocole de fin de stream

1. Wrapup enregistré dans `prompts/wrapups/wrapup-09.md`
2. `tools/reindex_graphify_jcodemunch.sh`
3. `make check` puis commit (Conventional Commits, sans trailer Co-authored-by)
4. `git push origin <branche>` — après vérification du range (aucun chemin sous
   `data/raw/eurofidai/`, `data/derived/d4_eurofidai/` ou `data/raw/baf/`,
   aucun fichier > 50 Mo)
