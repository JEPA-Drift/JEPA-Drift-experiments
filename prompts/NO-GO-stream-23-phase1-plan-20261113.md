# Revue Codex — plan E6/23 phase 1, 13 novembre 2026

**NO-GO d'implémentation en l'état. Révision native bornée autorisée, dans la même session.**
Plan reçu : `lis-la-mission-compl-te-greedy-wreath.md`, SHA-256
`6e870ad9b089d7cbf9895befa73c6883f58f005d7f7c2f8d2eda3a10e87ac73c`.
Double revue statique Codex : aucune nouvelle décision scientifique nécessaire pour les corrections ci-dessous.

## Corrections bloquantes

1. **H3 est refusée.** L'interdiction des observations 2020+ s'applique à leur lecture. Le filtrage après
   `sp500._load_wide` et le hachage de `ret_wide.npy` entier ne la respectent pas. Ne demander ni exception ni
   redéfinition implicite de cette restriction. Proposer le plus petit adaptateur d'entrée borné, avant toute
   lecture de valeurs, réutilisant un précédent du dépôt si son contrat convient. Ne pas toucher aux noyaux
   scientifiques, paramètres, graines, cohortes, dates ou estimands. Aucun accès aux véritables fichiers ni à
   leurs métadonnées pendant cette révision ; les hypothèses de disposition doivent être testées sur fixtures.
2. **Les tests doivent respecter la même frontière.** Les tests historiques chargent le panel réel et la CLI
   hache le fichier entier. Prévoir des fixtures synthétiques et un témoin qui échoue si le lecteur tente une
   lecture interdite. Aucun test, import, Python ou CLI ne s'exécute dans le lot statique. Ne pas simplement
   ignorer ou exclure les contrats historiques pour faire passer les contrôles.
3. **Séparer les identités.** Conserver les huit empreintes historiques et les objets des deux commits comme
   références intactes. Tracer séparément tout patch technique d'entrée/tests et ses nouveaux hashes source.
   Les empreintes CSV/figures attendues par C3 restent inchangées. Aucun résultat divergent ne peut être réparé
   par un nouveau paramètre ou une nouvelle empreinte. C6/Wilson et tous les labels scientifiques restent intacts.
4. **Scinder les portes.** La dernière instruction limite les implémentations à E4 et 23 ; elle permet de
   préparer le code statique 23 avant la publication E4, après plan corrigé enregistré, GO technique écrit,
   sortie native officielle du mode plan et signal distinct. La reproduction scientifique, tous les tests,
   imports et sondes réelles restent derrière E4 clôturé/publié, réconciliation sur ce main et créneau Codex
   sous verrou. Le STOP disque E4 est actuellement actif ; aucune expérience 23 ne le contourne.
   Retirer le RED pytest du lot statique. Pour C1, Codex appliquera les deux commits historiques dans leur ordre
   dans le nouveau worktree ; Claude n'effectue aucune mutation Git. Décrire les patches ultérieurs séparément.

## Corrections de procédure

- Ordre de clôture : wrapup → réindexation → make check → commit → audit de publication → push contrôlé par
  Codex. Réconciliation/revalidation si main a avancé. Aucun push de branche par Claude.
- Contrôles globaux avec PATH de la .venv, environnement déterministe et torch du projet accessible ; gardes
  torch/PCA-G1 réellement exécutées. Ne pas modifier les dépendances.
- Nouvelle note DEVIATIONS en français ; texte historique conservé verbatim. Aucun registre global écrit par Claude.
- Corriger H2 : W23 documente jobs=1/48 ; le test tiny compare 1/2. Jobs=8 est un choix technique proposé,
  pas une reproduction déjà établie.
- Garder un périmètre minimal, sans nouveau registre, harmonisation Wilson, IC/deff D6, P4-D/P5-D ou J4.

Réviser le seul plan natif, puis le soumettre à Codex. Budget de révision : 20 minutes. Aucun code, test, lecture
de donnée, import, expérience, Git en écriture ou sortie du mode plan autorisé par le présent fichier.
