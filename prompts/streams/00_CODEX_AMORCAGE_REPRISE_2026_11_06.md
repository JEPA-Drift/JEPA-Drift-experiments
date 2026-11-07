# AMORÇAGE — Codex orchestrateur, reprise après le benchmark PCA full 2000

**Date de cadrage : 6 novembre 2026.** **Destinataire :** nouvelle instance Codex / ChatGPT-6.1 Sol, effort **Max**. **Racine de travail :** `~/JEPA-Drift-experiments`. **Référence historique à appliquer avec les amendements ci-dessous :** `prompts/streams/00_CODEX_AMORCAGE_2026_10_24.md`.

**Mission immédiatement autorisée :** (1) planifier, faire implémenter et auditer le **stream 31** (contrats scientifiques du benchmark PCA) ; (2) inventorier et arbitrer les streams **01–27 non clos et encore pertinents**, puis amorcer ceux dont les dépendances, les quotas et le GO sont satisfaits. **Hors mandat présent :** lancer un nouveau pipeline PCA sans oracle, une expérience financière réelle 2020+, JEPA, VAE, J4 ou une ré-exécution du benchmark PCA full. Ces chantiers déterminent la stratégie à venir, non l'exécution immédiate.

Tu es **orchestrateur, responsable des GO, auditeur et intégrateur Git**. Tu n'implémentes pas toi-même de code scientifique. Tu conduis les instances **Claude Code CLI interactives**, fais examiner leurs plans, réponds à leurs questions techniques, valides un GO explicite, contrôles leurs livrables et effectues les intégrations. **Au maximum deux sessions Claude Code simultanées au total**, planification, implémentation, reprise et audit délégué compris. Ne pas substituer un essaim d'agents dans une session à cette limite ; désactiver la délégation à des sous-agents multiples si elle contourne la limite.

## A. Hiérarchie documentaire et vérité opérationnelle

**Lecture obligatoire AVANT toute action modifiante :**

1. `CLAUDE.md`, `AGENTS.md` et les règles Git, données, tests, versionnement et environnement ;
2. `prompts/streams/00_CODEX_AMORCAGE_2026_10_24.md` dans son intégralité, notamment invariants, séquençage, monitoring non bloquant et wrapup ;
3. `prompts/wrapups/handover-01-27.md`, en donnant priorité à la section **3.6** tout en reconnaissant son obsolescence au 6 novembre ;
4. `prompts/streams/INDEX.md`, `prompts/streams/31_STREAM_PCA_DRIFT_CONTRACTS.md`, les prompts 15–26 et les documents 28–30 ;
5. `prompts/plans/`, `prompts/wrapups/`, `prompts/GO-stream-*.md`, `docs/DEVIATIONS.md`, `tests/test_contracts.py`, `tests/test_decoupling.py`, `tools/check_prompts.py` ;
6. `results/pca_drift_benchmark/full_2000_20261101/manifest.json`, `results/pca_drift_benchmark/tables/full_2000_20261101/{TABLES_VALIDATION.md,table_manifest.json}`, `results/pca_drift_benchmark/figures/full_2000_20261101_fix_smoke_no_claims/` et les manifestes correspondants.

**Dernier état GitHub vérifié lors de la rédaction :** `origin/main` = `a0c576e13e8e647dfd61350eec52058ffc794dbf`, correction conditionnelle de l'étiquette `SMOKE_NO_CLAIMS`. Le full synthétique 2000/rôle et les tableaux intégrés se trouvent dans la lignée du commit `87a15ad`. Une branche locale `ops/pca-full-2000-20261101`, signalée à `1af0862`, contient un README additionnel ; ne pas supposer que ce commit a été fusionné. La branche locale `stream-23` et `~/JEPA-stream-23` peuvent contenir des données non publiées. **Toutes ces indications sont des indices, jamais des substituts à la vérification du serveur.**

### A1. Inspection strictement en lecture seule

Depuis `~/JEPA-Drift-experiments`, relever et consigner dans un rapport d'ouverture :

```bash
pwd
git rev-parse --show-toplevel
git rev-parse HEAD
git status --porcelain=v1
git branch -avv
git worktree list --porcelain
git remote -v
git log --oneline --decorate -15
tmux list-sessions 2>/dev/null || true
ps -eo pid,ppid,etime,args | grep -E '[c]laude|[v]ibe|[c]odex|[p]ca_drift' || true
find prompts/plans prompts/wrapups -maxdepth 1 -type f | sort
```

Comparer les SHA locaux et distants ; `git fetch origin` seulement après inspection et sans mutation des worktrees d'autrui. Détecter changements non suivis, commits non poussés, tâches en cours, GO historiques, worktrees occupés et fusions partielles. **Ne jamais exécuter** `git stash`, `reset --hard`, `clean -fd`, `checkout`, `rebase`, `worktree remove`, `branch -D`, `push --force` dans un worktree existant appartenant à un autre stream. Aucun `git add .` / `git add -A`.

La présence d'un wrapup est un indice de clôture, **pas une preuve suffisante de fusion**. L'absence de wrapup ne prouve pas l'absence de code. Pour chaque stream, recouper le prompt, les plans, GO, wrapup, branche, commits, résultats, tests et journaux. Ne pas prendre l'`INDEX.md` de 2026-10-16 au pied de la lettre : ses statuts et colonnes de modèle sont historiques.

## B. Invariants et barrières non négociables

1. **Intégrité J1 :** `results/e2/e2_cells.csv` natif CRLF conserve le SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, aussi bien sur disque que dans le blob de l'index Git :
   ```bash
   sha256sum results/e2/e2_cells.csv
   git show :results/e2/e2_cells.csv | sha256sum
   ```
   Écart = arrêt avant commit, rebase ou fusion. Ne jamais convertir CRLF en LF. Le verdict historique E3/D8 `iid/first_order_d1_l3` = **FAIL +5,2833 %** pour une tolérance de 5 % reste inchangé ; aucun rerun destiné à le faire passer.
2. **PCA full scellé :** ne pas réexécuter, modifier, normaliser ni remplacer les tables/figures du full 2000. `trials.csv` full (environ 48,3 Mo) peut ne résider que sur `~/JEPA-full-2000` ; son absence dans le clone Git ne légitime pas des résultats synthétiques inventés. Les tests 31 doivent fonctionner hors ligne sur fixtures pour les propriétés mathématiques, et distinguer explicitement les contrôles d'intégration bloqués faute de trajectoires locales.
3. **Null, information et délai :** définir la divergence KL et ses hypothèses ; la somme des informations par axes est additive pour une moyenne gaussienne dans une vraie base propre de la même covariance, **pas** pour une rotation de covariance ; la KL Student du benchmark est un **proxy gaussien**. `V(S)=I(S)/M(|S|,γ)` classe les sous-ensembles selon un **critère fluide de substitution**, ce n'est ni l'ADD exact ni une preuve d'optimalité du détecteur. Différencier `FPR(H)`, `ARL0`, RMST censurée et budget d'évidence ; ne jamais déduire une garantie à ARL fini de `ln γ/I`.
4. **Leakage :** aucune information des ruptures alternatives n'entre dans la calibration des seuils nulls ou une méthode *ex ante*. Distinguer **oracle de diagnostic** et **méthode déployable**. Les données financières 2020+ sont hors accès expérimental avant gel explicite vérifié ; Covid mars 2020 reste `NOT_EVALUABLE_STANDARD_SPLIT` dans la cohorte avec embargo, et `REAL_RETROSPECTIVE_EXPLORATORY` seulement dans la cohorte dédiée sans embargo, si une exécution distincte a été autorisée. Les statuts `NA/BLOCKED` ne valent jamais zéro.
5. **Données et identité :** ne jamais versionner EUROFIDAI ni données propriétaires, fichiers >50 Mo ou `trials.csv` absent de la politique de suivi ; conserver les règles de confidentialité et anonymisation, `pre-commit` et `pre-push`. Le dépôt GitHub est actuellement déclaré public ; confirmer avant chaque push les règles du dépôt compagnon d'une soumission anonyme et les autorisations en vigueur.
6. **Reproductibilité :** `.venv` partagé, versions épinglées, BLAS mono-thread selon `CLAUDE.md`, graines et données appariées, `make check`, `make prompts-check` quand requis, empreintes de source/configuration/figures. Un test non exécuté n'est jamais `PASS`.
7. **Gel des représentations :** l'encodeur, ses statistiques, les axes, les seuils et choix de canaux restent figés pendant `monitor` ; seule la mémoire interne d'un détecteur séquentiel peut évoluer, outre une transformation quotidienne purement instantanée autorisée.

## C. Priorité 1 — Stream 31 : tests de contrats scientifiques

**Prompt canonique existant, à ne pas réécrire :** `prompts/streams/31_STREAM_PCA_DRIFT_CONTRACTS.md`. L'absence de `prompts/plans/plan-31.md` ou de wrapup-31 sur le `main` consulté ne doit pas être confondue avec un état local : rechercher les deux avant toute création. Respecter l'exclusivité d'édition : `tests/test_pca_drift_contracts.py` et fixtures minimales, sans changer les programmes du runner, de l'assembleur ou des figures sauf GO séparé du chercheur.

Le `trials.csv` non suivi peut être consulté **en lecture seule** à son emplacement effectif dans `~/JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/` après vérification de l'identité du run ; ne pas le recopier dans des fixtures suivies, ni le déclarer présent sans contrôle de disque.

**Contrats de réception obligatoires**, détaillés dans le prompt 31 :

- KL de moyenne gaussienne, décomposition dans la vraie base propre, contre-exemple au classement par variance ; optimalité **combinatoire** exhaustive des `top-d` pour les `q_k` additifs et coût cardinal, avec tous les `d` et tests des égalités ; ne pas transférer cette propriété à la covariance.
- Rotation 2D : KL jointe `0,5625`, somme marginale d'environ `0,3393`, non-additivité et métadonnées `GAUSSIAN_PROXY` pour Student ; énergie de l'indice potentiellement aveugle.
- Coût fluide de mélange `M(d,γ)` : résolution, croissance, valeurs de contrôle, interdiction des étiquettes `EXACT_ADD`, `COV_EXACT_COST`, `ARL0`.
- **CUSUM exact de mélange gaussien pour la moyenne** : comparaison exhaustive `log L_{τ:t}`, maxima et alarmes avec implémentation préfixes vectorisée ; toutes les dates de départ, aucun GLR fenêtré de remplacement ; référence des chemins sans alarme et égalités de maxima ; précision numérique appropriée.
- Covariance empirique / Ledoit–Wolf, CPV spectrale complète, Marčenko–Pastur **sur corrélation**, Kaiser **sur corrélation**, `CPV90_OUTSIDE_TOP20` admissible ; aucune valeur inventée.
- Réemploi exact des `metric_id` et valeurs sérialisées entre Tableau 1, Tableau 2, Tableau 3 sur les seules lignes où l'égalité théorique est prévue ; tests négatifs sur permutations d'axes, indexation, covariance et mélange de FPR ; ne pas lancer d'autre Monte Carlo pour vérifier un même identifiant.
- Plans d'échantillonnage disjoints, reproductibilité des graines et appariement des scénarios, indépendance calibration/holdout, horizon, censure, date et embargo, cohorte Covid distincte, refus des oracles ex post utilisés comme ex ante.
- Provenance des figures, correction `SMOKE_NO_CLAIMS` conditionnelle au `run_mode`, statut `COV_SURROGATE_EXPLORATORY`, absence de `CPV90=90% à k=14` et de numéros préremplis.
- J1 CRLF/SHA et D8 FAIL immuables.

**Incident d'outillage vérifié :** `tools/check_prompts.py` ne découvre actuellement que `prompt-*.md`. Les quatre nouveaux prompts `28_STREAM_PCA_DRIFT_RUNNER.md` à `31_STREAM_PCA_DRIFT_CONTRACTS.md` sont **ignorés** par `make prompts-check` tel quel. Le contrat 31 demande d'étendre la découverte aux deux familles de noms, de rejeter les ID doublés et de démontrer qu'un prompt manquant/modifié provoque effectivement un échec. Attention : `prompt-28-e11.md` est un **autre stream historique**, distinct de `28_STREAM_PCA_DRIFT_RUNNER.md`, malgré son numéro. **Ne jamais réattribuer silencieusement cet identifiant.**

La modification de `tools/check_prompts.py` déborde la zone de propriété QA du stream 31 : elle doit être **explicitement arbitrée et autorisée par Codex dans un GO d'outillage séparé**, idéalement commit indépendant, sans toucher aux scripts scientifiques et avec tests de non-régression du parseur. Déterminer le traitement des ID historiques avant toute mutation du master `Prompts_Claude_Code_v5.md` ; éviter `--sync-master` aveugle qui écraserait les blocs archivés. Le test doit faire échouer un master tronqué ou un identifiant attendu absent, et non produire un faux `100 %` sur le mauvais ensemble.

**Livrables attendus :** plan 31 en français, GO 31 daté, tests et fixtures, `PCA_CONTRACTS_VALIDATION.md` indiquant PASS/FAIL/BLOCKED et commandes exactes, wrapup 31 en anglais, hash et commits, validation de l'absence de modifications scientifiques. Exécuter réellement les tests (unitaires sans données privées même si le `trials.csv` n'est pas disponible), `make check`, et la validation correcte des prompts après GO d'outillage. Les échecs négatifs attendus sont des **tests de rejet réussis** ; ne jamais les masquer avec `xfail` ou `skip`.

## D. Priorité 2 — Audit des streams 01 à 27 et re-priorisation

**Ne pas relancer un stream parce que son prompt figure dans `INDEX.md`.** Construire une matrice au jour de l'audit couvrant **01–27 et 08b, 11b**, avec ces champs : identifiant canonique et alias, objet, source du statut, plan/GO, wrapup, existence de code, résultats/commits et présence sur `main`, dépendances satisfaites, pertinence actuelle après le full PCA, coût/risques, éventuelle redondance, **décision** `{CLOS_VALIDÉ, TERMINER_PARTIEL, À_REPLANIFIER, DIFFÉRER, ABANDON_DOCUMENTÉ, BLOQUÉ}` et justification vérifiable. Ne jamais déclarer `CLOS_VALIDÉ` sans preuve de fusion et tests, ou `ABANDON_DOCUMENTÉ` sans consigner la décision.

**Hypothèses de départ à vérifier, pas commandes d'exécution :**

- 01–14, 17, 27 sont signalés terminés (avec 08b), 18 documenté sans intégration CD-DFM ; aucun rerun de ces travaux n'est autorisé sur la seule base du nouvel audit. Les résultats du stream 17 relatifs à P4-D ne sont **pas** un comparateur à FPR validée ; E3/D8 FAIL reste FAIL.
- 23 : `~/JEPA-stream-23` / branche `stream-23`, phase 1 F4 documentée mais possiblement non fusionnée ; vérifier le SHA local, les écarts de dépendance, les fichiers non suivis, les lois de null, l'absence de fuite et les résultats. **Ne pas checkout/merge/rebase/nettoyer ce worktree**. Proposer soit sauvegarde/audit non destructeurs, soit intégration ciblée d'une phase 1 réellement compatible et non redondante, soit maintien en sommeil ; jamais reprendre automatiquement la phase JEPA.
- 15 et 24 : branche BAF / T-JEPA, en dehors de la priorité actuelle « finance d'abord » ; différer sans prétendre que BAF a été évalué par le PCA full.
- 16 : campagne de pré-entraînement JEPA ; son prompt historique exige une **ACP post-JEPA**, désormais contraire à l'architecture à bottleneck natif du stream 14 corrigé. **Réécriture du plan indispensable avant tout lancement**, mais ne pas démarrer l'entraînement dans ce mandat.
- 19 : lois d'échelle en largeur N et PCA de queue : intérêt de contrôle ou d'annexe, mais son ancienne grille n'est pas le benchmark PCA full du stream 29. Évaluer la nécessité d'une adaptation future, sans lancement automatique.
- 20 : transmission de dérive, dépend de représentations JEPA réellement entraînées ; différer.
- 21 : gel/runner J4, mais l'outil PCA full 28–30 existe déjà ; vérifier recouvrements et ne pas créer un second runner incompatible. Gel avant toute expérience réelle 2020+, à replanifier plus tard.
- 22 : expérience confirmatoire JEPA / J4, non recevable avant le gel, la validation ex ante et des références pertinentes ; différer.
- 25 : événements réels datés, à maintenir derrière la porte de gel et les garde-fous rétrospectifs ; différer.
- 26 : absorption adaptative, dépend de JEPA entraîné ; différer.
- 28 **ancien** (`prompt-28-e11.md`, Electricity) : hors périmètre 01–27 et de la phase finance, signaler séparément comme homonyme non prioritaire, sans le confondre avec le nouveau 28 PCA.

**Résultat de l'audit :** `docs/audits/streams_01_27_relevance_2026_11_06.md` avec matrice, graphe de dépendances, doublons, lacunes réellement bloquantes, séquence proposée et au plus deux voies de travail simultanées. Une tâche ne peut passer de « plausible » à « GO d'exécution » qu'après lecture de son prompt exact et du code déjà disponible, production d'un plan en mode plan, réponses aux questions de Claude et approbation explicite d'un GO enregistré. Évite de créer des sous-streams dont le périmètre recoupe un propriétaire actif.

**Règle de lancement :** exécuter d'abord 31 ; conduire l'audit 01–27 en lecture seule pendant la planification/implémentation 31 si les ressources le permettent. N'activer un second stream de code que si son indépendance est établie, sa pertinence pour la prochaine phase est argumentée et son GO validé. Si l'audit démontre qu'aucun stream ancien non traité n'est immédiatement utile, **ne lancer aucun stream supplémentaire** ; enregistrer la décision et rendre la main. Ne pas commencer les nouvelles expériences ex ante, financières réelles ou JEPA sous couvert d'un ancien numéro.

## E. Procédure Claude Code CLI — interaction, plan et GO obligatoires

**Le protocole de supervision du 24 octobre reste la référence pour l'isolation, la surveillance et la clôture. Modification explicite : les sessions sont maintenant INTERACTIVES et LIMITÉES À DEUX au total.** Le vieux lancement `claude -p` suivi de `--dangerously-skip-permissions` en headless **n'est pas le mode par défaut de cette reprise**. Ne pas faire d'action en tâche de fond sans dispositif externe `tmux`/logs et vérification de processus.

### E1. Préparer le worktree d'un nouveau stream, après préflight

Si aucune branche ni worktree préexistant ne possède le nom souhaité, préparer par exemple le stream 31 (sur un `main` local vérifié, synchronisé ou explicitement réconcilié) :

```bash
ROOT="$HOME/JEPA-Drift-experiments"
WT="$HOME/JEPA-stream-31"
BR="stream-31"
# Arrêter ici si chemin/branche existent : inspecter, ne pas écraser.
git -C "$ROOT" worktree list --porcelain
git -C "$ROOT" branch --list "$BR"
test ! -e "$WT" || { echo 'WORKTREE_EXISTS — STOP'; exit 2; }
test -z "$(git -C "$ROOT" branch --list "$BR")" || { echo 'BRANCH_EXISTS — STOP'; exit 2; }
git -C "$ROOT" worktree add -b "$BR" "$WT" origin/main
```

Configurer les liens `.venv`, `external/` et les sous-répertoires `data/raw/` nécessaires **suivant `CLAUDE.md`**, en respectant `git check-ignore` sur les données EUROFIDAI. Ne pas installer de nouveau Python ou modifier les données sources. Un worktree principal propre n'est pas une permission de déplacer la branche d'un worktree secondaire.

### E2. Démarrer Claude Code en mode plan interactif

```bash
cd "$HOME/JEPA-stream-31"
claude --version
claude --help | grep -E 'model|effort|permission-mode' || true
# Terminal persistant interactif :
tmux new-session -d -s jepa-s31 -c "$PWD" \
  'claude --model claude-opus-5-5 --effort max --permission-mode plan'
tmux attach -t jepa-s31
```

Dans la session : « Lis `CLAUDE.md`, `prompts/streams/31_STREAM_PCA_DRIFT_CONTRACTS.md`, les manifestes full et les tests existants. **MODE PLAN UNIQUEMENT.** Rédige le plan d'implémentation détaillé, les tests négatifs, les obstacles, les fichiers à modifier et les questions nécessitant arbitrage. N'édite aucun code, test ou prompt ; ne lance pas de benchmark. »

**Boucle d'approbation :** Claude soumet son plan et ses questions ; Codex y répond précisément, demande les révisions, vérifie mathématiques, `trials.csv` local, fichiers possédés, risques de fuite et interactions avec le stream 30. Faire enregistrer le plan approuvé dans `prompts/plans/plan-31.md`, avec section « Décision GO intégrée » ; créer `prompts/GO-stream-31.md` résumant la décision, les restrictions, les exceptions d'outillage et les tests obligatoires. **Aucun code applicatif ni scientifique avant GO.** Si le plan propose de modifier le runner full ou de réécrire l'historique, **STOP et arbitrage chercheur**.

### E3. Implémentation interactive après GO

Quitter proprement le mode plan via le mécanisme officiel de la CLI, ou ouvrir une nouvelle session interactive Claude dans le **même worktree et avec le même modèle/effort**, sans option de plan seulement. Vérifier les permissions affichées par la CLI ; ne pas ouvrir une seconde session concurrente sur le même worktree. Fournir le plan et le GO, autoriser uniquement les modifications prévues, imposer TDD RED→GREEN et les tests à petite échelle. Tout nouveau changement de protocole, de statistique ou de source exige un nouveau GO écrit. `--dangerously-skip-permissions` n'est pas requis pour ce workflow interactif et ne doit pas être ajouté automatiquement.

Une seconde session Claude Code peut être planifiée **uniquement** si la première et la deuxième réunies respectent `N_active_claude<=2`, ont des branches/worktrees distincts et ne touchent aucun fichier partagé. Aucun troisième agent même pour « juste un plan ». Les audits indépendants peuvent être effectués directement par Codex sans créer une troisième session.

### E4. Surveillance non bloquante et reprises

Depuis le dépôt principal, relever ponctuellement :

```bash
tmux list-sessions 2>/dev/null || true
tmux capture-pane -p -t jepa-s31 -S -120 2>/dev/null | tail -n 80 || true
ps -eo pid,ppid,etime,args | grep '[c]laude' || true
git -C "$HOME/JEPA-stream-31" status --short
```

**Surveillance périodique déterministe (cadence 30 minutes) :**
En tant que moteur d'inférence réactif, Codex ne dispose pas de persistance mémoire active ni de thread d'exécution continu pour maintenir une boucle de veille interne. La surveillance périodique à 30 minutes est obligatoirement externalisée auprès du système hôte via un harnais déterministe (démon détaché ou tâche cron `*/30 * * * *` exécutant `tools/ops/monitor_claude_sessions.sh`).

À chaque cycle de 30 minutes, le harnais exécute automatiquement :
1. La capture d'écran des terminaux `tmux` actifs (`tmux capture-pane`) et le contrôle des processus Claude Code (`ps aux`).
2. La détection des attentes de saisie utilisateur (`WAITING_INPUT` : question technique, confirmation d'outil, soumission de plan) ou des sorties anormales (`EXIT/CRASH`).
3. La détection de stagnation (> 30 minutes sans modification de fichier dans le worktree cible ni nouvelle sortie terminal).
4. La consignation d'un rapport synthétique horodaté dans `logs/claude_surveillance.log`.
5. Le réveil de l'instance Codex (ou la levée d'un drapeau d'intervention `logs/NEEDS_CODEX_REVIEW`) pour formuler les réponses techniques, débloquer Claude Code ou arbitrer les GO/NO-GO. Si aucune action n'est requise, le cycle se termine sans solliciter d'inférence superflue.

Une session tmux absente n'est pas une preuve de succès : vérifier explicitement l'état des tests, des commits, du wrapup et le code de sortie. En cas de dépassement de quota ou d'erreur de Claude, consigner l'état exact dans le journal de surveillance, geler la session, ne pas relancer aveuglément sans arbitrage et ne jamais manipuler les sessions appartenant à un autre propriétaire.

### E5. Audit, clôture et intégration supervisés

Avant un commit : vérifier les chemins effectivement modifiés, `git diff --check`, tests ciblés, `make check`, `make prompts-check` si concerné, J1 disque + index et D8 FAIL ; produire le wrapup **en anglais** avec les six rubriques de `CLAUDE.md`. Utiliser **`git add` par chemins explicites** ; aucune trace privée ni `trials.csv` dans le staging. Réindexer `tools/reindex_graphify_jcodemunch.sh` à la clôture selon la procédure du dépôt, puis relancer les contrôles nécessaires. L'orchestrateur relit chaque diff et compte rendu avant d'intégrer. Vérifier que la session propriétaire n'écrit plus.

Pour intégrer, choisir une méthode locale sûre après vérification des branches actuelles, du fast-forward et des hooks : par exemple, `git fetch origin`, rebase de la branche de travail **uniquement lorsque son propriétaire est arrêté et son arbre propre**, contrôles après rebase, puis fast-forward contrôlé de `main` et `git push origin main`. Aucun push à partir d'un worktree tiers sans audit de la plage de commits. Respecter la politique actualisée de dépôt public et le test pré-push. Ne jamais forcer le push.

## F. Premier compte rendu et arrêt de l'amorçage

**Avant tout lancement Claude**, produire dans la réponse à l'utilisateur un compte rendu court et factuel incluant :

1. `HEAD` local/`origin/main`, états dirty et commits non synchronisés ; inventaire réel des worktrees, notamment 23, full et 30 ; sessions/quotas ; statut des sorties full et des figures corrigées.
2. Statut vérifié de 31 (prompt, plan/GO éventuels, fichier de tests déjà présent ou non), et proposition de planification + propriétaire de chaque fichier.
3. Matrice provisoire des 01–27 par statut et un ordre d'arbitrage argumenté, avec distinction **pertinent maintenant / à replanifier / différé / abandonné**, sans ressusciter automatiquement les tâches historiques.
4. Dépendances, risque de collision d'ID 28 et vrai comportement de `tools/check_prompts.py`, points exigeant une décision du chercheur, et deux sessions maximum.
5. Prochaines commandes autorisées, sans annoncer tests, GO ou fusions qui ne sont pas effectivement réalisés.

**Objectif de cette reprise :** clôturer proprement les contrats scientifiques du benchmark PCA full ; assainir l'arriéré des 01–27 sur preuves et dépendances ; préparer la phase suivante sans l'exécuter prématurément. **Si un fait matériel manque, inscrire `BLOCKED` et la preuve attendue plutôt que conjecturer.**
