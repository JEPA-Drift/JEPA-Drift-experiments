# Stream 32 — réception B2c, enveloppes de masques

Date : 16 novembre 2026. Décision Codex : **B2c REÇU, COMPOSANT PUR LIMITÉ**.
Autorité : GO B-TDD, plan v2.1 et réception B2b ; empreintes vérifiées.
Reçu : nonoracle_masks(Y,policy), oracle_masks(q_true,policy) et validation privée des clés.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Schéma exact | ACCEPTED | Dict et kind str validés, clés exactes par variante ; champs inconnus refusés sans lecture de leurs valeurs ni repr de la politique. Sept objets piégés et variantes croisées testés. |
| Non-oracle ONLINE | ACCEPTED | Délégation unique à online_masks reçu, arguments inchangés ; comparaison au noyau et à la référence scalaire, deux ordres/quatre coûts/trois fenêtres. Repli et causalité conservés. |
| Non-oracle STATIC | ACCEPTED | Masque ndarray bool(K,) non vide diffusé tel quel ; sélecteurs piégés, masque non contigu sans axe0 conservé sur Y nul/altéré, B0/H1/K1. |
| ORACLE | ACCEPTED | H entier Python/NumPy strictement positif, bool/flottant refusés ; best_sets reçu diffusé sur tout H dès t1, INFO/PREFIX confrontés aux références indépendantes. Ni ONLINE ni nouveau repli. |
| Préservation | ACCEPTED | Préfixe69504octets de source exactement conservé, append conforme à la capture ; tests289cas figés et producteur /2 inchangé. Aucun changement de noyau, import ou autre fichier applicatif. |
| Qualification des sorties | MODIFIED | STATIC et ORACLE renvoient des vues diffusées ; ONLINE renvoie le résultat du noyau. La phrase de capture prétendant toutes les sorties readonly est inexacte et n'est pas retenue ; aucun contrat de writeability des sorties n'est ajouté. |
| Réserve des refus | MODIFIED | Snapshots des politiques refusées vérifient l'identité de leurs valeurs, pas tout contenu mutable ; positifs readonly/contenus vérifiés. Pas de mutation dans le code reçu, mais aucune preuve universelle déduite des pièges. |
| Contre-revue indépendante | ACCEPTED | Aucun blocage concret sur clés, frontières et constance ; acceptation limitée sous289passés/pyflakes/diff propres, conditions observées par Codex. Aucune exécution ou mutation du relecteur. |
| Réception globale | REJECTED | Fabrique/identités des politiques, AST et appelants CAL/évaluation, simulateur et intégration restent dus ; T10/T22/T25/T38 gardent leurs raccordements ouverts. Aucun reçu B1/B ou nouveau GO scientifique. |

Sous .venv/environnement déterministe/verrou : RED **22failed267passed en11.63s**,
puis GREEN **289passed en8.48s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Les22nouveaux cas exercent désormais les assertions métier, sans aucun test affaibli.
Capture GREEN complète : exit0, erreur vide, success/is_error=false, session PhaseB existante,
six empreintes conformes ; patch source seule lu/appliqué avec outil natif après revue Codex.

| Pièce | SHA-256 |
|---|---|
| Source finale,71051octets | `12ec0c03bbd13f6388934ecf5950c7c2016dd6b66128e240b07d750f058a69d7` |
| Tests figés,194236octets | `d470886df77b6c4a0f1f5d582dd2d496fcd83f3cea1cff56aa6af7e0a2010cde` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète | `7556fe05774d419714edff02ad92c1bc205d311e611292499e5657b049afa1e1` |
| Journal pytest GREEN | `c7211e6f48953eeec59016b5a632afe7727085b9be1b2850c45adb8b5f9fcc98` |
| Journal contrôles GREEN | `a34d1fc6ebb0f9f3958deee70f4c2c6f4f83e0370870126c8b697ca5610b662a` |

Revue détaillée : REVIEW-stream-32-B2c-red-20261116.md ; preuves check/lot-B2c-green.*.
Matrice68 conservée :18PASS/0FAIL/50NOT_RUN ; composant reçu sans promotion des contrats partiels.
Suite bornée sous GO B : B2d tests seuls de géométrie des dérives population, supports et KL,
à partir de vecteurs de fixture fournis ; ni RNG nouveau, fit, cohorte ou injection de trajectoire.
API fonctionnelle minimale proposée dans la capture de tests, relue avant toute application.

T15 calcul/transmission s2 commun, T16 bundle réel/global, identités/calendrier, FITTED/DEV/HEAD,
CAL/NULL_PLAN/HOLD/ALT, uint32/CLI/cohortes/graines/A/T68 restent bloquants avant réception B.
CPU hors checkpoints/crash, borne externe, jointures workers/jobs, gardes driver et mémoire
agrégée restent bloquants ; aucun report implicite en C ni mesure runtime revendiquée.
LotC/runtime/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
