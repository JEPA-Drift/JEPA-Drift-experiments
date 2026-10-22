# Amorçage — stream 23, E6 phase 1

Lis `CLAUDE.md`, `prompts/streams/INDEX.md` et `prompts/streams/prompt-23-e6.md`.
Travaille dans le worktree `stream-23`. Planifie uniquement la livraison P1-D/P3-D de phase 1 ;
P4-D attend la fusion de 17 et P5-D attend 16. Vérifie le chevauchement des fenêtres de calib,
la taille effective et la séparation calibration/évaluation. Traite la formule de variance
comme information gaussienne de conception. Avant le GO, vérifie la normalisation P1-D de l'Article B,
Γ_z^op après le seuil final, le statut exploratoire du témoin PC2–PC3 sur D6 et les IC D6 estimables. Utilise `.venv` pour Python,
pytest et les hooks ; garde les logs hors Git et rédige les nouveaux audits en anglais.
Présente les fichiers touchés, cellules, contrôles
de FPR et questions ; attends le GO de l'orchestrateur avant le code. Après ce GO, enregistre
`prompts/plans/plan-23.md` avec « Décision GO intégrée » et exécute la phase autorisée.
