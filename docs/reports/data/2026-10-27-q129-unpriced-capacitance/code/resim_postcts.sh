#!/bin/bash
# Q129(eda-cap): re-simulate the POST-CTS/POST-REPAIR netlist with the same vectors.
# Same verilator flags as tools/open-flow/txfma/gatesim.sh, but the model is built ONCE into a
# shared obj_dir and every pattern is a run of it (gatesim.sh rebuilds per TAG), and -j 4 instead
# of -j 8 (this box also carries other agents' work).
set -u
S=$HOME/scratch-q129-cap
W=$S/work
R=$S/core-et/rtl
P=$S/orfs/flow/platforms/asap7
V=$S/oss-cad-suite/bin/verilator
T=$S/tools/txfma
TB=$T/tb_gate.sv
SEQ=$T/asap7_seq_behav.v
NET=${NET:-$W/pnr/txfma_pnr.v}
OUT=${OUT:-$W/sim/pnrsim}
mkdir -p "$OUT" "$S/logs"
LOG=$OUT/build.log
echo "=== $(date -u +%FT%TZ) build start NET=$NET" | tee -a "$S/logs/resim.log"
if [ ! -x "$OUT/obj_dir/Vtb" ]; then
  nice -n 19 "$V" --binary --timing --trace-saif --trace-underscore --public-flat-rw \
    --trace-max-width 4096 --trace-max-array 4096 \
    -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 4 -O2 \
    --Mdir "$OUT/obj_dir" -o Vtb \
    +define+FMA_TB_LATENCY=7 +define+FMA_TB_LANES=1 \
    +incdir+"$R/inc" +incdir+"$R" \
    "$R/libs/rf_latches/et_clk_gate.v" \
    "$P"/verilog/stdcell/asap7sc7p5t_AO_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_INVBUF_RVT_TT_*.v \
    "$P"/verilog/stdcell/asap7sc7p5t_OA_RVT_TT_*.v \
    "$SEQ" \
    "$P"/verilog/stdcell/asap7sc7p5t_SIMPLE_RVT_TT_*.v \
    "$NET" "$TB" > "$LOG" 2>&1
  echo "build rc=$? (log $LOG)" | tee -a "$S/logs/resim.log"
fi
if [ ! -x "$OUT/obj_dir/Vtb" ]; then
  echo "BUILD_FAILED" | tee -a "$S/logs/resim.log"
  tail -40 "$LOG" | tee -a "$S/logs/resim.log"
  exit 1
fi
echo "=== $(date -u +%FT%TZ) build ok" | tee -a "$S/logs/resim.log"
for p in ${PATTERNS:-randn zeros ones lb_h8 lq_h8 lb_h0 lq_h0 lb_h1 lq_h1 lb_h2 lq_h2 lb_h4 lq_h4}; do
  for o in 0 1; do
    f=$OUT/${p}_o${o}.saif
    [ -s "$f" ] && { echo "skip $p o$o"; continue; }
    nice -n 19 "$OUT/obj_dir/Vtb" +tiles="$W/tiles/$p.hex" +ops=$o +warm=1 \
      +saif="$f" > "$OUT/${p}_o${o}.log" 2>&1
    echo "$p o$o rc=$? $(grep -m1 '^ACCT' "$OUT/${p}_o${o}.log") $(stat -c%s "$f" 2>/dev/null)" | tee -a "$S/logs/resim.log"
  done
done
echo "RESIM_DONE $(date -u +%FT%TZ)" | tee -a "$S/logs/resim.log"
