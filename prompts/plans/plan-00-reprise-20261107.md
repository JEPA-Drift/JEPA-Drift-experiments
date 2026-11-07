# Plan 00-reprise-20261107 — passation après clôture des lots 21

Date : 2026-11-07. Base publiée : `9ec3a7bd4406733d5da1d9b9337be63658b7e178`. Branche : `stream-00-reprise-20261107`.

## Périmètre et préalables constatés

L'ordre utilisateur demande la persistance sans root, la clôture des deux sessions terminées, puis une passation complète après audit et arbre propre. Le cron utilisateur fonctionne ; les lots DPI et annexe sont audités, commités, intégrés et poussés. Leurs sessions sont fermées. Le drapeau traité est archivé sous verrou, sans alerte restante.

Le worktree propre de l'ancien lot 00-monitor a été avancé par fast-forward jusqu'à la base publiée, puis une branche documentaire propre a été créée. Les deux prompts utilisateur non suivis du dépôt principal restent intacts ; aucun nettoyage n'est autorisé.

## Hypothèses et choix par défaut

1. La demande est documentaire et opérationnelle : Codex rédige la passation directement, sans ouvrir une nouvelle instance Claude ni écrire de code scientifique.
2. Les SHA intégrés et les périmètres audités priment sur les statuts historiques des prompts, de l'INDEX et des wrapups précommit. Une clôture partielle n'est jamais la clôture d'un stream entier.
3. Aucun prochain stream ne reçoit un GO d'implémentation par cette passation. Les propositions 21 et 19 commencent par une replanification ; les exclusions scientifiques et les dépendances restent applicables.

## Exécution bornée

1. Créer `prompts/streams/00_CODEX_AMORCAGE_REPRISE_2026_11_07.md` : état Git et worktrees préservés, inventaire 01–27 avec 08b/11b, distinction des deux 28, clôture de 31, lots 21, dépendances et ordre conditionnel.
2. Y inscrire le protocole interactif Claude : `/plan`, revue, GO explicite avant code, Opus 5.5 Max pour les tâches complexes, effort inchangé pendant l'implémentation, plafond strict de deux instances et exclusion des appels concurrents aux modules partagés.
3. Décrire le cron 30 minutes réellement installé, ses preuves d'exécution, le verrou, les journaux et le drapeau ; distinguer l'inspection déterministe d'un réveil cognitif de Codex.
4. Vérifier les références et l'absence de régression documentaire : `make prompts-check`, J1 disque/index CRLF/SHA, diff et quatre chemins possédés. Aucun nouveau test pour ces documents.
5. Enregistrer le wrapup anglais à six rubriques, réindexer en mode AST, puis laisser le hook obligatoire exécuter `make check` pour l'unique commit documentaire. Auditer la plage, intégrer par fast-forward et pousser `origin main` sous l'identité anonyme existante.

## Décision GO intégrée

**GO documentaire Codex dans le mandat explicite de l'utilisateur**, enregistré avant la rédaction. Le GO correspondant est `prompts/GO-stream-00-reprise-20261107.md`. Les quatre seuls livrables sont ce plan, ce GO, le nouvel amorçage et son wrapup. Aucun changement d'INDEX, master, mémoire canonique, code, configuration, CSV, figure ou dépendance ; aucune nouvelle expérience, J4 ou session Claude. Si une référence manque, constater la lacune plutôt que fabriquer un résultat ou un GO scientifique.
