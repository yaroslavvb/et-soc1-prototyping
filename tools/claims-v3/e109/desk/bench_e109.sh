#!/usr/bin/env bash
# E109 desk: rtl-sim/fma_toggle_v2's whole-VPU bench (core-et's vpu_top, its register accounting), copied into a scratch directory, given three
# plusargs (+rows, +cols, +mask: the TensorFMA's A rows, A columns and row mask; defaults are the original word, rows 16, cols 16, no mask) and built
# lean (no coverage, no trace). Then bench_arms_e109.py runs every E109 arm through it.
#   VERILATOR=<verilator> CXX=clang++ bash tools/claims-v3/e109/desk/bench_e109.sh <scratch dir>        # from the lab repo's root
set -eu
OUT=${1:?usage: bench_e109.sh <scratch dir>}
ROOT=$(pwd); CORE_ET=$ROOT/external/core-et; RTL=$CORE_ET/rtl; V=$RTL/shire/minion/vpu
VER=${VERILATOR:-verilator}; CXX=${CXX:-clang++}; AR=${AR:-ar}
mkdir -p "$OUT"
cp rtl-sim/fma_toggle_v2/tb_vpu.sv rtl-sim/fma_toggle_v2/ff_acct.sv rtl-sim/fma_toggle_v2/macros_acct.vh rtl-sim/fma_toggle_v2/acct.cpp "$OUT/"
python3 tools/claims-v3/e109/desk/tb_patch_e109.py "$OUT"
cd "$OUT"
nice -n 10 "$VER" --binary --timing --Mdir obj_lean -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 6 \
  -MAKEFLAGS CXX=$CXX -MAKEFLAGS LINK=$CXX -MAKEFLAGS AR=$AR -fno-dfg \
  +define+ET_SIMULATION +incdir+. +incdir+$RTL/inc +incdir+$RTL +incdir+$CORE_ET \
  -y $V -y $V/txfma_7s -y $V/tima -y $V/trans_unit \
  -y $RTL/libs/macros -y $RTL/libs/rf_latches -y $RTL/libs/compressors \
  -y $RTL/libs/floating_point -y $RTL/libs/fixed_point \
  ff_acct.sv tb_vpu.sv acct.cpp > build.log 2>&1
ls -la obj_lean/Vtb
