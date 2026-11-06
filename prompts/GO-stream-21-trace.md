# GO stream 21-trace — contrôle des six correspondances E2

Date : 2026-11-06, 20:10 UTC. Décision Codex dans le mandat d'orchestration délégué par le chercheur.

**GO d'exécution de `prompts/plans/plan-21-trace.md`, selon sa Décision GO intégrée.** Base `3467df4b7426fa15c1ab16ef94687f25a976636d`, branche `stream-21-trace`, session interactive Claude Opus 5.5 déjà ouverte, effort **Max conservé jusqu'à clôture**, sans sous-agent. Proposition native relue : SHA-256 `ddf45a147204320993758763ece4ee516c5b041ede13ecb8422c689ae4f568ca`.

## Arbitrages

Q1 : G-T réduit ouvert par Codex ; Q2 : bloc Check inputs avec sept métadonnées, dont les six `Key columns` ; Q3 : preuves dans wrapup et journaux ; Q4 : aucune entrée DEVIATIONS ; Q5 : sentinelle des comptes, six couples et colonnes dans le test réel.

Chaque clé contient exactement les colonnes déclarées, puis sélectionne une ligne unique. Retirer une colonne même redondante échoue. Les anciens témoins restent des tests de rejet, avec le statut structurel précisé dans le plan. Refuser les littéraux décimaux hors précision supportée, ainsi que les autres cas négatifs du plan. Les six lignes Entries restent identiques ; tous les ajouts restent dans le périmètre déclaré.

## Propriété et clôture

Claude écrit uniquement :
- `tools/trace_numbers.py` ;
- `tests/test_trace_numbers.py` ;
- les ajouts nécessaires à `docs/MAPPING.md` ;
- `prompts/wrapups/wrapup-21-trace.md`, six sections anglaises après le wrap-up natif ;
- journaux ignorés.

Codex possède plan, GO, revue, réindexation et Git. Lire plan/GO, relever leurs SHA, suivre RED→GREEN et les contrôles ciblés, produire le wrapup, puis s'arrêter. Le contrôle complet `make check` obligatoire est réservé au hook de clôture Codex après réindexation ; aucun doublon par Claude.

Bibliothèque standard seule dans l'outil. Environnement partagé épinglé : `.venv/bin/python`, BLAS mono-thread, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. Aucun fichier du lot 19-oracle, aucune installation.

Aucun papier, producteur, résultat, donnée réelle, PCA, campagne E2/E3, gel/J4, JEPA/VAE, runner ou autre outil historique modifié/exécuté. READ_MATCH certifie uniquement littéral/cellule/arrondi du sous-ensemble, sans conclusion scientifique. J1 disque/index/47 CRLF reste `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; D8 reste FAIL +5,2833 %. Aucun commit, push ou réindexage par Claude. Au quota ou à l'erreur bloquante : conserver l'état et rapporter sans nouvelle instance ni réessai automatique.
