# Amorçage parallèle de Claude Code — 2026-10-22

Chaque session utilise **Claude Opus 5.5**, l'effort **max** et le mode interactif **plan**.
Chaque worktree lie le `.venv` du dépôt principal et lance Claude Code avec ce `.venv` activé.
Les colonnes de modèle et d'effort de `prompts/streams/INDEX.md` sont historiques. Le plan,
ses questions et ses hypothèses sont transmis à l'orchestrateur pour revue avant le GO. Aucune
implémentation, installation, fusion ou publication ne précède ce GO. Après le GO, Claude Code
enregistre `prompts/plans/plan-[XX].md` avec la décision intégrée, puis implémente et vérifie.

| Porte | Amorçages à ouvrir dans des terminaux séparés |
| ----- | --------------------------------------------- |
| Maintenant | `amorcage-08b.md`, `amorcage-23.md`, `amorcage-27.md` |
| Après fusion de 8b sur `main` | `amorcage-12.md`, `amorcage-13.md`, `amorcage-14.md`, `amorcage-17.md`, `amorcage-18.md` |

Créer les worktrees depuis le commit local de `main` qui contient ces prompts :

```bash
cd ~/JEPA-Drift-experiments
for s in 08b 23 27; do
  git worktree add -b "stream-$s" "../JEPA-stream-$s" main
  ln -s "$PWD/.venv" "../JEPA-stream-$s/.venv"
  ln -s "$PWD/external" "../JEPA-stream-$s/external"
  mkdir -p "../JEPA-stream-$s/data/raw"
  for d in baf d3_yf; do ln -s "$PWD/data/raw/$d" "../JEPA-stream-$s/data/raw/$d"; done
done
```

Dans trois terminaux distincts, lancer respectivement :

```bash
cd ~/JEPA-stream-08b && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-08b.md)"
cd ~/JEPA-stream-23 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-23.md)"
cd ~/JEPA-stream-27 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-27.md)"
```

Quand le stream 8b est fusionné et présent sur `main`, vérifier que `jepadrift/data_loader/chars.py`,
`jepadrift/stats/drift.py` et `tools/check_prompts.py` existent, puis créer la vague suivante :

```bash
cd ~/JEPA-Drift-experiments
for s in 12 13 14 17 18; do
  git worktree add -b "stream-$s" "../JEPA-stream-$s" main
  ln -s "$PWD/.venv" "../JEPA-stream-$s/.venv"
  ln -s "$PWD/external" "../JEPA-stream-$s/external"
  mkdir -p "../JEPA-stream-$s/data/raw"
  for d in baf d3_yf; do ln -s "$PWD/data/raw/$d" "../JEPA-stream-$s/data/raw/$d"; done
done
ln -s "$PWD/data/raw/eurofidai" ../JEPA-stream-17/data/raw/eurofidai
```

Dans cinq terminaux distincts, lancer respectivement :

```bash
cd ~/JEPA-stream-12 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-12.md)"
cd ~/JEPA-stream-13 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-13.md)"
cd ~/JEPA-stream-14 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-14.md)"
cd ~/JEPA-stream-17 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-17.md)"
cd ~/JEPA-stream-18 && source .venv/bin/activate && claude --model claude-opus-5-5 --effort max --permission-mode plan "$(cat prompts/amorcage-18.md)"
```

Les sessions 14 et 17 peuvent coder en parallèle, puis intégrer leurs modifications du registre
partagé successivement. La session 18 développe l'adaptateur en parallèle et enregistre sa variante
P4 après 17. Les compléments 23/P4-D, 27/F2 et 27/P5-C restent soumis aux portes 17, 8b et 16.

Pour chaque session, transmettre à l'orchestrateur le plan, les questions de Claude Code, les
commandes de vérification prévues et les écarts proposés. Après implémentation, transmettre le
diff, les résultats des vérifications, les SHA-256 des sorties et le wrapup pour contrôle.
