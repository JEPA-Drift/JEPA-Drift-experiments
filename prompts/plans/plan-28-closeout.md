# Stream 28 — Plan de correction et de clôture (mode plan, lecture seule)

**Dernière décision GO d'exécution intégrée :** le chercheur autorise désormais Mistral Vibe `large-4`, thinking high, à exécuter ce plan ciblé. Lire `prompts/GO-stream-28-closeout-vibe.md` avant les instructions. Les mentions antérieures d'attente d'un moteur conservent leur valeur historique ; Claude reste limité aux plans et Codex conserve l'audit/intégration.

## 0. Cadre
- **Périmètre.** Ce plan concerne le seul Stream 28, worktree `stream-28`, base `e1f80847245b14498e331abda1e3d13cf415ec8f`.
- **Ce que n'est pas ce plan.** Il ne vaut ni GO d'implémentation ni gel du schéma. `prompts/POLICY-PCA-PLAN-ONLY.md` exclut toute Phase B Claude.
- **Exécution.** Un implémenteur autorisé exécutera ce plan, selon les instructions que le chercheur fournira ; aucune commande Vibe n'est supposée ici. Codex garde la revue, les portes et Git.
- **Base de travail.** Le code existant est repris, jamais recréé. Les streams 29, 30 et 31 restent fermés jusqu'à la clôture du 28.

## 1. Constats acquis
- **Revue Codex** (`docs/audits/stream-28-codex-review.md`) : 48 tests passent en 7,91 s. Les sept fichiers /2 de `smoke_predictive_v2/` sont identiques au repeat ; manifest `45afe273…25768`. E2 est intact (SHA-256 `e315e537…570823`, i/crlf, w/crlf, -text) et la ligne D8 est présente.
- **Défaut 1, lu dans le code.**
  - `experiments/pca_drift_benchmark.py:535` : `size = min(chunk, mem_bytes // cov_batch_bytes(d))`.
  - Avec `mem_bytes` flottant, `//` renvoie un flottant. Dès que ce plafond mémoire est inférieur à `chunk`, `range(…, size)` (l.540) lève TypeError.
  - En production, `Store.mem_limit` vaut `float(mem_limit_gib) * 2**30` (l.1733), donc `Run.available_bytes()` (l.803) est flottant.
  - Le test de mémoire réduite (`tests/…:977`) passe un entier et ne couvre pas ce chemin.
- **Défaut 1, reproduit par Codex.** C0 = I6, C1 = diag(1..6), nmax = 6, chunk = 20000, mem_bytes = 3.0 × 1728 = 5184.0 donnent `TypeError: 'float' object cannot be interpreted as an integer`.
- **Portée du défaut 1.** Le défaut ne peut qu'interrompre une exécution, jamais en altérer les valeurs. Dans le smoke existant, le plafond mémoire (≈ 4×10⁵) dépassait 20000, si bien que `min` renvoyait l'entier `chunk`. Les sorties /2 déjà produites n'ont pas emprunté ce chemin.
- **Défaut 2.** `configs/pca_drift_benchmark.yaml:1` déclare encore `pca_drift_benchmark/1`. Le manifest de `smoke_predictive_v2/` porte /2 à la racine et dans `identity`, mais /1 dans `config.schema_version`. Ces métadonnées sont mixtes : l'artefact est conservé tel quel et ne sera jamais édité à la main.
- **Hors défaut.** La revue n'a relevé aucun autre blocage sur : le rang prédictif, GE/GT, la portée d'échangeabilité, la séparation du holdout, le scan, l'objectif de covariance jointe et la réutilisation des métriques.

## 2. Correctif 1 — taille de lot entière (travail futur)
- **Changement.** Une seule ligne dans `exhaustive_cov` : `size = chunk if mem_bytes is None else min(chunk, int(mem_bytes // cov_batch_bytes(d)))`. Le refus `size < 1` → `ResourceBlocked` existant est conservé.
- **Garde de frontière minimale, dans la même fonction.** Un `mem_bytes` non fini (NaN ou inf) lève ValueError avec un message explicite, au lieu de l'erreur opaque de `int()`.
- **Garde dans `validate_config`.** Ajouter `math.isfinite` aux limites de ressources (l.333), qui acceptent aujourd'hui `.inf`.
- **Invariants inchangés :**
  - extractions (lot, d, d) ;
  - lots d'au plus 20000 ;
  - `check(stage)` avant chaque lot, y compris à d fixé ;
  - une évaluation par sous-ensemble, réutilisée pour tout k ;
  - aucun repli approché.
- **Hors champ.** Aucune modification de `kl_cov_raw`, `clip_kl`, du scan, des détecteurs ou des seuils. Le docstring précise que la taille vaut floor(mem_bytes / cov_batch_bytes(d)), entière.

## 3. Correctif 2 — configuration alignée sur /2 (travail futur)
- **YAML.** Ligne 1 du fichier : `schema_version: pca_drift_benchmark/2`.
- **Code.** Une condition dans `validate_config` : `cfg["schema_version"] == SCHEMA_VERSION`. Une config /1 est alors refusée au lieu de produire un manifest mixte.
- **Conséquences.** Les colonnes ne changent pas, donc le schéma reste /2. `config_hash`, `code_hash`, `run_fingerprint` et tous les identifiants changent : la preuve corrigée exige des répertoires neufs (§5).

## 4. Séquence TDD ciblée (non démarrée)
- **T0, état initial, lecture seule.** Consigner dans `logs/pca_drift_benchmark/closeout_fixes.log` :
  - HEAD et `git status` ;
  - 48 tests verts ;
  - SHA-256 du runner, des tests, du YAML et du document de schéma ;
  - un digest des listings SHA-256 de `smoke/` (/1), `smoke_predictive_v2/`, `smoke_predictive_v2_repeat/` et de toutes les partitions ;
  - l'absence des deux répertoires closeout.
- **T1, RED défaut 1.** Ajouter un test dans `tests/test_pca_drift_benchmark.py` :
  - référence : C0 = I6, C1 = diag(1..6), `ref = exhaustive_cov(…, 20000)` ;
  - optimum analytique attendu : S(k,d) = axes k−d..k−1, I = Σ ½(r − 1 − ln r) ;
  - mem_bytes = 3.0·cov_batch_bytes(6) : résultat égal à `ref` (égalité exacte du dict) ;
  - instrumentation par `kl_cov_raw` monkeypatché : somme des lots = 63, chaque lot ≤ floor(5184/cov_batch_bytes(d)), nombre d'appels de `check` égal au nombre de lots ;
  - mem_bytes = cov_batch_bytes(1) − 0.5 : `ResourceBlocked`, sans aucun appel KL ;
  - NaN et inf : ValueError ;
  - chemin production : un `Store` à `mem_limit` flottant et `peak_rss_bytes` monkeypatché, pour que `available_bytes()` vaille 5184.0 ; le résultat doit être égal à `ref`.
  - Consigner le TypeError observé mot pour mot.
- **T2, GREEN défaut 1.** Appliquer le §2. Les tests entiers existants (`test_p1_exhaustive…`) restent inchangés et verts.
- **T3, RED défaut 2.** Ajouter un test :
  - `load_config(CONFIG, mode)["schema_version"] == SCHEMA_VERSION` pour smoke et full ;
  - `validate_config` refuse /1 ;
  - le manifest de `tiny_run` porte /2 à la racine, dans `identity` et dans `config` ;
  - la colonne `schema_version` vaut /2 dans les six CSV.
- **T4, GREEN défaut 2.** Appliquer le §3.
- **T5, contrôles du stream.** pyflakes sur les deux fichiers, puis `python -m pytest -q tests/test_pca_drift_benchmark.py` : anciens et nouveaux tests verts. Diff dans `logs/pca_drift_benchmark/closeout.diff`.
- **T6, documentation minimale.** Dans `docs/sections/pca_drift_benchmark.md`, deux précisions :
  - lot entier issu d'un budget flottant ;
  - `smoke_predictive_v2_closeout/` comme preuve candidate, et `smoke_predictive_v2/` antérieur aux correctifs (config /1).
  - Aucune entrée DEVIATIONS : ce sont des correctifs d'ingénierie, sans écart de méthode. Le wrapup les consigne.

## 5. Double smoke de clôture (après T5, répertoires neufs)
- **Primaire.** `--mode smoke --dataset synthetic --out results/pca_drift_benchmark/smoke_predictive_v2_closeout --log-dir logs/pca_drift_benchmark/smoke_predictive_v2_closeout`.
- **Repeat.** `--out logs/pca_drift_benchmark/smoke_predictive_v2_closeout_repeat/out --log-dir logs/pca_drift_benchmark/smoke_predictive_v2_closeout_repeat/log`.
- **Mesures.** Logs de temps séparés, `smoke_predictive_v2_closeout{,_repeat}.time.log`, via `/usr/bin/time -v`.
- **Paramètres inchangés :**
  - N239, H250, n40, α = .05 ;
  - scan exact ;
  - deux fonds, scénarios A/B30/C ;
  - un processus, BLAS sur un thread, 8 Gio, 30 min ;
  - environnement imposé, `.venv` partagé ;
  - aucun full, aucune donnée réelle postérieure à 2019.
- **Vérifications :**
  - `cmp` des sept fichiers ;
  - égalité des `identity` ;
  - /2 homogène : racine, `identity`, `config` et chaque cellule CSV ;
  - refus d'une relance dans le répertoire primaire (exit 2) ;
  - aucun fichier de plus de 50 Mo ;
  - aucun chemin personnel.
- **Rapport.** Durées, CPU, RSS, sept SHA-256 et fingerprint, tels que mesurés. Une comparaison descriptive des valeurs non identifiantes avec `smoke_predictive_v2/` est rapportée telle quelle, sans retouche.
- **Préservation.** Le digest T0 des artefacts /1 et /2, du repeat et des partitions est recalculé et doit être identique.

## 6. Portes de clôture sous contrôle Codex
1. **Revue du diff.** Il doit se limiter à `exhaustive_cov`, `validate_config`, la ligne 1 du YAML, les tests et la documentation. Aucun changement de KL, de détecteur ou de seuil.
2. **Tests ciblés.** Tests du stream et pyflakes, puis non-régression `.venv` : `tests/test_check_prompts.py`, `tests/test_decoupling.py`, `python tools/check_prompts.py`.
3. **Schéma /2 homogène.** Preuve sur les sorties closeout. Les artefacts /1 et pré-correctifs restent intacts et étiquetés.
4. **Invariants E2 et E3.**
   - E2 : SHA-256 sur disque et dans l'index, 47 lignes CRLF, -text.
   - E3 : FAIL inchangé, ligne D8 présente, `git diff --quiet -- results/e3`.
   - `docs/DEVIATIONS.md` en ajout seul.
5. **Taille et confidentialité.** Sources et sorties sous 50 Mo ; aucun chemin EUROFIDAI dans le statut ni dans la plage poussée.
6. **Wrapup formel.** Directive invoquée par Codex : `prompts/wrapups/wrapup-28.md` rafraîchi avec les hashes et coûts closeout et le statut des smokes antérieurs.
7. **Réindexation.** `tools/reindex_graphify_jcodemunch.sh` lance `graphify update`, sans extraction LLM payante ; vérifier que les résumés IA jCodeMunch restent désactivés. Une ambiguïté d'index (précédent du stream 13) se signale sans invalidation.
8. **make check et Git, sérialisés, tous processus éteints.**
   - Audit de `git status`, staging explicite par chemin.
   - Exclure les partitions et le repeat ; décider explicitement de `git add -f` des traces de `logs/` et du smoke /1.
   - Commit Conventional Commits sans trailer, identité anonymisée inchangée.
   - Contrôle de la plage poussée, puis fetch/rebase ; nouveau make check si la base a bougé.
   - `git push origin stream-28:main` seulement après ces portes et l'autorisation du chercheur.

## 7. Critères de clôture
- **Défaut 1.** RED consigné (TypeError), puis GREEN. Équivalence exacte à l'exhaustif et à l'optimum analytique. Budget flottant insuffisant → `ResourceBlocked` ; NaN/inf refusés. Tests entiers inchangés et verts.
- **Défaut 2.** YAML à /2, refus de /1 testé, aucune métadonnée /1 dans les sorties closeout.
- **Tests.** Tous les tests du stream verts, pyflakes propre, make check vert (Codex).
- **Double smoke.** Deux exits 0, sept fichiers identiques, identités égales ; mesures et hashes rapportés.
- **Préservation.** Digest identique des artefacts /1 et /2 et des partitions.
- **Invariants.** E2, E3/D8, taille, confidentialité, staging et identité conformes. Wrapup et réindexation faits ou blocage rapporté.
- **Gel du schéma /2.** Il relève de Codex et du chercheur, après ces critères, hors de ce plan.

## 8. Limitations encore attendues
- **Coût du full.** Il reste extrapolé, non mesuré : environ 21–29 min, plus environ 1 min de réel antérieur à 2020, proche de la limite de 30 min. `--resume` peut être nécessaire, et `memory_estimate` n'inclut pas les lignes de trials.
- **Effectifs du smoke.** À n40, FPR holdout et RMST restent descriptifs (trajectoires partagées) : aucune revendication.
- **Garantie prédictive.** Elle reste marginale, limitée aux maxima synthétiques échangeables ; elle n'est pas établie pour D6 ni pour une trajectoire réelle.
- **Cohortes réelles.** Elles restent `BLOCKED_PRE_J4` jusqu'à `configs/FROZEN.json` (stream 21).
- **Lectures du smoke.** B30 sature les comparaisons de covariance ; CPV90 tombe hors des 20 axes candidats pour les deux fonds.
- **Smoke pré-correctifs.** `smoke_predictive_v2/` conserve `config.schema_version` /1 : c'est un artefact pré-correctifs, jamais une preuve scellée.

## 9. Décision GO intégrée — PLAN UNIQUEMENT

Revue Codex du 2026-10-30 : plan approuvé pour préparer la correction et la clôture du Stream 28. Source Phase A de 121 lignes, SHA-256 `f17da53fa8f4dc9b8b3b139da107a157f72857d43d2381b26c510242c26e1789`.

- Les deux constats sont couverts sans changer le détecteur, la KL, la règle prédictive ou les paramètres des expériences.
- La taille du lot devient entière sous budget flottant ; le cas insuffisant reste ResourceBlocked. Les contrôles des limites non finies restent des validations de frontière.
- La configuration et les métadonnées produites doivent être homogènes /2. Les anciens artefacts ne seront jamais corrigés à la main ; code/config modifiés impliquent de nouveaux fingerprints et deux sorties closeout neuves.
- Les tests doivent vérifier exactement les sous-ensembles retenus. Les comparaisons à une formule analytique indépendante emploient une tolérance numérique explicite ; cela ne remplace pas le contrat d'identité exacte des métriques réutilisées entre expériences.
- Toute commande Python, test ou Make utilise le .venv du projet, avec les variables déterministes fixées avant NumPy. Aucune dépendance changée et aucune évaluation réelle post-2019.
- make check doit réussir avant commit, puis être répété si un rebase change la base. Contrôle de la plage finale poussée après rebase, E2 dans le fichier et le blob indexé, aucun fichier EUROFIDAI ou >50 Mo, identité anonymisée, staging explicite et arbre propre à la clôture.
- **Cette approbation n'autorise aucune implémentation Claude ni aucun appel Mistral Vibe.** Le chercheur fournira les instructions de l'implémenteur. Le garde partagé plan-only reste actif.
- Aucun gel de schéma, commit, push ou plan 29/30/31 avant correction, vérifications et clôture effective du 28 sous contrôle Codex.
