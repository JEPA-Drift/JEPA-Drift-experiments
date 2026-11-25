# Projet de décision T7_RUNTIME_GO v2 — qualification Stream 32 Student-t7

NO_RUNTIME_GO

Projet soumis au chercheur. La portée proposée est `qualification/smoke`, cas `continuous`, `jobs=1`, par reprise du registre apuré après réconciliation écrite du jeton.

| Champ | Valeur proposée |
| --- | --- |
| `stage` | `qualification` |
| `mode` | `smoke` |
| `design_id` | `a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804` |
| `seed_plan_sha256` | `5bdb1b70b5253c1e16eb14017621e2ff4ae327b00142072bc22c8edb450994e7` |
| `approval_sha256` | `9dff9191614fa268ed77dd98880a6bde994f4642f99dca314b8befe8573d3673` |
| SHA-256 du superviseur A2 | `6dff87b497882aa1b7783394d5119986091c6e5433675d84f66061d8a773ff5b` |
| Jeton précédent | `0958186bcdfb4072b2e6cc51b1831d49` |

L’enveloppe conserve 8 Gio, 2 h de CPU cumulées, 900 s par invocation, `jobs_max=2` et un seul CPU logique par unité. Sur cet hôte, le contrôle repose sur l’affinité et le refus effectif de `sched_setaffinity` par `EPERM`. Le lanceur vérifie aussi `cpu.max` quand le contrôleur `cpu` est disponible. Le calcul demeure sous verrou partagé. Les témoins ALT portent `SMOKE_NO_CLAIMS`.

Le premier démarrage régi par ce projet est la reprise de `continuous`. Le plan technique de qualification conserve le cas `resumed`, dont l’exécution attend une décision écrite distincte. Le Pilote et le Full restent soumis à leurs propres décisions.

Après décision écrite, créer le GO actif avec la ligne `T7_RUNTIME_GO ACCORDÉ` et les champs `stage`, `design_id`, `seed_plan_sha256` et `approval_sha256` ci-dessus. Calculer son SHA-256, inscrire sa référence dans le bloc `authorization` du YAML v2, puis calculer le SHA-256 du YAML. Renseigner ces deux SHA-256 dans l’INTENT v2 actif et vérifier le préflight. Calculer le SHA-256 brut de l’INTENT final avant de soumettre l’autorité de réconciliation.

[Projet INTENT v2](DRAFT-stream-32-t7-runtime-v2-intent-20261124.json) · [Projet de réconciliation](DRAFT-stream-32-t7-reconciliation-v2-20261124.md)
