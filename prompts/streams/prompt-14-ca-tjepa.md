## PROMPT 14 — CA-T-JEPA : modèle, pré-entraînement et représentation (avec variantes MAE et prétexte temporel)

### Contexte
JEPA-Drift apprend une représentation de la coupe quotidienne par un JEPA transversal (Cross-Asset Temporal JEPA) :
- les actifs sont des jetons, conditionnés par leurs caractéristiques ;
- le masquage porte sur des actifs, avec prédiction dans l'espace latent et cible EMA.

Une tête impaire, obtenue par antisymétrisation, alimente les flux de signe exacts ; une tête paire alimente les capteurs d'énergie. Le code doit être prêt pour la campagne de J3 (1er novembre). Lire `CLAUDE.md`.

### Tâche
0. **torch dans `.venv`.**
   - Installer la roue CPU stable la plus récente compatible avec numpy 2.4.4 (`--index-url https://download.pytorch.org/whl/cpu`).
   - L'épingler dans `requirements.txt` et régénérer `requirements.lock`.
   - numpy, scipy et pandas ne doivent pas bouger (comparer `pip freeze` avant et après) ; `make j1` doit redonner `e315e537…`.
   - Ne jamais utiliser le torch de l'environnement Trading.
1. **`jepadrift/jepa/ca_tjepa.py`** (torch, CPU, au plus 1 M de paramètres) :
   - jeton i = MLP([x_{i,t}/s_i, C_{i,t}]), où s_i est l'échelle de l'actif, figée sur `pretrain`. C_{i,t} vient de `data_loader.chars.load_chars_tensor("d3_239")` (15 colonnes ; NaN → 0 comptés par `impute_zero`) ;
   - 2 à 4 couches d'auto-attention équivariantes par permutation, sans encodage de position (d_model = 64, 4 têtes) ; LayerNorm autorisée, BatchNorm interdite ;
   - encodeur de contexte sur les actifs visibles ; encodeur cible EMA sur tous les actifs (moment de 0,996 à 0,9995, calendrier cosinus) ;
   - prédicteur à 2 couches, dont les requêtes portent C_{i,t} des actifs masqués ;
   - perte L2 dans l'espace latent sur les jetons masqués, plus un terme de variance de type VICReg (charnière sur l'écart-type ≥ 1) ;
   - masquage aléatoire de 30 à 50 % des actifs, ou masquage par secteur (option).
2. **Têtes.**
   - φ_impair(x;C) = ½[g(x;C) − g(−x;C)] et φ_pair = ½[g(x;C) + g(−x;C)], avec g le plongement poolé (moyenne sur les actifs) du tronc.
   - Lecture : ACP blanchissante apprise sur `calib`, D ∈ {2, 4, 8, 16}. Elle est linéaire, donc l'imparité est conservée.
3. **Variantes.**
   - `--objective mae` : un décodeur reconstruit x_{i,t} masqué.
   - `--objective temporal` : les cibles sont les plongements du jour t+1, sur `pretrain` seulement ; l'extraction n'utilise que le jour t.
4. **Script `experiments/jepa_pretrain.py`.**
   - Données : `d3_239`, segment `pretrain`.
   - AdamW (taux 1e-3), lots de 64 jours, au plus 200 époques, arrêt sur la perte JEPA de `calib`.
   - Écrit `ckpt/<hash>/` : poids, configuration, empreinte des données. `ckpt/` est ignoré par git ; ses empreintes sont versionnées.
5. **Représentation** `jepadrift/jepa/representation.py`, sous-classe de `representations.base.Representation` (interface Z-1) qui charge un point de contrôle figé :
   - `state_hash` inclut le SHA-256 du point de contrôle ;
   - `_fit` n'ajuste que la lecture, sur les lignes de calib ;
   - `_day` n'utilise que x_t et C_t ;
   - `transform_panel` peut traiter les jours par lots seulement si le résultat est identique au bit près à l'empilement de `transform_day` ; sinon, boucle jour par jour.
6. **Enregistrement et extraction.**
   - Ajouter une entrée paresseuse `ca_tjepa` dans `representations/extract.REGISTRY` : torch est importé dans la fabrique, jamais à l'import de `jepadrift.representations`.
   - Extraction par la CLI existante, étendue d'une option `--ckpt` : `python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt ckpt/<hash>`. Les lignes extraites suivent `C-repr-rows`.
7. **Contrats.** Les tests paramétrés sur le registre s'appliquent. Les quatre gardes torch de `tests/test_contracts.py` doivent tourner dans `make check`, et non être sautées.
8. **Test de fumée** : 2 époques sur 200 jours, extraction, puis contrats.

### Entrées
D3 et caractéristiques (stream 3, chargeur partagé du stream 8b) ; interface Z (stream 6) ; contrats (stream 8) ; `CLAUDE.md`.

### Livrables
- Code : `jepadrift/jepa/{ca_tjepa,representation}.py` ; entrée `ca_tjepa` et option `--ckpt` de `jepadrift/representations/extract.py` ; `experiments/jepa_pretrain.py`.
- Configuration et tests : `configs/ca_tjepa.yaml`, `tests/test_ca_tjepa.py`, `requirements.txt` et `requirements.lock` mis à jour.
- Documentation : `docs/sections/ca_tjepa.md` (architecture, nombre de paramètres, choix d'anti-effondrement).

### Contraintes techniques
- `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`, toutes les graines fixées (`torch.manual_seed` et `SeedSequence`), CPU.
- Aucune méthode non publiée.
- Aucune donnée de `monitor` vue à l'entraînement ou à l'ajustement de la lecture.
- `jepadrift/jepa/` n'importe ni `jepadrift.injection` ni `jepadrift.monitors`.

### Critères de succès
- Contrats au vert, dont imparité ≤ 1e-6, avec les gardes torch exécutées.
- Deux extractions identiques au SHA-256 près.
- Nombre de paramètres ≤ 1 M.
- Test de fumée en moins de 10 minutes ; `make j1` inchangé.

### Commandes de vérification
```bash
python experiments/jepa_pretrain.py --config configs/ca_tjepa.yaml --smoke
python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt ckpt/<hash>
pytest -q -rs tests/test_ca_tjepa.py tests/test_contracts.py
make j1 && sha256sum results/e2/e2_cells.csv | cut -c1-16
```