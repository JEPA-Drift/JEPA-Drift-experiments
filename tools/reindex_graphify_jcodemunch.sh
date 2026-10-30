#!/usr/bin/env bash
# Reindex the project knowledge graphs (Graphify + jCodeMunch).
# Run at the end of each stream — see CLAUDE.md, "Engineering rules".
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[reindex] graphify update ."
graphify update .

echo "[reindex] jcodemunch index $ROOT"
jcodemunch-mcp index --no-ai-summaries "$ROOT"

echo "[reindex] done"
