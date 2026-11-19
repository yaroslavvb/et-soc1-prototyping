#!/bin/bash
# counts-e214 (Q225) step 1 (inner; one slot job): the sources, read only, by git archive of commit objects (no working tree is used):
#   from GitHub main (= LAB HEAD 8bde0182; LAB is not changed): rtl-sim/fma_toggle_v2 (the RTL bench), tools/claims-v3/kinds (the lab's kind
#   tiles: train_maps.py and run_kinds.py read them), tools/claims-v3/e210 (E210's desk count code, count_e210.py and its committed counts),
#   tools/claims-v3/e214 (E214's registration and its proposal copy of the model session's src: arms.json, tiles, schedules; NO E214 data
#   folder), MM1-v1's switch table, counts-v2.json, tools/matmul/mm1/v3 (MM1-v3 as landed, for COUNT_FOOTING and energy_v3.counts),
#   and from tools/matmul/mm1/v3.1 only energy_v31.py, mm1_v31.py, data_v31.py, counts/ (3e8991d0's committed counts) and inputs/census/;
#   core-et's rtl, dv/inc, extern and LICENSE by git archive of b38a1a31 from the box's checkout.
# Every extracted file is checked against its commit's blob (git hash-object); the bench copy's one change is Verilator's -j 10 -> -j 2.
# No device is opened; nothing is built here.
set -u
. <W>/out/counts-e214/scripts/env.sh
WK=$L/work
echo "start $(ts); load $(load1)"
[ "$(git -C "$LAB" rev-parse HEAD)" = "$MAINREV" ] || { echo "LAB HEAD is not $MAINREV"; exit 3; }
P_LAB="rtl-sim/fma_toggle_v2 tools/claims-v3/kinds tools/claims-v3/e210 tools/claims-v3/e214 tools/matmul/mm1/v1/inputs/switch_table.json
docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json tools/matmul/mm1/v3 tools/matmul/mm1/v3.1/energy_v31.py tools/matmul/mm1/v3.1/mm1_v31.py
tools/matmul/mm1/v3.1/data_v31.py tools/matmul/mm1/v3.1/counts tools/matmul/mm1/v3.1/inputs/census"
mkdir -p "$WK/lab" "$WK/bench" "$WK/core-et"
# shellcheck disable=SC2086
git -C "$LAB" archive "$MAINREV" $P_LAB | tar -x -C "$WK/lab" || exit 4
# shellcheck disable=SC2086
git -C "$LAB" ls-tree -r "$MAINREV" -- $P_LAB | awk '{print $3" "$4}' > "$WK/lab-tree.txt"
cut -d' ' -f2- "$WK/lab-tree.txt" | sed "s|^|$WK/lab/|" | git hash-object --no-filters --stdin-paths > "$WK/lab-hashes.txt" || exit 4
n=$(wc -l < "$WK/lab-tree.txt")
bad=$(paste -d' ' <(cut -d' ' -f1 "$WK/lab-tree.txt") "$WK/lab-hashes.txt" | awk '$1 != $2' | wc -l)
echo "LAB archive vs commit blobs: $n files, $bad mismatches"
[ "$bad" -eq 0 ] || exit 5
nfiles=$(find "$WK/lab" -type f | wc -l)
echo "files extracted: $nfiles (tree entries $n)"
[ "$nfiles" -eq "$n" ] || { echo "extracted file count differs from the tree"; exit 5; }
# no E214 or E215 data folder is in the archive (by path name only)
grep -c 'docs/reports/data/2026-11-18-e214\|e215' "$WK/lab-tree.txt" | sed 's/^/paths naming an E214 data dir or e215: /'
cp -p "$WK/lab/rtl-sim/fma_toggle_v2/"* "$WK/bench/"
( cd "$WK/bench" && sha256sum * ) > "$WK/bench-copy.sha256"
( cd "$WK/lab/rtl-sim/fma_toggle_v2" && sha256sum * ) > "$WK/bench-src.sha256"
cmp -s "$WK/bench-copy.sha256" "$WK/bench-src.sha256" || { echo "bench copy differs"; exit 5; }
cmp -s "$WK/bench-src.sha256" "$W/out/v31-counts/work/bench-src.sha256" && echo "bench sources: identical manifest to v31-counts' (6efdb002)" \
  || echo "bench sources: manifest DIFFERS from v31-counts'"
sed -i 's/-j 10/-j 2/' "$WK/bench/Makefile"
diff "$WK/lab/rtl-sim/fma_toggle_v2/Makefile" "$WK/bench/Makefile" | sed 's/^/makefile diff: /'
echo "core-et HEAD $(git -C "$CORE" rev-parse HEAD); status lines $(git -C "$CORE" status --short | wc -l)"
git -C "$CORE" archive "$CORE_REV" rtl dv/inc extern LICENSE | tar -x -C "$WK/core-et" || exit 6
( cd "$WK/core-et" && find rtl dv extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-copy.sha256"
( cd "$CORE" && find rtl dv/inc extern -type f | LC_ALL=C sort | xargs sha256sum ) > "$WK/core-et-tree.sha256"
cmp -s "$WK/core-et-copy.sha256" "$WK/core-et-tree.sha256" && echo "core-et archive = the checkout's working tree" || echo "core-et archive DIFFERS from the working tree"
cmp -s "$WK/core-et-copy.sha256" "$W/out/v31-counts/work/core-et-copy.sha256" && echo "core-et manifest identical to v31-counts'" || { echo "core-et manifest differs from v31-counts'"; exit 6; }
echo "core-et copy: $(wc -l < "$WK/core-et-copy.sha256") files; manifest sha256 $(sha256sum < "$WK/core-et-copy.sha256" | cut -c1-64)"
echo "bench sources manifest sha256 $(sha256sum < "$WK/bench-src.sha256" | cut -c1-64)"
echo "end $(ts)"
