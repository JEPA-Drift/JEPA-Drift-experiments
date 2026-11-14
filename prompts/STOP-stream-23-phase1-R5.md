# STOP — stream 23 / E6 phase 1, porte R5 (reproduction complète, jobs 48)

Date : 2026-11-14, 02:13:32 UTC. Session Claude Code interactive 23 conservée. GO appliqué :
`prompts/GO-stream-23-phase1-historical-runtime-20261114.md`
(SHA-256 `60826a36799c88999e9c59c499c0dc6411c6da966d5570e9c9d278b18a8d1dc3`).

## Constat

R5 a été interrompu par l'enveloppe mémoire du scope, pas par un calcul divergent observé.

- L'unité `jepa23-r5-full-20261114T021314Z.scope` est restée en état `failed`. `systemctl --user show` donne :
  `Result=oom-kill`, `OOMPolicy=stop`, `MemoryMax=8589934592`, `KillMode=control-group`, active de 02:13:14 à 02:13:32 UTC.
- Le noyau a tué un processus du scope en atteignant 8 Gio. systemd a ensuite arrêté tout le scope par SIGTERM.
- La commande sort avec le code 143 (128 + SIGTERM) après 18,45 s.
- Aucune sortie n'a été produite : `logs/23-phase1/full` n'existe pas. Le script s'arrête avant `args.out.mkdir`, qui suit
  `run_d6` et `run_d5`.
- Aucune empreinte C3 n'a donc pu être comparée.

Je n'ai fait aucune relance, et je n'ai modifié ni les jobs, ni la mémoire, ni un paramètre, ni une empreinte.

## Commande (créneau unique R4 puis R5, PID shell 3751678, verrou acquis à 02:12:03 UTC)

```
flock -n 9   # fd 9 ouvert en lecture sur logs/.jepa_execution.lock du checkout principal (convention E4)
systemd-run --user --scope --quiet -p MemoryMax=8G --unit=jepa23-r5-full-20261114T021314Z -- \
  sh -c '<memory.max ; /usr/bin/time -v -o r5-full.time timeout 1200 "$@" ; memory.peak + memory.events>' \
  logs/23-phase1/historical-runtime-20261114/r5-full 1200 \
  env -u PYTHONPATH OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE \
      PYTHONHASHSEED=42 MPLBACKEND=Agg \
  .venv/bin/python experiments/e6_second_order.py --phase 1 --jobs 48 --out logs/23-phase1/full \
      --fig-dir logs/23-phase1/full/figures --log-dir logs/23-phase1/full/logs
sha256sum -c logs/23-phase1/sealed-full.sha256
```

## Codes

| Élément | Résultat |
|---|---|
| R5 | code 143 ; `Terminated` ; 02:13:14.115 → 02:13:32.566 UTC (18,45 s) |
| GNU time | rapport vide (`r5-full.time`, 0 octet) : processus tué avant l'écriture |
| memory.peak / memory.events | non relevés : l'enveloppe `sh` a été tuée avec le scope |
| stderr | 250 octets : `resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown` |
| stdout | 0 octet |
| `sha256sum -c sealed-full.sha256` | code 1 ; 5 × `FAILED open or read` |
| script d'arrière-plan | code 21 (porte R5) |

## Empreintes attendues et observées

| Fichier attendu | SHA-256 attendu (C3) | Observé |
|---|---|---|
| `logs/23-phase1/full/e6_cells_phase1.csv` | `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249` | absent |
| `logs/23-phase1/full/figures/e6_phase1_delays.png` | `ca929eee4cb9f7e3bad769241cb7df8145c3354f6f4da56c6491b73bebc9e897` | absent |
| `logs/23-phase1/full/figures/e6_phase1_delays.pdf` | `cdffaf9eb2755a98f01193ce206010a57c4979556f79fe24c723e3b55b1dc811` | absent |
| `logs/23-phase1/full/figures/e6_phase1_gadd.png` | `f14e06cb976cd8099e66daf826f76d474a67eebf512367c02375281c18b34113` | absent |
| `logs/23-phase1/full/figures/e6_phase1_gadd.pdf` | `1ed21dc6ee4317eabf0d0c2996d5b3d7b57bdfb00db8a2a91e04984a3777570b` | absent |

## Écart disponible

- La cause est établie par l'état de l'unité (`Result=oom-kill`). Le journal utilisateur et le journal noyau ne sont pas
  lisibles par ce compte (« insufficient permissions »). Le processus tué n'est donc pas identifié.
- Les pics mémoire des autres invocations, sous la même enveloppe de 8 Gio, viennent de `memory.peak` :
  - R4 quick jobs 1 : 629 051 392 o (un seul processus) ;
  - R2 : 482 496 512 o.
  - Le pic agrégé de R5 (processus principal et 48 workers spawn) n'a pas été relevé.
- Rien ne concerne une valeur produite, un noyau, un paramètre ou une graine.
- Après l'arrêt, il ne reste aucun processus. Le verrou partagé est libre. L'unité en échec n'a pas été réinitialisée
  (`reset-failed` non lancé), pour inspection.

## Étapes précédentes du même GO

| Porte | Résultat observé |
|---|---|
| R1 mutant (2 cas synthétiques, `PYTHONPATH=.:logs/23-phase1/mutant`) | code 1, `2 failed in 1.47s`, 2 × `AssertionError: ret_wide.npy opened without mmap_mode='r'` (`tests/test_e6.py:42`) |
| R2 fichier entier | code 0, `27 passed in 8.53s` |
| R3 pyflakes | code 0, aucune sortie |
| R4 quick jobs 1 | code 0, 70,07 s ; CSV `874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2`, `sealed-quick.sha256` OK |
| R6 | non exécuté (arrêt au premier écart) |

Le journal quick de R4 (hors R6) montre :
- aucune mention de `ret_wide.npy` ;
- `sha256 data/derived/d3_239/splits.yaml 3f3a65ba…` et `sha256 configs/e6.yaml ca74d2e1…` ;
- la ligne `calib rows [2834, 3775) = 2016-04-07..2019-12-31 (941 days)` ;
- `D6 d3_239: sha256 of the 3775 x 239 return rows read, C order d18ddc3b541ea3037ae9a817b40bd43ee9568c71e62eeeb095fda8c2bd2a4b6c`.

## Environnement R0

- `.venv/bin/python` résolu vers le binaire python3.12 de Trading. Paquets chargés depuis
  `~/JEPA-Drift-experiments/.venv/lib/python3.12/site-packages/`.
- Versions égales à `requirements.lock` : matplotlib 3.11.2, numpy 2.4.4, pandas 3.0.6, PyYAML 6.0.3, scipy 1.17.1,
  statsmodels 0.15.0.
- Machine : 48 CPU (affinité 0-47), 187 Gio de mémoire, systemd 252 (252-51.el9_6.2). Service E4 inactif, charge 0,14 avant
  le lot.
- Identités pendant le lot :
  - HEAD `461f2b13894be2cca954676dc3aab10e0b640a2b` ;
  - source `5af91240df658f8ec7e8f45139cf74144ed9c6665d52bc6f8aec67da42902855` ;
  - tests `39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc` ;
  - configuration `ca74d2e117edb47b0ff11822501a20a381460c35c69e81b57a6d11de81a2bcf5`.

## État laissé et décision attendue

- Aucun code, test, configuration, donnée, résultat, figure, GO ou plan n'a été modifié.
- Les sorties de R4 restent sous `logs/23-phase1/quick/`. Le plugin mutant reste sous `logs/23-phase1/mutant/`, ignoré.
- Preuves : `logs/23-phase1/historical-runtime-20261114/`, avec `journal.log` et `SHA256SUMS`.
- R5 et R6 restent ouverts. La valeur de 8 Gio de l'enveloppe vient du GO. Toute reprise de R5 attend une décision
  Codex sur l'enveloppe d'exécution. Les jobs, paramètres et cibles C3 du plan ne sont pas en cause et restent inchangés.
