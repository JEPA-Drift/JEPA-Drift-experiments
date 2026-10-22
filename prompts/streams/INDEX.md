# Index des prompts — streams Claude Code & Mistral Vibe

Date : 2026-10-16. `prompts/streams/` stocke les configurations canoniques des streams (29
fichiers, un par stream) ; `prompts/Prompts_Claude_Code_v5.md` en est la collection dérivée
(section 4), synchronisée par Mistral Vibe. **Fidélité vérifiée** : chacun des 29 fichiers est une
sous-chaîne exacte du master ; les 7 sections requises (Contexte, Tâche, Entrées, Livrables,
Contraintes techniques, Critères de succès, Commandes de vérification) sont présentes dans chacun.

Révision du 2026-10-18 : prompts 12 à 28 révisés d'après les streams 1 à 11 et 11b ; nouveau prompt
`prompt-08b-hygiene.md` ; routage replanifié (section « Replanification du 18 octobre 2026 »).
Le master est resynchronisé depuis les fichiers stream ; l'outil de contrôle
`tools/check_prompts.py` et la cible `make prompts-check` sont livrés par le stream 8b.

Révision d'exécution du 2026-10-22 : tous les nouveaux streams sont confiés à Claude Code avec
`--model claude-opus-5-5 --effort max --permission-mode plan`. Les colonnes « Modèle » et « Effort »
du tableau historique ci-dessous ne gouvernent plus les lancements. Les amorçages et la porte de
dépendance sont dans `prompts/AMORCAGE_PARALLELE_CLAUDE_CODE.md`. Chaque worktree utilise
obligatoirement le `.venv` partagé du projet (`CLAUDE.md`, « Engineering rules »).

Les prompts sont **agent-neutres** : ils sont autoporteurs et instructent « Lire `CLAUDE.md` » (une
lecture de fichier, exécutable par tout agent). Ils fonctionnent donc tels quels pour **Claude Code**
et pour **Mistral Vibe**.

## Dépôt Article B — local (amendement 2026-10-16)

Tous les prompts qui référençaient le dépôt distant `github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments` (clone vers `external/` du dépôt distant) utilisent désormais le **dépôt local** `~/The-Whitening-Advantage-Experiments` (lecture seule, utilisé tel quel à son commit courant). **Aucun prompt n'instruit de cloner le dépôt B distant.** Le venv Article B est créé côté projet (`external/articleB-venv/`, gitignoré via `external/`), hors du dépôt B, qui reste en lecture seule. Prompts concernés : **01** (`CLAUDE.md`), **02**, **04**, **07**. Les clones `alexouadi/CD-DFM` (prompts 03, 18) sont un dépôt différent, inchangés.

## Mémoire projet — le seul point d'adaptation Claude Code ↔ Mistral Vibe

- **Claude Code** charge automatiquement `CLAUDE.md` à chaque session.
- **Mistral Vibe** charge automatiquement `AGENTS.md` (niveau projet), pas `CLAUDE.md`.

Le prompt 1 écrit la mémoire dans `CLAUDE.md` (contenu canonique) et crée le lien symbolique
relatif `AGENTS.md` -> `CLAUDE.md` : les deux agents chargent automatiquement la même mémoire,
sans copie ni dérive. Les prompts disant explicitement « Lire `CLAUDE.md` » visent le fichier
canonique.
Le `AGENTS.md` projet s'ajoute au `~/.vibe/AGENTS.md` utilisateur (pas de conflit).

Note : le seul « Claude Code » littéral des 28 prompts est dans `prompt-10-eurofidai.md`
(note contextuelle « Claude Code n'a pas d'accès au portail EUROFIDAI » — le sens, « l'agent n'a pas
accès au portail », vaut pour tout agent ; aucune action requise).

## Plans de stream — enregistrement avant exécution

Lorsqu'un plan d'implémentation est créé pour un stream [XX] (demande textuelle explicite de
l'utilisateur, ou appel direct de la directive `/plan`), il est enregistré dans
`prompts/plans/plan-[XX].md` AVANT son exécution. `prompts/plans/` stocke les plans
d'implémentation des streams.

## Fin de stream — protocole de clôture (tous les streams)

Chronologie exacte, une fois le traitement d'un stream terminé :
1. l'agent invoque sa directive de wrapup et enregistre le résumé dans
   `prompts/wrapups/wrapup-[XX].md` ([XX] = numéro ou référence du stream) ;
2. `tools/reindex_graphify_jcodemunch.sh` (réindexe jCodeMunch et Graphify) ;
3. `make check` (pyflakes + tests), puis commit explicite (Conventional Commits) — unique, ou
   plusieurs si les travaux du stream sont hétérogènes et risquent des erreurs sur une partie
   des livrables ;
4. push — depuis `main` : `git push origin main` ; depuis un worktree `stream-XX` :
   `git fetch origin`, rebase sur `origin/main`, `make check` si la base a bougé, puis
   `git push origin stream-XX:main` (jamais la branche `stream-XX` elle-même).

Avant **chaque** commit (y compris en cours de stream), l'instance chargée de l'implémentation
(Mistral Vibe ou Claude Code) invoque sa directive de wrapup et enregistre le résumé dans
`prompts/wrapups/wrapup-[XX].md` (fichier rafraîchi à chaque commit). Rôles des répertoires :
`prompts/streams/` stocke les prompts des streams planifiés ; `prompts/wrapups/` stocke les
résumés des traitements des streams.

Le push est autorisé tant que l'adresse du dépôt n'est ni partagée publiquement ni liée à une
publication (dépôt compagnon d'une soumission anonyme : commits anonymisés, aucun nouvel
identifiant d'auteur ou d'institution ; le chercheur a confirmé le 2026-10-16 que le dépôt,
public, n'est connu de personne). Les données EUROFIDAI ne quittent jamais la machine : rien sous
`data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` ne peut être commité ni pushé, et aucun
fichier de plus de 50 Mo. Voir `CLAUDE.md` (règles d'ingénierie et « Repository layout »).

## Routage par stream

Modèles : **Opus** = Claude Code (Claude Opus) · **Vibe** = Mistral Vibe (Large-4).
Effort Opus : low / medium / high / xhigh / max. Effort Vibe : Low / Medium / High / Max
(Max → niveau `high` de vibe, son maximum). Vagues : voir `prompts/Orchestration_Streams_v5.md`.

| #   | Fichier                          | Titre                                       | Piste | Prio                 | Jalon          | Prérequis                                | Vague   | Modèle   | Effort    | État                |
| --- | -------------------------------- | ------------------------------------------- | ----- | -------------------- | -------------- | ---------------------------------------- | ------- | -------- | --------- | ------------------- |
| 1   | `prompt-01-socle-e2.md`          | Socle + lot 1 + E2                          | X     | A                    | J1             | —                                        | 0       | Vibe     | High      | fait (J1 PASS)      |
| 2   | `prompt-02-data-d1-d2.md`        | D1 + D2 (dépôt B)                           | X     | A                    | J2             | 1                                        | 1       | Vibe     | High      | fait                |
| 3   | `prompt-03-data-d3.md`           | D3 S&P 500                                  | X     | A                    | J2, J3         | 1                                        | 1       | Vibe     | High      | fait                |
| 4   | `prompt-04-monitors-core.md`     | Surveillance : noyau, portage B             | T→CC  | A                    | J2             | 1, 2                                     | 2       | **Opus** | **max**   | fait                |
| 5   | `prompt-05-injections.md`        | Injections F1–F4, fonds D5/D6               | T→CC  | A                    | J2             | 1, 2, 3                                  | 2       | Vibe     | High      | fait                |
| 6   | `prompt-06-representations-z.md` | Représentations linéaires, interface Z      | T→CC  | A                    | J2             | 2, 3                                     | 2       | **Opus** | **xhigh** | fait                |
| 7   | `prompt-07-pipelines.md`         | Pipelines P2-C, P3-C/D, P3-CS, P7           | T→CC  | A                    | J2             | 4, 5, 6                                  | 3       | **Opus** | **max**   | fait                |
| 8   | `prompt-08-contracts.md`         | Tests de contrat, découplage                | T→CC  | A                    | fusions        | 4–7                                      | 4       | Vibe     | High      | fait                |
| 8b  | `prompt-08b-hygiene.md`          | Hygiène : modules partagés, fixture, écarts | T→CC  | A                    | J2             | 7, 8, 11                                 | 9       | Vibe     | High      | à lancer            |
| 9   | `prompt-09-baf.md`               | BAF                                         | X     | B                    | E9             | 1                                        | 1       | Vibe     | Medium    | fait                |
| 10  | `prompt-10-eurofidai.md`         | EUROFIDAI (D4)                              | X     | B                    | E4-EU          | 1                                        | 1       | Vibe     | High      | fait (D4 construit) |
| 11  | `prompt-11-audit.md`             | Audit informationnel                        | T→CC  | A                    | J2             | 2, 3, 6                                  | 3       | Vibe     | High      | fait                |
| 11b | `../GO-stream-11b.md`            | Audit : bruit de N2, placebo                | T→CC  | A                    | J2             | 11                                       | 3       | Opus     | —         | fait                |
| 12  | `prompt-12-e1.md`                | E1                                          | T→CC  | A                    | J2             | 2–8, 8b, 11                              | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 13  | `prompt-13-e3.md`                | E3                                          | T→CC  | A                    | J2             | 4–8, 8b                                  | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 14  | `prompt-14-ca-tjepa.md`          | CA-T-JEPA (code)                            | T→CC  | A/B                  | J3             | 3, 6, 8, 8b                              | 10      | **Opus** | **xhigh** | révisé 18/10        |
| 15  | `prompt-15-tjepa-baf.md`         | T-JEPA pour BAF (code)                      | T→CC  | B                    | E9             | 9 (torch : 14)                           | 11      | Vibe     | High      | révisé 18/10        |
| 16  | `prompt-16-pretrain-rankme.md`   | Pré-entraînement + RankMe                   | X     | A                    | J3             | 14                                       | 11      | Vibe     | High      | révisé 18/10        |
| 17  | `prompt-17-ipca.md`              | IPCA                                        | T→CC  | A                    | E4, E5, E6     | 3, 6, 8b                                 | 10      | Vibe     | High      | révisé 18/10        |
| 18  | `prompt-18-cddfm.md`             | Adaptateur CD-DFM                           | T→CC  | B                    | E4, E5         | 3, 6, 8b                                 | 11      | Vibe     | High      | révisé 18/10        |
| 19  | `prompt-19-e4-p3kf.md`           | E4 + P3-KF                                  | T→CC  | A/B                  | J4             | 5, 7, 8b, 11, 17                         | 11      | Vibe     | High      | révisé 18/10        |
| 20  | `prompt-20-transmission.md`      | Transmission T(u), dictionnaire             | T→CC  | B/C                  | J4             | 16, 17                                   | 12      | Vibe     | High      | révisé 18/10        |
| 21  | `prompt-21-freeze-runner.md`     | Gel config, runner, figures                 | T→CC  | A                    | J4, J6         | 12, 13                                   | 11      | Vibe     | High      | révisé 18/10        |
| 22  | `prompt-22-e5.md`                | E5                                          | T→CC  | A/B/C                | J4             | 16, 17, 19, 21, 23 (ph. 2)               | 12      | **Opus** | **max**   | révisé 18/10        |
| 23  | `prompt-23-e6.md`                | E6 (ph. 1 linéaire, ph. 2 JEPA)             | T→CC  | A (ph. 1), B (ph. 2) | J3 (ph. 1), J4 | ph. 1 : 5, 7 (17 pour P4-D) ; ph. 2 : 16 | 10 / 12 | Vibe     | High      | révisé 18/10        |
| 24  | `prompt-24-e9.md`                | E9                                          | T→CC  | B                    | J5             | 9, 15                                    | 13      | Vibe     | High      | révisé 18/10        |
| 25  | `prompt-25-e8.md`                | E8                                          | T→CC  | A/B                  | J5             | 8b, 21                                   | 13      | Vibe     | High      | révisé 18/10        |
| 26  | `prompt-26-e7.md`                | E7                                          | T→CC  | C                    | J5             | 16                                       | 12      | Vibe     | Medium    | révisé 18/10        |
| 27  | `prompt-27-e10.md`               | E10                                         | T→CC  | C                    | J5             | 7                                        | 13      | Vibe     | High      | révisé 18/10        |
| 28  | `prompt-28-e11.md`               | E11                                         | T→CC  | C                    | J5             | 5, 7, 14                                 | 13      | Vibe     | Medium    | révisé 18/10        |

Streams **Opus** restants (quota compté) : **12, 13, 14, 22**. Tous les autres : **Vibe**.

## Lancement effectif du 22 octobre 2026

| Porte | Sessions parallèles | Limite de la livraison initiale |
| ----- | -------------------- | ------------------------------- |
| Maintenant | 8b, 23, 27 | 23 : phase 1 P1-D/P3-D ; 27 : étape linéaire P1-C/P3-C |
| Après fusion de 8b | 12, 13, 14, 17, 18 | 18 : adaptateur en parallèle, enregistrement P4 après 17 |

Les plans peuvent avancer en parallèle ; l'exécution du code de chaque stream attend le GO de
son plan. Les modifications au registre partagé de 14, 17 et 18 sont intégrées l'une après l'autre.
Les compléments 23/P4-D et 27/P5-C attendent respectivement 17 et 16.

## Replanification du 18 octobre 2026 (historique)

| Vague | Dates            | Streams (parallèles)                                                                                                                     | Déclencheur                                          |
| ----- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 9     | 18–19 oct.       | 8b hygiène                                                                                                                               | immédiat ; bloque 12, 13, 14, 17                     |
| 10    | 19–23 oct.       | 12 E1 et 14 CA-T-JEPA (Opus) ; 13 E3 (Opus, démarrage décalé de 12 h, repli Vibe High si le quota Opus sature) ; 17 IPCA ; 23 E6 phase 1 | 8b fusionné                                          |
| 11    | 24 oct.–1er nov. | 16 pré-entraînement ; 21 gel et runner ; 19 E4 ; 18 CD-DFM ; 15 T-JEPA BAF                                                               | 14 (pour 15 et 16), 12 et 13 (pour 21), 17 (pour 19) |
| 12    | 2–8 nov.         | 22 E5 ; 23 E6 phase 2 ; 20 transmission ; 26 E7                                                                                          | 16 et 21 fusionnés ; gel au J4                       |
| 13    | 9–15 nov.        | 25 E8 ; 24 E9 ; 27 E10 ; 28 E11                                                                                                          | gel J4 (pour 25), 15 (pour 24)                       |

Jalons : J2 = résumés d'E1 et d'E3 ; J3 = porte RankMe du stream 16 et E6 phase 1 (évidence pour
la contingence C1) ; J4 = gel du stream 21 et porte d'E5.

## Lancement Claude Code actuel

Utiliser `prompts/AMORCAGE_PARALLELE_CLAUDE_CODE.md` : chaque commande y fixe explicitement
`claude-opus-5-5`, `max` et `plan`, puis attend la revue du plan avant l'implémentation.

## Lancement historique (ne pas utiliser)

Depuis `~/JEPA-Drift-experiments`. Nommage suggéré : `s01`…`s28`.

**Claude Code (Opus)** — interactif (recommandé pour les longues tâches + auto-relance) :
```bash
tmux new-session -d -s s04 'cd ~/JEPA-Drift-experiments && claude --effort xhigh'
tmux send-keys -t s04 "$(cat prompts/streams/prompt-04-monitors-core.md)" Enter
```
- `--effort` : low | medium | high | xhigh | max. Modèle Opus par défaut (ou `--model opus`).
- `--dangerously-skip-permissions` pour supprimer toute pause d'approbation (autonomie).
- One-shot programmatique : `claude --effort xhigh --dangerously-skip-permissions -p "$(cat <fichier>")`.

**Mistral Vibe (Large-4)** — interactif :
```bash
tmux new-session -d -s s02 'cd ~/JEPA-Drift-experiments && vibe'
tmux send-keys -t s02 '/thinking high' Enter          # niveau d'effort (none|low|medium|high)
tmux send-keys -t s02 "$(cat prompts/streams/prompt-02-data-d1-d2.md)" Enter
```
- Effort vibe : slash-command `/thinking` (none | low | medium | high) ou `[agent] thinking = "high"`
  dans `~/.vibe/config.toml` / un agent `~/.vibe/agents/NAME.toml` (lancé via `--agent NAME`).
  Le « Max » de l'utilisateur = `high` (niveau max de vibe). Éviter `low` (bug connu : envoie
  `reasoning_effort=none`, 400 avec glm-5.3).
- One-shot programmatique : `vibe --prompt-file <fichier> --auto-approve` (effort via la config).
- `bypass_tool_permissions = true` est déjà actif dans `~/.vibe/config.toml`.

## Auto-relance historique (ne pas utiliser)

Au reset de quota Claude Pro (fenêtre 5 h), relancer les sessions Opus interrompues (vague 5 :
streams 12, 13, 14 — pic de quota). Les streams Vibe (quota team quasi illimité) tournent sans
interruption. Reprendre une session tmux : `tmux attach -t sNN` ; relancer à neuf si le process
est mort : rejouer la commande `tmux new-session` + `send-keys` ci-dessus.
