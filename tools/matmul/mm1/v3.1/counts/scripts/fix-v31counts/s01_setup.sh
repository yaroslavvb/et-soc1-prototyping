#!/bin/bash
# fix-v31counts (Q217) step 1: the inputs, read only (desk; nothing is built; no device).
#  (a) From GitHub main (= LAB HEAD 6efdb002, read with git archive: LAB is not changed): E210's desk folder (count_e210.py, hd_model_e210.py,
#      the committed switch-counts-e210.json and counts-e210-S1/S2.json), E207's two fp32 blind4 tiles, MM1-v1's switch table, counts-v2.json,
#      MM1-v3's mm1_v3.py (its COUNT_FOOTING) and the bench's run_kinds.py; every extracted file checked against its tree blob.
#  (b) v31-counts' build, unchanged, copied (not rebuilt): obj_vpu/Vtb, settle_count, run_kinds.py and the three net maps, each checked
#      against the sha256 v31-counts recorded in its SOURCES.json (so the re-count runs on the binary that made the published rows).
#  (c) v31-counts' land dir (SHA256SUMS 76ad5d97..., checked) and the work files its table script reads (its raw bench outputs, the tile
#      inventory, the desk tiles' list, the two source manifests), copied into this lane's folder.
set -u
. <W>/out/fix-v31counts/scripts/env.sh
WK=$L/work
VL=$VC/land/tools/matmul/mm1/v3.1/counts
echo "$(ts) start"
[ "$(git -C "$LAB" rev-parse HEAD)" = "$MAINREV" ] || { echo "LAB HEAD is not $MAINREV"; exit 3; }
mkdir -p "$WK/lab" "$WK/bench/obj_vpu" "$WK/maps" "$WK/counts" "$WK/old" "$WK/dsk" "$WK/tmp"
P="tools/claims-v3/e210/desk tools/claims-v3/kinds/blind4/tiles/fp32 tools/matmul/mm1/v1/inputs/switch_table.json docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json tools/matmul/mm1/v3/mm1_v3.py rtl-sim/fma_toggle_v2/run_kinds.py"
git -C "$LAB" archive "$MAINREV" $P | tar -x -C "$WK/lab" || exit 4
git -C "$LAB" ls-tree -r "$MAINREV" -- $P | awk '{print $1" "$3" "$4}' > "$WK/lab-tree.txt"
bad=0; n=0
while read -r mode blob path; do
  n=$((n+1))
  [ "$mode" = "120000" ] && continue
  h=$(git hash-object "$WK/lab/$path"); [ "$h" = "$blob" ] || { bad=$((bad+1)); echo "MISMATCH $path"; }
done < "$WK/lab-tree.txt"
echo "(a) lab archive vs commit blobs: $n entries, $bad mismatches"
[ "$bad" -eq 0 ] || exit 5
# (b) v31-counts' build and maps, copied
cp -p "$VC/work/bench/obj_vpu/Vtb" "$WK/bench/obj_vpu/Vtb" || exit 6
cp -p "$VC/work/bench/settle_count" "$VC/work/bench/run_kinds.py" "$WK/bench/" || exit 6
cp -p "$VC/work/maps/"*.map "$WK/maps/" || exit 6
$PY - "$VC/counts/SOURCES.json" "$WK" <<'EOF' || exit 7
import hashlib, json, os, sys
src = json.load(open(sys.argv[1])); wk = sys.argv[2]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
bad = 0
for b in ('obj_vpu/Vtb', 'settle_count'):
    ok = sha(os.path.join(wk, 'bench', b)) == src['binaries_sha256'][b]; bad += not ok
    print(f"(b) {b}: {'EQUAL' if ok else 'DIFFERS'} to v31-counts' recorded sha256 {src['binaries_sha256'][b][:16]}...")
for m, h in src['maps_sha256'].items():
    ok = sha(os.path.join(wk, 'maps', m)) == h; bad += not ok
    print(f"(b) map {m}: {'EQUAL' if ok else 'DIFFERS'} ({h[:16]}...)")
for p in ('rtl-sim/fma_toggle_v2/run_kinds.py', 'tools/claims-v3/e210/desk/count_e210.py', 'tools/claims-v3/e210/desk/hd_model_e210.py'):
    ok = sha(os.path.join(wk, 'lab', p)) == src['drivers_sha256'][p]; bad += not ok
    print(f"(a) {p}: {'EQUAL' if ok else 'DIFFERS'} to SOURCES.json's driver sha256")
ok = sha(os.path.join(wk, 'bench', 'run_kinds.py')) == src['drivers_sha256']['rtl-sim/fma_toggle_v2/run_kinds.py']; bad += not ok
print(f"(b) bench run_kinds.py copy: {'EQUAL' if ok else 'DIFFERS'} to the committed one")
for p, h in src['committed_references_sha256'].items():
    q = os.path.join(wk, 'lab', p)
    if os.path.exists(q):
        ok = sha(q) == h; bad += not ok
        print(f"(a) {p}: {'EQUAL' if ok else 'DIFFERS'} to SOURCES.json")
for p in ('tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_pythia_embed_qkv.bin', 'tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_qwen_q_down.bin'):
    ok = sha(os.path.join(wk, 'lab', p)) == src['tiles_sha256'][p]['sha256']; bad += not ok
    print(f"(a) tile {os.path.basename(p)}: {'EQUAL' if ok else 'DIFFERS'} to SOURCES.json ({src['tiles_sha256'][p]['sha256'][:16]}...)")
sys.exit(1 if bad else 0)
EOF
# (c) v31-counts' land (checked against its own SHA256SUMS, whose sha256 must be 76ad5d97...) and its work files
( cd "$VL" && sha256sum -c --quiet SHA256SUMS ) || { echo "v31-counts land: SHA256SUMS does not verify"; exit 8; }
h=$(sha256sum < "$VL/SHA256SUMS" | cut -c1-64)
[ "$h" = "76ad5d9719b173e47f0b090e819bae277b45dde60562a8042892a42d45e89c10" ] || { echo "v31-counts land SHA256SUMS is $h, not 76ad5d97..."; exit 8; }
echo "(c) v31-counts land: $(wc -l < "$VL/SHA256SUMS") files verify; SHA256SUMS sha256 $h"
cp -p "$VL/raw/"*.json "$WK/counts/" || exit 9
for f in README.md counts-fp32-gemm-states.json counts-fp16-int8-launch.json counts-v31.csv counts-v31-tiles.csv SOURCES.json e213-check.json; do
  cp -p "$VL/$f" "$WK/old/$f" || exit 9
done
cp -p "$VC/work/tiles-inventory.json" "$VC/work/bench-src.sha256" "$VC/work/core-et-copy.sha256" "$WK/" || exit 9
cp -p "$VC/work/dsk/tiles-made.sha256" "$WK/dsk/tiles-made.sha256" || exit 9
cmp -s "$WK/dsk/tiles-made.sha256" "$VL/raw/desk-tiles.sha256" && echo "(c) desk tiles list equal to the land's raw/desk-tiles.sha256" || { echo "desk tiles list differs"; exit 9; }
for f in "$WK/counts/"*.json; do cmp -s "$f" "$VL/raw/$(basename "$f")" || { echo "raw copy differs: $f"; exit 9; }; done
echo "(c) raw files copied: $(ls "$WK/counts" | wc -l), each equal to the land's"
echo "bench sources manifest sha256: $(sha256sum < "$WK/bench-src.sha256" | cut -c1-64)"
echo "core-et manifest sha256: $(sha256sum < "$WK/core-et-copy.sha256" | cut -c1-64)"
cp -p "$VC/scripts/inventory.py" "$L/scripts/inventory.py" || exit 9
echo "$(ts) end"
