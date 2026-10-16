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
