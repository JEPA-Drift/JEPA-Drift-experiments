# Plan — stream 8b : hygiène (modules partagés, fixture sans effet de bord, registre des écarts)

Statut : **GO reçu le 2026-10-22** par l'écran d'approbation du plan ; trace verbatim : `prompts/GO-stream-08b.md`.

**Base de travail.** `stream-08b` = `main` = `5048a96`, atteint par fast-forward. Les corrections du prompt 8b y sont
présentes (`.gitignore` ajouté à la tâche 4 et aux livrables).

**Références de comparaison.** Entre `53dbdd3` et `5048a96`, le code, les tests, le `Makefile`, `CLAUDE.md`,
`.gitignore` et `docs/` sont identiques. Toutes les comparaisons sont donc prises sur `5048a96`, et les numéros de ligne
de l'audit cités plus bas restent valables. `prompts/GO-stream-12.md` n'est pas utilisé.

## Décision GO intégrée

| Point | Décision |
|---|---|
| Q1 — liens `.venv` et `external` non suivis | Option c : cause racine corrigée dans `.gitignore`, `/.venv` et `/external` remplacent `.venv/` et `external/` (QD) ; `.gitignore` devient un livrable ; `.git/info/exclude` n'est pas utilisé |
| Q2 — troisième copie du pivot dans `audit_information.load()` | Hors périmètre de 8b |
| Q3 — D4 | Contrôle ponctuel en lecture seule |
| Q4 — clôture | Arrêt après le commit et les vérifications, pour l'audit de l'orchestrateur ; aucun fetch, push ni fusion sur `main` |
| QA — trace du GO | Transcription verbatim de la revue et du GO dans `prompts/GO-stream-08b.md` |
| QB — hypothèses | H1, H9 et H10 confirmées |
| QC — lignes de sept accents graves (blocs 19, 22, 25) | Laissées en l'état |
| QD — `.gitignore` | Les anciennes lignes sont remplacées |
| H11 — commit | Un seul commit Conventional Commits, après tous les changements, le wrapup actualisé et un `make check` complet sous `.venv` ; `git status --porcelain` vide après ce commit |
| Environnement | `.venv` pour toutes les commandes, Python et pytest compris ; Trading n'est jamais activé ; `make` vient de `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`, placé en tête du PATH |

## Contexte

La vague suivante (streams 12, 13, 14, 17 et 18) attend la fusion de 8b. Trois briques partagées n'existent qu'en copies
locales : le pivot des caractéristiques, les statistiques de dérive de l'audit et le placebo de phases. Par ailleurs, le
fixture D1/D2 réécrit des fichiers suivis, les liens de worktree apparaissent comme non suivis, et aucun outil ne
contrôle la fidélité des prompts au master. Le stream 8b factorise ces briques sans changer aucune sortie.

## Conventions d'exécution

- **Python et pytest.** Toujours `.venv/bin/python` et `.venv/bin/pytest`, avec le PATH de la session, qui commence par
  `.venv/bin`. Les appels directs reçoivent
  `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42`.
- **make.** `MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`, puis `PATH="$MAKEBIN:$PATH" make …`. Ce
  préfixe vaut aussi pour `git commit`, puisque le hook pre-commit lance `make check`. Le Makefile trouve `python`,
  `pytest` et `pyflakes` dans `.venv/bin`.
- **Scratchpad.** `S` désigne le scratchpad de session ; aucune sortie temporaire n'est écrite dans `/tmp` ni dans le
  dépôt.
- **Réindexation.** `graphify` et `jcodemunch-mcp` sont trouvés par le PATH de la session, sans activation.

## État vérifié (lecture seule)

- **Worktree et liens.** Branche `stream-08b` à `5048a96`. `.venv` et `external` sont des liens vers le dépôt principal ;
  ce sont les seuls nœuds de ces noms dans l'arborescence. `data/raw/` est un répertoire réel contenant les liens `baf`
  et `d3_yf`.
- **Données.** D4 dérivé est absent du worktree mais présent dans l'arbre principal. La source de `MANIFEST.json` est
  `a05f0d9…`, le HEAD du dépôt B. `logs/data/build.log` est suivi.
- **Hooks.** `pre-commit` lance `make check` après `unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE GIT_QUARANTINE_PATH` ;
  `pre-push` contrôle les chemins EUROFIDAI.
- **Master des prompts.** 29 fichiers sur 29 sont des sous-chaînes exactes du master à `5048a96`. 19, 22 et 25 n'ont pas
  de saut de ligne final, d'où trois lignes de sept accents graves dans le master.
- **Fichiers suivis sous une règle d'ignorance.** `git ls-files -ci --exclude-standard` en liste 16 : 9 sous `logs/` et
  7 sous `slides/`. Cette liste doit rester identique après le correctif de `.gitignore`.
- **Environnements.** L'arbre principal est propre. Le MCP Graphify n'a pas pu se connecter ; jCodeMunch est disponible.

## Contradictions et points signalés

1. **Déplacement des statistiques de dérive.** Le prompt demande un déplacement « sans modifier les corps », mais ces
   corps dépendent d'autres éléments de l'audit : `debiased_sr2` appelle `_sr2`, `transitions` lit `WINDOW` et
   `MIN_PHASE`, et `mbb_indices` lit `BLOCK`. Le transfert verbatim déplace donc aussi `_sr2` et ces trois constantes
   (H1).
2. **Commande de vérification du prompt.** Elle ne redirige que `--out`. Avec les valeurs par défaut de `--fig-dir` et
   de `--log-dir`, elle écraserait `figures/audit/*` (8 fichiers suivis) et `logs/audit/audit.log` (suivi). Ces deux
   options, ainsi que `/tmp/audit_q`, sont redirigées vers `S`.
3. **Deux binaires make.** `.venv/bin/make` est un lien vers `envs/jepa-make`. Le binaire imposé est placé devant dans le
   PATH.
4. **Même défaut pour D4.** Le motif `data/derived/d4_eurofidai/` se termine aussi par `/` et ne couvrirait pas un lien
   symbolique ; le motif du hook pre-commit ne bloquerait pas non plus un tel lien. Hors périmètre ; le contrôle D4 lit
   les fichiers par chemin absolu, sans créer de lien.

## Hypothèses (confirmées par le GO)

- **H1 — Contenu de `drift.py`.** `jepadrift/stats/drift.py` reçoit verbatim `WINDOW`, `MIN_PHASE`, `BLOCK`,
  `transitions`, `_sr2`, `debiased_sr2`, `mbb_indices`, `rotate_phases`, ainsi que `_ci`, renommée
  `shifted_percentile_ci` (seule la ligne `def` change). Le module n'importe que numpy, et sa docstring indique la
  provenance. L'audit importe ces noms, dont `shifted_percentile_ci as _ci` ; `tests/test_audit.py` reste inchangé.
- **H2 — `load_chars_tensor(dataset, rows=None)`.** `rows` est tout index numpy de l'axe des jours de `dates.npy`. Le
  pivot réindexe sur `MultiIndex(dates[rows] × assets)`, sur le modèle du pivot de `tests/test_injection.py`. `names`
  contient les colonnes `c_*` dans l'ordre du parquet. Jeux acceptés : `d3_239`, `d3_500`, `d4_eurofidai` ; `d2_us97`
  lève `ValueError("D2 has no characteristics")`, tout autre nom une `ValueError`.
- **H3 — `impute_zero(C)`.** Elle reprend `injection.inject` (lignes 118 à 121). `inject` n'est pas modifié.
- **H4 — `horizon_gamma(H, alpha=TARGET_FPR)`.** La fonction rend H/α, se place à côté de `null_target`, et sa
  docstring cite P∞(alarme avant H) ≤ H/γ. Son test, dans `tests/test_pipelines.py`, vérifie les valeurs et que
  `null_target` rend α pour une lecture anytime-valid à γ_H.
- **H5 — Fixture `rebuilt`.** Fixture de session, non autouse, sur une racine `tmp_path_factory`.
  `pytest.MonkeyPatch.context()` remplace `ab.REPO_ROOT`, `ab.DERIVED`, `ab.RESULTS_DATA` et `ab.LOGS_DATA` le temps de
  `ab.build()`. Le `MANIFEST.json` commité est copié au préalable. Les autres tests lisent les fichiers commités.
- **H6 — Pivot de référence et graine.** `test_chars.py` importe `_d3_239_calib` et `_d3_239_to_2019` de
  `test_injection`. La graine est `SeedSequence([82, 1])`.
- **H7 — `tools/check_prompts.py`.** stdlib seule ; sortie `prompts-check: 29/29`, code 1 en cas d'échec.
- **H8 — `--sync-master`.** Un bloc va du titre `## PROMPT <id> —` jusqu'à la première de ces bornes : la clôture de
  quatre accents graves, le titre suivant ou la fin du fichier. Le remplacement conserve les sauts de ligne finaux du
  master. Un bloc absent est ajouté en fin de section 4. Résultat attendu : diff nul sur le master de `5048a96`.
- **H9 — Test et lint de l'outil.** `tests/test_check_prompts.py` tourne sur un master synthétique et couvre
  remplacement, ajout et idempotence. `tools` entre dans la portée de pyflakes du `Makefile`.
- **H10 — Registre des écarts.** Une entrée propre `C-stats-drift` suit les deux entrées verbatim.
- **H11 — Commit.** Un seul commit Conventional Commits, après tous les changements, le wrapup actualisé et un
  `make check` complet sous `.venv` ; `git status --porcelain` vide après ce commit.

## Fichiers touchés

- **Créés.** Modules : `jepadrift/stats/drift.py`, `jepadrift/data_loader/chars.py`, `tools/check_prompts.py`. Tests :
  `tests/test_drift_stats.py`, `tests/test_chars.py`, `tests/test_check_prompts.py`. Trace :
  `prompts/plans/plan-08b.md`, `prompts/wrapups/wrapup-08b.md`, `prompts/GO-stream-08b.md`.
- **Modifiés.** `.gitignore` ; `experiments/audit_information.py` (3 constantes et 6 fonctions retirées, 1 import
  ajouté) ; `jepadrift/pipelines.py` et `tests/test_pipelines.py` ; `tests/test_data_d1_d2.py` (fixture remplacé,
  2 tests ajoutés) ; `Makefile` (cible `prompts-check`, `.PHONY`, portée de pyflakes) ; `docs/DEVIATIONS.md`
  (2 entrées verbatim, plus H10) ; `CLAUDE.md` (`chars`, `drift`, `check_prompts.py`, phrase du fixture supprimée).
- **Inchangés et contrôlés.** `tests/test_audit.py`, `tests/test_injection.py`, `jepadrift/monitors/`,
  `jepadrift/injection.py`, les loaders, les prompts de stream et `prompts/Prompts_Claude_Code_v5.md` (diff nul).

## Tâches

### T0 — GO, mémoire et référence

1. Écrire ce plan et `prompts/GO-stream-08b.md` (QA).
2. Mettre à jour les mémoires `project-venv-interpreter` et `stream-worktree-setup`.
3. Référence sur `5048a96` : `make check` chronométré ; `find data results logs figures -newer $S/stamp -type f` ; audit
   `--quick` dans `$S/before` et empreintes dans `$S/sha_before.txt` ; `git ls-files -ci --exclude-standard` dans
   `$S/ignored_before.txt` ; hachage des 9 segments depuis `git show 5048a96:experiments/audit_information.py`.

### T1 à T6

| Tâche | Contenu | Méthode |
|---|---|---|
| T1 | `stats/drift.py` | TDD : `test_drift_stats.py` d'abord |
| T2 | `data_loader/chars.py` | TDD : `test_chars.py` d'abord |
| T3 | `horizon_gamma` | TDD |
| T4 | Fixture D1/D2, `.gitignore`, phrase de `CLAUDE.md` | `git check-ignore -v .venv external` désigne `.gitignore` ; `git ls-files -ci --exclude-standard` identique à `$S/ignored_before.txt` |
| T5 | `check_prompts.py`, cible `make`, test de l'outil | `--sync-master`, puis `git diff --exit-code prompts/Prompts_Claude_Code_v5.md`, puis `make prompts-check` : 29/29 |
| T6 | `DEVIATIONS.md`, puis `CLAUDE.md` | 2 entrées verbatim en fin de fichier, puis H10 |

## Transfert AST et contrôles SHA-256

1. **Segments.** SHA-256 de `ast.get_source_segment` pour les 9 nœuds de la base : constantes aux lignes 56, 58 et 61 ;
   fonctions aux lignes 285, 292, 302, 309, 339 et 389. Même calcul sur `drift.py` (ligne `def` de
   `shifted_percentile_ci` ramenée à `_ci`) : empreintes égales, figées dans `MOVED_SOURCE_SHA256`, sur le modèle de
   `test_e2_uses_moved_generator`.
2. **Reste de l'audit.** L'`ast.dump` du module modifié égale celui de la base, moins les 9 nœuds, plus un `ImportFrom`
   (script ponctuel dans `S`).
3. **Objets.** `au.<nom> is drift.<nom>` pour chaque nom déplacé ; l'audit ne définit plus aucun des 9 noms.
4. **Sorties de l'audit.** Audit `--quick` (`--datasets d2_us97 d3_239`, sorties dans `S`) avant et après : les deux
   listes `sha256sum` des 9 CSV sont identiques. Tout écart arrête le stream (déviation D3) ; la référence est alors
   relancée pour distinguer un non-déterminisme d'une régression.
5. **Fixture.** Les 16 fichiers reconstruits (8 D1, 5 D2, le profil, `build.log`, `MANIFEST.json`) ont les SHA-256 des
   fichiers commités ; les entrées `d1_etf4`, `d2_us97`, `d1_d2_profile` et `source` du manifeste sont égales.
6. **Sorties commitées.** `results/audit/*`, `figures/audit/*` et `logs/audit/audit.log` restent intacts.

## D4 (Q3) — contrôle ponctuel, lecture seule

Un script lancé depuis la racine du worktree avec `.venv/bin/python` remplace `eurofidai.DERIVED_D4` en mémoire par
`~/JEPA-Drift-experiments/data/derived/d4_eurofidai`. Il n'affiche que la forme, les noms de colonnes, les
décomptes de NaN et le résultat de l'alignement sur 50 paires tirées ; aucune valeur, aucun fichier écrit, aucun lien.
Le wrapup ne reprend que ces métadonnées.

## Critère « git status vide »

```
git status --porcelain                                        # vide grâce à .gitignore
touch $S/stamp && PATH="$MAKEBIN:$PATH" make check
find data results logs figures -newer $S/stamp -type f        # vide
git status --porcelain                                        # vide
```

## Vérification finale

```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
  .venv/bin/python experiments/audit_information.py --datasets d2_us97 d3_239 --quick \
  --out $S/after/out --fig-dir $S/after/fig --log-dir $S/after/log
sha256sum $S/after/out/*.csv | sed "s|$S/after/out/||" | diff - $S/sha_before.txt
.venv/bin/pytest -q tests/test_chars.py tests/test_drift_stats.py tests/test_audit.py \
  tests/test_check_prompts.py tests/test_data_d1_d2.py tests/test_pipelines.py
git diff --exit-code 5048a96 -- tests/test_audit.py tests/test_injection.py jepadrift/monitors
PATH="$MAKEBIN:$PATH" make check && git status --porcelain     # < 5 min, vide
PATH="$MAKEBIN:$PATH" make prompts-check                       # 29/29
```

## Clôture (Q4 : arrêt pour audit)

1. **Wrapup.** `prompts/wrapups/wrapup-08b.md`, en anglais : Context, Validated Results (SHA-256), Errors and Dead Ends,
   Current State, Vigilance Points, Recommendations.
2. **Réindexation.** `tools/reindex_graphify_jcodemunch.sh`.
3. **Commit unique (H11).** Une fois tous les changements faits et le wrapup actualisé, `PATH="$MAKEBIN:$PATH" make check`
   complet sous `.venv`, puis un seul `PATH="$MAKEBIN:$PATH" git commit` au format Conventional Commits ; indexation par
   chemin explicite, sans trailer ; `git status --porcelain` vide après ce commit.
4. **Arrêt.** Transmettre `git diff --stat 5048a96..HEAD`, les sorties des vérifications, les empreintes SHA-256, le
   wrapup et le hash du commit. Aucun `git fetch`, `git push` ni fusion sur `main`.

## Hors périmètre

- `inject` garde sa propre imputation ; `drift_rows`, `_moments` et `spy_phases` restent dans l'audit.
- `transitions` reste borné à `WINDOW` : E8 devra le paramétrer après J4.
- La colonne « État » de `INDEX.md`, la protection de D4 contre les liens symboliques et la copie du pivot dans l'audit
  (Q2) ne sont pas traitées par 8b.
