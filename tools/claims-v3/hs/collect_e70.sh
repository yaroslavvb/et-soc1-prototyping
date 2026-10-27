#!/usr/bin/env bash
# E70 (Q129): reduce every finished pass and assemble the data directory. Run on the box from ~/aifoundry:
#
#   bash tools/claims-v3/hs/collect_e70.sh [<date-slug>]
#
# Output: build/e70-out/<date-slug>/ with hl.json, runs.csv, reduce.txt, the leakage sensitivity reductions
# (departure D-d), report.md / scored.json, manifest.json, logs/ and the per-pass raw data. Only passes whose
# block.json says "ok" are reduced; an `.attempt-*` directory (a pass that did not finish) is never read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
SLUG=${1:-2026-10-27-e70-saturation-ladder}
GEN=$ROOT/build/hl-gen5
PRED=$ROOT/docs/reports/data/2026-10-20-bitflip-ladder/predictions.json
E70PRED=$ROOT/docs/reports/data/2026-10-27-e70-saturation-ladder/predictions-e70.json
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
OUT=$ROOT/build/e70-out/$SLUG
rm -rf "${ROOT:?}/build/e70-out"
mkdir -p "$OUT/aifoundry3/hl" "$OUT/logs"

ok=()
for d in "$ROOT"/build/claims-v3/aifoundry3/hl/p79[0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

"$PY" tools/claims-v3/hl/reduce_hl.py "${ok[@]}" --gen "$GEN" --pred "$PRED" \
  --out "$OUT/hl.json" --csv "$OUT/runs.csv" > "$OUT/reduce.txt" 2>&1
echo "reduce rc=$?"; tail -8 "$OUT/reduce.txt"

# departure D-d: the same reduction at three fixed leakage slopes, as a labelled sensitivity
for k in 0.2 0.3 0.4; do
  "$PY" tools/claims-v3/hl/reduce_hl.py "${ok[@]}" --gen "$GEN" --pred "$PRED" --leak "$k" \
    --out "$OUT/hl-leak$k.json" --csv "$OUT/runs-leak$k.csv" > "$OUT/reduce-leak$k.txt" 2>&1
  echo "leak $k rc=$?"
done

"$PY" tools/claims-v3/hs/report_e70.py --hl "$OUT/hl.json" --pred "$E70PRED" \
  --leak "$OUT/hl-leak0.2.json,$OUT/hl-leak0.3.json,$OUT/hl-leak0.4.json" \
  --load "$ROOT/build/e70-load.jsonl" --runs "$OUT/runs.csv" \
  --out "$OUT/report.md" --json "$OUT/scored.json" > "$OUT/report.txt" 2>&1 &&
  echo "report.md written" || { echo "report_e70 failed"; tail -20 "$OUT/report.txt"; }

cp "$GEN/manifest.json" "$OUT/manifest.json"
cp "$E70PRED" "$OUT/predictions-e70.json" 2>/dev/null || true
for f in e70-sat.log e70-load.jsonl e70-setup.log; do [ -f "$ROOT/build/$f" ] && cp "$ROOT/build/$f" "$OUT/logs/$f"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/hl/"; done
du -sh "$OUT"
echo "done: $OUT"
