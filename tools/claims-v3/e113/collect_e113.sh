#!/usr/bin/env bash
# E113 (Q133): reduce every finished pass and assemble the data directory. Run on the box from ~/aifoundry after the session:
#   bash tools/claims-v3/e113/collect_e113.sh [<date-slug>]
# Output build/e113-out/<slug>/: hl.json, runs.csv, reduce.txt (hl/reduce_hl.py, its own per-run gates), the leakage arms
# 0.2 / 0.3 / 0.4 W per C (hl-leak*.json, runs-leak*.csv: E70's departure D-d, registered here as arms), report.md and scored.json
# (score_e113.py: the registered pass gates, the paired contrasts and P1-P7), manifest.json, logs/ and the raw passes. Only
# passes whose block.json says "ok" are read; an `.attempt-*` directory is never read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
SLUG=${1:-2026-11-01-e113-a-side-saturation}
GEN=$ROOT/build/hl-gen6-e113
PRED=$ROOT/docs/reports/data/2026-10-20-bitflip-ladder/predictions.json
E113PRED=$ROOT/tools/claims-v3/e113/predictions-e113.json
PY=${PY:-$ROOT/.venv/bin/python3}; [ -x "$PY" ] || PY=python3
OUT=$ROOT/build/e113-out/$SLUG
rm -rf "${ROOT:?}/build/e113-out"
mkdir -p "$OUT/aifoundry3/e113" "$OUT/logs"
ok=()
for d in "$ROOT"/build/claims-v3/aifoundry3/e113/p113[1-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }
"$PY" tools/claims-v3/hl/reduce_hl.py "${ok[@]}" --gen "$GEN" --pred "$PRED" --out "$OUT/hl.json" --csv "$OUT/runs.csv" > "$OUT/reduce.txt" 2>&1
echo "reduce rc=$?"; tail -4 "$OUT/reduce.txt"
arms=()
for k in 0.2 0.3 0.4; do
  "$PY" tools/claims-v3/hl/reduce_hl.py "${ok[@]}" --gen "$GEN" --pred "$PRED" --leak "$k" \
    --out "$OUT/hl-leak$k.json" --csv "$OUT/runs-leak$k.csv" > "$OUT/reduce-leak$k.txt" 2>&1
  echo "leak $k rc=$?"
  arms+=(--arm "leakage $k W per C=$OUT/runs-leak$k.csv")
done
"$PY" tools/claims-v3/e113/score_e113.py --runs "$OUT/runs.csv" --pred "$E113PRED" --hl "$OUT/hl.json" "${arms[@]}" \
  --out "$OUT/report.md" --json "$OUT/scored.json" > "$OUT/report.txt" 2>&1 && echo "report.md written" || { echo "score_e113 failed"; tail -20 "$OUT/report.txt"; }
cp "$GEN/manifest.json" "$OUT/manifest.json"
cp "$E113PRED" "$OUT/predictions-e113.json"
for f in session.log session.out queue.out smoke.log load.jsonl config-session-start.json config-session-end.json session-start.time session-end.time setup.log; do
  [ -f "$ROOT/build/e113/$f" ] && cp "$ROOT/build/e113/$f" "$OUT/logs/$f"
done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/e113/"; done
[ -d "$ROOT/build/claims-v3/aifoundry3/e113-smoke/p1130" ] && cp -r "$ROOT/build/claims-v3/aifoundry3/e113-smoke/p1130" "$OUT/aifoundry3/smoke-p1130"
du -sh "$OUT"
echo "done: $OUT"
