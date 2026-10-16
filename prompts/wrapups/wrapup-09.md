# Wrapup — Stream 09 : BAF (Bank Account Fraud, variante Base)

Date : 2026-10-16. Stream 09 terminé avec succès.

## Résumé

Construction du jeu D7 (BAF — Bank Account Fraud, Jesus et al., NeurIPS 2022) : téléchargement
Kaggle, contrôles, conversion, prétraitement figé, découpage, chargeur, tests, profil et
documentation.

## Livrables

| Fichier | Statut |
|---|---|
| `jepadrift/data_loader/baf.py` | Créé — chargeur + builder (CLI `--build`, `--refresh`) |
| `tests/test_data_baf.py` | Créé — 13 tests de contrat, tous au vert |
| `data/derived/d7_baf/base.parquet` | Créé — 1M×32, zstd, 38.1 Mo (< 50 Mo) |
| `data/derived/d7_baf/splits.yaml` | Créé — fit mois 0–2, calib 3, monitor 4–7 |
| `data/derived/d7_baf/preproc.json` | Créé — paramètres figés sur mois 0–2 |
| `results/data/baf_profile.csv` | Créé — 8 lignes × 28 colonnes (données brutes) |
| `logs/data/baf_build.log` | Créé — journal de build |
| `docs/sections/data_baf.md` | Créé — documentation complète (schéma, licence CC BY 4.0, sentinelles) |
| `prompts/plans/plan-09.md` | Créé — plan d'implémentation (mis à jour avec GO) |
| `prompts/GO-stream-09.md` | Livré par le chercheur |
| `requirements.txt` | Modifié — + `kaggle==1.6.17` (épinglé) |
| `requirements.lock` | Modifié — + kaggle 1.6.17 et deps transitives |
| `data/derived/MANIFEST.json` | Modifié — + entrées D7 (fusion, 36 insertions, 0 suppressions) |
| `docs/DEVIATIONS.md` | Modifié — + `C-BAF-synthetic` |

## Contrôles effectués

- 6 variantes présentes (`Base.csv` à `Variant V.csv`), 1 000 000 lignes chacune (vérifié par `wc -l`).
- 32 colonnes : noms validés strictement (erreur si écart).
- Schéma : 20 numériques continus, 5 booléennes (valeurs {0,1} validées), 5 catégorielles
  (cardinalité ≤ 7, warning si > 50).
- `month` ∈ {0,…,7}, 8 mois présents.
- Licence : CC BY 4.0.
- Prévalence de fraude par mois : de 0.87 % (mois 2) à 1.47 % (mois 7).

## Prétraitement (figé sur mois 0–2)

- **Standardisation z-score** : 25 colonnes numériques (20 continues float32 + 5 booléennes
  float64). `mean`/`std` calculés sur mois 0–2 uniquement. `std=0` → 1 (colonne constante).
- **Encodage catégoriel** : 5 colonnes, vocabulaire sur mois 0–2, inconnues → −1 (int16).
- **Sentinelles −1** : détectées automatiquement dans 6 colonnes (`prev_address_months_count`,
  `current_address_months_count`, `credit_risk_score`, `bank_months_count`,
  `session_length_in_minutes`, `device_distinct_emails_8w`). Standardisées comme les autres
  valeurs. Après z-score, elles ne sont plus égales à −1.
- **Colonne constante** : `device_fraud_count` = 0 partout (std=0 brut → remplacé par 1).

## Particularités découvertes

- `device_fraud_count` : constant à 0 sur tout le jeu (std=0).
- `prev_address_months_count` : 71 % de sentinelles −1 sur les mois fit — pic attendu et
  correct après standardisation.
- Authentification Kaggle : le fichier `~/.kaggle/access_token` (format `KGAT_…`) fonctionne
  avec le package kaggle 1.6.17 via Basic Auth (username vide). Un `kaggle.json` a été créé
  à partir du token pour compatibilité.

## Tests

13 tests, tous au vert :

1. Forme (1M×32, index 0..999999)
2. Mois (0–7, 8 présents)
3. Fraude (booléen, taux ~1.1 %)
4. Pas de NaN
5. Splits (fit/calib/monitor)
6. Reproductibilité (SHA-256 preproc.json)
7. Contrat loader (dtypes: float32/float64/int16/int8)
8. Prétraitement figé (moyennes ~0, écart-types ~1 sur fit)
9. Catégoriels (codes valides, pas de −1 en fit)
10. Sentinelles (colonnes documentées, pas de NaN)
11. Manifeste (SHA-256 + préservation D1/D2/D3)
12. Profil CSV (8×28, cohérence fraude)
13. Taille parquet (< 50 Mo)

## Métriques

| Métrique | Valeur |
|---|---|
| Lignes | 1 000 000 |
| Colonnes | 32 |
| Mois | 8 (0–7) |
| Taux de fraude global | 1.10 % |
| Taille parquet | 38.1 Mo (zstd niveau 19) |
| SHA-256 Base.csv | `7bf10a37ce07e72e14c1b09e5efee3d27261baff4facc7da767b0474dcf9b809` |
| SHA-256 base.parquet | `c8dd174a281694a9…` |
| SHA-256 preproc.json | `1fbd71a759e74ff3…` |
| Tests D7 | 13/13 pass |
| Tests globaux | 164 pass, 1 pré-existant fail, 3 skip |

## Écarts consignés

- **C-BAF-synthetic** : dérive native d'un jeu synthétique, jamais « in-the-wild ».

## Commandes de vérification

```bash
python -m jepadrift.data_loader.baf --build
pytest -q tests/test_data_baf.py -v
make check
python -c "import pandas as pd; d=pd.read_parquet('data/derived/d7_baf/base.parquet'); print(d.shape, d.month.value_counts().sort_index().to_dict())"
```

## Prochaines étapes

- Stream 15 (T-JEPA pour BAF) : utilisera D7 comme domaine tabulaire.
- Stream 24 (E9) : expérience sur BAF avec dérive native.
