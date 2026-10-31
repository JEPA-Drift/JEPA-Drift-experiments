# Stream 29 — GO d'exécution Vibe, priorité présentation de lundi

Décision directe du chercheur du 2026-10-31 : suspendre le stream 31 jusqu'à nouvel ordre ; implémenter le stream 29 jusqu'à résultats audités, puis seulement le stream 30, avec **Mistral Vibe `large-4` (`mistral-large-4`), thinking `high`**.

**GO d'exécution pour le 29 maintenant**, sur `prompts/plans/plan-29.md`, avec les précisions de `prompts/GO-stream-29.md`. Cette décision postérieure remplace, pour cette exécution Vibe uniquement, les anciennes mentions « plans seulement » et « sans GO d'exécution ». Les propositions et décisions antérieures restent l'historique de la revue.

- Un seul implémenteur actif, dans le worktree `stream-29`, base `fc533d003098a45c8ce533876642712d47038b31`. Aucun stream 30 avant audit, clôture et intégration du 29 ; aucun stream 31 avant nouvel ordre.
- Périmètre et sorties : assembleur de tableaux, tests propres, documentation du contrat, déviation motivée en ajout, neuf sorties prévues et wrapup anglais. Référence d'entrée unique : `results/pca_drift_benchmark/smoke_predictive_v2_closeout/`, schéma /2 scellé, fingerprint `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.
- Il s'agit de résultats issus du smoke existant (N=239, H=250, 40 trajectoires par rôle), à présenter avec leur statut. Aucun nouveau run scientifique full, recalibration, simulation d'observations, réajustement PCA ou rendement réel post-2019 n'est autorisé. Aucune donnée EUROFIDAI ne sera lue.
- Le runner, sa configuration, son contrat /2 et ses sept fichiers d'entrée restent inchangés. L'import de ses aides en lecture seule est l'écart H2 approuvé, pas une autorisation de déplacement/refactorisation.
- Les trois grandeurs taux empirique de calibration / borne prédictive / FPR holdout restent distinctes. Les lignes réelles bloquées et leurs NA restent présentes, les informations covariance ne deviennent pas additives et le coût covariance demeure un substitut exploratoire.
- Les résultats de préfixe et les métriques réutilisées proviennent des mêmes enregistrements immuables ; aucune recomputation des RMST/FPR. Vérification stricte, lignée par cellule, double rendu dans des répertoires neufs, comparaison des neuf fichiers et mesures de coût.
- Environnement partagé `.venv`, variables déterministes fixées avant NumPy, dépendances inchangées. E2 disque/index CRLF et SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; historique E3/D8 FAIL conservé.
- Vibe ne modifie aucun fichier de plan/GO/politique ni fichier d'un autre stream. Aucun sous-agent ou worker parallèle, aucun Git add/commit/fetch/push/merge/rebase/stash/reset/checkout, aucune réindexation ni make check global. Codex conduit revue indépendante, vérifications globales, clôture et Git unitairement après extinction du processus.

Prompt opérationnel : `prompts/IMPLEMENT-stream-29-vibe.md`. Le garde Claude plan-only reste actif ; il ne bloque pas cette autorisation Vibe spécifique.

## Audit 1 — correction ciblée autorisée

Le premier candidat n'est pas accepté malgré 45 tests verts. Les défauts et preuves sont `docs/audits/stream-29-implementation-review.md`. La correction dans le périmètre du plan est autorisée à Vibe large-4/high via `prompts/REPAIR-stream-29-vibe-audit1.md`. Aucun nouveau plan, changement de science, benchmark ou autre stream n'est demandé à cet implémenteur. Les archives du candidat sont conservées ; l'intégration et le full restent bloqués jusqu'à re-revue satisfaisante.

## Re-revue — trois écarts restants

Le candidat audit-fix1 compte 75 tests verts, mais trois écarts restent ouverts dans `docs/audits/stream-29-implementation-rereview.md`. La correction ciblée est autorisée via `prompts/REPAIR-stream-29-vibe-audit2.md`, même moteur large-4/high et même périmètre. Aucune nouvelle science ni modification du producteur ; la clôture attend leur résolution effective.
