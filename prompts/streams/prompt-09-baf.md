## PROMPT 9 — Jeu BAF (Bank Account Fraud, variante Base) : téléchargement, contrôle et découpage

### Contexte
JEPA-Drift ajoute un domaine tabulaire hors finance : BAF (Jesus et al., NeurIPS 2022 Datasets and Benchmarks). Ce sont des demandes d'ouverture de compte synthétiques, générées à partir de données réelles, sur huit mois, avec une dérive native. Requis pour T-JEPA (prompt 15) et E9 ; non bloquant pour J1 et J2. Lire `CLAUDE.md`.

### Tâche
1. **Source.** Lire la fiche technique officielle du jeu (dépôt `feedzai/bank-account-fraud` sur GitHub et page Kaggle associée ; vérifier l'identifiant Kaggle, par exemple `sgpjesus/bank-account-fraud-dataset-neurips-2022`). Télécharger par l'API Kaggle, avec des identifiants lus dans `~/.kaggle/kaggle.json`, jamais commités, vers `data/raw/baf/`.
2. **Contrôles.**
   - Six variantes (Base, Variant I à V) de 1 000 000 lignes chacune.
   - 30 attributs, plus `fraud_bool` et `month`, avec `month` ∈ {0,…,7}.
   - Consigner le schéma (types, catégories), la licence de la fiche et la prévalence de fraude par mois.
3. **Conversion.** Base vers `data/derived/d7_baf/base.parquet`, avec l'ordre des lignes d'origine conservé et un index de ligne. Découpage `splits.yaml` : `fit` mois 0–2, `calib` mois 3, `monitor` mois 4–7.
4. **Prétraitement figé, appris sur les mois 0–2 seulement** : standardisation des numériques, encodage des catégories (inconnues → modalité réservée), traitement des sentinelles −1 documentées dans la fiche. Sauvegarder les paramètres dans `preproc.json`.
5. **Profil** dans `results/data/baf_profile.csv` : effectifs, taux de fraude et moyennes des attributs par mois.
6. **Écarts.** `C-BAF-synthetic` : rédiger « dérive native d'un jeu synthétique », jamais « in-the-wild ».

### Entrées
Compte Kaggle du chercheur ; `CLAUDE.md`.

### Livrables
`data/raw/baf/` (ignoré par git), `data/derived/d7_baf/{base.parquet,splits.yaml,preproc.json}`, `jepadrift/data_loader/baf.py` (`--build`), `tests/test_data_baf.py`, `results/data/baf_profile.csv`, `docs/sections/data_baf.md`.

### Contraintes techniques
- pandas et pyarrow.
- Aucun paramètre de prétraitement estimé hors des mois 0–2.
- Données brutes non commitées.

### Critères de succès
1 000 000 lignes, 32 colonnes, 8 mois ; tests au vert ; prétraitement reproductible au SHA-256 près.

### Commandes de vérification
```bash
python -m jepadrift.data_loader.baf --build
pytest -q tests/test_data_baf.py
python -c "import pandas as pd; d=pd.read_parquet('data/derived/d7_baf/base.parquet'); print(d.shape, d.month.value_counts().sort_index().to_dict())"
```
