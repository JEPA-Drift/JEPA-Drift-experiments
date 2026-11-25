# **Prompt 1 — A0/A1 : diagnostic statique et spécification prospective (version révisée)**

# MANDAT CODEX — Étape 1 Student-t7 P1+P4 — A0/A1

## 0. COMPLÉMENT D'ORCHESTRATION — CLAUDE CODE (OPUS 5.5) ET EXÉCUTION ASYNCHRONE ÉCONOME EN TOKENS

Ces règles priment explicitement sur `prompts/Protocole Codex.md` (référence historique antérieure : ne réutilise JAMAIS son `--dangerously-skip-permissions`, son `--effort max` systématique, son `nohup` sans cgroup/ledger, son boucle `worktrees/stream-*` ni ses appels Phase A à `claude -p`) ainsi que sur toute mention historique d'interdiction de `claude -p` ou de recours à `vibe`/`GLM-5.3` dans les prompts suivants :

1. **Références locales à inspecter en lecture seule en A0 (si encore présentes sur disque) :**
   Dans un nouveau worktree tiré de `main`, `logs/` est initialement vide. Tu es autorisé en lecture seule à inspecter (sans jamais les modifier ni les exécuter directement) :
   - `/home/m53/.codex/worktrees/364e/JEPA-Drift-experiments/logs/stream-32/run-phase-b-B3f-red.sh` (modèle de lancement asynchrone détaché de `claude -p` avec préflight SHA, capture `stream-json` et rappel `codex queue --resume`) ;
   - `/home/m53/JEPA-stream-32-Student-T7/logs/stream-32-t7/` (`run-t7.sh`, `check-t7-status.sh`, `t7-worker.sh`, `t7-wall-guard.py`, `t7-supervisor.py` : modèle de superviseur `systemd-run --user`, ledger transactionnel en deux temps, non-héritage `9>&-` du verrou `/home/m53/JEPA-Drift-experiments/logs/.jepa_execution.lock`, et mode `MANUAL_FALLBACK`).
   Si l'un de ces répertoires locaux n'est plus présent sur disque, applique directement les règles ci-dessous et celles des reçus committés (`prompts/RECEIPT-stream-32-t7-tech-A2-20261122.md` et `prompts/RECEIPT-stream-32-t7-runtime-20261124.md`) en adaptant tous les chemins au nouveau worktree et en utilisant `.venv/bin/python` (jamais `Trading` seul pour le code scientifique).

2. **Rôle de *Claude Code* (`Opus 5.5`) pour l'implémentation (actif dès A2 ; non requis en A0/A1) :**
   - *Codex* (`xhigh`) reste seul orchestrateur, relecteur statique, vérificateur des SHA/tests et applicateur (`apply_patch` uniquement après contre-revue statique acceptée). En A0/A1 (`Prompt 1`), *Codex* exécute le diagnostic et les projets documentaires directement sans lancer `claude -p`.
   - À partir de l'implémentation (**A2**, puis tout correctif/script autorisé ultérieurement), délègue la production des patches code/tests/auditeur à *Claude Code* (`--model claude-opus-5-5`) en **lecture seule stricte** (`--restricted --safe-mode --setting-sources '' --tools Read,Grep,Glob --allowedTools Read,Grep,Glob --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands --no-session-persistence`), avec un `--session-id <nouvel-UUID>` neuf à chaque mission (sans `--resume`, `--continue` ni `--fork-session` sur une session précédente).
   - Adapte explicitement le niveau d'effort CLI (`--effort`) à la difficulté de la sous-tâche : `high` par défaut pour les tranches RED/GREEN bornées et tests standards, `xhigh` pour les adaptations transversales (`allocation`, fractionnement `CAL`, `NULL_PLAN` multi-priors, découpage `HOLD`, auditeur deux passes), et `max` réservé uniquement aux invariants mathématiques/architecture particulièrement complexes ou après rejet statique difficile. Consigne chaque UUID et l'effort effectif dans le journal de continuation local.

3. **Communication asynchrone économe en tokens (zéro polling) :**
   - **Briefs ciblés sur `stdin` :** ne transmets jamais à `claude -p` des fichiers volumineux entiers (comme tout `tests/test_pca_info_online.py` ou l'historique complet d'un `continuation.md`) ; fournis un brief borné contenant uniquement les signatures, plages de lignes, contrats et formats de patch attendus.
   - **Lancement détaché + fin de tour immédiate :** interdiction absolue dans *Codex* d'appeler `wait`, `write_stdin`, `sleep` ou de relire les journaux en boucle pour attendre *Claude Code* ou un calcul Python. Lance chaque appel `claude -p` (capture `--output-format stream-json` filtrée par `jq` vers `.raw.json`, sortie `.exit`) et chaque exécution runtime via `systemd-run --user` détaché, avec notification de fin utilisant la variable d'environnement courante `CODEX_THREAD_ID` (jamais un ancien UUID codé en dur) :
     `codex queue --resume --thread "$THREAD_ID" --message "..."` (doublé d'un script `check-status` qualifié pour `MANUAL_FALLBACK` si `codex queue` ne réveille pas la session).
   - **Parcimonie des vérifications :** après lancement détaché, prends **au plus un cliché instantané (<= 15 s)** vérifiant l'unité/PID actif, le préflight SHA et le verrou, consigne dans le journal local, affiche la commande de contrôle puis **TERMINE TON TOUR IMMÉDIATEMENT**. De même, lors des audits de gros CSV/journaux, inspecte par scripts de synthèse/SHA plutôt que de charger des sorties brutes massives en contexte *Codex*.

## 1. Autorité et limites du mandat

Statut à l'entrée :

- `A0_A1_AUTHORIZED`
- `TECHNICAL_GO = ABSENT`
- `RUNTIME_GO = ABSENT`
- `PILOT_GO = ABSENT`
- `FULL_GO = ABSENT`
- `GIT_CLOSEOUT_GO = ABSENT`

Le chercheur autorise exclusivement le diagnostic statique, la préparation d'un worktree dédié et la rédaction de projets documentaires et de configuration.

Aucune édition du code de production, des tests existants, de l'auditeur historique ou du lanceur n'est autorisée.

Aucun tirage scientifique, aucune campagne, aucun profil runtime, aucun commit ni push.

Le présent mandat n'est pas un GO A2.

Respecter le registre historique des 34 prompts de stream. Les nouveaux documents de cette extension seront créés sous `prompts/plans/`, `prompts/` et `prompts/wrapups/`, hors des fichiers enregistrés dans `prompts/streams/`.

Au commit de référence, `tools/check_prompts.py:15–19` et `:30–32` limitent la découverte aux fichiers de `prompts/streams/` correspondant aux motifs `prompt-*.md` et `[0-9][0-9]_STREAM_PCA_DRIFT_*.md`.

En conséquence :

- les nouveaux documents A0/A1 ne nécessitent aucune modification de `EXPECTED_IDS` ;
- ne pas modifier `tools/check_prompts.py` ;
- ne pas modifier `prompts/Prompts_Claude_Code_v5.md` ;
- ne pas ajouter de nouveau prompt au registre historique ;
- le résultat attendu de `make prompts-check`, lors des contrôles ultérieurs autorisés, reste 34/34.

A0/A1 doit uniquement vérifier statiquement ce contrat et préparer les modalités de validation applicables aux phases suivantes.

## 2. Objectif scientifique

Mettre le setup `FITTED_LW_T7`, N=239, application RESIDUAL, fit_id=0 à une précision de calibration comparable au bloc primaire du Full Gaussien publié au commit :

`075d62f78811e7729ebf87ead5ca260e9afde7ca`

L'extension constitue une nouvelle campagne prospective, distincte des quatre campagnes historiques.

Elle doit permettre :

1. Une comparaison d'INFO, PREFIX et FULL_K avec des cohortes CAL/HOLD renforcées.
2. Une sensibilité au prior commun et au prior sélectionné sur DEV.
3. Une comparaison directe entre INFO et FULL_K lorsque les deux utilisent `s2_dev`.
4. L'export des diagnostics HEAD, de sélection et de développement qui manquent aux publications T7 historiques.

Aucune revendication H1–H3 confirmatoire n'est autorisée sous T7.

Ne pas relancer le Full Gaussien.

Ne pas ouvrir D6, OUTER_FIT, F0-uniforme, estimateur robuste ou repli vers FULL_K dans ce mandat.

## 3. Création du worktree et protection des entrées

Lire intégralement `CLAUDE.md`, vérifier son lien avec `AGENTS.md`, puis relever les états réels de `main`, `origin/main`, du verrou partagé et des worktrees actifs.

Créer un worktree dédié depuis le commit exact demandé, sous réserve de disponibilité des chemins et du nom de branche :

- branche proposée : `stream-32-t7-p1-p4` ;
- worktree proposé : `/home/m53/JEPA-stream-32-T7-P1-P4`.

Ne pas déplacer le `main` local ni modifier un worktree appartenant à une autre instance.

Créer les liens absolus `.venv` et `external` vers les ressources locales partagées effectivement vérifiées.

Créer `data/raw/` comme répertoire réel conformément à `C-worktree-data-raw`. Si nécessaire pour les futurs tests data-backed, créer seulement les liens absolus vers les sous-répertoires autorisés et utiles.

Ne jamais créer un lien symbolique unique `data/raw`.

Ne pas exposer, lire, copier ou journaliser les données EUROFIDAI.

Vérifier `git check-ignore` et les exclusions de données avant toute autre opération.

Établir un inventaire de protection comprenant tous les fichiers des répertoires :

- `results/pca_info_online/full-gaussian/`
- `results/pca_info_online/pilot-gaussian/`
- `results/pca_info_online/t7-full/`
- `results/pca_info_online/t7-pilot/`

Pour chaque fichier, relever son chemin, sa taille, son identité Git et son SHA-256 réel. Comparer les octets du worktree à ceux du commit de référence.

Protéger également les configurations historiques, les GO, les audits, les reçus, les amendements, les plans et wrapups historiques.

L'inventaire et les preuves volumineuses restent locaux. Ne jamais inventer une empreinte, ni confondre SHA de blob Git et SHA-256 de contenu.

### 3.1. Préparation des modalités de validation en worktree

Lire :

- `prompts/RECEIPT-stream-32-t7-tech-A2-20261122.md`, notamment les lignes 49–52 ;
- `prompts/wrapups/wrapup-32-t7.md`, notamment la section de clôture Git ;
- `Makefile`, lignes 24–30 ;
- `tests/test_pca_drift_contracts.py`, notamment `test_post2019_rows_never_reach_fit_thresholds_stress`, lignes 1183 et suivantes.

Le reçu A2 historique documente un échec artificiel de l'assertion située à la ligne 1193 lorsque les répertoires temporaires pytest sont créés à l'intérieur du worktree.

Le test compare les identités de deux panels générés. Il suppose que leurs chemins se trouvent hors de la racine logique du producteur, de sorte que les clés du manifeste se réduisent à des basenames communs. Lorsque les fichiers temporaires sont situés dans le worktree, les chemins relatifs distincts peuvent faire échouer cette assertion, indépendamment de la propriété scientifique testée.

Le closeout T7 documente ensuite l'utilisation d'un répertoire temporaire pytest extérieur au worktree.

Préparer, pour les futures exécutions A2 et Git, un répertoire temporaire absolu :

- extérieur au worktree ;
- extérieur à la racine logique du producteur ;
- dédié à la nouvelle extension ;
- non partagé avec une autre instance active ;
- non destiné à Git.

Prévoir la transmission de ce répertoire par `--basetemp`, notamment via `PYTEST_ADDOPTS`, puisque `make check` invoque pytest deux fois.

Employer un chemin réservé à la session de validation concernée. Ne pas utiliser un répertoire temporaire appartenant à une autre instance.

Ne pas modifier le test historique, son assertion ou le producteur pour contourner ce problème de chemin.

Inventorier la disponibilité effective des données locales nécessaires à `make check`.

Si `data/raw/` est vide ou partiel, proposer la validation en deux temps documentée lors du closeout T7 :

1. Validation synthétique tracée dans le worktree, sous verrou partagé, avec liste explicite des deselections, ignores et skips.
2. Validation complète par `make check` sur `main`, après intégration fast-forward, dans l'environnement disposant des données locales requises.

Cette procédure ne permet pas de présenter une validation synthétique comme un `make check` complet.

Toute sélection réduite doit être motivée par l'indisponibilité effective des données ou références externes nécessaires. Elle ne peut exclure les tests synthétiques du nouveau producteur, du nouvel auditeur ou des mécanismes d'allocation et de reprise.

Préparer les modalités de traçabilité :

- commandes ;
- variables d'environnement ;
- chemin `--basetemp` ;
- version et SHA des éventuels plugins locaux de sélection ;
- liste des tests exclus ;
- nombres de tests exécutés, réussis, échoués, sautés et désélectionnés ;
- codes de retour ;
- durée ;
- obligation de validation complète ultérieure.

Aucune exécution pytest ni `make check` n'est autorisée au titre du présent mandat A0/A1.

## 4. Inventaire obligatoire des sources

Lire au commit figé :

- `CLAUDE.md`
- `docs/DEVIATIONS.md`
- `docs/MAPPING.md`
- `Makefile`
- `tools/check_prompts.py`
- `experiments/pca_info_online.py`
- `tests/test_pca_info_online.py`
- `tests/test_pca_drift_contracts.py`
- `tools/ops/audit_stream32_t7.py`
- `configs/pca_info_online_full.yaml`
- `configs/pca_info_online_t7_full.yaml`
- `prompts/plans/plan-32.md`
- `prompts/plans/plan-32-v2.1-amendment.md`
- `prompts/AMENDMENT-stream-32-t7-20261122.md`
- `prompts/SPEC-stream-32-t7-audit-and-runner-20261122.md`
- `prompts/amorcage-32-Pilote-32-Student-T7.md`
- `prompts/RECEIPT-stream-32-t7-tech-A2-20261122.md`
- `prompts/RECEIPT-stream-32-t7-runtime-20261124.md`
- `prompts/RECEIPT-stream-32-t7-pilot-20261124.md`
- `prompts/RECEIPT-stream-32-t7-full-20261124.md`
- `prompts/AUDIT-stream-32-t7-full-20261124.md`
- `prompts/AUDIT-stream-32-full-gaussian-20261122.md`
- `prompts/wrapups/wrapup-32.md`
- `prompts/wrapups/wrapup-32-t7.md`
- `results/pca_info_online/t7-full/telemetry.json`

Inspecter localement, en lecture seule, les scripts d'orchestration utilisés et leurs reçus de qualification. Ne pas présumer que les scripts historiques sont directement réutilisables.

## 5. A0 — Audit statique exhaustif du producteur

Construire une matrice des fonctions à adapter, conserver ou étendre.

Pour chaque fonction, donner :

- le nom et les lignes exactes au commit reçu ;
- ses préconditions actuelles ;
- les champs du descripteur qu'elle consomme ;
- les appels et gardes concernés ;
- le comportement gaussien à préserver ;
- le comportement T7 non alloué à préserver ;
- la modification minimale proposée ;
- le témoin RED correspondant ;
- les risques de régression, de fuite d'information et de corruption de filiation.

### 5.1. Découplage allocation / développement / confirmation

Inspecter au minimum :

`_check_cfg`, `_check_allocation`, `seed_plan`, `design_descriptor`, `authorize`, `_plan_applies`, `_check_plan`, `_expected_rows`, `_cal_keys`, `_hold_plan_keys`, `partition_plan`, `_scheduled_keys`, `dev_phase`, `_dev_reload`, `_dev_derived`, `dev_choices`, `_dev_choice_check`, `policy_rule`, `_cal_cells`.

Le couplage actuel est connu :

- `_check_allocation` refuse les bras T7 ;
- l'applicabilité de NULL_PLAN dépend de `phi.setup` ;
- DEV utilise ce même primaire pour sélectionner `s2_dev` ;
- `_dev_derived` introduit conjointement S2_DEV et GAMMA_M ;
- `main` utilise `_plan_applies` comme condition d'entrée dans l'inférence confirmatoire Full ;
- `confirmatory_from_staging` réserve explicitement le primaire à FITTED_LW_GAUSSIAN.

Proposer un découplage explicite, versionné et activé uniquement par le nouveau design.

Conserver `phi` et le sens des anciens YAML. Ne pas utiliser un simple remplacement du bras dans `phi.setup` comme solution suffisante.

Proposer une garde indépendante pour l'autorisation H1–H3, avec refus de toute tentative confirmatoire T7, y compris par appel direct.

Ne pas élargir l'ensemble des bras autorisés sans distinguer leurs qualifications scientifiques.

### 5.2. CAL renforcé et fractionnement par groupe de prior

Inspecter `cal_phase`, `_cal_keys`, `_expected_rows`, `_cal_cells`, les validations des groupes CAL, les clés primitives de génération, `guarded_partition`, `require_budget`, `partition` et les mécanismes de reconstruction des seuils.

Dans le nouveau Full T7, chacune des politiques distinctes doit disposer de 10 000 simulations CAL :

- INFO / prior commun ;
- PREFIX / prior commun ;
- FULL_K / prior commun ;
- INFO / prior DEV ;
- PREFIX / prior DEV ;
- FULL_K / prior DEV.

Les six configurations doivent utiliser les mêmes indices primitifs CAL, les mêmes observations nulles et le même fit gelé pour permettre une comparaison appariée des politiques.

Si `s2_dev == s2_common`, conserver l'identité de politique existante et l'alias documenté. Ne pas créer trois cellules artificiellement distinctes.

Le niveau nominal reste exactement `alpha = 0.05`.

Pour CAL de taille 10 000, vérifier `r=499` et la borne prédictive marginale `500/10001`.

Aucun seuil h ne sera ajusté à partir de NULL_PLAN, HOLD ou ALT.

#### 5.2.1. Diagnostic du partitionnement actuel

Vérifier explicitement si l'extension envisagée conduirait :

- à une seule partition CAL contenant les six cellules, soit 60 000 scans ;
- ou à deux partitions CAL distinctes, chacune contenant trois cellules et 30 000 scans.

Au commit de référence :

- `_cal_keys`, lignes 1108–1119, construit actuellement les groupes historiques `P_CONF` et `OTHER` pour le primaire alloué ;
- `_expected_rows`, lignes 605–609, réserve `primary_cal_null` au groupe `P_CONF` ;
- `cal_phase`, lignes 2773–2777, associe chaque clé CAL à son effectif ;
- `cal_phase`, lignes 2801–2830, construit le tenseur de scores et exécute successivement les scans de toutes les cellules appartenant à une même partition ;
- `cal_phase`, lignes 2847–2850, réserve actuellement le groupe long aux trois identités PRIMARY ;
- `cal_phase`, lignes 2890–2900, appelle `guarded_partition` pour chaque partition manquante, puis scelle le record global CAL.

Le partitionnement historique `P_CONF` / `OTHER` n'est donc pas directement équivalent au partitionnement requis `COMMON` / `S2_DEV` à 10 000 simulations chacun.

Le déplacement des six identités dans un unique groupe long produirait une unité de travail monolithique de 60 000 scans. Il ne faut pas retenir cette solution sans examen de son coût et de ses conséquences sur les reprises.

#### 5.2.2. Fractionnement requis dans le nouveau design

Lorsque les deux priors sont distincts, prévoir deux partitions CAL scientifiquement distinctes mais appariées sur les mêmes observations :

| Groupe | Politiques           | Simulations par politique | Scans  |
| ------ | -------------------- | ------------------------- | ------ |
| COMMON | INFO, PREFIX, FULL_K | 10 000                    | 30 000 |
| S2_DEV | INFO, PREFIX, FULL_K | 10 000                    | 30 000 |

Les noms exacts des nouvelles clés constituent une décision de schéma A1.

Chaque groupe doit être :

- identifiable par sa propre clé de partition ;
- produit indépendamment ;
- contrôlé par `guarded_partition` ;
- enregistré avec son NPZ et son sidecar ;
- vérifiable à la reprise ;
- protégé contre une réexécution lorsqu'il est déjà commité.

Le groupe COMMON doit pouvoir être produit, scellé et réutilisé même si une interruption survient avant la production du groupe S2_DEV.

Le record global `CAL.json` ne doit être déclaré complet que lorsque toutes les partitions requises par le design effectif ont été vérifiées et que tous les seuils sont reconstruits.

Si les deux priors sont égaux, un seul groupe effectif de trois politiques est nécessaire.

Le plan de partitions devra définir une représentation déterministe de cet alias, compatible avec la planification avant tirage et la décision réalisée de DEV. Si une partition sentinelle est nécessaire pour conserver un inventaire prédéfini, elle ne doit entraîner ni scan supplémentaire ni nouvelle identité de calibration.

Ne pas modifier le partitionnement CAL historique des anciens designs.

#### 5.2.3. Conservation de l'appariement

Le découpage opérationnel par prior ne doit pas créer deux cohortes CAL indépendantes.

Les groupes COMMON et S2_DEV doivent partager exactement :

- les mêmes clés primitives CAL_NULL ;
- les mêmes indices de 0 à 9 999 ;
- les mêmes innovations Student-t7 ;
- le même repère ;
- le même fit ;
- la même transformation PCA.

Les groupes se distinguent par les politiques effectives et le paramètre du scan, non par les observations qui les alimentent.

Il est acceptable de régénérer déterministement les scores CAL à partir des mêmes clés pour traiter séparément les deux groupes.

Le nom du groupe de prior ne doit pas être ajouté à l'entropie des tirages CAL d'une manière qui détruirait cet appariement.

Toute optimisation de cache entre les groupes devra être évaluée en A1 et rester compatible avec les contraintes de mémoire, de filiation et de reprise.

#### 5.2.4. Checkpoints et risque de timeout

À partir de la télémétrie historique du Full T7, vérifier l'ordre de grandeur suivant :

- CPU producteur cumulé : environ 10 224,92 s ;
- nombre nominal de scans : 705 600 ;
- estimation moyenne : environ 0,01449 seconde CPU par scan ;
- extrapolation à 60 000 scans : environ 870 secondes CPU ;
- extrapolation à 30 000 scans : environ 435 secondes CPU.

Ces chiffres sont des extrapolations globales, non des mesures de la durée d'une partition CAL de 10 000 simulations.

Le coût réel peut différer en raison de la génération des scores, des allocations mémoire, des temporaires du scan, des relectures, de la sérialisation et des différences de coût entre politiques.

En outre, le fractionnement peut entraîner une seconde génération du tenseur de scores lorsque les deux groupes sont exécutés séparément.

Vérifier le comportement de `guarded_partition` et `require_budget` : un contrôle de budget à la frontière d'une partition ne garantit pas qu'une partition déjà admise puisse terminer avant un timeout externe.

Vérifier le mécanisme effectif du lanceur historique, notamment la relation entre :

- plafond mur de 2 700 s ;
- échéance applicative historique de l'ordre de 2 000 s ;
- marge de drainage et de persistance ;
- temps restant au début de chaque partition ;
- durée maximale raisonnablement attendue de la partition.

Prévoir une règle d'admission opérationnelle empêchant de démarrer une nouvelle partition CAL lorsqu'il ne reste pas une marge suffisante pour sa production, sa vérification et sa persistance.

Cette règle doit s'appuyer sur les mesures de qualification et sur une réserve prudente. Elle ne doit jamais permettre de dépasser l'enveloppe autorisée.

Si la qualification montre que même un groupe de 30 000 scans est trop long ou trop gourmand en mémoire pour l'enveloppe retenue, arrêter et soumettre une solution de fractionnement supplémentaire avant toute campagne Full.

Ne pas prétendre que le découpage en deux groupes garantit à lui seul l'absence de timeout forcé.

### 5.3. Prior sélectionné sur DEV

Conserver la règle principale :

`s2_common = 2*ln(H/alpha)/(H*K)`.

Utiliser la grille :

`{1, 4, 16, 64} * s2_common`.

Les trois politiques P_CONF sont :

`ONLINE_INFO_MIX_W128`, `ONLINE_PREFIX_MIX_W128`, `FULL_K`.

Pour chaque multiplicateur et chaque politique :

1. Calibrer un seuil provisoire sur DEV_NULL.
2. Évaluer les quatre familles résiduelles sur DEV_ALT.
3. Calculer le critère DEV moyen, avec poids égaux entre les politiques et entre les familles.
4. Choisir le minimiseur commun, avec la plus petite valeur en cas d'égalité.

Ne jamais choisir un multiplicateur différent pour chaque politique dans cette expérience.

Figer le résultat dans DEV avant CAL.

Exporter explicitement :

- `s2_common` ;
- `s2_dev` ;
- multiplicateur retenu ;
- valeurs candidates ;
- critère DEV par candidat ;
- identités des politiques ;
- statut d'égalité ou de distinction des deux priors ;
- provenance du DEV.

Proposer de conserver les fonctions DEV historiques, y compris leurs contrôles de profondeur si nécessaires au schéma, sans publier ni évaluer une nouvelle grille de références fixes en ALT.

Distinguer le calcul interne de développement du périmètre des politiques scientifiques évaluées.

Ne pas exécuter GAMMA_M. La présence éventuelle du champ historique `gamma_M_sensitivity` pour satisfaire le schéma ne constitue pas une autorisation de l'utiliser.

### 5.4. Dimensionnement indépendant de HOLD

Inspecter :

`_null_plan_counts`, `plan_holdout`, `_null_plan_alarms`, `_null_plan_derived`, `null_plan_phase`, `_hold_spans`, `_hold_valid`, `_hold_checks`, `hold_phase`, `_staged_hold_cells`.

Conserver le dimensionnement du §10 du plan historique.

Paramètres Full :

- `alpha = 0.05`
- `m = 3`
- `eps = 0.01`
- `eps_v = 0.01`
- `eta = 0.10`
- `beta = 0.20`
- `n_plan = 2000`
- `n_min = 2000`
- `n_cap = 20000`

La partition NULL_PLAN est indépendante de CAL, HOLD et ALT.

Le plan doit couvrir, au minimum, les quatre comparaisons :

- INFO contre PREFIX sous prior commun ;
- INFO contre FULL_K sous prior commun ;
- INFO contre PREFIX sous prior DEV ;
- INFO contre FULL_K sous prior DEV.

Il doit aussi prendre en compte les exigences de validation individuelle de chaque cellule distincte.

Proposer un seul n_hold commun, égal au maximum des besoins des comparaisons et cellules retenues, tronqué au plafond 20 000.

Privilégier la réutilisation de `plan_holdout` : sa représentation de comptages accepte plusieurs politiques et paires nommées, sous réserve de cohérence des discordances avec les marges.

Conserver les plug-ins conservateurs CP/Tango historiques.

#### 5.4.1. Parité exacte de la règle de dimensionnement

Fixer explicitement `m = 3` dans l'appel à `plan_holdout`.

Ne pas remplacer m par le nombre de paires T7, ni par le nombre de politiques effectives.

Ce choix conserve exactement la règle numérique du dimensionnement historique gaussien pour chaque paire.

Au commit de référence, `plan_holdout`, lignes 244–271, utilise :

- `z_a = norm.isf(alpha/m)` ;
- `z_eq = norm.isf(beta/2)` ;
- `z_b = norm.isf(beta)` ;
- `z_v = norm.isf(0.05)`.

Pour une paire j :

- `D_plus[j]` est la borne CP supérieure de la proportion de discordances, avec `tail = eta = 0.10` ;
- `delta_abs_plus[j]` est le maximum des valeurs absolues des deux bornes Tango calculées avec `tail = eta = 0.10`.

Calculer :

`n_eq[j] = ceil(D_plus[j]*(z_a + z_eq)^2/(eps - delta_abs_plus[j])^2)`

si `delta_abs_plus[j] < eps`, et considérer le besoin comme infini sinon.

Pour une politique P :

- `F_plus[P]` est la borne CP supérieure de sa FPR estimée dans NULL_PLAN, avec `tail = eta = 0.10`.

Calculer :

`n_v[P] = ceil(F_plus[P]*(1 - F_plus[P])*(z_v + z_b)^2/(alpha + eps_v - F_plus[P])^2)`

si `F_plus[P] < alpha + eps_v`, et considérer le besoin comme infini sinon.

Puis :

`n_req = max(n_min, max_j(n_eq[j]), max_P(n_v[P]))`

`n_hold = min(n_req, n_cap)`.

Distinguer clairement :

- la queue `eta = 0.10` utilisée pour les plug-ins conservateurs du NULL_PLAN ;
- la queue `alpha/m = 0.05/3` utilisée dans le quantile normal de dimensionnement de l'équivalence ;
- la queue `0.05` utilisée pour le quantile associé à la validation individuelle.

La parité porte sur la règle numérique de dimensionnement, non sur l'obtention nécessaire du même n_hold que dans la campagne gaussienne historique.

L'application de cette règle aux quatre paires T7 ne constitue ni une garantie de puissance familiale globale, ni un contrôle confirmatoire de multiplicité.

#### 5.4.2. Niveaux d'inférence à distinguer dans les exports

Prévoir trois lectures séparées des différences appariées de FPR :

| Lecture                     | Queue Tango | Intervalle bilatéral correspondant |
| --------------------------- | ----------- | ---------------------------------- |
| IC nominal à 95 %           | 0.025       | 95 %                               |
| Examen TOST à 5 % par paire | 0.05        | 90 %                               |
| Parité numérique historique | 0.05/3      | 96,6667 %                          |

Pour chaque lecture, identifier explicitement la queue, les bornes et la méthode `TANGO_SCORE_ASYMPTOTIC`.

L'examen TOST nominal à 5 % correspond à deux tests unilatéraux à 5 %, ou à l'examen de l'inclusion de l'IC bilatéral à 90 % dans la marge d'équivalence ±0,01.

La lecture à queue `0.05/3` reproduit les niveaux numériques utilisés dans le protocole confirmatoire gaussien historique, sans en transférer les revendications au T7.

Ne pas utiliser l'IC nominal à 95 % comme substitut silencieux à l'IC à 90 % associé au TOST.

Ne jamais annoncer un contrôle familial global sur les quatre paires T7 à partir de `m=3`.

Tous les contrastes T7 demeurent descriptifs. Les comparaisons directes de sensibilité au prior qui ne sont pas incluses dans le dimensionnement doivent être identifiées comme telles.

Le plan doit être figé, haché et vérifiable avant la génération de HOLD.

Si le plafond est atteint, conserver `PLAN_CAPPED_EXPECT_INCONCLUSIVE`. Ne pas augmenter automatiquement le plafond ni modifier la marge.

### 5.5. Taille des NPZ et découpage HOLD

Vérifier `partition` et `_verify_partition`.

La limite stricte des designs alloués est `size < 50*1024*1024` octets à l'écriture et à la relecture, pour toute phase.

Réutiliser autant que possible `_hold_spans`, les indices `path_index`, le contrôle de couverture et `_staged_hold_cells`.

Proposer des blocs de 1 000 simulations au maximum.

Les six politiques distinctes doivent bénéficier du même cohortage long. Ne pas laisser les variantes S2_DEV à la taille ordinaire de 2 000.

Vérifier explicitement :

- la frontière 2 000 / cohorte longue ;
- le dernier bloc incomplet ;
- les clés prévues au plafond et les clés effectivement exécutées ;
- l'ordre numérique des blocs ;
- l'absence de doublons, trous ou recouvrement ;
- le rejet d'un NPZ de taille exactement égale à 50 Mio ;
- les conséquences d'une modification du nombre de cellules exécutables ;
- les tailles des partitions SETUP, DEV, CAL, NULL_PLAN et ALT.

Ne pas supprimer la garde de taille pour faire passer une campagne.

### 5.6. Garde confirmatoire et comparaisons directes

Inspecter `alt_phase`, `_alt_confirmatory`, `confirmatory_inference`, `confirmatory_from_staging`, `descriptive_contrasts`, `_staged_descriptive_rows`, `export_aggregates`, `export_payloads` et `main`.

Le code actuel de `descriptive_contrasts` compare les candidats aux références PRIMARY INFO/PREFIX. Ce comportement est insuffisant pour le point de décision scientifique demandé.

Ajouter à la spécification les contrastes directement appariés, pour chaque famille résiduelle et chaque prior :

- INFO − PREFIX ;
- INFO − FULL_K.

Ajouter également les contrastes de sensibilité au prior, à politique fixée :

- INFO DEV − INFO COMMON ;
- PREFIX DEV − PREFIX COMMON ;
- FULL_K DEV − FULL_K COMMON.

Ces contrastes doivent utiliser les mêmes indices ALT, les mêmes indices HOLD communs et les matrices bootstrap appariées appropriées.

Ne pas soustraire deux intervalles de confiance obtenus contre une troisième référence pour fabriquer un IC direct.

Tous les contrastes du Full T7 restent `DESCRIPTIVE_NOMINAL`.

Les résultats du pilote éventuel restent `PILOT_ONLY`.

Aucune ligne `record_kind=CONFIRMATORY`, aucune hypothèse H1–H3 et aucun statut `CONFIRMED_*` ne peuvent être émis pour ce design.

## 6. A1 — Spécification des diagnostics supplémentaires

### 6.1. HEAD : détectabilité et marge de 10 %

Pour chacun des deux priors, utiliser les premiers hits ALT vérifiés de la famille F_HEAD_RESIDUAL.

Définir T tronqué à 250, avec un premier hit absent contribuant 250.

Exporter :

- RMST INFO ;
- RMST PREFIX ;
- `D_NI = RMST_INFO - 1.10*RMST_PREFIX` ;
- borne supérieure bootstrap appariée de D_NI ;
- `U_PREFIX`, borne supérieure bootstrap de RMST PREFIX ;
- min, moyenne et max de `f_E` et `f_pop` sur les 16 profils HEAD ;
- seuils de géométrie et détectabilité historiques ;
- tailles, clé bootstrap, niveau des bornes et identifiants de calibration.

Reprendre les formules numériques de `confirmatory_inference`, sans appeler sa logique de décision confirmatoire.

Publier la borne à queue nominale 0.05 et, à titre de parité numérique avec le Gaussien historique, la borne à queue `0.05/3`.

Les deux lectures sont descriptives sous T7. Ne pas qualifier H2 de confirmée.

### 6.2. Dynamique de sélection

Inspecter `selection_telemetry`, `hold_selection_telemetry`, `_staged_hold_cells`, `export_alt_selections`, les masques ALT et les diagnostics de projection.

Proposer un export compact, distinct des anciens CSV, portant une ligne par cellule HOLD_NULL et une ligne par cellule ALT/famille.

Pour les n simulations et l'horizon H, définir :

- `axis_frequency[k] = sum(1{k ∈ S_t})/(n*H)` ;
- `switching_rate = sum(1{S_t != S_(t-1)})/(n*(H-1))` ;
- dimension moyenne ;
- histogramme de dimension ;
- ordre explicite des PC2 à PC21 ;
- dénominateurs et comptes entiers permettant le recalcul.

Sur ALT, calculer un Jaccard moyen avec l'ensemble oracle construit hors ligne à partir du vrai q proxy, selon la règle INFO MIX et gamma_M=504 :

`J(S_t,S_oracle) = |S_t ∩ S_oracle| / |S_t ∪ S_oracle|`.

Cet oracle sert exclusivement de témoin géométrique. Il n'est pas nécessaire de calibrer ou d'exécuter un détecteur oracle supplémentaire.

Sur H0, il n'existe pas de vraie direction de rupture. Le Jaccard avec un oracle de rupture est donc non applicable ; le signaler explicitement au lieu de construire un faux oracle nul.

Sous H0, publier les fréquences d'axes et la dynamique de sélection observées. Ne pas annoncer une comparaison avec une PCA de population exacte, absente du scope.

Les métriques principales portent sur l'horizon entier de 250 jours, comme les diagnostics historiques. Toute métrique supplémentaire tronquée à l'alarme doit être distincte et clairement définie.

Les données de simulation privilégiées, q vrai, covariance de population et métadonnées oracle sont interdites dans le chemin non oracle.

Préserver le contrat T48 et l'interdiction d'importer `jepadrift.data_loader` dans le producteur.

## 7. Qualification statistique obligatoire

Sous T7 :

- SETUP : `GAUSSIAN_PROXY` ;
- information des sélections : `ORACLE_DIAGONAL_GAUSSIAN_PROXY` ;
- coût : `ANALYTIC_PROXY`.

Ne jamais appeler ces quantités KL Student-t exactes.

Rappeler que le générateur elliptique utilise un facteur chi-deux journalier commun aux coordonnées.

Le scan utilise une vraisemblance gaussienne de travail. Aucune garantie d'e-processus ou de martingale anytime-valid n'est revendiquée.

La calibration par rang porte sur le risque marginal d'alarme à horizon 250, conditionnellement au fit, en intégrant l'aléa du CAL.

Conserver les trois statuts CP historiques et le seuil individuel de 6 %.

Toute paire impliquant un `NULL_FAILED` doit rester dans les exports et recevoir dans l'analyse la mention `NULL_FAILED — NOT_CLAIMABLE`.

Ne pas confondre `NULL_INCONCLUSIVE` avec `NULL_VALIDATED`.

Ne jamais réécrire la porte historique du §18 ni les décisions antérieures.

## 8. Graines et identité de la nouvelle campagne

Relever le comportement exact de `seed_plan`, de `design_descriptor` et des domaines primitifs de génération.

Au commit de référence :

- `seed_plan`, lignes 361–385, construit les clés primitives à partir de la graine racine, de `mode.upper()`, des setups, des rôles et des indices ;
- `design_descriptor`, lignes 392–404, inscrit notamment la campagne, la graine et le SHA du plan de graines dans le descripteur.

Un nouveau `design_id`, un nouveau worktree ou une nouvelle destination de publication ne suffit donc pas à assurer de nouveaux tirages si les entropies primitives restent identiques.

Ce risque est particulièrement important puisque le Full T7 historique et la nouvelle campagne utilisent tous deux le mode `full` et le setup `FITTED_LW_T7`, N=239, fit_id=0.

La nouvelle campagne doit exclure toute réutilisation non autorisée des observations historiques de développement, de calibration ou d'évaluation.

Soumettre explicitement au chercheur l'une des deux conventions suivantes.

### 8.1. Convention A — Conservation du repère et du FIT_NULL historique, nouveaux rôles d'évaluation

Conserver le repère de population et le `FIT_NULL` historique du setup `FITTED_LW_T7`, N=239, fit_id=0 de `t7-full`.

L'objectif est d'étudier l'effet du renforcement CAL/HOLD et de `s2_dev` sur la même représentation PCA, sans introduire simultanément un changement de fit.

La réutilisation doit être limitée au SETUP approuvé :

- repère ;
- échantillon FIT_NULL ou sa reproduction déterministe ;
- fit Ledoit–Wolf ;
- paramètres de centrage ;
- valeurs propres ;
- vecteurs propres ;
- transformation de blanchiment.

Les clés historiques effectivement utilisées pour ces éléments doivent être identifiées et documentées.

Leur reproduction ou leur réutilisation doit être vérifiée par les empreintes réelles des artefacts et paramètres correspondants.

**Tous les rôles postérieurs à SETUP doivent impérativement utiliser de nouveaux domaines de graines, distincts de ceux de la campagne historique :**

| Rôle                 | Convention A                                     |
| -------------------- | ------------------------------------------------ |
| Repère de population | Historique, conservé et vérifié                  |
| FIT_NULL             | Historique, conservé et vérifié                  |
| DEV_LIB              | Nouveau                                          |
| DEV_NULL             | Nouveau                                          |
| DEV_ALT              | Nouveau                                          |
| CAL_NULL             | Nouveau                                          |
| NULL_PLAN            | Nouveau                                          |
| HOLD_NULL            | Nouveau                                          |
| ALT                  | Nouveau                                          |
| Bootstrap            | Nouvelles clés, liées aux nouvelles cohortes ALT |

La séparation doit couvrir toutes les composantes primitives de génération pertinentes, notamment :

- les innovations nulles ;
- les directions de rupture ;
- les signes ;
- les métadonnées de famille ;
- les clés de la bibliothèque DEV ;
- les clés bootstrap.

Il est strictement interdit :

- de reprendre les 2 000 simulations ALT déjà examinées dans `t7-full` ;
- de prolonger cette ancienne cohorte en présentant son préfixe comme inédit ;
- de réutiliser les anciennes simulations DEV pour sélectionner `s2_dev` ;
- de reprendre les maxima ou seuils CAL historiques comme entrées du nouveau CAL ;
- de compléter simplement les 2 000 simulations HOLD historiques par de nouvelles simulations ;
- de réutiliser une ancienne cohorte en changeant seulement son chemin de stockage.

Proposer un mécanisme explicite de séparation des domaines de graines permettant simultanément :

1. L'identité du repère et du FIT_NULL historique.
2. La fraîcheur des nouvelles cohortes DEV, CAL, NULL_PLAN, HOLD et ALT.
3. L'appariement des politiques et des priors dans chaque nouveau rôle.
4. La séparation entre pilote éventuel, qualification runtime et Full.
5. La reproductibilité indépendante du nombre de workers et des reprises.

La mise en œuvre doit vérifier les entropies effectives, pas seulement la différence textuelle des clés ou des noms de campagne.

Ne pas présumer que le schéma actuel permet de séparer les domaines SETUP et évaluation sans modification.

Présenter en A1 la modification minimale nécessaire, son impact sur `seed_plan`, le descripteur, la génération effective, la filiation et l'auditeur indépendant.

Ne jamais affaiblir les contrôles de lignée ou accepter directement un artefact historique dans un nouveau staging sans vérifier sa provenance et son identité.

Si les artefacts historiques locaux ne sont plus disponibles, examiner la possibilité de reproduire exactement le SETUP historique à partir des clés et du code reçus, puis de vérifier cette identité à l'aide des preuves disponibles.

Si l'identité du SETUP ne peut être établie, la Convention A ne peut pas être déclarée satisfaite. Arrêter et soumettre la Convention B au chercheur.

### 8.2. Convention B — Nouveau FIT_NULL et nouvelles cohortes

Générer un nouveau FIT_NULL pour le setup T7 N=239, fit_id=0 dans la nouvelle campagne.

Utiliser des domaines frais pour tous les rôles DEV, CAL, NULL_PLAN, HOLD et ALT, ainsi que pour les métadonnées et les bootstraps correspondants.

La conservation éventuelle du repère de population historique doit être décidée explicitement. Un nouveau repère ne doit pas être introduit silencieusement.

Cette convention fournit une nouvelle réalisation de la représentation ajustée, contrairement à la Convention A.

Elle ne constitue cependant pas une étude OUTER_FIT ni une réplication multi-fits : un seul fit demeure évalué dans la nouvelle campagne.

Le rapport devra rappeler que la comparaison avec le T7 historique mêle alors :

- le changement de précision CAL/HOLD ;
- l'effet du prior ;
- la variabilité du nouveau fit ;
- la variabilité des nouvelles cohortes.

### 8.3. Vérification de la séparation des domaines

Pour chaque convention, produire une matrice explicite des domaines historiques et proposés, comprenant :

- rôle ;
- graine racine ;
- espace de noms ;
- campagne ;
- setup ;
- indices ;
- composants de l'entropie ;
- justification de toute identité intentionnellement conservée.

Vérifier l'absence de chevauchement non autorisé des entropies primitives entre :

- ancien Full T7 et nouveau Full T7 ;
- ancien Pilote T7 et nouveau Pilote éventuel ;
- qualification runtime et campagnes scientifiques ;
- nouveau Pilote et nouveau Full ;
- rôles indépendants d'une même campagne.

L'appariement entre politiques et priors doit, au contraire, être préservé à l'intérieur d'un même rôle.

Le fait que deux groupes CAL possèdent des clés de partition différentes ne doit pas conduire à leur attribuer des innovations différentes.

La Convention A est préférable pour isoler l'effet de la mise à parité sur le fit déjà étudié, si elle est techniquement réalisable et explicitement validée par le chercheur.

Dans les deux conventions :

- conserver la qualification `FIT_CONDITIONAL` ;
- documenter toute réutilisation intentionnelle ;
- ne pas présenter un simple changement de `design_id` comme une preuve d'indépendance ;
- ne pas prétendre à une réplication indépendante du fit si le fit est conservé ;
- préserver les clés et les identités historiques des anciens designs.

Les nouveaux YAML ne devront pas activer une convention définitive avant la décision A1 du chercheur.

## 9. Projet de publication FAIR

Conserver les cinq exports historiques, sous leurs noms habituels, dans la nouvelle publication.

Proposer des exports supplémentaires conditionnels au nouveau design, par exemple :

- `dev_summary.csv` ;
- `selection_dynamics.csv` ;
- `null_plan_summary.csv`.

Les diagnostics HEAD peuvent être portés par des champs explicitement documentés dans les contrastes descriptifs ou par un export dédié.

Tous ces noms supplémentaires sont des propositions à figer dans A1.

Ne pas modifier les colonnes ni le comportement des exports des anciennes configurations sans nécessité démontrée et autorisation.

Chaque nouvelle sortie doit être :

- liée aux design_id, setup_id, policy_id, calibration_id et digests de phases pertinents ;
- écrite par les mécanismes FAIR du dépôt ;
- reconstructible ;
- liée au manifeste et au realization_id ;
- incluse dans la vérification indépendante ;
- strictement inférieure à 50 Mio.

Aucun tableau complet de masques ni vecteur quotidien brut ne doit être publié dans Git.

## 10. Projection de ressources

Produire un tableau statique exact des comptes de scans par phase et par partition.

Pour le Full, avec six cellules distinctes et HOLD au plafond, vérifier les ordres de grandeur suivants :

| Phase          | Calcul        | Scans   |
| -------------- | ------------- | ------- |
| CAL — COMMON   | 3 × 10 000    | 30 000  |
| CAL — S2_DEV   | 3 × 10 000    | 30 000  |
| NULL_PLAN      | 6 × 2 000     | 12 000  |
| HOLD           | 6 × 20 000    | 120 000 |
| ALT            | 6 × 4 × 2 000 | 48 000  |
| Total hors DEV | <br>          | 240 000 |

Si le DEV historique de profondeur est conservé, ajouter ses comptes et ceux des douze configurations de prior évaluées sur DEV.

Sous réserve de confirmation du chemin effectivement retenu, les coûts DEV historiques conduisent à 32 400 scans supplémentaires :

- grille de profondeur : 6 × (1 000 + 4 × 200) = 10 800 scans ;
- grille de prior : 4 × 3 × (1 000 + 4 × 200) = 21 600 scans.

Total nominal au plafond : 272 400 scans.

Distinguer le cas `S2_DEV_EQUALS_COMMON`, qui réduit les scans des phases postérieures à DEV.

### 10.1. Projection CPU et durée des partitions

À partir du Full T7 historique, vérifier :

`CPU moyen nominal par scan = 10224.92 / 705600`

Cette extrapolation correspond approximativement à :

| Périmètre                         | Scans   | CPU extrapolé |
| --------------------------------- | ------- | ------------- |
| DEV complet                       | 32 400  | 470 s         |
| CAL COMMON                        | 30 000  | 435 s         |
| CAL S2_DEV                        | 30 000  | 435 s         |
| CAL total                         | 60 000  | 870 s         |
| SETUP exclu, DEV + CAL            | 92 400  | 1 340 s       |
| Full, hors DEV, HOLD au plafond   | 240 000 | 3 478 s       |
| Full, DEV inclus, HOLD au plafond | 272 400 | 3 947 s       |

Ces ordres de grandeur ne constituent pas des mesures du nouveau design.

Ne pas assimiler le CPU moyen historique par scan au temps mur d'une partition CAL longue.

Le coût par scan est hétérogène selon les politiques et les phases. Il faut également considérer les coûts qui ne sont pas proportionnels au nombre de scans.

En particulier, la nouvelle taille CAL peut modifier les comportements mémoire, les coûts de génération et les temporaires des noyaux numériques.

Le découpage CAL par prior doit réduire la taille maximale de l'unité de travail non encore commitée, même s'il ne réduit pas le nombre total de scans.

### 10.2. Projection mémoire et disque

Vérifier notamment :

- le tenseur CAL de scores float64 ;
- les temporaires du scan et de la sélection ;
- la taille brute des blocs HOLD ;
- la mémoire de la finalisation et du bootstrap ;
- les copies nécessaires à l'audit indépendant ;
- le coût des relectures de filiation à chaque reprise ;
- l'empreinte disque permanente et transitoire.

Le tenseur CAL d'un seul groupe de prior contient :

`10000 × 250 × 20 × 8 = 400000000 octets`

soit 400 Mo décimaux, environ 381,47 Mio.

Ce chiffre ne représente que le tenseur principal de scores. Il ne constitue pas une borne du pic RAM du groupe.

Le fractionnement par prior ne divise pas par deux la taille de ce tenseur, puisque chaque groupe consomme les mêmes 10 000 simulations. Il évite principalement de réunir les six scans dans une même unité de travail durable.

Vérifier que les tenseurs des groupes successifs ne restent pas inutilement résidents en mémoire.

Pour six cellules effectives, un bloc HOLD de 1 000 simulations contient approximativement :

`6 × 1000 × (250 × 4 + 8) = 6048000 octets`

hors indices et en-têtes.

Vérifier les dtypes réels et toutes les allocations supplémentaires avant de convertir cette estimation en enveloppe.

Distinguer explicitement :

- taille des tableaux scientifiques ;
- taille des NPZ ;
- mémoire maximale du processus parent ;
- mémoire agrégée du cgroup ;
- espace disque local ;
- taille des fichiers destinés à Git.

### 10.3. Enveloppe et stratégie de reprise

Proposer une enveloppe CPU/RAM/mur/jobs prudente, à confirmer après qualification runtime.

Ne pas supposer qu'une partition CAL plus longue tient dans la fenêtre de 2 700 secondes du seul fait que son NPZ final est petit.

Prévoir une réserve opérationnelle suffisante avant admission de chaque groupe CAL.

Présenter une stratégie de reprise après :

- SETUP ;
- DEV ;
- CAL COMMON ;
- CAL S2_DEV ;
- NULL_PLAN ;
- blocs HOLD ;
- ALT ;
- finalisation.

Une reprise après CAL COMMON doit réutiliser ses maxima et son sidecar vérifiés, sans recalculer les trois scans déjà reçus.

La projection doit inclure le cas où la génération des scores est répétée pour traiter séparément les deux groupes CAL.

Ne pas extrapoler une limite sûre de RAM ou de temps à partir du seul nombre de scans.

## 11. Projets YAML et documentation A1

Préparer :

1. Un plan `prompts/plans/plan-32-t7-p1-p4.md`.
2. Un amendement prospectif complémentaire.
3. Une spécification technique TDD et audit indépendant.
4. Un projet YAML Full.
5. Un projet YAML pilote.

Noms proposés :

- `prompts/AMENDMENT-stream-32-t7-p1-p4.md`
- `prompts/SPEC-stream-32-t7-p1-p4.md`
- `configs/pca_info_online_t7_p1_p4_pilot.yaml`
- `configs/pca_info_online_t7_p1_p4_full.yaml`

Tous les nouveaux YAML portent `authorization: null`.

Le projet Full reprend exactement le périmètre scientifique et les tailles convenues.

Le pilote est une décision distincte. Proposer par défaut un pilote réduit, sans NULL_PLAN scientifique applicable, avec `s2_dev` activé indépendamment de l'allocation, pour vérifier le chemin de développement et les sorties.

Le chemin alloué doit être exercé sur des fixtures et une qualification runtime réduite, même si le pilote scientifique est jugé inutile.

Un éventuel pilote alloué constitue une extension supplémentaire des gardes du mode pilot et doit être justifié en A1.

### 11.1. Qualification représentative de CAL=10 000

Un pilote réduit ou un smoke de l'ordre de 200 simulations par rôle ne reproduit ni :

- le tenseur de scores de 400 Mo associé à CAL=10 000 ;
- le coût de génération des 10 000 simulations T7 ;
- les temporaires des trois scans d'un groupe de prior ;
- la durée d'une partition CAL longue ;
- le coût des vérifications et de la persistance à cette échelle.

En conséquence, le projet de qualification runtime devra comporter une règle prospective de suffisance des preuves de ressources.

Si le smoke réduit ne permet pas d'établir une borne crédible sur le pic mémoire agrégé et la durée d'une partition CAL de 10 000 simulations, proposer une sonde runtime dédiée à cette échelle.

Cette sonde doit :

- utiliser un design de qualification distinct ;
- disposer de domaines de graines dédiés, différents des campagnes scientifiques ;
- utiliser `N=239`, `H=250`, `K=20` et le chemin de génération T7 pertinent ;
- exercer effectivement une partition CAL de 10 000 simulations ;
- reproduire le chemin de production, de vérification et de persistance prévu pour le Full ;
- couvrir les groupes COMMON et S2_DEV ou démontrer que les témoins retenus couvrent leurs coûts pertinents ;
- mesurer les ressources à l'échelle cgroup ;
- mesurer les durées de génération, scan, sérialisation, vérification et reprise ;
- vérifier la marge disponible avant l'échéance applicative ;
- ne générer ni lire ALT ;
- ne produire aucune revendication scientifique de performance.

Si le CLI actuel ne permet pas de s'arrêter à CAL, proposer un mécanisme de qualification borné utilisant les contrôleurs effectivement autorisés, sans contourner les gardes scientifiques ou opérationnelles.

La sonde ne constitue ni un Pilote scientifique ni un Full.

Elle ne peut être lancée qu'après un RUNTIME_GO spécifique ou une extension écrite du RUNTIME_GO couvrant précisément son design et son enveloppe.

Ses maxima, seuils, éventuelles directions DEV et autres sorties de qualification ne doivent pas être transférés à la campagne Full pour remplacer ses propres cohortes.

La dispense éventuelle du Pilote ne peut être soumise à décision que lorsque les preuves de ressources à l'échelle pertinente sont suffisantes.

Un Pilote réduit qui n'exerce pas CAL=10 000 ne peut pas, à lui seul, remplacer cette preuve.

Ne pas présenter un YAML incompatible avec le producteur actuel comme prêt à exécuter.

Ne pas inventer un design_id définitif avant A2. Les futurs descripteurs dépendront des octets du nouveau code.

Préparer la matrice des tests d'acceptation et les critères de refus, avec traçabilité vers les fonctions inspectées.

### 11.2. Préparation des contrôles du dépôt

Consigner dans le projet de plan :

- conservation du registre historique 34/34 ;
- absence de modification de `EXPECTED_IDS` ;
- utilisation de pytest avec `--basetemp` extérieur au worktree ;
- validation synthétique tracée si les données locales requises sont absentes ;
- validation complète sur `main` après intégration fast-forward lorsque le périmètre complet n'a pas pu être exécuté dans le worktree.

Ne pas présenter la validation en deux temps comme une dispense définitive de `make check`.

Les éventuelles exclusions de tests doivent être reçues par le chercheur et rester explicites dans le wrapup et la réception finale.

## 12. Réception A0/A1 et arrêt obligatoire

Fournir au chercheur :

- état Git et worktree ;
- inventaire des fichiers protégés ;
- diagnostic des verrous ;
- architecture proposée ;
- schéma de configuration proposé ;
- convention de graines à arbitrer ;
- matrice des domaines primitifs historiques et nouveaux ;
- méthode de dimensionnement HOLD sur les deux priors ;
- définition exacte de m et des différentes queues statistiques ;
- spécification des contrastes directs ;
- schéma des diagnostics FAIR ;
- projection de ressources ;
- diagnostic du partitionnement CAL actuel ;
- proposition de fractionnement CAL COMMON/S2_DEV ;
- stratégie de checkpoint et de reprise entre les deux groupes CAL ;
- stratégie d'admission des partitions au regard du crédit mur et CPU restant ;
- critères de suffisance de la qualification runtime ;
- projet de sonde CAL=10 000, si nécessaire ;
- modalités de validation du dépôt en worktree ;
- matrice TDD ;
- liste exacte des nouveaux fichiers documentaires.

Critères binaires :

- HEAD de départ vérifié : PASS/FAIL ;
- publications historiques inchangées : PASS/FAIL ;
- aucune édition de production : PASS/FAIL ;
- aucun calcul scientifique : PASS/FAIL ;
- projets YAML non autorisés : PASS/FAIL ;
- séparation allocation/prior/confirmation explicitée : PASS/FAIL ;
- comparaisons S2_DEV directes spécifiées : PASS/FAIL ;
- contraintes NPZ couvertes : PASS/FAIL ;
- fractionnement CAL par groupe de prior spécifié : PASS/FAIL ;
- reprise indépendante des deux groupes CAL spécifiée : PASS/FAIL ;
- appariement CAL entre priors préservé : PASS/FAIL ;
- protection contre l'admission tardive d'une partition CAL : PASS/FAIL ;
- conservation des domaines historiques SETUP, si Convention A : PASS/FAIL ;
- fraîcheur obligatoire de tous les nouveaux rôles postérieurs à SETUP : PASS/FAIL ;
- absence de réutilisation ALT historique : PASS/FAIL ;
- dimensionnement NULL_PLAN avec m=3 spécifié : PASS/FAIL ;
- queues 0.025, 0.05 et 0.05/3 distinguées : PASS/FAIL ;
- qualification CAL à l'échelle pertinente prévue : PASS/FAIL ;
- registre des 34 prompts préservé : PASS/FAIL ;
- modalités pytest et validation en deux temps spécifiées : PASS/FAIL ;
- qualification T7 descriptive préservée : PASS/FAIL.

À ce stade, les critères relatifs aux futures exécutions portent sur la complétude et la cohérence de leur spécification, non sur leur réalisation effective.

En cas de FAIL, ne pas ouvrir A2.

ARRÊT OBLIGATOIRE à la livraison A1.

Attendre le TECHNICAL_GO écrit du chercheur.