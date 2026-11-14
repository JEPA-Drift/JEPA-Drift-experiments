# Autorisation du chercheur — finalisation E4 sans certificat du plafond

Date : 2026-11-14. Provenance : réponse explicite dans la conversation Codex, après présentation de la réserve
comptable et de `prompts/STOP-stream-19-e4-closeout-accounting-20261114.md`, SHA-256
`d1156e360ff426eeda177ae86d6fc50261d7eddaa7a160c5d340b7d68dd5a69f`.

Décision exacte du chercheur : « autorisation de finalisation E4 sans certificat du plafond ».

## Disposition

Le chercheur autorise la finalisation documentaire, les vérifications de clôture déjà autorisées, le commit et
la publication contrôlée du lot E4 **avec la réserve comptable explicitement conservée**, sans présenter le
plafond global de 24 CPU-heures comme certifié. Cette décision lève l'arrêt de clôture lié à cette réserve.
Le STOP antérieur reste conservé comme historique ; aucune mesure n'est réécrite et aucun poste UNKNOWN
n'est remplacé par zéro. Aucun dépassement n'est établi ; aucun dépassement ni relèvement du budget n'est
autorisé par cette décision.

Les mesures des invocations, le dernier relevé WHOLE-service, la borne dérivée conditionnelle et les limites
de leur couverture restent distincts dans le rapport. Les coûts des vérifications et du hook sont ajoutés,
avec leur propre cutoff. Les journaux de commande, sorties, temps et empreintes sont conservés.

Le protocole scientifique, ses paramètres, les sources gelées et la publication terminale restent inchangés.
Aucun recalage, nouvelle simulation scientifique ou suppression opportuniste de résultat n'est autorisé.
Les limites de 8 Gio et de 30 minutes par invocation, le verrou partagé et les gardes de données s'appliquent
aux opérations restantes. L'exception de vérification globale existante reste strictement limitée à son GO.

## Dépendances

Après publication et clôture E4 réussies seulement, Codex peut reprendre la réconciliation du stream 23 et la
vérification de ses portes existantes. Aucun GO runtime implicite n'est créé : les signaux techniques/runtime
bornés restent distincts et doivent reposer sur les autorisations existantes et les preuves de leurs portes.
Les restrictions des streams 27, 21 et 16 sont inchangées : P8 non approuvé, aucun code 21/27 supplémentaire,
aucun pilote ou entraînement 16/J3, aucune phase 2 JEPA/P5-D, aucun J4 ni nouvel accès privé ou 2020+.
