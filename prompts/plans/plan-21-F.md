# Plan 21-F — vérificateur de gel sur fixtures synthétiques

Base : `47d85dc977547409fc6f6d71dcf5488eb935d7d5`, branche `stream-21-F`.
Proposition native révisée : 533 lignes, SHA-256 `3b8a72a31b2d87793ca38d9636d86d24783fcff16ee8fa6423a259d4f504a086`.
Le texte natif ci-dessous est conservé comme contrat technique. Son statut PLAN ONLY décrit la phase antérieure au GO ; la section finale « Décision GO intégrée » fixe maintenant le périmètre exécutable.
Autorité : GO Codex au titre du mandat délégué par l'amorçage de continuation et la demande d'exécution autonome. Aucune signature personnelle du chercheur n'est attribuée.

---
# Plan natif 21-F — `tools/freeze_config.py` sur dépôts Git synthétiques (PLAN ONLY, révision 1)

## 0. Statut
- Phase **PLAN ONLY** (`logs/stream_21_F/mission-plan.md`) : aucun code, test, Python, import du projet, simulation ni expérience ; aucune mutation Git ni `make check`. Seule écriture : ce fichier.
- Base `47d85dc977547409fc6f6d71dcf5488eb935d7d5` (= `main` = `origin/main`), branche `stream-21-F`, worktree `~/.codex/worktrees/1a88/JEPA-Drift-experiments`, session `921f284c-d6ae-4f31-b270-3f881fb33718`, Opus 5.5 effort Max, sans sous-agent.
- Propriété Codex : `prompts/plans/plan-21-F.md`, `prompts/GO-stream-21-F.md`, `docs/DEVIATIONS.md`, et le rapport non suivi `docs/audits/streams_01_31_continuation_2026_11_07.md` présent dans ce worktree (jamais lu, modifié ni indexé par Claude).
- Point Codex intégré : baseline exclusive close à **1003 PASS, 5 skips D4**, sans skip torch/PCA ; créneau libéré ; **aucun GO de code ni de test**.
- NO-GO technique Codex sur la révision 0 (`prompts/NO-GO-stream-21-F.md`) : cinq corrections bornées ci-dessous ; les autres sections sont inchangées.

## Révision 1 : réponses au NO-GO
1. **Présence des racines.** Les onze racines sont exigées dans C (HEAD pour `write`) et sur disque, avec leur type ; chaque racine-répertoire contient au moins un fichier couvert (§4.3, §4.7–§4.9). Témoins K1–K3, mutant ajouté.
2. **Création concurrente.** Témoins W9 (insertion entre le dernier contrôle d'absence et l'ouverture créatrice) et W10 (échec de `fsync` après substitution du nom). Le nettoyage n'est plus présenté comme atomique (§4.8, §11).
3. **Chemins possédés.** Le §7 accepte exactement les fichiers Codex (plan, GO, NO-GO, rapport), sans les modifier : leurs empreintes sont relevées avant la première écriture. Le wrapup n'entre qu'après son créneau.
4. **RED exploitable.** Fixtures construites par Git et l'oracle du test seuls, outil importé paresseusement, aucun squelette ; RED-0 prouvé par des assertions CLI (§6.1, §6.2).
5. **Gel unique.** L'usage unique par lignée est explicité ; un regel, l'activation et toute évolution de schéma relèvent d'un autre plan et d'un autre GO (§4.4, §11).

## 1. Objet et exclusions
- **Objet.** Le plus petit `tools/freeze_config.py` complet (bibliothèque standard seule) et `tests/test_freeze_config.py`, testés **uniquement** sur des dépôts Git synthétiques temporaires.
- **Exclusions.**
  - `configs/FROZEN.json` réel, cible `make freeze`, toute modification du Makefile.
  - Câblage des gardes pré-J4 des expériences, runner (lot R), activation J4.
  - Lecture de données, accès monitor, run réel ; contenu EUROFIDAI ou lignes 2020+ dans les tests.
  - Toute modification des dépendances numériques et des sorties scellées E2/E3/PCA.

## 2. Revue critique de plan-21-rest §5.2/§6 → décisions arrêtées
| # | Proposition 21-rest | Défaut | Décision 21-F |
|---|---|---|---|
| D1 | Code identifié par `git diff C HEAD` et `git status` | Dépend des filtres, attributs, `core.fsmonitor` et de l'index ; `git status` peut réécrire l'index | SHA-256 des octets de chaque fichier couvert, dans une table unique `files`. Git ne sert qu'aux arbres et à l'historique (plomberie). |
| D2 | `frozen_paths` stocké et égal à une constante | Redondant | Retiré. La couverture est la constante `POLICY` de l'outil, lui-même couvert ; le schéma `jepadrift-freeze/1` la désigne. |
| D3 | POLICY avec `tools/benchmark_runner.py`, sans les manifestes | Fichier absent ; emplacement du runner non tranché (prompt 21 : `jepadrift/` ; 21-rest : `tools/`) | Retiré. Les deux manifestes deviennent des racines-fichiers. |
| D4 | Sceau : un seul ajout `--diff-filter=A` | Fragile avec les fusions ; ne voit ni une modification suivie d'un retour, ni un gel antérieur à C | Historique linéaire `C..HEAD` ; S enfant de C, qui n'ajoute que FROZEN ; FROZEN absent de toute l'histoire de C ; aucun commit après S ne touche `POLICY`, FROZEN ou l'approbation. |
| D5 | Approbation : SHA du blob à C | Nature de l'objet non dite | Provenance hachée : chemin et SHA-256, document suivi dans C et inchangé ensuite. **Aucune interprétation du contenu.** |
| D6 | `write` confiné aux fixtures par procédure seulement | Aucune barrière dans le code | Deux gardes codées (§4.8). |
| D7 | Q13 : sentinelle de test sur l'absence de FROZEN réel | Contraire à « tests uniquement synthétiques » | Devient une commande de validation shell en lecture seule (§7). |
| D8 | `lstat` par composant, puis `O_NOFOLLOW` final | Course possible entre contrôle et ouverture | Parcours relatif à des descripteurs (`dir_fd`), `O_NOFOLLOW` à chaque composant, contrôle `fstat`. |
| D9 | — | Limites, isolation Git et codes d'erreur non spécifiés | §3 à §4.9. |

## 3. Interface publique (figée)
**Module.**
- `tools/freeze_config.py`, bibliothèque standard seule : aucun import de `tools.*`, `jepadrift`, `experiments`, `yaml` ni d'un paquet numérique.
- Lancement par `python tools/freeze_config.py` ou `python -m tools.freeze_config`.
- La docstring de module porte le contrat de la CLI ; docstrings d'une ligne ; seuls commentaires `# ponytail:`.

**Constantes.**
| Nom | Valeur |
|---|---|
| `ROOT` | `Path(__file__).resolve().parents[1]` |
| `SCHEMA` | `"jepadrift-freeze/1"` |
| `FROZEN` | `"configs/FROZEN.json"` |
| `POLICY` | `("Makefile", "conda-torch.lock", "configs", "conftest.py", "data/derived/MANIFEST.json", "docs/manifests/d4_manifest.json", "experiments", "jepadrift", "requirements.lock", "requirements.txt", "tools/freeze_config.py")` |
| `APPROVAL` | `re.compile(r"prompts/GO-[A-Za-z0-9][A-Za-z0-9._-]*\.md")`, appliqué par `fullmatch` |
| `PROJECT_ROOT_COMMIT` | `"32a55c8d6e16dc74f79f7cd17e61e5fb73d89332"` : unique commit racine du projet, relevé en lecture |
| `MAX_FROZEN_BYTES` | `1048576` |
| `GIT_TIMEOUT` | `60` secondes par appel Git |
| `CODES` | `("ROOT", "GIT", "ABSENT", "LINK", "FORMAT", "SEAL", "CHANGED", "COVERAGE", "HASH", "APPROVAL", "EXISTS", "PROJECT", "IO")` |

**API.**
- `class FreezeError(Exception)`, construite par `FreezeError(code, detail)`. Elle porte les attributs `code` (élément de `CODES`) et `detail`, et `str(err) == f"{code}: {detail}"`.
- `check(root=ROOT) -> dict` : lecture seule. Rend `{"commit", "seal", "approval", "files", "freeze_id"}`, où `files` est le nombre de fichiers et `freeze_id` le SHA-256 des octets de FROZEN. Lève `FreezeError` sinon.
- `write(root, approval) -> dict` : rend `{"path": FROZEN, "sha256", "commit", "files"}`. Lève `FreezeError` sinon.
- `main(argv=None) -> int`.
- Découpage interne, non contractuel : `_git`, `_root`, `_open`, `_walk`, `_tree`, `_parse`, `_canonical`. Les tests n'appellent que l'API publique et les constantes.

**CLI.**
```
python tools/freeze_config.py --check [--root DIR]
python tools/freeze_config.py --write --approval prompts/GO-<id>.md [--root DIR]
```
- **Options.**
  - `--check` et `--write` forment un groupe exclusif requis.
  - `--approval` est exigé avec `--write` et refusé avec `--check` (`parser.error`).
  - `--root` vaut `ROOT` par défaut.
- **Sorties**, sur la sortie standard, préfixées `freeze-config:` :
  - `check` : `freeze-config: OK commit <C> seal <S> approval <path> files <n> freeze_id <sha256>`, puis la mise en garde.
  - `write` : `freeze-config: wrote configs/FROZEN.json sha256 <h> commit <C> files <n>`, puis `freeze-config: not committed; seal with one commit whose only parent is <C> and whose only change adds configs/FROZEN.json`, puis la mise en garde.
  - Refus : `freeze-config: error: <CODE>: <detail>`.
    - Les chemins sont relatifs au dépôt ; au plus 5 chemins sont cités, suivis du compte.
    - Aucun message ne contient le chemin de la racine.
- **Mise en garde** (texte anglais dans le code). Un check réussi fige les octets des fichiers de la politique au commit C et ceux du document d'approbation. Il ne lit aucun fichier de données, ne vérifie aucun octet de données contre les manifestes, n'interprète pas le document d'approbation et n'autorise aucun run.
- **Codes de sortie :** 0 succès ; 1 refus, quel que soit le code de `CODES` ; 2 usage (argparse).

| Code | Sens |
|---|---|
| ROOT | Racine absente ou non répertoire, hors Git, hors sommet d'arbre de travail, nue ou superficielle ; fichier de greffes présent ; HEAD sans commit ; format d'objet autre que SHA-1 |
| GIT | Échec, absence ou délai dépassé d'une commande Git (infrastructure) |
| ABSENT | `configs/FROZEN.json` absent : état attendu avant J4 |
| LINK | Lien symbolique à un composant quelconque, fichier non régulier, entrée d'arbre 120000, substitution détectée pendant le contrôle |
| FORMAT | Taille, UTF-8, JSON strict, schéma exact ou octets non canoniques |
| SEAL | C, S ou historique de FROZEN non conformes |
| CHANGED | Commit postérieur à S touchant une racine de `POLICY` |
| COVERAGE | Ensemble de fichiers non conforme : racine absente, de type inattendu ou sans fichier couvert ; fichier non suivi ou ignoré, manquant ; entrée en trop ou en moins ; nom non portable ; sous-module |
| HASH | Octets du disque ≠ FROZEN ou ≠ blob de C, ou fichier modifié pendant la lecture |
| APPROVAL | Motif, suivi, modification ou empreinte de l'approbation |
| EXISTS | Cible d'écriture déjà présente : fichier, lien ou lien pendant |
| PROJECT | Écriture hors fixture refusée (garde 21-F) |
| IO | Erreur d'entrée-sortie en lecture, ou en écriture après nettoyage |

## 4. Politique canonique
### 4.1 Racine
- `Path(root).resolve(strict=True)` doit être un répertoire.
- Git confirme ensuite :
  - un dépôt non nu, dont `--show-toplevel` égale la racine résolue ;
  - un dépôt non superficiel ;
  - l'absence de fichier au chemin `--git-path info/grafts` ;
  - un `HEAD^{commit}` de 40 hexadécimaux.
- Les liens situés au-dessus de la racine sont résolus une fois ; aucun lien n'est accepté en dessous.
- `check` accepte tout dépôt, y compris le projet, puisqu'il ne fait que lire.

### 4.2 FROZEN : lecture, JSON strict, schéma exact
- **Lecture.** Ouverture sans suivi de lien (§4.7), fichier régulier exigé, `st_size ≤ MAX_FROZEN_BYTES` vérifié avant la lecture.
- **Analyse.** Décodage UTF-8 strict, puis `json.loads` :
  - les clés dupliquées sont refusées à tout niveau (`object_pairs_hook`) ;
  - `NaN`, `Infinity` et `-Infinity` sont refusés (`parse_constant`) ;
  - `ValueError` et `RecursionError` deviennent FORMAT.
- **Schéma exact.**
  - Clés `{"schema", "commit", "files", "approval"}`, avec `schema == SCHEMA`.
  - `commit` : 40 hexadécimaux minuscules.
  - `files` : objet non vide `{chemin: sha256}`.
  - `approval` : objet aux clés exactes `{"path", "sha256"}`.
  - Toute valeur d'un autre type est refusée : nombre, booléen, `null`, liste.
- **Chemins de `files`.**
  - Chemin POSIX relatif canonique ; chaque composant suit `[A-Za-z0-9_.-]+` et diffère de `.` et `..`.
  - Il égale une racine-fichier de `POLICY` ou se trouve sous une racine-répertoire.
  - Il diffère de `FROZEN`.
- **Autres champs.** `approval.path` respecte `APPROVAL` ; chaque SHA-256 compte 64 hexadécimaux minuscules.
- **Octets canoniques.**
  - Les octets lus doivent égaler exactement `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n"`, en ASCII.
  - C'est le motif `canon` du runner PCA, réécrit sans importer ce module scellé.
  - `freeze_id` est le SHA-256 de ces octets.

### 4.3 Couverture et identité : code, configurations, manifestes
- **Ensemble couvert.**
  - Tout fichier régulier sous les racines de `POLICY`, sous-répertoires compris.
  - Exceptions : les répertoires réels nommés `__pycache__`, et `configs/FROZEN.json`.
  - Les règles d'ignorance de Git ne masquent rien : un fichier ignoré autre que `__pycache__` est refusé.
  - Les répertoires vides internes ne sont pas couverts.
- **Présence des racines.**
  - Les onze racines doivent exister dans l'arbre de C (de HEAD pour `write`) et sur disque, avec leur type.
  - Les huit racines-fichiers : entrée blob 100644 ou 100755, et fichier régulier.
  - `configs`, `experiments` et `jepadrift` : arbre, et répertoire réel contenant au moins un fichier couvert (FROZEN et `__pycache__` exclus).
  - Absence, type inattendu ou racine-répertoire sans fichier couvert : COVERAGE. Lien : LINK.
- **Suivi.**
  - Chaque fichier couvert doit figurer dans l'arbre de C, en mode 100644 ou 100755.
  - Fichier non suivi ou ignoré : COVERAGE. Entrée de C absente du disque : COVERAGE.
  - Entrée 160000 (sous-module) : COVERAGE. Entrée 120000 (lien suivi) : LINK.
  - L'index n'est jamais lu : seuls comptent les octets du disque et les arbres des commits.
- **Égalités exigées par `check`.**
  - Les clés de `files` égalent les chemins de C sous `POLICY` ; sinon COVERAGE, avec les manquants et les surplus listés.
  - Pour chaque fichier, une seule lecture calcule deux empreintes :
    - le SHA-256, qui doit égaler `files[chemin]` ;
    - l'identifiant de blob Git, SHA-1 de `blob <taille>\0<octets>` (`usedforsecurity=False`), qui doit égaler le blob de C.
  - Sinon HASH.
- **Catégories.** Elles se déduisent du chemin :
  - code : `experiments`, `jepadrift`, `tools/freeze_config.py` ;
  - configurations : `configs`, hachées comme octets, sans aucune analyse YAML ;
  - manifestes : les deux fichiers ;
  - environnement : `Makefile`, `conftest.py` et les fichiers de verrouillage.
- **Manifestes.** Seuls leurs octets sont figés. Aucun fichier de données n'est lu ni vérifié contre eux (témoin P5).

### 4.4 Sceau, commits ultérieurs, branches et base
- **C.** C est le champ `commit` de FROZEN : un objet commit existant, ancêtre strict de HEAD.
- **Linéarité.** `rev-list --topo-order --reverse --parents C..HEAD` ne contient que des commits à parent unique. S est le premier de la liste, et son parent égale C.
- **Contenu de S.** `diff-tree -r -z --name-status C S` se réduit à l'ajout de `configs/FROZEN.json`, en mode 100644 dans S.
- **Gel antérieur.** `rev-list --full-history C -- configs/FROZEN.json` est vide : aucun gel avant C, même retiré ensuite.
- **Usage unique.** En conséquence, le schéma `jepadrift-freeze/1` ne sert qu'une fois par lignée.
  - Dès qu'un FROZEN est apparu dans l'histoire, même retiré ensuite, aucun nouveau gel ne peut passer `check` avec ce vérificateur. Une nouvelle approbation n'y suffit pas.
  - Un regel, l'activation J4 et toute évolution de schéma demandent un autre plan et un autre GO.
- **FROZEN figé depuis S.** `rev-list C..HEAD -- configs/FROZEN.json` vaut `[S]`, et les octets de FROZEN sur disque égalent le blob de S. Sinon SEAL.
- **Commits autorisés après S.**
  - Ils restent linéaires.
  - Ils ne touchent pas `POLICY` : `rev-list C..HEAD -- <POLICY>` vaut `[S]`, sinon CHANGED.
  - Ils ne touchent pas l'approbation, sinon APPROVAL.
  - Restent libres : `docs/` (hors manifestes), `results/`, `paper/`, `prompts/` (hors approbation), `tests/`, `figures/`.
- **Règle par commit.** Une modification suivie d'un retour sur un fichier gelé reste refusée.
- **Branches et base.**

  | Mutation | Résultat |
  |---|---|
  | Passage sur une ligne sans S | ABSENT si FROZEN quitte le disque, sinon SEAL |
  | Réécriture de C : rebase, nouvelle base, contenu identique sur un autre parent | SEAL (C absent ou non ancêtre) |
  | Réécriture des seuls commits postérieurs à S, ou du message de S (même parent, même ajout) | Accepté : S est défini par sa structure, son hachage n'est pas enregistré |
  | Fusion après C | SEAL |

### 4.5 Approbation et chemins protégés
- **Motif.** Pour `--approval`, le motif `APPROVAL` est vérifié avant toute lecture. Il impose un seul niveau sous `prompts/`, donc jamais un chemin de `POLICY`.
- **`write`.** L'approbation est suivie à HEAD (= C), en mode 100644, et ses octets sur disque égalent le blob de HEAD.
- **`check`.**
  - L'approbation figure dans l'arbre de C, et aucun commit de `C..HEAD` ne la touche.
  - Ses octets sur disque égalent le blob de C, et leur SHA-256 égale `approval.sha256`.
- **Nature.** Le document est une **provenance hachée**, pas une autorisation analysée.
  - Aucun mot-clé, aucune signature, aucun verdict n'est lu.
  - La fixture déclare explicitement ne pas être une approbation, et elle passe.
  - L'autorité réelle relève de la revue humaine.
- **Chemins protégés.**
  - Aucune racine ne se trouve sous `data/raw/` ni sous `data/derived/d4_eurofidai/`. `data/` n'est atteint que par la racine-fichier `data/derived/MANIFEST.json`.
  - L'outil n'ouvre jamais un chemin lu dans FROZEN, sauf l'approbation après validation de son motif.
  - `.git/` n'est lu que par Git, à un `lstat` près sur le chemin des greffes. `logs/` n'est jamais lu.

### 4.6 Isolation Git
- **Appel.** `subprocess.run` reçoit une liste d'arguments, sans shell :
  - `cwd` est la racine résolue, `timeout=GIT_TIMEOUT` ;
  - les sorties sont lues en octets, avec `-z` dès qu'un chemin apparaît ;
  - un code de retour inattendu, un délai dépassé ou un Git introuvable donnent GIT.
- **Environnement.**
  - `os.environ` est privé de **toute** variable `GIT_*`.
  - Sont ensuite fixés :
    - `GIT_CONFIG_NOSYSTEM=1` et `GIT_CONFIG_GLOBAL=os.devnull` ;
    - `GIT_CEILING_DIRECTORIES=<parent résolu de la racine>` ;
    - `GIT_NO_REPLACE_OBJECTS=1` et `GIT_NO_LAZY_FETCH=1` ;
    - `GIT_OPTIONAL_LOCKS=0`, `GIT_LITERAL_PATHSPECS=1`, `GIT_TERMINAL_PROMPT=0` ;
    - `LC_ALL=C`.
  - Ces variables sont documentées par git(1) dans la version installée 2.51.1, vérifiée en lecture.
- **Commandes.**
  - Plomberie seulement : `rev-parse`, `merge-base --is-ancestor`, `rev-list`, `ls-tree`, `diff-tree`.
  - Ni `status` ni `diff` porcelaine : donc ni filtres, ni fsmonitor, ni pilote de diff externe, ni rafraîchissement d'index.
  - Seuls des identifiants déjà validés (40 hexadécimaux) sont passés comme révisions.
- **Refus (ROOT).** Fichier de greffes présent, car aucune variable documentée ne le neutralise ; dépôt superficiel ; format d'objet SHA-256.

### 4.7 Liens, courses et limites
- **Ouvertures.** Toutes partent d'un descripteur de la racine :
  - chaque répertoire intermédiaire par `os.open(nom, O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=parent)` ;
  - le fichier final par `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`.
- **Contrôle.** `fstat` doit montrer un répertoire ou un fichier régulier ; sinon LINK.
  - `ELOOP` donne LINK.
  - `ENOTDIR` signale un composant attendu comme répertoire qui n'en est pas un. Il donne COVERAGE pour une racine ou son parent, y compris `configs` pendant la lecture de FROZEN, et APPROVAL pour l'approbation.
- **Énumération.**
  - `os.scandir(fd)`, puis `os.stat(nom, dir_fd=fd, follow_symlinks=False)` pour chaque entrée.
  - Lien, FIFO, socket ou périphérique : LINK, sans ouverture.
  - Après ouverture, `(st_dev, st_ino)` est comparé entre `lstat` et `fstat` ; une substitution donne LINK.
  - Pile explicite, sans récursion Python.
- **Limites.**
  - FROZEN ≤ 1 MiB ; lecture en blocs de 1 MiB.
  - Un nombre d'octets lus différent de `st_size` donne HASH (« changed while reading »).
  - 60 s par appel Git ; messages bornés à 5 chemins.
  - Le nombre de fichiers est borné de fait par la taille de FROZEN (environ 10⁴ entrées). `write` refuse aussi un FROZEN canonique de plus de 1 MiB.

### 4.8 Écriture : gardes fixtures, création exclusive, nettoyage
**Ordre de `write`.**
1. **Garde d'emplacement**, avant tout appel Git : la racine résolue doit se trouver strictement sous `Path(tempfile.gettempdir()).resolve()`, sinon PROJECT.
2. Motif `APPROVAL`.
3. Racine (§4.1).
4. **Garde projet** : si `rev-parse --verify --quiet PROJECT_ROOT_COMMIT^{commit}` réussit, PROJECT. Cette garde couvre tout worktree et tout clone complet du projet.
5. FROZEN absent du disque sous toute forme (sinon EXISTS) et de toute l'histoire de HEAD (sinon SEAL).
6. Présence et type des onze racines dans HEAD et sur disque, puis couverture et octets égaux à HEAD (COVERAGE, HASH ou LINK).
7. Approbation (§4.5).
8. Enregistrement canonique ≤ 1 MiB.
9. Création.

**Création.**
- Le descripteur de `configs/` est obtenu sans suivi de lien.
- `os.open("FROZEN.json", O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0o644, dir_fd=…)` ; `EEXIST` donne EXISTS, sans toucher au fichier présent.
- Le contrôle d'absence de l'étape 5 n'est pas la barrière : seul `O_EXCL` l'est, y compris contre une insertion concurrente (W9).
- Boucle d'écriture complète, `os.fsync`, puis fermeture.

**Échec après création.**
- Le nom n'est supprimé que si `os.stat(nom, dir_fd=…, follow_symlinks=False)` désigne encore l'inode du descripteur créé (`st_dev`, `st_ino`).
- Sinon, le nom n'est pas touché, et IO signale un fichier partiel non supprimé (W10).
- Une substitution reste possible entre cette dernière vérification et `unlink`. C'est une limite POSIX : aucune suppression conditionnelle atomique n'est promise.
- Aucun fichier temporaire, aucune autre écriture.

**Plafonds `# ponytail:`.**
- L'écriture est limitée aux dépôts synthétiques du répertoire temporaire jusqu'au GO d'activation J4, qui remplacera les deux gardes.
- Pas de publication atomique : un arrêt brutal laisse un fichier partiel, que `check` refuse et que `write` n'écrase pas.

### 4.9 Ordre de `check`
1. Racine.
2. Lecture de FROZEN (ABSENT, LINK, FORMAT ; COVERAGE si `configs` n'est pas un répertoire).
3. Format et schéma.
4. Sceau (SEAL).
5. Commits postérieurs à S (CHANGED, APPROVAL).
6. Présence et type des racines dans C, puis arbre de C et `files` (COVERAGE, LINK).
7. Présence et type des racines sur disque, puis parcours (COVERAGE, LINK, HASH).
8. Approbation sur disque (LINK, APPROVAL).

Le premier échec produit un refus unique. Aucune écriture, aucun verrou optionnel.

## 5. Fichiers
**Possédés après GO (liste finie).**
- `tools/freeze_config.py` (nouveau).
- `tests/test_freeze_config.py` (nouveau).
- `prompts/wrapups/wrapup-21-F.md`, dans le créneau de clôture seulement.
- Journaux ignorés `logs/stream_21_F/{red0,green1,green2,green3,green4,green5,green_final,mutants,controls}.log` et `logs/stream_21_F/codex_files.sha256`.

**Jamais modifiés.**
- `Makefile`, `configs/`, `experiments/`, `jepadrift/`, `results/`, `paper/`.
- `docs/`, dont MAPPING, DEVIATIONS et le rapport Codex.
- Les autres fichiers de `tools/` et de `tests/`.
- Le plan, le GO et le NO-GO de Codex (`prompts/NO-GO-stream-21-F.md`), `logs/stream_21_F/mission-plan.md`, `logs/stream_21_F/baseline-make-check.log`, la mémoire.

## 6. TDD
### 6.1 Fixtures synthétiques
- **Gabarit.**
  - Construit une fois par module (`tmp_path_factory`), copié pour chaque test (`shutil.copytree(..., symlinks=True)`).
  - Construit uniquement avec Git et l'oracle du test (hashlib et `json.dumps` canonique) : C, FROZEN oracle, puis S. Jamais avec `write` ni `check`.
  - L'outil est importé paresseusement dans chaque test (`importlib.import_module`) : la collecte et le montage des fixtures réussissent sans lui.
  - Git de test isolé comme au §4.6, avec un `HOME` temporaire.
  - Identité `Fixture Synthetic <fixture@example.invalid>` ; dates fixes croissantes (`2001-01-01T00:00:00+00:00`, puis +1 min par commit). Les commits sont donc déterministes.
- **Contenu.**
  - Toutes les racines de `POLICY`, avec des octets synthétiques :
    - `configs/sub/b.yaml`, imbriqué ;
    - `configs/raw.yaml`, volontairement non-YAML ;
    - `jepadrift/sub/m.py` ;
    - `tools/freeze_config.py`, texte factice et non l'outil réel ;
    - les deux manifestes, contenant `{"synthetic_fixture": true}`.
  - Un fichier de données factice `data/derived/d0/panel.bin`.
  - Des fichiers libres sous `docs/`, `results/`, `paper/` et `tests/`.
  - Un `.gitignore` (`__pycache__/`, `ignored.bin`) et un `.pyc` factice ignoré.
  - `prompts/GO-fixture-synthetic.md`, au texte : « Synthetic fixture text for tests/test_freeze_config.py; not a GO, not an approval, no decision. »
- **Interdits.**
  - Contenu privé, données réelles, lignes datées.
  - Identité ou formulation du chercheur.
  - Tout appel des fonctions sur le `ROOT` réel.
  - Les pièges de chemins protégés (P7) sont des FIFO vides, sans contenu.

### 6.2 Étapes
**Préalable à toute exécution.**
- Lire le registre `~/JEPA-Drift-experiments/logs/orchestration_20261107/execution-19-21-state.json`.
- Le propriétaire et le verrou sont ceux qu'exige le GO 21-F ; la commande passe par `flock -n`, sans boucle d'attente.
- Interpréteur `.venv/bin/python -B`, avec l'environnement épinglé.

**Étapes.**
1. **RED-0.** Tests complets, **sans fichier d'outil ni squelette**. La preuve RED exige :
   - une collecte et un montage des fixtures sans erreur ;
   - T0 vert, indépendamment de l'outil ;
   - quatre assertions CLI en échec, lancées en sous-processus `-I -B` sur des fixtures oracle :
     - `--check` sur S : code 0 et ligne OK attendus ;
     - 1 octet modifié : code 1 et `HASH` ;
     - fixture à C : code 1 et `ABSENT` ;
     - `--write` à C : code 0 et octets égaux à l'oracle.
   - Les autres cas échouent à l'import paresseux. Ils restent des exigences de comportement et ne comptent pas comme preuve.
   - R2 exige aussi le texte d'usage d'argparse, que le code 2 rendu par l'interpréteur sans fichier ne fournit pas.
   - Les comptes sont consignés.
2. **GREEN-1** (création du module ; racine, Git, lecture et format de FROZEN) : R1, F1–F10, L1 (FROZEN, `configs`), S9, X1 (cas GIT).
3. **GREEN-2** (sceau, historique, isolation) : S1–S8, G1–G3.
4. **GREEN-3** (couverture, présence des racines, parcours, courses) : P5, P7, M1–M6, K2, K3, L1–L3, X1 (cas IO).
5. **GREEN-4** (approbation) : A1–A5.
6. **GREEN-5** (écriture, gardes, nettoyage, CLI) : W1–W10, K1, P1–P4, P6.
7. **Final.**
   - Fichier entier vert, sans `skip` ni `xfail` ; pyflakes ; mutants ; contrôles du §7.
   - Puis `REVIEW_READY stream-21-F`, et attente du créneau de clôture Codex.

### 6.3 Témoins décisifs (code attendu)
| ID | Témoin | Attendu |
|---|---|---|
| T0 | Auto-contrôle de la fixture, sans l'outil : FROZEN oracle canonique ; S enfant unique de C, qui n'ajoute que FROZEN | Vert dès RED-0 |
| P1 | `write`, commit S, puis `check`. FROZEN égale l'oracle canonique indépendant (hashlib et `json.dumps` dans le test). Lignes de sortie exactes, sans chemin absolu. | OK |
| P2 | Instantané complet avant et après `check` : chemins, types, tailles, `mtime_ns`, SHA-256, `.git` compris. Deux sorties consécutives. | Instantané inchangé ; sorties identiques |
| P3 | Deux fixtures construites indépendamment | C, FROZEN et `freeze_id` identiques |
| P4 | Commits après S sur `docs/`, `results/`, `paper/`, `tests/`, un autre fichier de `prompts/` ; message de S amendé | OK |
| P5 | `__pycache__` présent ; `configs/raw.yaml` non-YAML ; fichier de données factice modifié | OK ; mise en garde « no data bytes » |
| P6 | `main` comparé à la bibliothèque (OK et 4 refus) ; sous-processus `-I -B` sur des fixtures oracle, dont les quatre assertions de RED-0 | Sorties et codes identiques |
| P7 | FIFO pièges non suivies sous `data/raw/eurofidai/` et `data/derived/d4_eurofidai/` | OK sans blocage : chemins jamais parcourus |
| M1 | 1 octet modifié sur disque (configuration, code imbriqué, Makefile, manifeste, outil factice), puis restauré | HASH, puis OK |
| M2 | 1 octet modifié dans un commit après S (configuration, code), puis commit de retour | CHANGED, et toujours CHANGED après le retour |
| M3 | Fichier non suivi (dans une racine et imbriqué) ; fichier ignoré `jepadrift/ignored.bin` | COVERAGE |
| M4 | Fichier suivi supprimé du disque | COVERAGE |
| M5 | FROZEN construit et scellé avec une entrée retirée, ajoutée ou renommée | COVERAGE |
| M6 | Sous-module (160000) ; lien suivi (120000) sous une racine | COVERAGE ; LINK |
| K1 | `write` avant C : chacune des 11 racines retirée de HEAD et du disque ; racine-répertoire réduite à `__pycache__` ; `Makefile` suivi comme répertoire ; `experiments` suivi comme fichier | COVERAGE ; rien n'est créé |
| K2 | FROZEN oracle scellé pour un C sans `docs/manifests/d4_manifest.json`, sans `experiments`, ou avec un `Makefile` de type arbre | COVERAGE |
| K3 | Après S : `data/derived/MANIFEST.json` ou `tools/freeze_config.py` supprimé du disque ; `Makefile` remplacé sur disque par un répertoire ; `configs` remplacé par un fichier ; racine supprimée par un commit | COVERAGE ; CHANGED pour la suppression commitée |
| F1 | Octets non UTF-8 ; JSON invalide ; BOM | FORMAT |
| F2 | Clé dupliquée (racine, `files`), même avec une valeur égale | FORMAT |
| F3 | `NaN`, `Infinity`, `-Infinity`, nombre | FORMAT |
| F4 | Clés manquantes ou en trop (deux niveaux) ; types liste, entier, booléen, `null` | FORMAT |
| F5 | Hexadécimal en majuscules, de 39 ou 41 caractères, ou non hexadécimal | FORMAT |
| F6 | `schema` inconnu | FORMAT |
| F7 | Chemins `./x`, `a//b`, absolu, `..`, `/` final, hors POLICY, `configs/FROZEN.json`, non portable ; approbation hors motif | FORMAT |
| F8 | Indentation ; clés non triées ; aucune ou deux fins de ligne ; échappement `a` | FORMAT |
| F9 | 1 MiB + 1 octet, refusé avant analyse ; imbrication de 200 000 niveaux | FORMAT, sans trace d'exception |
| F10 | `files` vide | FORMAT |
| L1 | Lien : FROZEN (vers un FROZEN valide), `configs/`, fichier gelé, sous-répertoire gelé, lien pendant sous une racine, `data/derived`, `prompts/`, approbation | LINK |
| L2 | FIFO sous une racine | LINK, sans blocage |
| L3 | Course simulée : entrée remplacée par un lien (fichier ou répertoire) ou par une FIFO entre l'énumération et l'ouverture, via une enveloppe de `os.open` qui fait la substitution puis délègue | LINK |
| S1 | FROZEN écrit mais non commité (HEAD = C) | SEAL |
| S2 | S ajoute FROZEN et un autre fichier | SEAL |
| S3 | Commit `docs/` entre C et S | SEAL |
| S4 | FROZEN modifié après S ; FROZEN supprimé puis réajouté identique | SEAL |
| S5 | FROZEN ajouté puis retiré avant C | SEAL |
| S6 | Fusion d'une branche `docs/` après S | SEAL |
| S7 | C absent (FROZEN copié dans une autre fixture) ; C égal à un identifiant d'arbre ; contenu identique sur une branche orpheline | SEAL |
| S8 | FROZEN sur disque différent de S d'un chiffre hexadécimal, JSON canonique conservé ; FROZEN en mode 100755 dans S | SEAL |
| S9 | Retour de branche à C : FROZEN absent | ABSENT |
| G1 | `GIT_DIR`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_INDEX_FILE`, `GIT_CONFIG_PARAMETERS` et `GIT_NAMESPACE` pointés vers une autre fixture | Résultat identique, dans un cas OK et un cas HASH |
| G2 | `git replace` qui masque un commit modifiant une configuration, octets du disque remis à C | CHANGED (un mutant donnerait OK) |
| G3 | Fichier de greffes ; clone `--depth 1` | ROOT |
| X1 | Git absent du `PATH` ; délai dépassé (`GIT_TIMEOUT` patché) ; fichier gelé illisible (mode 000) | GIT ; GIT ; IO |
| A1 | `--approval` égal à `docs/GO-x.md`, `prompts/sub/GO-x.md`, `prompts/GO-x.txt`, `prompts/go-x.md` ou `prompts/GO-.md` | APPROVAL, sans appel Git (espion) |
| A2 | Pour `write` : approbation non suivie ; approbation modifiée sur disque | APPROVAL ; rien n'est créé |
| A3 | FROZEN scellé qui nomme une approbation absente de C | APPROVAL |
| A4 | Approbation modifiée après S (par commit ou sur disque) ; approbation supprimée | APPROVAL |
| A5 | `approval.sha256` faux | APPROVAL |
| W1 | FROZEN préexistant : fichier, lien pendant, lien vers un fichier externe | EXISTS ; octets et cible intacts ; rien n'est créé |
| W2 | Racines sales : fichier non suivi, modifié ou manquant | COVERAGE ou HASH ; rien n'est créé |
| W3 | FROZEN déjà présent dans l'histoire | SEAL ; rien n'est créé |
| W4 | HEAD sans commit | ROOT |
| W5 | Racine hors de `tempfile.gettempdir()` (`tempfile.tempdir` patché) | PROJECT ; zéro appel Git ; rien n'est créé |
| W6 | `PROJECT_ROOT_COMMIT` patché sur le commit racine de la fixture | PROJECT ; rien n'est créé |
| W7 | `os.fsync` en échec après la création | IO ; FROZEN supprimé ; `configs/` inchangé |
| W8 | Lignes de sortie de `write` | Exactes |
| W9 | Insertion d'un fichier étranger entre le dernier contrôle d'absence et l'ouverture créatrice (enveloppe de `os.open` sur l'appel `O_CREAT`) | EXISTS ; octets et inode étrangers intacts ; fichier étranger non supprimé |
| W10 | Échec de `os.fsync` après remplacement du nom par un inode étranger (`os.replace` dans l'enveloppe) | IO ; inode et octets étrangers intacts sous le nom ; rien n'est supprimé |
| R1 | `--root` absent, fichier, hors Git, sous-répertoire ou dépôt nu ; racine passée par un lien | ROOT ; avec le lien, résultat identique au chemin direct |
| R2 | Aucun mode ; deux modes ; `--approval` avec `--check` ; `--write` sans `--approval` | Sortie 2 et texte d'usage argparse |
| R3 | AST : imports inclus dans `sys.stdlib_module_names` | Aucun import du projet, de YAML ou d'un paquet numérique |

### 6.4 Mutants
**Méthode.** Mutants appliqués hors dépôt, en mémoire, dans un processus neuf ; empreintes des fichiers contrôlées avant et après.

**Liste.** 16 mutants, chacun tué par au moins un témoin :

| Mutant | Témoin |
|---|---|
| Sans `O_NOFOLLOW` | L1 |
| Sans refus des clés dupliquées | F2 |
| Sans comparaison canonique | F8 |
| Sans contrôle de linéarité | S6 |
| Sans purge des `GIT_*` | G1 |
| Sans `GIT_NO_REPLACE_OBJECTS` | G2 |
| Sans exclusion de `__pycache__` | P5 |
| Sans refus des fichiers non suivis | M3 |
| Sans `O_EXCL` | W9 |
| Sans nettoyage | W7 |
| Nettoyage sans contrôle d'inode | W10 |
| Sans garde d'emplacement | W5 |
| Sans contrôle de l'histoire avant C | S5 |
| Sans contrôle de l'approbation après C | A4 |
| Règle nette au lieu de la règle par commit | M2 |
| Sans contrôle de présence et de type des racines | K1, K2 |

## 7. Validation (après GO, sous verrou) et ressources
```bash
set -euo pipefail
export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_freeze_config.py
.venv/bin/python -m pyflakes tools/freeze_config.py tests/test_freeze_config.py
test "$(git rev-list --max-parents=0 HEAD)" = 32a55c8d6e16dc74f79f7cd17e61e5fb73d89332
rc=0; out=$(.venv/bin/python -I -B tools/freeze_config.py --check) || rc=$?
test "$rc" = 1 && grep -q '^freeze-config: error: ABSENT: ' <<<"$out"
test ! -e configs/FROZEN.json && test ! -L configs/FROZEN.json
J1=e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823
test "$(sha256sum < results/e2/e2_cells.csv | cut -c1-64)" = "$J1"
test "$(git show :results/e2/e2_cells.csv | sha256sum | cut -c1-64)" = "$J1"
test "$(grep -c $'\r$' results/e2/e2_cells.csv)" = 47 && test "$(wc -l < results/e2/e2_cells.csv)" = 47
test "$(sha256sum < results/e3/e3_overshoot.csv | cut -c1-64)" = 1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3
test "$(sha256sum < results/pca_drift_benchmark/full_2000_20261101/manifest.json | cut -c1-64)" = 3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47
git --no-optional-locks diff --quiet HEAD
st=$(git --no-optional-locks status --porcelain=v1 --untracked-files=all)
grep -qxF '?? tools/freeze_config.py' <<<"$st" && grep -qxF '?? tests/test_freeze_config.py' <<<"$st"
test -z "$(cut -c4- <<<"$st" | grep -vxF -e tools/freeze_config.py -e tests/test_freeze_config.py \
  -e prompts/plans/plan-21-F.md -e prompts/GO-stream-21-F.md -e prompts/NO-GO-stream-21-F.md \
  -e docs/audits/streams_01_31_continuation_2026_11_07.md || true)"
sha256sum -c --quiet logs/stream_21_F/codex_files.sha256
! grep -nE '/home/|/tmp/' tools/freeze_config.py tests/test_freeze_config.py
```
- **Fichiers Codex.**
  - Avant la première écriture du lot, Claude relève dans `logs/stream_21_F/codex_files.sha256` les empreintes de ceux des quatre fichiers Codex listés qui sont présents.
  - Ces fichiers sont acceptés tels quels, jamais modifiés. Tout écart d'empreinte est signalé à Codex, jamais corrigé.
  - `prompts/wrapups/wrapup-21-F.md` ne rejoint la liste qu'après son créneau de clôture ; aucune autre entrée n'y est ajoutée.
- **Interdits.** Aucun `--write` sur un dépôt réel. Le `make check` complet revient à Codex, dans son créneau.
- **Ressources.**
  - Environ 100 cas, chacun avec au plus 15 appels Git, sur un gabarit copié.
  - Estimation : 30 s au plus, un cœur, RSS < 200 MB, aucun import numérique.
  - Borne d'arrêt : 60 s ou 300 MB ; au-delà, arrêt et signalement.
  - Le `--check` réel s'arrête à ABSENT en moins de 1 s.

## 8. Collisions
- **Écritures.** Elles sont disjointes de celles de tout autre lot.
- **Runtime partagé.** Aucun import de `tools/trace_numbers.py`, pourtant listé comme runtime partagé dans le registre. Le partage réel se limite à `.venv`, pytest et le créneau `make check`.
- **Absence de FROZEN réel.** Trois éléments en dépendent :
  - `tests/test_pca_drift_benchmark.py:719` (`frozen_json_present is False`) ;
  - `experiments/pca_drift_benchmark.py:1802` (`pre_j4.frozen_json_present`) ;
  - la garde `experiments/e1_problem.py:1196-1199`.

  Les deux gardes de `write` et des tests confinés à `tmp_path` préservent cette absence.
- **Homonymie.** `FROZEN` désigne déjà un dictionnaire PCA dans `e1_problem.py`, `e10_robustness.py` et `audit_information.py`, sans import croisé avec l'outil.
- **Contrôles existants.** Le pyflakes de `make check` (via `find`) couvre les deux nouveaux fichiers ; `make prompts-check` n'est pas concerné.
- **Concurrence.** Aucune exécution concurrente du créneau Codex.

## 9. Conditions d'acceptation
1. Fichier de tests vert, sans `skip` ni `xfail` ; RED-0 consigné comme des échecs de comportement.
2. pyflakes vide ; seuls commentaires `# ponytail:` ; docstrings d'une ligne ; lignes de 120 caractères au plus.
3. 16 mutants sur 16 tués.
4. Toutes les commandes du §7 réussissent, empreintes des fichiers Codex comprises ; aucun chemin hors du §5 n'est créé ou modifié.
5. Wrapup en anglais, à six rubriques, écrit dans le créneau de clôture Codex ; aucune opération Git par Claude.

## 10. Hypothèses et défauts
- **H1.** Le gel porte sur les octets (SHA-256) des fichiers couverts à C et du document d'approbation, sans aucune sémantique YAML.
- **H2.** `POLICY` v1 compte 11 racines (§3), toutes exigées présentes avec leur type (§4.3) ; FROZEN est exclu de sa propre couverture.
- **H3.** Le disque est ce qui s'exécute ; l'index n'est pas lu.
- **H4.** La base d'objets Git locale fait foi pour C. Les remplacements sont désactivés ; les greffes et les dépôts superficiels sont refusés.
- **H5.** L'historique est linéaire après C, conformément au flux rebase et fast-forward du projet.
- **H6.** L'approbation est une provenance hachée, jamais interprétée.
- **H7.** Dans ce lot, l'écriture est réservée aux dépôts synthétiques.
- **H8.** SHA-1 sert seulement d'identifiant de blob Git ; SHA-256 porte l'identité du gel.
- **H9.** Codes de sortie 0, 1 et 2, le code de refus étant donné dans le texte.
- **H10.** Seuls les répertoires `__pycache__` sont exclus ; les autres fichiers ignorés sont couverts.
- **H11.** Les fichiers gelés sont extraits sans conversion (ni `autocrlf` ni filtre), ce qui est vrai pour le projet aujourd'hui (`.gitattributes` ne vise que J1).

## 11. Limites résiduelles
1. **Environnement non vérifié** : Python, `.venv`, `external/`, pont torch, variables. Les fichiers de verrouillage sont hachés, pas comparés à l'installation.
2. **Manifestes** : octets seulement. Aucune donnée n'est lue ni vérifiée, et aucun chargeur ne vérifie non plus contre `MANIFEST.json` (plan-21-rest §8.7).
3. **Approbation** : aucune garantie d'autorité. Un texte arbitraire suivi dans C passe.
4. **`__pycache__` non couvert** : un `.pyc` forgé, aux métadonnées concordantes, resterait invisible.
5. **Fenêtre entre `check` et l'exécution.** Les liens physiques ne sont pas détectés, et la substitution du chemin de la racine elle-même n'est pas couverte.
6. **Bit exécutable** : il n'est pas comparé sur disque. Les modes commités restent contrôlés par la règle par commit.
7. **Historique local réécrit** de façon cohérente (C et S recréés) : indétectable sans le distant poussé. Un vérificateur modifié peut mentir : il ne se couvre lui-même que s'il est intact.
8. **Règle par commit, linéarité et gel unique.** Toute retouche d'un fichier gelé, ou toute fusion après C, bloque définitivement ce gel sur sa lignée. Le même vérificateur refuse aussi tout regel (§4.4) : il faudrait un autre vérificateur ou un autre schéma, sous un autre plan et un autre GO.
9. **Écriture et nettoyage non atomiques** (§4.8). Un arrêt brutal laisse un fichier partiel. Une substitution du nom après la dernière vérification d'inode peut conduire à supprimer un inode étranger.
10. **`POLICY` v1 fixe** : un runner placé hors de `jepadrift/` exigera une v2 ; le reste de `tools/` n'est pas gelé.
11. **Gardes pré-J4 des expériences inchangées** : elles refusent toujours, sans lire FROZEN. Le câblage relève du lot R ou de l'activation.
12. **Effet d'un futur FROZEN réel** : il changera `pre_j4.frozen_json_present` et le témoin PCA de la ligne 719 ; c'est à traiter lors de l'activation.
13. **Conversion de fin de ligne ou filtre** : une extraction qui convertit un fichier gelé donne HASH, ce qui est fermé par défaut mais peu portable.

## 12. Questions d'arbitrage (défaut appliqué sauf décision contraire)
- **Q1.** Après S : [règle par commit et linéarité]. Variante : égalité nette des arbres, qui accepte un retour.
- **Q2.** `POLICY` v1 : [11 racines, sans `tools/benchmark_runner.py`]. Variantes : l'ajouter dès maintenant, ou geler tout `tools/`.
- **Q3.** Gardes d'écriture : [emplacement temporaire et commit racine du projet]. Variante : commit racine seul.
- **Q4.** Codes : [0, 1 et 2, avec le code de refus dans le texte]. Variante : un statut de sortie distinct par code.
- **Q5.** Mutants : [16, hors dépôt]. Variante : aucun.
- **Q6.** `--check` sur le dépôt réel (lecture seule, ABSENT attendu) : [oui, sous verrou]. Variante : omis.

## 13. Trace de session
- **Lu.**
  - Pilotage : la mission, `CLAUDE.md`, les deux amorçages du 7 novembre, le prompt 21, le plan, le GO et le wrapup 21-rest, `docs/MAPPING.md`.
  - Outils et configuration : `tools/{trace_numbers,appendix_b,dpi_lint}.py`, les hooks, le Makefile, `.gitignore`, `.gitattributes`.
  - Extraits des gardes : `e1_problem.py`, `pca_drift_benchmark.py`.
  - Tests : `test_appendix_b.py`, `test_trace_numbers.py`, `test_claude_surveillance.py`, `test_pca_drift_benchmark.py:676-722`, `test_pca_drift_tables.py:456-465`.
  - Orchestration : le registre d'exécution, le journal de la baseline, la mémoire de workflow.
- **Commandes.** Lecture seule : `git rev-parse/log/worktree/ls-files/rev-list/check-attr/status`, `ls`, `sed`, `rg`, `find`, `man`.
  - Le premier `git status` a été lancé sans `--no-optional-locks`. Il a pu rafraîchir les métadonnées de l'index du worktree, sans changement de contenu suivi ; les appels suivants ont utilisé l'option.
- **Non fait.** Aucun Python, import, test, `make`, mutation Git ni appel Graphify ou jCodeMunch. Seul ce fichier a été écrit.
- **Révision 1.** Seule lecture nouvelle : `prompts/NO-GO-stream-21-F.md`. Seule commande : `sha256sum` et `wc -l` du plan révisé.

## Décision GO intégrée

**GO TECHNIQUE ACCORDÉ POUR LE LOT 21-F SUR FIXTURES UNIQUEMENT — 7 novembre 2026.**

La révision 1 lève le NO-GO de révision 0 pour ce seul lot : racines obligatoires K1–K3 ; courses de création et de nettoyage W9/W10 ; liste des fichiers Codex ; RED indépendant ; usage unique explicite. Le NO-GO reste conservé comme trace de revue.

Arbitrages Q1–Q6 : règle par commit et linéarité ; onze racines obligatoires sans runner anticipé ; deux gardes d'écriture ; codes 0/1/2 ; seize mutations d'invariants hors dépôt ; contrôle réel --check limité au refus ABSENT, sous verrou.

Précisions de réception qui priment en cas d'ambiguïté :

- Un lien symbolique reste LINK pour L1/L3, y compris si Linux renvoie ENOTDIR avec O_DIRECTORY et O_NOFOLLOW. Un véritable fichier à la place d'un répertoire requis relève de COVERAGE. La classification ne doit jamais suivre un lien pour déterminer son type.
- Les fixtures ont un seul propriétaire pendant chaque opération ; les courses sont injectées aux points du plan. L'écriture et le nettoyage ne sont pas publiés comme atomiques, et le code reste interdit à l'activation réelle J4.
- Les seize mutants servent à contrôler les invariants. Ne jamais retirer une garde correcte ou affaiblir un test pour obtenir le compte annoncé. Une mutation équivalente par redondance est consignée et soumise à Codex avant toute réception finale ; un contrôle manquant reste à corriger.
- Le témoin de O_NOFOLLOW doit exercer une ouverture concurrente, au besoin en conservant l'inode du fichier après son déplacement puis remplacement par un lien. Les seuls liens statiques ne suffisent pas si une autre garde les rejette déjà.
- Claude possède seulement tools/freeze_config.py, tests/test_freeze_config.py et, après attribution du créneau de clôture, prompts/wrapups/wrapup-21-F.md. Codex possède les quatre documents de contrôle et toute la clôture Git. Les commits et manipulations Git nécessaires aux fixtures temporaires sont autorisés ; aucune mutation Git du dépôt réel ne l'est pour Claude.

Exécution : tests avant code et preuve RED observable, puis GREEN minimal. Chaque commande de test utilise le venv du projet, l'environnement déterministe, le registre et le verrou existants. Le propriétaire science_owner doit être stream-21-F et closeout_owner nul. Aucun make check concurrent.

À REVIEW_READY, Claude attend la revue de Codex sans lancer la clôture. Wrapup installé en anglais à six rubriques, réindexation AST sans résumé IA, contrôle complet, commit anonyme et push appartiennent à la séquence de clôture sérialisée. Aucun résultat scientifique scellé n'est régénéré.

L'activation J4, un FROZEN réel, un nouveau gel sur une lignée existante, le runner, toute lecture de rendements, tout entraînement et toute expérience restent exclus et demandent leurs autorisations propres.
