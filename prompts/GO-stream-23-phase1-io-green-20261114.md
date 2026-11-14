# GO technique distinct — P-IO et GREEN synthétique 23

Date : 2026-11-14. Autorité scientifique : GO E6 phase 1 existant du chercheur, sans extension.

## Réception de R0 et du RED

Codex a lu les sorties brutes et le journal `logs/23-phase1/r0-red-20261114/journal.log`, vérifié les empreintes
du manifeste SHA256SUMS et confirmé :

- R0 versions conformes à requirements.lock ; six origines dans le site-packages résolu de la .venv ;
- RED exécuté sur les trois seuls nodeids autorisés : 14 échecs, pytest code 1, en 2.21 s ;
- les quatorze erreurs sont AttributeError sur DERIVED, au premier monkeypatch, avant _fake_d3 ou lecteur ;
- pas de fixture d6 réelle ni de lecture de calendrier/rendement réel ; source et fixtures inchangés ;
- mémoire maximale des scopes : 8 Gio ; coût mesuré de ce lot 2.92 CPU_s, RSS maximal 166396 Kio.

Ce RED attendu est une preuve TDD, pas une reproduction scientifique échouée. Les portes GR0–GR3 demeurent reçues.

## Autorisation bornée

Dans la même session interactive 23, après le signal distinct Codex :

1. Appliquer uniquement P-IO à `experiments/e6_second_order.py`, conformément au plan et aux six clauses de
   sa décision intégrée : retrait de DATASETS, DERIVED local, lecteur memmap borné, gardes de nom/date/calendrier/
   bornes/forme avant toute copie de rendements, empreinte des seules lignes pré-2020 consommées et retrait
   du hachage du panneau complet dans main. Conserver dtype et ordre C, données, noyaux, paramètres et graines.
2. Relancer seulement les mêmes trois nodeids synthétiques. Attente : quatorze réussites, à rapporter comme
   résultats observés seulement après exécution. Les témoins négatifs restent actifs.
3. Exécuter pyflakes et les contrôles statiques de S3, relever le nouveau SHA source et le diff contre 3d0bd20.
   Le fichier de tests reçu conserve ses treize tests historiques et ses quatorze nouveaux cas ; ne pas le
   modifier sans signaler un défaut concret. Trois corrections d'ingénierie au maximum, avec preuves conservées.
4. Arrêter pour revue Codex du patch et du GREEN, avant toute fixture réelle, fichier de tests entier, mutant,
   reproduction quick/full ou nouveau résultat scientifique.

Les cinq fichiers de sorties C3 et la configuration restent strictement aux empreintes historiques. Aucun module
partagé, GO, plan, DEVIATIONS, MAPPING, registre, donnée, résultat ou figure n'est modifié par Claude dans ce lot.
Les journaux et manifestes ignorés sont autorisés ; les archives de tests portent une extension .py.source pour
éviter la collecte globale accidentelle de test_*.py sous logs.

## Ressources et suite

.venv sans shim torch/PYTHONPATH pour ces tests, environnement déterministe, verrou partagé, scopes 8 Gio,
timeout <=600 s et mesures GNU time pour chaque invocation. Coût séparé d'E4, aucune concurrence numérique.
Pas de J4, phase 2, JEPA/P5-D, donnée privée ou valeur 2020+. H-cal reste limité aux métadonnées du futur lot réel.
La réception du GREEN ne lance pas automatiquement la reproduction : Codex doit revoir le diff et donner le
signal du lot historique suivant, déjà compris dans l'autorisation scientifique bornée du chercheur.
