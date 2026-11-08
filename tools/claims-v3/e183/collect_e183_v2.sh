#!/usr/bin/env bash
# E183 (Q155, the kit's dated note 1): the collection at the desk v2, after step 11 v2's exact copy-back (rb/s22_collect_e183_v2.sh). It is
# collect_e183.sh (v1, cc597bf2), which stays as committed, with two changes:
#   1. THE PINS FIRST (the kit verifier's fault 3: v1's collector and scorer never checked their frozen inputs). Before any reduction, the
#      three hash lists are checked at their pinned counts, each OK in full: the registration's 20, the kit's 46 and note 1's 46
#      (SHA256SUMS-e183-note1). Together they pin every file the reduction, the scorer and the loop compare read: the registration's
#      forecasts, plan, kinds and statistics, E182's statistics, E180's scored file and kernel listing, and the shared desk files. A miss
#      stops the collection (exit 1) before any number is made.
#   2. THE REDUCTION v2 (the verifier's fault 1, nit 6 and nit 8): reduce_e183_v2.py, given the session's T0 (--t0 "$E183_T0", the T0 step 9
#      recorded). It reduces a stop block by E183.md section 5.1's process rule, gives no value to a process run on a wrong image, and sets
#      aside a block from before the session's T0.
# Everything else is v1's, line for line: from the raw copy, the blocks, the smoke and the stop test into <out>/raw (no *.raw file), and the
# session's and the build's files into <out>/logs; the session's own log checked to open with its T0; the kernel's loop against E180's
# (loopcmp_e183.py, reported); the scorer (score_e183.py, unchanged). It opens no device and reaches no box.
#   E183_DATE=<YYYY-MM-DD> E183_T0=<epoch> [PY=/usr/bin/python3] bash tools/claims-v3/e183/collect_e183_v2.sh <raw copy>
# The output is build/e183-out/<day>-e183-vector-add-r2-aifoundry3/ (the data directory's name, docs/reports/data/<day>-e183-vector-add-r2-aifoundry3/).
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e183_v2.sh <raw copy>}
DAY=${E183_DATE:?E183_DATE - the card day, YYYY-MM-DD}
T0=${E183_T0:?E183_T0 - the session T0 step 9 recorded}
case "$T0" in ''|*[!0-9]*) echo "E183_T0 must be epoch seconds (read '$T0')"; exit 1 ;; esac
PY=${PY:-/usr/bin/python3}
E=tools/claims-v3/e183
bad=""
for spec in SHA256SUMS-e183-registration:20 SHA256SUMS-e183-kit:46 SHA256SUMS-e183-note1:46; do    # v2 (change 1): the pins
  l=${spec%%:*}; pin=${spec##*:}
  if [ ! -f "$E/$l" ]; then bad="$bad $l(missing)"; continue; fi
  res=$(shasum -a 256 -c "$E/$l" 2>&1); rc=$?
  n=$(printf '%s\n' "$res" | grep -c ': OK$'); m=$(grep -c . "$E/$l")
  { [ "$rc" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $l($n OK of $m; pinned $pin)"
done
[ -z "$bad" ] || { echo "the frozen inputs are not at their pins:$bad: nothing reduced or scored (read shasum -a 256 -c on each list)"; exit 1; }
echo "the frozen inputs at their pins: the registration 20, the kit 46, note 1 46 (every entry OK)"
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
"$PY" -B $E/loopcmp_e183.py "$OUT/logs/e183-kernel-dis.txt" > "$OUT/logs/loopcmp-e183.txt" 2>&1
echo "loopcmp_e183: $(tail -n 1 "$OUT/logs/loopcmp-e183.txt" | cut -c1-200)"
"$PY" -B $E/reduce_e183_v2.py --raw "$OUT/raw" --t0 "$T0" --out "$OUT/reduced-e183.json" || { echo "reduce_e183_v2 failed"; exit 1; }   # v2 (change 2)
"$PY" -B $E/score_e183.py --reduced "$OUT/reduced-e183.json" --out "$OUT/scored-e183" || { echo "score_e183 failed"; exit 1; }
[ -s "$OUT/scored-e183.md" ] && echo "scored-e183.md written: $OUT (reduced by reduce_e183_v2.py, T0 $T0)"
