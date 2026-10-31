#!/usr/bin/env bash
# E79 (Q130): reduce every finished pass and assemble the data directory. Run on the box from the tree that holds
# the binaries:
#
#   bash tools/claims-v3/hlp/collect_e79.sh [<pass glob>]
#
# Output: build/e79-out/2026-10-31-e79-fp16-int8-bit-prices/ with hlp.json, runs.csv, reduce.txt, results.md,
# scored.json, manifest.json, the E71-slope sensitivity arm, logs/ and the per-pass raw data. Only passes whose
# block.json says "ok" are reduced; an `.attempt-*` directory (a pass that did not finish) is never read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hlp-gen
PRED=$ROOT/tools/claims-v3/hlp/predictions.json
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p791[0-9]}
OUT=$ROOT/build/e79-out/2026-10-31-e79-fp16-int8-bit-prices
rm -rf "${ROOT:?}/build/e79-out"
mkdir -p "$OUT/aifoundry3/hlp" "$OUT/logs"

ok=()
for d in "$ROOT"/build/claims-v3/aifoundry3/hlp/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

"$PY" tools/claims-v3/hlp/reduce_hlp.py "${ok[@]}" --gen "$GEN" \
  --out "$OUT/hlp.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" > "$OUT/reduce.log" 2>&1
echo "reduce rc=$?"; tail -20 "$OUT/reduce.log"

# the registered sensitivity arm: E71's measured aifoundry3 idle slope instead of the fitted one
"$PY" tools/claims-v3/hlp/reduce_hlp.py "${ok[@]}" --gen "$GEN" --leak 0.3803 \
  --out "$OUT/hlp-leak0.3803.json" --csv "$OUT/runs-leak0.3803.csv" --txt "$OUT/reduce-leak0.3803.txt" \
  > "$OUT/reduce-leak0.3803.log" 2>&1
echo "leak-arm rc=$?"

"$PY" tools/claims-v3/hlp/report_e79.py --hl "$OUT/hlp.json" --pred "$PRED" \
  --hl-leak "$OUT/hlp-leak0.3803.json" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/report.log" 2>&1 && echo "results.md written" || { echo "report_e79 failed"; tail -20 "$OUT/report.log"; }

cp "$GEN/manifest.json" "$OUT/manifest.json"
( cd "$ROOT/tools/claims-v3" && sha256sum lib.sh hlp/* ) > "$OUT/code.sha256" 2>/dev/null || true
for f in e79-queue.log; do [ -f "$ROOT/build/$f" ] && cp "$ROOT/build/$f" "$OUT/logs/$f"; done
[ -d "$ROOT/build/hlp-ident" ] && cp -r "$ROOT/build/hlp-ident" "$OUT/ident"
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/hlp/"; done
for d in "$ROOT"/build/claims-v3/aifoundry3/hlp-smoke/p790*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry3/hlp/smoke-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
