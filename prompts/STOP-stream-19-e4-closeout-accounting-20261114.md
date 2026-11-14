# Arrêt de clôture E4 — couverture de la comptabilité CPU

Date : 2026-11-14. Décision Codex : **STOP de la clôture technique et de la levée des dépendances**,
dans l'attente du traitement de la réserve comptable ci-dessous. Aucun dépassement de CPU n'est établi.

## Provenance et portée

Le GO scientifique conditionnel du chercheur est `prompts/GO-stream-19-e4-full-20261112.md`, SHA-256
`19d2697700bc9a0af5d98c9bd7c901129450aed385487582ef67c3f17e094746`.
Il impose un plafond global de 24 CPU-heures, pilotes déjà consommés inclus, et un retour au chercheur si une
condition bloquante échoue. La décision ultérieure d'orchestration exige aussi de conserver la comptabilité
du surcoût du driver. La demande de fin E4 conserve les portes propres du stream 23 et les interdictions des
streams 27, 21 et 16.

Cette réserve concerne la couverture de la comptabilité. Elle ne constitue ni une reproduction scientifique
échouée ni une preuve de dépassement. Aucun paramètre scientifique n'est modifié.

## Réception établie

- Campagne lancée le 2026-11-13 à 14:59:28 UTC, terminée le 2026-11-14 à 00:02:44 UTC, sortie 0.
- 354 partitions terminées ; merge et analyse terminés ; vérification et publication locale réussies.
- Audit portable : activation=true, 560 blocs, 42 calibrations recalculées, 91 fichiers déclarés.
- 672000 essais, 84000 maxima, 28000 diagnostics et 3948000 lignes de diagnostics d'axes.
- Sept tables scientifiques finales : 84 cellules par lecture, 168 lignes de FPR holdout, douze contrastes
  NOT_IDENTIFIED. Les quatorze flags FPR_ABOVE_NOMINAL de la lecture prédictive restent publiés.
- Les 91 SHA déclarés dans PUBLISHED.json ont été revérifiés par Codex. Le plus gros fichier déclaré mesure
  13651324 octets, sous la limite de 45 Mio de l'audit portable et sous la limite Git de 50 Mo.

Publication locale : `results/e4_alignment/full_20261113`.
SHA-256 de `PUBLISHED.json` : `5c318af8768b7f1b83e08e30a20dd57067010ad05bf7b70a0cb31d3c03fd544d`.
SHA-256 de `manifest.json` : `b7514d600af40dc5e10ac8738333c25059218bd184c4a49008adbe2b5de6d69c`.
La revue scientifique ne relève aucune anomalie matérielle ; les fortes censures et les différences de FPR
restent des résultats à rapporter, sans ajustement a posteriori.

## Mesures conservées et limite établie

Le reçu comptable terminal, hors publication immuable, arrête le ledger à A0000749 : 34995.28 CPU_s,
imports et pilote initial inclus. Sa propre invocation administrative A0000750 ajoute 1.43 CPU_s mesurées.
Le total des invocations ainsi couvertes vaut **34996.71 CPU_s, soit 9.721308333 CPU-heures**.
Les échecs et essais RED mesurés sont inclus ; aucune ligne n'a été supprimée pour réduire ce total.

Ce total n'inclut pas tous les processus d'infrastructure. Le dernier relevé WHOLE-service conservé date du
2026-11-13 à 23:30:25 UTC : 30574198723000 ns pour le service, plus la baseline pré-service enregistrée de
2999.71 CPU_s, soit 33573.908723 CPU_s. Ce compteur comprend le driver, les wrappers, les enfants et une
invocation active. Il chevauche le ledger ; il ne doit jamais lui être ajouté comme un coût indépendant.
SHA-256 du relevé : `432adf909761db22889d60826aa5754f1b042c017046e3289ae40d152ff5faa7`.

L'unité transitoire collect a disparu après sa sortie : le compteur final n'est plus disponible. Le journal
ciblé est inaccessible avec les permissions courantes ; sudo non interactif exige un mot de passe. Aucune
escalade ni modification du driver gelé n'a été réalisée.

Une borne conditionnelle dérivée peut couvrir la fin du service :

    33573.908723 + 2056.48 + 8 * 1940 = 51150.388723 CPU_s, soit environ 14.21 CPU-heures.

Les 2056.48 CPU_s correspondent à toutes les invocations A0000736–A0000750, incluant un chevauchement
conservateur avec le dernier relevé. Les 1940 secondes arrondissent par excès la durée restante. Le facteur 8
est une enveloppe conservatrice de processus d'infrastructure monotâches simultanés pour les wrappers
synchrones observés ; la route production ne lance pas le ProcessPoolExecutor du prototype.
Cette borne est **DERIVED, conditionnelle à cette structure**, et non une mesure du coût terminal.

Elle ne couvre pas les surcoûts pré-service non enregistrés et la lecture administrative XML déjà identifiée
UNKNOWN avant activation. Ils ne sont ni supprimés ni remplacés par zéro. Le compteur final du service seul
ne résoudrait pas cette seconde réserve. La marge du périmètre couvert ne constitue donc pas un certificat
exhaustif de respect du plafond global.

Le RSS maximal de la production est 538020 Kio ; l'invocation de production la plus longue dure 243.99 s.
Le lot d'ingénierie inclut aussi R0009 à 3838968 Kio et 592.76 s, selon ses mesures existantes. Les deux
périmètres sont distincts et inférieurs aux limites de 8 Gio et de 30 minutes sur les mesures disponibles.

## Disposition et retour nécessaire

Le rapport scientifique et la traçabilité documentaire peuvent être préparés à partir de la publication
terminale. Aucun nouveau test, reindex, commit, push ou runtime dépendant n'est déclenché dans cet état.
La campagne terminée n'est ni relancée ni recalibrée. Les résultats locaux, sources gelées et traces restent
conservés. Le lot E4 n'est pas déclaré clos avec succès ; le stream 19 historique reste partiel.

Le chercheur doit disposer explicitement de cette réserve avant la clôture et la reprise : soit apporter une
preuve comptable couvrant les postes manquants, soit autoriser la réception et la publication avec cette limite
de mesure déclarée, sans présenter le plafond comme certifié et sans autoriser un dépassement. Le choix n'est
pas inféré des GO antérieurs. Les vérifications globales et le hook déjà autorisés restent ensuite à exécuter
sous verrou, avec leurs coûts ajoutés et sans masquer de skips ou d'échecs.
