#!/usr/bin/env bash
# E112 (Q133): reduce and score every finished pass of the session with the registered code, and assemble the data
# directory. Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e112/collect_e112.sh <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ (only the p112*
# passes) and logs/. (a), passes p1121[0-9]: E91's own collection, tools/claims-v3/kinds/collect_e91.sh, run UNCHANGED with
# that glob (reduce_e91.py's primary and its five arms, score_e91.py), its output copied into a-e91-rerun/. (b), passes
# p1125[0-9]: reduce_e112b.py (primary: dips removed, leakage auto; arms dips kept, 0.1994, 0.545, 0.3803, 0) and
# score_e112b.py into b-e95-card1/. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no pass is chosen after the fact. Output: build/e112-out/2026-11-01-e112-real-replicates/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
RAW=${1:?raw root}
OUT=$ROOT/build/e112-out/2026-11-01-e112-real-replicates
K=tools/claims-v3/kinds
E=tools/claims-v3/e112
rm -rf "${ROOT:?}/build/e112-out"
mkdir -p "$OUT/a-e91-rerun" "$OUT/b-e95-card1" "$OUT/aifoundry1-c1/kinds" "$OUT/logs"

# ---- (a): E91's collection, unchanged
PY=$PY bash $K/collect_e91.sh 'p1121[0-9]' "$RAW" > "$OUT/a-e91-rerun/collect.log" 2>&1; echo "(a) collect_e91.sh rc=$?"
A=$ROOT/build/e91-out/2026-10-31-e91-real-tensors-aifoundry1
for f in "$A"/*.json "$A"/*.csv "$A"/*.txt "$A"/*.md "$A"/*.log "$A"/code.sha256; do [ -f "$f" ] && cp "$f" "$OUT/a-e91-rerun/"; done
tail -3 "$OUT/a-e91-rerun/collect.log"

# ---- (b): E95's pass on card 1
ok=()
for d in "$RAW"/kinds/p1125[0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "(b) skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "(b) passes reduced: ${#ok[@]}"
B=$OUT/b-e95-card1
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" $E/reduce_e112b.py "${ok[@]}" --out "$B/e112b.json" --csv "$B/runs.csv" --txt "$B/reduce.txt" > "$B/reduce.log" 2>&1
  echo "(b) reduce rc=$?"; tail -3 "$B/reduce.log"
  ARMS=()
  "$PY" $E/reduce_e112b.py "${ok[@]}" --keep-dips --out "$B/e112b-dipskept.json" --csv "$B/runs-dipskept.csv" \
    --txt "$B/reduce-dipskept.txt" > "$B/reduce-dipskept.log" 2>&1; echo "(b) dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$B/e112b-dipskept.json")
  for k in 0.1994 0.545 0.3803 0; do
    "$PY" $E/reduce_e112b.py "${ok[@]}" --leak "$k" --no-refit --out "$B/e112b-leak$k.json" --csv "$B/runs-leak$k.csv" \
      --txt "$B/reduce-leak$k.txt" > "$B/reduce-leak$k.log" 2>&1; echo "(b) leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$B/e112b-leak$k.json")
  done
  AA=(); [ -f "$OUT/a-e91-rerun/e91.json" ] && AA=(--e112a "$OUT/a-e91-rerun/e91.json")
  "$PY" $E/score_e112b.py --e112b "$B/e112b.json" "${ARMS[@]}" ${AA[@]+"${AA[@]}"} --json "$B/scored.json" --md "$B/results.md" \
    > "$B/score.log" 2>&1 && echo "(b) results.md written" || { echo "(b) score_e112b failed"; tail -20 "$B/score.log"; }
fi

# ---- raw passes, the smoke, logs, hashes
for d in "$RAW"/kinds/p112[0-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] || continue
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json"; then cp -r "$d" "$OUT/aifoundry1-c1/kinds/"
  else cp -r "$d" "$OUT/aifoundry1-c1/kinds/notok-$(basename "$d")"; fi
done
for d in "$RAW"/kinds/p112*.attempt-* "$RAW"/kinds-smoke/p112*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E86.md $K/E91.md $K/E95.md $E/* \
    $K/predictions-e78.json $K/predictions-e82.json $K/predictions-e86.json $K/predictions-e91.json $K/predictions-e95.json \
    $K/kinds.json $K/real/real.json $K/real/predictions-real.json $K/real/amendment-1.json $K/real/tiles/*/*.bin \
    $K/real2/real2.json $K/real2/predictions-real2.json $K/real2/tiles/*/*.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E86.md $K/E91.md $K/E95.md $E/* \
    $K/predictions-e78.json $K/predictions-e82.json $K/predictions-e86.json $K/predictions-e91.json $K/predictions-e95.json \
    $K/kinds.json $K/real/real.json $K/real/predictions-real.json $K/real/amendment-1.json $K/real/tiles/*/*.bin \
    $K/real2/real2.json $K/real2/predictions-real2.json $K/real2/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
