# AMORÇAGE — Codex orchestrateur : reprise des streams manquants au 12 novembre 2026

**Date : 12 novembre 2026. Destinataire : nouvelle instance Codex, ChatGPT-6.1 Sol, effort Max. Répertoire de référence : `~/JEPA-Drift-experiments`, sur le serveur SSH du chercheur.**

**Point de départ publié, vérifié sur GitHub :** `main` = `3c7f8f399bd1e1c0e4f14d67df7ecf50e7a9a9a6`, dernier commit daté du 8 novembre 2026 à 01:04 UTC. Le 12 novembre à la vérification, **aucun nouveau commit sur `main` depuis cette date** ; seules les branches publiques `main` et `ops/pca-full-2000-20261101` sont listées. Ce constat ne prouve pas l'absence de travaux locaux non poussés, d'agents ou de modifications ignorées par Git.

**Documents de procédure à conserver :** `prompts/streams/00_CODEX_AMORCAGE_CONTINUATION_2026_11_07.md`, `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md`, `prompts/streams/00_CODEX_AMORCAGE_2026_10_24.md`. Le présent fichier **actualise les statuts et la file d'exécution**. En cas de contradiction temporelle sur un lot déjà clos, l'état local vérifié, les commits intégrés et le dernier GO spécifique font foi. Ne pas appliquer à nouveau un ancien amorçage demandant de commencer par 21-F : **21-F est déjà livré**.

## A. Mandat, autorité et limites

Tu es **l'orchestrateur autonome de niveau 2**, pas le développeur scientifique principal. Tu peux auditer les travaux existants, organiser les dépendances, ouvrir des instances **Claude Code CLI interactives** pour élaborer des plans, auditer ces plans et, sous GO autorisé et tracé, superviser des implémentations bornées. **Deux instances Claude Code simultanées au maximum, tous modes confondus**, y compris sessions privées déjà actives. Une seule instance est préférable si les bibliothèques, jeux de tests ou verrous se recouvrent. Claude n'ouvre aucun sous-agent `Agent`/`Task`.

**Décision de reprise :** la nouvelle demande du chercheur autorise le diagnostic, la planification et la poursuite d'implémentations des streams **déjà prévus et encore pertinents**. Elle vaut retour explicite permettant de réexaminer la consigne antérieure de suspension des nouveaux streams, mais **ce n'est pas un GO scientifique universel**. Pour toute opération ayant besoin d'une approbation spécifique — campagne E4 ou E6, PCA sans oracle, données réelles ou post-2019, préentraînement JEPA/VAE, J4/E5, gel effectif `configs/FROZEN.json`, protocole/statistique nouveaux — prépare le plan et demande un GO explicite au chercheur avant l'exécution. Un GO technique Codex ne tient pas lieu d'autorisation scientifique.

**Lecture initiale, avant nouvelle session Claude :**

1. `CLAUDE.md`, `AGENTS.md`, ces trois amorçages et `docs/DEVIATIONS.md`.
2. `docs/audits/streams_01_31_continuation_2026_11_07.md` en entier, **y compris sa section finale « Latest instruction: hold further Claude streams »**, `docs/audits/streams_01_27_relevance_2026_11_06.md`, `prompts/wrapups/handover-01-27.md` §3.6, `prompts/streams/INDEX.md` (inventaire historique seulement).
3. `prompts/wrapups/wrapup-21-F.md`, `wrapup-21-R.md`, `wrapup-21-rest.md`, leurs plans/GO, `tools/freeze_config.py`, `tests/test_freeze_config.py`, `docs/sections/benchmark_runner_contract.md`, `docs/MAPPING.md` et `docs/audits/stream_21_trace_scope_2026_11_06.md`.
4. `prompts/wrapups/wrapup-19-plan.md`, `wrapup-19-oracle.md`, `docs/audits/stream_19_theory_spll_20261107.md`, `docs/audits/stream_19_replan_2026_11_06.md` et les prompts 19.
5. `docs/audits/stream_23_compatibility_2026_11_06.md`, `prompts/plans/plan-23-review.md`, `prompts/wrapups/wrapup-23-review.md` et le prompt historique 23 ; `prompts/wrapups/wrapup-31.md` et `docs/audits/PCA_CONTRACTS_VALIDATION.md`.
6. `tools/ops/monitor_claude_sessions.sh`, `tools/ops/monitor_claude_sessions.py`, `tools/ops/auto_wake_codex.sh`, état réel `tmux`, cron, registres et drapeaux ; **lecture sans exécution des scripts de veille pendant la phase initiale**.

**Sources et traçabilité :** le dépôt Git local et les fichiers sur le disque sont plus probants que GitHub pour l'état des worktrees et des journaux ignorés. Les rapports de wrapup peuvent refléter un état **avant commit** : toujours comparer à la branche principale et aux objets Git. Ne pas déclarer un flux « clos » sur la seule présence d'un prompt, plan ou wrapup, ni dire qu'un code documentaire a été exécuté comme expérience.

## B. Reconnaissance non destructive du dépôt et de l'environnement

Depuis la racine du dépôt principal, sans toucher à un autre worktree ni envoyer de frappes aux agents :

```bash
cd "$HOME/JEPA-Drift-experiments"
pwd
git rev-parse --show-toplevel
git rev-parse HEAD origin/main
git status --porcelain=v1 --untracked-files=all
git branch -avv
git worktree list --porcelain
git log --oneline --decorate -20
# Voir les sessions et services effectivement présents, sans les relancer :
tmux list-sessions 2>/dev/null || true
ps -u "$USER" -o pid,ppid,etime,comm,args | rg 'claude|codex|vibe|auto_wake_codex|monitor_claude|pca_drift' || true
crontab -l 2>/dev/null || true
systemctl is-active crond.service || true
# Lire les scripts, sans les exécuter :
sed -n '1,100p' tools/ops/auto_wake_codex.sh
git ls-files -s tools/ops/auto_wake_codex.sh
```

Inspecter par lecture bornée, si disponibles : `logs/orchestration_20261107/continuation.md`, `logs/orchestration_20261107/execution-19-21-state.json`, `logs/claude_sessions.json`, `logs/NEEDS_CODEX_REVIEW`, `logs/claude_surveillance.log`, `logs/cron_monitor.log` et les logs `stream_21_F`, `stream_21_R`. Les logs ignorés peuvent contenir des travaux récents absents de GitHub ; rechercher une session Claude encore vivante et une éventuelle intervention du chercheur après le 8 novembre. Consigner preuves et limites dans un nouvel état daté.

Après cette photographie initiale, `git fetch origin` est permis ; comparer ensuite HEAD, `origin/main` et le distant. **Pas de `reset --hard`, `clean`, `stash`, `checkout` dans un worktree non possédé, suppression de worktree, réécriture d'historique ni push forcé.** Ne pas commiter sur `main` des données privées ou des logs. Une branche locale non poussée n'est pas un résultat absent : l'examiner sans la modifier.

### Supervision : état à réconcilier avant toute relance

- Au commit `924c97f`, la première ligne du script `tools/ops/auto_wake_codex.sh` a été corrigée. **Le fichier publié au 12 novembre conserve toutefois deux lignes résiduelles finales `EOF` et `chmod 700 tools/ops/auto_wake_codex.sh` après `done`.** Ce défaut de source n'établit pas une panne active du veilleur. Ne pas « réparer en force » un processus personnel ou un worktree possédé ; signaler et, si une correction s'impose, isoler un correctif borné, vérifié statiquement puis autorisé.
- Le script transmis à GitHub prévoit un repli vers une session `tmux` non spécifique, puis vers `codex exec resume --last`. **Après la mort d'une instance Codex, ces replis sont susceptibles de viser le mauvais contexte.** Vérifier propriétaire, panneau exact, cible et état du drapeau avant d'autoriser une frappe ou une relance. Ne pas transmettre automatiquement `continue` pour lever un HOLD, valider un plan, contourner un GO ou réouvrir une instance morte.
- Le moniteur utilisateur `crond` 30 minutes doit rester unique, avec verrou `flock` ; ne pas démarrer un second cron ou un second auto-wake pour « réparer » un silence. Si l'état vivant est ambigu, désactiver toute nouvelle délégation **sans arrêter aveuglément les processus existants** ; demander l'arbitrage nécessaire.

### Invariants de reproductibilité et de confidentialité

```bash
sha256sum results/e2/e2_cells.csv
git show :results/e2/e2_cells.csv | sha256sum
git check-attr text -- results/e2/e2_cells.csv
sha256sum results/e3/e3_overshoot.csv
sha256sum results/pca_drift_benchmark/full_2000_20261101/manifest.json
```

- **E2/J1** : SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF, zéro LF isolé, `-text`, disque et index identiques.
- **E3/D8** : `results/e3/e3_overshoot.csv` SHA-256 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3` ; **FAIL historique +5,2833 %**, tolérance 5 %, à préserver et non « corriger » par rerun opportuniste.
- **PCA full 2000** : manifeste SHA-256 `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`. Le `trials.csv` full reste non suivi sous `~/JEPA-full-2000/`, 48 317 020 octets, SHA-256 déclaré `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`. Ne pas déplacer ni ajouter à Git. Pas de régénération des figures/tableaux scellés.
- **Environnement** : utiliser exclusivement `.venv/bin/python` du projet, `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg` ; conserver locks et liens `external/`. Aucune installation sans besoin identifié et approbation.
- EUROFIDAI est privé. Aucun accès expérimental 2020+, aucun ajustement de seuils sur `monitor`, aucune publication de données. D3 souffre de survivorship et GICS non point-in-time ; P4-D ne dispose pas d'un FPR nul indépendant de référence ; sous Student t7 la KL gaussienne est un **proxy** ; pour covariance rotationnelle, la KL jointe n'est pas la somme des KL marginales ; `M(d,γ)` est un coût de sélection fluide, pas l'ADD exact.

## C. Inventaire des streams 01 à 31 — état publié de référence

Les catégories portent **sur le périmètre effectivement livré**, pas sur toutes les ambitions d'un numéro historique. Les commits sont à recontrôler comme ancêtres de `HEAD` local. **Ne pas confondre le stream historique 28/Electricity avec le nouveau stream 28/PCA.**

| Stream(s) | État GitHub au 12/11 | Résultat acquis / reste à faire |
|---|---|---|
| 01, 02, 03, 04, 05, 06, 07, 08, 08b, 09, 10, 11, 11b, 12, 13 | **CLOS, périmètres livrés** | Fondations, données, générateurs, moniteurs, contrats E1/E2/E3 ; E3/D8 FAIL historique préservé. Aucun rerun automatique. |
| 14 | **CLOS, architecture seulement** | Bottleneck JEPA natif spécifié ; aucun modèle entraîné. |
| 15 | **DIFFÉRÉ** | T-JEPA/BAF, pas de campagne. Attend mandat BAF. |
| 16 | **À REPLANIFIER** | Prétrain JEPA/J3 absent ; ancien pipeline ACP post-JEPA à réviser. Dépend de validation PCA non-oracle et GO scientifique. |
| 17 | **CLOS, ingénierie IPCA** | P4-D non calibré sur null indépendant ; pas de baseline FPR équivalente admissible. |
| 18 | **BLOQUÉ, documentation close** | CD-DFM : source/package/licence et intégration non résolus. |
| 19 | **PARTIEL** | Audit, oracle gaussien `46c2492`, note N/k/d et SPLL `8b1f6db` livrés. **Pas de campagne E4 ni de port SPLL**, protocole expérimental à préciser. |
| 20 | **DIFFÉRÉ** | Transmission et dictionnaire : attend checkpoints entraînés 16. |
| **21** | **PARTIEL global ; lots P, S-recherche, F et R-documentaire traités** | 15/19 occurrences `READ_MATCH` ; 4 bornes `UNSOURCED` (13,16,8,11), recherche locale `SOURCE_NOT_FOUND`. **Lot F clos `26a2a56`** : `tools/freeze_config.py`, 190 tests sur fixtures ; aucun FROZEN réel. **Lot R documentaire clos `3c7f8f3`** : contrat 564 lignes ; **runner global NON implémenté, toutes cibles `UNQUALIFIED`**. |
| 22 | **DIFFÉRÉ** | E5/J4, gel effectif et monitor 2020+ non activés ; exige protocoles et GO propres. |
| 23 | **PARTIEL LOCAL, non fusionné** | Revue documentaire `03f1ced` intégrée ; deux commits E6 locaux `7e4c7a1`, `3d0bd20` au worktree `~/JEPA-stream-23` non intégrés selon dernière preuve. Reprise soumise à C1–C7 et GO expérimental. |
| 24 | **DIFFÉRÉ** | E9 BAF ; dépend 15. |
| 25 | **DIFFÉRÉ** | Régimes financiers réels ; nécessite gel effectif et protocole 2020+. |
| 26 | **DIFFÉRÉ** | Absorption/aging ; dépend au moins d'une représentation 16 entraînée et du protocole d'adaptation. |
| 27 | **CLOS F1 seulement** | E10/F1 linéaire livré ; F2/P5 requièrent mandat séparé. |
| 28 historique (Electricity/E11) | **DIFFÉRÉ** | Hors priorité financière, distinct du numéro PCA. |
| **28 PCA, 29, 30, 31** | **CLOS** | Runner PCA, full synthétique 2000, tableaux, figures, 44 tests de contrats 31 ; aucun rerun. |

**État des tests** : après 21-F, le journal rapporte **1 193 PASS / 5 skips D4 / 0 FAIL** pour le contrôle global. 21-R a ensuite passé **23 contrôles documentaires**, sans nouvelle suite scientifique. Ces totaux sont des rapports historiques et ne doivent pas être présentés comme des tests fraîchement exécutés le 12 novembre.

**Important — dernière instruction du précédent orchestrateur.** L'audit `docs/audits/streams_01_31_continuation_2026_11_07.md` se termine par une suspension explicite des nouveaux streams jusqu'au retour du chercheur. **Le retour est maintenant exprimé par la demande datée du 12 novembre** ; reprends seulement les tâches d'organisation et d'ingénierie dont l'autorisation est couverte, jamais les expériences nécessitant un GO de recherche indépendant. Si des instructions locales ultérieures ou de même rang contredisent cette reprise, arrête-toi et expose-les avant tout lancement.

## D. File de reprise priorisée — dépendances et décisions

**Ne pas commencer par les lots déjà clos 21-F ou 21-R.** Ordre adapté à l'état du 12 novembre ; les priorités sont des propositions soumises au mandat et aux contrats locaux.

### P0 — Récupération de l'instance Codex morte

Identifier sessions Claude/Codex existantes, worktrees, modifications locales, fichiers de plan/GO non committés, registres et alertes. Ne pas écraser de contexte. Valider la cohérence de la branche principale avec `3c7f8f3` et archiver un compte rendu daté en fichier distinct, sans modifier les inventaires historiques scellés. Si une session Claude encore active détient un worktree ou un verrou, attendre une décision du propriétaire avant d'y toucher. Ne jamais utiliser `resume --last` sans identifier précisément la cible et le GO correspondant.

### P1 — Stream 19 : protocole expérimental E4 réellement non redondant (documentaire en premier)

**Première nouvelle mission à envisager**, car elle n'est pas achevée et ne dépend ni d'un gel effectif ni d'un modèle JEPA pour la **planification documentaire**. Déléguer sous nouveau plan `plan-19-protocol-20261112.md` puis GO documentaire, si le propriétaire et les droits sont libres. Rédiger un protocole falsifiable d'**une seule question** qui ne répète ni l'oracle analytique de marché équicorrélé ni les scénarios déjà mesurés par le full PCA 239 actifs.

Spécifier : paramètres fixés N, k, d et amplitude ; choix de loi d'échelle visée et hypothèses ; moyenne équipondérée de N actifs, préfixes PCA, score informationnel, `P3-CS(b)`, méthode SPLL seulement si ses choix inconnus sont réglés ou si elle est explicitement une variante indépendante ; fonds gaussien et t7, dérives de marché/facteur/résiduel, jeux pré-2020 seulement si autorisés, nul fit/calib/holdout indépendant, FPR(H), RMST(H), ARL0 distinct, simulations appariées, FPR égales, ressources CPU/RAM, issue et données sources. Définir **oracle vs ex ante** séparément ; aucun calcul de pente ne doit choisir les axes par connaissance du futur lorsque présenté comme déployable.

**Arrêt obligatoire après le plan/protocole.** `experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, campagne N, reproduction de figures, accès D6 ou données réelles requièrent un **GO scientifique distinct du chercheur**. En particulier l'exposant en N dépend du mode de normalisation de l'amplitude et de l'alignement ; ne pas préremplir des pentes empiriques.

### P2 — Stream 21 : qualification du runner global et décision sur le gel effectif

Le **lot F est implémenté sur fixtures, le lot R est purement documentaire**. Ne pas leur affecter une seconde instance pour refaire leur contenu. Lire les dix portes G1–G10 du contrat `docs/sections/benchmark_runner_contract.md`. Le prochain travail autorisable sans expérience est un **plan de qualification des cibles et des lecteurs bornés** (éventuellement spécification et tests de refus sur fixtures uniquement), identifiant pour chaque cible `e1`, `e3`, `e10` les descripteurs `protocol`, `data`, `reader`, code origin, identité, holdout, schéma, chemins, gestion des erreurs, cas limites, dépendances et couverture gelée. Les cibles sont actuellement `UNQUALIFIED` ; la politique de gel v1 et ses gardes fixture empêchent d'écrire un vrai FROZEN.

**Ne pas implémenter le runner de production** en trahissant les marqueurs `DEFERRED`. Si toutes les portes ne peuvent être levées sans E5 ou décision 2020+, livrer un plan de blocage exact, pas un programme qui invente des valeurs par défaut. Une implémentation de dispatcher sur fixtures, si utile, demande un plan et GO bornés distincts ; **un `configs/FROZEN.json` réel, J4, `--include-test-window`, dégel du monitor et tout accès post-2019 nécessitent un GO spécifique du chercheur**. Noter le conflit du prompt 22 : il attend `results/e5/J4_gate.txt` par défaut alors que le contrat R refuse des cibles non qualifiées ; résoudre dans le plan, pas par création anticipée d'un fichier fictif.

**Lot S** : la recherche dans le dépôt a conclu `SOURCE_NOT_FOUND`, quatre bornes `13`, `16`, `8`, `11` encore `UNSOURCED` dans `paper/sec3_theory.tex:111`. Si aucune nouvelle source n'est fournie, arrêter ce nœud et proposer soit la source primaire manquante, soit un amendement scientifique explicite du manuscrit. Ne pas générer une simulation pour retrouver les chiffres imprimés.

### P3 — Stream 23 : reprise de l'archive E6 après examen des sept conditions C1–C7

Inspecter **en lecture seule** le worktree utilisateur `~/JEPA-stream-23` (`stream-23`, tête historique attendue `3d0bd2071cb86afc6b196b5020ff729204746a93`), et les deux commits `7e4c7a1`, `3d0bd20`. La revue `docs/audits/stream_23_compatibility_2026_11_06.md` établit la compatibilité **statique**, pas une reproduction sur main.

Différences cruciales : E6 `pair: [1, 2]` est **zéro-based**, donc PC2–PC3 ; le benchmark PCA `rotation_pair: [1, 2]` est **un-based**, donc PC1–PC2 ; la calibration E6 utilise parfois des fenêtres nulles in-sample, contrairement à la calibration prédictive indépendante du full PCA ; l'énergie de l'indice est un comparateur unilatéral aveugle à certaines baisses de variance, pas une démonstration générale d'avantage PCA. Les 72 lignes D6 de dérive ne possèdent pas d'IC de G_ADD valide. Lire toutes C1–C7 avant décision.

Proposer un plan d'intégration propre depuis `main`, **sans cherry-pick automatique**, ni suppression du worktree historique, ni adaptation opportuniste des sorties figées. Le GO **d'expérimentation D6/E6** et toute migration doivent être accordés séparément. Le préflight ne vaut pas autorisation de fusion.

### P4 — Backlog scientifique explicitement différé

- **PCA informationnelle synthétique sans oracle** : étape prioritaire pour la valeur scientifique, **hors catalogue fermé des streams 01–31** ; demander un nouveau numéro, plan expérimental et GO. Apprendre sélection et coût sur train uniquement ; calibrer sur null indépendant ; utiliser le même Tableau PCA 29 et Figures 30, ajouter moyenne équipondérée de N actifs, PCA par variance, P3-CS(b), oracle comme borne supérieure seulement. Ne jamais lancer silencieusement en prolongation de 19 ou 23.
- **PCA sur données financières réelles** : seulement après validation du protocole sans oracle, périodes/splits/cohortes, gel effectif et GO post-2019 si applicable. Les dates Covid sous embargo normal et la cohorte rétrospective doivent rester distinctes.
- **16 / JEPA**, puis 20,22,23 phase 2,26 et volet réel : réviser l'ancien protocole ACP post-JEPA vers bottleneck natif 14, stabilité, anti-collapse, essais sans oracle ; conditionner au résultat PCA et GO dédié. Prévoir AE/VAE/VQ-VAE comme comparateurs de repli sous critères de stabilité préspécifiés, pas comme preuve d'un gain de KL.
- **18** CD-DFM bloqué par sources/licence/package ; **15→24** BAF secondaires ; **25** régimes réels bloqué ; **27** F2/P5 et **28 historique** Electricity nécessitent mandats distincts.

**Politique de parallélisme :** P1 (documentation 19) et un P2 strictement documentaire peuvent coexister si deux créneaux restent réellement disponibles et si leurs fichiers sont disjoints. Toute tâche touchant `floors`, `pipelines`, `trace_numbers`, `configs`, `Makefile`, l'environnement ou un `make check` doit être **sérialisée** avec le verrou d'exécution existant. Si l'un des nœuds est bloqué, ne pas combler automatiquement le créneau avec une expérience non autorisée.

## E. Procédure Claude Code interactive, de la planification à l'intégration

### E1. Deux agents maximum ; sessions et identités persistantes

Chaque session a un propriétaire, un worktree/branche unique, une base Git, un GO, une liste de fichiers autorisés et un registre d'exécution. Comptabiliser les sessions Claude privées de l'utilisateur et les agents plan-only dans le plafond de deux. Choisir **Claude Code CLI Opus 5.5, effort Max** pour les tâches difficiles ; `xhigh`/`high` seulement si les options existent réellement dans la CLI et qu'un motif technique est consigné ; **pas de changement de modèle/effort en pleine session pour compenser un quota**. Aucun subagent Agent/Task, aucune troisième instance cachée. Conserver UUID et contexte de session si un quota coupe la production.

### E2. Phase A : plan natif dans la même CLI interactive

Créer un nouveau worktree **uniquement lorsque la tâche est réellement autorisée** et qu'aucun worktree préexistant ne le possède. Contrôler `claude --version` et `claude --help` avant d'utiliser des options. Pour une CLI compatible :

```bash
cd "$WORKTREE_PATH"
claude --version
claude --help
# Adapter les options à la version installée, sans inventer de drapeau :
tmux new-session -d -s "jepa-${STREAM_ID}" -c "$PWD" \
 'claude --model claude-opus-5-5 --effort max --permission-mode plan --disallowedTools Agent Task'
```

Dans cette **même instance interactive**, communiquer les sources, l'ancien prompt canonique, les GO existants, les contraintes de la nouvelle tâche, l'absence de GO expérimental et le mandat `PLAN ONLY`. Pas de `claude -p`, ni headless, ni détournement de `ExitPlanMode`. Demander explicitement : hypothèses scientifiques, sources, cas limites, frontières train/calibration/holdout/monitor, objets propriétaires, tests négatifs, choix API, alternatives concurrentes, mémoire/CPU, données interdites, dépendances, plan RED→GREEN et questions d'arbitrage.

Codex lit le plan, confronte les hypothèses aux sources et répond aux questions techniques **sans casser le contexte Claude**. Il peut demander des révisions plan-only jusqu'à convergence. Le plan approuvé doit être archivé **en français**, avec identifiant inédit, sous `prompts/plans/plan-[ID].md`. L'absence d'un plan validé interdit toute mutation scientifique.

### E3. Phase B : GO écrit et implémentation dans la même session

Le GO est **séparé** : `prompts/GO-stream-[ID].md` ; il cite le SHA-256 du plan, base Git, identifiant de session, fichiers autorisés, tests d'acceptation, budget, politique de données, refus/STOP et provenance de la décision. Distinguer sans ambiguïté « **GO Codex au titre du mandat d'ingénierie délégué** » et « **GO spécifique du chercheur** » ; ne jamais inventer la signature du chercheur. Un GO documentaire ne permet pas de lancer l'expérience proposée dans le document.

Après GO, demander la sortie officielle du mode plan **dans la session initiale**, puis vérifier le mode effectif. Pas de `--dangerously-skip-permissions` par défaut. Réaliser les tests RED→GREEN, tests négatifs, permutations de graines, invariants de non-fuite, refus d'artefacts obsolètes, hash et sorties. Si un nouvel objet scientifique, une porte J4 ou une divergence de modèle apparaît, STOP et revenir au chercheur, sans étendre le GO ni modifier le critère pour obtenir PASS.

### E4. Suivi sans consommation artificielle de tokens

Le moniteur passif du projet contrôle périodiquement les sessions et peut déposer `logs/NEEDS_CODEX_REVIEW`. Un tel signal est **une alerte, pas un GO**. Réception : vérifier le contenu, le hash, la session et le registre ; traiter une seule fois sous verrou ; archiver la preuve de résolution. En cas de watcher actif, les relances automatiques ne doivent jamais cibler un panneau ambigu ni utiliser la session Codex précédente morte comme repli. Préférer un Codex interactif explicitement identifié ; aucun `codex exec resume --last` non borné. Pas de boucle d'inférence qui poll les agents ou `sleep` dans la conversation ; les suivis serveur sont des processus hôte contrôlés par leur propriétaire.

### E5. Réception, closeout et Git sous contrôle Codex

Avant toute clôture : contrôler le diff complet, les fichiers réellement modifiés, schémas, sources, tests, les refus de fuite/2020+, E2 CRLF, E3/D8 FAIL et manifeste PCA. Faire rédiger par Claude un wrapup **en anglais** avec six rubriques exactes : `Context`, `Validated Results`, `Errors and Dead Ends`, `Current State`, `Vigilance Points`, `Recommendations`. Sortir proprement de la CLI et fermer **uniquement** le `tmux` possédé ; conserver le contexte et les logs.

Sérialiser toute validation partageant des imports ou l'environnement :

1. Vérifier le commit de base et les dépendances ; ne pas avancer une branche propriétaire d'un autre agent.
2. `tools/reindex_graphify_jcodemunch.sh` en mode AST sans résumé IA si la procédure du dépôt le requiert ; pas d'appel de modèle externe non autorisé.
3. Exécuter les tests ciblés, `make check`, `make prompts-check` en cas de changement de prompts ; rapporter **les nombres réellement constatés** de PASS/FAIL/SKIP, les durées, le statut PCA 31 (44 contrats) et le statut D8 conservé. Ne pas citer 1 193 PASS comme mesure nouvelle tant que `make check` n'a pas été lancé.
4. Recontrôler J1 disque/index/CRLF, E3, `docs/DEVIATIONS.md`, artefacts PCA et données privées.
5. Stage uniquement des chemins explicitement approuvés ; `git diff --cached --check`, inspection du diff ; exclure logs, caches, secrets, EUROFIDAI, fichiers volumineux et full `trials.csv`.
6. Commit Conventional Commits, sans trailer de co-auteur ; audit de la plage destinée à être poussée, puis intégration sur `main` par fast-forward contrôlé quand les tests et dépendances passent. `git push origin main` seulement si la politique publique du dépôt le permet ; jamais de force-push.
7. Vérifier HEAD local/distant, propriété des sessions, worktrees, cron et registre ; consigner le closeout dans un nouvel état daté.

Si un contrôle scientifique échoue, ne pas retoucher le générateur ou les seuils historiques pour produire artificiellement un PASS. Trois tentatives au maximum pour de purs défauts d'infrastructure, pas pour « réessayer » une hypothèse invalidée.

## F. Première livraison exigée de la nouvelle instance Codex

**D'abord, réponse au chercheur, sans nouveau lancement Claude :**

1. Base locale et distante : HEAD, `origin/main`, commit GitHub, branches/worktrees, état des modifications ignorées et processus persistants ; justification de chaque éventuel écart par rapport à `3c7f8f3`.
2. Inventaire **01–31** incluant `08b`, `11b`, les deux `28`, et surtout les deux nouvelles clôtures **21-F (`26a2a56`) et 21-R (`3c7f8f3`)** : pour chaque stream, `CLOS` / `PARTIEL` / `BLOQUÉ` / `DIFFÉRÉ`, preuve Git et dernière tâche réellement ouverte.
3. Diagnostic du watcher et du précédent orchestrateur décédé : processus, `tmux`, cron, `logs/NEEDS_CODEX_REVIEW`, propriété des worktrees ; relever le défaut résiduel de fin de `auto_wake_codex.sh` sans exécution abusive ni effacement d'un état utilisateur.
4. Ordre des prochaines délégations **19 protocole → 21 qualification/portes G1–G10 → 23 C1–C7**, avec GO requis, conflits de fichiers, limitations de données et tâches bloquées. Préciser que **21-F et 21-R ne doivent pas être relancés**.
5. Tests réellement exécutés pendant cette reprise vs chiffres historiques ; fichiers E2/E3/PCA contrôlés vs simples valeurs déclarées ; dernière instruction de suspension et manière dont la nouvelle demande est interprétée.

**Ensuite seulement :** si la propriété des processus et worktrees est vérifiée, ouvrir **une** session Claude Code de planification sur la tâche documentaire 19. Une session 21 documentaire distincte peut être proposée simultanément seulement si l'inventaire montre un second créneau réellement libre et aucune collision. Il est permis de préparer les plans 23 et 21-runner en lecture seule sans lancement d'expérience. **Ne pas relancer 21-F, 21-R, le full PCA, E3/D8, ou le stream 31.**

Si aucun GO technique ou scientifique ne peut être émis sans question bloquante, livrer la question, les options et les conséquences, puis stopper le nœud. La priorité doit rester la **première expérience scientifique non redondante et vérifiable**, pas le remplissage du quota de deux agents.

**Format attendu :** français pour l'orchestration, anglais pour les documents scientifiques et les wrapups. Distinguer explicitement `vérifié localement`, `publié sur GitHub`, `rapporté par un wrapup`, `inféré`, et `NON EXÉCUTÉ`. Aucun nombre ou gain de performance ne doit être inventé.
