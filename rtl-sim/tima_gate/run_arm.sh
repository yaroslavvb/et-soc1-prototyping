#!/bin/bash
# Q133(a): one bench binary through the int8 tiles, behind the bench's functional check, with fma_toggle_v2's own
# train_maps.py, run_kinds.py and settle_count, unchanged. nice 10, JOBS at a time (at most 6).
#   BUILD=<dir with obj_<arm>/Vtb, accum, settle_count> OUT=<dir> LAB=<lab checkout> bash run_arm.sh <arm>
# <arm>: rtl (the control, Q132(b)'s bench as built) or a netlist arm (plain, booth, booth_tree, booth_swap).
#
# Knobs (environment):
#   MAPS=full    train_maps.py's maps (18 streams in three formats), so nets_map means what it means in Q132(b)
#   MAPS=quick   a map learned on one int8 stream: run_kinds.py needs one per binary, but its nets_map is then not a count
#                to quote. Every count this lane quotes is nets_hier, which uses no map.
#   TYPES=int8   or fp32,fp16 for a float-unit netlist (rtl-sim/tima_gate/Makefile gatef); BITS applies to int8 only
#   KINDS=a,b    tools/claims-v3/kinds kinds to run (default all of TYPES); KPOINTS=launch (the three launch points) or n,n
#   BITS=all|ab|<e102_x,e79_y,...>|none   the single-bit tiles: ab = E79's A list (a8q, a8_0..a8_7) and E102's B list (hq,
#                bk_0..bk_7, byte-identical to E79's h8q and b8k list); all = ab and E102's five masks; BPOINTS (default 471698,
#                the middle of the three launch points)
set -u
ARM=${1:?arm}
B=${BUILD:?set BUILD}
LAB=${LAB:?set LAB}
O=${OUT:?set OUT}/$ARM
JOBS=${JOBS:-6}
TYPES=${TYPES:-int8}
V2=$LAB/rtl-sim/fma_toggle_v2
K=$LAB/tools/claims-v3/kinds
E79=$LAB/docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/aifoundry3/hlp/p7910/tiles
E102=$K/e102/tiles/int8
mkdir -p "$O/tmp"
t0=$(date +%s)

if [ ! -s "$O/maps/vpu.map" ]; then
  if [ "${MAPS:-full}" = full ]; then
    nice -n 10 python3 "$V2/train_maps.py" --bin "$B/obj_$ARM/Vtb" --settle "$B/settle_count" --kinds "$K" --out "$O/maps" \
      --jobs "$JOBS" --tmp "$O/tmp" > "$O/train_maps.log" 2>&1 || { echo "train_maps failed"; tail "$O/train_maps.log"; exit 1; }
  else
    mkdir -p "$O/maps"
    T1=${TYPES%%,*}
    if [ "$T1" = int8 ]; then QT=full; QU="unit_int8 .lane_tima.tima."; else QT=randn; QU="unit_float .txfma."; fi
    python3 - "$K/tiles/$T1/$QT.bin" "$O/tmp/q.hex" <<'PY'
import struct, sys
w = struct.unpack("<512I", open(sys.argv[1], "rb").read()) + (0,) * 256
open(sys.argv[2], "w").write("\n".join(f"{x:08x}" for x in w) + "\n")
PY
    nice -n 10 "$B/obj_$ARM/Vtb" +tiles="$O/tmp/q.hex" +fmt="$T1" +warm=1 +first=1 +ops=1 +dump="$O/tmp/q.vcd" +dump_ops=1 \
      +verilator+coverage+file+"$O/tmp/q.dat" > /dev/null
    for m in "$QU" "vpu .dut."; do
      set -- $m
      "$B/settle_count" --train "$O/tmp/q.vcd" --include "$2" --skip 1 --write-map "$O/maps/$1.map" 2>> "$O/train_maps.log"
    done
    for n in unit_int8 unit_float; do [ -s "$O/maps/$n.map" ] || cp "$O/maps/${QU%% *}.map" "$O/maps/$n.map"; done
    echo "quick maps: one $T1 stream ($QT); nets_map from them is not quoted" >> "$O/train_maps.log"
    rm -f "$O/tmp/q.vcd"
  fi
fi
t1=$(date +%s)

if [ "${KINDS:-all}" != none ]; then
  ONLY=${KINDS:-}; [ "$ONLY" = all ] && ONLY=
  nice -n 10 python3 "$V2/run_kinds.py" --bin "$B/obj_$ARM/Vtb" --accum "$B/accum" --settle "$B/settle_count" --maps "$O/maps" \
    --kinds "$K" --types "$TYPES" --only "$ONLY" --out "$O/counts_kinds.json" --jobs "$JOBS" --tmp "$O/tmp" \
    --points "${KPOINTS:-launch}" --keep-going > "$O/run_kinds_kinds.log" 2>&1
  echo "$ARM kinds: rc=$? $(grep -cE '^(int8|fp32|fp16) ' "$O/run_kinds_kinds.log") tiles, $(grep -c FAILED "$O/run_kinds_kinds.log") failed"
fi
t2=$(date +%s)

BITS=${BITS:-ab}
case $BITS in
  none) LIST= ;;
  ab)   LIST="e79_a8q e79_a8_0 e79_a8_1 e79_a8_2 e79_a8_3 e79_a8_4 e79_a8_5 e79_a8_6 e79_a8_7 e102_hq e102_bk_0 e102_bk_1 e102_bk_2 e102_bk_3 e102_bk_4 e102_bk_5 e102_bk_6 e102_bk_7" ;;
  all)  LIST="e79_a8q e79_a8_0 e79_a8_1 e79_a8_2 e79_a8_3 e79_a8_4 e79_a8_5 e79_a8_6 e79_a8_7 e102_hq e102_bk_0 e102_bk_1 e102_bk_2 e102_bk_3 e102_bk_4 e102_bk_5 e102_bk_6 e102_bk_7 e102_bk_0f e102_bk_f0 e102_bk_15 e102_bk_2a e102_bk_ff" ;;
  *)    LIST=$(echo "$BITS" | tr ',' ' ') ;;
esac
if [ -n "$LIST" ]; then
  EXTRA=""
  for n in $LIST; do
    case $n in
      e102_*) EXTRA="$EXTRA,int8:$n:$E102/${n#e102_}.bin" ;;
      e79_*)  EXTRA="$EXTRA,int8:$n:$E79/${n#e79_}.b7910.bin" ;;
    esac
  done
  nice -n 10 python3 "$V2/run_kinds.py" --bin "$B/obj_$ARM/Vtb" --accum "$B/accum" --settle "$B/settle_count" --maps "$O/maps" \
    --kinds "$K" --types int8 --only __none__ --extra-tiles "${EXTRA#,}" --out "$O/counts_bits.json" --jobs "$JOBS" \
    --tmp "$O/tmp" --points "${BPOINTS:-471698}" --keep-going > "$O/run_kinds_bits.log" 2>&1
  echo "$ARM bits: rc=$? $(grep -c '^int8' "$O/run_kinds_bits.log") tiles, $(grep -c FAILED "$O/run_kinds_bits.log") failed"
fi
t3=$(date +%s)
echo "$ARM: maps $((t1 - t0)) s, kinds $((t2 - t1)) s, bits $((t3 - t2)) s"
