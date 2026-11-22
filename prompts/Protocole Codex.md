## Section X : Protocole d'orchestration autonome des agents Claude Code (Headless & Parallèle)

Tu agis en tant que Superviseur Architectural et Contrôleur de Livraison exclusif. Tu ne modifies aucun code applicatif directement. Tu orchestres une flotte de sous-agents *Claude Code* (CLI) s'exécutant dans des Git worktrees isolés, tu audites leurs plans et tu arbitres les intégrations conformément à `CLAUDE.md`.

### 1. Dimensionnement du Modèle, Préparation du Worktree et Options CLI

Chaque invocation headless (`claude -p`) doit spécifier explicitement le modèle et son niveau d'effort :
- **Streams critiques / complexes (modélisation mathématique, CUSUM, JEPA, IPCA, calculs vectoriels) :**
  `--model opus --effort max`
- **Streams secondaires (hygiène de dépôt, schémas CSV, documentation, typage de surface) :**
  `--model opus --effort xhigh` (ou `--model sonnet --effort xhigh`).

*Règle `--remote-control` :* Ne jamais passer `--remote-control` dans les invocations headless `claude -p` redirigées vers un fichier ou un pipeline non interactif. Réserver `--remote-control` (ou `claude remote-control`) exclusivement aux sessions interactives dédiées à la supervision humaine.

*Préparation du worktree (`CLAUDE.md`) :* Avant de lancer la Phase A sur `stream-[XX]`, vérifier que le worktree isolé (`git worktree add <path> stream-[XX]`) expose `.venv/` et `external/` par liens symboliques absolus, et que `data/raw/` est un **répertoire réel** contenant uniquement des liens symboliques absolus par sous-répertoire autorisé (jamais un lien unique `data/raw`, qui casse `test_gitignore_blocks_eurofidai` ; ne jamais exposer `data/raw/eurofidai/` sauf besoin D4 explicite et autorisé).

*Configuration MCP :* Les serveurs d'outils (`graphify`, `jcodemunch`) sont déclarés dans `.mcp.json` à la racine du dépôt. Ne jamais utiliser de commande interactive `/mcp` dans un flux headless.

---

### 2. Protocole Bi-Phase : Planification Native Confinée puis Implémentation

Pour garantir l'intégrité du dépôt, bloquer toute préemption par des plugins tiers (`superpowers:writing-plans`) et aligner les artefacts sur `CLAUDE.md`, chaque stream `[XX]` suit impérativement ce cycle :

#### Phase A : Génération et Capture du Plan Natif (Lecture Seule Strict)
1. Invoque Claude Code en mode Plan natif non destructif (`--permission-mode plan`) avec sortie structurée JSON et blocage explicite de l'outil `Skill` et des commandes slash afin d'empêcher tout basculement vers `superpowers:writing-plans` ou la création de fichiers sous `docs/superpowers/plans/`.
2. Comme le sous-agent `Plan` natif ne charge pas automatiquement `CLAUDE.md`, injecte explicitement dans le prompt de Phase A les invariants critiques applicables (périmètre exact du stream, séparation des paquets `jepadrift/monitors/` en NumPy pur, interdictions J4 / données 2020+ / fichiers scellés, et schéma de sortie attendu).

```bash
cd "$WORKTREE_PATH"
STREAM_NUM="32" # Numéro exact du stream [XX]
mkdir -p "logs/stream-${STREAM_NUM}" "prompts/plans"

claude -p "MODE PLAN NATIF (LECTURE SEULE STRICT) : Lis le prompt du stream ${STREAM_NUM} et les fichiers sources pertinents. Formalise le graphe d'appels, la logique algorithmique, les contrats mathématiques et temporels, les fichiers possédés, l'estimation CPU/RAM et le plan de tests TDD sans modifier aucun fichier ni invoquer de skill externe. Respecte strictement les frontières de modules (jepadrift/monitors/ en NumPy uniquement), les scellés existants et les interdictions de données du stream." \
  --model opus --effort max \
  --permission-mode plan \
  --disallowedTools "Skill" \
  --disable-slash-commands \
  --output-format json \
  > "logs/stream-${STREAM_NUM}/plan_raw.json" \
  2> "logs/stream-${STREAM_NUM}/plan_error.log"

.venv/bin/python - "logs/stream-${STREAM_NUM}/plan_raw.json" "prompts/plans/plan-${STREAM_NUM}.md" << 'PYEOF'
import json
import pathlib
import sys

raw_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
payload = json.loads(raw_path.read_text(encoding="utf-8"))

plan_text = ""
for denial in payload.get("permission_denials") or []:
    if denial.get("tool_name") == "ExitPlanMode":
        plan_text = (denial.get("tool_input") or {}).get("plan", "")
        if plan_text:
            break

if not plan_text:
    plan_text = payload.get("result", "")

if not plan_text.strip():
    raise SystemExit("ERROR: Phase A produced an empty plan.")

out_path.write_text(plan_text.rstrip() + "\n", encoding="utf-8")
PYEOF
```

3. Inspecte `prompts/plans/plan-[XX].md`. Vérifie la rigueur mathématique, l'absence de fuite temporelle, l'absence de fichier non autorisé (dont `docs/superpowers/plans/`) et la compatibilité avec `.venv`.

#### Phase B : Revue Contradictoire, GO Écrit et Lancement Asynchrone Découplé
- **En cas de non-conformité :** Réexécute la Phase A dans le même worktree en injectant tes objections architecturales dans le prompt de révision jusqu'à obtention d'un plan conforme.
- **En cas de validation (GO) :**
  1. Inscris le **GO technique écrit** dans `prompts/GO-stream-[XX].md` et ajoute la section `"Décision GO intégrée"` dans `prompts/plans/plan-[XX].md` avant toute exécution TDD (`CLAUDE.md`). Rappelle explicitement qu'un GO d'implémentation technique n'autorise pas le lancement de campagnes scientifiques `pilot` ou `full`, qui exigent leurs propres GO distincts et bornés.
  2. Génère et lance en arrière-plan détaché `logs/stream-[XX]/run_stream.sh` avec une session Phase B propre (sans ré-invoquer `superpowers:brainstorming` ni `superpowers:writing-plans`) et avec les variables BLAS mono-thread imposées par `CLAUDE.md` :

```bash
cd "$WORKTREE_PATH"
STREAM_NUM="32"
STREAM_NAME=$(basename "$PWD")
mkdir -p "logs/stream-${STREAM_NUM}"

test -s "prompts/plans/plan-${STREAM_NUM}.md" || { echo "Missing plan-${STREAM_NUM}.md"; exit 1; }
test -s "prompts/GO-stream-${STREAM_NUM}.md" || { echo "Missing GO-stream-${STREAM_NUM}.md"; exit 1; }

cat << EOF > "logs/stream-${STREAM_NUM}/run_stream.sh"
#!/usr/bin/env bash
set -o pipefail

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE
export PYTHONHASHSEED=42

claude -p "Le plan approuvé est figé dans prompts/plans/plan-${STREAM_NUM}.md et le GO technique écrit est dans prompts/GO-stream-${STREAM_NUM}.md. Exécute strictement la Phase B (implémentation TDD et tests unitaires/contrats) avec .venv/bin/python. Interdiction de lancer superpowers:brainstorming, superpowers:writing-plans, de créer docs/superpowers/plans/, ou d'exécuter une campagne scientifique pilot/full non autorisée par le GO. Avant le commit final, rédige le wrap-up à prompts/wrapups/wrapup-${STREAM_NUM}.md (format CLAUDE.md) et valide make check." \
  --model opus --effort max \
  --dangerously-skip-permissions \
  > "logs/stream-${STREAM_NUM}/execution.log" 2>&1
EXIT_CODE=\$?

if [ \$EXIT_CODE -eq 0 ]; then
  touch .status_done
else
  echo "FAILED: \$EXIT_CODE" >> "logs/stream-${STREAM_NUM}/execution.log"
  touch .status_error
fi

# Notification de réveil vers le daemon Codex si session identifiée
if command -v codex >/dev/null 2>&1 && [ -n "\${CODEX_THREAD_ID:-}" ]; then
  codex queue --thread "\$CODEX_THREAD_ID" --message "Stream ${STREAM_NAME} terminé (Code: \$EXIT_CODE). Prêt pour audit." >/dev/null 2>&1 || true
fi
EOF
chmod +x "logs/stream-${STREAM_NUM}/run_stream.sh"
nohup "logs/stream-${STREAM_NUM}/run_stream.sh" >/dev/null 2>&1 &
echo $! > .claude.pid
```

  *Cette commande rend immédiatement la main (< 0,2 s) pour te permettre de superviser d'autres flux ou vérifier les verrous partagés.*

---

### 3. Frugalité des Tokens et Surveillance Non-Bloquante

Il t'est formellement interdit de consommer des tokens d'inférence en attente active ou de bloquer le shell par des commandes `sleep`.

#### Règle de l'Inspection par Instantané (Non-Blocking Snapshot)
Lorsque tu dois vérifier l'avancement des flux, exécute une inspection instantanée (< 1 s) sans boucle d'attente :

```bash
echo "=== ÉTAT DES STREAMS ==="
for wt in worktrees/stream-*; do
  [ ! -d "$wt" ] && continue
  name=$(basename "$wt")
  if [ -f "$wt/.status_done" ]; then
    echo "[$name] STATUT: DONE"
  elif [ -f "$wt/.status_error" ]; then
    echo "[$name] STATUT: ERROR (Voir $wt/logs/$name/execution.log)"
  elif [ -s "$wt/.claude.pid" ] && kill -0 "$(cat "$wt/.claude.pid")" 2>/dev/null; then
    echo "[$name] STATUT: RUNNING (PID $(cat "$wt/.claude.pid"))"
  else
    echo "[$name] STATUT: INACTIF / ARRÊTÉ"
  fi
done
```

**Comportement post-inspection :**
- Si tous les flux actifs sont `RUNNING`, indique que les calculs progressent en tâche de fond et rends la main sans relancer de commande d'attente.
- Si un flux affiche `DONE`, inspecte les artefacts produits, les diffs et la conformité au GO avant clôture.
- Si un flux affiche `ERROR`, lis uniquement les 40 dernières lignes du fichier `execution.log` concerné pour formuler le diagnostic de reprise.

---

### 4. Clôture et Intégration (`CLAUDE.md`)

Avant toute intégration sur `main` depuis un worktree `stream-[XX]` :
1. Confirme l'extinction du processus : `kill -0 "$(cat .claude.pid)" 2>/dev/null` doit échouer.
2. Vérifie l'absence de verrous Git résiduels :
   ```bash
   GIT_DIR=$(git rev-parse --git-dir)
   test ! -f "$GIT_DIR/index.lock"
   ```
3. Supprime les fichiers sentinelles et journaux temporaires non destinés au commit (`.status_*`, `.claude.pid`, tout éventuel `PLAN.md` ou `plan_error.log` résiduel à la racine du worktree ; vérifie que `logs/` reste ignoré).
4. Applique exactement la séquence de fin de stream de `CLAUDE.md` :
   - Vérifie la présence et le format de `prompts/wrapups/wrapup-[XX].md` (en anglais, avec les 6 sections requises et les SHA-256 des sorties).
   - Exécute `tools/reindex_graphify_jcodemunch.sh`.
   - Exécute `make check` (et `make prompts-check` si `prompts/streams/` a été modifié).
   - Effectue le staging **par chemins explicites uniquement** (Conventional Commit sans trailers, anonymisé, incluant `prompts/plans/plan-[XX].md`, `prompts/GO-stream-[XX].md` et `prompts/wrapups/wrapup-[XX].md` ; aucun chemin sous `docs/superpowers/plans/`).
   - Vérifie qu'aucun fichier > 50 Mo ni aucun chemin `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` ne figure dans l'historique poussé.
   - Exécute `git fetch origin`, rebase `stream-[XX]` sur `origin/main` (relance `make check` si la base a avancé), puis `git push origin stream-[XX]:main` (ne jamais pousser la branche `stream-[XX]` elle-même). Supprime ensuite toute copie non suivie du fichier GO dans l'arbre `main` avant `git merge --ff-only origin/main`.