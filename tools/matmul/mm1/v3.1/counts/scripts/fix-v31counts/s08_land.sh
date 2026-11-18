#!/bin/bash
# fix-v31counts step 8: the land dir (new files only, under tools/matmul/mm1/v3.1/counts/), its SHA256SUMS, and a scan for home paths and
# logins. It replaces v31-counts' land (SHA256SUMS 76ad5d97...) as a whole: that version's files the findings do not touch are byte copies of
# its land; the fixed tables, README and SOURCES.json come from this lane's counts/; the fix's bench outputs go in raw/ and its scripts in
# scripts/fix-v31counts/ with the box's paths replaced by placeholders (<W>, <LAB>, ~). The substitution's patterns are built from variables
# (env.sh's W and LAB, the home directory, the login from id), so this script's published copy shows them as they ran.
# Desk; no device; nothing is committed (the land lane commits).
set -u
. <W>/out/fix-v31counts/scripts/env.sh
D=$L/land/tools/matmul/mm1/v3.1/counts
VL=$VC/land/tools/matmul/mm1/v3.1/counts
[ -e "$L/land/tools" ] && { echo "land dir exists already: refusing to overwrite (remove it by hand first)"; exit 3; }
mkdir -p "$D/raw" "$D/scripts/fix-v31counts"
for f in README.md counts-fp32-gemm-states.json counts-fp16-int8-launch.json counts-v31.csv counts-v31-tiles.csv recount-check.json recount-check.txt \
         crosscheck-launch-fp32.json crosscheck-launch-fp32.txt unpriced-mm1v3.json e213-check.json tile-zero-shares.json SOURCES.json \
         recount-S2-real_blind4-check.json recount-S2-real_blind4-check.txt e37-randn-pair0-bound.json; do
  cp -p "$L/counts/$f" "$D/$f" || { echo "missing counts/$f"; exit 4; }
done
cp -p "$VL/raw/"* "$D/raw/" || exit 4
for f in recount-fp32-S2-real_blind4.json e37-bound-G4.json e37-bound-G7.json; do
  cp -p "$L/work/counts/$f" "$D/raw/$f" || exit 4
done
# the first version's scripts: byte copies of its land's (their paths are placeholders already); s12_land.sh gets a note after its first line
cp -p "$VL/scripts/"* "$D/scripts/" || exit 4
{
  head -n 1 "$VL/scripts/s12_land.sh"
  echo "# NOTE (fix-v31counts, Wed 18 Nov 2026): in this published copy the sed patterns of the substitution below show their own placeholders,"
  echo "# because the substitution rewrote this script's own text. The patterns that ran were the box's absolute paths for <W>, <LAB>, <CORE_ET>"
  echo "# and <VERILATOR_BIN>, the home directory (for ~) and a quote-split login (for \"<LOGIN>\"), and the scan's P2 was that quote-split login."
  echo "# The fix's land script (scripts/fix-v31counts/s08_land.sh) builds its patterns from variables, so its copy shows them as they ran."
  tail -n +2 "$VL/scripts/s12_land.sh"
} > "$D/scripts/s12_land.sh" || exit 4
HM=$(cd ~ && pwd -P)
for f in env.sh run_slot.sh s01_setup.sh s02a_spec.py s02_recount_inner.sh s03_compare.py s04_tables.py s04_desk_inner.sh s05_diff.py s06_sources.py \
         s07_readme.py s08_land.sh s09_land_check.py s10a_randn.sh s10_e37_spec.py s10_e37_inner.sh s11_e37_compare.py s12_desk2_inner.sh \
         s13_copy_unchanged.sh; do
  sed -e "s|$W|<W>|g" -e "s|$LAB|<LAB>|g" -e "s|$HM|~|g" "$L/scripts/$f" > "$D/scripts/fix-v31counts/$f" || exit 4
done
# the scan: no home path, no login, no machine scratch path in any landed file
P1="/ho""me/"; P2=$(id -un); P3="/tmp/cla""ude"
if grep -rIl -e "$P1" -e "$P2" -e "$P3" "$D"; then echo "SCAN FAILED: the files above carry a home path, login or scratch path"; exit 5; fi
echo "scan: no home path, login or scratch path in $(find "$D" -type f | wc -l) files"
( cd "$D" && find . -type f ! -name SHA256SUMS | LC_ALL=C sort | sed 's|^\./||' | xargs sha256sum > SHA256SUMS )
echo "files: $(wc -l < "$D/SHA256SUMS") + SHA256SUMS"
( cd "$D" && sha256sum SHA256SUMS )
echo "$(ts) land dir written"
