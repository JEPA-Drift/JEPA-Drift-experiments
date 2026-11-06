# Plan lot 21-trace — contrôle exécutable des six correspondances E2 de MAPPING

Proposition native, en attente du GO écrit de Codex. Aucun code, test ou édition avant ce GO. Aucun sous-agent, Graphify/jCodeMunch non utilisés.

## Contexte
- Mandat : `logs/orchestration_20261106/plan-request.md`. Base vérifiée `3467df4b7426fa15c1ab16ef94687f25a976636d`, branche `stream-21-trace`, arbre propre. Lot distinct du lot documentaire 21 et du gel J4 ; 19-oracle ne fournit aucune entrée.
- Problème : les six `READ_MATCH` de `docs/MAPPING.md` (sec3 l. 52 ↔ `results/e2/e2_cells.csv`) reposent sur une vérification ponctuelle archivée (audit 21 §3, script non suivi). Aucune édition du papier, d'une clé ou d'une colonne n'est contrôlée par `make check`.
- Mesuré en lecture seule à la base :
  - CSV : SHA disque = index = `e315…0823`, 47 lignes, toutes en CRLF.
  - `paper/sec3_theory.tex` : `6bfe…4013`, 0 CR ; `split("\n")` et `splitlines()` coïncident.
  - Ligne 52 : chacun des six littéraux est un jeton `NUM` unique ; `18` est absent.

## Révision de la porte G-T : décision de Codex, non imposée par le chercheur
- G-T (audit 21 §7) est la décision YAGNI de Codex pour le lot documentaire. Elle s'ouvre au premier nombre issu d'un CSV hors E2, ou au premier nombre balisé. Aucune de ces conditions n'est remplie.
- Révision proposée : ouvrir un G-T réduit aux entrées actuelles de MAPPING, puisque leur seule preuve est ponctuelle. Coût estimé : environ 130 lignes d'outil et 150 lignes de test, bibliothèque standard seule, moins d'une seconde dans `make check`.
- Écarts au contrat minimal de G-T :
  - test `tests/test_trace_numbers.py`, au lieu de `test_tools.py`, selon la convention de `test_check_prompts.py` ;
  - ni balises `\E{}` ni balayage de `paper/` ;
  - préfixes de chemin par rôle ;
  - ajout de la vérification du texte source exact et d'un inventaire déclaré.
- Alternative : statu quo, sans code ; les six références restent sans garde exécutable.

## Réemploi (recherche faite)
- **Consommateurs existants.** `grep` ne trouve aucun code qui consomme `MAPPING.md`, `trace_numbers` ou `test_tools` : seulement des documents et des prompts. Aucun outil ne relie la prose LaTeX à un CSV, donc l'outil ne fait doublon avec rien.
- **Repris du script de l'audit §3 :**
  - la regex `NUM`, l'ordre des contrôles et les statuts `READ_MATCH`, `LITERAL_OCCURRENCES_n`, `KEY_ROWS_n`, `EMPTY_OR_NON_FINITE`, `MISMATCH` ;
  - `Decimal(...).quantize(Decimal(1), ROUND_HALF_EVEN)` et le format des lignes de sortie.
  - `ENTRIES` et `BASE`, codés en dur, sont remplacés par la lecture de MAPPING. Les témoins W1–W3 deviennent des tests sur le MAPPING réel.
- **Conventions de `tools/check_prompts.py` :**
  - `ROOT` et `read_bytes().decode("utf-8")` ;
  - les refus par `ValueError`, affichés `trace-numbers: error: …` ;
  - `main(argv) -> int` et `raise SystemExit(main())` ;
  - côté tests, `monkeypatch` de `ROOT` et `capsys`.
- **Conservé sans duplication :** `tests/test_pca_drift_contracts.py::test_e2_cells_crlf_disk_and_index_unchanged`, qui épingle le SHA disque et index, les 47 CRLF et l'attribut `-text`.
- **Écarté :** `experiments/pca_drift_tables.validate_lineage`, spécifique au PCA et qui importe numpy, pandas et jepadrift.

## Fichiers
| Fichier | Action |
|---|---|
| `tools/trace_numbers.py` | nouveau, bibliothèque standard seule |
| `tests/test_trace_numbers.py` | nouveau |
| `docs/MAPPING.md` | ajouts seulement : section `## Check inputs` et une puce d'usage ; table Entries et prose existante inchangées octet pour octet |
| `prompts/wrapups/wrapup-21-trace.md` | wrap-up natif, puis six sections en anglais |
| `logs/stream_21_trace/*.log` | journaux ignorés : RED/GREEN, CLI, pyflakes, `make check` |

- **Codex :** plan canonique `prompts/plans/plan-21-trace.md`, GO, revue, réindexation et Git.
- **Intouchés :** producteurs, bibliothèques, `paper/`, `results/`, Makefile, DEVIATIONS, prompts et CLAUDE.md.

## Format MAPPING : ajout exact, en anglais, entre `## Column definitions` et `## Entries`
```markdown
## Check inputs

`tools/trace_numbers.py` reads only this table and the Entries table. It exits 0 only when both SHA-256 values match, the Entries table holds exactly the declared number of rows and every entry is `READ_MATCH`; `tests/test_trace_numbers.py` runs it at every `make check`. It certifies no more than `READ_MATCH` does.

| Input | Value |
|---|---|
| CSV | `results/e2/e2_cells.csv` |
| CSV SHA-256 | `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` |
| LaTeX | `paper/sec3_theory.tex` |
| LaTeX SHA-256 | `6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013` |
| Entries | 6 |
| Result-bearing occurrences | 19 |
```
Sous « A new entry gives: », ajouter la puce `- the updated Entries count of Check inputs.`

## Interface de `tools/trace_numbers.py`
- **Imports :** `argparse`, `csv`, `hashlib`, `io`, `re`, `decimal`, `pathlib`.
- **`table(text, heading) -> (header, rows)`.** Le titre doit apparaître exactement une fois. La fonction lit la première table pipe qui le suit, avant tout autre titre. Elle exige la ligne de séparation et le même nombre de cellules sur chaque ligne. Une paire de backticks englobante est retirée de chaque cellule.
- **`confined(root, rel, prefix) -> Path`.** Refuse le chemin avant toute ouverture s'il est :
  - absolu, avec un composant `..`, ou non canonique (`str(PurePosixPath(rel)) != rel`) ;
  - hors de `prefix/` ;
  - résolu (liens suivis) hors de `root.resolve()/prefix`, ou différent d'un fichier régulier.
  - `OSError` et `RuntimeError` deviennent des refus.
  - Préfixes : `paper` pour le LaTeX, `results` pour le CSV, `docs` pour le MAPPING (chemin fixe). `data/` n'est donc jamais lisible.
- **`entry_status(entry, lines, header, rows) -> (status, cell, rounded)`.** Ordre de l'audit §3, plus deux statuts :
  1. `LITERAL_OCCURRENCES_n` : le littéral n'est pas exactement un jeton `NUM` de la ligne déclarée.
  2. `UNKNOWN_COLUMN` : une colonne de la clé ou la colonne déclarée manque à l'en-tête CSV.
  3. `KEY_ROWS_n` : la clé complète (toutes ses paires, égalité textuelle) ne sélectionne pas exactement une ligne.
  4. `EMPTY_OR_NON_FINITE` : cellule vide, NA, NaN ou ±Inf, illisible ou non quantifiable. Elle n'est jamais lue comme 0.
  5. `MISMATCH` : l'arrondi diffère du littéral (sans `{,}`) ou de la colonne `Rounded`.
  6. `SOURCE_TEXT_MISMATCH` : le texte de la cellule diffère du `Source text` déclaré.
  7. Sinon, `READ_MATCH`.
- **`check(root, mapping_text) -> list`.** Chaque fichier est lu une seule fois, en binaire. Le SHA-256 porte sur ces octets, le décodage UTF-8 est strict, et le CSV est analysé par `csv.DictReader(io.StringIO(text, newline=""))`. Les mêmes octets sont donc hachés et lus, sans réouverture ni écriture. Refus structurels (`ValueError`) :
  - **tables :** titre ou table absents, en-têtes inattendus ;
  - **Check inputs :** noms différents des six attendus, SHA autre qu'un hexadécimal de 64 caractères, comptes qui ne sont pas des entiers ≥ 1, ou `Result-bearing occurrences` < `Entries` ;
  - **chemins** refusés par `confined` ;
  - **empreinte périmée :** SHA lu ≠ SHA déclaré, pour le CSV comme pour le LaTeX ;
  - **CSV :** pas d'en-tête, noms de colonnes dupliqués, ou ligne de longueur différente (cellule manquante) ;
  - **inventaire :** zéro ligne, nombre de lignes ≠ `Entries`, ou couple (emplacement, littéral) dupliqué ;
  - **ligne de MAPPING :** chemin ≠ LaTeX déclaré, numéro de ligne hors de `[1, n]`, littéral qui n'est pas un jeton `NUM`, lecture ∉ {budget, anytime-valid, exact}, statut déclaré ≠ `READ_MATCH`, ou clé mal formée (sans `=`, nom ou valeur vide, nom répété).
- **`main(argv=None) -> int`.** Aucune option ; argparse sert uniquement à `--help`. Sortie :
```text
trace-numbers: csv results/e2/e2_cells.csv sha256 e315…0823 = declared
trace-numbers: tex paper/sec3_theory.tex sha256 6bfe…4013 = declared
paper/sec3_theory.tex:52 literal '17' | reading exact | key arm=G1, mode=cusum_x, … | column pred_delay | cell '16.71475236584297' | rounded 17 | READ_MATCH
… (one line per entry)
trace-numbers: 6/6 entries READ_MATCH; verified subset 6 of 19 result-bearing occurrences, 13 of 19 not covered (docs/MAPPING.md, Coverage)
trace-numbers: READ_MATCH means literal, cell and rounding agree; it certifies no ARL0, FPR or ADD, no scientific conclusion and no reproduction by the producer; 'exact' names the ARL0-calibrated reading, not the precision of the value
```
- **Codes de sortie :**
  - 0 seulement sans refus et avec k = n ;
  - si k < n : `trace-numbers: FAILED: <n-k> of <n> entries not READ_MATCH`, code 1 ;
  - refus structurel : `trace-numbers: error: …`, code 1.
  - En cas d'échec, aucune ligne de couverture n'est imprimée.
- **Commentaires `# ponytail:` (deux) :**
  - un seul CSV et un seul LaTeX par MAPPING ;
  - arrondi à zéro décimale seulement : un littéral décimal donne `MISMATCH`, donc l'échec reste fermé.

## Tests RED → GREEN : `tests/test_trace_numbers.py`, environ 8 fonctions paramétrées
- **Données de test :**
  - fixtures `tmp_path` construites par le test : CSV en CRLF, `.tex`, MAPPING avec des SHA calculés ;
  - MAPPING réel modifié en mémoire seulement. Chaque `replace` vérifie d'abord une occurrence unique : si MAPPING change, le témoin échoue au lieu de passer à vide.
- **Les huit fonctions :**
  1. **Positif, fixture, via `main`** (`ROOT` monkeypatché) : code 0, `1/1`, couverture affichée. Octets CSV identiques avant et après. Les imports de l'outil sont inclus dans `sys.stdlib_module_names`.
  2. **Positif, MAPPING actuel** : code 0, six lignes `READ_MATCH`, `6 of 19` et `13 of 19`. Le SHA du CSV est inchangé après l'exécution.
  3. **Témoins de l'audit, sur le MAPPING réel :**
     - W1 : entrée 2 en `mean_delay` → `MISMATCH`.
     - W1b : entrée 1 en `mean_delay` → `SOURCE_TEXT_MISMATCH`. 16.7295 arrondit pourtant à 17 : c'est une détection nouvelle.
     - W2 : `17` → `18` → `LITERAL_OCCURRENCES_0`.
     - W3 : `mode` retiré → `KEY_ROWS_3`, six fois.
     - Un chiffre du SHA LaTeX modifié → refus.
     - Ligne 6 supprimée → refus d'inventaire.
  4. **Nombre ou littéral altéré :** la cellule, le littéral dans MAPPING, le littéral dans le `.tex` (SHA mis à jour), `Rounded` et `Source text`.
  5. **Colonne et clé :** colonne absente → `UNKNOWN_COLUMN` ; clé ambiguë → `KEY_ROWS_2` ; clé sans ligne → `KEY_ROWS_0` ; clé mal formée → refus.
  6. **Cellule :** `""`, `NA`, `nan`, `inf` et `-Infinity` → `EMPTY_OR_NON_FINITE` ; ligne courte → refus.
  7. **Égalités d'arrondi :**
     - `16.5` → 16 : `READ_MATCH` avec le littéral `16`, `MISMATCH` avec `17` ;
     - `17.5` → 18 ;
     - `16.500000000000001` → 17 : `Decimal` lit le texte, alors qu'un `float` donnerait 16.
  8. **Chemins, inventaire, empreintes :**
     - chemins refusés avant lecture : absolu, `..`, non canonique, `data/raw/eurofidai/…`, `data/derived/d4_eurofidai/…`, lien vers l'extérieur de `root`, lien vers `data/` dans `root` ;
     - inventaire refusé : table vide, `Entries` ≠ nombre de lignes, doublon, occurrences < entrées ;
     - empreintes : SHA CSV ou LaTeX périmé → refus ;
     - dans ces cas, `main` n'affiche aucune ligne `verified subset`.
- **Séquence :**
  - RED-1 : tests seuls → `ModuleNotFoundError`.
  - RED-2 : outil dont `entry_status` accepte tout → les témoins d'entrée échouent (preuve qu'ils discriminent), les refus structurels passent.
  - GREEN : tous les tests passent.
  - Aucun `xfail` ni `skip` ; aucun test miroir.

## Vérification : chaque commande échoue sur écart
```bash
set -euo pipefail
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
E2=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823; L=logs/stream_21_trace; mkdir -p "$L"
.venv/bin/python tools/trace_numbers.py > "$L/trace_numbers.log"
test "$(grep -c '| READ_MATCH$' "$L/trace_numbers.log")" = 6
.venv/bin/python -m pyflakes tools/trace_numbers.py tests/test_trace_numbers.py
.venv/bin/python -m pytest -q tests/test_trace_numbers.py "tests/test_pca_drift_contracts.py::test_e2_cells_crlf_disk_and_index_unchanged"
test "$(sha256sum < results/e2/e2_cells.csv)" = "$E2  -"
test "$(git show :results/e2/e2_cells.csv | sha256sum)" = "$E2  -"
test "$(grep -c $'\r$' results/e2/e2_cells.csv)" = 47 && test "$(wc -l < results/e2/e2_cells.csv)" = 47
git diff --quiet -- paper results experiments jepadrift tests/test_pca_drift_contracts.py tests/test_floors.py Makefile
test "$(git diff --numstat -- docs/MAPPING.md | cut -f2)" = 0
test "$(git status --porcelain)" = "$(printf '%s\n' ' M docs/MAPPING.md' '?? prompts/GO-stream-21-trace.md' '?? prompts/plans/plan-21-trace.md' '?? prompts/wrapups/wrapup-21-trace.md' '?? tests/test_trace_numbers.py' '?? tools/trace_numbers.py')"
! grep -nE '/home/|/tmp/|/Users/|/root/' tools/trace_numbers.py tests/test_trace_numbers.py docs/MAPPING.md prompts/wrapups/wrapup-21-trace.md
.venv/bin/make check > "$L/make_check.log" 2>&1
```
- `git diff --numstat … | cut -f2` vérifie qu'aucune ligne n'a été retirée de MAPPING.
- Les noms des fichiers de Codex dans l'état Git attendu sont à confirmer par le GO.

## Séquence après le GO écrit
0. Pré-contrôle : `HEAD` = base, ou bien le commit Codex qui n'ajoute que le plan et le GO ; `git status --porcelain` exact.
1. Ajouts dans MAPPING.
2. RED-1.
3. RED-2.
4. GREEN.
5. Vérification.
6. Wrap-up natif, puis `wrapup-21-trace.md`.
7. Arrêt et remise à Codex : ni commit, ni push, ni réindexation.

En cas de quota ou d'erreur : conserver l'état et rapporter. Au plus trois tentatives pour une erreur d'infrastructure.

## Hors périmètre
Gel, `FROZEN.json`, J4 et runner ; JEPA/VAE ; données réelles, D4 et fenêtre monitor ; `dpi_lint`, figures et `appendix_b` ; réécriture de `paper/` ; recalcul des 13 occurrences non couvertes ; PCA ; campagnes E2 ou E3 ; producteurs et bibliothèques épinglés ; dépendances et installations.

## Hypothèses et défauts
- **H1. Métadonnées :** bloc `Check inputs` ajouté (Q2). La prose et la table Entries restent intactes.
- **H2. Clé « complète et unique » :** toutes les paires déclarées, avec égalité textuelle exacte ; colonnes présentes ; exactement une ligne sélectionnée. Aucun schéma de colonnes identifiantes n'est imposé.
- **H3. Position déclarée :** `fichier:ligne`, découpage sur `\n`. Le littéral doit être exactement un jeton `NUM` ; un `17` contenu dans `1{,}710` ne compte pas.
- **H4. Arrondi :** zéro décimale, `ROUND_HALF_EVEN` appliqué à `Decimal(texte)`.
- **H5. Ordre des contrôles :** le texte source est comparé après l'arrondi, si bien que W1 donne `MISMATCH` comme dans l'audit.
- **H6. Lecture :** l'appartenance à {budget, anytime-valid, exact} est vérifiée, pas sa cohérence avec la colonne, qui reste une déclaration de MAPPING. Un READ_MATCH vérifie la déclaration, pas son bien-fondé scientifique.
- **H7. Dépôt choisi :** c'est le `root` passé à `check` (`tmp_path` en test). Le CLI utilise le dépôt de l'outil, sans option `--root`. La forme `paper/ --mapping` du prompt 21, conçue pour les balises `\E{}`, n'est pas reproduite. Aucune cible Makefile : `make check` exécute déjà le test.
- **H8. Fil-piège voulu :** toute modification d'un octet de `sec3_theory.tex` fera échouer `make check`, jusqu'à ce que les lignes soient revérifiées et le SHA du bloc mis à jour. Le CSV a déjà cette propriété.
- **H9. Sentinelle :** le test sur le MAPPING actuel fige seulement 6 et 19 (Q5).
- **H10.** Claude exécute `make check` une fois, en fin de lot ; Codex le rejoue au commit.

## Questions (défaut entre crochets)
- **Q1, bloquante.** Révision de G-T : ouvrir maintenant ce G-T réduit [recommandé], ou garder le statu quo sans code ?
- **Q2, bloquante.** Représentation des métadonnées :
  - (a) [défaut] bloc `Check inputs`, prose intacte ; les deux SHA figurent aussi dans les puces « Source of entries », qui ne sont pas lues par l'outil ;
  - (b) pas de bloc : l'outil extrait chemins et SHA des puces `**CSV.**` et `**LaTeX.**`, et le compte « 6 of 19 » de la table Coverage ;
  - (c) bloc, et retrait des SHA des puces.
- **Q3.** Note de validation séparée : [non, les preuves vont dans le wrapup et les journaux], ou une courte note `docs/audits/stream_21_trace_validation_2026_11_06.md` ?
- **Q4.** Entrée DEVIATIONS pour l'écart au prompt 21 (§4 `\E{}`, nom `test_tools.py`) : [non, tracé par le plan et le GO ; DEVIATIONS hors liste], ou `C-trace-numbers-scope` ?
- **Q5.** Sentinelle : [compteurs seuls], ou aussi les six couples (emplacement, littéral) ?

## Décision GO intégrée — Codex, 2026-11-06, 20:10 UTC

Décision dans le mandat d'orchestration délégué par le chercheur. **GO de ce seul outil de traçabilité**, avec les arbitrages ci-dessous, prioritaires sur les propositions natives divergentes. Le plan natif est archivé sans modification dans `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `ddf45a147204320993758763ece4ee516c5b041ede13ecb8422c689ae4f568ca`. Plan et GO sont enregistrés avant exécution.

### Réponses Q1–Q5

- **Q1 : ouvrir G-T réduit.** La décision documentaire précédente est révisée par Codex pour apporter une garde exécutable aux six références existantes. Aucune révision n'est attribuée personnellement au chercheur ; aucun gel J4 ou autre outil du prompt 21 n'est ouvert.
- **Q2 : option (a), bloc Check inputs.** Préserver intégralement les six lignes Entries et la prose historique. Ajouter aux métadonnées proposées une septième ligne `Key columns`, valeur `arm, mode, background, dim, sr_annual, gamma`. La lecture déclarée, les deux empreintes et les comptes sont des contrats explicites, sans liste de cellules codée en dur dans l'outil.
- **Q3 : pas de note de validation supplémentaire.** Preuves, commandes, statuts et SHA dans le wrapup et les journaux ignorés.
- **Q4 : pas d'entrée DEVIATIONS.** Cette réduction du périmètre est tracée par le plan et le GO ; aucun producteur, protocole scientifique ou papier n'est modifié.
- **Q5 : sentinelle dans le test réel.** Fixer les comptes 6 et 19, les six couples (emplacement, littéral) déjà recensés et les six noms de colonne de clé. L'outil de production lit les entrées de MAPPING ; cette sentinelle de test ne le remplace pas.

### Clé complète et refus structurels

- Réviser H2 : une clé unique ne suffit pas. Les noms de chaque clé doivent être exactement ceux de `Key columns`, distincts, non vides et présents dans l'en-tête CSV. Ensuite seulement vérifier l'unicité de la ligne sélectionnée et les autres conditions.
- Un retrait de `background` ou de `dim`, même si la ligne reste unique, doit échouer. Le témoin W3 qui retire `mode` peut désormais être refusé pour clé incomplète, avant son ancienne ambiguïté à trois lignes ; consigner cette différence sans changer l'audit historique.
- Le bloc Check inputs contient exactement ses sept noms attendus, chacun une seule fois. Les colonnes de clé y sont non vides et distinctes.
- Garder les refus des chemins qui s'échappent, symlinks hors du préfixe autorisé, inventaires vides/incomplets/dupliqués, empreintes périmées, en-têtes CSV dupliqués, lignes de longueur incorrecte et cellules non finies. Aucune lecture de contenu ne précède sa validation de chemin.
- Pour la limite « zéro décimale », un littéral comportant un point décimal est explicitement refusé ; ne pas le laisser passer par une simple égalité Decimal entre 17 et 17.0. Ajouter le témoin correspondant.
- Le succès rapporte uniquement le sous-ensemble 6 sur 19. Il ne qualifie ni les treize occurrences restantes ni une lecture scientifique. Le label « exact » et l'approximation de diffusion restent distingués.

### Contrôles et propriété

- Claude exécute RED→GREEN, les témoins, pyflakes, la CLI réelle et le contrôle J1 ciblé. Le `make check` complet obligatoire est effectué par Codex après wrapup et réindexation, via le hook avant commit ; supprimer sa répétition dans la session Claude (révision H10).
- Les fichiers Claude sont exactement ceux du tableau Fichiers, avec les ajouts MAPPING nécessaires ci-dessus ; `docs/MAPPING.md` reste un diff d'ajouts. Aucun autre document, outil ou test historique n'est modifié.
- `prompts/plans/plan-21-trace.md` et `prompts/GO-stream-21-trace.md` sont les fichiers Codex : relever leurs SHA avant et après, ne pas les modifier.
- Modèle `claude-opus-5-5`, effort **Max inchangé jusqu'à clôture**, même session interactive, aucun sous-agent. Sortie du mode plan par le mécanisme natif, après ce GO écrit.
- Wrap-up natif puis six sections anglaises avec résultats réels, puis arrêt pour revue Codex. Aucun Git modifiant, commit, push ou réindexage par Claude.
- J1 disque/index/47 CRLF reste scellé ; D8 reste FAIL. Aucun producteur, résultat, papier, donnée réelle, PCA, JEPA/VAE ou J4 ; aucune nouvelle expérience, installation ou dépendance.
