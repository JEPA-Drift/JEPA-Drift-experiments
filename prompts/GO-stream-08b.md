# GO — Stream 8b : hygiène (modules partagés, fixture sans effet de bord, registre des écarts)

Date : 2026-10-22.
Destinataire : instance Claude Code du worktree `stream-08b` (base `5048a96`).
Forme : transcription verbatim, par l'instance, des messages de l'orchestrateur et du GO (décision QA). Le GO a été
donné par l'écran d'approbation du plan ; le plan approuvé est `prompts/plans/plan-08b.md`.

## Consignes données pendant l'exploration (verbatim)

> Précision pour ton plan : toute commande Python ou pytest doit utiliser le .venv partagé (.venv/bin/python ou source .venv/bin/activate), jamais l'interpréteur Trading seul. Dans ce worktree, .venv et external apparaissent non suivis : prévois une solution locale et vérifiable pour que le critère git status propre soit testable.

> Les entrées nécessaires au plan sont suffisamment lues. Conclus maintenant par un plan borné pour 8b : hypothèses, fichiers exacts, contrôles SHA-256, correction des liens .venv/external non suivis et questions à arbitrer. N'engage aucune implémentation avant le GO.

## Revue du premier plan (verbatim)

> Correction impérative : reste dans le .venv du projet pour toutes les commandes du stream. Ne préfixe plus les appels Bash par `conda activate Trading` ; utilise `.venv/bin/python`, `.venv/bin/pytest` et le PATH du .venv, y compris dans le plan. La session Claude a bien été lancée depuis .venv. Termine maintenant un plan borné avec questions regroupées, avant tout code.

> Révise le plan avant GO. La branche stream-08b a été avancée par fast-forward sur main=5048a96 (les corrections du prompt 8b sont maintenant présentes) : actualise la base et les références de comparaison. Q1=c : corrige la cause racine dans `.gitignore` avec `/.venv` et `/external`, et ajoute ce fichier aux livrables ; n'utilise pas `.git/info/exclude`. Q2 : laisse la troisième copie du pivot hors périmètre de 8b. Q3 : oui, contrôle D4 ponctuel en lecture seule. Q4 : arrête-toi après commits et vérifications pour mon audit ; aucun fetch, push ni fusion sur main à cette étape. N'active plus Trading : toutes les commandes utilisent `.venv`, y compris Python et pytest ; pour make, ajoute au PATH le binaire conda-forge déjà présent `/home/m53/miniforge3/pkgs/make-4.4.1-h1114479_4/bin`. Présente le plan corrigé en mode plan, sans code.

## Revue du plan révisé : décision finale avant GO (verbatim)

> Décision finale avant GO : QA transcris verbatim cette revue et le GO dans `prompts/GO-stream-08b.md` ; QB H1, H9 et H10 confirmées ; QC garde les blocs 19/22/25 en l'état ; QD remplace les anciennes lignes de `.gitignore`. Corrige H11 : un seul commit Conventional Commits, après tous les changements, le wrapup actualisé et `make check` complet sous `.venv` ; vérifie `git status --porcelain` vide après ce commit. Cela évite l'incohérence du statut vide après chaque commit partiel. Une revue indépendante ne relève aucun autre blocage AST/SHA/fixture. Mets seulement cette correction dans le plan et repropose-le ; je donnerai le GO via l'écran d'approbation ensuite.

## GO

Plan corrigé (H11 : commit unique) approuvé par l'orchestrateur via l'écran d'approbation, le 2026-10-22.
