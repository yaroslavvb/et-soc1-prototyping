#!/usr/bin/env bash
# E91 (Q130): reduce every finished pass with E78's reduction (reduce_e91.py: reduce_e78.py unchanged with E86's items,
# card 1's config gate and its meter dips removed), run the registered arms (dips kept; leakage 0.1994, 0.545, 0.3803,
# 0), score E91's rules and assemble the data directory. A port of collect_e86.sh. Desk compute: run it on the Intel
# over a copy of the raw passes, never on the card's host:
#
#   PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e91.sh ['p91[1-9][0-9]'] <raw root>
#
# <raw root> holds kinds/ and kinds-smoke/ as copied from aifoundry1:nekko/build/claims-v3/aifoundry1-c1/ (only the
# p91* passes) and logs/. Output: build/e91-out/2026-10-31-e91-real-tensors-aifoundry1/ with e91.json, runs.csv,
# reduce.txt, the arms (e91-dipskept, e91-leak<k> .json/.csv/.txt), scored.json, results.md, code.sha256, logs/, the
# smoke and every pass's raw data. Only passes whose block.json says "ok" are reduced; an `.attempt-*` directory is
# never read; no pass is chosen after the fact.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
GLOB=${1:-p91[1-9][0-9]}
RAW=${2:-$ROOT/build/claims-v3/aifoundry1-c1}
OUT=$ROOT/build/e91-out/2026-10-31-e91-real-tensors-aifoundry1
rm -rf "${ROOT:?}/build/e91-out"
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
"$PY" $K/reduce_e91.py "${ok[@]}" --out "$OUT/e91.json" --csv "$OUT/runs.csv" --txt "$OUT/reduce.txt" \
  > "$OUT/reduce.log" 2>&1; echo "reduce rc=$?"; tail -5 "$OUT/reduce.log"
ARMS=()
"$PY" $K/reduce_e91.py "${ok[@]}" --keep-dips --out "$OUT/e91-dipskept.json" --csv "$OUT/runs-dipskept.csv" \
  --txt "$OUT/reduce-dipskept.txt" > "$OUT/reduce-dipskept.log" 2>&1; echo "dips-kept arm rc=$?"
ARMS+=(--arm "dips_kept=$OUT/e91-dipskept.json")
for k in 0.1994 0.545 0.3803 0; do   # Q130(n)'s D scope, card 1's idle slope (E82), E71's idle slope, none
  "$PY" $K/reduce_e91.py "${ok[@]}" --leak "$k" --no-refit --out "$OUT/e91-leak$k.json" --csv "$OUT/runs-leak$k.csv" \
    --txt "$OUT/reduce-leak$k.txt" > "$OUT/reduce-leak$k.log" 2>&1; echo "leak-arm $k rc=$?"
  ARMS+=(--arm "leak$k=$OUT/e91-leak$k.json")
done
"$PY" $K/score_e91.py --e91 "$OUT/e91.json" "${ARMS[@]}" --md "$OUT/results.md" --json "$OUT/scored.json" \
  > "$OUT/score.log" 2>&1 && echo "results.md written" || { echo "score_e91 failed"; tail -20 "$OUT/score.log"; }

( cd "$ROOT" && { sha256sum tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E82.md $K/E86.md $K/E91.md \
    $K/predictions-e78.json $K/predictions-e82.json $K/predictions-e86.json $K/predictions-e91.json $K/kinds.json \
    $K/real/real.json $K/real/predictions-real.json $K/real/amendment-1.json $K/real/tiles/*/*.bin 2>/dev/null ||
  shasum -a 256 tools/claims-v3/lib.sh $K/*.py $K/*.sh $K/E78.md $K/E82.md $K/E86.md $K/E91.md \
    $K/predictions-e78.json $K/predictions-e82.json $K/predictions-e86.json $K/predictions-e91.json $K/kinds.json \
    $K/real/real.json $K/real/predictions-real.json $K/real/amendment-1.json $K/real/tiles/*/*.bin; } ) > "$OUT/code.sha256" 2>/dev/null
for f in "$RAW"/logs/*; do [ -f "$f" ] && cp "$f" "$OUT/logs/"; done
for d in "${ok[@]}"; do cp -r "$d" "$OUT/aifoundry1-c1/kinds/"; done
for d in "$RAW"/kinds/p91*.attempt-* "$RAW"/kinds-smoke/p91*; do
  [ -d "$d" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/$(basename "$(dirname "$d")")-$(basename "$d")"
done
for d in "$RAW"/kinds/p91*; do   # a pass whose block did not end ok is kept beside, never reduced
  case "$d" in *.attempt-*) continue ;; esac
  [ -d "$d" ] && [ ! -d "$OUT/aifoundry1-c1/kinds/$(basename "$d")" ] && cp -r "$d" "$OUT/aifoundry1-c1/kinds/notok-$(basename "$d")"
done
du -sh "$OUT"
echo "done: $OUT"
