# Audit des échecs nuls du pilote gaussien

Audit du 21 novembre 2026, sur le pilote du 20 novembre. Verdict unique **`EXPECTED_SAMPLING_VARIABILITY`**. Les quatre comptes HOLD se reproduisent à partir des graines et des objets figés. Les contrôles de calibration, de sélection et de rejeu concordent avec le staging. Les quatre cellules conservent leur statut `NULL_FAILED`. La porte T7 de la section 18 reste fermée et le Full attend les décisions R3–R5. [Réception R2](RECEIPT-stream-32-pilot-gaussian-20261120.md) · [Plan §§8 et 18](plans/plan-32.md#8-calibration-et-statuts-nuls)

## Distribution prédictive

Pour un fit et une politique figés, les maxima CAL et HOLD sont des tirages de la même loi continue $F$, sur des cohortes distinctes. Avec $n=200$ et $\alpha=0{,}05$, le rang supérieur est $r=\lfloor\alpha(n+1)\rfloor-1=9$. La borne $b$ est le 191ᵉ maximum en ordre croissant. Le seuil `GE` est `nextafter(b, +inf)`. Dans le modèle continu, $1-F(b)$ suit une `Beta(10,191)` sur les répétitions de CAL, avec moyenne 0,04975124 et écart-type 0,01529836. Conditionnellement au seuil réalisé, le nombre d’alarmes HOLD est binomial. En intégrant sur CAL, il suit une `BetaBinomial(200,10,191)`. [Règle de rang](../experiments/pca_drift_benchmark.py#L221) · [Calcul indépendant](../logs/stream-32/audit-pilot-null-failures.py)

| Qualification unilatérale Clopper–Pearson à 95 %, frontière 0,06 | Alarmes sur 200 | Probabilité exacte arrondie |
| --- | ---: | ---: |
| `NULL_VALIDATED` | 0 à 6 | 22,2555 % |
| `NULL_INCONCLUSIVE` | 7 à 18 | 73,9366 % |
| `NULL_FAILED` | 19 à 200 | 3,8079 % |

Les trois valeurs de l’amorçage (22,03 %, 73,20 %, 3,77 %) totalisent 99,00 %. Le calcul exact retrouve l’ordre de grandeur de 3,81 % par cellule. Pour 99 cellules supposées indépendantes, $P(J\ge4)=52{,}3398\,\%$ avec la probabilité exacte et 52,3837 % avec $p=0{,}0381$. Ces probabilités illustrent l’ordre de grandeur sous indépendance. Le partage de trajectoires interdit leur lecture comme une p-valeur de campagne. Les queues marginales $P(K\ge24)=0{,}5000\,\%$ et $P(K\ge26)=0{,}2028\,\%$ situent les deux cellules extrêmes. Elles concernent chaque cellule prise isolément avant sélection parmi les 99. [Résultats numériques](../logs/stream-32/audit-pilot-null-failures.json)

## Contrôles des quatre cellules

| Calibration | Setup, application | Politique | Médiane / P95 CAL | Borne CAL $b$ | Seuil $h$ | Alarmes CAL / HOLD | Borne CP inf. |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `902743ca294fea06` | EXACT 239, MARKET | `ONLINE_INFO_AFF_W128` | 0,687862 / 1,666894 | 1,6826862097495443 | 1,6826862097495445 | 9 / 19 | 0,063106 |
| `3c3eb9517a60d822` | EXACT 239, RESIDUAL | `ONLINE_INFO_AFF_W128` | 0,683866 / 1,674471 | 1,6834647123446411 | 1,6834647123446413 | 9 / 19 | 0,063106 |
| `8491081f7f14e71a` | FITTED_LW_GAUSSIAN 239, MARKET | `FIXED_EIGENMEAN_PREFIX` | 1,257780 / 2,362185 | 2,3860095163142550 | 2,3860095163142554 | 9 / 24 | 0,084140 |
| `3d21bbba6bd2cb96` | FITTED_LW_GAUSSIAN 32, MARKET | `FIXED_EIGENMEAN_PREFIX` | 1,150918 / 2,481419 | 2,5720201347250870 | 2,5720201347250873 | 9 / 26 | 0,092713 |

Chaque cellule contient 200 maxima CAL distincts, avec rang 9, seuil au flottant suivant et 9 alarmes CAL. Le rejeu des 800 trajectoires CAL retrouve chacun des maxima à $1{,}34\times10^{-15}$ près en valeur absolue. Celui des 800 trajectoires HOLD retrouve exactement les 800 premiers jours d’alarme ou censures et les 200 000 masques journaliers. Les quatre bornes HOLD ont été recalculées. Sur les 99 cellules non-oracle, le staging donne 21 `NULL_VALIDATED`, 74 `NULL_INCONCLUSIVE` et 4 `NULL_FAILED`. [Résultats numériques](../logs/stream-32/audit-pilot-null-failures.json)

Les 2 clés `fit` de `FIT_NULL`, 800 clés `CAL_NULL` et 800 clés `HOLD_NULL` ont des entropies canoniques disjointes et 1 602 témoins distincts de l’état initial de `SeedSequence`. Les cohortes CAL et HOLD utilisent des flux PCG64 séparés, conditionnellement au fit figé. À l’intérieur d’un setup, les clés de trajectoire omettent volontairement l’application et la politique. Sur EXACT 239, les PC 2 à 20 sont donc communes à MARKET et RESIDUAL. Le rejeu retrouve 950 000 scores communs bit à bit par rôle. Les maxima CAL appariés ont une corrélation de Pearson de 0,9550. En HOLD, 16 chemins déclenchent dans les deux applications, 3 dans MARKET seul, 3 dans RESIDUAL seul et 178 dans aucune. La corrélation des indicatrices vaut 0,8255. [Construction des clés](../experiments/pca_info_online.py#L1597) · [Résultats numériques](../logs/stream-32/audit-pilot-null-failures.json)

- `ONLINE_INFO_AFF_W128` emploie les $m=\min(128,t-1)$ scores précédant le jour $t$. Le rejeu emploie des moyennes de fenêtre directes et une régression OLS sur les profondeurs 1 à 16. Les masques retrouvent les départages par ordre d’axe puis par profondeur minimale. La première sélection porte sur la PC 1 en MARKET et la PC 2 en RESIDUAL. Le premier jour et les égalités de coût sont couverts par la comparaison de tous les masques HOLD. [Sélection adaptative](../experiments/pca_info_online.py#L34)
- `FIXED_EIGENMEAN_PREFIX` compare les valeurs propres ajustées à la moyenne des 20 valeurs propres éligibles. Le rejeu retrouve les PC 1 à 7 pour N239 et les PC 1 à 6 pour N32. Il retrouve exactement la moyenne des échantillons `FIT_NULL` et reconstruit les scores avec le centrage figé et la division par la racine des valeurs propres ajustées. Les variances de population des 20 scores sont comprises entre 0,93965 et 1,10854 pour N239, et entre 0,91611 et 1,10039 pour N32. Cette dispersion est cohérente avec la normalisation par le fit ajusté. L’audit réutilise les vecteurs et valeurs propres figés. [Préfixes spectraux](../experiments/pca_info_online.py#L1272) · [Trajectoires et projection](../experiments/pca_info_online.py#L1681)
- Les quatre cellules emploient le prior isotrope commun $s^2=0{,}0034068772765664954$. Le score de sélection et le scan utilisent des termes quadratiques. Le rejeu compare le maximum log par chemin et le premier jour, indexé à partir de 1, où le maximum courant atteint ou dépasse le seuil figé. Les contrôles couvrent le signe du terme logarithmique, le sens du franchissement, la normalisation et le décalage de la fenêtre. [Scan](../experiments/pca_info_online.py#L101) · [Prior](../experiments/pca_info_online.py#L1833)

## Traçabilité

Le code de GLM‑5.3 a fourni les formules de rejeu. Codex a réduit la proposition aux schémas figés, corrigé la jointure des maxima par `policy_id` et famille, puis vérifié les empreintes de phases et de partitions. Le script s’est exécuté sous le verrou partagé avec `.venv`, sans appel au producteur ni lecture d’ALT. Le premier lancement Vibe a échoué avant l’appel au modèle faute de `PATH` pour Git. Le deuxième a atteint sa limite après des appels outils refusés. Le troisième, sans outils, a remis le script. [Lanceur d’audit](../logs/stream-32/run-audit-pilot-null.sh) · [Export Vibe](../logs/stream-32/pilot-null-failures-vibe-a3/export.json)

| Pièce | SHA-256 |
| --- | --- |
| [Script](../logs/stream-32/audit-pilot-null-failures.py) | `7e9fd5332f8e241be95cf2ca9a9427b9501227a159d040f64252b0c6b92fe8e8` |
| [JSON](../logs/stream-32/audit-pilot-null-failures.json) | `b61bc5ce727ddbbba51e02082bff05316f794c692deec9cc8a91c0481b9ec6f0` |
| [Manifeste du pilote](../results/pca_info_online/pilot-gaussian/manifest.json) | `325b3f406296fdededd429d3515953a52b18158d9024a923c00049ef2c2648b8` |

L’analyse d’impact du Full est consignée séparément. [Analyse R3–R5](ANALYSIS-stream-32-full-r3-20261120.md)
