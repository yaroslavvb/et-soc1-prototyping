#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 2), v2: the desk collection of a session copied back from the box
# (step 22 v2 runs it), on the Intel. collect_e180.sh (v1, which stays as committed) with two changes: the reduction is reduce_e180_v2.py
# (v1's, unchanged, plus the per-burst readings the registration's dated note A1 section 4 reports: D on FL1's and E60's footings, the net
# minion rail on footing A, the die rise) and the scorer is score_e180_v2.py (every registered rule by v1's code, A1's rules A1-1, A1-5 and
# A1-7, and A1's reported arms), given the box's disassembly check (logs/elfcheck-e180.txt, from the build step) for A1-7. It reads no card
# and commits nothing.
#
#   E180_DATE=<YYYY-MM-DD> [PY=/usr/bin/python3] bash tools/claims-v3/e180/collect_e180_v2.sh <raw copy: build/e180-raw>
#   -> build/e180-out/<day>-e180-vector-add-aifoundry3/{raw/, logs/, reduced-e180-v2.json, scored-e180.json, scored-e180.md}
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e180_v2.sh <raw copy>}
DAY=${E180_DATE:?E180_DATE - the card day, YYYY-MM-DD}
PY=${PY:-python3}
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
mkdir -p "$OUT/raw" "$OUT/logs"
for d in e180 e180-smoke e180-stoptest; do
  [ -d "$RAW/$d" ] && rsync -a --exclude '*.raw' "$RAW/$d" "$OUT/raw/"
done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
"$PY" -B tools/claims-v3/e180/reduce_e180_v2.py --data "$OUT/raw/e180" --out "$OUT/reduced-e180-v2.json" --root . || { echo "reduce_e180_v2 failed"; exit 1; }
"$PY" -B tools/claims-v3/e180/score_e180_v2.py --reduced "$OUT/reduced-e180-v2.json" --out "$OUT/scored-e180" \
  --elfcheck "$OUT/logs/elfcheck-e180.txt" || { echo "score_e180_v2 failed"; exit 1; }
[ -s "$OUT/scored-e180.md" ] && echo "scored-e180.md written: $OUT"
