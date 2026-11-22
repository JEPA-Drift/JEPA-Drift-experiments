# Amendement natif v2.1 — Stream 32 PCA-INFO-ONLINE (ciblé C1–C3, PLAN ONLY, 2026-11-14)

> **Statut.** Amendement versionné, normatif et autonome de la v2 native (`ex-cute-la-mission-de-gleaming-bird.md`,
> SHA-256 `79293fa331d0ba3493ba40037be98f7b0cef8e1337313e783ab1424b3b34f641`, inchangée), rédigé dans la même session
> sous la notification n° 15. Il ne rouvre ni A1–A3 ni B1–B3 et ne réécrit pas l'architecture. Il remplace ou complète
> exactement les passages listés au §2. Statuts inchangés par ce texte : `PLAN_V2_CORRECTIONS_REQUIRED` jusqu'à la revue
> Codex, `TECHNICAL_GO = NOT_GRANTED_PENDING_V2_1`, `PILOT_GO = ABSENT`, `FULL_GO = ABSENT`. Aucun calcul, import, test,
> simulateur, smoke, profilage, worker ni Git en écriture. Les choix nouveaux sont préenregistrables et n'autorisent aucun
> runtime. Périmètre de production inchangé (quatre fichiers).

## 0. Autorités (SHA-256 vérifiés en lecture seule)

| Pièce | SHA-256 |
| --- | --- |
| Notification chercheur n° 15 `prompts/15_CODEX_REVIEW_STREAM32_PLAN_V2_20261114.md` | `51e2b4dc9498c8cf00fe537269c008b736c6688be82cb74edef9227e43260c41` |
| Disposition Codex `prompts/REVIEW-stream-32-plan-v2-20261114.md` | `5e7b24c5f46a422d749825a4459723716d8ac1a258f60753b6213156c847200e` |
| Réception préparatoire `prompts/plans/plan-32.md` (843 lignes, non suivi, sans valeur de GO) | `aa8e96619fd766c61ca27ef8269365272055eb78b3e6a58a5fc44a0c2e6396b8` |
| Base native v2 | `79293fa331d0ba3493ba40037be98f7b0cef8e1337313e783ab1424b3b34f641` |

Préséance : notification 15 > disposition Codex v2 > réception préparatoire (`plan-32.md` §21) > v2 native >
notification 14 et dispositions antérieures, déjà intégrées. `prompts/GO-stream-32.md` n'existe pas.

## 1. Disposition C1–C3

| Obs. | Disposition | Justification vérifiable | Sections v2.1 | Tests |
| --- | --- | --- | --- | --- |
| C1 autorisation circulaire | MODIFIED | Fond accepté : `design_id` calculable avant tout tirage ; `realization_id` après les phases ; staging dérivé de `design_id` ; reprise par phases ; publication atomique. Seule modification : la mention « GO » de la notification 15 §C1.1 sort de `design_id`. Le GO cite `design_id`, donc l'y inclure créerait un auto-hachage. Il est vérifié séparément avant calcul et conservé dans le manifeste, conformément à la disposition Codex v2. L'enveloppe et les bornes restent dans `design_id`. | §3 | T52–T62 |
| C2 HEAD vacueux | ACCEPTED | Proposition Codex formalisée. Contrôle géométrique dans le fit figé, avant ALT : min sur 16 profils de signes de f_E >= 0.80. Contrôle de détectabilité de `ONLINE_PREFIX_MIX` : U_PREFIX <= 0.80 H à 1 − α/3. Statuts séparés et traduction déterministe vers §9.3. H2, δ_NI, Φ et la multiplicité restent inchangés. Précision ajoutée : la règle porte sur f_E (univers partagé par INFO et PREFIX) ; f_pop est rapportée. | §4 | T63–T67 |
| C3 staging et smoke | ACCEPTED | `--output-dir` libre, identités indépendantes des chemins et des jobs ; publication complète et atomique ; gel de R1 et de tous les paramètres avant le premier GO runtime ; smoke de bout en bout (identités, reprise) avant tout profil. | §5 | T56, T60, T68 |

## 2. Application à la v2 (passages remplacés ou complétés)

| Passage v2 | Action | Par |
| --- | --- | --- |
| En-tête « Statut » | complété | statut ci-dessus |
| §2.3 graphe d'appels, lignes `main(argv)` à `pour chaque setup` | remplacé | §3.1 |
| §2.4 interfaces | complété | §3.8 |
| §4.1 formules `setup_id` et `policy_id` | remplacé | §3.2 |
| §4.4 ordre par setup | remplacé | §3.1 |
| §5 ligne `F_HEAD_RESIDUAL` | complété | §4.1 |
| §9.3 hypothèse H2 et libellés | complété | §4.3, §4.4 |
| §11.3 diagnostics | complété | §4.1 |
| §12 paramètres | complété | §6 |
| §13 puces « Identité scientifique », « Télémétrie » (exclusions), « Partitions », « Fichiers publiés » | remplacé | §3.2–§3.7 |
| §14 premier point (garde) | remplacé | §3.4 |
| §14 clause smoke | remplacé | §5 |
| §15 | complété | §7 (T52–T68) |
| §17 enveloppe et faisabilité | complété | §5 |
| §18 ligne C | remplacé | §5 |
| §20 R1 (échéance) | remplacé | §5, §8 |
| `plan-32.md` §4.1 l. 272–273, §13, §14 (C32-R3 : `specification_sha256`, `run_id`, `lineage`) | remplacé | §3 : `specification_sha256` ≡ `design_id` ; `run_id` ≡ `design_tag` ; `lineage` ≡ descripteur de réalisation |

Corrections de réception conservées sans changement, et sans calcul relancé ici :
- C32-R1 : puissance TOST bilatérale avec z_{1−β/2} ; chiffres §10 ; témoin T21.
- C32-R2 : loi Beta de F_cond sous maxima iid continus sachant setup/politique ; échangeabilité seule pour la borne de rang.
- C32-R4 : `pdb.q_plugin(V_hat_E.T @ Delta, lambda_hat_E)` ; QR d'une matrice dont la première colonne 1/sqrt(N) est imposée avant factorisation, jamais remplacée ; branches numériques de Tango explicites.

## 3. C1 — `design_id` autorisable, réalisation a posteriori

### 3.1 Séquencement (remplace §2.3 en tête et §4.4)

```
config + mode ─> design_descriptor (§3.3) ─> design_id = SHA-256(canon) ; design_tag = run_id = design_id[:16]
   (aucun tirage, aucun worker, aucune écriture ; `--describe` imprime design_id et le descripteur)
   ▼
authorize (pilot|full) : stage, design_id, GO {chemin, sha256} présent, concordant, citant design_id ; --jobs <= jobs_max
   ▼   refus ⇒ AuthorizationRefused, aucun effet de bord
open_staging : <log-dir>/staging/<design_tag>/design.json (atomique ; existant ⇒ même design_id, sinon StagingMismatch)
   ▼
SETUP     : frame(N) (tirage), FIT_NULL (tirage), sous-ensembles statiques, géométrie HEAD (§4.1)   ─> phases/SETUP.json
   ▼
DEV       : DEV_LIB, DEV_NULL, DEV_ALT ─> qbar, d_dev, s2_dev, dev_id                              ─> phases/DEV.json
   ▼
CAL       : CAL_NULL de toutes les politiques ─> seuils, calibration_id                            ─> phases/CAL.json
   ▼
NULL_PLAN : full, setup primaire ; smoke réduit ; pilote NOT_APPLICABLE ─> plan_id, n_hold <= n_cap ─> phases/NULL_PLAN.json
   ▼
HOLD      : n_hold (primaire full) ou tailles du design ─> premiers franchissements                ─> phases/HOLD.json
   ▼
ALT       : familles ─> premiers franchissements, masques hachés, diagnostics hors ligne          ─> phases/ALT.json
   ▼
FINAL     : payloads ─> realization_id ─> manifest.json, summary.md, telemetry.json dans un répertoire temporaire frère
            ─> os.replace vers --output-dir ─> phases/FINAL.json
```

SETUP est la première phase réalisée : elle précède DEV dans la séquence `design authorization -> DEV -> CAL ->
NULL_PLAN -> HOLD -> ALT -> final manifest`.

### 3.2 Identités avant et après exécution (remplace §4.1 `setup_id`/`policy_id` et §13 « Identité »)

| Identité | Calculable | Contenu | Exclu |
| --- | --- | --- | --- |
| `design_id` (SHA-256 hex) | avant tout tirage, worker, écriture | descripteur §3.3 | authorization, GO, `--jobs` réel, chemins, hôte, heure, télémétrie, toute valeur réalisée |
| `design_tag` = `run_id` | avant | 16 premiers hex de `design_id` | — |
| `seed_plan_sha256` | avant | toutes les clés planifiées, HOLD jusqu'à n_cap | n_hold réalisé |
| `policy_rule_id` | avant | règle : ordre, coût, γ_M, w, repli, égalités, règle s2, règle de sous-ensemble (FULL_K, EIGENMEAN, CPV90, RESIDUAL_CPV90, DEV_PREFIX, EXANTE) | sous-ensemble ou prior réalisés |
| `setup_id` | après SETUP | sha16{design_id, arm, N, fit_id, application, universe_pcs, basis_sha (tirage frame), fit_hash ou None} | famille |
| `head_geometry` | après SETUP | f_E(s), f_pop(s) pour les 16 profils, statut (§4.1) | ALT |
| `dev_id` | après DEV | sha16{setup_id, dev_library_id, qbar_sha, d_dev, s2_dev, dev_calibration_ids} | famille d'évaluation |
| `policy_id` | après DEV | sha16{policy_rule_id, sous-ensemble, prior et s2 réalisés} ; nom hors identité | famille |
| `calibration_id`, seuil h | après CAL | v2 §4.1 inchangé (sans famille pour les non-oracles) | famille (non-oracle) |
| `plan_id`, n_hold | après NULL_PLAN | comptes nuls, plug-ins, n_req, n_hold <= n_cap, statut | ALT |
| `phase_digest[P]` | après la phase P | SHA-256(canon{design_id, P, digests amont, liste triée (clé canonique, SHA du payload), objets dérivés}) | chemins, jobs, télémétrie |
| `realization_id` | après ALT, avant publication | §3.6 | §3.6 |

L'invariance A1 est intacte : aucune identité non-oracle ne contient de famille.

### 3.3 Descripteur de design

**Contenu** (`pdb.canon`, clés triées) :
- `schema_version = "pca_info_online/1"` ; `mode` ∈ {smoke, pilot, full} ; `campaign` ∈ {SMOKE, PILOT, FULL}.
- Configuration scientifique canonique :
  - paramètres §12 (v2 et v2.1) ;
  - applications et univers ;
  - familles (supports, poids, lois de signes) ;
  - politiques et grilles ;
  - règles DEV (bibliothèque, grilles d et s2, critères, égalités) ;
  - règle NULL_PLAN (η, β, n_min, n_plan, n_cap) ;
  - tailles maximales par rôle et par setup ;
  - B bootstrap ;
  - famille Φ ;
  - règle de statut nul ;
  - seuils κ_geo et κ_det.
- Portée : setups (arm, N, fit_id), applications, politiques, familles, rôles.
- Enveloppe maximale : `memory_max_gib`, `cpu_hours_max`, `wall_seconds_per_invocation`, `jobs_max`.
- Graine racine et `seed_plan_sha256`.
- `spectrum_sha` (formule λ, sans tirage).
- Code : {chemin relatif : SHA-256} de la liste fixe (script, `experiments/pca_drift_benchmark.py`,
  `jepadrift/pipelines.py`, `jepadrift/representations/pca.py`, modules atteints).
- Environnement : python, numpy, scipy, pandas, pyyaml, statsmodels, BLAS, variables d'environnement requises.

**Exclu** :
- le bloc `authorization` ;
- le GO (chemin, contenu, SHA) ;
- `--jobs` réel, `--output-dir`, `--log-dir`, `--resume` ;
- hôte, heure, PID, télémétrie, sorties antérieures ;
- toute valeur réalisée : base tirée, fit, sélections DEV, seuils, n_hold, SHA de partitions.

Une limite modifiée change `design_id` et invalide la correspondance au GO. Un `--jobs` réel <= `jobs_max` ne change rien.

### 3.4 Autorisation (remplace §14 premier point)

- Pour `--mode pilot|full`, un bloc `authorization = {stage, design_id, go_reference: {path (POSIX relatif), sha256}}`
  est exigé. Il est vérifié avant tout tirage, toute création de staging, toute écriture et tout lancement de worker.
- Conditions d'acceptation :
  - `stage` = mode ;
  - `authorization.design_id` = `design_id` recalculé ;
  - le fichier GO existe, son SHA concorde, et son texte contient `design_id` verbatim (64 hex) ;
  - `--jobs` <= `jobs_max`.
- Toute autre situation lève `AuthorizationRefused`, y compris un bloc nul avec une configuration complète.
- La portée et les limites sont liées par `design_id`. Le GO cite aussi un résumé lisible de cette portée.
- La référence GO est consignée dans le manifeste (`authority`), hors de `design_id` et de `realization_id`.
- Aucune réautorisation rétroactive d'une réalisation. Un changement de design exige un nouveau `design_id`, un nouveau
  GO et un nouveau staging.
- La garde n'accorde rien : c'est un fil-piège, sans signature inventée. Smoke : pas de garde de code ; le GO runtime
  Codex procédural cite le `design_id` donné par `--describe`.

### 3.5 Staging, états, reprise (remplace §13 « Partitions »)

**Emplacements.**
- `--log-dir` par défaut : `logs/pca_info_online/<basename(--output-dir)>`.
- Staging : `<log-dir>/staging/<design_tag>/`. Il contient `design.json`, `phases/<PHASE>.json`, `partitions/`,
  `status.json` et `telemetry/` (exclu des identités).

**Enregistrement de phase** : {design_id, phase, digests amont, partitions (clé canonique, SHA-256, n_rows), objets
dérivés, `phase_digest`}. Objets dérivés par phase :
- SETUP : setup_ids, empreintes de base et de fit, sous-ensembles statiques, géométrie HEAD ;
- DEV : qbar, d_dev, s2_dev, dev_id ;
- CAL : table des seuils et calibration_id ;
- NULL_PLAN : comptes, plug-ins, n_req, n_hold, statut, plan_id ;
- HOLD et ALT : listes de partitions.

Écriture : fichier temporaire dans le même répertoire, fsync, `os.replace`.

**Partitions.** Fingerprint = SHA-256(canon{design_id, clé de partition, digests des phases amont}). Écriture npz puis JSON,
chacun en tmp + fsync + `os.replace`, JSON en dernier.

| Dernier état valide | Reprise | Refus |
| --- | --- | --- |
| aucun staging | crée `design.json`, puis SETUP | — |
| `DESIGN_FIXED` | SETUP | `design.json` ≠ design_id ⇒ `StagingMismatch` |
| `SETUP_DONE` | DEV | design_id, digest ou partition incohérents ⇒ `PartitionMismatch` |
| `DEV_DONE` | CAL ; DEV jamais recalculé | idem |
| `CAL_DONE` | NULL_PLAN ou HOLD ; seuils chargés, jamais recalibrés | partition CAL manquante ou altérée |
| `NULL_PLAN_DONE` / `NOT_APPLICABLE` | HOLD avec n_hold enregistré | n_hold > n_cap, n_hold < n_min, digest CAL différent |
| `HOLD_DONE` | ALT | idem |
| `ALT_DONE` | FINAL | partition planifiée absente ⇒ `INCOMPLETE`, aucune publication |
| `PUBLISHED` | idempotent si le manifeste publié concorde | manifeste d'un autre design ⇒ `OutputExists` |

Règles générales :
- Un staging existant sans `--resume` lève `OutputExists`.
- Le record d'une phase sans le record d'une phase antérieure applicable lève `PhaseOrderError`.
- Un record existant est chargé et vérifié (SHA des partitions recalculés), jamais recalculé.
- Une phase sans record est calculée en réutilisant les partitions valides et en refusant les divergentes.
- Échéance par invocation, registre CPU cumulé >= `cpu_hours_max` ou `--jobs` > `jobs_max` ⇒ `ResourceBlocked` ou
  refus. `status.json` = {dernière phase complète, partitions manquantes, `BLOCKED_RESOURCE` | `INCOMPLETE`}, conservé et
  reprenable sous le même `design_id` et le même GO.
- Aucune refonte générique du runner : une dizaine de fonctions dans le script.

### 3.6 Réalisation et publication (remplace §13 « Fichiers publiés »)

1. Après `ALT_DONE`, les payloads scientifiques sont écrits via `save_fair_csv` (`calibration.csv`, `selections.csv`,
   trials ou résumé compact, `aggregates.csv`, `issues.csv`). Destination : `<parent(--output-dir)>/.<basename>.publish-<design_tag>.tmp/`.
   Ils portent `design_id`, jamais `realization_id`.
2. Descripteur de réalisation = {design_id, `phase_digest` de chaque phase applicable (NULL_PLAN : digest ou
   `NOT_APPLICABLE`), dev_ids, `thresholds_sha`, plan_id et n_hold (ou null), payloads {nom de base : SHA-256}}.
   `realization_id` = SHA-256(`pdb.canon`(descripteur)).
3. Exclusions de `realization_id` : `manifest.json`, `summary.md`, `telemetry.json`, figures, référence d'autorité, tout
   chemin autre que les noms de base des payloads, jobs, hôte, heures.
4. Normalisation : noms POSIX relatifs au répertoire de publication ; clés de partition en JSON canonique ; hex minuscule.
5. Le répertoire temporaire reçoit ensuite :
   - `manifest.json` : descripteur de design, `design_id`, descripteur et `realization_id`, `authority` (stage, chemin et
     SHA du GO, ou référence runtime smoke), payloads avec statut `PUBLISHED` ou `LOCAL_HASHED_ONLY`, `status = COMPLETE` ;
   - `summary.md` et `telemetry.json`.
   Puis fsync, `os.replace(temporaire, --output-dir)` (cible absente ou vide, sinon `OutputExists`), puis
   `phases/FINAL.json`.
6. Crash avant `os.replace` : `--output-dir` intact, le temporaire est reconstruit à la reprise. Crash après remplacement
   et avant `FINAL.json` : la reprise vérifie le manifeste publié (même design_id, realization_id recalculé égal) puis
   écrit `FINAL.json`. Un manifeste n'est jamais réécrit pour ajouter une identité.

### 3.7 `run_id` et noms

- `run_id` ≡ `design_tag`, connu avant exécution. Il ne sert qu'au staging et au nom temporaire de publication.
- `realization_tag` (16 hex de `realization_id`) n'existe que dans le manifeste après FINAL. Aucun répertoire ni nom de
  fichier ne dépend de `realization_id`.
- Deux designs ont deux tags : aucune collision. Le même design publié dans deux `--output-dir` a deux stagings
  indépendants, avec des identités et SHA identiques.

### 3.8 Interfaces ajoutées (complète §2.4)

- `design_descriptor(cfg, mode) -> dict` et `design_id(desc) -> str` : purs, sans tirage ni écriture.
- `authorize(mode, cfg, desc, jobs) -> dict` : vérifications §3.4, sans effet de bord.
- `open_staging(log_dir, desc, resume) -> Path` ; `phase_record(staging, phase, upstream, partitions, derived) -> dict`.
- `realization(records, payload_shas) -> (realization_id, descriptor)` ; `publish(temp_dir, output_dir)`.
- `head_geometry(frame, fit, istar, universe) -> dict` ; `head_control(u_prefix, geometry, kappa_det, kappa_geo, H) -> dict`.
- CLI : ajout de `--describe` ; `--output-dir`, `--log-dir`, `--jobs` et `--resume` restent hors identités.

## 4. C2 — Contrôle HEAD non vacueux, fit figé

H2, δ_NI = 0.10, supports, H, I*, w, Φ, comparateurs et multiplicité sont inchangés.

### 4.1 Géométrie (complète §5 et §11.3 ; phase SETUP, avant tout ALT)

Calcul pour chaque setup résiduel et chaque s ∈ {±1}⁴ (16 profils ; s et −s donnent la même valeur) :
- Δ(s) = Σ_j s_j sqrt(2 (I*/4) λ_{k_j}) v_{k_j}, avec (k_j) = (2, 3, 4, 5) dans le repère population ;
- β̂(s) = Λ̂_E^{-1/2} V̂_E' Δ(s) ;
- C0 = Λ̂_E^{-1/2} V̂_E' Σ0 V̂_E Λ̂_E^{-1/2} ;
- P4 = les quatre premiers axes éligibles ajustés (PC ajustées 2..5) ;
- I_J(S; s) = ½ β̂_S(s)' [C0_SS]^{-1} β̂_S(s) (`pdb.kl_mean`) ;
- f_E(s) = I_J(P4; s)/I_J(E; s) ; f_pop(s) = I_J(P4; s)/I*.

**Règle (NEW_PROPOSAL).** `GEOMETRY_ALIGNED` ssi I_J(E; s) > 0 pour tout s et min_s f_E(s) >= κ_geo = 0.80. Sinon
`DESIGN_CONTROL_INCONCLUSIVE`.

**Rapporté** : les 16 valeurs, min, moyenne et max de f_E et f_pop. En EXACT, f_E = f_pop = 1 identiquement.

**Justification statique.**
- La règle porte sur l'univers E_res, que INFO et PREFIX partagent, et sur le pire profil de signes : aucun tirage
  favorable n'est retenu.
- f_pop montre les fuites hors de E_res.
- κ_geo = 0.80 définit « favorable au préfixe » comme au moins 80 % de l'information jointe disponible captée par le
  préfixe canonique de longueur 4. Aucune issue n'est prédite.

**Portée et isolement.**
- Le contrôle concerne le préfixe canonique ajusté, pas la sélection adaptative de `ONLINE_PREFIX_MIX`.
- Les grandeurs vraies (Σ0, V, Λ) restent hors ligne : jamais en sélection non-oracle, calibration ou choix du fit.
- Un échec n'entraîne ni re-tirage de fit ou de direction, ni changement d'amplitude, de support ou d'univers.

### 4.2 Détectabilité (après ALT ; composante d'intersection–union)

- U_PREFIX = borne supérieure unilatérale bootstrap percentile apparié, à 1 − α/3, de RMST_H(`ONLINE_PREFIX_MIX`) sur
  F_HEAD (setup primaire, mêmes tirages d'indices que H2).
- `PREFIX_DETECTABLE` ssi U_PREFIX <= κ_det H, avec κ_det = 0.80, soit 200 jours à H = 250 (NEW_PROPOSAL).

**Justification statique.**
- κ_det H = 200 < H/(1 + δ_NI) = 227.27 : le contrôle reste hors de la zone vacueuse.
- Sous `PREFIX_DETECTABLE`, la non-infériorité exige E[min(T_INFO, H)] < 1.10 × 200 = 220 < H. Elle échoue donc si
  INFO ne détecte jamais.
- min(T, H) >= H·1[T > H] implique P(T <= H) >= 1 − RMST_H/H >= 0.2, au-delà du niveau nominal 0.05.

### 4.3 Statuts H2 (complète §9.3)

- `H2_NONINFERIORITY_SUCCESS` : borne bootstrap à 1 − α/3 de E[min(T_INFO, H) − 1.10 min(T_PREFIX, H)] < 0
  (inégalité censurée, inchangée).
- `HEAD_POSITIVE_CONTROL_VALID` = `GEOMETRY_ALIGNED` ∧ `PREFIX_DETECTABLE`.

| Condition | Libellé H2 |
| --- | --- |
| `NULL_FAILED` (INFO ou PREFIX) ou précondition déterministe en échec | `INVALID_NULL_FAILED` |
| non `H2_NONINFERIORITY_SUCCESS` | `NOT_ESTABLISHED` (validité du contrôle rapportée) |
| succès NI, contrôle non valide | `NONINFERIORITY_NOT_PROBATIVE`, avec `DESIGN_CONTROL_INCONCLUSIVE` et/ou `PREFIX_DETECTABILITY_NOT_ESTABLISHED` |
| succès NI, contrôle valide, (b) atteint | `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR` |
| succès NI, contrôle valide, (b) non atteint | `CONFIRMED_AT_COMMON_NOMINAL_ALPHA_ONLY` |

Toujours rapportés : estimation et IC nominal 95 % de RMST_INFO − RMST_PREFIX, borne NI, U_PREFIX, statistiques
géométriques, statuts nuls. `NONINFERIORITY_NOT_PROBATIVE` n'autorise aucune conclusion sur les cas où le préfixe est bon.

### 4.4 Multiplicité

- m = 3 inchangé.
- Les libellés confirmés de H2 sont une intersection–union de {NI à α/3, détectabilité à α/3, (b) à α/3 pour le libellé
  le plus fort}, plus la géométrie et les préconditions, qui sont déterministes et ne consomment pas d'erreur.
- Niveau α/3, FWER approximatif <= 0.05 (Bonferroni) inchangé ; composantes asymptotiques ; aucune hypothèse ajoutée.
- H1 et H3 inchangées.

## 5. C3 — Staging, gel avant runtime, smoke futur (remplace §14 clause smoke, §18 ligne C, échéance de §20 R1)

**Sorties et publication.**
- `--output-dir` est une destination libre (absente ou vide), jamais une identité.
- `--log-dir` et `--jobs` sont hors identités.
- Staging par log-dir (§3.5) ; publication seulement complète et atomique (§3.6).
- `INCOMPLETE` et `BLOCKED_RESOURCE` restent dans `status.json`, sans publication.

**Gel.**
- Doivent être écrits dans la configuration dont le `design_id` est cité par le premier GO runtime (smoke) :
  - R1 : setup primaire FITTED_LW_GAUSSIAN N = 239 fit 0, F2, H2 avec δ_NI = 0.10, H3, m = 3 ;
  - I*, w, s2_common, grille et critère s2_dev ;
  - supports, poids et lois de signes ;
  - κ_geo, κ_det ;
  - règle NULL_PLAN, tailles maximales, enveloppe.
- Ce gel précède toute consultation de puissance smoke ou pilote.
- Aucun paramètre listé ne change après lecture d'une sortie ALT smoke ou pilote. Un changement exige un nouveau
  `design_id`, une justification non informée par ALT et un nouveau GO.
- Seuls les éléments budgétaires du full (n_cal de P_conf, n_cap, n_alt, enveloppe, R3–R5) peuvent s'appuyer sur les
  discordances nulles du pilote et les coûts mesurés, jamais sur ALT.

**Smoke et fixtures.**
- `SMOKE_NO_CLAIMS` est purement fonctionnel : les sorties ALT du smoke exercent le pipeline et ne sont jamais lues pour
  une décision.
- Les fixtures TDD sont des témoins fonctionnels bornés, jamais une source de réglage.

**Lot C** (nouvelle ligne §18, sous GO runtime Codex distinct citant le `design_id` smoke) :
1. smoke de bout en bout, NULL_PLAN réduit inclus : contrôle de `design_id`, `realization_id` et de la publication atomique ;
2. interruptions induites après SETUP, DEV, CAL et NULL_PLAN puis reprise : même `realization_id`, aucune recalibration ;
3. `--jobs 1` et `--jobs 8` vers deux `--output-dir` distincts : identités et SHA scientifiques égaux ;
4. seulement ensuite, profil 1/4/8/12 ; 16 plus tard, sous GO, selon charge et RAM.

Les unités du §17 restent des prévisions non mesurées ; aucun coût n'est garanti.

## 6. Paramètres ajoutés (complète §12)

| Paramètre | Valeur | Provenance |
| --- | --- | --- |
| κ_geo | 0.80 sur min_s f_E(s), préfixe ajusté canonique de longueur 4, 16 profils ; f_pop rapportée | NEW_PROPOSAL |
| κ_det | 0.80 : U_PREFIX <= κ_det H, borne bootstrap à 1 − α/3 | NEW_PROPOSAL |
| enveloppe dans le descripteur | `memory_max_gib`, `cpu_hours_max`, `wall_seconds_per_invocation`, `jobs_max` ; valeurs proposées v2 §17 (32 Gio, pilote 4 CPU-h, 2700 s, 8) | NOTIFICATION_DECISION (structure) ; NEW_PROPOSAL (valeurs) |
| NULL_PLAN smoke | n_plan = n_min = 40, n_cap = 80 | NEW_PROPOSAL |
| emplacements | `--log-dir` par défaut `logs/pca_info_online/<basename(--output-dir)>` ; `staging/<design_tag>` ; publication temporaire sœur puis `os.replace` | NEW_PROPOSAL |

## 7. Tests ajoutés (complète §15)

T1–T51 sont conservés avec les amendements de réception : T21 (C32-R1) et T47 (C32-R3, précisé par T52–T56). Tous les
nouveaux tests sont déterministes et utilisent des fixtures minuscules dans `tmp_path`.

**C1 — identités, autorisation, staging**
52. `test_design_id_computable_before_any_draw` :
    - `design_descriptor`, `design_id` et `--describe` sont appelés sous fils-pièges (SeedSequence, default_rng,
      ProcessPoolExecutor, écritures) ⇒ aucun appel ;
    - clés du descripteur = liste blanche : aucun dev_id, seuil, n_hold, basis_sha, fit_hash, SHA de partition,
      authorization, GO, jobs ni chemin ;
    - n_cap, enveloppe, portée, graines, code et environnement présents ; résultat déterministe.
53. `test_pilot_full_authorization_without_future_digests` :
    - fixtures pilote et full ; GO de fixture rédigé depuis le seul `design_id` ⇒ exécutions acceptées ;
    - deux graines racines ⇒ deux designs ; les valeurs réalisées d_dev, s2_dev, n_hold n'apparaissent jamais dans
      l'autorisation ni dans le GO ;
    - le manifeste porte le `design_id` autorisé et un `realization_id` calculé après coup.
54. `test_altered_design_code_seed_limit_refused_before_side_effects` :
    - GO valide pour C, puis altération de la graine, de I*, de n_cap, de `jobs_max`/échéance, ou d'un fichier de code
      (liste pointée vers une copie altérée d'un octet) ⇒ `AuthorizationRefused` ;
    - aucun tirage, aucun pool, aucun fichier ni répertoire créé.
55. `test_go_reference_absent_mismatched_or_not_citing_design_refused` :
    - bloc nul avec configuration complète, GO absent, SHA différent, texte sans `design_id`, stage différent,
      `--jobs` > `jobs_max` ⇒ refus sans effet de bord ;
    - smoke sans bloc accepté (garde procédurale).
56. `test_identities_independent_of_output_dir_jobs_and_telemetry` :
    - même design vers deux `--output-dir` avec `--jobs 1` et `--jobs 3` ⇒ `design_id`, `realization_id` et SHA des
      payloads égaux ;
    - deux stagings distincts, chacun a calculé ses partitions (compteurs > 0) ; la télémétrie diffère sans effet.
57. `test_crash_after_setup_dev_cal_null_plan_resume_same_realization` :
    - crash injecté après SETUP, DEV, CAL puis NULL_PLAN, suivi de `--resume` ⇒ `realization_id` égal à celui d'une
      exécution ininterrompue ;
    - zéro appel à `rank_threshold` à la reprise après CAL ; zéro recalcul de d_dev/s2_dev après DEV.
58. `test_phase_and_partition_inconsistency_refused` :
    - cas : `design.json` d'un autre design, digest amont altéré, n_hold > n_cap ou < n_min, HOLD sans NULL_PLAN en full,
      partition altérée d'un octet, JSON sans npz ;
    - résultat : `StagingMismatch` / `PhaseOrderError` / `PartitionMismatch`, aucune publication, `--output-dir` intact.
59. `test_realization_id_excludes_manifest_and_paths` :
    - recalcul depuis les payloads publiés, `manifest.json`, `summary.md` et `telemetry.json` exclus ⇒ égal au manifeste ;
    - payloads sans `realization_id` ; réécrire summary ou télémétrie ne le change pas ;
    - noms POSIX relatifs seulement, aucun chemin absolu.
60. `test_publication_atomic_and_incomplete_status` :
    - partition planifiée manquante ⇒ `INCOMPLETE`, aucune publication ;
    - crash avant `os.replace` ⇒ `--output-dir` intact, puis publication identique à la reprise ;
    - crash après `os.replace` ⇒ reprise idempotente ;
    - `--output-dir` non vide ou manifeste d'un autre design ⇒ `OutputExists`.
61. `test_run_id_is_design_tag_and_no_path_uses_realization` : `run_id = design_id[:16]` connu avant exécution ; aucun
    nom ne dépend de `realization_id`.
62. `test_envelope_enforced_without_identity_change` :
    - `--jobs` <= `jobs_max` sans effet sur `design_id` ; au-delà, refus ;
    - registre CPU >= `cpu_hours_max` ou échéance ⇒ `ResourceBlocked`, état reprenable ;
    - modifier une limite change `design_id`.

**C2 — contrôle HEAD**
63. `test_head_all_censored_never_positive_control` : T_INFO = T_PREFIX = H partout ⇒ succès NI brut (−0.1 H < 0),
    U_PREFIX = H > 0.8 H, libellé `NONINFERIORITY_NOT_PROBATIVE`, jamais `CONFIRMED_*`.
64. `test_head_geometry_exact_and_misaligned_fit` :
    - EXACT ⇒ f_E = f_pop = 1 pour les 16 profils, f(s) = f(−s) ;
    - base ajustée de fixture tournant l'information hors des quatre premiers axes ⇒ min f_E < 0.80 ⇒
      `DESIGN_CONTROL_INCONCLUSIVE` ;
    - un seul appel de fit ; Δ, supports, amplitude et univers inchangés ; calcul en SETUP avant toute partition ALT ;
    - I_J(E) = 0 ⇒ inconclusif.
65. `test_head_thresholds_frozen_and_diagnostics_isolated` :
    - κ lus dans le descripteur seulement ; les changer change `design_id` ;
    - partitions ALT d'autres familles et répertoire smoke empoisonnés sans effet ;
    - fil-piège : géométrie et U_PREFIX jamais passés à la sélection, la calibration ou le fit.
66. `test_head_valid_control_but_noninferiority_fails` : contrôle valide et RMST_INFO > 1.10 RMST_PREFIX ⇒
    `NOT_ESTABLISHED`, contrôle rapporté valide, aucune confirmation.
67. `test_head_threshold_boundaries_null_qualification_and_multiplicity` :
    - U_PREFIX = 0.8 H accepté, `nextafter` supérieur refusé ; min f_E = 0.80 aligné, `nextafter` inférieur inconclusif ;
    - `NULL_FAILED` de INFO ou PREFIX ⇒ `INVALID_NULL_FAILED` ;
    - (b) atteint ou non ⇒ les deux libellés confirmés ;
    - H2 reste l'une de m = 3 au niveau α/3.

**C3 — gel**
68. `test_smoke_or_prior_outputs_cannot_inform_design` :
    - `design_id` identique avec ou sans répertoires smoke/pilote antérieurs empoisonnés ;
    - AST : `design_descriptor` et le chargement de configuration ne lisent ni `results/` ni `logs/`.

Matrice totale : 68 tests. Les tests de répertoires, de jobs et de publication incomplète de la disposition Codex sont
couverts par T56 et T60.

## 8. Seules propositions nouvelles à geler avant tout runtime

1. Contenu et exclusions du descripteur de `design_id`, enveloppe et bornes comprises (§3.3).
2. Garde d'autorisation : stage, `design_id`, GO présent / SHA / texte citant `design_id`, `--jobs` <= `jobs_max` (§3.4).
3. Emplacements : `--log-dir` par défaut, `staging/<design_tag>`, publication temporaire sœur et `os.replace` (§3.5–§3.6).
4. Contenu, exclusions et normalisation de `realization_id` (§3.6).
5. Machine d'états et règles de refus de reprise (§3.5).
6. κ_geo = 0.80 sur min f_E (16 profils, préfixe ajusté canonique de longueur 4), f_pop rapportée.
7. κ_det = 0.80 : U_PREFIX <= 0.8 H à 1 − α/3.
8. Traduction des statuts H2 (§4.3).
9. NULL_PLAN réduit du smoke : n_plan = n_min = 40, n_cap = 80.

Règle d'échéance associée : R1 et tous les paramètres listés au §5 sont gelés avant le premier GO runtime. R2–R5 sont
inchangés (GO pilote, tailles full, variante exacte, couche OUTER_FIT).

## 9. Porte

`TECHNICAL_GO = NOT_GRANTED_PENDING_V2_1` ; `PILOT_GO = ABSENT` ; `FULL_GO = ABSENT`.

Prochaines étapes, toutes à Codex :
1. revue de cet amendement v2.1 et de la matrice T1–T68 ;
2. enregistrement du plan canonique `prompts/plans/plan-32.md` réconcilié ;
3. décision technique écrite séparée.

Aucun GO technique, pilote ou full n'est accordé ni supposé par ce texte ; aucun « Ready to code ».
