# Stream 31 — GO d’outillage, lot 1 uniquement

Date : 2026-11-06, 09:42 UTC. Décision de Codex dans le mandat de supervision/GO explicitement délégué par le chercheur. Ce texte n’est pas une signature personnelle du chercheur.

## Décision et référence

**GO pour implémenter le seul lot 1 du plan `prompts/plans/plan-31.md`, puis arrêt pour revue Codex.** Aucun GO QA, producteur, figure, expérience, commit ou push n’est délivré à Claude.

Base vérifiée : `a0c576e13e8e647dfd61350eec52058ffc794dbf`. Plan natif v2 : 527 lignes, SHA-256 `a82a231d458a27e3b4affe6e8dae56a71588d3cedfea8c8b110006b1317972f7`, archivé octet pour octet dans `logs/orchestration_reprise_20261106/plan-v2.md`. Le plan canonique est enregistré avant code, avec « Décision GO intégrée ». La revue v1 et les réponses Q1–Q12 sont conservées dans `prompts/NO-GO-stream-31.md`.

## Propriété et modifications autorisées

- `tools/check_prompts.py` : découverte des deux familles de fichiers, validation des titres/IDs, contrôle non vacu, correction d’idempotence et I/O préservant les octets.
- `tests/test_check_prompts.py` : régressions T1–T7 et témoins négatifs, deux tests existants conservés.
- `prompts/Prompts_Claude_Code_v5.md` : migration par le programme existant corrigé, exclusivement en ajout pur de quatre blocs PCA, sans changement des 29 blocs historiques.
- `prompts/wrapups/wrapup-31.md` : état anglais du seul lot 1, six rubriques du projet, commandes/résultats/durées et SHA-256 réels.
- Journaux ignorés sous `logs/prompts_tooling/`.

Le plan canonique, ce GO, le NO-GO et l’audit 01–27 appartiennent à Codex et sont déjà présents. Ne pas les réécrire. Aucun autre fichier suivi n’est modifié. `PLAN.md`, les traces de quota et les fichiers étrangers sont préservés.

## Contrats et réponses à la revue

1. Ensemble CLI exactement égal à `{1,…,28,8b,28-PCA,29,30,31}` : 33 IDs. L’ancien Electricity garde `28`, le runner PCA garde `28-PCA`. Les fichiers d’amorçage et de réorientation restent hors découverte.
2. Titres manquants, IDs dupliqués ou inattendus, fichiers attendus absents/modifiés, master tronqué ou incomplet : refus explicite, code 1, aucun faux 100 %. Le contrôle teste l’égalité du bloc et la présence exacte du texte source, sans normalisation des fins de ligne.
3. `blocks()` s’arrête à la prochaine ouverture de fence lorsqu’un bloc final non clôturé la précède. Les fences historiques imbriquées et les deux tests existants restent compatibles. `sync()` conserve sa sémantique générale ; aucune interdiction permanente de synchroniser un ancien bloc n’est ajoutée.
4. Toutes les validations du résultat sont faites avant écriture. La migration actuelle exige précontrôle des 29 blocs, master initial préfixe exact du résultat, mêmes blocs historiques et second sync inchangé.
5. `main()` transmet explicitement le chemin courant de découverte, pour que les tests avec monkeypatch restent confinés à leurs répertoires temporaires.
6. RED réellement exécuté avant le correctif de l’outil ; GREEN et tests de rejet ensuite. Ne pas modifier les producteurs pour fabriquer un RED. Une erreur de test/fixture est distinguée d’un défaut d’outil ; au plus trois corrections diagnostiquées avant arrêt déclaré.
7. Les comptes attendus du plan ne sont pas des cibles à imposer : rapporter les résultats effectifs. Aucune dépendance ni configuration numérique changée.

QR1 à QR4 sont retenus avec les précisions ci-dessus. QR5 et QR6 ne donnent aucun GO au lot 2 ; le plan canonique en fixe la portée future. Le défaut d’étiquette « n = 40 » du full reste observé et non corrigé.

## Séquence autorisée

1. Vérifier HEAD, les chemins possédés et l’état Git ; lire les fichiers avant édition. Utiliser la session interactive courante, même modèle Opus 5.5 et effort max, quitter proprement le mode plan après lecture du présent GO. Aucun sous-agent ni deuxième session dans ce worktree.
2. Écrire les régressions, exécuter RED et conserver le code de sortie ; modifier l’outil au minimum puis exécuter GREEN et pyflakes.
3. Exécuter le contrôle avant migration : code 1 et quatre PCA absents du master. Capturer cet échec attendu sans le masquer ni interrompre la vérification du code.
4. Faire la migration contrôlée, vérifier l’ajout pur, les IDs, l’absence de changement historique et l’idempotence ; `make prompts-check` doit effectivement découvrir et contrôler les 33 fichiers.
5. Exécuter `make check` sous le venv et les variables déterministes du projet. Préserver les codes de sortie avec `pipefail`. Produire le wrapup et le compte rendu anglais avec les résultats réellement obtenus.
6. **Arrêt** pour revue, reindex, contrôles de clôture, staging explicite et commit par Codex. Aucun fichier `tests/test_pca_drift_contracts.py` avant le GO QA distinct.

Toutes les commandes du dépôt utilisent `.venv/bin/python`, `.venv/bin/make` et PATH du venv ; OMP/MKL/OPENBLAS à 1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Aucun entraînement, expérience réelle, accès expérimental 2020+, full/smoke de production, refit, recalibration, correction des figures ou utilisation de Graphify/jCodeMunch par Claude.

J1 disque et index conservent `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` et les CRLF natifs. D8 reste FAIL. Aucun fichier propriétaire, `trials.csv` ou fichier >50 Mo ne sera proposé au suivi. Claude ne fait aucune mutation Git ni intervention dans un worktree voisin.
