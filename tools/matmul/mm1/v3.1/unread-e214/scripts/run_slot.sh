#!/bin/bash
# unread-e214: run one numerical step as ONE slot job (THE CPU RULE: single-threaded, nice 10, one slot job of this lane at a time),
# after a bounded wait (8 min at most) while the 1-minute load is above 6. Logs start, end and rc in logs/progress.txt.
#   bash run_slot.sh <step tag> <python script> [args...]
set -u
. <W>/out/unread-e214/scripts/env.sh
tag=${1:?tag}; shift
script=${1:?script}; shift
wait_load 480 || { echo "$(ts) load $(load1) above 6 for 8 min: $tag not started"; plog "$tag not started (load) rc=9"; exit 9; }
t0=$(ts)
echo "$t0 $tag: slot job start; load $(load1)"
bash "$W/slot.sh" "$PY" -I -B "$script" "$@"
rc=$?
echo "$(ts) $tag: slot job end rc $rc; load $(load1)"
plog "$tag (slot job from $t0; load $(load1)) rc=$rc"
exit $rc
