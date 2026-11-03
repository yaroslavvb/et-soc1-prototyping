#!/usr/bin/env bash
# E147 (Q138): reduce every finished block with E78's reduction (reduce_e147.py runs reduce_e78.py unchanged with E147's
# items) on the registered primary (dips removed at the 2 W line, leakage auto), run the registered arms (E134's 4 W dip
# line; dips kept; gates off), score E147's rules on the primary with every arm beside (score_e147.py: board p_raw primary;
# rail, p80, the 4 W line, dips kept, gates off), and assemble the data directory. Desk compute: run it on the Intel over a
# copy of the raw blocks, never on the card's host. A port of tools/claims-v3/e134/collect_e134.sh (E130's, E127's):
#
#   PY=python3 nice -n 10 bash tools/claims-v3/e147/collect_e147.sh ['p147[1-2][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/ and logs/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the
# p147* blocks) and build/e147-logs/. Output: build/e147-out/2026-11-02-e147-bit-prices-rest/ with e147.json, runs.csv,
# reduce.txt, the arms (e147-dipskept, e147-gatesoff: .json, .csv, .txt), scored.json, results.md, code.sha256, logs/, the
# smoke and every block's raw data. Only blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no block is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p147[1-2][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e147-out/2026-11-02-e147-bit-prices-rest
rm -rf "${ROOT:?}/build/e147-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "blocks reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished block" >&2; exit 1; }

E=tools/claims-v3/e147
K=tools/claims-v3/kinds
"$PY" $E/reduce_e147.py "${ok[@]}" --drop-dips --dip-w 2.0 --no-refit --out "$OUT/e147.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary, dips removed at 2 W) rc=$?"; tail -3 "$OUT/reduce.log"
"$PY" $E/reduce_e147.py "${ok[@]}" --drop-dips --dip-w 4.0 --no-refit --out "$OUT/e147-dips4.json" --csv "$OUT/runs-dips4.csv" \
  --txt "$OUT/reduce-dips4.txt" > "$OUT/reduce-dips4.log" 2>&1; echo "E134's 4 W dip line (frame arm) rc=$?"
"$PY" $E/reduce_e147.py "${ok[@]}" --no-refit --out "$OUT/e147-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $E/reduce_e147.py "${ok[@]}" --drop-dips --dip-w 2.0 --gates-off --no-refit --out "$OUT/e147-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $E/score_e147.py --primary "$OUT/runs.csv,$OUT/e147.json" \
  --arm "rail=$OUT/runs.csv,$OUT/e147.json,rail_raw,on" \
  --arm "board_p80=$OUT/runs.csv,$OUT/e147.json,p80,on" \
  --arm "dips_4w=$OUT/runs-dips4.csv,$OUT/e147-dips4.json,p_raw,on" \
  --arm "dips_kept=$OUT/runs-dipskept.csv,$OUT/e147-dipskept.json,p_raw,on" \
  --arm "gates_off=$OUT/runs-gatesoff.csv,$OUT/e147-gatesoff.json,p_raw,off" \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
  { echo "score_e147 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $E/e147/e147-tiles.json $E/e147/sha256.txt $E/e147/tiles/fp32/*.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $E/e147/e147-tiles.json $E/e147/sha256.txt $E/e147/tiles/fp32/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p147*.attempt-* "$RAW"/kinds-smoke/p147* "$RAW"/kinds-stoptest/p147*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
