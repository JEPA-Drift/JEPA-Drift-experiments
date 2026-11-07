# GO stream 21-rest — Lot P direct de traçabilité analytique

Date : 7 novembre 2026. Autorité : arbitrages et ordre d'exécution explicites du chercheur dans la session Codex d'orchestration. Codex enregistre la décision sans inventer de signature personnelle.

**GO ACCORDÉ POUR LE LOT P**, selon `prompts/plans/plan-21-rest.md`, décision intégrée avant exécution. Base `1440927b49463c13bdd0c819fcd73f30d6a32c31`, branche `stream-21-rest`, session `jepa-s21-rest`, Claude Opus 5.5 effort Max, contexte conservé. Aucun Agent/Task ni délégation imbriquée.

## Arbitrages

- Lot P direct ; Lot A écarté, aucun fichier `test_sec3_values.py` intermédiaire.
- Les neuf occurrences analytiques/dérivées rejoignent une source CSV uniquement après calcul, empreinte et `READ_MATCH` effectifs. Objectif : 15/19, sans annoncer la couverture avant vérification.
- Les quatre bornes `13`, `16`, `8`, `11` de la l. 111 restent `UNSOURCED` (Lot S). Aucun ajustement du papier ou des paramètres pour retrouver ces valeurs.
- Lot F non exécuté par ce GO : toute réalisation ultérieure restera confinée aux fixtures. Lot R différé. Aucune création de `configs/FROZEN.json`, aucun changement du Makefile. Le calendrier J4 n'ouvre aucune porte.

## Fichiers de Claude

1. `experiments/sec3_analytic_values.py` : nouveau producteur analytique, CLI `main(argv)` ; `--out` refuse explicitement tout fichier déjà présent, sans le modifier. Imports du projet limités à `jepadrift.floors` et `jepadrift.pipelines.save_fair_csv` ; utilitaires standard et pandas déjà épinglé pour le DataFrame de sérialisation, sans nouvelle dépendance ni import de bras E2. Aucun PRNG.
2. `results/sec3/sec3_analytic.csv` : sortie neuve via `save_fair_csv`, une ligne et une clé explicite par grandeur ; SHA-256 relevé. Le rapport ARL0/ADD utilise la lecture analytique avec approximation de diffusion, jamais l'intitulé d'ADD exact à pas fini.
3. `tools/trace_numbers.py` : sources CSV multiples, clés propres à chaque source, décimales quantifiées à l'exposant du littéral en `ROUND_HALF_EVEN`, identifiants d'occurrence et ancres de grandeur.
4. `tests/test_trace_numbers.py` : TDD du producteur et de l'extension, conservation des refus existants et des six correspondances J1. L'ancien format mono-source reste pris en charge. Aucun test de simple présence de code à la place d'un comportement réel.
5. `docs/MAPPING.md` : nouvelles sources et empreintes, neuf entrées supplémentaires après vérification ; les six sources J1 gardent leur sémantique, les bornes restent non couvertes.
6. `prompts/wrapups/wrapup-21-rest.md`, anglais à six sections, après invocation du wrap-up dans le créneau de clôture attribué par Codex ; journaux ignorés `logs/stream_21_rest/`.

Codex possède plan, GO, revue, coordination, réindexation, vérification complète et Git. Aucun autre chemin n'est modifié sans nouvelle justification et revue de périmètre.

## TDD et réception

- Lire chaque fichier avant édition et rechercher les consommateurs du checker. RED observable sur le comportement manquant, puis GREEN et simplification minimale. Conserver les journaux des commandes, sorties et codes retour ; une erreur de syntaxe n'est pas un RED de fonctionnalité.
- Témoins : nouvelle source/décimales ; arrondi à mi-chemin ; source/clé ambiguë ou absente ; SHA périmé ; NA/non-fini ; chemin refusé ; fichier de sortie préexistant intact ; exécutions déterministes dans deux fichiers neufs.
- Les deux `2.01` ne se distinguent pas par leur valeur : lier ID, localisation, formule/paramètres et ancre disjointe (`$M=` versus `\tau_a/\tau_\gamma=`). Un échange de leurs références doit être rejeté même si l'accord numérique persiste.
- Les tests utiles du Lot A sur ces identités sont repris dans le Lot P, sans construire le lot intermédiaire.
- Aucun producteur E2/E3 ni benchmark PCA n'est relancé. Au moindre écart de reproduction scientifique scellée : arrêt et constat, jamais modification destinée à obtenir PASS. Infrastructure/syntaxe : trois corrections bornées maximum.

## Exclusion des exécutions et clôtures

Le registre opérationnel ignoré de Codex est `logs/orchestration_20261107/execution-19-21-state.json` dans l'arbre principal. Avant chaque import/exécution du projet, vérifier que `science_owner` vaut `stream-21-rest` et `closeout_owner` est nul, puis lancer la commande sous le verrou commun indiqué dans ce registre, par `flock -n`. Si le créneau n'est pas disponible, signaler l'attente et poursuivre seulement la lecture/édition ; aucune boucle de retry ou attente bloquante.

Tout Python applicatif utilise `.venv/bin/python` et l'environnement épinglé : BLAS mono-thread, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`, pont torch existant. Aucun remplacement de dépendance.

Lorsque le Lot P et ses tests ciblés sont prêts, émettre `REVIEW_READY stream-21-rest — awaiting Codex review`, puis attendre le créneau de clôture avant le wrap-up. Codex sérialise wrapup → réindexation AST/sans résumé IA → `make check` → commit → fetch/rebase → contrôle de plage → push nommé vers main. Claude ne lance pas cette séquence ni Git. La confirmation au moment du push reste requise par l'ordre utilisateur.

## Invariants

J1 disque/index : `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF, zéro LF isolé. E3 SHA `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`, D8 reste FAIL +5,2833 %. Aucun changement de `floors`, `pipelines`, des treize sources d'identité PCA, des résultats scellés, du papier ou de la mémoire. Aucun accès aux rendements réels, aux données 2020+, aucun entraînement JEPA/VAE. Au quota : conserver modèle, effort, contexte et session.

## Lot S — clarification réservée à Codex et au chercheur

La demande à préparer porte sur : définition exacte de CV²(I_t) et de τ_int, estimateur et fenêtre, unités, valeurs de SR/γ/mode, identification des lignes et colonnes derrière les deux plages, producteur et version des sources. Aucun message externe n'est envoyé par Claude. Toute source reçue sera traitée dans un lot distinct ; aucune simulation implicite.
