# Stream 32 — GO technique Codex après revue v2.1

Date : 14 novembre 2026. Base : `e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a`.
Décision distincte des notifications du chercheur : **R_A_B_GATED ; première activation R seulement**.
Autorité : instruction de poursuivre32, puis notifications14 et15 demandant la revue Codex avant décision technique.
Cette décision n'est ni un GO runtime ni un GO scientifique.

## Pièces revues

- Plan canonique `prompts/plans/plan-32.md`, SHA-256
  `035e47147c75df439b44748dae9be96b02b551ffee132ca11c59c3935e3fe482`.
- Amendement natif v2.1 capturé intégralement : `prompts/plans/plan-32-v2.1-amendment.md`, SHA-256
  `d6d5866ff2fa1669fcb86641263b0fff68cb95b13aef7726f2dfe786b90219e9`.
- Notifications14/15, dispositions correspondantes et revue finale `prompts/REVIEW-stream-32-plan-v2.1-20261114.md`.

Lecture complète et contre-revue statique terminées. C1 est corrigé par la séparation design/réalisation,
les exclusions d'autorité, les états de reprise et la suppression du setup_id réalisé des clés bootstrap.
C2 distingue NI brute et contrôle HEAD valide ; C3 fige les décisions avant toute puissance smoke/pilote.
Les68 comportements de test sont prévus ; aucun test d'implémentation n'a encore été exécuté à cette décision.

## Activation initiale : lot R

Propriétaire : Claude Code, session Phase B propre Opus/max, fondée sur le plan et ce GO ; pas de replanification.
Codex applique les patches de l'implémenteur avec l'outil natif apply_patch et contrôle les commandes.
Si apply_patch n'est pas exposé au client Claude, celui-ci fournit le patch en sortie structurée ; il ne lui
substitue pas une écriture shell. Codex reste intégrateur, pas auteur d'un noyau scientifique.

Périmètre R strict :

- `tests/test_check_prompts.py` : test de découverte34/30, ID32, amorçage exclu, témoin d'ID artificiel99 ; RED observé.
- `tools/check_prompts.py` : ajout32 seulement dans EXPECTED_IDS.
- `prompts/streams/prompt-32-pca-info-online.md` : première ligne seule normalisée ; corps inchangé.
- `prompts/streams/INDEX.md` : seule ligne de routage32.
- `prompts/Prompts_Claude_Code_v5.md` : synchronisation uniquement via `tools/check_prompts.py --sync-master`.

Séquence : tests d'abord → RED du contrôleur observé → production minimale → GREEN, prompts-check34/34,
conservation exacte des33 blocs et des autres prompts → arrêt pour réception écrite.
Les seuls tests activés sont ceux du contrôleur documentaire ; aucun calcul scientifique ou fixture ALT de campagne.
Commandes sous .venv, environnement déterministe et verrou principal partagé.

## Lots suivants et portes fermées

A puis B exigent une activation écrite après réception du lot précédent. Leur préparation technique est recevable
dans le périmètre de quatre fichiers, mais ils ne sont pas activés par ce premier lancement.
Pas de smoke CLI/profilage, pilote/full, données réelles/2020+, JEPA/J4, autre stream ou modification des scellés.
Pas de commit/push ni réindexation par Claude. Remote Control reste annulé.

RUNTIME_GO=ABSENT ; PILOT_GO=ABSENT ; FULL_GO=ABSENT. Les paramètres HEAD et les choix scientifiques restent
préenregistrables, à confirmer avant le premier GO runtime ; aucune puissance ne les informe.
