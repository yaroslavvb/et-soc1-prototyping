#!/bin/bash
# v31-counts step 6 (inner; inside W/slot.sh + W/nodev.sh): before any new count, re-count committed points and compare:
#  (1) fp32 at a GEMM's accumulator states: E210's S1 random row (gemmL1x1x1, j = 3, 11, 19, 27 of 32 ops, tiles 0 and 1 of the 61 desk-only
#      randn tiles that make_tiles_e210.sh draws with rgm136's own drawTile, seeded 'E210-desk|randn|fp32'), by E210's committed
#      count_e210.py unchanged -> against tools/claims-v3/e210/desk/counts-e210-S1.json's randn row;
#  (2) int8 and fp16 at the harness's launch points: run_kinds.py (the command behind counts-v2.json) for int8 full and fp16 randn ->
#      against docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json (the counts MM1-v1's switch table was made from).
# Also draws the desk-only e37 tiles (fp32, 61 pairs, seeded 'E210-desk|e37|fp32') for step 7. --jobs 2. No device is opened.
set -u
. <W>/out/v31-counts/scripts/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
E=$L/work/lab/tools/claims-v3/e210/desk
B=$L/work/bench
D=$L/work/dsk
C=$L/work/counts
mkdir -p "$L/work/bin" "$D/fp32/randn" "$D/fp32/e37" "$C" "$L/work/tmp"
echo "start $(ts); load $(load1)"
g++ -O2 -std=c++17 -o "$L/work/bin/gen_tiles_e210" "$E/gen_tiles_e210.cpp" || exit 4
g++ --version | head -1
"$L/work/bin/gen_tiles_e210" randn fp32 61 "$D/fp32/randn" || exit 4
"$L/work/bin/gen_tiles_e210" e37 fp32 61 "$D/fp32/e37" || exit 4
( cd "$D" && find fp32 -name '*.bin' | LC_ALL=C sort | xargs sha256sum ) > "$D/tiles-made.sha256"
echo "desk tiles: $(wc -l < "$D/tiles-made.sha256"); list sha256 $(sha256sum < "$D/tiles-made.sha256" | cut -c1-16)"
$PY - "$D" "$L/work/spec-recount.json" <<'EOF'
import glob, json, os, sys
d, out = sys.argv[1], sys.argv[2]
fl = sorted(glob.glob(os.path.join(d, 'fp32', 'randn', 'randn_*.bin')))
assert len(fl) == 61
json.dump({'randn': {'files': fl}}, open(out, 'w'), indent=1)
print('spec: randn', len(fl))
EOF
$PY "$E/count_e210.py" --bench "$B" --maps "$L/work/maps" --spec "$L/work/spec-recount.json" --kinds randn --js 3,11,19,27 --tsel 0,1 \
  --jobs 2 --tmp "$L/work/tmp" --stop-if-file "$W/locks/quiet-desk-aifoundry2" --label "recount: S1 gemmL1x1x1 fp32 randn (E210's row)" \
  --out "$C/recount-fp32-S1-randn.json" || exit 5
echo "$(ts) fp32 S1 randn re-counted"
cd "$B" || exit 2
$PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$L/work/maps" --kinds "$L/work/lab/tools/claims-v3/kinds" \
  --types int8 --only full --jobs 2 --tmp "$L/work/tmp" --out "$C/recount-launch-int8-full.json" || exit 6
$PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$L/work/maps" --kinds "$L/work/lab/tools/claims-v3/kinds" \
  --types fp16 --only randn --jobs 2 --tmp "$L/work/tmp" --out "$C/recount-launch-fp16-randn.json" || exit 6
echo "$(ts) int8 full and fp16 randn re-counted at the launch points"
echo "end $(ts)"
