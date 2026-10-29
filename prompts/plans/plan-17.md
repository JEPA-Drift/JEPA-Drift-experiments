# Plan — stream 17 : composant C partagé, IPCA et pipelines P4-C/P4-D — révision 3

Statut : **GO final reçu pour la révision 3 (2026-10-23)** ; exécution en mode auto. Worktree `~/JEPA-stream-17`,
branche `stream-17` = `main` = `c284823`.

## Décision GO intégrée (2026-10-23)

- **GO.** Accordé dans l'amorçage (`prompts/amorcage-17.md`), puis confirmé en session : « Les arbitrages Q1-Q10
  sont accordés » ; « l'implémentation a GO sous réserve du contrôle du plan ».
- **Q1 — worktree D4.** Retirer le lien `data/raw/eurofidai`. `data/derived/d4_eurofidai/` devient un répertoire
  réel avec sept liens absolus, un par fichier dérivé de l'arbre principal :
  `assets.json`, `chars.parquet`, `dates.npy`, `flags.csv`, `panel.parquet`, `ret_wide.npy`, `splits.yaml`.
  Aucune reconstruction ; `docs/manifests/d4_manifest.json` inchangé ; écart `C-worktree-d4`.
- **Q2 — bêta.** `c_beta_252` est utilisé tel quel. Son dénominateur fautif est chiffré dans
  `results/ipca/char_audit.csv` et consigné dans `C-D3-beta-denominator`. La correction des données revient à un
  autre stream.
- **Q7 du transfert 14→17.** 17 pose d'abord l'échafaudage générique (alignement C, masque, segment `pretrain`,
  `NEEDS_C`, `CHAR_CASES`, méta-test), puis ajoute IPCA. 14 intègre ensuite le commit de 17 et étend l'échafaudage.
- **Q3 à Q10 (défauts du plan).**
  - Q3 : cash-neutral « constant » seul.
  - Q4 : lignes `C-repr-rows` jusqu'à la fin du panel, sans statistique sur les lignes ≥ 2020.
  - Q5 : argmax du R² tenu à l'écart ; en cas d'égalité, le plus petit K.
  - Q6 : lignes D4 agrégées de `k_selection.csv` commitées.
  - Q7 : `Z-1` conservée.
  - Q8 : second moment non centré, racine symétrique.
  - Q9 : rangs fantômes utilisés tels quels, constat `C-D3-chars-phantom`.
  - Q10 : deux lignes de `CLAUDE.md`.
- **Ordre imposé.** D'abord le composant C partagé (`extract.py` et ses tests), puis IPCA, puis P4.
- **Corrections du GO technique (2026-10-23).**
  - §6.0 : après création de `prompts/plans/plan-17.md` et de `prompts/GO-stream-17.md`, `git status --porcelain`
    doit montrer exactement ces deux fichiers non suivis, et rien d'autre. L'arbre doit être vide après le commit.
  - §8 : les paires de référence D2/PCA sont comparées par `cmp`, qui fait échouer la vérification en cas de
    divergence. Afficher les SHA-256 ne suffit pas.
  - Le R² en cash-neutral est étiqueté **R² de rendements relatifs**. f_A est toujours estimé sur A seul.
  - Langues (`CLAUDE.md` l. 148-149) :
    - plan et revue GO en **français** ;
    - nouveaux audits en **anglais** : `docs/sections/ipca.md`, entrées nouvelles de `docs/DEVIATIONS.md`
      (consigne de l'amorçage, précédent `C-e10-*`), wrapup, journaux, en-têtes CSV ;
    - code, docstrings et commit en anglais.
  - `MPLBACKEND=Agg` dans toutes les vérifications, y compris `make check` et `git commit`, dont le hook lance
    `make check`.
- **GO final (2026-10-23).** Révision 3 approuvée.
  - Livrer d'abord le composant C partagé et ses tests, dans un commit vérifié.
  - Avertir le stream 14 dès que ce commit est prêt.
  - Garder effectives les portes D2/PCA (`cmp`) et la séparation pretrain/calib.
  - D'où R8 : deux commits.
- **Environnement.** Opus 5.5 à l'effort max, `.venv` exclusivement, aucun sous-agent. Après le
  `/mcp reconnect all` de l'utilisateur, Graphify (`graph_stats` : 3 317 nœuds) et jCodeMunch (`resolve_repo` :
  index du worktree) répondent. Je revérifie par appel avant la première écriture.
- **Arrêt.** Au commit local vérifié, avant fetch, fusion ou push.

## 1. Contexte

L'IPCA [Kelly, Pruitt & Su, 2019, *Characteristics are covariances*, JFE 134(3)] modélise x_t = C_tΓf_t + ε_t.
Les chargements C_tΓ sont connus en t−1. f_t est linéaire en x_t, donc impair, et ses flux de signe sont exacts
sous un nul centralement symétrique.

Le stream 17 livre trois choses :
- la représentation IPCA ;
- les pipelines P4-C (signes) et P4-D (énergie), utilisés par E4, E5 et E6 ;
- le chemin « caractéristiques » de l'extraction, partagé avec 14 (CA-T-JEPA) et 18 (CD-DFM), conformément à
  `prompts/handoff-14-to-17.md` et aux §2.7–2.8 et §3 du plan 14.

## 2. Vérifications faites (lecture seule)

- **8b sur `main`.** `24be667` et la fusion `33d847d` sont ancêtres de `stream-17`. Depuis le plan antérieur
  (`c8fe24d`), seuls l'E10 et des prompts ont changé ; `jepadrift/` est identique.
- **Bloquant infra, corrigé par Q1.** `git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x`
  renvoie rc 128 (« beyond a symbolic link »). Dans ce worktree, `test_gitignore_blocks_eurofidai` fait donc échouer
  `make check`.
- **Consommateurs de `extract.DATASETS`.**
  - `experiments/audit_information.py` (`default=sorted(DATASETS)`) ;
  - `experiments/e10_robustness.py` ;
  - la CLI de `pipelines`.

  Ajouter `d3_500` et D4 à ce registre changerait le défaut de l'audit du stream 11 (voir R2).
- **Outils.**
  - `.venv/bin/{python,pytest,pyflakes}` ; numpy 2.4.4, scipy 1.17.1, pandas 3.0.6.
  - `tests/` n'a pas de `__init__.py`.
  - `logs/` est ignoré par git ; les journaux suivis ont été ajoutés de force (précédent `logs/e10/run.log`).

## 3. Faits mesurés (sondes de cette session, lignes < 2020, sans écriture)

| panel | segment | jours | NaN ret. | N_t min/méd/max | NaN C (cellules observées) | jours déficients | min σ_min/σ_max(C̃) |
|---|---|---|---|---|---|---|---|
| d3_239 (N = 239) | pretrain | 2769 | 0 | 239/239/239 | 8 | 0 | 0,119 |
| d3_239 | calib | 941 | 0 | 239/239/239 | 24 | 0 | 0,265 |
| d3_500 (N = 503) | pretrain | 2769 | 15,77 % | 383/423/464 | 10 571 | 0 | 0,158 |
| d3_500 | calib | 941 | 5,90 % | 464/473/482 | 2 319 | 0 | 0,299 |
| D4 (session antérieure) | pretrain | 2823 | 4,0 % | 0/486/494 | 6 795 | 2 (N_t = 0) | — |
| D4 (session antérieure) | calib | 959 | 9,4 % | 132/459/477 | 2 151 | 0 | — |

- **Masque.** `in_universe` de `panel.parquet`, réindexé sur `dates.npy × assets.json`, coïncide avec
  `isfinite(ret)` sur `d3_239` et `d3_500`. Les chiffres D4 seront recalculés par le script de la tâche 4.
- **ALS (prototype, P = 4, pretrain).**
  - 1 à 146 itérations, au plus 0,27 s ; objectif non croissant ; ΓᵀΓ = I à 1e-15 près.
  - Sur chaque jour de calib, rang(C̃_tΓ_K) = K, et min σ_min/σ_max(C̃_tΓ) ≥ 0,26.
- **Imparité.** f(−x) = −f(x) au bit près sur 26 jours de calib de `d3_239` et sur 26 jours de `d3_500` avec NaN.
- **R² tenu à l'écart sur calib** (définition H6), indicatif. La ligne cash-neutral est un R² de rendements
  relatifs, non comparable aux autres :

| panel | cible | K = 1 | K = 2 | K = 3 | K = 4 | K* |
|---|---|---|---|---|---|---|
| d3_239 | rendements | 0,0547 | **0,0606** | 0,0566 | 0,0509 | 2 |
| d3_239 | rendements relatifs (cash-neutral) | 0,0728 | **0,0825** | 0,0810 | 0,0792 | 2 |
| d3_500 | rendements | 0,0456 | 0,0649 | **0,0688** | 0,0676 | 3 |
| D4 (session antérieure) | rendements | 0,0254 | **0,0266** | 0,0198 | 0,0158 | 2 |

- **R² dans l'échantillon.** Il porte sur les actifs servant à estimer f_t et croît avec K : de 0,068 à 0,109 sur
  `d3_239` calib.
- **Défaut du bêta (Q2).** Dans `sp500._compute_chars`, `sx, sy, … = _rolling_xy_sums(y, mkt, …)` inverse les
  sommes. Le dénominateur devient Σm² − (Σr_i)²/n au lieu de Σm² − (Σm)²/n.
  - `eurofidai.build` réutilise cette fonction : D4 est touché aussi.
  - Sur `d3_239`, les 32 NaN de `c_beta_252` (8 en pretrain, 24 en calib) viennent de dénominateurs fautifs
    négatifs.

## 4. Conception

**H1 — Caractéristiques.**
- Principal : les 4 colonnes `sp500.CONTINUOUS_CHARS`, sélectionnées par nom (P = 4).
- Une caractéristique NaN sur une cellule observée vaut 0 et est comptée (`C-inject-F2-nan`). Une valeur ±inf
  lève `ValueError`.
- Les 15 colonnes (GICS statique, `C-D3-gics-static`) ne servent qu'aux lignes
  `protocol = retrospective_gics_static` de `k_selection.csv`. Ces lignes portent sur D3 seulement, sans
  cash-neutral (R5). Ni l'extraction ni P4 n'exposent les GICS.

**H2 — Rendements absents.**
- NaN dans X = rendement absent ; un zéro est une observation.
- `Representation.missing = False`. `_check(a, ndim, name, missing=False)` n'accepte NaN que si `missing` ; ±inf
  est toujours refusé. IPCA déclare `missing = True`. `pipelines._panel(a, missing=False)` applique la même règle.
- PCA, DegreeZero et Ranks refusent toujours NaN.
- `chars.load_universe(dataset, rows)` charge le masque ; l'appelant écrit `np.where(in_universe, ret, nan)`.
- Chaque jour, IPCA n'utilise que O_t = {i : x_{i,t} fini}, sans imputation de rendement.

**H3 — Identifiabilité, borne de K, jours déficients.**
- K ≤ min(K_max, P), avec K_max = 4 par défaut. En principal, K = 5 ou 6 lève `ValueError`, sans pseudo-inverse.
- Un jour est utilisé si et seulement si `np.linalg.matrix_rank(C̃_t[O_t]) == P` (C̃ centré en cash-neutral).
  La tolérance vaut σ_max·max(N_t, P)·ε (R1).
- Comme Γ est orthonormé, ce critère implique rang(C̃_tΓ_K) = K. Les tests vérifient cette égalité chaque jour,
  et min σ_min/σ_max(C̃_tΓ) est consigné (`min_rcond_calib`).
- Un jour déficient est exclu de l'ALS (pretrain), du score et du blanchiment (calib), puis listé par date dans le
  sidecar. À la transformation, il donne z = 0 : le signe est départagé par une pièce et l'énergie reste
  conservatrice.
- La règle ne dépend que de O_t et de C_t : elle est la même pour x et pour −x.

**H4 — ALS.**
- Initialisation : les K premiers vecteurs singuliers droits de [y_t/N_t]_t.
- Pas f : f_t = (ΓᵀW_tΓ)⁻¹Γᵀy_t, avec W_t = C̃ᵀC̃ et y_t = C̃ᵀx̃.
- Pas Γ : vec(Γ) = [Σ_t f_tf_tᵀ ⊗ W_t]⁻¹ vec(Σ_t y_tf_tᵀ). Un système singulier lève `ValueError`.
- Arrêt sur le projecteur : ‖QQᵀ − Q₋Q₋ᵀ‖_F ≤ 1e-10. Après 10 000 itérations, `RuntimeError`.
- Normalisation finale : ΓᵀΓ = I ; (1/T)Σf_tf_tᵀ diagonale décroissante ; dans chaque colonne de Γ, la plus grande
  entrée en valeur absolue est positive.
- L'objectif Σ_t(‖x̃_t‖² − f_tᵀΓᵀy_t) est non croissant.

**H5 — Deux segments.**
- `IPCA.pretrain(X, C, dates)` est le crochet propre à IPCA. Il estime Γ_k pour chaque K candidat et consigne dans
  `sidecar()["pretrain"]` : dates, jours utilisés et exclus, `x_sha256`, `c_sha256`, NaN imputés, itérations et R²
  dans l'échantillon.
- `fit` (calib) choisit K et le blanchiment. `_day` n'utilise que x_t et C_t.
- L'état haché contient Γ_{K*}, W et, en cash-neutral, s_m.

**H6 — R² tenu à l'écart et choix de K.**
- Partage déterministe des colonnes d'actifs par parité d'indice : A (paires) et B (impaires).
- Pour chaque jour de calib utilisé et chaque sens (A→B, B→A) :
  - f_t^A est estimé sur O_t ∩ A seul ;
  - la prédiction est x̂_B = C̃_BΓf_t^A ;
  - le sens est sauté et compté (`fold_skips`) si rang(C̃_A) < P.
- R²_ho = 1 − Σ(x̃_B − x̂_B)²/Σx̃_B², sur les deux sens cumulés (R² total non centré).
  - Principal : x̃ = x. Le R² porte sur les **rendements** (`r2_target = returns`).
  - Cash-neutral : chaque pli est centré par ses propres moyennes observées. A est centré par m_A et c̄_A pour
    estimer f_A ; la cible de B est x_B − m_B, avec C̃_B = C_B − 1c̄_Bᵀ. Le R² porte alors sur les **rendements
    relatifs** (`r2_target = relative_returns`). x_B n'entre jamais dans f_A.
- Γ vient de pretrain : la séparation est temporelle pour Γ (embargo de 65 jours) et transversale pour f_t.
- K* = argmax R²_ho ; une égalité à 1e-12 près donne le plus petit K.
- Les R² dans l'échantillon (calib, pretrain) portent l'étiquette « in-sample (assets used for f_t) » et la même
  cible.

**H7 — Blanchiment et têtes.**
- M = (1/T_c)Σf_tf_tᵀ sur les jours de calib utilisés, non centré ; W = M^{−1/2}, racine symétrique.
- z_odd = Wf_t (linéaire homogène, sans centrage ni intercept) ; z_even = z_odd².
- `channels = {"residual": [0..K−1]}`.

**H8 — Cash-neutral « constant ».**
- C̃_t = C_t[O_t] − 1c̄_tᵀ et x̃_t = x_t[O_t] − m_t, où c̄_t et m_t sont les moyennes sur O_t.
- Le marché reste le canal 0 : m_t/s_m, avec s_m la RMS non centrée de calib. `channels = {"market": [0],
  "residual": [1..K]}`.
- Invariances : z_facteurs(x + c·1) = z_facteurs(x) et m(x + c·1) = m(x) + c.

**H9 — Pipelines P4.**
- P4-C = (`_rep_ipca`, `_stream_signs`, `_detect_p3c`, `_cal_p3c`). Lectures anytime-valid (dictionnaire) et exact
  (un canal, treillis) ; pas de mélange.
- P4-D = (`_rep_ipca`, `_stream_p3d`, `_detect_p3d`, `_cal_p3d`), lecture bootstrap sur calib.
- Défauts : `K="select"`, `cash_neutral=None`.
- C voyage dans `split_rows(dates, splits, C=None)` : la clé `"C"`, alignée sur les lignes comme `"dates"`,
  n'est ajoutée que si C est fourni.
- `fit_pipeline` appelle le crochet `pretrain`, puis `fit`. `_cal_p3d` transforme les lignes de calib avec C.
  `null_check` transforme X avec `splits["C"]`.
- La surveillance P4 prend un dict Z (`Z = state["rep"].transform_panel(X, C)`). Un panel X est refusé par
  `IPCA._day` (« needs C_t »).
- `_detect_p3c` et `_cal_p3c` lisent `spec.get("mixture_s2")`.

**H10 — Extraction (échafaudage partagé du transfert).**
- `NEEDS_C` (frozenset) et `extract(rep, X, dates, splits, out_dir, dataset, C=None)`, qui refuse un C mal aligné
  (`C.shape[:2] != X.shape`).
- Déroulement : crochet `hasattr(rep, "pretrain")` sur les lignes pretrain, puis `fit` sur calib (X et C), puis
  transformation des lignes [premier jour de pretrain, fin du panel) avec C.
- La clé de sidecar `c_sha256` n'apparaît que sur le chemin C : les octets D2/PCA sont inchangés.
- CLI :
  - pour `NEEDS_C`, X = `where(load_universe, ret, nan)` et C = `chars.load_continuous_chars` ;
  - D2 lève « D2 has no characteristics » ;
  - `--K select|int|mp` et `--cash-neutral constant`, filtrés par le contrôle `inspect.signature` existant ;
  - `CHAR_DATASETS = {d3_500, d4_eurofidai}`, réservé à `NEEDS_C` (R2).

**H11.** `Z-1` est conservée. `missing` et `pretrain` sont documentés comme extensions rétrocompatibles.

**H12 — Sélection de K consignée : `experiments/ipca_k_selection.py`.**
- Argparse ; journal `logs/ipca/k_selection.log` ; CSV écrits par `pipelines.save_fair_csv`.
- Garde bloquante : aucune ligne ≥ 2020-01-01.
- Grille :
  - {d3_239, d3_500, D4} × principal × cash_neutral ∈ {None, constant} × K ∈ {1..4} ;
  - D3 × GICS rétrospectif × K ∈ {1..6} (K_max = 6, P = 15).
- Colonnes : `dataset, protocol, chars, cash_neutral, r2_target, K, selected, r2_heldout_calib,
  r2_insample_calib, r2_insample_pretrain, days_pretrain, days_calib, excluded_pretrain, excluded_calib,
  fold_skips, c_nan_imputed_pretrain, c_nan_imputed_calib, als_iterations, projector_change, min_rcond_calib,
  n_assets, state_sha256`.
- Le script écrit aussi `char_audit.csv` (R6).

**Précisions de cette révision.**
- **R1.** La règle de rang passe par `matrix_rank` (SVD de C̃). La formule antérieure λ_min(W_t) >
  λ_max(W_t)(max(N_t,P)ε)² plaçait sa tolérance sous le bruit d'arrondi d'`eigvalsh`.
- **R2.** `extract.DATASETS` reste inchangé ; `CHAR_DATASETS` ne sert que le chemin C.
- **R3.** Les noms du transfert (`NEEDS_C`, `CHAR_CASES`, `extract(..., C=None)`, crochet `pretrain`) remplacent
  l'attribut `needs_chars`. La fixture D3 est commune avec le plan 14 : `d3_239` < 2020, avec 128 jours de
  pretrain, 120 jours de calib et les 60 jours suivants, X masqué, C sur 4 colonnes.
- **R4.** L'échafaudage est testé avant IPCA par un témoin propre aux tests (`_CharProbe`). Jusqu'à l'ajout d'IPCA,
  `NEEDS_C = CHAR_CASES = ∅`, et le méta-test tient à chaque étape.
- **R5.** Le R² cash-neutral est un R² de rendements relatifs (H6). La sensibilité GICS tourne sans cash-neutral :
  les indicatrices centrées sont colinéaires (rang ≤ P − 1 chaque jour).
- **R6.** Les chiffrages de Q2 et Q9 sont tracés dans `results/ipca/char_audit.csv` (format long `dataset, segment,
  metric, value`, D3 et D4).
  - Bêta : cellules comparées ; écarts de reproduction du stocké ; erreur relative (médiane, p99, max) face au bêta
    MCO ; part des rangs modifiés ; décalage maximal de rang ; NaN dus à la formule ; dénominateurs fautifs négatifs.
  - Fantômes : titres classés sans rendement ; |moyenne des rangs observés| maximale.
- **R7.** Journaux `logs/ipca/` ajoutés par `git add -f`, chemins explicites, aucun chemin absolu.
- **R8.** Deux commits Conventional Commits, sans trailer.
  - Commit 1, composant C partagé : traces, Q1, `base`, `chars`, `extract`, tests, docs d'interface,
    `C-worktree-d4`. Il est suivi de l'avertissement au stream 14.
  - Commit 2 : IPCA, P4, audits, docs, écarts.
  - Avant chaque commit : wrapup rafraîchi et `make check`. Après chaque commit : arbre vide.

## 5. Fichiers

| fichier | changement |
|---|---|
| `jepadrift/representations/base.py` | `missing` ; `_check(..., missing)` (≈ 5 lignes) |
| `jepadrift/data_loader/chars.py` | `load_universe(dataset, rows=None)`, `load_continuous_chars(dataset, rows=None)` |
| `jepadrift/representations/extract.py` | `NEEDS_C`, `CHAR_DATASETS`, chemin C, crochet pretrain, `c_sha256`, CLI ; puis `"ipca"` |
| `jepadrift/representations/ipca.py` (nouveau, numpy seul) | `IPCA(K="select", K_max=4, cash_neutral=None)` : `pretrain`, `_fit`, `_day`, `sidecar` ; `design`, `als`, `heldout_r2` ; `TOL`, `MAX_ITER` |
| `jepadrift/pipelines.py` | P4-C/P4-D (`DEFAULTS`, `READINGS`, `PIPELINES`, `null_specs`, `make_spec`), `_rep_ipca`, `split_rows(C=)`, `_panel(missing)`, `fit_pipeline`, `_cal_p3d`, `null_check`, `.get("mixture_s2")`, CLI P4 |
| `experiments/ipca_k_selection.py` (nouveau) | H12, R6 |
| `tests/test_representations.py` | tests du chemin C (témoin), `missing`, `load_universe` ; boucle D2 sur `REGISTRY − NEEDS_C` |
| `tests/test_contracts.py` | script D2 sur `REGISTRY − NEEDS_C` ; `d3_char_data()`, `CHAR_CASES`, méta-test, contrats D3 |
| `tests/test_ipca.py` (nouveau) | §7 |
| `results/ipca/` | `k_selection.csv`, `char_audit.csv`, `alarms_P4-{C,D}_d3_239_null.csv`, `runs_P4-{C,D}_d3_239_null.json` |
| `logs/ipca/` | `k_selection.log`, `extract.log`, `null_P4-{C,D}_d3_239.log` |
| `data/derived/{d3_239,d3_500}/z_<hash>.{npz,json}` | extractions IPCA (D4 locale, ignorée) |
| `docs/sections/ipca.md` (nouveau, anglais) | modèle, ALS, masque, rang, R² tenu à l'écart (rendements / rendements relatifs), K retenus, blanchiment, cash-neutral, têtes, P4, tests, références |
| `docs/sections/interface_Z.md`, `contracts.md`, `pipelines.md` (anglais) | chemin C, `NEEDS_C`/`CHAR_CASES`, `missing`, IPCA, P4 |
| `docs/DEVIATIONS.md` (entrées nouvelles en anglais) | `C-IPCA-design`, `C-IPCA-K`, `C-D3-beta-denominator`, `C-D3-chars-phantom`, `C-worktree-d4` |
| `CLAUDE.md` | 2 lignes de « Repository layout » : `ipca` ; P4-C, P4-D |
| `prompts/plans/plan-17.md` (français), `prompts/GO-stream-17.md` (français, messages verbatim), `prompts/wrapups/wrapup-17.md` (anglais) | traces |

Hors dépôt et non commités : le lien `data/raw/eurofidai` (retiré) et les 7 liens sous `data/derived/d4_eurofidai/`
(ignorés).

**Partage avec 14, 18 et 23.** L'intégration est successive, 17 d'abord (Q7).

| fichier | 17 | 14 | 18 | 23 |
|---|---|---|---|---|
| `extract.py` | échafaudage C, `CHAR_DATASETS`, `ipca` | rebase ; `ca_tjepa` paresseux, `--ckpt`, `--D` | rien | — |
| `tests/test_contracts.py` | `d3_char_data`, `CHAR_CASES`, méta-test, contrats D3, boucle D2 | son cas, gardes torch | rien | — |
| `tests/test_representations.py` | témoin C, boucle D2 | rien de plus | rien | — |
| `base.py`, `chars.py` | `missing` ; `load_universe`, `load_continuous_chars` | lecture | rien | — |
| `pipelines.py` | P4, `split_rows(C=)`, crochet pretrain | — | pas d'entrée P4 avant sa garde et l'intégration de 17 | consomme P4-D après fusion (`split_rows(..., C=C)`, `fit_pipeline`, dict Z) |
| `interface_Z.md`, `contracts.md`, `DEVIATIONS.md`, `CLAUDE.md` | ajouts | ajouts | `C-CDDFM-stop` | — |

## 6. Exécution après le GO final (TDD : test rouge → code → vert)

0. **Traces et worktree.**
   1. Revérifier Graphify et jCodeMunch par appel. Charger `superpowers:test-driven-development`.
   2. Écrire `prompts/plans/plan-17.md` (ce plan, en français, chemins en `~/`) et `prompts/GO-stream-17.md`
      (en français, messages verbatim, chemins absolus du répertoire personnel écrits `~`).
   3. Appliquer Q1 :
      ```bash
      test -L data/raw/eurofidai && rm data/raw/eurofidai
      mkdir data/derived/d4_eurofidai
      # puis, pour chacun des 7 fichiers :
      ln -s ~/JEPA-Drift-experiments/data/derived/d4_eurofidai/<f> data/derived/d4_eurofidai/<f>
      ```
   4. Contrôles :
      - `git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x` doit sortir avec rc 0 ;
      - `git status --porcelain` doit valoir **exactement** `?? prompts/GO-stream-17.md` puis
        `?? prompts/plans/plan-17.md` ; toute autre ligne arrête l'exécution (§8).
1. **Composant C partagé.**
   - Code : `base.missing`, `chars.load_universe`, `chars.load_continuous_chars`, chemin C d'`extract.py` avec
     `NEEDS_C = frozenset()`.
   - Tests : boucles D2, `CHAR_CASES = {}`, méta-test.
   - Porte : `make check` vert, et `cmp` octet à octet des réextractions D2/`d3_239` PCA contre les références
     commitées (§8).
   - Docs d'interface (`interface_Z.md`, `contracts.md`) et entrée `C-worktree-d4`.
   - Wrapup partiel `prompts/wrapups/wrapup-17.md`, puis **commit 1** :
     `feat(extract): shared characteristic path for C-driven representations (stream 17)`.
   - Vérifier que `git status --porcelain` est vide, puis **avertir le stream 14** (`SendMessage`) avec le hash, les
     fichiers et l'API : `NEEDS_C`, `CHAR_CASES`, `d3_char_data`, `extract(..., C=None)`, crochet `pretrain`,
     `missing`, `load_universe`, `load_continuous_chars`.
2. **IPCA.**
   - Ordre : ALS et normalisation → masque → jours déficients → R² tenu à l'écart et choix de K → blanchiment →
     cash-neutral → têtes et sidecar.
   - Enregistrement : `REGISTRY["ipca"]`, `NEEDS_C = {"ipca"}`, `CHAR_CASES["ipca"]`.
   - Extractions `d3_239` et `d3_500` (commitées) et D4 (locale), chacune deux fois, avec `cmp` des deux sorties
     (§8) ; journal `logs/ipca/extract.log`.
3. **P4.** Code de H9, tests de câblage, puis contrôles nuls CLI P4-C et P4-D sur `d3_239` (500 réplicats) vers
   `results/ipca/` et `logs/ipca/`. Un FAIL déclenche un arrêt D3 et un rapport, sans réglage.
4. **Audits.** `experiments/ipca_k_selection.py` produit `k_selection.csv` et `char_audit.csv` ; des tests relient
   le code aux CSV.
5. **Documentation et écarts** (§5) : audits en anglais.
6. **Fin.**
   1. Wrapup anglais `prompts/wrapups/wrapup-17.md` : Context, Validated Results (SHA-256 compris), Errors and Dead
      Ends, Current State, Vigilance Points, Recommendations.
   2. `tools/reindex_graphify_jcodemunch.sh`, puis `make check` complet sous `MPLBACKEND=Agg`.
   3. Indexer les fichiers par chemin explicite. Contrôles sur l'index : aucun chemin D4, aucun chemin absolu du
      répertoire personnel, aucun fichier de plus de 50 Mo.
   4. **Commit 2** : `feat(ipca): IPCA representation, P4-C and P4-D pipelines, K selection (stream 17)`, puis
      exiger que `git status --porcelain` soit **vide**.
   5. **Arrêt avant fetch, fusion ou push.** Transmettre le diff, les vérifications, les SHA-256 et le wrapup.

## 7. Tests (budget ajouté à `make check` ≤ 45 s, mesuré et consigné)

**Étape 1 — composant C partagé.**
- `test_extract_char_path_alignment`. Le témoin `_CharProbe` (`missing = True`, crochet `pretrain`, z = moyenne
  observée) reçoit exactement les lignes pretrain et calib, X et C alignés. La transformation porte sur les lignes
  [first:) avec C[first:]. NaN reste absent (un remplissage par zéro donnerait un autre z). `c_sha256` est présent,
  et absent sur le chemin C=None.
- `test_extract_rejects_misaligned_C`.
- `test_missing_flag` : NaN accepté seulement si `missing` ; ±inf toujours refusé ; PCA et Ranks refusent NaN.
- `test_load_universe_matches_finite_returns` : `d3_239` et `d3_500` < 2020 ; D4 s'il est présent (sinon le test
  est sauté).
- `test_monitor_perturbation_keeps_state` et le script de déterminisme D2 bouclent sur `REGISTRY − NEEDS_C`.
- `test_char_registries_agree` : `NEEDS_C == set(CHAR_CASES) ⊆ REGISTRY`.
- Contrats D3, paramétrés par `CHAR_CASES` :
  - non-anticipation ;
  - imparité ≤ 1e-6 à C figé ;
  - absence de statistique de test : reconstruction par le constructeur, lignes ultérieures perturbées,
    `state_hash` et `normalization` inchangés ;
  - segment déclaré (dates, jours, `x_sha256`, `c_sha256` de `fit`) ;
  - déterminisme sur 2 sous-processus : `state_sha256` et SHA-256 de Z identiques.

**Étape 2 — IPCA (`tests/test_ipca.py`).**
- `test_recovery_principal_angles` : données synthétiques P = 4, K = 2, N = 150, T = 1200, 15 % de NaN plus un bloc
  manquant. Angles principaux (`scipy.linalg.subspace_angles`) < 5° ; `K="select"` donne 2.
- `test_als_projector_stopping` : deux initialisations (tournée et de signes opposés, `G0`) donnent le même
  projecteur (≤ 1e-8) et le même Γ normalisé. L'objectif est non croissant. Si `max_iter` est atteint,
  `RuntimeError`.
- `test_missing_is_not_zero` : un NaN équivaut au retrait de l'actif (lstsq explicite, 1e-12). Un zéro change z.
  Un jour tout-NaN donne z = 0, fini. ±inf est refusé.
- `test_rank_bound_and_deficient_days` :
  - K = 5 avec P = 4 lève `ValueError` ;
  - les candidats sont 1..min(K_max, P) ;
  - un jour avec N_t < P, ou une colonne constante en cash-neutral, est exclu, daté et donne z = 0 ;
  - rang(C̃_tΓ) = K sur tous les jours utilisés.
- `test_heldout_r2_definition` : un recalcul indépendant (boucle lstsq) concorde à 1e-10, en principal et en
  cash-neutral (rendements relatifs). Perturber x_B ne change pas f_A. `r2_target` est déclaré.
- `test_whitening_uncentered` : (1/T_c)Σzzᵀ = I (1e-10) sur calib ; z(0) = 0.
- `test_odd_head_exact` : φ(−x;C) = −φ(x;C) au bit près, en principal et en cash-neutral, y compris les jours avec
  NaN. La tête paire est symétrique.
- `test_cash_neutral_invariance`, `test_state_frozen_and_non_anticipation`.
- `test_extract_monitor_rows_do_not_move_state` : les lignes ≥ 2020 de X et de C sont remplacées par des tirages
  synthétiques, comme dans le test D2.
- `test_extract_cli_refuses_d2`.

**Étape 3 — P4 (`test_p4_wiring`).**
- `make_spec` : défauts et lectures ; l'exact exige un seul canal ; `mixture_s2` est refusé.
- `fit_pipeline` appelle `pretrain` puis `fit` avec `split_rows(C=)`.
- Un dict Z est accepté ; un panel X est refusé.
- Niveau exact du treillis ; Γ^op de P4-D.
- Specs et `run_id` de P3 inchangés.

**Étape 4 — audits.**
- `test_real_d3_239_selection` : K, R², `r2_target` et comptes de NaN égaux aux lignes `d3_239` de
  `k_selection.csv`, lu avec `float_precision="round_trip"`.
- `test_beta_denominator_reproduces_stored` : la formule fautive reproduit `c_beta_252` au bit près sur
  `d3_239` < 2020, et la formule MCO s'en écarte.

## 8. Commandes de vérification (toutes échouent en cas d'écart)

```bash
export MPLBACKEND=Agg OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42
MAKEBIN=~/miniforge3/pkgs/make-4.4.1-h1114479_4/bin; SCRATCH=<scratchpad de session>
REF_D2=z_85147fd9f553130ea70a7492770fa3ea4b068f0edf421d878a9e31bed7296f3d
REF_D3=z_6c44d64a3bf139beeca0939ab0ba821004796a053ec81e9952d44c7ac37ace3f

# §6.0 : après Q1, exactement les deux traces non suivies
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
test "$(git status --porcelain)" = "$(printf '?? prompts/GO-stream-17.md\n?? prompts/plans/plan-17.md')" \
  || { git status --porcelain; exit 1; }

# tests ciblés
.venv/bin/pytest -q tests/test_ipca.py tests/test_contracts.py tests/test_representations.py

# octets D2/PCA inchangés : cmp échoue sur toute divergence ou tout fichier manquant
.venv/bin/python -m jepadrift.representations.extract --dataset d2_us97 --rep pca --mode factor --out $SCRATCH/ref_d2_us97
.venv/bin/python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor --out $SCRATCH/ref_d3_239
for f in d2_us97/$REF_D2.npz d2_us97/$REF_D2.json d3_239/$REF_D3.npz d3_239/$REF_D3.json; do
  cmp "$SCRATCH/ref_${f%%/*}/${f#*/}" "data/derived/$f" || { echo "D2/PCA divergence: $f"; exit 1; }
done

# extractions IPCA : deux exécutions identiques, puis la sortie retenue identique à la copie de contrôle
for d in d3_239 d3_500 d4_eurofidai; do
  for k in 1 2; do .venv/bin/python -m jepadrift.representations.extract --dataset $d --rep ipca --out $SCRATCH/ipca_${d}_$k; done
  for f in $SCRATCH/ipca_${d}_1/*; do cmp "$f" "$SCRATCH/ipca_${d}_2/${f##*/}" || exit 1; done
  .venv/bin/python -m jepadrift.representations.extract --dataset $d --rep ipca | tee -a logs/ipca/extract.log
  for f in $SCRATCH/ipca_${d}_1/*; do cmp "$f" "data/derived/$d/${f##*/}" || exit 1; done
done

# audits et contrôles nuls (verdict PASS exigé)
.venv/bin/python experiments/ipca_k_selection.py --out results/ipca --log-dir logs/ipca
.venv/bin/python -m jepadrift.pipelines --pipeline P4-C --dataset d3_239 --null-check --reps 500 --out results/ipca --log-dir logs/ipca
.venv/bin/python -m jepadrift.pipelines --pipeline P4-D --dataset d3_239 --null-check --reps 500 --out results/ipca --log-dir logs/ipca

# check complet (< 300 s, durée consignée), contrôles de l'index, commit, arbre vide
PATH="$MAKEBIN:$PATH" make check
git diff --cached --name-only | grep -E '^data/(raw/eurofidai|derived/d4_eurofidai)/' && exit 1
git diff --cached --name-only -z | xargs -0 grep -l "$HOME/" && exit 1
PATH="$MAKEBIN:$PATH" git commit -F <message>        # le hook pre-commit relance make check sous MPLBACKEND=Agg
test -z "$(git status --porcelain)" || { git status --porcelain; exit 1; }
```

## 9. Risques résiduels

- Γ, K et les R² héritent du bêta fautif (Q2) et des rangs fantômes de `d3_500` (Q9) ; ils sont à réexécuter après
  correction des données. Le biais de survie de D3 et de D4 (`C-D3-survivor-correction`, `C-D4-survivor`) demeure.
- Des conflits de fusion avec 14 sont attendus sur `extract.py` et `test_contracts.py` ; 14 rebase sur 17 (Q7).
- Le crochet `hasattr(rep, "pretrain")` est un contrat implicite, documenté dans `interface_Z.md`.
- Les tests EUROFIDAI réels s'exécutent désormais dans ce worktree : `make check` sera plus long.
- Les empreintes d'extraction dépendent de la pile numérique (`.venv`, numpy 2.4.4).

## 10. Références

- Kelly, B., Pruitt, S. and Su, Y. (2019). Characteristics are covariances: A unified model of risk and return.
  Journal of Financial Economics, 134(3), 501–524.
- Article C, Section 3 : lemme « Whitening by an odd encoder », Proposition « Absorption ».
