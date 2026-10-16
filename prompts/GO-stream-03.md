# GO — Stream 03 (D3 S&P 500) : réponse à la question ouverte du plan

Date : 2026-10-16.
Destinataire : instance en charge de l'implémentation du stream 03 (`prompts/streams/prompt-03-data-d3.md`).
Plan concerné : `prompts/plans/plan-03-temp.md` (plan temporaire, renommé par le chercheur) → plan final à
consigner dans `prompts/plans/plan-03.md`.

## Instruction préalable — à exécuter AVANT l'implémentation

Avant de lancer l'implémentation du plan (étapes 0 à 10), consigner le **plan final mis à jour** dans
`prompts/plans/plan-03.md`. Ce fichier reprend le plan temporaire `prompts/plans/plan-03-temp.md` (ne pas
modifier ce dernier) en y intégrant les réponses à la question ouverte ci-dessous et en corrigeant les
options non retenues (notamment « séparer en deux commits », sans effet sur la règle des 50 Mo par fichier).
**Ne commencer aucune étape d'implémentation avant que `prompts/plans/plan-03.md` soit écrit.**

## Question ouverte (plan-03, « Questions ouvertes pour le chercheur »)

> Taille du panel d3_500 vs limite 50 MB : le panel ~500 titres × ~6400 jours en parquet fera probablement
> 60-100 MB. Le dépasserait la limite de push. Faut-il (a) compresser en zstd, (b) ne commiter que d3_239
> et garder d3_500 local, ou (c) autre ?

## Réponse

**GO — option (c) « autre » : commiter les deux panneaux dérivés `d3_239` et `d3_500`, et gérer la limite
des 50 Mo par fichier techniquement.**

1. **Livrables data commités.** Les panneaux dérivés `data/derived/d3_239/` et `data/derived/d3_500/` sont
   commités (données publiques Yahoo Finance / Wikipedia). Les bruts `data/raw/d3_yf/` restent gitignorés
   et ne sont jamais commités. L'option (b) « ne commiter que d3_239 » est rejetée : `d3_500` est un
   livrable du prompt 03 et la coupe transversale principale (audit, E1, J2/J3).
2. **Gestion de la limite 50 Mo par fichier** (règle `AGENTS.md` : aucun fichier > 50 Mo dans le range
   pushé ; GitHub bloque en dur à 100 Mo par fichier) :
   - (1) Builder d'abord, mesurer les tailles réelles.
   - (2) Si un fichier dépasse 50 Mo : le réécrire en parquet `compression='zstd'` avec dictionary
     encoding (pyarrow 26.0.0, épinglé dans `requirements.lock`). Estimation calibrée sur D2
     (4 381 532 octets / 499 938 lignes = 8,76 octets/ligne en snappy) : `d3_500/panel.parquet`
     ~3,2 M lignes → ~30 Mo, passe ; `d3_239/panel.parquet` ~1,5 M lignes → ~14 Mo, passe.
   - (3) `d3_500/chars.parquet` (3,2 M lignes × 17 colonnes : 4 flottants + 11 one-hot GICS) est le
     seul fichier à risque. Si zstd ne suffit pas : sharder par année (`chars_YYYY.parquet`, chargeur
     adapté) et consigner l'écart `C-D3-shard` dans `docs/DEVIATIONS.md`.
   - Ne **pas** découper en plusieurs commits : la règle est par fichier, un blob > 50 Mo le reste quel
     que soit le commit.
   - Ne pas utiliser Git LFS (incompatible avec une diffusion publique anonymisée type 4open.science).
3. **Script + manifeste SHA-256 = chemin d'audit, pas un substitut aux données.** Le script de
   téléchargement, le manifeste (SHA-256 des entrées brutes et des sorties dérivées) et le test de
   reconstruction bit-à-bit depuis le cache restent obligatoires : c'est le moyen de vérifier la
   conformité avec les propres téléchargements du chercheur. Ils ne remplacent pas les panneaux
   commités, qui sont l'ancrage reproductible de tous les résultats aval (les streams 4–7 et E1/E3
   chargent D3 via `sp500.py` ; un re-téléchargement Yahoo n'est pas garanti bit-identique, Yahoo
   révisant l'historique ajusté).
4. **Écarts à consigner dans `docs/DEVIATIONS.md`** : `C-D3-shard` (si sharding de `chars.parquet`) ;
   consigner que les hashes des bruts Yahoo sont une provenance à date fixe et que l'ancrage
   reproductible est le panneau dérivé commité + hash de sortie. Le déterminisme bit-à-bit du parquet
   repose sur pyarrow épinglé + codec fixé + pas de timestamp embarqué (couvert par le test de
   reconstruction depuis le cache).
5. **Avant le push** (protocole de fin de stream inchangé) : vérifier le range (aucun chemin sous
   `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo), `make check`,
   wrapup `prompts/wrapups/wrapup-03.md`, `tools/reindex_graphify_jcodemunch.sh`, commit, push.

## Justification (pour mémoire)

- Les données D3 sont publiques : aucune restriction de type EUROFIDAI (les gardes sont scopées par
  chemin à `data/raw/eurofidai/` et `data/derived/d4_eurofidai/`).
- Précédent D1/D2 : panneaux dérivés publics commités, bruts gitignorés, manifeste hashé.
- Sans panneau commité, chaque instance aval refait un téléchargement de 1–1,5 h (rate-limiting) avec
  un risque de données révisées → résultats non reproductibles d'une instance à l'autre.
