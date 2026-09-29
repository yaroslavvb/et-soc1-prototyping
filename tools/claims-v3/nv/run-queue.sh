#!/usr/bin/env bash
# NV's own queue: runs nv/block.sh for each line of an NV schedule, one block at a time, unattended.
#   setsid nohup bash tools/claims-v3/nv/run-queue.sh tools/claims-v3/nv/schedule-<role>-<card>.txt \
#       > build/claims-v3/nv-queue-<card>.log 2>&1 < /dev/null &
# Schedule lines: "nv <pass> [--probe|--smoke]"; "sleep <s>"; "end" stops the queue; blank lines and # comments are
# skipped. The file is re-read before every block.
# Why not tools/claims-v3/queue.sh: on a multi-card host its cooling wait samples the card with the sampler, without
# the card lock and under timeout 20, before its own checks. This runner never opens a device: every device access is
# inside block.sh, under the card lock and timeout -k 3 10, and block.sh checks the temperature itself (exit 3 when the
# die is too warm to start).
# Exit codes of a block: 0 done (or not needed) -> next line; 3 busy or too warm -> the same pass again in 10 min (at
# most 12 tries, then the queue stops); 1 failed -> the next line, unless an ALERT file or a STOP file now exists
# (block.sh wrote it: the queue stops); 2 refused -> the queue stops (a person must look). Stop with a STOP file:
# build/claims-v3/STOP (every queue on the host) or build/claims-v3/<card>/nv/STOP (NV on this card).
set -u
sched=${1:?usage: run-queue.sh <schedule file>}
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
WD=tools/claims-v3/nv
if [ -n "${V3_DRY:-}" ]; then
  CTL=build/claims-v3-dry; RETRY_S=${NV_RUNQ_RETRY_S:-600}; GAP_S=${NV_RUNQ_GAP_S:-20}
  CARD=${NV_DRY_CARD:-aifoundry3}
else
  bad=$(env | grep -o '^NV_\(STUB\|DRY\|RUNQ\)[A-Z_]*' | tr '\n' ' ')
  [ -n "$bad" ] && { echo "run-queue: dry-only variables set without V3_DRY: $bad" >&2; exit 2; }
  CTL=build/claims-v3; RETRY_S=600; GAP_S=20
  CARD=$(hostname)
fi
log() { echo "$(date +%FT%T) [$CARD nv-queue] $*"; }
stopped() { [ -e "$CTL/STOP" ] || [ -e "$CTL/$CARD/nv/STOP" ] || ls "$CTL"/ALERT-NV-*.json > /dev/null 2>&1; }
STATE=$CTL/$CARD/nv/queue-state.jsonl
mkdir -p "$CTL/$CARD/nv"
log "queue starts: $sched"
i=0
while :; do
  stopped && { log "a STOP or ALERT file is present: the queue stops"; break; }
  line=$(grep -v '^\s*\(#\|$\)' "$sched" | sed -n "$((i + 1))p")
  [ -z "$line" ] && { log "the schedule ran out of lines: the queue stops"; break; }
  i=$((i + 1))
  read -r exp pass mode <<< "$line"
  [ "$exp" = end ] && { log "end"; break; }
  if [ "$exp" = sleep ]; then sleep "$pass"; continue; fi
  [ "$exp" = nv ] || { log "not an NV line: '$line': the queue stops"; break; }
  rc=3
  for try in $(seq 1 12); do
    t0=$(date +%s%3N)
    bash "$WD/block.sh" "$pass" ${mode:+"$mode"} < /dev/null
    rc=$?
    echo "{\"pass\":$pass,\"mode\":\"${mode:-full}\",\"try\":$try,\"rc\":$rc,\"t0_ms\":$t0,\"t1_ms\":$(date +%s%3N)}" >> "$STATE"
    [ "$rc" = 3 ] || break
    log "p$pass: busy or too warm (rc 3), again in $RETRY_S s"
    sleep "$RETRY_S"
    stopped && break
  done
  case "$rc" in
    0) ;;
    1) log "p$pass failed (rc 1)" ;;
    2) log "p$pass was refused (rc 2): the queue stops"; break ;;
    3) log "p$pass stayed busy for 12 tries: the queue stops"; break ;;
    *) log "p$pass: unexpected rc $rc: the queue stops"; break ;;
  esac
  sleep "$GAP_S"
done
log "queue ends: $sched"
