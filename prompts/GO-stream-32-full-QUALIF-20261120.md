# STREAM 32 — FINALISATION DE LA QUALIFICATION AVANT FULL_GO

Le `FULL_GO_ACCORDE` précédemment transmis est confirmé comme **décision scientifique de principe** concernant le Full gaussien, mais **il ne dispense d'aucune porte technique du protocole**.

Tu as correctement maintenu le Full à l'arrêt en l'absence du verdict `READY_FOR_RESEARCHER_FULL_GO`.

## 1. Mission immédiate

**Je t'autorise à finaliser la Phase 1 de qualification technique, et uniquement cette phase.**

Tu dois maintenant exécuter les vérifications manquantes, localiser les preuves existantes ou produire les livrables non encore réalisés.

Ne reviens pas vers moi pour une nouvelle autorisation de qualification : elle est accordée par le présent message.

En revanche, **aucune exécution scientifique `--mode full` n'est encore autorisée**.

Travaille dans le worktree de la branche `stream-32-pca-info-online-20261114`.

Conserve le verrou global partagé et les règles d'isolation du dépôt.

## 2. Design et ressources intangibles

`full_design_id = 8a4af3ecd7864f167ac32b82f0751547dc68b8a4bf24cec0f6c7fefbb19895d4`

`seed_plan_sha256 = 88e7c755bb33cd48c57bab000959cac09f4efb9211545951e4fc89469979c450`

Enveloppe :

- 10 CPU-heures cumulées.
- 32 Gio agrégés.
- 2 700 secondes par invocation.
- `jobs_max = 8`.
- Lancement initial prévu avec `--jobs 1`.

Conserver strictement R3-A, R4 (Tango asymptotique) et R5 (`FIT_CONDITIONAL`, fit 0).

Aucune modification de `experiments/pca_info_online.py`, du YAML scientifique gelé, des graines ou des hypothèses H1–H3 n'est autorisée.

## 3. Retrouver ou produire les trois livrables

### A. Rapport de qualification technique

Recherche d'abord les rapports et journaux de la Phase 1 du Prompt Codex de qualification finale.

S'ils existent, vérifie leurs preuves effectives. Ne déduis pas un PASS de la seule présence d'un fichier.

S'ils n'existent pas, exécute les témoins manquants sous les contraintes de sécurité du stream 32.

La réception doit couvrir :

- `T-LEDGER-DURABILITY`.
- `T-CPU`, incluant les processus enfants.
- `T-WALL-CAP`, incluant le délai de grâce.
- `T-SCOPE-LOCK`.
- `T-SUPERVISOR-CRASH`.
- `Q-B` ou `MANUAL_FALLBACK_VERIFIED`.
- `Q-C1` : arrêt applicatif propre et reprise.
- `Q-C2` et `T-2700-BOUNDARY` : interruption forcée, conservation des partitions et réconciliation.
- `T-AUDIT-PRIMITIVE`.

Aucun test ne doit être déclaré PASS sans témoin exécuté et vérifié.

### B. Superviseur Full gaussien

Localise ou implémente, selon les besoins :

`logs/stream-32/run-full-supervisor.sh`

`logs/stream-32/check-full-status.sh`

Le superviseur doit garantir :

1. L'acquisition du verrou partagé sans héritage involontaire.
2. La journalisation durable `RUNNING` avant lancement.
3. L'écriture atomique correcte : `fsync(fichier temporaire)`, puis `os.replace`, puis `fsync(répertoire)`.
4. Le contrôle du CPU cumulé, y compris celui des processus enfants.
5. Le plafonnement effectif du temps mur et des ressources.
6. La vérification de l'arrêt complet du scope.
7. Le blocage en cas de consommation CPU inconnue ou d'interruption non réconciliée.
8. L'absence de double lancement et la reprise sans recalcul des partitions validées.

Ne considère pas `--jobs 1` comme une preuve suffisante que le CPU total est inférieur au temps mur.

Privilégie le repli manuel qualifié si le réveil automatique Codex n'est pas fiable.

### C. Audit scientifique indépendant

Localise ou implémente :

`logs/stream-32/audit-full-gaussian.py`

Ce script doit recalculer les statistiques depuis les entrées primitives, sans importer les fonctions décisionnelles du runner principal.

Modes requis :

- `--pre-alt`
- `--alt`

Valide-le sur les données primitives du Pilote gaussien et sur le témoin synthétique de qualification.

Vérifie rangs CAL, Clopper–Pearson, Tango, RMST, bootstrap, HEAD et décisions H1–H3.

Fige son SHA-256 dans :

`logs/stream-32/continuation.md`

Ce gel doit précéder toute exécution Full.

## 4. Orchestration

Tu es responsable de la qualification et de la contre-revue.

Délègue les scripts techniques à GLM-5.3 Max si nécessaire, en conservant une revue Codex à effort `xhigh` pour les invariants de sécurité et les calculs statistiques.

Évite les cycles de discussion supplémentaires avec Gemini.

Les tests doivent utiliser uniquement des commandes neutres, témoins synthétiques ou stagings jetables. Ne déclenche aucune trajectoire du Full gaussien scientifique.

## 5. Réception et arrêt

Après les vérifications, produis un rapport contenant :

- Tableau des témoins `PASS / FAIL / NOT_RUN`.
- Chemins exacts des journaux et preuves.
- SHA-256 du superviseur et de l'auditeur indépendant.
- Résultat des tests d'interruption et de reprise.
- Vérification des empreintes scientifiques gelées.
- État du verrou et des processus résiduels.
- État de l'autorisation et du registre CPU.
- Éventuels défauts ou limitations restant ouverts.

Si tous les critères sont satisfaits, émets explicitement :

`READY_FOR_RESEARCHER_FULL_GO`

Sinon :

`BLOCKED`, avec le défaut précis et la correction nécessaire.

**ARRÊT OBLIGATOIRE à cette réception.**

Ne modifie pas encore le fichier GO signé, ne renseigne pas `authorization`, ne lance pas `--mode full`, ne lance pas T7 et n'effectue aucun commit, push ou wrap-up.

Une fois ton verdict `READY_FOR_RESEARCHER_FULL_GO` reçu, je confirmerai immédiatement l'autorisation définitive de lancement pour le design et l'enveloppe gelés.

**[Strategic Advice]** Termine les preuves techniques manquantes sans rouvrir R3–R5 ni réexécuter les qualifications déjà valides. L'objectif est de passer directement du verdict READY au lancement effectif du Full.
