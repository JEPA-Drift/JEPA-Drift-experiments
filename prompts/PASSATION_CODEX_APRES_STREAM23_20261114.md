# Passation à une nouvelle instance Codex — après le stream 23

Date : 2026-11-14 UTC. Dépôt : `/home/m53/JEPA-Drift-experiments`.

## 0. Autorité et première action

Le chercheur a demandé à l'instance précédente de terminer uniquement le stream 23, puis d'arrêter tous
ses agents et de transmettre cette passation. Elle ne doit pas reprendre elle-même le stream 32.
La nouvelle instance reprend la supervision architecturale et l'intégration Git, sans écrire directement
le code applicatif. Le choix scientifique prioritaire est PCA-INFO-ONLINE, stream 32 ; les autres streams
restent dans l'inventaire avec leurs portes propres. Cette passation ne crée aucun GO scientifique.

Lire obligatoirement, dans cet ordre :

1. `CLAUDE.md`, mémoire canonique ; `AGENTS.md` est son lien relatif, ne pas en créer une deuxième copie.
2. **La version locale révisée de `prompts/Protocole Codex.md`**, même si elle n'est pas encore commitée.
   SHA-256 reçu : `5eb63af813eb5e1af04c344b24f8662329c1abb04d38412fc9512c476770dae8`.
3. `prompts/streams/13_CODEX_AMORCAGE_PCA_INFO_ONLINE_2026_11_14.md` et l'intégralité de
   `prompts/streams/32_STREAM_PCA_INFO_ONLINE_SPEC.md`.
4. Les rapports et GO précis des lots concernés ci-dessous. `INDEX.md` contient des états historiques
   obsolètes : ne pas en déduire les clôtures ou les autorisations actuelles.

Avant toute action : vérifier `git status`, les références locales/distantes, les worktrees, les vrais PID
Claude, les processus scientifiques et le verrou `logs/.jepa_execution.lock`. Ne pas assimiler une session
tmux conservée à un processus Claude actif. Maximum quatre instances Claude Code simultanées, toutes comprises.

## 1. Protocole révisé à appliquer aux prochains lancements

La révision corrige l'ancien contournement du mode Plan natif par `superpowers:writing-plans`.
Ne pas recopier les anciens lancements sans ces corrections.

- Phase A : Plan natif, lecture seule stricte, modèle Opus et effort Max explicites, `--permission-mode plan`,
  `--disallowedTools "Skill"`, `--disable-slash-commands`, sortie JSON. Injecter les invariants scientifiques
  dans la mission : le sous-agent natif Plan ne charge pas automatiquement toute la mémoire projet.
- Pas de `--remote-control` dans une invocation headless `claude -p` redirigée. Cette option est réservée
  aux sessions interactives de supervision. Respecter les options réellement installées.
- Capturer le plan natif, inspecter aussi les refus `ExitPlanMode` si la sortie finale ne contient pas le plan,
  refuser une capture vide. Enregistrer le plan canonique dans `prompts/plans/plan-[XX].md` avant TDD.
  Avec Codex, employer `apply_patch` pour les éditions manuelles et les schémas réellement exposés.
- Revue contradictoire, puis GO technique écrit `prompts/GO-stream-[XX].md` et section
  « Décision GO intégrée » dans le plan. Aucun `docs/superpowers/plans/`.
- Phase B propre, asynchrone, strictement fondée sur le plan et le GO. Ne pas réinvoquer brainstorming ou
  writing-plans pour refaire un plan approuvé. Un GO technique ne vaut jamais GO de pilote ou de full.
- Préparer les worktrees avec `.venv` et `external` partagés par liens absolus ; `data/raw` est un répertoire
  réel, avec seulement les sous-répertoires autorisés exposés individuellement. Pas de données réelles pour 32.
- Tous les calculs, tests globaux et intégrations sont sérialisés sous le verrou partagé. Pas de boucle de
  surveillance ni de sommeil shell : instantanés bornés, puis rendre la main si tous les flux tournent.
- Clôture : processus éteint, absence de verrou Git résiduel, wrapup natif installé en anglais aux six sections
  de `CLAUDE.md`, réindexation autorisée, `make check`, staging explicite, audit puis commit/push contrôlés.
  Respecter la procédure Git courante de `CLAUDE.md` et du protocole ; jamais force, stash/reset d'un tiers,
  branche de travail poussée comme telle, données privées ou fichier de plus de 50 Mo.

## 2. Réception stream 23 / E6 phase 1

**CLOS ET PUBLIÉ : `main`, `origin/main` et la référence distante sont à
`e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a`.** Commit :
`feat(e6): integrate historical phase one with bounded pre-2020 reader`.
Le hook inchangé a exécuté `make check` : 37 + 1 335 = **1 372 tests passés, cinq skips D4 seulement**,
aucun échec ; gardes torch et PCA-G1 exécutées. Le worktree 23 est propre. Les 27 chemins de la plage
ont été audités ; plus gros fichier 407 472 octets, aucun chemin privé, trailer ou scellé modifié.
Intégration fast-forward puis `git push origin main`, sortie 0 ; empreinte distante revérifiée.

Worktree d'intégration : `/home/m53/.codex/worktrees/2160/JEPA-Drift-experiments`, branche
`stream-23-phase1-20261113`. Base publiée avant ce lot : `461f2b13894be2cca954676dc3aab10e0b640a2b`.
Le worktree historique `/home/m53/JEPA-stream-23` reste intact à
`3d0bd2071cb86afc6b196b5020ff729204746a93`. Les deux commits historiques ont été réutilisés dans leur ordre.

Le seul changement applicatif nouveau est le lecteur D3 borné pré-2020, avec contrats anti-lecture complète.
Les noyaux numériques, paramètres, graines, colonnes et calculs de Wilson historiques sont conservés.
Source reçue : `5af91240df658f8ec7e8f45139cf74144ed9c6665d52bc6f8aec67da42902855`.
Tests reçus : `39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc`.

- RED initial : 14 échecs attendus ; GREEN : 14 tests ; mutant de lecture complète : 2 échecs attendus.
- Suite E6 ciblée : 27 tests passés. Quick jobs=1 et full jobs=48 reproduisent les SHA attendus.
- CSV quick : `874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2`.
- CSV full : `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249`, 190 lignes : 112 D5 + 78 D6.
  Les quatre figures PNG/PDF reproduisent aussi leurs empreintes archivées.
- D3 consommé : 3 775 × 239 observations pré-2020, dont 941 jours de calibration.
  Empreinte consommée : `d18ddc3b541ea3037ae9a817b40bd43ee9568c71e62eeeb095fda8c2bd2a4b6c`.
- Premier full : OOM sous l'enveloppe d'ingénierie 8 Gio, sans sortie ni divergence numérique établie.
  Une reprise unique autorisée à 64 Gio, jobs=48 inchangé, a réussi : 815,51 CPU-s, 44,89 s murales,
  pic mémoire agrégé 14 849 028 096 octets. Le STOP initial et son GO d'amendement sont conservés.
- Coût couvert avant clôture : 1 182,820667 CPU-s, échec inclus. Ne pas ajouter le compteur de cgroup
  de la reprise, 815,577751 s : il chevauche GNU time. Les opérations de clôture sont comptées séparément.
- D5 : calibration indépendante, inférence conditionnelle au fit. D6 : descriptif, calibration in-sample,
  pas d'IC de FPR indépendant ni d'égalité de FPR établie. Délais restreints, pas ADD de Lorden.

Références : `docs/audits/stream_23_compatibility_2026_11_06.md`, conditions C1–C7 ;
`docs/audits/stream_23_phase1_integration_20261114.md`, SHA
`339d62310ef9bff62a002d0e67b0efbdb726851ebd1f1f836164e5968182686b` ;
`prompts/plans/plan-23-phase1-20261113.md`, SHA
`bd1301d29ab28944cd3c1803fd2da1ba2e516f415848856ccd7146c0eeba999e`.
Les GO, STOP et wrapups sont livrés avec le lot. La phase 2 JEPA/P5-D reste interdite.
Wrapup final : `prompts/wrapups/wrapup-23-phase1-20261113.md`, SHA
`ef5455d48b29562a167c101b59e712a004d063d591544fd6ee2fd68c15ffdec1`.
Clôture mesurée : quatre invocations de réindexation, 34,46 CPU-s cumulées, échecs compris ; hook/commit
624,30 CPU-s, 597,39 s murales, RSS maximal par processus 3 824 536 Kio ; push 0,10 CPU-s.
Total des invocations ainsi couvertes : 1 841,680667 CPU-s. L'administration auxiliaire non instrumentée
reste hors de ce total, pas égale à zéro. Aucun coût de 23 n'est ajouté rétroactivement au budget E4.

## 3. E4 déjà clos : conserver les résultats et la réserve comptable

Commit publié E4 : `461f2b13894be2cca954676dc3aab10e0b640a2b`.
Rapport : `docs/audits/stream_19_e4_full_20261114.md`, SHA
`34c450085c80bb6e9653c1d9737d0506f68d6120aac7d2de45e0c7c3d6c6d901`.
Les 354 partitions, fusion, analyse, vérification, publication et vérification portable sont terminées.
91 fichiers déclarés, 560 blocs, 42 calibrations ; 84 cellules par lecture, 12 contrastes tous
`NOT_IDENTIFIED`, 14 flags prédictifs de FPR conservés. Les références O-dir et O-score1 sont ORACLE,
t7 porte son proxy d'information gaussienne. Aucun résultat ne qualifie une sélection apprise sans oracle.

Publication : `PUBLISHED.json` SHA `5c318af8768b7f1b83e08e30a20dd57067010ad05bf7b70a0cb31d3c03fd544d` ;
manifeste SHA `b7514d600af40dc5e10ac8738333c25059218bd184c4a49008adbe2b5de6d69c`.
Le chercheur a autorisé explicitement la finalisation **sans certificat du plafond** ; GO
`prompts/GO-stream-19-e4-finalization-accounting-reserve-20261114.md`, SHA
`1f5edab746e526aaf2b9543eace6947f0172750f1d968f46443e361822a5f5c7`.
35 653,56 CPU-s sont mesurées jusqu'au push ; certains surcoûts restent UNKNOWN. Aucun certificat 24 h,
aucun dépassement établi, aucune augmentation rétroactive du budget. Le stream 19 historique reste PARTIAL.
La synthèse anglaise facultative E4 n'a pas été lancée, priorité 32 maintenue.

## 4. Priorité suivante : stream 32 PCA-INFO-ONLINE

Worktree neuf déjà préparé : `/home/m53/.codex/worktrees/364e/JEPA-Drift-experiments` ; branche
`stream-32-pca-info-online-20261114`, base E4 ci-dessus. Aucun lien vers les données brutes.
Les deux nouveaux prompts y ont été copiés à l'identique, ainsi qu'un GO **documentaire seulement** :
`prompts/GO-stream-32-planning-20261114.md`, SHA
`ccdd9c872197dabe553c5bf6458cfa218f4f252590b9030f11c442ca127471b4`.

Un plan natif v1 est arrivé pendant la clôture 23 :
`/home/m53/.claude/plans/pasted-content-id-9c4b-mission-polymorphic-scott.md`, 46 025 octets, SHA-256
`35bd58e1d1267ff08940e5faca8987d628a9833570217e5042bb8485c6580284`.
**NON REVU, NON APPROUVÉ**, reçu sans poursuite de l'orchestration à la suite de la dernière instruction.
Aucun GO technique, pilote ou full. Le worktree 32 reste à l'ancienne base E4 : sa réconciliation sur
`e33ac1d` incombe à la nouvelle instance avant une future implémentation, sans écraser ses trois entrées
documentaires non suivies. L'ancien client est antérieur à la dernière révision du protocole ;
ne pas le reprendre en supposant que ses options bloquent Skill et les slash commands. Réutiliser ce
contenu comme entrée, puis appliquer la Phase A corrigée et sa revue. Ne pas refaire les lectures
déjà reçues sans besoin concret. Le dialogue natif « Ready to code? » n'a pas été approuvé.

Identités des entrées : amorçage SHA
`6c047b4447d752462efb687e7b1192a3df503f572d37405099e7738386bb4b9d` ; spécification SHA
`db2ef8717e56d36b41a7ff805cea8a21c57ab9fcafd5d56ec96e9b21ab97201b`.
Mission et pré-revue conservées dans `logs/orchestration_20261114/mission-32-native-plan.md` et
`logs/orchestration_20261114/prereview-32-math-time.md` du worktree principal.

Contrats essentiels à retrouver dans le futur plan, sans les présenter comme des choix scientifiques approuvés :

- Strictement synthétique, changement de moyenne, PCA initiale figée. Huit méthodes :
  ORACLE/ONLINE × INFO/PREFIX × MIX/AFF ; étiquettes oracle explicites. Baselines variance seule,
  sous-ensemble ex ante indépendant et FULL_K ; véritable CPV90 ou statut OUTSIDE_UNIVERSE.
- Comparaison centrale ONLINE_INFO_MIX contre ONLINE_PREFIX_MIX, puis baselines fortes, à FPR atteints
  comparables. Tri top-q et glouton sont le même optimum additif, pas deux bras expérimentaux.
- Univers résiduel PC2..PC(K+1), distinct d'une strate PC1-inclusive ; PC1 ne disparaît pas silencieusement.
  Définir tous les supports par indices canoniques. F0 isotrope, F1 faible variance, F2 non contigu,
  F3 marché séparé : ces étiquettes propres à 32 ne remplacent pas les familles d'injection historiques.
- `S_t` est choisi avec le passé jusqu'à t−1, avant `Y_t`, sans accès à la dérive, l'onset, la famille ou au q vrai.
  Un seul masque global prévisible pour tous les débuts de segment ; jamais de relecture rétroactive avec
  le masque courant. Le screening peut lire tous les axes passés, dont le coût doit être déclaré.
- Proposition d'estimateur : moyenne passée de fenêtre m, normalisation et correction de variance explicites,
  `qhat = 0.5 * max(0, bhat**2 - 1/m)` dans le cas standardisé. Le clipping est biaisé ; ne pas dire « sans biais ».
  Fenêtres 32/128 proposées, initialisation et égalités déterministes à figer avant les alternatives.
- Sous vrai Gaussian diagonal, information additive exacte. Sous PCA/LW apprise, le score additif plug-in est
  un substitut : ne pas le confondre avec la KL jointe projetée. Le centre estimé conserve un biais nul
  conditionnel ; une correction de variance ne le retire pas. F0 uniforme dans un repère appris dépend
  géométriquement du fit : résoudre explicitement la convention population versus conditionnelle au fit.
- Même mélange gaussien masqué pour tous les bras, mêmes prior et règles de franchissement. Le prior proposé
  dépend de K, pas du d sélectionné. Le test statique réutilise le noyau historique avec ce même prior ;
  l'ancien constructeur avec prior dépendant de d ne serait pas une identité du détecteur.
- Chaque segment masqué est une martingale sous iid N(0,I), avec filtration du passé complet. Ce n'est pas
  la vraisemblance de tout le panel quand le screening lit les axes exclus. Le maximum sur les onsets
  n'est pas lui-même un e-processus ; il nécessite sa calibration propre.
- M(d,gamma_M) est un coût fluide substitutif, pas un délai exact ; gamma_M est distinct du seuil opérationnel.
  Énumérer tous les préfixes, pas d'arrêt au premier incrément défavorable. L'affine historique est une corde
  1..20 ; l'affine 1..16 proposée exige une nouvelle définition, sans modifier le producteur scellé.
- Rôles FIT_NULL, DEVELOPMENT, CAL_NULL, HOLDOUT_NULL, TEST_ALT isolés par SeedSequence ; appariement des
  trajectoires et bootstrap des contrastes. Calibrer chaque politique complète et son identité.
  L'oracle conserve sa direction indépendante des innovations nulles pendant la calibration : mettre
  delta=0 dans sa sélection fabriquerait une autre politique.
- Rang prédictif : réutiliser exactement rank_threshold(..., "GE") et nextafter. Garantie marginale
  calibration + nouvelle trajectoire, conditionnelle au fit figé, pas au seuil réalisé. Sous LW/t7,
  échangeabilité des trajectoires ne signifie pas martingale gaussienne.
- FPR holdout, Wilson, RMST censuré et bootstrap apparié ; ni Lorden ni exposant universel.
  FPR comparables : critère d'équivalence préspécifié, pas chevauchement des IC. Traiter les zéro discordances
  sans IC artificiellement nul ; déclarer famille et multiplicité. Une alarme OR entre bras n'a pas alpha
  par simple calibration individuelle. Inférence conditionnelle aux fits et calibrations.
- Propositions non approuvées à geler : exact-PC Gaussian puis fitted-LW Gaussian ; N={32,239}, K=20,
  H=250, alpha=.05, T_fit=1000, I*=.25 ; autres fenêtres/grilles/t7 séparément déclarées, jamais ajustées
  après les performances. Le plan doit décider ses options avant tout pilote autorisé.
- Schéma nouveau `pca_info_online/1`, sorties bornées/partitionnées, reprise atomique à identité contrôlée,
  déterminisme jobs=1/3 ou 8, télémétrie de sélection produite sans chargement global non borné.

Synchronisation documentaire à implémenter par Claude après GO technique : le titre actuel du nouveau prompt
n'est pas `## PROMPT 32 —`, EXPECTED_IDS omet 32, les tests comptent 33/29. Étendre minimalement contrôleur,
tests et INDEX ; conserver les 33 anciens blocs ; resynchroniser le master uniquement par
`tools/check_prompts.py --sync-master`. Ne pas annoncer prompts-check réussi sur 32 : il n'a pas été exécuté.

Ressources proposées seulement : 32 Gio, pilote de 4 CPU-heures au maximum, 45 minutes par invocation,
jobs=8 ; profilage 1/4/8/12, puis 16 sous GO/charge/RAM. 24 cœurs physiques, pas 48 SMT assimilés à un gain
linéaire. BLAS par worker mono-thread. Aucun coût smoke/pilote mesuré, aucun budget full garanti.
Séquence : plan revu → GO technique → TDD/revue → GO chercheur pilote borné → coût mesuré/grille figée →
GO confirmatoire full. Aucun GO de données réelles, JEPA, J4 ou changement de covariance comme cible principale.

## 5. Streams conservés en attente, sans reprise automatique

### 27 — E10, complément F2 sur D3

Plan v5 natif : `/home/m53/.claude/plans/lis-la-mission-compl-te-purrfect-sparkle.md`, SHA
`01596fd3c53c1cf31394118ce2e267b1d290b0a3935eb6781590a1df0a12eb5b`.
Worktree conservé `1a88`, ancien client déjà archivé. Plan acceptable ; aucun nouveau code/runtime autorisé.
O1=full et O2=brut définitivement décidés, ne pas les rouvrir.

Préserver P3-C/full ; géométrie d'injection sur X_raw de calibration, X_fit indépendant et X_mon symétrisé
distincts ; K_MP=10, D_factor=11, K_inj=11 à vérifier, résidualisation GLS contrôlée, distincte de
l'orthogonalité PCA. H0 full neuf, séparé du témoin H0 factor/F1 scellé. D6 d3_239 pré-2020 seulement,
SR={4,8,16}, information gaussienne conventionnelle étiquetée proxy, P1-C quatre bras, P3 anytime-valid.
Refus d'un row group qui franchit 2020 ou ne permet pas de certifier la frontière, sans contournement.

P7 reste une proposition de tolérances d'ingénierie. P8 : test binomial unilatéral exact, famille fermée de
21 unités, Bonferroni, eta=.05, méthodologiquement recevable pour détecter un excès de FPR. **Approbation
scientifique toujours distincte et absente.** Une non-réjection ne certifie ni calibration ni FPR égales.
B-INT-1 concerne les tests historiques chars, établi statiquement ; B-INT-2 désigne 12 fichiers candidats,
pas 12 blocages prouvés. Préparer la matrice des chemins effectivement exécutés avant qualification future.
GO de code puis runtime distincts nécessaires ; aucun P5-C/JEPA. Ne pas relancer F1 scellé.

### 21 — G9/G10, E-1, production runner

Plan documentaire v2 : `/home/m53/.claude/plans/lis-la-mission-compl-te-dazzling-giraffe.md`, SHA
`105a67647ad212502795e180e221a40d5d31364b4aaf4125d66c2f6778b9419e`, worktree `5e00`.
E-13 maintenu : runner DEFERRED, cibles UNQUALIFIED, portes non qualifiées OPEN. Les livrables 21-F/21-R
et cartographies déjà livrés ne sont pas à refaire. Aucun GO d'implémentation, J4 ou E5.

Propositions G9/G10 et erratum E-1 restent PROPOSED — NOT APPROVED : ordre normatif des refus versus ARGV
atteignable, descripteurs protocol/data/reader et preuve consommée, identité de variante/exécution,
ORIGIN avant import, racine approuvée, workers, BLAS/dtype, reprise et preuve incomplète. Matrice G1–G10,
Q1–Q7 distingue conception possible, code après approbations et qualification scientifique bloquée.
Un null/TBD, digest arbitraire ou chemin vers un GO ne qualifie rien. La fin E4 n'est pas un prérequis
à la rédaction G9. Ne pas implémenter un runner qui refuse tout comme substitut à la conception.

### 16 — J3 CA-T-JEPA et critère RankMe

Plan v2 conservé sans modification :
`/home/m53/.claude/plans/read-home-m53-jepa-drift-experiments-log-cheerful-sloth.md`, SHA
`8d25c3f1c3ffbe77cd182ae8d9398420e0570b45f2a5276cfe33e5114af09f90`, worktree `0af0`.
Plan acceptable pour présentation, pas approuvé pour code/entraînement. Goulots natifs d={2,4,8,16},
pas d'ACP après entraînement. Qualification des représentations distincte de la détection.

Note mathématique autonome : `/home/m53/.claude/plans/pasted-content-id-25a4-mission-adaptive-gosling.md`,
SHA `e1ff4bdba2cec139a745a531b3f73fcdb7595ad0604058815a08b05d766e5365` ; réception Codex
`/home/m53/.claude/plans/reception-codex-rankme-16-20261114.md`, SHA
`c4a93ea373796c7a2099f0200b43e327e48cc7151230ec10fc642720cb82317b`.

Conclusion centrale : à d=2, RankMe_c >= .5d est la borne triviale >=1 ; une représentation centrée de
rang 1 avec deux colonnes identiques variables satisfait aussi n_active=d. La conjonction n'exclut donc
pas le rang 1. Diviser RankMe par d et ajouter epsilon aux poids sont des conventions différentes.
La note propose des conditions spectrales alternatives, aucun seuil nouveau n'est approuvé. Lire aussi
les réserves de réception : hypothèses de Marchenko–Pastur plus fortes que la seule isotropie, seuil de
corrélation pour exclure une paire dupliquée, centrage des constantes et dépendance sérielle.
Aucun entraînement, pilote, test numérique ou GO J3. Arbitrage scientifique anti-collapsus nécessaire.

### Autres streams et compléments

Inventaire documentaire borné, confronté à Git au HEAD E4 ; les absences ci-dessous concernent les fichiers
suivis et les documents inspectés, pas une garantie sur tout travail local ignoré. Aucun runtime de ces
streams n'a été exécuté pour cet inventaire. L'ancien calendrier n'accorde aucun GO.

| Stream | État établi et prochaine porte | Preuve à relire |
|---|---|---|
| 15 — T-JEPA BAF | Différé ; pas de plan/GO/wrapup ou livrable attendu repéré. Socle BAF/torch disponible, entraînement/sélection/extraction à planifier et autoriser séparément. | `docs/audits/streams_01_27_relevance_2026_11_06.md`, prompt 15 |
| 17 — IPCA | Ingénierie P4-C intégrée, commits `6ed8f8a`, `b95f077`. **P4-D reste FAIL/non calibré**, pas une référence J4 qualifiée. Nouveau contrôle indépendant sous GO scientifique. | `prompts/wrapups/wrapup-17.md`, `prompts/GO-stream-17-D3.md` |
| 18 — CD-DFM | Clôture documentaire intégrée `ef77886`, modèle bloqué : paquet upstream absent au pin. Résoudre disponibilité, conditions d'utilisation et écart d'entrées avant nouveau pin/plan/GO ; pas de substitut implicite. | `docs/sections/cd_dfm.md`, `prompts/wrapups/wrapup-18.md` |
| 19 historique — N/SPLL | PARTIAL malgré E4 clos. P3-KF/SPLL non livré ; variantes, clustering, covariance, fenêtres, représentation et calibration à décider sous nouveau GO. | `docs/audits/stream_19_theory_spll_20261107.md`, rapport E4 full |
| 20 — transmission/dictionnaire | Différé/non qualifié. Dépend notamment de 16 ; 17 existe, 18 indisponible. Nouveau protocole et GO avant matrices et dictionnaires. | Audit 01–27, prompt 20 |
| 22 — E5/J4 | Bloqué par modèles 16, gel validé 21, comparateurs qualifiés dont limitation P4-D, et E6 phase 2. Réécriture documentaire sans GO expérimental. | `prompts/streams/07_STREAM_22_E5_J4_REWRITE.md`, prompt 22 |
| 23 — E6 compléments | Phase 1 bornée seule livrée ici ; P4-D reste soumis à sa qualification, phase 2 P5-D dépend de 16 et de GO spécifiques. | Rapport d'intégration 23, prompt 23 |
| 24 — E9 BAF | Différé/non qualifié, dépend de 9 et 15 ; ordre, échangeabilité et null à fixer avant GO expérimental. | Audit 01–27, prompt 24 |
| 25 — E8 régimes réels | Différé/non qualifié ; gel 21, pipelines et autorisation explicite des fenêtres réelles. L'exception QA globale ne l'autorise pas. | Prompt 25, rapport E4 full |
| 26 — E7 absorption | Différé/non qualifié ; dépend de 14/16, adaptation causale à approuver, 2020+ soumis au gel et à un GO. | Audit 01–27, prompt 26 |
| 28 — Electricity/E11 | Mission historique distincte de 28 PCA, différée ; loader et expérience spécifiques non repérés. Construction, désaisonnalisation, null et campagne à autoriser ; SWaT/WADI conditionnels aux accès. | Audit 01–27, `prompts/streams/prompt-28-e11.md` |
| 28 PCA | Producteur historique `experiments/pca_drift_benchmark.py` et résultats scellés existants. Ne pas le modifier pour fabriquer 32 ; réutiliser seulement les noyaux appropriés. | `prompts/streams/28_STREAM_PCA_DRIFT_RUNNER.md`, contrats PCA |
| 29 — tables PCA | Intégré `6f9322b`, publication full `87a15ad`, contrat `pca_drift_tables/1`. Pas de nouvelle simulation ni changement de contrat implicite. | `docs/audits/stream-29-delivery.md` |
| 30 — figures PCA | Intégré `b025450`, figures full `1172855`/`87a15ad` et corrections ultérieures. Préserver covariance exploratoire et familles de détecteurs distinctes. | `prompts/wrapups/wrapup-30.md` |
| 31 — tooling/QA PCA | Intégré `20ad9e8`, correctif/QA `69d5624`. STOP historique 43/1 conservé, réception 44/0/0 avec G1. Pas de nouvelle campagne autorisée. | `docs/audits/PCA_CONTRACTS_VALIDATION.md`, `prompts/wrapups/wrapup-31.md` |

Les socles et lots déjà intégrés ne sont pas à réimplémenter par lecture littérale de l'INDEX historique.
Les nouvelles sorties 32 ont leur propre schéma et ne remplacent pas les scellés PCA/E2/E3/E4.

## 6. Environnement, intégrité et accès

Python de projet : `/home/m53/JEPA-Drift-experiments/.venv/bin/python`, y compris depuis les worktrees.
Ne jamais exécuter les sciences avec le Python Trading seul. NumPy épinglé, BLAS/OMP/MKL=1,
MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Torch conda-forge via
`PYTHONPATH=.:external/torch-cf-shim` pour les checks qui doivent exécuter les gardes torch.
Le Python Trading a servi uniquement à l'administration du cache MCP, pas aux calculs du dépôt.

Le G1 PCA full doit réellement s'exécuter lors des checks autorisés : entrée externe conservée
`/home/m53/JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv`, SHA
`40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c` ; ne pas la recopier/stager.
L'exception des checks historiques globaux est documentée dans `prompts/GO-legacy-global-check-access-20261113.md` ;
elle n'autorise pas une nouvelle expérience réelle ni le monitor pour 32. D4 indisponible = skips explicites ;
une disponibilité inattendue ne constitue pas une autorisation de lecture.

Préserver les scellés E2/E3/PCA et l'Article B local en lecture seule au commit imposé par CLAUDE.md.
Pas de données privées, J4/FROZEN activé, accès aux valeurs 2020+, JEPA/VAE ou phase 2 par implication.
Les données brutes EUROFIDAI ne quittent jamais la machine. Aucun recalage scientifique pour faire coïncider
un hash, aucune exclusion opportuniste ou adaptation après résultats.

Incident administratif de clôture 23 : jCodeMunch 1.108.268 confondait l'ancien index local du worktree 2160
avec son ancre Git. Deux tentatives ont montré la récurrence après reconstruction. Sauvegarde ciblée puis
effacement du seul champ git_root de cet index local, sous assertions propriétaire et source exacte :
la réindexation et la résolution locale suivantes ont réussi. Aucun paquet ni autre index modifié.
Archives et coûts dans `logs/23-phase1/closeout-20261114/` du worktree 2160 ; ne pas supprimer les caches
globalement. Graphify AST seul, résumés IA désactivés ; Graphify/jCodeMunch restent explicites hors clôture.

## 7. État final de l'arrêt et consigne à la nouvelle instance

Arrêt vérifié après publication, le 2026-11-14 à 04:03:54 UTC : `pgrep -x claude` ne retourne aucun processus ;
aucun sous-agent Codex actif ; verrou d'exécution libre. Les trois clients restants ont quitté nativement,
sans approbation du menu « Ready to code? » de 32. Les quatre créneaux sont donc libres, pas seulement inactifs.

| Dernier occupant | Identité préservée | État final |
|---|---|---|
| 23 | UUID `34422c08-7f4f-44bc-86bf-db27fb842976`, ancien PID 2846624 | Déjà éteint avant intégration, lot clos et publié |
| 21 | UUID `cfb93c5c-5e9f-438b-9a99-26a90f592853`, ancien PID 2846634, worktree `5e00` | Éteint, documents conservés, pas de code |
| 16 | UUID `306a2445-e9d2-4d1c-b9e1-91d7c41a7c50`, ancien PID 3585960, worktree `0af0` | Éteint, plan v2 conservé, pas d'entraînement |
| 32 | UUID `6d4d5143-6340-40a3-a95e-9985c4b9c45f`, ancien PID 3766821, worktree `364e` | Éteint, plan v1 NON REVU conservé, pas d'implémentation |

Archive consolidée : `logs/orchestration_20261114/handover-stop-20261114/` du worktree principal.
Elle contient plans 16/21/27/32, note et réception RankMe, copie exacte du protocole révisé, captures avant
arrêt et historiques JSONL finaux 16/21/32 ; `SHA256SUMS` vérifié. Archives antérieures E4/23/RankMe conservées.
Aucun worktree, branche, résultat ou contexte natif n'a été supprimé. Tous les `required` du registre des
sessions sont à false ; aucune relance automatique. Les entrées Git locales utilisateur restent intactes :

- modification non commitée de `prompts/Protocole Codex.md`, SHA indiqué au §0 ;
- deux prompts non suivis 13/32, SHA indiqués au §4 ;
- le présent prompt de passation, non suivi.

Ne pas déclarer l'arbre principal entièrement propre : ces documents locaux sont conservés volontairement.
Le worktree 23, lui, est propre. Les 91 empreintes publiées E4 ont été revérifiées après intégration,
et les chemins scellés E2/E3/PCA/E4 sont absents de la plage 23.

Journaux locaux : `logs/orchestration_20261107/execution-19-21-state.json`,
`logs/orchestration_20261113/continuation.md`, `logs/claude_sessions.json`. Leurs premières entrées anciennes
peuvent être obsolètes : privilégier les dernières réceptions et les preuves Git/processus.
Ce fichier de passation est local, non commité ; ses chemins absolus ne doivent pas être ajoutés à la
plage scientifique publiée par inadvertance. La modification utilisateur du protocole reste distincte du lot 23.

Reprendre 32 en premier, selon le protocole révisé et ses GO séparés. Pour les autres streams,
présenter les décisions réellement manquantes et leur portée avant toute implémentation/expérience non autorisée.
Un plan terminé, la fin E4 ou la clôture 23 ne lèvent aucune porte scientifique à eux seuls.
