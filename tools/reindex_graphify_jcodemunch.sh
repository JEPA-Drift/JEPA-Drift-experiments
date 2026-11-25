#!/usr/bin/env bash
# Reindex the project knowledge graphs (Graphify + jCodeMunch).
# Run at the end of each stream — see CLAUDE.md, "Engineering rules".
# --diff (default): drop graph nodes whose source file is gone, then AST reindex.
# --full: print the node types it destroys, purge both indexes, rebuild from zero.
# --semantic: replace the AST pass with `graphify extract`, the only path that produces the
#             image, paper and concept nodes; billable, cached by content, never implied.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"

usage() {
    cat <<'EOF'
usage: tools/reindex_graphify_jcodemunch.sh [--diff|--full] [--semantic]

  --diff      incremental reindex, dropping graph nodes whose source file is gone (default)
  --full      print the node types destroyed, purge both indexes, rebuild from zero
  --semantic  run `graphify extract` instead of `graphify update`: LLM pass, billable
              backend (whichever API key is set), semantic cache by content hash, so
              later runs only pay for changed documents
EOF
}

mode=diff
semantic=0
for arg in "$@"; do
    case "$arg" in
        --diff) mode=diff ;;
        --full) mode=full ;;
        --semantic) semantic=1 ;;
        -h|--help) usage; exit 0 ;;
        *)
            echo "[reindex] error: unknown argument: $arg" >&2
            usage >&2
            exit 2
            ;;
    esac
done

repo_id() {
    jcodemunch-mcp list-repos --json 2>/dev/null | python3 -c '
import json, os, sys
root = sys.argv[1]
ids = [r["repo_id"] for r in json.load(sys.stdin)
       if os.path.realpath(r.get("source_root") or "") == root]
print(ids[0] if ids else "")
' "$ROOT"
}

inventory() {
    [ -f "$ROOT/graphify-out/graph.json" ] || { echo "[reindex] no graph to inventory"; return 0; }
    python3 - "$ROOT/graphify-out/graph.json" <<'PY' || echo "[reindex] inventory failed, continuing"
import collections
import json
import sys

counts = collections.Counter(node.get("file_type") for node in json.load(open(sys.argv[1])).get("nodes", []))
print("[reindex] destroying: " + ", ".join(f"{kind} {count}" for kind, count in counts.most_common()))
PY
}

expected=""
if [ "$mode" = full ]; then
    echo "[reindex] --full: purging graphify-out/ and the jCodeMunch index"
    inventory
    rm -rf "$ROOT/graphify-out"
    expected="$(repo_id)"
    if [ -n "$expected" ]; then
        echo "[reindex] jcodemunch-mcp delete-index $expected"
        jcodemunch-mcp delete-index "$expected" --json \
            || echo "[reindex] warning: delete-index reported failure for $expected"
    else
        echo "[reindex] no existing jCodeMunch index for $ROOT"
    fi
fi

if [ -f "$ROOT/graphify-out/graph.json" ]; then
    echo "[reindex] prune_graph_ghosts.py"
    python3 "$ROOT/tools/prune_graph_ghosts.py" --root "$ROOT"
fi

if [ "$semantic" = 1 ]; then
    echo "[reindex] graphify extract . (LLM pass, billable)"
    graphify extract .
else
    echo "[reindex] graphify update ."
    graphify update .
fi

echo "[reindex] jcodemunch-mcp index $ROOT"
jcodemunch-mcp index --no-ai-summaries "$ROOT"

actual="$(repo_id)"
if [ -n "$expected" ] && [ "$actual" != "$expected" ]; then
    echo "[reindex] error: index resolved to '${actual}' instead of '$expected'" >&2
    echo "[reindex] an index whose git_root contains $ROOT captured the path;" >&2
    echo "[reindex] find it with 'jcodemunch-mcp list-repos --json' and delete it" >&2
    exit 1
fi

echo "[reindex] done"
