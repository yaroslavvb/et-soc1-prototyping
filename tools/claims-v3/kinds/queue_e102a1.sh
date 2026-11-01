#!/usr/bin/env bash
# E102 amendment A1 (E102.md, "Amendments"): the added blocks on aifoundry1 card 1, one after another, inside A1's budget. 10213 runs through the registered block_e102.sh, unchanged; 10214 and the R blocks through block_e102a1.sh.
#
#   setsid nohup bash tools/claims-v3/kinds/queue_e102a1.sh > build/e102a1-queue.log 2>&1 < /dev/null &
#
# It projects each block's end from its estimate (G 345 s, short G 125 s, R 105 s) and does not start a block that would pass E102A1_BUDGET_S seconds from the queue's start (860 s: with the smoke and the config reads, A1's 15 card-minutes), so the last R
# blocks go first. A block in flight is never cut. It stops before the next block on build/claims-v3/STOP or build/kinds-STOP and after any block that fails. Another user on the card (exit 3): it stops and says so; A1 has no time for a retry.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
BUDGET_S=${E102A1_BUDGET_S:-860}
t_start=$(date +%s); done_n=0
deadline=$(date -d '2026-11-01 07:00 PST' +%s)
run() {   # <pass> <script> <estimate s>
  local p=$1 s=$2 e=$3 now el t0 rc
  for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$p"; exit 0; }; done
  now=$(date +%s); el=$((now - t_start))
  if [ $((el + e)) -gt "$BUDGET_S" ] || [ $((now + e)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (elapsed $el s, estimate $e s, $done_n blocks done)"; exit 0
  fi
  echo "$(date +%T) p$p starts (elapsed $el s)"
  t0=$(date +%s)
  bash "tools/claims-v3/kinds/$s" "$p" < /dev/null; rc=$?
  echo "$(date +%T) p$p rc=$rc ($(( $(date +%s) - t0 )) s)"
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; exit "$rc"; }
  done_n=$((done_n + 1))
  sleep 5
}
echo "$(date +%T) queue: E102 A1, budget ${BUDGET_S} s, deadline 2026-11-01 07:00 PST"
run 10213 block_e102.sh 345
run 10214 block_e102a1.sh 125
run 10240 block_e102a1.sh 105
run 10241 block_e102a1.sh 85
run 10242 block_e102a1.sh 85
run 10243 block_e102a1.sh 85
echo "$(date +%T) queue done: $done_n blocks, $(( $(date +%s) - t_start )) s"
