#!/bin/bash
# NOTE (fix-v31counts, Wed 18 Nov 2026): in this published copy the sed patterns of the substitution below show their own placeholders,
# because the substitution rewrote this script's own text. The patterns that ran were the box's absolute paths for <W>, <LAB>, <CORE_ET>
# and <VERILATOR_BIN>, the home directory (for ~) and a quote-split login (for "<LOGIN>"), and the scan's P2 was that quote-split login.
# The fix's land script (scripts/fix-v31counts/s08_land.sh) builds its patterns from variables, so its copy shows them as they ran.
# v31-counts step 12: the land dir (new files only, under tools/matmul/mm1/v3.1/counts/), its SHA256SUMS, and a scan for home paths and
# logins. Copies of this lane's scripts go in with the box's paths replaced by placeholders (<W>, <LAB>, <CORE_ET>, <VERILATOR_BIN>, ~).
# Desk; no device; nothing is committed (the land lane commits).
set -u
. <W>/out/v31-counts/scripts/env.sh
D=$L/land/tools/matmul/mm1/v3.1/counts
[ -e "$L/land/tools" ] && { echo "land dir exists already: refusing to overwrite (remove it by hand first)"; exit 3; }
mkdir -p "$D/raw" "$D/scripts"
for f in README.md counts-fp32-gemm-states.json counts-fp16-int8-launch.json counts-v31.csv counts-v31-tiles.csv recount-check.json recount-check.txt \
         crosscheck-launch-fp32.json crosscheck-launch-fp32.txt unpriced-mm1v3.json e213-check.json tile-zero-shares.json SOURCES.json; do
  cp -p "$L/counts/$f" "$D/$f" || { echo "missing counts/$f"; exit 4; }
done
for f in new-fp32-S1.json new-fp32-S2.json new-launch.json recount-fp32-S1-randn.json recount-launch-int8-full.json recount-launch-fp16-randn.json; do
  cp -p "$L/work/counts/$f" "$D/raw/$f" || exit 4
done
cp -p "$L/work/dsk/tiles-made.sha256" "$D/raw/desk-tiles.sha256"
for f in env.sh run_slot.sh s01_enum.sh s01_enum_unpriced.py s02_setup.sh s03_build_inner.sh s04_fcheck_inner.sh s05_maps_inner.sh \
         s06_recount_inner.sh s06b_compare.py inventory.py s07a_spec.py s07_fp32_inner.sh s08_launch_inner.sh s07_chain.sh s09_tables.py \
         s10_e213_check.py s11_sources.py s12_land.sh s12_readme.py s13_desk_inner.sh s14_zero_share.py s14_inner.sh s15_e37_check.py s15_inner.sh wait_file.sh; do
  sed -e 's|<W>|<W>|g' -e 's|<LAB>|<LAB>|g' \
      -e 's|<CORE_ET>|<CORE_ET>|g' -e 's|<VERILATOR_BIN>|<VERILATOR_BIN>|g' \
      -e 's|~|~|g' -e 's|"<LOGIN>"|"<LOGIN>"|g' "$L/scripts/$f" > "$D/scripts/$f" || exit 4
done
# the scan: no home path, no login, no machine path in any landed file
P1="/ho""me/"; P2="<LOGIN>"; P3="/tmp/cla""ude"
if grep -rIl -e "$P1" -e "$P2" -e "$P3" "$D"; then echo "SCAN FAILED: the files above carry a home path or login"; exit 5; fi
echo "scan: no home path, login or scratch path in $(find "$D" -type f | wc -l) files"
( cd "$D" && find . -type f ! -name SHA256SUMS | LC_ALL=C sort | sed 's|^\./||' | xargs sha256sum > SHA256SUMS )
echo "files: $(wc -l < "$D/SHA256SUMS") + SHA256SUMS"
( cd "$D" && sha256sum SHA256SUMS )
echo "$(ts) land dir written"
