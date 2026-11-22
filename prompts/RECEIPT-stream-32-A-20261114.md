# Stream 32 — bilan des noyaux A

Date : 14 novembre 2026. Décision Codex : **A_KERNELS_RECEIVED**.
Base : e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a ; plan canonique v2.1 inchangé.
Pièces : réceptions A1, A2, A3a et A3b du même jour ; GO technique A limité au TDD.
Revue indépendante finale : aucun autre défaut matériel de noyau identifié ; garde des quatre quantiles présente avant dimensionnement.

Cette décision reçoit les noyaux numériques. Elle ne déclare pas une couverture intégrale de T1–T22
et n'active pas B. Le GO A prévoit que les refus de fit, schéma et orchestration restent à compléter enB.

| Contrat | Décision | État exact et obligations d'intégration |
|---|---|---|
| T1–T6 | ACCEPTED | M réemployé, OLS distinct de la corde, INFO/préfixes, égalités, exhaustif et refus de sélection ; débordements refusés. |
| T7–T9 | ACCEPTED | Passé strict, fenêtre glissante, tous les axes observés, références scalaires et invariance avant début. |
| T10 / wrappers §2.4 | MODIFIED | Repli online testé au noyau ; nonoracle_masks/oracle_masks et conservation des choix statiques/oracles restent dus avec les politiques B. |
| T11–T14 | ACCEPTED | Scan masqué complet, comptes par axe, absence de rescoring, premiers franchissements, comparaison scellée au même prior. |
| T15 | MODIFIED | Noyau conserve le s2 fourni ; B doit calculer/transmettre le même s2_common fondé sur K à toutes les politiques/cardinalités. |
| T16 | MODIFIED | Test encore absent : à exécuter sur les véritables colonnes et libellés exportés enB, sans constante inutilisée destinée à satisfaire un test. |
| T17–T19 | ACCEPTED | Tango/CP qualifiés techniquement ; référence T18 corrigée à tolérance conservée ; Tango reste asymptotique. |
| T19/T21 raccordements | MODIFIED | Échecs de conception/calibration, cohortes NULL_PLAN/HOLD indépendantes et n_hold figé avant HOLD restent dus enB. |
| T20–T21 noyaux | ACCEPTED | Espérance Fraction avant clipping, dimensionnement nul beta/2, cap/inconclusion, comptes appariés cohérents et JSON strict. |
| T22 | MODIFIED | Refus numériques couverts ; fit, valeurs propres, écart spectral, configuration et identités d'orchestration restent dus enB. |
| Couverture intégrale / clôture du stream | REJECTED | Aucun runtime, pilote, full ou résultat scientifique de campagne ; aucun lotB reçu. |

Les obligations ci-dessus restent **bloquantes pour la réception de B**. Elles ne sont ni supprimées ni transformées
en garanties obtenues par les seuls tests de noyaux. Les décisions scientifiques acceptées ne sont pas rouvertes.

Vérification finale ciblée : **45passés en1.36s** (36A,9R), pyflakes propre, diff-check propre.
Source SHA65a3bfb59bd50e51c6a9a8ebad6d719422e207a6b033d61d158035d719f3a44e ;
tests SHA99e3701ba9661e5bffb093cce2e2876d40200e002018ecac23575aa39aad5c75.
Le producteur28 conserve8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373.
Make check global reste dû avant commit. Aucun commit/push, campagne ou changement de dépendance.
Une activation écrite distincte reste nécessaire pour B ; aucun GO runtime/scientifique n'est déduit de ce bilan.
