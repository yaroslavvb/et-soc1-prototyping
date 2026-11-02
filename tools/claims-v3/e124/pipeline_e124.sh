#!/usr/bin/env bash
# E124 (Q134): reduce, score and read E124's passes, on the Intel (desk compute; never on the card's host). Registered in E124.md.
#
#   nice -n 10 bash tools/claims-v3/e124/pipeline_e124.sh <out dir> <pass dir> [<pass dir> ...]
#
# Only pass directories whose block.json says "ok" are read; an `.attempt-*` directory is never passed; no pass is chosen after the fact.
#   1. the primary reduction: reduce_e124.py --leak 0.2414 (E78's gates; E109's items; card 1's config gate; dips removed) -> e124.json, runs.csv, reduce.txt
#   2. the set-aside rule's reduction: the same with --relax-random -> e124-relaxed.json (always run; it carries the verdicts only if 1 keeps < 3 passes)
#   3. the arms: dips kept (--keep-dips) and leakage auto (E109's own choice on aifoundry3), --no-refit -> e124-dipskept.json, e124-auto.json
#   4. score_e109.py (E109's scorer, unchanged) with predictions-e124.json on each -> scored*.json, results*.md
#   5. extras_e124.py: which reduction carries the verdicts, Y1, Y2, Z, the reported readings, the table beside E109 -> extras.json, extras.txt
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
H=tools/claims-v3/e124
S109=tools/claims-v3/e109/score_e109.py
PRED=$H/predictions-e124.json
RED=(uv run --quiet "$H/reduce_e124.py")
"${RED[@]}" "${ok[@]}" --leak 0.2414 --out "$OUT/e124.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1; echo "primary rc=$?"
"${RED[@]}" "${ok[@]}" --relax-random --leak 0.2414 --out "$OUT/e124-relaxed.json" --csv "$OUT/runs-relaxed.csv" --txt "$OUT/reduce-relaxed.txt" \
  > "$OUT/reduce-relaxed.log" 2>&1; echo "relaxed rc=$?"
"${RED[@]}" "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e124-dipskept.json" --csv "$OUT/runs-dipskept.csv" --txt "$OUT/reduce-dipskept.txt" \
  > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"${RED[@]}" "${ok[@]}" --leak auto --no-refit --out "$OUT/e124-auto.json" --csv "$OUT/runs-auto.csv" --txt "$OUT/reduce-auto.txt" \
  > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
for v in "" -relaxed -dipskept -auto; do
  [ -s "$OUT/e124$v.json" ] || { echo "no e124$v.json"; continue; }
  python3 "$S109" "$OUT/e124$v.json" --pred "$PRED" --out "$OUT/scored$v.json" --md "$OUT/results$v.md" > "$OUT/score$v.log" 2>&1
  echo "score$v rc=$?: $(tail -1 "$OUT/score$v.log")"
done
python3 "$H/extras_e124.py" --primary "$OUT/e124.json" --relaxed "$OUT/e124-relaxed.json" --scored "$OUT/scored.json" \
  --scored-relaxed "$OUT/scored-relaxed.json" --out "$OUT/extras.json" --txt "$OUT/extras.txt" > "$OUT/extras.log" 2>&1
echo "extras rc=$?"; head -6 "$OUT/extras.txt" 2>/dev/null
