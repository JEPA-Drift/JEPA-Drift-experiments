# Stream 31 — Plan séparé du correctif D7b

**Statut.** Plan natif relu et enregistré par Codex avant exécution. GO séparé au §8 ; les propositions et questions initiales sont conservées ci-dessous pour la trace de décision. Base d'implémentation : `20ad9e860a58373ec85405de6ee19a68322dd02e`.

## Contexte

- **Demande.** `logs/pca_drift_contracts/fix-d7b-plan-request.md`, sur la base `20ad9e860a58373ec85405de6ee19a68322dd02e` du worktree `stream-31`.
- **Autorités lues intégralement.**
  - `researcher-fix-amendment.md`, identique octet pour octet à `prompts/FIX-stream-31-nb-assets.md` du worktree principal (SHA `ce91c189…`).
  - `researcher-fix-request.md`, identique à `prompts/31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` (SHA `fbfccc96…`).
  - Ce qu'elles autorisent : le correctif de `plot_figure_1.py:582` et le remplacement des deux seuls répertoires de figures full.
  - Ce qu'elles exigent encore : un plan séparé et un GO séparé avant toute mutation.
- **Cause établie (lot 2, `qa.log`, rapport §6).** `render_figure` imprime « (n = 40) » en dur (l. 582). Le manifeste full déclare 2000 par rôle. Les valeurs tracées sont intactes (D3).
- **Lecture seule dans le worktree principal.** Seulement `ls`, `sha256sum` et un `git status --porcelain` (aucun ajout à l'index, aucune écriture voulue). Les trois fichiers non suivis du chercheur y sont intacts.

## 1. Constats vérifiés en lecture seule

**Une seule ligne est impossible.**
- `render_figure(src, meta)` n'a accès ni au manifeste ni au contexte.
- `src` (colonnes `SRC_COLS`) ne contient aucun effectif.
- Les interdits excluent les autres voies :
  - retrouver n en inversant les bornes de Wilson serait un nombre deviné ;
  - un état global ou une introspection de pile sont exclus.
- Il faut donc un champ dans `meta`, ce qui fait deux lignes dans le même traceur.

**Effectif pertinent : le rôle `holdout_null`.** C'est le n des FPR250 observés, filtrés par la règle P + Wilson W.

| Grandeur | SMOKE | FULL | Verdict |
|---|---|---|---|
| `config.n_null` (rôle null holdout) | 40 | 2000 | **retenu** |
| `aggregates.n` des 106 lignes `HOLDOUT_NULL_FPR` (toutes OK/EXECUTED) | 40 | 2000 | égal à `config.n_null` ; les 31/31/22 holdouts de mean/mean_t7/cov n'ont qu'une valeur |
| `config.real.n_null` | **2000** | 2000 | piège : vaut 2000 même en smoke ; trajectoires réelles non tracées (refus `REAL_FIGURE_NOT_EXECUTED_SCHEMA_2`) |
| `config.N` | 239 | 239 | nombre d'actifs, pas de trajectoires |
| `n_cal`, `n_alt` | 40 | 2000 | autres rôles ; égaux ici, mais ce n'est pas le n des FPR |

**Callers.** Tous passent par `build_entry` → `meta`, sans exception :
- `main` (l. 898, 916) ;
- QA : `_render` (l. 204–211), `full_renders`, A6 (l. 493), D7a ;
- `tests/test_plot_figure_1.py` (l. 335–475), dont le contexte factice déclare `config.n_null = 40`.

**Rejeu depuis le manifeste.** `main` sérialise `meta` dans `figure_manifest.json` → `records.<key>.render` (l. 935). `test_round_trip_from_source_csv` rejoue `render_figure(src, rec["render"])` et compare les octets. Le canal `meta` est donc nécessaire pour que le manifeste reste suffisant au rejeu.

**Provenance indépendante du répertoire de sortie.**
- `command` : `_command_gabarit` produit `--output-dir <OUT>`, avec des chemins d'entrée et de tables relatifs (`pdb._rel`).
- `FIGURE_CHECK.md` : chemins relatifs, gabarits `<OUT>`/`<LOG>`.
- `figures_fingerprint = sha256(canon({schema, input, tables, code, environment, filters, strict}))` : aucun chemin de sortie.
- Les légendes et les CSV ne contiennent aucun chemin.

**État des répertoires (17 fichiers chacun, suivis par Git).**

| Répertoire | Traceur enregistré |
|---|---|
| full `full_2000_20261101` | `5346b314…` (avant le correctif des tags) |
| full `full_2000_20261101_fix_smoke_no_claims` | `c40a5e77…` |
| smoke `smoke_predictive_v2_closeout` | `f2a0e7f0…` |
| smoke `smoke_predictive_v2_closeout_fix_smoke_no_claims` | `c40a5e77…` |

- Les trois CSV sources full sont identiques dans les deux répertoires full : `8a2ec3a4…` (cov), `a4c343a2…` (mean) et `f8ec238c…` (mean_t7). Ce sont les « six CSV sources ».
- Bloc `environment` identique dans les manifestes : Python 3.12.9, numpy 2.4.4, pandas 3.0.6, matplotlib 3.11.2, `MPLBACKEND` Agg, variables OMP/MKL/PYTHONHASHSEED, police DejaVuSans.ttf.
- Aucun document suivi ne cite les hachages ou empreintes actuels des figures full.

**Retour à la ligne.** `textwrap` à 72 colonnes : la 2ᵉ ligne passe de « equality test (n = 40) » à « … (n = 2000) ». Elle reste sur deux lignes, sans changement de mise en page attendu.

**Sélecteurs.** `-k "D7b or D7 or D2 or D3 or D4"` est vacant : aucun nom de test ne contient ces étiquettes. Node IDs réels :
- D2 `tests/test_pca_drift_contracts.py::test_sealed_identity_recomputes_with_current_code`
- D3 `…::test_figure_points_trace_to_aggregates`
- D4 `…::test_cov_figure_exploratory_effective_labels`
- D7a `…::test_annotations_follow_values_and_status`
- D7b `…::test_full_figure_text_sample_sizes_match_manifest`
- G1 `…::test_full2000_trials_read_only`

Un node ID erroné sort en erreur (code 4) ; un `-k` vide sort avec le code 5.

## 2. Chemin manifeste → `render_figure(src, meta)`

1. `load_context` lit `<run>/manifest.json` et contrôle `outputs`, le schéma et `run_fingerprint == sha256(canon(identity))`. Avec `--strict`, il vérifie aussi `identity_block(config, inputs) == identity` (l. 226) : `config` est lié à l'empreinte. D2 recalcule ce lien pour SMOKE et FULL.
2. `build_entry` (l. 460) ajoute `meta["n_null"] = int(ctx.manifest["config"]["n_null"])`. C'est la seule lecture nouvelle.
3. `render_figure` (l. 582) imprime `meta['n_null']`. `main` enregistre `meta` dans `records.render` (l. 935).

## 3. Modifications exactes

### 3.1 Traceur `experiments/figures/plot_figure_1.py` : 2 lignes modifiées, 0 ajoutée

```text
L460 avant :             "is_cov": spec["comparator"] is not None}
L460 après :             "is_cov": spec["comparator"] is not None, "n_null": int(ctx.manifest["config"]["n_null"])}
L582 avant :         lines.append("FPR comparability (P identity + Wilson W): descriptive filter, not an equality test (n = 40)")
L582 après :         lines.append(f"FPR comparability (P identity + Wilson W): descriptive filter, not an equality test (n = {meta['n_null']})")
```

- **Exclus :** import, fonction, constante, état global, introspection et toute autre ligne du producteur. `render_caption`, `SPECS`, les tags, le runner et les tables restent inchangés.
- **Effet déclaré :**
  - les trois `records.render` du manifeste gagnent `n_null` ;
  - le hash du traceur change ;
  - `code` et `figures_fingerprint` changent ;
  - la ligne de code SHA de `FIGURE_CHECK.md` change.

### 3.2 Test QA : D7b étendu en place

D7b reste dernier. Le fichier garde 44 tests : 2 lignes modifiées, 7 ajoutées, aucun nouveau test, ni skip ni xfail.

```python
def test_full_figure_text_sample_sizes_match_manifest(sealed, full_renders, smoke_ctx):   # + smoke_ctx
    ...  # 7 lignes FULL inchangées (cfg, allowed, found, boucle)
    sm = smoke_ctx.manifest
    probe = pf.Ctx(dict(sm, config=dict(sm["config"], n_null=39)), smoke_ctx.run_text, smoke_ctx.tables_text,
                   smoke_ctx.table_manifest, smoke_ctx.input_dir, smoke_ctx.tables_dir)
    side = {tag: sorted({int(x) for t in _render(pf.build_entry(c, "mean"))["texts"] for x in re.findall(r"\bn = (\d+)", t)})
            for tag, c in (("SMOKE", smoke_ctx), ("SMOKE_n_null_39", probe))}
    print(f"D7b printed n: FULL {sorted(found)} (manifest {sorted(allowed)}); {side}")
    assert allowed == {2000} and found                                              # inchangé
    wrong = {...}                                                                   # inchangé
    assert not wrong and side == {"SMOKE": [40], "SMOKE_n_null_39": [39]}, (
        f"full 2000 figure text prints sample sizes {sorted(wrong)} != manifest counts {sorted(allowed)}: {wrong}; smoke {side}")
```

- **Rôle de la sonde.** Elle travaille sur une copie en mémoire du manifeste smoke, avec `n_null = 39` et `n_cal = n_alt = 40` inchangés. Elle discrimine :
  - toute constante (40, 2000, ou une bascule sur `run_mode`) ;
  - `n_cal` et `n_alt`, restés à 40 ;
  - `config.real.n_null` (2000 en smoke) ;
  - N = 239.
- **Garanties.** La fixture partagée `smoke_ctx` n'est jamais mutée. Aucun artefact scellé n'est touché.
- **Coût.** 2 rendus en mémoire de plus (smoke mean et sonde mean), soit 5 au total dans le fichier.
- **RED attendu avant le correctif, une seule assertion :**
  - message `sample sizes [40] != manifest counts [2000]` ;
  - suivi de `smoke {'SMOKE': [40], 'SMOKE_n_null_39': [40]}`.
- **GREEN attendu :** FULL `[2000]`, `{'SMOKE': [40], 'SMOKE_n_null_39': [39]}`.

## 4. Séquence après GO

Racine du worktree. Préfixe `export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`.

Les journaux vont sous un nouveau `logs/pca_drift_contracts/fix_d7b/` (ignoré ; noté `$L` ci-dessous). `qa.log`, `ledger.md` et les journaux du lot 2 ne sont pas touchés, car leurs SHA sont cités. Le ledger `$L/ledger.md` consigne chaque étape et chaque arbitrage.

**S0 — Pré-vol et inventaire AVANT** (`$L/inventory_before.txt`)
- Conditions à vérifier :
  - HEAD = `20ad9e8` ;
  - `git status` donne les 5 lignes connues, plus le GO Codex éventuel ;
  - `$L` absent ;
  - traceur `c40a5e77…`, QA `dad74703…`, rapport `fd6346ea…`.
- Contenu de l'inventaire :
  - `sha256sum` de tous les fichiers sous `results/pca_drift_benchmark/` (4 répertoires de figures, runs SMOKE/FULL, tables) ;
  - J1 : disque, index (`git show :results/e2/e2_cells.csv | sha256sum`) et nombre de CRLF (47) ;
  - D8 : `results/e3/e3_overshoot.csv` ;
  - `docs/DEVIATIONS.md`, `PLAN.md`, runner et assembleur.

**S1 — RED réel.**
- Éditer D7b (§3.2), puis lancer `pyflakes` sur le fichier QA.
- Lancer ensuite `PCA_FULL2000_TRIALS=… .venv/bin/python -m pytest -q -rA <D7b node ID>` > `$L/red_d7b.log`.
- Attendu : 1 failed, avec le message du §3.2.
- Toute autre issue est une erreur QA : au plus 3 corrections tracées.

**S2 — Correctif puis GREEN.**
- Appliquer les deux lignes du §3.1 et lancer `pyflakes` sur le traceur et le test : rien affiché, code 0.
- D7b seul : 1 passed (`$L/green_d7b.log`).
- D2, D3, D4, D7a et D7b par node IDs : 5 passed (`$L/green_D.log`).
- `tests/test_plot_figure_1.py` : tout passe (`$L/plot_tests.log`).

**S3 — Re-render vers un chemin neuf ignoré** (`$L/render.log`, code de sortie consigné) :

```bash
.venv/bin/python experiments/figures/plot_figure_1.py --input-dir results/pca_drift_benchmark/full_2000_20261101 \
  --tables-dir results/pca_drift_benchmark/tables/full_2000_20261101 --output-dir $L/render_full --figure both --strict
```

- Les entrées sont seulement le run et les tables scellés : 4 CSV runner, `manifest.json` et les tables.
- `--strict` hache aussi l'entrée déclarée `splits.yaml`, qui ne contient que des métadonnées.
- Aucun runner, aucune table et aucun rendement ne sont lus ni réexécutés.

**S4 — Vérifier le rendu avant tout remplacement** (`$L/render_checks.log`). Le script Python est en lecture seule, lancé avec `-B`. Les outils externes sont poppler et grep. Les contrôles :
1. `pf.verify_figures_dir` vrai, et mêmes 17 noms que les deux répertoires full.
2. `command` est la chaîne exacte du manifeste `_fix` actuel, avec `--output-dir <OUT>`, les chemins relatifs, `--figure both --strict`.
3. `input`, `tables`, `environment`, `filters`, `strict` et `figures_schema` sont égaux à ceux du manifeste `_fix`.
4. `code` : traceur au nouveau SHA, runner `8324b47b…` et assembleur `13d386fe…` inchangés.
5. `figures_fingerprint` est recalculé, égal à la valeur enregistrée et différent de `df4e5c30…`.
6. Chaque `record` est égal à celui de `_fix`, sauf `render.n_null == 2000` ; les tags ne contiennent pas `SMOKE_NO_CLAIMS`.
7. Fichiers inchangés : les 3 `*_source.csv` (= `8a2ec3a4…` / `a4c343a2…` / `f8ec238c…`) et les 3 légendes (= celles de `_fix`). Fichiers changés : seulement les 9 SVG/PDF/PNG, `FIGURE_CHECK.md` et `figure_manifest.json`.
8. Aucun des 17 fichiers ne contient `/home/`, `logs/pca_drift_contracts`, `fix_d7b` ou `render_full` : la provenance est indépendante du répertoire final.
9. Texte des trois figures :
   - `pdftotext` sur chaque PDF et grep sur chaque SVG, espaces normalisés ;
   - « equality test (n = 2000) » est présent et « n = 40 » absent ;
   - `SMOKE_NO_CLAIMS` est absent ;
   - `COV_SURROGATE_EXPLORATORY` figure seulement dans cov ;
   - `pdfinfo` donne le format attendu.
10. `FIGURE_CHECK.md` : strict PASS, et pour les 3 entrées `text_in_frame`, `legend_disjoint` et `ylim_covers` PASS, PNG (1620, 1050) PASS, issues none.

La cohérence PNG/PDF/SVG tient par construction : les trois formats sortent du même objet `Figure` (`figure_bytes`). Les points 9 et 10 la contrôlent.

**S5 — Sauvegarde et manifeste SHA initial.**
- `cp -a` des deux répertoires full vers `$L/backup/`.
- `$L/backup.sha256` doit égaler les lignes correspondantes de `inventory_before.txt`.
- `$L/render.sha256` enregistre les 17 fichiers rendus.

**S6 — Installation sans suppression.** Pour chacun des deux répertoires full finaux, noms conservés :
1. vérifier que la liste de ses noms est identique à celle de `render_full` ;
2. `cp -- $L/render_full/* <dir>/` : écrase en place les fichiers générés, sans `rm` ni `mv` de répertoire, mode 0644 conservé ;
3. `sha256sum -c $L/render.sha256` doit être tout OK ;
4. `verify_figures_dir` doit être vrai.

Contrôles finaux :
- `diff -r` des deux répertoires finaux et du rendu : identiques.
- En cas d'échec : restauration depuis `$L/backup/`, contrôle par `backup.sha256`, puis STOP.

**S7 — Contrôles globaux avec G1** (variable exportée pour tous).
- QA complet, `-rA --durations=0` (`$L/qa_after.log`) : **44 passed, 0 failed, 0 skipped**, et D3 trace le nouveau `_fix`.
- `tests/test_plot_figure_1.py` : vert.
- `.venv/bin/make check` (`$L/make_check.log`, en arrière-plan si plus de 10 min) : code 0.
  - Attendu : 37 passed, puis 545 + 44 = 589 passed et 5 skipped préexistants.
  - Aucun nouveau skip ; G1 exécuté.

**S8 — Inventaire APRÈS** (`$L/inventory_after.txt`, avec le diff contre AVANT).
- Seules différences admises :
  - le traceur ;
  - 11 fichiers de `_fix` (9 graphiques, `FIGURE_CHECK.md`, manifeste) ;
  - 14 de `full_2000_20261101` (les mêmes, plus ses 3 anciennes légendes à `5346b314`).
- Doivent rester identiques : les deux répertoires smoke, les runs, les tables, J1 (disque = index = `e315e537…`, 47 CRLF), D8 (`1ca7c3ae…`), `DEVIATIONS` et `PLAN.md` (`ed14c47a…`).
- `git status` et `git diff --stat` sont consignés ; Claude ne fait aucun stage.

**S9 — Rapport, puis arrêt.**
- Ajouter en fin de `docs/audits/PCA_CONTRACTS_VALIDATION.md` une section « 10. D7b fix measurement », en anglais. Elle contient :
  - l'autorité ;
  - le diff de 2 lignes ;
  - les journaux RED et GREEN, avec les node IDs ;
  - la commande de rendu et les contrôles S4 ;
  - les sauvegardes ;
  - le diff d'inventaire ;
  - le résultat 44/0/0 et `make check`.
- Les §1–9 restent inchangés : l'historique 43/1 au traceur `c40a5e77…` y reste. La nouvelle section qualifie `c40a5e77…` de hash historique du traceur et donne le nouveau.
- Ensuite : rapport au terminal et attente de Codex. Le wrapup-31 n'est rafraîchi que sur sa demande.

## 5. Arrêts

- **STOP immédiat** (constat et rapport, sans rerun) dans les cas suivants :
  - un échec non prévu, refus ou code de sortie non nul en S2–S7 ;
  - un render check FAIL ;
  - un écart en S4 (sources, légendes, `command`, `environment` ou blocs d'entrée) ;
  - un diff d'inventaire hors de la liste admise en S8.
- **Erreur QA de mon propre test :** au plus 3 corrections, chacune au ledger.
- **Après un STOP :** aucune autre mutation. Les sauvegardes restent dans `$L`.

## 6. Propriété et invariants

- **Écritures de Claude :**
  - `experiments/figures/plot_figure_1.py` (2 lignes) ;
  - les deux répertoires full (artefacts générés seulement) ;
  - D7b dans le fichier QA ;
  - la section 10 du rapport ;
  - `$L` (ignoré) ;
  - le wrapup-31, sur demande.
- **Hors de ma main :**
  - plan, GO, Git, reindex et commit restent à Codex ;
  - les fichiers du chercheur dans le worktree principal ne sont ni touchés ni indexés ;
  - pas de sous-agent, pas de Graphify ni jCodeMunch.
- **Vigilance pour la clôture Codex :**
  - Exporter `PCA_FULL2000_TRIALS` avant le hook de commit (`make check`). Sinon G1 y serait sauté pour disponibilité.
  - Les manifestes smoke non re-rendus gardent leurs traceurs historiques et n'ont pas `render.n_null`. Les rejouer depuis `records.render` avec le nouveau traceur lèverait `KeyError`. Aucun consommateur ne le fait.

## 7. Questions résiduelles (défaut entre crochets)

1. **QD1 — Source de n.** [`config.n_null` du manifeste]. Alternative : `n_holdout` du protocole validé, `int(proto_prefix[1][5])`. Le diff garde la même forme de 2 lignes, mais la sonde devrait alors altérer une copie de `aggregates.csv` (lignes HOLDOUT, `n` = "39") au lieu de `config`.
2. **QD2 — Manifeste.** `records.render.n_null` est ajouté sans changer `figures_schema = pca_drift_figures/1`. [oui]
3. **QD3 — Test QA.** D7b est étendu en place (SMOKE + sonde), sans nouveau test, avec 5 rendus en mémoire au total. [oui]
4. **QD4 — `make check`.** Exécuté par Claude en S7 avec la variable G1, avant la clôture Codex. [oui]
5. **QD5 — Rapport.** Section ajoutée en fin, en-tête « Status: STOP » et §1–9 inchangés. [oui] Alternative : une ligne de renvoi sous l'en-tête.
6. **QD6 — `docs/DEVIATIONS.md`.** Aucune entrée D7b : c'est un défaut d'étiquette, sans écart de protocole. [aucune]
7. **QD7 — Contenu de `full_2000_20261101`.** Il reçoit le même contenu vérifié que `_fix`. Son état antérieur (traceur `5346b314…`, bannière smoke) ne reste que dans Git et dans `$L/backup`. [oui]

## 8. Décision GO intégrée — Codex, 2026-11-06, 15:32 UTC

**GO du correctif D7b selon `prompts/GO-stream-31-fix.md`.** Cette décision remplace les mentions d'attente et tranche les questions du plan natif ci-dessus, archivé sans changement dans `logs/pca_drift_contracts/fix-d7b-native-plan.md` (SHA-256 `10beef540aa3ac4b2810c5751dddd71e2c6d80342d7a21451ccef0a8fcd02451`).

- **QD1–QD4 :** `config.n_null`, champ additif `render.n_null` sans changement de schéma, extension D7b en place (44 tests, cinq rendus mémoire), puis `make check` Claude avec G1. Les deux lignes du §3.1 sont le minimum nécessaire dans le seul traceur : le prompt d'implémentation autorise une ligne « si possible », et `render_figure` ne reçoit actuellement pas le manifeste. Ni introspection ni état global.
- **QD5 :** conserver l'évidence initiale 43/1, ses journaux, ses SHA et son STOP. Après mesure seulement, ajouter un statut courant et un renvoi au §10 en tête du rapport ; qualifier les §1–9 d'historiques. Préciser que `mean_t7` n'était pas dans l'assertion initiale D7b : D7a en avait un rendu mémoire altéré. Ne pas présenter `c40a5e77…` comme hash courant après correctif.
- **QD6–QD7 :** aucune entrée DEVIATIONS ; les deux dossiers full reçoivent le même rendu complet vérifié. Les deux dossiers smoke sont conservés octet pour octet et restent liés à leurs traceurs historiques ; aucun rejeu de leurs anciens `records.render` avec le nouveau code n'est revendiqué.
- **S0 :** le statut attendu comprend aussi les nouveaux plan et GO du correctif, possédés par Codex. Les fichiers antérieurs de plan/GO et les trois fichiers non suivis du chercheur restent intacts.
- **S1 :** RED limité à la régression D7b connue et autorisée. Aucun nouveau défaut producteur n'est un RED attendu. Aucun test ni contrat existant affaibli.
- **S3 :** lecture des sorties du runner, des tables, des sources pour leur hash, et des seules métadonnées de dates autorisée. Aucune ré-exécution du benchmark ou des tables ; les petits appels synthétiques sous `tmp_path` de la suite QA restent ceux déjà approuvés.
- **S4–S6 :** vérifier les empreintes au répertoire réellement contrôlé. Les listes `render.sha256` et de sauvegarde emploient des noms relatifs à leur racine ; exécuter `sha256sum -c` depuis chacun des deux dossiers finaux, sans recontrôler par erreur le seul dossier source. Comparer les inventaires après normalisation des préfixes. Les sauvegardes complètes sont contrôlées avant l'écrasement. Restauration seule autorisée si une installation est incomplète, puis STOP documenté.
- **S7 :** un passage du fichier de tests du traceur suffit après le changement ; ne pas le répéter inchangé avant `make check`. La QA complète utilise `PCA_FULL2000_TRIALS`, sans nouveau skip/xfail. Les cinq skips préexistants de la suite générale sont rapportés distinctement.
- **Clôture :** Claude livre le rapport et s'arrête ; Codex relit le diff et les preuves. Le wrapup natif est rafraîchi sur instruction Codex, puis réindexation AST seule, `make check`, commit et intégration contrôlés par Codex. Aucun autre producteur, résultat ou stream n'entre dans ce GO.
