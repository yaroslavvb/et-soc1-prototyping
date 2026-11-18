#!/bin/bash
# Q217 v31-trace: negative control on real traces: a run checked against the OTHER kernel's walk must read DIFFERS (one slot job).
#   bash s08_wrong_walk.sh <run name> <wrong kernel> <shape> <mask>
set -u
W=<W>
L=$W/out/v31-trace
R=$L/traces/runs/$1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
bash "$W/slot.sh" /usr/bin/python3 -I -B "$L/traces/check_v31.py" --summary "$R/summary.json.gz" --kernel "$2" --shape "$3" --mask "$4" \
  --out "$R/check-wrongwalk-$2.json" > "$R/check-wrongwalk-$2.out" 2>&1
echo "rc=$?"
/usr/bin/python3 -I -B -c "import json;d=json.load(open('$R/check-wrongwalk-$2.json'));print(d['verdict'], 'exact harts', d['exact_harts'], 'of', d['working_harts_traced'], 'diff positions', d['diff_positions_total'], 'shire steps unequal', {s: v['steps_unequal'] for s, v in d['shires'].items()}, 'chip', d['chip_sharing'], 'first diff', d['per_hart'][[h for h in d['per_hart'] if d['per_hart'][h].get('first_diff')][0]]['first_diff'] if d['diff_harts'] else None)"
