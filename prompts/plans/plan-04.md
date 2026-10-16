# Plan — Stream 04 : surveillance (1/3), noyau univarié, treillis exact, e-détecteurs, portage de l'Article B

> Exécution : `superpowers:executing-plans` en mode natif (dans cette session, sans sous-agent : tâches couplées par leurs interfaces, sous-agents non demandés), `superpowers:test-driven-development` par tâche, `superpowers:verification-before-completion` avant toute annonce de fin. Cases `- [ ]` pour le suivi.

Date : 2026-10-16. Spécification : `prompts/streams/prompt-04-monitors-core.md`. Code de référence : `~/The-Whitening-Advantage-Experiments` @ `a05f0d9` (lecture seule, propre).

Statut : **GO avec amendements** (revue `prompts/GO-stream-04.md`, 2026-10-16), intégrés dans ce plan final (section « Décision GO intégrée »). Ce fichier remplace la copie à l'identique enregistrée à la Tâche 0 ; le fichier de travail `~/.claude/plans/magical-sleeping-piglet.md` n'est pas la référence.

## Contexte

`jepadrift/monitors/` et `jepadrift/stats/` sont vides. Cette bibliothèque est le socle de tous les pipelines : les streams 07, 12 et 13 en dépendent, et elle bloque J2 (2026-10-25). Le stream doit (i) porter à l'identité les moniteurs de l'Article B et prouver cette identité sur les sorties R01 et R08, (ii) fournir les détecteurs exacts de l'Article C : loi exacte du treillis, flux de signe exact, Γ, e-processus et e-détecteurs.

Le stream 03 est terminé et commité (`3e3a804`, 2026-10-16 15:22). Au HEAD, le `Makefile` contient `pytest -q --ignore=external`, `docs/DEVIATIONS.md` les entrées C-D3-*, `jepadrift/data_loader/articleB.py` la fusion du manifeste, et `requirements.*` yfinance et pyyaml ; `make check` y est vert à 42 tests (constat de la revue GO). Aucune modification non commitée d'un autre stream ne subsiste : l'arbre de travail ne contient que les fichiers du stream 04 et des `__pycache__`.

## Décision GO intégrée (2026-10-16)

Source : `prompts/GO-stream-04.md` (verdict : GO avec amendements). Intégration :

| Point de la revue | Intégration dans ce plan |
|---|---|
| Amendement 1 — contexte périmé | Section « Contexte » réécrite (stream 03 commité, arbre propre, `make check` vert à 42 tests) |
| Amendement 2 — Tâche 4, `Makefile` déjà appliqué et conforme | Tâche 4 : ne pas revenir sur le hunk ; le vérifier tel quel dans `git diff --staged` à la Tâche 11 |
| Amendement 3 — Tâche 11 simplifiée | Plus d'indexation partielle (aucun hunk étranger) ; garde « Read juste avant chaque Edit » conservée ; `make check` part d'un état vert : tout échec est investigué, non attribué au stream 03 ; gel et signalement maintenus pour un échec externe en cours de stream |
| Amendement 4 — Tâche 0 | Plan final mis à jour (ce fichier), et non copie à l'identique |
| Recommandation 5 — marge du contrôle des e-détecteurs | Tâches 6 et 10 : 2000 trajectoires conservées, marges mesurées documentées dans `docs/sections/monitors.md` ; échec lié à la plateforme → écart consigné, 3 tentatives au plus, puis gel et alerte |
| Recommandation 6 — taille des artefacts commités | Tâche 11 : aucun fichier indexé > 50 Mo, aucun horodatage dans les journaux commités, aucun chemin absolu du répertoire personnel (substitution `~`) |
| Recommandation 7 — hors périmètre | `docs/MAPPING.md` non créé ; `prompts/streams/INDEX.md` inchangé |
| Trace de décision | `prompts/GO-stream-04.md` commité avec le stream (précédent : `GO-stream-03.md` dans `3e3a804`) |

État à l'intégration : tâches 0 à 5 terminées (registre `.superpowers/sdd/plan-04/progress.md`, 16 tests verts) ; tâche 6 en cours (tests écrits, échec initial constaté, module `eprocess.py` à écrire). Points endossés tels quels par la revue : portage octet par octet et test d'identité de source, `C-garch-pyflakes`, `C-lattice-midpoint` (utilisé par P1-C/C et la Tâche 7 via `sel["threshold"]`), exception `articleB_csv` (`C-R01-parse`), second environnement (`C-R01-env`), liste blanche d'imports, configurations P1, e-processus en log, recette de clôture et conventions de langue.

## Constats des sondes (lecture seule, menées pendant la planification)

1. **Réplication R01 prototypée** (phases 1 à 3), dans `.venv` (numpy 2.4.4, pandas 3.0.6, scipy 1.17.1, statsmodels 0.15.0) et dans l'environnement conda `Trading` (numpy 1.26.4, pandas 2.3.2, scipy 1.16.2, statsmodels 0.14.5, soit les versions de l'Article B).
   - **Entrée D1** (`load_d1`) : sont bit-identiques α, β, Γ̂, q̂, `n_days`, les alarmes 2020 (aucune), les taux, les IC de Wilson, ADD, SEM, les médianes et `S_over_thr_Concept`. Écarts relatifs : ω ≤ 2.6e-14, σ_unc ≤ 1.3e-14, `S_over_thr_Data` ≤ 2.0e-14.
   - **Entrée « lecteur R01 »** (CSV dérivés de B lus comme à R01 l.249) : toutes les cellules sont bit-identiques dans l'env Article B. Dans `.venv`, seule `lb_pvalue_warmup` diffère (4.6e-15 en relatif).
   - **Cause des écarts de 1e-14** : R01 lit ses CSV avec le convertisseur flottant par défaut de pandas, D1 avec `round_trip`. Ces deux lectures diffèrent sur 6258 des 6414 rendements SPY, jusqu'à 7356 ulp, sous pandas 2.3.2 comme sous 3.0.6.
2. **Treillis.** Un DP générique sur la chaîne absorbante (S⁺, S⁻) généralise `lattice_exceedance_exact` (R08 l.521–549). Il reproduit les 16 lignes `exact_survival` avec un écart relatif maximal de 9.7e-15 et les 16 lignes `enumeration_validation` à l'identique. Coût : 0.16 s par niveau bilatéral à H = 5000.
3. **ARL₀ exact** par résolution dense de (I − Q)t = 1. Il concorde avec le Monte Carlo (L = 10 : 61.51 en unilatéral, 30.75 en bilatéral) et prend 0.7 s à L = 57 en bilatéral.
4. **e-détecteurs** moyennés sur 8 mises, sur pièces équitables, 2000 trajectoires : ARL₀ SR = 21.7 à γ = 20 et 110.3 à γ = 100 ; ARL₀ CUSUM ≥ 521 et ≥ 2778 (bornes censurées).
5. **pyflakes** signale R01 l.99 (`except … as e`, variable inutilisée). Le portage verbatim de `fit_garch_qmle` ferait donc échouer `make check`.

## Décisions

| Question | Décision | Raison |
|---|---|---|
| Portage « sans modification » | Copie octet par octet par extraction `ast.get_source_segment`, puis test d'identité de source contre le dépôt B | Identité AST et octets (prompt, FAIR) |
| pyflakes sur `garch.py` | Exclure ce seul fichier de la ligne pyflakes de `make check`, écart `C-garch-pyflakes` | Seule alternative : modifier la fonction portée |
| Seuil flottant du treillis | `select_threshold` renvoie le point du treillis `lam = L·u` et le seuil opérationnel `threshold = (L + ½)·u` (strict) ou `(L − ½)·u` (large), à utiliser avec `S > threshold` en flottant ; écart `C-lattice-midpoint` | Au point du treillis, l'accumulation flottante change `>` en `≥` (écart B `R08-delivered-level-above-nominal`) |
| ARL₀ exact | Résolution dense sur (L+1)^sided états, garde n ≤ 10 000 avec commentaire `# ponytail:` | L ≤ 99 couvre γ ≤ 10⁵ |
| Entrée des e-processus | x ∈ [−1, 1], facteur 1 + λx ; flux de signe exact : x = 2s ; mises λ = 2·côté·η₀ (= 2(½ ± η₀) de R09) ; sorties en log | Prop. 3 (2b − 1), R09, pas de débordement |
| Identité R01 | `experiments/identity_articleB.py` transcrit les phases 1 à 3 de R01 avec les primitives portées et les constantes P1. Entrée `d1_loader` : contrôle bloquant. Entrée `articleB_csv` : diagnostic d'attribution | Prompt (« chargeur du prompt 2 ») et attribution des écarts |
| Critère d'identité | Cellule non flottante : égalité exacte. Cellule flottante : bit-identique ou écart relatif ≤ 1e-12. NaN = NaN | 1e-12 est le critère R08 du prompt ; un écart discret (α arrondi à 1e-6, délai entier) dépasse toujours 1e-12 |
| Second environnement | `external/articleB-venv` créé depuis `~/miniforge3/envs/Trading/bin/python` (3.12.9) : `pip install -r` des requirements de B, plus `pyyaml` pour importer le chargeur D1 | Commande du prompt ; pyyaml n'a aucun rôle numérique (consigné dans `C-R01-env`) |
| CSV d'identité | Un seul fichier, colonnes `env,input,source,row,column,reference,reproduced,rel_diff,bit_identical,pass`. Chaque exécution remplace les lignes de son `env` (`venv` ou `articleB-venv`) | Un livrable, deux environnements |
| Écriture CSV | `save_fair_csv`, port verbatim de `experiments/common/fair_harness.py` l.84–88, défini localement dans le script | Règle FAIR ; un seul appelant |
| Fichiers partagés (`Makefile`, `docs/DEVIATIONS.md`) | Read juste avant chaque Edit ; aucun hunk étranger non commité (stream 03 commité en `3e3a804`), donc indexation normale par chemins explicites | Amendement 3 de la revue GO |
| Langue | Anglais : code, docstrings, `docs/sections/monitors.md`, wrapup, commit. Français : entrées de `docs/DEVIATIONS.md` (convention du fichier) et ce plan | Règles du projet |

## Contraintes globales

- `jepadrift/monitors/` : numpy et bibliothèque standard seulement. Aucun générateur aléatoire interne : le `rng` est toujours passé explicitement. Calculs vectorisés en float64. Constantes de l'Article B inchangées : δ = 0.1 et λ = 10 ; δ = 0.5 et λ = 65·Γ̂ ; MIX = 16 départs × {0.05, 0.10, 0.15} × ±1, poids 1/96, H = 5000.
- Dans tout script, avant `import numpy` : OMP/MKL/OPENBLAS_NUM_THREADS = 1 et MKL_CBWR = COMPATIBLE. Commandes lancées avec `PYTHONHASHSEED=42`. Aléa uniquement par `np.random.SeedSequence`, jamais `np.random.seed`.
- Lectures CSV avec `float_precision='round_trip'`. Seule exception : l'entrée diagnostique `articleB_csv`, qui reproduit délibérément le lecteur de R01 (l.249).
- Scripts : argparse et `if __name__ == "__main__":` ; journaux dans `logs/identity/`, CSV dans `results/identity/`. Aucun chemin absolu du répertoire personnel dans les artefacts (substitution par `~`) ; aucun horodatage dans les journaux commités.
- Aucun commentaire sauf `# ponytail:`. Docstrings d'une ligne (provenance « fichier l.a–b » ou contrat d'usage). Aucune marque d'IA.
- Python : `.venv/bin/python` (venv bâti sur Trading 3.12.9). `make` s'exécute après `source .venv/bin/activate`, car il est absent du PATH système.
- Commit : Conventional Commits, sans trailer `Co-authored-by` (le CLAUDE.md utilisateur prime). Indexation par chemins explicites, jamais `git add .` ni `-A`.

## Points de vigilance (Review Focus)

1. **Comparaison flottante au point du treillis** (`S > λ` avec λ = L·u accumulé) → test `test_midpoint_threshold_reproduces_lattice_rule` (tâche 3).
2. **NaN dans les flux.** D1 contient des NaN hors série. En Python, `max(0.0, nan)` vaut 0.0, alors que `np.maximum` propage le NaN → `ValueError` dans les flux et dans les versions vectorisées ; tests aux tâches 1 et 2.
3. **Débordement des e-détecteurs** sous dérive forte (1.4ⁿ) → calcul en log ; test `test_edetector_strong_drift_finite` (tâche 6).
4. **δ flottant** (0.1 n'est pas exact en binaire) → pas du treillis calculé par `Fraction(repr(δ))`. Si δ est trop fin, l'espace d'états explose → `ValueError` ; tests à la tâche 3.
5. **Γ^op inatteignable** (trajectoires trop courtes pour l'ARL₀ visé) → `ValueError` ; test à la tâche 5.

## Fichiers

- **Créés** : `jepadrift/monitors/{cusum,lattice,streams,gamma,eprocess}.py`, `jepadrift/stats/garch.py`, `experiments/identity_articleB.py`, `tests/test_monitors.py`, `tests/test_identity_articleB.py`, `results/identity/articleB_R01_R08.csv`, `logs/identity/identity_articleB_{venv,articleB-venv}.log`, `docs/sections/monitors.md`, `prompts/plans/plan-04.md`, `prompts/wrapups/wrapup-04.md`.
- **Modifiés** : `Makefile` (ligne pyflakes seulement, déjà appliqué), `docs/DEVIATIONS.md` (quatre entrées ajoutées en fin).
- **Commité avec le stream** : `prompts/GO-stream-04.md` (trace de la décision GO).
- **Non commité** : `external/articleB-venv/`.
- **Non touchés** : `requirements.*` (numpy, scipy, pandas, statsmodels et pyyaml y sont déjà) et les livrables du stream 03.

---

### Tâche 0 — Enregistrer le plan
- [x] Copie à l'identique enregistrée dans `prompts/plans/plan-04.md` avant l'implémentation (règle C-plan-recording).
- [x] Amendement 4 de la revue GO : `prompts/plans/plan-04.md` est remplacé par ce plan final, qui intègre `prompts/GO-stream-04.md`, avant toute nouvelle action d'implémentation.

### Tâche 1 — `jepadrift/monitors/cusum.py`

**Ports verbatim**
- R01 l.110–142 : `strict_cusum(stream, delta_P, threshold) -> int`, `get_multiple_alarms(stream, delta_P, threshold, bilateral=False) -> list[int]`, `get_cusum_trajectory(stream, delta_P) -> ndarray`.
- R15_b l.350–360 : `bilateral_delay(stream, delta, thr) -> int`, `cusum_max_bilateral(stream, delta) -> float`. Le `strict_cusum` de R15 (l.343–348) est AST-identique à celui de R01.

**Versions vectorisées**
- Entrée (..., T) en float64 ; `ValueError` si une valeur n'est pas finie.
- Fonctions :
  - `cusum_trajectory_vec(streams, delta_P) -> (..., T)` ;
  - `strict_cusum_vec(streams, delta_P, threshold) -> (...) int64` (−1 si aucune alarme) ;
  - `bilateral_delay_vec(streams, delta, thr) -> (...) int64` ;
  - `cusum_max_bilateral_vec(streams, delta) -> (...) float64` ;
  - `multiple_alarms_vec(streams, delta_P, threshold, bilateral=False) -> (..., T) bool`. S⁺ et S⁻ sont remis à zéro après chaque alarme, comme dans `get_multiple_alarms`.
- Boucle sur T, vectorisée sur les trajectoires. Mêmes opérations IEEE dans le même ordre ((S + x) − δ, puis max avec 0), donc résultats bit-identiques aux ports scalaires.

**`P1`** (dict des configurations)
- `"P1-C/B"` : stream "label", delta 0.1, threshold 10.0, bilateral True, q_hat_window ("2018-01-02", "2019-12-31"), trailing_days 250.
- `"P1-C/C"` : stream "exact_sign", delta 0.1, threshold "lattice", bilateral True, comparison "strict", rule "at_or_below".
- `"P1-D/B"` : stream "energy", delta 0.5, lambda_iid 65.0, bilateral False, trailing_days 250. Seuil = 65·Γ̂, avec Γ̂ ajusté une seule fois sur gamma_hat_window ("2018-01-02", "2019-12-31") (écart B `R01-gamma-hat-refit`).

**Étapes**
- [ ] Tests dans `tests/test_monitors.py` :
  - `test_vectorized_cusum_matches_scalar_ports` : 50 trajectoires × 400 pas pour trois flux (étiquettes (u > 0.45) − 0.55 ; signe exact ±½ ; énergie (z² − 1)/√2), avec des seuils qui produisent des alarmes. Égalité stricte des indices, des trajectoires (`np.array_equal`), des maxima et des listes d'alarmes uni- et bilatérales.
  - `test_vectorized_cusum_rejects_nan`.
  - `test_p1_constants` (valeurs ci-dessus).
- [ ] `pytest -q tests/test_monitors.py` → échec attendu (module absent).
- [ ] Insérer les ports par extraction programmatique : octets identiques, espaces de fin compris. Écrire ensuite les versions vectorisées et `P1`.
- [ ] `pytest -q tests/test_monitors.py` → succès.

### Tâche 2 — `jepadrift/monitors/streams.py`

**Fonctions**
- `label_stream(r, q_hat)` = `(r > 0).astype(float) - q_hat` (R01 l.304, 374).
- `exact_sign_stream(y, rng)` = `1{y > 0} − ½`. Les cas y == 0 sont tranchés par `rng.random(n_ties) < 0.5` (tirage seulement pour ces cas ; `rng` est un `np.random.Generator`).
- `energy_stream(r, mu, sigma)` = `(r ** 2 - mu) / sigma` (R01 l.298, 369).
- `ValueError` si une entrée n'est pas finie.

**Étapes**
- [ ] Tests :
  - `test_streams_match_r01_expressions` : égalité bit à bit avec les expressions de R01.
  - `test_exact_sign_stream_ties_and_determinism` : valeurs dans {−½, ½} ; y > 0 ↦ +½ et y < 0 ↦ −½ ; sur 10 000 zéros, part de +½ dans 0.5 ± 0.02 ; même graine → même sortie.
  - `test_streams_reject_nan`.
- [ ] Échec attendu → implémentation → succès.

### Tâche 3 — `jepadrift/monitors/lattice.py`

**`lattice_steps(delta) -> (a, b, unit)`**
- Pas de S⁺ pour le flux exact ±½ de référence δ : +a / −b unités, avec `unit = pgcd(½ − δ, ½ + δ)`.
- Calcul en rationnels exacts sur `Fraction(repr(float(delta)))`.
- `ValueError` si δ ∉ [0, ½) ou si a + b > 1000.

**`exceedance(H, L, a, b, q=0.5, sided=2, comparison="strict") -> float`**
- Renvoie P(M_H > L) (strict) ou P(M_H ≥ L) (large), en unités, avec S_0 = 0. M_H = max_{t≤H} S⁺_t si sided=1, max_{t≤H} max(S⁺_t, S⁻_t) si sided=2.
- Barrière B = L + 1 (strict) ou L (large) ; états transitoires [0, B)^sided.
- À chaque pas : si y = 1 (probabilité q), S⁺ += a et S⁻ = max(0, S⁻ − b) ; si y = 0, S⁺ = max(0, S⁺ − b) et S⁻ += a.
- La masse qui franchit B s'accumule dans `absorbed` (on ne calcule pas 1 − survie). Décalages par tranches, en généralisation de R08 l.521–549.
- Cas limites : H = 0 → 0.0 ; B = 0 → 1.0.

**`arl0(L, a, b, q=0.5, sided=2, comparison="strict") -> float`**
- t = (I − Q)⁻¹1 sur les B^sided états, valeur lue à l'état 0. Exige 0 < q < 1.
- Si n > 10 000 → `ValueError`, avec `# ponytail: dense O(n^3) solve, banded/sparse solver if L > 99 is ever needed`.

**`attainable_levels(H=None, delta=0.1, sided=2, q=0.5, comparison="strict", min_level=1e-3) -> ndarray (n, 2)`**
- Lignes (λ = L·unit, niveau) pour L = 0, 1, …, jusqu'au premier niveau ≤ min_level.
- Niveau = FPR à l'horizon H, ou 1/ARL₀ si H is None.

**`select_threshold(nominal, rule="at_or_below", comparison="strict", *, H=None, delta=0.1, sided=2, q=0.5) -> dict`**
- Renvoie le plus petit L de niveau ≤ nominal : recherche par doublement puis dichotomie, le niveau étant monotone en L. `rule="at_or_above"` → L − 1 ; toute autre règle → `ValueError`.
- Retour : `{"units", "lam", "threshold", "level", "unit"}`, avec `threshold = (L + ½)·unit` (strict) ou `(L − ½)·unit` (large).
- Pour un ARL₀ visé γ : `nominal = 1/γ` et `H=None`.

**Étapes**
- [ ] Tests :
  - `test_lattice_steps` : 0.1 → (2, 3, 0.2) ; 0 → (1, 1, 0.5) ; 0.25 → (1, 3, 0.25) ; 0.5 → ValueError.
  - `test_exceedance_matches_enumeration` : H ∈ {6, 9} ; (a, b) ∈ {(2,3), (1,1), (1,3)} ; q ∈ {0.5, 0.3} ; sided ∈ {1, 2} ; strict et large ; L = 0…7. Comparaison à l'énumération pondérée des 2^H chemins, écart ≤ 1e-14.
  - `test_arl0_closed_form_and_mc` :
    - a = b = 1, unilatéral strict : ARL₀ = (L+1)(L+2) pour L = 0…10, à 1e-12 ;
    - L = 0 strict, a = 2 : ARL₀ = 1/q ;
    - (2, 3) bilatéral, L = 10 : écart au Monte Carlo (20 000 trajectoires, `bilateral_delay_vec` au seuil 2.1) inférieur à 4 erreurs-types.
  - `test_select_threshold_r08_bracket` (H = 5000, δ = 0.1, bilatéral, nominal 0.05) :
    - strict → units 57, lam ≈ 11.4, threshold = 57.5·0.2, level = 0.043428228893176074 à 1e-12 ;
    - at_or_above → units 56, level = 0.051020717214682557 ;
    - large → units 58, même threshold flottant ;
    - mode ARL₀ à γ = 252 : arl0(units) ≥ 252 > arl0(units − 1).
  - `test_midpoint_threshold_reproduces_lattice_rule` : 4000 trajectoires de pièces × 2000 pas. M/0.2 est à moins de 1e-6 d'un entier, et `M > threshold` ⇔ `round(M/0.2) > units`.
  - `test_attainable_levels_shape` (H = 200) : λ = k·0.2 ; niveaux non croissants ; dernier niveau ≤ 1e-3.
- [ ] Échec attendu → implémentation → succès.
- [ ] Vérifier `python -c "from jepadrift.monitors.lattice import attainable_levels as f; print(f(H=5000, delta=0.1, sided=1, q=0.5)[:5])"` (environ 4 s).

### Tâche 4 — `jepadrift/stats/garch.py` et `make check`
- [ ] Insérer verbatim `_garch_nll`, `fit_garch_qmle` et `compute_gamma_exact` (R01 l.72–108), avec `import numpy as np` et `from scipy.optimize import minimize`.
- [ ] Dans la cible `check` du `Makefile`, remplacer `pyflakes jepadrift experiments tests` par `pyflakes $(filter-out jepadrift/stats/garch.py,$(shell find jepadrift experiments tests -name '*.py'))`. Relire le Makefile juste avant et conserver le `--ignore=external` du stream 03.
- [ ] Test `test_compute_gamma_exact_spy` : `compute_gamma_exact(0.211551, 0.729081) == 14.998367977816738`.
- [ ] Lancer pyflakes sur la nouvelle liste de fichiers : aucun signalement attendu.
- Constat GO (amendement 2) : le hunk `Makefile` est appliqué et conforme, la ligne `pytest -q --ignore=external` est intacte. Ne pas y revenir ; le vérifier tel quel dans `git diff --staged` à la Tâche 11.

### Tâche 5 — `jepadrift/monitors/gamma.py`

**Fonctions**
- `gamma_spectral(x, L=None)` : Γ̂ = 1 + 2 Σ_{k=1}^{L} (1 − k/(L+1)) ρ̂(k), calculé sur le dernier axe. ρ̂ est l'ACF empirique (moyenne retirée, dénominateur Σ(x − x̄)²). Par défaut L = ⌊4(n/100)^{2/9}⌋ [Newey & West, 1994].
- `required_threshold(paths, delta, target, criterion="fpr", H=None, tol=1e-9) -> float` : CUSUM strict unilatéral sur des trajectoires nulles (R, T), calculées une seule fois par `cusum_trajectory_vec`.
  - "fpr" : plus petit λ tel que mean(max_{t<H} S_t > λ) ≤ target ;
  - "arl0" : plus petit λ tel que la durée moyenne (premier t + 1, censurée à T) ≥ target ;
  - dichotomie monotone sur [0, max S] ; cible inatteignable → `ValueError`.
- `gamma_operational(paths, delta, lam_iid, target, criterion="fpr", H=None, tol=1e-9) -> float` = `required_threshold(...) / lam_iid`.

**Étapes**
- [ ] Tests :
  - `test_gamma_spectral` : L par défaut = 4, 6 et 9 pour n = 100, 1000 et 5000 ; AR(1) φ = 0.5, n = 200 000 : à 3 % de 1 + 2Σ(1 − k/(L+1))φ^k ; i.i.d. : |Γ̂ − 1| < 0.05 ; axes de tête respectés.
  - `test_required_threshold_semantics` : FPR(λ) ≤ cible < FPR(λ − 1e-6) ; ARL(λ) ≥ cible > ARL(λ − 1e-6).
  - `test_gamma_operational` : trajectoires i.i.d. contre un λ_iid tiré d'un échantillon i.i.d. indépendant → Γ^op ∈ [0.9, 1.1] ; AR(1) positif → Γ^op > 1.3 ; ARL₀ visé > T → ValueError.
- [ ] Échec attendu → implémentation → succès.

### Tâche 6 — `jepadrift/monitors/eprocess.py`

**(a) Pari**
- `log_betting_eprocess(x, lam)` : somme cumulée de log1p(λ_t x_t) sur le dernier axe.
- `ValueError` si x ∉ [−1, 1] ou si |λ| ≥ 1.
- λ est un scalaire ou un tableau prévisible : λ_t ne dépend que de x_{<t}, ce qui relève du contrat de l'appelant.

**(b) MIX**
- Constantes : `MIX_H = 5000`, `START_GRID_SIZE = 16`, `ETA0_MIX_GRID = [0.05, 0.10, 0.15]`, `SIDES = [1, -1]`, `START_GRID = np.linspace(0, MIX_H - 1, START_GRID_SIZE, dtype=int)`, `C_MIX`, `MIX_W = 1.0 / C_MIX`.
- `build_mixture_kernel()` verbatim (R09 l.317–336).
- `log_mix_eprocess(x)` : boucle sur t comme R09 l.451–455. Composantes actives si `t >= start` ; incrément selon x_t > 0 ; valeur log MIX_W avant le départ ; logsumexp écrit en numpy.

**(c) e-détecteurs**
- `EDETECTOR_ETA0 = (0.05, 0.10, 0.15, 0.20)`.
- `log_edetector(x, kind="cusum", eta0=EDETECTOR_ETA0)` : 8 détecteurs de base, λ = 2·côté·η₀, f = 1 + λx.
  - SR : l_n = logaddexp(0, l_{n−1}) + log f_n ;
  - CUSUM : l_n = max(0, l_{n−1}) + log f_n ;
  - l_0 = −∞ ; sortie = log de la moyenne des 8.

**(d) Dictionnaire**
- `log_dictionary_edetector(x, kind="cusum", eta0=EDETECTOR_ETA0)` : x de forme (..., T, K) → log de la moyenne sur K des `log_edetector` de chaque direction. Valide quelle que soit la dépendance entre directions (Remarque « Combining channels »).

**(e) Mélange sous-gaussien**
- `log_subgaussian_mixture(z, s2)` : z de forme (..., T, D), S_n = Σ z, log L_n = −(D/2) log1p(n s²) + s²‖S_n‖²/(2(1 + n s²)) (Prop. 3).
- Docstring : « valid only if the coordinates are independent under H0 (sub-Gaussian variance proxy I_D, e.g. independent sign streams 2b − 1) ».

**Utilitaire**
- `first_alarm(log_m, gamma) -> (...) int64` : premier t tel que log_m ≥ log γ, −1 sinon.

**Étapes**
- [ ] Tests :
  - `test_betting_eprocess` : formule ; ValueError pour |λ| ≥ 1 ou |x| > 1 ; Ville sur 2000 pièces × 2000 pas, λ = 0.3 : P(sup ≥ 20) ≤ 0.05 + 3·√(0.05·0.95/2000).
  - `test_mix_kernel_constants` : 96 composantes ; MIX_W = 1/96 ; départs uniques = linspace(0, 4999, 16, int) ; ½e^{inc1} + ½e^{inc0} = 1 à 1e-15.
  - `test_mix_matches_direct_sum` (T = 700) : comparaison à la somme explicite Σ_c w Π_{s=start_c}^{t} f_c(y_s), valeur 1 avant le départ, à 1e-12.
  - `test_mix_ville` : 1000 trajectoires × 5000 pas, α = 0.05.
  - `test_edetector_recursions` : récurrences explicites en échelle linéaire, T = 50.
  - `test_edetector_strong_drift_finite` : x ≡ +1, T = 20 000 → sortie finie et croissante.
  - `test_edetector_arl0_exceeds_gamma` (contrôle Monte Carlo du prompt) : γ ∈ {20, 100}, SR et CUSUM, 2000 trajectoires, T_max = 60γ ; durée moyenne censurée > γ. Marges mesurées documentées dans `docs/sections/monitors.md` (recommandation 5) ; échec lié à la plateforme → écart consigné, 3 tentatives au plus, puis gel et alerte.
  - `test_dictionary_average` : égal à la moyenne explicite ; K directions dupliquées → même valeur que le détecteur unique.
  - `test_subgaussian_mixture` : D = 1, comparaison à l'intégrale numérique sur u ~ N(0, s²) à 1e-8 ; Ville avec D = 5 signes indépendants, s² = 0.02, 1000 × 2000 ; présence de la phrase de validité dans la docstring.
  - `test_first_alarm`.
  - `test_monitors_import_numpy_only` : les imports (lus par AST) de `jepadrift/monitors/*.py` sont inclus dans {numpy, math, fractions, jepadrift.monitors}.
- [ ] Échec attendu → implémentation → succès.

### Tâche 7 — Contrôle Monte Carlo GARCH (item 10 du prompt)
- [ ] `test_lattice_calibrated_cusum_on_garch_sign_stream` :
  - données : `from experiments.e2_floor_validation import Garch` ; 4 blocs de 5000 trajectoires (`SeedSequence([4, 7, bloc])`) ; `Garch(rng, 5000, 1, 0.08, 0.90)` ; H = 1000 tirages ; s = `exact_sign_stream(...)` ;
  - seuil : sel = `select_threshold(0.05, H=1000, delta=0.1, sided=2)` ;
  - FPR = part des 20 000 trajectoires où `bilateral_delay_vec(s, 0.1, sel["threshold"]) >= 0` ;
  - critère : l'intervalle `scipy.stats.binom.interval(0.99, 20000, sel["level"]) / 20000` contient le FPR.

### Tâche 8 — Identité Article B : `experiments/identity_articleB.py` et `tests/test_identity_articleB.py`

**Fonctions du script**
- `wilson_ci` et `save_fair_csv` verbatim (R01 l.144–148 ; `fair_harness.py` l.84–88).
- `r01_frames(input_mode) -> dict[str, DataFrame]` :
  - "d1_loader" → `load_d1()` ; pour chaque ETF, les valeurs non NaN de sa colonne, index `DatetimeIndex` (ns) nommé Date, colonne `log_ret` ;
  - "articleB_csv" → `pd.read_csv(..., index_col='Date', parse_dates=True)`, comme R01 l.249.
- `injection_streams(frames, models) -> list[dict]` (ticker, onset, delta_f, e_test, s_test, thr_data) : flux de la phase 3 (R01 l.350–378), partagés par la réplication et par le test de vectorisation.
- `replicate_r01(frames) -> dict[str, DataFrame]` : transcription des phases 1 à 3 de R01 (l.257–332 et 346–416).
  - Options pandas `compute.use_bottleneck` et `compute.use_numexpr` à False, comme `disable_pandas_multithreading`.
  - Primitives tirées de `jepadrift.monitors.cusum`, `streams` et `jepadrift.stats.garch` ; constantes `P1`.
  - Mêmes colonnes et même ordre de lignes que les six CSV de B.
- `compare_frames(source, ref, new) -> DataFrame` : comparaison en format long.
- `r08_rows() -> DataFrame` : les 32 lignes de `R08_lattice_exact_law.csv`, recalculées par `lattice.exceedance(H, units, 2, 3)`, avec input "n/a".
- `identity_table(inputs=("d1_loader", "articleB_csv")) -> DataFrame` : colonne env = `Path(sys.prefix).name.lstrip(".")`.
- `main(argv=None)` :
  - options `--out results/identity/articleB_R01_R08.csv` et `--log-dir logs/identity` ;
  - remplace les lignes de son env, puis tri stable par (env, input, source) ;
  - journal : versions, commit de B, comptes de cellules passées et bit-identiques par source × entrée, écart relatif maximal par colonne ;
  - code retour 0 si et seulement si toutes les lignes `d1_loader` et R08 passent.

**Tests** (module ignoré si le dépôt B est absent ; table calculée une fois par une fixture de module)
- [ ] `test_ported_sources_byte_identical` :
  - R01 : strict_cusum, get_multiple_alarms, get_cusum_trajectory, _garch_nll, fit_garch_qmle, compute_gamma_exact, wilson_ci ;
  - R15_b : bilateral_delay, cusum_max_bilateral ;
  - R09 : build_mixture_kernel ;
  - fair_harness : save_fair_csv ;
  - en plus, `ast.dump` égal entre le strict_cusum de R15 (l.343) et celui de R01 (l.110).
- [ ] `test_r01_identity_d1_loader` : toutes les lignes `pass`. SPY : alpha 0.211551, beta 0.729081, gamma_hat 14.998367977816738, q_hat 0.55864811133200798. `n_alarms` = 0.
- [ ] `test_r01_reader_bit_identical_in_article_b_env` : ignoré hors numpy 1.26.4 / scipy 1.16.2 / pandas 2.3.2 / statsmodels 0.14.5 ; dans cet environnement, toutes les cellules `articleB_csv` sont bit-identiques.
- [ ] `test_r08_exact_law` : 32 lignes à 1e-12 ; λ = 11.2 → 0.051020717214682557 ; λ = 11.4 → 0.043428228893176074.
- [ ] `test_vectorized_cusum_on_r01_streams` : sur les 576 flux (4 ETF × 36 onsets × 4 Δ), `strict_cusum_vec` et `bilateral_delay_vec` égalent les ports scalaires.
- [ ] Échec attendu → implémentation → succès dans `.venv`. Puis `PYTHONHASHSEED=42 .venv/bin/python experiments/identity_articleB.py` → code de retour 0.

### Tâche 9 — Second environnement
- [ ] Créer le venv et l'équiper :
  ```bash
  ~/miniforge3/envs/Trading/bin/python -m venv external/articleB-venv
  external/articleB-venv/bin/pip install -r ~/The-Whitening-Advantage-Experiments/requirements.txt
  external/articleB-venv/bin/pip install pyyaml
  ```
  Vérifier numpy 1.26.4 et scipy 1.16.2. En cas d'échec réseau ou de compilation : 3 tentatives au plus, puis gel et alerte.
- [ ] `PYTHONHASHSEED=42 external/articleB-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_identity_articleB.py`.
- [ ] `PYTHONHASHSEED=42 external/articleB-venv/bin/python experiments/identity_articleB.py`, qui ajoute les lignes `articleB-venv` au CSV.

### Tâche 10 — Documentation et écarts
- [ ] `docs/sections/monitors.md` (anglais) :
  - API, module par module ;
  - fonctions et constantes portées, avec fichier, lignes et commit B `a05f0d9` ;
  - conventions d'échelle : CUSUM sur flux centrés, e-processus sur x ∈ [−1, 1] ;
  - sémantique du treillis : strict ou large, seuil au milieu, utilisé par P1-C/C et par le contrôle GARCH (Tâche 7) via `sel["threshold"]` ;
  - marges de l'ARL₀ des e-détecteurs (SR et CUSUM, γ ∈ {20, 100}) mesurées par `test_edetector_arl0_exceeds_gamma` ;
  - configurations P1 ;
  - résultats d'identité tirés du CSV, avec les commandes de reproduction ;
  - références : [Page, 1954], [Lorden, 1971], [Ville, 1939], [Ramdas et al., 2023], [Shin, Ramdas & Rinaldo, 2024], [Newey & West, 1994], [Robbins, 1970].
- [ ] `docs/DEVIATIONS.md` : relire juste avant, puis ajouter en fin de fichier :
  - `C-R01-parse` : lecteur pandas par défaut de R01 contre `round_trip` de D1 (jusqu'à 7356 ulp) ; effets mesurés par colonne ; identité exacte avec le lecteur de R01 ;
  - `C-R01-env` : écarts mesurés entre `.venv` et `articleB-venv` ; pyyaml ajouté au venv B ;
  - `C-garch-pyflakes` ;
  - `C-lattice-midpoint`.

  Toutes les valeurs citées sont reprises du CSV d'identité.

### Tâche 11 — Clôture du stream (ordre AGENTS.md)
- [ ] **Vérifications** :
  - `pytest -q tests/test_monitors.py tests/test_identity_articleB.py`, le second fichier dans les deux environnements ;
  - la commande `attainable_levels` du prompt ;
  - `source .venv/bin/activate && make check`. L'état de départ est vert (42 tests au HEAD `3e3a804`) : tout échec est investigué, pas attribué au stream 03 ; un échec externe apparu en cours de stream entraîne gel et signalement. Contrôler ensuite `git diff data/derived/MANIFEST.json` (le fixture D1/D2 reconstruit le manifeste).
- [ ] **(1)** Skill `wrap-up`, résumé enregistré dans `prompts/wrapups/wrapup-04.md`.
- [ ] **(2)** `tools/reindex_graphify_jcodemunch.sh`.
- [ ] **(3)** `make check`, puis `git status` et `git diff`.
  - Indexer explicitement les fichiers créés listés plus haut, `Makefile`, `docs/DEVIATIONS.md`, `prompts/plans/plan-04.md`, `prompts/wrapups/wrapup-04.md` et `prompts/GO-stream-04.md` (aucune indexation partielle : aucun hunk étranger non commité).
  - `git diff --staged` : hunk `Makefile` identique à celui de la Tâche 4 ; aucun `__pycache__`, aucun `external/`, aucun chemin absolu du répertoire personnel ; aucun fichier indexé > 50 Mo ; aucun horodatage dans `logs/identity/*.log`.
  - Commit unique, sans trailer : `feat(monitors): add univariate CUSUM core, exact lattice law, e-detectors and Article B R01/R08 identity`.
- [ ] **(4)** Vérifier que la plage `origin/main..HEAD` ne contient aucun chemin `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` ni aucun fichier > 50 Mo. Puis `git push origin main` et rapporter le hash.

## Vérification de bout en bout

```bash
source .venv/bin/activate && export PYTHONHASHSEED=42
pytest -q tests/test_monitors.py tests/test_identity_articleB.py
python -c "from jepadrift.monitors.lattice import attainable_levels as f; print(f(H=5000, delta=0.1, sided=1, q=0.5)[:5])"
python experiments/identity_articleB.py
external/articleB-venv/bin/python -m pytest -q -p no:cacheprovider tests/test_identity_articleB.py
external/articleB-venv/bin/python experiments/identity_articleB.py
make check
```

Résultats attendus :
- tous les tests passent ;
- dans `results/identity/articleB_R01_R08.csv`, toutes les lignes `d1_loader` et R08 ont `pass=True` dans les deux environnements ;
- les lignes `articleB_csv` sont bit-identiques dans `articleB-venv`.

## Risques

| Risque | Parade |
|---|---|
| SLSQP ou statsmodels divergent d'une version à l'autre | Constaté : α et β identiques, p-values de Ljung–Box à 4.6e-15 près → `C-R01-env` |
| pip sans réseau, ou échec de compilation (river) | 3 tentatives. À défaut, installer numpy, pandas, scipy, statsmodels, pytest et pyyaml aux versions de B, consigner l'écart et alerter |
| `make check` rouge | État de départ vert (42 tests) : tout échec est investigué ; gel, signalement et aucun commit si la cause est externe |
| Édition concurrente d'un fichier partagé | Read juste avant chaque Edit |
| Marge du contrôle ARL₀ des e-détecteurs (≈ 8–10 % pour SR) | Test déterministe à 2000 trajectoires, marge documentée ; échec lié à la plateforme → écart consigné, 3 tentatives, gel |
| Durée des tests | Environ 20 s pour `test_monitors` (Monte Carlo compris), environ 15 s pour l'identité |
