# JEPA-Drift — paquet de directives Codex, 24 octobre 2026

**Usage** : transmettre ce dossier à l'instance Codex supervisant `~/JEPA-Drift-experiments` et **injecter d'abord** le contenu de `00_CODEX_AMORCAGE_2026_10_24.md`. Codex vérifie le dépôt local et les worktrees avant de déplacer les fichiers dans `prompts/streams/`. Les versions des prompts 14 et 22 constituent des remplacements proposés ; les autres sont des addenda à réconcilier avec les versions canoniques via plan et GO. `10_CODEX_INTEGRATION_AND_ORDER.md` fournit l'ordre et le mapping.

**Source de vérité** : handover `prompts/wrapups/handover-01-27.md`, section 3.6 au 23 octobre 2026, index et fichiers du dépôt local. L'audit scientifique rédigé dans la conversation sert à la refonte ; le fichier distinct mentionné par l'utilisateur sous le titre `ANSWER Chat-GPT-6 ASTRA.md` n'a pas été retrouvé dans les fichiers disponibles ici. Aucun état Git réel du serveur à l'instant de réception n'est présumé.

**Invariants** : SHA-256 complet de J1 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` avec fins de lignes CRLF natives ; gel de tous les états d'encodeur et de référence sur `monitor` ; TDD/`make check` et GO avant fusion ; pas de réinterprétation du budget d'évidence comme borne universelle ARL finie ; DPI ; J4 pré-gelé avec P3-CS(b)/P4 à FPR comparables ; panel biaisé par survie étiqueté et GICS statique exclu du principal.

**Fichiers** :

- `00_CODEX_AMORCAGE_2026_10_24.md` : premier message autonome pour Codex.
- `01_STREAM_14_REWRITE_BOTTLENECK.md` : refonte intégrale CA-T-JEPA, masque et anti-fuite, tests négatifs.
- `02_STREAM_12_E1_J2_ADDENDUM.md` : E1, pooling, calibration à horizon et jalon J2.
- `03_STREAM_13_E3_J2_ADDENDUM.md` : FPR/ARL, null multicanal, asymétrie et recentrage.
- `04_STREAM_16_J3_PRETRAIN_ADDENDUM.md` : préentraînement, RankMe, contrôles et sélection.
- `05_STREAM_17_18_BASELINES_ADDENDUM.md` : IPCA/P4 et CD-DFM sans avantage informationnel déloyal.
- `06_STREAM_21_FREEZE_PROTOCOL_ADDENDUM.md` : freeze et tests pré-J4.
- `07_STREAM_22_E5_J4_REWRITE.md` : E5, baselines principales et porte confirmatoire.
- `08_STREAM_23_26_SECOND_ORDER_ABSORPTION.md` : E6 F4 et E7 absorption, interprétation conditionnelle.
- `09_THEORY_MANUSCRIPT_REVIEW.md` : corrections mathématiques §3/Annexe A.
- `10_CODEX_INTEGRATION_AND_ORDER.md` : mapping, dépendances, collisions et décision GO.

**Contrôle local réalisé** : tous les fichiers annoncés sont du Markdown, les blocs de code sont équilibrés et les directives de streams disposent des sept sections standard exigées. Aucune commande `make check` ni `make j1` n'a été exécutée sur le serveur ; leur réussite doit être vérifiée par Codex. Les empreintes listées dans `CHECKSUMS.sha256` identifient seulement **ce paquet**.
