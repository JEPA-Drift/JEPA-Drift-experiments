# Plan canonique — Stream 32 PCA-INFO-ONLINE (v2.1, réception Codex, 2026-11-14)

> **Statut.** Réception de la révision native v2.1, dans la même session Phase A, sous les notifications du chercheur
> n°14 et n°15 et leurs dispositions Codex. Ce document et son amendement lié forment le plan normatif :
> il remplace intégralement le v1, aucune section v1 ne reste applicable. Statuts : `TECHNICAL_GO =
> R_A_B_GATED` (§21, activation initiale R), `PILOT_GO = ABSENT`, `FULL_GO = ABSENT`. Tout réglage scientifique nouveau reste
> préenregistrable et n'autorise aucun pilote. Production de la version native : lectures, `sha256sum` et `git rev-parse` seulement ; aucun code,
> test, import Python, smoke, pilote, full ni Git en écriture. Codex enregistre `prompts/plans/plan-32.md`, fait sa revue
> et décide d'un GO technique écrit distinct. Aucun « Ready to code » n'a été approuvé dans la session native.
>
> Capture native : `ex-cute-la-mission-de-gleaming-bird.md`, SHA-256
> `79293fa331d0ba3493ba40037be98f7b0cef8e1337313e783ab1424b3b34f641`, 798 lignes, conservée intacte.
> La réception intègre C32-R1 à C32-R6 et [l'amendement natif v2.1](plan-32-v2.1-amendment.md), SHA-256
> `d6d5866ff2fa1669fcb86641263b0fff68cb95b13aef7726f2dfe786b90219e9`.
> Préséance : sections réconciliées de ce plan et §21, puis amendement v2.1, puis v2 native.

## Autorités et empreintes (SHA-256 vérifiés en lecture seule le 2026-11-14)

| Rang | Pièce | SHA-256 |
| --- | --- | --- |
| 1 | Notification chercheur `prompts/14_CODEX_REVIEW_STREAM32_PLAN_20261114.md` | `2ae0d422b1463660467ad59af1bfd61a9209c74c95195b0dd9bbbfecd1c31abd` |
| 2 | Disposition Codex `prompts/REVIEW-stream-32-plan-v1-20261114.md` (non suivi) | `e82529a3c9696a326c574dbb520962344e0d584ac3a7c9716cdc1747ba6e349d` |
| 3 | Spec `prompts/streams/prompt-32-pca-info-online.md` (non suivi) ; ses lignes 2..fin | `db2ef8717e56d36b41a7ff805cea8a21c57ab9fcafd5d56ec96e9b21ab97201b` ; `15a3003864e43c275fb2c6ce3113d4180e4cbc771b011f9bdbc60dbeb8784b96` |
| 4 | Amorçage `prompts/streams/13_CODEX_AMORCAGE_PCA_INFO_ONLINE_2026_11_14.md` ; GO planning `prompts/GO-stream-32-planning-20261114.md` | `6c047b4447d752462efb687e7b1192a3df503f572d37405099e7738386bb4b9d` ; `ccdd9c872197dabe553c5bf6458cfa218f4f252590b9030f11c442ca127471b4` |
| 5 | Protocole local révisé du checkout principal, `prompts/Protocole Codex.md` | `5eb63af813eb5e1af04c344b24f8662329c1abb04d38412fc9512c476770dae8` |
| 6 | Dix objections antérieures `logs/stream-32/mission-phase-a-v2.md` ; mission v2 `logs/stream-32/mission-researcher-review-v2.md` (locaux) | `fa08585fffdd0513e91bc1cb6a65f42b797b7c6e7b75fe27d2cd0715df253673` ; `95b84a6c0e78ee180a6b1d600e0ead1f106402118496fac9140a65f42cf48dfa` |
| — | Archive native v1 `pasted-content-id-9c4b-mission-polymorphic-scott.md` (base non approuvée) | `35bd58e1d1267ff08940e5faca8987d628a9833570217e5042bb8485c6580284` |
| — | Audit déterministe Codex `logs/stream-32/review-statistical-check.json` ; `.py` (locaux) | `0d3b9d0356d5424c4652e8e0b35f6f95532fadbe39c1dee9f00519b43bb960a0` ; `2bb7c6c21b1a55b5586f32d2543fe9385c9f414fcfc2674c133fca138d2c5999` |
| — | Scellé `experiments/pca_drift_benchmark.py` (inchangé) | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| — | `tools/check_prompts.py` ; `tests/test_check_prompts.py` ; `prompts/streams/INDEX.md` | `053930fd7a5d85560d3ed701f551999c5c9fc837dd21ace4a306d45498fbbf4c` ; `f65adbea5cd34281fb0955415d67fc6a4edc4121cf4290667941ee29c0ec844a` ; `06c7901135cfd42be2556e095950b6a992479fa6a5eb604c129b48c1be89543f` |
| — | Master `prompts/Prompts_Claude_Code_v5.md` (188 955 octets, 33 titres `## PROMPT `) | `c84d560cfaf821a16892d11cb5ff854f941c09e50a2f07a70026e10d02bdceac` |

Préséance : notification 14 > disposition Codex (exécution de la notification) > contrats de la spec 32 > dix objections
antérieures compatibles > v1. Les SHA historiques restent cités ; les nouveaux SHA (prompt 32 normalisé, master, INDEX,
outils de registre) seront publiés par le lot R.

## Contraintes globales

- Synthétique seulement, changements de moyenne, PCA figée pendant chaque trajectoire. Interdits : JEPA, J4, 2020+,
  données réelles, covariance comme cible principale, refit quotidien, recherche d'intervalles, E2/E3, E4 (producteurs,
  sorties, manifestes), PCA `/2` (producteur et schéma), producteurs et scellés Article B, J1 CRLF.
- `.venv` seul pour tout calcul futur, jamais Trading seul ; avant NumPy : `OMP_NUM_THREADS=MKL_NUM_THREADS=
  OPENBLAS_NUM_THREADS=1`, `MKL_CBWR=COMPATIBLE`, `PYTHONHASHSEED=42`, `MPLBACKEND=Agg`, vérifiés dans le parent et dans
  chaque worker (`pdb.check_env`).
- PRNG locaux `np.random.SeedSequence` par rôle et réplique, indépendants du nombre de workers ; CSV via
  `jepadrift.pipelines.save_fair_csv` ; lectures pandas avec `float_precision='round_trip'`.
- Un noyau déplacé dans `jepadrift/monitors/` serait NumPy seul (aucun déplacement prévu).
- Aucun commentaire hors `# ponytail:`, aucun `# noqa`, aucun filigrane ; code et `docs/sections/` en anglais.
- Aucun choix après lecture d'une puissance alternative ; aucun résultat ALT de campagne consulté avant le GO pilote.

## Correspondance v1 → v2 (aucun paragraphe v1 conservé par empilement)

| v1 | v2 | Nature |
| --- | --- | --- |
| §0 | §0 | remplacé : 23 clos ; blocages 23 et préséance interactive supprimés ; étiquettes de provenance |
| §1 | §2 | remplacé : politiques renommées/ajoutées ; interfaces non-oracle et oracle séparées |
| §2 | §3 | remplacé : oracle surrogate, terme Var0, M proxy, trois objets de calibration |
| §3, §5 | §4, §8 | remplacés : identités sans famille, calibration oracle séparée |
| §4 | §5, §6, §7, §12 | remplacé : F_HEAD, baselines, développement |
| §6 | §9, §10 | remplacé : tri-état nul, Tango principal, famille Φ, NULL_PLAN |
| §7 | §13 | remplacé : N réel, bruit sans famille, télémétrie hors identité |
| §8 | §15 | remplacé : 51 tests |
| §9 | §16 | remplacé : ID artificiel 99, motif corrigé |
| §10 | §17 | remplacé : unités seulement, recompte |
| §11, §12 | §18, §19 | remplacés |
| §13–§15 | §1, §20 | remplacés |

## 0. État vérifié, provenance, sources

- Git (lecture) : `HEAD = main = origin/main = e33ac1d0a9ce77e1a9cbdb1c88836511ec52110a` ; stream 23 clos et publié
  (statut Codex, références locales concordantes). Worktree `stream-32-pca-info-online-20261114` : cinq fichiers non
  suivis, aucun créé par cette session (GO planning, REVIEW v1, copie `prompts/14_CODEX_REVIEW_STREAM32_PLAN_20261114.md`
  au SHA de la notification, amorçage 13, prompt 32). `.venv` et `external` : liens absolus ; `data/raw` : répertoire réel
  vide ; aucun accès aux données prévu.
- Phase A headless native selon le protocole révisé (Skill et commandes slash désactivés). Les clauses v1 « préséance
  interactive » et les blocages liés à la clôture 23 (OOM, essai 64G, QA) sont périmés et retirés.
- Étiquettes de provenance de chaque règle ou valeur : `SOURCE_RULE` (contrat de la spec 32), `SPEC_PROPOSAL` (valeur
  suggérée par la spec, non décidée scientifiquement), `NOTIFICATION_DECISION` (décidé par la notification 14),
  `NEW_PROPOSAL` (ce plan, soumis à Codex/chercheur). Aucun GO déduit d'une source, d'un chemin ou d'une empreinte.
- `REFERENCE_NOT_MOUNTED` : `Réponses_Clarification_Gemini_JEPA_Drift_3.md`, `DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md`
  (non lues, non nécessaires aux équations autonomes). Note 11 présente
  (`prompts/streams/11_PROMPT_CGPT_REORIENTATION_REFERENCE_EXP_PCA_GEMINI.md`) : ses énoncés de « délai exact » sont
  supplantés par le contrat fluide de la spec 32 et jamais réemployés.
- Écarts code existant / spec 32 (résolution : nouvelles identités 32, stream 28 intact) : s2 en `d` du stream 28
  (`pdb._detector`, `experiments/pca_drift_benchmark.py:1083`) contre s2 commun en K ; corde affine 1..20
  (`pdb.affine_costs`, `:98`) contre OLS 1..min(16,K) ; dérive résiduelle du stream 28 sur axes LW figés (`scenario_C`,
  `:495`) contre repère population ; EXANTE synthétique `UNSUPPORTED` au stream 28 contre bibliothèque de développement ;
  6 fichiers de la spec contre 4.
- Constats locaux utiles aux décisions : `pdb.Store` n'est pas atomique (`np.savez` puis JSON sans `os.replace`,
  `:777-792`) et borne la RSS par processus (`:769-775`) ; `pdb.identity_block`/`provenance_block` (`:726-752`) séparent
  déjà identité scientifique et provenance Git ; aucun utilitaire Clopper–Pearson n'existe (`jepadrift/stats/intervals.py:5`
  = Wilson via statsmodels) ; scipy 1.17.1 épinglé (`requirements.txt:2`) ; `memory.peak` d'un scope utilisateur est
  lisible (wrapup 23 : pic agrégé 14 849 028 096 o contre 666 432 KiB pour le plus gros processus, autre code, non
  transférable) ; verrou partagé = `flock` sur `logs/.jepa_execution.lock` du checkout principal.

## 1. Disposition

### 1.1 Notification A1–A3, B1–B3, C

| Obs. | Disposition | Justification technique | v2 § (v1 lignes remplacées) | Tests (§15) |
| --- | --- | --- | --- | --- |
| A1 | ACCEPTED | Aucune politique non-oracle n'a d'argument famille, méta, Δ, τ* ni paramètre vrai ; clés de bruit sans famille ; `calibration_id` = f(setup, politique, n_cal, règle) ; un seuil par (setup, politique) réutilisé pour F0/F1/F2/HEAD ; HOLDOUT évalué une fois ; univers fixé par application. ORACLE : loi par famille, identité séparée, `NON_DEPLOYABLE_ORACLE_CALIBRATION`, FPR séparés. | §4, §8.1 (141, 265–285, 319–323) | T23–T26, T41 |
| A2 | ACCEPTED | `F_HEAD_RESIDUAL` (PC 2–5, q = I*/4, signes Rademacher indépendants, KL pleine I*) ajouté ; F0/F1/F2 gardés ; F3 marché séparé. Famille Φ concentrée et équilibrée figée ici (à geler par Codex avant tout pilote de puissance) : setup FITTED_LW_GAUSSIAN N = 239 fit 0 ; H1 supériorité F2 ; H2 non-infériorité HEAD ; H3 FULL_K sur F2 ; le reste descriptif ; gains contextuels. | §5, §9.3 (241–246, 304–311) | T27–T30 |
| A3 | MODIFIED | Fond accepté. Modalités : tri-état nul CP (qualificatif bloquant, hors famille FWER) ; Tango score principal (asymptotique, algèbre vérifiée par l'audit Codex) ; aucune porte FULL_K ; rôle NULL_PLAN indépendant qui fixe n_hold depuis les nulls (discordance, différence réalisée, puissance, plafond) ; degrés de certitude préenregistrés ; FWER déclaré approximatif. | §8, §9, §10 (287–315) | T17–T19, T21, T31, T32, T43 |
| B1 | ACCEPTED | s2 commun principal ; sensibilité s2_dev (grille {1,4,16,64}·s2_common, critère DEV équilibré, rôles DEV_NULL/DEV_ALT, gelée avant CAL) ; sensibilité γ_M = H/α = 5000 à identités propres ; diagnostic V/RMST descriptif ; ratios de prior apparié. M jamais coût RMST. | §3.3, §3.6, §7, §11 (177–178, 197–201, 236–239) | T15, T16, T33, T34, T49 |
| B2 | ACCEPTED | `FIXED_EIGENMEAN_PREFIX` (renommage) ; CPV90 global intact (`OUTSIDE_UNIVERSE`) ; `RESIDUAL_CPV90` ; `FIXED_DEV_PREFIX` d ∈ {1,2,4,8,16,20} ∩ [1,K] choisi sur DEV équilibré incluant HEAD, un d par setup ; FULL_K ; ex ante = prior structurel de transfert. | §6, §7 (149–153, 247–249) | T35–T37 |
| B3 | ACCEPTED | FITTED : oracle `ORACLE_DIAGONAL_SURROGATE` ; I_joint, c, Var0 hors ligne ; biais ½(c² + (Var0 − 1)/m) avec témoin exact ; diagnostics H0 par axe ; aucune correction depuis le simulateur ; ablation de correction nulle hors architecture ; télémétrie screening, commutations, d_t, alignement, seuil, CPU ; recherche répétée non couverte par M. | §3.1, §3.7, §11.3 (162–167, 203–209, 219–227) | T20, T38–T40, T42 |
| C1 portes, scellés | ACCEPTED | GO technique avant R/A/B ; runtime, pilote, full distincts ; scellés inchangés. | §14, §18 | T47, témoins SHA §19 |
| C2 ressources | ACCEPTED | Unités seulement ; enveloppe agrégée par scope superviseur ; profil après GO runtime. | §17 | T44–T46 |
| C3 registre | ACCEPTED | Lot R après GO ; contrats du prompt 32 inchangés ; amendements tracés `NOTIFICATION_DECISION` dans le plan. | §16 | tests registre §16 |
| C4 références | ACCEPTED | `REFERENCE_NOT_MOUNTED` maintenu. | §0 | — |
| C5 quatre fichiers | ACCEPTED | Noyaux à interfaces explicites et témoins séparés ; extraction au second consommateur. | §2 | T1–T22 |

### 1.2 Dix objections antérieures

| Obj. | Disposition | Traitement v2 |
| --- | --- | --- |
| O1 état, provenance | ACCEPTED | §0 ; étiquettes SOURCE_RULE / SPEC_PROPOSAL / NOTIFICATION_DECISION / NEW_PROPOSAL. |
| O2 IC apparié | MODIFIED (notification) | Tango score principal, domaine complet, branches stables, témoins ; CP–Bonferroni non implémenté ; variante exacte chiffrée (§9.2), décision R4. |
| O3 multiplicité | ACCEPTED | §9.3 : m = 3, Bonferroni α/3, IUT des composantes ; bootstrap et score approximatifs ; aucune alarme OU ; statut de chaque comparaison forte déclaré. |
| O4 estimands, cellules | ACCEPTED | N ∈ {32, 239} dans les deux bras gaussiens, N réel dans les clés ; EXACT simulé indépendamment par N (même loi éligible, réplications) ; cellules EXACT descriptives : aucun double comptage confirmatoire. |
| O5 biais fitted | ACCEPTED (avec B3) | §3.7, §4.3. |
| O6 identités, publication | ACCEPTED | §13. |
| O7 autorisations | ACCEPTED | §14. |
| O8 ressources | ACCEPTED | §17 ; aucune borne RSS par worker présentée comme borne agrégée. |
| O9 registre | ACCEPTED, motif corrigé | `tests/test_check_prompts.py:123-154` monkeypatche `STREAMS` et `EXPECTED_IDS={1,2,3,31}` (l. 130–132) : l'ajout réel de 32 ne casse pas ce test ; le renommage 32 → 99 est retenu pour supprimer la collision sémantique avec le vrai stream 32. |
| O10 architecture | ACCEPTED | §2, §15 : 4 fichiers, tests déterministes, aucun test fondé sur une FPR aléatoire. |

## 2. Architecture, réemplois, graphe d'appels

### 2.1 Fichiers possédés

- Créer `experiments/pca_info_online.py` : noyaux (§2.4), générateurs, setups, développement, calibrations, NULL_PLAN,
  inférence, partitions, autorisation, CLI (`--config`, `--mode smoke|pilot|full`, `--jobs`, `--resume`, `--output-dir`,
  `--log-dir` optionnel, défaut `logs/pca_info_online/<run_id>`).
- Créer `configs/pca_info_online.yaml` : paramètres avec étiquette de provenance, applications et familles, famille Φ,
  grilles, tailles par mode, ressources, `authorization: null`.
- Créer `tests/test_pca_info_online.py`.
- Créer `docs/sections/pca_info_online.md` (anglais) : protocole, estimands, couverture, journal de décisions par
  provenance, limites, préséance sur la note 11.
- Lot R (après GO technique) : `prompts/streams/prompt-32-pca-info-online.md` (ligne 1), `tools/check_prompts.py:19`,
  `tests/test_check_prompts.py` (l. 1, 45–52, 80, 149–150), `prompts/streams/INDEX.md` (une ligne),
  `prompts/Prompts_Claude_Code_v5.md` (par `--sync-master` seulement).
- Non créés : `jepadrift/selection/pca_information.py`, `jepadrift/monitors/adaptive_gaussian_mixture.py`.
- Sorties : `results/pca_info_online/<run_id>/` (CSV et manifeste compacts), `figures/pca_info_online/<run_id>/` (plus tard,
  depuis CSV), partitions et journaux sous `logs/pca_info_online/<run_id>/` (ignorés).
- À Codex : `prompts/plans/plan-32.md`, fichiers GO, `prompts/wrapups/wrapup-32.md`, `docs/DEVIATIONS.md`,
  `docs/MAPPING.md`, Git, `make check`, réindexation.

### 2.2 Réemplois en lecture seule (`from experiments import pca_drift_benchmark as pdb`, précédent `experiments/pca_drift_tables.py:13`)

| Besoin | Réemploi | Usage 32 |
| --- | --- | --- |
| M(d, γ_M) | `pdb.mixture_cost` `:71` | coûts MIX (γ_M = 504 et 5000), base de l'ajustement affine |
| corde historique | `pdb.affine_costs` `:98` | `AFFINE_CHORD_1_20` journalisée, jamais sélectionnante |
| tri top-q | `pdb.select_top_q` `:506` | référence de `best_sets`, ex ante |
| scan statique | `pdb.scan_statistic` `:193`, `pdb.segment_loglik` `:211` | équivalence au même s2 |
| seuil | `pdb.rank_threshold` `:236`, `predictive_rank` `:221`, `predictive_bound` `:226`, `min_calibration_n` `:231`, `CalibrationFailed`/`InsufficientCalibration` `:63-67` | toute calibration |
| information | `pdb.q_plugin` `:115`, `pdb.kl_mean` `:121` | surrogate diagonal ; KL joint diagnostic |
| base LW, CPV90 | `pdb.fit_basis` `:455`, `pdb.cpv90` `:444` | bras FITTED ; CPV90 global |
| hachage | `pdb.array_sha256` `:410`, `canon` `:420`, `sha16` `:425`, `file_sha256` `:700` | identités, manifeste |
| graines | `pdb.label_code` `:350`, `pdb.check_entropies` `:369` | plan de graines 32 |
| env, sorties | `pdb.check_env` `:688`, `prepare_dirs` `:818`, `OutputExists`/`ResourceBlocked`/`PartitionMismatch` `:664-676`, `first_index` `:842` | garde-fous |
| CSV, γ_H | `jepadrift.pipelines.save_fair_csv` `:67`, `horizon_gamma` `:465` | sorties FAIR, `H/α` |
| lois | `scipy.stats.beta`, `norm`, `binom` ; `scipy.optimize.brentq` | CP, Tango, planification |
| témoins | `scipy.optimize.minimize_scalar` (tests seulement) ; `statsmodels` `proportion_confint(method="beta")` (tests seulement) | contrôle indépendant Tango et CP |

Non réemployés : `pdb._detector` (s2 en d), `pdb.Store` (non atomique, RSS par processus), `pdb.seed_key` (`STREAM = 28`),
`experiments/e4_production.py`.

### 2.3 Graphe d'appels — v2.1

```
config+mode -> design_descriptor + seed_plan_sha (aucun tirage) -> design_id
 -> authorize(stage, design_id, GO, portée/enveloppe) AVANT tirage/worker/écriture
 -> staging(design_tag, full_design_id)
 -> SETUP(frame/fit/géométrie HEAD) -> DEV -> CAL -> NULL_PLAN applicable
 -> HOLD -> ALT -> diagnostics -> payloads FAIR -> realization_id
 -> manifeste final -> publication atomique -> FINAL
```

Séquence normative détaillée : amendement v2.1 §3.1, avec reprise par phase (§3.5).
run_block conserve les générateurs et politiques des §§3–8, sans métadonnées oracle pour les non-oracles.

### 2.4 Interfaces (noyaux à témoins séparés)

- `affine_ols(gamma, K, d_max=16) -> (a, c, info)` : OLS de M(d) sur d = 1..min(d_max, K) ; `info = {identity:
  "AFF_OLS_1_16", range, max_abs_resid_fit, max_abs_resid_1K}` ; `ArithmeticError` si a <= 0, c <= 0 ou non fini ;
  `ValueError` si min(d_max, K) < 2.
- `cost_vectors(gamma, K) -> {"MIX": (K,), "AFF": (K,)}`.
- `best_sets(q (B,K), cost (K,), order "INFO"|"PREFIX") -> (d (B,), mask (B,K) bool)`.
- `online_masks(Y (B,H,K), window, cost (K,), order) -> (B,H,K) bool` : non-oracle, aucune méta.
- `masked_scan(Y (B,H,K), M (B,H,K) bool, s2, h=None) -> (W (B,H), first (B,))`.
- `nonoracle_masks(Y, policy) -> (B,H,K) bool` : `online_masks` ou masque constant du sous-ensemble figé.
- `oracle_masks(q_true (B,K), policy) -> (B,H,K) bool` : `best_sets` sur q vrai (EXACT) ou surrogate (FITTED), constant en t.
- `tango_interval(b, c, n, tail) -> (lo, hi)` ; `cp_bounds(k, n, tail) -> (lo, hi)` ;
  `null_status(k, n, alpha, eps, tail) -> "NULL_VALIDATED"|"NULL_INCONCLUSIVE"|"NULL_FAILED"`.
- `plan_holdout(counts, alpha, m, eps, eps_v, beta, eta, n_min, n_cap) -> (n_hold, status, details)` : comptes nuls seulement.
- `null_score_bias(c, var0, m) -> 0.5 * (c**2 + (var0 - 1) / m)`.

## 3. Contrats mathématiques

**3.1 Information et libellé oracle.** EXACT : q_k = (v_k'Δ)²/(2λ_k) exact et I(S) = Σ_S q_k = KL joint (base
diagonalisante) ; `oracle_basis = EXACT_ADDITIVE_KL`. FITTED : β̂ = Λ̂_E^{-1/2} V̂_E' Δ (décalage moyen des scores
standardisés ajustés), q_k^surr = β̂_k²/2 = surrogate diagonal additif ; l'appel réemployé est
`pdb.q_plugin(V_hat_E.T @ Delta, lambda_hat_E)`, qui normalise lui-même les projections non standardisées.
Ne jamais lui passer β̂ avec lambda_hat_E, ce qui normaliserait deux fois. Les ORACLE_* y sélectionnent
sur ce surrogate : `oracle_basis = ORACLE_DIAGONAL_SURROGATE`, jamais « optimum KL joint » ni « KL optimale ».
I_joint(S) = ½ β̂_S' [Cov0(y_S)]^{-1} β̂_S (`pdb.kl_mean`), Cov0(y) = A A', diagnostic hors ligne jamais lu par un
sélecteur. T7 : proxys gaussiens seulement.

**3.2 Argmax.** Pour q >= 0 additif et C(d) > 0 fonction de d seule : max_S I(S)/C(|S|) = max_d T_d/C(d), T_d somme des d
plus grands q ; tri = glouton avant = exhaustif. Égalités : plus petit d parmi les maximiseurs, puis liste triée
lexicographiquement minimale (ordre (−q, indice canonique)). Pas de d* unique inconditionnel : q = (2, 1), C = (2, 3) donne
V(1) = V(2) = 1. PREFIX : V(d) = Σ_{j<=d} q_{e_j}/C(d) énuméré pour tout d = 1..K, sans arrêt au premier gain nul ni d*
INFO appliqué au préfixe. Égalités en flottant exact comme `select_top_q`.

**3.3 M, proxy analytique.** M(d, γ_M) = x_d/A, x_d = A + (d/2) log(1 + 2x_d/d), A = ln γ_M : multiplicateur fluide d'un
mélange à prior apparié de dimension fixe. Ni ADD, ni RMST, ni seuil ; maximiser V ne minimise pas le RMST à horizon
fini ; M ne couvre ni l'erreur d'estimation de qhat ni la recherche répétée sur K axes. γ_M = 504 (SPEC_PROPOSAL,
historique) étiqueté `ANALYTIC_PROXY`, distinct du niveau opérationnel H/α = 5000 et du seuil calibré h ; sensibilité
γ_M = H/α en §11.2.

**3.4 Affine.** `AFFINE_CHORD_1_20` (stream 28, journalisée) ≠ `AFF_OLS_1_16` (32) : c = Σ(d − d̄)(M_d − M̄)/Σ(d − d̄)²,
a = M̄ − c d̄ sur d = 1..min(16, K) ; résidus maximaux sur 1..16 et 1..K et taux de désaccord d'argmax MIX/AFF
journalisés ; aucun R² recopié.

**3.5 Scan masqué.** Filtration F_t = σ(y_1..y_t sur les K coordonnées éligibles ; métadonnées de setup indépendantes du
bruit). Un masque m_i ∈ F_{i−1} par instant, commun à tous les τ ; n_k(τ,t) = Σ_{i=τ}^t m_ik, D_k(τ,t) = Σ_{i=τ}^t m_ik y_ik ;
aucune recomposition de l'historique à l'entrée d'un axe. logL(τ,t) = Σ_k [−½ log1p(n_k s2) + s2 D_k²/(2(1 + n_k s2))],
W_t = max_{τ<=t} logL, alarme W_t >= h. Si y_i ~ N(0, I_K) iid indépendant de F_{i−1}, pour τ et s2 fixés exp logL(τ,t)
est une martingale positive d'espérance 1 (facteur exp(Σ_k m_ik(b_k y_ik − b_k²/2)) d'espérance conditionnelle 1, produit,
mélange b ~ N(0, s2 I), Tonelli). Portée : vraisemblance des seules coordonnées masquées ; hypothèse sur la loi nulle
jointe des K coordonnées éligibles. Le maximum en τ n'est pas une e-process ; borne d'union P0(∃τ<=t<=H : logL >= h) <= H e^{−h}
en EXACT seulement, diagnostic conservateur. FITTED/T7 : calibration empirique seule. Scan complet en τ, sans troncature.

**3.6 s2 commun et prior apparié.** s2_common = 2 ln(H/α)/(H K) = 0.0034068772765664954 (H = 250, α = 0.05, K = 20 ; audit
Codex) pour toute politique, indépendant de d_t. Ratio de prior apparié d'un sous-ensemble S de dimension d portant
l'information I(S) : ρ(S) = (2 I(S)/d)/s2_common = I(S)/(d s2/2) ; avec I(S) = I* = 0.25 : 7.338098196831849 (d = 20) et
73.3809819683185 (d = 2) (audit Codex) ; si I(S) < I*, I(S) effectif est utilisé. Rapporté, jamais corrigé.

**3.7 Estimateur online et biais.** m_t = min(w, t − 1) ; bhat_{k,t−1} = moyenne(y_{k,s}, t − m_t <= s <= t − 1) ;
qhat = ½ max(0, bhat² − 1/m_t). Variance nulle `NULL_VARIANCE_NOMINAL_UNIT` : exacte en EXACT, nominale sous LW.
FITTED sous H0, fit figé : y_{k,s} iid en s de moyenne c_k = [Λ̂_E^{-1/2} V̂_E'(μ0 − μ̂)]_k et de variance
Var0_k = [Cov0(y)]_kk ; avant écrêtage E[½(bhat² − 1/m)] = ½(c_k² + (Var0_k − 1)/m) ; sous H1 remplacer c_k par c_k + β̂_k ;
après écrêtage l'espérance est au moins cette valeur (surrogate, non sans biais). c, Var0 et Cov0 sont calculés hors ligne
depuis le simulateur et jamais transmis à ONLINE (§4.2). Une correction de variance apprise sur un rôle nul supplémentaire
indépendant serait une ablation étiquetée, hors architecture initiale. Repli : m_t = 0 ou qhat entièrement nul ⇒ règle
d'égalité ⇒ S_t = {min E} pour INFO et PREFIX ; oracles et statiques gardent leur choix de setup.

**3.8 Trois objets de calibration distincts.** (i) Garantie marginale de rang (SOURCE_RULE, règle
`predictive_exchangeable_rank_v2`) : si les n_cal maxima CAL et un nouveau maximum nul sont échangeables (trajectoires
nulles indépendantes, même setup figé, même politique, même loi de masque), P(nouveau > b) <= (r + 1)/(n + 1) <= α,
marginale sur CAL et la nouvelle trajectoire, conditionnelle au fit (et à la loi de métadonnées déclarée pour un oracle).
(ii) FPR réalisée conditionnelle du seuil figé F_cond = P(W_max > b | CAL) : pour des maxima iid continus conditionnellement
au setup et à la politique figés,
F_cond ~ Beta(r + 1, n − r) exactement [Vovk, 2012, Conditional validity of inductive conformal predictors] ; écart-type
≈ sqrt(α(1 − α)/(n + 2)) : 0.0049 (n = 2000), 0.0031 (5000), 0.0022 (10 000) (approximation normale ; la loi Beta exacte se
calcule sans simulation). L'échangeabilité seule suffit à (i), pas à cette loi Beta. Le HOLDOUT estime F_cond.
(iii) Objectif d'équivalence ±0.01 sur Δ_cond = F_cond(A) − F_cond(B)
des seuils figés : cible empirique, jamais confondue avec (i).

## 4. Chronologie, API et invariance non-oracle (A1)

**4.1 Objets et clés exacts — remplacés par l'amendement v2.1 §§3.2–3.3.**

design_id est pré-exécution ; design_tag=run_id=design_id[:16] n'est qu'un alias.
setup_id après SETUP inclut design_id et les empreintes de base/fit. dev_id/policy_id après DEV,
calibration_id/seuils après CAL, plan_id/n_hold après NULL_PLAN, realization_id après ALT.
calibration_id non-oracle unique par setup/politique, réutilisé entre familles ; oracle par famille et libellé
NON_DEPLOYABLE_ORACLE_CALIBRATION. Univers fixé par application ex ante.

Précision de réception C32-R5 : toutes les clés de graines sont des primitives pré-exécution.
Bruit : (path,campaign,arm,N,fit_id,role,i), sans famille. Méta :
(meta,campaign,arm,N,fit_id,role,family,i), CAL/HOLD pour les oracles seulement.
DEV_LIB : (devlib,campaign,arm,N,fit_id,family,l).
Bootstrap : (boot,campaign,arm,N,fit_id,application,family), partagé entre comparateurs.
Aucune clé ne dépend de design_id, setup_id, basis_sha, fit_hash ou d'un digest réalisé.
seed_plan_sha256 est connu avant tirage, bootstrap et HOLD jusqu'au cap inclus ; T41/T52 le vérifient.

**4.2 Chaîne non-oracle.** `nonoracle_masks(Y, policy)` : `online_masks(Y, window, cost, order)` ou masque constant du
sous-ensemble figé. Entrées : Y (scores éligibles de l'univers de l'application) et la politique figée sans famille. Aucune
famille, Δ, τ*, méta, rôle, centre ou covariance vrais dans la signature ou la fermeture ; même fonction pour CAL_NULL,
NULL_PLAN, HOLD_NULL et ALT. Pour un (setup, politique) : un CAL, un `calibration_id`, un seuil h, une évaluation HOLDOUT
appariée, ALT évalué par famille avec ce même h. Le prior ex ante, d_dev et s2_dev viennent de la bibliothèque DEV poolée
(définitions des quatre familles résiduelles, graines DEV), identique pour toute famille d'évaluation ; aucune variante par
famille d'évaluation (pas de leave-one-family-out). La fenêtre primaire w = 128 est fixée a priori. Les métadonnées des
lignes ALT (`family_id`, `meta_sha256`) sont des étiquettes ; les diagnostics lisent les masques hachés après coup et ne
renvoient rien.

**4.3 Chaîne oracle.** `oracle_masks(q_true, policy)` constant en t. CAL et HOLD : directions non nulles tirées de la loi de
la famille sur des clés méta propres au rôle, indépendantes des innovations et des dérives ALT ; ALT : dérive injectée.
Calibration par (politique oracle, famille), étiquetée `NON_DEPLOYABLE_ORACLE_CALIBRATION` ; FPR oracle rapportés à part ;
toute comparaison impliquant un oracle porte `fpr_status = ORACLE_SEPARATE`, jamais `ATTAINED_FPR_COMPARABLE`. Aucune
trajectoire ALT n'est lue pendant CAL. EXACT F1/F2/HEAD/F3 : q invariant au signe, sous-ensemble oracle constant ; F0 et
FITTED : sous-ensemble par trajectoire.

**4.4 Ordre par setup.** design_id → autorisation → staging → SETUP → DEV → CAL →
NULL_PLAN applicable → HOLD → ALT → diagnostics → realization_id → publication.
Chaque phase contrôle design_id complet, digests amont et partitions ; phase complète chargée sans recalcul.
Un échec de géométrie HEAD ne modifie ni fit ni dérive.

**4.5 Tests d'invariance.** T23 (permutation des noms de familles), T24 (`calibration_id` unique réutilisé), T25 (graphe de
dépendances et méta empoisonnées), T41 (clés de bruit sans famille).

## 5. Applications, familles, supports (A2)

| Application | Famille | Support (PC population absolues) | Poids | Signes | Statut |
| --- | --- | --- | --- | --- | --- |
| RESIDUAL (E_res = PC 2..21, K = 20) | `F0_ISOTROPIC_RESIDUAL` | direction uniforme sur la sphère des 20 coordonnées standardisées de E_res, b = sqrt(2 I*) u | — | — | contrôle négatif du ex ante statique ; descriptif |
| | `F1_TAIL_RESIDUAL` (spec `F1_SPARSE_LOW_VARIANCE`) | {18, 19, 20, 21} | q = I*/4 chacun | Rademacher indépendants par axe et trajectoire | descriptif |
| | `F2_STRUCTURED_RESIDUAL` | {3, 9, 17, 21} ; K < 20 ⇒ `UNSUPPORTED` | q = I*/4 | idem | primaire favorable INFO (H1, H3) |
| | `F_HEAD_RESIDUAL` | {2, 3, 4, 5} | q = I*/4 | idem | contrôle primaire favorable au préfixe (H2) |
| MARKET (E_mkt = PC 1..20) | `F3_MARKET` | {1} | q = I* | Rademacher | descriptif, jamais regroupé |

- Toutes les dérives sont définies dans le repère population (vrais v_k, λ_k), indépendamment du fit, avec
  ½ Δ'Σ0^{-1}Δ = I* exactement. FITTED : β̂, KL nominal, KL projeté atteint (surrogate et joint) enregistrés ; le fit ne
  modifie jamais Δ. Signes et directions : clés méta ; bibliothèque DEV : clés `devlib` disjointes.
- Valeurs fluides de référence (EXACT, γ_M = 504, I* = 0.25 ; calcul manuel recalculé par le code) : F1 et F2 →
  ORACLE_INFO_MIX d = 4, V ≈ 0.159 ; ORACLE_PREFIX_MIX d = 20 (sous-ensemble de FULL_K), V ≈ 0.0995 (rapport ≈ 1.60) ;
  HEAD → mêmes sous-ensembles d = 4 pour INFO et PREFIX (V ≈ 0.159) ; F0 aléatoire. Classement issu du seul dessin injecté.
- Le repli {min E} sélectionne PC2 (support HEAD) et PC1 (support F3) au premier pas pour INFO comme pour PREFIX :
  asymétrie déclarée, identique entre ordres.

## 6. Politiques et baselines (B2)

| Politique | Définition | Applications | Calibration |
| --- | --- | --- | --- |
| `ONLINE_{INFO,PREFIX}_{MIX,AFF}` × w ∈ {32, 128} | §3.7 puis §3.2 à chaque pas | les deux | non-oracle |
| `ORACLE_{INFO,PREFIX}_{MIX,AFF}` | `best_sets` sur q vrai (EXACT) ou surrogate (FITTED, `ORACLE_DIAGONAL_SURROGATE`) | les deux, par famille | oracle par famille |
| `FULL_K` | les K axes | les deux | non-oracle |
| `FIXED_EIGENMEAN_PREFIX` | préfixe canonique de E avec λ_k >= moyenne_{j∈E} λ_j, spectre de covariance restreint à E (population en EXACT, LW en FITTED) ; pas la règle de Kaiser (valeurs propres de corrélation > 1) | les deux | non-oracle |
| `CPV90` | k90 sur le spectre complet (sémantique `pdb.cpv90`) ; RESIDUAL : `OUTSIDE_UNIVERSE` (contient PC1), jamais tronqué ; MARKET : {1..k90} si k90 <= 20, sinon `OUTSIDE_UNIVERSE` | ligne de statut dans les deux | non-oracle si faisable |
| `RESIDUAL_CPV90` | plus court préfixe canonique de E_res atteignant 90 % de Σ_{k∈E_res} λ_k ; distinct du CPV90 global | RESIDUAL | non-oracle |
| `FIXED_DEV_PREFIX` | préfixe canonique de dimension d_dev (§7) | RESIDUAL (MARKET : `NOT_RUN`) | non-oracle |
| `FIXED_EXANTE_QBAR_MIX` | `select_top_q(qbar, K, M)`, qbar de la bibliothèque DEV poolée ; `TRANSFER_STRUCTURAL_POOLED_PRIOR` : la bibliothèque partage les supports F1/F2/HEAD, seules graines et signes changent ; en EXACT q est invariant au signe ; aucune revendication de support jamais vu | RESIDUAL (MARKET : `UNSUPPORTED`) | non-oracle |

Valeurs EXACT manuelles (recalculées par le code) : EIGENMEAN RESIDUAL = PC 2..9 (d = 8), MARKET = PC 1..7 ;
RESIDUAL_CPV90 = PC 2..16 (d = 15) ; CPV90 N = 32 → k90 = 17 (MARKET {1..17}), N = 239 → k90 > 20 (`OUTSIDE_UNIVERSE`) ;
EXANTE poolé (espérance) ≈ {2, 3, 4, 5, 9, 17, 18, 19, 20, 21} (d = 10), qui couvre tous les supports structurés.
Aucune combinaison OU/ET d'alarmes de politiques différentes, explicite ou implicite.

## 7. Développement (DEV)

- Rôles par setup résiduel : `DEV_LIB` (n_lib = 100 directions par famille F0/F1/F2/HEAD), `DEV_NULL` (n_dn trajectoires
  nulles), `DEV_ALT` (n_da trajectoires par famille, bruit sans famille + méta DEV_ALT). Clés disjointes de
  CAL_NULL/NULL_PLAN/HOLD_NULL/ALT ; calcul avant CAL ; sorties gelées et hachées dans `dev_id` ; TEST_ALT jamais lu ;
  aucune décision humaine après l'étape DEV (fonction déterministe des graines).
- qbar = moyenne de q (exact en EXACT ; surrogate β̂ en FITTED) sur DEV_LIB, équilibrée entre familles.
- d_dev : pour d ∈ D_K = {1, 2, 4, 8, 16, 20} ∩ [1, K], préfixe canonique, s2_common, calibration rang sur DEV_NULL ;
  RMST_H sur DEV_ALT ; critère J(d) = moyenne sur les quatre familles (poids égaux) de la moyenne de min(T, H) ;
  d_dev = argmin J, égalité ⇒ plus petit d. Qualification : candidats comparés à α nominal commun
  (`COMMON_NOMINAL_ALPHA_DEV`), pas à FPR atteints équivalents. Un d_dev par setup (arm, N, fit), figé avant CAL.
- s2_dev (setup primaire seulement) : grille G = {1, 4, 16, 64} × s2_common ; politiques P_conf = {ONLINE_INFO_MIX w128,
  ONLINE_PREFIX_MIX w128, FULL_K} ; chaque (s2, P) calibré sur DEV_NULL ; critère J(s2) = moyenne sur P_conf et les quatre
  familles du RMST_H DEV ; argmin, égalité ⇒ plus petit s2. Un seul s2_dev pour tous les comparateurs de la sensibilité,
  jamais propre à une famille, indépendant du CAL_NULL final. Les valeurs appariées 2I*/d = 0.125 (d = 4) et 0.025 (d = 20)
  sont encadrées par la grille.
- Normalisation : dérives DEV à KL pleine I*, même H que l'évaluation.

## 8. Calibration et statuts nuls

**8.1 Calibration.** `pdb.rank_threshold(maxima, α, "GE")` repris strictement : r = ⌊α(n + 1)⌋ − 1, b = tri[n − r − 1],
h = nextafter(b, +inf), alarme W_t >= h sur l'échelle log. Non-oracle : une calibration par (setup, politique) sur les
trajectoires CAL_NULL 0..n_cal(politique) − 1 ; oracle : une par (setup, politique oracle, famille). Politiques adaptatives :
pipeline complet (sélection + scan masqué) sur chaque trajectoire CAL. Seuils calculés par le parent, hachés, figés avant
NULL_PLAN/HOLD/ALT ; aucune recalibration après un résultat HOLD/ALT. Contrôle déterministe : alarmes CAL = r exactement
pour des maxima distincts (T43).

**8.2 Tri-état nul (HOLD_NULL, par politique, préenregistré).** `cp_bounds(k, n_hold, 0.05)` : bornes unilatérales
Clopper–Pearson exactes à 95 % (L = 0 si k = 0, sinon Beta.ppf(0.05; k, n − k + 1) ; U = 1 si k = n, sinon
Beta.isf(0.05; k + 1, n − k)). `NULL_VALIDATED` ssi U <= α + ε_v ; `NULL_FAILED` ssi L > α + ε_v, ou échec de conception
(r < 0, alarmes CAL ≠ r sur maxima distincts, recouvrement de clés, identité incohérente) ; sinon `NULL_INCONCLUSIVE` ;
ε_v = 0.01 ; α + ε_v évalué par la même expression flottante dans le code et les tests (0.060000000000000005). Témoin
d'audit : n = 2000 ⇒ VALIDATED ssi k <= 102 et P_{p=0.05}(k <= 102) = 0.6067391237795827 : un moniteur calibré est
INCONCLUSIVE environ 39 % du temps à n = 2000, jamais FAILED pour ce motif. Rôle : qualificatif descriptif hors famille
FWER ; `NULL_FAILED` bloque tout libellé confirmatoire de la politique (un blocage ne peut que retirer des revendications).
Oracles : tri-état par famille, `NON_DEPLOYABLE`.

**8.3 Critère de validité nulle déclaré.** Une politique satisfait le critère de la spec si son seuil vient d'une
calibration de rang valide sur une cohorte CAL indépendante (garantie §3.8 (i) par conception) et si son statut n'est pas
`NULL_FAILED`. `NULL_VALIDATED` est une qualification supplémentaire, jamais exigée par un libellé.

## 9. Inférence, famille confirmatoire, multiplicité

**9.1 Estimands.** RMST_H = E[min(T, H)], T premier franchissement 1-based après le début (τ* = 1), non-détections = H ;
fraction détectée, fraction censurée, médiane conditionnelle à la détection (étiquetée), différences et ratios appariés à
H. Jamais « ADD de Lorden », aucune extrapolation non tronquée. FITTED : `FIT_CONDITIONAL` (fit 0) ; couche de fits
externes non prévue (R5).

**9.2 Intervalle apparié de ΔFPR, méthode principale : score de Tango** [Tango, 1998, Equivalence test and confidence
interval for the difference in proportions for the paired-sample design, Statistics in Medicine 17:891–908].
- Domaine : entiers n >= 1, b, c >= 0, b + c <= n, 0 < tail < 0.5, sinon `ValueError` ; z = Φ^{-1}(1 − tail) ;
  Δ̂ = (b − c)/n ; b = #(A = 1, B = 0), c = #(A = 0, B = 1) sur les mêmes trajectoires HOLD_NULL.
- EMV contraint de p01 sous Δ = Δ0 ∈ (−1, 1) : W = −b − c + (2n − b + c)Δ0, C = cΔ0(1 − Δ0), s = sqrt(max(0, W² + 8nC)) ;
  q̃ = 2C/(W + s) si W > 0 (sans annulation), sinon (s − W)/(4n) ; q̃ ramené dans [max(0, −Δ0), (1 − Δ0)/2] si l'écart est
  <= 1e−12, sinon `ArithmeticError`. Un discriminant ou une variance matériellement négatifs sont refusés ; seul un
  écart d'arrondi documenté est ramené à zéro. Z(Δ0) = (b − c − nΔ0)/sqrt(n(2q̃ + Δ0(1 − Δ0))), décroissante.
  Si la variance vaut zéro : Z = 0 si le numérateur est nul, sinon l'infini de son signe, jamais NaN.
- b = c = 0 : forme close ±z²/(n + z²). Borne basse : −1 si Δ̂ = −1 ou Z(nextafter(−1, 0)) <= z, sinon racine `brentq` de
  Z − z sur [nextafter(−1, 0), Δ̂] ; borne haute : +1 si Δ̂ = 1 ou Z(nextafter(1, 0)) >= −z, sinon racine de Z + z sur
  [Δ̂, nextafter(1, 0)] ; sortie dans [−1, 1] ; symétrie tango(c, b) = (−hi, −lo).
- Étiquettes : `ci_method = TANGO_SCORE_ASYMPTOTIC`, `coverage_claim = NONE_FINITE`.
- Motif du choix : algèbre vérifiée par l'audit Codex (81 cas contre EMV numérique contraint, écart maximal
  4.99672658804684e−9, faisabilité, symétrie, limites), un seul algorithme, intervalle plus étroit que les variantes
  exactes conservatrices.
- Variante exacte conservatrice non implémentée : bornes CP marginales de b/n et c/n à tail/2 chacune (Bonferroni),
  [L_b − U_c, U_b − L_c] ; coût ≈ 2(z_{1−α/(2m)}/z_{1−α/m})² ≈ 2.5 × n_hold à m = 3 pour des discordances équilibrées
  (approximation normale) ; décision R4.

**9.3 Famille confirmatoire Φ** (structure équilibrée : NOTIFICATION_DECISION ; contenu : NEW_PROPOSAL à geler par Codex
avant tout pilote de puissance ; aucune sélection de famille après ALT).
- Setup primaire : FITTED_LW_GAUSSIAN, N = 239, fit_id = 0, RESIDUAL, w = 128, MIX, γ_M = 504, s2_common, H = 250,
  α = 0.05, I* = 0.25, τ* = 1. Motif : analogue de déploiement (base apprise), échelle du panel `d3_239` ; le bras EXACT
  reste le contrôle mathématique descriptif.
- H1 (décisive, favorable INFO) : ONLINE_INFO_MIX contre ONLINE_PREFIX_MIX sur F2, supériorité :
  RMST(PREFIX) − RMST(INFO) > 0.
- H2 (contrôle HEAD, favorable au préfixe) : même paire sur F_HEAD, non-infériorité relative δ_NI = 0.10 :
  E[min(T_INFO, H) − 1.10 min(T_PREFIX, H)] < 0.
- H3 (baseline forte, jamais conditionnée) : ONLINE_INFO_MIX contre FULL_K sur F2, supériorité.
- m = 3, Bonferroni α/3 = 0.05/3 par revendication ; intersection–union des composantes, chacune à α/3 :
  (a) gain : borne unilatérale bootstrap percentile apparié à 1 − α/3 (B = 10 000, tirages d'indices partagés par
  (setup, famille), deff = 1, trajectoires ALT iid), `BOOTSTRAP_PERCENTILE_APPROX` ;
  (b) équivalence FPR : TOST Tango, deux bornes unilatérales à 1 − α/3 dans [−0.01, +0.01] sur les indicateurs HOLD_NULL
  de la paire.
- Préconditions déterministes : calibrations valides, partitions complètes, identités concordantes, aucune politique
  `NULL_FAILED`.
- Degrés de certitude préenregistrés pour H1/H3 (H2 suit la matrice du §9.5) : `CONFIRMED_AT_ATTAINED_COMPARABLE_FPR` ((a) et (b) et préconditions) ;
  `CONFIRMED_AT_COMMON_NOMINAL_ALPHA_ONLY` ((a) et préconditions, (b) non atteint) ; `NOT_ESTABLISHED` ((a) non atteint,
  signe de l'estimation rapporté) ; `INVALID_NULL_FAILED` (précondition en échec).
- Énoncé d'erreur : FWER approximatif <= 0.05 sur les trois revendications (Bonferroni + intersection–union) ; composantes
  bootstrap et score asymptotiques ; aucune garantie FWER finie exacte affirmée.
- Les trois revendications sont calculées et rapportées quel que soit le sort des autres ; aucune porte séquentielle ;
  aucune alarme OU.

**9.4 Statut du reste** (`DESCRIPTIVE_NOMINAL` : intervalles bilatéraux nominaux 95 %, jamais « établi », aucune correction
de multiplicité, déclaré) : EXACT N ∈ {32, 239} (contrôle mathématique, mêmes contrastes) ; FITTED N = 32 ; F0, F1, F3 ;
AFF, w = 32 ; FIXED_*, CPV90, RESIDUAL_CPV90, EXANTE ; oracles (`ORACLE_SEPARATE`) ; sensibilités s2_dev et γ_M ; T7.
Contrastes descriptifs préenregistrés : par (setup, application, famille), chaque politique non-oracle contre
ONLINE_INFO_MIX w128 et contre ONLINE_PREFIX_MIX w128, écart ORACLE_INFO_MIX − ONLINE_INFO_MIX. Pilote : tout `PILOT_ONLY`.
Gains contextuels (résiduel structuré F2 face au contrôle HEAD), jamais « supériorité générale ».

### 9.5 Contrôle HEAD non vacueux, fit figé — v2.1

H2, δ_NI = 0.10, supports, H, I*, w, Φ, comparateurs et multiplicité sont inchangés.

#### 9.5.1 Géométrie (complète §5 et §11.3 ; phase SETUP, avant tout ALT)

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

#### 9.5.2 Détectabilité (après ALT ; composante d'intersection–union)

- U_PREFIX = borne supérieure unilatérale bootstrap percentile apparié, à 1 − α/3, de RMST_H(`ONLINE_PREFIX_MIX`) sur
  F_HEAD (setup primaire, mêmes tirages d'indices que H2).
- `PREFIX_DETECTABLE` ssi U_PREFIX <= κ_det H, avec κ_det = 0.80, soit 200 jours à H = 250 (NEW_PROPOSAL).

**Justification statique.**
- κ_det H = 200 < H/(1 + δ_NI) = 227.27 : le contrôle reste hors de la zone vacueuse.
- Sous `PREFIX_DETECTABLE`, la non-infériorité exige E[min(T_INFO, H)] < 1.10 × 200 = 220 < H. Elle échoue donc si
  INFO ne détecte jamais.
- min(T, H) >= H·1[T > H] implique P(T <= H) >= 1 − RMST_H/H >= 0.2, au-delà du niveau nominal 0.05.

#### 9.5.3 Statuts H2 (complète §9.3)

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

#### 9.5.4 Multiplicité

- m = 3 inchangé.
- Les libellés confirmés de H2 sont une intersection–union de {NI à α/3, détectabilité à α/3, (b) à α/3 pour le libellé
  le plus fort}, plus la géométrie et les préconditions, qui sont déterministes et ne consomment pas d'erreur.
- Niveau α/3, FWER approximatif <= 0.05 (Bonferroni) inchangé ; composantes asymptotiques ; aucune hypothèse ajoutée.
- H1 et H3 inchangées.

## 10. Dimensionnement du HOLDOUT par le seul nul (NULL_PLAN)

- Rôle `NULL_PLAN` (full, setup primaire, P_conf) : n_plan trajectoires nulles (proposé 2000), clés disjointes de
  CAL/HOLD/ALT, évaluées avec les seuils figés après CAL ; ALT jamais lu.
- Statistiques : pour chaque paire j ∈ {(INFO_MIX, PREFIX_MIX), (INFO_MIX, FULL_K)} : b_p, c_p, D̂ = (b_p + c_p)/n_p,
  Δ̂ = (b_p − c_p)/n_p ; pour chaque politique : k_p.
- Plug-ins conservateurs (queue unilatérale η = 0.10) : D⁺ = borne CP supérieure de (b_p + c_p)/n_p ;
  |Δ|⁺ = max(|lo|, |hi|) de Tango à la queue η ; F⁺ = borne CP supérieure de k_p/n_p.
- Tailles requises, z_a = z_{1−α/3}, z_eq = z_{1−β/2}, z_b = z_{1−β}, β = 0.2 :
  n_eq,j = ⌈D⁺_j (z_a + z_eq)²/(ε − |Δ|⁺_j)²⌉ si |Δ|⁺_j < ε, sinon ∞ ;
  n_v,P = ⌈F⁺(1 − F⁺)(z_{0.95} + z_b)²/(α + ε_v − F⁺)²⌉ si F⁺ < α + ε_v, sinon ∞ ;
  n_req = max(n_min, max_j n_eq,j, max_P n_v,P) ; n_hold = min(n_req, n_cap) ; statut `PLAN_ADEQUATE` ou
  `PLAN_CAPPED_EXPECT_INCONCLUSIVE`.
- n_min = 2000 (spec), n_cap fixé par le GO full (proposé 20 000). Plafond atteint : HOLD exécuté à n_cap, ε inchangé,
  ALT non lu ; le TOST observé est rapporté tel quel (test valide, puissance faible attendue), sinon INCONCLUSIVE et
  `COMMON_NOMINAL_ALPHA_ONLY`.
- Validité : HOLD indépendant de NULL_PLAN, n_hold figé et haché avant toute génération HOLD ⇒ tests HOLD valides
  conditionnellement (asymptotiquement pour le score). La formule ne vise que la puissance par contraste (approximation
  normale), sans garantie de puissance familiale. À différence nulle, l'approximation TOST bilatérale est
  2 Φ(ε sqrt(n/D) − z_a) − 1 : employer z_{1−β} donnerait 1−2β = 0.60, contre 0.80 avec z_{1−β/2}.
- Différence réalisée : Δ_cond ≠ 0 même si les deux seuils sont calibrés à α ; écart-type ≈ sqrt(2(1 − ρ)) × sd(F_cond),
  ρ inconnu : ρ = 0 ⇒ ≈ 0.0044 (n_cal = 5000), 0.0031 (10 000). n_cal est fixé avant CAL (R3) ; NULL_PLAN mesure Δ_cond des
  seuils effectivement figés.
- Ordres de grandeur calculés sans simulation (m = 3, puissance par contraste 0.8, (z_a + z_eq)² = 11.625350336726223) :
  D = 0.095, Δ = 0 ⇒ 11 045 ; D = 0.05, Δ = 0 ⇒ 5 813 ; D = 0.095, |Δ| = 0.003 ⇒ 22 539.
  Cette dernière valeur dépasse le plafond proposé 20 000 : l'inconclusion prévue est conservée.
  Référence demi-largeur seule (audit Codex, D = 0.095) :
  3 650 (m = 2), 5 445 (m = 6), 5 927 (m = 8).
- Pilote : pas de NULL_PLAN ; les discordances HOLD nulles du pilote servent seulement à la prévision budgétaire du full.

## 11. Sensibilités et diagnostics (B1, B3)

**11.1 s2_dev** (setup primaire) : P_conf recalibrées sur les mêmes clés CAL_NULL (nouveaux `calibration_id`, s2 différent),
évaluées sur HOLD et ALT ; descriptif. Si s2_dev = s2_common, identités identiques, calculs réutilisés, ligne
`S2_DEV_EQUALS_COMMON`.

**11.2 γ_M = H/α = 5000** (setup primaire) : ONLINE_INFO_MIX et ONLINE_PREFIX_MIX (w = 128) avec M(·, 5000), identités et
calibrations propres ; FULL_K et FIXED_* inchangés (identités inchangées) ; descriptif.

**11.3 Diagnostics hors ligne** (après hachage des masques ; jamais entrées d'une sélection) :
- V statique : V(S) = I_true(S)/M(|S|, γ_M) (exact en EXACT ; versions surrogate et jointe en FITTED).
- V adaptatif : V̄_H = (1/H) Σ_{t=1..H} I_true(S_t)/M(|S_t|) sur l'horizon complet des trajectoires ALT (masques calculés
  pour tout t, indépendamment de l'alarme : aucune dépendance au résultat).
- V/RMST : par setup et application, corrélation de rang de Spearman entre V moyen (V̄_H) et RMST_H observé sur les cellules
  (politique × famille) ; table et CSV ; `DESCRIPTIVE_V_RMST` ; jamais utilisé pour sélectionner, régler ou revendiquer.
- Ratio de prior apparié ρ(S) par politique statique et famille ; moyenne temporelle pour les adaptatives.
- Télémétrie de sélection : lectures de screening K·H par trajectoire, opérations de sélection, distribution de d_t,
  fréquences d'axes, commutations, temps d'atteinte du sous-ensemble oracle, Jaccard avec l'oracle, seuil h par politique,
  unités de scan et CPU par politique.
- Diagnostics H0 par axe (B3) : fréquences de sélection ONLINE sur HOLD_NULL, termes c_k² et (Var0_k − 1)/m, rapport aux
  fréquences H0 du bras EXACT (référence) ; descriptif.
- FITTED : KL projeté atteint (surrogate, joint) par famille ; dispersion des axes support sur les axes ajustés.

## 12. Paramètres préenregistrables

| Paramètre | Valeur | Provenance |
| --- | --- | --- |
| H, α, K, T_fit | 250, 0.05, 20, 1000 | SPEC_PROPOSAL |
| N | {32, 239} dans les deux bras gaussiens, N réel dans les clés | SPEC_PROPOSAL (O4) |
| γ_M | 504 `ANALYTIC_PROXY` ; sensibilité 5000 | SPEC_PROPOSAL ; NOTIFICATION_DECISION |
| I* | 0.25 (0.10 et 0.50 seulement après revue) | SPEC_PROPOSAL |
| w | {32, 128} ; primaire 128 | grille SPEC_PROPOSAL ; primaire NEW_PROPOSAL |
| s2 | s2_common principal ; s2_dev sur grille {1, 4, 16, 64} × s2_common | SOURCE_RULE ; NOTIFICATION_DECISION ; grille NEW_PROPOSAL |
| affine | OLS d = 1..min(16, K) | plage SPEC_PROPOSAL ; méthode NEW_PROPOSAL |
| spectre | λ1 = 16, λk = 0.05 + 6 exp(−(k − 2)/8) | SPEC_PROPOSAL |
| repère | QR d'une matrice dont la première colonne est 1/sqrt(N) et les autres gaussiennes de graine `frame(N)` ; signes diag(R) > 0 ; jamais de remplacement après QR ; hash par N | NEW_PROPOSAL |
| univers | E_res = PC 2..21, E_mkt = PC 1..20, fixés par application | SOURCE_RULE ; NOTIFICATION_DECISION |
| familles | §5 | SPEC_PROPOSAL (F0–F3) ; NOTIFICATION_DECISION (HEAD) ; poids et signes NEW_PROPOSAL |
| famille Φ | §9.3 | NOTIFICATION_DECISION (équilibre) ; NEW_PROPOSAL (setup, H1–H3, δ_NI = 0.10, m = 3) |
| κ_geo, κ_det | 0.80, minimum des 16 signes HEAD pour la géométrie ; U_PREFIX<=0.80H pour la détectabilité (§9.5) | NEW_PROPOSAL v2.1 |
| NULL_PLAN smoke | n_plan=n_min=40, n_cap=80, seulement sous GO runtime | NEW_PROPOSAL v2.1 |
| tri-état nul | queue 0.05, ε_v = 0.01 | NEW_PROPOSAL |
| NULL_PLAN | η = 0.10, β = 0.2, n_min = 2000, n_plan = 2000, n_cap = 20 000 | NEW_PROPOSAL (n_cap : R3) |
| d_dev | {1, 2, 4, 8, 16, 20} ∩ [1, K], critère J, plus petit d | NOTIFICATION_DECISION ; critère NEW_PROPOSAL |
| tailles smoke | 40 par rôle ; DEV n_dn = 40, n_da = 10 par famille, n_lib = 100 | NEW_PROPOSAL |
| tailles pilote | 200 par rôle ; DEV n_dn = 200, n_da = 50 par famille, n_lib = 100 | SPEC_PROPOSAL (100–200) ; DEV NEW_PROPOSAL |
| tailles full | P_conf n_cal = 10 000 ; autres 2000 par rôle ; n_alt = 2000 par famille ; DEV n_dn = 1000, n_da = 200 | SPEC_PROPOSAL (2000) ; NEW_PROPOSAL (R3) |
| bootstrap | B = 10 000, percentile apparié | NEW_PROPOSAL |
| graine racine | `seed` uint32 du YAML | NEW_PROPOSAL |

## 13. Graines, identités, partitions, schéma — v2.1 normative

Les §§3.2–3.8 de [l'amendement v2.1](plan-32-v2.1-amendment.md) remplacent intégralement les anciennes
identités, partitions et publication. Descripteur pré-exécution, autorisation sans digest futur, table des identités,
phase records, états/reprise, exclusions de realization_id et publication atomique y sont normatifs.
Les précisions de réception C32-R5/R6 du §21 priment sur le texte brut de l'amendement.

- SeedSequence locale [32,seed,crc(campaign),crc(domain),*parts], indépendante des workers ; clés du §4.1,
  sans design_id ni setup_id. Le plan de graines complet est calculable avant tirage.
- N réel dans les clés ; EXACT N32/N239 indépendants ; bruit ALT sans famille partagé entre familles.
  EXACT scores PC1..21 iid normaux ; FITTED y=A g+c(+beta_hat) au fit figé ; T7 conserve ses proxies.
- design_id inclut règles, rôles, cellules, limites maximales, code/env et graines ; aucun résultat futur, GO,
  authorization, chemin ou jobs réel. realization_id est calculé après les phases, jamais requis pour les autoriser.
- Masques uint32 LOCAL_HASHED_ONLY avec SHA ; fusion des petites tables en flux sans chargement global de masques.
  Payloads FAIR et schéma /1 ; noms POSIX relatifs ; aucun fichier commité >50Mo.
- Précision C32-R6 : le tag16hex n'est pas injectif ; collision avec un autre design_id complet ⇒ StagingMismatch.
  Deux destinations au même basename partagent le log-dir par défaut : fournir --log-dir distinct pour deux calculs
  indépendants ; sinon staging existant sans --resume ⇒ OutputExists. T56 couvre ce cas.
- Télémétrie séparée : CPU SELF+CHILDREN après jointure, mur/RSS et memory.peak agrégé du scope ou NOT_MEASURED.
  Ces valeurs, les chemins et l'autorité ne participent pas aux identités ; reprise dans l'enveloppe restante uniquement.

## 14. Autorisations — v2.1 normative

La garde de l'amendement §3.4 remplace l'ancien scientific_identity_sha256 : stage, design_id pré-exécution,
référence GO présente/SHA concordant/texte citant design_id complet, jobs réel<=jobs_max. Avant tout tirage,
worker, staging ou écriture scientifique. Portée et limites maximales sont liées à design_id ; aucun GO/digest
futur auto-référent. La référence d'autorité est vérifiée séparément et consignée hors des deux identités.
La garde reste un fil-piège, pas un accord ou une signature inventés.

GO technique séparé : TDD et fixtures bornées R/A/B, revue à chaque lot.
GO runtime séparé : smoke fonctionnel identités/reprise puis profilage. Pilote/full : GO scientifiques du chercheur.
Le gel du §5 de l'amendement précède toute consultation de puissance smoke/pilote ; les sorties SMOKE_NO_CLAIMS
et fixtures ne servent jamais au réglage. R1 et paramètres HEAD sont préenregistrés avant ce premier runtime.

## 15. Tests TDD (`tests/test_pca_info_online.py` ; RED avant GREEN)

Fixtures minuscules et déterministes ; fichier < 60 s ; aucune assertion sur un niveau de FPR aléatoire ; les fixtures
statistiques sont une qualification technique, pas une preuve de performance ; aucun test ne vaut GO scientifique.

Lot A — noyaux :
1. `test_mixture_cost_is_reused` : `pio.mixture_cost is pdb.mixture_cost` ; M(4, 504) arrondi à 1.5696.
2. `test_affine_ols_distinct_from_chord` : (a, c) OLS ≠ `pdb.affine_costs(504)` ; a, c > 0 ; min(16, K) < 2 refusé.
3. `test_info_sort_equals_greedy_equals_exhaustive` : q dyadiques avec ex aequo et zéros, K <= 8, coûts MIX, AFF et deux
   tables ; d et S identiques à l'énumération des 2^K − 1 sous-ensembles et au glouton.
4. `test_adjacent_tie_strictly_decreasing_q` : q = (2, 1), C = (2, 3) ⇒ d = 1.
5. `test_prefix_full_enumeration_non_monotone` : q canonique (0, 0, 3, 0, 1) ⇒ maximiseur tardif ; un mutant à arrêt
   précoce donne un autre d.
6. `test_best_sets_matches_select_top_q` : lignes aléatoires écrêtées ⇒ mêmes d et S que `pdb.select_top_q`.
7. `test_online_masks_predictable` : perturber y_t puis y_{>t} laisse S_1..S_t inchangés.
8. `test_online_masks_onset_invariance` : changer un début futur et la direction (fixture τ* > 1) laisse les masques
   pré-début inchangés.
9. `test_online_masks_match_scalar_reference` : boucle scalaire sélection → observation → mise à jour = vectorisé.
10. `test_fallback_min_E_online_only` : t = 1 et historique nul ⇒ {min E} pour INFO et PREFIX ; oracles et statiques
    inchangés.
11. `test_masked_scan_static_equals_scan_statistic_same_s2` : masque constant ⇒ W = `pdb.scan_statistic(Y[..., S], s2)`
    (rtol 1e−12) au s2 commun.
12. `test_masked_scan_bruteforce` : H = 12, K = 4, masques aléatoires ⇒ logL(τ, t) pour tout τ, t égal à une référence
    `math.fsum` ; W et premiers franchissements identiques.
13. `test_masked_scan_no_rescore` : perturber y non masqué laisse W inchangé ; un axe entrant en t0 ne contribue qu'à partir
    de t0 ; n = 0 contribue 0.
14. `test_masked_scan_column_pruning_exact` : élagage des colonnes jamais sélectionnées ⇒ W identique.
15. `test_common_prior_independent_of_selected_dimension` : s2 identique pour toute politique et tout d_t ;
    s2 = 2 ln(H/α)/(HK).
16. `test_fluid_score_never_labelled_exact_delay` : énumérations de colonnes et libellés de V/M sans « delay »/« ADD »
    exact ; `ANALYTIC_PROXY` présent.
17. `test_tango_constrained_mle_boundaries_and_symmetry` : q̃ contre maximisation bornée indépendante
    (`scipy.optimize.minimize_scalar`) de b log(q + Δ0) + c log q + (n − b − c) log(1 − 2q − Δ0), termes à compte nul omis,
    sur >= 81 cas (zéro discordance, b = 1/c = 0 et inverse, b + c = n, Δ0 extrêmes), écart <= 1e−7 ; les neuf intervalles
    limites de l'audit (n = 2000, queue 0.05/6) reproduits en littéraux à 1e−12 ; symétrie b ↔ c ; sortie dans [−1, 1].
18. `test_zero_discordance_interval_nonzero` : b = c = 0 ⇒ ±z²/(n + z²) ; n = 2000, queue 0.05/6 ⇒ ±0.0028573816149894.
19. `test_cp_tristate_boundaries` : n = 2000, queue 0.05 : k = 102 VALIDATED, k = 103 non ; k* = min{k : L(k) > 0.06} ⇒ FAILED,
    k* − 1 ⇒ INCONCLUSIVE ; k = 0 et k = n ; `binom.cdf(102, 2000, 0.05)` = 0.6067391237795827 (1e−12) ; bornes CP égales à
    `proportion_confint(method="beta")` à alpha = 2 × queue.
20. `test_fitted_unclipped_score_expectation` : lois à trois points de moyenne c et variance v, énumération exacte en
    `fractions.Fraction` pour m ∈ {1, 2, 3} ⇒ E[½(bhat² − 1/m)] = ½(c² + (v − 1)/m) = `null_score_bias(c, v, m)` ;
    EXACT (c = 0, v = 1) ⇒ 0.
21. `test_null_only_holdout_planning_rule` : `plan_holdout` sur indicateurs nuls synthétiques : monotone en discordance ;
    |Δ|⁺ >= ε ⇒ n_cap et `PLAN_CAPPED_EXPECT_INCONCLUSIVE` ; n_hold >= n_min ; aucun argument ALT ; déterministe ;
    témoin de puissance normale bilatérale 0.80 avec beta/2 et 0.60 avec l'ancienne formule ; aucune puissance familiale annoncée.
22. `test_refusals` : K, d, E vide, coûts non finis ou négatifs, γ_M <= 1, w < 1, valeur propre <= 0, écart relatif de
    valeurs propres LW < 1e−10 sur les K + 2 premiers axes, clé de configuration manquante, b + c > n ou n = 0 pour Tango ⇒ refus.

Lot B — orchestration :
23. `test_nonoracle_family_permutation_invariant_masks_threshold_hits` : mêmes tableaux d'observations ALT étiquetés
    (F0, F1, F2, HEAD) puis étiquettes permutées ⇒ masques (octets), h et T identiques par tableau ; seules les colonnes
    d'étiquette changent.
24. `test_nonoracle_calibration_id_reused_across_families` : une seule ligne de calibration non-oracle par (setup,
    politique) ; tous les trials ALT des quatre familles la référencent ; compteur de scans CAL non-oracle = n_cal ×
    nombre d'identités, jamais × familles ; HOLD évalué une fois.
25. `test_nonoracle_dependency_graph_excludes_oracle_metadata` : méta remplacée par un objet qui lève à tout accès, Δ, τ* et
    famille empoisonnés ⇒ sorties non-oracles identiques sans exception ; AST de `nonoracle_masks`, `online_masks`,
    `calibrate_nonoracle`, `evaluate_nonoracle` : aucun paramètre ni nom libre parmi {meta, delta, tau_star, family,
    oracle, q_true, sigma0, mu0, c_true, var0}.
26. `test_oracle_calibration_non_deployable_and_separate` : une calibration par (politique oracle, famille), libellé
    `NON_DEPLOYABLE_ORACLE_CALIBRATION`, méta des rôles CAL_NULL non nulle, compteur de générateur : aucune clé ALT tirée
    pendant CAL ; contrastes avec oracle ⇒ `ORACLE_SEPARATE`.
27. `test_head_population_support_and_equal_information` : HEAD = PC {2, 3, 4, 5} ⊂ E_res, q_k = I*/4, ½Δ'Σ0^{-1}Δ = I*
    (1e−12), signes de clés distinctes ; en EXACT, sous-ensembles oracle INFO et PREFIX identiques (d = 4).
28. `test_family_supports_universes_and_unsupported` : supports et normalisation F0/F1/F2/F3 ; F2 = PC {3, 9, 17, 21} ;
    K < 20 ⇒ F2 `UNSUPPORTED` ; CPV90 RESIDUAL `OUTSIDE_UNIVERSE` ; F3 en MARKET seulement ; univers lus depuis la
    configuration de l'application.
29. `test_fitted_injection_independent_of_fit` : même clé méta ⇒ Δ population identique sous deux fits ; seul β̂ change.
30. `test_confirmatory_family_balanced_and_frozen_before_alt` : bloc Φ de la configuration = H1, H2, H3 au même setup,
    inclus dans l'identité scientifique ; inférence limitée aux contrastes déclarés ; partitions ALT empoisonnées sans effet
    sur Φ ni m ; Φ sans contrôle HEAD ou déséquilibrée ⇒ refus.
31. `test_full_k_comparison_not_gated_on_other_cells` : fixture où H1 est `NOT_ESTABLISHED` ⇒ H3 calculée et libellée.
32. `test_null_only_holdout_planning_and_independent_evaluation` : clés NULL_PLAN disjointes ; n_hold haché avant toute
    génération HOLD (journal d'ordre) ; ALT empoisonné sans effet sur n_hold ; HOLD = exactement n_hold trajectoires neuves.
33. `test_development_prior_frozen_and_alt_poisoning_invariant` : qbar, d_dev, s2_dev, `dev_id` identiques quand
    CAL/NULL_PLAN/HOLD/ALT sont empoisonnés ; clés DEV disjointes ; bibliothèque équilibrée et poolée.
34. `test_gamma_sensitivity_has_own_calibration_identity` : γ_M 504 → 5000 change `policy_id`/`calibration_id` des seules
    politiques MIX online ; FULL_K et FIXED_* inchangés.
35. `test_eigenmean_not_classical_kaiser` : règle λ_k >= moyenne_E λ sur la covariance restreinte ; fixture où Kaiser de
    corrélation diffère ; aucun libellé « KAISER ».
36. `test_global_and_residual_cpv90_distinct` : CPV90 global ≠ RESIDUAL_CPV90 ; EXACT : RESIDUAL_CPV90 = PC 2..16 ;
    k90(N = 32) = 17 ; N = 239 ⇒ `OUTSIDE_UNIVERSE` en MARKET.
37. `test_development_prefix_single_frozen_dimension_across_families` : d_dev ∈ {1, 2, 4, 8, 16, 20} ∩ [1, K], une valeur
    par setup, même objet politique pour toute famille ; égalité ⇒ plus petit d ; clés DEV seulement.
38. `test_online_cannot_read_true_center_or_covariance` : μ0, Σ0, c, Var0 du simulateur remplacés par NaN ou fil-piège ⇒
    masques ONLINE identiques ; signature `online_masks` = (Y, window, cost, order).
39. `test_fitted_oracle_is_surrogate_only` : lignes oracle FITTED `ORACLE_DIAGONAL_SURROGATE`, EXACT `EXACT_ADDITIVE_KL` ;
    aucun libellé « KL_OPTIMAL » ni « JOINT_OPTIMUM » en FITTED ; colonne I_joint présente.
40. `test_null_axis_selection_and_screening_cost_telemetry` : colonnes de télémétrie exactes sur une séquence de masques
    construite (commutations, d_t, fréquences, K·H lectures, h, unités) ; fréquences H0 calculées sur HOLD seulement.
41. `test_role_keys_disjoint_and_family_free_noise` : clés DEV/CAL/NULL_PLAN/HOLD/ALT disjointes, entropies uniques,
    campagnes disjointes, N réel, aucune famille dans les clés de bruit.
42. `test_exact_additive_equals_joint_and_fitted_surrogate_labelled` : EXACT Σq = `pdb.kl_mean` ; FITTED surrogate ≠ joint,
    étiquetés ; T7 étiqueté proxy.
43. `test_calibration_rank_deterministic` : maxima distincts ⇒ alarmes CAL = r ; h = nextafter(tri[n − r − 1]) ; identique au
    rejeu ; aucune assertion de niveau de FPR.
44. `test_worker_count_does_not_change_scientific_artifacts` : configuration minuscule, `--jobs 1` et `--jobs 3` ⇒
    artefacts scientifiques identiques (hash canonique, télémétrie exclue).
45. `test_resume_interrupt_and_stale_refusal` : interruption après k partitions puis `--resume` ⇒ identique ; fingerprint
    altéré ⇒ `PartitionMismatch` ; npz sans JSON recalculé ; JSON sans npz refusé ; partition manquante ⇒ `INCOMPLETE`,
    aucun agrégat.
46. `test_resource_refusal_preserves_incomplete_state` : échéance dépassée ⇒ `ResourceBlocked`, partitions terminées
    intactes et reprenables, aucun agrégat.
47. `test_pilot_full_refuse_without_matching_authorization` : bloc nul, stage faux, identité différente, portée inférieure,
    jobs > jobs_max, GO absent ou SHA différent ⇒ refus sans écriture ; acceptation seulement sur concordance complète
    (fixture `tmp_path`) ; empreinte calculable avant DEV/CAL ; tout appel aux générateurs avant autorisation lève ;
    jobs/répertoire/télémétrie changés ne changent pas l'empreinte, code/graine/plan scientifique changés l'invalident.
48. `test_no_real_data_access` : AST du script : aucun import `jepadrift.data_loader`, aucun chemin `data/`, aucune date
    >= 2020.
49. `test_v_rmst_diagnostic_offline_descriptive` : V̄_H sur t = 1..H après hachage des masques, `DESCRIPTIVE_V_RMST` ;
    aucune fonction de sélection ne reçoit V ni RMST.
50. `test_manifest_relative_paths_and_local_hashed_only` : chemins relatifs POSIX seulement ; partitions locales
    `LOCAL_HASHED_ONLY` avec SHA ; aucune donnée absente déclarée publiée ; aucun fichier > 50 Mo sous `results/`.
51. `test_tiny_oracle_fluid_score_dominates` : V de l'oracle INFO >= V(S) de tout sous-ensemble (score fluide seulement,
    aucune dominance de RMST affirmée).

Les 51 tests ci-dessus sont conservés. Ajouter T52–T68 de l'amendement §7, sans retirer T21/T47 amendés.
Renforcer T41/T52 : toutes les clés, bootstrap inclus, sous fils-pièges sans tirage ni empreinte réalisée.
Renforcer T56 : deux destinations au même basename exigent des log-dir distincts ou un refus explicite.
Les interfaces pures et de staging/HEAD du §3.8 de l'amendement complètent le §2.4.

## 16. Registre 32 (lot R, premier lot, seulement après GO technique)

1. RED : `tests/test_check_prompts.py` — docstring l. 1 « 34 prompts » ; l. 45 `test_cli_discovers_the_34_expected_ids`
   (34 prompts, 30 `prompt-*.md`, `ids["32"] == "prompt-32-pca-info-online.md"`,
   `13_CODEX_AMORCAGE_PCA_INFO_ONLINE_2026_11_14.md` non découvert) ; l. 80 `len(history) == 30` ; l. 149–150 ID
   artificiel `99_STREAM_PCA_DRIFT_Y.md`, titre `## PROMPT 99 — Y`, attente `"unexpected ['99']"`.
2. Ligne 1 du prompt 32 seulement : `# STREAM 32 — ` devient `## PROMPT 32 — ` ; reste octet pour octet ; témoin
   `tail -n +2 | sha256sum` = `15a3003864e43c275fb2c6ce3113d4180e4cbc771b011f9bdbc60dbeb8784b96` ; SHA historique
   `db2ef871…` conservé, nouveau SHA publié dans le GO et le wrapup. Aucun contrat scientifique du prompt modifié : les
   amendements de la notification vivent dans `plan-32.md` (`NOTIFICATION_DECISION`) et `docs/sections/pca_info_online.md`.
3. `tools/check_prompts.py:19` : ajout de `"32"` à `EXPECTED_IDS` ; aucune autre logique.
4. `prompts/streams/INDEX.md` : une ligne après la ligne 28 du tableau de routage (l. 113) :
   `| 32  | \`prompt-32-pca-info-online.md\` | PCA-INFO-ONLINE (oracle vs online) | T→CC | P0 | — | 28-PCA, 31 | — | Opus | max | plan v2 14/11 |`.
5. `.venv/bin/python tools/check_prompts.py --sync-master` seulement : bloc 32 ajouté en fin de master ; les 33 blocs
   historiques restent octet pour octet (`cmp -n 188955`), 34 titres ; tous les autres prompts inchangés.
6. `make prompts-check` (PATH `.venv/bin` en tête) après implémentation : `prompts-check: 34/34 (30 prompt-*.md + 4
   [0-9][0-9]_STREAM_PCA_DRIFT_*.md: 28-PCA, 29, 30, 31)`. Non exécuté à ce stade.
7. Amorçage 13 : SHA `6c047b44…` inchangé, jamais découvert.

## 17. Ressources et comptes théoriques (unités seulement, aucune mesure, aucun coût en temps)

- Unité : un scan d'une trajectoire sur K_eff coordonnées coûte U = K_eff H(H + 1)/2 mises à jour ; H(H + 1)/2 = 31 375 ;
  borne K_eff <= 20 ⇒ U <= 627 500. Bornes supérieures : sans arrêt précoce ALT, sans élagage ni déduplication par identité.
- Scans par setup gaussien (c = n_cal, h = n_hold, a = n_alt par famille, DEV : dn, da par famille) :
  RESIDUAL = 13 non-oracles × (c + h + 4a) + 16 (oracle × famille) × (c + h + a) + 6 candidats d_dev × (dn + 4 da) ;
  MARKET = 11 non-oracles × (c + h + a) + 4 oracles × (c + h + a). CAL et HOLD non-oracles une fois par setup (A1).

| Phase | Composition | Scans | Unités (borne) |
| --- | --- | --- | --- |
| Smoke | 4 setups gaussiens à 40/rôle (7 320 chacun) + extras primaires 2 160 | 31 440 | 1.97e10 |
| Pilote gaussien | 4 setups à 200/rôle (36 600 chacun : RESIDUAL 27 600, MARKET 9 000) + extras primaires 10 800 (sélection s2_dev 4 800, sensibilité s2 3 600, γ_M 2 400) | 157 200 | 9.86e10 |
| Pilote T7 (après portes gaussiennes) | 2 setups FITTED_LW_T7 | 73 200 | 4.59e10 |
| Full, setup primaire (R3 par défaut) | P_conf 3 × 40 000 (CAL 10 000, NULL_PLAN 2000, HOLD <= 20 000, ALT 8000) + 10 non-oracles × 12 000 + oracles 96 000 + d_dev 10 800 + s2_dev 21 600 + sensibilités 60 000 + MARKET 90 000 | 518 400 | 3.25e11 |
| Full, setup descriptif | 2000/rôle : RESIDUAL 262 800 + MARKET 90 000 | 352 800 chacun | 2.21e11 chacun |
| Full T7 (2 setups descriptifs) | idem | 705 600 | 4.43e11 |

- EXACT N = 32 et N = 239 : même loi éligible (invariance théorique), mais deux réplications expérimentales comptées
  séparément.
- Hors scans, par trajectoire : génération EXACT 21 H = 5 250 normales ; FITTED N = 239 : H N = 59 750 normales et
  ≈ 1.25e6 multiplications-additions, partagées par toutes les politiques et par les familles ALT ; sélection online
  ≈ H(K log₂ K + 3K) ≈ 3.7e4 opérations par trajectoire-politique ; screening K H = 5 000 lectures ; diagnostics de capture
  K H = 5 000 ; I_joint <= K³/3 ≈ 2 700 par sous-ensemble distinct (mémorisé) ; bootstrap B n_alt = 2e7 indices par (setup,
  famille), puis une moyenne par contraste.
- Mémoire théorique par worker (bloc de 100 trajectoires) : bruit FITTED N = 239 ≈ 47.8 Mo, scores ≈ 4.2 Mo, sommes préfixes
  du scan ≈ 6 Mo, temporaires (B, t, K) ≈ 24 Mo, masques 0.1 Mo par politique, plus interpréteur et bibliothèques non mesurés
  pour ce code. Pic agrégé connu seulement par `memory.peak` du scope.
- Disque local : masques ONLINE 1 ko par trajectoire-politique avant compression ; pilote ≈ 63 Mo ; full setup primaire
  ≈ 248 Mo ; `LOCAL_HASHED_ONLY`.
- Enveloppe proposée (NEW_PROPOSAL, à fixer par Codex et le chercheur) : scope superviseur
  `systemd-run --user --scope -p MemoryMax=32G -p OOMPolicy=stop`, GNU time hors du scope, `timeout 2700`,
  `memory.peak`/`memory.events` relevés par le superviseur, verrou partagé ; pilote cumulé <= 4 CPU-h, <= 45 min par
  invocation, 8 workers ; profil `--jobs 1/4/8/12` après GO runtime (sorties scientifiques égales, débit, `memory.peak`),
  16 seulement avec GO, charge et RAM ; 24 cœurs physiques = limite de planification, aucun gain linéaire promis.
- Faisabilité conditionnelle, sans hypothèse de vitesse : le pilote gaussien tient dans 4 CPU-h seulement si le débit mesuré
  au smoke dépasse 9.86e10/14 400 ≈ 6.9e6 unités par seconde-CPU ; sinon découpage ou réduction sous nouveau GO. Aucun
  budget full avant mesure du pilote.

## 18. Lots et portes

| Lot | Contenu | Porte d'entrée | Sortie et revue |
| --- | --- | --- | --- |
| R | registre §16 | GO technique écrit Codex | RED/GREEN `tests/test_check_prompts.py`, prompts-check 34/34, témoins SHA |
| A | noyaux §2.4 ; T1–T22 | R accepté | RED/GREEN, pyflakes ; revue Codex mathématique et temporelle |
| B | setups, familles, DEV, calibrations, NULL_PLAN, inférence, partitions, identités, autorisation, CLI, docs ; T23–T51 | A accepté | RED/GREEN ; revue Codex fuites et identités |
| C | bout en bout design/realization, publication/reprise ; jobs1/8 ; puis profil1/4/8/12 (amendement §5) | GO runtime distinct citant design_id + verrou libre | identités/SHA égaux, coûts MESURÉS ; aucune puissance utilisée pour régler |
| Pilote | §17, T7 après portes gaussiennes (complétude, aucun `NULL_FAILED` non-oracle, invariances vertes ; jamais une performance) | GO pilote chercheur (R1 gelé, R2) | `PILOT_ONLY`, prévision CPU/RAM/disque du full, discordances nulles |
| Full | §9–§10 | GO full chercheur (R3–R5) | rapport Φ et descriptif, résultats négatifs publiés tels quels |

Chaque lot s'arrête pour revue Codex. Avant tout commit : wrapup `prompts/wrapups/wrapup-32.md` ; `docs/DEVIATIONS.md`
(`C-pca-info-online-*`) seulement pour un écart au plan canonique ; `docs/MAPPING.md` dès qu'un nombre du pilote est
rapporté. Le plan canonique `prompts/plans/plan-32.md` est écrit par Codex.

## 19. Vérification (commandes qui échouent en cas d'écart ; aucune exécutée pour ce plan)

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
.venv/bin/python -m pytest -q tests/test_check_prompts.py tests/test_pca_info_online.py
.venv/bin/python -m pyflakes experiments/pca_info_online.py tests/test_pca_info_online.py tests/test_check_prompts.py tools/check_prompts.py
PATH="$PWD/.venv/bin:$PATH" make prompts-check
test "$(sha256sum experiments/pca_drift_benchmark.py | cut -d' ' -f1)" = 8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373
test "$(tail -n +2 prompts/streams/prompt-32-pca-info-online.md | sha256sum | cut -d' ' -f1)" = 15a3003864e43c275fb2c6ce3113d4180e4cbc771b011f9bdbc60dbeb8784b96
cmp -n 188955 <(git show e33ac1d:prompts/Prompts_Claude_Code_v5.md) prompts/Prompts_Claude_Code_v5.md
test "$(grep -c '^## PROMPT ' prompts/Prompts_Claude_Code_v5.md)" = 34
# lot C seulement, après GO runtime Codex :
.venv/bin/python experiments/pca_info_online.py --config configs/pca_info_online.yaml --mode smoke --jobs 1 --output-dir results/pca_info_online/smoke_j1
.venv/bin/python experiments/pca_info_online.py --config configs/pca_info_online.yaml --mode smoke --jobs 8 --output-dir results/pca_info_online/smoke_j8
# comparaison des champs scientifiques canoniques (télémétrie exclue), puis make check par Codex
```

## 20. Décisions du chercheur, limites, incertitudes

**Décisions réellement nécessaires.**
- R1 (avant le PREMIER GO runtime et toute lecture de puissance smoke/pilote) : famille Φ préenregistrée,
  setup FITTED_LW_GAUSSIAN N239 fit0, F2, contrôle HEAD avec NI=.10 et kappa_geo=kappa_det=.80,
  H3 contre FULL_K, m=3 Bonferroni. Supports, I*, w, prior/grilles et seuils figés. Aucun changement informé par ALT.
- R2 (avant le pilote) : GO pilote — portée (4 setups gaussiens et extras primaires ; T7 après portes), 200 par rôle,
  enveloppe (32 Gio agrégés, <= 4 CPU-h cumulés, <= 45 min par invocation, 8 workers), après mesure du smoke.
- R3 (avant le full) : tailles — n_cal de P_conf (proposé 10 000), n_plan 2000, n_cap 20 000, puissance 0.8, n_alt 2000 par
  famille ; grille descriptive du full (autres setups, T7) ; enveloppe issue du pilote.
- R4 (avant le full) : exigence de couverture finie exacte pour l'équivalence FPR — défaut Tango asymptotique ; variante
  CP–Bonferroni ≈ 2.5 × n_hold.
- R5 (avant le full) : portée `FIT_CONDITIONAL` (fit 0) ou couche `OUTER_FIT` (coût × nombre de fits).

**Limites conservées.** Coût fluide ≠ délai réel (M proxy ; prior commun décalé de 7.3× à 73× du prior apparié ; V/RMST
descriptif) ; qhat bruité, écrêté, biaisé sous FITTED H0 de ½(c² + (Var0 − 1)/m), recherche répétée non couverte par M,
seuil propre à la politique seul absorbant le coût H0 de la recherche ; fit conditionnel (fit 0) ; censure à H, RMST_H
jamais ADD ; comparabilité FPR ±0.01 possiblement hors budget ⇒ `COMMON_NOMINAL_ALPHA_ONLY`, intervalles score et bootstrap
asymptotiques ; prior ex ante structurel ; gains contextuels ; repli {min E} favorable à HEAD et F3 au premier pas pour les
deux ordres.

**Incertitudes (aucune exécution faite).** I1 débit inconnu : coûts en unités seulement. I2 discordances, ρ et Δ_cond
inconnus avant NULL_PLAN et pilote. I3 valeurs manuelles (EIGENMEAN, RESIDUAL_CPV90, CPV90, EXANTE, V fluides) recalculées
par le code. I4 dispersion des supports F2 et HEAD sur les axes ajustés à N = 239, T_fit = 1000 : rapportée, pas refusée.
I5 algèbre de Tango vérifiée par l'audit Codex seulement ; tests non implémentés. I6 n_cal = 10 000 et n_cap = 20 000
peuvent dépasser le budget full ⇒ INCONCLUSIVE, sans relâcher la marge ni consulter ALT.

**Porte courante.** `TECHNICAL_GO = R_A_B_GATED`, activation initiale R ; `RUNTIME_GO = ABSENT` ;
`PILOT_GO = ABSENT` ; `FULL_GO = ABSENT`.

## 21. Décision GO intégrée — v2.1 revue, lots techniques conditionnés

Décision Codex du 14 novembre 2026 après lecture intégrale de la v2, de l'amendement v2.1 et de T1–T68,
avec contre-revue indépendante statique de C1–C3. Les corrections de réception ci-dessous sont intégrées.
**GO technique R/A/B conditionné, écrit séparément dans `prompts/GO-stream-32.md` ; premier lancement limité à R.**
Chaque lot exige une réception écrite avant le suivant. Aucun test d'implémentation n'est présenté comme déjà passé.

Amendements de réception, intégrés aux sections normatives ci-dessus avant toute implémentation :

- C32-R1 : puissance TOST bilatérale dimensionnée avec z_{1−β/2}, chiffres et témoin T21 corrigés ; puissance par contraste.
- C32-R2 : loi Beta de F_cond sous maxima iid continus sachant setup/politique ; garantie de rang sous échangeabilité maintenue.
- C32-R3 : empreinte pré-exécution séparée de la provenance réalisée, autorisation avant tout tirage, reprise sans cycle ; T47 étendu.
- C32-R4 : appel q_plugin sur projections non standardisées, première colonne imposée avant QR, limites numériques de Tango explicites.
- C32-R5 : plan de graines pré-exécution jusqu'au cap, bootstrap inclus ; aucune clé issue de setup_id/design_id ou d'une empreinte réalisée ; T41/T52 renforcés.
- C32-R6 : tags tronqués contrôlés par digest complet ; destinations au même basename avec log-dir explicites distincts, sinon refus ; T56 renforcé.

Ces amendements sont des corrections mathématiques ou de contrat d'exécution ; ils ne changent ni l'horizon, ni l'amplitude,
ni la cible PCA figée et moyenne, ni les familles approuvées par la notification. Φ et sa marge de non-infériorité de 10 %
restent des propositions préenregistrées à confirmer avant le PREMIER GO runtime et toute puissance smoke/pilote ;
aucune lecture ALT de campagne ne les a informées. Les seuils HEAD .80 gardent le même statut proposé.
Tango/TOST et bootstrap gardent leur qualification asymptotique. Les tailles et ressources full restent proposées.

Le GO technique distinct autorise uniquement le TDD et les fixtures bornées du lot activé. La notification n°15 n'a
autorisé aucun calcul de campagne ; aucune science nouvelle n'a été exécutée pendant la revue v2.1. Aucun smoke CLI,
profilage, pilote, full, accès réel, J4, JEPA, autre stream, commit/push par l'implémenteur ou Remote Control n'est autorisé.
Les validations de code doivent passer avant tout GO runtime séparé, puis les GO scientifiques pilote/full restent propres.
