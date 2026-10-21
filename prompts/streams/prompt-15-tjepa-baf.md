## PROMPT 15 — T-JEPA pour BAF : enveloppe tabulaire et plongements

### Contexte
Sur BAF, domaine tabulaire, JEPA-Drift utilise T-JEPA (Thimonier et al., ICLR 2025) : masquage de colonnes, encodeur cible EMA, prédiction latente, sans augmentation. Les plongements alimentent la surveillance de la dérive des données (P6-D) dans E9. Lire `CLAUDE.md`.

### Tâche
1. Chercher une implémentation officielle publique de T-JEPA. Si elle existe, l'utiliser à un commit épinglé, avec sa licence vérifiée et citée. Sinon, implémenter une version minimale fidèle à l'article dans `jepadrift/jepa/tjepa.py` :
   - un jeton par attribut (linéaire pour les numériques, plongement pour les catégories) ;
   - transformeur sur les jetons ;
   - masques de sous-ensembles de colonnes ;
   - cible EMA, prédicteur.
2. Entraîner sur les mois 0–2 de la variante Base (`preproc.json` : catégories inconnues codées −1 ; `device_fraud_count`, constant, exclu des jetons ; sentinelles −1 déjà standardisées). Licence du jeu : CC BY 4.0.
3. Plongement = moyenne des jetons, puis ACP blanchissante apprise sur le mois 3. D* ∈ {4, 8, 16}, choisi sur les mois 0–2 seulement (RankMe ≥ 0.5·D et perte de validation).
4. Extraire les plongements des mois 0–7 vers `data/derived/d7_baf/z_<hash>.npz`, avec le JSON de l'interface Z. Les lignes ne sont pas des jours : `dates` est remplacé par (`month`, `row`), écart `C-Z-baf`. Enregistrer la représentation par une entrée paresseuse du registre : torch n'est pas importé à l'import de `jepadrift.representations`.
5. Références à produire avec le même extracteur : ACP sur attributs bruts standardisés (90 % de variance) et attributs bruts.

### Entrées
`data/derived/d7_baf/` (prompt 9) ; interface Z ; `CLAUDE.md`.

### Livrables
`jepadrift/jepa/tjepa.py` (ou une enveloppe), `experiments/tjepa_baf.py`, `configs/tjepa_baf.yaml`, plongements et JSON, `tests/test_tjepa.py`, `docs/sections/tjepa_baf.md` (source, écarts à l'article).

### Contraintes techniques
- CPU ; torch installé dans `.venv` selon AGENTS.md (par le stream 14 ; si ce stream démarre avant, l'installer à l'identique et réconcilier `requirements.lock` au rebase) ; déterminisme comme au prompt 14.
- Aucune information des mois 4–7 dans l'entraînement ou la lecture.

### Critères de succès
Contrats de non-anticipation, de déterminisme et d'absence de statistiques de test au vert. La tête impaire est sans objet en tabulaire : la marquer comme absente dans le JSON. RankMe rapporté.

### Commandes de vérification
```bash
python experiments/tjepa_baf.py --smoke
pytest -q tests/test_tjepa.py
```
