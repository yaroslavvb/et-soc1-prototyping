#!/usr/bin/env bash
# E145 (Q138; a port of E138's collector): reduce every finished block with E78's reduction (reduce_e145.py runs reduce_e78.py unchanged
# with E145's items and card 1's configuration gate) on the registered primary (dips removed, leakage auto), run the registered arms
# (dips kept; gates off), score every rule on the primary with every arm beside (score_e145.py: the rail primary; the board, p80, dips
# kept, gates off; the pools with card 0's E130 and E138 blocks, reported), summarise the telemetry (telemetry_max_e145.py) and assemble
# the data directory. Desk compute: run it on the Intel over a copy of the raw blocks, never on the card's host.
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e145/collect_e145.sh ['p145[1-3][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/, kinds-stoptest/ and logs/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ (only
# the p145* blocks) and build/e145/. Output: build/e145-out/2026-11-02-e145-int8-b-card1/ with e145.json, runs.csv, reduce.txt, the arms
# (e145-dipskept, e145-gatesoff: .json, .csv, .txt), scored.json, results.md, telemetry.json, code.sha256, logs/, the smoke, the stop
# test and every block's raw data. Only blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; no block
# is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p145[1-3][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e145-out/2026-11-02-e145-int8-b-card1
rm -rf "${ROOT:?}/build/e145-out"
mkdir -p "$OUT/aifoundry1-c1/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "blocks reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished block" >&2; exit 1; }

E=tools/claims-v3/e145
K=tools/claims-v3/kinds
D130=docs/reports/data/2026-11-02-e130-int8-netlists
D138=docs/reports/data/2026-11-02-e138-int8-b-rail
"$PY" $E/reduce_e145.py "${ok[@]}" --drop-dips --no-refit --out "$OUT/e145.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary, dips removed) rc=$?"; tail -3 "$OUT/reduce.log"
"$PY" $E/reduce_e145.py "${ok[@]}" --no-refit --out "$OUT/e145-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $E/reduce_e145.py "${ok[@]}" --drop-dips --gates-off --no-refit --out "$OUT/e145-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $E/score_e145.py --primary "$OUT/runs.csv,$OUT/e145.json" \
  --arm "board=$OUT/runs.csv,$OUT/e145.json,p_raw,on" \
  --arm "board_p80=$OUT/runs.csv,$OUT/e145.json,p80,on" \
  --arm "rail_dips_kept=$OUT/runs-dipskept.csv,$OUT/e145-dipskept.json,rail_raw,on" \
  --arm "rail_gates_off=$OUT/runs-gatesoff.csv,$OUT/e145-gatesoff.json,rail_raw,off" \
  --pool "E130=$D130/runs.csv,$D130/e130.json" --pool "E138=$D138/runs.csv,$D138/e138.json" \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
  { echo "score_e145 failed"; tail -20 "$OUT/score.log"; }
"$PY" $E/telemetry_max_e145.py "$RAW" > "$OUT/telemetry.json" 2> "$OUT/telemetry.err"; echo "telemetry summary rc=$?"

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin tools/claims-v3/e138/score_e138.py tools/claims-v3/e130/score_e130.py 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin tools/claims-v3/e138/score_e138.py tools/claims-v3/e130/score_e130.py; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue and session logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/kinds/"; done
for d in "$RAW"/kinds/p145*.attempt-* "$RAW"/kinds-smoke/p145* "$RAW"/kinds-stoptest/p145*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
