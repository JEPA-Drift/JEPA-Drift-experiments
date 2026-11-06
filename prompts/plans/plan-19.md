# Plan 19 — audit documentaire de replanification E4 / P3-KF (v1, mode plan natif)

**État canonique : GO du lot limité, enregistré avant exécution ; la décision intégrée en fin de fichier tranche les questions de la proposition native conservée ci-dessous.**


Base `69d562419be77b17af9e56711a6ae069caa6bfc4`, branche `stream-19`, arbre propre. Mandat :
`logs/orchestration_20261106/plan-request.md`. Statut : en attente du GO écrit de Codex (`prompts/GO-stream-19.md`) ;
l'approbation de l'écran natif ne vaut pas GO.

## 1. Contexte

Le prompt historique 19 (`prompts/streams/prompt-19-e4-p3kf.md`) demande une campagne E4 sur D6 réel (lois d'échelle
en N, P3-KF/SPLL). L'audit 01–27 (l. 49) la classe `À_REPLANIFIER`. Le lot présent est uniquement documentaire. Il
produit un audit anglais qui établit, depuis les sources existantes, ce que l'ancienne grille apporterait encore et
quelles portes précèdent un éventuel futur lot scientifique. L'ancien prompt n'est pas implémenté, et ce lot ne
clôture pas E4.

Constats établis en lecture, à consigner avec leurs sources :
- **Benchmark full PCA.** `N = 239`, `H = 250`, `T_fit = 1000` et `nmax = 20` sont fixes (manifeste
  `results/pca_drift_benchmark/full_2000_20261101/manifest.json`, l. 32–45). Seuls varient le réservoir `k`
  (P_k = axes 1..k) et la taille `d` (`docs/sections/pca_drift_benchmark.md`, l. 101–102). Il n'y a donc ni loi en N,
  ni pente extractible.
- **Pentes en N existantes.** Seul le bras B d'E1 (stream 12, `CLOS_VALIDÉ`) en fournit : D2 avec N ∈ {8, 16, 32, 64,
  97}, D3 avec N ∈ {8, …, 239} ; F3 avec P2-C ; F2 avec P3-C full, P3-CS (b) et le mélange là où la porte Holm passe ;
  a_max(N) rapporté (`prompt-12-e1.md`, l. 45–56 ; `results/e1/e1_j2_summary.txt` ; `wrapup-12.md`, l. 41–46). La
  lecture est rétrospective, à α nominal commun.
- **Théorie.** Le corollaire « Scaling » (`paper/sec3_theory.tex`, l. 82–84) donne un gain fluide en N^{a−b/2}, sous
  I(N) ≍ N^a, D(N) ≍ N^b et D ≫ ln γ. Ces exposants sont conditionnels. Ce ne sont ni des ADD calibrés, ni des pentes
  mesurées.
- **SPLL.** Aucun code n'existe. La référence « Kuncheva (2013) » est non vérifiée (`handover-01-27.md`, l. 918 et
  942 ; `wrapup-01-11.md`, l. 49). La bibliographie ne porte que `kuncheva_faithfull_2014` et `qahtan_2015`
  (`paper/articleC_biblio_addendum.bib`, l. 54–65), qui sont d'autres travaux.

## 2. Périmètre exact

Fichiers que cette session écrira après le GO, et seulement ceux-là :
1. `docs/audits/stream_19_replan_2026_11_06.md` (anglais).
2. `prompts/wrapups/wrapup-19.md` (anglais, six sections, via la directive wrap-up native).
3. `logs/stream_19/doc_checks.log`, ignoré par `.gitignore:9`, qui reçoit la sortie des contrôles du §7.

À Codex : `prompts/plans/plan-19.md`, `prompts/GO-stream-19.md`, `make check`, la réindexation AST seule et Git.

Restent inchangés :
- code, tests, configurations, résultats et figures ;
- `docs/DEVIATIONS.md`, `docs/sections/` ;
- prompts canoniques, master, `INDEX.md` ;
- matrice 01–27 et fichiers du stream 21 ;
- `jepadrift/floors.py` (lu seulement) et les mémoires.

Cette session ne crée aucune sauvegarde ni aucun index.

## 3. Sources (lecture seule ; SHA-256 relevés dans l'audit)

- `CLAUDE.md` (= `AGENTS.md`), `plan-request.md`, `prompt-19-e4-p3kf.md`.
- Audits : `docs/audits/streams_01_27_relevance_2026_11_06.md`, `docs/audits/stream_18_closeout_2026_11_06.md`.
- `docs/DEVIATIONS.md`, entrées : C-P3C-mixture-gate, C-e1-holm-gate, C-e1-f2-chars, C-e1-amplitude-grid,
  C-D3-beta-denominator, C-D3-chars-phantom, C-P4D-null-insample, C-pca-predictive-rank, C-repr-layout.
- Théorie : `paper/sec3_theory.tex`, `paper/articleC_biblio_addendum.bib`, `jepadrift/floors.py`
  (`mixture_multiplier`, `dictionary_multiplier`).
- E1 : `prompt-12-e1.md`, `wrapup-12.md`, `results/e1/e1_j2_summary.txt`.
- Benchmark PCA : `28_STREAM_PCA_DRIFT_RUNNER.md`, `docs/sections/pca_drift_benchmark.md`, manifeste full.
- `prompts/streams/INDEX.md` (l. 104 et 107), `wrapup-06.md` (l. 89).

Aucun `ret_wide.npy`, aucun rendement et aucun import Python.

## 4. Plan de l'audit (sections)

1. Scope and authority : GO, base, ce qui n'est pas fait.
2. Sources read et commands executed (lecture seule).
3. F1 — What the full PCA benchmark measures : N fixe, k et d variables, donc aucune pente. Il sert de cadre à N fixe
   (préfixes contre sous-ensembles sélectionnés par l'information), sans chiffre nouveau.
4. F2 — Six quantités tenues séparées, dans un tableau :
   - exposant conditionnel (corollaire « Scaling ») ;
   - information I(N) (corollaire « Factor » : terme factoriel borné, terme de largeur linéaire) ;
   - alignement a_max / cos² ;
   - coût du mélange M(D, γ) et du dictionnaire (A + ln K)/(A cos²) ;
   - budget fluide τ_γ (lemme 1) ;
   - ADD et FPR réellement calibrés (lectures E1).

   Pour chacune : définition, source, domaine de validité et existence d'une mesure. Aucune pente nouvelle.
5. F3 — Existing N-slope evidence : bras B d'E1 cité tel quel (Q2), avec ses étiquettes.
6. F4 — Dependencies and bounds : tableau obligatoire/optionnel (H3), sans corriger les producteurs.
7. F5 — Coverage and necessity : matrice de l'ancienne grille face au bras B d'E1 et au benchmark full (couvert, non
   couvert, bloqué) ; redondances à ne pas réexécuter et éléments résiduels (H2).
8. F6 — P3-KF / SPLL :
   - rôle d'antériorité (R3 des plans v3/v4) ;
   - tail10 : m = 46 / 123 (C-repr-layout) ;
   - coût k-means non mesuré (`wrapup-06.md`, l. 89) ;
   - risque de seuil recalibré in-sample, analogue à C-P4D-null-insample ;
   - référence non vérifiée.
9. F7 — Gates before any future scientific lot (G1–G8, §6).
10. Decision : 19 n'est ni clos ni abandonné (Q3). E5 (prompt 22) liste 19 parmi ses dépendances (`INDEX.md`,
    l. 107), ce qui est consigné sans arbitrage.
11. Not examined ; Test evidence (aucun test : lot documentaire) ; Hashes.

## 5. Hypothèses et défauts (à confirmer ou infirmer au GO)

- **H1.** Le benchmark full n'entre dans l'audit que comme preuve de non-couverture en N. Aucun chiffre agrégé nouveau.
- **H2. Couverture de l'ancienne grille.**
  - Redondante sur les triplets déjà exécutés par le bras B d'E1, à ne pas réexécuter :
    - (D2, F3, P2-C) ;
    - (D3 ≤ 239, F3, P2-C) ;
    - (D3 ≤ 239, F2, P3-C full / P3-CS (b) / mélange).
  - Non couverte ailleurs :
    - F1 ;
    - F3 hors P2-C ;
    - F2 hors P3-C full et P3-CS (b) ;
    - P3-C factoriel, P4-C, P3-KF ;
    - N = 500 et D4 ;
    - prévision par le dictionnaire corrigée par a_max(N) ;
    - audit par sous-ensemble.
- **H3. Dépendances d'un futur lot.**

  | Stream | Statut proposé |
  |---|---|
  | 05 injections (F1–F3, convention b, D6) | obligatoire |
  | 07 pipelines (P2-C, P3-C, P3-CS) | obligatoire |
  | 08b caractéristiques + `stats.drift` | obligatoire pour F2 ; optionnel pour l'audit par sous-ensemble |
  | 11 audit | contrainte de lecture (sélection, NaN de `predicted_gains.csv`) |
  | 17 IPCA | P4-C optionnel ; P4-D exclu (C-P4D-null-insample) |
  | 18 CD-DFM | absent : « non disponible », sans substitut |

  Bornes :
  - le mélange n'est lu que là où la porte Holm passe, en « validité approchée » ; le dictionnaire est le défaut
    (C-P3C-mixture-gate, C-e1-holm-gate) ;
  - toute cellule F2 ou P4-C hérite de C-D3-beta-denominator (via C-e1-f2-chars et C-IPCA-K) ;
  - `d3_500` et D4 héritent de C-D3-chars-phantom ; `d3_239` est indemne ;
  - la garantie prédictive ne vaut que pour des trajectoires synthétiques indépendantes (C-pca-predictive-rank).
- **H4.** P3-KF est un comparateur d'antériorité complémentaire. L'affirmation centrale (concentration et calibration
  exacte) ne l'exige pas. Il est différé avec ses portes, non abandonné.
- **H5.** L'audit ne contient ni pente, ni coût extrapolé, ni hyperparamètre, ni grille choisie.

## 6. Portes d'un futur lot scientifique (décrites, non tranchées)

- **G1 — Question.** Une question falsifiable non couverte, au choix du chercheur. Candidats :
  - saturation de F1 en N ;
  - extension à N = 500 et à D4 ;
  - antériorité de P3-KF ;
  - prévision par le dictionnaire contre pente mesurée.
- **G2 — Sources.**
  - lignes antérieures au 2020-01-01 uniquement ;
  - levée écrite de l'interdit sur les rendements réels si le lot utilise D6 ;
  - D4 reste local et n'est jamais suivi ;
  - fonds synthétiques D5 si l'objet est une loi en N à I(N) connue.
- **G3 — Calibration indépendante.** Requise pour P3-KF calibré sur des fenêtres D6, selon l'exigence de
  C-P4D-null-insample. Sont écrits avant tout résultat :
  - la source et l'unité d'indépendance ;
  - le partage calibration/évaluation ;
  - la taille et la cible ;
  - l'intervalle et la règle de verdict.
- **G4 — Gel.** Avant J4, la configuration est figée avant tout tirage : grilles, graines, sous-ensembles emboîtés, et
  règle d'amplitude du prompt 12 consignée comme degré de liberté. `FROZEN.json` ne s'impose que pour une lecture
  ≥ 2020, hors périmètre.
- **G5 — Coût.** Non mesuré pour E4. Le seul analogue mesuré est le bras B d'E1 (`wrapup-12.md`, l. 20). Le budget
  sera établi par un smoke autorisé.
- **G6 — Artefacts.** Les livrables du prompt 19 sont différés. Tout futur code suivra :
  - TDD avec témoins sur fixtures factices uniquement ;
  - compatibilité avec les 44 contrats scellés (`tests/test_pca_drift_contracts.py`, SHA-256 `2e488fe7…`) ;
  - `monitors/` en numpy seul ;
  - `save_fair_csv`, SeedSequence et résultats indépendants de `--jobs`.
- **G7 — Caractéristiques.** Avant tout F2 ou P4-C : correction en amont (stream séparé) ou héritage étiqueté.
- **G8 — SPLL.** Référence vérifiée sur source primaire avant toute écriture de `spll.py`.

## 7. Contrôles après écriture (assertions qui échouent ; pas de TDD de prose)

Commandes shell seulement, aucun Python ; sortie dans `logs/stream_19/doc_checks.log`.
- **C1.** `git status --porcelain` : cette session n'a écrit que l'audit et le wrapup. Les fichiers Codex sont
  comparés à leur SHA-256 relevé avant écriture.
- **C2.** `git diff --quiet 69d5624 -- jepadrift experiments tests configs results figures docs/DEVIATIONS.md
  docs/sections prompts/streams prompts/Prompts_Claude_Code_v5.md
  docs/audits/streams_01_27_relevance_2026_11_06.md`.
- **C3 (J1).** `results/e2/e2_cells.csv` : disque et index = `e315e537…`, 47 lignes CRLF, aucune LF nue.
- **C4.** Chaque chemin cité existe (`test -e`).
- **C5.** Chaque SHA-256 cité est recalculé (`sha256sum`).
- **C6.** Chaque nombre cité figure tel quel dans sa source (`grep -F`).
- **C7.** Aucun chemin personnel absolu dans les deux fichiers (`! grep -n '/home/'`).

`make check`, la réindexation et le commit reviennent à Codex à la clôture.

## 8. Différé explicitement (non autorisé)

Chacun des éléments suivants exige un plan et un GO séparés :
- `experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`, `results/e4/*`, `figures/e4/*` ;
- tout test de moniteur, toute pente, tout smoke ;
- D6 réel, D4, `d3_500` ;
- P4-D, CD-DFM ;
- correction des caractéristiques ;
- gel / J4 ;
- re-run d'E1 ou du benchmark.

## 9. Questions résiduelles (avec défauts)

- **Q1 — Référence SPLL.**
  - Défaut : aucune consultation externe ; l'audit garde « unverified ».
  - Option : notice éditeur primaire (IEEE Xplore / DOI) uniquement, URL et date consignées, sans clone, installation
    ni code.
  - Candidat de mémoire, non vérifié et non repris dans l'audit : Kuncheva, IEEE TKDE 2013, « Change detection in
    streaming multivariate data using likelihood detectors ».
- **Q2 — Pentes E1 existantes.**
  - Défaut : citées mot pour mot depuis `results/e1/e1_j2_summary.txt` (SHA-256 relevé), étiquetées « E1,
    retrospective, common nominal α », sans agrégation.
  - Option : renvoi par chemin seul.
- **Q3 — Issue.**
  - Défaut : `À_REPLANIFIER` maintenu jusqu'au choix de G1 ; les questions candidates sont listées sans classement.
  - Option : `DIFFÉRER` avec portes, ou question prioritaire désignée par le chercheur.
- **Q4 — Contrôles.**
  - Défaut : C1–C7 par cette session, `make check` par Codex.
  - Option : `make check` aussi dans cette session.

## 10. Séquence après GO

1. Relire le GO.
2. Relever les SHA-256 des fichiers Codex.
3. Écrire l'audit.
4. Exécuter C1–C7.
5. Lancer le wrap-up natif et écrire `wrapup-19.md`.
6. Relancer C1 et C7.
7. Arrêter pour la revue Codex (ni Git, ni réindexation).

Au quota ou à l'erreur : état conservé et rapport, sans relance ni remplacement d'instance.

## 11. Décision GO intégrée — Codex, 2026-11-06, 17:49 UTC

**GO du seul lot documentaire**, selon `prompts/GO-stream-19.md`. Le plan natif est archivé sans changement sous `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `d2cb81d9f55a1e87e1cf5765bf4aa740ce99e9b1a0cfaccabe715f9dad64db7e`. Cette section tranche les questions et prime sur les formulations de la proposition native.

- **Q1 :** pas de consultation externe ; conserver la référence SPLL comme non vérifiée, sans titre supposé ni attribution bibliographique nouvelle. Aucune écriture de moniteur.
- **Q2 :** les pentes déjà publiées dans E1 peuvent être citées avec leur SHA, leur lecture rétrospective, le nominal commun et leurs qualifications de source. Ce sont des résultats archivés, pas une reproduction ni une preuve de comparabilité atteinte des FPR.
- **Q3 :** maintenir `À_REPLANIFIER` pour la campagne E4. Le lot documentaire peut être terminé ; la campagne et les composants historiques non exécutés ne sont ni clos ni abandonnés.
- **Q4 :** contrôles documentaires C1–C7 par Claude ; suite complète, réindexation et Git par Codex.
- **H2 :** remplacer « redondante » par « recouvrement historique partiel » tant que l'identité des fenêtres, amplitudes, horizons, unités d'échantillonnage, lectures, canaux et règles de calibration n'est pas établie. Un triplet jeu/famille/pipeline commun ne suffit pas à établir une duplication exacte. Aucun rerun n'est autorisé.
- **H3 :** distinguer les exigences du prompt historique des options d'un futur plan. Le caractère optionnel proposé de P4-C ou d'un audit ne modifie pas les critères historiques. « d3_239 indemne » vise seulement les cellules fantômes absentes dans le périmètre audité : C-D3-beta-denominator l'affecte aussi. Ne pas généraliser l'absence de cellules fantômes à toute fenêtre future.
- **H4 :** le caractère non indispensable de P3-KF reste une proposition de replanification à arbitrer, et non une décision attribuée au chercheur ou une dispense générale de comparateur.
- **H5 / G4 :** aucune pente nouvelle, extrapolation de coût, grille ou hyperparamètre nouveau. Les pentes E1 archivées de Q2 restent permises. Présenter le garde-fou 2020+ comme une exigence minimale de la mémoire actuelle, sans affirmer que le gel ne peut servir à aucun autre protocole futur.
- **C4 / C6 :** contrôler les chemins effectivement présents et distinguer les futurs livrables absents. Vérifier les nombres archivés par leur source ; les expressions théoriques se relient à leurs équations, sans imposer un grep littéral artificiel. Les bornes de validité et les lectures restent explicites.
- Aucun chiffre expérimental nouveau, aucun rendement réel, aucun code/test/configuration modifié. Les fichiers autorisés sont l'audit anglais, le wrapup anglais et les journaux ignorés. Claude invoque son wrap-up et enregistre les six sections avant de remettre la main à Codex.
