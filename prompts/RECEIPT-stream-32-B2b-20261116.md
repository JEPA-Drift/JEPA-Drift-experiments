# Stream 32 — réception B2b, univers et baselines spectrales

Date : 16 novembre 2026. Décision Codex : **B2b REÇU, NOYAU LIMITÉ**.
Autorité : GO B-TDD, plan v2.1 et réception B2a, empreintes vérifiées.
Reçu : spectral_baselines(lam,application), sans fit, cohorte ou campagne.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Univers et lignes de statut | ACCEPTED | RESIDUAL2..21, MARKET1..20, FULL_K limité à E ; CPV90 global jamais tronqué, OUTSIDE_UNIVERSE et UNSUPPORTED explicites. Références canoniques N32/N239 et entrée readonly. |
| EIGENMEAN de covariance | ACCEPTED | Moyenne exacte Fraction des doubles matérialisés, comparaison inclusive ; covariance distincte de Kaiser sur corrélation, constante non dyadique non vide sans epsilon ou repli. |
| Distinction CPV90 | ACCEPTED | Spectre complet pour CPV90, tranche E_res pour RESIDUAL_CPV90 ; rangs manuels et coupure dyadique confrontés au helper reçu. Aucun remplacement de convention. |
| Report du témoin constant | REJECTED | Entrée valide du noyau, donc défaut non reportable au fit. V1 non appliquée ; v2 ajoute seulement ce témoin aux onze cas conservés. |
| Finitude des éléments suffisante | REJECTED | GREEN initial264passés suspendu : trace pleine infinie possible malgré valeurs finies. EdgeRED intercepte deux appels CPV non protégés ; aucun faux rang effectivement calculé sous le spy. |
| Garde numérique | MODIFIED | Petit helper partagé vérifie sum fini et positif ET tous les préfixes cumsum finis, sous errstate local, avant chacun des deux appels CPV. Vecteur original inchangé ; aucune renormalisation, tolérance, coupure ou modification du producteur scellé. |
| TDD et préservation | ACCEPTED | EdgeRED2failed265passed9.28s, contrôle à grande trace finie passant ; EdgeGREEN267passed8.31s. Tests267cas inchangés pendant GREEN. Inversion exacte du patch restitue la source b4541836. |
| Contre-revue indépendante | ACCEPTED | Garde partagée, divergences possibles des arrondis sum/cumsum, statuts et comparaison Fraction relus ; acceptation limitée conditionnée à267passés et pyflakes propre, observés par Codex. Aucun test ou import par le relecteur. |
| Couverture numérique et coût | MODIFIED | Contrôle positif N32 à float64max/64, k90=29 et deux refus N239 couverts. Bord où sum et cumsum divergent de quelques ulp non témoigné ; les deux valeurs sont néanmoins contrôlées explicitement. Aucun coût runtime mesuré ou qualifié négligeable. |
| Réception globale | REJECTED | T22/T28/T35/T36 restent partiels ; identités de setup/politique, FITTED, familles, DEV, CAL, HOLD, ALT, HEAD et intégration encore dus. Aucune clôture B1/B ou ouverture de porte scientifique. |

Vérification réelle sous .venv, environnement déterministe et verrou partagé :
`-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short` :
**267passed en8.31s**, pytest/contrôles exit0, pyflakes et diff-check propres.
Les264cas précédents et le contrôle fini sont préservés ; aucune suppression ou réduction d'assertion.

| Pièce | SHA-256 |
|---|---|
| Source finale,69504octets | `b4d811c3c333ad39099ac8ccf20812ba8f4bf5755b9a945172c8d1c8b8801513` |
| Tests figés,183797octets | `33289a791fb82eeec0e803204935bdde5d9c822a2498be611d2616c181d16f69` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture EdgeRED complète | `a8290375a7731b0aa2604c4cb4a914fa54422e1b8dc8295a98c39e66b5cdcf70` |
| Capture EdgeGREEN complète | `5eca896960ea9d99e59003ab1cd14c60b39c092b833d7675dff63af92b7e8184` |
| Journal pytest EdgeGREEN | `e0d0fc9e8fbff86f9c4da75417a4a4ebcb4d1cac9adc9e7dcc124788ee772a32` |
| Journal contrôles EdgeGREEN | `fe248b0beb52919b4ff3cb2a56e8429543597ae3460a417d0849c3154b0c5283` |

Capture EdgeGREEN : exit0, erreur vide, success/is_error=false, même session PhaseB et
six empreintes de précondition conformes ; patch source seule lu/appliqué nativement.
Revue détaillée : REVIEW-stream-32-B2b-red-20261115.md ; preuves check/lot-B2b-edge-green.*.
Matrice exhaustive conservée :18PASS/0FAIL/50NOT_RUN ; aucun contrat partiel promu.

Suite bornée sous GO B existant : B2c, tests seuls des enveloppes nonoracle_masks/oracle_masks,
repli réservé à ONLINE et conservation des masques statiques. Pas de fit ni trajectoire générée.
T15 calcul/transmission du prior commun, T16 global/bundle, masques uint32, calendrier,
cohortes, CLI, consommation des graines, raccordements A et T68 restent bloquants.
CPU hors checkpoints/crash, borne externe, jointures workers/jobs, gardes du driver et
mémoire agrégée restent bloquants avant réception B ; aucun report implicite en C.
LotC/runtime/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
