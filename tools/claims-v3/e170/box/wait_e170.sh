#!/usr/bin/env bash
# E170: one bounded wait on the queue (at most 520 s), repeated as needed; it never touches the card. From the Intel (box/step_e170.sh wait):
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e170/box/wait_e170.sh
# It ends early when build/e170/runs/status.json reads "ended" or "halted". It prints the queue's last records (counts and verdicts only).
# SPDX-License-Identifier: Apache-2.0
cd ~/nekko || exit 1
LIM=${LIM:-520}; t=0
while [ $t -lt "$LIM" ]; do
  grep -q '"state": "\(ended\|halted\)"' build/e170/runs/status.json 2>/dev/null && break
  sleep 15; t=$((t + 15))
done
date '+%T %Z'
echo "== status: $(cat build/e170/runs/status.json 2>/dev/null | cut -c1-300)"
echo "== queue (last records)"; tail -n 8 build/e170/runs/queue.jsonl 2>/dev/null | cut -c1-300
[ -e build/e170/runs/QUEUE-HALT ] && { echo "== QUEUE-HALT"; cut -c1-300 build/e170/runs/QUEUE-HALT; }
f=$(ls -t build/e170/runs/*/run.log 2>/dev/null | head -1); echo "== latest run.log: $f"; tail -n 3 "$f" 2>/dev/null | cut -c1-250
