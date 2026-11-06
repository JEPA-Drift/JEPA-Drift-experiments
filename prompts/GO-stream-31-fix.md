# GO stream 31 — correctif D7b et figures full

Date : 2026-11-06, 15:32 UTC. Décision Codex dans le mandat d'orchestration délégué par le chercheur.

## Autorité et décision

**GO d'exécution du plan séparé `prompts/plans/plan-31-fix.md`, avec les arbitrages de son §8.** Ce GO lève le STOP D7b uniquement pour le correctif d'étiquette et les deux remplacements full explicitement autorisés. Le GO QA antérieur reste historique.

Autorités du chercheur, lues intégralement et archivées sans modification dans les journaux ignorés :
- `FIX-stream-31-nb-assets.md` : SHA-256 `ce91c1899db2fac30dcb88e64f3b1043861263adb7c2988d5394a706b84735e6` ;
- `31_FIX_STREAM_PCA_DRIFT_CONTRACTS.md` : SHA-256 `fbfccc96fc777b6fef600ae9b16239ba46a852b68444ec3b717ac1d0a8e36c4c`.

Plan natif Claude Opus relu : SHA-256 `10beef540aa3ac4b2810c5751dddd71e2c6d80342d7a21451ccef0a8fcd02451`. Plan enregistré et GO écrit avant tout changement du traceur.

## Périmètre

Claude Code Opus 5.5 interactif, effort max, même session, sans sous-agent, dans le worktree `stream-31`, base `20ad9e860a58373ec85405de6ee19a68322dd02e`.

- Deux lignes du seul `experiments/figures/plot_figure_1.py` (§3.1 du plan) : passage de `config.n_null` dans `meta`, puis interpolation dans le libellé FPR. La transmission est nécessaire ; la formulation « une seule ligne si possible » ne justifie aucun contournement.
- Extension minimale de D7b dans `tests/test_pca_drift_contracts.py`, sans réduire ses assertions full : preuve mémoire full 2000, smoke 40 et sonde factice 39 ; 44 tests conservés.
- Rendu neuf complet `--figure both --strict` sous les journaux ignorés, vérification, sauvegarde contrôlée, puis installation identique dans :
  - `results/pca_drift_benchmark/figures/full_2000_20261101` ;
  - `results/pca_drift_benchmark/figures/full_2000_20261101_fix_smoke_no_claims`.
- Rapport `docs/audits/PCA_CONTRACTS_VALIDATION.md` : nouvelle mesure, statut courant, SHA avant/après ; mesure historique 43/1 et journaux préservés. Le wrapup 31 sera rafraîchi sur demande Codex.

Plan, GO, Git, intégration et réindexation appartiennent à Codex.

## Vérifications et arrêts

Exécuter S0–S9 et les précisions du §8. RED attendu : le seul défaut connu D7b ; GREEN : D7b, cinq contrats D, tests du traceur, puis 44 contrats avec G1 et `make check` complet. Enregistrer les commandes, codes de sortie et SHA, sans sélection pytest vacante.

Environnement : `export PATH="$PWD/.venv/bin:$PATH" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`. Python et make du venv. `PCA_FULL2000_TRIALS=../JEPA-full-2000/results/pca_drift_benchmark/full_2000_20261101/trials.csv` pour la QA globale et les hooks ; lecture en place, aucun lien ni copie.

Aucun benchmark ou assemblage relancé, aucune nouvelle expérience, donnée financière réelle, JEPA, VAE ou J4. Runner, assembleur, tables, smoke, autres résultats, dépendances, `PLAN.md`, `prompts/streams/` et `docs/DEVIATIONS.md` restent scellés. Les six CSV sources full restent identiques ; la provenance nouvelle doit être complète et les trois formats cohérents.

J1 disque/index : `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, 47 CRLF. D8 reste FAIL +5,2833 %, SHA `1ca7c3aea355e42910c828b8fa1b7f40acf9846d99953a5e93136e457e4d68b3`.

**Nouveau défaut hors périmètre : STOP immédiat, rapport sans rerun ni affaiblissement de contrat.** Au plus trois corrections tracées pour une erreur propre au test QA, sans modification scientifique.
