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

## Décision GO-B intégrée
GO-B : `prompts/GO-stream-14-B.md` (SHA-256 `20d1c15ab074e96b4b1402e53b94c40f40550b507f04fef6d4ce471f450ab2ad`) sur le plan
revu, révision 5 (SHA-256 `9895b584a86794847d0cd09680c7eca1599e10863ce1b577d7bcc2ee261e26da`). Autorisés : nettoyage C2,
fusion locale du commit `6ed8f8a` du stream 17, chemin pretrain réel `d3_239`, enregistrement de `ca_tjepa`, contrôles
d'ingénierie, documentation et commit local C3. Exclus : push, fetch, streams 16/22, toute revendication scientifique J4.
Q1 accepté : l'extraction CLI figée de `ca_tjepa` peut transformer toutes les lignes `C-repr-rows`, monitor compris,
vers un répertoire temporaire, pour des contrôles de forme et de hash seulement ; ni ajustement, ni sélection, ni
résumé de performance, ni inférence de dérive sur ces lignes. Le script de pré-entraînement n'ouvre jamais monitor.
P4-D et toute FPR bootstrap P5-D restent hors des comparaisons calibrées J4 ; défauts hérités `c_beta_252` et rangs
fantômes documentés sans modifier D3 ; les smokes réels établissent la seule faisabilité d'ingénierie. MCP `graphify`
et `jcodemunch` reconnectés et appelés (graph_stats ; resolve_repo) avant toute modification de code.

Corrections intégrées :
1. `tests/test_contracts.py::_det_env()` conserve le `PYTHONPATH` hérité (shim torch) en plus du chemin du dépôt ;
   preuve : le test de déterminisme en sous-processus des représentations à caractéristiques passe sous `.venv` + shim ;
   aucun `.pth` pour contourner ce test.
2. Lecteur pretrain filtré : en-tête de `ret_wide.npy` validé (float64, 2-D, ordre C, nombre exact d'éléments du
   préfixe lus) ; le témoin monitor tronqué passe tant que le préfixe pretrain est complet. Pour chaque row group
   Parquet sélectionné : bornes de date fiables exigées, rejet de tout row group qui chevauche `monitor`, aucun row
   group monitor ouvert. Le row group 0 réel contient des lignes `calib` : règle précise — seules les lignes pretrain
   atteignent l'entraînement, l'estimation de l'état figé, la validation, les hachages et la sélection du checkpoint.
   Témoin : perturber les lignes `calib` de ce row group lu laisse inchangés les tableaux pretrain filtrés et le
   checkpoint.
3. `CATJEPA` rejette explicitement les jours d'extraction à zéro ou un actif observé (tests pour les deux cas) ; NaN
   reste un rendement absent ; ±inf est rejeté (Z-1).

Séquence GO-B (révision 5 corrigée) : C2 (docstrings de module et de classe retirées ; contrôle AST, pyflakes, tests,
hash du smoke synthétique `058a5d04…` inchangé, `make check`) → M (`git merge --no-ff 6ed8f8a`, worktree 17 propre et
SHA vérifié ; retour à `PRE` en cas d'échec) → lecteur pretrain filtré et `--data d3_239` (estimation interne < 2014
moins 65 jours ; s_i, PC1 b et médianes figés sur ces seules lignes) → fichiers partagés (`extract.py`,
`test_contracts.py`, `interface_Z.md`, `contracts.md`, `DEVIATIONS.md`, `CLAUDE.md`, `.gitignore`) → portes (tests
ciblés, D2/PCA à l'octet, deux extractions identiques, quatre smokes réels, `make check` ≤ 300 s, J1 CRLF/SHA-256) →
wrapup → C3 local. `.pth` différé tant qu'un autre stream utilise `.venv`.

Arrêt GO-B (2026-10-29) : `data/derived/d3_239/ret_wide.npy` est en ordre Fortran (npy 1.0, float64, (6738, 239),
SHA-256 `a266fbab…`), contrairement à la révision 5 ; la validation d'en-tête en ordre C exigée par la correction 2
le rejette. Trace : `external/torch-cf-logs/goB_stop.txt`.

## Décision GO-B2 intégrée
GO-B2 : `prompts/GO-stream-14-B2.md` (SHA-256 `9cc5c4749df42346a3f27df426c30d4f2045f62884fa96c70e514d6df9f25590`, après
GO-C4 ; `bd84e2107c4992eb0ee5b7fc7fefe105e77af97dadef5c39b2471909eeb7f26e` avant le remplacement du chemin) sur le plan revu,
révision 6, archivé à l'octet dans `prompts/plans/plan-14-B2-revision6.md` (SHA-256
`bf04f2fdb9af477720b363cced06f9f334409c9bf2d9567b6e3a7f52d256b459`). Il prolonge GO-B
après l'arrêt « ordre Fortran » ; C2 `7fbd43f`, la fusion `93370e4`, les six fichiers GO-B non commités, GO-A, GO-B, le
stream 17 et le checkout principal sont préservés. Ni autre stream, ni fetch, ni push, ni résultat J4 calibré.
- Option A : `ret` et `in_universe` lus dans le même row group filtré de `panel.parquet`, C dans `chars.parquet`
  filtré ; `ret_wide.npy` n'est jamais ouvert par le lecteur pretrain ; lecteur en ordre C et tests obsolètes retirés ;
  fixture `.npy` empoisonnée conservée.
- Portes de données avant tout entraînement : couverture date × actif exacte et unique, ni clé manquante ni clé en
  trop, aucun infini, rendements observés présents, bornes de date Parquet fiables, aucun row group monitor ouvert.
  Grille réelle 2 769 dates × 239 actifs = 661 791 clés ; SHA-256 en ordre C des rendements pretrain
  `3115d872421e2df0dc6d58d9093e4a8703b5b314cfcb4c9f1333f54e086c4830` ; 8 NaN, tous dans `c_beta_252`, aucun infini dans
  C. Ni réécriture des sources D3, ni réglage du modèle pour franchir ces portes.
- Ordre des actifs (correction obligatoire) : un entraînement sur données D3 réelles échoue sans identifiants
  d'actifs ordonnés ; le checkpoint ne stocke que leur condensat SHA-256 canonique. La CLI `ca_tjepa` rejette un
  checkpoint sans condensat et une permutation de même effectif. Un checkpoint synthétique de contrat ne reste non lié
  que s'il est utilisé sans identifiants ; passer les identifiants d'un jeu de données à un checkpoint non lié échoue.
  `CATJEPA` vérifie les identifiants liés avant `fit` et toute extraction. Chemins acceptés et rejetés testés ; la
  limite Z-1 des tableaux directs est documentée sans affaiblir la porte.
- Invariants `CALIB_FREE` et état figé conservés ; tests no-leak réels `group` et `random`, garde temporelle
  multi-jours sur les deux têtes avec témoin fautif, contrôles du registre et des options CLI, porte d'extraction
  déterministe complète. Tout témoin, porte de données, test, comparaison D2/PCA ou porte J1 en échec est un STOP avec
  preuves, jamais un motif d'ajustement.
- Exécution : `Edit` natif pour toute modification (ni redirection shell, ni `cat`, ni script Python) ; MCP graphify
  et jcodemunch reconnectés et appelés (graph_stats ; resolve_repo) avant implémentation ; `.venv` + shim torch,
  `MPLBACKEND=Agg` ; RED → GREEN ; portes GO-B ; documentation ; wrapup ; C3 local sans trailer. `.pth` différé.

## Décision GO-C4 intégrée
GO-C4 : `prompts/GO-stream-14-C4.md` (SHA-256 `c9756d933c3b623c2cd3e29155634a5b1f0dbda8d77eea3a7106b6264a4fd5aa`),
continuation bornée après C3 `30fc19b` : une correction de contrat et un archivage, sans smoke réel, sans réglage du
modèle, sans fetch ni push, sans toucher au stream 17 ni au checkout principal.
- Contrat : `ca_tjepa.train` refuse, avant tout calcul et toute écriture de checkpoint, une source de données déclarée
  non synthétique (`data["source"]` présent et ne commençant pas par `synthetic:`) sans identifiants d'actifs
  ordonnés ; les appels synthétiques (`data=None` ou `source="synthetic:..."`) restent valides. Test RED puis GREEN ;
  aucun checkpoint n'est écrit. Limite : des tableaux transmis sans provenance véridique ne peuvent pas être reconnus
  automatiquement comme des données réelles ; l'API Z-1 n'est pas élargie.
- Archivage : plan revu de la révision 6 copié à l'octet dans `prompts/plans/plan-14-B2-revision6.md` (SHA-256
  `bf04f2fd…`) ; dans `prompts/GO-stream-14-B2.md`, seul le chemin local absolu du plan est remplacé par ce chemin
  relatif ; `prompts/GO-stream-14-B.md` reste verbatim avec son chemin local (défaut historique de provenance à
  signaler avant tout push).
- Vérification : MCP graphify et jcodemunch appelés avant toute modification ; tests ciblés, `git diff --check`, hook
  `make check` ; un commit local C4 à chemins explicites, sans trailer.

## Décision GO-J1 intégrée
GO-J1 : `prompts/GO-stream-14-J1.md` (SHA-256 `7ea96abbc92bb26ae1c974521f118ebf1c14d971fdf1dfc8122bc453bcd8b0dc`), après
C4 `7204730`. Avant toute fusion, `results/e2/e2_cells.csv` doit être suivi en CRLF natif avec le SHA-256
`e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; jusqu'ici le fichier et le blob de HEAD du stream 14
sont en LF (`206dbe3b…`), et `core.autocrlf=input` (configuration globale de l'utilisateur) normalise un CRLF à
l'indexation.
- Seul ajout de configuration : `.gitattributes` racine avec la règle de chemin exact `results/e2/e2_cells.csv -text`,
  qui supprime toute conversion de fin de ligne pour ce seul fichier.
- Régénération par `make j1` (cible déterministe existante) sous `.venv` ; inspection de tous les fichiers modifiés ;
  arrêt si une sortie inattendue reste inexpliquée.
- Vérifications : assertions Python du chercheur (SHA-256, présence de CRLF, aucun LF isolé) ; `git ls-files --eol`
  = `i/crlf w/crlf attr/-text` ; SHA-256 du blob indexé = `e315e537…` (arrêt et diagnostic si Git normalise) ;
  `make prompts-check`, `git diff --check`, `make check` sous `.venv` + shim, quatre gardes torch exécutées sans skip.
- Inchangés : code du modèle, paramètres, seuils, autres streams, `main`, fichiers GO historiques. Un seul commit local,
  sans trailer ni contournement de hook ; ni fetch, ni push, ni fusion.
