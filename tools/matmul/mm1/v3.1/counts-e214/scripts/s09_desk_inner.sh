#!/bin/bash
# counts-e214 step 9-11 (inner; one slot job): the tables (s09), the zero shares (s10), the scope record and the re-count rule copied into
# counts/, the merge check (s09b), and SOURCES.json (s11). Desk; no device; no bench run.
set -u
. <W>/out/counts-e214/scripts/env.sh
echo "start $(ts)"
$PY "$L/scripts/s09_tables.py" "$L" || { echo "s09 failed"; exit 5; }
$PY "$L/scripts/s10_zero_share.py" "$L" || { echo "s10 failed"; exit 6; }
cp -p "$L/work/scope-e214.json" "$L/work/scope-e214.txt" "$L/work/recount-rule.txt" "$L/counts/" || exit 7
$PY "$L/scripts/s09b_mergecheck.py" "$L" || { echo "s09b failed"; exit 9; }
$PY "$L/scripts/s11_sources.py" "$L" "$W" || { echo "s11 failed"; exit 8; }
echo "end $(ts)"
