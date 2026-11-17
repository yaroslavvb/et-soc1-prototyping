#!/usr/bin/env bash
# E210 (Q202) desk: draw E210's tile files with the committed generator, and the desk-only calibration tiles the switch count reads.
#   bash tools/claims-v3/e210/desk/make_tiles_e210.sh <lab top> <build dir> <desk-only tile dir>
# 1. g++ -O2 -std=c++17 desk/gen_tiles_e210.cpp -> <build dir>/gen_tiles_e210 (a desk program; it opens no device);
# 2. the card's tiles (committed): tiles/fp32/<p>/<p>_00 .. _60.bin, 61 pairs each, for signs lowmant8 highmant8 bhalfeq badjeq hd4 maxalte
#    arow50 (the first 61 pairs of each pattern's seeded stream; F = 61, a prime, so the pool's cycle aligns with neither the 32 k steps nor
#    the tile rows), and tiles/fp32/negzero/negzero_00.bin (every word -0.0: one file is the whole law);
# 3. the desk-only tiles (not committed, reproducible by this script): randn and sparse50, 61 pairs each, drawn by rgm136's own drawTile()
#    (copied verbatim in gen_tiles_e210.cpp) for the switch count of the random and sparse50 laws;
# 4. sha256 of every tile written: <desk-only dir>/tiles-made.sha256 (paths from the lab top for the committed ones).
set -eu
TOP=${1:?lab top}
BLD=${2:?build dir}
DSK=${3:?desk-only tile dir}
E=$TOP/tools/claims-v3/e210
mkdir -p "$BLD" "$DSK"
g++ -O2 -std=c++17 -o "$BLD/gen_tiles_e210" "$E/desk/gen_tiles_e210.cpp"
g++ --version | head -1
for p in signs lowmant8 highmant8 bhalfeq badjeq hd4 maxalte arow50; do
  mkdir -p "$E/tiles/fp32/$p"
  "$BLD/gen_tiles_e210" "$p" fp32 61 "$E/tiles/fp32/$p"
done
mkdir -p "$E/tiles/fp32/negzero" "$BLD/negzero-tmp"
"$BLD/gen_tiles_e210" negzero fp32 1 "$E/tiles/fp32/negzero"
for k in randn sparse50; do
  mkdir -p "$DSK/fp32/$k"
  "$BLD/gen_tiles_e210" "$k" fp32 61 "$DSK/fp32/$k"
done
( cd "$TOP" && find tools/claims-v3/e210/tiles -name '*.bin' | LC_ALL=C sort | xargs sha256sum ) > "$DSK/tiles-made.sha256"
( cd "$DSK" && find fp32 -name '*.bin' | LC_ALL=C sort | xargs sha256sum ) >> "$DSK/tiles-made.sha256"
echo "tiles written: $(grep -c . "$DSK/tiles-made.sha256")"
