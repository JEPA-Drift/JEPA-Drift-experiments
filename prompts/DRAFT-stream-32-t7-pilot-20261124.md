# Projet de décision T7_PILOT_GO — Stream 32 Student-t7

`NO_T7_PILOT_GO`

Projet soumis au chercheur pour une exécution `PILOT_ONLY` à un worker, sous verrou partagé. Le périmètre comprend `FITTED_LW_T7` aux dimensions 32 et 239, au fit 0 (`FIT_CONDITIONAL`), les applications RESIDUAL et MARKET, les cinq familles canoniques et H = 250. Le plan compte `4/18/4/0/4/10` partitions pour `SETUP/DEV/CAL/NULL_PLAN/HOLD/ALT`. Les effectifs `DEV_LIB/DEV_NULL/DEV_ALT/CAL_NULL/HOLD_NULL/ALT` sont `100/200/50/200/200/200`. `NULL_PLAN` est inapplicable. Les diagnostics d’information restent des proxys gaussiens et les comparaisons du Pilote restent descriptives.

| Champ | Valeur proposée |
| --- | --- |
| `stage` / `mode` | `pilot` / `pilot` |
| `design_id` | `2ac79300374b99ba1842c2d501c4a1d03ce890c623018ab9cc0f7a9cc20e1ddf` |
| `seed_plan_sha256` | `0354e3a4f470e6075e1c552b85fb7405e53d9ee1a03b397c8f4173b7de1ea98e` |
| `approval_sha256` provisoire | `d8465243d1c4866f09345fd2630dbf9630720ac13ac49e2ccac5b2f4c0421bec` |
| SHA-256 du YAML scientifique | `e0bd1f4dedb7b2792453c19907b09c210765232f042652908fb212e526086c09` |
| Enveloppe | 8 Gio agrégés, 2 h CPU cumulées, 2 700 s au mur par invocation, `jobs_max=1` et un CPU logique |

## Enveloppe proposée

Conserver l’enveloppe du YAML. Le `continuous` à un worker a consommé 112,011852 s CPU et 112,927525 s entre réservation et drainage. Le pic cgroup observé sur la qualification est de 342,74 Mio, et les quatre mesures disponibles ont des compteurs OOM à zéro. Les scénarios dérivés des effectifs donnent environ 736 s au mur sur la référence à un worker et 1 446 s avec les durées de phase les plus élevées des deux cas. Le bootstrap descriptif propre au Pilote n’est pas chronométré par le smoke. La limite applicative de 2 000 s laisse environ 1 264 s et 554 s de marge dans ces deux scénarios. L’enveloppe de 2 h laisse crédit pour deux débits conservateurs de 2 702 s. Ces chiffres soutiennent le maintien des plafonds, sous réserve des mesures effectives du Pilote. [Reçu de qualification](RECEIPT-stream-32-t7-runtime-20261124.md)

## Vérification et décision

Le descripteur calculé sous `.venv/bin/python -B` correspond exactement au projet d’INTENT. Le SHA-256 d’approbation provisoire lie le descripteur, le plan de graines, l’enveloppe, le YAML scientifique et les 20 empreintes de code et d’orchestration. La projection omet la référence GO et le SHA du YAML autorisé. Le projet laisse ces deux empreintes à `null`, et le YAML scientifique conserve `authorization: null`.

```sh
MPLBACKEND=Agg OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 \
  .venv/bin/python -B experiments/pca_info_online.py \
  --config configs/pca_info_online_t7_pilot.yaml --mode pilot --describe
```

La décision écrite fixe le design et les limites. Après cette décision, les chemins réservés au GO et à la copie autorisée du YAML pourront être renseignés, leurs empreintes reportées dans l’INTENT actif puis contrôlées au préflight. Une publication éventuelle sera soumise à l’audit en deux passes et à la cartographie des cinq CSV. Les statuts HOLD seront conservés. Les comparaisons liées à `NULL_FAILED` porteront `NOT_CLAIMABLE`. La décision Full reste indépendante.

[Projet d’INTENT Pilote](DRAFT-stream-32-t7-pilot-intent-20261124.json) · [YAML scientifique](../configs/pca_info_online_t7_pilot.yaml) · [Amendement prospectif](AMENDMENT-stream-32-t7-20261122.md)
