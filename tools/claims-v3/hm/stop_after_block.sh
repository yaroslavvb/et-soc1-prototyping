#!/usr/bin/env bash
# E62: touch a session's STOP file as soon as the named block logs its block_end, so the session ends cleanly in the
# gap before the next block (the runner's guard sees STOP, ends the session and releases the card). Usage, on
# aifoundry2:  bash stop_after_block.sh <rundir> <block id> [max seconds]
set -u
R=${1:?usage: stop_after_block.sh <rundir> <block id> [max s]}
B=${2:?block id}
MAX=${3:-1800}
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt "$MAX" ]; do
  if grep -q "\"kind\": \"block_end\", \"detail\": \"$B:" "$R/marks.jsonl" 2>/dev/null; then
    touch "$R/STOP"
    echo "STOP touched at $(date +%T) after $B ended"
    exit 0
  fi
  if [ -e "$R/session.json" ]; then
    echo "the session ended before $B did"
    exit 1
  fi
  sleep 0.5
done
echo "timed out after $MAX s"
exit 2
