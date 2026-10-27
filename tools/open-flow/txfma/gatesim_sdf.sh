#!/bin/bash
# Q126(e): the timed pass. Records the unit's pins from the zero-delay bench, replays them into
# the same netlist under Icarus, once with no delays and once with the post-CTS SDF, and counts
# the toggles of both. The difference is the glitches.
#   SCRATCH=... TILES=<hex> SDF=<file> bash tools/open-flow/txfma/gatesim_sdf.sh
set -u
S=${SCRATCH:?set SCRATCH}
W=$S/work
P=$S/orfs/flow/platforms/asap7
I=$S/oss-cad-suite/bin/iverilog
VVP=$S/oss-cad-suite/bin/vvp
HERE=${HERE:?set HERE to the directory holding this script}
NET=${NET:-$W/syn/txfma_keep.v}
SDF=${SDF:-$W/pnr/txfma.sdf}
TAG=${TAG:-randn}
VEC=${VEC:?set VEC to the vector file tb_gate.sv wrote}
OUT=$W/sim/timed_$TAG
mkdir -p "$OUT"

if [ ! -s "$OUT/tb.vvp" ]; then
  # ASAP7's own SEQ models carry ifnone edge-sensitive specify paths that Icarus refuses, so the
  # two sequential cells come from the behavioural file. The combinational models keep their
  # specify blocks, which is where the SDF delays land and where glitches are made.
  # -gspecify is not optional: without it Icarus ignores every specify block, $sdf_annotate
  # then changes nothing and the timed run comes out byte-identical to the zero-delay one.
  nice -n 19 "$I" -g2012 -gspecify -o "$OUT/tb.vvp" -s tbt \
    "$P"/verilog/stdcell/asap7sc7p5t_AO_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_INVBUF_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_OA_RVT_TT_*.v \
    "$HERE/asap7_seq_behav.v" \
    "$P"/verilog/stdcell/asap7sc7p5t_SIMPLE_RVT_TT_*.v \
    "$NET" "$HERE/tb_timed.v" > "$OUT/build.log" 2>&1
  echo "iverilog rc=$?"
  [ -s "$OUT/tb.vvp" ] || { tail -20 "$OUT/build.log"; exit 1; }
fi

for mode in zero timed; do
  [ -s "$OUT/$mode.vcd" ] && { echo "have $mode"; continue; }
  args="+vectors=$VEC +vcd=$OUT/$mode.vcd"
  [ "$mode" = timed ] && args="$args +sdf=$SDF"
  # shellcheck disable=SC2086
  nice -n 19 "$VVP" "$OUT/tb.vvp" $args > "$OUT/$mode.log" 2>&1
  echo "$mode rc=$? $(grep -o 'TIMED .*' "$OUT/$mode.log") $(du -h "$OUT/$mode.vcd" 2>/dev/null | cut -f1)"
done

for mode in zero timed; do
  [ -s "$OUT/$mode.vcd" ] || continue
  echo "=== $mode"
  # count only the measured op: the first half of the replay is the warm-up
  python3 -I "$HERE/vcd_toggles.py" "$OUT/$mode.vcd" --from "${T0:-110500}" --to "${T1:-221000}" \
      --out "$OUT/toggles_$mode.json"
done
