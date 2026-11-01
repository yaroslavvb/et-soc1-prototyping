#!/usr/bin/env bash
# E102 (Q132): reduce every finished block with E78's reduction (reduce_e102.py: reduce_e78.py unchanged with E102's items, card 1's config gate and its meter dips removed, leakage frozen at E82's
# 0.2414), run the registered arms (dips kept; pass gates opened; leakage auto, 0.1994, 0.3803, 0.545, 0), score E102's rules and assemble the data directory. A port of collect_e94.sh.
# Desk compute: run it on the Intel over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e102.sh ['p102[1-3][0-9]'] <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ (only the p102* passes) and logs/. Output: build/e102-out/2026-11-01-e102-balanced-bit-prices/ with
# e102.json, runs.csv, reduce.txt, the arms (e102-dipskept, e102-gatesoff, e102-auto, e102-leak<k> .json/.csv/.txt), scored.json, results.md, code.sha256, logs/, the smoke and every pass's raw data. Only passes whose
# block.json says "ok" are reduced; an `.attempt-*` directory is never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p102[1-3][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry1-c1}
OUT=$ROOT/build/e102-out/2026-11-01-e102-balanced-bit-prices
rm -rf "${ROOT:?}/build/e102-out"
mkdir -p "$OUT/aifoundry1-c1/kinds" "$OUT/logs"

ok=()
for d in "$RAW"/kinds/$GLOB; do
  [ -e "$d/block.json" ] || continue
  grep -q '"status":"ok"' "$d/block.json" || { echo "skipped (not ok): $d"; continue; }
  ok+=("$d")
done
echo "passes reduced: ${#ok[@]}"
[ ${#ok[@]} -gt 0 ] || { echo "no finished pass" >&2; exit 1; }

K=tools/claims-v3/kinds
"$PY" $K/reduce_e102.py "${ok[@]}" --leak 0.2414 --out "$OUT/e102.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -3 "$OUT/reduce.log" | cut -c1-200
"$PY" $K/reduce_e102.py "${ok[@]}" --keep-dips --leak 0.2414 --no-refit --out "$OUT/e102-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
"$PY" $K/reduce_e102.py "${ok[@]}" --gates-off --leak 0.2414 --no-refit --out "$OUT/e102-gatesoff.json" --csv "$OUT/runs-gatesoff.csv" \
  --txt "$OUT/reduce-gatesoff.txt" > "$OUT/reduce-gatesoff.log" 2>&1; echo "gates-off arm rc=$?"
"$PY" $K/reduce_e102.py "${ok[@]}" --leak auto --no-refit --out "$OUT/e102-auto.json" --csv "$OUT/runs-auto.csv" \
  --txt "$OUT/reduce-auto.txt" > "$OUT/reduce-auto.log" 2>&1; echo "auto arm rc=$?"
for k in 0.1994 0.3803 0.545 0; do   # E78's fit (Q130(n)'s D scope), E71's idle slope, card 1's idle slope (E82), none
  "$PY" $K/reduce_e102.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e102-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
done
"$PY" $K/score_e102.py --dir "$OUT" --md "$OUT/results.md" --json "$OUT/scored.json" > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e102 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { shasum -a 256 tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/make_kinds.py \
    $K/*e102*.* $K/E102.md $K/predictions-e102.json $K/kinds.json $K/e102/e102.json $K/e102/tiles/*/*.bin 2>/dev/null ||
  sha256sum tools/claims-v3/lib.sh $K/e78_common.py $K/run_e78.py $K/reduce_e78.py $K/make_kinds.py \
    $K/*e102*.* $K/E102.md $K/predictions-e102.json $K/kinds.json $K/e102/e102.json $K/e102/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/kinds/"; done
for d in "$RAW"/kinds/p102*.attempt-* "$RAW"/kinds-smoke/p102*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/kinds/p102*; do   # a pass whose block did not end ok is kept beside, never reduced
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry1-c1/kinds/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
