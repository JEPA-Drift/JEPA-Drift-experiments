# Plan stream 31 — v2 : lot 1 outillage des prompts, puis lot 2 contrats PCA (QA)

> Exécutant : superpowers:executing-plans, en exécution native **sans sous-agent**, et superpowers:test-driven-development. Cases `- [ ]` pour le suivi.

**Statut : lot 1 intégré et poussé dans 20ad9e860a58373ec85405de6ee19a68322dd02e ; lot 2 mesuré à 44/0 après le correctif D7b sous plan et GO séparés ; clôture Git en revue (§11).**
- Il y aura deux GO d'exécution distincts. Le **GO outillage** ouvre le lot 1. Le **GO QA** ouvre le lot 2, et seulement après revue et commit du lot 1 par Codex.
- Choisir « modifier le plan » ou approuver cet écran ne donne aucune permission d'implémenter.
- Le v1 est archivé par Codex : `logs/orchestration_reprise_20261106/plan-v1.md`, SHA-256 `34f07a35ee96abe7e24eb268224b2d75a2da6d653f214ef4c494c5ea437fa01d`.
- Revue intégrée : `prompts/NO-GO-stream-31.md`.
- `PLAN.md` n'est ni recopié ni modifié. Seule son empreinte est contrôlée.

**Objectif.**
- Lot 1 : `tools/check_prompts.py` découvre les 33 prompts, synchronise le master en ajout pur et de façon idempotente, et échoue sur un master tronqué, un fichier attendu absent ou modifié, un titre dupliqué ou un ensemble incomplet.
- Lot 2 : `tests/test_pca_drift_contracts.py` vérifie chaque contrat du prompt 31, avec des références indépendantes et des témoins négatifs non tautologiques, sur les API réelles et les artefacts scellés.

**Pile.** `.venv/bin/python` (3.12.9) et `.venv/bin/make`, avec `PATH="$PWD/.venv/bin:$PATH"`. numpy 2.4.4, pandas 3.0.6, matplotlib 3.11.2 (Agg), pytest. Versions inchangées. Aucun chemin absolu personnel dans ce plan ni dans les commandes suivies.

**Spécification.** `prompts/streams/31_STREAM_PCA_DRIFT_CONTRACTS.md`, la demande `logs/orchestration_reprise_20261106/plan-request.md`, le NO-GO ci-dessus, et les contrats de schéma `docs/sections/pca_drift_{benchmark,tables,figures}.md`.

## 0. Journal de révision v1 → v2

| NO-GO | Intégration v2 |
|---|---|
| Corr. 1 (E1, indexation) | §4.5 E1 : round-trip `S_json([i - 1 for i in parse_S(text, nmax)]) == text` |
| Corr. 2 (E3, domaine SPD) | §4.5 E3 et §6 : rejets documentés uniquement (signe du déterminant, finitude, tolérance `clip_kl` de 1e-12). Limite SPD consignée comme observation. |
| Corr. 3 (A18) | §4.1 A15 : recette du rang et flux des données recalculés depuis les trials. Plus d'interdiction `threshold != log(γ)`. |
| Corr. 4 (B1/B3) | §4.2 : compteurs « mesuré » et « bloqué NA » séparés. B3 filtré sur `row_kind=SELECTED`, dans le domaine additif plug-in. |
| Corr. 5 (F-fake) | §4.0 : effectifs propres au calendrier factice. Les 941 dates réelles sont un contrôle de métadonnées distinct (C6). |
| Corr. 6 (D7a) | §4.4 D7a : l'annotation suit valeurs et statut. Aucune interdiction de chaînes générales. |
| Corr. 7 (outillage minimal) | §3 : sémantique générale conservée ; migration contrôlée ; arrêt de l'étendue sur l'ouverture de fence ; CLI vérifiant 33 IDs ; pas de normalisation des fins de ligne. |
| Corr. 8 (ordre et arrêt) | Lot 1 d'abord, puis STOP et commit Codex. Lot 2 sous GO distinct ; D7b est un FAIL réel, suivi d'un STOP (§5). |
| Corr. 9 (portabilité) | `.venv/bin/*`, chemins relatifs, `PLAN.md` intact |
| Corr. 10 (TDD sur l'existant) | §5 : témoins en mémoire ou en `tmp_path`. Au plus 3 corrections tracées d'une erreur QA. Défaut confirmé → STOP. |
| Q1–Q12 | Intégrées : Q1 §4.0 ; Q2–Q3 §4.0 et C6 ; Q4 G1 ; Q5 D7b ; Q6 A5 ; Q7 B4 et C7 ; Q8 §4.6 ; Q9 B3 ; Q10–Q11 §3 ; Q12 D4. |

## 1. Base vérifiée (lecture seule)

**État du dépôt**
- HEAD : `a0c576e13e8e647dfd61350eec52058ffc794dbf`.
- Fichiers non suivis étrangers, appartenant à Codex et non touchés : `docs/audits/streams_01_27_relevance_2026_11_06.md` et `prompts/NO-GO-stream-31.md`.
- `configs/FROZEN.json` est absent.

**`make check` de référence (Codex)** : sortie 0. Pyflakes propre, 37 passés (36,66 s), puis 538 passés et 5 ignorés (450,90 s).

**Prompts et master**
- Le master `prompts/Prompts_Claude_Code_v5.md` compte 29 blocs : 28 blocs clôturés et le bloc 8b, non clôturé, en fin de fichier. On y trouve 28 ouvertures `` ````markdown `` et 28 lignes de fermeture. Il ne contient aucun octet CR, et les 33 fichiers de prompts non plus.
- Selon Codex, les 29 étendues historiques extraites par `blocks()` égalent exactement leurs sources, après retrait des seuls `\n` finaux.
- Dans l'ajout en mémoire des 4 prompts PCA, les longueurs successives valent 136069, puis 184889, puis **184875** au deuxième `sync()` : celui-ci n'est pas idempotent, car 8b absorbe l'ouverture de fence suivante.
- Les 4 prompts PCA (`28-PCA`, `29`, `30`, `31`) sont absents du master. `prompt-28-e11.md` garde l'ID `28`.

**Historique E2 / E3**
- E2 : `e315e537…0823`, identique sur disque et dans l'index, avec 47 CRLF ; l'attribut est `-text`.
- D8 : `C-e3-d8-fail` est présent. `results/e3/e3_overshoot.csv` a le SHA `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, et la ligne `iid/first_order_d1_l3` primary porte `rel_gap 0.052833421330517272` et `gate FAIL`.

**Run full et code**
- Le manifeste full a le SHA `3b2299bc…2f47` et `run_fingerprint` `ea702d03…`.
- Son `trials.csv` est déclaré à 48 317 020 octets, 716 000 lignes, SHA `40b5f891…`. Le fichier est absent ici, mais présent dans le worktree voisin `../JEPA-full-2000/`.
- Hashes du code : runner `8324b47b…`, assembleur `13d386fe…`, traceur `c40a5e77…`, égaux aux enregistrements des figures corrigées.

**Défaut établi.** `experiments/figures/plot_figure_1.py:582` imprime « (n = 40) » en dur. Codex a constaté ce texte dans le PDF full corrigé `Figure_1_mean.pdf`, dont le manifeste annonce 2000 trajectoires par rôle.

**Écart déclaré en v1, maintenu.** Une exécution Python de `blocks/check` en mémoire, sans écriture, a eu lieu pendant la lecture.

## 2. Contraintes globales

- **Préfixe d'environnement de chaque commande** : `export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`.
- **Interdits.** Aucun rerun full ou smoke de production, aucune expérience nouvelle, aucun rendement réel, aucune donnée réelle post-2019, aucun travail JEPA/VAE/J4, aucune dépendance modifiée.
- **Fichiers intouchables.** Le runner, l'assembleur, le traceur, les configurations, `results/`, `figures/`, `docs/DEVIATIONS.md`, `CLAUDE.md`, `PLAN.md` et `prompts/streams/` ne sont jamais modifiés. Aucune correction producteur pour faire passer un test.
- **Pas de xfail ni de skip pour masquer un contrat.** Seul G1 peut être BLOCKED, et seulement si le chemin local est absent.
- **Git et outils exclus.** Aucune opération Git par Claude ; Codex possède Git, le GO et la revue. Aucune opération sur les worktrees voisins autre que la lecture de G1. Graphify et jCodeMunch ne sont pas sollicités.
- **Langues.** Code, tests, rapports et wrapup en anglais ; plan en français.

## 3. LOT 1 — Outillage des prompts (exécution bornée, GO outillage distinct)

### 3.1 Fichiers possédés

| Fichier | Opération |
|---|---|
| `tools/check_prompts.py` | modification |
| `tests/test_check_prompts.py` | ajouts ; les 2 tests existants restent inchangés |
| `prompts/Prompts_Claude_Code_v5.md` | **uniquement** par `--sync-master`, en ajout pur |
| `prompts/plans/plan-31.md` | création : ce v2, plus « Décision GO intégrée — lot 1 » |
| `prompts/wrapups/wrapup-31.md` | création : état du lot 1 avant le commit Codex (QR4) |
| `logs/prompts_tooling/*.log` | journaux ignorés par Git : RED, GREEN, migration, make check |

### 3.2 Règles (sémantique générale conservée, Q10 minimale)

- **R-O1 Découverte (CLI).** `prompt-*.md` triés, puis `[0-9][0-9]_STREAM_PCA_DRIFT_*.md` triés : 29 + 4 fichiers. Les fichiers 00/01/07/09–12 restent hors du motif. Les fonctions génériques (`check`, `sync`, `blocks`) prennent toujours un dictionnaire `{nom: texte}`.
- **R-O2 Titres.** Chaque fichier commence par `## PROMPT <id> —`, vérifié dans le chemin de contrôle comme dans celui de la synchronisation. Un ID en double entre fichiers lève `ValueError` en nommant les deux fichiers. Un titre en double dans le master lève toujours `ValueError`. Aucun ID n'est renommé ni réattribué : `28` et `28-PCA` sont distincts.
- **R-O3 Extraction.** L'étendue d'un bloc s'arrête au premier des trois repères : fence de fermeture, titre suivant, ou **ligne d'ouverture `` ````markdown `` suivante**. Ce dernier repère corrige le cas 8b.
- **R-O4 Présence exacte.** Le bloc master de chaque ID discret doit égaler **octet pour octet** le texte du fichier, sans ses `\n` finaux. Les fins de ligne ne sont pas normalisées : lecture `read_bytes().decode("utf-8")`, écriture `write_bytes(...)`. Cette règle inclut la présence exacte du texte source. Elle détecte aussi un fichier source tronqué, qui reste une sous-chaîne et passe donc un simple test d'inclusion (QR1).
- **R-O5 Master tronqué.** Les fences doivent être équilibrées : autant d'ouvertures `^````markdown$` que de fermetures `````$` (28/28 aujourd'hui, 32/32 après migration) (QR2).
- **R-O6 Ensemble attendu (CLI seulement).**
  - `EXPECTED_IDS` contient les 33 IDs : `1`…`28`, `8b`, `28-PCA`, `29`, `30`, `31`.
  - `main()` exige que les IDs découverts égalent `EXPECTED_IDS`, en listant les IDs manquants et inattendus.
  - Sortie : `prompts-check: 33/33 (29 prompt-*.md + 4 *_STREAM_PCA_DRIFT_*.md: 28-PCA, 29, 30, 31)`. Sinon, code 1.
  - Un `ValueError` (titre absent ou dupliqué) est imprimé `prompts-check: error: …`, code 1.
- **R-O7 Synchronisation.** La sémantique générale est inchangée : chaque bloc d'ID découvert est remplacé, et les manquants sont ajoutés en fin avec fence. Seul ajout : une post-condition. Si le résultat viole R-O2, R-O4 ou R-O5, rien n'est écrit et le code vaut 1 (QR3). Aucune restriction permanente sur les blocs historiques. Leur préservation est un **contrôle de migration** (T4 et les commandes de §3.5).

### 3.3 Tests RED, à écrire d'abord dans `tests/test_check_prompts.py`

| Test | Assertions | Cause RED attendue sur le code actuel |
|---|---|---|
| T1 `test_cli_discovers_the_33_expected_ids` (dépôt réel, lecture seule) | `discover()` renvoie 29 `prompt-*.md` et 4 fichiers PCA. Les IDs égalent `EXPECTED_IDS`. `prompt-28-e11.md` donne `28` ; `28_STREAM_PCA_DRIFT_RUNNER.md` donne `28-PCA`. | `discover` et `EXPECTED_IDS` absents |
| T2 `test_duplicate_or_missing_titles_rejected` (petits dictionnaires) | Deux fichiers de même ID lèvent `ValueError` nommant les deux. Un fichier sans titre lève `ValueError` dans le chemin de contrôle. | Aujourd'hui, `sync` écrase le doublon en silence et `check` ignore les titres |
| T3 `test_sync_idempotent_after_unfenced_legacy_tail` (synthétique : bloc historique non clôturé en fin, plus un prompt nouveau) | `sync(sync(M)) == sync(M)` ; ouvertures = fermetures | Ouverture absorbée |
| T4 `test_real_master_sync_append_only_idempotent_history_unchanged` (master réel et `discover()`, en mémoire, indépendant de l'état du disque) | `s1 = sync(M)` vérifie `s1.startswith(M)`. `sync(s1) == s1`. Les 29 blocs historiques de `s1` égalent ceux de `M` et leurs fichiers. `check(s1)` est vide, les fences sont équilibrées, les IDs de `s1` contiennent `EXPECTED_IDS`. | 184889 → 184875 |
| T5 `test_check_fails_on_modified_truncated_missing_or_incomplete` (sur `s1` en mémoire) | (a) 1 octet modifié dans un prompt PCA → listé. (b) Dernière ligne d'un prompt PCA retirée → listé. (c) Un fichier attendu retiré de la découverte → l'ensemble est incomplet et l'ID est nommé. (d) Master coupé avant la fermeture finale → fences déséquilibrées. (e) Master coupé dans un bloc historique → ce prompt est listé. | (b), (c), (d) non détectés |
| T6 `test_no_hidden_line_ending_normalization` (`tmp_path`) | Un fichier de prompt écrit en CRLF face à un master en LF fait échouer le contrôle. La synchronisation écrit les octets exacts. | `read_text` normalise le CRLF |
| T7 `test_main_reports_counts_and_exit_codes` (`STREAMS`, `MASTER` et `EXPECTED_IDS` patchés vers un petit jeu en `tmp_path`) | Avant sync : code 1, `n/N` et noms manquants. `--sync-master` : `rewritten`, code 0. Deuxième passage : `unchanged`, code 0. Les fichiers du dépôt sont intacts. | Découverte et ensemble attendu absents |

### 3.4 Étapes du lot 1 (après GO outillage)

- [ ] **Étape 0 — Pré-vol et persistance du plan.**
  - Vérifier que HEAD et l'état correspondent à §1 (lignes étrangères notées) et que le SHA de `PLAN.md` vaut `ed14c47a8df2898ec2cba4662fe7b39a0f0fd8316b9f9eaa299a31ae7b0730ac`.
  - Écrire `prompts/plans/plan-31.md` : ce v2, plus « Décision GO intégrée — lot 1 ».
- [ ] **Étape 1 — RED.** Écrire T1–T7, puis lancer `.venv/bin/python -m pytest -q tests/test_check_prompts.py 2>&1 | tee logs/prompts_tooling/red.log`. Attendu : code 1. T1–T7 échouent pour les causes du §3.3 ; les 2 tests existants passent.
- [ ] **Étape 2 — GREEN, changement minimal de `tools/check_prompts.py`.**
  - Ajouts : `PATTERNS`, `EXPECTED_IDS`, `OPEN`, `discover(streams=STREAMS)`, `prompt_ids(prompts)` (R-O2) et `fences_balanced(master)`.
  - `blocks()` s'arrête à `OPEN` ; `check()` passe en exacte (R-O4) ; `sync()` reçoit la post-condition ; `main()` applique R-O6. Lecture et écriture se font en octets.
  - La docstring est mise à jour. Aucune nouvelle dépendance.
- [ ] **Étape 3 — Vérification GREEN.**
  - `.venv/bin/python -m pytest -q tests/test_check_prompts.py 2>&1 | tee logs/prompts_tooling/green.log` : code 0, 9 passés.
  - `.venv/bin/pyflakes tools/check_prompts.py tests/test_check_prompts.py` : sortie vide.
- [ ] **Étape 4 — Migration du master** (§3.5).
- [ ] **Étape 5 — Contrôle global.** `.venv/bin/make check 2>&1 | tee logs/prompts_tooling/make_check.log` : code 0 ; 37 passés, puis 538 + 7 passés et 5 ignorés.
- [ ] **Étape 6 — Wrapup et STOP.**
  - Écrire `prompts/wrapups/wrapup-31.md`, état du lot 1, en anglais.
  - Rapport au terminal : sorties RED et GREEN, migration, make check, SHA avant et après du master, liste exacte de `git status`.
  - **STOP** : revue et commit indépendants par Codex. Aucun code QA avant le GO QA.

### 3.5 Commandes de migration (chaque divergence fait échouer)

```bash
mkdir -p logs/prompts_tooling
.venv/bin/python tools/check_prompts.py > logs/prompts_tooling/pre.log; test $? -eq 1    # 29/33, liste les 4 prompts PCA
.venv/bin/python tools/check_prompts.py --sync-master | tee logs/prompts_tooling/sync1.log
grep -qx 'sync-master: master rewritten' logs/prompts_tooling/sync1.log
grep -q '^prompts-check: 33/33 ' logs/prompts_tooling/sync1.log
cmp <(git show HEAD:prompts/Prompts_Claude_Code_v5.md) \
    <(head -c "$(git cat-file -s HEAD:prompts/Prompts_Claude_Code_v5.md)" prompts/Prompts_Claude_Code_v5.md)    # ajout pur
.venv/bin/python tools/check_prompts.py --sync-master | grep -qx 'sync-master: master unchanged'    # idempotence sur disque
.venv/bin/make prompts-check
git diff --quiet HEAD -- prompts/streams experiments jepadrift configs results docs/DEVIATIONS.md CLAUDE.md
test "$(sha256sum < PLAN.md | cut -d' ' -f1)" = ed14c47a8df2898ec2cba4662fe7b39a0f0fd8316b9f9eaa299a31ae7b0730ac
```

`git status --porcelain` attendu pour mes fichiers, à l'exclusion des lignes étrangères notées à l'étape 0, qui restent inchangées :

```
 M prompts/Prompts_Claude_Code_v5.md
 M tests/test_check_prompts.py
 M tools/check_prompts.py
?? prompts/plans/plan-31.md
?? prompts/wrapups/wrapup-31.md
```

`CLAUDE.md` décrit encore des « exact substrings » : je le signale à Codex sans le modifier.

## 4. LOT 2 — Contrats PCA (QA) : plan complet, GO QA distinct, après commit du lot 1

### 4.0 Principes, fixtures, recouvrement

**Fichiers possédés.**
- `tests/test_pca_drift_contracts.py` ;
- `docs/audits/PCA_CONTRACTS_VALIDATION.md` (Q8) ;
- `prompts/wrapups/wrapup-31.md`, actualisé seulement si Codex le demande, car aucun commit QA n'est prévu en état STOP (QR6) ;
- journaux ignorés `logs/pca_drift_contracts/`.

Aucun fichier de fixture n'est prévu sous `tests/`.

**Recouvrement (Q1).** Avant chaque groupe, je cherche par `grep -n` dans `tests/test_pca_drift_{benchmark,tables}.py` et `tests/test_plot_figure_1.py` si une assertion identique existe déjà. Si elle existe avec la même référence, je ne l'écris pas et la matrice du rapport la marque « couvert par <test> ». Seuls les tests marqués [NOUVEAU] ou [EXTENSION] apportent une référence, un témoin ou un artefact nouveau ; les tests [CONDITIONNEL] sont abandonnés si le recouvrement est constaté (QR5). La QA n'importe aucun module de test producteur.

**Fixtures** (Q2 : fixtures unitaires synthétiques, très petites, avec oracle, sans ligne réelle).
- **F-tiny.** `pdb.load_config(CONFIG, "smoke")`, puis N=24, H=12, T_fit=80, nmax=6, n_center=6, n_cal=19, n_null=8, n_alt=8, minibatch=3, cov_search_chunk=7, `C_axes=[3,5]`. Ensuite `pdb.run_benchmark(cfg, "synthetic", tmp/out, tmp/log)` doit renvoyer 0.
- **F-poison.** F-tiny avec `draw_path` patché : `holdout_null` et `alternative` multipliés par 10.
- **F-fake.** Panel daté factice en `tmp_path` :
  - N = 21, sur un calendrier de jours ouvrés 2004-12-31..2023-12-29 qui exclut le 2020-01-01 ;
  - `splits.yaml` et `MANIFEST.json` locaux ;
  - `expected_calib_rows` **calculé sur ce calendrier** avec `segment_rows`, et non 941 (corr. 5) ;
  - lignes post-2019 en NaN (variante a) ou à 1e6 (variante b) ;
  - `run_benchmark(…, "both")` avec `mode = "full"` exigé par l’API, sur les seuls petits effectifs factices ; aucun run de production ;
  - chaque chemin de rendements pointe explicitement vers `tmp_path`, sans lecture de rendements du dépôt.
- **Artefacts scellés, lus en place :**

  | Alias | Chemin sous `results/pca_drift_benchmark/` |
  |---|---|
  | `SMOKE` | `smoke_predictive_v2_closeout/` (7 fichiers) |
  | `FULL` | `full_2000_20261101/` (6 fichiers) |
  | `TAB_SMOKE`, `TAB_FULL` | `tables/…` |
  | `FIG_SMOKE_FIX`, `FIG_FULL_FIX` | `figures/*_fix_smoke_no_claims/` |

  Les mutations se font sur `copy.deepcopy(pdt.load_run(SMOKE))` ou sur des copies en `tmp_path` (corr. 10).

**Comparaisons.** Les égalités d'artefacts se font en texte (`dtype=str`, `keep_default_na=False`), jamais sur des chaînes arrondies.

**Budget.** Au plus 60 s, hors G1. Aucune figure n'est rendue sur disque ; au plus 3 `render_figure` en mémoire.

### 4.1 A — Mathématiques (hors ligne, `SeedSequence([31, …])` locales)

**A1 [EXTENSION] `test_mean_kl_eigenbasis_identity_and_order_counterexamples`**
- Σ est SPD, de taille 6×6, avec cond ≤ 10. `kl_mean(Δ,Σ)` égale 0,5‖L⁻¹Δ‖² (Cholesky de la QA). `q_plugin(VᵀΔ, λ).sum()`, calculé avec eigh de la même Σ, donne la même valeur à rtol = 64·ε·cond(Σ).
- Avec Δ = c·v₁, l'information est sur l'axe 1. Avec Δ = c·v_N, elle est sur l'axe N : `select_top_q` donne {N} alors que l'information de P_d est nulle.
- Témoin : avec les λ de Σ + 0,5 I, l'écart relatif dépasse 1e-3.

**A2 [EXTENSION] `test_nested_plugin_information_monotone`**
- Les sommes plug-in cumulées sur P₁..P_k sont non décroissantes (Δ fixé, base emboîtée).
- Témoin : une suite non emboîtée construite viole l'inégalité.

**A3 [NOUVEAU] `test_top_q_exhaustive_forward_exact_with_ties`**
- Entrées : q dyadiques (j/64 ∈ [0,4], zéros et égalités), k = 1..12.
- Coûts : M et affine de `cost_tables(504,12)`, coût = d, et un coût de cardinalité non concave.
- Contrat : S, d et V sont **exactement** égaux pour trois méthodes :
  - `select_top_q` ;
  - l'énumération exhaustive des 2^k − 1 sous-ensembles (V maximal, puis d minimal, puis tuple d'axes trié lexicographiquement minimal) ;
  - l'ajout du plus grand q (égalité → plus petit axe), avec examen de tous les d.
- `tie_broken` est vrai si et seulement si au moins 2 sous-ensembles atteignent le V maximal.

**A4 [NOUVEAU] `test_early_stop_greedy_not_equivalent`**
- q = (1,1,1) et coût (1; 2,5; 2,9). `select_top_q` et l'énumération exhaustive donnent d = 3.
- Témoin : l'arrêt précoce donne d = 1.

**A5 [EXTENSION] `test_rotation_joint_vs_marginal_spd_symmetry_energy`**
- La KL jointe vaut 0,5625 (formule 2×2 fermée et `kl_cov`, à 1e-12 près). La somme des marginales vaut 0,33936 (à 1e-4 près). L'écart dépasse 0,2. Le balayage 15°/30°/45° donne jointe ≠ somme à chaque angle.
- Σ1 est SPD. Sa composante hors diagonale vaut 1,5 dans la base propre de Σ0.
- **Symétrie à tolérance flottante explicite, |Σ1 − Σ1ᵀ| ≤ 4ε·max|Σ1| (Q6)** ; la valeur mesurée est rapportée.
- L'énergie le long de e₁ passe de 4 à 2,5 alors que la KL est > 0. Dans `prepare_background` de F-tiny, |C1[0,1]| > 1e-3.
- Témoin : à 0°, jointe = somme = 0.

**A6 [NOUVEAU, scellés] `test_t7_information_labels_are_gaussian_proxies`**
- SMOKE et FULL : `info_kind` t7 finit par `_T7_PROXY`, les contrôles sont `GAUSS_PROXY_CHECK_T7`, le `q_info_type` de T2 vaut `*_PROXY`, et les tags effectifs mean_t7 contiennent `GAUSSIAN_PROXY`.
- Témoins : `EXACT_T_KL` donne `ENUM_VIOLATION` ; `COV_GAUSS_POP_JOINT_EXACT` sur une ligne t7 est rejeté par le vérificateur QA.

**A7 [EXTENSION] `test_mixture_cost_unique_positive_root`**
- Pour d ∈ {1, 4, 20, 500} et γ = 504 : g strictement croissante sur (0, 4x] avec un seul changement de signe ; résidu ≤ 1e-12·x ; M > 1 et fini ; M(4) = 1,5696 ± 5e-5 ; M(500) = 9,6427 ± 5e-5.
- Référence : itération de point fixe contractante.

**A8 [NOUVEAU, scellés] `test_mixture_cost_labelled_surrogate`**
- Aucun champ d'étiquette ni bloc `costs` ne contient `EXACT_ADD`, `ARL0` ou `COV_EXACT_COST`. Le coût M porte `MIX_FLUID_SURROGATE`, ou `HEURISTIC_COST` pour COV.
- Témoin : `EXACT_ADD` donne `ENUM_VIOLATION`.

**A9 [NOUVEAU] `test_v_surrogate_fixed_before_trials`**
- Scellés : V_mix = I/M_cost et V_affine = I/C_affine (float exact) ; `M_cost == manifest.costs["M"][d-1]`.
- `selection.csv` est identique à l'octet près entre F-tiny et F-poison.
- Témoin : sur ces deux runs, les agrégats diffèrent.

**A10 [EXTENSION] `test_projection_equals_stored_transform`**
- λ_LW > 0 ; VᵀV = I à 1e-12 ; `prep["W"] == V[:, :nmax]/sqrt(λ)` ; `project(...) == draw_path(...) @ W` (`array_equal`).
- Témoin : une base issue d'un autre rôle a un `basis_hash` différent.

**A11 [NOUVEAU, scellés] `test_mp_kaiser_cpv_on_sealed_spectra_and_tables`**
- `mp_edge` = (1+sqrt(239/1000))² à rel 4ε ; `kaiser_ge1 == (lambda_corr >= 1)` ; le champ `criteria` ne contient jamais « λ<1 ».
- CPV non décroissante ; CPV = 1 à k = N à 1e-12 ; CPV₂₀ < 0,9 ; statut OUTSIDE.
- La population donne CPV₁₄ = 104/239 = 0,435146.
- Lignes T3 `BASELINE_CPV90` : `CPV90_OUTSIDE_TOP20`, S et métrique NA, `NOT_COMPARABLE_OUTSIDE_TOP20`. C'est un **test négatif réussi**.
- Témoin : un `criteria` muté en « CPV 90 % » à k = 14 est rejeté.

**A12 [EXTENSION] `test_scan_reference_on_required_path_classes`**
- Référence en Python pur : double boucle sur 1 ≤ τ ≤ t, somme du segment **directe** (`math.fsum`, sans préfixe).
- Contrat : chaque `segment_loglik` (τ,t), chaque W_t et chaque première alarme de `scan_statistic` correspondent, à rtol = atol = 1e-12, pour d ∈ {1,2,4} et H ≤ 12.
- Classes de chemins : aucune alarme, alarme immédiate, maxima égaux répétés, départ non nul.
- Témoin : la règle GT au lieu de GE déplace l'alarme sur le chemin aux maxima égaux.

**A13 [NOUVEAU] `test_scan_full_history_instrumentation`**
- Un espion sur `pdb._scan_rows` vérifie des largeurs égales à t pour t = 1..250 (maximum 250). Sous la convention déclarée `CONTINUOUS_RESTART_AFTER_ALARM` (`scan_alarms` sur 300 jours sans alarme), le scan considère plus de 250 départs.
- Témoin : une variante fenêtrée QA (w = 50) donne un W différent.

**A14 [EXTENSION] `test_scan_prefix_terms_and_ex_ante_s2`**
- `_prefix` : S₀ = 0, a = −(p/2)log1p(n·s2), b = s2/(2(1+n·s2)). Un s2 ≤ 0 ou non fini lève `ValueError`.
- Dans les calibrations scellées, s2 = 2 ln(H/α)/(H·p) à rel 4ε. Une seule calibration existe par (dataset, famille, S).
- Le registre `pf.SPECS["mean"]` déclare la famille `MEAN_GAUSSIAN_MIXTURE_SCAN_CUSUM`.
- Témoins : le s2 apparié ‖mu_S‖²/p diffère du s2 stocké ; `GLR_WINDOWED` donne `ENUM_VIOLATION`.

**A15 [NOUVEAU] `test_calibration_rank_recipe_and_data_flow` (corr. 3)**
- Porte sur chaque calibration OK de SMOKE ; FULL est couvert par G1.
- Les maxima sont les `stat_max` des trials (`group_id = null_calibration_id`, rôle `calibration`), pris dans l'ordre des réplicats.
- Contrat :
  - `array_sha256(maxima) == maxima_sha256` ;
  - `rank_r == predictive_rank(n_cal, α)` ;
  - b = trié[n − r − 1] et seuil = b (GT) ou nextafter(b) (GE) ;
  - `calibration_alarms = #{m > b} ≤ r` ;
  - `calibration_hash` = sha256(octets des maxima + repr(seuil)) ;
  - `predictive_bound` = (r+1)/(n+1) pour le synthétique, NA pour D6 ;
  - le `fpr` du holdout égale le décompte de ses propres trials.
- Témoin : le même recalcul sur les maxima du holdout donne un autre seuil. Le flux des données est ainsi identifié.
- Aucune comparaison seuil/logarithme.

**A16 [NOUVEAU, scellés] `test_no_exact_eprocess_claim_and_mandatory_holdout`**
- `anytime_valid` est faux partout, `null_validity` est empirique ou approximative, aucune étiquette `EXACT_EPROCESS` n'existe, et chaque calibration OK possède un `HOLDOUT_NULL_FPR` fini.
- Témoin : `anytime_valid` à vrai est rejeté par le vérificateur QA.

### 4.2 B — Réutilisation exacte entre expériences (SMOKE, FULL)

**B1 [NOUVEAU] `test_t1_t2_prefix_identity_measured_and_blocked` (corr. 4)**
- Pour chaque ligne T2, je retrouve la ligne T1 de même (dataset, cohort, event, family, k). Les lignes sont classées en deux compteurs disjoints.
- **Mesurées** (statut OK, `execution` EXECUTED, valeurs finies). Doivent être égaux en texte :
  - `rmst_prefix*` = `rmst*` ;
  - `fpr_prefix*` = `fpr_test_null`, `fpr_lo`, `fpr_hi` ;
  - `metric_id_prefix`, `null_metric_id_prefix`, `selection_id_prefix` ;
  - `config_hash`, `basis_hash`, `split_hash`, `calibration_hash`, `null_calibration_id` ;
  - et ces valeurs égalent aussi la cellule source de `aggregates.csv`.
- **Bloquées NA.** Seuls les identifiants et statuts sont comparés, avec un NA des deux côtés et un `na_reason`. Ces lignes ne sont **jamais** comptées comme métriques vérifiées.
- Chaque bloc synthétique doit avoir un compteur « mesuré » > 0. Les deux compteurs sont rapportés.

**B2 [NOUVEAU] `test_identity_comparator_is_strict_text`**
- Témoins : une perturbation `nextafter`, re-sérialisée en `%.17g`, est détectée ; une chaîne `.4g` est rejetée.

**B3 [NOUVEAU] `test_e2_k20_e3_oracle_mix_identity_selected_rows` (corr. 4, Q9)**
- Portée : A_market_mean et C_residual_mean, fonds Gauss et t7 (t7 étiqueté proxy).
- Dans `selection.csv`, seulement `row_kind=SELECTED` : les lignes `ORACLE_Q_MIX` E2 à k = 20 et E3 ont le même `selection_id`, et les mêmes S, d, `I_objective` (plug-in), V_mix et `metric_id`.
- T2 (k = 20) contre T3 ordre « 2 » : `S_star`/`S`, `d_star`, `V_star`, `I_star`, `metric_id`, `rmst*`, `fpr*` égaux.
- Domaine **additif plug-in figé** : aucune optimalité n'est affirmée pour `I_pop_joint` ni pour une covariance.

**B4 [NOUVEAU] `test_reuse_negative_witnesses` (Q7)**

| Mutation | Code de rejet attendu |
|---|---|
| S non trié | `INVALID_S` |
| Axe 21 ou base 0 | `INVALID_S` |
| Axe décalé dans le domaine | `L18_Q_CONTROL` / `L17_E3_COPY` |
| Famille changée sur la copie E3 | `L17_E3_COPY` / `ACCORD_MISMATCH` |
| `null_metric_id` d'une autre calibration | `FOREIGN_NULL` / `ACCORD_MISMATCH` |

- Le comparateur B1/B3 désigne la cellule mutée.
- Avant toute conclusion, je vérifie que le témoin est correct et que le code attendu est bien documenté. Une mutation acceptée constitue alors un FAIL réel.

**B5 [NOUVEAU] `test_cov_and_exante_outside_additive_equalities`**
- Les lignes T3 « 1 » et « 2 » de B_cov sont `UNSUPPORTED`. `ORACLE_Q_*` est absent des sélections B_cov. `EXANTE_QBAR` synthétique est `UNSUPPORTED`.
- Témoin : ajouter `ORACLE_Q_MIX` pour B_cov donne `UNEXPECTED_ROW_STATE`.

### 4.3 C — Temps, fuite, échantillonnage

**C1 [NOUVEAU, scellés] `test_seed_plan_matches_manifests_and_role_groups_disjoint`**
- `seed_plan(config full)["sha256"]` égale le `rng.plan` de FULL (idem pour SMOKE). Dans les trials de SMOKE, les groupes calibration, holdout et alternative sont deux à deux disjoints.
- Témoin : la graine 43 donne un SHA différent.

**C2 [NOUVEAU] `test_thresholds_never_consume_holdout_or_alternative`**
- F-tiny contre F-poison : `calibration.csv` et `spectra.csv` sont identiques à l'octet près. Ces runs servent aussi de second run de reproductibilité.
- Témoin : les agrégats diffèrent.

**C3 [EXTENSION] `test_alternatives_paired_across_subsets`**
- Un espion sur `pdb.detect_alternative` relève un seul hachage de Z par scénario, quels que soient la famille et S. Les réplicats vont de 0 à n_alt−1, avec `ONSET_ALIGNED` et `SYNTH_ONSET_ALIGNED`.

**C4 [NOUVEAU, scellés] `test_horizon_rmst_censoring_on_sealed_trials`**
- Sur SMOKE (FULL via G1) :
  - H = 250 partout ;
  - `censored_time` = `first_hit` si détecté, H sinon ;
  - `rmst == mean(censored_time)` exactement ;
  - `det_rate + censored_share = 1` à 1e-15 près ;
  - `fpr == alarms/n` exactement.

**C5 [EXTENSION] `test_continuous_statistic_not_reset_at_onset`**
- `evaluate_real_path(…, FAKE_DATED_TEST)` sur une dérive qui commence avant l'onset : l'alarme arrive plus tôt qu'avec un scan relancé à l'onset (z[oi:]).
- Une alarme pré-onset est comptée une seule fois et n'est pas une détection pendant l'événement. Une alarme après la fin de l'événement est marquée `post_event_alarm`.

**C6 [NOUVEAU] `test_real_split_metadata_and_cohort_disjointness` (Q3, corr. 5)**
- Le SHA de `splits.yaml` égale son entrée dans `data/derived/MANIFEST.json` : calib [2016-04-07, 2019-12-31], embargo 65, `monitor.first_day` 2020-04-06.
- Contrôle distinct sur les **dates seules** de `dates.npy`, dont le SHA est vérifié contre le manifeste : 941 dates dans le segment calib, et 2020-01-02 comme première séance ≥ 2020-01-01. Aucun rendement n'est lu.
- `cohort_definitions(cfg, splits, dates)` :
  - standard : COVID au statut `NOT_EVALUABLE_STANDARD_SPLIT` ;
  - rétrospective : armée le 2020-01-02, `REAL_RETROSPECTIVE_EXPLORATORY`, embargo 0.
- SMOKE et FULL : aucun `selection_id`, `metric_id`, `split_hash` ni `null_calibration_id` partagé entre cohortes.

**C7 [NOUVEAU] `test_fake_confirmatory_status_rejected` (Q7)**

| Mutation | Code attendu |
|---|---|
| `claim_scope` rétrospectif → `REAL_STANDARD_SPLIT` | `COHORT_MISSING` |
| `status` « MAIN_TEST_VALID » | `ENUM_VIOLATION` |
| Ligne `EXECUTED` avec rmst renseigné | `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2` |
| COVID standard → `BLOCKED_PRE_J4` | `COHORT_MISSING` |
| `metric_id` partagé | `COHORT_ID_SHARED` |

**C8 [NOUVEAU] `test_post2019_rows_never_reach_fit_thresholds_stress`**
- F-fake (a) contre (b) : les résultats numériques de spectra, calibration et selection, ainsi que le bloc `real` hors `files`, sont identiques. Les effectifs sont ceux du calendrier factice.
- Les modifications des entrées changent légitimement `inputs`, `input_hash`, `run_fingerprint` et leurs identifiants dérivés. La liste limitée de champs non comparés entre les deux runs est définie au §9 ; aucune exclusion générique de tous les IDs/hashes. `basis_hash`, `x_fit_sha256`, `split_hash`, `calibration_hash`, `maxima_sha256`, S, seuils et bibliothèque de stress restent comparés strictement.
- Témoin : la perturbation d'une ligne calib change le `basis_hash`.

**C9 [EXTENSION] `test_stress_library_historical_and_qbar_not_oracle`**
- Les fenêtres vont jusqu'au 2011-12-31 au plus. Une fenêtre 2020 ou 2022 lève `IncompleteWindow`.
- Les lignes `EXANTE_QBAR` portent `STRESS_LIBRARY_2008_2011` et aucun flag ORACLE. qbar ne change pas avec les dates d'événement.
- Avec un stress sur l'axe a et un Δ sur l'axe b, les S diffèrent ; aucune égalité n'est supposée.

**C10 [NOUVEAU] `test_oracle_labels_and_sigma1_absent_from_detector`**
- Correspondances : `INJECTED_DELTA` ↔ `ORACLE_INJECTED_DELTA` ; `TRUE_SIGMA1` ↔ `ORACLE_TRUE_SIGMA1`, seulement pour les diagnostics oracle COV ; 2022 ↔ `RETROSPECTIVE_DIAGNOSTIC`.
- `_detector(cfg, prep avec C1 = NaN, COV, S)` produit un flux identique au flux d'origine.
- Témoin : la suppression du flag 2022 est rejetée.

**C11 [NOUVEAU, scellés] `test_real_rows_na_never_zero_or_target`**
- Lignes réelles de SMOKE, FULL et F-tiny avec `derived_dir` absent :
  - statut ∈ {NOT_EVALUABLE_STANDARD_SPLIT, BLOCKED_PRE_J4, DATA_UNAVAILABLE} ;
  - métriques NA et `na_reason` renseigné dans T1–T3 ;
  - aucun n = 2000 ;
  - calibrations D6 (F-fake) en `NOT_ESTABLISHED_HISTORICAL_WINDOWS`, avec `predictive_bound` NA.
- Témoin : rmst = 0 donne `REAL_EVENT_PATH_UNSUPPORTED_SCHEMA_2`.

### 4.4 D — Reproductibilité et provenance

**D1 [NOUVEAU] `test_reproducibility_hashes_exclude_time_and_paths`**
- Les blocs `identity` et les CSV de SMOKE, FULL et F-tiny ne contiennent ni horodatage, ni durée, ni chemin absolu. `provenance` reste hors de `identity`.
- Le double run est couvert par `test_g3_two_fresh_directories_are_byte_identical_and_the_seed_matters` et par C2 ; ce recouvrement est documenté.

**D2 [NOUVEAU] `test_sealed_identity_recomputes_with_current_code`**
- SMOKE et FULL : `sha256(canon(identity)) == run_fingerprint` ; `identity_block(config, entrées déclarées)` égale `identity` ; les sorties présentes ont le SHA du manifeste. Le manifeste FULL a le SHA `3b2299bc…`.

**D3 [NOUVEAU, figures corrigées] `test_figure_points_trace_to_aggregates`**
- `verify_figures_dir` est vrai.
- Chaque y fini suit lignée → `SOURCE` → cellule runner, avec égalité en texte.
- Les RMST correspondent à des `ALT_RMST` EXECUTED/OK. `null_fpr` égale le `fpr` mesuré. k = 1..20.
- Témoin : un `null_fpr` remplacé par la cible est détecté.

**D4 [EXTENSION] `test_cov_figure_exploratory_effective_labels` (Q12)**
- Les tags **effectifs** et le titre rendu contiennent `COV_SURROGATE_EXPLORATORY` pour cov, et ne le contiennent pas pour mean. Les `spec.tags`, copie du registre, peuvent contenir `SMOKE_NO_CLAIMS` ; les tags effectifs du full, non.
- Les V de cov proviennent de lignes `COV_GAUSS_POP_JOINT_*`, jamais de `I_cov_marginal_sum`. L'axe droit porte `H5_PHRASE`.

**D5 [CONDITIONNEL] `test_stale_or_wrong_source_hash_refused`**
- 1 octet modifié dans une copie `tmp` : `INPUT_INVALID`, `HASH_MISMATCH` ou `TABLES_INCOMPLETE`.

**D6 [CONDITIONNEL] `test_missing_values_are_gaps_not_interpolations`**
- Avec NaN à k = 6, la ligne tracée vaut NaN et le marqueur « × » est présent.

**D7a [CONDITIONNEL/EXTENSION] `test_annotations_follow_values_and_status` (corr. 6)**
- L'annotation CPV est une fonction des données et du statut : croisement à 7 → « k = 7 » ; croisement à 14 → « k = 14 » ; OUTSIDE sans croisement → « k90_full = <valeur> ».
- Le texte FPR reprend les `null_fpr` fournis et change si on les change.
- Aucune interdiction générale de chaînes (≈, d*, 5 %).

**D7b [NOUVEAU — FAIL établi] `test_full_figure_text_sample_sizes_match_manifest`**
- `load_context(FULL, TAB_FULL)`, `build_entry` et `render_figure` en mémoire : chaque « n = x » imprimé doit égaler un compte du manifeste (2000).
- Attendu : **FAIL** sur « (n = 40) ». **Exécuté en dernier** (§5).

### 4.5 E, F — Parseur, numérique, invariants historiques

**E1 [NOUVEAU, scellés] `test_axis_list_round_trip_and_d` (corr. 1)**
- Pour toute ligne avec S : `S_json([i - 1 for i in parse_S(text, nmax)]) == text` ; `pdt._parse_S` donne le même résultat ; `d == len(parse_S(text, nmax))`. Les rejets sont couverts par le producteur, recouvrement documenté.

**E2 [NOUVEAU, scellés] `test_information_finite_nonnegative_positive_eigenvalues`**
- `lambda_lw` > 0 et fini ; `whitening_scale` = sqrt ; I_* ≥ 0 et finis sur les lignes OK ; `clipped_negative_kl` est un entier ≥ 0.

**E3 [EXTENSION] `test_clip_tolerance_and_documented_rejections` (corr. 2)**
- `clip_kl` : la tolérance documentée est −1e-12·max(1,|I|), une **constante de tolérance et non l'epsilon machine**. −1e-13 donne 0 avec un compte de 1 ; −2e-12 lève `ArithmeticError`.
- `kl_cov_raw` rejette un déterminant de signe non positif (diag(1,−1)). Son prérequis déclaré est une paire de matrices SPD ; le contrôle implémenté porte seulement sur le signe de `slogdet`.
- **Observations hors domaine SPD fini** : diag(−1,−1) n'est pas rejetée par `kl_cov_raw` ; certaines entrées NaN/inf et `clip_kl(NaN)` renvoient NaN. Le plan attribuait à tort un rejet non fini à cette primitive. Ces limites sont rapportées séparément, sans PASS de validation des entrées et sans correctif producteur ; toute sortie non finie pour une entrée du domaine déclaré reste un FAIL bloquant. Arbitrage Codex du §10.

**F1 [NOUVEAU] `test_e2_cells_crlf_disk_and_index_unchanged`**
- SHA disque = SHA de `git show :results/e2/e2_cells.csv` = `e315e537…0823`, et les octets sont égaux.
- 47 CRLF, aucun LF nu ; règle `-text` présente. Échec franc si Git est indisponible.
- Témoin : la version normalisée en LF change le SHA.

**F2 [NOUVEAU] `test_d8_fail_preserved_verbatim`**
- `## C-e3-d8-fail`, « +0.0528334213 > 0.05 » et « It is a FAIL by excess » sont présents.
- `e3_overshoot.csv` a le SHA `1ca7c3ae…68b3`. Sa ligne primary porte `gate FAIL` et un `rel_gap` égal à +5,2833 % (arrondi à 4 décimales).
- Témoin : un texte muté en « PASS » est rejeté.

### 4.6 G — Intégration full 2000 en lecture seule (Q4)

**G1 [NOUVEAU] `test_full2000_trials_read_only`**
- Exécuté réellement avec `PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv`, par lecture directe, sans copie ni lien.
- Contrôles :
  - taille 48 317 020 octets, SHA `40b5f891…` égal au manifeste, 716 000 lignes ;
  - inventaire des groupes ;
  - recette de rang A15 et identités C4 recalculées exactement.
- Statut `BLOCKED_DATA_UNAVAILABLE` (skip) **seulement** si la variable est absente ou si le chemin n'existe pas. Une empreinte erronée ou une divergence numérique est un **FAIL**.

**Rapport** `docs/audits/PCA_CONTRACTS_VALIDATION.md`, en anglais. Il contient :
- les commandes et l'environnement ;
- les comptes PASS/FAIL/BLOCKED par groupe et les durées ;
- les hachages vérifiés et le manifeste de découpage ;
- la matrice contrat → test → témoin, avec les recouvrements producteurs ;
- les tests négatifs réussis ;
- le FAIL D7b et l'état STOP ;
- les observations (limite SPD, `spec.tags`).

Il ne contient aucune affirmation de « no defect ».

### 4.7 Tâches du lot 2 (après GO QA, sur la base du commit lot 1)

- [ ] **Q0 — Pré-vol.** Base = commit lot 1 de Codex ; vérifications F1 et `PLAN.md` par `cmp`/`test` ; recherche des recouvrements (§4.0).
- [ ] **Q1 — Groupes F et E.**
- [ ] **Q2 — A1–A11.**
- [ ] **Q3 — A12–A16.**
- [ ] **Q4 — B.**
- [ ] **Q5 — C.**
- [ ] **Q6 — D1–D7a.**
- [ ] **Q7 — G1, avec la variable.**
- [ ] **Q8 — D7b en dernier.** Son FAIL déclenche le STOP.
- [ ] **Q9 — Mesure finale et rapport.** Une exécution unique du fichier, avec la variable G1, mesure le tout ; puis j'écris le rapport en état STOP. Aucun commit, aucun `make check`, aucun outillage, aucune nouvelle tâche de code. L'arbitrage revient au chercheur.

Commandes :

```bash
.venv/bin/python -m pytest -q tests/test_pca_drift_contracts.py -k <groupe>
PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv \
  .venv/bin/python -m pytest -q -rA tests/test_pca_drift_contracts.py 2>&1 | tee logs/pca_drift_contracts/qa.log
.venv/bin/pyflakes tests/test_pca_drift_contracts.py
```

## 5. Politique de diagnostic et STOP (corr. 8 et 10)

- **Témoins.** Ils vivent en mémoire ou en `tmp_path`. On ne modifie jamais un producteur pour fabriquer un RED.
- **Erreur de référence ou de fixture de la QA** (contradiction avec la doc de schéma) : diagnostic séparé, **au plus 3 corrections du test**, chacune tracée dans le rapport.
- **Défaut numérique ou de provenance confirmé, ou mutation acceptée contrairement à un contrat documenté** (après vérification du témoin) : **STOP**. Je rapporte au terminal le test, l'entrée, la sortie et le contrat cité. Aucun xfail, aucune correction producteur. Le fichier STOP relève de Codex et du chercheur.
- **Après un STOP non levé :** aucun `make check`, aucun outillage, aucun commit, aucune tâche de code. Seuls le rapport et l'état STOP sont produits.
- **Tests négatifs réussis, à ne jamais effacer :**
  - covariance non additive (A5, B5) ;
  - Covid sous embargo standard (C6, C7) ;
  - CPV90 hors top 20 (A11).

## 6. Observations hors contrat (Review Focus)

1. **Validation SPD de `kl_cov_raw`** : elle repose sur le signe du déterminant (diag(−1,−1) passe). À arbitrer ; ce n'est pas un faux contrat (E3).
2. **Comptes imprimés en dur** dans les figures : D7b, FAIL établi.
3. **`spec.tags`** des manifestes full : copie du registre, distincte des étiquettes effectives (D4).
4. **Coût O(L²)** des chemins réels continus longs : non testé.
5. **Quasi-égalités flottantes de V hors q dyadiques** : tranchées par l'égalité exacte en production ; A3 ne couvre que les dyadiques.
6. **`CLAUDE.md`** décrit encore check_prompts par « exact substrings » : à mettre à jour par Codex s'il le souhaite.

## 7. Questions résiduelles v2 (défaut entre crochets)

1. **QR1** : R-O4, égalité exacte du bloc, est-elle acceptée comme forme de la « présence exacte » ? Elle détecte un fichier source tronqué, qu'un simple test de sous-chaîne laisse passer. [oui]
2. **QR2** : l'équilibre des fences, ouvertures = fermetures, sert-il de garde contre un master tronqué ? [oui]
3. **QR3** : `--sync-master` doit-il avoir la post-condition « n'écrit rien si le résultat viole R-O2, R-O4 ou R-O5 » ? [oui]
4. **QR4** : le lot 1 crée-t-il `prompts/plans/plan-31.md` (ce v2 avec la Décision GO lot 1) et `prompts/wrapups/wrapup-31.md` (état lot 1) avant le commit Codex ? [oui]
5. **QR5** : les tests [CONDITIONNEL] D5, D6 et D7a sont-ils abandonnés si la recherche de recouvrement trouve une assertion producteur équivalente ? [oui, documenté]
6. **QR6** : en état STOP, le lot 2 produit-il seulement `PCA_CONTRACTS_VALIDATION.md`, le wrapup n'étant actualisé que sur demande de Codex ? [oui]

## 8. Décision GO intégrée

Date : 2026-11-06, 09:42 UTC. Décision Codex dans le mandat délégué, sans attribution d’une signature personnelle au chercheur.

**Lot 1 : GO d’exécution borné**, selon `prompts/GO-stream-31-tooling.md`. Base `a0c576e13e8e647dfd61350eec52058ffc794dbf`. Proposition v2 native de 527 lignes, SHA-256 `a82a231d458a27e3b4affe6e8dae56a71588d3cedfea8c8b110006b1317972f7`, archivée sans changement dans les journaux ignorés. Codex a enregistré ce plan avant toute implémentation ; Claude ne le recopie pas.

Réponses QR1–QR6 et précisions opératoires :
1. QR1 retenu : égalité du bloc hors séparateurs de fin, avec présence exacte du texte source complet ; aucune normalisation CRLF/LF. Ne pas remplacer le contenu canonique par un préfixe tronqué.
2. QR2 retenu : équilibre des fences, en respectant les fences imbriquées historiques et les deux tests existants. La migration garde les 29 blocs et les octets du master initial.
3. QR3 retenu : toutes les validations applicables ont lieu avant toute écriture ; un refus ne laisse pas un master partiellement modifié.
4. QR4 retenu : plan déjà persisté par Codex ; wrapup anglais du lot 1 produit par Claude avant revue/commit. Les deux fichiers Codex étrangers et le GO restent intacts.
5. QR5 concerne seulement le lot 2 non autorisé. Aucun contrat obligatoire ne disparaît : un recouvrement éventuel doit nommer le test existant et sa commande réellement exécutée, sans import d’un module de tests producteur.
6. QR6 retenu pour un éventuel GO QA futur : un STOP permet le rapport d’incident ; il n’autorise aucune correction producteur ni nouvelle tâche de code.

Amendements pratiques sans changement de périmètre :
- `main()` passe explicitement la valeur courante de `STREAMS` à la découverte, ou la découverte résout cette valeur à l’appel : les tests temporaires ne doivent jamais utiliser le chemin du dépôt capturé dans un argument par défaut.
- Les pipelines de commandes préservent les codes de sortie (`pipefail`). L’échec attendu du contrôle avant migration est capturé explicitement sans être masqué par `tee` ni interrompre la procédure avant vérification du code 1.
- Les comptes 9 tests ciblés / 582 tests globaux sont des attentes du plan, pas des valeurs à forcer ; consigner les comptes et durées réellement obtenus.
- Après le lot 1 : arrêt pour revue Codex. Aucun fichier de contrats PCA, aucune exécution de D7b, aucun Git ni reindex par Claude.

**État historique à 09:42 : aucun GO du lot 2.** La décision ultérieure du §9 ouvre seulement la QA bornée après clôture du lot 1. Aucun changement des producteurs, données ou figures scellées n’est autorisé.

## 9. Décision GO intégrée — QA, 2026-11-06 à 12:22 UTC

GO Codex dans le mandat délégué, sans signature personnelle du chercheur. Base : `20ad9e860a58373ec85405de6ee19a68322dd02e`, vérifiée sur main et le distant après le hook réussi (37 + 545 tests passés, 5 ignorés). Le worktree 31 est propre avant la présente décision et aucun hook n’est en cours. Référence exécutoire : `prompts/GO-stream-31.md`.

La reprise native en mode plan est archivée sans changement dans `logs/orchestration_reprise_20261106/qa-readiness-plan-reviewed.md` : 114 lignes, SHA-256 `e6765d9beeb0436f84e66b2fc2bb8a3be4b449aaa04ccda30be04f8584fcd128`. Les précisions P1–P5 de cette revue sont retenues, avec les bornes suivantes.

**QQA1 — C8 accepté comme correction de référence.** `identity_block` inclut les hashes d’entrées ; les IDs de null/calibration/sélection/métrique en dépendent. Pour la comparaison entre les deux panels factices seulement, la liste explicite autorisée est `run_fingerprint`, `config_hash`, `null_id`, `null_calibration_id`, `selection_id`, `metric_id`, `null_metric_id`. `config_hash` ne peut différer qu’à cause des chemins factices, après contrôle que le reste de la configuration est identique. Les blocs `identity` ne diffèrent que par `inputs`/`input_hash` et ce `config_hash` éventuel ; code, environnement et graines restent identiques. Dans le bloc `real`, seule la provenance `files` est exclue. Tous les autres champs, y compris les hashes scientifiques de base/calibration et les données de stress, restent comparés. Les références et l’intégrité des IDs sont contrôlées séparément dans chacun des deux artefacts. Le témoin sur une ligne de calibration est conservé.

**QQA2 — Fixture F-fake autorisée.** Le nom de mode `full` est une exigence de l’API pour `dataset="both"`. Il ne donne aucun GO au benchmark full : petits effectifs du plan, rendements entièrement factices sous `tmp_path`, aucune lecture de rendements réels et aucune sortie dans les répertoires scellés. Les 941 dates réelles de C6 sont un contrôle de métadonnées séparé.

**QQA3 — Arrêt et Git.** Aucun commit, hook ou `make check` du worktree 31 après le FAIL de contrat, aucune suppression/déplacement du test pour rendre une suite verte. Le rapport indique les comptes réels. Les autres worktrees documentaires sont isolés ; ils ne collectent pas ce fichier QA.

**FULL sans trials local.** Lire les six sorties locales présentes avec vérification SHA. Ne pas appeler `pdt.load_run(FULL)`, qui exige les sept fichiers. Mutations et validation de run sur SMOKE ; G1 lit les trials directement par la variable prévue, sans copie ni lien. `pf.load_context(FULL, TAB_FULL)` reste autorisé en lecture seule.

**Précision B1/B3 et scan.** T2 n’a pas de colonne `execution` : utiliser T1 et `status_prefix`, et les colonnes `metric_id_subset`/`rmst_selected*`/`fpr_selected*` pour la copie E3. Les comparaisons de W sur tout l’horizon utilisent le scan sans arrêt anticipé ; les premières alarmes sont testées séparément en respectant sa règle GE et son comportement documenté après alarme.

**Ordre Q8–Q9 amendé.** Les groupes et G1 sont exécutés avant D7b. Après écriture de D7b en dernière position et pyflakes, une unique exécution finale du fichier avec G1 et `-x` mesure les comptes et atteint D7b en dernier si les autres contrats passent. Le premier défaut producteur confirmé déclenche immédiatement STOP ; aucune seconde exécution ni nouvelle tâche de code ensuite, seulement le rapport d’incident. Cette séquence remplace toute lecture de Q9 qui autoriserait un rerun après STOP.

**Propriété.** Claude crée seulement `tests/test_pca_drift_contracts.py`, `docs/audits/PCA_CONTRACTS_VALIDATION.md` et les journaux ignorés. Le plan, ce GO, l’audit et le wrapup du lot 1 appartiennent à Codex. Aucun changement producteur ni correction du texte « n = 40 ». Tous les autres invariants et exclusions du plan restent applicables.

## 10. Reprise après quota et arbitrages de revue — 2026-11-06, 13:25 UTC

Le chercheur confirme la réinitialisation du quota pour cinq heures et demande la reprise des trois streams. Le registre QA constate 26 tests réussis (F/E, A, B), sans mesure finale et sans STOP de défaut producteur. Reprendre aux groupes C, puis D et G1 ; ne pas recommencer les groupes inchangés.

**E3, correction de référence.** Codex a reproduit sous le venv le retour NaN de `kl_cov_raw(I, diag(NaN,1))`, `kl_cov_raw(I, diag(inf,1))` et `clip_kl(NaN)`. La docstring exige des matrices SPD, ne promet pas un validateur universel. Retirer l'attribution erronée de rejet automatique du plan, consigner `O-E3-NONFINITE` comme limite observée et non comme succès de contrôle. Le rejet du signe non positif, le clipping documenté et la finitude/non-négativité dans le domaine SPD fini restent testés. Aucun rejet existant ni exigence de finitude applicable n'est supprimé.

**Finitude E2.** Une valeur NA n'est admise que pour un champ non applicable au rôle et au type d'information de la ligne. Les champs d'information requis sur une ligne OK doivent être renseignés, finis et non négatifs avant tout filtrage. Ne pas transformer un NaN requis en absence inoffensive. Réutiliser les contrôles existants s'ils couvrent exactement ce point, sinon ajouter le plus petit témoin QA.

**B4, ordre des refus.** La mutation d'une famille incompatible avec la méthode E3 est rejetée en `UNEXPECTED_ROW_STATE` avant la vérification de lignée, conformément à l'applicabilité documentée. Ce refus est accepté ; conserver le second témoin compatible E2 qui atteint `L16_PREFIX_IDENTITY`, ainsi que les contrôles d'axes et de null étranger.

**Ingésions et corrections.** Toute lecture CSV utilise explicitement `float_precision='round_trip'`, y compris le lecteur en texte. La limite de trois corrections concerne les tentatives d'un même incident QA diagnostiqué ; une divergence scientifique confirmée ne relève jamais de cette procédure et impose STOP immédiat. La correction A7 déjà consignée reste dans le rapport.

Le GO QA reste borné aux deux livrables et journaux autorisés. Aucun producteur, dépendance, donnée, figure, valeur scellée ou seuil ne change. La séquence finale unique avec `-x`, D7b en dernier et rapport après STOP reste inchangée.

## 11. Réception après l'avenant D7b — 2026-11-06

Le STOP initial du lot 2 a donné 43 réussites et un échec D7b ; ses preuves et ses journaux sont conservés. Le chercheur a ensuite autorisé le correctif ciblé et le remplacement des deux seuls dossiers full par son avenant `FIX-stream-31-nb-assets.md` (SHA-256 `ce91c1899db2fac30dcb88e64f3b1043861263adb7c2988d5394a706b84735e6`).

Le plan séparé `prompts/plans/plan-31-fix.md` et le GO `prompts/GO-stream-31-fix.md` ont été enregistrés avant l'exécution. Ils remplacent, pour ce seul correctif, les interdictions antérieures sur le traceur et les deux dossiers full. Les décisions QA des §9–10 restent inchangées.

La réception Claude mesure 44 contrats réussis, sans échec ni skip, G1 exécuté, puis `make check` : 37 + 589 réussites et cinq skips D4 préexistants. Le traceur ne change que sur deux lignes ; les CSV sources, les smoke, les tables, le runner, J1 et D8 gardent leurs octets. Le rapport `docs/audits/PCA_CONTRACTS_VALIDATION.md` distingue la mesure historique de la nouvelle et porte la revue indépendante Codex. La réindexation, les contrôles pré-commit, le commit et l'intégration restent à terminer par Codex.
