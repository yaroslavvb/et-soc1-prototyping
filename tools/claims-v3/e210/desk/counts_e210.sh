#!/usr/bin/env bash
# E210 (Q202) desk: the switch counts from the committed sources, end to end (the command behind desk/counts-e210-S1.json, -S2.json and
# desk/switch-counts-e210.json). No device is opened by anything here; run it inside the lab's CPU slot and with no device nodes visible
# (on aifoundry2: bash W/slot.sh bash W/nodev.sh bash counts_e210.sh ...), never while the box's card is in use (the quiet-desk flag).
#
#   bash tools/claims-v3/e210/desk/counts_e210.sh <lab top> <core-et checkout at b38a1a31> <work dir (new or empty)> <desk-only tile dir>
#
# 1. the bench: rtl-sim/fma_toggle_v2 from <lab top> and core-et's rtl, dv/inc and extern from the checkout, copied into <work>, every file's
#    sha256 compared with its source; the Makefile's -j 10 made -j 4 (the one change); built with Verilator 5 (-fno-dfg, the Makefile's own);
# 2. the bench's functional check (fcheck_all.sh), which must PASS before any count;
# 3. the net maps trained on this binary (train_maps.py: a map belongs to its binary), and the build's calibration: run_kinds.py (the command
#    behind the committed counts-v2.json) at the harness's own launch points for fp32 randn, zeros, ones and sparse50;
# 4. the kinds spec (spec_e210.py; the desk-only tiles from make_tiles_e210.sh) and the counts at a GEMM's accumulator states (count_e210.py):
#    S1 (gemmL1x1x1: j = 3, 11, 19, 27 of 32 ops, tiles 0 and 1) and S2 (gemmL1x1x4: j = 15, 47, 79, 111 of 128, tile 2), jobs 4;
# 5. MM1-v1's units (switch_counts_e210.py).
set -u
TOP=${1:?lab top}
CORE=${2:?core-et checkout}
WK=${3:?work dir}
DSK=${4:?desk-only tile dir}
E=$TOP/tools/claims-v3/e210
PY="/usr/bin/python3 -I -B"
ts() { TZ=America/Los_Angeles date '+%F %T %Z'; }
STOPF=${STOP_IF_FILE:-}     # optional: a file whose presence stops the run between steps and between bench points (on aifoundry2: the quiet-desk flag)
chk() { if [ -n "$STOPF" ] && [ -e "$STOPF" ]; then echo "$(ts) STOPPED: $STOPF exists"; exit 12; fi; }
echo "$(ts) start; lab $(git -C "$TOP" rev-parse HEAD 2>/dev/null || echo 'not a git tree'); core-et $(git -C "$CORE" rev-parse HEAD 2>/dev/null)"
mkdir -p "$WK/bench" "$WK/core-et/dv" "$WK/maps" "$WK/tmp" "$WK/fcheck"
cp -p "$TOP"/rtl-sim/fma_toggle_v2/* "$WK/bench/"
( cd "$WK/bench" && sha256sum * ) > "$WK/bench-copy.sha256"
( cd "$TOP/rtl-sim/fma_toggle_v2" && sha256sum * ) > "$WK/bench-src.sha256"
cmp -s "$WK/bench-copy.sha256" "$WK/bench-src.sha256" || { echo "bench copy differs from its source"; exit 5; }
sed -i 's/-j 10/-j 4/' "$WK/bench/Makefile"
cp -a "$CORE/rtl" "$WK/core-et/"
cp -a "$CORE/dv/inc" "$WK/core-et/dv/"
cp -a "$CORE/extern" "$WK/core-et/"
( cd "$WK/core-et" && find rtl dv extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-copy.sha256"
( cd "$CORE" && find rtl dv/inc extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-src.sha256"
cmp -s "$WK/core-et-copy.sha256" "$WK/core-et-src.sha256" || { echo "core-et copy differs from its source"; exit 5; }
echo "$(ts) sources copied: bench $(wc -l < "$WK/bench-copy.sha256") files, core-et $(wc -l < "$WK/core-et-copy.sha256") files (manifest $(sha256sum < "$WK/core-et-copy.sha256" | cut -c1-16))"
verilator --version
chk
( cd "$WK/bench" && prlimit --as=4294967296 nice -n 10 make CORE_ET="$WK/core-et" VERILATOR="$(command -v verilator)" all > "$WK/make.log" 2> "$WK/make.err" ) \
  || { echo "build failed"; tail -5 "$WK/make.err"; exit 6; }
echo "$(ts) built"
chk
( cd "$WK/bench" && JOBS=4 PY=/usr/bin/python3 bash fcheck_all.sh "$WK/fcheck" > "$WK/fcheck.log" 2>&1 ) || { echo "functional check FAILED"; tail -8 "$WK/fcheck.log"; exit 7; }
tail -7 "$WK/fcheck.log"
( cd "$WK/bench" && $PY train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds "$TOP/tools/claims-v3/kinds" --out "$WK/maps" --jobs 4 --tmp "$WK/tmp" ) \
  || { echo "train_maps failed"; exit 8; }
( cd "$WK/maps" && sha256sum * )
echo "$(ts) maps trained"
chk
( cd "$WK/bench" && $PY run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps "$WK/maps" --kinds "$TOP/tools/claims-v3/kinds" \
    --types fp32 --only randn,zeros,ones,sparse50 --out "$E/desk/calib-launch-e210.json" --jobs 4 --tmp "$WK/tmp" > "$WK/run_kinds.log" 2>&1 ) \
  || { echo "run_kinds failed"; tail -5 "$WK/run_kinds.log"; exit 8; }
echo "$(ts) the build's calibration at the harness's own launch points (four fp32 kinds) written"
chk
$PY "$E/desk/spec_e210.py" "$TOP" "$DSK" "$WK/spec-e210.json" || exit 9
K=negzero,signs,lowmant8,highmant8,bhalfeq,badjeq,hd4,maxalte,arow50,randn,zeros,ones,sparse50,real
$PY "$E/desk/count_e210.py" --bench "$WK/bench" --maps "$WK/maps" --spec "$WK/spec-e210.json" --kinds "$K" --js 3,11,19,27 --tsel 0,1 \
  --jobs 4 --tmp "$WK/tmp" --stop-if-file "$STOPF" --label "S1 gemmL1x1x1 fp32" --out "$E/desk/counts-e210-S1.json" || exit 10
echo "$(ts) S1 counted"
chk
$PY "$E/desk/count_e210.py" --bench "$WK/bench" --maps "$WK/maps" --spec "$WK/spec-e210.json" --kinds "$K" --js 15,47,79,111 --tsel 2 \
  --jobs 4 --tmp "$WK/tmp" --stop-if-file "$STOPF" --label "S2 gemmL1x1x4 fp32" --out "$E/desk/counts-e210-S2.json" || exit 10
echo "$(ts) S2 counted"
$PY "$E/desk/switch_counts_e210.py" "$TOP" "$E/desk/counts-e210-S1.json" "$E/desk/counts-e210-S2.json" "$E/desk/switch-counts-e210.json" \
  "$E/desk/switch-counts-e210.txt" "$E/desk/calib-launch-e210.json" || exit 11
echo "$(ts) done"
