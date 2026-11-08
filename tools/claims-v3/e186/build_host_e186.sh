#!/usr/bin/env bash
# E186 (Q158, the kit): build the train host in build/e186host/ from EXACTLY the pinned build inputs. It is E182's
# tools/claims-v3/e182/build_host_e182_v2.sh (E182's kit note 1; built on aifoundry3 on 8 Nov 2026, TRAIN-HOST-BUILT) with two changes,
# each marked E186: (1) the build directory is build/e186host/, so E186's build, its record and its host never touch E182's
# build/e182host/ on the box; (2) the built binary is also checked to hold the string fp16 (H16 is E186's first fp16 train).
# Everything else is E182's v2, line for line, and calls E182's files unchanged: check_inputs_e182.py checks the tree's 8 build inputs
# and E182 note 1's two box files against harness-e182-note1.json, the copy is exactly the 9 build inputs (check_inputs_e182.py
# --list), checked again in the copy (--src) before the patch, and patch_host_e182.py applies Q139(k)'s C-log patch and E182's three
# flags (--values-b, --abba, --launches), so the patched source is the one harness-e182.json registers (train_host_source_sha256), which
# harness-e186.json pins under build/e186host/. The patch is type-blind: an fp16 train runs this host with --type fp16 (the kit's desk
# test, desktest_host_e186.sh). build/e186host/SHA256 (the build record) is removed with src/ and b/ at the start, so a failed build never
# leaves an earlier build's record behind. NO device access: nothing here opens a card; build/sparsity, build/ccheck and build/e182host
# are not touched.
#
#   bash tools/claims-v3/e186/build_host_e186.sh          # from anywhere; it runs in the tree that holds it
# Exit 0 and "BUILD OK: ..." last, or 1 ("TRAIN-HOST-INPUTS-DIFFER: ..." when a pin fails; else the configure or build log's tail).
# SPDX-License-Identifier: Apache-2.0
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
W="$ROOT/build/e186host"                                                                                         # E186
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
sha256sum "$SRC/host/main.cpp" "$W/b/host/sparsity_host" | tee "$W/SHA256"
for s in '--c-log' '--c-poison' '--values-b' '--abba' '--launches' '--stop-file' 'file:' int8 fp16; do      # E186 (2): fp16 too
  grep -a -q -- "$s" "$W/b/host/sparsity_host" || { echo "the built host has no $s"; exit 1; }
done
echo "BUILD OK: build/e186host/b/host/sparsity_host"
