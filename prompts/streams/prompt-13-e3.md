## PROMPT 13 — E3 : calibration sous H₀ (exactitude des flux, Γ spectral contre Γ opérationnel)

### Contexte
E3 vérifie, sans aucune dérive, que chaque moniteur de JEPA-Drift tient son taux de fausses alarmes. Les flux de signe sont exacts par construction. Les statistiques à amplitude subissent l'hétéroscédasticité : facteur Γ et pénalité de dépassement. E3 fournit le §5.2 et le premier critère de J2. Lire `CLAUDE.md`.

Définitions :
- **Γ^spec** = 1 + 2Σρ(k) de la statistique surveillée.
- **Γ^op** = λ_requis/λ_iid pour tenir l'ARL₀ visé.

### Tâche
Écrire `experiments/e3_calibration.py` ; fenêtres réelles limitées à 2005–2019.
1. **Fonds.**
   - D5 : GARCH(0.08 ; 0.90) à innovations t₇ et gaussiennes ;
   - D6 : SYM-D2, SYM-`d3_239` ;
   - placebo : D2 et D3 bruts.
2. **Pipelines.**
   - P1-C : flux d'étiquettes centré en q̂, et flux exact centré en 1/2 ;
   - P1-D : règle λ_iid × Γ̂, et seuil opérationnel ;
   - P2-C : CUSUM bootstrap, et e-détecteur de pari ;
   - P3-C, P3-D, P3-CS.
3. **Mesures.**
   - FPR à H ∈ {750, 2000} contre le niveau exact du treillis, pour les CUSUM de signe ;
   - ARL₀ Monte Carlo contre γ, pour les e-détecteurs ;
   - Γ^spec (Bartlett) contre Γ^op, pour chaque statistique à amplitude.
4. **Pénalité de dépassement**, à reproduire à ±5 % avec 2000 trajectoires. CUSUM de premier ordre sur x/σ_inconditionnel, GARCH(0.08 ; 0.90) gaussien :
   - δ = 0.5, λ = 6 : ARL₀ ≈ 2587 en i.i.d. contre ≈ 889 sous GARCH ;
   - δ = 1, λ = 3 : 1894 contre 669 ;
   - CUSUM de signe : 213 contre 214 (exact).
5. **Encodeurs à fenêtre.** z_t = moyenne sur L jours de uᵀx, L ∈ {5, 20, 60}. Montrer :
   - Γ_z^spec ≈ L ;
   - l'explosion du FPR d'un CUSUM calibré en i.i.d. ;
   - le rejet de Ljung–Box (20 retards) sur les signes de z.

   Cela justifie un chemin surveillé jour par jour.
6. **Contrôle J2.** Pour chaque flux de signe exact, |FPR − niveau du treillis| ≤ 1 point, écrit dans `results/e3/e3_j2_check.txt`.

### Entrées
Prompts 4 à 8 ; `CLAUDE.md`.

### Livrables
`experiments/e3_calibration.py`, `configs/e3.yaml`, `results/e3/{e3_cells.csv,e3_overshoot.csv,e3_window_encoders.csv,e3_j2_check.txt}`, `figures/e3/*`.

### Contraintes techniques
Au moins 20 000 trajectoires nulles par cellule de signe ; IC de Wilson ; option `--quick`.

### Critères de succès
Flux exacts dans l'IC du niveau exact ; valeurs de la pénalité reproduites ; contrôle J2 écrit.

### Commandes de vérification
```bash
python experiments/e3_calibration.py --quick --out results/e3_quick
python experiments/e3_calibration.py --out results/e3 && cat results/e3/e3_j2_check.txt
```
