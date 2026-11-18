#!/bin/bash
# fix-v31counts step 12 (inner; one slot job): the tables rebuilt again with the e37 note's final text (s04; the numbers are those of the
# 06:16 run), their diff against v31-counts' published tables (s05), the e37 bound file (s11, after s10's two points), and the re-count's
# comparison (s03's output) copied into counts/ under its landed name. Desk arithmetic only; no device; nothing committed.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
echo "start $(ts)"
$PY "$L/scripts/s04_tables.py" "$L" > "$L/logs/s04_tables_2.log" 2>&1 || { echo "s04 rc $?"; cat "$L/logs/s04_tables_2.log"; exit 4; }
head -n 1 "$L/logs/s04_tables_2.log"
$PY "$L/scripts/s05_diff.py" "$L" || { echo "s05 rc $?"; exit 5; }
$PY "$L/scripts/s11_e37_compare.py" "$L" "$VV" || { echo "s11 rc $?"; exit 6; }
cp -p "$L/work/recount-compare.json" "$L/counts/recount-S2-real_blind4-check.json" || exit 7
cp -p "$L/work/recount-compare.txt" "$L/counts/recount-S2-real_blind4-check.txt" || exit 7
echo "end $(ts)"
