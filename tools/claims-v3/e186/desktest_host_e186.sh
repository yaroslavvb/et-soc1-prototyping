#!/usr/bin/env bash
# E186 (Q158, the kit): the train host at the desk, no card, on E186's trains: E182's desk test (tools/claims-v3/e182/desktest_host_e182.sh)
# with E186's tiles and trains. Build workloads/sparsity's host with E182's patch_host_e182.py (unchanged: the host E186's box build makes)
# applied against the check of C's mock runtime (tools/claims-v3/ccheck/mockrt, Q139(k)'s: device memory is host memory and kernelLaunch
# runs a software SP_FMA with rtl-sim/fma_toggle_v2/accum.c's arithmetic on the tiles at the launch's a_tile and b_tile), then run E186's
# trains - THE FP16 TRAIN H16 in both orientations (E186.md section 7: "fp16 trains are new ... the kit's desk test must run an fp16 train
# through the train host against the check of C's mock runtime before the box"), an fp32 train (S23), an fp32 ladder train (B15-B7) and
# two int8 trains (Q63-sign, Q3-swap) - and read them with desktest_host_e186.py: every launch's SPARSITY record and C record follow the
# registered schedule, and ccheck.py judges every launch's C against its own tiles. No device access of any kind.
#
#   bash tools/claims-v3/e186/desktest_host_e186.sh <out-dir>
# SPDX-License-Identifier: Apache-2.0
set -u
OUT=${1:?usage: desktest_host_e186.sh <out-dir>}
mkdir -p "$OUT/src" && OUT=$(cd "$OUT" && pwd)      # E186: the out-dir resolved where it was given, before the cd (E182's form read a
                                                   # relative out-dir against the repository's top)
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
R=$PWD
case "$OUT/" in "$R/"*) echo "the out-dir must be outside the repository"; exit 2 ;; esac
M=$R/tools/claims-v3/ccheck/mockrt
cp "$R/workloads/sparsity/host/main.cpp" "$OUT/src/main.cpp"
/usr/bin/python3 -B "$R/tools/claims-v3/e182/patch_host_e182.py" "$OUT/src/main.cpp" > "$OUT/patch.log" 2>&1 || { cat "$OUT/patch.log"; exit 1; }
nice -n 10 c++ -std=c++17 -O1 -Wall -Wno-unused-variable -I "$M/include" -I "$R/workloads/sparsity" "$OUT/src/main.cpp" "$M/mock_rt.cpp" \
  -o "$OUT/sparsity_host_e186" > "$OUT/build.log" 2>&1 || { tail -30 "$OUT/build.log"; exit 1; }
cc -O2 -o "$OUT/accum" "$R/rtl-sim/fma_toggle_v2/accum.c" -lm || exit 1
export MOCK_ACCUM=$OUT/accum MOCK_SLEEP_MS=20
T=$R/tools/claims-v3/m12/tiles
T78=$R/tools/claims-v3/kinds/tiles
run() { # name type F S orientation extra...
  local name=$1 ty=$2 f=$3 s=$4 ori=$5; shift 5
  rm -f "$OUT/$name.jsonl"
  "$OUT/sparsity_host_e186" --test fma --type "$ty" --pattern none --values "file:$f" --values-b "file:$s" --abba "$ori" --launches 13 \
    --seconds 60 --shires 0x3 --per-shire 8 --seed 1 --kernel "$OUT/accum" --c-log "$OUT/$name.jsonl" --c-poison \
    --dump-tiles "$OUT/$name.tiles" "$@" > "$OUT/$name.out" 2> "$OUT/$name.err"
  echo "$name rc=$?"
}
run h16_sffs fp16 "$T/fp16/m12_a3c00_b3fff.bin" "$T/fp16/m12_a3fff_b3c00.bin" SFFS
run h16_fssf fp16 "$T/fp16/m12_a3c00_b3fff.bin" "$T/fp16/m12_a3fff_b3c00.bin" FSSF
run s23_fssf fp32 "$T/fp32/m12_a1_b3f80ffff.bin" "$T/fp32/m12_a3f80ffff_b1.bin" FSSF
run b157_fssf fp32 "$T/fp32/m12_a1_b3f8000ff.bin" "$T78/fp32/ones.bin" FSSF
run q63s_fssf int8 "$T/int8/m12_am1_bm63.bin" "$T/int8/m12_a1_b63.bin" FSSF
run q3w_fssf int8 "$T/int8/m12_a1_b3.bin" "$T/int8/m12_a3_b1.bin" FSSF
# the refusals: a train without --launches, a bad orientation, a built-in --values
"$OUT/sparsity_host_e186" --test fma --type fp16 --pattern none --values "file:$T/fp16/m12_a3c00_b3fff.bin" --values-b "file:$T/fp16/m12_a3fff_b3c00.bin" \
  --abba SFFS --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_nolaunches.out" 2>&1; echo "refuse_nolaunches rc=$?"
"$OUT/sparsity_host_e186" --test fma --type fp16 --pattern none --values "file:$T/fp16/m12_a3c00_b3fff.bin" --values-b "file:$T/fp16/m12_a3fff_b3c00.bin" \
  --abba SSFF --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_ori.out" 2>&1; echo "refuse_ori rc=$?"
"$OUT/sparsity_host_e186" --test fma --type fp16 --pattern none --values ones --values-b "file:$T/fp16/m12_a3fff_b3c00.bin" \
  --abba SFFS --launches 13 --seconds 1 --shires 0x3 --per-shire 8 --kernel "$OUT/accum" > "$OUT/refuse_builtin.out" 2>&1; echo "refuse_builtin rc=$?"
# without --values-b the patched host runs a plain run, as the C-logging host does
"$OUT/sparsity_host_e186" --test fma --type fp16 --pattern none --values "file:$T/fp16/m12_a3c00_b3fff.bin" --seconds 0.3 --shires 0x3 --per-shire 8 \
  --kernel "$OUT/accum" --c-log "$OUT/plain.jsonl" --c-poison > "$OUT/plain.out" 2> "$OUT/plain.err"; echo "plain rc=$?"
for n in h16_sffs h16_fssf s23_fssf b157_fssf q63s_fssf q3w_fssf plain; do
  python3 "$R/tools/claims-v3/ccheck/ccheck.py" check "$OUT/$n.jsonl" --jobs 2 --cache "$OUT/cache" > "$OUT/$n.check" 2>&1
  echo "$n ccheck rc=$? $(tail -1 "$OUT/$n.check")"
done
/usr/bin/python3 -B "$R/tools/claims-v3/e186/desktest_host_e186.py" "$OUT"
