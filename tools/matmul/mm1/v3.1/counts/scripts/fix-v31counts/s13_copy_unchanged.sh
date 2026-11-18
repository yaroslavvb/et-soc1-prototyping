#!/bin/bash
# fix-v31counts step 13: the first version's files that the findings do not touch, copied into counts/ unchanged from v31-counts' land
# (verified by its SHA256SUMS in s01; each copy compared byte for byte), and the E213 record re-hashed with the time (its first sha256 kept).
# Desk; no device.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
VL=$VC/land/tools/matmul/mm1/v3.1/counts
for f in recount-check.json recount-check.txt unpriced-mm1v3.json e213-check.json tile-zero-shares.json; do
  cp -p "$VL/$f" "$L/counts/$f" || exit 3
  cmp -s "$VL/$f" "$L/counts/$f" || { echo "copy differs: $f"; exit 4; }
done
for f in crosscheck-launch-fp32.json crosscheck-launch-fp32.txt counts-fp16-int8-launch.json; do
  cmp -s "$VL/$f" "$L/counts/$f" && echo "$f: rebuilt, byte-equal to the first version's" || { echo "$f: rebuilt, DIFFERS"; exit 5; }
done
FIRST=ce95b1620244bd775d1566a4ddb1026f47298685811bb95cbaab97eedcc0e223
h=$(sha256sum < "$L/counts/e213-check.json" | cut -c1-64)
echo "e213-check.json re-hashed at $(ts): $h ($([ "$h" = "$FIRST" ] && echo 'the same as the first version, kept' || echo 'DIFFERS from the first version'))"
[ "$h" = "$FIRST" ] || exit 6
echo "copied unchanged: recount-check.json recount-check.txt unpriced-mm1v3.json e213-check.json tile-zero-shares.json"
