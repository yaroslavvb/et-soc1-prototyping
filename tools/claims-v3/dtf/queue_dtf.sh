#!/usr/bin/env bash
# V3-DTF: run passes <first> .. <first>+<n>-1 of block.sh on the local card, one after another (not lib.sh's queue.sh:
# its wait_free uses lib.sh's others_present, which departure D1 replaces on aifoundry3 and aifoundry1).
#   DTF_DUP=<names> setsid nohup bash tools/claims-v3/dtf/queue_dtf.sh <first-pass> <n-passes> <items> [--cam] \
#     > build/dtf-queue-<card>.log 2>&1 < /dev/null &
# Stops before the next pass when build/claims-v3/STOP or build/dtf-STOP exists, and on any pass that fails. A pass
# that found another user on the card (exit 3) is retried up to four times, 10 minutes apart; after that the queue
# moves on to the next pass and says so (README "Protocol").
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}; items=${3:?items}; mode=${4:-}
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/dtf-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  echo "$(date +%T) p$i starts"
  bash tools/claims-v3/dtf/block.sh "$i" "$items" $mode < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc"
  t=0
  while [ $rc -eq 3 ] && [ $t -lt 4 ]; do
    t=$((t + 1)); sleep 600
    for f in build/claims-v3/STOP build/dtf-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping"; exit 0; }; done
    bash tools/claims-v3/dtf/block.sh "$i" "$items" $mode < /dev/null; rc=$?
    echo "$(date +%T) p$i retry $t rc=$rc"
  done
  if [ $rc -eq 3 ]; then echo "$(date +%T) p$i: another user still on the card after 4 retries; moving on"; continue; fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  sleep 15
done
echo "$(date +%T) queue done"
