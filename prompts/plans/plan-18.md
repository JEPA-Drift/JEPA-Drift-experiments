# Stream 18 — clôture documentaire CD-DFM : plan natif (revu par Codex)

## Contexte
Demande : `logs/orchestration_20261106/request.md` (6 nov. 2026). Objet unique : correction factuelle du diagnostic
`docs/sections/cd_dfm.md` (commit `d8e644b`, 2026-10-30), plus audit de clôture et wrapup. Aucun adaptateur,
entraînement, installation, exécution de la chaîne externe, Git, sous-agent, Graphify/jCodeMunch.
Worktree `review/stream-18-20261106` à `20ad9e8` (= base annoncée). `make check` non relancé (lecture seule).

## Constats vérifiés (lecture seule, 2026-11-06)
- F1 Épinglage : `data/derived/MANIFEST.json` `sources.d3.cd_dfm` = repo `https://github.com/alexouadi/CD-DFM`,
  commit `37a1dfb39974884df822aa2994854bbf1270e381`, `access: read-only` (écrit par
  `sp500._update_manifest` après `_clone_cd_dfm`, stream 3). HEAD du clone = ce SHA (2026-07-29, « Update contact
  email »). `GIT_OPTIONAL_LOCKS=0 git status --porcelain` : 0 ligne non ignorée ; 13 `*.pyc` ignorés seulement.
- F2 Imports : scripts/tests insèrent `<clone>/src` dans `sys.path` (`scripts/train.py:18`). `from data.dataset
  import` : 25 instructions dans 22 fichiers (dont `scripts/train.py:21`, `src/train.py:12`) ; `from data import
  preprocess_panel` : `scripts/preprocess_dataset.py:19` ; `from data.preprocess import` : `tests/test_preprocess.py:9` ;
  `from cddfm.data.dataset import` : `scripts/benchmarks/run_sparse_pca.sh:25`. Arbre suivi au pin : 71 fichiers,
  0 chemin avec composant `data/` ou fichier `data.py`, aucun paquet `cddfm/`. Présents : `src/model/`, `src/eval/`,
  `src/analysis/`, `src/paths.py`, `src/train.py`. Le README (table « Repository layout ») annonce `src/data/`.
- F3 Licence : aucun fichier `licen[cs]e|copying|notice|copyright` (toute casse, toute profondeur) au pin ; README
  sans mention de licence du code. Métadonnées distantes non consultées (pas de fetch).
- F4 Entrées : README/`configs/data.yaml` exigent 10 caractéristiques continues issues de RavenPack et Compustat,
  11 parts compositionnelles, 2 catégorielles (`gics_sector`, `exchg`), rendements log ; panel déclaré non
  redistribuable. Local : 4 continues tirées des rendements (`CONTINUOUS_CHARS`, `jepadrift/data_loader/sp500.py:56`)
  + 11 indicatrices GICS statiques (`C-D3-gics-static`).
- F5 Historique : `d8e644b` est le seul commit touchant `cd_dfm.md` ; aucun P/G/W 18 ; `prompts/amorcage-18.md`
  prévoyait `plan-18.md` après GO, jamais enregistré ; branche `stream-18` = `c284823`, 0 commit propre. Aucun
  `cddfm_adapter.py`, test d'adaptateur ni entrée P4 CD-DFM dans le code.

## Erreurs du document `d8e644b` à corriger
| Lignes | Affirmation | Preuve locale | Action |
|---|---|---|---|
| 5 | « Continuous-Discrete Dynamic Factor Model » | titre README : « Characteristic-Driven » | corriger |
| 5-7 | « was evaluated » | aucun entraînement ni évaluation | « prévu comme variante P4 (prompt 18), jamais exécuté » |
| 11-14 | « All rights reserved », violation, règles CIFRE « recorded in CLAUDE.md » | conclusion juridique ; `CLAUDE.md` ne contient pas « CIFRE » | remplacer par F3, observation seule |
| 15-19 | motif « Z-1 loader », « state-space ingestion layer » | Z-1 = livrable prévu de l'adaptateur ; `kalman|state.space` : 0 occurrence au pin | remplacer par le motif réel F2 (prompt 18, tâche 5) |
| 20-24 | citation J4, « license condition not met » | texte exact en `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md:26` (§2) ; chemin incomplet | chemin complet ; seule la disponibilité est jugée non remplie ; licéité non évaluée |
| 26-37 | Kalman, coût élevé, JEPA, « sufficient orthogonal coverage », « no coverage gap » | aucune preuve ; le README affirme une inversion Woodbury O(nK²+K³) | supprimer la section |

## Livrables après GO (anglais, propriété proposée par la demande)
1. `docs/sections/cd_dfm.md`, réécrit (~40 lignes) : Status (unavailable ; condition d'arrêt de la tâche 5 remplie ;
   ni adaptateur, extraction, entrée P4, entraînement, remplacement local ni comparateur de substitution) ; Pinned
   source (F1, nom correct) ; Official training chain (table absent/présent F2 ; chaîne externe non exécutée) ;
   License observation (F3, « not a legal conclusion ») ; Input limit (F4, aucune correspondance construite ni
   évaluée) ; J4 eligibility (citation §2, « non disponible ») ; Not established (coût, supériorité JEPA,
   suffisance des comparateurs, couverture expérimentale).
2. `docs/audits/stream_18_closeout_2026_11_06.md` : sources lues, commandes lecture seule et sorties, table
   affirmation→correction ci-dessus, trace de workflow F5, éléments non examinés, décision `BLOQUÉ` inchangée.
3. `prompts/wrapups/wrapup-18.md` : Context, Validated Results (comptes F1-F4, SHA-256 des fichiers 1-2), Errors and
   Dead Ends, Current State, Vigilance Points, Recommendations.

## Hypothèses et défauts
- H1 Chemin conservé `docs/sections/cd_dfm.md` ; le prompt 18 nommait `cddfm_adapter.md` : écart noté dans audit et
  wrapup, sans entrée `DEVIATIONS.md` (interdit) ni `C-CDDFM-inputs` (non exigée sur chemin d'arrêt).
- H2 Hypothèse non établie (motif `.gitignore` amont `data/` non ancré, qui couvre `src/data/`) : audit seulement.
- H3 Dépendances amont (Python 3.11, PyTorch 2.5, statsmodels, nonlinshrink, ipca) : « non examinées », l'arrêt
  étant déjà déclenché par F2.
- H4 Pas de journal de corrections dans `cd_dfm.md` : la table vit dans l'audit, l'ancien texte dans Git.
- H5 Aucun nettoyage des `*.pyc` du clone ; audit 01–27, INDEX, master, DEVIATIONS, CLAUDE.md intacts ; pas de
  reindex (Codex possède Git et la fin de stream).

## Questions (défaut entre crochets)
- Q1 Chemin : garder `cd_dfm.md` ou créer `cddfm_adapter.md` nommé par le prompt 18 ? [garder]
- Q2 Hypothèse `.gitignore` : audit seul, aussi dans `cd_dfm.md`, ou omise ? [audit seul]
- Q3 `make check` lancé par Claude après écriture (résultat dans le wrapup) ou laissé au hook de commit Codex ? [Claude]

## Vérification après GO (chaque commande échoue sur divergence)
```bash
P=37a1dfb39974884df822aa2994854bbf1270e381; C=external/cd-dfm
test "$(git -C $C rev-parse HEAD)" = "$P"
test -z "$(git -C $C ls-tree -r --name-only $P | grep -E '(^|/)data(/|\.py$)')"
test -z "$(git -C $C ls-tree -r --name-only $P | grep -iE '(^|/)(licen[cs]e|copying|notice|copyright)([._-]|$)')"
test "$(git -C $C grep -l 'from data\.dataset import' $P | wc -l)" -eq 22
git -C $C grep -q 'from data import preprocess_panel' $P -- scripts/preprocess_dataset.py
! grep -n -i -E 'continuous-discrete|kalman|state-space|all rights reserved|would violate|cifre|coverage gap|orthogonal coverage' docs/sections/cd_dfm.md
! grep -n '/home/' docs/sections/cd_dfm.md docs/audits/stream_18_closeout_2026_11_06.md prompts/wrapups/wrapup-18.md
test "$(GIT_OPTIONAL_LOCKS=0 git status --porcelain)" = "$(printf ' M docs/sections/cd_dfm.md\n?? docs/audits/stream_18_closeout_2026_11_06.md\n?? prompts/wrapups/wrapup-18.md')"
PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE \
  PYTHONHASHSEED=42 MPLBACKEND=Agg .venv/bin/make check   # attendu : 37 + 545 passed, 5 skipped
```
La ligne `git status` exacte sera ajustée si Codex dépose ses fichiers GO dans ce worktree.

## Arrêt
Plan présenté, attente de la revue Codex. Une approbation d'ExitPlanMode n'est pas le GO : aucune écriture du dépôt
avant le GO daté distinct.


## Décision GO intégrée — clôture documentaire du 6 novembre

Date : 2026-11-06, 12:22 UTC. GO Codex dans le mandat de supervision délégué par le chercheur ; aucune signature personnelle du chercheur n'est attribuée. Base 20ad9e860a58373ec85405de6ee19a68322dd02e. Référence exécutoire : `prompts/GO-stream-18.md`. Le fichier natif original reste archivé, non réécrit.

**Réponses Q1–Q3.** Q1 : conserver `docs/sections/cd_dfm.md`, sans second document de diagnostic concurrent. Q2 : omettre l'hypothèse causale sur le `.gitignore` ; l'absence observée des modules suffit, sa cause n'est pas établie. Q3 : contrôles documentaires seulement par Claude ; `make check` et réindexation seront exécutés par Codex à la clôture. Aucun test, entraînement ou installation externe n'est nécessaire à ce diagnostic.

**Corrections de la procédure.** Le GO et le plan, déposés par Codex, sont des fichiers étrangers à préserver dans le statut Git ; ne pas exiger exactement trois lignes au statut global. Vérifier les chemins propres à Claude et l'absence de modification des autres fichiers. Le wrapup doit invoquer la directive installée avant tout commit, conserver l'anglais et les six rubriques du projet. Aucun commit par Claude.

- [ ] Confirmer les observations F1–F4 sur l'arbre Git épinglé, sans exécution externe.
- [ ] Corriger le diagnostic et écrire l'audit factuel, sans conclusions juridiques ni comparatives non mesurées.
- [ ] Contrôler le diff, les chemins possédés, les SHA des sorties et les invariants ; distinguer les contrôles réellement exécutés de la référence antérieure.
- [ ] Invoquer la directive wrap-up installée pour le checkpoint anglais, puis s'arrêter pour revue Codex.

**Vigilance de revue.** Ne pas confondre absence au commit avec inexistence ailleurs ; absence de licence avec jugement juridique ; absence d'adaptateur Z-1 avec cause racine des imports cassés ; diagnostic documentaire avec évaluation empirique ; résultats de tests archivés avec tests exécutés dans cette session.
