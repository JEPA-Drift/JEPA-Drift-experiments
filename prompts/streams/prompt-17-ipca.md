## PROMPT 17 — IPCA sur caractéristiques tirées des rendements (pipelines P4)

### Contexte
JEPA-Drift compare le JEPA à des facteurs latents pilotés par les caractéristiques. Le premier est l'IPCA (Kelly, Pruitt & Su, 2019) : x_t = C_t Γ f_t + ε_t, avec des chargements C_tΓ connus en t−1. Ses rendements de facteurs sont linéaires en x_t, donc impairs, et leurs flux de signe sont exacts. Lire `CLAUDE.md`.

### Tâche
1. Implémenter dans `jepadrift/representations/ipca.py` l'estimation par moindres carrés alternés :
   - f_t = (ΓᵀC_tᵀC_tΓ)⁻¹ΓᵀC_tᵀx_t, pour Γ donné ;
   - Γ mis à jour par la régression empilée ;
   - normalisation ΓᵀΓ = I, facteurs orthogonaux ; avec quatre caractéristiques principales, K ≤ 4 et `rank(C_t[in_universe_t] @ Γ) = K` doivent tenir chaque jour utilisé. Consigner les jours déficients et une règle d'exclusion ou de régularisation justifiée ; K = 5, 6 sont non identifiables en principal, sans recours aux GICS rétropolés ni pseudo-inverse silencieuse ;
   - critère d'arrêt sur l'objectif ou le projecteur ΓΓᵀ (ou Γ aligné par Procrustes), pas sur Γ brut sensible aux signes et rotations.
2. Caractéristiques : `data_loader.chars.load_chars_tensor` (stream 8b) ; protocole principal avec les 4 colonnes continues connues à t−1 sur D3 et D4. Les 11 GICS de D3 sont une classification actuelle rétropolée (`C-D3-gics-static`) : les 15 colonnes ne servent qu'à une sensibilité rétrospective explicitement étiquetée, jamais à une conclusion prospective. NaN des caractéristiques → 0 comptés. `d3_500` et D4 sont déséquilibrés : charger le masque `in_universe` aligné aux dates et titres, exclure les rendements manquants des équations et scores sans les imputer. `Representation._check` et `pipelines._panel` refusent les NaN : détailler une adaptation qui conserve les autres représentations et ne traite pas un zéro de remplissage comme une observation. Apprendre Γ sur `pretrain` ; choisir K parmi les rangs identifiables par R² sur actifs de `calib` tenus à l'écart : estimer f_t sur les actifs d'ajustement et scorer les actifs disjoints, avec partage déterministe. Ne pas appeler « hors échantillon » une reconstruction sur les actifs servant à estimer f_t. Blanchir f_t sur `calib` par une transformation linéaire homogène, sans centrage ni intercept de la tête impaire.
3. Option « cash-neutral » : retirer le facteur de marché (constante ou bêta) avant extraction.
4. Enregistrer la représentation et les pipelines P4-C (signes des facteurs, e-détecteur de dictionnaire) et P4-D (énergie). Étendre `extract.py` pour passer C aligné et séparer Γ appris sur `pretrain` de K/blanchiment ajustés sur `calib`, sans changer D2/PCA ; coordonner `extract.py` et `tests/test_contracts.py` avec le stream 14, et `pipelines.py` avec 23 avant les fusions.
5. **Tests** :
   - récupération sur données simulées : sous-espace de Γ retrouvé avec des angles principaux < 5° ;
   - imparité `φ(−x;C) = −φ(x;C)` avec C figé, y compris cash-neutral ; non-anticipation ; état figé ;
   - contrats du prompt 8.

### Entrées
`d3_239`, `d3_500` (et D4) avec leurs caractéristiques ; interface Z ; stream 8b ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/ipca.py`, `tests/test_ipca.py`, extractions, `results/ipca/k_selection.csv`, `docs/sections/ipca.md`.

### Contraintes techniques
numpy seul ; aucune donnée de `monitor` ; nouveaux audits en anglais.

### Critères de succès
Tests au vert ; K choisi et consigné ; contrats passés.

### Commandes de vérification
```bash
.venv/bin/pytest -q tests/test_ipca.py tests/test_contracts.py
.venv/bin/python -m jepadrift.representations.extract --dataset d3_239 --rep ipca
```
