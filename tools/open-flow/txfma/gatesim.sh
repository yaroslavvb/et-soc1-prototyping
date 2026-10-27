#!/bin/bash
# Q126(e): drive the fma_toggle stimulus into the synthesized netlist and write a SAIF.
#   SCRATCH=... TILES=<hex> OPS=1 bash tools/open-flow/txfma/gatesim.sh
# Zero delay (Verilator). The timed pass is gatesim_sdf.sh.
set -u
S=${SCRATCH:?set SCRATCH}
W=$S/work
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
V=$S/oss-cad-suite/bin/verilator
TB=${TB:?set TB to tb_gate.sv}
NET=${NET:-$W/syn/txfma_keep.v}
LANES=${LANES:-1}
OPS=${OPS:-1}
WARM=${WARM:-1}
TAG=${TAG:-run}
# ASAP7's own SEQ models are built on sequential UDPs that Verilator refuses; the two cells this
# netlist uses have behavioural stand-ins beside this script. SEQ= overrides it for other tools.
SEQ=${SEQ:-$(dirname "$TB")/asap7_seq_behav.v}
OUT=$W/sim/$TAG
mkdir -p "$OUT"
LOG=$OUT/build.log

if [ ! -x "$OUT/obj_dir/Vtb" ]; then
  # --trace-underscore is not optional here: every net abc creates is named _0123_, and without
  # it the activity file silently misses most of the netlist. --public-flat-rw stops the
  # optimiser folding gate outputs away before they can be traced.
  nice -n 19 "$V" --binary --timing --trace-saif --trace-underscore --public-flat-rw \
    --trace-max-width 4096 --trace-max-array 4096 \
    -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 8 -O2 \
    --Mdir "$OUT/obj_dir" -o Vtb \
    +define+FMA_TB_LATENCY=7 +define+FMA_TB_LANES="$LANES" \
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
[ -x "$OUT/obj_dir/Vtb" ] || { tail -30 "$LOG"; exit 1; }

nice -n 19 "$OUT/obj_dir/Vtb" +tiles="${TILES:?set TILES}" +ops="$OPS" +warm="$WARM" \
  +saif="$OUT/activity.saif" ${EXTRA:-} | tee "$OUT/run.log" | grep -E "^ACCT|^CHK" | head -20
ls -la "$OUT/activity.saif"
