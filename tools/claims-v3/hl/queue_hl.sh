#!/usr/bin/env bash
# V3-HL: run passes <first> .. <first>+<n>-1 of block.sh on the local card, one after another (not lib.sh's queue.sh:
# its wait_free uses lib.sh's others_present, which departure D1 replaces on aifoundry3 and aifoundry1).
#   setsid nohup bash tools/claims-v3/hl/queue_hl.sh <first-pass> <n-passes> <items> > build/hl-queue-<card>.log 2>&1 < /dev/null &
# Stops before the next pass when build/claims-v3/STOP or build/hl-STOP exists, on any pass that fails, and after a
# pass that found another user on the card (exit 3) it waits 10 min and tries that pass once more.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
p=${1:?first pass}; n=${2:?number of passes}; items=${3:?items}
for i in $(seq "$p" $((p + n - 1))); do
  for f in build/claims-v3/STOP build/hl-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: stopping before p$i"; exit 0; }; done
  echo "$(date +%T) p$i starts"
  bash tools/claims-v3/hl/block.sh "$i" "$items" < /dev/null; rc=$?
  echo "$(date +%T) p$i rc=$rc"
  if [ $rc -eq 3 ]; then
    sleep 600
    bash tools/claims-v3/hl/block.sh "$i" "$items" < /dev/null; rc=$?
    echo "$(date +%T) p$i retry rc=$rc"
  fi
  [ $rc -eq 0 ] || { echo "$(date +%T) stopping after p$i (rc $rc)"; exit "$rc"; }
  sleep 15
done
echo "$(date +%T) queue done"
