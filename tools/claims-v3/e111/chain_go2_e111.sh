#!/usr/bin/env bash
# E111 amendments A2 and A3: wait on aifoundry2 (until 18:00 PST at most) for the first queue's queue_end, then start the second queue
# (W1B, END2, CAM) with the card minutes the first used. Detached; opens no device itself. Usage, from the lab checkout:
#     setsid nohup bash tools/claims-v3/e111/chain_go2_e111.sh > build/e111/chain.out 2>&1 < /dev/null &
set -u
ROOT="$HOME/claude/et-soc1-prototyping"; B="$ROOT/build/e111"
deadline=$(date -d 'today 18:00' +%s)
while [ "$(date +%s)" -lt "$deadline" ]; do
  if grep -q '"kind": "queue_end"' "$B/runs/queue.jsonl" 2>/dev/null && ! pgrep -f "queue_e111.py --schedule $B/schedule.json" > /dev/null; then
    cmb=$(python3 "$ROOT/tools/claims-v3/e111/first_queue_min_e111.py" "$B/runs/queue.jsonl")
    echo "$(date '+%T %Z') the first queue ended, card minutes $cmb: go2"
    bash "$ROOT/tools/claims-v3/e111/run_e111.sh" go2 "$cmb"
    exit 0
  fi
  sleep 20
done
echo "$(date '+%T %Z') 18:00 PST reached: no second queue"
