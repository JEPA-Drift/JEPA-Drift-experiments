# GO stream 19-oracle — référence analytique gaussienne connue

Date : 2026-11-06, 20:10 UTC. Décision Codex dans le mandat d'orchestration délégué par le chercheur.

**GO d'exécution du seul lot `prompts/plans/plan-19-oracle.md`, selon sa Décision GO intégrée (§12).** Base `3467df4b7426fa15c1ab16ef94687f25a976636d`, branche `stream-19-oracle`, session interactive Claude Opus 5.5 déjà ouverte, effort **Max conservé jusqu'à clôture**, sans sous-agent. Proposition native relue : SHA-256 `fc966d66395b13481fe5708caba2f9797072a166ec4dcb455ae27398516593b6`.

## Arbitrages

Q1 : sorties temporaires seulement ; Q2 : 16 lignes de la grille proposée ; Q3 : plafond `inf` uniquement pour ρ = 0 ; Q4 : contrôles ciblés Claude, `make check` complet obligatoire au commit par Codex ; Q5 : noms des fichiers Codex confirmés dans le plan.

Le helper gelé renvoie 2 I. Son résultat est divisé par deux. La référence δ²/2 et toutes les sorties finies sont contrôlées ; les valeurs sous-représentables, débordements et inverse de ρ positif non représentable sont rejetés explicitement. Témoins supplémentaires et distinction entre domaine mathématique et float64 au §12.

## Propriété et clôture

Claude écrit uniquement :
- `experiments/e4_oracle_reference.py` ;
- `tests/test_e4_oracle_reference.py` ;
- `docs/sections/e4_oracle_reference.md` ;
- `prompts/wrapups/wrapup-19-oracle.md`, six sections anglaises après le wrap-up natif ;
- journaux et CSV temporaires ignorés.

Codex possède plan, GO, revue, réindexation et Git. Lire plan et GO, relever leurs SHA, suivre RED→GREEN et la réception, produire le wrapup, puis s'arrêter pour revue. Aucune modification de ces deux fichiers Codex ni d'un fichier du lot 21-trace.

Environnement partagé épinglé : `.venv/bin/python`, BLAS mono-thread, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`. Aucune installation.

Aucun résultat suivi, donnée réelle, campagne E4/D6, PCA estimée, SPLL, JEPA/VAE/J4, changement de producteur ou d'artefact scellé. Aucun nouveau délai ou test FPR/ARL0. J1 disque/index/47 CRLF reste `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; D8 reste FAIL +5,2833 %. Aucun commit, push ou réindexage par Claude. Au quota ou à l'erreur bloquante : conserver l'état et rapporter sans nouvelle instance ni réessai automatique.
