## PROMPT 8 — Surveillance (3/3) : tests de contrat, règles de découplage et garde-fous

### Contexte
JEPA-Drift sépare strictement représentation et surveillance : un encodeur qui anticipe, n'est pas impair, n'est pas déterministe ou s'ajuste sur la fenêtre de test fausse toutes les mesures. Quatre tests de contrat bloquent donc toute fusion de code. Ils doivent s'appliquer automatiquement à toute représentation enregistrée, y compris le futur JEPA. Lire `CLAUDE.md`.

### Tâche
1. **`tests/test_contracts.py`**, paramétré sur toutes les représentations du registre :
   - **(1) Non-anticipation** : perturber x_{t+1:T} laisse z_{1:t} identique bit à bit.
   - **(2) Imparité** : ‖φ(−x) + φ(x)‖_∞ ≤ 1e-6 sur la tête impaire.
   - **(3) Déterminisme** : deux exécutions dans des sous-processus neufs (`PYTHONHASHSEED=42`, un thread, CPU) donnent des SHA-256 identiques pour `z_*.npz` et `alarms.csv`.
   - **(4) Absence de statistiques de test** : `fit` ne reçoit que les segments `pretrain` ou `calib`. Perturber le segment `monitor` laisse `state_hash` inchangé, et les statistiques de normalisation du JSON proviennent du seul segment déclaré.
2. **`tests/test_decoupling.py`**, par analyse `ast` des imports :
   - `jepadrift/monitors/**` n'importe ni torch, ni `jepadrift.jepa`, ni `jepadrift.representations` ;
   - `jepadrift/jepa/**` n'importe ni `jepadrift.injection`, ni `jepadrift.monitors` ;
   - `jepadrift/injection.py` n'accepte que des panels de rendements : `assert` sur la forme et le dtype, refus explicite d'un objet `Z`.
3. **Pour les modèles torch** (s'appliquera au JEPA) :
   - en mode `eval`, aucun buffer ne change après 10 passes avant ;
   - aucune couche `BatchNorm*` en mode entraînement ;
   - aucune normalisation calculée sur l'axe temporel ;
   - cible EMA inactive à l'extraction.

   Si torch n'est pas installé, ces tests sont marqués comme sautés.
4. **Garde-fous git.** `tools/pre-commit` lance `make check`. Il refuse tout fichier sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/`, tout fichier de plus de 50 Mo, et tout `git push` signalé par un hook `pre-push` qui échoue avec un message rappelant l'accord de propriété intellectuelle. Installer les hooks avec `make hooks`.
5. **Étendre `make check`** : pyflakes, tests unitaires, tests de contrat et de découplage.

### Entrées
Prompts 4 à 7 ; `CLAUDE.md`.

### Livrables
`tests/test_contracts.py`, `tests/test_decoupling.py`, `tools/pre-commit`, `tools/pre-push`, cibles `hooks` et `check` du `Makefile`, `docs/sections/contracts.md`.

### Contraintes techniques
- Tests rapides (moins de 2 minutes au total), sur données réduites et déterministes.
- Aucune dépendance réseau.

### Critères de succès
Les quatre contrats passent pour PCA, DegreeZero et CenteredRanks. Une représentation volontairement fautive (fixture : normalisation sur toute la série) échoue au contrat (4). Le hook bloque un fichier factice placé sous `data/raw/eurofidai/`.

### Commandes de vérification
```bash
make hooks && make check
mkdir -p data/raw/eurofidai && echo x > data/raw/eurofidai/t.csv && git add -f data/raw/eurofidai/t.csv; git commit -m test || echo "bloqué : attendu"
git reset -q HEAD data/raw/eurofidai/t.csv && rm -r data/raw/eurofidai
```
