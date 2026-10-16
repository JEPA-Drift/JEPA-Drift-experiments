# DEVIATIONS — JEPA-Drift (Article C)

Écarts au plan ou à l'Article B, consignés sous un identifiant `C-<topic>`.

## C-push-policy — politique de push (2026-10-16)

Le plan initial (« aucun `git push` avant l'accord de propriété intellectuelle LUSIS CIFRE »,
mémoire projet) est amendé par le chercheur le 2026-10-16 : après chaque stream traité, l'agent
qui le termine exécute `tools/reindex_graphify_jcodemunch.sh`, `make check`, un commit explicite
(Conventional Commits) puis `git push origin <branche courante>`. Condition : l'adresse du dépôt
n'est ni partagée publiquement ni liée à une publication — le dépôt est le compagnon anonymisé
d'une soumission anonyme (« anonymous submission »), les commits restent anonymisés (identité
`JEPA-Drift Authors <jepa.drift@gmail.com>`, aucun nouvel identifiant d'auteur ou d'institution).
Les gardes EUROFIDAI sont inchangées : les données propriétaires ne quittent jamais la machine,
`data/raw/eurofidai/` et `data/derived/d4_eurofidai/` restent ignorées et bloquées, et aucun push
ne doit les contenir (aucun fichier de plus de 50 Mo non plus).

Vérification 2026-10-16 : `https://github.com/JEPA-Drift/JEPA-Drift-experiments` répond HTTP 200
(dépôt public, soumission anonyme) ; l'alias SSH `github-jepa-drift` pointe vers `github.com` ;
aucune donnée EUROFIDAI suivie par git ; la plage `origin/main..HEAD` ne contient aucun chemin
eurofidai. Le push est effectué conformément à l'amendement, la condition portant sur le partage
de l'adresse (et non sur l'accessibilité du dépôt, voulue pour la soumission anonyme).

## C-eos-protocol — protocole de fin de stream (amendement complémentaire, 2026-10-16)

Complément de `C-push-policy`. Avant **chaque** commit, l'instance chargée de l'implémentation
(Mistral Vibe ou Claude Code) invoque sa directive de wrapup et enregistre le résumé produit dans
`prompts/wrapups/wrapup-[XX].md` ([XX] = numéro ou référence du stream ; fichier rafraîchi à chaque
commit). Chronologie exacte en fin de stream : (1) wrapup + enregistrement ; (2) réindexation via
`tools/reindex_graphify_jcodemunch.sh` ; (3) `make check` puis commit unique — ou multiples si les
travaux sont hétérogènes et risquent des erreurs sur une partie des livrables — ; (4)
`git push origin <branche>`. Le chercheur a confirmé le 2026-10-16 que le dépôt GitHub, public,
n'est connu de personne : l'instruction de push après chaque stream ne souffre aucune exception.
Les rôles des répertoires sont désormais décrits dans AGENTS.md (« Repository layout »), notamment
`prompts/streams/` (prompts des streams planifiés) et `prompts/wrapups/` (résumés des traitements
des streams).

## C-plan-recording — enregistrement des plans de stream (2026-10-16)

Nouvelle règle du projet (amendement 2026-10-16) : lorsqu'un plan d'implémentation est créé pour
un stream [XX] (demande textuelle explicite de l'utilisateur, ou appel direct de la directive
`/plan`), il est enregistré dans `prompts/plans/plan-[XX].md` AVANT son exécution. Le rôle du
répertoire `prompts/plans/` est documenté dans AGENTS.md (« Repository layout »).

## C-D2-survivor — périmètre des données (2026-10-16)

D2 est le panel des 97 actions américaines survivantes du dépôt B (R15 : 5154 jours × 97 titres,
2005-01-04 à 2025-06-30). Échantillon biaisé par la survie, réutilisé tel quel et sans re-filtrage :
le panel est la population de l'Article B, et tout re-filtrage romprait l'identité bit à bit avec le
code de référence.

## C-interface-f64 — interface (2026-10-16)

`ret` est stocké et retourné en float64 (et non float32) : lu avec `float_precision='round_trip'`,
il est identique bit à bit aux séries CSV de l'Article B (chaîne SHA-256 des entrées et des sorties
dans `data/derived/MANIFEST.json`).

## C-D3-no239 — liste des 239 titres CD-DFM absente (2026-10-16)

Le dépôt `alexouadi/CD-DFM` (cloné dans `external/cd-dfm/`, commit épinglé dans le manifeste) ne
contient pas la liste explicite des 239 titres du S&P 500 utilisés par Alouadi & Lehalle
(arXiv:2607.24410) : le README indique « We cannot redistribute the panel » (caractéristiques
RavenPack/Compustat sous licence). Règle de repli déterministe appliquée : parmi les 503
constituants actuels du S&P 500 (Wikipedia), les 239 titres retenus sont ceux ayant le plus grand
nombre de jours de trading depuis 2000-01-01 (ex æquo : ordre alphabétique). La sélection est
enregistrée dans `data/derived/d3_239/selection.json` et vérifiée par le test
`test_d3_239_selection`.

## C-D3-survivor — constituants actuels du S&P 500 (2026-10-16)

`d3_500` est construit à partir des constituants actuels du S&P 500 (table Wikipedia « List of
S&P 500 companies », 503 titres au 2026-10-16), et non d'une sélection par survie. Contrairement
à D2 (97 survivants biaisés par la survie), D3 n'a pas de biais de survie : les titres sont les
constituants actuels, et l'historique individuel de chaque titre peut être partiel (géré par
`in_universe`). 503/503 titres téléchargés avec succès depuis Yahoo Finance.

## C-D3-gics-static — secteur GICS statique (2026-10-16)

Le secteur GICS utilisé dans `chars.parquet` est le secteur actuel (table Wikipedia), non une
classification point-in-time. Un titre ayant changé de secteur au cours de la période conserve
son secteur actuel sur toute la période. Les 11 secteurs GICS sont encodés en one-hot
(`c_gics_<sector>`).

## C-D3-provenance — provenance et reproductibilité (2026-10-16)

Les cours ajustés proviennent de Yahoo Finance via yfinance 1.7.0 (installé dans `.venv`, figé
dans `requirements.lock`). Les hashes SHA-256 des bruts Yahoo (`data/raw/d3_yf/`, gitignoré) sont
une provenance à date fixe : Yahoo révise l'historique ajusté, un re-téléchargement n'est pas
garanti bit-identique. L'ancrage reproductible est le panneau dérivé commité
(`data/derived/d3_239/`, `data/derived/d3_500/`) + hash de sortie dans le manifeste. Le test de
reconstruction depuis le cache (`test_reconstruction_from_cache`) vérifie que `ret_wide.npy` est
bit-identique à la reconstruction depuis les caches bruts. Le déterminisme bit-à-bit du parquet
repose sur pyarrow 26.0.0 épinglé + codec fixé (snappy par défaut) + pas de timestamp embarqué.
Tous les fichiers dérivés sont sous la limite de 50 Mo (plus grand : `d3_500/panel.parquet` à
45,97 Mo) : pas de compression zstd ni de sharding nécessaires, aucun écart C-D3-shard requis.

## C-D3-manifest-merge — préservation des entrées D3 dans le manifeste (2026-10-16)

`articleB.build()` (exécuté par le fixture de test de `test_data_d1_d2.py`) recrée le manifeste
et préserve désormais les entrées des autres builders (`datasets`, `results`, `sources` non
D1/D2) : sans ce mécanisme, le rebuild D1/D2 écrasait les entrées D3 (`d3_239`, `d3_500`,
`sources.d3`) ajoutées par `sp500._update_manifest`.

## C-R01-parse — lecture des CSV dérivés par R01 (2026-10-16)

R01 (`exp_R01_real_world_backtest.py` l.249) lit `data/derived_firstrate/R01_daily_<ETF>.csv` avec
le convertisseur flottant par défaut de pandas, alors que D1 (prompt 2) lit les mêmes fichiers avec
`float_precision='round_trip'`. Les deux lectures diffèrent sur 6258 des 6414 rendements SPY,
jusqu'à 7356 ulp, sous pandas 2.3.2 comme sous 3.0.6. Effet sur la réplication de R01 depuis le
chargeur D1 (`results/identity/articleB_R01_R08.csv`, entrée `d1_loader`, identique dans les deux
environnements) : `omega` ≤ 2.64e-14 et `sigma_unc` ≤ 1.32e-14 en relatif (4 cellules chacune),
`S_over_thr_Data` ≤ 1.97e-14 (220 cellules sur 253). Les sorties discrètes (α, β, Γ̂, q̂, alarmes
2020, délais, taux, IC, ADD, SEM) sont bit-identiques. Avec le lecteur de R01 (entrée diagnostique
`articleB_csv`, seule exception délibérée à `round_trip`), ces colonnes sont bit-identiques.

## C-R01-env — environnements de contrôle R01 (2026-10-16)

Les contrôles d'identité tournent dans `.venv` (numpy 2.4.4, scipy 1.17.1, pandas 3.0.6,
statsmodels 0.15.0) et dans `external/articleB-venv` (créé par `~/miniforge3/envs/Trading/bin/python
-m venv`, puis `pip install -r` des requirements de l'Article B : numpy 1.26.4, scipy 1.16.2,
pandas 2.3.2, statsmodels 0.14.5 ; PyYAML 6.0.3 ajouté pour importer le chargeur D1, sans rôle
numérique). Résultat identique dans les deux : 1401 cellules R01 et 32 cellules R08 conformes ;
SLSQP (`fit_garch_qmle`) bit-identique sous scipy 1.16.2 et 1.17.1. Seul écart d'environnement :
`lb_pvalue_warmup`, 4 cellules à 4.63e-15 en relatif. Cause établie : `acorr_ljungbox` appelle
`acf(fft=False)`, donc `np.correlate`, dont le résultat dépend de la BLAS liée à numpy ; les roues
PyPI (openblas64) donnent Q = 0x1.8a1ef17b13742p+4 pour SPY, la build conda-forge de
l'environnement `Trading` (versions de l'Article B) donne 0x1.8a1ef17b13749p+4 et reproduit le CSV
de l'Article B bit à bit (1401/1401 cellules `articleB_csv`, exécution diagnostique non écrite) ;
`chi2.sf` est identique partout. Les versions de paquets n'épinglent pas la build BLAS : le test
diagnostique exige la bit-identité de l'entrée `articleB_csv` hors `lb_pvalue_warmup`, colonne qui
reste soumise au seuil de 1e-12.

## C-garch-pyflakes — exclusion de `jepadrift/stats/garch.py` de pyflakes (2026-10-16)

`fit_garch_qmle` est porté sans modification (R01 l.84–100) et lie une exception inutilisée
(`except (TypeError, np.linalg.LinAlgError) as e`, R01 l.99), que pyflakes signale. Modifier la ligne
romprait l'identité octet par octet exigée par le prompt 04. La cible `check` du `Makefile` exclut
donc ce seul fichier de pyflakes ; `tests/test_identity_articleB.py::test_ported_sources_byte_identical`
fige son contenu sur la source de l'Article B.

## C-lattice-midpoint — seuil flottant des CUSUM calibrés sur le treillis (2026-10-16)

`select_threshold` (`jepadrift/monitors/lattice.py`) renvoie le point du treillis λ = L·u et le seuil
opérationnel `threshold` = (L + ½)·u (règle stricte) ou (L − ½)·u (règle large), à comparer en
flottant par `S > threshold`. L'Article B compare au point du treillis lui-même ; l'accumulation
flottante des pas +0.4/−0.6 y fait alors appliquer la règle large sur une partie des trajectoires
(écart B `R08-delivered-level-above-nominal`). Le seuil au milieu laisse une marge d'une demi-unité ;
l'équivalence avec la règle exacte est vérifiée trajectoire par trajectoire
(`test_midpoint_threshold_reproduces_lattice_rule`). Valeurs inchangées : à H = 5000 et 5 %, L = 57
(λ = 11.4, niveau exact 0.043428228893176074) ; le seuil flottant vaut 11.5.
