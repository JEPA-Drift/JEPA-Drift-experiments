# Plan — stream 23, E6 phase 1 : P1-D et P3-D sur dérives F4 (révision 2)

État : **GO reçu le 2026-10-22**. La révision 1 (base `5048a96`) avait vu son GO suspendu ; cette
révision 2 a été approuvée par l'écran d'approbation. Trace verbatim : `prompts/GO-stream-23.md` ;
décision : section « Décision GO intégrée » en fin de plan.

Base : `2b0b1cd` (HEAD de `stream-23`, `git status --porcelain` vide). Cette base contient 8b :
`/.venv` et `/external` ignorés, `pipelines.horizon_gamma`.

Exécution : `.venv` exclusivement, sans `conda activate`.
- Python et tests : `.venv/bin/python` et `.venv/bin/pytest`, avec
  `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42`.
- `make check` et `git commit` (son hook lance `make check`) s'exécutent avec
  `MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin` en tête du PATH.
- Après implémentation : **arrêt avant fetch, push et merge**.

## Contexte

Les wrapups 11 et 11b ont montré que l'information de localisation aux frontières SPY est du bruit
ou de la sélection. La contingence C1 (second ordre) devient donc plausible. La phase 1 mesure deux
choses :
- ce que les capteurs linéaires d'énergie, P1-D (indice équipondéré) et P3-D (factoriel et complet),
  détectent sur des dérives F4 injectées ;
- ce que coûte leur calibration.

P4-D attend la fusion du stream 17 et P5-D le stream 16. La formule de variance est une
**information gaussienne de conception** (`meta["info"]`), jamais la KL exacte des fonds t₇ ou D6.

## Révisions demandées et traitement

| demande | traitement |
|---|---|
| P1-D : flux d'énergie de l'Article B | q_t = `streams.energy_stream(r, μ̂, σ̂)`, r = moyenne transversale ; μ̂ = mean(r²) et σ̂ = std(r²) sur les lignes d'ajustement (calib pour D6, panel d'ajustement pour D5). Sonde refaite. |
| Γ_op avec le seuil final | D5 : Γ_z^op = λ_D5/λ_iid ; λ_in (règle D6 sur le panel d'ajustement) n'est qu'un diagnostic. |
| D6 réutilise ses 941 jours | FPR D6 dans l'échantillon, descriptif, **sans IC** ; G_ADD D6 `IC=NA` avec raison préfixée ; ⌊941/H⌋ n'est jamais présenté comme une taille effective. |
| D5 | IC de Wilson (FPR, taux) et bootstrap apparié du rapport des RMST_H. |
| PC2–PC3 | témoin négatif déclaré : exploratoire sur D6 (déjà sondé), préspécifié sur les panels de test D5. Les autres paires, choisies après sonde, sont exploratoires. |
| K sur D5 | K = 10 fixé, étiqueté conditionnel ; sensibilité K = 1. |
| Rotation | information conjointe seulement ; pas de partage par direction. |
| Budget | `floors.evidence_budget` comme repère de conception, jamais borne de délai du CUSUM. |
| Journaux et audits | `logs/e6/` local et ignoré, jamais indexé ; nouvelle entrée de `docs/DEVIATIONS.md` en anglais. |

## Constats des sondes (lecture seule)

### D6 : calib de `d3_239`

941 jours, lignes 2834–3774 (2016-04-07 → 2019-12-31), 239 titres finis, K = 10. Il y a 692
fenêtres à H = 250 et 442 à H = 500.

| moniteur | D | λ_req (H = 250 = H = 500) | λ_iid 250 / 500 | Γ^op 250 / 500 | Γ^spec | FPR dans l'éch. | niveau atteignable suivant 250 / 500 |
|---|---|---|---|---|---|---|---|
| P1-D (Article B ; σ̂/(√2μ̂) = 1,76) | 1 | 36,09 | 11,90 / 13,14 | 3,03 / 2,75 | 2,12 | 0 | 0,2775 / 0,5656 |
| P3-D factor | 10 | 172,49 | 8,31 / 9,25 | 20,75 / 18,65 | 1,68 | 0 | 0,2428 / 0,5249 |
| P3-D full | 238 | 182,87 | 6,99 / 7,70 | 26,16 / 23,75 | 3,40 | 0 | 0,2370 / 0,5023 |

λ_req est le pic de l'épisode de volatilité dominant ; le FPR dans l'échantillon ne peut valoir que
0 ou au moins 24 %, si bien que 5 % est inatteignable. Sous dérive, les détections D6 coïncident
avec ce bloc d'égalité :
- **P1-D** : taux 0,277 et 0,566, c'est-à-dire le niveau suivant, dans 6 des 12 cellules, dont
  deux où le décalage moyen Δq est négatif ; taux nul ailleurs. 100 % des alarmes tombent à
  ± 7 jours du 2019-01-04.
- **P3-D** : alarmes entre le 2018-12-24 et le 2019-02-07, avec une part modale de 0,75 à 1.
- **PC2–PC3** : aucune détection (info conjointe ≤ 0,017 nat/jour).

Les cellules D6 sont donc descriptives et exploratoires.

### D5 : calibration seulement

Graines de sonde `[23, 99, …]`, disjointes des rôles finaux ; un panel d'ajustement de 941 jours,
400 panels de calibration ; aucun panel de test, aucune dérive.

| moniteur | D | λ_D5 250 / 500 | λ_in (panel d'ajust.) | λ_iid 250 / 500 | **Γ_z^op = λ_D5/λ_iid** | Γ^op dans l'éch. |
|---|---|---|---|---|---|---|
| P1-D | 1 | 88,78 / 157,94 | 25,55 | 11,90 / 13,14 | 7,46 / 12,02 | — |
| P3-D factor K = 10 (conditionnel) | 10 | 28,75 / 55,79 | 362,94 | 8,38 / 9,24 | 3,43 / 6,04 | 43,3 / 39,3 |
| P3-D factor K = 1 (sensibilité) | 1 | 10,68 / 14,07 | 276,54 | 11,86 / 13,24 | 0,90 / 1,06 | 23,3 / 20,9 |
| P3-D full | 238 | 4953 / 7899 | 350,18 | 6,98 / 7,72 | 710 / 1023 | 50,2 / 45,4 |

Sur D5, W est ajusté hors échantillon, sur le panel d'ajustement. Interprétation, à vérifier par la
moyenne de q sous H₀ que le CSV rapportera : ce blanchiment biaise l'énergie des panels
indépendants
- vers le bas en factor (valeurs propres du haut du bulk surestimées) ;
- vers le haut en full (petites valeurs propres sous-estimées).

La règle D6 dans l'échantillon (λ_in) ne transpose donc pas : son seuil est trop haut en factor,
trop bas pour P1-D et en full. C'est la mesure directe de la séparation calibration/évaluation.

## Conception

### Fonds

**D6 : lignes brutes de la calib de `d3_239`**
- Un signe par jour laisse q_t inchangé au bit, puisque l'énergie est paire. Il n'y a donc aucun
  pseudo-échantillon par signes et aucun `null_check` ; un test fige cette invariance.
- Représentation, μ̂/σ̂, seuils et évaluation utilisent les mêmes 941 jours (`in_sample = True`).
- Garde pré-J4 : le chargeur coupe au 2019-12-31 et refuse toute date ≥ 2020-01-01.

**D5 : `sim.garch_panel(T, 239, 0.08, 0.90, 7, rng, factor_rho=0.40)`, burn-in 1000**
- Rôles `SeedSequence([23, rôle, i])` disjoints :
  - 0 : panel d'ajustement (941 jours) ;
  - 1 : n_cal = 2000 panels de calibration (500 jours) ;
  - 2 : n_test = 2000 panels de test (500 jours).
- H = 250 lit les lignes [0, 250) des mêmes panels.
- Les panels de test sont partagés par H₀, toutes les cellules et tous les moniteurs (appariement).

### Cellules F4

`injection.inject(..., I_target=None, ...)` ; information lue dans `meta`, étiquetée
`gaussian_design`.

| cellule | paramètres | info D6 (nat/j) | statut D6 | statut D5 |
|---|---|---|---|---|
| H₀ | — | — | descriptif | préspécifié |
| deform r ∈ {1,25 ; 1,5 ; 2} | `subspace` (1, 2, 3) = PC2–PC4 | 0,0403 / 0,1418 / 0,4603 ; par direction ½(r − 1 − ln r) = 0,0134 / 0,0473 / 0,1534 | exploratoire (sondé) | préspécifié |
| rotate PC2–PC3, θ ∈ {15, 30, 45}° | `pair` (1, 2) | conjointe : 0,0023 / 0,0085 / 0,0170 | exploratoire (sondé), témoin négatif | **préspécifié**, témoin négatif |
| rotate PC1–PC2, θ ∈ {15, 30, 45}° | `pair` (0, 1) | conjointe : 0,0974 / 0,3635 / 0,7271 | exploratoire | exploratoire (choisie après sonde) |
| rotate PC2–PC12, θ ∈ {15, 30, 45}° | `pair` (1, 11) | conjointe : 0,1241 / 0,4632 / 0,9263 | exploratoire | exploratoire (choisie après sonde) |

Les valeurs propres sont lues sur la covariance d'ajustement de chaque fond, et l'info D5 est lue
dans `meta` à l'exécution.

Injection :
- D6 : une injection à τ* = début de calib, puis découpage des fenêtres [s, s + H). F4 agit ligne
  par ligne ; un test vérifie l'égalité avec une injection par onset, à l'arrondi près.
- D5 : M est obtenu par `inject` sur [ajustement | test], avec `calib = (0, 941)` et τ* = 941, puis
  appliqué aux lignes de chaque panel de test.

### Moniteurs

Tous utilisent un CUSUM strict unilatéral (`cusum.strict_cusum_vec`) avec δ = `pipelines.ENERGY_DELTA`
= 0,5.

- **P1-D, sans entrée `PIPELINES`** : q_t = (r_t² − μ̂)/σ̂ par `streams.energy_stream`, avec μ̂ et
  σ̂ calculés sur les lignes d'ajustement.
- **P3-D** : `pipelines.fit_pipeline(make_spec("P3-D", mode, K, H, dataset))`, puis
  `pipelines.run_pipeline` avec `state` ajusté sans dérive (dictionnaires Z par blocs de `CHUNK`).
  - D6 : factor (K = mp = 10) et full.
  - D5 : factor K = 10 (**conditionnel**), factor K = 1 (**sensibilité**) et full ; le seuil de
    l'état est remplacé par λ_D5.

### Seuils, Γ_z^op et FPR sous H₀

| fond | seuil | Γ_z^op | FPR | IC |
|---|---|---|---|---|
| D6 | `required_threshold` sur toutes les fenêtres de calib | λ_req/λ_iid | dans l'échantillon, et niveau atteignable suivant | **aucun**, descriptif |
| D5 | `required_threshold` sur les n_cal panels de calibration | **λ_D5/λ_iid** (seuil final) | atteint sur les n_test panels de test | Wilson 95 % ; région à 99 % de α avec le bruit 1/n_cal (`pipelines.summarize`), verdict consigné tel quel |
| D5, diagnostic | règle D6 sur le panel d'ajustement (λ_in) | λ_in/λ_iid | atteint sur les panels de test | Wilson 95 % |

Valeurs communes :
- λ_iid : trajectoires i.i.d. (χ²_D − D)/√(2D), N_cal = 20 000 (D = 1 pour P1-D).
- Γ^spec : `gamma_spectral` sur la calib (D6) ou le panel d'ajustement (D5).
- Moyenne et écart-type de q sous H₀ (calib pour D6, panels de calibration pour D5), qui exposent
  le biais hors échantillon.

### Mesures et censure (préfixées)

1. **Délai** : délai = alarm_index − τ* + 1 ∈ [1, H]. Une trajectoire sans alarme dans H est
   censurée.
2. **RMST_H** : moyenne de min(délai, H), une trajectoire censurée comptant H. C'est une borne
   inférieure de l'ADD dès qu'il y a censure. On rapporte aussi le taux de détection, la part
   censurée, la médiane (« > H » si le taux est < 0,5) et la moyenne conditionnelle aux
   détections.
3. **G_ADD(A → B)** = RMST_H(A)/RMST_H(B), sur les mêmes fenêtres ou panels :
   - A = P1-D ;
   - B ∈ {P3-D factor, P3-D full}, plus factor K = 1 sur D5 ;
   - étiquette `exact` (aucune censure), `lower_bound` (censure dans A seulement) ou
     `undetermined` (censure dans B).
4. **IC** :
   - D5 : Wilson 95 % pour les taux ; bootstrap apparié percentile du rapport des RMST_H sur les
     panels de test, B = 2000, `SeedSequence([23, 4, cellule, H])`.
   - D6 : **`IC=NA`**, avec la raison écrite dans le CSV. Les fenêtres à moins de H jours d'écart
     partagent des jours, et la volatilité allonge encore la portée de dépendance. Un bootstrap par
     blocs ou un deff exige des blocs de longueur ≥ H et au moins 10 blocs [Künsch, 1989 ; Lahiri,
     2003, *Resampling Methods for Dependent Data*]. Or n_fenêtres/H vaut 2,8 (H = 250) et 0,9
     (H = 500).
5. **Diagnostics D6** : part du bloc d'égalité (niveau atteignable suivant), date d'alarme modale et
   part des alarmes à ± 7 jours de cette date.
6. **Information** :
   - `meta["info"]` est conjointe ;
   - la valeur par direction n'est donnée que pour la déformation, où l'information est additive
     sur des directions propres (½(r − 1 − ln r)) ;
   - la rotation n'a que l'information conjointe ;
   - τ_budget = ln(H/α)/I (`floors.evidence_budget`) est étiqueté « design reference » et n'est
     jamais lu comme une borne du CUSUM.

### Sorties

- `results/e6/e6_cells_phase1.csv`, suivi : une ligne par (fond, H, moniteur, K, cellule), écrite
  par `pipelines.save_fair_csv`, avec les colonnes `status`, `in_sample`, `ci_reason`, `info_model`
  et `K_choice`.
- `figures/e6/e6_phase1_delays.{png,pdf}` et `figures/e6/e6_phase1_gadd.{png,pdf}`, tirées du CSV
  seul, suivies.
- `logs/e6/phase1.log`, **local et ignoré**, jamais indexé.
- En `--quick`, figures et log sont écrits sous `--out`.

## Fichiers touchés

| fichier | action |
|---|---|
| `experiments/e6_second_order.py` | nouveau ; `--phase {1,2}` (2 refusé avant le stream 16), `--config`, `--quick`, `--out`, `--fig-dir`, `--log-dir`, `--jobs` (pool `spawn`, résultats indépendants du nombre de processus) |
| `configs/e6.yaml` | nouveau ; H, cellules et statuts, paramètres D5, rôles de graines, n_cal = n_test = 2000, B = 2000, K_D5 ∈ {10, 1}, tailles `--quick` (200) |
| `tests/test_e6.py` | nouveau ; tailles réduites (`make check` < 5 min) |
| `results/e6/e6_cells_phase1.csv`, `figures/e6/*` | sorties suivies |
| `docs/DEVIATIONS.md` | entrée `C-E6-phase1` **en anglais** : D6 dans l'échantillon (bloc d'égalité, FPR 0, IC=NA) ; D5 à graines disjointes, K conditionnel et K = 1 ; biais de blanchiment hors échantillon ; paires exploratoires ; règles de censure |
| `prompts/plans/plan-23.md`, `prompts/GO-stream-23.md`, `prompts/wrapups/wrapup-23.md` | plan avec « Décision GO intégrée » ; messages de revue et GO transcrits mot pour mot ; wrapup en anglais |

Aucune modification de `jepadrift/`, `.gitignore` ou `Makefile`.

## Tâches (TDD, après le GO)

1. Vérifier HEAD = `2b0b1cd` et `git status --porcelain` vide. Transcrire les revues et le GO dans
   `prompts/GO-stream-23.md`, puis enregistrer `prompts/plans/plan-23.md`.
2. Écrire `tests/test_e6.py` d'abord (rouge). Les tests couvrent :
   - l'invariance des énergies au signe journalier (au bit) ;
   - les fenêtres F4 identiques aux injections par onset ;
   - P1-D égal à `energy_stream` avec μ̂ et σ̂ d'ajustement ;
   - la règle de seuil et Γ_z^op = λ_final/λ_iid ;
   - la censure, RMST_H et les étiquettes de G_ADD ;
   - la règle `IC=NA` sur D6 ;
   - Wilson et le bootstrap apparié ;
   - les rôles D5 disjoints et l'invariance au nombre de processus (1 contre 2) ;
   - la garde pré-J4 ;
   - le refus de `--phase 2` ;
   - un smoke test de la CLI (CSV identique d'une exécution à l'autre).
3. Écrire `experiments/e6_second_order.py` et `configs/e6.yaml` jusqu'au vert.
4. Exécuter la commande rapide du prompt, puis supprimer `results/e6_quick`. Lancer le run complet,
   puis le relancer et vérifier le même SHA-256 ; vérifier aussi l'égalité entre `--jobs 1` et
   `--jobs 8` en mode rapide. Tout écart aux sondes est consigné sans être corrigé.
5. Écrire l'entrée de `docs/DEVIATIONS.md` en anglais.
6. Clôture :
   - wrapup en anglais ;
   - `tools/reindex_graphify_jcodemunch.sh` ;
   - `PATH="$MAKEBIN:$PATH" make check` ;
   - commit unique `feat(e6): measure second-order F4 detection with P1-D and P3-D (stream 23,
     phase 1)`, indexé chemin par chemin, sans log ;
   - `git status --porcelain` vide ;
   - **arrêt**, sans fetch, push ni merge.

## Vérification

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42
MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin
.venv/bin/pytest -q tests/test_e6.py
.venv/bin/python experiments/e6_second_order.py --phase 1 --quick --out results/e6_quick && rm -r results/e6_quick
.venv/bin/python experiments/e6_second_order.py --phase 1 --out results/e6
sha256sum results/e6/e6_cells_phase1.csv     # identique sur une seconde exécution
PATH="$MAKEBIN:$PATH" make check
git status --porcelain                        # vide après le commit
```

## Questions bloquantes (défaut entre parenthèses)

- **Q1. Cellules de dérive D6.** Elles ne mesurent que l'appartenance au bloc d'égalité de
  l'épisode 2018–2019. (Les garder, descriptives, avec `IC=NA` et les diagnostics de bloc.)
  Alternative : limiter D6 à H₀, aux seuils et à Γ_z^op.
- **Q2. Biais hors échantillon sur D5.** La moyenne de q sous H₀ est loin de 0, et λ_D5 vaut 4953
  à 7899 en full. (Flux P3-D inchangé, sans recentrage, le biais étant rapporté.) Alternative :
  recentrer q sur les panels de calibration, ce qui changerait la spécification de P3-D.
- **Q3. Convention de K = 1.** (`PCAOrthogonal(K=1)` : résiduel = PC2 seul ; le modèle vrai n'a
  aucun facteur résiduel au-delà de PC1, et K = 0 est inadmissible.)
- **Q4. Paires exploratoires PC1–PC2 et PC2–PC12.** (Les garder sur les deux fonds, étiquetées
  exploratoires.) Alternative : déformation et PC2–PC3 seulement.
- **Q5. Règle `IC=NA` pour D6.** (Au moins 10 blocs de longueur H : toujours NA sur 941 jours.)

Défauts non bloquants :
- facteur sectoriel reporté (`injection.py` inchangé) ;
- n_cal = n_test = 2000, B = 2000, `--quick` à 200 ;
- G_ADD calculé depuis P1-D.

## Hors périmètre

P4-D (après le stream 17), P5-D et la porte J4 (phase 2, après le stream 16), facteur sectoriel,
toute ligne datée de 2020 ou après.

## Décision GO intégrée (2026-10-22)

GO de l'orchestrateur pour le plan révisé, phase 1 P1-D/P3-D. Les défauts de Q1 à Q5 sont approuvés :

| question | décision |
|---|---|
| Q1 | les cellules de dérive D6 restent, descriptives, avec `IC=NA` et les diagnostics du bloc d'égalité |
| Q2 | aucun recentrage du flux P3-D sur D5 ; le biais hors échantillon est rapporté |
| Q3 | K = 1 en sensibilité sur D5 : `PCAOrthogonal(K=1)`, résiduel = PC2 seul |
| Q4 | les paires exploratoires PC1–PC2 et PC2–PC12 restent, sur les deux fonds |
| Q5 | règle `IC=NA` pour D6 : au moins 10 blocs de longueur H requis |

Les défauts non bloquants sont conservés : facteur sectoriel reporté, n_cal = n_test = 2000,
B = 2000, `--quick` à 200, G_ADD calculé depuis P1-D.

Consignes d'exécution :
- n'implémenter que ce plan, dans le worktree `stream-23`, via `.venv` ;
- transcrire le GO et les revues dans `prompts/GO-stream-23.md` ;
- consigner les écarts dans `docs/DEVIATIONS.md` ;
- exécuter les contrôles ;
- s'arrêter avant fetch, push et merge.
