#!/usr/bin/env bash
set -u
J=logs/stream_19_e4_production
E="OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg"

attempt() {
  local k=1 id rc
  until mkdir "$J/attempts/$(printf 'A%07d' "$k")" 2>/dev/null; do
    [ -e "$J/attempts/$(printf 'A%07d' "$k")" ] || return 8
    k=$((k + 1))
  done
  id=$(printf 'A%07d' "$k")
  printf '%s\n' "$*" > "$J/attempts/$id/cmd.txt" || return 8
  /usr/bin/time -f '%U %S %e %M %x' -o "$J/attempts/$id/time.txt" timeout --signal=TERM --kill-after=10s 1790s \
    env $E E4_ATTEMPT_ID="$id" .venv/bin/python experiments/e4_production.py "$@"
  rc=$?
  printf '%s\n' "$rc" > "$J/attempts/$id/exit.txt"
  return "$rc"
}

if [ -z "${E4_LOCK:-}" ]; then
  common_dir=$(git rev-parse --path-format=absolute --git-common-dir) || exit 1
  E4_LOCK="$common_dir/../logs/.jepa_execution.lock"
fi
exec 9>"$E4_LOCK" || exit 1
flock -n 9 || { echo "shared execution lock busy: $E4_LOCK" >&2; exit 1; }
mkdir -p "$J/attempts" || exit 1

case "${1:-}" in
  attempt)
    shift
    attempt "$@"
    exit $?
    ;;
  campaign)
    { [ "$#" -eq 5 ] || [ "$#" -eq 6 ]; } || { echo "usage: $0 campaign MODE ROOT BLOCK TARGET [ACTIVATION]" >&2; exit 2; }
    mode=$2 root=$3 block=$4 target=$5
    case "$block" in ''|0*|*[!0-9]*) echo "BLOCK must be a positive decimal integer, got '$block'" >&2; exit 2 ;; esac
    common=(--mode "$mode" --root "$root")
    [ "$#" -eq 6 ] && common+=(--activation "$6")
    K=$(attempt --phase plan --block "$block" "${common[@]}") || exit $?
    case "$K" in ''|0*|*[!0-9]*) echo "plan printed a non-decimal K '$K'" >&2; exit 5 ;; esac
    [ "${#K}" -le 6 ] || { echo "plan printed K=$K beyond six digits" >&2; exit 5; }
    rc=9
    for _ in $(seq 1 $((K + 1))); do
      attempt --phase next "${common[@]}"
      rc=$?
      [ "$rc" -eq 10 ] && break
      [ "$rc" -eq 0 ] || exit "$rc"
    done
    [ "$rc" -eq 10 ] || exit 9
    attempt --phase verify "${common[@]}" || exit $?
    attempt --phase publish "${common[@]}" --to "$target" || exit $?
    exit 0
    ;;
  *)
    echo "usage: $0 attempt ARGS... | campaign MODE ROOT BLOCK TARGET [ACTIVATION]" >&2
    exit 2
    ;;
esac
