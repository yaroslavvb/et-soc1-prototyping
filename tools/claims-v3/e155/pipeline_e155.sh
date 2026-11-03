#!/usr/bin/env bash
# E155 (Q139): reduce, score and read E155's passes, on the Intel (desk compute; never on the card's host). Registered in README.md. A copy of
# tools/claims-v3/e148/pipeline_e148.sh with the names changed.
#
#   nice -n 10 bash tools/claims-v3/e155/pipeline_e155.sh <out dir> <pass dir> [<pass dir> ...]
#
# Only pass directories whose block.json says "ok" are read; an `.attempt-*` directory is never passed; no pass is chosen after the fact.
#   1. the primary reduction: reduce_e155.py --leak 0.2414 (E78's gates; E155's items; card 1's config gate; dips removed) -> e155.json, runs.csv, reduce.txt
#   2. the set-aside rule's reduction: the same with --relax-tie -> e155-relaxed.json (always run; it carries the verdicts only as the rule says)
#   3. the arms: dips kept (--keep-dips) and leakage auto, --no-refit -> e155-dipskept.json, e155-auto.json
#   4. score_e155.py with predictions-e155.json: the primary with the relaxed (the set-aside rule picks) -> scored.json, results.md; each arm alone ->
#      scored-dipskept.json, scored-auto.json, and the relaxed alone -> scored-relaxed.json (reported)
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
OUT=${1:?out dir}; shift
mkdir -p "$OUT"
ok=()
for d in "$@"; do
  case "$d" in *.attempt-*) echo "never read: $d"; continue ;; esac
  [ -e "$d/block.json" ] && grep -q '"status":"ok"' "$d/block.json" && ok+=("$d") || echo "skipped (not ok): $d"
done
echo "passes read: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }
H=tools/claims-v3/e155
PRED=$H/predictions-e155.json
RED=(uv run --quiet "$H/reduce_e155.py")
"${RED[@]}" "${ok[@]}" --leak 0.2414 --out "$OUT/e155.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1; echo "primary rc=$?"
"${RED[@]}" "${ok[@]}" --relax-tie --leak 0.2414 --out "$OUT/e155-relaxed.json" --csv "$OUT/runs-relaxed.csv" --txt "$OUT/reduce-relaxed.txt" \
  > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed rc=$?"
"${RED[@]}" "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e155-dipskept.json" --csv "$OUT/runs-dipskept.csv" --txt "$OUT/reduce-dipskept.txt" \
  > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"${RED[@]}" "${ok[@]}" --leak auto --no-refit --out "$OUT/e155-auto.json" --csv "$OUT/runs-auto.csv" --txt "$OUT/reduce-auto.txt" \
  > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
python3 "$H/score_e155.py" --primary "$OUT/e155.json" --relaxed "$OUT/e155-relaxed.json" --pred "$PRED" --out "$OUT/scored.json" --md "$OUT/results.md" \
  > "$OUT/score.log" 2>&1; echo "score rc=$?: $(tail -1 "$OUT/score.log")"
for v in relaxed dipskept auto; do
  [ -s "$OUT/e155-$v.json" ] || { echo "no e155-$v.json"; continue; }
  python3 "$H/score_e155.py" --primary "$OUT/e155-$v.json" --pred "$PRED" --out "$OUT/scored-$v.json" --md "$OUT/results-$v.md" > "$OUT/score-$v.log" 2>&1
  echo "score-$v rc=$?: $(tail -1 "$OUT/score-$v.log")"
done
