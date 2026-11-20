#!/bin/bash
# decl-e217 (Q228) step 4f: COUNTS-FROZEN.txt, the counts' freeze line (counts-e217 and group S's nominal energy with them), for the orchestrator
# to post on the Discussion. Reads only this lane's files and out/orch/e217-releases.txt; writes COUNTS-FROZEN.txt once (refuses to overwrite).
set -u
. <W>/out/decl-e217/scripts/env.sh
F=$L/COUNTS-FROZEN.txt
[ -e "$F" ] && { echo "COUNTS-FROZEN.txt exists: not overwritten"; exit 4; }
C=$L/cnt/counts
[ -s "$C/counts-fp32-gemm-states.json" ] && [ -s "$C/counts-fp16-int8-launch.json" ] || { echo "counts tables missing"; exit 3; }
cd "$L" || exit 2
NREL=$(grep -c '^#13' "$W/out/orch/e217-releases.txt")
LASTREL=$(grep '^#13' "$W/out/orch/e217-releases.txt" | tail -1 | cut -c1-60)
{
  echo "decl-e217 (round Q228) step 4: counts-e217, the switch counts of E217's 21 new tile kinds, FROZEN at $(ts), made from the kit's tile files alone (no E217 measurement read)."
  echo "Bench: rtl-sim/fma_toggle_v2 at GitHub main 8bde0182, Verilator 5.042 (-j 2, make -j 1), one bench process, inside slot.sh + nodev.sh; counts-e214's scripts and rules."
  echo "Re-count first: $(grep -o 'VERDICT: [A-Z ]*' cnt/logs/s06b.out 2>/dev/null | head -1) (two committed MM1-v3.1 rows of 3e8991d0 in each footing; cnt/counts/recount-check.json)."
  echo "each count (sha256, file, the time its bench run ended):"
  t1=$(grep -m1 'S1 counted' cnt/logs/s07.out | cut -c1-28)
  t2=$(grep -m1 'S2 counted' cnt/logs/s07.out | cut -c1-28)
  t3=$(sed -n 's/.*run_kinds rc \([0-9]*\); end \(.*\)/rc \1, \2/p' cnt/logs/s08.out | head -1)
  echo "$(sha256sum cnt/work/counts/new-fp32-S1.json | cut -c1-64)  cnt/work/counts/new-fp32-S1.json  (fp32 at S1, 10 kinds x 4 points; ended ${t1})"
  echo "$(sha256sum cnt/work/counts/new-fp32-S2.json | cut -c1-64)  cnt/work/counts/new-fp32-S2.json  (fp32 at S2, 10 kinds x 4 points; ended ${t2})"
  echo "$(sha256sum cnt/work/counts/new-launch.json | cut -c1-64)  cnt/work/counts/new-launch.json  (fp16 5 and int8 6 tiles x 3 launch points; ${t3})"
  echo "the tables (the models' row form) and their sums:"
  sha256sum cnt/counts/counts-fp32-gemm-states.json cnt/counts/counts-fp16-int8-launch.json cnt/counts/counts-e217.csv cnt/counts/counts-e217-tiles.csv
  [ -s cnt/counts/SHA256SUMS ] && echo "$(sha256sum cnt/counts/SHA256SUMS | cut -c1-64)  cnt/counts/SHA256SUMS"
  echo "group S's nominal energy with the counts (the declaration's section h):"
  sha256sum forecasts-nominal-e217-counts.csv forecasts-nominal-e217-counts.json
  echo "the makers: $(sha256sum scripts/s04c_nominal_counts.py | cut -c1-64) scripts/s04c_nominal_counts.py"
  echo "The freeze before it: FROZEN.txt $(sha256sum FROZEN.txt | cut -c1-64) (declaration 099806dc... / 633d7256..., nominal forecasts 4725efa3... / 611ca08d..., 11:37:53 PST)."
  echo "State at this freeze: out/orch/e217-releases.txt holds ${NREL} post lines (the last: '${LASTREL}...')."
  echo "Label (the declaration's section g): group S's switch-route energy is BLIND for a session whose first datum comes after this file is posted; UNREAD for one whose first datum precedes the post if no lab lane had read its data first; else POST-READ (REPORTED)."
} > "$F"
cat "$F"
echo "COUNTS-FROZEN.txt sha256 $(sha256sum "$F" | cut -c1-64)"
