#!/usr/bin/env bash
# E125 (Q134): reduce every finished pass and assemble the data directory. Run on the box from ~/nekko after the session:
#   bash tools/claims-v3/e125/collect_e125.sh [<date-slug>]
# Output build/e125-out/<slug>/:
#   dips/            dips_e125.py: card 1's board-meter dips (E82 A2), the filtered pass copies and dips.json
#   hl.json, runs.csv, reduce.txt          THE PRIMARY: hl/reduce_hl.py unchanged over the dip-free copies, --leak 0.2414
#                                          (E82's own slope on this card, E93's and E124's choice): card 1's frame
#   *-e113frame.*    arm: E113's own reduction (dips kept, --leak auto)
#   *-dipskept.*     arm: dips kept, --leak 0.2414
#   *-leakauto.*, *-leak0.2/0.3/0.4.*      arms: dips removed, the slope fitted, or fixed as E113's (E70's D-d) arms
#   report.md, scored.json                 score_e125.py: E113's P1-P7 (score_e113.py unchanged), Z, the X rules, N1, the arms
#   report-e113-format.md                  score_e113.py's own report for card 1's runs
#   manifest.json, predictions-e113.json, predictions-e125.json, logs/, aifoundry1-c1/e125/p125NN (raw), aifoundry1-c1/smoke-p12500
# Only passes whose block.json says "ok" are read; an `.attempt-*` directory is never read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
SLUG=${1:-2026-11-01-e125-a-side-replicate}
GEN=$ROOT/build/hl-gen6-e113
PRED=$ROOT/docs/reports/data/2026-10-20-bitflip-ladder/predictions.json
P113=$ROOT/tools/claims-v3/e113/predictions-e113.json
P125=$ROOT/tools/claims-v3/e125/predictions-e125.json
# aifoundry1 keeps numpy unpacked in pylib/ (lib.sh); use the first interpreter that imports it
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
for c in "${PY:-}" "$ROOT/.venv/bin/python3" python3; do [ -n "$c" ] && "$c" -c "import numpy" 2> /dev/null && { PY=$c; break; }; done
echo "python: ${PY:-none}"
RAW=$ROOT/build/claims-v3/aifoundry1-c1/e125
OUT=$ROOT/build/e125-out/$SLUG
rm -rf "${ROOT:?}/build/e125-out"
mkdir -p "$OUT/aifoundry1-c1/e125" "$OUT/logs"
ok=()
for d in "$RAW"/p125[0-9][0-9]; do
  [ -e "$d/block.json" ] || continue
  [ "$(basename "$d")" = p12500 ] && continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }
"$PY" tools/claims-v3/e125/dips_e125.py "$OUT/dips" "${ok[@]}"
nod=()
for d in "${ok[@]}"; do nod+=("$OUT/dips/passes/$(basename "$d")"); done
red() {  # red <suffix> <leak> <dirs...>
  local sfx=$1 lk=$2; shift 2
  "$PY" tools/claims-v3/hl/reduce_hl.py "$@" --gen "$GEN" --pred "$PRED" --leak "$lk" \
    --out "$OUT/hl$sfx.json" --csv "$OUT/runs$sfx.csv" > "$OUT/reduce$sfx.txt" 2>&1
  echo "reduce '$sfx' leak $lk rc=$?"
}
red "" 0.2414 "${nod[@]}"
tail -4 "$OUT/reduce.txt"
red -e113frame auto "${ok[@]}"
red -dipskept 0.2414 "${ok[@]}"
red -leakauto auto "${nod[@]}"
for k in 0.2 0.3 0.4; do red "-leak$k" "$k" "${nod[@]}"; done
"$PY" tools/claims-v3/e125/score_e125.py --runs "$OUT/runs.csv" --pred113 "$P113" --pred "$P125" --hl "$OUT/hl.json" \
  --arm "E113's own reduction (dips kept, leak auto)=$OUT/runs-e113frame.csv" \
  --arm "dips kept, leak 0.2414=$OUT/runs-dipskept.csv" \
  --arm "dips removed, leak auto=$OUT/runs-leakauto.csv" \
  --arm "dips removed, leak 0.2=$OUT/runs-leak0.2.csv" \
  --arm "dips removed, leak 0.3=$OUT/runs-leak0.3.csv" \
  --arm "dips removed, leak 0.4=$OUT/runs-leak0.4.csv" \
  --out "$OUT/report.md" --json "$OUT/scored.json" --e113-report "$OUT/report-e113-format.md" > "$OUT/report.txt" 2>&1 \
  && echo "report.md written" || { echo "score_e125 failed"; tail -20 "$OUT/report.txt"; }
cp "$GEN/manifest.json" "$OUT/manifest.json"
cp "$P113" "$OUT/predictions-e113.json"; cp "$P125" "$OUT/predictions-e125.json"
for f in session.log session.out queue.out smoke.log load.jsonl config-session-start.json config-session-end.json \
         config-session-start.json.time config-session-end.json.time session-start.time session-end.time anchor-t0.txt; do
  [ -f "$ROOT/build/e125/$f" ] && cp "$ROOT/build/e125/$f" "$OUT/logs/$f"
done
[ -f "$ROOT/build/e125/setup.log" ] && cp "$ROOT/build/e125/setup.log" "$OUT/logs/setup.log"
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/e125/"; done
[ -d "$ROOT/build/claims-v3/aifoundry1-c1/e125-smoke/p12500" ] && cp -r "$ROOT/build/claims-v3/aifoundry1-c1/e125-smoke/p12500" "$OUT/aifoundry1-c1/smoke-p12500"
rm -rf "${OUT:?}/dips/passes"
du -sh "$OUT"
echo "done: $OUT"
