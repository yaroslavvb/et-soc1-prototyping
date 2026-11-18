#!/bin/bash
# v31-counts (Q217) step 2: the sources, read only. From GitHub main (= LAB HEAD 6efdb002, read with git archive: LAB is not changed):
#   rtl-sim/fma_toggle_v2 (the RTL bench), tools/claims-v3/kinds (the lab's kind tiles, which train_maps.py and run_kinds.py read),
#   tools/claims-v3/e210 (E210's desk count code: count_e210.py, hd_model_e210.py, spec_e210.py, gen_tiles_e210.cpp, drawtile_e210.h,
#   switch_counts_e210.py, and its committed counts-e210-S1/S2.json and switch-counts-e210.json), tools/claims-v3/e212/proposal/src/tiles
#   (E212's 30 tile files), tools/matmul/mm1/v1/inputs/switch_table.json (MM1-v1's frozen table: the unit constants),
#   docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json (the committed counts the table was made from);
# and core-et's rtl, dv/inc and extern from the box's checkout at b38a1a31 (the commit E210 and sw-design-a built against), copied.
# Every copied file's sha256 is recorded and compared with its source. No device is opened; nothing is built here.
set -u
. <W>/out/v31-counts/scripts/env.sh
CORE=<CORE_ET>
WK=$L/work
echo "$(ts) start"
[ "$(git -C "$LAB" rev-parse HEAD)" = "$MAINREV" ] || { echo "LAB HEAD is not $MAINREV"; exit 3; }
mkdir -p "$WK/lab" "$WK/bench" "$WK/core-et/dv"
git -C "$LAB" archive "$MAINREV" rtl-sim/fma_toggle_v2 tools/claims-v3/kinds tools/claims-v3/e210 tools/claims-v3/e212/proposal/src/tiles \
  tools/matmul/mm1/v1/inputs/switch_table.json docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json | tar -x -C "$WK/lab" || exit 4
# the archive's files against the commit's blobs (git hash-object of each extracted file = the tree's blob id)
( cd "$WK/lab" && git -C "$LAB" ls-tree -r "$MAINREV" -- rtl-sim/fma_toggle_v2 tools/claims-v3/kinds tools/claims-v3/e210 \
    tools/claims-v3/e212/proposal/src/tiles tools/matmul/mm1/v1/inputs/switch_table.json docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json \
    | awk '{print $3" "$4}' > "$WK/lab-tree.txt" )
bad=0; n=0
while read -r blob path; do
  n=$((n+1)); h=$(git hash-object "$WK/lab/$path"); [ "$h" = "$blob" ] || { bad=$((bad+1)); echo "MISMATCH $path"; }
done < "$WK/lab-tree.txt"
echo "archive vs commit blobs: $n files, $bad mismatches"
[ "$bad" -eq 0 ] || exit 5
cp -p "$WK/lab/rtl-sim/fma_toggle_v2/"* "$WK/bench/"
( cd "$WK/bench" && sha256sum * ) > "$WK/bench-copy.sha256"
( cd "$WK/lab/rtl-sim/fma_toggle_v2" && sha256sum * ) > "$WK/bench-src.sha256"
cmp -s "$WK/bench-copy.sha256" "$WK/bench-src.sha256" || { echo "bench copy differs"; exit 5; }
# LAB's working tree copy of the bench, compared (read only)
( cd "$LAB/rtl-sim/fma_toggle_v2" && sha256sum * ) > "$WK/bench-labtree.sha256"
cmp -s "$WK/bench-copy.sha256" "$WK/bench-labtree.sha256" && echo "bench: equal to LAB's working tree" || echo "bench: DIFFERS from LAB's working tree"
sed -i 's/-j 10/-j 2/' "$WK/bench/Makefile"
grep -c -- '-j 2' "$WK/bench/Makefile"
echo "core-et HEAD $(git -C "$CORE" rev-parse HEAD); status lines $(git -C "$CORE" status --short | wc -l)"
[ "$(git -C "$CORE" rev-parse HEAD)" = "b38a1a31da67efe00c61e983e64b892c58080115" ] || { echo "core-et is not at b38a1a31"; exit 6; }
cp -a "$CORE/rtl" "$WK/core-et/"
cp -a "$CORE/dv/inc" "$WK/core-et/dv/"
cp -a "$CORE/extern" "$WK/core-et/"
cp -p "$CORE/LICENSE" "$WK/core-et/" 2>/dev/null
( cd "$WK/core-et" && find rtl dv extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-copy.sha256"
( cd "$CORE" && find rtl dv/inc extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-src.sha256"
cmp -s "$WK/core-et-copy.sha256" "$WK/core-et-src.sha256" || { echo "core-et copy differs"; exit 5; }
echo "core-et copy: $(wc -l < "$WK/core-et-copy.sha256") files equal; manifest sha256 $(sha256sum < "$WK/core-et-copy.sha256" | cut -c1-64)"
cmp -s "$WK/core-et-copy.sha256" "$W/out/sw-design-a/work/core-et-rtl.sha256" && echo "same rtl manifest as sw-design-a" || echo "(manifest differs in scope from sw-design-a's rtl-only file; fine)"
echo "bench sources sha256 (as built):"; cat "$WK/bench-src.sha256"
echo "$(ts) end"
