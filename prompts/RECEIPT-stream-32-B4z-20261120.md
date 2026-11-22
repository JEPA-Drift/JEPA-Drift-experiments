# Stream 32 — B4z receipt

20 November 2026. **T10, T15 and T34 pass on the full CLI fixture.**

HOLD and ALT preserve the day-one fallback bit for both ONLINE
orders, at both budgets. FULL_K keeps all 20 bits. Direct
verification of each oracle partition confirms non-fallback,
time-constant mask words on both families. The observed prior
at CAL, HOLD and ALT is the K-based common prior, including
masks of first-day cardinality one and 20. The singleton DEV
grid exercises the explicit S2_DEV alias.

Only ONLINE_INFO_MIX_W128 and ONLINE_PREFIX_MIX_W128 carry a
separate gamma rule, policy and CAL identity. The publication
contains four selections with the fixture budget 120, and
eight with the nominal budget 504. The previous pure witness
covers the preregistered sensitivity budget 5000.

Locked C0 measured **1,059 passes in 94.17 seconds**.
Matrix totals are **64 PASS and 4 NOT_RUN**.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |
| `tests/test_pca_info_online.py` | `b4a7be9f179040d696210ad796115e2eca91e7dbd4e3840b705ab641b2ebba63` |
| `logs/stream-32/lot-B4z-tests.pytest.log` | `59c90ed1e58db99cbea9fefb6d2ff7f80f18ee0a487ca09f72ec8f3d61e8d2c2` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `6cbee0db5264be3dbc52c7ce2e9f6f9b4b5e93c6f93a232b968bdd34125452ef` |
| Fixture manifest.json | `2f31f685c5836bfd7e7b267f77a6a7692651af2ad399bc0842719fdbda7f6dec` |
| Fixture selections.csv | `52e27fa067a2514290b5027b3806f33c761143717122fae2a467b06d49e049c0` |
| Fixture calibration.csv | `5ae0226a9c2fdc3aa0bb641d1c22b854f0d56f7830277783e8a9ea20ab1fc5c9` |
