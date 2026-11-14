# STOP E4 — garde disque avant activation, 13 novembre 2026

**Décision Codex : exécution scientifique FULL NON ACTIVÉE.** Aucun appel scientifique full n'a été lancé.

Autorité : `prompts/GO-stream-19-e4-full-20261112.md`, section « Limites et arrêts » : échec d'une condition
bloquante ⇒ STOP, rapport motivé et retour au chercheur. Ce refus concerne l'état du stockage, pas un résultat
scientifique. Il ne permet aucun repli de grille ou ajustement de protocole.

## Mesure et seuil

Contrôle shell à 14:28 UTC le 13 novembre 2026 : `df -B1 --output=source,size,used,avail,target .` dans le dépôt.
Volume `/dev/md1`, espace disponible **887 238 656 octets**. Aucune donnée financière n'a été ouverte pour ce contrôle.

Le rapport final technique donne 107 933 096 octets projetés et un temporaire maximal dérivé de 7 333 882 octets.
Règle d'activation du code reçu : `4 * projected_bytes + max(projected_tmp_bytes)` = **439 066 266 octets**,
plus la réserve obligatoire de **1 073 741 824 octets**. Minimum total requis : **1 512 808 090 octets**.
Déficit à cette observation : **625 569 434 octets**. Même la réserve seule n'est plus disponible.

## État conservé

- Pilotes P1/P2 terminés, deux générations de preuves candidates validées, source et protocole inchangés.
- Prévision figée finale : 57 178,3295905 CPU s ; avec la queue déjà mesurée jusqu'à A0000389 :
  57 287,7895905 CPU s, sous 86 400 s. Ce sont des estimations conditionnelles, pas une garantie de coût.
- Rapport technique : `docs/audits/stream_19_e4_production_pilot_20261113.md`.
- Aucun fichier d'activation full créé, aucune donnée du pilote utilisée pour adapter la science.
- Aucun nettoyage d'artefact, suppression de donnée ou modification de processus privé effectué.

## Reprise

Le chercheur doit rendre de l'espace disponible sur ce volume ou autoriser une solution de stockage précise.
Libérer au moins le déficit ci-dessus, avec une marge pour les autres processus ; 2 Gio disponibles donneraient
une marge supplémentaire. Ne pas supprimer les données, les scellés ou les preuves référencées par les manifestes.
Codex devra ensuite mesurer à nouveau le disque, confirmer les identités et les coûts cumulés, documenter la
levée de ce STOP, puis activer explicitement le GO 2 déjà accordé sous conditions. Aucun nouveau choix scientifique
n'est demandé. Les expériences 23 et 27 restent derrière la clôture scientifique réussie d'E4.
