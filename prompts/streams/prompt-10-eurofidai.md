## PROMPT 10 — EUROFIDAI (D4) : spécification d'extraction, ingestion locale et garde-fous

### Contexte
D4 (actions européennes, constituants point-in-time, jusqu'à environ 1000 titres) sert au test d'échelle en N et au recensement européen de JEPA-Drift. Les données sont propriétaires : elles ne quittent jamais la machine du chercheur, et seuls les scripts et les manifestes d'empreintes sont versionnés. Claude Code n'a pas d'accès au portail EUROFIDAI : il prépare l'extraction que le chercheur exécute, puis l'ingestion. Lire `CLAUDE.md`.

### Tâche
1. Rédiger `docs/sections/eurofidai_extraction_spec.md`, à exécuter sur le portail :
   - marchés de la zone euro et du Royaume-Uni ;
   - période 2000-01-01 → dernière date disponible ;
   - fréquence quotidienne ;
   - champs : identifiant stable, ISIN, marché, date, cours ajusté ou facteurs d'ajustement, rendement total si disponible, capitalisation, statut de cotation et dates de radiation (titres radiés inclus), appartenance aux indices si disponible ;
   - format CSV, un fichier par marché et par année ;
   - dépôt dans `data/raw/eurofidai/`.
2. `jepadrift/data_loader/eurofidai.py` :
   - lecture des fichiers exportés, avec une table de correspondance des champs dans `configs/eurofidai_schema.yaml`, modifiable si les noms diffèrent ;
   - rendements log à partir des cours ajustés, sans remplissage ;
   - `in_universe` point-in-time ;
   - filtre de liquidité documenté (jours sans échange) ;
   - caractéristiques tirées des rendements, avec la même définition que D3 (réutiliser le code de `sp500.py`) ;
   - sortie `data/derived/d4_eurofidai/` aux formats de D3.
3. **Manifeste versionné** `docs/manifests/d4_manifest.json` : empreintes, effectifs, dates, sans aucune donnée.
4. **Tests sur données synthétiques** (`tests/fixtures/eurofidai_fake/`) : schéma, ajustements, radiations, non-anticipation des caractéristiques. Les tests réels sont sautés si `data/raw/eurofidai/` est vide.
5. **Vérifier** que `.gitignore` et le hook du prompt 8 bloquent `data/raw/eurofidai/` et `data/derived/d4_eurofidai/`.

### Entrées
Export manuel du chercheur (plus tard) ; `CLAUDE.md` ; code de D3.

### Livrables
Spécification d'extraction, chargeur, configuration de schéma, fixtures et tests, manifeste vide prêt à remplir.

### Contraintes techniques
- Aucune donnée EUROFIDAI dans git, dans les journaux ou dans les CSV de `results/` (seulement des agrégats).
- Aucune requête automatisée vers le portail.

### Critères de succès
Tests sur fixtures au vert ; hook vérifié ; spécification exécutable telle quelle par le chercheur.

### Commandes de vérification
```bash
pytest -q tests/test_data_eurofidai.py
git check-ignore -v data/derived/d4_eurofidai/x data/raw/eurofidai/x
```
