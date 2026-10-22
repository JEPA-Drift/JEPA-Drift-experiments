## PROMPT 18 — Adaptateur CD-DFM (facteurs cash-neutral et covariance conditionnelle)

### Contexte
CD-DFM (Alouadi & Lehalle, arXiv:2607.24410, dépôt public) construit des facteurs cash-neutral à partir des caractéristiques et prévoit la covariance. JEPA-Drift l'utilise comme deuxième modèle latent piloté par les caractéristiques (P4) et comme blanchiment conditionnel (canal N2). Ses entrées d'origine (fondamentaux) ne sont pas disponibles : on l'adapte aux caractéristiques tirées des rendements. Lire `CLAUDE.md`.

### Tâche
1. Réutiliser le clone `external/cd-dfm/` du stream 3, dont le commit est épinglé dans `data/derived/MANIFEST.json` ; ne pas recloner. Lire la licence et les dépendances ; le README indique que le panel d'origine n'est pas redistribuable. Toute exécution du stream reste dans la `.venv` du projet ; si ses dépendances ne peuvent y être intégrées, suivre le chemin d'arrêt, sans créer un second environnement.
2. Adapter les entrées : les 4 caractéristiques continues de `d3_239`, connues à t−1 et lues par `data_loader.chars.load_chars_tensor` (stream 8b), au format attendu. Les 11 GICS actuels sont rétropolés (`C-D3-gics-static`) : les utiliser seulement en sensibilité rétrospective étiquetée. Entraîner sur `pretrain` selon la recette du dépôt, avec K = 11 (marché plus dix facteurs cash-neutral), ou documenter dans le plan pourquoi ce rang n'est pas identifiable avec les entrées disponibles.
3. Extraire :
   - les rendements de facteurs, linéaires en x_t avec appartenances connues en t−1, donc impairs ;
   - la covariance prévue Σ̂(t), pour le blanchiment conditionnel.

   Emballer le tout dans l'interface Z, avec un JSON qui précise l'écart d'entrées.
4. Enregistrer P4-C et P4-D (variante CD-DFM) après intégration de la variante IPCA du stream 17 dans le registre partagé ; l'adaptateur et ses tests peuvent être développés en parallèle.
5. Avant toute installation, vérifier au commit épinglé que la chaîne officielle d'entraînement est complète, notamment le module `data.dataset` et l'objet `preprocess_panel` importé depuis `data`. Si ces éléments manquent, livrer seulement un diagnostic factuel dans `docs/sections/cddfm_adapter.md` (commit, fichiers/imports absents, licence observée) ; ne créer ni adaptateur, ni extraction, ni entrée P4, ni remplacement local du code manquant. Même chemin d'arrêt si les dépendances sont introuvables. Priorité B.

### Entrées
Dépôt CD-DFM ; D3 et caractéristiques ; `CLAUDE.md`.

### Livrables
`jepadrift/representations/cddfm_adapter.py`, extractions, `tests/test_cddfm_adapter.py`, `docs/sections/cddfm_adapter.md`, entrée `C-CDDFM-inputs` dans `docs/DEVIATIONS.md`.
Si la tâche 5 déclenche l'arrêt, seul le diagnostic documentaire et le plan/wrapup sont exigés ; les livrables de modèle et les critères de test ci-dessous ne s'appliquent pas.

### Contraintes techniques
Code externe non modifié (adaptateur seulement) ; graines fixées ; CPU ; nouveaux audits en anglais.

### Critères de succès
Imparité des rendements de facteurs ≤ 1e-6 ; contrats au vert ; écart d'entrées documenté.

### Commandes de vérification
```bash
.venv/bin/pytest -q tests/test_cddfm_adapter.py tests/test_contracts.py
```
