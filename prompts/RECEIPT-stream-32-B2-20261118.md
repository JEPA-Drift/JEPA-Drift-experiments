# Stream 32 — réception complète du lot B2

18 novembre 2026. Décision Codex distincte. **B2 COMPLET REÇU SUR FIXTURES**, sous le GO
`B_TDD_ONLY`. L'autorité reste le plan v2.1 et le GO B du 14 novembre.

| Périmètre reçu | Décision | Preuves et réserves |
| --- | --- | --- |
| Repère, spectres, projections et HEAD | ACCEPTED | B2a–B2i. Univers fixes, contrôles EIGENMEAN/CPV, KL population et FITTED, géométrie HEAD et fit sur tableaux fournis. La détectabilité et les portes d'inférence restent à B3. |
| Clés, trajectoires et SETUP | ACCEPTED | B2j–B2o. EXACT 21 axes, bruit FITTED gaussien/T7, méta séparée, injection en retours et cache SETUP avec moyenne apprise. T7 étiqueté GAUSSIAN_PROXY pour les diagnostics concernés. |
| Bibliothèque, politiques et choix DEV | ACCEPTED | B2p–B2v. qbar poolé sur les quatre familles, calibrations DEV GE au même alpha nominal, RMST pondéré, égalités déterministes. Prior commun, masques, statuts spectraux et recettes de sensibilité reçus. |
| Contrôleur et gel DEV | ACCEPTED | B2w lie les NPZ, les choix et les identités à SETUP. L'ordre, le budget aux checkpoints, l'écriture atomique et la reprise isolée ont été testés. Identités primaires réutilisées quand s2_dev égale le prior commun. |
| Matrice globale | MODIFIED | T33, T37 et T51 passent. T34 conserve la preuve du policy_id et attend le calibration_id final. T41 conserve les preuves SETUP/DEV et attend la consommation des autres rôles. Les 68 lignes restent ordonnées, 21 PASS et 47 NOT_RUN. |
| Portes suivantes | REJECTED | Cette réception ne lance aucun lot. B3/B4 restent à la prochaine instance sous le GO B après vérification locale. C, runtime, campagne smoke, pilote et full gardent leurs décisions distinctes. |

C0 sous .venv, environnement verrouillé et variables déterministes. **840 passés en 19,85 s**,
pytest exit 0, pyflakes et diff-check propres. Le contrôle direct des diagnostics stockés
confirme un rang non nul valide et trois refus. Les 806 anciens cas ont été conservés octet
pour octet. Les ajouts groupés B2w ont renforcé des assertions sans retirer de cas.

| Pièce | SHA-256 |
| --- | --- |
| Source finale `experiments/pca_info_online.py` | `936afa0c13b59bb59d63591b5309c1b582a9b2594668b897a63e906021cb387d` |
| Tests `tests/test_pca_info_online.py` | `73e931a1030a1587012d6b660a1b2b41a25d19e4da85f1d754c81ac51dbb4f59` |
| Producteur scellé `experiments/pca_drift_benchmark.py` | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Réception B2w | `2cb804e2f1d14fc72e00a5bcb642a7c8f4f28e0ec98b5e80999b5f4776d67059` |
| Revue GREEN finale B2w | `92eb8a3966e2eab57c29b5a12b1df3c5c23346b56b78a3612085b5027adc349b` |
| Matrice T1–T68 | `da6c0ba56658359878ac76ec5fad5020f89ac59112ca4455a111379f40538acb` |
| `logs/stream-32/lot-B2w-green-final.pytest.log` | `42b921730fe7dbca3e6145147ac65d73b733216b27cb56e2c3f15641039119d0` |
| `logs/stream-32/lot-B2w-green-final.checks.log` | `6606347f99d1df1cb3b71805a0066cd8e150d14c957efe17b532064478d894ed` |

La réception B couvre encore à terme les raccordements T10, T15, T16, T19, T21 et T22,
les statuts et seuils finaux, l'export FAIR de bout en bout, le CLI, les ressources hors
checkpoints et T68. La campagne reste fermée. Le worktree conserve les changements locaux
et le journal de preuves. Arrêt de cette instance à B2 et reprise par le prompt dédié.
