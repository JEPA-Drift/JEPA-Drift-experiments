# Stream 32 — GO pour le Full gaussien

**FULL_GO ACCORDÉ — STREAM 32 / FULL GAUSSIEN**

21 novembre 2026. Ce fichier consigne l’autorisation écrite du chercheur pour les phases 2 à 5 du Prompt 3 v4, après acceptation des dix critères de qualification. Le mandat couvre le design et le plan de graines ci-dessous, avec 10 h CPU cumulées, 32 Gio agrégés, 2 700 s par invocation, `jobs_max = 8` et un lancement initial avec `--jobs 1`. R3-A, R4 et R5 s’appliquent tels que gelés. [Réception technique](RECEIPT-stream-32-full-QUALIF-20261121.md) · [Verdicts et empreintes](../logs/stream-32/full-qualif-readiness.json)

| Empreinte | SHA‑256 |
| --- | --- |
| `full_design_id` | `8a4af3ecd7864f167ac32b82f0751547dc68b8a4bf24cec0f6c7fefbb19895d4` |
| `seed_plan_sha256` | `88e7c755bb33cd48c57bab000959cac09f4efb9211545951e4fc89469979c450` |
| YAML Full | `34d8addc6b4c91c821c94e0e075d2873952a7118203b3882942d99e46b278539` |
| Source `experiments/pca_info_online.py` | `9fbd6a500789cf8fb9add1317c03ae88a5ad3db979492451a88e3add8fb741ec` |

Le descripteur a été calculé sous verrou dans l’environnement `.venv`. Ses quatorze empreintes de sources correspondent aux fichiers de l’espace de travail. Le YAML d’origine et le manifeste du Pilote correspondent aux empreintes de réception `63dc10ffb660272cff12bcac69b2fe1bf5754b0ffa207d4b4f415197bb095d56` et `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8`. [Descripteur](../logs/stream-32/full-r3-describe.json) · [Configuration Full](../configs/pca_info_online_full.yaml) · [Réception du Pilote](RECEIPT-stream-32-pilot-gaussian-20261120.md)

## Périmètre scientifique autorisé

- **R3-A.** Quatre setups gaussiens `EXACT` et `FITTED_LW_GAUSSIAN` en dimensions 32 et 239, fit 0. Deux applications `RESIDUAL` et `MARKET`, cinq familles préenregistrées, `H = 250`, `K = 20`. `DEV_LIB / DEV_NULL / DEV_ALT` vaut `100 / 1 000 / 200`, `ALT = 2 000` par famille. T7 reste fermé. Le Full gaussien couvre une partie des expériences synthétiques du stream 32.
- **CAL.** `ONLINE_INFO_MIX_W128`, `ONLINE_PREFIX_MIX_W128` et `FULL_K` reçoivent chacun 10 000 trajectoires CAL sur `FITTED_LW_GAUSSIAN`, `N = 239`, fit 0, `RESIDUAL`. Toutes les autres cellules, y compris les oracles et les sensibilités distinctes, en reçoivent 2 000. Les deux groupes CAL partagent les clés des 2 000 premières trajectoires et ont des partitions distinctes.
- **NULL_PLAN et HOLD.** `NULL_PLAN` évalue 2 000 trajectoires nulles indépendantes avec les seuils CAL figés. Il fixe et hache `n_hold = min(n_req, 20 000)`, avec `n_req ≥ 2 000`, avant toute génération HOLD. Les trois `P_CONF` du primaire RESIDUAL partagent exactement cet effectif réalisé. Les autres cellules, y compris MARKET sur le setup primaire, restent à 2 000. La phase génère, calcule, vérifie et écrit des blocs d’au plus 1 000 trajectoires. Les blocs validés sont réutilisés en reprise. La limite de taille est strictement inférieure à 50 Mio par artefact.
- **Appariement.** Les contrastes descriptifs entre effectifs distincts vérifient l’identité du préfixe de chemins `[0, 2 000)` par clés et indices signés. Ils publient les deux effectifs individuels, l’effectif apparié, la plage et le digest HOLD. Les bornes Clopper–Pearson individuelles emploient l’effectif propre de chaque cellule. Les contrastes de Φ utilisent l’effectif partagé complet décidé par `NULL_PLAN`.
- **R4.** Équivalence FPR par TOST de Tango asymptotique à la marge ±0,01, avec queues à `α/3` pour Φ. Bootstrap percentile apparié de 10 000 réplications des 2 000 trajectoires ALT. La couverture finie exacte et une garantie finie de FWER sont hors de la portée de ces méthodes. Un plan plafonné conserve `PLAN_CAPPED_EXPECT_INCONCLUSIVE`, les marges et les résultats observés. Le dimensionnement vise la puissance par contraste. Une politique `NULL_FAILED` invalide la revendication qui la compare. La formulation des conclusions distingue FPR atteinte comparable et alpha nominal commun.
- **R5.** `FIT_CONDITIONAL` au fit 0. La variabilité entre ajustements et une généralisation à d’autres fits sont hors du périmètre. H1 et H3 comparent respectivement INFO à PREFIX et à FULL_K sur F2. H2 évalue la non-infériorité relative à 10 % sur HEAD avec le contrôle de géométrie et de détectabilité du plan. Les estimands temporels sont tronqués à H. Les oracles et les sensibilités restent descriptifs.

[Plan canonique §§9–10](plans/plan-32.md#10-dimensionnement-du-holdout-par-le-seul-nul-null_plan) · [Amendement v2.1](plans/plan-32-v2.1-amendment.md) · [Écart R3-A documenté](../docs/DEVIATIONS.md#c-pca-info-online-full-r3-allocation--allocation-r3-a-et-partitions-hold)

## Témoins RED, GREEN et non-régression

| Cycle | RED | GREEN |
| --- | --- | --- |
| CAL à deux effectifs | 2 échecs attendus | 17 cas ciblés passent. [RED](../logs/stream-32/full-r3-cal-red.pytest.log) · [GREEN](../logs/stream-32/full-r3-cal-green.pytest.log) |
| HOLD par bloc et reprise | 3 échecs attendus | 1 cas ciblé de plan et C0 de 1 082 cas passent. [RED](../logs/stream-32/full-r3-hold-red.pytest.log) · [GREEN](../logs/stream-32/full-r3-hold-c0.runner.log) |
| Appariement et refus d’identités étrangères | 11 échecs attendus, puis 2 cas limites RED | 15 cas ciblés passent. [RED](../logs/stream-32/full-r3-pair-red.pytest.log) · [Cas limites](../logs/stream-32/full-r3-pair-red-edges.pytest.log) · [GREEN](../logs/stream-32/full-r3-pair-green.pytest.log) |
| Intégration et limites de taille | 7 échecs attendus | 7 cas ciblés passent. [RED](../logs/stream-32/full-r3-integration-red-tests.runner.log) · [GREEN](../logs/stream-32/full-r3-integration-green-tests.runner.log) |

Les témoins de plan donnent 2 000 et 3 184 sous `PLAN_ADEQUATE`, et 20 000 sous `PLAN_CAPPED_EXPECT_INCONCLUSIVE`. Le témoin borné reproduit bit à bit les premiers hits et masques d’une référence déterministe non partitionnée, ainsi que les comptes et les bornes CP. Une interruption au deuxième bloc laisse le premier intact. La reprise avec trois workers et l’exécution continue à un worker produisent les mêmes seuils, partitions, cinq CSV et identité de réalisation. Un indice altéré, une filiation étrangère ou une taille égale à 50 Mio sont refusés. Le témoin FINAL au plafond a produit 124 contrastes mixtes avec 2 000 réalisations appariées et des effectifs individuels de 2 000 et 20 000. Les trois lignes de Φ ont chacune reçu 20 000 chemins HOLD dans ce témoin. [Tests](../tests/test_pca_info_online.py#L17659) · [Inférence témoin](../logs/stream-32/full-r3-qual-sizing/bootstrap/fixture-inference.json)

C0 a exécuté 1 089 tests avec succès et `make prompts-check` a vérifié 34/34. Le premier `make check` du même lanceur a échoué sur le préfixe `+` d’une option pytest. La relance corrigée sous verrou a terminé avec le code 0, `pyflakes`, 22 tests de contrats et de découplage et 1 089 tests dans le périmètre retenu. Quinze cas sur panels réels ont été désélectionnés. [C0 et prompts](../logs/stream-32/full-r3-final-c0.runner.log) · [Relance make check](../logs/stream-32/full-r3-make-check.runner.log)

## Mesures et enveloppe retenue

| Invocation de qualification | Mur (s) | CPU utilisateur + système (s) | `memory.peak` (Mio) | Disque alloué à la sortie (Mio) |
| --- | ---: | ---: | ---: | ---: |
| `smoke`, 1 worker | 255,98 | 254,64 | 194,15 | 35,26 |
| HOLD, 1 worker, préambule inclus | 345,11 | 343,17 | 591,93 | 34,96 |
| HOLD, 3 workers, préambule inclus | 352,38 | 371,23 | 627,46 | 34,96 |
| Préparation du témoin FINAL | 201,88 | 200,36 | 1 882,23 | 1 076,58 |
| Relecture, bootstrap et contrastes | 50,63 | 50,38 | 857,96 | 1,11 |
| Revalidation et assemblage `FINAL` | 503,18 | 501,30 | 298,22 | 1,42 |
| Agrégations FAIR isolées | 1,17 | 1,12 | 116,05 | 1,00 |

Les mesures proviennent de scopes distincts à 32 Gio avec `OOMPolicy=stop` sous verrou. Les compteurs mémoire n’ont pas évolué. HOLD a traité 34 cellules sur un seul lot de scores `1 000 × 250 × 20`. Les phases HOLD proprement dites ont pris 332,21 s et 330,63 s. À trois workers, le pic RSS maximal d’un enfant est de 219,18 Mio et le pic RSS parent de 675,54 Mio sur l’invocation. Le pool traite au plus 100 trajectoires par tâche. Le SHA‑256 du NPZ HOLD est identique entre les deux exécutions, `7178539f370eecbaf2c37cd317e20c438345e47d0ef04a0afb4189cc4ed78a81`. Il occupe 32,71 Mio. Le plus grand NPZ du témoin est un ALT de 42,32 Mio, et le plus grand CSV de qualification pèse 0,98 Mio. Pour `DEV_NULL` à 1 000 trajectoires, le tableau de scores `float64[1 000,250,20]` occupe 38,15 Mio hors en-tête. Le code contrôle la taille de chaque NPZ au commit et à la relecture. [Mesures HOLD 1](../logs/stream-32/full-r3-qual-sizing/hold1/report.json) · [Mesures HOLD 3](../logs/stream-32/full-r3-qual-sizing/hold3/report.json) · [Inventaire témoin](../logs/stream-32/full-r3-qual-sizing/fixture.sizes) · [Garde NPZ](../experiments/pca_info_online.py#L741)

Le témoin FINAL couvre quatre setups, 34 blocs HOLD et 20 partitions ALT. Les premiers hits sont des entrées synthétiques de charge, avec les masques ALT obtenus par les politiques gelées sur des scores gaussiens projetés. Il a traité 20 matrices bootstrap `10 000 × 2 000` et 520 contrastes descriptifs. La construction des indices a pris 1,46 s au total. Le noyau Φ a pris 0,33 s et les contrastes descriptifs 28,37 s, dont la génération de leurs indices. L’assemblage et les cinq exports ont pris 451,81 s, après 48,32 s de revalidation. L’agrégation isolée a reproduit le SHA‑256 d’`aggregates.csv`. Les deux invocations bootstrap et publication cumulent 553,81 s, avec des relectures répétées. Ce chiffrage et les pics mesurés par scope qualifient la préparation sur témoin. Le temps et le pic agrégé de la campagne autorisée restent des mesures à relever. [Banc exécuté](../logs/stream-32/qualify-full-r3.py) · [Journal sizing](../logs/stream-32/full-r3-qual-sizing.runner.log) · [Bootstrap](../logs/stream-32/full-r3-qual-sizing/bootstrap/report.json) · [FINAL](../logs/stream-32/full-r3-qual-sizing/publish/report.json) · [Agrégations](../logs/stream-32/full-r3-qual-sizing/aggregates/report.json)

L’enveloppe autorisée est de **10 h CPU cumulées, 32 Gio agrégés, 2 700 s par invocation et huit workers au maximum**. Le rythme mesuré sur le bloc HOLD, appliqué à titre de projection au compte de scans §17 et augmenté du temps CPU FINAL, donne environ 4,6 h CPU avant surcoût des reprises. Au même rythme mur, les CAL longs, CAL ordinaires et ALT les plus chargés représentent environ 293, 606 et 430 s par partition, sur la base de 30 000, 62 000 et 44 000 scans. Le lancement utilise un worker. Les reprises sont manuelles, sur les mêmes destinations et dans le même budget cumulé. Chaque reprise exige `CLEAN_BLOCKED_RESOURCE`, au moins 2 702 s CPU disponibles, aucun processus résiduel, un staging intègre, un inventaire des phases et blocs restants et l’absence d’OOM ou d’anomalie. Tout autre arrêt requiert un arbitrage préalable. [Projection initiale](ANALYSIS-stream-32-full-r3-20261120.md#cpu-délai-et-décisions) · [Journal sizing](../logs/stream-32/full-r3-qual-sizing.runner.log)

**Clôture du mandat.** Après publication de `FINAL.json`, l’audit indépendant vérifie d’abord les données pré‑ALT, publie le rapport correspondant, puis examine ALT. La réception conserve les résultats négatifs, inconclusifs ou invalides. T7, données réelles ou `2020+`, JEPA, wrap-up, réindexation, commit et push restent fermés. Le Pilote et ses quatre statuts `NULL_FAILED` restent consignés dans son audit. [Audit du Pilote](AUDIT-stream-32-pilot-null-20261120.md)
