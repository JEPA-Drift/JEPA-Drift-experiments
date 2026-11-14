# GO technique distinct — stream 23, R0 et RED synthétique initial

Date : 2026-11-14. Émetteur : Codex, dans le périmètre scientifique déjà autorisé par le chercheur pour E6
phase 1, après clôture et publication E4. Aucun nouveau GO scientifique n'est créé.

## Portes reçues

- GR0 : E4 clos et publié sur main/origin/main au commit `461f2b13894be2cca954676dc3aab10e0b640a2b`.
  Le hook a exécuté 37 + 1308 tests réussis, cinq skips D4 seulement, avec torch et PCA-G1 actifs.
  La finalisation sans certificat du plafond CPU est explicitement autorisée par le chercheur ; sa réserve
  reste consignée dans le GO E4 du 14 novembre. Aucun résultat scientifique E4 n'est modifié.
- GR1/C1 : ce worktree 23 est avancé sur ce commit. Les ports historiques `7e4c7a1`, puis `3d0bd20`, restent
  matérialisés sans commit. Le worktree historique reste à `3d0bd2071cb86afc6b196b5020ff729204746a93`.
- C2/GR2 : préfixe DEVIATIONS de main identique (1324 lignes), puis ajout exact des 66 lignes historiques.
  Les trois blobs D3 sont identiques entre b18d8e5 et main publié ; requirements.txt, requirements.lock et
  conda-torch.lock sont identiques. Aucun changement jepadrift/, Makefile ou conftest.py dans cette plage.
- Source historique avant RED : `experiments/e6_second_order.py`, SHA-256
  `072b7b0c03754b41c8a489359a46de26e3597f208c07f5dd2623e92dd098c750`.
- Fixtures reçues : `tests/test_e6.py`, SHA-256
  `39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc`.
- Plan v2 reçu : SHA-256 `29c6566abf3922ef923e5e69b7e4d282723c6414c82687d4c0f64914bcf7e48a` avant
  l'ajout documentaire de la présente décision. Sa version native reste inchangée, SHA-256
  `211d79077fc08f3b2338a38db3de8c28496a863b6605f25abe01b57f1250dc0b`.

## Signal GR3 borné

Dans la session interactive 23 conservée, sortie officielle du mode plan déjà reçue pour le lot statique,
Codex autorise maintenant **R0 et le premier RED synthétique uniquement**, après le signal de démarrage distinct.
L'implémentation P-IO attend l'observation et la réception de ce RED par Codex.

1. Refaire R0 versions et emplacements des six dépendances du plan avec la .venv du projet et sans shim torch.
   Les versions doivent égaler requirements.lock et les modules provenir du site-packages résolu de cette .venv.
   Le grep -vF des origines doit ne produire aucune ligne : son code 1 est attendu dans ce cas ; une erreur
   d'import ne doit pas être masquée. Un écart R0 impose STOP avant test ou lecture réelle.
2. Vérifier les deux SHA du source et des fixtures ci-dessus, puis lancer seulement les trois nodeids :

       .venv/bin/python -m pytest -q -p no:cacheprovider \
         tests/test_e6.py::test_bounded_reader_slices_no_return_row_after_last_day \
         tests/test_e6.py::test_bounded_reader_refuses_before_any_return_copy \
         tests/test_e6.py::test_bounded_cli_hashes_no_return_panel

   Attente statique : 14 échecs, code pytest 1, sur l'attribut DERIVED absent du source historique, avant
   création du panel synthétique ou appel du lecteur. Ce compte n'est pas encore un résultat observé.
   Pas de fichier de test entier, ni fixture d6 réelle, ni mutant, ni script expérimental à ce stade.
3. Arrêter après ce résultat, transmettre commandes, sorties, codes, temps CPU/RSS/durée et SHA des journaux.
   Aucune écriture de code, configuration, données ou artefacts scellés dans ce sous-lot.

## Ressources et limites

Créneau exclusif sous `logs/.jepa_execution.lock` du checkout principal. .venv uniquement ; OMP/MKL/OPENBLAS
à un thread, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Retirer PYTHONPATH pour ces probes et
pour python -m pytest depuis la racine ; aucun torch Trading ou shim NumPy. Mesurer chaque invocation sous
GNU time, timeout au plus 600 secondes pour ces probes, et enveloppe mémoire 8 Gio. Aucun calcul concurrent.
Les coûts 23 sont consignés séparément de ceux d'E4.

Interdictions inchangées : pas de rendement réel, de valeur 2020+, de J4/FROZEN, de phase 2, de JEPA/P5-D,
de nouveau paramètre ou graine. Pas de Git en écriture, hook, reindex ni modification partagée par Claude.
H-cal reste limité aux métadonnées de calendrier pour le futur lot réel, non exécuté ici. Le stream 16/J3
n'est pas une dépendance supplémentaire de cette phase 1. Les streams 27, 21 et 16 restent sans runtime.
