#!/bin/bash
# counts-e217 (decl-e217 step 4; counts-e214's script) step 4 (inner; inside W/slot.sh + W/nodev.sh): the bench's functional check (fcheck_all.sh: one txfma_top over 40,000 vectors
# in fp32 and fp16; whole TensorFMA ops in three formats; the zero gate), which must PASS before any count is quoted. JOBS=1 (one bench
# process). Then step 4b: E212's 30 registered tile files by git archive of GitHub main 8bde0182 (the re-counts' tiles; checked against
# their blobs). No device is opened.
set -u
. <W>/out/decl-e217/scripts/cnt/env.sh
if quiet_flag; then echo "QUIET DESK FLAG present: not running"; exit 3; fi
mkdir -p "$L/work/fcheck"
echo "start $(ts); load $(load1)"
( cd "$L/work/bench" && JOBS=1 PY=/usr/bin/python3 bash fcheck_all.sh "$L/work/fcheck" )
rc=$?
echo "fcheck rc $rc; $(ts)"
P=tools/claims-v3/e212/proposal/src/tiles
git -C "$LAB" archive "$MAINREV" "$P" | tar -x -C "$L/work/lab" || exit 4
git -C "$LAB" ls-tree -r "$MAINREV" -- "$P" | awk '{print $3" "$4}' > "$L/work/lab-tree-e212tiles.txt"
cut -d' ' -f2- "$L/work/lab-tree-e212tiles.txt" | sed "s|^|$L/work/lab/|" | git hash-object --no-filters --stdin-paths > "$L/work/lab-hashes-e212tiles.txt" || exit 4
bad=$(paste -d' ' <(cut -d' ' -f1 "$L/work/lab-tree-e212tiles.txt") "$L/work/lab-hashes-e212tiles.txt" | awk '$1 != $2' | wc -l)
echo "E212 tiles archive vs commit blobs: $(wc -l < "$L/work/lab-tree-e212tiles.txt") files, $bad mismatches"
[ "$bad" -eq 0 ] || exit 5
echo "end $(ts)"
exit $rc
