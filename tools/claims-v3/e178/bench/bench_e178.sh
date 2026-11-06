#!/bin/bash
# E178 (Q146): the toggle bench on E178's one-number tiles, as it was run on the mini on Thu 5 Nov 2026 (bench/README.md).
# Run from the Intel. The bench is rtl-sim/fma_toggle_v2 built on the mini with Homebrew's Verilator 5.052 (-fno-dfg), the
# recorded Q141(t2) build (Vtb sha256 a740318c...); run_kinds.py, accum.c, settle_count and maps are the repo's, unchanged.
#   BENCH=<the build's directory on the mini>  WORK=<a scratch directory on the mini>  bash bench_e178.sh
# It stages the 40 E178 tiles plus each format's committed zeros tile (the build check), then
#   (1) run_kinds.py over all 43 tiles at its three launch points, 3 jobs -> counts-e178.json (M10's counts form)
#   (2) vcd_signals_e178.py on 28 (type, kind, n0) points -> vcd-signals-e178-1.json and -2.json (the signal-level reading)
# SPDX-License-Identifier: Apache-2.0
set -eu
: "${BENCH:?the bench build directory on the mini}"
: "${WORK:?a scratch directory on the mini}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
T="$(mktemp -d)"
for t in fp32 fp16 int8; do
  mkdir -p "$T/tiles/$t"
  cp "$HERE/tiles/$t/"*.bin "$T/tiles/$t/"
  cp "$ROOT/tools/claims-v3/kinds/tiles/$t/zeros.bin" "$T/tiles/$t/zeros.bin"
done
ssh -o BatchMode=yes -o ConnectTimeout=10 mini "mkdir -p $WORK/out $WORK/tmp"
rsync -a "$T/tiles" "mini:$WORK/kinds/"
rsync -a "$HERE/vcd_signals_e178.py" "mini:$WORK/"
RR="${RUN_REMOTE:-run_remote}"   # the batch-work door (section 28 of the round brief)
"$RR" --host mini --max-gb 6 --timeout 900 --cd "$WORK" -- python3 "$BENCH/run_kinds.py" --bin "$BENCH/obj_vpu/Vtb" \
  --accum "$BENCH/accum" --settle "$BENCH/settle_count" --maps "$BENCH/maps" --kinds "$WORK/kinds" \
  --out "$WORK/out/counts-e178.json" --jobs 3 --tmp "$WORK/tmp"
J1=int8:zeros:471698,int8:ones:471698,int8:e178_v4:471698,int8:e178_v5:471698,int8:neg_ones:471698,int8:e178_v3:471698,int8:e178_v6:471698
J1=$J1,fp32:zeros:274725,fp32:ones:274725,fp32:e178_v2:274725,fp32:e178_v4:274725,fp32:e178_v5:274725,fp32:e178_uf:274725,fp32:e178_a4_b5:274725
J2=int8:e178_a4_b5:471698,int8:e178_a5_b4:471698,int8:e178_v85:471698,int8:e178_v127:471698,int8:e178_v2:471698,fp16:zeros:274725
J2=$J2,fp16:ones:274725,fp16:e178_v4:274725,fp16:e178_v5:274725,fp16:e178_a4_b5:274725,fp32:e178_v1p5:274725,fp32:e178_a5_b4:274725
J2=$J2,fp32:e178_v7:274725,fp32:neg_ones:274725
for j in 1 2; do
  eval "JOBS=\$J$j"
  "$RR" --host mini --max-gb 4 --timeout 900 --cd "$WORK" -- python3 vcd_signals_e178.py --bin "$BENCH/obj_vpu/Vtb" \
    --accum "$BENCH/accum" --tiles "$WORK/kinds/tiles" --jobs "$JOBS" --out "$WORK/out/vcd-signals-$j.json" --tmp "$WORK/tmp"
done
rsync -a "mini:$WORK/out/counts-e178.json" "$HERE/bench/counts-e178.json"
rsync -a "mini:$WORK/out/vcd-signals-1.json" "$HERE/bench/vcd-signals-e178-1.json"
rsync -a "mini:$WORK/out/vcd-signals-2.json" "$HERE/bench/vcd-signals-e178-2.json"
rm -rf "${T:?}"
