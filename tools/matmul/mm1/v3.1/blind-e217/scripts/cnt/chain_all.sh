#!/bin/bash
# counts-e217 (decl-e217 step 4): the rest of the counting chain after the functional check, one slot job at a time (each through run_slot.sh:
# a bounded wait for load <= 6 and no quiet-desk flag; slot.sh + nodev.sh), in counts-e214's order: the re-count rule (hashed before any
# re-count), the maps, the re-count of two committed rows, the comparison (MATCH or stop), the new fp32 counts, the new launch-point counts,
# then the tables. Each step's output in cnt/logs/<step>.out. Stops at the first failure.
set -u
S=<W>/out/decl-e217/scripts/cnt
. "$S/env.sh"
LG=$L/logs
grep -q 'fcheck rc 0' "$LG/s04.out" || { echo "$(ts) the functional check did not read rc 0: stop"; plog "chain: fcheck not rc 0, nothing counted rc=20"; exit 20; }
$PY "$S/s06a_recount_rule.py" "$L" > "$LG/s06a.out" 2>&1 || { plog "s06a re-count rule failed rc=21"; exit 21; }
plog "s06a re-count rule written and hashed before any re-count: $(grep -o 'sha256 [0-9a-f]*' "$LG/s06a.out") rc=0"
bash "$S/run_slot.sh" "s05 net maps trained on this binary (train_maps.py, jobs 1)" "$S/s05_maps_inner.sh" > "$LG/s05.out" 2>&1 || exit 22
bash "$S/run_slot.sh" "s06 re-count two committed v3.1 rows (fp32 fld_mant S1, den8 S2; int8 i8_pm1, fp16 fld16_mant at the launch points; jobs 1)" \
  "$S/s06_recount_inner.sh" > "$LG/s06.out" 2>&1 || exit 23
$PY "$S/s06b_compare.py" "$L" > "$LG/s06b.out" 2>&1
rc=$?
plog "s06b re-counts vs committed v3.1 rows: $(grep -o 'VERDICT: [A-Z ]*' "$LG/s06b.out" | head -1) rc=$rc"
[ "$rc" -eq 0 ] || { echo "re-count NO MATCH: no new count"; exit 24; }
$PY "$S/passcheck.py" "$L/counts/recount-check.json" || { echo "re-count check not MATCH: no new count"; exit 25; }
bash "$S/run_slot.sh" "s07 new fp32 counts at GEMM states (10 kinds, S1 and S2, jobs 1)" "$S/s07_fp32_inner.sh" > "$LG/s07.out" 2>&1 || exit 26
bash "$S/run_slot.sh" "s08 new fp16/int8 counts at the launch points (11 tiles, jobs 1)" "$S/s08_launch_inner.sh" > "$LG/s08.out" 2>&1 || exit 27
bash "$S/run_slot.sh" "s09-s11 tables, zero shares, merge check, SOURCES.json" "$S/s09_desk_inner.sh" > "$LG/s09.out" 2>&1 || exit 28
echo "chain done $(ts)"
