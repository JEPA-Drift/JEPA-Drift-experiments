# Plan — stream 14 : CA-T-JEPA v2 (environnement torch isolé, cœur synthétique) — révision 4 + GO-A

## Contexte
La directive v2 `prompts/streams/01_STREAM_14_REWRITE_BOTTLENECK.md` du checkout principal (SHA-256
`1b5f2f8e92ba131f9e2845687e82a815b0c18674b85766af07662e008a9362c3`, non modifiée) est imposée par le chercheur : goulot
natif compact alimentant le prédicteur, masquage visible-only, encodeur cible EMA à l'entraînement, encodeur de contexte
figé à l'extraction, canal marché séparé, ACP post-JEPA réservée aux ablations. Ce plan ouvre une nouvelle séquence
plan/GO ; il ne modifie ni `prompt-14-ca-tjepa.md`, ni `amorcage-14.md`, ni les GO antérieurs.

## Décision GO intégrée
GO-A : `prompts/GO-stream-14-A.md` (SHA-256 `35acb12ba5d64140048400d48085456c38c270d2d80ca2bde0cad4a52fdd0ecf`), commité
avec le stream. Il autorise P0, P1 et 2A uniquement. 2B, données D3 réelles, fichiers sources partagés, intégration,
fetch, fusion, push et streams 16/22 restent bloqués. Corrections intégrées :
1. **U5** — quatre médianes estimées sur le seul segment d'entraînement interne de pretrain ; dictionnaire figé de
   16 codes binaires plus `nochar`, schéma de clés `SeedSequence`, règles d'égalité, groupes vides ou absents,
   sélection reproductible et repli visant 30–50 % d'actifs masqués ; état sauvegardé dans le checkpoint ; tests
   synthétiques couvrant groupes vides et surdimensionnés (règles ci-dessous).
2. **U9** — `make j1` peut modifier trois sorties suivies : `results/e2/e2_cells.csv`, `results/e2/e2_j1_summary.txt`,
   `logs/e2/run.log`. Instantané avant J1, vérification CRLF natif et SHA-256 de référence, restauration des seules
   modifications générées dans ces trois fichiers. Statut Git vide non exigé (lock et fichiers d'implémentation présents).
3. **U12/U13** — toute archive ou métadonnée exacte manquante : STOP, aucune substitution de build, canal ou source ;
   seul `solveB.json` vérifié (SHA-256 `df071043e438f5ef38e7bafdc104372db800c05eed8961c76f5fead05ef85ef9`) fait foi.
   **U14** reste ouvert pour GO-B ; aucune donnée réelle n'est lue sous GO-A.
Arbitrages antérieurs intégrés : QB1–QB7, U1–U11 (révision 4). MCP `graphify` et `jcodemunch` reconnectés et appelés
avec succès avant implémentation (graph_stats ; resolve_repo).

## Faits vérifiés (lecture seule, 2026-10-28)
- `solveB.json` (scratchpad du stream 14, 2026-10-23) : 65 enregistrements FETCH = 65 LINK, 65 noms distincts, 65 URL
  conda-forge (`linux-64`, `noarch`), 65 SHA-256, 195,5 Mo ; python 3.12.9 `h9e4cc4f_0_cpython`, numpy 2.4.4
  `py312h33ff503_0`, pytorch 2.14.1 `cpu_generic_py312_h29917d7_0`, libtorch `cpu_generic_hbc98363_0`, libstdcxx/libgcc
  15.1.0 `h8f9b012_5`/`h767d61c_5`, llvm-openmp 23.1.4, libopenblas 0.3.34 `openmp_*`, nomkl.
- Archives : 65/65 présentes dans le scratchpad `condapkgs` de la session tools, 65/65 SHA-256 conformes ; cache
  repodata conda-forge `noarch` et `linux-64` (2026-10-22) présent. Emplacement volatil (/tmp).
- conda 26.3.2 : `conda list --explicit --sha256` écrit `url#<64 hex>` ; le parseur explicite accepte ce format.
- `.venv/bin/make` → `jepa-make` (exécutable) ; le `Makefile` résout `python`, `pytest`, `pyflakes` par `PATH`.
- Stream 17 : HEAD `f67accf`, fichiers partagés modifiés non commités, arrêt D3 sur le null P4-D (non traité ici).

## Conception (synthétique sous GO-A)
- **Prétraitement figé (numpy, float64)** sur les lignes d'entraînement interne (dates < `validation_start`, moins les
  65 derniers jours avant cette date) : s_i = RMS des valeurs observées (STOP si moins de 63 observations, seuil jamais
  assoupli) ; b = PC1 de norme 1 de la matrice des seconds moments de u = x/s, absents remplis par 0
  (`stats.covariance.eigh_desc`, signe Σb ≥ 0) avec diagnostics de couverture ; médianes m_k des quatre
  caractéristiques sur les cellules présentes et finies.
- **Neutralisation visible-only (référence minimale)** : f̂(V) = b_Vᵀu_V/(b_Vᵀb_V + λ_f), e_i = u_i − b_i f̂(V) ;
  aucune statistique transversale de la coupe complète n'atteint le contexte.
- **Réseau** : jeton = MLP([e_i, C_i]) (C passé par `impute_zero`) ; encodeur de contexte sur les seuls visibles
  (entrées masquées remplacées par 0 avant le MLP, `src_key_padding_mask`) : 3 couches pré-LN, d_model 64, 4 têtes,
  FFN 256, dropout 0, LN finale, sans encodage de position ni BatchNorm. Goulot : moyenne sur V → Linear(64→d) = z_ctx.
  Prédicteur : MLP à 2 couches sur [z_ctx, C_j] par actif masqué, sans accès aux jetons de contexte. Cible : copie EMA
  (MLP de jeton + encodeur + LN) sur tous les actifs présents avec le même f̂(V), sans gradient ; moment cosinus
  0,996 → 0,9995 sur les pas prévus [Grill et al., 2020].
- **Perte** : L_JEPA (MSE latente sur les jetons masqués) + λ_var L_var + λ_cov L_cov + λ_market L_market, où L_var
  (charnière std ≥ 1) et L_cov (hors-diagonale, normalisée par d(d−1)) portent sur z_odd et z_even de la vue
  d'extraction (contexte, `mask=none`, x et −x) à travers les jours du lot [Bardes et al., 2022] ; lot de moins de
  2 jours : erreur explicite.
- **Extraction** : encodeur de contexte figé, `mask=none` ; z_odd = [f̂(P), ½(g(x) − g(−x))] (d + 1 colonnes),
  z_even = ½(g(x) + g(−x)) (d colonnes) ; `channels = {"market": [0], "residual": [1..d]}`.
- **Constantes fixées avant tout entraînement** (`configs/ca_tjepa.yaml`, hachées dans le checkpoint) : λ_var = 1,
  λ_cov = 0,04, λ_market = 0, λ_f = 1e-3 ; AdamW lr 1e-3, weight decay 0,01 ; lots de 64 jours ; au plus 200 époques ;
  validation interne à partir du 2014-01-01, embargo de 65 jours, patience 10 ; d ∈ {2, 4, 8, 16} ; ρ ~ U[0,3 ; 0,5].

### Masques (U5, état figé dans le checkpoint)
- Dictionnaire : code = Σ_k 2^k · 1{C_{i,t,k} > m_k} ∈ {0, …, 15} pour les quatre caractéristiques causales ; égalité
  C = m_k → bit 0 ; une caractéristique NaN avant imputation → `nochar` (code 16) ; actif absent (rendement NaN) → hors
  de tout groupe, ni visible ni masqué. L'affectation n'utilise que C_t, connu avant x_t.
- Sélection par jour (n = |P| présents ; jour ignoré et compté si n < 4) : lo = ⌈0,3 n⌉, hi = ⌊0,5 n⌋,
  cible = min(hi, max(lo, ⌈ρ n⌉)) avec ρ tiré une fois par lot ; groupes non vides parcourus dans un ordre aléatoire ;
  un groupe entier est ajouté si masqués + taille ≤ hi (un groupe plus grand est sauté) ; arrêt dès que masqués ≥ cible ;
  si masqués < lo après le parcours, complément uniforme parmi les présents non masqués jusqu'à lo (jour compté
  « partiel »). Groupes vides : absents de la liste, aucun tirage consommé pour eux.
- `random` (diagnostic) : ⌈ρ n⌉ borné à [lo, hi] actifs uniformes ; `none` : extraction ; `sector_pit` : refusé
  (`C-D3-gics-static`).
- Clés `SeedSequence([14, seed, usage])` : 0 initialisation des poids, 1 ordre des lots, 2 masques et ρ d'entraînement,
  3 masques d'évaluation, 4 données synthétiques ; chaque générateur local (`torch.Generator` ou
  `numpy.random.Generator`) est consommé dans un ordre fixe ; aucun RNG global.

### Contrôle de prétexte et baseline constante (obligatoires)
Panneau à un facteur gaussien i.i.d. (`sim.gaussian_latent` pour f et ε), C = rangs i.i.d. indépendants des rendements :
aucun couplage résiduel. Prédicteur constant = moyenne des cibles des jetons masqués d'entraînement (constante optimale
en MSE) ; L_model et L_const sur les mêmes jours et masques de validation, avec les poids retenus. Lecture
conservatrice : un couplage résiduel n'est lisible que si le gain 1 − L_model/L_const du panneau réel excède celui du
contrôle (la cible EMA voit aussi les visibles).

## P1 — environnement
1. Pré-contrôle : worktree, `.venv/bin/python` 3.12.9, numpy 2.4.4 / scipy 1.17.1 / pandas 3.0.6 depuis `.venv`, aucun
   `sitecustomize`, empreinte des fichiers de `.venv` et `pip list --path`, lien `make`.
2. Copie durable (`external/torch-cf-stage/`) de `solveB.json`, des 65 archives et du cache repodata ; SHA-256 des
   copies = sources. Source manquante : STOP (U12).
3. Dry-run hors ligne (`CONDA_PKGS_DIRS=<stage>`, `--offline --override-channels -c conda-forge`, mêmes spécifications
   que le solve B) : les 65 (nom, version, build, canal) doivent égaler `solveB.json`.
4. `conda-torch.lock` depuis `solveB.json` : en-tête `# platform: linux-64`, `@EXPLICIT`, 65 lignes `url#sha256`.
5. Vérification indépendante avant toute création : structure (65 lignes, conda-forge seul, 64 hex, builds épinglés),
   `sha256sum -c` des archives de la copie, égalité lock = `solveB.json` = dry-run.
6. `conda create --offline --copy -p .venv/torch-cf --file conda-torch.lock` (explicite, sans solveur ni réseau) ;
   ensuite `conda list --explicit --sha256` = lock et empreinte des fichiers préexistants de `.venv` inchangée ; écart :
   `rm -rf .venv/torch-cf`, STOP.
7. Shim hors dépôt (`external/torch-cf-shim/sitecustomize.py` : `sys.path.append(<site-packages de torch-cf>)`) ;
   provenance torch / numpy / scipy / pandas dans les deux ordres d'import.
8. Sous le shim (`PATH=.venv/bin:$PATH`) : `make check` vert ; `pytest -rs tests/test_contracts.py -k torch` = 4 passed,
   0 skipped ; J1 selon U9.
9. `.pth` seulement après 8 et si aucun autre stream n'utilise `.venv` (constat unique, sans sondage répété) ; sinon
   en attente. Après pose : 7–8 répétés sans shim ; écart : retrait, STOP.

## 2A — modèle synthétique (nouveaux fichiers seulement)
Ordre : `configs/ca_tjepa.yaml` → `tests/test_ca_tjepa.py` (RED) → `jepadrift/jepa/ca_tjepa.py` →
`jepadrift/jepa/representation.py` → `experiments/jepa_pretrain.py` (`--data {synthetic,control}`, `CHECKPOINT_PATH=`)
→ `docs/sections/ca_tjepa.md`, `docs/audits/ca_tjepa_leakage.md` (anglais) → `prompts/wrapups/wrapup-14.md`.
Familles : no-leak (masques `group` et `random`), témoin de normalisation avant masque, parité, équivariance, gel et
témoin EMA, frontières, bascule de signe, anti-effondrement, déterminisme et RNG global, baseline constante, groupes
vides et surdimensionnés, paramètres ≤ 1 M.
**G2** : tests verts ; smoke synthétique (N = 239, 200 jours, 2 époques) < 10 min et identique au bit près sur deux
exécutions ; `make check` ≤ 300 s avec gardes torch vivantes ; J1 conforme (U9). Puis wrapup et commit local C1
(chemins explicites, sans trailer).

## Hors GO-A
2B (bloqué par l'arrêt D3 P4-D du stream 17 et la finalisation de ses fichiers partagés) : lecture filtrée à la
source de `d3_239`, chemin NaN via `missing`, smokes protocolaires, `extract.py`, `test_contracts.py` (réconciliation
`CALIB_FREE` de la l.321, gardes réelles), `interface_Z.md`, `contracts.md`, `DEVIATIONS.md`, `CLAUDE.md`, `.gitignore`.
Push : GO séparé. Question ouverte pour GO-B : U14.
