#!/usr/bin/env bash
# E180 (Q146(f), the kit): the box build of the energy catalogue with E180's two accumulating modes, before the session (a box step of
# KIT.md; no device opens). gen_acc_e180.py copies the committed workloads/enercat into build/enercat-e180-src and appends modes 261-262
# there (nothing committed is edited); the text it appends must equal the registration's acc-modes-e180.inc; then cmake with the box's
# own ET toolchain (/opt/et) into build/enercat-e180, `nice -j4`; then BUILD-E180.json records the host's and the kernel's sha256 and
# the toolchain's, which check_e180.py harness --binaries compares before every session. A build that already exists is rebuilt only
# with --rebuild (a session never runs on a binary other than the one recorded).
#
#   bash tools/claims-v3/e180/build_e180.sh [--rebuild]        # V3_DRY=1: print the steps, build nothing
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
SRC=build/enercat-e180-src
OUT=build/enercat-e180
H=tools/claims-v3/e180
run() { if [ -n "${V3_DRY:-}" ]; then echo "DRY build: $*" >&2; else "$@"; fi; }
if [ -e "$OUT/BUILD-E180.json" ] && [ "${1:-}" != --rebuild ]; then echo "build exists ($OUT/BUILD-E180.json); --rebuild to rebuild"; exit 0; fi
mkdir -p build
python3 -B "$H/gen_acc_e180.py" --src workloads/enercat --print > build/acc-modes-e180.check 2>/dev/null ||
  { echo "gen_acc_e180.py --print failed"; exit 2; }
cmp -s build/acc-modes-e180.check "$H/acc-modes-e180.inc" || { echo "the appended modes differ from acc-modes-e180.inc: refusing"; exit 2; }
rm -f build/acc-modes-e180.check
run python3 -B "$H/gen_acc_e180.py" --src workloads/enercat --dst "$SRC" || { echo "gen_acc_e180.py failed"; exit 2; }
run cmake -B "$OUT" -S "$SRC" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/enercat-e180-cmake.log 2>&1 || { echo "cmake configure failed"; exit 1; }
run nice cmake --build "$OUT" -j4 >> build/enercat-e180-cmake.log 2>&1 || { echo "build failed (build/enercat-e180-cmake.log)"; exit 1; }
[ -n "${V3_DRY:-}" ] && { echo "DRY build: done (nothing built)"; exit 0; }
python3 - "$OUT" "$H/acc-modes-e180.inc" <<'PYEOF'
import hashlib, json, os, subprocess, sys, time
out, inc = sys.argv[1], sys.argv[2]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
bins = {f"{out}/host/enercat_host": None, f"{out}/kernel/enercat.elf": None}
for p in bins:
    bins[p] = sha(p)
tc = subprocess.run(["bash", "-c", "ls -l /opt/et/bin | head -3; cat /opt/et/VERSION 2>/dev/null"], capture_output=True, text=True).stdout
json.dump({"binaries": bins, "acc_modes_inc_sha256": hashlib.sha256(open(inc, "rb").read()).hexdigest(),
           "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "toolchain_listing": tc[-400:]},
          open(f"{out}/BUILD-E180.json", "w"), indent=1)
print(json.dumps(bins))
PYEOF
grep -a -q 'fadd.ps.acc' "$OUT/host/enercat_host" && grep -a -q 'fadd.pi.acc' "$OUT/host/enercat_host" || { echo "the host lacks the two modes"; exit 1; }
echo "BUILD OK: $OUT"
