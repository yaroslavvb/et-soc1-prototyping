#!/usr/bin/env bash
# E182 (Q153, the kit's dated note 1; the verifier's MAJOR 2, the E174 class): build the train host in build/e182host/ from EXACTLY the
# pinned build inputs. build_host_e182.sh (v1) stays as committed; this v2 is the runbook's step 6 from now on (rb/s08_a3_preflight_e182_v2.sh).
# Three changes, each marked v2:
#   1. before anything is built, check_inputs_e182.py checks the tree's 8 build inputs (and note 1's two box files) against
#      harness-e182-note1.json; v1 copied whatever workloads/sparsity held on the box, unpinned but for host/main.cpp;
#   2. the copy is exactly the 9 build inputs (check_inputs_e182.py --list), checked again in the copy (--src) before the patch: never
#      `cp -a workloads/sparsity/.`;
#   3. build/e182host/SHA256 (the build record) is removed with src/ and b/ at the start, so a failed build never leaves an earlier
#      build's record behind.
# Everything else is v1's, line for line: patch_host_e182.py on the copy's main.cpp (Q139(k)'s C-log patch, then E182's three flags), the
# same cmake configure and build, the same record (the patched source and the binary, as check_e182.py reads it), the same strings
# checked in the binary. NO device access: nothing here opens a card; build/sparsity and build/ccheck are not touched.
#
#   bash tools/claims-v3/e182/build_host_e182_v2.sh          # from anywhere; it runs in the tree that holds it
# Exit 0 and "BUILD OK: ..." last, or 1 ("TRAIN-HOST-INPUTS-DIFFER: ..." when a pin fails; else the configure or build log's tail).
# SPDX-License-Identifier: Apache-2.0
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/e182host"
SRC="$W/src"
mkdir -p "$W"
rm -rf "${W:?}/src" "${W:?}/b" "${W:?}/SHA256"                                                                   # v2 change 3
/usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py ||
  { echo "TRAIN-HOST-INPUTS-DIFFER: the tree's build inputs are not the pinned ones (the lines above): nothing was built"; exit 1; }   # v2 change 1
mkdir -p "$SRC"
L=$(/usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py --list)                                          # v2 change 2
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
sha256sum "$SRC/host/main.cpp" "$W/b/host/sparsity_host" | tee "$W/SHA256"
for s in '--c-log' '--c-poison' '--values-b' '--abba' '--launches' '--stop-file' 'file:' int8; do
  grep -a -q -- "$s" "$W/b/host/sparsity_host" || { echo "the built host has no $s"; exit 1; }
done
echo "BUILD OK: build/e182host/b/host/sparsity_host"
