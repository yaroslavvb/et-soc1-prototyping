#!/bin/bash
# Q129: drive the card's operand stream into the synthesized scope netlist and write a SAIF.
#   SCRATCH=... LAB=... TILES=<hex> TAG=randn bash tools/open-flow/scope/gatesim.sh
# Zero delay (Verilator), exactly as tools/open-flow/txfma/gatesim.sh does it for the arithmetic.
# Two runs per pattern: TAG_o1 with the measured ops, TAG_o0 with none, so power.py can take the
# difference and the warm-up and reset fall outside the window.
set -u
S=${SCRATCH:?set SCRATCH}
L=${LAB:-$HOME/claude/et-soc1-prototyping}
W=$S/work-scope
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
V=$S/oss-cad-suite/bin/verilator
TB=${TB:-$L/tools/open-flow/scope/tb_scope.sv}
NET=${NET:-$W/syn/scope_mixed.v}
SEQ=${SEQ:-$L/tools/open-flow/scope/asap7_seq_behav_scope.v}
TAG=${TAG:-run}
OPS=${OPS:-1}
WARM=${WARM:-1}
LANE=${LANE:-0}
MODE=${MODE:-}        # extra plusargs, e.g. "+accfix=1" or "+resfix=1"
BUILD=$W/sim/build-$(basename "$NET" .v)
mkdir -p "$BUILD"
LOG=$BUILD/build.log

if [ ! -x "$BUILD/obj_dir/Vtb" ]; then
  # --trace-underscore is not optional: every net abc creates is named _0123_, and without it
  # the activity file silently misses most of the netlist. --public-flat-rw stops the optimiser
  # folding gate outputs away before they can be traced.
  nice -n 19 "$V" --binary --timing --trace-saif --trace-underscore --public-flat-rw \
    --trace-max-width 4096 --trace-max-array 4096 \
    -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 4 -O2 \
    --Mdir "$BUILD/obj_dir" -o Vtb \
    +incdir+"$R/inc" +incdir+"$R" \
    "$R/libs/rf_latches/et_clk_gate.v" \
    "$P"/verilog/stdcell/asap7sc7p5t_AO_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_INVBUF_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_OA_RVT_TT_*.v \
    "$SEQ" \
    "$P"/verilog/stdcell/asap7sc7p5t_SIMPLE_RVT_TT_*.v \
    "$NET" "$TB" > "$LOG" 2>&1
  echo "build rc=$? (log $LOG)"
fi
[ -x "$BUILD/obj_dir/Vtb" ] || { tail -40 "$LOG"; exit 1; }

OUT=$W/sim/out
mkdir -p "$OUT"
for n in 1 0; do
  nice -n 19 "$BUILD/obj_dir/Vtb" +tiles="${TILES:?set TILES}" +ops="$([ $n = 1 ] && echo "$OPS" || echo 0)" \
    +warm="$WARM" +lane="$LANE" +saif="$OUT/${TAG}_o$n.saif" ${MODE} \
    | tee "$OUT/${TAG}_o$n.log" | grep -E "^ACCT" | head -3
done
ls -la "$OUT/${TAG}_o1.saif" "$OUT/${TAG}_o0.saif"
