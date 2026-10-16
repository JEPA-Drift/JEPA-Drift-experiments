## PROMPT 18 — Adaptateur CD-DFM (facteurs cash-neutral et covariance conditionnelle)

### Contexte
CD-DFM (Alouadi & Lehalle, arXiv:2607.24410, code public) construit des facteurs cash-neutral à partir des caractéristiques et prévoit la covariance. JEPA-Drift l'utilise comme deuxième modèle latent piloté par les caractéristiques (P4) et comme blanchiment conditionnel (canal N2). Ses entrées d'origine (fondamentaux) ne sont pas disponibles : on l'adapte aux caractéristiques tirées des rendements. Lire `CLAUDE.md`.

### Tâche
1. Cloner `https://github.com/alexouadi/CD-DFM`, épingler le commit, lire la licence et les dépendances. Installer dans `external/cddfm/.venv` si les dépendances entrent en conflit.
2. Adapter les entrées : caractéristiques de `d3_239` (prompt 3) au format attendu. Entraîner sur `pretrain` selon la recette du dépôt, avec K = 11 (marché plus dix facteurs cash-neutral).
3. Extraire :
   - les rendements de facteurs, linéaires en x_t avec appartenances connues en t−1, donc impairs ;
   - la covariance prévue Σ̂(t), pour le blanchiment conditionnel.

   Emballer le tout dans l'interface Z, avec un JSON qui précise l'écart d'entrées.
4. Enregistrer P4-C et P4-D (variante CD-DFM).
5. Si le dépôt est inutilisable (code incomplet, dépendances introuvables), s'arrêter après un diagnostic écrit dans `docs/sections/cddfm_adapter.md`. Priorité B.

### Entrées
Dépôt CD-DFM ; D3 et caractéristiques ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/cddfm_adapter.py`, extractions, `tests/test_cddfm_adapter.py`, `docs/sections/cddfm_adapter.md`, entrée `C-CDDFM-inputs` dans `docs/DEVIATIONS.md`.

### Contraintes techniques
Code externe non modifié (adaptateur seulement) ; graines fixées ; CPU.

### Critères de succès
Imparité des rendements de facteurs ≤ 1e-6 ; contrats au vert ; écart d'entrées documenté.

### Commandes de vérification
```bash
pytest -q tests/test_cddfm_adapter.py tests/test_contracts.py
```
