# Stream 28 — GO d'exécution ciblée Mistral Vibe

Date : 2026-10-30. Autorisation explicite du chercheur : lancer l'implémentation manquante dans le CLI Mistral Vibe, modèle `large-4`, thinking `high`.

## Portée autorisée

Exécuter le plan audité `prompts/plans/plan-28-closeout.md` sur le travail existant : correctif du lot mémoire flottant, homogénéité du schema_version /2, validations de frontière prévues, régressions TDD, documentation minimale et deux smoke closeout neufs. Le plan approuvé avant ce GO avait le SHA-256 `535cc4e0a8d56f86f89bd8b74441a31a1b370b0223c2d4df1ffc498bbf8e5d40` ; seule une référence à la présente décision lui est ajoutée.

Une seule session d'implémentation, dans le worktree `stream-28`. Le CLI local 3.0.4 expose le mode headless, --model et --prompt-file ; l'alias global `large-4` résout `mistral-large-4` chez Mistral avec `thinking = "high"`, vérifié sans modifier la configuration globale. Le lanceur revérifie ce couple avant l'appel.

Les restrictions antérieures d'attente d'un moteur sont levées pour cette reprise Vibe 28 uniquement. Claude Code reste limité aux plans, et son garde partagé reste actif. Les streams 29, 30, 31 restent fermés jusqu'à la clôture effective du 28.

## Limites

- Aucun redémarrage général, changement de détecteur, de KL, de règle prédictive ou de paramètres scientifiques.
- Aucune installation ou mise à jour de dépendances. Commandes scientifiques exclusivement dans le .venv du projet, variables déterministes fixées avant NumPy ; jamais Python Trading seul pour JEPA.
- N239/H250/n40, alpha=.05, deux fonds A/B30/C, scan exact, un processus/threads=1, 8 Gio et 30 min par invocation du runner.
- Préserver tous les artefacts précédents et les partitions. Utiliser les répertoires closeout neufs du plan ; aucun CSV/manifest corrigé à la main.
- Aucun full, aucune évaluation réelle post-2019, aucune donnée EUROFIDAI. E2 CRLF/SHA disque/index et le FAIL E3/D8 restent intacts.
- Éditions limitées au runner (exhaustive_cov et validate_config), YAML, tests et document de schéma. Rapport de fin dans logs et wrapup 28 ; ne pas réécrire les décisions GO ou les plans.
- Aucune délégation ou seconde session par Vibe. Pas de Graphify/jCodeMunch, de réindexation, de make check global, de git add/commit/push/merge/rebase/stash/reset/checkout : Codex conserve la revue et la clôture sérialisée, après extinction du processus.

## Rapport attendu

Modifications réellement appliquées, commandes et résultats RED/GREEN, tests ciblés, comparaison des sept fichiers et identités du double smoke, schéma /2 homogène, conservation des artefacts précédents, temps/CPU/RSS et SHA-256. Signaler un blocage honnêtement sans contourner une porte. Aucun gel du schéma ni intégration déclaré par l'implémenteur.

Prompt exact : `prompts/IMPLEMENT-stream-28-closeout-vibe.md`. Une session nouvelle utilise explicitement --model large-4 afin que l'override CLI soit effectif ; aucune reprise d'une ancienne session Vibe.
