#!/bin/bash
# counts-e214 steps 7-8: the new counts, one slot job at a time (each through run_slot.sh: a bounded wait for load <= 6 and no quiet-desk
# flag), only after the re-count check reads MATCH (counts/recount-check.json "pass": true).
set -u
S=<W>/out/counts-e214/scripts
. "$S/env.sh"
$PY "$S/passcheck.py" "$L/counts/recount-check.json" || { echo "re-count check not MATCH: no new count"; exit 20; }
bash "$S/run_slot.sh" "s07 new fp32 counts at GEMM states (9 kinds, S1 and S2, jobs 1)" "$S/s07_fp32_inner.sh" || exit $?
bash "$S/run_slot.sh" "s08 new fp16/int8 counts at the launch points (11 tiles) + the sparse50h cross-check (jobs 1)" "$S/s08_launch_inner.sh" || exit $?
echo "chain done $(ts)"
