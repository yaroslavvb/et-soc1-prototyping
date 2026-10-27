#!/usr/bin/env bash
# E67 (Q128a): reduce every finished pass and assemble the data directory. Run on the box from ~/aifoundry:
#
#   bash tools/claims-v3/ha/collect_e67.sh
#
# Output: build/e67-out/2026-10-27-e67-a-side-bit-prices/ with hl.json, runs.csv, reduce.txt, closure.json,
# manifest.json, logs/ and the per-pass raw data. Only passes whose block.json says "ok" are reduced; an
# `.attempt-*` directory (a pass that did not finish) is never read.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen4
PRED=$ROOT/docs/reports/data/2026-10-20-bitflip-ladder/predictions.json
E65=$ROOT/docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
OUT=$ROOT/build/e67-out/2026-10-27-e67-a-side-bit-prices
rm -rf "${ROOT:?}/build/e67-out"
mkdir -p "$OUT/aifoundry3/hl" "$OUT/logs"

ok=()
for d in "$ROOT"/build/claims-v3/aifoundry3/hl/p75[0-9] "$ROOT"/build/claims-v3/aifoundry3/hl/p77[0-9]; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

"$PY" tools/claims-v3/hl/reduce_hl.py "${ok[@]}" --gen "$GEN" --pred "$PRED" \
  --out "$OUT/hl.json" --csv "$OUT/runs.csv" > "$OUT/reduce.txt" 2>&1
echo "reduce rc=$?"
tail -12 "$OUT/reduce.txt"

if [ -f "$E65" ]; then
  "$PY" tools/claims-v3/ha/closure.py --gen "$GEN" --e67 "$OUT/hl.json" --e65 "$E65" \
    --out "$OUT/closure.json" > "$OUT/closure.txt" 2>&1
  echo "closure rc=$?"; cat "$OUT/closure.txt"
else
  echo "E65 hl.json not found at $E65: the closure test needs the B-side price list" | tee "$OUT/closure.txt"
fi

"$PY" tools/claims-v3/ha/report_e67.py --e67 "$OUT/hl.json" --e65 "$E65" \
  --closure "$OUT/closure.json" --out "$OUT/results.md" --json "$OUT/scored.json" > /dev/null 2>&1 &&
  echo "results.md written" || echo "report_e67 failed"

cp "$GEN/manifest.json" "$OUT/manifest.json"
for f in e67-as.log e67-as-750.log e67-as-755.log e67-ix.log e67-chain3.log q128-gen4.log; do
  [ -f "$ROOT/build/$f" ] && cp "$ROOT/build/$f" "$OUT/logs/$f"
done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry3/hl/"; done
du -sh "$OUT"
echo "done: $OUT"

# ---- the constant-operand spread (a diagnostic, not a gate: ha/constspread.py says why) and, on the passes it
# calls clean, a labelled post-hoc sensitivity reduction beside the registered one.
"$PY" tools/claims-v3/ha/constspread.py "$OUT/runs.csv" --json "$OUT/constspread.json" \
  > "$OUT/constspread.txt" 2>&1
cat "$OUT/constspread.txt"
CLEAN=$("$PY" -c 'import json,sys; print(" ".join(str(p) for p in json.load(open(sys.argv[1]))["clean_passes"]))' \
  "$OUT/constspread.json" 2>/dev/null)
if [ -n "${CLEAN// /}" ]; then
  sel=()
  for p in $CLEAN; do
    d="$ROOT/build/claims-v3/aifoundry3/hl/p$p"
    [ -d "$d" ] && sel+=("$d")
  done
  echo "sensitivity reduction over the clean passes: ${CLEAN}"
  "$PY" tools/claims-v3/hl/reduce_hl.py "${sel[@]}" --gen "$GEN" --pred "$PRED" \
    --out "$OUT/hl-clean.json" --csv "$OUT/runs-clean.csv" > "$OUT/reduce-clean.txt" 2>&1
  if [ -f "$E65" ]; then
    "$PY" tools/claims-v3/ha/closure.py --gen "$GEN" --e67 "$OUT/hl-clean.json" --e65 "$E65" \
      --out "$OUT/closure-clean.json" > "$OUT/closure-clean.txt" 2>&1
    "$PY" tools/claims-v3/ha/report_e67.py --e67 "$OUT/hl-clean.json" --e65 "$E65" \
      --closure "$OUT/closure-clean.json" --out "$OUT/results-clean.md" --json "$OUT/scored-clean.json" \
      > /dev/null 2>&1
  fi
  echo "clean reduction written"
fi
