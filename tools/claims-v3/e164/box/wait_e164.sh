#!/usr/bin/env bash
# E164: one bounded wait on the session (at most 540 s), repeated as needed; it never touches the card. From the Intel:
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e164/box/wait_e164.sh
cd ~/nekko || exit 1
LIM=${LIM:-520}; t=0
while [ $t -lt "$LIM" ]; do
  grep -q 'session end' build/e164/session.log 2>/dev/null && break
  sleep 15; t=$((t + 15))
done
date '+%T %Z'
tail -n 14 build/e164/session.log 2>/dev/null | cut -c1-300
echo "== queue"; tail -n 6 build/e164/queue.out 2>/dev/null
echo "== latest run.log"; f=$(ls -t build/claims-v3/aifoundry1-c1/e164*/p*/run.log 2>/dev/null | head -1); echo "$f"; tail -n 3 "$f" 2>/dev/null | cut -c1-250
