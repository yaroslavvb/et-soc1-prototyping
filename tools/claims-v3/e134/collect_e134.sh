#!/usr/bin/env bash
# E134 (Q136): reduce every finished block with E78's reduction (reduce_e134.py runs reduce_e78.py unchanged with E134's
# items) on the registered primary (dips removed, leakage auto), run the registered arms (dips kept; gates off), score
# E134's rules on the primary with every arm beside (score_e134.py: board p_raw primary; rail, p80, dips kept, gates off), and
# assemble the data directory. Desk compute: run it on the Intel over a copy of the raw blocks, never on the card's host.
# A port of tools/claims-v3/e130/collect_e130.sh (itself E127's collect_e127.sh):
#
#   PY=python3 nice -n 10 bash tools/claims-v3/e134/collect_e134.sh ['p134[1-2][0-9]'] <raw root>
#
# <raw root> holds kinds/, kinds-smoke/ and logs/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/ (only the
# p134* blocks) and build/e134-logs/. Output: build/e134-out/2026-11-02-e134-bit-prices-more/ with e134.json, runs.csv,
# reduce.txt, the arms (e134-dipskept, e134-gatesoff: .json, .csv, .txt), scored.json, results.md, code.sha256, logs/, the
# smoke and every block's raw data. Only blocks whose block.json says "ok" are reduced; an `.attempt-*` directory is never
# read; no block is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
GLOB=${1:-p134[1-2][0-9]}
RAW=${2:?raw root}
OUT=$ROOT/build/e134-out/2026-11-02-e134-bit-prices-more
rm -rf "${ROOT:?}/build/e134-out"
mkdir -p "$OUT/aifoundry3/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "blocks reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished block" >&2; exit 1; }

E=tools/claims-v3/e134
K=tools/claims-v3/kinds
"$PY" $E/reduce_e134.py "${ok[@]}" --drop-dips --no-refit --out "$OUT/e134.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary, dips removed) rc=$?"; tail -3 "$OUT/reduce.log"
"$PY" $E/reduce_e134.py "${ok[@]}" --no-refit --out "$OUT/e134-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $E/reduce_e134.py "${ok[@]}" --drop-dips --gates-off --no-refit --out "$OUT/e134-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $E/score_e134.py --primary "$OUT/runs.csv,$OUT/e134.json" \
  --arm "rail=$OUT/runs.csv,$OUT/e134.json,rail_raw,on" \
  --arm "board_p80=$OUT/runs.csv,$OUT/e134.json,p80,on" \
  --arm "dips_kept=$OUT/runs-dipskept.csv,$OUT/e134-dipskept.json,p_raw,on" \
  --arm "gates_off=$OUT/runs-gatesoff.csv,$OUT/e134-gatesoff.json,p_raw,off" \
  --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
  { echo "score_e134 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $E/e134/e134-tiles.json $E/e134/sha256.txt $E/e134/tiles/fp32/*.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $E/*.py $E/*.sh $E/*.json $K/e78_common.py $K/run_e78.py $K/reduce_e78.py \
    $K/kinds.json $E/e134/e134-tiles.json $E/e134/sha256.txt $E/e134/tiles/fp32/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done   # the pull puts the queue/dry logs and the session reads there
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/kinds/"; done
for d in "$RAW"/kinds/p134*.attempt-* "$RAW"/kinds-smoke/p134*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
