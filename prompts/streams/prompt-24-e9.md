## PROMPT 24 — E9 : dérives natives de BAF (P6-D données, P6-C concept)

### Contexte
E9 évalue la surveillance de JEPA-Drift hors finance, sur la dérive mensuelle native du jeu synthétique BAF. Deux cas : dérive des données, par martingale de test conforme sur plongements ; dérive de concept, par flux d'erreur d'un classifieur figé avec taux nul recentré. Les lignes d'un même mois sont traitées comme échangeables. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e9_baf.py`.
1. **P6-D.**
   - Score de non-conformité : distance au 10ᵉ plus proche voisin dans un échantillon de référence (50 000 lignes des mois 0–2), sur les plongements T-JEPA, ACP et bruts.
   - p-valeurs conformes lissées.
   - Martingale de puissance mélangée sur ε ∈ {0.1, …, 0.9} (Vovk et al., 2003), alarme à 1/α.
   - Mesures : délai en lignes après chaque frontière de mois ; FPR dans des mois stables (lignes permutées dans un mois).
2. **Confirmation hors ligne** : test MMD par permutation entre mois consécutifs (noyau RBF, heuristique de la médiane, 2000 lignes par mois, 1000 permutations).
3. **P6-C.**
   - `HistGradientBoostingClassifier` (`random_state` fixé) entraîné sur les mois 0–2, puis figé.
   - Flux d'erreur binaire au seuil choisi sur le mois 3 ; taux nul q̂ estimé sur le mois 3.
   - e-détecteur de pari recentré sur q̂.
   - Délai d'étiquetage simulé (étiquettes disponibles après L lignes, L ∈ {0, 10 000, 50 000}).
   - Ajouter des p-valeurs conformes sur l'erreur.

### Entrées
Prompts 9 et 15 ; bibliothèque de surveillance ; `CLAUDE.md`.

### Livrables
`experiments/e9_baf.py`, `configs/e9.yaml`, `results/e9/{e9_data_drift.csv,e9_concept_drift.csv,e9_mmd.csv}`, `figures/e9/*`.

### Contraintes techniques
Aucune donnée des mois 4–7 dans l'apprentissage ; scikit-learn autorisé ici ; graines fixées.

### Critères de succès
FPR dans les mois permutés au plus α (IC) ; délais rapportés par frontière ; MMD rapporté ; formulation « dérive native d'un jeu synthétique » dans le CSV de métadonnées.

### Commandes de vérification
```bash
python experiments/e9_baf.py --quick --out results/e9_quick
```
