# Décision de reprise T7 — qualification `resumed`

Décision écrite du chercheur du 24 novembre 2026 pour `resumed --jobs 2 --resume` à partir du point de reprise `CAL`, avec l’INTENT v2 et le registre cumulatif existants.

T7_RESUME_GO ACCORDÉ
stage: qualification
case: resumed
design_id: a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804
previous_token: fde8c70b672e462bab47465f87695c1c
intent_sha256: 5c5259d602dc6571884c807b4452083cde741a142eb05430ffde425db7e53db5
receipt_sha256: c6522e85c6d37dc692b759e159d2c37dfd85a03e55a8001b6b88570103299a84
inventory_sha256: a964dc40677533870708c7107d0f44757042e45723e14b1e31bd0d1a39f37363
cpu_charged_seconds: 160

Le contrôle du 24 novembre 2026 à 16:35:22 UTC a confirmé `CLEAN_BLOCKED_RESOURCE`, `last_complete_phase = CAL` et les deux cgroups vidés. Le registre porte 160 s CPU débitées (2 + 113 + 45) et 0 s réservée.

Le témoin d’arrêt forcé intervient au premier checkpoint stable après `CAL`. La poursuite après interruption requiert une décision écrite de réconciliation.
