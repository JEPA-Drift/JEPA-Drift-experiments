# Stream 14 — plan GO-B2 (révision 6, mode plan ; aucune implémentation accordée)

## Contexte
GO-B s'est arrêté à la porte du lecteur pretrain réel. `ret_wide.npy` est en ordre Fortran (npy 1.0, float64,
(6738, 239), SHA-256 `a266fbab…`), et non en ordre C comme l'affirmait à tort la révision 5. État conservé :
- C2 `7fbd43f` et fusion locale `93370e4` commités ;
- six fichiers GO-B non commités : `configs/ca_tjepa.yaml`, `experiments/jepa_pretrain.py`, `jepadrift/jepa/ca_tjepa.py`,
  `jepadrift/representations/extract.py`, `tests/test_ca_tjepa.py`, `tests/test_contracts.py` (+380/−71) ;
- trace de l'arrêt : `external/torch-cf-logs/goB_stop.txt`.

GO-B2 retient l'option A et corrige trois constats d'audit bloquants. GO-A et GO-B restent inchangés. Toute édition
passera par l'outil natif `Edit`, l'équivalent `apply_patch` de ce harnais ; aucun script shell ni Python n'édite de
fichier.

## Portes d'intégrité des données (audit indépendant, lecture seule)
- 2 769 dates pretrain (2005-01-03 → 2015-12-31) et 239 actifs.
- 661 791 clés uniques date × actif dans chacun des deux fichiers Parquet, sans clé manquante ni en trop.
- Aucun NaN ni infini dans les rendements ; `panel.ret` = `ret_wide.npy` à l'octet sur la grille pretrain.
- SHA-256, en ordre C, du tableau pretrain des rendements : `3115d872421e2df0dc6d58d9093e4a8703b5b314cfcb4c9f1333f54e086c4830`.
- C : 8 NaN, tous sur `c_beta_252` (`C-D3-beta-denominator`, compte pretrain de 17), aucun infini.

Ces valeurs deviennent des portes de test. Aucun fichier source D3 n'est réécrit.

## Différences de fichiers (minimales, par rapport à l'état non commité)
1. **`experiments/jepa_pretrain.py`**
   - Supprimer `_npy_rows`.
   - `load_pretrain` lit `ret` et `in_universe` dans `panel.parquet`, et C dans `chars.parquet`, via `_parquet_rows`
     (inchangé : bornes de date par row group exigées, rejet d'un row group qui chevauche monitor, filtrage Arrow des
     lignes post-2016 avant pandas).
   - Le calendrier attendu vient de `dates.npy` (mmap + `searchsorted`), les actifs de `assets.json`.
   - Nouveau contrôle, avant tout `reindex` de chaque table :
     - aucune clé (date, asset_id) dupliquée ;
     - ensemble des clés = grille attendue exactement (comptes manquants et en trop rapportés) ;
     - aucun ±inf ;
     - `in_universe` sans valeur nulle ;
     - aucun `ret` NaN là où `in_universe` est vrai.
   - X = `where(U, ret, NaN)` ; NaN de C conservés.
   - Retourne `(X, C, dates, assets)`. `ret_wide.npy` n'est jamais ouvert.
   - `--data d3_239` passe `assets` à `train`.
2. **`jepadrift/jepa/ca_tjepa.py`**
   - `assets_digest(assets)` : SHA-256 de la liste ordonnée sérialisée en JSON compact.
   - `train(..., assets=None)` :
     - rejette ±inf dans X ou C avant tout masque ou imputation ;
     - exige `len(assets) == N` ;
     - inscrit `assets_sha256` (le condensat seul, ou `null` en synthétique) dans `config.json`, donc dans les
       empreintes publiées.
   - `extract_day` rejette ±inf dans C avant `impute_zero`. ±inf dans x est déjà rejeté par la base Z-1 de 17.
3. **`jepadrift/jepa/representation.py`**
   - `CATJEPA(ckpt, D=None, assets=None)` : si le checkpoint porte `assets_sha256`, il exige `assets` et un condensat
     identique dès la construction, donc avant `fit` et avant toute extraction. Sinon (synthétique), `assets` est
     facultatif.
   - `config` inclut `assets_sha256`.
4. **`jepadrift/representations/extract.py`**
   - `_ca_tjepa(ckpt, D=None, assets=None)`.
   - `main` reprend `ret, dates, assets = load()` et ajoute `kwargs["assets"] = list(assets)` quand la fabrique accepte
     `assets` (`inspect.signature`).
5. **`tests/test_ca_tjepa.py`** : voir « Tests ».
6. **`tests/test_contracts.py`** : garde de normalisation temporelle renforcée (voir « Tests »).
7. **Documentation**, comme prévu en GO-B, plus quatre points :
   - lecteur `panel.parquet` ;
   - découverte de l'ordre Fortran ;
   - liaison d'identité des actifs ;
   - limite : `fit(X, C, dates)` de Z-1 ne peut pas vérifier les étiquettes de colonnes de l'appelant, seule la liste
     d'actifs relayée par la CLI le peut.

   Fichiers : `docs/sections/{ca_tjepa,interface_Z,contracts}.md`, `docs/audits/ca_tjepa_leakage.md`,
   `docs/DEVIATIONS.md` (entrées EN, dont `C-jepa-d3-reader`), `CLAUDE.md` (ligne torch), `.gitignore` (`/ckpt`).

## Tests (RED avant GREEN)
- **Fixture D3 synthétique.**
  - `panel.parquet` reçoit `ret`.
  - `ret_wide.npy` est remplacé par des octets invalides : `np.load` échoue, mais `load_pretrain` réussit.
  - Les row groups monitor contiennent des +inf ; l'espion `read_row_group` voit seulement `[0, 0]`.
- **Contrôles négatifs du lecteur** : chacun doit lever `ValueError` avec un message précis.
  - Row group qui chevauche monitor ; absence de statistiques de date.
  - Clé manquante, dupliquée ou en trop.
  - +inf dans `ret`, −inf dans C, `ret` NaN avec `in_universe` vrai, `in_universe` nul.
- **Témoin calib conservé** : perturber `ret`, `in_universe` et C sur les lignes calib du row group 0 laisse
  identiques les tableaux pretrain et le hash du checkpoint.
- **Données réelles** (lecture < 2016 seulement) :
  - les portes d'intégrité ci-dessus ;
  - l'espion voit `[0, 0]` ;
  - égalité avec `test_contracts.d3_char_data()["pretrain"]` ;
  - fenêtre de smoke = 200 lignes, dont 100 d'estimation et 35 de validation.
- **No-leak sur jours réels**, paramétré par `group` et `random`.
- **Infinis** : `train` rejette +inf dans X et −inf dans C ; l'extraction rejette ±inf dans x et dans C. NaN dans C
  reste imputé et compté.
- **Identité des actifs** : checkpoint entraîné avec 239 identifiants (`A000…A238`, données synthétiques).
  - Sans `assets` : rejet.
  - Permutation des 239 identifiants (même effectif) : rejet.
  - Bonne liste : accepté.
  - Le checkpoint synthétique sans identité reste utilisable.
  - `config.json` et l'empreinte publiée ne contiennent aucun identifiant, seulement le condensat.
- **Registre et CLI**, en remplaçant par `monkeypatch` les chargeurs `extract.DATASETS["d3_239"]` et `extract.chars`
  par des lignes synthétiques < 2020 (aucune ligne réelle ≥ 2020 n'est lue en test) :
  - `REGISTRY["ca_tjepa"](ckpt, D=mauvais)` lève une erreur ;
  - sans `--ckpt` : `SystemExit 2` ;
  - `--D` incohérent : rejet ;
  - liste d'actifs permutée par le chargeur : rejet ;
  - deux extractions CLI identiques à l'octet ;
  - fichiers du checkpoint inchangés (extraction figée).
- **`test_contracts.py`** : garde de normalisation temporelle sur les jours {0, 7, 19}, avec z_odd **et** z_even
  inchangés quand les autres jours changent et égaux à `transform_day` ; le témoin `Centred` doit échouer.
- **Supprimés** : les cas d'en-tête `.npy` (float32, Fortran, 3-D, préfixe tronqué) et `_npy_rows`.

## Ordre et portes
1. Consigner GO-B2 (verbatim, nouveau fichier `prompts/GO-stream-14-B2.md`) et la « Décision GO-B2 intégrée » dans
   `plan-14.md`. Reconnecter et appeler graphify et jcodemunch.
2. Tests RED, puis code, puis GREEN sous `.venv` + shim. Suites : `test_ca_tjepa`, `test_contracts`, `test_decoupling`,
   `test_representations`, `test_chars`.
3. Portes GO-B inchangées :
   - D2/PCA (4 fichiers identiques à l'octet) ;
   - smokes réels d ∈ {2, 4, 8, 16} avec empreintes, et d = 8 deux fois → même hash ;
   - deux extractions CLI réelles complètes vers un répertoire temporaire, `cmp`, avec le checkpoint smoke d = 8 et
     la liste d'actifs relayée (Q1, aucune statistique sur monitor) ;
   - `make check` ≤ 300 s ;
   - J1 (3 sorties restaurées depuis l'instantané).
4. Documentation, wrapup, puis commit local C3 (chemins explicites, sans trailer, sans `--no-verify`, shim exporté
   pour le hook). Pas de fetch, push ni `.pth` tant qu'un autre stream utilise `.venv`.

## STOP
- Une porte d'intégrité diffère (2 769 dates, 239 actifs, 661 791 clés par fichier, SHA `3115d872…`, 8 NaN de C,
  aucun ±inf).
- `ret_wide.npy` ou un row group monitor est ouvert par le lecteur.
- Échec d'un test d'identité, d'infini, de couverture, de fuite ou de garde, ou témoin non détecté.
- Écart D2/PCA ou J1.
- `make check` au-delà de 300 s ou smoke au-delà de 10 min.
- 3 échecs de remédiation.

Aucun paramètre n'est réglé pour forcer un passage. Aucune revendication scientifique. P4-D et P5-D restent exclus des
comparaisons calibrées.
