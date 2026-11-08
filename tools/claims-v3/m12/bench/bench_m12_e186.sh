#!/bin/bash
# M12 for E186 (Q158): the toggle bench on the merged list's kinds that M12's bench never ran (kinds-m12-e186.json > bench_rows), in the
# form of bench_m12.sh: rtl-sim/fma_toggle_v2 built on the mini with Homebrew's Verilator 5.052 (-fno-dfg), the recorded build E178's,
# E182's and M12's counts came from (Vtb sha256 a740318c..., docs/reports/data/2026-11-04-q141t-s7-recount/step243/build-record-mini.json);
# run_kinds.py, accum.c, settle_count and maps are the repo's, unchanged. Run from the Intel:
#   BENCH=<the build's directory on the mini>  WORK=<a scratch directory on the mini>  STAGE=<an empty local directory>  bash bench_m12_e186.sh
# It stages every bench row's tile under STAGE/tiles/<type>/<name>.bin (the new tiles from tiles-e186/, the committed ones at their
# committed paths; the references: each format's zeros, fp32.ones, E182's (1.0, 0x3fffffff) and one M12 tile a format, each checked by
# candidates_m12_e186.py against its committed counts), copies them to the mini, runs run_kinds.py over all of them at its three launch
# points through the batch-work door, and copies counts-m12-e186.json back beside this script.
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
for b in json.load(open(os.path.join(here, "kinds-m12-e186.json")))["bench_rows"]:
    t, name = b["key"].split(".", 1)
    os.makedirs(os.path.join(st, "tiles", t), exist_ok=True)
    dst = os.path.join(st, "tiles", t, name + ".bin")
    assert not os.path.exists(dst), dst
    shutil.copyfile(os.path.join(root, b["tile"]), dst)
EOF
ssh -o BatchMode=yes -o ConnectTimeout=10 mini "mkdir -p $WORK/out $WORK/tmp $WORK/kinds"
rsync -a "$STAGE/tiles" "mini:$WORK/kinds/"
RR="${RUN_REMOTE:-run_remote}"   # the batch-work door
"$RR" --host mini --max-gb 4 --timeout 900 --cd "$WORK" -- python3 "$BENCH/run_kinds.py" --bin "$BENCH/obj_vpu/Vtb" \
  --accum "$BENCH/accum" --settle "$BENCH/settle_count" --maps "$BENCH/maps" --kinds "$WORK/kinds" \
  --out "$WORK/out/counts-m12-e186.json" --jobs 4 --tmp "$WORK/tmp"
rsync -a "mini:$WORK/out/counts-m12-e186.json" "$HERE/bench/counts-m12-e186.json"
