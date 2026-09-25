#!/usr/bin/env bash
# Run the version-3 blocks of one card in schedule order, unattended:
#   setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-<card>.txt > build/claims-v3/queue-<card>.log 2>&1 < /dev/null &
# Each schedule line is "<exp> <pass>" (blank lines and # comments skipped); "sleep <s>" pauses; "end" stops the
# queue. The file is re-read before every block, so lines can be appended while the queue runs; when it runs out of
# lines before an "end", it waits (up to 3 h) for more.
# Before every block it waits until no other user is logged in and no device process is running; a block that
# finds someone else on the card exits 3 and is retried after a wait. A block that fails is logged and skipped
# (its pass can be re-run by listing it again: the failed attempt is kept aside). Stop with: touch build/claims-v3/STOP
set -u
sched=${1:?schedule file}
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
. tools/claims-v3/lib.sh
mkdir -p "$DATA_ROOT"
STATE=$DATA_ROOT/queue-state.jsonl
log "queue starts: $sched"
i=0; idle=0
while :; do
  [ -e build/claims-v3/STOP ] && { log "STOP file present: queue stops"; break; }
  line=$(grep -v '^\s*\(#\|$\)' "$sched" | sed -n "$((i + 1))p")
  if [ -z "$line" ]; then
    idle=$((idle + 60)); [ $idle -ge 10800 ] && { log "no new lines for 3 h: queue stops"; break; }
    sleep 60; continue
  fi
  idle=0; i=$((i + 1))
  read -r exp pass <<< "$line"
  [ "$exp" = end ] && break
  if [ "$exp" = sleep ]; then sleep "$pass"; continue; fi
  if [ -e "$DATA_ROOT/$exp/p$pass/block.json" ] && grep -q '"status":"ok"' "$DATA_ROOT/$exp/p$pass/block.json"; then
    log "skip $exp p$pass (done)"; continue
  fi
  # a failed or interrupted earlier attempt: keep it aside, never mix it into the pass
  [ -d "$DATA_ROOT/$exp/p$pass" ] && mv "$DATA_ROOT/$exp/p$pass" "$DATA_ROOT/$exp/p$pass.attempt-$(date +%s)"
  for try in 1 2 3 4 5 6; do
    wait_free 7200 || { log "card busy for 2 h: giving up on $exp p$pass"; break; }
    t0=$(now_ms)
    bash "tools/claims-v3/$exp/block.sh" "$pass" < /dev/null
    rc=$?
    echo "{\"exp\":\"$exp\",\"pass\":$pass,\"try\":$try,\"rc\":$rc,\"t0_ms\":$t0,\"t1_ms\":$(now_ms)}" >> "$STATE"
    if [ $rc -eq 3 ]; then
      log "$exp p$pass: someone else on the card, retry in 10 min"
      [ -d "$DATA_ROOT/$exp/p$pass" ] && mv "$DATA_ROOT/$exp/p$pass" "$DATA_ROOT/$exp/p$pass.attempt-$(date +%s)"
      sleep 600; continue
    fi
    [ $rc -ne 0 ] && log "$exp p$pass failed (rc $rc)"
    break
  done
  sleep 20
done
log "queue ends: $sched"
