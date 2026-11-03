#!/usr/bin/env bash
# E142 (Q138): reduce and score every finished pass of the session with the registered code, and assemble the data directory. Desk compute:
# run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=<python with numpy> nice -n 10 bash tools/claims-v3/e142/collect_e142.sh <raw root> [<E141 reduction json>]
#
# <raw root> holds e142/, e142-smoke/ and e142-stoptest/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/, and logs/. Only
# passes whose block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact. A port of
# tools/claims-v3/e131/collect_e131.sh:
#   1. the primary: reduce_e142.py --leak 0.2414 (E78's gates; blind pool 5's items; card 1's config gate; dips removed) -> e142.json,
#      runs.csv, reduce.txt
#   2. the arms, --no-refit: leakage auto, dips kept at 0.2414, leakage 0.1994, 0.3803 and 0, and the anchor gates relaxed (reported)
#   3. score_e142.py -> scored.json, results.md (with --e141 if E141's committed reduction of pool 5 on aifoundry3 is given)
# Output: build/e142-out/2026-11-02-e142-blind5-card1/.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-python3}
RAW=${1:?raw root}
E141=${2:-}
OUT=$ROOT/build/e142-out/2026-11-02-e142-blind5-card1
K=tools/claims-v3/kinds
E=tools/claims-v3/e142
rm -rf "${ROOT:?}/build/e142-out"
mkdir -p "$OUT/aifoundry1-c1/e142" "$OUT/logs"
ok=()
for d in "$RAW"/e142/p142[1-9][0-9]; do
  case "$d" in *.attempt-*) continue ;; esac
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]} (${ok[*]##*/})"
if [ ${#ok[@]} -gt 0 ]; then
  "$PY" $E/reduce_e142.py "${ok[@]}" --leak 0.2414 --out "$OUT/e142.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
  echo "primary rc=$?"; tail -3 "$OUT/reduce.log"
  ARMS=()
  "$PY" $E/reduce_e142.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e142-auto.json" --csv "$OUT/runs-auto.csv" \
    --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
  ARMS+=(--arm "auto=$OUT/e142-auto.json")
  "$PY" $E/reduce_e142.py "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e142-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
    --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
  ARMS+=(--arm "dips_kept=$OUT/e142-dipskept.json")
  for k in 0.1994 0.3803 0; do
    "$PY" $E/reduce_e142.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e142-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
      --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
    ARMS+=(--arm "leak$k=$OUT/e142-leak$k.json")
  done
  "$PY" $E/reduce_e142.py "${ok[@]}" --relax-anchors --leak 0.2414 --no-refit --out "$OUT/e142-relaxed.json" --csv "$OUT/runs-relaxed.csv" \
    --txt "$OUT/reduce-relaxed.txt" > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed arm rc=$?"
  ARMS+=(--arm "relaxed=$OUT/e142-relaxed.json")
  X=(); [ -n "$E141" ] && [ -f "$E141" ] && X=(--e141 "$E141")
  "$PY" $E/score_e142.py --e142 "$OUT/e142.json" --runs "$OUT/runs.csv" "${ARMS[@]}" ${X[@]+"${X[@]}"} --json "$OUT/scored.json" \
    --md "$OUT/results.md" > "$OUT/score.log" 2>&1 && { echo "results.md written"; cat "$OUT/score.log"; } ||
    { echo "score_e142 failed"; tail -20 "$OUT/score.log"; }
fi
for d in "$RAW"/e142/p142[0-9][0-9]*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  if [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && [ "${b#*.attempt-}" = "$b" ]; then cp -r "$d" "$OUT/aifoundry1-c1/e142/"
  else cp -r "$d" "$OUT/aifoundry1-c1/e142/notok-$b"; fi
done
for m in smoke stoptest; do for d in "$RAW"/e142-$m/p142*; do [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/e142-$m-$(basename "$d")"; done; done
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
( cd "$ROOT" && shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/kinds.json $K/blind5/blind5.json \
    $K/blind5/SHA256SUMS $K/blind5/predictions-blind5-aifoundry1c1.json $K/blind5/tiles/*/*.bin tools/claims-v3/e128/ettelem_guard.sh \
    tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json $E/* ) > "$OUT/code.sha256" 2>/dev/null
du -sh "$OUT"
echo "done: $OUT"
