#!/usr/bin/env bash
# E174: one bounded wait on the queue (at most 520 s by the box's clock, v3's fault 9), repeated as needed; it never touches the card. From the Intel
# (box/step_e174.sh wait):
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e174/box/wait_e174.sh
# It ends early when build/e174/runs/status.json reads "ended" or "halted". It prints the queue's last records (counts and verdicts only).
# SPDX-License-Identifier: Apache-2.0
cd ~/nekko || exit 1
LIM=${LIM:-520}
while [ "$SECONDS" -lt "$LIM" ]; do
  grep -q '"state": "\(ended\|halted\)"' build/e174/runs/status.json 2>/dev/null && break
  sleep 15
done
date '+%T %Z'
echo "== status: $(cut -c1-300 build/e174/runs/status.json 2>/dev/null)"
echo "== queue (last records)"; tail -n 8 build/e174/runs/queue.jsonl 2>/dev/null | cut -c1-300
[ -e build/e174/runs/QUEUE-HALT ] && { echo "== QUEUE-HALT"; cut -c1-300 build/e174/runs/QUEUE-HALT; }
f=$(ls -t build/e174/runs/*/run.log 2>/dev/null | head -1); echo "== latest run.log: ${f:-none}"; [ -n "$f" ] && tail -n 3 "$f" | cut -c1-250
