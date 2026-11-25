# Décision T7_RUNTIME_GO v2 — qualification Stream 32 Student-t7

Décision écrite du chercheur du 24 novembre 2026, consignée selon le projet v2.

T7_RUNTIME_GO ACCORDÉ
stage: qualification
design_id: a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804
seed_plan_sha256: 5bdb1b70b5253c1e16eb14017621e2ff4ae327b00142072bc22c8edb450994e7
approval_sha256: 9dff9191614fa268ed77dd98880a6bde994f4642f99dca314b8befe8573d3673

Le périmètre se limite à la reprise de `continuous --jobs 1` en mode `smoke`. La réconciliation et la reprise exigent les décisions écrites `T7_RECONCILIATION_GO` et `T7_RESUME_GO` liées au SHA-256 brut de l’INTENT v2. Le cas `resumed`, le Pilote et le Full exigent chacun une décision distincte.

L’enveloppe fixe 8 Gio, 2 h de CPU cumulées, 900 s par invocation, `jobs_max=2` et un CPU logique. L’exécution est soumise au verrou partagé et les témoins ALT relèvent de `SMOKE_NO_CLAIMS`.

[Projet de décision v2](DRAFT-stream-32-t7-runtime-v2-20261124.md)
