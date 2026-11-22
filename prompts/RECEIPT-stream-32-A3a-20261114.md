# Stream 32 — réception technique A3a

Date : 14 novembre 2026. Décision Codex : **A3a ACCEPTÉ**, noyaux Tango/CP/statut nul uniquement.
Autorité : `GO-stream-32-A-20261114.md` ; plan canonique v2.1 inchangé.
Patches écrits par Claude Code, session PhaseB `e8ae637e-9cc7-4c82-a3c2-bec597e3ba23`,
relus et appliqués nativement par Codex. Aucune réception du lotA entier à ce stade.

## Observations et décisions

| Observation | Décision | Justification et tests |
|---|---|---|
| T17, EMV contraint et intervalles Tango | ACCEPTED | 108 cas contre minimisation numérique indépendante avec frontières incluses ; neuf intervalles historiques à tolérance absolue1e-12, symétrie et cas n=1. |
| Annulation de variance près de Δ0=-1 | MODIFIED | RED reproduit : une variance positive était arrondie à0, Z=-inf détruisait le bracket. Réécriture algébrique stable commune pour Δ0<0 ; contrôles, racines et tolérances conservés. Témoin de score fini et de signe correct à n=1/2000. |
| Littéral T18 historique à tolérance1e-15 | MODIFIED | Le littéral approché avait une erreur2.8359e-14. Remplacé par0.002857381614961041, qualifié indépendamment, avec1e-15 conservé. Les neuf références historiques et leur1e-12 restent inchangées. La forme fermée du plan est conservée. |
| T19, CP et statut à trois états | ACCEPTED | Bornes comparées à statsmodels ; les2001 comptes k=0..2000 donnent les statuts de référence ; 102 VALIDATED,103 INCONCLUSIVE et frontière FAILED vérifiés ; alpha+eps conserve son expression flottante. |
| T22, comptes/types/queues ; T2 garde OLS | ACCEPTED | Comptes et queues invalides refusés ; conversion des entiers NumPy avant soustraction ; garde OLS forcée par monkeypatch local, producteur28 intact. |
| Assertion que pytest.approx(abs=...) conserve rel=1e-6 | REJECTED | Le pytest installé retourne uniquement la tolérance absolue quand abs est explicite et rel absent ; constat retiré par le relecteur. Aucun test modifié pour ce motif. |
| Couverture finie de Tango | REJECTED | Qualification algorithmique uniquement ; Tango reste asymptotique, sans revendication de couverture finie. Les libellés sérialisés restent à vérifier lors du raccordement. |

La revue indépendante confirme les domaines des comptes/queues et la correction minimale de variance.
Le discriminant matériellement négatif est refusé ; seul un négatif compatible avec1e-12 de la somme des termes est
ramené à0. La faisabilité de q accepte au plus1e-12 d'arrondi avant projection ; sinon ArithmeticError.
La variance positive, même petite, est conservée. La branche de variance nulle retourne0 ou l'infini signé, jamais NaN.
Les crochets de racines restent dans l'intervalle ouvert via nextafter lorsque la différence observée vaut±1.

## Résultats observés

- RED initial :4échecs explicites,34passés en1.27s ; le nouveau témoin OLS passe déjà.
- GREEN initial refusé :2échecs,36passés en1.42s ; aucune réception sur ce résultat.
- RED de borne après correction qualifiée du littéral :2échecs,37passés en1.47s.
- GREEN final sous .venv, environnement déterministe et verrou partagé : **39passés en1.34s** (30A,9R), sans skip.
- pyflakes ciblé et git diff--check : exit0. Tests inchangés entre RED de borne et GREEN final.
- Qualification indépendante : norm.isf et NormalDist.inv_cdf donnent des demi-largeurs distantes de2.1684e-18 ;
  erfc contrôle la queue. Ce contrôle déterministe est une fixture technique, pas une campagne scientifique.

| Pièce | SHA-256 |
|---|---|
| experiments/pca_info_online.py | `014053d6f013d7e174c6fc2a266cfeeb380fdb09d854dc3e3bed15f406b0ebc3` |
| tests/test_pca_info_online.py | `ef98a6307888b868b0d964cdebe59100ddb999120927a32bd45aab71686f8c29` |
| experiments/pca_drift_benchmark.py | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| logs/stream-32/lot-A3a-reference-qualification.json | `2a6edf0818f1d91e208a3ac28de65ba89d86c964a33e6d3087b096a32b2f7d88` |
| logs/stream-32/lot-A3a-repair-red-pytest.log | `5957d22919e248c08db67568f996fcadb13f12accef6601a4f9ead3c0fc3cfeb` |
| logs/stream-32/lot-A3a-repair-green-checks.log | `a65167ed082058505d387ada84c5251d04dbac6c915f01c7d90db29afb5f7eb3` |
| logs/stream-32/phase-b-A3a-repair-green.raw.json | `6a10584e0744267d4acb2e2d8606c533d250c833f0c792aea18743364156c943` |

Captures appliquées complètes, exit0/is_error=false, sans erreur ni refus de permission.
T16, T20/T21 et refus/raccordements restants restent dus. Prochaine étape : tests RED T20/T21 uniquement.
Make check global reste dû avant commit ; aucun commit/push ni producteur scellé modifié.
LotB, runtime, smoke, pilote/full et autres streams restent fermés.
