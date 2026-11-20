#!/bin/bash
# counts-e217 (decl-e217 step 4; counts-e214's script) step 9-11 (inner; one slot job): the tables (s09), the zero shares (s10), the scope record and the re-count rule copied into
# counts/, the merge check (s09b), and SOURCES.json (s11). Desk; no device; no bench run.
set -u
. <W>/out/decl-e217/scripts/cnt/env.sh
echo "start $(ts)"
$PY "$W/out/decl-e217/scripts/cnt/s09_tables.py" "$L" || { echo "s09 failed"; exit 5; }
$PY "$W/out/decl-e217/scripts/cnt/s10_zero_share.py" "$L" || { echo "s10 failed"; exit 6; }
cp -p "$L/work/scope-e217.json" "$L/work/scope-e217.txt" "$L/work/recount-rule.txt" "$L/counts/" || exit 7
$PY "$W/out/decl-e217/scripts/cnt/s09b_mergecheck.py" "$L" || { echo "s09b failed"; exit 9; }
$PY "$W/out/decl-e217/scripts/cnt/s11_sources.py" "$L" "$W" || { echo "s11 failed"; exit 8; }
echo "end $(ts)"
