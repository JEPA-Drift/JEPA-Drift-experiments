Les streams 1 à 11 valident la pile de calibration au bit près. En revanche, trois choix de spécification des prompts 12 à 28 sont désormais invalidés et doivent être corrigés avant la prochaine vague :

- **La lecture anytime-valid à γ ∈ {20, 252} n'est plus utilisable** : sur 2 000 jours, ses alarmes sont dominées par les fausses alarmes.
- **Les gains « prévus » tirés de l'audit ne sont plus exploitables** : ils sont rendus inutilisables par le bruit (R9) et par la sélection des frontières de phases.
- **F2 et P3-D, tels que spécifiés pour E1, sont incompatibles avec les données** : D2 n'a pas de caractéristiques et la calib ne compte que 941 jours.

Ce qui suit contient l'analyse, les corrections de configuration, un prompt d'hygiène 8b à lancer en premier, et les révisions des prompts 12 à 28.

## 1. Analyse des résultats (streams 1 à 11 et 11b)

### 1.1 Acquis vérifiés

| Stream | Résultat                                                                                                                                                                                                    | Portée                                         |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 1      | J1 PASS (16 oct.) ; `e2_cells.csv` bit-identique (`e315e537…`)                                                                                                                                              | Props 2–3 validées sous forme non asymptotique |
| 2      | D1 (SPY : 6 414 jours depuis 2000) ; D2 (5 154 × 97) ; datations 66 / 48 / 102                                                                                                                              | Bases univariée et poolée de l'Article B       |
| 3      | 503 titres sur 6 738 jours ; `d3_239` = les 239 plus longs historiques (liste CD-DFM non redistribuable) ; `d3_500` à 13 % de NaN                                                                           | Coupe principale                               |
| 4      | Identités R01 (1 401 cellules, deux environnements) et R08 (32/32 à 1e-12). Le treillis coïncide avec l'énumération exhaustive. Signe exact sous GARCH-t₇ : FPR 0,04275 pour un niveau 0,042898 (H = 1 000) | Noyau de détection fidèle à l'Article B        |
| 5      | F1–F4 injectés à information exacte (1e-10) ; E2 inchangé après le déplacement de `Garch`                                                                                                                   | Protocole semi-synthétique                     |
| 6      | Interface Z-1 ; K = 5 (D2) et 10 (D3) ; tail10 : 46 et 123 composantes                                                                                                                                      | Contrat de branchement des représentations     |
| 7      | Identité R15 : 56 cellules, dont 54 au bit. Canaux exacts sur D6 : FPR de 0,0385 à 0,0505 pour un niveau de 0,043947 (H = 750)                                                                              | Critère J2 (i) déjà tenu sur D2                |
| 8      | Quatre contrats, découplage, hooks                                                                                                                                                                          | Garde-fous de fusion                           |
| 9, 10  | BAF (licence CC BY 4.0 ; fraude de 0,87 % à 1,47 %) ; D4 : 498 titres, 6 541 jours, six places                                                                                                              | Domaines secondaires                           |

### 1.2 Lecture scientifique

1. **La pile de calibration est publiable.**
   - Les flux de signe sont exacts sur D6.
   - Les identités avec l'Article B tiennent au bit près.
   - Les garanties anytime-valid sont vérifiées par Monte Carlo.

   Ce socle n'est plus un risque.

2. **Aux transitions réelles, aucune information de largeur n'est mesurable.**
   - Médianes de SR² débiaisé : marché 40,8 (D2, `lt_spy`) et 38,2 (D3) ; sous-espace factoriel ≈ 0 ; idiosyncratique +16,6 et +8,6 sur D2, −181,6 et −51,7 sur D3 (R9).
   - Le placebo du stream 11b montre que le SR² de marché aux frontières datées vient de la sélection. Sous rotation des phases, il vaut ≈ −2,5. L'excès réel va de +21 à +43, avec p ≤ 0,0015.
   - Conséquence : la preuve de l'article sera semi-synthétique, et les données réelles servent d'appui.
   - Le déclencheur R10 de la contingence C1 est partiellement atteint. La phase linéaire d'E6 passe donc en priorité A.

3. **Le goulot est la conception du détecteur, pas seulement l'information.**
   - Sur F2 à SR = 8 (SYM-D2, caractéristiques synthétiques constantes), les délais moyens sont :
     - P7 : 15 jours ;
     - P3-C (résiduel complet) : 373 jours ;
     - P3-CS (b) : 446 jours ;
     - P3-CS (a) : 1 164 jours.
   - Cet écart d'un facteur 25 cumule trois pertes : l'efficacité du signe (2/π), la taxe ln K du dictionnaire, et surtout l'alignement cos²ϑ entre la dérive et les canaux.
   - Le mélange isotrope de la Prop. 3, qui éviterait la perte d'alignement, est bloqué par la porte d'indépendance :
     - en mode factoriel, la porte échoue sur une paire de canaux sur 10 (|ρ̂| = 0,13 pour un seuil de 0,098) : c'est une dépendance réelle ;
     - en mode complet, elle échoue sur 13 paires sur 4 560, contre 12,3 attendues sous indépendance : l'échec vient de la seule multiplicité.
   - Le critère J2 (iii) est donc menacé par construction. E1 doit mesurer l'alignement pour pouvoir attribuer une pente faible.

4. **N1 ≈ 2 est le canal le plus robuste.**
   - N1 = 1,97 (D2) et 2,00 (D3).
   - N2, net du bruit d'estimation : de 1,74 à 3,04 pour F1 ; de 1,45 à 1,88 pour F2 (hors `rev_21`).
   - N3 : de 1,21 à 1,25.
   - P3-CS (b) capte N1 sans aucun apprentissage. C'est donc la référence d'attribution du JEPA, avant P3-C.

5. **La lecture anytime-valid à γ = 20 est inutilisable sur un horizon long.**
   - Sous H₀, sur 750 jours, l'e-détecteur de P3-C alarme sur 71 % des trajectoires, celui de P2-C sur 29 %. Ce n'est pas une violation : la garantie porte sur l'ARL₀, pas sur le FPR à horizon.
   - Correction : γ_H = H/α. On a alors P∞(alarme avant H) ≤ α, et cette lecture devient comparable aux lectures exacte, bootstrap et par randomisation.

6. **La symétrie centrale tombe sur données brutes.**
   - Rejets de l'audit (Holm à 5 %) :
     - D2 : PC1 (tests binomial et des triplets), PC3 (binomial) ;
     - D3 : PC1 et PC2 (les deux tests), PC3 et `rev_21` (binomial).
   - L'exactitude des flux de signe tient sur D6, mais pas sur le canal marché brut.

7. **Les univers D3 et D4 sont biaisés par la survie.**
   - D3 repose sur les constituants actuels du S&P 500 ; D4 sur une sélection d'au moins 5 000 observations, sans dates de radiation. L'écart `C-D3-survivor` affirme l'inverse pour D3 et doit être corrigé.
   - Pour l'Article B, la sélection des frontières gonfle le SR intra-phase. La part « hors budget » du recensement est donc une borne inférieure, ce qui renforce son énoncé.

### 1.3 Défauts de mes spécifications révélés par l'exécution

| Prompt | Défaut                                         | Constat                                                                                                 | Correction                                   |
| ------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 5      | F2 demandé sur SYM-D2                          | D2 n'a pas de caractéristiques                                                                          | F2 restreint à D3 et D4                      |
| 7      | FPR des e-détecteurs « dans l'IC de la cible » | Une garantie d'ARL₀ ne fixe pas un FPR(H) ; les cibles ont été redéfinies au GO (`C-pipe-null-targets`) | Lecture γ_H = H/α                            |
| 11     | Formule de débiaisage                          | Biais résiduel de 252·d·c·(d + 1)/ν (`C-audit-debias`)                                                  | `sr2_debiased`                               |
| 11     | Gains prévus aux transitions                   | Valeurs NaN (R9) et dénominateur sélectionné (stream 11b)                                               | Prévisions calculées à partir des Δ injectés |
| 12     | H_det = 2 000 pour P3-D                        | La calib ne compte que 941 jours (`C-P3D-windows`)                                                      | P3-D à H = 750                               |

### 1.4 Processus

Incidents déjà corrigés :
- l'interpréteur Trading (numpy 1.26.4) utilisé à la place du `.venv` ;
- les contrats sautés en `.venv` jusqu'au commit `8ae232e` ;
- `GIT_DIR` exporté au hook, désormais réinitialisé par `unset` ;
- un `git stash -u` lancé par une autre instance, d'où l'adoption des worktrees.

Points encore ouverts :
- le fixture D1/D2 réécrit des fichiers suivis à chaque `make check` ;
- le pivot des caractéristiques, le débiaisage et le placebo de phases n'existent qu'en copies locales, alors que les streams 12, 14 et 17 vont tourner en parallèle ;
- l'étape 4 de fin de stream de `CLAUDE.md` (`git push origin <current-branch>`) contredit la recette des worktrees (`stream-XX:main`) ;
- la fidélité du master des prompts n'est plus vérifiée.

### 1.5 Calendrier

- **J2 (25 oct.)** : stream 8b (une demi-journée), puis 12 et 13, avec les runs complets terminés avant le 24.
- **J3 (1er nov.)** : le stream 14 doit démarrer maintenant, en parallèle de 12 et 13.

## 2. Configuration

### 2.1 `CLAUDE.md`

`AGENTS.md` n'est qu'un lien vers `CLAUDE.md` : rien à modifier séparément. Il y a huit modifications.

**A1. Glossaire, puce « e-detector »** — remplacer :
```text
- e-detector: statistic M_n >= 0 with E_inf[M_tau] <= E_inf[tau]; alarm at M_n >= gamma gives
  ARL0 >= gamma. Channels are combined by averaging e-detectors, never by multiplying them.
```
par :
```text
- e-detector: statistic M_n >= 0 with E_inf[M_tau] <= E_inf[tau]; alarm at M_n >= gamma gives
  ARL0 >= gamma and P_inf(alarm before H) <= H/gamma. Channels are combined by averaging
  e-detectors, never by multiplying them. e-process inputs live in [-1, 1]: pass
  2*exact_sign_stream(...), or 2*f for a fraction stream f.
- Readings at a fixed horizon H (location experiments, E1 onwards): anytime-valid = e-detector at
  gamma_H = H/alpha (`pipelines.horizon_gamma`), hence FPR(H) <= alpha = 0.05; exact = sign CUSUM
  at the attainable lattice level <= alpha at H, compared with `select_threshold(...)["threshold"]`
  (the lattice midpoint, C-lattice-midpoint), never with `lam`; bootstrap (R15 port, H = 750) and
  randomization (sign flips) target FPR(H) ~ alpha. ARL0 readings (gamma in {20, 252}) belong to
  E2 and E3 only: at gamma = 20 an e-detector alarms on most null paths within 750 days.
  Delays count monitored days up to the alarm included: delay = alarm_index - tau_star + 1
  (C-pipe-delay).
```

**A2. Glossaire, puce « Gains »** — remplacer :
```text
- Gains: G_floor = I_B/I_A (exact); G_ADD_av = ADD ratio at equal anytime-valid threshold (primary);
  G_ADD_ex = ADD ratio at equal exact ARL0 (exact sign streams only); G_SR = ratio of the smallest SR
  detected within H days with probability >= 1/2.
```
par :
```text
- Gains: G_floor = I_B/I_A (exact, from the injected drift); G_ADD_av = ADD ratio at equal
  gamma_H = H/alpha (primary); G_ADD_ex = ADD ratio at the same exact lattice level at H (exact
  sign streams only); G_SR = ratio of the smallest SR detected within H days with probability
  >= 1/2. Predicted gains use the injected drift, the measured channel alignment
  a_max = max_k dz_k^2/||dz||^2 and `floors` (dictionary multiplier for dictionaries, M(D) for
  mixtures), never `results/audit/predicted_gains.csv`.
```

**A3. Section « Data, splits, leakage »** — insérer après la puce `- D2-D4 splits: …` :
```text
- Panel facts that bind every experiment: `d3_239` = the 239 longest-history current S&P 500
  constituents (C-D3-no239); current constituents form a survivorship-biased universe
  (C-D3-survivor-correction); `d3_500` has 13 % NaN and D4 covers 91 % of its cells (callers pick
  complete sub-panels; `injection.inject` needs a finite panel); D4 = 498 EUROFIDAI stocks with
  >= 5,000 observations, no delisting dates, no GICS, MIL missing 2024-2026 (C-D4-survivor);
  D2 has no characteristics (F2 runs on D3 or D4 only).
- Audit findings that bind every experiment (`results/audit/`, wrapups 11 and 11b): central
  symmetry is rejected on raw rows for D2 PC1 (binomial and triples) and PC3 (binomial), D3 PC1
  and PC2 (both tests), PC3 and char:rev_21 (binomial): exact sign streams hold on D6, raw-data
  sign monitors on these channels need q_hat recentring and claim no exactness. The market SR^2
  at dated SPY boundaries is selection (placebo rotations, p <= 0.0015) and the residual drift
  medians are noise-dominated (R9): `predicted_gains.csv` is descriptive and its NaN stay NaN.
```

**A4. Section « Repository layout »** — remplacer la puce `jepadrift/` par :
```text
- `jepadrift/`: library — `floors.py` (analytic floors, Article C section 3; frozen lot 1),
  `sim.py` (D5 generators), `injection.py` (D6 symmetrization, F1-F4), `pipelines.py` (registry
  P2-C, P3-C, P3-D, P3-CS, P7; the only module importing both representations and monitors) and
  the subpackages `monitors/` (numpy only: `cusum`, `streams`, `lattice`, `gamma`, `eprocess`,
  `calibration`), `representations/` (interface Z-1: `base`, `pca`, `cross_section`, `extract`),
  `jepa/` (torch), `data_loader/` (`articleB`, `sp500`, `baf`, `eurofidai`), `stats/`
  (`covariance`; `garch`, a verbatim R01 port excluded from pyflakes).
```

Remplacer la puce `experiments/` par :
```text
- `experiments/`: one script per experiment or audit (`e2_floor_validation.py`,
  `identity_articleB.py`, `audit_information.py`, then E1, E3, ...), argparse and
  `if __name__ == "__main__":`; a function moves to `jepadrift/` when a second consumer appears.
```

Remplacer la puce `docs/` par :
```text
- `docs/`: `sections/` (section notes), `audits/` (lot audits), `manifests/` (hash manifests of
  proprietary data, e.g. `d4_manifest.json`), `DEVIATIONS.md` (deviations under `C-<topic>`),
  `MAPPING.md` (traceability of reported numbers, created by stream 21).
```

Dans la puce `prompts/`, remplacer la fin `; the master collection Prompts_Claude_Code_v5.md and Orchestration_Streams_v5.md live at this level.` (ces deux noms de fichiers sont entre accents graves dans `CLAUDE.md`) par :
```text
; `prompts/GO-stream-[XX].md` stores the researcher's GO review of a stream plan (decision trace,
committed with the stream); the master collection `Prompts_Claude_Code_v5.md` (derived from
`prompts/streams/`, kept in sync by Mistral Vibe via `tools/check_prompts.py`) and
`Orchestration_Streams_v5.md` (historical wave plan, superseded by the routing table of
`prompts/streams/INDEX.md`) live at this level.
```

**A5. Section « Engineering rules », étape (4) de fin de stream** — remplacer `(4) git push origin <current-branch>.` (commande entre accents graves dans le fichier) par :
```text
(4) push — from `main`: `git push origin main`; from a worktree branch `stream-XX`:
`git fetch origin`, rebase onto `origin/main`, `make check` again if the base moved, then
`git push origin stream-XX:main` (never push the branch `stream-XX` itself).
```

**A6. Section « Engineering rules », puce Article B** — remplacer l'incise `used as-is at its current commit;` par :
```text
used as-is at commit a05f0d9c654b6692e626080c298acebc0f0a0b5c (recorded in
data/derived/MANIFEST.json and checked by tests/test_data_d1_d2.py);
```

**A7. Fin de la section « Engineering rules »** — ajouter :
```text
- Languages: French for user communication, plans, GO reviews and `docs/DEVIATIONS.md` entries;
  English for code, docstrings, `docs/sections/`, wrapups and commit messages.
- Code style: one-line docstrings on public functions (contract or provenance); no comment except
  `# ponytail:` (a deliberate ceiling); no `# noqa`; verbatim ports keep their own text and are
  frozen by byte-identity tests; no AI watermark; Conventional Commits without trailers; staging
  by explicit path only.
- Stream workflow: `/plan` with explicit hypotheses and defaults -> researcher's GO in
  `prompts/GO-stream-[XX].md` -> plan recorded at `prompts/plans/plan-[XX].md` with a "Décision GO
  intégrée" section -> TDD execution -> wrapup -> end of stream. The GO file is committed with the
  stream; an untracked copy left in the main tree is deleted after the push, before
  `git merge --ff-only origin/main` there.
- Wrapups (any agent): English, sections Context, Validated Results (numbers and SHA-256 of
  outputs), Errors and Dead Ends, Current State, Vigilance Points, Recommendations.
- Pre-J4 guard: experiment scripts reading real rows refuse dates >= 2020-01-01 unless
  `configs/FROZEN.json` (stream 21) matches; tests never read such rows (Article B identity
  reproductions excepted).
- Experiments call `pipelines.run_pipeline` / `pipelines.null_check` with a `state` fitted on
  drift-free rows (never `state=None` with injected records); `injection.fit_background` is cached
  per (dataset, window, K); characteristics come from `data_loader.chars`, drift statistics and
  phase placebos from `stats.drift` (stream 8b).
- torch lives only in `.venv` (CPU wheel pinned in `requirements.txt`, from stream 14 on), never
  the Trading environment's torch; once installed, the torch guards of `tests/test_contracts.py`
  must run, not skip.
- `make check` stays under 5 minutes: Monte Carlo tests use reduced sizes; full runs live in
  experiment scripts.
```

**A8. Section « Worktrees and parallel streams »** — remplacer :
```text
  `data/raw/` is a real directory holding one absolute symlink per subdirectory (`d3_yf`, `baf`;
  link `eurofidai` only when the stream needs D4), so a single pinned environment produces stable
  hashes.
```
par :
```text
  `data/raw/` is a real directory holding one absolute symlink per raw subdirectory the stream
  reads (`d3_yf`, `baf`, `electricity`; `eurofidai` only when the stream needs D4), so a single
  pinned environment produces stable hashes.
```

### 2.2 `prompts/streams/INDEX.md`

**I1.** Après le premier paragraphe (celui qui se termine par « présentes dans chacun. »), ajouter :
```text
Révision du 2026-10-18 : prompts 12 à 28 révisés d'après les streams 1 à 11 et 11b ; nouveau prompt
`prompt-08b-hygiene.md` ; routage replanifié (section « Replanification du 18 octobre 2026 »).
Le master est resynchronisé depuis les fichiers stream ; l'outil de contrôle `tools/check_prompts.py` et la cible `make prompts-check` sont livrés par le stream 8b.
```

**I2. Fin de stream, étape 4** — remplacer `4. git push origin <branche courante>.` par :
```text
4. push — depuis `main` : `git push origin main` ; depuis un worktree `stream-XX` :
   `git fetch origin`, rebase sur `origin/main`, `make check` si la base a bougé, puis
   `git push origin stream-XX:main` (jamais la branche `stream-XX` elle-même).
```

**I3. Routage** — remplacer tout le tableau, de la ligne d'en-tête jusqu'à la ligne 28, ainsi que la phrase « Streams **Opus** (quota compté) … », par :

| #   | Fichier                          | Titre                                       | Piste | Prio                 | Jalon          | Prérequis                                | Vague   | Modèle   | Effort    | État                |
| --- | -------------------------------- | ------------------------------------------- | ----- | -------------------- | -------------- | ---------------------------------------- | ------- | -------- | --------- | ------------------- |
| 1   | `prompt-01-socle-e2.md`          | Socle + lot 1 + E2                          | X     | A                    | J1             | —                                        | 0       | Vibe     | High      | fait (J1 PASS)      |
| 2   | `prompt-02-data-d1-d2.md`        | D1 + D2 (dépôt B)                           | X     | A                    | J2             | 1                                        | 1       | Vibe     | High      | fait                |
| 3   | `prompt-03-data-d3.md`           | D3 S&P 500                                  | X     | A                    | J2, J3         | 1                                        | 1       | Vibe     | High      | fait                |
| 4   | `prompt-04-monitors-core.md`     | Surveillance : noyau, portage B             | T→CC  | A                    | J2             | 1, 2                                     | 2       | **Opus** | **max**   | fait                |
| 5   | `prompt-05-injections.md`        | Injections F1–F4, fonds D5/D6               | T→CC  | A                    | J2             | 1, 2, 3                                  | 2       | Vibe     | High      | fait                |
| 6   | `prompt-06-representations-z.md` | Représentations linéaires, interface Z      | T→CC  | A                    | J2             | 2, 3                                     | 2       | **Opus** | **xhigh** | fait                |
| 7   | `prompt-07-pipelines.md`         | Pipelines P2-C, P3-C/D, P3-CS, P7           | T→CC  | A                    | J2             | 4, 5, 6                                  | 3       | **Opus** | **max**   | fait                |
| 8   | `prompt-08-contracts.md`         | Tests de contrat, découplage                | T→CC  | A                    | fusions        | 4–7                                      | 4       | Vibe     | High      | fait                |
| 8b  | `prompt-08b-hygiene.md`          | Hygiène : modules partagés, fixture, écarts | T→CC  | A                    | J2             | 7, 8, 11                                 | 9       | Vibe     | High      | à lancer            |
| 9   | `prompt-09-baf.md`               | BAF                                         | X     | B                    | E9             | 1                                        | 1       | Vibe     | Medium    | fait                |
| 10  | `prompt-10-eurofidai.md`         | EUROFIDAI (D4)                              | X     | B                    | E4-EU          | 1                                        | 1       | Vibe     | High      | fait (D4 construit) |
| 11  | `prompt-11-audit.md`             | Audit informationnel                        | T→CC  | A                    | J2             | 2, 3, 6                                  | 3       | Vibe     | High      | fait                |
| 11b | `../GO-stream-11b.md`            | Audit : bruit de N2, placebo                | T→CC  | A                    | J2             | 11                                       | 3       | Opus     | —         | fait                |
| 12  | `prompt-12-e1.md`                | E1                                          | T→CC  | A                    | J2             | 2–8, 8b, 11                              | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 13  | `prompt-13-e3.md`                | E3                                          | T→CC  | A                    | J2             | 4–8, 8b                                  | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 14  | `prompt-14-ca-tjepa.md`          | CA-T-JEPA (code)                            | T→CC  | A/B                  | J3             | 3, 6, 8, 8b                              | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 15  | `prompt-15-tjepa-baf.md`         | T-JEPA pour BAF (code)                      | T→CC  | B                    | E9             | 9 (torch : 14)                           | 11      | Vibe     | High      | révisé 18/10        |
| 16  | `prompt-16-pretrain-rankme.md`   | Pré-entraînement + RankMe                   | X     | A                    | J3             | 14                                       | 11      | Vibe     | High      | révisé 18/10        |
| 17  | `prompt-17-ipca.md`              | IPCA                                        | T→CC  | A                    | E4, E5, E6     | 3, 6, 8b                                 | 10      | Vibe     | High      | révisé 18/10        |
| 18  | `prompt-18-cddfm.md`             | Adaptateur CD-DFM                           | T→CC  | B                    | E4, E5         | 3, 6, 8b                                 | 11      | Vibe     | High      | révisé 18/10        |
| 19  | `prompt-19-e4-p3kf.md`           | E4 + P3-KF                                  | T→CC  | A/B                  | J4             | 5, 7, 8b, 11, 17                         | 11      | Vibe     | High      | révisé 18/10        |
| 20  | `prompt-20-transmission.md`      | Transmission T(u), dictionnaire             | T→CC  | B/C                  | J4             | 16, 17                                   | 12      | Vibe     | High      | révisé 18/10        |
| 21  | `prompt-21-freeze-runner.md`     | Gel config, runner, figures                 | T→CC  | A                    | J4, J6         | 12, 13                                   | 11      | Vibe     | High      | révisé 18/10        |
| 22  | `prompt-22-e5.md`                | E5                                          | T→CC  | A/B/C                | J4             | 16, 17, 19, 21, 23 (ph. 2)               | 12      | **Opus** | **max**   | révisé 18/10        |
| 23  | `prompt-23-e6.md`                | E6 (ph. 1 linéaire, ph. 2 JEPA)             | T→CC  | A (ph. 1), B (ph. 2) | J3 (ph. 1), J4 | ph. 1 : 5, 7 (17 pour P4-D) ; ph. 2 : 16 | 10 / 12 | Vibe     | High      | révisé 18/10        |
| 24  | `prompt-24-e9.md`                | E9                                          | T→CC  | B                    | J5             | 9, 15                                    | 13      | Vibe     | High      | révisé 18/10        |
| 25  | `prompt-25-e8.md`                | E8                                          | T→CC  | A/B                  | J5             | 8b, 21                                   | 13      | Vibe     | High      | révisé 18/10        |
| 26  | `prompt-26-e7.md`                | E7                                          | T→CC  | C                    | J5             | 16                                       | 12      | Vibe     | Medium    | révisé 18/10        |
| 27  | `prompt-27-e10.md`               | E10                                         | T→CC  | C                    | J5             | 7                                        | 13      | Vibe     | High      | révisé 18/10        |
| 28  | `prompt-28-e11.md`               | E11                                         | T→CC  | C                    | J5             | 5, 7, 14                                 | 13      | Vibe     | Medium    | révisé 18/10        |

Streams **Opus** restants (quota compté) : **12, 13, 14, 22**. Tous les autres : **Vibe**.

**I4.** Avant la section « Lancement (tmux) », ajouter :

```text
## Replanification du 18 octobre 2026 (après les streams 1 à 11 et 11b)

| Vague | Dates            | Streams (parallèles)                                                                                                                     | Déclencheur                                          |
| ----- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 9     | 18–19 oct.       | 8b hygiène                                                                                                                               | immédiat ; bloque 12, 13, 14, 17                     |
| 10    | 19–23 oct.       | 12 E1 et 14 CA-T-JEPA (Opus) ; 13 E3 (Opus, démarrage décalé de 12 h, repli Vibe High si le quota Opus sature) ; 17 IPCA ; 23 E6 phase 1 | 8b fusionné                                          |
| 11    | 24 oct.–1er nov. | 16 pré-entraînement ; 21 gel et runner ; 19 E4 ; 18 CD-DFM ; 15 T-JEPA BAF                                                               | 14 (pour 15 et 16), 12 et 13 (pour 21), 17 (pour 19) |
| 12    | 2–8 nov.         | 22 E5 ; 23 E6 phase 2 ; 20 transmission ; 26 E7                                                                                          | 16 et 21 fusionnés ; gel au J4                       |
| 13    | 9–15 nov.        | 25 E8 ; 24 E9 ; 27 E10 ; 28 E11                                                                                                          | gel J4 (pour 25), 15 (pour 24)                       |

Jalons : J2 = résumés d'E1 et d'E3 ; J3 = porte RankMe du stream 16 et E6 phase 1 (évidence pour
la contingence C1) ; J4 = gel du stream 21 et porte d'E5.
```

### 2.3 `prompts/Orchestration_Streams_v5.md`

Insérer sous le titre :
```text
> Statut (2026-10-18) : les vagues de ce document sont historiques. Le routage en vigueur est la table de
> `prompts/streams/INDEX.md` et sa section « Replanification du 18 octobre 2026 ».
```

### 2.4 `docs/DEVIATIONS.md`

Les entrées `C-D3-survivor-correction` et `C-D4-survivor` sont ajoutées par le stream 8b, avec le texte fourni dans son prompt.

## 3. Prompts

### 3.1 Nouveau : `prompts/streams/prompt-08b-hygiene.md`

### 3.2 Mise à jour des prompts existants
#### 3.2.1 `prompts/streams/prompt-12-e1.md` a été mis à jour
#### 3.2.2 `prompts/streams/prompt-13-e3.md` a été mis à jour
#### 3.2.3 `prompts/streams/prompt-14-ca-tjepa.md` a été mis à jour
#### 3.2.4 `prompts/streams/prompt-19-e4-p3kf.md` a été mis à jour
#### 3.2.5 `prompts/streams/prompt-22-e5.md` a été mis à jour
#### 3.2.6 `prompts/streams/prompt-23-e6.md` a été mis à jour
#### 3.2.6 `prompts/streams/prompt-25-e8.md` a été mis à jour

### 3.3 Modifications ciblées

**`prompt-15-tjepa-baf.md`**

Remplacer :
```text
2. Entraîner sur les mois 0–2 de la variante Base (prétraitement `preproc.json`).
```
par :
```text
2. Entraîner sur les mois 0–2 de la variante Base (`preproc.json` : catégories inconnues codées −1 ; `device_fraud_count`, constant, exclu des jetons ; sentinelles −1 déjà standardisées). Licence du jeu : CC BY 4.0.
```

Remplacer :
```text
4. Extraire les plongements des mois 0–7 vers `data/derived/d7_baf/z_<hash>.npz`, avec le JSON de l'interface Z.
```
par :
```text
4. Extraire les plongements des mois 0–7 vers `data/derived/d7_baf/z_<hash>.npz`, avec le JSON de l'interface Z. Les lignes ne sont pas des jours : `dates` est remplacé par (`month`, `row`), écart `C-Z-baf`. Enregistrer la représentation par une entrée paresseuse du registre : torch n'est pas importé à l'import de `jepadrift.representations`.
```

Remplacer :
```text
- CPU accepté ; déterminisme comme au prompt 14.
```
par :
```text
- CPU ; torch installé dans `.venv` selon `CLAUDE.md` (par le stream 14 ; si ce stream démarre avant, l'installer à l'identique et réconcilier `requirements.lock` au rebase) ; déterminisme comme au prompt 14.
```

**`prompt-16-pretrain-rankme.md`**

Remplacer :
```text
1. Entraîner, sur `d3_239` (segment `pretrain`), les objectifs `jepa`, `mae` et `temporal`, chacun avec 3 graines (0, 1, 2) ; enregistrer les points de contrôle.
```
par :
```text
1. Entraîner, sur `d3_239` (segment `pretrain`), les objectifs `jepa`, `mae` et `temporal`, chacun avec 3 graines (0, 1, 2) ; une exécution par processus et un thread par exécution (`--jobs`, résultats indépendants du nombre de processus) ; enregistrer les points de contrôle. La lecture D ∈ {2, 4, 8, 16} est une ACP post hoc : un seul entraînement par (objectif, graine).
```

Remplacer :
```text
CPU ; exécutions séquentielles déterministes ; durée totale consignée.
```
par :
```text
CPU (48 cœurs) ; exécutions parallèles déterministes, une par processus ; durée totale consignée ; contrats, dont les quatre gardes torch, au vert sur chaque point de contrôle extrait.
```

Remplacer :
```text
python experiments/jepa_campaign.py --dataset d3_239 --seeds 0 1 2 --objectives jepa mae temporal
```
par :
```text
python experiments/jepa_campaign.py --dataset d3_239 --seeds 0 1 2 --objectives jepa mae temporal --jobs 9
```

**`prompt-17-ipca.md`**

Remplacer :
```text
2. Apprendre Γ sur `pretrain` ; choisir K ∈ {1, …, 6} par R² hors échantillon sur `calib` ; blanchir f_t sur `calib`.
```
par :
```text
2. Caractéristiques : `data_loader.chars.load_chars_tensor` (stream 8b) ; 15 colonnes sur D3 (4 continues, 11 GICS), 4 sur D4 ; NaN → 0 comptés. `d3_500` et D4 sont déséquilibrés : régressions transversales restreintes aux titres `in_universe` du jour, sans imputation de rendement. Apprendre Γ sur `pretrain` ; choisir K ∈ {1, …, 6} par R² hors échantillon sur `calib` ; blanchir f_t sur `calib`.
```

Remplacer :
```text
`d3_239` et `d3_500` avec leurs caractéristiques ; interface Z ; `CLAUDE.md`.
```
par :
```text
`d3_239`, `d3_500` (et D4) avec leurs caractéristiques ; interface Z ; stream 8b ; `CLAUDE.md`.
```

**`prompt-18-cddfm.md`**

Remplacer :
```text
1. Cloner `https://github.com/alexouadi/CD-DFM`, épingler le commit, lire la licence et les dépendances. Installer dans `external/cddfm/.venv` si les dépendances entrent en conflit.
```
par :
```text
1. Réutiliser le clone `external/cd-dfm/` du stream 3, dont le commit est épinglé dans `data/derived/MANIFEST.json` ; ne pas recloner. Lire la licence et les dépendances ; le README indique que le panel d'origine n'est pas redistribuable. Installer dans `external/cddfm-venv/` si ses dépendances (torch notamment) entrent en conflit avec `.venv`.
```

Remplacer :
```text
2. Adapter les entrées : caractéristiques de `d3_239` (prompt 3) au format attendu.
```
par :
```text
2. Adapter les entrées : caractéristiques de `d3_239`, lues par `data_loader.chars.load_chars_tensor` (stream 8b), au format attendu.
```

**`prompt-20-transmission.md`**

Remplacer :
```text
   - (B) mélange isotrope sur le sous-espace résiduel de dimension D ;
   - mesurer cos²ϑ et les délais, puis comparer à `floors.dictionary_multiplier` et `floors.mixture_multiplier` (angles de bascule).
```
par :
```text
   - (B) mélange isotrope sur le sous-espace résiduel de dimension D, valide seulement si les coordonnées sont indépendantes : le comparer sur fonds D5 (coordonnées indépendantes) et, sur D6, rapporter l'état de la porte d'indépendance corrigée de la multiplicité (prompt 12) ;
   - mesurer cos²ϑ et les délais, puis comparer à `floors.dictionary_multiplier` et `floors.mixture_multiplier` (angles de bascule) ; lecture anytime-valid à γ_H = H/α (`CLAUDE.md`).
```

**`prompt-21-freeze-runner.md`**

Remplacer :
```text
   - Point d'entrée unique : `--config configs/<stream>.yaml`.
```
par :
```text
   - Point d'entrée unique : `--config configs/<stream>.yaml`. Il appelle le `main(argv)` des scripts existants (`experiments/e1_problem.py`, `e3_calibration.py`, …) sans les réimplémenter.
```

Remplacer :
```text
   - Écrit `configs/FROZEN.json` (empreintes de toutes les configurations d'expérience plus commit).
```
par :
```text
   - Écrit `configs/FROZEN.json` : empreintes de toutes les configurations d'expérience, commit, et empreintes de `data/derived/MANIFEST.json` et `docs/manifests/d4_manifest.json` ; cible `make freeze`.
```

Remplacer :
```text
Les outils ci-dessus, `configs/FROZEN.json` (au J4), `docs/MAPPING.md` initial, `tests/test_tools.py`.
```
par :
```text
Les outils ci-dessus, `configs/FROZEN.json` (au J4), `docs/MAPPING.md` initialisé avec les nombres déjà cités (E2/J1, identités R01/R08/R15, audit, E1, E3), `tests/test_tools.py`.
```

Remplacer :
```text
Aucune figure lue depuis un état en mémoire ; aucun nombre saisi à la main dans `paper/`.
```
par :
```text
Aucune figure lue depuis un état en mémoire ; aucun nombre saisi à la main dans `paper/`. `results/e2/e2_cells.csv` est en fins de ligne CRLF (empreinte de référence) : ne pas le normaliser ; `make j1` réécrit la ligne de durée du résumé. Fusion requise avant le stream 22 et avant toute exécution sur la fenêtre de test.
```

**`prompt-24-e9.md`**

Remplacer :
```text
   - Score de non-conformité : distance au 10ᵉ plus proche voisin dans un échantillon de référence (50 000 lignes des mois 0–2), sur les plongements T-JEPA, ACP et bruts.
```
par :
```text
   - Score de non-conformité : distance au 10ᵉ plus proche voisin dans un échantillon de référence (50 000 lignes des mois 0–2), sur les plongements T-JEPA, ACP et bruts (`device_fraud_count`, constant, exclu).
   - Échangeabilité : tester l'ordre intra-mois (test des runs et autocorrélation des scores sur le mois 3) ; en cas de rejet, permuter les lignes de chaque mois avec une graine fixe et consigner `C-BAF-order`.
```

Remplacer :
```text
   - Flux d'erreur binaire au seuil choisi sur le mois 3 ; taux nul q̂ estimé sur le mois 3.
```
par :
```text
   - Flux d'erreur binaire au seuil choisi sur le mois 3 ; taux nul q̂ estimé sur le mois 3 (prévalence de fraude de 0,87 % à 1,47 % selon le mois, `results/data/baf_profile.csv`).
```

**`prompt-26-e7.md`**

Remplacer :
```text
2. **Comparaison avec P5-C gelé**, sur F1 et F2 injectées sur fonds D6 de `d3_239`, avec τ_a/τ_γ ∈ {0.5, 1, 2, 4, 8}. Comparer les délais mesurés à la prédiction calculée avec le τ_a mesuré (`floors.absorption_delay`).
3. **Vieillissement** : sous H₀, ARL₀ par tranche annuelle depuis la fin du pré-entraînement, sur fonds symétrisés.
```
par :
```text
2. **Comparaison avec P5-C gelé**, sur F1 et F2 injectées sur fonds D6 de `d3_239`, avec τ_a/τ_γ ∈ {0.5, 1, 2, 4, 8}, en lecture anytime-valid à γ_H = H/α (`CLAUDE.md`). Comparer les délais mesurés à la prédiction calculée avec le τ_a mesuré (`floors.absorption_delay`).
3. **Vieillissement** : sous H₀, ARL₀ par tranche annuelle depuis la fin du pré-entraînement, sur fonds symétrisés. Avant J4, tranches 2016–2019 seulement ; 2020 et au-delà uniquement avec la configuration gelée.
```

**`prompt-27-e10.md`**

Remplacer :
```text
   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4).
```
par :
```text
   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4), avec ses violations naturelles mesurées par l'audit (symétrie rejetée sur PC1, PC2, PC3 et `rev_21` selon le jeu, `CLAUDE.md`) et ses rendements nuls (2 864 sur D2 avant 2020, tranchés par pièce).
```

Remplacer :
```text
3. **Mesures** : FPR contre niveau nominal, G_ADD sur F1 et F2.
```
par :
```text
3. **Mesures** : FPR contre niveau nominal, G_ADD sur F1 et F2 (lecture γ_H = H/α).
```

**`prompt-28-e11.md`**

Remplacer :
```text
1. Télécharger le jeu depuis le dépôt UCI : chercher « ElectricityLoadDiagrams20112014 » sur archive.ics.uci.edu et consigner l'URL exacte. Agréger au pas quotidien ; prendre la log-différence de la charge quotidienne par client.
```
par :
```text
1. Télécharger le jeu depuis le dépôt UCI : chercher « ElectricityLoadDiagrams20112014 » sur archive.ics.uci.edu et consigner l'URL exacte. Agréger au pas quotidien ; prendre la log-différence de la charge quotidienne par client. Dans un worktree, exposer `data/raw/electricity` par un lien absolu (`CLAUDE.md`).
```

Remplacer :
```text
5. Mesurer G_ADD et le FPR.
```
par :
```text
5. Mesurer G_ADD (lecture γ_H = H/α) et le FPR.
```

## 4. Ordre d'application

1. Les huit prompts complets (8b, 12, 13, 14, 19, 22, 23, 25) ont déjà été enregistrés. Il reste à appliquer les dix modifications ciblées dans `prompts/streams/`.
2. Appliquer les modifications de `CLAUDE.md`, `INDEX.md` et `Orchestration_Streams_v5.md`, en un commit `docs(config): …` du chercheur, sans fichier de code.

**[Strategic Advice]**

- **Sources.** Tout vient de la mémoire du projet (synchronisation GitHub) ; le miroir public n'a pas été consulté. J'ai lu en détail les wrapups 1 à 11 et 11b, `docs/DEVIATIONS.md`, `docs/sections/{pipelines,interface_Z,articleB_deviations_digest}.md`, AGENTS.md, INDEX.md, le Makefile, les hooks et les prompts 12 à 28. Les modules de code et une partie des plans et GO n'ont été lus que par extraits.
- **Ancres de remplacement.** Les textes « à remplacer » sont copiés des extraits de la mémoire. Si un remplacement échoue sur un retour à la ligne, l'appliquer par le sens et contrôler avec `git diff`.
- **Décisions à confirmer au GO du stream 12** :
  - lecture principale γ_H = H/α ;
  - SR ∈ {2, 4, 8} ;
  - F2 limité à D3 et D4 ;
  - P3-D à H = 750 ;
  - grille d'amplitude réglée sur D6 avant 2020 (degré de liberté consigné) ;
  - mélange de P3-C corrigé par Holm, en diagnostic seulement : sa validité n'est qu'approchée.
- **Risque sur J2 (iii).**
  - Le critère peut échouer à cause de la conception du dictionnaire, sans absence d'information.
  - Règle de décision proposée : un échec avec un a_max faible et une pente positive de P3-CS (b) ou du mélange relève du détecteur, pas de C1. Un échec avec un a_max élevé déclenche C1, avec E6 phase 1 comme preuve de repli.
- **Théorie.** Sur fonds réels, les prévisions de la Prop. 3 doivent passer par le multiplicateur de dictionnaire avec l'alignement mesuré. Un mélange valide sous dépendance, restreint au sous-espace des caractéristiques, est la piste naturelle pour P4 et P5. Ces deux points sont à intégrer à mon lot 3 (§1 v0, Tableaux 1–3, T6–T7), qui reste à livrer côté piste T.
- **Article B.** La sélection des frontières établie par le stream 11b fait de la part hors budget du recensement (80,3 %) une borne inférieure. L'argument est utilisable dans la version caméra.
- **Non vérifiés.**
  - La version exacte de la roue CPU de torch compatible avec numpy 2.4.4.
  - Si `tests/test_decoupling.py` signale les imports paresseux de `jepadrift.jepa` depuis `representations/extract.py`.
  - La référence Kuncheva (2013).
- **Écarts au format demandé.** Prompts révisés livrés en remplacements complets ou ciblés, non en diff unifié ; le prompt 8b est ajouté hors numérotation d'origine pour respecter l'ordre des dépendances.