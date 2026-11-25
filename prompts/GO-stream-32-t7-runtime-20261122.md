# Décision T7_RUNTIME_GO — qualification Stream 32 Student-t7

Consignation de la décision écrite du chercheur reçue dans la session du 23 novembre 2026 UTC, en réponse au projet du 22 novembre 2026.

T7_RUNTIME_GO ACCORDÉ
stage: qualification
mode: smoke
design_id: a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804
seed_plan_sha256: 5bdb1b70b5253c1e16eb14017621e2ff4ae327b00142072bc22c8edb450994e7
approval_sha256: 20f2f6696214bf44cbb37f78739d9f73d7e8114caa0a6376666c3605dd35289e

Le périmètre couvre `continuous` à `jobs=1` et `resumed` à `jobs=1` jusqu’à l’arrêt propre après CAL. Le passage de `resumed` à `jobs=2` requiert l’autorité écrite de reprise. Le témoin d’arrêt forcé à `jobs=2` impose une réconciliation écrite avant la reprise finale.

L’enveloppe fixe 8 Gio agrégés, 2 h de CPU cumulées dans le registre commun, 900 s au mur par invocation, `jobs_max=2` et un CPU logique par cgroup. Chaque invocation passe par le lanceur scellé et le verrou partagé.

`SMOKE_NO_CLAIMS` s’applique aux témoins ALT. La décision exclut toute analyse de puissance ou de performance ALT, l’exécution du Pilote et du Full T7, ainsi que tout commit ou push.

[Projet de décision](DRAFT-stream-32-t7-runtime-20261122.md) · [Intention scellée](DRAFT-stream-32-t7-runtime-intent-20261122.json) · [Reçu A2](RECEIPT-stream-32-t7-tech-A2-20261122.md)
