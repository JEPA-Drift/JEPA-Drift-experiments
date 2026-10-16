## PROMPT 14 — CA-T-JEPA : modèle, pré-entraînement et extracteur (avec variantes MAE et prétexte temporel)

### Contexte
JEPA-Drift apprend une représentation de la coupe quotidienne par un JEPA transversal (Cross-Asset Temporal JEPA) :
- les actifs sont des jetons, conditionnés par leurs caractéristiques ;
- le masquage porte sur des actifs, avec prédiction dans l'espace latent et cible EMA.

Une tête impaire, obtenue par antisymétrisation, alimente les flux de signe exacts ; une tête paire alimente les capteurs d'énergie. Le code doit être prêt pour la campagne de J3 (1er novembre). Lire `CLAUDE.md`.

### Tâche
1. **`jepadrift/jepa/ca_tjepa.py`** (torch, CPU, au plus 1 M de paramètres) :
   - jeton i = MLP([x_{i,t}/s_i, C_{i,t}]), avec s_i l'échelle de l'actif figée sur `pretrain` ;
   - 2 à 4 couches d'auto-attention équivariantes par permutation, sans encodage de position (d_model = 64, 4 têtes) ;
   - encodeur de contexte sur les actifs visibles ; encodeur cible EMA (moment de 0.996 à 0.9995, calendrier cosinus) sur tous les actifs ;
   - prédicteur à 2 couches, dont les requêtes portent C_{i,t} des actifs masqués ;
   - perte L2 dans l'espace latent sur les jetons masqués, plus un terme de variance de type VICReg (charnière sur l'écart-type ≥ 1) ;
   - masquage aléatoire de 30 à 50 % des actifs, ou masquage par secteur (option).
2. **Têtes.**
   - φ_impair(x;C) = ½[g(x;C) − g(−x;C)], φ_pair = ½[g(x;C) + g(−x;C)], avec g le plongement poolé (moyenne sur les actifs) du tronc.
   - Lecture : ACP blanchissante apprise sur `calib`, D ∈ {2, 4, 8, 16} pour la tête impaire et D' identique pour la tête paire. Elle est linéaire, donc l'imparité est conservée.
3. **Variantes.**
   - `--objective mae` : décodeur qui reconstruit x_{i,t} masqué dans l'espace d'entrée.
   - `--objective temporal` : cibles = plongements du jour t+1, sur `pretrain` seulement. L'extraction n'utilise que le jour t.
4. **Script `experiments/jepa_pretrain.py`.**
   - Données : `d3_239`, segment `pretrain`.
   - AdamW (taux 1e-3), lots de 64 jours, au plus 200 époques, arrêt sur la perte JEPA de `calib`.
   - Écrit `ckpt/<hash>/` : poids, configuration, empreinte des données.
5. **Extracteur `jepadrift/jepa/extract.py`.**
   - `model.eval()`, sans gradient, sur CPU.
   - Écrit `z_<hash>.npz` et son JSON selon `docs/sections/interface_Z.md`.
   - Interdit : BatchNorm, normalisation d'instance temporelle (RevIN), EMA active.
6. **Enregistrement** dans le registre des représentations, pour que les tests de contrat du prompt 8 s'appliquent.
7. **Test de fumée** : 2 époques sur 200 jours, extraction, puis contrats.

### Entrées
D3 et caractéristiques (prompt 3) ; interface Z (prompt 6) ; contrats (prompt 8) ; `CLAUDE.md`.

### Livrables
`jepadrift/jepa/{ca_tjepa,extract}.py`, `experiments/jepa_pretrain.py`, `configs/ca_tjepa.yaml`, `tests/test_ca_tjepa.py`, `docs/sections/ca_tjepa.md` (architecture, nombre de paramètres, choix d'anti-effondrement).

### Contraintes techniques
- torch CPU, version figée.
- `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`, toutes les graines fixées.
- Aucune méthode non publiée.
- Aucune donnée de `monitor` vue à l'entraînement ou à l'ajustement de la lecture.

### Critères de succès
- Contrats au vert, dont imparité ≤ 1e-6.
- Deux extractions identiques au SHA-256 près.
- Nombre de paramètres ≤ 1 M.
- Test de fumée en moins de 10 minutes.

### Commandes de vérification
```bash
python experiments/jepa_pretrain.py --config configs/ca_tjepa.yaml --smoke
python -m jepadrift.jepa.extract --ckpt ckpt/<hash> --dataset d3_239
pytest -q tests/test_ca_tjepa.py tests/test_contracts.py
```
