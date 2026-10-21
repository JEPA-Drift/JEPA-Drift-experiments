## PROMPT 16 — Campagne de pré-entraînement CA-T-JEPA et diagnostics d'effondrement (jalon J3)

### Contexte
J3 (1er novembre) exige une représentation non effondrée : le RankMe de la tête de lecture doit atteindre au moins 0.5·D. Cette campagne entraîne CA-T-JEPA et ses variantes sur trois graines et mesure le rang effectif, avant les comparaisons d'E5. Lire `CLAUDE.md`.

Définition : RankMe(Z) = exp(−Σ_k p_k log p_k), avec p_k = σ_k/Σσ + ε (Garrido et al., ICML 2023).

### Tâche
1. Entraîner, sur `d3_239` (segment `pretrain`), les objectifs `jepa`, `mae` et `temporal`, chacun avec 3 graines (0, 1, 2) ; une exécution par processus et un thread par exécution (`--jobs`, résultats indépendants du nombre de processus) ; enregistrer les points de contrôle. La lecture D ∈ {2, 4, 8, 16} est une ACP post hoc : un seul entraînement par (objectif, graine).
2. Pour chaque point de contrôle et chaque D ∈ {2, 4, 8, 16} :
   - ajuster la lecture sur `calib` et extraire Z ;
   - calculer le RankMe du tronc et de la lecture, la variance par dimension et la part de dimensions de variance inférieure à 1e-3.
3. **Porte J3** : RankMe(lecture) ≥ 0.5·D pour chaque D, sur l'objectif `jepa`. Résultat écrit dans `results/jepa_pretrain/J3_gate.txt`.
4. **Contingence si J3 échoue** : doubler le poids du terme de variance, réduire d_model à 32, relancer une fois et consigner les deux campagnes.
5. Construire le tableau des courbes de perte, à partir des journaux d'entraînement exportés en CSV.

### Entrées
Prompt 14 ; D3 ; `CLAUDE.md`.

### Livrables
`ckpt/<hash>/` (ignoré par git, empreintes versionnées), `results/jepa_pretrain/{runs.csv,rankme.csv,losses.csv,J3_gate.txt}`, `figures/jepa_pretrain/*`.

### Contraintes techniques
CPU (48 cœurs) ; exécutions parallèles déterministes, une par processus ; durée totale consignée ; contrats, dont les quatre gardes torch, au vert sur chaque point de contrôle extrait.

### Critères de succès
12 exécutions principales et 6 de variantes terminées ; porte J3 évaluée ; résultats reproductibles au SHA-256 près pour une graine relancée.

### Commandes de vérification
```bash
python experiments/jepa_campaign.py --dataset d3_239 --seeds 0 1 2 --objectives jepa mae temporal --jobs 9
cat results/jepa_pretrain/J3_gate.txt
```
