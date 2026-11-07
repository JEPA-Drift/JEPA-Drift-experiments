# AMORÇAGE — Codex orchestrateur, reprise après clôture des lots 21 et activation du cron

**Date : 7 novembre 2026. Racine : `~/JEPA-Drift-experiments`. Base publiée de rédaction : `9ec3a7bd4406733d5da1d9b9337be63658b7e178`.** Cette base comprend les clôtures décrites ci-dessous ; elle ne désigne pas le futur commit documentaire portant ce fichier. Relire l'état réel avant toute reprise.

Codex orchestre les sessions Claude Code interactives, examine leurs plans et réponses, émet les GO dans le mandat délégué, audite les livrables et intègre Git. Le code scientifique est confié à Claude après GO. Les opérations hôte et la présente passation documentaire ont été exécutées directement par Codex sur instruction explicite de l'utilisateur.

**Mandat accompli à la base de rédaction :** persistance utilisateur du moniteur, audit/corrections/clôture de `21-dpi` et `21-appendix`. Les deux sessions sont fermées. **Aucun nouveau stream n'est lancé par cette passation.** Les prochains travaux sont ordonnés en section D, avec leurs conditions et limites.

**Mandat scientifique inchangé :** aucune nouvelle expérience PCA sans oracle, aucune expérience sur données réelles ou JEPA/VAE, aucune campagne E4/SPLL, évaluation J4, création effective de `FROZEN.json` ou réexécution du benchmark PCA full. L'existence de l'oracle gaussien du lot 19 ne constitue pas une autorisation de campagne. Une date de jalon ou un quota réinitialisé ne vaut pas GO scientifique.

## A. Sources de vérité et préflight en lecture seule

Lire `CLAUDE.md`, mémoire canonique ; `AGENTS.md` est son lien relatif, pas une seconde mémoire à remplacer. Appliquer ses règles scientifiques, environnementales, de plan/GO/wrapup et de Git. Lire ensuite ce document, le prompt exact du périmètre envisagé, son code existant, ses plans, GO, wrapups et déviations pertinents.

Le présent inventaire remplace les **statuts et ordres de lancement** des reprises du 24 octobre et du 6 novembre. Ces documents et leurs preuves restent archivés. `prompts/streams/INDEX.md`, `prompts/wrapups/handover-01-27.md`, l'ancienne matrice `docs/audits/streams_01_27_relevance_2026_11_06.md` et les colonnes de modèles historiques ne sont pas des commandes de relance. Un wrapup précommit disant « uncommitted » n'annule pas une intégration ultérieure vérifiée ; la présence d'un prompt n'implique pas un travail ouvert.

Avant toute mutation, relever depuis la racine :

```bash
pwd
git rev-parse --show-toplevel
git rev-parse HEAD origin/main
git status --porcelain=v1 --untracked-files=all
git branch -avv
git worktree list --porcelain
git log --oneline --decorate -12
tmux list-sessions 2>/dev/null || true
ps -u "$USER" -o pid,ppid,etime,comm,args | rg 'claude|codex|vibe|pca_drift' || true
crontab -l
systemctl is-active crond.service
systemctl is-enabled crond.service
```

Consulter les journaux locaux `logs/orchestration_20261107/continuation.md`, `logs/claude_surveillance.log`, `logs/cron_monitor.log`, `logs/claude_sessions.json` et l'éventuel `logs/NEEDS_CODEX_REVIEW`. Ces fichiers sont ignorés par Git et ne sont pas nécessairement présents dans un autre clone. Ne pas publier les buffers, chemins propriétaires ou l'adresse du dépôt dans une communication publique.

Comparer les références avant/après `git fetch origin`, effectué seulement après le préflight. Ne jamais déplacer, nettoyer ou réécrire un worktree d'autrui. Aucun `git stash`, `reset --hard`, `clean -fd`, `checkout`, rebase ou suppression d'un worktree historique ; aucun `git add .`, `git add -A` ou push forcé.

### A1. État Git et worktrees à transmettre

Après les deux intégrations, le `main` local et `origin/main` étaient à la base publiée ci-dessus, sans changement suivi. Deux fichiers utilisateur restent volontairement **non suivis** dans le dépôt principal :

| Fichier à préserver, hors staging | SHA-256 |
|---|---|
| `prompts/31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` | `fbfccc96fc777b6fef600ae9b16239ba46a852b68444ec3b717ac1d0a8e36c4c` |
| `prompts/FIX-stream-31-nb-assets.md` | `ce91c1899db2fac30dcb88e64f3b1043861263adb7c2988d5394a706b84735e6` |

La rédaction a commencé dans un **worktree propre**, `~/.codex/worktrees/1721/JEPA-Drift-experiments`, branche `stream-00-reprise-20261107`, après fast-forward de l'ancien lot opérationnel. Ne pas supprimer les deux fichiers utilisateur pour rendre artificiellement propre le dépôt principal.

| Worktree ou groupe | État vérifié après audit ; conduite à tenir |
|---|---|
| `~/.codex/worktrees/a1a8/JEPA-Drift-experiments`, `stream-21-dpi` | Propre à `527e59c`, commit intégré ; session fermée. Aucun resume nécessaire. |
| `~/.codex/worktrees/63f8/JEPA-Drift-experiments`, `stream-21-appendix` | Propre à `9ec3a7b`, commit intégré ; session fermée. |
| `~/.codex/worktrees/5182/JEPA-Drift-experiments`, `stream-21-trace` | Lot clos à `da518dd`, intégré ; conserver. |
| `~/JEPA-stream-18-closeout-20261106` | Clôture documentaire `ef77886`, intégrée. L'adaptateur reste indisponible. |
| `~/JEPA-stream-19` | Clôture documentaire `3467df4`, intégrée ; l'oracle ultérieur est sur main. |
| `~/JEPA-stream-21` | Lot documentaire `ebf94bf`, intégré ; ne signifie pas gel/runner livré. |
| `~/JEPA-stream-23` | Propre à `3d0bd2071cb86afc6b196b5020ff729204746a93` ; deux commits non intégrés : `7e4c7a1`, puis `3d0bd20`. **Préserver sans mutation ni fusion automatique.** |
| `~/JEPA-stream-23-review-20261106` | Revue documentaire `03f1ced`, intégrée ; elle n'intègre pas la phase 1 E6. |
| `~/JEPA-full-2000` | Branche `ops/pca-full-2000-20261101` à `1af0862` : README local additionnel non intégré. Données full non suivies ; ne pas modifier ni supprimer. |
| `~/JEPA-stream-28`, `~/JEPA-stream-29`, `~/JEPA-stream-30`, `~/JEPA-stream-31` | Lots intégrés, dernières têtes respectives `fc533d0`, `6f9322b`, `b025450`, `69d5624`. Archives à préserver, pas des sessions à reprendre. |

Recontrôler ces têtes plutôt que les avancer pour uniformiser les worktrees. À la clôture des deux lots 21 : **zéro processus Claude actif**, aucune des sessions `jepa-s21-dpi` et `jepa-s21-appendix` présente, modèle/effort conservés jusqu'à la fin de chaque session. Un terminal tmux personnel restant n'est pas une session Claude appartenant à Codex.

## B. Invariants et résultats scellés

### B1. Environnement et rigueur

Exécuter tout code/test du projet avec **`.venv/bin/python`**, jamais le Python Trading seul. Le venv partagé repose sur Python 3.12.9 ; conserver `requirements.lock` et `conda-torch.lock` : NumPy 2.4.4, SciPy 1.17.1, pandas 3.0.6, PyYAML 6.0.3, torch 2.14.1 CPU conda-forge selon le pont existant. Ne pas installer ou actualiser de dépendance. Dans un worktree, `.venv` et `external` sont les liens absolus partagés prescrits ; `data/raw` reste un vrai répertoire avec des liens individuels pour les seules sources nécessaires, jamais un lien global.

Avant les imports numériques :

```bash
export PATH="$PWD/.venv/bin:$PATH"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg
```

PRNG locaux injectés via `SeedSequence`, aucun état aléatoire global ; ingestion pandas `float_precision='round_trip'`, export scientifique via `save_fair_csv`, SEM avec `deff`. Maintenir les frontières d'import monitors/représentations/JEPA, le null sans dérive pour l'ajustement et la séparation calibration/holdout. Aucune fuite des ruptures alternatives vers les seuils ou la sélection ex ante.

Les représentations et seuils restent gelés pendant `monitor`. D6 est une symétrisation par signe journalier, pas une justification de symétrie des données brutes. Les comparateurs P4-D du stream 17 n'ont pas une FPR indépendante calibrée. Distinguer budget d'évidence, anytime-valid, exact, FPR(H), ARL0 et RMST censurée. `ln(gamma)/I` n'est pas un ADD exact. La KL Student du benchmark est un proxy gaussien ; l'additivité de KL de moyenne dans la vraie base propre ne s'étend pas aux rotations de covariance. Le critère fluide de mélange ne prouve pas l'optimalité d'un détecteur exact.

Les données 2020+ restent derrière le gel explicite et les garde-fous de `CLAUDE.md`. Le calendrier J3/J4 n'ouvre aucune porte. Aucun accès expérimental aux rendements ni nouvelle reproduction réelle par cette passation. Les tests de régression prescrits restent permis. EUROFIDAI ne quitte jamais la machine et aucun chemin ou contenu propriétaire n'entre dans un commit ou journal.

### B2. J1 et D8

| Invariant | État à conserver |
|---|---|
| `results/e2/e2_cells.csv`, disque **et** blob d'index | SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, **47 CRLF et zéro LF isolé**, attribut `-text`. Ne pas normaliser ni réexporter. |
| `results/e3/e3_overshoot.csv` | SHA-256 `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`. Critère E3/D8 `iid/first_order_d1_l3` : **FAIL +5,2833 %**, tolérance 5 %. Ne pas relancer pour obtenir PASS. |

Le critère D8 d'E3 est distinct du jeu D8 Electricity. Écart J1 ou échec de reproduction scientifique : arrêt et constat, sans changement de code/paramètres destiné à forcer une concordance. Blocage infrastructure/syntaxe : trois tentatives bornées au maximum, puis gel déclaré et signalement.

### B3. PCA 28–31 : clos dans leurs périmètres

Le full 2000/rôle appartient à la lignée `87a15ad`. Les outils 28, tableaux 29 et figures 30 sont intégrés. Aucune nouvelle simulation, table, figure ou correction des sorties scellées n'est autorisée. Les fixtures de contrat ne remplacent pas les trajectoires réelles du run.

| Preuve | Identité |
|---|---|
| `results/pca_drift_benchmark/full_2000_20261101/manifest.json` | SHA-256 `3b2299bc1c841ef5c9f425a135ad9e318b310c08acfbfaf228a0b49034372f47` ; `run_mode=full` ; empreinte `ea702d03b9faf332d0ae74a7746422189b92854fbe728ceff9cb842a3ce7985a` |
| `trials.csv` full, local à `~/JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/` | SHA-256 `40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c` ; 716 000 lignes de données, 48 317 020 octets. Ne pas copier, lier dans une fixture suivie ou ajouter à Git. |
| `results/pca_drift_benchmark/tables/full_2000_20261101/table_manifest.json` | SHA-256 `79804fcf434ee375446d2fdbeface8bda189fb1e7e530fb7095151ddde87f619` |
| `figure_manifest.json` dans `results/pca_drift_benchmark/figures/full_2000_20261101/` et `full_2000_20261101_fix_smoke_no_claims/` | Les deux : `41b36c4e2c0ca8fed34ce216c2844c39518fd0b4dee4153e813dcaec47f72ade` |

**Stream 31 = CLOS_VALIDÉ pour l'outillage et les 44 contrats autorisés.** Outillage `20ad9e860a58373ec85405de6ee19a68322dd02e`, QA et correctif autorisé de provenance des effectifs `69d562419be77b17af9e56711a6ae069caa6bfc4`. Plans et GO : `plan-31.md`, `GO-stream-31.md`, `plan-31-fix.md`, `GO-stream-31-fix.md`. Rapport : `docs/audits/PCA_CONTRACTS_VALIDATION.md`, wrapup : `prompts/wrapups/wrapup-31.md`.

Leurs mentions précommit « uncommitted » et le STOP historique à 43 PASS/1 FAIL décrivent des checkpoints antérieurs. Le correctif a été intégré ; la réception finale était **44 PASS, zéro FAIL, zéro skip, G1 exécuté**. Les hooks de clôture suivants incluent ces 44 tests. Ne pas rouvrir 31 sur la seule lecture de l'ancien en-tête.

`make prompts-check` couvre **33 prompts canoniques : 29 historiques et 4 PCA**. Le prompt historique `prompt-28-e11.md` (Electricity) et `28_STREAM_PCA_DRIFT_RUNNER.md` ont des identités distinctes. `11b` n'a pas de prompt autonome : ses décisions sont dans son GO et le wrapup consolidé 11. Les fichiers `00_CODEX_...` ne sont pas des prompts canoniques de stream à synchroniser dans le master. Aucun `--sync-master` aveugle.

## C. Inventaire actualisé de tous les streams

Les SHA des travaux intégrés ci-dessous ont été contrôlés comme ancêtres de la base de rédaction. Les statuts s'appliquent au **périmètre nommé**, sans nouvelle reproduction des expériences anciennes. Ils ne transforment pas un résultat exploratoire ou un FAIL conservé en résultat confirmatoire.

| Stream | Décision et périmètre actuel | Preuve intégrée ou condition restante |
|---|---|---|
| 01 | CLOS_VALIDÉ — fondations analytiques/E2 | `320dea7`, J1 scellé |
| 02 | CLOS_VALIDÉ — D1/D2 | `aa3a155` |
| 03 | CLOS_VALIDÉ — construction D3 | `3e3a804` ; biais de survivants et caractéristiques datées restent déclarés |
| 04 | CLOS_VALIDÉ — moniteurs et ports Article B | `b74ad6c` |
| 05 | CLOS_VALIDÉ — injection, D5/D6 | `cbd0692` |
| 06 | CLOS_VALIDÉ — représentations/interface Z-1 | `eae6f33` |
| 07 | CLOS_VALIDÉ — pipelines | `d5aa364` et correctifs intégrés |
| 08 | CLOS_VALIDÉ — contrats/hooks | `f7bde91` et correctifs intégrés |
| 08b | CLOS_VALIDÉ — hygiène/helpers | `24be667`, intégré dans la lignée `33d847d` |
| 09 | CLOS_VALIDÉ — loader BAF seulement | `611a1b9` ; ni T-JEPA ni E9 entraîné |
| 10 | CLOS_VALIDÉ — loader/spécification D4 | `672ce26` ; n'affirme pas la disponibilité/reproduction des données privées dans chaque worktree |
| 11 | CLOS_VALIDÉ — audit descriptif | `9a36c2f`, `985353b` ; pas de gain ex ante déduit des frontières choisies |
| 11b | CLOS_VALIDÉ — placebos/bruit | `4974815` ; GO 11b, wrapup consolidé 11 (`3b77562`) ; garder les NaN descriptifs |
| 12 | CLOS_VALIDÉ — E1 | `ecf4ab3`, intégré dans `77991ac` |
| 13 | CLOS_VALIDÉ — ingénierie/archive E3 | `1dcc392`, intégré dans `4811bda` ; **D8 reste FAIL** |
| 14 | CLOS_VALIDÉ — bottleneck natif JEPA | `67437b3`, intégré dans `779e3fb` ; aucune campagne entraînée/J3 livrée par cette clôture |
| 15 | DIFFÉRER — T-JEPA BAF | Dépend du loader 09 ; hors priorité finance et hors mandat JEPA |
| 16 | À_REPLANIFIER — préentraînement/J3 | Le prompt à ACP post-JEPA contredit le bottleneck natif 14 ; objectifs, graines et décompte des runs à réconcilier ; aucun modèle J3 produit |
| 17 | CLOS_VALIDÉ — IPCA, périmètre d'ingénierie | `6ed8f8a`, intégré dans `b95f077` ; P4-D avec contrôle in-sample n'est pas une référence principale à FPR indépendante calibrée |
| 18 | BLOQUÉ — intégration CD-DFM ; documentaire clos | `ef7788670b1c88bf1bb751418e3ad7a9cc962d88` ; package de données/prétraitement manquant au pin, conditions amont non satisfaites |
| 19 | À_REPLANIFIER — E4/SPLL global ; deux lots clos | Audit `3467df4b7426fa15c1ab16ef94687f25a976636d`, oracle pur `46c24923957ec505947016118def9453284bd1bc` ; aucune campagne E4 exécutée |
| 20 | DIFFÉRER — transmission de dérive | Attend des représentations 16 entraînées et les comparateurs pertinents 17/18 ; pas de JEPA réel autorisé |
| 21 | TERMINER_PARTIEL — quatre lots clos, stream global incomplet | Audit `ebf94bf`, checker `da518dd`, DPI `527e59c`, annexe `9ec3a7b` ; runner et gel effectif absents |
| 22 | DIFFÉRER — E5/porte J4 | Prérequis historiques 16, 17, 19, 21 et 23 phase 2 ; 18/20 complémentaires ; aucun gel ni modèle prêt au sens du protocole |
| 23 | À_REPLANIFIER — E6 ; revue documentaire close | Revue `03f1ced99cc98f63d7b28010170b197a9f123ac3` ; phase 1 originale non intégrée, phase 2 attend 16 ; conditions C1–C7 et nouveau GO requis |
| 24 | DIFFÉRER — E9 BAF | Dépend de 09 et 15 ; finance prioritaire, pas de JEPA autorisé |
| 25 | DIFFÉRER — événements/régimes réels | Attend le gel effectif 21 et les garde-fous rétrospectifs/Covid/embargo |
| 26 | DIFFÉRER — absorption | Attend 14 et les modèles entraînés 16 ; toute fenêtre 2020+ reste derrière le gel |
| 27 | CLOS_VALIDÉ — E10 F1 linéaire seulement | `57c3a34`, intégré dans `c284823` ; complément F2 et P5 distincts, non lancés |
| 28 historique | DIFFÉRER — E11 Electricity | `prompt-28-e11.md`, branche hors priorité finance ; pas le runner PCA |
| 28-PCA | CLOS_VALIDÉ — runner/full scellé | `fc533d0`, full intégré dans la lignée `87a15ad` ; aucun rerun |
| 29 | CLOS_VALIDÉ — tableaux PCA | `6f9322b` ; réemploi des métriques scellées, lecture seule |
| 30 | CLOS_VALIDÉ — figures PCA et corrections autorisées | `b025450`, `a0c576e`, puis provenance des effectifs dans `69d5624` ; aucun nouveau rendu |
| 31 | CLOS_VALIDÉ — outillage/QA/correctif borné | `20ad9e8`, `69d5624` ; 44 contrats, voir B3 |
| 00-monitor | CLOS_VALIDÉ — harnais et persistance utilisateur | Documentation E4 `4dfbe2a`, harnais `21aea53`, cron/PATH `c24ff626895a35e4944f91e70f4fa43a8cc63159` |

### C1. Portée exacte des quatre lots 21

1. **Documentaire**, `ebf94bffa84d491ffa37df91b7e156521a46d8b6` : `docs/MAPPING.md` et `docs/audits/stream_21_trace_scope_2026_11_06.md`. Recensement de 507 jetons numériques, 19 occurrences classées porteuses de résultat, **6/19** liées à une cellule analytique E2 scellée. Les **13 autres** : un candidat dérivé, cinq valeurs analytiques avec référence de test, trois sans CSV/test, quatre bornes de plages sans source identifiée. Ne pas inventer de source pour combler ces lacunes.
2. **Checker**, `da518ddaab1322c938a668e7e9d12f477d3b3475` : `tools/trace_numbers.py`, 88 tests. Vérifie le sous-ensemble déclaré, ses empreintes et littéraux entiers arrondis à zéro décimale avec `ROUND_HALF_EVEN`. `READ_MATCH` n'est ni une preuve scientifique, ni une reproduction du producteur, ni la couverture de tout l'article.
3. **DPI**, `527e59c920a10e0563ab57e821461a036213ccea` : `tools/dpi_lint.py`, 69 tests. Garde lexical à grammaire finie, signalant FLAG/NEGATED ; **zéro FLAG n'établit pas la cohérence sémantique avec la DPI**. Le corpus courant donne une négation et zéro FLAG. Audit corrigé : tests compatibles avec l'ajout d'un texte valide et refus contrôlé des erreurs de lecture. Hook final : **849 PASS, 5 skips D4** ; session `jepa-s21-dpi` fermée.
4. **Annexe**, `9ec3a7bd4406733d5da1d9b9337be63658b7e178` : `tools/appendix_b.py`, 92 tests. Inventaire **partiel des valeurs déclarées** dans deux sections YAML et quatre lignes D5, six liens manuels. Réception : **17 lignes = 6 MATCH, 0 DIVERGENT, 0 UNSUPPORTED_DOC_VALUE, 7 UNMAPPED_CONFIG, 4 UNMAPPED_DOC**. Fragment ignoré SHA-256 `dabf3ca9482c4721ec84b8eea2d29d4f8a97449fd3fbe8c5ecb27bbc450803c2`. Les deux derniers statuts décrivent ces liens, pas une absence globale dans la note/code. Corrections : refus des clés construites équivalentes et des cycles dans les sections sélectionnées, sans refuser la réutilisation finie d'un alias. Réception Codex **181 PASS**, puis hook **941 PASS, 5 skips D4** ; session `jepa-s21-appendix` fermée.

Plans/GO/wrapups de chaque lot sont intégrés sous `prompts/{plans,wrapups}/` et `prompts/GO-stream-21*.md`. Les deux sessions sont restées sur **Opus 5.5 Max**, sans changement d'effort ni purge de contexte. Leurs validations ont été sérialisées parce qu'elles appellent toutes deux `tools.trace_numbers`.

Limites annexe : ni grilles F1–F4 en prose, ni littéraux de code, ni paramètres effectivement exécutés. Les configurations courantes ne contiennent pas de cycle/merge ; la sentinelle doit être réexaminée si leurs sources changent. YAML extrêmement imbriqué : un `RecursionError` peut encore produire un traceback sans refus préfixé ; très grand entier : diagnostic potentiellement sans préfixe d'entrée. Ces limites sont consignées dans le wrapup et restent hors du correctif clos.

**Ne sont pas livrés :** `jepadrift/benchmark_runner.py`, `tools/freeze_config.py`, `configs/FROZEN.json` et le gel global J4. Le runner PCA 28 ne remplace pas par défaut le contrat du runner global 21. Aucun de ces fichiers ne doit être créé pour donner artificiellement le statut « clos » à 21.

### C2. Blocages 18, 19 et 23

**18.** `external/cd-dfm` reste au pin `37a1dfb39974884df822aa2994854bbf1270e381`. Le package attendu `data.dataset`, le prétraitement et les imports `cddfm` nécessaires ne sont pas disponibles dans le périmètre inspecté ; pas de fichier de licence suivi au pin. C'est un constat, pas une conclusion juridique. Aucun adapter, installation, entraînement ou comparateur fictif pour contourner le blocage. Nouveau pin/package et conditions de réutilisation établis avant un nouveau plan/GO.

**19.** L'oracle pur porte sur une moyenne gaussienne connue avec covariance équicorrélée ; le gain analytique est `N/(1+(N-1)*rho)`, plafond `1/rho` seulement pour `rho>0`. Ce lot ne traite ni les préfixes PCA k, ni toutes les questions N versus d, ni SPLL, ni une campagne. Lire `experiments/e4_oracle_reference.py`, `tests/test_e4_oracle_reference.py` et `docs/sections/e4_oracle_reference.md` avant replanification. L'article/code primaire SPLL doit être identifié avant toute prétention de reproduction. CD-DFM est un complément conditionnel, pas un prétexte pour bloquer toute question analytique 19.

**23.** Lire `docs/audits/stream_23_compatibility_2026_11_06.md`. La revue ne fusionne pas les deux commits originaux et ne reproduit pas E6. Une intégration future exige un déclencheur écrit, un nouveau GO C1–C7, un **nouveau** worktree depuis main, reprise des deux commits dans l'ordre, déviation ajoutée sans écraser l'historique, reproduction complète et quick avec SHA attendus, 13 tests E6 puis `make check`. Une divergence de reproduction déclenche l'arrêt D3. Les appels D6 requis sont hors de l'actuel mandat de données réelles. Ni P4-D/P5-D ajouté ni contribution J4 implicite. Distinguer l'index aveugle à certaines baisses de variance et l'alignement du canal d'un gain JEPA ; indexation E6 zéro-based et PCA full un-based à documenter.

## D. Ordre conditionnel des prochains travaux et dépendances

**Aucun nouveau GO d'implémentation scientifique n'est contenu dans ce document.** Les deux premières entrées sont des replanifications à examiner avant code. Ne pas remplir deux créneaux pour respecter un nombre minimal : deux est un plafond, et une dépendance non produite demeure bloquante.

| Ordre | Prochain périmètre | Préalables et décision de lancement |
|---|---|---|
| 1 | **21 restant : traçabilité puis architecture runner/gel** | Partir des quatre lots clos ; classer les 13 occurrences restantes, définir leurs sources sans inventer de CSV, délimiter le runner global et les configurations à geler. Plan de tâches d'ingénierie bornées et GO distinct avant code. Ne pas créer FROZEN, lancer J4 ou une reproduction réelle. |
| 2 | **19 restant : nouvelle question E4/SPLL** | Réutiliser l'oracle clos ; lever l'ambiguïté N/d/k, vérifier la référence SPLL primaire et l'apport non redondant face au full. Plan seulement tant que le chercheur n'a pas autorisé la campagne et ses entrées. |
| 3 conditionnel | **18 intégration** | Seulement après résolution documentée du package et des conditions amont ; nouveau pin, plan/GO. L'ancien constat ne vaut pas implémentation. |
| 4 conditionnel | **16 J3 révisé** | Autorisation JEPA/données nouvelle, plan conforme au bottleneck natif 14, protocole et nombres de runs cohérents ; produire réellement les checkpoints et contrôles de fuite. |
| 5 conditionnel | **23 E6** | Phase 1 seulement si son utilité et C1–C7 sont acceptés ; phase 2 après checkpoints 16 et références nulls appropriées. La reproduction D6 nécessite un nouveau mandat. |
| 6 conditionnel | **21 gel/runner effectif, puis 22 E5** | Gel seulement après protocole/configurations approuvés, avant accès monitor. E5 attend 16, 17 recevable, 19, 21 effectif et 23 phase 2 ; 18/20 complètent selon le protocole. Aucun jalon calendaire ne remplace ces livrables. |
| 7 conditionnel | **20, 26, puis 25 selon leur porte** | 20/26 attendent les modèles 16 et références ; 25 attend le gel 21 et les cohortes/embargos. Ces voies ne sont pas autorisées aujourd'hui. |
| Différé | **15 → 24 ; 28 historique ; compléments 27** | BAF/Electricity restent secondaires ; F2/P5 de 27 demandent leur propre plan et, pour P5, le modèle 16. |

Les plans documentaires 21 et 19 peuvent être préparés en parallèle **seulement** s'ils n'écrivent aucun fichier partagé et n'exécutent aucun module commun du projet. Ils n'ont pas encore un GO de mise en œuvre par ce classement. Toute phase d'implémentation susceptible d'appeler `floors`, `pipelines`, les helpers de traçabilité ou les mêmes tests doit être sérialisée. L'ordre de gel exact et son ensemble de configurations sont des objets du plan 21, pas une dépendance à inventer pour conclure que le gel existe.

## E. Orchestration interactive, GO et exclusivité

### E1. Plafond et ressources

**Au maximum deux instances Claude Code simultanées au total**, planification, reprise, implémentation et audit délégué compris. Les exceptions temporaires anciennes ne sont plus applicables. Pas de délégation imbriquée Agent/Task pour contourner ce plafond. Audits directs par Codex possibles sans ouvrir un troisième Claude.

Avant chaque lancement, déclarer le propriétaire, branche/worktree, chemins écrits, modules du projet appelés directement ou indirectement, validations prévues et dépendances de livrables. **Deux worktrees distincts ne suffisent pas à établir l'indépendance.** Aucun appel concurrent aux mêmes modules partagés, même sans écriture. Un `make check` occupe seul le créneau de validation ; intégrations Git et réindexations sont sérialisées. Le moniteur hôte lit des métadonnées et buffers, sans appeler de module scientifique ni helper de traçabilité.

Un stream complexe, mathématique ou à risque d'erreur élevé utilise **Claude Opus 5.5, effort Max**. Fixer ce niveau avant le lancement. **Ne jamais modifier l'effort d'un stream en cours d'implémentation**, ni purger son contexte pour économiser un quota : cela casse le cache. En cas de quota atteint, conserver la session et le dernier état, consigner puis reprendre après réinitialisation ; ne pas multiplier les instances ou changer silencieusement de modèle.

### E2. Plan, revue, GO, puis code

Préparer un nouveau worktree seulement après vérification de l'absence de collision de nom/propriétaire, sur une base publiée auditée. Exposer l'environnement partagé et les seuls liens de données nécessaires selon `CLAUDE.md` ; aucune installation de remplacement.

Lancer dans tmux une CLI **interactive** en mode plan natif, avec les options réellement supportées par la version locale. Exemple pour un stream complexe, dans son worktree déjà préparé :

```bash
claude --version
claude --help
tmux new-session -d -s jepa-sXX -c "$PWD" \
  'claude --model claude-opus-5-5 --effort max --permission-mode plan --disallowedTools Agent Task'
```

Envoyer le prompt exact et les sources nécessaires : **plan uniquement, pas de code/test applicatif avant GO, pas d'expérience**. Exiger hypothèses, valeurs par défaut, dépendances, propriété des fichiers, tests de rejet, cas limites, garanties scientifiques et questions d'arbitrage. Lire les réponses ; corriger les hypothèses erronées avant toute permission d'implémentation.

Enregistrer le plan en français à `prompts/plans/plan-[XX].md` **avant exécution**, avec « Décision GO intégrée », et la revue en `prompts/GO-stream-[XX].md`. Identifier l'autorité réelle : GO Codex dans le mandat délégué, sans attribuer une signature personnelle au chercheur. Une extension de mandat scientifique exige le chercheur ; Codex ne l'autorise pas en renommant un lot.

Après GO explicite seulement, quitter le mode plan par le mécanisme officiel de la **même** session, vérifier son mode de permissions et exécuter le plan en TDD borné. Ni `claude -p` headless ni `--dangerously-skip-permissions` par défaut. Répondre aux questions techniques en contexte. Toute modification de protocole, source ou périmètre exige un GO écrit adapté ; aucun changement d'effort en cours de travail.

### E3. Surveillance déterministe toutes les 30 minutes

**Installation effective sans root :** la crontab utilisateur est disponible en lecture/écriture. Une seule entrée est installée, avec le chemin absolu correspondant à :

```cron
*/30 * * * * $HOME/JEPA-Drift-experiments/tools/ops/monitor_claude_sessions.sh >> $HOME/JEPA-Drift-experiments/logs/cron_monitor.log 2>&1
```

Le service hôte est **`crond.service`**, actif et activé au démarrage. Une recherche limitée à `cron.service` avait produit un diagnostic incomplet ; ne pas reproduire cette erreur. Le mécanisme de relance après reboot repose sur crond et la crontab, sans droit administrateur. **Aucun reboot de vérification n'a été effectué.** Le démon provisoire PID 34317 et son enfant 34337 ont été arrêtés après réception ; aucune modification de `.bashrc` n'a été nécessaire. L'ancien `jepa-stream-watch.timer` de 20 minutes reste inactif/désactivé.

Le launcher `tools/ops/monitor_claude_sessions.sh` fixe son PATH depuis le venv et le binaire Python de base résolu, ainsi que l'environnement déterministe ; il fonctionne sans initialisation du shell interactif. Verrou par `flock` : `logs/.claude_surveillance.lock`. Inspecteur stdlib : `tools/ops/monitor_claude_sessions.py`, réception du harnais : 24 tests. Le correctif PATH/cron est publié à `c24ff62`.

À chaque cycle : registre `logs/claude_sessions.json` et découverte `jepa-*`, captures tmux `-S -80`, inspection des processus et worktrees Git autorisés ; aucune frappe envoyée, requête de modèle ou lecture de données. Journal JSON horodaté UTC `logs/claude_surveillance.log`, journal cron `logs/cron_monitor.log`. Les arbres data/venv/cache sont exclus. Les attentes de saisie, plans prêts, quotas, erreurs, sorties, demandes de revue et stagnations alimentent `logs/NEEDS_CODEX_REVIEW`, avec extrait de buffer.

L'inactivité disque/Git au-delà de 1 800 s est enregistrée séparément ; `STALLED` exige aussi l'absence de nouvelle sortie terminal depuis plus de 1 800 s. Ce sont des signaux d'inspection, pas des preuves de succès ou d'échec scientifique. Les cycles cron réels de **01:00:01, 01:30:01 et 02:00:01 UTC** ont été reçus sans erreur ; le contrôle après clôture de **02:15:19 UTC** a retourné trois `ABSENT_NOT_EXPECTED`, zéro drapeau restant.

Les entrées `jepa-s31`, `jepa-s21-dpi`, `jepa-s21-appendix` sont maintenant `required=false`. Enregistrer chaque future session active et son worktree avant de dépendre du suivi ; ne pas marquer une session terminée comme non attendue avant audit/intégration/push. Lire et traiter les alertes ; archiver le drapeau sous le même verrou après vérification de son contenu et de son empreinte, sans perdre d'alerte concurrente. Archive traitée : `logs/orchestration_20261107/NEEDS_CODEX_REVIEW.acknowledged-20261107T0215Z`, SHA-256 `f96669e2c8084fc0677ce665b7d10a5c1010a49d9af2376dd57487c82818ac14`, mode 600. Elle conserve les deux demandes de revue et l'erreur PATH initiale résolue.

**Le dispositif installé lève un drapeau ; il ne réveille pas automatiquement une inférence Codex.** C'est l'alternative d'intervention prévue par E4. La décision, les réponses et les GO restent à Codex lorsqu'il est actif. Ne pas annoncer une boucle de surveillance cognitive persistante ni bloquer l'inférence dans une longue attente ; ne pas ajouter un second démon ou cron.

### E4. Audit, clôture et intégration

À chaque fin de lot : revue du diff complet, tests ciblés utiles, refus/absence de fuite, hashes protégés, J1 disque/index/CRLF et D8 conservé. L'instance implémentante produit son `$wrap-up` et le fichier anglais à six rubriques : Context, Validated Results, Errors and Dead Ends, Current State, Vigilance Points, Recommendations. Plans/GO et `docs/DEVIATIONS.md` en français ; code, tests, audit trails, wrapups et commits en anglais.

Après réception, demander `/exit`, vérifier la fin du processus et fermer uniquement le tmux possédé s'il subsiste. Ne pas changer la base sous une instance qui écrit. Sur un lot arrêté, avancer sa base vers le main publié **avant** l'unique contrôle complet de clôture lorsque le fast-forward et les chemins possédés le permettent. Une base modifiée ensuite impose les contrôles requis, pas un contournement du hook.

Ordre de clôture : wrapup enregistré → `tools/reindex_graphify_jcodemunch.sh` en mode AST/sans résumé IA → `make check` obligatoire → commit → push. Les explorations Graphify/jCodeMunch et appels LLM payants restent sur demande explicite ; la réindexation requise ne les autorise pas. L'indexation du dépôt principal a un plafond partiel de 2 000 fichiers ; les réindexations des lots DPI/annexe ont terminé sans ce plafonnement. Ne pas annoncer une indexation principale complète.

Une collision d'identités jCodeMunch a été rencontrée pendant cette clôture documentaire : les métadonnées de l'index local du worktree correspondaient aux deux identités signalées. Sa copie de sauvegarde hors dépôt précède l'invalidation officielle de cette seule entrée. Si ce cas revient, examiner uniquement les métadonnées du cache possédé, sauvegarder et invalider son identifiant exact ; ne pas supprimer les index tiers ni modifier le paquet global. Le journal local de clôture conserve le diagnostic.

Stage par chemins explicites après `git status`, puis `git diff --cached --check` et lecture du diff. Aucun log/cache, secret, donnée privée, chemin serveur absolu, fichier >50 Mo ou trials full. Conventional Commits anonymes sous l'identité du dépôt existante, sans trailer/co-auteur/signature ajoutée. Examiner **toute la plage poussée**, pas seulement le dernier diff ; vérifier EUROFIDAI, tailles et anonymat.

Intégrer par fast-forward supervisé du main possédé puis **`git push origin main`** ; jamais de push forcé ni de branche de stream envoyée par inadvertance. Si le distant a avancé, réconcilier seulement le lot arrêté et propre et refaire les contrôles exigés. Le dépôt était public, non archivé, avec droit de push lors de la clôture ; l'autorisation compagnon de soumission anonyme reste conditionnée à l'absence de diffusion de son adresse/lien de publication. Ne pas afficher l'URL publiquement.

Les hooks de réception restent actifs. Dernier hook de code : **37 + 904 = 941 PASS, 5 skips D4**, en 36,60 s puis 483,93 s. Les skips sont `test_chars.py:69/83` et `test_data_eurofidai.py:318/326/337`, D4 non construit dans le worktree ; aucun skip torch ni PCA G1. Le budget visé de cinq minutes reste une dette observée, pas une raison de réduire les contrôles numériques. Pour G1 sans copie de données, utiliser seulement le chemin local existant :

```bash
export PCA_FULL2000_TRIALS="$HOME/JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv"
export PYTEST_ADDOPTS=-rs
```

Avant de conclure : vérifier le hash poussé et l'égalité main/distant, l'arbre suivi propre, les deux prompts utilisateur préservés, les sessions fermées et le cron toujours unique/actif. Rendre un rapport factuel avec les tests exécutés, skips, limites et périmètres encore ouverts. Ne pas annoncer un nouveau stream lancé sans plan, GO, dépendances et exclusivité réellement satisfaits.

## F. Première action de la prochaine instance

Effectuer le préflight A en lecture seule et donner un compte rendu bref : Git/worktrees, processus Claude réels, état du cron et du drapeau, clôtures 31/21-dpi/21-appendix et tâches restantes. Si une alerte existe, l'auditer avant toute planification. Sinon, présenter la première replanification 21 puis 19 dans les limites D ; l'ouverture de sessions ou l'implémentation doit être couverte par la demande active, le plan et le GO. Aucun redémarrage automatique des sessions closes, aucun entraînement ou campagne sous couvert d'un ancien numéro.
