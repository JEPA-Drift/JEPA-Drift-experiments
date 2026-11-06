# Plan stream 21 — lot de traçabilité hors gel J4 (v1 native, en attente du GO écrit Codex)

**État canonique : GO du lot limité, enregistré avant exécution ; la décision intégrée en fin de fichier tranche les questions de la proposition native conservée ci-dessous.**


## Contexte
Mandat : `logs/orchestration_20261106/plan-request.md`, base `69d5624`. Le prompt 21 regroupe gel J4, `benchmark_runner`, figures, `trace_numbers`, `dpi_lint` et `appendix_b`. Le mandat réduit le lot à la traçabilité des nombres déjà rapportés : il exclut gel, `FROZEN.json`, configurations, runs, figures et second runner, et reste indépendant du stream 19 et des modèles entraînés. L'audit 01–27 classe le stream 21 `À_REPLANIFIER` (« une couche gel/trace cohérente, pas un second runner »). L'approbation de cet écran natif ne vaut pas GO.

Sources lues : CLAUDE.md (= AGENTS.md, lien symbolique), mandat, `prompt-21-freeze-runner.md`, audit `streams_01_27_relevance_2026_11_06.md`, prompts 29 et 31 (en entier), clauses lignée/manifeste des prompts 28 et 30, `paper/sec3_theory.tex`, `paper/appA_proofs.tex`, `tools/`, `Makefile`, hooks, `tests/test_check_prompts.py`, `test_decoupling.py`, `test_floors.py`, garde-fous D2, `results/e2/J1_report.md`, en-têtes de lignée et de manifeste PCA.

## Constat (lecture seule)
- `paper/` contient `sec3_theory.tex`, `appA_proofs.tex` et un `.bib`. Il n'y a ni macro `\E{}` ni `\newcommand` : **0 nombre balisé**. Les sections expérimentales citées par sec3 (`sec:exp-floors`, `sec:problem`) n'existent pas dans `paper/`.
- Inventaire préliminaire des nombres porteurs de résultat : 19 jetons, tous dans sec3. appA ne contient que des constantes de littérature (ρ = 0.5826).

| Classe | Jetons (ligne de sec3) | Preuve |
|---|---|---|
| Cellule unique d'un CSV scellé | 17, 142, 1{,}510, 2{,}787, 1{,}066, 2{,}322 (l. 52) | `results/e2/e2_cells.csv`, G1/gauss/dim 1/SR 1.0. Colonnes : `pred_delay` (cusum_x, cusum_t) et `first_order` (onset). Chaque sélecteur trouve exactement 1 ligne (awk, lecture). L'arrondi entier concorde, et `J1_report.md` donne les mêmes valeurs. Le SHA du fichier est déjà épinglé (`E2_SHA`, `tests/test_pca_drift_contracts.py:41`). |
| Dérivé candidat | 1.8 (l. 52) | `arl0_pred / pred_delay` sur la même ligne (252/142.04). La formule est inférée de la phrase. |
| Analytique, épinglé par un test | 1.22, 2.01, 3.91, 9.64 (l. 80) ; 2.01 (l. 105) | `tests/test_floors.py` (tolérance 0.01 ; 2.012 ± 1e-3). |
| Analytique, non épinglé | 5.2 (l. 80) ; 1.39, 1.15 (l. 105) | `jepadrift/floors.py` ; ni test ni CSV. |
| Non sourcé | 13–16 et 8–11 (l. 111) | Aucun CSV ni formule documentés. « 8 to 11 » renvoie à une section absente. |

Sont exclus de l'inventaire : années de citation, renvois, constantes de formule (504, 252) et paramètres (γ, D, SR, τ_a/τ_γ, α, β, t7, D ≤ 16).

- Lignée existante :
  - PCA : `table_lineage.csv` relie chaque cellule affichée à son fichier source et à sa clé ou formule. S'y ajoutent `table_manifest.json`, `figure_manifest.json` et `Figure_1_*_source.csv` (point → `metric_id`), sous la garde des 44 contrats.
  - E2 : J1 report et invariant SHA.
  - Données : `MANIFEST.json` et `d4_manifest.json`.

  Aucune de ces couches ne couvre la prose de `paper/`, et aucun nombre PCA n'y est cité.
- Motifs DPI (prompt 21 §5) : une seule occurrence, sec3 l. 25 (« An encoder creates no information »). C'est un énoncé correct par négation, donc un faux positif d'un lint à motifs.

## Décision YAGNI : audit documentaire et MAPPING, sans code
- `trace_numbers.py` vérifierait aujourd'hui 0 nombre balisé. Les 6 nombres repérables par leur littéral viennent d'un CSV dont le SHA est déjà épinglé. Le mandat limite les tests aux fixtures factices, donc ces tests ne couvriraient aucun nombre réel dans `make check`.
- `dpi_lint.py` : la seule occurrence est un faux positif.
- `appendix_b`, figures, runner et gel sont différés.

## Livré maintenant, après GO (anglais, 3 fichiers nouveaux)
1. `docs/audits/stream_21_trace_scope_2026_11_06.md`, avec :
   - périmètre et base ;
   - règle d'énumération et table par jeton (classe, ligne, preuve) ;
   - chevauchement avec les couches existantes ;
   - scan des motifs DPI et ses limites (négations, paraphrases ; ce n'est pas un contrôle de sens) ;
   - lacunes signalées, non corrigées ;
   - portes futures.
2. `docs/MAPPING.md`, pour la règle CLAUDE.md « every reported number traces to a CSV and a script ».
   - 6 lignes au format : fichier de `paper/` + label voisin + littéral | CSV relatif | sélecteur `(arm, mode, background, dim, sr_annual, gamma)` | colonne | valeur source lue | arrondi à 0 décimale `ROUND_HALF_EVEN`, `{,}` retiré | statut `READ_MATCH` (vérifié par lecture, sans outil).
   - Une ligne de couverture : balisés 0 ; jetons de résultat 19 ; cellule unique 6 ; le reste renvoie à l'audit. Ni PASS ni pourcentage.
3. `prompts/wrapups/wrapup-21.md` (six sections), après le wrap-up natif.

Codex gère `prompts/plans/plan-21.md`, `prompts/GO-stream-21.md`, la réindexation AST et Git. Aucun autre fichier n'est touché : ni `paper/`, `tools/`, `tests/`, `configs/`, `results/`, `figures/`, ni DEVIATIONS, prompts/master, CLAUDE.md ou fichiers du stream 19.

## Hors lot (exécution future non autorisée)
Gel J4, `FROZEN.json` et `freeze_config`, `benchmark_runner`, `figures/make_*`, `appendix_b`, tout run (E1, E3, PCA), toute édition de `paper/`, tout test d'épinglage de 5.2, 1.39 ou 1.15.

## Dépendances
- Aucune nouvelle dépendance, aucun lien avec le stream 19 ni avec des modèles entraînés.
- Lectures seules : `paper/`, `e2_cells.csv` et J1 report, `test_floors.py`, lignée PCA.
- Tests D2 et règle numpy-only non affectés : aucun `.py` créé, rien sous `data/`.

## Contrôles (commandes en lecture seule, pas de TDD de prose)
- `git status --porcelain` et `git diff --name-only origin/main` : exactement les 3 fichiers, plus ceux de Codex.
- J1 : `sha256sum results/e2/e2_cells.csv` et `git show :results/e2/e2_cells.csv | sha256sum` valent `e315e537…570823` ; 47 lignes, dont 47 en CRLF.
- Chaque ligne de MAPPING : `awk` compte exactement 1 ligne ; la cellule est relue et l'arrondi recopié dans l'audit.
- `grep -nE '/home/|/tmp/|/Users/|/root/'` sur les 3 fichiers : sortie vide.
- Claude ne lance ni pytest ni `make check`, faute de code ; `make check` passe par le hook pre-commit de Codex.
- 44 contrats : aucun fichier couvert n'est modifié, ce que prouve le diff. Aucune annonce de résultat de test sans exécution.

## Portes futures (spécification minimale pour un GO ultérieur)
- **G-T `tools/trace_numbers.py` + `tests/test_tools.py`.** S'ouvre au premier nombre issu d'un CSV hors E2, ou au premier nombre balisé dans `paper/`.
  - Stdlib seulement (`csv`, `decimal`) ; aucun import numpy, pandas ou jepadrift.
  - Chemins relatifs POSIX, sous `paper/` et `results/` uniquement. Refus avant toute ouverture : chemin absolu, `..`, `data/raw/**`, `data/derived/d4_eurofidai/**`.
  - Le sélecteur doit trouver exactement 1 ligne.
  - NA, vide ou nan : refus, jamais 0.
  - Arrondi `Decimal` explicite ; littéral présent une seule fois ; CSV lu avec `newline=''`, jamais réécrit.
  - Sortie : compteurs avec leurs dénominateurs.
  - TDD sur fixtures factices : cas positif, nombre altéré, sélecteur ambigu ou absent, NA, égalité .5, chemin refusé. Ensuite pyflakes et les 44 contrats.
- **G-D `dpi_lint`.** S'ouvre si la prose théorique s'étend. Doit traiter les négations et se présenter comme un lint à motifs.
- **G-J4.** Gel, runner, figures et `appendix_b` sous un GO J4 distinct, avec un seul runner (réemploi de `experiments/pca_drift_benchmark.py`).

## Séquence après GO
1. Rédiger l'audit, puis MAPPING.
2. Exécuter les contrôles et consigner leurs sorties.
3. Wrap-up natif, puis `wrapup-21.md`.
4. Arrêt. Codex réindexe (AST), exécute `make check` via le hook, commit et push.

En cas de quota ou d'erreur : conserver l'état, rapporter, ne pas réessayer.

## Questions (défaut entre crochets)
- **Q1.** Décision YAGNI : audit et MAPPING sans code [oui], ou ouverture de G-T dès maintenant ?
- **Q2.** « 1.8 » : uniquement dans l'audit, comme `DERIVED_CANDIDATE` [oui], ou ligne dérivée dans MAPPING (`arl0_pred/pred_delay`) ?
- **Q3.** `docs/MAPPING.md` comme fichier séparé [oui], ou table intégrée à l'audit seulement ?
- **Q4.** Inventaire limité à `paper/*.tex` [oui] ? `docs/sections`, les wrapups et le glossaire CLAUDE.md (142 / 2,787) seraient seulement mentionnés dans l'audit.
- **Q5.** Lacunes (5.2, 1.39, 1.15 ; 13–16, 8–11) signalées sans test ni édition de `paper/` [oui] ?

## Décision GO intégrée — Codex, 2026-11-06, 17:49 UTC

**GO du lot documentaire et de MAPPING, sans outil nouveau**, selon `prompts/GO-stream-21.md`. Plan natif archivé sous `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `03da31042270fd859d7888683d40d628803d24f284dcb5312fd8b0f1f4f2c490`. Cette décision prime sur les formulations de la proposition.

- **Q1 :** audit et MAPPING sans code. Le besoin d'un contrôleur générique n'est pas établi par le corpus actuel à zéro nombre balisé. Retirer l'argument selon lequel des fixtures factices interdiraient toute vérification de nombres existants : des contrôles de lecture sur les CSV scellés sont autorisés. La décision YAGNI repose sur le périmètre actuel et ne dispense pas d'une vérification reproductible des six correspondances.
- **Q2 :** `1.8` reste uniquement dans l'audit comme dérivation candidate, explicitement inférée et non vérifiée. Ne pas le présenter comme une cellule source ou une validation numérique.
- **Q3 :** `docs/MAPPING.md` séparé, avec source LaTeX et emplacement, littéral exact, clé complète, colonne, texte numérique source, règle d'arrondi, CSV et SHA-256, ainsi que chemin du script producteur. Distinguer un `pred_delay` théorique et un `first_order` de toute moyenne Monte Carlo `mean_delay`. Aucune prétention de reproduction par le code actuel.
- **Q4 :** inventaire limité à `paper/*.tex`. Autres documents : contexte seulement. Le compte de 19 est préliminaire : établir le recensement par occurrence, expliciter les extrémités de fourchettes et les exclusions, puis rapporter le compte observé sans le forcer.
- **Q5 :** lacunes ou références analytiques non épinglées signalées comme telles, sans les déclarer fausses faute de CSV. Les fourchettes sans source identifiée dans le périmètre lu restent des lacunes de traçabilité. Aucun test numérique nouveau ni édition de paper.
- **Vérification des correspondances :** autoriser, après GO, un court contrôle en lecture seule sous `.venv/bin/python` utilisant seulement `csv`, `decimal` et la bibliothèque standard. Zéro import de code du projet, numpy ou pandas ; aucun recalcul scientifique. Pour chaque entrée : clé unique, cellule non vide/finie, normalisation explicite du littéral LaTeX, `Decimal.quantize(..., ROUND_HALF_EVEN)`, comparaison à zéro décimale et conservation des octets du CSV. Consigner commande, code de sortie, six clés/colonnes et SHA dans les journaux ignorés et l'audit. Pas de nouvelle bibliothèque, outil de dépôt, test ou CSV généré.
- `READ_MATCH` atteste seulement la correspondance littéral/cellule/arrondi. Il ne certifie ni une conclusion scientifique, ni une lecture ARL0/FPR/ADD, ni toute la prose. Zéro macro, six correspondances et autres classes sont rapportés avec leurs dénominateurs, sans taux global artificiel.
- Les bornes budget / anytime-valid / calibration ARL0 sont conservées ; une valeur de prédiction ne devient pas une mesure. Ne pas convertir NA en zéro ou transformer les incertitudes en PASS.
- Fichiers autorisés : audit anglais, MAPPING anglais, wrapup-21 anglais et journaux ignorés ; aucun autre fichier. Le wrap-up natif puis le fichier aux six sections font partie du GO avant remise à Codex. Le gel J4 et tous les outils/campagnes historiques restent hors lot.
