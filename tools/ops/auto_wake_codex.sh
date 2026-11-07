#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/JEPA-Drift-experiments"
ALERT_FILE="$ROOT/logs/NEEDS_CODEX_REVIEW"
LAST_HASH=""

# Configuration de la cible (surchargeable via arguments : ./auto_wake_codex.sh [session] [fenetre] [panneau])
TARGET_SESSION="${1:-${CODEX_TMUX_SESSION:-0}}"
TARGET_WINDOW="${2:-${CODEX_TMUX_WINDOW:-0}}"
TARGET_PANE="${3:-${CODEX_TMUX_PANE:-0}}"

TARGET="${TARGET_SESSION}:${TARGET_WINDOW}.${TARGET_PANE}"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Veilleur actif."
echo " -> Cible tmux configurée : session '$TARGET_SESSION', fenêtre '$TARGET_WINDOW', panneau '$TARGET_PANE' ($TARGET)"
echo " -> Surveillance de : $ALERT_FILE"

while true; do
    if [ -s "$ALERT_FILE" ]; then
        CURRENT_HASH=$(sha256sum "$ALERT_FILE" | awk '{print $1}')
        
        if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
            echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Alerte $CURRENT_HASH détectée."
            
            # 1. Vérification que la cible tmux exacte existe
            if tmux list-panes -t "$TARGET" >/dev/null 2>&1; then
                echo " -> Injection scindée dans $TARGET..."
                # Écriture littérale
                tmux send-keys -t "$TARGET" -l "continue"
                # Pause de stabilisation pour Crossterm / Tokio
                sleep 0.5
                # Validation Entrée
                tmux send-keys -t "$TARGET" Enter
            elif tmux has-session -t "$TARGET_SESSION" 2>/dev/null; then
                # Si la fenêtre/panneau spécifique n'est pas trouvée mais la session existe
                echo " [AVERTISSEMENT] Panneau $TARGET introuvable, repli sur la fenêtre active de $TARGET_SESSION..."
                tmux send-keys -t "$TARGET_SESSION" -l "continue"
                sleep 0.5
                tmux send-keys -t "$TARGET_SESSION" Enter
            else
                # Repli headless si la session tmux interactive est fermée
                echo " -> Session $TARGET_SESSION introuvable. Exécution headless via codex exec..."
                export PATH="$HOME/.local/bin:$PATH"
                codex exec resume --last "Une alerte est levée dans logs/NEEDS_CODEX_REVIEW. Traite l'arbitrage."
            fi
            
            LAST_HASH="$CURRENT_HASH"
        fi
    fi
    sleep 30
done
EOF
chmod 700 tools/ops/auto_wake_codex.sh