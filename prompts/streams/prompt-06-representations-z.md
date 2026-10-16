## PROMPT 6 — Représentations linéaires et interface Z (ACP orthogonale, coupe de degré 0, rangs)

### Contexte
Dans JEPA-Drift, toute représentation (ACP, IPCA, CD-DFM, JEPA) se branche sur les moniteurs par une même interface : apprentissage sur la seule fenêtre de calibration, transformation jour par jour, état figé et haché. Les représentations linéaires servent de références et fixent ce contrat avant l'arrivée du JEPA. Bloquant pour J2. Lire `CLAUDE.md`.

### Tâche
1. **Classe de base** `jepadrift/representations/base.py`, `Representation` :
   - `fit(X_fit, C_fit, dates_fit)` ;
   - `transform_day(x_t, C_t) -> {"z_odd": (D,), "z_even": (D',)}` ;
   - `transform_panel(X, C)`, appliquée jour par jour sans aucune opération temporelle ;
   - `state_hash()`, SHA-256 des tableaux d'état ;
   - attribut `odd_head = True` ;
   - `sidecar()`, JSON : empreintes de l'état et des données, dates d'apprentissage, drapeaux impair/pair, statistiques de normalisation figées.
2. **`pca.py`, `PCAOrthogonal(K="mp"|int, mode="factor"|"full"|"tail10", shrinkage="ledoit_wolf"|None)`.**
   - Canal marché : z_mkt = v₁ᵀx/√λ₁.
   - Résiduel factoriel : PC2..PC(K+1), K au bord de Marčenko–Pastur λ₊ = σ²(1 + √(N/T))² sur la corrélation.
   - Résiduel complet : N−1 directions.
   - « tail10 » : composantes des derniers 10 % de variance, pour P3-KF.
   - Toutes les sorties sont blanchies ; la tête paire contient les carrés des coordonnées blanchies.
3. **`cross_section.py`.**
   - `DegreeZero` : z = Uᵀ P x / ‖P x‖, avec P = I − b bᵀ/‖b‖² (b = chargements de PC1 ou vecteur de 1) et U un ensemble de directions résiduelles figé.
   - `CenteredRanks` : r_i − (N+1)/2, divisé par N, ex aequo moyennés. Cette transformation est impaire.
4. **Extraction** `python -m jepadrift.representations.extract --dataset d3_239 --rep pca --mode factor` : écrit `data/derived/<dataset>/z_<state_hash>.npz` (`Z_odd` T×D, `Z_even` T×D', `dates`) et le JSON associé.
5. **Tests** `tests/test_representations.py` :
   - imparité ‖φ(−x) + φ(x)‖_∞ ≤ 1e-12 ;
   - invariance de degré 0, z(c·x) = z(x) pour c > 0 ;
   - perturber la fenêtre de surveillance laisse `state_hash` identique ;
   - D attendu, pas de NaN.

### Entrées
D2 et D3 (`splits.yaml`, `ret_wide.npy`, `chars.parquet`) ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/{base,pca,cross_section,extract}.py`, `tests/test_representations.py`, extractions de référence pour D2 et `d3_239`, `docs/sections/interface_Z.md` (contrat d'interface, versionné).

### Contraintes techniques
- numpy (et scipy pour Ledoit–Wolf si besoin).
- Aucune statistique calculée sur la fenêtre de surveillance.
- Aucun import de `jepadrift.monitors` ou de `jepadrift.injection`.

### Critères de succès
Tests au vert ; deux exécutions donnent des `.npz` identiques au SHA-256 près ; contrat documenté.

### Commandes de vérification
```bash
python -m jepadrift.representations.extract --dataset d2_us97 --rep pca --mode factor
pytest -q tests/test_representations.py
sha256sum data/derived/d2_us97/z_*.npz
```
