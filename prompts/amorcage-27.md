# Amorçage — stream 27, E10 linéaire

Lis `CLAUDE.md`, `prompts/streams/INDEX.md` et `prompts/streams/prompt-27-e10.md`.
Travaille dans le worktree `stream-27`. Planifie l'étape `linear` avec P1-C et P3-C sur F1 ;
F2 sur D3 attend le chargeur partagé de 8b, sans pivot local, et P5-C attend le point de contrôle
gelé du stream 16. P1-C réutilise `monitors/cusum.py` ; les données brutes avant
2020 restent descriptives. Rapporte FPR observé et IC avec les gains, sans revendiquer une
exactitude sous asymétrie ou pour P3-C recentré sur q̂ estimé ; respecte `[-1, 1]` pour son e-processus.
Présente les fichiers touchés, graines, cellules et questions ;
attends le GO de l'orchestrateur avant le code. Après ce GO, enregistre
`prompts/plans/plan-27.md` avec « Décision GO intégrée » et exécute l'étape autorisée.
