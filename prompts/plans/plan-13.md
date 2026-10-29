# Plan — stream 13 (E3) : calibration sous H₀ — révision 4 (GO reçu le 2026-10-28)

**Statut.** GO final reçu le 2026-10-28 pour la révision 4, avec corrections obligatoires (section « Décision GO
intégrée (2026-10-28, révision 4) » en fin de plan). Le GO du 2026-10-23 sur la révision 3 est un historique remplacé.
La section **R4** prévaut sur les sections 0 à 15 en cas de conflit. Le GO d'archivage du 2026-10-29
(`prompts/GO-stream-13-archive.md`) lève la seule clause d'arrêt avant commit sur le FAIL de D8 (dernière section du
plan).
Séquence après le GO :
1. rechargement et appel de contrôle de `graphify` et de `jcodemunch` avant la première écriture ;
2. transcription verbatim du GO dans `prompts/GO-stream-13.md`, l'ancien GO conservé comme historique ;
3. enregistrement de ce plan (révision 4) avec « Décision GO intégrée » ;
4. exécution TDD (rouge avant corrections) jusqu'au commit local vérifié, puis arrêt avant fetch, rebase, fusion ou
   push.

## Contexte

E3 mesure la calibration de chaque moniteur sous son hypothèse nulle, sans aucune dérive :
- niveau exact du treillis pour les flux de signe ;
- ARL₀ ≥ γ pour les e-détecteurs ;
- FPR(H) ≈ α pour les seuils bootstrap ou randomisés.

Il chiffre aussi le coût de l'hétéroscédasticité (Γ) et de l'asymétrie des données brutes, et fournit le §5.2 et le
critère (i) de J2 (`prompts/streams/prompt-13-e3.md`). La révision 2 a intégré les corrections de l'orchestrateur du
2026-10-23 (`prompts/amorcage-13.md` et messages de revue) au plan du 2026-10-22
(`~/.claude/plans/amor-age-stream-merry-starlight.md`, base `c8fe24d`), sur la base `c284823`. La révision 3 intègre
le NO-GO statistique provisoire du 2026-10-23 : classement d'ARL₀ sous censure (D9) et dépendance entre cellules
(D10). Les autres arbitrages sont inchangés.

## R4. Révision 4 (2026-10-28) : audit des fichiers partiels et corrections du GO

### R4.1 État vérifié (2026-10-28)
- `stream-13` = `c284823`. `main` = `3f8750d` (gitignore, handover, decks) ; le diff `c284823..main` est vide sous
  `jepadrift/`, `experiments/`, `tests/`, `configs/`, `Makefile`, `conftest.py` et `requirements.txt`.
- Cinq fichiers non commités, conservés : ce plan, `prompts/GO-stream-13.md`, `jepadrift/stats/intervals.py`,
  `experiments/e10_robustness.py` (déplacement de `wilson`) et `experiments/e3_calibration.py` (1 092 lignes, écrit le
  2026-10-23 avant les tests). Absents : tests, configuration, sorties et entrées `C-e3-*`.
- `composition_for(5, 97)` = [24, 71, 56, 46, 75] et `composition_for(5, 239)` = [60, 177, 141, 116, 184], comme dans
  le plan 12 révision 2.
- MCP rechargés après le redémarrage et vérifiés par appel : graphify (`graph_stats`) et jcodemunch (`resolve_repo`).

### R4.2 Audit du code partiel (lecture du 2026-10-28)
- Borne : `check_window` est correcte, mais `load_rows` masquait le 2005-01-03 de D3 avant le contrôle, sans trace.
- Remise à zéro : conforme à la lecture pour P1-C (D5, D6, brut), P1-D (D5, réel), P3-D, dépassement et encodeurs ;
  aucun test.
- Séparation FPR(H) / ARL₀ / Γ : fichiers distincts ; l'e-processus P3-CS (a) à γ = 20 (Ville, ≤ 1/γ) est une lecture
  FPR(H), distincte du γ = 20 d'ARL₀.
- IC : `e3_overshoot` et `e3_window_encoders` n'avaient ni `deff` ni `n_eff`. P1-D D5 calculait λ_iid et λ_req sur
  les trajectoires mêmes dont il donnait le FPR avec Wilson.
- `fpr_threshold` remplace la bissection de `required_threshold` par un tri des pics : égalité à tester.
- `j2_lines` écrivait un verdict J2 propre.

### R4.3 Corrections obligatoires du GO
1. **Q-J2.** Le verdict primaire J2 (i) est celui d'E1 (stream 12) à 2 000 réplications. `e3_j2_check.txt` est un
   contrôle secondaire de calibration à 20 000 trajectoires : écart au niveau, règle à 1 point et région à 99 % par
   cellule, sans ligne de verdict. Les comptes multi-cellules sont descriptifs ; aucune probabilité conjointe sous
   indépendance. L'espérance par linéarité et la borne de l'union, valides sous toute dépendance, sont étiquetées comme
   telles.
2. **P1-D D5.** Deux jeux de 20 000 trajectoires par fond, de rôles distincts dans la clé `SeedSequence`
   (`d5|<fond>|cal` et `d5|<fond>|eval`). λ_req et λ_iid viennent de la calibration. Le FPR et son Wilson (deff = 1)
   sont mesurés sur l'évaluation aux règles λ_req, λ_iid·Γ̂_r, λ_iid et 65·Γ̂_r, avec les colonnes `n_cal` et
   `n_eval` et la validité `out_of_sample`. P1-C D5 est lu sur l'évaluation. Le coût CPU par bloc est consigné dans
   `run.log`. Toute ligne dont le seuil vient de son propre échantillon (P1-D réel, P3-D, placebos bruts) garde
   `ci_kind = na` et une validité descriptive, hors de toute porte.
3. **Borne stricte.** `EXCLUDED_DAYS` déclare les lignes antérieures au 2005-01-04 (D2 : aucune ; D3 : 2005-01-03).
   `load_rows` les compte, lève `ValueError` si elles diffèrent de la déclaration ou si une ligne dépasse le
   2019-12-31, puis applique `check_window`. Le compte figure dans `run.log`.
4. **Indices** figés en littéraux dans `tests/test_e3.py`, avec les noms des titres.
5. **deff.** `deff` = 1 et `n_eff` = n sur `e3_overshoot` et `e3_window_encoders` ; `n_cal` sur les encodeurs (λ_iid
   tiré de trajectoires i.i.d. indépendantes).
6. **P2-C bootstrap (D6)** : validité `calibrated_conditional` (seuil de la symétrisation d'ajustement, évaluation sur
   des symétrisations neuves du même panel) ; hors porte.
7. **Portes de reproduction.** Si la porte primaire du dépassement (D8) donne FAIL, ou si le contrôle σ borné certifie
   une violation, l'exécution s'arrête avant le commit et l'échec est rapporté, sans réglage ni rerun.

### R4.4 Tests (`tests/test_e3.py`, rouges avant les corrections)
Borne stricte et exclusion comptée ; indices littéraux ; remise à zéro (production contre `strict_cusum` et
`bilateral_delay` scalaires sur la fenêtre seule, invariance au préfixe, non-vacuité) pour P1-C, P1-D, dépassement et
encodeurs ; Brook–Evans et 213,09 ; `fpr_threshold` contre `required_threshold` ; `wilson` aux bornes ; classement
D9 ; contrôle σ borné sur pièces ; trajectoire D6 circulaire ; absence d'injection ; rôles calibration/évaluation de
P1-D D5 ; tailles de la configuration ; une fumée de la CLI sur une configuration minimale à `--jobs 1` et `--jobs 2`
(octets identiques), qui vérifie aussi la séparation FPR(H) / ARL₀ / Γ, les colonnes `deff`, les placebos
descriptifs et l'absence de verdict J2.

### R4.5 Vérification et coût
- Q-A : identité AST de `wilson` avec `c284823:experiments/e10_robustness.py`, puis `pytest tests/test_e10.py` (le
  SHA-256 « avant » de la session interrompue n'est pas traçable).
- Le reste du §13 est inchangé : deux `--quick` comparés par `cmp`, un seul run complet, `make check`, état Git exact.
- Le bloc P1 de D5 double (calibration et évaluation) : +0,6 h CPU, soit environ +2 min murales à `--jobs 24`.

## 0. État vérifié (lecture seule, 2026-10-23)

- **8b est fusionné.** `24be667` et le merge `33d847d` sont ancêtres de `main` et de `stream-13`, et la pointe
  `stream-08b` est ancêtre de `main`. `stream-13` = `main` = `c284823` (stream 27 fusionné). `origin/main` vaut
  `ef63362` au dernier fetch local, et aucun fetch n'a été fait : `main` a 11 commits locaux d'avance.
- `prompt-13-e3.md` est inchangé depuis `c8fe24d`. `amorcage-13.md` est identique dans le dépôt principal et dans le
  worktree. Depuis `c8fe24d`, `jepadrift/` n'a pas changé : seuls E10 (script, tests, `configs/e10.yaml`, `C-e10-*`)
  et des prompts sont arrivés.
- **Stream 12** : worktree propre à `c284823`, sans porte de Holm. Le mélange reste donc différé.
- **Session** sous `.venv` (`VIRTUAL_ENV` = `~/JEPA-Drift-experiments/.venv` ; `python` et `pytest` viennent de
  `.venv`). 48 cœurs, charge 0,3 et 161 Go disponibles au moment de la sonde.
- **MCP** : après `/mcp reconnect all` (2 serveurs sur 3), Graphify (`graph_stats`, 3 317 nœuds) et jCodeMunch
  (`resolve_repo`) répondent. L'index jCodeMunch (2026-10-23 00:18) ne contient pas les symboles d'E10, qui ont été lus
  directement. Le serveur non reconnecté n'est pas utilisé par ce stream.

## 1. Décisions intégrées (revue du 2026-10-23)

- **D1 — Borne réelle stricte.** Toute ligne réelle vérifie 2005-01-04 ≤ date ≤ 2019-12-31. `check_window(days)` lève
  `ValueError` avant tout ajustement (contrôle bloquant). D3 perd le 2005-01-03 ; D2 commence déjà au 2005-01-04.
- **D2 — Cinq titres.** P1-C (D6 et brut) et P1-D (réel) portent sur `pl.composition_for(5, N)`, les titres du
  J2 (i) d'E1 :
  - D2 : indices [24, 71, 56, 46, 75] = COST, SHW, SO, MDLZ, PSA ;
  - D3 : indices [60, 177, 141, 116, 184] = CASY, KEY, GPC, ERIE, LRCX.

  Le « tous les titres » de la v1 (brut, P1-D réel) est retiré.
- **D3 — Remise à zéro par fenêtre, sans dérive ni onset dans le préfixe.** Chaque lecture locale repart de S₀ = 0 au
  début de sa fenêtre ou trajectoire : P1-C (exacte, étiquettes), P1-D, dépassement, encodeurs. E3 est entièrement
  sous H₀ : aucune fonction d'injection n'est importée (seule `symmetrize`), et chaque enregistrement porte
  `family = "H0"`. Les lignes de préfixe sont toutes nulles : jours propres de D5, calib (q̂, μ, σ, Γ̂), H_ref de P2-C,
  L − 1 jours des encodeurs. Tests au §8.
- **D4 — Fenêtrage D6.**
  - Les fenêtres chevauchantes des flux pairs (P1-D, P3-D) et des placebos bruts sont descriptives : ni IC binomial ni
    SEM.
  - La trajectoire d'ARL₀ sur D6 est circulaire et continue à la couture : les lignes (s + t) mod n reçoivent des signes
    neufs chaque jour, et ni l'état de l'e-détecteur ni l'EWMA de P3-CS (b) ne repartent au passage de n − 1 à 0.
- **D5 — Q1 retenu.** Portée D5 : P1 univarié (exact, étiquettes, P1-D), dépassement et encodeurs. Pas de panel D5
  multi-titres ; `sim.py` est inchangé.
- **D6 — Q3 retenu.** P3-C, P3-D et P3-CS en mode `factor` seulement.
- **D7 — Q4 retenu.** E3 est livré sans la cellule mélange. Le complément viendra une fois la porte de Holm du stream 12
  sur `main` (commit séparé dans ce stream, ou 13b) : réutilisation de la porte sans duplication, FPR étiqueté
  « validité approchée ». Un non-rejet ne démontre pas l'indépendance.
- **D8 — Q5 retenu.** La porte primaire du dépassement est |ARL₀_MC/réf − 1| ≤ 5 % sur 2 000 trajectoires, avec des
  graines fixées dans la configuration avant tout run. Un seul run complet ; un échec est consigné et attribué, sans
  nouveau tirage ni rerun opportuniste. Le diagnostic à 20 000 trajectoires et les valeurs i.i.d. exactes ne sont pas
  bloquants.
- **D9 — Classement d'ARL₀ (NO-GO statistique du 2026-10-23).**
  - PASS si la borne inférieure à 99 % de la moyenne restreinte atteint γ.
  - INDÉTERMINÉ sinon, en particulier dès qu'une trajectoire est censurée.
  - Aucun FAIL d'ARL sans borne valide sur la queue.
  - Le déficit de moyenne restreinte est rapporté à part (§5).
- **D10 — Dépendance entre cellules (même revue).** Les cellules partagent trajectoires et tirages. Leurs comptes
  (sorties de région, échecs) restent descriptifs, sans p-valeur binomiale. Une probabilité conjointe n'est bornée que
  par l'union (§3, §6, §9, §15).

## 2. Vérifications demandées par l'amorçage

| Point | Constat | Source |
|---|---|---|
| Γ^spec de Bartlett | 1 + 2Σ_{k≤L}(1 − k/(L+1))ρ̂_k. ACF biaisée (moyenne retirée, Σ produits / Σ carrés). L = ⌊4(n/100)^{2/9}⌋ : 6 (n = 750 ou 941), 7 (n = 2 000), 8 (n = 3 774). Conforme au prompt. | `monitors/gamma.py:7` |
| Gaussien distinct de t₇ | `sim.Garch` : t₇ seul (`standard_t`) et signe journalier tiré dans `draw` ; chemin figé par le hash d'E2 (`C-e2-sim`). `garch_panel(nu=None)` est gaussien ; son t₇ (χ² commun) est une autre construction. E3 : t₇ = `Garch(rng, 1, 1, 0.08, 0.90)` par réplication, gaussien = `garch_panel(2941, 1, 0.08, 0.90, None, rng)` par réplication. Clés distinctes, bras non couplés ; chemin t₇ conservé au bit (D5). | `sim.py:19,48` |
| Flux P1-D de l'Article B | Fenêtre 2018-01-02..2019-12-31 (R01 l.260). μ_f = mean(r²) et σ_f = `np.std(r²)`, ddof 0 (l.263–264) ; q̂ = mean(r > 0) (l.265). Γ̂ = `compute_gamma_exact(a, b)` sur `fit_garch_qmle(r − r̄)` (l.271–273). Flux (r² − μ_f)/σ_f, CUSUM unilatéral strict, δ = 0,5, seuil 65·Γ̂ (l.298–299). `energy_stream` est identique. λ_iid = 65 est un point de fonctionnement fixe (v87 l.321), non calibré à (H, α) ; v87 l.449 mesure 129,5 à l'horizon long. E3 calibre donc λ_iid(H, α), sans substitut (z² − 1)/√2. | R01 `a05f0d9`, v87 |
| Fenêtres brutes chevauchantes | P1-D et P3-D sont pairs, donc D6 ≡ brut. Leurs fenêtres et les placebos bruts viennent d'une seule trajectoire : descriptifs (D4), avec n_fenêtres et n_disjointes. | `pipelines.null_check` |
| Arithmétique du prompt | H_ref + H = 500 + 750 = 1 250, et non 1 500. La conclusion tient (> 941) : `null_rows="pre_monitor"`. | R15, `H_REF` |
| CUSUM de signe de l'item 5 | δ = 0,1, unilatéral, L = 16 unités (λ = 3,2, seuil milieu 3,3) : ARL₀ exact 213,09 ; L = 15 donnerait 173,2. | `lattice.arl0` |
| Références de dépassement | Valeurs Monte Carlo du plan v1, graines inconnues. ARL₀ i.i.d. exacts (Brook–Evans, sonde du 2026-10-22, retestée en exécution) : 2 553,1 (δ = 0,5, λ = 6) et 1 962,8 (δ = 1, λ = 3), contre 2 587 (+1,3 %) et 1 894 (−3,5 %). | `Plan_Claude_Opus_v1.md:163` |

**Cibles exactes** (bilatéral, δ = 0,1, règle stricte, `select_threshold(0.05, H=H)`) :

| H | L | λ | `threshold` | niveau exact | région à 99 % (n = 20 000) | 1 point |
|---|---|---|---|---|---|---|
| 750 | 45 | 9,0 | 9,1 | 0,0439467 | [0,04021 ; 0,04768] | 6,90 ET |
| 2 000 | 51 | 10,2 | 10,3 | 0,0456695 | [0,04187 ; 0,04947] | 6,77 ET |

**Lignes réelles (D1).** `d2_us97` et `d3_239` ont 3 774 lignes chacun : pretrain [0, 2 768), calib [2 833, 3 774)
(941 jours). Pour D3, l'audit gardait le 2005-01-03 (une ligne de plus). K vaut 5 et 10, soit 6 et 11 canaux P3-C.
Rendements nuls des cinq titres : 0,89 % et 0,91 % (tranchés par pièce dans le flux exact). Rejets de symétrie de
l'audit : D2 PC1 et PC3 ; D3 PC1, PC2 et PC3 ; `char:rev_21` n'est pas un canal P3-C.

## 3. Garanties (A), diagnostics (B) et mesures (C)

| Bloc | Fond | Mécanisme | Statut | IC | Fichier |
|---|---|---|---|---|---|
| A1 | D5 GARCH(0,08 ; 0,90), t₇ et gaussien | réplications indépendantes | niveau exact du signe exact (Lemme 2) ; λ_req et Γ^op de P1-D | Wilson 95 % (deff = 1) et région à 99 % | `e3_cells` |
| A2 | D6 SYM-`d2_us97`, SYM-`d3_239` | panel fixé, symétrisation neuve par réplication | flux **impairs** seulement : niveau exact (P1-C, canaux P3-C) ; e-détecteurs ≤ H/γ_H = α ; P3-CS (a) ≤ 1/γ ; randomisation ≈ α | Wilson conditionnel au panel et région à 99 % (1/n_cal inclus) | `e3_cells` |
| A3 | pièces équitables | réplications indépendantes | ARL₀ ≥ γ : CUSUM, E∞τ ≥ E∞M_τ ≥ γ ; SR, marge mince (E∞τ = E∞M_τ) | moyenne restreinte ± ET (deff = 1), borne inférieure à 99 % | `e3_arl0` |
| A4 | D6 circulaire (D4) | départs uniformes, signes neufs chaque jour | ARL₀ ≥ γ conditionnellement au panel | idem, conditionnel | `e3_arl0` |
| B1 | brut `d2_us97`, `d3_239` | toutes les fenêtres d'une trajectoire | aucune exactitude ; écart au niveau, attribué canal par canal | aucun (n_fenêtres, n_disjointes) | `e3_raw_placebo` |
| B2 | réel pair (P1-D sur les cinq titres, P3-D) | D6 ≡ brut, fenêtres énumérées | Γ̂, Γ^spec, Γ^op, non-stationnarité | aucun | `e3_cells` (`validity = descriptive`) |
| B3 | P2-C bootstrap sur D6 | seuil tiré de 20 000 maxima d'une symétrisation (2 525 départs, 3 fenêtres disjointes de 1 250 jours) | ≈ α dans l'échantillon ; 1/n_cal sous-estime le bruit de calibration | Wilson conditionnel, signalé | `e3_cells` |
| B4 | ARL₀ brut | chaque départ, censure en fin de données | moyenne restreinte = borne inférieure | aucun | `e3_arl0` |
| C | dépassement (D5), encodeurs (D5, D6) | réplications indépendantes | mesures Monte Carlo, pas des garanties | ET ou Wilson (deff = 1) | `e3_overshoot`, `e3_window_encoders` |

Les SEM ne portent que sur des réplications indépendantes, avec les colonnes `deff` = 1 et `n_eff` = n. Aucune SEM
n'est calculée sur des fenêtres chevauchantes : `deff_rate_ci` d'E10 n'est pas repris.

**Dépendance entre cellules (D10).** Les IC et les régions sont marginaux, cellule par cellule. Les cellules partagent
des tirages :
- la symétrisation d'ajustement et le panel d'un groupe `null_check` ;
- les réplications P1-C, communes aux cinq titres et aux deux bras ;
- en D5, les trajectoires H = 2 000, dont H = 750 lit le préfixe ;
- les trajectoires d'ARL₀, communes aux trois γ et aux deux types ;
- les trajectoires du dépassement, communes à ses trois statistiques ;
- les tirages des encodeurs, communs aux valeurs de L.

Aucune statistique conjointe ne suppose donc l'indépendance. Un compte sur plusieurs cellules reste descriptif, sans
loi binomiale ni p-valeur. Une probabilité conjointe n'est encadrée que par max_i p_i ≤ P(au moins un) ≤ Σ_i p_i
(borne de l'union).

## 4. Calibration et cellules FPR(H), H ∈ {750, 2 000}, α = 0,05

### 4.1 Lignes, unités, K

- `load_rows(name)` : lignes `pre_monitor`, masque D1, `check_window`, contrôle de finitude, puis `split_rows` sur les
  jours tronqués.
- Les ajustements sur D6 fixent K à la valeur MP brute (5, 10), comme E10 (`C-e10-backgrounds`) : une symétrisation
  change le centrage, et une valeur propre proche du bord changerait n₊.
- Les ajustements bruts gardent `K="mp"` (= 5, 10). La base est alors celle de l'audit et d'E10 : son empreinte est
  consignée et comparée à `85147fd9…` et `6c44d64a…`.

### 4.2 D6, lectures du registre (`null_check`)

Un appel `null_check(specs, X, splits, 20000, [13, crc32(f"d6|{jeu}|H{H}")])` par (jeu, H) :
- une seule symétrisation d'ajustement par groupe ;
- la réplication r de la spécification i est tirée sous la clé [13, crc, 2, i, r], ses pièces sous [.., 7] ;
- cibles et régions viennent de `null_target` et `summarize`, les IC de Wilson des lignes d'alarmes.

| Lecture | Seuil (calibration) | Cible | H |
|---|---|---|---|
| P3-C exacte, canal k (6 / 11) | treillis, `threshold` = 9,1 / 10,3 | niveau exact (=) | 750, 2 000 |
| P3-C dictionnaire | γ_H = H/α (15 000 / 40 000) | ≤ α | 750, 2 000 |
| P2-C bootstrap R15 | quantile de 20 000 maxima, `null_rows="pre_monitor"` explicite | ≈ α, n_cal = 20 000 (B3) | 750 |
| P2-C anytime-valid | 2·moyenne des signes bruts exacts, K = N, γ_H | ≤ α | 750, 2 000 |
| P3-CS (a) e-processus | mises ±{0,1 ; 0,25 ; 0,5 ; 0,9}, γ = 20 (Ville) | ≤ 1/γ | 750, 2 000 |
| P3-CS (a) randomisation | B = 2 000 inversions | ≈ α, n_cal = B | 750, 2 000 |
| P3-CS (b) | mises prévisibles, EWMA de ‖Px‖, γ_H | ≤ α | 750, 2 000 |
| P3-C mélange | différé (D7) | — | — |

Au total, 23 spécifications sur D2 et 33 sur D3, soit 56 × 20 000 réplications.

### 4.3 P1-C sur D6 (boucle locale)

Le registre n'a pas de P1-C : le mécanisme de `null_check` est reproduit sans ses fonctions privées, car
`pipelines.py` est modifié en parallèle par les streams 12, 14, 17 et 18.
- q̂_i = mean(1{X_fit[calib, i] > 0}) sur une symétrisation d'ajustement, selon la règle zéro = négatif de l'Article B.
- Réplication r : départ s ~ U[0, n − H] et H signes ε tirés sous [13, crc, r] ; Y = ε·X[s:s+H, titres].
- Bras exact : `exact_sign_stream(Y, pièces [13, crc, r, 7])` → `bilateral_delay_vec(·, 0.1, threshold)` ; cible =
  niveau exact.
- Bras étiquettes : `label_stream(Y, q̂)`, même CUSUM et même seuil ; le niveau sert de référence, sans exactitude.
- 2 jeux × 2 H, 20 000 réplications par cellule, communes aux cinq titres et aux deux bras.

### 4.4 D5, P1 (D5 = Q1)

Par fond (t₇, gaussien) : 20 000 trajectoires indépendantes de 941 jours propres suivis de 2 000 jours surveillés ;
H = 750 lit les 750 premiers.
- P1-C exact et étiquettes comme au §4.3, avec q̂ calculé sur les jours propres.
- P1-D :
  - μ, σ = mean et `np.std` de r² sur les jours propres ; e = `energy_stream(r_surv, μ, σ)` ;
  - Γ̂_r = `compute_gamma_exact(a, b)` sur `fit_garch_qmle(propre − moyenne)`, avec la part des fits non convergés ;
  - Γ exact = 21,52 (formule de R01 à (0,08 ; 0,90)) ;
  - λ_req(H) = `required_threshold(e, 0.5, α, "fpr", H)` sur les 20 000 trajectoires ;
  - λ_iid(H) : même calcul après permutation globale des valeurs surveillées (même marginale, sans dépendance sérielle) ;
  - Γ^op = λ_req/λ_iid ; Γ^spec = médiane et quartiles sur les trajectoires surveillées ;
  - FPR aux règles λ_iid·Γ̂_r, λ_iid seul et 65·Γ̂_r (annexe), chacune avec Wilson.
- Cibles : P1-C exact = niveau (A1) ; P1-C étiquettes = niveau en référence (~) ; P1-D = α (~).

### 4.5 Réel pair (B2, descriptif)

- **P1-D, cinq titres.**
  - μ, σ et Γ̂ sur la calib ; e sur les 3 774 lignes ;
  - λ_req sur toutes les fenêtres, dans l'échantillon ;
  - λ_iid sur 20 000 trajectoires bootstrap i.i.d. des énergies standardisées ;
  - Γ^op, Γ^spec (médiane sur les fenêtres) et Γ̂ ;
  - FPR sur fenêtres à λ_iid·Γ̂, à λ_iid et à 65·Γ̂ ;
  - 3 025 / 1 775 fenêtres, dont 5 / 1 disjointes.
- **P3-D (factor).**
  - `fit_pipeline` P3-D sur les lignes brutes pour (H, `null_rows`) ∈ {(750, calib), (750, pre_monitor),
    (2 000, pre_monitor)} : λ_req, λ_iid χ² du registre, Γ^op et Γ^spec ;
  - FPR de chaque λ sur toutes les fenêtres `pre_monitor` de longueur H (application croisée) ;
  - moyenne de q sur le pretrain et sur la calib, pour la non-stationnarité.
  - Référence : `C-P3D-windows` donne Γ^op ≈ 191 en factor sur les fenêtres 2005–2019 (H = 500). Le 2 346 cité par le
    prompt vaut pour le mode full, hors portée (D6).

### 4.6 Placebo brut (B1)

Toutes les fenêtres de H jours des 3 774 lignes strictes : 3 025 / 1 775, dont 5 / 1 disjointes. 31 % / 53 % d'entre
elles recoupent la calib et sont donc dans l'échantillon pour la base et pour q̂ (consigné).
- **P3-C, chaque canal**, base de calib brute : bras exact (pièces) et bras recentré `label_stream(z, q̂_k)`, avec q̂_k
  de la calib brute ; CUSUM au treillis.
- **P1-C, cinq titres** : mêmes deux bras.
- **Lectures du registre** : `fit_pipeline` brut, puis `run_pipeline` sur toutes les fenêtres (entrée Z pour les
  pipelines à représentation). P3-C dictionnaire, P2-C (bootstrap calibré sur les fenêtres brutes, anytime-valid),
  P3-CS (a) e-processus et randomisation, P3-CS (b).
- **Colonnes** : taux, cible, écart, q̂ de calib, taux moyen des bits sur `pre_monitor`, part de zéros.
- **Jointure** avec `results/audit/symmetry_tests.csv` par (jeu, direction = PC{k+1}) : p binomial et triples (Holm)
  et rejets. Inflation attendue sur D2 PC1 et PC3, D3 PC1, PC2 et PC3. Les titres n'ont pas de test d'audit (NA) ;
  leurs taux propres sont rapportés.

## 5. ARL₀ des e-détecteurs (`e3_arl0.csv`)

- **Détecteurs** : types SR et CUSUM (`log_edetector` / `log_dictionary_edetector`, `kind ∈ {sr, cusum}`) sur les flux
  du registre (`PIPELINES[p][1]`). P2-C avec la grille η₀ par défaut, P3-C en dictionnaire, P3-CS (b) avec
  η₀ = 0,25.
- **Horizons** : γ ∈ {20, 100, 252}, T_max = 60γ (1 200 ; 6 000 ; 15 120).
  - Une trajectoire de 15 120 pas par réplication est lue aux trois γ (nombres aléatoires communs).
  - Durée = premier indice où log M ≥ log γ, plus 1 ; elle est censurée au-delà de 60γ.
- **Fonds** :
  - **pièces** (20 000) : une pièce ±1 par colonne surveillée ; pour P3-CS (b), mises constantes 2η₀_j ∈ {0,1 ; … ;
    0,4}, soit σ̂ = σ̄ ;
  - **D6 circulaire** (20 000, D4) : départ s uniforme sur [0, n), lignes (s + t) mod n, signe de Rademacher neuf
    chaque jour. La trajectoire déroulée est passée comme un seul enregistrement au constructeur de flux du registre :
    l'e-détecteur et l'EWMA continuent à la couture. La base est ajustée sur une symétrisation, comme dans
    `null_check` ;
  - **brut** : chaque départ s ∈ [0, n), longueur n − s, censure en fin de données. Une alarme dans le rembourrage est
    ignorée (le SR croît de +1 par pas sur x = 0).
- **Rapportés** :
  - n ;
  - moyenne restreinte μ_R = moyenne de min(T, 60γ), borne inférieure d'ARL₀ ;
  - ET et deff = 1 (pièces, D6), lb99 = μ_R − 2,326·ET ;
  - part censurée, médiane si la censure est < 50 %, μ_R/γ.
- **Classement d'ARL₀ (D9)** sur pièces et D6 :
  - PASS si lb99 ≥ γ. La règle vaut avec ou sans censure, puisque μ_R = E[min(T, 60γ)] ≤ E∞[T].
  - INDÉTERMINÉ dans tous les autres cas, en particulier dès qu'une trajectoire est censurée.
  - Jamais FAIL. Une borne supérieure de μ_R sous γ ne prouve pas E∞[T] < γ, car la queue E[(T − 60γ)₊] n'est pas
    observée. Même sans censure observée, une masse au-delà de 60γ n'est pas exclue, et E3 n'a pas de borne valide sur
    cette queue.
  - Le déficit de moyenne restreinte, γ − μ_R avec son IC à 99 %, est rapporté dans des colonnes séparées, comme
    grandeur descriptive.

  Le brut reste descriptif, sans classement.
- **Contrôle sans hypothèse de queue (H14, ajout proposé).**
  - Au temps d'arrêt borné σ = min(T, 60γ), la définition de l'e-détecteur donne E∞[M_σ] ≤ E∞[σ] (égalité pour le
    type SR).
  - M_σ ≤ 1,5·(1 + γ), y compris pour les moyennes sur mises et sur directions, et σ ≤ 60γ : l'IC à 99 % de la
    moyenne de M_σ − σ est valide (réplications indépendantes, deff = 1).
  - Une borne inférieure > 0 certifie une violation de l'inégalité qui fonde ARL₀ ≥ γ. C'est le seul échec qu'E3 peut
    établir sans borne de queue ; il est consigné tel quel. Sur pièces et D6 seulement, conditionnellement au panel
    pour D6.
- La marge SR est mince par construction (+9,3 % / +10,9 % aux graines du stream 04, environ 13 ET à 20 000
  trajectoires). Un classement INDÉTERMINÉ est consigné, jamais corrigé par de nouvelles graines.

## 6. Pénalité de dépassement (`e3_overshoot.csv`)

- **Statistiques** :
  - CUSUM de premier ordre unilatéral strict sur x/σ_inc (σ_inc = 1), (δ, λ) ∈ {(0,5 ; 6), (1 ; 3)} ;
  - CUSUM de signe unilatéral, δ = 0,1, λ = 3,2 (seuil 3,3).
- **Fonds** : i.i.d. N(0, 1) et GARCH(0,08 ; 0,90) gaussien (`garch_panel(nu=None)`). Une trajectoire sert aux trois
  statistiques d'une réplication. T_max = 40 000 (i.i.d.) et 30 000 (GARCH), censure rapportée.
- **Porte primaire (D8)** : réplications r = 0..1 999 de chaque cellule, |ARL₀_MC/réf − 1| ≤ 5 %, avec réf. ∈
  {2 587, 889, 1 894, 669, 213, 214}. Les graines figurent dans `configs/e3.yaml` avant tout run ; aucun rerun.
- **Diagnostics pré-enregistrés, non bloquants** :
  - r = 0..19 999 (sur-ensemble des 2 000 primaires) ;
  - ARL₀ i.i.d. exacts (Brook–Evans), et 213,09 pour la ligne de signe ;
  - Γ^spec de x ;
  - λ_req du GARCH à l'ARL₀ i.i.d. exact (`required_threshold`, critère `arl0`, sur les 2 000 primaires), d'où Γ^op.
    Si des trajectoires sont censurées, λ_req et Γ^op sont des bornes supérieures.
- **Risque chiffré** (D10) : probabilités marginales d'échec à code correct, en approximation normale.
  - i.i.d. : environ 5 % pour (0,5 ; 6), 27 % pour (1 ; 3) (référence 3,5 % sous la valeur exacte) et 2,5 % pour le
    signe.
  - GARCH : environ 12 à 23 % par ligne du premier ordre, selon l'erreur MC inconnue des références, et 2,7 % pour le
    signe.

  Les trois statistiques d'un fond partagent leurs trajectoires : l'indépendance n'est pas supposée. La probabilité
  d'au moins un échec sur six est seulement encadrée par 0,27 ≤ P ≤ 0,83 (maximum et borne de l'union).
- **Censure (D9)** : si une trajectoire primaire est censurée, l'ARL₀ de la cellule n'est qu'une moyenne restreinte.
  La porte de la cellule est alors INDÉTERMINÉE, sauf si la moyenne restreinte dépasse déjà 1,05·réf (FAIL certain par
  excès). La probabilité de censure est négligeable aux T_max retenus.

## 7. Encodeurs à fenêtre (`e3_window_encoders.csv`)

- z_t = (1/L)Σ_{j<L} uᵀx_{t−j}, avec L ∈ {1 (contrôle, chemin journalier), 5, 20, 60}. Les L − 1 jours avant la
  fenêtre sont un retard d'entrée (lignes nulles) ; le CUSUM repart au début de la fenêtre.
- **Fonds** :
  - D5 i.i.d. N(0, 1), où Γ_z = L exactement ;
  - D6 SYM-`d2_us97` avec u = canal marché (colonne 0 de `z_odd`) de la base brute, signes neufs, départs uniformes
    sur [L − 1, n − H].

  20 000 réplications, H ∈ {750, 2 000}. Une trajectoire de base par réplication sert aux quatre valeurs de L.
- **Mesures** :
  - Γ_z^spec à la largeur par défaut (prompt), et Γ_z^spec à largeur 10L en diagnostic ;
  - L analytique ;
  - CUSUM unilatéral sur z/sd(z) (sd = 1/√L en D5, sd de calib en D6), δ = 0,5, à λ_iid (trajectoires i.i.d.
    N(0, 1), FPR(H) = α), avec λ_req et Γ_z^op ;
  - CUSUM de signe au treillis sur 1{z > 0} − ½ ;
  - Ljung–Box à 20 retards sur les signes (`acorr_ljungbox`) : taux de rejet à 5 % et p médiane.
- **Attendu** : à la largeur par défaut (6–7 retards), Γ_z^spec ≈ 4 ; 7 ; 7,6 pour L = 5, 20, 60. « ≈ L » n'est
  atteint qu'avec une largeur ≳ L (H5).

## 8. Remise à zéro par fenêtre et absence de dérive (tests)

`tests/test_e3.py::test_window_reset` est paramétré sur les lectures locales : P1-C exacte et étiquettes, P1-D,
dépassement (premier ordre et signe), encodeurs (CUSUM sur z, CUSUM de signe).
1. Séries et préfixes sont des tirages nuls (i.i.d. ou GARCH), sans dérive ni onset.
2. Pour chaque fenêtre (départs énumérés et aléatoires), l'indice d'alarme de la fonction de production égale celui
   des portages scalaires de l'Article B (`cusum.strict_cusum`, `cusum.bilateral_delay`) lancés sur la seule fenêtre
   depuis S₀ = 0.
3. **Invariance au préfixe** : remplacer les lignes antérieures à la fenêtre par un autre tirage nul laisse chaque
   indice inchangé. Seul le retard déclaré est conservé (L − 1 pour les encodeurs, 0 ailleurs), ainsi que les
   constantes ajustées q̂, μ, σ et Γ̂.
4. **Non-vacuité** : un CUSUM reporté d'une fenêtre à l'autre a S > 0 au début d'au moins une fenêtre et change au
   moins un indice. Le test détecterait donc une remise à zéro manquante.

S'y ajoutent :
- `test_no_injection` : E3 n'importe de `injection` que `symmetrize`, et tous ses enregistrements portent H0 ;
- `test_circular_arl_path` :
  - lignes (s + t) mod n et |x| conservé ;
  - signes neufs au deuxième tour ;
  - mises de P3-CS (b) et e-détecteur continus à la couture : égaux au calcul sur la trajectoire déroulée, différents
    d'un redémarrage à la couture.

## 9. Contrôle secondaire de calibration (`results/e3/e3_j2_check.txt`) — révision 4 : sans verdict J2, voir R4.3

Le fichier compte 54 lignes : P1-C exact (5 titres × 2 jeux × 2 H = 20) et canaux P3-C ((6 + 11) × 2 = 34).
- Chaque ligne donne le FPR, le niveau, |écart|, PASS si |écart| ≤ 0,01 (6,8 à 6,9 ET à 20 000 réplications) et
  l'appartenance à la région à 99 %.
- Ligne finale : verdict de la règle du prompt et compte **descriptif** des sorties de région à 99 % (D10).
  - Les cellules partagent symétrisation, panel et réplications : aucune loi binomiale ni p-valeur n'est attachée à ce
    compte.
  - Son espérance sous exactitude, Σ_i P(sortie_i) ≈ 0,54, vaut par linéarité quelle que soit la dépendance. Elle est
    donnée comme ordre de grandeur, pas comme test.
- Le risque de faux FAIL de la règle à 1 point est borné par l'union : 54 × P(|Z| > 6,77) < 10⁻⁹ (approximation
  normale).
- Les titres et canaux sont ceux du J2 (i) d'E1, qui utilise 2 000 réplications.
- En `--quick`, le fichier porte la mention « quick: not a J2 verdict ».

## 10. Coût et fractionnement des 20 000 trajectoires

**Coûts unitaires** mesurés le 2026-10-22 sur un fil, non remesurés ; `--quick` rechronomètre chaque bloc :
- e-détecteur CUSUM : 18,8 ns par (trajectoire × mise × pas) ; SR : 31,6 ns ;
- dictionnaire : 17,5 ns par (trajectoire × canal × mise × pas) ;
- CUSUM bilatéral 20 000 × 2 000 : 0,29 s ;
- `garch_panel` : 5,4 µs/pas ; `Garch` (reps = 1) : ≈ 10 µs/pas ;
- `fit_garch_qmle` (n = 941) : 20 ms.

| Bloc | Trajectoires | Unité de tâche | Mémoire/tâche | CPU |
|---|---|---|---|---|
| D6 registre (56 spécifications) | 20 000 / spéc. | 1 groupe (jeu, H) ; `null_check` séquentiel, paquets internes de 64 | ≤ 0,5 Go | ≈ 0,5 h (groupe max ≈ 10 min) |
| P1-C D6 | 20 000 × 4 | paquets de 2 000 | faible | ≈ 0,1 h |
| D5 P1 (t₇, gaussien) | 20 000 / fond | paquets de 500 ; 320 Mo d'énergies rapatriées par fond | ≤ 1 Go (principal) | ≈ 0,6 h (`Garch` ≈ 790 s, `garch_panel` ≈ 425 s, QMLE ≈ 800 s) |
| Réel pair, P3-D, placebo brut | énumération ; 20 000 i.i.d. par (titre, H) | 1 jeu × lecture | ≤ 0,5 Go | ≈ 0,3 h |
| ARL₀ pièces (5 structures × 2 types) | 20 000, une passe de 15 120 pas pour les trois γ | paquets ≤ 2·10⁷ éléments par tableau | ≤ 0,5 Go | ≈ 1,1 h |
| ARL₀ D6 circulaire (3 pipelines × 2 jeux × 2 types) | 20 000 | idem | ≤ 0,5 Go | ≈ 1,5 h (dont ≈ 0,3 h de flux P2-C) |
| ARL₀ brut | 3 774 départs | paquets de 100 départs | ≤ 0,5 Go | ≈ 0,15 h |
| Dépassement | 20 000 / cellule, dont les 2 000 primaires | paquets de 250 | ≤ 0,2 Go | ≈ 1,0 h (GARCH à 31 000 pas ≈ 0,9 h) |
| Encodeurs | 20 000 × 2 fonds × 4 L × 2 H | paquets de 2 000 | faible | ≈ 0,2 h |
| **Total** | | | | **≈ 5,6 h CPU**, marge × 1,5 → 8,5 h, soit ≈ 25 min à `--jobs 24` (35–40 min à 16) |

- **Graines** :
  - réplication r de la cellule c : `SeedSequence([13, crc32(c), r])`, suffixe 7 pour les pièces ;
  - tirages de niveau cellule : `[13, crc32(c), 10⁶ + j]` ;
  - groupes `null_check` : clé [13, crc32(groupe)].

  Les paquets ne servent qu'à l'ordonnancement : les sorties sont invariantes à `--jobs` et à la taille des paquets,
  et l'agrégation suit un ordre trié fixe. Pool `concurrent.futures`, contexte `spawn`.
- **`--quick`** : 500 réplications de signe et de `null_check`, 200 trajectoires d'ARL₀, 200 de dépassement, 500
  d'encodeurs, toutes les unités réelles. Cible : < 10 min à `--jobs 8`.
- **Réduction** si la projection de `--quick` dépasse 1 h murale à `--jobs 24` : d'abord ARL₀ pièces et D6, de 20 000 à
  10 000 (`C-e3-sizes`). Jamais les cellules de signe ni les 2 000 trajectoires primaires du dépassement.

## 11. Fichiers touchés et réutilisations

- **Nouveaux** :
  - `experiments/e3_calibration.py` (≈ 800 lignes) : options `--config`, `--quick`, `--out`, `--fig-dir`, `--log-dir`
    et `--jobs` ; figures et journal par défaut dans `figures/<nom de --out>` et `logs/<nom de --out>` ;
  - `configs/e3.yaml` : tailles, grilles, paquets, T_max, lignes et références du dépassement, L, Ljung–Box, étiquettes
    de cellule et bloc `quick` ;
  - `tests/test_e3.py` (< 60 s ; `make check` dure environ 3 min 16 s aujourd'hui) ;
  - `results/e3/{e3_cells,e3_arl0,e3_raw_placebo,e3_overshoot,e3_window_encoders}.csv` et `e3_j2_check.txt`
    (`save_fair_csv`) ;
  - `figures/e3/{fpr_cells,arl0,raw_placebo,gamma}.{png,pdf}`, tirées des CSV seuls ;
  - `logs/e3/run.log`, indexé par `git add -f` comme `logs/e10/run.log` : commande, commit, SHA-256 de la
    configuration, des entrées et des sorties, durées, verdicts ; chemins relatifs, sans chemin absolu de la machine.
- **Partagé (Q-A, défaut)** : nouveau `jepadrift/stats/intervals.py`, qui reçoit `wilson` déplacé à l'identique depuis
  `experiments/e10_robustness.py` (Wilson 95 % borné du stream 27).
  - E10 l'importe ; `tests/test_e10.py` passe inchangé ; les CSV d'E10 `--quick` gardent le même SHA-256 avant et
    après.
  - E3 est le second consommateur (règle de `CLAUDE.md` ; recommandation du wrapup 27). `coin_bits`, `alarms` et
    `deff_rate_ci` restent dans E10, car E3 ne les utilise pas.
- **Modifiés** : `docs/DEVIATIONS.md` (entrées `C-e3-*` en anglais). Après le GO : `prompts/plans/plan-13.md`,
  `prompts/GO-stream-13.md`, `prompts/wrapups/wrapup-13.md` (anglais).
- **Inchangés, par choix** : `jepadrift/sim.py` (D5) et `jepadrift/pipelines.py`, modifié en parallèle par les streams
  12, 14, 17 et 18. E3 n'utilise que son API publique : `make_spec`, `fit_pipeline`, `run_pipeline`, `null_check`,
  `null_target`, `summarize`, `horizon_gamma`, `split_rows`, `save_fair_csv`, `composition_for`, `residual_energy`,
  `stakes`, `PIPELINES`, `Z99`.
- **Réutilisations** :
  - `monitors` : `lattice`, `cusum`, `eprocess`, `gamma` (`gamma_spectral`, `required_threshold`,
    `gamma_operational`), `streams` (`exact_sign_stream`, `label_stream`, `energy_stream`) ;
  - `stats.garch` (R01 verbatim), `injection.symmetrize`, `sim`, `representations.extract.DATASETS` ;
  - statsmodels : `acorr_ljungbox`, et `proportion_confint` par `intervals.wilson`.
- **Non commités** : `results/e3_quick`, `figures/e3_quick` et `logs/e3_quick`, supprimés après le contrôle des
  SHA-256, consigné dans le wrapup.

## 12. Exécution après GO (TDD)

0. GO explicite seulement : `GO-stream-13.md` verbatim, `plan-13.md` avec « Décision GO intégrée », appels de
   contrôle de graphify et jcodemunch.
1. Si Q-A est retenu, mettre de côté dans le scratchpad le SHA-256 des CSV d'E10 `--quick`, déplacer `wilson`,
   relancer E10 `--quick` (SHA-256 identiques) et `pytest tests/test_e10.py`.
2. Écrire `tests/test_e3.py` d'abord (rouge). Il couvre :
   - la garde D1 (refus du 2005-01-03 et du 2020-01-02 ; D3 = 3 774 lignes dès le 2005-01-04) ;
   - les cinq titres ;
   - le §8 ;
   - l'invariance à `--jobs` et à la taille des paquets (cellule d'ARL₀ sur pièces, 40 trajectoires ; cellule P1 de
     D5, 30 réplications) ;
   - Brook–Evans contre les tables (k = 0,5 : h = 4 → ≈ 336 ; h = 5 → ≈ 931) et la valeur 213,09 ;
   - le câblage P1-D identique aux expressions de R01 ;
   - les comptes de fenêtres brutes (3 025 / 1 775 ; 5 / 1) ;
   - Γ_z^spec large ≈ L sur une longue moyenne mobile ;
   - la borne de `wilson` en k = 0 et k = n ;
   - le classement d'ARL₀ (D9) : PASS seulement si lb99 ≥ γ, INDÉTERMINÉ sinon, aucun chemin vers FAIL, colonnes de
     déficit ; le contrôle σ borné sur pièces (SR : moyenne de M_σ − σ compatible avec 0 ; CUSUM : ≤ 0) ;
   - une fumée de la CLI sur une configuration minimale, lancée deux fois, octets identiques.
3. Écrire `configs/e3.yaml` puis `e3_calibration.py` jusqu'au vert.
4. Lancer `--quick` deux fois, la seconde dans le scratchpad, `--jobs 1` contre `--jobs 8` : SHA-256 identiques.
   Chronométrer chaque bloc, puis appliquer la règle de réduction du §10.
5. Lancer **un seul** run complet (`--jobs 24`). Les verdicts sont lus tels quels. Un rerun n'a lieu qu'après la
   correction d'un défaut de code détecté par un test ou par un plantage ; il est consigné avec les deux SHA-256, à
   graines inchangées.
6. Figures : skill `dataviz` chargé avant le code de tracé.
7. Entrées `DEVIATIONS` en anglais :
   - `C-e3-design` : D1, D2, D5, D6, D10, K fixé sur D6 ;
   - `C-e3-readings` : λ_iid de P1-D et lignes propres, fenêtre et chevauchement de P2-C, règle des étiquettes,
     mélange différé ;
   - `C-e3-arl0` : pièces, D6 circulaire continu, censure brute, trajectoires communes aux γ, classement D9, déficit de
     moyenne restreinte, contrôle σ borné ;
   - `C-e3-overshoot` : références MC contre valeurs exactes, porte primaire, absence de rerun ;
   - `C-e3-encoders` : largeur de bande, contrôle L = 1 ;
   - `C-e3-shared-wilson`, si Q-A est retenu.
8. Clôture :
   - wrapup en anglais (Context, Validated Results avec SHA-256, Errors and Dead Ends, Current State, Vigilance
     Points, Recommendations) ;
   - `tools/reindex_graphify_jcodemunch.sh` ;
   - `PATH="$MAKEBIN:$PATH" make check` ;
   - commit unique `feat(e3): calibrate the monitors under H0 (stream 13)`, indexé chemin par chemin, plus
     `git add -f logs/e3/run.log`, sans trailer ;
   - `git status --porcelain` vide ;
   - **arrêt** avant fetch, fusion ou push, puis transmission à l'orchestrateur du diff, des vérifications, des SHA-256
     et du wrapup.

## 13. Vérification

Chaque commande échoue en cas d'écart : `cmp` sur les octets, `test` sur l'état Git, `MPLBACKEND=Agg` partout, y
compris pour `make check` et `git commit`.

```bash
cd ~/JEPA-stream-13
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin
SCRATCH=<scratchpad de la session>
# step 0: only the two decision files are new
test "$(git status --porcelain)" = "$(printf '?? prompts/GO-stream-13.md\n?? prompts/plans/plan-13.md')" || exit 1
# Q-A: E10 quick outputs identical before/after the move of wilson
for f in e10_cells.csv e10_gains.csv; do cmp "$SCRATCH/e10_before/$f" "$SCRATCH/e10_after/$f" || exit 1; done
.venv/bin/pytest -q tests/test_e3.py tests/test_e10.py || exit 1
.venv/bin/python experiments/e3_calibration.py --quick --jobs 8 --out results/e3_quick || exit 1
.venv/bin/python experiments/e3_calibration.py --quick --jobs 1 --out "$SCRATCH/e3_quick2" \
    --fig-dir "$SCRATCH/fig" --log-dir "$SCRATCH/log" || exit 1
for f in e3_cells.csv e3_arl0.csv e3_raw_placebo.csv e3_overshoot.csv e3_window_encoders.csv e3_j2_check.txt; do
  cmp "results/e3_quick/$f" "$SCRATCH/e3_quick2/$f" || exit 1
done
.venv/bin/python experiments/e3_calibration.py --jobs 24 --out results/e3 || exit 1
cat results/e3/e3_j2_check.txt
PATH="$MAKEBIN:$PATH" make check || exit 1
test -z "$(git status --porcelain)" || exit 1   # after the commit
```

## 14. Questions et hypothèses (défaut entre crochets)

**Bloquante (arbitrage avec le stream 12)**

- **Q-A — `wilson` partagé.** [Déplacé par ce stream dans le nouveau `jepadrift/stats/intervals.py` ; E10 l'importe ;
  le stream 12 l'importe après intégration.]
  - Alternative : `jepadrift/stats/drift.py`, que le stream 12 modifie aussi (son changement c).
  - Alternative : le stream 12 fait le déplacement, et E3 attend sa fusion.

**Défauts à confirmer (non bloquants)**

- **H4 (ex-Q2) — P1-D.** [Lignes propres = calib (941 jours) pour μ, σ et Γ̂ ; λ_iid par permutation globale (D5) ou
  bootstrap i.i.d. (réel), 20 000 trajectoires ; 65·Γ̂ en annexe.] Alternative : la fenêtre de R01,
  2018-01-02..2019-12-31.
- **H5 (ex-Q6) — Γ^spec.** [Largeur du prompt partout, plus un diagnostic à 10L pour les seuls encodeurs.]
- **H6 — Tailles** et règle de réduction du §10.
- **H7 — Pièces de l'ARL₀.** [Une pièce ±1 par colonne ; mises constantes pour P3-CS (b).]
- **H8 — Exécution.** [`--jobs 24` ; sorties quick non commitées ; `logs/e3/run.log` indexé de force, précédent
  d'E10.]
- **H10 — Lectures e-détecteur.** [γ_H = H/α ; P3-CS (a) à γ = 20.]
- **H11 — Fenêtres brutes.** [Toutes les fenêtres des lignes strictes, alignées sur les n de l'audit.] Alternative : les
  seules fenêtres du pretrain, comme E10 (2 019 / 769).
- **H12 — Encodeurs.** [D5 i.i.d. et D6 SYM-`d2_us97` seulement ; contrôle L = 1 ajouté.]
- **H13 — Bras recentrés.** [Règle zéro = négatif de l'Article B (`label_stream`), q̂ de calib, pour P1-C et P3-C.]
- **H14 — Contrôle sans hypothèse de queue (ajout proposé, §5).** [Inclus : moyenne de M_σ − σ au temps d'arrêt borné
  σ = min(T, 60γ).] Alternative : le retirer ; E3 ne certifie alors aucun échec d'e-détecteur.

## 15. Points de vigilance

- **Multiplicité (D10).** 58 cellules exactes (D5 : 4 ; D6 : 54) sont lues dans leur région à 99 %.
  - Elles partagent trajectoires et tirages (§3) : le nombre de sorties n'est pas binomial.
  - Il est rapporté comme compte descriptif, avec son espérance par linéarité (≈ 0,58), sans p-valeur ni comparaison à
    une loi binomiale.
  - La règle J2 à 1 point (≈ 6,8 ET par cellule) reste robuste par la borne de l'union.
- **Base D6.** Elle est ajustée sur la symétrisation (K fixé) et diffère légèrement de la base brute. Les canaux bruts
  utilisent la base de calib brute, celle de l'audit, ce qui permet la jointure par indice de PC.
- **P1-C sur D6** est trivialement exact (signes = pièces) : la cellule vérifie l'implémentation et le traitement des
  nuls. Les cellules informatives sont les placebos bruts.
- **P1-C au registre.** Si le stream 12 ajoute un P1-C au registre avant la fin d'E3, la boucle locale bascule dessus.
  Son plan le garde aujourd'hui hors du registre.
- **P2-C bootstrap** : calibré dans l'échantillon, avec 3 fenêtres disjointes.
- **Borne stricte.** E1 et E3 implémentent la même : mutualisation dans `jepadrift/` après les deux fusions.
- **Porte du dépassement.** Le risque d'au moins un échec a priori est élevé : entre 0,27 et 0,83 (maximum et borne
  de l'union, §6). Tout FAIL est attribué (erreur MC de la référence contre valeur exacte), sans rerun.
- **Machine partagée** : le temps mural peut doubler ou tripler.

## Journal des révisions

**v1 → v2 (2026-10-23)** : base `c8fe24d` → `c284823`.
1. D1 remplace H9 : borne stricte au 2005-01-04, D3 passe de 3 775 à 3 774 lignes.
2. D2 remplace H3/Q7 : cinq titres pour toutes les lectures P1 réelles.
3. D3 : tests de remise à zéro et absence de dérive ou d'onset dans le préfixe.
4. D4 : fenêtres chevauchantes descriptives ; ARL₀ D6 circulaire continue à la couture.
5. D5 à D8 : Q1, Q3, Q4 et Q5 tranchés.
6. K fixé sur D6 (précédent d'E10).
7. Trajectoires d'ARL₀ communes aux trois γ, soit environ −30 % de CPU.
8. Boucle P1-C locale au lieu de `_null_block` et `_coins`.
9. Q-A : `wilson` d'E10.
10. Contrôle L = 1 des encodeurs.
11. Session sous `.venv`.

**v2 → v3 (2026-10-23, NO-GO statistique provisoire)** :
1. D9 : classement d'ARL₀ PASS / INDÉTERMINÉ, sans FAIL faute de borne de queue. Le déficit de moyenne restreinte est
   rapporté à part, et le contrôle σ borné (H14) est proposé.
2. D10 : comptes multi-cellules descriptifs, sans p-valeur binomiale ; probabilités conjointes encadrées par l'union
   (risque du dépassement réécrit : 0,27 ≤ P ≤ 0,83 au lieu de 0,5–0,6 sous indépendance).
3. Censure de la porte du dépassement : INDÉTERMINÉE sauf excès certain ; bornes supérieures pour λ_req et Γ^op censurés.
4. Encodeurs : trajectoire de base commune aux valeurs de L, déclarée.

**v3 → v4 (2026-10-28, GO avec corrections obligatoires)** :
1. Audit des fichiers partiels (R4.2) et état revérifié (R4.1).
2. Q-J2 : verdict primaire J2 (i) d'E1 à 2 000 réplications ; contrôle E3 secondaire, sans verdict.
3. P1-D D5 : calibration et évaluation indépendantes (rôles `SeedSequence` distincts, `n_cal`, `n_eval`).
4. Borne stricte : exclusion déclarée, comptée et consignée du 2005-01-03 de D3.
5. Colonnes `deff` et `n_eff` sur le dépassement et les encodeurs ; P2-C bootstrap `calibrated_conditional`.
6. Q-A vérifié par identité AST ; arrêt sur échec d'une porte de reproduction.

## Décision GO intégrée (2026-10-23, révision 3) — historique remplacé

GO de l'orchestrateur, verbatim :

> GO final pour la révision du plan 13. Je viens d'exécuter /mcp reconnect all et de vérifier graphify et jcodemunch
> connectés. Lance ExitPlanMode puis implémente en mode auto. Maintiens la porte primaire 2000 répétitions/±5 %, les
> resets CUSUM, la date stricte et la qualification indéterminée des ARL censurées, sans relance opportuniste.

Application :
- **Révision 3 approuvée sans amendement.** Les questions ouvertes prennent leur défaut :
  - Q-A : `wilson` déplacé vers `jepadrift/stats/intervals.py` ;
  - H4 à H13 ;
  - H14 : contrôle σ borné inclus.
- **Réaffirmés** :
  - porte primaire de 2 000 répétitions à ±5 % (D8) ;
  - remises à zéro du CUSUM par fenêtre (D3) ;
  - borne stricte du 2005-01-04 au 2019-12-31 (D1) ;
  - ARL₀ censurés classés INDÉTERMINÉ (D9) ;
  - aucune relance opportuniste : un rerun n'a lieu qu'après la correction d'un défaut de code, et il est consigné.
- **MCP** : graphify et jcodemunch ont été vérifiés par l'orchestrateur. L'instance refait un appel de contrôle avant la
  première écriture.
- **Mode** : exécution autonome jusqu'au commit local vérifié, puis arrêt avant fetch, fusion ou push.
- **Conventions appliquées à l'exécution** (mémoire du GO 17, 2026-10-23) :
  - `prompts/GO-stream-13.md` est rédigé en français, avec les messages de l'orchestrateur cités verbatim ;
  - les commandes de vérification échouent sur écart (`cmp`, `test`, état Git exact), sous `MPLBACKEND=Agg` (§13).

## Décision GO intégrée (2026-10-28, révision 4)

GO de l'orchestrateur, verbatim (transcrit aussi dans `prompts/GO-stream-13.md`, avec le message de reprise) :

> GO FINAL STREAM 13 pour le plan révision 4 du 2026-10-28
> (~/.claude/plans/tu-reprends-uniquement-le-imperative-truffle.md), avec corrections obligatoires. Préserve les cinq
> fichiers non commités, conserve le GO antérieur comme historique remplacé, ajoute le présent arbitrage verbatim à
> prompts/GO-stream-13.md et enregistre prompts/plans/plan-13.md révision4 avec Décision GO intégrée avant code. Q-J2:
> le verdict primaire J2(i) est E1/stream12 à 2000 répliques; e3_j2_check.txt à 20000 est contrôle secondaire de
> calibration sans verdict J2 distinct. Les comptes multi-cellules E3 partagent des tirages: descriptifs seulement, sans
> probabilité conjointe sous indépendance. P1-D D5: pour publier un IC Wilson de FPR, estime lambda_iid sur 20000
> trajectoires de calibration et mesure le FPR sur 20000 trajectoires d'évaluation indépendantes, avec SeedSequence
> rôles distincts, n_cal/n_eval et coût consignés; sinon CI=NA et ligne descriptive exclue de toute porte. Ne présente
> jamais un Wilson du même échantillon de calibration comme inférentiel. La borne réelle doit être stricte et
> l'exclusion du 2005-01-03 D3 doit être explicitement comptée, jamais silencieuse. Fige les cinq indices littéraux
> communs avec E1; teste reset de chaque fenêtre et séparation FPR/ARL/Γ. Le contrôle CLI confirme graphify et
> jcodemunch connectés; recharge et vérifie les deux MCP par appel avant la première écriture. Implémente uniquement E3
> dans ce worktree via .venv et MPLBACKEND=Agg, TDD RED avant corrections, deux quick identiques par cmp, un run
> complet, make check, empreintes, wrapup et commit local. Aucun autre stream, aucun fetch/rebase/push/fusion. En cas de
> blocage outillage ou temps, stoppe et rapporte précisément.

Application :
- **Révision 4 approuvée avec les corrections R4.3**, intégrées avant tout code ; les défauts H4 à H14 restent ceux de
  la révision 3.
- **Q-J2 tranchée** : le verdict primaire J2 (i) est E1 (stream 12) à 2 000 réplications ; E3 ne produit aucun verdict
  J2.
- **Réaffirmés** : D1 (borne stricte, exclusion comptée), D3 (remises à zéro), D8 (porte primaire de 2 000
  trajectoires à ±5 %, sans rerun), D9 (ARL₀ censurés INDÉTERMINÉ), D10 (comptes descriptifs).
- **MCP** : rechargés et vérifiés par appel avant la première écriture (R4.1).
- **Mode** : exécution jusqu'au commit local vérifié, sans fetch, rebase, fusion ni push ; arrêt et rapport en cas de
  blocage d'outillage ou de temps, ou d'échec d'une porte de reproduction.

## Décision GO intégrée (2026-10-29, archivage du FAIL D8)

GO d'archivage : autorisation du chercheur par une directive en français du 2026-10-29, non reproduite ; instructions
opérationnelles en anglais rédigées par l'orchestrateur Codex d'après cette directive, citées verbatim dans
`prompts/GO-stream-13-archive.md` sans être un texte verbatim du chercheur. Il amende le GO du 2026-10-28 après
l'arrêt consigné dans `prompts/STOP-stream-13-D8.md`.

Constat (run complet unique du 2026-10-28, `results/e3/e3_overshoot.csv`) : la porte primaire D8 de
`iid/first_order_d1_l3` (trajectoires 0 à 1 999) est **FAIL** : ARL₀ moyen 1 994,0665 contre la référence 1 894,
écart relatif +0,0528334213 > 0,05, aucune trajectoire censurée. Les cinq autres cellules primaires passent. Le
diagnostic à 20 000 trajectoires (1 964,2627) et la valeur i.i.d. exacte (1 962,7935) restent descriptifs.

Application :
- **Seule clause levée** : l'arrêt avant commit sur un FAIL de D8 (R4.3, point 7, et « Mode » de la décision du
  2026-10-28). Le FAIL est archivé tel quel, sans correction ni requalification.
- **Inchangés** : D8 (porte primaire de 2 000 trajectoires à ±5 %, sans rerun), D9, D10, les autres points de R4.3 et
  les sections 0 à 15, hors restrictions ci-dessous. Aucun run d'E3 ni de `--quick`, aucun nouveau tirage, aucun rerun
  sélectif, aucun réglage de seuil, aucun changement de tolérance ou de référence, aucune réinterprétation de la porte
  primaire.
- **Consignation** : entrée `C-e3-d8-fail` (anglais) dans `docs/DEVIATIONS.md` ; `prompts/wrapups/wrapup-13.md`
  (anglais) avec les chemins et les SHA-256 des sorties ; `prompts/STOP-stream-13-D8.md` commité inchangé.
- **Restrictions du GO** (elles remplacent les points correspondants des §11, §12 et §13) :
  - vérification sans script d'expérience : empreintes des artefacts existants, `pytest` ciblé sur `tests/test_e3.py`
    et `tests/test_e10.py`, `make prompts-check` et `make check` ; si un test échoue, arrêt avec les preuves et
    modifications laissées en place ;
  - indexation chemin par chemin des seuls livrables complets ; `logs/e3/run.log`, journal ignoré, n'est pas indexé de
    force ; `results/e3_quick/`, `figures/e3_quick/` et `logs/e3_quick/` ne sont ni commités ni supprimés ;
  - clôture : wrapup, `tools/reindex_graphify_jcodemunch.sh` (`graphify update .`, AST seulement, et
    `jcodemunch-mcp index` avec `use_ai_summaries: false`), `make check`, puis un seul commit
    `feat(e3): archive H0 calibration with failed D8 gate (stream 13)`, sans trailer ;
  - état Git attendu après le commit : exactement `?? figures/e3_quick/` et `?? results/e3_quick/` ;
  - ni fetch, ni rebase, ni push, ni fusion, ni modification de `main`.
- **MCP** : graphify (`graph_stats`) et jcodemunch (`menu`) vérifiés par appel avant la première écriture.
