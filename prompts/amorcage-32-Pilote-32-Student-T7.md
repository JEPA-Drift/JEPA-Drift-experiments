# Amorçage Codex — Stream 32, extension descriptive Student-t7 — v5

**Date : 2026-11-22**  
**Statut : `A0_A1_ONLY — NO_TECHNICAL_GO — NO_RUNTIME_GO — NO_T7_PILOT_GO — NO_T7_FULL_GO`**  
**Destinataire : Codex**  
**Base immédiate : `amorcage-32-Pilote-32-Student-T7_v4.md` (SHA-256 `fcfd3452d59358cd58c784865d518be2b14be2e29ab1d398bed3ec10dad42b75`) ; filiation v2 → v3 → v4 → v5. Deux rectifications de traçabilité, sans modification des spécifications scientifiques.**

## 0. Autorité, périmètre et invariants

Travaille exclusivement dans le worktree `/home/m53/JEPA-stream-32-Student-T7` (branche `JEPA-stream-32-Student-T7`), tiré depuis `main`. Ne sors du worktree que pour consulter le verrou partagé `/home/m53/JEPA-Drift-experiments/logs/.jepa_execution.lock`, les cibles `.venv`/`external`, les répertoires `vibe`/`systemd`, et les références nécessaires **en lecture seule**. Ne suppose pas que le HEAD ou les fichiers du worktree sont identiques à ceux de `main` : vérifie-les.

**La présente mission autorise uniquement A0 (diagnostic sans mutation) et A1 (préparation documentaire limitée).** Elle n'autorise ni TDD de production, ni smoke, ni simulation scientifique, ni pilote, ni Full, ni intégration. Une proposition de design, un `design_id`, un fichier GO historique ou la disponibilité du runner n'accordent aucune autorisation d'exécuter.

Invariants absolus :

1. Préserver sans altération le Full gaussien (`realization_id` commençant par `d574db30`, résultats H1–H3 `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR`), le pilote gaussien (`ede212c8…`, quatre `NULL_FAILED`), les identités et empreintes historiques, ainsi que **la fermeture de la porte T7 du §18**. La nouvelle campagne exige une dérogation **prospective, indépendante et écrite** du chercheur ; elle ne réinterprète pas cette porte.
2. T7 est exclusivement **descriptif** : `PILOT_ONLY` pour le pilote, `DESCRIPTIVE_NOMINAL` pour le Full, `ORACLE_DIAGONAL_GAUSSIAN_PROXY` pour les diagnostics oracles et `GAUSSIAN_PROXY` pour les informations T7 pertinentes. Aucune confirmation T7 de H1–H3, aucune prétention de KL Student-t exacte ou de validité anytime du scan gaussien.
3. Ne pas modifier `experiments/`, `jepadrift/`, `tests/`, `tools/`, `docs/`, les artefacts historiques, les GO historiques, le registre scientifique ni les scripts d'exécution. En A1, les seules créations/modifications permises sont les projets explicitement désignés sous `prompts/` et `configs/` ; ne pas committer/pusher en l'absence de revue écrite.
4. Éviter polling et agents pendants : pas de `wait`, `write_stdin` ou `sleep` dans Codex, pas de `claude -p`. Une éventuelle consultation auxiliaire GLM-5.3 via `vibe -p < /dev/null` reste non nécessaire par défaut et ne constitue pas un GO. Aucun lancement détaché n'est déclaré achevé sur son seul cliché initial.
5. Les cinq scripts d'orchestration historiques, même copiés, ne sont **pas** présumés qualifiés pour T7. `MANUAL_FALLBACK_VERIFIED` doit être établi, s'il est requis, par des témoins propres au nouveau périmètre.

## A0 — Diagnostic strictement en lecture seule

### A0.1 Provenance et état du worktree

- Vérifie `git branch --show-current`, `git rev-parse HEAD`, `git status --short`, le commit de base par rapport à `origin/main`, `readlink -f .venv` et l'existence de `.venv/bin/python`. Vérifie l'environnement BLAS=1 : `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. N'active pas d'outil susceptible de produire des écritures de test ou de cache.
- Vérifie en lecture le verrou partagé ; un verrou libre pendant A0 **n'autorise pas** l'exécution ultérieure.
- Consulte, pour diagnostic, `CLAUDE.md`, `docs/DEVIATIONS.md`, `docs/MAPPING.md`, `prompts/plans/plan-32.md` (§§6, 8, 9.4, 17, 18, 20), `prompts/plans/plan-32-v2.1-amendment.md`, `docs/sections/pca_info_online.md`, `prompts/RECEIPT-stream-32-pilot-gaussian-20261120.md`, `prompts/AUDIT-stream-32-pilot-null-20261120.md`, `prompts/RECEIPT-stream-32-full-QUALIF-20261121.md`, `prompts/RECEIPT-stream-32-full-gaussian-20261120.md`, `prompts/AUDIT-stream-32-full-gaussian-20261122.md`, puis `prompts/streams/00_CODEX_AMORCAGE_2026_10_24.md`. **Cet ordre de lecture n’est pas une hiérarchie normative.** En cas de conflit : applique `CLAUDE.md` pour les contrats généraux d’ingénierie et de Git, le plan canonique réconcilié avec son amendement v2.1 pour les règles scientifiques, et uniquement les dérogations ultérieures explicitement autorisées et versionnées. `docs/MAPPING.md` et les reçus/audits constatent les réalisations ; ils ne modifient pas le plan. Signale tout conflit restant sans arbitrage implicite.
- Compare les SHA-256 des cinq scripts d'orchestration copiés sous `logs/stream-32/` aux témoins du reçu de qualification, **s'ils existent effectivement**. Signale les fichiers manquants au lieu d'inférer leur présence. Cherche les chemins codés en dur vers `364e`, `full-gaussian`, d'anciens `staging` ou réalisations gaussiennes ; rapporte les occurrences et leur statut.
- Identifie sous Git le répertoire futur pertinent pour l'auditeur indépendant (`tools/`, `ops/` ou autre selon les contrats de `Makefile`, `tests/test_contracts.py`, `tests/test_decoupling.py`) : un auditeur enregistré uniquement sous `logs/` ignoré serait insuffisant pour la reproductibilité.

### A0.2 Audit statique du chemin T7, y compris publication

Lis `jepadrift/sim.py`, les deux YAML gaussiens de référence et `experiments/pca_info_online.py`. Dresse une **matrice par fonction, avec numéros de lignes du worktree**, pour :

`_check_cfg`, `_check_allocation`, `design_descriptor`, `seed_plan`, `authorize`, `_plan_applies`, `_expected_rows`, `_cal_keys`, `_hold_plan_keys`, `partition_plan`, `run_phases`, `null_plan_phase`, `hold_phase`, `_hold_checks`, `_alt_confirmatory`, `alt_phase`, `confirmatory_from_staging`, `descriptive_contrasts`, `_staged_descriptive_rows`, `export_alt_selections` (**nom réel, pas `export_selections`**), `export_payloads`, `_npz_payload`, `partition`, `_verify_partition`, `finalize_planned`, `finalize`, `_verified_publication` et `main`.

**Question principale.** Peut-on exécuter, après GO futur, un **FULL T7 descriptif non alloué**, via le runner actuel, sans modifier `experiments/pca_info_online.py` ? Hypothèses documentaires à tester :

- `scope.setups` contient seulement `['FITTED_LW_T7', 32, 0]` et `['FITTED_LW_T7', 239, 0]` ; `scope.applications` garde `RESIDUAL` et `MARKET`, familles et politiques conformes à la grille historique T7.
- Le bloc `modes.full.allocation` est **absent** ; `modes.full.null_plan` est `null` ; aucune allocation confirmatoire n'est reconstruite implicitement.
- Le bloc `phi` demeure **si le schéma l'exige**, avec son setup gaussien historique **hors du scope T7** : les labels INFO/PREFIX/FULL_K peuvent naturellement figurer parmi les politiques descriptives, mais il ne doit exister **aucune partition de CAL de groupe confirmatoire `P_CONF`, aucune phase `NULL_PLAN` applicable ni aucune ligne confirmatoire H1–H3**. Une phase `NULL_PLAN` de statut `NOT_APPLICABLE` est admissible.
- Les phases `SETUP → DEV → CAL → NULL_PLAN → HOLD → ALT → FINAL` et les cinq fichiers publiés (`selections.csv`, `trials_summary.csv`, `calibration.csv`, `aggregates.csv`, `issues.csv`) sont examinés jusqu'au bout. Vérifie également les propriétés `LOCAL_HASHED_ONLY` des NPZ de staging.

**Tailles envisagées, avant GO et sans exécution :**

| Rôle        | Pilote T7 | Full T7 descriptif |
| ----------- | --------: | -----------------: |
| `DEV_LIB`   |       100 |                100 |
| `DEV_NULL`  |       200 |              1 000 |
| `DEV_ALT`   |        50 |                200 |
| `CAL_NULL`  |       200 |              2 000 |
| `HOLD_NULL` |       200 |              2 000 |
| `ALT`       |       200 |              2 000 |

Les comptes historiques attendus sont respectivement **73 200** et **705 600** scans pour deux setups, **sous réserve que le scope et la grille de politiques soient identiques à ceux du plan §17**. Recalcule-les si une hypothèse change.

**Limites de taille : distinction impérative.** La partition `HOLD_NULL` non allouée d'un setup RESIDUAL peut contenir 29 cellules et des masques `uint32` de forme `(2000, 250)`, soit approximativement 55,76 Mio pour la partition NPZ. Vérifie **séparément** :

1. la limite de 50 Mio applicable aux *fichiers CSV/JSON publiés* ;
2. l'application exacte de `MAX_PUBLISHED_BYTES` dans `partition` (`:740–775`) et `_verify_partition` : vérifier sur le code si cette borne bloque **tout** NPZ de staging >= 50 Mio (même sans `allocation`) ou seulement les partitions allouées ;
3. les contraintes pratiques de mémoire, de stockage local, de sérialisation et de reprise, indépendamment de la limite de publication.

**N'introduis pas de découpage HOLD superflu si `partition` n'impose pas la borne de 50 Mio aux NPZ non alloués et si le modèle existant reste soutenable en ressources** (éviter un changement de code et de `design_id`). **À l'inverse**, si le code existant impose déjà `MAX_PUBLISHED_BYTES` à tout NPZ de staging sans `allocation`, ou si les ressources l'exigent, motive l'adaptation minimale **à soumettre pour A2**, sans implémentation anticipée. Ne présente jamais la faisabilité statique comme une preuve d'exécution complète : énumère les assertions nécessitant des fixtures et un smoke futur.

### A0.3 Divergence normative `NULL_FAILED` / export descriptif

Vérifie le comportement et le schéma exacts de `descriptive_contrasts` et de l'export `aggregates.csv` : les lignes comportant une cellule `NULL_FAILED` sont actuellement **conservées** sous le statut de campagne `DESCRIPTIVE_NOMINAL` ; vérifie si les statuts nuls des deux politiques figurent en colonnes directes (`candidate_null_status`, `reference_null_status`) ou à l'intérieur de `inference_json`.

Distingue les objets suivants :

- **conservation des observations et exports** : aucune suppression, falsification, recalibration ou réécriture rétrospective ;
- **admissibilité des conclusions** : toute comparaison avec `candidate_null_status == NULL_FAILED` ou `reference_null_status == NULL_FAILED` est signalée dans l'analyse comme `NULL_FAILED — NOT_CLAIMABLE` et n'étaye aucune conclusion de supériorité ou d'équivalence FPR ;
- **statut machine** : n'invente pas de nouvelle valeur de `status` si elle n'est pas prise en charge par le schéma existant. Propose, si nécessaire, un signalement documentaire dérivé des colonnes existantes, ou une modification **explicite A2 sous GO technique**, sans altérer silencieusement les CSV.

Il est donc incorrect de déduire de `DESCRIPTIVE_NOMINAL` qu'une cellule est `NULL_VALIDATED` ; inversement, le statut `NULL_FAILED` n'oblige pas à effacer les résultats descriptifs bruts.

## A1 — Préparation documentaire uniquement

**Seuls les fichiers suivants peuvent être créés ou révisés, en tant que projets sans GO :**

1. `prompts/AMENDMENT-stream-32-t7-20261122.md` ;
2. `configs/pca_info_online_t7_pilot.yaml` ;
3. `configs/pca_info_online_t7_full.yaml` ;
4. `prompts/SPEC-stream-32-t7-audit-and-runner-20261122.md`.

Ne modifie ni `docs/DEVIATIONS.md` ni `docs/MAPPING.md` à A1 ; mentionne précisément **quand** ils devront être mis à jour dans les étapes futures autorisées, y compris `docs/MAPPING.md` dès publication des résultats du pilote.

### A1.1 Projet d'amendement prospectif

Rédige la dérogation versionnée : causes de la fermeture historique (`4 NULL_FAILED` conservés, audit `EXPECTED_SAMPLING_VARIABILITY`), information nouvelle (`0 NULL_FAILED` au Full gaussien, non assimilable à la réouverture du §18), autorisations futures distinctes, et maintien intégral des réalisations antérieures.

Définis la loi T7 effectivement simulée. `jepadrift.sim.t_innov(rng, (T,N))` partage une variable chi-deux à **7 degrés de liberté par ligne/jour** entre les `N` coordonnées : loi multivariée elliptique avec dépendance de queue et variance marginale 1. Les trajectoires/générateurs et ajustements doivent rester indépendants suivant les clés canoniques et les rôles.

Conséquences scientifiques non négociables :

- \(q_k=\beta_k^2/2\), le niveau \(I^*=0{,}25\) et la mesure \(M(d,\gamma_M)\) sont des **proxys gaussiens**, pas des KL Student-t exactes ni un temps de détection démontré.
- Les libellés d'information et de sélection T7 demeurent `GAUSSIAN_PROXY`, `ORACLE_DIAGONAL_GAUSSIAN_PROXY`, `ANALYTIC_PROXY` là où le code les prévoit.
- Le score de scan fondé sur une vraisemblance gaussienne n'hérite pas d'une garantie martingale/e-process sous Student-t ; pas de revendication *anytime-valid*.
- La calibration **par rang des maxima** reste valide au sens **marginal par trajectoire** sous échangeabilité CAL / nouvelle trajectoire nulle, conditionnellement aux règles et ajustements gelés. Ce n'est ni un contrôle anytime, ni une garantie automatique d'`ARL₀`.
- Les quantités d'intérêt sont `RMST_250 = E[min(T,250)]`, fraction détectée/censurée, FPR atteinte avec incertitude, et contrastes appariés **descriptifs**, avec `FIT_CONDITIONAL` (`fit_id=0`) et sans généralisation à des fits indépendants.

Consigne les règles tri-état exactes : `NULL_VALIDATED` si la borne supérieure CP est \(\leq \alpha+\varepsilon_v\) ; `NULL_FAILED` si la borne inférieure CP est \(>\alpha+\varepsilon_v\) ou violation de conception ; sinon `NULL_INCONCLUSIVE`, avec \(\alpha=0{,}05\), \(\varepsilon_v=0{,}01\), queue CP 0,05. N'altère pas les effectifs, seuils ou familles après lecture des puissances ALT. Aucun test T7 ne fait partie de la famille H1–H3.

Explique que des contrastes comportant `NULL_FAILED` restent traçables mais deviennent **non revendicables** ; ne demande pas leur suppression automatique sans convention de schéma approuvée. Interdiction d'annoncer une supériorité générale ou une équivalence FPR garantie à partir des IC descriptifs nominaux.

### A1.2 Projets YAML et pré-descripteurs

Construis deux fichiers YAML *non autorisés* (`authorization: null`), avec les tailles ci-dessus, les deux setups T7 seulement, `fit_id=0`, et les `scope`/grilles/paramètres hérités du canon lorsque compatibles :

- `pilot` : sans `allocation`, `null_plan` réglé selon la règle exacte vérifiée en A0 dans `_check_cfg` / `design_descriptor` (`null` uniquement si admis par le schéma, sinon conservation des champs canoniques sans activation via `_plan_applies`) ; effectifs du pilote ; enveloppe pilote **chiffrée, motivée et explicitement provisoire** (ne pas prendre l'enveloppe du Full gaussien pour un GO T7).
- `full` : sans `allocation`, `null_plan` réglé selon le même contrôle A0 ; effectifs du Full descriptif ; enveloppe provisoire à **réévaluer et geler après les ressources observées pendant le pilote T7**.

Conserve le bloc `phi` hors portée si requis par le schéma ; explique pourquoi il n'active ni les partitions confirmatoires ni `confirmatory_from_staging`. Vérifie que `dev.n_lib` concorde avec `DEV_LIB`. Les valeurs `modes` supplémentaires nécessaires au parsing peuvent être présentes, mais aucune d'elles n'accorde de scope scientifique.

Tu peux exécuter **uniquement** `--describe` pour chacun de ces deux projets **après leur écriture**, si son chemin est effectivement sans tirage, staging ni production scientifique ; utilise impérativement `.venv/bin/python -B` (jamais le `python` de `Trading`) sous `PYTHONDONTWRITEBYTECODE=1` et les variables BLAS/seed déterministes requises, puis consigne le résultat ou l'erreur de validation. `--describe` ne remplace pas les tests futurs. Les identifiants produits sont des **pré-descripteurs provisoires** : toute modification autorisée ultérieure de code, de YAML, d'environnement, de ressources ou de graines change le `design_id` et impose un nouveau GO le citant. Ne préremplis jamais une autorisation à partir de ces seuls identifiants.

### A1.3 Spécification d'audit et requalification du lanceur

Propose l'emplacement **suivi par Git** de l'auditeur indépendant et de ses tests. L'auditeur peut utiliser des bibliothèques scientifiques, mais **aucune fonction de décision du runner** `experiments/pca_info_online.py` (rangs, seuils, CP, premiers franchissements, statistiques appariées, export). Décris les témoins primitifs indépendants, les schémas, les SHA et le plan de contrôle.

Par défaut, utilise une vérification en deux passes **honnêtement libellée** :

1. Passe `pre-alt` aveugle aux fichiers ALT, scellée avant l'ouverture ALT par l'auditeur ; si le runner a déjà généré ALT, **ne pas présenter cette passe comme chronologiquement antérieure à la génération**.
2. Passe ALT après validation du scellé de la passe 1 ; indépendance des algorithmes et reproduction des invariants, pas seulement concordance des exports.

Propose un véritable arrêt pré-ALT seulement si une orchestration native et sûre le permet sans amendement substantiel ; sinon conserve l'option à deux passes et ses limites.

Contrats de requalification du lanceur T7 : SHA des scripts effectivement utilisés, absence de chemins historiques et d'écritures croisées, vérification pré-exécution des GO (`stage`, `design_id`, `go_reference`, `jobs_max`), ledger CPU durable, verrou, mémoire/temps, reprise et publication atomique, comportement conservateur en cas de kill/interruption et réconciliation humaine lorsque requise. Les témoins de la qualification gaussienne ne valent pas transfert automatique. Toute adaptation nécessite le **GO technique A2** avant édition ; tout smoke scientifique nécessite ensuite le **GO runtime distinct** (voir portes ci-dessous).

## Portes et séquence future (aucune autorisée par le présent prompt)

| Stade                 | Porte obligatoire                                                                                    | Action possible après porte                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| A0                    | Ce prompt                                                                                            | Lecture seule, audit statique et rapport                                                             |
| A1                    | Ce prompt                                                                                            | Quatre projets documentaires explicitement autorisés, `--describe` strictement non scientifique      |
| A2                    | **`T7_TECHNICAL_GO` écrit**                                                                          | TDD, fixtures déterministes, correction minimale éventuelle, versionnage auditeur/lanceur            |
| Qualification runtime | **`T7_RUNTIME_GO` distinct, citant le `design_id` final et l'enveloppe**                             | Smoke/qualification d'intégrité et de reprise sous verrou, sans analyse opportuniste de la puissance |
| Pilote T7             | **`T7_PILOT_GO` scientifique du chercheur** avec design, périmètre et budget gelés                   | Pilote `PILOT_ONLY` ; audit complet ; rapport des nulls et ressources                                |
| Full T7               | **`T7_FULL_GO` scientifique distinct**, fondé sur la revue du pilote T7 et un nouveau design complet | Full prospectif `DESCRIPTIVE_NOMINAL`, audit indépendant, résultats positifs/négatifs conservés      |
| Clôture Git           | **Revue explicite du chercheur**, `make check`, wrapup, vérifications SHA/push-policy                | Intégration conforme à `CLAUDE.md`, sans nettoyage aveugle des GO non suivis                         |

Ne transfère aucun `GO` gaussien au nouveau design. En particulier, un `--describe` réussi ne constitue pas un GO runtime. Les lots A2 et qualification runtime peuvent être replanifiés après le rapport A0/A1 ; aucune autorisation n'est implicite.

## Rapport obligatoire et arrêt

À l'issue de **A0 + A1 uniquement**, rends :

1. État du worktree, inventaire SHA et éventuels blocages de provenance.
2. Matrice de compatibilité des fonctions ci-dessus, avec lignes exactes du HEAD local ; décision `NATIVE_DESCRIPTIVE_PATH_POSSIBLE`, `NEEDS_A2_CHANGE` ou `INCONCLUSIVE`, précisant les conditions non prouvées statiquement.
3. Analyse distincte des limites de fichiers publiés, NPZ alloués/non alloués et empreinte mémoire ; taille recalculée et politique de découpage **seulement si nécessaire**.
4. Analyse du comportement réel des contrastes `NULL_FAILED` et convention d'interprétation sans effacement des lignes.
5. Les quatre fichiers projets listés en A1, les pré-descripteurs éventuels et leurs limites ; aucun fichier scientifique créé ailleurs.
6. Un schéma précis des GO, un tableau des tests A2 et un plan d'audit indépendant, avec écarts à soumettre au chercheur.

**ARRÊT ABSOLU :** pas de TDD, pas de code de production, pas de tests exécutés sur trajectoires, pas de smoke, pas de pilote, pas de Full, pas de rebase/commit/push, pas de nettoyage GO en dehors des fichiers A1 autorisés. Ne passe à aucune étape supplémentaire sans décision écrite du chercheur.
