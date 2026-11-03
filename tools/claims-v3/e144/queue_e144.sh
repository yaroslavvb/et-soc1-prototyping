#!/usr/bin/env bash
# E144 (Q138): the measured pass on aifoundry3 card 0, detached on the box (session_e144.sh go):
#   setsid nohup bash tools/claims-v3/e144/queue_e144.sh > build/e144/queue.log 2>&1 < /dev/null &
# One pass, 14420, with the design E144_DESIGN (subset unless the gates leave room for the full design) and the deadline
# E144_DEADLINE_EPOCH (23:49 PST, under the round's 23:50 end gate); then the session-end config read through E128's guard.
# It starts nothing when build/claims-v3/STOP or build/e144-STOP exists.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export E144_DESIGN=${E144_DESIGN:-subset}
export E144_DEADLINE_EPOCH=${E144_DEADLINE_EPOCH:-$(date -d '2026-11-02 23:49 PST' +%s)}
for f in build/claims-v3/STOP build/e144-STOP; do [ -e "$f" ] && { echo "$(date +%T) $f exists: nothing started"; exit 0; }; done
echo "$(date +%T) p14420 starts: design $E144_DESIGN, deadline $E144_DEADLINE_EPOCH"
t0=$(date +%s)
bash tools/claims-v3/e144/block_e144.sh 14420 < /dev/null; rc=$?
echo "$(date +%T) p14420 rc=$rc ($(( ($(date +%s) - t0) / 60 )) min)"
flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>build/e144/config-session-end.json.err \
  | grep '^{' | tail -1 > build/e144/config-session-end.json
echo "$(date +%T) session-end config: $(head -c 400 build/e144/config-session-end.json)"
timeout 20 et-who 2>&1 | head -3
echo "$(date +%T) queue done rc=$rc"
exit "$rc"
