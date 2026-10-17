# GO — Stream 11 (audit informationnel D2/D3) : revue du plan et réponses aux hypothèses

Date : 2026-10-17.
Destinataire : instance Claude Code en charge de l'implémentation du stream 11
(`prompts/streams/prompt-11-audit.md`).
Plan concerné : `~/.claude/plans/drifting-baking-lovelace.md` → plan final à consigner dans
`prompts/plans/plan-11.md` (dans le worktree, règle C-plan-recording).

## Instruction préalable — avant toute ligne de code

**Contexte à jour (le plan est en retard sur ces points) :**
- `origin/main` = `653ec8b` (et non `f7bde91`). Depuis la rédaction du plan, deux correctifs ont été
  poussés : `424b199` (AGENTS.md épingle la chaîne d'interpréteur : `.venv/bin/python`, Trading d'abord
  puis le venv, jamais Trading seul) et `8ae232e` (les 4 contrats bloquants tournent désormais en
  `.venv` — `importorskip("torch")` module-level remplacé par `skipif` sur les 4 guards torch ; et
  `test_reconstruction_from_cache` est sauté hors stack de référence). La Tâche 0 crée le worktree
  depuis `origin/main` : la base est à jour malgré la ligne « Base : f7bde91 ».
- **La panne `test_reconstruction_from_cache` de `f7bde91` est résolue — ne pas la réexaminer.** La
  sonde 11 du plan la vérifie déjà (passe en `.venv`, 4,9 s) ; elle venait de l'interpréteur Trading
  (numpy 1.26.4) utilisé par l'instance stream 08. C'est désormais durable : skipif hors stack de
  référence (`8ae232e`) + interpréteur épinglé dans AGENTS.md (`424b199`). Ne pas y consacrer de tâche.
- **Interpréteur** : la chaîne du plan (`conda activate Trading` puis `source .venv/bin/activate`) est
  la bonne — c'est la règle « Interpreter » d'AGENTS.md. Pour `git`/`ls`, la chaîne conda seule suffit
  (indépendant de l'interpréteur Python) ; la chaîne complète ne pose aucun problème.
- **Données EUROFIDAI restaurées** (`653ec8b`) : `data/raw/eurofidai/` (426 Mo, 153 fichiers) et
  `data/derived/d4_eurofidai/` (89 Mo) sont de retour, rebuild vérifié bit-identique, manifeste à jour,
  22/22 tests eurofidai au rebuild. Le stream 11 n'en a pas besoin (D4 hors périmètre). Les 3 tests
  réels eurofidai vont de nouveau tourner dans `make check` (baseline attendu : run 1 = 22 passés +
  4 sautés, run 2 = 187 passés).
- **`prompts/plans/plan-11-vibe.md` (arbre principal) est périmé** — plan d'une autre instance (base
  `be7d938`, datation `strict_ps` seule). Ne pas le lire ni le suivre : le plan canonique est celui-ci,
  enregistré en `prompts/plans/plan-11.md` dans le worktree. Une seule instance implémente le stream 11.
- Après le push du stream, **retirer `prompts/GO-stream-11.md` de l'arbre principal** avant d'y
  avancer `main` (fichier non suivi qui bloquerait le checkout) — le plan le signale en risque.

**Enregistrer le plan final** dans `prompts/plans/plan-11.md` (worktree), section
« Décision GO intégrée » remplie avec les réponses ci-dessous ((Hn) → (GO Hn)), avant toute
ligne de code.

## Verdict

**GO.** Le plan est conforme au prompt 11 item par item : spectre et η (calib, avec/sans LW, bord MP,
K), signes (ρ̂_signe, ρ = sin(πρ̂/2), K_eff), symétrie centrale (q̂ + binomiale exacte, triplets de
Randles sur y/σ̂ avec GARCH(1,1), correction de Holm), spectre de Sharpe de dérive débiaisé aux
transitions des datations SPY (formule exacte, IC bootstrap par blocs de 20 jours, médiane sur les
transitions, sous-espaces contraints à d_S ≤ 30), plafonds N1/N2/N3, part du budget à γ ∈ {20, 252},
gains prévus évalués par `floors` sur les estimations — avec les livrables (8 CSV, 4 figures PNG+PDF,
journal, tests), les contraintes (fenêtre 2005–2019 avec contrôle bloquant, graines `SeedSequence`,
figures depuis les CSV relus en `round_trip`) et les critères (estimations négatives rapportées,
déterminisme au SHA-256 par double exécution). Sondes solides : base figée contrôlée par
`state_hash` contre le sidecar commité, triplets validés contre l'énumération O(n³) avec
calibration null/puissance, table de planification du plan v4 reproduite, débiaisage vérifié par
Monte Carlo. La politique worktree d'AGENTS.md est respectée (H16). EUROFIDAI hors périmètre,
aucune donnée lue ni indexée.

Le canal retenu est ce fichier (prompt destiné à l'instance), et non l'édition directe de
`~/.claude/plans/drifting-baking-lovelace.md` : le plan appartient au workflow
`superpowers:executing-plans` de l'instance, la règle C-plan-recording fait enregistrer le plan final
par l'instance dans `prompts/plans/`, et la trace de décision reste dans le dépôt.

## Réponses aux seize hypothèses — les seize défauts sont CONFIRMÉS (H12 avec le choix indiqué)

- **H1 (fenêtre et lignes) — CONFIRMÉ** : toutes les lignes de W (embargo inclus), contrôle bloquant
  aucune date > 2019-12-31, spectre et K sur la calib, η par année civile 2005–2019.
- **H2 (base figée) — CONFIRMÉ** : eigen-paires LW de la calib, `state_hash` comparé au sidecar
  commité — contrôle fort.
- **H3 (signes) — CONFIRMÉ** : définition des profils (oracle sur la calib) + arithmétique R15, trois
  segments, gains prévus sur W.
- **H4 (caractéristiques) — CONFIRMÉ** : D3 seule (15 colonnes, NaN → 0, projection euclidienne sur
  le sous-espace idiosyncratique, normalisation quotidienne) ; les caractéristiques de D2 restent
  différées (cohérent avec le GO-05 et la décision stream 12).
- **H5 (symétrie) — CONFIRMÉE** : fenêtre W, q̂ sur y brut (zéros exclus), binomiale exacte
  bilatérale, triplets sur y/σ̂ avec GARCH(1,1) ajusté sur la série, Holm à 5 % sur la famille jointe
  des 2D p-values.
- **H6 (transitions) — CONFIRMÉE** : les trois datations SPY, phase = (début, fin], frontière dans
  [2005-01-01, 2019-12-31), n₁/n₂ ≥ 20 ; `lt_spy` et `symmetric` sans déduplication (identiques sur
  SPY, sonde 3), signalé dans le journal. Le prompt dit « les datations de SPY » (pluriel).
- **H7 (sous-espaces) — CONFIRMÉ** : blocs d'au plus 30 PC, somme sans covariances inter-blocs, Σ̂
  intra-phase poolée (ν = n₁ + n₂ − 2) ; contrainte d_S ≤ 30 respectée ; écart `C-audit-subspaces`.
- **H8 (débiaisage) — CONFIRMÉ** : `sr2_debiased` (forme exactement sans biais) par défaut, la
  formule littérale du prompt conservée en `sr2_spec`, les trois colonnes au CSV ;
  `test_debiased_sr2_unbiased` (Monte Carlo, Tâche 3) chiffre l'absence de biais et le biais résiduel
  de la formule du prompt.
- **H9 (bootstrap) — CONFIRMÉ** : blocs mobiles de 20 jours dans chaque phase, B = 2000, tirages
  partagés entre sous-espaces et transitions, graines `SeedSequence([11, crc32…])`, IC percentile,
  IC des médianes par tirage.
- **H10 (N1) — CONFIRMÉ** : énergie blanchie du bloc PC(K+2)..PCN, dispersion du jour sans modèle de
  volatilité, valeur brute et corrigée χ².
- **H11 (N2) — CONFIRMÉ** : LW glissant 60 jours (passé seulement), F1 = colonnes de B, F2 = résidus
  GLS des 15 caractéristiques, rapport ≥ 1 exactement.
- **H12 (N3) — CONFIRMÉ, variante choisie : `mvt_static`** (lecture littérale du prompt : « loi t
  multivariée ajustée sur les résidus blanchis »). Les variantes `mvt_garch` et `t_garch` restent
  dans le CSV (colonne `variant`).
- **H13 (part du budget) — CONFIRMÉE** : L = n₂ découpé, Î de la transition d'arrivée, sous-espaces
  agrégés seuls.
- **H14 (gains prévus) — CONFIRMÉ** : formules du tableau du plan v4 évaluées sur ρ̂ (rendements, W),
  ρ̂_signe (W), K, N et κ̂ ; NaN propagé si une médiane ≤ 0 ; aucune valeur de planification
  substituée (consigne du plan v4 respectée).
- **H15 (figures) — CONFIRMÉE** : 4 figures depuis les CSV relus, PNG + PDF, `CreationDate=None` pour
  la déterminism du PDF.
- **H16 (exécution) — CONFIRMÉE** : worktree `~/JEPA-Drift-stream-11`, branche `stream-11` depuis
  `origin/main`, liens absolus `.venv/`/`data/raw/`/`external/`, fin par
  `git push origin stream-11:main` après rebase — conforme à la section « Worktrees and parallel
  streams » d'AGENTS.md.

## Points particuliers

- **Skill `dataviz`** : s'il n'existe pas dans l'environnement de l'instance, poursuivre sans — les
  règles de déterminisme sont déjà spécifiées (MPLBACKEND=Agg en tête de script, pas de date dans les
  figures, figures depuis les CSV relus, `CreationDate=None` pour le PDF).
- **Liens du worktree non suivis** (les motifs `.venv/`, `data/raw/`, `external/` de `.gitignore` ne
  couvrent pas un lien symbolique) : jamais indexés (le plan le prévoit). Optionnel, hors ce GO :
  étendre `.gitignore` sans slash final.
- **`make check` au démarrage** inclura les 3 tests eurofidai réels (données restaurées, 22/22 au
  rebuild) : baseline attendu run 1 = 22 passés + 4 sautés (guards torch), run 2 = 187 passés.
- **Jamais indexés** : les liens du worktree, les fichiers D1/D2 réécrits par le fixture de
  `make check`, `logs/d4/` (journal du stream 10, décision du chercheur en attente).
