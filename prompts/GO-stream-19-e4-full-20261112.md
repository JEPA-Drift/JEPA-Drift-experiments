# Décision du chercheur — E4 production et full conditionnel, 2026-11-12

**Provenance.** Décision explicite du chercheur dans la conversation Codex, intitulée « DÉCISION DU CHERCHEUR — E4 FULL
ET CONTINUATION PARALLÈLE », après réception du rapport `docs/audits/stream_19_e4_cost_pilot_20261112.md`. Transcription
opérationnelle par Codex, sans signature ajoutée ni délégation scientifique inventée. Référence Git fournie par le
chercheur : `main` à `b18d8e5b01706bcb3dea8268c93fc0b9c361e441`.

Le chercheur valide la réception et la traçabilité du pilote. Les 8,837424 CPU-heures sont une prévision conditionnelle,
pas une garantie. Cette décision succède aux GO de protocole et de prototype ; les clauses historiques interdisant le
full restent applicables par défaut tant que les conditions d'activation ci-dessous ne sont pas effectivement levées.

## GO 1 — Ingénierie de production accordée

Autorisation de finaliser l'infrastructure de la campagne E4, sans modifier le protocole scientifique :

1. Blocs bornés de réplicats, reprise idempotente, écritures atomiques, identité contrôlée et partitions divergentes refusées.
2. Fusion déterministe et export FAIR des statistiques scientifiques.
3. Tables incrémentales, dont J_k (jusqu'à 3 948 000 lignes) et essais (jusqu'à 672 000), sans chargement global non borné.
4. Politique de stockage explicite : SHA-256, schémas et manifestes conservés ; aucun fichier de plus de 50 Mo commité ;
   aucune perte silencieuse. Le stockage et les temporaires entrent dans le bilan technique.
5. Tests sur fixtures : interruptions/reprises, divergences, blocs manquants, frontières de réplicats, agrégations et
   reproductibilité jobs=1/jobs=3.
6. Nouveau pilote exclusivement technique couvrant partitionnement, sérialisation, fusion et reprise. Aucune performance
   de détection du pilote ne sera inspectée ou utilisée pour changer le protocole.
7. Bilan actualisé du CPU cumulé, du RSS, du disque et des risques résiduels.

Le cycle reste : plan natif dans Claude Code interactif, revue Codex, plan canonique enregistré et GO technique écrit,
sortie officielle du mode plan, signal distinct, implémentation TDD, réception et vérification. Le présent GO 1 ne
dispense pas de cette revue. Codex tranche les décisions ordinaires d'ingénierie dans ce périmètre sans nouvelle question.

## GO 2 — Exécution scientifique distincte, accordée sous conditions bloquantes

Le chercheur accorde maintenant l'autorisation scientifique distincte de la campagne full. **État initial : NON ACTIVÉ.**
L'activation explicite par Codex exige simultanément :

- réussite documentée de tous les contrôles du GO 1, dont les tests, le pilote technique et les contrôles de non-fuite ;
- prévision CPU actualisée dans le plafond cumulé de 24 CPU-heures, pilote antérieur déjà consommé inclus ;
- contrôle final de l'identité du protocole, des sources, de la configuration, des versions et des graines ;
- preuves et commande d'activation explicites, traçables ; refus par défaut sans cette activation.

Ces conditions satisfaites, Codex peut lancer toute la grille sans redemander une validation purement technique. Un
simple fichier GO présent ou une alerte de supervision ne constitue pas la preuve que ces conditions sont satisfaites.
Le rapport et la trace d'activation doivent citer les empreintes des preuves effectivement reçues.

## Protocole scientifique inchangé

- N = {8,16,32,64,128,239,500}, fonds Gaussian équicorrélé et t7, rho=0,4.
- H=2000, alpha=0,05, I* fixé par ln(H/alpha)/I*=H/40 ; amplitude résiduelle isotrope orthogonale au marché inchangée.
- T_fit=n_cal=n_hold=n_alt=B_boot=2000, seed 42.
- EW, SPEC-prefix8, SPEC-full, P3-CS(b), O-dir et O-score1 ; les deux dernières restent ORACLE.
- Lecture principale predictive-rank ; secondaire anytime-valid ; calibration scalaire commune, seuil gelé et règles
  d'appariement inchangés. Fit, calibration, holdout, alternative et pilote restent dans leurs domaines distincts.
- Conventions spectrales, tolérance et refus des bases non identifiables du protocole déjà approuvé conservés.
- Qualification Wilson par borne inférieure >=0,95 sur toute la grille de chaque contraste ; inférence conditionnelle
  aux fits et calibrations, bootstrap apparié, sans rééchantillonnage externe des fits.
- I* reste `INFO_GAUSS_PROXY_T7` pour t7, jamais un KL t7 ; Delta=Delta_1+Delta_2 reste descriptif.
- Aucune adaptation post hoc de I*, de la grille, des critères statistiques, de qualification ou de cohorte.

Sources de référence : protocole §12 et GO scientifique antérieur `prompts/GO-stream-19-e4-science-20261112.md`.
Configuration de référence `configs/e4_alignment.yaml`, SHA-256
`5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2`.
Producteur du prototype `experiments/e4_alignment.py`, SHA-256
`e457ebae9011a5f1d1b0b9bc43d38f2ab97a70bccd64069dba07ad51996efd01`.
Rapport du pilote SHA-256 `b31ff72ad67d2814871a331cbed1996d788e1b6247feb004e20151493917a115`.
Coût antérieur mesuré à reporter dans le compteur cumulé : 645,23 secondes CPU.

## Limites et arrêts

Verrou d'exécution partagé existant ; 8 Gio de RSS, 30 minutes par invocation et plafond cumulé de 24 CPU-heures.
Les replis restent documentés dans l'ordre approuvé, sans application automatique : retirer N=500, puis t7 sur
{8,64,239}, puis STOP. Un dépassement prévu, un contrôle bloquant échoué ou un besoin de modification scientifique
impose STOP, rapport motivé et retour au chercheur. Aucun repli pour améliorer les résultats.

La censure aux dimensions 239 et 500 est rapportée telle quelle. `NOT_IDENTIFIED` est recevable ; ce statut ne justifie
aucun recalage. Toutes les cellules et leurs statuts sont conservés, avec les deux lectures distinctes : FPR holdout,
RMST, détection, bootstrap apparié, Wilson et contrastes Delta/Delta_1/Delta_2 sur la grille entière. Publier les
`FPR_ABOVE_NOMINAL`, refus de base et autres qualifications applicables sans exclusion opportuniste.

Séparer MESURÉ, THÉORIQUE et limites non résolues. Conserver configurations, versions, graines, partitions, commandes,
résultats et hashes. Aucun accès financier réel, privé ou 2020+, J4/FROZEN, JEPA/VAE ni modification des scellés E2,
E3/D8 et PCA pour ce lot. Une rupture de reproduction ne se corrige pas en ajustant source ou paramètres pour forcer PASS.

## Clôture et suite

Après campagne : rapport scientifique et artefacts, wrapup, réindexation autorisée sans résumé IA, tests, audit de plage,
commit/push contrôlé. E4 est clos seulement après publication de ses résultats ou documentation formelle d'un arrêt.
Ne pas déclarer tout le stream 19 historique achevé. La vague parallèle 23/E6 phase 1 et 27/E10-F2 ne démarre qu'après
clôture réussie d'E4, selon `prompts/GO-wave-23-27-after-e4-20261112.md`.
