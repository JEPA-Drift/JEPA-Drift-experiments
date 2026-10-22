# Amorçage — stream 14, CA-T-JEPA

Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
`prompts/streams/INDEX.md` et `prompts/streams/prompt-14-ca-tjepa.md` dans le worktree
`stream-14`. Reste en mode `plan`. Résous sans installer la compatibilité de torch CPU issu
exclusivement de `conda-forge` dans `.venv`, avec Python 3.12.9, numpy/scipy/pandas épinglés et les tests
existants. Propose un environnement reproductible ; signale toute incompatibilité avant le GO.
Le protocole principal n'emploie que les quatre caractéristiques continues causales. Prévois
des générateurs torch locaux, des gardes sur le vrai modèle et le hash J1. Présente les fichiers
touchés et les questions ; attends le GO de l'orchestrateur. Après ce GO, enregistre
`prompts/plans/plan-14.md` avec « Décision GO intégrée » et implémente.
