# Index des prompts extraits — streams Claude Code & Mistral Vibe

Date : 2026-10-16. Source : `prompts/Prompts_Claude_Code_v5.md` (28 prompts, section 4).
Extraction : verbatim, un fichier par prompt. **Fidélité vérifiée** : chacun des 28 fichiers est une
sous-chaîne exacte de la source ; les 7 sections requises (Contexte, Tâche, Entrées, Livrables,
Contraintes techniques, Critères de succès, Commandes de vérification) sont présentes dans chacun.

Les prompts sont **agent-neutres** : ils sont autoporteurs et instructent « Lire `CLAUDE.md` » (une
lecture de fichier, exécutable par tout agent). Ils fonctionnent donc tels quels pour **Claude Code**
et pour **Mistral Vibe**.

## Dépôt Article B — local (amendement 2026-10-16)

Tous les prompts qui référençaient le dépôt distant `github.com/TheWhiteningAdvantage-KDD2027/The-Whitening-Advantage-Experiments` (clone vers `external/` du dépôt distant) utilisent désormais le **dépôt local** `~/The-Whitening-Advantage-Experiments` (lecture seule, utilisé tel quel à son commit courant). **Aucun prompt n'instruit de cloner le dépôt B distant.** Le venv Article B est créé côté projet (`external/articleB-venv/`, gitignoré via `external/`), hors du dépôt B, qui reste en lecture seule. Prompts concernés : **01** (`CLAUDE.md`), **02**, **04**, **07**. Les clones `alexouadi/CD-DFM` (prompts 03, 18) sont un dépôt différent, inchangés.

## Mémoire projet — le seul point d'adaptation Claude Code ↔ Mistral Vibe

- **Claude Code** charge automatiquement `CLAUDE.md` à chaque session.
- **Mistral Vibe** charge automatiquement `AGENTS.md` (niveau projet), pas `CLAUDE.md`.

Le prompt 1 écrit la mémoire dans `AGENTS.md` (contenu canonique) et crée le lien symbolique
relatif `CLAUDE.md` -> `AGENTS.md` : les deux agents chargent automatiquement la même mémoire,
sans copie ni dérive. Les prompts disant explicitement « Lire `CLAUDE.md` » restent valides
(lecture à travers le lien).
Le `AGENTS.md` projet s'ajoute au `~/.vibe/AGENTS.md` utilisateur (pas de conflit).

Note : le seul « Claude Code » littéral des 28 prompts est dans `prompt-10-eurofidai.md`
(note contextuelle « Claude Code n'a pas d'accès au portail EUROFIDAI » — le sens, « l'agent n'a pas
accès au portail », vaut pour tout agent ; aucune action requise).

## Fin de stream — protocole de clôture (tous les streams)

Dès qu'un stream est traité, l'agent qui le termine exécute, dans l'ordre :
1. `tools/reindex_graphify_jcodemunch.sh` (réindexe Graphify et jCodeMunch) ;
2. `make check` (pyflakes + tests) ;
3. commit explicite (Conventional Commits) ;
4. `git push origin <branche courante>`.

Le push est autorisé tant que l'adresse du dépôt n'est ni partagée publiquement ni liée à une
publication (dépôt compagnon d'une soumission anonyme : commits anonymisés, aucun nouvel
identifiant d'auteur ou d'institution). Les données EUROFIDAI ne quittent jamais la machine :
rien sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` ne peut être commité ni pushé,
et aucun fichier de plus de 50 Mo. Voir AGENTS.md (règles d'ingénierie).

## Routage par stream

Modèles : **Opus** = Claude Code (Claude Opus) · **Vibe** = Mistral Vibe (Large-4).
Effort Opus : low / medium / high / xhigh / max. Effort Vibe : Low / Medium / High / Max
(Max → niveau `high` de vibe, son maximum). Vagues : voir `prompts/Orchestration_Streams_v5.md`.

| # | Fichier | Titre | Piste | Prio | Jalon | Prérequis | Vague | Modèle | Effort |
|---|---------|-------|-------|------|-------|-----------|-------|--------|--------|
| 1 | `prompt-01-socle-e2.md` | Socle + lot 1 + E2 | X | A | J1 | — | 0 | Vibe | High |
| 2 | `prompt-02-data-d1-d2.md` | D1 + D2 (dépôt B) | X | A | J2 | 1 | 1 | Vibe | High |
| 3 | `prompt-03-data-d3.md` | D3 S&P 500 | X | A | J2, J3 | 1 | 1 | Vibe | High |
| 4 | `prompt-04-monitors-core.md` | Surveillance : noyau, portage B | T→CC | A | J2 | 1, 2 | 2 | **Opus** | **xhigh** |
| 5 | `prompt-05-injections.md` | Injections F1–F4, fonds D5/D6 | T→CC | A | J2 | 1, 2, 3 | 2 | Vibe | High |
| 6 | `prompt-06-representations-z.md` | Représentations linéaires, interface Z | T→CC | A | J2 | 2, 3 | 2 | **Opus** | **high** |
| 7 | `prompt-07-pipelines.md` | Pipelines P2-C, P3-C/D, P3-CS, P7 | T→CC | A | J2 | 4, 5, 6 | 3 | **Opus** | **xhigh** |
| 8 | `prompt-08-contracts.md` | Tests de contrat, découplage | T→CC | A | fusions | 4–7 | 4 | Vibe | High |
| 9 | `prompt-09-baf.md` | BAF | X | B | E9 | 1 | 1 | Vibe | Medium |
| 10 | `prompt-10-eurofidai.md` | EUROFIDAI (D4) spec | X | B | E4-EU | 1 | 1 | Vibe | High |
| 11 | `prompt-11-audit.md` | Audit informationnel | T→CC | A | J2 | 2, 3, 6 | 3 | Vibe | High |
| 12 | `prompt-12-e1.md` | E1 | T→CC | A | J2 | 4–8, 11 | 5 | **Opus** | **high** |
| 13 | `prompt-13-e3.md` | E3 | T→CC | A | J2 | 4–8 | 5 | **Opus** | **high** |
| 14 | `prompt-14-ca-tjepa.md` | CA-T-JEPA (code) | T→CC | A/B | J3 | 3, 6, 8 | 5 | **Opus** | **high** |
| 15 | `prompt-15-tjepa-baf.md` | T-JEPA pour BAF (code) | T→CC | B | E9 | 9 | 6 | Vibe | High |
| 16 | `prompt-16-pretrain-rankme.md` | Pré-entraînement + RankMe | X | A | J3 | 14 | 6 | Vibe | High |
| 17 | `prompt-17-ipca.md` | IPCA | T→CC | A | E4, E5 | 3, 6 | 3 | Vibe | High |
| 18 | `prompt-18-cddfm.md` | Adaptateur CD-DFM | T→CC | B | E4, E5 | 3, 6 | 3 | Vibe | High |
| 19 | `prompt-19-e4-p3kf.md` | E4 + P3-KF | T→CC | A/B | J4 | 5, 7, 11, 17 | 4 | Vibe | High |
| 20 | `prompt-20-transmission.md` | Transmission T(u), dictionnaire | T→CC | B/C | J4 | 16, 17 | 7 | Vibe | High |
| 21 | `prompt-21-freeze-runner.md` | Gel config, runner, figures | T→CC | A | J4, J6 | 12, 13 | 6 | Vibe | High |
| 22 | `prompt-22-e5.md` | E5 | T→CC | A/B/C | J4 | 16, 17, 19, 21 | 7 | **Opus** | **max** |
| 23 | `prompt-23-e6.md` | E6 | T→CC | B | J4 | 7, 16 | 7 | Vibe | High |
| 24 | `prompt-24-e9.md` | E9 | T→CC | B | J5 | 9, 15 | 8 | Vibe | High |
| 25 | `prompt-25-e8.md` | E8 | T→CC | A/B | J5 | 21 | 8 | Vibe | High |
| 26 | `prompt-26-e7.md` | E7 | T→CC | C | J5 | 16 | 7 | Vibe | Medium |
| 27 | `prompt-27-e10.md` | E10 | T→CC | C | J5 | 7 | 4 | Vibe | High |
| 28 | `prompt-28-e11.md` | E11 | T→CC | C | J5 | 5, 7, 14 | 8 | Vibe | Medium |

Streams **Opus** (quota compté) : **4, 6, 7, 12, 13, 14, 22**. Tous les autres : **Vibe**.

## Lancement (tmux)

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

## Auto-relance (rappel)

Au reset de quota Claude Pro (fenêtre 5 h), relancer les sessions Opus interrompues (vague 5 :
streams 12, 13, 14 — pic de quota). Les streams Vibe (quota team quasi illimité) tournent sans
interruption. Reprendre une session tmux : `tmux attach -t sNN` ; relancer à neuf si le process
est mort : rejouer la commande `tmux new-session` + `send-keys` ci-dessus.
