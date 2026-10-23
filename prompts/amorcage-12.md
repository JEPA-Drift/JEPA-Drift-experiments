# Amorçage — stream 12, E1

Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
`prompts/streams/INDEX.md` et `prompts/streams/prompt-12-e1.md` dans le worktree `stream-12`.
Reste en mode `plan`. Présente la grille de calcul, les coûts de run, la mesure du FPR atteint,
les comparaisons à fausse alarme égale et les limites des prévisions gaussiennes sur D6.
À H = 2 000, qualifie l'analyse de rétrospective ; sépare délai restreint, censure et ADD de Lorden.
Étiquette les meilleurs titre/canal comme oracles et fixe la référence P1 avant la loi d'échelle.
Les rotations placebo n'identifient pas une fraction causale. L'ancien
`prompts/GO-stream-12.md` porte sur une spécification antérieure : ne le traite pas comme GO de
ce plan. Révise le plan : borne réelle stricte au 2005-01-04, mêmes cinq titres
`composition_for(5, N)` que dans E3, et test d'invariance au préfixe avant chaque onset
pour la nouvelle lecture P1-C. Pour J2(i), garde les 2 000 répliques et la règle de verdict
du prompt en analyse primaire ; rapporte le risque de faux FAIL dû aux 54 contrôles,
sans changer les graines après résultat. Retient les défauts Q2–Q9 du plan et soumets
la version corrigée à l'orchestrateur. Attends son GO. Après ce GO seulement,
enregistre `prompts/plans/plan-12.md` avec « Décision GO intégrée » et implémente.
Utilise `.venv`, rédige les nouveaux audits en anglais et arrête-toi au commit local vérifié avant fetch, fusion ou push.
