# Wrapup — Stream 10 : EUROFIDAI (D4) — spécification, extraction réelle, ingestion et build

Date : 2026-10-16 (phase 1), 2026-10-17 (phase 2). Agent : Mistral Vibe (Large-4).

## Objectif

Intégrer le jeu D4 (actions européennes, EUROFIDAI, données propriétaires) :
**phase 1** — spécification d'extraction pour le portail, chargeur `jepadrift/data_loader/eurofidai.py`,
schéma YAML, manifeste versionné, fixtures synthétiques et tests de contrat ;
**phase 2** — extraction réelle sur le portail EUROFIDAI par le chercheur, traitement
des données brutes, ajustement du schéma et build du panel D4.

## Phase 1 — Spécification, chargeur, fixtures (2026-10-16)

### Livrables

| Fichier | Statut |
|---|---|
| `prompts/plans/plan-10.md` | Plan enregistré avant exécution |
| `docs/sections/eurofidai_extraction_spec.md` | Spécification d'extraction portail EUROFIDAI |
| `configs/eurofidai_schema.yaml` | Schéma de correspondance champs (placeholders, ajusté en phase 2) |
| `jepadrift/data_loader/eurofidai.py` | Chargeur D4 (lecture CSV, rendements log, in_universe PIT, liquidité, caractéristiques D3) |
| `docs/manifests/d4_manifest.json` | Manifeste (vide en phase 1, rempli en phase 2) |
| `tests/fixtures/eurofidai_fake/eur_2020.csv` | Fixture : 3 titres, radiation mid-period |
| `tests/fixtures/eurofidai_fake/eur_2021.csv` | Fixture : 2 titres, jour sans échange (NaN close) |
| `tests/fixtures/eurofidai_fake/uk_2020.csv` | Fixture : 2 titres, split (ajustement) |
| `tests/fixtures/eurofidai_fake/schema.yaml` | Schéma de test |
| `tests/test_data_eurofidai.py` | 22 tests (19 fixture + 3 real-data) |

### Tests phase 1 (fixtures, pas de données réelles)

```
pytest -q tests/test_data_eurofidai.py -v
→ 19 passed, 3 skipped in 0.44s
```

Tests couverts : schéma YAML, lecture fichiers raw, rendements log, ajustement split,
radiation, filtre de liquidité, non-anticipation des caractéristiques, intégration
fixture end-to-end, contrat loader / panel layout / splits (skippés), manifeste,
`.gitignore`.

## Phase 2 — Extraction réelle et build D4 (2026-10-17)

### 2.1 Extraction portail EUROFIDAI

- **Dataset** : Stocks (Daily Database)
- **Codes** : 500 codes EUROFIDAI sélectionnés (zone euro + UK, 6 places principales,
  ≥ 5 000 observations chacun) — `data/raw/eurofidai/_meta/eurofidai_codes_d4_500.txt`
- **Période** : 2001-01-01 → 2026-10-16
- **Variables** : Adjusted return, Closing Price, Adjustment Coefficient,
  Trading Volume (shares + value), Market Capitalization, Best Ask
- **Fichier reçu** : `stocks_results_20261017_1901_eurofidai_codes.csv` (366 Mo, 3 009 997 lignes)

### 2.2 Traitement des données brutes

| Aspect | Valeur |
|---|---|
| Séparateur | `|` (pipe) → converti en `,` |
| Encodage | UTF-8 avec BOM |
| Lignes | 3 009 997 |
| Codes uniques | 500 |
| Colonnes | 15 (security_name, eurofidai_code, quotation_date, adjusted_return, closing_price, adjust_coef, trading_volume_shares, capitalization, ...) |

**Colonnes manquantes** (non fournies par le portail) : place de cotation et ISIN
→ ajoutés par jointure avec les métadonnées ; date de radiation et statut → non
disponibles (radiations détectées indirectement via absence de données).

**Reconstruction du prix ajusté** : `adjust_coef` n'est renseigné que pour
1 356 lignes (0,04 %, jours de split). `adjusted_close` reconstruit depuis
`adjusted_return` par cumul intra-titre :
`adjusted_close[t] = adjusted_close[t-1] × (1 + adjusted_return[t])`.
Vérification : différence < 1e-6 dans 100 % des cas (moyenne 8,8e-17, epsilon machine).

### 2.3 Découpage

Fichier bloc découpé en **153 fichiers** `<MARCHE>_<ANNEE>.csv` :

| Marché | Code | Fichiers | Lignes |
|---|---|---|---|
| Euronext Paris | EPA | 26 | 1 080 330 |
| LSE SETS | LSE | 26 | 858 558 |
| Xetra | XET | 26 | 479 173 |
| Euronext Amsterdam | AMS | 26 | 297 298 |
| Euronext Bruxelles | BRU | 26 | 209 775 |
| Borsa Italiana | MIL | 23 | 84 863 |

### 2.4 Ajustement du schéma

`configs/eurofidai_schema.yaml` mis à jour avec les vrais noms de colonnes :
`eurofidai_code`, `isin_code`, `stock_exchange_name`, `quotation_date`,
`adjusted_close`, `adjust_coef`, `adjusted_return`, `capitalization`.

### 2.5 Build D4

```bash
python -m jepadrift.data_loader.eurofidai --build
```

| Métrique | Valeur |
|---|---|
| Actifs | **498** (sur 500 codes — 2 sans données dans la période) |
| Jours de trading | **6 541** (2001-01-02 → 2026-06-30) |
| Lignes panel | 3 257 418 |
| `in_universe` | 91,0 % des cellules |
| Flags (|ret| > 0,5) | 931 |
| Marchés | AMS, BRU, EPA, LSE, MIL, XET |

**Splits** (embargo 65 jours) :

| Segment | Début | Fin |
|---|---|---|
| pretrain | 2005-01-03 | 2015-12-31 |
| calib | 2016-04-06 | 2019-12-31 |
| monitor | 2020-04-02 | 2026-06-30 |

**Artefacts générés** (`data/derived/d4_eurofidai/`, 89 Mo total, gitigné) :

| Fichier | Taille |
|---|---|
| panel.parquet | 45 Mo |
| ret_wide.npy | 25 Mo |
| chars.parquet | 20 Mo |
| flags.csv | 53 Ko |
| dates.npy | 52 Ko |
| assets.json | 8,3 Ko |
| splits.yaml | 620 o |

### 2.6 Tests phase 2 (données réelles)

```
pytest -q tests/test_data_eurofidai.py -v
→ 22 passed in 0.62s  (avant : 19 passed, 3 skipped)
```

Les 3 tests précédemment skippés (panel layout, splits, contrat loader) passent
maintenant avec les données réelles.

## Vérifications globales

```bash
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
→ .gitignore:3:data/derived/d4_eurofidai/  data/derived/d4_eurofidai/x
→ .gitignore:2:data/raw/  data/raw/eurofidai/x
```

| Vérification | Statut |
|---|---|
| Pyflakes | 0 erreur |
| Tests D4 | 22/22 passed |
| Tests complets | 184 passed, 1 skipped, 1 failed (pré-existant D3, epsilon machine) |
| Garde-fous git | `data/raw/eurofidai/` et `data/derived/d4_eurofidai/` gitignés |
| Aucune donnée EUROFIDAI trackée | Confirmé (`git status` clean) |
| Fichiers dérivés < 50 Mo | Confirmé (max 45 Mo) |
| Manifeste | Rempli (153 fichiers sources, 7 outputs, SHA-256, 498 actifs) |

Le failure `test_reconstruction_from_cache` (D3) est pré-existant : différence flottante
max 1.1e-16 (epsilon machine), non lié à ce stream.

## Aucune donnée EUROFIDAI commitées

- Aucun fichier sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` n'est commité
- Le manifeste ne contient que des empreintes SHA-256, effectifs et dates
- Les fixtures sont synthétiques (`tests/fixtures/eurofidai_fake/`)

## Fichiers modifiés (phase 2)

| Fichier | Modification |
|---|---|
| `configs/eurofidai_schema.yaml` | Noms de colonnes réels du portail EUROFIDAI |
| `docs/manifests/d4_manifest.json` | Rempli (SHA-256, effectifs, dates, 498 actifs) |
| `data/raw/eurofidai/` | 153 CSV découpés + `_meta/` (codes, métadonnées) — gitigné |
| `data/derived/d4_eurofidai/` | 7 artefacts dérivés (89 Mo) — gitigné |

## Points d'attention

1. **2 codes sans données** : 500 codes sélectionnés, 498 actifs dans le panel.
   À investiguer (radiés avant 2001 ? données manquantes ?).
2. **Prix ajusté reconstruit** : validé à l'epsilon machine, mais le niveau absolu
   dépend du prix de départ. Sans impact sur les rendements log.
3. **Radiations non explicites** : pas de colonne `delisting_date`. Détection indirecte
   via absence de données → `close_valid` False → `in_universe` False. Fonctionnel.
4. **Test D3 pré-existant** : `test_reconstruction_from_cache` (epsilon machine).
   À corriger séparément.
5. **MIL (Borsa Italiana)** : 23 fichiers (2001-2023) contre 26 pour les autres
   marchés. Années 2024-2026 manquantes — à vérifier.

## Prochaines étapes

1. **Stream 11+** : utiliser D4 dans les expériences E4 (P3-KF, P3-C, P3-D)
   avec symétrisation D6.
2. **Corriger le test D3** : `test_reconstruction_from_cache` (epsilon machine).
3. **Investiguer les 2 codes manquants** et les années MIL manquantes.
4. **Éventuellement** : extraction complémentaire des métadonnées de référence
   (Reference Data) pour obtenir ISIN, statut, dates de radiation explicites.
