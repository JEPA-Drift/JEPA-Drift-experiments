# GO — Stream 13 : archivage du résultat négatif D8 d'E3

Date : 2026-10-29.
Destinataire : instance Claude Code du worktree `stream-13` (branche `stream-13`, base `c284823`).
Forme : le chercheur a autorisé l'archivage par une directive en français du 2026-10-29. L'orchestrateur Codex en a
tiré des instructions opérationnelles en anglais, seules transmises à l'instance et reproduites verbatim ci-dessous ;
ce texte n'est pas une citation verbatim du chercheur, et la directive française n'est pas reproduite ici. Ces
instructions sont ensuite transcrites en français, avec leur application par
l'instance. Ce GO amende le GO du 2026-10-28 sur la révision 4 (`prompts/GO-stream-13.md`), qui reste en vigueur pour
tout ce qu'il ne modifie pas. Il répond à l'arrêt du 2026-10-28 (`prompts/STOP-stream-13-D8.md`), conservé à
l'identique. Il est intégré au plan dans la section « Décision GO intégrée (2026-10-29, archivage du FAIL D8) » de
`prompts/plans/plan-13.md`.

## Instructions opérationnelles de l'orchestrateur Codex (verbatim), tirées de la directive du chercheur

> Researcher GO amendment for EXISTING Stream 13 only: archive the negative E3 D8 result in this worktree and make one
> local conventional commit. Before editing, explicitly reconnect graphify and jcodemunch MCP servers with safe
> connectivity calls; do not run Graphify LLM extraction or enable AI summaries. Use project .venv for all code/tests
> and native Edit/Write for manual file changes. Preserve all current uncommitted E3 code, config, tests, full CSVs and
> figures. Do not run E3, quick E3, any new draw, selective rerun, threshold tuning, tolerance change, or reinterpret
> the primary gate. Primary iid/first_order_d1_l3 at n=2000 is FAIL: mean ARL0 1994.0665 vs reference 1894, relative
> gap +0.0528334213 > 0.05, zero censored. The 20000 diagnostic and exact iid value are descriptive only. Record this
> researcher GO in prompts/GO-stream-13-archive.md in French, amend prompts/plans/plan-13.md with a Decision GO
> integrated section lifting only the stop-before-commit clause, add the observed FAIL with analysis to
> docs/DEVIATIONS.md, and write/update prompts/wrapups/wrapup-13.md in English with output paths and SHA-256.
> Preserve the original STOP file. Verify existing artifacts and run targeted tests plus make prompts-check and make
> check, but no experiment scripts. Stage explicit paths for full deliverables only; exclude quick outputs, ignored
> logs, secrets and absolute paths. Commit once, no push, fetch, merge or edit of main. If tests fail, stop with
> evidence and leave changes intact.

## Décision (transcription française)

1. **Portée.** Stream 13 existant seulement : le résultat négatif D8 d'E3 est archivé dans ce worktree par un seul
   commit local conventionnel.
2. **Résultat primaire.** La porte primaire D8 de `iid/first_order_d1_l3` sur n = 2 000 trajectoires est **FAIL** :
   ARL₀ moyen 1 994,0665 contre la référence 1 894, écart relatif +0,0528334213 > 0,05, aucune trajectoire censurée.
   Le diagnostic à 20 000 trajectoires et la valeur i.i.d. exacte sont seulement descriptifs.
3. **Interdits.** Aucun run d'E3, complet ou `--quick` ; aucun nouveau tirage ; aucun rerun sélectif ; aucun réglage
   de seuil ; aucun changement de tolérance ; aucune réinterprétation de la porte primaire ; aucun script
   d'expérience.
4. **Préservation.** Le code, la configuration, les tests, les CSV complets et les figures d'E3 non commités sont
   conservés, ainsi que le fichier STOP original.
5. **Documents.** Ce GO en français ; une section « Décision GO intégrée » dans `prompts/plans/plan-13.md`, qui lève
   la seule clause d'arrêt avant commit ; le FAIL observé et son analyse dans `docs/DEVIATIONS.md` ;
   `prompts/wrapups/wrapup-13.md` en anglais, avec les chemins et les SHA-256 des sorties.
6. **Outillage.** Avant toute écriture, reconnexion explicite de graphify et de jcodemunch par des appels de contrôle
   sûrs ; ni extraction LLM de Graphify ni activation des résumés IA. `.venv` pour tout code et tout test ;
   modifications manuelles par les outils natifs Edit et Write.
7. **Vérification.** Contrôle des artefacts existants, tests ciblés, `make prompts-check` et `make check`. Si un test
   échoue : arrêt avec les preuves, modifications laissées en place.
8. **Git.** Indexation chemin par chemin des seuls livrables complets ; exclusion des sorties quick, des journaux
   ignorés, des secrets et des chemins absolus. Un seul commit ; ni push, ni fetch, ni fusion, ni modification de
   `main`.

## Application par l'instance

- **MCP**, avant la première écriture : graphify `graph_stats` (3 506 nœuds, 4 218 arêtes, 282 communautés) et
  jcodemunch `menu` (catalogue de 91 actions, aucune action exécutée). Aucune extraction Graphify n'est lancée ; la
  configuration de jCodeMunch garde `"use_ai_summaries": false` (lue, non modifiée).
- **Artefacts**, vérifiés avant écriture par `sha256sum -c` : les six sorties de `results/e3/` contre
  `logs/e3/run.log` (dont `e3_overshoot.csv`, `1ca7c3ae…`, cité par le STOP), les six de `results/e3_quick/` contre
  `logs/e3_quick/run.log`, `configs/e3.yaml` (`6e385738…`) et les deux `ret_wide.npy` d'entrée. Les valeurs D8 de ce
  GO sont relues par assertion dans `results/e3/e3_overshoot.csv`.
- **Livrables commités** : code, configuration et tests d'E3, `jepadrift/stats/intervals.py` et
  `experiments/e10_robustness.py` (déplacement de `wilson`), `results/e3/`, `figures/e3/`, `docs/DEVIATIONS.md`, le
  plan, les deux fichiers GO, le STOP (inchangé, comme trace de décision) et le wrapup.
- **Non commités** : `logs/e3/run.log`, journal ignoré (le `git add -f` prévu aux §11 et §12.8 du plan ne s'applique
  plus ; son SHA-256 figure dans le wrapup) ; `results/e3_quick/`, `figures/e3_quick/` et `logs/e3_quick/`, conservés
  sur disque sans suppression.
- **Commit** : `feat(e3): archive H0 calibration with failed D8 gate (stream 13)`, sans trailer.
