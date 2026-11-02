#!/usr/bin/env bash
# Q136(c): build the TIMA bench. rtl-sim/fma_toggle_v2's whole-VPU bench (core-et's vpu_top, -fno-dfg), with E109's three plusargs
# (tools/claims-v3/e109/desk/tb_patch_e109.py: +rows +cols +mask) and this directory's additions: the register arrays instrumented
# (arrays_acct.sv), every macro register named by file and line (macros_line.vh, ff_acct_line.sv, acct_line.cpp), the scratchpad's reads by
# size and the buses' toggles, +pre and +firstall (tb_patch_q136c.py). Lean, as E109's desk built it: no coverage, no trace.
#   VERILATOR=<verilator> CXX=/usr/bin/clang++ JOBS=6 bash rtl-sim/tima_bench/build.sh <scratch dir>        # from the lab repo's root
# Writes <scratch dir>/obj_q136c/Vtb. On the Intel: VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator, CXX=/usr/bin/clang++.
# SPDX-License-Identifier: Apache-2.0
set -eu
OUT=${1:?usage: build.sh <scratch dir>}
ROOT=$(pwd); CORE_ET=$ROOT/external/core-et; RTL=$CORE_ET/rtl; V=$RTL/shire/minion/vpu
VER=${VERILATOR:-verilator}; CXX=${CXX:-clang++}; AR=${AR:-ar}; JOBS=${JOBS:-6}
HERE=$ROOT/rtl-sim/tima_bench
mkdir -p "$OUT"
cp rtl-sim/fma_toggle_v2/tb_vpu.sv rtl-sim/fma_toggle_v2/acct.cpp "$OUT/"
cp "$HERE/arrays_acct.sv" "$HERE/macros_line.vh" "$HERE/ff_acct_line.sv" "$HERE/acct_line.cpp" "$OUT/"
python3 tools/claims-v3/e109/desk/tb_patch_e109.py "$OUT"
python3 "$HERE/tb_patch_q136c.py" "$OUT"
rm -f "$OUT/acct.cpp"          # E109's patch edits it; this build uses acct_line.cpp in its place
cd "$OUT"
nice -n 10 "$VER" --binary --timing --Mdir obj_q136c -Wno-fatal -Wno-lint -Wno-style --top-module tb -j "$JOBS" \
  -MAKEFLAGS CXX=$CXX -MAKEFLAGS LINK=$CXX -MAKEFLAGS AR=$AR -fno-dfg \
  +define+ET_SIMULATION +incdir+. +incdir+$RTL/inc +incdir+$RTL +incdir+$CORE_ET \
  -y $V -y $V/txfma_7s -y $V/tima -y $V/trans_unit \
  -y $RTL/libs/macros -y $RTL/libs/rf_latches -y $RTL/libs/compressors \
  -y $RTL/libs/floating_point -y $RTL/libs/fixed_point \
  ff_acct_line.sv arrays_acct.sv tb_vpu.sv acct_line.cpp > build.log 2>&1 || { tail -40 build.log; exit 1; }
ls -la obj_q136c/Vtb
