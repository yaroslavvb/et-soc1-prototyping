#!/bin/bash
# counts-e214: run one of this lane's inner scripts as ONE slot job with no device node visible:
#   bash run_slot.sh <step tag> <inner script> [args...]
# waits (bounded, 8 min) while the 1-minute load is above 6 or the quiet-desk flag stands; then bash W/slot.sh bash W/nodev.sh bash <inner>.
# Logs the step, its start and end clock and its rc in logs/progress.txt.
set -u
. <W>/out/counts-e214/scripts/env.sh
tag=${1:?tag}; shift
inner=${1:?inner script}; shift
wait_clear 480 || { echo "$(ts) load $(load1) or the quiet-desk flag did not clear in 8 min: not started"; plog "$tag not started (load/flag) rc=9"; exit 9; }
t0=$(ts)
echo "$t0 $tag: slot job start; load $(load1)"
bash "$W/slot.sh" bash "$W/nodev.sh" bash "$inner" "$@"
rc=$?
echo "$(ts) $tag: slot job end rc $rc; load $(load1)"
plog "$tag (slot job from $t0) rc=$rc"
exit $rc
