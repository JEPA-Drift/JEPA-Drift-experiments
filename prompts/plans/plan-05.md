# Plan — Stream 05 : injections F1–F4, fonds D5 (Monte Carlo) et D6 (symétrisés)

> Exécution : Claude Code — `superpowers:executing-plans` en mode natif (tâches couplées par leurs interfaces), `superpowers:test-driven-development` par tâche, `superpowers:verification-before-completion` avant toute annonce de fin. Mistral Vibe (routage INDEX : Vibe, High) — mêmes tâches dans l'ordre, mêmes commandes. Cases `- [ ]` pour le suivi.

Date : 2026-10-16. Spécification : `prompts/streams/prompt-05-injections.md`. Base : HEAD `9a5d76b` (passe de correction du stream 04, après `b74ad6c` ; aucun fichier commun avec le stream 05 ; E2 est inchangé depuis `3e3a804`).

Statut : **GO** (revue `prompts/GO-stream-05.md`, 2026-10-16), intégré dans ce plan final (section « Décision GO intégrée »). Le plan avait été enregistré avant exécution (règle AGENTS.md, `C-plan-recording`).

**Objectif.** Livrer les fonds D5 et D6 et l'injecteur de dérives F1–F4 en espace des rendements, avec τ* exact et trace `tau_star.json`, sans modifier le hash d'E2.
**Architecture.** `jepadrift/sim.py` (générateurs D5, `Garch` d'E2 déplacé tel quel), `jepadrift/stats/covariance.py` (Ledoit–Wolf), `jepadrift/injection.py` (D6, estimations de calibration, `inject`, onset, JSON). numpy et scipy seulement.

## Décision GO intégrée

Source : `prompts/GO-stream-05.md` (verdict : GO). Intégration :

| Point de la revue | Intégration dans ce plan |
|---|---|
| Base du plan `b74ad6c` → `9a5d76b` | En-tête, « Concurrence » et Tâche 0 mis à jour |
| Retrait du `# noqa: E402` sur l'import d'E2 (inerte : pyflakes n'implémente pas E402 ; règle « aucun commentaire sauf `# ponytail:` » ; l'import modèle n'en porte pas) | Décision « Déplacement E2 » et Tâche 1 : ligne d'import sans commentaire |
| Hypothèses 1 à 5 confirmées (normalisation F2, convention (b), NaN de C_t, test SHA-256 d'E2, `nu=None`) | Marques (H) remplacées par (GO) ; aucun changement de contenu |
| Renforcement du test SHA-256 d'E2 : le hash dépend de numpy 2.4.4 et de la build BLAS | Tâche 1 : `test_e2_quick_sha256_unchanged` porte un `pytest.mark.skipif` hors environnement de référence (numpy 2.4.4, scipy 1.17.1, versions de `requirements.lock`) |
| Architecture confirmée (`jepadrift/stats/covariance.py`, `delta` renvoyé par `inject`) | Inchangé |
| Exécution en session unique, sans sous-agent | Inchangé ; revue finale en auto-revue (aucun sous-agent) |
| Chargeur commun de C_t reporté au premier consommateur (06 ou 12), dans `jepadrift/data_loader/` | Inchangé (pivot local au test) |
| F2 sur D2 : décision du stream 12 | Inchangé (signalé dans « Risques ») |
| Trace de décision | `prompts/GO-stream-05.md` commité avec le stream (Tâche 8) |

## Contexte

E1 et E3 (J2, 2026-10-25), puis E4–E7, E10 et E11, mesurent délais et fausses alarmes sur des dérives injectées à un τ* exact, sur fonds simulés (D5) ou réels symétrisés (D6). Les streams aval fixent les contrats suivants :
- **stream 07** (P7 oracle) : « w* = Σ̂⁻¹Δ, Δ connu par `tau_star.json` » → Δ et Σ̂ doivent être reconstructibles ;
- **stream 08** : `injection.py` n'accepte que des panels de rendements et refuse explicitement un objet Z ;
- **stream 12** (E1) : F1–F3 sur SYM-D2 et SYM-`d3_239`, conventions (a) et (b), 1000 onsets par cellule ;
- **stream 13** (E3) : D5 GARCH(0.08 ; 0.90) à innovations t₇ **et gaussiennes** ;
- **stream 19** (E4) : F2 à κ fixé, F3 à « SR de marché par titre = 1 » ;
- **stream 04** (commité en `b74ad6c`, corrigé en `9a5d76b`) : `tests/test_monitors.py` importe `Garch` depuis `experiments.e2_floor_validation`. Ce nom doit rester importable depuis E2 après le déplacement.

Concurrence. Le stream 04 a été commité et poussé (`b74ad6c`, puis `9a5d76b`) ; l'arbre ne contient plus que ce plan et le GO du stream 05. Si un autre stream (06, par exemple) travaille en parallèle dans le même arbre, les points de contact sont `docs/DEVIATIONS.md` (ajouts en fin de fichier) et `make check`, qui exécute toute la suite de tests de l'arbre (Tâche 0).

## Constats des sondes (lecture seule, sorties dans le scratchpad de session)

1. **E2 au HEAD** (`.venv` : numpy 2.4.4, scipy 1.17.1 ; un thread ; PYTHONHASHSEED=42). `--reps 2000` reproduit `e2_cells.csv` = `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` en 73.7 s, identique au fichier commité. `--quick --reps 50` donne `7828e1a3c6b013476174e64b407cff0d07561fb85f5839963e1ebaaac8daa1f9` (30 cellules, 24.7 s), identique en sous-processus et par appel de `main()` dans le processus. Le code de retour 1 est attendu : J1 échoue à 50 réplications.
2. **Code à déplacer** (E2 @ `3e3a804`), SHA-256 des segments source (`ast.get_source_segment`) :
   - `NU` (l.45) : `1cfff581049555d63312f5c5b1cf2fefadadde3fc5757a1e107ff9c91520cd90` ;
   - `T_SCALE` (l.46) : `5fe894e1d876ef61d969723fe7107956d099539c2b2f708c85365cbd896d1c5c` ;
   - `t_innov` (l.74–80) : `a50ac136f975c1b6f89023c2f6062ebdc02e2e0154e4af16be5e8bc3f021afdf` ;
   - `Garch` (l.83–104) : `38af3cecb70b5fddbf0dd6de15e33e4e888b02bca7136b1b9b1bbf85ffa0b74c`.

   `t_innov` n'est appelé que par `Garch`. `p_up`, qui reste dans E2, utilise `NU` et `T_SCALE`.
3. **Panels.** `d2_us97` (5154 × 97) : aucun NaN. `d3_239` (6738 × 239) : 0.01 % de NaN ; complet sur pretrain (lignes 1256–4024) et sur calib (lignes 4090–5030, soit 941 jours, 2016-04-07 → 2019-12-31). `d3_500` (6738 × 503) : 13 % de NaN ; titres complets : 383 sur pretrain, 464 sur calib.
4. **Caractéristiques `d3_239`.** 15 colonnes : `c_beta_252`, `c_vol_63`, `c_mom_12_1`, `c_rev_21` et 11 indicatrices GICS. Le pivot vers (T, N, P) prend 0.23 s. Là où le rendement est fini, des NaN subsistent sur 8 jours de pretrain, 24 jours de calib et 119 jours de surveillance (colonnes `c_beta_252`, `c_vol_63`, `c_mom_12_1`).
5. **Estimations sur la calib `d3_239`.** Ledoit–Wolf : δ̂ = 0.025. PC1 porte 25.9 % de la trace. Bord de Marčenko–Pastur sur la corrélation : 2.262, soit 11 valeurs propres au-dessus (PC1 compris). Avec K = 11, Ψ̂ ∈ [7.9e-6 ; 4.0e-4]. La version vectorisée de LW égale la formule en boucle (écart 0.0 sur 40 × 7).
6. **F2 sur données réelles** (K = 11, SR ∈ {0.5 ; 4}, 3 directions).
   - Une seule projection GLS donne max_t |BᵀΨ̂⁻¹Δ_t|_∞ ≤ 8.4e-15.
   - La normalisation, recalculée par Cholesky, vérifie |I − I_target| ≤ 7e-18.
   - L'information journalière ½Δ_tᵀΣ̂⁻¹Δ_t varie de −17 % à +26 % autour de sa moyenne de calibration.
   - La KL de la dérive moyenne vaut 73 à 95 % de la moyenne des KL journalières : les deux lectures possibles de « moyenne de calibration » diffèrent.
7. **Ordres de grandeur sur la calib `d3_239`.**
   - Convention (a) à SR = 1, RMS des Sharpe par titre : ≈ 0.34 pour F1 (K = 11, une direction) et 0.52 pour F3.
   - F4, déformation : KL par dimension d/2·(r − 1 − ln r) = 0.0134, 0.0473 et 0.1534 pour r = 1.25, 1.5 et 2, soit 6.8, 23.8 et 77.3 fois I(SR = 1). C'est cohérent avec la contingence C1 du plan v4 (« 24 à 77 fois »).
   - F4, rotation de Givens à θ = 15°, 30° et 45° : 0.0023, 0.0085 et 0.0170 nat entre PC2 et PC3 ; 0.097, 0.364 et 0.727 entre PC1 et PC2.
8. **Prototype `garch_panel`** (5000 × 239 en 0.08 s).
   - ρ = 0.40 : corrélation moyenne 0.403, variance 1.057.
   - Sans facteur, t₇ : variance 1.006, ACF(1) du carré moyen quotidien 0.21.
   - Sans facteur, gaussien : variance 0.997, ACF(1) 0.20.
9. **Graine.** `rng.bit_generator.seed_seq` (numpy 2.4.4) expose `entropy` et `spawn_key` : la graine d'une réplication se lit sur le générateur passé en argument.

## Décisions

(GO) marque une hypothèse d'interprétation confirmée par la revue GO (`prompts/GO-stream-05.md`).

| Question | Décision | Raison |
|---|---|---|
| Déplacement E2 | `NU`, `T_SCALE`, `t_innov` et `Garch` sont copiés octet par octet dans `jepadrift/sim.py`, par extraction `ast.get_source_segment` depuis `3e3a804`. E2 importe `from jepadrift.sim import NU, T_SCALE, Garch`, sans commentaire (GO : le `# noqa: E402` serait inerte, pyflakes n'implémentant pas E402) | Identité des octets et de l'AST (FAIR). `t_innov` n'est utilisé que par `Garch` : l'importer dans E2 créerait un import inutilisé, que pyflakes signale dans `make check` (écart `C-e2-sim`). `experiments.e2_floor_validation.Garch` reste importable pour le test du stream 04 |
| Test « SHA-256 d'E2 inchangé » | (GO) Le test appelle `main(["--quick", "--reps", "50", "--out", tmp])` et compare au hash épinglé `7828e1a3…` (≈ 25 s) ; il est sauté hors environnement de référence (numpy 2.4.4, scipy 1.17.1). Il est complété par l'identité des sources et des objets. Le run complet (73 s, `e315e537…`) reste la commande de vérification du prompt, avant et après le déplacement | Le run complet doublerait la durée de `make check`. Le mode rapide parcourt les quatre bras et `h0_sign_check` |
| `garch_panel` | (GO) Même récursion que `Garch` : σ_t² = ω + α·m_{t−1} + β·σ_{t−1}², avec ω = 1 − α − β, m = carré moyen transversal du jour, départ s² = 1 et m = 0, `burn=1000`. Innovations t_ν multivariées de variance unité (un χ²_ν commun par jour, comme `t_innov` en 2-D). `nu=None` donne des innovations gaussiennes. `factor_rho` donne z = √ρ·g·1 + √(1 − ρ)·u, de corrélation ρ | Précédent d'E2 (`Garch` avec dim > 1). E3 exige des innovations gaussiennes. Le χ² commun préserve le regroupement de volatilité quand N est grand |
| Ledoit–Wolf | `jepadrift/stats/covariance.py::ledoit_wolf(X) -> (sigma, shrinkage)` : données centrées, S = XᵀX/n, cible μI avec μ = tr S/N, δ̂ = min(b̄², d²)/d² [Ledoit & Wolf, 2004] | numpy seul, sans scikit-learn. Le module vit dans `stats/` et non dans `injection.py` : les représentations (streams 06 et 11) ne peuvent pas importer `jepadrift.injection` |
| Estimations de calibration | `fit_background(X_calib, K)` : Σ̂ = LW ; vecteurs propres triés par valeur propre décroissante, signe fixé par une somme ≥ 0 ; B = V_K Λ_K^{1/2} (facteurs de variance unité, K compte PC1) ; Ψ̂ = diag(Σ̂) − Σ_k B_ik² = diag(Σ̂ − BBᵀ) > 0 | (GO) Convention Σ_F = I du Corollaire 1. LW conserve les vecteurs propres de S. Le signe fixé rend les résultats indépendants de LAPACK |
| Projection F2 | `gls_residual(A, B, psi)` = A − B K⁻¹ BᵀΨ̂⁻¹A, avec K = BᵀΨ̂⁻¹B, vectorisé sur les lignes, en une passe | Corollaire 1 (Δα_⊥). Sonde 6 : 8e-15, très en deçà de 1e-10 |
| Normalisation de F2, convention (a) | (GO) ½·moyenne_{t ∈ calib}(Δ_tᵀΣ̂⁻¹Δ_t) = I_target, soit la moyenne des KL journalières, et non la KL de la dérive moyenne (écart `C-inject-F2-norm`) | Prop. « Latent delay floors » (c) : SR² = 252·E[Δμ_tᵀΣ_t⁻¹Δμ_t]. L'information s'additionne jour par jour (Lemme 1). Sonde 6 : les deux lectures diffèrent de 5 à 27 % |
| NaN de C_t (F2) | (GO) Un NaN se lit comme une exposition nulle (rang centré neutre 0). Le nombre d'entrées imputées est consigné dans `meta["c_nan_imputed"]`. ±inf → `ValueError` (écart `C-inject-F2-nan`) | Sonde 4 : 24 jours de calib touchés sur `d3_239`. Refuser les NaN rendrait F2 inutilisable sur D3 |
| Convention (b) | (GO) L'amplitude par titre est la RMS transversale des Sharpe annualisés √252·Δ_i/σ̂_i, avec σ̂_i² = Σ̂_ii (pour F2, RMS sur les titres et les jours de calib). Cible : `SR_ASSET_B = 1.0` pour F1 et F3, κ·`SR_ASSET_B` pour F2 (écart `C-inject-conv-b`) | Prompt 19 : « SR de marché par titre = 1 ». Sous le modèle équicorrélé du plan v4, cette définition redonne κ = dispersion / dérive de marché et le gain κ²(1 + (N − 1)ρ)/(1 − ρ) |
| Choix de la convention | `I_target` flottant > 0 → convention (a). `I_target=None` → convention (b) pour F1–F3. F4 exige `I_target=None` | Une seule source de vérité, sans clé redondante |
| F3 | b₁ = première colonne de V, de somme > 0 ; Δm > 0 | Translation de marché déterministe. Les fonds symétrisés et les détecteurs bilatéraux sont insensibles au signe |
| Directions aléatoires | Δλ ∈ R^K et Δγ ∈ R^P : gaussienne normalisée tirée sur `rng`, en un seul tirage par appel | Prompt (« direction aléatoire ») ; déterminisme par graine |
| Fenêtre et K | `params["calib"] = (start, stop)`, indices de lignes de `X`. `params["K"]` est explicite : 11 correspond au bord MP sur la calib `d3_239` | Le choix de K appartient à l'expérience (E1, E4) |
| Sortie d'`inject` | `(X_tilde, delta, meta)`. Pour F1–F3, `delta` est la dérive additive telle que `X_tilde[τ*:] = X[τ*:] + delta`, de forme (N,) pour F1 et F3, (T − τ*, N) pour F2. Pour F4, `delta` est la matrice M telle que `X_tilde[τ*:] = X[τ*:] @ M.T`. `meta` est un dict sérialisable en JSON | P7 (stream 07) consomme `delta` dans le processus ; `meta` alimente `tau_star.json` |
| `tau_star.json` | `write_tau_star(path, records)` écrit `json.dumps(records, indent=2, sort_keys=True) + "\n"`. Champs : `family`, `tau_star`, `convention`, `amplitude`, `seed` (`entropy` et `spawn_key` lus sur `rng.bit_generator.seed_seq`), `direction` (Δλ·s, Δγ·s ou [Δm] ; `null` pour F4), `direction_sha256` (SHA-256 des octets float64 de `delta`), `info`, `K`, `calib`, `shrinkage`, et `c_nan_imputed` pour F2 | Champs exigés par le prompt (item 6), plus ce qui permet de reconstruire Δ (P7). Écriture déterministe |
| Contrat d'entrée | `X` doit être un `np.ndarray` 2-D float64. `TypeError` sinon (dict, liste : objet Z) ; `ValueError` si la dimension ou le dtype est faux. `inject` exige X fini : sur `d3_500`, l'appelant sélectionne un sous-panel complet. `symmetrize` accepte les NaN | Stream 08. Validation à la frontière par exception, jamais par `assert` (inactif sous `-O`) |
| Commit | Unique, en fin de stream : `feat(injection): add D5 generators, D6 symmetrization and F1-F4 drift injection` | Convention des streams 03 et 04 |
| Langue | Anglais : code, docstrings, `docs/sections/injection.md`, wrapup, commit. Français : entrées de `docs/DEVIATIONS.md` et ce plan | Règles du projet (GO-04) |

## Contraintes globales

- numpy et scipy seulement. Aucune injection dans un espace latent. Les générateurs sont passés explicitement (`np.random.Generator`) ; jamais `np.random.seed`.
- Commandes avec OMP/MKL/OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE et PYTHONHASHSEED = 42. Python : `.venv/bin/python` (venv bâti sur Trading 3.12.9). `make` s'exécute après `source .venv/bin/activate`.
- Avant J4 (2026-11-08), aucune donnée de la fenêtre de surveillance (2020 et après) dans les tests ni dans la documentation. Les contrôles sur données réelles n'utilisent que les lignes 0 à 5030 de `d3_239` (jusqu'au 2019-12-31), et la calib (lignes 4090–5030) pour les estimations.
- Le code déplacé est copié tel quel, commentaires existants compris. Le code nouveau ne porte aucun commentaire, sauf `# ponytail:`, et des docstrings d'une ligne (contrat ou provenance). Aucune marque d'IA.
- `results/e2/e2_cells.csv` reste `e315e537…` : `make j1` avant et après le déplacement.
- Commit : Conventional Commits, sans trailer `Co-authored-by`. Indexation par chemins explicites, jamais `git add .` ni `-A` ; aucun `__pycache__`.

## Points de vigilance (Review Focus)

1. **Mutation de l'entrée.** E1 réutilise le même fond pour 1000 onsets : `inject` et `symmetrize` ne modifient jamais `X`. Test : `test_inputs_not_mutated` (tâches 3 et 4).
2. **NaN réels.** `symmetrize` conserve les NaN à leur place ; `inject` refuse un X non fini avec un message qui nomme le remède ; les NaN de C sont imputés et comptés. Tests aux tâches 3 et 4.
3. **Bornes de τ*.** τ* = 0 (tout le panel), τ* = T − 1 (dernière ligne seulement), bornes incluses de U[t₀ + H_ref, t_fin − H_det], intervalle vide → `ValueError`. Tests aux tâches 4 et 6.
4. **Import croisé.** `experiments.e2_floor_validation.Garch`, importé par le test du stream 04, doit rester le même objet que `jepadrift.sim.Garch`. Test : `test_e2_uses_moved_generator` (tâche 1). Les éditions d'E2 sont ordonnées pour que chaque état intermédiaire reste importable.
5. **Mise à l'échelle dégénérée.** Une direction sans information (C nul ou entièrement NaN, dérive dans le noyau de Σ̂⁻¹) déclenche une `ValueError` au lieu d'écrire inf ou NaN dans les rendements. Test : `test_degenerate_direction_rejected` (tâche 4).

## Fichiers

- **Créés** : `jepadrift/sim.py`, `jepadrift/injection.py`, `jepadrift/stats/covariance.py`, `tests/test_injection.py`, `docs/sections/injection.md`, `prompts/wrapups/wrapup-05.md`, et ce plan.
- **Modifiés** : `experiments/e2_floor_validation.py` (déplacement) ; `docs/DEVIATIONS.md` (quatre entrées en fin de fichier).
- **Non touchés** :
  - `Makefile` et `requirements.*` (numpy et scipy y figurent) ;
  - `jepadrift/data_loader/*` : le pivot de `chars.parquet` reste local au test, et un chargeur partagé de C_t relève du premier stream consommateur (06 ou 12) ;
  - `results/e2/*` et `logs/e2/run.log` : après `make j1`, seule la durée change, et ces fichiers sont restaurés.

---

### Tâche 0 — Préconditions
- [ ] Intégrer la revue GO dans ce fichier (section « Décision GO intégrée ») avant toute implémentation.
- [ ] `git log --oneline -3` et `git status --short` : HEAD attendu `9a5d76b` ou un descendant. Si des fichiers d'un autre stream restent non commités :
  - ne jamais les indexer ;
  - relire `docs/DEVIATIONS.md` juste avant de l'éditer ;
  - ne lancer que des tests ciblés pendant le travail ;
  - à la clôture, si `make check` échoue à cause d'un autre stream en cours : gel et signalement, aucun commit.
- [ ] Référence « avant » : `source .venv/bin/activate && make j1 && sha256sum results/e2/e2_cells.csv` → `e315e537ead0f656…`.

### Tâche 1 — Déplacement vers `jepadrift/sim.py`

**Interfaces.** Produit : `jepadrift.sim.{NU, T_SCALE, t_innov, Garch}`, inchangés. E2 importe `NU`, `T_SCALE` et `Garch`.

- [ ] Créer `tests/test_injection.py` : docstring `"""Tests for jepadrift.sim, jepadrift.injection and jepadrift.stats.covariance (pytest)."""`, helper `_rng(*key) = np.random.default_rng(np.random.SeedSequence([5, *key]))`. Premiers tests :
  - `test_e2_uses_moved_generator` : `e2.Garch is sim.Garch`, `e2.NU is sim.NU`, `e2.T_SCALE is sim.T_SCALE` ; le SHA-256 de `ast.get_source_segment` pour `NU`, `T_SCALE`, `t_innov` et `Garch` dans `jepadrift/sim.py` égale les quatre valeurs du constat 2 ;
  - `test_e2_quick_sha256_unchanged` : `e2.main(["--quick", "--reps", "50", "--out", str(tmp_path)])`, code de retour ignoré ; le SHA-256 de `tmp_path / "e2_cells.csv"` vaut `7828e1a3c6b013476174e64b407cff0d07561fb85f5839963e1ebaaac8daa1f9`. Garde GO : `pytest.mark.skipif((np.__version__, scipy.__version__) != ("2.4.4", "1.17.1"), reason=...)`.
- [ ] `pytest -q tests/test_injection.py` → échec attendu (module `jepadrift.sim` absent).
- [ ] Créer `jepadrift/sim.py` : docstring d'une ligne, `import math`, `import numpy as np`, puis les quatre segments extraits par programme de `git show 3e3a804:experiments/e2_floor_validation.py`, dans l'ordre `NU`, `T_SCALE`, `t_innov`, `Garch`, séparés par deux lignes vides.
- [ ] Éditer E2 dans cet ordre, chaque état restant importable : (1) ajouter `from jepadrift.sim import NU, T_SCALE, Garch`, sans commentaire, sous `from jepadrift import floors as fl` ; (2) supprimer les définitions de `t_innov` et de `Garch` ; (3) supprimer `NU = 7` et `T_SCALE = …`. Conserver `import math` et `from scipy import stats`, encore utilisés.
- [ ] `pyflakes jepadrift/sim.py experiments/e2_floor_validation.py` → aucun signalement. `pytest -q tests/test_injection.py` → succès.
- [ ] `make j1 && sha256sum results/e2/e2_cells.csv` → `e315e537…`. Puis `git diff results/e2 logs/e2` : si seule la durée diffère, `git checkout -- results/e2/e2_j1_summary.txt logs/e2/run.log`. Tout autre écart : arrêt (D3), sans retouche destinée à forcer la convergence.

### Tâche 2 — Générateurs D5

**Interfaces.** Produit :
- `gaussian_latent(T, D, rng) -> ndarray (T, D)`, soit `rng.standard_normal((T, D))` ;
- `garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None, burn=1000) -> ndarray (T, N)`, selon la décision « `garch_panel` ». `ValueError` si α < 0, β < 0, α + β ≥ 1, ν ≤ 2 (ν renseigné) ou ρ ∉ [0, 1). Boucle sur `burn + T` pas, vectorisée sur N, avec `# ponytail: one panel per call, add a replicate axis if E3's many-path loops dominate runtime`.

- [ ] Tests :
  - `test_garch_panel_moments` : T = 20 000, N = 50, (α, β) = (0.08, 0.90), ν = 7, ρ = 0.40 → |variance − 1| < 0.15 et corrélation moyenne hors diagonale ∈ [0.37 ; 0.43]. Sans facteur : ACF(1) du carré moyen quotidien > 0.05. Avec ν = None et N = 1 : forme (T, 1), sortie finie. Paramètres invalides → `ValueError` ;
  - `test_generators_deterministic` : même graine → `gaussian_latent` et `garch_panel` identiques octet par octet.
- [ ] Échec attendu → implémentation → succès.

### Tâche 3 — Covariance, estimations de calibration, D6, contrôles d'entrée

**Interfaces.** Produit :
- `jepadrift.stats.covariance.ledoit_wolf(X) -> (sigma (N, N), shrinkage: float)` ;
- `jepadrift.injection.symmetrize(X, rng) -> (X_sym, eps)` : `eps = rng.choice((-1.0, 1.0), size=T)` (idiome de `Garch.draw`) ; `X_sym = X * eps[:, None]`, nouveau tableau ;
- `fit_background(X_calib, K) -> dict` avec les clés `sigma`, `shrinkage`, `eigval`, `eigvec`, `B`, `psi`. `ValueError` si K ∉ [1, N − 1] ou si min Ψ̂ ≤ 0 ;
- `gls_residual(A, B, psi) -> ndarray`, de la forme de A ((N,) ou (T, N)) ;
- `_check_panel(X, finite)`, privé : `TypeError` ou `ValueError` selon la décision « Contrat d'entrée ».

- [ ] Tests :
  - `test_ledoit_wolf_matches_formula` : X de 40 × 7 tiré de `_rng(3)`, comparé à une référence en boucle Σ_t ‖x_t x_tᵀ − S‖²_F / n² : écart max ≤ 1e-12. δ̂ ∈ [0, 1] ; sigma symétrique et factorisable par Cholesky. Sur 4000 × 5 gaussien : δ̂ < 0.05 ;
  - `test_gls_residual_matches_corollary` : B (30 × 3), Ψ̂ > 0 et a ∈ R³⁰ aléatoires ; r = `gls_residual(a, B, psi)`. Vérifier |BᵀΨ̂⁻¹r|_∞ ≤ 1e-12·|BᵀΨ̂⁻¹a|_∞, et rᵀΨ̂⁻¹r = `floors.factor_information(B, np.eye(3), psi, np.zeros(3), a)[1]` à 1e-12 en relatif. Une entrée (T, N) est traitée ligne par ligne ;
  - `test_fit_background_conventions` (calib `d3_239`, K = 11) : valeurs propres décroissantes ; chaque vecteur propre de somme ≥ 0 ; B = V[:, :11]·√λ ; Ψ̂ > 0 ;
  - `test_symmetrize_abs_bitwise_one_sign_per_day` (prompt). Entrée : lignes 0–5030 de `d3_239`, copie où quelques entrées valent NaN et −0.0. Vérifier :
    - `np.abs(X_sym).view(np.uint64) == np.abs(X).view(np.uint64)` partout ;
    - eps ∈ {−1, 1} ;
    - chaque jour, sign(X_sym·X) sur les entrées finies non nulles vaut {eps_t} ;
    - NaN aux mêmes positions ;
    - |moyenne(eps)| < 4/√T ;
  - `test_inputs_rejected` : `{"z_odd": Z}` (sortie de type `transform_day`, prompt 06) et liste → `TypeError` ; float32 et 1-D → `ValueError` ;
  - `test_inputs_not_mutated`, partie D6 : copie de X avant `symmetrize`, égalité octet par octet après.
- [ ] Échec attendu → implémentation → succès.

### Tâche 4 — `inject` : F1, F2, F3 et conventions d'amplitude

**Interfaces.** Consomme la tâche 3. Produit :
- `inject(X, family, tau_star, I_target, params, rng) -> (X_tilde, delta, meta)` ;
- `FAMILIES = ("F1", "F2", "F3", "F4-deform", "F4-rotate")` ;
- `SR_ASSET_B = 1.0`.

Clés de `params` : `calib` (toutes familles) ; `K` (F1, F2) ; `C`, tableau (T, N, P) float64 (F2) ; `kappa` (F2 en convention (b)).

Algorithme pour F1–F3 :
1. Valider X (fini), la famille, 0 ≤ τ* < T, `calib`, la présence de `K` (F1, F2), puis `I_target` (> 0, ou `None`) et `C` (forme (T, N, P), sans ±inf).
2. `fit = fit_background(X[start:stop], params.get("K", 1))`.
3. Direction brute :
   - F1 : `D = B @ u`, avec u unitaire tiré sur `rng` ;
   - F2 : `D = gls_residual(np.where(np.isnan(C), 0.0, C) @ g, B, psi)` sur toutes les lignes, avec g unitaire tiré sur `rng` ;
   - F3 : `D = eigvec[:, 0] * sqrt(eigval[0])`.
4. Référence : `D_ref = D[start:stop]` pour F2, `D` sinon. q = ½·moyenne des formes D_refᵀΣ̂⁻¹D_ref (`np.linalg.solve`). `ValueError` si q n'est pas strictement positif.
5. Échelle :
   - convention (a) : s = √(I_target/q) ;
   - convention (b) : s = cible / RMS(√252·D_ref/σ̂), avec cible = `SR_ASSET_B`·(κ pour F2, 1 sinon) et 252 = `floors.TRADING_DAYS`.
6. `delta = s * D[τ*:]` pour F2, `s * D` sinon ; `X_tilde = X.copy()` ; `X_tilde[τ*:] += delta`.
7. `meta` reprend les champs de la décision « `tau_star.json` », avec `info` = ½·moyenne des formes (s·D_ref)ᵀΣ̂⁻¹(s·D_ref).

- [ ] Tests :
  - `test_f2_orthogonal_to_loadings` (prompt). Deux fonds, puis B et Ψ̂ recalculés par `fit_background` sur la même fenêtre ; critère max_t |BᵀΨ̂⁻¹Δ_t|_∞ < 1e-10 :
    - calib `d3_239` : X = lignes 4090–5030, `calib=(0, 941)`, τ* = 600, K = 11, C = pivot local de `sp500.load_chars("d3_239")` sur les mêmes lignes ;
    - synthétique : `garch_panel` × 0.01, C uniforme sur [−0.5 ; 0.5] avec P = 4 ;
  - `test_information_target` (prompt) : F1, F2 et F3, SR ∈ {0.5 ; 4}, I_target = `floors.kl_from_sharpe(SR)`. ½ΔᵀΣ̂⁻¹Δ est recalculé par `scipy.linalg.cho_factor`/`cho_solve`. Pour F2, la moyenne porte sur les lignes de calib, avec Δ_t reconstruit par `gls_residual(C_t @ meta["direction"])`. Critères : |I − I_target| ≤ 1e-10 et ≤ 1e-12·I_target ; même contrôle pour `meta["info"]`. Pour F1, `B @ meta["direction"]` égale `delta` à 1e-13 près en relatif ;
  - `test_no_change_before_tau_star` (prompt) : chaque famille, τ* ∈ {0, 600, T − 1}. `X_tilde[:τ*]` est identique octet par octet à `X[:τ*]` ; `X_tilde[τ*:]` égale exactement `X[τ*:] + delta` ; au moins une entrée est modifiée ;
  - `test_convention_b_per_asset_amplitude` : RMS des Sharpe par titre = 1 à 1e-12 pour F1 et F3, = κ à 1e-12 pour F2 avec κ ∈ {0.25 ; 0.5 ; 1} ; `meta["convention"] == "b"` ;
  - `test_f2_nan_characteristics_imputed` : 5 NaN placés dans C donnent la même sortie que 0 aux mêmes positions, et `meta["c_nan_imputed"] == 5` ;
  - `test_degenerate_direction_rejected` : F2 avec C entièrement NaN → `ValueError` ;
  - `test_inject_arguments_rejected` → `ValueError` pour : X avec NaN, famille inconnue, τ* ∈ {−1, T}, F1 ou F2 sans `K`, F2 sans C ou avec un C de mauvaise forme, F2 en convention (b) sans `kappa`, I_target ≤ 0 ;
  - `test_inputs_not_mutated`, partie inject ;
  - `test_determinism` (prompt) : même graine → `X_tilde`, `delta` et `json.dumps(meta, sort_keys=True)` identiques ; graine différente → direction différente pour F1 et F2.
- [ ] Échec attendu → implémentation → succès.

### Tâche 5 — `inject` : F4

**Interfaces.** `I_target` vaut `None`.
- **Déformation** (`F4-deform`), paramètres `subspace` (indices de vecteurs propres, 0 = PC1) et `r` > 0 :
  - M = I + (√r − 1)·V_S V_Sᵀ ;
  - info = ½[tr(Σ̂⁻¹MΣ̂M) − N − 2 ln det M], soit d/2·(r − 1 − ln r) quand S est engendré par des vecteurs propres.
- **Rotation** (`F4-rotate`), paramètres `pair` (i, j) et `theta_deg` :
  - u = v_i, w = v_j, G = I + (cos θ − 1)(uuᵀ + wwᵀ) + sin θ·(wuᵀ − uwᵀ) ;
  - info = ½[tr(Σ̂⁻¹GΣ̂Gᵀ) − N] = ½ sin²θ (λ_i − λ_j)²/(λ_iλ_j).
- Dans les deux cas : `X_tilde[τ*:] = X[τ*:] @ M.T` ; `delta = M` ; `meta["direction"] = None` ; `amplitude` = {r, subspace} ou {theta_deg, pair}.

- [ ] `test_f4_deformation_and_rotation` (calib `d3_239`) :
  - déformation, r ∈ {1.25 ; 1.5 ; 2}, S = {1} puis {1, 2} : M V_S = √r V_S et M v = v pour tout vecteur propre v hors de S (1e-12) ; info = d/2·(r − 1 − ln r) à 1e-10 en relatif ;
  - rotation, θ ∈ {15°, 30°, 45°}, paire (1, 2) : GGᵀ = I (1e-12), det G = 1, Gu = cos θ·u + sin θ·w ; info égale à la formule fermée à 1e-10 en relatif.
- [ ] Étendre à F4 les tests de la tâche 4 (rien avant τ*, déterminisme, non-mutation). I_target non nul → `ValueError`.
- [ ] Échec attendu → implémentation → succès.

### Tâche 6 — Onset et `tau_star.json`

**Interfaces.**
- `draw_tau_star(t0, t_end, h_ref, h_det, rng) -> int` : `rng.integers(t0 + h_ref, t_end - h_det + 1)` ; `ValueError` si l'intervalle est vide.
- `write_tau_star(path, records) -> None`, avec un dict ou une liste de dicts.

- [ ] Tests :
  - `test_draw_tau_star_bounds` : (t0, t_end, h_ref, h_det) = (0, 10, 3, 4) → 2000 tirages couvrent exactement {3, 4, 5, 6} ; (0, 10, 6, 5) → `ValueError` ;
  - `test_tau_star_json_roundtrip`, sur des records de F1 et de F4 :
    - relecture par `json.loads` égale aux records, et deux écritures donnent les mêmes octets ;
    - clés présentes : `family`, `tau_star`, `convention`, `amplitude`, `seed`, `direction_sha256` ;
    - `direction_sha256` = SHA-256 de `np.ascontiguousarray(delta, dtype=np.float64).tobytes()` ;
    - `seed` = `{"entropy": [5, …], "spawn_key": []}` pour un générateur `_rng(…)`.
- [ ] Échec attendu → implémentation → succès.

### Tâche 7 — Documentation et écarts
- [ ] Rédiger `docs/sections/injection.md` en anglais. Il sert de base à l'Annexe B : ses tableaux restent en Markdown simple, pour être lus plus tard par `tools/appendix_b.py` (stream 21). Contenu :
  - API des trois modules et contrat d'entrée (panels de rendements seulement, refus des objets Z) ;
  - D5 : `gaussian_latent`, récursion et innovations de `garch_panel`, `Garch` d'E2 déplacé tel quel avec son hash E2 ;
  - D6 : formule, propriétés (|x|, corrélations et volatilité conservées ; dérive de localisation et levier effacés), lien avec le Lemme 2 ;
  - estimations de calibration : LW, B, Ψ̂, convention de signe ;
  - table des familles : formule, paramètres, grilles (SR ∈ {0.5 ; 1 ; 2 ; 4}, κ ∈ {0.25 ; 0.5 ; 1}, r ∈ {1.25 ; 1.5 ; 2}, θ ∈ {15°, 30°, 45°}), information gaussienne ;
  - conventions (a) et (b), onset, schéma de `tau_star.json`, correspondance entre tests et garanties ;
  - valeurs analytiques seulement (KL de déformation par dimension) : aucun chiffre tiré des données, faute de CSV et de script traçables ;
  - références : [Ledoit & Wolf, 2004], [Kelly, Pruitt & Su, 2019] pour F2, et l'Article C (Corollaire 1, Lemme 2, Prop. « Latent delay floors »).
- [ ] `docs/DEVIATIONS.md` : relire juste avant l'édition, puis ajouter en fin de fichier, en français, `C-e2-sim`, `C-inject-F2-norm`, `C-inject-F2-nan` et `C-inject-conv-b`, en citant les constats de ce plan.

### Tâche 8 — Clôture (ordre AGENTS.md)
- [ ] Vérifications :
  - `pytest -q tests/test_injection.py` ;
  - `make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16` → `e315e537ead0f656`, puis restauration des fichiers de durée ;
  - `source .venv/bin/activate && make check`. En cas d'échec : diagnostic, 3 tentatives au plus. Un échec imputable à un autre stream en cours entraîne gel et signalement, sans commit ;
  - `git diff data/derived/MANIFEST.json` vide.
- [ ] (1) Skill `wrap-up` → `prompts/wrapups/wrapup-05.md`.
- [ ] (2) `tools/reindex_graphify_jcodemunch.sh`.
- [ ] (3) `make check`, puis commit unique sans trailer :
  - indexer explicitement les fichiers créés et modifiés listés plus haut, `prompts/plans/plan-05.md`, `prompts/wrapups/wrapup-05.md`, et le fichier GO du stream 05 s'il existe ;
  - `git diff --staged` : aucun fichier d'un autre stream, aucun `__pycache__`, aucun chemin absolu du répertoire personnel, aucun fichier > 50 Mo.
- [ ] (4) Plage `origin/main..HEAD` : aucun chemin sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo. Puis `git push origin main` ; rapporter le hash et l'état propre de l'arbre.

## Vérification de bout en bout

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16   # e315e537ead0f656
pytest -q tests/test_injection.py
make check
```

## Risques

| Risque | Parade |
|---|---|
| Hash d'E2 modifié | Copie octet par octet et test d'identité des sources. Tout écart entraîne l'arrêt (D3), sans retouche destinée à forcer la convergence |
| `make check` rouge à cause d'un autre stream en cours (tests en phase rouge, ajouts concurrents à DEVIATIONS) | Tests ciblés pendant le travail. À la clôture : gel et signalement, aucun commit |
| Une hypothèse (GO) à réviser plus tard | Chacune est isolée dans une fonction ou une constante (`SR_ASSET_B`, normalisation de F2, imputation de C) : le changement reste local |
| Durée de la suite | `test_e2_quick_sha256_unchanged` ≈ 25 s ; le reste < 10 s |
| `garch_panel` pour E3 (2000 trajectoires univariées) | Un appel par trajectoire (≈ 6000 pas Python). Si la durée l'exige, E3 ajoutera un axe de réplication (plafond marqué `# ponytail:`) |
| F2 sur D2 | D2 n'a pas de caractéristiques. E1 (stream 12) devra les calculer depuis les rendements ou réserver F2 à D3. Hors périmètre, signalé |
