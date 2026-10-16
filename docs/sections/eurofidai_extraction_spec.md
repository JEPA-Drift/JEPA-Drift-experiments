# EUROFIDAI (D4) — Spécification d'extraction

Document à exécuter manuellement par le chercheur sur le portail EUROFIDAI.
L'agent n'a pas d'accès au portail ; aucune requête automatisée n'est autorisée.

## 1. Périmètre

| Paramètre | Valeur |
|---|---|
| Fournisseur | EUROFIDAI (données propriétaires) |
| Marchés | Zone euro (17 pays) + Royaume-Uni |
| Période | 2000-01-01 → dernière date disponible |
| Fréquence | Quotidienne (jours de bourse) |
| Univers | Constituants point-in-time, jusqu'à ~1000 titres |
| Titres radiés | Inclus (pas de biais de survie) |

## 2. Champs requis

| # | Champ | Description | Format |
|---|---|---|---|
| 1 | Identifiant stable | Identifiant interne EUROFIDAI pérenne (ne change pas lors d'un changement de ticker) | entier ou chaîne |
| 2 | ISIN | Code ISIN international | chaîne 12 caractères |
| 3 | Marché | Place de cotation (ex: EPA, ETR, LSE) | chaîne |
| 4 | Date | Date de cotation | AAAA-MM-JJ |
| 5 | Cours ajusté | Cours de clôture ajusté des splits et dividendes | nombre |
| 6 | Facteur d'ajustement | Facteur multiplicatif cumulé (si le portail fournit ce champ plutôt que le cours ajusté) | nombre |
| 7 | Rendement total | Rendement total (prix + dividendes réinvestis) si disponible | nombre |
| 8 | Capitalisation | Capitalisation boursière en devise locale | nombre |
| 9 | Statut de cotation | Code statut : coté, suspendu, radié | chaîne |
| 10 | Date de radiation | Date de radiation de la cote (si applicable) | AAAA-MM-JJ ou vide |
| 11 | Appartenance aux indices | Indices auxquels le titre appartient (si disponible) | chaîne |

## 3. Format de sortie

- **Format** : CSV (séparateur virgule, encodage UTF-8)
- **Organisation** : un fichier par marché et par année
- **Nommage** : `<marché>_<année>.csv` (ex: `EPA_2020.csv`, `ETR_2020.csv`, `LSE_2020.csv`)
- **En-tête** : première ligne = noms de colonnes (voir section 2)
- **Séparateur décimal** : point
- **Dates** : format ISO 8601 (AAAA-MM-JJ)

## 4. Dépôt

Les fichiers CSV sont déposés dans :

```
data/raw/eurofidai/
```

Ce répertoire est gitignoré (`data/raw/` dans `.gitignore`). Les données ne quittent
jamais la machine du chercheur.

## 5. Procédure d'extraction (portail EUROFIDAI)

1. Se connecter au portail EUROFIDAI (https://www.eurofidai.org)
2. Naviguer vers la section « Data » ou « Export »
3. Sélectionner les marchés : tous les marchés de la zone euro + Royaume-Uni
4. Sélectionner la période : 2000-01-01 → date courante
5. Sélectionner la fréquence : quotidienne
6. Sélectionner les champs listés en section 2 (cocher « titres radiés inclus » si l'option existe)
7. Choisir le format CSV
8. Lancer l'export par marché et par année (ou exporter en bloc si le portail le permet,
   puis découper en fichiers annuels avec le script fourni ci-dessous)
9. Déposer les fichiers dans `data/raw/eurofidai/`

### Script de découpage (si export en bloc)

```bash
# Après dépôt du fichier bloc dans data/raw/eurofidai/
/home/m53/miniforge3/envs/Trading/bin/python -c "
import pandas as pd
from pathlib import Path

raw = Path('data/raw/eurofidai')
df = pd.read_csv(raw / 'export_block.csv', float_precision='round_trip')
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['market'] = df['market'].astype(str)
for (mkt, yr), grp in df.groupby(['market', 'year']):
    out = raw / f'{mkt}_{yr}.csv'
    grp.drop(columns=['year']).to_csv(out, index=False)
    print(f'{out}: {len(grp)} rows')
"
```

## 6. Vérification post-extraction

Après extraction, vérifier :

```bash
# Lister les fichiers extraits
ls -la data/raw/eurofidai/

# Compter les lignes par fichier
wc -l data/raw/eurofidai/*.csv

# Vérifier le gitignore
git check-ignore -v data/raw/eurofidai/x
# Doit afficher : .gitignore:2:data/raw/  data/raw/eurofidai/x
```

## 7. Ingestion

Une fois les fichiers déposés, lancer l'ingestion :

```bash
python -m jepadrift.data_loader.eurofidai --build
```

Le chargeur lit les CSV, applique le schéma `configs/eurofidai_schema.yaml`, calcule
les rendements log, détermine `in_universe` point-in-time, applique le filtre de
liquidité, calcule les caractéristiques (mêmes définitions que D3) et écrit les
artefacts dérivés dans `data/derived/d4_eurofidai/`.

## 8. Garde-fous

- **Aucune donnée EUROFIDAI** dans git, dans les journaux ou dans les CSV de `results/`
  (seulement des agrégats : effectifs, dates, empreintes SHA-256)
- **Aucune requête automatisée** vers le portail EUROFIDAI
- `data/raw/eurofidai/` et `data/derived/d4_eurofidai/` sont gitignorés et bloqués
  par le hook pre-commit (stream 8)
- Le manifeste `docs/manifests/d4_manifest.json` ne contient que des empreintes,
  effectifs et dates — aucune donnée de marché
