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
