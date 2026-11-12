#!/usr/bin/env bash
# E188 (Q165, the kit): the train host at the desk, no card, on E188's trains: E186's desk test (tools/claims-v3/e186/desktest_host_e186.sh,
# itself E182's) with E188's tiles and trains. Build workloads/sparsity's host with E182's patch_host_e182.py (unchanged: the host E188's box
# build makes) applied, against the check of C's mock runtime (tools/claims-v3/ccheck/mockrt, Q139(k)'s: device memory is host memory and
# kernelLaunch runs a software SP_FMA with rtl-sim/fma_toggle_v2/accum.c's arithmetic on the tiles at the launch's a_tile and b_tile), then
# run E188's trains - B05 (the smoke's train) in both orientations, PAIR, AALL and B22 - and read them with desktest_host_e188.py: every
# launch's SPARSITY record and C record follow the registered schedule, ccheck.py judges every launch's C against its own tiles, and a C
# record re-paired to the other kind's tiles is NOT judged PASS on any of E188's trains (their two kinds' C differ). No device access.
#
#   bash tools/claims-v3/e188/desktest_host_e188.sh <out-dir>
# SPDX-License-Identifier: Apache-2.0
set -u
OUT=${1:?usage: desktest_host_e188.sh <out-dir>}
mkdir -p "$OUT/src" && OUT=$(cd "$OUT" && pwd)
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
R=$PWD
case "$OUT/" in "$R/"*) echo "the out-dir must be outside the repository"; exit 2 ;; esac
M=$R/tools/claims-v3/ccheck/mockrt
cp "$R/workloads/sparsity/host/main.cpp" "$OUT/src/main.cpp"
/usr/bin/python3 -B "$R/tools/claims-v3/e182/patch_host_e182.py" "$OUT/src/main.cpp" > "$OUT/patch.log" 2>&1 || { cat "$OUT/patch.log"; exit 1; }
nice -n 10 c++ -std=c++17 -O1 -Wall -Wno-unused-variable -I "$M/include" -I "$R/workloads/sparsity" "$OUT/src/main.cpp" "$M/mock_rt.cpp" \
  -o "$OUT/sparsity_host_e188" > "$OUT/build.log" 2>&1 || { tail -30 "$OUT/build.log"; exit 1; }
cc -O2 -o "$OUT/accum" "$R/rtl-sim/fma_toggle_v2/accum.c" -lm || exit 1
export MOCK_ACCUM=$OUT/accum MOCK_SLEEP_MS=20
T88=$R/tools/claims-v3/e188/tiles/fp32
T78=$R/tools/claims-v3/kinds/tiles/fp32
T82=$R/tools/claims-v3/e182/tiles/fp32
T86=$R/tools/claims-v3/m12/tiles-e186/fp32
run() { # name type F S orientation extra...
  local name=$1 ty=$2 f=$3 s=$4 ori=$5; shift 5
  rm -f "${OUT:?}/${name:?}.jsonl"
  "$OUT/sparsity_host_e188" --test fma --type "$ty" --pattern none --values "file:$f" --values-b "file:$s" --abba "$ori" --launches 13 \
    --seconds 60 --shires 0x3 --per-shire 8 --seed 1 --kernel "$OUT/accum" --c-log "$OUT/$name.jsonl" --c-poison \
    --dump-tiles "$OUT/$name.tiles" "$@" > "$OUT/$name.out" 2> "$OUT/$name.err"
  echo "$name rc=$?"
}
run b05_sffs fp32 "$T88/e188_a1_b3f800020.bin" "$T78/ones.bin" SFFS
run b05_fssf fp32 "$T88/e188_a1_b3f800020.bin" "$T78/ones.bin" FSSF
run pair_sffs fp32 "$T88/e188_a1_b3f800c00.bin" "$T88/e188_a1_b3f804400.bin" SFFS
run aall_fssf fp32 "$T82/e182_a3fffffff_b1.bin" "$T78/ones.bin" FSSF
run b22_sffs fp32 "$T86/e186_a1_b3fc00000.bin" "$T78/ones.bin" SFFS
# the refusals: a train without --launches, a bad orientation, a built-in --values
"$OUT/sparsity_host_e188" --test fma --type fp32 --pattern none --values "file:$T88/e188_a1_b3f800020.bin" --values-b "file:$T78/ones.bin" \
  --abba SFFS --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_nolaunches.out" 2>&1; echo "refuse_nolaunches rc=$?"
"$OUT/sparsity_host_e188" --test fma --type fp32 --pattern none --values "file:$T88/e188_a1_b3f800020.bin" --values-b "file:$T78/ones.bin" \
  --abba SSFF --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_ori.out" 2>&1; echo "refuse_ori rc=$?"
"$OUT/sparsity_host_e188" --test fma --type fp32 --pattern none --values ones --values-b "file:$T78/ones.bin" \
  --abba SFFS --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_builtin.out" 2>&1; echo "refuse_builtin rc=$?"
# without --values-b the patched host runs a plain run, as the C-logging host does
"$OUT/sparsity_host_e188" --test fma --type fp32 --pattern none --values "file:$T88/e188_a1_b3f800020.bin" --seconds 0.3 --shires 0x3 --per-shire 8 \
  --kernel "$OUT/accum" --c-log "$OUT/plain.jsonl" --c-poison > "$OUT/plain.out" 2> "$OUT/plain.err"; echo "plain rc=$?"
for n in b05_sffs b05_fssf pair_sffs aall_fssf b22_sffs plain; do
  python3 "$R/tools/claims-v3/ccheck/ccheck.py" check "$OUT/$n.jsonl" --jobs 2 --cache "$OUT/cache" > "$OUT/$n.check" 2>&1
  echo "$n ccheck rc=$? $(tail -1 "$OUT/$n.check")"
done
/usr/bin/python3 -B "$R/tools/claims-v3/e188/desktest_host_e188.py" "$OUT"
