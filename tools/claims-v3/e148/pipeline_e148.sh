#!/usr/bin/env bash
# E148 (Q138): reduce, score and read E148's passes, on the Intel (desk compute; never on the card's host). Registered in E148.md.
#
#   nice -n 10 bash tools/claims-v3/e148/pipeline_e148.sh <out dir> <pass dir> [<pass dir> ...]
#
# Only pass directories whose block.json says "ok" are read; an `.attempt-*` directory is never passed; no pass is chosen after the fact.
#   1. the primary reduction: reduce_e148.py --leak 0.2414 (E78's gates; E148's items; card 1's config gate; dips removed) -> e148.json, runs.csv, reduce.txt
#   2. the set-aside rule's reduction: the same with --relax-tie -> e148-relaxed.json (always run; it carries the verdicts only as the rule says)
#   3. the arms: dips kept (--keep-dips) and leakage auto, --no-refit -> e148-dipskept.json, e148-auto.json
#   4. score_e148.py with predictions-e148.json: the primary with the relaxed (the set-aside rule picks) -> scored.json, results.md; each arm alone ->
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
H=tools/claims-v3/e148
PRED=$H/predictions-e148.json
RED=(uv run --quiet "$H/reduce_e148.py")
"${RED[@]}" "${ok[@]}" --leak 0.2414 --out "$OUT/e148.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1; echo "primary rc=$?"
"${RED[@]}" "${ok[@]}" --relax-tie --leak 0.2414 --out "$OUT/e148-relaxed.json" --csv "$OUT/runs-relaxed.csv" --txt "$OUT/reduce-relaxed.txt" \
  > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed rc=$?"
"${RED[@]}" "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e148-dipskept.json" --csv "$OUT/runs-dipskept.csv" --txt "$OUT/reduce-dipskept.txt" \
  > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"${RED[@]}" "${ok[@]}" --leak auto --no-refit --out "$OUT/e148-auto.json" --csv "$OUT/runs-auto.csv" --txt "$OUT/reduce-auto.txt" \
  > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
python3 "$H/score_e148.py" --primary "$OUT/e148.json" --relaxed "$OUT/e148-relaxed.json" --pred "$PRED" --out "$OUT/scored.json" --md "$OUT/results.md" \
  --e129 docs/reports/data/2026-11-02-e129-int8-noissue/e129.json \
  > "$OUT/score.log" 2>&1; echo "score rc=$?: $(tail -1 "$OUT/score.log")"
for v in relaxed dipskept auto; do
  [ -s "$OUT/e148-$v.json" ] || { echo "no e148-$v.json"; continue; }
  python3 "$H/score_e148.py" --primary "$OUT/e148-$v.json" --pred "$PRED" --out "$OUT/scored-$v.json" --md "$OUT/results-$v.md" \
    --e129 docs/reports/data/2026-11-02-e129-int8-noissue/e129.json > "$OUT/score-$v.log" 2>&1
  echo "score-$v rc=$?: $(tail -1 "$OUT/score-$v.log")"
done
