# Projet de décision T7_RUNTIME_GO — qualification Stream 32 Student-t7

22 novembre 2026 · `DRAFT_ONLY` · `NO_RUNTIME_GO` · `NO_T7_PILOT_GO` · `NO_T7_FULL_GO`

La demande porte sur le seul stage `qualification` en mode natif `smoke`, dans le worktree `JEPA-stream-32-Student-T7`. Le design reprend N = 32 et 239 au fit 0, les deux univers, cinq familles, H = 250 et les politiques T7. Les effectifs `DEV_LIB/DEV_NULL/DEV_ALT/CAL_NULL/HOLD_NULL/ALT` sont `8/39/4/39/60/6`. L’enveloppe proposée fixe un plafond de 8 Gio agrégés, 2 heures CPU cumulées, 900 s au mur par invocation et `jobs_max=2`. Le cgroup est limité à un CPU logique. Cette enveloppe sert à qualifier la fonctionnalité et les ressources de la fixture. Les effectifs du Pilote et du Full restent ceux de leurs propres projets. [YAML de qualification](../configs/pca_info_online_t7_qualification.yaml)

| Identité | SHA-256 |
| --- | --- |
| `design_id` | `a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804` |
| `seed_plan_sha256` | `5bdb1b70b5253c1e16eb14017621e2ff4ae327b00142072bc22c8edb450994e7` |
| `approval_sha256` | `20f2f6696214bf44cbb37f78739d9f73d7e8114caa0a6376666c3605dd35289e` |

## Séquence à soumettre au chercheur

1. Sous réserve du GO écrit, vérifier l’empreinte d’intention, les SHA des outils et YAML, le descripteur, le verrou et l’admission cgroup. Exécuter `continuous` à `jobs=1`. Archiver les reçus, les digests des phases et l’inventaire des cinq CSV. Retenir la réserve CPU cumulée dans le même ledger pour les cas suivants.
2. Exécuter `resumed` à `jobs=1` jusqu’à l’arrêt propre après CAL. Constater `CLEAN_BLOCKED_RESOURCE`, le cgroup drainé, la mesure CPU et le préfixe validé. L’autorité de reprise écrite lie le dernier jeton, le reçu, le SHA d’intention, l’inventaire commité et le débit déjà inscrit.
3. Reprendre `resumed` à `jobs=2`. Pour le témoin d’arrêt forcé, interrompre l’invocation autorisée après constat d’un checkpoint stable. Vérifier le drainage effectif, la réservation convertie en débit conservateur et le blocage de toute reprise tant que la réconciliation écrite manque. Si la preuve du préfixe permet la reprise, reprendre le même cas à `jobs=2` et vérifier ses SHA jusqu’à CAL. Comparer le `realization_id`, les cinq CSV et les artefacts scientifiques avec `continuous`. Les reçus d’invocation conservent leur télémétrie propre.
4. Exécuter les deux passes de l’auditeur sur les publications de qualification, en capturant le SHA pré-ALT dans le reçu avant l’ouverture des entrées ALT par l’auditeur. Rapporter le pic mémoire, les événements OOM, le CPU mesuré et débité, le temps jusqu’au drainage, la durée par partition et le coût de reprise. Borner l’extrapolation au Pilote à partir des effectifs observés. Les maxima et résumés ALT servent aux témoins de fonctionnalité, sans analyse de puissance.

Les cas ont des répertoires distincts sous `logs/stream-32-t7/qualification/a565c473535afc70/cases/`. Le ledger cumulatif et les reçus restent sous la racine commune de ce design. Le chemin d’exécution reste gouverné par un GO positif propre au runtime, l’intention complétée, le YAML autorisé, puis les autorisations distinctes de reprise ou de réconciliation. En A2, le YAML scientifique contient `authorization: null` et les références de l’intention restent incomplètes. [Intention préparatoire](DRAFT-stream-32-t7-runtime-intent-20261122.json) · [Décision A2](GO-stream-32-t7-tech-20261122.md)

Le préflight vérifie notamment `stage`, `design_id`, `seed_plan_sha256` et `approval_sha256` contre la décision écrite. Après cette décision, les deux SHA encore nuls seront calculés sur le GO et sur le YAML autorisé. Leur ajout conserve l’empreinte d’approbation. Le même `design_id` vaut pour `--case continuous --jobs 1`, `--case resumed --jobs 1` et `--case resumed --jobs 2 --resume --resume-authority <autorité>`. L’autorité de reprise lie explicitement `case: resumed`.
