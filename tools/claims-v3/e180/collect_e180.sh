#!/usr/bin/env bash
# E180 (Q146(f), the kit): the desk collection of a session copied back from the box (step 22 runs it), on the Intel: the passes, the
# smoke and the stop-path test into the data directory's raw/, the session's logs into logs/, then reduce_e180.py (the catalogue's
# bursts_of on every pass) and score_e180.py (E180.md section 5's rules). It reads no card and commits nothing.
#
#   E180_DATE=<YYYY-MM-DD> [PY=/usr/bin/python3] bash tools/claims-v3/e180/collect_e180.sh <raw copy: build/e180-raw>
#   -> build/e180-out/<day>-e180-vector-add-aifoundry3/{raw/, logs/, reduced-e180.json, scored-e180.json, scored-e180.md}
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e180.sh <raw copy>}
DAY=${E180_DATE:?E180_DATE - the card day, YYYY-MM-DD}
PY=${PY:-python3}
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
mkdir -p "$OUT/raw" "$OUT/logs"
for d in e180 e180-smoke e180-stoptest; do
  [ -d "$RAW/$d" ] && rsync -a --exclude '*.raw' "$RAW/$d" "$OUT/raw/"
done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
"$PY" -B tools/claims-v3/e180/reduce_e180.py --data "$OUT/raw/e180" --out "$OUT/reduced-e180.json" --root . || { echo "reduce_e180 failed"; exit 1; }
"$PY" -B tools/claims-v3/e180/score_e180.py --reduced "$OUT/reduced-e180.json" --out "$OUT/scored-e180" || { echo "score_e180 failed"; exit 1; }
[ -s "$OUT/scored-e180.md" ] && echo "scored-e180.md written: $OUT"
