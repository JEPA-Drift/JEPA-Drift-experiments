#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/JEPA-Drift-experiments"
ALERT_FILE="$ROOT/logs/NEEDS_CODEX_REVIEW"
LAST_HASH=""

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Veilleur actif. Surveillance de $ALERT_FILE..."

while true; do
    if [ -s "$ALERT_FILE" ]; then
        CURRENT_HASH=$(sha256sum "$ALERT_FILE" | awk '{print $1}')
        
        if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
            echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Alerte $CURRENT_HASH : injection scindée dans tmux:0..."
            
            if tmux has-session -t 0 2>/dev/null; then
                # 1. Écriture du mot littéral
                tmux send-keys -t 0 -l "continue"
                # 2. Pause de stabilisation TUI (500ms indispensable pour Codex / Crossterm)
                sleep 0.5
                # 3. Validation par Entrée isolée
                tmux send-keys -t 0 Enter
            else
                export PATH="$HOME/.local/bin:$PATH"
                codex exec resume --last "Une alerte est levée dans logs/NEEDS_CODEX_REVIEW. Traite l'arbitrage."
            fi
            
            LAST_HASH="$CURRENT_HASH"
        fi
    fi
    sleep 30
done
