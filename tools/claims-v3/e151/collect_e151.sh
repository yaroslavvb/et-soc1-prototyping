#!/usr/bin/env bash
# E151 (Q139; a port of E145's collector): reduce every finished block with E78's reduction (reduce_e151.py runs reduce_e78.py unchanged
# with E151's items) on the registered primary (the board's dips and the rail's glitches removed, leakage auto), run the registered arms
# (the rail filter off, i.e. E145's primary form; the dips kept; the gates off), score every rule on the primary with every arm beside
# (score_e151.py: the rail primary; the board, p80, filter off, dips kept, gates off; the pools with E130's, E138's and E145's filtered
# blocks, reported), census the rail filter and summarise the telemetry (railfilter_e151.py, telemetry_max_e151.py). Desk compute: run it
# on the Intel over the raw copy inside the data directory, never on the card's host.
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e151/collect_e151.sh <raw root> [<out dir>]
#
# <raw root> (relative to the repository root, so no host path enters a table) holds e151/, e151-smoke/ and e151-stoptest/ as copied from
# aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the p151* blocks). Output (default docs/reports/data/2026-11-03-e151-int8-b-aifoundry3):
# e151.json, runs.csv, reduce.txt, the arms (e151-filteroff, e151-dipskept, e151-gatesoff: .json, .csv, .txt), scored.json, results.md,
# rail-census.json, telemetry.json, code.sha256. Only blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no block is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
PY=${PY:-python3}
RAW=${1:?raw root, relative to the repository root}
OUT=${2:-docs/reports/data/2026-11-03-e151-int8-b-aifoundry3}
case "$RAW$OUT" in /*) echo "give both paths relative to the repository root (no host path in the tables)" >&2; exit 2 ;; esac
mkdir -p "$OUT"
ok=()
for d in "$RAW"/e151/p151[1-3][0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "blocks reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished block" >&2; exit 1; }
E=tools/claims-v3/e151
K=tools/claims-v3/kinds
D130=docs/reports/data/2026-11-02-e130-int8-netlists
D138=docs/reports/data/2026-11-02-e138-int8-b-rail
F145=tools/claims-v3/e151/e145-filtered
"$PY" $E/reduce_e151.py "${ok[@]}" --drop-dips --rail-filter --no-refit --out "$OUT/e151.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary: dips and rail glitches removed) rc=$?"; tail -3 "$OUT/reduce.log"
"$PY" $E/reduce_e151.py "${ok[@]}" --drop-dips --no-refit --out "$OUT/e151-filteroff.json" --csv "$OUT/runs-filteroff.csv" \
  --txt "$OUT/reduce-filteroff.txt" > "$OUT/reduce-filteroff.log" 2>&1; echo "rail-filter-off arm rc=$?"
"$PY" $E/reduce_e151.py "${ok[@]}" --rail-filter --no-refit --out "$OUT/e151-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $E/reduce_e151.py "${ok[@]}" --drop-dips --rail-filter --gates-off --no-refit --out "$OUT/e151-gatesoff.json" \
  --csv "$OUT/runs-gatesoff.csv" --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $E/score_e151.py --primary "$OUT/runs.csv,$OUT/e151.json" \
  --arm "board=$OUT/runs.csv,$OUT/e151.json,p_raw,on" \
  --arm "board_p80=$OUT/runs.csv,$OUT/e151.json,p80,on" \
  --arm "rail_filter_off=$OUT/runs-filteroff.csv,$OUT/e151-filteroff.json,rail_raw,on" \
  --arm "rail_dips_kept=$OUT/runs-dipskept.csv,$OUT/e151-dipskept.json,rail_raw,on" \
  --arm "rail_gates_off=$OUT/runs-gatesoff.csv,$OUT/e151-gatesoff.json,rail_raw,off" \
  --pool "E130=$D130/runs.csv,$D130/e130.json" --pool "E138=$D138/runs.csv,$D138/e138.json" \
  --pool "E145f=$F145/runs.csv,$F145/e145-filtered.json" \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
  { echo "score_e151 failed"; tail -20 "$OUT/score.log"; }
python3 $E/railfilter_e151.py "$RAW" > "$OUT/rail-census.json" 2> "$OUT/rail-census.err"; echo "rail census rc=$?"
python3 $E/telemetry_max_e151.py "$RAW" > "$OUT/telemetry.json" 2> "$OUT/telemetry.err"; echo "telemetry summary rc=$?"
{ sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin tools/claims-v3/e145/score_e145.py \
    tools/claims-v3/e138/score_e138.py tools/claims-v3/e130/score_e130.py 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin tools/claims-v3/e145/score_e145.py \
    tools/claims-v3/e138/score_e138.py tools/claims-v3/e130/score_e130.py; } > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
