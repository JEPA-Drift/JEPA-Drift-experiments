# AMORÇAGE — Nouvelle instance Codex : reprise des streams manquants (JEPA-Drift)

**Date de rédaction : 7 novembre 2026.** **Destinataire : Codex, ChatGPT-6.1 Sol, effort Max.** **Racine :** `~/JEPA-Drift-experiments` sur le serveur SSH du chercheur. **Base GitHub inspectée :** `477428380cc610314f5deed23f2fec8224990778` sur `main` ; **ne pas supposer cette base encore courante**. **Document de procédure faisant foi :** `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md` ; la présente directive actualise son inventaire et son ordre d'action, mais conserve ses garanties et son protocole interactif.

## A. Mandat, frontières et critères de vérité

Tu es **l'orchestrateur autonome de niveau 2**, non l'implémenteur des modules scientifiques. Le chercheur te demande de reprendre les **streams historiquement planifiés mais non encore livrés**, de les prioriser selon leur nécessité scientifique et leurs dépendances, puis d'en conduire les implémentations autorisées au moyen d'instances **Claude Code CLI interactives, Claude Opus 5.5, effort Max** pour les tâches complexes. Le plafond est de **deux instances Claude Code simultanées au total**, plans, exécutions, audits délégués et reprises compris. Ne lance pas un deuxième agent par habitude : une seule session est préférable si les outils, modules ou validations se recouvrent. Ni sous-agent Agent/Task ni sous-orchestration de Claude pour augmenter ce nombre.

**Nouvelle demande = reprise et arbitrage des streams, pas GO universel d'expériences scientifiques.** Elle t'autorise à faire le préflight, produire/faire produire des plans, arbitrer les dépendances et, après GO écrit conforme, déléguer l'**ingénierie bornée** des streams encore pertinents. Elle n'autorise **pas automatiquement** : nouvelle campagne PCA `full`, sélection PCA sans oracle, analyse de rendements 2020+, expérience réelle, nouveau simulateur E4, apprentissage JEPA/VAE, lancement J4/E5, écriture effective d'un `configs/FROZEN.json` ni un changement du protocole historique. Pour ces opérations, il faut un protocole expérimental daté, des split/holdout et une autorisation explicite du chercheur **en plus** de ton GO technique. Ne transforme jamais une date de jalon en consentement expérimental.

**L'autorité des sources suit cet ordre :** (1) dépôt LOCAL et contrats actifs vérifiés ; (2) GO/plans/commits intégrés et `docs/DEVIATIONS.md` ; (3) la passation du 7 novembre ; (4) anciennes passations/index comme preuves historiques ; (5) énoncés de cette reprise à revalider. Le miroir GitHub n'établit pas l'état des fichiers ignorés, des sessions `tmux`, du cron ni de `~/JEPA-stream-23`. Un wrapup précommit « uncommitted » ne prouve pas que le commit final n'est pas intégré. Ne présume pas qu'un prompt existant est une tâche ouverte.

### Lecture initiale obligatoire (avant tout changement)

1. `CLAUDE.md` et `AGENTS.md` (lien relatif), `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md`, puis le présent amorçage.
2. `docs/audits/streams_01_27_relevance_2026_11_06.md`, `prompts/wrapups/handover-01-27.md` **section 3.6**, `prompts/streams/INDEX.md` (routing historique seulement).
3. `prompts/wrapups/wrapup-31.md`, `docs/audits/PCA_CONTRACTS_VALIDATION.md`, `prompts/wrapups/wrapup-19-plan.md`, `docs/audits/stream_19_theory_spll_20261107.md`, `prompts/wrapups/wrapup-21-rest.md`, `docs/MAPPING.md`, `prompts/plans/plan-21-rest.md`, `prompts/GO-stream-21-rest.md` et `docs/audits/stream_23_compatibility_2026_11_06.md`.
4. `docs/DEVIATIONS.md`, les contrats/test d'intégrité E2/E3/PCA, les prompts exacts de 16, 18, 19, 21, 23 et leurs GO et plans existants.
5. `tools/ops/monitor_claude_sessions.sh`, `tools/ops/monitor_claude_sessions.py`, `tools/ops/auto_wake_codex.sh` **à lire, jamais à lancer pendant le préflight**. Inspecter les événements locaux, registres, locks et crons réels.

## B. Préflight non destructeur, impératif avant ouverture de Claude

Depuis la racine du dépôt principal **sans toucher aux worktrees voisins**, relève au minimum :

```bash
pwd
git rev-parse --show-toplevel
git rev-parse HEAD origin/main
git status --porcelain=v1 --untracked-files=all
git branch -avv
git worktree list --porcelain
git log --oneline --decorate -16
# Lecture des tâches locales, sans envoyer de touche aux terminaux :
tmux list-sessions 2>/dev/null || true
ps -u "$USER" -o pid,ppid,etime,comm,args | rg 'claude|codex|vibe|pca_drift|auto_wake_codex|monitor_claude' || true
crontab -l 2>/dev/null || true
systemctl is-active crond.service || true
systemctl is-enabled crond.service || true
# Vérifier le script de réveil seulement sous forme de texte :
git ls-files -s tools/ops/auto_wake_codex.sh
sed -n '1,65p' tools/ops/auto_wake_codex.sh
```

Consulte sans les modifier : `logs/orchestration_20261107/continuation.md`, `logs/orchestration_20261107/execution-19-21-state.json` si présent, `logs/claude_sessions.json`, `logs/claude_surveillance.log`, `logs/cron_monitor.log`, `logs/NEEDS_CODEX_REVIEW`, `logs/.claude_surveillance.lock`. Les logs sont ignorés par Git et peuvent être absents d'un clone. Utilise une lecture bornée, non une boucle qui attend.

Après un état local initial consigné, `git fetch origin` peut mettre à jour les références distantes. Compare alors `HEAD`, `origin/main` et le HEAD distant sans reset/rebase automatique. **N'efface, ne stashe, ne checkoute, ne nettoie et ne supprime aucun worktree** ; `git reset --hard`, `git clean -fd`, `git add .`, `git add -A` et force-push sont interdits. Si `main` a une modification utilisateur, identifie le propriétaire et stoppe toute intégration risquant de l'affecter.

### B1. Intégration et statut opérationnel de `tools/ops/auto_wake_codex.sh`

Le script `tools/ops/auto_wake_codex.sh`, dont la première ligne d'encapsulation a été **assainie au commit `924c97f`**, est le composant d'orchestration validé pour automatiser le réveil de Codex sans blocage d'inférence continue. Il complète le harnais de surveillance passif `monitor_claude_sessions.sh`.

**Mécanique opérationnelle vérifiée :**
- Le script surveille en boucle passive l'empreinte SHA-256 de `logs/NEEDS_CODEX_REVIEW`.
- À chaque nouvelle alerte (transition d'état, fin de plan, quota, ou fin d'implémentation posée par le cron), il transmet la directive `continue` de façon scindée (`tmux send-keys -l "continue"`, pause de 500 ms indispensable au moteur TUI Rust/Crossterm de Codex, puis `tmux send-keys Enter`) vers le panneau configuré (`TARGET_SESSION:TARGET_WINDOW.TARGET_PANE`).
- Si le panneau configuré est introuvable mais que la session existe, il se replie sur la fenêtre active ; si la session tmux est inactive, il invoque `codex exec resume --last`.

### B2. Intégrité scellée et systèmes externes

```bash
sha256sum results/e2/e2_cells.csv
# Vérification des octets de l'index et des attributs, sans checkout :
git show :results/e2/e2_cells.csv | sha256sum
git check-attr text -- results/e2/e2_cells.csv
sha256sum results/e3/e3_overshoot.csv
```

**E2** : SHA-256 exact `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF, zéro LF isolé, attribut `-text` ; interdit de régénérer ou normaliser E2 pour rapprocher un résultat. **E3** : SHA-256 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`; D8/E3 `iid/first_order_d1_l3` **FAIL +5,2833 %** pour une tolérance de 5,0 %. **PCA full** : manifeste SHA `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47`, full 2000 par rôle ; `trials.csv` local seulement, 48 317 020 octets, SHA selon la passation `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`. Aucune réexécution du full, ni republication de trials, ni réécriture des sorties.

Exécute Python avec `.venv/bin/python` du projet (Python 3.12) et les versions épinglées ; ne remplace jamais l'environnement par Trading seul. Les imports scientifiques exigent `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. `external/` et `.venv/` sont partagés par liens absolus dans les worktrees ; `data/raw/` reste un **vrai dossier** contenant éventuellement des liens individuels, jamais un lien global pour contourner les tests Gitignore. Pas de réinstallation de packages.

EUROFIDAI reste local, non suivi et non journalisé. D3 est un panel de survivants ; les GICS actuelles ne sont pas point-in-time. `P4-D` de 17 n'a pas de calibration indépendante utilisable comme baseline FPR principale. Le modèle de covariance de Student n'a qu'une KL **proxy gaussienne** ; les composantes marginales d'une rotation ne somment pas la KL jointe. `M(d, γ)` est un coût **fluide de sélection**, pas une formule d'ADD exacte. `P3-C` garde explicitement PC1 dans la représentation par défaut. Aucune calibration sur `monitor` et aucun résultat réel 2020+ hors gel effectif autorisé.

## C. Inventaire actuel des streams : ne pas remettre les pendules à zéro

Base vérifiée sur GitHub au moment de la rédaction : `477428380c`. Contrôle les ancêtres dans la branche locale avec `git merge-base --is-ancestor <sha> HEAD` et les fichiers réellement intégrés avant toute classification définitive. Ne confonds pas les deux IDs « 28 » : `prompt-28-e11.md` = Electricity, `28_STREAM_PCA_DRIFT_RUNNER.md` = benchmark PCA.

| Streams                 | Statut de référence                                                                                         | Exécution attendue                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 01–14, **08b**, **11b** | **CLOS** pour les périmètres explicitement livrés ; 13 archivé avec D8 FAIL ; 14 bottleneck natif seulement | Aucun rerun.                                                                                  |
| 15                      | DIFFÉRÉ T-JEPA/BAF                                                                                          | 09 existe ; pas de recherche BAF autorisée ici.                                               |
| 16                      | À REPLANIFIER entraînement/J3                                                                               | Ancienne ACP post-JEPA contraire à 14 ; pas de modèle/checkpoint J3.                          |
| 17                      | CLOS IPCA, P4-D non validé sur holdout                                                                      | Ne pas utiliser P4-D comme égal-FPR sans correctif/protocole distinct.                        |
| 18                      | BLOQUÉ, clôture documentaire seulement                                                                      | Package/pin/licence et adaptateur CD-DFM non résolus.                                         |
| 19                      | **PARTIEL** : audit initial `3467df4`, oracle gaussien `46c2492`, note théorique/SPLL **`8b1f6db`**         | Pas de campagne E4, pas de port SPLL : redéfinir le problème.                                 |
| 20                      | DIFFÉRÉ transmission/dictionnaire                                                                           | Attend des représentations 16 entraînées.                                                     |
| 21                      | **PARTIEL** : audit `ebf94bf`, checker `da518dd`, DPI `527e59c`, annexe `9ec3a7b`, **Lot P `632d19b`**      | **15/19 READ_MATCH**, quatre bornes sans source ; pas de runner global/gel.                   |
| 22                      | DIFFÉRÉ E5/J4                                                                                               | Attend 16, 17 recevable, 19, 21 gel effectif, 23 phase 2 ; 18/20 complémentaires.             |
| 23                      | **À REPLANIFIER** : revue `03f1ced` intégrée, phase 1 historique non intégrée dans `~/JEPA-stream-23`       | Conserver les deux commits et C1–C7 ; aucun merge direct.                                     |
| 24                      | DIFFÉRÉ E9/BAF                                                                                              | Attend 15.                                                                                    |
| 25                      | DIFFÉRÉ historique réel                                                                                     | Attend 21 effectif, splits/cohortes/embargo et protocole 2020+.                               |
| 26                      | DIFFÉRÉ vieillissement/absorption                                                                           | Attend entraînement 16 et gel pour 2020+.                                                     |
| 27                      | CLOS pour E10/F1 linéaire ; F2/P5 non livrés                                                                | Compléments = nouvelle tâche et GO ; ne pas relancer F1.                                      |
| 28 historique           | DIFFÉRÉ capteurs électriques E11                                                                            | Distinct du PCA 28, hors priorité finance.                                                    |
| 28-PCA, 29, 30, **31**  | **CLOS**                                                                                                    | Runner, full, tableaux, figures, outillage 33 prompts, 44 tests 31 validés. Ne pas reprendre. |

Les fichiers `prompts/31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` et `prompts/FIX-stream-31-nb-assets.md`, auparavant non suivis dans la passation, sont maintenant suivis à `aeea450596`. Ils documentent un défaut **déjà corrigé** par `69d5624` ; ils ne sont pas un nouvel ordre de travail. Les anciens arrêts 31 « 43 PASS / 1 FAIL » sont des étapes historiques avant **44 PASS / 0 FAIL**. `make prompts-check` attend **33** prompts canoniques : 29 historiques + 4 PCA, avec deux identités distinctes pour le numéro 28. Ne pas lancer `--sync-master` aveuglément.

## D. Priorisation, dépendances et GO distincts

**Ordre opératoire (non calendaire) :** P0 supervision/orchestration → P1 reste 21 → P2 reste 19 → P3 réévaluation 23 → portes suivantes selon autorisations. Quand une dépendance est absente, **arrête ce nœud**, ne remplis pas artificiellement le deuxième créneau. Identifie précisément la première expérience qui manque, sa valeur scientifique non redondante, ses données et son GO.

### P0 — Aligner la chaîne de supervision opérationnelle

- Contrôler le bon alignement de la chaîne de supervision : crontab 30 min active (`monitor_claude_sessions.sh`), veilleur `auto_wake_codex.sh` opérationnel au commit `924c97f`, cible tmux synchronisée avec l'orchestrateur, absence de processus orphelins et propreté de `logs/NEEDS_CODEX_REVIEW`.
- Contrôler les claims de clôture précédents contre les commits et l'index, pas seulement les wrapups.
- Mettre à jour un **rapport d'état** versionnable à un chemin nouveau dans `docs/audits/` (ou fichier de logs local si aucune mutation n'est encore autorisée). Mentionne que le précédent fichier d'amorçage reste une archive, et ne réécris pas les anciens bilans.
- Une fois la chaîne de supervision confirmée, engager le flux P1 sans délai.

### P1 — Stream 21 restant, priorité d'ingénierie

**Lot P est clos. Ne le répète pas.** `docs/MAPPING.md` et `results/sec3/sec3_analytic.csv` fixent **15/19** correspondances ; les quatre bornes `13`, `16`, `8`, `11` à `paper/sec3_theory.tex` ligne 111 restent `UNSOURCED`. Leurs producteurs/estimateurs (notamment `CV²(I_t)`, temps de corrélation intégré, fenêtre, SR/γ/mode et provenance) ne sont pas spécifiés. Distingue : source absente ≠ zéro ≠ échec d'un test ; ne fabrique pas de CSV ou recalage du manuscrit.

**Lot S (documentaire, possible en premier)** : identifier une source exacte pour les quatre bornes, ou rendre un `SOURCE_NOT_FOUND` étayé. Aucun nouveau nombre supposé calculé ou vérifié. Nouvelle source et nouveau producteur uniquement après arbitrage écrit.

**Lot F (ingénierie prioritaire)** : rédiger un plan spécifique pour `tools/freeze_config.py` testable **sur fixtures synthétiques uniquement**, avec schéma canonique, vérification des chemins autorisés, empreintes de code/config/data, contrôles des entrées absentes/dupliquées, symlinks, correspondance de l'ensemble des fichiers du schéma, refus de mutation et `--check` équivalent, tests de modification de 1 octet et de changement de base. **Ne jamais créer un vrai `configs/FROZEN.json` ni activer l'accès à `monitor` au cours de ce lot.** Les noms d'options et leur sémantique sont à figer dans le plan, pas à deviner au moment de coder. Les fixtures ne doivent contenir aucune donnée EUROFIDAI ni séries 2020+.

**Lot R (après spécification)** : rédiger le contrat minimal de `jepadrift/benchmark_runner.py` et des empreintes de run par rapport au runner PCA 28 existant, **sans dédoubler la logique ni réexécuter les expériences scellées**. Définir interface `main(argv)` et lecture sûre des configurations, validations de sortie, refus d'accès réel sans gel et compatibilité des identifiants de résultats. Le runner global doit être considéré comme **différé** tant que les configurations E5 et le modèle de monitor/holdout ne sont pas figés. Un plan de schéma et des tests de refus/fixtures ne constituent pas une exécution J4.

**GO et propriétaire :** un GO nouveau séparé `21-F` pour la fixture et `21-R` pour le runner (ou seulement le contrat R). Codex peut autoriser les tests et l'ingénierie non expérimentale dans le mandat, après revue du plan, mais doit demander un GO **au chercheur** pour l'activation effective de J4, `FROZEN.json`, accès 2020+ ou changement de protocole scientifique.

### P2 — Stream 19 restant, après audit théorique du 7 novembre

La note `docs/audits/stream_19_theory_spll_20261107.md` est **livrée** : elle distingue N (actifs), k (réservoir PCA), d (sous-espace), p (dimension du détecteur covariance), `K_MP`, coût de mélange, coût de dictionnaire et combinaison du marché avec le résiduel. L'oracle fermé `experiments/e4_oracle_reference.py` prouve `G(N) = N/[1+(N-1)ρ]` pour un déplacement de marché gaussien connu, sous ses hypothèses ; **il ne mesure ni ADD ni pente empirique en N**. Les textes primaires de Kuncheva ont été identifiés ; plusieurs choix de SPLL (estimateur covariance, matrice éventuellement singulière, cluster, seuil, fenêtres) restent à préspécifier.

La prochaine session 19 commence en **mode plan documentaire** : formuler une seule question de recherche non couverte par le full 239 actifs et par l'oracle, choisir les variables tenues fixes (N, k, d, amplitude), la référence moyenne N actifs, PCA spectrale, PCA informationnelle, `P3-CS(b)` et une éventuelle variante SPLL ; spécifier les fonds nuls, segments d'ajustement, calibrations, holdout, FPR(H), RMST, censures, graines appariées, coût CPU/mémoire et statut non-oracle. Séparer les lectures `evidence budget`, `ARL0`, `anytime-valid`, `diffusion` et `RMST(H)`.

**Aucun code de reproduction SPLL** avant contrat fidèle à une référence source, ou étiquette explicite de variante indépendante ; ne revendique pas une reproduction fidèle quand les choix sont devinés. **Aucune campagne E4/N** avant GO scientifique dédié. Un microtest analytique isolé peut être proposé mais demande lui aussi un périmètre clair ; il ne doit pas reproduire inutilement l'oracle déjà scellé.

### P3 — Stream 23 E6, préserver les deux commits non intégrés

`~/JEPA-stream-23`, branche `stream-23`, tête historique `3d0bd207...` avec deux commits locaux (`7e4c7a1`, puis `3d0bd20`). Le review `docs/audits/stream_23_compatibility_2026_11_06.md` est déjà intégré sous `03f1ced` ; il **n'intègre aucun résultat E6**. Sans mutation du worktree d'origine, examiner :

```bash
git -C "$HOME/JEPA-stream-23" status --porcelain=v1
git -C "$HOME/JEPA-stream-23" log --oneline --decorate -4
git -C "$HOME/JEPA-stream-23" log --oneline origin/main..HEAD
```

Avant toute reprise : nouveau plan et GO satisfaisant les **conditions C1–C7** de la revue, dans un **worktree neuf issu de main**, migration des commits dans l'ordre par un responsable désigné, contrôle d'indexation zéro-based versus PCA full un-based, maintien du comparateur d'indice aveugle aux diminutions de variance comme diagnostic spécifique (pas preuve générale de supériorité PCA), reproduction `quick` et `full` si autorisée avec SHA attendus, 13 tests E6, `make check`, et audit statistique D6. Les données D6 et tout rerun E6 sont **hors du présent GO** : demander l'autorisation expérimentale précise. `P4-D` est non calibré sur null indépendant et `P5-D` attend 16 ; ne pas les fabriquer ni déclarer le 23 « livré » par une cherry-pick.

### P4 et suivantes — pièces différées, à maintenir en backlog argumenté

- **16 / J3 (avant 20, 22, 23 phase 2, 26)** : remplacer l'ancien protocole ACP post-JEPA par bottleneck natif 14 ; préspécifier heads odd/even, anti-collapse, splits, graines, coûts, critères de stabilité temporelle et fallback AE/VAE/VQ-VAE ; entraînement **seulement après mandat de reprise JEPA** et validation des références PCA sans oracle, pas dans la présente mission.
- **18** : bloqueur de source/licence/package à résoudre avant tout adaptateur CD-DFM ; le closeout documentaire reste clos.
- **20 et 26** : attendent les checkpoints entraînés 16 ; aucun monitor adaptatif pendant test sans protocole spécifique.
- **21 effectif → 22/J4 → 25 réel** : le gel ne peut être produit qu'après préspécification complète, et le 22 ne se lance qu'avec 16, 17 recevable, 19 si requis, 23 phase 2 et 21 effectif. Historique réel 2020+ derrière le gel, cohorte standard avec 65 séances et cohorte Covid rétrospective sans embargo clairement séparées. Aucun accès réel ni création de `FROZEN.json` par anticipation.
- **15 → 24** : BAF et T-JEPA hors priorité financière ; **28 historique** Electricity hors priorité ; **27 compléments F2/P5** = nouveaux plans si une question indépendante des résultats 28–30 existe.

## E. Protocole de délégation Claude Code : reprise intégrale de la procédure du 7 novembre

### E1. Limite d'agents, exclusivité et absence de perte de contexte

**Deux sessions Claude Code maximum simultanées**, tous modes compris ; recommandation **une pour les tâches partageant la même librairie.** Avant chaque session, consigner `session_id`, propriétaire, branche, worktree, ensemble des fichiers autorisés, imports/outils partagés en lecture **et** écriture, jeux de tests et GO. Deux worktrees ne suffisent pas à isoler des imports de `floors`, `pipelines`, `trace_numbers`, des ressources `.venv`, ou un `make check`. Mettre en place la sérialisation via le registre local `execution-19-21-state.json` et/ou le verrou existant plutôt que d'inventer un nouveau mécanisme sans audit.

Ne change **ni modèle ni effort** d'une session existante. En cas de quota épuisé : préserver session, contexte, plan et dernier état ; ne pas recréer 10 sessions, ne pas purger le contexte ni abaisser l'effort sans décision écrite. Les agents Claude n'ouvrent pas de sous-agents `Agent`/`Task` ; pas de troisième agent caché. Aucune inference Codex consommée en boucle d'attente.

### E2. Phase A — Plan natif interactif, sans implémentation

Après création **sécurisée et contrôlée** d'un worktree neuf (une branche libre, une base effectivement intégrée ; aucun `checkout` dans un worktree possédé par quelqu'un d'autre), expose `.venv`, `external/` et les seuls sous-dossiers `data/raw` nécessaires. Vérifie les options de la CLI installée :

```bash
cd "$WORKTREE_PATH"
claude --version
claude --help
# Exemple à adapter UNIQUEMENT si la CLI effective l'exige :
tmux new-session -d -s jepa-s21-f -c "$PWD" \
  'claude --model claude-opus-5-5 --effort max --permission-mode plan --disallowedTools Agent Task'
```

Dans **cette même CLI interactive**, transmettre le prompt canonique du stream, le GO historique, les documents de replanification et la mission spécifique **PLAN ONLY**. Pas de `claude -p`, ni sortie de plan, ni implémentation, tests applicatifs ou expériences à ce stade. Faire répondre l'agent aux points : hypothèses de validité et cas limites ; frontières prétrain/calib/holdout/monitor ; dépendances exactes ; fichiers propriétaires ; commandes de validation et risques de collision ; API publique proposée ; expériences exclues ; tests négatifs (fuite, résultats fabriqués, source absent, mauvais hash, cov non additive, refus d'accès réel) ; ressources CPU/mémoire ; questions d'arbitrage.

**Codex examine le plan et dialogue avec Claude** dans la même session pour corriger les erreurs ; un plan écrit par Claude n'est pas automatiquement un GO. Si des points scientifiques non délégués restent ouverts, soumettre une décision nette au chercheur puis attendre. Le plan final doit être enregistré **en français** sous `prompts/plans/plan-[ID].md` (par exemple `plan-21-F.md`, avec nom fixé avant écriture) **avant** toute implémentation. GO séparé sous `prompts/GO-stream-[ID].md`, avec « Décision GO intégrée », le SHA du plan, les fichiers autorisés, critères d'acceptation et exclusions. Ne pas usurper une signature du chercheur : indiquer explicitement « GO Codex au titre du mandat délégué » ou « GO du chercheur », selon la source réelle.

### E3. Phase B — Implémentation dans la même session après GO

Seulement après GO enregistré, quitter le mode plan via le mécanisme officiel **dans la même session CLI** ; vérifier le changement effectif de permission. Interdire `--dangerously-skip-permissions` par défaut. Conduire le travail par tests RED→GREEN, fixtures contrôlées, témoins négatifs et validations ciblées. L'agent peut poser des questions techniques, et Codex y répond après confrontation avec les sources. N'exécute aucune campagne scientifique hors du GO et ne retouche jamais les anciens résultats pour faire passer un test.

Si l'implémentation révèle un nouveau contrat scientifique, un passage à la donnée réelle ou une incompatibilité de schéma amont : **STOP**, enregistrement de la cause et nouveau plan/GO, pas d'extension implicite. Ne pas utiliser `claude -c -p`, `codex exec resume --last` ou des sessions headless de remplacement pour contourner un GO, une revue ou un quota.

### E4. Surveillance persistante et réveil automatisé

Conserver le **moniteur utilisateur crond** installé le 7 novembre : une entrée unique toutes les 30 minutes vers `tools/ops/monitor_claude_sessions.sh`, verrou `flock`, registre `logs/claude_sessions.json`, journaux et drapeau `logs/NEEDS_CODEX_REVIEW`. Vérifie la fréquence, la cible, la dernière exécution, les droits de fichiers, la fermeture des anciennes sessions et l'absence de second cron. Ce système passif **signale** l'état sans consommer de tokens d'inférence en attente.

Le script compagnon **`tools/ops/auto_wake_codex.sh`** assure la liaison réactive : il détecte l'apparition d'un nouveau hash dans `NEEDS_CODEX_REVIEW` et injecte `continue` avec le délai de stabilisation de 500 ms vers l'orchestrateur Codex. Dès réveil, Codex prend la main, audite l'alerte (plan prêt, question bloquante, quota, livrable à valider), instruit la réponse ou émet le GO, puis **archive le drapeau sous verrou** selon le protocole établi pour clore le cycle d'alerte. Ne pas couper une session qui n'appartient pas au stream contrôlé. Aucun polling actif par inférence, aucune boucle `sleep` dans Codex pour attendre les progrès.

### E5. Clôture et intégration sérialisées

Avant clôture, auditer le **diff complet**, traçabilité, test de non-fuite, politique CRLF/J1, D8 FAIL, conformité Go, jeu de sorties et hashes. Demander à Claude de produire son wrapup **en anglais** avec les six rubriques : Context, Validated Results, Errors and Dead Ends, Current State, Vigilance Points, Recommendations. Puis `/exit` ; vérifier le processus réellement arrêté ; fermer uniquement le tmux possédé.

Quand tous les agents concernés sont arrêtés :

1. Contrôler l'absence de collisions et avancer seulement la branche possédée vers le main publié, par fast-forward/reconciliation explicite non destructrice.
2. `tools/reindex_graphify_jcodemunch.sh` en mode AST sans résumé IA ; les explorations LLM de Graphify/jCodeMunch ne sont pas implicitement autorisées.
3. `make check`, tests ciblés et `make prompts-check` **si les prompts sont modifiés** ; rapporter les véritables nombres de PASS/FAIL/SKIP et la durée. Le dernier compte rendu utilisateur donnait **1 003 PASS, 5 skips D4**, à recontrôler si l'environnement change ; les anciens **44 contrats PCA** doivent rester présents et valides.
4. Recontrôler E2 SHA disque/index/CRLF, E3 et `docs/DEVIATIONS.md`, statuts des sorties historiques.
5. `git status`, stage par **chemins explicites**, `git diff --cached --check`, inspection du diff. Exclure logs, caches, secrets, données EUROFIDAI, fichiers >50 Mo et `trials.csv` full, toute nouvelle identité d'auteur non anonyme.
6. Commit Conventional Commits sans trailer/co-auteur ; examiner **toute la plage** destinée à être poussée ; intégrer sur `main` par fast-forward supervisé, `git push origin main` si la politique de publication reste satisfaite. Jamais de push forcé ou de branche de stream envoyée par accident.
7. Vérifier HEAD local, distant, états des worktrees, fermeture sessions, cron unique, registre et alertes ; mettre à jour l'inventaire d'avancement. Un commit documentaire ne transforme pas un stream d'expérience en stream clos.

Le hook `make check` peut prendre davantage que les cinq minutes théoriques ; ne supprime pas de tests pour raccourcir un contrôle. Les cinq skips D4 en worktree sont à qualifier, pas à présenter comme validation privée. Si une anomalie E2, une modification non autorisée de protocole ou une contamination 2020 apparaît, STOP et diagnostic ; trois essais au plus pour problèmes de pure infrastructure, jamais pour réessayer une hypothèse qui échoue.

## F. Première livraison exigée de cette nouvelle instance, AVANT tout lancement

Produis **dans ta réponse au chercheur** :

1. HEAD local, `origin/main` et commit distant réellement contrôlés ; travaux non suivis et worktrees, sans les écraser ; statut E2/E3/PCA scellé.
2. Tableau de tous les streams de 01 à 31 (avec 08b, 11b et double identité 28) : `CLOS`, `PARTIEL`, `BLOQUÉ`, `DIFFÉRÉ`, preuve Git + wrapup + livrables, propriété des worktrees, dernière action nécessaire.
3. Statut opérationnel de `auto_wake_codex.sh` (commit `924c97f`, session hôte `codex-watcher`, cible tmux vérifiée) **et** état réel du cron/`tmux`/registre.
4. Queue de tâches minimale 21-F, 21-R, 19, 23 avec dépendances, GO nécessaires, propriétaires de fichiers et risques de modules partagés. Préciser ce qui est autorisé **maintenant** et ce qui attend une décision du chercheur ; ne pas inférer une autorisation E4/J4/JEPA.
5. Résultat des vérifications réellement exécutées, statut d'exécution des 1 003 tests (rapport historique ou nouveau run), drapeaux d'alerte non acquittés et conditions de reprise.

**Après cette première livraison**, si le préflight est sûr, commence par **le plan du Lot F du stream 21**, puis sa revue et son GO explicite. La note 19 peut être planifiée en lecture seule en parallèle uniquement si elle n'utilise aucun module partagé et qu'un deuxième créneau est réellement libre. Ne démarre pas la campagne E4, la reprise 23, le préentraînement 16 ou le gel J4 sous prétexte de combler les sessions disponibles. La première tâche qui requiert un consentement scientifique nouveau doit être présentée au chercheur avec deux choix concrets et leurs conséquences expérimentales.

**Format de la communication :** français, sans formule d'assurance gratuite, avec état confirmé vs supposé, références de commit et chemins contrôlés. Tout travail non lancé doit rester désigné `NON EXÉCUTÉ`. Ne prétends jamais qu'une alerte cron est une décision d'orchestration.
