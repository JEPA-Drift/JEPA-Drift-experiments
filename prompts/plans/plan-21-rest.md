# Plan 21-rest : 13 occurrences restantes et architecture minimale du runner et du gel (proposition native, révision 1)

**Statut.** Plan approuvé par le chercheur le 7 novembre 2026 ; GO d'exécution du Lot P direct enregistré dans `prompts/GO-stream-21-rest.md`. Le présent arbitrage remplace l'attente historique et prévaut sur les variantes natives ci-dessous.
- **Fichiers enregistrés par Codex :** `prompts/plans/plan-21-rest.md` et `prompts/GO-stream-21-rest.md`.
- **Portée de l'approbation :** Lot A écarté, Lot P seul autorisé. Lot S documentaire, bornes `UNSOURCED` ; Lot F réservé aux fixtures sous décision distincte ; Lot R différé. Aucun FROZEN réel ni modification du Makefile.

## Révision 1 : réponses à la revue Codex

1. **FAIR.** Les trois niveaux sont distingués (§2.1).
   - La couverture CSV reste à 6/19.
   - Les neuf épingles du lot A sont des contrôles intermédiaires.
   - La clôture FAIR passe par un lot P séparé, soumis à GO : un producteur analytique vers un nouveau CSV via `save_fair_csv`, sans réécriture de J1 et sans Monte Carlo.
   - Aucune exemption au contrat CSV.
2. **Les deux `2.01`** (§3).
   - L'identifiant de chaque occurrence est lié à sa localisation, à sa grandeur, à ses paramètres et à sa lecture.
   - Chaque grandeur reçoit une ancre textuelle.
   - Un témoin permute réellement les références.
   - Limite déclarée : la valeur seule ne peut pas rejeter cette permutation.
3. **Gel** (§4.2, §5).
   - `check` contrôle le chemin, le suivi Git et le SHA du GO d'approbation.
   - `frozen_paths` doit être égal à la politique du schéma.
   - Les liens symboliques sont refusés avant toute résolution ou lecture.
   - Le scellement se fait en deux commits, la cible Makefile précédant le commit gelé.
   - Le témoin positif crée le commit de scellement avant `check`.
4. **Runner** (§4.3).
   - Un arbre sale sur les sources scientifiques est refusé ; le booléen `dirty` disparaît.
   - Six variables d'environnement sont exigées, dont `MPLBACKEND=Agg`.
   - Le benchmark PCA est retiré des cibles.
5. **Lecture monitor** (§1).
   - La formulation est corrigée.
   - Le lecteur borné avant I/O est listé comme prérequis non produit.
   - La conservation des 13 fichiers PCA est désormais présentée comme un choix de périmètre.

Cette révision n'a fait aucune lecture nouvelle du dépôt, n'a exécuté aucun module et n'a lancé aucun test.

## Contexte

- **Mandat.** Cadrage Codex du 7 novembre 2026 (mandat utilisateur), suivi des reprises « continue » et « termine », puis de la revue Codex.
  - Session interactive Opus 5.5, effort Max, sans sous-agent.
  - Worktree `~/JEPA-stream-21-rest`, branche `stream-21-rest`, base `1440927b49463c13bdd0c819fcd73f30d6a32c31`.
- **Problème.** Le stream 21 est en état TERMINER_PARTIEL (amorçage C1).
  - 13 des 19 occurrences porteuses de résultat de `paper/sec3_theory.tex` n'ont pas de source CSV.
  - Le runner global, l'outil de gel, `configs/FROZEN.json` et le gel J4 n'existent pas.
- **Résultat visé.** Une cartographie des occurrences, des lacunes explicites et une architecture minimale, découpées en lots bornés sous GO distincts.
  - Ce plan ne crée ni code, ni FROZEN, ni source.
  - La date J4 (2026-11-08) n'ouvre aucune porte.
- **Sources lues, texte seulement.**
  - Documents de pilotage :
    - `CLAUDE.md` ; amorçage du 7 novembre (B, C1, D, E) ; prompt 21 ; audit 21 ; `MAPPING.md` ;
    - plans, GO et wrapups 21, 21-trace, 21-dpi et 21-appendix ; titres de `DEVIATIONS.md`.
  - Outils et code :
    - `tools/trace_numbers.py`, `tools/pre-commit`, `Makefile` ;
    - `jepadrift/floors.py`, `tests/test_floors.py`, `experiments/e2_floor_validation.py` ;
    - les gardes pré-J4 et les `main(argv)` ;
    - l'identité et le manifeste du runner PCA scellé, le contrat `tests/test_pca_drift_contracts.py`.
  - Résultats : `results/e2/e2_cells.csv` (lignes G1 et S1), `J1_report.md`, et le bloc `costs` du manifeste PCA full.

## 1. Faits établis en lecture seule

### Intégrité à la base

| Fichier | SHA-256 | Remarque |
|---|---|---|
| `results/e2/e2_cells.csv` (J1) | `e315e537…570823` | Identique sur disque et dans l'index ; 47 lignes, 47 CRLF |
| `results/e3/e3_overshoot.csv` | `1ca7c3ae…68b3` | D8 non examiné |
| `paper/sec3_theory.tex` | `6bfebdd0…4013` | |
| `paper/appA_proofs.tex` | `4a5469c8…2a30` | |
| Manifeste PCA full | `3b2299bc…2f47` | |

### Contrat d'identité PCA scellé et choix de périmètre

- **Contrat existant.** `tests/test_pca_drift_contracts.py:1352-1363` recalcule `pdb.identity_block` avec le code courant et exige l'égalité avec l'identité scellée.
  - Le contrat couvre `experiments/pca_drift_benchmark.py` et ses `CODE_MODULES` (`:579-582`) : `floors`, `injection`, `sim`, `pipelines`, `monitors.{calibration,cusum,streams}`, `representations.{base,extract,pca}`, `stats.{covariance,intervals}`.
  - Il couvre aussi les entrées scellées, dont `configs/pca_drift_benchmark.yaml`.
- **Choix de périmètre de ce reliquat.** Ce plan ne modifie aucun de ces 13 fichiers ni aucune de ces entrées, parce que le contrat les recalcule.
  - Les modifier exigerait un GO propre : re-scellement ou amendement du contrat.
  - Ce n'est pas une règle d'immuabilité générale. L'autorité d'écriture définie par `CLAUDE.md` reste entière.

### Gardes pré-J4

Toutes refusent sans condition, et aucune ne lit FROZEN :
- `e1_problem.py` :
  - `check_window` (`:96-100`) ;
  - `--include-test-window` refusé (`:1196-1199`, plafond `# ponytail:` « until stream 21 »), épinglé par `tests/test_e1.py:59-62`.
- `e3_calibration.py:110`, `e10_robustness.py:318-320`, `ipca_k_selection.py:27,39`, `jepa_pretrain.py:33-45`.
- `pca_drift_benchmark.py` (`:568-570`, `:680-697`).
- Les constantes `MONITOR_START` des chargeurs.

Sont absents : `tools/freeze_config.py`, `benchmark_runner`, `configs/FROZEN.json` et la cible `make freeze`. Les cibles Makefile sont `test`, `j1`, `hooks`, `check` et `prompts-check`.

### Lecture monitor

- **Calcul.** Aucun calcul sur la fenêtre monitor n'est autorisé ni implémenté ; les gardes de date refusent sans condition.
- **Lecture physique.** E1 charge physiquement le panneau par `load()`, lignes monitor comprises, avant de le restreindre aux lignes pre_monitor (`e1_problem.py:103-111`). E3 et E10 n'ont pas été vérifiés sur ce point.
- **Prérequis non produit.** Il n'existe pas, pour E1, de lecteur borné avant I/O comparable au lecteur Parquet JEPA (C-jepa-d3-reader). Ce n'est pas une garde acquise.

### Interfaces `main(argv)`

| Script | Options relevées |
|---|---|
| `e1_problem`, `e3_calibration`, `e10_robustness` | `--config`, `--out`, `--fig-dir`, `--log-dir` |
| `pca_drift_benchmark` | `--config`, `--out`, `--log-dir`, plus `--mode`, requis |
| `e2_floor_validation` | `--out` seulement ; écrit `e2_cells.csv` dans ce répertoire |
| `jepa_pretrain` | `--config`, requis ; entraînement, non autorisé |

### Configurations et manifestes

- **Configurations (7 fichiers, préfixes SHA-256) :** `ca_tjepa` `4fd90ba4`, `e1` `281bd590`, `e10` `ac8f135a`, `e3` `6e385738`, `eurofidai_schema` `81c10f20`, `pca_drift_benchmark` `79d2b5e5`, `pca_drift_benchmark_full_2000_resources` `c4be3301`.
- **Manifestes :** `data/derived/MANIFEST.json` `7bf9f22d` ; `docs/manifests/d4_manifest.json` `0a8b83d4` (seules les clés de premier niveau ont été lues).

### Réemploi disponible sans modification

- `tools.trace_numbers.{confined, table, FORM}`. D'après la lecture de la regex, `FORM` tokenise `2.01` en un seul jeton ; à confirmer en RED.
- `confined` accepte un lien interne au préfixe : il ne suffit donc pas pour le gel (§4.2).
- Le hook `pre-commit` neutralise `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` et `GIT_QUARANTINE_PATH`.

### Textes de ligne lus à la base

- l. 80 contient `$M=` et pas `\tau_a/\tau_\gamma=`.
- l. 105 contient `\tau_a/\tau_\gamma=` et pas `$M=`.
- l. 52 contient `expected run to a false alarm`.

### Trace de session

- **Commandes.** Lectures seulement : `git rev-parse/status/log/show`, `sha256sum`, `sed`, `rg`, `grep`, `head`, `ls`, `cat`.
- **Écart déclaré.** `python3 -c "pass"` a été lancé une fois par inadvertance, avec l'interpréteur système : opération vide, aucun import, aucun fichier.
- **Ce qui n'a pas été fait.** Aucun module du projet n'a été exécuté ni importé. Seul ce fichier de plan a été écrit.

## 2. Cartographie des 13 occurrences

### 2.1 Trois niveaux distincts

| Niveau | Contenu | Ce qu'il certifie | Compte |
|---|---|---|---|
| Cartographie documentaire | Localisation, lecture, producteur candidat et lacune de chaque occurrence | Le recensement seulement | 19/19 dans l'audit 21 ; les 13 seraient ajoutées à MAPPING par le lot A |
| Épinglage au code (contrôle intermédiaire) | Un test compare au littéral arrondi l'évaluation du code courant, ou deux cellules scellées | L'accord d'arrondi au moment du test ; pas une source | 0 aujourd'hui ; 9 après le lot A |
| Clôture FAIR (contrat du projet) | Cellule unique d'un CSV produit par un script ; `READ_MATCH` vérifié par `trace_numbers` | Littéral égal à la cellule arrondie ; ni reproduction, ni conclusion scientifique | **6/19, inchangé jusqu'au lot P** |

Le contrat CSV ne connaît pas d'exemption : les épingles ne ferment pas l'obligation.

### 2.2 Occurrences

**Arrondi.** `Decimal(valeur)` exact, quantifié à l'exposant du littéral, en `ROUND_HALF_EVEN`.

**Sources existantes citées dans le tableau :**
- **(i)** `test_floors.py:23-26` vérifie |M − réf| < 0.01.
  - Cette tolérance n'implique pas l'arrondi à deux décimales.
  - Les références proviennent de la note du 11 octobre : le test épingle le code au papier.
- **(ii)** `test_pca_drift_benchmark.py:51-58` vérifie `pdb.mixture_cost ≈ floors` à 1e-10 relatif, et |· − 1.2239| < 6e-5 pour D = 1.
- **(iii)** Le manifeste scellé contient `costs.M[d−1]`, avec `gamma_M` = 504 : `M[0]` en `:104`, `M[9]` en `:113`. C'est un JSON, illisible par l'outil actuel.

| ID | Ligne, littéral | Grandeur, paramètres | Lecture ; approximation | Source existante | Lacune FAIR | Action |
|---|---|---|---|---|---|---|
| `S80-M-D1` | l. 80, `1.22` | `mixture_multiplier`, D = 1, γ = 504 | anytime-valid (γ = seuil de l'e-détecteur) ; fluide | (i) ; (ii) : arrondi 1.22 si le test passe ; (iii) `1.2239421009676454` | Aucun CSV | A, puis P |
| `S80-M-D10` | l. 80, `2.01` | idem, D = 10 | idem | (i) ; (iii) `2.0057517760709644` ; pas de test serré | Aucun CSV ; homonyme de `S105-ABS-R2.5` | A, puis P |
| `S80-M-D64` | l. 80, `3.91` | idem, D = 64 | idem | (i) seulement | Aucun CSV ; arrondi non garanti par (i) | A, puis P |
| `S80-M-D500` | l. 80, `9.64` | idem, D = 500 | idem | (i) ; (ii) 9.6427 ± 6e-5 ; A7 ± 5e-5 (`test_pca_drift_contracts.py:530`) | Aucun CSV | A, puis P |
| `S80-M-D128` | l. 80, `5.2` | idem, D = 128 (tronc JEPA « monitored as such », aucun run JEPA) | idem | Aucune | Ni test ni CSV ; la conclusion `D ≤ 16` (classe B) n'est pas couverte | A, puis P |
| `S105-ABS-R2.5` | l. 105, `2.01` | `absorption_delay(1, r)/1`, r = τ_a/τ_γ = 2.5 ; −(r/2) ln(1−2/r) = (5/4) ln 5 | budget (rapport à τ_γ) ; fluide | `test_floors.py:50-52` : [2.011, 2.013] ⊂ [2.005, 2.015), donc arrondi 2.01 si le test passe | Aucun CSV ; non relié à la ligne | A, puis P |
| `S105-ABS-R4` | l. 105, `1.39` | idem, r = 4 ; 2 ln 2 | idem | Aucune | Ni test ni CSV | A, puis P |
| `S105-ABS-R8` | l. 105, `1.15` | idem, r = 8 ; 4 ln(4/3) | idem | Aucune | Ni test ni CSV | A, puis P |

#### `S52-ARL0ADD-252` : `1.8` (l. 52), valeur dérivée

- **Lecture.** Lecture **exact** : CUSUM calibré à ARL0 = γ = 252, avec SR = 1 et I = 1/504.
  - ADD = Φ(γI)/I est une approximation de **diffusion** (C-e1-readings).
  - « 1.8 times shorter » est lu comme ARL0/ADD (hypothèse H1).
- **Source.** Aucune cellule ne contient ce rapport. Les opérandes sont deux cellules de la ligne scellée `arm=G1, mode=cusum_x, background=gauss, dim=1, sr_annual=1.0, gamma=252` :
  - `arl0_pred` = `252.0` (`e2_floor_validation.py:147`) ;
  - `pred_delay` = `142.0388135314031`, l'entrée 2 de MAPPING.
  - La paire mesurée `arl0_mc` = `258.4925` et `mean_delay` = `145.081` ne correspond pas à la phrase.
- **Formule candidate, non évaluée ici.** Le quotient `Decimal` des deux textes, arrondi au dixième. Son équivalent analytique est γI/Φ(γI) avec γI = 1/2.
- **Lacunes FAIR.**
  - La valeur ne tient pas dans une cellule unique.
  - `trace_numbers` refuse les littéraux décimaux (`:154-156`).
  - Le choix des opérandes reste une déclaration.
- **Action.** Contrôle intermédiaire dans le lot A ; cellule unique dans le lot P.

#### `S111-VM-LO`, `S111-VM-HI`, `S111-EXP-LO`, `S111-EXP-HI` : `13`, `16`, `8`, `11` (l. 111)

- **Statut.** Ces quatre bornes restent `UNSOURCED`.
- **Lecture.**
  - « 13 to 16 » : ordre de grandeur de CV²(I_t)·τ_int(I_t) pour un GARCH(1,1) de paramètres (0.08, 0.90), innovations t7.
  - « 8 to 11 » : mesure attribuée à `sec:exp-floors`, section absente de `paper/`.
- **Sources consultées.**
  - Aucun code ne calcule CV² ni τ_int.
  - Le docstring `e2_floor_validation.py:18-19` dit « about 10-15 days » : écart consigné, non tranché.
  - La prose provient de `prompts/Plan_Claude_Opus_v4_correction.md:776-777`, sans dérivation.
  - Les lignes S1 de `e2_cells.csv` sont les seules mesures GARCH du périmètre lu.
- **Fait de code.** Sur les lignes S1 :
  - `pred_delay` = (ln γ + ½ ln 2p̄)/I (`:213,216`), alors que `first_order` = ln γ/I ;
  - la référence « ln γ/Ī » correspond donc à `first_order`.
- **Exclusions.** Aucune recherche post hoc d'opérandes, aucune édition du papier, aucun changement de paramètre.
- **Action (lot S, sans code).**
  - Demander aux auteurs de `sec:exp-floors` la définition, l'estimateur (dont la fenêtre de τ_int), les valeurs de SR, γ et mode, et le producteur.
  - Toute source fournie passera par un lot séparé.
  - Une simulation exige un mandat propre.

## 3. Lot A : contrôle intermédiaire (cartographie documentaire et épinglage au code)

**Portée.** Le lot A ne modifie pas la couverture CSV, qui reste à 6/19, et ne crée aucun CSV.

**Fichiers de Claude :**
- `tests/test_sec3_values.py` (nouveau) ;
- `docs/MAPPING.md` :
  - section ajoutée `## Occurrences not traced to a CSV` ;
  - une phrase ajoutée à l'introduction, qui la signale ;
  - reformulation de la ligne « Not mapped » de Coverage, qui reste à « 13 of 19 » ;
  - les sections Entries et Check inputs restent identiques octet pour octet ;
- `prompts/wrapups/wrapup-21-rest.md` et journaux ignorés `logs/stream_21_rest/`.

Restent inchangés : `tests/test_floors.py`, `tests/test_trace_numbers.py`, les outils, le papier, les résultats et les producteurs.

**Contrat du test.** Bibliothèque standard, plus `jepadrift.floors` et `tools.trace_numbers.{FORM, table}`, en lecture seule.

1. **`EXPECTED`.** Une ligne par ID des 13 occurrences, avec les champs :
   - localisation, littéral, grandeur, paramètres ;
   - lecture (budget, anytime-valid ou exact) et approximation (fluide ou diffusion) ;
   - contrôle, statut, ancre.
   - Statuts : `CODE_PINNED` (8), `DERIVED_CELL_CHECK` (1), `UNSOURCED` (4, sans contrôle de valeur).
   - Ancres :
     - `mixture_multiplier` : `$M=` ;
     - `absorption_delay` : `\tau_a/\tau_\gamma=` ;
     - rapport ARL0/ADD : `expected run to a false alarm`.
2. **Pour chacune des 9 lignes contrôlées :**
   - (a) le littéral est exactement un jeton `FORM` complet sur la ligne déclarée ; le papier est lu en octets et décodé en UTF-8 strict ;
   - (b) l'ancre de la grandeur figure sur cette ligne ;
   - (c) la valeur est finie et s'arrondit au littéral ;
   - (d) pour `1.8` :
     - J1 est lu avec `csv.DictReader(strict=True)` ; son SHA est vérifié avant et après la lecture ;
     - la clé complète sélectionne une seule ligne ;
     - les textes `252.0` et `142.0388135314031` sont exacts ;
     - le quotient arrondi au dixième vaut 1.8.
3. **Sentinelle MAPPING.** La section est comparée **ligne à ligne par ID** à `EXPECTED`, sur l'égalité de tous les champs. Ce n'est pas un ensemble de couples (emplacement, littéral). Comptes : 6 + 13 = 19.
4. **Paramètres des helpers.** Les helpers reçoivent `root` et la table attendue en paramètres, pour que les témoins puissent tourner sur des copies.

**Témoins de rejet (TDD) :**

- **RED-1.** Test seul, section absente : échec.
- **RED-2 : mutants.** Ils tournent hors dépôt, dans un processus neuf, par `monkeypatch` ; `floors.py` n'est jamais édité (choix de périmètre, §1).
  - `mixture_multiplier(1, ·)` renvoie 1.2149 : l'ancien test passe, l'épingle échoue.
  - +0.006 sur le rapport d'absorption : échec.
- **Les deux `2.01`.**
  - **Limite déclarée.** Les valeurs lues (`M[9]` = `2.0057517760709644`) et la borne du test existant (A(2.5) ∈ [2.011, 2.013]) arrondissent toutes deux à 2.01. La permutation n'est donc pas détectable par la valeur, et le contrat ne promet pas ce rejet.
  - **W-2.01-a.** Dans une copie de MAPPING, on échange la grandeur et les paramètres de `S80-M-D10` et `S105-ABS-R2.5`, en gardant les emplacements et les littéraux. Résultat attendu : refus par la comparaison par ID.
  - **W-2.01-b.** On passe au helper une table attendue où les producteurs des deux `2.01` sont échangés.
    - Le test vérifie explicitement que l'épreuve de valeur passe pour les deux lignes.
    - Il exige ensuite que l'ancre échoue : `\tau_a/\tau_\gamma=` est absent de la l. 80, et `$M=` de la l. 105.
    - Résultat attendu : refus.
  - **W-ligne.** D = 1 et D = 10 permutés sur la l. 80 : refus par la valeur (1.22 ≠ 2.01).
  - **Portée de l'ancre.** Elle prouve une co-présence textuelle sur la ligne, pas un lien sémantique. Elle suffit ici parce que les lignes 80 et 105 portent des ancres disjointes.
- **Autres témoins.**
  - Littéral altéré dans une copie du papier.
  - Texte d'opérande altéré ; `mode` retiré de la clé ; ligne dupliquée.
  - Ligne MAPPING retirée, ajoutée, ou dont le statut ou la lecture change.
  - r = 2, valeur infinie : échec explicite.
- **GREEN.** Aucun `skip`, aucun `xfail`.

**Cas limites :**
- Les remplacements en mémoire de `test_trace_numbers` exigent une occurrence unique (`:49`). La nouvelle section ne doit dupliquer aucune de leurs chaînes ; à vérifier par `grep` avant l'écriture.
- Le titre de la section ne doit pas commencer par `## Entries`.
- La CLI `trace_numbers` affiche toujours « 13 of 19 not covered », ce qui reste exact.

## 4. Lot P : clôture FAIR des neuf valeurs (lot séparé, GO distinct, proposé)

- **Producteur.** `experiments/sec3_analytic_values.py`, avec `main(argv)` et argparse.
  - `--out` désigne un nouveau fichier ; l'écrasement est refusé.
  - Imports limités à `jepadrift.floors` et `jepadrift.pipelines.save_fair_csv`.
  - Aucun générateur aléatoire, aucun bras Monte Carlo d'E2, aucune lecture ni réécriture de J1.
- **Sortie.** `results/sec3/sec3_analytic.csv`, écrite via `save_fair_csv`.
  - Une ligne par grandeur instanciée : `quantity`, ses paramètres et `value`.
  - Le rapport γ/ADD exact (γ = 252, SR = 1) y figure, ce qui donne une cellule unique pour `1.8`.
- **Cartographie.** `trace_numbers` ne lit aujourd'hui qu'un CSV et refuse les littéraux décimaux (deux plafonds `# ponytail:`). Le lot P doit étendre, sous GO :
  - le format : une source par entrée, des colonnes de clé par source, une quantification à l'exposant du littéral ;
  - la sentinelle 21-trace.
- **Les deux `2.01`.** Des clés CSV permutées produiraient aussi deux `READ_MATCH`. Le lot P doit donc porter dans l'outil l'identifiant lié et l'ancre de grandeur.
- **Couverture.** Seul ce lot peut porter la couverture CSV au-delà de 6/19, et seulement après un `READ_MATCH` vérifié. Les bornes de la l. 111 restent hors de son périmètre.

## 5. Architecture minimale du runner et du gel

### 5.1 Phases

| Phase | Contenu | Autorité | État |
|---|---|---|---|
| Conception | Ce plan | Revue Codex | En cours |
| Lot F, gel | `tools/freeze_config.py` et tests sur fixtures ; aucun FROZEN réel ni cible Makefile | GO Codex | Proposé |
| Lot R, runner | Runner mince | GO Codex, après le protocole E5 et le lecteur borné | Différé |
| Activation J4 | Commit gelé, écriture de FROZEN, commit de scellement, exécutions sur la fenêtre de test | GO du chercheur ; prérequis du §8 | Hors plan |

### 5.2 Identité de gel (schéma seulement ; aucun fichier créé)

```json
{"schema": "jepadrift-freeze/1",
 "commit": "<40 hex : commit gelé C>",
 "frozen_paths": ["Makefile", "conda-torch.lock", "conftest.py", "configs", "experiments", "jepadrift",
                  "requirements.lock", "requirements.txt", "tools/benchmark_runner.py", "tools/freeze_config.py"],
 "configs": {"configs/<nom>.yaml": "<sha256 des octets>"},
 "manifests": {"data/derived/MANIFEST.json": "<sha256>", "docs/manifests/d4_manifest.json": "<sha256>"},
 "approval": {"path": "prompts/GO-<…>.md", "sha256": "<sha256>"}}
```

- **Politique.** La constante `POLICY["jepadrift-freeze/1"]` du vérificateur contient la liste `frozen_paths` ci-dessus, triée. `check` exige l'égalité exacte de la liste lue avec cette constante. Une liste réduite, élargie ou permutée est refusée.
- **Identifiant.** `freeze_id` est le SHA-256 des octets canoniques : clés triées, séparateurs compacts.

**Protocole de scellement (activation J4, hors plan).** Il n'y a pas de référence circulaire : FROZEN cite C, et C ne cite pas FROZEN.
1. **Commit C (commit gelé).** Il contient la cible `make freeze`, les configurations définitives, les manifestes et le GO d'approbation suivi.
2. **Écriture.** Sur un arbre propre, `freeze_config --write --approval <GO>` écrit FROZEN avec `commit = C`, sans rien commiter.
3. **Commit S (scellement).** Il ajoute **uniquement** `configs/FROZEN.json` et a C pour unique parent.
4. **Contrôle.** `check` ne peut réussir qu'après S.

**`check(root)`** refuse en état fermé, avec un message `freeze: error: …`.
1. **Liens symboliques, avant toute résolution ou lecture.**
   - Concerne FROZEN, le GO d'approbation, les configurations et les manifestes.
   - Chaque composant du chemin, de la racine au fichier, est examiné par `lstat` ; tout lien est refusé.
   - La lecture se fait par `os.open(…, O_RDONLY | O_NOFOLLOW)` et exige un fichier régulier.
2. **FROZEN.**
   - UTF-8 strict et JSON strict : doublons, NaN et Infinity sont refusés.
   - L'ensemble des clés est exact et `schema` est connu.
   - `frozen_paths` est égal à `POLICY`, et les formats hexadécimaux sont valides.
3. **Scellement.**
   - `git log --format=%H --diff-filter=A -- configs/FROZEN.json` rend exactement un commit S.
   - S a un seul parent, égal à `commit`.
   - `git diff --name-only commit S` se réduit à `configs/FROZEN.json`.
   - S est un ancêtre de HEAD.
   - FROZEN est inchangé depuis S : diff vide, et octets de l'arbre égaux à `git show S:configs/FROZEN.json`.
4. **Sources.**
   - `git diff --quiet <commit> HEAD -- <POLICY> ':(exclude)configs/FROZEN.json'` ;
   - `git status --porcelain --untracked-files=all -- <POLICY>` est vide.
5. **Configurations.** L'ensemble des `configs/*.yaml` est égal aux clés de `configs`, avec les mêmes empreintes.
6. **Manifestes.** Les empreintes sont égales.
7. **Approbation.**
   - Le chemin est conforme à la politique (`prompts/GO-*.md`).
   - Le fichier est présent dans l'arbre de `<commit>` (`git cat-file -e`).
   - Le SHA-256 du blob à `<commit>` est égal à `approval.sha256`.
   - Le fichier est inchangé dans HEAD et dans l'arbre de travail.

**Appels git.** Ils se font dans un environnement purgé de `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE`, `GIT_QUARANTINE_PATH`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` et `GIT_COMMON_DIR`.

**`write(root, approval)`.**
- Il exige :
  - l'absence de FROZEN : `open(…, "xb")` échoue aussi sur un lien ;
  - un arbre propre sur `POLICY` ;
  - une approbation suivie, commitée à HEAD et inchangée.
- Il enregistre `commit = HEAD`.
- Dans le lot F, il ne s'exécute que sur des fixtures. La cible `make freeze` est ajoutée par l'activation, avant C.

**Périmètre par défaut.**
- Configurations gelées : tous les `configs/*.yaml` (Q9).
- Hors gel : `results/`, `figures/`, `logs/`, `paper/`, `prompts/` (sauf le GO d'approbation) et `docs/` (sauf les manifestes).
- Seuls les manifestes de données sont hachés (H11).

### 5.3 Runner : contrat seulement (lot R)

- **Emplacement.** `tools/benchmark_runner.py` (Q11). Placé dans `jepadrift/`, il inverserait la dépendance entre la bibliothèque et `experiments/`.
- **Réemploi.**
  - Il réemploie `freeze_config`.
  - Il reprend en bibliothèque standard les motifs du runner PCA : `canon`, `hashlib.file_digest`, séparation entre identité et provenance, exclusion du temps et des chemins, sortie exclusive.
  - Il n'importe pas le module scellé, et ne le modifie pas (choix de périmètre).
- **Cibles.** La table définitive viendra du protocole E5.
  - Candidates de conception : `e1.yaml`, `e3.yaml` et `e10.yaml`.
  - Chacune porte `bounded_reader: false`. Le runner refuse tout dispatch réel tant que deux conditions manquent : un lecteur borné avant I/O pour cette cible, et un mandat.
  - Les tests utilisent seulement des cibles factices injectées.
- **Exclusions.**
  - **Le benchmark PCA scellé n'est pas une cible.** Son usage reste documentaire : inspection et réemploi des motifs, sans relance.
  - Sont aussi exclus :
    - `ca_tjepa.yaml`, entraînement non autorisé ;
    - `eurofidai_schema.yaml`, schéma de chargeur ;
    - `*_resources.yaml`, surcouche de ressources ;
    - E2, qui n'a pas de `--config` et dont J1 est scellé.
- **Entrée.** `python -m tools.benchmark_runner --config configs/<nom>.yaml [-- extras]`.
  - Un drapeau géré passé en extra est refusé : `--config`, `--out`, `--fig-dir`, `--log-dir`, `--include-test-window`.
  - Une configuration hors table ou hors `configs/` est refusée.
- **Identité sans ambiguïté.**
  - Refus si `git status --porcelain --untracked-files=all -- <POLICY>` n'est pas vide. Le commit identifie alors les sources scientifiques.
  - `run_id` = SHA-256 de `canon({schema, target, config: {chemin: sha}, argv scientifique normalisé, commit, manifests, freeze_id ou null, env, python})`, sans champ `dirty`.
  - `--jobs` et `--resume` restent hors de l'identité et vont en provenance (`tests/test_e1.py:172-187`).
- **Environnement.** Six variables sont exigées à l'identique, avant l'import de la cible, et consignées dans l'identité :
  - `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` ;
  - `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`.
- **Sorties.**
  - Création exclusive de `results/<stem>/run-<id16>/`, `figures/<stem>/run-<id16>/` et `logs/<stem>/run-<id16>/`.
  - Le runner n'écrit jamais dans les répertoires par défaut.
  - Il garde les CSV des producteurs ; ne pas imposer de schéma unifié est un écart au prompt 21 §1, à déclarer (Q12).
  - `run.json` contient l'identité, le code de sortie et les SHA-256 des sorties, sans horodatage.
- **Fenêtre de test.** Aucun calcul monitor n'est autorisé. `--include-test-window` n'arrive qu'avec E5, dans cet ordre :
  1. `freeze.check`, avant tout import ou chargement ;
  2. un lecteur borné avant I/O ;
  3. la transmission à une cible qui déclare le drapeau.

  Les gardes des scripts restent la dernière barrière.
- **Critères du prompt 21.**
  - La reproduction bit à bit d'E1 exige un mandat sur données réelles antérieures à 2020 **et** le lecteur borné. Le fichier cible est `9ae7e261…` ; le run se fait dans un répertoire neuf, jamais dans `results/e1`.
  - Le gel qui bloque une configuration modifiée relève des fixtures du lot F.
  - Le nombre altéré est déjà couvert par 21-trace.

## 6. Lot F : outil de gel sur fixtures

**Fichiers de Claude :**
- `tools/freeze_config.py` : bibliothèque standard, git via `subprocess` ; CLI `--check` et `--write --approval <chemin>` ;
- `tests/test_freeze_config.py` ;
- le wrapup et les journaux ignorés.

Ni Makefile, ni expérience, ni FROZEN réel.

**Fixtures.** Dépôts créés dans `tmp_path` :
- identité de commit passée par `-c user.*` ;
- `HOME` et `GIT_CONFIG_GLOBAL` isolés, `GIT_CONFIG_NOSYSTEM=1`.

**Témoins :**
1. **Positif.**
   - Commit C : configurations, code factice, manifestes, `Makefile` factice avec sa cible, GO factice suivi.
   - `write`, puis `check` : **refus** tant que FROZEN n'est pas suivi.
   - Commit S, limité à FROZEN, puis `check` : **succès**, avec une sortie déterministe.
2. **Après S.** Un commit limité à `docs/`, `results/` ou `prompts/` (hors GO d'approbation) est accepté.
3. **Configurations.** Un octet modifié, un ajout ou un retrait : refus.
4. **Code et Makefile.**
   - Un commit sous `jepadrift/`, `experiments/` ou `Makefile` après C est refusé.
   - S est refusé s'il touche un autre fichier que FROZEN, `Makefile` compris.
5. **Scellement.** Chacun des cas suivants est refusé :
   - FROZEN modifié après S ;
   - FROZEN supprimé puis réajouté, ce qui donne deux ajouts ;
   - S avec deux parents, ou un parent différent de `commit` ;
   - FROZEN non suivi.
6. **Approbation.** Chacun des cas suivants est refusé :
   - chemin hors politique ;
   - fichier non suivi ou absent de C ;
   - SHA différent ;
   - GO modifié après C ;
   - lien symbolique.
7. **FROZEN.** Chacun des cas suivants est refusé :
   - fichier absent ou JSON invalide ;
   - NaN ;
   - clé dupliquée, manquante ou en trop ;
   - hexadécimal invalide ;
   - `schema` inconnu ;
   - `frozen_paths` réduit, élargi ou permuté.
8. **Liens.** Chacun des cas suivants est refusé avant toute lecture :
   - FROZEN lien vers un fichier valide de `configs/` ;
   - `configs/` lui-même lien ;
   - configuration ou manifeste lien.
9. **Historique.** Commit non ancêtre (branche orpheline) ou objet absent : refus.
10. **Manifeste.** Manifeste modifié : refus.
11. **`write`.** Refus si FROZEN existe déjà (lien pendant compris), si l'arbre est sale, ou si l'approbation n'est pas commitée.
12. **Environnement git.** `GIT_DIR` pointé vers un autre dépôt : résultat inchangé.
13. **Imports.** Limités à la bibliothèque standard et à `tools`.
14. **Option Q13.** Sentinelle d'absence de FROZEN dans le dépôt réel.

**Contrôles ciblés.**
- `pytest` sur ce test et `test_trace_numbers`, puis `pyflakes`.
- Sur le dépôt réel, `--check` doit sortir avec le code 1 et le motif « absent ».

## 7. Lot R : runner (différé)

**Déclencheur :** protocole E5 approuvé, lecteur borné produit et GO.

**Fichiers :** `tools/benchmark_runner.py` et `tests/test_benchmark_runner.py`.

**Témoins :**
- **Refus d'entrée.**
  - Arbre sale sur `POLICY`.
  - Chacune des six variables d'environnement, absente ou différente.
  - `pca_drift_benchmark.yaml`, qui n'est pas une cible.
  - Configuration hors table ou hors `configs/`.
  - Répertoire de sortie existant.
  - Extra qui redéfinit un drapeau géré.
- **Dispatch réel.** Une cible réelle avec `bounded_reader: false` est refusée.
- **Identité.**
  - `run_id` reste stable à entrées égales et change avec l'argv scientifique.
  - `--jobs` n'a pas d'effet.
- **Sorties.**
  - `run.json` ne contient ni temps ni chemin absolu.
  - Le code de sortie de la cible est propagé.
  - Aucune écriture dans les répertoires par défaut.

## 8. Prérequis manquants du gel (les dépendances restent ouvertes)

1. Le protocole E5 (stream 22) et ses configurations. Aucun `configs/e4*` ni `configs/e5*` n'existe ; l'ensemble à geler reste ouvert.
2. Un lecteur borné avant I/O pour toute cible réelle. E1 charge le panneau entier ; E3 et E10 ne sont pas vérifiés.
3. Un mandat pour tout dispatch ou toute reproduction réelle, y compris le critère E1.
4. Les conditions de l'amorçage, section D : 16 ; 17 recevable ; 19 ; 21 effectif ; 23 phase 2 ; 18 et 20 en complément.
5. La décision du chercheur, sous la forme d'un GO suivi, commité dans C.
6. La cible `make freeze` et les configurations définitives, commitées dans C par le lot d'activation.
7. Une politique de vérification des fichiers de données. Aucune vérification contre `MANIFEST.json` au chargement n'a été trouvée, par une recherche ciblée non exhaustive.
8. La décision sur `POLICY` v1 et les questions du §12.
9. Le lot P pour la clôture FAIR des neuf valeurs, et une source pour les quatre bornes.

## 9. Dépendances et étapes sérialisées

1. Revue Codex. Codex rédige ensuite le plan, le GO et les écarts éventuels dans `DEVIATIONS.md`.
2. Lot A, dans un créneau de validation exclusif, car il importe `floors` et les helpers de trace. Clôture Codex : réindexation AST, `make check` par le hook, commit, push.
3. Lot P, sous un GO séparé et dans un créneau exclusif. Il suit A, ou le remplace (Q1).
4. Lot F, dans un créneau exclusif, puis clôture Codex.
5. Lot S : une demande au chercheur.
6. Lot R : après le protocole E5 et le lecteur borné.
7. Activation J4 : conditions du §8.

Aucune dépendance nouvelle n'est ajoutée : bibliothèque standard, plus numpy et scipy déjà épinglés pour les lots A et P. Un seul `make check` tourne à la fois.

## 10. Garanties scientifiques

- **Couverture CSV.** Elle reste à 6/19 après le lot A. Seul le lot P peut l'augmenter, après un `READ_MATCH` vérifié. Aucune exemption au contrat CSV.
- **Statuts intermédiaires.** `CODE_PINNED` et `DERIVED_CELL_CHECK` ne valent ni `READ_MATCH` ni reproduction. Les lectures (budget, anytime-valid, exact) et les approximations (fluide, diffusion Φ) restent nommées.
- **Calculs.**
  - Aucun Monte Carlo, aucun générateur aléatoire.
  - Le lot A lit J1 en lecture seule, sous contrôle de SHA ; le lot P ne touche pas J1.
- **Inchangés.**
  - Le papier et les paramètres ne sont pas modifiés ; les quatre bornes restent `UNSOURCED`.
  - J1 est intact (disque, index, 47 CRLF).
  - D8 reste en FAIL à +5,2833 %.
  - Le PCA scellé n'est pas relancé, et ses 13 fichiers d'identité restent hors du périmètre.
- **Exclusions.** Aucun FROZEN, aucun `make freeze`, aucun J4, aucune donnée 2020+ ni donnée propriétaire.

## 11. Hypothèses et valeurs par défaut

- **H1.** « 1.8 times shorter » se lit ARL0/ADD, avec des opérandes analytiques.
- **H2.** La précision retenue est celle du littéral. L'arrondi `ROUND_HALF_EVEN` porte sur le `Decimal` exact de la valeur, ou sur le texte de la cellule.
- **H3.** γ = 504 est le seuil de l'e-détecteur. L'expression « (ARL0 = 504) » de `test_floors.py:24` est approximative et ne justifie aucune modification.
- **H4.** τ_γ est le budget ; le rapport est sans échelle.
- **H5.** Un ID lie localisation, grandeur, paramètres et lecture. Les deux `2.01` se distinguent par l'ID et par l'ancre, pas par la valeur (H13).
- **H6.** Une référence de test n'est pas une cellule CSV.
- **H7.** Le gel porte sur les octets.
- **H8.** Le commit gelé C est le parent unique du commit de scellement S.
- **H9.** Aucun calcul monitor n'est possible aujourd'hui, quelle que soit la date. E1 lit cependant physiquement les lignes monitor au chargement.
- **H10.** Ne pas modifier les 13 fichiers d'identité PCA est un choix de périmètre lié au contrat scellé, pas une règle générale.
- **H11.** Seuls les manifestes de données sont gelés.
- **H12.** `wrapup-21-rest.md` est rafraîchi à chaque lot.
- **H13.** Les deux `2.01` arrondissent identiquement : leur permutation est indétectable par la valeur.
- **H14.** Le runner refuse un arbre sale sur `POLICY`, au lieu de chercher à identifier un état sale.

## 12. Questions d'arbitrage (défaut entre crochets)

- **Q1.** [Lot A comme contrôle intermédiaire, puis lot P.] Variante : lot P seul, ce qui rend A redondant.
- **Q2.** `1.8` dans le lot A : [contrôle par les deux cellules scellées]. Variante : épingle via `cusum_exact`.
- **Q3.** [Nouveau fichier `tests/test_sec3_values.py`.] Variante : ajout à `tests/test_floors.py`.
- **Q4.** Emplacement de la cartographie documentaire : [section de MAPPING, avec la phrase d'introduction et la reformulation de Coverage]. Variante : document séparé, avec seule la ligne de Coverage mise à jour.
- **Q5.** Lot P : [lot séparé, nom et chemin proposés, extension de `trace_numbers` incluse]. Variante : extension de `trace_numbers` dans un lot à part.
- **Q6.** Bornes de la l. 111 : [demande au chercheur ; statut `UNSOURCED`]. Qui transmet la demande ?
- **Q7.** Lot F : [après A, sur fixtures]. Variante : différé jusqu'à l'activation.
- **Q8.** `POLICY` v1 : [liste du §5.2]. Variante : tout `tools/`, ou une liste réduite.
- **Q9.** Configurations gelées : [tous les `configs/*.yaml`]. Variante : sans la surcouche de ressources.
- **Q10.** Format de l'approbation : [`prompts/GO-*.md`, suivi, commité dans C].
- **Q11.** Emplacement du runner : [`tools/`, avec un écart `C-*` déclaré]. Variante : `jepadrift/`.
- **Q12.** Sorties du runner : [CSV des producteurs et `run.json`]. Variante : schéma unifié.
- **Q13.** Sentinelle d'absence de FROZEN : [oui, dans le lot F].
- **Q14.** Entrées `DEVIATIONS.md` : [rédigées par Codex].
- **Q15.** `figures/make_*` : [hors 21-rest].

## 13. Hors périmètre

- `figures/make_*`.
- Toute exécution d'E1, E2, E3 ou du benchmark PCA.
- La vérification des fichiers de données.
- Le chemin monitor d'E5.
- La source SPLL, qui relève du stream 19 ; aucune exploration n'a été faite ici.

## 14. Vérification des lots futurs

Chaque commande échoue en cas d'écart.

```bash
set -euo pipefail
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
J1=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
.venv/bin/python -m pytest -q tests/test_sec3_values.py tests/test_floors.py tests/test_trace_numbers.py   # lot A
.venv/bin/python -m pytest -q tests/test_freeze_config.py                                                 # lot F
.venv/bin/python -m pyflakes tools/freeze_config.py tests/test_sec3_values.py tests/test_freeze_config.py
test "$(sha256sum < results/e2/e2_cells.csv | cut -c1-64)" = "$J1"
test "$(git show :results/e2/e2_cells.csv | sha256sum | cut -c1-64)" = "$J1"
test "$(grep -c $'\r$' results/e2/e2_cells.csv)" = 47 && test "$(wc -l < results/e2/e2_cells.csv)" = 47
test "$(sha256sum < results/e3/e3_overshoot.csv | cut -c1-64)" = 1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3
git diff --quiet HEAD -- paper results experiments jepadrift configs Makefile tools/trace_numbers.py tools/dpi_lint.py \
  tools/appendix_b.py tests/test_floors.py tests/test_trace_numbers.py
test ! -e configs/FROZEN.json
```

- Le diff de MAPPING se limite à la section ajoutée, à la phrase d'introduction et à la ligne de Coverage.
- Entries et Check inputs sont comparés octet pour octet à `git show HEAD:docs/MAPPING.md`.
- Le `make check` complet est exécuté par le hook de clôture de Codex.
- Codex refuse tout chemin absolu dans les fichiers livrés et dans la plage poussée, après un contrôle dédié avant push.

## Décision GO intégrée

**GO ACCORDÉ POUR LE LOT P DIRECT — décision explicite du chercheur, 7 novembre 2026.**

Le périmètre exécutable est celui de `prompts/GO-stream-21-rest.md` : producteur analytique, CSV FAIR neuf, extension du checker et de ses tests, MAPPING et wrapup. La cible est 15/19 après vérification effective ; aucun statut anticipé. Les quatre bornes de la l. 111 restent `UNSOURCED`. A est écarté ; F n'est pas implémenté par ce GO et restera confiné aux fixtures ; R et J4 restent différés. Les validations et toute la clôture sont sérialisées par Codex ; le push attend la confirmation exigée au moment de l'action.

## Revue Codex de la planification — 7 novembre 2026

- Proposition native révisée relue ; SHA-256 de la source : `81795aed4b400cbc8ef5fa16db6ee217044267542d9a83502f4fcaeb412ca5fc`.
- L'archivage initial avait clos la préparation sans autoriser d'implémentation. Le nouvel ordre du chercheur autorise maintenant le seul Lot P, suivant le GO intégré ci-dessus.
- **Arbitrage Q1 de conception : lot P seul.** Le contrôle intermédiaire A est écarté comme redondant avec le futur producteur analytique et la vérification CSV. Ses témoins utiles sur les identifiants, les deux `2.01` et les ancres devront être repris par le lot P, sous son propre plan/GO ; aucun test intermédiaire n'est créé ici.
- La couverture CSV reste 6/19 ; les quatre bornes restent `UNSOURCED`. La source de ces bornes sera demandée dans un échange séparé, sans message externe envoyé par cette session.
- Le lot F reste une proposition sur fixtures ; le runner, le lecteur borné et l'activation J4 restent différés. La politique de gel n'est pas un protocole approuvé. Aucun `FROZEN.json`, donnée réelle ou entraînement n'est autorisé. Seuls les calculs analytiques du Lot P sont désormais permis.
