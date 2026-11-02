#!/usr/bin/env bash
# E131 (Q136): reduce and score every finished pass of the session with the registered code, and assemble the data directory. Desk compute:
# run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e131/collect_e131.sh <raw root>
#
# <raw root> holds e131/ and e131-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ and logs/. Only passes whose block.json
# says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact. A port of tools/claims-v3/e112/collect_e112.sh's (b):
#   1. the primary: reduce_e131.py --leak 0.2414 (E78's gates; E95's items; card 1's config gate; dips removed) -> e131.json, runs.csv, reduce.txt
#   2. the set-aside rule's reduction: the same with --relax-anchors -> e131-relaxed.json (always run; score_e131.py takes from it only what the rule
#      restores, and only when the primary keeps fewer than 3 passes)
#   3. the arms, --no-refit: leakage auto (E112b's registered primary), dips kept at 0.2414, leakage 0.1994, 0.3803, 0 and 0.545
#   4. score_e131.py -> scored.json, results.md
# Output: build/e131-out/2026-11-02-e131-real-tiles-card1/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
OUT=$ROOT/build/e131-out/2026-11-02-e131-real-tiles-card1
K=tools/claims-v3/kinds
E=tools/claims-v3/e131
rm -rf "${ROOT:?}/build/e131-out"
mkdir -p "$OUT/aifoundry1-c1/e131" "$OUT/logs"
ok=()
for d in "$RAW"/e131/p131[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" $E/reduce_e131.py "${ok[@]}" --leak 0.2414 --out "$OUT/e131.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  "$PY" $E/reduce_e131.py "${ok[@]}" --relax-anchors --leak 0.2414 --out "$OUT/e131-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
    --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed rc=$?"
  ARMS=()
  "$PY" $E/reduce_e131.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e131-auto.json" --csv "$OUT/runs-auto.csv" \
    --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
  ARMS+=(--arm "auto=$OUT/e131-auto.json")
  "$PY" $E/reduce_e131.py "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e131-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
    --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$OUT/e131-dipskept.json")
  for k in 0.1994 0.3803 0 0.545; do
    "$PY" $E/reduce_e131.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e131-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e131-leak$k.json")
  done
  "$PY" $E/score_e131.py --primary "$OUT/e131.json" --relaxed "$OUT/e131-relaxed.json" "${ARMS[@]}" --json "$OUT/scored.json" \
    --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && { echo "results.md written"; tail -1 "$OUT/score.log"; } ||
    { echo "score_e131 failed"; tail -20 "$OUT/score.log"; }
fi
for d in "$RAW"/e131/p131[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry1-c1/e131/"
  else cp -r "$d" "$OUT/aifoundry1-c1/e131/notok-$b"; fi
done
for d in "$RAW"/e131-smoke/p131*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e131-smoke-$(basename "$d")"; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/e95_common.py \
    $K/score_e95.py $K/predictions-e95.json $K/real/real.json $K/real2/real2.json $K/real2/predictions-real2.json $K/real2/tiles/*/*.bin \
    $K/real/tiles/*/*.bin tools/claims-v3/e112/score_e112b.py tools/claims-v3/e112/predictions-real2-card1.json \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json $E/* 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/e95_common.py \
    $K/score_e95.py $K/predictions-e95.json $K/real/real.json $K/real2/real2.json $K/real2/predictions-real2.json $K/real2/tiles/*/*.bin \
    $K/real/tiles/*/*.bin tools/claims-v3/e112/score_e112b.py tools/claims-v3/e112/predictions-real2-card1.json \
    tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json $E/*; } ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
