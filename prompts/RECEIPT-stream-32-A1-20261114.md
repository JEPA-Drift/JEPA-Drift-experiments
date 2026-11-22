# Stream 32 — réception technique A1

Date : 14 novembre 2026. Décision Codex : **A1 ACCEPTÉ**, périmètre coûts et sélection uniquement.
Autorité : `GO-stream-32-A-20261114.md` ; plan canonique v2.1 inchangé.
Claude Code est l'auteur des patches, dans la session PhaseB
`e8ae637e-9cc7-4c82-a3c2-bec597e3ba23`. Codex les a relus et appliqués avec apply_patch.

## Revue et corrections

| Observation | Décision | Justification et témoins |
|---|---|---|
| Réemploi M, OLS 1..min(16,K), coûts et argmax | ACCEPTED | T1–T6 : alias identique, OLS indépendant de la corde scellée, références exhaustive/gloutonne/préfixe, égalités et optimum tardif. |
| Débordement de `cumsum(q)/cost` malgré des entrées finies | MODIFIED | RED additionnel observé avant correction ; garde locale `np.errstate` commune aux deux ordres, cumul et quotient. Les entrées extrêmes lèvent ArithmeticError. |
| Dimension triviale | ACCEPTED | K=1 accepté pour best_sets, q nul et positif, INFO/PREFIX ; OLS à moins de deux points refusé. |
| Réception du lot A entier à ce stade | REJECTED | A2/A3 et les autres refus T22 restent dus ; A1 ne couvre ni causalité, ni scan, ni statistiques. |

La revue indépendante en lecture seule n'a identifié aucun autre défaut matériel A1.
Sa réserve sur les débordements du cumul et du quotient est levée par le RED/GREEN complémentaire.
Le tri stable impose l'indice canonique aux égalités de q ; argmax retient le plus petit d ; PREFIX énumère tout K.

## Vérifications observées

- RED initial : 11 échecs explicites pour module absent, 9 tests R passés, avant tout noyau A1.
- GREEN initial : 20 tests passés, pyflakes propre.
- RED complémentaire : 1 échec attendu, 20 passés en 1.13s ; ArithmeticError absent et avertissement de débordement.
- GREEN final sous .venv, environnement déterministe et verrou partagé : **21 passés en 1.03s**, sans skip.
- pyflakes ciblé et `git diff --check` : exit0 ; tests inchangés entre RED complémentaire et GREEN final.
- Producteur stream28 inchangé. Aucun autre producteur scientifique scellé modifié.

| Pièce | SHA-256 |
|---|---|
| experiments/pca_info_online.py | `da70818bb79320cd7bc7313c3343ca59b04e9a4019523da69ef5265b72ee1fd8` |
| tests/test_pca_info_online.py | `ea9d83053340015316ef9c3d63b7f8804b601018c9377331ea682db23ce89b95` |
| experiments/pca_drift_benchmark.py | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| logs/stream-32/lot-A1-edge-red-pytest.log | `e9e80d61fe66cbf76d248aca65f8e134a3d9f9fc343fe26de9590dfad7b16d6b` |
| logs/stream-32/lot-A1-edge-green-checks.log | `5ecb7233e586d333b1d41b3baa7ef404504a412d8c902c41f23158efdd97c86e` |
| logs/stream-32/phase-b-A1-edge-green.raw.json | `da58e2e56b72ee0ffd95f6b74958ebdf4160df10a362ddc37048717fa339ff3b` |

Les captures GREEN sont complètes, exit0, is_error=false, sans erreur ni refus de permission.
`make check` global reste à exécuter avant tout commit ; aucun commit/push ici.
Étape suivante limitée à la proposition de tests RED A2 causaux/scan. LotB, runtime, smoke, pilote/full et autres streams fermés.
