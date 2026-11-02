#!/usr/bin/env bash
# E116 amendment A1 (AMENDMENT-A1.md): one more measured pass after the session's queue, inside the registered 40
# card-minutes. Started detached on aifoundry3 (from ~/aifoundry) while the queue runs; it waits for the session's end:
#
#   setsid nohup bash tools/claims-v3/e116/extra_e116.sh > build/e116/extra.out 2>&1 < /dev/null &
#
# It runs block_e88.sh (unchanged) for the next pass number only if fewer than five passes ended ok, the projected end
# (now + the longest pass + 30 s) is at most the session's start + 39 min and before 18:55, and no STOP file exists. Then a
# read-only `ettelem config` under the lock (timeout 10) and et-who. Nothing is set: no knob, no --reset-ms, no PMIC command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
LOG=build/e116/session.log
say() { echo "$(date '+%F %T %Z') A1: $*" >> "$LOG"; }
t0=$(date -d "$(cat build/e116/session-start.time)" +%s)
say "waiting for the session's end"
until grep -q "session end" "$LOG"; do
  sleep 5
  [ $(( $(date +%s) - t0 )) -gt 2400 ] && { say "the session did not end within 40 min of its start: no extra pass"; exit 0; }
done
R=build/claims-v3/aifoundry3/rpath
read -r n_ok longest last <<< "$(python3 - <<'PYEOF'
import glob, json, os, re
ok, longest, last = 0, 0, 11609
for d in glob.glob("build/claims-v3/aifoundry3/rpath/p116[1-9][0-9]"):
    m = re.search(r"/p(\d+)$", d)
    if not m:
        continue
    last = max(last, int(m.group(1)))
    try:
        b = json.load(open(os.path.join(d, "block.json")))
    except Exception:
        continue
    if b.get("status") == "ok":
        ok += 1
        longest = max(longest, (b["t1_ms"] - b["t0_ms"]) // 1000)
print(ok, longest, last)
PYEOF
)"
now=$(date +%s); el=$((now - t0)); p=$((last + 1))
dl=$(date -d "today 18:55" +%s)
say "passes ok $n_ok, longest ${longest} s, last p$last, elapsed $((el / 60)) min $((el % 60)) s"
if [ "$n_ok" -ge 5 ]; then say "five passes already ok: no extra pass"; exit 0; fi
if [ $((el + longest + 30)) -gt $((39 * 60)) ] || [ $((now + longest + 30)) -gt "$dl" ]; then
  say "p$p would end after the session's start + 39 min or after 18:55: no extra pass"; exit 0
fi
for f in build/claims-v3/STOP build/rpath-STOP; do [ -e "$f" ] && { say "$f exists: no extra pass"; exit 0; }; done
say "p$p starts"
bash tools/claims-v3/rpath/block_e88.sh "$p" >> build/e116/extra.log 2>&1 < /dev/null; rc=$?
say "p$p rc=$rc ($(( ($(date +%s) - now) / 60 )) min)"
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null 2>/dev/null | grep '^{' | tail -1 > build/e116/config-a1-end.json
say "config config-a1-end.json: $(head -c 400 build/e116/config-a1-end.json)"
et-who >> "$LOG" 2>&1
say "end ($(( ($(date +%s) - t0) / 60 )) min since the session's start)"
