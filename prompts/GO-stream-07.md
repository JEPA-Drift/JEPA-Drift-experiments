# GO — Stream 07 (pipelines P2-C, P3-C, P3-D, P3-CS, P7 et calibrations) : revue du plan et réponses aux hypothèses

Date : 2026-10-16.
Destinataire : instance Claude Code en charge de l'implémentation du stream 07
(`prompts/streams/prompt-07-pipelines.md`).
Plan concerné : `~/.claude/plans/greedy-sparking-mist.md` → plan final à consigner dans
`prompts/plans/plan-07.md`.

## Instruction préalable — à exécuter AVANT l'implémentation

**`prompts/plans/plan-07.md` n'existe pas encore** (constaté à la rédaction de ce GO). L'enregistrer
(règle C-plan-recording, AGENTS.md:86) en y intégrant les réponses ci-dessous dans la section
« Décision GO intégrée » (Tâche 0 du plan), en remplaçant chaque (Hn) par (GO Hn) ou par la décision
révisée — comme `plan-06.md`. **Aucune ligne de code avant que `prompts/plans/plan-07.md` soit écrit.**

**Contexte de concurrence (à respecter impérativement).** Au moment de ce GO :
- HEAD = `672ce26` (stream 10, EUROFIDAI D4), commit **local uniquement** — `origin/main` est à
  `c9d93f1`. La base du plan (`c9d93f1` ou un descendant) est satisfaite. Si `672ce26` n'est toujours
  pas poussé au moment du push du stream 07, le range `origin/main..HEAD` couvre les deux commits :
  vérifié sans données EUROFIDAI (spécification, loader, schéma, fixtures synthétiques et tests
  uniquement) et sans fichier > 50 Mo — conforme à la politique de push ; le range check le couvre.
- L'arbre contient des **modifications étrangères non commitées** : `data/derived/MANIFEST.json`,
  `data/derived/d1_etf4/panel.parquet`, `data/derived/d2_us97/panel.parquet`,
  `results/data/d1_d2_profile.csv` (rebuild D1/D2 par une instance concurrente — différences au
  niveau BLAS, derniers ulps dans le profil, et octets parquet) ; `prompts/plans/plan-09.md` est non
  tracké (stream 09 en planification). **Ne jamais indexer ces fichiers ni `plan-09.md`.** Note : le
  fixture de `tests/test_data_d1_d2.py`, exécuté par `make check` dans `.venv`, rebuildera D1/D2 à
  l'identique des octets commités et écrasera ce rebuild étranger — si l'instance concurrente tient
  à son rebuild, elle doit le commiter ou le stasher avant.
- Fichiers du stream 04 modifiés par le plan (ajouts seulement) : `jepadrift/monitors/streams.py`,
  `jepadrift/monitors/eprocess.py`, `experiments/identity_articleB.py`,
  `tests/test_identity_articleB.py`, `docs/sections/monitors.md`, `logs/identity/*.log` — relire
  juste avant chaque édition. `tests/test_monitors.py` et `tests/test_injection.py` restent
  inchangés et au vert ; `results/identity/articleB_R01_R08.csv` est réécrit à l'identique
  (`git diff` vide attendu, vérifié en Tâche 9).

## Verdict

**GO.** Le plan est conforme au prompt 07 sur tous les points : registre
`PIPELINES[id] = (representation, stream_builder, detector, calibration)`, `run_pipeline` avec les
colonnes d'`alarms.csv` du prompt, P2-C avec les constantes de R15 (H_ref = 500, H_det = 750,
N_cal = 20 000, FPR 5 %) et la lecture anytime-valid ajoutée, ρ̂_signe et K_eff rapportés, identité
R15 pour K ∈ {5, 10, 20}, P3-C (dictionnaire d'e-détecteurs CUSUM, option mélange sous test
 d'indépendance), P3-D (q_t, δ = 0,5, Γ^op), P3-CS (a)/(b) selon le prompt item 6, P7 (oracle,
borne seulement), les trois calibrations dans `jepadrift/monitors/calibration.py` (le treillis exact
reste `lattice.select_threshold`), les tests du item 9 (FPR sous H₀ sur D6 dans l'IC binomial à
99 %, bootstrap P2-C à 5 % ± IC, détection F2 SR = 8), livrables, contraintes (monitors numpy seul,
représentations en tableaux, invariance au parallélisme). Revérification indépendante à la revue :
ρ̂ et K_eff recalculés depuis `load_d2` avec la composition figée de R15 — **bit-identiques** à
K = 5 et K = 20, **1 ulp** à K = 10 (2,14e-16 relatif), dans la porte de 1e-12 ; λ_boot et FPR_boot
lus dans le CSV de l'Article B cohérents. Sondes solides : contrôles D6 (tous les canaux dans la
région à 99 %), puissance F2 (100 % pour P3-C full, P3-CS (b), P7), bootstrap et randomisation
avec bruit de calibration, non-stationnarité de P3-D (Γ^op ≈ 191/2346 sur 2005–2019).

Le canal retenu est ce fichier (prompt destiné à l'instance), et non l'édition directe de
`~/.claude/plans/greedy-sparking-mist.md` : le plan appartient au workflow `superpowers:executing-plans`
de l'instance, la règle C-plan-recording fait enregistrer le plan final par l'instance dans
`prompts/plans/`, et la trace de décision reste dans le dépôt (précédents `GO-stream-03` à
`GO-stream-06`, commités avec leurs streams).

## Réponses aux quatorze hypothèses — les quatorze défauts sont CONFIRMÉS

- **H1 (convention de délai) — CONFIRMÉ** : `delay = alarm_index − tau_star + 1` (T_γ du Lemme 1,
  convention d'E2 et de `floors`) — seule convention comparable aux planchers.
- **H2 (lectures anytime-valid) — CONFIRMÉ** : e-détecteurs CUSUM pour P2-C, P3-C et P3-CS (b) ;
  e-processus de pari pour P3-CS (a) ; CUSUM du LLR à ln γ pour P7 — suit le prompt item par item.
- **H3 (cibles des tests sous H₀) — CONFIRMÉ** : chaque cible correspond à la garantie de sa
  lecture (exacte canal par canal vs niveau du treillis — test net du Lemme 2 sur D6 ; e-détecteurs à
  γ = 20H contre H/γ ; e-processus P3-CS (a) à γ = 20 contre 1/γ ; bootstrap/randomization avec la
  demi-largeur à n_cal finie) — sondes 4, 7 et 9 cohérentes.
- **H4 (bootstrap P2-C) — CONFIRMÉ** : fenêtres sur les lignes pré-surveillance (discipline pre-J4 ;
  R15 lisait le panel complet — écart documenté), `SeedSequence` par tirage, `composition_for` garde
  la graine MD5 de R15, signes bruts exacts pour la lecture anytime-valid.
- **H5 (données d'ajustement) — CONFIRMÉ** : `X_fit` fourni par l'appelant et sans dérive ;
  symétrisation indépendante de celle des réplications pour les contrôles D6 (W indépendant des
  signes surveillés → Lemme 2 exact) ; sonde 7 (seuil brut invalide sur D6) justifie cette
  indépendance ; le test bootstrap P2-C suit le protocole R15 (brut sur brut).
- **H6 (lecture exacte de P3-C) — CONFIRMÉ** : canal unique, CUSUM bilatéral strict δ = 0,1, règle
  `at_or_below`, `select_threshold(α, H)` ou `(1/γ, H=None)` ; pas d'exacte multi-canal (la
  dépendance entre canaux l'interdit).
- **H7 (option mélange de P3-C) — CONFIRMÉ** : `mixture_s2` fourni par l'appelant, test
  d'indépendance littéral (|ρ̂| < 3/√T sur toutes les paires résiduelles), `ValueError` en échec,
  combinaison pondérée marché/résiduel — fidèle au prompt. Sonde 3 : le test littéral échoue sur D2
  dans les deux modes → l'option lèvera `ValueError` sur D2, documenté.
- **H8 (P3-D) — CONFIRMÉ** : colonnes résiduelles seules ; fenêtres de longueur H de la calib
  énumérées sans tirage ; λ_iid par trajectoires i.i.d. (χ²_D − D)/√(2D) ; FPR à l'horizon H
  seulement ; H > calib → `ValueError`. Sonde 6 (Γ^op ≈ 191/2346 sur 2005–2019, régime 2008)
  justifie les fenêtres de calib par défaut.
- **H9 (P3-CS (a)) — CONFIRMÉ** : e-processus moyenne sur les mises ±`PIVOT_BETS` et les directions
  de Π(1 + λ s_{t,k}) ; CUSUM « design fixe » = max sur directions et côtés du CUSUM bilatéral δ = 0
  des pivots divisés par leur RMS de calib ; seuil par inversion de signe (B = 2000, un signe par
  jour commun à toutes les directions). Sonde 5 : alternatives à 35 %/17,5 % contre 100 %.
- **H10 (P3-CS (b)) — CONFIRMÉ** : σ̄ = médiane de ‖Px_t‖ sur la calib ; c_j = 2η₀_j·σ̄ ; σ̂
  redémarre de σ̄ au début de la surveillance puis moyenne exponentielle de demi-vie 20 ;
  λ_{t,j} = min(0,5 ; c_j/σ̂_{t|t−1}) ; e-détecteur CUSUM deux côtés sans nouveau code de moniteur ;
  (b) variante par défaut en anytime-valid. Fidèle au prompt item 6 ; le redémarrage à σ̄
  (statistique figée de la calib) est le choix non anticipant.
- **H11 (P7) — CONFIRMÉ** : Σ̂ = Ledoit–Wolf des lignes de calib de `X_fit` ; Δ_t lu dans le
  `delta` de l'enregistrement (découpé à τ*) ; reconstruction depuis `tau_star.json` reportée
  (B·direction ne redonne pas `direction_sha256` au bit près) ; seuil ln γ ; P7 rapporté comme borne
  seulement.
- **H12 (portages et périmètre de l'identité R15) — CONFIRMÉ** : identité étendue au-delà de ρ̂ et
  K_eff (λ_boot, FPR_boot avec les graines de R15 ; DetRate et ADD de la course à c = 0,25) ; dans
  les tests, partie sans aléa + λ_boot/FPR_boot à K = 5 ; le panel complet 2005–2025 ne sert qu'à
  la reproduction de l'Article B — discipline pre-J4 respectée (comme R01 au stream 04).
- **H13 (test F2) — CONFIRMÉ** : C synthétique constant sur SYM-D2, H = 2000, γ = 20, 50
  réplications ; 100 % exigé pour P3-C (full), P3-CS (b) (full) et P7 ; ≥ 90 % pour les deux
  lectures de P3-CS (a) (queue des délais à 1755/2000 — sonde 5) ; P2-C exclu (dérive de largeur,
  77 % — sonde 5).
- **H14 (hors périmètre et sorties) — CONFIRMÉ** : variante « rangs » de P3-CS reportée (pas de
  ‖Px‖ pour la mise de (b)) ; sorties de la CLI commitées sous `results/pipelines/` et
  `logs/pipelines/`.

## Points de vigilance (Review Focus) — endossés

1. **Absorption** : `state=None` + enregistrement injecté de τ* < fin de calib → `ValueError` ;
   tests et CLI ajustent sur un `X_fit` sans dérive.
2. **Anticipation** : perturber les lignes ≥ t ne change ni flux ni mises jusqu'à t ; les mises de
   P3-CS (b) ne lisent que les lignes < t.
3. **Ex æquo** : pièces par enregistrement sur clé ; 2864 zéros sur D2 avant 2020 traversés par le
   test nul de P2-C anytime-valid.
4. **Bornes de fenêtre** → `ValueError`, jamais de troncature silencieuse.
5. **Option mélange** : test d'indépendance en échec → `ValueError`, jamais de repli silencieux.

## Risques — endossés

Durée de `make check` (+60 s, couverte par l'empilement et la vectorisation) ; cibles faibles des
e-détecteurs (couvert par le test net canal par canal et l'ARL₀ laissé à E3) ; P3-D non stationnaire
(couvert par les fenêtres de calib, E1 tranchera pour H_det = 2000) ; queue des délais de P3-CS (a)
(seuil ≥ 90 %, puissance documentée) ; ρ̂ sensible au BLAS d'un ulp à K = 10 (porte relative 1e-12,
revérifié à la revue) ; modification des fichiers des streams 04/05 (ajouts seulement, tests
inchangés et au vert, R01 réécrit à l'identique) ; `n_jobs` > 1 (test d'invariance) ; hypothèse
renversée (choix isolés, changement local).
