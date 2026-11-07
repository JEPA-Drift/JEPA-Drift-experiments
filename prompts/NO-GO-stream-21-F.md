# Revue Codex du plan 21-F — révision 0

Date : 7 novembre 2026. Autorité : revue technique Codex au titre du mandat délégué. Aucun GO d'implémentation ni signature du chercheur.

Base : `47d85dc977547409fc6f6d71dcf5488eb935d7d5`, branche `stream-21-F`. Proposition native : 484 lignes, SHA-256 `fbb35ca8257c0244f41bb006a9c37f8941b46dc438c0b0cc1272ea4348e04477`.

**NO-GO technique sur la révision 0 ; poursuivre la planification dans la même session Opus 5.5/Max, sans code ni tests.**

1. **Présence des racines.** Le §4.3 permet de figer une racine absente sans enregistrer explicitement son absence. Cela permettrait un succès sans manifeste de données, sans outil ou sans code requis. Les onze racines de POLICY doivent être présentes dans C et sur disque, avec leur type attendu ; les trois racines-répertoires doivent contenir au moins un fichier couvert. Ajouter les témoins correspondants avant C et après S, et un refus sans création par `write`.
2. **Création concurrente.** W1 préexistant est refusé avant `os.open` et ne suffit donc pas à tuer le mutant supprimant O_EXCL. Ajouter une insertion de fichier entre la dernière vérification d'absence et l'ouverture créatrice : EXISTS, octets et inode étrangers intacts, aucun nettoyage du fichier étranger. Ajouter aussi le témoin d'échec de fsync après substitution du nom par un inode étranger, afin de vérifier le nettoyage annoncé. Les courses de substitutions après la dernière vérification d'inode restent une limite POSIX explicite ; ne pas promettre une suppression conditionnelle atomique.
3. **Validation des chemins possédés.** Le §7 doit autoriser explicitement les nouveaux plan, GO, présente revue et rapport de Codex, sans les modifier ; le wrapup ne rejoint l'ensemble attendu qu'après son créneau de clôture. Ne pas rejeter ces fichiers légitimes ni élargir arbitrairement la liste.
4. **RED exploitable.** Le premier RED doit atteindre une assertion de comportement sur une fixture construite indépendamment des fonctions encore absentes, sans erreurs de collection ou de fixture en cascade. Une erreur de syntaxe ou de montage n'est pas une preuve RED. Les cas restants restent des exigences de comportement ; aucune implémentation n'est autorisée maintenant.
5. **Gel unique.** La règle interdisant tout FROZEN dans l'histoire de C rend ce schéma à usage unique sur une lignée. Le préciser ; une nouvelle autorisation ne suffit pas à permettre un regel avec le même vérificateur. La future activation et toute évolution de schéma demanderont un autre plan/GO.

Les autres choix bornés sont recevables : table SHA-256 de tous les fichiers couverts, manifeste haché sans lecture des données, approbation comme provenance, ouvertures par descripteurs, refus par commit et histoire linéaire, codes 0/1/2, gardes fixtures, aucun câblage J4. Les choix proposés ne constituent pas un protocole expérimental approuvé.

Claude corrige seulement les sections et témoins concernés dans son plan natif, indique son nouveau SHA-256 et reste en mode plan. Codex enregistrera ensuite le plan canonique avec sa décision GO intégrée et un GO séparé, avant toute implémentation.
