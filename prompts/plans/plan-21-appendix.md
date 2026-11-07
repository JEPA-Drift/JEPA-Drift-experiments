# Plan lot 21-appendix — inventaire des paramètres déclarés D5/F1–F4 (`tools/appendix_b.py`)

## Contexte
Base `46c24923957ec505947016118def9453284bd1bc`, branche `stream-21-appendix`, arbre propre. Prompt 21, tâche 6 ; mandat `logs/orchestration_20261106/plan-request.md`. Lus : `CLAUDE.md`, prompt 21, `docs/sections/injection.md`, `configs/e3.yaml` § `d5`, `configs/pca_drift_benchmark.yaml` § `synthetic`, `tools/trace_numbers.py` et ses tests. Aucune configuration JEPA/VAE, aucune donnée ouverte, aucun `make j1`. Sorties de `table()` et de PyYAML contrôlées en lecture seule (`python -B`, arbre resté propre).

## Ce qu'ajoute la génération à la note (mesuré)
- La note n'a qu'une table à valeurs de paramètres : `parameter | values` sous `## D5 — Monte Carlo backgrounds`, 4 lignes ((α, β) (0.08, 0.90) ; ν 7 ou `None` ; ρ 0.40 ou `None` ; burn-in 1000 days), sans lien aux configurations ni empreinte. Les deux sections déclarent 13 feuilles (`d5` : 5, `synthetic` : 8).
- Apport 1, provenance : chemin relatif, `section.clé` et SHA-256 de chaque entrée.
- Apport 2, 7 valeurs configurées absentes de la note, rendues en NOT_DOCUMENTED : `d5.T_clean` 941, `d5.backgrounds` ["t7", "gaussian"], `synthetic.sr_annual_A` 4.0, `.rotation_deg` 30.0, `.rotation_pair` [1, 2], `.C_axes` [10, 20], `.C_I_target` 3.0.
- Apport 3, 4 absences par source, rendues en NOT_CONFIGURED : `d5` ne déclare ni ν ni ρ ; `synthetic` ni (α, β) ni burn-in. Le code y emploie des littéraux non déclarés (E3 t7 : `sim.Garch`, donc `sim.NU = 7`, `experiments/e3_calibration.py:341-344` ; PCA : `garch_panel(T, N, 0.0, 0.0, nu, …, burn=0)`, `experiments/pca_drift_benchmark.py:405-407`). Une fusion sans statut attribuerait (0.08, 0.90) et 1000 aux fonds PCA.
- Apport 4, comparaison exacte des 6 recouvrements note/configuration (aujourd'hui 6 MATCH) : toute dérive future devient une ligne DIVERGENT.
- Rien d'autre : aucun nombre nouveau, aucune KL, gain, délai, FPR ou estimation.
- Exclus de la note : tables non paramétriques (API, clés `meta`, garanties) ; tables analytiques (r → information ; SR → `I_target`, une KL) ; table des familles (noms et formules ; `table()` y retire une paire de backticks non englobante, « `subspace` (S), `r` » → « subspace` (S), `r » : contrat inadapté) ; paramètres en prose (grilles r/θ de F4, κ, `SR_ASSET_B`, H_ref/H_det), faute d'extracteur.

## Réemploi
- `tools/trace_numbers.py`, non modifié : `table()` (titre exact unique, cellules verbatim, refus d'une table irrégulière ; conforme pour la table D5, dont aucune cellule n'est entourée de backticks) et `confined()` (chemin POSIX relatif canonique, préfixe, échappement par lien, fichier régulier). Import `from tools.trace_numbers import confined, table`, comme les tests ; invocation `python -m tools.appendix_b`.
- PyYAML 6.0.3 épinglé (`requirements.lock:38`) ; stdlib `json` (`allow_nan=False` refuse NaN/inf), `decimal`, `hashlib`, `re`, `argparse`, `pathlib`. Motif AST d'imports de `tests/test_trace_numbers.py:82-86`.
- Aucun import de `jepadrift`, `experiments`, numpy ou torch ; aucun sous-processus.

## Contrat de `tools/appendix_b.py` (≈110 lignes, docstrings d'une ligne)
- Sources fermées, constantes et ordonnées : `configs/e3.yaml` § `d5` et `configs/pca_drift_benchmark.yaml` § `synthetic` (`confined(…, "configs")`) ; `docs/sections/injection.md`, table sous `## D5 — Monte Carlo backgrounds`, en-tête exact `parameter`, `values` (`confined(…, "docs")` puis `table()`). Les autres sections YAML (dont `real` et ses chemins) sont analysées par PyYAML, jamais exploitées ni ouvertes.
- Feuilles configurées : mappings imbriqués aplatis en `section.clé[.sous-clé]`, ordre du document ; une liste est une feuille ; texte = `json.dumps(v, allow_nan=False)`.
- Lignes documentées : libellé, cellule verbatim, jetons `[-−]?[0-9]+(?:\.[0-9]+)?|\bNone\b`.
- `LINKS`, 6 correspondances déclarées (position 1-based) : `d5.alpha`→(α, β)[1], `d5.beta`→(α, β)[2], `d5.burn`→burn-in[1], `synthetic.rho`→ρ (`factor_rho`)[1], `synthetic.backgrounds.SYNTH_T7_EQUICORR`→ν[1], `synthetic.backgrounds.SYNTH_GAUSS_EQUICORR`→ν[2].
- Statuts :
  - MATCH : null ↔ `None` ; nombre ↔ égalité `Decimal` du jeton (0.9 = 0.90).
  - DIVERGENT : jeton absent ou différent, booléen ou texte face à un jeton.
  - NOT_DOCUMENTED : feuille sans lien, ou libellé lié absent de la table.
  - NOT_CONFIGURED : une ligne par couple (source, libellé documenté) sans clé liée présente.
  - Absence = « — » ; aucune valeur copiée d'une origine vers l'autre ; DIVERGENT montre les deux.
- Refus (`ValueError` préfixée par l'entrée → `appendix-b: error: …`, code 1, rien écrit) :
  - chemins : entrée hors préfixe ou échappant par lien ;
  - YAML : syntaxe invalide ; clé dupliquée (sous-classe `yaml.SafeLoader` ; PyYAML garde sinon la dernière en silence, vérifié) ; section absente, non mapping ou vide ; mapping imbriqué vide ; clé non chaîne ou contenant `.`, `|` ou un saut de ligne ; valeur non finie (`.nan`, `.inf`, y compris dans une liste) ou hors JSON (date) ; `|` dans un texte de valeur ;
  - note : titre absent ou dupliqué, en-tête différent, table vide, libellé dupliqué, cellule non finie (`nan`, `inf`, `∞`), UTF-8 invalide.
- Sortie : `--out`, défaut `logs/21-appendix/appendix_b.md` ; chemin POSIX relatif canonique sous `logs/`, suffixe `.md`, parent existant résolu sous `logs/` ; écriture exclusive `open(…, "xb")` (fichier ou lien préexistant → refus) ; affiche `appendix-b: wrote <rel> sha256 <hex>` et les comptes par statut. Code 0 dès l'écriture, même avec DIVERGENT : inventaire, pas une porte.
- Fragment anglais, octets déterministes (ni horodatage, ni chemin absolu, ni commit) : titre ; ligne de réserve « declared generation and injection parameters only; values hard-coded in experiment code are not inventoried; not an executed configuration nor a J4 freeze; no KL, gain, delay or FPR value » ; table `Input | Section | SHA-256` (3 lignes) ; table `Source | Key | Configured | Row | Documented | Status`.
- Attendu à la base : 17 lignes (6 MATCH, 7 NOT_DOCUMENTED, 4 NOT_CONFIGURED, 0 DIVERGENT) ; SHA-256 `e3.yaml` `6e3857382200f0b7…`, `pca_drift_benchmark.yaml` `79d2b5e557074384…`, `injection.md` `8708a1df9d55975a…`.

## Tests RED → GREEN : `tests/test_appendix_b.py` (≈6 fonctions paramétrées, fixtures `tmp_path`)
1. Sentinelle courante : les 17 triplets (source, clé ou libellé, statut) exacts, les textes des 6 MATCH, les comptes, les empreintes égales au `hashlib` des fichiers.
2. `main` sur fixture : code 0 et empreinte affichée = SHA-256 du fichier ; second appel → code 1, octets inchangés ; deux sorties distinctes identiques octet à octet ; entrées inchangées ; aucun `str(tmp_path)` dans le fragment ; imports ⊆ stdlib ∪ {`yaml`, `tools`}.
3. Divergence et absence explicites : `beta` 0.85 → DIVERGENT, 0.85 et (0.08, 0.90) visibles ; échange alpha/beta → 2 DIVERGENT (position, pas appartenance) ; `d5.burn` supprimé → (e3, burn-in) NOT_CONFIGURED ; note « 500 days » → DIVERGENT ; libellé renommé → NOT_DOCUMENTED et 2 NOT_CONFIGURED ; GAUSS null → 5 → DIVERGENT ; `rho: 0.40` → MATCH (témoin positif) ; clé ajoutée → NOT_DOCUMENTED ; colonne Configured jamais remplie depuis la note.
4. Refus d'entrées : un témoin par refus du contrat, message attendu, code 1, `--out` inexistant ensuite.
5. Chemins : `configs/e3.yaml` lien vers l'extérieur ; `--out` absolu, `..`, `./`, `//`, hors `logs/`, suffixe autre que `.md`, parent absent, parent lien vers l'extérieur, lien préexistant à la cible.
- RED : collecte en échec `ModuleNotFoundError` (outil absent), journal `logs/21-appendix/red.log`. GREEN : tests du lot et `tests/test_trace_numbers.py` verts, pyflakes propre.

## Séquence après GO écrit
1. SHA-256 du plan et du GO ; 2. RED (test seul) ; 3. GREEN (outil) ; 4. réception : `mkdir -p logs/21-appendix`, génération, relance refusée ; 5. contrôles ci-dessous ; 6. wrap-up natif puis `prompts/wrapups/wrapup-21-appendix.md` (six sections anglaises) ; arrêt. Ni `make check` (clôture Codex), ni commit, push ou réindexation.

## Vérification (chaque commande échoue sur écart)
```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
.venv/bin/python -m pytest -q tests/test_appendix_b.py tests/test_trace_numbers.py
.venv/bin/pyflakes tools/appendix_b.py tests/test_appendix_b.py
.venv/bin/python -m tools.appendix_b > logs/21-appendix/reception.log && cat logs/21-appendix/reception.log
H=$(sha256sum < logs/21-appendix/appendix_b.md | cut -c1-64); grep -q "sha256 $H" logs/21-appendix/reception.log
! .venv/bin/python -m tools.appendix_b && test "$(sha256sum < logs/21-appendix/appendix_b.md | cut -c1-64)" = "$H"
J1=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
test "$(sha256sum < results/e2/e2_cells.csv | cut -c1-64)" = "$J1" && test "$(git show :results/e2/e2_cells.csv | sha256sum | cut -c1-64)" = "$J1" && test "$(grep -c $'\r$' results/e2/e2_cells.csv)" = 47
git diff --quiet HEAD -- tools/trace_numbers.py configs docs paper results Makefile
test "$(git status --porcelain -- tools tests)" = "$(printf '?? tests/test_appendix_b.py\n?? tools/appendix_b.py')"
```

## Limites
- Valeurs déclarées seulement : les littéraux de code restent invisibles ; l'inventaire ne décrit pas ce que les exécutions emploient.
- `LINKS` est un savoir de domaine manuel (6 lignes, visibles dans la colonne Row) ; un paramètre nouveau sans lien reste NOT_DOCUMENTED ou NOT_CONFIGURED, jamais apparié.
- Jetons simples : unités ignorées (« 1000 days » → 1000) ; formes groupées ou à exposant (« 1,000 », « 1e3 ») non prises en charge (`# ponytail:` ceiling) : DIVERGENT en général, faux MATCH seulement si un fragment coïncide (« 1,000 » contre 1).
- Flottants YAML comparés par leur repr Python ; idiomes YAML 1.1 (`yes` booléen, `1e3` chaîne) rendus tels quels, jamais convertis.
- Fragment ignoré, ni suivi ni porté dans `paper/` ; régénérer exige un autre `--out` ou une suppression manuelle. Ni configuration exécutée, ni gel J4, ni MAPPING. D8 reste FAIL +5,2833 %, non examiné.
- Hors périmètre : FROZEN/J4, runner, données réelles, PCA/JEPA/VAE, expériences, nouvelle mesure, relance ou remplacement d'artefact scellé, Graphify/jCodeMunch, lot 21-dpi.

## Hypothèses et défauts
- H1 : « tables de paramètres de la note » = la seule table à valeurs (D5).
- H2 : fragment et statuts en anglais (artefact de type `docs/sections/`) ; plan, GO et échanges en français.
- H3 : le parent de `--out` est créé par la réception, pas par l'outil.
- H4 : `C_I_target` (cible d'information déclarée) est inventorié comme paramètre déclaré ; aucune KL n'est calculée.
- H5 : propriété — Claude : `tools/appendix_b.py`, `tests/test_appendix_b.py`, `prompts/wrapups/wrapup-21-appendix.md`, `logs/21-appendix/` ; Codex : `prompts/plans/plan-21-appendix.md`, `prompts/GO-stream-21-appendix.md`, revue, réindexation, Git, `make check`.

## Questions (défaut entre crochets ; aucune ne bloque si les défauts sont retenus)
- Q1 Tables de la note : [D5 seule] ; ou aussi la colonne SR de « Amplitude conventions » (sans `I_target`), au prix d'un statut d'appartenance (`sr_annual_A` 4.0 ∈ {0.5, 1, 2, 4}).
- Q2 Code de sortie : [0 si écrit, 1 si refus] ; ou 2 en présence de DIVERGENT.
- Q3 Invocation : [`python -m tools.appendix_b`] ; ou chargement par chemin (`importlib`, +3 lignes) pour `python tools/appendix_b.py`.
- Q4 Clés YAML dupliquées : [refus, sous-classe `SafeLoader` de 5 lignes] ; ou comportement PyYAML (dernière valeur gardée).
- Q5 Sentinelle sur les fichiers courants : [oui ; elle casse volontairement à toute modification des trois entrées] ; ou fixtures seules.
- Q6 Sources : [les trois ci-dessus] ; `configs/e10.yaml` § `d5` (variantes de robustesse, `factor_rho`, lu par `experiments/e10_robustness.py:753`) et `configs/e1.yaml` restent hors mandat, non ouverts.

## Décision GO intégrée

Décision de Codex, par délégation d'orchestration : **GO explicite pour le lot borné 21-appendix**, après revue de la proposition native. Cette section remplace tout élément contradictoire de la proposition conservée ci-dessus ; elle ne modifie ni le modèle ni l'effort Max de la session existante.

1. Q1 = D5 seule pour la table documentaire, plus les feuilles des deux sections YAML sélectionnées ; Q2 = code 0 après écriture d'un inventaire bien formé, même en présence de divergence, code 1 pour un refus ; Q3 = réemploi de `table` et `confined`, CLI module ; Q4 = refus des clés YAML dupliquées ; Q5 = sentinelle sur les trois entrées actuelles ; Q6 = ces trois sources seules.
2. Le titre, la réserve et les statuts doivent annoncer un **inventaire partiel** : table numérique D5 et paramètres déclarés des sections `d5` et `synthetic`. Ni schéma complet F1–F4 ni Annexe B exhaustive ; les paramètres en prose et dans les autres tables, les littéraux de code et les configurations exécutées ne sont pas inventoriés. Les 7 feuilles sans lien ne sont pas « absentes de la note » : certaines valeurs sont présentes ailleurs dans celle-ci.
3. Remplacer NOT_DOCUMENTED par **UNMAPPED_CONFIG** et NOT_CONFIGURED par **UNMAPPED_DOC**. Ces statuts décrivent uniquement les correspondances sélectionnées, jamais une absence globale dans la note ou dans le code. Le texte source, la clé et les six liens manuels restent visibles. Une clé liée supprimée doit être rendue comme absence, y compris alpha seul quand beta reste présent ; aucune complétion depuis l'autre origine.
4. Interdit de conclure MATCH à partir d'un fragment numérique. Analyser la cellule documentée entière selon des formes bornées adaptées aux quatre lignes D5 connues, en préservant son texte intégral. Comparaison par Decimal pour les nombres réellement reconnus ; null correspond seulement au None explicite. Pour une forme non prise en charge : statut **UNSUPPORTED_DOC_VALUE**, jamais MATCH. Pas de parseur mathématique général ni de conversion d'unités.
5. Vérifier la structure et l'arité de chaque forme liée : paire alpha/beta, alternatives nombre/None, scalaire burn-in avec unité `days`. `1,000` ou `1e3` contre 1 ne doivent jamais donner MATCH ; une unité changée en `weeks`, une forme malformée ou un jeton numérique supplémentaire ne doivent pas être silencieusement ignorés. Une forme groupée ou exponentielle peut être correctement reconnue en entier, ou rester explicitement non prise en charge.
6. Ajouter ces témoins TDD avant code, avec permutation alpha/beta, absence contre None, différence de valeur, refus des doublons, contrôle des entrées/sorties et déterminisme. État de référence : 17 lignes, 6 MATCH, 7 UNMAPPED_CONFIG, 4 UNMAPPED_DOC, 0 DIVERGENT et 0 UNSUPPORTED_DOC_VALUE.
7. Garder le helper publié intact. L'inadéquation de `table()` aux cellules multi-backticks de la table des familles justifie son exclusion déclarée ; elle n'autorise ni correction du helper dans ce lot ni prétention de couverture complète. Les trois sources, paper/, MAPPING, résultats et Makefile restent inchangés. Lire une configuration contenant des chemins ne donne aucune autorisation d'ouvrir ces chemins.
8. Sortie Markdown déterministe uniquement sous `logs/`, écriture exclusive, chemin relatif confiné, SHA-256 et comptes explicites. Aucun nombre de résultat nouveau, aucune KL calculée ; `C_I_target` reste une entrée déclarée. Code 0 signifie seulement qu'un inventaire a été écrit.
9. Propriété Claude : `tools/appendix_b.py`, `tests/test_appendix_b.py`, `prompts/wrapups/wrapup-21-appendix.md`, journaux ignorés `logs/21-appendix/`. Propriété Codex : le présent plan, le GO, les revues et la clôture Git. Les fichiers Codex sont lus et hachés avant/après, jamais modifiés par Claude.
10. Vérifications ciblées avec la .venv et l'environnement déterministe, puis wrap-up natif et six sections anglaises ; arrêt pour revue Codex. Le `make check` complet obligatoire sera exécuté par le hook à la clôture ; ne pas le doubler maintenant. Ni commit, push ni réindexation par Claude.
11. Même session Opus 5.5 Max, sans changement d'effort, purge, redémarrage ni sous-agent ; au plus deux instances orchestrées simultanément. Pas d'expériences PCA nouvelles, données réelles, JEPA/VAE, J4/FROZEN, runner, campagnes, tableaux ou figures.

Base de revue : `46c24923957ec505947016118def9453284bd1bc`. Proposition native archivée à l'identique dans `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `901eafc201486fa3f4e3231840908d9dfc4a4e05e9a90455803584184efe20b7`. La revue anglaise est dans `logs/orchestration_20261106/codex-plan-review.md`. Le présent GO ne clôture pas le périmètre complet du stream 21.
