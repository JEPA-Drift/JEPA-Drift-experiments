# Plan — stream 12, E1 : le problème (§2) sur fonds D6, pipelines 1 → 2 → 3 → 3-CS, critères de J2

Ce fichier consigne le plan exécuté du stream 12 : la décision GO du 2026-10-28 (ci-dessous), puis le plan delta
révision 2 (annexe A, 2026-10-28) et le plan révision 1 (annexe B, 2026-10-23), recopiés tels qu'ils ont été soumis.
En cas de conflit, la présente section prévaut, puis l'annexe A, puis l'annexe B. Prompt canonique :
`prompts/streams/prompt-12-e1.md` ; GO verbatim : `prompts/GO-stream-12.md`.

## Décision GO intégrée (2026-10-28)

- **GO final de l'orchestrateur** reçu le 2026-10-28 et transcrit verbatim dans `prompts/GO-stream-12.md`. L'ancien
  GO (2026-10-18) y est conservé sous la mention « spécification remplacée, non applicable » (Q9).
- **Q2–Q10 acceptées** :
  - (a) `inject` accepte `params["fit"]` (cache de `fit_background`) et `params["sr_asset"]` ;
  - (b) `cross_independence` : porte de Holm au niveau de famille 1 % sur les p-valeurs des paires ;
  - (c) déplacement verbatim de `spy_phases`, `char_directions`, `projections`, `subspaces`, `N_PC` et `MAX_DIM`
    vers `jepadrift/stats/drift.py`, ré-exportés par l'audit ;
  - Q10 : F2 injectée sur les quatre caractéristiques continues `c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21`
    (`C-e1-f2-chars`).
- **J2(i) primaire** : 54 contrôles, 2 000 réplications chacun, seuil |FPR − ℓ_H| ≤ 1 point. Le risque a priori de
  faux FAIL, 0,813 sous exactitude des 54 flux, est mentionné à côté du verdict. Le verdict est rapporté sans rerun
  ni changement de graines.
- **Φ(γ·I)/I** (`floors.phi`) est étiquetée « approximation de diffusion » (colonne `add_diffusion_approx`), jamais
  borne exacte d'ADD à γ fini. Cette étiquette remplace les mentions « Lorden analytique » ou `lorden_add` des
  annexes ; seul le budget ln γ/I (Lemme 1) reste une quantité exacte.
- **Fenêtre brute ≥ 2005-01-04** (garde bloquante), **mêmes cinq titres que E3** (`composition_for(5, N)`),
  **remise à zéro du CUSUM par fenêtre**, **test RED d'invariance au préfixe P1-C** avant le code de run.
- **MCP** : graphify et jcodemunch rechargés dans la session d'exécution et vérifiés par appel avant la première
  écriture (`graph_stats` : 3 506 nœuds ; `resolve_repo` : dépôt indexé, chargeable).
- **Exécution** : `.venv`, `MPLBACKEND=Agg`, TDD, tests, `make check`, empreintes SHA-256 et wrapup ; uniquement E1
  dans ce worktree. Aucun autre stream, aucun fetch, rebase, push ni fusion. Arrêt au commit local propre et vérifié.

---

# Annexe A — plan delta révision 2 (2026-10-28), tel que soumis

## Plan delta — stream 12 (E1), révision 2

**État : en attente du GO de l'orchestrateur.** Aucun fichier du dépôt n'est modifié et aucun run n'est lancé.
L'ancien `prompts/GO-stream-12.md` (2026-10-18) porte sur une spécification antérieure : il ne vaut pas GO de ce plan.

### Contexte
Le prompt 12 a été révisé : borne réelle stricte, titres de J2(i) communs avec E3, P1-C locale, J2(i) à 2 000
réplications. L'ancien GO précède ces révisions. Ce delta s'applique au prompt 12 et au plan révision 1 du 2026-10-23
(`~/.claude/plans/amor-age-stream-glimmering-turing.md`). Les §2–§10 et §15 de ce plan restent en vigueur, sauf
mention contraire ci-dessous. Après le GO seulement :
1. GO verbatim en tête de `prompts/GO-stream-12.md`, l'ancien GO conservé sous « spécification remplacée » (Q9) ;
2. enregistrement de `prompts/plans/plan-12.md` avec « Décision GO intégrée » ;
3. TDD, puis `make check` et commit local vérifié ; arrêt avant fetch, fusion ou push.

### Constats revérifiés le 2026-10-28 (lecture seule)
- `stream-12` = `c284823`, arbre propre. `main` = `3f8750d` : diff net de 9 fichiers (handover, slides), rien dans
  `jepadrift/`, `experiments/` ni `tests/`. Aucun impact sur E1.
- `composition_for(5, 97)` = [24, 71, 56, 46, 75] ; `composition_for(5, 239)` = [60, 177, 141, 116, 184]. Les deux
  sont disjoints de `composition_for(20, N)`. Valeurs obtenues par exécution.
- E3 (worktree `stream-13`, non commité) : `WINDOW = 2005-01-04..2019-12-31`, `N_TICKERS = 5`,
  `pl.composition_for(N_TICKERS, n_cols)` sur `d2_us97` et `d3_239`. Les titres sont donc les mêmes que dans E1.
- API confirmée : `pipelines.{null_check, _null_block, _coins, _window, horizon_gamma, summarize}`,
  `monitors.cusum.bilateral_delay_vec`, `monitors.eprocess.log_edetector`, `monitors.lattice.select_threshold`,
  `floors.{evidence_budget, first_order_floor, dictionary_multiplier, mixture_multiplier, phi}`.

### Delta

### 1. Date brute ≥ 2005-01-04 (garde bloquante)
- Toute ligne réelle lue doit être datée dans [2005-01-04 ; 2019-12-31]. Sinon, une exception est levée ; aucune
  troncature silencieuse. `--include-test-window` est refusée sans `configs/FROZEN.json` concordant.
- D2 : lignes [0, 3 774), inchangées. D3 : le 2005-01-03 est retiré ; E1 lit les lignes absolues [1 257, 5 031),
  soit 3 774 jours.
- La calib est inchangée : 2016-04-07 → 2019-12-31, 941 jours. Ceci tranche le point ouvert du handover §3.6 :
  absolu [4 090 ; 5 031) = relatif `pre_monitor` [2 834 ; 3 775) (E6) = relatif E1 [2 833 ; 3 774). L'alignement se
  fait par dates. L'état P3-C factor doit égaler les sidecars `z_*.json` commités.
- Les préfixes restent dans la fenêtre :
  - P2-C bootstrap (H_ref = 500) tire τ* ∈ [500 ; T − H) ;
  - la calibration R15 utilise `null_rows = pre_monitor` coupé au 2005-01-04, étiquetée rétrospective.
- Bras C, D3 : la première phase SPY passe de 697 à 696 jours. Les transitions (9, 10, 9) sont inchangées.
- Test `test_window_strict_bounds` : première date 2005-01-04 et dernière 2019-12-31 sur les deux jeux. Une ligne
  datée 2005-01-03 ou 2020-01-02 doit lever l'exception.

### 2. `composition_for(5, N)`, commune à E3
- Titres de J2(i) : D2 COST, SHW, SO, MDLZ, PSA ; D3 CASY, KEY, GPC, ERIE, LRCX. Les bras A et C gardent
  `composition_for(20, N)` (composition R15 figée).
- Pas de nouveau code partagé : `composition_for` est déjà dans `jepadrift.pipelines`. `WINDOW` et `5` sont deux
  constantes locales, comme dans E3.
- `tests/test_e1.py` fige les indices littéraux. Une assertion littérale identique côté E3 (hors périmètre 12,
  signalée à l'orchestrateur) rendrait toute divergence bloquante dans les deux streams.

### 3. Remise à zéro du CUSUM par fenêtre
- Registre (P2-C, P3-C, P3-CS, P7) : l'état repart de zéro à τ* via `pipelines._window` (`pre = 0`). P2-C bootstrap
  lit les H_ref lignes précédentes pour son seul recentrage R15, sans aucun état de CUSUM antérieur.
- P1-C locale (hors registre, comme dans E10) :
  - elle ne reçoit que Y = X[τ*:τ*+H, titres] ;
  - lecture exacte : `bilateral_delay_vec(b − c, 0.1, select_threshold(...)["threshold"])` avec S₀ = 0 ;
  - lecture anytime-valid : `log_edetector` avec M₀ = 0 ;
  - c = ½ sur D6, q̂ de calib au bras C ;
  - les pièces des nuls sont tirées sur Y seulement.
- Bras C : chaque phase repart de zéro à sa frontière, avec q̂ figé.

### 4. Invariance au préfixe P1-C (tests rouges avant tout code de run)
- `test_p1c_cusum_resets_at_onset` :
  - avec un préfixe entièrement positif, S⁺ atteindrait 0,4·τ*, bien au-delà de 10,3 ;
  - l'offset d'E1 égale celui de la fenêtre seule ;
  - le contrefactuel sans remise à zéro alarme à l'offset 0, donc le test discrimine ;
  - même contrôle pour l'e-détecteur.
- `test_p1c_prefix_invariance_each_onset` :
  - mini-cellule D6 de 40 réplications, 1 % de rendements nuls, τ* = 0 et τ* = T − H forcés ;
  - pour chaque onset, les lignes hors [τ*, τ*+H) sont remplacées par des zéros, puis par leur opposé, puis par un
    bruit gaussien ;
  - offsets des deux lectures et pièces : identiques au bit.
- `test_phase_monitor_resets_at_each_boundary` (bras C).

### 5. J2(i) : analyse primaire à 2 000 réplications et risque des 54 contrôles
- **Contrôles.** 54 au total, chacun à 2 000 réplications :
  - P1-C exacte : 5 titres × 2 jeux × H ∈ {750, 2 000} = 20 ;
  - canaux factor de P3-C en lecture exacte : (6 + 11) × 2 H = 34.
- **Mécanisme.** P3-C : `pipelines.null_check(specs, X, splits, 2000, key)`. P1-C : `_null_block` et `_coins` sur la
  colonne du titre. Une symétrisation D6 neuve par réplication dans les deux cas.
- **Règle primaire du prompt, inchangée.** Un contrôle passe ssi |FPR − ℓ_H| ≤ 0,01, avec ℓ_750 = 0,0439467 et
  ℓ_2000 = 0,0456695. J2(i) passe ssi les 54 contrôles passent.
- **Risque de faux FAIL, chiffré avant tout tirage.**
  - Sous exactitude, un contrôle échoue avec une probabilité de 0,0293 à H = 750 (PASS ssi k ∈ [68 ; 107] alarmes
    sur 2 000) et de 0,0319 à H = 2 000 (PASS ssi k ∈ [72 ; 111]).
  - Les contrôles sont indépendants sachant le panel (clés distinctes). On attend donc 1,65 faux FAIL, et
    **P(J2(i) = FAIL | 54 flux exacts) = 1 − 0,9707²⁷ · 0,9681²⁷ = 0,813**.
  - Ce risque est inscrit à côté du verdict dans `e1_j2_summary.txt`. Un FAIL est rapporté tel quel.
- **Diagnostics préenregistrés, sans effet sur le verdict :**
  - k, le nombre d'échecs, et P(#FAIL ≥ k | exact) sous la loi de Poisson-binomiale exacte ;
  - p-valeurs binomiales exactes bilatérales, avec Holm au niveau de famille 1 % ;
  - appartenance à la région à 99 %.
- **Préenregistrement.**
  - Clés `[12, crc32("full|j2i|<jeu>|<H>")]`, fixées dans `configs/e1.yaml`.
  - `--quick` utilise le libellé `quick|`, avec la mention « pas un verdict J2 ».
  - Aucun rerun, ni changement de clés ou d'effectif après le résultat. Seule exception : un défaut de code avéré,
    corrigé et consigné (`C-e1-j2i`), puis un recalcul aux mêmes clés.

### 6. FPR atteint
- Par lecture, le FPR(H) est mesuré sur les cellules H₀ (1 000 réplications par jeu et par H). Il porte un IC de
  Wilson à 95 % conditionnel au panel, à côté de sa cible et de la région à 99 % de `summarize`.
- Chaque ligne de gain porte les FPR atteints de ses deux pipelines. Pour P1-C, c'est le FPR du titre médian ou du
  titre oracle, pas la moyenne des 20.
- E-détecteurs à γ_H : ≤ α est une borne, pas un niveau atteint ; on attend un FPR très inférieur à α.
- « À fausse alarme égale » est réservé à G_ADD,ex (même ℓ_H). La marge d'équivalence de ±1 point est fixée avant
  test : l'étiquette `equal_fa_verified` exige que l'IC apparié de la différence tienne dans [−0,01 ; 0,01] ; sinon
  `equal_fa_not_shown`. Les autres gains sont dits « à seuil nominal commun ». Pas de lecture iso-FPR.
- P3-D et bras C : fenêtres chevauchantes, taux descriptifs sans IC binomial.

### 7. Censure
- Par cellule et par lecture, cinq quantités jamais confondues :
  - `add_h` = moyenne de min(T, H) ;
  - `det_rate`, avec IC de Wilson ;
  - `censored_share` ;
  - `mean_detected` ;
  - `median_delay`, NaN et signalée si `det_rate` ≤ 0,5.
- G_ADD,H porte une étiquette : `uncensored`, `lower_bound` (censure dans A seulement) ou `undetermined` (censure
  dans B).
- L'ADD de Lorden est seulement analytique : `phi(γ_H·I_x)/I_x`, à côté du budget `evidence_budget(γ_H, I_x)`.
- Prévisions et mesures ne sont juxtaposées que si la censure est ≤ 5 % dans les deux cellules ; sinon
  `not_directly_interpretable`.
- À H = 2 000, tout onset précède la calib : toutes les cellules portent `retrospective = True`.

### 8. Coûts
- Coûts unitaires mesurés le 2026-10-23 (un fil). Les blocs suivants sont en temps CPU :
  - A : ≈ 0,5 h ;
  - H = 750 : ≈ 0,15 h ;
  - J2(i) (108 000 trajectoires) : < 0,05 h ;
  - B avec pilote : ≈ 1,6 h ;
  - G_SR : ≈ 0,3 h ;
  - C : ≈ 0,1 h.
- Total ≈ 2,7 h, ≈ 4 h avec la marge × 1,5. Temps mural : 12 à 20 min à `--jobs 24` (défaut, machine partagée).
- Pic mémoire ≈ 1 Go par processus. Aucun tableau (J, K, T) ne dépasse 0,24 Go, sous la limite de 2 Go.
- `--quick` remesure chaque bloc et extrapole avant le run complet.
- Si la projection dépasse 8 h, on réduit dans cet ordre, en consignant chaque réduction (`C-e1-sizes`) :
  G_SR 200 → 100, puis B 200 → 100, puis A 1 000 → 500.

### 9. Défauts retenus (Q2–Q10, inchangés depuis la révision 1)
- Q2 : changements (a), (b) et (c) de `pipelines.py` (plan révision 1, §11).
- Q3 : voir le §6.
- Q4 : P3-CS (a) à γ = 20.
- Q5 : règles des pentes et de PASS de (ii), (iii) et (iv).
- Q6 : bras C à γ_L = L/α.
- Q7 : mélange avec s² ajusté sur l'amplitude injectée, étiqueté oracle.
- Q8 : aides de délai locales, marquées `# ponytail:` et `C-e1-local-helpers`.
- Q9 : traitement des fichiers GO.
- Q10 : F2 utilise les 4 caractéristiques continues (`c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21`). C'est un
  écart à la lecture littérale « 15 colonnes » du prompt, consigné `C-e1-f2-chars`. Le bras C garde les 15 colonnes
  de l'audit.

### Fichiers touchés (après GO)
- Création : `experiments/e1_problem.py`, `configs/e1.yaml`, `tests/test_e1.py`, `results/e1/*`, `figures/e1/*`,
  `logs/e1/`, `prompts/plans/plan-12.md`, `prompts/wrapups/wrapup-12.md`.
- Modification : `jepadrift/pipelines.py` (Q2), `docs/DEVIATIONS.md` (`C-e1-*`, en anglais),
  `prompts/GO-stream-12.md`.

### Vérification (chaque commande échoue sur divergence)
```bash
.venv/bin/pytest -q tests/test_e1.py
MPLBACKEND=Agg .venv/bin/python experiments/e1_problem.py --quick --out results/e1_quick
MPLBACKEND=Agg .venv/bin/python experiments/e1_problem.py --quick --out /tmp/e1_quick2 \
  && for f in results/e1_quick/*.csv; do cmp "$f" "/tmp/e1_quick2/$(basename "$f")" || exit 1; done
MPLBACKEND=Agg .venv/bin/python experiments/e1_problem.py --out results/e1 && test -s results/e1/e1_j2_summary.txt
make check
```

### Questions bloquantes
Aucune. Le GO vaut acceptation de ce delta, y compris Q10 et le risque a priori de 0,813 sur J2(i).

---

# Annexe B — plan révision 1 (2026-10-23), tel que soumis

# Plan — stream 12, E1 : le problème (§2) sur fonds D6, pipelines 1 → 2 → 3 → 3-CS, critères de J2 (révision 1)

**État : en attente de l'audit et du GO de l'orchestrateur.** Aucun fichier du dépôt n'est modifié. L'approbation de
l'écran ExitPlanMode ne vaut pas GO. L'ancien `prompts/GO-stream-12.md` (2026-10-18) porte sur une spécification
antérieure et ne vaut pas GO de ce plan. Après le GO seulement :
1. transcription verbatim dans `prompts/GO-stream-12.md` (cadre en français) ;
2. enregistrement de `prompts/plans/plan-12.md` avec « Décision GO intégrée » ;
3. exécution TDD, puis arrêt au commit local vérifié, avant fetch, fusion ou push.

Toutes les commandes s'exécutent dans `~/JEPA-stream-12`, jamais dans l'arbre principal.

Cette révision intègre l'amorçage `prompts/amorcage-12.md` du dépôt principal (identique à celui du worktree) et les
consignes du 2026-10-23 :
- date réelle strictement ≥ 2005-01-04 ;
- cinq titres `composition_for(5, N)` ;
- test explicite de remise à zéro du CUSUM et d'invariance au préfixe de la P1-C locale ;
- J2(i) à 2 000 répétitions, tolérance primaire ±1 point, sans rerun opportuniste.

## 0. Constats (lecture seule, 2026-10-23)

**Dépôt et outils**
- 8b est fusionné sur `main` : `24be667` et la fusion `33d847d` sont ancêtres de `main` = `stream-12` = `c284823`, et
  l'arbre est propre. `origin/main` = `ef63362` : `main` local a 11 commits d'avance, et aucun fetch n'a été fait.
- Stream 27 (E10) est fusionné (`57c3a34`). Il définit localement `coin_bits`, `alarms`, `restricted`, `delay_stats` et
  `wilson`. Stream 23 (E6, `7e4c7a1`) n'est pas fusionné.
- MCP :
  - Graphify est reconnecté (3 317 nœuds) ; ses voisinages ont servi au rayon d'impact de `inject` et de
    `cross_independence` (seul appelant : `_cal_p3c`).
  - jCodeMunch a été indexé le 2026-10-23 à 00:09, avant que le worktree n'avance sur `c284823` :
    `e10_robustness.py` a été lu directement. Réindexation en fin de stream.
- Environnement :
  - `.venv/bin/python` et `.venv/bin/pytest` ;
  - `OMP/MKL/OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg` ;
  - `make` vient de `~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin` ;
  - machine : 48 cœurs, 162 Go disponibles, inactive au moment des sondes.

**Fenêtre réelle stricte [2005-01-04 ; 2019-12-31]**
- D2 : lignes [0, 3 774), inchangées.
- D3 : `pre_monitor` commence le 2005-01-03 (ligne 1 256). E1 lit les lignes [1 257, 5 031), soit 3 774 jours.
- Sur les deux panels coupés : pretrain [0, 2 768), calib [2 833, 3 774), soit 2016-04-07 → 2019-12-31 (941 jours).
  Les deux panels sont finis.
- Les lignes de calib sont inchangées : l'état P3-C factor doit égaler les sidecars `z_*.json` commités. Ce contrôle
  est repris d'E10.

**Canaux et titres**
- P3-C : factor 6 canaux (D2) et 11 (D3) ; full 97 et 239. P3-CS : factor 5 et 10 ; full 96 et 238.
- `composition_for(5, N)`, titres de J2(i) :
  - D2 [24, 71, 56, 46, 75] = COST, SHW, SO, MDLZ, PSA ;
  - D3 [60, 177, 141, 116, 184] = CASY, KEY, GPC, ERIE, LRCX.
  Aucun n'appartient à `composition_for(20, N)`.

**Treillis** (δ = 0,1, bilatéral strict, niveau le plus proche ≤ α)

| H | L (unités) | λ | `threshold` | niveau exact ℓ_H |
|---|---|---|---|---|
| 750 | 45 | 9,0 | 9,1 | 0,0439467 |
| 2 000 | 51 | 10,2 | 10,3 | 0,0456695 |

**Données et audit**
- Caractéristiques D3 : 15 colonnes, dont 4 continues (`c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21`) et 11
  indicatrices GICS statiques (`C-D3-gics-static`).
- Bras C, D3 : retirer le 2005-01-03 ôte une ligne à la première phase SPY (697 → 696), dans la première transition de
  chaque datation. Le nombre de transitions ne change pas (9, 10, 9) ; D2 n'est pas touché.
- Rappels de l'audit :
  - N1 = 1,968 / 1,925 (D2, brut / χ²) et 1,998 / 1,980 (D3) ;
  - K_eff_meas = 3,64 (D2) et 3,85 (D3) ;
  - symétrie rejetée sur D2 PC1 et PC3, et sur D3 PC1, PC2, PC3 et `char:rev_21`.
- R15 : H_ref + H = 500 + 750 = 1 250 jours (le prompt écrit 1 500). C'est toujours plus que les 941 jours de calib,
  d'où `null_rows = pre_monitor` et une calibration rétrospective.
- `floors` fournit `evidence_budget`, `first_order_floor`, `dictionary_multiplier`, `mixture_multiplier` et `phi`.

## 1. Révisions par rapport au plan du 2026-10-22

| point | plan précédent | révision |
|---|---|---|
| Fenêtre réelle | garde [2005-01-01 ; 2019-12-31] | garde bloquante stricte : toute ligne réelle lue est datée dans [2005-01-04 ; 2019-12-31] ; D3 commence à la ligne 1 257 |
| Titres de J2(i) | 5 premiers titres | `composition_for(5, N)`, les mêmes que dans E3 |
| P1-C locale | invariance au partitionnement et à `--jobs` | en plus, tests explicites de remise à zéro du CUSUM à l'onset et d'invariance au préfixe, pour chaque onset d'une mini-cellule (§9) |
| J2(i) | Q1 : 10 000 répliques recommandées | 2 000 répliques et tolérance primaire ±1 point ; risque de faux FAIL chiffré ; clés préenregistrées ; aucun rerun opportuniste (§5) |
| Q2–Q9 | questions ouvertes | défauts retenus (§15) |
| Coûts | coûts unitaires supposés | coûts unitaires mesurés (§10) |
| F2 injectée | 15 colonnes, implicitement | Q10, défaut : les 4 caractéristiques continues causales |
| Prévisions | formules locales | fonctions de `floors` (§8) |
| Vérifications | `sha256sum` affichés | assertions `cmp` et `test` qui échouent sur divergence (§14) |

## 2. Conventions de mesure

**Délais**
- Délai observé = alarm_index − τ* + 1 (`C-pipe-delay`). Tous les moniteurs repartent de zéro à τ*.
- Cinq quantités par cellule et par lecture, jamais confondues :
  - `add_h` = moyenne de min(T, H), une trajectoire sans alarme comptant H. C'est le délai restreint (`rmst` d'E10).
  - `det_rate`, avec IC de Wilson à 95 %.
  - `censored_share` = 1 − `det_rate`.
  - `mean_detected`, moyenne des délais observés.
  - `median_delay`, définie seulement si `det_rate` > 0,5 ; sinon NaN, avec signalement.
- **ADD de Lorden : réservé aux bornes analytiques.** `add_h` moyenne des onsets uniformes, avec censure, et n'estime
  pas le pire cas de Lorden. La seule colonne de Lorden est analytique : `lorden_add` = Φ(γ_H·I_x)/I_x (`floors.phi`)
  pour l'oracle gaussien. Elle figure à côté du budget `budget_days` = ln γ_H/I_x (`floors.evidence_budget`).

**Gains**
- **G_ADD,H(A→B)** = add_h(A)/add_h(B), à lecture, H et réplications égaux. IC par bootstrap apparié des réplications
  (B = 2 000).
- Étiquette de censure :
  - `uncensored` : aucune censure ;
  - `lower_bound` : censure dans A seulement, le rapport sous-estime celui des délais moyens ;
  - `undetermined` : censure dans B.

**Rétrospectif**
- États des représentations, Σ̂ et géométrie d'injection sont ajustés une seule fois, sur la calib 2016-04-07 →
  2019-12-31 du panel d'origine.
- À H = 2 000, τ* ≤ 1 774 < 2 833 : tout onset précède la calib, et la fenêtre surveillée la recouvre dès τ* > 833.
- Toutes les cellules portent `retrospective = True`, sans interprétation prospective. Les signes D6 neufs rendent le
  nul exact sachant le panel (Lemme 2), ce qui n'ôte pas ce caractère.

**IC**
- Sachant le panel 2005–2019, les réplications D6 sont i.i.d. (signes, onsets et directions neufs) : deff = 1 par
  construction, et les IC de Wilson sont conditionnels au panel.
- Le bras B rééchantillonne les chaînes, qui sont des grappes.
- Aucune SEM n'est calculée sur des fenêtres chevauchantes : P3-D et bras C restent descriptifs, sans IC.

**Oracles**
- `oracle = True` marque le meilleur titre P1-C et le meilleur canal exact de P3-C, choisis a posteriori sur les mêmes
  réplications, ainsi que le mélange, dont s² est ajusté sur l'amplitude injectée (Q7).
- Aucun gain principal ne s'appuie sur un oracle. La base P1-C principale est le titre médian, rang 10 sur 20 par
  `add_h` (`asset_selection = median`).

## 3. Lectures

γ_H = H/α vaut 40 000 à H = 2 000 et 15 000 à H = 750. P1-C passe par le noyau `monitors`, sans entrée de registre,
comme dans E10.

| pipeline | lecture | statistique, détecteur | seuil | cible FPR(H) | rôle |
|---|---|---|---|---|---|
| P1-C, 20 titres `composition_for(20, N)` | anytime-valid | e-détecteur CUSUM (`log_edetector`) sur 2b − 1 | γ_H | ≤ α | principal (titre médian) ; meilleur titre = oracle |
| P1-C | exacte | CUSUM bilatéral strict, δ = 0,1, sur b − ½ | `select_threshold(α, H=H)["threshold"]` (milieu), jamais `lam` | = ℓ_H | G_ADD,ex |
| P2-C, K = N | anytime-valid | `run_pipeline`, e-détecteur sur 2·moyenne des signes | γ_H | ≤ α | principal |
| P2-C | bootstrap R15 (H = 750) | fraction recentrée sur H_ref = 500, CUSUM bilatéral δ = 0 | λ_boot : 20 000 fenêtres d'une symétrisation, `pre_monitor` (rétrospectif) | ≈ α (+1/n_cal) | secondaire |
| P3-C | anytime-valid | dictionnaire : marché + résiduel factoriel (F3, F1), marché + résiduel complet (F2) | γ_H | ≤ α | principal |
| P3-C | exacte, par canal | CUSUM bilatéral, δ = 0,1 | treillis | = ℓ_H | diagnostic : canal marché préspécifié (F3), meilleur canal = oracle (F1, F2) |
| P3-C | mélange (`mixture_s2`) | e-détecteur marché + mélange sous-gaussien du résiduel | γ_H | validité approchée | diagnostic, porte de Holm à 1 % |
| P3-CS (b), `b = pc1` | anytime-valid | mises prévisibles ∝ 1/σ̂, dictionnaire | γ_H | ≤ α | principal |
| P3-CS (a) | e-processus | pari moyen sur les pivots | γ = 1/α = 20 (Ville, Q4) | ≤ α | secondaire |
| P7 | borne | CUSUM du LLR gaussien, Δ connu | γ_H | aucune | borne ; budget et Lorden analytiques |
| P3-D (H = 750) | bootstrap | énergie résiduelle, CUSUM δ = 0,5 | λ_req sur les fenêtres de calib (`C-P3D-windows`) | ≤ α dans l'échantillon | preuve d'orthogonalité, hors tableaux de gains |

P3-C et P3-CS sont en `factor` (K = mp) pour F3 et F1, en `full` pour F2.

## 4. Grille de calcul

### 4.1 Bras A — gains à information égale (convention a, H = 2 000)

**Fonds et onsets**
- `d2_us97` (N = 97) et `d3_239` (N = 239), avec une symétrisation D6 neuve par réplication.
- τ* = `draw_tau_star(0, T, 0, H)`, uniforme sur [0, 1 774].

**Cellules** : 15 cellules de 1 000 onsets, soit SR ∈ {2, 4, 8} × {F3, F1} sur D2 et D3, plus F2 sur D3. SR = 1 est
exclu (τ_γ ≈ 5 341 jours).

| SR | I (nat/j) | budget ln γ_H/I (j) | Lorden analytique Φ(γ_H·I)/I (j) |
|---|---|---|---|
| 2 | 0,00794 | 1 335 | 603 |
| 4 | 0,0317 | 334 | 194 |
| 8 | 0,127 | 84 | 59 |

**Familles**
- F1 : K = n₊ (6 / 11), soit PC1..PC(K_mp + 1) : exactement les canaux factoriels de P3-C.
- F2 : résidu GLS sur les chargements à K = n₊. C = les 4 caractéristiques continues (Q10), NaN → 0 et comptés.
  L'information réalisée sur [τ*, τ* + H) est rapportée (`info_realized`) à côté de la cible de calib.
- Les coefficients F1 et F2 sont tirés par réplication. La géométrie est celle de la calib d'origine, fournie par le
  cache de `fit_background` (§11 (a)).

**Pipelines et réplications**
- Toutes les lectures du §3 tournent sur chaque cellule.
- Les couples sans information (P3-CS sur F3, canaux résiduels de P3-C sur F3) sont étiquetés `no_information` : ce
  sont des contrôles nuls in situ.
- La clé de réplication exclut l'amplitude : fonds, onsets et directions sont les mêmes aux trois SR. Tous les
  pipelines d'une cellule lisent les mêmes réplications, d'où des gains appariés.
- **Cellules H₀** : 1 000 réplications par jeu, même machinerie, même loi d'onsets, tous les pipelines et modes (factor
  et full sur D3).

### 4.2 Cellules secondaires (H = 750)

- Mêmes familles et SR, 1 000 onsets, τ* ∈ [500, T − 750] pour le H_ref de P2-C bootstrap.
- Pipelines : P1-C (deux lectures) ; P2-C (bootstrap, et anytime-valid à γ = 15 000).
- P3-D factor et full sur F1 et F2 : taux d'alarme sous dérive moins taux sous H₀, sur les mêmes réplications.
  L'énergie est paire, donc D6 = brut pour P3-D : résultat descriptif.
- Cellules H₀ : 1 000 réplications par jeu.

### 4.3 J2(i)

Voir le §5.

### 4.4 Bras B — lois d'échelle (convention b, H = 2 000, γ_H = 40 000)

**Référence P1 fixée avant la loi d'échelle**
- 20 chaînes par jeu. La chaîne s est une permutation π_s tirée par `SeedSequence([12, crc32("B|<jeu>"), s])`, avant
  toute injection.
- Le titre de référence P1 est π_s[0]. Il est écrit dans le journal et dans `e1_slopes.csv` avant les cellules.
- Les sous-ensembles emboîtés sont S_s(N) = π_s[:N] ; tous contiennent la référence.
- Grilles : N ∈ {8, 16, 32, 64, 97} pour D2 et {8, 16, 32, 64, 128, 239} pour D3.

**Cellules**

| famille | jeux | amplitude | pipelines |
|---|---|---|---|
| F3 | D2, D3 | SR RMS par titre ∈ {2, 4} (`sr_asset`) | P1 de référence + P2-C |
| F2 | D3 | κ ∈ {1, 2} | P1 de référence + P3-C full + P3-CS (b) full + mélange si la porte de Holm passe sur le sous-ensemble |

- 200 onsets par (chaîne, N, cellule).
- Signes, onsets et coefficients F2 sont communs aux N et aux amplitudes d'une chaîne.
- États et géométrie d'injection sont ajustés par (jeu, sous-ensemble) sur la calib d'origine.

**Grille d'amplitude (`C-e1-amplitude-grid`)** : étape pilote automatique en tête du bras B, sur des clés disjointes
(50 onsets × 5 chaînes × grille de N).
- Règle : le délai médian du pipeline mesuré (P2-C pour F3, P3-C pour F2) reste dans [20 ; 1 600] sur toute la grille
  de N. La médiane n'est définie que si la détection dépasse 50 %.
- Les amplitudes du prompt sont gardées si elles satisfont la règle. Sinon, on retient les deux amplitudes consécutives
  les plus proches qui la satisfont, dans les échelles déclarées {1, 2, 4, 8} (F3) et {0,5, 1, 2, 4} (F2).
- Si aucune ne la satisfait, les amplitudes du prompt sont gardées et les cellules sont marquées hors règle.
- Médianes pilotes et grille retenue sont écrites dans `e1_slopes.csv` et dans le journal.

**Pente**
- MCO de log G_ADD,H(N) = log add_h(P1 réf.) − log add_h(P) sur log N, cellules (s, N) poolées.
- Les cellules où P détecte au plus 50 % sont exclues et signalées.
- IC à 95 % par bootstrap percentile des chaînes (2 000 tirages).
- Sont aussi rapportées les pentes de log add_h(P) et de log add_h(P1 réf.). La référence est dite constante si l'IC de
  sa pente contient 0. La pente retenue reste celle du rapport, estimée directement.
- a_max(N), I_z(N) et K_eff(N) sont rapportés par (N, chaîne).

**Verdicts J2 (Q5)**
- (ii) P2-C sur F3, N ≥ 20 (D2 : 32, 64, 97 ; D3 : 32 → 239), par (jeu, amplitude) : PASS si chacun des quatre IC
  contient 0 ou a une borne haute < 0,15.
- (iii) P3-C sur F2, toute la grille, par κ : PASS si les deux pentes sont > 0 avec un IC excluant 0.
- En cas d'échec de (iii) : attribution (a_max(N), pente de P3-CS (b), pente du mélange) et renvoi à la contingence C1
  (prompt 23, phase 1).

### 4.5 G_SR (mesure secondaire)

- Grille réduite : F3 sur D2 et D3, F2 sur D3.
- Pipelines : P1-C, P2-C, P3-C, P3-CS (b) et P7. Pour P1-C, on retient le titre médian : le SR auquel la médiane des
  taux de détection des 20 titres atteint 1/2.
- Bissection sur log₂ SR dans [0,25 ; 64], en 6 pas de 200 onsets, avec les mêmes réplications à chaque pas.
- SR* > 64 est rapporté censuré. G_SR(A→B) = SR*_A/SR*_B.

### 4.6 Bras C — phases réelles (descriptif)

**Phases.** Phases SPY des trois datations dans la fenêtre stricte (`spy_phases`, `transitions`) : 9, 10 et 9
transitions par jeu.

**Budget**
- Part des transitions avec n₂·SR²_débiaisé/504 ≥ ln γ, γ ∈ {20, 252}, par sous-espace : market, factor, idio,
  residual_full, chars.
- Construction de l'audit : `subspaces` et `projections`, avec les 15 colonnes de caractéristiques sur D3
  (`C-audit-subspaces`), étiquetées rétrospectives.
- Les parts de D2 sont comparées au bit à `budget_share.csv`. L'écart de D3, dû à une ligne, est rapporté.

**Placebo**
- 2 000 rotations (`rotate_phases`) : moyenne, intervalle à 95 % et p = (1 + #{placebo ≥ réel})/(1 + P).
- Les parts réelles sont des **bornes supérieures** : Î est gonflé par la sélection des frontières (`C-audit-placebo`).
- Le placebo teste l'alignement avec les datations choisies. Il **n'identifie pas une fraction causale** de la dérive.

**Alarmes sur données brutes**
- Le moniteur est remis à zéro à chaque frontière et lu jusqu'à la fin de la phase (L = n₂ jours). E-détecteur CUSUM à
  γ_L = L/α (Q6).
- P1-C : flux d'étiquettes Article B sur les 20 titres, q̂ de calib par titre, rendu borné par
  x = (1{r > 0} − q̂)/max(q̂, 1 − q̂).
- P3-C factor : recentrage sur q̂ de calib pour les canaux rejetés (D2 : PC1, PC3 ; D3 : PC1, PC2, PC3) ; signes exacts
  ailleurs.
- Parts d'alarme réelles et placebo ; aucune exactitude revendiquée, aucun IC.

**Gains prévus de l'audit.** `results/audit/predicted_gains.csv` est cité tel quel (SHA-256 dans le journal), NaN
conservés. Il n'est jamais complété ni utilisé pour les prévisions.

## 5. J2(i) — analyse primaire et risque de faux FAIL

**Contrôles.** 54 au total, à H ∈ {750, 2 000} et 2 000 réplications chacun :
- P1-C sur les titres `composition_for(5, N)` : 5 × 2 jeux × 2 H = 20 ;
- canaux factor de P3-C en lecture exacte : (6 + 11) × 2 H = 34.

**Mécanisme**
- P3-C : `pipelines.null_check(specs, X, splits, 2000, key)`. Une symétrisation d'ajustement (`key + [0]`), puis des
  symétrisations neuves par contrôle et par réplication (`key + [2, i, r]`).
- P1-C : même mécanisme, reproduit localement comme dans E3 : `pipelines._null_block` sur la colonne du titre, et
  `pipelines._coins`.

**Règle primaire (prompt).** Un contrôle passe ssi |FPR − ℓ_H| ≤ 0,01. J2(i) passe ssi les 54 contrôles passent.

**Risque de faux FAIL, chiffré avant tout tirage**
- Sous exactitude, un contrôle échoue avec une probabilité de 0,0293 à H = 750 (il passe ssi le nombre d'alarmes est
  dans [68 ; 107] sur 2 000) et de 0,0319 à H = 2 000 (passe ssi [72 ; 111]).
- Les contrôles sont indépendants : chacun a ses clés, donc ses symétrisations et ses pièces.
- On attend donc 1,65 faux FAIL, et **P(J2(i) = FAIL | 54 flux exacts) = 1 − 0,9707²⁷ × 0,9681²⁷ = 0,813**.
- Un FAIL de (i) est ainsi probable sans aucun défaut. À titre de repère, la même règle à 20 000 réplications (lecture
  d'E3 sur les mêmes 54 flux) échoue par hasard avec une probabilité de 1,1·10⁻⁹.

**Diagnostics préenregistrés, sans effet sur le verdict** (dans `e1_null.csv` et le résumé) :
- nombre k d'échecs et P(#FAIL ≥ k | exact), sous la loi de Poisson-binomiale exacte (27 × 0,0293, 27 × 0,0319) ;
- p-valeurs binomiales exactes bilatérales de FPR = ℓ_H, avec Holm au niveau de famille 1 % ;
- appartenance à la région à 99 % (0,54 sortie attendue).

**Préenregistrement**
- Clés `[12, crc32("full|j2i|<jeu>|<H>")]`, fixées dans `configs/e1.yaml` et dans ce plan.
- `--quick` utilise le libellé `quick|` : les tirages primaires ne sont évalués qu'une fois, lors du run complet.
- Aucun rerun, aucun changement de clés ni de nombre de réplications après le résultat.
- Seule exception : un défaut de code constaté après coup, corrigé et consigné (`C-e1-j2i`), avec un nouveau calcul aux
  mêmes clés.

## 6. Mesure du FPR atteint

- **Bras A et H = 750.** Pour chaque lecture, FPR(H) est mesuré sur les cellules H₀ (1 000 réplications par jeu et
  par H), avec un IC de Wilson à 95 % conditionnel au panel. Il est placé à côté de sa cible et de la région à 99 % de
  `pipelines.summarize` (bruit 1/n_cal inclus). Cibles : ≤ α, = ℓ_H, ≈ α ou ≤ 1/γ selon la lecture.
- **Gains.** Chaque ligne de gain porte les FPR atteints de ses deux pipelines. Pour le titre P1-C médian ou oracle,
  c'est le FPR H₀ du même titre, et non la moyenne des 20.
- **E-détecteurs à γ_H.** Leur garantie est une borne, et non un niveau atteint : on attend un FPR bien inférieur à α
  (sondes du stream 07 : 0,0000 à 0,0015 à γ = 15 000).
- **Mélange.** Le FPR est mesuré sur les réplications H₀ pour chaque s² employé.
- **P3-D et bras C.** Fenêtres chevauchantes : taux descriptifs, sans IC binomial.
- **J2(i).** Voir le §5.

## 7. Comparaisons à fausse alarme égale

- **Par défaut, seuil nominal commun.** Les G_ADD,H des lectures anytime-valid sont qualifiés « à seuil nominal commun
  α = 0,05 » (`comparison = common_nominal_alpha`), avec les FPR atteints affichés. Le chevauchement d'IC n'est jamais
  invoqué.
- **« À fausse alarme égale » : seulement G_ADD,ex.** Ce gain compare des lectures exactes au même niveau ℓ_H du
  treillis (même δ, même H, même règle), dont l'égalité vaut exactement en loi sur D6 (Lemme 2). Deux comparaisons :
  - P1-C exacte (titre médian) → canal marché de P3-C en lecture exacte, pour F3 : canal préspécifié, non oracle ;
  - P1-C exacte → meilleur canal exact, pour F1 et F2 : oracle, étiqueté comme tel.
- **Marge d'équivalence, fixée ici avant tout test** : |FPR_A − FPR_B| ≤ 1 point. Si l'IC à 95 % de la différence
  (bootstrap apparié des réplications H₀ communes) tient dans [−0,01 ; 0,01], l'étiquette est `equal_fa_verified` ;
  sinon, `equal_fa_not_shown`.
- **Aucune revendication iso-FPR pour les e-détecteurs** (Q3) : la lecture iso-FPR sur graines disjointes n'est pas
  exécutée.

## 8. Prévisions gaussiennes de conception et limites sur D6

**Informations**
- Oracle : I_x = ½ΔᵀΣ̂⁻¹Δ, avec Σ̂ = Ledoit–Wolf de la calib d'origine, la même que pour les représentations et P7.
  Elle est nommée « information quadratique gaussienne de conception », jamais « KL exacte de D6 ». Pour F2, c'est la
  moyenne réalisée sur [τ*, τ* + H), rapportée avec sa cible de calib.
- Par pipeline, Δz = WᵀΔ dans la base figée :
  - P3-C, en factor ou en full ;
  - P3-CS (b) : canaux résiduels (mêmes signes que P3-C, puisque u_k ⟂ b) ;
  - P2-C : I_EW = (1ᵀΔ)²/(2·1ᵀΣ̂1) ;
  - P1-C, titre i : Δᵢ²/(2Σ̂ᵢᵢ).
- a_max = max_k Δz_k²/‖Δz‖², en moyennes temporelles pour F2.

**Efficacité du signe**
- e_k = 4f̂_k(0)², où f̂_k est la densité à 0 de la coordonnée k sur la calib (noyau gaussien, fenêtre de Silverman).
  e = 2/π sous normalité.
- Pour P2-C : I_sign = 2·K_eff·(moyenne_i f̂_i(0)Δ_i)².

**Délais prévus, par `floors`**
- Flux unique : `first_order_floor(γ_H, e·I)`.
- Dictionnaire : `dictionary_multiplier(K, γ_H, a_max)·first_order_floor(γ_H, e·I_z)`, soit
  (ln γ_H + ln K)/(e·a_max·I_z), la formule du prompt.
- Mélange : `mixture_multiplier(D, γ_H)·first_order_floor(γ_H, e·I_res)`.
- P7 : budget `evidence_budget(γ_H, I_x)` (Lemme 1) et Lorden analytique `phi(γ_H·I_x)/I_x`. Ce sont deux bornes
  analytiques, distinctes d'un délai mesuré.
- P3-CS (b) : intervalle [d̂_res/N1 ; d̂_res], avec N1 = 1,968 (D2) et 1,998 (D3), lus dans `channel_ceilings.csv`.

**Gains prévus.** G_floor = I_B/I_A et g_pred = d̂_A/d̂_B. Ils sont placés à côté des gains mesurés seulement si la
censure est ≤ 5 % dans les deux cellules ; sinon, `not_directly_interpretable`.

**Limites sur D6** (journal, wrapup, `C-e1-predictions`) :
1. D6 garde |x|, les corrélations et le clustering de volatilité : la KL d'une translation dans ce fond n'est pas I_x
   (queues épaisses, N3 ; hétéroscédasticité, N1 et `lw60_net`).
2. Sachant le panel, un jour où |z_t| > |Δz_t| reste une pièce équitable sous dérive : l'information se concentre sur
   les jours de faible |z_t|. e, estimé sur la loi marginale de calib, n'en est que l'approximation de premier ordre.
   Sous volatilité persistante, le délai calendaire dépasse ln γ/Ī d'un terme d'ordre CV²(I_t)·τ_int (sec3, l. 111).
3. La grille de mises est fixe (2η₀ ∈ {0,1 ; … ; 0,4}). La croissance reste sous la KL quand la mise optimale sort de
   la grille ; pour ε < 0,025, la plus petite mise a une dérive négative.
4. Les formules sont de premier ordre (Lai) : elles ignorent le dépassement, le redémarrage du CUSUM et la censure à H.
5. P2-C : les signes poolés ne sont pas le rendement équipondéré, et K_eff est mesuré sur 2005–2019.
6. F2 : l'information réalisée diffère de la cible de calib, à cause de la dérive de C_t.
7. Le mélange suppose des coordonnées indépendantes. Sur D6, sachant le panel, le signe journalier commun couple les
   canaux : la validité n'est qu'approchée.

## 9. P1-C locale : remise à zéro du CUSUM et invariance au préfixe

**Construction**
- La fonction P1-C d'E1 ne reçoit que les lignes surveillées Y = X[τ*:τ* + H, titres] et un générateur indexé par
  (cellule, réplication, rôle « pièces »).
- Bits : b = 1{y > 0}. Les nuls sont tranchés par des pièces tirées sur Y seulement.
- Lecture exacte : `bilateral_delay_vec(b − c, 0,1, seuil)`, avec S₀ = 0.
- Lecture anytime-valid : `log_edetector` sur (b − c)/max(c, 1 − c), avec M₀ = 0.
- c = ½ sur D6, q̂ de calib dans le bras C.
- Aucun état ne franchit τ* ni une frontière de phase.

**Tests** (`tests/test_e1.py`, avant tout run)
1. `test_p1c_cusum_resets_at_onset`
   - Un titre a un préfixe entièrement positif : S⁺ atteindrait 0,4·τ*, bien au-delà de 10,3.
   - L'offset d'E1 égale celui de la fenêtre calculée seule.
   - Le contrefactuel sans remise à zéro (CUSUM lancé à la ligne 0) alarme à l'offset 0 : le test discrimine.
   - Même contrôle pour l'e-détecteur.
2. `test_p1c_prefix_invariance_each_onset`
   - Mini-cellule D6 : 40 réplications, 1 % de rendements nuls, τ* = 0 et τ* = T − H forcés.
   - Pour chaque onset, les lignes avant τ* sont remplacées successivement par des zéros (des nuls), par leur opposé,
     puis par un bruit gaussien. Les lignes après τ* + H sont remplacées aussi.
   - Offsets des deux lectures et pièces des nuls : identiques au bit.
3. `test_phase_monitor_resets_at_each_boundary` (bras C)
   - Toutes les lignes avant une frontière sont perturbées, q̂ restant figé.
   - L'alarme de la phase est inchangée, et l'état vaut zéro à la frontière.

**Registre.** Les pipelines du registre (P2-C, P3-C, P3-CS, P7) repartent à τ* par `pipelines._window`. P2-C bootstrap
lit, par construction (R15), les H_ref = 500 lignes qui précèdent τ*.

## 10. Coûts de run

**Coûts unitaires mesurés** (un fil, 2026-10-23) :
- `transform_panel`, 2 000 jours :
  - ACP factor : 10–11 ms ; full : 15 ms (D2), 27 ms (D3) ;
  - degré 0 factor : 18–20 ms ; full : 21 ms (D2), 32 ms (D3).
- `fit_background` : 2 ms (D2, K = 6), 10 ms (D3, K = 11).
- `inject`, ajustement compris : F1 3 ms (D2), 14 ms (D3) ; F2 (D3, 15 colonnes) 75 ms.
- Symétrisation : < 1 ms. `load_chars_tensor` : 0,3 s.
- E-détecteur CUSUM : 18,7 ns par (trajectoire × mise × pas).
- Dictionnaire : 17,2 ns par (trajectoire × canal × mise × pas).
- CUSUM bilatéral 20 000 × 2 000 : 0,29 s. `stakes` : 0,55 ms pour 2 000 jours.

**Par réplication à H = 2 000** : D2 factor ≈ 30 ms ; D3 factor ≈ 60 ms ; D3 full (F2) ≈ 310 ms, dont ≈ 65 ms pour
chacun des dictionnaires P3-C et P3-CS (b).

| bloc | réplications | CPU estimé |
|---|---|---|
| A : 15 cellules × 1 000 + H₀ 2 × 1 000 | 17 000 | ≈ 0,5 h |
| H = 750 : 15 × 1 000 + H₀ 2 × 1 000 + 2 × 20 000 fenêtres bootstrap | 17 000 | ≈ 0,15 h |
| J2(i) : 54 × 2 000 | 108 000 | < 0,05 h |
| B : 136 000 + pilote (≈ 25 %) | ≈ 170 000 | ≈ 1,6 h, dont ≈ 1,2 h pour F2 full |
| G_SR : 3 cellules × 5 pipelines × 6 pas × 200 | 18 000 évaluations | ≈ 0,3 h |
| C : 2 000 rotations × 6 (jeu, datation) | — | ≈ 0,1 h |
| **Total** | | **≈ 2,7 h ; ≈ 4 h avec une marge × 1,5** |

Temps mural : environ 6 à 10 min à 48 processus, 12 à 20 min à 24.

**Mémoire**
- Paquets de 64 enregistrements, ramenés à 16 pour les dictionnaires full de D3.
- Le plus grand tableau (16 × 2 000 × 952 float64) pèse 0,24 Go. Pic d'environ 1 Go par processus, soit environ 50 Go à
  48 processus, pour 162 Go disponibles.
- La limite du prompt (aucun tableau (J, K, T) au-delà de 2 Go) est respectée.

**Règle des 8 h.** Le temps de `--quick` est mesuré par bloc, puis extrapolé. Aucune réduction n'est attendue. Si la
projection dépassait 8 h, on réduirait dans cet ordre, chaque réduction étant consignée (`C-e1-sizes`) :
1. G_SR (200 → 100) ;
2. bras B (200 → 100) ;
3. bras A (1 000 → 500).

**`--quick`**
- 100 onsets, SR = 4, N ∈ {16, 64}, 4 chaînes, sans pilote.
- Nuls et J2(i) à 200 réplications, avec la mention « quick : pas un verdict J2 ».
- 20 rotations ; G_SR en 2 pas de 50.
- Estimation : moins de 3 min à `--jobs 8`, pour une cible de 10 min.

**Parallélisme**
- Une tâche est une paire (cellule, paquet), sur un pool `spawn`. L'initialiseur charge panels, caractéristiques et
  états une fois par processus.
- Chaque paquet concatène les fenêtres surveillées de ses réplications, comme `null_check`, et appelle `run_pipeline`
  une fois par spécification.
- Les sorties sont réassemblées dans l'ordre canonique : elles ne dépendent ni de `--jobs` ni de la taille des paquets.
- `--jobs` vaut 24 par défaut, la machine étant partagée ; l'orchestrateur peut le fixer.

**Graines.** `SeedSequence([12, crc32(libellé de cellule), r, rôle])`, avec les rôles : 0 symétrisation, 1 onset,
2 direction, 3 pièces P1-C. Les pièces du registre restent celles de `_coins` (`[*seed, 7]`).

## 11. Code partagé (Q2) et fichiers touchés

**(a) `jepadrift/injection.py::inject`** — exigé par le prompt (cache de `fit_background` par jeu, fenêtre et K ;
amplitudes 2 et 4 en convention b). Deux clés optionnelles :
- `params["fit"]` : un résultat de `fit_background` réutilisé.
  - Contrôle de forme : Σ̂ de taille (N, N) ; B à K colonnes pour F1 et F2.
  - Avec cette clé, `X[calib]` n'est plus lu ; F2 lit toujours C sur les lignes de calib.
- `params["sr_asset"]` : amplitude par titre de la convention (b), `SR_ASSET_B` par défaut.
- Sans ces clés, les sorties sont identiques au bit (test).

**(b) `jepadrift/pipelines.py::cross_independence`** — exigé par le prompt ; amende `C-P3C-mixture-gate`.
- p-valeurs bilatérales de √T·ρ̂ par paire, avec Holm au niveau de famille α = 0,01.
- La porte passe ssi aucune paire n'est rejetée, c'est-à-dire ssi min p > α/m.
- `over` compte les rejets ; les clés sont conservées, plus `p_min` et `alpha`.
- Le message de `_cal_p3c` est mis à jour, ainsi que `test_cross_independence_gate`.

**(c) Déplacement verbatim** de `spy_phases`, `char_directions`, `projections` et `subspaces`, avec `N_PC` et
`MAX_DIM`, de l'audit vers `jepadrift/stats/drift.py`. Le bras C en est le second consommateur. Protocole 8b :
- SHA-256 des segments figés dans `tests/test_drift_stats.py` ;
- ré-export par l'audit (`tests/test_audit.py` inchangé) ;
- les 9 CSV de `audit_information.py --quick` identiques avant et après (`cmp`).

`drift.py` gagne l'import d'`articleB`, que lit `spy_phases`.

**Rien d'autre** dans `jepadrift/`. Les aides de délai restent locales (Q8).

| fichier | action |
|---|---|
| `experiments/e1_problem.py` | nouveau. Options `--config`, `--quick`, `--out`, `--fig-dir`, `--log-dir`, `--jobs`, `--arms`, `--include-test-window`. Cette dernière est refusée sans `configs/FROZEN.json` concordant (plafond `# ponytail:` jusqu'au stream 21). Garde bloquante : lignes ∈ [2005-01-04 ; 2019-12-31] |
| `configs/e1.yaml` | nouveau : grilles, tailles, libellés des clés, bloc `quick` |
| `tests/test_e1.py` | nouveau, moins de 40 s (`make check` dure 3 min 16 s aujourd'hui) |
| `jepadrift/injection.py`, `tests/test_injection.py`, `docs/sections/injection.md` | changement (a) |
| `jepadrift/pipelines.py`, `tests/test_pipelines.py`, `docs/sections/pipelines.md` | changement (b) |
| `jepadrift/stats/drift.py`, `experiments/audit_information.py`, `tests/test_drift_stats.py` | changement (c) |
| `results/e1/*.csv`, `results/e1/e1_j2_summary.txt`, `figures/e1/*.{png,pdf}` | sorties suivies. CSV écrits par `save_fair_csv` ; figures tirées des seuls CSV |
| `logs/e1/e1.log` | local et ignoré (`logs/`) |
| `docs/DEVIATIONS.md` | nouvelles entrées `C-e1-*` **en anglais** |
| `prompts/GO-stream-12.md`, `prompts/plans/plan-12.md`, `prompts/wrapups/wrapup-12.md` | GO et plan en français, wrapup en anglais |

## 12. Sorties

- **`e1_cells.csv`** : une ligne par (bras, jeu, N, chaîne, famille, amplitude, H, pipeline, lecture, unité).
  - Délais : `add_h`, `det_rate` et son IC, `censored_share`, `mean_detected`, `median_delay`.
  - FPR : FPR atteint, son IC, sa cible et son type.
  - Information : `info_x`, `info_sub`, `a_max`, `e_sign`, `info_realized`, `c_nan_imputed`.
  - Prévisions : `pred_delay`, `budget_days`, `lorden_add`.
  - Gains : `g_add_h` et son IC, son étiquette de censure, `g_floor`, `g_pred`.
  - Étiquettes : `comparison`, `oracle`, `asset_selection`, `retrospective`, `status`.
- **`e1_slopes.csv`** : pilote, grille retenue, références P1, pentes, IC, cellules exclues, verdicts (ii) et (iii).
- **`e1_null.csv`** : les 54 contrôles de J2(i) avec leurs diagnostics, le FPR par lecture et les portes de Holm.
- **`e1_real_phases.csv`** : parts réelles et placebo du budget et des alarmes, avec l'étiquette
  `alignment_upper_bound_not_causal`.
- **`e1_j2_summary.txt`**
  - En tête, la fenêtre `2005-01-04..2019-12-31` et l'étiquette rétrospective.
  - Une ligne `J2(i): PASS|FAIL` à `J2(iv): PASS|FAIL` par critère, avec les IC.
  - Pour (i), le risque de faux FAIL et les diagnostics ; pour (iv), le tableau 1 → 2 → 3 → 3-CS à SR = 4, mesuré et
    prévu.

Chaque nombre du §2 figure dans un CSV, prévisions et mesures côte à côte.

## 13. Exécution après GO

Méthode : superpowers `test-driven-development` pour chaque changement, `verification-before-completion` avant toute
annonce.

0. **Préparation**
   - HEAD = `c284823` (ou le `main` local désigné par l'orchestrateur), et `test -z "$(git status --porcelain)"`.
   - Contrôle MCP : `graph_stats` et `resolve_repo` doivent répondre ; un échec est signalé avant tout code.
   - Écrire `prompts/GO-stream-12.md` : GO et messages de l'orchestrateur verbatim, ancien GO conservé (Q9).
   - Écrire `prompts/plans/plan-12.md` avec « Décision GO intégrée ».
   - Contrôle : `test "$(git status --porcelain)" = "$(printf ' M prompts/GO-stream-12.md\n?? prompts/plans/plan-12.md')"`.
1. **Changement (c)**
   - `audit_information.py --quick` vers le scratchpad (avant).
   - Tests de segments (rouges), déplacement, ré-export.
   - Second `--quick` (après), puis `cmp` des 9 CSV.
2. **Changements (a) et (b)** : tests rouges, puis code ; `pytest` sur `test_injection`, `test_pipelines`,
   `test_drift_stats` et `test_audit`.
3. **`tests/test_e1.py`** (rouge), puis `e1_problem.py` et `configs/e1.yaml` jusqu'au vert. Les tests couvrent :
   - la garde stricte : une ligne datée du 2005-01-03 ou du 2020-01-02 lève une erreur ; `--include-test-window` est
     refusé ;
   - les trois tests du §9 ;
   - le calcul du risque de J2(i) : 0,0293, 0,0319 et 0,813 ;
   - les résumés de délai : censure, règle de la médiane, étiquettes de G, Wilson ;
   - l'invariance à `--jobs` (1 contre 2) et à la taille des paquets ;
   - la référence P1 fixée avant l'injection et présente dans tous les emboîtements ;
   - avec le fit en cache : F3 exactement dans la colonne 0, et ½‖z_full(Δ)‖² = I_x ;
   - e ≈ 2/π sur données gaussiennes ;
   - le flux recentré borné, égal à 2b − 1 quand q̂ = ½ ;
   - une pente et son IC sur des données de pente connue ;
   - les parts du bras C de D2, égales à `budget_share.csv` sur une datation ;
   - une fumée CLI sur une configuration minuscule, deux exécutions identiques (`cmp`).
4. **Runs `--quick`** : deux runs (`--jobs 8`, puis `--jobs 1` vers le scratchpad), `cmp`, chronométrage par bloc,
   décision des tailles.
5. **Run complet** vers `results/e1`, exécuté une seule fois ; le pilote du bras B s'exécute à l'intérieur. Les
   SHA-256 des sorties vont dans le wrapup.
6. **Finitions**
   - Figures, avec le skill `dataviz` chargé avant le code de tracé.
   - Entrées `C-e1-*` en anglais : `C-e1-window`, `C-e1-titles`, `C-e1-inject-cache`, `C-e1-holm-gate`,
     `C-e1-drift-move`, `C-e1-readings`, `C-e1-amplitude-grid`, `C-e1-j2i`, `C-e1-predictions`,
     `C-e1-local-helpers`, `C-e1-f2-chars`, et `C-e1-sizes` si une réduction est nécessaire.
   - Relecture du résumé J2 ; `rm -r results/e1_quick`.
7. **Clôture**
   - Wrapup en anglais (Context, Validated Results avec SHA-256, Errors and Dead Ends, Current State, Vigilance Points,
     Recommendations).
   - `tools/reindex_graphify_jcodemunch.sh`, puis `make check`.
   - Un seul commit, `feat(e1): measure the detection problem and the J2 criteria (stream 12)`, indexé chemin par
     chemin, sans trailer ni chemin absolu.
   - `test -z "$(git status --porcelain)"`.
   - **Arrêt** : ni fetch, ni fusion, ni push.

Priorité J2 (25 octobre) : J2(i), bras A et bras B d'abord (`--arms` pendant le développement). Le run commité
exécute tous les bras en une seule invocation.

## 14. Vérification (chaque commande échoue sur divergence)

```bash
cd ~/JEPA-stream-12
set -e
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
export PATH="$HOME/miniforge3/pkgs/make-4.4.1-h1114479_4/bin:$HOME/JEPA-stream-12/.venv/bin:$PATH"
S=<scratchpad de la session>
.venv/bin/pytest -q tests/test_e1.py tests/test_injection.py tests/test_pipelines.py tests/test_drift_stats.py tests/test_audit.py
for f in "$S"/audit_before/*.csv; do cmp "$f" "$S/audit_after/$(basename "$f")"; done
.venv/bin/python experiments/e1_problem.py --quick --jobs 8 --out results/e1_quick --fig-dir "$S/fq1" --log-dir "$S/lq1"
.venv/bin/python experiments/e1_problem.py --quick --jobs 1 --out "$S/e1_quick2" --fig-dir "$S/fq2" --log-dir "$S/lq2"
for f in e1_cells.csv e1_slopes.csv e1_real_phases.csv e1_null.csv e1_j2_summary.txt; do cmp "results/e1_quick/$f" "$S/e1_quick2/$f"; done
.venv/bin/python experiments/e1_problem.py --out results/e1
head -1 results/e1/e1_j2_summary.txt | grep -q '2005-01-04..2019-12-31'
test "$(grep -cE '^J2\((i|ii|iii|iv)\): (PASS|FAIL)' results/e1/e1_j2_summary.txt)" -eq 4
rm -r results/e1_quick
make check
# après le commit unique
test -z "$(git status --porcelain)"
```

## 15. Décisions retenues (défauts Q2–Q9) et question ouverte

Défauts retenus, conformément à l'amorçage :
- **Q1** est remplacée par la consigne : 2 000 réplications et règle du prompt (§5).
- **Q2** : changements (a), (b) et (c) (§11).
- **Q3** : « fausse alarme égale » réservée à G_ADD,ex, avec une marge de ±1 point ; tout le reste est « à seuil
  nominal commun » ; pas de lecture iso-FPR.
- **Q4** : P3-CS (a) à γ = 1/α = 20 (Ville).
- **Q5** (bras B) :
  - H = 2 000, pente sur `add_h`, exclusion des cellules où P détecte au plus 50 % ;
  - (ii) sur N ≥ 20 par (jeu, amplitude) ; (iii) sur toute la grille, par κ ; PASS si toutes les cellules passent ;
  - règle de grille appliquée à P2-C (F3) et à P3-C (F2) ;
  - (iv) PASS = tableau complet de 5 (jeu, famille) × 3 étapes, avec IC et prévision ou étiquette, sans juger le signe
    des gains.
- **Q6** : alarmes du bras C à γ_L = L/α par phase.
- **Q7** : mélange avec s² = 2·ē·I_{z,res}/D par cellule (prior de la Prop. 3 ajusté sur l'amplitude injectée),
  étiqueté oracle.
- **Q8** : aides de délai locales, alignées sur E6 et E10 (`restricted`, `delay_stats`, `wilson`, `alarms` : mêmes noms,
  mêmes formules). Leur déplacement commun vers `jepadrift/` attend les fusions de 12, 13 et 23 ; il est consigné
  (`C-e1-local-helpers`) et marqué `# ponytail:`.
- **Q9** : nouveau GO verbatim en tête de `prompts/GO-stream-12.md` ; l'ancien est conservé sous « GO du 2026-10-18 —
  spécification remplacée, non applicable ».

Décisions de révision :
- 20 titres P1-C des bras A et C = `composition_for(20, N)`, la composition R15 figée ;
- titres de J2(i) = `composition_for(5, N)` ;
- référence P1 du bras B = π_s[0] (§4.4).

**Q10 — Caractéristiques de F2 injectée (bras A, B et G_SR)** — non bloquante ; le défaut s'applique sans réponse.
- Défaut : les 4 caractéristiques continues causales (`c_beta_252` tel quel, comme au GO 17 ; `c_vol_63` ;
  `c_mom_12_1` ; `c_rev_21`). Motifs :
  - cohérence avec le protocole principal des streams 14 et 17 et avec D4, qui n'a pas de GICS ;
  - les représentations P4/P5 d'E5 ne verront que ces colonnes ;
  - le GICS statique n'est pas point-in-time (`C-D3-gics-static`).
- Alternative : les 15 colonnes de `load_chars_tensor`, lecture littérale du prompt et de l'audit.
- Dans les deux cas, le bras C garde la construction de l'audit (15 colonnes), étiquetée rétrospective.

## 16. Correspondance avec l'amorçage et le prompt

| critère | section |
|---|---|
| 8b fusionné sur `main` | §0 |
| grille de calcul | §4 |
| coûts de run | §10 |
| mesure du FPR atteint | §6 (et §5) |
| comparaisons à fausse alarme égale | §7 |
| limites des prévisions gaussiennes sur D6 | §8 |
| H = 2 000 rétrospectif ; délai restreint, censure et ADD de Lorden séparés | §2, §4.1 |
| meilleurs titre et canal = oracles | §2, §3 |
| référence P1 fixée avant la loi d'échelle | §4.4 |
| placebo sans fraction causale | §4.6, §12 |
| ancien GO non applicable | État, Q9 |
| borne stricte au 2005-01-04 | §0, §11, §13 (test), §14 |
| cinq titres `composition_for(5, N)` comme dans E3 | §0, §5 |
| remise à zéro du CUSUM et invariance au préfixe de la P1-C locale | §9 |
| J2(i) : 2 000 réplications, ±1 point, risque, aucun rerun | §5 |
| défauts Q2–Q9 | §15 |
| `.venv`, audits en anglais, arrêt avant fetch, fusion ou push | §13, §14 |
| prompt : deux `--quick` identiques | §14 (`cmp`) |
| prompt : résumé J2 rempli, avec IC et verdicts | §12, §14 |
| prompt : chaque nombre du §2 dans un CSV, prévisions et mesures côte à côte | §12 |
| prompt : graines, paquets ≤ 2 Go, `--quick` < 10 min, < 8 h, aucune ligne de 2020 ou après | §10, §11 |

## 17. Hors périmètre et risques

**Hors périmètre**
- Toute ligne datée de 2020 ou après.
- La lecture « randomisation » de P3-CS (a).
- D4, P4 et P5.
- `MAPPING.md` (stream 21).
- La sensibilité GICS de F2 (Q10).

**Risques**
- **J2(i)** peut échouer par hasard, avec une probabilité de 0,81. Le verdict est alors rapporté tel quel, avec le
  risque et les diagnostics du §5.
- **(iii)** peut échouer par construction du dictionnaire : l'information de F2 s'étale sur environ N canaux, si bien
  que max_k I_{z,k} peut ne pas croître avec N. L'attribution doit l'établir.
- **Porte de Holm** : elle échoue déjà sur D2 factor (paire max |ρ̂| = 0,1308, z = 4,01, p ≈ 6·10⁻⁵ < 0,01/10). La
  lecture mélange y est alors absente, et l'échec est rapporté (`gate_failed`).
- **Fusion** : conflits d'ajout dans `docs/DEVIATIONS.md` (13, 14, 17, 18, 23) et dans `pipelines.py` (14, 17, 18).
- **`.venv` partagé** : un `.pth` torch posé par le stream 14 activerait les gardes torch de `make check`. Celui-ci est
  relancé juste avant le commit, et son résultat est rapporté.
- **Machine partagée** : le temps mural peut doubler ou tripler.
