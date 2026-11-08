#!/usr/bin/env bash
# E183 (Q155, the kit): the box build of the train host, before the session (KIT.md box step 6, run by rb/s08_a3_build_e183.sh as one
# detached job; no device opens). E180's build (build_e180.sh), with the host-only change on top, in a tree of its own:
#   1. the build inputs at their pins (check_inputs_e183.py: the 37 committed files of workloads/enercat, E180's generator and its appended
#      text, and this kit's patch): else TRAIN-HOST-INPUTS-DIFFER and nothing is built;
#   2. a clean stage of the 37 (build/e183-enercat-stage: those files alone, whatever else the box's workloads/enercat holds), then E180's
#      generator, unchanged (gen_acc_e180.py --src <stage> --dst build/enercat-e183-src), its appended text checked against E180's
#      acc-modes-e180.inc first, as build_e180.sh checks it;
#   3. patch_host_e183.py on that tree's host/main.cpp (the input must be the committed file, the output the pinned one), then the whole
#      tree against harness-e183.json's build_tree (check_inputs_e183.py --src): else TRAIN-HOST-INPUTS-DIFFER, nothing built;
#   4. cmake with the box's own ET toolchain (/opt/et) into build/enercat-e183, `nice -j4` (E180's);
#   5. BUILD-E183.json: the host's and the kernel's sha256, the patched main.cpp's, every source file's of the tree, and the toolchain's
#      version line (no owner or group: E180's kit note 2), which check_e183.py harness --binaries compares before every session;
#   6. the kernel's listing for the desk's loop check (objdump -d into build/e183-kernel-dis.txt, if /opt/et has objdump: reported only).
# Its last line is BUILD OK, or a line naming what failed. Every earlier build's tree, stage, binaries and listing are removed first, so no
# host of an earlier build outlives this one (step 6 refuses a second build after a good one the same day). The runbook's desk test puts a
# stand-in "cmake" first on a stand-in box's PATH (E182's way); nothing here reads a desk variable.
#   bash tools/claims-v3/e183/build_host_e183.sh        # V3_DRY=1: check, stage, generate and patch the tree; build nothing
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
STAGE=build/e183-enercat-stage
SRC=build/enercat-e183-src
OUT=build/enercat-e183
H=tools/claims-v3/e183
E=tools/claims-v3/e180
run() { if [ -n "${V3_DRY:-}" ]; then echo "DRY build: $*" >&2; else "$@"; fi; }
mkdir -p build
python3 -B "$H/check_inputs_e183.py" > build/e183-inputs-build.txt 2>&1 || {
  head -n 12 build/e183-inputs-build.txt; echo "TRAIN-HOST-INPUTS-DIFFER: a build input is off its pin (above): nothing built"; exit 3; }
rm -rf "$OUT" "$SRC" "$STAGE" build/e183-kernel-dis.txt
for rel in $(python3 -B "$H/check_inputs_e183.py" --list); do
  mkdir -p "$STAGE/$(dirname "$rel")" && cp -p "workloads/enercat/$rel" "$STAGE/$rel" || { echo "staging $rel failed"; exit 2; }
done
python3 -B "$E/gen_acc_e180.py" --src "$STAGE" --print > build/acc-modes-e183.check 2>/dev/null ||
  { echo "gen_acc_e180.py --print failed"; exit 2; }
cmp -s build/acc-modes-e183.check "$E/acc-modes-e180.inc" || { echo "the appended modes differ from E180's acc-modes-e180.inc: refusing"; exit 2; }
rm -f build/acc-modes-e183.check
python3 -B "$E/gen_acc_e180.py" --src "$STAGE" --dst "$SRC" || { echo "gen_acc_e180.py failed"; exit 2; }
python3 -B "$H/patch_host_e183.py" "$SRC/host/main.cpp" || { echo "patch_host_e183.py failed: nothing built"; exit 2; }
python3 -B "$H/check_inputs_e183.py" --src "$SRC" > build/e183-tree-check.txt 2>&1 || {
  head -n 12 build/e183-tree-check.txt; echo "TRAIN-HOST-INPUTS-DIFFER: the build tree is not the pinned one (above): nothing built"; exit 3; }
head -n 1 build/e183-tree-check.txt
run cmake -B "$OUT" -S "$SRC" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/enercat-e183-cmake.log 2>&1 || { echo "cmake configure failed (build/enercat-e183-cmake.log)"; exit 1; }
run nice cmake --build "$OUT" -j4 >> build/enercat-e183-cmake.log 2>&1 || { echo "build failed (build/enercat-e183-cmake.log)"; exit 1; }
[ -n "${V3_DRY:-}" ] && { echo "DRY build: done (the patched tree is $SRC; nothing built)"; exit 0; }
[ -x "$OUT/host/enercat_host" ] && [ -f "$OUT/kernel/enercat.elf" ] || { echo "the build left no host or no kernel"; exit 1; }
python3 - "$OUT" "$SRC" <<'PYEOF'
import hashlib, json, os, sys, time
out, src = sys.argv[1], sys.argv[2]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
bins = {f"{out}/host/enercat_host": sha(f"{out}/host/enercat_host"), f"{out}/kernel/enercat.elf": sha(f"{out}/kernel/enercat.elf")}
tree = {}
for d, _dirs, files in os.walk(src):
    for f in sorted(files):
        p = os.path.join(d, f)
        tree[os.path.relpath(p, src)] = sha(p)
ver = ""
try:
    ver = open("/opt/et/VERSION").read().strip()[:200]
except OSError:
    pass
json.dump({"binaries": bins, "patched_main_sha256": sha(f"{src}/host/main.cpp"), "source_tree_sha256": dict(sorted(tree.items())),
           "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "toolchain_version": ver},
          open(f"{out}/BUILD-E183.json", "w"), indent=1, sort_keys=True)
print(json.dumps(bins))
PYEOF
grep -a -q -- '--operands-b' "$OUT/host/enercat_host" && grep -a -q 'train_kind' "$OUT/host/enercat_host" || { echo "the host lacks the train change"; exit 1; }
grep -a -q 'fadd.ps.acc' "$OUT/host/enercat_host" || { echo "the host lacks E180's mode table"; exit 1; }
OD=/opt/et/bin/riscv64-unknown-elf-objdump
if [ -x "$OD" ]; then
  timeout 120 "$OD" -d "$OUT/kernel/enercat.elf" > build/e183-kernel-dis.txt 2>/dev/null && echo "kernel listing: build/e183-kernel-dis.txt ($(wc -l < build/e183-kernel-dis.txt) lines)"
else
  echo "kernel listing: no objdump at $OD (the desk's loop check reads UNREAD)"
fi
echo "BUILD OK: $OUT"
