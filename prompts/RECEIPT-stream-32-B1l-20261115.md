# Stream 32 — réception B1l, journal CPU et garde de budget sur instantané

Date : 15 novembre 2026. Décision Codex : **B1l REÇU, COMPOSANT COMPTABLE LIMITÉ**.
Autorité : GO B-TDD et réception B1k ; aucun GO runtime ou scientifique.
T46/T62, B1 et B restent ouverts jusqu'au câblage complet de leurs obligations.

Reçu : charge_cpu(staging,token,cpu_seconds), journal canonique par invocation à checkpoints
monotones ; require_budget(staging,authority,plan,started), bornes inclusives CPU/mur, statut
BLOCKED_RESOURCE atomique sur progression vérifiée. Les valeurs CPU sont fournies par l'appelant,
et le journal est une borne inférieure tant que la mesure et le cycle de vie ne sont pas raccordés.
Les aides pures de validation/progression sont partagées avec finalize_planned sans changer son API.

| Observation | Décision | Justification / tests |
|---|---|---|
| Cumul par invocation | ACCEPTED | Même token remplace par une valeur non décroissante, jamais ajouté deux fois ; nouveau token ajouté, fsum fini, baisse refusée sans écriture. |
| Journal et frontière I/O | ACCEPTED | resources.json régulier, non symbolique et borné avant lecture ; UTF-8/JSON strict, octets canoniques, DID complet, valeurs et total finis/non négatifs. Pas de remise à zéro d'un journal manquant avec travail ou incohérent. |
| CPU et mur | ACCEPTED | Bornes inclusives au plafond et à l'échéance, contrôle juste en dessous ; aucun calcul scientifique ou mesure réelle dans les fixtures. |
| État et reprise | ACCEPTED | BLOCKED_RESOURCE véridique, caches conservés ; reprise avec nouveau délai mural conserve600s puis ajoute30s, termine la fixture sous même design/GO. |
| Réemploi B1k | MODIFIED | Extraction de _validated_plan/_planned_progress au second consommateur ; anciennes gardes/refus, y compris sortie symbolique avant contenu, conservés et tests B1k toujours passants. |
| Capture après quota | MODIFIED | Premier GREEN rejeté exit1/is_error=true sans patch ; reprise unique21:01UTC, même session/mission/empreintes, capture complète acceptée. Aucun minuteur actif restant. |
| Contre-revue indépendante | ACCEPTED | Relecteur distinct de l'auteur et du superviseur : aucun défaut matériel dans le composant comptable borné ; aucun test ou fichier modifié par le relecteur. Vérifications exécutées séparément par Codex. |
| Enforcement global | REJECTED | Pas d'opération gardée exposée, pas de mesure réelle SELF+CHILDREN ni couverture du CPU interrompu/hors checkpoints. Ces raccordements restent bloquants ; aucun plafond réel4CPUh ou blocage de vrais callbacks revendiqué. |
| Clôture T46/T62/B1/B | REJECTED | Worker/jobs/driver/CLI, limites externes et mémoire agrégée, énumération scientifique, LOCAL_HASHED_ONLY, bundle/T16 global, cohortes/graines/intégration A/T68 restent dus. |

Preuves sous .venv/environnement déterministe/verrou : RED **9failed219passed en8.74s**,
puis GREEN après reset **228passed en7.58s**, pytest/contrôles exit0, pyflakes/diff-check propres.
Tests228cas/156702octets inchangés pendant GREEN ; préfixe219cas conservé, aucun affaiblissement.

| Pièce | SHA-256 |
|---|---|
| Source finale | `31d4b1f964e9c4ac2e58519464d28c6dd350aa4e0a40e63b2cd102840c4eaa07` |
| Tests figés | `9abd8d115a25a00db52c6d2dbf2ed826a9b05a0444d54ff3e11687f04c90095b` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture après reset complète | `db869daa097240fc58379f370db7eab76539ff74f10de947eba2ac21e45013b4` |
| Journal pytest GREEN | `9426a7159b6717b5fc942a1b8639505b3fb387b6d9fb7c54dbabe136823d89aa` |
| Journal contrôles GREEN | `19a5308b60fcb0f79fef667b93e661ab4afb3a47ebaabbd92ba58a83ebfe6c3d` |

Revue : REVIEW-stream-32-B1l-red-20261115.md ; scripts/preuves check-B1l-*.sh et lot-B1l-*.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; succès du composant non promu en contrat complet.
Suite bornée : tests RED de mesure CPU et opération de partition gardée, API minimale soumise
à revue avant production, horloges/compteurs de fixture seulement. Pas de workers ou campagne.
Réserves bloquantes conservées : CPU avant crash/hors checkpoints et borne externe, vraies jointures,
câblage avant engagement/finalisation, consommation scientifique des graines et calendrier complet.
require_budget n'a pas de chemin de sortie ; ordre d'appel avant publication et conservation d'un
statut consultatif après FINAL relèvent encore du driver. Statuts préexistants corrompus/symboliques,
composants de chemins symboliques et TOCTOU non couverts ; callback d'export de confiance.
LotC/runtime/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl, changement de dépendance ou réglage scientifique.
