## PROMPT 27 — E10 : robustesse (queues épaisses, levier, dépendance asymétrique, rendements nuls)

### Contexte
L'exactitude des flux de signe de JEPA-Drift suppose la symétrie centrale conditionnelle. E10 mesure jusqu'où les fausses alarmes et les gains tiennent quand elle est violée, et ce que corrige le recentrage sur un taux estimé q̂_u. Annexe D. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e10_robustness.py`.
1. **Fonds D5** :
   - t_ν avec ν ∈ {3, 4, 5, 7} ;
   - GJR-GARCH (levier ∈ {0, 0.05, 0.10}) ;
   - choc commun asymétrique (dépendance de queue asymétrique) ;
   - part de rendements nuls ∈ {0, 2 %, 5 %}, par arrondi.

   S'y ajoutent D6 et le placebo D2–D3 brut (fenêtres antérieures à 2020 avant J4), avec ses violations naturelles mesurées par l'audit (symétrie rejetée sur PC1, PC2, PC3 et `rev_21` selon le jeu, `CLAUDE.md`) et ses rendements nuls (2 864 sur D2 avant 2020, tranchés par pièce).
   Les innovations t_ν symétriques et un levier GJR prévisible avec innovations symétriques conservent la symétrie conditionnelle ; les égalités dues à l'arrondi sont départagées par des pièces indépendantes issues d'un PRNG local. Classer chaque fond par validité du nul avant d'interpréter son FPR.
2. **Pipelines par portes** : P1-C et P3-C sur F1 dès maintenant, avec et sans recentrage sur q̂_u estimé sur `calib` ; F2 sur D3 seulement après le chargeur partagé du stream 8b, sans pivot local dupliqué ; P5-C seulement après disponibilité d'un point de contrôle gelé du stream 16. Le P1-C existant est dans `monitors/cusum.py`, pas dans `pipelines.PIPELINES` : réutiliser ce noyau avant d'envisager une entrée de registre. Une option explicite sélectionne les familles et l'exécution initiale ne dépend ni de 8b ni de P5-C.
   Pour P3-C recentré, utiliser un flux borné `x = (B − q̂_u) / max(q̂_u, 1 − q̂_u)` avec `q̂_u ∈ [0, 1]` appris sur `calib` puis gelé. Ne pas transmettre `2(B − q̂_u)` à `eprocess._bounded` s'il sort de `[-1, 1]`. Le recentrage estimé est descriptif sans preuve de moyenne conditionnelle nulle tenant compte de son erreur d'estimation.
   Pour chaque paire de variantes P1-C et P3-C, départager les zéros par des pièces locales indépendantes, réutiliser les mêmes bits réalisés entre les bras et estimer q̂ sur `calib` avec cette même convention. Si la règle « zéro = négatif » de l'Article B est rapportée, en faire un bras distinct : elle ne doit pas confondre l'effet du recentrage.
3. **Mesures** : FPR observé avec IC contre le niveau nominal et le niveau atteint sous le nul valide ; G_ADD sur F1 immédiatement, puis F2 sur D3 uniquement (D2 n'a pas de caractéristiques), à γ_H = H/α. Sur les placebos bruts asymétriques, ne pas qualifier la lecture de garantie exacte. Rapporter le FPR atteint à côté de chaque gain ; si les FPR diffèrent, ne pas conclure à un gain à fausse alarme égale.
   Le rapport `RMST_P1/RMST_P3` est un rapport de délais restreints à H ; il ne borne le rapport d'ADD que si P3 n'est pas censuré. Le chevauchement des IC de FPR ne démontre pas leur équivalence : une revendication « à fausse alarme égale » exige une marge préspécifiée et un test d'équivalence valide. Les pièces indépendantes entre canaux ne fournissent qu'un scénario de référence iid, pas le FPR atteint universel du dictionnaire P3-C dépendant. Le placebo brut sur pretrain, ajusté sur une calib ultérieure, est rétrospectif ; un titre choisi sur les résultats F1 est un oracle exploratoire.

### Entrées
Étape initiale F1 : prompts 5 et 7. Complément F2 : stream 8b. Complément P5-C : stream 16 et son point de contrôle gelé ; `CLAUDE.md`.

### Livrables
`experiments/e10_robustness.py`, `configs/e10.yaml`, `results/e10/e10_cells.csv`, `figures/e10/*`.

### Contraintes techniques
Graines locales `SeedSequence` ; option `--quick` ; aucun accès aux lignes réelles datées de 2020 ou après avant J4. Pour les fenêtres brutes chevauchantes, n'utiliser un IC qu'avec un `deff` estimable et `1 ≤ n_eff ≤ n` ; si l'indicatrice est constante ou l'estimateur pathologique, indiquer `IC=NA`, sans fabriquer une précision binomiale avec `floor(lignes/H)`. Exporter tous les CSV par `save_fair_csv` ; rédiger les nouveaux comptes rendus d'audit en anglais.

### Critères de succès
Inflation du FPR quantifiée par violation, avec IC ; effet du recentrage rapporté.

### Commandes de vérification
```bash
.venv/bin/python experiments/e10_robustness.py --stage linear --families F1 --quick --out results/e10_quick
```
