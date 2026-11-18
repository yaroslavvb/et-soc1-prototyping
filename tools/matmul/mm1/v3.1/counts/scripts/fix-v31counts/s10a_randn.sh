#!/bin/bash
# fix-v31counts step 10a-0: the lab's fp32 randn.bin (E207's e37 arms name it as the pool's pair 0), by git archive of GitHub main 6efdb002
# (= LAB HEAD; LAB is not changed), checked against its tree blob. Desk; no device.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
P=tools/claims-v3/kinds/tiles/fp32/randn.bin
[ "$(git -C "$LAB" rev-parse HEAD)" = "$MAINREV" ] || { echo "LAB HEAD is not $MAINREV"; exit 3; }
git -C "$LAB" archive "$MAINREV" "$P" | tar -x -C "$L/work/lab" || exit 4
blob=$(git -C "$LAB" ls-tree "$MAINREV" -- "$P" | awk '{print $3}')
[ "$(git hash-object "$L/work/lab/$P")" = "$blob" ] && echo "randn.bin equal to its blob $blob" || { echo "randn.bin differs from its blob"; exit 5; }
git -C "$LAB" show "$MAINREV:tools/claims-v3/e207/points-e207.csv" | grep -E '^b4[23],' | sed 's/.*,\([^,]*\)$/\1/' | sed 's/^/E207 e37 arm gen: /'
