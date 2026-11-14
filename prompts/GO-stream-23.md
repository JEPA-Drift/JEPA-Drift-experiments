# GO — Stream 23 : E6 phase 1, P1-D et P3-D sur dérives de second ordre F4

Date : 2026-10-22.
Destinataire : instance Claude Code du worktree `stream-23` (base `2b0b1cd`).
Forme : transcription verbatim, par l'instance, des messages de l'orchestrateur et du GO. Le plan
approuvé est `prompts/plans/plan-23.md` (révision 2).

## Consignes données pendant l'exploration (verbatim)

> Correction : utilise .venv/bin/python et .venv/bin/pytest pour toute exécution ; Trading seul casse les hashes. P1-D peut réutiliser monitors/cusum.py sans nouvelle entrée PIPELINES. Les liens .venv/external non suivis sont du bruit de worktree à résoudre pour le critère git status.

> Correction impérative : reste dans le .venv du projet pour toutes les commandes du stream. Ne préfixe plus les appels Bash par `conda activate Trading` ; utilise `.venv/bin/python`, `.venv/bin/pytest` et le PATH du .venv, y compris dans le plan. La session Claude a bien été lancée depuis .venv. Termine maintenant un plan borné avec questions regroupées, avant tout code.
> Les lectures et la sonde suffisent pour la planification. N'en lance aucune autre. Rédige maintenant un plan borné pour E6 phase 1 P1-D/P3-D sur la base 5048a96, `.venv` uniquement : D6 fenêtres chevauchantes et N_eff/deff, aucun pseudo-échantillon par signes pour les énergies paires, FPR D6 en échantillon qualifié descriptif, D5 calibration/test sur graines disjointes pour contrôle externe, FPR atteint/IC et règles de censure préfixées, I_target=None pour F4, KL gaussienne de conception seulement. P4-D après 17, P5-D après 16. Regroupe les questions, attends mon GO et n'écris aucun code.

## Revue du premier plan : GO suspendu (verbatim)

> Plan 23 : GO suspendu. Le main local est 2b0b1cd, stream-23 a été avancé dessus et les prompts E6/amorcage ont été corrigés. Relis-les puis révise le plan sans coder : P1-D doit utiliser energy_stream Article B, mu=mean(r^2), sigma=std(r^2) sur fit propre, puis refaire la sonde et les seuils ; si le seuil D5 P3-D change, recalculer Gamma_op avec lambda_D5/lambda_iid. D6 réutilise ses 941 jours pour calibrer et évaluer : FPR descriptif sans IC, G_ADD IC=NA si dépendance non estimable ; D5 garde IC Wilson et bootstrap apparié du rapport RMST_H. PC2-PC3 est exploratoire sur D6 après sonde, mais fixé avant test D5 ; K=10 D5 conditionnel, ajouter sensibilité K=1. Information de rotation conjointe ; budget gaussien non borne opérationnelle du CUSUM. Aucun log non suivi dans Git, nouveaux audits en anglais, .venv exclusivement. Arrêt avant fetch/push/merge après implémentation. Présente un plan corrigé et les questions bloquantes ; attends mon GO.

## GO (verbatim)

> GO pour le plan révisé du stream 23, phase 1. Les réponses Q1–Q5 par défaut sont approuvées : garder D6 descriptif avec IC=NA, ne pas recentrer P3-D, K=1 comme sensibilité, garder les paires exploratoires, règle IC=NA D6. Implémente exclusivement ce plan dans ce worktree via .venv, consigne le GO et les écarts, exécute les contrôles, puis arrête-toi avant fetch, push et merge.

Le plan révisé, avec sa section « Décision GO intégrée », a ensuite été approuvé par l'écran
d'approbation, le 2026-10-22.
