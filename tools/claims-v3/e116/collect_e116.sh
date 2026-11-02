#!/usr/bin/env bash
# E116 (Q133): reduce every finished aifoundry3 pass with E88's frozen reduction (reduce_e88.py: reduce_e78.py unchanged),
# run E88's registered arms, score with score_e88.py unchanged (E88's 32 rules on this card) and with score_e116.py (E116's
# rules), and assemble the data directory. Desk compute, on the Intel, over a copy of the raw passes.
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e116/collect_e116.sh <raw root>
#
# <raw root> holds rpath/, rpath-smoke/ and rpath-readback/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/,
# and logs/. Output: build/e116-out/2026-11-01-e116-split-replicate/. Only passes whose block.json says "ok" are reduced;
# an `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
OUT=$ROOT/build/e116-out/2026-11-01-e116-split-replicate
rm -rf "${ROOT:?}/build/e116-out"
mkdir -p "$OUT/aifoundry3/rpath" "$OUT/logs"
ok=()
for d in "$RAW"/rpath/p116[1-9][0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }
K=tools/claims-v3/rpath
E=tools/claims-v3/e116
"$PY" $K/reduce_e88.py "${ok[@]}" --out "$OUT/e116.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce (primary: dips removed) rc=$?"; head -3 "$OUT/reduce.log"
"$PY" $K/reduce_e88.py "${ok[@]}" --keep-dips --no-refit --out "$OUT/e116-keepdips.json" --csv "$OUT/runs-keepdips.csv" \
  --txt "$OUT/reduce-keepdips.txt" > "$OUT/reduce-keepdips.log" 2>&1; echo "arm dips-kept rc=$?"
for k in 0.545 0.3803 0; do
  "$PY" $K/reduce_e88.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e116-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "arm leak $k rc=$?"
done
"$PY" $K/score_e88.py --e88 "$OUT/e116.json" --arm "dips-kept=$OUT/e116-keepdips.json" \
  --arm "leak0.545=$OUT/e116-leak0.545.json" --arm "leak0.3803=$OUT/e116-leak0.3803.json" --arm "leak0=$OUT/e116-leak0.json" \
  --json "$OUT/scored-e88rules.json" --md "$OUT/results-e88rules.md" > "$OUT/score-e88rules.log" 2>&1 && echo "score_e88 (E88's rules) written" \
  || { echo "score_e88 failed"; tail -20 "$OUT/score-e88rules.log"; }
RB=$(ls -d "$RAW"/rpath-readback/p11602 2>/dev/null | head -1)
"$PY" $E/score_e116.py --red "$OUT/e116.json" --e88rules "$OUT/scored-e88rules.json" ${RB:+--readback "$RB/readback.jsonl"} \
  --arm "dips-kept=$OUT/e116-keepdips.json" --arm "leak0.545=$OUT/e116-leak0.545.json" --arm "leak0.3803=$OUT/e116-leak0.3803.json" \
  --arm "leak0=$OUT/e116-leak0.json" --json "$OUT/scored.json" --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && echo "score_e116 written: $(cat "$OUT/score.log")" \
  || { echo "score_e116 failed"; tail -20 "$OUT/score.log"; }
( shasum -a 256 tools/claims-v3/lib.sh tools/claims-v3/kinds/run_e78.py tools/claims-v3/kinds/reduce_e78.py \
    tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/patch_host_e104.py \
    $K/*.py $K/*.sh $K/E88.md $K/e88.json $K/predictions-e88.json $K/tiles/*/*.bin $E/* ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/rpath/"; done
for d in "$RAW"/rpath/p116*.attempt-* "$RAW"/rpath-smoke/p116* "$RAW"/rpath-readback/p116*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/rpath/$(basename "$(dirname "$d")")-$(basename "$d")"
done
find "$OUT/aifoundry3" -name 'telemetry.jsonl.raw' -delete
find "$OUT/aifoundry3" -name 'c.bin' -delete
du -sh "$OUT"
