# GO — Stream 17 : composant C partagé, IPCA et pipelines P4-C/P4-D

Date : 2026-10-23.
Destinataire : instance Claude Code du worktree `stream-17` (base `c284823`).
Forme : transcription verbatim, par l'instance, des messages de l'orchestrateur. Le GO, accordé dans l'amorçage et
confirmé en session, a été suivi d'un GO technique avec corrections, puis d'un GO final pour la révision 3 du plan.
Le plan approuvé est `prompts/plans/plan-17.md` (révision 3, « Décision GO intégrée »). Le plan antérieur
(révision 1, questions Q1–Q10) est resté dans le mode plan d'une session précédente. Les chemins absolus du
répertoire personnel sont transcrits `~`.

## Amorçage (verbatim, `prompts/amorcage-17.md`)

> # Amorçage — stream 17, IPCA
>
> Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
> `prompts/streams/INDEX.md` et `prompts/streams/prompt-17-ipca.md` dans le worktree `stream-17`.
> Lis aussi `prompts/handoff-14-to-17.md` et les §2.7–2.8, §3 du plan 14 qui y sont cités.
> Reste en mode `plan`. Prévois les quatre caractéristiques continues causales en principal,
> GICS statique seulement en sensibilité rétrospective ; vérifie les panneaux déséquilibrés,
> l'identifiabilité, la sélection K sur calib et le contrat d'imparité. Avant le GO, borne K par 4
> et par le rang journalier de CΓ, définis le R² sur actifs tenus à
> l'écart et préserve le masque des rendements absents. Prévois l'extraction avec C et segments
> `pretrain`/`calib` distincts. Indique les fichiers partagés avec 14/18, les tests et les questions ;
> le GO est accordé avec Q1 (retirer le lien D4 local et exposer les sept fichiers dérivés
> par des liens individuels sans modifier le manifeste), Q2 (utiliser `c_beta_252` tel quel,
> chiffrer et consigner son dénominateur fautif, réserver la correction des données à un autre
> stream), Q7 du transfert partagé et les défauts Q3–Q10 du plan. Enregistre
> `prompts/plans/plan-17.md` avec « Décision GO intégrée » ; exécute `/mcp reconnect all`,
> vérifie `graphify` et `jcodemunch` dans `/mcp`, puis implémente. Utilise `.venv`,
> rédige les nouveaux audits en anglais et arrête-toi
> au commit local vérifié avant fetch, fusion ou push.

## Commandes locales de l'orchestrateur (sorties reproduites)

- `/mcp reconnect all` : « Reconnected 2 of 3 MCP servers (1 still not connected — run /mcp to check) » ; puis
  `/mcp` : « MCP dialog dismissed ».

## Message de reprise (verbatim)

> Stream 17 : reprends le plan selon ~/JEPA-Drift-experiments/prompts/amorcage-17.md et handoff-14-to-17.md. Les
> arbitrages Q1-Q10 sont accordés. Produis d'abord le composant C partagé extract.py et ses tests, puis IPCA.
> Présente le plan révisé avant sortie du mode plan ; l'implémentation a GO sous réserve du contrôle du plan. MCP
> graphify et jcodemunch viennent d'être reconnectés. Utilise uniquement Opus 5.5 Max et .venv.

## Message après redémarrage de la session (verbatim)

Précédé de deux `/mcp reconnect all` : « Reconnected 2 of 3 MCP servers (1 still not connected — run /mcp to
check) », puis « Reconnected 0 of 1 MCP server (1 still not connected — run /mcp to check) ».

> Reprends le plan 17 interrompu par le redémarrage à partir des sondes déjà faites. Applique les arbitrages Q1-Q10
> et le handoff 14→17. Écris le plan révisé, puis présente-le pour mon contrôle avant de quitter le mode plan.

## GO technique (verbatim), après le refus de la première sortie du mode plan (révision 2)

> GO technique du Stream 17 après correction du plan. §6.0 : `git status --porcelain` ne peut être vide après
> création de `prompts/plans/plan-17.md` et `prompts/GO-stream-17.md` ; accepte seulement ces changements attendus
> puis exige arbre vide après commit. §8 : `sha256sum` seul affiche les hash ; ajoute `cmp` ou assertion qui échoue
> si les paires D2/PCA divergent. Étiquette le R² cash-neutral comme R² de rendements relatifs (facteurs f_A
> toujours estimés sur A). `CLAUDE.md` l.148-149 impose plan et revue GO en français, nouveaux audits en anglais ;
> corrige la mention GO anglais. Fixe `MPLBACKEND=Agg` pour les vérifications. Réécris et repropose le plan ; reste
> en mode plan jusqu'à mon GO final.

## GO final (verbatim), après le refus de la deuxième sortie du mode plan (révision 3)

Précédé de `/mcp reconnect all` : « Reconnected 0 of 1 MCP server (1 still not connected — run /mcp to check) ».

> GO final pour la révision 3 du plan 17. Je viens d'exécuter /mcp reconnect all et de vérifier graphify et
> jcodemunch connectés. Lance ExitPlanMode puis implémente en mode auto. Livre d'abord le composant C partagé et ses
> tests ; avertis le Stream 14 dès que son commit vérifié est prêt. Garde les portes D2/PCA effectives et la
> séparation pretrain/calib.

## Suite donnée par l'instance

- Révision 3 approuvée en sortie du mode plan ; GO intégré dans `prompts/plans/plan-17.md`.
- Graphify (`graph_stats`) et jCodeMunch (`resolve_repo`) vérifiés par appel avant la première écriture.
- Deux commits locaux :
  - le composant C partagé, suivi de l'avertissement au stream 14 ;
  - IPCA, P4, les audits et la documentation.
- Arrêt avant fetch, fusion ou push.
