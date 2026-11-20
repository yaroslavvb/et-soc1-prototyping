#!/bin/bash
# blind-e217 step 2b: the forecasts, one model per process, one slot job at a time: lay, v31, v3, v2 at the measured conditions, then the
# nominal self-check of v31, v3, v2 (the same code at the declared nominal conditions; compared with decl-e217's frozen nominal forecasts).
set -u
. <W>/out/blind-e217/scripts/env.sh
for m in lay v31 v3 v2; do
  bash "$L/scripts/run_slot.sh" "step 2b forecasts $m (measured conditions)" "$L/scripts/s02b_forecast.py" "$L" "$m" || exit 1
done
for m in v31 v3 v2; do
  bash "$L/scripts/run_slot.sh" "step 2b nominal self-check $m" "$L/scripts/s02b_forecast.py" "$L" "$m" --nominal || exit 1
done
echo "chain done $(ts)"
