#!/bin/bash
# amend-e223 (Q239a) step 6: the land folder (new files only, beside decl-e223's blind-e223/): the amendment, its forecasts, the freeze record,
# the scripts (under scripts/amend1/, so no name meets the declaration's own scripts/), SHA256SUMS-amend1; a public-text scan. No commit.
# Run: bash s06_land.sh <lane dir>
set -euo pipefail
L="${1:?lane dir}"
D="$L/land/tools/matmul/mm1/v3.1/blind-e223"
mkdir -p "$D/scripts/amend1"
for f in DECLARED-blind-e223-amendment-1.md DECLARED-blind-e223-amendment-1.json forecasts-nominal-e223-amend1.csv forecasts-nominal-e223-amend1.json; do
  [ ! -e "$D/$f" ] || { echo "exists in the land: $f"; exit 3; }
  cp -p "$L/$f" "$D/$f"
done
cp -p "$L/FROZEN.txt" "$D/FROZEN-amend1.txt"
for f in p01_time.py s01_check.py s02_amend.py s03_forecast.py s04_write.py s05_frozen.sh s06_land.sh; do
  cp -p "$L/scripts/$f" "$D/scripts/amend1/$f"
done
cd "$D"
# the public-text scan: no home path, no login, no credential-looking text
PAT="/"'ho''me'"/|$(id -un)|BEGIN [A-Z ]*PRIV""ATE KEY|pass""word|tok""en="     # built at run time: the pattern does not match its own text
if grep -rIl -E "$PAT" --exclude=SHA256SUMS-amend1 . ; then
  echo "PUBLIC-TEXT SCAN: hits above"; SCAN=HITS
else
  SCAN=CLEAN
fi
find . -type f ! -name SHA256SUMS-amend1 | sed 's|^\./||' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS-amend1
sha256sum -c SHA256SUMS-amend1 > /dev/null
N=$(wc -l < SHA256SUMS-amend1)
for f in DECLARED-blind-e223-amendment-1.md DECLARED-blind-e223-amendment-1.json forecasts-nominal-e223-amend1.csv forecasts-nominal-e223-amend1.json; do
  grep -q "^$(sha256sum "$f" | cut -c1-64)  $f\$" "$L/FROZEN.txt" || { echo "land copy differs from FROZEN.txt: $f"; exit 4; }
done
echo "$(TZ=America/Los_Angeles date '+%Y-%m-%d %H:%M:%S %Z') step 6: land built at land/tools/matmul/mm1/v3.1/blind-e223/ (new files only: the amendment, its forecasts, FROZEN-amend1.txt, scripts/amend1/ 7 files, SHA256SUMS-amend1 $N lines $(sha256sum SHA256SUMS-amend1 | cut -c1-16)...; the four frozen files equal FROZEN.txt; public-text scan $SCAN) rc=0" >> "$L/logs/progress.txt"
echo "scan $SCAN files $N"
cat SHA256SUMS-amend1
