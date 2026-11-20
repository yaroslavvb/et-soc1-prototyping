#!/bin/bash
# decl-e219: bounded wait (at most 8.5 minutes a call) for the orchestrator's copy of EE/src (W/out/orch/e219-src/COPIED.txt).
# Reads only; exit 0 when COPIED.txt exists, 3 when the bound is reached first.
set -u
W=<W>
F=$W/out/orch/e219-src/COPIED.txt
LOG=$W/out/decl-e219/logs/progress.txt
end=$(( $(date +%s) + 510 ))
while :; do
  if [ -e "$F" ]; then
    echo "$(date '+%a %d %b %Y %H:%M:%S %Z') wait COPIED.txt: present rc=0" >> "$LOG"
    cat "$F"
    exit 0
  fi
  if [ "$(date +%s)" -ge "$end" ]; then
    echo "$(date '+%a %d %b %Y %H:%M:%S %Z') wait COPIED.txt: bound reached (8.5 min), not yet present rc=3" >> "$LOG"
    exit 3
  fi
  sleep 15
done
