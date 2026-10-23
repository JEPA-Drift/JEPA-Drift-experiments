# Plan — Stream 27 : E10, étape `linear`, famille F1 (P1-C, P3-C) — révision 4

Statut : GO donné le 2026-10-22 pour la révision 4 ; décision intégrée ci-dessous ; sections harmonisées.
**Prêt à coder.**

## Décision GO intégrée (2026-10-22)

- **Périmètre et décisions.** GO de l'orchestrateur pour la révision 4, strictement F1 et P1-C/P3-C.
  - B1 = F1 seul ; B2 = aucune revendication iso-FPR ; B3 = générateur local, sans modifier `sim.py`.
  - H1 à H5 approuvées.
- **Précisions d'implémentation.**
  - `fpr_iid` devient `fpr_iid_mc`, une estimation Monte Carlo. Son test a une tolérance fixée : sur n chemins de
    pièces, l'estimation pour `half` en lecture exacte doit tomber dans la région binomiale à 99 % de 0,043947
    (z = 2,5758).
  - Les IC de Wilson calculés sur les fenêtres brutes symétrisées (P3-C et P1-C) portent
    `ci_kind=wilson_conditional_approx` : ils sont conditionnels à l'état et aux magnitudes, et approximatifs.
- **Libellés de mise en œuvre**, sans changement de conception :
  - la référence de `half` sur le brut (même état, fenêtre symétrisée) est notée
    `reference_kind=symmetrized_window` ;
  - les lignes `zero_neg` ont un nul de flux invalide (`null_valid=invalid`). Elles portent `reference_kind=none`
    en D5 zéros et en D6, et `reference_kind=descriptive_contrast` sur le brut ;
  - les lignes `ref_coins` portent `design=iid_scenario` ;
  - `ci_kind` ∈ {wilson, wilson_conditional_approx, hac_bartlett, paired_bootstrap, na} qualifie chaque IC.
- **Suite.**
  - Transcrire le GO dans `prompts/GO-stream-27.md` et enregistrer ce plan dans `prompts/plans/plan-27.md`.
  - Implémenter en TDD et vérifier sous `.venv`.
  - Un seul commit local, puis arrêt avant fetch, push ou fusion.

## 0. Base, décisions de revue, environnement

- **Base.** `stream-27` est sur le `main` local `2b0b1cd`, qui contient le prompt et l'amorçage 27 resserrés.
  Le stream 8b est fusionné (`33d847d`). L'arbre est propre.
- **Décisions de revue intégrées.**
  - **B1 = F1 seul.** F2 sur D3 fera l'objet d'une révision ultérieure. P5-C attend le point de contrôle gelé du
    stream 16. `--families F2` et `--stage jepa` sont refusés avec un message qui nomme la porte.
  - **B2 = aucune revendication « à fausse alarme égale ».**
  - **B3 = générateur GJR et choc local au script E10**, pour éviter le conflit avec le stream 13 sur `sim.py`.
    `sim.garch_panel` reste utilisé pour la base, t_ν et les zéros. `jepadrift/sim.py` n'est pas modifié.
- **Langues.** Les nouvelles entrées de `docs/DEVIATIONS.md` et toute la trace d'audit sont en anglais : journal,
  wrapup, cadre de l'enregistrement du GO. Les messages de l'orchestrateur sont transcrits tels quels. Le plan est
  en français.
- **Environnement.** `.venv` seulement : `.venv/bin/python` et `.venv/bin/pytest`.
  - `make check` et `git commit` (hook) se lancent avec
    `MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin` en tête de PATH.
  - Variables exportées : OMP/MKL/OPENBLAS = 1, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`.
- **Lignes réelles.** Seulement 2005-01-04 → 2019-12-31 (`pipelines.split_rows(...)["pre_monitor"]`), avec une
  garde bloquante. Ni torch ni EUROFIDAI.
- **Git.**
  - Un seul commit, après tous les changements.
  - Arrêt avant tout fetch, push ou fusion.
  - Publication ultérieure, sur instruction seulement : `git push origin stream-27`.

## 1. Faits établis (sondes en lecture seule, 2026-10-22)

| objet | valeur |
|---|---|
| treillis, H = 750, δ = 0,1, bilatéral strict, α = 0,05 | L = 45 ; seuil 9,1 ; niveau 0,043947 |
| FPR exact prédit pour des bits i.i.d. Bernoulli(q) | q = 0,51 → 0,051 ; 0,525 → 0,091 ; 0,54 → 0,178 ; 0,549 → 0,259 ; 0,446 → 0,314 |
| D2 | 3 774 lignes ; pretrain [0, 2 768) ; calib [2 833, 3 774) ; 2 864 zéros ; P3-C D = 6 ; état `85147fd9…` = sidecar |
| D3 (`d3_239`) | 3 775 lignes ; 7 556 zéros ; D = 11 ; état `6c44d64a…` = sidecar |
| q̂ brut, calib → pretrain | D2 : PC1 0,576 → 0,540. D3 : PC4 0,453 → 0,519. Titres (médiane) : 0,535 → 0,510 |
| D5 `garch_panel` (N = 97, ρ = 0,40, t₇) | `K="mp"` donne 0, d'où K = 5 entier |
| F1, γ_H = 15 000 | D5, P3-C : médianes 467 / 119 / 56 j à SR 4 / 8 / 16. D5, P1-C titre médian : détection 7 / 37 / 60 % |
| choc commun asymétrique, p = 0,05 | w = 0,25 : q du facteur 0,525 ; w = 0,50 : 0,561 |

## 2. Fonds, classés par validité du nul avant toute interprétation

**D5.** Chaque réplication est un chemin indépendant de 941 lignes de calib suivies de 750 lignes surveillées. On
fait varier un seul facteur à la fois autour de la base t₇, GARCH(0,08 ; 0,90), ρ = 0,40, N = 97.

| fond | générateur | nul des flux à pièces |
|---|---|---|
| base, t_ν, ν ∈ {3, 4, 5, 7} | `sim.garch_panel` | valide |
| zéros, p₀ ∈ {2 % ; 5 %} | `sim.garch_panel` puis arrondi au tick pilote, après l'injection | valide pour les bras à pièces (`half`, `qhat`) ; invalide pour `zero_neg` |
| GJR, γ ∈ {0,05 ; 0,10} | local : α = 0,08 − γ/2, β = 0,90, indicatrice x̄_{t−1} < 0 | valide : levier prévisible, innovations symétriques |
| choc commun, w ∈ {0,25 ; 0,50}, p = 0,05 | local : saut négatif compensé dans le facteur | invalide (q ≠ ½) |

Le générateur local `_d5_panel` reprend la boucle de `garch_panel` en y ajoutant les termes GJR et choc. Avec
`gjr=0` et `shock=None`, il reproduit `sim.garch_panel` bit à bit ; un test le vérifie.

**D6** (D2, D3). Valide, exact conditionnellement à \|X\|. Chaque réplication utilise une symétrisation
d'ajustement et une symétrisation surveillée indépendantes (`injection.symmetrize` : un signe de Rademacher par
jour, commun à tous les actifs) ; τ* est uniforme.

**Brut** (D2, D3). Fenêtres de 750 jours du pretrain, ajustées sur la calib postérieure 2016–2019. Le nul est
inconnu, le dispositif rétrospectif, et la lecture descriptive.

**Pièces de référence** (`ref_coins`). Bits i.i.d. équitables, sans fond : c'est un scénario iid
(`design=iid_scenario`).

Chaque ligne du CSV porte deux libellés :
- `null_valid` ∈ {valid, invalid, unknown}, évalué au niveau du flux. Sur tout fond à zéros (D5 zéros, D6, brut),
  le flux du bras `zero_neg` a un nul invalide.
- `design` ∈ {prospective, symmetrized, retrospective, iid_scenario}.

## 3. Bits partagés, bras et lectures

**Bits.** Pour chaque unité et chaque ligne, de calib comme surveillée, on calcule B = 1{y > 0}.
- Chaque ex aequo est remplacé par une pièce équitable tirée d'un PRNG local indépendant.
- Le même B réalisé alimente les bras `half` (c = ½) et `qhat` (c = q̂_u).
- q̂_u est la moyenne de B sur la calib, avec la même convention de pièces. Il est gelé et appartient à [0, 1].
- Le bras `zero_neg` (règle de l'Article B : B⁰ = 1{y > 0}, zéros comptés 0, centrages ½ et q̂⁰) est distinct. Il
  ne concerne que P1-C, sur les fonds à zéros.
  - Sur ces fonds, son flux de signe a un nul invalide : sous symétrie, P(B⁰ = 1) = (1 − p₀)/2 ≠ ½.
  - Ses lignes portent `null_valid=invalid` et `reference_kind=none`, sans garantie de FPR.

**Lectures**, sur le flux s = B − c :
- **exacte** : `bilateral_delay_vec(s, 0.1, 9.1)`. Le seuil est `select_threshold(0.05, H=750)["threshold"]`.
- **anytime-valid** : x = (B − c)/max(c, 1 − c) ∈ [−1, 1], puis `log_edetector` (P1-C) ou
  `log_dictionary_edetector` (P3-C), et `first_alarm(·, pipelines.horizon_gamma(750))`. On n'envoie jamais
  2(B − q̂) à `eprocess._bounded`.

**P1-C.** Noyau de `monitors`, sans entrée de registre. On suit 20 titres : les colonnes 0–19 en D5 ; en D6 et sur
le brut, 20 titres tirés une fois avec `SeedSequence([27, crc32(jeu), 1])`.

**P3-C.** `fit_pipeline` en mode factor : `K="mp"` en D6 et sur le brut, K = 5 en D5.
- Le bras `half` passe par `run_pipeline` sur une entrée Z ; ses pièces `[*seed, 7]` définissent B.
- Le bras `qhat` est calculé sur ce même B. L'identité des bits est testée.

**F1.** `inject`, avec K = nombre de canaux de P3-C, SR ∈ {4, 8, 16} et la convention (a). Les cellules F1
n'utilisent que la lecture anytime-valid.

## 4. Garanties et limites du recentrage

| nul du flux | bras | lecture | garantie |
|---|---|---|---|
| valide | `half` | exacte | FPR(750) = 0,043947 exactement, flux isolé par flux isolé (Lemme 2) |
| valide | `half` | anytime-valid | FPR(750) ≤ α |
| valide | `qhat` | toutes | aucune ; le recentrage estimé est descriptif |
| invalide | tous | toutes | aucune. Pour `half` en lecture exacte, `fpr_pred_iid` = `lattice.exceedance(750, 45, 2, 3, q)` au q moyen sert de référence à bits i.i.d. On rapporte l'écart sans critère de conformité : la dépendance et la variation de q d'une réplication à l'autre ne sont pas modélisées |
| invalide (fond à zéros) | `zero_neg` | toutes | aucune garantie de FPR. Pour le centrage ½ en lecture exacte, `fpr_pred_iid` au q moyen, sans critère |
| inconnu (brut) | tous | toutes | descriptive et rétrospective, sans attribution causale |

Limites du recentrage q̂ pour P3-C, rapportées via les colonnes `q_hat` et `q_mean` :
1. Il ne corrige que le taux marginal de chaque canal. Il ne touche ni à la dépendance sérielle ni à la loi jointe
   des canaux.
2. Il n'existe aucune preuve d'une moyenne conditionnelle nulle compte tenu de l'erreur d'estimation de q̂.
3. Il suppose q_u stable entre la calib et la surveillance. Le brut contredit cette hypothèse : q̂ de PC1 (D2) varie
   de 0,036 et q̂ de PC4 (D3) de 0,066 entre la calib et le pretrain.
4. Sur le brut, q̂ mêle asymétrie et dérive de localisation.
5. Le flux recentré n'est plus un flux à deux points ±½. Il n'a pas de niveau de treillis exact, et la borne
   max(q̂, 1 − q̂) réduit la puissance.
6. Un seul canal biaisé suffit à invalider le dictionnaire.

## 5. Références, IC, comparaisons

**Références de niveau.**
- `level_exact` : le niveau du treillis. Il ne s'applique qu'au bras `half`, en lecture exacte, sur un flux isolé.
- `fpr_iid_mc` : estimation Monte Carlo sur des pièces équitables indépendantes (fond `ref_coins`,
  `design=iid_scenario`, 20 000 chemins).
  - Elle estime la loi exacte seulement pour le bras `half` d'un flux isolé sous un nul valide. Tolérance : pour
    `half` en lecture exacte, l'estimation doit tomber dans la région binomiale à 99 % de 0,043947
    (p ± 2,5758·√(p(1 − p)/n)). Le test et le journal l'appliquent.
  - Pour `qhat` (q̂ tiré sur 941 bits) et pour le dictionnaire P3-C : scénario iid de référence seulement.
  - Aucune valeur pour `zero_neg`.
- **Niveau H₀ atteint** (`reference_kind`). Toute symétrisation applique un seul signe de Rademacher par jour,
  commun à tous les actifs (`injection.symmetrize`), ce qui préserve la dépendance transversale.
  - **Générateurs D5 valides** (base, t_ν, GJR, zéros) : `self_valid`. La simulation directe du générateur donne
    elle-même le niveau atteint. On la compare à α et, pour le bras `half` en lecture exacte, à `level_exact`.
    Aucune re-symétrisation : sur GJR, re-symétriser le chemin en gardant les magnitudes ne reproduit pas le
    générateur à levier, puisque le signe passé y pilote la volatilité future. Ce serait au mieux un benchmark
    diagnostique ; il n'est pas calculé.
  - **Choc commun** (invalide) : `matched_valid_generator`. C'est le même générateur, avec un signe de Rademacher
    par jour appliqué dans la boucle, en calib comme en surveillance ; état et q̂ sont réajustés. Sa récurrence ne
    lit que les magnitudes passées : ce générateur valide équivaut donc, réplication par réplication, au chemin
    re-symétrisé, ce qui apparie le contraste (un test déterministe le vérifie). On en tire `fpr_ref` et
    `inflation`.
  - **Brut, bras `half`** : `symmetrized_window`. Même état de représentation ; seule la fenêtre surveillée est
    symétrisée, avec des signes neufs par fenêtre. C'est un nul valide pour `half`, et la seule référence valide
    sur le brut. La comparaison au brut reste descriptive (dispositif rétrospectif). Son IC de Wilson porte
    `ci_kind=wilson_conditional_approx`.
  - **Brut, autres bras** (`qhat`, `zero_neg`) : pas de `fpr_ref` ni d'inflation. Avec le q̂ de la calib brute
    (q̂ ≠ ½), la fenêtre symétrisée n'est pas un nul valide du bras. Ces lignes forment un contraste descriptif
    distinct (`reference_kind=descriptive_contrast`). Un nul calibré symétrisé distinct (même état, q̂ réestimé sur
    une calib symétrisée) n'est pas retenu ; il peut être ajouté au GO.
  - **D6** : `self_valid`, sans `fpr_ref`. D6 est lui-même un nul valide : le FPR mesuré y est le niveau atteint,
    y compris par le dictionnaire.
  - **`zero_neg`, sur D5 zéros et D6** : `none`. Le flux a un nul invalide ; il n'y a ni référence valide ni
    garantie de FPR.

**IC.**
- Par unité : IC de Wilson à 95 %. Les simulations directes D5 donnent des réplications indépendantes ; en D6, les
  réplications sont i.i.d. conditionnellement au panel. `fpr − level_exact` : IC de Wilson décalé.
- Inflation du choc, `fpr − fpr_ref` : IC par bootstrap apparié sur les réplications, qui partagent leurs
  magnitudes avec le générateur symétrique.
- **Brut**, fenêtres chevauchantes :
  - deff = `monitors.gamma.gamma_spectral(série, L=H−1)`, appliqué aux indicatrices et, pour le bras `half`
    seulement, aux différences brut − symétrisé ;
  - IC calculé seulement si deff est fini et si 1 ≤ n_eff ≤ n ;
  - si la série est constante ou l'estimateur pathologique : `IC=NA` ; aucun recours à ⌊lignes/H⌋ ;
  - pour les fenêtres symétrisées des flux de signe, les signes sont neufs par fenêtre : IC de Wilson, conditionnel à
    l'état et aux magnitudes, et approximatif (`ci_kind=wilson_conditional_approx`).

**Gains (`e10_gains.csv`).**
- **Titres comparés à P3-C.**
  - Titre médian : rang 10 sur 20 par RMST sous F1 ; ex aequo départagés par l'indice. Il est choisi sur F1 sans
    viser le meilleur.
  - Titre oracle : meilleur RMST sous F1 ; `oracle=True`, exploratoire.
- **Rapports.**
  - `rmst_ratio` = RMST_titre/RMST_P3 : estimand de délais restreints à H.
  - `bounds_add_ratio` vaut vrai seulement si P3-C n'est jamais censuré.
  - Rapport des médianes si les deux taux de détection dépassent 50 %.
  - IC par bootstrap apparié, l'identité du titre étant fixée ; IC conditionnel à la sélection.
- **À côté de chaque gain :**
  - le FPR H₀ du même titre, sur le même fond, avec son IC de Wilson et son statut (`asset_selection` ∈
    {median, oracle}) ;
  - le FPR H₀ du dictionnaire P3-C, avec son IC ;
  - leur différence appariée et son IC ;
  - jamais la moyenne des 20 titres.
- Aucune revendication « à fausse alarme égale » (B2).

## 6. Sorties

- `results/e10/e10_cells.csv` et `results/e10/e10_gains.csv`, par `save_fair_csv` (tous les CSV).
  - Valeurs autorisées dans `e10_cells.csv` :
    - `reference_kind` ∈ {level_exact, self_valid, matched_valid_generator, symmetrized_window,
      descriptive_contrast, none} ;
    - `design` ∈ {prospective, symmetrized, retrospective, iid_scenario} ;
    - `null_valid` ∈ {valid, invalid, unknown} ;
    - `ci_kind` ∈ {wilson, wilson_conditional_approx, hac_bartlett, paired_bootstrap, na}.
  - Colonnes de référence de `e10_cells.csv` :
    - `fpr_iid_mc`, l'estimation Monte Carlo de la section 5 ;
    - `fpr_ref` et `inflation`, renseignés seulement si la référence est valide, sinon NA ;
    - `contrast_fpr`, pour les lignes `descriptive_contrast` ;
    - `fpr_pred_iid` et `pred_gap` = FPR − `fpr_pred_iid` : écart descriptif, sans critère.
- `figures/e10/fpr_inflation.{png,pdf}` et `figures/e10/gains.{png,pdf}`, tracées depuis les CSV.
- `logs/e10/run.log`, en anglais : commandes ; SHA-256 de la configuration, des entrées et des CSV ; états des
  représentations comparés aux sidecars ; durées.

## 7. Graines (PRNG locaux)

Clé générale : `SeedSequence([27, crc32(cell_id), r, j])`.

| j | usage |
|---|---|
| 0 | fond |
| 1 | symétrisation d'ajustement (D6) |
| 2 | onset et direction de F1 |
| 3 | pièces de P1-C sur les lignes surveillées |
| 4 | pièces de P1-C sur la calib |
| 5 | pièces de P3-C sur la calib |
| 6 | signes journaliers, communs à tous les actifs : générateur symétrique du choc, fenêtres brutes symétrisées |

- Pièces de P3-C sur les lignes surveillées : `[27, crc32(cell_id), r, 7]`, la convention de `run_pipeline`.
- Pilote du tick : `[27, crc32(cell_id), 10**6]`. Bootstrap : `[27, crc32(cell_id), 10**6 + 1]`.
- Brut : les pièces sont tirées une fois par unité sur toute la série.
- Aucun état global. Le résultat ne dépend pas de `--jobs` (pool `spawn`, une tâche par cellule).

## 8. Tailles

- Run complet :
  - 2 000 réplications par cellule H₀ (D5 et D6), plus le générateur symétrique apparié des deux cellules à choc ;
  - 500 réplications par (fond, SR) sous F1 ;
  - toutes les fenêtres brutes (2 019 et 2 020) et 20 000 chemins de pièces ;
  - au total ≈ 2 h CPU, mesurées et journalisées.
- `--quick` : 200 réplications H₀, 100 sous F1, SR ∈ {8, 16}, 2 000 chemins de pièces. Cible : moins de 3 min.
- La grille est portée par `configs/e10.yaml`, dont le SHA-256 est journalisé.

## 9. Fichiers

- **Nouveaux** : `experiments/e10_robustness.py`, `configs/e10.yaml`, `tests/test_e10.py`,
  `results/e10/{e10_cells,e10_gains}.csv`, `figures/e10/*`, `logs/e10/run.log`, `prompts/plans/plan-27.md`,
  `prompts/GO-stream-27.md`, `prompts/wrapups/wrapup-27.md`.
- **Modifié** : `docs/DEVIATIONS.md`, avec les entrées anglaises `C-e10-backgrounds`, `C-e10-streams`,
  `C-e10-readings`.
- **Inchangés** : `jepadrift/` (dont `sim.py`, `pipelines.py`, `monitors/`, `injection.py`), `CLAUDE.md`,
  `docs/sections/`.
- **Hors commit** : `results/e10_quick/`, supprimé après contrôle.

## 10. Contrôles demandés avant GO

| point | traitement | test |
|---|---|---|
| ex aequo appariés entre bras | `half` et `qhat` partagent B ; q̂ suit la même convention ; `zero_neg` est distinct | égalité bit à bit de B entre bras et avec `run_pipeline` |
| censure RMST | estimand restreint ; `bounds_add_ratio` seulement sans censure de P3-C | cas synthétique censuré |
| comparaison des FPR | FPR du même titre et du dictionnaire, différence appariée ; aucune revendication iso-FPR | — |
| référence iid | `fpr_iid_mc` : estimation Monte Carlo, qui n'estime la loi exacte que pour `half` sur un flux isolé ; niveau H₀ tiré des simulations directes des générateurs valides | `fpr_iid_mc` de `half` exact dans la région binomiale à 99 % de 0,043947 |
| `zero_neg` | nul de flux invalide sur les fonds à zéros ; aucune garantie de FPR | `null_valid=invalid` ; `reference_kind=none` en D5 zéros et D6, `descriptive_contrast` sur le brut |
| nul apparié | choc : générateur symétrique simulé directement, signe journalier commun à tous les actifs ; GJR : aucune re-symétrisation | signe dans la boucle = re-symétrisation post hoc, bit à bit, pour le choc |
| placebo rétrospectif | `design=retrospective` ; `half` : `reference_kind=symmetrized_window` ; `qhat` et `zero_neg` : contraste descriptif sans `fpr_ref` ; IC ou NA | série constante → NA ; 1 ≤ n_eff ≤ n ; `fpr_ref` et `inflation` à NA hors `half` sur le brut |
| prédiction iid sous choc | `fpr_pred_iid` est une référence à bits i.i.d. ; écart rapporté sans critère | test unitaire de la formule sur des bits i.i.d. simulés, pas sur le fond GARCH |
| titre oracle | `oracle=True`, exploratoire ; FPR H₀ du même titre | — |
| générateur local | `_d5_panel(gjr=0, shock=None)` = `sim.garch_panel` | SHA-256 identiques |

## 11. Étapes après GO

1. Écrire `prompts/GO-stream-27.md` : cadre en anglais, messages de revue et GO transcrits tels quels. Enregistrer
   `prompts/plans/plan-27.md` avec « Décision GO intégrée ».
2. TDD dans le script : générateur local, bits partagés, bras, lectures, bornes [−1, 1], références et nuls
   appariés, règle IC/NA, gains par titre, refus de F2, de `jepa` et des dates ≥ 2020, invariance par `--jobs`.
3. Deux runs `--quick` (SHA-256 identiques), puis le run complet, les figures et le journal.
4. Clôture :
   - entrées anglaises de `docs/DEVIATIONS.md`, wrapup-27 en anglais ;
   - `tools/reindex_graphify_jcodemunch.sh`, `make check` complet ;
   - un seul commit `feat(e10): measure sign-stream FPR robustness outside central symmetry (stream 27, F1)` ;
   - `git status --porcelain` vide ; arrêt pour l'audit.

## 12. Vérification

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42
MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin
SCRATCH="$(mktemp -d)"
.venv/bin/pytest -q tests/test_e10.py
.venv/bin/python experiments/e10_robustness.py --stage linear --families F1 --quick --out results/e10_quick
.venv/bin/python experiments/e10_robustness.py --stage linear --families F1 --quick --out "$SCRATCH/e10_q2"
diff <(cd results/e10_quick && sha256sum *.csv) <(cd "$SCRATCH/e10_q2" && sha256sum *.csv)
.venv/bin/python experiments/e10_robustness.py --stage linear --families F1 --out results/e10
PATH="$MAKEBIN:$PATH" make check && git status --porcelain
```

Résultats attendus :
- sur les fonds valides, le bras `half` en lecture exacte tombe dans la région à 99 % de 0,043947 (Lemme 2) ;
- sur le fond à choc, l'écart à `fpr_pred_iid` est rapporté, sans critère de conformité ;
- F2, `jepa` et les dates ≥ 2020 sont refusés.

Tests (`tests/test_e10.py`, moins de 60 s) :
1. Générateur : `_d5_panel(gjr=0, shock=None)` égale `sim.garch_panel` au SHA-256 près ; variance unitaire sous
   GJR ; moyenne nulle sous le choc.
2. Bits partagés : `half` et `qhat` partagent B bit à bit, et B égale les bits de `run_pipeline`. À q̂ = ½, `qhat`
   égale `half`. Les entrées des e-détecteurs restent dans [−1, 1].
3. Exactitude : `half` en lecture exacte sur un fond D5 valide tombe dans la région à 99 % de 0,043947.
4. Références iid :
   - `fpr_pred_iid` : sur des bits i.i.d. Bernoulli(q) simulés, le FPR mesuré concorde avec `lattice.exceedance`.
     Ce test porte sur la formule, pas sur le fond GARCH ;
   - `fpr_iid_mc` : pour `half` en lecture exacte, l'estimation Monte Carlo sur n chemins de pièces tombe dans la
     région binomiale à 99 % de 0,043947.
5. Références :
   - générateurs D5 valides : `reference_kind=self_valid`, sans `fpr_ref` ;
   - choc : le générateur avec signe journalier dans la boucle égale, bit à bit, le chemin re-symétrisé avec les
     mêmes signes ; état et q̂ sont réajustés ;
   - toute symétrisation partage un signe par jour entre tous les actifs ;
   - sur le brut, `fpr_ref` existe pour `half` seulement ;
   - les lignes `qhat` et `zero_neg` du brut ont `fpr_ref` et `inflation` à NA, et
     `reference_kind=descriptive_contrast` ;
   - les lignes `zero_neg` portent `null_valid=invalid` sur tout fond à zéros. Elles ont `reference_kind=none` en D5
     zéros et en D6, et `reference_kind=descriptive_contrast` sur le brut ;
   - chaque libellé appartient aux valeurs autorisées de la section 6.
6. IC : une série constante donne `IC=NA` ; on vérifie 1 ≤ n_eff ≤ n.
7. Gains : `bounds_add_ratio` dans un cas censuré ; FPR H₀ du même titre ; statut `oracle`.
8. Refus de F2, de `jepa` et des dates ≥ 2020 ; déterminisme et invariance par `--jobs` sur une mini-grille.

## 13. Hypothèses par défaut (confirmées sauf avis contraire)

- **H1.** H = 750 et γ_H = 15 000 ; SR ∈ {4, 8, 16}.
- **H2.** Grille D5 de la section 2 ; tick pilote par cellule.
- **H3.** Bras `zero_neg` limité à P1-C, sur les fonds à zéros : nul de flux invalide, aucune garantie de FPR.
- **H4.** Références de niveau H₀ :
  - les générateurs D5 valides sont leur propre niveau atteint, par simulation directe ;
  - seul le choc reçoit un générateur symétrique apparié (signe journalier commun, état et q̂ réajustés) ;
  - aucune re-symétrisation de GJR, même comme benchmark ;
  - sur le brut, la référence valide est limitée à `half` ; un nul calibré symétrisé distinct pour `qhat` reste
    possible sur demande.
- **H5.** Effectifs de la section 8 ; `e10_gains.csv` en plus de `e10_cells.csv`.
