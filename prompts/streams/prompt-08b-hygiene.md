## PROMPT 8b — Hygiène avant la vague E1/E3/JEPA : modules partagés, fixture sans effet de bord, registre des écarts

### Contexte
JEPA-Drift (« Article C ») entre dans sa vague la plus parallèle : E1, E3, CA-T-JEPA et IPCA vont tourner en même temps dans des worktrees distincts. Trois briques qu'ils partagent n'existent qu'en copies locales : le pivot des caractéristiques, le débiaisage et le bootstrap de l'audit, et le placebo de phases. Par ailleurs, le fixture de `tests/test_data_d1_d2.py` réécrit des fichiers suivis à chaque `make check`. Ce stream court factorise ces briques avant le lancement de la vague. Lire `CLAUDE.md`.

### Tâche
1. **Pivot des caractéristiques** `jepadrift/data_loader/chars.py` :
   - `load_chars_tensor(dataset, rows=None) -> (C, names)` : C est un tableau float64 (T, N, P), aligné sur `ret_wide.npy`, `dates.npy` et `assets.json` du jeu (`d3_239`, `d3_500`, `d4_eurofidai` si construit). Les NaN sont conservés et l'ordre des colonnes suit `chars.parquet` ;
   - `impute_zero(C) -> (C0, n_imputed)` : remplace les NaN par 0 et en rend le compte (convention de `injection.inject`, `C-inject-F2-nan`) ;
   - pour `d2_us97`, lever `ValueError("D2 has no characteristics")` ;
   - tests `tests/test_chars.py` :
     - alignement exact sur 50 couples (date, titre) tirés avec graine, comparés à `chars.parquet` ;
     - formes attendues ; NaN conservés ;
     - égalité au bit près avec le pivot local de `tests/test_injection.py` sur la calib de `d3_239`.
2. **Statistiques de dérive partagées** `jepadrift/stats/drift.py`.
   - Déplacer sans modifier leur corps, depuis `experiments/audit_information.py` : `debiased_sr2`, `mbb_indices`, `_ci` (exporté sous le nom `shifted_percentile_ci`), `transitions` et `rotate_phases`.
   - L'audit les importe désormais et réexporte les anciens noms, de sorte que `tests/test_audit.py` reste inchangé.
   - Non-régression : `python experiments/audit_information.py --datasets d2_us97 d3_239 --quick` donne des CSV identiques au SHA-256 avant et après le déplacement.
3. **Lecture à horizon** dans `jepadrift/pipelines.py` :
   - ajouter `horizon_gamma(H, alpha=0.05) -> float`, égal à H/α ;
   - sa docstring cite la borne P∞(alarme avant H) ≤ H/γ ;
   - ajouter un test.
4. **Fixture sans effet de bord** (`tests/test_data_d1_d2.py`).
   - Le fixture de session reconstruit D1 et D2 sous une racine temporaire qui reproduit l'arborescence du dépôt. Il passe par un monkeypatch de `REPO_ROOT` et des chemins dérivés de `jepadrift.data_loader.articleB`, lus à l'appel.
   - Les tests comparent les SHA-256 des fichiers reconstruits à ceux des fichiers commités. Ils comparent aussi les entrées D1/D2 du manifeste reconstruit (jeux `d1_etf4` et `d2_us97`, résultat `d1_d2_profile`, source) à celles du manifeste commité.
   - Dans `.gitignore`, ignorer les nœuds `.venv` et `external` aussi lorsqu'ils sont des liens symboliques de worktree (les motifs actuels avec `/` final ne les couvrent pas). Vérifier `git check-ignore .venv external` dans un worktree, sans masquer d'autres modifications suivies.
   - Après `make check` sur un arbre propre, `git status --porcelain` doit être vide.
   - Dans `CLAUDE.md` (« Worktrees and parallel streams »), supprimer la phrase sur la réécriture des fichiers D1/D2 par le fixture.
5. **Fidélité des prompts** `tools/check_prompts.py`, avec une cible `make prompts-check`.
   - Mode par défaut : vérifier que chaque `prompts/streams/prompt-*.md` est une sous-chaîne exacte de `prompts/Prompts_Claude_Code_v5.md`.
   - `--sync-master` : remplacer dans le master chaque bloc de prompt (repéré par son titre `## PROMPT <id> —`) par le contenu du fichier de stream ; ajouter les blocs absents en fin de section 4.
   - Exécuter `--sync-master` (idempotent : le master est synchronisé depuis les fichiers stream), puis `make prompts-check` : 29/29.
6. **Registre des écarts** (`docs/DEVIATIONS.md`, en français, en fin de fichier) : ajouter verbatim les deux entrées du bloc ci-dessous.
7. **`CLAUDE.md`** (mémoire canonique ; `AGENTS.md` en est le lien symbolique) :
   - ajouter `chars` à la liste de `data_loader/` et `drift` à celle de `stats/` dans la puce `jepadrift/` du « Repository layout » ;
   - ajouter `check_prompts.py` à la puce `tools/`.

```markdown
## C-D3-survivor-correction — biais de survie de D3 (2026-10-18)

Correction de `C-D3-survivor`. Un univers formé des constituants actuels du S&P 500, projeté en
arrière jusqu'en 2000, est biaisé par la survie : un titre n'y figure que parce qu'il a survécu et a
rejoint l'indice. `d3_239` (les 239 plus longs historiques parmi ces constituants, `C-D3-no239`) l'est
doublement. Portée : les expériences sur fonds symétrisés D6 avec dérives injectées en dépendent peu ;
les mesures sur données brutes (recensement, E8, placebos) héritent du biais et servent d'appui, jamais
de preuve de détectabilité. Aucune donnée n'est modifiée.

## C-D4-survivor — sélection de D4 (2026-10-18)

D4 contient 498 titres EUROFIDAI retenus pour au moins 5 000 observations entre 2001 et 2026 (places
AMS, BRU, EPA, LSE, MIL, XET). Cette sélection sur la longueur d'historique est une sélection par la
survie ; l'export ne fournit ni date de radiation ni statut (radiations inférées par l'absence de
données), et MIL n'a pas de données pour 2024–2026. `in_universe` couvre 91 % des cellules : les
appelants choisissent des sous-panels complets sur leur fenêtre (`inject` exige un panel fini). D4 n'a
pas de secteur GICS : F2 n'y utilise que les quatre caractéristiques continues.
```

### Entrées
`experiments/audit_information.py`, `tests/test_injection.py` (pivot local), `jepadrift/data_loader/{articleB,sp500,eurofidai}.py`, `prompts/streams/`, `prompts/Prompts_Claude_Code_v5.md` ; `CLAUDE.md`.

### Livrables
- Code : `jepadrift/data_loader/chars.py`, `jepadrift/stats/drift.py`, `horizon_gamma` dans `jepadrift/pipelines.py`, `tools/check_prompts.py`.
- Tests : `tests/test_chars.py`, `tests/test_drift_stats.py`, fixture révisé de `tests/test_data_d1_d2.py`.
- Configuration : cible `prompts-check` du `Makefile`, master resynchronisé, `.gitignore` adapté aux liens de worktree, entrées de `docs/DEVIATIONS.md`, `CLAUDE.md` mis à jour.

### Contraintes techniques
- Déplacements sans modification de corps, contrôlés par `ast` sur les segments.
- Aucun changement de sortie de l'audit.
- `jepadrift/monitors/` reste inchangé ; numpy et pandas seulement.
- `make check` reste sous 5 minutes.

### Critères de succès
- Audit `--quick` identique au SHA-256.
- `tests/test_audit.py`, `tests/test_chars.py` et `tests/test_drift_stats.py` au vert.
- `git status --porcelain` vide après `make check` sur un arbre propre.
- `make prompts-check` : 29/29.
- Écarts et mise à jour de `CLAUDE.md` commités.

### Commandes de vérification
```bash
python experiments/audit_information.py --datasets d2_us97 d3_239 --quick --out /tmp/audit_q && sha256sum /tmp/audit_q/*.csv
pytest -q tests/test_chars.py tests/test_drift_stats.py tests/test_audit.py
make check && git status --porcelain
make prompts-check
```
