#!/bin/bash
# v31-trace (Q217): ONE bounded chunk of the wait for aifoundry3 (at most 8 min 30 s): every 60 s read `bash W/book.sh show` and
# `python3 W/out/orch/queue_state.py aifoundry3 e213a`; exit 0 as soon as no aifoundry3 booking is listed AND the queue reads QUEUE OVER
# (and no claim file stands), else exit 1 at the chunk's end. Reads only (book.sh show, queue_state.py, ls); no ssh. Logs to logs/wait.log.
set -u
W=<W>
L=$W/out/v31-trace
end=$(( $(date +%s) + 510 ))
while :; do
  bk=$(bash "$W/book.sh" show 2>&1)
  q=$(python3 "$W/out/orch/queue_state.py" aifoundry3 e213a 2>&1); qrc=$?
  booked=no
  printf '%s\n' "$bk" | grep -qi 'aifoundry3' && booked=yes
  claim=no; [ -e "$W/out/orch/claim-aifoundry3.txt" ] && claim=yes
  line="$(date '+%F %T %Z') booked=$booked claim=$claim queue_rc=$qrc $(printf '%s' "$q" | tail -1) | $(printf '%s' "$q" | head -1 | cut -c1-120)"
  echo "$line" >> "$L/logs/wait.log"
  if [ "$booked" = no ] && [ "$claim" = no ] && [ "$qrc" = 0 ]; then echo "FREE: $line"; exit 0; fi
  [ "$(date +%s)" -ge "$end" ] && { echo "STILL BUSY: $line"; exit 1; }
  sleep 60
done
