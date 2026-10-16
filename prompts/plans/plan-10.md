# Plan — Stream 10 : EUROFIDAI (D4) — spécification d'extraction, ingestion locale et garde-fous

Date : 2026-10-16. Statut : **GO** (directive `/plan` invoquée par le chercheur).

## 1. Résumé

Préparer l'intégration du jeu D4 (actions européennes, EUROFIDAI, données propriétaires) :
spécification d'extraction pour le portail (à exécuter manuellement par le chercheur), chargeur
`jepadrift/data_loader/eurofidai.py` réutilisant la logique de caractéristiques de D3, schéma
YAML modifiable, manifeste versionné vide, fixtures synthétiques et tests de contrat. Aucune
donnée EUROFIDAI n'est téléchargée, commitées ou loguée — seuls les scripts et le manifeste
d'empreintes sont versionnés.

## 2. Décisions d'architecture clés

| Question | Décision | Justification |
|---|---|---|
| Extraction | Spécification textuelle (`docs/sections/eurofidai_extraction_spec.md`) exécutée manuellement par le chercheur sur le portail EUROFIDAI | L'agent n'a pas d'accès au portail ; aucune requête automatisée autorisée |
| Schéma CSV | Table de correspondance dans `configs/eurofidai_schema.yaml` (modifiable) | Les noms de champs EUROFIDAI peuvent différer ; le chercheur ajuste sans toucher au code |
| Rendements | Log-rendements depuis les cours ajustés, sans remplissage (forward-fill interdit) | Cohérence D3 (`sp500.py`) |
| `in_universe` | Point-in-time : un titre est dans l'univers à t ssi coté, non radié, et liquide ce jour | Cohérence D3 + filtre de liquidité documenté |
| Filtre de liquidité | Exclusion des jours sans échange (volume nul ou absent) ; seuil documenté dans le chargeur | Évite les faux signaux de rendement nul |
| Caractéristiques | Réutilisation directe de `sp500._compute_chars` (mêmes définitions beta_252, vol_63, mom_12_1, rev_21) | Le prompt exige la même définition que D3 ; pas de duplication de code |
| GICS secteurs | Non disponibles dans EUROFIDAI standard → les colonnes `c_gics_*` sont omises ou remplacées par une table de secteurs externe si fournie | EUROFIDAI fournit typiquement le secteur mais pas le mapping GICS ; le schéma YAML permet d'ajouter un mapping |
| Sortie | `data/derived/d4_eurofidai/` au format D3 : `panel.parquet`, `ret_wide.npy`, `dates.npy`, `assets.json`, `chars.parquet`, `splits.yaml`, `flags.csv` | Cohérence inter-jeux |
| Manifeste | `docs/manifests/d4_manifest.json` — empreintes SHA-256, effectifs, dates, sans aucune donnée | Versionné, traçable, sans fuite de données propriétaires |
| Tests | Fixtures synthétiques dans `tests/fixtures/eurofidai_fake/` ; tests réels skippés si `data/raw/eurofidai/` vide | Tests de contrat exécutables sans données réelles |
| Garde-fous git | `.gitignore` bloque déjà `data/raw/` et `data/derived/d4_eurofidai/` ; le hook pre-commit de stream 8 (à venir) bloquera explicitement | Vérifié dans ce stream |

## 3. Plan détaillé

### Phase 1 — Spécification d'extraction (`docs/sections/eurofidai_extraction_spec.md`)

Document à exécuter manuellement par le chercheur sur le portail EUROFIDAI :
- Marchés : zone euro + Royaume-Uni
- Période : 2000-01-01 → dernière date disponible
- Fréquence : quotidienne
- Champs : identifiant stable, ISIN, marché, date, cours ajusté ou facteurs d'ajustement, rendement total si disponible, capitalisation, statut de cotation, dates de radiation (titres radiés inclus), appartenance aux indices si disponible
- Format : CSV, un fichier par marché et par année
- Dépôt : `data/raw/eurofidai/`

### Phase 2 — Schéma (`configs/eurofidai_schema.yaml`)

Table de correspondance nom de champ EUROFIDAI → nom interne :
```yaml
fields:
  id_stable: "id_eurofidai"
  isin: "isin"
  market: "market"
  date: "date"
  adjusted_close: "close_adj"
  adjustment_factor: "facteur_ajust"
  total_return: "rendement_total"
  market_cap: "capitalisation"
  listing_status: "statut_cotation"
  delisting_date: "date_radiation"
  index_membership: "indice_appartenance"
liquidity:
  min_volume: 0
  min_days_traded_21: 1
```

### Phase 3 — Chargeur (`jepadrift/data_loader/eurofidai.py`)

Structure miroir de `sp500.py` :
- Constantes de chemins : `RAW_D4 = data/raw/eurofidai/`, `DERIVED_D4 = data/derived/d4_eurofidai/`
- `_load_schema()` : lit `configs/eurofidai_schema.yaml`
- `_read_raw_files()` : lit les CSV exportés, mappe les champs via le schéma
- `_compute_returns()` : log-rendements depuis cours ajustés, sans remplissage
- `_compute_in_universe()` : point-in-time (coté + non radié + liquide)
- `_apply_liquidity_filter()` : filtre documenté (jours sans échange)
- `_compute_chars()` : délègue à `sp500._compute_chars` (mêmes définitions)
- `_write_panel()`, `_write_splits()`, `_write_flags()`, `_write_chars()` : writers D3-style
- `build()` : orchestre la lecture → rendements → univers → caractéristiques → écriture
- `load_d4()` : chargeur `(ret, dates, assets)`
- `load_chars_d4()`, `load_splits_d4()` : loaders
- `main()` : argparse avec `--build`

### Phase 4 — Manifeste (`docs/manifests/d4_manifest.json`)

Structure prête à remplir (vide au départ) :
```json
{
  "dataset": "d4_eurofidai",
  "source": "EUROFIDAI (proprietary)",
  "extraction_date": null,
  "markets": [],
  "files": [],
  "sha256": {},
  "n_assets": 0,
  "n_days": 0,
  "first_date": null,
  "last_date": null,
  "outputs": {}
}
```

### Phase 5 — Fixtures synthétiques (`tests/fixtures/eurofidai_fake/`)

Fichiers CSV imitant le format EUROFIDAI avec schéma connu :
- `eur_2020.csv` : 3 titres, 5 jours, avec un titre radié mid-period
- `eur_2021.csv` : 2 titres, 5 jours, avec un jour sans échange (volume nul)
- `uk_2020.csv` : 2 titres, 5 jours, avec ajustement (split)
- `schema.yaml` : schéma de test pointant vers les noms de colonnes des fixtures

### Phase 6 — Tests (`tests/test_data_eurofidai.py`)

Tests sur fixtures synthétiques (toujours exécutés) :
1. **Schéma** : le schéma YAML mappe correctement les champs
2. **Ajustements** : un split produit le bon rendement ajusté
3. **Radiations** : un titre radié sort de `in_universe` à la date de radiation
4. **Non-anticipation des caractéristiques** : perturber les rendements à partir de t laisse les caractéristiques jusqu'à t identiques
5. **Liquidité** : un jour sans échange est exclu de `in_universe`
6. **Contrat loader** : `load_d4()` retourne `(ret, dates, assets)` avec les bons dtypes

Tests réels (skippés si `data/raw/eurofidai/` vide) :
7. **Panel layout** : colonnes, dtypes, pas de NaN dans `ret` quand `in_universe`
8. **Splits** : embargo 65 jours, bornes nominales

### Phase 7 — Vérification des garde-fous

```bash
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
```

Vérifier que `.gitignore` bloque les deux chemins. Le hook pre-commit de stream 8 (à venir)
bloquera explicitement ces chemins.

## 4. Fichiers à créer

| Fichier | Description |
|---|---|
| `prompts/plans/plan-10.md` | Ce plan |
| `docs/sections/eurofidai_extraction_spec.md` | Spécification d'extraction portail |
| `configs/eurofidai_schema.yaml` | Schéma de correspondance champs |
| `jepadrift/data_loader/eurofidai.py` | Chargeur D4 |
| `docs/manifests/d4_manifest.json` | Manifeste vide (empreintes, sans données) |
| `tests/fixtures/eurofidai_fake/eur_2020.csv` | Fixture : 3 titres, radiation |
| `tests/fixtures/eurofidai_fake/eur_2021.csv` | Fixture : 2 titres, jour sans échange |
| `tests/fixtures/eurofidai_fake/uk_2020.csv` | Fixture : 2 titres, split |
| `tests/fixtures/eurofidai_fake/schema.yaml` | Schéma de test |
| `tests/test_data_eurofidai.py` | Tests de contrat D4 |
| `prompts/wrapups/wrapup-10.md` | Wrapup de fin de stream |

## 5. Commandes de vérification

```bash
pytest -q tests/test_data_eurofidai.py -v
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
make check
```

## 6. Critères de succès

- [ ] Tests sur fixtures au vert (`pytest -q tests/test_data_eurofidai.py`)
- [ ] `.gitignore` bloque `data/raw/eurofidai/` et `data/derived/d4_eurofidai/` (vérifié)
- [ ] Spécification exécutable telle quelle par le chercheur
- [ ] `make check` vert (non-régression)
- [ ] Aucune donnée EUROFIDAI dans git, journaux ou CSV de résultats

## 7. Risques et points de vigilance

| Risque | Mitigation |
|---|---|
| Noms de champs EUROFIDAI inconnus | Schéma YAML modifiable ; le chercheur ajuste sans toucher au code |
| Pas de secteur GICS dans EUROFIDAI | Colonnes `c_gics_*` optionnelles ; le schéma permet un mapping externe |
| Données propriétaires | Aucune donnée dans git ; manifeste d'empreintes uniquement |
| Stream 8 (hooks) pas encore fait | `.gitignore` couvre déjà ; le hook pre-commit viendra avec stream 8 |
