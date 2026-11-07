#!/usr/bin/env bash
set -euo pipefail
umask 077

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg GIT_OPTIONAL_LOCKS=0
mkdir -p "$root/logs"
exec 9>"$root/logs/.claude_surveillance.lock"
flock -n 9 || exit 0
exec "$root/.venv/bin/python" "$root/tools/ops/monitor_claude_sessions.py"
