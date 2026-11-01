#!/usr/bin/env bash
# E100 on aifoundry2: wait for the slot, look, smoke, run. Started detached; needs nothing from outside once it runs.
#   setsid nohup bash build/e100/code/go_e100.sh > build/e100/go.log 2>&1 < /dev/null &
# It launches nothing before the slot's start, keeps inside its end (run_e100.py enforces that per run and per process), never waits on a person, and posts nothing:
# the night's Discord claim is E98's lane's. Nothing is set on the card.
set -u
ROOT=$HOME/claude/et-soc1-prototyping
CODE=$ROOT/build/e100/code
RUNS=$ROOT/build/e100/runs
SLOTS=$HOME/claude/work/q132-a2-slots.txt
LOCK=/run/lock/etsoc-shire0.lock
say() { echo "$(date '+%F %T %Z') $*"; }
cd "$ROOT" || exit 2
mkdir -p "$RUNS"
line=$(grep -E '^SLOT E100:' "$SLOTS" | head -1)
START=$(echo "$line" | sed -E 's/.*start ([0-9]+).*/\1/')
END=$(echo "$line" | sed -E 's/.*end ([0-9]+).*/\1/')
case "$START$END" in *[!0-9]*|"") say "no E100 slot in $SLOTS: nothing launched"; exit 2;; esac
say "slot $START to $END"
now=$(date +%s)
[ "$now" -lt "$END" ] || { say "the slot has passed: nothing launched"; exit 2; }
sleep $(( START > now ? START - now : 0 ))
# look first: a probe may still be running; wait with bounded polls for the card, inside the slot only
LIMIT=$(( END - 300 ))
while :; do
  now=$(date +%s)
  if [ "$now" -ge "$LIMIT" ]; then say "the card was not free by $LIMIT: nothing launched"; exit 3; fi
  who_out=$(timeout 20 et-who 2>/dev/null | head -3)
  if flock -n "$LOCK" true && echo "$who_out" | grep -q 'No process holds'; then break; fi
  say "card busy, waiting: $(python3 -c "import json;d=json.load(open('build/e98/runs/status.json'));print(d.get('state') or d)" 2>/dev/null | cut -c1-80)"
  sleep 15
done
say "card free; status: $(python3 -m json.tool build/e98/runs/status.json 2>/dev/null | tr -d '\n ' | cut -c1-200)"
export E100_ROOT=$ROOT
PY=python3
say "smoke"
$PY "$CODE/run_e100.py" --protocol "$CODE/protocol.json" --out "$RUNS/smoke" --only SMOKE --slot-start "$START" --slot-end "$END"
rc=$?
say "smoke exit $rc"
if [ "$rc" -ne 0 ]; then say "smoke failed: the session is not started"; touch "$RUNS/SMOKE_FAILED"; exit 4; fi
$PY "$CODE/smoke_ok.py" "$RUNS/smoke"
rc=$?
if [ "$rc" -ne 0 ]; then say "the smoke's check failed: the session is not started"; touch "$RUNS/SMOKE_FAILED"; exit 4; fi
say "session"
$PY "$CODE/run_e100.py" --protocol "$CODE/protocol.json" --out "$RUNS/s1" --slot-start "$START" --slot-end "$END"
rc=$?
say "session exit $rc"
timeout 20 et-who 2>/dev/null | head -3 | cut -c1-100
echo "$rc" > "$RUNS/DONE"
