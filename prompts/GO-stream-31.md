# GO stream 31 — lot 2 QA uniquement

Date : 2026-11-06, 12:22 UTC. Décision Codex dans le mandat de supervision et de GO délégué par le chercheur ; aucune signature personnelle du chercheur n’est attribuée.

## Décision

**GO d’exécution du lot 2 de `prompts/plans/plan-31.md`, amendé au §9, puis STOP pour revue.** Base `20ad9e860a58373ec85405de6ee19a68322dd02e` : lot 1 intégré et poussé, hook terminé avec 37 + 545 tests passés et 5 ignorés. Le plan canonique est enregistré avant code ; l’addendum natif de 114 lignes est archivé avec SHA `e6765d9beeb0436f84e66b2fc2bb8a3be4b449aaa04ccda30be04f8584fcd128`.

QQA1, QQA2 et QQA3 : oui, avec les restrictions explicites du §9. P1–P5 sont retenues ; leur observation Git pendant la préparation du commit est historique, remplacée par la base effective ci-dessus.

## Périmètre et séquence

- Fichiers possédés : `tests/test_pca_drift_contracts.py`, `docs/audits/PCA_CONTRACTS_VALIDATION.md`, journaux ignorés `logs/pca_drift_contracts/`. Aucun autre fichier suivi. Ne pas réécrire plan/GO, audit 01–27 ou wrapup du lot 1.
- Vérifier les contrats de chaque groupe et les recouvrements existants. Les témoins négatifs vivent en mémoire ou en `tmp_path` ; aucune mutation d’un producteur ou d’un artefact scellé pour fabriquer RED. Tests de rejet réussis, FAIL produit et BLOCKED disponibilité restent distincts.
- C8 exclut seulement les champs de provenance/identifiants listés au §9 entre les deux fixtures ; les hashes scientifiques, seuils, S, dimensions, cohortes, configurations hors chemins factices et bibliothèque de stress restent contrôlés. Les liaisons de chaque artefact restent vérifiées. Aucun affaiblissement général sur les IDs.
- F-fake utilise le mode API `full`, avec les petits effectifs prévus et des rendements entièrement factices. Tous les chemins de panel sont explicitement confinés à `tmp_path`. C6 peut lire dates et métadonnées seules ; aucun rendement réel.
- Les comparaisons FULL lisent les sorties présentes vérifiées ; pas de `pdt.load_run(FULL)` sans trials. G1 lit directement `../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv` via `PCA_FULL2000_TRIALS`, sans copie ni lien : 48 317 020 octets, SHA `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c`. Absent : BLOCKED disponibilité seulement ; hash ou résultat divergent : FAIL.
- D7b est défini en dernier. Après les groupes, G1 et pyflakes, exécuter une seule mesure finale avec la variable G1 et `pytest -q -rA -x tests/test_pca_drift_contracts.py`, codes de sortie préservés par `pipefail`. Le texte « n = 40 » sur full 2000 doit produire un FAIL réel, non un xfail ni un skip.
- Au premier défaut producteur confirmé : **STOP immédiat**, rapport uniquement. Aucun rerun après STOP, aucun changement de test pour cacher le défaut, aucun `make check`, hook, reindex ou commit. Une erreur de fixture/référence QA exige diagnostic tracé, au plus trois corrections ; aucune tolérance ou formule scientifique changée pour faire passer les tests.

## Invariants

Session interactive courante, Opus 5.5, effort max, sortie du mode plan par le mécanisme officiel après lecture du GO ; aucun sous-agent. Le chercheur a temporairement levé le plafond global de deux sessions pour les voies documentaires 18 et 23 en parallèle. Chaque session garde son worktree et ses fichiers.

`.venv/bin/python` et `.venv/bin/make`, PATH du venv, OMP/MKL/OPENBLAS à 1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Aucune dépendance modifiée, Graphify/jCodeMunch, entraînement, nouvelle expérience PCA sans oracle, expérience réelle, JEPA/VAE/J4, full ou smoke de production, recalibration ou refit des artefacts scellés. J1 disque/index/47 CRLF restent au SHA `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; D8 reste FAIL +5,2833 %. Git et l’arbitrage après incident appartiennent à Codex et au chercheur.

## Reprise confirmée — 2026-11-06, 13:25 UTC

Le quota est annoncé réinitialisé par le chercheur pour cinq heures. **GO de reprise depuis le checkpoint**, selon le §10 du plan canonique, lu avant toute nouvelle édition : 26 tests F/E/A/B déjà réussis, puis C, D et G1. E3 non fini est une limite observée hors prérequis SPD fini, non un PASS de validation ; la finitude des champs d'information requis reste obligatoire. B4 accepte le refus documenté `UNEXPECTED_ROW_STATE` pour la famille incompatible et conserve le témoin E2 de lignée. Les CSV sont lus avec `float_precision='round_trip'`. Corriger seulement le minimum QA nécessaire à ces précisions, sans refaire les groupes inchangés. Aucun GO producteur ni levée du STOP scientifique ; D7b reste en dernier dans l'unique mesure finale.
