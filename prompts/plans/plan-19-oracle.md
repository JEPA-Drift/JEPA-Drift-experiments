# Plan 19-oracle — référence analytique oracle de l'information en N pour E4 (proposition native)

**Statut : proposition en attente de la revue et du GO écrit de Codex. L'approbation de l'écran natif ne vaut pas GO.
Aucun fichier du dépôt n'est écrit avant ce GO.**

Base vérifiée `3467df4b7426fa15c1ab16ef94687f25a976636d`, branche `stream-19-oracle`, arbre propre. Mandat :
`logs/orchestration_20261106/plan-request.md`. Ce lot est distinct de la campagne E4 historique, qui reste
`À_REPLANIFIER`, et du lot documentaire 19. Il ne clôt pas la campagne 19.

## 1. Contexte et justification YAGNI

- **Besoin.** E4 n'a aucune référence sérialisée en N qui isole l'information d'un drift et sa saturation, à l'écart
  des délais, des coûts de mélange et de la calibration historique.
- **Existant.** Le seul témoin est `tests/test_floors.py::test_one_factor_keff` (l. 43–47) : une forme quadratique à
  N = 239, ρ = 0,4, δ = 1. Il ne contrôle ni I (facteur ½), ni δ ≠ 1, ni le domaine, ni la saturation, et ne
  sérialise rien. Aucun appelant de `floors.factor_information` ne produit de CSV (callers lus : `tests/test_floors.py`,
  `tests/test_injection.py:155`).
- **Échelle ponytail.**
  1. Nécessaire : oui, aucun producteur de cette référence n'existe.
  2. Réemploi : `floors.factor_information` sans modification, `pipelines.save_fair_csv`, gabarit
     `experiments/ipca_k_selection.py`.
  3. Stdlib : `argparse`, `hashlib`, `math`, `numbers`.
  4–5. Aucune dépendance nouvelle.
  7. Code minimal : un script (une fonction publique et `main`) et un test.
- **Écarté.** Module généraliste dans `jepadrift/` (règle CLAUDE.md : déplacement au second consommateur), registre de
  pipelines, options CLI de grille, colonnes de délai, de SR ou de coût.

## 2. Référence analytique, indépendante du code réemployé

Modèle gaussien connu : Σ_N = ρ11ᵀ + (1−ρ)I_N (variances unitaires), Δμ = δ1, N entier ≥ 1, 0 ≤ ρ < 1, 0 < δ < ∞.
- Σ_N1 = (1+(N−1)ρ)1, donc ΔμᵀΣ_N⁻¹Δμ = δ²N/(1+(N−1)ρ) = 2 I_N. C'est la forme quadratique de `cor:factor`
  (`paper/sec3_theory.tex`, l. 54–61), et le facteur ½ est celui de `eq:hierarchy` (l. 16).
- I_N = δ²N/[2(1+(N−1)ρ)] nats par jour : KL exacte d'un déplacement gaussien à covariance connue.
- G(N) = I_N/I_1 = N/(1+(N−1)ρ), avec I_1 = δ²/2 quel que soit ρ.
- ρ > 0 : G croît strictement vers 1/ρ, avec l'écart exact 1/ρ − G(N) = (1−ρ)/[ρ(1+(N−1)ρ)], et I_N ≤ δ²/(2ρ).
- ρ = 0 : G(N) = N, sans plafond fini.
- Aucun de ces nombres n'est un délai, un ADD, un ARL0 ou une FPR.

## 3. Fichiers

| Chemin | Rôle | Propriétaire |
|---|---|---|
| `experiments/e4_oracle_reference.py` | producteur et CLI (§4) | Claude, après GO |
| `tests/test_e4_oracle_reference.py` | tests ciblés (§7) | Claude, après GO |
| `docs/sections/e4_oracle_reference.md` | note anglaise courte (H7) | Claude, après GO |
| `prompts/wrapups/wrapup-19-oracle.md` | six sections anglaises, via le wrap-up natif | Claude, à la clôture |
| `logs/stream_19_oracle/` (ignoré par `.gitignore:9`) | journaux RED/GREEN, CSV temporaires, `make check` | Claude |
| `prompts/plans/plan-19-oracle.md`, `prompts/GO-stream-19-oracle.md`, archive du plan natif | plan canonique, GO, revue | Codex |

Restent inchangés (contrôle au §8) :
- tout `jepadrift/`, dont `floors.py` et `pipelines.py`, hachés par `CODE_MODULES`
  (`experiments/pca_drift_benchmark.py:579`) ;
- `tests/test_floors.py`, les producteurs et artefacts PCA scellés, `tests/test_pca_drift_contracts.py` ;
- `results/`, `figures/`, `paper/`, `docs/DEVIATIONS.md`, `docs/MAPPING.md` ;
- `prompts/streams/`, le master, les mémoires et les dépendances.

Git, réindexation et commit reviennent à Codex.

## 4. Interfaces (`experiments/e4_oracle_reference.py`)

- **En-tête** du gabarit `ipca_k_selection.py` : variables BLAS à 1 et `MKL_CBWR=COMPATIBLE` avant numpy, `sys.path`
  vers la racine, sans `# noqa`, docstring de module avec l'usage.
- **Constantes :**
  - `N_GRID = (1, 8, 16, 32, 64, 128, 239, 500)` ;
  - `RHO_GRID = (0.0, 0.4)` ;
  - `DELTA = 1.0` ;
  - `QUALIFICATION = "ORACLE_KNOWN_SIGMA_DELTA"`.
- **`oracle_row(n, rho, delta=DELTA) -> dict`**, avec une docstring d'une ligne.
  - Lève `ValueError` si `n` est booléen, n'est pas un `numbers.Integral` (2.5, 8.0) ou vaut moins de 1 ; si
    `not 0 <= rho < 1` (couvre NaN et ±inf) ; si `not 0 < delta < inf` (couvre NaN, ±inf, 0 et δ < 0).
  - Calcule `factor_term, breadth_term = fl.factor_information(np.ones((n, 1)), [[rho]], np.full(n, 1 - rho), [delta], np.zeros(n))`.
  - En déduit `info_nats = (factor_term + breadth_term) / 2` et `gain_vs_single = info_nats / (delta**2 / 2)`.
    `gain_ceiling` vaut `1/rho` si ρ > 0, sinon `inf`.
  - Lève `ValueError` sur une sortie non finie (débordement de δ²).
  - Renvoie les colonnes `N, rho, delta, factor_term, breadth_term, info_nats, gain_vs_single, gain_ceiling,
    qualification`, avec les réels convertis en `float`.
- **`main(argv=None)`.**
  - Seule option : `--out PATH`, le fichier CSV, obligatoire et sans défaut sous `results/`.
  - Produit 16 lignes, `oracle_row(n, r)` pour r ∈ RHO_GRID puis n ∈ N_GRID, dans un ordre fixe.
  - Écrit par création exclusive (`open(out, "x", newline="")`, donc sans écrasement) et passe le descripteur à
    `save_fair_csv`.
  - Imprime une seule ligne au format `sha256sum` : `<sha256>  <out>`. Termine par `raise SystemExit(main())`.

## 5. Réemploi

- **`jepadrift/floors.py:131` `factor_information`**, sans modification. Paramètres : B = 1 (N×1), Σ_F = [[ρ]],
  Ψ = (1−ρ)I, Δλ = δ, Δα = 0. Elle renvoie la forme quadratique (2 I), scindée en terme facteur et terme largeur. Le ½
  est appliqué dans le script, jamais dans `floors`.
- **`jepadrift/pipelines.py:67` `save_fair_csv`** : `%.17g`, `NaN`, `\n`, sans index. C'est un port Article B gelé
  par `tests/test_identity_articleB.py:29`. Le dépôt lui passe déjà un descripteur
  (`experiments/figures/plot_figure_1.py:149–153`).
- **Empreinte** : une ligne `hashlib.sha256(out.read_bytes()).hexdigest()`, même motif que `_sha256`
  (`experiments/e1_problem.py:1107`), sans import croisé d'un script lourd.
- **Hors périmètre, donc non appelés :** `evidence_budget`, `phi`, `mixture_multiplier`, `dictionary_multiplier`,
  `kl_from_sharpe`.

## 6. Hypothèses et défauts (à confirmer ou infirmer au GO)

- **H1 — Grille.**
  - N : grille historique d'E4 (`prompt-19-e4-p3kf.md`, l. 16), plus N = 1, la référence d'un seul actif.
  - ρ ∈ {0 ; 0,4}. La valeur 0 montre l'absence de plafond. La valeur 0,4 est déjà en usage dans le dépôt (manifeste
    full PCA `"rho": 0.4`, `test_one_factor_keff`). Ce sont des paramètres du modèle analytique, pas des
    hyperparamètres de détection.
  - δ = 1, en écart-type par actif. I varie comme δ², G ne dépend pas de δ.
- **H2 — Signe de δ.** δ ≤ 0 est rejeté, conformément au périmètre « fini strictement positif », bien que I soit
  pair en δ.
- **H3 — N.** Un entier Python ou numpy ≥ 1 est accepté. Booléen, flottant (même 8.0) et chaîne sont rejetés, avec
  une seule exception, `ValueError`.
- **H4 — Plafond à ρ = 0.** `gain_ceiling = inf`, écrit `inf` par `%.17g` et relu `inf` par
  `read_csv(float_precision="round_trip")`. Jamais NaN, qui signifierait une valeur manquante.
- **H5 — Les sorties temporaires suffisent.**
  - Aucun résultat suivi : le CSV est une fonction déterministe des constantes du script suivi. Le test fixe son
    contenu par des formules indépendantes et vérifie le déterminisme des octets. Un CSV suivi serait une seconde
    source de vérité.
  - Réception : Codex régénère le CSV dans un répertoire temporaire, vérifie `sha256sum -c`, puis l'égalité avec le
    SHA-256 consigné dans le wrapup. Ce SHA ne vaut que pour l'environnement épinglé (`.venv`, BLAS mono-thread,
    `MKL_CBWR=COMPATIBLE`).
  - Variante, si Codex la retient : `results/e4_oracle/e4_oracle_reference.csv`, chemin neuf. Pas d'entrée MAPPING
    tant que `paper/` ne cite aucun de ses nombres.
- **H6 — Qualification.** Colonne constante `ORACLE_KNOWN_SIGMA_DELTA` : Σ_N et Δμ connus, KL gaussienne analytique.
  Ni estimation, ni détecteur, ni délai, ni FPR. Elle suit le style des drapeaux `ORACLE_*` du benchmark PCA sans
  réemployer leur énumération scellée.
- **H7 — Note.** `docs/sections/e4_oracle_reference.md`, environ 40 lignes en anglais.
  - Contenu : modèle et domaine ; formules, avec renvois de lignes à `sec3_theory.tex` ; piège du facteur ½ ;
    colonnes ; commande et procédure de réception.
  - Ce que la référence n'est pas : τ_γ, Φ, ADD, ARL0/FPR, coût de mélange ou de dictionnaire, pente empirique, PCA
    estimée, données réelles. Statut : ne clôt pas E4.
  - Aucun nombre calculé, SHA compris : paramètres et formules seulement, donc aucune entrée `docs/MAPPING.md`.
- **H8 — Contrôles.** Claude exécute les tests ciblés, pyflakes, puis un `make check` complet en fin de lot, car c'est
  un lot de code, à la différence du lot 19. Codex rejoue les contrôles de clôture.
- **H9 — DEVIATIONS.** Aucune entrée : le lot n'exécute ni ne modifie le prompt 19, qui reste différé.

## 7. Tests RED → GREEN (`tests/test_e4_oracle_reference.py`)

Tolérances fixées avant toute exécution et jamais recalées :
- relative 1e-12 contre les formules fermées ;
- relative 1e-10 contre la résolution dense ;
- absolue 1e-12/ρ sur l'écart au plafond.

Tests :
1. **Formule indépendante et résolution dense.** Pour N ∈ {1, 2, 3, 5, 8, 13}, ρ ∈ {0 ; 0,25 ; 0,9} et
   δ ∈ {0,5 ; 2} :
   - `info_nats` égale δ²N/[2(1+(N−1)ρ)], et ½ Δμᵀ solve(Σ, Δμ) avec Σ construite densément ;
   - `gain_vs_single` égale N/(1+(N−1)ρ) ;
   - `breadth_term == 0`.
2. **Facteur ½.** `info_nats == (factor_term + breadth_term)/2`. À N = 1, I = δ²/2 pour tout ρ (δ = 2 donne 2,
   jamais 4) et G = 1.
3. **ρ = 0.** G(N) = N jusqu'à N = 2^20, et `gain_ceiling == inf`.
4. **ρ proche de 1.** Pour ρ ∈ {1 − 1e-6 ; 1 − 1e-12 ; `np.nextafter(1, 0)`} et N ∈ {1, 2, 500}, les sorties sont
   finies et égales à la formule fermée. La voie de Woodbury n'inverse jamais Σ ; aucune résolution dense ici.
5. **Domaine.** `ValueError` pour :
   - N ∈ {0, −1, 2.5, 8.0, True} ;
   - ρ ∈ {−0,1 ; 1 ; 1,5 ; NaN ; ±inf} ;
   - δ ∈ {0 ; −1 ; NaN ; ±inf}, et le débordement δ = 1e200.

   `np.int64(8)` est accepté.
6. **Saturation à paramètres fixés.** Pour ρ ∈ {0,1 ; 0,4}, δ = 1 et N = 2^k (k = 0..20) : G strictement croissant,
   G < 1/ρ, écart égal à (1−ρ)/[ρ(1+(N−1)ρ)], et I_N ≤ δ²/(2ρ).
7. **Export.** Deux appels `main(["--out", …])` dans `tmp_path` :
   - octets identiques ;
   - la ligne imprimée vaut le SHA-256 recalculé ;
   - la relecture `round_trip`, avec dtypes déclarés, égale les lignes d'`oracle_row`. Sans dtypes déclarés,
     `delta` et `breadth_term`, écrits `1` et `0`, se reliraient en int64 ;
   - les paires (N, ρ) valent N_GRID × RHO_GRID, et `qualification` est constante ;
   - un troisième appel sur un chemin existant lève `FileExistsError` et laisse le fichier intact.

Étapes :
- **RED** : test seul, collecte en échec (`ModuleNotFoundError: experiments.e4_oracle_reference`), journal
  `logs/stream_19_oracle/red.log`.
- **GREEN** : script écrit, les 7 tests et `tests/test_floors.py` passent, journal `green.log`.
- Méthode : skill `superpowers:test-driven-development`, sans sous-agent.

## 8. Vérifications (chaque commande échoue en cas d'écart)

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
L=logs/stream_19_oracle; B=3467df4b7426fa15c1ab16ef94687f25a976636d; F=e4_oracle_reference.csv; mkdir -p "$L"
.venv/bin/pyflakes experiments/e4_oracle_reference.py tests/test_e4_oracle_reference.py
.venv/bin/python -m pytest -q tests/test_e4_oracle_reference.py tests/test_floors.py
.venv/bin/python experiments/e4_oracle_reference.py --out "$L/a/$F" > "$L/a.sha256" && sha256sum -c "$L/a.sha256"
.venv/bin/python experiments/e4_oracle_reference.py --out "$L/b/$F" > "$L/b.sha256" && cmp "$L/a/$F" "$L/b/$F"
! .venv/bin/python experiments/e4_oracle_reference.py --out "$L/a/$F" && sha256sum -c "$L/a.sha256"
git diff --quiet "$B"
PATH="$PWD/.venv/bin:$PATH" .venv/bin/make check 2>&1 | tee "$L/make_check.log"; test "${PIPESTATUS[0]}" -eq 0
test "$(git status --porcelain | grep -v -E '^\?\? prompts/(GO-stream-19-oracle|plans/plan-19-oracle)\.md$')" = \
  "$(printf '%s\n' '?? docs/sections/e4_oracle_reference.md' '?? experiments/e4_oracle_reference.py' \
     '?? prompts/wrapups/wrapup-19-oracle.md' '?? tests/test_e4_oracle_reference.py')"
! grep -n -E '/home/|noqa' docs/sections/e4_oracle_reference.md experiments/e4_oracle_reference.py \
    tests/test_e4_oracle_reference.py prompts/wrapups/wrapup-19-oracle.md
! grep -n -E '(^|\s)#' experiments/e4_oracle_reference.py tests/test_e4_oracle_reference.py
```

Compléments :
- Les SHA-256 des fichiers Codex sont relevés avant toute écriture, puis revérifiés par `sha256sum -c` en fin de lot.
- Le filtre `git status` est ajusté aux noms réels des fichiers Codex (Q5).
- Si Codex avance la branche, la référence de `git diff` devient HEAD, et le diff de B à HEAD est limité à ses
  fichiers.

## 9. Limites et hors périmètre

- **Modèle.** Un facteur, équicorrélation non négative, dérive de marché seule. Ni terme de largeur, ni ρ < 0 (Σ
  resterait pourtant définie positive pour ρ > −1/(N−1)), ni variances hétérogènes.
- **Quantité.** Information seulement : ni τ_γ, ni Φ, ni ADD, ni ARL0/FPR, ni coût M(D, γ) ou de dictionnaire, ni
  pente ou exposant mesuré.
- **Empreinte.** Le SHA-256 dépend de l'environnement épinglé. Hors de cet environnement, les valeurs sont garanties
  par les tests à 1e-12 près, pas au bit près.
- **Hors mandat :** campagne E4/D6, rendements réels quelle que soit la date, PCA estimée ou sans oracle, SPLL/P3-KF,
  JEPA/VAE, gel/J4, pente empirique, ADD/Lorden, édition de l'article, hyperparamètres de détection, dépendances,
  rerun du full PCA.

## 10. Questions (aucune bloquante ; défauts appliqués faute de réponse)

- **Q1 (H5).** Sorties temporaires (défaut) ou CSV suivi sous `results/e4_oracle/` ?
- **Q2 (H1).** La grille ρ ∈ {0 ; 0,4} avec δ = 1 suffit-elle (défaut), ou Codex prescrit-il d'autres valeurs ?
- **Q3 (H4).** Plafond à ρ = 0 écrit `inf` (défaut) ou cellule vide ?
- **Q4 (H8).** `make check` complet par Claude (défaut), ou réservé à Codex ?
- **Q5.** Noms exacts des fichiers plan et GO de Codex, pour le filtre `git status` du §8.

## 11. Séquence après GO

1. Lire le GO et relever les SHA-256 des fichiers Codex.
2. Écrire le test ; RED journalisé.
3. Écrire le script ; GREEN journalisé ; pyflakes.
4. Export, empreinte, déterminisme et refus d'écrasement (§8).
5. Écrire la note.
6. `make check` complet et contrôles d'état du §8.
7. Wrap-up natif, enregistré dans `prompts/wrapups/wrapup-19-oracle.md` : six sections anglaises, avec le SHA-256 du
   CSV de référence et des fichiers produits. Relancer ensuite le contrôle `git status` et celui des chemins.
8. Arrêt pour la revue Codex : ni Git, ni réindexation, ni push. Au quota ou à l'erreur, l'état est conservé et
   rapporté, sans relance.

## 12. Décision GO intégrée — Codex, 2026-11-06, 20:10 UTC

Décision dans le mandat d'orchestration délégué par le chercheur. **GO de ce seul lot analytique**, sous les décisions ci-dessous, qui priment sur les propositions natives divergentes. Le plan natif relu est archivé sans modification dans `logs/orchestration_20261106/native-plan-reviewed.md`, SHA-256 `fc966d66395b13481fe5708caba2f9797072a166ec4dcb455ae27398516593b6`. Le plan canonique et le GO sont enregistrés avant exécution.

### Réponses Q1–Q5

- **Q1 / H5 : sorties temporaires seulement.** Aucun CSV suivi. Réception et empreinte dans les journaux ignorés et le wrapup ; aucune entrée MAPPING supplémentaire.
- **Q2 / H1 : grille proposée acceptée.** N = (1, 8, 16, 32, 64, 128, 239, 500), ρ = (0, 0,4), δ = 1 ; 16 lignes, sans option de grille. Ce sont des paramètres d'une référence analytique, pas un réglage de détecteur.
- **Q3 / H4 : plafond infini seulement pour ρ = 0.** Le champ exprime alors une absence mathématique de plafond. Aucun NaN ou vide ne remplace cette quantité.
- **Q4 / H8 : contrôles ciblés par Claude ; contrôle complet par Codex.** Claude exécute RED→GREEN, pyflakes, réception CLI et contrôles d'intégrité. Le `make check` complet obligatoire est réalisé par Codex, après wrapup et réindexation, via le hook avant commit. Ne pas le doubler dans cette session.
- **Q5 :** `prompts/plans/plan-19-oracle.md` et `prompts/GO-stream-19-oracle.md` sont les fichiers Codex ; les considérer comme présents, non possédés par Claude et inchangés.

### Précisions numériques obligatoires

- L'API rejette par `ValueError` les paramètres hors domaine et les valeurs dont les calculs requis ne sont pas représentables en float64. Le domaine mathématique et cette limite numérique sont distingués dans la note.
- Avant d'appeler le helper, vérifier que la référence d'un seul actif δ²/2 est strictement positive et finie. Rejeter aussi bien un carré sous-représentable qu'un débordement ; aucun zéro silencieux, division par zéro ou exception de débordement non traitée.
- Après le helper, `factor_term`, `breadth_term`, `info_nats` et `gain_vs_single` sont finis ; information et gain sont strictement positifs. Ne pas confondre la forme quadratique renvoyée par le helper avec la KL : le facteur 1/2 reste explicite.
- Si ρ > 0 et son inverse déborde, rejeter explicitement ; `inf` ne peut pas signifier une limite finie non représentable. Si ρ = 0, seul le champ plafond peut être infini.
- Ajouter aux rejets des témoins δ = 1e-200, δ = 1e200 et ρ strictement positif dont l'inverse déborde, avec une dimension minuscule. Conserver les tests aux limites et les tolérances déjà fixées. Ne jamais modifier les routines gelées ni retoucher les tolérances pour obtenir GREEN.

### Réception et propriété

- Créer explicitement les répertoires de réception a et b avant les commandes du §8 ; l'export exclusif n'implique pas la création de parents.
- Le changement est limité aux quatre fichiers Claude du §3 et aux journaux ignorés. Les plans/GO appartiennent à Codex.
- Le modèle reste `claude-opus-5-5`, effort **Max inchangé jusqu'à clôture**, dans la même session interactive, sans sous-agent. La sortie du mode plan utilise le mécanisme natif, après lecture de ce GO.
- Invoquer le wrap-up natif, écrire ses six sections anglaises avec commandes, sorties et SHA-256 réels, puis arrêter les modifications pour revue Codex. Aucun commit, push ou réindexage par Claude.
- Tous les producteurs et artefacts scellés, J1 disque/index/47 CRLF, le FAIL D8, la mémoire, les dépendances et les exclusions du mandat restent préservés. Aucune campagne E4, PCA estimée, donnée réelle, JEPA/VAE ou J4.
