#!/usr/bin/env bash
# E116 (Q133): the card session on aifoundry3 card 0, detached on the box after the claim is posted (run from ~/aifoundry):
#
#   setsid nohup bash tools/claims-v3/e116/session_e116.sh > build/e116/session.out 2>&1 < /dev/null &
#
# 1. et-who and the opening `ettelem config` (read only, under the card lock, timeout 10);
# 2. the read-back, pass 11602 (block_readback_e116.sh: 22 launches of n = 199,874 ops, one per E88 tile, C dumped and
#    compared with accum.c's frozen words). A failed read is recorded and the session goes on: the power passes do not
#    depend on it;
# 3. the smoke, pass 11601 (block_e88.sh --smoke, unchanged: anchor_pi, fp32.zeros, fp32.r_abs, fp32.r_walk,
#    fp16.r_cancel, int8.r_cancel at the current reading, 2 s each), and its gate (every launch ok, 600 MHz, cycles per op
#    546 / 546 / 318); no measured pass starts if the gate fails;
# 4. the registered passes, queue_e88.sh unchanged from 11610, at most 7, with E88_BUDGET_MIN = min(34, 38 - the minutes
#    since this session started) and E88_DEADLINE 18:55, so the whole session stays inside 40 card-minutes and ends by
#    19:00 PST;
# 5. the closing `ettelem config` and et-who.
# Nothing is set: no governor, TDP, threshold or clock write, no reset, no --reset-ms, no PMIC command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/e116
LOG=build/e116/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 400 "$1")"
}
t_start=$(date +%s)
say "session start"
et-who >> "$LOG" 2>&1
cfg build/e116/config-session-start.json
date --iso-8601=seconds > build/e116/session-start.time
say "read-back 11602 starts"
bash tools/claims-v3/e116/block_readback_e116.sh 11602 >> build/e116/readback.log 2>&1 < /dev/null; rc=$?
say "read-back rc=$rc: $(tail -1 build/e116/readback.log)"
say "smoke 11601 starts"
bash tools/claims-v3/rpath/block_e88.sh 11601 --smoke >> build/e116/smoke.log 2>&1 < /dev/null; rc=$?
say "smoke rc=$rc"
gate=$(python3 - <<'PYEOF'
import json, glob
d = "build/claims-v3/aifoundry3/rpath-smoke/p11601"
try:
    rr = [json.loads(l) for l in open(d + "/runs.jsonl")]
    blk = open(d + "/block.json").read()
except Exception as e:
    print("FAIL no smoke data:", e); raise SystemExit
want = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
rr = [r for r in rr if r.get("launch", 0) >= 0]
bad = [r["item"] for r in rr if not r.get("ok") or abs(float(r.get("cycles_per_op", 0)) - want.get(r.get("type"), -1)) > 1.0]
mhz = sorted({round(float(r.get("ghz") or 0) * (1000 if float(r.get("ghz") or 0) < 10 else 1)) for r in rr})
items = sorted({r["item"] for r in rr})
ok = '"status":"ok"' in blk and not bad and len(items) >= 6 and mhz and all(550 <= g <= 650 for g in mhz)
print(("PASS" if ok else "FAIL"), "items", len(items), "bad", bad[:6], "MHz", mhz)
PYEOF
)
say "smoke gate: $gate"
if [ "${gate%% *}" = PASS ]; then
  el=$(( ($(date +%s) - t_start) / 60 ))
  b=$((38 - el)); [ $b -gt 34 ] && b=34
  say "queue starts: passes 11610.., budget $b card-min, deadline 18:55"
  E88_BUDGET_MIN=$b E88_DEADLINE=18:55 bash tools/claims-v3/rpath/queue_e88.sh 11610 7 > build/e116/queue.log 2>&1 < /dev/null
  say "queue rc=$?: $(tail -1 build/e116/queue.log)"
else
  say "smoke gate failed: no measured pass"
fi
cfg build/e116/config-session-end.json
et-who >> "$LOG" 2>&1
say "session end ($(( ($(date +%s) - t_start) / 60 )) min)"
