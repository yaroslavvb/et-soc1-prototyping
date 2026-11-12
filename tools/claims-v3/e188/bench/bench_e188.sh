#!/bin/bash
# E188 (registration): the toggle bench on E188's bench rows (kinds-e188.json > bench_rows: every kind with no committed counts, and six
# reference rows re-run and checked by forecast_e188.py against their committed counts point for point), in the form of
# tools/claims-v3/m12/bench/bench_m12_e186.sh: rtl-sim/fma_toggle_v2 as built on the mini with Homebrew's Verilator 5.052 (-fno-dfg), the
# recorded build E178's, E182's, M12's and E186's counts came from (docs/reports/data/2026-11-04-q141t-s7-recount/step243/
# build-record-mini.json: Vtb a740318c..., accum aeddf308..., settle_count 9da18b75..., and its inputs run_kinds.py and the three maps).
# Every binary and input is checked against that record's sha256 before the run; a mismatch stops it. Run from the Intel:
#   BENCH=<the build's directory on the mini>  MAPS=<a local directory holding the record's three maps>  WORK=<a new scratch directory on
#   the mini>  STAGE=<an empty local directory>  bash tools/claims-v3/e188/bench/bench_e188.sh
# It stages every bench row's tile under STAGE/kinds/tiles/fp32/<name>.bin, copies run_kinds.py (the repository's), the maps and the tiles
# to WORK on the mini, runs run_kinds.py over all of them at its three launch points through the batch-work door, and copies
# counts-e188.json back beside this script.
# SPDX-License-Identifier: Apache-2.0
set -eu
: "${BENCH:?the bench build directory on the mini}"
: "${MAPS:?a local directory with unit_float.map, unit_int8.map and vpu.map}"
: "${WORK:?a new scratch directory on the mini}"
: "${STAGE:?an empty local staging directory}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
REC="$ROOT/docs/reports/data/2026-11-04-q141t-s7-recount/step243/build-record-mini.json"
/usr/bin/python3 -B - "$ROOT" "$HERE" "$STAGE" "$MAPS" "$REC" <<'EOF'
import hashlib, json, os, shutil, sys
root, here, st, maps, rec = sys.argv[1:6]
r = json.load(open(rec))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
for k, want in r["inputs"].items():
    p = os.path.join(root, "rtl-sim/fma_toggle_v2/run_kinds.py") if k == "run_kinds.py" else os.path.join(maps, os.path.basename(k))
    assert sha(p) == want, ("input differs from the build record", k)
os.makedirs(os.path.join(st, "kinds", "tiles", "fp32"))
os.makedirs(os.path.join(st, "maps"))
for k in ("unit_float.map", "unit_int8.map", "vpu.map"):
    shutil.copyfile(os.path.join(maps, k), os.path.join(st, "maps", k))
shutil.copyfile(os.path.join(root, "rtl-sim/fma_toggle_v2/run_kinds.py"), os.path.join(st, "run_kinds.py"))
for b in json.load(open(os.path.join(here, "kinds-e188.json")))["bench_rows"]:
    t, name = b["key"].split(".", 1)
    dst = os.path.join(st, "kinds", "tiles", t, name + ".bin")
    assert not os.path.exists(dst), dst
    shutil.copyfile(os.path.join(root, b["tile"]), dst)
json.dump({k: v for k, v in r["binaries"].items()}, open(os.path.join(st, "binaries.json"), "w"))
print("staged", len(os.listdir(os.path.join(st, "kinds", "tiles", "fp32"))), "tiles")
EOF
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10 mini"
$SSH "test ! -e $WORK && mkdir -p $WORK/out $WORK/tmp"
# the build's binaries on the mini against the record
got=$($SSH "cd $BENCH && shasum -a 256 obj_vpu/Vtb accum settle_count")
/usr/bin/python3 -B - "$STAGE/binaries.json" "$got" <<'EOF'
import json, sys
want = json.load(open(sys.argv[1]))
got = {l.split()[1]: l.split()[0] for l in sys.argv[2].strip().splitlines()}
for k, v in want.items():
    assert got.get(k) == v, ("binary differs from the build record", k, got.get(k))
print("binaries match the build record:", ", ".join(sorted(want)))
EOF
rsync -a "$STAGE/kinds" "$STAGE/maps" "$STAGE/run_kinds.py" "mini:$WORK/"
RR="${RUN_REMOTE:-run_remote}"   # the batch-work door
"$RR" --host mini --max-gb 4 --timeout 900 --cd "$WORK" -- python3 "$WORK/run_kinds.py" --bin "$BENCH/obj_vpu/Vtb" \
  --accum "$BENCH/accum" --settle "$BENCH/settle_count" --maps "$WORK/maps" --kinds "$WORK/kinds" \
  --out "$WORK/out/counts-e188.json" --types fp32 --jobs 4 --tmp "$WORK/tmp"
rsync -a "mini:$WORK/out/counts-e188.json" "$HERE/bench/counts-e188.json"
