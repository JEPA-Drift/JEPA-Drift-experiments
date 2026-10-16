## PROMPT 7 — Surveillance (2/3) : pipelines transversaux P2-C, P3-C, P3-D, P3-CS, P7 et calibrations

### Contexte
JEPA-Drift compare un actif seul (P1), le pooling de signes (P2), la projection orthogonale au marché (P3), la coupe normalisée de degré 0 (P3-CS) et un oracle (P7). Chaque pipeline traverse la même pile de détection ; seule la représentation change. Bloquant pour E1 et E3 (J2). Lire `CLAUDE.md`.

Propriété clé : toute moyenne de bits exacts centrés en 1/2 est une différence de martingale bornée sous H₀. Un e-processus de pari sur cette moyenne est donc exactement valide, quelle que soit la corrélation entre actifs.

### Tâche
1. **Registre** `jepadrift/pipelines.py` : `PIPELINES[id] = (representation, stream_builder, detector, calibration)`. Exécution via `run_pipeline(spec, X|Z, splits, onset_info) -> alarms.csv`, avec les colonnes `run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold, reading`.
2. **P2-C, portage de R15.**
   - Recopier `composition_for`, `worker_null_window_real` et `worker_race_h1_real` de `~/The-Whitening-Advantage-Experiments/experiments/R15_cross_sectional/exp_R15_cross_sectional_b.py`.
   - Flux de fraction f_t = moyenne des 1{z_k > 0} − 0.5, avec médiane et écart-type par fenêtre sur H_ref = 500.
   - CUSUM bilatéral δ = 0 ; seuil par bootstrap de N_cal = 20 000 fenêtres réelles, H_det = 750, FPR cible 5 %.
   - Lecture anytime-valid ajoutée : e-détecteur de pari sur la fraction des signes bruts (centrés en 0, sans recentrage par médiane).
   - Rapporter ρ̂_signe et K_eff.
3. **Contrôle d'identité.** Reproduire `rho_sign_meas` et `K_eff_meas` de `~/The-Whitening-Advantage-Experiments/results/R15_cross_sectional/data/R15_panel_diagnostics.csv` pour K ∈ {5, 10, 20} à 1e-12. La fonction de calcul est à reprendre dans le script R15. Valeurs attendues de ρ̂ : 0.25774155995343417, 0.25904514047705118 et 0.28810195766064206.
4. **P3-C.**
   - Flux de signe exact par direction : canal marché plus directions résiduelles (prompt 6).
   - Détecteur par défaut : moyenne de dictionnaire des e-détecteurs CUSUM par direction, poids égaux sur tous les canaux.
   - Option : mélange sous-gaussien sur les directions résiduelles, autorisé seulement si le test d'indépendance croisée sous H₀ passe (|ρ̂| < 3 erreurs-types sur toutes les paires).
5. **P3-D.**
   - q_t = (‖z_res‖² − D)/√(2D) ; CUSUM strict δ = 0.5.
   - Seuil par bootstrap de fenêtres nulles de calibration. L'inversion de signe n'a aucun effet sur une statistique paire.
   - Rapporter Γ_z^op = λ_requis/λ_iid.
6. **P3-CS.**
   - (a) Pivot s_t = uᵀPx_t/‖Px_t‖ : e-processus de pari, et CUSUM à design fixe calibré par randomisation d'inversion de signe (B = 2000).
   - (b) e-détecteur de signe à mise prévisible λ_t = min(0.5, c/σ̂_{t|t−1}). σ̂ est une moyenne exponentielle (demi-vie 20 jours) de ‖Px_{t−1}‖ ; c est fixé sur la fenêtre de calibration.
7. **P7, oracle.** w* = Σ̂⁻¹Δ (Δ connu par `tau_star.json`) ; CUSUM du rapport de vraisemblance gaussien. P7 est rapporté comme borne seulement.
8. **Calibrations** dans `jepadrift/monitors/calibration.py` :
   - randomisation d'inversion de signe, exacte sous symétrie conditionnelle et sans effet de levier ;
   - bootstrap de fenêtres (port de R15) ;
   - treillis exact (prompt 4).
9. **Tests** `tests/test_pipelines.py` :
   - FPR sous H₀ sur fonds D6 dans l'IC binomial à 99 % de la cible, pour P3-C, P3-CS (pari) et la lecture anytime-valid de P2-C ;
   - P2-C par bootstrap à 5 % ± IC ;
   - détection à 100 % d'une injection F2 forte (SR = 8).

### Entrées
Prompts 2 à 6 ; `~/The-Whitening-Advantage-Experiments/` (lecture seule) ; `CLAUDE.md`.

### Livrables
`jepadrift/pipelines.py`, `jepadrift/monitors/calibration.py`, `tests/test_pipelines.py`, `results/identity/articleB_R15.csv`, `docs/sections/pipelines.md`, qui donne pour chaque pipeline sa lecture (budget, anytime-valid, exacte, bootstrap).

### Contraintes techniques
- `monitors` reste en numpy seul.
- Les représentations entrent sous forme de tableaux Z ou X, jamais comme objets importés dans `monitors`.
- Tâches parallélisables, mais résultats identiques quel que soit le nombre de processus.

### Critères de succès
Identité R15 exacte ; tests au vert ; une ligne d'`alarms.csv` par réplication.

### Commandes de vérification
```bash
pytest -q tests/test_pipelines.py
python -m jepadrift.pipelines --pipeline P3-C --dataset d2_us97 --null-check --reps 500
```
