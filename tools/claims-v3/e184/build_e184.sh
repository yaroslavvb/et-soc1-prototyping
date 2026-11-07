#!/usr/bin/env bash
# E184 (Q153, the kit): the box build of the energy catalogue with E184's host-only change, before the session (a box step of KIT.md; no
# device opens). host_patch_e184.py copies the committed workloads/enercat into build/enercat-e184-src and makes its four insertions in the
# copy's host/main.cpp (the input must be the committed file, the output the pinned one; nothing committed is edited); then cmake with the
# box's own ET toolchain (/opt/et) into build/enercat-e184, `nice -j4`; then BUILD-E184.json records the host's and the kernel's sha256 and
# the patched source's, which check_e184.py harness --binaries compares before every session. A build that exists is rebuilt only with
# --rebuild (a session never runs on a binary other than the one recorded). The same build serves both arms (arm B uses the stock options).
#   bash tools/claims-v3/e184/build_e184.sh [--rebuild]        # V3_DRY=1: patch into the build tree, build nothing
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
SRC=build/enercat-e184-src
OUT=build/enercat-e184
H=tools/claims-v3/e184
run() { if [ -n "${V3_DRY:-}" ]; then echo "DRY build: $*" >&2; else "$@"; fi; }
if [ -e "$OUT/BUILD-E184.json" ] && [ "${1:-}" != --rebuild ]; then echo "build exists ($OUT/BUILD-E184.json); --rebuild to rebuild"; exit 0; fi
mkdir -p build
python3 -B "$H/host_patch_e184.py" --check workloads/enercat || { echo "the patch does not apply to this tree's workloads/enercat: refusing"; exit 2; }
python3 -B "$H/host_patch_e184.py" --src workloads/enercat --dst "$SRC" || { echo "host_patch_e184.py failed"; exit 2; }
run cmake -B "$OUT" -S "$SRC" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/enercat-e184-cmake.log 2>&1 || { echo "cmake configure failed"; exit 1; }
run nice cmake --build "$OUT" -j4 >> build/enercat-e184-cmake.log 2>&1 || { echo "build failed (build/enercat-e184-cmake.log)"; exit 1; }
[ -n "${V3_DRY:-}" ] && { echo "DRY build: done (the patched tree is $SRC; nothing built)"; exit 0; }
python3 - "$OUT" "$SRC/host/main.cpp" <<'PYEOF'
import hashlib, json, subprocess, sys, time
out, main_cpp = sys.argv[1], sys.argv[2]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
bins = {f"{out}/host/enercat_host": None, f"{out}/kernel/enercat.elf": None}
for p in bins:
    bins[p] = sha(p)
tc = subprocess.run(["bash", "-c", "ls -l /opt/et/bin | head -3; cat /opt/et/VERSION 2>/dev/null"], capture_output=True, text=True).stdout
json.dump({"binaries": bins, "patched_main_sha256": sha(main_cpp), "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "toolchain_listing": tc[-400:]}, open(f"{out}/BUILD-E184.json", "w"), indent=1)
print(json.dumps(bins))
PYEOF
grep -a -q -- '--schedule' "$OUT/host/enercat_host" && grep -a -q -- '--stop-file' "$OUT/host/enercat_host" || { echo "the host lacks --schedule"; exit 1; }
echo "BUILD OK: $OUT"
