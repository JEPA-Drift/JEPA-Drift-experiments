# Plan lot 21-dpi — garde lexical DPI `tools/dpi_lint.py` (proposition native, en attente du GO écrit de Codex)

Aucun code, test ou édition du dépôt avant ce GO ; aucun sous-agent ; Graphify/jCodeMunch non utilisés.

## Contexte et constat (lecture seule)
- Mandat `logs/orchestration_20261106/plan-request.md`, prompt 21 §5. Base `46c24923957ec505947016118def9453284bd1bc`, branche `stream-21-dpi`, arbre propre.
- Corpus : `paper/sec3_theory.tex` (SHA `6bfebdd0…4013`, 112 l.) et `paper/appA_proofs.tex` (`4a5469c8…2a30`, 46 l.) ; ASCII, 0 CR, 10 lignes de commentaire en tête, aucun `%` en milieu de ligne, aucun `\%`, aucune abréviation `e.g.`/`i.e.`.
- Un seul mot à radical `increas`/`creat` : sec3 l. 25, col. 12, « creates no information ». C'est une négation correcte, que le scan `creates?.*information` de l'audit 21 §6 signale à tort.
- Réemploi : aucun outil DPI ni lint de prose dans le dépôt (grep : documents seulement). Réemployés sans modification : `confined` de `tools/trace_numbers.py` (chemin canonique sous un préfixe, liens résolus, fichier régulier, `OSError`/`RuntimeError` → refus) et les conventions de trace : `ROOT`, refus `ValueError` affiché `<outil>: error: …`, `main(argv) -> int`, tests `tmp_path`/`monkeypatch`/`capsys`, contrôle AST des imports.

## Justification YAGNI : révision de la porte G-D par Codex
- G-D (audit 21 §7) s'ouvrait « si la prose théorique s'étend » : condition non remplie. Le mandat l'ouvre pour remplacer le scan ponctuel par un garde reproductible exécuté à chaque `make check`. Révision de Codex, non attribuée au chercheur.
- Valeur : fil-piège pour la prose à venir (`sec:problem`, `sec:method`, `sec:exp-floors` sont citées mais absentes). Coût ≈ 60 lignes d'outil et 130 de tests, stdlib, < 1 s. Alternative : statu quo (scan archivé).

## Contrat lexical exact (toutes les regex en `re.IGNORECASE`, sauf COMMENT)
```text
COMMENT (?<!\\)%[^\n]*   remplacé par autant d'espaces (lignes et colonnes conservées)
VERB    (?<!non-)\b(?:increas(?:e|es|ed|ing)|creat(?:e|es|ed|ing|ion))\b
TAIL    (?:[^\w.;:!?]+\w+){0,6}?[^\w.;:!?]+(?:KL|information|divergences?)\b      match à la fin du verbe
AFTER   \W+(?:no|neither)\b                                                      match à la fin du verbe
BEFORE  \b(?:no|not|never|cannot|nor|neither|without)\b(?:[^\w.,;:!?]+\w+){0,2}[^\w.,;:!?]+\Z   sur le texte jusqu'au verbe
```
- Occurrence : un VERB suivi de TAIL, soit 0 à 6 mots (mot = suite de lettres, chiffres ou `_` ; un nom de macro compte) puis l'objet, sans `. ; : ! ?` entre eux. Virgules, `~`, `{}`, `$`, `\`, `--` et retours à la ligne sont admis. Chaque verbe est évalué séparément : une négation antérieure n'absorbe pas un verbe suivant.
- Ce motif unique couvre « increase(s|d) … (KL|information|divergence) » et « create(s) information » du prompt, plus les formes en -ing et les noms (« an increase in KL », « creation of information »).
- NEGATED si AFTER (premier mot après le verbe : `no`/`neither`) ou BEFORE (négateur parmi les 3 mots avant le verbe, sans virgule ni `. ; : ! ?`) ; sinon FLAG. `non-` collé au verbe : pas d'occurrence.
- Aucun autre traitement LaTeX : maths et macros restent du texte (`\mathrm{KL}` compte). Formulation ambiguë : toujours FLAG (p. ex. « increases the information » relatif à la classe linéaire, correct par la Prop. hierarchy).
- FLAG = demande de revue, jamais verdict de fausseté ; NEGATED = négation reconnue, pas une validation.

## Limites (heuristique lexicale : ne prouve rien sur le texte)
- Non vus : paraphrases (« adds information », « more information than x »), passif et ordre inverse (« information is created », « the KL increases »), trou > 6 mots, ponctuation dans le trou (« by 0.5 nats », « i.i.d. »).
- NEGATED à tort : « not only/merely increases », « no less information », négation proche portant sur un autre verbe (« does not create but increases »).
- FLAG à tort (sens sûr) : `\emph{no}`, `none`, négation lointaine ou après virgule (« does not, in general, increase »), contractions, environnements `comment`/`\iffalse`.
- Hors corpus : `.bib`, sous-dossiers de `paper/`, `docs/`, prompts, wrapups.

## Fichiers et interfaces (code, docstrings, sorties et wrapup en anglais)
| Fichier | Action |
|---|---|
| `tools/dpi_lint.py` | nouveau ; stdlib + `tools.trace_numbers.confined` ; docstring d'usage, aucune note séparée |
| `tests/test_dpi_lint.py` | nouveau ; découvert par pytest et pyflakes de `make check` |
| `prompts/wrapups/wrapup-21-dpi.md` | wrap-up natif, puis six sections anglaises |
| `logs/stream_21_dpi/*.log` | journaux ignorés |

Codex : `prompts/plans/plan-21-dpi.md`, `prompts/GO-stream-21-dpi.md`, revue, réindexation, Git. Intouchés : `paper/`, `tools/trace_numbers.py` et son test, `docs/` (MAPPING compris), Makefile, `results/`, CLAUDE.md.
- `find(text) -> [(offset, words, negated)]` : `words` = portée verbe→objet, blancs normalisés (aucune phrase entière citée).
- `scan(root) -> (files, hits)` : corpus `sorted(root/"paper"/"*.tex")`, non récursif. Toutes les entrées passent `confined(root, "paper/<nom>", "paper")` avant la première lecture ; hit = fichier, ligne et colonne du verbe, `words`, `negated`.
- Refus `ValueError` de `scan` : aucun `paper/*.tex` (dossier absent ou sans `.tex`) ; entrée refusée par `confined` (lien hors `paper/`, vers `data/raw/eurofidai/`, cassé, dossier) ; octets non UTF-8 ; fichier vide hors commentaires. Une entrée refusée bloque tout le corpus.
- `main(argv=None) -> int` : `python -m tools.dpi_lint` depuis la racine, sans option (argparse pour `--help`). Sortie attendue sur le corpus actuel, code 0 :
```text
paper/sec3_theory.tex:25:12: NEGATED 'creates no information'
dpi-lint: files 2 (paper/appA_proofs.tex, paper/sec3_theory.tex); hits 1: FLAG 0, NEGATED 1
dpi-lint: pattern lint only: zero FLAG does not show the text is DPI-consistent, and a FLAG requests review without judging the sentence
```
- Ligne FLAG : `<fichier>:<l>:<c>: FLAG '<words>': wording suggests creating or increasing information/KL; review it against the DPI (KL of z <= KL of (x, C)); not a verdict on the sentence`. Après le résumé : `dpi-lint: FLAGGED: k of n hits to review`, code 1. Refus : `dpi-lint: error: …` seul, code 1. Code 0 seulement sans refus ni FLAG.
- Deux `# ponytail:` : motif verbe→objet seulement (ordre inverse sous GO) ; aucune dérogation (un FLAG revu et conservé passe par un GO).

## Tests discriminants : `tests/test_dpi_lint.py`, 8 fonctions paramétrées
1. Positifs, un FLAG chacun : « increases KL », « Increased the Kullback--Leibler divergence », « INCREASES INFORMATION », « an increase in the information rate », « by increasing $\mathrm{KL}(P_1\|P_0)$ », « creates information », « Creates⏎information », « creates new drift information », « the creation of information », « increases, in the latent space, the KL », « a 5\% shift creates information », « creates % x⏎information ».
2. Négations du contrat, un NEGATED et zéro FLAG : la phrase existante, « creates neither KL nor information », « No encoder creates information », « cannot increase the KL », « never increases information », « does not increase the divergence », « without creating information ».
3. Bornes en paires : négateur au 3ᵉ mot avant le verbe → NEGATED, au 4ᵉ → FLAG ; « the encoder, not the data, creates information » → FLAG ; trou de 6 mots → FLAG, de 7 → aucune occurrence ; `.`, `;` ou `:` dans le trou → aucune ; « creates no new bias, but increases the KL » → un NEGATED et un FLAG.
4. Sans motif, aucune occurrence : « The KL divergence grows with $N$ », « increases the Sharpe ratio » (SR_z > SR_x permis par N3), « a non-increasing information sequence », ligne `% creates information`.
5. Format via `main` (`ROOT` monkeypatché) : occurrence à cheval sur les l. 3–4 → ligne FLAG exacte (l. 3, colonne du verbe, mots sur une ligne), résumé, ligne FLAGGED, code 1.
6. Corpus réel : code 0, ligne NEGATED `paper/sec3_theory.tex:25:12`, 0 FLAG, les deux fichiers lus, octets de `paper/` identiques avant et après. Mutations d'une copie dans `tmp_path` (« creates no information » → « creates information », → « creates new information ») → FLAG en `paper/sec3_theory.tex:25:12`.
7. Refus (code 1, `dpi-lint: error:` seul, aucune ligne FLAG ni résumé) : `paper/` absent ; `.bib` seul. Puis, à côté d'un `.tex` valide : lien hors racine ; lien vers `data/raw/eurofidai/x.tex` (cible contenant « creates information », jamais affichée) ; lien cassé ; dossier `x.tex` ; fichier vide ou fait de commentaires ; octets non UTF-8.
8. Imports de l'outil ⊆ stdlib ∪ {`tools`} (AST, comme `test_trace_numbers`).
- Séquence : RED-1, tests seuls → `ImportError` ; RED-2, négation forcée à faux → 2, 3 et 6 échouent ; RED-3, négation forcée à vrai → 1, 3, 5 et les mutations de 6 échouent ; GREEN. Aucun `skip`/`xfail`.

## Vérification après GO (chaque commande échoue sur écart)
```bash
set -euo pipefail
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
L=logs/stream_21_dpi; mkdir -p "$L"; E2=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
.venv/bin/python -m pytest -q tests/test_dpi_lint.py tests/test_trace_numbers.py "tests/test_pca_drift_contracts.py::test_e2_cells_crlf_disk_and_index_unchanged"
.venv/bin/python -m pyflakes tools/dpi_lint.py tests/test_dpi_lint.py
.venv/bin/python -m tools.dpi_lint > "$L/cli.log"; test "$(wc -l < "$L/cli.log")" = 3
grep -qx "paper/sec3_theory.tex:25:12: NEGATED 'creates no information'" "$L/cli.log"
grep -qx "dpi-lint: files 2 (paper/appA_proofs.tex, paper/sec3_theory.tex); hits 1: FLAG 0, NEGATED 1" "$L/cli.log"
test "$(sha256sum < paper/sec3_theory.tex)" = "6bfebdd022d55ca37abb0e695b946bd61b8d9e44012cea5165bac6bebf7c4013  -"
test "$(sha256sum < paper/appA_proofs.tex)" = "4a5469c84f12bb5902fee9f68a783b64c45b77b11f1172c5bf4b81f7603c2a30  -"
test "$(sha256sum < results/e2/e2_cells.csv)" = "$E2  -" && test "$(git show :results/e2/e2_cells.csv | sha256sum)" = "$E2  -"
git diff --quiet HEAD -- paper results docs tools/trace_numbers.py tests/test_trace_numbers.py Makefile CLAUDE.md
test "$(git status --porcelain)" = "$(printf '%s\n' '?? prompts/GO-stream-21-dpi.md' '?? prompts/plans/plan-21-dpi.md' '?? prompts/wrapups/wrapup-21-dpi.md' '?? tests/test_dpi_lint.py' '?? tools/dpi_lint.py')"
test -z "$(grep -nE '/home/|/tmp/|/Users/|/root/' tools/dpi_lint.py tests/test_dpi_lint.py prompts/wrapups/wrapup-21-dpi.md || true)"
```
- Également : seuls commentaires `# ponytail:` (assertion `tokenize`), lignes ≤ 120 caractères. Lignes Codex de `git status` à confirmer par le GO.
- `make check` complet : hook Codex. D8 reste FAIL, non examiné.

## Séquence après GO écrit
0. Pré-contrôle : `HEAD`, `git status --porcelain` exact, SHA des fichiers Codex avant et après.
1. RED-1 → RED-2 → RED-3 → GREEN, puis la vérification.
2. Wrap-up natif, puis `wrapup-21-dpi.md`.
3. Arrêt pour revue Codex : ni Git ni réindexation. Quota ou erreur : état conservé et rapporté, au plus 3 tentatives d'infrastructure.
- Hors périmètre : gel/FROZEN/J4, runner, tableaux, figures, résultats, expériences, données réelles, PCA, JEPA/VAE, nouvelles mesures ou dépendances, commandes illustratives des documents historiques. 21-appendix ne fournit rien.

## Hypothèses et défauts
- H1 Corpus fixe sans argument CLI (précédent trace H7) ; « chemin hors périmètre » = entrée de `paper/` résolue ailleurs ou non régulière.
- H2 Fichier vide hors commentaires : refus par fichier (corpus « vide » au sens strict).
- H3 Commentaires non analysés (non rendus) ; `\%` reste du texte.
- H4 Trou ≤ 6 mots, fenêtre de négation ≤ 3 mots ; la virgule ne coupe que la fenêtre de négation (biais vers FLAG).
- H5 Lignes NEGATED imprimées pour la revue, sans effet sur le code de sortie.
- H6 Le test réel n'épingle ni les empreintes de `paper/` (sec3 l'est déjà par MAPPING) ni la liste des fichiers : un `.tex` ajouté sans FLAG passe.

## Questions bloquantes (défaut entre crochets)
- Q1. Fil-piège : le test réel exige 0 FLAG, donc toute prose signalée bloque `make check` jusqu'à reformulation ou GO [oui, sans dérogation] ?
- Q2. Lexique : motif verbe→objet du prompt, formes en -ing et noms compris [oui] ; ou ajout de l'ordre inverse et du passif, au prix de FLAG sur des énoncés légitimes (« the KL increases with N ») ?
- Q3. `confined` importé, CLI `python -m tools.dpi_lint` [oui] ; ou copie locale de quatre lignes pour garder `python tools/dpi_lint.py` ?

## Décision GO intégrée

Décision de Codex, par délégation d'orchestration : **GO explicite pour le lot borné 21-dpi**, après revue de la proposition native. Cette section remplace tout élément contradictoire de la proposition conservée ci-dessus ; elle ne modifie ni le modèle ni l'effort Max de la session existante.

1. Q1 = oui : le test du corpus courant exige zéro FLAG, sans liste de dérogations. Q2 = motif verbe vers objet, formes nominales et en -ing comprises, sans extension au passif ou à l'ordre inverse. Q3 = réemploi de `confined`, invocation `python -m tools.dpi_lint`. Aucune copie ni modification du helper publié.
2. Les faux NEGATED connus ne sont pas acceptés comme simple limite : `not only`, `not merely`, `not just`, `no less` et `no doubt` ne doivent pas supprimer un FLAG. Dans le doute, FLAG demande une revue ; ce n'est pas une décision scientifique sur la phrase.
3. La portée de négation s'arrête à `but`, `yet`, `however`, ainsi qu'à un verbe candidat antérieur. Le témoin `does not create but increases information` doit signaler `increases` ; une négation portant sur `create` ne l'exonère pas. Tester aussi un connecteur sans virgule et deux verbes candidats.
4. Le statut de commentaire de `%` respecte la parité des antislashs contigus qui le précèdent : nombre pair, dont zéro, = début de commentaire ; nombre impair = pourcentage échappé. Remplacer les commentaires par des espaces de même longueur en conservant les retours à la ligne. Témoins 0, 1, 2 et 3 antislashs ; pas de parseur LaTeX général.
5. Ajouter ces témoins discriminants avant l'implémentation. Conserver les négations réellement prises en charge, les bornes 6/3 mots, les refus de chemins/corpus et les témoins positifs de la proposition. Sur le corpus actuel : exactement une occurrence NEGATED `creates no information`, zéro FLAG, octets des deux sources inchangés.
6. Sortie et docstring indiquent que zéro FLAG ne démontre aucune conformité sémantique à la DPI. L'ordre inverse, les paraphrases et les constructions hors fenêtre restent des limites déclarées. Aucun changement de prose pour satisfaire artificiellement le garde.
7. Propriété Claude : `tools/dpi_lint.py`, `tests/test_dpi_lint.py`, `prompts/wrapups/wrapup-21-dpi.md`, journaux ignorés `logs/stream_21_dpi/`. Propriété Codex : le présent plan, le GO, les revues et la clôture Git. Les fichiers Codex sont lus et hachés avant/après, jamais modifiés par Claude.
8. Exécuter TDD et vérifications ciblées avec la .venv et l'environnement déterministe du projet, puis le wrap-up natif et les six sections anglaises du fichier de wrapup. S'arrêter pour revue Codex. Le `make check` complet obligatoire sera exécuté à la clôture par le hook ; ne pas le doubler maintenant. Ni commit, push ni réindexation par Claude.
9. Maintenir la session interactive existante Opus 5.5 Max, sans sous-agent, redémarrage, changement d'effort ou purge du contexte. Au plus deux instances orchestrées simultanément. Aucun PCA nouveau, données réelles, JEPA/VAE, J4, expérience, résultat, tableau, figure, seuil ou dépendance nouvelle.

Base de revue : `46c24923957ec505947016118def9453284bd1bc`. Proposition native archivée à l'identique dans `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `a3ab3119e80cda29da3f2af3b176980edb9a4b54da6ec652fa0f93c08cf930d3`. La revue anglaise est dans `logs/orchestration_20261106/codex-plan-review.md`. Le présent GO ne clôture pas le périmètre complet du stream 21.
