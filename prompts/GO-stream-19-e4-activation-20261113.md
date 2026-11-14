# GO Codex — activation scientifique E4, 13 novembre 2026

Autorité : GO 2 conditionnel du chercheur, `prompts/GO-stream-19-e4-full-20261112.md`, SHA-256
`19d2697700bc9a0af5d98c9bd7c901129450aed385487582ef67c3f17e094746`, puis instruction explicite du chercheur
de libérer le disque et lancer E4 au plus vite. Le GO scientifique existe déjà ; aucune nouvelle convention n'est prise.

## Levée du STOP disque et conditions techniques

Le STOP historique `STOP-stream-19-e4-disk-20261113.md` est conservé intact. Nouvelle mesure shell sur `/dev/md1` :
**26 862 768 128 octets disponibles**, au-dessus des **1 512 808 090 octets requis**, empreinte et réserve comprises.
Le programme d'activation mesurera de nouveau le disque avant d'écrire son enregistrement.

Les deux réceptions correctives et la revue finale indépendante reçoivent les contrôles GO 1. R0007 : 155 PASS,
sans échec ni skip ; R0009 : 37 + 1 308 PASS et cinq seuls skips D4, torch et PCA/G1 exécutés. Aucun code n'a changé
depuis ces contrôles. P1 : neuf appels réels de coût ; P2 : 354 partitions, interruption/recalcul, reprise, refus,
trois rejeux identiques, publication et audit autonome. Aucun résultat de détection du pilote n'a guidé un choix.

Preuves finales : `results/e4_alignment/production_pilot_20261113/final1/{report,receipts,evidence}`.
Manifest SHA-256 `ccf1527c520cf7d986cfe7a34f3ff3fa6b3f752e4aa2716b0fe9eda12dde1c6d` ; prévision
`4c826ae14a81e1a93ac296918ee66c255dd6ccdd5db80da06e4727a2cbd9ec28`. Les trois contrôles evidence-cost passent
sous une seconde, borne de contrôle 60 s, volume 1 000 tentatives. Identité attendue :
`6d1acbd629975285acc7df37cb3d02e5daf5f0b7339473af78d02757ef6066af`.

Au cutoff A0000389 : 2 997,75 CPU s cumulées, pilote antérieur et imports inclus. Prévision avec cette queue :
57 287,7895905 CPU s, sous 86 400 s. La queue d'activation et tous les appels futurs sont comptés par le registre.
Les hypothèses de transfert, pics non observés et bookkeeping XML inconnu restent explicites dans le rapport technique.

Sources vérifiées inchangées : runner `402d23bf09a76c51f9dbcddaf4cd5edb3cbc476b14b42685871502e8b0826980`, tests
`d75d4350f0a3296605eec764169c28d860ce034ea14b427f6d5a373799008e79`, driver
`3ed5b9920dd3cb076369a55e1f532ffd4cdfbdf452d2cb3a7c535c837ace4af8`, configuration
`5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2`. Protocole, graines et critères inchangés.

## Activation et exécution autorisées

Codex autorise maintenant la commande explicite `--phase activate --mode full`, avec ces preuves et ce GO.
Seul son succès crée `logs/stream_19_e4_production/activation-full-20261113.json` et permet la campagne.
Puis `tools/run_e4_production.sh campaign full` : blocs de 250, grille complète préspécifiée, .venv et environnement
déterministe, un processus, verrou partagé, 8 Gio, 30 minutes par invocation et 24 CPU-heures cumulées.
Racine de travail : `logs/stream_19_e4_production/full_20261113` ; publication : `results/e4_alignment/full_20261113`.
L'audit autonome et le reçu comptable terminal suivent la publication. Toute condition bloquante échouée impose
STOP et retour au chercheur ; aucun repli automatique, changement de I*, seuil, grille ou critères statistiques.

Toutes les cellules/statuts, censure, FPR et lectures restent publiés. Aucun accès réel, privé ou 2020+, J4 ou JEPA.
Les expériences 23/27 attendent toujours la clôture scientifique réussie d'E4 ; les implémentations restent limitées
à E4 et 23. Aucune autre tâche numérique concurrente ni modification des sources pendant cette campagne.
