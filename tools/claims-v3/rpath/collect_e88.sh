#!/usr/bin/env bash
# E88 (Q130): reduce every finished card-1 pass with the frozen reduction (reduce_e88.py: reduce_e78.py unchanged),
# run the registered arms, score, and assemble the data directory. Desk compute, on the Intel, over a copy of the
# raw passes. Added after the freeze (3dd99088) and before any pass was reduced: it only calls the frozen code.
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/rpath/collect_e88.sh <raw root>
#
# <raw root> holds rpath/ and rpath-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/, and
# logs/. Output: build/e88-out/2026-10-31-e88-result-path/. Only passes whose block.json says "ok" are reduced; an
# `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
OUT=$ROOT/build/e88-out/2026-10-31-e88-result-path
rm -rf "${ROOT:?}/build/e88-out"
mkdir -p "$OUT/aifoundry1-c1/rpath" "$OUT/logs"
ok=()
for d in "$RAW"/rpath/p88[1-9][0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }
K=tools/claims-v3/rpath
"$PY" $K/reduce_e88.py "${ok[@]}" --out "$OUT/e88.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary: dips removed) rc=$?"; head -3 "$OUT/reduce.log"
"$PY" $K/reduce_e88.py "${ok[@]}" --keep-dips --no-refit --out "$OUT/e88-keepdips.json" --csv "$OUT/runs-keepdips.csv" \
  --txt "$OUT/reduce-keepdips.txt" > "$OUT/reduce-keepdips.log" 2>&1; echo "arm dips-kept rc=$?"
for k in 0.545 0.3803 0; do
  "$PY" $K/reduce_e88.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e88-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "arm leak $k rc=$?"
done
"$PY" $K/score_e88.py --e88 "$OUT/e88.json" --arm "dips-kept=$OUT/e88-keepdips.json" \
  --arm "leak0.545=$OUT/e88-leak0.545.json" --arm "leak0.3803=$OUT/e88-leak0.3803.json" --arm "leak0=$OUT/e88-leak0.json" \
  --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && echo "results.md written" \
  || { echo "score_e88 failed"; tail -20 "$OUT/score.log"; }
( shasum -a 256 tools/claims-v3/lib.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/reduce_e78.py \
    tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/kinds.json $K/*.py $K/*.sh $K/E88.md $K/e88.json \
    $K/predictions-e88.json $K/tiles/*/*.bin ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
[ -d "$RAW/logs/ident" ] && cp -r "$RAW/logs/ident" "$OUT/logs/"
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/rpath/"; done
for d in "$RAW"/rpath/p88*.attempt-* "$RAW"/rpath-smoke/p88*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/rpath/$(basename "$(dirname "$d")")-$(basename "$d")"
done
find "$OUT/aifoundry1-c1" -name 'telemetry.jsonl.raw' -delete
du -sh "$OUT"
