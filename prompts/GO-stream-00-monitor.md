# GO — lot opérationnel 00-monitor

**GO explicite du chercheur :** ordre de mission « résolution du blocage d'orchestration & harnais 30 minutes », reçu le 7 novembre 2026.

Plan : `prompts/plans/plan-00-monitor.md`. Autorisations : ajout du prompt E4 révisé, script d'inspection hôte, test ciblé, journaux/drapeau locaux, ordonnanceur détaché à 1800 secondes et remplacement de la surveillance à 20 minutes, puis vérification, commits et push main.

Le choix initial de l'option B est celui de Codex, fondé sur une vérification insuffisante de `cron.service`. Le drapeau de revue est retenu parmi les modalités permises par E4 ; il ne vaut ni décision cognitive automatique ni GO d'implémentation pour Claude.

Les lectures des sessions et métadonnées Git restent non modifiantes. Aucun message, redémarrage, changement de modèle/effort, arrêt ou édition du travail des deux Claude. Aucune expérience ni modification scientifique. Les règles de tests, wrapup, anonymisation, J1/D8, données protégées, staging explicite et push non forcé restent applicables.

## GO complémentaire — persistance utilisateur

L'ordre d'exécution du chercheur autorise le passage à la crontab utilisateur lorsque celle-ci fonctionne, l'arrêt du démon 34317 et de son enfant, puis les audits et clôtures des deux Claude. `crond.service` est le service actif et activé de cette machine. Le correctif de PATH nécessaire à l'exécution sans shell interactif, son test de non-régression et son commit sont inclus dans cette autorisation. Aucune modification de `.bashrc` n'est nécessaire. La restriction antérieure sur les interactions des deux Claude concernait le seul déploiement du harnais ; elle n'annule pas l'ordre présent de les auditer, corriger si nécessaire et fermer proprement après clôture.
