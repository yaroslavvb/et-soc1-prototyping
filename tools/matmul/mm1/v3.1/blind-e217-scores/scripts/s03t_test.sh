#!/bin/bash
# blind-e217 step 3t: the scorer's code test on two stand-in days (built from the frozen forecasts alone; no E217 measurement), one slot
# job at a time. Outputs in work/step3-standin-<mode>/ (never a result).
set -u
. <W>/out/blind-e217/scripts/env.sh
for m in exact noise; do
  bash "$L/scripts/run_slot.sh" "step 3s stand-in $m" "$L/scripts/s03s_standin.py" "$L" "$L/work/standin/$m" "$m" || exit 1
  bash "$L/scripts/run_slot.sh" "step 3t scorer on the stand-in $m" "$L/scripts/s03_score.py" "$L" --standin "$L/work/standin/$m" || exit 1
done
echo "test done $(ts)"
