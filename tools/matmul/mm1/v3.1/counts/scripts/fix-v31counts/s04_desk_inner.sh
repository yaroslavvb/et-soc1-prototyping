#!/bin/bash
# fix-v31counts steps 3-5 (inner; one slot job): the re-count's comparison (s03), the tables rebuilt (s04) and their diff against v31-counts'
# published tables (s05). Desk arithmetic only; no device; nothing committed.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
echo "start $(ts)"
$PY "$L/scripts/s03_compare.py" "$L" "$VV" > "$L/logs/s03_compare.log" 2>&1 || { echo "s03 rc $?"; cat "$L/logs/s03_compare.log"; exit 3; }
$PY "$L/scripts/s04_tables.py" "$L" || { echo "s04 rc $?"; exit 4; }
$PY "$L/scripts/s05_diff.py" "$L" || { echo "s05 rc $?"; exit 5; }
echo "end $(ts)"
