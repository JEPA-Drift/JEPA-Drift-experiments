# Amorçage — stream 14, CA-T-JEPA

Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
`prompts/streams/INDEX.md` et `prompts/streams/prompt-14-ca-tjepa.md` dans le worktree
`stream-14`. Reste en mode `plan`. `.venv` est un venv Python, pas un préfixe Conda :
diagnostique cette incompatibilité avant tout GO. Résous torch CPU exclusivement depuis
`conda-forge` sans installer, puis distingue ce dry-run d'une procédure vérifiable de
reconstruction ou migration au même chemin, préservant Python 3.12.9, numpy/scipy/pandas,
les autres dépendances, `make check` et le SHA J1. Si aucune procédure n'est démontrée,
consigne le blocage et arrête sans code. Diffère toute mutation de la `.venv` commune
jusqu'à la fin des vérifications et runs des autres streams ;
coordonne l'extracteur et les contrats partagés avec le stream 17, sans casser D2/PCA.
Le protocole principal n'emploie que les quatre caractéristiques continues causales. Prévois
des générateurs torch locaux, des gardes sur le vrai modèle et le hash J1. Présente les fichiers
touchés et les questions ; attends le GO de l'orchestrateur. Après ce GO, enregistre
`prompts/plans/plan-14.md` avec « Décision GO intégrée » et implémente.
Rédige les nouveaux audits en anglais et arrête-toi au commit local vérifié avant fetch, fusion ou push.
