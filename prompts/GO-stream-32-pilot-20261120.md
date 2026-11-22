# Stream 32 — GO R2 pour le pilote gaussien

20 novembre 2026. `PILOT_GO = GAUSSIAN_ONLY`. Ce fichier consigne le mandat écrit du chercheur transmis avec `prompts/amorcage-32-Pilote.md`, après réception du lot C.

| Autorité | SHA-256 |
| --- | --- |
| `design_id` décrit en mode `pilot` sous verrou | `750443a8413d477e0350c66061eed0c25784b9857cc7d3a6aa7ec2f62ca292e9` |
| `seed_plan_sha256` | `fe2184a6c6e5f2c30eb21eab36513fa8f63c9862bf204b0b174bd51b0451ac6e` |
| YAML source scellé | `63dc10ffb660272cff12bcac69b2fe1bf5754b0ffa207d4b4f415197bb095d56` |
| Réception du lot C | `ecef582b20dcd133db40e630b9fecd4be09928ce17cd0ac555f85a155d939e27` |

Le mandat couvre `EXACT` et `FITTED_LW_GAUSSIAN` en dimensions 32 et 239, fit 0. Les rôles CAL_NULL, HOLD_NULL et ALT comptent 200 trajectoires par cellule prévue. Les cohortes DEV du YAML préenregistré comptent 100 pour DEV_LIB, 200 pour DEV_NULL et 50 par famille pour DEV_ALT. Les extras primaires `s2_dev` et `gamma_M` sont inclus. Le gel R1 s’applique à tous les paramètres scientifiques et à Φ. Les résultats ALT sont réservés au compte rendu `PILOT_ONLY`.

L’enveloppe autorise 32 Gio agrégés, quatre heures CPU cumulées et 2 700 s par invocation, avec huit workers au maximum. Le pilote utilise un worker, retenu sur les mesures du lot C4, sous verrou partagé et scope `MemoryMax=32G`, `OOMPolicy=stop`. Toute reprise conserve le design, les destinations et l’enveloppe cumulée.

La réception vérifie la complétude, les invariances et l’absence de `NULL_FAILED` parmi les politiques non-oracles. Elle rapporte les statuts HEAD et la géométrie obtenus, ainsi que les discordances sous HOLD_NULL et les ressources mesurées pour préparer R3–R5. T7, Full, données réelles, JEPA, modification du benchmark scellé et fin de stream restent hors de cette autorisation.
