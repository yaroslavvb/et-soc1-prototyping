#!/usr/bin/env bash
# PCIE2: run a schedule's pcie2 passes in order on the local card, as queue.sh would, without queue.sh's own die
# reading before each block (on a two-card host that is lib's die_c: an ettelem sample with timeout 20 and no card
# lock), and stopping at the first pass that fails (queue.sh logs a failed block and goes on to the next). Each pass
# does its own checks and samples under the lock (block.sh). Lines: "pcie2 <pass>", "sleep <s>", "end". Used for
# development on aifoundry1 and for validation on aifoundry3.
#   [V3_DEVICE=1] bash tools/claims-v3/pcie2/run_passes.sh <schedule>
# A pass that finds someone else (exit 3) is retried after 10 minutes, three times at most; a failed process (exit 1),
# a refusal (2), a hot die (4) or a process that looked hung (5, which also writes build/claims-v3/STOP) stops the run,
# and so does build/claims-v3/STOP (build/claims-v3-dry/STOP under V3_DRY) before any pass.
set -u
sched=${1:?schedule file}
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
STOP=build/claims-v3/STOP; [ -n "${V3_DRY:-}" ] && STOP=build/claims-v3-dry/STOP
echo "$(date +%FT%T) run_passes: $sched${V3_DEVICE:+ (V3_DEVICE=$V3_DEVICE)}${V3_DRY:+ (DRY)}"
while read -r exp arg _; do
  [ -e "$STOP" ] && { echo "$(date +%FT%T) $STOP present: stopping"; exit 0; }
  case "$exp" in
    ''|\#*) continue ;;
    end) break ;;
    sleep) sleep "$arg"; continue ;;
    pcie2) ;;
    *) echo "$(date +%FT%T) not a pcie2 line: $exp $arg" >&2; exit 2 ;;
  esac
  for try in 1 2 3; do
    bash tools/claims-v3/pcie2/block.sh "$arg" < /dev/null; rc=$?
    echo "$(date +%FT%T) pcie2 p$arg try $try: exit $rc"
    [ $rc -eq 3 ] || break
    sleep 600
  done
  [ $rc -eq 0 ] || { echo "$(date +%FT%T) stopping after pcie2 p$arg (exit $rc)"; exit "$rc"; }
done < "$sched"
echo "$(date +%FT%T) run_passes: done"
