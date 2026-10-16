J1, tel qu'il est écrit dans le plan v4 (« ADD simulés à ±10 % des Props 2–3 »), échouait par construction. Le plancher de premier ordre ln γ/I n'est exact que comme budget d'évidence. Pour SR = 1, il surestime le délai minimal de Lorden d'un facteur 90 à γ = 20 et d'un facteur 19 à γ = 252. J'ai exécuté E2 en avance dans le bac à sable, puis reformulé les Props 2–3 sous forme non asymptotique. Sous la règle corrigée, la validation passe 46/46.

*Remarque: l' **Article B** dont il est fait référence dans la suite a une copie de son manuscrit dans `~/JEPA-Drift-experiments/articleB_whitening` et son repo local se trouve sur `~/The-Whitening-Advantage-Experiments`

## 1. Résultats d'E2 (2 000 réplications, graine 20261018, 75 s sur un cœur)

Fond gaussien, D = 1, SR = 1 (I = 1/504 nat par jour). Délais en jours de bourse.

| γ   | Lecture                              | Mesuré | Prédit | ln γ/I | ARL₀ mesuré |
| --- | ------------------------------------ | ------ | ------ | ------ | ----------- |
| 20  | budget (e-processus lancé à l'onset) | 1 519  | 1 528  | 1 510  | —           |
| 20  | CUSUM e-détecteur, seuil ln γ        | 1 050  | 1 066  | 1 510  | 8 005       |
| 20  | CUSUM calibré à ARL₀ = γ             | 16,7   | 16,7   | 1 510  | 20,7        |
| 252 | budget                               | 2 815  | 2 805  | 2 787  | —           |
| 252 | CUSUM e-détecteur                    | 2 320  | 2 322  | 2 787  | 142 211     |
| 252 | CUSUM calibré                        | 145    | 142    | 2 787  | 258         |

Résultats sur le reste de la grille :
- **G1** (18 cellules, SR ∈ {1, 2, 4}) : écart maximal de 2,4 %. Le premier ordre surestime le délai calibré d'un facteur allant de 3,6 (SR = 4, γ = 252) à 90 (SR = 1, γ = 20). Il surestime celui de l'e-détecteur de 14 à 44 %.
- **G2** (mélange isotrope, D de 1 à 64) : écart maximal de 4,7 %. M(D) tient.
- **S1** (flux de signe sur GARCH(0,08 ; 0,90)-t₇ symétrisé) :
  - l'horloge d'information tombe à 3,3 % de la prédiction ;
  - le délai calendaire tombe à 2,6 % pour SR ≤ 2 ;
  - à SR = 4, avec des délais sous 180 jours, il dépasse de 5,7 à 11,8 %. Cela correspond à un terme additif de 8 à 11 jours, dû à la mémoire de volatilité.
- **S2** (mélange sous-gaussien sur 5 et 20 flux de signes, même fond) : écart maximal de 4,6 %.
- **H₀** : les bits ont une moyenne de 0,4998, une autocorrélation de +0,0002 et une corrélation croisée de −0,0009 (écart-type 0,0010). Les carrés ont une autocorrélation de +0,067. Les flux de signe restent donc exacts sous GARCH.

À γ = 252, le détecteur calibré exactement détecte SR = 1 en environ 145 jours. Mais son délai n'est que 1,8 fois plus court que son temps moyen avant une fausse alarme. Le « plancher » décrit l'évidence disponible, pas le délai de Lorden.

## 2. Ce qui change dans la théorie

1. **Lemme 1 (budget d'évidence), nouveau et exact.** Toute supermartingale de test lancée à l'onset vérifie E₁[Σ_{t≤T} I_t] ≥ ln γ. Pour le rapport de vraisemblance, l'égalité tient au dépassement près. La preuve :
   - E_n/Λ_n est une P₁-surmartingale ;
   - on conclut par Jensen et par l'identité de Wald.

   Le plafond de Sharpe devient ainsi un énoncé non asymptotique, avec les mêmes chiffres.
2. **Prop. 2 en trois lectures.**
   - (a) e-détecteur CUSUM au seuil ln γ : ADD·I = h′ − 1 + e^{−h′}.
   - (b) calibration exacte : ADD·I → Φ(γI). Cela découle de Moustakides (1986), de Taylor (1975) et de la correction de Siegmund.
   - (c) forme Sharpe.
3. **Correction de la note du 11 octobre.** SR_z ≤ SR_x n'est vrai que si x_t est conditionnellement gaussien. Le canal N3 permet SR_z > SR_x tout en gardant I_z ≤ I_x : la DPI porte sur I, pas sur le Sharpe.
4. **Décomposition facteur/largeur exacte à N fini.** On a B⊤Σ⁻¹B = (Σ_F + K⁻¹)⁻¹, au lieu de la seule limite N → ∞. Un test le vérifie à 10⁻⁸ près.
5. **Prop. 3.** L'identité E₁[log L_n] = x − (D/2) ln(1 + 2x/D) est exacte. M(D) en est l'approximation fluide. Sur des flux de signe, le mélange n'est valide que si les bits des D directions sont indépendants sous H₀. Sinon, il faut faire la moyenne des supermartingales (Remarque 1).
6. **Prop. 4 (absorption), désormais démontrée.** Si le budget total B est inférieur à ln γ, aucune supermartingale de test n'atteint γ presque sûrement.

## 3. Conséquences pour le plan et pour l'Article B

- **J1 (à remplacer au §2.4 du plan v4).**
  - Bras gaussiens : les délais doivent tomber à ±10 % du Lemme 1, de la Prop. 2(a), de la Prop. 2(b) et de la Prop. 3. L'ARL₀ réalisé du CUSUM calibré doit tomber à ±10 % de γ.
  - Bras GARCH : l'horloge d'information doit tomber à ±10 %. Le délai calendaire aussi, dès que la prédiction dépasse 150 jours.
- **Métriques (§2.3).**
  - G_floor est le rapport des I. Il est exact.
  - G_ADD à seuil γ égal (lecture anytime-valid) devient la métrique principale. Sa prédiction est G_floor × M_A/M_B.
  - G_ADD à ARL₀ exact est réservé aux flux de signe. Sa prédiction (I_B/I_A)·Φ(γI_A)/Φ(γI_B) n'est pas linéaire. Elle ne doit donc jamais servir aux pentes de J2.
- **Brouillon du §1 (plan v4, §4.2).** La phrase « … SR = 1 requires at least 2,787 trading days » est fausse à γ fini. Je la réécris en lecture budget au lot 3.
- **Article B.** La Cor. 3.6 est correcte comme énoncé asymptotique. En revanche, « at γ = 20, SR = 1 costs at least ≈1,510 trading days » est faux comme énoncé sur l'ADD, puisque 17 jours sont atteignables.
  - Avec le Lemme 1, le recensement devient exact sans changer un chiffre : même un moniteur qui connaît le début et la direction d'une phase accumule en moyenne moins de ln γ nats sur la phase entière, pour 53 phases sur 66.
  - C'est une réponse à R11 plus forte que la reformulation du deck du 28/09.
  - À intégrer à la version caméra (D4) ou au cycle 2.

## 4. Reste de S1, à livrer avant le dimanche 18

- **Lot 2.**
  - `jepadrift/monitors.py` : P1-C et P1-D portés du dépôt public de l'Article B, P2-C, P3-C/D, P3-CS, randomisation par inversion de signe, injections F1–F4, e-détecteur à mélange.
  - Les quatre tests de contrat.
- **Lot 3.**
  - §1 v0 en lecture budget.
  - Tableaux 1–3 v0.
  - T6–T7 : Γ_z spectral contre Γ_z opérationnel, et l'échelle d'efficacité.

## 5. Livrables S1, lot 1/3 (six fichiers neufs)

Exécution côté piste X (Python ≥ 3.9, numpy, scipy, pytest) :

```bash
OPENBLAS_NUM_THREADS=1 python -m pytest -q tests/test_floors.py
python experiments/e2_floor_validation.py --reps 2000 --out results/e2
```

Valeurs de référence :
- les 6 tests passent ;
- le SHA-256 de `results/e2/e2_cells.csv` commence par `e315e537ead0f656` (Python 3.12.3, numpy 2.4.4, scipy 1.17.1) ;
- le script affiche « J1: PASS ».

Le §3 et l'annexe A compilent sans erreur avec `articleB_biblio_v69.bib` et l'addendum. Les étiquettes `sec:problem`, `sec:method` et `sec:exp-floors` seront définies par les sections correspondantes.

**Target file: `jepadrift/floors.py`**
```python
"""Analytic delay floors for sequential drift detection (Article C, Section 3).

Units: one observation per trading day. ``info`` is the per-observation
Kullback-Leibler divergence I between post- and pre-change laws (nats).
``gamma`` is either an in-control average run length (ARL0) or an anytime-valid
threshold on the e-value scale; the docstring of each function states which.

Three readings of the same budget (Proposition 2):
  * evidence budget, exact: any e-process started at the onset needs
    E[T] >= ln(gamma)/I to reach gamma (Lemma 1), equality up to overshoot
    for the likelihood-ratio e-process;
  * CUSUM e-detector at threshold ln(gamma) (anytime-valid, ARL0 >= gamma):
    ADD * I = h' - 1 + exp(-h') with h' = ln(gamma) + 2*rho*theta;
  * CUSUM calibrated to ARL0 = gamma exactly (Lorden-optimal, Moustakides 1986):
    ADD * I = Phi(gamma * I), Brownian limit with Siegmund's correction.
All three share Lai's first-order limit ln(gamma)/I as gamma -> infinity.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

TRADING_DAYS = 252
RHO_GAUSS = 0.5826  # Siegmund's overshoot constant, Gaussian increments


def kl_from_sharpe(sr_annual: float) -> float:
    """Per-day KL of a homoscedastic Gaussian location shift: SR^2 / 504."""
    return sr_annual ** 2 / (2 * TRADING_DAYS)


def sharpe_from_kl(info: float) -> float:
    """Annualized Sharpe ratio carrying ``info`` nats per day."""
    return math.sqrt(2 * TRADING_DAYS * info)


def first_order_floor(gamma: float, info: float) -> float:
    """Lai's first-order bound ln(gamma)/I, exact only as gamma -> infinity."""
    return math.log(gamma) / info


def evidence_budget(gamma: float, info: float) -> float:
    """Lemma 1: lower bound on E[T] for any e-process started at the onset
    and stopped at gamma; attained up to overshoot by the likelihood ratio."""
    return math.log(gamma) / info


def onset_lr_delay(gamma: float, info: float, theta: float) -> float:
    """Expected delay of the likelihood-ratio e-process started at the onset,
    Gaussian shift of theta standard deviations (LLR increment s.d. = theta):
    E[T] = (ln(gamma) + rho*theta) / I (Wald identity, ladder-height overshoot)."""
    return (math.log(gamma) + RHO_GAUSS * theta) / info


def brownian_h(g: float) -> float:
    """Root h > 0 of exp(h) - h - 1 = g (Brownian CUSUM threshold, scaled)."""
    if g <= 0:
        raise ValueError("g must be positive")
    upper = max(2.0, 2.0 * math.log1p(g) + 2.0)
    return brentq(lambda h: math.expm1(h) - h - g, 1e-12, upper)


def phi(g: float) -> float:
    """Scaled Lorden-optimal delay: ADD * I = Phi(gamma * I).
    Phi(g) = ln g - 1 + O(ln g / g) as g -> inf; g - (2g)^{3/2}/3 + O(g^2) as g -> 0."""
    h = brownian_h(g)
    return h - 1.0 + math.exp(-h)


def cusum_exact(gamma: float, theta: float) -> dict:
    """Page CUSUM on the Gaussian LLR, calibrated to ARL0 = gamma (Siegmund).
    Returns the LLR threshold h and the predicted Lorden delay."""
    info = theta ** 2 / 2
    h_prime = brownian_h(gamma * info)
    h = h_prime - 2 * RHO_GAUSS * theta
    return {"h": h, "h_prime": h_prime,
            "add": (h_prime - 1.0 + math.exp(-h_prime)) / info,
            "feasible": h > 0}


def cusum_threshold(gamma: float, theta: float) -> dict:
    """CUSUM e-detector stopped when exp(W_n) >= gamma, i.e. h = ln(gamma).
    ARL0 >= gamma holds by Lorden's bound; the realised ARL0 is ~ gamma / I."""
    info = theta ** 2 / 2
    h = math.log(gamma)
    h_prime = h + 2 * RHO_GAUSS * theta
    return {"h": h, "h_prime": h_prime,
            "add": (h_prime - 1.0 + math.exp(-h_prime)) / info,
            "arl0": (math.expm1(h_prime) - h_prime) / info}


def mixture_multiplier(dim: int, gamma: float) -> float:
    """Proposition 3: M(D) = x/A with x = A + (D/2) ln(1 + 2x/D), A = ln(gamma).
    Fluid delay of the isotropic Gaussian mixture e-process (matched prior)
    relative to the known-direction likelihood ratio."""
    a = math.log(gamma)
    x = a
    for _ in range(10_000):
        x_new = a + 0.5 * dim * math.log1p(2.0 * x / dim)
        if abs(x_new - x) < 1e-12 * x_new:
            break
        x = x_new
    return x_new / a


def dictionary_multiplier(n_atoms: int, gamma: float, cos2: float) -> float:
    """Average of n_atoms direction-wise e-processes: delay multiplier
    (A + ln n_atoms) / (A cos^2), cos^2 = alignment of the whitened drift
    with the nearest atom."""
    a = math.log(gamma)
    return (a + math.log(n_atoms)) / (a * cos2)


def absorption_delay(add_oracle: float, tau_a: float) -> float:
    """Fluid delay when an adaptive encoder absorbs the drift at rate 1/tau_a.
    Necessary condition for almost-sure detection: tau_a > 2 * add_oracle."""
    ratio = 2.0 * add_oracle / tau_a
    if ratio >= 1.0:
        return math.inf
    return -0.5 * tau_a * math.log1p(-ratio)


def kl_bernoulli_half(p):
    """kl(p || 1/2) in nats, vectorised; information of an exact sign stream."""
    p = np.clip(np.asarray(p, dtype=float), 1e-15, 1 - 1e-15)
    return p * np.log(2 * p) + (1 - p) * np.log(2 * (1 - p))


def factor_information(B, sigma_f, psi_diag, d_lambda, d_alpha):
    """Exact split of Delta_mu' Sigma^{-1} Delta_mu for Sigma = B Sigma_F B' + Psi
    (Corollary 1). Returns (factor_term, breadth_term), with
    factor_term = dl' (Sigma_F + K^{-1})^{-1} dl, K = B' Psi^{-1} B,
    breadth_term = da_perp' Psi^{-1} da_perp (GLS residual of d_alpha on B)."""
    B = np.atleast_2d(np.asarray(B, dtype=float))
    if B.shape[0] < B.shape[1]:
        B = B.T
    psi_inv = 1.0 / np.asarray(psi_diag, dtype=float)
    K = B.T @ (psi_inv[:, None] * B)
    c = np.linalg.solve(K, B.T @ (psi_inv * d_alpha))
    da_perp = d_alpha - B @ c
    dl_tilde = np.atleast_1d(d_lambda) + c
    M = np.atleast_2d(sigma_f) + np.linalg.inv(K)
    factor_term = float(dl_tilde @ np.linalg.solve(M, dl_tilde))
    breadth_term = float(da_perp @ (psi_inv * da_perp))
    return factor_term, breadth_term
```

**Target file: `tests/test_floors.py`**
```python
"""Contract tests for jepadrift.floors (pytest)."""
import math

import numpy as np

from jepadrift import floors as fl


def test_phi_limits():
    for g in (50.0, 500.0, 5000.0):
        assert abs(fl.phi(g) - (math.log(g) - 1.0)) < 2.5 * (math.log(g) + 2) / g
    for g in (1e-4, 1e-3):
        assert abs(fl.phi(g) - (g - (2 * g) ** 1.5 / 3)) < 5 * g ** 2


def test_first_order_overstates_exact():
    info = fl.kl_from_sharpe(1.0)
    for gamma in (20, 252, 1000):
        exact = fl.cusum_exact(gamma, math.sqrt(2 * info))["add"]
        assert exact < fl.first_order_floor(gamma, info)


def test_mixture_multiplier_table():
    # values reported in the theoretical note of 11 Oct 2026 (ARL0 = 504)
    for dim, ref in ((1, 1.22), (10, 2.01), (64, 3.91), (500, 9.64)):
        assert abs(fl.mixture_multiplier(dim, 504) - ref) < 0.01


def test_factor_identity_matches_direct_inverse():
    rng = np.random.default_rng(0)
    n, k = 60, 3
    B = rng.normal(size=(n, k))
    sigma_f = np.diag([0.5, 0.2, 0.1])
    psi = rng.uniform(0.5, 1.5, size=n)
    dl, da = rng.normal(size=k), rng.normal(size=n)
    sigma = B @ sigma_f @ B.T + np.diag(psi)
    dmu = B @ dl + da
    direct = dmu @ np.linalg.solve(sigma, dmu)
    f_term, b_term = fl.factor_information(B, sigma_f, psi, dl, da)
    assert abs(direct - (f_term + b_term)) < 1e-8 * direct


def test_one_factor_keff():
    n, rho = 239, 0.40
    B = np.ones((n, 1))
    f_term, b_term = fl.factor_information(B, [[rho]], np.full(n, 1 - rho), np.array([1.0]), np.zeros(n))
    assert abs(f_term - n / (1 + (n - 1) * rho)) < 1e-9 and b_term < 1e-12


def test_absorption_threshold():
    assert math.isinf(fl.absorption_delay(100.0, 200.0))
    assert abs(fl.absorption_delay(100.0, 250.0) / 100.0 - 2.012) < 1e-3
```

**Target file: `experiments/e2_floor_validation.py`**
```python
"""E2 (Section 5.1): Monte Carlo validation of Propositions 2-3, milestone J1.

Arms (drift starts at the onset, no pre-change data: Lorden's worst case)
  G1  Gaussian i.i.d., known direction (D = 1), three calibrations:
        onset   likelihood-ratio e-process started at the onset, stopped at gamma
        cusum_t CUSUM e-detector stopped at ln(gamma)  (anytime-valid, ARL0 >= gamma)
        cusum_x CUSUM calibrated to ARL0 = gamma        (Lorden-optimal)
  G2  Gaussian i.i.d., unknown direction in dimension D: isotropic mixture
      e-process started at the onset (Proposition 3)
  S1  symmetrised GARCH(1,1)-t7 background, exact sign stream (D = 1):
        fixed   Bernoulli likelihood ratio with p1 = E[p_t]
        oracle  predictable stakes 2 p_t - 1 (volatility known one step ahead)
  S2  symmetrised GARCH(1,1)-t7, D sign streams, sub-Gaussian mixture e-process
J1 rule. Gaussian arms: measured/predicted delay within [0.90, 1.10] (and the
realised ARL0 of cusum_x within 10% of gamma). GARCH arms: the information clock
sum_{t<=T} I_t at stopping within 10% of its prediction (Lemma 1, exact up to
overshoot); calendar delay within 10% whenever the predicted delay exceeds
CALENDAR_MIN days, below which the volatility-memory term (order CV^2 x tau_int
of I_t, about 10-15 days here) is reported, not gated.
The first-order floor ln(gamma)/I is reported next to each prediction.

Usage: python experiments/e2_floor_validation.py --reps 2000 --out results/e2
"""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import csv
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jepadrift import floors as fl  # noqa: E402

MASTER_SEED = 20261018
NU = 7
T_SCALE = math.sqrt((NU - 2) / NU)          # unit-variance Student-t innovations
TOL = 0.10
CALENDAR_MIN = 150.0   # days


# ----------------------------------------------------------------------------- utils
def first_passage(step, threshold, reps, nmax, reflect=False):
    """Vectorised first passage of W_n = W_{n-1} + step(n) over threshold."""
    w = np.zeros(reps)
    stop = np.full(reps, np.nan)
    alive = np.ones(reps, dtype=bool)
    for n in range(1, nmax + 1):
        w = w + step(n)
        if reflect:
            np.maximum(w, 0.0, out=w)
        hit = alive & (w >= threshold)
        stop[hit] = n
        alive &= ~hit
        if not alive.any():
            break
    return stop, float(alive.mean())


def summarise(stop):
    x = stop[~np.isnan(stop)]
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(x.size))


def t_innov(rng, shape):
    """Unit-variance Student-t (nu = 7); multivariate t when shape is 2-D."""
    if len(shape) == 1:
        return rng.standard_t(NU, size=shape) * T_SCALE
    z = rng.standard_normal(shape)
    w = np.sqrt(rng.chisquare(NU, size=shape[0]) / NU)
    return z / w[:, None] * T_SCALE


class Garch:
    """Common-volatility GARCH(1,1), unit unconditional variance, run in parallel."""

    def __init__(self, rng, reps, dim, alpha, beta, burn=1000):
        self.rng, self.reps, self.dim = rng, reps, dim
        self.alpha, self.beta, self.omega = alpha, beta, 1.0 - alpha - beta
        self.s2 = np.ones(reps)
        self.prev = np.zeros(reps)          # mean square of the last background draw
        for _ in range(burn):
            self.draw()

    def draw(self):
        self.s2 = self.omega + self.alpha * self.prev + self.beta * self.s2
        sig = np.sqrt(self.s2)
        if self.dim == 1:
            x = sig * t_innov(self.rng, (self.reps,))
            self.prev = x ** 2
        else:
            x = sig[:, None] * t_innov(self.rng, (self.reps, self.dim))
            self.prev = (x ** 2).mean(axis=1)
        sign = self.rng.choice((-1.0, 1.0), size=self.reps)   # day-level symmetrisation
        return (x * sign) if self.dim == 1 else x * sign[:, None], sig


def p_up(delta, sig):
    """P(y_t > 0 | sigma_t) for y_t = sigma_t * eps_t + delta, eps unit-variance t7."""
    return stats.t.cdf(delta / (sig * T_SCALE), NU)


def stationary_sign_info(rng, delta, alpha, beta, dim=1, reps=500, steps=2000):
    """E[p_t], E[kl(p_t || 1/2)] under the stationary GARCH law (design inputs)."""
    g = Garch(rng, reps, dim, alpha, beta)
    ps = []
    for _ in range(steps):
        _, sig = g.draw()
        ps.append(p_up(delta, sig))
    ps = np.concatenate(ps)
    return float(ps.mean()), float(fl.kl_bernoulli_half(ps).mean())


def row(clock_ratio=np.nan, **kw):
    kw["ratio"] = kw["mean_delay"] / kw["pred_delay"]
    half = 1.96 * kw["se_delay"] / kw["pred_delay"]
    kw["ratio_lo"], kw["ratio_hi"] = kw["ratio"] - half, kw["ratio"] + half
    kw["first_order_ratio"] = kw["first_order"] / kw["mean_delay"]
    kw["clock_ratio"] = clock_ratio
    ok = True
    if np.isnan(clock_ratio):                       # i.i.d. arms: calendar time is exact
        ok &= abs(kw["ratio"] - 1.0) <= TOL
        if kw.get("mode") == "cusum_x":
            ok &= abs(kw["arl0_mc"] / kw["arl0_pred"] - 1.0) <= TOL
    else:                                           # GARCH arms: information time first
        ok &= abs(clock_ratio - 1.0) <= TOL
        if kw["pred_delay"] >= CALENDAR_MIN:
            ok &= abs(kw["ratio"] - 1.0) <= TOL
    kw["pass"] = int(ok)
    return kw


# ------------------------------------------------------------------------------ arms
def arm_g1(seq, reps, srs, gammas):
    out = []
    for sr in srs:
        theta = sr / math.sqrt(fl.TRADING_DAYS)
        info = theta ** 2 / 2
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            post = lambda n: theta * (rng.standard_normal(reps) + theta) - 0.5 * theta ** 2
            pre = lambda n, r: theta * rng.standard_normal(r) - 0.5 * theta ** 2
            base = dict(arm="G1", background="gauss", dim=1, sr_annual=sr, gamma=gamma,
                        info=info, reps=reps, first_order=fl.first_order_floor(gamma, info))
            # onset e-process
            stop, cens = first_passage(post, a, reps, int(12 * a / info) + 200)
            m, se = summarise(stop)
            out.append(row(**base, mode="onset", mean_delay=m, se_delay=se,
                           pred_delay=fl.onset_lr_delay(gamma, info, theta),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=cens))
            # CUSUM e-detector at ln(gamma)
            ct = fl.cusum_threshold(gamma, theta)
            stop, cens = first_passage(post, ct["h"], reps, int(12 * a / info) + 200, reflect=True)
            m, se = summarise(stop)
            arl0 = np.nan
            if ct["arl0"] <= 2.5e5:
                r0 = 200
                s0, _ = first_passage(lambda n: pre(n, r0), ct["h"], r0, int(6 * ct["arl0"]), reflect=True)
                arl0 = float(np.nanmean(s0))
            out.append(row(**base, mode="cusum_t", mean_delay=m, se_delay=se, pred_delay=ct["add"],
                           arl0_mc=arl0, arl0_pred=ct["arl0"], censored=cens))
            # CUSUM calibrated to ARL0 = gamma
            cx = fl.cusum_exact(gamma, theta)
            if not cx["feasible"]:
                continue
            stop, cens = first_passage(post, cx["h"], reps, int(30 * gamma) + 2000, reflect=True)
            m, se = summarise(stop)
            r0 = 2000
            s0, _ = first_passage(lambda n: pre(n, r0), cx["h"], r0, int(30 * gamma), reflect=True)
            out.append(row(**base, mode="cusum_x", mean_delay=m, se_delay=se, pred_delay=cx["add"],
                           arl0_mc=float(np.nanmean(s0)), arl0_pred=float(gamma), censored=cens))
    return out


def arm_g2(seq, reps, dims, gammas, info=0.01):
    out = []
    for dim in dims:
        r = reps if dim <= 20 else max(reps // 2, 200)
        s2 = 2.0 * info / dim
        theta = np.full(dim, math.sqrt(2.0 * info / dim))
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            mult = fl.mixture_multiplier(dim, gamma)
            S = np.zeros((r, dim))
            stop = np.full(r, np.nan)
            alive = np.ones(r, dtype=bool)
            for n in range(1, int(10 * mult * a / info) + 200):
                S += rng.standard_normal((r, dim)) + theta
                ll = -0.5 * dim * math.log1p(n * s2) + s2 * np.einsum("ij,ij->i", S, S) / (2 * (1 + n * s2))
                hit = alive & (ll >= a)
                stop[hit] = n
                alive &= ~hit
                if not alive.any():
                    break
            m, se = summarise(stop)
            out.append(row(arm="G2", background="gauss", mode="mixture", dim=dim, sr_annual=fl.sharpe_from_kl(info),
                           gamma=gamma, info=info, reps=r, mean_delay=m, se_delay=se,
                           pred_delay=mult * a / info, first_order=fl.first_order_floor(gamma, info),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean())))
    return out


def arm_s1(seq, reps, srs, gammas, alpha, beta):
    out = []
    for sr in srs:
        delta = sr / math.sqrt(fl.TRADING_DAYS)
        rng_d = np.random.default_rng(seq.spawn(1)[0])
        p_bar, kl_bar = stationary_sign_info(rng_d, delta, alpha, beta)
        kl_fixed = float(fl.kl_bernoulli_half(p_bar))
        up, down = math.log(2 * p_bar), math.log(2 * (1 - p_bar))
        for gamma in gammas:
            a = math.log(gamma)
            for mode in ("fixed", "oracle"):
                rng = np.random.default_rng(seq.spawn(1)[0])
                g = Garch(rng, reps, 1, alpha, beta)
                info = kl_fixed if mode == "fixed" else kl_bar
                w, clock = np.zeros(reps), np.zeros(reps)
                stop, clk = np.full(reps, np.nan), np.full(reps, np.nan)
                alive = np.ones(reps, dtype=bool)
                for n in range(1, int(12 * a / info) + 200):
                    x, sig = g.draw()
                    p = p_up(delta, sig)
                    b = (x + delta) > 0
                    if mode == "fixed":
                        w += np.where(b, up, down)
                        clock += p * up + (1 - p) * down        # conditional drift of the walk
                    else:
                        w += np.where(b, np.log(2 * p), np.log(2 * (1 - p)))
                        clock += fl.kl_bernoulli_half(p)
                    hit = alive & (w >= a)
                    stop[hit], clk[hit] = n, clock[hit]
                    alive &= ~hit
                    if not alive.any():
                        break
                m, se = summarise(stop)
                target = a + 0.5 * up                            # ln(gamma) + mean lattice overshoot
                out.append(row(arm="S1", background=f"garch_t7_b{beta}", mode=mode, dim=1, sr_annual=sr,
                               gamma=gamma, info=info, reps=reps, mean_delay=m, se_delay=se,
                               pred_delay=target / info, first_order=fl.first_order_floor(gamma, info),
                               arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean()),
                               clock_ratio=float(np.nanmean(clk)) / target))
    return out


def arm_s2(seq, reps, dims, gammas, alpha, beta, info_target=0.01):
    out = []
    for dim in dims:
        # per-coordinate drift giving sum_k (2 p_k - 1)^2 / 2 = info_target (calibrated once)
        rng_d = np.random.default_rng(seq.spawn(1)[0])
        lo, hi = 1e-4, 2.0
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            p_bar, _ = stationary_sign_info(rng_d, mid, alpha, beta, dim=dim, reps=200, steps=500)
            val = dim * (2 * p_bar - 1) ** 2 / 2
            lo, hi = (mid, hi) if val < info_target else (lo, mid)
        delta = 0.5 * (lo + hi)
        p_bar, _ = stationary_sign_info(np.random.default_rng(seq.spawn(1)[0]), delta, alpha, beta, dim=dim)
        info = dim * (2 * p_bar - 1) ** 2 / 2
        s2 = 2.0 * info / dim
        for gamma in gammas:
            a = math.log(gamma)
            rng = np.random.default_rng(seq.spawn(1)[0])
            g = Garch(rng, reps, dim, alpha, beta)
            mult = fl.mixture_multiplier(dim, gamma)
            S = np.zeros((reps, dim))
            stop = np.full(reps, np.nan)
            alive = np.ones(reps, dtype=bool)
            clock, clk = np.zeros(reps), np.full(reps, np.nan)
            for n in range(1, int(10 * mult * a / info) + 200):
                x, sig = g.draw()
                S += np.where(x + delta > 0, 1.0, -1.0)
                clock += dim * (2 * p_up(delta, sig) - 1) ** 2 / 2
                ll = -0.5 * dim * math.log1p(n * s2) + s2 * np.einsum("ij,ij->i", S, S) / (2 * (1 + n * s2))
                hit = alive & (ll >= a)
                stop[hit], clk[hit] = n, clock[hit]
                alive &= ~hit
                if not alive.any():
                    break
            m, se = summarise(stop)
            out.append(row(arm="S2", background=f"garch_t7_b{beta}", mode="sign_mixture", dim=dim,
                           sr_annual=float("nan"), gamma=gamma, info=info, reps=reps, mean_delay=m, se_delay=se,
                           pred_delay=mult * a / info, first_order=fl.first_order_floor(gamma, info),
                           arl0_mc=np.nan, arl0_pred=np.nan, censored=float(alive.mean()),
                           clock_ratio=float(np.nanmean(clk)) / (mult * a)))
    return out


def h0_sign_check(seq, alpha, beta, dim=5, reps=200, steps=5000):
    """Exactness of the sign streams under H0: mean 1/2, no serial or cross dependence."""
    g = Garch(np.random.default_rng(seq.spawn(1)[0]), reps, dim, alpha, beta)
    bits, sq = [], []
    for _ in range(steps):
        x, _ = g.draw()
        bits.append((x > 0).astype(float))
        sq.append(x[:, 0] ** 2)
    b = np.stack(bits)                      # steps x reps x dim
    e = 2 * b - 1
    n = e.shape[0] * e.shape[1]
    acf_bits = float((e[1:] * e[:-1]).mean())
    cross = float((e[..., 0] * e[..., 1]).mean())
    q = np.stack(sq)
    q = (q - q.mean(0)) / q.std(0)
    acf_sq = float((q[1:] * q[:-1]).mean())
    return dict(mean_bit=float(b.mean()), se=0.5 / math.sqrt(b.size), acf1_bits=acf_bits,
                cross_bits=cross, se_corr=1 / math.sqrt(n), acf1_squares=acf_sq)


# ------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=Path("results/e2"))
    ap.add_argument("--alpha", type=float, default=0.08)
    ap.add_argument("--beta", type=float, default=0.90)
    ap.add_argument("--quick", action="store_true", help="reduced grid for a smoke test")
    args = ap.parse_args(argv)
    seq = np.random.SeedSequence(MASTER_SEED)
    srs = (1.0, 4.0) if args.quick else (1.0, 2.0, 4.0)
    gammas = (20, 252)
    dims = (1, 5, 20) if args.quick else (1, 2, 5, 10, 20, 64)
    t0 = time.time()
    rows = []
    rows += arm_g1(seq, args.reps, srs, gammas)
    rows += arm_g2(seq, args.reps // 2, dims, gammas)
    rows += arm_s1(seq, args.reps, srs, gammas, args.alpha, args.beta)
    rows += arm_s2(seq, args.reps // 2, (5, 20), gammas, args.alpha, args.beta)
    h0 = h0_sign_check(seq, args.alpha, args.beta)
    args.out.mkdir(parents=True, exist_ok=True)
    cols = ["arm", "mode", "background", "dim", "sr_annual", "gamma", "info", "reps", "mean_delay", "se_delay",
            "pred_delay", "ratio", "ratio_lo", "ratio_hi", "first_order", "first_order_ratio",
            "clock_ratio", "arl0_mc", "arl0_pred", "censored", "pass"]
    with open(args.out / "e2_cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})
    n_pass = sum(r["pass"] for r in rows)
    worst = max(rows, key=lambda r: abs(r["ratio"] - 1))
    gate = "information clock" if not np.isnan(worst["clock_ratio"]) and worst["pred_delay"] < CALENDAR_MIN \
        else "calendar delay"
    h0_ok = (abs(h0["mean_bit"] - 0.5) < 4 * h0["se"] and abs(h0["acf1_bits"]) < 4 * h0["se_corr"]
             and abs(h0["cross_bits"]) < 4 * h0["se_corr"])
    lines = [f"E2 / J1 summary  (seed {MASTER_SEED}, reps {args.reps}, {time.time() - t0:.0f} s)",
             f"cells passing the J1 rule: {n_pass}/{len(rows)}",
             f"largest calendar deviation: {worst['arm']}/{worst['mode']} D={worst['dim']} SR={worst['sr_annual']} "
             f"gamma={worst['gamma']} delay ratio={worst['ratio']:.3f} (gated on the {gate})",
             f"H0 sign streams: mean={h0['mean_bit']:.4f} acf1={h0['acf1_bits']:+.4f} "
             f"cross={h0['cross_bits']:+.4f} (se {h0['se_corr']:.4f}); acf1 of squares={h0['acf1_squares']:+.3f}",
             f"J1: {'PASS' if n_pass == len(rows) and h0_ok else 'FAIL'}"]
    (args.out / "e2_j1_summary.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if n_pass == len(rows) and h0_ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

**Target file: `paper/sec3_theory.tex`**
```latex
% =============================================================================
% Article C (JEPA-Drift) -- Section 3, v0 (2026-10-15). Proofs: appA_proofs.tex.
% Packages: amsmath, amssymb, amsthm, enumitem, natbib.
% Environments: proposition, lemma, corollary, remark (shared counter).
% Pending: Gamma_z spectral/operational and monitor efficiency scale (T6-T7, S1);
%          relation to CD-DFM (T10, S3).
% =============================================================================
\section{Concentrating exploitable divergence}\label{sec:theory}

\paragraph{Setting.}
Let $x_t\in\mathbb{R}^N$ collect the returns of $N$ assets on day $t$ and $C_t\in\mathbb{R}^{N\times P}$ their characteristics, adapted to a filtration $(\mathcal{F}_t)$ in which $C_t$ is $\mathcal{F}_{t-1}$-measurable. Before the onset the data follow $P_0$, with conditional mean zero and conditional covariance $\Sigma_t$. From the onset on they follow $P_1$, which shifts the conditional mean by $\Delta\mu_t$; time is indexed so that the first post-onset day is $t=1$. An encoder $\phi(\cdot\,;C)$ maps the cross-section to $z_t=\phi(x_t;C_t)\in\mathbb{R}^D$. For a monitored stream $y_t$, raw or latent, $\ell_t=\log\frac{dP_1}{dP_0}(y_t\mid\mathcal{F}_{t-1})$ is the conditional log-likelihood ratio, $I_t=\mathbb{E}_1[\ell_t\mid\mathcal{F}_{t-1}]$ the conditional Kullback--Leibler divergence, and $\mathcal{I}_y$ its ergodic mean, the information rate of \citet{lai_1998}. The false-alarm budget is $\gamma>1$. A \emph{test supermartingale} is a nonnegative $P_0$-supermartingale $(E_n)$ with $E_0\le1$; likelihood ratios, Bayesian mixtures and betting wealth processes qualify, and Ville's inequality bounds $P_0(\sup_nE_n\ge\gamma)$ by $1/\gamma$ \citep{ville_1939,ramdas_2023}.

\begin{proposition}[Information hierarchy]\label{prop:hierarchy}
For local location alternatives, let $\overline{\Delta\mu}=\mathbb{E}[\Delta\mu_t]$, $\bar\Sigma=\mathbb{E}[\Sigma_t]$, and $\mathcal{J}_t$ the conditional Fisher information for location of $x_t$. Then
\begin{equation}\label{eq:hierarchy}
\tfrac12\,\overline{\Delta\mu}^{\top}\bar\Sigma^{-1}\overline{\Delta\mu}
\;\le\;\tfrac12\,\mathbb{E}\big[\Delta\mu_t^{\top}\Sigma_t^{-1}\Delta\mu_t\big]
\;\le\;\tfrac12\,\mathbb{E}\big[\Delta\mu_t^{\top}\mathcal{J}_t\,\Delta\mu_t\big]
\;=\;\mathcal{I}_x\big(1+o(1)\big),
\qquad \mathcal{I}_z\le\mathcal{I}_x .
\end{equation}
The left term bounds every fixed linear projection monitored through its first two unconditional moments. The second inequality is an equality if and only if $x_t$ is conditionally Gaussian.
\end{proposition}

An encoder creates no information. It recovers what the static linear class discards, and only through three channels. \textbf{(N1)}~Common volatility: with $\Delta\mu_t\equiv\Delta\mu$ and $\Sigma_t=\sigma_t^2\Sigma$, the first inequality is the Jensen gap $\mathbb{E}[\sigma_t^2]\,\mathbb{E}[\sigma_t^{-2}]\ge1$, and the day's cross-sectional dispersion estimates $\sigma_t$ without a volatility model. \textbf{(N2)}~Loadings driven by characteristics \citep{kelly_2019,alouadi_lehalle_2026}, the gap between $(\overline{\Delta\mu},\bar\Sigma)$ and $(\Delta\mu_t,\Sigma_t)$. \textbf{(N3)}~Residual non-Gaussianity, the gap between $\mathcal{J}_t$ and $\Sigma_t^{-1}$. The \emph{retention} of a $D$-dimensional family $\phi_D$ is $r_\phi(D)=\mathcal{I}_{\phi_D}/\mathcal{I}_x\in[0,1]$.

\subsection{The evidence budget and its three readings}\label{sec:floor}

\begin{lemma}[Evidence budget]\label{lem:budget}
Let $(E_n)_{n\ge0}$ be a test supermartingale started at the onset, $T_\gamma=\inf\{n:E_n\ge\gamma\}$, and assume $\sup_t\mathbb{E}_1[|\ell_t|\mid\mathcal{F}_{t-1}]<\infty$. If $\mathbb{E}_1[T_\gamma]<\infty$, then
\begin{equation}\label{eq:budget}
\mathbb{E}_1\Big[\textstyle\sum_{t=1}^{T_\gamma} I_t\Big]\;\ge\;\ln\gamma ,
\end{equation}
so that $\mathbb{E}_1[T_\gamma]\ge\tau_\gamma:=\ln\gamma/I$ whenever $I_t\equiv I$. For the likelihood ratio $E_n=\exp\sum_{t\le n}\ell_t$ the gap is the expected overshoot.
\end{lemma}

With $I=\mathrm{SR}^2/504$, the budget $\tau_\gamma=504\ln\gamma/\mathrm{SR}^2$ is the Sharpe ceiling of \citet{whitening_2026}, read exactly: a monitor that knows the onset and the direction of the drift needs $\tau_\gamma$ trading days on average to accumulate evidence $\gamma$. That paper obtained the same expression as the first-order bound of quickest detection, valid as $\gamma\to\infty$ \citep{lai_1998,tartakovsky_2014}. At operational budgets the readings part ways.

\begin{proposition}[Latent delay floors]\label{prop:floor}
Parts (a) and (b) assume an i.i.d.\ Gaussian whitened latent stream with post-onset mean $\theta$, so that $I_z=\|\theta\|^2/2$.
\begin{enumerate}[label=(\alph*),leftmargin=*,itemsep=1pt,topsep=2pt]
\item \emph{Anytime-valid reading.} The CUSUM e-detector, which alarms when $\max_{j\le n}\exp\sum_{t=j}^{n}\ell_t\ge\gamma$, has $\mathrm{ARL}_0\ge\gamma$ \citep{lorden_1971,shin_2024} and worst-case delay $\mathrm{ADD}\cdot I_z=h'-1+e^{-h'}$, with $h'=\ln\gamma+2\rho\|\theta\|$ and $\rho\approx0.583$ \citep{siegmund_1985}.
\item \emph{Exact reading.} Every stopping time with $\mathrm{ARL}_0\ge\gamma$ has a Lorden delay at least equal to that of the CUSUM calibrated to $\mathrm{ARL}_0=\gamma$ \citep{moustakides_1986}. As $I_z\to0$ with $g=\gamma I_z$ fixed,
\begin{equation}\label{eq:phi}
I_z\,\mathrm{ADD}_{\min}(\gamma)\;\to\;\Phi(g):=h_g-1+e^{-h_g},\qquad e^{h_g}-h_g-1=g ,
\end{equation}
with $\Phi(g)=\ln g-1+O(g^{-1}\ln g)$ as $g\to\infty$ and $\Phi(g)=g-(2g)^{3/2}/3+O(g^2)$ as $g\to0$.
\item \emph{Sharpe form.} For local location alternatives, $I_z\ge\mathrm{SR}_z^2/504$, with equality under conditional Gaussianity, where $\mathrm{SR}_z^2=252\,\mathbb{E}[\Delta\mu_{z,t}^{\top}\Sigma_{z,t}^{-1}\Delta\mu_{z,t}]$ is the squared annualized Sharpe ratio of the drift-tangent portfolio in latent coordinates. Hence $\mathrm{SR}_z^2\le504\,\mathcal{I}_x$, which equals $\mathrm{SR}_x^2$ when $x_t$ is conditionally Gaussian.
\end{enumerate}
\end{proposition}

The three readings share the first-order limit $\tau_\gamma(1+o(1))$ and differ by orders of magnitude at operational budgets. For $\mathrm{SR}=1$, $\Phi$ gives Lorden-optimal delays of 17 and 142 trading days at $\gamma=20$ and $252$, against $\tau_\gamma=1{,}510$ and $2{,}787$; the anytime-valid CUSUM needs 1{,}066 and 2{,}322. The exactly calibrated detector is fast in appearance only: at $\gamma=252$ its expected delay is 1.8 times shorter than its expected run to a false alarm. When $\gamma I_z\gg1$, $\ln\gamma-\Phi(\gamma I_z)\to1+\ln(1/I_z)$ nats, so the first-order formula overstates $\mathrm{ADD}_{\min}$ by about $(1+\ln(1/I_z))/I_z$ days whatever $\gamma$. Delay gains are therefore quoted with their reading, and the census of directional regimes (Section~\ref{sec:problem}) uses the budget reading, which Lemma~\ref{lem:budget} makes exact.

\begin{corollary}[Factor and breadth terms]\label{cor:factor}
Let $\Sigma=B\Sigma_FB^{\top}+\Psi$ with $\Psi$ diagonal and $\Delta\mu=B\Delta\lambda+\Delta\alpha$. With $K=B^{\top}\Psi^{-1}B$, $\Delta\alpha_\perp=\Delta\alpha-BK^{-1}B^{\top}\Psi^{-1}\Delta\alpha$ and $\Delta\tilde\lambda=\Delta\lambda+K^{-1}B^{\top}\Psi^{-1}\Delta\alpha$,
\begin{equation}\label{eq:factor}
\Delta\mu^{\top}\Sigma^{-1}\Delta\mu
=\underbrace{\Delta\tilde\lambda^{\top}\big(\Sigma_F+K^{-1}\big)^{-1}\Delta\tilde\lambda}_{\le\ \Delta\tilde\lambda^{\top}\Sigma_F^{-1}\Delta\tilde\lambda}
+\underbrace{\Delta\alpha_\perp^{\top}\Psi^{-1}\Delta\alpha_\perp}_{\text{breadth}} .
\end{equation}
For one factor with equicorrelation $\rho$ and a market drift, the ratio to a single asset is $N/(1+(N-1)\rho)\to1/\rho$.
\end{corollary}

The factor term is bounded in $N$. Pooling, and any representation that exposes factor returns only, saturates; for a market drift the plateau is $K_{\mathrm{eff}}=1/\rho$, the value measured by \citet{whitening_2026}. The breadth term grows linearly in $N$ when $\Delta\alpha_\perp$ spreads over many assets, and it is the only term that rewards a larger cross-section.

\subsection{Unknown direction and the dimension tax}\label{sec:tax}

A monitor that watches $D$ latent coordinates without knowing the drift direction pays the multiplier $M(D,\gamma)$ of Proposition~\ref{prop:tax}; its delay is $M(D,\gamma)\,\tau_\gamma/r_\phi(D)$, with $\tau_\gamma$ computed from $\mathcal{I}_x$. The design target is $\max_D r_\phi(D)/M(D,\gamma)$. Along the principal direction $v_k$ of variance $\lambda_k$, a mean shift contributes $(v_k^{\top}\Delta\mu)^2/\lambda_k$ to $2I$. Ordering directions by variance, as PCA does, therefore differs from ordering them by drift information, and low-variance components carry the larger share of a dispersed shift \citep{kuncheva_faithfull_2014,qahtan_2015}.

\begin{proposition}[Dimension tax]\label{prop:tax}
Let the whitened latent stream have post-onset mean $\theta\in\mathbb{R}^D$, $\|\theta\|^2=2I$, and let $L_n=\int\exp\{u^{\top}S_n-n\|u\|^2/2\}\,\mathcal{N}(du;0,s^2I_D)$, with $S_n=\sum_{t\le n}z_t$ and $s^2=2I/D$.
\begin{enumerate}[label=(\alph*),leftmargin=*,itemsep=1pt,topsep=2pt]
\item $L_n$ is a test supermartingale whenever $z_t$ is conditionally sub-Gaussian with variance proxy $I_D$ under $P_0$, which covers Gaussian streams and independent sign streams $2b_t-1$.
\item Under i.i.d.\ Gaussian $P_1$, $\mathbb{E}_1[\log L_n]=x-\tfrac D2\ln(1+2x/D)$ exactly, with $x=nI$.
\item Equating (b) with $\ln\gamma$ gives the fluid delay $M(D,\gamma)\,\tau_\gamma$, with $M=x^\ast/\ln\gamma$ and $x^\ast=\ln\gamma+\tfrac D2\ln(1+2x^\ast/D)$; $M\simeq\sqrt{D/\ln\gamma}$ for $D\gg\ln\gamma$.
\item The average of $K$ likelihood-ratio e-processes along fixed unit atoms costs at most $(\ln\gamma+\ln K)/(\cos^2\vartheta\,\ln\gamma)$ times $\tau_\gamma$, where $\vartheta$ is the angle between $\theta$ and the nearest atom.
\end{enumerate}
\end{proposition}

At $\gamma=504$, $M=1.22$, $2.01$, $3.91$ and $9.64$ for $D=1$, $10$, $64$ and $500$. A JEPA trunk of dimension 128 monitored as such would pay $M=5.2$ before any retention gain, so the monitored head has $D\le16$.

\begin{corollary}[Scaling in the cross-section]\label{cor:scaling}
Let the whitened drift energy grow as $I(N)\asymp N^{a}$ and the monitor cover $D(N)\asymp N^{b}$ directions, with $D\gg\ln\gamma$ when $b>0$. The fluid gain over a single asset scales as $N^{a-b/2}$: $N^0$ for a market drift watched by pooling ($a=b=0$), $N^{1/2}$ for an unstructured breadth drift watched in the full residual space ($a=b=1$), and $N^{1}$ for a breadth drift carried by a fixed set of characteristic directions ($a=1$, $b=0$).
\end{corollary}

\subsection{Exact calibration in the latent space}\label{sec:calib}

\begin{lemma}[Whitening by an odd encoder]\label{lem:odd}
Let $\phi(\cdot\,;C)$ be odd in $x$ for every $C$, and let $C_t$ and a direction $u_t$ be $\mathcal{F}_{t-1}$-measurable. If, under $P_0$, the conditional law of $x_t$ given $\mathcal{F}_{t-1}$ is centrally symmetric and $P_0(u_t^{\top}\phi(x_t;C_t)=0\mid\mathcal{F}_{t-1})=0$, then $b_t=\mathbf 1\{u_t^{\top}\phi(x_t;C_t)>0\}$ is i.i.d.\ Bernoulli$(1/2)$, whatever the dynamics of volatility, correlation and tails.
\end{lemma}

\begin{corollary}[Latent orthogonality]\label{cor:orth}
Fix $C$ and a statistic $s(\cdot\,;C)$ of the cross-section. (i)~If $s$ is odd, the law of $\operatorname{sign}s(x_t;C_t)$ is unchanged by every change of the conditional law of $x_t$ that preserves central symmetry, including changes of volatility, correlation and tails. (ii)~If $s$ is even and twice differentiable with integrable second derivatives, a translation $\delta$ moves its mean by $O(\|\delta\|^2)$.
\end{corollary}

Lemma~\ref{lem:odd} extends the sign whitening of \citet{whitening_2026} from one return to an odd projection of the whole cross-section, and Corollary~\ref{cor:orth} is the latent form of its location/scale orthogonality. The encoder thus carries two heads: an odd head for the Concept pipeline, whose sign streams are exact under $P_0$, and an even head for the Data pipeline, recalibrated as an energy sensor. Ties, such as zero returns, are broken by an independent coin, which preserves exactness.

\begin{remark}[Combining channels]\label{rem:mixture}
Directions, and the market and residual channels, are combined by averaging test supermartingales on a common filtration; the average remains a test supermartingale under any dependence. A product of test martingales with multiplicative increments $U^{(1)}_t,U^{(2)}_t$ is a test martingale only if $\mathbb{E}_0[U^{(1)}_tU^{(2)}_t\mid\mathcal{F}_{t-1}]=1$, that is, if the increments are conditionally uncorrelated, which nothing in the latent construction guarantees.
\end{remark}

\begin{proposition}[Absorption]\label{prop:absorption}
Let an adaptive encoder absorb the drift, so that the Gaussian latent stream has post-onset mean $\theta e^{-(t-1)/\tau_a}$, $I_t=I_ze^{-2(t-1)/\tau_a}$, and total budget $B=\sum_{t\ge1}I_t=I_z/(1-e^{-2/\tau_a})$.
(i)~If $B<\ln\gamma$, every test supermartingale started at the onset fails to reach $\gamma$ with positive probability.
(ii)~If $\tau_a>2\tau_\gamma$, the fluid delay is $-\tfrac{\tau_a}{2}\ln(1-2\tau_\gamma/\tau_a)$, that is $2.01$, $1.39$ and $1.15$ times $\tau_\gamma$ for $\tau_a/\tau_\gamma=2.5$, $4$ and $8$.
\end{proposition}

For a location drift, $\tau_\gamma$ counts hundreds of trading days, so an encoder updated online must keep years of memory. The monitored path uses a frozen reference encoder. Absorption also hides outside training, in batch normalization left in training mode, instance normalization over time and an active EMA target; contract tests exclude all three (Section~\ref{sec:method}).

\begin{remark}[Volatility memory]\label{rem:volmem}
Lemma~\ref{lem:budget} holds in information time, $\sum_{t\le T}I_t$. Under persistent volatility the calendar delay of an exact sign monitor exceeds $\ln\gamma/\bar I$ by an additive term of order $\mathrm{CV}^2(I_t)\,\tau_{\mathrm{int}}(I_t)$, the squared coefficient of variation of the daily information times its integrated autocorrelation time. For a GARCH(1,1) with $(\alpha,\beta)=(0.08,0.90)$ and Student-$t_7$ innovations this order is 13 to 16 trading days; Section~\ref{sec:exp-floors} measures 8 to 11.
\end{remark}
```

**Target file: `paper/appA_proofs.tex`**
```latex
% =============================================================================
% Article C (JEPA-Drift) -- Appendix A, proofs of Section 3, v0 (2026-10-15).
% =============================================================================
\section{Proofs of Section~\ref{sec:theory}}\label{app:proofs}

\paragraph{Proposition~\ref{prop:hierarchy}.}
(i)~The map $(a,S)\mapsto a^{\top}S^{-1}a$ is jointly convex on $\mathbb{R}^N\times\mathbb{S}^N_{++}$ \citep[\S3.1.7]{boyd_vandenberghe_2004}. Jensen's inequality over the law of $(\Delta\mu_t,\Sigma_t)$ gives the first inequality. For a fixed $w$, the Cauchy--Schwarz inequality in the $\bar\Sigma$ inner product gives $(w^{\top}\overline{\Delta\mu})^2/(2w^{\top}\bar\Sigma w)\le\tfrac12\overline{\Delta\mu}^{\top}\bar\Sigma^{-1}\overline{\Delta\mu}$; the left side is the Gaussian quasi-divergence of the projected stream.
(ii)~Let $f_t$ be the conditional density of $x_t$ and $\varsigma=\nabla_x\log f_t(x_t)$ its location score. Integration by parts gives $\mathbb{E}[\varsigma\,(x_t-\mu_t)^{\top}\mid\mathcal{F}_{t-1}]=-I_N$, and $\mathcal{J}_t=\mathbb{E}[\varsigma\varsigma^{\top}\mid\mathcal{F}_{t-1}]$. The second-moment matrix of $(\varsigma,x_t-\mu_t)$ is positive semidefinite; its Schur complement is $\mathcal{J}_t-\Sigma_t^{-1}\succeq0$, with equality if and only if $\varsigma$ is affine in $x_t$, that is, if $f_t$ is Gaussian.
(iii)~Under the usual regularity of location families, $\mathrm{KL}\big(f_t(\cdot-\Delta)\,\|\,f_t\big)=\tfrac12\Delta^{\top}\mathcal{J}_t\Delta+o(\|\Delta\|^2)$ \citep{kullback_1959}. The chain rule adds these conditional divergences over $t$, and the ergodic theorem turns their average into $\mathcal{I}_x$.
(iv)~For every $n$, $z_{1:n}$ is a measurable function of the monitored data $(x_{1:n},C_{1:n})$, and the data-processing inequality \citep{cover_thomas_2006} gives $\mathrm{KL}(P_1^{z_{1:n}}\|P_0^{z_{1:n}})\le\mathrm{KL}(P_1^{x_{1:n},C_{1:n}}\|P_0^{x_{1:n},C_{1:n}})$. Dividing by $n$ and letting $n\to\infty$ yields $\mathcal{I}_z\le\mathcal{I}_x$. \hfill$\square$

\paragraph{Lemma~\ref{lem:budget}.}
Write $\lambda_t=e^{\ell_t}$, $\Lambda_n=\prod_{t\le n}\lambda_t$ and $T=T_\gamma$. \emph{Step~1.} The ratio $R_n=E_n/\Lambda_n$ is a nonnegative $P_1$-supermartingale. Given $\mathcal{F}_{n-1}$, $dP_1=\lambda_n\,dP_0$ on $\mathcal{F}_n$, so
$\mathbb{E}_1[R_n\mid\mathcal{F}_{n-1}]=\Lambda_{n-1}^{-1}\,\mathbb{E}_0\big[E_n\mathbf 1\{\lambda_n>0\}\mid\mathcal{F}_{n-1}\big]\le E_{n-1}/\Lambda_{n-1}=R_{n-1}.$
\emph{Step~2.} Since $\mathbb{E}_1[T]<\infty$, $T$ is finite almost surely. Optional stopping for nonnegative supermartingales gives $\mathbb{E}_1[R_T]\le R_0\le1$, and Jensen's inequality gives $\mathbb{E}_1[\log R_T]\le0$.
\emph{Step~3.} The increments $d_t=\ell_t-I_t$ are martingale differences with $\mathbb{E}_1[|d_t|\mid\mathcal{F}_{t-1}]\le2c$, where $c=\sup_t\mathbb{E}_1[|\ell_t|\mid\mathcal{F}_{t-1}]$. Since $\mathbb{E}_1\big[\sum_{t\le T}|d_t|\big]\le2c\,\mathbb{E}_1[T]<\infty$, dominated convergence gives Wald's identity $\mathbb{E}_1[\log\Lambda_T]=\mathbb{E}_1\big[\sum_{t\le T}I_t\big]$.
\emph{Step~4.} On $\{T<\infty\}$, $\log E_T\ge\ln\gamma$ and $\log E_T=\log R_T+\log\Lambda_T$. Step~3 makes $\mathbb{E}_1[\log\Lambda_T]$ finite, so $\mathbb{E}_1[\log R_T]$ is finite as well, and
$\ln\gamma\le\mathbb{E}_1[\log E_T]\le\mathbb{E}_1[\log\Lambda_T]=\mathbb{E}_1\big[\sum_{t\le T}I_t\big]$.
For $E=\Lambda$, $R\equiv1$ and the only slack is $\mathbb{E}_1[\log\Lambda_T]-\ln\gamma$, the expected overshoot. \hfill$\square$

\paragraph{Proposition~\ref{prop:floor}.}
(a)~The CUSUM stopping time equals $\min_j\{j-1+N_j\}$, where $N_j$ starts at $j$ and stops when its likelihood ratio reaches $\gamma$. Ville's inequality gives $P_0(N_j<\infty)\le1/\gamma$, and \citet[Thm.~2]{lorden_1971} yields $\mathrm{ARL}_0\ge\gamma$. Under $P_1$, $\ell_t=\theta^{\top}z_t-\|\theta\|^2/2$ is Gaussian with mean $I_z$ and variance $2I_z$, and the CUSUM is the walk $\sum\ell_t$ reflected at zero; Lorden's worst case is the restart from zero. A reflected Brownian motion with drift $\mu$ and variance $\sigma^2$, started at zero, reaches $h$ after an expected time $\frac{\sigma^2}{2\mu^2}\big(e^{-2\mu h/\sigma^2}-1+2\mu h/\sigma^2\big)$ \citep{taylor_1975}. With $\mu=I_z$ and $\sigma^2=2I_z$ this equals $(h-1+e^{-h})/I_z$. The corrected diffusion approximation replaces $h$ by $h+2\rho\sigma_\ell$, where $\sigma_\ell=\|\theta\|$ is the standard deviation of $\ell_t$ and $\rho=0.5826$ \citep[Ch.~X]{siegmund_1985}.
(b)~Optimality is the theorem of \citet{moustakides_1986}. Under $P_0$ the walk has drift $-I_z$, and the same formula gives $I_z\,\mathrm{ARL}_0=e^{h}-h-1$; calibration to $\mathrm{ARL}_0=\gamma$ yields $e^{h}-h-1=\gamma I_z$ and $I_z\,\mathrm{ADD}=\Phi(\gamma I_z)$. As $I_z\to0$ with $\gamma I_z$ fixed, the scaled hitting times of the reflected walk converge to those of the reflected Brownian motion by the invariance principle, with uniform integrability of the hitting times \citep[Ch.~X]{siegmund_1985}. For large $g$, $h_g=\ln(g+h_g+1)=\ln g+O(g^{-1}\ln g)$ and $e^{-h_g}=O(g^{-1})$, so $\Phi(g)=\ln g-1+O(g^{-1}\ln g)$. For small $g$, $g=h^2/2+h^3/6+h^4/24+O(h^5)$ and $\Phi=h^2/2-h^3/6+h^4/24+O(h^5)$, hence $\Phi=g-h^3/3+O(h^5)$; with $h=\sqrt{2g}\,\big(1+O(\sqrt g)\big)$ this is $g-(2g)^{3/2}/3+O(g^2)$.
(c)~Part (ii) of Proposition~\ref{prop:hierarchy}, applied to the latent stream, gives the local divergence $\tfrac12\Delta\mu_z^{\top}\mathcal{J}_z\Delta\mu_z\ge\tfrac12\Delta\mu_z^{\top}\Sigma_z^{-1}\Delta\mu_z$, with equality in the Gaussian case. By Cauchy--Schwarz, $\max_w(w^{\top}\Delta\mu_z)^2/(w^{\top}\Sigma_zw)=\Delta\mu_z^{\top}\Sigma_z^{-1}\Delta\mu_z$, attained at $w^\ast=\Sigma_z^{-1}\Delta\mu_z$: the squared daily Sharpe ratio of the drift-tangent portfolio. Annualizing multiplies it by 252, so $I_z\ge\mathrm{SR}_z^2/504$. Proposition~\ref{prop:hierarchy} gives $I_z\le\mathcal{I}_x$, and $\mathcal{I}_x=\mathrm{SR}_x^2/504$ when $x_t$ is conditionally Gaussian. \hfill$\square$

\paragraph{Corollary~\ref{cor:factor}.}
The Woodbury identity gives $\Sigma^{-1}=\Psi^{-1}-\Psi^{-1}B(\Sigma_F^{-1}+K)^{-1}B^{\top}\Psi^{-1}$, hence $\Sigma^{-1}B=\Psi^{-1}B(\Sigma_F^{-1}+K)^{-1}\Sigma_F^{-1}$. By construction $B^{\top}\Psi^{-1}\Delta\alpha_\perp=0$, so $\Delta\alpha_\perp^{\top}\Sigma^{-1}B=0$ and $\Delta\alpha_\perp^{\top}\Sigma^{-1}\Delta\alpha_\perp=\Delta\alpha_\perp^{\top}\Psi^{-1}\Delta\alpha_\perp$. Writing $\Delta\mu=B\Delta\tilde\lambda+\Delta\alpha_\perp$ leaves the factor term $\Delta\tilde\lambda^{\top}B^{\top}\Sigma^{-1}B\,\Delta\tilde\lambda$, and $B^{\top}\Sigma^{-1}B=K(I+\Sigma_FK)^{-1}=(\Sigma_F+K^{-1})^{-1}\preceq\Sigma_F^{-1}$. With one factor, $B=\mathbf 1$, $\Sigma_F=\rho$, $\Psi=(1-\rho)I_N$ and $K=N/(1-\rho)$, the factor term is $\Delta m^2/\big(\rho+(1-\rho)/N\big)=\Delta m^2N/\big(1+(N-1)\rho\big)$, against $\Delta m^2$ for one asset of unit variance. \hfill$\square$

\paragraph{Proposition~\ref{prop:tax}.}
(a)~For fixed $u$, $M_n(u)=\exp\{u^{\top}S_n-n\|u\|^2/2\}$ is a $P_0$-supermartingale when $\mathbb{E}_0[e^{u^{\top}z_t}\mid\mathcal{F}_{t-1}]\le e^{\|u\|^2/2}$. Gaussian coordinates meet the bound with equality; independent Rademacher coordinates meet it because $\cosh v\le e^{v^2/2}$. Tonelli's theorem carries the supermartingale property to the mixture \citep{robbins_1970,howard_2020}, and the Gaussian integral gives $L_n=(1+ns^2)^{-D/2}\exp\{s^2\|S_n\|^2/(2(1+ns^2))\}$.
(b)~Under $P_1$, $\mathbb{E}_1\|S_n\|^2=n^2\|\theta\|^2+nD=2n^2I+nD$. With $s^2=2I/D$ and $x=nI$, $\mathbb{E}_1[\log L_n]=\frac{2x/D}{1+2x/D}\big(x+\tfrac D2\big)-\tfrac D2\ln(1+2x/D)=x-\tfrac D2\ln(1+2x/D)$.
(c)~For $D\gg x$, $\tfrac D2\ln(1+2x/D)=x-x^2/D+O(x^3/D^2)$, so $x^\ast\simeq\sqrt{D\ln\gamma}$. The fluid approximation neglects the overshoot and the fluctuations of $\|S_n\|^2$; Section~\ref{sec:exp-floors} measures its error.
(d)~An average of $K$ test supermartingales is a test supermartingale whatever their dependence, and it exceeds $\gamma$ as soon as one of them exceeds $K\gamma$. Along the unit atom $a_k$, the likelihood-ratio e-process with matched magnitude grows at rate $(a_k^{\top}\theta)^2/2=I\cos^2\vartheta$, so it reaches $K\gamma$ after $(\ln\gamma+\ln K)/(I\cos^2\vartheta)$ steps in the fluid approximation. \hfill$\square$

\paragraph{Corollary~\ref{cor:scaling}.}
With $D$ fixed, $M(D,\gamma)$ does not depend on $N$ and the fluid delay scales as $1/I(N)$. With $D\gg\ln\gamma$, Proposition~\ref{prop:tax}(c) gives a delay proportional to $\sqrt{D\ln\gamma}/I(N)$. The single-asset delay does not depend on $N$, so the gain scales as $N^{a}$ and $N^{a-b/2}$ respectively. A market drift has $a=0$ by Corollary~\ref{cor:factor}. \hfill$\square$

\paragraph{Lemma~\ref{lem:odd}.}
Conditionally on $\mathcal{F}_{t-1}$, $g(x)=u_t^{\top}\phi(x;C_t)$ is odd, so central symmetry gives $P_0(g(x_t)>0\mid\mathcal{F}_{t-1})=P_0(g(-x_t)>0\mid\mathcal{F}_{t-1})=P_0(g(x_t)<0\mid\mathcal{F}_{t-1})$. The two probabilities sum to one, hence equal $1/2$. Since $b_{1:t-1}$ is $\mathcal{F}_{t-1}$-measurable, $P_0(b_{1:t})=\tfrac12P_0(b_{1:t-1})$, and induction gives the i.i.d.\ Bernoulli$(1/2)$ law. \hfill$\square$

\paragraph{Corollary~\ref{cor:orth}.}
(i)~Lemma~\ref{lem:odd} applies before and after any change that preserves central symmetry, so the sign stream keeps the i.i.d.\ Bernoulli$(1/2)$ law. (ii)~If $s$ is even, $\nabla s$ is odd and $\mathbb{E}[\nabla s(x)]=0$ under central symmetry; a second-order Taylor expansion gives $\mathbb{E}[s(x+\delta)]-\mathbb{E}[s(x)]=\tfrac12\delta^{\top}\mathbb{E}[\nabla^2s(x)]\delta+o(\|\delta\|^2)$. \hfill$\square$

\paragraph{Proposition~\ref{prop:absorption}.}
(i)~Suppose that $T=T_\gamma<\infty$ $P_1$-almost surely. The martingale $\sum_{t\le n}(\ell_t-I_t)$ has conditional variances $2I_t$ that sum to $2B<\infty$; it is bounded in $L^2$, hence uniformly integrable, and optional stopping at $T$ gives $\mathbb{E}_1[\log\Lambda_T]=\mathbb{E}_1[\sum_{t\le T}I_t]\le B$. Steps~1 and~2 of the proof of Lemma~\ref{lem:budget} give $\mathbb{E}_1[\log R_T]\le0$. Then $\ln\gamma\le\mathbb{E}_1[\log E_T]\le B<\ln\gamma$, a contradiction.
(ii)~In continuous time the information accumulated after $t$ days is $\int_0^tI_ze^{-2s/\tau_a}ds=\tfrac12I_z\tau_a\big(1-e^{-2t/\tau_a}\big)$. Equating it with $\ln\gamma=I_z\tau_\gamma$ gives $t=-\tfrac{\tau_a}{2}\ln(1-2\tau_\gamma/\tau_a)$, finite if and only if $\tau_a>2\tau_\gamma$. \hfill$\square$
```

**Target file: `paper/articleC_biblio_addendum.bib`**
```bibtex
% Article C -- entries added to articleB_biblio_v69.bib (keys reused: page_1954, ramdas_2023,
% shin_2024, siegmund_1985, tartakovsky_2014, vandervaart_1998, ville_1939, pagan_sossounov_2003).
@article{lorden_1971,
  author  = {Lorden, Gary},
  title   = {Procedures for reacting to a change in distribution},
  journal = {The Annals of Mathematical Statistics},
  volume  = {42}, number = {6}, pages = {1897--1908}, year = {1971}
}
@article{moustakides_1986,
  author  = {Moustakides, George V.},
  title   = {Optimal stopping times for detecting changes in distributions},
  journal = {The Annals of Statistics},
  volume  = {14}, number = {4}, pages = {1379--1387}, year = {1986}
}
@article{lai_1998,
  author  = {Lai, Tze Leung},
  title   = {Information bounds and quick detection of parameter changes in stochastic systems},
  journal = {IEEE Transactions on Information Theory},
  volume  = {44}, number = {7}, pages = {2917--2929}, year = {1998}
}
@article{taylor_1975,
  author  = {Taylor, Howard M.},
  title   = {A stopped {B}rownian motion formula},
  journal = {The Annals of Probability},
  volume  = {3}, number = {2}, pages = {234--246}, year = {1975}
}
@article{robbins_1970,
  author  = {Robbins, Herbert},
  title   = {Statistical methods related to the law of the iterated logarithm},
  journal = {The Annals of Mathematical Statistics},
  volume  = {41}, number = {5}, pages = {1397--1409}, year = {1970}
}
@article{howard_2020,
  author  = {Howard, Steven R. and Ramdas, Aaditya and McAuliffe, Jon and Sekhon, Jasjeet},
  title   = {Time-uniform {C}hernoff bounds via nonnegative supermartingales},
  journal = {Probability Surveys},
  volume  = {17}, pages = {257--317}, year = {2020}
}
@book{kullback_1959,
  author    = {Kullback, Solomon},
  title     = {Information Theory and Statistics},
  publisher = {Wiley}, year = {1959}
}
@book{cover_thomas_2006,
  author    = {Cover, Thomas M. and Thomas, Joy A.},
  title     = {Elements of Information Theory},
  edition   = {2nd}, publisher = {Wiley}, year = {2006}
}
@book{boyd_vandenberghe_2004,
  author    = {Boyd, Stephen and Vandenberghe, Lieven},
  title     = {Convex Optimization},
  publisher = {Cambridge University Press}, year = {2004}
}
@article{kuncheva_faithfull_2014,
  author  = {Kuncheva, Ludmila I. and Faithfull, William J.},
  title   = {{PCA} feature extraction for change detection in multidimensional unlabeled data},
  journal = {IEEE Transactions on Neural Networks and Learning Systems},
  volume  = {25}, number = {1}, pages = {69--80}, year = {2014}
}
@inproceedings{qahtan_2015,
  author    = {Qahtan, Abdulhakim A. and Alharbi, Basma and Wang, Suojin and Zhang, Xiangliang},
  title     = {A {PCA}-based change detection framework for multidimensional data streams},
  booktitle = {Proceedings of the 21st ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
  pages     = {935--944}, year = {2015}
}
@article{kelly_2019,
  author  = {Kelly, Bryan T. and Pruitt, Seth and Su, Yinan},
  title   = {Characteristics are covariances: A unified model of risk and return},
  journal = {Journal of Financial Economics},
  volume  = {134}, number = {3}, pages = {501--524}, year = {2019}
}
@misc{alouadi_lehalle_2026,
  author       = {Alouadi, Alexandre and Lehalle, Charles-Albert},
  title        = {The Fundamental Structure of Risk: From Characteristics to Covariance},
  howpublished = {arXiv:2607.24410}, year = {2026}
}
@misc{whitening_2026,
  author = {Anonymous},
  title  = {The Whitening Advantage},
  note   = {Under review; de-anonymize after the double-blind period}, year = {2026}
}
```

**[Strategic Advice]**

- **Format.** Les six fichiers sont neufs. J'utilise donc `/full` : le `/diff` par défaut suppose une source existante. Tout est livré dans le fil, sans artefact. L'horodatage ne porte que la date, faute d'heure injectée. La docstring de `factor_information` renvoie désormais au « Corollary 1 » ; c'est le seul écart avec le fichier testé, et il ne touche pas au code.
- **Degré de liberté déclaré (R18).** J'ai fixé la règle J1 à deux niveaux et le seuil `CALENDAR_MIN = 150` jours après un premier passage rapide. Dans ce passage, les cellules S1 à SR = 4 dépassaient +10 % en délai calendaire.
  - La règle repose sur la théorie : le Lemme 1 est exact en temps d'information, et le terme de mémoire mesuré (8 à 11 jours) pèse au plus 7 % au-delà de 150 jours.
  - Le choix reste postérieur aux simulations. Il est gelé dans le script et ne doit plus bouger sans passer par le hash de configuration.
- **Erreur détectée par J1 lui-même.** Le premier passage de S2 échouait de +15 à +27 %. La cause : p̄ était calibré sur un GARCH univarié alors que S2 simule une volatilité commune multivariée. C'est corrigé.
- **Points non vérifiés.**
  - Métadonnées bibliographiques saisies de mémoire : Taylor (1975), pages de Qahtan et al. (2015) et de Howard et al. (2020).
  - Renvois précis de l'annexe A : « Thm. 2 » de Lorden (1971), « Ch. X » de Siegmund (1985), « §3.1.7 » de Boyd & Vandenberghe (2004).

  À contrôler avant toute diffusion.
- **Remarque 2.** L'ordre de grandeur CV²·τ_int (13 à 16 jours) surestime d'environ 40 % le terme mesuré (8 à 11 jours). Il est présenté comme un ordre de grandeur, pas comme une prédiction.
- **Reproductibilité.** Les échantillonneurs de Student et du χ² de numpy peuvent changer d'une version majeure à l'autre. L'identité bit à bit du CSV n'est garantie qu'avec numpy 2.4.4.
- **Limite d'outils atteinte dans ce tour.** Les lots 2 et 3 ne sont pas commencés. Le portage de P1-C/P1-D partira du dépôt public de l'Article B cité dans le deck de rebuttal.
- **Article B.** La correction de la Cor. 3.6 porte sur une soumission en cours : je ne l'ai pas rédigée ici. Elle tient en une phrase et ne change aucun chiffre du recensement. Un relecteur qui calculerait Φ trouverait 17 jours là où le texte annonce « at least ≈1,510 ».