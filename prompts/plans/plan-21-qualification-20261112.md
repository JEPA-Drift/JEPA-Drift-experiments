# Plan natif 21-qualification-20261112 — qualification documentaire des cibles e1, e3, e10 (PLAN ONLY, révision 0)

## Contexte
Stream 21 partiel : 21-F clos à `26a2a56`, 21-R clos à `3c7f8f3` ; ni runner de production ni FROZEN réel ; e1, e3, e10 UNQUALIFIED ; G1–G10 ouvertes (`logs/stream_21_qualification/mission-plan.md:11` ; `docs/sections/benchmark_runner_contract.md:160-170`, `:500-534`). L'amorçage P2 demande un plan de qualification des cibles et des lecteurs bornés, à défaut un plan de blocage exact (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_12.md:119-123`). Résultat visé : un document anglais d'écarts qui rend la prochaine tâche d'ingénierie révisable, sans lever aucune porte.

## 0. Statut, autorité, exclusions
- PLAN ONLY, aucun GO scientifique ni de production. Base `891cfa5f56c8ec20988f9a18efef4ed468e1c720`, branche `stream-21-qualification-20261112`, session `jepa-s21-qualification-20261112` (UUID `8d7f770c-0998-45fe-b18b-90a9201d646c`), Opus 5.5 effort max, sans sous-agent (`logs/stream_21_qualification/mission-plan.md:3`).
- Empreintes relevées au shell : mission `d947c7c02b8c0a7462a542dbb98d2d370d1d351814f04868cc8edc3d9a1fcaba` ; contrat `2414f1da…3481` et `tools/freeze_config.py` `6e17eea2…f6a3`, égales à `prompts/wrapups/wrapup-21-R.md:32`, `:126`.
- Production DEFERRED (`docs/sections/benchmark_runner_contract.md:9-11`). Aucune décision de schéma : le GO 21-R n'a tranché que la restriction YAML et laisse les descripteurs DEFERRED (`prompts/GO-stream-21-R.md:21-24`).
- Exclus : runner, dispatcher, lecteur borné, activation de schéma, protocole statistique nouveau, qualification, reproduction E1/E3/E10, FROZEN, `make freeze`, J4/E5, D6/E6, 2020+, données privées, JEPA/VAE, PCA scellée ; Python, import, test, `make`, calcul, Git, installation, octets de données (ni en-tête `.npy` ni métadonnées Parquet), recherche externe, Graphify, jCodeMunch ; les quatre bornes UNSOURCED.

## 1. Livrable après GO : `docs/audits/stream_21_qualification_20261112.md` (anglais, ≤ 230 lignes, ≤ 120 octets par ligne)
Règles : un fait = `file:line` relu à `891cfa5`, chemin complet à la première ancre de chaque puce ; tout schéma, témoin ou fixture porte PROPOSED / NOT EXECUTED ; le manifeste fournit des empreintes déclarées, jamais des octets consommés ; aucune promesse de bac à sable OS ni de transaction atomique, limites de confiance et de course conservées (`docs/sections/benchmark_runner_contract.md:240-255`) ; renvoi aux sections du contrat plutôt que recopie.
Plan du document (budget de lignes) :
1. Status, authority, evidence rules (≈ 15).
2. Cross-cutting facts (≈ 25, §2.1).
3. Candidate maps e1, e3, e10 : CLI et sorties ; données ; descripteurs, origine, holdout, échecs, collisions ; classe de preuve (≈ 75, §2.2–2.5).
4. G1–G10 matrix, chaque ligne marquée `OPEN` (≈ 30, §3).
5. Minimal future fixtures and refusals (≈ 30, §4).
6. E5 gate file versus runner namespaces (≈ 12, §5).
7. Exact pending decisions (≈ 25, §10).
8. Not executed (≈ 8).

## 2. Faits ancrés à reporter (relus à `891cfa5` ; `:N` répète le dernier fichier cité)
### 2.1 Transversaux
- F : `check()` rend `files` comme nombre, plus `freeze_id` (`tools/freeze_config.py:382-383`) ; FROZEN porte `files` en mapping (`:452-453`) ; un check réussi ne lit aucune donnée et n'autorise rien (`:38-40`) ; POLICY = 11 racines, sans `results/` ni données hors `data/derived/MANIFEST.json` (`:29-31`) ; gardes d'écriture fixture intouchables ici (`:426-429`, `:433-435`).
- Chargeurs : `DATASETS` (`jepadrift/representations/extract.py:34-35`) → `np.load` de fichiers entiers (`jepadrift/data_loader/articleB.py:80-84`, `:93-95` ; `jepadrift/data_loader/sp500.py:582-591`) ; `pre_monitor` = [début pretrain, fin calib) tiré de `splits.yaml` (`jepadrift/pipelines.py:94-98` ; `jepadrift/data_loader/articleB.py:106-111` ; `jepadrift/data_loader/sp500.py:606-610`).
- Couverture déclarée, non observée : `ret_wide.npy` D2 jusqu'au 2025-06-30, D3 du 2000-01-03 au 2026-10-16 (`data/derived/MANIFEST.json:128-132`, `:163-167`) ; phases D1 jusqu'en 2025 (`:87-105`) ; `chars.parquet` D3 sans plage déclarée (`:182-183`).
- Précédent borné, pretrain seulement : row groups Parquet, refus d'un row group atteignant 2020-01-01 ; `ret_wide.npy` D3 en ordre Fortran, lecture d'un préfixe contigu en ordre C impossible (`docs/DEVIATIONS.md:752-756`). Ordre mémoire de D2 et frontières de row groups au 2020-01-01 : INCONNUS.
- Les trois producteurs réécrivent les variables de threads à l'import (`experiments/e1_problem.py:21-26`, `experiments/e3_calibration.py:24-29`, `experiments/e10_robustness.py:25-30`), insèrent ROOT en tête de `sys.path` (`experiments/e1_problem.py:48`, `experiments/e3_calibration.py:49`, `experiments/e10_robustness.py:48`) et ouvrent un pool `spawn` si `jobs > 1` (`experiments/e1_problem.py:546-551`, `experiments/e3_calibration.py:613-618`, `experiments/e10_robustness.py:503-508`) dont les tâches rappellent les chargeurs (`experiments/e1_problem.py:402-405`, `experiments/e3_calibration.py:313-315`, `experiments/e10_robustness.py:420-423`). Inféré, non exécuté : un worker `spawn` exécutant une tâche D6 peut réimporter la cible et rappeler un chargeur non borné ; le contrôle ORIGIN du parent ne suffit pas à établir celui des enfants. Aucune lecture réelle par les tâches D5 pures n'est inférée.
- `save_fair_csv` formate sans hacher (`jepadrift/pipelines.py:67-71`). Gardes pré-J4 inconditionnelles, sans lecture de FROZEN (`docs/sections/benchmark_runner_contract.md:402-406` ; `CLAUDE.md:161-162`).

### 2.2 e1 (`experiments.e1_problem`, `configs/e1.yaml`)
- CLI : `main(argv=None)` (`experiments/e1_problem.py:1187`) ; `--config --quick --arms --jobs(24) --out --fig-dir --log-dir --include-test-window` (`:1189-1196`) ; test window et bras inconnu refusés par `ap.error` (`:1198-1202`) ; `--arms` est un ensemble (`:1200`) : ordres et doublons diffèrent en jetons, pas en calcul ; `--quick` fusionne le bloc `quick` (`:1173-1184` ; `configs/e1.yaml:44-51`) ; la clé `window` (`configs/e1.yaml:3`) n'est pas lue, la fenêtre est codée (`experiments/e1_problem.py:67`) ; la cible relit la config (`:1175`), écart borné par le second `check()` (`docs/sections/benchmark_runner_contract.md:240-246`).
- Sorties fonction de `--arms` et des données : `e1_null` si J2I (`experiments/e1_problem.py:1218-1221`), `e1_cells` seulement s'il existe des lignes (`:1232-1234`), `e1_slopes` si B (`:1235-1238`), `e1_real_phases` si C (`:1240-1243`), résumé et `e1.log` toujours (`:1245`, `:1250`) ; figures selon la présence des CSV et des filtres (`:1123`, `:1138-1142`, `:1153-1156`) ; empreintes par glob `e1_*` (`:1247-1248`) ; répertoires `exist_ok` (`:1204-1205`, `:1122`).
- Données : `load_window` charge tout, découpe `pre_monitor`, exclut 2005-01-03 sur D3, contrôle fenêtre et contiguïté (`:103-128`, `:68`, `:96-100`) ; caractéristiques (`:131-135`, `:305-307`) par rechargement de `ret_wide.npy` et lecture entière de `chars.parquet` (`jepadrift/data_loader/chars.py:24`, `:34` ; `jepadrift/data_loader/sp500.py:599-603`) ; phases lues entières (`jepadrift/stats/drift.py:78-80` ; `jepadrift/data_loader/articleB.py:98-103`) ; sidecars `z_*.json` (`experiments/e1_problem.py:356-358`) ; CSV d'audit (`:836`, `:1023`) ; seule l'empreinte de `predicted_gains.csv` est journalisée (`:1215`).
- Holdout : cellules rétrospectives, calib postérieure aux onsets (`:12-15`) ; bras S avec P3-D (`:8`, `:350-351`), sous `C-P4D-null-insample` (`docs/DEVIATIONS.md:707-718`).

### 2.3 e3 (`experiments.e3_calibration`, `configs/e3.yaml`)
- CLI : `main` (`experiments/e3_calibration.py:939`) ; `--config --quick --out --fig-dir --log-dir --jobs(24)` (`:941-946`), sans `--include-test-window` ; `--quick` (`:952-954` ; `configs/e3.yaml:46-47`) ; défauts de figures et journaux dérivés de `--out` (`experiments/e3_calibration.py:955-956`), neutralisés par l'argv transmis (`docs/sections/benchmark_runner_contract.md:104-106`).
- Sorties fixes : cinq CSV (`experiments/e3_calibration.py:1106-1109`), `e3_j2_check.txt` (`:1111`), quatre figures ×{png,pdf} (`:868`, `:891`, `:912`, `:934`), `run.log` (`:1154`) ; répertoires créés après le calcul (`:1104-1105`) ; HEAD Git lu par sous-processus (`:1113`).
- Données : `load_rows` charge tout, découpe, exclusion D3 déclarée, fenêtre stricte (`:116-133`, `:68`, `:109-113`) ; `results/audit/symmetry_tests.csv` (`:64`, `:775`) ; empreinte de `ret_wide.npy` entier journalisée après calcul (`:1120`). Holdout : D6 et fenêtres brutes descriptives 2005–2019 (`:9-12`).

### 2.4 e10 (`experiments.e10_robustness`, `configs/e10.yaml`)
- CLI : `main` (`experiments/e10_robustness.py:732`) ; `--stage` et `--families` obligatoires (`:734-735`), `jepa` et `F2` refusés (`:743-746`) ; `--families` ne sert qu'à ce refus (`:745`) : `F1` et `F1 F1` calculent la même chose ; `--jobs` par défaut `os.cpu_count()` (`:741`) ; `--quick` (`:751-752` ; `configs/e10.yaml:8-10`).
- Sorties fixes : `e10_cells.csv`, `e10_gains.csv` (`experiments/e10_robustness.py:844-845`), figures `fpr_inflation`, `gains` (`:706`, `:727`), `run.log` (`:869`) ; répertoires créés tard (`:840-841`).
- Données : `load_real` charge tout puis découpe (`:323-334`) ; garde à borne haute seule (`:317-320`), donc la ligne D3 du 2005-01-03 reste incluse, contrairement à E1/E3 (`docs/DEVIATIONS.md:531-533`) : segments propres à chaque cible ; sidecars (`experiments/e10_robustness.py:349-352`) ; empreintes de `ret_wide.npy` journalisées (`:784`, `:837`, `:857`). Holdout : fenêtres brutes du pretrain ajustées sur la calib ultérieure, rétrospectives (`:11`).

### 2.5 Rubriques communes à écrire pour chaque cible
- Descripteurs : `protocol` (variante exacte, holdout) ; `data` (fichiers et segments propres à la cible, entrées annexes `splits.yaml`, sidecars, CSV d'audit, phases, caractéristiques) ; `reader` absent, détenu par la cible (`docs/sections/benchmark_runner_contract.md:148-150`), donc producteur modifié sous GO.
- Échecs : fenêtre, exclusion, sidecar ou fichier absent lèvent dans la cible → TARGET_FAILED, jamais DATA (`:116-117`, `:262-268`) ; un CSV d'audit périmé passe inaperçu. Collisions : espaces exclusifs préalables (`:208-218`), `exist_ok` des producteurs compatible (`:353-355`).
- Classes de preuve : (a) fixtures factices, spécifiables maintenant : refus P/S (§4) ; (b) GO d'ingénierie séparé : lecteur, routage des lectures (workers compris), schéma, dispatcher ; (c) décision du chercheur : variantes, holdout, segments, mandat pré-2020, J4.

## 3. Matrice G1–G10 à écrire (toutes OPEN ; aucune levée par la documentation)
| Porte | Preuve actuelle | Blocage | Propriétaire / dépendance | Prochaine tâche bornée | Témoin (PROPOSED) | Autorisation |
|---|---|---|---|---|---|---|
| G1 E5 | aucune config E5 ; conflit prompt 22 / réécriture 07 (§5) | protocole E5 absent | chercheur ; 16, 17, 19, 23 | note de décision E5 (§5) | artefact de porte déclaré dans la variante E5 | GO chercheur |
| G2 holdout | cibles rétrospectives (§2.2–2.4) ; splits (`CLAUDE.md:61-62`) | sémantique monitor/holdout | chercheur | champs `holdout` PROPOSED | descripteur sans holdout déclaré refusé | GO chercheur |
| G3 lecteurs | chargeurs non bornés (§2.1) ; précédent pretrain (`docs/DEVIATIONS.md:750-759`) | aucun lecteur `pre_monitor` ; disposition INCONNUE | Codex ingénierie | note de conception par jeu ; sonde de disposition sous GO | fixture à cheval sur 2020-01-01 refusée avant lecture | GO ingénierie ; chercheur si re-matérialisation |
| G4 octets | F ne lit rien (`tools/freeze_config.py:38-40`) ; empreintes seulement journalisées (§2.2–2.4) | aucune empreinte de segment déclarée | Codex + chercheur | schéma de déclaration de segment PROPOSED | segment altéré d'un octet refusé avant calcul | GO ingénierie ; GO chercheur pour hacher les segments réels |
| G5 J4 | gardes (`tools/freeze_config.py:426-429`, `:433-435`) ; couplage `pre_j4` (`prompts/wrapups/wrapup-21-F.md:152`) | GO J4 | chercheur | aucune ici | — | GO chercheur |
| G6 2020+ | gardes inconditionnelles (§2.1) | E5/E8 absents ; G5 | chercheur ; 22, 25 | aucune ici | — | GO chercheur |
| G7 amont | 16, 17, 19, 23 (`prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_12.md:84-91`) | streams amont | leurs propriétaires | aucune ici | — | GO par stream |
| G8 pré-2020 | critère `e1_cells.csv` bit à bit (`prompts/streams/prompt-21-freeze-runner.md:32`) | aucun mandat | chercheur | liste PROPOSED des variantes candidates | empreintes déclarées reproduites | GO chercheur |
| G9 formats | descripteurs DEFERRED (`docs/sections/benchmark_runner_contract.md:144-152`) | schéma non approuvé | Codex propose, chercheur approuve | exigences PROPOSED (§4) | nul et placeholder refusés | GO documentaire puis ingénierie |
| G10 méthodes | ORIGIN DEFERRED (`docs/sections/benchmark_runner_contract.md:65-72`) ; `sys.path`, `spawn` (§2.1) | mécanismes non choisis | Codex ingénierie | section du futur plan d'implémentation | cible préchargée ou worker hors ROOT refusé | GO ingénierie |

## 4. Fixtures et refus futurs — PROPOSED / NOT EXECUTED
- Aucun dispatch positif avant schéma approuvé et GO d'ingénierie borné séparé (`docs/sections/benchmark_runner_contract.md:441-443`) ; un descripteur nul, une chaîne non vide, un GO haché ou la présence de FROZEN ne qualifient rien (`:153-159`).
- Refus sans schéma, sur fixtures synthétiques sans import de producteur : R1 lignes e1/e3/e10 à descripteurs nuls → PROTOCOL, DATA ou READER (`:463`) ; R2 placeholder (`"TBD"`, chemin ou SHA d'un GO) → même refus ; R3 drapeau géré dans les extras, forme `=` comprise (`:99-101`) ; R4 `--stage jepa`, `--families F2`, bras inconnu, `--quick` non qualifié → ARGV ; R5 `--include-test-window` sur e1/e3/e10 → TARGET (`:194-195`) ; R6 configurations PCA, `ca_tjepa`, `eurofidai_schema` → TARGET (`:171-176`) ; R7 YAML strict (`:451-459`) ; R8 statique : candidats UNQUALIFIED, aucun `run.json` déclaré, aucun répertoire par défaut transmis.
- Exigences minimales de schéma (liste, pas un format) : `protocol` = variante exacte, empreinte de config, plan de holdout, référence d'approbation hachée ; `data` = fichiers consommés et empreintes déclarées, segment par cible, entrées annexes ; `reader` = unité de lecture, refus à 2020-01-01, preuve par processus des octets consommés.
- Fixtures de lecteur, après GO d'ingénierie seulement : panneau factice à cheval sur 2020-01-01, segment altéré d'un octet, sidecar périmé, worker `spawn`.

## 5. E5 : `results/e5/J4_gate.txt` contre espaces exclusifs — décision exacte requise
- Faits : le prompt 22 exécute E5 via le runner et écrit `results/e5/J4_gate.txt` (`prompts/streams/prompt-22-e5.md:17`, `:34`, `:54-55`), routé par `prompts/streams/INDEX.md:107` ; la réécriture proposée vise `results/e5/j4_verdict.json` par un script direct avec `--out` (`prompts/streams/07_STREAM_22_E5_J4_REWRITE.md:3`, `:56`, `:71`) ; le contrat exclut tout répertoire par défaut (`docs/sections/benchmark_runner_contract.md:367`), renvoie le conflit à G1 (`:396-397`) et exige le gel pour tout dispatch (`:545-546`).
- Décision du chercheur, sans défaut : (i) prompt E5 canonique ; (ii) nom et format de l'artefact de porte ; (iii) emplacement : seul un fichier déclaré par la variante E5 sous `results/benchmark_runner/e5/run-<run16>/` et lu via `run.json` respecte le contrat, toute publication sous `results/e5/` exige un amendement du contrat ; (iv) commande consommatrice. Aucun fichier factice, lien ni shim.

## 6. Lectures bornées restantes et faits à contrôler (après GO, lecture seule)
- Relire seulement les plages ancrées ci-dessus ; aucun producteur intégral, fichier de données ou `.npz`.
- Rapporter comme INCONNU : ordre mémoire de `data/derived/d2_us97/ret_wide.npy`, row groups au 2020-01-01, couverture de `chars.parquet`, vacuité possible de `e1_cells` selon les bras.
- Observations shell à rejouer (C8, C10) : absence de `experiments/__init__.py`, `configs/FROZEN.json`, `jepadrift/benchmark_runner.py`, `results/e5/` ; `logs/` ignoré (`.gitignore:9`) ; sidecars `z_*.json` absents du manifeste (grep : 0).

## 7. Propriété, périmètre, séquence
- Codex : `prompts/plans/plan-21-qualification-20261112.md`, `prompts/GO-stream-21-qualification-20261112.md`, revues, registres, Git, `make check`, réindexation (`logs/stream_21_qualification/mission-plan.md:32-34`).
- Claude, après revue, GO documentaire écrit et sortie officielle du mode plan dans cette session : le document et les journaux ignorés `logs/stream_21_qualification/{doc-checks.md,protected.sha256}` (outils natifs). Sur allocation explicite : skill wrap-up, `prompts/wrapups/wrapup-21-qualification-20261112.md` en anglais (six rubriques exactes).
- Séquence : (1) hacher GO, plan canonique, mission, contrat, F, producteurs, configs → journal ; (2) `protected.sha256` (chemins protégés, sorties scellées) écrit avant le document, référence `-newer` ; (3) Write du document ; (4) C1–C10, corrections par Edit, rejeu complet ; (5) `REVIEW_READY stream-21-qualification-20261112 — awaiting Codex review`, puis arrêt.
- Session 19 parallèle : fichiers disjoints, lectures partagées seulement, aucun import ni calcul partagé par les workers ; Codex sérialise les vérifications applicatives sous le verrou existant.

## 8. Vérification : contrôles shell seulement (aucun Python, aucun Git)
```bash
D=docs/audits/stream_21_qualification_20261112.md; L=logs/stream_21_qualification
test "$(wc -l < "$D")" -le 230 && ! awk 'length > 120' "$D" | grep -q . || echo C1-FAIL       # taille, largeur
! grep -nP '[^\x00-\x7F]' "$D" || echo C2-FAIL                                                 # ASCII
for m in UNQUALIFIED DEFERRED PROPOSED 'NOT EXECUTED' OPEN; do grep -q "$m" "$D" || echo "C3-MISS $m"; done
test "$(grep -oE '\bG(10|[1-9])\b' "$D" | sort -u | wc -l)" -eq 10 || echo C4-FAIL               # dix portes
grep -niE '\b(closed|resolved|satisfied|qualified)\b' "$D"                                      # C5 revue manuelle
grep -oE '[A-Za-z0-9_./-]+\.(py|md|yaml|json|txt):[0-9]+(-[0-9]+)?' "$D" | sort -u | while IFS=: read -r f r; do
  test -f "$f" && test "${r#*-}" -le "$(wc -l < "$f")" || echo "C6-BAD $f:$r"; done              # ancres
! grep -nE '/home/|data/raw/eurofidai|d4_eurofidai/' "$D" || echo C7-FAIL                       # chemins privés
for p in configs/FROZEN.json jepadrift/benchmark_runner.py tools/benchmark_runner.py tests/test_benchmark_runner.py \
  results/e5 results/benchmark_runner experiments/__init__.py; do test ! -e "$p" || echo "C8-PRESENT $p"; done
sha256sum results/e2/e2_cells.csv results/e3/e3_overshoot.csv results/pca_drift_benchmark/full_2000_20261101/manifest.json
grep -c $'\r$' results/e2/e2_cells.csv                                                            # C9 : e315e537…, 1ca7c3ae…, 3b2299bc…, 47
sha256sum -c "$L/protected.sha256" && find . \( -path ./.venv -o -path ./external -o -path ./data \) -prune \
  -o -type f -newer "$L/protected.sha256" -print                                                 # C10 : document et journaux seuls
```
Limite : C6 vérifie l'existence et les bornes des ancres à chemin complet, pas la correspondance du contenu ; celle-ci repose sur les relectures ciblées de cette session.

## 9. Risques
- Dérive des ancres si la base bouge : rejeu C6 et relecture ciblée avant réception.
- Lecture du document comme levée de porte : colonne `OPEN`, revue C5.
- Confusion déclaré/consommé : vocabulaire `declared` / `consumed`, aucun octet de données ouvert.
- Budget de 230 lignes : priorité à la matrice et aux cartes ; prose coupée.
- Glissement vers une décision de schéma : exigences PROPOSED, aucun format arrêté.

## 10. Choix en attente
Hypothèses soumises à Codex (défaut entre parenthèses) :
- H1 ancres relues à `891cfa5`, contrat cité par ses lignes (oui).
- H2 `data/derived/MANIFEST.json` lu comme métadonnée de POLICY ; aucun en-tête `.npy` ni métadonnée Parquet ; INCONNUS conservés (oui).
- H3 intégrité sans Git : `protected.sha256` et `find -newer`, aucun `git` par Claude (oui ; Codex peut autoriser un `git status` en lecture).
- H4 constats `spawn` et `sys.path` portés en G3, G4 et G10 (oui).
- H5 E10 `F1` / `F1 F1` et E1 ordre de `--arms` rapportés comme faits, sans recommandation (oui).
Décisions à exposer dans le document, sans défaut appliqué (chercheur sauf mention) :
- Q1 (G9) schémas `protocol`, `data`, `reader` et format de preuve (proposition Codex, approbation chercheur).
- Q2 (G2, G8) holdout admissible pour des cibles rétrospectives pré-2020 ; variantes à qualifier, s'il y en a.
- Q3 (G3, G4) stratégie de lecteur : re-matérialisation `pre_monitor`, row groups ou décalages `.npy` ; déclaration des empreintes de segment.
- Q4 entrées hors POLICY (CSV d'audit, sidecars) : descripteur `data` ou POLICY v2, donc nouveau vérificateur.
- Q5 admissibilité pré-J4 de métadonnées postérieures à 2019 (phases déclarées jusqu'en 2025).
- Q6 (G1) E5 : §5 (i)–(iv).
- Q7 (G10, Codex) `--jobs > 1` sous runner : interdit, ou couvert par ORIGIN et par une preuve de lecteur par worker.

## Décision GO intégrée — 12 novembre 2026

GO Codex au titre du mandat documentaire délégué, sans signature ni GO scientifique du chercheur. Le présent plan canonique et cette section priment sur la proposition native v0, conservée à l'identique dans le journal ignoré. Le GO séparé enregistre son SHA-256 avant toute rédaction.

H1, H2, H4 et H5 sont retenues sous les précisions ci-dessous. H3 est remplacée : les lectures Git `git status --porcelain=v1 --untracked-files=all`, `git diff --quiet HEAD` et `git diff --name-only HEAD` sont permises avec `GIT_OPTIONAL_LOCKS=0`. Toute mutation Git reste interdite. Q1–Q7 restent OPEN ; leur énumération dans le document ne les tranche pas, Q7 relevant du futur plan technique Codex.

Précisions obligatoires de réception :

1. Le précédent Fortran interdit le préfixe contigu supposant l'ordre C ; il ne démontre pas l'impossibilité de tout lecteur borné. Aucun en-tête de données n'est ouvert ici.
2. L'analyse de `spawn` est conditionnelle aux tâches qui rappellent les chargeurs. Ne pas attribuer une lecture réelle à toutes les tâches, notamment les contrôles D5 purs. Le fait établi est l'absence de qualification des enfants par un contrôle ORIGIN limité au parent.
3. Les contrôles du §8 sont une liste d'observations à juger, pas un programme dont le statut 0 certifierait tout. Remplacer les branches `echo ... FAIL` par des échecs explicites ou consigner chaque résultat et tout FAIL ; aucun PASS global si un contrôle échoue. La vérification du sens des ancres reste une relecture ciblée.
4. `find -newer` est un diagnostic complémentaire. Il ne détecte pas une suppression ou une date restaurée et ne remplace ni les empreintes initiales ni le contrôle du périmètre Git. Exclure de son constat les seuls journaux propres, les fichiers Codex déclarés et les caches de validation connus ; signaler tout autre changement.
5. La sortie future d'une variante dépend exactement des bras, du contenu et des branches du producteur. Ne qualifier aucune variante à partir de cette cartographie. Tous les schémas restent PROPOSED, toutes les portes OPEN et toutes les cibles UNQUALIFIED.
6. Un échec de lecteur qualifié avant calcul serait DATA selon le futur contrat ; une exception du producteur actuel reste TARGET_FAILED. Ne pas confondre les deux phases.
7. Document anglais de 230 lignes au maximum, contrôles shell, aucune statistique nouvelle. Budget de rédaction : 30 minutes ; contrôles shell bornés, trois tentatives maximum pour un même défaut d'infrastructure, puis arrêt déclaré. Toute question scientifique nouvelle est exposée comme OPEN, sans recherche ou implémentation supplémentaire.

Périmètre : le seul document `docs/audits/stream_21_qualification_20261112.md`, les journaux ignorés propres et, après réception et allocation explicite, le wrapup anglais à six rubriques. Sortie officielle du mode plan dans la même session, sans bypass ; Codex vérifie le mode avant le signal de rédaction. Aucun runner, lecteur, fixture, schéma activé, FROZEN, donnée réelle, expérience, changement de source ou de mémoire n'est autorisé.
