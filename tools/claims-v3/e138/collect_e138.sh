#!/usr/bin/env bash
# E138 (Q137; a port of E130's collector): reduce every finished block with E78's reduction (reduce_e138.py runs reduce_e78.py unchanged with E130's
# items) on the registered primary (dips removed, leakage auto), run the registered arms (dips kept; gates off), score
# E130's rules on the primary with every arm beside (score_e138.py: board p_raw primary; rail, p80, dips kept, gates off), and
# assemble the data directory. Desk compute: run it on the Intel over a copy of the raw blocks, never on the card's host.
# A port of tools/claims-v3/e127/collect_e127.sh:
#
#   PY=python3 nice -n 10 bash tools/claims-v3/e138/collect_e138.sh ['p138[1-2][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/ and logs/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the
# p138* blocks) and build/e138-logs/. Output: build/e138-out/2026-11-02-e138-int8-b-rail/ with e130.json, runs.csv,
# reduce.txt, the arms (e130-dipskept, e130-gatesoff: .json, .csv, .txt), scored.json, results.md, code.sha256, logs/, the
# smoke and every block's raw data. Only blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no block is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p138[1-2][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e138-out/2026-11-02-e138-int8-b-rail
rm -rf "${ROOT:?}/build/e138-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "blocks reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished block" >&2; exit 1; }

E=tools/claims-v3/e138
K=tools/claims-v3/kinds
"$PY" $E/reduce_e138.py "${ok[@]}" --drop-dips --no-refit --out "$OUT/e138.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary, dips removed) rc=$?"; tail -3 "$OUT/reduce.log"
"$PY" $E/reduce_e138.py "${ok[@]}" --no-refit --out "$OUT/e138-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $E/reduce_e138.py "${ok[@]}" --drop-dips --gates-off --no-refit --out "$OUT/e138-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $E/score_e138.py --primary "$OUT/runs.csv,$OUT/e138.json" \
  --arm "board=$OUT/runs.csv,$OUT/e138.json,p_raw,on" \
  --arm "board_p80=$OUT/runs.csv,$OUT/e138.json,p80,on" \
  --arm "rail_dips_kept=$OUT/runs-dipskept.csv,$OUT/e138-dipskept.json,rail_raw,on" \
  --arm "rail_gates_off=$OUT/runs-gatesoff.csv,$OUT/e138-gatesoff.json,rail_raw,off" \
  --pool-e130 "docs/reports/data/2026-11-02-e130-int8-netlists/runs.csv,docs/reports/data/2026-11-02-e130-int8-netlists/e130.json" \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
  { echo "score_e138 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $K/e130/e130.json $K/e130/sha256.txt $K/e130/tiles/int8/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p138*.attempt-* "$RAW"/kinds-smoke/p138*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
