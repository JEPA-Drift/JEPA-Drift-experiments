# Stream 30 — GO du plan après amendements mineurs

Proposition Claude originale : 389 lignes, SHA-256 `12651c01a932d482622fd861c142e763491ba6eaaa1e50b0bfccdec01337c7b7`, conservée sans modification dans `PLAN.md` et `logs/pca_drift_orchestration/PLAN-v1.md`. Plan canonique amendé : `prompts/plans/plan-30.md`.

GO du **plan 30 uniquement**, le 2026-10-31, après audit Codex isolé et deux amendements mineurs autorisés directement par le chercheur. Les défauts du plan sont retenus. Aucun retour Claude n'est nécessaire pour ces précisions ; aucune logique scientifique ni sélection de scénario n'est changée.

Amendements intégrés dans le corps :
1. `V_NOT_COMPARABLE` vérifie une même fonction M et un même gamma, avec M évalué à la dimension propre de chaque ligne. Il n'exige pas M(k) = M(d_star) et ne recalcule pas V.
2. `INPUT_INVALID` vérifie les quatre CSV lus contre `manifest.outputs` ; le hash du manifest est contrôlé via la provenance d'entrée des tableaux. Le manifest producteur ne contient pas son propre hash.

La comparabilité FPR reste un filtre descriptif de protocole et d'intervalles : elle ne prouve pas l'égalité des FPR atteints. Les intervalles RMST marginaux ne sont pas des intervalles de différence appariée. Les API et sous-clés non encore fixées du futur assembleur 29 restent des préconditions G0 à vérifier lors de l'implémentation, sans prétendre qu'elles existent déjà.

**Portée : plans seulement.** Claude Code rédige les plans en max/xhigh ; Codex les audite et contrôle la clôture/intégration ; Mistral Vibe `large-4`, thinking `high`, est l'implémenteur désigné après GO d'exécution. Ce GO de plan autorise la planification du dernier stream 31, pas le démarrage d'une implémentation 30. Aucun full, nouvelle simulation, recalibration ou évaluation réelle post-2019 n'est autorisé.

Audit de référence : `docs/audits/stream-30-plan-review.md`. Seul le plan 30 a été chargé dans le contexte du relecteur. Les artefacts scellés et l'identité du runner, E2 disque/index CRLF/SHA-256 et le FAIL historique E3/D8 ont été contrôlés. Aucun script de figures ni rendu n'existe encore ; aucun test applicatif ou contrôle visuel n'est annoncé comme exécuté.

