# Plan natif — E4 production (stream 19), révision v1 — 2026-11-12

PLAN ONLY. Révise v0 (`e536126b…d8e9cb`) selon `prompts/NO-GO-stream-19-e4-production-20261112-v0.md` (R1–R7, lu
intégralement). Aucun code, test, pilote ni Git avant : GO technique écrit, sortie officielle du mode plan, vérification
du mode et signal distinct de Codex. GO 1 accordé ; GO 2 accordé sous conditions, **NON ACTIVÉ** : refus par défaut.

## 0. Contexte

- Base `b18d8e5`, branche `stream-19-e4-production-20261112`, worktree isolé. Sources lues : mission-plan, GO full, revue
  indépendante pré-plan, NO-GO v0, GO-wave-23-27 (vague différée jusqu'à E4 clos et publié), audit pilote coût, protocole
  §5–8 et §12, `plan-19-e4-code`, `experiments/e4_alignment.py` intégral, `pdb` ciblé, `save_fair_csv`, `.gitignore`.
- Écart : le prototype n'a ni blocs, ni barrière de seuils persistée, ni fusion, ni reprise de campagne. `_cell` et
  `run_cells` retiennent toutes les lignes et les J_k (e4:449-494). `partition_dir` n'accepte qu'un `:`. `Store.get`
  n'est ni atomique ni vérifié. `--mode full` sort en code 3.
- Cible : script de production testé, pilote technique, bilan CPU/RSS/disque ; puis, après activation prouvée seulement,
  campagne, analyse, publication vérifiable, rapport. Protocole, I*, grille, méthodes et critères inchangés.

## 1. Hypothèses et défauts (arbitrages techniques recevables selon le NO-GO)

- H1 Aucun fichier existant de code ou de config n'est modifié (`e4_alignment.py` e457eb…, `e4_alignment.yaml` 5b9086…,
  `pipelines.py`, `pca_drift_benchmark.py`). Le nouveau script importe `e4` et réplique les deux boucles de `_cell` sous
  le témoin d'octets T3.
- H2 Campagne sérielle : une invocation à la fois sous le verrou partagé, sans worker. Mono-fil (BLAS à 1), donc
  CPU ≤ mur ≤ 1800 s par invocation : c'est la borne de coût de la prochaine invocation.
- H3 Géométrie : bloc 250, cible ≤ 900 s par bloc ; 125 si la prévision du pilote l'exige avant activation, sinon STOP.
  Le bloc retenu est figé dans `campaign_plan.json` et absent de l'identité scientifique.
- H4 Mode et domaine sont distincts : `full`→`science` ; `production_pilot`→`pilot` ; `cost_fixture`→`pilot`.
  Aucun domaine ni aucune clé du producteur historique n'est ajouté ou modifié.
- H5 Racines de travail ignorées par Git : `logs/stream_19_e4_production/{full_20261112,prodpilot_20261112,attempts,
  receipts}` ; publications vérifiées : `results/e4_alignment/{full_20261112,production_pilot_20261112}`.
- H6 Réserve disque de 1 GiB ; alerte à 45 MiB par fragment ; réserve de prévision de 3 blocs interrompus. Les volumes
  restent ESTIMATE jusqu'au pilote.
- H7 Claude implémente (TDD, tests ciblés). Codex exécute `make check`, les reçus, le pilote, l'activation, la campagne et
  Git, sauf signal contraire.

## 2. Fichiers

- Nouveaux : `experiments/e4_production.py` et `tests/test_e4_production.py`.
- `docs/DEVIATIONS.md`, ajouts en français : `C-e4-production-blocks` (blocs, fit reconstruit, barrière globale,
  sérialité) et `C-e4-production-storage` (fragments gzip par cellule, SHA canonique non compressé, lignage).
- Après pilote (Codex) : `docs/audits/stream_19_e4_production_pilot_20261112.md`. Après campagne : rapport, MAPPING,
  wrapup `prompts/wrapups/wrapup-19-e4-production-20261112.md`.

## 3. Identité, identifiants, géométrie (R1)

- `production_identity(cfg, mode, space) -> dict` : corps de `e4.session_identity(cfg, mode)`, auquel s'ajoutent
  `code["experiments/e4_production.py"]`, `config_file_sha256` et `space`.
  - `session_id = sha256(pdb.canon(body))` ; le couple mode/domaine doit appartenir à H4, sinon ValueError.
  - Hors identité : bloc, ordre, processus, horodatage, RSS, chemins absolus.
- `block_ranges(n, block) -> list[tuple]` : `[(s, min(s + block, n)) for s in range(0, n, block)]`. Pas de queue vide,
  y compris si n est divisible ; `block` doit être un entier ≥ 1.
- `parse_pid(pid, cfg, mode) -> dict` : regex ancrée sur `[a-z0-9_-]`, bornes vérifiées avant tout chemin. Formes :
  - science et cost_fixture : `scalar_cal`, `fit_<bg>_N<N>`, `calmax_<bg>_N<N>_r<ssss>-<tttt>`, `thresholds`,
    `trials_<bg>_N<N>_<holdout|alternative>_r<ssss>-<tttt>`, `merge`, `analysis` ;
  - production_pilot seulement : `cost_<bg>_N<N>_<calibration|holdout|alternative>`.
  Tout identifiant `r` doit appartenir à `block_ranges` du plan figé. Les ids sans `:` passent tels quels dans
  `e4.partition_dir`.
- `plan_partitions(cfg, mode, block, fit_status) -> list[str]` (ordre §4). Les calmax ne sont planifiés que pour les
  cellules au fit COMPLETE et OK ; une cellule refusée garde EW/O-dir et n'a aucun calmax. La borne d'invocations
  `K = |plan_partitions(…, toutes cellules OK)|` vaut 354 au bloc 250 et 690 au bloc 125.
- `--phase plan` écrit atomiquement `campaign_plan.json` = {session_id, mode, block, K, n par rôle}. Une relance avec un
  autre bloc ou une autre identité est refusée (code 5). `next` et `verify` lisent ce fichier ; `--block` n'est accepté
  que par `plan`.
- Écriture par `e4.run_partition(root, pid, identity, compute)`, réutilisé tel quel : tmp puis `os.replace`,
  SKIPPED_COMPLETE vérifié par SHA, `PartitionMismatch`, restes `.tmp-*` jamais lus. En production, un bloc est COMPLETE
  ou absent : toute exception (ResourceBlocked, SIGALRM, OSError dont ENOSPC, kill, interruption fixture) laisse au plus
  un tmp, jamais de final.
- `load_partition(root, pid, identity)` exige, avant usage : session, statut COMPLETE, ensemble exact de fichiers,
  SHA de fichier et SHA canonique décompressé.

## 4. Phases scientifiques (cfg complet, i global, rôles et domaines inchangés)

Dépendance absente → code 5, rien n'est écrit. Ordre :
1. `scalar_cal` : `e4.scalar_calibration(cfg, space)`, une fois. Champs dans `objects` (JSON, types exacts) et dans
   `scalar_calibration.csv` (1 ligne : status, threshold_rule, n_cal, maxima_sha256, rank_r, threshold_hex,
   calibration_alarms, calibration_hash).
2. `fit_<bg>_N<N>` : `e4.fit_cell(cfg, bg, N, space)`, sur les seules lignes `fit` i=0 ; `EigenTieUnresolved` donne
   `EIGENVALUE_TIE_UNRESOLVED`. Sortie `cell.csv` (CELL_COLUMNS) ; objects = cinq empreintes et le statut.
3. `calmax_*` (cellules OK) : recalcule `fit_cell` et exige l'égalité des empreintes avec `fit_*`. Pour i ∈ [s,t) et
   m ∈ DICTIONARY : `e4.method_log_path(m, cell, e4.role_path(cfg, space, bg, "calibration", i, N),
   e4.coins_rec(cfg, space, "calibration", i)).max()`. Sortie `maxima.csv.gz` [background, N, method, replicate,
   max_log], triée (method, replicate).
4. `thresholds`, barrière globale : exige scalar_cal, les 14 fit et le pavage exact `block_ranges(n_cal)` de chaque
   cellule OK.
   - Assemble le vecteur float64 indexé par i = 0..n_cal−1 et contrôle la couverture ; `e4.cell_calibration`.
   - Les lignes reproduisent `cal_rows` de `_cell` : scalaires = copie commune ; méthodes de base d'une cellule refusée
     = status EIGENVALUE_TIE_UNRESOLVED.
   - Sorties `calibration.csv` (CAL_COLUMNS) et `cells.csv` ; objects = SHA des partitions consommées.
   Aucun chemin holdout ou alternative n'est simulé avant ce COMPLETE.
5. `trials_*` : exige `thresholds` (SHA de `calibration.csv` consigné) ; recalcule le fit et le confronte à `cells.csv`.
   - `h = {m: float.fromhex(threshold_hex) si OK}` ; méthodes = METHODS si OK, sinon EW et O-dir.
   - Boucle de `_cell` pour chaque i global : `u = residual_direction(direction_draw(cfg, space, i), N)` ;
     `X = role_path(...)`, plus `drift_scale(cfg)·u` en alternative ; `rec = coins_rec(...)`.
   - Un appel `e4.method_log_path` par (chemin, méthode) : pièces neuves et EWMA P3-CS redémarrée à chaque chemin.
   - Lectures : `predictive_rank` si m ∈ h ; `anytime_valid_horizon` toujours.
   - Alternative OK : `e4.oracle_diagnostics` donne `diagnostics.csv.gz` et `axes.csv.gz`. J est un tableau (t−s, N)
     converti en DataFrame colonne par colonne, sans liste de dicts. `trials.csv.gz` est trié TRIAL_KEYS.
6. `merge` : exige les pavages holdout et alternative. Par cellule triée (background, N) :
   - trials : chargement des blocs (≤ 48 000 lignes), clés uniques et couverture vérifiées, tri TRIAL_KEYS stable
     (concaténer par start n'est pas canonique), fragment `trials/<bg>_N<N>.csv.gz` ;
   - `calibration_maxima/`, `diagnostics/`, `diagnostics_axes/` : copie ligne à ligne en flux par start croissant,
     ordre canonique pour leurs clés. Le flux vérifie N axes 0..N−1 par réplicat alternatif OK. Jamais de `read_csv`.
   - `manifest.json` (logique) : par table, fragments ordonnés {fichier, lignes, sha256_csv} et `sha256_whole`
     (en-tête + corps, égal au CSV du prototype).
   - `lineage.json` (physique) : chaque `partition.json` recopié tel quel, plus le lien bloc → fragment (filtre
     rôle/replicate ∈ [s,t), lignes, sha256_csv du bloc). Aucune table entière n'est matérialisée.
7. `analysis` : lit les fragments trials (`round_trip`). Contrôle unicité de TRIAL_KEYS, effectif n_role par
   (bg, N, méthode, rôle, lecture) et replicate = 0..n−1, refus sinon. Puis `e4.analyse(t_lecture, cfg, space,
   reading)` pour chaque lecture et `e4.holdout_fpr`. Sorties : `holdout_fpr.csv`, `{cells,contrasts,warnings}_<reading>
   .csv`. Borne déclarée : ≤ 672 000 lignes trials en RAM, J_k jamais chargés. Aucun nouveau critère ; NOT_IDENTIFIED,
   FPR_ABOVE_NOMINAL, `fpr_comparability`, ORACLE_*, INFO_GAUSS_PROXY_T7 visibles.

Bloc absent, dupliqué, chevauchant, vide ou étranger : `IncompleteWork`, code 5. Jamais NOT_IDENTIFIED, jamais
d'alarme fabriquée. `tiles(found, block_ranges(n, block))` exige l'égalité exacte des ensembles.

## 5. Stockage FAIR

- `write_table(df, path_gz) -> dict` : `pipelines.save_fair_csv(df, tmp.csv)` → SHA-256 et taille canoniques →
  `gzip.GzipFile(filename="", mtime=0, compresslevel=6)` en flux → suppression du `.csv` ; espace libre contrôlé avant
  chaque écriture. Renvoie {rows, sha256_csv, bytes_csv, sha256_gz, bytes_gz}. Petites tables : CSV non compressés.
- RAM des J_k bornée par un bloc (250·500 = 125 000 lignes). ESTIMATE : axes ≈ 250 Mo canoniques, 40–60 Mo gz, ≤ 15 Mo
  gz pour N=500 ; trials ≈ 45 Mo canoniques, ≈ 8 Mo gz ; maxima 84 000 lignes. Fragment > 45 MiB refusé avant publication.

## 6. Tentatives et compteur CPU (R2)

- Répertoire commun au pilote et à la campagne, en ajout seul : `logs/stream_19_e4_production/attempts/A<7 chiffres>/`.
  - Réservation par `mkdir` atomique (échoue si l'identifiant existe) ; jamais réécrit ni réutilisé. Les noms ne
    portent aucune statistique.
  - Fichiers : `cmd.txt` (arguments relatifs, écrit avant lancement) ; `time.txt` (`/usr/bin/time -o`, propre à la
    tentative) ; `exit.txt` (écrit par l'hôte après le retour de `time` : finalisation).
- États : RUNNING (sans `exit.txt`, identifiant = `E4_ATTEMPT_ID` actif) ; MEASURED (`exit.txt` + `time.txt` analysable) ;
  INTENDED_FIXTURE_INTERRUPT (rc 7, `--fixture-interrupt --mode cost_fixture` dans `cmd.txt`) ; UNKNOWN (autre cas).
- `ledger(attempts_dir, prior_cpu_s=645.23)` somme les 645,23 s antérieurs (source `external_attempts.csv` 45b797…) et
  toutes les tentatives MEASURED : échecs, rejeux, SKIPPED, refus, tuées sans CSV, interruptions voulues. Toute UNKNOWN
  hors tentative active entraîne `GateStop`, jamais zéro CPU.
- `gate(cfg, mode, root, forecast)` s'exécute dans le processus avant tout calcul. `E4_ATTEMPT_ID` est obligatoire en
  CLI (sinon code 6) ; seule cette tentative est exclue. STOP code 6 si :
  - ledger + 1800 s (prochaine invocation, H2) + coût prévu restant après elle > 86 400 s ;
  - espace libre − octets prévus (tmp compris) < 1 GiB ;
  - pic RSS mesuré > 8 GiB ;
  - tentative précédente non MEASURED ou rc ∉ {0, 10}, sauf INTENDED_FIXTURE_INTERRUPT.
  Une mesure est finalisée avant que la suivante soit autorisée.
- Gardes internes : `e4.guard` par groupe de 8 chemins, `signal.alarm(1800)`, espace libre avant chaque écriture et
  avant `os.replace`. OSError/ENOSPC → code 4, aucun COMPLETE. Restes `.tmp-*` journalisés ; suppression par Codex
  seulement, chemins exacts, racine propre. Aucun fichier étranger purgé.
- Disque observé : 2 948 812 800, puis 2 578 821 120, puis 2 583 306 240 octets (`/dev/md1` à 100 %). L'espace n'est pas
  réservé : contrôle avant activation, avant chaque allocation et avant publication.

## 7. Pilote technique (avant activation)

### P1 — noyaux réels mesurés, entrée de coût distincte (R3)

- `cost_kernels(cfg, bg, N, role, replicates, meter)`, CLI `--phase cost-kernels --mode production_pilot --cell
  <bg>_N<N> --role <role> --replicates 40`. Domaine `pilot` uniquement ; partition `cost_<bg>_N<N>_<role>`.
  - Ne lit ni n'écrit aucune partition scientifique : la barrière `thresholds` n'est pas touchée.
  - Rôle calibration : fit + chemins log des dictionnaires + `e4.cell_calibration` sur les 40 maxima pilot (mesuré,
    jeté).
  - Rôles holdout et alternative : fit + 6 méthodes + deux lectures, comparées à `COST_FIXTURE_LOG_THRESHOLD =
    log γ_H` pour toutes les méthodes. Ce seuil explicite existe seulement dans cette entrée. Il diffère de
    `_pilot_cell`, qui calibre les dictionnaires et réserve le repli aux scalaires ; ici le coût de comparaison ne dépend
    pas de la valeur.
  - Alternative : `oracle_diagnostics` et tableau J_k construits puis jetés.
- Neuf invocations : {gaussian_N8, gaussian_N500, t7_N500} × {calibration, holdout, alternative}. Stades écrits dans
  `cost.csv` (liste blanche) : `startup`, `identity`, `fit_cell`, `paths:<m>:<role>`, `dict_calibration`,
  `readings:<role>`, `oracle_diagnostics`, `j_k_table`, `io`. Aucune charge utile n'est écrite. ESTIMATE ≈ 300 CPU s.

### P2 — mode cost_fixture, domaine pilot, effectifs complets (R4)

- `fixture_counts(cfg) = {calibration: n_cal, holdout: n_hold, alternative: n_alt}` (2000), passés partout
  explicitement, jamais pilot_n.
- `fixture_values(L, label) = 1 + ((arange(L) + pdb.label_code(label)) · 0.6180339887498949) mod 1` : réels finis,
  distincts, 17 chiffres, sans PRNG ni domaine nouveau.
- Générateurs COMPLETE aux schémas, types, lignes et dépendances exacts, via les mêmes partitions et la même géométrie
  (bloc 250) :
  - scalar_cal : `e4.cell_calibration(fixture_values(n_cal))` ;
  - 14 fit : OK, empreintes `sha256("COST_FIXTURE|fit|bg|N")`, k_mp 0, mp_count_total 1 ;
  - calmax : 3 × (t−s) lignes ;
  - trials : first_hit H/2 en alternative et −1 en holdout (comme `analysis_fixture`), 12 lignes par réplicat,
    diagnostics typés, N axes par réplicat. Les claim_flag suivent le schéma ; l'étiquette COST_FIXTURE vit dans
    le mode, l'identité et chaque manifeste.
- Phases réelles inchangées : `thresholds` (vraie barrière de rang sur les maxima indexés), `merge`, `analysis`
  (`e4.analyse(t, cfg, "pilot", reading, n={alternative: n_alt, holdout: n_hold})`), `publish` vers
  `logs/.../prodpilot_publish/`.
- Interruption déterministe : `--fixture-interrupt`, refusé hors cost_fixture.
  1. `FixtureInterrupt` (rc 7) après écriture des charges dans le tmp, avant `partition.json` et `os.replace`.
  2. Observation par l'hôte : `ls -d <pid>.tmp-*` non vide et `test ! -e <pid>`, sortie journalisée.
  3. La boucle recalcule (rc 0) ; le reste est intact ; les deux tentatives sont comptées.
- Reprise :
  - `--phase replay-check` vérifie toutes les partitions et mesure le coût de vérification ;
  - trois `--phase run` rejoués (fit N500, calmax N500, trials alternative N500) doivent répondre SKIPPED_COMPLETE avec
    octets inchangés (instantané SHA).
- Mesures : CPU, mur et RSS par tentative ; octets canoniques et gz par table ; `du -sb` par phase (blocs, fragments,
  staging, publication, restes). Les objets Git sont estimés comme la somme des octets publiés (ESTIMATE, aucun Git).
- Rapport publié sous `results/e4_alignment/production_pilot_20261112/`, mécanisme §9, label
  `COST_ONLY_NOT_SCIENTIFIC_E4` : `attempts.jsonl`, `stage_costs.csv`, `volumes.csv`, `partition_forecast.csv`,
  `forecast.csv`, `unmeasured.csv`. Les fixtures (fichiers propres) sont supprimées par Codex après le reçu.
- `forecast_production(...)`, valeurs finies et ≥ 0, recoupées avec le ledger et les volumes :
  - par partition : fixe (startup + identité + fit_N, P1) + pente (max entre pilote antérieur et P1) × bloc +
    sérialisation (P2) ;
  - plus thresholds, merge et analysis à volume complet ;
  - plus 3 blocs interrompus.
  Total = ledger + prévision ≤ 86 400 s, sinon STOP avec les replis listés, non appliqués.

## 8. Reçus et activation (R5)

- `--phase receipt --kind tests|make_check|pilot|nonleak` construit `logs/.../receipts/<kind>.json` à partir des
  artefacts réels. Chaque reçu porte `session_id` (identité `full` courante), commandes, codes de retour, SHA des
  journaux bruts et inventaires.
  - tests : JUnit XML de `pytest --junitxml`. Le test `test_identity_stamp` y inscrit `e4_session_id` via
    `record_testsuite_property`. Le reçu exige :
    - égalité de ce `e4_session_id` à l'identité courante ;
    - présence de chaque test requis (§10), passé, non sauté ;
    - zéro failure ou error.
  - make_check : rc 0, SHA du log, deux synthèses pytest analysées (0 failed/error, seuls les skips D4 attendus).
  - pilot : identités production_pilot et cost_fixture égales aux identités recalculées (sinon preuve périmée). Il
    vérifie aussi :
    - neuf P1 MEASURED rc 0 ;
    - toutes les partitions P2 COMPLETE selon `plan_partitions` ;
    - interruption prouvée (rc 7, tmp observé, recalcul rc 0) et rejeux SKIPPED ;
    - SHA des tables CPU/RSS/volumes/prévision.
  - nonleak : ensembles fermés de fichiers et de colonnes par sortie du pilote publié ; mode fixture vérifié.
    Paramètres et coûts autorisés ; toute colonne hors ensemble est refusée.
- `--phase activate --mode full --technical-go <GO>` (commande explicite de Codex) relit et revalide tous les reçus. Il
  contrôle aussi :
  - config 5b9086…, prototype e457eb…, protocole cd786a…, GO full et GO technique (SHA réels) ;
  - seed_plan ;
  - prévision finie ≤ cap et égale au ledger recalculé ;
  - disque : libre − empreinte prévue (blocs + fragments + publication + objets Git + tmp max) ≥ 1 GiB.
  Il écrit `logs/stream_19_e4_production/activation-full-20261112.json`, sans écrasement divergent, puis imprime son SHA.
- `check_activation(path, identity)` s'exécute à chaque invocation science, avant toute écriture, et revérifie :
  - SHA des reçus et des feuilles ;
  - égalité des identités ;
  - contenus (JUnit, phases, valeurs finies, sans NaN).
  Échec, absence ou booléen seul → code 3. Un journal RED historique ou une phrase n'est jamais une preuve.

## 9. Boucle hôte et publication (R1, R2, R7)

```sh
E="OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg"
P=experiments/e4_production.py; J=logs/stream_19_e4_production; W=$J/full_20261112; A=$J/activation-full-20261112.json
L="$(git rev-parse --path-format=absolute --git-common-dir)/../logs/.jepa_execution.lock"
exec 9>"$L"; flock -n 9 || exit 1; mkdir -p "$J/attempts"
attempt() {
  k=1; until mkdir "$J/attempts/$(printf 'A%07d' $k)" 2>/dev/null; do
    [ -e "$J/attempts/$(printf 'A%07d' $k)" ] || return 8; k=$((k+1)); done; id=$(printf 'A%07d' $k)
  printf '%s\n' "$*" > "$J/attempts/$id/cmd.txt"
  /usr/bin/time -f '%U %S %e %M %x' -o "$J/attempts/$id/time.txt" timeout --signal=TERM --kill-after=10s 1790s \
    env $E E4_ATTEMPT_ID="$id" .venv/bin/python "$P" "$@"
  rc=$?; printf '%s\n' "$rc" > "$J/attempts/$id/exit.txt"; return "$rc"
}
K=$(attempt --phase plan --mode full --root "$W" --activation "$A" --block 250) || exit $?
for i in $(seq 1 $((K + 1))); do attempt --phase next --mode full --root "$W" --activation "$A"; rc=$?
  [ "$rc" -eq 10 ] && break; [ "$rc" -eq 0 ] || exit "$rc"; done
[ "$rc" -eq 10 ] || exit 9
attempt --phase verify --mode full --root "$W" --activation "$A" || exit $?
attempt --phase publish --mode full --root "$W" --activation "$A" --to results/e4_alignment/full_20261112 || exit $?
```
- Codes : 0 partition traitée ; 10 plus rien à faire ; 3 activation refusée ; 4 ressource/ENOSPC ; 5 refus (pavage,
  dépendance, divergence) ; 6 STOP gate ; 7 interruption fixture ; 8 réservation d'identifiant impossible ; 9 borne K+1
  épuisée sans 10. Aucun échec ne sort en succès. `verify` exige l'ensemble exact de `plan_partitions` selon les fits
  réels. Le pilote réutilise `attempt` (`--mode cost_fixture`, sans activation ; l'étape d'interruption exige rc 7).
- Publication, avec une liste blanche exacte et fermée :
  - `PUBLISHED.json`, `session.json`, `campaign_plan.json`, `manifest.json`, `lineage.json` ;
  - `scalar_calibration.csv`, `calibration.csv`, `cells.csv` ;
  - `calibration_maxima/`, `trials/`, `diagnostics/`, `diagnostics_axes/` (`<bg>_N<N>.csv.gz`) ;
  - `analysis/*.csv` ;
  - `ledger/attempts.jsonl` (sans perte : cmd, time, rc, état) et `ledger/cpu_ledger.csv` ;
  - `activation/activation.json` et `activation/receipts/*.json`.
  Les journaux bruts restent locaux, déclarés par SHA dans les reçus et non requis pour l'audit structuré.
- Mise en scène dans `$J/publish.tmp-<pid>/`, puis `verify_publication(staged)`, puis écriture de `PUBLISHED.json`
  (inventaire SHA et octets) en dernier, puis `os.replace` vers la cible. `verify_publication` contrôle :
  - l'ensemble exact des fichiers ; SHA et octets ; ≤ 50 Mo par fichier ;
  - `sha256_whole` ;
  - le sha256_csv de chaque bloc, recalculé depuis les fragments selon `lineage.json` ;
  - les seuils recalculés depuis `calibration_maxima/` (égaux à `calibration.csv`) ;
  - les reçus et `session.json`.
- Cible existante identique → SKIPPED ; cible différente → refus. Une copie interrompue laisse un staging, jamais de
  cible ni de marqueur. Reprise : nouveau staging.
- `--phase verify-publication --root <cible>` audite à partir des seuls artefacts publiés et des sources commitées.

## 10. Tests TDD (RED observé puis GREEN ; N ≤ 8, H ≤ 60, n ≤ 40, prefix_k ≤ min N, n_cal ≥ 19)

Noms requis par le reçu tests :
1. `test_block_ranges_cover_exactly` : n divisible, non divisible, block=1, block=n, dernier réplicat, aucune queue vide.
2. `test_pid_parser_refuses_unsafe_ids` : `:`, `/`, `..`, bg/N hors cfg, bornes hors `block_ranges`, mode interdit.
3. `test_production_matches_prototype_bytes` : `sha256_whole` des trois tables longues et octets de calibration, cells
   et analyse égaux à `e4.write_tables(e4.run_cells(cfg))` et `e4.analyse`, pour les deux lectures.
4. `test_logical_outputs_invariant_to_geometry_order_and_processes` (R6) : blocs {1, 3, n}, ordre inverse, 3 processus
   spawn → `manifest.json`, tables canoniques et analyse identiques octet pour octet. Seuls `lineage.json`, les records
   et les coûts diffèrent. Une autre graine change les octets.
5. `test_refused_basis_cell_matches_prototype` : fit monkeypatché, aucun calmax, EW/O-dir seuls, octets du prototype.
6. `test_resume_skips_complete_without_recompute` : compteur de compute nul, empreintes inchangées.
7. `test_fixture_interrupt_leaves_tmp_and_recomputes` : rc 7, tmp sans final, recalcul, reste intact.
8. `test_tiling_refuses_holes_overlaps_duplicates_extras` : trou, chevauchement, doublon, étranger, dernier réplicat
   manquant, bloc vide → code 5, aucune sortie.
9. `test_divergences_are_refused_without_mutation` : bloc altéré, SHA de calibration, fit ≠ cells, session étrangère,
   `campaign_plan` à bloc différent.
10. `test_threshold_barrier_blocks_monitoring` : trials avant thresholds, thresholds avant pavage, calmax d'une
    cellule refusée.
11. `test_fair_fragments_and_maxima_order` : octets `save_fair_csv`, gz déterministe, `round_trip` exact ; hash des
    maxima assemblés par i indépendant de l'ordre des blocs.
12. `test_axes_are_streamed_and_complete` : `read_csv` intercepté sur les axes ; axe manquant → refus.
13. `test_analysis_checks_coverage_and_bounds` : doublon ou réplicat manquant refusé avant `e4.analyse`.
14. `test_activation_requires_bound_receipts` : absence, booléen, SHA valide mais identité périmée, phase pilote
    manquante, test requis absent ou sauté, JUnit RED, coût NaN ou négatif, prévision non réconciliée → code 3 ; fixture
    valide (constantes monkeypatchées) acceptée.
15. `test_cost_kernels_stay_outside_science` : domaine science refusé, aucune partition scientifique lue ou écrite,
    liste blanche de `cost.csv`.
16. `test_cost_fixture_runs_every_phase_with_full_counts` : effectifs explicites, pas de pilot_n ; `e4.analyse` en
    domaine pilot avec n explicite ; mode ≠ domaine dans l'identité.
17. `test_attempt_ledger_is_append_only_and_stops_on_unknown` : reprise conservant les anciens octets, tuée sans CSV
    comptée, active exclue seulement si identifiée, ancienne inachevée → 6, 645,23 inclus.
18. `test_gate_budget_disk_and_previous_exit` : prochaine invocation plus reste > cap ; disque < réserve ; rc 124 →
    6 ; rc 7 voulu accepté.
19. `test_enospc_never_completes` : ENOSPC simulé dans `write_table`, `os.replace` et publication.
20. `test_publication_is_closed_verified_and_atomic` : fichier en trop ou manquant, staging interrompu, cible
    divergente, seuils recalculés depuis les maxima publiés.
21. `test_scientific_route_reads_no_data_file` et aucun `np.random.seed` global.
22. `test_identity_stamp` : écrit `e4_session_id` dans le JUnit.

## 11. Commandes de vérification (après GO technique)

- `env $E .venv/bin/python -m pytest tests/test_e4_production.py tests/test_e4_alignment.py -q
  --junitxml=logs/stream_19_e4_production/receipts/junit-e4.xml` (< 60 s visé), puis `make check` par Codex.
- `sha256sum experiments/e4_alignment.py configs/e4_alignment.yaml` : doivent rester e457eb… et 5b9086….
- `git status --porcelain` : seuls le script, ses tests et `docs/DEVIATIONS.md`.
- Pilote : la fonction `attempt` du §9 pour P1, puis P2 (plan, boucle, interruption, rejeux, verify, publish), puis
  reçus et `verify-publication` du rapport pilote.

## 12. Après campagne (Codex)

- Rapport en anglais : MESURÉ / THÉORIQUE / limites ; deux lectures séparées ; toutes les cellules et tous les statuts ;
  FPR individuels, Wilson, RMST, Δ/Δ1/Δ2 sur la grille entière ; censure à 239 et 500 telle quelle ; I* t7 =
  INFO_GAUSS_PROXY_T7 ; SHA de l'activation et des reçus cités.
- MAPPING, wrapup, réindexation sans résumé IA, `make check`, contrôle de plage (≤ 50 Mo, aucun chemin EUROFIDAI ni
  absolu), `git add -f` documenté pour les `.csv.gz`. E4 n'est clos qu'après publication ou arrêt documenté ; la vague
  23/27 reste différée jusque-là.

## 13. Correspondance NO-GO v0

| R | Correction | Sections |
|---|---|---|
| R1 | `block_ranges` sans queue vide ; K dérivé du plan (354/690) ; code 10 + `verify` exigés ; code 9 si borne épuisée | §3, §9, T1, T8 |
| R2 | tentatives `mkdir` en ajout seul ; RUNNING/MEASURED/UNKNOWN ; active identifiée ; inconnue → STOP ; budget prochaine + reste | §6, §9, T17, T18 |
| R3 | `cost_kernels` distinct, seuil fixture explicite et local, barrière intacte ; neuf invocations décrites | §7 P1, T15 |
| R4 | mode ≠ domaine ; domaine pilot + n explicite ; fixtures COMPLETE pour toutes les phases ; interruption rc 7 déterministe | §7 P2, T7, T16 |
| R5 | reçus structurés liés à l'identité ; JUnit avec tampon ; phases, couverture, coûts finis réconciliés ; activation explicite | §8, T14, T22 |
| R6 | invariance des tables canoniques et du manifeste logique ; lignage physique libre ; borne et couverture de l'analyse | §4, T4, T13 |
| R7 | liste blanche fermée ; fragments + lignage sans perte, maxima publiés ; reçus publiés ; staging, marqueur final, reprise | §9, T20 |

## Décision GO intégrée — précisions Codex du 13 novembre 2026

Le GO 1 technique accepte la révision native v1 ci-dessus, avec les précisions obligatoires suivantes, qui priment sur
ses raccourcis. Le GO 2 scientifique reste NON ACTIVÉ jusqu'à réception de toutes ses preuves. Aucun choix scientifique
n'est modifié. Les deux revues indépendantes ont clos les défauts v0 sous ces précisions finies.

1. **Preuves figées et queue comptable.** Chaque reçu référence un instantané immuable des tentatives finalisées :
   identifiants/cutoff, SHA et CPU consommé. Prévision totale = consommé au cutoff + reste projeté + réserve. Les appels
   ultérieurs constituent une queue en ajout seul, jamais une modification de l'instantané. Le gate additionne le
   consommé courant et le coût restant ; il ne demande pas l'égalité éternelle du forecast au ledger vivant. Une
   interruption fixture est MEASURED avec classification d'interruption voulue et son CPU est toujours inclus. Tester
   une queue autorisée après activation, une mutation de préfixe refusée et une ancienne tentative inachevée refusée.
2. **Finalisation des mesures.** Les propres mesures externes de receipt/activate/publish sont encore actives pendant
   l'appel. Exclure seulement l'identifiant actif attesté par l'hôte ; finaliser time+exit avant l'appel suivant. La
   clôture doit inclure la mesure finale de publication dans un reçu comptable terminal, avec cutoff explicite et lien
   au manifeste publié, sans cycle de hash ni réécriture de l'inventaire figé. Ne pas annoncer une somme complète en
   omettant une queue connue ; documenter séparément le bookkeeping administratif hors mesure des producteurs.
3. **Géométrie et sortie de plan.** Le bloc vient du pilote (250 ou 125), jamais d'un littéral 250 dans la boucle.
   plan imprime seulement K décimal et un newline sur stdout, égal à campaign_plan.json ; diagnostics sur stderr.
   Valider K avant l'arithmétique hôte. La grammaire des ids admet le N majuscule littéral prévu par les formes. Tester
   stdout exact, couverture 354/690 quand tous les fits sont OK, fin par code 10 et échec non nul à borne épuisée.
4. **Budget CPU effectif.** Le mono-fil déclaré ne prouve pas à lui seul CPU<=mur. Full reste sans worker ; imposer
   une limite native CPU au processus scientifique (soft 1700 s, hard 1750 s), en plus du timeout externe 1790+10 s.
   L'enveloppe prochaine invocation de 1800 CPU s inclut une marge de supervision, à documenter au pilote. Surveiller
   aussi le CPU courant dans les gardes ; les mesures externes finalisées restent autoritaires. Une hypothèse de marge
   n'est jamais étiquetée mesure et un dépassement observé/anticipé entraîne STOP avec coût conservé.
5. **Maxima canoniques.** Les blocs calmax sont method-major : ne pas les concaténer par start pour le fragment final.
   Charger au plus les 3*n_cal=6000 lignes d'une cellule, les trier (method,replicate) et les exporter FAIR, ou faire
   l'équivalent en flux trié. Cette table supplémentaire a son ordre défini explicitement et entre dans le test
   d'invariance de géométrie. Les axes J_k globaux ne sont jamais chargés en DataFrame.
6. **Fixtures et couverture.** La fixture scalaire appelle exactement
   e4.cell_calibration(fixture_values(cfg['n_cal'], 'scalar_cal'), cfg['alpha']). Les valeurs de fixture utilisent des
   indices globaux, jamais un recommencement dépendant de la taille des blocs. Les groupes attendus méthode/lecture
   dérivent de cells et calibration : conserver les absences déclarées après refus de base ou CALIBRATION_FAILED,
   exiger les lignes horizon des méthodes restantes et refuser tout vrai réplicat/bloc manquant. Ajouter ce témoin.
7. **Lignage sans auto-référence.** lineage couvre seulement les partitions productrices consommées par merge, jamais
   merge lui-même ou analysis encore absent. Leurs sorties finales sont couvertes par PUBLISHED. Conserver les petites
   charges utiles scalar/fit nécessaires, ou un codage typé explicite qui permet leur reconstruction exacte ; tester
   aussi un mélange de cellules OK/refusées. Les blocs longs sont reconstruits depuis les fragments et vérifiés par SHA.
8. **Audit scalaire et audit autonome.** Les maxima dictionnaires ne reproduisent pas la calibration commune. Vérifier
   la ligne scalaire publiée, ses champs/hashes et toutes ses copies ; choix minimal : régénération déterministe par
   e4.scalar_calibration(cfg,'science') pour full, et par la fixture explicite pour cost_fixture. Ce contrôle ne crée
   aucun nouveau seuil scientifique ; son coût est compté. L'audit autonome utilise les faits/reçus normalisés publiés
   et les hashes reconstruits ; il ne déréférence pas les journaux bruts locaux volontairement non publiés. Les preuves
   brutes restent requises lors de l'activation en ligne. Les phases de contrôle receipt/activate peuvent fonctionner
   avant activation, mais aucune phase productrice science ni publication science ne le peut.

9. **Writer de partitions imbriquées.** e4.run_partition inventorie tmp.iterdir() et suppose des fichiers plats ; il ne
   peut pas être réutilisé tel quel pour merge, qui crée des sous-répertoires. Définir localement dans e4_production.py
   run_production_partition(root,pid,identity,compute) : mêmes états/atomicité/reprise, inventaire récursif de fichiers
   en chemins POSIX relatifs, vérification exacte des hashes et chemins, refus de liens symboliques et traversées.
   Les répertoires admis sont les parents des fichiers déclarés. Tester nested COMPLETE, rejeu sans recalcul, fichier
   imbriqué altéré, fichier/répertoire étranger et exception avant rename. Ne pas modifier le writer du prototype.

Ces précisions ajoutent des témoins significatifs aux tests prévus. Les paramètres scientifiques, les trois sources
prototype/config/tests existantes, les dépendances, les modules partagés et les scellés restent intacts. Codex garde les
reçus, contrôles globaux, pilotes, activation, exécution, publication et Git ; le worker n'exécute que les tests ciblés
sur fixtures sous verrou, puis s'arrête à IMPLEMENTATION_READY pour réception indépendante.
