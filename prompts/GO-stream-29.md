# Stream 29 — GO du plan v2, sans GO d'exécution

Proposition Claude examinée : 434 lignes, SHA-256 `6ec97fca7d5f69c29576cc2822ec45eaa434af14dde2af7a6d838e17f02750ed`. Historique : `prompts/NO-GO-stream-29.md` et plan v1 archivé sans modification ; la présente décision remplace le NO-GO pour la version v2.

GO du **plan v2 uniquement**, décidé par Codex le 2026-10-30 dans le cadre de l'audit délégué. Les objections R1 à R5 du NO-GO v1 sont levées. Les défauts H1 à H15 sont retenus avec les précisions de domaine ci-dessous, qui priment sur les formulations générales du plan.

1. **Champs applicables et états.** La finitude s'exige pour les mesures pertinentes au `metric_kind` et à leur effectif ; FPR dans un ALT_RMST et RMST dans un HOLDOUT restent NA, comme les intervalles non définis par le producteur. Les valeurs théoriques ne sont pas des mesures exécutées. La cascade CALIBRATION_FAILED vers ALT/HOLDOUT du §3.6 concerne les mesures synthétiques ; une calibration D6 réelle échouée ne transforme pas les lignes réelles bloquées en évaluations exécutées, ni ne remplace leur statut fourni par le runner. Les tests positifs g1/g4 couvriront ces domaines sans compléter une valeur manquante.
2. **Séparation des cohortes.** Le contrôle de disjonction concerne les identifiants de sélection, de métrique, de split et de calibration effectivement renseignés. `calibration_hash`, `basis_hash` et `config_hash` sont des empreintes de contenu : leur égalité éventuelle n'est pas en elle-même un partage de cohorte. Ne pas imposer leur inégalité ni modifier des empreintes pour la produire ; conserver la provenance exacte et vérifier les liens de cohorte par leurs identifiants.

**Rôles et portée.** Claude Code rédige les plans en max/xhigh ; Codex audite et conduit la clôture/intégration ; Mistral Vibe `large-4`, thinking `high`, est l'implémenteur désigné. L'étape actuelle reste **plans seulement** : ce GO n'est pas un GO d'exécution Vibe. L'ordre de planification reste 29 → 30 → 31, audits unitaires.

Le runner et les artefacts /2 restent inchangés ; aucune révision /3, simulation, recalibration, exécution full ou évaluation réelle post-2019 n'est autorisée par cette décision. Aucun résultat du futur assembleur de tableaux n'a encore été exécuté ou contrôlé.

Vérifications Codex bornées sur les artefacts existants : hashes des six CSV, en-têtes /2, clés primaires par fichier, compteurs de références, correspondances des effectifs essais/agrégats/calibrations, H = 250, identité producteur courante, E2 disque/index CRLF/SHA-256 et statut historique E3/D8. Aucune simulation ni test du futur script n'a été lancé.

Plan canonique : `prompts/plans/plan-29.md`, proposition Claude conservée textuellement puis section « Décision GO intégrée ». Les décisions et précisions ci-dessus sont intégrées à cette section.

## Autorisation d'exécution postérieure — 2026-10-31

Le chercheur a maintenant autorisé **l'implémentation Vibe large-4/high du 29 jusqu'à résultats audités, puis le 30 séquentiellement**. Le stream 31 est en standby jusqu'à nouvel ordre. L'autorisation opérationnelle et ses limites sont `prompts/GO-stream-29-vibe.md` ; elle remplace pour Vibe les mentions plan-only historiques ci-dessus, sans modifier les choix scientifiques ni autoriser de full ou d'évaluation réelle post-2019.
