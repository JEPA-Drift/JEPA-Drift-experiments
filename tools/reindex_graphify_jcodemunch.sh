#!/usr/bin/env bash
# Reindex the project knowledge graphs (Graphify + jCodeMunch).
# Run at the end of each stream — see CLAUDE.md, "Engineering rules".
# --diff (default): incremental reindex. --full: purge graphify-out/ and the
# jCodeMunch index, then rebuild both from zero; the Graphify semantic layer
# (LLM-extracted nodes) is not regenerated and needs `graphify extract`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"

usage() {
    cat <<'EOF'
usage: tools/reindex_graphify_jcodemunch.sh [--diff|--full]

  --diff   incremental reindex of both indexes (default)
  --full   purge graphify-out/ and the jCodeMunch index, then rebuild from zero
EOF
}

mode=diff
for arg in "$@"; do
    case "$arg" in
        --diff) mode=diff ;;
        --full) mode=full ;;
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

expected=""
if [ "$mode" = full ]; then
    echo "[reindex] --full: purging graphify-out/ and the jCodeMunch index"
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

echo "[reindex] graphify update ."
graphify update .

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
