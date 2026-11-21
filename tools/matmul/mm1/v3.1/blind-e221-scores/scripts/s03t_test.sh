#!/bin/bash
# blind-e221 (Q235) step 3t: the scorer's code test on two stand-in days built from the frozen forecasts alone (no E221 measurement):
# exact (MM1-v3.2's errors 0 by construction) and noise (seeded noise, capped runs, queue failures). Each step one slot job, in turn.
set -u
. <WF>/out/blind-e221/scripts/env.sh
for n in exact noise; do
  bash "$L/scripts/run_slot.sh" "step 3s stand-in $n" "$L/scripts/s03s_standin.py" "$L" "$n" > "$L/logs/s03s-standin-$n.log" 2>&1 || { echo "stand-in $n rc $?"; exit 1; }
  bash "$L/scripts/run_slot.sh" "step 3t scorer on the stand-in $n" "$L/scripts/s03_score.py" "$L" --standin "$L/work/standin/$n" > "$L/logs/s03t-score-standin-$n.log" 2>&1
  echo "scorer on stand-in $n rc $?"
done
