# GO — Stream 04 (surveillance 1/3) : revue du plan et amendements

Date : 2026-10-16.
Destinataire : instance Claude Code en charge de l'implémentation du stream 04
(`prompts/streams/prompt-04-monitors-core.md`).
Plan concerné : `~/.claude/plans/magical-sleeping-piglet.md` → plan final à consigner dans
`prompts/plans/plan-04.md`.

## Instruction préalable — à exécuter AVANT l'implémentation

Avant toute autre action, enregistrer le **plan final mis à jour** dans `prompts/plans/plan-04.md` :
reprendre `~/.claude/plans/magical-sleeping-piglet.md` en y intégrant les amendements ci-dessous
(règle AGENTS.md:86 — enregistrement du plan avant exécution ; précédent `prompts/plans/plan-03.md`,
« GO decision integrated »). Ceci amende la Tâche 0 du plan (« copier à l'identique » devient
« consigner le plan mis à jour avec les réponses de la revue »). **Ne commencer aucune tâche
d'implémentation avant que `prompts/plans/plan-04.md` soit écrit.**

État constaté au moment de ce GO : l'instance a déjà exécuté la Tâche 0 (copie à l'identique) et les
tâches 1–4 sont en cours (`monitors/{cusum,gamma,lattice,streams}.py`, `stats/garch.py`,
`tests/test_monitors.py` écrits ; `Makefile` déjà édité). Intégrer les amendements ci-dessous dans
`prompts/plans/plan-04.md` avant la prochaine action, et impérativement avant la Tâche 11
(commit).

## Verdict

**GO, avec amendements.** Le plan est conforme au prompt 04 sur tous les points : portages
R01/R15/R09, treillis exact, flux, Γ, e-processus, configurations P1, contrôles d'identité
R01/R08 bloquants, double environnement, contrôles Monte Carlo, livrables, contraintes
numpy-only et déterminisme. Les sondes de planification sont solides : identité R01 bit-identique
en entrée D1, treillis à 9,7e-15 des 16 lignes R08, ARL₀ dense concordant avec le Monte Carlo,
ARL₀ des e-détecteurs mesurés (21,7 à γ = 20 ; 110,3 à γ = 100). Le canal de revue retenu est ce
fichier (prompt destiné à l'instance), et non l'édition directe de
`~/.claude/plans/magical-sleeping-piglet.md` : ce fichier appartient au workflow
`superpowers:executing-plans` de l'instance, la règle AGENTS.md:86 fait enregistrer le plan final
par l'instance dans `prompts/plans/`, et la trace de décision doit rester dans le dépôt
(précédent `prompts/GO-stream-03.md`, commité dans `3e3a804`).

## Amendements obligatoires

1. **Contexte périmé — réécrire la section « Contexte ».** Le stream 03 a terminé et commité
   (`3e3a804`, 2026-10-16 15:22) : le `Makefile` au HEAD a déjà `pytest -q --ignore=external`,
   `docs/DEVIATIONS.md` contient les entrées C-D3-*, `articleB.py` a la fusion du manifeste,
   `requirements.*` contient yfinance et pyyaml, `make check` est vert à 42 tests. Il n'y a plus
   de modifications non commitées du stream 03 ; l'arbre de travail est propre (hors
   `__pycache__`).
2. **Tâche 4 (Makefile) — déjà appliquée, conforme.** L'édition du working tree remplace bien
   `pyflakes jepadrift experiments tests` (cible `check`) par
   `pyflakes $(filter-out jepadrift/stats/garch.py,$(shell find jepadrift experiments tests -name '*.py'))`
   et préserve intacte la ligne `pytest -q --ignore=external`. Ne pas revenir sur ce hunk ; le
   vérifier tel quel dans `git diff --staged` au commit.
3. **Tâche 11 (clôture) — simplifier.** Le staging partiel (`git apply --cached` des seuls hunks)
   n'est plus nécessaire : aucun hunk étranger n'est non commité. Conserver « relire juste avant
   chaque Edit » comme garde. `make check` part d'un état vert (42 tests) : tout échec est à
   investiguer, pas à attribuer au stream 03. Conserver gel et signalement si un échec externe
   apparaît en cours de stream.
4. **Tâche 0 amendée** (cf. instruction préalable) : plan mis à jour avec les réponses de la
   revue, pas de copie à l'identique.

## Recommandations (non bloquantes)

5. **Marge du contrôle e-détecteurs** (Tâche 6, `test_edetector_arl0_exceeds_gamma`). Sonde :
   ARL₀ SR = 21,7 à γ = 20 et 110,3 à γ = 100 (marges ~8–10 %). Le test est déterministe
   (SeedSequence, BLAS mono-thread, PYTHONHASHSEED=42) : conserver 2 000 trajectoires et
   documenter la marge dans `docs/sections/monitors.md`. En cas d'échec lié à la plateforme,
   consigner l'écart plutôt que relancer en boucle — règle des 3 tentatives, puis gel et alerte.
6. **Taille des artefacts commités.** `results/identity/articleB_R01_R08.csv` (format long,
   cellule par cellule, 2 entrées × 2 environnements) et `logs/identity/*.log` seront commités :
   vérifier au commit qu'aucun fichier ne dépasse 50 Mo (la vérification de range de la Tâche 11
   le couvre). Aucun horodatage dans les journaux commités ; aucun chemin absolu de la machine
   hôte dans les artefacts (substitution par `~`).
7. **Hors périmètre, noté pour mémoire** : `docs/MAPPING.md` n'existe pas encore (pas requis pour
   ce stream) ; `prompts/streams/INDEX.md` décrit les 28 prompts, pas l'avancement (pas de mise à
   jour requise).

## Points du plan endossés tels quels

- Portage octet par octet par extraction `ast.get_source_segment` + test d'identité de source
  (`test_ported_sources_byte_identical`) : conforme FAIR.
- Exclusion pyflakes de `jepadrift/stats/garch.py` seul (écart `C-garch-pyflakes`) : seule façon de
  préserver l'identité octet du port (R01 l.99, `except … as e` inutilisé).
- `C-lattice-midpoint` : seuil opérationnel `(L ± ½)·unit` avec `S > threshold` en flottant, test
  dédié `test_midpoint_threshold_reproduces_lattice_rule` ; la sémantique (strict/large, seuil au
  milieu) doit figurer dans `docs/sections/monitors.md` et être utilisée par P1-C/C et le
  contrôle GARCH (Tâche 7) via `sel["threshold"]`.
- Exception `articleB_csv` au `float_precision='round_trip'` : délibérée (reproduit le lecteur
  R01 l.249), consignée `C-R01-parse`, entrée diagnostique non bloquante.
- Second environnement `external/articleB-venv` conforme à l'item 9 du prompt (pyyaml ajouté,
  documenté `C-R01-env`, aucun rôle numérique) ; le test d'identité lecteur est ignoré hors
  versions B (numpy 1.26.4 / scipy 1.16.2 / pandas 2.3.2 / statsmodels 0.14.5).
- Whitelist d'imports `test_monitors_import_numpy_only` ({numpy, math, fractions,
  jepadrift.monitors}) : conforme à la règle numpy-only de `monitors/` ; `garch.py` (scipy) reste
  hors `monitors/`, conforme au prompt (scipy autorisé hors monitors).
- Configurations P1 conformes au glossaire AGENTS.md (δ = 0.1, λ = 10 ; δ = 0.5, λ = 65·Γ̂ avec Γ̂
  réajusté une seule fois, écart B `R01-gamma-hat-refit` ; MIX 16 départs × {0.05, 0.10, 0.15} ×
  ±1, poids 1/96, H = 5000).
- e-processus en échelle log (pas de débordement sous dérive forte), entrées x ∈ [−1, 1],
  λ = 2·côté·η₀ ; `first_alarm` ; dictionnaire et mélange sous-gaussien conformes à l'item 6 du
  prompt.
- Recette de clôture conforme à AGENTS.md : wrapup `prompts/wrapups/wrapup-04.md` → reindex
  `tools/reindex_graphify_jcodemunch.sh` → `make check` → commit unique sans trailer
  (`feat(monitors): add univariate CUSUM core, exact lattice law, e-detectors and Article B
  R01/R08 identity`) → vérification du range pushé (aucun chemin sous `data/raw/eurofidai/` ou
  `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo) → `git push origin main`.
- Conventions de langue : anglais (code, docstrings, `docs/sections/monitors.md`, wrapup, commit),
  français (entrées `docs/DEVIATIONS.md`, plan).
