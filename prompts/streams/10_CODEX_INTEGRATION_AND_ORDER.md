# CODEX — Plan d'intégration des directives, mapping de fichiers et contrôle de conflits

**Mode d'emploi autonome.** Ce dossier constitue un paquet de **textes d'injection**. Il n'est pas lui-même un commit et ne donne pas accès au serveur. Après transfert dans une zone de travail du serveur, Codex inspecte la copie locale canonique et fait valider les plans/GO avant modification. La section 3.6 du handover datée 23/10 prévaut sur toutes les autres versions historiques.

## Ordre documentaire et destination

| Fichier du paquet | Usage | Cible recommandée après GO |
|---|---|---|
| `00_CODEX_AMORCAGE_2026_10_24.md` | **premier prompt** à injecter à Codex ; audit non destructeur avant toute action | `prompts/orchestration/codex-amorcage-2026-10-24.md` |
| `01_STREAM_14_REWRITE_BOTTLENECK.md` | remplacement du prompt 14 après revue scientifique du plan 14 courant | `prompts/streams/prompt-14-ca-tjepa.md` |
| `02_STREAM_12_E1_J2_ADDENDUM.md` | addendum à intégrer au prompt 12 ; préserver son GO historique et terminer son plan | append contractuel dans `prompts/streams/prompt-12-e1.md` après intégration GO |
| `03_STREAM_13_E3_J2_ADDENDUM.md` | addendum à intégrer au prompt 13 ; préserver d'abord code/plan non commités | append contractuel dans `prompts/streams/prompt-13-e3.md` après revue GO |
| `04_STREAM_16_J3_PRETRAIN_ADDENDUM.md` | addendum entraînement et attribution | append contractuel dans `prompts/streams/prompt-16-pretrain-rankme.md` |
| `05_STREAM_17_18_BASELINES_ADDENDUM.md` | note commune ; scinder en addenda ciblés sans écraser 17 ou 18 | `prompts/orchestration/validation-baselines-17-18.md` **et** référence dans les prompts 17/18 |
| `06_STREAM_21_FREEZE_PROTOCOL_ADDENDUM.md` | addendum au freeze et à la sélection pré-J4 | append contractuel dans `prompts/streams/prompt-21-freeze-runner.md` |
| `07_STREAM_22_E5_J4_REWRITE.md` | remplacement du prompt 22 avant son plan/GO final | `prompts/streams/prompt-22-e5.md` |
| `08_STREAM_23_26_SECOND_ORDER_ABSORPTION.md` | note commune, à lire dans GO 23 phase 2 et 26 | `prompts/orchestration/validation-second-order-23-26.md` **et** référence dans prompts 23/26 |
| `09_THEORY_MANUSCRIPT_REVIEW.md` | mission théorique de papier, sans créer de stream numéroté sans GO | `prompts/orchestration/theory-revision-2026-10-24.md` |
| `10_CODEX_INTEGRATION_AND_ORDER.md` | procédure d'adoption et règles de priorité | `prompts/orchestration/directive-index-2026-10-24.md` |

**Obligation de synchronisation** : le validateur `tools/check_prompts.py` du stream 8b exige que chaque prompt de `prompts/streams/` soit une sous-chaîne exacte du master `prompts/Prompts_Claude_Code_v5.md`. Après toute modification canonique, relancer son mode `--sync-master` **en lecture du comportement et du `--help` local**, puis `make prompts-check` ; ne pas modifier manuellement le master dans un autre worktree. L'INDEX historique indique 29/29 ; une cible remaniée doit conserver ce contrat ou le faire évoluer par GO préalable explicite.

**Règle de collision** : le texte complet du remplacement 14/22 prend le pas sur la partie correspondante de leur ancien prompt après GO, mais les bonnes règles environnement / TDD / provenance de l'ancien prompt sont réconciliées, jamais jetées sans inventaire. Les addenda 12/13/16/21 sont des priorités supplémentaires : en cas de conflit avec un plan déjà approuvé et une implémentation en cours, Codex documente le delta, fait un nouveau GO et conserve le diff original. Ne jamais utiliser `git reset --hard`, `stash` ou `checkout` pour « appliquer le paquet » à la place de la revue.

## Séquence d'exécution dépendance-vérifiée

1. **Audit :** vérification HEAD local, `git status` par worktree, présence des prompts/GO/plans, état .venv/Torch et statut quota explicitement notifié. Examiner la contradiction des offsets D3 et résoudre par dates/manifeste avant toute jointure. Aucun commit ou push à ce stade.
2. **Préparation des prompts :** appliquer les textes et synchroniser le master sous un seul responsable de fichiers partagés ; publier une revue GO des modifications. Un fichier non commité dans 13, 17 ou 23 ne doit pas être remplacé par une version distante.
3. **J2 :** achever streams 12 et 13, tableaux des portes (i)-(iv), tests de FPR/ARL distincts. En parallèle possible : socle C de 17 ; staging torch de 14 s'il ne modifie pas les fichiers partagés. Pas de nouveaux tests `monitor` pour aider le modèle.
4. **J3 :** finir 17 ; intégrer 14 natif sans ACP principal, avec anti-fuite ; finir 16 (prétrain+RankMe). Baseline 18 seulement si réellement disponible et licence vérifiée. 19 prépare lois en N ; 23/P4-D dépend de 17.
5. **J4 :** achever 21 et figer entrée/estimandes/comparateurs, puis 22 E5 + 23/P5-D lorsque les dépendances sont valides. Lecture test seule après freeze. Verdict PASS/FAIL/INDETERMINATE dans un fichier immuable ; contingent titre B si absence de victoire établie. 20/25/26 et domaines externes ensuite.
6. **Théorie :** corriger les preuves parallèlement sans modifier à posteriori les critères confirmatoires. Étendre éventuellement les annexes mathématiques du papier, mais ne pas forcer `d*` ni annoncer gain de KL.

## Garde de publication et intégration

- Versionnez les nouveaux prompts et leurs nouvelles approbations sans écrire d'identifiants de chercheur sur des commits anonymisés si la politique de soumission l'interdit. Aucun push si le dépôt public est désormais lié à la publication ou sans autorisation de la politique existante. Les données EUROFIDAI sont exclues de tout commit/journal/push.
- Chaque agent possède un worktree dédié ; la fusion peut suivre le protocole `INDEX.md` actuel seulement après `make check`, revue des tests, statut propre et constat de non-régression J1. Ne pas rebaser mécaniquement le `main` local sur l'ancien `origin/main` (le handover le décrit comme en retard).
- Capturer avant/après modification des prompts : hash des fichiers, diff source, plan/GO, décision de dépendances, `make prompts-check`. Pour Torch enregistrer l'état parent, check PyTorch via `.venv/bin/python`, empreintes du CSV et test d'encodage CRLF natif.

## Contrôle de complétude avant transmission à un agent

Vérifier pour chaque prompt canonique de stream la présence de sept sections `Contexte`, `Tâche`, `Entrées`, `Livrables`, `Contraintes techniques`, `Critères de succès`, `Commandes de vérification`. Confirmer qu'aucun placeholder de prompt n'est interprété comme une mesure : les variables de chemins de worktrees restent à **résoudre automatiquement par Codex** depuis `git worktree list` avant commande. Les commandes de reproduction doivent ensuite être copiées avec leurs paramètres *réels* dans le plan et le wrapup (pas de valeur « exemple » exécutée comme preuve).

Contrôler la présence de tous les prérequis, sinon noter `BLOCKED` et stopper uniquement le stream dépendant. Un résultat négatif scientifique conforme au protocole est une livraison valide ; une réussite obtenue après changement de test ou de baselines ne l'est pas.

## Format de première réponse obligatoire de Codex

Fournir en français un audit de prise de fonction : `HEAD`, branches/worktrees propres ou non, statut/quota, torch et hash J1 de référence, conflits d'interface 14↔17, tâches reprenables sans intrusion, gates J2/J3/J4 avec leurs dépendances et la liste des GO requis. Distinguer « vérifié maintenant », « état historique du handover » et « proposé ». Ne pas annoncer qu'un fichier a été modifié ni qu'un test a réussi s'il n'a pas été réellement exécuté.
