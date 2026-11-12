#!/usr/bin/env bash
# E188 (Q165, the kit): build the train host in build/e188host/ from EXACTLY the pinned build inputs. It is E186's
# tools/claims-v3/e186/build_host_e186.sh (built on aifoundry3 on 9 Nov 2026, TRAIN-HOST-BUILT; itself E182's build_host_e182_v2.sh) with
# two changes, each marked E188: (1) the build directory is build/e188host/, so E188's build, its record and its host never touch E182's
# build/e182host/ or E186's build/e186host/ on the box; (2) THE TRAIN CHANGE IS READ FROM THE BUILT HOST'S BEHAVIOUR, NEVER GREPPED FROM
# ITS BYTES (E183's kit note 4's lesson, binding on E188's kit): E186's last loop grepped the binary for '--c-log', '--c-poison',
# '--values-b', '--abba', '--launches', '--stop-file', 'file:', int8 and fp16, and GCC at -O2 can build a short literal from overlapping
# immediates (E183's two builds on aifoundry3, Thu 12 Nov 2026, each "the host lacks the train change" on a correctly patched host); here
# train_check_e188.sh runs the host with every option of both patches and an empty --kernel (rc 1 at "cannot read kernel ", before any
# device call), and each value option alone (rc 2, "<option> needs a value"). The type strings E186 also grepped (int8, fp16) are not a
# change of the patch: the patched source is pinned by its sha256 before cmake, and every E188 train is fp32.
# Everything else is E186's, line for line, and calls E182's files unchanged: check_inputs_e182.py checks the tree's 8 build inputs and
# E182 note 1's two box files against harness-e182-note1.json, the copy is exactly the 9 build inputs (check_inputs_e182.py --list), checked
# again in the copy (--src) before the patch, and patch_host_e182.py applies Q139(k)'s C-log patch and E182's three flags (--values-b,
# --abba, --launches), so the patched source is the one harness-e182.json registers (train_host_source_sha256), which harness-e188.json
# pins under build/e188host/ (check_e188.py reads it and the build record before every session). build/e188host/SHA256 (the build record)
# is removed with src/ and b/ at the start, so a failed build never leaves an earlier build's record behind. NO device access: nothing here
# opens a card (the check's runs stop before the device, train_check_e188.sh's header gives the lines); build/sparsity, build/ccheck,
# build/e182host and build/e186host are not touched.
#
#   bash tools/claims-v3/e188/build_host_e188.sh          # from anywhere; it runs in the tree that holds it
# Exit 0 and "BUILD OK: ..." last, or 1 ("TRAIN-HOST-INPUTS-DIFFER: ..." when a pin fails; "TRAIN-CHANGE MISSING: ..." when the built host
# does not behave as the patch; else the configure or build log's tail).
# SPDX-License-Identifier: Apache-2.0
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/e188host"                                                                                         # E188 (1)
SRC="$W/src"
mkdir -p "$W"
rm -rf "${W:?}/src" "${W:?}/b" "${W:?}/SHA256"
/usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py ||
  { echo "TRAIN-HOST-INPUTS-DIFFER: the tree's build inputs are not the pinned ones (the lines above): nothing was built"; exit 1; }
mkdir -p "$SRC"
L=$(/usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py --list)
for rel in $L; do
  mkdir -p "$SRC/$(dirname "$rel")"
  cp -p "workloads/sparsity/$rel" "$SRC/$rel"
done
/usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py --src "$SRC" ||
  { echo "TRAIN-HOST-INPUTS-DIFFER: the build's copy is not the pinned inputs (the lines above): nothing was built"; exit 1; }
/usr/bin/python3 -B tools/claims-v3/e182/patch_host_e182.py "$SRC/host/main.cpp"
nice -n 5 cmake -S "$SRC" -B "$W/b" -DCMAKE_PREFIX_PATH=/opt/et > "$W/configure.log" 2>&1 || { tail -20 "$W/configure.log"; exit 1; }
nice -n 5 cmake --build "$W/b" --target sparsity_host -- -j4 > "$W/build.log" 2>&1 || { tail -30 "$W/build.log"; exit 1; }
ls -l "$W/b/host/sparsity_host"
grep -m 3 -iE 'CXX compiler identification|C compiler identification' "$W/configure.log" || true      # the box's compiler, named
sha256sum "$SRC/host/main.cpp" "$W/b/host/sparsity_host" | tee "$W/SHA256"
bash tools/claims-v3/e188/train_check_e188.sh "$W/b/host/sparsity_host" ||                                   # E188 (2)
  { echo "the built host does not behave as the train change (the line above): build/e188host/SHA256 removed"; rm -f "${W:?}/SHA256"; exit 1; }
echo "BUILD OK: build/e188host/b/host/sparsity_host"
