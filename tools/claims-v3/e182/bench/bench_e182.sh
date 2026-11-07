#!/bin/bash
# E182 (Q153): the toggle bench on E182's one-number tiles, as it was run on the mini on Sat 7 Nov 2026 (bench/README.md). It is
# E178's bench_e178.sh, step (1) only, with E182's tiles. Run from the Intel. The bench is rtl-sim/fma_toggle_v2 built on the mini with
# Homebrew's Verilator 5.052 (-fno-dfg), the recorded Q141(t2) build (Vtb sha256 a740318c...) that E178's counts came from;
# run_kinds.py, accum.c, settle_count and maps are the repo's, unchanged.
#   BENCH=<the build's directory on the mini>  WORK=<a scratch directory on the mini>  bash bench_e182.sh
# It stages E182's 24 tiles (16 new, 8 committed under their own labels) plus each format's committed zeros tile (run_kinds.py reads all three
# formats' directories; the zeros rows are the build check against E178's counts), then runs
# run_kinds.py over all 27 at its three launch points, 4 jobs -> counts-e182.json (M10's counts form). No VCD reading: the structure
# is E178's (the same RTL and build), read there.
# SPDX-License-Identifier: Apache-2.0
set -eu
: "${BENCH:?the bench build directory on the mini}"
: "${WORK:?a scratch directory on the mini}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
T="$(mktemp -d)"
/usr/bin/python3 -B - "$ROOT" "$HERE" "$T" <<'EOF'
import json, os, shutil, sys
root, here, t = sys.argv[1:4]
for k in json.load(open(os.path.join(here, "kinds-e182.json")))["kinds"]:
    src = os.path.join(here, "tiles", k["type"], k["name"] + ".bin") if k["tile"] == "new" else os.path.join(root, k["tile"].split(":", 1)[1])
    os.makedirs(os.path.join(t, "tiles", k["type"]), exist_ok=True)
    shutil.copyfile(src, os.path.join(t, "tiles", k["type"], k["name"] + ".bin"))
for ty in ("int8", "fp32", "fp16"):
    os.makedirs(os.path.join(t, "tiles", ty), exist_ok=True)
    shutil.copyfile(os.path.join(root, "tools/claims-v3/kinds/tiles", ty, "zeros.bin"), os.path.join(t, "tiles", ty, "zeros.bin"))
EOF
ssh -o BatchMode=yes -o ConnectTimeout=10 mini "mkdir -p $WORK/out $WORK/tmp $WORK/kinds"
rsync -a "$T/tiles" "mini:$WORK/kinds/"
RR="${RUN_REMOTE:-run_remote}"   # the batch-work door (CONTEXT section 28 of the round brief)
"$RR" --host mini --max-gb 6 --timeout 900 --cd "$WORK" -- python3 "$BENCH/run_kinds.py" --bin "$BENCH/obj_vpu/Vtb" \
  --accum "$BENCH/accum" --settle "$BENCH/settle_count" --maps "$BENCH/maps" --kinds "$WORK/kinds" \
  --out "$WORK/out/counts-e182.json" --jobs 4 --tmp "$WORK/tmp"
rsync -a "mini:$WORK/out/counts-e182.json" "$HERE/bench/counts-e182.json"
rm -rf "${T:?}"
