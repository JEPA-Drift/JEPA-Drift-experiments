# Plan 21-R — rédaction du contrat documentaire du runner global

Date : 8 novembre 2026. Base vérifiée : `26a2a5696a4412af8aceb6dbde3a9874e996aaad`, branche `stream-21-R`.

## Décision GO intégrée

**GO Codex au titre du mandat délégué**, limité à la rédaction documentaire. Ce GO lève le NO-GO provisoire de la révision 0 ; il ne vaut ni GO scientifique, ni autorisation de coder le runner ou d'activer J4.

- Proposition native révisée reçue : 413 lignes, SHA-256 `f3493029b7f6ede5bff7bde8926d37b83324f173779fae7a61adaf804c74d200`.
- Revue finale à huit points : SHA-256 `75a886719f0ff048a3f93726af3e427eebc4b10b3e2570eb0acef75753bbaeac`, conservée dans les journaux ignorés. Les huit réponses sont reçues pour ce lot documentaire. La revue indépendante n'a exécuté aucun code.
- La proposition native ci-dessous est un instantané antérieur au présent GO. Ses mentions « GO absent » et « mode plan » décrivent cet instantané. La présente décision et le GO séparé font autorité pour l'exécution documentaire.

### Arbitrage YAML définitif pour ce contrat

Refuser les ancres, alias et étiquettes YAML **explicites**, y compris les formes standard `!!str`, les étiquettes locales et les directives `%TAG`. Le refus futur est CONFIG et intervient avant l'import d'une cible. Il porte sur les constructions syntaxiques, pas sur un caractère placé dans une chaîne littérale. Les types implicites restent admissibles si le document construit a des clés chaînes distinctes et des valeurs JSON finies. Conserver les refus des doublons, fusions, cycles et valeurs non JSON.

Les configurations courantes n'emploient pas ces constructions ; cette restriction borne le langage du futur runner. Elle renforce le contrat sémantique réemployé sans modifier `tools/appendix_b.py`, dont les alias finis actuellement acceptés restent hors de ce lot. Aucun chargeur n'est écrit ou déplacé maintenant. Des témoins de refus sont seulement spécifiés, jamais présentés comme exécutés.

### Précisions de réception

1. Dans le §2.4 natif, « aucun run.json, aucune suppression » concerne les **échecs** post-import ; une réussite écrit bien `run.json` en dernier. Un échec d'import signifie une tentative d'import, pas un import nécessairement réussi.
2. L'invariance de ressource retenue porte sur `--jobs`. Git HEAD, chemins de sortie et horodatages restent hors identité selon le schéma ; un changement de fichier de POLICY est refusé par F. Ne promettre aucune invariance aux surcouches de ressources incluses dans POLICY.
3. Les descripteurs de protocole, de données, de preuve du lecteur et de collecte numérique, ainsi que le mécanisme ORIGIN, restent des portes bloquantes. Le contrat ne les remplit pas, ne qualifie aucune cible et n'authentifie pas un runtime hostile.
4. Les chemins proposés ou futurs sont identifiés comme tels ; le contrôle d'existence porte sur les références factuelles existantes. Adapter uniquement les contrôles shell documentaires à cette distinction, sans produire de code ou de test.

### Propriété et exécution

Claude peut écrire uniquement `docs/sections/benchmark_runner_contract.md`, les journaux ignorés `logs/stream_21_R/`, puis `prompts/wrapups/wrapup-21-R.md` après réception et invocation du wrap-up installé. Codex possède ce plan, `prompts/GO-stream-21-R.md`, une éventuelle mise à jour de réception du rapport d'inventaire et toute la clôture Git.

Le document suit les douze sections du §2, en anglais. Contrôles textuels et shell seulement : aucun Python, import, test, calcul, simulation, expérimentation, donnée de rendement ou entraînement. Aucun FROZEN réel, J4, modification de DEVIATIONS, MAPPING, source, configuration ou résultat scellé. La validation complète de clôture revient à Codex après arrêt de la session.

Même session interactive `jepa-s21-R`, UUID `2142c482-a8fc-47e4-975b-dbf6c9bd1f80`, Opus 5.5 Max et contexte conservés, sans Agent/Task. Sortie officielle du mode plan seulement après enregistrement du plan et du GO séparé ; démarrage documentaire après vérification du changement effectif par Codex.

## Proposition native révisée — instantané avant GO

# Plan natif 21-R — contrat documentaire minimal de `jepadrift/benchmark_runner.py` (PLAN ONLY, révision 1)

## Révision 1 : réponses à la revue Codex

**Source.** `logs/stream_21_R/codex-plan-review-v0.md` : NO-GO documentaire provisoire sur la révision 0 (SHA-256 `9e4fd544…e1f8`). Elle comprend les corrections 1–6, le complément indépendant 7–8 et les arbitrages Q1–Q9.

**Lectures de cette révision.** Seulement la revue et, en lecture seule, HEAD, l'état de l'arbre et le SHA de `tools/freeze_config.py`.

| # | Correction | Réponse intégrée |
|---|---|---|
| 1 | API F, pas 8 | `check()` reste tel que publié ; son champ `files` est un nombre. On lit un instantané canonique de FROZEN (sans lien, au plus 1 MiB) et on exige que le SHA-256 de ses octets égale `freeze_id`. Seuls `snapshot.files` et `snapshot.approval.sha256` servent ensuite. Lecture appariée et second `check()` sont des contrôles de cohérence bornés, pas une transaction atomique (§2.4). |
| 2 | Identité et qualification | `protocol`, `data` et la preuve du lecteur sont DEFERRED ; leur schéma est une porte E5 bloquante. Avant le dispatch, l'identité lie des déclarations attendues, pas des empreintes d'entrée observées. Le lecteur vérifie exactement ces octets avant tout calcul scientifique, et une preuve concordante est exigée à l'acceptation finale. Que le runner n'ouvre pas les rendements ne constitue pas cette preuve. Aucun run complet ni positif factice accepté avec `null` ; ni une chaîne non vide ni un GO haché ne valent autorité ; aucune décision E5 n'est inventée (§2.3-§2.5). |
| 3 | Environnement numérique | BLAS et dtype entrent dans l'identité, comme dans le précédent PCA. L'inspection de la bibliothèque numérique vient après les portes gel et qualification, et avant l'import de la cible et la création des sorties ; sa méthode est différée. Ni les versions ni l'empreinte d'un verrou ne vérifient les binaires installés ; les limites d'empreinte sont listées (§2.4, §2.5). |
| 4 | Qualification par variante | Une variante fixe la suite exacte des jetons scientifiques et l'ensemble exact des sorties. L'arité ne qualifie aucune valeur ; une valeur inconnue ou non qualifiée donne ARGV avant l'import. Les candidates restent UNQUALIFIED (§2.2-§2.4). |
| 5 | Précision des témoins | A1 compare le suffixe du répertoire à `run_id[:16]` ; `run.json` garde l'identifiant complet (64 hex). A4 porte sur des commits hors POLICY et hors approbation. Les témoins pré-import et post-import sont séparés. L'identité couvre toute la POLICY F, et la seule invariance promise est `--jobs` (§2.5, §2.7). |
| 6 | Ni refactor ni écart | Réemploi sémantique du contrat de chargeur strict d'`appendix_b` ; l'emplacement du code relève d'un plan futur. Aucun changement d'`appendix_b` ni de helper partagé. Les écarts `C-runner-*` sont listés dans le contrat « pending » ; `docs/DEVIATIONS.md` n'est pas touché (§2.8). |
| 7 | cwd et origine du code | Le cwd réel doit être ROOT ; sinon refus CWD avant l'import, sans `chdir` global. Les témoins positifs tournent avec cwd = ROOT de la fixture. L'origine résolue de la cible doit être son fichier source gelé déclaré sous ROOT ; une cible préchargée ou d'origine étrangère est refusée (ORIGIN) avant toute exécution de son code. Le contrôle du cwd ne ferme pas la substitution par chemin de recherche ou par cache d'import ; le mécanisme exact est différé. Les limites F restent écrites : vérificateur de confiance, cache de bytecode, runtime hostile. L'empreinte des fichiers n'authentifie pas l'état du runtime Python (§2.1, §2.4). |
| 8 | Création non atomique | Les trois `mkdir` sont séquentiels et suivent l'import. Une course au deuxième ou au troisième laisse les précédents : c'est un échec post-import, qui conserve la tentative incomplète, n'écrit pas `run.json` et ne supprime rien. Aucune promesse tout-ou-rien ; le refus EXISTS initial garde son témoin étroit (§2.4, §2.6, §2.7). |

**Arbitrages Codex intégrés.**
- **Q1.** Oui : un gel effectif et valide est exigé pour tout dispatch, sans contournement pré-2020.
- **Q2.** Oui, après la correction 5 : les commits Git et de gel et l'approbation restent dans `authorization` ou `provenance`, hors identité.
- **Q3, Q4, Q6.** Oui : extras exacts sur liste blanche, sans séparateur nu ; espaces de sortie dédiés et immuables ; `--jobs` vaut 1 par défaut et reste hors identité.
- **Q5, Q7, Q9.** Corrigés comme ci-dessus.
- **Q8.** Oui, avec une limite explicite : un code de cible qualifié de confiance et un espace de travail contrôlé sont des hypothèses. Le runner n'est pas un bac à sable OS, et aucun cadre d'instantané n'est ajouté.
- **Conservés :**
  - aucun FROZEN réel ni J4 ;
  - aucun run, test ou import ;
  - toutes les cibles UNQUALIFIED ;
  - identités et sorties PCA intactes.

## 0. Statut et contexte

- **Mandat.** `logs/stream_21_R/mission-plan.md`. Session interactive Opus 5.5, effort Max, sans sous-agent ; plafond de deux Claude.
- **Base.** Branche `stream-21-R` à HEAD `26a2a5696a4412af8aceb6dbde3a9874e996aaad`, avancée par Codex en avance rapide depuis `47d85dc`. L'arbre est propre et `tools/freeze_config.py` est présent (SHA-256 `6e17eea2…cf6a3`).
  - `26a2a56` n'ajoute que sept fichiers (lot F et rapport d'inventaire) et n'en modifie aucun.
  - Les lectures faites à `47d85dc` restent historiques, et les références de ligne des producteurs restent valides.
- **Pourquoi.** Le stream 21 reste PARTIEL : ni runner global, ni gel effectif, ni `configs/FROZEN.json` (REPRISE l.163). Le lot R fixe le contrat minimal du futur runner, sans code. Le runner reste DIFFÉRÉ jusqu'aux configurations E5 et à la sémantique monitor/holdout (CONTINUATION l.117 ; inventaire F l.76).
- **Autorité.**
  - Ce plan révisé n'est pas un GO. La session reste en mode plan, sans ExitPlanMode.
  - Le plan canonique français et le GO documentaire n'existent pas encore ; Codex possède `prompts/plans/plan-21-R.md` et `prompts/GO-stream-21-R.md`.
  - L'arrivée de J4 n'ouvre rien.

## 1. Faits établis (lecture seule)

### 1.1 Emplacement
- **Demandé :** `jepadrift/benchmark_runner.py`, par le prompt 21 §1 (l.7-10), CONTINUATION l.117 et REPRISE l.163. Les prompts 22 (l.17, 54-55) et 25 (l.20, 57) l'appellent par `python -m jepadrift.benchmark_runner --config configs/<x>.yaml [--quick | --include-test-window]`.
- **`tools/benchmark_runner.py`.** C'était une proposition non arbitrée de plan-21-rest §5.3/Q11 :
  - GO-21-rest l.12 : « Lot R différé » ;
  - F D3 (plan-21-F l.38) l'a retirée de POLICY ;
  - F limite 10 (l.518) et wrapup-21-F l.161 : sous `tools/`, POLICY v1 ne couvre que `freeze_config.py`.
- **Graphe actuel.** Aucun module de `jepadrift/` n'importe `experiments` ou `tools`. Ces deux paquets sont des espaces de noms sans `__init__.py`, et `jepadrift/__init__.py` est vide.

### 1.2 Contrat F publié (`26a2a56`)
- **API.** `FreezeError(code, detail)`, 13 codes (`freeze_config.py:36-50`) ; `main(argv=None)` sort en 0, 1 ou 2.
- **`check(root=ROOT)`** (l.353-388) rend `{commit, seal, approval, files, freeze_id}`. `files` est un nombre, `approval` un chemin, `freeze_id` le SHA-256 des octets de FROZEN.
- **`write`** est gardé pour les fixtures : racine sous `tempfile.gettempdir()` et absence du commit racine du projet (l.420-464).
- **FROZEN canonique.** `{schema, commit, files{chemin: sha256}, approval{path, sha256}}`, lu sans lien et borné à `MAX_FROZEN_BYTES` (l.136-203). POLICY compte 11 racines (l.29-31), dont les deux manifestes.
- **Portée du check.** CAVEAT l.38-40 : aucune lecture de données, aucune vérification d'octets de données, aucune interprétation de l'approbation, aucune autorisation de run. Limites : environnement non vérifié, `__pycache__` non couvert, course entre `check` et exécution, historique local de confiance (plan-21-F l.508-520).
- **`configs/FROZEN.json` est absent.** Un FROZEN réel casserait `tests/test_pca_drift_benchmark.py:719`.

### 1.3 Identité PCA scellée (à préserver)
- **Sources.** `docs/sections/pca_drift_benchmark.md` §1-2 et §8 ; `experiments/pca_drift_benchmark.py`, lignes 12-17, 420-427, 688-752, 818-830 et 1704-1865.
- **Identité.** `run_fingerprint` est le SHA-256 du JSON canonique de `identity` :
  - `schema_version` ;
  - `config_hash`, sans `resources` ;
  - `code_files` ;
  - `environment` : versions, BLAS, `dtype` et 5 variables ;
  - `inputs` ;
  - `seed`.
- **Hors identité.** La provenance : HEAD, branche, `dirty` et la commande avec `<OUT>`/`<LOG>`.
- **Identifiants dérivés.** `selection_id`, `metric_id` et `null_calibration_id` sont des `sha16` dérivés (doc l.67-76).
- **Écriture.** Le manifeste est écrit en dernier, et les sorties sont immuables. Le manifeste full `3b2299bc…` et les 13 fichiers d'identité sont scellés.

### 1.4 Producteurs existants
| Script | `main` | Options | Config | Sorties |
|---|---|---|---|---|
| `e1_problem.py:1187-1251` | 0 ; `ap.error` → `SystemExit(2)`, dont `--include-test-window` (l.1198) | `--config --quick --arms --jobs`(24) `--out --fig-dir --log-dir --include-test-window` | `Path(path).read_text()` + `safe_load` (l.1173-1175) | `e1_{null,cells,slopes,real_phases}.csv` selon `--arms`, `e1_j2_summary.txt`, figures, `e1.log` |
| `e3_calibration.py:939-1156` | 0 | `--config --quick --out --fig-dir --log-dir --jobs`(24) | `args.config.read_text()` (l.951) | 5 CSV + `e3_j2_check.txt`, figures, `run.log` (HEAD et durée) |
| `e10_robustness.py:732-871` | 0 ; `ap.error` pour `jepa`/`F2` (l.743-746) | `--stage`, `--families` requis ; `--config --quick --out --fig-dir --log-dir --jobs`(`os.cpu_count()`) | `args.config.read_text()` (l.750) | `e10_{cells,gains}.csv`, figures, `run.log` |

- **Chemins.** Les chemins reçus sont résolus relativement au cwd. Les autres entrées passent par `REPO_ROOT`, dérivé de `__file__` (E1 l.62, E3 l.62).
- **Écriture.** `mkdir(exist_ok=True)` puis écriture, donc écrasement ; E1 `plot()` relit les CSV présents (l.1122-1154).
- **Environnement.** Les variables BLAS, `MKL_CBWR` et `MPLBACKEND` sont forcées à l'import (E1 l.21-26, E3 l.24-29, E10 l.25-30).
- **Sorties.**
  - Elles sont agrégées par cellule ; aucune ligne par réplication n'existe sur disque.
  - Le déterminisme vis-à-vis de `--jobs` est épinglé : `tests/test_e1.py:172-187`, `tests/test_e3.py:335-347`, `tests/test_e10.py:188-195`.

### 1.5 Gardes, lecture physique, données
- **Gardes `check_window`.** E1 (l.96-100), E3 (l.109-113) et E10 (l.317-320) refusent sans condition et ne lisent pas FROZEN.
- **Chargement.** Les chargeurs E1, E3 et E10 (l.103-111, l.117-130, l.324-334) lisent le panneau entier via `DATASETS` avant la coupe. Il n'existe aucun lecteur borné avant I/O.
- **Précédents.**
  - C-jepa-d3-reader (`DEVIATIONS.md:750-759`) est le seul lecteur borné en I/O.
  - `read_pre2020_panel` du PCA (l.1359-1388) hache les fichiers entiers, octets 2020+ compris.
- **Vérification.** Aucune vérification des octets de données au chargement pour E1, E3 et E10. Le SHA journalisé par E3 et E10 est une consignation, pas une vérification.

### 1.6 Réemplois et conflits
- **F** : `check` et `FreezeError` publics ; sémantique de `_read_frozen`, `_canonical` et `_portable`.
- **Chargeur strict** : `tools/appendix_b.py:54-61` (clés égales par valeur construite), l.64-83 (valeurs finies et JSON) et l.95-98 (acyclicité).
- **Configurations à la base** : aucune ancre, aucun alias, aucune étiquette, aucune date non quotée ; taille maximale 1 582 octets (rg). `tools/trace_numbers.confined` est insuffisant.
- **Conflits.**
  - Le prompt 21 §1 (`run_hash` avec commit, CSV par réplication) contredit le §1.3 et le §1.4.
  - Le prompt 22 l.55 lit `results/e5/J4_gate.txt`.
  - Exigence d'un runner unique qui n'importe, ne copie ni ne relance le runner PCA (plan-21 l.79, audit 01-27 l.51, inventaire F l.76).

## 2. Tâche unique (après GO) : `docs/sections/benchmark_runner_contract.md` (anglais ; propositions)

Les sections du document sont les suivantes. Les propositions normatives sont résumées en 2.1–2.8.
1. Status and scope.
2. Location and layering.
3. Command-line interface.
4. Target table and qualification.
5. Refusal order.
6. Identity, authorization and provenance.
7. Output namespaces and validation.
8. Test-window path (2020+).
9. Future witnesses (test specification).
10. Unresolved gates.
11. Proposed departures (pending).
12. Not executed.

### 2.1 Emplacement, couches, cwd, origine (§1-2)
- **Statut.** DEFERRED : contrat seulement, candidates UNQUALIFIED, aucun run autorisé.
- **Emplacement.** Un module unique, `jepadrift/benchmark_runner.py`, couvert par POLICY v1. Ni shim `tools/`, ni couche d'enveloppe, ni `chdir`, ni abstraction de chargeur. Module feuille.
- **Imports.**
  - Au niveau du module : bibliothèque standard seule.
  - Imports tardifs, dans cet ordre :
    1. `tools.freeze_config`, après les portes statiques ;
    2. la bibliothèque numérique, après les portes gel et qualification ;
    3. la cible, en dernier.
- **cwd.** Le cwd réel doit être ROOT, c'est-à-dire le même `(st_dev, st_ino)`. Sinon : refus CWD avant l'import. Les chemins transmis sont relatifs à ROOT, donc au cwd.
- **Origine du code.** Un nom de module fixe ne garantit pas l'origine.
  - L'origine résolue de la cible doit être son fichier source gelé déclaré sous ROOT, présent dans `snapshot.files`.
  - Une cible préchargée (déjà dans `sys.modules`) ou d'origine étrangère est refusée (ORIGIN) avant toute exécution de son code.
  - Le contrôle du cwd ne ferme pas la substitution par chemin de recherche ou par cache d'import.
  - Le mécanisme exact est différé au plan d'implémentation, comme porte bloquante (G10).
- **YAML strict.** Réemploi sémantique du contrat d'`appendix_b`, avec une restriction proposée : refus des ancres, alias et étiquettes, absents des configurations actuelles. L'emplacement ou l'extraction du code relève d'un plan futur, sans changement d'`appendix_b` maintenant.

### 2.2 Interface (§3)
- **Signature.** `main(argv=None) -> int`. argparse avec `allow_abbrev=False` ; chaque option au plus une fois, sinon erreur d'usage, y compris sous la forme `=`.
- **Options du runner.**
  - `--config PATH` : requis, de la forme `configs/<nom>.yaml`.
  - `--jobs N` : entier ≥ 1, défaut 1. Ressource transmise à la cible, hors identité.
  - `--include-test-window` : drapeau.
- **Extras.**
  - Les autres jetons doivent égaler, jeton pour jeton, une variante qualifiée de la cible : pas d'analyse d'arité, pas de séparateur nu.
  - Diagnostic ARGV explicite pour les drapeaux gérés (`--config --out --output-dir --fig-dir --log-dir --jobs --include-test-window --resume --seed --mode`), y compris leurs formes `=`.
  - Toute autre suite donne ARGV : jeton inconnu ou abrégé, ordre différent, valeur non qualifiée.
- **argv transmis.** `--config <c> --out <R> --fig-dir <F> --log-dir <L> --jobs <N>`, suivi des jetons de la variante, plus `--include-test-window` seulement si la cible est qualifiée pour.
- **Sorties de processus.**
  - 0 : run complet, `run.json` écrit.
  - 1 : refus `benchmark-runner: error: CODE: detail`.
  - 2 : erreur d'usage.
  - 3 : `TARGET_FAILED` (code non nul, `SystemExit` ou exception de la cible) ; aucun `run.json`.

### 2.3 Table des cibles et qualification (§4)
- **Table.** `TARGETS` est une constante du module, donc du code gelé. Champs :
  - `module` et `config` ;
  - `variants` : liste de `{argv: suite exacte de jetons, outputs: {results|figures|logs: noms exacts}, expected_sha256: {…}}` ;
  - `protocol`, `data`, `reader`, `test_window`.
- **Descripteurs DEFERRED (porte E5, bloquante) :**
  - `protocol` : descripteur de protocole approuvé et immuable, holdout compris, dont les octets sont figés par le gel ;
  - `data` : déclarations attendues des jeux et segments, avec leurs empreintes attendues. Ce ne sont pas des empreintes observées.
  - `reader` : lecteur appartenant à la cible. Il ne lit que les segments déclarés et vérifie exactement les octets consommés contre `data`, avant tout calcul scientifique. Il produit une preuve, exigée à l'acceptation finale.

  Le schéma des descripteurs, celui de la preuve et la preuve de qualification restent des portes bloquantes. Que le runner n'ouvre pas les rendements ne constitue pas une preuve.
- **Qualification.**
  - Elle exige une variante exacte, plus `protocol`, `data` et `reader` liés à des descripteurs conformes au schéma approuvé, plus une preuve de qualification (DEFERRED).
  - Ni une chaîne non vide, ni un GO haché ne qualifient ou ne font autorité.
  - Aucun run de production complet ni positif factice accepté avec `null`.
- **Candidates e1, e3 et e10 : UNQUALIFIED.**
  - Elles n'ont aucune variante et des descripteurs nuls.
  - Les valeurs `--quick`, `--arms`, `--stage` et `--families` ne seront fixées que par un protocole approuvé.
  - Aucune revendication P4-D ni P5.
- **Refus TARGET :**
  - configurations PCA (`pca_drift_benchmark.yaml`, `_full_2000_resources.yaml`) ;
  - `ca_tjepa.yaml` ;
  - `eurofidai_schema.yaml`.

  E2 et `jepa_pretrain` sont absents de la table.

### 2.4 Ordre des refus (§5)
| # | Contrôle | Code | Classe |
|---|---|---|---|
| 1 | Six variables à l'import, avant tout import hors bibliothèque standard : `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg` | ENV | pré-import |
| 2 | Analyse argparse | usage (2) | pré-import |
| 3 | cwd réel égal à ROOT | CWD | pré-import |
| 4 | Chemin de configuration : canonique, `configs/`, composants portables, ouverture sans lien, fichier régulier, au plus 1 MiB | LINK / CONFIG | pré-import |
| 5 | Configuration présente dans `TARGETS` | TARGET | pré-import |
| 6 | Extras égaux à une variante qualifiée ; drapeaux gérés refusés | ARGV | pré-import |
| 7 | YAML strict (§2.1) ; racine mapping, clés chaînes, valeurs JSON finies | CONFIG | pré-import |
| 8 | Descripteurs `protocol`, `data`, `reader` ; fenêtre de test seulement si `test_window` | PROTOCOL / DATA / READER / TARGET | pré-import |
| 9 | `check(ROOT)`, API publiée inchangée. Instantané de FROZEN (sans lien, fichier régulier, au plus 1 MiB) dont le SHA-256 doit égaler `freeze_id`, puis analyse stricte et canonique. `snapshot.files[config]` doit égaler le SHA des octets du pas 4, et les fichiers des descripteurs doivent figurer dans `snapshot.files` avec un SHA égal. | FREEZE | pré-import |
| 10 | Import de la seule bibliothèque numérique ; descripteurs BLAS et dtype (méthode DEFERRED) | ENV | pré-import (cible) |
| 11 | Identité et `run_id` (§2.5) | — | — |
| 12 | Avant toute création : parents réels sans lien ; les trois `run-<run16>` absents | LINK / EXISTS | pré-import |
| 13 | Origine résolue égale au fichier source gelé déclaré sous ROOT, cible non préchargée (mécanisme DEFERRED), contrôlées avant toute exécution de la cible ; puis import, dont l'échec donne 3 sans rien créer | ORIGIN / TARGET_FAILED | pré-import / import |
| 14 | `mkdir` exclusifs et séquentiels : `results`, puis `figures`, puis `logs` | EXISTS | post-import |
| 15 | Appel de `main(argv)` | — | post-import |
| 16 | Sortie 0, sinon 3. Second `check()` au même `freeze_id`. Sorties exactes de la variante, `expected_sha256`. Preuve concordante du lecteur exigée à l'acceptation finale (format DEFERRED). `run.json` exclusif, écrit en dernier. | TARGET_FAILED / FREEZE / OUTPUTS / DATA | post-import |

- **Pré-import (pas 1 à 13 avant l'import).** Aucun import de la cible, aucune création, aucun accès aux données ; le runner n'ouvre jamais un fichier de données.
- **Post-import (pas 14 à 16).**
  - Aucun `run.json`, aucune suppression.
  - Une course au deuxième ou au troisième `mkdir` laisse les répertoires déjà créés, conservés comme tentative incomplète. Un espace étranger ou partiel n'est jamais supprimé.
  - Aucune promesse tout-ou-rien ni sans effet de bord.
- **Cohérence bornée, pas une transaction atomique.** La lecture appariée et le second `check()` ne ferment pas les fenêtres check → lecture, lecture → import, pendant le run, ni le cas « modifier puis restaurer ». Les limites F s'appliquent : liens physiques, substitution de la racine, historique et vérificateur de confiance.
- **Limite Q8.** Code de cible qualifié de confiance et espace de travail contrôlé sont des hypothèses. Le runner n'est pas un bac à sable OS.
- **Limites d'authentification conservées de F.**
  - Le vérificateur est de confiance : modifié, il peut mentir.
  - Le cache de bytecode (`__pycache__`) n'est pas couvert.
  - Un runtime hostile (`sitecustomize`, fichiers `.pth`, modules préchargés ou modifiés) n'est pas détecté.
  - L'empreinte des fichiers n'authentifie pas l'état arbitraire du runtime Python.
- **Ce que FROZEN et le GO ne font pas.** La présence de FROZEN ne débloque rien. Lire un GO n'authentifie aucune autorité scientifique.
- **Rapport à F.** Ni `write`, ni modification des gardes de F, ni création de FROZEN.
- **Codes.**
  - Fermés : ENV, CWD, ARGV, CONFIG, LINK, TARGET, PROTOCOL, DATA, READER, FREEZE, ORIGIN, EXISTS, OUTPUTS, IO.
  - `TARGET_FAILED` correspond à la sortie 3.

### 2.5 Identité, autorisation, provenance (§6)
```
{"schema": "jepadrift-runner/1", "target": "<nom>", "config": {"path": "configs/<nom>.yaml", "sha256": "<hex>"},
 "argv": ["<jeton>", ...], "test_window": false, "policy_files_sha256": "<sha256 de canon(snapshot.files)>",
 "environment": {"python": "<x.y.z>", "packages": {"<distribution>": "<version>"},
                 "numeric": {"blas": "<descripteur qualifié>", "dtype": "float64"}, "variables": {<les six>}},
 "protocol": <DEFERRED : descripteur approuvé, lié aux octets gelés>, "data": <DEFERRED : segments, liés aux octets gelés>}
```
- **Canonicalisation.** `canon(x) = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)`, encodé en ASCII, sans flottant.
- **Identifiant.** `run_id` est le SHA-256 complet (64 hex), inscrit dans `run.json`. `run16 = run_id[:16]` ne sert qu'aux noms de répertoire.
- **Portée conservatrice.**
  - `policy_files_sha256` couvre toute la POLICY F : toutes les configurations, même sans rapport avec la cible, les surcouches de ressources, `experiments/`, `jepadrift/`, les verrous, les manifestes, `Makefile`, `conftest.py` et `tools/freeze_config.py`. Tout octet modifié change `run_id`.
  - Seule invariance promise : `--jobs`. Le reste est hors identité par construction.
- **Hors identité :**
  - `--jobs`, horodatages, durées ;
  - chemins de sortie et chemins absolus ;
  - HEAD, branche et état Git ;
  - C, S et l'approbation ;
  - nom d'hôte.
- **`authorization`** (hors `run_id`, vérifiée avant et après) : le résultat de `check()` et `snapshot.approval.sha256`.
- **`provenance`** : HEAD par plomberie isolée comme F, `jobs`, commande normalisée à marqueurs.
- **Relations entre identités.**
  - **Code, configurations et manifestes :** via `policy_files_sha256`, vérifiés par `check()` avant et après, de façon bornée.
  - **Environnement :** Python, distributions, descripteurs numériques et six variables.
    - Limites :
      - ni les chaînes de version ni l'empreinte d'un verrou ne vérifient les binaires installés : `site-packages`, `.venv`, `torch-cf`, bibliothèques BLAS et OpenMP ;
      - ne sont couverts ni le jeu d'instructions ni le chemin MKL au-delà de `MKL_CBWR=COMPATIBLE`, ni l'OS, le noyau ou la libc.
    - La collecte et la vérification exactes sont différées.
  - **Approbation :** dans `authorization` seulement.
  - **Données.** Hacher un manifeste ne vérifie pas les octets des données.
    - Avant le dispatch, `identity.data` lie des déclarations attendues, pas des empreintes observées.
    - Le lecteur vérifie ces octets avant tout calcul, et la preuve concordante est exigée à l'acceptation (DEFERRED).
    - Le refus du runner d'ouvrir les rendements ne vaut pas preuve.
    - Aucun chemin ni contenu propriétaire.
- **PCA.** Espace distinct : `schema` et `run_id`, jamais `run_fingerprint`. Aucun recalcul, aucune réécriture et aucun import d'identifiant PCA ; PCA n'est pas une cible.

### 2.6 Sorties, validation, chemin 2020+ (§7-8)
- **Espaces.** `results/benchmark_runner/<cible>/run-<run16>/`, de même sous `figures/` et `logs/`. Jamais un répertoire par défaut, jamais `results/pca_drift_benchmark/`.
- **Création.** Séquentielle, après l'import, non atomique (§2.4).
- **Validation.**
  - Chaque espace contient exactement les fichiers réguliers de la variante qualifiée : un fichier manquant ou en trop, un sous-répertoire ou un lien donne OUTPUTS.
  - `expected_sha256` est comparé quand il est déclaré ; un écart est une divergence, avec arrêt D3 et aucun changement de code ni de paramètre.
  - Journaux et figures sont hachés, jamais comparés.
  - La preuve du lecteur doit concorder avec `data`, sinon DATA (DEFERRED).
- **`run.json`.**
  - Octets canoniques suivis d'un saut de ligne : `{schema, run_id, identity, authorization, provenance, exit_code, outputs{chemin relatif: {sha256, bytes}}}`.
  - Création exclusive sans lien, en dernier ; son absence signale une tentative incomplète.
  - Ni écrasement, ni reprise, ni suppression par le runner.
- **Pas de CSV unifié par réplication** : les producteurs émettent des agrégats.
- **Chemin 2020+.** Il exige, dans l'ordre :
  1. `--include-test-window` ;
  2. une cible neuve, gelée sous son propre GO, qui déclare `test_window` ;
  3. une variante et des descripteurs qualifiés, lecteur borné avant I/O compris ;
  4. un `check()` de production valide.

  Les gardes des cibles restent inchangées et forment la dernière barrière. Aujourd'hui, toute demande est refusée au plus tard au pas 8.

### 2.7 Témoins futurs (§9 ; spécification, rien n'est lancé)
- **Montage.**
  - Un dépôt Git temporaire par test, avec les racines POLICY, `experiments/fake_target.py` gelé avec la fixture et des configurations synthétiques.
  - FROZEN est créé par `freeze_config.write`, autorisé sous tmp seulement, puis scellé par S.
  - `ROOT` et `TARGETS` sont injectés, avec un espion d'import. cwd = ROOT de la fixture pour tout positif.
  - Ni donnée réelle ni expérience du projet.
- **Dépendance au schéma.** Tout témoin qui atteint le pas 9 exige une cible de fixture qualifiée, avec des descripteurs synthétiques conformes au schéma approuvé (porte E5), jamais `null`. Ces témoins sont spécifiés maintenant, mais ne pourront être écrits qu'après le schéma.
- **Classe P — refus pré-import.** Chacun rend 1 ou 2, un seul message, aucun import de la cible et aucune création.
  - ENV : chacune des six variables.
  - Usage.
  - CWD : cwd sur une copie de ROOT ; un chemin symbolique vers ROOT est accepté.
  - LINK / CONFIG : chemin absolu, `..`, `./`, `//`, hors `configs/`, lien, FIFO, plus de 1 MiB.
  - CONFIG (YAML) :
    - YAML invalide ;
    - doublons `0x10`/`16` et `yes`/`true` ;
    - ancre, alias, étiquette ;
    - NaN ou inf, racine non mapping.
  - TARGET : configuration inconnue, configuration PCA.
  - ARGV : drapeau géré, forme `=`, abréviation, jeton inconnu, ordre différent, valeur non qualifiée, `--` nu.
  - PROTOCOL / DATA / READER : descripteurs nuls, lignes e1, e3 et e10.
  - Fenêtre de test non déclarée.
  - Après schéma :
    - FREEZE : FROZEN absent ; 1 octet modifié (HASH) ; commit touchant `jepadrift/` (CHANGED) ; FROZEN remplacé entre `check` et l'instantané ; configuration différente de l'instantané ;
    - ENV numérique ;
    - EXISTS initial : chaque espace présent, même vide ; parent lien ;
    - ORIGIN : cible préchargée dans `sys.modules`, même depuis ROOT ; résolution hors ROOT par une entrée prioritaire du chemin de recherche. Dans les deux cas, le code de la cible n'est jamais exécuté.
- **Classe Q — échecs post-import et courses** (après schéma). La cible est importée ; aucun `run.json`, aucune suppression.
  - Échec d'import : 3, sans espace créé.
  - Collision au deuxième ou au troisième `mkdir` : EXISTS, et le ou les répertoires précédents sont conservés.
  - Cible qui rend 1, lève une exception ou appelle `ap.error` : 3.
  - Sortie manquante, en trop, sous-répertoire, lien ou mauvais hash : OUTPUTS.
  - Preuve du lecteur absente ou discordante : DATA.
  - L'ordre « vérifier avant de calculer » est une propriété du lecteur, démontrée par ses propres témoins de qualification (DEFERRED). Le runner ne contrôle que la preuve finale.
  - Fichier de POLICY modifié par la cible : FREEZE au second `check`.
- **Classe A — acceptation** (après schéma).
  - **A1.** Trois répertoires et `run.json` écrit en dernier, avec `run_id` complet. Le suffixe égale `run_id[:16]`, `sha256(canon(identity))` égale `run_id`, l'argv transmis est exact et cwd = ROOT.
  - **A2.** Entrées égales, octets d'identité égaux ; `--jobs` 1 et 2 donnent le même `run_id`.
  - **A3.** Une autre variante qualifiée donne un autre `run_id`.
  - **A4.** Un commit après S, hors POLICY et hors approbation (`results/`, `paper/`), garde le `run_id` et change `provenance.head`. Tout changement de POLICY, `docs/manifests/d4_manifest.json` et surcouches de ressources compris, est refusé par F : aucune invariance n'est promise.
- **Classe S — statiques.**
  - Imports au niveau du module : bibliothèque standard seule ; aucun module `jepadrift` n'importe le runner ; aucun `os.chdir`.
  - La table ne contient ni entrée PCA ni drapeau géré dans une variante, et toutes ses candidates sont UNQUALIFIED.
  - `run.json` ne contient ni chemin absolu ni la racine de la fixture.

### 2.8 Écarts proposés et wrapup
- **Écarts.** Le §11 du contrat liste, avec la mention « pending future implementation approval » :
  - `C-runner-identity` : `run_id` sans commit ni approbation ;
  - `C-runner-outputs` : espaces par run, sans CSV par réplication ;
  - `C-runner-freeze-required` : Q1.

  `docs/DEVIATIONS.md` n'est pas modifié (Q9 décliné).
- **Wrapup.** `prompts/wrapups/wrapup-21-R.md`, en anglais, en six rubriques, après la revue Codex et l'attribution du créneau de clôture. Aucune opération Git par Claude.

## 3. Hypothèses et défauts
- **H1.** Emplacement `jepadrift/`, puisqu'une variante `tools/` exigerait une POLICY v2.
- **H2.** Spécification seulement : les SHA et valeurs des exemples sont des marqueurs `<…>`.
- **H3.** F est cité tel que publié à `26a2a56`, et les lignes citées valent à cette base.
- **H4.** Variantes à jetons exacts, sans analyse d'arité ni nouveau cadre de dispatch.
- **H5.** Chargeur strict : réemploi sémantique, plus la restriction sur ancres et étiquettes ; emplacement différé.
- **H6.** Descripteurs `protocol`, `data` et preuve du lecteur : DEFERRED ; aucune décision E5 n'est inventée.
- **H7.** Collecte numérique et contrôle d'origine : méthodes différées au plan d'implémentation.
- **H8.** Contrat en anglais, à 120 colonnes au plus, sans chemin absolu ; plan et échanges en français.

## 4. Périmètre de fichiers
- **Écrits après GO :** seulement `docs/sections/benchmark_runner_contract.md` (nouveau) et `prompts/wrapups/wrapup-21-R.md` (au créneau de clôture).
- **Non modifiés :** tout le reste, dont `jepadrift/`, `tools/` (`appendix_b.py` compris), `tests/`, `configs/`, `experiments/`, `Makefile`, `docs/DEVIATIONS.md`, `docs/MAPPING.md`, les prompts et les fichiers Codex.
- **Interdits :** FROZEN, opération Git, réindexation, `make`.

## 5. Portes non résolues (bloquent l'implémentation de production)
- **G1. Protocole E5.** Configurations, variantes, sorties ; `J4_gate.txt` à placer dans les espaces du runner.
- **G2. Sémantique monitor et holdout.**
  - Fenêtre et embargo de 65 séances ; holdout.
  - Cohortes, dont C-pca-covid-retrospective.
  - Lectures à H ; ARL0 réservé à E2 et E3.
- **G3. Lecteurs bornés avant I/O** par jeu réel, avec des empreintes de segment.
- **G4. Vérification des octets consommés** au chargement.
- **G5. Activation J4 sous GO du chercheur.**
  - Approbation nommée.
  - Code et configurations dans C.
  - Remplacement des deux gardes d'écriture de F.
  - Ligne 719 du test PCA.
  - `make freeze`.
- **G6. Cibles 2020+** en code neuf gelé (E5, E8).
- **G7. Dépendances amont** : 16, 17 recevable, 19 si requis, 23 phase 2.
- **G8. Mandat réel pré-2020** pour toute reproduction ; référence E1 `9ae7e261…`.
- **G9. Formats de production non tranchés (E5, bloquants) :** schémas des descripteurs `protocol` et `data`, forme de la preuve du lecteur, preuve de qualification.
- **G10. Méthodes différées au plan d'implémentation (bloquantes pour la production) :**
  - collecte et vérification des descripteurs numériques ;
  - liste des distributions (torch pour E5) ;
  - contrôle ORIGIN contre le préchargement, la recherche et le cache.

## 6. Validation documentaire (sans Python, test, import ni `make`)
```bash
set -euo pipefail; export GIT_OPTIONAL_LOCKS=0 LC_ALL=C
D=docs/sections/benchmark_runner_contract.md; W=prompts/wrapups/wrapup-21-R.md
test "$(sha256sum < tools/freeze_config.py | cut -c1-64)" = 6e17eea2a1d3b974d3452dc9fe9f9acc634a0cf96450104a02861b67354cf6a3
test -f "$D" && test ! -L "$D" && test "$(rg -c '^## ' "$D")" = 12 && test -z "$(awk 'length > 120' "$D")"
! rg -n '/home/|\.codex/|/tmp/' "$D" && rg -q 'DEFERRED' "$D" && rg -q 'UNQUALIFIED' "$D" && rg -q 'pending' "$D"
test ! -e configs/FROZEN.json && test ! -e jepadrift/benchmark_runner.py && test ! -e tools/benchmark_runner.py
git diff --quiet HEAD && test "$(git status --porcelain=v1 --untracked-files=all | rg -v '^\?\? prompts/(plans/plan|GO-stream)-21-R\.md$')" = "?? $D"
rg -o --no-filename '`(configs|docs|experiments|jepadrift|prompts|results|tests|tools)/[A-Za-z0-9_./-]+' "$D" | tr -d '`' \
  | sed 's/:.*//' | sort -u | rg -v '^(jepadrift/benchmark_runner\.py|tests/test_benchmark_runner\.py|configs/FROZEN\.json|(results|figures|logs)/benchmark_runner)' \
  | while read -r p; do test -e "$p" || { echo "absent: $p"; exit 1; }; done
test "$(sha256sum < results/e2/e2_cells.csv | cut -c1-64)" = e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
test "$(git show :results/e2/e2_cells.csv | sha256sum | cut -c1-64)" = e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
test "$(grep -c $'\r$' results/e2/e2_cells.csv)" = 47
test "$(sha256sum < results/e3/e3_overshoot.csv | cut -c1-64)" = 1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3
test "$(sha256sum < results/pca_drift_benchmark/full_2000_20261101/manifest.json | cut -c1-64)" = 3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47
# at closeout only:
test "$(rg -c '^## (Context|Validated Results|Errors and Dead Ends|Current State|Vigilance Points|Recommendations)$' "$W")" = 6 && ! rg -n '/home/' "$W"
```

## 7. Risques finis
1. **Contrat lu comme une autorisation ou comme un schéma E5.** Parade : bannière DEFERRED, descripteurs DEFERRED, candidates UNQUALIFIED, section « Not executed ».
2. **Promesse de garanties excessives.** Parade : cohérence bornée, création non atomique, absence de bac à sable et limites d'empreinte écrites en toutes lettres.
3. **Confusion avec les identifiants PCA.** Parade : schéma, clés et espaces distincts.
4. **Conflit avec les prompts 22 et 25.** Parade : conflit déclaré, à trancher par G1.
5. **Affirmation inexacte.** Parade : chaque fait cite un `fichier:ligne` lu.
6. **Chemin privé dans le livrable.** Parade : contrôle rg du §6.

## 8. Questions résiduelles
Aucune question bloquante : les arbitrages Q1–Q9 et les points 1–8 sont intégrés. Codex peut retirer la restriction YAML proposée (ancres, alias, étiquettes) si elle juge qu'elle excède le réemploi sémantique.

## 9. Ressources
- **Charge.** Deux fichiers d'environ 380 et 120 lignes, et des contrôles shell de moins de 5 s.
- **Ce qui n'est pas mobilisé.** Aucun créneau d'exécution du projet, aucun verrou, aucun Python ni réseau.
- **Session.** La même, sans changement de modèle, d'effort ou de contexte.

## 10. Trace de session
- **Révision 0.**
  - Lu : mission, `CLAUDE.md`, les deux amorçages du 7 novembre (extraits), prompt 21, plan, GO et wrapup 21-rest.
  - Lu : note et code PCA (extraits), fichiers F, producteurs E1/E3/E10 (extraits), `appendix_b`, `confined`, `DEVIATIONS.md` (extraits), tests, prompts 22 et 25.
  - Commandes : `ls`, `rg`, `wc`, `sha256sum` et `cat` sur un fichier vide ; Git en lecture seule avec `GIT_OPTIONAL_LOCKS=0`, y compris sur `26a2a56`.
- **Révision 1.**
  - Lu : `logs/stream_21_R/codex-plan-review-v0.md`, relu dans sa version finale à huit points (points 2 et 7 précisés).
  - Commandes : `git rev-parse HEAD` (`26a2a56…`), `git status --porcelain` (vide), `sha256sum tools/freeze_config.py` (`6e17eea2…`).
- **Non fait.** Aucun Python, import, test, `make`, mutation Git, Graphify ni jCodeMunch. Seul ce fichier de plan a été écrit.
