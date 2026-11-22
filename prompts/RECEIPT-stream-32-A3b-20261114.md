# Stream 32 — réception technique A3b

Date : 14 novembre 2026. Décision Codex : **A3b ACCEPTÉ**, biais de score et dimensionnement nul uniquement.
Autorité : `GO-stream-32-A-20261114.md` ; plan canonique v2.1 inchangé.
Claude Code reste l'auteur, session PhaseB `e8ae637e-9cc7-4c82-a3c2-bec597e3ba23`.
Codex a lu les captures complètes, relu puis appliqué les patches nativement.

## Observations et décisions

| Observation | Décision | Justification et tests |
|---|---|---|
| T20, espérance avant écrêtage | ACCEPTED | Énumération exacte Fraction de cinq lois à trois points pour m=1/2/3 ; moyennes décalées, variances inférieure/supérieure à1 et nulle ; valeurs négatives conservées ; diagnostic scalaire et vectoriel. |
| Première fixture de comptes appariés | REJECTED | b60/c20 avec10 alarmes par politique est impossible ; le premier patch n'a jamais été appliqué. |
| Cohérence des comptes | MODIFIED | Fixture corrigée : kINFO60,kPREFIX=kFULL20, joint0/neither1920. Contrôles des marges, intersection, aucune alarme et références A|B ; refus ciblés indépendants. |
| T21, dimensionnement | ACCEPTED | Référence CP indépendante et Tango qualifié ; beta/2, hausse stricte non plafonnée, plancher, cap et égalité n_req=n_cap ; aucune modification de la marge pour réussir. |
| Détails sérialisables | MODIFIED | Exigences inatteignables représentées par None. RED supplémentaire sur alpha/m ou beta/2 sous-fluant à0 ; garde des quatre quantiles finis avant dimensionnement. JSON strict des cas valides conservé. |
| Puissance familiale ou couverture finie | REJECTED | Témoins de puissance normale par contraste seulement ; aucune simulation de puissance ni garantie familiale. |

La revue indépendante confirme les formules, le diagnostic non écrêté, la validation de cohorte et les types natifs.
Sa réserve sur les quantiles est levée par deux témoins RED puis la garde commune.
Le diagnostic c/var0 reste séparé des entrées ONLINE. Aucune génération NULL_PLAN/HOLD/ALT n'est ajoutée.

## Résultats observés

- RED v2 :4échecs explicites,39passés en1.54s, avant les deux noyaux.
- GREEN initial :43passés en1.33s ; réception différée pour la limite numérique des quantiles.
- RED complémentaire :2échecs explicites,43passés en1.50s.
- GREEN final sous .venv, environnement déterministe et verrou partagé : **45passés en1.36s** (36A,9R), sans skip.
- pyflakes ciblé et git diff--check : exit0 ; tests inchangés entre RED complémentaire et GREEN final.
- Producteur stream28 inchangé ; aucun producteur scientifique scellé modifié.

| Pièce | SHA-256 |
|---|---|
| experiments/pca_info_online.py | `65a3bfb59bd50e51c6a9a8ebad6d719422e207a6b033d61d158035d719f3a44e` |
| tests/test_pca_info_online.py | `99e3701ba9661e5bffb093cce2e2876d40200e002018ecac23575aa39aad5c75` |
| experiments/pca_drift_benchmark.py | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| logs/stream-32/lot-A3b-red-v2-pytest.log | `8ff154f64eef081e443b37a0aad37c9e1b61620bc2c89bca728361410b34ecd2` |
| logs/stream-32/lot-A3b-edge-red-pytest.log | `1df33e59813b6fb4502d1c67c0280080531888741d05632014ba1f52d9a5ab30` |
| logs/stream-32/lot-A3b-edge-green-checks.log | `5dc922832fd60bb5733a6a21168fbad5cfabd22579d4660d67269aafaaf6894c` |
| logs/stream-32/phase-b-A3b-edge-green.raw.json | `327de944ca032d31fddb266fde3bad06946fdbca7fda239a0d33d8606b433607` |

Captures appliquées complètes, exit0/is_error=false, sans erreur ni refus de permission.
Bilan A distinct : noyaux reçus, obligations d'intégration T16 et autres raccordements encore dus.
Make check global reste dû avant commit ; aucun commit/push.
LotB, runtime, smoke, pilote/full et autres streams restent fermés par cette réception.
