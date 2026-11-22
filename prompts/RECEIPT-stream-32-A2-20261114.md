# Stream 32 — réception technique A2

Date : 14 novembre 2026. Décision Codex : **A2 ACCEPTÉ**, noyaux causaux et scan uniquement.
Autorité : `GO-stream-32-A-20261114.md` ; plan canonique v2.1 inchangé.
Claude Code reste l'auteur dans la session PhaseB `e8ae637e-9cc7-4c82-a3c2-bec597e3ba23`.
Codex a lu les captures complètes, relu puis appliqué les patches avec apply_patch.

## Revue et corrections

| Observation | Décision | Justification et témoins |
|---|---|---|
| T7–T9, sélection avant observation | ACCEPTED | Perturbations présentes/futures et changements de début/direction ; référence scalaire indépendante sur le passé strict de tous les axes, fenêtres 1/3/>H, deux ordres et quatre coûts. |
| T10, repli online | ACCEPTED | Premier pas, historique nul et score entièrement nul donnent l'axe canonique0 ; le choix best_sets sur q oracle non nul est conservé. Raccordement des politiques complet à vérifier enB. |
| T11–T14, vraisemblance masquée | ACCEPTED | Égalité au scan scellé pour masque constant, référence exhaustive math.fsum, départ ancien gagnant, comptes nuls, entrée d'axe sans rescoring, élagage et premiers franchissements 1-based avec règle >=. |
| T15, prior commun au noyau | ACCEPTED | Le s2 fourni reste identique aux différentes cardinalités et après élagage ; le test distingue une variante le recalculant depuis d. Raccordement des politiques à vérifier enB. |
| Entier non signé accepté puis indices flottants | MODIFIED | La revue indépendante a identifié np.uint64(3). RED reproduit avant correction ; conversion en entier Python et borne H avant np.minimum, sans changement de la fenêtre configurée. UInt64 maximal et entier Python2**80 couverts. |
| Réception de tout le lot A | REJECTED | T16, statistiques T17–T21 et refus restants sont encore dus. A2 ne reçoit aucune orchestration expérimentale. |

La revue indépendante ne relève aucun autre défaut matériel : masques historiques figés, tous les départs τ,
W négatif conservé, masques entièrement faux acceptés, s2 fourni inchangé. H=1, K=1 et B=0 sont cohérents par inspection.
La seule réserve est levée par le RED/GREEN sur les fenêtres entières.

## Vérifications observées

- RED A2 : **11 échecs explicites**, 21 tests passés en1.28s, avant ajout des noyaux.
- GREEN initial :32passés en1.11s ; pyflakes propre ; tests inchangés.
- RED complémentaire :1échec,32passés en1.19s ; IndexError reproduit avec np.uint64(3).
- GREEN final sous .venv, environnement déterministe et verrou partagé : **33passés en1.08s** (24A,9R), sans skip.
- pyflakes ciblé et git diff--check : exit0 ; tests inchangés entre RED complémentaire et GREEN final.
- Producteur stream28 inchangé ; aucun producteur scientifique scellé modifié.

| Pièce | SHA-256 |
|---|---|
| experiments/pca_info_online.py | `309489663fbdf18e561316e5bbcddde96a24a412e6d348a32d77b242dd7babf3` |
| tests/test_pca_info_online.py | `bd3d3898d5db5d9149c5aeab88db1a520199e0339412ca46fb63101dd2553fea` |
| experiments/pca_drift_benchmark.py | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| logs/stream-32/lot-A2-red-pytest.log | `22bc1070419c95a72934d12fe4cda91a655c0492c4dc5093b05d17b878b2e88e` |
| logs/stream-32/lot-A2-edge-red-pytest.log | `8dde610da24a8c4b386c003eee753ec4d03c99fa3a1d7873de241b1a78b8c703` |
| logs/stream-32/lot-A2-edge-green-checks.log | `f5fef294046916de276a8fd69827be15a6eb750129f89f23e6a8492f51e86c70` |
| logs/stream-32/phase-b-A2-edge-green.raw.json | `27d07b87d789a0905fad20ef2212cf5fec0209b36cc593904b4851c88d2b8ba0` |

Captures GREEN complètes : exit0, is_error=false, aucune erreur ni refus de permission.
Prochaine étape : proposition de tests RED A3 statistiques, par sous-lots bornés.
Le lotA entier reste ouvert ; make check global reste dû avant commit. Aucun commit/push.
LotB, runtime, smoke, pilote/full et autres streams restent fermés.
