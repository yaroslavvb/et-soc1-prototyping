#!/usr/bin/env bash
# E183 (Q155, the kit): the collection at the desk, after step 11's exact copy-back (E180's collect_e180_v3.sh, ported). From the raw copy:
# the blocks, the smoke and the stop test into <out>/raw (no *.raw file), the session's and the build's files into <out>/logs; the session's
# own log checked to open with its T0; the kernel's loop against E180's (loopcmp_e183.py, reported); the reduction (reduce_e183.py); the
# scorer (score_e183.py). It opens no device and reaches no box.
#   E183_DATE=<YYYY-MM-DD> E183_T0=<epoch> [PY=/usr/bin/python3] bash tools/claims-v3/e183/collect_e183.sh <raw copy>
# The output is build/e183-out/<day>-e183-vector-add-r2-aifoundry3/ (the data directory's name, docs/reports/data/<day>-e183-vector-add-r2-aifoundry3/).
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e183.sh <raw copy>}
DAY=${E183_DATE:?E183_DATE - the card day, YYYY-MM-DD}
T0=${E183_T0:?E183_T0 - the session T0 step 9 recorded}
PY=${PY:-/usr/bin/python3}
OUT=build/e183-out/$DAY-e183-vector-add-r2-aifoundry3
mkdir -p "$OUT/raw" "$OUT/logs"
for d in e183 e183-smoke e183-stoptest; do
  [ -d "$RAW/$d" ] && rsync -a --exclude '*.raw' "$RAW/$d" "$OUT/raw/"
done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
L=$OUT/logs/session-t$T0.log
[ -s "$L" ] || { echo "no session log for T0 $T0 in the copy"; exit 1; }
head -n 1 "$L" | grep -q "(T0 $T0 " || { echo "the session log does not open with T0 $T0"; exit 1; }
grep -q "session end (T0 $T0)" "$L" || echo "note: the session log holds no session end for T0 $T0"
"$PY" -B tools/claims-v3/e183/loopcmp_e183.py "$OUT/logs/e183-kernel-dis.txt" > "$OUT/logs/loopcmp-e183.txt" 2>&1
echo "loopcmp_e183: $(tail -n 1 "$OUT/logs/loopcmp-e183.txt" | cut -c1-200)"
"$PY" -B tools/claims-v3/e183/reduce_e183.py --raw "$OUT/raw" --out "$OUT/reduced-e183.json" || { echo "reduce_e183 failed"; exit 1; }
"$PY" -B tools/claims-v3/e183/score_e183.py --reduced "$OUT/reduced-e183.json" --out "$OUT/scored-e183" || { echo "score_e183 failed"; exit 1; }
[ -s "$OUT/scored-e183.md" ] && echo "scored-e183.md written: $OUT"
