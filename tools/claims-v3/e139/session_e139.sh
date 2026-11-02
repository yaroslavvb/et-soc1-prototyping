#!/usr/bin/env bash
# E139: the card session on aifoundry3 card 0, detached on the box after the day's post carries the claim (run from ~/aifoundry):
#
#   setsid nohup bash tools/claims-v3/e139/session_e139.sh > build/e139/session.out 2>&1 < /dev/null &
#
# A port of tools/claims-v3/e132/session_e132.sh; marked changes: pass numbers (smoke 13901), log dir build/e139, MF_GEN=build/e139-gen,
# MF_EXPN=e139, MF_MAX_C=70, the board-power watcher (watch_e139.py, reads telemetry files only), the queue's deadline = this session's
# start + 42 min capped at 21:40 PST, and a refusal to start after 21:00 PST. 1. et-who and the opening `ettelem config` (read only,
# under the card lock, timeout 10); 2. the smoke 13901; 3. E110's smoke gate, unchanged; 4. the passes; 5. the closing config and et-who.
# Nothing is set. A failed gate runs no pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/e139
LOG=build/e139/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
t_start=$(date +%s)
latest_start=$(TZ=America/Los_Angeles date -d "${E139_DAY:-2026-11-02} 21:00" +%s)
cap=$(TZ=America/Los_Angeles date -d "${E139_DAY:-2026-11-02} 21:40" +%s)
if [ "$t_start" -gt "$latest_start" ]; then say "refused: after 21:00 PST, no session starts"; exit 9; fi
dl=$((t_start + 42 * 60)); [ "$dl" -gt "$cap" ] && dl=$cap
export E139_DEADLINE_S=$dl
rm -f build/e139/session-end.time
say "session start (queue deadline $(date -d @"$E139_DEADLINE_S" '+%T %Z'))"
et-who >> "$LOG" 2>&1
cfg build/e139/config-session-start.json
date --iso-8601=seconds > build/e139/session-start.time
export MF_GEN=$PWD/build/e139-gen MF_EXPN=e139 MF_ENERCAT=build/enercat-e99/host/enercat_host MF_MAX_C=70
python3 tools/claims-v3/e139/watch_e139.py --root "build/claims-v3/$(hostname)/e139" --stop-w 65 --max-s 3000 >> build/e139/watch.log 2>&1 &
WPID=$!
bash tools/claims-v3/mf/block.sh 13901 anchor_pi,ab_4,ab_rnd,eh_64,c3_128 < /dev/null > build/e139/smoke.log 2>&1; rc=$?
say "smoke rc=$rc"
python3 tools/claims-v3/e110/smoke_gate_e110.py "build/claims-v3/$(hostname)/e139/p13901" anchor_pi,ab_4,ab_rnd,eh_64,c3_128 >> "$LOG" 2>&1; g=$?
if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ] || [ -e build/e139-STOP ]; then
  say "smoke gate failed or a stop is set (block rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e139/queue_e139.sh < /dev/null > build/e139/queue.out 2>&1
  say "queue: $(tail -1 build/e139/queue.out)"
fi
cfg build/e139/config-session-end.json
date --iso-8601=seconds > build/e139/session-end.time
sleep 2; kill "$WPID" 2>/dev/null
et-who >> "$LOG" 2>&1
say "session end"
