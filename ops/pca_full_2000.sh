#!/usr/bin/env bash
# PCA-Drift full 2000 — operational launch/audit; no scientific-code mutation.
set -Eeuo pipefail

ACTION="${1:-check}"
case "$ACTION" in check|all|run|audit) ;; *) echo "Usage: $0 check|run|audit|all" >&2; exit 2 ;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE
export PYTHONHASHSEED=42
export MPLBACKEND=Agg

CONFIG='configs/pca_drift_benchmark_full_2000_resources.yaml'
OUT='results/pca_drift_benchmark/full_2000_20261101'
LOG='logs/pca_drift_benchmark/full_2000_20261101'
TAB1='results/pca_drift_benchmark/tables/full_2000_20261101'
TAB2='logs/pca_drift_benchmark/full_2000_20261101/tables_repeat'
PY='.venv/bin/python'
HIST='e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823'
RUNNER='8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373'
ASSEMBLER='13d386fe12c24e0d9ddeb994a7a113043b541d5e2b52f9c497377eb7eb0f4c5c'

mkdir -p "$LOG"
if [[ "$ACTION" != check ]]; then
  trap 'printf "%s\n" "$?" > "$LOG/operator_exit_code"' EXIT
fi

echo "[preflight] action=$ACTION root=$ROOT"
test -x "$PY" || { echo "Shared .venv missing: create symlink to main worktree .venv" >&2; exit 2; }
test -f "$CONFIG" || { echo "Missing resource-only YAML $CONFIG" >&2; exit 2; }
test "$(git rev-parse --show-toplevel)" = "$ROOT" || { echo "Not at worktree root" >&2; exit 2; }
[[ "$(git symbolic-ref --quiet --short HEAD)" == 'ops/pca-full-2000-20261101' ]] || { echo 'Wrong branch; refuse to run' >&2; exit 2; }
# Check worktree and index independently (CRLF is intentional).
echo "$HIST  results/e2/e2_cells.csv" | sha256sum -c -
[[ "$(git show ':results/e2/e2_cells.csv' | sha256sum | cut -d' ' -f1)" == "$HIST" ]] || { echo 'E2 Git-index hash mismatch' >&2; exit 2; }
echo "$RUNNER  experiments/pca_drift_benchmark.py" | sha256sum -c -
echo "$ASSEMBLER  experiments/pca_drift_tables.py" | sha256sum -c -
git diff --exit-code HEAD -- experiments/pca_drift_benchmark.py experiments/pca_drift_tables.py configs/pca_drift_benchmark.yaml results/e2/e2_cells.csv >/dev/null

"$PY" - "$CONFIG" <<'PY'
import sys, yaml
base=yaml.safe_load(open('configs/pca_drift_benchmark.yaml'))
cfg=yaml.safe_load(open(sys.argv[1]))
assert base.pop('resources') == {'mem_limit_gib':8.0,'max_wall_minutes':30.0}
resources=cfg.pop('resources')
assert cfg==base, 'Resource YAML changed scientific configuration'
assert resources == {'mem_limit_gib':24.0,'max_wall_minutes':360.0}, resources
assert all(cfg[k]==2000 for k in ('n_center','n_cal','n_null','n_alt'))
assert (cfg['N'],cfg['H'],cfg['nmax'],cfg['seed'],cfg['T_fit']) == (239,250,20,42,1000)
print('SCIENTIFIC_CONFIG_IDENTICAL: PASS; full counts 2000; resources 24 GiB / 360 min')
PY

echo "[preflight] HEAD=$(git rev-parse HEAD)"
git status --short
if [[ "$ACTION" == check ]]; then
  echo '[preflight] PASS (no simulation started)'
  exit 0
fi

if [[ "$ACTION" == run || "$ACTION" == all ]]; then
  if [[ -f "$OUT/manifest.json" ]]; then
    echo "[run] Existing completed manifest: refusing to rerun (will audit if action=all)"
    [[ "$ACTION" == all ]] || exit 2
  else
    RESUME=()
    if [[ -d "$LOG/partitions" ]] && find "$LOG/partitions" -type f -print -quit | grep -q .; then
      RESUME=(--resume)
      echo '[run] Detected incomplete partition set: --resume with unchanged config'
    elif [[ -d "$OUT" ]] && find "$OUT" -mindepth 1 -print -quit | grep -q .; then
      echo '[run] Output dir nonempty without manifest and no saved partitions: manual investigation required' >&2
      exit 2
    fi
    echo '[run] Starting immutable runner; no real data; 2000 per role'
    /usr/bin/time -v -o "$LOG/runner.time.log" "$PY" experiments/pca_drift_benchmark.py \
      --config "$CONFIG" --mode full --dataset synthetic --out "$OUT" --log-dir "$LOG" "${RESUME[@]}"
    echo '[run] Runner exit 0; manifest exists check next'
  fi
  test -s "$OUT/manifest.json" || { echo 'Runner did not seal manifest' >&2; exit 3; }
fi

if [[ "$ACTION" == audit || "$ACTION" == all ]]; then
  test -s "$OUT/manifest.json" || { echo 'Missing sealed runner manifest: cannot audit' >&2; exit 2; }
  for f in spectra.csv selection.csv calibration.csv trials.csv aggregates.csv issues.csv; do
    test -s "$OUT/$f" || { echo "Missing $OUT/$f" >&2; exit 2; }
  done
  "$PY" - "$OUT/manifest.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))
assert m['schema_version']=='pca_drift_benchmark/2'
assert m['run_mode']=='full' and m['dataset']=='synthetic'
assert m['config']['mode']=='full'
assert all(m['config'][k]==2000 for k in ['n_center','n_cal','n_null','n_alt'])
assert m['config']['resources']=={'mem_limit_gib':24.0,'max_wall_minutes':360.0}
print('RUN_MANIFEST: PASS; fingerprint',m['run_fingerprint'])
PY
  for d in "$TAB1" "$TAB2"; do
    if [[ -e "$d" ]]; then
      echo "[audit] Existing table output $d: refuse overwrite; verify/manual handling required" >&2
      exit 2
    fi
    "$PY" experiments/pca_drift_tables.py --input-dir "$OUT" \
      --output-dir "$d" --format both --strict
  done
  for f in TABLES_VALIDATION.md Tableau_PCA_1.csv Tableau_PCA_1.md \
    Tableau_PCA_2.csv Tableau_PCA_2.md Tableau_PCA_3.csv Tableau_PCA_3.md \
    table_lineage.csv table_manifest.json; do
    cmp "$TAB1/$f" "$TAB2/$f" || { echo "Not byte-identical: $f" >&2; exit 2; }
  done
  "$PY" - "$TAB1" "$TAB2" <<'PY'
import sys
from experiments.pca_drift_tables import verify_output_dir
assert verify_output_dir(sys.argv[1])
assert verify_output_dir(sys.argv[2])
print('TABLES_VERIFY_OUTPUT_DIR: PASS both runs')
PY
  { echo "HEAD $(git rev-parse HEAD)";
    echo "CONFIG_SHA $(sha256sum "$CONFIG")";
    echo 'RUN_OUTPUT_SHA256'; sha256sum "$OUT"/*.csv "$OUT"/manifest.json;
    echo 'TABLE_OUTPUT_SHA256'; sha256sum "$TAB1"/*;
    echo 'TABLE_1_2_BYTE_EQUAL PASS';
    echo 'HISTORICAL_E2_SHA256'; sha256sum results/e2/e2_cells.csv;
    echo 'RUNNER_RESOURCE_MEASURE'; cat "$LOG/runner.time.log";
  } > "$LOG/validation-summary.txt"
  echo '[audit] FULL TABLES PASS: input source preserved, two table renders byte-identical'
fi

echo "[done] action=$ACTION complete; output=$OUT ; tables=$TAB1 ; log=$LOG"
