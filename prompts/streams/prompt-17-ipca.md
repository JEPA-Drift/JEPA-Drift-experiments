## PROMPT 17 — IPCA sur caractéristiques tirées des rendements (pipelines P4)

### Contexte
JEPA-Drift compare le JEPA à des facteurs latents pilotés par les caractéristiques. Le premier est l'IPCA (Kelly, Pruitt & Su, 2019) : x_t = C_t Γ f_t + ε_t, avec des chargements C_tΓ connus en t−1. Ses rendements de facteurs sont linéaires en x_t, donc impairs, et leurs flux de signe sont exacts. Lire `CLAUDE.md`.

### Tâche
1. Implémenter dans `jepadrift/representations/ipca.py` l'estimation par moindres carrés alternés :
   - f_t = (ΓᵀC_tᵀC_tΓ)⁻¹ΓᵀC_tᵀx_t, pour Γ donné ;
   - Γ mis à jour par la régression empilée ;
   - normalisation ΓᵀΓ = I, facteurs orthogonaux ;
   - critère d'arrêt sur la variation relative de Γ (≤ 1e-8).
2. Caractéristiques : `data_loader.chars.load_chars_tensor` (stream 8b) ; 15 colonnes sur D3 (4 continues, 11 GICS), 4 sur D4 ; NaN → 0 comptés. `d3_500` et D4 sont déséquilibrés : régressions transversales restreintes aux titres `in_universe` du jour, sans imputation de rendement. Apprendre Γ sur `pretrain` ; choisir K ∈ {1, …, 6} par R² hors échantillon sur `calib` ; blanchir f_t sur `calib`.
3. Option « cash-neutral » : retirer le facteur de marché (constante ou bêta) avant extraction.
4. Enregistrer la représentation et les pipelines P4-C (signes des facteurs, e-détecteur de dictionnaire) et P4-D (énergie).
5. **Tests** :
   - récupération sur données simulées : sous-espace de Γ retrouvé avec des angles principaux < 5° ;
   - imparité ; non-anticipation ; état figé ;
   - contrats du prompt 8.

### Entrées
`d3_239`, `d3_500` (et D4) avec leurs caractéristiques ; interface Z ; stream 8b ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/ipca.py`, `tests/test_ipca.py`, extractions, `results/ipca/k_selection.csv`, `docs/sections/ipca.md`.

### Contraintes techniques
numpy seul ; aucune donnée de `monitor`.

### Critères de succès
Tests au vert ; K choisi et consigné ; contrats passés.

### Commandes de vérification
```bash
pytest -q tests/test_ipca.py tests/test_contracts.py
python -m jepadrift.representations.extract --dataset d3_239 --rep ipca
```
