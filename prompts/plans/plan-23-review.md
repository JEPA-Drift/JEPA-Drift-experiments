# Plan — revue du stream 23 : compatibilité de la phase 1 E6 avec main (2026-11-06)

## Contexte
- Demande : `logs/orchestration_20261106/request.md`, instruction du chercheur du 6 novembre relayée par Codex. Question posée : existe-t-il une phase 1 E6 compatible avec le main actuel et encore utile à intégrer, et à quelles conditions exactes ? Le plan ne présuppose ni fusion ni abandon.
- Objet : les deux commits propres à `stream-23` (`7e4c7a1` feat, `3d0bd20` correctif éditorial), base `2b0b1cd`, comparés à `20ad9e8` (HEAD de ce worktree, égal à main).
- Livrables, après un GO écrit distinct, en anglais : `docs/audits/stream_23_compatibility_2026_11_06.md` et `prompts/wrapups/wrapup-23-review.md` (les six rubriques du projet). Codex détient le plan canonique, le GO et Git.
- État à ce stade : seul ce fichier de plan natif a été écrit. Aucun fichier suivi n'a changé, aucune exécution n'a eu lieu (pas de Python, de test ni d'accès à `../JEPA-stream-23`).

## Méthode (lecture seule, avant comme après le GO)
- Commandes : `git show stream-23:<chemin>`, `git diff`, `git log`, `git rev-parse`, `git ls-files`, plus Read/grep dans ce worktree. Les objets Git sont lus sans toucher au disque des autres worktrees.
- Interdits : importer `jepadrift`, lancer pytest, `make check` ou E6, lire des rendements réels, copier des résultats dans ce worktree, lancer un sous-agent, utiliser Graphify ou jCodeMunch, muter Git, modifier la mémoire ou `DEVIATIONS.md`.

## Matrice de vérification
Les constats pré-GO ci-dessous ont déjà été observés en lecture seule pendant le mode plan.

| ID | Point | Source / méthode | Constat pré-GO | Contrôle post-GO | Statut |
|---|---|---|---|---|---|
| V1 | Commits propres | `git log HEAD..stream-23`, `rev-list --left-right --count`, `merge-base` | Deux commits seulement (7e4c7a1, 3d0bd20), base 2b0b1cd. Il manque 36 commits de main : 35 à `a0c576e` selon l'audit 01–27, plus `20ad9e8` (outillage) | Relancer et consigner | CONFIRMÉ |
| V2 | Empreintes scellées | `git show <ref>:<chemin> \| sha256sum` | CSV = `4101c867…d249` (stream-23 = 3d0bd20). La version 7e4c7a1 valait `1d16e6bd…` (avant correctif ; seul `ci_reason` change selon W23). Les 4 figures (`ca929eee`, `cdffaf9e`, `f14e06cb`, `1ed21dc6`) et `configs/e6.yaml` (`ca74d2e1`) sont égales à W23 et identiques entre les deux commits | Empreintes complètes dans l'audit | CONFIRMÉ |
| V3 | Schéma du CSV | En-tête via `git show` | 50 colonnes ; 191 lignes = 190 lignes de données + l'en-tête | pandas `dtype=str` sur stdin : 78 lignes D6 et 112 lignes D5 ; 72 lignes D6 de dérive avec `ci_reason` « prespecified reporting criterion » sans Künsch/Lahiri ; D6 sans IC de FPR | À CONTRÔLER |
| V4 | Entrées | Blobs `data/derived/d3_239/{ret_wide.npy,splits.yaml}` à 2b0b1cd, HEAD et stream-23 | Identiques (`a266fbab`, `3f3a65ba`, égaux à W23). Seul ajout depuis la base : un sidecar `z_55a1…`, que E6 ne lit pas | — | CONFIRMÉ |
| V5 | Imports et symboles | Inventaire de `pl.*`, `cusum.*`, `streams.*`, `sim.*`, `floors.*`, `inject`, `gamma.*`, `extract.DATASETS` (script et test) | Tous présents sur HEAD. Sont inchangés depuis 2b0b1cd : `monitors/`, `floors.py`, `sim.py`, `representations/pca.py`, `stats/covariance.py`, `data_loader/sp500.py`, Makefile, conftest, requirements et lock, `test_decoupling.py`. `ENERGY_DELTA` = 0,5, `TARGET_FPR` = 0,05, `CHUNK` et `summarize(rows, p, kind, n_cal)` n'ont pas changé | Comparaison AST des signatures (script historique lu sur stdin, fichiers HEAD), sans import | CONFIRMÉ statiquement |
| V6 | Appels de pipeline | diff de `pipelines.py`, `injection.py`, `representations/base.py` et `extract.py` | `run_pipeline(spec, data, splits, onset_info, state)` est inchangé. Dans `fit_pipeline`, le hook `pretrain` n'existe que sur IPCA, `_rows(None, …)` renvoie None et `missing` vaut False pour PCAOrthogonal. `_cal_p3d` garde la règle `required_threshold(…, "fpr", H)`. Dans `inject` F4, `fit` et `sr_asset` sont optionnels et absent des cellules de `e6.yaml` | Justifier chaque hunk comme « non exercé par E6 » | COMPATIBLE ; reproduction non testée (H-repro) |
| V7 | Déterminisme | Script, test, W23 | Graines `SeedSequence([23, …])` par rôle, cellule et H. `_map` en spawn ne dépend pas de `--jobs` (test dédié). Écriture par `pl.save_fair_csv`. W23 : deux exécutions complètes identiques, et quick identique avec jobs 1 et 48 | Relance hors mandat | Documenté ; non reproduit sur HEAD |
| V8 | Seuils et délais | Script, `C-pipe-delay`, `C-pca-predictive-rank`, section PCA | E6 : CUSUM strict, δ = 0,5, plus petit λ avec FPR(H) ≤ α sur les fenêtres ou panels nuls ; délai = offset + 1 ∈ [1, H] ; une exécution censurée compte H ; mesure RMST_H. PCA full : même δ et même `censored_time` = H, mais seuil `predictive_exchangeable_rank_v2` | Lire `C-pca-predictive-rank` et la définition du SE (deff = 1) | Délais compatibles ; seuils non comparables ligne à ligne |
| V9 | Doublons avec le PCA full | `configs/pca_drift_benchmark.yaml` ; `pca_drift_benchmark.py` l.1007–1010 et 1797 | Le PCA full appelle `injection.inject("F4-rotate")` avec `rotation_pair: [1, 2]` en base 1, soit **PC1–PC2 à 30°**. Fonds i.i.d. gaussien et t7, équicorrélés ρ = 0,4, N = 239, H = 250. Comparateur `e_t = (m_t² − mu_fit)/sd_fit` (analogue de P1-D) et CUSUM d'énergie sur préfixes spectraux. Il recouvre donc la cellule E6 exploratoire `rotate_pc1_pc2_30`, sur un autre fond. Il ne couvre pas : GARCH-t7 ; déformations r ∈ {1,25 ; 1,5 ; 2} de PC2–PC4 ; θ = 15° et 45° ; le témoin PC2–PC3 ; PC2–PC12 ; H = 500 ; P3-D full (D = 238) ; le contraste K = 1 / K = 10 ; D6. Piège : `[1, 2]` désigne PC2–PC3 dans E6 (base 0) mais PC1–PC2 dans le PCA full (base 1) | Confirmer que `sd_fit` = std(m²) et qu'il n'existe aucun autre scénario F4 | PARTIEL |
| V10 | Doublons de helpers | Script E6, `jepadrift/stats/intervals.py` | `e6.wilson` (formule fermée, z tiré de NormalDist) double `stats/intervals.wilson` (statsmodels, borné), ajouté par le stream 27 après la base. `delays`, `delay_summary`, `g_add` et `paired_bootstrap` restent locaux | Garder le code verbatim (identité d'octets) ; toute harmonisation exige un GO, une relance et le contrôle des hashes | NOTE |
| V11 | Intégration Git | `comm` des chemins modifiés par chaque côté | Un seul chemin commun : `docs/DEVIATIONS.md`, où les deux côtés ajoutent après `C-stats-drift` (déjà signalé par W23, vigilance 8). Aucun homonyme sur HEAD pour plan-23, GO-23, W23 ou les fichiers e6. `logs/` reste ignoré | — | Conflit textuel prévisible, résoluble par un ajout en fin de fichier |
| V12 | Coûts | W23 et la demande | Relance complète : 41 s sur 48 cœurs (quick : 30 s, 62 s avec `--jobs 1`). `test_e6.py` : 13 tests, 8 s. Le `make check` actuel (37 + 545 tests, 5 ignorés) dépasse déjà 5 min. L'intégration ajoute 12 fichiers, dont environ 0,69 Mo de figures | — | FAIBLE |
| V13 | FPR D6 descriptif | `C-E6-phase1` (a), W23 §3 | Résultat en échantillon : FPR atteint 0, niveau atteignable suivant 0,24–0,57. Les détections D6 tombent dans le bloc d'égalité de l'épisode de fin 2018 | Via V3 | CONFIRMÉ |
| V14 | Règle des dix blocs | 3d0bd20, `d6_ci_reason`, `C-E6-phase1` (a) | Critère de reporting préspécifié (Q5), qui n'est plus attribué à Künsch ni à Lahiri ; 2,77 et 0,88 blocs | Via V3 | CONFIRMÉ |
| V15 | Contraste PC1–PC2 | W23 §5 et vigilance 6, `C-E6-phase1` (d) | P1-D détecte sous son FPR (0,040, 0,024, 0,006) : les G_ADD de 14,6 à 105 sont des `lower_bound` dus à l'aveuglement unilatéral de l'indice. Avec K = 1, le résiduel est PC2, l'axe tourné : l'alignement vient de la construction. La représentation est une PCA, pas une représentation apprise | — | Aucune revendication de gain de représentation apprise |
| V16 | D8 et P4-D | HEAD : `C-e3-d8-fail`, `C-P4D-null-insample` | D8 reste FAIL. P4-D est enregistré par le stream 17, mais son contrôle nul est en échantillon et il n'est pas calibré pour J4 | — | P4-D exclu |
| V17 | Phase 2 | Audit 01–27, l.47 et l.53 | Le stream 16 est absent : P5-D et la contribution J4 sont bloqués | — | Hors périmètre |

## Recommandation provisoire
- Verdict technique : **compatible sous conditions** (vérification statique ; reproduction numérique non démontrée).
- Utilité : **complémentaire, non critique**.
- Décision recommandée : **préserver et différer**. La branche et le worktree historique restent intacts. Une **intégration ultérieure conditionnelle passerait par un nouveau GO ciblé**, déclenché par un besoin écrit : citation de résultats F4 linéaires dans l'Article C ou J4, ou planification de la phase 2 après le stream 16.
- Arguments pour l'intégration :
  - aucune rupture d'API ;
  - entrées identiques et coût faible ;
  - E6 est le seul témoin de GARCH-t7, des déformations, de H = 500 et des contrastes de K ;
  - livrable scellé et traçable.
- Arguments contre une intégration maintenant :
  - la reproduction n'est pas démontrée sans relance, interdite ici ;
  - le conflit sur `DEVIATIONS.md` doit être résolu, et ce fichier est interdit ici ;
  - D6 n'apporte pas d'information (bloc d'égalité) ;
  - D5 dépend d'un seul panel d'ajustement (λ_D5 varie d'un facteur 3) ;
  - l'effet principal (PC1–PC2) est en partie un artefact et en partie un doublon du PCA full ;
  - le stream 31 est prioritaire, et J4 comme JEPA sont exclus.
- Contre l'abandon : le travail est déjà payé et sa conservation ne coûte rien ; la phase 2 en dépend.

## Conditions exactes d'une intégration future (contenu proposé du GO ciblé)
- C1 : travailler dans un worktree neuf issu de `origin/main` et y appliquer 7e4c7a1 puis 3d0bd20, jamais dans `../JEPA-stream-23`.
- C2 : `DEVIATIONS.md` reçoit `C-E6-phase1` (texte de 3d0bd20) en fin de fichier, avec une note d'intégration. Les entrées existantes de main ne changent pas.
- C3 : relancer `--phase 1` en version complète puis quick, sous `.venv` avec les variables d'environnement du projet. Le CSV doit valoir `4101c867…`, la sortie quick `874be212…`, et les 4 figures doivent égaler W23. Tout écart est une déviation D3 : STOP, sans correction forcée.
- C4 : `tests/test_e6.py` donne 13 tests passés, puis `make check` complet.
- C5 : aucun ajout de P4-D ni de P5-D, aucune contribution J4. Les étiquettes restent inchangées : D6 descriptif avec IC=NA ; D5 conditionnel au panel d'ajustement ; PC1–PC2 sans revendication de représentation apprise ; information gaussienne de conception, pas de KL exacte.
- C6 : `e6.wilson` reste verbatim, sauf GO avec C3. La différence de convention d'axes `[1, 2]` entre E6 et le PCA full est documentée.
- C7 : pour le push, Codex applique les règles du projet (plage poussée, chemins EUROFIDAI, limite de 50 Mo, anonymat).

## Étapes après le GO (Claude)
1. Rejouer V1–V17. Les contrôles Python se font uniquement sur le stdout de `git show` (pandas `dtype=str`, AST), avec `.venv/bin/python`, BLAS à 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42` et `MPLBACKEND=Agg`. Les sorties temporaires vont uniquement dans le scratchpad de session.
2. Écrire `docs/audits/stream_23_compatibility_2026_11_06.md`, avec les sections Scope and sources, Verification matrix, Compatibility verdict, Utility versus full PCA, Exact integration conditions et Recommendation.
3. Écrire `prompts/wrapups/wrapup-23-review.md` avec les rubriques Context, Validated Results (empreintes contrôlées), Errors and Dead Ends, Current State, Vigilance Points et Recommendations.
4. Contrôles qui doivent échouer en cas d'écart :
   - `git status --porcelain` donne exactement les deux lignes `??` des livrables ;
   - `git diff --quiet` réussit ;
   - `rg -n '[/]home/[^/[:space:]]+'` ne renvoie aucune occurrence dans les deux fichiers.
   Puis arrêt pour la revue Codex : pas de commit, pas de réindexation, pas de `make check`.

## Hypothèses (valeurs par défaut)
- H1 : « ligne 23 » désigne la ligne du stream 23 dans la matrice (ligne 53 du fichier). La ligne 23 littérale concerne le stream 03.
- H2 : « compatible » signifie que les symboles et signatures sont présents et que les chemins numériques exercés sont inchangés ou modifiés seulement par des options non passées. « Reproduit » exige C3.
- H3 : « utile » désigne un résultat absent du PCA full et requis par un livrable planifié ; aucun livrable ne l'exige aujourd'hui.
- H4 : le PCA full est jugé sur ses fichiers suivis de HEAD, sans lire le `trials.csv` du worktree full-2000.
- H5 : l'écart de 35 à 36 commits vient de `20ad9e8` (outillage), sans effet sur E6.

## Questions pour Codex
- Q1 : faut-il un verdict unique ? Par défaut, verdict composite : préserver et différer maintenant, avec C1–C7 pour un GO ciblé futur.
- Q2 : les contrôles post-GO peuvent-ils utiliser `.venv/bin/python` sur le stdout de `git show` (pandas, AST), sans importer `jepadrift` ? Par défaut : oui.
- Q3 : l'analyse de chevauchement des chemins suffit-elle pour `DEVIATIONS.md`, ou faut-il une simulation `git merge-tree` (forme à 3 arguments, sans écriture d'objet) ? Par défaut : l'analyse des chemins seule.
- Q4 : le wrapup peut-il être rédigé directement au format projet, sans la directive `wrap-up` ni `make check`, Codex se chargeant du commit ? Par défaut : oui.
- Q5 : faut-il un autre déclencheur de réouverture que ceux de la recommandation ?

L'approbation d'ExitPlanMode ne vaut pas GO : rien ne sera exécuté avant un GO écrit distinct.


## Décision GO intégrée — revue documentaire du 6 novembre

Date : 2026-11-06, 12:22 UTC. GO Codex dans le mandat de supervision délégué ; aucune signature personnelle du chercheur n'est attribuée. Base 20ad9e860a58373ec85405de6ee19a68322dd02e. Référence exécutoire : `prompts/GO-stream-23-review.md`. Référence d'audit : 23-review. Le plan historique de stream-23 et son worktree sont préservés.

**Réponses Q1–Q5.** Q1 : verdict composite, séparant compatibilité statique, reproduction non exécutée, utilité et recommandation. Q2 : oui aux contrôles Python sur les blobs Git de résultats et au parsing AST, exclusivement sous `.venv`, sans importer le code scientifique ni lire de rendements. Q3 : analyse des chemins suffisante ; un conflit prévisible n'est pas présenté comme un conflit de fusion effectivement reproduit. Q4 : non à l'omission de wrap-up ; invoquer la directive installée pour le checkpoint anglais avant toute clôture Git, sans `make check` par Claude. Q5 : ajouter comme déclencheur possible une demande écrite ciblant un diagnostic F4 linéaire absent du full. Ce déclencheur ne donne aucun GO d'expérience dans le présent mandat.

**Précisions scientifiques obligatoires.** V8 : le delta 0,5 du full concerne son comparateur CUSUM d'énergie ; il ne s'applique pas au scan mélange moyen ni au scan de covariance. V15 : la PCA est ajustée sur les données de calibration ; les résultats ne mesurent ni JEPA ni une supériorité d'un encodeur entraîné. Remplacer « D6 n'apporte pas d'information » par son rôle de diagnostic descriptif sans FPR indépendant. « Coût faible » décrit les temps historiques cités, pas une mesure récente. Aucune reproduction ni compatibilité dynamique n'est certifiée par l'AST.

**Procédure.** Les fichiers plan/GO de Codex sont étrangers à Claude ; contrôler séparément les deux livrables propres et leurs hashes, sans exiger deux seules lignes au statut global. Aucun correctif de code, de CSV ou de figure. Les conditions C1–C7 sont des recommandations futures non exécutoires.

- [ ] Recontrôler la matrice V1–V17 et les empreintes, avec les seules lectures autorisées.
- [ ] Écrire le rapport anglais en distinguant constat, hypothèse, preuve historique et vérification présente.
- [ ] Contrôler les deux chemins possédés et invoquer la directive wrap-up installée.
- [ ] S'arrêter pour revue Codex, sans intégration ni expérience.

**Vigilance de revue.** Conventions d'axes 0/1 ; in-sample contre indépendant ; compatibilité statique contre reproduction ; temps historiques contre temps actuels ; F4 linéaire contre résultats JEPA. Aucune de ces distinctions ne sera effacée pour faciliter une intégration.
