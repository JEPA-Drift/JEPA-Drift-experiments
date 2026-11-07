# Plan 00-monitor — harnais déterministe de surveillance Claude Code

## Objectif et périmètre

Appliquer l'ordre de mission du chercheur du 7 novembre 2026 : versionner E4, puis déployer une inspection hôte toutes les 30 minutes. Codex implémente ici de l'outillage opérationnel, sans code scientifique. Les deux sessions Claude existantes conservent leur effort Max et leurs fichiers.

## Constat et choix

- Le prompt d'amorçage est non suivi : `git diff` est vide, son ajout sera explicite. La section E4 révisée est lue et acceptée sans modification.
- Le timer utilisateur existant fournit seulement des instantanés à 20 minutes ; aucun drapeau de revue. Cron est installé mais son service est inactif.
- Choix Codex : option B autorisée, démon détaché avec veille de 1800 secondes hors inférence. Désactiver l'ancien timer après réception du nouveau dispositif.
- Une entrée shell exécutable appelle le Python de la .venv ; moteur d'inspection stdlib séparé, sans dépendance ajoutée. Verrou natif `flock`, aucune interaction envoyée aux sessions.
- Sessions déclarées dans un registre local ignoré, découverte complémentaire des sessions `jepa-`. `jepa-s31` reste inspecté mais son absence historique n'est pas un succès ni un incident actif attendu.

## Étapes et réception

1. Commit documentaire explicite demandé, avec ce plan, GO et wrapup ; `make check` obligatoire par hook, contrôles J1/D8 et anonymisation, push main.
2. TDD du classement : activité, question/permission, plan prêt, quota, sortie/exception, absence ; contrôle des alertes persistantes et des frontières de 30 minutes. Tester les effets réels sur journal/drapeau ; doubler seulement la frontière des commandes hôte.
3. Créer `tools/ops/monitor_claude_sessions.sh`, `tools/ops/monitor_claude_sessions.py` et `tests/test_claude_surveillance.py`. Capturer `tmux -S -80`, contrôler les processus ; observer HEAD/statut Git sans rafraîchir l'index, métadonnées de fichiers sans suivre les liens ni parcourir données/environnements/caches.
4. Journal UTC `logs/claude_surveillance.log`, état précédent local, drapeau `logs/NEEDS_CODEX_REVIEW` contenant motifs et extraits tmux. Les alertes non acquittées persistent. Aucun GO, redémarrage ou réveil d'inférence automatique ; le drapeau est la modalité d'intervention autorisée par E4.
5. Exécuter une réception réelle, lancer le démon, vérifier PID/commande et intervalle, arrêter l'ancien timer ; ne pas attendre 30 minutes dans Codex. La stagnation exige absence d'activité disque/Git et de changement terminal ; une première observation initialise l'historique terminal.
6. Revue indépendante bornée, corrections éventuelles, wrapup actualisé, réindexation AST de fin de lot, hook `make check`, commit outillage, push main ; état initial des sessions et code de l'entrée shell dans le rapport final.

## Décision GO intégrée

L'ordre de mission détaillé du chercheur constitue le GO d'exécution et de publication de ce lot. Pas de demande de confirmation supplémentaire. Les refus d'infrastructure sont consignés ; maximum trois tentatives de réparation, puis arrêt déclaré. Aucune expérience PCA nouvelle, données réelles, JEPA/VAE, J4, campagne, résultat ou dépendance numérique n'est autorisé. Les deux prompts utilisateur étrangers au lot restent non suivis et inchangés.
