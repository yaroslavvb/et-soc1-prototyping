#!/usr/bin/env bash
# E95 amendment A1 (tools/claims-v3/kinds/E95.md, "Amendments"): when the queue of passes 9510-9513 has ended cleanly, run
# pass 9514 with queue_e95.sh, unchanged, if it would end inside 48 card-minutes of the claim. Detached on the box:
#
#   setsid nohup bash tools/claims-v3/kinds/chain_e95_a1.sh > build/e95-chain.log 2>&1 < /dev/null &
#
# It opens no device itself. A clean end is the queue log's last line "queue done: 4 passes"; anything else, or a STOP
# file, and it starts nothing.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
CLAIM_EPOCH=1793522146                  # the claim, 2026-11-01T08:35:46Z
LIMIT=$((CLAIM_EPOCH + 48 * 60))
PASS_S=540                              # pass 9510 took 509 s; a margin
while pgrep -f '[q]ueue_e95.sh 9510 4' > /dev/null; do sleep 5; done
last=$(tail -1 build/e95-queue.log)
echo "$(date -Is) the queue of 9510-9513 ended: $last"
case "$last" in *"queue done: 4 passes"*) ;; *) echo "$(date -Is) it did not run all four: no pass 9514"; exit 0 ;; esac
sleep 15
for f in build/claims-v3/STOP build/kinds-STOP; do [ -e "$f" ] && { echo "$(date -Is) $f exists: no pass 9514"; exit 0; }; done
if [ $(($(date +%s) + PASS_S)) -gt "$LIMIT" ]; then echo "$(date -Is) pass 9514 would end past 48 card-minutes: not started"; exit 0; fi
exec bash tools/claims-v3/kinds/queue_e95.sh 9514 1
