# Projet de décision T7_FULL_GO — Stream 32 Student-t7

`NO_T7_FULL_GO`

Le projet Full reprend le périmètre prospectif `DESCRIPTIVE_NOMINAL` de l’amendement. Il couvre `FITTED_LW_T7` à N = 32 et 239, `fit_id=0` (`FIT_CONDITIONAL`), RESIDUAL et MARKET, cinq familles, 18 labels de politique dans leurs univers respectifs et H = 250. La graine est 3232. Les effectifs `DEV_LIB/DEV_NULL/DEV_ALT/CAL_NULL/HOLD_NULL/ALT` restent `100/1000/200/2000/2000/2000`. Le plan garde `NULL_PLAN=NOT_APPLICABLE`, sans allocation confirmatoire. Le bloc gaussien `phi` reste hors périmètre. [Amendement prospectif](AMENDMENT-stream-32-t7-20261122.md) · [YAML Full](../configs/pca_info_online_t7_full.yaml)

Le Pilote a deux audits `PASS` et un échec CP sur 87 cellules HOLD. L’oracle non déployable `ORACLE_INFO_MIX` (N = 239, `F2_STRUCTURED_RESIDUAL`) a alarmé sur 20/200 chemins. Le contraste associé porte `NULL_FAILED — NOT_CLAIMABLE`. Le Full réappliquera aux nouveaux chemins CAL et HOLD la règle de rang et les bornes CP prévues. Les tailles, politiques, familles, graines et règles de seuil restent celles de l’amendement prospectif. Les mesures ALT du Pilote contribuent uniquement à l’estimation de charge, par le nombre de scans et le temps de phase. [Reçu Pilote](RECEIPT-stream-32-t7-pilot-20261124.md) · [Cartographie Pilote](../docs/MAPPING.md#stream-32-student-t7-pilot)

## Enveloppe soumise à revue

| Ressource | Mesure Pilote | Prévision Full | Plafond proposé |
| --- | ---: | ---: | ---: |
| CPU agrégé | 699,683 s | 2–3 h | 6 h |
| Mur actif | 703,649 s | 2–3 h, 4–7 invocations | 2 700 s par invocation |
| Pic cgroup | 334,50 Mio | 3–5 Gio | 8 Gio |
| Disque alloué | 81,29 Mio | ~0,8 Gio persistants, 2 Gio libres à prévoir | |

L’enveloppe du YAML est conservée. Le lanceur borne chaque invocation à un worker sur un CPU logique. La fenêtre de calcul applicative est de 2 000 s et l’admission réserve 2 702 s CPU. Les 4–7 invocations tiennent compte des frontières de partition et des relectures. Le mur actif exclut l’attente d’une éventuelle autorisation de reprise. [Méthode et hypothèses](RECEIPT-stream-32-t7-pilot-20261124.md#full-t7-resource-forecast)

## Identité du projet

| Champ | Valeur |
| --- | --- |
| `stage` / `mode` | `full` / `full` |
| `design_id` | `03abb171a86076e1eaab777cc5d789d7e556646b09eb3c26c9cfa8f5094b1f96` |
| `seed_plan_sha256` | `67649579bbf5144899bbfb094b7c884b457afb975aa57f80dee792273cf09871` |
| SHA-256 du YAML scientifique | `774a8921a37c7ec45a6092bcd22ea9359250a0ca9efefa71fa4ce457371a4a0c` |
| `approval_sha256` du projet | `32ec3fc1ceacf4df545308b985740614b366c98212732872e9dd2d0868a4d2ff` |

`--describe` a retourné le descripteur consigné dans le projet d’INTENT. La projection d’approbation lie ce descripteur, le plan de graines, l’enveloppe, le SHA du YAML scientifique et les 20 empreintes d’artefacts. `authorization` est à `null` dans le YAML. Les empreintes de la référence GO et de la copie autorisée du YAML sont à `null` dans le projet d’INTENT. [Projet d’INTENT Full](DRAFT-stream-32-t7-full-intent-20261124.json)

```sh
MPLBACKEND=Agg OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -B experiments/pca_info_online.py \
  --config configs/pca_info_online_t7_full.yaml --mode full --describe
```

Une décision écrite du chercheur est requise avant toute admission. Si le Full est autorisé ultérieurement, sa publication et sa cartographie devront couvrir tous les résultats, y compris les résultats négatifs et inconclusifs, avec le rapport pré-ALT scellé avant la lecture ALT par l’auditeur et le marquage des paires concernées.
