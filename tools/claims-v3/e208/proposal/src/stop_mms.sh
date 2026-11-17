#!/usr/bin/env bash
# 1116-mmsweep: stop a card's session the gentle way: touch its STOP files. The running host sees its --stop-file and ends at
# its next launch boundary (about 0.5 s); the runner starts nothing further and closes the session itself (the sampler
# stopped with SIGTERM, the closing config read, the manifest). No process is killed. Read the result with status_mms.sh.
#   bash ~/claude/work/ee-1116-mmsweep/src/stop_mms.sh <card> [<session id>]
# The kit-wide run/STOP also refuses new sessions on this box until start_mms.sh moves it aside (with no session running).
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${1:-}
case "$CARD" in a2c0|a1c1|a1c0) ;; *) echo "usage: stop_mms.sh a2c0|a1c1|a1c0 [<session id>]"; exit 2 ;; esac
SID=${2:-$(cat "run/current-$CARD" 2>/dev/null)}
mkdir -p run
touch run/STOP && echo "touched run/STOP"
if [ -n "$SID" ] && [ -d "sessions/$SID" ]; then
  touch "sessions/$SID/STOP" && echo "touched sessions/$SID/STOP"
else
  echo "no session directory for '${SID:-<none>}': only run/STOP was touched"
fi
echo "STOP REQUESTED $(TZ=America/Los_Angeles date '+%F %T %Z'); follow it with status_mms.sh $CARD"
