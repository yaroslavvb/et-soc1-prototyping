#!/usr/bin/env bash
# E182 (Q153, the kit): the train host at the desk, no card. Build workloads/sparsity's host with patch_host_e182.py applied against the
# check of C's mock runtime (tools/claims-v3/ccheck/mockrt, Q139(k)'s: device memory is host memory and kernelLaunch runs a software SP_FMA
# with rtl-sim/fma_toggle_v2/accum.c's arithmetic on the tiles at the launch's a_tile and b_tile), then run trains and read them with
# desktest_host_e182.py: every launch's SPARSITY record and C record follow the registered schedule, and ccheck.py judges every launch's C
# against its own tiles. No device access of any kind.
#
#   bash tools/claims-v3/e182/desktest_host_e182.sh <out-dir>
# SPDX-License-Identifier: Apache-2.0
set -u
OUT=${1:?usage: desktest_host_e182.sh <out-dir>}
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
R=$PWD
mkdir -p "$OUT/src"
OUT=$(cd "$OUT" && pwd)
M=$R/tools/claims-v3/ccheck/mockrt
cp "$R/workloads/sparsity/host/main.cpp" "$OUT/src/main.cpp"
/usr/bin/python3 -B "$R/tools/claims-v3/e182/patch_host_e182.py" "$OUT/src/main.cpp" > "$OUT/patch.log" 2>&1 || { cat "$OUT/patch.log"; exit 1; }
nice -n 10 c++ -std=c++17 -O1 -Wall -Wno-unused-variable -I "$M/include" -I "$R/workloads/sparsity" "$OUT/src/main.cpp" "$M/mock_rt.cpp" \
  -o "$OUT/sparsity_host_e182" > "$OUT/build.log" 2>&1 || { tail -30 "$OUT/build.log"; exit 1; }
cc -O2 -o "$OUT/accum" "$R/rtl-sim/fma_toggle_v2/accum.c" -lm || exit 1
export MOCK_ACCUM=$OUT/accum MOCK_SLEEP_MS=20
T=$R/tools/claims-v3/e182/tiles
T78=$R/tools/claims-v3/e178/tiles
run() { # name type F S orientation extra...
  local name=$1 ty=$2 f=$3 s=$4 ori=$5; shift 5
  rm -f "$OUT/$name.jsonl"
  "$OUT/sparsity_host_e182" --test fma --type "$ty" --pattern none --values "file:$f" --values-b "file:$s" --abba "$ori" --launches 13 \
    --seconds 60 --shires 0x3 --per-shire 8 --seed 1 --kernel "$OUT/accum" --c-log "$OUT/$name.jsonl" --c-poison \
    --dump-tiles "$OUT/$name.tiles" "$@" > "$OUT/$name.out" 2> "$OUT/$name.err"
  echo "$name rc=$?"
}
run t1_sffs int8 "$T78/int8/e178_v5.bin" "$T78/int8/e178_v4.bin" SFFS
run t1_fssf int8 "$T78/int8/e178_v5.bin" "$T78/int8/e178_v4.bin" FSSF
run t2_sffs int8 "$T/int8/e182_a1_bm1.bin" "$T/int8/e182_am1_b1.bin" SFFS
run t5_fssf fp32 "$T/fp32/e182_a1_b3fffffff.bin" "$T/fp32/e182_a3fffffff_b1.bin" FSSF
run t6_sffs fp32 "$T78/fp32/e178_v5.bin" "$T78/fp32/e178_v4.bin" SFFS
# the refusals: a train without --launches, a bad orientation, a built-in --values
"$OUT/sparsity_host_e182" --test fma --type int8 --pattern none --values "file:$T78/int8/e178_v5.bin" --values-b "file:$T78/int8/e178_v4.bin" \
  --abba SFFS --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_nolaunches.out" 2>&1; echo "refuse_nolaunches rc=$?"
"$OUT/sparsity_host_e182" --test fma --type int8 --pattern none --values "file:$T78/int8/e178_v5.bin" --values-b "file:$T78/int8/e178_v4.bin" \
  --abba SSFF --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_ori.out" 2>&1; echo "refuse_ori rc=$?"
"$OUT/sparsity_host_e182" --test fma --type int8 --pattern none --values ones --values-b "file:$T78/int8/e178_v4.bin" \
  --abba SFFS --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_builtin.out" 2>&1; echo "refuse_builtin rc=$?"
# without --values-b the patched host runs a plain run, as the C-logging host does
"$OUT/sparsity_host_e182" --test fma --type int8 --pattern none --values "file:$T78/int8/e178_v5.bin" --seconds 0.3 --shires 0x3 --per-shire 8 \
  --kernel "$OUT/accum" --c-log "$OUT/plain.jsonl" --c-poison > "$OUT/plain.out" 2> "$OUT/plain.err"; echo "plain rc=$?"
for n in t1_sffs t1_fssf t2_sffs t5_fssf t6_sffs plain; do
  python3 "$R/tools/claims-v3/ccheck/ccheck.py" check "$OUT/$n.jsonl" --jobs 2 --cache "$OUT/cache" > "$OUT/$n.check" 2>&1
  echo "$n ccheck rc=$? $(tail -1 "$OUT/$n.check")"
done
/usr/bin/python3 -B "$R/tools/claims-v3/e182/desktest_host_e182.py" "$OUT"
