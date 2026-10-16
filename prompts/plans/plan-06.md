# Plan — Stream 06 : représentations linéaires et interface Z (ACP orthogonale, coupe de degré 0, rangs)

> Exécution : Claude Code (routage INDEX : Opus, xhigh), en session unique, sans sous-agent (précédents des streams 04 et 05). Méthode : `superpowers:executing-plans` en mode natif, `superpowers:test-driven-development` pour chaque tâche, `superpowers:verification-before-completion` avant toute annonce de fin. Cases `- [ ]` pour le suivi.

Date : 2026-10-16. Spécification : `prompts/streams/prompt-06-representations-z.md`. Base : HEAD `be5b87c` (correctif du stream 05, après `cbd0692`). Arbre propre ; seuls des `__pycache__/` et `prompts/GO-stream-06.md` sont non suivis.

Statut : **GO**. La revue `prompts/GO-stream-06.md` (2026-10-16) est intégrée dans ce plan final, section « Décision GO intégrée ».
- **Étape préalable** (règle AGENTS.md, `C-plan-recording` ; instruction du GO) : enregistrer ce plan dans `prompts/plans/plan-06.md` avant toute ligne de code.
- (GO Hn) marque l'hypothèse n du plan initial, confirmée par la revue.

**Objectif.** Fixer le contrat de toute représentation : apprentissage sur la seule calibration, transformation jour par jour, état figé et haché. Livrer trois références linéaires (ACP orthogonale, coupe de degré 0, rangs centrés), la CLI d'extraction et les extractions de référence de D2 et `d3_239`.

**Architecture.**
- `jepadrift/representations/base.py` : classe `Representation`. Elle porte la validation, le hachage, le sidecar et la boucle panel ; les sous-classes écrivent `_fit` et `_day`.
- `pca.py` : règle de Marčenko–Pastur, décomposition partagée, `PCAOrthogonal`.
- `cross_section.py` : `DegreeZero` et `CenteredRanks`.
- `extract.py` : `REGISTRY`, `extract`, CLI.
- `jepadrift/stats/covariance.py` reçoit `eigh_desc`, partagé avec `injection.fit_background`.
- Dépendances : numpy seul, plus les chargeurs de données dans `extract.py`.

## Décision GO intégrée

Source : `prompts/GO-stream-06.md` (verdict : **GO**). Les dix valeurs par défaut sont confirmées ; le contenu du plan ne change pas. Intégration :

| Point de la revue | Intégration dans ce plan |
|---|---|
| Instruction préalable : enregistrer `prompts/plans/plan-06.md` avant toute ligne de code | Statut et Tâche 0 |
| Revérifications de la revue : K = 5 (D2, λ₊ = 1.7452) et K = 10 (`d3_239`, λ₊ = 2.2619) ; δ̂ = 0.0192 et 0.0252 ; décomposition de Σ̂_LW identique au bit près à `fit_background` sur les deux jeux | Constats 2, 3 et 5 inchangés |
| H1 (σ² = 1 sur la corrélation, K = n₊ − 1) : c'est la formule du prompt. La variante de Laloux reste documentée dans `C-repr-mp-K` | (GO H1) ; Tâche 7 |
| H2 (Ledoit–Wolf par défaut, alignement exact avec l'information de l'injecteur) | (GO H2) ; écart `C-repr-whiten-lw` |
| H3 (z = x @ W sans centrage, colonne 0 = marché dans les trois modes) | (GO H3) ; écart `C-repr-layout` |
| H4 (règle tail10 sur les valeurs propres de la Σ̂ utilisée ; m = 0 → `ValueError`) | (GO H4) |
| H5 (têtes paires : carrés pour l'ACP et les rangs, [‖Px‖] pour DegreeZero) | (GO H5) ; écart `C-repr-even-heads` |
| H6 (DegreeZero : b unitaire, U de la même décomposition, zéros si ‖p‖ = 0, aucun canal marché déclaré) | (GO H6) |
| H7 (fit sur calib, transformation du premier jour de pretrain à la fin, non fini → `ValueError`). Le « T × D » du prompt est la forme nominale | (GO H7) ; écart `C-repr-rows` |
| H8 (extractions de référence : `pca`, mode factor, LW, sur `d2_us97` et `d3_239` ; la grille complète reste hors du dépôt) | (GO H8) ; Tâche 6 |
| H9 (`eigh_desc` partagé, appelé par `injection.fit_background`) : indispensable pour que le canal marché soit exactement la direction de F3 | (GO H9) ; Tâche 1 |
| H10 (chargeur de C_t reporté au stream 17 ou 14) | (GO H10) |
| Points de vigilance 1 à 5 et risques : endossés | Inchangés |
| Trace de décision | `prompts/GO-stream-06.md` commité avec le stream (Tâche 8) |

## Contexte

Les streams aval fixent le contrat de l'interface :
- **stream 07** (P3-C, P3-D, P3-CS, P7) :
  - P3-C : flux de signe par direction, avec un canal marché et des directions résiduelles ;
  - P3-D : q_t = (‖z_res‖² − D)/√(2D) ;
  - P3-CS : pivot s_t = uᵀPx_t/‖Px_t‖ et mise λ_t = min(0.5, c/σ̂_{t|t−1}), σ̂ étant une moyenne exponentielle de ‖Px_{t−1}‖.

  Les représentations entrent dans `monitors` sous forme de tableaux Z ou X, jamais comme objets importés.
- **stream 08** : contrats paramétrés sur « toutes les représentations du registre » :
  - (1) non-anticipation bit à bit ;
  - (2) imparité ≤ 1e-6 ;
  - (3) SHA-256 identiques de `z_*.npz` sur deux exécutions ;
  - (4) `fit` ne voit que `pretrain` ou `calib`, et perturber `monitor` laisse `state_hash` inchangé. Les statistiques de normalisation du JSON doivent provenir du seul segment déclaré.
- **streams 14, 17, 18** (JEPA, IPCA, CD-DFM) : ils s'enregistrent dans le registre et écrivent `z_<hash>.npz` et leur JSON « selon `docs/sections/interface_Z.md` ». Le stream 17 lance `python -m jepadrift.representations.extract --dataset d3_239 --rep ipca`.
- **stream 11** (audit) : spectre, bord de MP et K sur la calibration.
- **stream 19** (P3-KF) : composantes « tail10 ».
- **streams 12 et 19** (E1, E4) : ils transforment dans le processus des fonds D6 injectés, et ajustent la représentation sur des sous-ensembles d'actifs.

## Constats des sondes (lecture seule, sans écriture de fichier ; lignes ≤ 2019-12-31 pour toute statistique)

1. **Lignes et NaN.**
   - `d2_us97` (5154 × 97) : pretrain sur les lignes 0–2767, calib sur 2833–3773 (941 jours), monitor à partir de la ligne 3839. Aucun NaN.
   - `d3_239` (6738 × 239) : pretrain sur 1256–4024, calib sur 4090–5030 (941 jours). Seule la ligne 0 (2000-01-03, premier rendement non défini) contient des NaN, soit 239 valeurs. Les lignes postérieures à la calib n'en contiennent aucun : c'est un simple comptage, confirmé par `results/data/d3_profile.csv`, où `assets_min` vaut 239 sur le segment monitor.
2. **Marčenko–Pastur sur la corrélation empirique de la calib.**
   - `d2_us97` : N/T = 0.1031 et λ₊ = 1.7452 avec σ² = 1. Six valeurs propres dépassent le bord, PC1 compris, d'où K = 5.
   - `d3_239` : N/T = 0.254 et λ₊ = 2.2619. Onze valeurs propres le dépassent, d'où K = 10. Cela redonne les « K = 11 (marché plus dix facteurs) » du prompt 18.
   - Variante σ² = 1 − λ₁/N [Laloux et al., 2000] : λ₊ = 1.1752 et 10 valeurs au-dessus, soit K = 9, sur D2 ; λ₊ = 1.6256 et 16 valeurs au-dessus, soit K = 15, sur `d3_239`.
3. **Ledoit–Wolf sur la calib.**
   - Coefficient δ̂ : 0.0192 sur D2, 0.0252 sur `d3_239`.
   - Part de PC1 : 33.1 % sur D2, 25.9 % sur `d3_239`.
   - Valeur propre minimale : 1.4e-5 avec LW contre 1.0e-5 en empirique sur D2 ; 1.2e-5 contre 5.8e-6 sur `d3_239`.
4. **tail10**, plus grand ensemble de dernières composantes dont la variance cumulée reste ≤ 10 % de la trace :
   - D2 : m = 46 avec LW (part 0.0996, 0.1033 avec la suivante), m = 48 en empirique ;
   - `d3_239` : m = 123 avec LW (part 0.0992, puis 0.1008), m = 130 en empirique.
5. **Identités sur la calib de `d3_239`.**
   - `eigh` de Σ̂_LW, trié par ordre décroissant puis signé, est identique au bit près à `injection.fit_background(...)["eigvec"/"eigval"]`.
   - En mode full avec LW, ½‖z(δ)‖² vaut I_target à 1.7e-16 près en relatif pour une dérive F1 issue de `inject` (I = 0.01). Le blanchiment reproduit donc exactement l'information de l'injecteur.
   - Une dérive F3 tombe entièrement dans le canal marché : z₀ = 0.1414, et les autres coordonnées sont ≤ 3e-16.
6. **Imparité et degré 0.**
   - Écart d'imparité ‖φ(−x) + φ(x)‖_∞ : 4.4e-16 pour l'ACP (le produit matrice-vecteur BLAS n'est pas symétrique au bit près), 0 pour DegreeZero et 0 pour les rangs.
   - Écart de degré 0 à c = 3.7 : 7e-17 pour DegreeZero et 0 pour les rangs.
   - Le produit panel X @ W n'est pas égal au bit près à l'empilement des x @ W : la boucle jour par jour s'impose.
7. **Rangs.**
   - La formule numpy `r = (cumsum(c) − (c − 1)/2)[inv]`, avec `np.unique(x, return_inverse=True, return_counts=True)`, est identique à `scipy.stats.rankdata` (rangs moyens).
   - Exemple : [0.3, −0.1, 0.3, 0.0] donne [0.25, −0.375, 0.25, −0.125].
   - Sur `d3_239`, de pretrain à calib : 7556 rendements exactement nuls, un seul ex aequo non nul, aucun jour entièrement nul.
8. **Règle MP sur données simulées.**
   - Panel spiké 1000 × 60 à 4 facteurs (échelles 3 ; 1.5 ; 1.2 ; 1) : n₊ = 4 sur 10 graines.
   - Panel i.i.d. gaussien 941 × 97 : n₊ ∈ {0, 1} sur 20 graines, donc K = n₊ − 1 ≤ 0.
9. **Coût de la boucle jour par jour** (3775 à 5482 lignes) :
   - ACP full 239 × 239 : 0.04 s ;
   - DegreeZero : 0.04 s ;
   - rangs : 0.15 s.
10. **Déterminisme de `np.savez`** (numpy 2.4.4, source inspectée) : chaque entrée est écrite par `ZipFile.open(name, "w")`, donc datée du 1980-01-01. Mêmes tableaux, mêmes octets.

## Décisions

| Question | Décision | Raison |
|---|---|---|
| Classe de base | `Representation`, attribut de classe `odd_head = True`. `fit(X_fit, C_fit, dates_fit)` : valide, enregistre `n_assets` et l'empreinte d'apprentissage, appelle `_fit`, renvoie `self`. `transform_day(x_t, C_t=None)` : valide x_t, appelle `_day` et renvoie `{"z_odd": (D,), "z_even": (D',)}`. `transform_panel(X, C=None)` empile `transform_day` ligne par ligne. Restent `state_hash()` et `sidecar()`. Les sous-classes n'écrivent que `_fit` et `_day` | Validation et hachage en un seul endroit. La boucle exclut toute opération temporelle et rend le panel égal, au bit près, aux jours (sonde 6) |
| Contrat d'entrée | `np.ndarray` float64 et fini, sinon `TypeError` (objet non ndarray) ou `ValueError`. `fit` : 2-D avec au moins 2 lignes et 2 colonnes, `dates_fit` de même longueur. `transform_day` : 1-D de longueur `n_assets`. C est accepté mais lu par aucune des trois représentations | Politique d'`inject` (`C-interface-f64`). Validation par exception, jamais par `assert` |
| `state_hash` | SHA-256 d'un en-tête JSON canonique `{class, config, n_assets}`, puis, pour chaque tableau d'état pris par nom trié : nom, dtype, forme, octets. État minimal : PCA `{W}`, DegreeZero `{b, U}`, rangs `{}` | « SHA-256 des tableaux d'état ». L'en-tête empêche deux transformations distinctes de partager un même nom de fichier |
| `sidecar()` | Dict sérialisable en JSON avec les clés suivantes :<br>• `interface` (`"Z-1"`), `representation`, `config`, `state_sha256`, `n_assets`, `odd_head` ;<br>• `heads` : pour `z_odd` et `z_even`, `dim`, `parity`, `degree` et `definition` ;<br>• `channels` : nom → colonnes ;<br>• `fit` : `first_day`, `last_day`, `days`, `x_sha256`, `c_sha256` ;<br>• `normalization` : statistiques figées.<br>`extract` y ajoute `dataset`, `fit_segment`, `rows`, `dates`, `x_sha256` du panel transformé et `z_sha256` | Champs du prompt (empreintes, dates, drapeaux impair/pair, statistiques figées). Le contrat (4) du stream 08 exige un segment déclaré et des statistiques recalculables |
| (GO H9) Décomposition partagée | `stats/covariance.py::eigh_desc(sigma)` : valeurs propres décroissantes, chaque vecteur signé à somme ≥ 0. `injection.fit_background` l'appelle ; les opérations sont les mêmes, donc les sorties sont identiques au bit | Le canal marché de P3-C doit être exactement la direction de F3 (b₁ = v₁√λ₁). `representations` ne peut pas importer `injection` (sonde 5 ; revérifié au GO sur les deux jeux) |
| (GO H2) Covariance de l'ACP | `shrinkage="ledoit_wolf"` par défaut : Σ̂ = `ledoit_wolf(X_calib)`. `None` : S = X_cᵀX_c/n (convention de `ledoit_wolf`) | Avec LW, ½‖z_full(δ)‖² = ½δᵀΣ̂⁻¹δ, l'information de l'injecteur (sonde 5). La variance des coordonnées sur la calib vaut λ_S/λ_LW, entre 0.49 et 1.03 sur `d3_239`. Avec `None`, elle vaut 1 exactement |
| (GO H1) K de Marčenko–Pastur | λ₊ = (1 + √(N/T))², avec σ² = 1 (trace/N d'une corrélation), sur la corrélation empirique de la calib. n₊ = #{λ > λ₊}, PC1 compris, et K = n₊ − 1. K ≤ 0 → `ValueError`. Un K entier doit vérifier 1 ≤ K ≤ N − 1 | Le glossaire dit « PC2..PC(K+1), K au bord MP » : le résiduel factoriel est l'ensemble des directions hors marché au-dessus du bord. Sur `d3_239`, cela donne D = 11, soit « marché plus dix facteurs » au prompt 18 (sonde 2) |
| (GO H3) Colonnes de l'ACP | z = x @ W, avec W = V_sel Λ_sel^{−1/2}, sans centrage. La colonne 0 est le canal marché v₁ᵀx/√λ₁ dans les trois modes. Modes :<br>• `factor` : PC2..PC(K+1) ;<br>• `full` : PC2..PCN ;<br>• `tail10` : les m dernières composantes.<br>`channels = {"market": [0], "residual": [1, …, D − 1]}` | « PC1 is never discarded silently » ; une seule disposition pour tous les consommateurs. Un centrage rendrait la transformation affine, donc non impaire |
| (GO H4) tail10 | m = max{m : somme des m plus petites valeurs propres ≤ 0.10·tr Σ̂}, sur les valeurs propres de la Σ̂ utilisée (LW par défaut). m = 0 → `ValueError` | Lecture de « composantes des derniers 10 % de variance » [Kuncheva & Faithfull, 2014]. m = 46 sur D2 et 123 sur `d3_239` (sonde 4) |
| (GO H5) Têtes paires | ACP et rangs : z_even = z_odd², avec D' = D. DegreeZero : z_even = [‖Px‖], avec D' = 1 ; cette tête est homogène de degré 1 | Pour l'ACP, c'est le texte du prompt. P3-CS (b) lit σ̂ = moyenne exponentielle de ‖Px_{t−1}‖ ; Z suffit alors à P3-CS. En mode full, Σ z_k² = 1 : les carrés de DegreeZero seraient dégénérés |
| (GO H6) DegreeZero | `DegreeZero(b="pc1"\|"ones", K="mp"\|int, mode="factor"\|"full")` :<br>• b unitaire : v₁ de Σ̂_LW, ou 1/√N ;<br>• U : vecteurs propres résiduels de la même décomposition (PC2..PC(K+1) en factor, PC2..PCN en full) ;<br>• p = x − b(bᵀx), z_odd = Uᵀp/‖p‖, et z_odd = 0 si ‖p‖ = 0 ;<br>• aucun canal marché : la direction b est retirée, ce que déclare `channels`/`normalization` | P3-CS observe les mêmes directions que P3-C : la comparaison isole la normalisation (Λ figée contre ‖Px_t‖ du jour). \|z_k\| ≤ 1, ce qui donne le pivot borné du pari |
| `CenteredRanks` | z_i = (r_i − (N+1)/2)/N, rangs moyens des ex aequo calculés par la formule numpy de la sonde 7 ; −0.0 et 0.0 sont confondus. État vide | numpy seul, identique à `rankdata`. Imparité et degré 0 exacts au bit |
| (GO H7) Lignes extraites | `fit` sur les lignes de calib, repérées par les dates de `splits.yaml`. Transformation des lignes allant du premier jour de pretrain à la fin du panel. Une valeur non finie → `ValueError` | Sur `d3_239`, la ligne 0 contient des NaN et les années 2000–2004 n'appartiennent à aucun segment. Sur D2, toutes les lignes sont transformées. Le « T × D » du prompt est la forme nominale : écart `C-repr-rows` |
| Fichiers | `data/derived/<dataset>/z_<state_hash>.npz`, écrit par `np.savez` (Z_odd, Z_even, dates en datetime64[D]), et `z_<state_hash>.json`, écrit par `json.dumps(indent=2, sort_keys=True) + "\n"` | Octets déterministes (sonde 10). Même écriture que `write_tau_star` |
| Registre | `extract.REGISTRY = {"pca": PCAOrthogonal, "degree0": DegreeZero, "ranks": CenteredRanks}`. Options de la CLI :<br>• `--dataset {d2_us97, d3_239}`, `--rep` ;<br>• `--mode`, `--K` (`mp` ou entier), `--shrinkage {ledoit_wolf, none}`, `--b` ;<br>• `--out`, par défaut `data/derived/<dataset>`.<br>Une option n'est transmise au constructeur que si elle est fournie | C'est le registre des prompts 8, 14 et 17. `d3_500` est exclu : 13 % de NaN, sous-panel à choisir par l'appelant |
| (GO H8) Extractions de référence | `pca`, mode factor, LW, sur `d2_us97` (D = 6) et sur `d3_239` (D = 11), soit environ 0.5 et 1 Mo | C'est la commande de vérification du prompt. Les autres configurations se reproduisent par la CLI ; la grille complète pèserait environ 80 Mo et reste hors du dépôt |
| (GO H10) Chargeur de C_t | Reporté : aucune des trois représentations ne lit C, et `extract` passe `C=None` | GO-05 confie le chargeur au premier consommateur réel, qui sera le stream 17 (IPCA) ou le stream 14 |
| Journal | Les deux extractions de référence sont journalisées par `tee` dans `logs/representations/extract.log` | Règle « logs in logs/<stream>/ » |
| Commit | Unique : `feat(representations): add Z interface, PCA-orthogonal, degree-0 and rank representations` | Convention des streams 03 à 05 |
| Langue | Anglais : code, docstrings, `docs/sections/interface_Z.md`, wrapup, commit. Français : `docs/DEVIATIONS.md` et ce plan | Règles du projet (GO-04) |

## Contraintes globales

- **Dépendances et imports.** numpy seul dans `base.py`, `pca.py` et `cross_section.py` (avec `jepadrift.stats.covariance`). `extract.py` importe en plus `jepadrift.data_loader`. Aucun import de `jepadrift.monitors`, de `jepadrift.injection` ni de torch sous `jepadrift/representations/` ; les tests peuvent importer `injection`.
- **Environnement.** Commandes avec OMP/MKL/OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE et PYTHONHASHSEED = 42. Interpréteur : `.venv/bin/python`. `make` s'exécute après `source .venv/bin/activate`. `extract.py` fixe les variables de threads avant d'importer numpy, sur le modèle de `data_loader/articleB.py`.
- **Fenêtre de surveillance avant J4.** Aucune statistique calculée sur les lignes datées du 2020-01-01 ou après. Les tests de perturbation remplacent ces lignes par des valeurs synthétiques, sans lire les valeurs réelles. Seul le test de déterminisme de la CLI touche les Z de cette fenêtre, et uniquement par une égalité d'empreintes.
- **Code nouveau.** Aucun commentaire, sauf `# ponytail:`, et des docstrings d'une ligne. Aucune marque d'IA. Aucun `# noqa`.
- **Commit.** Conventional Commits, sans trailer `Co-authored-by`. Indexation par chemins explicites, jamais `git add .` ni `-A` ; aucun `__pycache__`.

## Points de vigilance (Review Focus) — endossés au GO

1. **Fuite d'apprentissage.** `fit` ne reçoit que les lignes de calib. Remplacer les lignes postérieures au 2019-12-31 par deux tirages synthétiques différents laisse inchangés `state_hash`, `normalization` et les Z antérieurs. Modifier une ligne de calib change `state_hash` : le test n'est donc pas vide (Tâche 5).
2. **Alignement avec l'injecteur.** PC1 et Σ̂ sont ceux de `fit_background`, au bit près. Deux contrôles : F3 tombe dans la colonne 0, et ½‖z_full(δ)‖² = I_target (Tâches 1 et 3).
3. **Bit à bit.** `transform_panel` égale l'empilement de `transform_day`. Les octets du `.npz` et du `.json` sont identiques d'une exécution à l'autre (Tâches 2 et 5).
4. **Cas dégénérés à issue explicite** :
   - ‖Px‖ = 0, y compris x = 0 → zéros ;
   - K ≤ 0 → `ValueError` ;
   - m = 0 en tail10 → `ValueError` ;
   - valeur propre retenue ≤ 0 → `ValueError` ;
   - entrée non finie → `ValueError` ;
   - colonne de variance nulle dans la corrélation de calib → `ValueError`.
5. **Isolation.** Un test analyse par `ast` les imports de `jepadrift/representations/*.py` (Tâche 5). Le stream 08 ne couvre que `monitors` et `jepa`.

## Fichiers

- **Créés** :
  - `jepadrift/representations/{base,pca,cross_section,extract}.py` ;
  - `tests/test_representations.py` ;
  - `docs/sections/interface_Z.md` ;
  - `data/derived/d2_us97/z_<h>.{npz,json}` et `data/derived/d3_239/z_<h>.{npz,json}` ;
  - `logs/representations/extract.log` ;
  - `prompts/plans/plan-06.md`, `prompts/wrapups/wrapup-06.md`.
- **Déjà présent, commité avec le stream** : `prompts/GO-stream-06.md`.
- **Modifiés** :
  - `jepadrift/stats/covariance.py` : ajout de `eigh_desc` ;
  - `jepadrift/injection.py` : `fit_background` appelle `eigh_desc` (GO H9) ;
  - `docs/DEVIATIONS.md` : cinq entrées en fin de fichier.
- **Non touchés** :
  - `Makefile`, car `make check` couvre déjà les nouveaux fichiers ;
  - `requirements.*` ;
  - `jepadrift/representations/__init__.py`, qui reste vide ;
  - `jepadrift/data_loader/*` ;
  - `data/derived/MANIFEST.json`, réécrit par les builders : le JSON sidecar porte sa propre provenance.

---

### Tâche 0 — Préconditions
- [x] Intégrer `prompts/GO-stream-06.md` dans la section « Décision GO intégrée » ; (H) remplacé par (GO).
- [ ] Enregistrer ce plan dans `prompts/plans/plan-06.md`, avant toute ligne de code.
- [ ] `git log --oneline -3` et `git status --short` : HEAD attendu `be5b87c` ou un descendant. Si un autre stream a laissé des fichiers non commités :
  - ne jamais les indexer ;
  - relire `docs/DEVIATIONS.md` juste avant de l'éditer ;
  - ne lancer que des tests ciblés.
- [ ] Référence « avant » : `pytest -q tests/test_injection.py`, tout au vert.

### Tâche 1 — `eigh_desc` partagé (GO H9)

**Interface.** `jepadrift.stats.covariance.eigh_desc(sigma) -> (eigval (N,), eigvec (N, N))`.

- [ ] Créer `tests/test_representations.py` : docstring `"""Tests for jepadrift.representations (pytest)."""`, helper `_rng(*key)` = `np.random.default_rng(np.random.SeedSequence([6, *key]))`, et helper `_calib(dataset)`, qui renvoie (X, dates) sur les lignes de calib à partir des chargeurs et de `splits.yaml`.
- [ ] `test_eigh_desc_sorted_signed` :
  - les valeurs propres sont décroissantes ;
  - la somme de chaque vecteur est ≥ 0 ;
  - V diag(λ) Vᵀ = Σ à 1e-12 ;
  - sur la calib de `d3_239`, `fit_background(X, 11)["eigvec"/"eigval"]` est égal au bit près à `eigh_desc(ledoit_wolf(X)[0])`.
- [ ] Échec attendu → implémenter (`np.linalg.eigh`, inversion de l'ordre, signe) → remplacer les lignes 41–43 d'`injection.py` par `eigval, eigvec = eigh_desc(sigma)`.
- [ ] `pytest -q tests/test_injection.py tests/test_representations.py` : tout au vert, sans changement des tests du stream 05.

### Tâche 2 — `base.py` et `CenteredRanks`

**Interfaces.** `Representation` (décision « Classe de base ») ; `cross_section.CenteredRanks()`.

- [ ] Tests :
  - `test_ranks_values` : l'exemple de la sonde 7 ; sur des entiers aléatoires avec ex aequo (N = 239), égalité avec `(scipy.stats.rankdata(x) − (N+1)/2)/N` ;
  - `test_transform_panel_day_by_day` : `transform_panel(X)` est égal au bit près à l'empilement de `transform_day`. Modifier les lignes > t laisse les lignes ≤ t identiques au bit près (non-anticipation) ;
  - `test_inputs_rejected` :
    - pour `fit` : un NaN, un tableau 1-D, du float32, des `dates_fit` de mauvaise longueur ou une liste → `ValueError` ou `TypeError` ;
    - pour `transform_day` : une mauvaise longueur ou un NaN → `ValueError` ;
  - `test_state_hash_and_sidecar` :
    - deux fits identiques donnent le même hash ;
    - `json.loads(json.dumps(sidecar))` redonne le sidecar ;
    - `fit.first_day`, `fit.last_day` et `fit.days` correspondent à `dates_fit` ;
    - `x_sha256` est le SHA-256 des octets float64 de X_fit.
- [ ] Échec attendu → implémentation → succès. `transform_panel` porte `# ponytail: per-day loop (bitwise equal to transform_day), vectorize in a subclass if E1 runtime needs it`.

### Tâche 3 — `pca.py` : règle MP, décomposition, `PCAOrthogonal`

**Interfaces.**
- `mp_edge(T, N) -> float` ;
- `mp_count(X) -> (n_above, edge)` : `ValueError` si la corrélation n'est pas finie ;
- `pca_directions(X, K, mode, shrinkage) -> (eigval, eigvec, sel, stats)`, partagé avec `DegreeZero` ;
- `PCAOrthogonal(K="mp", mode="factor", shrinkage="ledoit_wolf")` : `ValueError` à la construction si le mode, le shrinkage ou K est invalide.

`normalization` contient :
- `eigval`, les valeurs propres retenues ;
- `trace`, `shrinkage` (δ̂ ou `null`), `mp_edge`, `n_above_edge` ;
- `K` en mode factor ;
- `tail_count` et `tail_share` en mode tail10.

- [ ] Tests :
  - `test_mp_rule` :
    - `mp_edge(1000, 60)` = (1 + √0.06)² ;
    - sur le panel spiké de la sonde 8, avec les graines 0 à 4 : n₊ = 4, K = 3 et D = 4 ;
    - sur un panel i.i.d. 941 × 97 dont la graine donne n₊ ≤ 1 : `PCAOrthogonal().fit` → `ValueError` ;
    - K entier hors de [1, N − 1] → `ValueError` ;
  - `test_pca_dimensions_real` (prompt : « D attendu, pas de NaN »). Fit sur la calib, transformation des lignes allant du début du pretrain au 2019-12-31. Valeurs attendues :
    - D2 : K = 5 en factor, D = 6 ;
    - `d3_239` : K = 10, D = 11 ;
    - full : D = N ;
    - tail10 : D = 1 + m, avec m = 46 sur D2 et 123 sur `d3_239` ;
    - dans tous les cas : D' = D, aucun NaN, et `channels["market"] == [0]` ;
  - `test_tail10_rule` (`d3_239`) : la somme des m valeurs propres retenues est ≤ 0.10·tr ; ajouter la suivante dépasse 0.10·tr ;
  - `test_whitening` (calib de `d3_239`) :
    - avec `shrinkage=None`, mode full : la covariance centrée (÷ n) des Z de calib vaut I à 1e-10 ;
    - avec LW, mode full : ½‖z(δ)‖² = `meta["info"]` à 1e-12 en relatif, pour δ tiré d'`injection.inject` en F1 (I = 0.01) ;
    - pour une dérive F3 : |z_k(δ)| ≤ 1e-12·|z₀(δ)| pour tout k ≥ 1 ;
  - `test_odd_head` (prompt), sur les trois modes et les deux shrinkages, pour 50 jours de calib et 50 vecteurs gaussiens : ‖z_odd(−x) + z_odd(x)‖_∞ ≤ 1e-12 et ‖z_even(−x) − z_even(x)‖_∞ ≤ 1e-12 ;
  - `test_normalization_from_declared_segment` : recalculer `eigval` et `mp_edge` depuis les lignes désignées par `fit.first_day`/`last_day` redonne les valeurs du sidecar.
- [ ] Échec attendu → implémentation → succès.

### Tâche 4 — `DegreeZero`

**Interface.** `cross_section.DegreeZero(b="pc1", K="mp", mode="factor")`. Elle utilise `pca_directions(X, K, mode, "ledoit_wolf")`, et `normalization` contient `b`, `K`, `mp_edge` et `n_above_edge`.

- [ ] Tests :
  - `test_degree_zero_invariance` (prompt) : pour DegreeZero, avec b ∈ {pc1, ones} et mode ∈ {factor, full}, et pour CenteredRanks, avec c ∈ {0.5, 3.7, 1e3} :
    - ‖z_odd(cx) − z_odd(x)‖_∞ ≤ 1e-12 ;
    - pour DegreeZero, z_even(cx) = c·z_even(x) à 1e-12 en relatif ;
  - `test_degree_zero_bounds_and_zero_day` :
    - |z_odd| ≤ 1 ;
    - en full avec b = pc1 : ‖z_odd‖ = 1 à 1e-12 ;
    - x = 0 donne z_odd = 0 et z_even = [0], sans NaN ; il en va de même pour les rangs et l'ACP ;
  - `test_odd_head` étendu à DegreeZero et à CenteredRanks ;
  - dimensions : D = K en factor (5 sur D2, 10 sur `d3_239`), N − 1 en full, D' = 1. Rangs : D = D' = N.
- [ ] Échec attendu → implémentation → succès. Le garde ‖p‖ = 0 porte `# ponytail: exact-zero guard only, add a relative threshold if a pure-market day ever appears`.

### Tâche 5 — `extract.py`, registre et CLI

**Interfaces.**
- `segment_rows(dates, segment) -> (start, stop)` ;
- `extract(rep, X, dates, splits, out_dir, dataset) -> (npz_path, sidecar)` :
  - fit sur la calib, avec `C=None` ;
  - transformation des lignes allant du premier jour de pretrain à la fin ;
  - contrôle de finitude des sorties ;
  - écriture du `.npz` et du `.json` ;
- `REGISTRY` ;
- `main(argv=None)`.

La CLI affiche le chemin, D, D' et le SHA-256 du `.npz`.

- [ ] Tests :
  - `test_monitor_perturbation_keeps_state` (prompt) :
    - X = panel D2, dont les lignes datées du 2020-01-01 ou après sont remplacées par 0.01·N(0, 1) (tirage A, puis tirage B) ;
    - pour chaque entrée de `REGISTRY` en configuration par défaut : même `state_hash`, même `normalization`, et lignes de Z antérieures au 2020-01-01 identiques au bit près ;
    - une ligne de calib multipliée par 1.5 change `state_hash` ;
  - `test_extract_deterministic` (critère de succès du prompt) : `main(["--dataset", "d2_us97", "--rep", "pca", "--mode", "factor", "--out", tmp_k])` lancé pour k = 1 et 2. Vérifications :
    - les octets du `.npz` et du `.json` sont identiques ;
    - le nom du fichier est `z_<sidecar["state_sha256"]>.npz` ;
    - les clés sont {Z_odd, Z_even, dates}, avec les dtypes float64 et datetime64[D] ;
    - `dates` égale les dates du panel à partir du premier jour de pretrain ;
    - `fit.first_day` et `fit.last_day` sont les bornes de calib de `splits.yaml`, avec `fit.days` = 941 et `fit_segment` = "calib" ;
  - `test_import_isolation` : analyse `ast` de `jepadrift/representations/*.py` ; aucun import de `jepadrift.monitors`, de `jepadrift.injection` ni de `torch`.
- [ ] Échec attendu → implémentation → succès.

### Tâche 6 — Extractions de référence (GO H8)
- [ ] `mkdir -p logs/representations`, puis `python -m jepadrift.representations.extract --dataset d2_us97 --rep pca --mode factor 2>&1 | tee logs/representations/extract.log`, et la même commande pour `d3_239`, avec `tee -a`.
- [ ] Déterminisme : relancer les deux extractions avec `--out` dans le scratchpad de session. `cmp` et `sha256sum` doivent donner des fichiers identiques aux extractions de référence.
- [ ] Consigner dans le wrapup les hashes d'état, les SHA-256 des `.npz` et les valeurs de D.

### Tâche 7 — Documentation et écarts
- [ ] Rédiger en anglais `docs/sections/interface_Z.md`, contrat versionné « Z-1 » :
  - API de `Representation` ;
  - contrat d'entrée (float64, fini, panels de rendements) ;
  - têtes impaire et paire, avec leur parité et leur degré d'homogénéité ;
  - absence d'opération temporelle ;
  - segments d'apprentissage autorisés (`pretrain`, `calib`) ;
  - définition de `state_hash` ;
  - schéma du sidecar et du `.npz`, nommage des fichiers, lignes extraites, déterminisme ;
  - registre, et procédure d'enregistrement d'une représentation (streams 14, 17 et 18) ;
  - table des trois représentations : formules, D, D', canaux ;
  - règle MP, règle tail10, blanchiment LW (variance de calibration λ_S/λ_LW) et lien exact avec l'information de l'injecteur ;
  - risque τ* dans la calib ou avant : le choix des lignes sans dérive revient aux streams 07 et 12 ;
  - références : [Marčenko & Pastur, 1967], [Ledoit & Wolf, 2004], [Kuncheva & Faithfull, 2014, PCA feature extraction for change detection in multidimensional unlabeled data], Article C (lemme de blanchiment par un encodeur impair, Remarque « Combining channels »).
- [ ] `docs/DEVIATIONS.md` : relire juste avant l'édition, puis ajouter en fin de fichier, en français, en citant les sondes de ce plan et le GO :
  - `C-repr-mp-K`, avec la variante de Laloux (K = 9 et 15) ;
  - `C-repr-whiten-lw` ;
  - `C-repr-layout` (colonne marché et tail10) ;
  - `C-repr-even-heads` ;
  - `C-repr-rows`.

### Tâche 8 — Clôture (ordre AGENTS.md)
- [ ] Vérifications :
  - `pytest -q tests/test_representations.py tests/test_injection.py` ;
  - `source .venv/bin/activate && make check`. En cas d'échec : diagnostic, 3 tentatives au plus. Un échec imputable à un autre stream entraîne gel et signalement, sans commit ;
  - `git diff data/derived/MANIFEST.json` doit être vide.
- [ ] (1) Skill `wrap-up` → `prompts/wrapups/wrapup-06.md`.
- [ ] (2) `tools/reindex_graphify_jcodemunch.sh`.
- [ ] (3) `make check`, puis commit unique sans trailer :
  - indexer explicitement les fichiers créés et modifiés de la section « Fichiers », y compris `prompts/GO-stream-06.md` ;
  - `git diff --staged` : aucun fichier d'un autre stream, aucun `__pycache__`, aucun chemin absolu du répertoire personnel, aucun fichier > 50 Mo.
- [ ] (4) Contrôler la plage `origin/main..HEAD` : aucun chemin sous `data/raw/eurofidai/` ni sous `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo. Puis `git push origin main`, et rapporter le hash du commit et l'état propre de l'arbre.

## Vérification de bout en bout

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
python -m jepadrift.representations.extract --dataset d2_us97 --rep pca --mode factor
python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor
pytest -q tests/test_representations.py
sha256sum data/derived/d2_us97/z_*.npz data/derived/d3_239/z_*.npz   # rerun the two extractions: same hashes
make check
```

## Risques — endossés au GO

| Risque | Parade |
|---|---|
| Ajustement de la représentation sur des lignes déjà dérivées : un τ* tombe dans la calib ou avant elle (E1, H_det = 2000) | L'interface accepte toutes les lignes d'apprentissage ; le choix des lignes sans dérive (pretrain, ou lignes antérieures à τ*) revient aux streams 07 et 12. Signalé dans `interface_Z.md` et dans le wrapup |
| Hashes d'état et du `.npz` dépendants de LAPACK/BLAS | Déterminisme vérifié sur la pile de référence (`.venv`, numpy 2.4.4). Aucun hash d'état n'est épinglé dans les tests ; les valeurs de référence figurent dans le wrapup |
| K sensible à σ² (5 contre 9 sur D2, 10 contre 15 sur `d3_239`) | Tranché par le prompt et le GO : σ² = 1 sur la corrélation. Règle isolée dans `mp_count` ; variante documentée dans `C-repr-mp-K` |
| tail10 compte 123 dimensions sur `d3_239` | Conforme à la règle ; la conséquence pour SPLL relève du stream 19 |
| Durée de la boucle jour par jour pour E1 (1000 onsets par cellule) | 0.04 s par panel pour l'ACP, 0.15 s pour les rangs. Plafond marqué `# ponytail:` : un consommateur pourra vectoriser dans une sous-classe |
| Modification d'`injection.py`, fichier du stream 05 (GO H9) | Opérations identiques, revérifiées au bit près au GO ; `tests/test_injection.py` doit rester inchangé et au vert ; test d'égalité au bit près (Tâche 1) |
| Une décision (GO) à réviser plus tard | Chaque décision est isolée dans une fonction ou un paramètre (`mp_count`, `TAIL_SHARE`, `_day` des sous-classes, `segment_rows`) ; le changement reste local |
