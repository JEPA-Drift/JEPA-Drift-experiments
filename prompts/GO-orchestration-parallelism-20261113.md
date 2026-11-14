# Clarification du chercheur — parallélisme, 13 novembre 2026

**Provenance :** instruction explicite dans la conversation Codex, après le bilan de réception E4 : la limite de
deux instances est indicative, vise les instances que Codex orchestre activement et ne compte pas les autres sessions
ouvertes. Le chercheur demande de relancer les sessions prioritaires ; aucune fermeture de session privée n'est requise.

Cette clarification remplace les anciennes formulations incluant toutes les sessions privées. Elle lève le blocage
opérationnel de reprise d'E4. Codex conserve deux travaux orchestrés activement comme cible et reprend la conversation
E4 existante, dans son worktree et avec son contexte. Aucun processus privé n'est modifié.

Les autorisations scientifiques et leurs dépendances restent celles des GO existants : corrections de production E4,
réception, pilote technique, bilan des ressources puis activation explicite du GO full si toutes ses conditions passent.
Les streams 23/E6 phase 1 et 27/E10-F2 démarrent après la clôture réussie et la publication scientifique d'E4.

Le verrou partagé, la sérialisation des calculs/tests/intégrations, les plafonds CPU/RSS/durée, les données interdites,
les scellés et l'absence de remplacement automatique par un troisième stream restent applicables. Cette clarification
n'autorise ni J4, ni JEPA/VAE, ni une modification de protocole ou de périmètre des données.

## Nouvelle instruction du chercheur — quatre streams maximum

Instruction explicite ultérieure dans la même conversation, le 13 novembre 2026 : « Poursuis en lançant en parallèle
plusieurs streams parmi les streams prioritaires », avec une borne maximale de quatre streams activement orchestrés.
Cette borne remplace la cible indicative de deux ci-dessus ; les sessions privées restent exclues du comptage.

Codex poursuit E4 et ouvre trois sessions natives de planification distinctes : 23/E6 phase 1, 27/E10-F2 et
21/dispatcher sur fixtures ou blocage exact. Elles partent du main publié `b18d8e5`, chacune dans un worktree propre.
Chaque plan sera revu avant tout GO d'implémentation, dans la même session interactive. Le lot 21 déjà qualifié
documentairement n'est pas refait ; le runner de production reste DEFERRED et G1–G10 restent OPEN.

Cette instruction autorise la préparation parallèle. Les reproductions scientifiques 23 et 27 restent subordonnées
à la clôture scientifique réussie d'E4 ; leurs bases seront réconciliées sur le main alors publié. Les plafonds E4,
le verrou partagé et la sérialisation des calculs/tests/intégrations sont inchangés. Aucun cinquième stream,
remplacement automatique d'un bras bloqué, J4, accès privé ou 2020+, ni entraînement n'est autorisé.

## Dernière instruction — deux implémentations seulement

Le chercheur précise ensuite : « Continue en ne lançant pour l'instant l'implémentation que des deux streams les
plus prioritaires en parallèle pour l'instant ». Cette limite d'implémentation prime sur la capacité de quatre
sessions. Codex retient E4 et 23/E6 phase 1, sous leurs portes techniques et scientifiques ; 27/E10-F2 et 21 restent
en planification/revue, sans GO de code. Un bras bloqué n'est pas remplacé automatiquement.

Au contrôle du 13 novembre à 14:28 UTC, E4 échoue à la garde disque et son activation reste absente. Le plan 23
requiert une correction de son hypothèse H3 : lire les observations 2020+ puis les filtrer est interdit. Ni la
limite de deux, ni une instruction de continuation ne lève ces blocages. Les sessions restent ouvertes et leurs
plans conservés ; aucune expérience supplémentaire ne démarre.
