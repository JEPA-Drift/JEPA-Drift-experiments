# GO — Stream 23 : correctif d'audit de `7e4c7a1` (E6 phase 1, correction éditoriale)

Date : 2026-10-23.
Destinataire : instance Claude Code du worktree `stream-23` (commit `7e4c7a1`).
Forme : transcription verbatim, par l'instance, des messages d'audit de l'orchestrateur, du prompt d'amorçage, des
reprises, de la revue du plan et du GO final. Une seule rédaction : le nom de compte du répertoire personnel est écrit
`<user>`. Le plan reste un fichier local (`~/.claude/plans/amor-age-stream-proud-plum.md`, révision 2) et n'est pas
commité, comme l'exige la revue du plan.

## Messages d'audit (verbatim, 2026-10-22)

> Mission de correction scientifique limitée, après audit du commit 7e4c7a1. Reste en mode plan et propose le plus petit correctif cohérent, sans aucun changement avant GO. Deux formulations à corriger dans le stream 23 : (1) « every window start is an onset » doit préciser que c'est un onset contrefactuel équivalent, car la matrice F4 fixe appliquée une fois à a puis chaque fenêtre avec CUSUM remis à zéro donne les mêmes observations qu'une injection propre à s; (2) « a block bootstrap or a deff needs blocks of length >= H and at least 10 of them » n'est pas une nécessité statistique universelle. Présente 10 blocs comme règle conservatrice préspécifiée du protocole pour refuser un IC D6, sans prétendre qu'un deff exige en général cette règle. Traite les occurrences dans script, CSV ci_reason, docs/DEVIATIONS.md et wrapup; conserve les plans/GO historiques. Si CSV change, régénère avec save_fair_csv et actualise SHA dans wrapup et éventuelles traces; vérifie les résultats numériques identiques, les tests sous .venv avec variables BLAS et make check. Nouveau commit local conventionnel, arrêt avant fetch, push et merge. Plan et questions d'abord.

> Continue the narrow E6 phase-1 audit correction in plan mode. The implementation commit 7e4c7a1 remains intact. Prepare a minimal plan to clarify that the F4 transformation at calibration start is equivalent to a counterfactual onset at each window because the clean calibration matrix is fixed and the transform is pointwise; clarify that requiring at least ten independent blocks is our conservative prespecified reporting criterion, not a universal prerequisite for bootstrap or design effect. Propagate the labels consistently through code-generated ci_reason, docs, and wrapup, regenerate CSV through save_fair_csv and update hash, verify numerical values unchanged, run .venv checks, then make one local Conventional Commit. Do not implement until I explicitly approve this plan. Stop before fetch, push, or merge.

## Prompt d'amorçage et reprises (verbatim, 2026-10-23)

Le prompt d'amorçage est `prompts/amorcage-23.md`, tel que commité sur `main` à `c10b68a`.

> # Amorçage — stream 23, correction éditoriale E6 phase 1
>
> Travaille dans le worktree `stream-23` au-dessus du commit E6 `7e4c7a1`. Lis `CLAUDE.md`,
> `prompts/streams/prompt-23-e6.md` et le plan correctif
> `~/.claude/plans/pasted-content-id-1e06-mission-de-rippling-feigenbaum.md`.
> GO accordé pour la correction éditoriale : préciser que la calibration F4 propre est
> équivalente pour chaque onset contrefactuel de chaque fenêtre ; présenter la règle des dix
> blocs comme critère de reporting préspécifié, sans l'attribuer comme nécessité universelle
> à Künsch ou Lahiri. Ne change ni nombres, ni figures, ni conclusions causales.
> Avant de quitter le mode plan, exécute `/mcp reconnect all` et vérifie `graphify` et
> `jcodemunch` dans `/mcp`. Implémente dans `.venv`, vérifie le diff et les contrôles pertinents,
> puis arrête-toi au commit local, sans fetch, fusion ou push. Rédige les nouveaux audits en anglais.

> Stream 23 : reprends en mode plan. Lis le prompt actuel /home/<user>/JEPA-Drift-experiments/prompts/amorcage-23.md. GO accordé uniquement à la correction éditoriale E6 : F4 clean calibration équivalent pour chaque contrefactuel onset/fenêtre ; règle des dix blocs = critère de reporting préspécifié, pas nécessité universelle de Künsch/Lahiri. Présente le plan de diff court, puis quitte plan après contrôle MCP graphify/jcodemunch et implémente seulement cette correction. Opus 5.5 Max, .venv. Pas de modification des données ni des calculs.

> Reprends le plan 23 interrompu par le redémarrage sans refaire les vérifications. Le GO porte uniquement sur la correction éditoriale E6 déjà décrite. Présente le diff prévu, puis demande la sortie du mode plan. Graphify et jcodemunch sont reconnectés.

## Revue du plan : correction requise avant GO (verbatim, 2026-10-23)

> Plan 23 : correction requise avant GO. L'étape 0 copie ce plan dans prompts/plans/plan-23-audit.md, alors que son contrôle final exige zéro occurrence littérale de /home/<user> dans git diff --staged ; la ligne du contrôle contient elle-même cette chaîne, donc le plan échoue mécaniquement. Solution minimale : retire la copie du plan du commit et ajuste la liste des fichiers indexés ; conserve le contrôle contre les vrais chemins absolus dans les artefacts à livrer. Préserve strictement les deux corrections éditoriales E6, sans données ni calculs modifiés. Réécris le plan et repropose la sortie du mode plan.

## GO final (verbatim, 2026-10-23)

> GO final pour la révision 2 du plan 23 : correction éditoriale E6 seulement, avec arrêts prévus si chiffres, figures ou autres champs changent. Je viens d'exécuter /mcp reconnect all et de vérifier graphify et jcodemunch connectés. Lance maintenant ExitPlanMode et implémente en mode auto conformément au plan.

L'orchestrateur a lancé `/mcp reconnect all` avant chacun des trois derniers messages. graphify et jcodemunch ont
répondu aux appels directs de l'instance, et l'orchestrateur les a confirmés connectés avant le GO final. La révision 2
du plan, avec sa section « Décision GO intégrée », a ensuite été approuvée par l'écran d'approbation, le 2026-10-23.
