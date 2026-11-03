#!/usr/bin/env bash
# E141 (Q138): reduce and score every finished pass of the session with the registered code, and assemble the data directory. Desk compute:
# run it on the Intel over a copy of the raw passes, never on the card's host. A port of tools/claims-v3/e140/collect_e140.sh (E140's
# reduction and arms on this card) with E142's layout (e141/, e141-smoke/, e141-stoptest/ under build/claims-v3/aifoundry3/):
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e141/collect_e141.sh <raw root>
#
# <raw root> holds e141/, e141-smoke/ and e141-stoptest/ as copied from aifoundry3:aifoundry/build/claims-v3/aifoundry3/, and logs/. Only
# passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact.
#   1. the primary: reduce_e141.py (reduce_e78.py unchanged: leakage auto, dips kept, E78's gates; E140's primary) -> e141.json, runs.csv
#   2. the arms (--no-refit for the leakage arms, as E140): leakage 0.1994, 0.3803 and 0; dips removed (E82 A2); pass gates opened
#   3. score_e141.py on the primary with every arm beside -> scored.json, results.md; the dips-removed arm scored alone (reported, never
#      the verdict) -> scored-nodips.json, results-nodips.md
# Output: build/e141-out/2026-11-02-e141-blind5-aifoundry3/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
OUT=$ROOT/build/e141-out/2026-11-02-e141-blind5-aifoundry3
K=tools/claims-v3/kinds
E=tools/claims-v3/e141
rm -rf "${ROOT:?}/build/e141-out"
mkdir -p "$OUT/aifoundry3/e141" "$OUT/logs"
ok=()
for d in "$RAW"/e141/p141[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" $E/reduce_e141.py "${ok[@]}" --out "$OUT/e141.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  ARMS=()
  for k in 0.1994 0.3803 0; do   # E78's primary slope value on E78's runs, E71's idle slope, no correction (E140's arms)
    "$PY" $E/reduce_e141.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e141-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e141-leak$k.json")
  done
  "$PY" $E/reduce_e141.py "${ok[@]}" --drop-dips --out "$OUT/e141-nodips.json" --csv "$OUT/runs-nodips.csv" \
    --txt "$OUT/reduce-nodips.txt" > "$OUT/reduce-nodips.log" 2>&1; echo "dips arm rc=$?"
  ARMS+=(--arm "dips_removed=$OUT/e141-nodips.json")
  "$PY" $E/reduce_e141.py "${ok[@]}" --gates-off --out "$OUT/e141-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
    --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
  ARMS+=(--arm "gates_off=$OUT/e141-gatesoff.json")
  "$PY" $E/score_e141.py --e141 "$OUT/e141.json" --runs "$OUT/runs.csv" "${ARMS[@]}" --json "$OUT/scored.json" \
    --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
    { echo "score_e141 failed"; tail -20 "$OUT/score.log"; }
  "$PY" $E/score_e141.py --e141 "$OUT/e141-nodips.json" --runs "$OUT/runs-nodips.csv" --json "$OUT/scored-nodips.json" \
    --md "$OUT/results-nodips.md" > "$OUT/score-nodips.log" 2>&1 && echo "results-nodips.md written (reported arm)" ||
    { echo "score of the dips arm failed"; tail -20 "$OUT/score-nodips.log"; }
fi
for d in "$RAW"/e141/p141[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry3/e141/"
  else cp -r "$d" "$OUT/aifoundry3/e141/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e141-$m/p141*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/e141-$m-$(basename "$d")"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind5/blind5.json \
    $K/blind5/SHA256SUMS $K/blind5/predictions-blind5-aifoundry3.json $K/blind5/tiles/*/*.bin tools/claims-v3/e128/ettelem_guard.sh \
    tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json $E/* ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
