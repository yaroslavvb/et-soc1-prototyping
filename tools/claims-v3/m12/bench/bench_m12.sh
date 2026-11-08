#!/bin/bash
# M12 (Q157): the toggle bench on M12's candidate kinds (REFIT.md section 5), in the form of E182's bench_e182.sh: rtl-sim/fma_toggle_v2
# built on the mini with Homebrew's Verilator 5.052 (-fno-dfg), the recorded build E178's and E182's counts came from (Vtb sha256
# a740318c...); run_kinds.py, accum.c, settle_count and maps are the repo's, unchanged. Run from the Intel:
#   BENCH=<the build's directory on the mini>  WORK=<a scratch directory on the mini>  STAGE=<an empty local directory>  bash bench_m12.sh
# It stages kinds-m12.json's tiles (new ones from tiles/, the references at their committed paths) plus each format's committed zeros
# tile (the build check against E178's counts) under STAGE/tiles/<type>/<name>.bin, copies them to the mini, runs run_kinds.py over
# all of them at its three launch points through the batch-work door, and copies counts-m12.json back beside this script.
# SPDX-License-Identifier: Apache-2.0
set -eu
: "${BENCH:?the bench build directory on the mini}"
: "${WORK:?a scratch directory on the mini}"
: "${STAGE:?an empty local staging directory}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
/usr/bin/python3 -B - "$ROOT" "$HERE" "$STAGE" <<'EOF'
import json, os, shutil, sys
root, here, st = sys.argv[1:4]
for k in json.load(open(os.path.join(here, "kinds-m12.json")))["kinds"]:
    os.makedirs(os.path.join(st, "tiles", k["type"]), exist_ok=True)
    shutil.copyfile(os.path.join(root, k["tile"]), os.path.join(st, "tiles", k["type"], k["name"] + ".bin"))
for ty in ("int8", "fp32", "fp16"):
    os.makedirs(os.path.join(st, "tiles", ty), exist_ok=True)
    shutil.copyfile(os.path.join(root, "tools/claims-v3/kinds/tiles", ty, "zeros.bin"), os.path.join(st, "tiles", ty, "zeros.bin"))
EOF
ssh -o BatchMode=yes -o ConnectTimeout=10 mini "mkdir -p $WORK/out $WORK/tmp $WORK/kinds"
rsync -a "$STAGE/tiles" "mini:$WORK/kinds/"
RR="${RUN_REMOTE:-run_remote}"   # the batch-work door
"$RR" --host mini --max-gb 4 --timeout 900 --cd "$WORK" -- python3 "$BENCH/run_kinds.py" --bin "$BENCH/obj_vpu/Vtb" \
  --accum "$BENCH/accum" --settle "$BENCH/settle_count" --maps "$BENCH/maps" --kinds "$WORK/kinds" \
  --out "$WORK/out/counts-m12.json" --jobs 4 --tmp "$WORK/tmp"
rsync -a "mini:$WORK/out/counts-m12.json" "$HERE/bench/counts-m12.json"
