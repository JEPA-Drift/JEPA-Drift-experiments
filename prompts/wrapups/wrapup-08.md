# Wrap-up — Stream 08 : tests de contrat, règles de découplage et garde-fous

Date : 2026-10-17. Instance : Mistral Vibe. Base : `be7d938`.

## Objectif

Livrer quatre tests de contrat bloquant toute fusion de code entre représentation et surveillance,
les règles de découplage par analyse AST des imports, les garde-fous pour modèles torch (futur JEPA),
les hooks git pre-commit/pre-push, et l'extension de `make check`.

## Livrables

| Fichier | Description |
|---|---|
| `tests/test_contracts.py` | 20 tests de contrat paramétrés sur PCA (3 modes), DegreeZero (2 configs), CenteredRanks : non-anticipation (6), imparité (6), déterminisme subprocess (1), absence de stats test (3). + 4 tests torch guards (eval buffer stabilité, pas de BatchNorm en training, pas de normalisation temporelle, EMA inactive). |
| `tests/test_decoupling.py` | 6 tests de découplage par analyse AST : monitors n'importe ni torch ni jepa ni representations ; jepa n'importe ni injection ni monitors ; representations n'importe ni torch ni monitors ni injection ; injection accepte uniquement des panels de rendements (assertions shape/dtype, refus des objets Z). |
| `tools/pre-commit` | Hook pre-commit : lance `make check`, bloque `data/raw/eurofidai/` et `data/derived/d4_eurofidai/`, bloque fichiers > 50 Mo. |
| `tools/pre-push` | Hook pre-push : bloque tout push contenant un fichier eurofidai dans la plage, rappelle la règle de soumission anonyme. |
| `Makefile` | Cible `hooks` (installe les hooks git via symlinks), `check` étendu (pyflakes + contrats + découplage + tests unitaires). |
| `docs/sections/contracts.md` | Documentation des 4 contrats, règles de découplage, garde-fous torch, hooks git. |
| `prompts/plans/plan-08.md` | Plan d'exécution enregistré avant le premier changement de code. |

## Résultats des tests

- **26/26 tests stream 08 passent** (20 contrats + 6 découplage) en 3.2s.
- **182/183 tests totaux passent** (1 échec pré-existant `test_reconstruction_from_cache` : différence flottante 1e-16, non lié au stream 08).
- **4 tests skippés** : 3 dans les suites existantes (E2 hash pin, etc.), 0 dans stream 08 (torch 2.5.1 installé, tous les guards torch passent).
- **Hook pre-commit testé** : bloque `data/raw/eurofidai/t.csv` et `data/derived/d4_eurofidai/t.csv` avec exit 1.

## Vérifications effectuées

```bash
make hooks    # installe les symlinks .git/hooks/pre-commit et pre-push
make check    # pyflakes + 26 tests stream 08 + 156 tests unitaires
# Test manuel du hook :
mkdir -p data/raw/eurofidai && echo x > data/raw/eurofidai/t.csv
git add -f data/raw/eurofidai/t.csv
git commit -m test  # BLOCKED, exit 1
```

## Fichiers modifiés

- `Makefile` — ajout cible `hooks`, extension `check`
- `tests/test_contracts.py` — nouveau (20 contrats + 4 torch guards)
- `tests/test_decoupling.py` — nouveau (6 tests AST)
- `tools/pre-commit` — nouveau (hook git)
- `tools/pre-push` — nouveau (hook git)
- `docs/sections/contracts.md` — nouveau (documentation)
- `prompts/plans/plan-08.md` — nouveau (plan)

## Fichiers non stagés (pré-existants, non modifiés par ce stream)

- `data/derived/MANIFEST.json`, `data/derived/d1_etf4/panel.parquet`, `data/derived/d2_us97/panel.parquet`, `results/data/d1_d2_profile.csv` — modifiés par le fixture de `test_data_d1_d2.py` pendant `make check` (règle AGENTS.md : jamais stagés).
- `logs/d4/`, `prompts/plans/plan-11-vibe.md` — fichiers d'autres streams, non suivis.

## Prochaines étapes

- Stream 09 (déjà planifié) : će stream est terminé, le wrap-up est enregistré.
- Le futur JEPA (stream 11+) devra passer les 4 contrats + les 4 torch guards automatiquement.
