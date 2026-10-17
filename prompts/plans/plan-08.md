# Plan — Stream 08 : tests de contrat, règles de découplage et garde-fous

> Exécution : Mistral Vibe, en session unique. Date : 2026-10-17. Spécification : `prompts/streams/prompt-08-contracts.md`. Base : `be7d938` (HEAD main).

**Objectif.** Livrer quatre tests de contrat bloquant toute fusion de code entre représentation et surveillance, les règles de découplage par analyse AST des imports, les garde-fous pour modèles torch (futur JEPA), les hooks git pre-commit/pre-push, et l'extension de `make check`.

**Architecture.**

| Fichier | Rôle |
|---|---|
| `tests/test_contracts.py` | 4 contrats paramétrés sur PCA, DegreeZero, CenteredRanks : non-anticipation, imparité, déterminisme (sous-processus), absence de statistiques de test. + tests torch (skip si absent). |
| `tests/test_decoupling.py` | Analyse AST : monitors n'importe ni torch ni jepa ni representations ; jepa n'importe ni injection ni monitors ; injection refuse les objets Z. |
| `tools/pre-commit` | Lance `make check`, bloque `data/raw/eurofidai/` et `data/derived/d4_eurofidai/`, bloque fichiers > 50 Mo. |
| `tools/pre-push` | Bloque tout push dont la plage contient un fichier eurofidai, rappelle la règle de soumission anonyme. |
| `Makefile` | Cible `hooks` (installe les hooks git), `check` étendu (pyflakes + tous les tests). |
| `docs/sections/contracts.md` | Documentation des contrats et garde-fous. |

## Tâches

- [ ] **T0** — Enregistrer ce plan dans `prompts/plans/plan-08.md` (fait).
- [ ] **T1** — `tests/test_contracts.py` : contrat (1) non-anticipation, contrat (2) imparité, contrat (3) déterminisme subprocess, contrat (4) absence de stats test. Paramétré sur `extract.REGISTRY` (pca, degree0, ranks).
- [ ] **T2** — `tests/test_contracts.py` : fixture de représentation fautive (normalisation sur toute la série) qui échoue au contrat (4).
- [ ] **T3** — `tests/test_contracts.py` : tests torch (eval mode buffer stabilité, pas de BatchNorm en training, pas de normalisation temporelle, EMA inactive). Skip si torch absent.
- [ ] **T4** — `tests/test_decoupling.py` : AST import isolation (monitors, jepa, injection).
- [ ] **T5** — `tools/pre-commit` et `tools/pre-push` (scripts bash exécutables).
- [ ] **T6** — `Makefile` : cible `hooks`, extension de `check`.
- [ ] **T7** — `docs/sections/contracts.md`.
- [ ] **T8** — Vérification : `make hooks && make check`, test du hook pre-commit avec fichier factice eurofidai.
- [ ] **T9** — Wrap-up `prompts/wrapups/wrapup-08.md`, reindex, commit, push.

## Contraintes

- Tests rapides (< 2 min total), données réduites et déterministes.
- Aucune dépendance réseau.
- `jepadrift/monitors/` reste numpy-only.
- Les contrats s'appliquent à toute représentation du registre, y compris le futur JEPA.
- Hooks git : pas de `git add .`, staging explicite par path.
