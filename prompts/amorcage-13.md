# Amorçage — stream 13, E3

Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
`prompts/streams/INDEX.md` et `prompts/streams/prompt-13-e3.md` dans le worktree `stream-13`.
Reste en mode `plan`. Sépare les garanties sous D6 des diagnostics sur placebos bruts ; détaille
la calibration, les niveaux atteints, les IC et la censure d'ARL₀. Présente le coût et le
fractionnement des 20 000 trajectoires, les fichiers touchés et les questions.
Vérifie Γ^spec pondéré de Bartlett, la génération gaussienne distincte de t₇, le flux P1-D de
l'Article B et le statut descriptif des fenêtres brutes chevauchantes. Diffère `mixture_s2`
jusqu'à l'intégration de la porte Holm du stream 12.
Révise le plan : borne réelle stricte au 2005-01-04, mêmes cinq titres
`composition_for(5, N)` que dans E1 et test de remise à zéro par fenêtre pour les lectures
locales P1-C, P1-D, dépassement et encodeurs. Les défauts Q1/Q3/Q4/Q5 sont retenus :
la porte ±5 % à 2 000 trajectoires reste primaire, avec échec rapporté sans nouveaux tirages.
Attends le GO de l'orchestrateur. Après ce GO seulement, enregistre `prompts/plans/plan-13.md` avec
« Décision GO intégrée » et implémente.
Utilise `.venv`, rédige les nouveaux audits en anglais et arrête-toi au commit local vérifié avant fetch, fusion ou push.
